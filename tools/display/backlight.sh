#!/usr/bin/env bash
# Control the 5" screen backlight via sysfs. Lowering brightness is one
# of the biggest battery savings available.
#
#   ./backlight.sh               # show current level
#   ./backlight.sh 40            # set to 40 %
#   ./backlight.sh up | down     # +/- 10 %
#   ./backlight.sh off | on
#
# Works with displays that expose /sys/class/backlight (official DSI
# touchscreen and most DSI panels). HDMI panels usually control the
# backlight in hardware and are not covered.
set -euo pipefail

BL=$(ls -d /sys/class/backlight/* 2>/dev/null | head -n1 || true)
[[ -n "$BL" ]] || { echo "No backlight device found in /sys/class/backlight" >&2; exit 1; }

max=$(cat "$BL/max_brightness")
cur=$(cat "$BL/brightness")
pct=$(( cur * 100 / max ))

write() {
  local target=$1
  (( target < 0 )) && target=0
  (( target > 100 )) && target=100
  local raw=$(( target * max / 100 ))
  if [[ -w "$BL/brightness" ]]; then
    echo "$raw" > "$BL/brightness"
  else
    echo "$raw" | sudo tee "$BL/brightness" >/dev/null
  fi
  echo "Backlight: $target %"
}

case "${1:-}" in
  "")   echo "Backlight: $pct % ($cur/$max) [$BL]" ;;
  up)   write $(( pct + 10 )) ;;
  down) write $(( pct - 10 )) ;;
  off)  write 0 ;;
  on)   write 100 ;;
  *[!0-9]*) echo "Usage: $0 [0-100|up|down|on|off]" >&2; exit 1 ;;
  *)    write "$1" ;;
esac
