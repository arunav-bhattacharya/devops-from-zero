"""Book-voice rewrite of d60 (Linkerd, Cilium and choosing a mesh (or none)). Writer: th."""
import sys
sys.path.insert(0, "/home/user/devops-from-zero/brief/scratch/v5/th")
from common import apply, load, lesson

OPENING = """Picture a small bakery with three people in the back and one door. A salesman visits with a brochure: badge readers on every door, a guard on every floor, a control room that watches it all. It is a fine system. The office tower down the street runs on it, and its managers would never go back. But the bakery has one door, and everyone inside knows everyone else.

Saying yes is tempting. The brochure is full of real problems, and the tower's managers really are happy. What the brochure leaves out is the monthly bill, and the person who has to look after it all.

Last time, Istio printed badges and checked them at every door. Today we meet three other meshes, write one route that works in more than one of them, and measure what one proxy costs. Then we ask the bakery's question about our own system: do we need any of this?

Before we start, make a guess, and keep it in mind."""

S1 = """Linkerd's site calls it the first service mesh project, and it was the first mesh to graduate in the CNCF, the non-profit foundation that looks after Kubernetes. Its goal is to do the common things with very little configuration. If Istio is the tower's full security system, Linkerd is a good lock and a doorbell camera that work out of the box.

The control plane has three parts:
- The destination service tells each proxy where a Service's endpoints are and which policies apply.
- The identity service is a certificate authority. It signs a certificate for each proxy, bound to the Pod's ServiceAccount, valid for 24 hours and rotated automatically.
- The proxy injector is a mutating webhook, like Istio's (Day 59). It adds the proxy to new Pods in namespaces annotated `linkerd.io/inject: enabled`.

The data plane is linkerd2-proxy, a micro-proxy written in Rust; Linkerd does not use Envoy. It runs as a sidecar in every Pod (Kubernetes' wrapper around an app's containers). Since Linkerd 2.20 it is a native sidecar by default. An init container, or Linkerd's CNI plugin, writes the iptables rules that send the Pod's traffic through it.

What you get before writing a single policy:
- mTLS for all TCP traffic between meshed Pods, from the moment they are meshed.
- Golden metrics for every workload: success rate, requests per second and latency, much like Day 49's golden signals.
- Load balancing per request, toward the fastest endpoints by a moving average of latency.

That last point matters more than it looks. Day 41's kube-proxy balances only connections. Now take gRPC, a fast way for programs to call each other. A gRPC client keeps one connection open for a long time, so all its calls stay on one Pod. Linkerd spreads the calls themselves.

The viz extension adds the tools to see it:
- `linkerd viz stat-outbound` prints a workload's calls by route and backend.
- `linkerd viz edges` shows which connections are secured.
- `linkerd viz tap` streams live requests, and `linkerd viz dashboard` opens a web UI.

Linkerd has stayed with sidecars: every meshed Pod has its own proxy.

Next, we'll look at who builds Linkerd's releases, because it changes what "free" means."""

S2 = """The Linkerd code is open source under the Apache 2.0 license, the legal terms that let anyone use and change it. What changed in February 2024 is who builds the releases:
- The open source project publishes edge releases about once a week, named `edge-YY.M.N`. `edge-26.11.1` is the first edge release of November 2026. The project calls edge releases production ready and marks one as not recommended when a bug turns up.
- The project still announces versions such as 2.20 (June 2026), but it no longer publishes stable builds of them. Those come from vendors.
- Buoyant, the company that created Linkerd, sells Buoyant Enterprise for Linkerd (BEL). Its FAQ says companies with fewer than 50 employees may run it for free, in production too. Larger companies may evaluate it outside production and pay to run it in production.

For you as a learner nothing changes: the getting started guide installs the latest edge release, and so does the lab. At work, somebody has to choose. One way is to follow edge releases and read their notes every week. The other is to pay for a stable channel with support. Make that choice before the first install, because swapping meshes later is a project of its own.

The install is short, and `linkerd check` guards each step:
1. `linkerd check --pre` checks the cluster.
2. You install the Gateway API CRDs yourself. Linkerd 2.20 supports Gateway API 1.2.1 to 1.5.1.
3. `linkerd install --crds | kubectl apply -f -` adds Linkerd's own CRDs.
4. `linkerd install | kubectl apply -f -` installs the control plane, and `linkerd check` waits until it is healthy.

Now the trap in the easy path. The trust anchor that `linkerd install` creates, the root certificate of the mesh, expires after 365 days. A team that takes the defaults and never looks again has a mesh that breaks a year later. Linkerd's docs call a mesh with expired certificates invalid and give it a separate recovery guide.

Rotating the anchor in time is work too. Every proxy has to trust the old and the new anchor side by side for a while, which takes several steps and Pod restarts. For anything that outlives a lab, create your own anchor with a longer life. **A certificate you did not choose still expires. Write down the date.**

Next, we'll meet a mesh that lives inside the network itself."""

S3 = """Day 41 named Cilium as a network plugin (CNI) that can replace kube-proxy. Cilium does its work with eBPF: small programs that the Linux kernel, the core of the operating system, runs safely as packets arrive. Nothing has to travel up to a separate proxy program. Since Cilium already sits on every packet, adding mesh features to it is a short step.

Here is what Cilium does where:
- In the kernel, with eBPF: Pod networking, Service load balancing, and network policy based on an identity taken from each Pod's labels.
- In Envoy, one per node (the `cilium-envoy` DaemonSet): anything that needs HTTP, such as HTTP-aware policy, the Gateway API, GAMMA routes and L7 load balancing.
- Between nodes: encryption with WireGuard or IPsec, two standard ways to encrypt traffic between machines. That protects the wire, but it is not mTLS between workload identities.

The second line answers the guess. "Sidecar-free" does not mean "Envoy-free": an HTTP retry or a path-based route runs in that per-node Envoy.

Node encryption tells the receiver which node a packet came from. mTLS proves which workload sent it, with a certificate issued to that workload. Workload mTLS is where Cilium is still moving. Its first design, mutual authentication based on SPIFFE, is Beta and deprecated in Cilium 1.20, and the docs for the next release have removed it. The replacement runs Istio's ztunnel on each node and is also Beta. If identity-based mTLS is your main reason for a mesh, check its status before you pick Cilium for it.

Hubble is Cilium's observability layer. It records every flow the eBPF programs see. Each flow has the source and destination identity and a verdict, forwarded or dropped, plus HTTP details for traffic through Envoy. The command `hubble observe` streams flows in the terminal, and the Hubble UI draws a service map. When a NetworkPolicy drops a packet, Hubble names the Pods involved and the reason, which beats guessing.

Cilium's GAMMA support has one limit to know about. It supports only producer routes, so an HTTPRoute must live in the same namespace as the Service it attaches to.

Next, we'll meet one more mesh, and say goodbye to one that has gone."""

S4 = """Consul is HashiCorp's service discovery tool, a phone book that tells services where to find each other. Its service mesh uses Envoy sidecars. On Kubernetes, the Helm chart installs Consul with the mesh switched on. A component called Consul Dataplane manages each Envoy, and the Consul servers hand the proxies their config over xDS.

Consul's strength is reach outside Kubernetes. One mesh can include services on VMs (virtual machines, whole computers simulated in software) and in several data centers. That makes it a natural pick for a company that already runs Consul for service discovery.

Since August 2023 Consul has been source-available under the Business Source License. You can read the code, but the license limits how you may use it, so it is no longer open source.

AWS App Mesh, Amazon's managed mesh built on Envoy, is gone. AWS stopped taking new customers in September 2024 and ended support on September 30, 2026. After that date the console and its resources are no longer available. If you find App Mesh in an old design document, read it as history. For ECS workloads (Amazon's own container service), look at ECS Service Connect, which is where AWS's migration guide points.

Four meshes, four sets of routing objects. Next, we'll see how to write one route for all of them."""

S5 = """Every mesh used to have its own routing objects: VirtualService in Istio, ServiceProfile and TrafficSplit in Linkerd, CiliumEnvoyConfig in Cilium. Moving to another mesh meant rewriting every route. GAMMA, the Gateway API's work for meshes, is the fix. It started in 2022, and its routes have been in the Standard channel since Gateway API 1.1.

The idea is small. On Day 44 an HTTPRoute had a Gateway as its parent, so its rules applied to traffic entering through that Gateway. In GAMMA the parent is a Service:
- `parentRefs` names the Service with `kind: Service` and `group: ""`, the core API group. Linkerd's docs and the GAMMA page write `group: core` instead; Linkerd accepts both.
- The rules apply to every meshed call to that Service, wherever the caller runs. The caller's proxy does the work, or the waypoint in Istio's ambient mode.
- Once a route is attached to a Service, requests that match none of its rules are rejected. A last rule with no `matches` catches everything else.

Where the route lives matters. A producer route sits in the Service's own namespace and applies to callers from every namespace, so the team that owns the Service writes it. A consumer route sits in the caller's namespace and changes only that caller's traffic, for example a shorter timeout for one client.

The lab shows the payoff. `mesh/linkerd/httproute-canary.yaml` has exactly the spec of Day 59's Istio route. Only the annotations differ, because Linkerd reads retries from annotations.

The meshes still support different Gateway API versions. Istio 1.31's docs install 1.6.0, while Linkerd 2.20 stops at 1.5.1. So use fields that exist in the oldest version you need, and check the CRD version a cluster has before you rely on a field.

Routes can move between meshes now. Next, we'll put a price on running one at all."""

S6 = """A mesh is not free, and the bill has five lines:
- Latency. Every proxy adds a hop. In the worked example, one Envoy hop on the test machine added about 0.6 ms to the median call (the middle value when all calls are sorted by time). A sidecar mesh puts two proxies on each call, one at each end.
- CPU and memory. The lab's idle Envoy, with a tiny config, held about 64 MB of memory. In sidecar mode you pay that for every Pod. By default an Istio sidecar also hears about every Service in the mesh, so its config grows with the mesh unless you limit it.
- Upgrades. The control plane and every proxy need upgrading, in a supported order. In sidecar mode a new proxy version means restarting every Pod.
- Debugging. A failed call has more places to fail. A 503 can come from the app, the caller's proxy, a waypoint or the receiver's proxy, and on-call engineers must know how to tell which.
- People. Somebody owns the certificates and the trust anchor, reads the release notes, and is the expert when the mesh is the suspect.

Istio's own numbers from Day 59 are 0.63 to 0.88 ms per call for sidecars and 0.16 to 0.20 ms for ambient mode without a waypoint. Numbers from someone else's test bench are a starting point. The worked example shows how to measure your own in five minutes, and your own are the ones to put in a decision document.

This is the brochure's missing page. Next, we'll read it next to our real needs and decide."""

S7 = """For a handful of services owned by one team, I would not start with a mesh. That is the bakery with one door. Tools you already know cover most of Day 58's list:
- NetworkPolicy (Day 41) decides who may talk to whom.
- A shared client library sets timeouts and retries, such as Resilience4j for Java or Kotlin services.
- One Gateway (Day 44) handles TLS and routing at the edge, including canaries for traffic from users.
- OpenTelemetry (Day 57) and Prometheus (Day 50) give per-call metrics and traces.

A mesh also cannot fix every problem. It will not speed up a slow database query or stop an app from crashing on bad input; it only wraps proxies around the slow call. Before you install one, write down the two or three problems you expect it to solve. Measure them before and after, and take the mesh out again if the numbers do not move.

The answer changes as services and teams multiply, when services are written in many languages, or when a customer or auditor asks for encryption and identity on every internal call. At that point one mesh is cheaper than the same work done in every repository. The lab's `CHECKLIST.md` turns this into questions you can answer for a real system.

If you adopt one, go one namespace at a time, in this order:
1. Observe. Mesh a namespace and only watch the golden metrics. You will find calls nobody knew about.
2. mTLS in permissive mode, so meshed callers encrypt and everyone else still works.
3. Strict mTLS, once the metrics show that every caller is meshed.
4. Authorization policies, starting with the services that hold sensitive data.
5. Traffic policies last: retries, timeouts, canaries and fault tests.

Multi-cluster is its own project. Istio, Linkerd and Cilium can all connect clusters, so a call can fail over to another region. Each needs certificates that all the clusters trust and network paths between them. Start it only after one cluster runs smoothly.

Even a well-run mesh only sees the calls between services. It does not see inside the code, the database or the machine. Putting all of that in one picture is the job of the next part."""

CLOSING = """We started with a bakery that was offered a tower's security system. Today we met Linkerd's small proxy, Cilium's mesh inside the network, Consul's reach beyond Kubernetes, and one GAMMA route that works in more than one of them. We also put a price on a single proxy: about 0.6 ms and 64 MB. In the lab, run the checklist in `CHECKLIST.md` for a system you know, and count how many boxes you can tick.

Next, we'll leave the open-source parts behind and meet Dynatrace, one commercial product that collects every signal at once. What do you gain when one tool sees everything, and what do you give up?"""

L = lesson(load(15), "d60")
deeper = L["deeper"]["body"].split("\n\nGAMMA's name, spelled out")[0]
deeper += "\n\nGAMMA's name, spelled out, for when you search for it: Gateway API for Mesh Management and Administration."

new = {
    "goal": "By the end you can compare Linkerd, Istio, Cilium and Consul, write one GAMMA route that works in more than one mesh, put numbers on what a mesh costs, and decide whether your system needs one.",
    "opening": OPENING,
    "guess": (
        "Cilium's service mesh is often called sidecar-free (no proxy inside each Pod). Where does an HTTP retry or a path-based route actually run?",
        "eBPF handles L3 and L4 work in the kernel, but HTTP is read by Envoy. Cilium runs one Envoy per node, the `cilium-envoy` DaemonSet, for its L7 features.",
    ),
    "terms": [
        "Linkerd's sidecar proxy: a small proxy written in Rust, built only for service mesh work.",
        "A frequent Linkerd build from the main branch, named like edge-26.11.1. The open source project ships only these.",
        "The root certificate a mesh trusts. Every workload certificate is signed under it.",
        "Small programs that the Linux kernel runs safely, which Cilium uses to handle packets without a separate proxy program.",
        "Cilium's tool that records the network flows between Pods so you can watch and search them.",
        "The Gateway API's way to configure a mesh: routes attach to a Service instead of a Gateway.",
        "A GAMMA route in the same namespace as its Service. It applies to callers from every namespace.",
    ],
    "sections": [
        ("Linkerd: a small proxy and few knobs", S1),
        ("Linkerd's releases, its license, and a certificate that expires", S2),
        ("Cilium: the mesh inside the network plugin", S3),
        ("Consul, and a mesh that was retired", S4),
        ("GAMMA: one route for many meshes", S5),
        ("What a mesh costs", S6),
        ("When you do not need a mesh, and how to adopt one", S7),
    ],
    "diagram_caption": "Decide first; if a mesh is worth it, switch it on one layer at a time.",
    "say": [
        "Start the Day 58 lab. Compose puts its containers on a network called `mesh-envoy_default`, so a throwaway curl container on that network can call the app directly and through Envoy. It sends 300 requests to each address and prints the 150th and 270th time after sorting: the median and the 90th percentile, in seconds.",
        "Read the numbers. Through Envoy the median went from 1.46 ms to 2.09 ms, about 0.6 ms more, and the 90th percentile moved by about as much. Each curl opens a new connection, so connection setup is included. A sidecar mesh puts two such hops on every call. Your laptop will give other numbers, which is exactly why you measure.",
        "Now memory. The admin port reports what Envoy has allocated, and `/proc` (a folder where Linux reports on running programs) shows what the whole process holds in RAM. This Envoy uses about 7 MB for its config and state, and about 64 MB in total once the program itself is counted.",
        "Turn the measurement into a rough budget for a made-up payments product: 8 services with 3 Pods each. With a sidecar per Pod at about 64 MB, the proxies need about 1.5 GB before they carry any traffic, and every call crosses two of them. In ambient mode the count is one ztunnel per node instead of one proxy per Pod. These are estimates from one small proxy, so treat them as a first guess.",
        "Then answer section 1 of the lab's checklist for the same product. It has one team, Kotlin and Python, NetworkPolicies, one Gateway and OpenTelemetry already, and no auditor asking for mTLS. Every box is ticked, so the answer is no mesh yet, with a note to look again when a second team or a compliance rule arrives. Stop the lab with `docker compose down`.",
    ],
    "task": (
        [
            "Create a new kind cluster named `linkerd`, separate from the Istio one, and install the Linkerd CLI with the edge install script.",
            "Install the Gateway API CRDs v1.5.1, then Linkerd's CRDs and control plane, running `linkerd check` after each step.",
            "Install the viz extension, load `hello-devops:1.0.0` into kind, and apply `mesh/linkerd/namespace.yaml` and `mesh/istio/apps.yaml`.",
            "Send 50 calls from the client Pod, then confirm with `linkerd viz -n hello-mesh edges deployment` that the connections are secured.",
            "Apply `mesh/linkerd/httproute-canary.yaml`, count the versions over 200 calls, and compare with your Istio result from Day 59.",
            "Run `linkerd viz -n hello-mesh stat-outbound deploy/client` and find the two backends and their request rates.",
            "Diff the Linkerd and Istio route files and write down which lines are Linkerd-only, and why.",
            "Fill in `CHECKLIST.md` for a system you know from work, then delete the cluster.",
        ],
        [
            "If `linkerd check --pre` fails, it prints a link with hints next to the failed check. Fix that one first.",
            "The Commands list has a `kubectl get crds` line that prints which Gateway API version a cluster has.",
            "Calls through `kubectl port-forward` skip the client's proxy, so the route does not apply to them. Call from the client Pod.",
        ],
        "You are done when `linkerd viz edges` shows the connections between your Pods as secured and about 9 in 10 calls from the client reach version 1.0.0.",
    ),
    "explain_back": (
        "Explain in 3 to 4 sentences when you would add a service mesh and which one you would try first. Mention cost, mTLS and GAMMA.",
        "I would add a mesh when many services in several languages need the same mTLS, metrics and traffic rules. An auditor who requires encryption and identity on every internal call is another good reason. For a few services, NetworkPolicy, client-side retries, one Gateway and OpenTelemetry are cheaper. Every mesh costs latency per hop, memory per proxy, upgrades and people, so I would measure those first. I would try Linkerd for mTLS and golden metrics, or Istio in ambient mode for a wider feature set, and write routes as GAMMA HTTPRoutes so they move with me.",
    ),
    "recap": [
        "Linkerd uses its own Rust sidecar proxy and gives mTLS and golden metrics with almost no config. Its default trust anchor expires after a year.",
        "The Linkerd project ships edge releases; stable releases come from vendors such as Buoyant, free under 50 employees.",
        "Cilium handles L3 and L4 in eBPF and runs one Envoy per node for HTTP; its workload mTLS is still Beta.",
        "GAMMA attaches HTTPRoutes to a Service, so one route file works in Istio, Linkerd and Cilium.",
        "A mesh costs latency, memory, upgrades, debugging time and people, and it cannot fix a slow query. Measure before you decide.",
        "Adopt in steps: observe, permissive mTLS, strict mTLS, authorization, then traffic rules.",
    ],
    "closing": CLOSING,
    "check": [
        ("Your cluster runs Cilium as its CNI. A team wants a 95/5 canary between two internal services. Which object is the most portable way to write it?",
         "A GAMMA HTTPRoute works in Cilium today, and in Istio and Linkerd too."),
        ("A team installs Linkerd with the default `linkerd install` and never touches its certificates. What breaks first, a year later?",
         "The default trust anchor and issuer certificate last a year. Without rotation, the proxies can no longer get valid certificates."),
        ("Which situation is the weakest reason to add a service mesh?",
         "A mesh can show you the slow call, but it cannot make the query faster."),
    ],
    "interview": [
        ("How do Istio, Linkerd and Cilium differ as service meshes?",
         "Istio uses Envoy, either as a sidecar in every Pod or, in ambient mode, as an optional waypoint behind a per-node ztunnel, and it has the widest feature set. Linkerd uses its own small Rust sidecar and focuses on mTLS, golden metrics and reliability with very little configuration. Cilium builds the mesh into its network plugin: eBPF in the kernel for L3 and L4, one Envoy per node for HTTP, and Hubble for flow visibility. Its workload mTLS is still Beta. All three accept Gateway API routes, which makes the routing layer portable."),
        ("When would you not use a service mesh?",
         "With only a few services and teams, a shared client library, NetworkPolicies, an ingress Gateway and OpenTelemetry cover retries, segmentation, edge TLS and visibility for less. A mesh adds latency to every call, memory for every proxy, upgrades and one more system to debug. I would also wait when nobody can own it, because certificates and upgrades need a named owner. I revisit the decision when the number of services, languages or compliance demands grows."),
        ("How would you roll out a mesh in an existing cluster?",
         "Namespace by namespace, in layers. First I mesh one namespace and use only the metrics, which usually shows dependencies nobody knew about. Then I turn on mTLS in permissive mode, check that every caller is meshed, and switch to strict. Authorization policies come next and traffic policies such as retries and canaries last. At each step I keep a way back, such as removing the namespace label, and I watch the error rates."),
    ],
    "deeper": deeper,
    "drop": ["analogy", "mistake", "real_world"],
}

apply(15, "d60", new)
