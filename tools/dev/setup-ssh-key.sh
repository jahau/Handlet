#!/usr/bin/env bash
# Set up password-less SSH to the Pi and add a short host alias, so that
# `ssh handlet` and `./deploy.sh` work without typing a password.
#
#   ./setup-ssh-key.sh pi@raspberrypi.local [alias]
set -euo pipefail

TARGET="${1:?Usage: $0 user@host [alias]}"
ALIAS="${2:-handlet}"
KEY="$HOME/.ssh/id_ed25519"

mkdir -p "$HOME/.ssh"
[[ -f "$KEY" ]] || ssh-keygen -t ed25519 -f "$KEY" -N "" -C "handlet-dev"

# ssh-copy-id is missing on some Windows setups; fall back to a pipe.
if command -v ssh-copy-id >/dev/null; then
  ssh-copy-id -i "$KEY.pub" "$TARGET"
else
  ssh "$TARGET" 'mkdir -p ~/.ssh && chmod 700 ~/.ssh && cat >> ~/.ssh/authorized_keys && chmod 600 ~/.ssh/authorized_keys' < "$KEY.pub"
fi

USER_PART="${TARGET%@*}"
HOST_PART="${TARGET#*@}"
if ! grep -q "^Host $ALIAS\$" "$HOME/.ssh/config" 2>/dev/null; then
  cat >> "$HOME/.ssh/config" <<EOF

Host $ALIAS
    HostName $HOST_PART
    User $USER_PART
    IdentityFile $KEY
    ServerAliveInterval 30
EOF
  echo "Added host alias '$ALIAS' to ~/.ssh/config"
fi

echo "Done. Try: ssh $ALIAS   or   PI_HOST=$ALIAS ./deploy.sh ./myapp"
