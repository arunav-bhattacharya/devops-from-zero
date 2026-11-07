# labs/aws: hands-on AWS for Days 13 and 14

Scripts and policy files for the two hands-on AWS lessons. Day 13 opens an account,
signs in to the AWS CLI with short-lived credentials and works with S3 and IAM.
Day 14 launches one small Ubuntu server that installs hello-devops by itself and
runs it as a systemd service, then watches it with CloudWatch.

Everything here is built to cost nothing or a few cents, and `cleanup.sh` deletes
all of it. You can also do every script without an AWS account, against a local
emulator (see "No account: the emulator path" below).

## Get the folder onto your Mac

```bash
git clone --depth 1 https://github.com/arunav-bhattacharya/devops-from-zero ~/code/devops-from-zero
cp -R ~/code/devops-from-zero/labs/aws ~/code/aws-lab
cd ~/code/aws-lab
```

You need the AWS CLI v2 (`brew install awscli`, then `aws --version` shows `aws-cli/2.x`).
Day 14 also needs the Session Manager plugin: `brew install --cask session-manager-plugin`.

## What is in the folder

| Path | What it is | Day |
|---|---|---|
| `env.sh` | Settings every script loads: region (default `us-east-1`), bucket names, and a check that you are signed in and not as root | 13, 14 |
| `s3-lab.sh` | Creates a private, versioned bucket, uploads a report, prints a presigned URL, adds a lifecycle rule | 13 |
| `s3/lifecycle.json` | The lifecycle rule: delete `reports/` after 30 days and old versions after 7 | 13 |
| `policies/reports-reader-trust.json` | Trust policy: who may assume the reports-reader role (people in your account) | 13 |
| `policies/reports-reader-permissions.json` | Permissions: list and read `reports/` in the lab bucket, nothing else | 13 |
| `server-up.sh` | Uploads the app, creates the role, instance profile and security group, launches the server | 14 |
| `server/user-data.sh` | Runs once at first boot: installs Python, the AWS CLI, the app and the CloudWatch agent | 14 |
| `server/hello-devops.service` | The systemd unit that runs gunicorn as the `hello` user | 14 |
| `server/cloudwatch-agent.json` | Sends the `hello-devops` unit's journal to the log group `/hello-devops/app` | 14 |
| `policies/ec2-trust.json` | Trust policy: the EC2 service may assume the server role | 14 |
| `policies/hello-server-permissions.json` | Permissions: read `app/` in the app bucket, nothing else | 14 |
| `alarm.sh` | An SNS topic with your email and a CPU alarm on the server | 14 |
| `cleanup.sh` | Deletes everything from both days, then counts what could still cost money | 13, 14 |

The policy files contain the word `ACCOUNT_ID`. The scripts replace it with your
12-digit account ID. When you use a file by hand, do the same:

```bash
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
sed "s/ACCOUNT_ID/$ACCOUNT_ID/g" policies/reports-reader-trust.json
```

## Why Ubuntu 24.04 on the server

The server runs Ubuntu Server 24.04 LTS for ARM (Graviton), found through Canonical's
public SSM parameter, so the scripts never hard-code an AMI ID. It is the same system
as the `ubuntu:24.04` practice container from Part 1, so `apt`, the `ubuntu` user and
`systemctl` work as you already know them, and its Python 3.12 is new enough for
gunicorn 26 (which needs Python 3.10 or later).

Amazon Linux 2023, AWS's own distribution, is a good choice too. The catch for this
app: its `/usr/bin/python3` stays Python 3.9 for the life of the release, so you would
add a newer one with `dnf install python3.12` and build the virtual environment from it.

## What it costs (us-east-1, checked November 2026)

| Item | Price | For a 2-hour Day 14 |
|---|---|---|
| t4g.micro instance | $0.0084 an hour | about 1.7 cents |
| Public IPv4 address | $0.005 an hour | 1 cent |
| 8 GB gp3 disk | $0.08 per GB-month | well under 1 cent |
| S3, a few kilobytes | per GB-month and per request | well under 1 cent |
| CPU alarm, logs | within the CloudWatch free tier (10 alarms, 5 GB of logs) | 0 |
| Session Manager | no extra charge on EC2 | 0 |

On the AWS Free plan these come out of your credits and your card is never charged.
The server launches in CPU credit "standard" mode, so it slows down instead of
billing extra if it runs out of CPU credits. Prices change: check the EC2, S3 and
CloudWatch pricing pages for your region.

What would cost real money if you forgot it: a running or stopped instance (the disk
still bills), an Elastic IP, a NAT gateway or a load balancer. None of these scripts
create the last three, and `cleanup.sh` checks for leftovers.

## No account: the emulator path

[moto](https://moto.readthedocs.io/en/latest/docs/server_mode.html) is a free, open
source program that pretends to be AWS on your laptop. The AWS CLI talks to it when
you point it there with `--endpoint-url` (one command) or the `AWS_ENDPOINT_URL`
environment variable (every command in this terminal).

```bash
# Install moto in its own virtual environment (Homebrew's Python refuses global pip installs).
python3 -m venv ~/.venvs/moto
~/.venvs/moto/bin/pip install "moto[server]"

# Start it on port 5050 and leave this tab open. (macOS uses port 5000 for AirPlay.)
~/.venvs/moto/bin/moto_server -p 5050
```

In a second terminal tab:

```bash
cd ~/code/aws-lab
export AWS_ENDPOINT_URL=http://localhost:5050
export AWS_ACCESS_KEY_ID=testing AWS_SECRET_ACCESS_KEY=testing AWS_REGION=us-east-1
aws sts get-caller-identity          # account 123456789012, user "moto"

./s3-lab.sh
# moto has no Canonical parameters, so give it one of its own images:
export AMI_ID=$(aws ssm get-parameter --name /aws/service/ami-amazon-linux-latest/al2023-ami-kernel-default-arm64 \
  --query Parameter.Value --output text)
./server-up.sh
./alarm.sh you@example.com
./cleanup.sh
```

One command at a time works too: `aws s3 ls --endpoint-url http://localhost:5050`.

When you are done, close that tab or run
`unset AWS_ENDPOINT_URL AWS_ACCESS_KEY_ID AWS_SECRET_ACCESS_KEY`.
Left set, the fake keys win over your real `AWS_PROFILE`, and every real call fails.
moto keeps everything in memory, so stopping it deletes all its "resources".

### What the emulator cannot teach

All of the scripts above were run against moto 5.2.5 with the AWS CLI 2.39.6. Where
moto behaves differently from AWS, the lessons say so. The differences we saw:

- **IAM is not checked.** Every call is allowed, so you never see `AccessDenied`. The
  policy simulator (`aws iam simulate-custom-policy`) and IAM Access Analyzer
  (`aws accessanalyzer validate-policy`) do not work in moto at all.
- **New buckets have no Block Public Access setting** until you set one. Real S3 turns
  all four settings on for every new bucket.
- **Presigned URLs never expire** in moto. Real S3 refuses an expired one with 403.
- **Version IDs look like UUIDs.** Real S3 version IDs are longer random strings.
- **The default VPC has no internet gateway** and no `0.0.0.0/0` route. Real default VPCs do.
- **No server boots.** An instance is "running" at once, user data never runs, there is
  no Session Manager, no metrics and no logs. Canonical's Ubuntu parameter is missing.
- **Security groups delete too easily.** Real EC2 refuses to delete a group that a
  server still uses (`DependencyViolation`); moto allows it.
- **Alarms start as `OK`** (real ones start as `INSUFFICIENT_DATA`), and an email
  subscription is active at once (real SNS waits for you to click the confirmation link).

Nothing costs money there either, so an emulator cannot teach you to read a bill.
It is good for learning the commands, their flags and their JSON, and for testing
scripts (Day 16 uses moto inside Python tests).

LocalStack is a bigger AWS emulator. Since March 23, 2026 its Docker image needs a
LocalStack account and an auth token; a free Hobby plan covers non-commercial use.
moto needs no account, so these lessons use it.

## How the server setup was tested

- `server/user-data.sh` ran in an `ubuntu:24.04` container (x86_64) with moto standing
  in for S3: apt, the AWS CLI v2 zip, the app download, the virtual environment
  (Python 3.12.3, Flask 3.1.3, gunicorn 26.2.0) and the CloudWatch agent package
  (1.300074.1) all installed.
- systemd cannot run as PID 1 in that container, so `systemctl` was a stub there.
  `systemd-analyze verify` passed for `hello-devops.service`, and its `ExecStart`, run by
  hand as the `hello` user, answered on port 8000 with
  `{"message":"Hello from EC2","version":"1.0.0",...}`.
- The agent's own translator accepted `cloudwatch-agent.json` and built a journald
  pipeline for the `hello-devops` unit.
- Not tested here: a real EC2 boot, Session Manager, real metrics, the alarm email and
  the agent sending logs. Those need an AWS account.
