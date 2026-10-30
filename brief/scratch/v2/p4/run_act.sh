#!/usr/bin/env bash
# Run the Day 20 worked example with act and save the real output.
# Usage: run_act.sh /path/to/act WORKDIR
# Needs Docker and the ubuntu:24.04 image. Output goes to files/out-*.txt.
set -euo pipefail
ACT=$1
WORK=$2
HERE=$(cd "$(dirname "$0")" && pwd)
FILES=$HERE/files
rm -rf "$WORK"
mkdir -p "$WORK/.github/workflows"
cd "$WORK"
git init -q -b main
git config user.email learner@example.com
git config user.name Learner
cp "$FILES/logic-demo.yml" .github/workflows/logic-demo.yml
git add -A
git commit -qm "Add logic demo"

run() { "$ACT" workflow_dispatch -P ubuntu-latest=ubuntu:24.04 --pull=false "$@" 2>&1 | grep -v 'level=' || true; }

"$ACT" -l 2>&1 | grep -v 'level=' | sed 's/[[:space:]]*$//' > "$FILES/out-list.txt"
run | grep -F ' | ' > "$FILES/out-run.txt"
run --input break-build=true | grep -E ' \| |exitcode|^Error' > "$FILES/out-break.txt"

# Step 6: move the build job into a reusable workflow.
cp "$FILES/logic-demo-reusable.yml" .github/workflows/logic-demo.yml
cp "$FILES/build.yml" .github/workflows/build.yml
git add -A
git commit -qm "Move build into a reusable workflow"
run | grep -F ' | ' > "$FILES/out-reusable.txt"

for f in list run break reusable; do echo "== $f"; cat "$FILES/out-$f.txt"; done
