#!/bin/bash
# Run a quick -ql check, but at most 2 quick checks at once across all writers (4 shared cores).
# Usage: videos/quick_slot.sh <file.py relative to videos/> <SceneClass>
cd "$(dirname "$0")"
F=$1; S=$2
MANIM=${MANIM:-/home/user/videotools/manimenv/bin/manim}
while true; do
  for i in 1 2; do
    exec 9>"/tmp/ql_slot_$i.lock"
    if flock -n 9; then nice -n 15 "$MANIM" -ql --disable_caching --media_dir "media/$S" "$F" "$S"; exit $?; fi
  done
  sleep 15
done
