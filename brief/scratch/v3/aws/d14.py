"""Day 14: Hands-on AWS 2: a server of your own with EC2, VPC and CloudWatch. Imported by build_p3_aws.py."""

from labfiles import lab

DIAGRAM = (
    '<svg viewBox="0 0 560 300" xmlns="http://www.w3.org/2000/svg" role="img" '
    'aria-label="Your Mac opens a session through Systems Manager, whose agent on the EC2 server dials out. '
    'The server reads its app files from S3 with its role and sends metrics and logs to CloudWatch. '
    'Its security group has no inbound rules.">'
    '<rect x="180" y="16" width="168" height="44" rx="10" class="bxp"/>'
    '<text x="264" y="43" font-size="13" text-anchor="middle" class="tk">Systems Manager</text>'
    '<rect x="8" y="120" width="104" height="52" rx="10" class="bx"/>'
    '<text x="60" y="151" font-size="13" text-anchor="middle" class="t">Your Mac</text>'
    '<rect x="180" y="120" width="168" height="52" rx="10" class="bxo"/>'
    '<text x="264" y="142" font-size="13" text-anchor="middle" class="tk">EC2: hello-devops</text>'
    '<text x="264" y="160" font-size="11" text-anchor="middle" class="tk">t4g.micro, Ubuntu</text>'
    '<rect x="416" y="72" width="136" height="44" rx="10" class="bxt"/>'
    '<text x="484" y="99" font-size="13" text-anchor="middle" class="tk">S3: app files</text>'
    '<rect x="416" y="176" width="136" height="52" rx="10" class="bxg"/>'
    '<text x="484" y="198" font-size="13" text-anchor="middle" class="tk">CloudWatch</text>'
    '<text x="484" y="216" font-size="11" text-anchor="middle" class="tk">metrics, logs</text>'
    '<rect x="180" y="236" width="168" height="44" rx="10" class="bx"/>'
    '<text x="264" y="263" font-size="13" text-anchor="middle" class="t">no inbound rules</text>'
    '<text x="360" y="262" font-size="11" text-anchor="start" class="ts">the security group</text>'
    '<line x1="112" y1="130" x2="178" y2="58" class="lnd" marker-end="url(#ar)"/>'
    '<text x="56" y="104" font-size="11" text-anchor="middle" class="ts">start-session</text>'
    '<line x1="264" y1="118" x2="264" y2="63" class="ln" marker-end="url(#ar)"/>'
    '<text x="272" y="94" font-size="11" text-anchor="start" class="ts">agent dials out</text>'
    '<line x1="114" y1="152" x2="177" y2="152" class="lnd" marker-end="url(#ar)"/>'
    '<text x="146" y="188" font-size="11" text-anchor="middle" class="ts">port 8000</text>'
    '<line x1="350" y1="134" x2="413" y2="106" class="ln" marker-end="url(#ar)"/>'
    '<line x1="350" y1="160" x2="413" y2="194" class="ln" marker-end="url(#ar)"/>'
    '<line x1="264" y1="234" x2="264" y2="175" class="lnd"/>'
    '<text x="272" y="210" font-size="11" text-anchor="start" class="ts">guards it</text>'
    '</svg>'
)

ON_SERVER = (
    "$ curl -s localhost:8000\n"
    "{\"host\":\"e32c140fc25c\",\"message\":\"Hello from EC2\",\"version\":\"1.0.0\",\"visits\":1}\n"
    "$ ps -o user,pid,cmd -C gunicorn | head -2\n"
    "USER         PID CMD\n"
    "hello         12 /opt/hello-devops/venv/bin/python3 /opt/hello-devops/venv/bin/gunicorn --bind 0.0.0.0:8000 --workers 2 --access-logfile - app:app\n"
    "$ systemd-analyze verify /etc/systemd/system/hello-devops.service; echo \"exit $?\"\n"
    "exit 0"
)

LESSON = {
    "id": "d14",
    "title": "Hands-on AWS 2: a server of your own with EC2, VPC and CloudWatch",
    "minutes": 50,
    "goal": "By the end you can launch a small Linux server from the CLI that installs and runs hello-devops by itself, reach it without opening SSH, watch it with CloudWatch, and delete every piece of it.",
    "guess": {
        "q": "You stop (not terminate) your EC2 server for the weekend. What keeps billing?",
        "options": [
            "Nothing at all, because a stopped server is free",
            "Its disk, and any Elastic IP you allocated",
            "The full hourly price, as if it were running",
            "Only the operating system's licence fee",
        ],
        "answer": 1,
        "why": "Stopping ends the compute bill, but the EBS disk bills per GB-month and an Elastic IP bills by the hour whether it is attached or not. Terminating is what ends both.",
    },
    "terms": [
        {"term": "EC2 instance", "plain": "A virtual server you rent from AWS by the second."},
        {"term": "AMI", "plain": "Amazon Machine Image: the disk image a server starts from, such as Ubuntu 24.04 for ARM."},
        {"term": "EBS volume", "plain": "A network disk attached to a server; it bills per GB-month even while the server is stopped."},
        {"term": "User data", "plain": "A script you pass at launch that cloud-init runs once, as root, on the first boot."},
        {"term": "Instance profile", "plain": "The wrapper that attaches one IAM role to an EC2 server, so software on it gets temporary credentials."},
        {"term": "Session Manager", "plain": "An AWS service that opens a shell on a server through its agent, with no open inbound port and no SSH key."},
        {"term": "Elastic IP", "plain": "A public IPv4 address you keep in your account until you release it; it bills by the hour."},
        {"term": "CloudWatch alarm", "plain": "A rule that watches one metric and changes state, and can send a message, when it crosses a threshold."},
    ],
    "sections": [
        {
            "h": "The network your server lands in",
            "body": (
                "Every region gives your account a default VPC, so you can launch a server before you design a network. It is the Day 12 picture, already built:\n\n"
                "- The VPC is `172.31.0.0/16`.\n"
                "- Each availability zone has one `/20` subnet: 4,096 addresses, minus the 5 that AWS keeps.\n"
                "- An internet gateway is attached, and the route table sends `0.0.0.0/0` to it, so every default subnet is public.\n"
                "- A server launched there gets a public IPv4 address unless you ask it not to.\n\n"
                "That is enough for one learning server. Production teams build their own VPC, with private subnets for apps and databases, as you sketched on Day 12.\n\n"
                "The firewall is a security group. It is stateful (Day 12), so replies to allowed traffic go out without a rule of their own. Its outbound rules allow everything by default, which lets the server download packages. `server-up.sh` makes a group called `hello-devops-web` with no inbound rules at all. Nobody on the internet can start a connection to the server, you included. That sounds like a problem until the next section."
            ),
            "refs": [
                {"title": "AWS networking foundations, re:Invent 2023 (AWS Events)", "url": "https://www.youtube.com/watch?v=8nNurTFy-h4", "kind": "watch"},
                {"title": "Subnet CIDR blocks (AWS VPC docs)", "url": "https://docs.aws.amazon.com/vpc/latest/userguide/subnet-sizing.html", "kind": "docs"},
            ],
        },
        {
            "h": "A shell without opening port 22",
            "body": (
                "On Day 7 you logged in to a machine with SSH, which needs port 22 open and a key. AWS gives you three ways in, and the one to use needs neither.\n\n"
                "Session Manager, part of AWS Systems Manager, works the other way round. A small program on the server, the SSM Agent, keeps an outbound HTTPS connection open to Systems Manager. When you run `aws ssm start-session --target i-...`, AWS checks your IAM permissions and joins your terminal to that connection. It needs four things:\n\n"
                "1. The SSM Agent on the server. AWS's and Canonical's Ubuntu images, and Amazon Linux 2023, come with it.\n"
                "2. An instance role with the AWS managed policy `AmazonSSMManagedInstanceCore`.\n"
                "3. Outbound HTTPS from the server to three endpoints in its region: `ssm`, `ssmmessages` and `ec2messages`. A public IP and the default outbound rule cover it.\n"
                "4. The Session Manager plugin for the CLI on your Mac: `brew install --cask session-manager-plugin`.\n\n"
                "It costs nothing extra on EC2, and there is no port to open and no key to lose. You arrive as `ssm-user`, a user the agent creates, with sudo rights. It forwards ports too: the document `AWS-StartPortForwardingSession` makes `localhost:8000` on your Mac reach port 8000 on the server.\n\n"
                "EC2 Instance Connect is the second way. It pushes a one-time SSH key for you, but port 22 must still be open, either to AWS's Instance Connect address range or through an EC2 Instance Connect Endpoint.\n\n"
                "Key pairs are the old way: AWS keeps the public key, you download a private `.pem` file once, and you open port 22. That is Day 7's SSH plus a file you must never lose or leak."
            ),
            "refs": [
                {"title": "Step 1: Complete Session Manager prerequisites (Systems Manager docs)", "url": "https://docs.aws.amazon.com/systems-manager/latest/userguide/session-manager-prerequisites.html", "kind": "docs"},
                {"title": "Install the Session Manager plugin on macOS", "url": "https://docs.aws.amazon.com/systems-manager/latest/userguide/install-plugin-macos-overview.html", "kind": "docs"},
                {"title": "Prerequisites for EC2 Instance Connect (EC2 docs)", "url": "https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ec2-instance-connect-prerequisites.html", "kind": "docs"},
            ],
        },
        {
            "h": "Choosing the machine: image, type and price",
            "body": (
                "An **AMI** (Amazon Machine Image) is the disk image a server starts from. AMI IDs differ per region and change with every update, so look them up by name instead of copying one. Canonical publishes the newest Ubuntu IDs as public parameters in Systems Manager Parameter Store, and `server-up.sh` reads `/aws/service/canonical/ubuntu/server/24.04/stable/current/arm64/hvm/ebs-gp3/ami-id`.\n\n"
                "The lab runs Ubuntu 24.04 because you know it from the Part 1 practice container. Its Python 3.12 is also new enough for gunicorn 26, which needs 3.10 or later. Amazon Linux 2023, AWS's own system, is a fine choice too. Its built-in `python3`, though, stays at 3.9 for the whole life of the release, so you would install a newer one first.\n\n"
                "The instance type sets CPU and memory. The lab uses `t4g.micro`: 2 vCPUs, 1 GiB of memory and a Graviton processor. Graviton is ARM, like your Mac's chip, which is why the image is arm64. The Free plan lists six eligible types: t3.micro, t3.small, t4g.micro, t4g.small, c7i-flex.large and m7i-flex.large.\n\n"
                "T types are burstable: they save up CPU credits while idle and spend them when busy. In the default unlimited mode, staying above the baseline over a day costs extra. The script launches in standard mode, where the server slows down instead.\n\n"
                "In us-east-1, checked today:\n\n"
                "- The instance costs $0.0084 an hour.\n"
                "- Its public IPv4 address costs $0.005 an hour, the same as an Elastic IP, used or not.\n"
                "- Its 8 GB gp3 disk costs $0.08 per GB-month, about 64 cents a month.\n\n"
                "A two-hour session comes to about 3 cents, paid from Free plan credits.\n\n"
                "Stop and terminate are different. A stopped server ends the compute bill, keeps its disk and that disk's bill, and gives back its public IP, so it gets a new one on start. Terminating deletes the server and, by default, its disk."
            ),
            "refs": [
                {"title": "Find Ubuntu images on AWS (Canonical docs)", "url": "https://ubuntu.com/server/docs/cloud-images/amazon-ec2", "kind": "docs"},
                {"title": "Track your Free Tier usage for Amazon EC2 (EC2 docs)", "url": "https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ec2-free-tier-usage.html", "kind": "docs"},
                {"title": "New AWS public IPv4 address charge (AWS News Blog)", "url": "https://aws.amazon.com/blogs/aws/new-aws-public-ipv4-address-charge-public-ip-insights", "kind": "read"},
            ],
        },
        {
            "h": "User data: a server that installs itself",
            "body": (
                "User data is a script you hand to EC2 at launch. On the first boot, a tool called cloud-init runs it once, as root. It may be up to 16 KB, and everything it prints lands in `/var/log/cloud-init-output.log` on the server, which is where you look first when something is missing.\n\n"
                "The lab's `server/user-data.sh` turns a bare Ubuntu server into a hello-devops server in seven steps:\n\n"
                "1. Install `python3-venv`, `unzip` and `curl` with apt.\n"
                "2. Install the AWS CLI v2 from AWS's official zip, unless the image already has it.\n"
                "3. Create a system user `hello` that cannot log in.\n"
                "4. Copy the app files from S3 with `aws s3 cp`, using the server's role.\n"
                "5. Make a virtual environment and `pip install` the requirements.\n"
                "6. Install `hello-devops.service`, then `systemctl enable --now` it.\n"
                "7. Install the CloudWatch agent and load its config.\n\n"
                "It is Day 7's bash with `set -euo pipefail`, so a failed step stops the script. One line handles a cloud quirk: Ubuntu may update itself during its first boot, so apt waits up to five minutes for its lock instead of failing.\n\n"
                "Why systemd, and not `nohup gunicorn &`? Day 6 already answered it. The service manager starts the app at boot, restarts it after a crash (`Restart=on-failure`), runs it as `hello` instead of root, and sends its output to the journal. The unit binds gunicorn to `0.0.0.0:8000` so outside traffic can reach it (Day 10), and leaves the security group to decide who may.\n\n"
                "Installing on every boot is slow, two to four minutes here. Teams that launch many servers bake the result into their own AMI, or ship the app as a container image (Part 5). Days 36 and 37 show Ansible, which configures servers that are already running."
            ),
            "refs": [
                {"title": "Run commands when you launch an EC2 instance with user data (EC2 docs)", "url": "https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/user-data.html", "kind": "docs"},
                {"title": "systemctl manual (freedesktop.org)", "url": "https://www.freedesktop.org/software/systemd/man/latest/systemctl.html", "kind": "docs"},
            ],
        },
        {
            "h": "A role on the server instead of keys",
            "body": (
                "The server reads S3 and writes to CloudWatch, so it needs credentials. Copying your access key onto it would put a long-lived key on a machine the internet can reach. A role does the job without one.\n\n"
                "EC2 attaches a role through an instance profile, a wrapper that holds exactly one role. Software on the server asks the instance metadata service (IMDS), a local address at `169.254.169.254`, for the role's temporary credentials, and the AWS CLI does that by itself. They rotate automatically, and you never manage a file of keys.\n\n"
                "`server-up.sh` launches with `HttpTokens=required`, which means IMDSv2 only: a program must first fetch a session token with a PUT request before IMDS answers anything. A web app that an attacker tricks into fetching a URL has a much harder time stealing the credentials that way.\n\n"
                "The role `hello-devops-server` carries three policies:\n\n"
                "- `AmazonSSMManagedInstanceCore`, AWS's managed policy for Session Manager.\n"
                "- `CloudWatchAgentServerPolicy`, AWS's managed policy for the agent.\n"
                "- `read-app-files`, our own: list and read `app/` in one bucket, and nothing else.\n\n"
                "A new role takes a few seconds to reach EC2. Launch too soon and EC2 calls the instance profile invalid, so the script waits and retries."
            ),
            "refs": [
                {"title": "IAM roles for Amazon EC2 (EC2 docs)", "url": "https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/iam-roles-for-amazon-ec2.html", "kind": "docs"},
                {"title": "IMDSv2 on Amazon Linux 2023 (AL2023 docs)", "url": "https://docs.aws.amazon.com/linux/al2023/ug/imdsv2.html", "kind": "docs"},
            ],
        },
        {
            "h": "CloudWatch: metrics, an alarm and the app's logs",
            "body": (
                "CloudWatch is AWS's monitoring service, and an EC2 server reports to it from its first minute. Basic monitoring is on and free: CPU, network and disk activity every 5 minutes, plus status checks. Memory and free disk space are missing, because AWS cannot see inside your operating system; the CloudWatch agent can add them.\n\n"
                "An alarm watches one metric and is in one of three states: OK, ALARM, or INSUFFICIENT_DATA, which is where a new alarm starts. The script `alarm.sh` makes one that goes to ALARM when the average CPU stays above 70% for two 5-minute periods in a row. On every change of state it sends a message to an SNS topic, a named mailbox that delivers to your email. SNS first sends a confirmation email, and nothing arrives until you click its link. To test the chain without loading the server, `aws cloudwatch set-alarm-state` flips the alarm to ALARM by hand. The first 10 alarms are in the free tier.\n\n"
                "For logs you have two choices:\n\n"
                "- The simple one: open a session and run `journalctl -u hello-devops -f`. For one server you check now and then, that is enough.\n"
                "- The CloudWatch agent: it reads the journal and sends the `hello-devops` unit's lines to the log group `/hello-devops/app`, one stream per server. The agent learned to read journald in 2026; before that, people installed rsyslog to write log files for it.\n\n"
                "The agent earns its place when servers come and go. Logs outlive a terminated server, and `aws logs tail /hello-devops/app --follow` shows every server at once. The free tier covers 5 GB of logs a month, far more than this lab writes. Parts 12 to 14 go much further with Prometheus, Grafana and the Elastic stack."
            ),
            "refs": [
                {"title": "Amazon CloudWatch agent adds support for journald logs (AWS What's New)", "url": "https://aws.amazon.com/about-aws/whats-new/2026/08/amazon-cloudwatch-agent-journald/", "kind": "read"},
                {"title": "Amazon CloudWatch pricing", "url": "https://aws.amazon.com/cloudwatch/pricing/", "kind": "docs"},
                {"title": "Get actionable insights from Amazon CloudWatch Logs, re:Invent 2023 (AWS Events)", "url": "https://www.youtube.com/watch?v=aB5mGbiV_Kk", "kind": "watch"},
            ],
        },
        {
            "h": "One script for the launch, then a console tour",
            "body": (
                "The script `server-up.sh` prints a heading for each of its six steps:\n\n"
                "1. Upload the app files to S3.\n"
                "2. Create the role and the instance profile.\n"
                "3. Create the security group.\n"
                "4. Look up the AMI.\n"
                "5. Fill in user data.\n"
                "6. Launch.\n\n"
                "The launch first runs with `--dry-run`. Only when AWS answers DryRunOperation does the script launch for real and wait until the server runs. Every piece carries the tag `Project=hello-devops`, the same tag Day 35's Terraform and Day 37's Ansible inventory use, and `cleanup.sh` uses it to find the server. The server also gets `Role=web` and an `owner` tag with your user name.\n\n"
                "Then look at the same things in the console, in the same region:\n\n"
                "1. EC2, then Instances: the state, the public IP, and the Connect button, whose Session Manager tab opens a shell in the browser.\n"
                "2. EC2, then Security Groups: the inbound rules of `hello-devops-web`, empty until you add one.\n"
                "3. CloudWatch: Alarms, then Log groups.\n"
                "4. Billing and Cost Management, then Bills, the next day, to see the cents by service.\n\n"
                "From here, Day 35 moves AWS work into Terraform, where one destroy removes it all. Days 36 and 37 configure servers like this one with Ansible, and Part 10 meets EKS, AWS's managed Kubernetes."
            ),
            "refs": [
                {"title": "Connect to your Amazon EC2 instance using Session Manager (EC2 docs)", "url": "https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/session-manager.html", "kind": "docs"},
            ],
        },
    ],
    "analogy": (
        "Launching a server is like booking a serviced flat in a city you never visit. The note you leave for the caretaker (user data) says what to set up before you arrive. "
        "The front desk (Session Manager) can put you through to the flat's phone, so you never need a door key (port 22). The doorman (the security group) turns away anyone not on his list. "
        "The bill is where flats and servers part ways. A flat charges by the month, while this one charges by the second, and switching off the lights (stop) still leaves you paying for the room. Only checking out (terminate) gives it back."
    ),
    "diagram": DIAGRAM,
    "diagram_caption": "You reach the server through Systems Manager, whose agent dials out; the server reads S3 with its role and reports to CloudWatch, behind a security group with no inbound rules.",
    "worked": {
        "title": "Launch the lab server step by step, on the emulator",
        "steps": [
            {
                "say": "Read the default VPC first. moto's layout matches AWS: one `172.31.0.0/16` VPC and one public `/20` subnet per availability zone (us-east-1 has six). One difference: on AWS, `describe-route-tables` also shows `0.0.0.0/0` going to an `igw-...`, and moto has no internet gateway.",
                "code": (
                    "$ VPC_ID=$(aws ec2 describe-vpcs --filters Name=is-default,Values=true --query 'Vpcs[0].VpcId' --output text)\n"
                    "$ aws ec2 describe-vpcs --vpc-ids $VPC_ID --query 'Vpcs[0].[VpcId,CidrBlock,IsDefault]' --output text\n"
                    "vpc-f337be3037a70b614\t172.31.0.0/16\tTrue\n"
                    "$ aws ec2 describe-subnets --filters Name=vpc-id,Values=$VPC_ID --query 'sort_by(Subnets,&AvailabilityZone)[].[AvailabilityZone,CidrBlock,MapPublicIpOnLaunch]' --output text\n"
                    "us-east-1a\t172.31.0.0/20\tTrue\nus-east-1b\t172.31.16.0/20\tTrue\nus-east-1c\t172.31.32.0/20\tTrue\n"
                    "us-east-1d\t172.31.48.0/20\tTrue\nus-east-1e\t172.31.64.0/20\tTrue\nus-east-1f\t172.31.80.0/20\tTrue"
                ),
                "lang": "console",
            },
            {
                "say": "Make the security group and look at its rules. Inbound is an empty list, so nothing can connect in; outbound allows everything, so the server can download what user data asks for.",
                "code": (
                    "$ SG_ID=$(aws ec2 create-security-group --group-name hello-devops-web --description 'hello-devops lab server (Day 14)' --vpc-id $VPC_ID --query GroupId --output text)\n"
                    "$ aws ec2 describe-security-groups --group-ids $SG_ID --query 'SecurityGroups[0].{inbound: IpPermissions, outbound: IpPermissionsEgress[].IpRanges[].CidrIp}'\n"
                    "{\n    \"inbound\": [],\n    \"outbound\": [\n        \"0.0.0.0/0\"\n    ]\n}"
                ),
                "lang": "console",
            },
            {
                "say": "Create the role from `ec2-trust.json`, whose Principal is the EC2 service, attach the Session Manager policy, and wrap the role in an instance profile. The commands that change something print nothing when they work.",
                "code": (
                    "$ aws iam create-role --role-name hello-devops-server --assume-role-policy-document file://policies/ec2-trust.json --query Role.Arn --output text\n"
                    "arn:aws:iam::123456789012:role/hello-devops-server\n"
                    "$ aws iam attach-role-policy --role-name hello-devops-server --policy-arn arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore\n"
                    "$ aws iam create-instance-profile --instance-profile-name hello-devops-server --query InstanceProfile.Arn --output text\n"
                    "arn:aws:iam::123456789012:instance-profile/hello-devops-server\n"
                    "$ aws iam add-role-to-instance-profile --instance-profile-name hello-devops-server --role-name hello-devops-server"
                ),
                "lang": "console",
            },
            {
                "say": "Find an image and ask whether the launch would work. moto lacks Canonical's Ubuntu parameter, so on the emulator we borrow Amazon Linux's. The dry-run error is the good answer, and its wording is exactly what AWS prints.",
                "code": (
                    "$ AMI_ID=$(aws ssm get-parameter --name /aws/service/ami-amazon-linux-latest/al2023-ami-kernel-default-arm64 --query Parameter.Value --output text)\n"
                    "$ aws ec2 run-instances --dry-run --image-id $AMI_ID --instance-type t4g.micro --security-group-ids $SG_ID --iam-instance-profile Name=hello-devops-server\n"
                    "aws: [ERROR]: An error occurred (DryRunOperation) when calling the RunInstances operation: Request would have succeeded, but DryRun flag is set."
                ),
                "lang": "console",
            },
            {
                "say": "Now let `server-up.sh` do the whole launch, including the steps above (it reuses what exists). On moto the server runs at once; on AWS `wait instance-running` takes under a minute, and user data then needs another two to four.",
                "code": (
                    "$ ./server-up.sh\n...\n== 6. Ask AWS whether the launch would work (--dry-run), then launch\n"
                    "dry run: the request would succeed\nlaunched i-690b2c4be4c53fa21; waiting until it is running\n"
                    "--------------------------------------\n|          DescribeInstances         |\n+------------+-----------------------+\n"
                    "|  az        |  us-east-1a           |\n|  id        |  i-690b2c4be4c53fa21  |\n|  privateIp |  172.31.0.5           |\n"
                    "|  publicIp  |  54.214.91.141        |\n|  type      |  t4g.micro            |\n+------------+-----------------------+"
                ),
                "lang": "console",
            },
            {
                "say": "On a real server you would now run `aws ssm start-session --target i-...`, then `sudo cloud-init status --wait` and `systemctl status hello-devops`. No server boots on moto, so we tested `user-data.sh` in an `ubuntu:24.04` container instead, with moto standing in for S3. These lines come from that run; on EC2 the host field reads like `ip-172-31-0-5`.",
                "code": ON_SERVER,
                "lang": "console",
            },
            {
                "say": "Make the alarm and test it by hand. A real alarm starts as INSUFFICIENT_DATA and becomes OK once metrics arrive. Its email only comes after you confirm the subscription, while moto shows OK at once and sends no mail.",
                "code": (
                    "$ ./alarm.sh you@example.com\n...\n-------------------------------------------------\n|                DescribeAlarms                 |\n"
                    "+------------------------+--------+-------------+\n|          alarm         | state  |  threshold  |\n"
                    "+------------------------+--------+-------------+\n|  hello-devops-cpu-high |  OK    |  70.0       |\n"
                    "+------------------------+--------+-------------+\n"
                    "$ aws cloudwatch set-alarm-state --alarm-name hello-devops-cpu-high --state-value ALARM --state-reason \"Testing by hand\"\n"
                    "$ aws cloudwatch describe-alarms --alarm-names hello-devops-cpu-high --query 'MetricAlarms[0].[StateValue,StateReason]' --output text\n"
                    "ALARM\tTesting by hand"
                ),
                "lang": "console",
            },
            {
                "say": "Clean up. Terminating comes first, because the security group cannot go while a server uses it (moto skips that check, AWS does not). The last four counts are the ones to read.",
                "code": (
                    "$ ./cleanup.sh\n\n== 1. Terminate every server tagged Project=hello-devops (terminate deletes the disk too; stop keeps billing for it)\n"
                    "i-690b2c4be4c53fa21\tshutting-down\nwaiting until terminated (about a minute)\n...\n"
                    "== 6. Anything left that could still cost money?\nservers tagged Project=hello-devops, not terminated: 0\n"
                    "Elastic IPs in us-east-1: 0\nunattached disks in us-east-1: 0\nhello-devops buckets: 0"
                ),
                "lang": "console",
            },
        ],
    },
    "code": [
        {"lang": "bash", "title": "labs/aws/server/user-data.sh", "src": lab("server/user-data.sh"), "run": "./server-up.sh   # passes this file to EC2 as user data"},
        {"lang": "ini", "title": "labs/aws/server/hello-devops.service", "src": lab("server/hello-devops.service"), "run": "systemctl status hello-devops   # on the server"},
        {"lang": "json", "title": "labs/aws/server/cloudwatch-agent.json", "src": lab("server/cloudwatch-agent.json"), "run": "aws logs tail /hello-devops/app --follow"},
        {"lang": "json", "title": "labs/aws/policies/ec2-trust.json", "src": lab("policies/ec2-trust.json"), "run": "jq . policies/ec2-trust.json"},
        {"lang": "json", "title": "labs/aws/policies/hello-server-permissions.json", "src": lab("policies/hello-server-permissions.json"), "run": "aws iam get-role-policy --role-name hello-devops-server --policy-name read-app-files"},
        {"lang": "bash", "title": "labs/aws/server-up.sh", "src": lab("server-up.sh"), "run": "./server-up.sh"},
        {"lang": "bash", "title": "labs/aws/alarm.sh", "src": lab("alarm.sh"), "run": "./alarm.sh you@example.com"},
    ],
    "commands": [
        {"cmd": "brew install --cask session-manager-plugin", "what": "Install the plugin the AWS CLI needs for Session Manager."},
        {"cmd": "aws ec2 describe-vpcs --filters Name=is-default,Values=true --query 'Vpcs[0].VpcId' --output text", "what": "Find this region's default VPC."},
        {"cmd": "aws ec2 describe-subnets --filters Name=vpc-id,Values=VPC_ID --query 'Subnets[].[AvailabilityZone,CidrBlock]' --output table", "what": "List a VPC's subnets with their zone and address block."},
        {"cmd": "aws ssm get-parameter --name /aws/service/canonical/ubuntu/server/24.04/stable/current/arm64/hvm/ebs-gp3/ami-id --query Parameter.Value --output text", "what": "Look up the newest Ubuntu 24.04 ARM image in this region."},
        {"cmd": "aws ec2 run-instances --dry-run --image-id AMI_ID --instance-type t4g.micro", "what": "Ask whether a launch would be allowed, without launching (DryRunOperation means yes)."},
        {"cmd": "aws ec2 describe-instances --filters Name=tag:Project,Values=hello-devops --query 'Reservations[].Instances[].[InstanceId,State.Name,PublicIpAddress]' --output table", "what": "List the course's servers with their state and public IP."},
        {"cmd": "aws ssm start-session --target INSTANCE_ID", "what": "Open a shell on the server through Session Manager, with no open port."},
        {"cmd": "aws ssm start-session --target INSTANCE_ID --document-name AWS-StartPortForwardingSession --parameters '{\"portNumber\":[\"8000\"],\"localPortNumber\":[\"8000\"]}'", "what": "Make localhost:8000 on your Mac reach port 8000 on the server."},
        {"cmd": "sudo cloud-init status --wait", "what": "On the server: wait until user data has finished, then print the result."},
        {"cmd": "sudo journalctl -u hello-devops -f", "what": "On the server: follow the app's log lines."},
        {"cmd": "curl -s https://checkip.amazonaws.com", "what": "Print your Mac's public IP address, for a /32 security group rule."},
        {"cmd": "aws ec2 authorize-security-group-ingress --group-id SG_ID --protocol tcp --port 8000 --cidr MY_IP/32", "what": "Let only your address reach port 8000."},
        {"cmd": "aws ec2 revoke-security-group-ingress --group-id SG_ID --protocol tcp --port 8000 --cidr MY_IP/32", "what": "Remove that rule again."},
        {"cmd": "aws cloudwatch set-alarm-state --alarm-name hello-devops-cpu-high --state-value ALARM --state-reason \"Testing by hand\"", "what": "Force an alarm into ALARM to test its email, without real load."},
        {"cmd": "aws logs tail /hello-devops/app --follow", "what": "Stream the app's log lines that the CloudWatch agent sends."},
        {"cmd": "aws ec2 terminate-instances --instance-ids INSTANCE_ID", "what": "Delete a server and its disk (stop-instances keeps the disk and its bill)."},
    ],
    "mistake": (
        "Stopping the server and calling it cleaned up. A stopped instance ends only the compute bill: its disk keeps billing, and so does any Elastic IP you allocated. "
        "Terminate it, then run `./cleanup.sh` and check that its last four lines all end in 0."
    ),
    "real_world": (
        "In a team that runs a payments API on EC2, no security group anywhere allows port 22. "
        "Engineers open Session Manager sessions through their single sign-on role, and the sessions are logged to S3 for auditors. "
        "New servers start from a baked AMI with the app already installed. An Auto Scaling group, a rule that keeps a set number of servers running, replaces a failing one without anyone logging in."
    ),
    "task": {
        "title": "Your server, open to you alone, then gone",
        "steps": [
            "No account? Run `server-up.sh`, `alarm.sh` and `cleanup.sh` against moto as the lab README shows, then read the remaining steps instead of doing them.",
            "Install the Session Manager plugin, sign in with `aws login --profile learn`, and run `./server-up.sh` from `~/code/aws-lab`. Note the instance ID.",
            "Open a shell with `aws ssm start-session`. Wait for `cloud-init status --wait`, read the end of the user data log, and check the service with `systemctl status` and `journalctl`.",
            "Still on the server, run `whoami` and `aws sts get-caller-identity`. Explain both answers: who you are in Linux, and which identity the server's CLI uses.",
            "In a second terminal on your Mac, start port forwarding to port 8000 and `curl localhost:8000` a few times.",
            "From your Mac, `curl` the server's public IP on port 8000 with `--max-time 5`. Name the failure, using Day 10's three kinds of error.",
            "Add a security group rule for port 8000 from your own IP as a `/32`, curl the public IP again, then revoke the rule.",
            "Run `./alarm.sh` with your email, confirm the subscription, force the alarm to ALARM, and wait for the email.",
            "Run `aws logs tail /hello-devops/app --follow` and make a few requests through the port forward until their log lines appear.",
            "Run `./cleanup.sh`, check the last four counts, and look at Bills by service in the console tomorrow.",
        ],
        "hints": [
            "If start-session says the target is not connected, wait a minute: the agent registers after boot, and only once the role has reached the server.",
            "A curl that hangs until the timeout means the packets are dropped; a refused connection means they arrived and nothing listened.",
            "Your home IP from checkip.amazonaws.com can change when your router reconnects, and then the /32 rule no longer matches.",
        ],
        "done_when": "You are done when the public IP answers on port 8000 only while your /32 rule exists, the alarm email arrived, and ./cleanup.sh ends with four zeros.",
    },
    "explain_back": {
        "prompt": "Explain in 3 to 4 sentences how your server installed and started the app with nobody logged in, and how it read S3 without a key. Mention user data, systemd and the instance profile.",
        "answer": (
            "At launch I passed `user-data.sh` as user data, and cloud-init ran it once as root on the first boot. "
            "The script installed Python and the AWS CLI, copied the app from S3 and built a virtual environment. Then it installed a systemd unit that runs gunicorn as the `hello` user and restarts it after a crash. "
            "The S3 copy worked because the instance profile attaches the `hello-devops-server` role, and the CLI fetched that role's temporary credentials from the instance metadata service. "
            "No key was ever written to the server, and the role can only read the `app/` folder of one bucket."
        ),
    },
    "recap": [
        "The default VPC has one public subnet per zone; a security group with no inbound rules blocks every new connection.",
        "Session Manager gives you a shell through an outbound agent: no port 22, no key, just IAM.",
        "Look up AMIs by public parameter; t4g.micro is ARM, cheap and on the Free plan list.",
        "User data runs once at first boot as root; systemd keeps the app running after that.",
        "An instance profile gives the server a role, so it never holds a stored key.",
        "Stop keeps the disk and its bill; terminate ends both, and cleanup.sh checks for leftovers.",
    ],
    "check": [
        {
            "q": "A teammate's security group allows port 22 from 0.0.0.0/0 so they can SSH in. Which change gives them a shell and closes the port?",
            "options": [
                "Allow port 22 only from 10.0.0.0/8 instead",
                "Move the key pair file into the repository",
                "Use Session Manager and delete the port 22 rule",
                "Swap the security group for a network ACL",
            ],
            "answer": 2,
            "why": "Session Manager needs no inbound port at all; the agent connects out, and IAM decides who may open a session.",
        },
        {
            "q": "Your new server answers nothing on port 8000, and `systemctl status hello-devops` says the unit does not exist. Where do you look first?",
            "options": [
                "/var/log/cloud-init-output.log on the server",
                "The CloudWatch CPU graph for the instance",
                "The security group's outbound rules",
                "The budget alerts in the Billing console",
            ],
            "answer": 0,
            "why": "The unit is installed by user data, and everything user data printed, including the line where it stopped, is in that log.",
        },
        {
            "q": "An alarm has a 300-second period, 2 evaluation periods and a threshold of 70. CPU averages 90% for one 5-minute period, then 5% for the next. What happens?",
            "options": [
                "It goes to ALARM after the first period",
                "It stays OK, because two periods in a row must breach",
                "It goes to INSUFFICIENT_DATA after the spike",
                "It goes to ALARM after the second period",
            ],
            "answer": 1,
            "why": "With 2 evaluation periods, the alarm needs two breaching 5-minute averages in a row, and the second one was 5%.",
        },
    ],
    "interview": [
        {
            "q": "How do you give an application on EC2 access to S3?",
            "a": (
                "I create an IAM role whose trust policy allows the EC2 service, and give it a policy for exactly the buckets and prefixes it needs. Then I attach it through an instance profile. "
                "The SDK or CLI on the server picks up temporary credentials from the instance metadata service and refreshes them by itself. "
                "I launch with IMDSv2 required, so a server-side request forgery bug cannot read the credentials easily. "
                "I never copy access keys onto a server."
            ),
        },
        {
            "q": "How do you get a shell on a server that has no SSH port open?",
            "a": (
                "With Systems Manager Session Manager. The SSM Agent on the server keeps an outbound HTTPS connection to Systems Manager, and `aws ssm start-session` joins my terminal to it after an IAM check. "
                "It needs the agent, an instance role with AmazonSSMManagedInstanceCore, outbound HTTPS to the ssm, ssmmessages and ec2messages endpoints, and the plugin on my laptop. "
                "Sessions can be logged, and port forwarding replaces most SSH tunnels."
            ),
        },
        {
            "q": "What is the difference between stopping and terminating an EC2 instance, and what keeps costing money?",
            "a": (
                "Stopping shuts the server down but keeps it and its EBS volumes, so I can start it again later. The compute bill stops, the disk bill does not, and an auto-assigned public IP is released. "
                "Terminating deletes the instance and, by default, its root volume. "
                "Things that bill while idle include volumes and snapshots, Elastic IPs, NAT gateways and load balancers. "
                "For lab work I terminate and delete everything the same day, and I check the bill by service the next morning."
            ),
        },
    ],
    "deeper": {
        "minutes": 15,
        "body": (
            "Three things happen on the server before your app answers, and you can watch each one from a Session Manager shell.\n\n"
            "First, the metadata service. Ask it for a token, then use the token:\n\n"
            "1. `TOKEN=$(curl -s -X PUT http://169.254.169.254/latest/api/token -H \"X-aws-ec2-metadata-token-ttl-seconds: 300\")` asks for a token that lasts five minutes.\n"
            "2. `curl -s -H \"X-aws-ec2-metadata-token: $TOKEN\" http://169.254.169.254/latest/meta-data/iam/security-credentials/` prints the role's name, `hello-devops-server`.\n"
            "3. Add that name to the end of the URL, and you see the temporary credentials themselves, with their expiry time.\n\n"
            "Without the token header the request is refused, because the server allows IMDSv2 only. On the server, `aws sts get-caller-identity` prints an assumed-role ARN whose last part is the instance ID, which is how AWS names the role session for a server.\n\n"
            "Second, cloud-init. It works through stages during boot, and your user data runs in the last one, after the network is up. It keeps a copy of the script under `/var/lib/cloud/instances/` in a folder named after the instance ID, and `cloud-init status --long` reports whether it finished and what failed. Because user data runs on the first boot only, editing it on a stopped server changes nothing. Launch a new server instead: Terraform, Auto Scaling groups and Kubernetes all build on that habit of replacing servers rather than repairing them.\n\n"
            "Third, the choice between baking and bootstrapping. Our user data downloads and installs everything on every new server, which takes minutes and depends on apt, PyPI and AWS's download site being up at that moment. Baking moves that work earlier: a tool such as HashiCorp's Packer starts a temporary server, runs the same install steps, and saves the disk as your own AMI. New servers then boot ready, and user data only sets what differs per server, such as a version or a greeting. Containers push the same idea further: the image you build in Part 5 is a baked app that runs anywhere.\n\n"
            "For one lab server, bootstrapping with user data is the right call. For a fleet that must replace servers quickly, bake the slow parts and keep user data small."
        ),
    },
    "sources": [
        {"title": "Run commands when you launch an EC2 instance with user data (EC2 docs)", "url": "https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/user-data.html"},
        {"title": "Step 1: Complete Session Manager prerequisites (Systems Manager docs)", "url": "https://docs.aws.amazon.com/systems-manager/latest/userguide/session-manager-prerequisites.html"},
        {"title": "New AWS public IPv4 address charge (AWS News Blog)", "url": "https://aws.amazon.com/blogs/aws/new-aws-public-ipv4-address-charge-public-ip-insights"},
        {"title": "Amazon CloudWatch agent adds support for journald logs (AWS What's New)", "url": "https://aws.amazon.com/about-aws/whats-new/2026/08/amazon-cloudwatch-agent-journald/"},
    ],
}
