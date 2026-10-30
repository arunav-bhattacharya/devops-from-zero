#!/usr/bin/env python3
"""Voice pass for Part 1: rewrite prose fields in place so they read like a person wrote them.

Loads the current content/p1.json, replaces prose fields only, and writes it back.
Ids, titles, code, commands, refs, sources, answers, options and the diagrams are left alone.
Run: python3 brief/scratch/p1/humanize.py
"""
import json
import pathlib

PATH = pathlib.Path(__file__).resolve().parents[3] / "content" / "p1.json"
P = json.loads(PATH.read_text())
L = {lesson["id"]: lesson for lesson in P["lessons"]}

# ---------------------------------------------------------------- part level
P["intro"] = (
    "Servers and containers run Linux, and every deploy travels over a network. "
    "So Part 1 spends one day in the Linux shell and one on networks and the cloud. "
    "You use both in every later lesson, and you need no cloud account for either."
)
P["recap"][4] = "Start bash scripts with `set -euo pipefail` so they stop on errors."
P["recap"][7] = "The cloud rents you machines by the minute, so set a budget alert and destroy what you create."
P["quiz"][7]["why"] = ("Idle resources keep charging by the hour, and a budget alert only warns you. "
                       "Delete what you no longer need.")

# ---------------------------------------------------------------- d03
d = L["d03"]
S = d["sections"]
S[0]["body"] = """Cloud servers usually run Linux, and every container in this course runs Linux inside. So when something breaks in production, you will be typing into a Linux shell. A shell is the program that reads your commands and runs them. Macs use zsh and most Linux servers use bash, but everything on this page works in both.

Files live in a tree that starts at `/`, the top folder. Your home folder is `~`, which on a Mac means `/Users/you`. You can write a path in two ways:

- An absolute path starts at `/`, such as `/etc/hosts`. It means the same thing from anywhere.
- A relative path starts from where you are now, such as `code/hello-devops`.

Four commands move you around:

- `pwd` prints where you are.
- `ls -la` lists everything here, including hidden files whose names start with a dot.
- `cd code/hello-devops` moves into a folder; `cd ..` goes up one level and `cd ~` goes home.
- `mkdir -p a/b/c` makes folders, including any missing parents.

Make a habit of pressing Tab while you type a name. The shell completes it, so you type less and make fewer typos."""

S[1]["body"] = """You will use these file commands all the time:

- `cat file` prints a whole file, and `less file` pages through a long one (press q to quit).
- `head -n 20 file` and `tail -n 20 file` show the first or last 20 lines.
- `tail -f app.log` keeps printing new lines as they arrive, so you can watch a live log.
- `cp a b` copies, `mv a b` moves or renames, and `rm file` deletes. There is no trash can.

Every file has an owner and permissions. The command `ls -l` shows them as a code such as `-rwxr-xr--`. After the first character (the file type) come three groups of three letters: for the owner, the group and everyone else. In each group:

- r means read, w means write, and x means execute (run).
- A dash means that right is missing.

`chmod +x smoke.sh` adds execute permission, and `chown` changes the owner.

The root user is the all-powerful admin, with user ID 0. `sudo` runs one command as root after asking for your password. That power is the reason containers should not run as root. By default, root in a container has the same user ID 0 as root on the host. So an attacker who breaks out of the container is root on the machine. On Day 8 your Dockerfile switches to a normal user."""

S[2]["body"] = """A process is a running program. Each one has a number called a PID (process ID). You see and control processes with these commands:

- `ps aux` lists every process, and `pgrep -f app.py` finds the PID of one by its command.
- `top` shows a live view of the busiest processes (press q to quit).
- `kill PID` sends a signal to a process.

A **signal** is a short message from the operating system to a process. Two matter most:

- SIGTERM (number 15) means "please stop". The app can finish its work and exit cleanly. A plain `kill` sends it.
- SIGKILL (number 9) means "stop now". The process cannot catch or ignore it, so it gets no chance to clean up. `kill -9` sends it.

This pair comes back all course. When you run `docker stop`, Docker sends SIGTERM, waits 10 seconds, then sends SIGKILL. Kubernetes does the same when it removes a pod, with a 30 second default wait. So write apps that handle SIGTERM. Then they can finish the requests they are serving before they exit."""

S[3]["body"] = """An environment variable is a named setting that a process gets from the shell that started it. Run `env` to see them all, or `echo $HOME` to print one. The `$` means "the value of". There are three ways to work with them:

- `export GREETING="Hi there"` sets one for this shell and every program it starts.
- `GREETING="Hi" python app.py` sets one for a single command only.
- `unset GREETING` removes one.

Your app reads its settings this way: `APP_VERSION`, `GREETING`, `REDIS_HOST` and `PORT`. That is how the same code runs on your laptop, in a container and in Kubernetes, with different settings each time.

You met PATH yesterday. It is the most important variable, and it holds a list of folders, separated by colons. When you type `kubectl`, the shell looks in each folder in order and runs the first `kubectl` it finds. `which kubectl` shows the one that won. Changes made with `export` vanish when you close the terminal. To keep one, add the line to `~/.zshrc` (zsh) or `~/.bashrc` (bash)."""

S[4]["body"] = """Every process has three standard streams: input (stdin), output (stdout) and errors (stderr). You can connect and redirect them:

- `|` (a pipe) sends one command's stdout into the next command's stdin.
- `>` writes stdout to a file, replacing what was there, and `>>` adds to the end.
- `2>&1` sends stderr to the same place as stdout, so errors land in your log too.

For example, `grep ERROR app.log | wc -l` counts error lines. The `grep` part keeps the lines that match, and `wc -l` counts them.

Every command also ends with an **exit code**: 0 means success, and any other number means failure. Run `echo $?` to print the exit code of the last command.

Exit codes are how CI decides whether your change passes. Systems such as GitHub Actions run your commands and check each exit code. If `pytest` exits with 1 because a test failed, the step fails and the pipeline stops. So a script that hides a failure and exits with 0 lets broken code through."""

S[5]["body"] = """A bash script is a text file of commands. Its first line, `#!/usr/bin/env bash`, says which program runs the file. You make it executable with `chmod +x` and run it with `./name.sh`. The next line should almost always be `set -euo pipefail`:

- `-e` stops the script at the first command that fails.
- `-u` treats a variable that was never set as an error, which catches typos.
- `-o pipefail` makes a pipe fail if any command in it fails, instead of only the last one.

Without these, bash keeps going after errors, and a script can report success after doing half its work.

Servers need a package manager too. Ubuntu and Debian use apt: `sudo apt-get update`, then `sudo apt-get install -y jq`. It does the job Homebrew does on your Mac, and you will see it in many Dockerfiles.

SSH opens a secure shell on another machine, as in `ssh you@server`. It uses a key pair. The private key never leaves your laptop, and you give the public key to the server or to GitHub. To create a pair, run `ssh-keygen -t ed25519`. In this course gh handles your GitHub login, so you need SSH only for real servers."""

d["analogy"] = ("Stopping a process is like closing a restaurant. "
                "SIGTERM is the manager saying \"we close in ten minutes\": cooks finish the plates already on the stove, and staff lock up properly. "
                "SIGKILL is a power cut: everything stops at once, mid-order, with nothing cleaned up. "
                "Real staff can't ignore the manager, though. A program can ignore SIGTERM, and only SIGKILL can't be ignored.")

W = d["worked"]["steps"]
W[2]["say"] = "Check that it answers. curl succeeded, so `echo $?` prints 0."
W[3]["say"] = "Send SIGTERM with a plain `kill`. The app receives the polite request and shuts down."
W[4]["say"] = ("Check that it is gone. curl now fails with exit code 7, which means it could not connect. "
               "The `ps` command finds nothing and exits with 1. Any non-zero code means failure, and CI uses the same rule.")

d["mistake"] = ("Using `kill -9` as your first move can lose data. "
                "SIGKILL gives the app no chance to finish requests, write its last log lines or close database connections. "
                "Send a plain `kill` (SIGTERM) first, wait a few seconds, and use `kill -9` only if the process is still there.")

d["deeper"]["body"] = """Some containers take exactly 10 seconds to stop. That number is a clue. `docker stop` sent SIGTERM, nothing happened, and Docker sent SIGKILL when its 10 second grace period ran out. The container's exit code is then 137. There are three usual causes.

The first is that PID 1 is special. Inside a container, your app often runs as process ID 1. [Docker's run reference](https://docs.docker.com/reference/cli/docker/container/run/) notes that Linux treats PID 1 specially: it ignores any signal whose default action would end it. So unless your code handles SIGTERM, it does not stop on it. Most web servers, including gunicorn, handle it.

The second is the shell form of a Dockerfile command. If you write `ENTRYPOINT python app.py` as a plain string, Docker starts it under `/bin/sh -c`. The shell becomes PID 1 and does not pass signals on, so your app never hears SIGTERM. The exec form, a JSON list such as `CMD ["gunicorn", "app:app"]`, runs your app directly. The lab's Dockerfile uses the exec form.

The third is a wrapper script. If an entrypoint script starts your app as a child process, the script receives SIGTERM, and your app does not. End such a script with `exec` followed by your command, which replaces the shell with your app.

Two tools help:

- `docker run --init` adds a tiny init process (tini) as PID 1. It passes signals on and cleans up finished child processes.
- `time docker stop` followed by the container name shows how long a stop takes. A second or two is normal; 10 seconds means the signal was lost.

Kubernetes works the same way with a longer default wait. It sends SIGTERM, waits 30 seconds (the pod's `terminationGracePeriodSeconds`), then sends SIGKILL. An app that exits cleanly on SIGTERM is replaced quickly during a rollout and can finish the requests it is serving. An app that ignores it adds 30 seconds to every pod replacement."""

d["real_world"] = ("When checkout slows down at PayFlow, a made-up payments company, the on-call engineer opens a shell next to the app. "
                   "They run `tail -f` and `grep` on its logs to find the failing requests. "
                   "The team's deploy scripts start with `set -euo pipefail`, so a failed step stops the deploy instead of shipping half a release. "
                   "And because the services handle SIGTERM, Kubernetes can replace pods without cutting off payments in progress.")

# ---------------------------------------------------------------- d04
d = L["d04"]
d["terms"][2]["plain"] = "The system that turns names like github.com into IP addresses."

S = d["sections"]
S[0]["body"] = """Every machine on a network has an IP address, like a street address. An IPv4 address is four numbers from 0 to 255, such as `192.168.1.20`. There are two kinds:

- Public addresses are unique on the whole internet. Your home router has one.
- Private addresses work only inside one network. Your laptop's address probably starts with `192.168.` or `10.`.

One address is special. `127.0.0.1`, also called localhost or loopback, always means "this same machine". Traffic to it never leaves the computer.

A port picks which program on a machine gets the traffic, like an apartment number in a building. Ports run from 0 to 65535. Web servers use 80 for HTTP and 443 for HTTPS, and your app uses 8000.

A server program **binds** to an address and a port, then listens there. The address it binds to decides who can connect, and this is the part most people get wrong:

- Binding to `127.0.0.1:8000` accepts connections only from the same machine.
- Binding to `0.0.0.0:8000` accepts connections on every network address the machine has.

A container has its own network and its own localhost, like a small separate machine. So an app inside a container must bind to `0.0.0.0`, or nothing outside can reach it. That is why `app.py` runs with `host="0.0.0.0"`."""

S[1]["body"] = """People remember names, but computers connect to IP addresses. DNS (the Domain Name System) turns one into the other. When you visit `github.com`, this happens:

1. Your computer asks a DNS resolver, a server usually run by your internet provider.
2. If the resolver has no saved answer, it asks a chain of DNS servers until it reaches the one in charge of that name.
3. The resolver returns the IP address and keeps it for a set time, called the TTL (time to live).
4. Your computer connects to that address.

A DNS record that maps a name to an IPv4 address is called an A record. You can look one up yourself with `dig +short github.com` or `nslookup github.com`.

The caching in step 3 explains a common surprise. After you change a DNS record, some users still reach the old address until their saved answer expires."""

S[2]["body"] = """HTTP is the language that browsers, curl and apps use to talk to web servers. The client sends a request, and the server sends back a response. A request has up to four parts:

- a method, such as GET to read or POST to send data,
- a path, such as `/healthz`,
- headers, extra lines such as `Host: localhost:8000`,
- sometimes a body, the data being sent.

A response starts with a status code, and the first digit tells you the family:

- 2xx: success, such as 200 OK.
- 3xx: look somewhere else, such as 301 Moved Permanently.
- 4xx: the client made a mistake, such as 404 Not Found.
- 5xx: the server failed, such as 500 Internal Server Error or 503 Service Unavailable.

Your app's `/readyz` returns 503 when Redis is down, and Kubernetes reads that code on Day 18. To see a whole conversation, use `curl -v`. Lines starting with `>` are what you sent, and lines starting with `<` came back.

HTTPS is HTTP inside an encrypted TLS connection. The server presents a certificate, a signed file that proves it owns the name. A certificate authority, such as Let's Encrypt, signs it after checking that the server controls the domain."""

S[3]["body"] = """One server is a single point of failure. So production apps run several copies behind a load balancer: a server that receives every request and passes it to a healthy copy. If one copy dies, the load balancer stops sending it traffic.

A reverse proxy is a server that sits in front of your apps and forwards requests to them. Most load balancers are reverse proxies, and they often take on extra jobs:

- end TLS, so the apps behind them can speak plain HTTP,
- route by path or name, for example `/api` to one service and `/` to another,
- add caching, compression or rate limits.

You will meet the same ideas in Kubernetes: Services on Day 17 and the Gateway API on Day 19.

A firewall decides which traffic may pass, by address and port. In AWS, the common firewall is a security group: a set of allow rules attached to a server. A new security group lets no incoming traffic in until you add a rule, such as "allow port 443 from anywhere". Open only the ports you need, and never open a database port to the whole internet."""

S[4]["body"] = """The cloud means renting computers, storage and services from a provider. You create them in minutes through an API and pay by the second, minute or hour. You never touch the hardware.

Providers group data centers into regions, such as Frankfurt. Each region has several availability zones (AZs): separate data centers with their own power and network. If you run copies in two or more AZs, your app stays up when one data center fails.

Services differ in how much you manage yourself:

- IaaS (infrastructure as a service): you rent virtual machines and manage the OS and everything on it.
- PaaS (platform as a service): you hand over your code, and the provider runs it.
- SaaS (software as a service): you just use finished software, such as an email service.
- Serverless: you give a function or container and pay only while it runs.

The big three providers use different names for the same things:

- Virtual machines: EC2 (AWS), Azure Virtual Machines, Compute Engine (Google Cloud).
- Object storage for files: S3 (AWS), Azure Blob Storage, Cloud Storage (Google Cloud).

A VPC (virtual private cloud) is your own private network inside a provider, split into subnets. Public subnets can reach the internet directly and private ones cannot, so databases go in private subnets.

Security is shared. The provider secures the cloud itself: buildings, hardware and the base software. You secure what you put in it: your data, who has access, your firewall rules and the OS on your VMs."""

S[5]["body"] = """Pay-as-you-go has a downside: a server you forgot about keeps charging every hour, even when nobody uses it. Watch for these traps:

- resources left running after a tutorial,
- services that charge by the hour just for existing, such as NAT gateways and load balancers,
- data sent out to the internet, which is billed per gigabyte,
- a large machine size picked by mistake,
- leaked access keys that strangers use to run their own servers.

Free tiers changed in 2025. New AWS accounts opened since 15 July 2025 choose a free plan or a paid plan. The free plan gives credits, lasts up to six months, and blocks some expensive services. The paid plan charges your card for anything beyond the credits. Rules change, so read the [AWS Free Tier page](https://aws.amazon.com/free/) before you sign up.

Three habits keep you safe:

1. Create a budget alert on day one. In AWS, open Billing and Cost Management, then Budgets, then Create budget, and pick the zero spend template.
2. Destroy everything you create as soon as you finish. On Day 15, that is `terraform destroy`.
3. Never put access keys in code or in git.

A budget alert only sends an email. It does not stop anything, so habit 2 still matters. You need no cloud account today. Day 15 is the only lesson that uses one, and that part is optional."""

d["analogy"] = ("Sending a request is like posting a letter to a friend in a big apartment building. "
                "DNS is the address book that turns your friend's name into a street address (the IP). "
                "The port is the apartment number, so the letter reaches the right person (program) in the building. "
                "The load balancer is the front desk that hands each letter to whichever clerk is free, "
                "and the firewall is the guard who only lets in mail for certain apartments. "
                "A real letter takes days, though, and all of this happens in a fraction of a second.")

d["mistake"] = ("Say you bind a server to 127.0.0.1 and then run it in a container or on a cloud server. "
                "It worked on your laptop, but now nothing outside can reach it, and the error looks like a network problem. "
                "Bind servers to 0.0.0.0, and use firewalls or security groups to control who can reach them.")
d["real_world"] = ("PayFlow, the made-up payments company, runs its checkout API as several copies in two availability zones. "
                   "They sit behind a load balancer that ends TLS, and only the load balancer accepts traffic from the internet. "
                   "Security groups let the app servers accept traffic only from the load balancer, and the database only from the app servers. "
                   "Every cloud account has budget alerts, and a pipeline destroys the test environments at the end of each day.")

d["deeper"]["body"] = """Day 15 has an optional part on a real cloud. A common cloud network for one app looks like this.

A VPC gets a private address range written in CIDR notation, such as `10.0.0.0/16`. The number after the slash says how many leading bits are fixed. `/16` fixes the first two numbers (10.0), which leaves 65,536 addresses. A `/24` subnet, such as `10.0.1.0/24`, fixes three numbers and holds 256 addresses.

You split the VPC into subnets and place each subnet in one availability zone. A common layout uses two zones and three layers:

1. Public subnets hold the load balancer. Their route table sends internet traffic to an internet gateway.
2. Private subnets hold the app servers. Nothing on the internet can reach them directly.
3. More private subnets hold the database.

Security groups then chain the layers together:

- The load balancer's group allows port 443 from anywhere.
- The app's group allows port 8000 only from the load balancer's group.
- The database's group allows its port only from the app's group.

A rule can name another security group as its source, so you never have to list IP addresses by hand.

Private servers still need to reach out sometimes, for example to download updates. A NAT gateway in a public subnet lets them start outgoing connections, while nothing outside can start one to them. NAT gateways are also a common cost trap, because they charge by the hour even when idle.

Network ACLs are a second, optional firewall at the subnet level. For most setups, security groups are enough.

Kubernetes repeats this pattern inside a cluster. Pods get private addresses, Services act like internal load balancers, and network policies act like security groups."""

PATH.write_text(json.dumps(P, ensure_ascii=False, indent=1) + "\n")
print("wrote", PATH)
