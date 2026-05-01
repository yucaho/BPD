from __future__ import annotations

import csv
from pathlib import Path
from typing import Any


def export_scan_csv(scan: dict[str, Any], out_path: str | Path) -> None:
    fields = ["address", "device_name", "local_name", "rssi", "tx_power", "service_uuids", "manufacturer_ids", "seen_count", "first_seen", "last_seen"]
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for d in scan.get("devices", []):
            writer.writerow(
                {
                    "address": d.get("address"),
                    "device_name": d.get("device_name"),
                    "local_name": d.get("local_name"),
                    "rssi": d.get("rssi"),
                    "tx_power": d.get("tx_power"),
                    "service_uuids": ";".join(d.get("service_uuids", [])),
                    "manufacturer_ids": ";".join(d.get("manufacturer_data", {}).keys()),
                    "seen_count": d.get("seen_count"),
                    "first_seen": d.get("first_seen"),
                    "last_seen": d.get("last_seen"),
                }
            )


def export_flipper_summary(scan: dict[str, Any] | None, report: dict[str, Any] | None, out_path: str | Path) -> None:
    lines = ["BLE Profile Inspector", "Passive QA Summary", ""]
    if scan:
        lines.append(f"Scan: {scan.get('created_at', 'n/a')}")
        lines.append(f"Duration: {scan.get('scan_duration_seconds', 'n/a')}s  Devices: {scan.get('device_count', len(scan.get('devices', [])))}")
        top = sorted(scan.get("devices", []), key=lambda d: d.get("rssi") if d.get("rssi") is not None else -999, reverse=True)[:5]
        lines.append("Top devices:")
        for d in top:
            name = d.get("local_name") or d.get("device_name") or "(unnamed)"
            lines.append(f"- {name} {d.get('address', '?')} RSSI {d.get('rssi', 'n/a')}")
        lines.append("")
    if report:
        lines.append(f"Compare Pass: {report.get('pass', False)}")
        matches = report.get("matched_devices", [])
        lines.append(f"Matched: {len(matches)}")
        for d in matches[:5]:
            status = "PASS" if d.get("pass") else "FAIL"
            lines.append(f"- {status} {d.get('name', '')} {d.get('address', '')}")
            for issue in d.get("issues", [])[:2]:
                lines.append(f"  ! {issue}")
    Path(out_path).write_text("\n".join(lines) + "\n", encoding="utf-8")


def make_markdown_summary(report: dict[str, Any]) -> str:
    lines = ["# BLE Profile Inspector Report", ""]
    if "matched_devices" in report:
        lines.append(f"Overall pass: **{report.get('pass')}**")
        for d in report.get("matched_devices", []):
            lines.append(f"- `{d.get('address')}` {d.get('name')} -> {'PASS' if d.get('pass') else 'FAIL'}")
            for issue in d.get("issues", []):
                lines.append(f"  - {issue}")
    else:
        lines.append("Diff report")
        lines.append(f"- Added: {len(report.get('added', []))}")
        lines.append(f"- Removed: {len(report.get('removed', []))}")
        lines.append(f"- Changed: {len(report.get('changed', []))}")
    lines.append("")
    return "\n".join(lines)
