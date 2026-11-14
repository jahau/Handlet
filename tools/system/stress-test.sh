#!/usr/bin/env bash
# Load all CPU cores and log temperature, clock and throttling once per
# second. Use it to validate cooling inside the case and whether the
# battery/boost converter holds up under full load.
#
#   ./stress-test.sh            # 5 minutes
#   ./stress-test.sh 600 log.csv
set -euo pipefail

DURATION="${1:-300}"
LOG="${2:-stress-$(date +%Y%m%d-%H%M%S).csv}"

command -v stress-ng >/dev/null || { echo "Install stress-ng: sudo apt install stress-ng" >&2; exit 1; }
command -v vcgencmd  >/dev/null || { echo "vcgencmd not found" >&2; exit 1; }

echo "time_s,temp_c,arm_mhz,throttled" > "$LOG"
stress-ng --cpu 0 --timeout "${DURATION}s" --quiet &
STRESS_PID=$!
trap 'kill $STRESS_PID 2>/dev/null || true' EXIT

start=$(date +%s)
while kill -0 "$STRESS_PID" 2>/dev/null; do
  now=$(( $(date +%s) - start ))
  temp=$(vcgencmd measure_temp | grep -oE '[0-9.]+')
  mhz=$(( $(vcgencmd measure_clock arm | cut -d= -f2) / 1000000 ))
  thr=$(vcgencmd get_throttled | cut -d= -f2)
  echo "$now,$temp,$mhz,$thr" | tee -a "$LOG"
  sleep 1
done

echo "Log written to $LOG"
