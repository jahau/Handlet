# Running tools as services

| Service | Runs | User | Configure |
|---------|------|------|-----------|
| `handlet-battery-guard` | [low_battery_guard.py](../power/low_battery_guard.py) | root | `--threshold`, `--warn` in `ExecStart` |
| `handlet-battery-leds` | [battery_leds.py](../power/battery_leds.py) | pi | `--pins` (LEDs not used by buttons) |
| `handlet-idle-dim` | [idle_dim.py](../display/idle_dim.py) | root | `--dim-after`, `--off-after`, `--dim-level` |
| `handlet-buttons` | [buttons.py](../gpio/buttons.py) | pi | `~/Handlet/buttons.json` |

The unit files assume the repo is cloned to `/home/pi/Handlet` and the
user is `pi`. Edit `User=` and the paths if yours differ.

```bash
sudo cp tools/systemd/*.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now handlet-battery-guard
sudo systemctl enable --now handlet-battery-leds
sudo systemctl enable --now handlet-idle-dim
sudo systemctl enable --now handlet-buttons      # needs ~/Handlet/buttons.json

# Status and logs
systemctl status 'handlet-*'
journalctl -u handlet-battery-guard -f
```

A GPIO pin can only be used by one process. If `buttons.json` lights an
LED on a pin, don't also pass that pin to `battery_leds.py`.

The button service runs as `pi`, so any command that needs root (for
example `shutdown`) must be allowed in sudoers, e.g.
`pi ALL=(root) NOPASSWD: /usr/sbin/shutdown` in `/etc/sudoers.d/handlet`
(edit with `sudo visudo -f /etc/sudoers.d/handlet`).

For your own app, see the
[template service file](../../templates/python-app/handlet-app.service).
