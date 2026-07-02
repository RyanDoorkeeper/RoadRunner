#!/usr/bin/env bash
set -u

STAMP="$(date +%Y%m%d-%H%M%S)"
OUT_DIR="${1:-logs/$STAMP}"
mkdir -p "$OUT_DIR"

capture() {
  local name="$1"
  shift
  echo "Collecting $name"
  {
    echo "$ $*"
    "$@"
  } > "$OUT_DIR/$name" 2>&1 || true
}

capture uname.txt uname -a
capture os-release.txt cat /etc/os-release
capture lsusb.txt lsusb
capture lspci.txt lspci -nn
capture ip-link.txt ip link
capture rfkill.txt bash -c 'if command -v rfkill >/dev/null 2>&1; then rfkill list; elif [ -x /usr/sbin/rfkill ]; then /usr/sbin/rfkill list; else echo "rfkill not found"; fi'
capture bluetoothctl-list.txt bluetoothctl list
capture bluetoothctl-show.txt bluetoothctl show
capture hciconfig.txt bash -c 'if command -v hciconfig >/dev/null 2>&1; then hciconfig -a; else echo "hciconfig not found"; fi'
capture btmgmt-info.txt bash -c 'if command -v btmgmt >/dev/null 2>&1; then btmgmt info; else echo "btmgmt not found"; fi'
capture iptsd-status.txt systemctl status iptsd --no-pager
capture bluetooth-status.txt systemctl status bluetooth --no-pager
capture power-supply.txt bash -c 'for ps in /sys/class/power_supply/*; do [ -d "$ps" ] || continue; echo "--- $(basename "$ps") ---"; for f in "$ps"/*; do [ -r "$f" ] && [ -f "$f" ] && echo "$(basename "$f"): $(cat "$f" 2>/dev/null)"; done; done'
capture dmesg.txt dmesg --color=never
capture dmesg-surface-wireless.txt bash -c 'dmesg --color=never | grep -iE "surface|ipts|bluetooth|btusb|firmware|marvell|mwifiex|1286|204c"'
capture journal-bluetooth.txt journalctl -u bluetooth -b --no-pager
capture journal-kernel.txt journalctl -k -b --no-pager
capture journal-suspend.txt journalctl -b --no-pager | grep -iE "suspend|resume|sleep|wake|mwifiex|bluetooth|firmware"

echo "Log bundle written to: $OUT_DIR"
