#!/usr/bin/env bash
# Capstone acceptance checks (Day 55).
# Each check runs one command and prints PASS, FAIL or SKIP.
# SKIP means "the tool or endpoint is not there", for example Dynatrace or a stopped stack.
# The script exits with 1 when any check fails, so it also works in CI.
#
# Needs: curl, jq, kubectl (pointing at your kind cluster). Optional: gh, cosign.
# Usage:   GITHUB_USER=<you> VERSION=1.2.0 security/capstone-check.sh
# Override any address, for example: PROM_URL=http://localhost:9091 security/capstone-check.sh
set -uo pipefail

GITHUB_USER="${GITHUB_USER:?set GITHUB_USER to your GitHub user name}"
VERSION="${VERSION:?set VERSION to the release you deployed, for example 1.2.0}"
APP_URL="${APP_URL:-http://localhost:8081/}"
PROM_URL="${PROM_URL:-http://localhost:9090}"
GRAFANA_URL="${GRAFANA_URL:-http://localhost:3000}"
ES_URL="${ES_URL:-http://localhost:9200}"
JAEGER_URL="${JAEGER_URL:-http://localhost:16686}"
JVM_REPO="${JVM_REPO:-${GITHUB_USER}/hello-jvm}"
owner=$(echo "$GITHUB_USER" | tr '[:upper:]' '[:lower:]')

pass=0 fail=0 skip=0
ok()   { echo "PASS  $1"; pass=$((pass + 1)); }
bad()  { echo "FAIL  $1"; fail=$((fail + 1)); }
miss() { echo "SKIP  $1"; skip=$((skip + 1)); }

# 1. Kubernetes (Part 7): the Deployment is fully rolled out.
if kubectl -n hello rollout status deploy/hello-devops --timeout=60s > /dev/null 2>&1; then
  ok "Deployment hello-devops is rolled out"
else
  bad "Deployment hello-devops is not ready (kubectl -n hello get pods)"
fi

# 2. The app answers through the kind NodePort and reports the released version.
got=$(curl -fs --max-time 5 "$APP_URL" | jq -r .version 2>/dev/null)
if [[ "$got" == "$VERSION" ]]; then ok "App at $APP_URL reports version $VERSION"
else bad "App at $APP_URL reports version '${got:-no answer}', expected $VERSION"; fi

# 3. Parts 4 and 13: every app Pod runs the released GHCR image, never :latest.
images=$(kubectl -n hello get pods -l app=hello-devops -o jsonpath='{.items[*].spec.containers[*].image}')
want="ghcr.io/${owner}/hello-devops"
if [[ -n "$images" ]] && ! tr ' ' '\n' <<< "$images" | grep -v -q "^${want}[:@]" \
  && ! grep -q ':latest' <<< "$images"; then
  ok "Pods run ${want} (not :latest)"
else
  bad "Pods run '${images:-nothing}', expected ${want}:<version> or @sha256:..."
fi

# 4. Part 8: Argo CD reports the app Synced and Healthy.
st=$(kubectl -n argocd get application hello-devops -o jsonpath='{.status.sync.status}/{.status.health.status}' 2>/dev/null)
if [[ "$st" == "Synced/Healthy" ]]; then ok "Argo CD: Synced/Healthy"
elif [[ -z "$st" ]]; then bad "Argo CD Application hello-devops not found in namespace argocd"
else bad "Argo CD: $st"; fi

# 5. Part 13: the cluster refuses a :latest image (Kyverno disallow-latest-tag).
out=$(kubectl -n hello run capstone-latest --image=nginx:latest --restart=Never --dry-run=server 2>&1)
if grep -qi 'latest' <<< "$out" && ! grep -q 'created' <<< "$out"; then ok "Kyverno rejects :latest"
else bad "A :latest Pod was accepted. Is Kyverno installed and policy/ applied?"; fi

# 6. Part 13: the image is signed by your release workflow (needs cosign).
if command -v cosign > /dev/null; then
  if cosign verify "${want}:${VERSION}" \
    --certificate-identity "https://github.com/${GITHUB_USER}/hello-devops/.github/workflows/release.yml@refs/tags/v${VERSION}" \
    --certificate-oidc-issuer https://token.actions.githubusercontent.com > /dev/null 2>&1; then
    ok "cosign: ${want}:${VERSION} is signed by release.yml"
  else bad "cosign could not verify ${want}:${VERSION}"; fi
else miss "cosign not installed (brew install cosign)"; fi

# 7. Part 5: the last hello-jvm CI run succeeded (needs gh).
if command -v gh > /dev/null; then
  c=$(gh run list --repo "$JVM_REPO" --limit 1 --json conclusion -q '.[0].conclusion' 2>/dev/null)
  if [[ "$c" == "success" ]]; then ok "hello-jvm: last CI run succeeded"
  elif [[ -z "$c" ]]; then miss "no CI runs found in $JVM_REPO (set JVM_REPO=owner/repo)"
  else bad "hello-jvm: last CI run is '$c'"; fi
else miss "gh not installed"; fi

# 8. Part 9: Prometheus has the app's request counter.
n=$(curl -fsG --max-time 5 "${PROM_URL}/api/v1/query" --data-urlencode 'query=sum(hello_requests_total)' \
  | jq -r '.data.result[0].value[1] // empty' 2>/dev/null)
if [[ -n "$n" ]]; then ok "Prometheus: sum(hello_requests_total) = $n"
else bad "Prometheus at $PROM_URL has no hello_requests_total (is the port-forward running?)"; fi

# 9. Part 10: Grafana is up and its database is fine.
g=$(curl -fs --max-time 5 "${GRAFANA_URL}/api/health" | jq -r .database 2>/dev/null)
if [[ "$g" == "ok" ]]; then ok "Grafana is healthy"
else bad "Grafana at $GRAFANA_URL did not answer /api/health"; fi

# 10. Part 11: Elasticsearch holds log documents.
docs=$(curl -fs --max-time 5 "${ES_URL}/_count" | jq -r '.count // 0' 2>/dev/null)
if [[ "${docs:-0}" -gt 0 ]]; then ok "Elasticsearch holds $docs documents"
else bad "Elasticsearch at $ES_URL has no documents (is Fluent Bit shipping?)"; fi

# 11. Part 11: Jaeger has received traces from at least one service.
svc=$(curl -fs --max-time 5 "${JAEGER_URL}/api/services" | jq -r '.data // [] | join(", ")' 2>/dev/null)
if [[ -n "$svc" ]]; then ok "Jaeger has traces from: $svc"
else bad "Jaeger at $JAEGER_URL has no services yet (send some requests first)"; fi

echo
echo "${pass} passed, ${fail} failed, ${skip} skipped"
[[ "$fail" -eq 0 ]]
