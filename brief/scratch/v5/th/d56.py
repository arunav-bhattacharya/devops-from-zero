"""Book-voice rewrite of d56 (Running EFK on Kubernetes). Writer: th."""
import sys
sys.path.insert(0, "/home/user/devops-from-zero/brief/scratch/v5/th")
from common import apply, load, lesson

OPENING = """Picture the hospital from last time, a year later. It now has three floors and a dozen wards, and the central chart room works: every note reaches it. One morning a doctor pulls a note that says "fever at 3 a.m., gave medicine". Which patient? Which ward? The note does not say. The nurse who wrote it was standing at the bed and saw no reason to write that down. Down the hall, the room's manager has a second worry. The shelves are full, because nobody ever throws a chart away.

Both troubles grow quietly. A detail is obvious to the person who writes the note, and a shelf fills one page at a time.

Last time, we gathered the logs of one laptop into Elasticsearch. Today we do it for a Kubernetes cluster. We'll put one log collector on every machine, stamp each line with who wrote it, and give old logs a day to leave.

Before we start, make a guess, and keep it in mind."""

S1 = """Last time, Docker handed each line straight to Fluent Bit. Kubernetes works differently. Kubernetes is the system that runs containers (sealed boxes that each hold an app and all it needs) across a group of machines, called a cluster.

Each machine is a node. Each running copy of an app is a pod, Kubernetes' wrapper around one or more containers.

On every node, the container runtime (the program that actually starts containers) writes each container's output to a file. The kubelet, the Kubernetes helper on every node, links those files into one folder:

`/var/log/containers/<pod>_<namespace>_<container>-<container id>.log`

A namespace is a named area of the cluster, and hello-devops lives in `hello`. So the job is to read every file in that folder, on every node. In hospital terms, we need one records clerk on every floor.

A DaemonSet does exactly that: it runs one copy of a pod on each node. Add a node, and Kubernetes starts another copy there by itself.

We install Fluent Bit with Helm, the package installer for Kubernetes, whose packages are called charts. The Fluent Bit chart gives its pod a `hostPath` volume, a window that shows the node's own `/var/log` folder inside the container.

The naive first try is to install the chart with its default settings and wait. Nothing arrives. The default output sends to a host named `elasticsearch-master`, which only exists if you installed Elastic's old chart. It also does not set `suppress_type_name`. Elasticsearch 8 and 9 answer that output with HTTP 400 and `Action/metadata line [1] contains an unknown parameter [_type]`. With unlimited retries, Fluent Bit keeps trying forever, quietly. The lab's values file sets the output itself. **Before you open Kibana, read one shipper's own log. It tells you why nothing arrived.**

With the lab's values, lines flow, each one wrapped by the runtime. Here is one from the lab test, with the JSON shortened:

`2026-10-30T10:15:02.123456789Z stdout F {"level":"INFO","path":"/","status":200}`

That is a timestamp, the stream (stdout for normal output), a flag and the message. The flag is `F` for a full line, or `P` for a partial line, used when the runtime splits a very long line. The `tail` input follows files the way `tail -f` does (Day 4): it reads lines as they are added. With `multiline.parser: docker, cri` it unwraps this format and joins `P` pieces back together. In the test, a line split into a `P` and an `F` part came out as one record.

Two more habits of the tail input:
- `db` stores how far each file was read, so a restarted Fluent Bit continues where it stopped.
- On first start, Fluent Bit reads new lines only, so send fresh traffic before you go looking for logs.

Lines arrive now, but nothing in them says which pod wrote them. Next, we'll fix that."""

S2 = """A bare log line is a note with no ward and no bed number. The `kubernetes` filter stamps them on. It reads the pod name, namespace and container name from the file name, for free. Labels and annotations are short name and value tags that people attach to a pod. For those, the filter asks the Kubernetes API, the cluster's front desk for questions. Then it caches the answer, keeping it in memory so it does not ask again for every line. The chart also creates the permissions those reads need (RBAC, Day 46).

Here is what Fluent Bit made of the line above in a test run, trimmed to the interesting fields:

`{"stream":"stdout","level":"INFO","path":"/","status":200,"kubernetes":{"pod_name":"hello-devops-7c9f8b6d5-x2x4k","namespace_name":"hello","labels":{"app":"hello-devops"},"host":"devops-worker","container_name":"web"}}`

Three settings in the lab's values shape that record:
- `merge_log: on` checks whether the line is JSON and, if so, lifts its keys (`level`, `path`, `status`) into real fields.
- `keep_log: off` then drops the original JSON string, so you do not store everything twice.
- `k8s-logging.exclude: on` lets a pod opt out. Add the annotation `fluentbit.io/exclude: "true"` to a chatty pod, and its lines are dropped at the node.

In Kibana these fields become filters you will use every day: `kubernetes.namespace_name: hello`, `kubernetes.labels.app: hello-devops`, or `kubernetes.host` to see whether one node is the problem.

The questions to the API are the part that can hurt at scale. A thousand nodes asking the API server about pods adds real load. The filter has a `use_kubelet` option that asks the node's own kubelet instead. Your three-node kind cluster (kind runs a practice cluster inside Docker) does not need it.

Each line now says who wrote it. Next, we'll look at the lines that arrive in pieces."""

S3 = """Parsing turns a string of text into fields. Fluent Bit has two kinds of parser, and you met both last time:
- A parser reads one line, for example as JSON or with a regular expression (a text pattern), and turns it into fields. The lab's `json_line` parser does this for the access log.
- A multiline parser decides which lines belong together. Stack traces need this, because each line of a trace arrives as its own record.

A stack trace (Python calls it a traceback) is the report a program prints when it crashes. It lists the chain of code lines that led to the error, one per line. Fluent Bit ships built-in multiline parsers. They cover `docker`, `cri`, `go`, `java`, `json`, `python` and `ruby`. hello-devops is written in Python, so the obvious first try is the `python` parser.

In the lab test, that parser left Python 3.14 tracebacks in pieces. It expects each `File ...` line to be followed by exactly one code line. Newer Python versions add a third line of `^^^^` markers under the failing code, and the parser lost its place. Treat the built-in parsers as a starting point, and test them with your real logs.

So the lab defines its own rule, which is short:
1. A new event starts with `[` (gunicorn and app messages begin with a timestamp in brackets) or `{` (the JSON access log).
2. Any other line, including blank lines and `^^^^` lines, belongs to the event above it.

With that rule, one failed request became one 72-line document in Elasticsearch, with the traceback readable from top to bottom.

On Kubernetes there are two layers. `multiline.parser: docker, cri` on the tail input only joins lines that the runtime split. Joining a stack trace is a second step, a `multiline` filter like the one in last lesson's lab. The best fix sits in the app. Log each error as one JSON object with the stack trace inside one field, and nobody has to glue anything.

Our records are now whole and labelled. Next, we'll stop the store from filling up."""

S4 = """Last lesson left two problems: mapping guesses, and indices that never go away. In hospital terms, the records room needs a printed form for every new chart, and a rule for when old charts go to the shredder. Elasticsearch has a tool for each.

An index template is the form. It says: every new index whose name matches `hello-logs-*` gets these settings and this mapping. It acts only when an index is created, so today's index keeps its old settings until tomorrow's index appears.

Index lifecycle management (ILM) is the shredder rule. A policy lists phases, and an index moves through them:
- hot: the index takes new writes and most searches.
- warm and cold: older data on cheaper or slower nodes, searched less.
- delete: the index is removed.

Each phase has a `min_age`. How long you keep logs before they are deleted is called retention. The lab's policy has only hot and delete, with delete at 7 days. Daily indices make this easy to reason about: the index for 30 October is deleted about a week later. ILM checks every 10 minutes by default. **A store with no delete rule only grows. Give every index a retention.**

Daily indices have a weakness. The shipper picks the index by date, so a quiet day makes a tiny index and a busy day a huge one. A data stream lets Elasticsearch decide instead, and data streams are Elastic's recommended way to store logs. You write to one name, for example `logs-hello-default`. Behind it sit hidden backing indices such as `.ds-logs-hello-default-2026.10.30-000001`, and only the newest one takes writes. A rollover starts a new backing index when the current one is old or big enough. Every document must have an `@timestamp`. Documents are also append-only: you add new ones and never change old ones.

The lab test with Fluent Bit showed the defaults. Any name that matches `logs-*-*` picks up Elasticsearch's built-in `logs` template. In 9.x that template uses logsdb, an index mode built to store logs compactly, and Elastic's benchmarks found it cut log storage by up to 60%. But the built-in `logs` policy only rolls over at 30 days or 50 GB. It has no delete phase, so data stays until you add retention yourself. The course lab keeps daily indices plus your own ILM policy, because every part of it is visible.

Old logs now leave on time. Next, we'll ask what the ones we keep cost."""

S5 = """Logs are the signal that grows fastest, because every request writes at least one line. Roughly, what you store is the daily volume, times one plus the number of replicas, times the days you keep it. You can cut any of the three.

Your lab already has a small example of waste. The hello-devops image has a Docker health check that calls `/healthz` every 30 seconds. That is 2,880 identical lines per container per day that nobody will read. On Kubernetes the kubelet's probes, its own regular "are you alive?" calls, do the same. They send the user agent `kube-probe`, the name a caller gives to say what it is.

Ways to spend less, cheapest first:
1. Do not ship it. Drop noise at the node with a Fluent Bit `grep` filter, which keeps or drops records that match a pattern, for example `exclude: path ^/healthz$`. Dropped lines cost nothing downstream.
2. Log less. Keep DEBUG off in production and avoid logging every loop iteration.
3. Keep it shorter. Seven days hot is plenty for many app logs. Audit logs, the records of who did what, may need a year in a cheaper tier.
4. Copy it less. Low-value logs can live with zero replicas, if you accept losing them when a node dies.
5. Store it smaller. logsdb mode and good mappings, such as keyword instead of text where you never need full-text search, shrink indices.

Reliability is part of the cost too. If Elasticsearch is down, Fluent Bit buffers the records (holds them for later) and retries. The lab's values retry without limit, so a short outage loses nothing. They also set `drop_unrecoverable_records: on`. A record Elasticsearch will never accept, such as one with a mapping conflict, is dropped instead of retried forever. Otherwise it would block the queue behind it, like one stuck letter holding up the whole mail sack.

Next, we'll turn the logs we keep into answers people look at every day."""

S6 = """Discover is for reading. A dashboard is a page of charts for the questions you ask every day. In Kibana you build each chart, called a visualization, with Lens, mostly by dragging fields, and pin it to a dashboard as a panel. A useful first logging dashboard for hello-devops has three panels:
- failed requests over time, split by `status`
- the top paths by number of 5xx responses (the status codes from 500 to 599, all server failures)
- a saved Discover session with the newest ERROR lines

Logs can also raise alerts. Kibana's Elasticsearch query rule runs a query on a schedule, compares the number of matches to a threshold and runs actions when the condition is met. The query can be ES|QL, KQL or Elasticsearch's JSON query language. A rule such as "more than 3 documents with `status >= 500` in 5 minutes" takes a few clicks. Actions go through connectors, links to places such as email or chat. The Elastic docs note that some connector types are paid features.

Should alerts come from logs or from metrics? For rates and latency (how long requests take), use metrics: Prometheus from Part 12 is cheaper and faster for those. Use log alerts for events that only exist in logs, such as a specific error message, a burst of failed logins or a payment provider's error code. Whichever you pick, give each symptom one alert source, so the person on call is not paged twice for the same thing.

Next, we'll step back and compare Elasticsearch with the other log store you have met."""

S7 = """In "Grafana beyond dashboards" (Day 54) you met Grafana Loki, a log store that makes the opposite trade. Elasticsearch indexes every word of every field. Any search, on any field, is fast, and so are aggregations (summaries such as "errors per path"). You pay for that index in disk, memory and CPU, the computer's processing power.

Loki indexes only a small set of labels per log stream, such as `namespace` and `app`. A stream is all the lines that share the same labels. The lines themselves are compressed into chunks and kept in object storage, cheap storage for big files such as Amazon S3. Loki's docs say this makes it less expensive to operate. The cost moves to query time: a search for a word inside the lines has to scan the chunks of every matching stream.

That leads to a different rule for each:
- In Loki, keep labels few and low in cardinality, which means few possible values. User IDs or order IDs must not be labels, the same rule as Prometheus labels in Part 12.
- In Elasticsearch, put structure in fields, and watch the field count and the shard count.

How I would choose:
- Your team already runs Grafana and Prometheus, and most log questions start from "this service, this time window": start with Loki.
- You need fast free-text search across months of logs, heavy analytics on log fields, or security investigations: Elasticsearch or OpenSearch.

Many teams use both: Loki for everyday app logs, Elasticsearch for security and audit data. The shipper does not decide for you, because Fluent Bit has outputs for both.

Either store has the same limit. A log line tells you what one service saw. When a request passes through several services, no single line says where its time went. That needs a different signal, and it is the next lesson."""

CLOSING = """We began with a note that named no patient and shelves that never emptied. Now one Fluent Bit runs on every node, and each line carries its pod, namespace and node. A template and a policy give every new index its types and its last day. In your own cluster, run `kubectl -n logging get pods -o wide` to check that there is one Fluent Bit per node, then read one of their logs for errors.

Next, we'll follow one request through several services with tracing, and answer the question logs cannot: where did the time go?"""

ASIDE = {
    "title": "Why not a log shipper inside every app pod?",
    "body": "You could add a sidecar, a small helper container that runs next to the app inside each pod and ships its logs. It works. But 40 app pods would then mean 40 shippers instead of one per node, each with its own memory and its own settings to keep up to date. Per-node agents are the common choice, and Fluent Bit's documentation says to deploy it as a DaemonSet.",
    "after": 0,
}

L = lesson(load(14), "d56")
deeper = L["deeper"]["body"]
for a, b in [
    ("which shows you Elastic's defaults at work. I tested this against the lab. Keep", "which shows you Elastic's defaults at work. This was tested against the lab. Keep"),
    ("I saw exactly that in the test:", "The lab test showed exactly that:"),
]:
    if a in deeper:
        deeper = deeper.replace(a, b)
EXTRA = "\n\nTwo details from the lesson, for when you meet them: the chart creates a ServiceAccount and a ClusterRole, the Kubernetes objects that let the Kubernetes filter read pod details. And in kind, the container runtime that writes the log files is containerd (Day 38)."
if EXTRA.strip() not in deeper:
    deeper += EXTRA

new = {
    "goal": "By the end you can run Fluent Bit as a DaemonSet with Helm, explain how a pod's log line gets its Kubernetes details attached, and give your log indices a mapping and a retention policy.",
    "opening": OPENING,
    "guess": (
        "Your kind cluster has 3 nodes (machines) and 12 pods (running app copies). You install Fluent Bit as a DaemonSet that is allowed on every node. How many Fluent Bit pods run?",
        "A DaemonSet runs one copy of its pod on every node it is allowed on, and that copy reads the log files of all pods on its node. Without the toleration in the lab's values, the setting that lets it onto the control-plane node, that node would be skipped and you would get 2.",
    ),
    "terms": [
        "A Kubernetes workload that runs one copy of a pod on every node, or on every node it is allowed on.",
        "The folder on each node where every container's output appears as a file, one file per container.",
        "The Fluent Bit filter that adds the pod name, namespace, labels and node to each log record.",
        "Rules that glue the lines of one event, such as a stack trace, back into one record.",
        "A rule that gives every new index whose name matches a pattern its settings and mappings.",
        "One name for time-stamped data that is only ever added to. Behind it, Elasticsearch starts a fresh hidden index whenever the current one is old or big enough.",
        "Index lifecycle management: a policy that moves indices through phases such as hot and delete, by age or size.",
        "How long you keep logs before they are deleted.",
    ],
    "sections": [
        ("One collector on every node: the DaemonSet", S1),
        ("Who wrote this line? The Kubernetes filter", S2),
        ("Parsers, and a traceback that came apart", S3),
        ("Templates, data streams and a day for old logs to leave", S4),
        ("What logs cost, and how to spend less", S5),
        ("Kibana dashboards and alerts", S6),
        ("Loki or Elasticsearch?", S7),
    ],
    "aside": ASIDE,
    "diagram_caption": "Every node runs its own Fluent Bit pod. It reads the node's container log files, adds labels from the Kubernetes API and ships to Elasticsearch outside the cluster.",
    "say": [
        "Start from last lesson's lab with some logs in it. First the policy: indices stay hot, and are deleted once they are 7 days old. A policy does nothing until an index uses it.",
        "Now the template. It matches every future `hello-logs-*` index and sets three things: one shard, zero replicas (there is one node, so a replica could never be placed), and the ILM policy. The mapping replaces last lesson's guesses: `path` becomes a keyword and `status` a small number.",
        "Templates act only when an index is created, so today's index is still yellow with 1 replica. In this lab you can simply delete today's index (never do this to real data). Fluent Bit creates a new one on its next write.",
        "Send a few requests and look again. The new index got its settings from the template: zero replicas, so the cluster is green.",
        "Ask ILM what it thinks of the index. It is managed by `hello-logs-7d` and sits in the hot phase. It will move to delete once it is 7 days old.",
        "Finally, check that the mapping did its job. `path` is a keyword now, so filters and counts on it are exact, and `status` is a number. Tomorrow's index gets the same mapping without anyone touching it.",
    ],
    "task": (
        [
            "Start only Elasticsearch and Kibana from your `logging` folder, so the cluster has somewhere to send logs.",
            "Check that your kind cluster from Part 10 runs and that the hello-devops pods are ready in the `hello` namespace.",
            "Add `logging/fluent-bit-values.yaml` to your repo, add the Fluent Bit chart repository, and install the chart into a new `logging` namespace.",
            "Confirm there is one Fluent Bit pod per node, and read one pod's log for errors.",
            "Turn on gunicorn's access log for hello-devops, wait for the rollout (Kubernetes replacing the old pods with new ones), then send 20 requests to http://localhost:8081/.",
            "In Kibana, create a data view for `k8s-logs-*` and filter Discover to the `hello` namespace.",
            "Pick one request and find which pod and which node served it.",
            "Stretch: drop the kubelet's probe requests at the node with a `grep` filter in the values file, upgrade the release, and check that new probe lines stop arriving.",
        ],
        [
            "If nothing arrives, the pod's log usually says why: a host that does not resolve, or an HTTP error from Elasticsearch.",
            "Fluent Bit reads only lines written after it started, so make new traffic after installing.",
            "The kubelet's probes send the user agent `kube-probe`, and gunicorn's plain access log line contains it.",
        ],
        "You are done when Discover shows a hello-devops access log line with `kubernetes.pod_name` and `kubernetes.host` filled in.",
    ),
    "explain_back": (
        "Explain to a teammate how a line printed by a hello-devops pod gets into Elasticsearch with its pod name attached, and how old logs get deleted, in 3 to 4 sentences. Mention the DaemonSet, the Kubernetes filter and ILM.",
        "The container runtime writes the pod's output to a file under /var/log/containers on its node. The Fluent Bit pod that the DaemonSet runs on that node reads the file. The Kubernetes filter takes the pod name, namespace and container from the file name, asks the API server for the pod's labels, and adds them to the record. Fluent Bit then sends the record to that day's k8s-logs index. An index template attaches an ILM policy to each new index, and ILM deletes the index once it is older than the retention we chose.",
    ),
    "recap": [
        "Fluent Bit runs as a DaemonSet: one pod per node, reading the files in /var/log/containers.",
        "The tail input's docker and cri parsers unwrap the runtime's line format and join split lines.",
        "The Kubernetes filter adds pod, namespace, labels and node; merge_log lifts JSON keys into fields.",
        "Index templates give new indices their mapping and settings; ILM deletes them when they are old.",
        "Log cost is volume times copies times days: drop noise at the node first.",
        "Loki indexes only labels and is cheaper; Elasticsearch indexes everything. Neither shows where a request's time went.",
    ],
    "closing": CLOSING,
    "check": [
        ("You add a fourth node to your cluster. What happens to the Fluent Bit DaemonSet?",
         "A DaemonSet has no replica count. It keeps one pod on every node it is allowed on, including new ones."),
        ("You change the index template so new hello-logs indices have 0 replicas. Today's index is still yellow. Why?",
         "Templates are read when an index is created. Existing indices keep their settings until you change them directly."),
        ("Your team often asks 'which requests mentioned order 8812 in the last 30 days?' across all services. Which store answers that fastest?",
         "Free-text search over a long window is what a full inverted index is for. Order IDs as Loki or Prometheus labels would explode cardinality."),
    ],
    "interview": [
        ("How would you collect logs from all pods in a Kubernetes cluster?",
         "Apps write to stdout and stderr, and the runtime stores that in files under /var/log/containers on each node. I run a log agent such as Fluent Bit as a DaemonSet, so one pod per node reads those files with the docker and cri parsers. The Kubernetes filter adds namespace, pod, container and labels, and the output ships to a store such as Elasticsearch or Loki. I add an exclusion annotation for noisy pods, buffer and retry for outages, and alert when the agent itself reports errors."),
        ("Our logging bill doubled. Where do you start?",
         "First I find where the volume comes from: the biggest indices, and the top services and messages by count. Most savings come from not shipping noise, such as health checks, debug logs and repeated lines, which I drop at the agent. Then I look at retention per log type, replica counts for low-value logs, and storage options such as logsdb or a cheaper tier for old data. I also agree on a rule with teams, such as a review for new high-volume log statements, so the bill does not drift back."),
        ("When would you pick Loki over Elasticsearch?",
         "Loki indexes only labels and keeps compressed lines in object storage, so it is cheaper to run and fits teams that already use Grafana and Prometheus. It works best when queries start from a known service and time window. Elasticsearch indexes every word and field, which costs more but gives fast free-text search and analytics across long periods. That is useful for security and audit work. High-cardinality values such as order IDs belong in Loki's log line, not in its labels."),
    ],
    "deeper": deeper,
    "drop": ["analogy", "mistake", "real_world"],
}

apply(14, "d56", new)
