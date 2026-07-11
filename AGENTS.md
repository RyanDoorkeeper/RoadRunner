# RoadRunner Agent Instructions

## Project intent

RoadRunner is an offline-first vehicle companion for a 2007 Nissan Pathfinder. It began on a Microsoft Surface Pro 4, but the target platform is the Dell Latitude 7210 Rugged Extreme. Treat Surface-specific work as prototype history and keep new core code portable to the Latitude.

Read these files before making architectural changes:

- `docs/context.md`
- `docs/architecture.md`
- `docs/hardware.md`
- `docs/project-log.md`
- `docs/roadmap.md`

## Engineering rules

- Local SQLite storage is the source of truth.
- Home Assistant, MQTT, LubeLogger, and server analytics are optional consumers.
- Driving and logging must work without Internet access.
- The UI must not own OBD, GPS, trip, or sync connections.
- Keep platform-specific code behind adapters.
- Do not couple core code to `linux-surface`, Marvell Bluetooth, fixed Linux device paths, or a particular COM port.
- OBD access is read-only by default. Do not add ECU writing, flashing, coding, or immobilizer functions.
- A failed integration must not stop local logging.
- Include a simulator or test double for hardware-facing components.
- Prefer small, reviewable changes and update relevant documentation with behavior changes.

## Initial implementation direction

The first software milestone is a minimal VehicleAgent that:

1. Connects to an ELM327-class adapter.
2. Reads a small set of standard PIDs.
3. Stores timestamped data in SQLite.
4. Survives disconnect and reconnect.
5. Exposes current state locally.
6. Runs against a simulator away from the vehicle.

Do not begin with a large dashboard, camera system, voice assistant, or cloud dependency.

## Data and sync expectations

- Persist before publishing.
- Use stable timestamps and message identifiers.
- Queue outbound data durably.
- Make replay policy configurable: none, summaries only, or full telemetry.
- Avoid duplicate ingestion after retries.
- Report data loss or queue trimming explicitly.

## Safety and usability

- Avoid designs that require interaction while driving.
- Use large touch targets and landscape layouts.
- Do not obstruct or control safety-critical vehicle functions.
- Do not assume permanent cellular service.
- Fail safely and provide simple recovery actions.

## Documentation discipline

The repository documentation is authoritative. Chat transcripts are historical input only. When a decision changes, update the appropriate document and preserve important superseded decisions in the project log rather than silently deleting their history.
