#!/usr/bin/env bash
set -Eeuo pipefail

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_DIR"

log() { printf '\n[INFO] %s\n' "$*"; }
ok() { printf '[OK] %s\n' "$*"; }
fail() { printf '[ERRO] %s\n' "$*" >&2; exit 1; }

[[ -f .venv/bin/activate ]] || fail "Execute primeiro: bash setup.sh"
# shellcheck disable=SC1091
source .venv/bin/activate
# shellcheck disable=SC1091
source env.sh

for command in softhsm2-util pkcs11-tool openssl python; do
  command -v "$command" >/dev/null 2>&1 || fail "Comando ausente: $command"
done

mkdir -p output/{data,datamatrix,pki,registry,tokens}

log "Limpando artefatos gerados"
find output/data output/datamatrix output/pki output/registry output/tokens -mindepth 1 ! -name .gitkeep -delete

cat > "$SOFTHSM2_CONF" <<CONF
# Arquivo gerado localmente
directories.tokendir = $PROJECT_DIR/output/tokens
objectstore.backend = file
log.level = INFO
CONF

log "Criando tokens"
softhsm2-util --init-token --free --label "$CA_TOKEN_LABEL" --so-pin "$HSM_SO_PIN" --pin "$HSM_USER_PIN"
softhsm2-util --init-token --free --label "$MANUFACTURER_TOKEN_LABEL" --so-pin "$HSM_SO_PIN" --pin "$HSM_USER_PIN"

log "Gerando chaves RSA no SoftHSM"
pkcs11-tool --module "$HSM_MODULE" --token-label "$CA_TOKEN_LABEL" --login --pin "$HSM_USER_PIN" \
  --keypairgen --key-type rsa:2048 --label "$CA_KEY_LABEL" --id 01
pkcs11-tool --module "$HSM_MODULE" --token-label "$MANUFACTURER_TOKEN_LABEL" --login --pin "$HSM_USER_PIN" \
  --keypairgen --key-type rsa:2048 --label "$MANUFACTURER_KEY_LABEL" --id 10

log "Criando PKI local"
openssl req -new -engine pkcs11 -keyform engine -key "$HSM_CA_KEY" \
  -subj "/C=BR/ST=SP/O=PoC Pharma/CN=PoC Pharma Root CA" \
  -out output/pki/ca.csr

openssl x509 -req -days 3650 -in output/pki/ca.csr \
  -engine pkcs11 -keyform engine -signkey "$HSM_CA_KEY" \
  -extfile config/pki/ca.ext -out output/pki/ca.crt

openssl req -new -engine pkcs11 -keyform engine -key "$HSM_MFG_KEY" \
  -subj "/C=BR/ST=SP/O=PoC Pharma/CN=PoC Pharma Manufacturer" \
  -out output/pki/manufacturer.csr

openssl x509 -req -days 825 -in output/pki/manufacturer.csr \
  -CA output/pki/ca.crt -CAcreateserial \
  -engine pkcs11 -CAkeyform engine -CAkey "$HSM_CA_KEY" \
  -extfile config/pki/manufacturer.ext -out output/pki/manufacturer.crt

openssl verify -CAfile output/pki/ca.crt output/pki/manufacturer.crt

log "Gerando dados e DataMatrix"
python scripts/generate_data.py \
  --gtin 05412345000013 \
  --lot L202401 \
  --exp 2027-05-31 \
  --serial ABC123456789
python scripts/sign_payload.py
python scripts/generate_datamatrix.py

ok "Laboratório reconstruído."
echo "Valide com:"
echo "  python scripts/verify_datamatrix.py output/datamatrix/medicine.png --check-chain"
