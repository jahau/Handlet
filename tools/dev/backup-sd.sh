#!/usr/bin/env bash
# Back up the Pi's SD card over the network to the machine you run this
# on, compressed. Restore with Raspberry Pi Imager ("Use custom").
#
#   ./backup-sd.sh pi@raspberrypi.local
#   ./backup-sd.sh handlet ~/backups
#
# The image is taken from a live system, so stop busy services first.
# For a guaranteed-consistent image, put the card in a reader instead.
set -euo pipefail

TARGET="${1:?Usage: $0 user@host [output-dir]}"
OUT_DIR="${2:-.}"
OUT="$OUT_DIR/handlet-$(date +%Y%m%d-%H%M%S).img.gz"

DEV=$(ssh "$TARGET" "lsblk -no pkname \$(findmnt -no source /)")
echo "==> Reading /dev/$DEV from $TARGET -> $OUT"
ssh "$TARGET" "sudo sync && sudo dd if=/dev/$DEV bs=4M status=progress | gzip -1" > "$OUT"
echo "==> Done: $(du -h "$OUT" | cut -f1)"
