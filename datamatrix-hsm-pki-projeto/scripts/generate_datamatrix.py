#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image
from pylibdmtx.pylibdmtx import decode, encode


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Gera e valida uma imagem DataMatrix.")
    parser.add_argument("--payload", default="output/data/payload.txt")
    parser.add_argument("--out", default="output/datamatrix/medicine.png")
    parser.add_argument("--decoded-out", default="output/datamatrix/decoded_payload.txt")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    payload_path = Path(args.payload)
    image_path = Path(args.out)
    decoded_path = Path(args.decoded_out)

    if not payload_path.exists():
        raise FileNotFoundError(payload_path)

    image_path.parent.mkdir(parents=True, exist_ok=True)
    decoded_path.parent.mkdir(parents=True, exist_ok=True)

    payload = payload_path.read_bytes()
    if payload.endswith(b"\n"):
        payload = payload[:-1]

    encoded = encode(payload)
    image = Image.frombytes("RGB", (encoded.width, encoded.height), encoded.pixels)
    image.save(image_path)

    items = decode(Image.open(image_path))
    if not items:
        raise RuntimeError("O DataMatrix gerado não pôde ser decodificado.")

    decoded = items[0].data
    if decoded != payload:
        raise RuntimeError("O payload decodificado difere do original.")

    decoded_path.write_bytes(decoded + b"\n")
    print("[OK] DataMatrix gerado:", image_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
