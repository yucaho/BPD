from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .utils import normalize_mfr_id, normalize_uuid


@dataclass
class MatchCriteria:
    name_contains: str | None = None
    address_contains: str | None = None
    required_any_service_uuid: list[str] = field(default_factory=list)
    manufacturer_id: str | None = None


@dataclass
class ExpectedCriteria:
    required_service_uuids: list[str] = field(default_factory=list)
    forbidden_service_uuids: list[str] = field(default_factory=list)
    required_manufacturer_ids: list[str] = field(default_factory=list)
    required_service_data_uuids: list[str] = field(default_factory=list)
    min_rssi: int | None = None
    max_rssi: int | None = None
    required_name_prefix: str | None = None
    required_name_contains: str | None = None


@dataclass
class ProfileRules:
    profile_name: str = "My BLE Profile"
    match: MatchCriteria = field(default_factory=MatchCriteria)
    expected: ExpectedCriteria = field(default_factory=ExpectedCriteria)
    notes: str = ""


def parse_rules(raw: dict[str, Any]) -> ProfileRules:
    m = raw.get("match", {})
    e = raw.get("expected", {})
    match = MatchCriteria(
        name_contains=m.get("name_contains"),
        address_contains=m.get("address_contains"),
        required_any_service_uuid=[normalize_uuid(x) for x in m.get("required_any_service_uuid", [])],
        manufacturer_id=normalize_mfr_id(m["manufacturer_id"]) if m.get("manufacturer_id") is not None else None,
    )
    expected = ExpectedCriteria(
        required_service_uuids=[normalize_uuid(x) for x in e.get("required_service_uuids", [])],
        forbidden_service_uuids=[normalize_uuid(x) for x in e.get("forbidden_service_uuids", [])],
        required_manufacturer_ids=[normalize_mfr_id(x) for x in e.get("required_manufacturer_ids", [])],
        required_service_data_uuids=[normalize_uuid(x) for x in e.get("required_service_data_uuids", [])],
        min_rssi=e.get("min_rssi"),
        max_rssi=e.get("max_rssi"),
        required_name_prefix=e.get("required_name_prefix"),
        required_name_contains=e.get("required_name_contains"),
    )
    return ProfileRules(profile_name=raw.get("profile_name", "My BLE Profile"), match=match, expected=expected, notes=raw.get("notes", ""))


def default_rules_template() -> dict[str, Any]:
    return {
        "profile_name": "My BLE Device",
        "match": {
            "name_contains": "MyDevice",
            "address_contains": "",
            "required_any_service_uuid": ["180f"],
            "manufacturer_id": "0x004c",
        },
        "expected": {
            "required_service_uuids": ["180f"],
            "forbidden_service_uuids": [],
            "required_manufacturer_ids": ["0x004c"],
            "required_service_data_uuids": [],
            "min_rssi": -95,
            "max_rssi": -10,
            "required_name_prefix": "My",
            "required_name_contains": "Device",
        },
        "notes": "Adjust this file for your own firmware/profile under test.",
    }
