# Surface Pro 4 Debian Setup Notes

## Base install

Installed Debian Trixie with KDE Plasma.

## linux-surface repository

Repository used:

```text
https://pkg.surfacelinux.com/debian
```

Example repository line:

```bash
echo "deb [arch=amd64] https://pkg.surfacelinux.com/debian release main" | sudo tee /etc/apt/sources.list.d/linux-surface.list
```

The correct hostname is:

```text
pkg.surfacelinux.com
```

Not:

```text
pkg.surface-linux.com
```

## Key import note

When importing the repository key with `wget`, the option is a capital letter O:

```bash
wget -qO- https://raw.githubusercontent.com/linux-surface/linux-surface/master/pkg/keys/surface.asc | sudo gpg --dearmor --yes -o /etc/apt/trusted.gpg.d/linux-surface.gpg
```

`-qO-` means quiet mode and write output to stdout.

## Packages installed

```bash
sudo apt update
sudo apt install linux-image-surface linux-headers-surface iptsd libwacom-surface
```

## Confirm kernel

```bash
uname -r
```

Observed result:

```text
6.19.8-surface-3
```

## Touchscreen

KDE showed:

```text
IPTS 1B96:006A Touchscreen
IPTSD Virtual Touchscreen 1B96:006A
```

`IPTSD Virtual Touchscreen` is expected when `iptsd` is working.

## Suspend/resume

Basic suspend/resume worked with:

```bash
systemctl suspend
```

However, after suspend/resume, the Marvell `mwifiex` firmware may enter a bad state. See `docs/bluetooth-marvell.md`.

## Auto-rotation

Auto-rotation did not work. This is currently not important because the tablet is expected to be mounted in fixed landscape orientation.

## Battery

Battery percentage works. Charging state may report oddly, such as showing plugged in while discharging.
