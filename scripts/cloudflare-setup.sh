#!/usr/bin/env bash
# Deploy the course site to Cloudflare from your Mac, then (optionally) let GitHub Actions
# redeploy it on every push to main.
#
#   bash scripts/cloudflare-setup.sh
#
# What it does:
#   1. Gets the latest course code into ~/code/devops-from-zero.
#   2. Logs you in to Cloudflare (your browser opens once) and deploys public/ as the
#      Worker "devops-from-zero". It prints the site's URL.
#   3. If you say yes: checks a Cloudflare API token you paste (it is never shown or saved
#      on disk), stores it and your account ID as GitHub secrets, and runs the deploy
#      workflow once so you can see it work.
set -euo pipefail

REPO="arunav-bhattacharya/devops-from-zero"
DIR="$HOME/code/devops-from-zero"
WRANGLER="wrangler@4.156.0" # the same version .github/workflows/deploy.yml uses

need() { command -v "$1" >/dev/null 2>&1 || { echo "Missing '$1'. Install it with: $2" >&2; exit 1; }; }
need git "xcode-select --install"
need npx "brew install node"
need gh "brew install gh"
need curl "brew install curl"

echo "==> 1. Getting the latest course code"
if [ -d "$DIR/.git" ]; then
  git -C "$DIR" pull --ff-only
else
  git clone "https://github.com/$REPO" "$DIR"
fi
cd "$DIR"

echo "==> 2. Deploying to Cloudflare"
if ! npx --yes "$WRANGLER" whoami 2>/dev/null | grep -q "associated with the email"; then
  npx --yes "$WRANGLER" login
fi
npx --yes "$WRANGLER" deploy

echo
read -r -p "Set up automatic deploys on every push to main? [y/N] " answer
case "$answer" in [Yy]*) ;; *) echo "Done. Run this script again any time to redeploy."; exit 0 ;; esac

echo "==> 3. Automatic deploys from GitHub Actions"
gh auth status >/dev/null 2>&1 || gh auth login

# The account ID is the 32-character code in `wrangler whoami`. With several accounts, check it.
ACCOUNT_ID=$(npx --yes "$WRANGLER" whoami 2>/dev/null | grep -oE '[0-9a-f]{32}' | head -1 || true)
echo "Cloudflare account ID found: ${ACCOUNT_ID:-none}"
read -r -p "Press Enter to use it, or paste a different account ID: " other
ACCOUNT_ID="${other:-$ACCOUNT_ID}"
[[ "$ACCOUNT_ID" =~ ^[0-9a-f]{32}$ ]] || { echo "That does not look like an account ID (32 characters, 0-9 and a-f)." >&2; exit 1; }

cat <<'STEPS'

Now create an API token for GitHub Actions. Your browser opens the API tokens page:
  1. Click "Create Token".
  2. Next to "Edit Cloudflare Workers", click "Use template".
  3. Under "Account Resources", pick your account. Under "Zone Resources", pick "All zones".
  4. Click "Continue to summary", then "Create Token", and copy the token.
STEPS
open "https://dash.cloudflare.com/profile/api-tokens" 2>/dev/null || echo "Open https://dash.cloudflare.com/profile/api-tokens"
read -r -s -p "Paste the token here (it will not show on screen): " TOKEN
echo

# Ask Cloudflare whether the token is real and active before storing it.
if ! curl -fsS -H "Authorization: Bearer $TOKEN" "https://api.cloudflare.com/client/v4/user/tokens/verify" | grep -q '"status":"active"'; then
  unset TOKEN
  echo "Cloudflare did not accept that token. Create it again and rerun this script." >&2
  exit 1
fi

printf '%s' "$TOKEN" | gh secret set CLOUDFLARE_API_TOKEN --repo "$REPO"
printf '%s' "$ACCOUNT_ID" | gh secret set CLOUDFLARE_ACCOUNT_ID --repo "$REPO"
unset TOKEN
echo "Stored CLOUDFLARE_API_TOKEN and CLOUDFLARE_ACCOUNT_ID as secrets in $REPO."

echo "==> Running the deploy workflow once"
gh workflow run deploy.yml --repo "$REPO" --ref main
sleep 8
RUN_ID=$(gh run list --repo "$REPO" --workflow deploy.yml --limit 1 --json databaseId -q '.[0].databaseId')
gh run watch "$RUN_ID" --repo "$REPO" --exit-status
echo "Done. Every push to main now redeploys the site."
