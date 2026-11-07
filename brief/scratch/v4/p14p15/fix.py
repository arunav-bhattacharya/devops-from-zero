#!/usr/bin/env python3
"""First-principles review fixes for Days 55 to 60 (content/p14.json, content/p15.json).
Exact old -> new replacements on prose fields only. Re-runnable: it always starts from
brief/scratch/v4/orig/pN.json and writes content/pN.json, and it stops if an old text
is not found exactly once."""
import json
import sys

SRC = "/home/user/devops-from-zero/brief/scratch/v4/orig/"
DST = "/home/user/devops-from-zero/content/"

# (lesson id, field, old, new). field: "sN" = section N body, "workedN" = worked step N say.
FIXES = [
    # ---------------- Day 55 ----------------
    ("d55", "s0",
     "In the lab, Docker itself hands each line to Fluent Bit. The compose file sets the `fluentd` logging driver on the web container, so the Docker engine sends every line to port 24224 as well as keeping its own copy.",
     "In the lab, Docker itself hands each line to Fluent Bit. Whatever a container prints goes to the Docker engine first, and a logging driver decides where the engine sends it. The default driver, `json-file`, writes it to a file that `docker logs` reads. The compose file sets the `fluentd` driver on the web container, so the engine sends every line to port 24224 and still keeps a local copy."),
    ("d55", "s0",
     "Without it, a container stops at once when it cannot reach its log collector.",
     "Without it, a container stops at once when it cannot reach its log collector.\n\n"
     "Fluent Bit itself is a pipeline, and the lab's `fluent-bit.yaml` has one block per stage:\n"
     "- Inputs take records in. `forward` listens on port 24224 for the Docker driver.\n"
     "- Filters change records. `multiline` glues a traceback into one record, and `parser` turns a JSON line into fields.\n"
     "- Outputs send records on. `es` writes to Elasticsearch, and `stdout` prints a copy.\n\n"
     "Each record carries a tag, here `hello.` plus the container name. Every filter and output has a `match` pattern and handles only the records whose tag fits it."),
    ("d55", "s0",
     "Every line every container prints is copied, as it is written, to one store you can search. The copy outlives the container, so the pod that handled the 14:02 payment can be gone and you can still read what it printed.",
     "Every line every container prints is copied, as it is written, to one store you can search. The pod that handled the 14:02 payment can be gone, and you can still read what it printed."),
    ("d55", "s2",
     "Search is fast because of the **inverted index**. When a document arrives, Elasticsearch splits each text field into words, called tokens, and lowercases them. Then it records, for every token, which documents contain it.",
     "With grep, every search reads every line again. That is fine for one file and far too slow for a week of logs from fifty pods. Elasticsearch does the reading once, when a document arrives, and builds an **inverted index**. A part called the analyzer splits each text field into words, called tokens, and lowercases them. Then Elasticsearch records, for every token, which documents contain it."),
    ("d55", "s3",
     "That guess is called dynamic mapping, and it sticks.",
     "That guess is called dynamic mapping, and it sticks. Every stored document was indexed for that type, so Elasticsearch never changes a field's type in place. You create a new index with the right mapping and copy the documents over, a reindex."),
    ("d55", "s4",
     "1. The number of primary shards is fixed when the index is created. The number of replicas can change at any time.\n2. Elasticsearch never puts a replica on the same node as its primary.",
     "1. The number of primary shards is fixed when the index is created. Elasticsearch picks each document's shard from a hash of its `_id` and the number of primaries, so a new number would send lookups to the wrong shard. Replicas can change at any time.\n2. Elasticsearch never puts a replica on the same node as its primary, because a copy on the same machine would die with it."),
    ("d55", "s5",
     "2. Elastic then switched to a choice of SSPL or the Elastic License, and neither counts as an open source licence.",
     "2. Elastic then switched to a choice of the Server Side Public License (SSPL) or the Elastic License, and neither counts as an open source licence."),
    ("d55", "s5",
     "4. In August 2024 Elastic added AGPLv3 as a third option.",
     "4. In August 2024 Elastic added the GNU Affero General Public License (AGPLv3), an open source licence, as a third option."),
    ("d55", "s6",
     "ES|QL mode needs no data view.",
     "ES|QL mode, the Elasticsearch Query Language, needs no data view."),

    # ---------------- Day 56 ----------------
    ("d56", "s0",
     "The container runtime on each node writes every container's stdout and stderr to a file, and the kubelet links those files into one folder:",
     "The container runtime on each node (containerd, Day 38) writes every container's stdout and stderr to a file, and the kubelet links those files into one folder:"),
    ("d56", "s0",
     "It runs one copy of a pod on each node, and the Fluent Bit chart mounts the node's `/var/log` into that pod.",
     "It runs one copy of a pod on each node. The Fluent Bit chart gives that pod a `hostPath` volume, which shows the node's own `/var/log` folder inside the container."),
    ("d56", "s0",
     "The `tail` input with `multiline.parser: docker, cri` unwraps this format and joins `P` pieces back together.",
     "The `tail` input follows files the way `tail -f` does (Day 4). With `multiline.parser: docker, cri` it unwraps this format and joins `P` pieces back together."),
    ("d56", "s1",
     "The chart creates a ServiceAccount and a ClusterRole that allow those reads.",
     "The chart creates a ServiceAccount and a ClusterRole that allow those reads (RBAC, Day 46)."),
    ("d56", "s3",
     "Data streams are Elastic's recommended way to store logs. You write to one name, for example `logs-hello-default`.",
     "Daily indices have a weakness: the shipper picks the index by date, so a quiet day makes a tiny index and a busy day a huge one. Data streams let Elasticsearch decide instead, and they are Elastic's recommended way to store logs. You write to one name, for example `logs-hello-default`."),
    ("d56", "s3",
     "which in 9.x uses logsdb mode.",
     "which in 9.x uses logsdb, an index mode built to store logs compactly."),

    # ---------------- Day 57 ----------------
    ("d57", "s1",
     "- a kind: server, client, internal, producer or consumer",
     "- a kind: server (it handled a call), client (it made one), internal, or producer and consumer for message queues"),
    ("d57", "s3",
     "and `app.py` stays untouched.\n\nSettings come from",
     "and `app.py` stays untouched.\n\n"
     "How do spans appear with no tracing code? `opentelemetry-instrument` starts the SDK before your app's code runs. Then each instrumentation library wraps functions of its own framework, such as Flask's request handling or the Redis client's command method. Every call to them now starts and ends a span.\n\n"
     "Settings come from"),
    ("d57", "s3",
     "For your JVM services the idea is the same: add the OpenTelemetry Java agent with `-javaagent:opentelemetry-javaagent.jar`, set the same variables, and Spring, JDBC and HTTP clients get spans.",
     "For your JVM services the idea is the same: add the OpenTelemetry Java agent with `-javaagent:opentelemetry-javaagent.jar` and set the same variables. The agent rewrites the bytecode of known libraries as their classes load, so Spring, JDBC and HTTP clients get spans."),
    ("d57", "s5",
     "and about 1 trace in 10 is kept.",
     "and about 1 trace in 10 is kept. Trace IDs are random, so the sampler can read each one as a number and keep the traces whose number falls in the lowest tenth."),

    # ---------------- Day 58 ----------------
    ("d58", "s1",
     "On the JVM you might use Resilience4j for retries and circuit breakers, plus your own TLS setup and a metrics library.",
     "On the JVM you might use Resilience4j for retries and circuit breakers (which stop calling a service that keeps failing), plus your own TLS setup and a metrics library."),
    ("d58", "s1",
     "and a second proxy on the receiving side does the same for incoming calls.",
     "and a second proxy on the receiving side does the same for incoming calls. The two proxies use mutual TLS (mTLS), the TLS of Day 11 with both sides showing a certificate, so each knows who the other is. Day 59 sets it up."),
    ("d58", "s2",
     "and sends the request over a pooled connection.",
     "and sends the request over a pooled connection, one that Envoy keeps open and reuses."),
    ("d58", "s2",
     "An Envoy cluster has nothing to do with a Kubernetes cluster. It is a group of upstream hosts for one service. Each of these objects is separate in the config.",
     "Many of Envoy's features are filters: plug-in steps that see the traffic, may change or answer it, and pass it on. An Envoy that only proxies L4 holds the TCP proxy filter where ours holds the HCM, and never parses HTTP. The router comes last because it is the filter that sends the request upstream, so nothing after it would run.\n\n"
     "An Envoy cluster has nothing to do with a Kubernetes cluster. It is a group of upstream hosts for one service. The lab lists host names such as `v1a`, and `type: STRICT_DNS` makes Envoy look them up in Compose's DNS (Day 20). Each of these objects is separate in the config."),
    ("d58", "s3",
     "- `retry_policy` retries on `5xx,reset,connect-failure`, at most twice, with `per_try_timeout: 1s` for each attempt.",
     "- `retry_policy` retries on `5xx,reset,connect-failure` (an error status, a dropped connection or a failed connect), at most twice, with `per_try_timeout: 1s` each."),
    ("d58", "s3",
     "Past a limit, Envoy answers 503 at once instead of letting a queue grow.",
     "Past a limit, Envoy answers 503 at once instead of letting a queue grow. A growing queue is how one slow service makes its callers slow too, because their threads and connections all sit waiting."),
    ("d58", "s4",
     "So Envoy can also fetch its config over gRPC from a server while it runs. These APIs are called xDS, one for each kind of object:",
     "So Envoy can also fetch its config from a server while it runs, over gRPC (a remote-call protocol on HTTP/2). Envoy still starts from a small static file, the bootstrap, which says where that server is. The rest arrives over APIs called xDS, one for each kind of object:"),
    ("d58", "s4",
     "The x stands for any of these letters. Many control planes send all of them over one stream, called ADS (the aggregated discovery service), so updates arrive in a safe order.",
     "The x stands for any of these letters. Order matters: a route that names a cluster Envoy has not received yet sends its traffic nowhere. So many control planes send everything over one stream, called ADS (the aggregated discovery service), clusters before the routes that use them."),
    ("d58", "s5",
     "Before the app starts, an init container or a CNI plugin on the node writes iptables rules inside the Pod's network. Istio's rules send outgoing connections to Envoy on port 15001 and incoming ones to port 15006. The app still calls `http://fraud-check/`, and the kernel quietly hands the connection to Envoy.",
     "Before the app starts, an init container or a CNI plugin on the node writes iptables rules inside the Pod's network. They are the same kernel packet rules kube-proxy writes (Day 41). Istio's rules send outgoing connections to Envoy on port 15001 and incoming ones to port 15006. The app still calls `http://fraud-check/`, and the kernel quietly hands the connection to Envoy.\n\n"
     "So how does Envoy know where the app meant to go? The kernel remembers the original address of every redirected connection, and Envoy reads it back. The rules also skip traffic sent by the proxy's own user (ID 1337 in Istio). Otherwise Envoy's outgoing calls would loop straight back into Envoy."),
    ("d58", "s5",
     "Kubernetes native sidecar containers fix this.",
     "Kubernetes native sidecar containers (Day 39) fix this."),

    # ---------------- Day 59 ----------------
    ("d59", "s0",
     "- It runs a certificate authority that gives every workload a short-lived certificate, valid for 24 hours by default.",
     "- It runs a certificate authority (a CA, the signer of certificates from Day 11) that gives every workload a short-lived certificate, valid for 24 hours by default."),
    ("d59", "s0",
     "- It runs the webhook that injects sidecars into new Pods.\n\nThe data plane comes in two modes.",
     "- It runs the webhook that injects sidecars into new Pods.\n\n"
     "That webhook is a mutating admission webhook, a Kubernetes hook for changing objects before they are stored. The API server sends each new Pod to istiod first, and istiod adds the Envoy container. Your Deployment's YAML never mentions the sidecar.\n\n"
     "The data plane comes in two modes."),
    ("d59", "s0",
     "Each proxy handles both L4 and L7, so every feature works everywhere.",
     "Each proxy handles both L4 and L7, so every feature works everywhere. The cost grows with the mesh: each sidecar is sized for its own Pod's busiest moment, and joining or upgrading means restarting every Pod."),
    ("d59", "s0",
     "Traffic between ztunnels and waypoints travels in an mTLS tunnel called HBONE, on port 15008.",
     "Traffic between ztunnels and waypoints travels in an mTLS tunnel called HBONE (HTTP-Based Overlay Network Environment), on port 15008. Most calls only need encryption and identity, which are cheap, so you pay for HTTP parsing only where you add a waypoint."),
    ("d59", "s0",
     "Istio now lists it as Stable for a single cluster, and multi-cluster ambient as Beta. Istio 1.31, released in August 2026, is the current version as I write this. The same page quotes Istio's latency tests, at p90 and p99:",
     "Istio's page comparing the two modes lists it as Stable for a single cluster, and multi-cluster ambient is Beta. Istio 1.31, released in August 2026, is the current version as I write this. The comparison page also quotes Istio's latency tests, at p90 and p99:"),
    ("d59", "s1",
     "- `ambient`: istiod, the Istio CNI node agent and ztunnel.",
     "- `ambient`: istiod, ztunnel and the Istio CNI node agent, which sets up rules that send each Pod's traffic to ztunnel."),
    ("d59", "s1",
     "ztunnel takes over the running Pods at once, with no restart and no extra container.",
     "ztunnel takes over the running Pods at once, with no restart and no extra container. The CNI node agent adds redirect rules inside each running Pod's network, and the Pod spec never changes."),
    ("d59", "s2",
     "The lab's `httproute-canary.yaml` attaches to the `hello-devops` Service, and the client's sidecar applies it to every call to `http://hello-devops`:",
     "The lab's `httproute-canary.yaml` attaches to the `hello-devops` Service. istiod turns it into Envoy routes in the client's sidecar, which applies them to every call to `http://hello-devops`:"),
    ("d59", "s4",
     "The identity comes from the Pod's ServiceAccount (Day 64). Istio writes it as a SPIFFE ID, a standard format for workload names:",
     "The identity comes from the Pod's ServiceAccount, the identity for programs from Day 46. Every Pod runs as one, `default` unless you name another. Istio writes it as a SPIFFE ID. SPIFFE, the Secure Production Identity Framework for Everyone, is a standard format for workload names:"),
    ("d59", "s4",
     "and renews them before they expire.\n\nPeerAuthentication says what a workload accepts:",
     "and renews them before they expire.\n\n"
     "The short life limits the damage of a stolen key, and nobody rotates certificates by hand. The SPIFFE ID sits inside the certificate, so the receiving proxy learns who is calling from the handshake itself, not from anything the app sent.\n\n"
     "PeerAuthentication says what a workload accepts:"),
    ("d59", "s4",
     "- DISABLE turns mTLS off. Avoid it.\n\nMove to STRICT in steps:",
     "- DISABLE turns mTLS off. Avoid it.\n\n"
     "In PERMISSIVE mode one port takes both. The receiving Envoy looks at the first bytes of each connection, and a TLS handshake is easy to tell from plain text. On the calling side, istiod tells each sidecar which destinations have a proxy, and the sidecar uses mTLS to those by itself.\n\n"
     "Move to STRICT in steps:"),
    ("d59", "worked1",
     "Its `envoy.yaml` already has a fault filter at 0 percent and a runtime layer that the admin port can change.",
     "Its `envoy.yaml` already has a fault filter at 0 percent and a runtime layer. That layer holds values the admin port can change while Envoy runs, and the fault filter reads them on every request."),

    # ---------------- Day 60 ----------------
    ("d60", "s0",
     "- The proxy injector adds the proxy to new Pods in namespaces annotated `linkerd.io/inject: enabled`.",
     "- The proxy injector is a mutating webhook, like Istio's (Day 59). It adds the proxy to new Pods in namespaces annotated `linkerd.io/inject: enabled`."),
    ("d60", "s0",
     "- Golden metrics for every workload: success rate, requests per second and latency.",
     "- Golden metrics for every workload: success rate, requests per second and latency, much like Day 49's golden signals."),
    ("d60", "s0",
     "- Load balancing per request, sending each one to the fastest endpoint by a moving average of latency. kube-proxy only balances connections (Day 41).",
     "- Load balancing per request, toward the fastest endpoints by a moving average of latency. Day 41's kube-proxy balances only connections, so one long-lived gRPC connection stays on one Pod."),
    ("d60", "s1",
     "expires after 365 days, and rotating it is real work.",
     "expires after 365 days. Linkerd's docs call a mesh with expired certificates invalid and give it a separate recovery guide. Rotating the anchor in time is work too. Every proxy has to trust the old and the new anchor side by side for a while, which takes several steps and Pod restarts."),
    ("d60", "s2",
     "- Between nodes, encryption with WireGuard or IPsec. That protects the wire, but it is not mTLS between workload identities.",
     "- Between nodes, encryption with WireGuard or IPsec, two standard ways to encrypt traffic between machines. That protects the wire, but it is not mTLS between workload identities."),
    ("d60", "s2",
     "Workload mTLS is where Cilium is still moving.",
     "Node encryption tells the receiver which node a packet came from. mTLS proves which workload sent it, with a certificate issued to that workload. Workload mTLS is where Cilium is still moving."),
    ("d60", "s3",
     "Since August 2023 Consul has been source-available under the Business Source License, so it is no longer open source.",
     "Since August 2023 Consul has been source-available under the Business Source License. You can read the code, but the license limits how you may use it, so it is no longer open source."),
    ("d60", "s5",
     "In sidecar mode you pay that for every Pod, and a sidecar's config grows with the mesh unless you limit what each proxy is told about.",
     "In sidecar mode you pay that for every Pod. By default an Istio sidecar also hears about every Service in the mesh, so its config grows with the mesh unless you limit it."),
    ("d60", "s5",
     "Istio publishes its own latency numbers on its sidecar-or-ambient page. It measured 0.63 to 0.88 ms per call for sidecars, and 0.16 to 0.20 ms for ambient mode without a waypoint.",
     "Istio's own numbers from Day 59 are 0.63 to 0.88 ms per call for sidecars and 0.16 to 0.20 ms for ambient mode without a waypoint."),

    # ---------------- trims to stay under 2,200 words ----------------
    ("d55", "s2",
     "If you are used to grep, which matches any substring, this gives you two surprises in the lab:",
     "Coming from grep, which matches any substring, you get two surprises in the lab:"),
    ("d55", "s5",
     "None of this changes what you do today. The lab images are free to run, and OpenSearch is close enough to Elasticsearch that today's ideas carry over.",
     "None of this changes the lab, and today's ideas carry over to OpenSearch."),
    ("d55", "s1",
     "A token in a log is a security incident. Deleting it later from every copy and backup is slow, painful work, so scrub at the source.",
     "A token in a log is a security incident, and deleting it later from every copy and backup is slow work. Scrub at the source."),
]


def get(L, field):
    if field.startswith("s"):
        return L["sections"][int(field[1:])], "body"
    if field.startswith("worked"):
        return L["worked"]["steps"][int(field[6:]) - 1], "say"
    return L, field


def main():
    parts = {}
    for f in ("p14.json", "p15.json"):
        parts[f] = json.load(open(SRC + f))
    lessons = {L["id"]: L for p in parts.values() for L in p["lessons"]}
    applied = 0
    for lid, field, old, new in FIXES:
        obj, key = get(lessons[lid], field)
        text = obj[key]
        n = text.count(old)
        if n != 1:
            sys.exit(f"{lid} {field}: old text found {n} times: {old[:70]!r}")
        obj[key] = text.replace(old, new)
        applied += 1
    for f, p in parts.items():
        with open(DST + f, "w") as fh:
            json.dump(p, fh, ensure_ascii=False, indent=1)
            fh.write("\n")
    print(f"applied {applied} of {len(FIXES)} fixes")


if __name__ == "__main__":
    main()
