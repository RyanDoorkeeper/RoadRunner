# Hardware Notes

## Vehicle

- 2007 Nissan Pathfinder
- Factory Bose audio system
- Plan is not to replace the factory radio initially
- Audio quality target: good enough; current baseline is Bluetooth-to-AUX through a Roav adapter

## Tablet

Prototype tablet:

- Microsoft Surface Pro 4
- Debian Trixie
- KDE Plasma
- linux-surface kernel

### Surface hardware status

| Component | Status | Notes |
|---|---|---|
| Touchscreen | Working | Works after linux-surface kernel + iptsd |
| Wi-Fi | Working | Built-in Marvell chipset |
| Bluetooth | Partially working | Adapter visible and scans BLE advertisements, but pairing unreliable |
| Audio | Working | Needs later AUX/pathfinder audio test |
| Battery percentage | Working | Charging state may be inaccurate |
| Suspend/resume | Working | Marvell firmware may enter bad state after suspend |
| Auto-rotation | Not working | Not important for fixed landscape mount |
| Cameras | Not tested | Not critical yet |

## Bluetooth / Wi-Fi chipset

The Surface Pro 4 uses Marvell wireless hardware:

```text
1286:204C Marvell Semiconductor, Inc. Bluetooth and Wireless LAN Composite
```

The relevant Linux driver is `mwifiex` / `mwifiex_pcie`.

Observed behavior:

- Wi-Fi works.
- Bluetooth service runs.
- Bluetooth controller appears in `bluetoothctl`.
- BLE advertisements can be seen.
- Pairing/discovery is unreliable.
- After suspend/resume, `mwifiex` may report firmware bad-state errors.

Potential mitigation:

- Use the built-in Marvell adapter for Wi-Fi.
- Use a USB Bluetooth adapter for reliable Android Auto / HuDiY pairing.

## OBD-II

Initial test adapter:

- Cheap ELM327 adapter

Expected initial PIDs:

- RPM
- Vehicle speed
- Coolant temperature
- Intake air temperature
- Throttle position
- Engine load
- Fuel trims
- Battery/charging voltage if supported
- Diagnostic trouble codes

Future possible upgrade:

- OBDLink CX for Bluetooth
- OBDLink EX for wired USB

Design note:

RoadRunner should abstract the OBD adapter so the rest of the software does not care whether the source is ELM327, OBDLink, or a simulator.

## Possible future hardware

- Automotive power supply / USB-C PD charger
- Solid tablet mount, likely RAM Mount or ProClip-style
- USB hub
- USB Bluetooth adapter
- USB GPS receiver if needed
- USB camera or capture device for dashcam
- Backup camera input/capture device
