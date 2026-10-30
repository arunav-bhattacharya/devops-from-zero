"""Day 48: Running EFK on Kubernetes."""
from common import lab, ref
import svg

L = {
    "id": "d48",
    "title": "Running EFK on Kubernetes",
    "minutes": 50,
    "goal": "By the end you can run Fluent Bit as a DaemonSet with Helm, explain how a pod's log line gets its Kubernetes metadata, and give your log indices a mapping and a retention policy.",
    "guess": {
        "q": "Your kind cluster has 3 nodes and 12 pods. You install Fluent Bit as a DaemonSet that tolerates every node. How many Fluent Bit pods run?",
        "options": [
            "1, shared by the whole cluster",
            "12, one next to each app pod",
            "3, one on each node",
            "As many as the autoscaler decides",
        ],
        "answer": 2,
        "why": "A DaemonSet runs one copy of its pod on every node it is allowed on, and that copy reads the log files of all pods on its node. Without the toleration in the lab's values, the control-plane node would be skipped and you would get 2.",
    },
    "terms": [
        {"term": "DaemonSet", "plain": "A Kubernetes workload that runs one copy of a pod on every node, or on every node it is allowed on."},
        {"term": "/var/log/containers", "plain": "The folder on each node where every container's output appears as a file, one file per container."},
        {"term": "Kubernetes filter", "plain": "The Fluent Bit filter that adds the pod name, namespace, labels and node to each log record."},
        {"term": "Multiline parser", "plain": "Rules that glue the lines of one event, such as a stack trace, back into one record."},
        {"term": "Index template", "plain": "A rule that gives every new index whose name matches a pattern its settings and mappings."},
        {"term": "Data stream", "plain": "One name for append-only, time-stamped data, backed by hidden indices that Elasticsearch rolls over for you."},
        {"term": "ILM", "plain": "Index lifecycle management: a policy that moves indices through phases such as hot and delete, by age or size."},
        {"term": "Retention", "plain": "How long you keep logs before they are deleted."},
    ],
    "sections": [
        {
            "h": "One shipper per node: the DaemonSet",
            "body": """On Day 47 Docker handed each line to Fluent Bit. Kubernetes works differently. The container runtime on each node writes every container's stdout and stderr to a file, and the kubelet links those files into one folder:

`/var/log/containers/<pod>_<namespace>_<container>-<container id>.log`

So the job is "read every file in that folder on every node". A DaemonSet does exactly that. It runs one copy of a pod on each node, and the Fluent Bit chart mounts the node's `/var/log` into that pod. Add a node and Kubernetes starts another Fluent Bit there by itself.

Why not a log sidecar in every app pod? It works, but 40 app pods would mean 40 shippers instead of one per node, each with its own memory and config. Per-node agents are the common choice, and Fluent Bit's documentation says to deploy it as a DaemonSet.

Each line in those files is wrapped by the runtime. Here is one from the lab test, with the JSON shortened:

`2026-10-30T10:15:02.123456789Z stdout F {"level":"INFO","path":"/","status":200}`

That is a timestamp, the stream, a flag and the message. The flag is `F` for a full line, or `P` for a partial line, used when the runtime splits a very long line. The `tail` input with `multiline.parser: docker, cri` unwraps this format and joins `P` pieces back together. In the test, a line split into a `P` and an `F` part came out as one record.

Two more tail settings matter:
- `db` stores how far each file was read, so a restarted Fluent Bit continues where it stopped.
- On first start, Fluent Bit reads new lines only, so send fresh traffic before you go looking for logs.""",
            "refs": [
                ref("Fluent Bit: Kubernetes installation", "https://docs.fluentbit.io/manual/installation/downloads/kubernetes", "docs"),
                ref("Fluent Bit: tail input", "https://docs.fluentbit.io/manual/pipeline/inputs/tail", "docs"),
                ref("Fluent Bit v3: unified layer for logs, metrics and traces (Eduardo Silva at KubeCon, CNCF)", "https://www.youtube.com/watch?v=4SqDRokC7ac", "watch"),
            ],
        },
        {
            "h": "Who wrote this line? The Kubernetes filter",
            "body": """A bare log line does not say which pod wrote it. The `kubernetes` filter adds that. It gets the pod name, namespace and container name from the file name, for free. For labels and annotations it asks the Kubernetes API about the pod, then caches the answer so it does not ask again for every line. The chart creates a ServiceAccount and a ClusterRole that allow those reads.

Here is what Fluent Bit made of the line above in a test run, trimmed to the interesting fields:

`{"stream":"stdout","level":"INFO","path":"/","status":200,"kubernetes":{"pod_name":"hello-devops-7c9f8b6d5-x2x4k","namespace_name":"hello","labels":{"app":"hello-devops"},"host":"devops-worker","container_name":"web"}}`

Three settings in the lab's values shape that record:
- `merge_log: on` checks whether the line is JSON and, if so, lifts its keys (`level`, `path`, `status`) into real fields.
- `keep_log: off` drops the original JSON string after that, so you do not store everything twice.
- `k8s-logging.exclude: on` lets a pod opt out. Add the annotation `fluentbit.io/exclude: "true"` to a chatty pod and its lines are dropped at the node.

In Kibana these fields become filters you will use every day: `kubernetes.namespace_name: hello`, `kubernetes.labels.app: hello-devops`, or `kubernetes.host` to see whether one node is the problem.

The API lookups are the part that can hurt at scale. A thousand nodes asking the API server about pods adds real load. The filter has a `use_kubelet` option that asks the local kubelet instead. Your three-node kind cluster does not need it.""",
            "refs": [
                ref("Fluent Bit: Kubernetes filter", "https://docs.fluentbit.io/manual/pipeline/filters/kubernetes", "docs"),
            ],
        },
        {
            "h": "Parsers and multiline logs",
            "body": """Parsing turns a string into fields. Fluent Bit has two kinds of parser, and you met both on Day 47:
- A parser reads one line, for example as JSON or with a regular expression, and turns it into fields. The lab's `json_line` parser does this for the access log.
- A multiline parser decides which lines belong together. Stack traces need this, because each line of a trace arrives as its own record.

Fluent Bit ships built-in multiline parsers for `docker`, `cri`, `go`, `java`, `json`, `python` and `ruby`. Treat them as a starting point and test them with your real logs. When I built the lab, the built-in `python` parser left Python 3.14 tracebacks in pieces. It expects each `File ...` line to be followed by exactly one code line, and newer Python versions add a third line of `^^^^` markers under the failing code.

So the lab defines its own rule, which is short:
1. A new event starts with `[` (gunicorn and Flask messages begin with a timestamp in brackets) or `{` (the JSON access log).
2. Any other line, including blank lines and `^^^^` lines, belongs to the event above it.

With that rule, one failed request became one 72-line document in Elasticsearch, with the traceback readable from top to bottom.

On Kubernetes there are two layers. `multiline.parser: docker, cri` on the tail input only joins lines the runtime split. Joining a stack trace is a second step, a `multiline` filter like the lab's. The best fix sits in the app: log errors as one JSON object with the stack trace inside one field, and nobody has to glue anything.""",
            "refs": [
                ref("Fluent Bit: multiline parsing", "https://docs.fluentbit.io/manual/pipeline/parsers/multiline-parsing", "docs"),
                ref("Fluent Bit: multiline filter", "https://docs.fluentbit.io/manual/pipeline/filters/multiline-stacktrace", "docs"),
            ],
        },
        {
            "h": "Index templates, data streams and lifecycle",
            "body": """Day 47 left two problems: dynamic mapping guesses, and indices that never go away. Elasticsearch has a tool for each.

An index template is a rule: every new index whose name matches `hello-logs-*` gets these settings and this mapping. It only acts when an index is created, so today's index keeps its old settings until tomorrow's index appears.

Index lifecycle management (ILM) handles age. A policy lists phases, and an index moves through them:
- hot: the index takes new writes and most searches.
- warm and cold: older data on cheaper or slower nodes, searched less.
- delete: the index is removed.

Each phase has a `min_age`. The lab's policy has only hot and delete, with delete at 7 days. Daily indices make this easy to reason about: the index for 30 October is deleted about a week later, and ILM checks every 10 minutes by default.

Data streams are Elastic's recommended way to store logs. You write to one name, for example `logs-hello-default`. Behind it sit hidden backing indices such as `.ds-logs-hello-default-2026.10.30-000001`, and only the newest one takes writes. A rollover starts a new backing index when the current one is old or big enough. Every document must have an `@timestamp`, and documents are append-only.

I tested this with Fluent Bit. Any name that matches `logs-*-*` picks up Elasticsearch's built-in `logs` template, which in 9.x uses logsdb mode. Elastic's benchmarks found logsdb cut log storage by up to 60%. But the built-in `logs` policy only rolls over at 30 days or 50 GB. It has no delete phase, so data stays until you add retention yourself. The course lab keeps daily indices plus your own ILM policy, because every part of it is visible.""",
            "refs": [
                ref("Elastic: index templates", "https://www.elastic.co/docs/manage-data/data-store/templates", "docs"),
                ref("Elastic: index lifecycle management", "https://www.elastic.co/docs/manage-data/lifecycle/index-lifecycle-management", "docs"),
                ref("Elastic: data streams", "https://www.elastic.co/docs/manage-data/data-store/data-streams", "docs"),
            ],
        },
        {
            "h": "What logs cost, and how to spend less",
            "body": """Logs are the signal that grows fastest, because every request writes at least one line. A simple way to think about the bill: what you store is roughly the daily volume, times one plus the number of replicas, times the days you keep it. Every one of those three is a lever.

Your lab already has a small example of waste. The hello-devops image has a Docker health check that calls `/healthz` every 30 seconds. That is 2,880 identical lines per container per day that nobody will read. On Kubernetes the kubelet's probes do the same, from the user agent `kube-probe`.

Ways to spend less, cheapest first:
1. Do not ship it. Drop noise at the node with a Fluent Bit `grep` filter, for example `exclude: path ^/healthz$`. Dropped lines cost nothing downstream.
2. Log less. Keep DEBUG off in production and avoid logging every loop iteration.
3. Keep it shorter. Seven days hot is plenty for many app logs. Audit logs may need a year, in a cheaper tier.
4. Copy it less. Low-value logs can live with zero replicas, if you accept losing them when a node dies.
5. Store it smaller. logsdb mode and good mappings, such as keyword instead of text where you never need full-text search, shrink indices.

Reliability is part of the cost too. If Elasticsearch is down, Fluent Bit buffers and retries. The lab's values retry without limit, so a short outage loses nothing. They also set `drop_unrecoverable_records: on`. A record Elasticsearch will never accept, such as one with a mapping conflict, is dropped instead of retried forever and blocking the queue behind it.""",
            "refs": [
                ref("Fluent Bit: grep filter", "https://docs.fluentbit.io/manual/pipeline/filters/grep", "docs"),
                ref("Elastic: logs data streams (logsdb)", "https://www.elastic.co/docs/manage-data/data-store/data-streams/logs-data-stream", "docs"),
            ],
        },
        {
            "h": "Kibana dashboards and alerts",
            "body": """Discover is for reading. Dashboards are for the questions you ask every day. In Kibana you build visualizations with Lens, mostly by dragging fields, and pin them to a dashboard. A useful first logging dashboard for hello-devops has three panels:
- failed requests over time, split by `status`
- the top paths by number of 5xx responses
- a saved Discover session with the newest ERROR lines

Logs can also alert. Kibana's Elasticsearch query rule runs a query on a schedule, compares the number of matches to a threshold and runs actions when the condition is met. The query can be ES|QL, KQL or Elasticsearch's JSON query language. A rule such as "more than 3 documents with `status >= 500` in 5 minutes" is a few clicks. Actions go through connectors, and the Elastic docs note that some connector types are paid features.

Should alerts come from logs or from metrics? Prefer metrics for rates and latency: Prometheus from Part 9 is cheaper and faster for those. Use log alerts for events that only exist in logs. Good examples are a specific error message, a failed login burst or a payment provider's error code. One alert source per symptom keeps on-call sane.""",
            "refs": [
                ref("Elastic: dashboards", "https://www.elastic.co/docs/explore-analyze/dashboards", "docs"),
                ref("Elastic: Elasticsearch query rule", "https://www.elastic.co/docs/explore-analyze/alerting/alerts/rule-type-es-query", "docs"),
            ],
        },
        {
            "h": "Loki or Elasticsearch?",
            "body": """Day 46 introduced Grafana Loki. It makes the opposite trade-off to Elasticsearch, so it is worth comparing them directly.

Elasticsearch indexes every word of every field. Any search, on any field, is fast, and so are aggregations such as "errors per path". You pay for that index in disk, memory and CPU.

Loki indexes only a small set of labels per log stream, such as `namespace` and `app`. The lines themselves are compressed into chunks in object storage such as S3. Loki's docs say this makes it less expensive to operate. The cost moves to query time: a search for a word inside the lines has to scan the chunks of every matching stream.

That leads to a different rule for each:
- In Loki, keep labels few and low in cardinality. Values such as user IDs or order IDs must not be labels, the same rule as Prometheus labels in Part 9.
- In Elasticsearch, put structure in fields, and watch the field count and the shard count.

How I would choose:
- Your team already runs Grafana and Prometheus, and most log questions start from "this service, this time window": start with Loki.
- You need fast free-text search across months of logs, heavy analytics on log fields, or security investigations: Elasticsearch or OpenSearch.

Many teams use both: Loki for everyday app logs, Elasticsearch for security and audit data. The shipper does not decide for you. Fluent Bit has outputs for both.""",
            "refs": [
                ref("Grafana Loki overview", "https://grafana.com/docs/loki/latest/get-started/overview/", "docs"),
            ],
        },
    ],
    "analogy": "A DaemonSet of Fluent Bit is like a mail room on every floor of an office building. Each floor's mail room collects the letters its offices put out, stamps each one with the sender's floor and department (the Kubernetes filter), and sends the sacks to one central archive (Elasticsearch). The archive's rules decide which shelf a letter goes on (the index template) and when old boxes go to the shredder (ILM). Where it breaks: real mail rooms do not need to ask head office who sits in which office, but Fluent Bit asks the Kubernetes API for pod labels, and in a very large building those questions add up.",
    "diagram": svg.d48(),
    "diagram_caption": "Every node runs its own Fluent Bit pod. It tails the node's container log files, adds labels from the Kubernetes API and ships to Elasticsearch outside the cluster.",
    "worked": {
        "title": "Give hello-logs a mapping and a 7-day retention",
        "steps": [
            {
                "say": "Start from the Day 47 lab with some logs in it. First the policy: indices stay hot, and are deleted once they are 7 days old. A policy does nothing until an index uses it.",
                "code": """$ curl -s -X PUT localhost:9200/_ilm/policy/hello-logs-7d -H 'Content-Type: application/json' -d '{
  "policy": {
    "phases": {
      "hot":    {"actions": {}},
      "delete": {"min_age": "7d", "actions": {"delete": {}}}
    }
  }
}'
{"acknowledged":true}""",
                "lang": "console",
            },
            {
                "say": "Now the template. It matches every future `hello-logs-*` index and sets three things: one shard, zero replicas (one node, so a replica could never be placed), and the ILM policy. The mapping replaces Day 47's guesses: `path` becomes a keyword and `status` a small number.",
                "code": """$ curl -s -X PUT localhost:9200/_index_template/hello-logs -H 'Content-Type: application/json' -d '{
  "index_patterns": ["hello-logs-*"],
  "priority": 200,
  "template": {
    "settings": {"number_of_shards": 1, "number_of_replicas": 0, "index.lifecycle.name": "hello-logs-7d"},
    "mappings": {"properties": {
      "@timestamp": {"type": "date"},   "level": {"type": "keyword"},
      "logger": {"type": "keyword"},    "method": {"type": "keyword"},
      "path": {"type": "keyword"},      "status": {"type": "short"},
      "duration_ms": {"type": "long"},  "log": {"type": "text"}
    }}
  }
}'
{"acknowledged":true}""",
                "lang": "console",
            },
            {
                "say": "Templates act only when an index is created, so today's index is still yellow with 1 replica. In this lab you can simply delete today's index (never do this to real data), and Fluent Bit creates a new one on its next write.",
                "code": """$ curl -s 'localhost:9200/_cat/indices/hello-logs-*?v&h=health,index,pri,rep,docs.count'
health index                 pri rep docs.count
yellow hello-logs-2026.10.30   1   1         79
$ curl -s -X DELETE localhost:9200/hello-logs-$(date -u +%Y.%m.%d)
{"acknowledged":true}""",
                "lang": "console",
            },
            {
                "say": "Send a few requests and look again. The new index got its settings from the template: zero replicas, so the cluster is green.",
                "code": """$ for i in 1 2 3; do curl -s -o /dev/null localhost:8000/readyz; done; sleep 3
$ curl -s 'localhost:9200/_cat/indices/hello-logs-*?v&h=health,index,pri,rep,docs.count'
health index                 pri rep docs.count
green  hello-logs-2026.10.30   1   0          4""",
                "lang": "console",
            },
            {
                "say": "Ask ILM what it thinks of the index. It is managed by `hello-logs-7d` and sits in the hot phase. It will move to delete once it is 7 days old.",
                "code": """$ curl -s 'localhost:9200/hello-logs-*/_ilm/explain?filter_path=indices.*.policy,indices.*.phase,indices.*.age,indices.*.managed&pretty'
{
  "indices" : {
    "hello-logs-2026.10.30" : {
      "managed" : true,
      "policy" : "hello-logs-7d",
      "age" : "9.38s",
      "phase" : "hot"
    }
  }
}""",
                "lang": "console",
            },
            {
                "say": "Finally, check the mapping did its job. `path` is a keyword now, so filters and counts on it are exact, and `status` is a number. Tomorrow's index gets the same mapping without anyone touching it.",
                "code": """$ curl -s 'localhost:9200/hello-logs-*/_mapping/field/path,status?filter_path=*.mappings.*.mapping'
{"hello-logs-2026.10.30":{"mappings":{"path":{"mapping":{"path":{"type":"keyword"}}},"status":{"mapping":{"status":{"type":"short"}}}}}}""",
                "lang": "console",
            },
        ],
    },
    "code": [
        {"lang": "yaml", "title": "logging/fluent-bit-values.yaml", "src": lab("logging/fluent-bit-values.yaml"),
         "run": "helm upgrade --install fluent-bit fluent/fluent-bit --namespace logging --create-namespace -f logging/fluent-bit-values.yaml"},
    ],
    "commands": [
        {"cmd": "helm repo add fluent https://fluent.github.io/helm-charts", "what": "Add the official Fluent Bit chart repository. The chart's README also shows an OCI install."},
        {"cmd": "helm template fluent-bit fluent/fluent-bit -f logging/fluent-bit-values.yaml | less", "what": "Preview the Kubernetes objects the chart would create, without installing anything."},
        {"cmd": "helm upgrade --install fluent-bit fluent/fluent-bit --namespace logging --create-namespace -f logging/fluent-bit-values.yaml", "what": "Install or upgrade Fluent Bit as a DaemonSet with the lab's values."},
        {"cmd": "kubectl -n logging get pods -o wide", "what": "Show the Fluent Bit pods and the node each one runs on. Expect one per node."},
        {"cmd": "kubectl -n logging logs daemonset/fluent-bit --tail=20", "what": "Read the last lines of one Fluent Bit pod. Connection or HTTP 400 errors show up here first."},
        {"cmd": "kubectl -n logging get configmap fluent-bit -o yaml", "what": "Show the config the chart really mounted, including your fluent-bit.yaml."},
        {"cmd": "kubectl -n hello set env deploy/hello-devops GUNICORN_CMD_ARGS=\"--access-logfile=-\"", "what": "Turn on gunicorn's access log in the cluster without editing any file."},
        {"cmd": "kubectl -n hello annotate pod <pod-name> fluentbit.io/exclude=\"true\"", "what": "Ask Fluent Bit to skip this pod's logs (needs `k8s-logging.exclude: on`)."},
        {"cmd": "curl -s 'localhost:9200/_cat/indices/k8s-logs-*?v'", "what": "Check that cluster logs arrive in Elasticsearch."},
        {"cmd": "curl -s 'localhost:9200/_cat/indices?v&s=store.size:desc'", "what": "List all indices, biggest first, to see where your disk goes."},
        {"cmd": "curl -s 'localhost:9200/_index_template/hello-logs?pretty'", "what": "Show the index template and the settings it gives new indices."},
        {"cmd": "curl -s 'localhost:9200/hello-logs-*/_ilm/explain?pretty'", "what": "Show which lifecycle policy and phase each index is in."},
        {"cmd": "helm uninstall fluent-bit -n logging", "what": "Remove Fluent Bit from the cluster."},
    ],
    "mistake": "Installing the Fluent Bit chart with its default config and waiting for logs. The default output sends to a host named `elasticsearch-master`, which only exists if you installed Elastic's old chart, and it does not set `suppress_type_name`. Against Elasticsearch 8 or 9 that answers HTTP 400 with `Action/metadata line [1] contains an unknown parameter [_type]`, and with unlimited retries Fluent Bit keeps trying forever. Always set the output yourself, and read one Fluent Bit pod's log with `kubectl logs` before you open Kibana.",
    "real_world": "A payments company runs Fluent Bit as a DaemonSet in every cluster with one shared Helm values file, so each service's logs arrive with the same Kubernetes fields. The platform team owns the index templates and lifecycle policies: application logs stay 14 days, while audit logs go to a separate data stream kept much longer in a cheaper tier. Teams that add a noisy debug log see it on the weekly 'biggest indices' report and fix it before it shows up on the bill.",
    "task": {
        "title": "Ship your kind cluster's logs to Elasticsearch",
        "steps": [
            "Start only Elasticsearch and Kibana from your `logging` folder, so the cluster has somewhere to send logs.",
            "Check that your kind cluster from Part 7 runs and that hello-devops pods are ready in the `hello` namespace.",
            "Add `logging/fluent-bit-values.yaml` to your repo, add the Fluent Bit chart repository, and install the chart into a new `logging` namespace.",
            "Confirm there is one Fluent Bit pod per node, and read one pod's log for errors.",
            "Turn on gunicorn's access log for hello-devops, wait for the rollout, then send 20 requests to http://localhost:8081/.",
            "In Kibana, create a data view for `k8s-logs-*` and filter Discover to the `hello` namespace.",
            "Pick one request and find which pod and which node served it.",
            "Stretch: drop the kubelet's probe requests at the node with a `grep` filter in the values file, upgrade the release, and check that new probe lines stop arriving.",
        ],
        "hints": [
            "If nothing arrives, the pod log usually says why: a host that does not resolve, or an HTTP error from Elasticsearch.",
            "Fluent Bit reads only lines written after it started, so make new traffic after installing.",
            "The kubelet's probes send the user agent `kube-probe`, and gunicorn's plain access log line contains it.",
        ],
        "done_when": "You are done when Discover shows a hello-devops access log line with `kubernetes.pod_name` and `kubernetes.host` filled in.",
    },
    "explain_back": {
        "prompt": "Explain to a teammate how a line printed by a hello-devops pod gets into Elasticsearch with its pod name attached, and how old logs get deleted, in 3 to 4 sentences. Mention the DaemonSet, the Kubernetes filter and ILM.",
        "answer": "The container runtime writes the pod's output to a file under /var/log/containers on its node, and the Fluent Bit pod that the DaemonSet runs on that node tails the file. The Kubernetes filter reads the pod name, namespace and container from the file name and asks the API server for the pod's labels, then adds them to the record. Fluent Bit sends the record to that day's k8s-logs index. An index template attaches an ILM policy to each new index, and ILM deletes the index once it is older than the retention we chose.",
    },
    "recap": [
        "Fluent Bit runs as a DaemonSet: one pod per node, tailing /var/log/containers.",
        "The tail input's docker and cri parsers unwrap the runtime's line format and join split lines.",
        "The Kubernetes filter adds pod, namespace, labels and node; merge_log lifts JSON keys into fields.",
        "Index templates give new indices their mapping and settings; ILM deletes them when they are old.",
        "Log cost is volume times copies times days: drop noise at the node first.",
        "Loki indexes labels only and is cheaper; Elasticsearch indexes everything and searches anything.",
    ],
    "check": [
        {
            "q": "You add a fourth node to your cluster. What happens to the Fluent Bit DaemonSet?",
            "options": [
                "Nothing until you raise its replica count to 4",
                "Kubernetes starts a Fluent Bit pod on the new node by itself",
                "One existing Fluent Bit pod starts reading the new node's files too",
                "You must reinstall the Helm chart so it sees the new node",
            ],
            "answer": 1,
            "why": "A DaemonSet has no replica count; it keeps one pod on every node it is allowed on, including new ones.",
        },
        {
            "q": "You change the index template so new hello-logs indices have 0 replicas. Today's index is still yellow. Why?",
            "options": [
                "Index templates only take effect after a restart of Elasticsearch",
                "The template's priority is too low to win against the default",
                "ILM has not reached the delete phase yet",
                "Templates apply only when an index is created, and today's index already existed",
            ],
            "answer": 3,
            "why": "Templates are read at index creation; existing indices keep their settings until you change them directly.",
        },
        {
            "q": "Your team often asks 'which requests mentioned order 8812 in the last 30 days?' across all services. Which store answers that fastest?",
            "options": [
                "Elasticsearch, because every word in the log lines is indexed",
                "Loki, because it stores lines in cheap object storage",
                "Loki, after adding the order ID as a label on every stream",
                "Prometheus, by adding order_id as a metric label",
            ],
            "answer": 0,
            "why": "Free-text search over a long window is what a full inverted index is for. Order IDs as Loki or Prometheus labels would explode cardinality.",
        },
    ],
    "interview": [
        {
            "q": "How would you collect logs from all pods in a Kubernetes cluster?",
            "a": "Apps write to stdout and stderr, and the runtime stores that in files under /var/log/containers on each node. I run a log agent such as Fluent Bit as a DaemonSet, so one pod per node tails those files with the docker and cri parsers. The Kubernetes filter adds namespace, pod, container and labels, and the output ships to a store such as Elasticsearch or Loki. I add an exclusion annotation for noisy pods, buffer and retry for outages, and alert when the agent itself reports errors.",
        },
        {
            "q": "Our logging bill doubled. Where do you start?",
            "a": "First I find where the volume comes from: the biggest indices, and the top services and messages by count. Most savings come from not shipping noise, such as health checks, debug logs and repeated lines, which I drop at the agent. Then I look at retention per log type, replica counts for low-value logs, and storage options such as logsdb or a cheaper tier for old data. I also agree on a rule with teams, such as a review for new high-volume log statements, so the bill does not drift back.",
        },
        {
            "q": "When would you pick Loki over Elasticsearch?",
            "a": "Loki indexes only labels and keeps compressed lines in object storage, so it is cheaper to run and fits teams that already use Grafana and Prometheus. It works best when queries start from a known service and time window. Elasticsearch indexes every word and field, which costs more but gives fast free-text search and analytics across long periods, useful for security and audit work. With high-cardinality values such as order IDs, Loki needs them in the log line, not in labels.",
        },
    ],
    "deeper": {
        "minutes": 12,
        "body": """You can point Fluent Bit at a data stream instead of daily indices, and it is a good way to see Elastic's defaults at work. I tested this trick against the lab. Keep `logstash_format: on`, so Fluent Bit still adds `@timestamp`, set `logstash_prefix: logs-hello` and `logstash_dateformat: default`. The date format is passed through as plain text, so every write goes to one name: `logs-hello-default`.

That name matches the `logs-*-*` pattern of Elasticsearch's built-in `logs` template, so the first write creates a data stream. Asking for it with `curl -s 'localhost:9200/_data_stream/logs-hello-default?pretty'` showed:
- backing index `.ds-logs-hello-default-2026.10.30-000001`
- template `logs`
- ILM policy `logs`
- index mode `logsdb`

The naming scheme is `type-dataset-namespace`. Here the type is `logs`, the dataset `hello`, and the namespace `default`. Elastic Agent and its integrations name their data streams the same way, which is why so many Kibana views look for `logs-*`.

Now read the policy behind it with `curl -s 'localhost:9200/_ilm/policy/logs?pretty'`. Its only phase is hot, with a rollover at 30 days or 50 GB per primary shard. There is no delete phase. A data stream on defaults keeps everything until the disk fills. To add retention, you either attach your own ILM policy with a delete phase, or use the data stream lifecycle, a simpler mechanism that takes a single `data_retention` value such as `7d`. Read Elastic's data stream lifecycle page before you mix the two: when an index is managed by ILM, ILM wins by default. I saw exactly that in the test. Setting `data_retention` on the stream was accepted, but the backing index still reported that ILM managed it.

Two practical differences from daily indices:
- You cannot delete "today's index" to pick up a new template, because writes always go to the stream. You trigger a rollover instead (`POST logs-hello-default/_rollover`), and the new backing index uses the current template.
- Data streams are append-only. If you ever need to update documents in place by `_id`, Elastic's docs point you back to aliases and plain indices.

For learning, daily indices show every moving part. For production on Elasticsearch 9, data streams with logsdb and an explicit retention are the default I would start from.""",
    },
    "sources": [
        {"title": "Fluent Bit: Kubernetes installation", "url": "https://docs.fluentbit.io/manual/installation/downloads/kubernetes"},
        {"title": "Fluent Bit: Kubernetes filter", "url": "https://docs.fluentbit.io/manual/pipeline/filters/kubernetes"},
        {"title": "Elastic: index lifecycle management", "url": "https://www.elastic.co/docs/manage-data/lifecycle/index-lifecycle-management"},
        {"title": "Elastic: data stream lifecycle", "url": "https://www.elastic.co/docs/manage-data/lifecycle/data-stream"},
    ],
}
