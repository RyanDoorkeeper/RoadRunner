# RoadRunner Architecture

## Design idea

RoadRunner should be the orchestration layer for the vehicle computer.

HuDiY handles Android Auto / CarPlay. RoadRunner should not attempt to reimplement Android Auto. Instead, it should launch and manage HuDiY alongside vehicle-specific services.

## High-level layout

```text
Linux / KDE / Surface or Latitude tablet

├── RoadRunner UI / CarShell
│   ├── Android Auto tile
│   ├── Vehicle tile
│   ├── Home Assistant tile
│   ├── Cameras tile
│   └── Settings tile
│
├── roadrunnerd
│   ├── service supervisor
│   ├── startup/shutdown behavior
│   ├── suspend/resume handling
│   └── app/window state coordination
│
├── VehicleAgent
│   ├── OBD-II polling
│   ├── GPS tracking
│   ├── trip detection
│   ├── SQLite history
│   ├── MQTT publishing
│   └── store-and-forward sync
│
├── HuDiY
│   ├── Android Auto
│   └── optional CarPlay
│
└── CameraService
    ├── dashcam later
    └── backup camera later
```

## Core data principle

SQLite on the tablet is the local source of truth for vehicle telemetry and trip history.

Home Assistant, MQTT, LubeLogger, InfluxDB, Grafana, and any future RoadRunner server are consumers of data. They should not be required for the vehicle system to keep logging.

This matters because the tablet may not have Internet while driving. It may only have connectivity when parked in the garage or when USB tethering / hotspot / LTE is available.

## Connectivity modes

RoadRunner should support at least two telemetry modes.

### Live mode

When MQTT or the sync server is reachable:

```text
OBD sample
  ├── save immediately to SQLite
  └── publish immediately to MQTT / server
```

This gives Home Assistant real-time sensors similar to the current Torque setup.

### Store-and-forward mode

When MQTT or the sync server is unreachable:

```text
OBD sample
  ├── save immediately to SQLite
  └── mark as unsent
```

When the tablet reconnects to home Wi-Fi, USB tethering, hotspot, or LTE:

```text
unsent samples / trip summaries
  ├── publish in order
  ├── mark sent after acknowledgement
  └── keep local SQLite history either way
```

The replay behavior should be configurable:

```text
Replay mode

( ) none
( ) summaries only
( ) full telemetry
```

The ideal default may be current-state plus trip summaries, with full telemetry replay available for users who want Home Assistant history to mirror the entire drive.

## Home Assistant role

Home Assistant should receive pushed data. It should not poll the tablet.

Possible MQTT topics:

```text
car/pathfinder/state
car/pathfinder/availability
car/pathfinder/trip/current
car/pathfinder/trip/last
car/pathfinder/odometer
car/pathfinder/maintenance
```

Home Assistant is best used for:

- Current state sensors.
- Availability / last seen.
- Alerts and automations.
- High-level trip events.
- Odometer state.
- Maintenance-related automations.

Home Assistant can receive full telemetry if desired, but RoadRunner should not depend on HA to preserve data.

## Server-side analytics

If the user wants graphs and analytics without waking or remote-accessing a sleeping tablet, RoadRunner should sync data to a server when connectivity exists.

Recommended split:

```text
Tablet / RoadRunner = capture + local buffer
Docker server = history + graphs + analytics + maintenance tools
```

Possible server components:

- MQTT broker for live and replayed state.
- InfluxDB for time-series telemetry.
- Grafana for graphs.
- PostgreSQL or SQLite for structured trip history.
- LubeLogger for odometer, fuel, and maintenance.
- Optional RoadRunner Server API to receive uploads from the tablet.

For detailed graphs, prefer InfluxDB/Grafana or a RoadRunner server database over relying only on Home Assistant history.

## Android Auto and Internet

Wireless Android Auto usually uses the phone's Wi-Fi radio for the head-unit link, so the tablet should not assume it can also join the phone's hotspot at the same time.

Practical connectivity options:

1. USB Android Auto plus USB tethering from the phone.
2. Separate phone hotspot when not using wireless Android Auto.
3. Dedicated LTE/5G modem or tablet SIM.
4. Offline while driving, then sync on home Wi-Fi.

USB Android Auto plus USB tethering may be the best technical path if live Home Assistant updates are desired while driving, because it can provide both Android Auto and Internet over the same physical phone connection.

## RoadRunner UI / CarShell

The tablet should not feel like a normal desktop in the vehicle. The user-facing UI should be large, touch-friendly, and appliance-like.

Proposed main screen:

```text
+----------------------------------+
|            Pathfinder            |
|                                  |
|        Android Auto              |
|        Vehicle                   |
|        Home Assistant            |
|        Cameras                   |
|        Settings                  |
+----------------------------------+
```

## roadrunnerd

A background daemon should eventually manage system state.

Responsibilities:

- Start RoadRunner UI after login.
- Launch HuDiY when requested.
- Recover from HuDiY crash or exit.
- Watch suspend/resume events.
- Flush SQLite data before suspend if needed.
- Restart Bluetooth/Wi-Fi/touch services if needed.
- Expose status to the UI.

## VehicleAgent

VehicleAgent should start simple and be written in a fast-to-iterate language such as Python.

Initial responsibilities:

- Connect to ELM327 adapter.
- Poll basic OBD-II PIDs.
- Save current values.
- Publish JSON state to MQTT when available.
- Store trips/history in SQLite.
- Queue unsent telemetry when offline.
- Replay queued telemetry or summaries when connectivity returns.

Future responsibilities:

- GPS logging.
- Trip start/stop detection.
- Maintenance tracking.
- DTC reading/clearing.
- Fuel economy estimates.
- Home Assistant device discovery.
- Server sync for analytics.
- LubeLogger odometer/fuel sync.

## MQTT state format idea

Publish a single JSON state payload initially:

```text
car/pathfinder/state
```

Example:

```json
{
  "rpm": 2140,
  "speed_mph": 58,
  "coolant_f": 189,
  "voltage": 13.9,
  "trip_miles": 18.3,
  "odometer_miles": 187312,
  "engine_running": true
}
```

Home Assistant can then create MQTT sensors from the JSON attributes.

## Local storage

SQLite should be the local source of truth for historical data.

Possible tables:

- trips
- samples
- outbound_queue
- sync_state
- dtcs
- maintenance_events
- locations
- system_events

The `outbound_queue` table should allow durable store-and-forward behavior for MQTT, LubeLogger, and server sync targets.

## Adapter abstraction

The OBD layer should not be hard-coded to a specific adapter.

Suggested interface:

```text
OBDAdapter
├── connect()
├── disconnect()
├── read_pid()
├── read_dtc()
├── clear_dtc()
└── adapter_info()
```

Implementations:

- ELM327 Bluetooth
- ELM327 USB
- OBDLink CX
- OBDLink EX
- Simulator

A simulator should be built early so the UI and MQTT integration can be developed without sitting in the vehicle.
