# Handlet

[![CI](../../actions/workflows/ci.yml/badge.svg)](../../actions/workflows/ci.yml)

Developer tools for [Handlet](https://handlet.eu), the battery-powered
Raspberry Pi 4B case with a 5" screen, speaker, LED buttons and a 40-pin
GPIO extension.

The scripts are small and have few dependencies. Use them as they are, or
copy them into your own projects.

## Tools at a glance

**Runs on:** 🍓 the Pi · 💻 your development machine · ⚙️ as a systemd service at boot

| Area | Tool | Runs on | What it does |
|------|------|:-------:|--------------|
| **Setup** | [bootstrap.sh](tools/setup/bootstrap.sh) | 🍓 | Installs dev, GPIO, I2C, audio and diagnostic packages, enables I2C/SPI/SSH and adds the user to the hardware groups |
| | [config.txt.example](tools/config/config.txt.example) | 🍓 | Annotated boot config snippets: power button, battery savings, 5" display, fan, RTC |
| **System** | [pi-info.sh](tools/system/pi-info.sh) | 🍓 | Health snapshot: model, temperature, clock, voltage, throttling, memory, disk, IP, battery |
| | [throttle-check.sh](tools/system/throttle-check.sh) | 🍓 | Decodes `vcgencmd get_throttled` (under-voltage, thermal limits) |
| | [stress-test.sh](tools/system/stress-test.sh) | 🍓 | Full CPU load with a CSV log of temperature, clock and throttling, to test cooling and battery output |
| | [readonly-root.sh](tools/system/readonly-root.sh) | 🍓 | Turns the read-only root filesystem on or off so a power cut can't corrupt the SD card |
| **Power** | [battery_monitor.py](tools/power/battery_monitor.py) | 🍓 | Charge, voltage and current from sysfs, MAX17048 or INA219. Prints once, watches, outputs JSON or logs CSV. Also importable as a library |
| | [low_battery_guard.py](tools/power/low_battery_guard.py) | 🍓 ⚙️ | Warns at low charge and shuts down cleanly before the battery runs out |
| | [battery_leds.py](tools/power/battery_leds.py) | 🍓 ⚙️ | Shows the battery level on button LEDs: one LED as solid, blinking or pulsing, or several as a bar graph |
| | [power-save.sh](tools/power/power-save.sh) | 🍓 | Battery mode: powersave governor, onboard LEDs off, Bluetooth/Wi-Fi off |
| **GPIO** | [buttons.py](tools/gpio/buttons.py) | 🍓 ⚙️ | Maps buttons to commands (press/release/hold) and lights an LED while each runs. `--test` shows presses on all free pins |
| | [buttons.example.json](tools/gpio/buttons.example.json) | 🍓 | Example mapping: power, volume, brightness, battery status |
| | [gpio-scan.sh](tools/gpio/gpio-scan.sh) | 🍓 | Pin states, I2C bus scan with common device addresses, SPI devices |
| | [PINOUT.md](tools/gpio/PINOUT.md) | 📖 | 40-pin header reference with wiring notes |
| **Display** | [backlight.sh](tools/display/backlight.sh) | 🍓 | Sets the backlight: percentage, up/down, on/off |
| | [idle_dim.py](tools/display/idle_dim.py) | 🍓 ⚙️ | Dims the screen after a period without input and turns it off later. Any touch or key restores it |
| | [screen-test.py](tools/display/screen-test.py) | 🍓 | Colour, grid and gradient test patterns plus a touch drawing test |
| **Audio** | [speaker-test.sh](tools/audio/speaker-test.sh) | 🍓 | Lists ALSA devices, sets the volume and plays a test sound |
| **Workflow** | [deploy.sh](tools/dev/deploy.sh) | 💻 | Copies a folder to the Pi over ssh+tar and optionally runs it. `--watch` redeploys on every change |
| | [deploy.ps1](tools/dev/deploy.ps1) | 💻 | The same for Windows PowerShell, using the built-in OpenSSH and tar |
| | [find-pi.sh](tools/dev/find-pi.sh) | 💻 | Finds Pis on the LAN through mDNS, the ARP table or nmap |
| | [setup-ssh-key.sh](tools/dev/setup-ssh-key.sh) | 💻 | Creates an SSH key, installs it on the Pi and adds a `handlet` host alias |
| | [backup-sd.sh](tools/dev/backup-sd.sh) | 💻 | Copies the Pi's SD card over the network into a compressed `.img.gz` |
| **Services** | [tools/systemd/](tools/systemd/) | ⚙️ | Unit files for the battery guard, battery LEDs, idle dimming and buttons ([install guide](tools/systemd/README.md)) |
| **Template** | [templates/python-app/](templates/python-app/) | 💻 🍓 | Starter app with gpiozero, logging, clean shutdown, a systemd unit and tests that run without hardware |
| **Quality** | [CI workflow](.github/workflows/ci.yml) | ☁️ | ShellCheck, Ruff and pytest with simulated GPIO on every push |

## Quick start

On the Pi:

```bash
git clone <this-repo> ~/Handlet
cd ~/Handlet
chmod +x tools/*/*.sh tools/*/*.py
sudo tools/setup/bootstrap.sh     # packages, I2C/SPI/SSH, user groups
sudo reboot
tools/system/pi-info.sh           # health check
```

From your development machine:

```bash
tools/dev/setup-ssh-key.sh pi@raspberrypi.local handlet
PI_HOST=handlet tools/dev/deploy.sh ./myapp "python3 main.py"
```

On Windows without Git Bash:

```powershell
.\tools\dev\deploy.ps1 .\myapp -PiHost handlet -Run "python3 main.py"
```

## Building a Handlet device step by step

| # | Step | Tools |
|:-:|------|-------|
| 1 | Install packages and enable interfaces, then reboot | `bootstrap.sh` |
| 2 | Add the power-button and battery-saving lines to `/boot/firmware/config.txt` | `config.txt.example` |
| 3 | Wire the fuel gauge and check that it is detected | `gpio-scan.sh`, `battery_monitor.py` |
| 4 | Find your button pins, then write `~/Handlet/buttons.json` | `buttons.py --test`, `buttons.example.json` |
| 5 | Check the screen, touch and speaker | `screen-test.py`, `backlight.sh`, `speaker-test.sh` |
| 6 | Enable the services you want at boot | `tools/systemd/` |
| 7 | Run a load test on battery and look for throttling | `stress-test.sh`, `throttle-check.sh` |
| 8 | When the device is finished, protect the SD card | `readonly-root.sh on` |

## Starting your own app

```bash
cp -r templates/python-app ~/projects/myapp
```

See the [template README](templates/python-app/README.md) for testing on
a PC, deploying and running at boot.

## Development

```bash
python -m venv .venv && . .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements-dev.txt
ruff check .
pytest                       # GPIO is simulated with gpiozero's MockFactory
shellcheck --severity=warning tools/*/*.sh
```

CI runs the same checks on Python 3.11 (Bookworm) and 3.13 (Trixie).

## Requirements

- Raspberry Pi 4B running Raspberry Pi OS Bookworm or newer (most tools
  also work on Bullseye and on other Pi models)
- Python 3.9+, `gpiozero`, `smbus2`, `evdev` (all installed by `bootstrap.sh`)
- Development machine: any OS with an OpenSSH client

## Notes for Windows developers

`.gitattributes` makes `.sh`, `.py` and `.service` files keep LF line
endings, so scripts edited on Windows still run on the Pi. If you see
`/usr/bin/env: 'bash\r'`, run `sed -i 's/\r$//' <file>` on the Pi.
