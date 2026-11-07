#!/usr/bin/env python3
"""Add Days 13 and 14 (hands-on AWS) to content/p3.json and update the part fields.

Re-runnable: it replaces d13/d14 if present, keeps Days 10 to 12 untouched, and
reads the lab files from labs/aws so the code blocks always match them.
Run: python3 brief/scratch/v3/aws/build_p3_aws.py
"""

import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import d13  # noqa: E402
import d14  # noqa: E402

ROOT = HERE.parents[3]
P3 = ROOT / "content" / "p3.json"

INTRO = (
    "Every deploy in this course travels over a network, and most production systems run in someone else's data center. "
    "Part 3 follows one request in the order things happen to it. Day 10 covers names, addresses and ports, Day 11 the HTTP conversation and the servers in the middle, and Day 12 the rented cloud around it all. "
    "Days 13 and 14 make that cloud real: an AWS account on the Free plan, the CLI, IAM, S3 and a small server of your own. They cost a few cents of credits. "
    "Without an account, every AWS command also runs against a local emulator."
)

RECAP = [
    "An IP address finds the machine and a port finds the program; private addresses reach the internet through NAT.",
    "/N fixes N bits: /24 holds 256 addresses and /16 holds 65,536; apps in containers bind to 0.0.0.0.",
    "DNS walks from your resolver to root, TLD and authoritative servers, and caches each answer for its TTL.",
    "Unresolved means DNS, refused means no listener, and a timeout means a drop or a wrong address.",
    "HTTP is text with methods, headers and status codes; TLS encrypts it and proves the server's name.",
    "A reverse proxy ends TLS and balances load, and 502, 503 and 504 usually come from it.",
    "In the cloud, route tables make subnets public or private; security groups are stateful and NACLs are not.",
    "On AWS: Free plan, root MFA and a zero-spend budget first; people get short-lived logins and programs get roles.",
    "An IAM policy is Effect, Action, Resource and Condition; calls start denied, and any Deny wins.",
    "A server should install itself with user data and systemd, be reached through Session Manager, and be terminated when done.",
]

FLASHCARDS = [
    {"front": "What does /24 mean, and how many addresses does it hold?", "back": "The first 24 bits are fixed; the block holds 256 addresses."},
    {"front": "Name the three private IPv4 ranges.", "back": "10.0.0.0/8, 172.16.0.0/12 and 192.168.0.0/16."},
    {"front": "What does NAT do in your home router?", "back": "It swaps your private source address for its public one on the way out, remembers the swap, and reverses it for replies."},
    {"front": "What is the difference between binding to 127.0.0.1 and to 0.0.0.0?", "back": "127.0.0.1 accepts only local connections; 0.0.0.0 listens on every address the machine has."},
    {"front": "Connection refused or timed out: what does each tell you?", "back": "Refused: the host answered but nothing listens on the port. Timed out: no answer, usually a firewall drop or a wrong address."},
    {"front": "In what order does a DNS lookup travel when nothing is cached?", "back": "Stub resolver, recursive resolver, root server, TLD server, authoritative server."},
    {"front": "401 or 403?", "back": "401: who are you? (no or bad credentials). 403: I know you, and you may not do this."},
    {"front": "502 or 504?", "back": "502: the proxy got no good answer from the app. 504: the proxy waited for the app and gave up."},
    {"front": "Layer 4 or layer 7 load balancer?", "back": "L4 forwards connections by address and port. L7 reads HTTP and can route by host, path and headers."},
    {"front": "Security group or network ACL?", "back": "Security group: stateful, allow-only, on a network interface. NACL: stateless, ordered allow and deny, on a subnet."},
    {"front": "Does an AWS budget alert stop your spending?", "back": "No. It only sends a notification, and its data can lag by hours; the resources keep running."},
    {"front": "What happens when a Free plan account's credits or six months run out?", "back": "The account closes instead of charging you. AWS keeps your data for 90 days, and upgrading in that window brings it back."},
    {"front": "Which identity should never have access keys?", "back": "The root user. Protect it with MFA and use it only for account-level tasks."},
    {"front": "How is `aws login` safer than an access key in ~/.aws/credentials?", "back": "It turns your console sign-in into temporary credentials that the CLI refreshes; a stored key works until someone deletes it."},
    {"front": "In a trust policy, what does `arn:aws:iam::123456789012:root` mean?", "back": "The whole account: any identity in it whose own policy allows sts:AssumeRole. It does not mean the root user."},
    {"front": "An access key ID starts with ASIA. What does that tell you?", "back": "It is temporary, from a role or a session. Long-lived keys start with AKIA."},
    {"front": "Why does `aws s3 rb --force` fail on a versioned bucket?", "back": "It deletes only the current objects; old versions and delete markers remain. Delete every version first."},
    {"front": "What four things does Session Manager need?", "back": "The SSM Agent, an instance role with AmazonSSMManagedInstanceCore, outbound HTTPS to the SSM endpoints, and the plugin on your laptop."},
    {"front": "Where do you look when EC2 user data seems to have done nothing?", "back": "In /var/log/cloud-init-output.log on the server."},
    {"front": "Stop or terminate: which one ends the disk bill?", "back": "Terminate. A stopped instance keeps its EBS disk, and the disk keeps billing."},
]

RESOURCES = [
    {"title": "How DNS Works, zine launch post (Julia Evans)", "url": "https://jvns.ca/blog/2022/04/26/new-zine--how-dns-works-/", "kind": "read",
     "why": "Julia Evans explains DNS with comics and real queries, so the moving parts are easy to picture."},
    {"title": "How DNS works (Computerphile)", "url": "https://www.youtube.com/watch?v=uOfonONtIuk", "kind": "watch",
     "why": "A clear whiteboard walk through resolvers, root servers and caching."},
    {"title": "You SUCK at Subnetting, full series (NetworkChuck)", "url": "https://www.youtube.com/playlist?list=PLIhvC56v63IKrRHh3gvZZBAGvsvOhwrRF", "kind": "watch",
     "why": "A fun video series that builds IP addresses, private ranges, NAT and subnetting step by step."},
    {"title": "Mess With DNS, a live DNS playground (Julia Evans)", "url": "https://messwithdns.net/about.html", "kind": "read",
     "why": "A free playground with a real subdomain, where you watch your own DNS queries arrive live."},
    {"title": "Overview of HTTP (MDN)", "url": "https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Overview", "kind": "docs",
     "why": "The standard reference for how HTTP works, with links to every header and status code."},
    {"title": "TLS handshake explained (Computerphile)", "url": "https://www.youtube.com/watch?v=86cQJ0MMses", "kind": "watch",
     "why": "Mike Pound draws the TLS handshake and the key exchange on paper, one message at a time."},
    {"title": "Certificate lifetime rationale and plans (Let's Encrypt)", "url": "https://letsencrypt.org/docs/cert-lifetimes/", "kind": "docs",
     "why": "Why certificates are getting shorter, the exact dates, and how to prepare your renewals."},
    {"title": "Shared responsibility (AWS Well-Architected)", "url": "https://docs.aws.amazon.com/wellarchitected/latest/security-pillar/shared-responsibility.html", "kind": "docs",
     "why": "AWS's own description of what it secures and what you must secure yourself."},
    {"title": "Choosing a Free plan or Paid plan (AWS Billing docs)", "url": "https://docs.aws.amazon.com/awsaccountbilling/latest/aboutv2/free-tier-plans.html", "kind": "docs",
     "why": "The current rules for new AWS accounts: the credits, the six-month limit, and what moves you to the Paid plan."},
    {"title": "Login for AWS local development using console credentials (AWS CLI docs)", "url": "https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-sign-in.html", "kind": "docs",
     "why": "How `aws login` works, which CLI version it needs, and where it keeps its temporary credentials."},
    {"title": "IAM policy power hour, re:Inforce 2024 (AWS Events)", "url": "https://www.youtube.com/watch?v=MKhkLqN0AyY", "kind": "watch",
     "why": "AWS engineers walk through the policy types and how to write, check and tighten them."},
    {"title": "AWS Certified Cloud Practitioner course, CLF-C02 (freeCodeCamp)", "url": "https://www.youtube.com/watch?v=NhDYbskXRgc", "kind": "watch",
     "why": "A long, free course on core AWS services; watch the parts on regions, VPCs, IAM, EC2 and billing."},
]

# Quiz: keep five Part 3 questions that still fit, add three on AWS, keep the two from earlier parts.
KEEP_QUIZ = [
    "An app in a container listens on 127.0.0.1:8000.",
    "How many addresses does 10.0.4.0/22 hold?",
    "You changed an A record whose TTL is 3600.",
    "Your load balancer returns 502 Bad Gateway",
    "What makes an AWS subnet public?",
]
NEW_QUIZ = [
    {
        "q": "`aws sts get-caller-identity` prints an ARN that ends in `:root` on your learning account. What should you do?",
        "options": [
            "Carry on, because root is fine for a lab",
            "Create an access key for root and use that",
            "Sign out, sign in as your IAM user, run aws login again",
            "Turn off MFA so the CLI can refresh the session",
        ],
        "answer": 2,
        "why": "The root user can do anything and no policy limits it; daily work, including the CLI, belongs to your IAM user with MFA.",
    },
    {
        "q": "Your server's security group has no inbound rules. From your Mac, `curl --max-time 5 http://PUBLIC_IP:8000` waits and then times out. What does that tell you?",
        "options": [
            "The app on the server has crashed",
            "DNS cannot resolve the address",
            "The server ran out of CPU credits",
            "The security group drops the packets",
        ],
        "answer": 3,
        "why": "A security group silently drops traffic it does not allow, so the client times out; a crashed app behind an open port would answer with connection refused.",
    },
    {
        "q": "Versioning is on, and you ran `aws s3 rm` on a report by mistake. How do you get it back?",
        "options": [
            "Delete the delete marker on top of it",
            "Wait for the lifecycle rule to restore it",
            "You cannot; S3 deletes are permanent",
            "Run aws s3 rb --force on the bucket",
        ],
        "answer": 0,
        "why": "In a versioned bucket a delete only adds a delete marker; removing the marker makes the newest version current again.",
    },
]


def main() -> None:
    part = json.loads(P3.read_text())
    lessons = [L for L in part["lessons"] if L["id"] not in ("d13", "d14")]
    lessons += [d13.LESSON, d14.LESSON]
    part["lessons"] = lessons
    part["intro"] = INTRO
    part["recap"] = RECAP
    part["flashcards"] = FLASHCARDS
    part["resources"] = RESOURCES

    old = part["quiz"]
    kept = [q for q in old if not q.get("from") and any(q["q"].startswith(k) for k in KEEP_QUIZ)]
    froms = [q for q in old if q.get("from")]
    assert len(kept) == 5, [q["q"][:40] for q in kept]
    assert len(froms) == 2
    # interleave so the AWS questions are not all at the end
    part["quiz"] = kept[:3] + [NEW_QUIZ[0]] + kept[3:] + NEW_QUIZ[1:] + froms

    # keep the key order of the original file
    order = ["part", "title", "intro", "lessons", "recap", "flashcards", "resources", "quiz"]
    part = {k: part[k] for k in order}
    P3.write_text(json.dumps(part, ensure_ascii=False, indent=1) + "\n")
    print(f"wrote {P3}: {[L['id'] for L in part['lessons']]}, quiz {len(part['quiz'])}, flashcards {len(part['flashcards'])}")


if __name__ == "__main__":
    main()
