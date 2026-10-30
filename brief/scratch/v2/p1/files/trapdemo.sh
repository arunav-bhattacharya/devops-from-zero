#!/usr/bin/env bash
set -euo pipefail
tmp=$(mktemp)
# Whatever happens next, delete the temp file when the script exits.
trap 'rm -f "$tmp"; echo "cleaned up $tmp"' EXIT

grep ERROR app.log > "$tmp"
echo "saved $(wc -l < "$tmp") error lines to $tmp"
false    # pretend a later step fails here
echo "this line never runs"
