# OBD-II Notes

## Initial goal

Use the tablet as the OBD-II logger instead of relying on the phone.

RoadRunner should:

- Poll OBD-II data.
- Store samples/trips in SQLite.
- Publish current state to Home Assistant when online.
- Queue data locally when offline.
- Replay queued data or summaries when back online.
- Push odometer/fuel/maintenance data to LubeLogger when reachable.
- Keep the software flexible enough to swap adapters later.

## Why RoadRunner should own OBD logging

For the RoadRunner/Linux-tablet path, adding a separate ESP32 OBD logger adds hardware and complexity. The tablet is already a Linux computer with storage, Bluetooth/USB, SQLite, MQTT, and network sync capabilities.

The ESP32 `obd2-mqtt` approach is more attractive for non-RoadRunner setups such as:

- Android tablet running Headunit Reloaded.
- Cheap portable Android Auto display.
- Aftermarket Android Auto radio.
- Any setup where the display cannot reliably own OBD logging.

For RoadRunner, the preferred path is:

```text
ELM327 / OBDLink
  → RoadRunner VehicleAgent
  → local SQLite
  → MQTT / Home Assistant / LubeLogger / server sync when online
```

## Initial adapter

Start with the cheap ELM327 adapter already available.

This is good enough for proving the concept, even if it is slower or less reliable than better adapters.

## Expected basic PIDs

Initial useful values:

- RPM
- Vehicle speed
- Coolant temperature
- Intake air temperature
- Throttle position
- Engine load
- Short-term fuel trim
- Long-term fuel trim
- Battery/charging voltage if exposed
- Diagnostic trouble codes

## Known limitations of cheap ELM327 adapters

- Slow polling rate
- Bluetooth instability
- Incomplete or buggy command support
- May lock up and need to be unplugged
- Quality varies between units

## Recommended abstraction

RoadRunner should use an adapter abstraction from the start.

Possible implementations:

- ELM327 Bluetooth
- ELM327 USB
- OBDLink CX
- OBDLink EX
- Simulator

This allows the software to start with the cheap adapter and later move to OBDLink hardware without rewriting the application.

## Store-and-forward logging

Every sample should be saved to SQLite first. Network publishing is secondary.

```text
OBD sample
  ├── write to SQLite
  ├── if MQTT connected: publish now
  └── if MQTT offline: mark unsent
```

When connectivity returns:

```text
unsent data
  ├── replay to MQTT / server / LubeLogger as configured
  └── mark sent after success
```

This prevents data loss when:

- Home Assistant reboots.
- The tablet leaves home Wi-Fi.
- The phone hotspot is not active.
- The tablet is offline while driving.
- LubeLogger is unreachable.

## MQTT publishing strategy

Publish current vehicle state as one JSON payload:

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

Home Assistant can parse this into separate MQTT sensors.

Additional topics:

```text
car/pathfinder/availability
car/pathfinder/trip/current
car/pathfinder/trip/last
car/pathfinder/odometer
car/pathfinder/dtc
```

## Replay options

RoadRunner should not force one replay behavior. It should support configurable sync modes:

```text
Replay mode

( ) none
( ) summaries only
( ) full telemetry
```

### None

Only publish new live values after reconnecting. Historical data remains in SQLite and optional server sync.

### Summaries only

Publish trip-ended events, final odometer, fuel estimates, DTCs, and aggregate trip data after reconnecting.

### Full telemetry

Replay every queued OBD sample to MQTT/Home Assistant or a server endpoint.

This can preserve detailed Home Assistant history, but may produce a large burst of messages after a long drive.

## Home Assistant role

Home Assistant should receive pushed data. It should not poll RoadRunner.

RoadRunner can publish live values while online and queued data when back online. If the tablet is offline/asleep, Home Assistant should simply show the last known state and availability.

## Server analytics

If detailed graphs and analytics are desired without accessing a sleeping tablet, sync data to the Docker server when connectivity exists.

Good targets:

- InfluxDB for time-series telemetry.
- Grafana for dashboards.
- PostgreSQL or SQLite for trip analytics.
- LubeLogger for odometer/fuel/maintenance.

Home Assistant can still receive current state and events, but it does not need to be the only historical database.

## LubeLogger sync

LubeLogger stays on the Docker server. RoadRunner only needs to update it when reachable.

Minimum useful sync:

```text
trip ended
  → final odometer calculated or read
  → later, when home Wi-Fi is available
  → POST odometer update to LubeLogger API
```

Future sync options:

- Fuel records entered from the tablet UI.
- Fuel estimates from OBD data.
- Oil change / maintenance events.
- DTC notes.

If Home Assistant already has the odometer entity, HA could call the LubeLogger API via REST command. However, a direct RoadRunner-to-LubeLogger sync or a small server-side bridge may be cleaner long term because RoadRunner already owns the vehicle trip database.

## Future features

- Trip detection
- MPG estimate
- Idle time
- Max speed
- Maintenance reminders
- DTC alerts
- Location at engine-off
- Home Assistant automations based on arrival/departure
- Configurable telemetry replay
- Server-side analytics sync
