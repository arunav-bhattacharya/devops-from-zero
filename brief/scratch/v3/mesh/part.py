"""Part 15 extras: intro, recap, flashcards, resources, quiz."""
from common import (BEL_LICENSE, E_LIFE, E_WHAT, G_MESH, I_MODES, L_WHAT, V_AMBIENT, V_ECHO27, V_NANA, V_XDS)


def res(ref, why):
    return {"title": ref["title"], "url": ref["url"], "kind": ref["kind"], "why": why}


INTRO = (
    "Part 10 gave you Services and a Gateway, and Parts 12 to 14 showed you metrics, logs and traces. This part is about "
    "the calls between your services: timeouts, retries, encryption with identity, traffic splits and per-call metrics. "
    "Day 58 builds the intuition with one Envoy proxy that you configure by hand and break on purpose. Day 59 runs Istio, "
    "and Day 60 compares Linkerd, Cilium and Consul and helps you decide whether you need a mesh at all."
)

RECAP = [
    "A service mesh moves timeouts, retries, mTLS, traffic splits and per-call metrics out of app code and into proxies.",
    "In Envoy, listeners accept connections, the HTTP connection manager runs filters, routes pick clusters and clusters pick endpoints.",
    "Health checks probe hosts, outlier detection watches real answers, and circuit breakers fail fast.",
    "A control plane sends Envoy its config over xDS; the admin port shows what each proxy really has.",
    "Istio is istiod plus either a sidecar per Pod or ambient mode: ztunnel per node and waypoints for HTTP.",
    "Workload identity comes from ServiceAccounts as SPIFFE IDs. Go PERMISSIVE, then STRICT, then add AuthorizationPolicies.",
    "Linkerd has a Rust sidecar and automatic mTLS; the project ships edge releases and vendors ship stable ones.",
    "Cilium does L3 and L4 in eBPF, runs Envoy per node for HTTP, and shows flows in Hubble.",
    "GAMMA HTTPRoutes attach to a Service and work across meshes.",
    "Measure what a mesh costs, and skip it while a few services do fine without one.",
]

FLASHCARDS = [
    {"front": "Which five problems between services does a mesh handle?", "back": "Timeouts, retries, encryption with identity (mTLS), traffic splitting and per-call metrics."},
    {"front": "Data plane or control plane: which one carries user traffic?", "back": "The data plane, made of the proxies. The control plane only configures them and signs their certificates."},
    {"front": "Name Envoy's core objects in the order a request meets them.", "back": "Listener, HTTP connection manager with its filters, route, cluster, endpoint."},
    {"front": "What do LDS, RDS, CDS, EDS and SDS send to Envoy?", "back": "Listeners, route tables, clusters, endpoints and secrets (certificates and keys)."},
    {"front": "How does an active health check differ from outlier detection?", "back": "A health check sends its own probe request. Outlier detection watches real answers and ejects hosts that keep failing."},
    {"front": "Why does a two-host Envoy cluster never eject a host with default settings?", "back": "`max_ejection_percent` defaults to 10%, which is less than one of two hosts."},
    {"front": "How does a sidecar catch the app's traffic without code changes?", "back": "iptables rules in the Pod's network send connections to the proxy. Istio uses port 15001 out and 15006 in."},
    {"front": "What is a Kubernetes native sidecar?", "back": "An init container with `restartPolicy: Always`. It starts before the app and stops after it; stable since Kubernetes 1.33."},
    {"front": "In Istio ambient mode, what do ztunnel and a waypoint each do?", "back": "ztunnel, one per node, does mTLS and L4 policy. A waypoint, an Envoy per namespace or service, does HTTP routing and L7 policy."},
    {"front": "Which namespace label joins Istio in each mode?", "back": "Sidecar: `istio-injection=enabled`, then restart the Pods. Ambient: `istio.io/dataplane-mode=ambient`, no restart."},
    {"front": "What is the SPIFFE ID of ServiceAccount `client` in namespace `shop`?", "back": "spiffe://cluster.local/ns/shop/sa/client, with the default trust domain."},
    {"front": "PERMISSIVE or STRICT: which one still accepts plain text?", "back": "PERMISSIVE accepts mTLS and plain text. STRICT accepts only mTLS."},
    {"front": "What happens once an ALLOW AuthorizationPolicy selects a workload?", "back": "Every request that no ALLOW rule matches is refused with 403 `RBAC: access denied`."},
    {"front": "Who ships Linkerd's stable releases?", "back": "Vendors, mainly Buoyant Enterprise for Linkerd. The open source project ships edge releases."},
    {"front": "Where does Cilium handle HTTP features?", "back": "In an Envoy proxy that runs once per node. eBPF in the kernel covers L3 and L4."},
    {"front": "What makes an HTTPRoute a GAMMA route?", "back": "Its parentRef is a Service (`kind: Service`, core group) instead of a Gateway."},
]

RESOURCES = [
    res(E_WHAT, "The Envoy project's own short case for running a proxy next to every service instead of a library in every app."),
    res(E_LIFE, "A step-by-step walk of one request through listeners, filters, routes and clusters, the Day 58 picture in full detail."),
    res(V_XDS, "A conference talk on how xDS works between a control plane and Envoy, for when static config is no longer enough."),
    res(V_NANA, "A quick visual overview of what a service mesh and Istio do, good to watch before Day 59."),
    res(I_MODES, "Istio's own comparison of sidecar and ambient mode, with feature status and latency numbers."),
    res(V_AMBIENT, "A hands-on workshop that installs Istio in ambient mode and adds waypoints step by step."),
    res(L_WHAT, "Linkerd's plain-language explanation of what a service mesh is and when it pays off."),
    res(BEL_LICENSE, "Buoyant's own account of what is open source in Linkerd and what its paid distribution adds."),
    res(G_MESH, "The Gateway API page on GAMMA: routes attached to Services, and producer versus consumer routes."),
    res(V_ECHO27, "Liz Rice and Thomas Graf on how Cilium uses eBPF for a mesh without sidecars."),
]

QUIZ = [
    {
        "q": "Envoy splits traffic 90/10 between two clusters, but over 100 requests you count 84 and 16. What is the most likely explanation?",
        "options": [
            "The weights are broken and must add up to 1000",
            "The cluster is chosen at random per request, so small samples vary",
            "Envoy splits by connection, not by request",
            "Health checks moved traffic to the canary",
        ],
        "answer": 1,
        "why": "Weighted clusters are picked at random for each request, and the shares only settle near 90/10 over many requests.",
    },
    {
        "q": "Which xDS API carries the data that changes most often in a busy Kubernetes cluster?",
        "options": ["LDS", "CDS", "EDS", "SDS"],
        "answer": 2,
        "why": "EDS carries the Pod IPs behind each cluster, which change with every rollout and scaling event.",
    },
    {
        "q": "A Pod in an ambient namespace needs an AuthorizationPolicy that matches HTTP paths. What must exist for it to work?",
        "options": [
            "A sidecar container in that same Pod",
            "A NetworkPolicy that allows port 15008",
            "An Istio Gateway in istio-system",
            "A waypoint that the policy targets",
        ],
        "answer": 3,
        "why": "ztunnel cannot read paths; only a waypoint can enforce HTTP rules, and the policy attaches to it with `targetRefs`.",
    },
    {
        "q": "You switch a namespace to PeerAuthentication STRICT. Which caller breaks?",
        "options": [
            "A Pod in a namespace that is not in the mesh",
            "A meshed Pod in another namespace",
            "A meshed Pod in the same namespace",
            "A meshed Pod that uses the default ServiceAccount",
        ],
        "answer": 0,
        "why": "STRICT refuses plain text, and only callers outside the mesh still send it.",
    },
    {
        "q": "Which command shows whether the connections between Linkerd workloads are encrypted?",
        "options": ["linkerd check --pre", "linkerd install --crds", "linkerd viz edges", "kubectl get pods -o wide"],
        "answer": 2,
        "why": "`linkerd viz edges` lists the connections between workloads with a SECURED column.",
    },
    {
        "q": "An HTTPRoute is attached to Service `orders` with one rule that matches only `/api`. A meshed client calls `/health` on `orders`. What does GAMMA say happens?",
        "options": [
            "The call goes to `orders` as if no route existed",
            "The call is rejected, because it matches no rule",
            "The call goes to the first backend of the route",
            "The mesh retries it until a rule matches",
        ],
        "answer": 1,
        "why": "Once routes are attached to a Service, requests that match none of their rules are rejected.",
    },
    {
        "q": "Which cost of sidecar mode does ambient mode avoid?",
        "options": [
            "Restarting every Pod to upgrade the proxy",
            "Running a control plane",
            "Installing the Gateway API CRDs",
            "Issuing certificates for mTLS",
        ],
        "answer": 0,
        "why": "In ambient mode the proxies run outside the app Pods, so upgrading them does not restart your apps.",
    },
    {
        "q": "Which situation is the strongest reason to skip a mesh for now?",
        "options": [
            "An auditor requires mTLS on every internal call",
            "Thirty services in four languages need the same retry rules",
            "Teams want canaries between internal services every week",
            "Six services, one team, with NetworkPolicies and OpenTelemetry in place",
        ],
        "answer": 3,
        "why": "A few services with segmentation and telemetry already in place get little from a mesh but pay all its costs.",
    },
    {
        "q": "You turn on mesh retries for 5xx answers on every route. Which call does that make risky?",
        "options": [
            "GET /orders/42 to read one order",
            "PUT /orders/42 with the full order",
            "POST /payments that charges a card",
            "DELETE /orders/42 to cancel it",
        ],
        "answer": 2,
        "why": "POST is not idempotent, so a retry after a timeout can charge the card twice unless the API uses idempotency keys.",
        "from": "Part 3",
    },
    {
        "q": "kube-proxy balances per connection. A gRPC client keeps one connection open to a Service with three Pods. What does an L7 mesh proxy change?",
        "options": [
            "Nothing, because the connection still pins one Pod",
            "It balances each request across the Pods",
            "It opens a new TCP connection for every request",
            "It turns the Service into a headless one",
        ],
        "answer": 1,
        "why": "An L7 proxy sees each request on the connection and can send each one to a different endpoint.",
        "from": "Part 10",
    },
]
