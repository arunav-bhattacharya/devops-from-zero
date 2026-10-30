#!/usr/bin/env bash
# Day 14: back up a named volume to a .tgz file in this folder, or restore one.
#   bash docker/volume-backup.sh backup  <volume>
#   bash docker/volume-backup.sh restore <volume> <file.tgz>
# A short-lived alpine container mounts the volume and runs tar.
set -euo pipefail

action=${1:-}
volume=${2:-}

case "$action" in
  backup)
    # Stop here if the volume does not exist. Otherwise docker run would
    # quietly create a new, empty one and back that up.
    docker volume inspect "$volume" >/dev/null
    file="$volume-$(date +%Y%m%d-%H%M%S).tgz"
    docker run --rm -v "$volume":/data:ro -v "$PWD":/backup alpine:3.22 \
      tar czf "/backup/$file" -C /data .
    echo "Saved $file"
    ;;
  restore)
    file=${3:?give the .tgz file to restore, from this folder}
    docker run --rm -v "$volume":/data -v "$PWD":/backup:ro alpine:3.22 \
      tar xzf "/backup/$file" -C /data
    echo "Restored $file into volume $volume"
    ;;
  *)
    echo "Usage: $0 backup <volume> | restore <volume> <file.tgz>" >&2
    exit 2
    ;;
esac
