# RoadRunner Development Roadmap

RoadRunner started on a Surface Pro 4, but the target platform is now the Dell Latitude 7210 Rugged Extreme. The Surface remains useful as a proof-of-concept and reference platform; new work should avoid deepening Surface-specific dependencies.

## Proven on the Surface prototype

- Debian Trixie and KDE Plasma boot and operate.
- Touchscreen works with `linux-surface` and IPTSD.
- HuDiY launches.
- Direct USB Android Auto works.
- Navigation, media, album art, and time synchronization work.
- A USB Bluetooth adapter is more reliable than the built-in Marvell controller.
- Local-first telemetry and store-and-forward architecture have been defined.

## Phase 0: Preserve and document the prototype

- Keep Surface-specific setup and troubleshooting in the project log.
- Record working HuDiY launch commands and direct-USB requirements.
- Avoid spending substantial time polishing Surface-only suspend, Marvell, or IPTSD issues unless needed to continue software development.

## Phase 1: Latitude 7210 bring-up

Goal: establish the Latitude as the primary development and vehicle platform.

Tasks:

1. Verify exact CPU, RAM, storage, battery health, BIOS, and Computrace state.
2. Select and install the initial OS.
3. Validate touchscreen, audio, Wi-Fi, Bluetooth, battery reporting, and suspend/resume.
4. Test every USB port alone and concurrently.
5. Test HuDiY and direct USB Android Auto.
6. Test USB Android Auto through the proposed dock or hub.
7. Test USB tethering while Android Auto is active.
8. Test analog AUX and USB audio paths.
9. Document all Latitude-specific setup under `docs/`.

Acceptance criteria:

- Normal use requires no terminal or keyboard.
- Android Auto launches reliably.
- Touch, audio, networking, and attached devices survive repeated sleep/wake cycles.
- The tablet can charge while the required data peripherals are connected.

## Phase 2: VehicleAgent minimum viable prototype

Do not start with a full dashboard.

```text
connect to OBD adapter
  -> read RPM, speed, coolant temperature, and voltage
  -> write timestamped samples to SQLite
  -> expose current state locally
```

Acceptance criteria:

- Supports the generic ELM327 test adapter.
- Reconnects after adapter loss.
- Does not corrupt the database after interruption.
- Includes a simulator for development outside the vehicle.
- Keeps platform-specific device discovery outside the core logic.

## Phase 3: Trip detection and local history

- Add trip state machine.
- Record trip start/end, duration, distance, and summary statistics.
- Add GPS input after OBD logging is stable.
- Store all data locally without requiring Internet access.
- Add retention and database-maintenance policies.

## Phase 4: MQTT and Home Assistant

- Publish live state when online.
- Add availability and last-seen status.
- Use Home Assistant MQTT discovery where practical.
- Publish trip-start and trip-end events.
- Keep SQLite as the authoritative history.

Initial topic namespace:

```text
roadrunner/pathfinder/availability
roadrunner/pathfinder/state
roadrunner/pathfinder/trip/current
roadrunner/pathfinder/trip/last
roadrunner/pathfinder/events
```

## Phase 5: Offline queue and replay

- Queue outbound records durably.
- Retry with backoff after connectivity returns.
- Support replay policies: none, summaries only, or full telemetry.
- Prevent duplicate ingestion with stable message IDs.
- Cap queue growth and report dropped data explicitly.

## Phase 6: Server analytics and LubeLogger

- Sync detailed telemetry to InfluxDB, PostgreSQL, or a RoadRunner server endpoint.
- Build Grafana dashboards without waking the tablet.
- Update LubeLogger odometer and trip-related records when connected.
- Keep Home Assistant focused on current state, alerts, and automations.

## Phase 7: Vehicle appliance shell

- Large touch controls and landscape layout.
- Automatic startup and simple recovery.
- Status page for OBD, GPS, MQTT, storage, and phone connection.
- HuDiY launcher/manager.
- Minimal interaction while moving.

## Phase 8: Automotive power and permanent installation

- Select an automotive-rated USB-C PD supply.
- Add fused wiring and accessory-power awareness.
- Define wake, suspend, grace-period, and shutdown behavior.
- Validate battery drain, cranking behavior, cold weather, and summer heat.
- Install a secure, airbag-safe mount and strain-relieved cabling.

## Later phases

- Backup camera
- Dashcam
- Fuel-entry workflow
- Maintenance reminders
- Remote status through VPN or secure broker
- Camping-van profile and multi-vehicle support
- Voice controls only after the core system is reliable

## Priority order

```text
Latitude bring-up
  -> OBD + SQLite
  -> trip detection
  -> MQTT/Home Assistant
  -> offline sync
  -> analytics/LubeLogger
  -> polished shell
  -> permanent power and mounting
  -> cameras and extras
```
