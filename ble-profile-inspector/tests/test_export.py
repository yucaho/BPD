from pathlib import Path

from ble_profile_inspector.export import export_flipper_summary, export_scan_csv


def test_csv_export(tmp_path: Path):
    out = tmp_path / "scan.csv"
    scan = {"devices": [{"address": "A", "device_name": "D", "local_name": "L", "rssi": -60, "tx_power": -4, "service_uuids": ["180f"], "manufacturer_data": {"0x004c": "aa"}, "seen_count": 1, "first_seen": "t1", "last_seen": "t2"}]}
    export_scan_csv(scan, out)
    text = out.read_text(encoding="utf-8")
    assert "address" in text
    assert "0x004c" in text


def test_flipper_summary_export(tmp_path: Path):
    out = tmp_path / "live_summary.txt"
    scan = {"created_at": "now", "scan_duration_seconds": 10, "device_count": 1, "devices": [{"address": "A", "local_name": "Dev", "rssi": -50}]}
    report = {"pass": True, "matched_devices": [{"name": "Dev", "address": "A", "pass": True, "issues": []}]}
    export_flipper_summary(scan, report, out)
    text = out.read_text(encoding="utf-8")
    assert "BLE Profile Inspector" in text
    assert "Compare Pass: True" in text
