from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class ObservedDevice:
    address: str
    address_type: str | None = None
    device_name: str | None = None
    local_name: str | None = None
    rssi: int | None = None
    tx_power: int | None = None
    service_uuids: list[str] = field(default_factory=list)
    manufacturer_data: dict[str, str] = field(default_factory=dict)
    service_data: dict[str, str] = field(default_factory=dict)
    platform_data: dict[str, Any] = field(default_factory=dict)
    first_seen: str = field(default_factory=utc_now_iso)
    last_seen: str = field(default_factory=utc_now_iso)
    seen_count: int = 1

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class ScanReport:
    tool_version: str
    created_at: str
    scan_duration_seconds: int
    devices: list[ObservedDevice]

    def to_dict(self) -> dict[str, Any]:
        return {
            "tool_version": self.tool_version,
            "created_at": self.created_at,
            "scan_duration_seconds": self.scan_duration_seconds,
            "device_count": len(self.devices),
            "devices": [d.to_dict() for d in self.devices],
        }
