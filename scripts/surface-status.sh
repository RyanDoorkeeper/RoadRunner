#!/usr/bin/env bash
set -u

section() {
  printf '\n==== %s ====\n' "$1"
}

run() {
  printf '\n$ %s\n' "$*"
  "$@" 2>&1 || true
}

section "RoadRunner Surface Status"
date

section "OS"
run cat /etc/os-release

section "Kernel"
run uname -r
if uname -r | grep -qi surface; then
  echo "OK: linux-surface kernel appears active."
else
  echo "WARN: linux-surface kernel does not appear active."
fi

section "Surface packages"
run dpkg -l | grep -E "linux-image-surface|linux-headers-surface|iptsd|libwacom-surface|surface"

section "IPTSD"
run systemctl status iptsd --no-pager

section "Input devices"
if command -v libinput >/dev/null 2>&1; then
  run libinput list-devices
else
  echo "libinput not found. Install with: sudo apt install libinput-tools"
fi

section "Power supplies"
run ls /sys/class/power_supply
for ps in /sys/class/power_supply/*; do
  [ -d "$ps" ] || continue
  echo "--- $(basename "$ps") ---"
  for f in type status capacity online present manufacturer model_name voltage_now current_now power_now; do
    [ -r "$ps/$f" ] && printf '%s: %s\n' "$f" "$(cat "$ps/$f")"
  done
 done

section "Wi-Fi and Bluetooth radios"
if command -v rfkill >/dev/null 2>&1; then
  run rfkill list
elif [ -x /usr/sbin/rfkill ]; then
  run /usr/sbin/rfkill list
else
  echo "rfkill not found. Install with: sudo apt install rfkill"
fi

section "Network devices"
run ip link

section "Audio"
if command -v pactl >/dev/null 2>&1; then
  run pactl info
  run pactl list short sinks
elif command -v wpctl >/dev/null 2>&1; then
  run wpctl status
else
  echo "Neither pactl nor wpctl found."
fi

section "Cameras"
run ls /dev/video*
if command -v v4l2-ctl >/dev/null 2>&1; then
  run v4l2-ctl --list-devices
else
  echo "v4l2-ctl not found. Install with: sudo apt install v4l-utils"
fi

section "Suspend support"
run systemctl status sleep.target --no-pager
run cat /sys/power/state
