# Marvell Bluetooth / Wi-Fi Notes

## Chipset

The Surface Pro 4 prototype uses Marvell wireless hardware, not Intel.

`lsusb` showed:

```text
1286:204C Marvell Semiconductor, Inc. Bluetooth and Wireless LAN Composite
```

## Services and tools checked

Bluetooth service:

```bash
systemctl status bluetooth
```

Controller listing:

```bash
bluetoothctl list
```

Example result:

```text
Controller 98:5F:D3:C6:51:E9 bronc [default]
```

HCI state:

```bash
hciconfig -a
```

Observed:

```text
hci0: Type: Primary  Bus: USB
UP RUNNING
Can't read local name on hci0: Connection timed out (110)
```

Radio block state:

```bash
sudo rfkill list
```

Observed:

```text
hci0: Bluetooth
    Soft blocked: no
    Hard blocked: no
phy1: Wireless LAN
    Soft blocked: no
    Hard blocked: no
```

Note: on Debian, `rfkill` may be located at `/usr/sbin/rfkill`, which may not be in a normal user's PATH. `sudo rfkill list` works.

## Observed behavior

- Bluetooth service runs.
- Controller is visible.
- Adapter can scan some BLE advertisements.
- KDE Bluetooth does not reliably show nearby devices.
- Phone can see the Surface, but pairing/connection fails.
- Surface does not reliably see the phone as a named pairable device.

## Relevant journal messages

Earlier journal messages showed repeated authentication failures:

```text
Failed to add UUID: Authentication Failed (0x05)
Failed to set mode: Authentication Failed (0x05)
Failed to remove UUID: Authentication Failed (0x05)
```

PipeWire/BlueZ endpoint messages appeared but did not seem to be the root cause:

```text
Endpoint registered
Endpoint unregistered
```

## mwifiex firmware bad state after suspend/resume

After suspend/resume, `dmesg` showed Marvell `mwifiex` driver/firmware problems:

```text
mwifiex_pcie ... Invalid RX len
mwifiex_pcie ... scan failed: -14
mwifiex_pcie ... Ignore scan. Card removed or firmware in bad state
mwifiex_pcie ... PREP_CMD: FW is in bad state
mwifiex_pcie ... Using reset_d3cold quirk to perform FW reset
mwifiex_pcie ... FW download over
mwifiex_pcie ... WLAN FW is active
```

This suggests the issue may be a suspend/resume power-management problem with the Marvell firmware rather than KDE or BlueZ alone.

## Working theory

The Marvell combo card handles both Wi-Fi and Bluetooth. After suspend/resume, the firmware can enter a bad state. Wi-Fi may recover after a firmware reset, but Bluetooth discovery/pairing remains unreliable.

## Next tests

1. Reboot cleanly.
2. Do not suspend.
3. Test Bluetooth pairing immediately after boot.
4. Test a spare USB Bluetooth adapter.
5. If USB Bluetooth works, prefer it for Android Auto/HuDiY.

## Possible final design

Use:

```text
Built-in Marvell adapter -> Wi-Fi
USB Bluetooth adapter    -> Bluetooth for Android Auto / HuDiY
```

This avoids depending on the Marvell Bluetooth stack for the head-unit function.
