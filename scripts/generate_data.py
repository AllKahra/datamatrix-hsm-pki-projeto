#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import random
import re
import secrets
import string
from dataclasses import asdict, dataclass
from datetime import date, datetime, timedelta
from pathlib import Path

GS = chr(29)
SERIAL_ALPHABET = string.ascii_uppercase + string.digits


@dataclass
class MedicineData:
    gtin: str
    expiration: str
    expiration_gs1: str
    lot: str
    serial: str
    ai_01: str
    ai_17: str
    ai_10: str
    ai_21: str
    gs1_base_raw: str
    gs1_base_visible: str
    gs1_hri: str
    separator_after_lot: bool


def validate_gtin(value: str) -> str:
    value = value.strip()
    if not re.fullmatch(r"\d{14}", value):
        raise ValueError("GTIN deve conter exatamente 14 dígitos.")
    return value


def validate_variable_field(name: str, value: str) -> str:
    value = value.strip().upper()
    if not 1 <= len(value) <= 20:
        raise ValueError(f"{name} deve ter entre 1 e 20 caracteres.")
    if not re.fullmatch(r"[A-Z0-9\-._/]+", value):
        raise ValueError(f"{name} contém caracteres inválidos.")
    return value


def validate_expiration(value: str) -> date:
    try:
        return datetime.strptime(value.strip(), "%Y-%m-%d").date()
    except ValueError as exc:
        raise ValueError("A validade deve usar o formato YYYY-MM-DD.") from exc


def random_serial(length: int = 12) -> str:
    return "".join(secrets.choice(SERIAL_ALPHABET) for _ in range(length))


def random_lot() -> str:
    return "L" + "".join(random.choice(string.digits) for _ in range(6))


def future_expiration() -> date:
    return date.today() + timedelta(days=random.randint(365, 900))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Gera dados demonstrativos do medicamento.")
    parser.add_argument("--gtin", default="05412345000013")
    parser.add_argument("--serial")
    parser.add_argument("--lot")
    parser.add_argument("--exp", help="Validade em YYYY-MM-DD")
    parser.add_argument("--outdir", default="output/data")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    gtin = validate_gtin(args.gtin)
    serial = validate_variable_field("SERIAL", args.serial or random_serial())
    lot = validate_variable_field("LOT", args.lot or random_lot())
    expiration = validate_expiration(args.exp) if args.exp else future_expiration()
    exp_gs1 = expiration.strftime("%y%m%d")

    ai_01 = f"01{gtin}"
    ai_17 = f"17{exp_gs1}"
    ai_10 = f"10{lot}"
    ai_21 = f"21{serial}"
    raw = ai_01 + ai_17 + ai_10 + GS + ai_21

    medicine = MedicineData(
        gtin=gtin,
        expiration=expiration.isoformat(),
        expiration_gs1=exp_gs1,
        lot=lot,
        serial=serial,
        ai_01=ai_01,
        ai_17=ai_17,
        ai_10=ai_10,
        ai_21=ai_21,
        gs1_base_raw=raw,
        gs1_base_visible=ai_01 + ai_17 + ai_10 + "<GS>" + ai_21,
        gs1_hri=f"(01){gtin}(17){exp_gs1}(10){lot}(21){serial}",
        separator_after_lot=True,
    )

    (outdir / "medicine.json").write_text(
        json.dumps(asdict(medicine), indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    (outdir / "gs1_base.txt").write_text(raw + "\n", encoding="utf-8")
    (outdir / "gs1_hri.txt").write_text(medicine.gs1_hri + "\n", encoding="utf-8")

    print("[OK] Dados gerados em", outdir)
    print("  GTIN:", gtin)
    print("  LOTE:", lot)
    print("  VALIDADE:", expiration.isoformat())
    print("  SERIAL:", serial)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
