"""Day 59: Istio: traffic management, mTLS and ambient mode."""
from common import (E_FAULT, I_131, I_AMB_START, I_AMBIENT, I_ANALYZE, I_AUTHZ, I_CB, I_DATAPLANE, I_DR, I_FAULT,
                    I_GWAPI, I_KIALI, I_KIND, I_L7, I_MODES, I_MTLS, I_PROFILES, I_PROXYCMD, I_SEC, I_TRACING, I_VS,
                    S, V_AMBIENT, lab)

DIAGRAM = (
    '<svg viewBox="0 0 560 280" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="istiod configures every '
    'proxy. In sidecar mode, app A talks to its own Envoy, which talks over mTLS to the Envoy next to app B. In ambient '
    'mode, app A goes through the ztunnel on its node, an optional waypoint, and the ztunnel on the other node to app B">'
    '<rect class="bxp" x="232" y="10" width="96" height="36" rx="10"/>'
    '<text class="tk" x="280" y="33" font-size="13" text-anchor="middle">istiod</text>'
    '<text class="ts" x="340" y="33" font-size="11" text-anchor="start">config and certificates</text>'
    '<line class="lnd" x1="256" y1="46" x2="150" y2="94" marker-end="url(#ar)"/>'
    '<line class="lnd" x1="304" y1="46" x2="404" y2="94" marker-end="url(#ar)"/>'
    # sidecar row
    '<text class="ts" x="8" y="86" font-size="11" text-anchor="start">sidecar mode</text>'
    '<rect class="bx" x="8" y="96" width="72" height="40" rx="10"/>'
    '<text class="t" x="44" y="121" font-size="13" text-anchor="middle">app A</text>'
    '<line class="ln" x1="82" y1="116" x2="100" y2="116" marker-end="url(#ar)"/>'
    '<rect class="bxt" x="104" y="96" width="80" height="40" rx="10"/>'
    '<text class="tk" x="144" y="121" font-size="13" text-anchor="middle">Envoy</text>'
    '<line class="ln" x1="186" y1="116" x2="364" y2="116" marker-end="url(#ar)"/>'
    '<text class="ts" x="276" y="108" font-size="11" text-anchor="middle">mTLS</text>'
    '<rect class="bxt" x="368" y="96" width="80" height="40" rx="10"/>'
    '<text class="tk" x="408" y="121" font-size="13" text-anchor="middle">Envoy</text>'
    '<line class="ln" x1="450" y1="116" x2="468" y2="116" marker-end="url(#ar)"/>'
    '<rect class="bx" x="472" y="96" width="72" height="40" rx="10"/>'
    '<text class="t" x="508" y="121" font-size="13" text-anchor="middle">app B</text>'
    '<text class="ts" x="96" y="154" font-size="11" text-anchor="middle">Pod A</text>'
    '<text class="ts" x="456" y="154" font-size="11" text-anchor="middle">Pod B</text>'
    # ambient row
    '<text class="ts" x="8" y="190" font-size="11" text-anchor="start">ambient mode</text>'
    '<rect class="bx" x="8" y="200" width="72" height="40" rx="10"/>'
    '<text class="t" x="44" y="225" font-size="13" text-anchor="middle">app A</text>'
    '<line class="ln" x1="82" y1="220" x2="100" y2="220" marker-end="url(#ar)"/>'
    '<rect class="bxt" x="104" y="200" width="80" height="40" rx="10"/>'
    '<text class="tk" x="144" y="225" font-size="13" text-anchor="middle">ztunnel</text>'
    '<line class="ln" x1="186" y1="220" x2="232" y2="220" marker-end="url(#ar)"/>'
    '<text class="ts" x="210" y="212" font-size="11" text-anchor="middle">HBONE</text>'
    '<rect class="bxo" x="236" y="200" width="88" height="40" rx="10"/>'
    '<text class="tk" x="280" y="225" font-size="13" text-anchor="middle">waypoint</text>'
    '<line class="ln" x1="326" y1="220" x2="372" y2="220" marker-end="url(#ar)"/>'
    '<text class="ts" x="350" y="212" font-size="11" text-anchor="middle">HBONE</text>'
    '<rect class="bxt" x="376" y="200" width="80" height="40" rx="10"/>'
    '<text class="tk" x="416" y="225" font-size="13" text-anchor="middle">ztunnel</text>'
    '<line class="ln" x1="458" y1="220" x2="468" y2="220" marker-end="url(#ar)"/>'
    '<rect class="bx" x="472" y="200" width="72" height="40" rx="10"/>'
    '<text class="t" x="508" y="225" font-size="13" text-anchor="middle">app B</text>'
    '<text class="ts" x="144" y="258" font-size="11" text-anchor="middle">node 1, L4</text>'
    '<text class="ts" x="280" y="258" font-size="11" text-anchor="middle">L7, optional</text>'
    '<text class="ts" x="416" y="258" font-size="11" text-anchor="middle">node 2, L4</text>'
    '</svg>'
)

FAULT_RULE = """    - match:
        - headers:
            x-fault:
              exact: "on"
      fault:
        delay:
          percentage:
            value: 50
          fixedDelay: 2s
        abort:
          percentage:
            value: 20
          httpStatus: 503"""

LESSON = {
    "id": "d59",
    "title": "Istio: traffic management, mTLS and ambient mode",
    "minutes": 50,
    "goal": "By the end you can explain how istiod, sidecars, ztunnel and waypoints fit together, write Istio and Gateway API objects for a canary, circuit breaking, mTLS and authorization, and debug them with istioctl.",
    "guess": {
        "q": "You label a namespace `istio-injection=enabled` while its Pods are already running. What happens to those Pods?",
        "options": [
            "Istio adds a sidecar to each of them within a minute",
            "Nothing, until each Pod is created again",
            "Kubernetes restarts all of them at once",
            "They lose their network until you restart them",
        ],
        "answer": 1,
        "why": "A webhook adds the sidecar when a Pod is created, so running Pods keep their old spec until a restart. Ambient mode's label is different: it works on running Pods, with no restart.",
    },
    "terms": [
        {"term": "istiod", "plain": "Istio's control plane: it turns your config into Envoy config, pushes it over xDS and signs workload certificates."},
        {"term": "Sidecar injection", "plain": "A webhook that adds the Envoy container to each new Pod in a labeled namespace."},
        {"term": "ztunnel", "plain": "Istio's small per-node proxy in ambient mode; it does mTLS and L4 policy for every Pod on its node."},
        {"term": "Waypoint", "plain": "An Envoy that Istio runs per namespace or per service in ambient mode, for HTTP features."},
        {"term": "SPIFFE ID", "plain": "A workload's name written as a URI, such as spiffe://cluster.local/ns/hello-mesh/sa/client."},
        {"term": "Mutual TLS (mTLS)", "plain": "TLS in which both sides show a certificate, so each knows who the other is."},
        {"term": "PeerAuthentication", "plain": "The Istio object that says whether a workload accepts plain text, mTLS, or both."},
        {"term": "AuthorizationPolicy", "plain": "The Istio object that allows or denies requests by caller identity, namespace, method or path."},
    ],
    "sections": [
        {
            "h": "One control plane, two kinds of data plane",
            "body": (
                "Istio is a service mesh built on Envoy, and Day 58 already gave you most of its moving parts. The control "
                "plane is one program, istiod, with three jobs:\n"
                "- It watches the Kubernetes API and your Istio and Gateway API objects, and turns them into listeners, routes, clusters and endpoints for every proxy, sent over xDS.\n"
                "- It runs a certificate authority that gives every workload a short-lived certificate, valid for 24 hours by default.\n"
                "- It runs the webhook that injects sidecars into new Pods.\n\n"
                "The data plane comes in two modes. One mesh can mix them, but each namespace should use one.\n\n"
                "Sidecar mode is the original design, used since 2017. Every Pod gets an Envoy, and every call passes through "
                "two of them, the caller's and the receiver's. Each proxy handles both L4 and L7, so every feature works "
                "everywhere.\n\n"
                "**Ambient mode** splits the work into two layers. ztunnel, a proxy written in Rust, runs once per node. It "
                "encrypts and authenticates the traffic of every Pod on its node and enforces L4 rules, but never parses "
                "HTTP. For HTTP features you add a waypoint: an Envoy that runs as its own Deployment, usually one per "
                "namespace. Traffic between ztunnels and waypoints travels in an mTLS tunnel called HBONE, on port 15008.\n\n"
                "Ambient mode became generally available in Istio 1.24, in November 2024. Istio now lists it as Stable for a "
                "single cluster, and multi-cluster ambient as Beta. Istio 1.31, released in August 2026, is the "
                "current version as I write this. The same page quotes Istio's latency tests, at p90 and p99:\n"
                "- 0.63 to 0.88 ms per call with sidecars.\n"
                "- 0.16 to 0.20 ms with ztunnel alone.\n"
                "- 0.40 to 0.50 ms through a waypoint."
            ),
            "refs": [I_AMBIENT, I_MODES, I_131],
        },
        {
            "h": "Install on kind and join a namespace",
            "body": (
                "On a Mac, `brew install istioctl` gets you the CLI. Istio's download script works too, and also brings the "
                "sample apps. istioctl installs Istio from a profile, a named set of settings:\n"
                "- `default`: istiod plus an ingress gateway, the starting point for production.\n"
                "- `demo`: more features and heavy logging, for tutorials only.\n"
                "- `minimal`: istiod alone. The lab uses it, because the Gateway API creates gateways when you ask for one.\n"
                "- `ambient`: istiod, the Istio CNI node agent and ztunnel.\n\n"
                "Install the Gateway API CRDs first, because Istio reads them. Istio 1.31's docs install Gateway API v1.6.0. "
                "Version 1.7.0 is out, and Envoy Gateway from Day 44 brings its own copy, so check which version a cluster "
                "already has before you apply another.\n\n"
                "Then decide how each namespace joins the mesh:\n"
                "- Sidecar mode: `kubectl label namespace hello-mesh istio-injection=enabled`. Only Pods created after the label get a sidecar, so restart your Deployments. Since Istio 1.27 the proxy is a native sidecar, an init container that keeps running.\n"
                "- Ambient mode: `kubectl label namespace hello-mesh istio.io/dataplane-mode=ambient`. ztunnel takes over the running Pods at once, with no restart and no extra container. When you need HTTP features, add a waypoint with `istioctl waypoint apply -n hello-mesh --enroll-namespace`.\n\n"
                "Never put both labels on one namespace. If you do, sidecar mode wins for those Pods."
            ),
            "refs": [I_PROFILES, I_AMB_START, V_AMBIENT],
        },
        {
            "h": "Routing: the Gateway API first, then the Istio APIs you will still meet",
            "body": (
                "Istio has its own routing objects, older than the Gateway API, and the project says it intends to make the "
                "Gateway API its default. For new work, write Gateway API objects. Traffic from outside enters through a "
                "Gateway with HTTPRoutes attached (Day 44). Traffic inside the mesh uses an HTTPRoute whose `parentRef` is a "
                "Service instead of a Gateway. Day 60 explains that pattern, called GAMMA.\n\n"
                "The lab's `httproute-canary.yaml` attaches to the `hello-devops` Service, and the client's sidecar applies it "
                "to every call to `http://hello-devops`:\n"
                "- A request with the header `x-canary: always` goes to the canary.\n"
                "- Everything else is split 90 to 10 by weight.\n"
                "- `timeouts.request: 3s` caps each request.\n\n"
                "Older Istio setups use Istio's own objects, and you will meet them at work:\n"
                "- VirtualService: routing rules for a host, with retries, timeouts, header matches and fault injection.\n"
                "- DestinationRule: what happens after routing picked a destination. Connection limits, outlier detection, TLS settings and subsets (named groups of Pods by label, such as `version: v2`) live here.\n"
                "- Istio's Gateway, in the `networking.istio.io` group: settings for an ingress proxy you deployed yourself. It is a different object from the Gateway API's Gateway, despite the name.\n\n"
                "Retries show where the two APIs still differ. The Standard channel of Gateway API v1.6.0 has no retry field, and "
                "v1.7.0 added one, so the lab puts retries in the VirtualService. Do not let an HTTPRoute and a VirtualService "
                "both route the same Service. The lab deletes one before it applies the other, so you always know which rules "
                "are live."
            ),
            "refs": [I_GWAPI, I_VS, I_DR],
        },
        {
            "h": "Breaking things on purpose: faults and circuit breakers",
            "body": (
                "How does your app behave when a dependency is slow or failing? Waiting for an outage to find out is "
                "expensive. Fault injection causes the failure on purpose, in a share of requests you choose.\n\n"
                "A VirtualService rule can add two kinds of fault:\n"
                "- A delay holds the request for a while, say 2 seconds, before sending it on.\n"
                "- An abort answers at once with a status such as 503, without calling the service at all.\n\n"
                "Each fault has a `percentage`, so you can hurt 1 request in 5 and leave the others alone. The lab's file "
                "only injects faults into requests that carry `x-fault: on`, which keeps normal traffic safe. Istio switches "
                "off timeouts and retries on a rule that injects faults, so healthy traffic gets a second rule with a "
                "3-second timeout and two retries. The fault happens in the caller's sidecar, which is exactly where your own "
                "timeout and retry code would notice it.\n\n"
                "Circuit breaking lives in a DestinationRule, and it maps one to one onto Day 58's Envoy settings:\n"
                "- `connectionPool.tcp.maxConnections` and `connectionPool.http.http1MaxPendingRequests` become Envoy circuit breakers. Over the limit, the caller gets a 503 at once.\n"
                "- `outlierDetection.consecutive5xxErrors`, `interval`, `baseEjectionTime` and `maxEjectionPercent` become Envoy outlier detection.\n\n"
                "Istio even keeps Envoy's stat names. Its circuit breaking task reads `upstream_rq_pending_overflow` for a "
                "cluster called `outbound|8000||httpbin.default.svc.cluster.local`: direction, port, subset and host, in that "
                "order."
            ),
            "refs": [I_FAULT, I_CB],
        },
        {
            "h": "Identity and mutual TLS",
            "body": (
                "Day 11 showed TLS in which only the server proves who it is. In mutual TLS both sides present a "
                "certificate, so the server also learns who is calling. Istio gives every workload that certificate "
                "automatically.\n\n"
                "The identity comes from the Pod's ServiceAccount (Day 64). Istio writes it as a SPIFFE ID, a standard format "
                "for workload names: `spiffe://cluster.local/ns/hello-mesh/sa/client` is ServiceAccount `client` in namespace "
                "`hello-mesh`, in the trust domain `cluster.local`. That is why the lab gives each Deployment its own "
                "ServiceAccount. Workloads that share one also share an identity.\n\n"
                "A sidecar gets its certificate in four steps:\n"
                "1. The Istio agent next to Envoy creates a private key and a signing request.\n"
                "2. It sends the request to istiod, with the Pod's ServiceAccount token as proof.\n"
                "3. istiod checks the token and signs a certificate valid for 24 hours.\n"
                "4. The agent hands key and certificate to Envoy over SDS, the secret API from Day 58, and renews them before they expire.\n\n"
                "PeerAuthentication says what a workload accepts:\n"
                "- PERMISSIVE, the default, accepts mTLS and plain text. Meshed callers already use mTLS, and callers outside the mesh still work.\n"
                "- STRICT accepts mTLS only, and plain-text callers are refused.\n"
                "- DISABLE turns mTLS off. Avoid it.\n\n"
                "Move to STRICT in steps: start PERMISSIVE, check that every caller of a namespace is in the mesh, then switch "
                "that namespace. In the lab, a Pod in the `outside` namespace can call hello-devops until you apply "
                "`peerauthentication.yaml`. After that the call fails, and curl exits with code 56: the connection was cut "
                "before any HTTP answer arrived."
            ),
            "refs": [I_SEC, I_MTLS],
        },
        {
            "h": "AuthorizationPolicy: who may call what",
            "body": (
                "With mTLS on, every request arrives with a verified caller identity, and AuthorizationPolicy can use it. A "
                "policy has three parts:\n"
                "- `selector`, or `targetRefs` in ambient mode: the workloads it protects.\n"
                "- `action`: ALLOW, DENY, AUDIT (log only) or CUSTOM (ask an outside service).\n"
                "- `rules`: `from` the caller (principals, namespaces, IP ranges) and `to` the operation (methods, paths, ports).\n\n"
                "Istio checks CUSTOM policies first, then DENY, then ALLOW. A workload with no policy allows everything. Once "
                "any ALLOW policy selects it, every request that no ALLOW rule matches is refused with 403 and the text `RBAC: "
                "access denied`. So an ALLOW rule written for one new caller can lock out every other "
                "caller of that workload.\n\n"
                "The lab has two policies for both app versions:\n"
                "1. `deny-metrics` refuses `/metrics` to every namespace except `monitoring`. `notNamespaces` reads the caller's namespace from its certificate, so a forged header cannot get around it.\n"
                "2. `allow-client-get` lets only `cluster.local/ns/hello-mesh/sa/client` in, only with GET, and only on `/`, `/healthz` and `/readyz`. A principal is the SPIFFE ID without `spiffe://`.\n\n"
                "In ambient mode, where the policy runs matters. ztunnel sees connections, so it can enforce identity and port "
                "rules but not paths or methods. A policy with HTTP rules has to be attached to a waypoint with `targetRefs`. "
                "If you write it with a `selector` instead, ztunnel enforces it and, to fail safe, treats it as a DENY. The "
                "lab's `ambient/authorizationpolicy.yaml` is the waypoint version."
            ),
            "refs": [I_AUTHZ, I_L7],
        },
        {
            "h": "Debugging and observing: istioctl, Prometheus, Kiali and traces",
            "body": (
                "Most Istio problems are config that did not do what you meant. istioctl shows what each proxy really "
                "received:\n"
                "- `istioctl analyze` checks your objects for known mistakes, such as a route to a missing Service. With `--use-kube=false` it checks files, with no cluster.\n"
                "- `istioctl proxy-status` lists every proxy and whether it has istiod's latest config.\n"
                "- `istioctl proxy-config listener`, `route`, `cluster`, `endpoint` and `secret` print one part of a proxy's live config, in Day 58's vocabulary. `secret` shows the workload certificate and its expiry.\n"
                "- `istioctl dashboard envoy deployment/client -n hello-mesh` opens that sidecar's Envoy admin page, with the same `/clusters` and `/stats` as yesterday.\n"
                "- In ambient mode, `istioctl ztunnel-config workload` shows what ztunnel knows about each Pod.\n\n"
                "Every proxy exports Prometheus metrics, and the one to start with is `istio_requests_total`, a counter "
                "labeled with source, destination and response code. The PromQL from Day 51 works on it unchanged. Kiali reads "
                "those metrics and draws a live graph of who calls whom, with error rates on the edges. Istio's sample addons "
                "install Prometheus and Kiali in two commands, listed in the lab's README.\n\n"
                "Traces need one thing from you. The proxies can create a span for every hop, but a proxy cannot tell which "
                "outgoing call belongs to which incoming request inside your app. Your app must copy the trace headers from "
                "the request it received onto the requests it sends: the context propagation of Day 57. OpenTelemetry "
                "instrumentation does it for you. Without it, Jaeger shows one short trace per hop instead of one trace per "
                "user request."
            ),
            "refs": [I_ANALYZE, I_PROXYCMD, I_TRACING],
        },
    ],
    "analogy": (
        "Workload identity in Istio works like staff badges in an office tower. A badge office (istiod) prints every "
        "employee a badge that is valid for one day, with their name and team on it. Door readers (the proxies) check the "
        "badge instead of the face, and a sign on each door says which teams may enter. In ambient mode one guard per "
        "floor (ztunnel) checks badges for everyone on that floor, and only rooms with special rules get their own doorman "
        "(a waypoint). A badge can be lent to a friend; a workload's key stays inside its proxy and is useless after a day."
    ),
    "diagram": DIAGRAM,
    "diagram_caption": "Sidecar mode puts an Envoy in every Pod; ambient mode uses a ztunnel per node and adds a waypoint only for HTTP features.",
    "worked": {
        "title": "Fault injection by hand in Envoy, then the Istio way",
        "steps": [
            {
                "say": "Start the Day 58 lab again. Its `envoy.yaml` already has a fault filter at 0 percent and a runtime layer that the admin port can change. Turn faults on while Envoy runs: abort 10% of requests with a 503 and delay 20% by 2 seconds. Envoy answers OK, and `/runtime` shows the new values.",
                "code": (
                    "$ docker compose up -d\n"
                    "$ curl -s -X POST 'localhost:9901/runtime_modify?fault.http.abort.abort_percent=10&fault.http.delay.fixed_delay_percent=20'\n"
                    "OK\n"
                    "$ curl -s localhost:9901/runtime | jq -c '.entries | with_entries(select(.key | startswith(\"fault\"))) | map_values(.final_value)'\n"
                    "{\"fault.http.abort.abort_percent\":\"10\",\"fault.http.delay.fixed_delay_percent\":\"20\"}"
                ),
                "lang": "console",
            },
            {
                "say": "Send 100 requests and keep each status code and total time. Six were aborted and 30 took more than 1.5 seconds. Each request rolls the dice on its own, so your counts will differ, and a few requests get both faults.",
                "code": (
                    "$ for i in $(seq 1 100); do curl -s -o /dev/null -w '%{http_code} %{time_total}\\n' localhost:10000/; done > faults.txt\n"
                    "$ awk '{print $1}' faults.txt | sort | uniq -c\n"
                    "     94 200\n"
                    "      6 503\n"
                    "$ awk '$2 > 1.5' faults.txt | wc -l\n"
                    "30"
                ),
                "lang": "console",
            },
            {
                "say": "The access log explains each odd line. The field after the status code is the response flags: `FI` is an injected abort and `DI` an injected delay. The aborted request never reached a host, so its upstream host at the end is `-`. The delayed one took 2004 ms in total, of which the app spent 3 ms.",
                "code": (
                    "$ docker compose logs --no-log-prefix envoy | grep '\" 503 FI ' | tail -1\n"
                    "[2026-11-07T17:50:22.307Z] \"GET / HTTP/1.1\" 503 FI 0 18 0 - \"-\" \"curl/8.5.0\" \"b7cd01d9-8c59-4461-97ee-0868c8c7ce5f\" \"localhost:10000\" \"-\"\n"
                    "$ docker compose logs --no-log-prefix envoy | grep '\" 200 DI ' | tail -1\n"
                    "[2026-11-07T17:50:32.563Z] \"GET / HTTP/1.1\" 200 DI 0 81 2004 3 \"-\" \"curl/8.5.0\" \"d1711511-dee2-41f7-86a7-1801c99089c7\" \"localhost:10000\" \"172.20.0.2:8000\""
                ),
                "lang": "console",
            },
            {
                "say": "Envoy counts every fault it injects. Check these counters whenever a fault test seems to change nothing: maybe the test never ran. Then switch the faults off again.",
                "code": (
                    "$ curl -s 'localhost:9901/stats?filter=^http\\.ingress_http\\.fault\\.(aborts|delays)_injected$'\n"
                    "http.ingress_http.fault.aborts_injected: 6\n"
                    "http.ingress_http.fault.delays_injected: 30\n"
                    "$ curl -s -X POST 'localhost:9901/runtime_modify?fault.http.abort.abort_percent=0&fault.http.delay.fixed_delay_percent=0'\n"
                    "OK\n"
                    "$ docker compose down"
                ),
                "lang": "console",
            },
            {
                "say": "Now the Istio version. You never write the fault filter yourself there. You write a VirtualService rule, and istiod puts the same Envoy fault settings into the routes of every calling sidecar. This is the fault rule from the lab's `virtualservice-fault.yaml`. It only hurts requests with the header `x-fault: on`.",
                "code": FAULT_RULE,
                "lang": "yaml",
            },
            {
                "say": "Check Istio files before you go near a cluster. On your Mac, `istioctl analyze --use-kube=false *.yaml` runs Istio's own offline checks. The course checked the lab with kubeconform and JSON schemas made from the CRD files of Istio 1.31 and Gateway API v1.6.0. All 20 objects passed, and a one-letter typo in the DestinationRule was caught at once (error trimmed).",
                "code": (
                    "$ kubeconform -strict -summary -schema-location default \\\n"
                    "    -schema-location 'schemas/{{.Group}}/{{.ResourceKind}}_{{.ResourceAPIVersion}}.json' *.yaml ambient/*.yaml\n"
                    "Summary: 20 resources found in 10 files - Valid: 20, Invalid: 0, Errors: 0, Skipped: 0\n"
                    "$ sed 's/consecutive5xxErrors/consecutive5xxError/' destinationrule.yaml > dr-typo.yaml\n"
                    "$ kubeconform -strict -schema-location default -schema-location 'schemas/{{.Group}}/{{.ResourceKind}}_{{.ResourceAPIVersion}}.json' dr-typo.yaml\n"
                    "dr-typo.yaml - DestinationRule hello-devops is invalid: problem validating schema. Check JSON formatting:\n"
                    "  ... at '/spec/trafficPolicy/outlierDetection': additional properties 'consecutive5xxError' not allowed"
                ),
                "lang": "console",
            },
        ],
    },
    "code": [
        {"lang": "yaml", "title": "mesh/istio/namespace.yaml", "src": lab("istio/namespace.yaml"), "run": "kubectl apply -f namespace.yaml"},
        {"lang": "yaml", "title": "mesh/istio/apps.yaml", "src": lab("istio/apps.yaml"), "run": "kind load docker-image hello-devops:1.0.0 --name mesh && kubectl apply -f apps.yaml"},
        {"lang": "yaml", "title": "mesh/istio/httproute-canary.yaml", "src": lab("istio/httproute-canary.yaml"), "run": "kubectl apply -f httproute-canary.yaml"},
        {"lang": "yaml", "title": "mesh/istio/destinationrule.yaml", "src": lab("istio/destinationrule.yaml"), "run": "kubectl apply -f destinationrule.yaml"},
        {"lang": "yaml", "title": "mesh/istio/peerauthentication.yaml", "src": lab("istio/peerauthentication.yaml"), "run": "kubectl apply -f peerauthentication.yaml"},
        {"lang": "yaml", "title": "mesh/istio/authorizationpolicy.yaml", "src": lab("istio/authorizationpolicy.yaml"), "run": "kubectl apply -f authorizationpolicy.yaml"},
        {"lang": "yaml", "title": "mesh/istio/virtualservice-fault.yaml", "src": lab("istio/virtualservice-fault.yaml"), "run": "kubectl delete -f httproute-canary.yaml && kubectl apply -f virtualservice-fault.yaml"},
        {"lang": "yaml", "title": "mesh/istio/ambient/namespace.yaml", "src": lab("istio/ambient/namespace.yaml"), "run": "kubectl apply -f ambient/namespace.yaml"},
        {"lang": "yaml", "title": "mesh/istio/ambient/waypoint.yaml", "src": lab("istio/ambient/waypoint.yaml"), "run": "kubectl apply -f ambient/waypoint.yaml"},
        {"lang": "yaml", "title": "mesh/istio/ambient/authorizationpolicy.yaml", "src": lab("istio/ambient/authorizationpolicy.yaml"), "run": "kubectl apply -f ambient/authorizationpolicy.yaml"},
    ],
    "commands": [
        {"cmd": "brew install istioctl", "what": "Install the Istio CLI on your Mac."},
        {"cmd": "istioctl x precheck", "what": "Check that the cluster is ready for Istio before you install."},
        {"cmd": "istioctl install --set profile=minimal -y", "what": "Install only the control plane, istiod, for sidecar mode."},
        {"cmd": "istioctl install --set profile=ambient --skip-confirmation", "what": "Install istiod, the CNI node agent and ztunnel for ambient mode."},
        {"cmd": "kubectl label namespace hello-mesh istio-injection=enabled", "what": "Give new Pods in the namespace an Envoy sidecar."},
        {"cmd": "kubectl rollout restart deployment -n hello-mesh", "what": "Recreate the Pods so they get their sidecars."},
        {"cmd": "kubectl label namespace hello-mesh istio.io/dataplane-mode=ambient", "what": "Put the namespace's Pods in the ambient mesh, with no restart."},
        {"cmd": "istioctl waypoint apply -n hello-mesh --enroll-namespace", "what": "Deploy a waypoint and send the namespace's traffic through it."},
        {"cmd": "istioctl analyze --use-kube=false *.yaml", "what": "Check Istio and Gateway API files for mistakes without a cluster."},
        {"cmd": "istioctl proxy-status", "what": "List every proxy and whether it has the latest config from istiod."},
        {"cmd": "istioctl proxy-config route deployment/client -n hello-mesh", "what": "Show the routes in one Pod's sidecar."},
        {"cmd": "istioctl proxy-config secret deployment/hello-devops -n hello-mesh", "what": "Show the workload certificate a sidecar holds, and when it expires."},
        {"cmd": "istioctl dashboard envoy deployment/client -n hello-mesh", "what": "Open the Envoy admin page of one sidecar."},
        {"cmd": "istioctl ztunnel-config workload", "what": "Show what ztunnel knows about each Pod in ambient mode."},
        {"cmd": "istioctl dashboard kiali", "what": "Open Kiali's live graph of the mesh (after installing the addon)."},
    ],
    "mistake": (
        "Switching a namespace to `STRICT` before every caller is in the mesh breaks those callers at once. A scraper, a "
        "CronJob in another namespace or an old VM without a proxy starts failing, and the error looks like a network "
        "fault. Stay in PERMISSIVE, look in Istio's metrics or Kiali for plain-text traffic into the namespace, mesh those "
        "callers, and only then switch."
    ),
    "real_world": (
        "Rolling Istio out across a company's clusters usually happens namespace by namespace, in the same order. Metrics "
        "come first, because a graph of who calls whom finds forgotten dependencies within a day. Then mTLS in permissive "
        "mode, then strict, and only after that the traffic rules. App teams own their HTTPRoutes and fault tests, while "
        "the platform team owns istiod, its upgrades and the certificate authority."
    ),
    "task": {
        "title": "Run the Istio lab on kind",
        "steps": [
            "Give Docker Desktop at least 8 GB of memory, create a kind cluster named `mesh`, and install istioctl.",
            "Follow `mesh/istio/README.md` to install the Gateway API CRDs and Istio with the `minimal` profile.",
            "Load `hello-devops:1.0.0` into kind, apply `namespace.yaml` and `apps.yaml`, and confirm with `istioctl proxy-status` that every Pod has a proxy.",
            "Apply the HTTPRoute and count the versions over 200 calls from the client Pod. Then send one call with `x-canary: always`.",
            "From a Pod in the `outside` namespace, call hello-devops before and after you apply `peerauthentication.yaml`.",
            "Apply `authorizationpolicy.yaml`. From the client, check that `/` answers 200 and `/metrics` answers 403.",
            "Delete the HTTPRoute, apply `virtualservice-fault.yaml`, and send 20 calls with and 20 without `x-fault: on`.",
            "Find the fault settings in `istioctl proxy-config route deployment/client -n hello-mesh -o json`, then delete the cluster.",
        ],
        "hints": [
            "If `kubectl exec` picks the wrong container, add `-c curl`: the proxy is a second container in the Pod.",
            "If a Pod has no sidecar, it was created before the namespace label. Run `kubectl rollout restart deployment -n hello-mesh`.",
            "A 403 with `RBAC: access denied` comes from the proxy, so the app's logs show nothing for those calls.",
        ],
        "done_when": "You are done when about 9 in 10 of the client's calls reach version 1.0.0, the Pod in `outside` is refused under STRICT, and `/metrics` answers 403 to the client.",
    },
    "explain_back": {
        "prompt": "Explain in 3 to 4 sentences how two workloads in an Istio mesh know who the other is, and how you turn that into a rule. Mention ServiceAccount, SPIFFE ID, PeerAuthentication and AuthorizationPolicy.",
        "answer": (
            "Each workload's identity comes from its Kubernetes ServiceAccount, written as a SPIFFE ID such as "
            "spiffe://cluster.local/ns/hello-mesh/sa/client. The control plane, istiod, signs a certificate with that ID that lasts 24 hours, and "
            "the proxies on both sides present their certificates in a mutual TLS handshake. PeerAuthentication decides "
            "whether a workload also accepts plain text (PERMISSIVE) or only mTLS (STRICT). AuthorizationPolicy then allows or "
            "denies requests by that verified identity, and by namespace, method and path."
        ),
    },
    "recap": [
        "istiod is the control plane: xDS config, workload certificates and sidecar injection.",
        "Sidecar mode puts Envoy in every Pod; ambient mode uses ztunnel per node for L4 and waypoints for L7.",
        "Ambient mode has been GA since Istio 1.24 and needs no Pod restarts; VirtualService on a waypoint is still Alpha.",
        "Write new routes as Gateway API HTTPRoutes; DestinationRules still hold connection limits and outlier detection.",
        "Identity comes from ServiceAccounts as SPIFFE IDs. Go PERMISSIVE, check every caller, then STRICT.",
        "Once an ALLOW policy selects a workload, everything it does not allow gets a 403.",
    ],
    "check": [
        {
            "q": "In ambient mode you add an AuthorizationPolicy with a `selector` that allows only `GET /orders`. No waypoint exists. What happens?",
            "options": [
                "ztunnel enforces the path rule itself",
                "Istio refuses the policy when you apply it",
                "ztunnel cannot read paths, so it acts as a DENY",
                "The policy is ignored and all traffic passes",
            ],
            "answer": 2,
            "why": "ztunnel only sees connections, so a selector policy with HTTP rules fails safe and denies; attach it to a waypoint with `targetRefs`.",
        },
        {
            "q": "A DestinationRule sets `http1MaxPendingRequests: 1`. A load test fires 20 calls at once from a meshed client. What do many of them get?",
            "options": [
                "A 503 from the caller's proxy, without waiting",
                "A 429 from hello-devops itself",
                "A longer wait, but every call succeeds",
                "A TLS error, because the pool is full",
            ],
            "answer": 0,
            "why": "Past the pending-request limit, Envoy's circuit breaker fails the call at once with a 503.",
        },
        {
            "q": "Deployments `billing` and `reports` both run as ServiceAccount `default`. An AuthorizationPolicy allows only billing's principal. What can `reports` do?",
            "options": [
                "Nothing, because Istio tells them apart by Pod name",
                "Call the service too, because they share one identity",
                "Call it, but only over plain text",
                "Call it, but only after a sidecar restart",
            ],
            "answer": 1,
            "why": "The identity is the ServiceAccount, so two workloads that share one are the same principal to Istio.",
        },
    ],
    "interview": [
        {
            "q": "Sidecar mode or ambient mode: how would you choose?",
            "a": (
                "Ambient mode costs less: one ztunnel per node instead of an Envoy per Pod, no Pod restarts to join, and HTTP "
                "processing only where you add a waypoint. Istio's own tests also show lower latency for it. Sidecar mode is "
                "older and supports every feature, including multi-cluster at the Stable level, and it gives each workload its "
                "own keys. For a new single-cluster mesh I would start in ambient mode with L4 only. Then I would add waypoints "
                "where a team needs HTTP features, unless a feature I need is still missing there."
            ),
        },
        {
            "q": "How does Istio implement mutual TLS between services?",
            "a": (
                "Each workload gets an identity from its ServiceAccount, in SPIFFE format. The Istio agent next to the proxy asks "
                "istiod to sign a certificate for that identity, gets one valid for 24 hours, and hands it to Envoy over SDS. "
                "The proxies on both sides present certificates and check each other against the mesh's trust root. "
                "PeerAuthentication controls whether plain text is still accepted, and AuthorizationPolicy uses the verified "
                "identity to allow or deny calls."
            ),
        },
        {
            "q": "A request through the mesh returns 503. How do you find out whether the proxy or the app produced it?",
            "a": (
                "I check the proxy's access log first. Envoy's response flags tell you when the proxy answered by itself, such "
                "as UO for a circuit breaker overflow or UH for no healthy upstream. The commands `istioctl proxy-config cluster` "
                "and `endpoint` show whether the destination has healthy endpoints at all, and `istioctl analyze` catches routes to "
                "missing Services. If the proxy forwarded the request and the upstream answered 503, the app's own logs show it."
            ),
        },
    ],
    "deeper": {
        "minutes": 12,
        "body": (
            "Follow one call in ambient mode, from the `client` Pod to `hello-devops`, with a waypoint in place:\n"
            "1. The client opens a plain TCP connection to the Service IP. It has no idea a mesh exists.\n"
            "2. When the Pod joined the mesh, the Istio CNI node agent wrote redirect rules inside the Pod's network namespace. They send the connection to the ztunnel on the same node, which listens inside the Pod's namespace on ports 15001, 15006 and 15008.\n"
            "3. ztunnel looks up the destination. The namespace uses a waypoint, so ztunnel sends the bytes to the waypoint instead of straight to a Pod.\n"
            "4. The bytes travel inside HBONE, an HTTP CONNECT tunnel over mutual TLS on port 15008. ztunnel presents the client's certificate, so the waypoint knows the caller is `sa/client`.\n"
            "5. The waypoint is a full Envoy. It parses HTTP, applies the HTTPRoute split and the AuthorizationPolicy, picks a hello-devops Pod, and opens a new HBONE tunnel to the ztunnel on that Pod's node.\n"
            "6. That ztunnel checks its L4 policy, unwraps the tunnel and delivers plain TCP to the app in its Pod.\n\n"
            "Without a waypoint, steps 3 to 5 disappear and the two ztunnels talk to each other directly. That is the cheap "
            "path: encryption, identity and L4 policy, with no HTTP parsing anywhere.\n\n"
            "Two consequences matter in practice. The first is keys. Each ztunnel holds certificates only for the Pods on its "
            "own node, and an app container never sees a key. Istio's comparison page counts that as a security gain over "
            "sidecars. The second is that the waypoint label states an intent; it does not force anything. Istio's docs "
            "warn that traffic can bypass a waypoint, for example when the waypoint has no address yet. To make it "
            "mandatory, add a policy that ztunnel enforces on the workload and that allows only the waypoint's identity.\n\n"
            "Istio 1.31 added an Alpha feature that applies the canary idea to the mesh itself: a Service can point at a "
            "primary and a canary waypoint, with a weight. You can roll out a new waypoint config to a few percent of "
            "connections before every caller gets it. The [ambient data plane page](https://istio.io/latest/docs/ambient/"
            "architecture/data-plane/) draws these paths, and the [waypoint page](https://istio.io/latest/docs/ambient/usage/"
            "waypoint/) covers the labels."
        ),
    },
    "sources": [
        S("Istio: sidecar or ambient?", I_MODES["url"]),
        S("Istio: ambient mode overview", I_AMBIENT["url"]),
        S("Istio: security concepts", I_SEC["url"]),
        S("Istio task: fault injection", I_FAULT["url"]),
    ],
}

_unused = (E_FAULT, I_DATAPLANE, I_KIALI, I_KIND)
