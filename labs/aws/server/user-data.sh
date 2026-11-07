#!/bin/bash
# user-data.sh: cloud-init runs this once, as root, when the server first boots
# (Day 14). It installs hello-devops and runs it as a systemd service.
# server-up.sh fills in the two values below before it launches the server.
# Read what happened on the server with: sudo cat /var/log/cloud-init-output.log
set -euo pipefail

BUCKET="__BUCKET__" # the bucket server-up.sh uploaded the app files to
REGION="__REGION__" # the region this server runs in

export AWS_REGION="$REGION"
export DEBIAN_FRONTEND=noninteractive # apt must never stop and ask a question
# On first boot Ubuntu may be updating itself; wait for apt's lock, do not fail.
APT="apt-get -y -q -o DPkg::Lock::Timeout=300"

echo "== 1. Packages: Python's venv module, unzip and curl"
$APT update
$APT install python3-venv unzip curl

echo "== 2. The AWS CLI v2, from the official zip (aarch64 on Graviton)"
if ! command -v aws >/dev/null; then
  curl -fsSL "https://awscli.amazonaws.com/awscli-exe-linux-$(uname -m).zip" -o /tmp/awscliv2.zip
  unzip -q /tmp/awscliv2.zip -d /tmp
  /tmp/aws/install
  rm -rf /tmp/aws /tmp/awscliv2.zip
fi

echo "== 3. A system user for the app, with no login shell"
id hello >/dev/null 2>&1 || useradd --system --home-dir /opt/hello-devops --shell /usr/sbin/nologin hello

echo "== 4. The app files from S3, read with the instance role (no keys here)"
mkdir -p /opt/hello-devops
aws s3 cp "s3://$BUCKET/app/" /opt/hello-devops/ --recursive --no-progress

echo "== 5. A virtual environment with the app's dependencies"
python3 -m venv /opt/hello-devops/venv
/opt/hello-devops/venv/bin/pip install --quiet --disable-pip-version-check -r /opt/hello-devops/requirements.txt
chown -R hello:hello /opt/hello-devops

echo "== 6. Run the app as a systemd service (Day 6)"
install -m 644 /opt/hello-devops/hello-devops.service /etc/systemd/system/hello-devops.service
systemctl daemon-reload
systemctl enable --now hello-devops

echo "== 7. The CloudWatch agent: it sends the app's journal to CloudWatch Logs"
curl -fsSL "https://amazoncloudwatch-agent.s3.amazonaws.com/ubuntu/$(dpkg --print-architecture)/latest/amazon-cloudwatch-agent.deb" -o /tmp/cwagent.deb
dpkg -i -E /tmp/cwagent.deb
rm -f /tmp/cwagent.deb
/opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-ctl \
  -a fetch-config -m ec2 -s -c file:/opt/hello-devops/cloudwatch-agent.json

echo "== Done: hello-devops listens on port 8000"
