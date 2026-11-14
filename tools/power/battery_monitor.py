#!/usr/bin/env python3
"""Read battery state from a common fuel gauge / power monitor.

Supported backends:
  sysfs     - any kernel power_supply device (/sys/class/power_supply/*)
  max17048  - MAX17048/MAX17043 LiPo fuel gauge over I2C (addr 0x36)
  ina219    - INA219 voltage/current monitor over I2C (addr 0x40),
              percentage estimated from a 1S Li-ion voltage curve

Examples:
  ./battery_monitor.py                    # auto-detect, print once
  ./battery_monitor.py --watch 5          # print every 5 s
  ./battery_monitor.py --backend max17048 --json
  ./battery_monitor.py --log battery.csv --watch 60   # discharge curve

Library use:
  from battery_monitor import read_battery
  state = read_battery()   # BatteryState(percent=..., voltage=..., ...)
"""
from __future__ import annotations

import argparse
import csv
import glob
import json
import os
import sys
import time
from dataclasses import asdict, dataclass
from typing import Optional

I2C_BUS = 1

# Open-circuit voltage -> state of charge for a typical 1S Li-ion/LiPo cell.
LIION_CURVE = [
    (4.20, 100), (4.10, 90), (4.00, 80), (3.90, 70), (3.80, 60),
    (3.75, 50), (3.70, 40), (3.65, 30), (3.60, 20), (3.50, 10),
    (3.30, 5), (3.00, 0),
]


@dataclass
class BatteryState:
    backend: str
    percent: Optional[float] = None
    voltage: Optional[float] = None
    current_ma: Optional[float] = None
    status: Optional[str] = None


def voltage_to_percent(v: float) -> float:
    if v >= LIION_CURVE[0][0]:
        return 100.0
    for (v_hi, p_hi), (v_lo, p_lo) in zip(LIION_CURVE, LIION_CURVE[1:]):
        if v_lo <= v <= v_hi:
            return p_lo + (p_hi - p_lo) * (v - v_lo) / (v_hi - v_lo)
    return 0.0


def _swap16(word: int) -> int:
    """SMBus returns words little-endian; these chips are big-endian."""
    return ((word & 0xFF) << 8) | (word >> 8)


def read_sysfs() -> Optional[BatteryState]:
    for path in sorted(glob.glob("/sys/class/power_supply/*")):
        cap = os.path.join(path, "capacity")
        if not os.path.exists(cap):
            continue

        def rd(name: str, path: str = path) -> Optional[str]:
            try:
                with open(os.path.join(path, name)) as f:
                    return f.read().strip()
            except OSError:
                return None

        volt = rd("voltage_now")
        curr = rd("current_now")
        return BatteryState(
            backend=f"sysfs:{os.path.basename(path)}",
            percent=float(rd("capacity") or 0),
            voltage=int(volt) / 1e6 if volt else None,
            current_ma=int(curr) / 1e3 if curr else None,
            status=rd("status"),
        )
    return None


def read_max17048(addr: int = 0x36) -> BatteryState:
    from smbus2 import SMBus

    with SMBus(I2C_BUS) as bus:
        vcell = _swap16(bus.read_word_data(addr, 0x02))
        soc = _swap16(bus.read_word_data(addr, 0x04))
    return BatteryState(
        backend="max17048",
        voltage=round(vcell * 78.125e-6, 3),
        percent=round(min(100.0, (soc >> 8) + (soc & 0xFF) / 256), 1),
    )


def read_ina219(addr: int = 0x40, shunt_ohms: float = 0.1) -> BatteryState:
    from smbus2 import SMBus

    with SMBus(I2C_BUS) as bus:
        shunt_raw = _swap16(bus.read_word_data(addr, 0x01))
        bus_raw = _swap16(bus.read_word_data(addr, 0x02))
    if shunt_raw & 0x8000:
        shunt_raw -= 1 << 16
    shunt_v = shunt_raw * 10e-6          # 10 uV / LSB
    bus_v = (bus_raw >> 3) * 4e-3        # 4 mV / LSB
    current_ma = shunt_v / shunt_ohms * 1000
    return BatteryState(
        backend="ina219",
        voltage=round(bus_v, 3),
        current_ma=round(current_ma, 1),
        percent=round(voltage_to_percent(bus_v), 1),
        status="Discharging" if current_ma > 0 else "Charging",
    )


BACKENDS = {"sysfs": read_sysfs, "max17048": read_max17048, "ina219": read_ina219}


def read_battery(backend: str = "auto") -> Optional[BatteryState]:
    if backend != "auto":
        return BACKENDS[backend]()
    for name in ("sysfs", "max17048", "ina219"):
        try:
            state = BACKENDS[name]()
            if state is not None:
                return state
        except Exception:
            continue
    return None


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--backend", choices=["auto", *BACKENDS], default="auto")
    ap.add_argument("--watch", type=float, metavar="SECONDS")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--log", metavar="CSV", help="append readings to a CSV file")
    args = ap.parse_args()

    writer = None
    if args.log:
        new = not os.path.exists(args.log)
        fh = open(args.log, "a", newline="")
        writer = csv.writer(fh)
        if new:
            writer.writerow(["timestamp", "percent", "voltage", "current_ma", "status"])

    while True:
        state = read_battery(args.backend)
        if state is None:
            print("No battery source found (try --backend).", file=sys.stderr)
            return 1
        if args.json:
            print(json.dumps(asdict(state)))
        else:
            parts = [f"{state.percent:.1f}%" if state.percent is not None else "?%"]
            if state.voltage is not None:
                parts.append(f"{state.voltage:.3f} V")
            if state.current_ma is not None:
                parts.append(f"{state.current_ma:.0f} mA")
            if state.status:
                parts.append(state.status)
            print(f"[{state.backend}] " + "  ".join(parts), flush=True)
        if writer:
            writer.writerow([int(time.time()), state.percent, state.voltage,
                             state.current_ma, state.status])
            fh.flush()
        if not args.watch:
            return 0
        time.sleep(args.watch)


if __name__ == "__main__":
    sys.exit(main())
