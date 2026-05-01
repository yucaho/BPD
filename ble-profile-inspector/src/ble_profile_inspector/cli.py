from __future__ import annotations

import argparse
import asyncio
from pathlib import Path

from .compare import compare_scan, diff_scans
from .export import export_flipper_summary, export_scan_csv, make_markdown_summary
from .rules import default_rules_template, parse_rules
from .scanner import scan_ble
from .utils import load_json, save_json


def main() -> int:
    p = argparse.ArgumentParser(prog="ble-profile-inspector")
    sp = p.add_subparsers(dest="cmd", required=True)

    s = sp.add_parser("scan")
    s.add_argument("--seconds", type=int, default=10)
    s.add_argument("--out", required=True)
    s.add_argument("--csv")

    ir = sp.add_parser("init-rules")
    ir.add_argument("--out", required=True)

    c = sp.add_parser("compare")
    c.add_argument("--scan", required=True)
    c.add_argument("--rules", required=True)
    c.add_argument("--out")
    c.add_argument("--md")
    c.add_argument("--summary")

    d = sp.add_parser("diff")
    d.add_argument("--baseline", required=True)
    d.add_argument("--current", required=True)
    d.add_argument("--out")

    sm = sp.add_parser("summarize")
    sm.add_argument("--scan", required=True)

    ex = sp.add_parser("export")
    ex.add_argument("--scan", required=True)
    ex.add_argument("--csv")
    ex.add_argument("--summary")
    ex.add_argument("--report")

    a = p.parse_args()
    try:
        if a.cmd == "scan":
            result = asyncio.run(scan_ble(a.seconds))
            save_json(a.out, result)
            if a.csv:
                export_scan_csv(result, a.csv)
            if getattr(a, "summary", None):
                export_flipper_summary(result, None, a.summary)
            print(f"Scan complete: {result.get('device_count')} devices -> {a.out}")
        elif a.cmd == "init-rules":
            save_json(a.out, default_rules_template())
            print(f"Wrote rules template to {a.out}")
        elif a.cmd == "compare":
            scan = load_json(a.scan)
            rules = parse_rules(load_json(a.rules))
            report = compare_scan(scan, rules)
            if a.out:
                save_json(a.out, report)
            if a.md:
                Path(a.md).write_text(make_markdown_summary(report), encoding="utf-8")
            if getattr(a, "summary", None):
                export_flipper_summary(scan, report, a.summary)
            print(make_markdown_summary(report))
        elif a.cmd == "diff":
            rep = diff_scans(load_json(a.baseline), load_json(a.current))
            if a.out:
                save_json(a.out, rep)
            print(make_markdown_summary(rep))
        elif a.cmd == "summarize":
            scan = load_json(a.scan)
            print(f"Scan created: {scan.get('created_at')} duration={scan.get('scan_duration_seconds')}s")
            for d in scan.get("devices", []):
                print(f"- {d.get('address')} name={d.get('local_name') or d.get('device_name')} rssi={d.get('rssi')} services={len(d.get('service_uuids', []))}")
        elif a.cmd == "export":
            scan = load_json(a.scan)
            if a.csv:
                export_scan_csv(scan, a.csv)
                print(f"CSV exported to {a.csv}")
            report = load_json(a.report) if a.report else None
            if a.summary:
                export_flipper_summary(scan, report, a.summary)
                print(f"Flipper summary exported to {a.summary}")
            if not a.csv and not a.summary:
                raise ValueError("Provide --csv and/or --summary")
        return 0
    except Exception as exc:
        print(f"Error: {exc}")
        return 1
