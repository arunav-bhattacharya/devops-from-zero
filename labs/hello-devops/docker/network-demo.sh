#!/usr/bin/env bash
# Day 14: containers find each other by name only on a user-defined network.
# Run it from anywhere: bash docker/network-demo.sh
# It removes everything it creates, even if a step fails.
set -euo pipefail

P=${PREFIX:-demo}   # name prefix, so the demo never clashes with your own containers
A="$P-a" B="$P-b" NET="$P-net"

cleanup() {
  docker rm -f "$A" "$B" >/dev/null 2>&1 || true
  docker network rm "$NET" >/dev/null 2>&1 || true
}
trap cleanup EXIT
cleanup

echo "1. Two containers on the default bridge network:"
docker run -d --name "$A" alpine:3.22 sleep 300 >/dev/null
docker run -d --name "$B" alpine:3.22 sleep 300 >/dev/null
if docker exec "$A" ping -c 1 -W 2 "$B" >/dev/null 2>&1; then
  echo "   $A reached $B by name"
else
  echo "   $A could not find $B by name"
fi

echo "2. Connect both to a user-defined network and try again:"
docker network create "$NET" >/dev/null
docker network connect "$NET" "$A"
docker network connect "$NET" "$B"
if docker exec "$A" ping -c 1 -W 2 "$B" >/dev/null 2>&1; then
  echo "   $A reached $B by name"
else
  echo "   $A could not find $B by name"
fi

echo "3. The DNS server $A asks now:"
docker exec "$A" grep nameserver /etc/resolv.conf | sed 's/^/   /'
