# Networking and Cloud Fundamentals for a DevOps Beginner (3 lessons of about 40 minutes)

Scope: notes for a lesson writer covering (1) how computers find each other, (2) HTTP, TLS and traffic, (3) the cloud. Audience: an experienced software engineer with no networking or cloud background, on an Apple Silicon Mac. Researched 2026-10-30.

How to read the labels in these notes:
- **[S]** a claim backed by the linked source. Each source line says how it was verified: "search" (URL and snippet came back from WebSearch; page not opened because the sandbox blocks most docs sites), "opened" (full text read, usually from the site's own source repository on GitHub), or "derived" (URL built from a source file's slug or a site's URL pattern; see the note on each).
- **[L]** run for real in this sandbox on 2026-10-30 (Linux, Docker Engine 29.9.2, curl 8.5.0, OpenSSL, nginx 1.27.5, Python 3 `ipaddress`). The same commands work on a Mac, but some output wording differs; differences are noted.
- **[K]** general networking knowledge that I did not check against a source in this session. It is standard material, but the writer should treat it as unsourced and check anything that will be stated as fact.

---

## Q1. What teaching order and analogies build real intuition?

### Takeaway
Teach in the order a real request happens: name to address (DNS), then address and door (IP and port), then the delivery rules (TCP or UDP), then the conversation (HTTP), then the sealed envelope (TLS), then the middlemen (proxy, load balancer, CDN, firewall), and only then the cloud, which is the same networking concepts again (CIDR, routes, firewalls) offered as rentable, API-driven building blocks. One running analogy (the postal system plus a phone book) carries all three lessons. Each new idea should be a new part of the same picture, not a new metaphor.

### Cited Findings

**Framing that the sources support**
- Julia Evans built her DNS teaching around the idea that DNS "can feel magical and incomprehensible if you don't know how it works", and she uses a step-by-step "life of a DNS query" comic and a hands-on playground rather than theory first. This supports teaching DNS through an observed query, not through a list of record types — [jvns.ca: new zine "How DNS Works"](https://jvns.ca/blog/2022/04/26/new-zine--how-dns-works-/) (search); [wizardzines: life of a DNS query](https://wizardzines.com/comics/life-of-a-dns-query/) (search).
- Mess With DNS gives each learner a real subdomain of messwithdns.com to create records on, and it shows the DNS queries arriving live. Records are deleted after a week. Evans built it because comics "take a long time and are hard to edit" and she wanted people to experiment instead — [messwithdns.net/about](https://messwithdns.net/about.html) (search); [jvns.ca: mess with dns](https://jvns.ca/blog/2021/12/15/mess-with-dns/) (search).
- MDN's own framing for HTTP: it is "a client-server protocol, which means requests are initiated by the recipient, usually the Web browser"; requests can pass through several proxies; and "HTTP is stateless, but not sessionless": "there is no link between two requests being successively carried out on the same connection", but "HTTP cookies allow the use of stateful sessions" — [MDN: Overview of HTTP](https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Overview) (opened from source `mdn/content/files/en-us/web/http/guides/overview/index.md`; URL derived from the file's `slug: Web/HTTP/Guides/Overview`).
- TLS handshake in one sentence, from Cloudflare: the two sides exchange messages to verify each other, agree on algorithms and session keys; the server presents a certificate, and the client checks that a certificate authority it already trusts signed it. After that, the session keys encrypt the rest of the connection — [Cloudflare: What happens in a TLS handshake?](https://www.cloudflare.com/learning/ssl/what-happens-in-a-tls-handshake/) (search).
- DNS happens before TCP and TLS, so a single `curl https://...` touches every lesson-1 and lesson-2 concept in order: resolve the name (subject to TTL caching), open TCP, run the TLS handshake, then speak HTTP — [Cloudflare TLS handshake page and DNS proxy-status docs](https://developers.cloudflare.com/dns/proxy-status/) (search; the ordering is from the search summary of these Cloudflare pages).
- Layer 4 vs layer 7, which gives the "envelope vs letter" analogy: a layer 7 load balancer "direct[s] traffic to specific endpoints based on information present in each HTTP/HTTPS request" (headers, path, cookies); a layer 4 balancer routes on IP and port and can carry non-HTTP protocols — [Cloudflare Learning Paths: Types of load balancers](https://developers.cloudflare.com/learning-paths/load-balancing/planning/types-load-balancers/) (search); [Cloudflare: Network layers reference](https://developers.cloudflare.com/fundamentals/reference/network-layers/) (search).
- Shared responsibility gives the "landlord vs tenant" analogy. AWS is responsible for "security *of* the cloud", the infrastructure from "the host operating system and virtualization layer down to the physical security of the facilities". The customer is responsible for security *in* the cloud, and that share depends on the service: with EC2 the customer manages "the guest operating system (including updates and security patches), any application software ... and the configuration of the AWS-provided firewall (called a security group)", while "when using serverless services, nearly all of the responsibility for security belongs to AWS" — [AWS Well-Architected: Shared responsibility](https://docs.aws.amazon.com/wellarchitected/latest/security-pillar/shared-responsibility.html) (search); [AWS whitepaper: Shared Security Responsibility Model](https://docs.aws.amazon.com/whitepapers/latest/aws-overview-security-processes/shared-security-responsibility-model.html) (search).
- Cloud services do not map one to one across providers, so teach categories first and names second. Google's comparison table maps its services to "similar or comparable" AWS and Azure offerings. Some services have no counterpart, and one product can map to several. Examples: Compute Engine parallels EC2, Cloud Storage is analogous to S3, and a Lambda function maps to Cloud Run. Google also warns that similar-looking services can behave differently; for example, GCP IAM sets permissions on the resource itself (for example on the bucket) — [Google Cloud: Compare AWS and Azure services to Google Cloud](https://docs.cloud.google.com/docs/get-started/aws-azure-gcp-service-comparison) (search; summary says the page was last updated December 2024); [Google Cloud blog: handy product map](https://cloud.google.com/blog/topics/developers-practitioners/handy-new-google-cloud-aws-and-azure-product-map) (search); [Google: Migrate from AWS, get started](https://docs.cloud.google.com/architecture/migration-from-aws-get-started) (search); [Google: Migrate from Azure, get started](https://docs.cloud.google.com/architecture/migration-from-azure-get-started) (search).

**CIDR facts used in the teaching order (verified by computation)**
- `10.0.0.0/16` = 65,536 addresses (10.0.0.0–10.0.255.255, mask 255.255.0.0); `10.0.1.0/24` = 256 addresses (mask 255.255.255.0); `172.16.0.0/12` = 1,048,576 addresses (172.16.0.0–172.31.255.255); `10.0.0.0/8` = 16,777,216. Splitting 10.0.0.0/16 into /24s gives 10.0.0.0/24, 10.0.1.0/24, 10.0.2.0/24 and so on; 10.0.1.5 is inside 10.0.0.0/16 — [L] Python `ipaddress`.
- 10.0.1.5, 172.20.3.4 and 192.168.0.10 are private; 8.8.8.8 is public/global; 127.0.0.1 is loopback; 169.254.169.254 is link-local (it is also the cloud instance-metadata address [K]); 100.64.0.1 is neither private nor global (shared carrier-grade NAT space) — [L] Python `ipaddress` classification.
- In AWS, every subnet loses 5 addresses: in 10.0.0.0/24 AWS reserves .0 (network), .1 (VPC router), .2 (DNS), .3 (future use) and .255 ("We do not support broadcast in a VPC, therefore we reserve this address"). Subnet sizes run from /28 (16 addresses) to /16 (65,536) — [AWS VPC: Subnet CIDR blocks](https://docs.aws.amazon.com/vpc/latest/userguide/subnet-sizing.html) (search). So a /24 has 251 usable addresses in AWS, compared with the classic 254 [K].

### Inferences
Below is the recommended concept sequence for each lesson. Each item has a one-line plain explanation and an analogy. Unless a line cites a source above, this is [K] teaching knowledge.

**One running analogy for all 3 lessons.** The internet is a postal system. An **IP address** is a building's street address. A **port** is the apartment or office number inside the building. **DNS** is the phone book (or your phone's contacts app) that turns a name into an address. **TCP** is registered mail with tracking and receipts; **UDP** is a postcard. **HTTP** is the letter's language and format. **TLS** is a sealed, tamper-evident envelope plus a check of the recipient's ID card. A **reverse proxy** is the front-desk receptionist. A **load balancer** is a receptionist who spreads visitors across several clerks. A **CDN** is a set of local branch warehouses. A **firewall** is a bouncer. In the cloud, a **VPC** is your own fenced office campus inside a huge rented business park.

**Lesson 1: How computers find each other (about 40 min)**
1. *The journey of one request* (3 min). Typing a URL triggers: name → address → connect to a door → talk. Show it once with `curl -v`, then unpack it. Analogy: mailing a letter to a business you only know by name.
2. *IP address.* A number that identifies a network interface; IPv4 is 32 bits written as 4 numbers 0–255; IPv6 is 128 bits written in hex. Analogy: street address. Note that a laptop has several (Wi-Fi, loopback, Docker bridge).
3. *Private vs public.* Private ranges (10.0.0.0/8, 172.16.0.0/12, 192.168.0.0/16) are reused inside millions of homes and VPCs and are not routed on the internet; public addresses are globally unique. Analogy: "Room 12" exists in every hotel; only the hotel's street address is unique.
4. *CIDR and subnets.* `/N` means "the first N bits are the network (street), the rest are hosts (house numbers)". Each extra bit halves the block: /24 = 256, /25 = 128, /16 = 65,536. A **bigger** prefix number means a **smaller** network. Analogy: a ZIP code prefix; "all addresses starting with 10.0.1". Teach with the 2^(32−N) rule, not binary drills.
5. *Router, default gateway and route table.* A host sends a packet straight to the destination if it is in its own subnet; otherwise it hands the packet to the default gateway. A route table is a list of "destination prefix → next hop" rules, and the most specific match wins. Analogy: the mailroom: local mail goes down the hall, everything else goes to the post office. This directly sets up cloud route tables in lesson 3.
6. *NAT.* Your router rewrites your private source address to its one public address and remembers the mapping, so replies come back to you. Outsiders cannot start a connection inward unless you set up port forwarding. Analogy: a company switchboard: staff can call out, and the outside world sees only the main number. The cloud NAT gateway in lesson 3 is the same idea.
7. *Ports.* A 16-bit number (0–65535) that picks which program on a host gets the traffic. Well-known ports: 22 SSH, 53 DNS, 80 HTTP, 443 HTTPS, 5432 Postgres, 6379 Redis. The client side uses a random high "ephemeral" port. A connection is identified by the 4-tuple of source IP, source port, destination IP and destination port (5-tuple with the protocol). Analogy: apartment number; the return address includes your apartment number too.
8. *TCP vs UDP.* TCP sets up a connection (handshake), orders bytes, retransmits losses and controls flow. UDP sends independent datagrams with no setup and no guarantee. DNS mostly uses UDP 53 (TCP for large answers), and HTTP/3 runs over QUIC on UDP. Analogy: a phone call vs shouting messages across a room / registered mail vs postcards.
9. *localhost, 127.0.0.1 and 0.0.0.0.* `127.0.0.1` (and `::1`) is the loopback interface, so traffic never leaves the machine. Binding a server to `0.0.0.0` means "listen on every interface I have". `0.0.0.0` is not an address you connect to. Analogy: 127.0.0.1 is an intercom that only works inside the house; binding to 0.0.0.0 means answering every door of the house. This matters a lot for Docker (see Q2 and [L] demo in Q4).
10. *DNS: names to addresses.* A distributed, cached phone book. Record types: **A** (name → IPv4), **AAAA** (name → IPv6), **CNAME** (this name is an alias, "see the entry for that other name"), **MX** (which servers accept email for this domain, with priority), **TXT** (free-text notes, used for domain-ownership proofs, SPF/DKIM email policy and Let's Encrypt DNS-01), **NS** (which servers are the authority for this zone).
11. *Resolution steps.* App → OS stub resolver (checks `/etc/hosts` and its cache) → recursive resolver (your ISP, 1.1.1.1 or 8.8.8.8; has a big cache) → root servers ("ask .com") → TLD servers ("ask example.com's nameservers") → authoritative server (the answer) → back down, cached at each layer. Analogy: you ask a librarian (recursive resolver), who checks the catalogue of catalogues. Use the Julia Evans "life of a DNS query" comic here.
12. *TTL and caching.* Every answer has a TTL in seconds: how long anyone may reuse it without asking again. "DNS propagation" is really old answers expiring from caches. Analogy: a "best before" date on a copy of the phone book.
13. */etc/hosts.* A local file checked before DNS, which overrides the phone book for your machine only. Analogy: a sticky note on your own phone that says "Mum = this number", whatever the directory says.
14. *Tools as questions you ask.* `ping` (are you there? ICMP echo), `traceroute` (which post offices did it pass through?), `dig` / `nslookup` (what does the phone book say?), `lsof` / `netstat` on Mac, `ss` on Linux (who is listening on which door?), `nc` (open a raw TCP or UDP conversation by hand).

**Lesson 2: HTTP, TLS and traffic (about 40 min)**
1. *HTTP is text over TCP.* A request has a request line (`GET /path HTTP/1.1`), headers, a blank line and an optional body. A response has a status line, headers, a blank line and a body. Show it raw with `curl -v` (see the [L] output in Q4). Analogy: a restaurant order slip and the receipt that comes back [S MDN Messages guide below].
2. *Methods.* GET (read), POST (create/submit), PUT (replace), PATCH (partial update), DELETE, HEAD (headers only), OPTIONS (what is allowed, CORS preflight). Safe = no side effects (GET, HEAD); idempotent = repeating it has the same effect (GET, PUT, DELETE).
3. *Status codes as families.* 1xx info, 2xx success (200, 201, 204), 3xx go elsewhere (301 permanent, 302/307 temporary, 304 not modified), 4xx you made a mistake (400, 401 not authenticated, 403 authenticated but not allowed, 404, 429 rate limited), 5xx the server failed (500, 502 bad gateway, 503 unavailable, 504 gateway timeout). DevOps people see 502/503/504 most, because they come from proxies and load balancers.
4. *Headers.* Metadata on the envelope: `Host` (which site; lets one IP serve many sites), `Content-Type`, `Authorization`, `Cache-Control`, `Location` (redirect target), `User-Agent`, `Set-Cookie`/`Cookie`, `X-Forwarded-For` (original client IP, added by proxies).
5. *Cookies.* HTTP is stateless, so the server hands you a token with `Set-Cookie` and your browser returns it with `Cookie` on every request. Attributes: `Secure`, `HttpOnly`, `SameSite`, `Expires/Max-Age`. Analogy: a coat-check ticket [S MDN Overview, cookies guide].
6. *curl in depth.* `-v` (show everything), `-i` (include response headers), `-I` (HEAD only), `-L` (follow redirects), `-X` (method), `-H` (header), `-d` (body), `-o /dev/null -s -w '%{http_code}'` (scripting), `-w` timing variables, `--resolve` (bypass DNS), `--cacert` (trust a specific CA), and `-k` (turns verification off, never in production).
7. *HTTPS = HTTP inside TLS.* TLS gives three things: confidentiality (encryption), integrity (tamper detection) and authentication (the server proves it holds the private key for a certificate for this name). Analogy: a sealed tamper-evident envelope, delivered only after the courier checks the recipient's ID.
8. *The TLS 1.3 handshake* (show the real `curl -v` lines from Q4 [L]): ClientHello (supported ciphers, key share, SNI = which hostname, ALPN = h2 or http/1.1) → ServerHello + certificate + proof of key (CertificateVerify) + Finished → client verifies the chain → both derive session keys → encrypted HTTP. That is 1 round trip in TLS 1.3. [S Cloudflare handshake page; hpbn TLS chapter; note hpbn predates TLS 1.3, see Q5.]
9. *Certificates and CAs.* A certificate is a signed statement: "this public key belongs to example.com (Subject Alternative Names), valid from X to Y, signed by CA Z". Your OS and browser ship a trust store of root CAs; servers send their certificate plus intermediates, which form a chain up to a trusted root. Analogy: a passport (certificate) issued by a government (CA) that border control (your browser) already trusts.
10. *Let's Encrypt and ACME.* A free, automated CA. The ACME protocol proves you control the domain using HTTP-01 (serve a token on port 80), DNS-01 (publish a TXT record; required for wildcard certificates) or TLS-ALPN-01. Lifetimes are shrinking (90 → 64 days in Feb 2027 → 45 days in Feb 2028), so automation is mandatory. [S Let's Encrypt; details in Q2 and Q4.]
11. *Reverse proxy.* A server in front of your apps that receives every request and forwards it inside: TLS termination, routing by host or path, compression, caching, rate limits. nginx, Caddy, Traefik and Envoy are common. Analogy: the receptionist who takes every visitor and walks them to the right office. Contrast this with a forward proxy, which acts on behalf of clients (a corporate egress proxy) [S MDN Proxy servers guide below].
12. *Load balancers, L4 vs L7.* A layer-4 balancer reads only the envelope (IP, port, TCP/UDP) and forwards connections; it is fast and protocol-agnostic (for example AWS NLB [K]). A layer-7 balancer opens the letter and routes on HTTP host, path, headers and cookies; it can do TLS termination and sticky sessions (for example AWS ALB, Azure Application Gateway [K]). Health checks remove dead backends [S Cloudflare types of load balancers].
13. *CDN.* A worldwide network of caching reverse proxies that serve copies of your content from a location near the user. `Cache-Control` decides what may be cached and for how long. Analogy: regional warehouses so that not every order ships from the factory.
14. *Firewalls.* Rules that allow or deny traffic by source, destination, port and protocol. Stateful firewalls remember connections and let replies back in automatically; stateless ones judge every packet on its own. Analogy: a bouncer with a list who remembers the faces of people who stepped out. This bridges to security groups vs NACLs in lesson 3.

**Lesson 3: The cloud (about 40 min)**
1. *What the cloud is.* Renting someone else's data centers by the second, through an API. Every console click is an API call, which is why Terraform works. Analogy: electricity from the grid instead of your own generator, billed by the meter.
2. *Regions and availability zones.* A region is a geographic area (for example us-east-1, West Europe, us-central1). An AZ is one or more physically separate data centers in that region, with independent power and networking. Spread across AZs for high availability; choose a region for latency, data-residency law and price. Analogy: region = city, AZ = separate buildings on separate power grids in that city.
3. *IaaS / PaaS / SaaS / serverless.* IaaS rents you VMs, disks and networks (you patch the OS). PaaS runs your code or container on a managed platform. SaaS is finished software (Gmail, GitHub). Serverless/FaaS runs a function per event and bills per request and duration, with scale to zero. Analogy: "pizza as a service" (make at home, take-and-bake, delivery, dine out). The shared-responsibility line moves with each step [S AWS shared responsibility].
4. *Core service map across AWS, Azure and GCP* (teach categories, then names; [K], check against Google's comparison table [S]):

| Category | AWS | Azure | Google Cloud |
|---|---|---|---|
| Virtual machines | EC2 | Virtual Machines | Compute Engine |
| Managed Kubernetes | EKS | AKS | GKE |
| Serverless containers | Fargate / App Runner | Container Apps | Cloud Run |
| Functions | Lambda | Functions | Cloud Run functions |
| Object storage | S3 | Blob Storage | Cloud Storage |
| Block disks | EBS | Managed Disks | Persistent Disk |
| Managed SQL | RDS / Aurora | Azure SQL / Azure Database for PostgreSQL | Cloud SQL |
| NoSQL | DynamoDB | Cosmos DB | Firestore / Bigtable |
| Private network | VPC | Virtual Network (VNet) | VPC |
| Instance firewall | Security groups (+ NACLs) | Network security groups | VPC firewall rules |
| Load balancing | ELB (ALB = L7, NLB = L4) | Load Balancer (L4), Application Gateway (L7) | Cloud Load Balancing |
| DNS | Route 53 | Azure DNS | Cloud DNS |
| CDN | CloudFront | Front Door | Cloud CDN |
| Identity and access | IAM (+ IAM Identity Center) | Microsoft Entra ID + Azure RBAC | Cloud IAM |
| Secrets | Secrets Manager | Key Vault | Secret Manager |
| Container registry | ECR | Container Registry (ACR) | Artifact Registry |
| Monitoring and logs | CloudWatch | Azure Monitor | Cloud Monitoring / Logging |
| Native IaC | CloudFormation | ARM / Bicep | Infrastructure Manager (Terraform-based) |
| Budgets | AWS Budgets | Cost Management budgets | Cloud Billing budgets |

   The Google page directly confirms EC2 ↔ Compute Engine, S3 ↔ Cloud Storage, Lambda → Cloud Run, Azure VMs → Compute Engine, AKS → GKE, Blob Storage → Cloud Storage and Azure SQL MI → Cloud SQL for SQL Server [S]. The other rows are [K]. Product names change often (for example "Cloud Functions" became "Cloud Run functions"), so check them before publishing.
5. *VPC.* Your own private, isolated network inside the provider, with a CIDR block such as 10.0.0.0/16. Analogy: a fenced campus with its own internal street numbering. [K] Difference to point out: an AWS or Azure VPC/VNet lives in one region, while a GCP VPC is global with regional subnets.
6. *Subnets.* Slices of the VPC CIDR (for example 10.0.1.0/24). An AWS subnet sits in exactly one AZ and loses 5 addresses [S AWS subnet sizing]. "Public" vs "private" subnet is decided by the route table, not by the name. Analogy: floors of the building.
7. *Route tables.* The same idea as lesson 1, step 5. Every VPC table has `10.0.0.0/16 → local`. A public subnet adds `0.0.0.0/0 → internet gateway`; a private subnet adds `0.0.0.0/0 → NAT gateway`, so it can reach out (package downloads) but nobody can reach in. Analogy: signposts at each floor's exit.
8. *Security groups vs network ACLs* (AWS terms). A security group is a stateful, allow-only firewall attached to each instance or network interface. A NACL is a stateless, ordered allow/deny list at the subnet edge. Analogy: the SG is a doorman at each office who remembers who went out and lets them back in; the NACL is a guard at the floor entrance with a checklist and no memory, so replies need their own rule [S AWS, details in Q2].
9. *IAM.* Who (principal: user, group, role, service account) can do what (actions such as `s3:GetObject`) on which resources, under which conditions. Policies are JSON documents (Effect, Action, Resource, Condition). A **role** is a hat you put on for a while and get temporary credentials for; it is the right way for machines (CI, EC2, Lambda) and humans to get access. **Least privilege** means granting only what the task needs, then tightening [S AWS IAM best practices]. Analogy: hotel key cards that open only certain doors and expire at checkout.
10. *Shared responsibility.* The provider secures the building; you lock your own office and decide who gets keys [S AWS].
11. *Pricing and bill shock.* You pay for compute time, storage per GB-month, requests, and data transfer out of the cloud (egress). Idle resources keep billing. Common surprises: NAT gateways, load balancers, public IPv4 addresses, unattached disks and snapshots, resources left in a region you are not looking at, and leaked access keys used for crypto-mining [K]. Analogy: leaving the lights and the heating on in a rented house.
12. *Free tiers in 2026 and the safety routine.* Teach this last, as a checklist the learner follows before touching any console (details in Q3).

**Pacing suggestion [K].** Each 40-minute lesson works well as 5 min warm-up guess → 20 min concepts (about 2 min per item, skipping the deep ones) → 12 min hands-on → 3 min explain-it-back. For lesson 1, cut NAT and traceroute to one minute each if time is short; for lesson 2, keep L4/L7 and CDN to a single diagram.

### Gaps
- I could not open Cloudflare's Learning Center DNS pages (for example "What is DNS?") because the sandbox blocks the site; only the DNS-security, TLS-handshake and "How does SSL work" pages appeared in search, so the analogies above are mine, not Cloudflare's wording.
- No source was fetched for the IaaS/PaaS/SaaS definitions or the "pizza as a service" analogy; both are standard [K].
- The cross-cloud table beyond the rows confirmed by Google is unverified; the Google comparison page itself was last updated in December 2024 according to the search summary.

---

## Q2. What do beginners get wrong?

### Takeaway
The worst mistakes are ones that "work on my machine" and then fail or leak in production: binding to the wrong address, publishing Docker ports to the whole network, trusting `dig` or a browser while caches lie, misreading `/N`, treating HTTPS as a trust badge, expecting a stateless NACL to behave like a stateful security group, and assuming a free tier caps spending. Each can be shown in under five minutes with a local demo, and those demos are in Q4.

### Cited Findings

**Lesson 1: addresses, ports, DNS**
- *0.0.0.0 vs 127.0.0.1 inside containers.* A server inside a container that binds to 127.0.0.1 cannot be reached through a published port; the same server bound to 0.0.0.0 can. Real output: `docker run -p 127.0.0.1:9001:8000 python:3.12-alpine python -m http.server 8000 --bind 127.0.0.1` → `curl http://127.0.0.1:9001/` gives `curl: (56) Recv failure: Connection reset by peer`; the same container with `--bind 0.0.0.0` on port 9002 returns `200` — [L]. (On Docker Desktop for Mac the curl error may read `Empty reply from server` instead [K].)
- *How the bind shows up on the host.* `lsof -iTCP -sTCP:LISTEN -n -P` shows `TCP 127.0.0.1:9101 (LISTEN)` for a server bound to loopback and `TCP *:9102 (LISTEN)` for one bound to 0.0.0.0 (`*` means all interfaces) — [L]. `lsof` exists on macOS with the same flags [K].
- *Docker publishes to the world by default.* Docker's docs say: "Publishing container ports is insecure by default. Meaning, when you publish a container's ports it becomes available not only to the Docker host, but to the outside world as well. If you include the localhost IP address (127.0.0.1, or ::1) with the publish flag, only the Docker host can access the published container port", for example `docker run -p 127.0.0.1:8080:80 -p '[::1]:8080:80' nginx`. Before Docker Engine 28.0.0, even ports published to localhost could be reached by hosts on the same L2 segment (moby/moby#45610) — [Docker docs: Port publishing](https://github.com/docker/docs/blob/main/content/manuals/engine/network/port-publishing.md) (opened from the docker/docs source repo; the rendered page lives under docs.docker.com/engine/network/, a derived path).
- *CIDR math.* `/24` is not "24 addresses". It is 24 fixed bits, which leaves 256 addresses, and a larger prefix number means a smaller network (/16 = 65,536) — [L] Python `ipaddress`. In AWS a /24 yields 251 usable addresses because 5 are reserved, and the smallest subnet is /28 = 16 addresses (11 usable) — [AWS: Subnet CIDR blocks](https://docs.aws.amazon.com/vpc/latest/userguide/subnet-sizing.html) (search).
- *"Private" is not "special" for 100.64.0.0/10.* Python classifies 100.64.0.1 as neither private nor global, because it is carrier-grade NAT shared space. Beginners who see a 100.x address on a phone hotspot or Tailscale assume it is public — [L].
- *DNS caching and TTL.* Resolvers may keep an answer until its TTL expires; Cloudflare proxied records use a fixed 300-second TTL, so "recursive resolvers will not cache the old address for longer than 300 seconds" — [Cloudflare DNS docs: Proxy status](https://developers.cloudflare.com/dns/proxy-status/) (search). That is why a changed record "doesn't work yet" for some people and not others.
- *"Is it DNS?"* Julia Evans has a whole post on telling whether a problem is caused by DNS, which is a good reading for the misconceptions slot — [jvns.ca: how do you tell if a problem is caused by DNS?](https://jvns.ca/blog/2021/11/04/how-do-you-tell-if-a-problem-is-caused-by-dns/) (search).

**Lesson 2: HTTP, TLS, proxies**
- *"HTTPS means safe."* TLS proves only that the server controls the domain name in the certificate, and it encrypts the traffic. Let's Encrypt issues a certificate to anyone who can prove control of the domain, by serving a token over HTTP on port 80 (HTTP-01) or publishing a DNS TXT record (DNS-01). So the padlock says "this is really example-phish.com and nobody can read your traffic", not "this site is honest" — [Let's Encrypt: Challenge types](https://letsencrypt.org/docs/challenge-types/) (opened from `letsencrypt/website` source; URL path from the docs folder).
- *"I'll get a Let's Encrypt cert for localhost."* Let's Encrypt does not issue certificates for "localhost" because "nobody uniquely owns it". The recommended option is to generate your own certificate, self-signed or signed by a local root — [Let's Encrypt: Certificates for localhost](https://letsencrypt.org/docs/certificates-for-localhost/) (opened from source).
- *"HTTP-01 works on any port / gives me a wildcard."* HTTP-01 "can only be done on port 80", fails if an ISP blocks port 80, and "cannot be used to issue wildcard certificates"; DNS-01 is needed for wildcards — [Let's Encrypt: Challenge types](https://letsencrypt.org/docs/challenge-types/) (opened from source).
- *"Certificates last a year; I'll renew by hand."* Let's Encrypt certificates are 90 days today. The default `classic` profile moves to **64 days on February 10, 2027** and **45 days on February 16, 2028**, with the authorization reuse period shrinking from 30 days to 10 days and then to 7 hours. An opt-in `tlsserver` profile has issued 45-day certificates since May 13, 2026, and an opt-in `shortlived` profile issues 160-hour (about 6-day) certificates, generally available since January 15, 2026. IP-address certificates must be short-lived. Industry rules cap all public certificates at 47 days from March 15, 2029. Let's Encrypt says "manually renewing certificates is not recommended" and advises renewing at about two thirds of the lifetime, or using ACME Renewal Information (ARI). It suggests grepping cron jobs for hard-coded 83, 80 or 60-day renewal intervals — [LE: Decreasing certificate lifetimes to 45 days (2025-12-02)](https://letsencrypt.org/2025/12/02/from-90-to-45) (opened from source; URL appears as a link inside LE's own pages); [LE: 64-day certificate lifetimes coming Feb 2027 (2026-10-07)](https://letsencrypt.org/2026/10/07/64-day-certs) (opened from source; URL derived from date + slug pattern); [LE: 6-day and IP certificates GA (2026-01-15)](https://letsencrypt.org/2026/01/15/6day-and-ip-general-availability) (opened from source; URL derived); [LE: Certificate lifetime rationale and plans](https://letsencrypt.org/docs/cert-lifetimes/) (opened from source, lastmod 2026-07-22; a localized copy appeared in search).
- *"My browser checks revocation with OCSP."* Let's Encrypt turned off its OCSP service on August 6, 2025, and now publishes revocation only through CRLs. It cited privacy (an OCSP responder learns which site each IP visits); at its peak it handled about 340 billion OCSP requests per month — [LE: OCSP service has reached end of life](https://letsencrypt.org/2025/08/06/ocsp-service-has-reached-end-of-life) (opened from source; URL derived). Old tutorials that teach `openssl ocsp` against Let's Encrypt are out of date.
- *"`curl -k` fixes the TLS error."* Real output: `curl https://localhost:8443/` against a self-signed cert gives `curl: (60) SSL certificate problem: self-signed certificate`. The correct fix for a lab is `--cacert localhost.crt`, which succeeds and still verifies; `-k` silently turns verification off — [L].
- *"The app sees the client's IP."* Behind a reverse proxy the backend sees the proxy's address. In the [L] nginx lab the backend (traefik/whoami) reported `RemoteAddr: 172.19.0.4:46980` (the nginx container) while the real caller only appeared in `X-Forwarded-For: 172.19.0.1` and `X-Real-Ip` — [L]. MDN's proxy guide covers forwarding headers — [MDN: Proxy servers and tunneling](https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Proxy_servers_and_tunneling) (opened from source; URL derived from slug).
- *"Round robin alternates perfectly."* With two upstreams in nginx, 4 requests landed `A, A, A, B` in the [L] run, not `A, B, A, B` — [L]. The likely cause is that each nginx worker process keeps its own round-robin position unless the upstream has a shared `zone` [K].
- *"HTTP remembers me."* HTTP is stateless; sessions come from cookies — [MDN: Overview of HTTP](https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Overview) (opened from source).

**Lesson 3: cloud networking, IAM, billing**
- *Security groups are stateful, NACLs are stateless.* Security groups "use connection tracking", so reply traffic for an allowed connection is permitted without a matching outbound rule. NACLs "are stateless. Therefore, you must include a rule that allows responses to the inbound traffic" (that is, the ephemeral port range). SGs are instance-level and allow-only; NACLs are subnet-level, take allow and deny rules, and are evaluated in number order until a match. AWS positions NACLs as a coarse secondary control ("to deny a specific subset of traffic" or "high-level subnet guard rails") — [AWS VPC: Network ACLs](https://docs.aws.amazon.com/vpc/latest/userguide/vpc-network-acls.html) (search); [AWS VPC: NACL example](https://docs.aws.amazon.com/vpc/latest/userguide/nacl-examples.html) (search); [AWS EC2: Security group connection tracking](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/security-group-connection-tracking.html) (search); [AWS EC2: Security groups](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ec2-security-groups.html) (search).
- *"I removed the rule, so the connection is cut."* In AWS, changing an SG rule does not immediately end already-tracked connections; a NACL that blocks traffic does break existing connections — [AWS EC2: connection tracking](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/security-group-connection-tracking.html) (search). Azure NSGs behave the same way: "Network security group rules only affect new connections ... if you have an active SSH session" it stays up. NSGs are stateful through flow records ("If you specify an outbound security rule to any address over port 80 ... it's not necessary to specify an inbound security rule for the response") — [Azure: Network security groups overview](https://github.com/MicrosoftDocs/azure-docs/blob/main/articles/virtual-network/network-security-groups-overview.md) (opened from source, ms.date 2025-07-15).
- *"The cloud provider handles security."* Only security *of* the cloud; with VMs you patch the guest OS and configure the security group yourself — [AWS Well-Architected: Shared responsibility](https://docs.aws.amazon.com/wellarchitected/latest/security-pillar/shared-responsibility.html) (search).
- *"I'll just use the root account / long-lived access keys."* AWS recommends temporary credentials through roles for humans and workloads. Long-term access keys only where there is no alternative, rotated or removed. MFA on the root user and no root access keys. Least privilege, refined over time with last-accessed data and IAM Access Analyzer — [AWS IAM best practices](https://aws.amazon.com/iam/resources/best-practices/) (search); [AWS: Root user best practices](https://docs.aws.amazon.com/IAM/latest/UserGuide/root-user-best-practices.html) (search).
- *"S3 ≈ Cloud Storage, so they behave the same."* Google warns that similar services can work differently; IAM in particular is set on the resource in GCP — [Google: Migrate from AWS, get started](https://docs.cloud.google.com/architecture/migration-from-aws-get-started) (search).
- *"Free tier means free."* Azure's free quantities reset monthly and "doesn't roll over" (for example, use 2 GB of a 5 GB File-storage allowance and the other 3 GB are lost). Resources created outside the portal's Free services page may not default to the free tier — [Azure: Avoid charges with your free account](https://github.com/MicrosoftDocs/azure-docs/blob/main/articles/cost-management-billing/manage/avoid-charges-free-account.md) (opened from source, ms.date 2026-03-03); [Azure: Create free services](https://learn.microsoft.com/azure/cost-management-billing/manage/create-free-services) (search; source opened). The GCP always-free e2-micro is free only in us-west1, us-central1 or us-east1; other regions are charged — [Google Cloud free program page](https://cloud.google.com/free-trial/) (search). AWS: "exceeding the limit of the Free Tier generally results in a billable charge" on a paid plan — [AWS: Control your costs tutorial](https://docs.aws.amazon.com/hands-on/latest/control-your-costs-free-tier-budgets/control-your-costs-free-tier-budgets.html) (search).

### Inferences
Further high-frequency mistakes worth a "myth vs fact" box [K]:
- **"localhost = 127.0.0.1."** On macOS, `localhost` may resolve to `::1` (IPv6) first. A server bound only to `127.0.0.1` then looks "down" to clients that try `::1`, and vice versa. Use `127.0.0.1` explicitly when debugging.
- **"0.0.0.0 is an address I can browse to."** It is a bind wildcard. Some tools accept it as a destination and quietly map it to localhost, which hides the confusion.
- **"`dig` shows what my app sees."** `dig` asks a DNS server directly and ignores `/etc/hosts` and the macOS resolver cache. `dscacheutil -q host -a name example.com` shows what macOS apps actually get. On macOS, `ping`, `curl` and browsers use the system resolver.
- **"I changed DNS; flushing my cache fixes it for everyone."** Only your machine's cache; the recursive resolver and other users' caches keep the old answer until the TTL runs out. Lower the TTL a day before a planned change. Negative answers (NXDOMAIN) are cached too.
- **"ping failed, so the host is down."** ICMP is often blocked (AWS security groups do not allow it unless you add a rule). Test the actual port with `nc -zv host 443` or `curl`.
- **"traceroute `* * *` means broken."** Many routers simply don't answer TTL-expired probes.
- **"My laptop's IP is my public IP."** The laptop has a private address (192.168.x.x or 10.x.x.x) behind home NAT. The public address belongs to the router and is shared by the whole household.
- **"`ss` works on my Mac."** `ss` is Linux-only (iproute2). On macOS use `lsof -iTCP -sTCP:LISTEN -n -P` or `netstat -anv -p tcp`. The learner will meet `ss` on Linux servers and in containers, so teach both.
- **"`nc` flags are universal."** macOS ships BSD netcat (`nc -l 9000`); some Linux variants need `nc -l -p 9000`.
- **"401 and 403 are the same"; "502 means my code crashed."** 401 = who are you?; 403 = I know you, and no. 502 = the proxy got a bad or no answer from the upstream (often the app isn't listening, or is bound to 127.0.0.1 inside a container). 504 = the upstream was too slow.
- **"An L7 load balancer and a reverse proxy are different animals."** An L7 load balancer is a reverse proxy with several backends and health checks.
- **"HTTPS hides which site I visit."** The destination IP, and usually the hostname in the SNI, are still visible unless Encrypted Client Hello is used. Cloudflare's ECH material exists if a "go deeper" box is wanted ([Cloudflare blog: Handshake Encryption: Endgame](https://blog.cloudflare.com/handshake-encryption-endgame-an-ech-update/), search).
- **"A public subnet is public because I named it public."** Only a route `0.0.0.0/0 → internet gateway` (plus a public IP on the instance) makes it public.
- **"Stopped means free."** A stopped VM still bills for its disks and any reserved public IP. Deleting a VM may leave volumes, snapshots and IPs behind, and NAT gateways and load balancers bill hourly even with no traffic.
- **"AWS Budgets will stop me spending."** Budgets alert; they do not cap spending (unless you configure budget actions). The true caps are the AWS Free plan (the account closes instead of billing; see Q3) and the Azure free-account spending limit.
- **"Resources only exist in the region I'm looking at."** Consoles are scoped to one region; forgotten resources in another region keep billing. Teach "one region, always" for labs.
- **"Security group = NACL."** Learners add an outbound NACL rule for port 443 and forget the inbound ephemeral range 1024–65535 for replies, then blame the app.

### Gaps
- I did not find a citable source for the macOS `localhost` → `::1` ordering or for `dig` bypassing `/etc/hosts` on macOS. Both are well known but [K]; the writer should run them on a Mac before stating them.
- I did not verify nginx's per-worker round-robin behaviour against the nginx docs (nginx.org was not searched); the observed `A, A, A, B` output is real [L], but the explanation is [K].
- I found no source in this session for the AWS charge on public IPv4 addresses or for NAT gateway hourly pricing. Mention them as risks, but do not quote prices without checking the AWS pricing pages.

---

## Q3. What are the 2026 free tier rules for AWS, Azure and Google Cloud, and the safest way to avoid surprise bills?

### Takeaway
All three providers now have a credit-based trial that **cannot charge you while you stay on it**. AWS has a "Free plan" ($100 up front plus up to $100 more by doing exploration activities, for 6 months or until the credits run out, after which the account closes instead of billing). Azure gives $200 for 30 days behind a spending limit that is on by default, plus 12 months of limited free quantities once you upgrade. Google Cloud gives $300 for 90 days and does not bill until you activate a paid account, plus an always-free tier (one e2-micro in three US regions). The safest learner routine: stay on the trial or free plan (don't upgrade), use one region, set a zero-spend and a small monthly budget alert on day one, enable MFA, never create root keys, build each lab in one deletable unit (resource group, project or Terraform stack), and tear it down the same day.

### Cited Findings

**AWS (new accounts created on or after July 15, 2025)**
- New customers get up to $200 in Free Tier credits: "$100 USD credits at sign-up and up to $100 USD more to earn as you explore key AWS services" — [AWS What's New, July 2025: Free Tier credits and 6-month free plan](https://aws.amazon.com/about-aws/whats-new/2025/07/aws-free-tier-credits-month-free-plan/) (search; page not opened, aws.amazon.com is blocked from this sandbox); [aws.amazon.com/free](https://aws.amazon.com/free) (search). The AWS cost-control tutorial asks learners to "confirm your $20 in credits" after setting up a budget, which suggests about $20 per exploration activity — [AWS: Control your costs (hands-on tutorial)](https://docs.aws.amazon.com/hands-on/latest/control-your-costs-free-tier-budgets/control-your-costs-free-tier-budgets.html) (search; tutorial updated October 8, 2025 per the search summary).
- At sign-up you choose a **Free plan** or a **Paid plan**. "Your free account plan ends after six months or when your credits are fully used – whichever occurs first. After your free account plan expires, your account closes automatically, and you lose access to your resources and data. AWS retains your content for 90 days before permanently deleting your account". Upgrading within that window (Console → "Upgrade plan") restores access, and remaining credits then apply to future bills until they expire — [AWS Billing: Choosing a plan](https://docs.aws.amazon.com/awsaccountbilling/latest/aboutv2/free-tier-plans.html) (search).
- While on the Free plan you are not charged when credits run out; AWS shuts the account down instead — [Neowin: AWS Free Tier overhauled](https://www.neowin.net/news/aws-free-tier-overhauled-new-users-get-200-in-credits-but-theres-a-catch/) (search, secondary) and [AWS Billing: Choosing a plan](https://docs.aws.amazon.com/awsaccountbilling/latest/aboutv2/free-tier-plans.html) (search).
- Some actions **automatically upgrade** a Free plan to Paid: joining AWS Organizations, setting up an AWS Control Tower landing zone, joining the AWS Partner Network, and similar — [AWS Billing: Choosing a plan](https://docs.aws.amazon.com/awsaccountbilling/latest/aboutv2/free-tier-plans.html) (search). Warn learners not to create an Organization on a learning account.
- On a Paid plan, unused credits can be used "for up to 12 months from your initial sign-up date"; AWS lists "30+ always free" services, and the Free plan gives access to "over 90 services" — [aws.amazon.com/free](https://aws.amazon.com/free) (search). **Conflict:** the AWS Free Tier FAQ says credits expire 12 months after account creation in one section and 6 months in another — [AWS Free Tier FAQs](https://docs.aws.amazon.com/awsaccountbilling/latest/aboutv2/free-tier-FAQ.html) (search summary). The writer should say "check the Credits page in the Billing console".
- Accounts created before July 15, 2025 stay on the legacy 12-month Free Tier program — [AWS: Control your costs tutorial](https://docs.aws.amazon.com/hands-on/latest/control-your-costs-free-tier-budgets/control-your-costs-free-tier-budgets.html) (search).
- Guardrails: AWS Budgets has a **zero spend budget** template that notifies you once spending goes above the Free Tier, and the tutorial recommends a total monthly cost budget for every account. Most accounts are opted in by default to **Free Tier usage alert emails at 85%** of any Free Tier limit; recipients are set in Billing Preferences — [AWS: Control your costs tutorial](https://docs.aws.amazon.com/hands-on/latest/control-your-costs-free-tier-budgets/control-your-costs-free-tier-budgets.html) (search); [AWS Builder Center: 5 practical cost guardrails](https://builder.aws.com/content/3KazOjAkkaPrN2e3UO4CJm9JNZg/5-practical-aws-cost-guardrails-every-student-and-builder-should-set-up) (search, community); [AWS Builder Center: Your first week on AWS, steps to avoid a surprise bill](https://builder.aws.com/content/3KPZGPVEAxaF11ZgjsxIV1WtZXf/your-first-week-on-aws-steps-to-avoid-a-surprise-bill) (search, community).
- AWS keeps an official checklist for tracking down unexpected charges — [AWS Billing: Understanding unexpected charges](https://docs.aws.amazon.com/awsaccountbilling/latest/aboutv2/checklistforunwantedcharges.html) (search; contents not read).
- Closing a standard AWS account starts a 90-day post-closure period during which you can reopen it; after that it is permanently closed — [AWS: Close an AWS account](https://docs.aws.amazon.com/accounts/latest/reference/manage-acct-closing.html) (search).

**Azure**
- "Eligible new users get $200 Azure credit in your billing currency for the first 30 days and a limited quantity of free services for 12 months." "As long as you have unexpired credit or you use only free services within the limits, you're not charged." When credit runs out or the 30 days end, the subscription and services are **disabled**, and you must upgrade (pay-as-you-go) to continue. After upgrading you keep the free quantities for the rest of the 12 months and pay only for usage beyond them. At the end of 12 months you pay pay-as-you-go rates for anything still running — [Azure: Avoid charges with your free account](https://github.com/MicrosoftDocs/azure-docs/blob/main/articles/cost-management-billing/manage/avoid-charges-free-account.md) (opened from source, ms.date 2026-03-03).
- The $200 credit works on any service "except for third-party Marketplace purchases". Unused credit after 30 days "is lost". The 12-month free quantities include three burstable VM types (**B1S, B2pts v2 (Arm), B2ats v2 (AMD), up to 750 hours per month**). Free services can be created in any region, and 750 hours can be split across instances (for example, 5 B1S VMs for 150 hours each). Create resources from the portal's **Free services** page, because "if you create resources outside of the Free services pages, free tiers or free resource configuration options aren't always selected by default" — [Azure: Create free services](https://learn.microsoft.com/azure/cost-management-billing/manage/create-free-services) (search; source opened, ms.date 2026-03-03).
- **Spending limit:** on by default for free accounts and equal to the credit (USD 200), and it cannot be changed. When it is hit, "Azure resources that you deployed are removed from production and your Azure virtual machines are stopped and de-allocated. The data in your storage accounts are available as read-only". Upgrading to pay-as-you-go removes the limit; it is not available on pay-as-you-go subscriptions — [Azure: Spending limit](https://github.com/MicrosoftDocs/azure-docs/blob/main/articles/cost-management-billing/manage/spending-limit.md) (opened from source, ms.date 2026-04-29).
- Always-free services: Microsoft's FAQ says 55+; a regional landing page says 65+ (**conflict** in Microsoft's own pages) — [Azure free account FAQ](https://azure.microsoft.com/free/free-account-faq) (search).
- Students: $100 credit valid for 12 months with no credit card (Azure for Students) — [Telkom University page](https://365.telkomuniversity.ac.id/?p=35011) (search; secondary source, low confidence).

**Google Cloud**
- New customers get a **90-day Free Trial with US$300** in credit; "You won't be charged until you activate your full paid account"; a credit card is required. The trial credit "can't pay for Gemini API costs in AI Studio" — [Google Cloud: $300 in free credit for new customers](https://cloud.google.com/free-trial/) (search; snippets from Google's localized copies of the same page).
- **Always Free** is separate from the trial, has no end date, covers 20+ products with monthly limits, and is not charged against the $300 credit. Compute Engine: one non-preemptible **e2-micro** VM per month in **us-west1, us-central1 or us-east1**, plus **30 GB-months of standard persistent disk**. The allowance is measured in hours (free up to the number of hours in the month) — [Google Cloud free program page](https://cloud.google.com/free-trial/) (search).

### Inferences
**Recommended safety routine to teach (a "before you click Create" checklist).** The structure follows the sources above; the step order is mine [K]:
1. **Default to local.** Every required exercise in these 3 lessons runs on the Mac with Docker. Cloud steps are optional and clearly marked.
2. **AWS: pick the Free plan, not the Paid plan,** for a learning account. Its failure mode is "account closes" rather than "card charged" [S]. Don't join an Organization or Control Tower (auto-upgrade) [S].
3. **Day-one guardrails, before creating anything:** root MFA, no root access keys, an admin identity with MFA for daily use [S IAM best practices]; a zero-spend budget plus a monthly budget of about $5 with email alerts at 50/80/100%; keep the 85% Free Tier alerts on [S AWS tutorial]. Azure: leave the spending limit on [S]; after any upgrade, create a Cost Management budget [K]. GCP: stay in the trial; create a Cloud Billing budget with alerts, and remember budget alerts notify but do not stop spending [K].
4. **One region, always** (for GCP's always-free VM it must be us-west1, us-central1 or us-east1 [S]).
5. **Build every lab as one deletable unit:** an Azure resource group, a GCP project, or a Terraform stack, so teardown is one command (`az group delete`, delete the project, `terraform destroy`) [K].
6. **Watch the known bill-shock items** [K]: NAT gateways, load balancers, public IPv4 addresses, unattached volumes and snapshots, data egress, managed databases left running, and anything in another region. Never commit access keys to Git; leaked keys are a classic path to large crypto-mining bills.
7. **Teardown ritual:** delete resources, then check the billing console's "cost by service" the next day, then (AWS) use the unexpected-charges checklist [S].
8. **Exit plan:** when finished, close the account. On AWS there is a 90-day reopen window [S].

Short teaching table [S for the facts above]:

| | AWS (accounts from Jul 15, 2025) | Azure | Google Cloud |
|---|---|---|---|
| Trial credit | $100 + up to $100 earned | $200 | $300 |
| Trial length | 6 months or until credits run out | 30 days | 90 days |
| Can the trial bill your card? | No on the Free plan (account closes) | No while the spending limit is on (services disabled) | No until you activate a paid account |
| Ongoing free | 30+ always-free services | 12 months of limited quantities (after upgrade) + 55–65 always-free services | Always Free: 20+ products, e2-micro in 3 US regions |
| Built-in guardrail | Zero-spend budget template, 85% Free Tier alerts | Spending limit (default on, free account only) | Budgets and alerts (notify only [K]) |

### Gaps
- I could not open any of the three official free-tier pages (aws.amazon.com, azure.microsoft.com and cloud.google.com/docs.cloud.google.com are blocked from this sandbox). AWS and GCP figures come from search snippets of official pages; Azure figures come from Microsoft's docs source on GitHub, which is strong evidence.
- Not confirmed: what exactly happens to GCP resources at the end of the 90-day trial (whether there is a grace period before deletion), and GCP always-free egress and Cloud Run / Cloud Storage limits.
- AWS credit expiry (6 vs 12 months) is contradictory in AWS's own FAQ per the search summary. The exact list of activities that earn the extra $100 (and the $20 each) was not confirmed.
- I found no official source for Azure for Students terms in this session.

---

## Q4. Which small hands-on exercises work on a Mac for free? (with example commands and expected output)

### Takeaway
Everything in lessons 1 and 2 can be done on a Mac with built-in tools (`dig`, `nslookup`, `ping`, `traceroute`, `curl`, `openssl`, `nc`, `lsof`, `netstat`, `route`, `ipconfig`, `scutil`) plus Docker Desktop. The two strongest exercises, both verified end to end here, are (a) an nginx reverse proxy load-balancing two `traefik/whoami` containers and (b) TLS on localhost with a self-signed certificate inspected with `curl -v` and `openssl`. Lesson 3 can be done fully offline as design exercises (carve a VPC, write route tables, write an IAM policy), with an optional and clearly cost-warned cloud step.

### Cited Findings
- Verified [L] reverse-proxy + load-balancer lab (copy-paste ready; use `mirror.gcr.io/library/nginx` only if Docker Hub rate-limits, as happened here with HTTP 429):
  ```bash
  mkdir -p ~/netlab && cd ~/netlab
  cat > default.conf <<'EOF'
  upstream app { server app1:80; server app2:80; }
  server {
      listen 80;
      location / {
          proxy_pass http://app;
          proxy_set_header Host $host;
          proxy_set_header X-Real-IP $remote_addr;
          proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
      }
  }
  EOF
  docker network create lab
  docker run -d --rm --name app1 --network lab traefik/whoami
  docker run -d --rm --name app2 --network lab traefik/whoami
  docker run -d --rm --name proxy --network lab -p 127.0.0.1:8080:80 \
    -v "$PWD/default.conf:/etc/nginx/conf.d/default.conf:ro" nginx:1.27-alpine
  curl -s http://127.0.0.1:8080/
  ```
  Real output (trimmed): `Hostname: da62c586727d` … `RemoteAddr: 172.19.0.4:46980` … `GET / HTTP/1.1` … `X-Forwarded-For: 172.19.0.1` / `X-Real-Ip: 172.19.0.1`. `docker ps` shows `proxy 127.0.0.1:8080->80/tcp` while `app1`/`app2` show only `80/tcp` (not published). Over 4 requests the Hostname changed between the two containers. `curl -v` showed `> GET / HTTP/1.1`, `> Host: 127.0.0.1:8080`, `< HTTP/1.1 200 OK`, `< Server: nginx/1.27.5`. The host listener was `TCP 127.0.0.1:8080 (LISTEN)` — [L].
- Verified [L] TLS-on-localhost lab:
  ```bash
  openssl req -x509 -newkey rsa:2048 -nodes -keyout localhost.key -out localhost.crt \
    -days 7 -subj "/CN=localhost" -addext "subjectAltName=DNS:localhost,IP:127.0.0.1"
  # nginx server block: listen 443 ssl; ssl_certificate/ssl_certificate_key; proxy_pass http://app1:80;
  # run with -p 127.0.0.1:8443:443 and the cert, key and conf mounted read-only
  curl https://localhost:8443/                      # -> curl: (60) SSL certificate problem: self-signed certificate
  curl --cacert localhost.crt https://localhost:8443/   # -> works (whoami output)
  curl -v --cacert localhost.crt -o /dev/null https://localhost:8443/
  ```
  Real `curl -v` handshake lines: `ALPN: curl offers h2,http/1.1` → `TLSv1.3 (OUT), TLS handshake, Client hello (1)` → `(IN) Server hello (2)` → `(IN) Encrypted Extensions (8)` → `(IN) Certificate (11)` → `(IN) CERT verify (15)` → `(IN) Finished (20)` → `(OUT) Finished (20)` → `SSL connection using TLSv1.3 / TLS_AES_256_GCM_SHA384 / X25519 / RSASSA-PSS` → `ALPN: server accepted http/1.1`. `echo | openssl s_client -connect 127.0.0.1:8443 -servername localhost` printed `subject=CN = localhost`, `issuer=CN = localhost` (subject = issuer, which is what self-signed means), `Protocol : TLSv1.3`, `Verify return code: 18 (self-signed certificate)`. Piping that into `openssl x509 -noout -subject -issuer -dates -ext subjectAltName` printed `notBefore=Oct 30 04:40:36 2026 GMT`, `notAfter=Nov  6 04:40:36 2026 GMT`, `DNS:localhost, IP Address:127.0.0.1` — [L]. On macOS, curl's `-v` wording differs slightly (Apple builds curl against LibreSSL or SecureTransport), and the system `openssl` is LibreSSL, whose `-addext` support depends on the version; Homebrew `openssl@3` avoids that [K].
- Let's Encrypt's localhost guidance supports this exact lab: make your own certificate, self-signed or signed by your own local root — [LE: Certificates for localhost](https://letsencrypt.org/docs/certificates-for-localhost/) (opened from source).
- Verified [L] bind-address lab: `python3 -m http.server 9101 --bind 127.0.0.1` and `python3 -m http.server 9102 --bind 0.0.0.0`; `lsof -iTCP -sTCP:LISTEN -n -P` → `TCP 127.0.0.1:9101 (LISTEN)` and `TCP *:9102 (LISTEN)`. Container variant: published port + app bound to 127.0.0.1 → `Recv failure: Connection reset by peer`; bound to 0.0.0.0 → `200` — [L].
- Verified [L] netcat: `nc -l 127.0.0.1 9200` in one terminal and `echo "hello over TCP" | nc 127.0.0.1 9200` in another delivered `hello over TCP`. `nc -zv 127.0.0.1 8080` → `Connection to 127.0.0.1 8080 port [tcp/http-alt] succeeded!`; `nc -zv 127.0.0.1 9999` → `connect to 127.0.0.1 port 9999 (tcp) failed: Connection refused` — [L] (Linux OpenBSD-netcat; on macOS the listen syntax is `nc -l 9200` and the success line reads similarly [K]).
- Verified [L] CIDR checks that a learner can run with no installs: `python3 -c "import ipaddress as i; n=i.ip_network('10.0.0.0/16'); print(n.num_addresses, list(n.subnets(new_prefix=24))[:3])"` → `65536 [IPv4Network('10.0.0.0/24'), IPv4Network('10.0.1.0/24'), IPv4Network('10.0.2.0/24')]` — [L].
- Free online DNS playground: Mess With DNS gives a real subdomain, shows incoming queries live, and deletes records after a week — [messwithdns.net/about](https://messwithdns.net/about.html) (search).
- Julia Evans' "tiny DNS resolver" comic has companion code at github.com/jvns/tiny-resolver, which is a stretch exercise for strong learners; there is also the free "Implement DNS in a Weekend" guide — [wizardzines: tiny dns resolver](https://wizardzines.com/comics/tiny-dns-resolver) (search); [jvns.ca: Implement DNS in a Weekend](https://jvns.ca/blog/2023/05/12/introducing-implement-dns-in-a-weekend/) (search).

### Inferences
Exercise menu per lesson. Commands are for macOS (zsh). Outputs marked "shape" are typical and illustrative [K]; the writer should run them on a Mac before quoting exact text.

**Lesson 1 exercises (about 12 min of hands-on; pick 3–4)**
1. *Where am I on the network?*
   ```bash
   ipconfig getifaddr en0          # shape: 192.168.1.23   (private, from your router's DHCP)
   ifconfig en0 | grep 'inet '     # shape: inet 192.168.1.23 netmask 0xffffff00 broadcast 192.168.1.255
   route -n get default            # shape: gateway: 192.168.1.1 / interface: en0
   netstat -rn -f inet | head      # route table: "default 192.168.1.1 UGScg en0", "127 127.0.0.1 UCS lo0"
   curl -s https://ifconfig.me; echo   # your public IP (the router's): compare with en0 to see NAT
   ```
   Question to ask: why do the two addresses differ, and what does `0xffffff00` mean? (= /24.)
2. *CIDR by hand, checked by Python.* Carve 10.0.0.0/16 into four /24s for "public-a, public-b, private-a, private-b"; work out how many addresses each has normally (256) and in AWS (251); is 10.0.3.7 in 10.0.2.0/23? Verify with `python3 -c "import ipaddress as i; print(i.ip_address('10.0.3.7') in i.ip_network('10.0.2.0/23'))"` → `True`.
3. *Read the phone book with dig.*
   ```bash
   dig +short example.com A          # one or more IPv4 addresses
   dig +short example.com AAAA       # IPv6 addresses
   dig +short www.github.com CNAME   # shape: github.com.  (an alias)
   dig +short gmail.com MX           # shape: 5 gmail-smtp-in.l.google.com.  (priority + host)
   dig +short example.com NS         # the authoritative nameservers
   dig +short google.com TXT         # verification and SPF strings, e.g. "v=spf1 include:_spf.google.com ~all"
   dig example.com                   # read the ANSWER SECTION: name, TTL, class, type, value
   dig @1.1.1.1 example.com | grep -A2 'ANSWER SECTION'   # run twice: the TTL counts down (cache)
   dig +trace example.com            # root (.) -> com. -> example.com's nameservers -> answer
   nslookup example.com              # the older tool, same question
   dig +tcp example.com              # same query over TCP instead of UDP
   ```
4. */etc/hosts overrides DNS, and dig doesn't care.*
   ```bash
   sudo sh -c 'echo "127.0.0.1 myapp.test" >> /etc/hosts'
   ping -c1 myapp.test                       # PING myapp.test (127.0.0.1)
   dscacheutil -q host -a name myapp.test    # ip_address: 127.0.0.1
   dig +short myapp.test                     # (empty) because dig asks DNS servers, not /etc/hosts
   sudo sed -i '' '/myapp.test/d' /etc/hosts # clean up
   sudo dscacheutil -flushcache; sudo killall -HUP mDNSResponder   # flush the macOS DNS cache
   ```
5. *Who is listening on which door?* Start the two `python3 -m http.server` processes (127.0.0.1 vs 0.0.0.0) and run `lsof -iTCP -sTCP:LISTEN -n -P` [L output above]. Stretch: from a phone on the same Wi-Fi, open `http://<laptop-ip>:9102` (works if the macOS firewall allows it) and `:9101` (fails). Then `docker run --rm -p 8080:80 nginx` vs `-p 127.0.0.1:8080:80` and compare `lsof` (`*:8080` vs `127.0.0.1:8080`).
6. *Talk raw TCP with nc.* `nc -l 9200` in one tab, `nc 127.0.0.1 9200` in another, and type; then `nc -zv 127.0.0.1 9200` and `nc -zv 127.0.0.1 9999` (refused). Bonus: `printf 'GET / HTTP/1.1\r\nHost: example.com\r\nConnection: close\r\n\r\n' | nc example.com 80` speaks HTTP by hand, which is a perfect bridge to lesson 2.
7. *ping and traceroute.* `ping -c 3 1.1.1.1` (shape: `64 bytes from 1.1.1.1: icmp_seq=0 ttl=57 time=12.3 ms`, then a summary with packet loss and min/avg/max); `traceroute -n 1.1.1.1` (shape: numbered hops, first one is your router 192.168.1.1, some `* * *`).
8. *Mess With DNS (browser, free):* create an A record and a CNAME on your messwithdns subdomain, `dig` it from the terminal, and watch the query appear live [S].

**Lesson 2 exercises (pick 3–4)**
1. *See HTTP raw:* `curl -v http://example.com -o /dev/null` and label each `>` (request) and `<` (response) line; then `curl -I https://example.com` (headers only).
2. *Status codes and redirects:* `curl -sI http://github.com | head -3` (shape: `HTTP/1.1 301 Moved Permanently` + `Location: https://github.com/`); `curl -sIL http://github.com | grep -E '^HTTP|^location'` follows it; `curl -s -o /dev/null -w '%{http_code}\n' https://example.com/does-not-exist`.
3. *Where does time go?* (ties lessons 1 and 2 together)
   ```bash
   curl -s -o /dev/null -w 'dns %{time_namelookup}s  tcp %{time_connect}s  tls %{time_appconnect}s  first-byte %{time_starttransfer}s  total %{time_total}s\n' https://example.com
   ```
   Run it twice; DNS time drops on the second run (cache).
4. *Inspect a real certificate:*
   ```bash
   curl -sv https://letsencrypt.org -o /dev/null 2>&1 | grep -E 'subject:|issuer:|expire date:|SSL connection'
   echo | openssl s_client -connect letsencrypt.org:443 -servername letsencrypt.org 2>/dev/null \
     | openssl x509 -noout -subject -issuer -dates -ext subjectAltName
   ```
   Ask: who issued it, how many days is it valid (expect about 90 today, 64 after Feb 10, 2027 [S LE]), and which names does it cover? Don't hard-code intermediate CA names in the lesson. Let's Encrypt announced a new "Generation Y" hierarchy (two new roots, six new intermediates, YE1–YE3 among them) on 2025-11-24, and the search results report the switch for the default profile on May 13, 2026, so names seen in older tutorials (R3, R10/R11, E5/E6) are stale — [LE: New "Generation Y" hierarchy](https://letsencrypt.org/2025/11/24/gen-y-hierarchy) (opened from source; URL derived from date/slug pattern); [Neowin: Let's Encrypt launches "Generation Y"](https://www.neowin.net/news/lets-encrypt-launches-generation-y-shortens-cert-lifetimes-to-45-days/) (search). The intermediate names in older tutorials are [K].
5. *TLS on localhost* (the [L] lab above): self-signed cert → error 60 → `--cacert` → read the handshake lines.
6. *Reverse proxy and load balancer* (the [L] lab above): find the client IP in `X-Forwarded-For`; stop `app2` (`docker stop app2`) and watch nginx keep serving from `app1`; stop both and see `502 Bad Gateway`. That last step teaches what a 502 means.
7. *Cookies:* `curl -s -c jar.txt -o /dev/null https://github.com && cat jar.txt` (cookies the server set), then send them back with `-b jar.txt`.
8. *Bypass DNS:* `curl --resolve example.com:443:<IP from dig> https://example.com -I` shows that the Host header and SNI come from the URL, not the IP.

**Lesson 3 exercises (local design work, free; optional cloud step)**
1. *Design a two-AZ VPC on paper:* 10.0.0.0/16; public 10.0.1.0/24 and 10.0.2.0/24, private 10.0.11.0/24 and 10.0.12.0/24; write both route tables (`10.0.0.0/16 local`, `0.0.0.0/0 igw-…` vs `0.0.0.0/0 nat-…`); check the math with Python `ipaddress`; count usable addresses with AWS's 5 reserved [S].
2. *Stateful vs stateless puzzle:* given an SG allowing inbound 443 and a NACL allowing inbound 443 but no outbound 1024–65535, does the response reach the client? (No: the NACL blocks the reply [S AWS].) Fix it with the right outbound rule.
3. *Write a least-privilege IAM policy* (read-only access to one bucket):
   ```json
   {"Version": "2012-10-17",
    "Statement": [{"Effect": "Allow",
                   "Action": ["s3:GetObject", "s3:ListBucket"],
                   "Resource": ["arn:aws:s3:::my-lab-bucket", "arn:aws:s3:::my-lab-bucket/*"]}]}
   ```
   Then ask: why are there two ARNs? (ListBucket acts on the bucket, GetObject on the objects.) What does `"Action": "*"` risk?
4. *Service-map bingo:* fill the AWS/Azure/GCP table from Google's comparison page [S].
5. *Optional cloud step (cost warning: use only a Free plan or trial account, one region, and delete everything the same day):* create an AWS Free plan account → root MFA → zero-spend budget + $5 budget → open CloudShell → `aws sts get-caller-identity` → stop. Or, on GCP, create one e2-micro in us-central1, `ssh` in, run `curl -s ifconfig.me` and `ip route` (now `ss -ltn` works, since it is Linux), then delete the VM and its disk.

### Gaps
- None of the Mac-specific outputs were captured on a real Mac (the sandbox is Linux). In particular the exact wording of macOS `curl -v` TLS lines, LibreSSL `openssl req -addext` support, and Docker Desktop's error text for the 127.0.0.1 bind case should be checked on an Apple Silicon Mac.
- I did not verify whether `traefik/whoami` and `nginx:1.27-alpine` publish arm64 images, which Apple Silicon needs. Both are widely used multi-arch images [K], but the writer should confirm or pin a tag that does.
- `ifconfig.me` and `github.com` cookie behaviour are third-party and can change; I did not test them here.

---

## Q5. Curated resources per lesson (3 to 8 each, exact URLs)

### Takeaway
For each lesson, pair one visual explainer (Julia Evans or a PowerCert/NetworkChuck video), one authoritative reference (MDN, Cloudflare, Let's Encrypt, cloud provider docs) and one hands-on playground. Every URL below appeared in my search results or was opened from the site's source; YouTube URLs are only ones that came back in search (tracking parameters stripped).

### Cited Findings

**Lesson 1: How computers find each other**
| Resource | Type | URL | How verified |
|---|---|---|---|
| Julia Evans, "New zine: How DNS Works!" (28-page zine, launch post) | read | https://jvns.ca/blog/2022/04/26/new-zine--how-dns-works-/ | search |
| Wizard Zines comic, "life of a DNS query" | comic | https://wizardzines.com/comics/life-of-a-dns-query/ | search |
| Mess With DNS (live DNS playground) | hands-on | https://messwithdns.net/about.html | search |
| Julia Evans, "How do you tell if a problem is caused by DNS?" | read | https://jvns.ca/blog/2021/11/04/how-do-you-tell-if-a-problem-is-caused-by-dns/ | search |
| PowerCert, "How a DNS Server (Domain Name System) works." (about 6 min, animated; covers resolver, root, TLD, authoritative) | video | https://www.youtube.com/watch?v=mpQZVYPuDGU | search (youtube.com result; channel identified via aggregator listing) |
| "DNS Records Explained" (A, AAAA, CNAME, MX, TXT, PTR, SOA, SRV; likely PowerCert per its sponsor link, not confirmed) | video | https://www.youtube.com/watch?v=HnUDtycXSNE | search (youtube.com result) |
| NetworkChuck, "what is an IP Address? // You SUCK at Subnetting // EP 1" (+ playlist for CIDR and NAT) | video | https://www.youtube.com/watch?v=5WfiTHiU4x8 ; playlist https://youtube.com/playlist?list=PLIhvC56v63IKrRHh3gvZZBAGvsvOhwrRF | search (youtube.com results) |
| Docker docs, "Port publishing" (why `-p 127.0.0.1:` matters) | docs | https://github.com/docker/docs/blob/main/content/manuals/engine/network/port-publishing.md | opened (source repo) |

Also seen in search, as optional extras: "we're out of IP Addresses….but this saved us (Private IP …)" https://www.youtube.com/watch?v=8bhvn9tQk8o (appears to be from the NetworkChuck series; channel not confirmed); "Computer Networking Course - Network Engineering [CompTIA Network+ Exam Prep]" https://www.youtube.com/watch?v=qiQR5rTSshw (a long full course; I believe it is freeCodeCamp's, but the search did not confirm the channel); Julia Evans networking zine launch https://jvns.ca/blog/networking-zine-launch/ (search); "Implement DNS in a Weekend" https://jvns.ca/blog/2023/05/12/introducing-implement-dns-in-a-weekend/ (search).

**Lesson 2: HTTP, TLS and traffic**
| Resource | Type | URL | How verified |
|---|---|---|---|
| MDN, "Overview of HTTP" | docs | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Overview | opened from mdn/content source; URL derived from slug |
| MDN, "HTTP messages" | docs | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Messages | opened from source; URL derived from slug |
| MDN, "Using HTTP cookies" | docs | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Cookies | opened from source; URL derived from slug |
| Cloudflare, "What happens in a TLS handshake?" | read | https://www.cloudflare.com/learning/ssl/what-happens-in-a-tls-handshake/ | search |
| High Performance Browser Networking, ch. "Transport Layer Security (TLS)" (free online; good on handshake latency, but written in 2013, before TLS 1.3 [K]) | book chapter | https://hpbn.co/transport-layer-security-tls/ | search |
| Let's Encrypt, "Challenge types" (HTTP-01 port 80, DNS-01, wildcards) and "Certificate lifetime rationale and plans" | docs | https://letsencrypt.org/docs/challenge-types/ ; https://letsencrypt.org/docs/cert-lifetimes/ | opened from letsencrypt/website source |
| Cloudflare Learning Paths, "Types of load balancers" (L4 vs L7 vs DNS) | read | https://developers.cloudflare.com/learning-paths/load-balancing/planning/types-load-balancers/ | search |
| "Full HTTP Networking Course" (long video; I believe it is from freeCodeCamp, channel not confirmed by search) | video | https://www.youtube.com/watch?v=2JYT5f2isg4 | search (youtube.com result) |

Also useful: MDN "Proxy servers and tunneling" https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Proxy_servers_and_tunneling (opened from source, URL derived); Cloudflare "How does SSL work?" https://www.cloudflare.com/en-ca/learning/ssl/how-does-ssl-work/ (search; en-ca locale copy); Let's Encrypt "Certificates for localhost" https://letsencrypt.org/docs/certificates-for-localhost/ (opened from source); Let's Encrypt "64-Day Certificate Lifetimes Coming Feb 2027" https://letsencrypt.org/2026/10/07/64-day-certs (opened from source, URL derived from LE's date/slug pattern).

**Lesson 3: The cloud**
| Resource | Type | URL | How verified |
|---|---|---|---|
| Google Cloud, "Compare AWS and Azure services to Google Cloud" (filterable 3-cloud map) | docs | https://docs.cloud.google.com/docs/get-started/aws-azure-gcp-service-comparison | search |
| AWS Well-Architected, "Shared responsibility" | docs | https://docs.aws.amazon.com/wellarchitected/latest/security-pillar/shared-responsibility.html | search |
| AWS VPC, "Control subnet traffic with network ACLs" (has the SG vs NACL comparison) | docs | https://docs.aws.amazon.com/vpc/latest/userguide/vpc-network-acls.html | search |
| AWS VPC, "Subnet CIDR blocks" (5 reserved IPs, /28–/16) | docs | https://docs.aws.amazon.com/vpc/latest/userguide/subnet-sizing.html | search |
| AWS, "IAM security best practices" | docs | https://aws.amazon.com/iam/resources/best-practices/ | search |
| AWS hands-on tutorial, "Control your AWS costs" (budgets, zero-spend, Free Tier alerts) | tutorial | https://docs.aws.amazon.com/hands-on/latest/control-your-costs-free-tier-budgets/control-your-costs-free-tier-budgets.html | search |
| AWS Billing, "Choosing a plan" (Free vs Paid plan, closure, 90-day retention) | docs | https://docs.aws.amazon.com/awsaccountbilling/latest/aboutv2/free-tier-plans.html | search |
| Azure, "Avoid charges with your Azure free account" and "Azure spending limit" | docs | https://github.com/MicrosoftDocs/azure-docs/blob/main/articles/cost-management-billing/manage/avoid-charges-free-account.md ; https://github.com/MicrosoftDocs/azure-docs/blob/main/articles/cost-management-billing/manage/spending-limit.md | opened (source repo); the learn.microsoft.com renderings sit under /azure/cost-management-billing/manage/ |

Also useful: Google Cloud free program page https://cloud.google.com/free-trial/ (search); AWS What's New on the 2025 Free Tier https://aws.amazon.com/about-aws/whats-new/2025/07/aws-free-tier-credits-month-free-plan/ (search); Azure free account FAQ https://azure.microsoft.com/free/free-account-faq (search); Azure "Create free services" https://learn.microsoft.com/azure/cost-management-billing/manage/create-free-services (search); AWS root user best practices https://docs.aws.amazon.com/IAM/latest/UserGuide/root-user-best-practices.html (search); AWS "Understanding unexpected charges" https://docs.aws.amazon.com/awsaccountbilling/latest/aboutv2/checklistforunwantedcharges.html (search); Google Cloud blog product map https://cloud.google.com/blog/topics/developers-practitioners/handy-new-google-cloud-aws-and-azure-product-map (search).

### Inferences
- For the "explain it back" and interview slots, the Julia Evans DNS post, the AWS NACL page's SG-vs-NACL table and the Let's Encrypt lifetimes post give the most quotable, current facts [K judgement].
- Prefer the official cloud docs over the YouTube cloud intros for lesson 3: free-tier rules changed in July 2025 (AWS) and Azure's VM list changed (B2pts/B2ats v2), so older videos are likely wrong on prices and limits [inference from S above].
- A good single "go deeper" pick per lesson: Mess With DNS (lesson 1), hpbn TLS chapter (lesson 2), Google's 3-cloud comparison table (lesson 3).

### Gaps
- **No Hussein Nasser YouTube URL appeared in search.** His TLS 1.2/1.3 videos were found only through Class Central listings (for example https://classcentral.com/course/youtube-transport-layer-security-tls-1-2-and-1-3-explained-by-example-139397), so I have not listed a YouTube link for him.
- **No freeCodeCamp networking course URL was confirmed as freeCodeCamp's.** The two long courses above (qiQR5rTSshw, 2JYT5f2isg4) appeared on youtube.com, but the search did not show the channel name.
- **No official AWS, Azure or GCP YouTube channel videos** were surfaced; I did not search for them, to stay within the search budget.
- **The Cloudflare Learning Center "What is DNS?" and DNS record pages** did not appear in search (only the DNS security page did: https://www.cloudflare.com/learning/dns/dns-security/), so they are not listed even though they are likely good.
- **YouTube video titles and lengths** could not be opened (the youtube.com oEmbed endpoint is blocked here); titles are as shown in search results.
