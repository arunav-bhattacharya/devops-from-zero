from common import lab, ref, src

DIAGRAM = (
    '<svg viewBox="0 0 560 300" xmlns="http://www.w3.org/2000/svg" role="img" '
    'aria-label="Prometheus scrapes the metrics pages of hello-devops, node_exporter and itself, stores samples '
    'in its time series database, sends firing alerts to Alertmanager, and answers queries from Grafana">'
    # targets on the left
    '<rect class="bxt" x="16" y="24" width="150" height="40" rx="10"/>'
    '<text class="tk" x="91" y="49" font-size="13" text-anchor="middle">hello-devops</text>'
    '<rect class="bxt" x="16" y="88" width="150" height="40" rx="10"/>'
    '<text class="tk" x="91" y="113" font-size="13" text-anchor="middle">node_exporter</text>'
    '<rect class="bxt" x="16" y="152" width="150" height="40" rx="10"/>'
    '<text class="tk" x="91" y="177" font-size="13" text-anchor="middle">Alertmanager</text>'
    '<text class="ts" x="91" y="212" font-size="11" text-anchor="middle">targets: GET /metrics</text>'
    # prometheus in the middle
    '<rect class="bxo" x="226" y="56" width="140" height="104" rx="10"/>'
    '<text class="tk" x="296" y="84" font-size="13" text-anchor="middle">Prometheus</text>'
    '<text class="ts" x="296" y="108" font-size="11" text-anchor="middle">scraper</text>'
    '<text class="ts" x="296" y="126" font-size="11" text-anchor="middle">TSDB</text>'
    '<text class="ts" x="296" y="144" font-size="11" text-anchor="middle">rules</text>'
    # scrape arrows: from prometheus to targets
    '<line class="ln" x1="224" y1="76" x2="170" y2="48" marker-end="url(#ar)"/>'
    '<line class="ln" x1="224" y1="108" x2="170" y2="108" marker-end="url(#ar)"/>'
    '<line class="ln" x1="224" y1="140" x2="170" y2="168" marker-end="url(#ar)"/>'
    '<text class="ts" x="197" y="40" font-size="11" text-anchor="middle">pull</text>'
    # right side: grafana and alertmanager destination
    '<rect class="bxg" x="420" y="56" width="124" height="40" rx="10"/>'
    '<text class="tk" x="482" y="81" font-size="13" text-anchor="middle">Grafana</text>'
    '<line class="ln" x1="418" y1="76" x2="370" y2="76" marker-end="url(#ar)"/>'
    '<text class="ts" x="394" y="68" font-size="11" text-anchor="middle">PromQL</text>'
    '<rect class="bx" x="420" y="128" width="124" height="40" rx="10"/>'
    '<text class="t" x="482" y="153" font-size="13" text-anchor="middle">You (UI)</text>'
    '<line class="ln" x1="418" y1="148" x2="370" y2="140" marker-end="url(#ar)"/>'
    # alerts down to alertmanager receiver
    '<line class="lnd" x1="296" y1="162" x2="296" y2="236" marker-end="url(#ar)"/>'
    '<text class="ts" x="304" y="204" font-size="11" text-anchor="start">firing alerts</text>'
    '<rect class="bxp" x="216" y="240" width="160" height="40" rx="10"/>'
    '<text class="tk" x="296" y="265" font-size="13" text-anchor="middle">Alertmanager</text>'
    "</svg>"
)

METRICS_SAMPLE = (
    "$ curl -s localhost:8000/metrics | grep '^hello_responses_total'\n"
    'hello_responses_total{path="/",status="200"} 865.0\n'
    'hello_responses_total{path="/healthz",status="200"} 13.0\n'
    'hello_responses_total{path="/",status="500"} 48.0'
)

LESSON = {
    "id": "d42",
    "title": "Prometheus: architecture and the data model",
    "minutes": 50,
    "goal": "By the end you can run Prometheus next to hello-devops with Docker Compose, read a /metrics page line by line, explain what a time series is, pick the right metric type, and spot a label that would explode the number of series.",
    "guess": {
        "q": "hello-devops crashes and stops answering. How does Prometheus find out?",
        "options": [
            "The app sends a last message to Prometheus before it dies",
            "Its next scrape of the app fails, and it records up = 0",
            "It does not notice; the graph just stays flat",
            "Docker tells Prometheus that the container stopped",
        ],
        "answer": 1,
        "why": "Prometheus pulls. Every scrape records an `up` value for the target: 1 if the scrape worked, 0 if it failed. A dead app cannot push anything.",
    },
    "terms": [
        {"term": "Target", "plain": "One endpoint Prometheus scrapes, such as web:8000/metrics."},
        {"term": "Scrape", "plain": "One HTTP GET of a target's /metrics page, done again every scrape interval."},
        {"term": "Exporter", "plain": "A small program that reads numbers from something else, such as Linux, and shows them on a /metrics page."},
        {"term": "Time series", "plain": "All the samples for one metric name plus one exact set of label values."},
        {"term": "Label", "plain": "A key and value pair on a metric, such as status=\"500\", used to split and filter."},
        {"term": "Sample", "plain": "One value with a timestamp, stored each time a series is scraped."},
        {"term": "Cardinality", "plain": "How many time series a metric creates: every new combination of label values is a new series."},
        {"term": "Histogram", "plain": "A metric that counts observations, such as request times, into buckets with upper limits."},
    ],
    "sections": [
        {
            "h": "Prometheus pulls",
            "body": (
                "Prometheus is a server that collects numbers from your programs every few seconds and stores them with a timestamp. "
                "It does this by pulling. Your app shows its current numbers on a plain web page, `/metrics`, and Prometheus fetches that page on a timer. "
                "One fetch is a scrape, and the thing it scrapes is a target.\n\n"
                "Pulling sounds backwards if you know logging, where the app sends lines out. It has real advantages:\n"
                "- Prometheus knows which targets should exist. If one does not answer, it records `up = 0` for it, a health check you get for free.\n"
                "- You can read the same page yourself with `curl` while you debug.\n"
                "- A slow or broken monitoring server never blocks your app. The app only keeps a few counters in memory.\n\n"
                "Pushing still has a place. A batch job that runs for 20 seconds may finish before any scrape. "
                "For that case the docs describe the Pushgateway, and they say [it is usually only right](https://github.com/prometheus/docs/blob/main/docs/practices/pushing.md) for the result of service-level batch jobs. "
                "Prometheus 3 can also receive metrics pushed over OTLP, the OpenTelemetry protocol you meet on Day 49."
            ),
            "refs": [ref("overview"), ref("v_how_prom")],
        },
        {
            "h": "The parts: server, targets, exporters",
            "body": (
                "One Prometheus server is a single program with four jobs:\n"
                "- A scraper that fetches every target each `scrape_interval` (default 1 minute; the lab uses 15 seconds).\n"
                "- A time series database (TSDB) on local disk.\n"
                "- A rule engine that runs recording rules (Day 43) and alerting rules (Day 44).\n"
                "- A web UI and HTTP API that answer PromQL queries.\n\n"
                "You list targets in `prometheus.yml` under `scrape_configs`. Each entry is a job: a group of targets that do the same work. "
                "The lab has four jobs: `prometheus` (it scrapes itself), `hello-devops`, `node` and `alertmanager`. "
                "In a big system you do not type addresses. Service discovery asks the platform for the current list instead: Kubernetes, Docker, AWS and plain files are all supported.\n\n"
                "Many programs have no `/metrics` page. An exporter fills the gap: it reads numbers from the system and shows them in Prometheus format.\n"
                "- [node_exporter](https://github.com/prometheus/node_exporter) shows CPU, memory, disk and network for a Linux machine, on port 9100.\n"
                "- [blackbox_exporter](https://github.com/prometheus/blackbox_exporter) probes other services from outside (HTTP, TCP, DNS), on port 9115.\n\n"
                "One warning for your Mac. Docker Desktop runs containers inside a small Linux virtual machine. "
                "So the node_exporter container in the lab reports that VM, not macOS. "
                "That is fine for learning PromQL; just do not read it as your laptop's numbers."
            ),
            "refs": [ref("config"), ref("node_exporter"), ref("v_intro_prom")],
        },
        {
            "h": "Reading a /metrics page",
            "body": (
                "Open `localhost:8000/metrics` and you see the exposition format: plain text, one sample per line. "
                "Here are the first lines for the app's own counter:\n"
                "- `# HELP hello_requests_total Requests served` is the description.\n"
                "- `# TYPE hello_requests_total counter` is the metric type.\n"
                "- `hello_requests_total{path=\"/\"} 3.0` is the metric name, its labels in braces, and the current value.\n\n"
                "The rest of the page has three sources:\n"
                "- `app.py` defines `hello_requests_total`. It counts visits to `/` and has one label, `path`.\n"
                "- `observability/red_metrics.py` adds `hello_responses_total` (with `path` and `status`) and the histogram `hello_request_duration_seconds`. Compose loads it next to the unchanged app; Day 44 explains how.\n"
                "- The Python client adds `process_*` metrics (memory, CPU, open files) and `python_*` metrics for free.\n\n"
                "Two details surprise most people. The Python client adds a `_created` series next to each counter, holding the time it was created; you can ignore it. "
                "And the names follow conventions from the [naming guide](https://github.com/prometheus/docs/blob/main/docs/practices/naming.md): base units such as seconds and bytes, `_total` at the end of counters, and a prefix for the app.\n\n"
                "Prometheus 3 is strict about the HTTP `Content-Type` header of this page. If it is missing or wrong, the scrape fails. Client libraries set it for you."
            ),
            "refs": [ref("exposition"), ref("naming")],
        },
        {
            "h": "A time series is a name plus labels",
            "body": (
                "This is the most important idea in Prometheus. A **time series** is identified by its metric name plus the exact set of label values. "
                "Change any label value and you have a different series.\n\n"
                "The app's page shows `hello_responses_total` three times, with three label sets: `/` and 200, `/healthz` and 200, `/` and 500. "
                "That is three time series. Each scrape adds one sample to each: a timestamp and a value.\n\n"
                "Prometheus adds two labels of its own when it stores them:\n"
                "- `job`: the job name from `prometheus.yml`, here `hello-devops`.\n"
                "- `instance`: the target's address, here `web:8000`.\n\n"
                "So the full name of one series in the lab is `hello_responses_total{instance=\"web:8000\", job=\"hello-devops\", path=\"/\", status=\"500\"}`. "
                "If you think in databases, the labels are a composite primary key, and each scrape appends a row to every key.\n\n"
                "Prometheus also writes a few series per target that the app never showed. "
                "`up` is 1 or 0 for each scrape, and `scrape_duration_seconds` tells you how long it took. "
                "When a scrape takes longer than `scrape_timeout` (10 seconds by default), it fails with `context deadline exceeded` and `up` becomes 0."
            ),
            "refs": [ref("data_model")],
        },
        {
            "h": "Four metric types",
            "body": (
                "Every metric has one of four types. The type tells you which questions it can answer.\n\n"
                "A counter only goes up, or drops to zero when the process restarts. `hello_responses_total` and `process_cpu_seconds_total` are counters. "
                "The raw value is rarely useful; you ask how fast it grows, which is `rate()` on Day 43.\n\n"
                "A gauge is a value that goes up and down: memory in use, queue length, temperature. "
                "For example, the app's `process_resident_memory_bytes` read 48,803,840 bytes (about 49 MB) in my run. You read a gauge as it is, and you never take its `rate()`.\n\n"
                "A histogram counts observations into buckets. Each bucket has an upper limit, the `le` label (less than or equal), and the buckets are cumulative. "
                "In my run the app's `/` route showed `le=\"0.005\"` 759 and `le=\"0.01\"` 1009: 759 requests took 5 ms or less, and 1009 took 10 ms or less. "
                "Next to the buckets come `_sum` (all the seconds added up) and `_count` (how many). From these, Prometheus can estimate percentiles and add them up across many servers.\n\n"
                "A summary computes percentiles inside the app and shows them with a `quantile` label. Prometheus itself has one: `go_gc_duration_seconds{quantile=\"0.5\"}`. "
                "Summaries from several servers cannot be combined, because you cannot average percentiles. "
                "That is why the [docs](https://prometheus.io/docs/practices/histograms/) usually point you to histograms.\n\n"
                "Quick rule: counting events, use a counter; measuring a level, a gauge; timing things or sizes, a histogram."
            ),
            "refs": [ref("metric_types"), ref("understanding_types"), ref("v_hist")],
        },
        {
            "h": "Cardinality: why user IDs never go in labels",
            "body": (
                "Labels look free, and this trips most people up. Each new label value creates new series, and series cost memory, disk and query time.\n\n"
                "Count the app's histogram. It has one label, `path`, and the default buckets give 15 `le` values. "
                "Each path therefore costs 15 bucket series plus `_sum`, `_count` and `_created`, and the counter adds 2 more. "
                "In the lab, one request to a new route took the `hello_*` series from 44 to 64.\n\n"
                "Now imagine someone adds a `user_id` label so they can see requests per user. With 10,000 users, that is 200,000 series for one route, from one app instance. "
                "The [instrumentation guide](https://prometheus.io/docs/practices/instrumentation/) suggests keeping most metrics under 10 series and looking hard at anything that could pass 100.\n\n"
                "Rules that keep you safe:\n"
                "- Labels hold small, fixed sets of values: status code, HTTP method, route pattern.\n"
                "- Never put user IDs, email addresses, request IDs or raw URLs in labels.\n"
                "- Record the route pattern, not the URL. `red_metrics.py` uses Flask's rule, so `/nope` and `/admin.php` both become `unmatched`.\n"
                "- Details about single requests belong in logs and traces (Part 11).\n\n"
                "For scale: the whole lab, with all four jobs, holds about 2,200 series."
            ),
            "refs": [ref("instrumentation"), ref("cardinality")],
        },
        {
            "h": "Storage, retention and what changed in Prometheus 3",
            "body": (
                "The TSDB keeps recent samples in memory and in a write-ahead log, then writes them to disk in two-hour blocks. "
                "Old blocks are merged in the background. "
                "By default it keeps 15 days of data (`--storage.tsdb.retention.time`); the lab keeps 7. "
                "The [storage docs](https://prometheus.io/docs/prometheus/latest/storage/) say plainly that local storage is not clustered or replicated. "
                "For months of history or a backup, you send data elsewhere, which Day 44 covers.\n\n"
                "Prometheus 3.0 came out in November 2024, the first major version in seven years. What you will notice:\n"
                "- A new web UI. The Query page has Table, Graph and Explain tabs, and Explore metrics in its menu lists every metric name.\n"
                "- Metric and label names may use any UTF-8 characters, such as dots from OpenTelemetry. Such names need quotes in PromQL.\n"
                "- An OTLP receiver, turned on with `--web.enable-otlp-receiver`, so OpenTelemetry apps can push metrics in.\n"
                "- Native histograms, a more precise histogram, are stable since 3.8 but stay off unless you turn them on.\n"
                "- Some old flags were removed. Tutorials written for Prometheus 2 may show flags that no longer start.\n\n"
                "The details are in the [Prometheus 3.0 announcement](https://prometheus.io/blog/2024/11/14/prometheus-3-0/)."
            ),
            "refs": [ref("storage"), ref("prom3_blog")],
        },
    ],
    "analogy": (
        "Prometheus is like a meter reader who walks past every house on a fixed round, every 15 seconds. "
        "Each house shows its meters through the window (the /metrics page), and the reader writes down every number with the time and the house address (the labels). "
        "If a house does not answer, the reader notes that too, which is up = 0. "
        "Where it breaks: one house cannot overwhelm a real meter reader. "
        "An app that invents a new label value per user can, because it creates thousands of new meters for Prometheus to read and store."
    ),
    "diagram": DIAGRAM,
    "diagram_caption": "Prometheus pulls /metrics from each target, stores the samples, and pushes only firing alerts onward.",
    "worked": {
        "title": "Count what one label costs",
        "steps": [
            {
                "say": (
                    "Start only the services this lesson needs, from the `observability` folder, and keep a request loop running in a second terminal. "
                    "Compose starts Redis too, because `web` depends on it."
                ),
                "code": "$ cd observability\n$ docker compose up -d --build web prometheus node-exporter\n"
                "$ while true; do curl -s localhost:8000/ > /dev/null; sleep 0.2; done",
                "lang": "console",
            },
            {
                "say": (
                    "Read one metric family straight from the app. One name, three label combinations, so three time series. "
                    "I had stopped Redis for a few minutes earlier, which is where the 500 line comes from."
                ),
                "code": METRICS_SAMPLE,
                "lang": "console",
            },
            {
                "say": (
                    "Ask Prometheus how many `hello_*` series it stores. A small shell function saves typing: it runs `promtool`, "
                    "the command-line tool inside the Prometheus container, against the server's API."
                ),
                "code": "$ q() { docker compose exec prometheus promtool query instant http://localhost:9090 \"$1\"; }\n"
                "$ q 'count({__name__=~\"hello_.*\"})'\n"
                "{} => 44 @[1793338157.211]",
                "lang": "console",
            },
            {
                "say": (
                    "Split that count by metric name. The buckets are the big part: 2 routes (`/` and `/healthz`) times 15 `le` values is 30."
                ),
                "code": "$ q 'count by (__name__) ({__name__=~\"hello_.*\"})'\n"
                "hello_requests_total => 1 @[1793338157.505]\nhello_requests_created => 1 @[1793338157.505]\n"
                "hello_responses_total => 3 @[1793338157.505]\nhello_responses_created => 3 @[1793338157.505]\n"
                "hello_request_duration_seconds_bucket => 30 @[1793338157.505]\nhello_request_duration_seconds_count => 2 @[1793338157.505]\n"
                "hello_request_duration_seconds_sum => 2 @[1793338157.505]\nhello_request_duration_seconds_created => 2 @[1793338157.505]",
                "lang": "console",
            },
            {
                "say": (
                    "Now add one new label value: call a route nobody had called yet, then count again after the next scrape. "
                    "One request to `/readyz` added 20 series."
                ),
                "code": "$ curl -s localhost:8000/readyz\n{\"status\":\"ready\"}\n$ q 'count({__name__=~\"hello_.*\"})'\n{} => 64 @[1793338169.071]",
                "lang": "console",
            },
            {
                "say": (
                    "Do the maths for a `user_id` label with 10,000 users on one route, then compare with the whole lab. "
                    "One careless label would make this single app 90 times bigger than everything Prometheus stores today."
                ),
                "code": "$ python3 -c \"print(20 * 10000)\"\n200000\n$ q 'prometheus_tsdb_head_series'\n"
                "prometheus_tsdb_head_series{instance=\"localhost:9090\", job=\"prometheus\"} => 2177 @[1793338169.53]",
                "lang": "console",
            },
        ],
    },
    "code": [
        {
            "lang": "yaml",
            "title": "observability/compose.yaml",
            "src": lab("observability/compose.yaml"),
            "run": "cd observability && docker compose up -d --build web prometheus node-exporter",
        },
        {
            "lang": "yaml",
            "title": "observability/prometheus/prometheus.yml",
            "src": lab("observability/prometheus/prometheus.yml"),
            "run": "docker compose exec prometheus promtool check config /etc/prometheus/prometheus.yml",
        },
        {
            "lang": "python",
            "title": "observability/red_metrics.py",
            "src": lab("observability/red_metrics.py"),
            "run": "curl -s localhost:8000/metrics | grep '^hello_'",
        },
    ],
    "commands": [
        {"cmd": "docker compose up -d --build web prometheus node-exporter", "what": "From the observability folder: build the app and start it with Redis, Prometheus and node_exporter."},
        {"cmd": "docker compose ps", "what": "Check that every service is running."},
        {"cmd": "curl -s localhost:8000/metrics | grep '^hello_'", "what": "Show only the app's own metric lines, without HELP and TYPE comments."},
        {"cmd": "curl -s localhost:9100/metrics | grep '^node_load'", "what": "Read node_exporter's load average lines directly."},
        {"cmd": "open http://localhost:9090/targets", "what": "Open Prometheus at Status, Target health: every target with its state and last error."},
        {"cmd": "q() { docker compose exec prometheus promtool query instant http://localhost:9090 \"$1\"; }", "what": "Define a shell function q that runs one PromQL query from the terminal."},
        {"cmd": "q 'up'", "what": "One line per target: 1 if the last scrape worked, 0 if it failed."},
        {"cmd": "q 'count by (job) ({__name__=~\".+\"})'", "what": "Count the stored series per job."},
        {"cmd": "q 'prometheus_tsdb_head_series'", "what": "How many series Prometheus holds in memory right now."},
        {"cmd": "docker compose exec prometheus promtool check config /etc/prometheus/prometheus.yml", "what": "Check prometheus.yml for mistakes before you reload."},
        {"cmd": "curl -X POST localhost:9090/-/reload", "what": "Tell Prometheus to re-read its config without a restart (the lab enables this endpoint)."},
        {"cmd": "docker compose stop node-exporter", "what": "Stop one target on purpose to watch its up value drop to 0."},
        {"cmd": "docker compose down", "what": "Stop the stack. Add -v to delete the stored metrics too."},
    ],
    "mistake": (
        "Putting an unbounded value in a label: a user ID, an email address, a request ID or the raw URL path. "
        "Nothing fails at first, then memory use climbs and queries slow down as the series pile up. "
        "Keep labels to small fixed sets such as status code and route pattern, and put per-request details in logs or traces."
    ),
    "real_world": (
        "At PayFlow, a made-up payments company, each service exposes /metrics and Prometheus finds the pods through Kubernetes service discovery. "
        "Their code review checklist asks one question about every new label: how many values can it have? "
        "A `merchant_id` label would mean one series per merchant per route per bucket, so merchant-level detail goes into logs instead."
    ),
    "task": {
        "title": "Start the lab and explore its targets",
        "steps": [
            "Add the three files above to `observability/` in your repo, then start `web`, `prometheus` and `node-exporter` with Compose. Stop the Day 15 stack first if it is still running, because both use port 8000.",
            "Open Status, then Target health in the Prometheus UI. Find the four jobs. One of them is down: read its error message and explain why it is down today.",
            "Run `curl -s localhost:8000/metrics` and find one counter, one gauge and one histogram. Write down the `# TYPE` line for each.",
            "In the Query page, run `up` in the Table tab. Then stop node-exporter with Compose, wait 30 seconds and run it again.",
            "Start node-exporter again. Run `count by (job) ({__name__=~\".+\"})` and note which job has the most series.",
            "Change `scrape_interval` in `prometheus.yml` from 15s to 5s, check the file with promtool, reload Prometheus and confirm the new value on the Status, Configuration page.",
            "Set the interval back to 15s and reload again.",
        ],
        "hints": [
            "The down target's error mentions a lookup that failed. Which service in compose.yaml did you not start?",
            "`process_resident_memory_bytes` is a gauge, and anything ending in `_bucket` belongs to a histogram.",
            "Reloading needs `curl -X POST`; a plain GET to `/-/reload` is refused.",
        ],
        "done_when": "Target health shows hello-devops, node and prometheus as UP, you can explain why alertmanager is DOWN, and you have one counter, one gauge and one histogram from the app's page.",
    },
    "explain_back": {
        "prompt": "Explain to a teammate in 3 to 4 sentences how a number in app.py ends up stored in Prometheus. Mention the /metrics page, the scrape, labels and what makes one time series different from another.",
        "answer": (
            "The app keeps counters in memory and prints their current values on its /metrics page in a simple text format. "
            "Every 15 seconds Prometheus scrapes that page, adds job and instance labels, and stores one timestamped sample per series. "
            "A series is the metric name plus one exact set of label values, so hello_responses_total with status 200 and with status 500 are two series. "
            "That is why every new label value costs a new series, and why user IDs never go in labels."
        ),
    },
    "recap": [
        "Prometheus pulls: it scrapes each target's /metrics page every scrape interval and records up = 0 when a scrape fails.",
        "One server scrapes, stores samples in its TSDB, runs rules and answers PromQL; exporters give /metrics pages to things that have none.",
        "A time series is a metric name plus one exact set of label values; Prometheus adds job and instance.",
        "Counters only go up, gauges go up and down, histograms count observations into cumulative buckets, summaries cannot be combined.",
        "Every new label value is a new series, so keep labels to small fixed sets and never use user IDs or raw URLs.",
        "Data stays on local disk for 15 days by default; Prometheus 3 brought a new UI, UTF-8 names and an OTLP receiver.",
    ],
    "check": [
        {
            "q": "A metric `orders_total` has labels `country` (40 values) and `payment_method` (5 values), and it runs on 3 instances. At most how many series can it create?",
            "options": ["48", "120", "200", "600"],
            "answer": 3,
            "why": "Series multiply across labels: 40 times 5 times 3 instances is 600.",
        },
        {
            "q": "You want to track how many jobs are waiting in a queue right now. Which metric type fits?",
            "options": ["Gauge", "Counter", "Histogram", "Summary"],
            "answer": 0,
            "why": "Queue length goes up and down, which is exactly what a gauge is for.",
        },
        {
            "q": "A nightly backup script runs for 30 seconds and then exits. Prometheus scrapes every minute. What is the usual way to get its result into Prometheus?",
            "options": [
                "Scrape it every second so you catch it",
                "Add a backup_id label to every metric",
                "Push the result to a Pushgateway at the end of the job",
                "Write the result into the app's /metrics page by hand",
            ],
            "answer": 2,
            "why": "A short batch job may finish between scrapes, and recording its outcome is the main case the Pushgateway exists for.",
        },
    ],
    "interview": [
        {
            "q": "Why does Prometheus pull metrics instead of having apps push them?",
            "a": (
                "With pull, Prometheus knows the full list of targets, so a target that stops answering shows up at once as up = 0. "
                "Pull also keeps the app simple: it only holds counters in memory and serves a page, and a slow monitoring server cannot block it. "
                "You can debug by opening the same page with curl. "
                "Push is still right for short batch jobs, through the Pushgateway, and Prometheus 3 can also accept OTLP pushes from OpenTelemetry."
            ),
        },
        {
            "q": "What is cardinality and why does it matter?",
            "a": (
                "Cardinality is the number of time series a metric creates, which is the product of the number of values of each label. "
                "Every series costs memory in the server and work for every query that touches it. "
                "A label with unbounded values, such as user IDs or raw URLs, can turn one metric into hundreds of thousands of series and slow or crash Prometheus. "
                "I keep labels to small fixed sets and put per-request details in logs or traces."
            ),
        },
        {
            "q": "When would you choose a histogram over a summary?",
            "a": (
                "Almost always, for request latency. A histogram exposes bucket counters, so you can add them up across all instances and then compute a percentile with histogram_quantile. "
                "A summary computes percentiles inside each process, and you cannot average percentiles from several processes into a correct total. "
                "Summaries can still make sense for one process when you need an exact percentile and never aggregate. "
                "The trade-off of a histogram is that its accuracy depends on the bucket limits you choose."
            ),
        },
    ],
    "deeper": {
        "minutes": 12,
        "body": (
            "Why does the lab run gunicorn with one worker process and four threads, when the Dockerfile from Day 16 runs two workers? Because of how counters live in memory.\n\n"
            "Gunicorn starts separate worker processes. Each Python process has its own copy of every counter, and each scrape of `/metrics` is answered by whichever worker is free. "
            "I started the plain image with two workers, sent 10 requests at once, and then read `/metrics` six times:\n"
            "- `hello_requests_total{path=\"/\"} 3.0`\n"
            "- `hello_requests_total{path=\"/\"} 7.0`\n"
            "- then 3, 3, 3 and 7 again.\n\n"
            "Neither number is the truth (10). Worse, Prometheus sees the counter drop from 7 to 3, treats it as a restart, and `rate()` counts the jump as new requests. "
            "Your request rate looks higher than it is, and it jumps around.\n\n"
            "The [Python client docs](https://github.com/prometheus/client_python/blob/master/docs/content/multiprocess/_index.md) say it directly: client libraries assume a threaded model, where all workers share the metrics. "
            "You have three fixes:\n"
            "- One process per container, with threads for concurrency. The lab does this, and Kubernetes adds more pods when you need more capacity.\n"
            "- The client's multiprocess mode: every worker writes to files in a shared folder, and `/metrics` adds them up. It has limits, listed in that doc.\n"
            "- A language whose runtime is one process with many threads, such as the JVM. A Spring Boot app has one set of counters however many requests it serves at once.\n\n"
            "The threads matter for a second reason. With one worker and one thread, I froze Redis with `docker compose pause redis`. "
            "Every request to `/` then hung for more than 10 seconds while the Redis client waited and retried. "
            "The scrape of `/metrics` waited behind them, failed after 10 seconds with `context deadline exceeded`, and `up` went to 0. "
            "The app was alive but Prometheus was blind, and the error counters it needed never arrived. "
            "With four threads, one thread can answer the scrape while others wait on Redis.\n\n"
            "Try the first experiment yourself: `docker run --rm -p 8001:8000 hello-devops:1.0.0` runs the image's own two-worker command. "
            "Send a burst of parallel requests with `for i in $(seq 10); do curl -s localhost:8001/ > /dev/null & done`, then read `/metrics` a few times."
        ),
    },
    "sources": [src("overview"), src("data_model"), src("metric_types"), src("storage")],
}
