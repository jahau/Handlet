#!/usr/bin/env python3
"""Shut the Pi down cleanly before the battery cuts out.

Corrupted SD cards are the classic failure on battery-powered Pis. This
daemon polls the battery and runs `shutdown` once the charge stays below
a threshold for a few consecutive readings. It can also blink a status
LED as a warning.

  sudo ./low_battery_guard.py --threshold 5 --warn 15 --led-pin 27

Install as a service: see tools/systemd/README.md
"""
from __future__ import annotations

import argparse
import os
import subprocess
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from battery_monitor import read_battery  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--threshold", type=float, default=5, help="shutdown at %% (default 5)")
    ap.add_argument("--warn", type=float, default=15, help="start warning at %% (default 15)")
    ap.add_argument("--interval", type=float, default=30, help="poll seconds")
    ap.add_argument("--confirm", type=int, default=3, help="consecutive low readings needed")
    ap.add_argument("--backend", default="auto")
    ap.add_argument("--led-pin", type=int, help="BCM pin of a warning LED")
    ap.add_argument("--dry-run", action="store_true", help="log instead of shutting down")
    args = ap.parse_args()

    led = None
    if args.led_pin is not None:
        from gpiozero import LED
        led = LED(args.led_pin)

    low_count = 0
    warned = False
    while True:
        state = read_battery(args.backend)
        pct = state.percent if state else None
        charging = state and state.status and state.status.lower().startswith("charg")

        if pct is None:
            print("battery unreadable, skipping", flush=True)
        elif charging:
            low_count, warned = 0, False
            if led:
                led.off()
        elif pct <= args.threshold:
            low_count += 1
            print(f"battery {pct:.1f}% <= {args.threshold}% ({low_count}/{args.confirm})", flush=True)
            if low_count >= args.confirm:
                subprocess.run(["wall", f"Battery at {pct:.0f}% - shutting down now"], check=False)
                if args.dry_run:
                    print("DRY RUN: would shut down", flush=True)
                    low_count = 0
                else:
                    subprocess.run(["shutdown", "-h", "now"], check=False)
                    return 0
        else:
            low_count = 0
            if pct <= args.warn:
                if not warned:
                    subprocess.run(["wall", f"Battery low: {pct:.0f}%"], check=False)
                    warned = True
                if led:
                    led.blink(on_time=0.2, off_time=1.8)
            else:
                warned = False
                if led:
                    led.off()

        time.sleep(args.interval)


if __name__ == "__main__":
    sys.exit(main())
