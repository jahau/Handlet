#!/usr/bin/env bash
# Show the state of every GPIO and scan the I2C bus. Handy when wiring
# peripherals through the 40-pin GPIO extension cable.
#
#   ./gpio-scan.sh
#   ./gpio-scan.sh --watch     # refresh every second
set -uo pipefail

show() {
  echo "=== GPIO (pinctrl) ==="
  if command -v pinctrl >/dev/null; then
    pinctrl get 0-27
  elif command -v raspi-gpio >/dev/null; then
    raspi-gpio get 0-27
  else
    echo "Neither pinctrl nor raspi-gpio found."
  fi

  echo
  echo "=== I2C bus 1 ==="
  if command -v i2cdetect >/dev/null && [[ -e /dev/i2c-1 ]]; then
    i2cdetect -y 1
    echo "Common addresses: 0x36 MAX17048 fuel gauge, 0x40 INA219,"
    echo "0x3C SSD1306 OLED, 0x48 ADS1115 ADC, 0x68 RTC/IMU, 0x76/0x77 BME280"
  else
    echo "I2C not enabled (sudo raspi-config nonint do_i2c 0) or i2c-tools missing."
  fi

  echo
  echo "=== SPI ==="
  ls /dev/spidev* 2>/dev/null || echo "SPI not enabled."
}

if [[ "${1:-}" == "--watch" ]]; then
  while true; do clear; show; sleep 1; done
else
  show
fi
