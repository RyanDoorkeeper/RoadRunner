#!/usr/bin/env bash
set -u

section() {
  printf '\n==== %s ====\n' "$1"
}

run() {
  printf '\n$ %s\n' "$*"
  "$@" 2>&1 || true
}

section "RoadRunner Bluetooth Status"
date

section "Kernel"
run uname -a

section "Bluetooth service"
run systemctl status bluetooth --no-pager

section "Bluetooth controllers"
run bluetoothctl list
run bluetoothctl show

section "HCI details"
if command -v hciconfig >/dev/null 2>&1; then
  run hciconfig -a
else
  echo "hciconfig not found. Install with: sudo apt install bluez"
fi

section "btmgmt info"
if command -v btmgmt >/dev/null 2>&1; then
  run btmgmt info
else
  echo "btmgmt not found. Install with: sudo apt install bluez"
fi

section "rfkill"
if command -v rfkill >/dev/null 2>&1; then
  run rfkill list
elif [ -x /usr/sbin/rfkill ]; then
  run /usr/sbin/rfkill list
else
  echo "rfkill not found. Install with: sudo apt install rfkill"
fi

section "USB Bluetooth devices"
run lsusb

section "Recent bluetooth journal"
run journalctl -u bluetooth -n 100 --no-pager

section "Bluetooth / btusb / firmware dmesg"
run dmesg --color=never | grep -iE "bluetooth|btusb|firmware|marvell|mwifiex|1286|204c"
