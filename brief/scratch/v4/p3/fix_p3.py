"""First-principles review of Part 3 (Days 10 to 14): exact old/new prose replacements.
Run from the repo root: python3 brief/scratch/v4/p3/fix_p3.py
Re-runnable: it always starts from the original (brief/scratch/v4/orig/p3.json) and writes content/p3.json."""
import json

ORIG = "brief/scratch/v4/orig/p3.json"
PATH = "content/p3.json"
d = json.load(open(ORIG))
L = {l["id"]: l for l in d["lessons"]}
done = skipped = 0


def get(lid, path):
    obj = L[lid]
    for k in path[:-1]:
        obj = obj[k]
    return obj, path[-1]


def rep(lid, path, old, new):
    global done, skipped
    obj, key = get(lid, path)
    s = obj[key]
    if old not in s and new in s:
        skipped += 1
        return
    n = s.count(old)
    assert n == 1, f"{lid} {path}: found {n} times: {old[:70]!r}"
    obj[key] = s.replace(old, new)
    done += 1


S = lambda i: ("sections", i, "body")
W = lambda i: ("worked", "steps", i, "say")

# ---------------------------------------------------------------- Day 10
rep("d10", S(0),
    "written as four numbers from 0 to 255, such as `192.168.1.23`. That gives",
    "written as four numbers from 0 to 255, such as `192.168.1.23`. Each number is one byte (8 bits), which is why it stops at 255. The 32 bits give")
rep("d10", S(0),
    "Some addresses are private. These ranges are reused inside millions of homes, offices and cloud networks, and routers on the internet never forward them:",
    "The 4.3 billion limit is why some addresses are private. These ranges are reused inside millions of homes, offices and cloud networks, and routers on the internet never forward them. The number after each slash is explained in the CIDR section below:")
rep("d10", S(1),
    "Everything else goes to the default gateway, which is your router. When two rules match, the more specific one wins.",
    "Everything else goes to the default gateway, which is your router. When two rules match, the more specific one wins: the one that covers fewer addresses.\n\nYour router has a route table of its own, whose default gateway is at your internet provider. Each router on the way reads the destination address and passes the packet one hop closer. `traceroute`, near the end of this lesson, lists those hops.")
rep("d10", S(2),
    "Networks are blocks of addresses, written in CIDR notation: an address, a slash and a number. The number says how many bits at the start are fixed. Those fixed bits name the network. The remaining bits number the machines inside it.",
    "Route tables, firewall rules and cloud networks all talk about blocks of addresses, not single ones. A block is written in CIDR notation (Classless Inter-Domain Routing): an address, a slash and a number. The number says how many bits at the start are fixed. Those fixed bits name the network. The remaining bits number the machines inside it. Each of the four numbers is 8 bits, so `/24` fixes the first three numbers and leaves the last one free.")
rep("d10", S(3),
    "Servers listen on well-known ports, so clients know where to knock:",
    "Servers listen on well-known ports, agreed numbers that tell a client where to knock. A URL like `https://github.com` names no port, so your browser uses 443. The common ones:")
rep("d10", S(3),
    "That is how one laptop keeps 50 browser tabs apart. An address",
    "That is how one laptop keeps 50 browser tabs apart. Your router's NAT uses the same four values to tell your laptop's connections from your phone's, and it may change the source port too. An address")
rep("d10", S(3),
    "After that, TCP numbers every byte, resends anything lost and delivers it in order.",
    "After that, TCP numbers every byte, and the receiver acknowledges what has arrived. The sender resends anything not acknowledged in time, and the receiver puts the bytes back in order.")
rep("d10", S(4),
    "- Binding to `0.0.0.0` means \"listen on every address this machine has\": Wi-Fi, loopback and any others alike.\n\n",
    "- Binding to `0.0.0.0` means \"listen on every address this machine has\": Wi-Fi, loopback and any others alike.\n\nDevelopment servers often choose `127.0.0.1` by default, so nobody else on your Wi-Fi can reach a half-finished app. Flask's built-in server does this, which matters in a moment.\n\n")
rep("d10", S(4),
    "A container gets its own network stack with its own loopback, like a tiny separate machine. When Docker publishes a port with `-p 8000:8000`, it forwards traffic to the container's network address, not to the container's loopback.",
    "A container gets its own network stack with its own loopback, like a tiny separate machine (Day 17 covers containers properly). Publishing a port with `-p 8000:8000` tells Docker to pass connections from port 8000 on your Mac to port 8000 in the container. Docker delivers them to the container's network address, not to its loopback.")
rep("d10", S(4),
    "binds to `127.0.0.1` never receives it.",
    "binds to `127.0.0.1` never receives them.")
rep("d10", S(4),
    "That is why `app.py` ends with `host=\"0.0.0.0\"`.",
    "That is why `app.py` ends with `host=\"0.0.0.0\"`, which overrides Flask's default.")
rep("d10", S(5),
    "It is a phone book spread over many thousands of servers, with caches everywhere. When your app",
    "It is a phone book spread over many thousands of servers, with caches everywhere. No single server could hold every name, so the work is split along the dots in a name, and each level only knows who runs the level below it. When your app")
rep("d10", S(5),
    "6. The answer flows back, and each layer caches it.\n\n",
    "6. The answer flows back, and each layer caches it.\n\nYour laptop learned which recursive resolver to use from the router, when it got its own address. Every recursive resolver ships with the root servers' addresses, so it always has a place to start.\n\n")
rep("d10", S(6),
    "- Connection refused: the machine answered, but nothing listens on that port.",
    "- Connection refused: the machine answered your SYN with a reset, because nothing listens on that port.")
rep("d10", S(6),
    "A refusal comes back in about a millisecond. A timeout makes you wait for seconds before it gives up, so even the waiting is a clue.",
    "A refusal comes back in about a millisecond. On a timeout, your machine resends the SYN a few times, waiting longer each time, before it gives up. So even the waiting is a clue.")
rep("d10", S(6),
    "It uses ICMP, a small control protocol that many firewalls block",
    "It uses ICMP (Internet Control Message Protocol), a small protocol for network status messages that many firewalls block")
rep("d10", W(0),
    "A Redis container called cache runs on a Docker network called shopnet.",
    "A Redis container called cache runs on a Docker network called shopnet. Redis is the small database hello-devops can use to count visits. A Docker network is a private network that containers join (Day 20), and `-d` runs a container in the background.")
rep("d10", W(1),
    "getaddrinfo is the name lookup.",
    "getaddrinfo is the function programs call to look up a name.")
rep("d10", ("check", 2, "q"),
    "Your VPC is 10.0.0.0/16",
    "Your network is 10.0.0.0/16")

# ---------------------------------------------------------------- Day 11
rep("d11", S(0),
    "HTTP/2 and HTTP/3 keep the same methods, headers and status codes. HTTP/2 packs messages into binary frames and runs many requests at once over one TCP connection. HTTP/3 does the same over QUIC, which runs on UDP.",
    "HTTP/2 and HTTP/3 keep the same methods, headers and status codes. An HTTP/1.1 connection carries one request at a time, so browsers open several. HTTP/2 runs many requests at once over one TCP connection, packed into binary frames. But TCP delivers bytes in order (Day 10), so one lost packet stalls them all. HTTP/3 runs over QUIC, on UDP, where a lost packet stalls only its own request.")
rep("d11", S(2),
    "Every response starts with a three-digit status code, and the first digit gives the family:",
    "Every response starts with a three-digit status code. The first digit gives the family, so even a client that does not know a code can act on it:")
rep("d11", S(2),
    "- 401 Unauthorized: who are you? Credentials are missing or wrong.",
    "- 401 Unauthorized: who are you? Despite the name, it means credentials are missing or wrong.")
rep("d11", S(2),
    "usually come from a proxy or load balancer, not from your code. A 502",
    "usually come from a proxy or load balancer, not from your code. \"Gateway\" in their names means that server in the middle. A 502")
rep("d11", S(3),
    "- `Authorization`: credentials, such as a bearer token. Never write it to a log.",
    "- `Authorization`: credentials, such as a bearer token (whoever holds it gets in). Never write it to a log.")
rep("d11", S(3),
    "curl is the tool you will use most, and a handful of flags cover nearly everything:",
    "A handful of curl flags cover nearly everything:")
rep("d11", S(4),
    "HTTPS is HTTP inside a TLS connection. TLS (Transport Layer Security) gives you three things:",
    "Plain HTTP is readable text, and every router between you and the server (Day 10) passes it along. Whoever runs one of them, or shares an open café Wi-Fi with you, could read a password or change the page. HTTPS is HTTP inside a TLS connection. TLS (Transport Layer Security) gives you three things:")
rep("d11", S(4),
    "It also names the host it wants (called SNI) and the HTTP versions it speaks (called ALPN).",
    "It also names the host it wants, in a field called SNI (Server Name Indication), which is TLS's version of the Host header. It lists the HTTP versions it speaks too, called ALPN.")
rep("d11", S(4),
    "Everything after this, including the HTTP request, is encrypted.\n\n",
    "Everything after this, including the HTTP request, is encrypted.\n\nHow can two machines agree on a key while others listen? Each side keeps a random secret and sends only a public value made from it. Each combines its own secret with the other's public value, and both arrive at the same key. The public values alone are not enough to work it out.\n\nThe signature in step 2 is the same proof your SSH key gave on Day 7. Only the private key can make it, and anyone with the public key can check it.\n\n")
rep("d11", S(4),
    "because SNI is sent before encryption starts. A newer extension, Encrypted Client Hello, hides it where both sides support it.",
    "because SNI is sent before encryption starts.")
rep("d11", S(5),
    "A certificate is a signed statement: \"this public key belongs to these names, from this date to that date\". The names live in a field called Subject Alternative Name (SAN), such as `DNS:localhost`. A certificate authority (CA) signs it.",
    "The signature only proves the server holds some private key. How does your browser know that key belongs to github.com, and not to an attacker? On Day 7, ssh asked you to accept a new server's fingerprint. A browser cannot ask you about every site, so it trusts a few certificate authorities (CAs) to vouch for servers.\n\nA certificate is a signed statement: \"this public key belongs to these names, from this date to that date\". The names live in a field called Subject Alternative Name (SAN), such as `DNS:localhost`. A CA signs it after checking that the requester controls those names.")
rep("d11", S(5),
    "They sign intermediate CAs, and an intermediate signs the server's certificate.",
    "They sign intermediate CAs, and an intermediate signs the server's certificate. That lets the root keys stay offline, locked away.")
rep("d11", S(5),
    "- DNS-01: publish a TXT record. It is the only way to get a wildcard such as `*.example.com`.\n\n",
    "- DNS-01: publish a TXT record. It is the only way to get a wildcard such as `*.example.com`.\n\nBoth prove control of the name. For HTTP-01, Let's Encrypt fetches the token from whatever server the name points to. For DNS-01, it reads the record from the domain's own DNS.\n\n")
rep("d11", S(5),
    "Certificates expire, and on purpose they expire sooner each year. Let's Encrypt certificates last 90 days today. Its default lifetime drops to 64 days on February 10, 2027, and to 45 days on February 16, 2028. Nobody should renew those by hand,",
    "Certificates expire, which limits how long a stolen key stays useful, and on purpose they expire sooner each year. Let's Encrypt certificates last 90 days today, and 45 days from 2028 (Go deeper has the dates). Nobody should renew those by hand,")
rep("d11", S(6),
    "In production, a request rarely goes straight to your app. It passes through servers in the middle.",
    "In production, a request rarely goes straight to your app. Picture hello-devops on one server with a public address: one crash takes the site down, and each new copy needs its own address and certificate. So requests pass through servers in the middle.")
rep("d11", S(6),
    "- Health checks: sending traffic only to copies that answer.",
    "- Health checks: probing each copy, for example with `GET /healthz`, and skipping the ones that fail.")
rep("d11", S(6),
    "A load balancer works at one of two levels. A layer 4 balancer",
    "A load balancer works at one of two levels, numbered after the OSI (Open Systems Interconnection) model of network layers. Layer 4 is TCP and UDP with their ports, and layer 7 is the application's protocol, such as HTTP. A layer 4 balancer")
rep("d11", S(6),
    "I would rather keep apps free of in-memory state, so any copy can serve any request.",
    "I would rather keep apps free of in-memory state, so any copy can serve any request. Today's task shows why: with `REDIS_HOST` empty, each copy of hello-devops counts visits in its own memory, so the two copies disagree.")
rep("d11", S(2),
    "These are the ones you will read in logs and dashboards, with what each one suggests:",
    "The ones you will read in logs and dashboards, and what each suggests:")
rep("d11", S(4),
    "You can watch it happen. `curl -v https://...` prints a line for each handshake message, and you read them in the worked example.\n\n",
    "")
rep("d11", S(6),
    "\n\nKubernetes has the same pieces under new names: Services balance connections on Day 41, and the Gateway API routes HTTP on Day 44.",
    "")

# ---------------------------------------------------------------- Day 12
rep("d12", S(0),
    "The cloud is renting computers, storage and ready-made services from a provider, by the second or the hour.",
    "Before the cloud, a team that needed a new server bought one, waited for it to be delivered and installed, and paid for it whether it was busy or idle. The cloud is renting computers, storage and ready-made services from a provider, by the second or the hour.")
rep("d12", S(0),
    "Every click in a cloud console is really an API call,",
    "Every click in a cloud console, the provider's website, is really an API call,")
rep("d12", S(0),
    "It scales to zero. Example: AWS Lambda.",
    "It scales to zero: when no events arrive, nothing runs and you pay nothing for compute. Example: AWS Lambda.")
rep("d12", S(1),
    "1. Where are your users? Closer means lower latency.",
    "1. Where are your users? Closer means lower latency, the delay before an answer arrives.")
rep("d12", S(2),
    "under different names. Learn the category first, and the names follow:",
    "under different names. Running hello-devops in the cloud would take one service from most of these lines, from a machine to run it to DNS for its name. Learn the category first, and the names follow:")
rep("d12", S(2),
    "- Object storage for files: S3, Blob Storage, Cloud Storage.",
    "- Object storage, for files you read and write whole over HTTPS: S3, Blob Storage, Cloud Storage.")
rep("d12", S(3),
    "AWS also keeps 5 addresses in every subnet (the first four and the last), so a /24 gives you 251 usable addresses, not 256.",
    "AWS also keeps 5 addresses in every subnet (the first four and the last), for jobs such as the VPC's router and DNS. So a /24 gives you 251 usable addresses, not 256.")
rep("d12", S(3),
    "That is your home router from Day 10 again. The internet gateway is the front door, and the NAT gateway is the switchboard that lets staff call out. The usual layout puts load balancers in public subnets, and apps and databases in private ones.",
    "Day 10's rule picks between routes: `10.0.0.0/16` is more specific than `0.0.0.0/0`, so traffic between subnets stays inside the VPC.\n\n"
    "This is your home router from Day 10 again, split in two. The internet gateway is the VPC's front door. A machine inside knows only its private address, so the gateway swaps in that machine's own public address, one for one. The NAT gateway does the home router's trick: many private machines share its single public address, and only replies get back in.\n\n"
    "The usual layout puts load balancers in public subnets, and apps and databases in private ones. A machine in a private subnet has no public address and no route in from the internet, so even a wrong firewall rule cannot expose it directly.")
rep("d12", S(5),
    "IAM (identity and access management) answers one question for every API call: may this caller do this action on this resource?",
    "Every API call can create, change or delete something, so the provider must know who is calling and what they may do. IAM (identity and access management) answers that for every call: may this caller do this action on this resource?")
rep("d12", S(5),
    "- Users: one person, with a password or access keys.",
    "- Users: one person, with a console password or access keys (a long-lived ID and secret for programs).")
rep("d12", S(6),
    "NAT gateways, load balancers, public IPv4 addresses, and disks",
    "NAT gateways, load balancers, public IPv4 addresses (scarce, as Day 10 showed), and disks")
rep("d12", ("task", "steps", 2),
    "Then add a deliberate overlap and a block with host bits set, and check that the script catches both.",
    "Then add a deliberate overlap, and a block with host bits set, such as `10.20.1.5/24`, which does not start at the first address of its block. Check that the script catches both.")

# ---------------------------------------------------------------- Day 13
rep("d13", S(0),
    "Control Tower landing zone. This course needs neither.",
    "Control Tower landing zone. Both are for companies that manage many accounts, and this course needs neither.")
rep("d13", S(1),
    "1. Turn on MFA for it.",
    "1. Turn on MFA (multi-factor authentication: a second proof on top of the password) for it.")
rep("d13", S(2),
    "for temporary credentials, a session token. The safe rule is about where they come from:",
    "for temporary credentials, a session token. The CLI never sends the secret itself. It uses it to sign each request, and AWS checks the signature with its own copy of the secret. The safe rule is about where credentials come from:")
rep("d13", S(3),
    " It is free, keeps 1 GB of files per region, and deletes them after 120 days without a visit.",
    " It is free.")
rep("d13", S(3),
    "prints the account and identity the CLI is using right now.",
    "prints the account and identity the CLI is using right now. STS is the Security Token Service, which hands out temporary credentials.")
rep("d13", S(3),
    "- Know your region. Each command works in one region, taken from",
    "- Know your region. Each region has its own API address, such as `ec2.eu-central-1.amazonaws.com`, so each command goes to one region. It comes from")
rep("d13", S(4),
    "`aws sts assume-role` hands back temporary credentials",
    "`aws sts assume-role` checks both sides, your own policy and the role's trust policy, then hands back temporary credentials")
rep("d13", S(5),
    "keeps files, which it calls objects, in buckets.",
    "keeps files, which it calls objects, in buckets. You read and write each object whole, over HTTPS, and cannot change a few bytes in the middle as on a disk.")
rep("d13", S(5),
    "- Bucket names are unique across every AWS account in the world, so the lab puts your account ID in the name. Since March 2026 you can also create buckets in your account regional namespace. Their names end with your account ID, the region and `-an`, and no other account can ever take them.",
    "- Bucket names are unique across every AWS account in the world, and each name becomes part of a web address, such as `NAME.s3.amazonaws.com`. So the lab puts your account ID in the name.")
rep("d13", S(5),
    "- Block Public Access has four settings,",
    "- Block Public Access stops any setting from opening a bucket to the whole internet. It has four settings,")

# ---------------------------------------------------------------- Day 14
rep("d14", S(0),
    "- Each availability zone has one `/20` subnet: 4,096 addresses,",
    "- Each availability zone has one `/20` subnet: 12 free bits, so 4,096 addresses,")
rep("d14", S(0),
    "- A server launched there gets a public IPv4 address unless you ask it not to.\n\n",
    "- A server launched there gets a public IPv4 address unless you ask it not to.\n\nThe server itself still sees only its private address, such as `172.31.0.5`. The internet gateway translates between the two (Day 12).\n\n")
rep("d14", S(1),
    "A small program on the server, the SSM Agent, keeps an outbound HTTPS connection open to Systems Manager.",
    "A small program on the server, the SSM Agent (SSM is Systems Manager's old short name), keeps an outbound HTTPS connection open to Systems Manager. The security group is stateful, so traffic on that connection flows both ways with no inbound rule.")
rep("d14", S(2),
    "Canonical publishes the newest Ubuntu IDs as public parameters in Systems Manager Parameter Store,",
    "Canonical, the company behind Ubuntu, publishes the newest Ubuntu IDs as public parameters in Parameter Store, a store of named values in Systems Manager,")
rep("d14", S(2),
    "`t4g.micro`: 2 vCPUs, 1 GiB",
    "`t4g.micro`: 2 vCPUs (virtual CPUs), 1 GiB")
rep("d14", S(2),
    "T types are burstable: they save up CPU credits while idle and spend them when busy.",
    "T types are burstable, made for servers that are mostly idle and sometimes busy. Each has a baseline, the share of CPU it may use all day: 10% per vCPU for `t4g.micro`. Below the baseline it saves up CPU credits, and above it the server spends them.")
rep("d14", S(3),
    "On the first boot, a tool called cloud-init runs it once, as root.",
    "On the first boot, a tool called cloud-init fetches it from the instance metadata service (see below) and runs it once, as root.")
rep("d14", S(3),
    "Installing on every boot is slow",
    "Installing on every new server is slow")
rep("d14", S(4),
    "asks the instance metadata service (IMDS), a local address at `169.254.169.254`, for the role's temporary credentials, and the AWS CLI does that by itself. They rotate automatically,",
    "asks the instance metadata service (IMDS) for the role's temporary credentials, and the AWS CLI does that by itself. IMDS lives at `169.254.169.254`, an address only the server itself can reach. The credentials rotate automatically,")
rep("d14", S(4),
    "has a much harder time stealing the credentials that way.",
    "has a much harder time stealing the credentials that way. Such tricks usually send a plain GET, and cannot send a PUT with a special header first.")
rep("d14", S(5),
    "plus status checks.",
    "plus status checks, AWS's own tests that the server and its hardware respond.")
rep("d14", S(5),
    "for two 5-minute periods in a row. On every change of state it sends a message to an SNS topic,",
    "for two 5-minute periods in a row. Needing two in a row means one short spike sends no email. On every change of state it sends a message to an SNS (Simple Notification Service) topic,")
rep("d14", S(6),
    "prints a heading for each of its six steps:",
    "prints a heading for each of its six steps. The order matters, because the launch in step 6 uses everything the first five made:")
rep("d14", ("task", "steps", 5),
    "using Day 10's three kinds of error.",
    "using Day 10's list of errors.")

open(PATH, "w").write(json.dumps(d, indent=1, ensure_ascii=False) + "\n")
print(f"{done} edits applied, {skipped} already present")
