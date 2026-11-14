# Raspberry Pi 4B 40-pin header

Physical pin numbers on the outside, BCM (GPIO) numbers inside. Software
like `gpiozero` uses the **BCM** numbers. Run `pinout` on the Pi for a
picture of your own board.

| Function        | BCM  | Pin | Pin | BCM  | Function        |
|-----------------|------|----:|:----|------|-----------------|
| 3.3 V           |      |   1 | 2   |      | 5 V             |
| I2C1 SDA        | 2    |   3 | 4   |      | 5 V             |
| I2C1 SCL        | 3    |   5 | 6   |      | GND             |
| GPCLK0          | 4    |   7 | 8   | 14   | UART TX         |
| GND             |      |   9 | 10  | 15   | UART RX         |
|                 | 17   |  11 | 12  | 18   | PCM CLK / PWM0  |
|                 | 27   |  13 | 14  |      | GND             |
|                 | 22   |  15 | 16  | 23   |                 |
| 3.3 V           |      |  17 | 18  | 24   |                 |
| SPI0 MOSI       | 10   |  19 | 20  |      | GND             |
| SPI0 MISO       | 9    |  21 | 22  | 25   |                 |
| SPI0 SCLK       | 11   |  23 | 24  | 8    | SPI0 CE0        |
| GND             |      |  25 | 26  | 7    | SPI0 CE1        |
| ID EEPROM SDA   | 0    |  27 | 28  | 1    | ID EEPROM SCL   |
|                 | 5    |  29 | 30  |      | GND             |
|                 | 6    |  31 | 32  | 12   | PWM0            |
| PWM1            | 13   |  33 | 34  |      | GND             |
| PCM FS / PWM1   | 19   |  35 | 36  | 16   |                 |
|                 | 26   |  37 | 38  | 20   | PCM DIN         |
| GND             |      |  39 | 40  | 21   | PCM DOUT        |

## Practical notes

- **GPIO is 3.3 V only.** 5 V on a GPIO pin will damage the SoC.
- Max ~16 mA per pin, ~50 mA total. Drive LEDs through a resistor
  (330 Ω–1 kΩ) and anything bigger through a transistor/MOSFET.
- **BCM 3 (pin 5)** wakes a halted Pi when pulled to GND, which makes it
  the natural power button. Pair it with
  `dtoverlay=gpio-shutdown,gpio_pin=3` for press-to-shutdown.
- BCM 2/3 have fixed 1.8 kΩ pull-ups (I2C). Using BCM 3 as a button is
  fine; it can share with I2C devices only if you accept the conflict.
- Avoid BCM 0/1 (HAT EEPROM) and BCM 14/15 if you use the serial console.
- Hardware PWM is available on BCM 12, 13, 18, 19 (useful for fan or
  backlight control).
- Free general-purpose pins with no alternate function in common use:
  BCM 4, 5, 6, 16, 17, 20, 21, 22, 23, 24, 25, 26, 27.
