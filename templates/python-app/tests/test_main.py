"""Runs without hardware: gpiozero's MockFactory simulates the pins."""
from gpiozero import Device
from main import App


def test_press_toggles_led():
    app = App(button_pin=5, led_pin=19, bounce=None)
    pin = Device.pin_factory.pin(5)

    pin.drive_low()   # press (button pulls to GND)
    assert app.led.is_lit
    assert app.presses == 1

    pin.drive_high()  # release
    pin.drive_low()   # press again
    assert not app.led.is_lit
    assert app.presses == 2
    app.close()


def test_stop_ends_run_loop():
    app = App(button_pin=5, led_pin=19)
    app.stop()
    app.run(interval=0.01)  # returns immediately because stop was set
    app.close()
