#!/usr/bin/env python3
"""Show the battery level on Handlet's button LEDs.

One LED:
  >= high %  solid on
  >= low %   slow blink
  <  low %   fast blink
  charging   slow pulse

Several LEDs (bar graph, lowest pin first):
  LEDs light up in proportion to the charge, the next LED pulses while
  charging, and the first LED blinks fast below the low threshold.

  ./battery_leds.py --pins 19                 # single LED
  ./battery_leds.py --pins 17 27 22 --low 15  # 3-LED bar

Pins are BCM numbers. A pin can only be used by one process, so pick LEDs
that buttons.py is not also driving.
"""
from __future__ import annotations

import argparse
import math
import os
import signal
import sys
import threading

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from battery_monitor import read_battery  # noqa: E402


def plan(pct: float | None, charging: bool, n: int,
         low: float = 20, high: float = 50) -> list[str]:
    """Return one state per LED: off, on, slow, fast or pulse."""
    if pct is None or n < 1:
        return ["off"] * n
    if n == 1:
        if charging:
            return ["pulse"]
        if pct >= high:
            return ["on"]
        if pct >= low:
            return ["slow"]
        return ["fast"]
    lit = max(1, min(n, math.ceil(pct / 100 * n)))
    states = ["on"] * lit + ["off"] * (n - lit)
    if charging and lit < n:
        states[lit] = "pulse"
    elif not charging and pct < low:
        states[0] = "fast"
    return states


def apply(led, state: str, brightness: float) -> None:
    if state == "off":
        led.off()
    elif state == "on":
        led.value = brightness
    elif state == "slow":
        led.blink(on_time=0.5, off_time=2.5)
    elif state == "fast":
        led.blink(on_time=0.15, off_time=0.35)
    elif state == "pulse":
        led.pulse(fade_in_time=1.0, fade_out_time=1.0)


def is_charging(status: str | None) -> bool:
    return bool(status) and status.lower() in ("charging", "full")


def main() -> int:
    ap = argparse.ArgumentParser(description="Battery level on LEDs")
    ap.add_argument("--pins", type=int, nargs="+", required=True)
    ap.add_argument("--low", type=float, default=20)
    ap.add_argument("--high", type=float, default=50)
    ap.add_argument("--brightness", type=float, default=1.0, help="0.0-1.0 for solid LEDs")
    ap.add_argument("--interval", type=float, default=10)
    ap.add_argument("--backend", default="auto")
    args = ap.parse_args()

    from gpiozero import PWMLED

    leds = [PWMLED(p) for p in args.pins]
    stop = threading.Event()
    signal.signal(signal.SIGTERM, lambda *_: stop.set())
    signal.signal(signal.SIGINT, lambda *_: stop.set())

    current: list[str] = []
    try:
        while not stop.is_set():
            state = read_battery(args.backend)
            pct = state.percent if state else None
            states = plan(pct, is_charging(state.status if state else None),
                          len(leds), args.low, args.high)
            if states != current:  # re-applying would restart blink cycles
                for led, s in zip(leds, states):
                    apply(led, s, args.brightness)
                current = states
            stop.wait(args.interval)
    finally:
        for led in leds:
            led.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
