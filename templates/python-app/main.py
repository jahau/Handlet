#!/usr/bin/env python3
"""Handlet app template.

A button toggles an LED, the battery level is logged once a minute, and
SIGTERM (systemctl stop) shuts down cleanly. Replace the bodies of
on_press() and tick() with your own logic.

Pins come from environment variables so the same code runs on different
wiring: APP_BUTTON_PIN (default 5), APP_LED_PIN (default 19).
"""
from __future__ import annotations

import logging
import os
import signal
import sys
import threading

from gpiozero import LED, Button

log = logging.getLogger("app")


class App:
    def __init__(self, button_pin: int, led_pin: int, bounce: float | None = 0.05) -> None:
        self.button = Button(button_pin, bounce_time=bounce)
        self.led = LED(led_pin)
        self.presses = 0
        self.button.when_pressed = self.on_press
        self._stop = threading.Event()

    def on_press(self) -> None:
        self.presses += 1
        self.led.toggle()
        log.info("button pressed (%d), led %s", self.presses, "on" if self.led.is_lit else "off")

    def tick(self) -> None:
        """Runs once per interval. Put periodic work here."""
        try:
            sys.path.insert(0, os.path.expanduser("~/Handlet/tools/power"))
            from battery_monitor import read_battery

            state = read_battery()
            if state and state.percent is not None:
                log.info("battery %.0f%%", state.percent)
        except Exception:  # battery tools not installed or no gauge
            pass

    def run(self, interval: float = 60) -> None:
        log.info("started")
        while not self._stop.wait(interval):
            self.tick()
        log.info("stopped")

    def stop(self, *_args) -> None:
        self._stop.set()

    def close(self) -> None:
        self.button.close()
        self.led.close()


def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    app = App(int(os.environ.get("APP_BUTTON_PIN", 5)), int(os.environ.get("APP_LED_PIN", 19)))
    signal.signal(signal.SIGTERM, app.stop)
    signal.signal(signal.SIGINT, app.stop)
    try:
        app.run()
    finally:
        app.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
