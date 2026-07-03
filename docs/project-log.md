# Project Log

## 2026-07-01: Initial Surface Pro 4 bring-up

### Project concept

RoadRunner is intended to turn a Microsoft Surface tablet into a Linux-based vehicle companion display for a 2007 Nissan Pathfinder.

The plan is to keep the factory Bose radio and use the Surface for:

- Android Auto through HuDiY
- OBD-II data collection
- Home Assistant integration
- Trip history
- Dashcam / backup camera support later
- A touch-friendly car launcher UI

### OS and desktop

Installed:

- Debian Trixie
- KDE Plasma

KDE was chosen because it is configurable, touch-friendly enough, and easier to adapt into a kiosk/car-appliance interface than GNOME or XFCE.

### linux-surface kernel

Added the linux-surface Debian repository and installed the Surface kernel and touch components.

Packages installed included:

```bash
linux-image-surface
linux-headers-surface
iptsd
libwacom-surface
```

Current kernel confirmed with:

```bash
uname -r
```

Result:

```text
6.19.8-surface-3
```

### Secure Boot / boot note

During boot, the Surface displayed:

```text
Loading Linux 6.19.8-surface-3 ...
error: bad shim signature.
Loading initial ramdisk ...
error: you need to load the kernel first.
```

This pointed to a Secure Boot / shim signature issue. The Surface kernel later booted successfully, and `uname -r` confirmed the Surface kernel was active.

### Hardware tested

Confirmed working:

- Touchscreen
- IPTSD virtual touchscreen
- Wi-Fi
- Audio
- Battery percentage
- Suspend/resume

Not working / not important:

- Auto-rotation does not work. This is acceptable because the tablet will be mounted in landscape in the Pathfinder.

Minor issue:

- Battery state may report as plugged in while still discharging.

### Touchscreen finding

KDE showed both:

```text
IPTS 1B96:006A Touchscreen
IPTSD Virtual Touchscreen 1B96:006A
```

The IPTSD virtual touchscreen indicates the `iptsd` daemon is running and creating the expected virtual input device.

### Bluetooth finding

Bluetooth service was running:

```bash
systemctl status bluetooth
```

The controller was visible:

```bash
bluetoothctl list
```

Example controller:

```text
Controller 98:5F:D3:C6:51:E9 bronc [default]
```

`hciconfig -a` showed hci0 as UP and RUNNING, but reported:

```text
Can't read local name on hci0: Connection timed out (110)
```

KDE did not show discoverable devices. `bluetoothctl scan on` did show some BLE advertisements, but pairing/discovery remained unreliable.

### Important chipset discovery

The Surface Pro 4 wireless/Bluetooth chipset is Marvell, not Intel.

`lsusb` showed:

```text
1286:204C Marvell Semiconductor, Inc. Bluetooth and Wireless LAN Composite
```

### Marvell / mwifiex issue

After suspend/resume, logs showed the Marvell firmware entering a bad state.

Observed log lines included:

```text
mwifiex_pcie ... Invalid RX len
mwifiex_pcie ... scan failed: -14
mwifiex_pcie ... Ignore scan. Card removed or firmware in bad state
mwifiex_pcie ... PREP_CMD: FW is in bad state
mwifiex_pcie ... Using reset_d3cold quirk to perform FW reset
mwifiex_pcie ... FW download over
mwifiex_pcie ... WLAN FW is active
```

This suggests the Bluetooth problem may be tied to Marvell firmware/power-management behavior after suspend/resume.

### Decision

Do not spend days chasing built-in Marvell Bluetooth if a USB Bluetooth adapter works. For a car appliance, reliability matters more than using every built-in part.

Next test:

1. Reboot and test Bluetooth before any suspend.
2. Test spare USB Bluetooth adapter.
3. If USB Bluetooth is reliable, use Marvell for Wi-Fi and USB adapter for Bluetooth.

## 2026-07-03: HuDiY / Android Auto validation

### USB Bluetooth adapter test

A Baseus USB Bluetooth adapter was tested.

Without the USB adapter, BlueZ showed only the internal Marvell controller:

```text
Controller 98:5F:D3:C6:51:E9 bronc [default]
```

With the USB adapter plugged in, BlueZ showed:

```text
Controller 04:7F:0E:33:A3:07 bronc #2 [default]
Controller 98:5F:D3:C6:51:E9 bronc
```

The USB adapter automatically became the default controller.

After unloading/reloading Bluetooth USB support during testing, only the USB adapter remained visible:

```text
Controller 04:7F:0E:33:A3:07 bronc [default]
```

This became the preferred test state because HuDiY no longer had multiple Bluetooth controllers to choose from.

### Bluetooth pairing and companion app

Pairing from the Android phone to the Surface worked with the Baseus USB adapter.

The HuDiY companion app connected to the Surface. Bluetooth media metadata and controls worked, including:

- Track title
- Artist/podcast information
- Album art
- Play/pause and skip controls

This confirmed that the USB Bluetooth path was healthy enough for HuDiY companion features.

### Android Auto connection

HuDiY showed an Android Auto page with:

- Connect USB
- Connect WiFi
- Resume
- Quit

Initial USB testing through a USB hub did not work. A later direct USB cable connection from the phone to the Surface worked.

After direct USB connection, Android Auto projection worked. Confirmed working:

- Android Auto display/projection
- Navigation card and turn instruction display
- Media metadata
- Album art
- Time synchronization

This indicates that the earlier failure was likely related to the USB hub and/or cable, not HuDiY or Linux as a whole.

### Display / scaling observations

The Surface is running KDE Plasma on Wayland.

Observed display state:

```text
Resolution: 2736x1824 (3:2)
Scale: 180%
Session: Wayland
```

`xrandr` showed the native display mode:

```text
eDP-1 connected primary 2736x1824
2736x1824 59.98+
```

HuDiY officially targets 1920x1080. During Android Auto startup, a small Android Auto projection window appeared layered with the HuDiY interface. This may be related to the Surface's high-DPI display, Wayland/XWayland behavior, and fractional scaling.

The projection did not necessarily crash. It may have been closed or interrupted by tapping a HuDiY control that was visually near an Android Auto control.

### Current working theory

The core Android Auto path now works when connected directly over USB. Remaining issues are likely polish items:

- Display scaling/window embedding under Wayland
- Whether wireless Android Auto works
- Whether USB hubs can be used reliably
- Whether a different display mode, such as 1920x1440 or 1920x1080 with 100% scaling, improves projection behavior

### Updated next tests

1. Test direct USB with a known-good data cable several times.
2. Test whether the same cable works through the USB hub.
3. Test 1920x1440 or 1920x1080 at 100% scaling.
4. Test KDE X11 session versus Wayland if projection/window embedding remains odd.
5. Test wireless Android Auto after a known-good USB Android Auto session.
6. Add RoadRunner startup logic to prefer the USB Bluetooth adapter and avoid the internal Marvell Bluetooth path.
