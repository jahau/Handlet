#!/usr/bin/env bash
# Print a quick health snapshot of the Pi: model, OS, temperature,
# clocks, voltage, throttling, memory, disk and network.
#
#   ./pi-info.sh
#   watch -n 2 ./pi-info.sh     # live view
set -uo pipefail

have() { command -v "$1" >/dev/null 2>&1; }
row()  { printf '%-14s %s\n' "$1" "$2"; }

model=$(tr -d '\0' < /proc/device-tree/model 2>/dev/null || echo unknown)
os=$(. /etc/os-release 2>/dev/null && echo "$PRETTY_NAME" || echo unknown)

row "Model"   "$model"
row "OS"      "$os"
row "Kernel"  "$(uname -r)"
row "Uptime"  "$(uptime -p)"

if have vcgencmd; then
  row "SoC temp"  "$(vcgencmd measure_temp | cut -d= -f2)"
  arm_hz=$(vcgencmd measure_clock arm | cut -d= -f2)
  row "ARM clock" "$(( arm_hz / 1000000 )) MHz"
  row "Core volt" "$(vcgencmd measure_volts core | cut -d= -f2)"
  row "Throttled" "$(vcgencmd get_throttled | cut -d= -f2)  (decode: ./throttle-check.sh)"
else
  t=$(cat /sys/class/thermal/thermal_zone0/temp 2>/dev/null)
  [[ -n "$t" ]] && row "SoC temp" "$(( t / 1000 )).$(( t % 1000 / 100 ))'C"
fi

gov=$(cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_governor 2>/dev/null || echo n/a)
row "CPU governor" "$gov"
row "Load"    "$(cut -d' ' -f1-3 /proc/loadavg)"
row "Memory"  "$(free -h | awk '/^Mem:/ {print $3" used / "$2}')"
row "Root fs" "$(df -h / | awk 'NR==2 {print $3" used / "$2" ("$5")"}')"
row "IP"      "$(hostname -I 2>/dev/null | awk '{print $1}')"
row "Hostname" "$(hostname).local"

# Battery, if the kernel exposes one (e.g. a fuel-gauge driver).
for ps in /sys/class/power_supply/*; do
  [[ -f "$ps/capacity" ]] || continue
  row "Battery" "$(cat "$ps/capacity")% ($(cat "$ps/status" 2>/dev/null || echo ?))"
done
