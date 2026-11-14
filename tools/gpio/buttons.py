#!/usr/bin/env python3
"""Map Handlet's external buttons to shell commands, with LED feedback.

Each button can have its own LED that lights while the command runs.
Buttons are configured in a small JSON file:

  {
    "buttons": [
      {"name": "power", "pin": 3,  "led": 27,
       "hold": "sudo shutdown -h now", "hold_time": 3},
      {"name": "vol+",  "pin": 5,  "press": "amixer -q sset Master 5%+"},
      {"name": "vol-",  "pin": 6,  "press": "amixer -q sset Master 5%-"},
      {"name": "app",   "pin": 13, "led": 19, "press": "python3 ~/app.py"}
    ]
  }

  ./buttons.py buttons.json
  ./buttons.py --test            # print presses on all free GPIOs

Pin numbers are BCM (GPIO numbers), not physical header pins.
"""
from __future__ import annotations

import argparse
import json
import signal
import subprocess
import sys
import threading

from gpiozero import LED, Button

# BCM pins that are safe to probe in --test mode (skips I2C, SPI, UART).
TEST_PINS = [4, 5, 6, 12, 13, 16, 17, 19, 20, 21, 22, 23, 24, 25, 26, 27]


def run(cmd: str, led: LED | None, name: str) -> None:
    def worker() -> None:
        print(f"[{name}] -> {cmd}", flush=True)
        if led:
            led.on()
        try:
            subprocess.run(cmd, shell=True, check=False)
        finally:
            if led:
                led.off()
    threading.Thread(target=worker, daemon=True).start()


def setup(cfg: dict) -> list:
    keep = []
    for b in cfg["buttons"]:
        name = b.get("name", f"gpio{b['pin']}")
        btn = Button(b["pin"], pull_up=b.get("pull_up", True),
                     bounce_time=b.get("bounce", 0.05),
                     hold_time=b.get("hold_time", 2))
        led = LED(b["led"]) if "led" in b else None
        if "press" in b:
            btn.when_pressed = lambda c=b["press"], led_=led, n=name: run(c, led_, n)
        if "release" in b:
            btn.when_released = lambda c=b["release"], led_=led, n=name: run(c, led_, n)
        if "hold" in b:
            btn.when_held = lambda c=b["hold"], led_=led, n=name: run(c, led_, n)
        keep.append((btn, led))
        print(f"configured {name}: pin {b['pin']}" + (f", led {b['led']}" if led else ""))
    return keep


def test_mode() -> list:
    keep = []
    for pin in TEST_PINS:
        try:
            btn = Button(pin, pull_up=True, bounce_time=0.05)
        except Exception as e:  # pin busy
            print(f"skip GPIO{pin}: {e}")
            continue
        btn.when_pressed = lambda p=pin: print(f"GPIO{p} pressed", flush=True)
        btn.when_released = lambda p=pin: print(f"GPIO{p} released", flush=True)
        keep.append(btn)
    print("Press buttons (Ctrl+C to quit)...")
    return keep


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("config", nargs="?", help="JSON config file")
    ap.add_argument("--test", action="store_true", help="report presses on free pins")
    args = ap.parse_args()

    if args.test:
        _keep = test_mode()
    elif args.config:
        with open(args.config) as f:
            _keep = setup(json.load(f))
    else:
        ap.print_help()
        return 1

    signal.pause()
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        pass
