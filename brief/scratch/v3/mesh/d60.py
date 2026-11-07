"""Day 60: Linkerd, Cilium and choosing a mesh (or none)."""
from common import (APPMESH, BEL_FAQ, BEL_LICENSE, C_GAMMA, C_HUBBLE, C_MESH, C_MUTUAL, C_ZTUNNEL, CONSUL, G_FACETS,
                    G_MESH, I_MODES, L_ARCH, L_MTLS, L_RELEASES, L_START, L_WHAT, S, V_ECHO27, V_GAMMA, V_LINKERD, lab)

DIAGRAM = (
    '<svg viewBox="0 0 560 250" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="First ask whether you need a '
    'mesh; if not, keep NetworkPolicy, retries and OpenTelemetry. If yes, adopt in four steps: observe, mTLS in '
    'permissive mode, strict mTLS, then policies">'
    '<rect class="bxg" x="8" y="24" width="120" height="40" rx="10"/>'
    '<text class="tk" x="68" y="49" font-size="13" text-anchor="middle">Need a mesh?</text>'
    '<line class="ln" x1="130" y1="44" x2="176" y2="44" marker-end="url(#ar)"/>'
    '<text class="ts" x="153" y="36" font-size="11" text-anchor="middle">no</text>'
    '<rect class="bx" x="180" y="24" width="112" height="40" rx="10"/>'
    '<text class="t" x="236" y="49" font-size="13" text-anchor="middle">No mesh yet</text>'
    '<text class="ts" x="304" y="49" font-size="11" text-anchor="start">NetworkPolicy, retries, OTel</text>'
    '<line class="ln" x1="60" y1="66" x2="60" y2="136" marker-end="url(#ar)"/>'
    '<text class="ts" x="70" y="104" font-size="11" text-anchor="start">yes</text>'
    '<rect class="bxt" x="8" y="140" width="104" height="40" rx="10"/>'
    '<text class="tk" x="60" y="165" font-size="13" text-anchor="middle">Observe</text>'
    '<line class="ln" x1="114" y1="160" x2="144" y2="160" marker-end="url(#ar)"/>'
    '<rect class="bxt" x="148" y="140" width="112" height="40" rx="10"/>'
    '<text class="tk" x="204" y="165" font-size="13" text-anchor="middle">Permissive</text>'
    '<line class="ln" x1="262" y1="160" x2="292" y2="160" marker-end="url(#ar)"/>'
    '<rect class="bxt" x="296" y="140" width="104" height="40" rx="10"/>'
    '<text class="tk" x="348" y="165" font-size="13" text-anchor="middle">Strict</text>'
    '<line class="ln" x1="402" y1="160" x2="432" y2="160" marker-end="url(#ar)"/>'
    '<rect class="bxo" x="436" y="140" width="104" height="40" rx="10"/>'
    '<text class="tk" x="488" y="165" font-size="13" text-anchor="middle">Policies</text>'
    '<text class="ts" x="60" y="198" font-size="11" text-anchor="middle">metrics only</text>'
    '<text class="ts" x="204" y="198" font-size="11" text-anchor="middle">plain text OK</text>'
    '<text class="ts" x="348" y="198" font-size="11" text-anchor="middle">mTLS only</text>'
    '<text class="ts" x="488" y="198" font-size="11" text-anchor="middle">authz, routes</text>'
    '<text class="ts" x="280" y="232" font-size="11" text-anchor="middle">one namespace at a time, watching the metrics after each step</text>'
    '</svg>'
)

LESSON = {
    "id": "d60",
    "title": "Linkerd, Cilium and choosing a mesh (or none)",
    "minutes": 50,
    "goal": "By the end you can compare Linkerd, Istio, Cilium and Consul, write one GAMMA route that works in more than one mesh, put numbers on what a mesh costs, and decide whether your system needs one.",
    "guess": {
        "q": "Cilium's service mesh is often called sidecar-free. Where does an HTTP retry or a path-based route actually run?",
        "options": [
            "In eBPF programs inside the Linux kernel",
            "In an Envoy proxy that runs once on each node",
            "In the application's own container",
            "In the Kubernetes API server",
        ],
        "answer": 1,
        "why": "eBPF handles L3 and L4 work in the kernel, but HTTP is parsed by Envoy. Cilium runs one Envoy per node, the `cilium-envoy` DaemonSet, for its L7 features.",
    },
    "terms": [
        {"term": "linkerd2-proxy", "plain": "Linkerd's sidecar proxy: a small proxy written in Rust, built only for service mesh work."},
        {"term": "Edge release", "plain": "A frequent Linkerd build from the main branch, named like edge-26.11.1; the open source project ships only these."},
        {"term": "Trust anchor", "plain": "The root certificate a mesh trusts; every workload certificate is signed under it."},
        {"term": "eBPF", "plain": "Small programs that the Linux kernel runs safely, which Cilium uses to handle packets without a user-space proxy."},
        {"term": "Hubble", "plain": "Cilium's tool that records the network flows between Pods so you can watch and search them."},
        {"term": "GAMMA", "plain": "The Gateway API's way to configure a mesh: routes attach to a Service instead of a Gateway."},
        {"term": "Producer route", "plain": "A GAMMA route in the same namespace as its Service; it applies to callers from every namespace."},
    ],
    "sections": [
        {
            "h": "Linkerd: a small proxy and few knobs",
            "body": (
                "Linkerd's site calls it the first service mesh project, and it was the first mesh to graduate in the CNCF. "
                "Its goal is to do the common things with very little configuration.\n\n"
                "The control plane has three parts:\n"
                "- The destination service tells each proxy where a Service's endpoints are and which policies apply.\n"
                "- The identity service is a certificate authority. It signs a certificate for each proxy, bound to the Pod's ServiceAccount, valid for 24 hours and rotated automatically.\n"
                "- The proxy injector adds the proxy to new Pods in namespaces annotated `linkerd.io/inject: enabled`.\n\n"
                "The data plane is linkerd2-proxy, a micro-proxy written in Rust; Linkerd does not use Envoy. It runs as a "
                "sidecar in every Pod, and since Linkerd 2.20 it is a native sidecar by default. An init container, or "
                "Linkerd's CNI plugin, writes the iptables rules that send the Pod's traffic through it.\n\n"
                "What you get before writing a single policy:\n"
                "- mTLS for all TCP traffic between meshed Pods, from the moment they are meshed.\n"
                "- Golden metrics for every workload: success rate, requests per second and latency.\n"
                "- Load balancing per request, sending each one to the fastest endpoint by a moving average of latency. kube-proxy only balances connections (Day 41).\n\n"
                "The viz extension adds the tools to see it:\n"
                "- `linkerd viz stat-outbound` prints a workload's calls by route and backend.\n"
                "- `linkerd viz edges` shows which connections are secured.\n"
                "- `linkerd viz tap` streams live requests, and `linkerd viz dashboard` opens a web UI.\n\n"
                "Linkerd has stayed with sidecars: every meshed Pod has its own proxy."
            ),
            "refs": [L_ARCH, L_MTLS, V_LINKERD],
        },
        {
            "h": "Linkerd's releases and license today",
            "body": (
                "The Linkerd code is open source under the Apache 2.0 license. What changed in February 2024 is who builds "
                "the releases:\n"
                "- The open source project publishes edge releases about once a week, named `edge-YY.M.N`. `edge-26.11.1` is the first edge release of November 2026. The project calls edge releases production ready and marks one as not recommended when a bug turns up.\n"
                "- The project still announces versions such as 2.20 (June 2026), but it no longer publishes stable builds of them. Those come from vendors.\n"
                "- Buoyant, the company that created Linkerd, sells Buoyant Enterprise for Linkerd (BEL). Its FAQ says companies with fewer than 50 employees may run it for free, in production too. Larger companies may evaluate it outside production and pay to run it in production.\n\n"
                "For you as a learner nothing changes: the getting started guide installs the latest edge release, and so "
                "does the lab. At work, somebody has to choose between following edge releases and reading their notes every "
                "week, or paying for a stable channel with support. Make that choice before the first install, because "
                "swapping meshes later is a project of its own.\n\n"
                "The install is short, and `linkerd check` guards each step:\n"
                "1. `linkerd check --pre` checks the cluster.\n"
                "2. You install the Gateway API CRDs yourself. Linkerd 2.20 supports Gateway API 1.2.1 to 1.5.1.\n"
                "3. `linkerd install --crds | kubectl apply -f -` adds Linkerd's own CRDs.\n"
                "4. `linkerd install | kubectl apply -f -` installs the control plane, and `linkerd check` waits until it is healthy.\n\n"
                "One operational detail matters more than the rest. The trust anchor that `linkerd install` creates, the root "
                "certificate of the mesh, expires after 365 days, and rotating it is real work. For anything that outlives a "
                "lab, create your own anchor with a longer life and write down when it expires."
            ),
            "refs": [L_RELEASES, BEL_FAQ, BEL_LICENSE],
        },
        {
            "h": "Cilium: the mesh inside the network plugin",
            "body": (
                "Day 41 named Cilium as a network plugin (CNI) that can replace kube-proxy. Cilium does its work with eBPF: "
                "small programs that the Linux kernel runs safely as packets arrive, with no trip through a user-space "
                "proxy. Since Cilium already sits on every packet, adding mesh features to it is a short step.\n\n"
                "Here is what Cilium does where:\n"
                "- In the kernel, with eBPF: Pod networking, Service load balancing, and network policy based on an identity derived from each Pod's labels.\n"
                "- In Envoy, one per node (the `cilium-envoy` DaemonSet): anything that needs HTTP, such as HTTP-aware policy, the Gateway API, GAMMA routes and L7 load balancing.\n"
                "- Between nodes, encryption with WireGuard or IPsec. That protects the wire, but it is not mTLS between workload identities.\n\n"
                "Workload mTLS is where Cilium is still moving. Its first design, mutual authentication based on SPIFFE, is "
                "Beta and deprecated in Cilium 1.20, and the docs for the next release have removed it. The replacement runs "
                "Istio's ztunnel on each node and is also Beta. If identity-based mTLS is your main reason for a mesh, check "
                "its status before you pick Cilium for it.\n\n"
                "Hubble is Cilium's observability layer. It records every flow the eBPF programs see. Each flow has the "
                "source and destination identity and a verdict, forwarded or dropped, plus HTTP details for traffic through Envoy. "
                "The command `hubble observe` streams flows in the terminal, and the Hubble UI draws a service map. When a NetworkPolicy "
                "drops a packet, Hubble names the Pods involved and the reason, which beats guessing.\n\n"
                "Cilium's GAMMA support has one limit to know about. It supports only producer routes, so an HTTPRoute must "
                "live in the same namespace as the Service it attaches to."
            ),
            "refs": [C_MESH, C_HUBBLE, V_ECHO27],
        },
        {
            "h": "Consul, and a mesh that was retired",
            "body": (
                "Consul is HashiCorp's service discovery tool, and its service mesh uses Envoy sidecars. On Kubernetes, the "
                "Helm chart installs Consul with the mesh switched on. A component called Consul Dataplane manages each "
                "Envoy, and the Consul servers hand the proxies their config over xDS. Consul's strength is reach outside "
                "Kubernetes: one mesh can include services on VMs and in several data centers. That makes it a natural pick "
                "for a company that already runs Consul for service discovery. Since August 2023 Consul has been "
                "source-available under the Business Source License, so it is no longer open source.\n\n"
                "AWS App Mesh, Amazon's managed mesh built on Envoy, is gone. AWS stopped taking new customers in September "
                "2024 and ended support on September 30, 2026, after which the console and its resources are no longer "
                "available. If you find App Mesh in an old design document, read it as history, and look at ECS Service "
                "Connect for ECS workloads, which is where AWS's migration guide points."
            ),
            "refs": [CONSUL, APPMESH],
        },
        {
            "h": "GAMMA: one route for many meshes",
            "body": (
                "Every mesh used to have its own routing objects: VirtualService in Istio, ServiceProfile and TrafficSplit "
                "in Linkerd, CiliumEnvoyConfig in Cilium. Moving to another mesh meant rewriting every route. **GAMMA**, short for "
                "Gateway API for Mesh Management and Administration, is the fix. It started in 2022, and its routes have been "
                "in the Standard channel since Gateway API 1.1.\n\n"
                "The idea is small. On Day 44 an HTTPRoute had a Gateway as its parent, so its rules applied to traffic "
                "entering through that Gateway. In GAMMA the parent is a Service:\n"
                "- `parentRefs` names the Service with `kind: Service` and `group: \"\"`, the core API group. Linkerd's docs and the GAMMA page write `group: core` instead; Linkerd accepts both.\n"
                "- The rules apply to every meshed call to that Service, wherever the caller runs. The caller's proxy does the work, or the waypoint in Istio's ambient mode.\n"
                "- Once a route is attached to a Service, requests that match none of its rules are rejected. A last rule with no `matches` catches everything else.\n\n"
                "Where the route lives matters. A producer route sits in the Service's own namespace and applies to callers "
                "from every namespace, so the team that owns the Service writes it. A consumer route sits in the caller's "
                "namespace and changes only that caller's traffic, for example a shorter timeout for one client.\n\n"
                "The lab shows the payoff. `mesh/linkerd/httproute-canary.yaml` has exactly the spec of Day 59's Istio route. "
                "Only the annotations differ, because Linkerd reads retries from annotations. The meshes still support "
                "different Gateway API versions: Istio 1.31's docs install 1.6.0, while Linkerd 2.20 stops at 1.5.1. So use "
                "fields that exist in the oldest version you need, and check the CRD version a cluster has before you rely on "
                "a field."
            ),
            "refs": [G_MESH, C_GAMMA, V_GAMMA],
        },
        {
            "h": "What a mesh costs",
            "body": (
                "A mesh is not free, and the bill has five lines:\n"
                "- Latency. Every proxy adds a hop. In the worked example, one Envoy hop on the test machine added about 0.6 ms to the median call. A sidecar mesh puts two proxies on each call, one at each end.\n"
                "- CPU and memory. The lab's idle Envoy, with a tiny config, held about 64 MB of memory. In sidecar mode you pay that for every Pod, and a sidecar's config grows with the mesh unless you limit what each proxy is told about.\n"
                "- Upgrades. The control plane and every proxy need upgrading, in a supported order. In sidecar mode a new proxy version means restarting every Pod.\n"
                "- Debugging. A failed call has more places to fail. A 503 can come from the app, the caller's proxy, a waypoint or the receiver's proxy, and on-call engineers must know how to tell which.\n"
                "- People. Somebody owns the certificates and the trust anchor, reads the release notes, and is the expert when the mesh is the suspect.\n\n"
                "Istio publishes its own latency numbers on its sidecar-or-ambient page. It measured 0.63 to 0.88 ms per call "
                "for sidecars, and 0.16 to 0.20 ms for ambient mode without a waypoint. Numbers from someone else's test bench "
                "are a starting point. The worked example shows how to measure your own in five minutes, and your own are the "
                "ones to put in a decision document."
            ),
            "refs": [I_MODES],
        },
        {
            "h": "When you do not need a mesh, and how to adopt one",
            "body": (
                "For a handful of services owned by one team, I would not start with a mesh. Tools you already know cover "
                "most of Day 58's list:\n"
                "- NetworkPolicy (Day 41) decides who may talk to whom.\n"
                "- A shared client library sets timeouts and retries, such as Resilience4j in your Kotlin services.\n"
                "- One Gateway (Day 44) handles TLS and routing at the edge, including canaries for traffic from users.\n"
                "- OpenTelemetry (Day 57) and Prometheus (Day 50) give per-call metrics and traces.\n\n"
                "The answer changes as services and teams multiply, when services are written in many languages, or when a "
                "customer or auditor asks for encryption and identity on every internal call. At that point one mesh is "
                "cheaper than the same work done in every repository. The lab's `CHECKLIST.md` turns this into questions "
                "you can answer for a real system.\n\n"
                "If you adopt one, go one namespace at a time, in this order:\n"
                "1. Observe. Mesh a namespace and only watch the golden metrics. You will find calls nobody knew about.\n"
                "2. mTLS in permissive mode, so meshed callers encrypt and everyone else still works.\n"
                "3. Strict mTLS, once the metrics show that every caller is meshed.\n"
                "4. Authorization policies, starting with the services that hold sensitive data.\n"
                "5. Traffic policies last: retries, timeouts, canaries and fault tests.\n\n"
                "Multi-cluster is its own project. Istio, Linkerd and Cilium can all connect clusters, so a call can fail "
                "over to another region. Each needs certificates that all the clusters trust and network paths between them. "
                "Start it only after one cluster runs smoothly."
            ),
            "refs": [L_WHAT],
        },
    ],
    "analogy": (
        "Choosing a mesh is like choosing between central air conditioning and a fan in each room. In a small flat, fans "
        "are cheaper and you understand every one of them. In a forty-floor tower, the central system wins, even though "
        "it needs a plant room, a maintenance contract and an engineer on call. Air conditioning is all or nothing once "
        "the ducts are in. A mesh can be switched on one floor at a time, in permissive mode, with the old fans still "
        "running."
    ),
    "diagram": DIAGRAM,
    "diagram_caption": "Decide first; if a mesh is worth it, switch it on one layer at a time.",
    "worked": {
        "title": "Measure one proxy hop, then decide",
        "steps": [
            {
                "say": "Start the Day 58 lab. Compose puts its containers on a network called `mesh-envoy_default`, so a throwaway curl container on that network can call the app directly and through Envoy. It sends 300 requests to each address and prints the 150th and 270th time after sorting: the median and the 90th percentile, in seconds.",
                "code": (
                    "$ docker compose up -d\n"
                    "$ docker run --rm --network mesh-envoy_default curlimages/curl:8.22.0 sh -c '\n"
                    "for url in http://v1a:8000/healthz http://envoy:10000/healthz; do\n"
                    "  for i in $(seq 1 300); do curl -s -o /dev/null -w \"%{time_total}\\n\" $url; done | sort -n | sed -n \"150p;270p\" | tr \"\\n\" \" \"; echo $url\n"
                    "done'\n"
                    "0.001464 0.001886 http://v1a:8000/healthz\n"
                    "0.002088 0.002539 http://envoy:10000/healthz"
                ),
                "lang": "console",
            },
            {
                "say": "Read the numbers. Through Envoy the median went from 1.46 ms to 2.09 ms, about 0.6 ms more, and the 90th percentile moved by about as much. Each curl opens a new connection, so connection setup is included. A sidecar mesh puts two such hops on every call. Your laptop will give other numbers, which is exactly why you measure.",
            },
            {
                "say": "Now memory. The admin port reports what Envoy has allocated, and `/proc` shows what the whole process holds in RAM. This Envoy uses about 7 MB for its config and state, and about 64 MB in total once the program itself is counted.",
                "code": (
                    "$ curl -s localhost:9901/memory | jq '{allocated, heap_size}'\n"
                    "{\n"
                    "  \"allocated\": \"7169536\",\n"
                    "  \"heap_size\": \"12582912\"\n"
                    "}\n"
                    "$ docker compose exec envoy grep VmRSS /proc/1/status\n"
                    "VmRSS:\t   64184 kB"
                ),
                "lang": "console",
            },
            {
                "say": "Turn the measurement into a rough budget for a made-up payments product: 8 services with 3 Pods each. With a sidecar per Pod at about 64 MB, the proxies need about 1.5 GB before they carry any traffic, and every call crosses two of them. In ambient mode the count is one ztunnel per node instead of one proxy per Pod. These are estimates from one small proxy, so treat them as a first guess.",
                "code": (
                    "$ echo \"$(( 8 * 3 )) Pods x 64 MB = $(( 8 * 3 * 64 )) MB of sidecars\"\n"
                    "24 Pods x 64 MB = 1536 MB of sidecars"
                ),
                "lang": "console",
            },
            {
                "say": "Then answer section 1 of the lab's checklist for the same product. It has one team, Kotlin and Python, NetworkPolicies, one Gateway and OpenTelemetry already, and no auditor asking for mTLS. Every box is ticked, so the answer is no mesh yet, with a note to look again when a second team or a compliance rule arrives. Stop the lab with `docker compose down`.",
                "code": (
                    "$ sed -n '9,16p' ../linkerd/CHECKLIST.md\n"
                    "- [ ] You run fewer than about ten services, owned by one or two teams.\n"
                    "- [ ] Most services are written in one or two languages, so a shared client library\n"
                    "      (for example Resilience4j on the JVM) can do retries and timeouts.\n"
                    "- [ ] NetworkPolicies (Day 41) already limit which Pods may talk to which.\n"
                    "- [ ] One Gateway (Day 44) handles TLS and routing for traffic from outside.\n"
                    "- [ ] OpenTelemetry (Day 57) and Prometheus (Day 50) already show you per-service errors\n"
                    "      and latency.\n"
                    "- [ ] No auditor or customer requires encryption and identity on every internal call."
                ),
                "lang": "console",
            },
        ],
    },
    "code": [
        {"lang": "yaml", "title": "mesh/linkerd/namespace.yaml", "src": lab("linkerd/namespace.yaml"), "run": "kubectl apply -f namespace.yaml -f ../istio/apps.yaml"},
        {"lang": "yaml", "title": "mesh/linkerd/httproute-canary.yaml", "src": lab("linkerd/httproute-canary.yaml"), "run": "kubectl apply -f httproute-canary.yaml && linkerd viz -n hello-mesh stat-outbound deploy/client"},
        {"lang": "text", "title": "mesh/linkerd/CHECKLIST.md", "src": lab("linkerd/CHECKLIST.md"), "run": "open mesh/linkerd/CHECKLIST.md"},
    ],
    "commands": [
        {"cmd": "curl --proto '=https' --tlsv1.2 -sSfL https://run.linkerd.io/install-edge | sh", "what": "Install the latest edge release of the Linkerd CLI into ~/.linkerd2/bin."},
        {"cmd": "linkerd check --pre", "what": "Check that the cluster can run Linkerd before you install it."},
        {"cmd": "linkerd install --crds | kubectl apply -f -", "what": "Install Linkerd's own CRDs."},
        {"cmd": "linkerd install | kubectl apply -f -", "what": "Install the Linkerd control plane."},
        {"cmd": "linkerd check", "what": "Wait until Linkerd is healthy and print what is wrong if it is not."},
        {"cmd": "linkerd viz install | kubectl apply -f -", "what": "Install the viz extension: metrics, tap and the dashboard."},
        {"cmd": "linkerd -n hello-mesh check --proxy", "what": "Check the proxies of the meshed Pods in one namespace."},
        {"cmd": "linkerd viz -n hello-mesh edges deployment", "what": "Show the connections between workloads and whether each is secured with mTLS."},
        {"cmd": "linkerd viz -n hello-mesh stat-outbound deploy/client", "what": "Show one workload's outgoing calls by route and backend, with success rate and latency."},
        {"cmd": "linkerd viz tap -n hello-mesh deploy/hello-devops", "what": "Stream live requests to a workload as they happen."},
        {"cmd": "linkerd viz dashboard", "what": "Open the Linkerd dashboard in your browser."},
        {"cmd": "kubectl get crds/httproutes.gateway.networking.k8s.io -o \"jsonpath={.metadata.annotations.gateway\\.networking\\.k8s\\.io/bundle-version}\"", "what": "Print the Gateway API version installed in the cluster."},
        {"cmd": "brew install cilium-cli hubble", "what": "Install the Cilium and Hubble CLIs, for the optional Cilium experiment."},
        {"cmd": "hubble observe -P --verdict DROPPED", "what": "Stream the network flows that Cilium dropped, with a port-forward opened for you."},
    ],
    "mistake": (
        "Installing a mesh to fix a problem it cannot fix is an expensive way to learn what a mesh does. A mesh will not speed up a slow database query or "
        "stop an app from crashing on bad input; it only wraps proxies around the slow call. Write down the two or three "
        "problems you expect it to solve, measure them before and after, and take it out again if the numbers do not move."
    ),
    "real_world": (
        "An auditor asks a payments company to encrypt every internal call, and the request lands on the platform team. "
        "They check what already exists, find NetworkPolicies and OpenTelemetry in place, and adopt Linkerd for mTLS and "
        "golden metrics only, with no traffic rules at first. When canaries between services become routine a year later, "
        "they add HTTPRoutes in the GAMMA form, so the routes would survive a move to another mesh."
    ),
    "task": {
        "title": "Mesh the same apps with Linkerd",
        "steps": [
            "Create a new kind cluster named `linkerd`, separate from the Istio one, and install the Linkerd CLI with the edge install script.",
            "Install the Gateway API CRDs v1.5.1, then Linkerd's CRDs and control plane, running `linkerd check` after each step.",
            "Install the viz extension, load `hello-devops:1.0.0` into kind, and apply `mesh/linkerd/namespace.yaml` and `mesh/istio/apps.yaml`.",
            "Send 50 calls from the client Pod, then confirm with `linkerd viz -n hello-mesh edges deployment` that the connections are secured.",
            "Apply `mesh/linkerd/httproute-canary.yaml`, count the versions over 200 calls, and compare with your Istio result from Day 59.",
            "Run `linkerd viz -n hello-mesh stat-outbound deploy/client` and find the two backends and their request rates.",
            "Diff the Linkerd and Istio route files and write down which lines are Linkerd-only, and why.",
            "Fill in `CHECKLIST.md` for a system you know from work, then delete the cluster.",
        ],
        "hints": [
            "If `linkerd check --pre` fails, it prints a link with hints next to the failed check. Fix that one first.",
            "The Commands list has a `kubectl get crds` line that prints which Gateway API version a cluster has.",
            "Calls through `kubectl port-forward` skip the client's proxy, so the route does not apply to them. Call from the client Pod.",
        ],
        "done_when": "You are done when `linkerd viz edges` shows the connections between your Pods as secured and about 9 in 10 calls from the client reach version 1.0.0.",
    },
    "explain_back": {
        "prompt": "Explain in 3 to 4 sentences when you would add a service mesh and which one you would try first. Mention cost, mTLS and GAMMA.",
        "answer": (
            "I would add a mesh when many services in several languages need the same mTLS, metrics and traffic rules. An "
            "auditor who requires encryption and identity on every internal call is another good reason. For a few services, NetworkPolicy, "
            "client-side retries, one Gateway and OpenTelemetry are cheaper. Every mesh costs latency per hop, memory per "
            "proxy, upgrades and people, so I would measure those first. I would try Linkerd for mTLS and golden metrics, or "
            "Istio in ambient mode for a wider feature set, and write routes as GAMMA HTTPRoutes so they move with me."
        ),
    },
    "recap": [
        "Linkerd uses its own Rust sidecar proxy and gives mTLS and golden metrics with almost no config.",
        "The Linkerd project ships edge releases; stable releases come from vendors such as Buoyant, free under 50 employees.",
        "Cilium handles L3 and L4 in eBPF and runs one Envoy per node for HTTP; its workload mTLS is still Beta.",
        "GAMMA attaches HTTPRoutes to a Service, so one route file works in Istio, Linkerd and Cilium.",
        "A mesh costs latency, memory, upgrades, debugging time and people. Measure before you decide.",
        "Adopt in steps: observe, permissive mTLS, strict mTLS, authorization, then traffic rules.",
    ],
    "check": [
        {
            "q": "Your cluster runs Cilium as its CNI. A team wants a 95/5 canary between two internal services. Which object is the most portable way to write it?",
            "options": [
                "A CiliumEnvoyConfig with weighted clusters",
                "An Istio VirtualService with two destinations",
                "An HTTPRoute whose parentRef is the Service",
                "A NetworkPolicy with two ingress rules",
            ],
            "answer": 2,
            "why": "A GAMMA HTTPRoute works in Cilium today and in Istio and Linkerd too.",
        },
        {
            "q": "A team installs Linkerd with the default `linkerd install` and never touches its certificates. What breaks first, a year later?",
            "options": [
                "The Gateway API CRDs expire",
                "The default trust anchor and issuer expire",
                "The edge release stops receiving traffic",
                "The proxies run out of memory",
            ],
            "answer": 1,
            "why": "The default trust anchor and issuer certificate last a year; without rotation, the proxies can no longer get valid certificates.",
        },
        {
            "q": "Which situation is the weakest reason to add a service mesh?",
            "options": [
                "One slow SQL query makes the checkout page slow",
                "An auditor requires authenticated, encrypted calls everywhere",
                "Forty services in five languages need the same retry rules",
                "Every team wants per-route success rates without code",
            ],
            "answer": 0,
            "why": "A mesh can show you the slow call, but it cannot make the query faster.",
        },
    ],
    "interview": [
        {
            "q": "How do Istio, Linkerd and Cilium differ as service meshes?",
            "a": (
                "Istio uses Envoy, either as a sidecar in every Pod or, in ambient mode, as an optional waypoint behind a "
                "per-node ztunnel, and it has the widest feature set. Linkerd uses its own small Rust sidecar and focuses on "
                "mTLS, golden metrics and reliability with very little configuration. Cilium builds the mesh into its network "
                "plugin: eBPF in the kernel for L3 and L4, one Envoy per node for HTTP, and Hubble for flow visibility. Its "
                "workload mTLS is still Beta. All three accept Gateway API routes, which makes the routing layer portable."
            ),
        },
        {
            "q": "When would you not use a service mesh?",
            "a": (
                "With only a few services and teams, a shared client library, NetworkPolicies, an ingress Gateway and "
                "OpenTelemetry cover retries, segmentation, edge TLS and visibility for less. A mesh adds latency to every "
                "call, memory for every proxy, upgrades and one more system to debug. I would also wait when nobody can own it, "
                "because certificates and upgrades need a named owner. I revisit the decision when the number of services, "
                "languages or compliance demands grows."
            ),
        },
        {
            "q": "How would you roll out a mesh in an existing cluster?",
            "a": (
                "Namespace by namespace, in layers. First I mesh one namespace and use only the metrics, which usually shows "
                "dependencies nobody knew about. Then I turn on mTLS in permissive mode, check that every caller is meshed, and "
                "switch to strict. Authorization policies come next and traffic policies such as retries and canaries last. At "
                "each step I keep a way back, such as removing the namespace label, and I watch the error rates."
            ),
        },
    ],
    "deeper": {
        "minutes": 15,
        "body": (
            "If you want to see the eBPF side for yourself, Cilium runs on kind as long as kind does not install its own "
            "network plugin. This is outside the graded lab, and none of it was run in the course's test environment, so "
            "follow the Cilium docs when a step has changed:\n"
            "1. Create a kind cluster from a config that sets `disableDefaultCNI: true` under `networking`. Its nodes stay NotReady until Cilium is installed, which is expected.\n"
            "2. Install the CLIs with `brew install cilium-cli hubble`.\n"
            "3. Run `cilium install`, then `cilium status --wait`.\n"
            "4. Turn on Hubble with `cilium hubble enable`, and check it with `hubble status -P`. The `-P` flag opens a port-forward to Hubble for you.\n"
            "5. Deploy `mesh/istio/apps.yaml`, add a deny-all NetworkPolicy like Day 41's to its namespace, and run `hubble observe -P --verdict DROPPED`.\n\n"
            "Each dropped flow shows source and destination with their Cilium identities and the reason. Remove the policy "
            "and watch the same flows turn into FORWARDED.\n\n"
            "Why bother if you are not choosing Cilium? Because Hubble shows the layer under every mesh. Istio's ztunnel "
            "and Linkerd's proxy both ride on the network plugin, and when a call fails before any proxy sees it, the "
            "network plugin is where you look. On a cluster that already runs Cilium, Hubble plus NetworkPolicies may be "
            "all the visibility and segmentation you need, which is the no-mesh answer from today's checklist.\n\n"
            "Two cautions from the docs. GAMMA in Cilium needs kube-proxy replacement turned on, so a default install may "
            "not be enough for HTTPRoutes; read the [GAMMA page](https://docs.cilium.io/en/stable/network/servicemesh/"
            "gateway-api/gamma/) first. And if you ever run Linkerd on top of Cilium, read Linkerd's cluster configuration "
            "page. Cilium's socket-level load balancing can bypass part of Linkerd's routing, and the page lists the Cilium "
            "setting to change.\n\n"
            "On workload mTLS, read the status line at the top of each page before you plan anything. The [mutual "
            "authentication page](https://docs.cilium.io/en/stable/network/servicemesh/mutual-authentication/"
            "mutual-authentication/) for 1.20 says Beta, and so does the newer [ztunnel encryption page](https://docs.cilium.io/"
            "en/latest/security/network/encryption-ztunnel/)."
        ),
    },
    "sources": [
        S("Linkerd: getting started", L_START["url"]),
        S("Linkerd: releases and versions", L_RELEASES["url"]),
        S("Cilium: service mesh", C_MESH["url"]),
        S("Gateway API for service mesh (GAMMA)", G_MESH["url"]),
    ],
}

_unused = (C_MUTUAL, C_ZTUNNEL, G_FACETS)
