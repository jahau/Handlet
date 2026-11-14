#!/usr/bin/env bash
# Decode `vcgencmd get_throttled` into human-readable flags.
# Essential on a battery-powered Pi: under-voltage shows up here first.
#
#   ./throttle-check.sh          # decode current value
#   ./throttle-check.sh 0x50005  # decode a given value
set -euo pipefail

if [[ $# -ge 1 ]]; then
  raw="$1"
else
  command -v vcgencmd >/dev/null || { echo "vcgencmd not found" >&2; exit 1; }
  raw=$(vcgencmd get_throttled | cut -d= -f2)
fi

val=$(( raw ))
echo "get_throttled = $raw"

declare -A FLAGS=(
  [0]="Under-voltage detected NOW"
  [1]="ARM frequency capped NOW"
  [2]="Currently throttled"
  [3]="Soft temperature limit active NOW"
  [16]="Under-voltage has occurred since boot"
  [17]="ARM frequency capping has occurred"
  [18]="Throttling has occurred"
  [19]="Soft temperature limit has occurred"
)

if (( val == 0 )); then
  echo "OK - no power or thermal problems since boot."
  exit 0
fi

for bit in 0 1 2 3 16 17 18 19; do
  (( val & (1 << bit) )) && echo "  [bit $bit] ${FLAGS[$bit]}"
done

if (( val & 0x10001 )); then
  echo
  echo "Hint: under-voltage usually means the battery is low, the boost"
  echo "converter can't deliver 3 A peaks, or the cable is too thin."
fi
exit 2
