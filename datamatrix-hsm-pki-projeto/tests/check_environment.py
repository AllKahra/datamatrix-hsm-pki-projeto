#!/usr/bin/env python3
from pathlib import Path

from PIL import Image
from pylibdmtx.pylibdmtx import decode, encode
import cryptography
import pkcs11

root = Path(__file__).resolve().parents[1]
required = [
    root / "config/pki/ca.ext",
    root / "config/pki/manufacturer.ext",
    root / "scripts/generate_data.py",
    root / "scripts/sign_payload.py",
    root / "scripts/generate_datamatrix.py",
    root / "scripts/verify_datamatrix.py",
]

for path in required:
    assert path.exists(), f"Arquivo ausente: {path}"

payload = b"environment-test"
encoded = encode(payload)
image = Image.frombytes("RGB", (encoded.width, encoded.height), encoded.pixels)
items = decode(image)
assert items and items[0].data == payload

print("[OK] Estrutura e dependências principais validadas.")
