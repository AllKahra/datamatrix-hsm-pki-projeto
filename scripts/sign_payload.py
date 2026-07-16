#!/usr/bin/env python3
from __future__ import annotations

import base64
import hashlib
import json
import os
import subprocess
import tempfile
from pathlib import Path

GS = b"\x1d"
PROJECT_ROOT = Path(__file__).resolve().parents[1]


def run(cmd: list[str], env: dict[str, str] | None = None) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, env=env, capture_output=True, check=True)


def required_env(name: str) -> str:
    value = os.environ.get(name)
    if not value:
        raise RuntimeError(f"Variável obrigatória ausente: {name}")
    return value


def resolve_path(value: str) -> Path:
    path = Path(value)
    return path if path.is_absolute() else PROJECT_ROOT / path


def read_without_final_newline(path: Path) -> bytes:
    data = path.read_bytes()
    return data[:-1] if data.endswith(b"\n") else data


def verify_chain(ca_crt: Path, mfg_crt: Path) -> None:
    result = run(["openssl", "verify", "-CAfile", str(ca_crt), str(mfg_crt)])
    output = result.stdout.decode(errors="replace").strip()
    if not output.endswith(": OK"):
        raise RuntimeError(f"Falha na cadeia: {output}")


def certificate_der(path: Path) -> bytes:
    return run(["openssl", "x509", "-in", str(path), "-outform", "der"]).stdout


def certificate_field(path: Path, option: str) -> str:
    result = run(["openssl", "x509", "-in", str(path), "-noout", option])
    return result.stdout.decode(errors="replace").strip()


def certificate_fingerprint(path: Path) -> str:
    result = run(["openssl", "x509", "-in", str(path), "-noout", "-fingerprint", "-sha256"])
    return result.stdout.decode().strip().split("=", 1)[1].replace(":", "").lower()


def sign(data: bytes, key_uri: str, module: str, config: str, pin: str) -> bytes:
    env = os.environ.copy()
    env["SOFTHSM2_CONF"] = config
    env["PKCS11_MODULE_PATH"] = module
    env["PKCS11_PIN"] = pin

    with tempfile.NamedTemporaryFile(delete=False) as input_file, tempfile.NamedTemporaryFile(delete=False) as output_file:
        input_path = Path(input_file.name)
        output_path = Path(output_file.name)

    try:
        input_path.write_bytes(data)
        run([
            "openssl", "dgst", "-sha256",
            "-engine", "pkcs11", "-keyform", "engine",
            "-sign", key_uri,
            "-out", str(output_path),
            str(input_path),
        ], env=env)
        return output_path.read_bytes()
    finally:
        input_path.unlink(missing_ok=True)
        output_path.unlink(missing_ok=True)


def main() -> int:
    data_dir = PROJECT_ROOT / "output/data"
    pki_dir = PROJECT_ROOT / "output/pki"
    data_dir.mkdir(parents=True, exist_ok=True)
    pki_dir.mkdir(parents=True, exist_ok=True)

    ca_crt = resolve_path(required_env("CA_CRT"))
    mfg_crt = resolve_path(required_env("MFG_CRT"))
    base_path = data_dir / "gs1_base.txt"

    if not base_path.exists():
        raise FileNotFoundError(base_path)

    base = read_without_final_newline(base_path)
    if GS not in base:
        raise RuntimeError("O payload base não contém o separador GS.")

    verify_chain(ca_crt, mfg_crt)
    kid = hashlib.sha256(certificate_der(mfg_crt)).hexdigest()[:16]
    signature = sign(
        data=base,
        key_uri=required_env("HSM_MFG_KEY"),
        module=required_env("HSM_MODULE"),
        config=required_env("SOFTHSM2_CONF"),
        pin=required_env("HSM_USER_PIN"),
    )
    signature_b64u = base64.urlsafe_b64encode(signature).decode("ascii").rstrip("=")
    payload = base + GS + f"92{kid}".encode() + GS + f"91{signature_b64u}".encode()

    (data_dir / "kid.txt").write_text(kid + "\n", encoding="utf-8")
    (data_dir / "signature.b64u").write_text(signature_b64u + "\n", encoding="utf-8")
    (data_dir / "payload.txt").write_bytes(payload + b"\n")

    cert_map = {
        kid: {
            "cert_path": "output/pki/manufacturer.crt",
            "cert_sha256": certificate_fingerprint(mfg_crt),
            "subject": certificate_field(mfg_crt, "-subject"),
            "issuer": certificate_field(mfg_crt, "-issuer"),
        }
    }
    (pki_dir / "cert_map.json").write_text(
        json.dumps(cert_map, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    print("[OK] Payload assinado")
    print("  KID:", kid)
    print("  Saída:", data_dir / "payload.txt")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
