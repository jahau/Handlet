import shutil
import subprocess
import sys

import pytest
from battery_leds import is_charging, plan
from battery_monitor import _swap16, voltage_to_percent
from idle_dim import next_state

# --- battery_monitor -------------------------------------------------------

@pytest.mark.parametrize("volts,expected", [(4.3, 100), (4.2, 100), (3.75, 50), (3.0, 0), (2.5, 0)])
def test_voltage_to_percent_anchor_points(volts, expected):
    assert voltage_to_percent(volts) == pytest.approx(expected)


def test_voltage_to_percent_is_monotonic():
    values = [voltage_to_percent(3.0 + i * 0.01) for i in range(121)]
    assert values == sorted(values)


def test_swap16():
    assert _swap16(0x3412) == 0x1234


# --- battery_leds ----------------------------------------------------------

def test_plan_single_led():
    assert plan(80, False, 1) == ["on"]
    assert plan(30, False, 1) == ["slow"]
    assert plan(10, False, 1) == ["fast"]
    assert plan(10, True, 1) == ["pulse"]
    assert plan(None, False, 1) == ["off"]


def test_plan_bar():
    assert plan(100, False, 3) == ["on", "on", "on"]
    assert plan(50, False, 3) == ["on", "on", "off"]
    assert plan(5, False, 3) == ["fast", "off", "off"]
    assert plan(40, True, 3) == ["on", "on", "pulse"]
    assert plan(100, True, 3) == ["on", "on", "on"]


def test_is_charging():
    assert is_charging("Charging")
    assert is_charging("Full")
    assert not is_charging("Discharging")
    assert not is_charging(None)


# --- idle_dim --------------------------------------------------------------

def test_idle_states():
    assert next_state("normal", 5, 30, 120) == "normal"
    assert next_state("normal", 31, 30, 120) == "dim"
    assert next_state("dim", 121, 30, 120) == "off"
    assert next_state("off", 0, 30, 120) == "normal"


def test_idle_never_off():
    assert next_state("dim", 10_000, 30, 0) == "dim"


# --- buttons ---------------------------------------------------------------

def test_buttons_setup_attaches_handlers():
    import buttons

    keep = buttons.setup({"buttons": [
        {"name": "a", "pin": 5, "led": 19, "press": "true"},
        {"name": "b", "pin": 6, "hold": "true"},
    ]})
    (btn_a, led_a), (btn_b, led_b) = keep
    assert btn_a.when_pressed is not None and led_a is not None
    assert btn_b.when_held is not None and led_b is None
    for btn, led in keep:
        btn.close()
        if led:
            led.close()


# --- shell scripts ---------------------------------------------------------

@pytest.mark.skipif(sys.platform == "win32" or not shutil.which("bash"), reason="needs Linux bash")
def test_throttle_check_decodes_flags():
    r = subprocess.run(["bash", "tools/system/throttle-check.sh", "0x50005"],
                       capture_output=True, text=True)
    assert r.returncode == 2
    assert "Under-voltage detected NOW" in r.stdout
    assert "Throttling has occurred" in r.stdout


@pytest.mark.skipif(sys.platform == "win32" or not shutil.which("bash"), reason="needs Linux bash")
def test_throttle_check_ok():
    r = subprocess.run(["bash", "tools/system/throttle-check.sh", "0x0"],
                       capture_output=True, text=True)
    assert r.returncode == 0
    assert "OK" in r.stdout
