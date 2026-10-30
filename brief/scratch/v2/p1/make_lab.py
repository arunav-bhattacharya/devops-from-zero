#!/usr/bin/env python3
"""Generate labs/linux: fake, deterministic sample files for Part 1 (Days 3 to 7).

Run: python3 brief/scratch/v2/p1/make_lab.py
Everything is made up: documentation IP ranges, example.com domains, fake request IDs.
"""
import json
import pathlib
import random
import shutil

ROOT = pathlib.Path(__file__).resolve().parents[4]
LAB = ROOT / "labs/linux"

# ---------------------------------------------------------------- app.log
APP_LOG = """\
2026-10-30T09:00:01Z INFO  checkout-api req=- server started on port 8000
2026-10-30T09:00:01Z INFO  checkout-api req=- connected to database orders-db:5432
2026-10-30T09:00:05Z INFO  checkout-api req=a41c07 GET /healthz 200 2ms
2026-10-30T09:01:12Z INFO  checkout-api req=4d5e6f GET /api/cart 200 34ms
2026-10-30T09:01:13Z INFO  checkout-api req=7a8b9c POST /api/cart/items 201 51ms
2026-10-30T09:02:40Z WARN  checkout-api req=2c3d4e slow query took 1200ms: SELECT * FROM carts
2026-10-30T09:03:05Z INFO  checkout-api req=5f6a7b GET /api/products 200 18ms
2026-10-30T09:04:30Z ERROR checkout-api req=8e9f0a database connection refused: orders-db:5432
2026-10-30T09:04:31Z INFO  checkout-api req=8e9f0a retrying database connection (attempt 2 of 3)
2026-10-30T09:04:33Z INFO  checkout-api req=8e9f0a database connection restored
2026-10-30T09:05:00Z INFO  checkout-api req=b52d18 GET /healthz 200 3ms
2026-10-30T09:06:18Z INFO  checkout-api req=7f3a9c POST /api/checkout started for cart 5521
2026-10-30T09:06:21Z WARN  checkout-api req=7f3a9c payments-api answered slowly: 2900ms
2026-10-30T09:06:24Z ERROR checkout-api req=7f3a9c timeout talking to payments-api after 3000ms
2026-10-30T09:06:24Z INFO  checkout-api req=7f3a9c POST /api/checkout 504 6012ms
2026-10-30T09:07:02Z INFO  checkout-api req=3b4c5d GET /api/orders/1001 200 22ms
2026-10-30T09:08:45Z WARN  checkout-api req=6e7f8a retrying after error from payments-api (attempt 1 of 3)
2026-10-30T09:08:46Z INFO  checkout-api req=6e7f8a POST /api/checkout 200 812ms
2026-10-30T09:10:00Z INFO  checkout-api req=c63e29 GET /healthz 200 2ms
2026-10-30T09:11:37Z ERROR checkout-api req=9d0e1f NullPointerException in CartService.total
    at com.shop.checkout.CartService.total(CartService.kt:42)
    at com.shop.checkout.CheckoutHandler.handle(CheckoutHandler.kt:17)
2026-10-30T09:11:37Z INFO  checkout-api req=9d0e1f POST /api/checkout 500 45ms
2026-10-30T09:12:10Z INFO  checkout-api req=2a3b4c GET /api/cart 200 31ms
2026-10-30T09:13:55Z WARN  checkout-api req=- disk usage at 85% on /var/log
2026-10-30T09:15:00Z INFO  checkout-api req=d74f3a GET /healthz 200 2ms
2026-10-30T09:16:20Z INFO  checkout-api req=5c6d7e GET /api/products?page=2 200 20ms
2026-10-30T09:17:42Z ERROR checkout-api req=8f9a0b payment declined: card expired (code 2001)
2026-10-30T09:17:42Z INFO  checkout-api req=8f9a0b POST /api/checkout 402 230ms
2026-10-30T09:18:03Z INFO  checkout-api req=1c2d3e GET /api/orders 200 1200ms
2026-10-30T09:20:00Z INFO  checkout-api req=e85a4b GET /healthz 200 3ms
2026-10-30T09:21:30Z INFO  checkout-api req=- received SIGTERM, finishing 2 open requests
2026-10-30T09:21:31Z INFO  checkout-api req=- shutdown complete
2026-10-30T09:21:40Z INFO  checkout-api req=- server started on port 8000
2026-10-30T09:21:41Z INFO  checkout-api req=- connected to database orders-db:5432
2026-10-30T09:22:15Z INFO  checkout-api req=f96b5c GET /healthz 200 2ms
2026-10-30T09:23:08Z INFO  checkout-api req=0a1b2c POST /api/checkout 200 640ms
"""

# ---------------------------------------------------------------- logs/ (one request across services)
LOGS = {
    "logs/gateway.log": """\
2026-10-30T09:06:10Z INFO  gateway req=6b1d2e GET /api/products -> checkout-api 200 19ms
2026-10-30T09:06:18Z INFO  gateway req=7f3a9c POST /api/checkout -> checkout-api
2026-10-30T09:06:24Z ERROR gateway req=7f3a9c upstream checkout-api answered 504 after 6013ms
2026-10-30T09:07:02Z INFO  gateway req=3b4c5d GET /api/orders/1001 -> checkout-api 200 23ms
2026-10-30T09:08:45Z INFO  gateway req=6e7f8a POST /api/checkout -> checkout-api
2026-10-30T09:08:46Z INFO  gateway req=6e7f8a POST /api/checkout -> checkout-api 200 813ms
2026-10-30T09:11:37Z ERROR gateway req=9d0e1f upstream checkout-api answered 500 after 46ms
""",
    "logs/checkout.log": """\
2026-10-30T09:05:00Z INFO  checkout-api req=b52d18 GET /healthz 200 3ms
2026-10-30T09:06:18Z INFO  checkout-api req=7f3a9c POST /api/checkout started for cart 5521
2026-10-30T09:06:18Z INFO  checkout-api req=7f3a9c calling payments-api: charge 59.90 EUR
2026-10-30T09:06:21Z WARN  checkout-api req=7f3a9c payments-api answered slowly: 2900ms
2026-10-30T09:06:24Z ERROR checkout-api req=7f3a9c timeout talking to payments-api after 3000ms
2026-10-30T09:06:24Z INFO  checkout-api req=7f3a9c POST /api/checkout 504 6012ms
2026-10-30T09:07:02Z INFO  checkout-api req=3b4c5d GET /api/orders/1001 200 22ms
2026-10-30T09:08:45Z WARN  checkout-api req=6e7f8a retrying after error from payments-api (attempt 1 of 3)
2026-10-30T09:08:46Z INFO  checkout-api req=6e7f8a POST /api/checkout 200 812ms
2026-10-30T09:11:37Z ERROR checkout-api req=9d0e1f NullPointerException in CartService.total
""",
    "logs/payments.log": """\
2026-10-30T09:06:18Z INFO  payments-api req=7f3a9c charge started: 59.90 EUR for cart 5521
2026-10-30T09:06:18Z INFO  payments-api req=7f3a9c calling bank-gateway
2026-10-30T09:06:21Z WARN  payments-api req=7f3a9c bank-gateway slow: 2800ms so far
2026-10-30T09:06:24Z ERROR payments-api req=7f3a9c bank-gateway timeout after 3000ms
2026-10-30T09:06:24Z ERROR payments-api req=7f3a9c charge failed, returning 504
2026-10-30T09:08:45Z INFO  payments-api req=6e7f8a charge started: 12.00 EUR for cart 5530
2026-10-30T09:08:45Z ERROR payments-api req=6e7f8a bank-gateway reset the connection
2026-10-30T09:08:46Z INFO  payments-api req=6e7f8a retry 1 of 3 succeeded in 640ms
2026-10-30T09:17:42Z ERROR payments-api req=8f9a0b card expired (code 2001)
""",
    "logs/worker.log": """\
2026-10-30T09:06:30Z INFO  orders-worker req=- polling queue orders.created
2026-10-30T09:06:31Z WARN  orders-worker req=7f3a9c no order found for cart 5521, skipping email
2026-10-30T09:08:50Z INFO  orders-worker req=6e7f8a sent confirmation email for order 1002
2026-10-30T09:12:00Z ERROR orders-worker req=- queue orders.created unreachable, retrying in 5s
2026-10-30T09:12:05Z INFO  orders-worker req=- queue orders.created reachable again
""",
    "logs/archive/checkout-2026-10-29.log": """\
2026-10-29T17:40:02Z INFO  checkout-api req=91aa20 GET /api/cart 200 30ms
2026-10-29T17:41:15Z ERROR checkout-api req=92bb31 database connection refused: orders-db:5432
2026-10-29T17:41:16Z INFO  checkout-api req=92bb31 retrying database connection (attempt 2 of 3)
2026-10-29T17:41:18Z INFO  checkout-api req=92bb31 database connection restored
2026-10-29T17:55:47Z ERROR checkout-api req=93cc42 timeout talking to payments-api after 3000ms
2026-10-29T18:02:09Z INFO  checkout-api req=94dd53 POST /api/checkout 200 702ms
""",
}

# ---------------------------------------------------------------- access.log (nginx "combined" format)
UA = {
    "safari": "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.6 Safari/605.1.15",
    "chrome": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36",
    "firefox": "Mozilla/5.0 (X11; Linux x86_64; rv:144.0) Gecko/20100101 Firefox/144.0",
    "curl": "curl/8.5.0",
    "probe": "kube-probe/1.37",
    "python": "python-requests/2.32.3",
    "scanner": "Mozilla/5.0 zgrab/0.x",
}

# (ip, user agent, number of requests, kind of traffic)
CLIENTS = [
    ("203.0.113.7", "curl", 61, "api-heavy"),
    ("198.51.100.23", "safari", 44, "shopper"),
    ("192.0.2.15", "chrome", 37, "shopper"),
    ("203.0.113.42", "firefox", 29, "shopper"),
    ("198.51.100.8", "scanner", 21, "scanner"),
    ("10.0.0.2", "probe", 18, "probe"),
    ("192.0.2.101", "python", 12, "api"),
    ("203.0.113.99", "safari", 9, "shopper"),
    ("198.51.100.77", "chrome", 7, "shopper"),
]

SCANNER_PATHS = ["/wp-login.php"] * 7 + ["/.env"] * 5 + ["/admin"] * 4 + ["/phpmyadmin/"] * 3 + ["/.git/config"] * 2


def build_access_log(rng):
    reqs = []
    for ip, ua, n, kind in CLIENTS:
        for i in range(n):
            ref = "-"
            if kind == "probe":
                m, p, s, b = "GET", "/healthz", 200, 2
            elif kind == "scanner":
                m, p, s, b = "GET", SCANNER_PATHS[i], 404, 153
            elif kind == "api-heavy":
                # a script hammering the product API; nginx rate-limits some calls with 429
                p = rng.choice(["/api/products", "/api/products?page=2", "/api/products?page=3"])
                m = "GET"
                s, b = (429, 162) if i % 9 == 4 else (200, rng.randint(1800, 5200))
            elif kind == "api":
                m, p = rng.choice([("GET", "/api/orders"), ("GET", "/api/orders/1001"), ("POST", "/api/cart/items")])
                s, b = (201, 88) if m == "POST" else (200, rng.randint(300, 1400))
            else:  # browser shopper
                m, p = rng.choice([("GET", "/"), ("GET", "/products"), ("GET", "/api/products"), ("GET", "/api/cart"),
                                   ("POST", "/api/cart/items"), ("GET", "/static/app.js"), ("GET", "/static/app.css"),
                                   ("POST", "/api/checkout"), ("GET", "/login"), ("POST", "/login")])
                ref = rng.choice(["https://shop.example.com/", "https://shop.example.com/products",
                                  "https://shop.example.com/cart"])
                if p.startswith("/static"):
                    s, b = (304, 0) if rng.random() < 0.4 else (200, rng.randint(8000, 42000))
                elif p == "/login" and m == "POST":
                    s, b = 302, 0
                elif m == "POST" and p == "/api/cart/items":
                    s, b = 201, 88
                else:
                    s, b = 200, rng.randint(400, 9000)
            reqs.append([ip, m, p, s, b, ref, UA[ua]])
    rng.shuffle(reqs)
    # Fixed failures so the error report has a clear answer: checkout 500 x6 and 504 x2, payments 502 x3,
    # plus 404s from browsers for an old link and a missing favicon.
    shoppers = [r for r in reqs if r[6] in (UA["safari"], UA["chrome"], UA["firefox"])]
    fixed = ([("POST", "/api/checkout", 500, 64)] * 6 + [("POST", "/api/checkout", 504, 160)] * 2 +
             [("POST", "/api/payments/charge", 502, 157)] * 3 + [("GET", "/favicon.ico", 404, 153)] * 1 +
             [("GET", "/products/old-sale", 404, 153)] * 1)
    picks = rng.sample(range(len(shoppers)), len(fixed))
    for idx, (m, p, s, b) in zip(picks, fixed):
        shoppers[idx][1:5] = [m, p, s, b]
    # one old bookmark that still uses http:// as the referrer
    shoppers[3][5] = "http://shop.example.com/"
    lines = []
    t = 0
    for r in reqs:
        t += rng.randint(5, 20)
        sec = min(t, 3599)
        ts = f"30/Oct/2026:09:{sec // 60:02d}:{sec % 60:02d} +0000"
        ip, m, p, s, b, ref, ua = r
        lines.append(f'{ip} - - [{ts}] "{m} {p} HTTP/1.1" {s} {b} "{ref}" "{ua}"')
    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------- events.jsonl (for jq)
EVENTS = [
    {"ts": "2026-10-30T09:01:13Z", "level": "info", "service": "checkout-api", "request_id": "7a8b9c", "event": "cart.item_added", "duration_ms": 51},
    {"ts": "2026-10-30T09:02:40Z", "level": "warn", "service": "checkout-api", "request_id": "2c3d4e", "event": "db.slow_query", "duration_ms": 1200},
    {"ts": "2026-10-30T09:04:30Z", "level": "error", "service": "checkout-api", "request_id": "8e9f0a", "event": "db.connection_refused", "duration_ms": 5, "error": {"type": "ConnectException", "message": "orders-db:5432 refused"}},
    {"ts": "2026-10-30T09:06:18Z", "level": "info", "service": "payments-api", "request_id": "7f3a9c", "event": "charge.started", "amount": 59.90, "currency": "EUR"},
    {"ts": "2026-10-30T09:06:24Z", "level": "error", "service": "payments-api", "request_id": "7f3a9c", "event": "charge.failed", "duration_ms": 6000, "error": {"type": "Timeout", "message": "bank-gateway timeout after 3000ms"}},
    {"ts": "2026-10-30T09:06:24Z", "level": "error", "service": "checkout-api", "request_id": "7f3a9c", "event": "checkout.failed", "duration_ms": 6012, "error": {"type": "Timeout", "message": "payments-api timeout"}},
    {"ts": "2026-10-30T09:07:02Z", "level": "info", "service": "checkout-api", "request_id": "3b4c5d", "event": "order.viewed", "order_id": 1001, "duration_ms": 22},
    {"ts": "2026-10-30T09:08:45Z", "level": "warn", "service": "payments-api", "request_id": "6e7f8a", "event": "charge.retry", "attempt": 1},
    {"ts": "2026-10-30T09:08:46Z", "level": "info", "service": "payments-api", "request_id": "6e7f8a", "event": "charge.succeeded", "amount": 12.00, "currency": "EUR", "duration_ms": 640},
    {"ts": "2026-10-30T09:08:46Z", "level": "info", "service": "checkout-api", "request_id": "6e7f8a", "event": "order.created", "order_id": 1002, "amount": 12.00, "currency": "EUR", "duration_ms": 812},
    {"ts": "2026-10-30T09:08:50Z", "level": "info", "service": "orders-worker", "request_id": "6e7f8a", "event": "email.sent", "order_id": 1002},
    {"ts": "2026-10-30T09:11:37Z", "level": "error", "service": "checkout-api", "request_id": "9d0e1f", "event": "checkout.failed", "duration_ms": 45, "error": {"type": "NullPointerException", "message": "CartService.total"}},
    {"ts": "2026-10-30T09:12:00Z", "level": "error", "service": "orders-worker", "request_id": None, "event": "queue.unreachable", "error": {"type": "IOException", "message": "orders.created unreachable"}},
    {"ts": "2026-10-30T09:17:42Z", "level": "error", "service": "payments-api", "request_id": "8f9a0b", "event": "charge.declined", "amount": 230.00, "currency": "EUR", "error": {"type": "CardExpired", "message": "card expired (code 2001)"}},
    {"ts": "2026-10-30T09:18:03Z", "level": "info", "service": "checkout-api", "request_id": "1c2d3e", "event": "orders.listed", "duration_ms": 1200},
    {"ts": "2026-10-30T09:23:08Z", "level": "info", "service": "payments-api", "request_id": "0a1b2c", "event": "charge.succeeded", "amount": 74.50, "currency": "EUR", "duration_ms": 410},
    {"ts": "2026-10-30T09:23:08Z", "level": "info", "service": "checkout-api", "request_id": "0a1b2c", "event": "order.created", "order_id": 1003, "amount": 74.50, "currency": "EUR", "duration_ms": 640},
    {"ts": "2026-10-30T09:23:12Z", "level": "info", "service": "orders-worker", "request_id": "0a1b2c", "event": "email.sent", "order_id": 1003},
]

# ---------------------------------------------------------------- pods.json (shaped like `kubectl get pods -o json`, trimmed)


def pod(name, app, phase, restarts, ready, waiting=None, started="2026-10-30T08:55:12Z"):
    state = {"waiting": {"reason": waiting}} if waiting else {"running": {"startedAt": started}}
    if phase == "Pending":
        cs = []
    else:
        cs = [{"name": app, "image": f"ghcr.io/example/{app}:1.4.1", "ready": ready, "restartCount": restarts, "state": state}]
    return {"metadata": {"name": name, "namespace": "shop", "labels": {"app": app}},
            "spec": {"nodeName": None if phase == "Pending" else "node-2"},
            "status": {"phase": phase, "containerStatuses": cs}}


PODS = {"apiVersion": "v1", "kind": "List", "items": [
    pod("checkout-api-7d9f8c6b5-x2k4p", "checkout-api", "Running", 0, True),
    pod("checkout-api-7d9f8c6b5-q8n2m", "checkout-api", "Running", 1, True),
    pod("payments-api-5c7d9b8f4-zt6wd", "payments-api", "Running", 14, False, waiting="CrashLoopBackOff"),
    pod("orders-worker-6f8b7c9d2-m4r7s", "orders-worker", "Pending", 0, False),
]}

# ---------------------------------------------------------------- server/: a small fake server tree for find and du
SMALL = {
    "server/etc/nginx/nginx.conf": """\
# Fake nginx config for practice. Not used by any real server.
user www-data;
worker_processes auto;

events {
    worker_connections 768;
}

http {
    access_log /var/log/nginx/access.log;
    error_log /var/log/nginx/error.log;
    include /etc/nginx/sites-enabled/*;
}
""",
    "server/etc/nginx/sites-enabled/shop.conf": """\
server {
    listen 80;
    server_name shop.example.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
    }
}
""",
    "server/etc/shop/config.yaml": """\
# Settings for the fake shop app.
port: 8000
database:
  host: orders-db
  port: 5432
payments:
  url: http://payments-api:8080
  timeout_ms: 3000
log_level: info
""",
    "server/etc/shop/.env": """\
# Fake values for practice. Real secrets never live in plain files like this.
DB_PASSWORD=changeme-not-a-real-password
PAYMENTS_API_KEY=fake-key-0000
""",
    "server/home/dev/notes.txt": """\
TODO: rotate the nginx logs, they keep growing
TODO: ask why the 2026-10-29 backup is so big
""",
    "server/home/dev/.bash_history": """\
cd /var/log/shop
tail -f app.log
df -h
du -sh /var/*
""",
    "server/opt/shop/bin/start.sh": """\
#!/usr/bin/env bash
# Fake start script for practice.
cd /opt/shop/releases/current
exec java -jar shop.jar
""",
    "server/opt/shop/releases/1.4.0/VERSION": "1.4.0\n",
    "server/opt/shop/releases/1.4.1/VERSION": "1.4.1\n",
    "server/var/log/shop/app.log": APP_LOG,
    "server/var/log/nginx/error.log": """\
2026/10/30 09:06:24 [error] 812#812: *4411 upstream timed out (110: Connection timed out) while reading response header from upstream, client: 192.0.2.15, server: shop.example.com, request: "POST /api/checkout HTTP/1.1", upstream: "http://127.0.0.1:8000/api/checkout"
""",
    "server/tmp/session-91aa.lock": "pid=4242\n",
}


def big_app_log(rng, day, n_lines):
    out = []
    paths = ["/api/cart", "/api/products", "/api/orders", "/healthz", "/api/checkout"]
    for i in range(n_lines):
        sec = (i * 86400) // n_lines
        ts = f"2026-10-{day}T{sec // 3600:02d}:{sec % 3600 // 60:02d}:{sec % 60:02d}Z"
        rid = f"{rng.randrange(16 ** 6):06x}"
        roll = rng.random()
        if roll < 0.004:
            out.append(f"{ts} ERROR checkout-api req={rid} timeout talking to payments-api after 3000ms")
        elif roll < 0.02:
            out.append(f"{ts} WARN  checkout-api req={rid} slow query took {rng.randint(1000, 2500)}ms: SELECT * FROM carts")
        else:
            p = rng.choice(paths)
            out.append(f"{ts} INFO  checkout-api req={rid} GET {p} 200 {rng.randint(2, 90)}ms")
    return "\n".join(out) + "\n"


def big_access_log(rng, n_lines):
    out = []
    ips = [c[0] for c in CLIENTS]
    for i in range(n_lines):
        sec = (i * 86400) // n_lines
        ts = f"29/Oct/2026:{sec // 3600:02d}:{sec % 3600 // 60:02d}:{sec % 60:02d} +0000"
        out.append(f'{rng.choice(ips)} - - [{ts}] "GET /api/products HTTP/1.1" 200 {rng.randint(1800, 5200)} "-" "{UA["curl"]}"')
    return "\n".join(out) + "\n"


def sql_dump(rng, n_rows):
    out = ["-- Fake database dump for practice. No real data.",
           "CREATE TABLE orders (id integer, cart integer, amount numeric, currency text, created_at text);"]
    for i in range(n_rows):
        out.append(f"INSERT INTO orders VALUES ({1000 + i}, {5000 + i}, {rng.randint(500, 40000) / 100:.2f}, 'EUR', "
                   f"'2026-10-{rng.randint(1, 29):02d}T{rng.randint(0, 23):02d}:{rng.randint(0, 59):02d}:00Z');")
    return "\n".join(out) + "\n"


START_LAB = """\
#!/usr/bin/env bash
# start-lab.sh: open a Linux practice shell for Part 1 of the course.
# Run it from the folder that holds the practice files:  bash start-lab.sh
#
# What the docker run options mean:
#   -it          interactive, with a terminal, so you can type into bash
#   --rm         delete the container when you exit (your files stay, see -v)
#   -v "$PWD":/work   show this folder inside the container as /work
#   -w /work     start in /work
# Inside, apt-get installs the extra tools the lessons use, then bash starts.
docker run -it --rm -v "$PWD":/work -w /work ubuntu:24.04 \\
  bash -c 'apt-get update -qq && apt-get install -y -qq less tree jq file curl lsof iproute2 psmisc shellcheck > /dev/null && exec bash'
"""


def main():
    rng = random.Random(20261030)
    if LAB.exists():
        for child in LAB.iterdir():
            if child.name != "README.md":
                shutil.rmtree(child) if child.is_dir() else child.unlink()
    LAB.mkdir(parents=True, exist_ok=True)

    def put(rel, text):
        p = LAB / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text)

    put("app.log", APP_LOG)
    for rel, text in LOGS.items():
        put(rel, text)
    put("access.log", build_access_log(rng))
    put("events.jsonl", "".join(json.dumps(e, separators=(",", ":")) + "\n" for e in EVENTS))
    put("pods.json", json.dumps(PODS, indent=2) + "\n")
    for rel, text in SMALL.items():
        put(rel, text)
    put("server/var/log/shop/app-2026-10-27.log", big_app_log(rng, "27", 11000))
    put("server/var/log/shop/app-2026-10-28.log", big_app_log(rng, "28", 16000))
    put("server/var/log/shop/app-2026-10-29.log", big_app_log(rng, "29", 23000))
    put("server/var/log/nginx/access.log.1", big_access_log(rng, 18000))
    put("server/var/log/nginx/access.log", "".join(build_access_log(random.Random(7)).splitlines(True)[:40]))
    put("server/var/backups/shop-db-2026-10-29.sql", sql_dump(rng, 36000))
    put("server/var/backups/shop-db-2026-10-28.sql", sql_dump(rng, 900))
    for i in range(12):
        put(f"server/var/cache/shop/thumbs/product-{1001 + i}.txt", f"fake thumbnail cache for product {1001 + i}\n" * 40)
    put("server/tmp/upload-3f9a.part", "partial upload, never finished\n" * 12000)
    put("start-lab.sh", START_LAB)
    (LAB / "start-lab.sh").chmod(0o755)
    (LAB / "server/opt/shop/bin/start.sh").chmod(0o755)


if __name__ == "__main__":
    main()
