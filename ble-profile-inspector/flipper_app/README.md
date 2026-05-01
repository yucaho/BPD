# Flipper Zero BLE Profile Inspector (Standalone v1)

This app runs directly on Flipper Zero.

## Behavior
- Press **OK** to start a passive scan session.
- While scanning, the app shows an **active advertisement count** and per-device detail rows (visual box-style rows).
- Press **BACK** while scanning to stop scan.
- Press **BACK** again (from idle) to exit app.

## Screen layout
- Header with scan status.
- Active advertisement count.
- Up to 3 advertisement detail rows, each with:
  - Device name
  - RSSI
  - Service UUID shorthand

> Current implementation uses firmware-agnostic placeholder advertisement rows for compatibility. Replace the placeholder refresh function with firmware-native BLE advertisement callbacks for live radio data.

## Build with uFBT
```bash
pip install ufbt
cd flipper_app
ufbt launch
```
