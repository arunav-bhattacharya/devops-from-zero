"""Day 58: Why a service mesh: proxies, sidecars and Envoy."""
from common import (APPMESH, CONSUL, E_ADMIN, E_CB, E_DYN, E_HC, E_LIFE, E_OUTLIER, E_ROUTING, E_WHAT, E_XDS,
                    I_MODES, K_SIDECAR, R, S, V_NANA, V_XDS, lab)

DIAGRAM = (
    '<svg viewBox="0 0 560 320" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="curl sends a request to an '
    'Envoy listener on port 10000; the HTTP connection manager and a route pick cluster hello_v1 (hosts v1a and v1b) for 90 percent '
    'and cluster hello_v2 (host v2) for 10 percent; a control plane can push the same objects over xDS">'
    # control plane, optional
    '<rect class="bxp" x="216" y="12" width="128" height="36" rx="10"/>'
    '<text class="tk" x="280" y="35" font-size="13" text-anchor="middle">Control plane</text>'
    '<line class="lnd" x1="280" y1="48" x2="280" y2="106" marker-end="url(#ar)"/>'
    '<text class="ts" x="290" y="82" font-size="11" text-anchor="start">xDS: LDS RDS CDS EDS</text>'
    # row A: downstream to route
    '<rect class="bx" x="8" y="110" width="72" height="40" rx="10"/>'
    '<text class="t" x="44" y="135" font-size="13" text-anchor="middle">curl</text>'
    '<line class="ln" x1="82" y1="130" x2="104" y2="130" marker-end="url(#ar)"/>'
    '<rect class="bxt" x="108" y="110" width="96" height="40" rx="10"/>'
    '<text class="tk" x="156" y="135" font-size="13" text-anchor="middle">Listener</text>'
    '<line class="ln" x1="206" y1="130" x2="228" y2="130" marker-end="url(#ar)"/>'
    '<rect class="bxt" x="232" y="110" width="128" height="40" rx="10"/>'
    '<text class="tk" x="296" y="135" font-size="13" text-anchor="middle">HTTP manager</text>'
    '<line class="ln" x1="362" y1="130" x2="384" y2="130" marker-end="url(#ar)"/>'
    '<rect class="bxo" x="388" y="110" width="88" height="40" rx="10"/>'
    '<text class="tk" x="432" y="135" font-size="13" text-anchor="middle">Route</text>'
    '<text class="ts" x="44" y="168" font-size="11" text-anchor="middle">downstream</text>'
    '<text class="ts" x="156" y="168" font-size="11" text-anchor="middle">port 10000</text>'
    '<text class="ts" x="296" y="168" font-size="11" text-anchor="middle">fault, router</text>'
    # route to clusters
    '<line class="ln" x1="420" y1="152" x2="330" y2="192" marker-end="url(#ar)"/>'
    '<text class="ts" x="384" y="186" font-size="11" text-anchor="start">90%</text>'
    '<line class="ln" x1="444" y1="152" x2="468" y2="192" marker-end="url(#ar)"/>'
    '<text class="ts" x="486" y="176" font-size="11" text-anchor="start">10%</text>'
    '<rect class="bxg" x="268" y="196" width="104" height="40" rx="10"/>'
    '<text class="tk" x="320" y="221" font-size="13" text-anchor="middle">hello_v1</text>'
    '<rect class="bxg" x="420" y="196" width="104" height="40" rx="10"/>'
    '<text class="tk" x="472" y="221" font-size="13" text-anchor="middle">hello_v2</text>'
    '<text class="ts" x="180" y="212" font-size="11" text-anchor="middle">health checks,</text>'
    '<text class="ts" x="180" y="228" font-size="11" text-anchor="middle">outlier detection</text>'
    # clusters to endpoints
    '<line class="ln" x1="310" y1="238" x2="280" y2="266" marker-end="url(#ar)"/>'
    '<line class="ln" x1="330" y1="238" x2="352" y2="266" marker-end="url(#ar)"/>'
    '<line class="ln" x1="472" y1="238" x2="472" y2="266" marker-end="url(#ar)"/>'
    '<rect class="bxt" x="236" y="270" width="72" height="36" rx="10"/>'
    '<text class="tk" x="272" y="293" font-size="13" text-anchor="middle">v1a</text>'
    '<rect class="bxt" x="324" y="270" width="72" height="36" rx="10"/>'
    '<text class="tk" x="360" y="293" font-size="13" text-anchor="middle">v1b</text>'
    '<rect class="bxt" x="436" y="270" width="72" height="36" rx="10"/>'
    '<text class="tk" x="472" y="293" font-size="13" text-anchor="middle">v2</text>'
    '<text class="ts" x="150" y="292" font-size="11" text-anchor="middle">upstream hosts</text>'
    '</svg>'
)

LESSON = {
    "id": "d58",
    "title": "Why a service mesh: proxies, sidecars and Envoy",
    "minutes": 50,
    "goal": "By the end you can explain which problems a proxy solves between services, read and change an Envoy config made of listeners, routes and clusters, and inspect a running Envoy through its admin port.",
    "guess": {
        "q": "Your app calls `http://orders/`. You add an Envoy sidecar to its Pod. What must change in the app so its calls go through the proxy?",
        "options": [
            "The URL must point at the proxy, such as `localhost:15001`",
            "Nothing: rules in the Pod's network send the traffic there",
            "The app must load an Envoy client library at startup",
            "The app must set the `HTTP_PROXY` environment variable",
        ],
        "answer": 1,
        "why": "A sidecar mesh writes packet rules (iptables) inside the Pod's network, so every connection in and out lands on the proxy first. The app keeps calling `http://orders/` and never notices.",
    },
    "terms": [
        {"term": "Proxy", "plain": "A program that receives a request meant for someone else and makes the real request on the caller's behalf."},
        {"term": "Sidecar", "plain": "A helper container that runs in the same Pod as the app and shares its network."},
        {"term": "Data plane", "plain": "The proxies that carry the real traffic between services."},
        {"term": "Control plane", "plain": "The program that configures all the proxies and usually hands out their certificates."},
        {"term": "Listener", "plain": "An address and port where Envoy accepts connections from clients."},
        {"term": "Cluster (Envoy)", "plain": "A named group of upstream hosts for one service, which Envoy balances requests across."},
        {"term": "xDS", "plain": "The family of APIs a control plane uses to send Envoy new config while it runs."},
        {"term": "Outlier detection", "plain": "Envoy watching real answers and taking a host out of the pool after it fails too often."},
    ],
    "sections": [
        {
            "h": "The problems that live between services",
            "body": (
                "Inside one program, a function call returns or throws. Between two services, a call can also hang, "
                "time out after the work was already done, hit a copy that is shutting down, or reach the wrong version. "
                "Day 44 called this east-west traffic: calls between Services inside the cluster.\n\n"
                "Picture a checkout service that calls a fraud check over HTTP. Before that call is safe in production, "
                "somebody has to decide:\n"
                "- How long to wait before giving up. That is the timeout.\n"
                "- Whether to try again, how often, and only for requests that are safe to repeat (Day 11 explained idempotent methods).\n"
                "- Whether the call is encrypted, and how the fraud check knows the caller really is checkout.\n"
                "- How to send 10% of calls to a new version of the fraud check.\n"
                "- How many calls failed and how slow they were, for each pair of services.\n\n"
                "None of this is business logic, and every service needs all of it. Left alone, each team solves it a little "
                "differently: one retries five times and another never, one waits 30 seconds and another 1. Those differences "
                "tend to surface during an outage, when they are hardest to untangle."
            ),
            "refs": [V_NANA],
        },
        {
            "h": "A library in every app, or a proxy next to it",
            "body": (
                "The first way to solve the list is a library inside every app. On the JVM you might use Resilience4j for "
                "retries and circuit breakers, plus your own TLS setup and a metrics library. Nothing extra sits on the "
                "network path, so it is fast. The costs arrive later:\n"
                "- Each language needs its own library, and they never behave quite the same.\n"
                "- A fix in the library means rebuilding and redeploying every service.\n"
                "- The settings live in each app's code, so nobody can see them all in one place.\n\n"
                "The second way moves the work out of the app into a proxy that runs next to it. The app makes a plain HTTP "
                "call. The proxy adds the timeout, the retry, the encryption and the metrics, and a second proxy on the "
                "receiving side does the same for incoming calls. Envoy's own docs give two reasons for this design: it works "
                "with any language, and you can upgrade the proxies without touching the apps.\n\n"
                "A **service mesh** is the second way at scale: a proxy next to every service, plus one control plane that "
                "configures all of them. The proxies form the data plane. The price is an extra hop on every call, and CPU and "
                "memory for every proxy. Day 60 measures it.\n\n"
                "One idea from Day 11 matters here. An L4 proxy sees TCP connections: addresses, ports and bytes. An L7 proxy "
                "reads each HTTP request: method, path, headers and status code. Retrying on a 503, routing by header and "
                "counting errors per request all need L7."
            ),
            "refs": [E_WHAT],
        },
        {
            "h": "Follow one request through Envoy",
            "body": (
                "Envoy is an L7 proxy written in C++. It started at Lyft and is a graduated CNCF project, and you met it on "
                "Day 44 inside Envoy Gateway. Istio's debugging tools print Envoy's vocabulary back at you, so it pays to "
                "learn it once.\n\n"
                "Start with two directions. Downstream is the side that sends requests to Envoy, such as curl. Upstream is "
                "the side Envoy sends them on to, such as hello-devops. Now follow one `curl localhost:10000/` through the "
                "lab's `envoy.yaml`:\n"
                "1. A listener accepts the TCP connection. Ours is called `ingress` and listens on port 10000.\n"
                "2. The listener runs its filter chain. Network filters work on raw bytes, and ours has one: the HTTP connection manager, or HCM.\n"
                "3. The HCM turns bytes into HTTP requests and runs the HTTP filters in order. Ours are a fault filter, switched off until Day 59, and the router, which must come last.\n"
                "4. The router looks up the route table. A virtual host matches the `Host` header, and `*` matches any. Inside it, the first route whose `match` fits wins.\n"
                "5. The route names a cluster, or several with weights. Ours sends 90 to `hello_v1` and 10 to `hello_v2`.\n"
                "6. The cluster's load balancer picks one endpoint, a single address and port such as `v1a:8000`, and sends the request over a pooled connection.\n\n"
                "An Envoy cluster has nothing to do with a Kubernetes cluster. It is a group of upstream hosts for one "
                "service. Each of these objects is separate in the config. That lets a control plane change a route without "
                "touching a listener, or add an endpoint without touching a route."
            ),
            "refs": [E_LIFE],
        },
        {
            "h": "Timeouts, retries and spotting a sick host",
            "body": (
                "Envoy's defaults are not what you want between services. A route waits 15 seconds, and it never retries "
                "until you say so. The lab sets both on purpose:\n"
                "- `timeout: 3s` on the route is the budget for the whole request, retries included.\n"
                "- `retry_policy` retries on `5xx,reset,connect-failure`, at most twice, with `per_try_timeout: 1s` for each attempt.\n"
                "- The `previous_hosts` predicate makes each retry pick a different host than the one that just failed.\n\n"
                "Retries hide failures, and that is both their use and their danger. If each hop in a chain of three retries "
                "twice, one user request can become 27 calls to the last service, just when it is struggling. Retry only "
                "requests that are safe to repeat, keep the count low, and give each try its own timeout.\n\n"
                "Envoy has two ways to notice a sick host. An active health check sends its own request, here `GET /healthz` "
                "every 5 seconds. Outlier detection is passive: it watches the real answers and ejects a host after "
                "`consecutive_5xx: 3`, three errors in a row. An ejected host is skipped for `base_ejection_time` (30 seconds "
                "here), and for longer each time it is ejected again. They see different things. In the worked example, one "
                "copy of the app loses its Redis: `/healthz` still says ok, but real requests fail, and only outlier detection "
                "notices.\n\n"
                "Circuit breakers are the third tool. In Envoy they are limits per cluster on connections, waiting requests, "
                "parallel requests and parallel retries, by default 1024, 1024, 1024 and 3. Past a limit, Envoy answers 503 at "
                "once instead of letting a queue grow. Istio calls connection limits plus outlier detection circuit breaking, "
                "so you will hear the word for both."
            ),
            "refs": [E_ROUTING, E_OUTLIER, E_CB],
        },
        {
            "h": "Static config, xDS and the control plane",
            "body": (
                "The lab's `envoy.yaml` is static config. Everything is in one file, and a change means restarting Envoy. "
                "That is fine for one proxy in front of three containers that never move.\n\n"
                "Kubernetes is the opposite. Pods start and stop all day, each with a new IP (Day 41), and a mesh may have "
                "hundreds of Envoys that must learn about every change within seconds. So Envoy can also fetch its config "
                "over gRPC from a server while it runs. These APIs are called xDS, one for each kind of object:\n"
                "- LDS, the listener discovery service, sends listeners.\n"
                "- RDS sends route tables.\n"
                "- CDS sends clusters.\n"
                "- EDS sends endpoints: the Pod IPs behind each cluster. They change most often.\n"
                "- SDS sends secrets, meaning TLS certificates and keys.\n\n"
                "The x stands for any of these letters. Many control planes send all of them over one stream, called ADS (the "
                "aggregated discovery service), so updates arrive in a safe order.\n\n"
                "The server on the other end is the control plane. It watches the Kubernetes API for Services, "
                "EndpointSlices and your routing objects, turns them into Envoy objects and pushes them to every proxy. In "
                "Istio that is istiod; in Envoy Gateway it is the controller from Day 44. If the control plane goes down, the "
                "proxies keep serving with the last config they received. You only lose the ability to change it.\n\n"
                "The admin interface shows what a running Envoy really has. `/config_dump` prints the live config, "
                "`/clusters` lists every host with its health, and `/stats` has counters for nearly everything. In the lab "
                "the dump lists our clusters under `static_clusters`. In an Istio sidecar the same dump fills "
                "`dynamic_active_clusters`, and `istioctl proxy-config` (Day 59) reads it for you."
            ),
            "refs": [E_XDS, E_DYN, V_XDS],
        },
        {
            "h": "How traffic reaches the proxy: sidecars, nodes and ambient",
            "body": (
                "A proxy only helps if traffic passes through it. In the lab you send requests to port 10000 by hand. In a "
                "mesh nobody changes the app's URLs, so the traffic has to be caught on its way.\n\n"
                "In sidecar mode the proxy is an extra container in every Pod. The containers of a Pod share one network "
                "(Day 39), so the proxy can see the app's traffic. Before the app starts, an init container or a CNI plugin "
                "on the node writes iptables rules inside the Pod's network. Istio's rules send outgoing connections to Envoy "
                "on port 15001 and incoming ones to port 15006. The app still calls `http://fraud-check/`, and the kernel "
                "quietly hands the connection to Envoy.\n\n"
                "Sidecars used to start and stop awkwardly. The app could start before its proxy, and a Job never finished "
                "because the proxy kept running. Kubernetes native sidecar containers fix this. A native sidecar is an init "
                "container with `restartPolicy: Always`: it starts before the app, keeps running, and stops after it. They are "
                "stable since Kubernetes 1.33, and Istio and Linkerd both use them by default now.\n\n"
                "A sidecar per Pod is easy to reason about, but 200 Pods means 200 proxies with their own memory. Two other "
                "designs share proxies:\n"
                "- A per-node proxy carries the traffic of every Pod on its node. Cilium runs Envoy this way for its HTTP features (Day 60).\n"
                "- Istio's ambient mode splits the job in two. A small L4 proxy on each node, called ztunnel, encrypts traffic for every Pod. An Envoy called a waypoint handles HTTP, only where you ask for it (Day 59).\n\n"
                "Shared proxies save memory. In exchange, a noisy neighbor can slow your traffic, and a broken node proxy "
                "hurts every Pod on that node."
            ),
            "refs": [K_SIDECAR, I_MODES],
        },
        {
            "h": "Where you will meet Envoy",
            "body": (
                "Envoy shows up all over this part of the stack, usually hidden behind a friendlier API:\n"
                "- Envoy Gateway runs it at the edge of the cluster, configured by the Gateway API (Day 44).\n"
                "- Istio runs it as every sidecar, every waypoint and every Istio gateway (Day 59).\n"
                "- Cilium runs one per node for HTTP-aware policy and routing (Day 60).\n"
                "- Consul's service mesh uses Envoy sidecars (Day 60).\n\n"
                "AWS App Mesh was Amazon's managed mesh built on Envoy. AWS ended its support on September 30, 2026, so "
                "treat any App Mesh setup you find as a migration; AWS points ECS users to ECS Service Connect. Linkerd is the "
                "odd one out: it uses its own proxy, written in Rust.\n\n"
                "Since all of these generate Envoy config, today's skills carry over. When a mesh misbehaves you end up in the "
                "same places: the listeners, the routes, the clusters with their health flags, and the stats."
            ),
            "refs": [APPMESH, CONSUL],
        },
    ],
    "analogy": (
        "A proxy next to each service works like the post room of an office building. Staff drop a letter in the out "
        "tray with just a name on it. The post room looks up the address, picks a courier, sends a second one if the "
        "first comes back empty-handed, and logs every delivery. Nobody upstairs has to learn how couriers work. A real "
        "post room adds hours and never opens the letters. Envoy adds well under a millisecond on a quiet machine, and it "
        "can read and change every header on the way through."
    ),
    "diagram": DIAGRAM,
    "diagram_caption": "One request through the lab's Envoy: listener, HTTP filters and route, then a weighted choice of cluster and host.",
    "worked": {
        "title": "Envoy in front of two versions, then break one",
        "steps": [
            {
                "say": "Copy `envoy.yaml` and `compose.yaml` from Files into `mesh/envoy` in your repo and start the lab. Compose names everything `mesh-envoy-...`. The app containers say `health: starting` for their first seconds, and Envoy runs its own health checks anyway.",
                "code": (
                    "$ docker compose up -d\n"
                    "$ docker compose ps --format 'table {{.Service}}\\t{{.Status}}\\t{{.Ports}}'\n"
                    "SERVICE   STATUS                             PORTS\n"
                    "envoy     Up 19 seconds                      127.0.0.1:9901->9901/tcp, 127.0.0.1:10000->10000/tcp\n"
                    "redis     Up 20 seconds                      6379/tcp\n"
                    "redis-b   Up 20 seconds                      6379/tcp\n"
                    "v1a       Up 19 seconds (health: starting)   8000/tcp\n"
                    "v1b       Up 19 seconds (health: starting)   8000/tcp\n"
                    "v2        Up 19 seconds (health: starting)   8000/tcp"
                ),
                "lang": "console",
            },
            {
                "say": "Send one plain request, one with the canary header, then 200 in a loop and count the versions. Envoy picks a cluster at random for each request, so 175 to 25 is a normal result for weights of 90 and 10. Run the loop again and the numbers move a little.",
                "code": (
                    "$ curl -s localhost:10000/\n"
                    "{\"host\":\"c32bed2a13e5\",\"message\":\"Hello, DevOps!\",\"version\":\"1.0.0\",\"visits\":1}\n"
                    "$ curl -s -H 'x-canary: always' localhost:10000/\n"
                    "{\"host\":\"dc25b52d7641\",\"message\":\"Hello from the canary!\",\"version\":\"2.0.0\",\"visits\":2}\n"
                    "$ for i in $(seq 1 200); do curl -s localhost:10000/ | jq -r .version; done | sort | uniq -c\n"
                    "    175 1.0.0\n"
                    "     25 2.0.0"
                ),
                "lang": "console",
            },
            {
                "say": "Ask the admin interface what happened. The `/clusters` page lists each host with its name, health and request count. Round robin shared the version 1 traffic almost evenly between v1a and v1b. The `/stats` page takes a regular expression as its filter.",
                "code": (
                    "$ curl -s localhost:9901/clusters | grep -E '::(hostname|health_flags|rq_total)::'\n"
                    "hello_v1::172.20.0.5:8000::rq_total::89\n"
                    "hello_v1::172.20.0.5:8000::hostname::v1a\n"
                    "hello_v1::172.20.0.5:8000::health_flags::healthy\n"
                    "hello_v1::172.20.0.4:8000::rq_total::87\n"
                    "hello_v1::172.20.0.4:8000::hostname::v1b\n"
                    "hello_v1::172.20.0.4:8000::health_flags::healthy\n"
                    "hello_v2::172.20.0.6:8000::rq_total::26\n"
                    "hello_v2::172.20.0.6:8000::hostname::v2\n"
                    "hello_v2::172.20.0.6:8000::health_flags::healthy\n"
                    "$ curl -s 'localhost:9901/stats?filter=^http\\.ingress_http\\.downstream_rq_(total|2xx|5xx)$'\n"
                    "http.ingress_http.downstream_rq_2xx: 202\n"
                    "http.ingress_http.downstream_rq_5xx: 0\n"
                    "http.ingress_http.downstream_rq_total: 202"
                ),
                "lang": "console",
            },
            {
                "say": "Now break one copy. `v1b` has its own Redis, so stop it: `/` on v1b now answers 500, while its `/healthz` still answers 200. The client saw twenty 200s anyway. Three requests failed on v1b and Envoy retried them on v1a, and after the third error in a row outlier detection ejected v1b.",
                "code": (
                    "$ docker compose stop redis-b\n"
                    "$ for i in $(seq 1 20); do curl -s -o /dev/null -w '%{http_code}\\n' localhost:10000/; done | sort | uniq -c\n"
                    "     20 200\n"
                    "$ curl -s 'localhost:9901/stats?filter=^cluster\\.hello_v1\\.(upstream_rq_retry|upstream_rq_retry_success|outlier_detection\\.ejections_active)$'\n"
                    "cluster.hello_v1.outlier_detection.ejections_active: 1\n"
                    "cluster.hello_v1.upstream_rq_retry: 3\n"
                    "cluster.hello_v1.upstream_rq_retry_success: 3"
                ),
                "lang": "console",
            },
            {
                "say": "`/clusters` shows the ejection as a health flag, while the active health check keeps passing. That is why the lab sets `successful_active_health_check_uneject_host: false`. Without it, the next good `/healthz` would put v1b straight back into the pool.",
                "code": (
                    "$ curl -s localhost:9901/clusters | grep -E 'hello_v1::.*::(hostname|health_flags)::'\n"
                    "hello_v1::172.20.0.5:8000::hostname::v1a\n"
                    "hello_v1::172.20.0.5:8000::health_flags::healthy\n"
                    "hello_v1::172.20.0.4:8000::hostname::v1b\n"
                    "hello_v1::172.20.0.4:8000::health_flags::/failed_outlier_check\n"
                    "$ curl -s 'localhost:9901/stats?filter=^cluster\\.hello_v1\\.health_check\\.(success|failure)$'\n"
                    "cluster.hello_v1.health_check.failure: 0\n"
                    "cluster.hello_v1.health_check.success: 18"
                ),
                "lang": "console",
            },
            {
                "say": "Peek at the live config, then repair and clean up. The dump has one section per xDS type, and our two clusters sit under `static_clusters`. Start Redis again: after the 30-second ejection, v1b is back. Then stop the lab.",
                "code": (
                    "$ curl -s localhost:9901/config_dump | jq -r '.configs[].\"@type\"'\n"
                    "type.googleapis.com/envoy.admin.v3.BootstrapConfigDump\n"
                    "type.googleapis.com/envoy.admin.v3.ClustersConfigDump\n"
                    "type.googleapis.com/envoy.admin.v3.ListenersConfigDump\n"
                    "type.googleapis.com/envoy.admin.v3.ScopedRoutesConfigDump\n"
                    "type.googleapis.com/envoy.admin.v3.RoutesConfigDump\n"
                    "type.googleapis.com/envoy.admin.v3.SecretsConfigDump\n"
                    "$ curl -s localhost:9901/config_dump | jq -r '.configs[1].static_clusters[].cluster.name'\n"
                    "hello_v1\n"
                    "hello_v2\n"
                    "$ docker compose start redis-b\n"
                    "$ docker compose down"
                ),
                "lang": "console",
            },
        ],
    },
    "code": [
        {"lang": "yaml", "title": "mesh/envoy/envoy.yaml", "src": lab("envoy/envoy.yaml"),
         "run": "docker run --rm -v \"$PWD/envoy.yaml:/etc/envoy/envoy.yaml:ro\" envoyproxy/envoy:v1.40.2 envoy --mode validate -c /etc/envoy/envoy.yaml"},
        {"lang": "yaml", "title": "mesh/envoy/compose.yaml", "src": lab("envoy/compose.yaml"),
         "run": "cd mesh/envoy && docker compose up -d"},
    ],
    "commands": [
        {"cmd": "docker compose up -d", "what": "Start Envoy, three app containers and two Redis containers in the background."},
        {"cmd": "curl -s localhost:10000/", "what": "Send one request through Envoy's listener."},
        {"cmd": "curl -s -H 'x-canary: always' localhost:10000/", "what": "Send a request that the header route sends to the canary."},
        {"cmd": "curl -s localhost:9901/clusters", "what": "List every upstream host with its health flags and counters."},
        {"cmd": "curl -s 'localhost:9901/stats?filter=^cluster\\.hello_v1\\.'", "what": "Show only the stats whose names match a regular expression."},
        {"cmd": "curl -s localhost:9901/config_dump", "what": "Print the config Envoy is really running, one section per xDS type."},
        {"cmd": "curl -s localhost:9901/listeners", "what": "List the listeners and the addresses they bind."},
        {"cmd": "curl -s localhost:9901/ready", "what": "Print Envoy's state; LIVE means it is serving."},
        {"cmd": "curl -s localhost:9901/memory", "what": "Show how much memory Envoy has allocated."},
        {"cmd": "docker run --rm -v \"$PWD/envoy.yaml:/etc/envoy/envoy.yaml:ro\" envoyproxy/envoy:v1.40.2 envoy --mode validate -c /etc/envoy/envoy.yaml",
         "what": "Check a config file for errors without starting the proxy."},
        {"cmd": "docker compose logs envoy", "what": "Read Envoy's access log: one line per request with status, response flags and upstream host."},
        {"cmd": "docker compose restart envoy", "what": "Restart only Envoy, so it reads a changed static config."},
        {"cmd": "docker compose stop redis-b", "what": "Break one app copy on purpose: its Redis disappears and `/` starts failing."},
        {"cmd": "docker compose pause v2", "what": "Freeze a container, so requests to it hang until a timeout fires."},
        {"cmd": "docker compose down", "what": "Stop and remove every container of the lab."},
    ],
    "mistake": (
        "Turning on generous retries without a per-try timeout is how a slow service gets pushed over. Every failed call "
        "comes back two or three times, and the extra load arrives just when the service is weakest. Without a per-try "
        "timeout, one slow attempt can also use up the whole request budget, so the retry never happens. Allow one or two retries, set `per_try_timeout` well below the route "
        "`timeout`, and retry only requests that are safe to repeat."
    ),
    "real_world": (
        "After a deploy, one of five copies of a payment adapter starts timing out while its health endpoint still says ok. "
        "Without outlier detection, every fifth checkout waits three seconds and then fails. With it, the proxy stops "
        "sending traffic to that copy after three errors, and the dashboard shows one ejection instead of a wall of "
        "timeouts. Few teams write Envoy config by hand for this. They set the same numbers through Istio or Envoy Gateway "
        "objects, and read them back through the admin port when something looks wrong."
    ),
    "task": {
        "title": "Tune the proxy, then watch a timeout fire",
        "steps": [
            "Start the Day 58 lab and confirm the 90/10 split with a loop of 200 requests.",
            "Change the weights in `envoy.yaml` to 50 and 50, run `docker compose restart envoy`, and count again.",
            "Add a route above the others that sends `/healthz` (an exact path) to `hello_v1` only.",
            "Call `/healthz` 20 times and check in `/clusters` that `rq_total` for the `hello_v2` host does not grow.",
            "Freeze the canary with `docker compose pause v2`. Send 20 requests and print each status code and total time.",
            "Find the failed requests in `docker compose logs envoy` and read their response flags. Then read `upstream_rq_per_try_timeout` and `upstream_rq_retry` for `hello_v2` in `/stats`.",
            "Run `docker compose unpause v2`, put the weights back to 90 and 10, and commit `mesh/envoy` to your repo.",
        ],
        "hints": [
            "A route's `match` can use `path: /healthz` for an exact path. Routes are tried from top to bottom, so the specific one goes first.",
            "`hello_v2` has one host. A retry has nowhere else to go, and outlier detection with `max_ejection_percent: 50` cannot eject the only host.",
            "In the access log, the field after the status code is the response flags. `UT` means the upstream request timed out.",
        ],
        "done_when": "You are done when the 50/50 loop shows about 100 of each version, `/healthz` never reaches `hello_v2`, and you can explain why about half the requests ended in 504 after 3 seconds while v2 was paused.",
    },
    "explain_back": {
        "prompt": "Explain in 3 to 4 sentences how one request travels through Envoy and how Envoy decides a host is sick. Mention listener, route, cluster and outlier detection.",
        "answer": (
            "A listener accepts the connection on a port, and its HTTP connection manager turns the bytes into requests and "
            "runs the HTTP filters. The router matches each request against the route table, and the matching route picks a "
            "cluster, here with weights of 90 and 10. The cluster's load balancer picks one healthy endpoint and sends the "
            "request there. Active health checks call a path like `/healthz` on a timer. Outlier detection watches the real "
            "answers and ejects a host after a few errors in a row, so a host that is up but broken still gets removed."
        ),
    },
    "recap": [
        "Timeouts, retries, mTLS, traffic splits and per-call metrics are needed by every service, so they belong in shared infrastructure.",
        "A mesh puts a proxy next to every service (the data plane) and one control plane in charge of them.",
        "In Envoy, a listener accepts, the HTTP connection manager runs filters, a route picks a cluster and the cluster picks an endpoint.",
        "Health checks probe hosts, outlier detection watches real traffic, and circuit breakers fail fast. Keep retries few and short.",
        "xDS (LDS, RDS, CDS, EDS, SDS) changes Envoy's config while it runs; the admin port shows what it really has.",
        "Sidecars catch traffic with iptables rules in the Pod; per-node and ambient designs share proxies to save memory.",
    ],
    "check": [
        {
            "q": "An Envoy cluster has three hosts. One starts answering 500 to real requests while its `/healthz` keeps answering 200. Which feature takes it out of the pool?",
            "options": [
                "Active health checking on `/healthz`",
                "Outlier detection on consecutive 5xx",
                "The route's `timeout` setting",
                "A higher `max_connections` limit",
            ],
            "answer": 1,
            "why": "Outlier detection judges the real answers; the health check only proves that `/healthz` works.",
        },
        {
            "q": "A gateway calls service A, A calls B, and B calls C. Each of the three hops makes up to three tries (one call plus two retries). C is down. How many calls can one user request cause at C?",
            "options": ["3 calls", "9 calls", "27 calls", "81 calls"],
            "answer": 2,
            "why": "Each hop multiplies the one below it: 3 x 3 x 3 = 27 calls land on C.",
        },
        {
            "q": "You add a route to a static `envoy.yaml`, save the file, and Envoy keeps serving the old routes. What is the most likely reason?",
            "options": [
                "Static config is read at startup, so Envoy needs a restart",
                "Routes can only arrive over EDS, never from a file",
                "The admin port blocks changes while it is open",
                "Envoy loads new routes only after a health check passes",
            ],
            "answer": 0,
            "why": "A static file is loaded when Envoy starts; changes without a restart need xDS from a control plane.",
        },
    ],
    "interview": [
        {
            "q": "What is a service mesh, and what problem does it solve?",
            "a": (
                "A service mesh is a set of proxies next to every service, plus a control plane that configures them. It moves "
                "the network concerns of service-to-service calls out of application code: timeouts, retries, mTLS with "
                "workload identity, traffic splitting and per-call metrics. Every service gets the same behavior in any "
                "language, and the platform team can change it without redeploying apps. The price is an extra hop per call, "
                "CPU and memory for the proxies, and one more system to run and debug."
            ),
        },
        {
            "q": "Explain Envoy's listeners, routes, clusters and endpoints.",
            "a": (
                "A listener is an address and port where Envoy accepts connections, with a chain of filters. For HTTP, the HTTP "
                "connection manager parses requests and passes them through HTTP filters, ending with the router. The router "
                "matches each request against a route table, and the matching route names a cluster, or several with weights. "
                "A cluster is a group of upstream hosts with a load balancing policy, health checks and outlier detection, and "
                "each endpoint is one address and port in it. A control plane can update each layer on its own over LDS, RDS, "
                "CDS and EDS."
            ),
        },
        {
            "q": "What is the difference between the data plane and the control plane?",
            "a": (
                "The data plane is the set of proxies that carry every request: sidecars, waypoints or node proxies. The control "
                "plane carries no user traffic. It watches the platform, turns your config into proxy config, pushes it over xDS "
                "and usually signs certificates. If it fails, the proxies keep serving with their last config, and you cannot "
                "change anything until it is back."
            ),
        },
    ],
    "deeper": {
        "minutes": 12,
        "body": (
            "Two Envoy defaults surprised me while testing this lab, and both are worth knowing before you meet them at work.\n\n"
            "The first run looked broken in `/clusters`. Every host carried the flag `/failed_active_hc`, yet every request "
            "worked. Two things were going on:\n"
            "1. Envoy ran its first health checks the moment it started, while gunicorn in the app containers was still booting. They failed with a network error.\n"
            "2. A cluster that has had no traffic yet is checked only every `no_traffic_interval`, which is 60 seconds by default. So the hosts stayed marked unhealthy for a whole minute after the apps were up.\n\n"
            "Requests still worked because of the panic threshold. When fewer than 50% of a cluster's hosts are healthy, "
            "Envoy stops trusting the health flags and balances across all hosts. The reasoning is that a broken health "
            "check should not take down a service whose hosts are fine. You can change the threshold, or tell Envoy to fail "
            "all traffic in panic, in the cluster's load balancing settings. The lab sets `no_traffic_interval: 5s`, so the "
            "flags turn healthy within seconds.\n\n"
            "The second surprise was ejection. Outlier detection never ejects more than `max_ejection_percent` of a cluster, "
            "and the default is 10%. In a cluster of two hosts, 10% is less than one host, so nobody is ever ejected. That is "
            "why the lab sets 50%. The hands-on shows the same rule from the other side: `hello_v2` has one host, so it is "
            "never ejected, and Envoy keeps sending it traffic while it times out.\n\n"
            "Put together, these rules show a design choice. Envoy would rather send traffic to hosts that might be sick than "
            "send it nowhere. That is usually right, but a small cluster gets little protection from outlier detection. Run "
            "at least three copies of anything that matters, and look at `/clusters` before you trust a dashboard.\n\n"
            "The [outlier detection](https://www.envoyproxy.io/docs/envoy/latest/intro/arch_overview/upstream/outlier) and "
            "[health checking](https://www.envoyproxy.io/docs/envoy/latest/intro/arch_overview/upstream/health_checking) "
            "pages of the Envoy docs list every setting with its default."
        ),
    },
    "sources": [
        S("What is Envoy", E_WHAT["url"]),
        S("Envoy: life of a request", E_LIFE["url"]),
        S("Envoy: xDS REST and gRPC protocol", E_XDS["url"]),
        S("Envoy: the administration interface", E_ADMIN["url"]),
    ],
}
