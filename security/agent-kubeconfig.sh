#!/usr/bin/env bash
# Make a separate kubeconfig file for the ai-agent ServiceAccount (Day 54).
# The file holds one short-lived token and nothing else. A tool that uses it can
# only do what policy/ai-agent-readonly.yaml allows, and only until the token expires.
#
# Needs: policy/ai-agent-readonly.yaml applied, and kubectl pointing at your kind cluster.
# Usage: security/agent-kubeconfig.sh [duration]          (default: 1h)
# Then:  KUBECONFIG=~/.kube/ai-agent.kubeconfig kubectl get pods
set -euo pipefail

duration="${1:-1h}"
# Outside the repo on purpose: the file holds a token, so it must never be committed.
out="${HOME}/.kube/ai-agent.kubeconfig"

# The address and CA certificate of the cluster your current context uses.
server=$(kubectl config view --minify --raw -o jsonpath='{.clusters[0].cluster.server}')
ca=$(kubectl config view --minify --raw -o jsonpath='{.clusters[0].cluster.certificate-authority-data}')
if [[ -z "$server" || -z "$ca" ]]; then
  echo "Could not read the cluster address or CA from your current kubectl context." >&2
  exit 1
fi

# Ask the API server for a token for the ai-agent ServiceAccount that expires after $duration.
token=$(kubectl -n hello create token ai-agent --duration="$duration")

mkdir -p "$(dirname "$out")"
# Only you may read the file (chmod 600 before the token goes in).
umask 077
cat > "$out" <<KUBECONFIG
apiVersion: v1
kind: Config
clusters:
  - name: devops
    cluster:
      server: ${server}
      certificate-authority-data: ${ca}
users:
  - name: ai-agent
    user:
      token: ${token}
contexts:
  - name: ai-agent
    context:
      cluster: devops
      user: ai-agent
      namespace: hello
current-context: ai-agent
KUBECONFIG

echo "Wrote ${out}. The token expires after ${duration}."
echo "Try: KUBECONFIG=${out} kubectl get pods"
