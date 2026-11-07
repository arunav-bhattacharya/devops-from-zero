#!/usr/bin/env bash
# server-up.sh: Day 14. Launch one small Ubuntu server that runs hello-devops.
# It creates, all tagged Project=hello-devops:
#   - an S3 bucket with the app files (app.py, requirements.txt, the unit file)
#   - an IAM role and instance profile, so the server needs no keys
#   - a security group with no inbound rules
#   - one t4g.micro instance (ARM, Graviton) with a public IPv4 address
# Cost while it runs: about 1.5 US cents an hour in us-east-1 (README).
# Delete everything with ./cleanup.sh.
# Usage: ./server-up.sh    (APP_DIR defaults to ~/code/hello-devops)
set -euo pipefail
cd "$(dirname "$0")"
source ./env.sh || exit 1

APP_DIR="${APP_DIR:-$HOME/code/hello-devops}"
INSTANCE_TYPE="${INSTANCE_TYPE:-t4g.micro}"
ROLE=hello-devops-server
SG_NAME=hello-devops-web
AMI_PARAM=/aws/service/canonical/ubuntu/server/24.04/stable/current/arm64/hvm/ebs-gp3/ami-id

running=$(aws ec2 describe-instances \
  --filters "Name=tag:Project,Values=$PROJECT" "Name=tag:Name,Values=hello-devops" "Name=instance-state-name,Values=pending,running,stopping,stopped" \
  --query 'Reservations[].Instances[].InstanceId' --output text)
if [ -n "$running" ]; then
  echo "A lab server already exists: $running. Run ./cleanup.sh first if you want a new one."
  exit 0
fi

step "1. Upload the app files to s3://$APP_BUCKET/app/"
[ -f "$APP_DIR/app.py" ] || { echo "No app.py in $APP_DIR. Set APP_DIR to your hello-devops folder." >&2; exit 1; }
if ! aws s3api head-bucket --bucket "$APP_BUCKET" >/dev/null 2>&1; then
  aws s3 mb "s3://$APP_BUCKET"
fi
aws s3api put-public-access-block --bucket "$APP_BUCKET" \
  --public-access-block-configuration BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true
aws s3api put-bucket-tagging --bucket "$APP_BUCKET" --tagging "TagSet=[{Key=Project,Value=$PROJECT}]"
for f in "$APP_DIR/app.py" "$APP_DIR/requirements.txt" server/hello-devops.service server/cloudwatch-agent.json; do
  aws s3 cp "$f" "s3://$APP_BUCKET/app/" --no-progress
done

step "2. An IAM role for the server, so no keys ever live on it"
if ! aws iam get-role --role-name "$ROLE" >/dev/null 2>&1; then
  aws iam create-role --role-name "$ROLE" --assume-role-policy-document file://policies/ec2-trust.json \
    --tags "Key=Project,Value=$PROJECT" --query Role.Arn --output text
fi
# Two AWS managed policies: Session Manager, and the CloudWatch agent.
aws iam attach-role-policy --role-name "$ROLE" --policy-arn arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore
aws iam attach-role-policy --role-name "$ROLE" --policy-arn arn:aws:iam::aws:policy/CloudWatchAgentServerPolicy
# Our own small policy: read the app/ folder of one bucket, nothing else.
aws iam put-role-policy --role-name "$ROLE" --policy-name read-app-files \
  --policy-document "$(sed "s/ACCOUNT_ID/$ACCOUNT_ID/g" policies/hello-server-permissions.json)"
# EC2 attaches a role through an instance profile, a small wrapper around it.
if ! aws iam get-instance-profile --instance-profile-name "$ROLE" >/dev/null 2>&1; then
  aws iam create-instance-profile --instance-profile-name "$ROLE" --tags "Key=Project,Value=$PROJECT" \
    --query InstanceProfile.Arn --output text
  aws iam add-role-to-instance-profile --instance-profile-name "$ROLE" --role-name "$ROLE"
fi

step "3. A security group in the default VPC, with no inbound rules at all"
VPC_ID=$(aws ec2 describe-vpcs --filters Name=is-default,Values=true --query 'Vpcs[0].VpcId' --output text)
[ "$VPC_ID" != "None" ] || { echo "This region has no default VPC. See the README." >&2; exit 1; }
SG_ID=$(aws ec2 describe-security-groups --filters "Name=group-name,Values=$SG_NAME" "Name=vpc-id,Values=$VPC_ID" \
  --query 'SecurityGroups[0].GroupId' --output text)
if [ "$SG_ID" = "None" ]; then
  SG_ID=$(aws ec2 create-security-group --group-name "$SG_NAME" --vpc-id "$VPC_ID" \
    --description "hello-devops lab server (Day 14)" \
    --tag-specifications "ResourceType=security-group,Tags=[{Key=Project,Value=$PROJECT}]" \
    --query GroupId --output text)
fi
echo "$SG_ID in $VPC_ID"
# Not every availability zone offers every instance type, so pick one that does.
AZ=$(aws ec2 describe-instance-type-offerings --location-type availability-zone \
  --filters "Name=instance-type,Values=$INSTANCE_TYPE" --query 'sort(InstanceTypeOfferings[].Location)[0]' --output text)
SUBNET_ID=$(aws ec2 describe-subnets --filters "Name=vpc-id,Values=$VPC_ID" "Name=availability-zone,Values=$AZ" \
  "Name=default-for-az,Values=true" --query 'Subnets[0].SubnetId' --output text)
echo "$INSTANCE_TYPE in $AZ, public subnet $SUBNET_ID"

step "4. The newest Ubuntu 24.04 image for ARM, from Canonical's public parameter"
AMI_ID="${AMI_ID:-$(aws ssm get-parameter --name "$AMI_PARAM" --query Parameter.Value --output text)}"
echo "$AMI_ID"

step "5. Fill in user-data.sh with the bucket and the region"
user_data=$(mktemp)
sed -e "s/__BUCKET__/$APP_BUCKET/" -e "s/__REGION__/$AWS_REGION/" server/user-data.sh >"$user_data"

launch() {
  aws ec2 run-instances "$@" --image-id "$AMI_ID" --instance-type "$INSTANCE_TYPE" \
    --subnet-id "$SUBNET_ID" --security-group-ids "$SG_ID" --iam-instance-profile "Name=$ROLE" \
    --user-data "file://$user_data" \
    --credit-specification CpuCredits=standard \
    --metadata-options HttpTokens=required \
    --tag-specifications "ResourceType=instance,Tags=[{Key=Name,Value=hello-devops},{Key=Project,Value=$PROJECT},{Key=Role,Value=web},{Key=owner,Value=$OWNER}]" \
    --query 'Instances[0].InstanceId' --output text
}

# A new role takes a few seconds to reach EC2. Until then EC2 calls the
# instance profile invalid, so wait and try again.
launch_with_retry() {
  local out attempt
  for attempt in 1 2 3 4 5 6 7 8; do
    if out=$(launch "$@" 2>&1); then
      echo "$out"
      return 0
    fi
    if echo "$out" | grep -q DryRunOperation; then
      echo "dry run: the request would succeed" >&2
      return 0
    fi
    if echo "$out" | grep -qi "instance profile" && [ "$attempt" -lt 8 ]; then
      echo "the new role has not reached EC2 yet; waiting 10 seconds" >&2
      sleep 10
    else
      echo "$out" >&2
      return 1
    fi
  done
}

step "6. Ask AWS whether the launch would work (--dry-run), then launch"
launch_with_retry --dry-run
INSTANCE_ID=$(launch_with_retry)
rm -f "$user_data"
echo "launched $INSTANCE_ID; waiting until it is running"
aws ec2 wait instance-running --instance-ids "$INSTANCE_ID"
aws ec2 describe-instances --instance-ids "$INSTANCE_ID" \
  --query 'Reservations[0].Instances[0].{id:InstanceId,type:InstanceType,az:Placement.AvailabilityZone,publicIp:PublicIpAddress,privateIp:PrivateIpAddress}' \
  --output table

cat <<EOF

The server is booting and user-data.sh is installing the app (2 to 4 minutes).
Next steps (Day 14):
  aws ssm start-session --target $INSTANCE_ID
  aws ssm start-session --target $INSTANCE_ID --document-name AWS-StartPortForwardingSession --parameters '{"portNumber":["8000"],"localPortNumber":["8000"]}'
When you are finished: ./cleanup.sh
EOF
