#!/usr/bin/env bash
# Prepare a fresh Raspberry Pi OS install for Handlet development.
#
#   sudo ./bootstrap.sh            # install packages + enable I2C/SPI/SSH
#   sudo ./bootstrap.sh --no-apt   # only enable interfaces
#
# Safe to run more than once.
set -euo pipefail

if [[ $EUID -ne 0 ]]; then
  echo "Run as root: sudo $0" >&2
  exit 1
fi

RUN_APT=1
[[ "${1:-}" == "--no-apt" ]] && RUN_APT=0

PACKAGES=(
  # Build & dev
  git build-essential cmake pkg-config
  python3-pip python3-venv python3-dev
  # GPIO / buses
  python3-gpiozero python3-lgpio python3-smbus2 i2c-tools
  python3-spidev python3-evdev
  # Audio (speaker)
  alsa-utils
  # Diagnostics
  htop iotop lsof usbutils stress-ng
  # Networking / remote work
  rsync avahi-daemon
)

if (( RUN_APT )); then
  echo "==> Installing packages"
  apt-get update
  apt-get install -y --no-install-recommends "${PACKAGES[@]}"
fi

if command -v raspi-config >/dev/null; then
  echo "==> Enabling interfaces (0 = enable in raspi-config nonint)"
  raspi-config nonint do_i2c 0
  raspi-config nonint do_spi 0
  raspi-config nonint do_ssh 0
else
  echo "raspi-config not found; enable I2C/SPI/SSH manually." >&2
fi

# Let the default user access GPIO, I2C, SPI and audio without sudo.
TARGET_USER="${SUDO_USER:-pi}"
if id "$TARGET_USER" >/dev/null 2>&1; then
  for g in gpio i2c spi audio video input; do
    getent group "$g" >/dev/null && usermod -aG "$g" "$TARGET_USER"
  done
  echo "==> Added $TARGET_USER to hardware groups (log out/in to apply)"
fi

echo "==> Done. A reboot is recommended: sudo reboot"
