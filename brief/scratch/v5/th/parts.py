"""Book-voice rewrite of the part fields of p14, p15 and p16 (intro, recap, flashcards, resources why, quiz q/why). Writer: th.
Only prose changes; options, answers, titles and URLs stay. Loads each file fresh right before writing."""
import sys
sys.path.insert(0, "/home/user/devops-from-zero/brief/scratch/v5/th")
from common import load, save

PARTS = {
    14: {
        "intro": "Parts 12 and 13 told you when hello-devops, our small lab app, is unwell, but not which request failed or where its time went. Logs and traces answer those two questions. Logs are the notes a program writes as it works, and a trace follows one request through every program it touches. Days 55 and 56 gather every log line into one searchable store, Elasticsearch, first on your laptop and then on a Kubernetes cluster. Day 57 puts a tracking number on every request with OpenTelemetry, without changing the app's code, and finds a slow call to Redis, the app's small database, in Jaeger.",
        "recap": [
            "Centralized logging copies every line to one searchable store, so logs outlive the containers that wrote them.",
            "Write structured JSON logs with a level, and never log secrets or personal data.",
            "Elasticsearch stores each event as a JSON document in an index and finds it through an inverted index of whole words (tokens).",
            "The mapping sets field types: text is split into words, keyword is matched whole, and the first guess sticks.",
            "A replica never shares a node with its primary, so a one-node cluster with replicas stays yellow.",
            "On Kubernetes, Fluent Bit runs as a DaemonSet, one copy per node, reading /var/log/containers and adding each pod's details.",
            "Index templates give new indices their mapping, and ILM deletes indices once they are old enough.",
            "A trace is a tree of timed spans that share a trace ID, carried between services in the traceparent header.",
            "OpenTelemetry makes the spans without code changes, and the Collector scrubs, samples and routes them to a backend such as Jaeger.",
            "Head sampling decides at the start of a trace; tail sampling in a Collector can keep every error and slow trace.",
        ],
        "flashcards": {
            8: ("Why run Fluent Bit as a DaemonSet?", "It puts one shipper on every node, and each one reads the log files of the pods on its node."),
        },
        "resources": {
            3: "Fluent Bit's creator explains where the project is going and how it handles logs, metrics and traces.",
        },
        "quiz": {},
    },
    15: {
        "intro": "Part 10 gave you Services and a Gateway, and Parts 12 to 14 showed you metrics, logs and traces. This part is about the calls between your services, and everything that can go wrong in them. Timeouts, retries, encryption with proof of identity, traffic splits and per-call numbers all belong there. Day 58 builds the intuition with one proxy, Envoy, that you set up by hand and break on purpose. Day 59 runs Istio, a full service mesh, and Day 60 compares Linkerd, Cilium and Consul and helps you decide whether you need a mesh at all.",
        "recap": [
            "A service mesh moves timeouts, retries, mTLS, traffic splits and per-call metrics out of app code and into proxies next to each service.",
            "In Envoy, listeners accept connections, the HTTP connection manager runs filters, routes pick clusters and clusters pick endpoints.",
            "Health checks probe hosts, outlier detection watches real answers, and circuit breakers fail fast. Keep retries few and short.",
            "A control plane sends Envoy its config over xDS while it runs; the admin port shows what each proxy really has.",
            "Istio is istiod plus either a sidecar per Pod or ambient mode: ztunnel per node and waypoints for HTTP.",
            "Workload identity comes from ServiceAccounts as SPIFFE IDs. Go PERMISSIVE, check every caller, then STRICT, then add AuthorizationPolicies.",
            "Linkerd has a small Rust sidecar and automatic mTLS; the project ships edge releases and vendors ship stable ones.",
            "Cilium does L3 and L4 in eBPF inside the kernel, runs Envoy per node for HTTP, and shows flows in Hubble.",
            "GAMMA HTTPRoutes attach to a Service and work across meshes.",
            "Measure what a mesh costs, and skip it while a few services do fine without one.",
        ],
        "flashcards": {
            6: ("How does a sidecar catch the app's traffic without code changes?", "Packet rules (iptables) in the Pod's network send connections to the proxy. Istio uses port 15001 out and 15006 in."),
        },
        "resources": {},
        "quiz": {},
    },
    16: {
        "intro": "In Parts 12 to 14 you put together your own tools to watch a system, one open-source program per kind of data. Dynatrace does the same job as one commercial product. Its agent collects the data, its store keeps every signal, and you read all of it with one query language. Day 61 explains how it thinks, using a free online sandbox. Day 62 gets your own data in and teaches that query language, DQL, from zero.",
        "recap": [
            "Dynatrace is a SaaS observability platform: one agent, one store (Grail), one query language (DQL).",
            "OneAgent instruments hosts and supported processes without code changes; ActiveGate relays data and reads APIs.",
            "Smartscape is a map of entities that Dynatrace draws itself, and every signal carries an entity ID that links them.",
            "Davis turns many related anomalies into one problem by walking dependencies and traces.",
            "Davis cannot see past anything nobody instruments, and it does not know your SLOs.",
            "Latest Dynatrace lives at <id>.apps.dynatrace.com; agents and APIs use <id>.live.dynatrace.com.",
            "On kind, the lab uses an applicationMonitoring DynaKube with a small ActiveGate, and it may fail on a Mac.",
            "DQL runs top to bottom; metrics come from timeseries, and SQL habits often return zero rows silently.",
            "Ingest, retention and query scans all cost money after the trial; learn in the Playground first.",
        ],
        "flashcards": {
            0: ("What does OneAgent do?", "It finds the programs running on a machine or in a pod and records metrics, logs and traces without code changes."),
            2: ("What is Smartscape?", "The live map of entities and how they depend on each other, drawn by Dynatrace from what OneAgent sees."),
        },
        "resources": {},
        "quiz": {},
    },
}

for part, P in PARTS.items():
    d = load(part)  # fresh load right before writing
    d["intro"] = P["intro"]
    d["recap"] = P["recap"]
    for i, (front, back) in P["flashcards"].items():
        d["flashcards"][i]["front"], d["flashcards"][i]["back"] = front, back
    for i, why in P["resources"].items():
        d["resources"][i]["why"] = why
    for i, (q, why) in P["quiz"].items():
        d["quiz"][i]["q"], d["quiz"][i]["why"] = q, why
    save(part, d)
    print("part", part, "done")
