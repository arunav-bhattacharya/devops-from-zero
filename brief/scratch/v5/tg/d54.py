"""Book-voice rewrite of d54 (Grafana beyond dashboards). Writer: tg."""
import json, pathlib

P = pathlib.Path("/home/user/devops-from-zero/content/p13.json")
d = json.loads(P.read_text())
L = next(x for x in d["lessons"] if x["id"] == "d54")

L["opening"] = (
    "Picture the doctor from last time, now looking at a clear board. It says bed 4 got worse at 14:02. That is "
    "useful, but it is not the story. The story is in the nurses' notes: what the patient said, what was given, what "
    "went wrong. Each ward keeps its notes in its own drawer, and the drawer is emptied when the patient leaves. By "
    "the time she asks, the page she needs may already be gone.\n\n"
    "It is easy to think a good dashboard is the end of the job. The numbers look complete, and the notes feel like "
    "something you can always dig up later.\n\n"
    "Last time, we built a dashboard that shows how hello-devops is doing at a glance. In this lesson, we'll give "
    "Grafana its own alarms. Then we'll collect every container's log lines in one store called Loki, search them "
    "with a query language much like PromQL, and meet the family of tools they belong to.\n\n"
    "Before we start, make a guess, and keep it in mind."
)

L["guess"]["q"] = (
    "Loki, a store for log lines, keeps the logs of every container in the lab. What does it put in its index, its "
    "lookup list, so it can find lines fast?"
)
L["guess"]["why"] = (
    "Loki indexes only the labels. A query uses them to pick a few streams, then reads the compressed text of just "
    "those streams."
)

plains = {
    "Grafana alert rule": "Queries plus a condition that Grafana checks on a schedule; it fires when the condition stays true for the waiting period.",
    "Contact point": "Where Grafana sends an alert message, such as email, Slack, PagerDuty or a web address.",
    "Notification policy": "A rule in a tree that matches alert labels and decides which contact point gets the alert, and when.",
    "Loki": "Grafana Labs' log store: it indexes only the labels of each log stream and keeps the text compressed.",
    "Log stream": "All the log lines in Loki that share exactly the same set of labels.",
    "LogQL": "Loki's query language: a stream selector in braces, then filters and parsers joined by a pipe.",
    "Grafana Alloy": "Grafana Labs' collector, built on the OpenTelemetry Collector, that gathers logs, metrics, traces and profiles and sends them on.",
    "LGTM stack": "Loki, Grafana, Tempo and Mimir: Grafana Labs' open-source tools for logs, dashboards, traces and metrics.",
}
for t in L["terms"]:
    t["plain"] = plains[t["term"]]

S = L["sections"]

S[0]["h"] = "Grafana's own alarms: rules, contact points and policies"
S[0]["body"] = (
    "Two lessons ago we built a nurses' station: Prometheus rules decided that something was wrong, and "
    "Alertmanager decided who should hear. Grafana has alerting of its own, built on the same model. The difference "
    "is that it can watch any data source Grafana can query. The parts:\n"
    "- An alert rule: one or more queries, a condition, and how often to check. Grafana runs it on a schedule, every 30 seconds in the lab.\n"
    "- Alert instances: each series the query returns gets its own instance. A rule over `sum by (job)` makes one instance per job.\n"
    "- A contact point: where the message goes, such as email, Slack, PagerDuty or a webhook (a web address that receives it).\n"
    "- Notification policies: a tree that sends firing instances to contact points by their labels, like the Alertmanager routing tree.\n\n"
    "The lab's rule lives in `grafana/provisioning/alerting/hello-alerts.yaml` and has two steps. Query A asks "
    "Prometheus for the error ratio of hello-devops, our tiny lab app, over 2 minutes. Expression C is a calculation "
    "Grafana does itself on A's result, here a threshold: is A above 0.05? The rule fires when C is true.\n\n"
    "Each instance moves through states:\n"
    "1. Normal: C is false.\n"
    "2. Pending: C is true, but not yet for the whole pending period (`for: 1m`).\n"
    "3. Alerting: C stayed true for the period. The notification goes out, and the rule shows as Firing.\n"
    "4. Normal again: Grafana sends a resolved message.\n\n"
    "Grafana also needs to know what to do when the query returns nothing or fails. By default it raises separate "
    "`DatasourceNoData` and `DatasourceError` alerts. For an error ratio, no 5xx series at all is good news, so the "
    "lab sets `noDataState: OK`.\n\n"
    "**An empty answer is not always bad news. Decide what \"no data\" means for every rule.**\n\n"
    "Otherwise the default can wake someone up because a query found no rows. The lab now has two stations, and "
    "both send to the same webhook. Next, which one should a team use?"
)

S[1]["h"] = "Grafana alerting or Alertmanager?"
S[1]["body"] = (
    "A hospital with two nurses' stations on one floor needs a clear rule about which station handles what. "
    "Otherwise the same alarm gets answered twice, or not at all. The facts first:\n"
    "- Prometheus rules run next to the data. They keep working when Grafana is down, and they live as YAML in git, or as PrometheusRule objects on Kubernetes.\n"
    "- Grafana-managed rules can query any data source, and even mix several in one rule. A rule can put a log count from Loki next to a metric from Prometheus, or a row from a SQL database.\n"
    "- Grafana rules have the no-data and error handling above, and a web page that people without PromQL can use.\n"
    "- Grafana can import Prometheus rule files and an Alertmanager configuration, so you can move later.\n\n"
    "YAML is the plain text format of these config files, and a SQL database is the kind that stores rows and "
    "columns. Go deeper notes which Grafana versions added the two imports.\n\n"
    "My default for a setup like this lab: keep the paging alerts that protect your SLO in Prometheus and "
    "Alertmanager, close to the data and independent of Grafana. The SLO is the reliability target from the start "
    "of Part 12. Use Grafana alerting for what only Grafana can see, such as alerts on logs or on data in other "
    "databases. If a team keeps all its data in one hosted Grafana stack, putting every rule in Grafana is a fair "
    "choice too.\n\n"
    "Whatever you pick, do not define the same alert in both systems. One incident would then page twice, and "
    "people learn to ignore pages.\n\n"
    "\"Alerts on logs\" assumes we have the logs somewhere Grafana can reach. So far we do not. Next, we'll build "
    "the records office."
)

S[2]["h"] = "Loki: labels pick the stream, the text stays cheap"
S[2]["body"] = (
    "So far you have read logs with `docker compose logs` (Day 21). Logs are the lines of text a program writes as "
    "it works, one per event. That command works on one machine, while the containers exist. Remove a container and "
    "its logs go with it, and with ten servers you would search in ten places. That is the ward drawer from the "
    "opening.\n\n"
    "Loki is Grafana Labs' log store, one place for the logs of every container, and its main idea comes from "
    "Prometheus. Each log line carries a few labels, such as `service=\"web\"` and "
    "`container=\"observability-web-1\"`. All lines with the same labels form one log stream. Loki indexes only the "
    "labels. The text of each line is compressed into chunks and not indexed at all.\n\n"
    "Picture a hospital records office that files notes by ward, bed and date, and never catalogues the words "
    "inside. To find a phrase, a clerk opens the few folders for that bed and day, and reads. The catalogue stays "
    "tiny, and the reading is quick because the folders are few.\n\n"
    "That makes Loki cheap to run and quick at one kind of question: give me the lines from these streams in this "
    "time range, then search inside them. Elasticsearch (Part 14) indexes every word instead. That costs more disk "
    "and memory, and in return finds a word across all logs faster.\n\n"
    "The cardinality rule from the Prometheus lessons applies here too, because every new label value makes a new "
    "stream:\n"
    "- Good labels: service, environment, cluster, container.\n"
    "- Bad labels: request ID, user ID, IP address, anything with endless values.\n"
    "- Keep those values in the line itself, where a filter finds them.\n\n"
    "A folder per visitor's name would make the catalogue bigger than the notes. Loki's docs suggest no more than "
    "10 to 15 labels, each with a small number of values.\n\n"
    "Loki also adds a `service_name` label by itself. It copies the value from a label such as `service`, `app` or "
    "`container`. The lab's Alloy (more on it soon) sets `service` to the Compose service name, so "
    "`{service_name=\"web\"}` finds the app's logs.\n\n"
    "The folders are filed. Next, we'll learn to ask for them."
)

S[3]["h"] = "LogQL, one step at a time"
S[3]["body"] = (
    "LogQL is Loki's query language, and it borrows a lot from PromQL. A query starts with a stream selector in "
    "braces, which picks the folders. Then comes an optional pipeline of steps joined by `|`, which reads inside "
    "them. All of these ran against the lab:\n"
    "1. `{service_name=\"web\"}` returns every line from the app.\n"
    "2. `{service_name=\"web\"} != \"/healthz\"` drops lines containing `/healthz`. The `|=` filter keeps lines containing a string, and `|~` takes a regular expression.\n"
    "3. `{service_name=\"web\"} | json` parses each JSON line, so `method`, `path`, `status` and `duration_ms` become labels for this query only.\n"
    "4. `{service_name=\"web\"} | json | status >= 500` keeps only the failed requests.\n"
    "5. Adding `| line_format \"{{.method}} {{.path}} -> {{.status}}\"` rewrites each line as `GET / -> 500`, easier to scan.\n\n"
    "A regular expression is a text pattern. JSON is a structured text format of names and values, and parsing a "
    "line means reading those names and values out of it.\n\n"
    "Put line filters before the parser. A plain text filter is the cheapest step, and every line it drops is a line "
    "the parser never touches.\n\n"
    "LogQL can also turn logs into numbers, which you can graph next to the Prometheus panels:\n"
    "- `count_over_time({service_name=\"web\"}[5m])` counts lines per stream over 5 minutes.\n"
    "- `rate({service_name=\"web\"}[5m])` gives lines per second.\n"
    "- `sum by (status) (count_over_time({service_name=\"web\"} | json | __error__=\"\" [5m]))` counts requests by status code.\n"
    "- `quantile_over_time(0.95, {service_name=\"web\"} | json | __error__=\"\" | unwrap duration_ms [5m])` reads a number out of each line and gives a p95.\n\n"
    "The `__error__=\"\"` part matters in the lab. When Redis is down, the app prints a Python traceback, the list "
    "of calls that led to an error, and those lines are not JSON. The parser marks them with an `__error__` label, "
    "and a metric query refuses to run until you drop them.\n\n"
    "We can ask, but someone still has to carry the notes to the records office. Next, the collector."
)

S[4]["h"] = "Alloy: the collector in the middle"
S[4]["body"] = (
    "Something has to read the logs and push them to Loki. Loki does not scrape like Prometheus: a log is a stream "
    "of events, with no current value to read, so a collector sends the lines as they appear. In the hospital, it "
    "is the porter who collects each ward's notes and carries them to the records office.\n\n"
    "In the lab that porter is Grafana Alloy, Grafana Labs' collector. It is a distribution of the OpenTelemetry "
    "Collector (Day 57) with Prometheus pipelines built in, and it handles metrics, logs, traces and profiles. "
    "Promtail, the older log shipper in many tutorials, reached [end of "
    "life](https://github.com/grafana/loki/blob/main/docs/sources/send-data/promtail/_index.md) on 2 March 2026, so "
    "new setups use Alloy.\n\n"
    "An Alloy config is a set of components wired together. Each block has a type and a name and passes its output "
    "to the next. The lab's `loki/config.alloy` has four:\n"
    "1. `discovery.docker` asks Docker which containers run, and keeps only this Compose project.\n"
    "2. `discovery.relabel` picks the labels: `service` from the Compose service name, `container` from the container name.\n"
    "3. `loki.source.docker` follows each container's output, like `docker logs -f`.\n"
    "4. `loki.write` pushes the lines to Loki's API.\n\n"
    "Alloy talks to Docker through `/var/run/docker.sock`. That is the socket file, a door for programs on the same "
    "machine, that the `docker` command also uses to reach the Docker daemon (Day 17). The daemon is the background "
    "program that runs your containers. The lab mounts the socket into the Alloy container.\n\n"
    "On a Mac this needs the Docker Desktop option \"Allow the default Docker socket to be used\", which you turned "
    "on during Day 2. The Alloy UI on http://localhost:12345 draws the pipeline and shows whether each component is "
    "healthy. Look there first when logs do not arrive.\n\n"
    "There is one more gap: Gunicorn, the program that runs the app's web server, does not log requests by default. "
    "The override file `compose.loki.yaml` sets `GUNICORN_CMD_ARGS` on the `web` service, which turns on the access "
    "log. You get one JSON line per request, in the same format as the Part 14 logging lab. Compose merges that "
    "setting into the `web` service from `compose.yaml`, so you do not edit the Part 12 file.\n\n"
    "Logs and metrics now sit side by side. Next, we'll see the rest of the family they belong to."
)

S[5]["h"] = "Traces, profiles and the LGTM stack"
S[5]["body"] = (
    "Grafana Labs builds an open-source store for each signal from the start of Part 12: metrics, logs, traces and "
    "profiles. Together they are called the LGTM stack:\n"
    "- Loki for logs.\n"
    "- Grafana for dashboards, exploring and alerting.\n"
    "- Tempo for traces. It needs only object storage to run, and you find traces by ID or with its query language, TraceQL.\n"
    "- Mimir for metrics. It speaks the Prometheus API and keeps long-term data for many Prometheus servers.\n\n"
    "A trace follows one request through every service it touches, like a parcel's tracking number stamped at "
    "every depot. Object storage is cheap online storage for large files.\n\n"
    "Pyroscope adds profiles. A profile shows which functions use the CPU and memory, drawn as a flame graph: the "
    "wider a function's bar, the more time it took. A function is a named piece of code. A trace tells you which "
    "service is slow, and a profile tells you which code inside it.\n\n"
    "If the app writes its trace ID into each log line, Grafana can link a slow step in Tempo to its log lines in "
    "Loki, and back. Day 57 adds tracing with OpenTelemetry, which is how trace IDs get into the app.\n\n"
    "To see everything on a laptop without building a stack, Grafana publishes one container with all of it "
    "inside, `grafana/otel-lgtm`. It serves Grafana on port 3000 and takes OpenTelemetry data on ports 4317 and "
    "4318. It is meant for development and demos, not production.\n\n"
    "If you would rather run nothing, Grafana Cloud hosts the whole stack. Its free tier currently lists 10,000 "
    "active metric series, 50 GB of logs, 14 days of retention and 3 users. Those limits change, so check the "
    "[pricing page](https://grafana.com/pricing/?pg=pricing) before you rely on them.\n\n"
    "One question is left from last time: how do we keep all of this, alerts included, as code once there are many "
    "Grafanas? That is the last step."
)

S[6]["h"] = "Dashboards and alerts as code, for many Grafanas"
S[6]["body"] = (
    "Last time we provisioned dashboards from files. That works well for a Grafana you start yourself. Teams with "
    "many instances, or a hosted one, use one of these:\n"
    "- Terraform. The `grafana/grafana` provider manages folders, data sources, alert rules and dashboards. A `grafana_dashboard` resource can read your JSON with `config_json = file(\"hello-red.json\")`, so Part 8 carries over.\n"
    "- The Foundation SDK. Typed builders in Go, TypeScript, Python, Java and PHP that write dashboard JSON for you, with autocomplete instead of hand-edited JSON.\n"
    "- Git Sync, generally available since Grafana 13.0. Grafana connects to a GitHub, GitLab or Bitbucket repository, saving in the UI can open a pull request, and merged changes flow back. It covers dashboards and folders.\n"
    "- gcx, Grafana's new command line tool for resources as code. It replaces Grizzly and grafanactl, which are deprecated, so skip tutorials that use them.\n"
    "- The Grafana Operator, for teams that want dashboards as Kubernetes custom resources.\n\n"
    "Terraform is the tool from Part 8 that builds things from code files. An SDK is a set of ready-made code for "
    "one job, and \"typed\" means the code editor can warn you about mistakes as you write.\n\n"
    "Pick one per team. For this course, file provisioning plus Terraform is plenty.\n\n"
    "Grafana 12 and 13 also changed things that make older tutorials wrong. The one you will hit first: the "
    "`grafana/grafana-oss` image stopped at 12.4, so use `grafana/grafana`. Go deeper lists the rest.\n\n"
    "That completes this part's view. Metrics say that something is wrong, dashboards show it at a glance, and Loki "
    "lets us read what the app said. Loki is fast because it reads only a few folders. When someone needs to find a "
    "word across every log at once, it is the wrong tool, and that is where the other big log store comes in."
)

# The records office carries the analogy; the label mistake is in section 3.
L.pop("analogy", None)
L.pop("mistake", None)
L["real_world"] = (
    "Splitting alerting between two systems works when each alert has exactly one home. A payments company might "
    "let Prometheus and Alertmanager page on-call for the checkout SLO. Grafana alerting gets the rest, such as a "
    "rule that counts `card declined` lines in Loki per merchant. Every Grafana rule and contact point lives in "
    "Terraform next to the dashboards, so a new team gets its alerts by pull request, not by clicking."
)

W = L["worked"]["steps"]
W[0]["say"] = (
    "Save `hello-alerts.yaml` from the Files section in `grafana/provisioning/alerting/` and restart Grafana. Then "
    "ask Grafana what it loaded. The field `provenance: file` means the rule came from a file, so the UI will not let "
    "anyone edit it."
)
W[1]["say"] = (
    "With the traffic loop running and Redis up, the rule is inactive: almost nothing fails, so condition C is "
    "false. Break the app the same way as last time."
)
W[2]["say"] = (
    "Watch the state with a small loop that prints a line only when it changes (times are UTC). Redis stopped at "
    "05:22:30. The rule looks at a 2-minute window and runs every 30 seconds, so the ratio crossed 5% at 05:24:04 "
    "and the rule turned Pending. It stayed true for the whole pending period of one minute, and at 05:25:05 it "
    "fired."
)
W[3]["say"] = (
    "Stop the loop with Ctrl+C and read the webhook's last few minutes. The `[lab-webhook]` prefix is Grafana's "
    "contact point. The summary comes from the rule's annotation template, which turned the value of query A into a "
    "percentage. The `[pager]` line is the fast-burn alert from two lessons ago, sent by Alertmanager to the same "
    "webhook. Its 4.5% is the 1-hour error ratio, which moves much more slowly than Grafana's 2-minute window."
)
W[4]["say"] = (
    "Start Redis. Once the 2-minute ratio drops back under 5%, the instance returns to Normal and Grafana sends a "
    "resolved message. Nothing in this rule is specific to Prometheus: the query could just as well count error "
    "lines in Loki, which you do in the task."
)

T = L["task"]
T["steps"] = [
    "Create `compose.loki.yaml`, `loki/loki.yaml`, `loki/config.alloy` and `grafana/provisioning/datasources/loki.yaml` from this lesson's Files section.",
    "Start the stack with both Compose files, wait until Loki says ready, and open the Alloy UI to check that every component is healthy.",
    "Make Grafana read the new data source (reload API or restart), then open Explore, pick Loki and run `{service_name=\"web\"}` while your traffic loop runs.",
    "Write three LogQL queries: all requests except `/healthz`, only failed requests, and requests per second by status code.",
    "Stop Redis for two minutes. Use Loki to find the exception message that explains the 500s, and note its exact text.",
    "Add a panel to a scratch dashboard that graphs your requests-by-status query from Loki next to the Prometheus error ratio, and compare the shapes.",
    "Create a second Grafana alert rule in the UI from a Loki query that fires when more than 5 lines contain `ConnectionError` in 5 minutes. Watch it fire while Redis is down.",
    "Start Redis again and check that both Grafana alerts resolve in the webhook output.",
]
T["hints"] = [
    "If Loki returns nothing, check the Alloy UI first, then `docker compose -f compose.yaml -f compose.loki.yaml logs alloy`.",
    "A metric query over JSON lines needs `| __error__=\"\"` after `| json`, because the traceback lines are not JSON.",
    "For the alert, the query is shaped like `sum(count_over_time({service_name=\"web\"} |= \"...\" [5m]))`, with a threshold above 5.",
]
T["done_when"] = (
    "In Explore, `sum by (status) (count_over_time({service_name=\"web\"} | json | __error__=\"\" [5m]))` shows a "
    "`500` series from your outage, and the webhook printed a FIRING and a RESOLVED line from your Loki alert."
)

L["explain_back"]["prompt"] = (
    "Explain to a teammate, in 3 to 4 sentences, how a log line from hello-devops ends up on your screen in Grafana, "
    "and why Loki labels must stay few. Mention Alloy, streams and LogQL."
)
L["explain_back"]["answer"] = (
    "Gunicorn writes one JSON line per request to its output, and Docker keeps it. Alloy finds the containers "
    "through the Docker socket, adds the labels service and container, and pushes the lines to Loki. Loki groups "
    "lines with the same labels into a stream and indexes only those labels. In Grafana, a LogQL query like "
    "{service_name=\"web\"} | json | status >= 500 picks the stream first and then filters its text. Every new label "
    "value creates a new stream, so labels like user IDs would make the index huge and the queries slow."
)

L["recap"] = [
    "Grafana alerting: a rule (queries, condition, pending period) makes instances; policies route them by label to contact points.",
    "Set no-data and error handling on purpose; for an error ratio, no 5xx data means OK.",
    "Keep SLO pages in Prometheus and Alertmanager; use Grafana alerts for what only Grafana can query, such as logs.",
    "Loki indexes only labels; keep them few and bounded, and leave IDs in the log line.",
    "LogQL: stream selector, line filters, then a parser such as `| json`; metric queries turn lines into numbers.",
    "Alloy collects and Tempo, Mimir and Pyroscope cover the other signals. Loki is weak at finding one word across all logs.",
]

C = L["check"]
C[0]["q"] = (
    "A teammate wants to search logs by customer, so they add a `customer_id` label in Alloy. There are 80,000 "
    "customers. What will happen?"
)
C[0]["why"] = "Every label value creates a stream. Keep customer IDs in the line and filter with |= or a parser."
C[1]["q"] = (
    "Your metric query `sum(count_over_time({service_name=\"web\"} | json [5m]))` fails with a JSONParserErr. Some "
    "lines are Python tracebacks. What is the smallest fix?"
)
C[1]["why"] = "The parser labels bad lines with __error__, and a metric query only runs once those lines are filtered out."
C[2]["q"] = (
    "You must alert when the share of declined payments in a SQL table rises while Prometheus shows normal traffic. "
    "Where does this rule fit best?"
)
C[2]["why"] = (
    "Grafana-managed rules can query any data source, and even mix several in one rule; Prometheus only sees what "
    "it scrapes."
)

I = L["interview"]
I[0]["a"] = (
    "Loki indexes only a few labels per stream and keeps the text compressed, usually in object storage, so it is "
    "cheap to run and to keep logs in. Queries pick streams by label and then scan their text, which is fast when "
    "the labels narrow things down. Elasticsearch indexes every field and word, which costs more storage and memory "
    "but makes free-text search across everything fast. I pick Loki when logs mainly support metrics and traces in "
    "Grafana, and Elasticsearch when people search logs as their main tool."
)
I[1]["a"] = (
    "For SLO alerts that page someone, I prefer Prometheus rules and Alertmanager: they run next to the data and "
    "keep working if Grafana is down. Grafana-managed alerts are the better fit when the condition needs data "
    "Prometheus does not have, such as logs in Loki or a SQL table, or several sources together. Either way the "
    "rules live in git, through provisioning files or Terraform. The one thing I avoid is the same alert in both "
    "systems, because one incident then pages twice."
)
I[2]["a"] = (
    "It is Grafana Labs' open-source observability stack: Loki for logs, Grafana for dashboards and alerting, Tempo "
    "for traces and Mimir for long-term metrics. Pyroscope adds profiles, and Alloy collects all the signals and "
    "sends them in. The parts share labels, so in Grafana you can jump from a metric spike to the matching logs and "
    "traces. For a laptop demo, the grafana/otel-lgtm image runs all of it in one container."
)

L["deeper"]["body"] = (
    "The lab parses the JSON access log at query time with `| json`. That is the Loki way: store lines as they are, "
    "and decide what they mean when you ask. Alloy can also do work before the lines reach Loki, with a "
    "`loki.process` component between the source and the writer. Some jobs belong there and some do not.\n\n"
    "Good jobs for `loki.process`:\n"
    "- Join multiline messages. A Python traceback arrives as many lines; a `stage.multiline` block glues them into one entry, so one error is one line in Loki.\n"
    "- Drop noise. A `stage.drop` block can throw away `/healthz` lines before they cost storage.\n"
    "- Hide secrets. A replace stage can mask anything that looks like a token or a card number.\n"
    "- Add structured metadata. Loki 3 can store extra key and value pairs next to each line without indexing them, such as a trace ID or a pod name. They show up in Grafana and can be filtered after the stream selector, and they do not create streams.\n\n"
    "A bad job is turning fields such as `status` or `path` into labels. It feels natural because you query them "
    "all the time. But status times path times containers multiplies your streams, and Loki does not need it: "
    "`| json | status >= 500` already filters fast once the stream selector has narrowed things down.\n\n"
    "There is also the other direction: metrics from logs. The LogQL metric queries in this lesson run each time "
    "someone opens the panel. When a log-based number matters enough to alert on, Loki's ruler can run the query on "
    "a schedule. It can evaluate alerting rules, or recording rules that write the result to Prometheus or Mimir as "
    "a normal metric. Then the dashboard and the alert read a cheap metric instead of scanning logs again and "
    "again.\n\n"
    "Retention is the next thing to plan. The lab keeps 7 days (`retention_period: 168h`), and the compactor deletes "
    "older chunks. In production, log volume grows with traffic, so logs can become a large share of the "
    "observability bill. Teams cut it by dropping debug lines in the collector, keeping noisy streams for less time, "
    "and sampling successful requests while keeping every error. Day 56 compares this cost model with "
    "Elasticsearch.\n\n"
    "Last, the version details. Grafana can import Prometheus rule files since 12.1, and an Alertmanager "
    "configuration since 13.3. Grafana 12 and 13 also changed these things:\n"
    "- 12.0 removed Angular plugins, so some old panels no longer load.\n"
    "- 13.0 removed the `grafana-cli` and `grafana-server` commands. Use `grafana cli` and `grafana server`.\n"
    "- 13.0 made dynamic dashboards generally available: tabs, rows that show or hide themselves, and automatic layout, in the v2 dashboard format.\n"
    "- 13.3 added Notebooks for investigations, and variables you define once and share across dashboards."
)

L["closing"] = (
    "We started with a doctor who could see that bed 4 got worse at 14:02, but not why, because the notes sat in a "
    "drawer that emptied itself. Now every container's lines reach one records office, filed by a few labels, and "
    "LogQL reads exactly the folders we need. In the lab, run `curl -s localhost:3100/loki/api/v1/labels` and check "
    "that every label name has only a handful of values.\n\n"
    "Next, we'll meet the Elastic stack, which indexes every word of every line, and ask when that bigger catalogue "
    "is worth its cost."
)

P.write_text(json.dumps(d, indent=1, ensure_ascii=False) + "\n")
print("d54 written")
