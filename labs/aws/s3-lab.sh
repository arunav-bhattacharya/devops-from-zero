#!/usr/bin/env bash
# s3-lab.sh: Day 13's S3 steps in one go. It creates a private, versioned
# bucket, uploads a small report, shares it for 5 minutes and adds a
# lifecycle rule. Cost: a fraction of a cent. Delete it all with ./cleanup.sh.
# Usage: ./s3-lab.sh
set -euo pipefail
cd "$(dirname "$0")"
source ./env.sh || exit 1

step "1. Create the bucket $LAB_BUCKET in $AWS_REGION"
if aws s3api head-bucket --bucket "$LAB_BUCKET" >/dev/null 2>&1; then
  echo "it already exists"
else
  aws s3 mb "s3://$LAB_BUCKET"
fi
aws s3api put-bucket-tagging --bucket "$LAB_BUCKET" --tagging "TagSet=[{Key=Project,Value=$PROJECT}]"

step "2. Block all public access (new buckets do this already; now it is written down)"
aws s3api put-public-access-block --bucket "$LAB_BUCKET" \
  --public-access-block-configuration BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true
aws s3api get-public-access-block --bucket "$LAB_BUCKET" --query PublicAccessBlockConfiguration --output table

step "3. Turn on versioning, so an overwrite or a delete can be undone"
aws s3api put-bucket-versioning --bucket "$LAB_BUCKET" --versioning-configuration Status=Enabled
aws s3api get-bucket-versioning --bucket "$LAB_BUCKET" --query Status --output text

step "4. Upload a small report, then list the bucket"
# "-" means: read the file's content from standard input (Day 5).
printf 'date,orders,failed\n2026-11-06,1520,12\n' | aws s3 cp - "s3://$LAB_BUCKET/reports/2026-11-06.csv"
aws s3 ls "s3://$LAB_BUCKET" --recursive --human-readable

step "5. Share the report for 5 minutes with a presigned URL"
aws s3 presign "s3://$LAB_BUCKET/reports/2026-11-06.csv" --expires-in 300

step "6. Add a lifecycle rule: delete reports after 30 days, old versions after 7"
aws s3api put-bucket-lifecycle-configuration --bucket "$LAB_BUCKET" --lifecycle-configuration file://s3/lifecycle.json
aws s3api get-bucket-lifecycle-configuration --bucket "$LAB_BUCKET" \
  --query 'Rules[].{id:ID,prefix:Filter.Prefix,days:Expiration.Days,oldVersionDays:NoncurrentVersionExpiration.NoncurrentDays}' --output table

echo
echo "Done. Open the URL from step 5 in a browser, then run ./cleanup.sh when you have finished."
