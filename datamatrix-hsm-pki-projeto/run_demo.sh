#!/usr/bin/env bash
set -Eeuo pipefail

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_DIR"

# shellcheck disable=SC1091
source .venv/bin/activate
# shellcheck disable=SC1091
source env.sh

bash rebuild_lab.sh

echo
echo "=== CENÁRIO 1: CONTEÚDO ÍNTEGRO ==="
python scripts/verify_datamatrix.py output/datamatrix/medicine.png --check-chain

echo
echo "=== CENÁRIO 2: CONTEÚDO ALTERADO ==="
python - <<'PY'
from pathlib import Path
source = Path("output/data/payload.txt").read_bytes()
if b"L202401" not in source:
    raise SystemExit("Lote original não encontrado.")
Path("output/data/payload_tampered.txt").write_bytes(source.replace(b"L202401", b"L999999", 1))
PY

python scripts/generate_datamatrix.py \
  --payload output/data/payload_tampered.txt \
  --out output/datamatrix/tampered.png \
  --decoded-out output/datamatrix/tampered_decoded.txt

set +e
python scripts/verify_datamatrix.py output/datamatrix/tampered.png --check-chain
status=$?
set -e

if [[ "$status" -ne 2 ]]; then
  echo "[ERRO] O cenário alterado não retornou o código esperado 2." >&2
  exit 1
fi

echo
echo "[OK] Demonstração concluída: válido no original e inválido no alterado."
