import os
import sys

import pytest
from gpiozero import Device
from gpiozero.pins.mock import MockFactory, MockPWMPin

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


@pytest.fixture(autouse=True)
def mock_pins():
    Device.pin_factory = MockFactory(pin_class=MockPWMPin)
    yield Device.pin_factory
    Device.pin_factory.reset()
