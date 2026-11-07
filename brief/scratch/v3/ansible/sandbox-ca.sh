#!/usr/bin/env bash
# Test-only helper for this sandbox: its egress gateway re-signs TLS, so the
# practice containers need the sandbox CA bundle for pip. Not part of the lab.
set -euo pipefail
for c in ansible-web1 ansible-web2 ansible-lb1; do
  docker cp /root/.ccr/ca-bundle.crt "$c":/etc/ssl/sandbox-bundle.crt
  docker exec "$c" bash -c 'printf "[global]\ncert = /etc/ssl/sandbox-bundle.crt\n" > /etc/pip.conf'
done
echo "sandbox CA bundle installed"
