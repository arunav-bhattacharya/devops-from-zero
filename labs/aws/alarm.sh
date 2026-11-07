#!/usr/bin/env bash
# alarm.sh: Day 14. Email you when the lab server's CPU stays above 70%
# for two 5-minute periods in a row. Uses the free basic EC2 metrics.
# Usage: ./alarm.sh you@example.com
set -euo pipefail
cd "$(dirname "$0")"
EMAIL="${1:?Usage: ./alarm.sh you@example.com}"
source ./env.sh || exit 1

INSTANCE_ID=$(aws ec2 describe-instances \
  --filters "Name=tag:Project,Values=$PROJECT" "Name=tag:Name,Values=hello-devops" "Name=instance-state-name,Values=running" \
  --query 'Reservations[].Instances[0].InstanceId' --output text)
[ -n "$INSTANCE_ID" ] && [ "$INSTANCE_ID" != "None" ] || { echo "No running lab server. Run ./server-up.sh first." >&2; exit 1; }

step "1. An SNS topic: one address that alarms send messages to"
TOPIC_ARN=$(aws sns create-topic --name hello-devops-alerts --tags "Key=Project,Value=$PROJECT" \
  --query TopicArn --output text)
echo "$TOPIC_ARN"

step "2. Subscribe your email. AWS sends a confirmation email: click its link"
aws sns subscribe --topic-arn "$TOPIC_ARN" --protocol email --notification-endpoint "$EMAIL" \
  --query SubscriptionArn --output text

step "3. The alarm: average CPUUtilization above 70% for 2 periods of 5 minutes"
aws cloudwatch put-metric-alarm --alarm-name hello-devops-cpu-high \
  --alarm-description "CPU above 70% for 10 minutes on the hello-devops lab server" \
  --namespace AWS/EC2 --metric-name CPUUtilization --dimensions "Name=InstanceId,Value=$INSTANCE_ID" \
  --statistic Average --period 300 --evaluation-periods 2 --threshold 70 \
  --comparison-operator GreaterThanThreshold --treat-missing-data notBreaching \
  --alarm-actions "$TOPIC_ARN" --ok-actions "$TOPIC_ARN" --tags "Key=Project,Value=$PROJECT"
aws cloudwatch describe-alarms --alarm-names hello-devops-cpu-high \
  --query 'MetricAlarms[0].{alarm:AlarmName,state:StateValue,threshold:Threshold}' --output table

cat <<EOF

Test the email path without waiting for real load:
  aws cloudwatch set-alarm-state --alarm-name hello-devops-cpu-high --state-value ALARM --state-reason "Testing by hand"
EOF
