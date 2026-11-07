#!/usr/bin/env bash
# Re-run the offline checks for labs/hello-devops/mesh (Part 15).
# Usage: bash brief/scratch/v3/mesh/validate_labs.sh [WORK_DIR]
# Downloads the CRD files the projects publish, turns them into kubeconform schemas,
# validates every manifest, prints the CEL rules to check by hand, and validates envoy.yaml.
set -euo pipefail
ROOT=$(cd "$(dirname "$0")/../../../.." && pwd)
HERE="$ROOT/brief/scratch/v3/mesh"
LAB="$ROOT/labs/hello-devops/mesh"
W=${1:-$(mktemp -d)}
mkdir -p "$W/crds"
cd "$W/crds"
curl -sSfo istio-1.31.yaml https://raw.githubusercontent.com/istio/api/release-1.31/kubernetes/customresourcedefinitions.gen.yaml
for v in v1.5.1 v1.6.0 v1.7.0; do
  curl -sSfLo "gwapi-$v.yaml" "https://github.com/kubernetes-sigs/gateway-api/releases/download/$v/standard-install.yaml"
done
for f in istio-1.31 gwapi-v1.5.1 gwapi-v1.6.0 gwapi-v1.7.0; do
  python3 -I "$HERE/crd2schema.py" "$W/schemas-$f" "$f.yaml" > /dev/null
done
loc() { echo "$W/schemas-$1/{{.Group}}/{{.ResourceKind}}_{{.ResourceAPIVersion}}.json"; }

echo "== Istio lab: built-in kinds, Istio 1.31 CRDs, Gateway API v1.6.0"
(cd "$LAB/istio" && kubeconform -strict -summary -schema-location default \
  -schema-location "$(loc istio-1.31)" -schema-location "$(loc gwapi-v1.6.0)" ./*.yaml ambient/*.yaml)
echo "== Linkerd lab: built-in kinds, Gateway API v1.5.1"
(cd "$LAB/linkerd" && kubeconform -strict -summary -schema-location default \
  -schema-location "$(loc gwapi-v1.5.1)" namespace.yaml httproute-canary.yaml ../istio/apps.yaml)
echo "== CEL rules to check by hand"
(cd "$LAB/istio" && python3 -I "$HERE/celrules.py" "$W/crds/istio-1.31.yaml" ./*.yaml ambient/*.yaml | cut -c1-200)
(cd "$LAB/linkerd" && python3 -I "$HERE/celrules.py" "$W/crds/gwapi-v1.5.1.yaml" httproute-canary.yaml | cut -c1-200)
echo "== Envoy config"
docker run --rm --name mesh-envoy-validate -v "$LAB/envoy/envoy.yaml:/etc/envoy/envoy.yaml:ro" \
  envoyproxy/envoy:v1.40.2 envoy --mode validate -c /etc/envoy/envoy.yaml 2>&1 | tail -1
echo "work dir: $W"
