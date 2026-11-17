"""Book-voice rewrite of d11 (fifth edition). Run: python3 brief/scratch/v5/tb/d11.py"""
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from apply import apply

opening = """Picture a café with free Wi-Fi. You buy a train ticket on your laptop and see the little padlock next to the web address. Safe, you think. Then a friend asks a fair question: safe from what?

The padlock says your message travels in a sealed envelope that nobody on the way can open. It says nothing about who opens it at the other end. That gap is easy to miss, because browsers show one small icon for a big promise, and we fill in the rest ourselves.

Last time, you followed a message to the right address and port, and learned to read the error when it failed. We never looked inside the envelope.

In this lesson, we'll open it. We'll read a web request line by line, seal it, check who holds the other end, and put a receptionist in front of two copies of hello-devops. Before we start, make a guess, and keep it in mind."""

guess = {
    "q": "Your browser shows a padlock on https://paypa1-login.example. What does the padlock prove?",
    "why": "A certificate proves that someone controls the domain name, and TLS seals the traffic. Anyone who controls paypa1-login.example can get a valid certificate for it.",
}

terms_plain = [
    "A message from a client: a method and path, headers, a blank line and an optional body.",
    "The three-digit number at the start of every HTTP response, such as 200, 404 or 502.",
    "A `Name: value` line in an HTTP message that carries extra details, such as `Host` or `Content-Type`.",
    "A request that has the same effect whether you send it once or many times, such as GET or DELETE.",
    "Transport Layer Security: the protocol under HTTPS that encrypts traffic and proves who the server is.",
    "A signed file that says which names a public key belongs to, and for how long.",
    "A server in front of your apps that receives every request and passes it on to one of them.",
    "A server that spreads incoming requests across several copies of an app and skips the broken ones.",
]

s1 = """Every time you open a web page, your browser sends a short letter and gets one reply. The language of those letters is HTTP. Browsers, apps and curl (the command-line tool that fetches web addresses) all use it to talk to web servers. It travels over a TCP connection, the reliable kind from last time. The client sends a request, and the server sends back exactly one response.

In HTTP/1.1, the version you will read most often, both are plain text. A request has four parts, in this order:

1. A request line: the method, the path and the version, such as `GET /healthz HTTP/1.1`.
2. Headers: one `Name: value` per line, such as `Host: localhost:8000`.
3. A blank line, which says the headers are over.
4. An optional body: the data you send, such as JSON (a common text format for data) for a POST.

A response has the same shape, with a status line first: `HTTP/1.1 200 OK`. You can see both halves with `curl -v`. Lines starting with `>` are what curl sent, and lines starting with `<` came back.

Because it is text, you could type a request by hand. `printf 'GET / HTTP/1.1\\r\\nHost: example.com\\r\\nConnection: close\\r\\n\\r\\n' | nc example.com 80` does exactly that. The `\\r\\n` pairs are the line endings HTTP requires.

HTTP is stateless: the server treats each request on its own and does not remember the last one. So how does a website keep you logged in? With cookies. The server sends a `Set-Cookie` header with a token, a random string that stands for you. The browser sends it back in a `Cookie` header on every later request.

The first line of every request names a method. Next, we'll see why the choice of method decides whether a request is safe to send twice."""

aside = {
    "title": "Do HTTP/2 and HTTP/3 change any of this?",
    "after": 0,
    "body": "Not the parts you read. HTTP/2 and HTTP/3 keep the same methods, headers and status codes. An HTTP/1.1 connection carries one request at a time, so browsers open several. HTTP/2 runs many requests at once over one TCP connection, packed into binary frames. But TCP delivers bytes in order, so one lost packet stalls them all. HTTP/3 runs over QUIC, on UDP, where a lost packet stalls only its own request. For debugging you can stay in HTTP/1.1 terms, because curl shows you the same fields.",
}

s2 = """The method says what you want to do:

- GET: read something. It should change nothing.
- POST: create something or submit data, such as a payment.
- PUT: replace something with the body you send.
- PATCH: change part of something.
- DELETE: remove something.
- HEAD: like GET, but return only the headers.
- OPTIONS: ask what is allowed. Browsers send it before some requests to other sites.

A safe method changes nothing on the server: GET and HEAD. An idempotent method has the same effect whether you send it once or five times: GET, HEAD, PUT and DELETE. Deleting order 42 twice leaves it just as deleted.

POST is neither. Send "charge this card 20 euros" twice, and you may charge twice.

Why does an operator care? Because networks fail halfway. Picture your train ticket: you press Pay, the café Wi-Fi drops, and nobody knows whether the server got the request. Retrying an idempotent request is safe. Retrying a POST is not, unless the API (the set of requests a service accepts) gives you a way to make it safe. Payment APIs often accept an idempotency key: a unique ID per payment, so the server can ignore a repeat.

Proxies, the servers in the middle from the end of this lesson, know this too. For example, nginx will not retry a POST on another server by default once it has sent it to one.

**A retry is only safe if sending twice changes nothing. Check the method before you retry.**

Every request gets a reply, and the reply starts with a number. Next, we'll learn to read it."""

s3 = """Every response starts with a three-digit status code. The first digit gives the family, so even a client that does not know a code can act on it:

- 1xx: information, rarely seen.
- 2xx: success.
- 3xx: go somewhere else.
- 4xx: the client did something wrong.
- 5xx: the server side failed.

These are the ones you will read in logs (the notes programs write about what they did) and dashboards, and what each suggests:

- 200 OK and 201 Created: it worked. 201 means a POST made something new.
- 301 and 302: redirects. The `Location` header says where to go, and 301 is permanent.
- 304 Not Modified: your cached copy is still good, so no body is sent.
- 400 Bad Request: the request itself is broken, such as invalid JSON.
- 401 Unauthorized: who are you? Despite the name, it means credentials (proof of who you are) are missing or wrong.
- 403 Forbidden: I know who you are, and you may not do this.
- 404 Not Found: no such path. Look for a typo or a missing route.
- 429 Too Many Requests: slow down, because a rate limit kicked in.
- 500 Internal Server Error: the app crashed or hit an error it did not handle.
- 502 Bad Gateway: a proxy could not get a good answer from the app behind it.
- 503 Service Unavailable: the server is up but cannot serve right now, like hello-devops's `/readyz` while Redis is down.
- 504 Gateway Timeout: a proxy waited for the app and gave up.

The last three, 502, 503 and 504, usually come from a proxy or load balancer, not from your code. "Gateway" in their names means that server in the middle. A 502 means the app was unreachable or answered with garbage. You will cause one on purpose in today's hands-on.

The status line is only the top of the reply. Below it sit the headers, and they carry most of the details. Next, we'll read them."""

s4 = """Headers carry the details, like the notes written on the outside of an envelope. A few matter every day:

- `Host`: which site you want. One server address can host many sites, and this header picks one.
- `Content-Type`: what the body is, such as `application/json`.
- `Authorization`: credentials, such as a bearer token (whoever holds it gets in). Never write it to a log.
- `Cache-Control`: who may cache (keep a copy of) the response, and for how long.
- `X-Forwarded-For`: the original client's address, added by proxies along the way.

A handful of curl options cover nearly everything:

- `-v` shows the whole conversation, including the DNS, TCP and TLS steps.
- `-i` prints the response headers with the body, and `-I` sends a HEAD request for headers only.
- `-L` follows redirects.
- `-X`, `-H` and `-d` set the method, add a header and send a body.
- `-o /dev/null -s -w '%{http_code}'` prints only the status code, which is handy in scripts.
- `-w` with timing variables shows how long DNS, connect, TLS and the first byte took.
- `--resolve name:port:address` skips DNS and sends that name to an address you choose.

With `--resolve` you can test a new server under its real name before you change DNS. The `Host` header and TLS still use the name from the URL.

So far, everything in this lesson was a postcard: anyone on the way could read it. Next, we'll seal it."""

s5 = """Back in the café. Plain HTTP is readable text, and every router between you and the server passes it along. Whoever runs one of them, or simply shares the café's open Wi-Fi, could read your password or change the page. HTTPS is HTTP inside a TLS connection, the sealed envelope. TLS gives you three things:

- Confidentiality: nobody on the path can read the traffic.
- Integrity: nobody can change it without the change being detected.
- Authentication: the server proves it holds the private key for a certificate that names this host.

A private key is the secret half of a key pair, and a certificate is a signed file that ties a public key to a name. Both get a fuller look in the next section. Before any HTTP flows, the client and the server run a handshake. In TLS 1.3, the current version, it takes one round trip:

1. The client sends ClientHello. It lists the ciphers (encryption methods) it supports and its half of a key exchange. It also names the host it wants, in a field called SNI, which is TLS's version of the Host header. It lists the HTTP versions it speaks too, in a field called ALPN.
2. The server answers with ServerHello and its half of the key exchange. Then, already encrypted, it sends its certificate and a signature that proves it holds the matching private key.
3. The client checks the certificate: the right name, still valid, and signed by someone it trusts.
4. Both sides compute the same session keys from the two halves. Everything after this, including the HTTP request, is encrypted.

How can two machines agree on a key while others listen? Each side keeps a random secret and sends only a public value made from it. Each combines its own secret with the other's public value, and both arrive at the same key. The public values alone are not enough to work it out. It feels like a magic trick, and it is the kind that holds up.

The signature in step 2 is the same proof your SSH key gave on Day 7. Only the private key can make it, and anyone with the public key can check it.

TLS does not hide everything. The server's IP address is visible to everyone on the path, and usually so is the host name, because SNI is sent before encryption starts.

The seal is only worth something if you know who holds the other end. Next, we'll see how your browser decides."""

s6 = """The signature only proves the server holds some private key. How does your browser know that key belongs to github.com, and not to an attacker? On Day 7, ssh asked you to accept a new server's fingerprint. A browser cannot ask you about every site, so it trusts a few certificate authorities (CAs) to vouch for servers, the way a passport office vouches for a photo.

A certificate is a signed statement: "this public key belongs to these names, from this date to that date". The names live in a field called Subject Alternative Name (SAN), such as `DNS:localhost`. A CA signs it after checking that the requester controls those names.

Your operating system and browser ship a trust store: a list of root CAs they trust. Roots rarely sign server certificates directly. They sign intermediate CAs, and an intermediate signs the server's certificate. That lets the root keys stay offline, locked away. The server sends its certificate plus the intermediates, and the client follows that chain up to a root it already trusts. If any link is missing, expired or made out to another name, the connection fails.

Let's Encrypt is a free CA run by a non-profit. It issues certificates automatically through a protocol called ACME. To prove you control a domain (a name such as example.com), you pass a challenge:

- HTTP-01: serve a token at a known URL on port 80. It cannot give you a wildcard certificate.
- DNS-01: publish a TXT record. It is the only way to get a wildcard such as `*.example.com`.

Both prove control of the name. For HTTP-01, Let's Encrypt fetches the token from whatever server the name points to. For DNS-01, it reads the record from the domain's own DNS.

Certificates expire, which limits how long a stolen key stays useful, and on purpose they expire sooner each year. Let's Encrypt certificates last 90 days today, and 45 days from 2028 (Go deeper has the dates). Nobody should renew those by hand, so renewal must be automated and watched.

Remember the guess? The padlock proves less than people think. Let's Encrypt gives a certificate to anyone who controls a domain, including `paypa1-login.example`. TLS says "you are talking privately to whoever controls this name", and nothing about whether they are honest.

For `localhost`, no public CA will issue a certificate, because nobody uniquely owns that name. You make your own, as in the worked example.

Now the envelope is sealed and the sender checked. Next, we'll meet who receives it on the server's side."""

s7 = """In production, the real setup that users reach, a request rarely goes straight to your app. Picture hello-devops on one server with a public address. One crash takes the site down, and each new copy needs its own address and certificate. So requests pass through servers in the middle.

A reverse proxy is the receptionist of an office building. It receives every request on the apps' behalf, then walks each one to an app behind it. Common ones are nginx, Envoy, Caddy and Traefik. A forward proxy is the opposite: it acts for clients, such as a company proxy that all outgoing traffic must pass through.

Reverse proxies take on jobs each app should not repeat:

- TLS termination: the proxy holds the certificate, opens the envelope, and talks plain HTTP to the apps behind it.
- Routing by host or path: `/api` goes to one service and `/` to another.
- Load balancing: spreading requests across several copies of an app.
- Health checks: probing each copy, for example with `GET /healthz`, and skipping the ones that fail.
- Rate limiting: answering 429 when one client sends too much.

nginx calls the app servers behind it upstreams, and today's `lb.conf` lists them in an `upstream` block.

A load balancer works at one of two levels, numbered after a standard model of network layers. Layer 4 is TCP and UDP with their ports, and layer 7 is the application's protocol, such as HTTP. A layer 4 balancer sees only addresses and ports and forwards whole TCP connections, so it is fast and works for any protocol. A layer 7 balancer reads the HTTP request, so it can route on paths, headers and cookies. An L7 balancer is really a reverse proxy with several backends, the apps behind it.

Sticky sessions are an L7 feature: one user keeps landing on the same copy, usually through a cookie. I would rather keep apps free of in-memory state, so any copy can serve any request. Today's task shows why: with `REDIS_HOST` empty, each copy of hello-devops counts visits in its own memory, so the two copies disagree.

**Keep the state out of the app copies. Then any copy can answer any request.**

Two more pieces sit further out. A CDN (content delivery network) is a worldwide set of caching proxies that serves copies of your files from near the user, and `Cache-Control` says what it may keep. A firewall allows or denies traffic by address, port and protocol before it reaches the proxy.

All of this runs on servers someone has to buy, power and look after. Renting them instead is the cloud, and that is where we go next."""

sections = [
    ("Opening the envelope: an HTTP request is plain text", s1),
    ("What you ask for, and which requests are safe to send twice", s2),
    ("Reading the reply's first line: status codes", s3),
    ("Headers, and curl as your magnifying glass", s4),
    ("Sealing the envelope: what TLS adds", s5),
    ("Who holds the other end? Certificates and the CAs that vouch", s6),
    ("The receptionist in front: proxies and load balancers", s7),
]

closing = """We started in a café, looking at a padlock. Now you know what it promises: the envelope is sealed, and the other end really controls that name. It promises nothing about whether the other end deserves your money. Inside the envelope sits a plain text letter, and a receptionist usually opens it before your app ever sees it.

In the hands-on, watch the status codes as you stop each copy of hello-devops, and say which side each code blames.

Next, we'll stop owning servers at all and rent them instead. What exactly do you rent in the cloud, and how do you keep the bill from surprising you?"""

worked_say = [
    "Make a folder and a certificate for localhost. Your Mac's openssl, the standard tool for keys and certificates, is a different build (LibreSSL) with different flags. So run real OpenSSL from the python:3.14-slim image instead. The flag `-x509` makes a self-signed certificate, `-nodes` leaves the key unencrypted, and `-addext` adds the names. While it makes the key, openssl prints a line of dots and plus signs; that is normal.",
    "Save `tls.conf` from this lesson in the same folder. Start a tiny app, `traefik/whoami`, which answers by printing the request it received. Then start nginx with the config and the certificate mounted read-only. Only nginx publishes a port, and only on 127.0.0.1, so the app is reachable through nginx alone.",
    "Ask for the page. curl refuses, and it is right to. The certificate is signed by itself, not by a CA in your trust store, so curl cannot tell it from an attacker's. The wording on your Mac may differ a little.",
    "Tell curl to trust exactly this certificate with `--cacert`. It still checks the name and the dates; it just adds one trusted signer. Now read whoami's answer. RemoteAddr is nginx, not you. Your address is in X-Forwarded-For. Here that is Docker's gateway, because traffic from your Mac enters the network there. X-Forwarded-Proto says the client used https, though the app only saw plain HTTP.",
    "Watch the handshake with `-v`. It prints about 40 lines; these are the ones to read. First comes ClientHello, offering HTTP/2 and HTTP/1.1. Then the server's hello, its certificate and its proof of the key. Last, the agreed TLS version and cipher, and the certificate check passing on name and dates. Your Mac's curl words these lines a little differently.",
    "Inspect the certificate the server sends, the way you would for any real site. Subject and issuer are the same name: that is what self-signed means. The dates show the 7 days you asked for. On a Mac the subject line looks slightly different, such as `subject= /CN=localhost`.",
    "Clean up. Both containers were started with `--rm`, so stopping them also removes them. Keep the folder if you want to repeat the experiment.",
]

recap = [
    "An HTTP message is a start line, headers, a blank line and an optional body, and `curl -v` shows all of it.",
    "GET, PUT and DELETE are idempotent and safe to retry; POST is not, unless the API takes an idempotency key.",
    "4xx blames the client and 5xx the server; 502, 503 and 504 usually come from proxies.",
    "TLS encrypts and proves control of a name; the client follows the certificate chain to a trusted root.",
    "Certificates are getting shorter-lived, so renewal must be automated and monitored.",
    "A reverse proxy ends TLS, routes and load-balances; its limit is that it cannot fix an app that keeps state in its own memory.",
]

explain_back = {
    "answer": "nginx received the client's HTTPS connection on port 443, ran the TLS handshake with its certificate and decrypted the request, which is TLS termination. It then picked one of the upstream servers, app1 or app2, and forwarded the request over plain HTTP on port 8000. On the way it added X-Forwarded-For, so the app knows the real client. When an upstream did not answer within the connect timeout, nginx tried the other one. When no upstream could answer, nginx itself replied 502 Bad Gateway, which means the proxy was fine but the app behind it was not.",
}

deeper = {"body": """Certificate lifetimes are shrinking on a schedule, and it changes how operators work. Let's Encrypt certificates last 90 days today. Its default profile moves to 64 days on February 10, 2027, and to 45 days on February 16, 2028. An opt-in profile already issues 45-day certificates, and another issues certificates that last about six days. Industry rules will cap every public certificate at 47 days from March 15, 2029. The plans and the reasons are in Let's Encrypt's [certificate lifetimes page](https://letsencrypt.org/docs/cert-lifetimes/).

What this means in practice:

- Never renew by hand. Use an ACME client that renews on its own, or a platform feature that does, such as cert-manager in Kubernetes.
- Renew early. Let's Encrypt suggests renewing at about two thirds of a certificate's lifetime, or following its renewal-information service, called ARI.
- Hunt for hard-coded intervals. A cron job (a task the system runs on a timer) that renews every 60 or 80 days will break when certificates last 45. Let's Encrypt suggests grepping for those numbers.
- Monitor expiry anyway. `openssl x509 -noout -checkend 1209600` exits non-zero when a certificate expires within 14 days, which makes a simple alert.

Two more changes make old tutorials wrong. First, Let's Encrypt switched off its OCSP service on August 6, 2025, and now publishes revocation only through certificate revocation lists (CRLs). Guides that run `openssl ocsp` against Let's Encrypt are out of date. Second, Let's Encrypt announced a new chain of root and intermediate CAs in late 2025. So do not hard-code intermediate names such as R3 or R10 in scripts or firewall rules, because the names change.

If you want the mechanics of the handshake in more depth, the TLS chapter of [High Performance Browser Networking](https://hpbn.co/transport-layer-security-tls/) is free and still clear. It was written before TLS 1.3, so remember that 1.3 cut the handshake to one round trip.

A few names from today, spelled out: SNI is Server Name Indication, and ALPN is Application-Layer Protocol Negotiation. The numbers in "layer 4" and "layer 7" come from the OSI (Open Systems Interconnection) model."""}

apply(3, "d11", {
    "goal": "By the end you can read a raw HTTP exchange with curl, explain what TLS proves and how a certificate is checked, and put nginx in front of two app copies as a reverse proxy and load balancer.",
    "opening": opening,
    "guess": guess,
    "terms_plain": terms_plain,
    "sections": sections,
    "aside": aside,
    "diagram_caption": "nginx opens the TLS envelope and passes plain HTTP to whichever app copy answers. With no copy left, it returns 502 Bad Gateway.",
    "worked_say": worked_say,
    "explain_back": explain_back,
    "recap": recap,
    "closing": closing,
    "check": [{}, {"why": "POST is not idempotent, so the server needs a unique key per payment to recognise and ignore the repeat."}, {}],
    "interview": [{}, {}, {}],
    "deeper": deeper,
    "drop": ["analogy", "real_world"],
})
print("d11 written")
