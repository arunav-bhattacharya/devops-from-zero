#!/usr/bin/env bash
# healthcheck.sh: check that hello-devops is alive and ready.
# Usage:    ./healthcheck.sh [BASE_URL]     (default: http://localhost:8000)
# Settings: RETRIES (default 5) and DELAY in seconds (default 2).
# Exit code: 0 healthy, 1 a check failed, 2 wrong usage. CI reads this number.
set -euo pipefail

if [[ $# -gt 1 ]]; then
  echo "usage: $0 [BASE_URL]" >&2
  exit 2
fi

base_url="${1:-http://localhost:8000}"
retries="${RETRIES:-5}"
delay="${DELAY:-2}"

# log: print a message to stderr, so it never mixes with real output.
log() {
  echo "healthcheck: $*" >&2
}

# check PATH: ask for one URL until it answers 200, or give up.
check() {
  local path="$1"
  local attempt code
  for ((attempt = 1; attempt <= retries; attempt++)); do
    # -s: no progress bar. -o /dev/null: throw the body away.
    # -w '%{http_code}': print only the status code (000 if nothing answered).
    # --max-time 5: give up on this try after 5 seconds.
    # || true: curl fails when it cannot connect; we handle that ourselves.
    code=$(curl -s -o /dev/null -w '%{http_code}' --max-time 5 "${base_url}${path}" || true)
    if [[ "$code" == "200" ]]; then
      log "OK   ${path} answered 200"
      return 0
    fi
    log "try ${attempt}/${retries}: ${path} answered ${code}"
    if ((attempt < retries)); then
      sleep "$delay"
    fi
  done
  log "FAIL ${path} never answered 200"
  return 1
}

check /healthz || exit 1
check /readyz || exit 1
log "all checks passed for ${base_url}"
