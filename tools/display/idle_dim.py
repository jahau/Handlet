#!/usr/bin/env python3
"""Dim the 5" screen after a period without input, and turn it off later.
Any touch, key or button event restores the previous brightness.

  sudo ./idle_dim.py                         # dim after 30 s, off after 120 s
  sudo ./idle_dim.py --dim-after 15 --dim-level 10 --off-after 0   # never off

Input is read from every /dev/input device (touchscreen, keyboards and
GPIO buttons set up as gpio-keys). Needs python3-evdev and root (or the
input group plus write access to the backlight).

Note: the touch that wakes the screen is also delivered to the app that
is running.
"""
from __future__ import annotations

import argparse
import glob
import os
import select
import sys
import time

RESCAN_SECONDS = 30


def next_state(state: str, idle: float, dim_after: float, off_after: float) -> str:
    """Return the screen state for the given idle time: normal, dim or off."""
    if off_after and idle >= off_after:
        return "off"
    if dim_after and idle >= dim_after:
        return "off" if state == "off" else "dim"
    return "normal"


class Backlight:
    def __init__(self, path: str | None = None) -> None:
        if path is None:
            found = sorted(glob.glob("/sys/class/backlight/*"))
            if not found:
                raise SystemExit("No backlight device in /sys/class/backlight")
            path = found[0]
        self.path = path
        with open(os.path.join(path, "max_brightness")) as f:
            self.max = int(f.read())

    def get(self) -> int:
        with open(os.path.join(self.path, "brightness")) as f:
            return int(f.read())

    def set(self, raw: int) -> None:
        with open(os.path.join(self.path, "brightness"), "w") as f:
            f.write(str(max(0, min(self.max, raw))))


def open_inputs():
    import evdev
    from evdev import ecodes

    devs = []
    for p in evdev.list_devices():
        try:
            d = evdev.InputDevice(p)
        except OSError:
            continue
        caps = d.capabilities()
        if ecodes.EV_KEY in caps or ecodes.EV_ABS in caps or ecodes.EV_REL in caps:
            devs.append(d)
    return devs


def main() -> int:
    ap = argparse.ArgumentParser(description="Dim the screen when idle")
    ap.add_argument("--dim-after", type=float, default=30, help="seconds (0 = never)")
    ap.add_argument("--off-after", type=float, default=120, help="seconds (0 = never)")
    ap.add_argument("--dim-level", type=float, default=15, help="dim brightness in %%")
    ap.add_argument("--backlight", help="sysfs backlight path (default: first found)")
    args = ap.parse_args()

    from evdev import ecodes

    bl = Backlight(args.backlight)
    devs = open_inputs()
    print(f"backlight {bl.path}, watching {len(devs)} input devices", flush=True)

    state = "normal"
    restore = bl.get() or bl.max
    last_input = last_scan = time.monotonic()

    while True:
        r, _, _ = select.select(devs, [], [], 1.0) if devs else ([], [], time.sleep(1))
        active = False
        for d in r:
            try:
                for ev in d.read():
                    if ev.type in (ecodes.EV_KEY, ecodes.EV_ABS, ecodes.EV_REL):
                        active = True
            except OSError:  # device unplugged
                devs.remove(d)

        now = time.monotonic()
        if active:
            last_input = now
        if now - last_scan > RESCAN_SECONDS:  # pick up hot-plugged devices
            for d in devs:
                d.close()
            devs = open_inputs()
            last_scan = now

        new = next_state(state, now - last_input, args.dim_after, args.off_after)
        if new == state:
            continue
        if state == "normal":
            restore = bl.get() or restore  # remember the user's level
        if new == "normal":
            bl.set(restore)
        elif new == "dim":
            bl.set(min(restore, round(bl.max * args.dim_level / 100)))
        else:
            bl.set(0)
        print(f"screen {state} -> {new}", flush=True)
        state = new


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        pass
