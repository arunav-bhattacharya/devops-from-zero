"""Book-voice rewrite of d14 (fifth edition). Run: python3 brief/scratch/v5/tb/d14.py"""
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from apply import apply

opening = """Picture renting a flat in a city you will never visit. You cannot be there to unpack, so you leave a note for the caretaker: unpack the boxes, plug in the radio, keep it playing. You do not want a front door key under the mat for anyone to copy. And when you are done, you must check out, not just switch off the lights.

That is exactly what a cloud server needs, and two traps catch almost everyone. Many tutorials open the server's door to the whole internet, port 22 for SSH, because it is the quickest way in. And many people stop a server for the weekend and think it costs nothing.

Last time, you opened an AWS account, locked its master key away and stored a file in S3.

In this lesson, we'll rent one small server that installs and runs hello-devops by itself. We'll reach it with no open door, watch it with an alarm, and then check out properly. Before we start, make a guess, and keep it in mind."""

guess = {
    "q": "EC2 is AWS's service for renting servers. You stop (not terminate) your EC2 server for the weekend. What keeps billing?",
    "why": "Stopping ends the compute bill, but the EBS disk bills per GB-month, and an Elastic IP bills by the hour whether it is attached or not. Terminating is what ends both.",
}

terms_plain = [
    "A virtual server you rent from AWS by the second.",
    "Amazon Machine Image: the disk image a server starts from, such as Ubuntu 24.04 for ARM.",
    "A network disk attached to a server; it bills per GB-month even while the server is stopped.",
    "A script you pass at launch that cloud-init runs once, as root, on the first boot.",
    "The wrapper that attaches one IAM role to an EC2 server, so software on it gets temporary credentials.",
    "An AWS service that opens a shell on a server through a small program on it, with no open inbound port and no SSH key.",
    "A public IPv4 address you keep in your account until you release it; it bills by the hour.",
    "A rule that watches one measurement and changes state, and can send a message, when it crosses a threshold.",
]

s1 = """A server is a computer that runs programs for others, and in EC2 you rent a virtual one, called an instance. Before you rent one, you need somewhere to put it. Every region gives your account a default VPC, so you can launch a server before you design a network. It is the picture from two lessons ago, already built:

- The VPC is `172.31.0.0/16`.
- Each availability zone has one `/20` subnet: 12 free bits, so 4,096 addresses, minus the 5 that AWS keeps.
- An internet gateway is attached, and the route table sends `0.0.0.0/0` to it, so every default subnet is public.
- A server launched there gets a public IPv4 address unless you ask it not to.

The server itself still sees only its private address, such as `172.31.0.5`. The internet gateway translates between the two.

That is enough for one learning server. Production teams build their own VPC, with private subnets for apps and databases, as you sketched in the cloud lesson.

The firewall is a security group, the lock on the flat's door. It is stateful, so replies to allowed traffic go out without a rule of their own. Its outbound rules allow everything by default, which lets the server download packages. `server-up.sh` makes a group called `hello-devops-web` with no inbound rules at all. Nobody on the internet can start a connection to the server, you included.

That sounds like a problem. A flat with no way in seems useless. Next, we'll see why it isn't."""

s2 = """On Day 7 you logged in to a machine with SSH, the secure remote login, which needs port 22 open and a key. AWS gives you three ways in, and the one to use needs neither.

Session Manager, part of AWS Systems Manager, works the other way round. A small program on the server, the SSM Agent (SSM is Systems Manager's old short name), keeps an outbound HTTPS connection open to Systems Manager. It is the flat's phone line, dialled from the inside. The security group is stateful, so traffic on that connection flows both ways with no inbound rule. When you run `aws ssm start-session --target i-...`, AWS checks your IAM permissions and joins your terminal to that connection. It needs four things:

1. The SSM Agent on the server. AWS's and Canonical's Ubuntu images, and Amazon Linux 2023, come with it.
2. An instance role with the AWS managed policy `AmazonSSMManagedInstanceCore`.
3. Outbound HTTPS from the server to three endpoints (AWS's service addresses) in its region: `ssm`, `ssmmessages` and `ec2messages`. A public IP and the default outbound rule cover it.
4. The Session Manager plugin, an add-on for the CLI, on your Mac: `brew install --cask session-manager-plugin`.

It costs nothing extra on EC2, and there is no port to open and no key to lose. You arrive as `ssm-user`, a user the agent creates, with sudo rights (permission to run commands as the all-powerful root user). It forwards ports too: the document `AWS-StartPortForwardingSession` makes `localhost:8000` on your Mac reach port 8000 on the server.

**Open no inbound door. Let the server dial out, and let IAM decide who may join.**

EC2 Instance Connect is the second way. It pushes a one-time SSH key for you, but port 22 must still be open, either to AWS's Instance Connect address range or through an EC2 Instance Connect Endpoint.

Key pairs are the old way: AWS keeps the public key, you download a private `.pem` file once, and you open port 22. That is Day 7's SSH plus a file you must never lose or leak.

You can reach the server now. Next, we'll decide what kind of server it is, and what it costs."""

s3 = """An AMI (Amazon Machine Image) is the disk image a server starts from: the operating system, ready to boot. AMI IDs differ per region and change with every update, so look them up by name instead of copying one. Canonical, the company behind Ubuntu, publishes the newest Ubuntu IDs as public parameters in Parameter Store, a store of named values in Systems Manager. `server-up.sh` reads `/aws/service/canonical/ubuntu/server/24.04/stable/current/arm64/hvm/ebs-gp3/ami-id`.

The lab runs Ubuntu 24.04 because you know it from the Part 1 practice container. Its Python 3.12 is also new enough for gunicorn 26, the program that serves hello-devops, which needs 3.10 or later. Amazon Linux 2023, AWS's own system, is a fine choice too. Its built-in `python3`, though, stays at 3.9 for the whole life of the release, so you would install a newer one first.

The instance type sets CPU and memory, the size of the flat. The lab uses `t4g.micro`: 2 vCPUs (virtual CPUs), 1 GiB of memory and a Graviton processor. Graviton is ARM, like your Mac's chip, which is why the image is arm64. The Free plan lists six eligible types: t3.micro, t3.small, t4g.micro, t4g.small, c7i-flex.large and m7i-flex.large.

T types are burstable, made for servers that are mostly idle and sometimes busy. Each has a baseline, the share of CPU it may use all day: 10% per vCPU for `t4g.micro`. Below the baseline it saves up CPU credits, and above it the server spends them. In the default unlimited mode, staying above the baseline over a day costs extra. The script launches in standard mode, where the server slows down instead.

In us-east-1, checked today:

- The instance costs $0.0084 an hour.
- Its public IPv4 address costs $0.005 an hour, the same as an Elastic IP, used or not.
- Its 8 GB gp3 disk, an EBS volume (a network disk), costs $0.08 per GB-month, about 64 cents a month.

A two-hour session comes to about 3 cents, paid from Free plan credits.

Stop and terminate are different, and the guess was about exactly this. A stopped server ends the compute bill, keeps its disk and that disk's bill, and gives back its public IP, so it gets a new one on start. Terminating deletes the server and, by default, its disk.

**Stopping switches off the lights. Terminating checks out.**

An empty flat of the right size is ready. Next, we'll write the note that makes it a home for hello-devops."""

s4 = """User data is the note for the caretaker: a script you hand to EC2 at launch. On the first boot, a tool called cloud-init fetches it from the instance metadata service (next section) and runs it once, as root. It may be up to 16 KB. Everything it prints lands in `/var/log/cloud-init-output.log` on the server, which is where you look first when something is missing.

The lab's `server/user-data.sh` turns a bare Ubuntu server into a hello-devops server in seven steps:

1. Install `python3-venv`, `unzip` and `curl` with apt, Ubuntu's package manager.
2. Install the AWS CLI v2 from AWS's official zip, unless the image already has it.
3. Create a system user `hello` that cannot log in.
4. Copy the app files from S3 with `aws s3 cp`, using the server's role.
5. Make a virtual environment and `pip install` the requirements.
6. Install `hello-devops.service`, then `systemctl enable --now` it.
7. Install the CloudWatch agent and load its config.

It is Day 7's bash with `set -euo pipefail`, so a failed step stops the script. One line handles a cloud quirk. Ubuntu may update itself during its first boot, so apt waits up to five minutes for its lock instead of failing.

Why systemd, and not `nohup gunicorn &`? Day 6 already answered it. systemd, Linux's service manager, starts the app at boot and restarts it after a crash (`Restart=on-failure`). It runs it as `hello` instead of root, and sends its output to the journal, systemd's log. The unit binds gunicorn to `0.0.0.0:8000` so outside traffic can reach it (Day 10), and leaves the security group to decide who may.

Installing on every new server is slow, two to four minutes here. Teams that launch many servers bake the result into their own AMI, or ship the app as a container image (Part 5). Days 36 and 37 show Ansible, which configures servers that are already running.

Step 4 copied files from a private bucket. That needs credentials, yet we never gave the server a key. Next, we'll see where they came from."""

s5 = """The server reads S3 and writes to CloudWatch, so it needs credentials. Copying your access key onto it would put a long-lived key on a machine the internet can reach. A role does the job without one.

EC2 attaches a role through an instance profile, a wrapper that holds exactly one role. Software on the server asks the instance metadata service (IMDS) for the role's temporary credentials, and the AWS CLI does that by itself. IMDS lives at `169.254.169.254`, an address only the server itself can reach. It is the caretaker's desk inside the building, and nobody outside can walk up to it. The credentials rotate automatically, and you never manage a file of keys.

`server-up.sh` launches with `HttpTokens=required`, which means IMDSv2 only. A program must first fetch a session token with a PUT request, a request that sends data, before IMDS answers anything. That protects against a web app that an attacker tricks into fetching a URL for them. Such tricks usually send a plain GET, and cannot send a PUT with a special header first.

The role `hello-devops-server` carries three policies:

- `AmazonSSMManagedInstanceCore`, AWS's managed policy for Session Manager.
- `CloudWatchAgentServerPolicy`, AWS's managed policy for the agent.
- `read-app-files`, our own: list and read `app/` in one bucket, and nothing else.

A new role takes a few seconds to reach EC2. Launch too soon and EC2 calls the instance profile invalid, so the script waits and retries.

The server now runs, reads its files and reports. Next, we'll watch it from far away."""

s6 = """You will not visit the flat, so you need a way to watch it from home. CloudWatch is AWS's monitoring service, and an EC2 server reports to it from its first minute. Basic monitoring is on and free. It sends metrics, measurements over time, for CPU, network and disk activity every 5 minutes. It also runs status checks, AWS's own tests that the server and its hardware respond. Memory and free disk space are missing, because AWS cannot see inside your operating system; the CloudWatch agent can add them.

An alarm watches one metric and is in one of three states: OK, ALARM, or INSUFFICIENT_DATA, which is where a new alarm starts. The script `alarm.sh` makes one that goes to ALARM when the average CPU stays above 70% for two 5-minute periods in a row. Needing two in a row means one short spike sends no email.

On every change of state the alarm sends a message to an SNS topic, a named mailbox that delivers to your email. SNS first sends a confirmation email, and nothing arrives until you click its link. To test the chain without loading the server, `aws cloudwatch set-alarm-state` flips the alarm to ALARM by hand. The first 10 alarms are in the free tier.

For logs, the lines the app writes about each request, you have two choices:

- The simple one: open a session and run `journalctl -u hello-devops -f`. For one server you check now and then, that is enough.
- The CloudWatch agent: it reads the journal and sends the `hello-devops` unit's lines to the log group `/hello-devops/app`, one stream per server.

The agent earns its place when servers come and go. Logs outlive a terminated server, and `aws logs tail /hello-devops/app --follow` shows every server at once. The free tier covers 5 GB of logs a month, far more than this lab writes. Parts 12 to 14 go much further with Prometheus, Grafana and the Elastic stack.

Every piece is ready: network, door, image, note, role and alarm. Next, one script puts them together in the right order."""

s7 = """The script `server-up.sh` prints a heading for each of its six steps. The order matters, because the launch in step 6 uses everything the first five made:

1. Upload the app files to S3.
2. Create the role and the instance profile.
3. Create the security group.
4. Look up the AMI.
5. Fill in user data.
6. Launch.

The launch first runs with `--dry-run`. Only when AWS answers DryRunOperation does the script launch for real and wait until the server runs. Every piece carries the tag `Project=hello-devops`, a label for finding things later. Day 35's Terraform and Day 37's Ansible inventory use the same tag, and `cleanup.sh` uses it to find the server. The server also gets `Role=web` and an `owner` tag with your user name.

Then look at the same things in the console, in the same region:

1. EC2, then Instances: the state, the public IP, and the Connect button, whose Session Manager tab opens a shell in the browser.
2. EC2, then Security Groups: the inbound rules of `hello-devops-web`, empty until you add one.
3. CloudWatch: Alarms, then Log groups.
4. Billing and Cost Management, then Bills, the next day, to see the cents by service.

Clicking through the console is fine for one server, but it has a clear limit. Nobody can review a click, or repeat it exactly tomorrow. From here, Day 35 moves AWS work into Terraform, where one destroy removes it all. Days 36 and 37 configure servers like this one with Ansible, and Part 10 meets EKS, AWS's managed Kubernetes."""

sections = [
    ("Where the server lands: the default VPC", s1),
    ("A shell with no open door: Session Manager", s2),
    ("Choosing the flat: image, size and price", s3),
    ("The note for the caretaker: user data", s4),
    ("A key the server never has to keep: its role", s5),
    ("Watching from afar: metrics, an alarm and the logs", s6),
    ("One script to launch, then a tour of the console", s7),
]

closing = """We started with a flat in a city you would never visit, a note for the caretaker and no key under the mat. Your server unpacked hello-devops by itself from user data, took its credentials from its role, and let you in by phone through Session Manager. An alarm watched it, and the cleanup script checked out, which is more than switching off the lights.

After every cloud session, read the last four lines of `./cleanup.sh` and make sure each one ends in 0.

Next, we'll leave the shell behind and write Python scripts for this kind of work. When does a Bash script become too big, and what does Python give you instead?"""

worked_say = [
    "Read the default VPC first. moto's layout matches AWS: one `172.31.0.0/16` VPC and one public `/20` subnet per availability zone (us-east-1 has six). One difference: on AWS, `describe-route-tables` also shows `0.0.0.0/0` going to an `igw-...`, and moto has no internet gateway.",
    "Make the security group and look at its rules. Inbound is an empty list, so nothing can connect in; outbound allows everything, so the server can download what user data asks for.",
    "Create the role from `ec2-trust.json`, whose Principal is the EC2 service, attach the Session Manager policy, and wrap the role in an instance profile. The commands that change something print nothing when they work.",
    "Find an image and ask whether the launch would work. moto lacks Canonical's Ubuntu parameter, so on the emulator we borrow Amazon Linux's. The dry-run error is the good answer, and its wording is exactly what AWS prints.",
    "Now let `server-up.sh` do the whole launch, including the steps above (it reuses what exists). On moto the server runs at once; on AWS `wait instance-running` takes under a minute, and user data then needs another two to four.",
    "On a real server you would now run `aws ssm start-session --target i-...`, then `sudo cloud-init status --wait` and `systemctl status hello-devops`. No server boots on moto, so `user-data.sh` was tested in an `ubuntu:24.04` container instead, with moto standing in for S3. These lines come from that run; on EC2 the host field reads like `ip-172-31-0-5`.",
    "Make the alarm and test it by hand. A real alarm starts as INSUFFICIENT_DATA and becomes OK once metrics arrive. Its email only comes after you confirm the subscription, while moto shows OK at once and sends no mail.",
    "Clean up. Terminating comes first, because the security group cannot go while a server uses it (moto skips that check, AWS does not). The last four counts are the ones to read.",
]

recap = [
    "The default VPC has one public subnet per zone; a security group with no inbound rules blocks every new connection.",
    "Session Manager gives you a shell through an outbound agent: no port 22, no key, just IAM.",
    "Look up AMIs by public parameter; t4g.micro is ARM, cheap and on the Free plan list.",
    "User data runs once at first boot as root; systemd keeps the app running after that.",
    "An instance profile gives the server a role, so it never holds a stored key.",
    "Stop keeps the disk and its bill; terminate ends both. The limit of clicks and scripts: nobody can review them, which is why Terraform comes later.",
]

explain_back = {
    "answer": "At launch I passed `user-data.sh` as user data, and cloud-init ran it once as root on the first boot. The script installed Python and the AWS CLI, copied the app from S3 and built a virtual environment. Then it installed a systemd unit that runs gunicorn as the `hello` user and restarts it after a crash. The S3 copy worked because the instance profile attaches the `hello-devops-server` role, and the CLI fetched that role's temporary credentials from the instance metadata service. No key was ever written to the server, and the role can only read the `app/` folder of one bucket.",
}

deeper = {"body": """Three things happen on the server before your app answers, and you can watch each one from a Session Manager shell.

First, the metadata service. Ask it for a token, then use the token:

1. `TOKEN=$(curl -s -X PUT http://169.254.169.254/latest/api/token -H "X-aws-ec2-metadata-token-ttl-seconds: 300")` asks for a token that lasts five minutes.
2. `curl -s -H "X-aws-ec2-metadata-token: $TOKEN" http://169.254.169.254/latest/meta-data/iam/security-credentials/` prints the role's name, `hello-devops-server`.
3. Add that name to the end of the URL, and you see the temporary credentials themselves, with their expiry time.

Without the token header the request is refused, because the server allows IMDSv2 only. On the server, `aws sts get-caller-identity` prints an assumed-role ARN whose last part is the instance ID, which is how AWS names the role session for a server.

Second, cloud-init. It works through stages during boot, and your user data runs in the last one, after the network is up. It keeps a copy of the script under `/var/lib/cloud/instances/` in a folder named after the instance ID, and `cloud-init status --long` reports whether it finished and what failed. Because user data runs on the first boot only, editing it on a stopped server changes nothing. Launch a new server instead: Terraform, Auto Scaling groups and Kubernetes all build on that habit of replacing servers rather than repairing them.

Third, the choice between baking and bootstrapping. Our user data downloads and installs everything on every new server, which takes minutes and depends on apt, PyPI and AWS's download site being up at that moment. Baking moves that work earlier: a tool such as HashiCorp's Packer starts a temporary server, runs the same install steps, and saves the disk as your own AMI. New servers then boot ready, and user data only sets what differs per server, such as a version or a greeting. Containers push the same idea further: the image you build in Part 5 is a baked app that runs anywhere.

For one lab server, bootstrapping with user data is the right call. For a fleet that must replace servers quickly, bake the slow parts and keep user data small.

Two footnotes. SNS stands for Simple Notification Service. And the CloudWatch agent learned to read the journal in 2026; before that, people installed rsyslog to write log files for it."""}

apply(3, "d14", {
    "goal": "By the end you can launch a small Linux server from the CLI that installs and runs hello-devops by itself, reach it without opening SSH, watch it with CloudWatch, and delete every piece of it.",
    "opening": opening,
    "guess": guess,
    "terms_plain": terms_plain,
    "sections": sections,
    "diagram_caption": "You reach the server through Systems Manager, whose agent dials out. The server reads S3 with its role and reports to CloudWatch, behind a security group with no inbound rules.",
    "worked_say": worked_say,
    "recap": recap,
    "explain_back": explain_back,
    "closing": closing,
    "check": [{}, {}, {}],
    "interview": [{}, {}, {}],
    "deeper": deeper,
    "drop": ["analogy"],
})
print("d14 written")
