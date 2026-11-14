#!/usr/bin/env bash
# Find Raspberry Pis on the local network.
#
#   ./find-pi.sh                    # try mDNS, then scan the ARP table
#   ./find-pi.sh 192.168.1.0/24     # active scan with nmap
#
# Raspberry Pi Foundation / Raspberry Pi Ltd MAC prefixes are used to
# recognise boards in the ARP table.
set -uo pipefail

PI_OUIS='b8:27:eb|dc:a6:32|e4:5f:01|d8:3a:dd|28:cd:c1|2c:cf:67'

echo "=== mDNS ==="
for h in raspberrypi.local handlet.local; do
  if ip=$(getent hosts "$h" 2>/dev/null | awk '{print $1}') && [[ -n "$ip" ]]; then
    echo "$h -> $ip"
  elif ping -c1 -W1 "$h" >/dev/null 2>&1 || ping -n 1 -w 1000 "$h" >/dev/null 2>&1; then
    echo "$h responds to ping"
  fi
done

if [[ -n "${1:-}" ]]; then
  echo
  echo "=== nmap scan of $1 ==="
  command -v nmap >/dev/null || { echo "nmap not installed"; exit 1; }
  sudo nmap -sn "$1" | grep -iB2 'Raspberry'
  exit 0
fi

echo
echo "=== ARP table (Raspberry Pi MAC prefixes) ==="
# Linux/macOS use colons, Windows 'arp -a' uses dashes.
arp -a 2>/dev/null | tr 'A-F-' 'a-f:' | grep -E "$PI_OUIS" \
  || echo "None found. Ping the subnet first or pass a CIDR to use nmap."
