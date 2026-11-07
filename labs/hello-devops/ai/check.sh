#!/usr/bin/env bash
# Run every check this repository has, in one command (Day 65).
# People and coding agents run the same script before they call a change done.
# AGENTS.md tells agents to run it.
#
# Each check prints PASS, FAIL or SKIP. SKIP means the tool is not installed.
# On a FAIL you see the last lines of that tool's output.
# The script exits with 1 if any check failed, so CI could run it too.
#
# Usage, from anywhere in the repository: ai/check.sh
# Install the tools on a Mac: brew install kubeconform actionlint shellcheck
set -uo pipefail

# Work from the repository root, one folder above this script.
cd "$(dirname "$0")/.." || exit 1

pass=0 fail=0 skip=0
out=$(mktemp)
trap 'rm -f "$out"' EXIT

# check NAME TOOL COMMAND [ARGS...]: run COMMAND if TOOL is installed.
check() {
  local name=$1 tool=$2
  shift 2
  if ! command -v "$tool" >/dev/null 2>&1; then
    echo "SKIP  $name ($tool is not installed)"
    skip=$((skip + 1))
    return
  fi
  if "$@" >"$out" 2>&1; then
    echo "PASS  $name"
    pass=$((pass + 1))
  else
    echo "FAIL  $name"
    tail -n 15 "$out" | sed 's/^/      /'
    fail=$((fail + 1))
  fi
}

check "ruff lint" ruff ruff check .
check "ruff format" ruff ruff format --check .
check "pytest" pytest pytest -q

# Kubernetes YAML against the official schemas. -strict also rejects unknown
# fields, the mistake AI tools make most. The second schema location covers
# CRDs such as the Gateway API. kustomization.yaml is not a Kubernetes object.
check "kubeconform k8s/" kubeconform kubeconform -strict -summary \
  -schema-location default \
  -schema-location 'https://raw.githubusercontent.com/datreeio/CRDs-catalog/main/{{.Group}}/{{.ResourceKind}}_{{.ResourceAPIVersion}}.json' \
  -ignore-filename-pattern kustomization \
  k8s/

check "helm lint" helm helm lint chart/hello-devops
check "actionlint" actionlint actionlint
check "terraform fmt" terraform terraform fmt -check -recursive infra

# Every shell script in the repository.
scripts=()
while IFS= read -r f; do scripts+=("$f"); done < <(find . -name '*.sh' -not -path './.venv/*' -not -path './.git/*')
check "shellcheck" shellcheck shellcheck "${scripts[@]}"

echo "----"
echo "$pass passed, $fail failed, $skip skipped"
[[ $fail -eq 0 ]]
