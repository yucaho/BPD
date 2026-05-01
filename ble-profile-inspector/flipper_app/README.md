# Flipper Zero BLE Profile Inspector (Standalone v1)

This app now runs directly on Flipper Zero without requiring PC-side command execution.

## What it does on-device
- Provides a standalone QA/debug session screen.
- Lets you start/stop a passive-scan session state using **OK**.
- Tracks per-session counters shown live on screen:
  - Scan runs
  - Observed advertisement packet count (session counter)
  - Strongest RSSI seen (session counter)

> Note: v1 keeps firmware integration intentionally lightweight. The scan counters are wired as a firmware-agnostic placeholder so the app remains buildable across firmware variants. A firmware-specific implementation can replace the placeholder increments with native passive BLE advertisement callbacks.

## Controls
- **OK**: Start/stop passive scan session
- **BACK**: Exit

## Build with uFBT
```bash
pip install ufbt
cd flipper_app
ufbt launch
```

## Next firmware-specific extension point
In `ble_profile_inspector.c`, replace the placeholder block in `app_input_callback()` with native BLE scanner start/stop and advertisement callback updates.
