# Project Context

## Purpose

RoadRunner turns a tablet into an offline-first vehicle companion for the 2007 Nissan Pathfinder. It adds navigation projection, vehicle telemetry, trip history, automations, and future camera features while retaining the factory Bose radio.

RoadRunner is a companion display and vehicle computer, not a replacement for the factory radio or safety-critical vehicle systems.

## Current prototype

- Vehicle: 2007 Nissan Pathfinder with factory Bose audio
- Tablet: Microsoft Surface Pro 4
- Operating system: Debian Trixie with KDE Plasma
- Kernel: linux-surface
- Android Auto: HuDiY
- OBD-II: generic ELM327-class adapter for initial development
- Local persistence: SQLite
- Home integration: Home Assistant through MQTT or an API bridge
- Server analytics: optional sync to the home Docker environment

## Design priorities

1. **Offline operation.** Driving, logging, and trip detection must continue without Internet or Home Assistant.
2. **Reliability over elegance.** A reliable external adapter is preferable to unstable built-in hardware.
3. **Local-first data ownership.** Raw readings and trip records are stored locally before any network transmission.
4. **Graceful degradation.** Android Auto, OBD, GPS, networking, and server sync should fail independently.
5. **Touch-first operation.** Common functions must be usable in landscape mode with large controls and minimal interaction.
6. **Safe behavior.** RoadRunner must not require distracting interaction while driving and must never control safety-critical vehicle functions.
7. **Replaceable components.** OBD adapters, GPS receivers, connectivity methods, and UI components should be abstracted behind stable interfaces.
8. **Multi-vehicle potential.** The architecture should eventually support the camping van or another vehicle without forking the entire application.

## Non-goals for the first release

- Replacing the factory radio
- Writing to vehicle ECUs
- Performing coding, flashing, immobilizer, or security functions
- Depending on permanent cellular service
- Uploading every sample to Home Assistant as the sole historical database
- Building a full autonomous voice assistant before the core vehicle service is stable

## Operating model

RoadRunner should behave like an appliance:

1. Wake or boot.
2. Start the background service.
3. Detect available OBD, GPS, Bluetooth, and network devices.
4. Restore the last safe state.
5. Begin or resume trip detection.
6. Launch the touch shell and HuDiY as appropriate.
7. Log locally at all times.
8. Publish live data when connected.
9. Upload queued summaries or telemetry after connectivity returns.
10. Shut down or suspend cleanly after vehicle-off conditions are met.

## Source of truth

The repository documentation is the project source of truth. Chat transcripts are historical input, not authoritative specifications. When implementation and documentation disagree, update the documentation as part of the same change once the intended behavior is confirmed.
