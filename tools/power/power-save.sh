#!/usr/bin/env bash
# Runtime power-saving toggles for running on battery. Nothing here is
# permanent; a reboot restores defaults. For permanent settings see
# tools/config/config.txt.example.
#
#   sudo ./power-save.sh on       # battery mode
#   sudo ./power-save.sh off      # back to normal
#   ./power-save.sh status
set -euo pipefail

MODE="${1:-status}"

set_governor() {
  for g in /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor; do
    echo "$1" > "$g"
  done
}

# Onboard LEDs are ACT/PWR on current kernels, led0/led1 on older ones.
set_leds() {
  for led in /sys/class/leds/ACT /sys/class/leds/PWR /sys/class/leds/led0 /sys/class/leds/led1; do
    [[ -d "$led" ]] || continue
    echo "$1" > "$led/trigger" 2>/dev/null || true
  done
}

case "$MODE" in
  on)
    [[ $EUID -eq 0 ]] || { echo "Run with sudo" >&2; exit 1; }
    set_governor powersave
    set_leds none
    command -v rfkill >/dev/null && rfkill block bluetooth
    # Wi-Fi stays on by default because you probably SSH in over it.
    [[ "${2:-}" == "--no-wifi" ]] && rfkill block wifi
    echo "Battery mode ON (governor=powersave, LEDs off, Bluetooth off)"
    ;;
  off)
    [[ $EUID -eq 0 ]] || { echo "Run with sudo" >&2; exit 1; }
    set_governor ondemand
    set_leds mmc0
    command -v rfkill >/dev/null && rfkill unblock all
    echo "Battery mode OFF"
    ;;
  status)
    echo "Governor : $(cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_governor)"
    echo "CPU MHz  : $(( $(cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_cur_freq) / 1000 ))"
    command -v rfkill >/dev/null && rfkill list | grep -E '^[0-9]|Soft blocked'
    ;;
  *)
    echo "Usage: $0 on [--no-wifi] | off | status" >&2
    exit 1
    ;;
esac
