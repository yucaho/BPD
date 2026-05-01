from __future__ import annotations

import asyncio
from datetime import datetime, timezone
from typing import Any

from bleak import BleakScanner

from .models import ObservedDevice, ScanReport
from .utils import hex_bytes, normalize_mfr_id, normalize_uuid
from . import __version__


async def scan_ble(seconds: int) -> dict[str, Any]:
    seen: dict[str, ObservedDevice] = {}

    def on_detect(device, adv_data):
        addr = device.address
        now = datetime.now(timezone.utc).isoformat()
        if addr not in seen:
            seen[addr] = ObservedDevice(address=addr, address_type=getattr(device, "address_type", None), first_seen=now, last_seen=now)
        item = seen[addr]
        item.last_seen = now
        item.seen_count += 1
        item.device_name = device.name
        item.local_name = getattr(adv_data, "local_name", None)
        item.rssi = getattr(adv_data, "rssi", None)
        item.tx_power = getattr(adv_data, "tx_power", None)
        item.service_uuids = [normalize_uuid(x) for x in (getattr(adv_data, "service_uuids", []) or [])]
        item.manufacturer_data = {normalize_mfr_id(k): hex_bytes(v) for k, v in (getattr(adv_data, "manufacturer_data", {}) or {}).items()}
        item.service_data = {normalize_uuid(k): v.hex() if isinstance(v, bytes) else str(v) for k, v in (getattr(adv_data, "service_data", {}) or {}).items()}
        item.platform_data = {"raw": str(getattr(adv_data, "platform_data", None))}

    scanner = BleakScanner(detection_callback=on_detect)
    await scanner.start()
    await asyncio.sleep(seconds)
    await scanner.stop()
    return ScanReport(tool_version=__version__, created_at=datetime.now(timezone.utc).isoformat(), scan_duration_seconds=seconds, devices=list(seen.values())).to_dict()
