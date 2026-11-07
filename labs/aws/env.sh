# env.sh: settings shared by the lab scripts (Days 13 and 14).
# The scripts load it with "source ./env.sh". Change the region here, once.
# On failure it returns 1 (it never closes your terminal if you source it by hand).
# shellcheck disable=SC2034,SC2317 # variables are used by the scripts that source it; exit runs when not sourced

export AWS_REGION="${AWS_REGION:-us-east-1}"
export AWS_PAGER="" # print results to the terminal, never open a pager

PROJECT="hello-devops" # every resource gets the tag Project=hello-devops (Days 35 and 37 use it too)

if [ -n "${AWS_ENDPOINT_URL:-}" ]; then
  echo "(using the emulator at $AWS_ENDPOINT_URL, not real AWS)"
fi

# Who am I? Stop if nobody is signed in, or if it is the root user.
if ! CALLER_ARN=$(aws sts get-caller-identity --query Arn --output text); then
  echo "The AWS CLI has no working credentials. Sign in first: aws login --profile learn" >&2
  return 1 2>/dev/null || exit 1
fi
case "$CALLER_ARN" in
  *:root)
    echo "You are signed in as the root user. Use your everyday IAM user instead (Day 13)." >&2
    return 1 2>/dev/null || exit 1
    ;;
esac
ACCOUNT_ID=$(echo "$CALLER_ARN" | cut -d: -f5)
OWNER="${CALLER_ARN##*/}" # your user name, for the owner tag (Day 16 checks it)

# Bucket names must be unique in the whole world, so they end with your account ID.
LAB_BUCKET="hello-devops-lab-$ACCOUNT_ID" # Day 13
APP_BUCKET="hello-devops-app-$ACCOUNT_ID" # Day 14

step() { printf '\n== %s\n' "$*"; }
