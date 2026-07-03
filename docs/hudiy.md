# HuDiY Notes

## Role in RoadRunner

HuDiY is the current target for Android Auto on Linux.

RoadRunner should not try to reimplement Android Auto. Instead:

- HuDiY handles Android Auto / optional CarPlay.
- RoadRunner launches and supervises HuDiY.
- RoadRunner provides vehicle-specific functions around HuDiY.

## Installation

HuDiY was installed from the official `.tar.gz` archive using the included `install.sh` script. This appears to be the only supported install method for this environment.

A `hudiy.desktop` file exists in the KDE autostart folder on the prototype Surface:

```text
~/.config/autostart/hudiy.desktop
```

## Current state

HuDiY now launches and has successfully displayed an Android Auto projection using a direct USB connection from the phone to the Surface.

Confirmed working:

- HuDiY launches.
- Bluetooth companion connection works with USB Bluetooth adapter.
- Bluetooth media metadata works.
- Bluetooth play/pause/skip controls work.
- Android Auto projection works over direct USB.
- Navigation card/turn instruction display works.
- Media art and time synchronization work.

Not yet fully validated:

- Wireless Android Auto.
- Android Auto through a USB hub.
- Reconnect behavior after suspend/resume.
- Long drive stability.
- Calls and voice assistant behavior.

## Android Auto modes observed

HuDiY's Android Auto page showed:

- Connect USB
- Connect WiFi
- Resume
- Quit

This confirms that HuDiY is not merely a Bluetooth companion interface. It can also launch an Android Auto projection session.

## Companion app behavior

The Android HuDiY companion app includes sections for:

- Connections
- Devices
- App Notifications
- Settings

Settings observed:

- Synchronize time

The companion app successfully connected to the Surface over Bluetooth and enabled media metadata/control functionality. This appears separate from full Android Auto projection.

## Bluetooth note

HuDiY / Android Auto needs reliable Bluetooth for initial pairing and companion features. The Surface Pro 4 built-in Marvell Bluetooth is unreliable after suspend/resume.

A Baseus USB Bluetooth adapter was tested and became the default BlueZ controller:

```text
Controller 04:7F:0E:33:A3:07 bronc [default]
```

This USB adapter is currently the preferred Bluetooth path.

## USB note

Initial Android Auto USB testing through a USB hub did not work. Direct USB connection from the phone to the Surface later worked.

Working theory:

- Android Auto USB accessory/projection mode may not work reliably through all hubs.
- Cable quality matters.
- Direct connection to the Surface's USB port should be considered the baseline test.

## Display / scaling note

The prototype Surface is running:

```text
KDE Plasma
Wayland
2736x1824 native resolution
180% display scaling
```

HuDiY appears to officially target 1920x1080. During Android Auto startup, a smaller Android Auto projection window appeared layered with the HuDiY interface.

This may be related to:

- Wayland
- XWayland window embedding
- Fractional scaling
- Surface high-DPI resolution
- HuDiY's 1920x1080 target

Suggested display experiments:

1. Test at 1920x1440 with 100% scaling.
2. Test at 1920x1080 with 100% scaling.
3. Test a KDE X11 session instead of Wayland.
4. Compare projection behavior after each change.

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
9. Wireless Android Auto works or is explicitly ruled out.
10. Direct USB works reliably with a known-good cable.

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
