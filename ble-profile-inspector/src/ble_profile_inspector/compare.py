from __future__ import annotations

from typing import Any

from .rules import ProfileRules
from .utils import normalize_mfr_id, normalize_uuid


def _name(d: dict[str, Any]) -> str:
    return d.get("local_name") or d.get("device_name") or ""


def device_matches(device: dict[str, Any], rules: ProfileRules) -> bool:
    n = _name(device).lower()
    addr = str(device.get("address", "")).lower()
    services = {normalize_uuid(x) for x in device.get("service_uuids", [])}
    mfr_ids = {normalize_mfr_id(k) for k in device.get("manufacturer_data", {}).keys()}
    m = rules.match
    if m.name_contains and m.name_contains.lower() not in n:
        return False
    if m.address_contains and m.address_contains.lower() not in addr:
        return False
    if m.required_any_service_uuid and not (set(m.required_any_service_uuid) & services):
        return False
    if m.manufacturer_id and m.manufacturer_id not in mfr_ids:
        return False
    return True


def compare_scan(scan: dict[str, Any], rules: ProfileRules) -> dict[str, Any]:
    matched = []
    for d in scan.get("devices", []):
        if device_matches(d, rules):
            matched.append(_evaluate(d, rules))
    if not matched:
        return {
            "profile_name": rules.profile_name,
            "pass": False,
            "matched_devices": [],
            "troubleshooting": [
                "No devices matched match criteria.",
                "Confirm adapter is enabled and nearby.",
                "Loosen filters (name/address/service UUID/manufacturer ID).",
            ],
        }
    return {"profile_name": rules.profile_name, "pass": all(x["pass"] for x in matched), "matched_devices": matched}


def _evaluate(device: dict[str, Any], rules: ProfileRules) -> dict[str, Any]:
    issues: list[str] = []
    exp = rules.expected
    services = {normalize_uuid(x) for x in device.get("service_uuids", [])}
    mfr_ids = {normalize_mfr_id(k) for k in device.get("manufacturer_data", {}).keys()}
    svc_data = {normalize_uuid(k) for k in device.get("service_data", {}).keys()}
    name = _name(device)

    for uuid in exp.required_service_uuids:
        if uuid not in services:
            issues.append(f"Missing required service UUID: {uuid}")
    for uuid in exp.forbidden_service_uuids:
        if uuid in services:
            issues.append(f"Forbidden service UUID present: {uuid}")
    for mid in exp.required_manufacturer_ids:
        if mid not in mfr_ids:
            issues.append(f"Missing manufacturer ID: {mid}")
    for su in exp.required_service_data_uuids:
        if su not in svc_data:
            issues.append(f"Missing service data UUID: {su}")
    rssi = device.get("rssi")
    if exp.min_rssi is not None and (rssi is None or rssi < exp.min_rssi):
        issues.append(f"RSSI below minimum ({exp.min_rssi}): {rssi}")
    if exp.max_rssi is not None and (rssi is None or rssi > exp.max_rssi):
        issues.append(f"RSSI above maximum ({exp.max_rssi}): {rssi}")
    if exp.required_name_prefix and not name.startswith(exp.required_name_prefix):
        issues.append(f"Name missing prefix: {exp.required_name_prefix}")
    if exp.required_name_contains and exp.required_name_contains not in name:
        issues.append(f"Name missing substring: {exp.required_name_contains}")

    return {"address": device.get("address"), "name": name, "pass": not issues, "issues": issues, "observed": device}


def diff_scans(baseline: dict[str, Any], current: dict[str, Any]) -> dict[str, Any]:
    base_map = {d.get("address"): d for d in baseline.get("devices", [])}
    curr_map = {d.get("address"): d for d in current.get("devices", [])}
    added = [curr_map[a] for a in curr_map.keys() - base_map.keys()]
    removed = [base_map[a] for a in base_map.keys() - curr_map.keys()]
    changed = []
    for addr in base_map.keys() & curr_map.keys():
        b, c = base_map[addr], curr_map[addr]
        delta = {}
        for key in ["rssi", "device_name", "local_name", "service_uuids", "manufacturer_data", "service_data"]:
            if b.get(key) != c.get(key):
                delta[key] = {"baseline": b.get(key), "current": c.get(key)}
        if delta:
            changed.append({"address": addr, "changes": delta})
    return {
        "added": added,
        "removed": removed,
        "changed": changed,
        "secondary_name_matches": _secondary_name_matches(removed, added),
    }


def _secondary_name_matches(removed: list[dict[str, Any]], added: list[dict[str, Any]]) -> list[dict[str, Any]]:
    out = []
    for r in removed:
        rn = _name(r).strip().lower()
        if not rn:
            continue
        for a in added:
            if rn and rn == _name(a).strip().lower():
                out.append({"removed_address": r.get("address"), "added_address": a.get("address"), "name": rn})
    return out
