#!/usr/bin/env bash
# setup.sh: make the lab's SSH key, build the practice servers and start them.
# Run it from this folder:  ./setup.sh        Remove everything: ./setup.sh down
set -euo pipefail
cd "$(dirname "$0")"

if [[ "${1:-}" == "down" ]]; then
  docker compose down --rmi local
  rm -f .keys/known_hosts
  echo "Servers removed. The key in .keys/ stays, so the next setup reuses it."
  exit 0
fi

# 1. A key pair for the lab only, with no passphrase. It never leaves this
#    folder, and .gitignore keeps it out of git.
mkdir -p .keys
chmod 700 .keys
if [[ ! -f .keys/id_ed25519 ]]; then
  ssh-keygen -t ed25519 -N '' -C 'ansible-lab' -f .keys/id_ed25519 -q
  echo "Made a new lab key: .keys/id_ed25519"
fi

# 2. New containers get new host keys, so forget the old ones.
rm -f .keys/known_hosts

# 3. Build the image (the public key goes in) and start three servers.
docker compose up -d --build

# 4. Wait until each server accepts an SSH login with the key.
for port in 2201 2202 2203; do
  for try in $(seq 1 30); do
    if ssh -q -i .keys/id_ed25519 -p "$port" \
      -o StrictHostKeyChecking=accept-new \
      -o UserKnownHostsFile=.keys/known_hosts \
      -o ConnectTimeout=2 ubuntu@127.0.0.1 true 2>/dev/null; then
      echo "port $port: SSH is ready"
      break
    fi
    if [[ "$try" -eq 30 ]]; then
      echo "port $port: no SSH after 60 seconds. Try: docker compose logs" >&2
      exit 1
    fi
    sleep 2
  done
done
echo "All three servers are up. Next: ansible all -m ping"
