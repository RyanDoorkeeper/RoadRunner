# Hardware Compatibility Matrix

This document tracks devices considered or tested for RoadRunner.

RoadRunner needs hardware that can reliably handle:

- Android Auto through HuDiY or similar software
- Touch input
- Suspend/resume
- USB connectivity
- Bluetooth and Wi-Fi
- OBD-II telemetry
- Local SQLite logging
- MQTT/Home Assistant publishing
- LubeLogger sync

## Rating key

| Symbol | Meaning |
|---|---|
| ✅ | Confirmed working |
| ⚠️ | Works with caveats or needs workaround |
| ❌ | Not working / unsuitable |
| ? | Not tested |

## Tested / candidate devices

| Device | CPU / Platform | Linux | Touch | Suspend | Bluetooth | USB | HuDiY / AA | Notes | Overall |
|---|---|---|---|---|---|---|---|---|---|
| Microsoft Surface Pro 4 | Intel x86, Marvell wireless | ✅ Debian Trixie + linux-surface | ⚠️ Works, but touch may fail after resume | ⚠️ Basic suspend works, but resume quirks observed | ⚠️ Built-in Marvell unreliable; USB BT works | ⚠️ One USB-A port only | ✅ Direct USB Android Auto works | Good development mule; not ideal final hardware | 7/10 |
| Surface Pro 6 | Intel x86 | ? | ? | ? | ? | ⚠️ Limited ports | ? | Likely better than SP4, but still Surface/Linux stack | TBD |
| Surface Pro 7 | Intel x86 | ? | ? | ? | ? | ⚠️ USB-A + USB-C | ? | Better candidate than SP4 because of newer platform and USB-C | TBD |
| Dell Latitude 7220 Rugged Extreme Tablet | Intel x86 | ? | ? | ? | ? | ✅ Multiple ports depending on dock/config | ? | Strong candidate; bright display, rugged, mountable | TBD |
| Dell Latitude 7230 Rugged Extreme Tablet | Intel x86 | ? | ? | ? | ? | ✅ Multiple ports depending on dock/config | ? | Expensive but likely excellent vehicle hardware | TBD |
| Dell Latitude 7320 Detachable | Intel x86 | ? | ? | ? | ? | ✅ USB-C | ? | Strong non-rugged detachable candidate | TBD |
| ThinkPad X12 Detachable | Intel x86 | ? | ? | ? | ? | ✅ USB-C | ? | Strong Linux candidate; worth testing | TBD |
| Intel Chromebook tablet/convertible with regular Linux | Intel x86 | ⚠️ Model-dependent | ⚠️ Model-dependent | ⚠️ Model-dependent | ? | ⚠️ Model-dependent | ? | Could be cheap, but exact model research is required | TBD |
| ARM Chromebook tablet | ARM | ⚠️ Often difficult | ? | ? | ? | ? | ❌ likely poor fit | Avoid unless HuDiY and Linux support are proven for exact model | Low |
| Android tablet | Android | N/A | ✅ | ✅ | ✅ | ⚠️ Usually limited | ⚠️ Needs Android Auto receiver app | Not ideal for RoadRunner because persistent OBD/SQLite/MQTT/LubeLogger services are harder | Mixed |

## Surface Pro 4 notes

Confirmed working on the current Surface Pro 4 prototype:

- Debian Trixie
- KDE Plasma
- linux-surface kernel `6.19.8-surface-3`
- IPTSD virtual touchscreen
- Wi-Fi
- audio
- battery percentage
- HuDiY
- Android Auto over direct USB
- Baseus USB Bluetooth adapter

Known issues:

- Built-in Marvell Bluetooth/Wi-Fi firmware can enter a bad state after suspend/resume.
- Touchscreen may stop responding after wake/resume.
- Only one built-in USB-A port creates practical problems for Android Auto, Bluetooth, OBD-II, keyboard/mouse, and future cameras.
- Native 2736x1824 display with 180% scaling may cause HuDiY/Android Auto projection quirks.

## Current hardware direction

The Surface Pro 4 is useful as a development platform, but the final RoadRunner hardware should probably prioritize:

1. Reliable Linux suspend/resume
2. Reliable touchscreen after resume
3. Intel Wi-Fi/Bluetooth or easily replaceable wireless
4. At least two useful USB ports, or USB-C with reliable hub/dock support
5. Bright display for vehicle use
6. Easy mounting options
7. Replaceable battery if possible

## Current best candidate classes

### Best rugged option

Dell Latitude Rugged Tablet series, especially 7220 or 7230.

Advantages:

- Designed for vehicle and field use
- Bright display
- Strong mounting ecosystem
- More ports and dock options
- Enterprise hardware

### Best detachable non-rugged option

Dell Latitude 7320 Detachable or ThinkPad X12 Detachable.

Advantages:

- Newer Intel hardware
- Better Linux odds than Surface
- USB-C
- Lighter than rugged tablets

### Budget option

Surface Pro 6 or Surface Pro 7.

Advantages:

- Cheap used market
- Better than Surface Pro 4
- Known linux-surface ecosystem

Caveat:

- Still dependent on Surface/Linux touch and suspend behavior.

## Chromebook caution

A Chromebook tablet or convertible can be a good RoadRunner platform only if the exact model is known to run regular Linux well.

Avoid:

- ARM Chromebook tablets
- MediaTek models
- Qualcomm models
- 2 GB RAM models
- Devices with locked-down firmware or poor Linux documentation

Prefer:

- Intel x86 models
- 4 GB RAM minimum, 8 GB preferred
- Known coreboot/MrChromebox support where applicable
- Confirmed touch/audio/suspend support under Linux
