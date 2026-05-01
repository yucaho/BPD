from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def normalize_uuid(value: str) -> str:
    return value.strip().lower()


def normalize_mfr_id(value: str | int) -> str:
    if isinstance(value, int):
        return f"0x{value:04x}"
    s = str(value).strip().lower()
    if s.startswith("0x"):
        return f"0x{int(s, 16):04x}"
    return f"0x{int(s):04x}"


def hex_bytes(data: bytes) -> str:
    return data.hex()


def load_json(path: str | Path) -> dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(path: str | Path, payload: dict[str, Any]) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
        f.write("\n")
