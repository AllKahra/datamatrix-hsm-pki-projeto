#!/usr/bin/env bash
set -Eeuo pipefail

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$PROJECT_DIR/.venv"
CLEAN_MODE=false

if [[ "${1:-}" == "--clean" ]]; then
  CLEAN_MODE=true
fi

log() { printf '\n[INFO] %s\n' "$*"; }
ok() { printf '[OK] %s\n' "$*"; }
warn() { printf '[AVISO] %s\n' "$*"; }
fail() { printf '[ERRO] %s\n' "$*" >&2; exit 1; }

cd "$PROJECT_DIR"

command -v sudo >/dev/null 2>&1 || fail "sudo não encontrado."
command -v apt-get >/dev/null 2>&1 || fail "apt-get não encontrado."
command -v python3 >/dev/null 2>&1 || fail "python3 não encontrado."

if [[ "$CLEAN_MODE" == true ]]; then
  log "Removendo ambiente virtual antigo"
  rm -rf "$VENV_DIR"
fi

log "Atualizando repositórios"
sudo apt-get update

log "Instalando dependências do sistema"
sudo apt-get install -y \
  build-essential \
  git \
  jq \
  libengine-pkcs11-openssl \
  opensc \
  openssl \
  pkg-config \
  python3 \
  python3-dev \
  python3-pip \
  python3-venv \
  softhsm2

LIBDMTX_PACKAGE=""
for package in libdmtx0b libdmtx0t64 libdmtx0a; do
  if apt-cache show "$package" >/dev/null 2>&1; then
    LIBDMTX_PACKAGE="$package"
    break
  fi
done

[[ -n "$LIBDMTX_PACKAGE" ]] || fail "Nenhum pacote runtime da libdmtx foi encontrado."
sudo apt-get install -y "$LIBDMTX_PACKAGE"

if apt-cache show libdmtx-dev >/dev/null 2>&1; then
  sudo apt-get install -y libdmtx-dev
else
  warn "libdmtx-dev não foi encontrado; o runtime foi instalado."
fi

log "Criando estrutura de saída"
mkdir -p output/{data,datamatrix,pki,registry,tokens}
for dir in data datamatrix pki registry tokens; do
  touch "output/$dir/.gitkeep"
done

if [[ ! -f .env ]]; then
  cp .env.example .env
  warn "Arquivo .env criado com valores demonstrativos."
fi

log "Criando configuração local do SoftHSM"
cat > output/softhsm2.conf <<CONF
# Arquivo gerado localmente pelo setup.sh
directories.tokendir = $PROJECT_DIR/output/tokens
objectstore.backend = file
log.level = INFO
CONF

log "Criando ambiente virtual Python"
python3 -m venv "$VENV_DIR"
# shellcheck disable=SC1091
source "$VENV_DIR/bin/activate"

python -m pip install --upgrade pip setuptools wheel
python -m pip install -r requirements.txt

log "Validando bibliotecas Python"
python - <<'PY'
from PIL import Image
from pylibdmtx.pylibdmtx import decode, encode
import cryptography
import pkcs11

payload = b"setup-test"
encoded = encode(payload)
image = Image.frombytes("RGB", (encoded.width, encoded.height), encoded.pixels)
items = decode(image)
assert items and items[0].data == payload
print("[OK] Dependências Python e DataMatrix validados")
PY

ok "Ambiente preparado."
echo
echo "Próximos comandos:"
echo "  source .venv/bin/activate"
echo "  source env.sh"
echo "  bash rebuild_lab.sh"
