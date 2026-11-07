#!/usr/bin/env bash
# Verify a hello-devops release before you run it (Day 52).
#
# It looks up the digest behind a version tag once, then checks that digest three ways:
#   1. cosign: the image was signed by YOUR release workflow, for this exact tag.
#   2. gh: a SLSA build provenance attestation exists, made by the same workflow.
#   3. gh: an SBOM attestation (SPDX) exists for the same digest.
# If all three pass, it prints the digest. Deploy that digest, not the tag.
#
# Needs: docker, jq, cosign and gh (brew install jq cosign gh), and gh auth login.
# Usage:   security/verify-release.sh <github-user> <version>
# Example: security/verify-release.sh octocat 1.2.0
set -euo pipefail

if [[ $# -ne 2 ]]; then
  echo "Usage: $0 <github-user> <version>   (for example: $0 octocat 1.2.0)" >&2
  exit 2
fi
user="$1"
version="$2"

# Registry names are lower case (release.yml does the same with ${GITHUB_REPOSITORY,,}).
image="ghcr.io/$(echo "$user" | tr '[:upper:]' '[:lower:]')/hello-devops"
workflow="${user}/hello-devops/.github/workflows/release.yml"

echo "==> Looking up the digest of ${image}:${version}"
digest=$(docker buildx imagetools inspect "${image}:${version}" --format '{{json .Manifest}}' | jq -r .digest)
echo "    ${digest}"

echo "==> 1/3 Signature (cosign)"
# The identity is the workflow file AND the tag that started the run.
cosign verify "${image}@${digest}" \
  --certificate-identity "https://github.com/${workflow}@refs/tags/v${version}" \
  --certificate-oidc-issuer "https://token.actions.githubusercontent.com" \
  > /dev/null
echo "    OK: signed by ${workflow} for tag v${version}"

echo "==> 2/3 Build provenance (gh attestation)"
gh attestation verify "oci://${image}@${digest}" \
  --owner "$user" \
  --signer-workflow "$workflow" \
  > /dev/null
echo "    OK: SLSA provenance from ${workflow}"

echo "==> 3/3 SBOM attestation (gh attestation)"
gh attestation verify "oci://${image}@${digest}" \
  --owner "$user" \
  --signer-workflow "$workflow" \
  --predicate-type "https://spdx.dev/Document/v2.3" \
  > /dev/null
echo "    OK: SPDX SBOM attached"

echo
echo "All checks passed. Deploy this exact image:"
echo "${image}@${digest}"
