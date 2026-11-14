# Handlet Python app template

A starting point for a Handlet app: GPIO through `gpiozero`, logging,
clean shutdown under systemd, and tests that run on any PC.

## Start a new project

```bash
cp -r templates/python-app ~/projects/myapp
cd ~/projects/myapp
```

## Develop and test on your PC

```bash
python -m venv .venv
. .venv/bin/activate            # Windows: .venv\Scripts\activate
pip install -r requirements.txt pytest
pytest                          # pins are simulated, no Pi needed
```

## Deploy and run on the Pi

```bash
PI_HOST=handlet ../Handlet/tools/dev/deploy.sh . "python3 main.py"
```

On the Pi, the first time:

```bash
cd ~/myapp
python3 -m venv --system-site-packages .venv   # reuse apt's gpiozero/lgpio
.venv/bin/pip install -r requirements.txt
```

## Run at boot

```bash
sudo cp handlet-app.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now handlet-app
journalctl -u handlet-app -f
```

Edit `WorkingDirectory`, `ExecStart` and the pin variables in the
service file to match your project.
