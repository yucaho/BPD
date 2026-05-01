from ble_profile_inspector.rules import parse_rules
from ble_profile_inspector.utils import normalize_mfr_id, normalize_uuid


def test_uuid_normalization():
    assert normalize_uuid(" 180F ") == "180f"


def test_mfr_normalization():
    assert normalize_mfr_id("76") == "0x004c"
    assert normalize_mfr_id("0x4C") == "0x004c"


def test_rule_parsing_normalizes_values():
    rules = parse_rules({"match": {"required_any_service_uuid": ["180F"], "manufacturer_id": "76"}})
    assert rules.match.required_any_service_uuid == ["180f"]
    assert rules.match.manufacturer_id == "0x004c"
