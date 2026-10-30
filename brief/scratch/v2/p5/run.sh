#!/usr/bin/env bash
# Run one Gradle command in a project dir and save plain output (sandbox proxy line removed).
# usage: run.sh <dir> <outname> <gradle args...>
dir=$1; name=$2; shift 2
out=/tmp/claude-0/-home-user/5a31be1b-d2d7-5096-8c55-314d3e3b0058/scratchpad/p5out/$name.txt
cd "$dir" && ./gradlew "$@" --console=plain 2>&1 | grep -v '^Picked up JAVA_TOOL_OPTIONS' > "$out"
echo "== $name (exit ${PIPESTATUS[0]})"; cat "$out"
