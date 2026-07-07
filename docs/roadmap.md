# RoadRunner Development Roadmap

This roadmap is focused on the current Surface Pro 4 development platform. The goal is to prove RoadRunner as a reliable vehicle appliance before adding optional features such as cameras, advanced dashboards, or server analytics.

## Current priority

The current Surface setup is usable enough to stop chasing every Linux paper cut and start proving the RoadRunner concept.

Already proven:

- Debian Trixie + KDE Plasma boots on the Surface Pro 4.
- linux-surface kernel is installed and running.
- Touchscreen works after cold boot.
- HuDiY launches.
- USB Android Auto works with direct cable connection.
- Navigation, media, album art, and time sync work in Android Auto.
- Baseus USB Bluetooth adapter works better than the internal Marvell Bluetooth controller.

Main remaining platform concern:

- Touchscreen may stop responding after suspend/resume.

## Phase 0: Car appliance milestone

Before adding more integrations, make the tablet feel like it belongs in a car.

Goal:

```text
Power on / wake
  → auto login
  → RoadRunner or HuDiY-ready launcher
  → one tap to Android Auto
  → no terminal or desktop interaction during normal use
```

Acceptance criteria:

- Boots or wakes without manual Linux maintenance.
- Screen stays on while driving.
- HuDiY launches with one tap or automatically.
- Android Auto starts reliably over direct USB.
- No keyboard or terminal needed for a normal drive.
- If something fails, there is a simple recovery action.

## Phase 1: Surface reliability

### 1. Characterize touchscreen after suspend

This is the highest-priority Surface issue.

Observed behavior:

- Touch works after cold boot.
- Android Auto worked during a drive.
- After returning to the vehicle and waking the Surface, the touchscreen appeared unresponsive.

Next tests:

1. Reproduce the issue intentionally.
2. When touch fails, try:

```bash
sudo systemctl restart iptsd
```

3. Check whether touch returns immediately.
4. Test the same behavior under KDE X11 instead of Wayland.
5. Record whether USB mouse/keyboard still works when touch fails.
6. Record whether the issue happens after suspend only, or also after screen blanking.

Possible workaround:

- Add a resume hook that restarts `iptsd` after wake if needed.

### 2. Repeated suspend/resume test

Run several controlled suspend/resume cycles.

Suggested test:

```text
Start HuDiY
Connect Android Auto
Suspend
Wake
Wait 2-5 minutes
Repeat 10-20 times
```

Track failures:

- Touchscreen
- USB Android Auto
- USB Bluetooth adapter
- Wi-Fi
- Audio
- HuDiY projection
- KDE/Wayland window behavior

### 3. HuDiY startup polish

Current Android Auto behavior is functional but still too manual.

Desired behavior:

```text
Power on / wake
  → RoadRunner launcher
  → HuDiY ready
  → phone plugged in
  → Android Auto starts
```

Tasks:

- Determine the reliable HuDiY launch command.
- Determine whether HuDiY should autostart at login.
- Test 1920x1440 or 1920x1080 at 100% scaling.
- Test Wayland vs X11 if Android Auto projection/window embedding remains odd.
- Confirm direct USB works with a known-good cable.
- Confirm whether the USB hub is reliable or should be avoided.

## Phase 2: VehicleAgent proof of concept

Do not start with a full UI.

The first real software milestone should be a minimal VehicleAgent that proves the OBD logging concept.

Minimum viable test:

```text
connect to OBD adapter
  → read RPM
  → write to SQLite
  → print values to terminal
```

Acceptance criteria:

- Connects to the cheap ELM327 adapter or selected OBD adapter.
- Reads at least RPM, speed, coolant temp, and voltage if available.
- Stores timestamped samples in SQLite.
- Survives disconnect/reconnect without corrupting the database.

No MQTT, Home Assistant, LubeLogger, Grafana, or GUI should be required for this milestone.

## Phase 3: MQTT and Home Assistant

After SQLite logging works:

- Publish live MQTT state when online.
- Use Home Assistant MQTT discovery where practical.
- Add availability status.
- Keep SQLite as the source of truth.

Initial topics:

```text
car/pathfinder/state
car/pathfinder/availability
car/pathfinder/trip/current
car/pathfinder/trip/last
car/pathfinder/odometer
```

## Phase 4: Offline queue and replay

After live MQTT works:

- Mark samples as unsent when MQTT/server is offline.
- Replay queued messages when the tablet reconnects.
- Support configurable replay modes:

```text
none
summaries only
full telemetry
```

This is what makes RoadRunner better than the current Torque setup.

## Phase 5: LubeLogger sync

LubeLogger stays on the Docker server.

RoadRunner should update it when connectivity exists.

Minimum useful sync:

```text
trip ended
  → final odometer calculated/read
  → tablet returns to network
  → POST odometer entry to LubeLogger API
```

Fuel records can be added later.

## Hardware decision point

Do not buy replacement hardware yet unless a very good deal appears or the Surface proves unreliable.

Reasons to continue with the Surface Pro 4 for now:

- It is already available.
- Debian, touch, audio, HuDiY, and Android Auto have been proven.
- It is now a useful development platform.
- Lessons learned will transfer to a Dell Latitude or other tablet later.

Reasons to replace it later:

- Touch after suspend cannot be fixed or worked around.
- Marvell Wi-Fi/Bluetooth issues become too annoying.
- A permanent vehicle install needs more reliable hardware.
- A good Dell Latitude 7275/7320/7220 deal appears.

Recommended eventual hardware direction:

1. Dell Latitude 7275 or 7320 Detachable.
2. Dell Latitude 7220 Rugged if weight/size are acceptable.
3. ThinkPad X12 Detachable.
4. Surface Pro 6/7 only if the price is right.

Avoid buying another Surface Pro 4 specifically for this project.

## Do not work on yet

These are good ideas, but should wait until the core platform is stable:

- Dashcam.
- Backup camera.
- GPS logging.
- Fancy launcher UI.
- Grafana/InfluxDB dashboards.
- LubeLogger fuel entry UI.
- Home Assistant automations.
- BirdNET or other novelty integrations.

The order should be:

```text
reliable car appliance
  → OBD SQLite proof of concept
  → MQTT/Home Assistant
  → offline queue/replay
  → LubeLogger sync
  → extra features
```
