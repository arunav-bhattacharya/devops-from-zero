#!/usr/bin/env python3
"""Build content/p2.json (Part 2, second edition): Days 8, 9 and 10.

Files the lessons show live in ./files and were run for real on 2026-10-30
(see ./test for the commands; container names were prefixed v2p2- and ports
moved to 18300-18399 while testing, then renamed back for the learner).
"""
import json
import pathlib

HERE = pathlib.Path(__file__).resolve().parent
FILES = HERE / "files"
OUT = pathlib.Path("/home/user/devops-from-zero/content/p2.json")


def f(name):
    return (FILES / name).read_text()


def L(title, url, kind):
    return {"title": title, "url": url, "kind": kind}


def src(d):
    return {"title": d["title"], "url": d["url"]}


# ---------------------------------------------------------------- links
NC_IP = L("What is an IP address? You SUCK at Subnetting, episode 1 (NetworkChuck)", "https://www.youtube.com/watch?v=5WfiTHiU4x8", "watch")
NC_PLAYLIST = L("You SUCK at Subnetting, full series (NetworkChuck)", "https://www.youtube.com/playlist?list=PLIhvC56v63IKrRHh3gvZZBAGvsvOhwrRF", "watch")
CP_DNS = L("How DNS works (Computerphile)", "https://www.youtube.com/watch?v=uOfonONtIuk", "watch")
JE_DNS_COMIC = L("Life of a DNS query, comic (Julia Evans)", "https://wizardzines.com/comics/life-of-a-dns-query/", "read")
JE_DNS_ZINE = L("How DNS Works, zine launch post (Julia Evans)", "https://jvns.ca/blog/2022/04/26/new-zine--how-dns-works-/", "read")
JE_IS_DNS = L("How do you tell if a problem is caused by DNS? (Julia Evans)", "https://jvns.ca/blog/2021/11/04/how-do-you-tell-if-a-problem-is-caused-by-dns/", "read")
MESS_DNS = L("Mess With DNS, a live DNS playground (Julia Evans)", "https://messwithdns.net/about.html", "read")
DOCKER_PORTS = L("Port publishing and mapping (Docker docs)", "https://docs.docker.com/engine/network/port-publishing/", "docs")
AWS_SUBNET_SIZE = L("Subnet CIDR blocks (AWS VPC docs)", "https://docs.aws.amazon.com/vpc/latest/userguide/subnet-sizing.html", "docs")
CF_LAYERS = L("Network layers reference (Cloudflare)", "https://developers.cloudflare.com/fundamentals/reference/network-layers/", "read")

MDN_OVERVIEW = L("Overview of HTTP (MDN)", "https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Overview", "docs")
MDN_MESSAGES = L("HTTP messages (MDN)", "https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Messages", "docs")
MDN_COOKIES = L("Using HTTP cookies (MDN)", "https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Cookies", "docs")
MDN_STATUS = L("HTTP response status codes (MDN)", "https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Status", "docs")
MDN_PROXY = L("Proxy servers and tunneling (MDN)", "https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Proxy_servers_and_tunneling", "docs")
CURL_WRITEOUT = L("Write out, in Everything curl", "https://everything.curl.dev/usingcurl/verbose/writeout", "docs")
CP_TLS = L("TLS handshake explained (Computerphile)", "https://www.youtube.com/watch?v=86cQJ0MMses", "watch")
CF_TLS = L("What happens in a TLS handshake? (Cloudflare)", "https://www.cloudflare.com/learning/ssl/what-happens-in-a-tls-handshake/", "read")
HPBN_TLS = L("High Performance Browser Networking, the TLS chapter (Ilya Grigorik)", "https://hpbn.co/transport-layer-security-tls/", "read")
LE_CHALLENGES = L("Challenge types (Let's Encrypt)", "https://letsencrypt.org/docs/challenge-types/", "docs")
LE_LIFETIMES = L("Certificate lifetime rationale and plans (Let's Encrypt)", "https://letsencrypt.org/docs/cert-lifetimes/", "docs")
LE_LOCALHOST = L("Certificates for localhost (Let's Encrypt)", "https://letsencrypt.org/docs/certificates-for-localhost/", "docs")
LE_64 = L("64-day certificate lifetimes coming February 2027 (Let's Encrypt)", "https://letsencrypt.org/2026/10/07/64-day-certs", "read")
CF_LB = L("Types of load balancers (Cloudflare)", "https://developers.cloudflare.com/learning-paths/load-balancing/planning/types-load-balancers/", "read")

FCC_CLF = L("AWS Certified Cloud Practitioner course, CLF-C02 (freeCodeCamp)", "https://www.youtube.com/watch?v=NhDYbskXRgc", "watch")
AWS_REGIONS = L("AWS Regions and Availability Zones (AWS docs)", "https://docs.aws.amazon.com/global-infrastructure/latest/regions/aws-regions-availability-zones.html", "docs")
GCP_COMPARE = L("Compare AWS and Azure services to Google Cloud (Google)", "https://docs.cloud.google.com/docs/get-started/aws-azure-gcp-service-comparison", "docs")
GCP_SUBNETS = L("Subnets (Google Cloud VPC docs)", "https://docs.cloud.google.com/vpc/docs/subnets", "docs")
AWS_NACL = L("Control subnet traffic with network ACLs (AWS VPC docs)", "https://docs.aws.amazon.com/vpc/latest/userguide/vpc-network-acls.html", "docs")
AWS_CONNTRACK = L("Security group connection tracking (AWS EC2 docs)", "https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/security-group-connection-tracking.html", "docs")
AWS_IAM_BP = L("IAM security best practices (AWS)", "https://aws.amazon.com/iam/resources/best-practices/", "docs")
AWS_SHARED = L("Shared responsibility (AWS Well-Architected)", "https://docs.aws.amazon.com/wellarchitected/latest/security-pillar/shared-responsibility.html", "docs")
AWS_PLANS = L("Choosing a Free plan or Paid plan (AWS Billing docs)", "https://docs.aws.amazon.com/awsaccountbilling/latest/aboutv2/free-tier-plans.html", "docs")
AZ_AVOID = L("Avoid charges with your Azure free account (Microsoft Learn)", "https://learn.microsoft.com/en-us/azure/cost-management-billing/manage/avoid-charges-free-account", "docs")
GCP_FREE = L("Google Cloud free trial and Always Free (Google)", "https://cloud.google.com/free-trial/", "docs")

# ---------------------------------------------------------------- SVGs
D08_SVG = (
    '<svg viewBox="0 0 560 264" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Your app asks the stub resolver, '
    'which asks a recursive resolver, which asks the root, TLD and authoritative servers. With the address in hand, the app '
    'opens a TCP connection to the server at that IP address and port.">'
    '<rect x="8" y="56" width="124" height="52" rx="10" class="bx"/>'
    '<text x="70" y="78" font-size="13" text-anchor="middle" class="t">Your app</text>'
    '<text x="70" y="96" font-size="11" text-anchor="middle" class="ts">curl, browser</text>'
    '<rect x="148" y="56" width="136" height="52" rx="10" class="bxt"/>'
    '<text x="216" y="78" font-size="13" text-anchor="middle" class="tk">Stub resolver</text>'
    '<text x="216" y="96" font-size="11" text-anchor="middle" class="tk">hosts file, cache</text>'
    '<rect x="300" y="56" width="108" height="52" rx="10" class="bxo"/>'
    '<text x="354" y="78" font-size="13" text-anchor="middle" class="tk">Recursive</text>'
    '<text x="354" y="96" font-size="11" text-anchor="middle" class="tk">resolver, cache</text>'
    '<rect x="424" y="8" width="128" height="40" rx="10" class="bx"/>'
    '<text x="488" y="33" font-size="13" text-anchor="middle" class="t">Root</text>'
    '<rect x="424" y="62" width="128" height="40" rx="10" class="bx"/>'
    '<text x="488" y="87" font-size="13" text-anchor="middle" class="t">TLD (.com)</text>'
    '<rect x="424" y="116" width="128" height="40" rx="10" class="bxg"/>'
    '<text x="488" y="141" font-size="13" text-anchor="middle" class="tk">Authoritative</text>'
    '<line x1="132" y1="82" x2="146" y2="82" class="ln" marker-end="url(#ar)"/>'
    '<line x1="284" y1="82" x2="298" y2="82" class="ln" marker-end="url(#ar)"/>'
    '<line x1="408" y1="70" x2="422" y2="30" class="lnd" marker-end="url(#ar)"/>'
    '<line x1="408" y1="82" x2="422" y2="82" class="lnd" marker-end="url(#ar)"/>'
    '<line x1="408" y1="94" x2="422" y2="134" class="lnd" marker-end="url(#ar)"/>'
    '<text x="230" y="134" font-size="11" text-anchor="middle" class="ts">each answer is cached for its TTL</text>'
    '<rect x="300" y="200" width="252" height="52" rx="10" class="bxp"/>'
    '<text x="426" y="222" font-size="13" text-anchor="middle" class="tk">Server</text>'
    '<text x="426" y="240" font-size="11" text-anchor="middle" class="tk">IP address and port</text>'
    '<line x1="70" y1="108" x2="70" y2="226" class="ln"/>'
    '<line x1="70" y1="226" x2="298" y2="226" class="ln" marker-end="url(#ar)"/>'
    '<text x="184" y="216" font-size="11" text-anchor="middle" class="ts">TCP connect to IP:port</text>'
    '</svg>'
)

D09_SVG = (
    '<svg viewBox="0 0 560 232" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="A client sends HTTPS to nginx, '
    'a reverse proxy that ends TLS and spreads plain HTTP requests across two app copies on port 8000. If no copy answers, '
    'nginx returns 502.">'
    '<rect x="8" y="94" width="112" height="52" rx="10" class="bx"/>'
    '<text x="64" y="116" font-size="13" text-anchor="middle" class="t">Client</text>'
    '<text x="64" y="134" font-size="11" text-anchor="middle" class="ts">curl</text>'
    '<rect x="176" y="78" width="176" height="84" rx="10" class="bxo"/>'
    '<text x="264" y="104" font-size="13" text-anchor="middle" class="tk">nginx</text>'
    '<text x="264" y="124" font-size="11" text-anchor="middle" class="tk">reverse proxy</text>'
    '<text x="264" y="142" font-size="11" text-anchor="middle" class="tk">TLS ends here</text>'
    '<rect x="400" y="24" width="152" height="52" rx="10" class="bxt"/>'
    '<text x="476" y="46" font-size="13" text-anchor="middle" class="tk">app1</text>'
    '<text x="476" y="64" font-size="11" text-anchor="middle" class="tk">HTTP :8000</text>'
    '<rect x="400" y="164" width="152" height="52" rx="10" class="bxt"/>'
    '<text x="476" y="186" font-size="13" text-anchor="middle" class="tk">app2</text>'
    '<text x="476" y="204" font-size="11" text-anchor="middle" class="tk">HTTP :8000</text>'
    '<line x1="120" y1="120" x2="174" y2="120" class="ln" marker-end="url(#ar)"/>'
    '<text x="148" y="112" font-size="11" text-anchor="middle" class="ts">HTTPS</text>'
    '<line x1="352" y1="104" x2="398" y2="56" class="ln" marker-end="url(#ar)"/>'
    '<line x1="352" y1="136" x2="398" y2="184" class="ln" marker-end="url(#ar)"/>'
    '<text x="264" y="186" font-size="11" text-anchor="middle" class="ts">502 if no copy answers</text>'
    '</svg>'
)

D10_SVG = (
    '<svg viewBox="0 0 560 330" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Traffic from the internet enters a '
    'VPC through an internet gateway into public subnets in two availability zones. Private subnets in each zone hold the app '
    'and database and reach out through a NAT gateway in the public subnet of their zone.">'
    '<rect x="200" y="8" width="160" height="36" rx="10" class="bx"/>'
    '<text x="280" y="31" font-size="13" text-anchor="middle" class="t">Internet</text>'
    '<rect x="200" y="64" width="160" height="36" rx="10" class="bxg"/>'
    '<text x="280" y="87" font-size="13" text-anchor="middle" class="tk">Internet gateway</text>'
    '<rect x="24" y="128" width="240" height="52" rx="10" class="bxt"/>'
    '<text x="144" y="150" font-size="13" text-anchor="middle" class="tk">Public subnet a</text>'
    '<text x="144" y="168" font-size="11" text-anchor="middle" class="tk">10.0.1.0/24, LB, NAT</text>'
    '<rect x="296" y="128" width="240" height="52" rx="10" class="bxt"/>'
    '<text x="416" y="150" font-size="13" text-anchor="middle" class="tk">Public subnet b</text>'
    '<text x="416" y="168" font-size="11" text-anchor="middle" class="tk">10.0.2.0/24, LB, NAT</text>'
    '<rect x="24" y="220" width="240" height="52" rx="10" class="bxp"/>'
    '<text x="144" y="242" font-size="13" text-anchor="middle" class="tk">Private subnet a</text>'
    '<text x="144" y="260" font-size="11" text-anchor="middle" class="tk">10.0.11.0/24, app, DB</text>'
    '<rect x="296" y="220" width="240" height="52" rx="10" class="bxp"/>'
    '<text x="416" y="242" font-size="13" text-anchor="middle" class="tk">Private subnet b</text>'
    '<text x="416" y="260" font-size="11" text-anchor="middle" class="tk">10.0.12.0/24, app, DB</text>'
    '<line x1="280" y1="44" x2="280" y2="62" class="ln" marker-end="url(#ar)"/>'
    '<line x1="240" y1="100" x2="172" y2="126" class="ln" marker-end="url(#ar)"/>'
    '<line x1="320" y1="100" x2="388" y2="126" class="ln" marker-end="url(#ar)"/>'
    '<line x1="144" y1="220" x2="144" y2="182" class="lnd" marker-end="url(#ar)"/>'
    '<text x="152" y="205" font-size="11" text-anchor="start" class="ts">out via NAT</text>'
    '<line x1="416" y1="220" x2="416" y2="182" class="lnd" marker-end="url(#ar)"/>'
    '<text x="424" y="205" font-size="11" text-anchor="start" class="ts">out via NAT</text>'
    '<text x="144" y="294" font-size="13" text-anchor="middle" class="t">AZ a</text>'
    '<text x="416" y="294" font-size="13" text-anchor="middle" class="t">AZ b</text>'
    '<text x="280" y="320" font-size="11" text-anchor="middle" class="ts">one VPC: 10.0.0.0/16</text>'
    '</svg>'
)

# ================================================================ Day 8
d08 = {
    "id": "d08",
    "title": "How computers find each other: IP, ports and DNS",
    "minutes": 50,
    "goal": "By the end you can read an IP address and a CIDR block, explain how a name becomes an address, and tell from an error message which step of a connection failed.",
    "guess": {
        "q": "Which network holds more addresses: 10.0.0.0/16 or 10.0.0.0/24?",
        "options": [
            "10.0.0.0/24, because 24 is bigger than 16",
            "10.0.0.0/16, with 65,536 addresses",
            "They hold the same number of addresses",
            "It depends on the router's settings",
        ],
        "answer": 1,
        "why": "The number after the slash counts the fixed bits. More fixed bits leave fewer free ones, so /16 has 65,536 addresses and /24 only 256.",
    },
    "terms": [
        {"term": "IP address", "plain": "A number that identifies one network interface, such as 192.168.1.23 or 127.0.0.1."},
        {"term": "Private address", "plain": "An address from a range that many networks reuse inside (10.x, 172.16 to 172.31, 192.168.x) and that the internet never routes."},
        {"term": "CIDR notation", "plain": "A way to write a block of addresses: 10.0.1.0/24 means the first 24 bits are fixed, which leaves 256 addresses."},
        {"term": "NAT", "plain": "Network address translation: a router swaps private addresses for its own public address on the way out, and back on the way in."},
        {"term": "Port", "plain": "A number from 0 to 65535 that picks which program on a machine receives the traffic."},
        {"term": "TCP", "plain": "A transport protocol that opens a connection with a handshake and delivers bytes in order, resending anything lost."},
        {"term": "DNS resolver", "plain": "A server that answers 'what is the address of this name?' by asking other DNS servers and caching the answers."},
        {"term": "TTL", "plain": "Time to live: how many seconds a DNS answer may be cached and reused before someone must ask again."},
    ],
    "sections": [
        {
            "h": "IP addresses: where a machine lives",
            "body": (
                "Every request starts with an address. An IP address identifies one network interface: the hardware or software that connects a machine to a network. "
                "Think of it as the street address of a building.\n\n"
                "An IPv4 address is 32 bits, written as four numbers from 0 to 255, such as `192.168.1.23`. That gives about 4.3 billion addresses, which is not enough for every device on earth. "
                "IPv6 fixes this with 128-bit addresses written in hex, such as `2001:db8::1`. You will see IPv6 in tool output, and it works the same way. "
                "This course mostly uses IPv4 because the numbers are easier to read.\n\n"
                "Your laptop has several addresses at once:\n\n"
                "- One on Wi-Fi, handed out by your home router.\n"
                "- `127.0.0.1`, the loopback address, which always means \"this machine\".\n"
                "- More inside Docker Desktop's Linux VM, one per Docker network.\n\n"
                "Some addresses are private. These ranges are reused inside millions of homes, offices and cloud networks, and routers on the internet never forward them:\n\n"
                "- `10.0.0.0/8`: every address that starts with 10.\n"
                "- `172.16.0.0/12`: from 172.16 to 172.31.\n"
                "- `192.168.0.0/16`: every address that starts with 192.168.\n\n"
                "Every other normal address is public and unique on the whole internet. Your laptop almost certainly has a private one, such as `192.168.1.23`. "
                "If you see an address starting with `100.64` to `100.127` on a phone hotspot or a VPN, that is a special shared range for providers, not a public address."
            ),
            "refs": [NC_IP],
        },
        {
            "h": "NAT and the way out of your house",
            "body": (
                "So how does a laptop with a private address reach GitHub? Through your home router, using NAT (network address translation). "
                "The router has one public address from your internet provider. Data travels in packets: small chunks, each labelled with a source and a destination address. "
                "When your laptop sends a packet out, the router does three things:\n\n"
                "1. It replaces your private source address with its public one.\n"
                "2. It remembers the swap, so it knows the reply belongs to your laptop.\n"
                "3. When the reply comes back, it swaps the address back and passes the reply to you.\n\n"
                "Everyone in your home shares that one public address. That is why a website sees your router's address, never your laptop's. "
                "It also explains why nobody outside can start a connection to your laptop: the router has no record for traffic it never saw go out.\n\n"
                "How does your laptop know to send packets to the router at all? Every machine has a route table: a short list of rules that says where to send traffic for each block of addresses. "
                "A laptop usually has two kinds of rule. Addresses on its own network go straight to the destination. Everything else goes to the default gateway, which is your router. "
                "When two rules match, the more specific one wins.\n\n"
                "Keep this picture. On Day 10 a cloud network uses the same ideas, with an internet gateway, a NAT gateway and route tables that you write yourself."
            ),
            "refs": [NC_PLAYLIST],
        },
        {
            "h": "CIDR: reading /24 and /16",
            "body": (
                "Networks are blocks of addresses, written in CIDR notation: an address, a slash and a number. The number says how many bits at the start are fixed. "
                "Those fixed bits name the network. The remaining bits number the machines inside it.\n\n"
                "An IPv4 address has 32 bits, so a block holds 2 to the power of (32 minus N) addresses:\n\n"
                "- `/32`: 1 address, a single machine.\n"
                "- `/24`: 256 addresses, such as `10.0.1.0` to `10.0.1.255`.\n"
                "- `/16`: 65,536 addresses, such as `10.0.0.0` to `10.0.255.255`.\n"
                "- `/8`: 16,777,216 addresses, everything that starts with `10.`.\n\n"
                "This trips up almost everyone at first: a bigger number after the slash means a smaller network. Each extra fixed bit halves the block, so a `/25` is half a `/24`, 128 addresses.\n\n"
                "You will also meet an older way to write the same thing, the subnet mask. `255.255.255.0` means /24 and `255.255.0.0` means /16. "
                "On a Mac, `ifconfig` prints the mask in hex, and `0xffffff00` is /24.\n\n"
                "You do not need binary drills. Python's `ipaddress` module checks your math. "
                "`python3 -c \"import ipaddress as i; print(i.ip_network('10.0.0.0/16').num_addresses)\"` prints `65536`."
            ),
            "refs": [AWS_SUBNET_SIZE],
        },
        {
            "h": "Ports, and how TCP and UDP deliver",
            "body": (
                "An IP address gets traffic to the right machine. A port picks the right program on that machine, like an apartment number in a building. "
                "A port is a number from 0 to 65535. Servers listen on well-known ports, so clients know where to knock:\n\n"
                "- 22: SSH\n"
                "- 53: DNS\n"
                "- 80: HTTP\n"
                "- 443: HTTPS\n"
                "- 5432: PostgreSQL\n"
                "- 6379: Redis\n\n"
                "The client uses a port too, picked at random from a high range for each connection. It is called an ephemeral port. "
                "Four values define one connection: source address, source port, destination address and destination port. That is how one laptop keeps 50 browser tabs apart. "
                "An address together with a port is called a socket.\n\n"
                "Two transport protocols carry the data. TCP is like registered mail with receipts. Before any data moves, the client and server do a three-step handshake:\n\n"
                "1. The client sends SYN: \"I want to talk.\"\n"
                "2. The server answers SYN-ACK: \"Fine, I hear you.\"\n"
                "3. The client sends ACK, and the connection is open.\n\n"
                "After that, TCP numbers every byte, resends anything lost and delivers it in order. HTTP, SSH and database connections use TCP.\n\n"
                "UDP is a postcard: no handshake and no guarantee. It is lighter, so it suits small questions and live media. "
                "DNS uses UDP on port 53 for most queries. HTTP/3 runs over UDP too, through a protocol called QUIC, and Day 9 comes back to that."
            ),
            "refs": [CF_LAYERS],
        },
        {
            "h": "Loopback, 0.0.0.0 and why containers bind to 0.0.0.0",
            "body": (
                "A server program binds to an address and a port, then listens there. The address it binds to decides who can reach it. People get this wrong more than anything else on this page:\n\n"
                "- Binding to `127.0.0.1` accepts connections from the same machine only. Loopback traffic never leaves the machine.\n"
                "- Binding to `0.0.0.0` means \"listen on every address this machine has\": Wi-Fi, loopback and any others alike.\n\n"
                "`0.0.0.0` is not an address you connect to. It is a wildcard for listening. You can see the difference in the tools. "
                "On Linux, `ss -tlnp` shows one server on `127.0.0.1:9101` and another on `0.0.0.0:9102`. On a Mac, `lsof` shows the second one as `*:9102`, where the star means every address.\n\n"
                "Now the container part. A container gets its own network stack with its own loopback, like a tiny separate machine. "
                "When Docker publishes a port with `-p 8000:8000`, it forwards traffic to the container's network address, not to the container's loopback. "
                "So an app inside the container that binds to `127.0.0.1` never receives it. curl then prints something like `Empty reply from server` or `Connection reset by peer`. "
                "The fix is to bind to `0.0.0.0` inside the container. That is why `app.py` ends with `host=\"0.0.0.0\"`.\n\n"
                "One more Docker detail. `-p 8000:8000` publishes the port on every address of your Mac, so other machines on your Wi-Fi may reach it. "
                "Docker's own docs call port publishing \"insecure by default\". Write `-p 127.0.0.1:8000:8000` when only your laptop should connect."
            ),
            "refs": [DOCKER_PORTS],
        },
        {
            "h": "DNS: from names to addresses",
            "body": (
                "People remember names, and machines connect to addresses. DNS, the Domain Name System, turns one into the other. "
                "It is a phone book spread over many thousands of servers, with caches everywhere. When your app looks up `github.com`, the question travels this chain:\n\n"
                "1. The stub resolver, a small part of your operating system, checks `/etc/hosts` and its own cache.\n"
                "2. If it has no answer, it asks a recursive resolver: your router, your internet provider, or a public one such as `1.1.1.1`.\n"
                "3. If that resolver has nothing cached, it asks a root server, which says \"ask the servers for .com\".\n"
                "4. A .com server, called a TLD (top-level domain) server, says \"ask github.com's own name servers\".\n"
                "5. The authoritative server for github.com gives the real answer.\n"
                "6. The answer flows back, and each layer caches it.\n\n"
                "Each answer is a record, and these are the types you will meet:\n\n"
                "- A: name to IPv4 address.\n"
                "- AAAA: name to IPv6 address.\n"
                "- CNAME: this name is an alias, so look up that other name instead.\n"
                "- MX: which servers accept email for the domain.\n"
                "- TXT: free text, used to prove you own a domain and for email policy.\n"
                "- NS: which servers are authoritative for the domain.\n\n"
                "Every record has a TTL in seconds: how long anyone may cache it. People say a DNS change takes time to \"propagate\". "
                "What really happens is that old answers sit in caches until their TTL runs out. "
                "So after a change, one colleague reaches the new server while another still reaches the old one. Teams lower the TTL a day before a planned move.\n\n"
                "`/etc/hosts` is a local file that beats DNS, for your machine only. One gotcha: `dig` asks DNS servers directly and ignores `/etc/hosts`, while your apps and `ping` read that file first. "
                "If `dig` and your app disagree about a name, look in `/etc/hosts`."
            ),
            "refs": [CP_DNS, JE_DNS_COMIC, MESS_DNS],
        },
        {
            "h": "Refused, timed out or unresolved: reading the error",
            "body": (
                "When a connection fails, the exact error tells you which step broke. Learn these four, and much of network debugging becomes reading:\n\n"
                "- Could not resolve host, or \"Name or service not known\": DNS failed. No packet went to the server at all.\n"
                "- Connection refused: the machine answered, but nothing listens on that port. The app is down, on another port, or bound to `127.0.0.1`.\n"
                "- Timed out: nothing answered. A firewall dropped the packets, or the address is wrong or unreachable.\n"
                "- Connection reset, or an empty reply: something accepted the connection and then closed it. Proxies and Docker's port forwarder do this when the app behind them is unreachable.\n\n"
                "A refusal comes back in about a millisecond. A timeout makes you wait for seconds before it gives up. That difference alone tells you a lot.\n\n"
                "Each tool in your toolbox answers one question:\n\n"
                "- `ping`: are you there? It uses ICMP, a small control protocol that many firewalls block, so a failed ping proves little.\n"
                "- `traceroute`: which routers does my traffic pass on the way?\n"
                "- `dig` and `nslookup`: what does DNS say about this name?\n"
                "- `ifconfig` on a Mac, `ip addr` on Linux: which addresses do I have?\n"
                "- `lsof -iTCP -sTCP:LISTEN` on a Mac, `ss -tlnp` on Linux: who listens on which port?\n"
                "- `nc -zv host port`: can I open a TCP connection to that port?\n\n"
                "`ss` and `ip` exist only on Linux. Use them in your practice box, where `apt install iproute2` adds them."
            ),
            "refs": [JE_IS_DNS],
        },
    ],
    "analogy": (
        "Connecting to a service is like mailing a letter to a business you only know by name. First you look up its street address in a phone book (DNS). "
        "The street address finds the building (the IP address), and the apartment number finds the right person inside (the port). "
        "Registered mail with receipts is TCP, and a postcard is UDP. Your home's front desk rewrites the return address on every outgoing letter to the building's address, and remembers who sent what (NAT). "
        "The picture breaks on speed and on copies. The whole thing takes milliseconds, and the phone book is copied into caches all over the world, each one possibly a little out of date."
    ),
    "diagram": D08_SVG,
    "diagram_caption": "The name is resolved first, through a chain of resolvers and caches. Only then does your app open a TCP connection to the address and port.",
    "worked": {
        "title": "Debug a service name that does not resolve",
        "steps": [
            {
                "say": "Set the scene. A Redis container called cache runs on a Docker network called shopnet. A second container, client, is your app's stand-in; it starts on Docker's default network. Inside client, install three tools: dig (in dnsutils), ip and nc. The first two docker commands print long IDs, trimmed here.",
                "code": (
                    "$ docker network create shopnet\n"
                    "$ docker run -d --name cache --network shopnet redis:8-alpine\n"
                    "$ docker run -it --rm --name client --hostname client ubuntu:24.04 bash\n"
                    "root@client:/# apt-get update -qq && apt-get install -y -qq dnsutils iproute2 netcat-openbsd > /dev/null\n"
                    "debconf: delaying package configuration, since apt-utils is not installed"
                ),
                "lang": "console",
            },
            {
                "say": "Reproduce the symptom. Your colleague says the app cannot reach cache on port 6379. Try it with nc. Read the error carefully: getaddrinfo is the name lookup. It failed before a single packet went to port 6379, so this is a DNS problem, not a firewall or a dead Redis.",
                "code": (
                    "root@client:/# nc -zv cache 6379\n"
                    "nc: getaddrinfo for host \"cache\" port 6379: Name or service not known"
                ),
                "lang": "console",
            },
            {
                "say": "Ask the system resolver the way apps do, with `getent hosts`. It reads /etc/hosts and then DNS. When the name is unknown, it prints nothing and exits with code 2. The hosts file only knows localhost and the container itself (IPv6 lines trimmed). So the DNS server this container uses has never heard of cache.",
                "code": (
                    "root@client:/# getent hosts cache; echo \"exit code: $?\"\n"
                    "exit code: 2\n"
                    "root@client:/# cat /etc/hosts\n"
                    "127.0.0.1\tlocalhost\n"
                    "172.17.0.3\tclient"
                ),
                "lang": "console",
            },
            {
                "say": "In a second Mac terminal, compare the two containers' networks. Docker answers container names through a built-in DNS server, but only on user-made networks, and only for containers on the same network. The client container sits on the default network, called bridge, so it cannot see the shopnet phone book.",
                "code": (
                    "$ docker inspect -f '{{range $k, $v := .NetworkSettings.Networks}}{{$k}} {{end}}' cache\n"
                    "shopnet\n"
                    "$ docker inspect -f '{{range $k, $v := .NetworkSettings.Networks}}{{$k}} {{end}}' client\n"
                    "bridge"
                ),
                "lang": "console",
            },
            {
                "say": "Fix it by connecting client to shopnet. Back inside client, the resolver has changed to 127.0.0.11, Docker's built-in DNS server, and the name now resolves.",
                "code": (
                    "$ docker network connect shopnet client\n\n"
                    "root@client:/# grep nameserver /etc/resolv.conf\n"
                    "nameserver 127.0.0.11\n"
                    "root@client:/# getent hosts cache\n"
                    "172.20.0.2      cache"
                ),
                "lang": "console",
            },
            {
                "say": "Read the DNS answer with dig, then test the ports. The answer line has five columns: name, TTL in seconds, class (IN, for internet), type (A) and the address. Port 6379 succeeds. Port 6380 is refused at once: the host is there, but nothing listens on that port.",
                "code": (
                    "root@client:/# dig +noall +answer cache\n"
                    "cache.\t\t\t600\tIN\tA\t172.20.0.2\n"
                    "root@client:/# nc -zv cache 6379\n"
                    "Connection to cache (172.20.0.2) 6379 port [tcp/redis] succeeded!\n"
                    "root@client:/# nc -zv cache 6380\n"
                    "nc: connect to cache (172.20.0.2) port 6380 (tcp) failed: Connection refused"
                ),
                "lang": "console",
            },
            {
                "say": "Look at what changed underneath. client now has two addresses, one per network, each in a /16. Its route table sends each /16 straight out of the matching interface and everything else to the default gateway. That is the route table from this lesson, for real, though your addresses will differ. Exit and clean up with `docker rm -f cache` and `docker network rm shopnet`.",
                "code": (
                    "root@client:/# ip -4 addr | grep inet\n"
                    "    inet 127.0.0.1/8 scope host lo\n"
                    "    inet 172.17.0.3/16 brd 172.17.255.255 scope global eth0\n"
                    "    inet 172.20.0.3/16 brd 172.20.255.255 scope global eth1\n"
                    "root@client:/# ip route\n"
                    "default via 172.17.0.1 dev eth0\n"
                    "172.17.0.0/16 dev eth0 proto kernel scope link src 172.17.0.3\n"
                    "172.20.0.0/16 dev eth1 proto kernel scope link src 172.20.0.3"
                ),
                "lang": "console",
            },
        ],
    },
    "code": [
        {"lang": "python", "title": "netcheck.py", "src": f("netcheck.py"), "run": "python3 netcheck.py github.com 443"},
    ],
    "commands": [
        {"cmd": "ipconfig getifaddr en0", "what": "Mac: print your Wi-Fi address. On Linux, use `hostname -I`."},
        {"cmd": "route -n get default", "what": "Mac: show your default gateway, usually your router. On Linux, use `ip route`."},
        {"cmd": "ip addr", "what": "Linux: list every interface and its addresses with their CIDR prefix."},
        {"cmd": "curl -s https://ifconfig.me; echo", "what": "Print your public address, as the internet sees it (a free third-party service)."},
        {"cmd": "python3 -c \"import ipaddress as i; print(i.ip_network('10.0.0.0/16').num_addresses)\"", "what": "Count the addresses in a CIDR block. Prints 65536."},
        {"cmd": "ping -c 3 1.1.1.1", "what": "Send three ICMP echo requests and show the round-trip times."},
        {"cmd": "traceroute -n 1.1.1.1", "what": "List the routers on the way to an address. Lines of `* * *` often just mean a router stays silent."},
        {"cmd": "dig +short github.com", "what": "Ask DNS for a name's addresses, and print only the answers."},
        {"cmd": "dig github.com MX", "what": "Ask for a specific record type and see the full answer, including the TTL."},
        {"cmd": "dig +trace example.com", "what": "Walk the chain yourself: root, then the TLD servers, then the authoritative servers."},
        {"cmd": "nslookup github.com", "what": "An older DNS lookup tool that also exists on Windows."},
        {"cmd": "dscacheutil -q host -a name github.com", "what": "Mac: show what apps get for a name, including /etc/hosts entries."},
        {"cmd": "lsof -nP -iTCP -sTCP:LISTEN", "what": "Mac and Linux: list programs listening on TCP ports and the address each one is bound to."},
        {"cmd": "ss -tlnp", "what": "Linux: list listening TCP sockets with their process. Install it with `apt install iproute2`."},
        {"cmd": "nc -zv localhost 8000", "what": "Try to open a TCP connection to a port and report success or the error."},
        {"cmd": "python3 netcheck.py github.com 443", "what": "Run this lesson's script: resolve the name, then try a TCP connection, and name the step that failed."},
    ],
    "mistake": (
        "When one service cannot reach another, people restart things and change firewall rules at random. Read the error first. "
        "\"Name or service not known\" means DNS. \"Refused\" means nothing listens on that port. A timeout means something drops the packets, or the address is wrong. "
        "Each points to a different fix, and `nc -zv` or `netcheck.py` tells you which one you have in seconds."
    ),
    "real_world": (
        "PayFlow, a made-up payments company, is moving its ledger database to a new server behind the name `ledger-db.internal`. "
        "A day before, the team lowers that record's TTL from one hour to 60 seconds, so every client picks up the new address within a minute of the switch. "
        "After the move, they raise the TTL again to cut the number of DNS queries."
    ),
    "task": {
        "title": "Take your own network apart",
        "steps": [
            "Find your laptop's private address and your default gateway. Then find your public address. Write down which range the private one is in, and why the two differ.",
            "Read the netmask from `ifconfig en0` and turn it into a /N. Use Python's `ipaddress` to count the addresses in your home network, and to check whether 10.0.3.7 is inside 10.0.2.0/23.",
            "Use dig to find the A, AAAA, MX, NS and TXT records of a domain you use. Run `dig @1.1.1.1 github.com` twice, a few seconds apart, and compare the TTLs.",
            "Run `dig +trace example.com` and name the three kinds of server it talks to, in order.",
            "Add the line `127.0.0.1 myapp.test` to /etc/hosts. Compare `ping -c 1 myapp.test` with `dig +short myapp.test`, explain the difference, then remove the line.",
            "Start two throwaway servers: `python3 -m http.server 9101 --bind 127.0.0.1` and `python3 -m http.server 9102 --bind 0.0.0.0`. Compare them in `lsof`, then try to reach both through your private address.",
            "Save `netcheck.py` from this lesson in `~/code/netlab`. Make it print each of its four results: TCP OK, REFUSED, DNS FAIL and TIMEOUT.",
            "For each of the four results, write one line: which step failed, and what you would check next.",
        ],
        "hints": [
            "Editing /etc/hosts needs sudo: `sudo sh -c 'echo \"127.0.0.1 myapp.test\" >> /etc/hosts'`, and later `sudo sed -i '' '/myapp.test/d' /etc/hosts` removes it.",
            "For REFUSED, try a port where nothing runs. For TIMEOUT, try an address that does not exist on your network, such as 10.255.255.1 port 443; some routers answer 'no route' instead.",
            "A 0xffffff00 netmask has 24 bits set, so it is a /24.",
        ],
        "done_when": "You are done when netcheck.py has printed TCP OK, REFUSED, DNS FAIL and TIMEOUT (or a 'no route' error) for four targets, and you can say which step failed each time.",
    },
    "explain_back": {
        "prompt": "Explain, step by step, what happens when an app connects to `cache:6379`. Mention the resolver, the IP address, the port and the TCP handshake.",
        "answer": (
            "First the app asks the operating system's resolver for the address of cache. It checks /etc/hosts and its cache, then asks a DNS server, such as Docker's built-in one at 127.0.0.11. "
            "With the IP address in hand, the app sends a SYN to that address on port 6379. The server answers SYN-ACK, the app sends ACK, and the TCP connection is open. "
            "If the name is unknown, it fails before any packet is sent. If nothing listens on 6379, the connection is refused, and if a firewall drops the packets, it times out."
        ),
    },
    "recap": [
        "An IP address finds the machine and a port finds the program; private ranges reach the internet through NAT.",
        "/N fixes N bits: /24 is 256 addresses, /16 is 65,536, and a bigger N means a smaller network.",
        "Bind to 0.0.0.0 inside containers; publish to 127.0.0.1 when only your laptop should connect.",
        "DNS goes from the stub resolver to a recursive resolver, then root, TLD and authoritative servers, caching each answer for its TTL.",
        "Unresolved means DNS, refused means no listener, and a timeout means a drop or a wrong address.",
    ],
    "check": [
        {
            "q": "A teammate's app listens on 127.0.0.1:8080 inside a container started with `-p 8080:8080`, and nobody can reach it. What do you suggest?",
            "options": [
                "Publish port 80 instead of port 8080",
                "Add the container's name to /etc/hosts",
                "Switch the app from TCP to UDP",
                "Bind the app to 0.0.0.0 in the container",
            ],
            "answer": 3,
            "why": "Docker forwards published ports to the container's network address, and an app bound to loopback never sees that traffic.",
        },
        {
            "q": "`nc -zv db.internal 22` succeeds at once, but `nc -zv db.internal 5432` waits 30 seconds and then times out. What is the most likely cause?",
            "options": [
                "A firewall drops traffic to port 5432",
                "DNS has no record for db.internal",
                "PostgreSQL is stopped on the server",
                "The server's disk is completely full",
            ],
            "answer": 0,
            "why": "The name resolves and the host answers on port 22, and a stopped database would be refused fast, so silence points to dropped packets.",
        },
        {
            "q": "Your VPC is 10.0.0.0/16 and you need four subnets of equal size, as large as possible. Which prefix do they get?",
            "options": ["/14", "/24", "/18", "/20"],
            "answer": 2,
            "why": "Four equal parts need two more fixed bits, so 16 + 2 = /18, with 16,384 addresses each.",
        },
    ],
    "interview": [
        {
            "q": "What is the difference between TCP and UDP, and when would you pick each?",
            "a": (
                "TCP opens a connection with a three-way handshake, then delivers bytes in order and resends anything lost. That suits HTTP, SSH and databases, where every byte matters. "
                "UDP just sends independent datagrams with no setup and no delivery promise, so it is lighter and has less delay. "
                "It suits small request-response protocols like DNS, and live audio or video, where a late packet is useless anyway. "
                "HTTP/3 runs on QUIC over UDP and builds its own reliability on top."
            ),
        },
        {
            "q": "A service logs 'connection refused' when it calls another service. How do you debug it?",
            "a": (
                "Refused means DNS worked and the target host answered, but nothing accepted the connection on that port. "
                "So I check the target: is the process running, which port does it listen on, and is it bound to 127.0.0.1 instead of 0.0.0.0? "
                "On the target I would run `ss -tlnp` to see the listeners. From the caller I would run `nc -zv` against the exact host and port from the config, to rule out a typo in the port."
            ),
        },
        {
            "q": "Walk me through DNS resolution for a name nobody on your network has looked up recently.",
            "a": (
                "The app asks the operating system's stub resolver, which checks /etc/hosts and its cache, then forwards the query to a recursive resolver. "
                "With an empty cache, the recursive resolver asks a root server, which refers it to the TLD servers, such as those for .com. "
                "The TLD server refers it to the domain's authoritative name servers, which return the record. "
                "The recursive resolver caches the answer for its TTL and returns it, and the stub resolver may cache it too."
            ),
        },
    ],
    "deeper": {
        "minutes": 15,
        "body": (
            "`dig +trace example.com` lets you play recursive resolver yourself. Instead of asking your usual resolver for a finished answer, dig starts at the top and follows each referral. "
            "You see three blocks of output:\n\n"
            "1. A list of root servers, named `a.root-servers.net` to `m.root-servers.net`. dig asks one of them about example.com.\n"
            "2. The root does not know the answer, but it knows who runs .com. It returns NS records for the .com servers. dig asks one of those.\n"
            "3. The .com server returns the NS records for example.com's own name servers. dig asks one of them and finally gets the A record.\n\n"
            "Each block ends with a line saying which server answered and how long it took. Every step is a referral to a server lower in the tree. "
            "Your recursive resolver does exactly this when its cache is empty, and caches each referral so the next lookup skips most of the trip.\n\n"
            "Two details from real life are worth knowing:\n\n"
            "- Negative answers are cached too. If you look up a name before its record exists, resolvers can remember \"no such name\" for a while, so a record you just created can still look missing.\n"
            "- Flushing your own cache only fixes your machine. On a Mac, `sudo dscacheutil -flushcache; sudo killall -HUP mDNSResponder` clears the local cache, but your router's and your provider's caches keep the old answer until the TTL ends.\n\n"
            "If you want to watch DNS from the other side, try [Mess With DNS](https://messwithdns.net/about.html) by Julia Evans. "
            "It gives you a real subdomain to create records on and shows the queries arriving live, so you can create an A record, `dig` it, and see the question land. Records are deleted after a week.\n\n"
            "One more trap. On a Mac, the name `localhost` can resolve to the IPv6 loopback `::1` as well as `127.0.0.1`. "
            "curl tries both, but some tools only try the first. If a server bound to `127.0.0.1` looks down from one tool and up from another, connect to `127.0.0.1` explicitly and compare."
        ),
    },
    "sources": [src(JE_DNS_ZINE), src(DOCKER_PORTS), src(AWS_SUBNET_SIZE), src(MESS_DNS)],
}

# ================================================================ Day 9
d09 = {
    "id": "d09",
    "title": "HTTP, TLS, proxies and load balancers",
    "minutes": 50,
    "goal": "By the end you can read a raw HTTP exchange with curl, explain what TLS proves and how a certificate is checked, and put nginx in front of two app copies as a reverse proxy and load balancer.",
    "guess": {
        "q": "Your browser shows a padlock on https://paypa1-login.example. What does the padlock prove?",
        "options": [
            "The site's owners are honest and safe",
            "A browser vendor reviewed and approved it",
            "Traffic is encrypted to whoever owns that name",
            "The server has passed a malware scan",
        ],
        "answer": 2,
        "why": "A certificate proves control of the domain name, and TLS encrypts the traffic. Anyone who controls paypa1-login.example can get a valid certificate for it.",
    },
    "terms": [
        {"term": "HTTP request", "plain": "A message from a client: a method and path, headers, a blank line and an optional body."},
        {"term": "Status code", "plain": "The three-digit number at the start of every HTTP response, such as 200, 404 or 502."},
        {"term": "Header", "plain": "A `Name: value` line in an HTTP message that carries extra details, such as `Host` or `Content-Type`."},
        {"term": "Idempotent", "plain": "A request that has the same effect whether you send it once or many times, such as GET or DELETE."},
        {"term": "TLS", "plain": "Transport Layer Security: the protocol under HTTPS that encrypts traffic and proves the server's identity."},
        {"term": "Certificate", "plain": "A signed file that says which names a public key belongs to and for how long."},
        {"term": "Reverse proxy", "plain": "A server in front of your apps that receives every request and forwards it to one of them."},
        {"term": "Load balancer", "plain": "A server that spreads incoming requests across several copies of an app and skips the broken ones."},
    ],
    "sections": [
        {
            "h": "HTTP is text with a strict shape",
            "body": (
                "HTTP is the language browsers, curl and apps use to talk to web servers. It runs on top of a TCP connection, which you met on Day 8. "
                "The client sends a request, and the server sends back exactly one response.\n\n"
                "In HTTP/1.1 both are plain text. A request has four parts, in this order:\n\n"
                "1. A request line: the method, the path and the version, such as `GET /healthz HTTP/1.1`.\n"
                "2. Headers: one `Name: value` per line, such as `Host: localhost:8000`.\n"
                "3. A blank line, which says the headers are over.\n"
                "4. An optional body: the data you send, such as JSON for a POST.\n\n"
                "A response has the same shape, with a status line first: `HTTP/1.1 200 OK`. You can see both halves with `curl -v`. "
                "Lines starting with `>` are what curl sent, and lines starting with `<` came back.\n\n"
                "Because it is text, you could type a request by hand. "
                "`printf 'GET / HTTP/1.1\\r\\nHost: example.com\\r\\nConnection: close\\r\\n\\r\\n' | nc example.com 80` does exactly that. The `\\r\\n` pairs are the line endings HTTP requires.\n\n"
                "HTTP is stateless: the server treats each request on its own and does not remember the last one. Logins still work because of cookies. "
                "The server sends a `Set-Cookie` header with a token, and the browser sends it back in a `Cookie` header on every later request.\n\n"
                "HTTP/2 and HTTP/3 keep the same methods, headers and status codes. HTTP/2 packs messages into binary frames and runs many requests at once over one TCP connection. "
                "HTTP/3 does the same over QUIC, which runs on UDP. For debugging you can think in HTTP/1.1 terms, because curl shows you the same fields."
            ),
            "refs": [MDN_MESSAGES, MDN_COOKIES],
        },
        {
            "h": "Methods, and why idempotency matters",
            "body": (
                "The method says what you want to do:\n\n"
                "- GET: read something. It should change nothing.\n"
                "- POST: create something or submit data, such as a payment.\n"
                "- PUT: replace something with the body you send.\n"
                "- PATCH: change part of something.\n"
                "- DELETE: remove something.\n"
                "- HEAD: like GET, but return only the headers.\n"
                "- OPTIONS: ask what is allowed. Browsers send it before some cross-site requests.\n\n"
                "Two words describe methods. A safe method changes nothing on the server: GET and HEAD. "
                "An **idempotent** method has the same effect whether you send it once or five times: GET, HEAD, PUT and DELETE. Deleting order 42 twice leaves it just as deleted.\n\n"
                "POST is neither. Send \"charge this card 20 euros\" twice, and you may charge twice.\n\n"
                "This matters to operators because networks fail halfway. A client sends a request, the connection drops, and nobody knows whether the server got it. "
                "Retrying an idempotent request is safe. Retrying a POST is not, unless the API gives you a way to make it safe. "
                "Payment APIs often accept an idempotency key: a unique ID per payment, so the server can ignore a repeat. "
                "Proxies know this too. nginx, for example, will not retry a POST on another server by default once it has sent it to one."
            ),
            "refs": [MDN_OVERVIEW],
        },
        {
            "h": "Status codes: what each one tells an operator",
            "body": (
                "Every response starts with a three-digit status code, and the first digit gives the family:\n\n"
                "- 1xx: information, rarely seen.\n"
                "- 2xx: success.\n"
                "- 3xx: go somewhere else.\n"
                "- 4xx: the client did something wrong.\n"
                "- 5xx: the server side failed.\n\n"
                "These are the ones you will read in logs and dashboards, with what each one suggests:\n\n"
                "- 200 OK and 201 Created: it worked. 201 means a POST made something new.\n"
                "- 301 and 302: redirects. The `Location` header says where to go, and 301 is permanent.\n"
                "- 304 Not Modified: your cached copy is still good, so no body is sent.\n"
                "- 400 Bad Request: the request itself is broken, such as invalid JSON.\n"
                "- 401 Unauthorized: who are you? Credentials are missing or wrong.\n"
                "- 403 Forbidden: I know who you are, and you may not do this.\n"
                "- 404 Not Found: no such path. Look for a typo or a missing route.\n"
                "- 429 Too Many Requests: slow down, because a rate limit kicked in.\n"
                "- 500 Internal Server Error: the app crashed or threw an exception.\n"
                "- 502 Bad Gateway: a proxy could not get a good answer from the app behind it.\n"
                "- 503 Service Unavailable: the server is up but cannot serve right now, like hello-devops's `/readyz` while Redis is down.\n"
                "- 504 Gateway Timeout: a proxy waited for the app and gave up.\n\n"
                "Notice the last three. 502, 503 and 504 usually come from a proxy or load balancer, not from your code. "
                "A 502 means the app was unreachable or answered with garbage. You will cause one on purpose in today's hands-on."
            ),
            "refs": [MDN_STATUS],
        },
        {
            "h": "Headers that matter, and curl as your microscope",
            "body": (
                "Headers carry the details. A few matter every day:\n\n"
                "- `Host`: which site you want. One server address can host many sites, and this header picks one.\n"
                "- `Content-Type`: what the body is, such as `application/json`.\n"
                "- `Authorization`: credentials, such as a bearer token. Never write it to a log.\n"
                "- `Cache-Control`: who may cache the response, and for how long.\n"
                "- `X-Forwarded-For`: the original client's address, added by proxies along the way.\n\n"
                "curl is the tool you will use most, and a handful of flags cover nearly everything:\n\n"
                "- `-v` shows the whole conversation, including the DNS, TCP and TLS steps.\n"
                "- `-i` prints the response headers with the body, and `-I` sends a HEAD request for headers only.\n"
                "- `-L` follows redirects.\n"
                "- `-X`, `-H` and `-d` set the method, add a header and send a body.\n"
                "- `-o /dev/null -s -w '%{http_code}'` prints only the status code, which is handy in scripts.\n"
                "- `-w` with timing variables shows how long DNS, connect, TLS and the first byte took.\n"
                "- `--resolve name:port:address` skips DNS and sends that name to an address you choose.\n\n"
                "`--resolve` is a good trick to know. It lets you test a new server under its real name before you change DNS, because the `Host` header and TLS still use the name from the URL."
            ),
            "refs": [CURL_WRITEOUT],
        },
        {
            "h": "TLS: what HTTPS adds",
            "body": (
                "HTTPS is HTTP inside a TLS connection. TLS (Transport Layer Security) gives you three things:\n\n"
                "- Confidentiality: nobody on the path can read the traffic.\n"
                "- Integrity: nobody can change it without the change being detected.\n"
                "- Authentication: the server proves it holds the private key for a certificate that names this host.\n\n"
                "Before any HTTP flows, the client and the server run a handshake. In TLS 1.3, the current version, it takes one round trip:\n\n"
                "1. The client sends ClientHello. It lists the ciphers (encryption methods) it supports and its half of a key exchange. It also names the host it wants (called SNI) and the HTTP versions it speaks (called ALPN).\n"
                "2. The server answers with ServerHello and its half of the key exchange. Then, already encrypted, it sends its certificate and a signature that proves it holds the matching private key.\n"
                "3. The client checks the certificate: the right name, still valid, and signed by someone it trusts.\n"
                "4. Both sides compute the same session keys from the two halves. Everything after this, including the HTTP request, is encrypted.\n\n"
                "You can watch it happen. `curl -v https://...` prints a line for each handshake message, and you read them in the worked example.\n\n"
                "Know what TLS does not hide. The server's IP address is visible to everyone on the path, and usually so is the host name, because SNI is sent before encryption starts. "
                "A newer extension, Encrypted Client Hello, hides it where both sides support it."
            ),
            "refs": [CP_TLS, CF_TLS, HPBN_TLS],
        },
        {
            "h": "Certificates, CAs and Let's Encrypt",
            "body": (
                "A certificate is a signed statement: \"this public key belongs to these names, from this date to that date\". "
                "The names live in a field called Subject Alternative Name (SAN), such as `DNS:localhost`. A certificate authority (CA) signs it.\n\n"
                "Your operating system and browser ship a trust store: a list of root CAs they trust. Roots rarely sign server certificates directly. "
                "They sign intermediate CAs, and an intermediate signs the server's certificate. The server sends its certificate plus the intermediates, and the client follows that chain up to a root it already trusts. "
                "If any link is missing, expired or made out to another name, the connection fails.\n\n"
                "Let's Encrypt is a free CA run by a non-profit. It issues certificates automatically through a protocol called ACME. To prove you control a domain, you pass a challenge:\n\n"
                "- HTTP-01: serve a token at a known URL on port 80. It cannot give you a wildcard certificate.\n"
                "- DNS-01: publish a TXT record. It is the only way to get a wildcard such as `*.example.com`.\n\n"
                "Certificates expire, and on purpose they expire sooner each year. Let's Encrypt certificates last 90 days today. "
                "Its default lifetime drops to 64 days on February 10, 2027, and to 45 days on February 16, 2028. Nobody should renew those by hand, so renewal must be automated and watched.\n\n"
                "The padlock proves less than people think. Let's Encrypt gives a certificate to anyone who controls a domain, including `paypa1-login.example`. "
                "TLS says \"you are talking privately to whoever controls this name\", and nothing about whether they are honest.\n\n"
                "For `localhost`, no public CA will issue a certificate, because nobody uniquely owns that name. You make your own, as in the worked example."
            ),
            "refs": [LE_CHALLENGES, LE_LIFETIMES, LE_LOCALHOST],
        },
        {
            "h": "Proxies, load balancers and the rest of the path",
            "body": (
                "In production, a request rarely goes straight to your app. It passes through servers in the middle.\n\n"
                "A **reverse proxy** sits in front of your apps and receives every request on their behalf, then forwards each one to an app behind it. Common ones are nginx, Envoy, Caddy and Traefik. "
                "A forward proxy is the opposite: it acts for clients, such as a company proxy that all outgoing traffic must pass through.\n\n"
                "Reverse proxies take on jobs each app should not repeat:\n\n"
                "- TLS termination: the proxy holds the certificate and talks plain HTTP to the apps behind it.\n"
                "- Routing by host or path: `/api` goes to one service and `/` to another.\n"
                "- Load balancing: spreading requests across several copies of an app.\n"
                "- Health checks: sending traffic only to copies that answer.\n"
                "- Rate limiting: answering 429 when one client sends too much.\n\n"
                "nginx calls the app servers behind it upstreams, and today's `lb.conf` lists them in an `upstream` block.\n\n"
                "A load balancer works at one of two levels. A layer 4 balancer sees only addresses and ports and forwards whole TCP connections, so it is fast and works for any protocol. "
                "A layer 7 balancer reads the HTTP request, so it can route on paths, headers and cookies. An L7 balancer is really a reverse proxy with several backends. "
                "Sticky sessions are an L7 feature: one user keeps landing on the same copy, usually through a cookie. I would rather keep apps free of in-memory state, so any copy can serve any request.\n\n"
                "Two more pieces sit further out. A CDN (content delivery network) is a worldwide set of caching proxies that serves copies of your files from near the user, and `Cache-Control` says what it may keep. "
                "A firewall allows or denies traffic by address, port and protocol before it reaches the proxy.\n\n"
                "Kubernetes has the same pieces under new names: Services balance connections on Day 33, and the Gateway API routes HTTP on Day 36."
            ),
            "refs": [CF_LB, MDN_PROXY],
        },
    ],
    "analogy": (
        "A reverse proxy is the receptionist of an office building. Every visitor talks to the receptionist first. The receptionist checks their papers at the door (TLS termination), "
        "looks at what they want (the path and headers) and walks them to a free clerk (load balancing). If no clerk is at a desk, the receptionist says so: that is the 502. "
        "TLS is the sealed envelope plus the check of the building's papers on the way in. "
        "The picture breaks on scale and memory: a real receptionist remembers yesterday's visitors, while HTTP forgets each request unless a cookie reminds it."
    ),
    "diagram": D09_SVG,
    "diagram_caption": "nginx ends TLS and forwards plain HTTP to whichever app copy answers. With no copy left, it returns 502 Bad Gateway.",
    "worked": {
        "title": "HTTPS on localhost, through nginx",
        "steps": [
            {
                "say": "Make a folder and a certificate for localhost. Your Mac's openssl is a different build (LibreSSL) with different flags, so run real OpenSSL from the python:3.14-slim image instead. The flag `-x509` makes a self-signed certificate, `-nodes` leaves the key unencrypted, and `-addext` adds the names. While it makes the key, openssl prints a line of dots and plus signs; that is normal.",
                "code": (
                    "$ mkdir -p ~/code/netlab/tls && cd ~/code/netlab/tls\n"
                    "$ docker run --rm -v \"$PWD\":/certs -w /certs python:3.14-slim \\\n"
                    "    openssl req -x509 -newkey rsa:2048 -nodes -keyout localhost.key -out localhost.crt \\\n"
                    "    -days 7 -subj /CN=localhost -addext \"subjectAltName=DNS:localhost,IP:127.0.0.1\"\n"
                    "$ ls\n"
                    "localhost.crt  localhost.key"
                ),
                "lang": "console",
            },
            {
                "say": "Save `tls.conf` from this lesson in the same folder. Start a tiny app, `traefik/whoami`, which answers by printing the request it received. Then start nginx with the config and the certificate mounted read-only. Only nginx publishes a port, and only on 127.0.0.1, so the app is reachable through nginx alone.",
                "code": (
                    "$ docker network create weblab\n"
                    "$ docker run -d --rm --name whoami --network weblab traefik/whoami\n"
                    "$ docker run -d --rm --name tls --network weblab -p 127.0.0.1:8443:443 \\\n"
                    "    -v \"$PWD/tls.conf:/etc/nginx/conf.d/default.conf:ro\" -v \"$PWD:/etc/nginx/certs:ro\" nginx:alpine\n"
                    "$ docker ps --format '{{.Names}}\\t{{.Ports}}'\n"
                    "tls\t80/tcp, 127.0.0.1:8443->443/tcp\n"
                    "whoami\t80/tcp"
                ),
                "lang": "console",
            },
            {
                "say": "Ask for the page. curl refuses, and it is right to. The certificate is signed by itself, not by a CA in your trust store, so curl cannot tell it from an attacker's. The wording on your Mac may differ a little.",
                "code": (
                    "$ curl -sS https://localhost:8443/\n"
                    "curl: (60) SSL certificate problem: self-signed certificate\n"
                    "More details here: https://curl.se/docs/sslcerts.html"
                ),
                "lang": "console",
            },
            {
                "say": "Tell curl to trust exactly this certificate with `--cacert`. It still checks the name and the dates; it just adds one trusted signer. Now read whoami's answer. RemoteAddr is nginx, not you. Your address is in X-Forwarded-For. Here that is Docker's gateway, because traffic from your Mac enters the network there. X-Forwarded-Proto says the client used https, though the app only saw plain HTTP.",
                "code": (
                    "$ curl -sS --cacert localhost.crt https://localhost:8443/\n"
                    "Hostname: 976fa83e67d8\n"
                    "IP: 127.0.0.1\n"
                    "IP: 172.22.0.2\n"
                    "RemoteAddr: 172.22.0.3:35000\n"
                    "GET / HTTP/1.1\n"
                    "Host: localhost\n"
                    "User-Agent: curl/8.5.0\n"
                    "Accept: */*\n"
                    "X-Forwarded-For: 172.22.0.1\n"
                    "X-Forwarded-Proto: https\n"
                    "X-Real-Ip: 172.22.0.1"
                ),
                "lang": "console",
            },
            {
                "say": "Watch the handshake with `-v`. It prints about 40 lines; these are the ones to read. First comes ClientHello, offering HTTP/2 and HTTP/1.1. Then the server's hello, its certificate and its proof of the key. Last, the agreed TLS version and cipher, and the certificate check passing on name and dates. Your Mac's curl words these lines a little differently.",
                "code": (
                    "$ curl -v --cacert localhost.crt -o /dev/null https://localhost:8443/\n"
                    "* ALPN: curl offers h2,http/1.1\n"
                    "* TLSv1.3 (OUT), TLS handshake, Client hello (1):\n"
                    "* TLSv1.3 (IN), TLS handshake, Server hello (2):\n"
                    "* TLSv1.3 (IN), TLS handshake, Certificate (11):\n"
                    "* TLSv1.3 (IN), TLS handshake, CERT verify (15):\n"
                    "* TLSv1.3 (IN), TLS handshake, Finished (20):\n"
                    "* SSL connection using TLSv1.3 / TLS_AES_256_GCM_SHA384 / X25519 / RSASSA-PSS\n"
                    "* ALPN: server accepted http/1.1\n"
                    "*  subjectAltName: host \"localhost\" matched cert's \"localhost\"\n"
                    "*  expire date: Nov  6 05:02:16 2026 GMT\n"
                    "*  SSL certificate verify ok.\n"
                    "< HTTP/1.1 200 OK"
                ),
                "lang": "console",
            },
            {
                "say": "Inspect the certificate the server sends, the way you would for any real site. Subject and issuer are the same name: that is what self-signed means. The dates show the 7 days you asked for. On a Mac the subject line looks slightly different, such as `subject= /CN=localhost`.",
                "code": (
                    "$ echo | openssl s_client -connect 127.0.0.1:8443 -servername localhost 2>/dev/null \\\n"
                    "    | openssl x509 -noout -subject -issuer -dates\n"
                    "subject=CN = localhost\n"
                    "issuer=CN = localhost\n"
                    "notBefore=Oct 30 05:02:16 2026 GMT\n"
                    "notAfter=Nov  6 05:02:16 2026 GMT"
                ),
                "lang": "console",
            },
            {
                "say": "Clean up. Both containers were started with `--rm`, so stopping them also removes them. Keep the folder if you want to repeat the experiment.",
                "code": (
                    "$ docker stop tls whoami\n"
                    "tls\n"
                    "whoami\n"
                    "$ docker network rm weblab\n"
                    "weblab"
                ),
                "lang": "console",
            },
        ],
    },
    "code": [
        {"lang": "text", "title": "tls.conf", "src": f("tls.conf"),
         "run": "docker run -d --rm --name tls --network weblab -p 127.0.0.1:8443:443 -v \"$PWD/tls.conf:/etc/nginx/conf.d/default.conf:ro\" -v \"$PWD:/etc/nginx/certs:ro\" nginx:alpine"},
        {"lang": "text", "title": "lb.conf", "src": f("lb.conf"),
         "run": "docker run -d --name proxy --network netlab -p 127.0.0.1:8080:80 -v \"$PWD/lb.conf:/etc/nginx/conf.d/default.conf:ro\" nginx:alpine"},
        {"lang": "text", "title": "curl-timing.txt", "src": f("curl-timing.txt"),
         "run": "curl -s -o /dev/null -w \"@curl-timing.txt\" https://example.com"},
    ],
    "commands": [
        {"cmd": "curl -v http://localhost:8000/", "what": "Show the whole HTTP conversation: lines with > were sent, lines with < came back."},
        {"cmd": "curl -i localhost:8000/healthz", "what": "Print the response headers, then the body."},
        {"cmd": "curl -I https://github.com", "what": "Send a HEAD request and print only the response headers."},
        {"cmd": "curl -sIL http://github.com", "what": "Follow redirects and print the headers of every hop."},
        {"cmd": "curl -X POST -H 'Content-Type: application/json' -d '{\"amount\": 20}' localhost:8000/", "what": "Send a POST with a JSON body. hello-devops answers 405, because / only allows GET."},
        {"cmd": "curl -s -o /dev/null -w '%{http_code}\\n' localhost:8000/nope", "what": "Print only the status code (here 404). Handy in scripts and health checks."},
        {"cmd": "curl -s -o /dev/null -w \"@curl-timing.txt\" https://example.com", "what": "Time each step of a request: DNS, connect, TLS, first byte, total."},
        {"cmd": "curl --resolve hello.test:8080:127.0.0.1 http://hello.test:8080/", "what": "Skip DNS: send this name to an address you choose, keeping the name in Host and TLS."},
        {"cmd": "curl --cacert localhost.crt https://localhost:8443/", "what": "Trust one extra certificate for this request, and still verify name and dates."},
        {"cmd": "docker run --rm -v \"$PWD\":/certs -w /certs python:3.14-slim openssl req -x509 -newkey rsa:2048 -nodes -keyout localhost.key -out localhost.crt -days 7 -subj /CN=localhost -addext \"subjectAltName=DNS:localhost,IP:127.0.0.1\"", "what": "Make a self-signed certificate for localhost with real OpenSSL in a container."},
        {"cmd": "echo | openssl s_client -connect github.com:443 -servername github.com 2>/dev/null | openssl x509 -noout -subject -issuer -dates", "what": "Fetch a site's certificate and print who it is for, who signed it and when it expires."},
        {"cmd": "openssl x509 -in localhost.crt -noout -text", "what": "Print everything in a certificate file, including the Subject Alternative Names."},
        {"cmd": "openssl x509 -in localhost.crt -noout -checkend 1209600", "what": "Exit with 1 if the certificate expires within 14 days (1,209,600 seconds). Good for a monitoring script."},
        {"cmd": "docker logs proxy", "what": "Read nginx's log, which names the upstream it failed to reach and why."},
        {"cmd": "docker rm -f app1 app2 proxy && docker network rm netlab", "what": "Remove the hands-on containers and their network."},
    ],
    "mistake": (
        "When curl fails with a certificate error, many people add `-k` (or the same switch in their HTTP library) and move on. "
        "That turns off the identity check, so you would talk to an attacker just as happily, and the setting tends to reach production. "
        "Fix the trust instead: give the tool the right CA file with `--cacert`, fix the server's chain, or use the right host name."
    ),
    "real_world": (
        "At PayFlow, a made-up payments company, every public request first reaches a layer 7 load balancer that holds the TLS certificates, renewed automatically. "
        "It routes `/api/payments` to the payments service and spreads requests over copies in two zones, using health checks to skip broken ones. "
        "The payments API requires an idempotency key on every POST, so a retry after a dropped connection never charges a card twice."
    ),
    "task": {
        "title": "Load-balance two copies of hello-devops",
        "steps": [
            "Make `~/code/netlab/lb`, save `lb.conf` from this lesson there, and create a Docker network called `netlab`.",
            "Start app1 from your hello-devops folder: `docker run -d --name app1 --network netlab -e GREETING=\"Hello from app1\" -v ~/code/hello-devops:/app:ro -w /app python:3.14-slim sh -c \"pip install -q -r requirements.txt && python app.py\"`. Start app2 the same way, with its own name and greeting.",
            "Wait until `docker logs app1` and `docker logs app2` both show \"Running on all addresses (0.0.0.0)\". Explain to yourself why that line matters.",
            "Start nginx as a container called `proxy` on the same network, with `lb.conf` mounted and port 8080 published on 127.0.0.1 only.",
            "Send ten requests to `localhost:8080` and count how many each copy answered. Is it a perfect 5 and 5?",
            "Send a POST and a request for a path that does not exist. Write down both status codes and which side (client or server) each one blames.",
            "Stop app2. Time the next few requests with `curl -s -o /dev/null -w '%{http_code} %{time_total}\\n' localhost:8080/`. Explain the slow one, using the comments in `lb.conf`.",
            "Stop app1 too. Get a 502, then find the reason in `docker logs proxy`.",
            "Clean up the three containers and the network.",
        ],
        "hints": [
            "Counting: `for i in $(seq 10); do curl -s localhost:8080/ | jq -r .message; done | sort | uniq -c` uses the Part 1 tools you already know.",
            "If nginx exits at once with \"host not found in upstream\", it started before app1 or app2 existed. Start the apps first, then nginx.",
            "`docker stop app2` takes about 10 seconds because Python, running as PID 1 in the container, ignores SIGTERM, so Docker waits and then sends SIGKILL (Day 6).",
        ],
        "done_when": "You are done when you have seen answers from both app1 and app2 through localhost:8080, then a 502 Bad Gateway after stopping both, and you can explain each result.",
    },
    "explain_back": {
        "prompt": "Explain what nginx did for one request in today's labs, in 3 to 4 sentences. Mention TLS termination, the upstream and what a 502 means.",
        "answer": (
            "nginx received the client's HTTPS connection on port 443, ran the TLS handshake with its certificate and decrypted the request, which is TLS termination. "
            "It then picked one of the upstream servers, app1 or app2, and forwarded the request over plain HTTP on port 8000. On the way it added X-Forwarded-For, so the app knows the real client. "
            "When an upstream did not answer within the connect timeout, nginx tried the other one. "
            "When no upstream could answer, nginx itself replied 502 Bad Gateway, which means the proxy was fine but the app behind it was not."
        ),
    },
    "recap": [
        "An HTTP message is a start line, headers, a blank line and an optional body, and `curl -v` shows all of it.",
        "GET, PUT and DELETE are idempotent and safe to retry; POST is not, unless the API takes an idempotency key.",
        "4xx blames the client and 5xx the server; 502, 503 and 504 usually come from proxies.",
        "TLS encrypts and proves control of a name; the client follows the certificate chain to a trusted root.",
        "Certificates are getting shorter-lived, so renewal must be automated and monitored.",
        "A reverse proxy ends TLS, routes and load-balances; L4 sees ports, L7 sees HTTP.",
    ],
    "check": [
        {
            "q": "During a slow database migration, users get 504 Gateway Timeout from the load balancer. What does that tell you first?",
            "options": [
                "The app answers too slowly, not that it is down",
                "The users' browsers sent broken requests",
                "The TLS certificate on the balancer expired",
                "DNS points the domain at the wrong address",
            ],
            "answer": 0,
            "why": "504 means the proxy reached the app but gave up waiting for an answer, which fits a slow database.",
        },
        {
            "q": "A POST /payments request timed out, the client retried it, and the customer was charged twice. Which fix addresses the cause?",
            "options": [
                "Change the method from POST to GET",
                "Turn off retries in every client",
                "Raise the proxy's timeout to 5 minutes",
                "Send an idempotency key the server checks",
            ],
            "answer": 3,
            "why": "POST is not idempotent, so the server needs a unique key per payment to recognise and ignore the repeat.",
        },
        {
            "q": "A logged-in user tries to delete another team's project. The API answers 401. Which code fits better?",
            "options": ["400 Bad Request", "403 Forbidden", "404 Not Found", "500 Server Error"],
            "answer": 1,
            "why": "401 means 'who are you?'. This user is known but not allowed, which is what 403 says.",
        },
    ],
    "interview": [
        {
            "q": "What happens when you type a URL into a browser and press Enter?",
            "a": (
                "The browser resolves the host name through DNS, using a cached answer if it has one. "
                "It opens a TCP connection to that address on port 443 and runs a TLS handshake. In the handshake, the server proves its identity with a certificate, which the browser checks against its trust store. "
                "It then sends an HTTP GET, usually to a load balancer or reverse proxy that ends TLS and forwards the request to one healthy app server. "
                "The response comes back with a status code, headers and a body, and the browser renders the page and fetches whatever else it references."
            ),
        },
        {
            "q": "What is the difference between a layer 4 and a layer 7 load balancer?",
            "a": (
                "A layer 4 balancer works with IP addresses and ports and forwards whole TCP or UDP connections without reading their contents. It is fast and protocol-agnostic. "
                "A layer 7 balancer understands HTTP, so it can route by host, path, headers or cookies, end TLS, add headers like X-Forwarded-For and run HTTP health checks. "
                "I would use L7 for web traffic and L4 for things like databases or custom TCP protocols."
            ),
        },
        {
            "q": "What is TLS termination, and where would you do it?",
            "a": (
                "TLS termination means a proxy or load balancer decrypts HTTPS and passes the request on, often as plain HTTP. "
                "It keeps certificates and renewal in one place and lets the proxy route on HTTP details. "
                "The trade-off is that traffic behind the proxy is unencrypted unless you re-encrypt it. In a shared or regulated network, I would use TLS to the backends too. "
                "Most teams terminate at the edge load balancer or the Kubernetes gateway."
            ),
        },
    ],
    "deeper": {
        "minutes": 12,
        "body": (
            "Certificate lifetimes are shrinking on a schedule, and it changes how operators work. "
            "Let's Encrypt certificates last 90 days today. Its default profile moves to 64 days on February 10, 2027, and to 45 days on February 16, 2028. "
            "An opt-in profile already issues 45-day certificates, and another issues certificates that last about six days. "
            "Industry rules will cap every public certificate at 47 days from March 15, 2029. "
            "The plans and the reasons are in Let's Encrypt's [certificate lifetimes page](https://letsencrypt.org/docs/cert-lifetimes/).\n\n"
            "What this means in practice:\n\n"
            "- Never renew by hand. Use an ACME client that renews on its own, or a platform feature that does, such as cert-manager in Kubernetes.\n"
            "- Renew early. Let's Encrypt suggests renewing at about two thirds of a certificate's lifetime, or following its renewal-information service, called ARI.\n"
            "- Hunt for hard-coded intervals. A cron job that renews every 60 or 80 days will break when certificates last 45. Let's Encrypt suggests grepping for those numbers.\n"
            "- Monitor expiry anyway. `openssl x509 -noout -checkend 1209600` exits non-zero when a certificate expires within 14 days, which makes a simple alert.\n\n"
            "Two more changes make old tutorials wrong. First, Let's Encrypt switched off its OCSP service on August 6, 2025, and now publishes revocation only through certificate revocation lists (CRLs). "
            "Guides that run `openssl ocsp` against Let's Encrypt are out of date. "
            "Second, Let's Encrypt announced a new chain of root and intermediate CAs in late 2025. So do not hard-code intermediate names such as R3 or R10 in scripts or firewall rules, because the names change.\n\n"
            "If you want the mechanics of the handshake in more depth, the TLS chapter of [High Performance Browser Networking](https://hpbn.co/transport-layer-security-tls/) is free and still clear. "
            "It was written before TLS 1.3, so remember that 1.3 cut the handshake to one round trip."
        ),
    },
    "sources": [src(MDN_OVERVIEW), src(LE_LIFETIMES), src(CF_TLS), src(MDN_PROXY)],
}

# ================================================================ Day 10
d10 = {
    "id": "d10",
    "title": "The cloud: regions, core services, IAM and cost",
    "minutes": 50,
    "goal": "By the end you can describe what a cloud provider rents you, design a small two-zone network with subnets, routes and firewalls, write a least-privilege policy, and avoid a surprise bill.",
    "guess": {
        "q": "You set an AWS budget of $5 with an email alert. Your forgotten test servers reach $5 this month. What happens?",
        "options": [
            "AWS stops the servers when you reach $5",
            "AWS deletes the servers and keeps your data",
            "Your bill is capped at $5 for that month",
            "You get an email, and the servers keep running",
        ],
        "answer": 3,
        "why": "A budget alert only notifies you. The servers keep running and billing until you delete them.",
    },
    "terms": [
        {"term": "Region", "plain": "A geographic area where a cloud provider runs data centers, such as Frankfurt."},
        {"term": "Availability zone (AZ)", "plain": "One or more separate data centers inside a region, with their own power and network."},
        {"term": "VPC", "plain": "Virtual private cloud: your own private network inside a cloud provider, with a CIDR block you choose."},
        {"term": "Subnet", "plain": "A smaller block of addresses inside a VPC; in AWS each subnet lives in one availability zone."},
        {"term": "Security group", "plain": "A stateful, allow-only firewall attached to a cloud machine's network interface."},
        {"term": "IAM role", "plain": "A set of permissions that a person or a machine takes on for a while, with credentials that expire."},
        {"term": "Least privilege", "plain": "Giving each person or job only the permissions it needs, and nothing more."},
        {"term": "Shared responsibility", "plain": "The split of security work: the provider secures the cloud itself, and you secure what you put in it."},
    ],
    "sections": [
        {
            "h": "What the cloud is",
            "body": (
                "The cloud is renting computers, storage and ready-made services from a provider, by the second or the hour. You never see the hardware. "
                "You ask for a machine on a website or through an API, and a minute later it exists. When you delete it, the bill for it stops.\n\n"
                "Every click in a cloud console is really an API call. That one fact explains a lot of this course. "
                "Anything you can click, a program can do. Terraform (Part 6) creates cloud resources from code by calling the same APIs, and a pipeline can run Terraform.\n\n"
                "Cloud services differ in how much the provider runs for you:\n\n"
                "- IaaS (infrastructure as a service): you rent virtual machines, disks and networks, and you install and patch the operating system. Example: AWS EC2.\n"
                "- PaaS (platform as a service): you hand over code or a container, and the provider runs it. Examples: Google Cloud Run, Azure Container Apps.\n"
                "- SaaS (software as a service): finished software that you just use, such as GitHub or Gmail.\n"
                "- Serverless functions: you upload one function, it runs on each event, and you pay per request and for the time it runs. It scales to zero. Example: AWS Lambda.\n\n"
                "Managed services sit in between. A managed database such as AWS RDS gives you PostgreSQL without you running the server: the provider patches it, backs it up and fails it over. "
                "You still own the schema, the queries and who may connect."
            ),
            "refs": [FCC_CLF],
        },
        {
            "h": "Regions and availability zones",
            "body": (
                "Providers group their data centers by place. A **region** is a geographic area, such as AWS's `eu-central-1` in Frankfurt or Google's `us-central1` in Iowa. "
                "Inside a region sit several availability zones (AZs). AWS describes an AZ as one or more separate data centers with their own power, networking and connectivity, linked to the other AZs by fast private fiber.\n\n"
                "Why the split? Because things fail at every size:\n\n"
                "- One server dies: run two copies.\n"
                "- One data center loses power or floods: run copies in two or more AZs.\n"
                "- A whole region has a bad day: rare, and only the most critical systems plan for it.\n\n"
                "For most apps, two or three AZs in one region is the right amount. The AZs are close enough for fast traffic between them and far enough apart not to fail together.\n\n"
                "To pick a region, answer three questions:\n\n"
                "1. Where are your users? Closer means lower latency.\n"
                "2. Where must the data live? Laws and contracts can require a country or region.\n"
                "3. What does it cost? Prices differ between regions.\n\n"
                "One trap catches nearly every beginner. A cloud console shows one region at a time, and a server you created in another region keeps running and billing, out of sight. "
                "Pick one region for all your learning and stay there."
            ),
            "refs": [AWS_REGIONS],
        },
        {
            "h": "The core service map across AWS, Azure and Google Cloud",
            "body": (
                "The three big providers sell the same kinds of building blocks under different names. Learn the category first, and the names follow:\n\n"
                "- Virtual machines: EC2 (AWS), Virtual Machines (Azure), Compute Engine (Google Cloud).\n"
                "- Managed Kubernetes: EKS, AKS, GKE.\n"
                "- Containers without a cluster: Fargate, Container Apps, Cloud Run.\n"
                "- Functions: Lambda, Azure Functions, Cloud Run functions.\n"
                "- Object storage for files: S3, Blob Storage, Cloud Storage.\n"
                "- Managed SQL databases: RDS, Azure SQL Database and Azure Database for PostgreSQL, Cloud SQL.\n"
                "- Private networks: VPC, Virtual Network (VNet), VPC.\n"
                "- DNS: Route 53, Azure DNS, Cloud DNS.\n"
                "- Load balancers: Elastic Load Balancing, Azure Load Balancer and Application Gateway, Cloud Load Balancing.\n"
                "- Identity and access: IAM, Microsoft Entra ID with Azure RBAC, Cloud IAM.\n"
                "- Monitoring and logs: CloudWatch, Azure Monitor, Cloud Monitoring and Cloud Logging.\n\n"
                "Similar names do not mean identical behaviour, and Google's own comparison page warns about this. "
                "One example: in Google Cloud a VPC network is global and its subnets are regional, while an AWS VPC lives in a single region.\n\n"
                "Names also change. Google's Cloud Functions became Cloud Run functions, for example. Check the current docs before you trust any table, including this one."
            ),
            "refs": [GCP_COMPARE],
        },
        {
            "h": "Networking in the cloud: VPCs, subnets and routes",
            "body": (
                "A VPC (virtual private cloud) is your own private network inside the provider. Everything from Day 8 comes back here, except that now you set it up yourself.\n\n"
                "You give the VPC a private CIDR block, such as `10.0.0.0/16`. Then you split it into subnets: smaller blocks such as `10.0.1.0/24`. "
                "In AWS each subnet lives in exactly one AZ, so an app in two AZs needs subnets in both. "
                "AWS also keeps 5 addresses in every subnet (the first four and the last), so a /24 gives you 251 usable addresses, not 256.\n\n"
                "What makes a subnet public or private is its route table, not its name:\n\n"
                "- Every route table has a local route, such as `10.0.0.0/16` to `local`, so all subnets in the VPC can reach each other.\n"
                "- A public subnet adds `0.0.0.0/0` to an internet gateway. `0.0.0.0/0` means every address, so this is the default route. Machines here can have public addresses and be reached from the internet.\n"
                "- A private subnet adds `0.0.0.0/0` to a NAT gateway instead. Its machines can reach out, for example to download packages, but nobody outside can start a connection to them.\n\n"
                "That is your home router from Day 8 again. The internet gateway is the front door, and the NAT gateway is the switchboard that lets staff call out. "
                "The usual layout puts load balancers in public subnets, and apps and databases in private ones."
            ),
            "refs": [AWS_SUBNET_SIZE, GCP_SUBNETS],
        },
        {
            "h": "Cloud firewalls: security groups and network ACLs",
            "body": (
                "AWS gives you two firewalls, and they behave differently. Mixing them up leads to a classic puzzle: the request arrives, but the reply never gets back.\n\n"
                "A security group is a firewall attached to each machine (more exactly, to its network interface). Its rules only allow, and anything not allowed is blocked. "
                "It is stateful: it tracks connections, so the reply to an allowed request gets out without a rule of its own. "
                "A rule can also name another security group as its source. \"Allow port 8000 from the load balancer's group\" keeps working when the load balancer's addresses change.\n\n"
                "A network ACL (NACL) guards a whole subnet. It is stateless: it judges every packet on its own, with no memory of connections. "
                "Its numbered rules can allow or deny, and the first match wins.\n\n"
                "Stateless has a cost. Say a NACL allows inbound port 443. The server's reply goes back to the client's ephemeral port, somewhere between 1024 and 65535. "
                "If the NACL has no outbound rule for those ports, the reply is dropped. The request arrived, the app answered, and the client still times out. "
                "A security group would have let the reply out by itself.\n\n"
                "AWS describes NACLs as a coarse, extra guard for whole subnets, and for most work security groups do the job. Azure's network security groups are stateful too. "
                "Whatever the cloud, start with nothing open and add only what each layer needs. Never open a database port to `0.0.0.0/0`."
            ),
            "refs": [AWS_NACL, AWS_CONNTRACK],
        },
        {
            "h": "IAM: who may do what",
            "body": (
                "IAM (identity and access management) answers one question for every API call: may this caller do this action on this resource? The callers are called principals:\n\n"
                "- Users: one person, with a password or access keys.\n"
                "- Groups: a set of users that share permissions.\n"
                "- Roles: a set of permissions that a person or a machine takes on for a while. A CI job, a VM or a person assumes the role and gets temporary credentials that expire.\n\n"
                "Permissions live in policies. In AWS a policy is a JSON document made of statements. "
                "Each statement has an Effect (allow or deny), an Action (such as `s3:GetObject`), a Resource (which bucket or object) and an optional Condition. Anything not allowed is denied.\n\n"
                "Two rules keep you out of trouble. The first is **least privilege**: grant only the actions and resources a job needs, then tighten from there. "
                "A deploy job that uploads to one bucket should not be able to delete databases. "
                "The second is to prefer roles over long-lived access keys. A key saved in a file or a CI secret works until someone deletes it, and a leaked key works for an attacker too. "
                "Role credentials expire on their own. Day 21 shows GitHub Actions getting cloud access this way, through a standard called OpenID Connect (OIDC), with no stored keys at all.\n\n"
                "Security is shared between you and the provider. The provider secures the cloud itself: buildings, hardware and the virtualization layer. "
                "You secure what you put in it: your data, your IAM policies, your firewall rules and, on a VM, the operating system and its patches. "
                "The line moves with the service type. With serverless, the provider does nearly all of it; with a VM, patching the OS is your job."
            ),
            "refs": [AWS_IAM_BP, AWS_SHARED],
        },
        {
            "h": "Pricing, free tiers and the cleanup habit",
            "body": (
                "Cloud bills come from a few meters:\n\n"
                "- Compute time, per second or hour, while a machine runs.\n"
                "- Storage, per gigabyte per month, even for disks nobody uses.\n"
                "- Requests, for services like object storage and functions.\n"
                "- Data sent out to the internet (egress), per gigabyte.\n\n"
                "You can buy compute three ways. On-demand is the default: no commitment and the highest price. Reserved capacity and savings plans give a discount for promising one or three years of use. "
                "Spot instances use spare capacity at a large discount, but the provider can take them back at short notice, so they suit work that can restart.\n\n"
                "Some resources bill by the hour just for existing: NAT gateways, load balancers, public IPv4 addresses, and disks or snapshots nobody uses. A stopped VM still pays for its disk.\n\n"
                "Free tiers changed in 2025, and the rules in October 2026 look like this:\n\n"
                "- AWS: new accounts pick a Free plan or a Paid plan. The Free plan gives $100 in credits plus up to $100 more for trying services, for 6 months or until the credits run out. Then the account closes instead of charging you. AWS's own FAQ disagrees with itself on when credits expire, so check the Credits page in your console.\n"
                "- Azure: $200 of credit for 30 days, behind a spending limit that is on by default. Some services are free in limited amounts for 12 months, but after the 30 days you must upgrade to keep using them. Microsoft's pages disagree on how many services are always free (55 or 65).\n"
                "- Google Cloud: $300 of credit for 90 days, and no charge until you activate a paid account. Separately, Always Free includes one small e2-micro VM, but only in three US regions.\n\n"
                "These rules change, so read the provider's current page before you sign up. Then build the habit:\n\n"
                "1. Set a budget alert on day one. It sends email; it does not stop anything.\n"
                "2. Use one region, and tag everything with an owner and a purpose.\n"
                "3. Delete what you made the same day. On Day 29 that is `terraform destroy`.\n"
                "4. Never put access keys in code or in git.\n\n"
                "Today needs no cloud account. Day 29 has the only cloud steps in this course, and they are optional."
            ),
            "refs": [AWS_PLANS, AZ_AVOID, GCP_FREE],
        },
    ],
    "analogy": (
        "A VPC is your own fenced campus inside a huge rented business park. The park owner keeps the roads, the fences and the power running; you decide which buildings to put up, who gets a key card and which doors stay locked. "
        "Public subnets are the buildings by the front gate, private subnets sit at the back, and the NAT gateway is a mailroom that sends letters out but accepts no visitors. "
        "The picture breaks on cost. A real campus charges rent whether you use it or not. The cloud charges by the hour for each thing that exists, so you can tear the whole campus down tonight and pay nothing tomorrow."
    ),
    "diagram": D10_SVG,
    "diagram_caption": "One VPC across two AZs. Public subnets hold the load balancer and NAT gateways; private subnets hold the app and database and reach out only through NAT.",
    "worked": {
        "title": "Design PayFlow's checkout network on paper",
        "steps": [
            {
                "say": "PayFlow, the made-up payments company, wants its checkout API in two AZs: a load balancer that the internet can reach, and the app and database that it cannot. Start with the VPC block. 10.0.0.0/16 gives 65,536 addresses, far more than needed, so there is room to add subnets for years. Python shows how it slices into /24s.",
                "code": (
                    "$ python3 -c \"import ipaddress as i; print(list(i.ip_network('10.0.0.0/16').subnets(new_prefix=24))[:3])\"\n"
                    "[IPv4Network('10.0.0.0/24'), IPv4Network('10.0.1.0/24'), IPv4Network('10.0.2.0/24')]"
                ),
                "lang": "console",
            },
            {
                "say": "Choose a numbering you can read at a glance. Public subnets get 10.0.1 and 10.0.2, private ones 10.0.11 and 10.0.12, and the letter is the AZ. Put that plan into `subnet_plan.py` and run it. Each /24 has 251 usable addresses in AWS, and nothing overlaps.",
                "code": (
                    "$ python3 subnet_plan.py\n"
                    "VPC 10.0.0.0/16: 65536 addresses\n"
                    "public-a   10.0.1.0/24     AZ a  public     251 usable  inside VPC\n"
                    "public-b   10.0.2.0/24     AZ b  public     251 usable  inside VPC\n"
                    "private-a  10.0.11.0/24    AZ a  private    251 usable  inside VPC\n"
                    "private-b  10.0.12.0/24    AZ b  private    251 usable  inside VPC\n"
                    "plan OK"
                ),
                "lang": "console",
            },
            {
                "say": "Break it on purpose, so you trust the check. Type private-b as 10.0.2.0/24, a copy-paste slip that really happens. Two subnets may never share addresses, and the script says so and exits with 1, which a CI job would treat as a failure.",
                "code": (
                    "$ python3 subnet_plan.py\n"
                    "VPC 10.0.0.0/16: 65536 addresses\n"
                    "public-a   10.0.1.0/24     AZ a  public     251 usable  inside VPC\n"
                    "public-b   10.0.2.0/24     AZ b  public     251 usable  inside VPC\n"
                    "private-a  10.0.11.0/24    AZ a  private    251 usable  inside VPC\n"
                    "private-b  10.0.2.0/24     AZ b  private    251 usable  inside VPC\n"
                    "OVERLAP   public-b 10.0.2.0/24 and private-b 10.0.2.0/24\n"
                    "plan has problems"
                ),
                "lang": "console",
            },
            {
                "say": "Write the route tables. Both public subnets share one table with a default route to the internet gateway. Each private subnet gets a table whose default route goes to the NAT gateway in its own AZ, so AZ b keeps working if AZ a fails. One shared NAT gateway would be cheaper, and many teams accept that for test environments.",
                "code": (
                    "public table (public-a, public-b)\n"
                    "  10.0.0.0/16   local\n"
                    "  0.0.0.0/0     internet gateway\n\n"
                    "private table a (private-a)\n"
                    "  10.0.0.0/16   local\n"
                    "  0.0.0.0/0     NAT gateway in public-a\n\n"
                    "private table b (private-b)\n"
                    "  10.0.0.0/16   local\n"
                    "  0.0.0.0/0     NAT gateway in public-b"
                ),
                "lang": "text",
            },
            {
                "say": "Chain the security groups so each layer accepts traffic only from the layer in front of it. Rules name groups, not addresses, so they survive scaling. Replies need no rules, because security groups are stateful.",
                "code": (
                    "lb-sg    inbound 443    from 0.0.0.0/0     (the internet)\n"
                    "app-sg   inbound 8000   from lb-sg         (only the load balancer)\n"
                    "db-sg    inbound 5432   from app-sg        (only the app)\n"
                    "all three: outbound allowed, replies handled by connection tracking"
                ),
                "lang": "text",
            },
            {
                "say": "A nightly reporting job must read files from one bucket and nothing else, and `read-one-bucket.json` grants exactly that. AWS names every resource with an ARN (Amazon Resource Name), such as `arn:aws:s3:::payflow-reports`. Note the two resources: listing acts on the bucket itself, while reading acts on the objects inside it, written with `/*`. The jq summary below is easy to read, and jq fails loudly if the JSON is broken.",
                "code": (
                    "$ jq -r '.Statement[] | \"\\(.Effect) \\(.Action) on \\(.Resource)\"' read-one-bucket.json\n"
                    "Allow s3:ListBucket on arn:aws:s3:::payflow-reports\n"
                    "Allow s3:GetObject on arn:aws:s3:::payflow-reports/*"
                ),
                "lang": "console",
            },
            {
                "say": "Last, the cost check. In this design, the load balancer and the two NAT gateways bill every hour even with no traffic, and so does any public IPv4 address. The database bills for its storage even when stopped. That list is exactly what you would delete first after a test, and on Day 29 a single `terraform destroy` removes all of it."
            },
        ],
    },
    "code": [
        {"lang": "python", "title": "subnet_plan.py", "src": f("subnet_plan.py"), "run": "python3 subnet_plan.py"},
        {"lang": "json", "title": "read-one-bucket.json", "src": f("read-one-bucket.json"), "run": "jq . read-one-bucket.json"},
    ],
    "commands": [
        {"cmd": "python3 -c \"import ipaddress as i; print(list(i.ip_network('10.0.0.0/16').subnets(new_prefix=24))[:3])\"", "what": "Show the first three /24 subnets of a /16."},
        {"cmd": "python3 -c \"import ipaddress as i; print(i.ip_network('10.0.0.0/24').num_addresses - 5)\"", "what": "Usable addresses in an AWS /24 subnet, after the 5 reserved ones. Prints 251."},
        {"cmd": "python3 -c \"import ipaddress as i; print(i.ip_network('10.0.2.0/24').overlaps(i.ip_network('10.0.2.128/25')))\"", "what": "Check whether two blocks overlap. Prints True."},
        {"cmd": "python3 subnet_plan.py", "what": "Check a whole VPC plan: sizes, inside the VPC, and no overlaps. Exits 1 if anything is wrong."},
        {"cmd": "jq . read-one-bucket.json", "what": "Pretty-print a policy file, or fail with an error if the JSON is broken."},
        {"cmd": "jq -r '.Statement[] | \"\\(.Effect) \\(.Action) on \\(.Resource)\"' read-one-bucket.json", "what": "Print one line per policy statement: effect, action and resource."},
        {"cmd": "aws sts get-caller-identity", "what": "Optional, Day 29: show which AWS identity your command line is using right now."},
        {"cmd": "aws ec2 describe-availability-zones --region eu-central-1 --output table", "what": "Optional, Day 29: list the availability zones in one region."},
    ],
    "mistake": (
        "Learners click around a cloud console, follow a tutorial, and forget half of what they created, often in another region. "
        "Build every experiment as one unit that one command can delete: a Terraform stack, an Azure resource group or a Google Cloud project. "
        "Stay in one region, and delete it the same day. Then check the bill by service the next morning."
    ),
    "real_world": (
        "PayFlow runs checkout in three availability zones in one region, with the load balancer in public subnets and everything else private. "
        "Its CI pipeline deploys by assuming an IAM role through OpenID Connect, so no access keys are stored anywhere. "
        "Every resource carries owner and cost-center tags, and a weekly cost report by tag goes to each team."
    ),
    "task": {
        "title": "Design a three-zone network for a ledger service",
        "steps": [
            "Copy `subnet_plan.py` and change the VPC to `10.20.0.0/16`.",
            "Plan nine /24 subnets: public, app and data tiers in each of three AZs (a, b and c). Pick a numbering scheme you can read at a glance.",
            "Run the script until it prints `plan OK`. Then add a deliberate overlap and a block with host bits set, and check that the script catches both.",
            "On paper, write the route table for each tier. Decide whether the data tier needs a route to the internet at all.",
            "Write the security group rules for a load balancer on 443, an app on 8080 and PostgreSQL on 5432, each accepting traffic only from the layer in front.",
            "Write `upload-releases.json`: a policy that lets a CI job upload objects under `releases/` in a bucket called `payflow-ledger-artifacts`, and nothing else.",
            "Check the policy with `jq .`, and print one line per statement with the jq command from this lesson.",
            "List everything in your design that bills by the hour even when idle, and write the single command you would use to delete it all on Day 29.",
        ],
        "hints": [
            "One readable scheme: 10.20.1-3 for public, 10.20.11-13 for app and 10.20.21-23 for data, with the last digit matching the AZ.",
            "Uploading is the action `s3:PutObject`, and a prefix inside a bucket is written as `arn:aws:s3:::bucket-name/releases/*`.",
            "A data tier with only the local route can still talk to the app tier, because the local route covers the whole VPC.",
        ],
        "done_when": "You are done when subnet_plan.py prints plan OK for nine subnets across three AZs, and `jq . upload-releases.json` prints your policy without an error.",
    },
    "explain_back": {
        "prompt": "Explain how a request from the internet reaches an app in a private subnet, and how that app downloads a package. Mention the load balancer, security groups, route tables and the NAT gateway.",
        "answer": (
            "The request enters the VPC through the internet gateway and reaches the load balancer in a public subnet, whose security group allows port 443 from anywhere. "
            "The load balancer forwards it to the app in a private subnet, whose security group allows traffic only from the load balancer's group. The reply goes back automatically, because security groups are stateful. "
            "When the app downloads a package, the private subnet's route table sends that traffic to the NAT gateway in a public subnet. "
            "The NAT gateway swaps in its public address, so the app can reach out while nobody outside can connect in."
        ),
    },
    "recap": [
        "The cloud rents machines, storage and services through APIs, which is why tools like Terraform can drive it.",
        "Regions are places; availability zones are separate data centers inside them, so spread copies across AZs.",
        "A subnet is public because its route table sends 0.0.0.0/0 to an internet gateway, not because of its name.",
        "Security groups are stateful and allow-only; NACLs are stateless, ordered and guard whole subnets.",
        "Least privilege and short-lived role credentials beat broad permissions and long-lived keys.",
        "Free tiers have rules that change; set a budget alert, stay in one region, and delete what you create.",
    ],
    "check": [
        {
            "q": "Your app runs as four copies, all in two subnets of the same availability zone. That AZ loses power. What happens?",
            "options": [
                "Traffic moves to the other subnet",
                "Every copy goes down at once",
                "The region moves them to a new AZ",
                "Only half of the copies fail",
            ],
            "answer": 1,
            "why": "Both subnets sit in the failed AZ, so every copy is lost; spreading copies across AZs is what survives this.",
        },
        {
            "q": "A subnet's NACL allows inbound 443 and outbound 443 only. The app logs every request, yet clients time out. Why?",
            "options": [
                "The security group blocks port 443",
                "TLS cannot run inside a private subnet",
                "Replies to ephemeral ports are dropped",
                "The load balancer has no public IP",
            ],
            "answer": 2,
            "why": "NACLs are stateless, so the replies, sent to the client's port between 1024 and 65535, need their own outbound rule.",
        },
        {
            "q": "A CI job must upload build files to one S3 bucket. Which setup follows least privilege and avoids long-lived keys?",
            "options": [
                "A role allowing PutObject on that bucket, assumed via OIDC",
                "An admin user's access key stored as a CI secret",
                "The root account's keys with MFA turned on",
                "A user with full S3 access and a yearly key rotation",
            ],
            "answer": 0,
            "why": "The role grants only the one action on the one bucket, and OIDC gives the job short-lived credentials instead of a stored key.",
        },
    ],
    "interview": [
        {
            "q": "What is the difference between a security group and a network ACL in AWS?",
            "a": (
                "A security group attaches to a network interface, has allow rules only and is stateful, so replies to allowed traffic go through without extra rules. "
                "A network ACL applies to a whole subnet, has numbered allow and deny rules evaluated in order, and is stateless, so return traffic to ephemeral ports needs explicit rules. "
                "I use security groups as the main control, chaining them by group reference, and keep NACLs for coarse subnet-wide blocks."
            ),
        },
        {
            "q": "Explain the shared responsibility model with an example.",
            "a": (
                "The provider secures the cloud itself: data centers, hardware, the network and the virtualization layer. "
                "The customer secures what they put in it: data, identities and permissions, network rules and configuration. "
                "On a VM service like EC2, I patch the guest operating system and configure the security group. "
                "On a serverless service like Lambda, the provider handles the runtime and OS, and I am left with my code, its permissions and its data."
            ),
        },
        {
            "q": "How would you keep cloud costs under control for a team?",
            "a": (
                "First visibility: tag every resource with an owner and a purpose, and send a regular cost report by tag to each team. "
                "Then guardrails: budget alerts per account, and short-lived environments built with infrastructure as code, so a test stack is destroyed with one command. "
                "Then the usual leaks: idle load balancers and NAT gateways, unattached disks and snapshots, oversized instances, and data egress. "
                "For steady workloads I would look at savings plans or reserved capacity, and spot for work that can restart."
            ),
        },
    ],
    "deeper": {
        "minutes": 15,
        "body": (
            "Put Days 8, 9 and 10 together by following one request to PayFlow's checkout, hop by hop.\n\n"
            "1. A customer's phone asks DNS for `checkout.payflow.example`. The provider's DNS service answers with the load balancer's public addresses, one per AZ.\n"
            "2. The phone opens TCP to one of them on port 443. The packet reaches the VPC through the internet gateway, and the load balancer's security group allows 443 from anywhere.\n"
            "3. The load balancer runs the TLS handshake with the certificate it holds, so TLS ends here. It reads the HTTP request and picks a healthy app copy, perhaps in the other AZ.\n"
            "4. It opens a new connection to the app's private address on port 8000. The app's security group allows that port only from the load balancer's group, so the packet passes.\n"
            "5. The app queries the database on 5432, allowed only from the app's group, and returns a response. Every reply rides back on the same tracked connections, so no extra rules are needed.\n"
            "6. Meanwhile, the app checks a fraud service on the internet. That traffic follows the private subnet's default route to the NAT gateway, which swaps in its public address.\n\n"
            "Now ask where each failure would show up:\n\n"
            "- A wrong DNS record: the phone never reaches you, and the error is a name or connection error, never an HTTP code.\n"
            "- An expired certificate: the handshake fails in step 3, with no HTTP status at all.\n"
            "- The app security group missing its rule: the load balancer cannot connect, its health checks fail, and users see 502 or 503 from the balancer.\n"
            "- A slow database: the load balancer gives up waiting, and users see 504.\n"
            "- A broken NAT route: checkout works until the fraud check, then that one call times out.\n\n"
            "This mapping, from symptom to hop, is most of what an on-call engineer does in the first five minutes of an incident. "
            "It is also why Parts 9 to 12 matter: metrics and traces tell you which hop is slow without guessing.\n\n"
            "For a real provider's version of these pieces, read AWS's [shared responsibility page](https://docs.aws.amazon.com/wellarchitected/latest/security-pillar/shared-responsibility.html). "
            "Its [network ACL page](https://docs.aws.amazon.com/vpc/latest/userguide/vpc-network-acls.html) has a side-by-side table of security groups and NACLs."
        ),
    },
    "sources": [src(AWS_SHARED), src(AWS_NACL), src(GCP_COMPARE), src(AWS_PLANS)],
}

part = {
    "part": 2,
    "title": "Networking and the cloud",
    "intro": (
        "Every deploy in this course travels over a network, and most production systems run in someone else's data center. "
        "Part 2 follows one request in the order it happens. Day 8 covers names, addresses and ports. "
        "Day 9 covers the HTTP conversation and the servers in the middle, and Day 10 the rented cloud network around it all. Everything runs on your Mac with Docker, and you need no cloud account."
    ),
    "lessons": [d08, d09, d10],
    "recap": [
        "An IP address finds the machine and a port finds the program; private addresses reach the internet through NAT.",
        "/N fixes N bits: /24 holds 256 addresses, /16 holds 65,536, and a bigger N means a smaller network.",
        "Apps in containers bind to 0.0.0.0; publish to 127.0.0.1 when only your laptop should connect.",
        "DNS walks from your resolver to root, TLD and authoritative servers, and caches each answer for its TTL.",
        "Unresolved means DNS, refused means no listener, and a timeout means a drop or a wrong address.",
        "HTTP is text with methods, headers and status codes; 502, 503 and 504 usually come from proxies.",
        "TLS encrypts and proves control of a name, and certificate renewal must be automatic.",
        "A reverse proxy ends TLS and balances load; L4 sees ports, L7 sees HTTP.",
        "In the cloud, route tables make subnets public or private, and security groups are stateful while NACLs are not.",
        "Use least privilege and roles, set a budget alert, stay in one region and delete what you create.",
    ],
    "flashcards": [
        {"front": "What does /24 mean, and how many addresses does it hold?", "back": "The first 24 bits are fixed; the block holds 256 addresses."},
        {"front": "Name the three private IPv4 ranges.", "back": "10.0.0.0/8, 172.16.0.0/12 and 192.168.0.0/16."},
        {"front": "What does NAT do in your home router?", "back": "It swaps your private source address for its public one on the way out, remembers the swap, and reverses it for replies."},
        {"front": "What is the difference between binding to 127.0.0.1 and to 0.0.0.0?", "back": "127.0.0.1 accepts only local connections; 0.0.0.0 listens on every address the machine has."},
        {"front": "Connection refused or timed out: what does each tell you?", "back": "Refused: the host answered but nothing listens on the port. Timed out: no answer, usually a firewall drop or a wrong address."},
        {"front": "What are the three steps of the TCP handshake?", "back": "SYN, SYN-ACK, ACK."},
        {"front": "In what order does a DNS lookup travel when nothing is cached?", "back": "Stub resolver, recursive resolver, root server, TLD server, authoritative server."},
        {"front": "What do A, CNAME and MX records hold?", "back": "A: an IPv4 address. CNAME: an alias for another name. MX: the mail servers for the domain."},
        {"front": "Why can dig and ping disagree about a name on your laptop?", "back": "dig asks DNS servers directly and ignores /etc/hosts; ping uses the system resolver, which reads /etc/hosts first."},
        {"front": "Which HTTP methods are idempotent?", "back": "GET, HEAD, PUT and DELETE. POST is not."},
        {"front": "401 or 403?", "back": "401: who are you? (no or bad credentials). 403: I know you, and you may not do this."},
        {"front": "502 or 504?", "back": "502: the proxy got no good answer from the app. 504: the proxy waited for the app and gave up."},
        {"front": "What three things does TLS give you?", "back": "Confidentiality, integrity and authentication of the server."},
        {"front": "Which Let's Encrypt challenge can issue a wildcard certificate?", "back": "DNS-01, which proves control by publishing a TXT record."},
        {"front": "Layer 4 or layer 7 load balancer?", "back": "L4 forwards connections by address and port. L7 reads HTTP and can route by host, path and headers."},
        {"front": "Security group or network ACL?", "back": "Security group: stateful, allow-only, on a network interface. NACL: stateless, ordered allow and deny, on a subnet."},
        {"front": "Why do roles beat long-lived access keys?", "back": "Role credentials are temporary and expire on their own; a leaked long-lived key works until someone deletes it."},
        {"front": "Does an AWS budget alert stop your spending?", "back": "No. It only sends a notification; the resources keep running."},
    ],
    "resources": [
        {"title": JE_DNS_ZINE["title"], "url": JE_DNS_ZINE["url"], "kind": "read", "why": "Julia Evans explains DNS with comics and real queries, and makes it stop feeling like magic."},
        {"title": CP_DNS["title"], "url": CP_DNS["url"], "kind": "watch", "why": "A clear whiteboard walk through resolvers, root servers and caching."},
        {"title": NC_PLAYLIST["title"], "url": NC_PLAYLIST["url"], "kind": "watch", "why": "A fun video series that builds IP addresses, private ranges, NAT and subnetting step by step."},
        {"title": MESS_DNS["title"], "url": MESS_DNS["url"], "kind": "read", "why": "A free playground with a real subdomain, where you watch your own DNS queries arrive live."},
        {"title": MDN_OVERVIEW["title"], "url": MDN_OVERVIEW["url"], "kind": "docs", "why": "The standard reference for how HTTP works, with links to every header and status code."},
        {"title": CP_TLS["title"], "url": CP_TLS["url"], "kind": "watch", "why": "Mike Pound draws the TLS handshake and the key exchange on paper, one message at a time."},
        {"title": HPBN_TLS["title"], "url": HPBN_TLS["url"], "kind": "read", "why": "A free book chapter on TLS performance and certificate chains; written before TLS 1.3, but still clear."},
        {"title": LE_LIFETIMES["title"], "url": LE_LIFETIMES["url"], "kind": "docs", "why": "Why certificates are getting shorter, the exact dates, and how to prepare your renewals."},
        {"title": CF_LB["title"], "url": CF_LB["url"], "kind": "read", "why": "A short comparison of layer 4, layer 7 and DNS load balancing."},
        {"title": GCP_COMPARE["title"], "url": GCP_COMPARE["url"], "kind": "docs", "why": "A filterable map of matching services across AWS, Azure and Google Cloud."},
        {"title": AWS_SHARED["title"], "url": AWS_SHARED["url"], "kind": "docs", "why": "AWS's own description of what it secures and what you must secure yourself."},
        {"title": FCC_CLF["title"], "url": FCC_CLF["url"], "kind": "watch", "why": "A long, free course on core AWS services; watch the parts on regions, VPCs, IAM and billing."},
    ],
    "quiz": [
        {
            "q": "An app in a container listens on 127.0.0.1:8000. You run it with `-p 8000:8000` and curl localhost:8000 on your Mac. What happens?",
            "options": [
                "It works, because Docker forwards the port",
                "Docker refuses to start the container",
                "curl gets an empty reply or a reset",
                "It works, but only over HTTPS",
            ],
            "answer": 2,
            "why": "Docker forwards to the container's network address, and an app bound to the container's loopback never sees that traffic.",
        },
        {
            "q": "How many addresses does 10.0.4.0/22 hold?",
            "options": ["1,024", "256", "4,096", "65,536"],
            "answer": 0,
            "why": "32 minus 22 leaves 10 free bits, and 2 to the power of 10 is 1,024.",
        },
        {
            "q": "You changed an A record whose TTL is 3600. Twenty minutes later, some users still reach the old server. Why?",
            "options": [
                "The new server's firewall blocks them",
                "Their browsers do not support TLS",
                "The registrar has not approved it yet",
                "Caches keep the old answer for the TTL",
            ],
            "answer": 3,
            "why": "Resolvers may reuse a cached answer until its TTL of one hour runs out.",
        },
        {
            "q": "Your load balancer returns 502 Bad Gateway for every request. Where do you look first?",
            "options": [
                "The client's browser settings",
                "Whether the app behind it is up",
                "The domain's DNS records",
                "The certificate's expiry date",
            ],
            "answer": 1,
            "why": "502 means the proxy itself works but could not get a good answer from the app behind it.",
        },
        {
            "q": "Which curl command shows the TLS handshake and both the request and response headers?",
            "options": ["`curl -I https://example.com`", "`curl -L https://example.com`", "`curl -v https://example.com`", "`curl -k https://example.com`"],
            "answer": 2,
            "why": "`-v` prints every step: DNS, TCP, the TLS handshake, then lines starting with > and <.",
        },
        {
            "q": "Why can't you get a Let's Encrypt certificate for localhost?",
            "options": [
                "Nobody uniquely owns the name localhost",
                "Port 443 is blocked on every laptop",
                "Let's Encrypt only signs IPv6 hosts",
                "Browsers reject all localhost traffic",
            ],
            "answer": 0,
            "why": "A CA must check who controls a name, and localhost exists on every machine, so you make your own certificate instead.",
        },
        {
            "q": "What makes an AWS subnet public?",
            "options": [
                "Its name contains the word public",
                "It has a route to a NAT gateway",
                "Its CIDR block is exactly a /24",
                "A 0.0.0.0/0 route to an internet gateway",
            ],
            "answer": 3,
            "why": "The route table decides: a default route to an internet gateway makes the subnet reachable from the internet.",
        },
        {
            "q": "You want Google Cloud's Always Free e2-micro VM. Which region keeps it free?",
            "options": ["europe-west1", "us-central1", "asia-east1", "The region nearest to you"],
            "answer": 1,
            "why": "The free e2-micro only applies in us-west1, us-central1 and us-east1; other regions are charged.",
        },
        {
            "q": "In access.log, field 9 is the status code. Which pipeline counts how many responses had each status code?",
            "options": [
                "`grep 9 access.log | wc -l`",
                "`sort access.log | uniq -c | awk '{print $9}' | head`",
                "`awk '{print $9}' access.log | sort | uniq -c`",
                "`cut -f9 access.log | uniq`",
            ],
            "answer": 2,
            "why": "awk picks the status field, sort puts equal codes together, and `uniq -c` counts each group; uniq only merges neighbouring lines.",
            "from": "Part 1",
        },
        {
            "q": "In the practice box you run `apt install dnsutils` to get dig, exit, and start a new box. dig is missing again. Why?",
            "options": [
                "`--rm` deleted the old container",
                "dig only works in a Multipass VM",
                "apt removes packages after an hour",
                "Docker Desktop resets the image daily",
            ],
            "answer": 0,
            "why": "Every docker run starts fresh from the image, and `--rm` threw away the container where you installed dig.",
            "from": "Part 0",
        },
    ],
}

OUT.write_text(json.dumps(part, indent=1, ensure_ascii=False) + "\n")
print("wrote", OUT)
