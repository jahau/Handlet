#!/usr/bin/env bash
# Check the built-in speaker: list devices, show volume, play a test.
#
#   ./speaker-test.sh               # default device
#   ./speaker-test.sh hw:1,0        # specific ALSA device
#   ./speaker-test.sh --volume 70   # set Master volume to 70 % first
set -euo pipefail

DEVICE="default"
while [[ $# -gt 0 ]]; do
  case "$1" in
    --volume) amixer -q sset Master "$2%" 2>/dev/null || amixer -q sset PCM "$2%"; shift 2 ;;
    *) DEVICE="$1"; shift ;;
  esac
done

echo "=== Playback devices ==="
aplay -l || true
echo
echo "=== Mixer ==="
amixer sget Master 2>/dev/null | tail -n 2 || amixer sget PCM 2>/dev/null | tail -n 2 || true
echo
echo "Playing test on '$DEVICE' (Ctrl+C to stop)..."
# Voice says "Front left / Front right"; on a mono speaker you hear both.
speaker-test -D "$DEVICE" -c 2 -t wav -l 2
