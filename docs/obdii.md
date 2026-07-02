# OBD-II Notes

## Initial goal

Use the Surface as the OBD-II logger instead of relying on the phone.

RoadRunner should:

- Poll OBD-II data.
- Store samples/trips in SQLite.
- Publish current state to Home Assistant.
- Keep the software flexible enough to swap adapters later.

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

## MQTT idea

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
  "trip_miles": 18.3
}
```

Home Assistant can parse this into separate MQTT sensors.

## Local data

SQLite should store detailed trip and sample history.

Home Assistant should primarily receive current state and high-level derived values.

## Future features

- Trip detection
- MPG estimate
- Idle time
- Max speed
- Maintenance reminders
- DTC alerts
- Location at engine-off
- Home Assistant automations based on arrival/departure
