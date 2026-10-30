"""Day 46: Grafana beyond dashboards. Content for content/p10.json (built by build.py)."""
from d45 import lab

DOC_ALERT = "https://grafana.com/docs/grafana/latest/alerting/fundamentals/"
DOC_POLICY = "https://grafana.com/docs/grafana/latest/alerting/fundamentals/notifications/notification-policies/"
DOC_CP = "https://grafana.com/docs/grafana/latest/alerting/fundamentals/notifications/contact-points/"
DOC_GMRULE = "https://grafana.com/docs/grafana/latest/alerting/alerting-rules/create-grafana-managed-rule/"
TUT_ALERT2 = "https://grafana.com/tutorials/alerting-get-started-pt2/"
VID_ALERT = "https://www.youtube.com/watch?v=nI-_MEnFBQs"
DOC_LOKI_LABELS = "https://grafana.com/docs/loki/latest/get-started/labels/"
DOC_LOKI_BP = "https://grafana.com/docs/loki/latest/get-started/labels/bp-labels/"
DOC_LOGQL = "https://grafana.com/docs/loki/latest/query/"
DOC_LOGQ = "https://grafana.com/docs/loki/latest/query/log_queries/"
DOC_METRICQ = "https://grafana.com/docs/loki/latest/query/metric_queries/"
VID_LOGQL = "https://www.youtube.com/watch?v=57dQwcmqkpQ"
DOC_ALLOY = "https://grafana.com/docs/alloy/latest/introduction/"
DOC_ALLOY_DOCKER = "https://github.com/grafana/alloy/blob/main/docs/sources/reference/components/loki/loki.source.docker.md"
VID_ALLOY = "https://www.youtube.com/watch?v=d9zLeFuIFIk"
LOKI_QS = "https://grafana.com/docs/loki/latest/get-started/quick-start/tutorial/"
DOC_TEMPO = "https://grafana.com/docs/tempo/latest/"
DOC_PYRO = "https://grafana.com/docs/pyroscope/latest/introduction/"
LGTM_REPO = "https://github.com/grafana/docker-otel-lgtm"
VID_LGTM = "https://www.youtube.com/watch?v=0MPDPFt-t4I"
PRICING = "https://grafana.com/pricing/?pg=pricing"
DOC_ASCODE = "https://grafana.com/docs/grafana/latest/as-code/observability-as-code/"
DOC_GITSYNC = "https://grafana.com/docs/grafana/latest/as-code/observability-as-code/git-sync/key-concepts/"
TF_GH = "https://grafana.com/docs/grafana/latest/as-code/infrastructure-as-code/terraform/dashboards-github-action/"
SDK_REPO = "https://github.com/grafana/grafana-foundation-sdk"
GCX_REPO = "https://github.com/grafana/gcx"
VID_GITSYNC = "https://www.youtube.com/watch?v=FBfl9ga5zWs"
VID_G13 = "https://www.youtube.com/watch?v=giocvyAXO28"
UPGRADE13 = "https://github.com/grafana/grafana/blob/main/docs/sources/upgrade-guide/upgrade-v13/upgrade-v13.0/index.md"
PROMTAIL_DOC = "https://github.com/grafana/loki/blob/main/docs/sources/send-data/promtail/_index.md"

D46 = {
    "id": "d46",
    "title": "Grafana beyond dashboards: alerting, Loki and the LGTM stack",
    "minutes": 50,
    "goal": "By the end you can provision a Grafana alert with a contact point, add Loki and Alloy to the lab, query hello-devops logs with LogQL, and say what each part of the LGTM stack does.",
    "guess": {
        "q": "Loki stores the logs of every container in the lab. What does it put in its index so it can find lines fast?",
        "options": [
            "Only the labels on each stream, such as service and container",
            "Every word of every line, like a search engine does",
            "Only the lines whose level is WARNING or ERROR",
            "Nothing: every query reads all the stored logs",
        ],
        "answer": 0,
        "why": "Loki indexes only the labels. A query uses them to pick a few streams, then scans the compressed text of just those streams.",
    },
    "terms": [
        {"term": "Grafana alert rule", "plain": "Queries plus a condition that Grafana checks on a schedule; it fires when the condition stays true for the pending period."},
        {"term": "Contact point", "plain": "Where Grafana sends an alert notification, such as email, Slack, PagerDuty or a webhook."},
        {"term": "Notification policy", "plain": "A rule in a tree that matches alert labels and decides which contact point gets the alert, and when."},
        {"term": "Loki", "plain": "Grafana Labs' log store: it indexes only the labels of each log stream and keeps the text compressed."},
        {"term": "Log stream", "plain": "All the log lines in Loki that share exactly the same set of labels."},
        {"term": "LogQL", "plain": "Loki's query language: a stream selector in braces, then filters and parsers joined by a pipe."},
        {"term": "Grafana Alloy", "plain": "Grafana Labs' collector, built on the OpenTelemetry Collector, that gathers logs, metrics, traces and profiles and sends them on."},
        {"term": "LGTM stack", "plain": "Loki, Grafana, Tempo and Mimir: Grafana Labs' open-source tools for logs, dashboards, traces and metrics."},
    ],
    "sections": [
        {
            "h": "Grafana alerting: rules, contact points and policies",
            "body": (
                "Day 44 built alerting from Prometheus rules and Alertmanager. Grafana has alerting of its own, built on the same model, and it can watch any data source Grafana can query. The parts:\n"
                "- An alert rule: one or more queries, a condition, and how often to check. Grafana runs it on a schedule, every 30 seconds in the lab.\n"
                "- Alert instances: each series the query returns gets its own instance. A rule over `sum by (job)` makes one instance per job.\n"
                "- A **contact point**: where the message goes, such as email, Slack, PagerDuty or a webhook.\n"
                "- Notification policies: a tree that sends firing instances to contact points by their labels, like the Alertmanager routing tree.\n\n"
                "The lab's rule lives in `grafana/provisioning/alerting/hello-alerts.yaml` and has two steps. Query A asks Prometheus for the error ratio over 2 minutes. "
                "Expression C is a threshold: is A above 0.05? The rule fires when C is true.\n\n"
                "Each instance moves through states:\n"
                "1. Normal: C is false.\n"
                "2. Pending: C is true, but not yet for the whole pending period (`for: 1m`).\n"
                "3. Alerting: C stayed true for the period. The notification goes out, and the rule shows as Firing.\n"
                "4. Normal again: Grafana sends a resolved message.\n\n"
                "Grafana also needs to know what to do when the query returns nothing or fails. By default it raises separate `DatasourceNoData` and `DatasourceError` alerts. "
                "For an error ratio, no 5xx series at all is good news, so the lab sets `noDataState: OK`. "
                "Decide this for every rule, or the default can wake someone up because a query found no rows."
            ),
            "refs": [
                {"title": "Grafana docs: introduction to Grafana Alerting", "url": DOC_ALERT, "kind": "docs"},
                {"title": "Grafana docs: notification policies", "url": DOC_POLICY, "kind": "docs"},
                {"title": "Get started with Grafana Alerting: multi-dimensional alerts and how to route them (Grafana tutorial video)", "url": VID_ALERT, "kind": "watch"},
            ],
        },
        {
            "h": "Grafana alerting or Alertmanager?",
            "body": (
                "The lab now has two alerting systems, and both send to the same webhook. Which should a team use? The facts first:\n"
                "- Prometheus rules run next to the data. They keep working when Grafana is down, and they live as YAML in git, or as PrometheusRule objects on Kubernetes (Day 44).\n"
                "- Grafana-managed rules can query any data source, and even mix several in one rule. Think of a log count from Loki next to a metric from Prometheus, or a row from a SQL database.\n"
                "- Grafana rules have the no-data and error handling above, and a UI that people without PromQL can use.\n"
                "- Grafana can import Prometheus rule files (since 12.1) and an Alertmanager configuration (since 13.3), so you can move later.\n\n"
                "My default for a setup like this lab: keep the paging alerts that protect your SLO in Prometheus and Alertmanager, close to the data and independent of Grafana. "
                "Use Grafana alerting for what only Grafana can see, such as alerts on logs or on data in other databases. "
                "If a team keeps all its data in one hosted Grafana stack, putting every rule in Grafana is a fair choice too.\n\n"
                "Whatever you pick, don't define the same alert in both systems. One incident would then page twice, and people learn to ignore pages."
            ),
            "refs": [
                {"title": "Grafana docs: configure Grafana-managed alert rules", "url": DOC_GMRULE, "kind": "docs"},
                {"title": "Grafana tutorial: multi-dimensional alerts and routing", "url": TUT_ALERT2, "kind": "read"},
            ],
        },
        {
            "h": "Loki: labels pick the stream, the text stays cheap",
            "body": (
                "Loki is Grafana Labs' log store, and its main idea comes from Prometheus. Each log line carries a few labels, such as `service=\"web\"` and `container=\"observability-web-1\"`. "
                "All lines with the same labels form one **log stream**. Loki indexes only the labels. The text of each line is compressed into chunks and not indexed at all.\n\n"
                "That makes Loki cheap to run and quick at one kind of question: give me the lines from these streams in this time range, then search inside them. "
                "A query uses the labels to pick a few streams, then scans just their text. "
                "Elasticsearch (Part 11) indexes every word instead. That costs more disk and memory, and in return finds a word across all logs faster.\n\n"
                "The cardinality rule from Day 42 applies here too, because every new label value makes a new stream:\n"
                "- Good labels: service, environment, cluster, container.\n"
                "- Bad labels: request ID, user ID, IP address, anything with endless values.\n"
                "- Keep those values in the line itself, where a filter finds them.\n\n"
                "Loki's docs suggest no more than 10 to 15 labels, each with a small number of values.\n\n"
                "Loki also adds a `service_name` label by itself. It copies the value from a label such as `service`, `app` or `container`. "
                "The lab's Alloy sets `service` to the Compose service name, so `{service_name=\"web\"}` finds the app's logs."
            ),
            "refs": [
                {"title": "Loki docs: understand labels", "url": DOC_LOKI_LABELS, "kind": "docs"},
                {"title": "Loki docs: label best practices", "url": DOC_LOKI_BP, "kind": "docs"},
            ],
        },
        {
            "h": "LogQL, one step at a time",
            "body": (
                "LogQL is Loki's query language, and it borrows a lot from PromQL. A query starts with a stream selector in braces, then an optional pipeline of steps joined by `|`. All of these ran against the lab:\n"
                "1. `{service_name=\"web\"}` returns every line from the app.\n"
                "2. `{service_name=\"web\"} != \"/healthz\"` drops lines containing `/healthz`. The `|=` filter keeps lines containing a string, and `|~` takes a regular expression.\n"
                "3. `{service_name=\"web\"} | json` parses each JSON line, so `method`, `path`, `status` and `duration_ms` become labels for this query only.\n"
                "4. `{service_name=\"web\"} | json | status >= 500` keeps only the failed requests.\n"
                "5. Adding `| line_format \"{{.method}} {{.path}} -> {{.status}}\"` rewrites each line as `GET / -> 500`, easier to scan.\n\n"
                "Put line filters before the parser. A plain text filter is the cheapest step, and every line it drops is a line the parser never touches.\n\n"
                "LogQL can also turn logs into numbers, which you can graph next to the Prometheus panels:\n"
                "- `count_over_time({service_name=\"web\"}[5m])` counts lines per stream over 5 minutes.\n"
                "- `rate({service_name=\"web\"}[5m])` gives lines per second.\n"
                "- `sum by (status) (count_over_time({service_name=\"web\"} | json | __error__=\"\" [5m]))` counts requests by status code.\n"
                "- `quantile_over_time(0.95, {service_name=\"web\"} | json | __error__=\"\" | unwrap duration_ms [5m])` reads a number out of each line and gives a p95.\n\n"
                "The `__error__=\"\"` part matters in the lab. When Redis is down, the app prints a Python traceback, and those lines are not JSON. "
                "The parser marks them with an `__error__` label, and a metric query refuses to run until you drop them."
            ),
            "refs": [
                {"title": "Loki docs: log queries", "url": DOC_LOGQ, "kind": "docs"},
                {"title": "Loki docs: metric queries", "url": DOC_METRICQ, "kind": "docs"},
                {"title": "How to query Grafana Loki with LogQL (Nicole van der Hoeven, Grafana developer advocate)", "url": VID_LOGQL, "kind": "watch"},
            ],
        },
        {
            "h": "Alloy: the collector in the middle",
            "body": (
                "Something has to read the logs and push them to Loki. In the lab that is Grafana Alloy, Grafana Labs' collector. "
                "It is a distribution of the OpenTelemetry Collector with Prometheus pipelines built in, and it handles metrics, logs, traces and profiles. "
                "Promtail, the older log shipper in many tutorials, reached [end of life](" + PROMTAIL_DOC + ") on 2 March 2026, so new setups use Alloy.\n\n"
                "An Alloy config is a set of components wired together. Each block has a type and a name and passes its output to the next. The lab's `loki/config.alloy` has four:\n"
                "1. `discovery.docker` asks Docker which containers run, and keeps only this Compose project.\n"
                "2. `discovery.relabel` picks the labels: `service` from the Compose service name, `container` from the container name.\n"
                "3. `loki.source.docker` follows each container's output, like `docker logs -f`.\n"
                "4. `loki.write` pushes the lines to Loki's API.\n\n"
                "Alloy talks to Docker through its socket, `/var/run/docker.sock`, mounted into the container. On a Mac this needs the Docker Desktop option \"Allow the default Docker socket to be used\", which you turned on during Day 2. "
                "The Alloy UI on http://localhost:12345 draws the pipeline and shows whether each component is healthy. Look there first when logs don't arrive.\n\n"
                "One more change makes the logs worth having. Gunicorn doesn't log requests by default. "
                "The override file `compose.loki.yaml` sets `GUNICORN_CMD_ARGS` on the `web` service, which turns on the access log. You get one JSON line per request, in the same format as the Part 11 logging lab. "
                "Compose merges that setting into the `web` service from `compose.yaml`, so you don't edit the Part 9 file."
            ),
            "refs": [
                {"title": "Grafana Alloy docs: introduction", "url": DOC_ALLOY, "kind": "docs"},
                {"title": "Alloy reference: loki.source.docker", "url": DOC_ALLOY_DOCKER, "kind": "docs"},
                {"title": "Introducing Grafana Alloy, a distribution of the OTel Collector (video)", "url": VID_ALLOY, "kind": "watch"},
            ],
        },
        {
            "h": "Traces, profiles and the LGTM stack",
            "body": (
                "Grafana Labs builds an open-source backend for each signal from Day 41. Together they are called the LGTM stack:\n"
                "- Loki for logs.\n"
                "- Grafana for dashboards, exploring and alerting.\n"
                "- Tempo for traces. It needs only object storage to run, and you find traces by ID or with its query language, TraceQL.\n"
                "- Mimir for metrics. It speaks the Prometheus API and keeps long-term data for many Prometheus servers (Day 44).\n\n"
                "Pyroscope adds profiles. A profile shows which functions use the CPU and memory, drawn as a flame graph: the wider a function's bar, the more time it took. "
                "A trace tells you which service is slow, and a profile tells you which code inside it.\n\n"
                "The signals are worth most when you can jump between them. If the app writes its trace ID into each log line, Grafana can link a slow span in Tempo to its log lines in Loki, and back. "
                "Day 49 adds tracing with OpenTelemetry, which is how trace IDs get into the app.\n\n"
                "To see everything on a laptop without building a stack, Grafana publishes one container with all of it inside, `grafana/otel-lgtm`. "
                "It serves Grafana on port 3000 and takes OpenTelemetry data on ports 4317 and 4318. It is meant for development and demos, not production.\n\n"
                "If you'd rather run nothing, Grafana Cloud hosts the whole stack. Its free tier currently lists 10,000 active metric series, 50 GB of logs, 14 days of retention and 3 users. "
                "Those limits change, so check the [pricing page](" + PRICING + ") before you rely on them."
            ),
            "refs": [
                {"title": "docker-otel-lgtm: the whole stack in one container", "url": LGTM_REPO, "kind": "docs"},
                {"title": "Grafana Tempo docs", "url": DOC_TEMPO, "kind": "docs"},
                {"title": "OpenTelemetry Looks Good To Me: Loki, Grafana, Tempo, Mimir (video)", "url": VID_LGTM, "kind": "watch"},
            ],
        },
        {
            "h": "Dashboards and alerts as code, and what changed in Grafana 12 and 13",
            "body": (
                "Day 45 provisioned dashboards from files. That works well for a Grafana you start yourself. Teams with many instances, or a hosted one, use one of these:\n"
                "- Terraform. The `grafana/grafana` provider manages folders, data sources, alert rules and dashboards. A `grafana_dashboard` resource can read your JSON with `config_json = file(\"hello-red.json\")`, so Part 6 carries over.\n"
                "- The Foundation SDK. Typed builders in Go, TypeScript, Python, Java and PHP that write dashboard JSON for you, with autocomplete instead of hand-edited JSON.\n"
                "- Git Sync, generally available since Grafana 13.0. Grafana connects to a GitHub, GitLab or Bitbucket repository, saving in the UI can open a pull request, and merged changes flow back. It covers dashboards and folders.\n"
                "- gcx, Grafana's new command-line tool for resources as code. It replaces Grizzly and grafanactl, which are deprecated, so skip tutorials that use them.\n"
                "- The Grafana Operator, for teams that want dashboards as Kubernetes custom resources.\n\n"
                "Pick one per team. For this course, file provisioning plus Terraform is plenty.\n\n"
                "Grafana 12 and 13 also changed things that make older tutorials wrong:\n"
                "- 12.0 removed Angular plugins, so some old panels no longer load.\n"
                "- 13.0 removed the `grafana-cli` and `grafana-server` commands. Use `grafana cli` and `grafana server`.\n"
                "- 13.0 made dynamic dashboards generally available: tabs, rows that show or hide themselves, and automatic layout, in the v2 dashboard format.\n"
                "- 13.3 added Notebooks for investigations, and variables you define once and share across dashboards.\n"
                "- The `grafana/grafana-oss` image stopped at 12.4. Use `grafana/grafana`."
            ),
            "refs": [
                {"title": "Grafana docs: observability as code", "url": DOC_ASCODE, "kind": "docs"},
                {"title": "Git Sync: observability as code built for scale (video)", "url": VID_GITSYNC, "kind": "watch"},
                {"title": "Grafana docs: upgrade to v13.0 (source on GitHub)", "url": UPGRADE13, "kind": "docs"},
            ],
        },
    ],
    "analogy": (
        "Loki works like a library that catalogs books only by shelf: subject, author and year, never the words inside. "
        "To find a quote, you walk to the right shelf and flip through the few books there. "
        "The catalog stays tiny, and flipping is fast when the shelf is small. "
        "Where it breaks: if you make a shelf for every reader's name, the catalog becomes larger than the books, which is exactly what a user ID label does to Loki."
    ),
    "diagram": (
        '<svg viewBox="0 0 560 228" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Alloy reads container logs and pushes them to Loki; Prometheus scrapes the containers; Grafana queries Loki with LogQL and Prometheus with PromQL, and sends alerts to a webhook">'
        '<rect class="bx" x="16" y="32" width="120" height="44" rx="10"/>'
        '<text class="t" x="76" y="59" font-size="13" text-anchor="middle">Containers</text>'
        '<rect class="bxp" x="168" y="32" width="90" height="44" rx="10"/>'
        '<text class="tk" x="213" y="59" font-size="13" text-anchor="middle">Alloy</text>'
        '<rect class="bxt" x="290" y="32" width="80" height="44" rx="10"/>'
        '<text class="tk" x="330" y="59" font-size="13" text-anchor="middle">Loki</text>'
        '<rect class="bxo" x="410" y="32" width="130" height="44" rx="10"/>'
        '<text class="tk" x="475" y="59" font-size="13" text-anchor="middle">Grafana</text>'
        '<rect class="bxt" x="196" y="164" width="124" height="44" rx="10"/>'
        '<text class="tk" x="258" y="191" font-size="13" text-anchor="middle">Prometheus</text>'
        '<rect class="bx" x="420" y="164" width="110" height="44" rx="10"/>'
        '<text class="t" x="475" y="191" font-size="13" text-anchor="middle">Webhook</text>'
        '<line class="ln" x1="136" y1="54" x2="165" y2="54" marker-end="url(#ar)"/>'
        '<text class="ts" x="152" y="24" font-size="11" text-anchor="middle">logs</text>'
        '<line class="ln" x1="258" y1="54" x2="287" y2="54" marker-end="url(#ar)"/>'
        '<text class="ts" x="274" y="24" font-size="11" text-anchor="middle">push</text>'
        '<line class="ln" x1="407" y1="54" x2="373" y2="54" marker-end="url(#ar)"/>'
        '<text class="ts" x="390" y="24" font-size="11" text-anchor="middle">LogQL</text>'
        '<line class="ln" x1="440" y1="78" x2="324" y2="166" marker-end="url(#ar)"/>'
        '<text class="ts" x="400" y="130" font-size="11" text-anchor="start">PromQL</text>'
        '<line class="ln" x1="500" y1="78" x2="500" y2="161" marker-end="url(#ar)"/>'
        '<text class="ts" x="508" y="124" font-size="11" text-anchor="start">alerts</text>'
        '<line class="lnd" x1="196" y1="176" x2="90" y2="80" marker-end="url(#ar)"/>'
        '<text class="ts" x="112" y="140" font-size="11" text-anchor="middle">scrape</text>'
        '</svg>'
    ),
    "diagram_caption": "Logs flow through Alloy into Loki; Grafana queries Loki and Prometheus side by side and sends the alerts.",
    "code": [
        {"lang": "yaml", "title": "observability/grafana/provisioning/alerting/hello-alerts.yaml",
         "src": lab("grafana/provisioning/alerting/hello-alerts.yaml"),
         "run": "curl -X POST -u admin:admin localhost:3000/api/admin/provisioning/alerting/reload"},
        {"lang": "yaml", "title": "observability/compose.loki.yaml",
         "src": lab("compose.loki.yaml"),
         "run": "docker compose -f compose.yaml -f compose.loki.yaml up -d"},
        {"lang": "yaml", "title": "observability/loki/loki.yaml",
         "src": lab("loki/loki.yaml"),
         "run": "curl localhost:3100/ready"},
        {"lang": "text", "title": "observability/loki/config.alloy",
         "src": lab("loki/config.alloy"),
         "run": "open http://localhost:12345"},
        {"lang": "yaml", "title": "observability/grafana/provisioning/datasources/loki.yaml",
         "src": lab("grafana/provisioning/datasources/loki.yaml"),
         "run": "curl -X POST -u admin:admin localhost:3000/api/admin/provisioning/datasources/reload"},
    ],
    "commands": [
        {"cmd": "docker compose -f compose.yaml -f compose.loki.yaml up -d", "what": "Start the lab with Loki and Alloy added; Compose merges the two files."},
        {"cmd": "docker compose -f compose.yaml -f compose.loki.yaml config", "what": "Print the merged configuration, to see what the override changed."},
        {"cmd": "curl localhost:3100/ready", "what": "Check that Loki is ready. Right after a start it says to wait about 15 seconds."},
        {"cmd": "curl -s localhost:3100/loki/api/v1/labels | jq", "what": "List the label names Loki has seen."},
        {"cmd": "curl -s -G localhost:3100/loki/api/v1/query_range --data-urlencode 'query={service_name=\"web\"} | json | status >= 500' | jq -r '.data.result[].values[][1]'", "what": "Run a LogQL query from the terminal and print the matching lines."},
        {"cmd": "open http://localhost:12345", "what": "Open the Alloy UI to see its components and whether each is healthy."},
        {"cmd": "curl -X POST -u admin:admin localhost:3000/api/admin/provisioning/datasources/reload", "what": "Make Grafana read the data source files again, without a restart."},
        {"cmd": "curl -X POST -u admin:admin localhost:3000/api/admin/provisioning/alerting/reload", "what": "Make Grafana read the alerting files again after an edit."},
        {"cmd": "curl -s -u admin:admin localhost:3000/api/prometheus/grafana/api/v1/rules | jq '.data.groups[].rules[] | {name, state}'", "what": "Show each Grafana-managed rule and whether it is inactive, pending or firing."},
        {"cmd": "docker compose logs -f webhook", "what": "Watch the notifications that Grafana and Alertmanager send to the lab's webhook."},
        {"cmd": "docker run --rm -p 3001:3000 -p 4317:4317 -p 4318:4318 grafana/otel-lgtm", "what": "Try the whole LGTM stack in one container, with Grafana on port 3001 (for demos only)."},
        {"cmd": "docker compose -f compose.yaml -f compose.loki.yaml down", "what": "Stop everything, including Loki and Alloy. Add -v to delete stored logs and metrics."},
    ],
    "mistake": (
        "Putting a request ID, user ID or full URL into a Loki label to make it easy to search. Each new value makes a new stream, and Loki slows down and fills its index with tiny chunks. "
        "Keep labels to a few values such as service and environment, leave the IDs in the line, and find them with a filter such as `|= \"req-42\"` or `| json | user_id=\"42\"`."
    ),
    "real_world": (
        "At the fake payments company PayFlow, Prometheus and Alertmanager page on-call for the checkout SLO. Grafana alerting handles the rest, such as a rule that counts `card declined` lines in Loki per merchant. "
        "Every Grafana rule and contact point lives in Terraform next to the dashboards, so a new team gets its alerts by pull request, not by clicking."
    ),
    "task": {
        "title": "Add Loki to the lab and investigate an outage from the logs",
        "steps": [
            "Create `compose.loki.yaml`, `loki/loki.yaml`, `loki/config.alloy` and `grafana/provisioning/datasources/loki.yaml` from this lesson's Files section.",
            "Start the stack with both Compose files, wait until Loki says ready, and open the Alloy UI to check that every component is healthy.",
            "Make Grafana read the new data source (reload API or restart), then open Explore, pick Loki and run `{service_name=\"web\"}` while your traffic loop runs.",
            "Write three LogQL queries: all requests except `/healthz`, only failed requests, and requests per second by status code.",
            "Stop Redis for two minutes. Use Loki to find the exception message that explains the 500s, and note its exact text.",
            "Add a panel to a scratch dashboard that graphs your requests-by-status query from Loki next to the Prometheus error ratio, and compare the shapes.",
            "Create a second Grafana alert rule in the UI from a Loki query that fires when more than 5 lines contain `ConnectionError` in 5 minutes. Watch it fire while Redis is down.",
            "Start Redis again and check that both Grafana alerts resolve in the webhook output.",
        ],
        "hints": [
            "If Loki returns nothing, check the Alloy UI first, then `docker compose -f compose.yaml -f compose.loki.yaml logs alloy`.",
            "A metric query over JSON lines needs `| __error__=\"\"` after `| json`, because the traceback lines are not JSON.",
            "For the alert, the query is shaped like `sum(count_over_time({service_name=\"web\"} |= \"...\" [5m]))`, with a threshold above 5.",
        ],
        "done_when": "In Explore, `sum by (status) (count_over_time({service_name=\"web\"} | json | __error__=\"\" [5m]))` shows a `500` series from your outage, and the webhook printed a FIRING and a RESOLVED line from your Loki alert.",
    },
    "explain_back": {
        "prompt": "Explain to a teammate, in 3 to 4 sentences, how a log line from hello-devops ends up on your screen in Grafana, and why Loki labels must stay few. Mention Alloy, streams and LogQL.",
        "answer": (
            "Gunicorn writes one JSON line per request to stdout, and Docker keeps it. "
            "Alloy finds the containers through the Docker socket, adds the labels service and container, and pushes the lines to Loki. "
            "Loki groups lines with the same labels into a stream and indexes only those labels. In Grafana, a LogQL query like {service_name=\"web\"} | json | status >= 500 picks the stream first and then filters its text. "
            "Every new label value creates a new stream, so labels like user IDs would make the index huge and the queries slow."
        ),
    },
    "recap": [
        "Grafana alerting: a rule (queries, condition, pending period) makes instances; policies route them by label to contact points.",
        "Set no-data and error handling on purpose; for an error ratio, no 5xx data means OK.",
        "Keep SLO pages in Prometheus and Alertmanager; use Grafana alerts for what only Grafana can query, such as logs.",
        "Loki indexes only labels; keep them few and bounded, and leave IDs in the log line.",
        "LogQL: stream selector, line filters, then a parser such as `| json`; metric queries turn lines into numbers.",
        "Alloy collects; Tempo, Mimir and Pyroscope cover traces, metrics and profiles; dashboards as code means Terraform, the Foundation SDK, Git Sync or gcx.",
    ],
    "check": [
        {
            "q": "A teammate wants to search logs by customer, so they add a `customer_id` label in Alloy. There are 80,000 customers. What will happen?",
            "options": [
                "Searches by customer get faster with no real downside",
                "Loki rejects the label because it is longer than ten characters",
                "Grafana hides the label because it contains an ID",
                "Loki gets a stream per customer, and its index and queries suffer",
            ],
            "answer": 3,
            "why": "Every label value creates a stream; keep customer IDs in the line and filter with |= or a parser.",
        },
        {
            "q": "Your metric query `sum(count_over_time({service_name=\"web\"} | json [5m]))` fails with a JSONParserErr. Some lines are Python tracebacks. What is the smallest fix?",
            "options": [
                "Remove `| json` and count every line instead",
                "Add `| __error__=\"\"` after `| json` to drop lines that failed to parse",
                "Change `count_over_time` to `rate` so parse errors are ignored",
                "Switch the stream selector to `{container=~\".+\"}`",
            ],
            "answer": 1,
            "why": "The parser labels bad lines with __error__, and a metric query only runs once those lines are filtered out.",
        },
        {
            "q": "You must alert when the share of declined payments in a SQL table rises while Prometheus shows normal traffic. Where does this rule fit best?",
            "options": [
                "A Grafana-managed rule, because it can query the SQL data source and Prometheus together",
                "A Prometheus alerting rule, because Prometheus can read SQL tables directly",
                "An Alertmanager inhibit rule, because it compares two alerts",
                "A Loki recording rule, because Loki stores all the payments",
            ],
            "answer": 0,
            "why": "Grafana-managed rules can query any backend data source, and even mix several in one rule; Prometheus only sees what it scrapes.",
        },
    ],
    "interview": [
        {
            "q": "How is Loki different from Elasticsearch, and when would you pick each?",
            "a": (
                "Loki indexes only a few labels per stream and keeps the text compressed, usually in object storage, so it is cheap to run and to keep logs in. "
                "Queries pick streams by label and then scan their text, which is fast when the labels narrow things down. "
                "Elasticsearch indexes every field and word, which costs more storage and memory but makes free-text search across everything fast. "
                "I pick Loki when logs mainly support metrics and traces in Grafana, and Elasticsearch when people search logs as their main tool."
            ),
        },
        {
            "q": "Would you put your alerts in Grafana or in Prometheus and Alertmanager?",
            "a": (
                "For SLO alerts that page someone, I prefer Prometheus rules and Alertmanager: they run next to the data and keep working if Grafana is down. "
                "Grafana-managed alerts are the better fit when the condition needs data Prometheus doesn't have, such as logs in Loki or a SQL table, or several sources together. "
                "Either way the rules live in git, through provisioning files or Terraform. "
                "The one thing I avoid is the same alert in both systems, because one incident then pages twice."
            ),
        },
        {
            "q": "What is the LGTM stack?",
            "a": (
                "It is Grafana Labs' open-source observability stack: Loki for logs, Grafana for visualization and alerting, Tempo for traces and Mimir for long-term metrics. "
                "Pyroscope adds profiles, and Alloy collects all the signals and sends them in. "
                "The parts share labels, so in Grafana you can jump from a metric spike to the matching logs and traces. "
                "For a laptop demo, the grafana/otel-lgtm image runs all of it in one container."
            ),
        },
    ],
    "deeper": {
        "minutes": 12,
        "body": (
            "The lab parses the JSON access log at query time with `| json`. That is the Loki way: store lines as they are, and decide what they mean when you ask. "
            "Alloy can also do work before the lines reach Loki, with a `loki.process` component between the source and the writer. "
            "It is worth knowing what belongs there and what doesn't.\n\n"
            "Good jobs for `loki.process`:\n"
            "- Join multiline messages. A Python traceback arrives as many lines; a `stage.multiline` block glues them into one entry, so one error is one line in Loki.\n"
            "- Drop noise. A `stage.drop` block can throw away `/healthz` lines before they cost storage.\n"
            "- Hide secrets. A replace stage can mask anything that looks like a token or a card number.\n"
            "- Add structured metadata. Loki 3 can store extra key and value pairs next to each line without indexing them, such as a trace ID or a pod name. "
            "They show up in Grafana and can be filtered after the stream selector, and they don't create streams.\n\n"
            "A bad job is turning fields such as `status` or `path` into labels. It feels natural because you query them all the time. "
            "But status times path times containers multiplies your streams, and Loki doesn't need it: `| json | status >= 500` already filters fast once the stream selector has narrowed things down.\n\n"
            "There is also the other direction: metrics from logs. The LogQL metric queries in this lesson run each time someone opens the panel. "
            "When a log-based number matters enough to alert on, Loki's ruler can run the query on a schedule. It can evaluate alerting rules, or recording rules that write the result to Prometheus or Mimir as a normal metric. "
            "Then the dashboard and the alert read a cheap metric instead of scanning logs again and again.\n\n"
            "Finally, retention. The lab keeps 7 days (`retention_period: 168h`), and the compactor deletes older chunks. "
            "In production, log volume grows with traffic, so logs can become a large share of the observability bill. "
            "Teams cut it by dropping debug lines in the collector, keeping noisy streams for less time, and sampling successful requests while keeping every error. "
            "Day 48 compares this cost model with Elasticsearch."
        ),
    },
    "sources": [
        {"title": "Grafana docs: introduction to Grafana Alerting", "url": DOC_ALERT},
        {"title": "Loki docs: query Loki (LogQL)", "url": DOC_LOGQL},
        {"title": "Loki quickstart with Docker Compose and Alloy", "url": LOKI_QS},
        {"title": "Grafana docs: observability as code", "url": DOC_ASCODE},
    ],
}
