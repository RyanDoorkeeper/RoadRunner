# RoadRunner

RoadRunner is an offline-first vehicle companion / smart head-unit project for a 2007 Nissan Pathfinder. It keeps the factory Bose stereo and adds Android Auto, local vehicle telemetry, trip history, Home Assistant integration, and future camera support.

The project began on a Microsoft Surface Pro 4 as a proof of concept. The intended long-term platform is the Dell Latitude 7210 Rugged Extreme. Surface-specific findings are retained as useful prototype history, while new core software should remain portable to the Latitude.

## Goals

- Run Android Auto through HuDiY.
- Keep the factory Bose audio system and feed audio through AUX or another low-impact method.
- Log OBD-II and GPS data locally.
- Keep trip history in SQLite.
- Publish live vehicle state to Home Assistant when connected.
- Store and forward summaries or telemetry after offline drives.
- Sync detailed history to server-side analytics without waking the tablet.
- Eventually support dashcam, backup camera, maintenance, and vehicle-state automations.

## Platforms

### Surface Pro 4 prototype

- Debian Trixie with KDE Plasma
- linux-surface kernel `6.19.8-surface-3`
- Touchscreen, Wi-Fi, audio, battery reporting, and basic suspend/resume validated
- HuDiY and direct USB Android Auto validated
- Built-in Marvell Bluetooth is unreliable; a USB Bluetooth adapter works better

### Dell Latitude 7210 Rugged Extreme target

- Primary future hardware platform
- Two USB-C ports and one USB-A port
- Rugged chassis and better peripheral flexibility
- OS, charging, suspend/resume, Android Auto, tethering, and audio behavior still require hands-on validation

## Planned architecture

```text
RoadRunner
├── CarShell / touch launcher
├── roadrunnerd background service
├── VehicleAgent: OBD-II, GPS, and normalized vehicle state
├── Trip Manager and SQLite history
├── Sync Manager: MQTT/API store-and-forward
├── HuDiY launcher/manager
└── CameraService: dashcam / backup camera later
```

SQLite on the tablet is the local source of truth. Home Assistant, MQTT, LubeLogger, InfluxDB, Grafana, and other server tools are optional consumers and must not be required for driving or logging.

## Current priorities

1. Bring up and validate the Latitude 7210 Rugged Extreme.
2. Build a minimal VehicleAgent for the generic ELM327 adapter.
3. Store RPM, speed, coolant temperature, and voltage in SQLite.
4. Add reconnect behavior and an OBD simulator.
5. Add trip detection and local history.
6. Publish live MQTT state to Home Assistant.
7. Add durable offline queueing and configurable replay.
8. Add server analytics and LubeLogger synchronization.

## Documentation

- [`docs/context.md`](docs/context.md) — purpose, constraints, and hardware direction
- [`docs/architecture.md`](docs/architecture.md) — system and data-flow design
- [`docs/hardware.md`](docs/hardware.md) — Surface findings and Latitude target hardware
- [`docs/project-log.md`](docs/project-log.md) — chronological experiments and decisions
- [`docs/roadmap.md`](docs/roadmap.md) — prioritized implementation phases
- [`AGENTS.md`](AGENTS.md) — instructions for Codex and other coding agents
