#!/bin/bash
# Run any heavy job (a -ql check, voice pre-generation, a frame grab loop) with at most 2 heavy jobs at once
# across all writers. Finals go through render_slot.sh (also 2 at once). Usage: videos/heavy.sh <command> [args...]
cd "$(dirname "$0")"
while true; do
  for i in 1 2; do
    exec 9>"/tmp/ql_slot_$i.lock"
    if flock -n 9; then nice -n 15 "$@"; exit $?; fi
  done
  sleep 15
done
