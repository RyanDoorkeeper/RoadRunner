# RoadRunner Architecture

## Design idea

RoadRunner should be the orchestration layer for the vehicle computer.

HuDiY handles Android Auto / CarPlay. RoadRunner should not attempt to reimplement Android Auto. Instead, it should launch and manage HuDiY alongside vehicle-specific services.

## High-level layout

```text
Linux / KDE / Surface

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
│   └── MQTT publishing
│
├── HuDiY
│   ├── Android Auto
│   └── optional CarPlay
│
└── CameraService
    ├── dashcam later
    └── backup camera later
```

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
- Restart Bluetooth/Wi-Fi services if needed.
- Expose status to the UI.

## VehicleAgent

VehicleAgent should start simple and be written in a fast-to-iterate language such as Python.

Initial responsibilities:

- Connect to ELM327 adapter.
- Poll basic OBD-II PIDs.
- Save current values.
- Publish JSON state to MQTT.
- Store trips/history in SQLite.

Future responsibilities:

- GPS logging.
- Trip start/stop detection.
- Maintenance tracking.
- DTC reading/clearing.
- Fuel economy estimates.
- Home Assistant device discovery.

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
  "trip_miles": 18.3
}
```

Home Assistant can then create MQTT sensors from the JSON attributes.

## Local storage

SQLite should be the local source of truth for historical data.

Home Assistant is good for current state and automations. RoadRunner should keep its own trip and maintenance history.

Possible tables:

- trips
- samples
- dtcs
- maintenance_events
- locations
- system_events

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
