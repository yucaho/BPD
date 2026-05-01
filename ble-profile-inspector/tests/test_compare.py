from ble_profile_inspector.compare import compare_scan, diff_scans
from ble_profile_inspector.rules import parse_rules


def test_compare_pass_fail():
    scan = {"devices": [{"address": "A", "local_name": "TempSensor", "rssi": -60, "service_uuids": ["1809"], "manufacturer_data": {"0x004c": "aa"}, "service_data": {"1809": "bb"}}]}
    rules = parse_rules({"match": {"name_contains": "Temp"}, "expected": {"required_service_uuids": ["1809"], "required_manufacturer_ids": ["0x004c"], "required_service_data_uuids": ["1809"]}})
    assert compare_scan(scan, rules)["pass"] is True

    rules2 = parse_rules({"match": {"name_contains": "Temp"}, "expected": {"required_service_uuids": ["9999"]}})
    rep2 = compare_scan(scan, rules2)
    assert rep2["pass"] is False
    assert "Missing required service UUID: 9999" in rep2["matched_devices"][0]["issues"]


def test_diff_added_removed_changed():
    b = {"devices": [{"address": "A", "local_name": "X", "rssi": -50, "service_uuids": ["180f"], "manufacturer_data": {}, "service_data": {}}]}
    c = {"devices": [{"address": "A", "local_name": "X", "rssi": -70, "service_uuids": ["180f", "1809"], "manufacturer_data": {}, "service_data": {}}, {"address": "B", "local_name": "Y"}]}
    d = diff_scans(b, c)
    assert len(d["added"]) == 1
    assert len(d["removed"]) == 0
    assert len(d["changed"]) == 1
