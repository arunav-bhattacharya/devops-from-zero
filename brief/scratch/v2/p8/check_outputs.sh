#!/usr/bin/env bash
# Capture real output for the Day 40 worked example (kustomize + git), and
# validate every lab file Part 8 owns. Run from anywhere:
#   bash brief/scratch/v2/p8/check_outputs.sh
# Needs: kubectl (with kustomize built in), kustomize, kubeconform, actionlint,
# and JSON schemas made from the Argo CD / Image Updater CRDs in $SCHEMAS.
set -euo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$HERE/../../../.." && pwd)"
LAB="$ROOT/labs/hello-devops"
OUTS="$HERE/outputs"
SCRATCH="${SCRATCH:?set SCRATCH to a scratch directory}"
SCHEMAS="${SCHEMAS:-$SCRATCH/p8schemas}"
mkdir -p "$OUTS"

# ---- 1. Validate the lab files this part owns ----
echo "== kubeconform"
kubeconform -strict -summary \
  -schema-location default \
  -schema-location "$SCHEMAS/{{.ResourceKind}}_{{.ResourceAPIVersion}}.json" \
  "$LAB"/argocd/*.yaml "$LAB/gitops/smoke-test.yaml"
echo "== actionlint"
actionlint "$LAB/gitops/bump-image.yml" && echo "actionlint: no errors"

# The overlays belong to the Kustomize lesson (Day 37). Render them if present.
for env in dev prod; do
  if [ -f "$LAB/k8s/overlays/$env/kustomization.yaml" ]; then
    echo "== render overlay $env"
    kubectl kustomize "$LAB/k8s/overlays/$env" > "$SCRATCH/p8-render-$env.yaml"
    kubeconform -strict -summary "$SCRATCH/p8-render-$env.yaml"
  else
    echo "!! overlay $env is missing"
  fi
done

# ---- 2. Real output for the worked example ----
# Work on a throw-away git copy of the lab, never on the lab itself.
WORK="$SCRATCH/p8-worked-$(date +%s)"
mkdir -p "$WORK"
cp -R "$LAB/k8s" "$WORK/k8s"
cd "$WORK"
git init -q -b main
git add -A
git -c user.name=you -c user.email=you@example.com commit -qm "start"

IMG="ghcr.io/<you>/hello-devops"
# Start both environments on 1.0.0 with the learner's registry image.
for env in dev prod; do
  (cd "k8s/overlays/$env" && kustomize edit set image "hello-devops=$IMG:1.0.0")
done
git -c user.name=you -c user.email=you@example.com commit -qam "both on 1.0.0"

{
  for env in dev prod; do
    echo "\$ kubectl kustomize k8s/overlays/$env | grep 'image:'"
    kubectl kustomize "k8s/overlays/$env" | grep 'image:'
  done
} > "$OUTS/01-images-before.txt"

{
  echo "\$ cd k8s/overlays/dev"
  echo "\$ kustomize edit set image hello-devops=$IMG:1.1.0"
  (cd k8s/overlays/dev && kustomize edit set image "hello-devops=$IMG:1.1.0")
  echo "\$ git diff --stat"
  git diff --stat
  echo "\$ git diff -U0 | grep '^[-+] '"
  git diff -U0 | grep '^[-+] ' || true
} > "$OUTS/02-bump-dev.txt"
git -c user.name=you -c user.email=you@example.com commit -qam "dev 1.1.0"

{
  echo "\$ cd ../prod"
  echo "\$ kustomize edit set image hello-devops=$IMG:1.1.0"
  (cd k8s/overlays/prod && kustomize edit set image "hello-devops=$IMG:1.1.0")
  echo "\$ git diff -U0 | grep '^[-+] '"
  git diff -U0 | grep '^[-+] ' || true
} > "$OUTS/03-promote-prod.txt"

echo "== captured"
for f in "$OUTS"/*.txt; do echo "--- $f"; cat "$f"; done
