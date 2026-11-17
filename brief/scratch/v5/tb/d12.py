"""Book-voice rewrite of d12 (fifth edition). Run: python3 brief/scratch/v5/tb/d12.py"""
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from apply import apply

opening = """Picture a friend's wedding in another city. You book a hotel room for two nights, because nobody builds a house for a weekend. On Monday you check out and fly home. A month later a bill arrives for a second room you booked by mistake, in a different hotel, which nobody ever slept in. It kept billing every night.

Renting is wonderful for short needs, and that is also the trap. A rented room costs money every night it exists, used or not. Nobody reminds you, because from the hotel's side nothing is wrong.

Last time, a receptionist, nginx, stood in front of two copies of hello-devops on your laptop. Real sites run those pieces on machines someone must buy, power and look after.

In this lesson, we'll rent instead of buy. We'll see what a provider rents you and design a small network on paper. Then we'll write a key card that opens one door only, and build habits that keep the bill near zero. Before we start, make a guess, and keep it in mind."""

guess = {
    "q": "In AWS, Amazon's cloud, you set a budget of $5 with an email alert. Your forgotten test servers reach $5 this month. What happens?",
    "why": "A budget alert only tells you. The servers keep running and billing until you delete them.",
}

terms_plain = [
    "A geographic area where a cloud provider runs data centers, such as Frankfurt.",
    "One or more separate data centers inside a region, with their own power and network.",
    "Virtual private cloud: your own private network inside a cloud provider, with a block of addresses you choose.",
    "A smaller block of addresses inside a VPC; in AWS each subnet lives in one availability zone.",
    "A firewall on each cloud machine that only allows traffic and remembers connections, so replies get out on their own.",
    "A set of permissions that a person or a machine takes on for a while, with credentials that expire.",
    "Giving each person or job only the permissions it needs, and nothing more.",
    "The split of security work: the provider secures the cloud itself, and you secure what you put in it.",
]

s1 = """Before the cloud, a team that needed a new server bought one. They waited for it to be delivered and installed, and paid for it whether it was busy or idle. That is building a house. The cloud is the hotel: renting computers, storage and ready-made services from a provider, by the second or the hour. You never see the hardware. You ask for a machine on a website or through an API, and a minute later it exists. When you delete it, the bill for it stops.

An API, as in the last lesson, is the set of requests a service accepts from programs. Every click in a cloud console, the provider's website, is really an API call. So anything you can click, a program can do. Terraform (Part 8) creates cloud resources from code by calling the same APIs, and a pipeline, a script that runs on every change, can run Terraform.

Cloud services differ in how much the provider runs for you, like the difference between an empty flat and a room with breakfast:

- IaaS (infrastructure as a service): you rent virtual machines, disks and networks, and you install and patch the operating system. A virtual machine, or VM, is a computer made of software, running on the provider's hardware. Example: AWS EC2.
- PaaS (platform as a service): you hand over code or a container, and the provider runs it. Examples: Google Cloud Run, Azure Container Apps.
- SaaS (software as a service): finished software that you just use, such as GitHub or Gmail.
- Serverless functions: you upload one function, a small piece of code, and it runs on each event. You pay per request and for the time it runs. It scales to zero: when no events arrive, nothing runs and you pay nothing for compute. Example: AWS Lambda.

Managed services sit in between. A managed database such as AWS RDS gives you PostgreSQL without you running the server. The provider patches it, backs it up and fails it over to a spare copy if it breaks. You still own the schema (how the data is laid out), the queries and who may connect.

A hotel is a building in some city. Next, we'll see where the cloud's buildings stand, and why that matters."""

s2 = """Providers group their data centers by place. A region is a geographic area, such as AWS's `eu-central-1` in Frankfurt or Google's `us-central1` in Iowa. Inside a region sit several availability zones (AZs). AWS describes an AZ as one or more separate data centers with their own power, networking and connectivity. Fast private fiber links it to the other AZs.

In hotel terms, the region is the city and each AZ is a separate hotel building across town, on its own power supply. The split exists because things fail at every size:

- One server dies: run two copies.
- One data center loses power or floods: run copies in two or more AZs.
- A whole region has a bad day: rare, and only the most critical systems plan for it.

For most apps, two or three AZs in one region is the right amount. The AZs are close enough for fast traffic between them and far enough apart not to fail together.

To pick a region, answer three questions:

1. Where are your users? Closer means lower latency, the delay before an answer arrives.
2. Where must the data live? Laws and contracts can require a country or region.
3. What does it cost? Prices differ between regions.

A cloud console shows one region at a time, and nearly every beginner gets caught by this. A server you created in another region keeps running and billing, out of sight. That is the second hotel room from the opening. Pick one region for all your learning and stay there.

Every provider rents out the same kinds of things, under different names. Next, we'll map them."""

s3 = """The three big providers are AWS (Amazon), Azure (Microsoft) and Google Cloud. They sell the same kinds of building blocks under different names. Running hello-devops in the cloud would take one service from most of these lines, from a machine to run it to DNS for its name. Learn the category first, and the names follow:

- Virtual machines: EC2 (AWS), Virtual Machines (Azure), Compute Engine (Google Cloud).
- Managed Kubernetes: EKS, AKS, GKE.
- Containers without a cluster: Fargate, Container Apps, Cloud Run.
- Functions: Lambda, Azure Functions, Cloud Run functions.
- Object storage, for files you read and write whole over HTTPS: S3, Blob Storage, Cloud Storage.
- Managed SQL databases: RDS, Azure SQL Database and Azure Database for PostgreSQL, Cloud SQL.
- Private networks: VPC, Virtual Network (VNet), VPC.
- DNS: Route 53, Azure DNS, Cloud DNS.
- Load balancers: Elastic Load Balancing, Azure Load Balancer and Application Gateway, Cloud Load Balancing.
- Identity and access: IAM, Microsoft Entra ID with Azure RBAC, Cloud IAM.
- Monitoring and logs: CloudWatch, Azure Monitor, Cloud Monitoring and Cloud Logging.

Kubernetes, a system that runs many containers across many machines, gets its own part later. Don't try to learn this list by heart; come back to it when a name puzzles you.

Similar names do not mean identical behaviour, and Google's own comparison page warns about this. One example: in Google Cloud a VPC network is global and its subnets are regional, while an AWS VPC lives in a single region.

Names also change. Google's Cloud Functions became Cloud Run functions, for example. Check the current docs before you trust any table, including this one.

Of all these blocks, the private network is the one everything else sits in. Next, we'll build one on paper."""

s4 = """Picture renting a whole private floor of the hotel, with your own locked doors. That is a VPC (virtual private cloud): your own private network inside the provider. The addresses, blocks and route tables from two lessons ago all come back here, except that now you set them up yourself.

You give the VPC a private CIDR block, such as `10.0.0.0/16`. Then you split it into subnets: smaller blocks such as `10.0.1.0/24`. In AWS each subnet lives in exactly one AZ, so an app in two AZs needs subnets in both. AWS also keeps 5 addresses in every subnet (the first four and the last), for jobs such as the VPC's router and DNS. So a /24 gives you 251 usable addresses, not 256.

What makes a subnet public or private is its route table, not its name:

- Every route table has a local route, such as `10.0.0.0/16` to `local`, so all subnets in the VPC can reach each other.
- A public subnet adds `0.0.0.0/0` to an internet gateway. `0.0.0.0/0` means every address, so this is the default route. Machines here can have public addresses and be reached from the internet.
- A private subnet adds `0.0.0.0/0` to a NAT gateway instead. Its machines can reach out, for example to download packages, but nobody outside can start a connection to them.

The more specific route wins, as before: `10.0.0.0/16` is more specific than `0.0.0.0/0`, so traffic between subnets stays inside the VPC.

This is your home router again, split in two. The internet gateway is the VPC's front door. A machine inside knows only its private address, so the gateway swaps in that machine's own public address, one for one. The NAT gateway does the home router's trick: many private machines share its single public address, and only replies get back in. It is the hotel's mail desk, which sends letters out but lets no visitor upstairs.

The usual layout puts load balancers in public subnets, and apps and databases in private ones. A machine in a private subnet has no public address and no route in from the internet, so even a wrong firewall rule cannot expose it directly.

Routes decide where traffic may go. Firewalls decide whether it is let in at all. Next, the locks."""

s5 = """AWS gives you two firewalls, and they behave differently. Mixing them up leads to a classic puzzle: the request arrives, but the reply never gets back.

A security group is a lock on each room's door. More exactly, it is a firewall attached to each machine's network interface. Its rules only allow, and anything not allowed is blocked. It is stateful: it tracks connections, so the reply to an allowed request gets out without a rule of its own. A rule can also name another security group as its source. "Allow port 8000 from the load balancer's group" keeps working when the load balancer's addresses change.

A network ACL (NACL) is a guard at the entrance to a whole wing, a whole subnet. It is stateless: it judges every packet on its own, with no memory of connections. Its numbered rules can allow or deny, and the first match wins.

Stateless has a cost. Say a NACL allows inbound port 443. The server's reply goes back to the client's ephemeral port, the random port the client picked, somewhere between 1024 and 65535. If the NACL has no outbound rule for those ports, the reply is dropped. The request arrived, the app answered, and the client still times out. The guard let the visitor in and then refused to let the answer out. A security group would have let the reply out by itself.

AWS describes NACLs as a coarse, extra guard for whole subnets, and for most work security groups do the job. Azure's network security groups are stateful too. Whatever the cloud, start with nothing open and add only what each layer needs. Never open a database port to `0.0.0.0/0`.

Locks keep strangers away from the machines. But who may create, change or delete the machines themselves? Next, the key cards."""

s6 = """Every API call can create, change or delete something, so the provider must know who is calling and what they may do. IAM (identity and access management) answers that for every call: may this caller do this action on this resource? It is the hotel's key card system. The callers are called principals:

- Users: one person, with a console password or access keys (a long-lived ID and secret for programs).
- Groups: a set of users that share permissions.
- Roles: a set of permissions that a person or a machine takes on for a while. A CI job (the robot that tests and ships each change, Part 6), a VM or a person assumes the role and gets temporary credentials that expire.

Permissions live in policies. In AWS a policy is a JSON document made of statements. Each statement has an Effect (allow or deny), an Action (such as `s3:GetObject`), a Resource (which bucket or object) and an optional Condition. A bucket is a named container for files in S3. Anything not allowed is denied.

**Give each key card only the doors its job needs. Start from none and add.**

That rule is called least privilege: grant only the actions and resources a job needs, then tighten from there. A deploy job that uploads to one bucket should not be able to delete databases.

The second habit is to prefer roles over long-lived access keys. A key saved in a file or a CI secret works until someone deletes it, and a leaked key works for an attacker too. Role credentials expire on their own, like a visitor badge that stops working at six o'clock. Day 27 shows GitHub Actions getting cloud access this way, through a standard called OpenID Connect (OIDC), with no stored keys at all.

Security is shared between you and the provider. The hotel keeps the building safe; you still lock your door and keep your passport out of sight. The provider secures the cloud itself: buildings, hardware and the virtualization layer. You secure what you put in it: your data, your IAM policies, your firewall rules and, on a VM, the operating system and its patches. The line moves with the service type. With serverless, the provider does nearly all of it; with a VM, patching the OS is your job.

Every one of these pieces, from a NAT gateway to a VM, appears on a bill. Next, we'll read the bill before it arrives."""

s7 = """Cloud bills come from a few meters:

- Compute time, per second or hour, while a machine runs.
- Storage, per gigabyte per month, even for disks nobody uses.
- Requests, for services like object storage and functions.
- Data sent out to the internet (egress), per gigabyte.

You can buy compute three ways. On-demand is the default: no commitment and the highest price. Reserved capacity and savings plans give a discount for promising one or three years of use. Spot instances use spare capacity at a large discount, but the provider can take them back at short notice, so they suit work that can restart.

Some resources bill by the hour just for existing: NAT gateways, load balancers, public IPv4 addresses (scarce, as you saw two lessons ago), and disks or snapshots nobody uses. A stopped VM still pays for its disk. These are the hotel rooms nobody sleeps in.

Free tiers changed in 2025, and the rules in October 2026 look like this:

- AWS: new accounts pick a Free plan or a Paid plan. The Free plan gives $100 in credits plus up to $100 more for trying services, for 6 months or until the credits run out. Then the account closes instead of charging you. AWS's own FAQ disagrees with itself on when credits expire, so check the Credits page in your console.
- Azure: $200 of credit for 30 days, behind a spending limit that is on by default. Some services are free in limited amounts for 12 months, but after the 30 days you must upgrade to keep using them. Microsoft's pages disagree on how many services are always free (55 or 65).
- Google Cloud: $300 of credit for 90 days, and no charge until you activate a paid account. Separately, Always Free includes one small e2-micro VM, but only in three US regions.

These rules change, so read the provider's current page before you sign up. Then build the habit:

1. Set a budget alert on day one. It sends email; it does not stop anything.
2. Use one region, and tag everything with an owner and a purpose.
3. Delete what you made the same day. On Day 35 that is `terraform destroy`.
4. Never put access keys in code or in git.

**A budget alert only tells you. Deleting is what stops the bill.**

The habits are the limit of today's tools, too: nothing in the cloud cleans up after you. Today needs no cloud account. Days 13 and 14 open one and use it by hand, and Day 35 builds on it with Terraform. All three are optional."""

sections = [
    ("Renting instead of building: what the cloud is", s1),
    ("Regions and availability zones: which city, which building", s2),
    ("The same building blocks under three sets of names", s3),
    ("Your private floor: VPCs, subnets and routes", s4),
    ("Two kinds of lock: security groups and network ACLs", s5),
    ("Key cards: IAM decides who may do what", s6),
    ("Reading the bill before it arrives", s7),
]

closing = """We started with a hotel room nobody slept in, billing every night in a city you had left. The cloud rents you machines, networks and key cards by the hour, in buildings you choose. It is generous with what you can create and silent about what you forgot.

Look at the worked example's design and point to each piece that bills by the hour even when no request arrives. That list is what you delete first after any experiment.

Next, we'll open a real AWS account, safely. How do you lock down the one login that can do anything, before you build a single thing?"""

worked_say = [
    "PayFlow, the made-up payments company, wants its checkout API in two AZs: a load balancer that the internet can reach, and the app and database that it cannot. Start with the VPC block. 10.0.0.0/16 gives 65,536 addresses, far more than needed, so there is room to add subnets for years. Python shows how it slices into /24s.",
    "Choose a numbering you can read at a glance. Public subnets get 10.0.1 and 10.0.2, private ones 10.0.11 and 10.0.12, and the letter is the AZ. Put that plan into `subnet_plan.py` and run it. Each /24 has 251 usable addresses in AWS, and nothing overlaps.",
    "Break it on purpose, so you trust the check. Type private-b as 10.0.2.0/24, a copy-paste slip that really happens. Two subnets may never share addresses, and the script says so and exits with 1, which a CI job would treat as a failure.",
    "Write the route tables. Both public subnets share one table with a default route to the internet gateway. Each private subnet gets a table whose default route goes to the NAT gateway in its own AZ, so AZ b keeps working if AZ a fails. One shared NAT gateway would be cheaper, and many teams accept that for test environments.",
    "Chain the security groups so each layer accepts traffic only from the layer in front of it. Rules name groups, not addresses, so they survive adding more machines. Replies need no rules, because security groups are stateful.",
    "A nightly reporting job must read files from one bucket and nothing else, and `read-one-bucket.json` grants exactly that. AWS names every resource with an ARN (Amazon Resource Name), such as `arn:aws:s3:::payflow-reports`. Note the two resources: listing acts on the bucket itself, while reading acts on the objects inside it, written with `/*`. The jq summary below is easy to read, and jq (the JSON tool from Part 1) fails loudly if the JSON is broken.",
    "Last, the cost check. In this design, the load balancer and the two NAT gateways bill every hour even with no traffic, and so does any public IPv4 address. The database bills for its storage even when stopped. That list is exactly what you would delete first after a test, and on Day 35 a single `terraform destroy` removes all of it.",
]

recap = [
    "The cloud rents machines, storage and services through APIs, which is why tools like Terraform can drive it.",
    "Regions are places; availability zones are separate data centers inside them, so spread copies across AZs.",
    "A subnet is public because its route table sends 0.0.0.0/0 to an internet gateway, not because of its name.",
    "Security groups are stateful and allow-only; NACLs are stateless, ordered and guard whole subnets.",
    "Least privilege and short-lived role credentials beat broad permissions and long-lived keys.",
    "The limit: nothing cleans up for you, and a budget alert only sends email; stay in one region and delete what you create.",
]

explain_back = {
    "answer": "The request enters the VPC through the internet gateway and reaches the load balancer in a public subnet, whose security group allows port 443 from anywhere. The load balancer forwards it to the app in a private subnet, whose security group allows traffic only from the load balancer's group. The reply goes back automatically, because security groups are stateful. When the app downloads a package, the private subnet's route table sends that traffic to the NAT gateway in a public subnet. The NAT gateway swaps in its public address, so the app can reach out while nobody outside can connect in.",
}

check = [
    {},
    {"q": "A subnet's NACL allows inbound 443 and outbound 443 only. The app logs every request, yet clients time out. Why?"},
    {"q": "A CI job must upload build files to one S3 bucket. Which setup follows least privilege and avoids long-lived keys?"},
]

apply(3, "d12", {
    "goal": "By the end you can describe what a cloud provider rents you, design a small two-zone network with subnets, routes and firewalls, write a least-privilege policy, and avoid a surprise bill.",
    "opening": opening,
    "guess": guess,
    "terms_plain": terms_plain,
    "sections": sections,
    "diagram_caption": "One VPC across two AZs. Public subnets hold the load balancer and NAT gateways; private subnets hold the app and database and reach out only through NAT.",
    "worked_say": worked_say,
    "explain_back": explain_back,
    "recap": recap,
    "closing": closing,
    "check": check,
    "interview": [{}, {}, {}],
    "drop": ["analogy", "real_world"],
})
print("d12 written")
