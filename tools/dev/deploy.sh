#!/usr/bin/env bash
# Copy a project folder from your development machine to the Pi and
# optionally run a command there. Uses only ssh + tar, so it works from
# Linux, macOS and Git Bash on Windows (no rsync needed).
#
#   ./deploy.sh ./myapp                         # -> pi@raspberrypi.local:~/myapp
#   ./deploy.sh ./myapp "python3 main.py"       # deploy and run
#   PI_HOST=pi@192.168.1.50 ./deploy.sh ./myapp
#   ./deploy.sh ./myapp --watch "python3 main.py"   # redeploy on change (needs inotifywait/fswatch)
set -euo pipefail

PI_HOST="${PI_HOST:-pi@raspberrypi.local}"
SRC="${1:?Usage: $0 <local-dir> [--watch] [remote-command]}"
shift
WATCH=0
[[ "${1:-}" == "--watch" ]] && { WATCH=1; shift; }
CMD="${1:-}"

NAME=$(basename "$(cd "$SRC" && pwd)")
DEST="${PI_DEST:-~/$NAME}"

deploy() {
  echo "==> $SRC -> $PI_HOST:$DEST"
  tar -C "$SRC" -czf - \
      --exclude=.git --exclude=__pycache__ --exclude=.venv --exclude=node_modules . \
    | ssh "$PI_HOST" "mkdir -p $DEST && tar -xzf - -C $DEST"
  if [[ -n "$CMD" ]]; then
    echo "==> running: $CMD"
    ssh -t "$PI_HOST" "cd $DEST && $CMD" || true
  fi
}

deploy

if (( WATCH )); then
  if command -v inotifywait >/dev/null; then
    while inotifywait -qq -r -e modify,create,delete,move "$SRC"; do deploy; done
  elif command -v fswatch >/dev/null; then
    fswatch -o "$SRC" | while read -r _; do deploy; done
  else
    echo "--watch needs inotifywait (inotify-tools) or fswatch" >&2
    exit 1
  fi
fi
