# HuDiY Notes

## Role in RoadRunner

HuDiY is the current target for Android Auto on Linux.

RoadRunner should not try to reimplement Android Auto. Instead:

- HuDiY handles Android Auto / optional CarPlay.
- RoadRunner launches and supervises HuDiY.
- RoadRunner provides vehicle-specific functions around HuDiY.

## Current state

A `hudiy.desktop` file exists in the KDE autostart folder on the prototype Surface:

```text
~/.config/autostart/hudiy.desktop
```

HuDiY appears to be installed or partially staged, but full Android Auto pairing has not yet been validated.

## Requirements to validate

Before RoadRunner depends on HuDiY, test:

1. HuDiY launches manually.
2. HuDiY launches full-screen.
3. Phone pairs successfully.
4. Android Auto appears.
5. Audio output works through Surface audio/AUX.
6. Android Auto reconnects after disconnect/reconnect.
7. Android Auto reconnects after suspend/resume.
8. HuDiY failure or exit returns cleanly to RoadRunner.

## Bluetooth note

HuDiY / Android Auto needs reliable Bluetooth for initial pairing and handoff. The Surface Pro 4 built-in Marvell Bluetooth is currently unreliable after suspend/resume.

A USB Bluetooth adapter may be preferred for the final setup.

## Intended RoadRunner behavior

RoadRunner should manage HuDiY like this:

```text
RoadRunner starts
    ↓
User taps Android Auto
    ↓
RoadRunner launches HuDiY full-screen
    ↓
HuDiY handles Android Auto
    ↓
HuDiY exits or phone disconnects
    ↓
RoadRunner returns to launcher
```

Later, RoadRunner may automatically launch HuDiY when the phone is nearby or when vehicle movement is detected.
