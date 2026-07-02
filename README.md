# RoadRunner

RoadRunner is a Linux-based vehicle companion / smart head-unit project.

The initial prototype uses a Microsoft Surface tablet in a 2007 Nissan Pathfinder while keeping the factory Bose stereo. The Surface acts as a companion display and vehicle computer rather than replacing the radio.

## Goals

- Run Android Auto through HuDiY.
- Keep the factory Bose audio system and feed audio through AUX or another low-impact method.
- Log OBD-II data locally.
- Publish vehicle data to Home Assistant.
- Keep trip history in SQLite.
- Eventually support dashcam, backup camera, GPS logging, and vehicle-state automations.

## Current prototype

- Vehicle: 2007 Nissan Pathfinder with Bose audio system
- Tablet: Microsoft Surface Pro 4
- OS: Debian Trixie with KDE Plasma
- Kernel: linux-surface `6.19.8-surface-3`
- Android Auto target: HuDiY
- OBD-II test hardware: cheap ELM327 adapter
- Potential workaround hardware: USB Bluetooth adapter

## Current status

Working:

- Debian installed
- KDE Plasma installed
- linux-surface repository added
- linux-surface kernel installed and booted
- Touchscreen working
- IPTSD virtual touchscreen present
- Wi-Fi working
- Audio working
- Battery percentage working
- Suspend/resume basically working

Known issues / notes:

- Auto-rotation does not work, but this is not important for fixed landscape car mounting.
- Battery state may report oddly, showing plugged in while still discharging.
- Built-in Bluetooth is detected and can scan some BLE advertisements, but pairing/discovery is unreliable.
- Surface Pro 4 built-in wireless/Bluetooth is Marvell, not Intel.
- `mwifiex` logs show firmware bad-state errors after suspend/resume.

See the `docs/` folder for the project log and hardware findings.

## Planned architecture

```text
RoadRunner
├── CarShell / launcher UI
├── roadrunnerd background service
├── VehicleAgent: OBD-II, GPS, trip logging
├── Home Assistant bridge: MQTT/API publishing
├── SQLite local trip database
├── HuDiY launcher/manager
└── CameraService: dashcam / backup camera later
```

## Next milestones

1. Test built-in Bluetooth immediately after a clean boot before suspend.
2. Test a spare USB Bluetooth adapter.
3. If USB Bluetooth works reliably, use it for Android Auto and leave Marvell for Wi-Fi only.
4. Launch HuDiY reliably.
5. Pair phone and test Android Auto.
6. Test Android Auto reconnect after suspend/resume.
7. Connect ELM327 and read basic OBD-II PIDs.
8. Publish first vehicle state payload to Home Assistant over MQTT.
