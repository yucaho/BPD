# ble-profile-inspector

Passive BLE advertisement/profile debugging tool for **owned devices, lab QA, and consent-based firmware validation**.

## Safety scope
- Passive BLE advertisement inspection only.
- No deauth/jamming/spoofing/pairing bypass/credential capture/exploit logic.
- No long-term tracking database by default.
- Does not attempt to defeat randomized BLE addresses.

## Project layout
- Python CLI core in `src/ble_profile_inspector`.
- Flipper Zero app in `flipper_app/`.

## Installation

### Python CLI (Linux/macOS)
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install -e .
```

### Python CLI (Windows PowerShell)
```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
pip install -e .
```

### Flipper app build toolchain
```bash
pip install ufbt
cd flipper_app
ufbt launch
```

## Usage

### CLI commands
- `scan`
- `init-rules`
- `compare`
- `diff`
- `summarize`
- `export`

### End-to-end CLI workflow
```bash
python -m ble_profile_inspector init-rules --out expected_profile.json
python -m ble_profile_inspector scan --seconds 20 --out latest_scan.json --csv latest_scan.csv
python -m ble_profile_inspector summarize --scan latest_scan.json
python -m ble_profile_inspector compare --scan latest_scan.json --rules expected_profile.json --out comparison_report.json --md comparison_report.md --summary live_summary.txt
python -m ble_profile_inspector diff --baseline baseline_scan.json --current latest_scan.json --out diff_report.json
python -m ble_profile_inspector export --scan latest_scan.json --csv latest_scan.csv --report comparison_report.json --summary live_summary.txt
```

### Windows PowerShell CLI examples
```powershell
python -m ble_profile_inspector scan --seconds 20 --out latest_scan.json --csv latest_scan.csv
python -m ble_profile_inspector compare --scan latest_scan.json --rules expected_profile.json --out comparison_report.json
```

## Flipper Zero standalone usage
The Flipper app runs on-device and does not require runtime PC interaction to show session output.

Controls:
- **OK** toggles passive scan session state.
- **BACK** exits.

On-screen output:
- Session status (idle/scanning)
- Scan run count
- Observed advertisement packet count (session counter)
- Strongest RSSI seen (session counter)

## Troubleshooting BLE scanning
- Ensure Bluetooth adapter is present and enabled.
- Linux may require permissions/capabilities and active DBus/Bluetooth daemon.
- Windows: verify adapter drivers and Bluetooth service state.
- macOS: ensure terminal/app has Bluetooth permissions.

## Current status
### Works now
- Full Python CLI workflow for scan/rules/compare/diff/summarize/export.
- Flipper standalone app loop for on-device session control and live counters.
- Unit tests that run without BLE hardware.

### Stubbed for later
- Firmware-specific BLE callback wiring in Flipper app is a compatibility placeholder in v1.
- Replace placeholder counters with native passive BLE advertisement callbacks per firmware API.
