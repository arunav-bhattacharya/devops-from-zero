#!/usr/bin/env bash
# smoke.sh: a tiny check that the hello-devops app is alive.
# Usage: ./smoke.sh                        (checks http://localhost:8000)
#        ./smoke.sh http://localhost:9000  (checks another address)

# Stop at the first failing command (-e), treat unset variables as errors (-u),
# and let a pipe fail if any command in it fails (-o pipefail).
set -euo pipefail

# Use the first argument if there is one, otherwise the default address.
url="${1:-http://localhost:8000}"

echo "Checking ${url}/healthz"
# -s: no progress bar. -f: fail on HTTP errors such as 404 or 503.
if ! curl -sf "${url}/healthz" > /dev/null; then
  echo "FAIL: ${url} did not answer" >&2 # >&2 writes the message to stderr
  exit 1
fi

# Ask for the home page and cut the visit count out of the JSON.
visits=$(curl -sf "${url}/" | grep -o '"visits":[0-9]*' | cut -d: -f2)
echo "OK: the app is up. Visits so far: ${visits}"
