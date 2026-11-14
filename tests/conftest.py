import os
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for sub in ("tools/power", "tools/display", "tools/gpio"):
    sys.path.insert(0, os.path.join(ROOT, sub))


@pytest.fixture(autouse=True)
def mock_pins():
    from gpiozero import Device
    from gpiozero.pins.mock import MockFactory, MockPWMPin

    Device.pin_factory = MockFactory(pin_class=MockPWMPin)
    yield Device.pin_factory
    Device.pin_factory.reset()
