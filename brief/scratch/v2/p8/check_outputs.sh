#!/usr/bin/env bash
# Validate the lab files Part 8 owns, and capture real output for the Day 40
# worked example (kubectl kustomize, kustomize edit, yq and git).
#   SCRATCH=/some/tmp/dir bash brief/scratch/v2/p8/check_outputs.sh
# Needs on PATH: kubectl, kustomize, kubeconform, actionlint (+ shellcheck), and
# mikefarah yq v4 as "yq". $SCHEMAS holds JSON schemas made from the Argo CD and
# Image Updater CRDs with crd2schema.py (files named <kind>_<version>.json).
set -euo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$HERE/../../../.." && pwd)"
LAB="$ROOT/labs/hello-devops"
OUTS="$HERE/outputs"
SCRATCH="${SCRATCH:?set SCRATCH to a scratch directory}"
SCHEMAS="${SCHEMAS:-$SCRATCH/p8schemas}"
mkdir -p "$OUTS"

# ---- 1. Validate the lab files this part owns ----
echo "== kubeconform (argocd/, gitops/smoke-test.yaml)"
kubeconform -strict -summary \
  -schema-location default \
  -schema-location "$SCHEMAS/{{.ResourceKind}}_{{.ResourceAPIVersion}}.json" \
  "$LAB"/argocd/*.yaml "$LAB/gitops/smoke-test.yaml"
echo "== actionlint (gitops/bump-image.yml)"
actionlint "$LAB/gitops/bump-image.yml" && echo "actionlint: no errors"

# The overlays belong to the Kustomize lesson (Day 37). Render and check them.
for env in dev prod; do
  echo "== render overlays/$env"
  kubectl kustomize "$LAB/overlays/$env" | kubeconform -strict -summary -
done

# ---- 2. Real output for the worked example ----
# Work on a throw-away git copy of the lab, never on the lab itself.
WORK="$SCRATCH/p8-worked-$(date +%s)"
mkdir -p "$WORK"
cp -R "$LAB/k8s" "$LAB/overlays" "$WORK/"
cd "$WORK"
git init -q -b main
git add -A
git -c user.name=you -c user.email=you@example.com commit -qm "start"

{
  for env in dev prod; do
    echo "\$ kubectl kustomize overlays/$env | grep 'image:'"
    kubectl kustomize "overlays/$env" | grep 'image:'
  done
} > "$OUTS/01-images-before.txt"

{
  echo "\$ cd overlays/prod"
  echo "\$ kustomize edit set image hello-devops:1.1.0"
  (cd overlays/prod && kustomize edit set image hello-devops:1.1.0)
  echo "\$ cd ../.."
  echo "\$ git diff --stat"
  git diff --stat
  echo "\$ git checkout -- ."
  git checkout -- .
} > "$OUTS/02-kustomize-edit.txt"

{
  echo "\$ yq -i '(.images[] | select(.name == \"hello-devops\")).newTag = \"1.1.0\"' \\"
  echo "    overlays/prod/kustomization.yaml"
  yq -i '(.images[] | select(.name == "hello-devops")).newTag = "1.1.0"' overlays/prod/kustomization.yaml
  echo "\$ git diff -U1"
  git diff -U1
} > "$OUTS/03-yq-edit.txt"

{
  echo "\$ kubectl kustomize overlays/prod | grep 'image:'"
  kubectl kustomize overlays/prod | grep 'image:'
} > "$OUTS/04-images-after.txt"

echo "== captured"
for f in "$OUTS"/*.txt; do echo "--- $f"; cat "$f"; done
