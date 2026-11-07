#!/usr/bin/env bash
# cleanup.sh: delete everything Days 13 and 14 created. Safe to run again:
# it skips what is already gone and keeps going if one step fails.
# Usage: ./cleanup.sh
set -uo pipefail
cd "$(dirname "$0")" || exit 1
source ./env.sh || exit 1

# Delete every version and delete marker in a bucket, then the bucket itself.
# "aws s3 rb --force" is not enough for a versioned bucket: old versions stay.
delete_bucket() {
  local bucket="$1" left
  if ! aws s3api head-bucket --bucket "$bucket" >/dev/null 2>&1; then
    echo "bucket $bucket: already gone"
    return 0
  fi
  while :; do
    left=$(aws s3api list-object-versions --bucket "$bucket" \
      --query 'length([Versions, DeleteMarkers][][])' --output text)
    [ "$left" = "0" ] && break
    echo "bucket $bucket: deleting $left object versions"
    aws s3api delete-objects --bucket "$bucket" --query 'length(Deleted)' --output text --delete "$(
      aws s3api list-object-versions --bucket "$bucket" --max-items 1000 --output json \
        --query '{Objects: [Versions, DeleteMarkers][][].{Key: Key, VersionId: VersionId}}'
    )" >/dev/null || return 1
  done
  aws s3 rb "s3://$bucket"
}

delete_role() {
  local role="$1" arn name
  if ! aws iam get-role --role-name "$role" >/dev/null 2>&1; then
    echo "role $role: already gone"
    return 0
  fi
  for arn in $(aws iam list-attached-role-policies --role-name "$role" --query 'AttachedPolicies[].PolicyArn' --output text); do
    aws iam detach-role-policy --role-name "$role" --policy-arn "$arn"
  done
  for name in $(aws iam list-role-policies --role-name "$role" --query 'PolicyNames' --output text); do
    aws iam delete-role-policy --role-name "$role" --policy-name "$name"
  done
  aws iam delete-role --role-name "$role" && echo "role $role: deleted"
}

step "1. Terminate every server tagged Project=$PROJECT (terminate deletes the disk too; stop keeps billing for it)"
ids=$(aws ec2 describe-instances \
  --filters "Name=tag:Project,Values=$PROJECT" "Name=instance-state-name,Values=pending,running,stopping,stopped" \
  --query 'Reservations[].Instances[].InstanceId' --output text)
# shellcheck disable=SC2086 # $ids may hold several IDs, so it is split on purpose
if [ -n "$ids" ]; then
  aws ec2 terminate-instances --instance-ids $ids --query 'TerminatingInstances[].[InstanceId,CurrentState.Name]' --output text
  echo "waiting until terminated (about a minute)"
  aws ec2 wait instance-terminated --instance-ids $ids
else
  echo "no servers with that tag"
fi

step "2. The CPU alarm, the SNS topic and the log group"
if [ "$(aws cloudwatch describe-alarms --alarm-names hello-devops-cpu-high --query 'length(MetricAlarms)' --output text)" != "0" ]; then
  aws cloudwatch delete-alarms --alarm-names hello-devops-cpu-high && echo "alarm: deleted"
else
  echo "alarm: already gone"
fi
topic=$(aws sns list-topics --query "Topics[?ends_with(TopicArn, ':hello-devops-alerts')].TopicArn" --output text)
if [ -n "$topic" ]; then aws sns delete-topic --topic-arn "$topic" && echo "topic: deleted"; else echo "topic: already gone"; fi
if aws logs delete-log-group --log-group-name /hello-devops/app 2>/dev/null; then echo "log group: deleted"; else echo "log group: already gone"; fi

step "3. The security group (it can only go once no server uses it)"
sg=$(aws ec2 describe-security-groups --filters Name=group-name,Values=hello-devops-web --query 'SecurityGroups[0].GroupId' --output text)
if [ "$sg" != "None" ] && [ -n "$sg" ]; then
  for _ in 1 2 3 4 5 6; do
    if aws ec2 delete-security-group --group-id "$sg" 2>/dev/null; then echo "security group $sg: deleted"; break; fi
    echo "security group still in use; waiting 10 seconds"
    sleep 10
  done
else
  echo "security group: already gone"
fi

step "4. The instance profile and the IAM roles"
if aws iam get-instance-profile --instance-profile-name hello-devops-server >/dev/null 2>&1; then
  aws iam remove-role-from-instance-profile --instance-profile-name hello-devops-server --role-name hello-devops-server 2>/dev/null
  aws iam delete-instance-profile --instance-profile-name hello-devops-server && echo "instance profile: deleted"
else
  echo "instance profile: already gone"
fi
delete_role hello-devops-server
delete_role hello-devops-reports-reader

step "5. The buckets, with every old version inside them"
delete_bucket "$LAB_BUCKET"
delete_bucket "$APP_BUCKET"

step "6. Anything left that could still cost money?"
echo "servers tagged Project=$PROJECT, not terminated: $(aws ec2 describe-instances --filters "Name=tag:Project,Values=$PROJECT" \
  "Name=instance-state-name,Values=pending,running,stopping,stopped" --query 'length(Reservations[].Instances[])' --output text)"
echo "Elastic IPs in $AWS_REGION: $(aws ec2 describe-addresses --query 'length(Addresses)' --output text)"
echo "unattached disks in $AWS_REGION: $(aws ec2 describe-volumes --filters Name=status,Values=available --query 'length(Volumes)' --output text)"
echo "hello-devops buckets: $(aws s3api list-buckets --query "length(Buckets[?starts_with(Name, 'hello-devops-lab-') || starts_with(Name, 'hello-devops-app-')])" --output text)"
echo "All four should be 0. Check the Billing console tomorrow as well."
