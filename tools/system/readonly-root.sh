#!/usr/bin/env bash
# Toggle the read-only root filesystem (overlayfs). When it is on, all
# writes go to RAM and vanish at reboot, so cutting the power can never
# corrupt the SD card - ideal for a finished, battery-powered device.
#
#   sudo ./readonly-root.sh on       # enable (takes effect after reboot)
#   sudo ./readonly-root.sh off      # disable (takes effect after reboot)
#   ./readonly-root.sh status
#
# Workflow for changes on a protected device:
#   off -> reboot -> install/configure -> on -> reboot
set -euo pipefail

is_overlay() { [[ "$(findmnt -no FSTYPE /)" == "overlay" ]]; }

case "${1:-status}" in
  on|off)
    [[ $EUID -eq 0 ]] || { echo "Run with sudo" >&2; exit 1; }
    command -v raspi-config >/dev/null || { echo "raspi-config not found" >&2; exit 1; }
    # raspi-config nonint: 0 = enable, 1 = disable
    if [[ "$1" == "on" ]]; then
      raspi-config nonint do_overlayfs 0
      echo "Overlay filesystem ENABLED after reboot. Changes will no longer persist."
    else
      raspi-config nonint do_overlayfs 1
      echo "Overlay filesystem DISABLED after reboot."
    fi
    echo "Reboot now: sudo reboot"
    ;;
  status)
    if is_overlay; then
      echo "Root filesystem: READ-ONLY overlay (changes are lost at reboot)"
      free -h | awk '/^Mem:/ {print "RAM used (includes overlay writes): "$3" / "$2}'
    else
      echo "Root filesystem: normal read-write"
    fi
    ;;
  *)
    echo "Usage: $0 on | off | status" >&2
    exit 1
    ;;
esac
