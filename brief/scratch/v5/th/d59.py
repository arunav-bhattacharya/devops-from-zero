"""Book-voice rewrite of d59 (Istio: traffic management, mTLS and ambient mode). Writer: th."""
import sys
sys.path.insert(0, "/home/user/devops-from-zero/brief/scratch/v5/th")
from common import apply, load, lesson

OPENING = """Picture the office building from last time, now with a building manager. Each morning the badge office prints every worker a fresh badge with their name and team, good for one day. Door readers check badges instead of faces. One Monday the manager makes the rule strict: no badge, no entry. By ten o'clock the cleaners, the plant service and the courier who brings the morning reports are all stuck on the pavement. Nobody had told them about badges.

It is an easy mistake. Inside the building, every door worked perfectly. The people who got hurt were the ones nobody remembered.

Last time, we set up one receptionist, Envoy, by hand and broke it on purpose. Today Istio becomes the building manager. It writes every receptionist's rules, prints the badges, and lets us decide who may open which door. We'll also make that Monday mistake in the lab, safely.

Before we start, make a guess, and keep it in mind."""

S1 = """Istio is a service mesh built on Envoy, so last lesson already gave you most of its moving parts. Its control plane, the building manager, is one program called istiod. It has three jobs:
- It watches the Kubernetes API and your Istio and Gateway API objects. It turns them into listeners, routes, clusters and endpoints for every proxy, sent over xDS.
- It runs a certificate authority (a CA, the signer of certificates from Day 11). The CA gives every workload a short-lived certificate, valid for 24 hours by default.
- It runs the webhook that injects sidecars into new Pods.

That webhook is a mutating admission webhook, a Kubernetes hook for changing objects before they are stored. The API server, the front door of Kubernetes, sends each new Pod to istiod first, and istiod adds the Envoy container. A Pod is Kubernetes' wrapper around an app's containers. Your Deployment, the object that keeps your Pods running, never mentions the sidecar.

The data plane comes in two modes. One mesh can mix them, but each namespace (a named area of the cluster) should use one.

Sidecar mode is the original design, used since 2017. Every Pod gets an Envoy, and every call passes through two of them, the caller's and the receiver's. Each proxy handles both L4 and L7, so every feature works everywhere. The cost grows with the mesh. Each sidecar is sized for its own Pod's busiest moment, and joining or upgrading means restarting every Pod.

Ambient mode splits the work into two layers, like one guard per floor plus a doorman only for the rooms with special rules. The guard is ztunnel, a proxy written in Rust that runs once per node (machine). It encrypts and authenticates the traffic of every Pod on its node and enforces L4 rules, but never reads HTTP. For HTTP features you add the doorman, a waypoint: an Envoy that runs as its own Deployment, usually one per namespace.

Traffic between ztunnels and waypoints travels in an mTLS tunnel called HBONE, on port 15008. Most calls only need encryption and identity, which are cheap. So you pay for reading HTTP only where you add a waypoint.

Ambient mode became generally available in Istio 1.24, in November 2024. Istio's page comparing the two modes lists it as Stable for a single cluster, and multi-cluster ambient is Beta. Istio 1.31, released in August 2026, is the current version at the time of writing. The comparison page also quotes Istio's latency tests at p90 and p99, the times that 90 and 99 of every 100 calls beat:
- 0.63 to 0.88 ms per call with sidecars.
- 0.16 to 0.20 ms with ztunnel alone.
- 0.40 to 0.50 ms through a waypoint.

Next, we'll install Istio and bring a namespace into the mesh."""

S2 = """The lab runs on kind, a tool that makes a practice Kubernetes cluster inside Docker. On a Mac, `brew install istioctl` gets you istioctl, Istio's command-line tool. Istio's download script works too, and also brings the sample apps. istioctl installs Istio from a profile, a named set of settings:
- `default`: istiod plus an ingress gateway, the starting point for production.
- `demo`: more features and heavy logging, for tutorials only.
- `minimal`: istiod alone. The lab uses it, because the Gateway API creates gateways when you ask for one.
- `ambient`: istiod, ztunnel and the Istio CNI node agent, which sets up rules that send each Pod's traffic to ztunnel.

Install the Gateway API CRDs first, because Istio reads them. A CRD (custom resource definition) teaches Kubernetes a new kind of object. Istio 1.31's docs install Gateway API v1.6.0. Version 1.7.0 is out, and Envoy Gateway from Day 44 brings its own copy, so check which version a cluster already has before you apply another.

Then decide how each namespace joins the mesh. The lab's namespace is `hello-mesh`, with hello-devops and a small `client` Pod that calls it.
- Sidecar mode: `kubectl label namespace hello-mesh istio-injection=enabled`. Since Istio 1.27 the proxy is a native sidecar, an init container that keeps running.
- Ambient mode: `kubectl label namespace hello-mesh istio.io/dataplane-mode=ambient`. ztunnel takes over the running Pods at once, with no restart and no extra container. The CNI node agent adds redirect rules inside each running Pod's network, and the Pod spec never changes. When you need HTTP features, add a waypoint with `istioctl waypoint apply -n hello-mesh --enroll-namespace`.

The naive move in sidecar mode is to add the label and wait. Nothing happens, which answers the guess. The webhook only acts when a Pod is created, so Pods that were already running keep their old spec. Only Pods created after the label get a sidecar, so restart your Deployments.

Never put both labels on one namespace. If you do, sidecar mode wins for those Pods.

The namespace is in the mesh. Next, we'll tell its proxies where to send traffic."""

S3 = """Istio has its own routing objects, older than the Gateway API, and the project says it intends to make the Gateway API its default. For new work, write Gateway API objects. Traffic from outside enters through a Gateway with HTTPRoutes attached (Day 44). Traffic inside the mesh uses an HTTPRoute whose `parentRef` is a Service instead of a Gateway. Day 60 explains that pattern, called GAMMA.

The lab's `httproute-canary.yaml` attaches to the `hello-devops` Service. istiod turns it into Envoy routes in the client's sidecar, which applies them to every call to `http://hello-devops`:
- A request with the header `x-canary: always` goes to the canary, the new version.
- Everything else is split 90 to 10 by weight.
- `timeouts.request: 3s` caps each request.

Older Istio setups use Istio's own objects, and you will meet them at work:
- VirtualService: routing rules for a host, with retries, timeouts, header matches and fault injection.
- DestinationRule: what happens after routing picked a destination. Connection limits, outlier detection, TLS settings and subsets live here. A subset is a named group of Pods by label, such as `version: v2`.

Retries show where the two APIs still differ. The Standard channel of Gateway API v1.6.0 has no retry field, and v1.7.0 added one, so the lab puts retries in the VirtualService. Do not let an HTTPRoute and a VirtualService both route the same Service, because then nobody knows which rules are live. The lab deletes one before it applies the other.

Routes decide where calls go. Next, we'll make some of them fail on purpose."""

S4 = """How does your app behave when a dependency (a service it calls) is slow or failing? Waiting for an outage to find out is expensive. Fault injection causes the failure on purpose, in a share of requests you choose. It is a fire drill for software.

A VirtualService rule can add two kinds of fault:
- A delay holds the request for a while, say 2 seconds, before sending it on.
- An abort answers at once with a status such as 503, without calling the service at all.

Each fault has a `percentage`, so you can hurt 1 request in 5 and leave the others alone. The lab's file only injects faults into requests that carry `x-fault: on`, which keeps normal traffic safe. Istio switches off timeouts and retries on a rule that injects faults. So healthy traffic gets a second rule with a 3-second timeout and two retries. The fault happens in the caller's sidecar, which is exactly where your own timeout and retry code would notice it.

Circuit breaking lives in a DestinationRule, and it maps one to one onto last lesson's Envoy settings:
- `connectionPool.tcp.maxConnections` and `connectionPool.http.http1MaxPendingRequests` become Envoy circuit breakers. Over the limit, the caller gets a 503 at once.
- `outlierDetection.consecutive5xxErrors`, `interval`, `baseEjectionTime` and `maxEjectionPercent` become Envoy outlier detection.

Istio even keeps Envoy's stat names, so the counters you read through the admin port last time still apply.

Next, we'll print the badges: identity and mutual TLS."""

S5 = """Day 11 showed TLS in which only the server proves who it is. In mutual TLS both sides present a certificate, so the server also learns who is calling. Istio gives every workload that certificate automatically, like the badge office printing a fresh badge each morning.

The identity comes from the Pod's ServiceAccount, the identity for programs from Day 46. Every Pod runs as one, `default` unless you name another. Istio writes it as a SPIFFE ID, a standard format for workload names. `spiffe://cluster.local/ns/hello-mesh/sa/client` is ServiceAccount `client` in namespace `hello-mesh`, in the trust domain `cluster.local`. That is why the lab gives each Deployment its own ServiceAccount. Workloads that share one also share an identity.

A sidecar gets its certificate in four steps:
1. The Istio agent next to Envoy creates a private key (the secret half of the certificate) and a signing request.
2. It sends the request to istiod, with the Pod's ServiceAccount token as proof.
3. istiod checks the token and signs a certificate valid for 24 hours.
4. The agent hands key and certificate to Envoy over SDS, the secret API from last lesson, and renews them before they expire.

The short life limits the damage of a stolen key, and nobody rotates certificates by hand. The SPIFFE ID sits inside the certificate. So the receiving proxy learns who is calling from the handshake itself, not from anything the app sent.

PeerAuthentication says what a workload accepts:
- PERMISSIVE, the default, accepts mTLS and plain text. Meshed callers already use mTLS, and callers outside the mesh still work.
- STRICT accepts mTLS only, and plain-text callers are refused.
- DISABLE turns mTLS off. Avoid it.

In PERMISSIVE mode one port takes both. The receiving Envoy looks at the first bytes of each connection, and a TLS handshake is easy to tell from plain text. On the calling side, istiod tells each sidecar which destinations have a proxy, and the sidecar uses mTLS to those by itself.

Now the Monday mistake. In the lab, a Pod in the `outside` namespace has no proxy, and it can call hello-devops until you apply `peerauthentication.yaml`. After that the call fails, and curl exits with code 56: the connection was cut before any HTTP answer arrived. The error looks like a network fault, which is why it is so confusing at work. **Go strict only after every caller has a badge. Start PERMISSIVE, check each caller of the namespace, then switch.**

Next, we'll use those verified badges to decide who may open which door."""

S6 = """With mTLS on, every request arrives with a verified caller identity, and AuthorizationPolicy can use it. A policy has three parts:
- `selector`, or `targetRefs` in ambient mode: the workloads it protects.
- `action`: ALLOW, DENY, AUDIT (log only) or CUSTOM (ask an outside service).
- `rules`: `from` the caller (principals, namespaces, IP ranges) and `to` the operation (methods, paths, ports).

Istio checks CUSTOM policies first, then DENY, then ALLOW. A workload with no policy allows everything. Now picture a team adding one ALLOW policy for a new caller, meaning to let it in. Once any ALLOW policy selects a workload, every request that no ALLOW rule matches is refused with 403 and the text `RBAC: access denied`. So that one friendly rule locks out every other caller of the workload. **An ALLOW policy is also a deny for everyone it does not name.**

The lab has two policies for both app versions:
1. `deny-metrics` refuses `/metrics` to every namespace except `monitoring`. `notNamespaces` reads the caller's namespace from its certificate, so a forged header cannot get around it.
2. `allow-client-get` lets only `cluster.local/ns/hello-mesh/sa/client` in, only with GET, and only on `/`, `/healthz` and `/readyz`. A principal is the SPIFFE ID without `spiffe://`.

In ambient mode, where the policy runs matters. ztunnel sees connections, so it can enforce identity and port rules but not paths or methods. A policy with HTTP rules has to be attached to a waypoint with `targetRefs`. If you write it with a `selector` instead, ztunnel enforces it and, to fail safe, treats it as a DENY. The floor guard cannot read the room list, so it keeps the door shut. The lab's `ambient/authorizationpolicy.yaml` is the waypoint version.

The rules are in place. Next, we'll check that each proxy really received them."""

S7 = """Most Istio problems are config that did not do what you meant. istioctl shows what each proxy really received:
- `istioctl analyze` checks your objects for known mistakes, such as a route to a missing Service. With `--use-kube=false` it checks files, with no cluster.
- `istioctl proxy-status` lists every proxy and whether it has istiod's latest config.
- `istioctl proxy-config listener`, `route`, `cluster`, `endpoint` and `secret` print one part of a proxy's live config, in last lesson's words. `secret` shows the workload certificate and its expiry.
- `istioctl dashboard envoy deployment/client -n hello-mesh` opens that sidecar's Envoy admin page, with the same `/clusters` and `/stats` as last time.
- In ambient mode, `istioctl ztunnel-config workload` shows what ztunnel knows about each Pod.

Every proxy exports Prometheus metrics. The one to start with is `istio_requests_total`, a counter labeled with source, destination and response code. The PromQL from Day 51 works on it unchanged. Kiali reads those metrics and draws a live graph of who calls whom, with error rates on the edges. Istio's sample addons install Prometheus and Kiali in two commands, listed in the lab's README.

Traces need one thing from you. The proxies can create a span for every hop, but a proxy cannot tell which outgoing call belongs to which incoming request inside your app. Your app must copy the trace headers from the request it received onto the requests it sends, the context propagation of Day 57. OpenTelemetry instrumentation does it for you. Without it, Jaeger shows one short trace per hop instead of one trace per user request.

Istio does a lot, and that is also its limit. It is one more system with its own objects, upgrades and certificate authority, and the lab needed 8 GB of memory for Docker just to try it. Not every team needs all of it. The next lesson looks at lighter meshes, and asks whether you need a mesh at all."""

CLOSING = """We started with a strict Monday that left the cleaners on the pavement. Today istiod printed every workload a one-day badge, and the proxies checked those badges in a mutual TLS handshake. The Pod in `outside` was refused the moment we went STRICT. In the lab, run `istioctl proxy-config secret deployment/client -n hello-mesh` and read when the client's badge expires. At work, list every caller of a namespace before you lock it.

Next, we'll meet Linkerd, Cilium and Consul, and answer the question this lesson left open: does your team need a mesh at all?"""

ASIDE = {
    "title": "Why are there two objects called Gateway?",
    "body": "Istio had its own Gateway long before the Gateway API existed. It lives in the `networking.istio.io` group and holds settings for an ingress proxy you deployed yourself. The Gateway API's Gateway is a different object, despite the name, and it can create the proxy for you. In new work, use the Gateway API one. When you read an older setup, check the group on the object's `apiVersion` line to see which one you are looking at.",
    "after": 2,
}

L = lesson(load(15), "d59")
deeper = L["deeper"]["body"].split("\n\nTwo names spelled out")[0]
deeper += ("\n\nTwo names spelled out, and one stat name explained. HBONE stands for HTTP-Based Overlay Network Environment. "
           "SPIFFE stands for the Secure Production Identity Framework for Everyone. Istio's circuit breaking task reads the stat "
           "`upstream_rq_pending_overflow` for a cluster called `outbound|8000||httpbin.default.svc.cluster.local`. "
           "The parts are direction, port, subset and host, in that order.")

new = {
    "goal": "By the end you can explain how istiod, sidecars, ztunnel and waypoints fit together, write Istio and Gateway API objects for a canary, circuit breaking, mTLS and authorization, and debug them with istioctl.",
    "opening": OPENING,
    "guess": (
        "You label a namespace `istio-injection=enabled` while its Pods are already running. What happens to those Pods?",
        "A webhook adds the sidecar when a Pod is created, so running Pods keep their old spec until a restart. Ambient mode's label is different: it works on running Pods, with no restart.",
    ),
    "terms": [
        "Istio's control plane: it turns your config into Envoy config, pushes it over xDS and signs workload certificates.",
        "A webhook that adds the Envoy container to each new Pod in a labeled namespace.",
        "Istio's small proxy that runs once per node in ambient mode. It does mTLS and simple connection rules for every Pod on its node.",
        "An Envoy that Istio runs per namespace or per service in ambient mode, for HTTP features.",
        "A workload's name written as a URI, such as spiffe://cluster.local/ns/hello-mesh/sa/client.",
        "TLS in which both sides show a certificate, so each knows who the other is.",
        "The Istio object that says whether a workload accepts plain text, mTLS, or both.",
        "The Istio object that allows or denies requests by caller identity, namespace, method or path.",
    ],
    "sections": [
        ("One control plane, two kinds of data plane", S1),
        ("Install on kind and join a namespace", S2),
        ("Routing: the Gateway API first, then the Istio APIs you will still meet", S3),
        ("Breaking things on purpose: faults and circuit breakers", S4),
        ("Identity, mutual TLS and a strict Monday", S5),
        ("AuthorizationPolicy: who may call what", S6),
        ("Debugging and observing: istioctl, Prometheus, Kiali and traces", S7),
    ],
    "aside": ASIDE,
    "diagram_caption": "Sidecar mode puts an Envoy in every Pod; ambient mode uses a ztunnel per node and adds a waypoint only for HTTP features.",
    "say": [
        "Start last lesson's lab again. Its `envoy.yaml` already has a fault filter at 0 percent and a runtime layer. That layer holds values the admin port can change while Envoy runs, and the fault filter reads them on every request. Turn faults on while Envoy runs: abort 10% of requests with a 503 and delay 20% by 2 seconds. Envoy answers OK, and `/runtime` shows the new values.",
        "Send 100 requests and keep each status code and total time. Six were aborted and 30 took more than 1.5 seconds. Each request rolls the dice on its own, so your counts will differ, and a few requests get both faults.",
        "The access log explains each odd line. The field after the status code is the response flags: `FI` is an injected abort and `DI` an injected delay. The aborted request never reached a host, so its upstream host at the end is `-`. The delayed one took 2004 ms in total, of which the app spent 3 ms.",
        "Envoy counts every fault it injects. Check these counters whenever a fault test seems to change nothing: maybe the test never ran. Then switch the faults off again.",
        "Now the Istio version. You never write the fault filter yourself there. You write a VirtualService rule, and istiod puts the same Envoy fault settings into the routes of every calling sidecar. This is the fault rule from the lab's `virtualservice-fault.yaml`, and it only hurts requests with the header `x-fault: on`.",
        "Check Istio files before you go near a cluster. On your Mac, `istioctl analyze --use-kube=false *.yaml` runs Istio's own offline checks. The course checked the lab with kubeconform, a file checker, and JSON schemas made from the CRD files of Istio 1.31 and Gateway API v1.6.0. All 20 objects passed, and a one-letter typo in the DestinationRule was caught at once (error trimmed).",
    ],
    "task": (
        [
            "Give Docker Desktop at least 8 GB of memory, create a kind cluster named `mesh`, and install istioctl.",
            "Follow `mesh/istio/README.md` to install the Gateway API CRDs and Istio with the `minimal` profile.",
            "Load `hello-devops:1.0.0` into kind, apply `namespace.yaml` and `apps.yaml`, and confirm with `istioctl proxy-status` that every Pod has a proxy.",
            "Apply the HTTPRoute and count the versions over 200 calls from the client Pod. Then send one call with `x-canary: always`.",
            "From a Pod in the `outside` namespace, call hello-devops before and after you apply `peerauthentication.yaml`.",
            "Apply `authorizationpolicy.yaml`. From the client, check that `/` answers 200 and `/metrics` answers 403.",
            "Delete the HTTPRoute, apply `virtualservice-fault.yaml`, and send 20 calls with and 20 without `x-fault: on`.",
            "Find the fault settings in `istioctl proxy-config route deployment/client -n hello-mesh -o json`, then delete the cluster.",
        ],
        [
            "If `kubectl exec` picks the wrong container, add `-c curl`: the proxy is a second container in the Pod.",
            "If a Pod has no sidecar, it was created before the namespace label. Run `kubectl rollout restart deployment -n hello-mesh`.",
            "A 403 with `RBAC: access denied` comes from the proxy, so the app's logs show nothing for those calls.",
        ],
        "You are done when about 9 in 10 of the client's calls reach version 1.0.0, the Pod in `outside` is refused under STRICT, and `/metrics` answers 403 to the client.",
    ),
    "explain_back": (
        "Explain in 3 to 4 sentences how two workloads in an Istio mesh know who the other is, and how you turn that into a rule. Mention ServiceAccount, SPIFFE ID, PeerAuthentication and AuthorizationPolicy.",
        "Each workload's identity comes from its Kubernetes ServiceAccount, written as a SPIFFE ID such as spiffe://cluster.local/ns/hello-mesh/sa/client. The control plane, istiod, signs a certificate with that ID that lasts 24 hours. The proxies on both sides present their certificates in a mutual TLS handshake. PeerAuthentication decides whether a workload also accepts plain text (PERMISSIVE) or only mTLS (STRICT). AuthorizationPolicy then allows or denies requests by that verified identity, and by namespace, method and path.",
    ),
    "recap": [
        "istiod is the control plane: xDS config, workload certificates and sidecar injection.",
        "Sidecar mode puts Envoy in every Pod; ambient mode uses ztunnel per node for L4 and waypoints for L7, with no Pod restarts. VirtualService on a waypoint is still Alpha.",
        "Write new routes as Gateway API HTTPRoutes; DestinationRules still hold connection limits and outlier detection.",
        "Identity comes from ServiceAccounts as SPIFFE IDs. Go PERMISSIVE, check every caller, then STRICT.",
        "Once an ALLOW policy selects a workload, everything it does not allow gets a 403.",
        "Istio is a big system to run and upgrade; smaller teams may need a lighter mesh, or none.",
    ],
    "closing": CLOSING,
    "check": [
        ("In ambient mode you add an AuthorizationPolicy with a `selector` that allows only `GET /orders`. No waypoint exists. What happens?",
         "ztunnel only sees connections, so a selector policy with HTTP rules fails safe and denies. Attach it to a waypoint with `targetRefs` instead."),
        ("A DestinationRule sets `http1MaxPendingRequests: 1`. A load test fires 20 calls at once from a meshed client. What do many of them get?",
         "Past the pending-request limit, Envoy's circuit breaker fails the call at once with a 503."),
        ("Deployments `billing` and `reports` both run as ServiceAccount `default`. An AuthorizationPolicy allows only billing's principal. What can `reports` do?",
         "The identity is the ServiceAccount, so two workloads that share one are the same principal to Istio."),
    ],
    "interview": [
        ("Sidecar mode or ambient mode: how would you choose?",
         "Ambient mode costs less: one ztunnel per node instead of an Envoy per Pod, no Pod restarts to join, and HTTP processing only where you add a waypoint. Istio's own tests also show lower latency for it. Sidecar mode is older and supports every feature, including multi-cluster at the Stable level, and it gives each workload its own keys. For a new single-cluster mesh I would start in ambient mode with L4 only. Then I would add waypoints where a team needs HTTP features, unless a feature I need is still missing there."),
        ("How does Istio implement mutual TLS between services?",
         "Each workload gets an identity from its ServiceAccount, in SPIFFE format. The Istio agent next to the proxy asks istiod to sign a certificate for that identity, gets one valid for 24 hours, and hands it to Envoy over SDS. The proxies on both sides present certificates and check each other against the mesh's trust root. PeerAuthentication controls whether plain text is still accepted, and AuthorizationPolicy uses the verified identity to allow or deny calls."),
        ("A request through the mesh returns 503. How do you find out whether the proxy or the app produced it?",
         "I check the proxy's access log first. Envoy's response flags tell you when the proxy answered by itself, such as UO for a circuit breaker overflow or UH for no healthy upstream. The commands `istioctl proxy-config cluster` and `endpoint` show whether the destination has healthy endpoints at all, and `istioctl analyze` catches routes to missing Services. If the proxy forwarded the request and the upstream answered 503, the app's own logs show it."),
    ],
    "deeper": deeper,
    "drop": ["analogy", "mistake", "real_world"],
}

apply(15, "d59", new)
