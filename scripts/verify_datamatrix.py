#!/usr/bin/env python3
from __future__ import annotations

import argparse
import base64
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from tempfile import NamedTemporaryFile

from PIL import Image
from pylibdmtx.pylibdmtx import decode

GS = b"\x1d"
PROJECT_ROOT = Path(__file__).resolve().parents[1]


def resolve_path(value: str) -> Path:
    path = Path(value)
    return path if path.is_absolute() else PROJECT_ROOT / path


def decode_datamatrix(path: Path) -> bytes:
    items = decode(Image.open(path))
    if not items:
        raise RuntimeError("Falha ao decodificar o DataMatrix.")
    return items[0].data


def parse_payload(payload: bytes) -> dict[str, str | bytes]:
    parts = payload.split(GS)
    if len(parts) != 4:
        raise RuntimeError(f"Payload inválido: esperado 4 partes, obtido {len(parts)}.")

    part1, part2, part3, part4 = parts
    if part1[0:2] != b"01" or part1[16:18] != b"17" or part1[24:26] != b"10":
        raise RuntimeError("AIs 01, 17 ou 10 ausentes ou fora de posição.")
    if not part2.startswith(b"21") or not part3.startswith(b"92") or not part4.startswith(b"91"):
        raise RuntimeError("AIs 21, 92 ou 91 ausentes ou fora de posição.")

    return {
        "gtin": part1[2:16].decode(),
        "expiration": part1[18:24].decode(),
        "lot": part1[26:].decode(),
        "serial": part2[2:].decode(),
        "kid": part3[2:].decode(),
        "signature": part4[2:].decode(),
        "signed_base": part1 + GS + part2,
    }


def load_certificate(cert_map_path: Path, kid: str) -> Path:
    cert_map = json.loads(cert_map_path.read_text(encoding="utf-8"))
    if kid not in cert_map:
        raise RuntimeError(f"KID não encontrado: {kid}")
    return resolve_path(cert_map[kid]["cert_path"])


def verify_signature(cert_path: Path, signed_base: bytes, signature_b64u: str) -> tuple[bool, str]:
    signature = base64.urlsafe_b64decode(signature_b64u + "=" * (-len(signature_b64u) % 4))

    with NamedTemporaryFile(delete=False) as sig_file, NamedTemporaryFile(delete=False) as data_file, NamedTemporaryFile(delete=False) as pub_file:
        sig_path = Path(sig_file.name)
        data_path = Path(data_file.name)
        pub_path = Path(pub_file.name)

    try:
        sig_path.write_bytes(signature)
        data_path.write_bytes(signed_base)
        pub_result = subprocess.run(
            ["openssl", "x509", "-in", str(cert_path), "-pubkey", "-noout"],
            capture_output=True,
            check=True,
        )
        pub_path.write_bytes(pub_result.stdout)

        result = subprocess.run([
            "openssl", "dgst", "-sha256",
            "-verify", str(pub_path),
            "-signature", str(sig_path),
            str(data_path),
        ], capture_output=True)
        output = (result.stdout + result.stderr).decode(errors="replace").strip()
        return result.returncode == 0 and "Verified OK" in output, output
    finally:
        sig_path.unlink(missing_ok=True)
        data_path.unlink(missing_ok=True)
        pub_path.unlink(missing_ok=True)


def verify_chain(ca_path: Path, cert_path: Path) -> tuple[bool, str]:
    result = subprocess.run(
        ["openssl", "verify", "-CAfile", str(ca_path), str(cert_path)],
        capture_output=True,
    )
    output = (result.stdout + result.stderr).decode(errors="replace").strip()
    return result.returncode == 0 and output.endswith(": OK"), output


def register_event(path: Path, info: dict[str, str | bytes]) -> dict:
    path.parent.mkdir(parents=True, exist_ok=True)
    registry = json.loads(path.read_text()) if path.exists() and path.read_text().strip() else {}
    key = f"{info['gtin']}|{info['serial']}"
    now = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    record = registry.setdefault(key, {
        "gtin": info["gtin"],
        "serial": info["serial"],
        "lot": info["lot"],
        "first_seen": now,
        "seen_count": 0,
    })
    record["last_seen"] = now
    record["seen_count"] += 1
    path.write_text(json.dumps(registry, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return record


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Verifica assinatura e cadeia de um DataMatrix.")
    parser.add_argument("image")
    parser.add_argument("--check-chain", action="store_true")
    parser.add_argument("--track-events", action="store_true", help="Registra leituras como experimento exploratório.")
    parser.add_argument("--registry", default="output/registry/events.json")
    parser.add_argument("--cert-map", default="output/pki/cert_map.json")
    parser.add_argument("--ca", default="output/pki/ca.crt")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    image_path = resolve_path(args.image)
    cert_map_path = resolve_path(args.cert_map)
    ca_path = resolve_path(args.ca)

    if not image_path.exists():
        raise FileNotFoundError(image_path)
    if not cert_map_path.exists():
        raise FileNotFoundError(cert_map_path)

    payload = decode_datamatrix(image_path).rstrip(b"\n")
    info = parse_payload(payload)
    cert_path = load_certificate(cert_map_path, str(info["kid"]))

    signature_ok, signature_output = verify_signature(cert_path, info["signed_base"], str(info["signature"]))
    if not signature_ok:
        print(signature_output)
        print("\n[RESULTADO] INVÁLIDO")
        print("Motivo: assinatura inválida ou conteúdo alterado.")
        return 2

    if args.check_chain:
        chain_ok, chain_output = verify_chain(ca_path, cert_path)
        if not chain_ok:
            print(chain_output)
            print("\n[RESULTADO] INVÁLIDO")
            print("Motivo: cadeia de confiança inválida.")
            return 3

    print("[RESULTADO] VÁLIDO")
    print("O conteúdo permaneceu íntegro e a assinatura corresponde ao certificado aceito.")
    print(f"GTIN={info['gtin']} LOTE={info['lot']} SERIAL={info['serial']}")

    if args.track_events:
        record = register_event(resolve_path(args.registry), info)
        print("\n[EXPERIMENTO DE EVENTOS]")
        print("Ocorrências registradas:", record["seen_count"])
        if record["seen_count"] > 1:
            print("A repetição indica um evento duplicado, mas não comprova clonagem.")

    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"[ERRO] {exc}", file=sys.stderr)
        raise SystemExit(1)
