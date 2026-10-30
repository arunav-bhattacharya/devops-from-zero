#!/usr/bin/env bash
# Checks that Docker works and shows which CPU type your containers use.
set -euo pipefail

echo "Docker client and server:"
docker version --format 'client {{.Client.Version}}, server {{.Server.Version}} ({{.Server.Os}}/{{.Server.Arch}})'

echo "CPU type inside a container:"
docker run --rm alpine uname -m

echo "Containers on this machine (running and stopped):"
docker ps -a --format '{{.Names}}  {{.Image}}  {{.Status}}'
