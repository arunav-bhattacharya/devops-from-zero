"""Book-voice rewrite of d58 (Why a service mesh: proxies, sidecars and Envoy). Writer: th."""
import sys
sys.path.insert(0, "/home/user/devops-from-zero/brief/scratch/v5/th")
from common import apply, load, lesson

OPENING = """Picture an office building with forty small offices, one team in each. All day, people walk the corridors with requests for each other. Each team has its own habits. One knocks five times and then knocks again. Another gives up after one second. Nobody checks who is at the door. One afternoon the payroll office slows down and a queue forms outside it. Soon the people stuck in that queue are late for everyone waiting on them. By four o'clock half the building is standing in corridors.

No team did anything foolish. Each habit made sense from inside one office. The trouble lives between the offices, where nobody is in charge.

Last time, a tracking number showed us which call between two programs was slow. It could not make that call behave any better. Today we put a receptionist at one door: a proxy called Envoy, which we configure by hand and then break on purpose.

Before we start, make a guess, and keep it in mind."""

S1 = """Inside one program, a function call (one piece of code asking another to do a job) returns an answer or raises an error. Between two services, separate programs that talk over the network, a call has more ways to go wrong. It can hang. It can time out after the work was already done. It can reach a copy that is shutting down, or the wrong version. Day 44 called these calls east-west traffic: calls between services inside a Kubernetes cluster, the group of machines that runs your containers.

Our lab app, hello-devops, is a tiny web app that answers every visit with a greeting and a count of visits so far. Today we run several copies of it, so it can play both a healthy service and a sick one.

Now picture a checkout service that calls a fraud check over HTTP, the language of web requests. Before that call is safe in production, somebody has to decide:
- How long to wait before giving up. That is the timeout.
- Whether to try again, how often, and only for requests that are safe to repeat (Day 11 called them idempotent).
- Whether the call is encrypted, and how the fraud check knows the caller really is checkout.
- How to send 10% of calls to a new version of the fraud check.
- How many calls failed and how slow they were, for each pair of services.

None of this is business logic, the work the service exists to do, and every service needs all of it. Left alone, each team solves it a little differently: one retries five times and another never, one waits 30 seconds and another 1. Those are the office habits from the opening. The differences tend to surface during an outage, when they are hardest to untangle.

Next, we'll weigh two ways to solve the list once."""

S2 = """There are two places to put this work. The first is a library, ready-made code, inside every app. A Java app might use Resilience4j for retries and circuit breakers, which stop calling a service that keeps failing. Add your own encryption setup and a metrics library. Nothing extra sits on the network path, so it is fast. The costs arrive later:
- Each language needs its own library, and they never behave quite the same.
- A fix in the library means rebuilding and redeploying every service.
- The settings live in each app's code, so nobody can see them all in one place.

The second way moves the work out of the app into a proxy. A proxy is a program that receives a request meant for someone else and makes the real call on the caller's behalf. It is the receptionist at the office door. The app makes a plain HTTP call. The proxy adds the timeout, the retry, the encryption and the metrics. A second proxy on the receiving side does the same for incoming calls.

The two proxies talk with mutual TLS, or mTLS. TLS is the encryption behind `https` (Day 11). In mTLS both sides show a certificate, a signed digital ID card, so each knows who the other is. It is a receptionist checking a visitor's badge. Day 59 sets it up. Envoy's own docs give two reasons for this design: it works with any language, and you can upgrade the proxies without touching the apps.

A service mesh is the second way at scale. A proxy sits next to every service, and those proxies form the data plane. One control plane, the building manager, configures all of them. The price is an extra hop on every call, plus CPU and memory for every proxy. Day 60 measures it.

One more idea from Day 11 matters here. An L4 proxy sees only connections: addresses, ports and bytes. An L7 proxy reads each HTTP request: method, path, headers and status code. Retrying on a 503 (the "service unavailable" answer), routing by header and counting errors per request all need L7.

Next, we'll follow one request through a real L7 proxy."""

S3 = """Envoy is an L7 proxy, and you met it on Day 44 inside Envoy Gateway. Istio's debugging tools print Envoy's words back at you, so it pays to learn them once.

Start with two directions. Downstream is the side that sends requests to Envoy, such as curl, the terminal command that sends web requests. Upstream is the side Envoy sends them on to, such as hello-devops. The lab runs three copies of the app: `v1a` and `v1b` of version 1, and `v2`, a canary (a new version that gets a small share of traffic first).

Now follow one `curl localhost:10000/` through the lab's settings file, `envoy.yaml`:
1. A listener accepts the connection. Ours is called `ingress` and listens on port 10000.
2. The listener runs its filter chain. Network filters work on raw bytes, and ours has one: the HTTP connection manager, or HCM.
3. The HCM turns bytes into HTTP requests and runs the HTTP filters in order. Ours are a fault filter, switched off until Day 59, and the router, which must come last.
4. The router looks up the route table. A virtual host matches the `Host` header (the name the caller asked for), and `*` matches any. Inside it, the first route whose `match` fits wins.
5. The route names a cluster, or several with weights. Ours sends 90 to `hello_v1` and 10 to `hello_v2`.
6. The cluster's load balancer picks one endpoint, a single address and port such as `v1a:8000`. It sends the request over a pooled connection, one that Envoy keeps open and reuses.

Many of Envoy's features are filters: plug-in steps that see the traffic, may change or answer it, and pass it on. An Envoy that only proxies L4 holds the TCP proxy filter where ours holds the HCM, and never reads HTTP. The router comes last because it is the filter that sends the request upstream, so nothing after it would run.

An Envoy cluster has nothing to do with a Kubernetes cluster. It is a group of upstream hosts for one service. The lab lists host names such as `v1a`, and `type: STRICT_DNS` makes Envoy look them up in Compose's DNS (Day 20), the name lookup that turns `v1a` into an address. Each of these objects is separate in the config. That lets a control plane change a route without touching a listener, or add an endpoint without touching a route.

The request found its way. Next, we'll make it survive a sick host."""

S4 = """Envoy's defaults are not what you want between services. A route waits 15 seconds, and it never retries until you say so. The lab sets both on purpose:
- `timeout: 3s` on the route is the budget for the whole request, retries included.
- `retry_policy` retries on `5xx,reset,connect-failure` (an error status, a dropped connection or a failed connect), at most twice, with `per_try_timeout: 1s` each.
- The `previous_hosts` predicate makes each retry pick a different host than the one that just failed.

Retries hide failures, and that is both their use and their danger. The naive setting is generous: retry everything, many times, with no limit per try. Now picture a chain of three services, each retrying twice. One user request can become 27 calls to the last service, just when it is struggling. Without a per-try timeout, one slow attempt can also use up the whole budget, so the retry never even happens. **Retries multiply the load on a sick service. Keep them few, short, and only for requests that are safe to repeat.**

Envoy has two ways to notice a sick host. An active health check sends its own request, here `GET /healthz` every 5 seconds. Outlier detection is passive: it watches the real answers and ejects a host after `consecutive_5xx: 3`, three errors in a row. An ejected host is skipped for `base_ejection_time` (30 seconds here), and for longer each time it is ejected again.

They see different things. In the worked example, one copy of the app loses Redis, the small database that keeps its visit count. Its `/healthz` still says ok, but real requests fail, and only outlier detection notices. It is a receptionist who stops sending visitors to an office whose door is open but whose phone is never answered.

Circuit breakers are the third tool. In Envoy they are limits per cluster on connections, waiting requests, parallel requests and parallel retries, by default 1024, 1024, 1024 and 3. Past a limit, Envoy answers 503 at once instead of letting a queue grow. A growing queue is how one slow service makes its callers slow too, because their threads (lines of work) and connections all sit waiting. That was the payroll corridor in the opening. Istio calls connection limits plus outlier detection circuit breaking, so you will hear the word for both.

Next, we'll see why one config file is fine for three containers and hopeless for three hundred."""

S5 = """The lab's `envoy.yaml` is static config. Everything is in one file, and a change means restarting Envoy. That is fine for one proxy in front of three containers that never move.

Kubernetes is the opposite. Kubernetes runs containers across many machines. Each Pod, its wrapper around an app's containers, starts and stops all day with a new IP address (Day 41). A mesh may have hundreds of Envoys that must learn about every change within seconds. So Envoy can also fetch its config from a server while it runs, over gRPC, a fast way for programs to call each other.

Envoy still starts from a small static file, the bootstrap, which says where that server is. The rest arrives over APIs (sets of requests one program offers another) called xDS, one for each kind of object:
- LDS, the listener discovery service, sends listeners.
- RDS sends route tables.
- CDS sends clusters.
- EDS sends endpoints: the Pod IPs behind each cluster. They change most often.
- SDS sends secrets, meaning TLS certificates and keys.

The x stands for any of these letters. Order matters: a route that names a cluster Envoy has not received yet sends its traffic nowhere. So many control planes send everything over one stream, called ADS (the aggregated discovery service), clusters before the routes that use them.

The server on the other end is the control plane, our building manager. It watches the Kubernetes API for Services, for EndpointSlices (the lists of Pod addresses behind a Service) and for your routing objects. It turns them into Envoy objects and pushes them to every proxy. In Istio that is istiod; in Envoy Gateway it is the controller from Day 44. If the control plane goes down, the proxies keep serving with the last config they received. You only lose the ability to change it.

The admin interface shows what a running Envoy really has. `/config_dump` prints the live config, `/clusters` lists every host with its health, and `/stats` has counters for nearly everything. In the lab the dump lists our clusters under `static_clusters`. In an Istio sidecar the same dump fills `dynamic_active_clusters`, and `istioctl proxy-config` (Day 59) reads it for you.

Next, we'll answer the guess: how does traffic reach the proxy when nobody changed the app?"""

S6 = """A proxy only helps if traffic passes through it. In the lab you send requests to port 10000 by hand. In a mesh nobody changes the app's URLs, so the traffic has to be caught on its way.

In sidecar mode the proxy is an extra container in every Pod, called a sidecar. The containers of a Pod share one network (Day 39), so the proxy can see the app's traffic. Before the app starts, a setup step writes iptables rules inside the Pod's network. These are packet rules kept by the kernel, the core of the operating system, and kube-proxy writes the same kind (Day 41). The setup step is an init container or a CNI plugin, the node's network add-on.

Istio's rules send outgoing connections to Envoy on port 15001 and incoming ones to port 15006. The app still calls `http://fraud-check/`, and the kernel quietly hands the connection to Envoy. That answers the guess: nothing in the app changes.

So how does Envoy know where the app meant to go? The kernel remembers the original address of every redirected connection, and Envoy reads it back. The rules also skip traffic sent by the proxy's own user (ID 1337 in Istio). Otherwise Envoy's outgoing calls would loop straight back into Envoy.

Sidecars used to start and stop awkwardly. The app could start before its proxy, and a Job (a Pod that runs a task to the end) never finished because the proxy kept running. Kubernetes native sidecar containers (Day 39) fix this. A native sidecar is an init container with `restartPolicy: Always`: it starts before the app, keeps running, and stops after it. They are stable since Kubernetes 1.33, and Istio and Linkerd both use them by default now.

A sidecar per Pod is easy to reason about, but 200 Pods means 200 proxies with their own memory. Two other designs share proxies:
- A per-node proxy carries the traffic of every Pod on its node (machine). Cilium runs Envoy this way for its HTTP features (Day 60).
- Istio's ambient mode splits the job in two. A small L4 proxy on each node, called ztunnel, encrypts traffic for every Pod. An Envoy called a waypoint handles HTTP, only where you ask for it (Day 59).

Shared proxies save memory. In exchange, a noisy neighbor can slow your traffic, and a broken node proxy hurts every Pod on that node. It is one receptionist for a whole floor instead of one per office.

Next, we'll count how many tools you already use have an Envoy inside."""

S7 = """Envoy shows up all over this part of the stack, usually hidden behind a friendlier API:
- Envoy Gateway runs it at the edge of the cluster, configured by the Gateway API (Day 44).
- Istio runs it as every sidecar, every waypoint and every Istio gateway (Day 59).
- Cilium runs one per node for HTTP-aware policy and routing (Day 60).
- Consul's service mesh uses Envoy sidecars (Day 60).

All of these generate Envoy config, so today's skills carry over. When a mesh misbehaves you end up in the same places: the listeners, the routes, the clusters with their health flags, and the stats.

Today's hand-written proxy has clear limits. It serves three containers on one laptop, every change needs a restart, and there is no encryption or identity between the services yet. Few teams write Envoy config by hand for a real cluster. They set the same numbers through Istio or Envoy Gateway objects, and read them back through the admin port when something looks wrong. The next lesson hands the writing to Istio."""

CLOSING = """We started in an office building where every team had its own habits at the door, and one slow office jammed the corridors. Today one receptionist, Envoy, set a time limit, tried another door, and stopped sending visitors to an office that had stopped answering. In the lab, stop `redis-b` and watch `/clusters` show `/failed_outlier_check` while `/healthz` keeps passing. In your own services, look for a call to another service that has no timeout.

Next, we'll hand the receptionists to a building manager, Istio. How does every proxy get its rules and its ID badge without anyone writing a file?"""

ASIDE = {
    "title": "Is every mesh built on Envoy?",
    "body": "No. Linkerd is the odd one out: it uses its own proxy, written in Rust. AWS App Mesh was Amazon's managed mesh built on Envoy. AWS ended its support on September 30, 2026, so treat any App Mesh setup you find as a migration. AWS points users of ECS, its own container service, to ECS Service Connect.",
    "after": 6,
}

L = lesson(load(15), "d58")
deeper = L["deeper"]["body"]
for a, b in [("Two Envoy defaults surprised me while testing this lab, and both", "Two Envoy defaults surprised the lab tests, and both")]:
    deeper = deeper.replace(a, b)
deeper = deeper.split("\n\nA little history")[0]
EXTRA = "\n\nA little history, for when you read about Envoy elsewhere. It is written in C++ and started at Lyft. It is also a graduated CNCF project, the most mature level of the non-profit foundation that looks after Kubernetes."
if EXTRA.strip() not in deeper:
    deeper += EXTRA

new = {
    "goal": "By the end you can explain which problems a proxy solves between services, read and change an Envoy config made of listeners, routes and clusters, and inspect a running Envoy through its admin port.",
    "opening": OPENING,
    "guess": (
        "Your app calls `http://orders/`. You add an Envoy sidecar, a helper container, to its Pod. What must change in the app so its calls go through the proxy?",
        "A sidecar mesh writes packet rules (iptables) inside the Pod's network, so every connection in and out lands on the proxy first. The app keeps calling `http://orders/` and never notices.",
    ),
    "terms": [
        "A program that receives a request meant for someone else and makes the real request on the caller's behalf.",
        "A helper container that runs in the same Pod as the app and shares its network.",
        "The proxies that carry the real traffic between services.",
        "The program that configures all the proxies and usually hands out their certificates.",
        "An address and port where Envoy accepts connections from clients.",
        "A named group of upstream hosts for one service, which Envoy spreads requests across.",
        "The family of APIs a control plane uses to send Envoy new config while it runs.",
        "Envoy watching real answers and taking a host out of the pool after it fails too often.",
    ],
    "sections": [
        ("The problems that live between services", S1),
        ("A library in every app, or a proxy next to it", S2),
        ("Follow one request through Envoy", S3),
        ("Timeouts, retries and spotting a sick host", S4),
        ("Static config, xDS and the control plane", S5),
        ("How traffic reaches the proxy: sidecars, nodes and ambient", S6),
        ("Where you will meet Envoy, and where hand-written config stops", S7),
    ],
    "aside": ASIDE,
    "diagram_caption": "One request through the lab's Envoy: listener, HTTP filters and route, then a weighted choice of cluster and host.",
    "say": [
        "Copy `envoy.yaml` and `compose.yaml` from Files into `mesh/envoy` in your repo and start the lab. Compose names everything `mesh-envoy-...`. The app containers say `health: starting` for their first seconds while Docker's own health check waits, and Envoy runs its own health checks anyway.",
        "Send one plain request, one with the canary header, then 200 in a loop and count the versions. Envoy picks a cluster at random for each request, so 175 to 25 is a normal result for weights of 90 and 10. Run the loop again and the numbers move a little.",
        "Ask the admin interface what happened. The `/clusters` page lists each host with its name, health and request count. Round robin (taking turns) shared the version 1 traffic almost evenly between v1a and v1b. The `/stats` page takes a regular expression, a text pattern, as its filter.",
        "Now break one copy. `v1b` has its own Redis, so stop it: `/` on v1b now answers 500, while its `/healthz` still answers 200. The client saw twenty 200s anyway. Three requests failed on v1b and Envoy retried them on v1a. After the third error in a row, outlier detection ejected v1b.",
        "`/clusters` shows the ejection as a health flag, while the active health check keeps passing. That is why the lab sets `successful_active_health_check_uneject_host: false`. Without it, the next good `/healthz` would put v1b straight back into the pool.",
        "Peek at the live config, then repair and clean up. The dump has one section per xDS type, and our two clusters sit under `static_clusters`. Start Redis again, and after the 30-second ejection v1b is back. Then stop the lab.",
    ],
    "task": (
        [
            "Start the Day 58 lab and confirm the 90/10 split with a loop of 200 requests.",
            "Change the weights in `envoy.yaml` to 50 and 50, run `docker compose restart envoy`, and count again.",
            "Add a route above the others that sends `/healthz` (an exact path) to `hello_v1` only.",
            "Call `/healthz` 20 times and check in `/clusters` that `rq_total` for the `hello_v2` host does not grow.",
            "Freeze the canary with `docker compose pause v2`. Send 20 requests and print each status code and total time.",
            "Find the failed requests in `docker compose logs envoy` and read their response flags. Then read `upstream_rq_per_try_timeout` and `upstream_rq_retry` for `hello_v2` in `/stats`.",
            "Run `docker compose unpause v2`, put the weights back to 90 and 10, and commit `mesh/envoy` to your repo.",
        ],
        [
            "A route's `match` can use `path: /healthz` for an exact path. Routes are tried from top to bottom, so the specific one goes first.",
            "`hello_v2` has one host. A retry has nowhere else to go, and outlier detection with `max_ejection_percent: 50` cannot eject the only host.",
            "In the access log, the field after the status code is the response flags. `UT` means the upstream request timed out.",
        ],
        "You are done when the 50/50 loop shows about 100 of each version, `/healthz` never reaches `hello_v2`, and you can explain why about half the requests ended in 504 after 3 seconds while v2 was paused.",
    ),
    "explain_back": (
        "Explain in 3 to 4 sentences how one request travels through Envoy and how Envoy decides a host is sick. Mention listener, route, cluster and outlier detection.",
        "A listener accepts the connection on a port, and its HTTP connection manager turns the bytes into requests and runs the HTTP filters. The router matches each request against the route table, and the matching route picks a cluster, here with weights of 90 and 10. The cluster's load balancer picks one healthy endpoint and sends the request there. Active health checks call a path like `/healthz` on a timer. Outlier detection watches the real answers and ejects a host after a few errors in a row, so a host that is up but broken still gets removed.",
    ),
    "recap": [
        "Every service needs timeouts, retries, mTLS, traffic splits and per-call metrics; a mesh puts a proxy (data plane) next to each, run by one control plane.",
        "In Envoy, a listener accepts, the HTTP connection manager runs filters, a route picks a cluster and the cluster picks an endpoint.",
        "Health checks probe hosts, outlier detection watches real traffic, and circuit breakers fail fast. Keep retries few and short.",
        "xDS (LDS, RDS, CDS, EDS, SDS) changes Envoy's config while it runs; the admin port shows what it really has.",
        "Sidecars catch traffic with iptables rules in the Pod; per-node and ambient designs share proxies to save memory.",
        "A hand-written static Envoy suits a lab only: real clusters need a control plane, and every proxy costs a hop and memory.",
    ],
    "closing": CLOSING,
    "check": [
        ("An Envoy cluster has three hosts. One starts answering 500 to real requests while its `/healthz` keeps answering 200. Which feature takes it out of the pool?",
         "Outlier detection judges the real answers. The health check only proves that `/healthz` works."),
        ("A gateway calls service A, A calls B, and B calls C. Each of the three hops makes up to three tries (one call plus two retries). C is down. How many calls can one user request cause at C?",
         "Each hop multiplies the one below it: 3 x 3 x 3 = 27 calls land on C."),
        ("You add a route to a static `envoy.yaml`, save the file, and Envoy keeps serving the old routes. What is the most likely reason?",
         "A static file is loaded when Envoy starts. Changes without a restart need xDS from a control plane."),
    ],
    "interview": [
        ("What is a service mesh, and what problem does it solve?",
         "A service mesh is a set of proxies next to every service, plus a control plane that configures them. It moves the network concerns of service-to-service calls out of application code: timeouts, retries, mTLS with workload identity, traffic splitting and per-call metrics. Every service gets the same behavior in any language, and the platform team can change it without redeploying apps. The price is an extra hop per call, CPU and memory for the proxies, and one more system to run and debug."),
        ("Explain Envoy's listeners, routes, clusters and endpoints.",
         "A listener is an address and port where Envoy accepts connections, with a chain of filters. For HTTP, the HTTP connection manager parses requests and passes them through HTTP filters, ending with the router. The router matches each request against a route table, and the matching route names a cluster, or several with weights. A cluster is a group of upstream hosts with a load balancing policy, health checks and outlier detection, and each endpoint is one address and port in it. A control plane can update each layer on its own over LDS, RDS, CDS and EDS."),
        ("What is the difference between the data plane and the control plane?",
         "The data plane is the set of proxies that carry every request: sidecars, waypoints or node proxies. The control plane carries no user traffic. It watches the platform, turns your config into proxy config, pushes it over xDS and usually signs certificates. If it fails, the proxies keep serving with their last config, and you cannot change anything until it is back."),
    ],
    "deeper": deeper,
    "drop": ["analogy", "mistake", "real_world"],
}

apply(15, "d58", new)
