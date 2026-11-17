#!/bin/bash
# Run render_hd.sh, but at most 2 final renders at once across all writers (4 shared cores).
# Usage: same as render_hd.sh. Waits for a free slot.
cd "$(dirname "$0")"
while true; do
  for i in 1 2; do
    exec 9>"/tmp/hd_slot_$i.lock"
    if flock -n 9; then ./render_hd.sh "$@"; exit $?; fi
  done
  sleep 20
done
