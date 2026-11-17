"""Book-voice rewrite of d10 (fifth edition). Run: python3 brief/scratch/v5/tb/d10.py"""
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from apply import apply

opening = """Picture a parcel that comes back to your door with a sticker on it. One sticker says "no such street". Another says "nobody at this apartment". A third parcel never comes back at all, and after three weeks you stop waiting. Each sticker points to a different mistake, and each needs a different fix.

Computers send each other messages in much the same way, and when a message fails, they leave a sticker too: an error message. The trap is that every failure feels like the same "it can't connect". So people restart things and change settings at random, when the sticker already said what broke.

Last time, you pushed your work to GitHub, which quietly needed your laptop to find GitHub's computers. In this lesson, we'll follow one message from a name to an address, through your router, to the right program, and learn to read the sticker when it fails. Before we start, make a guess, and keep it in mind."""

guess = {
    "q": "Networks are often written as an address, a slash and a number. Which network holds more addresses: 10.0.0.0/16 or 10.0.0.0/24?",
    "why": "The number after the slash counts the fixed bits. More fixed bits leave fewer free ones, so /16 has 65,536 addresses and /24 only 256.",
}

terms_plain = [
    "A number that identifies one network connection of a machine, such as 192.168.1.23 or 127.0.0.1.",
    "An address from a range that many networks reuse inside (10.x, 172.16 to 172.31, 192.168.x) and that the internet never carries.",
    "A way to write a block of addresses: 10.0.1.0/24 means the first 24 bits are fixed, which leaves 256 addresses.",
    "Network address translation: your router swaps private addresses for its own public address on the way out, and back on the way in.",
    "A number from 0 to 65535 that picks which program on a machine receives the traffic.",
    "A way of sending data that first sets up a connection, then delivers every byte in order and resends anything lost.",
    "A server that answers 'what is the address of this name?' by asking other DNS servers and remembering the answers.",
    "Time to live: how many seconds a DNS answer may be kept and reused before someone must ask again.",
]

s1 = """A letter needs an address on the envelope, and so does every message between programs. Take hello-devops, this course's tiny web app that answers every visit with a greeting and a count of visits. To keep that count, it can talk to a small database called Redis. So where does Redis live?

On a network, a group of machines linked so they can send each other data, the answer is an IP address. It identifies one network interface, the hardware or software that connects a machine to a network. It does the job a street address does for a building.

An IPv4 address, the common kind, is 32 bits, written as four numbers from 0 to 255, such as `192.168.1.23`. A bit is a single 0 or 1. Each number is one byte (8 bits), which is why it stops at 255. That gives about 4.3 billion addresses, not enough for every device on earth.

IPv6, the newer kind, fixes this with 128-bit addresses written in hex (0 to 9 and a to f), such as `2001:db8::1`. It works the same way, but this course mostly uses IPv4 because the numbers are easier to read.

Your laptop has several addresses at once:

- One on Wi-Fi, handed out by your home router, the box that links your home to the internet.
- `127.0.0.1`, the loopback address, which always means "this machine".
- More inside Docker Desktop's Linux VM (the small virtual computer it runs on your Mac), one per Docker network.

That 4.3 billion limit is why some addresses are private. Every hotel has a room 101, and nobody minds, because nobody posts a letter to just "room 101". Private ranges work the same way. They are reused inside millions of homes, offices and cloud networks, and routers on the internet never forward them. The number after each slash is explained in the CIDR section below:

- `10.0.0.0/8`: every address that starts with 10.
- `172.16.0.0/12`: from 172.16 to 172.31.
- `192.168.0.0/16`: every address that starts with 192.168.

Every other normal address is public and unique on the whole internet. Your laptop almost certainly has a private one.

A private address is like a room number: useful inside the building, useless on an envelope from abroad. Next, we'll see how your laptop's messages get out anyway."""

s2 = """So how does a laptop with a private address reach GitHub? Picture an office building with one street address and a front desk. The clerk writes the building's address on every outgoing letter as the return address, and notes who sent it. When a reply arrives, the clerk walks it to the right desk.

Your home router is that front desk, and its trick is called NAT, short for network address translation. The router has one public address from your internet provider. Data travels in packets: small chunks, each labelled with a source and a destination address. When your laptop sends a packet out, the router does three things:

1. It replaces your private source address with its public one.
2. It remembers the swap, so it knows the reply belongs to your laptop.
3. When the reply comes back, it swaps the address back and passes the reply to you.

Everyone in your home shares that one public address. That is why a website sees your router's address, never your laptop's. It also explains why nobody outside can start a connection to your laptop: the router has no record for traffic it never saw go out.

How does your laptop know to hand packets to the router at all? It follows its route table. Every machine has one: a short list of rules that says where to send traffic for each block of addresses. A laptop usually has two kinds of rule. Addresses on its own network go straight to the destination. Everything else goes to the default gateway, which is your router. When two rules match, the more specific one wins: the one that covers fewer addresses.

Your router has a route table of its own, whose default gateway is at your internet provider. Each router on the way reads the destination address and passes the packet one hop closer, as sorting offices do with a letter. The `traceroute` command, near the end of this lesson, lists those hops.

Day 12 brings these ideas back in a cloud network, with an internet gateway, a NAT gateway and route tables you write.

Route tables speak in blocks of addresses, such as "everything on my own network". Next, we'll learn to read how a block is written."""

s3 = """Route tables, firewalls (which let traffic in or keep it out) and cloud networks talk about blocks of addresses, as a postcode covers many streets.

A block is written in CIDR notation: an address, a slash and a number. The number says how many bits at the start are fixed. Those fixed bits name the network, like the postcode. The remaining bits number the machines inside it. Each of the four numbers is 8 bits, so `/24` fixes the first three numbers and leaves the last one free.

An IPv4 address has 32 bits, so a block holds 2 to the power of (32 minus N) addresses:

- `/32`: 1 address, a single machine.
- `/24`: 256 addresses, such as `10.0.1.0` to `10.0.1.255`.
- `/16`: 65,536 addresses, such as `10.0.0.0` to `10.0.255.255`.
- `/8`: 16,777,216 addresses, everything that starts with `10.`.

Remember the guess at the start? The direction feels backwards at first: a bigger number after the slash means a smaller network. Each extra fixed bit halves the block, so a `/25` is half a `/24`, 128 addresses.

You will also meet an older way to write the same thing, the subnet mask. `255.255.255.0` means /24 and `255.255.0.0` means /16. On a Mac, the command `ifconfig` lists your addresses and prints the mask in hex, where `0xffffff00` is /24.

You do not need binary drills. Python's `ipaddress` module checks your math. `python3 -c "import ipaddress as i; print(i.ip_network('10.0.0.0/16').num_addresses)"` prints `65536`. Here `-c` runs one line of Python.

An address finds the machine, but one machine runs many programs. Next, we'll find the right one."""

s4 = """An IP address gets traffic to the right building. A port, a number from 0 to 65535, picks the right program inside it, like an apartment number. A server, the program that waits for others to connect, listens on a port. Servers use well-known ports, agreed numbers that tell a client (the program that connects) where to knock. A web address like `https://github.com` names no port, so your browser uses 443. The common ones:

- 22: SSH, the secure login from Day 7
- 53: DNS, the phone book for names (later today)
- 80: HTTP, the web
- 443: HTTPS, the web, encrypted
- 5432: PostgreSQL, a popular database
- 6379: Redis

The client uses a port too, picked at random from a high range for each connection. It is called an ephemeral port. Four values define one connection: source address, source port, destination address and destination port. That is how one laptop keeps 50 browser tabs apart. Your router's NAT uses the same four values to tell your laptop's connections from your phone's, and it may change the source port too. An address together with a port is called a socket.

Two transport protocols carry the data. A protocol is a set of rules two programs agree on. TCP is like registered mail with receipts. Before any data moves, the client and server do a three-step handshake:

1. The client sends SYN: "I want to talk."
2. The server answers SYN-ACK: "Fine, I hear you."
3. The client sends ACK, and the connection is open.

After that, TCP numbers every byte, and the receiver acknowledges what has arrived. The sender resends anything not acknowledged in time, and the receiver puts the bytes back in order. HTTP, SSH and database connections use TCP.

UDP is a postcard: no handshake and no guarantee. It is lighter, so it suits small questions and live audio or video. DNS uses UDP on port 53 for most queries. HTTP/3, the newest web protocol, also runs over UDP, through QUIC (Day 11).

Even on the right port, a program can turn visitors away. Next, we'll see how, and why containers make it worse."""

s5 = """A server program binds to an address and a port, then listens there: it claims that door and waits for knocks. The address it binds to decides who can reach it, and people get this wrong more than anything else:

- Binding to `127.0.0.1` accepts connections from the same machine only. Loopback traffic never leaves the machine.
- Binding to `0.0.0.0` means "listen on every address this machine has": Wi-Fi, loopback and any others alike.

Development servers often choose `127.0.0.1` by default, so nobody else on your Wi-Fi can reach a half-finished app. Flask, the Python toolkit behind hello-devops, does this, which matters in a moment.

`0.0.0.0` is a wildcard for listening, and you never connect to it. The tools show the difference. On Linux, `ss -tlnp` (a command that lists listening programs) shows one server on `127.0.0.1:9101` and another on `0.0.0.0:9102`. On a Mac, `lsof` shows the second one as `*:9102`, where the star means every address.

A container is a program packed with everything it needs and run in its own walled-off space (Day 17). It gets its own set of addresses and ports, with its own loopback, like a tiny separate machine. Publishing a port with `-p 8000:8000` tells Docker, the tool that runs containers, to pass connections from port 8000 on your Mac to port 8000 in the container.

Docker delivers them to the container's network address, not its loopback, so an app inside bound to `127.0.0.1` never receives them. The curl command, which fetches a web address, then prints something like `Empty reply from server` or `Connection reset by peer`. The fix is to bind to `0.0.0.0` inside the container. That is why `app.py` ends with `host="0.0.0.0"`, which overrides Flask's default.

Publishing also opens the port wider than you might expect. `-p 8000:8000` publishes the port on every address of your Mac, so other machines on your Wi-Fi may reach it. Docker's own docs call port publishing "insecure by default". Write `-p 127.0.0.1:8000:8000` when only your laptop should connect.

**Inside the container, bind to 0.0.0.0. On your Mac, publish to 127.0.0.1.**

Yet you typed `github.com`, a name, and never an address. Next, we'll see who turns one into the other."""

s6 = """People remember names, and machines connect to addresses. DNS, the Domain Name System, is the phone book between them. It is spread over many thousands of servers, with caches (stores of recent answers) everywhere. No single server could hold every name, so the work is split along the dots in a name. Each level only knows who runs the level below it. When an app looks up `github.com`, the question travels this chain:

1. The stub resolver, a small part of your operating system (macOS, for example), checks `/etc/hosts` and its own cache.
2. If it has no answer, it asks a recursive resolver: your router, your internet provider, or a public one such as `1.1.1.1`.
3. If that resolver has nothing cached, it asks a root server, which says "ask the servers for .com".
4. A .com server, called a TLD (top-level domain) server, says "ask github.com's own name servers".
5. The authoritative server for github.com gives the real answer.
6. The answer flows back, and each layer caches it.

Each answer is a record, and these are the types you will meet:

- A: name to IPv4 address.
- AAAA: name to IPv6 address.
- CNAME: this name is an alias, so look up that other name instead.
- MX: which servers accept email for the domain.
- TXT: free text, used to prove you own a domain and for email policy.
- NS: which servers are authoritative for the domain.

Every record has a TTL in seconds: how long anyone may cache it. People say a DNS change takes time to "propagate". What really happens is that old answers sit in caches until their TTL runs out. So after a change, one colleague reaches the new server while another still reaches the old one.

So a team moving its database to a new server lowers the TTL of its name a day early, from one hour to 60 seconds. Every client picks up the new address within a minute of the switch.

`/etc/hosts` is a local file that beats DNS, for your machine only. Watch out with `dig`, a DNS lookup tool: it asks DNS servers directly and ignores `/etc/hosts`. Your apps and `ping` read that file first. If `dig` and your app disagree about a name, look in `/etc/hosts`.

Next, we'll use every step from today to read the stickers on failed messages."""

s7 = """Back to the returned parcels. When a connection fails, the exact error tells you which step broke. Four errors cover most cases:

- Could not resolve host, or "Name or service not known": DNS failed. No packet went to the server at all. That is the "no such street" sticker.
- Connection refused: the machine answered your SYN with a reset, because nothing listens on that port. The app is down, on another port, or bound to `127.0.0.1`. Nobody is home at that apartment.
- Timed out: nothing answered. A firewall dropped the packets, or the address is wrong or unreachable. The parcel simply vanished.
- Connection reset, or an empty reply: something accepted the connection and then closed it. Proxies (programs that pass traffic on) and Docker's port forwarder do this when the app behind them is unreachable.

A refusal comes back in about a millisecond. On a timeout, your machine resends the SYN a few times, waiting longer each time, before it gives up. So even the waiting is a clue.

**Read the error before you fix anything. Each one names a different step.**

Each tool in your toolbox answers one question:

- `ping`: are you there? It uses ICMP, a small protocol for network status messages that many firewalls block, so a failed ping proves little.
- `traceroute`: which routers does my traffic pass on the way?
- `dig` and `nslookup`: what does DNS say about this name?
- `ifconfig` on a Mac, `ip addr` on Linux: which addresses do I have?
- `lsof -iTCP -sTCP:LISTEN` on a Mac, `ss -tlnp` on Linux: who listens on which port?
- `nc -zv host port`: can I open a TCP connection to that port?

`ss` and `ip` exist only on Linux. Use them in your practice box, the Ubuntu container from Part 1, where `apt install iproute2` adds them.

These tools tell you whether a message arrived, but not what it said. That is the next layer up."""

sections = [
    ("Every machine needs an address", s1),
    ("How a private address gets out: NAT and the route table", s2),
    ("Reading a block of addresses: /24 and /16", s3),
    ("Ports pick the program, and TCP or UDP carries the data", s4),
    ("Who may knock: 127.0.0.1, 0.0.0.0 and containers", s5),
    ("DNS: from a name to an address", s6),
    ("Refused, timed out or unresolved: reading the sticker", s7),
]

closing = """We started with parcels that came back with stickers on them. A network message fails at one of a few steps: the name, the address, the way out through the router, or the door of the program. The error message names the step, if you read it before you start restarting things.

The next time `curl localhost:8000` fails for hello-devops, read the first line of the error and name which step broke before you change anything.

Next, we'll open the envelope itself. What does a web request actually say, and how is it sealed so that nobody can read it on the way?"""

worked_say = [
    "A Redis container called cache runs on a Docker network called shopnet. Redis is the small database hello-devops can use to count visits. A Docker network is a private network that containers join (Day 20), and `-d` runs a container in the background. A second container, client, stands in for your app, and it starts on Docker's default network. Inside client, install three tools: dig (in dnsutils), ip and nc. The first two docker commands print long IDs, trimmed here.",
    "Reproduce the symptom. Your colleague says the app cannot reach cache on port 6379. Try it with nc, a small tool that opens connections. Read the error carefully: getaddrinfo is the function programs call to look up a name. It failed before a single packet went to port 6379, so this is a DNS problem, not a firewall or a dead Redis.",
    "Ask the system resolver the way apps do, with `getent hosts`. It reads /etc/hosts and then DNS. When the name is unknown, it prints nothing and exits with code 2. The hosts file only knows localhost and the container itself (IPv6 lines trimmed). So the DNS server this container uses has never heard of cache.",
    "In a second Mac terminal, compare the two containers' networks. Docker answers container names through a built-in DNS server, but only on networks you create, and only for containers on the same network. The client container sits on the default network, called bridge, so it cannot see the shopnet phone book.",
    "Fix it by connecting client to shopnet. Back inside client, the resolver has changed to 127.0.0.11, Docker's built-in DNS server, and the name now resolves.",
    "Read the DNS answer with dig, then test the ports. The answer line has five columns: name, TTL in seconds, class (IN, for internet), type (A) and the address. Port 6379 succeeds. Port 6380 is refused at once: the host is there, but nothing listens on that port.",
    "Look at what changed underneath. client now has two addresses, one per network, each in a /16. Its route table sends each /16 straight out of the matching interface and everything else to the default gateway. That is the route table from this lesson, for real, though your addresses will differ. Exit and clean up with `docker rm -f cache` and `docker network rm shopnet`.",
]

recap = [
    "An IP address finds the machine and a port finds the program; private ranges reach the internet through NAT.",
    "/N fixes N bits: /24 is 256 addresses, /16 is 65,536, and a bigger N means a smaller network.",
    "Bind to 0.0.0.0 inside containers; publish to 127.0.0.1 when only your laptop should connect.",
    "DNS goes from the stub resolver to a recursive resolver, then root, TLD and authoritative servers, caching each answer for its TTL.",
    "Unresolved means DNS, refused means no listener, and a timeout means a drop or a wrong address.",
    "The limit: these tools show whether a message arrived, not what it said; that is HTTP, next lesson.",
]

task = {
    "steps": [
        "Find your laptop's private address and your default gateway. Then find your public address. Write down which range the private one is in, and why the two differ.",
        "Read the netmask from `ifconfig en0` and turn it into a /N. Use Python's `ipaddress` to count the addresses in your home network, and to check whether 10.0.3.7 is inside 10.0.2.0/23.",
        "Use dig to find the A, AAAA, MX, NS and TXT records of a domain you use. Run `dig @1.1.1.1 github.com` twice, a few seconds apart, and compare the TTLs.",
        "Run `dig +trace example.com` and name the three kinds of server it talks to, in order.",
        "Add the line `127.0.0.1 myapp.test` to /etc/hosts. Compare `ping -c 1 myapp.test` with `dig +short myapp.test`, explain the difference, then remove the line.",
        "Start two throwaway web servers: `python3 -m http.server 9101 --bind 127.0.0.1` and `python3 -m http.server 9102 --bind 0.0.0.0`. Compare them in `lsof`, then try to reach both through your private address.",
        "Save `netcheck.py` from this lesson in `~/code/netlab`. Make it print each of its four results: TCP OK, REFUSED, DNS FAIL and TIMEOUT.",
        "For each of the four results, write one line: which step failed, and what you would check next.",
    ],
}

explain_back = {
    "answer": "First the app asks the operating system's resolver for the address of cache. It checks /etc/hosts and its cache, then asks a DNS server, such as Docker's built-in one at 127.0.0.11. With the IP address in hand, the app sends a SYN to that address on port 6379. The server answers SYN-ACK, the app sends ACK, and the TCP connection is open. If the name is unknown, it fails before any packet is sent. If nothing listens on 6379, the connection is refused, and if a firewall drops the packets, it times out.",
}

check = [
    {"q": "A teammate's app listens on 127.0.0.1:8080 inside a container started with `-p 8080:8080`, and nobody can reach it. What do you suggest?"},
    {"q": "`nc -zv db.internal 22` succeeds at once, but `nc -zv db.internal 5432` (the database port) waits 30 seconds and then times out. What is the most likely cause?"},
    {"q": "Your network is 10.0.0.0/16, and you need to split it into four smaller networks of equal size, as large as possible. Which prefix do they get?"},
]

deeper = {"body": """Two facts make the chain work. Your laptop learned which recursive resolver to use from the router, when it got its own address. And every recursive resolver ships with the root servers' addresses, so it always has a place to start.

`dig +trace example.com` lets you play recursive resolver yourself. Instead of asking your usual resolver for a finished answer, dig starts at the top and follows each referral, each "ask that server instead". You see three blocks of output:

1. A list of root servers, named `a.root-servers.net` to `m.root-servers.net`. dig asks one of them about example.com.
2. The root does not know the answer, but it knows who runs .com. It returns NS records for the .com servers. dig asks one of those.
3. The .com server returns the NS records for example.com's own name servers. dig asks one of them and finally gets the A record.

Each block ends with a line saying which server answered and how long it took. Every step is a referral to a server lower in the tree. Your recursive resolver does exactly this when its cache is empty, and caches each referral so the next lookup skips most of the trip.

Real resolvers add two complications:

- Negative answers are cached too. If you look up a name before its record exists, resolvers can remember "no such name" for a while, so a record you just created can still look missing.
- Flushing your own cache only fixes your machine. On a Mac, `sudo dscacheutil -flushcache; sudo killall -HUP mDNSResponder` clears the local cache, but your router's and your provider's caches keep the old answer until the TTL ends.

If you want to watch DNS from the other side, try [Mess With DNS](https://messwithdns.net/about.html) by Julia Evans. It gives you a real subdomain to create records on and shows the queries arriving live, so you can create an A record, `dig` it, and see the question land. Records are deleted after a week.

Last, a trap on the Mac: the name `localhost` can resolve to the IPv6 loopback `::1` as well as `127.0.0.1`. curl tries both, but some tools only try the first. If a server bound to `127.0.0.1` looks down from one tool and up from another, connect to `127.0.0.1` explicitly and compare.

Two names from today, spelled out for the curious: CIDR stands for Classless Inter-Domain Routing, and ICMP for Internet Control Message Protocol."""}

apply(3, "d10", {
    "goal": "By the end you can read an IP address and a block of addresses, explain how a name becomes an address, and tell from an error message which step of a connection failed.",
    "opening": opening,
    "guess": guess,
    "terms_plain": terms_plain,
    "sections": sections,
    "diagram_caption": "The name is looked up first, through a chain of resolvers and caches. Only then does your app open a TCP connection to the address and port.",
    "worked_say": worked_say,
    "task": task,
    "explain_back": explain_back,
    "recap": recap,
    "closing": closing,
    "check": check,
    "interview": [{}, {}, {}],
    "deeper": deeper,
    "aside": {"title": "My hotspot gave me 100.64 something. Is that public?", "after": 0, "body": "No. Some phone hotspots and VPNs hand out addresses from `100.64` to `100.127`. That is a special shared range that internet providers use inside their own networks. It is not one of the three private ranges, but it is not a public address either. The internet never routes it to you directly."},
    "drop": ["analogy", "mistake", "real_world"],
})
print("d10 written")
