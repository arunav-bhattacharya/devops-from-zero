"""Book-voice rewrite of d50 (Prometheus: architecture and the data model). Writer: tg."""
import json, pathlib

P = pathlib.Path("/home/user/devops-from-zero/content/p12.json")
d = json.loads(P.read_text())
L = next(x for x in d["lessons"] if x["id"] == "d50")

L["opening"] = (
    "Picture a hospital ward at night. Beside each bed, a small screen shows the patient's heart rate and "
    "temperature right now. At 3 a.m. a doctor asks a simple question: when did the fever in bed 4 start? The "
    "screen cannot say. It only knows the present. So a nurse walks the ward every 15 minutes and writes every "
    "number on a chart, with the time and the bed.\n\n"
    "It is easy to think the live screen is enough, because it is right there and always up to date. Our app has "
    "the same blind spot: its page of numbers shows only this moment.\n\n"
    "Last time, we wrote an SLO for hello-devops on paper, with no real numbers behind it. In this lesson, we'll "
    "start the nurse on her rounds. We'll run Prometheus next to the app, read the app's page of numbers line by "
    "line, and find the one careless change that can fill the chart room overnight.\n\n"
    "Before we start, make a guess, and keep it in mind."
)

L["guess"]["q"] = (
    "hello-devops crashes and stops answering. How does Prometheus, the tool that collects its numbers, find out?"
)
L["guess"]["why"] = (
    "Prometheus fetches the numbers itself. After every fetch it records an `up` value for the app: 1 if the "
    "fetch worked, 0 if it failed. A dead app cannot send anything."
)

plains = {
    "Target": "One address Prometheus reads numbers from, such as web:8000/metrics.",
    "Scrape": "One fetch of a target's /metrics page, repeated on a fixed timer.",
    "Exporter": "A small program that reads numbers from something else, such as a Linux machine, and shows them on a /metrics page.",
    "Time series": "All the stored readings for one metric name plus one exact set of label values.",
    "Label": "A name and value pair on a metric, such as status=\"500\", used to split and filter.",
    "Sample": "One value with a timestamp, stored each time a series is scraped.",
    "Cardinality": "How many time series a metric creates: every new combination of label values is a new series.",
    "Histogram": "A metric that counts measurements, such as request times, into buckets with upper limits.",
}
for t in L["terms"]:
    t["plain"] = plains[t["term"]]

S = L["sections"]

S[0]["h"] = "The nurse comes to the bed: why Prometheus pulls"
S[0]["body"] = (
    "hello-devops, our tiny lab app that greets every visitor and counts the visits, already keeps its count in "
    "memory. It shows the number on a web page at `/metrics`. That page is the screen beside the bed: it shows "
    "the value right now. Nothing remembers what it was ten minutes ago, so you cannot tell whether traffic is "
    "rising or when errors started.\n\n"
    "Prometheus is the nurse with the chart. It is a server, a program that runs all the time, that collects "
    "numbers from your programs every few seconds. It stores each number with a timestamp, and that stored "
    "history is what you graph and alert on.\n\n"
    "Prometheus collects by pulling. Your app shows its current numbers on that plain page, and Prometheus "
    "fetches the page on a timer. One fetch is a scrape. The thing it scrapes is a target, one bed on the round.\n\n"
    "Pulling sounds backwards if you know logging, where the app sends its lines out. It has real advantages:\n"
    "- Prometheus knows which targets should exist. If one does not answer, it records `up = 0` for it, a health check you get for free.\n"
    "- You can read the same page yourself with `curl`, the tool that fetches a web address, while you debug.\n"
    "- A slow or broken monitoring server never blocks your app. The app only keeps a few counters in memory.\n\n"
    "That first point answers the guess. A nurse who finds an empty bed writes \"no reading\" on the chart. A "
    "patient who has left cannot phone in to say so.\n\n"
    "Pushing still has a place. A batch job, a script that runs once and exits, may last 20 seconds and finish "
    "before any scrape. For that case the docs describe the Pushgateway, a place where such jobs can leave their "
    "result. The docs say [it is usually only right]"
    "(https://github.com/prometheus/docs/blob/main/docs/practices/pushing.md) for the result of service-level "
    "batch jobs. Prometheus 3 can also receive metrics pushed over OTLP, the OpenTelemetry protocol you meet on "
    "Day 57.\n\n"
    "We know how a number gets fetched. Next, we'll see what the nurse carries on her round."
)

S[1]["h"] = "What Prometheus is made of: server, targets and exporters"
S[1]["body"] = (
    "One Prometheus server is a single program with four jobs:\n"
    "- A scraper that fetches every target each `scrape_interval` (default 1 minute; the lab uses 15 seconds).\n"
    "- A time series database (TSDB) on local disk, the chart room.\n"
    "- A rule engine that runs recording rules (Day 51) and alerting rules (Day 52).\n"
    "- A web UI and HTTP API that answer PromQL queries.\n\n"
    "The UI is the web page you click in. The API is the same service for other programs. PromQL is Prometheus's "
    "language for asking questions of the stored numbers, and it gets a whole lesson next time.\n\n"
    "You list targets in `prometheus.yml` under `scrape_configs`. Each entry is a job: a group of targets that do "
    "the same work. The lab has four jobs: `prometheus` (it scrapes itself), `hello-devops`, `node` and "
    "`alertmanager`.\n\n"
    "In a big system you do not type addresses. Containers and servers come and go, and each new one has a new "
    "address. Service discovery asks the platform for the current list instead. Kubernetes, Docker, AWS and plain "
    "files are all supported. In the ward, it is the nurse checking the admissions list before each round, "
    "instead of a list of beds written last week.\n\n"
    "Many programs have no `/metrics` page. An exporter fills the gap: it reads numbers from the system and shows "
    "them in Prometheus format. Each one listens on a port, a numbered door on the machine:\n"
    "- [node_exporter](https://github.com/prometheus/node_exporter) shows CPU, memory, disk and network for a Linux machine, on port 9100.\n"
    "- [blackbox_exporter](https://github.com/prometheus/blackbox_exporter) probes other services from outside (HTTP, TCP, DNS), on port 9115.\n\n"
    "One warning for your Mac. Docker Desktop runs containers inside a small Linux virtual machine, a computer "
    "made of software. So the node_exporter container in the lab reports that virtual machine, not macOS. That is "
    "fine for learning PromQL; just do not read it as your laptop's numbers.\n\n"
    "Now we know who visits whom. Next, we'll read one page the way Prometheus does."
)

S[2]["h"] = "Reading a /metrics page line by line"
S[2]["body"] = (
    "Open `localhost:8000/metrics` and you see the exposition format: plain text, one sample per line. Here are "
    "the first lines for the app's own counter:\n"
    "- `# HELP hello_requests_total Requests served` is the description.\n"
    "- `# TYPE hello_requests_total counter` is the metric type.\n"
    "- `hello_requests_total{path=\"/\"} 3.0` is the metric name, its labels in braces, and the current value.\n\n"
    "A label is a name and a value attached to a number, such as `path=\"/\"`. It says which part of the app the "
    "number is about, like the bed number on a chart.\n\n"
    "The rest of the page has three sources:\n"
    "- `app.py` defines `hello_requests_total`. It counts visits to `/` and has one label, `path`.\n"
    "- `observability/red_metrics.py` adds `hello_responses_total` (with `path` and `status`) and the histogram `hello_request_duration_seconds`. Compose loads it next to the unchanged app; Day 52 explains how.\n"
    "- The Python client library, `prometheus_client`, adds `process_*` metrics (memory, CPU, open files) and `python_*` metrics for free.\n\n"
    "A client library is ready-made code that your app uses to keep and show its numbers.\n\n"
    "Two details look odd at first. The Python client adds a `_created` series next to each counter, holding the "
    "time it was created; you can ignore it. And the names follow conventions from the [naming "
    "guide](https://github.com/prometheus/docs/blob/main/docs/practices/naming.md). It asks for base units such "
    "as seconds and bytes, `_total` at the end of counters, and a prefix for the app.\n\n"
    "Prometheus 3 is strict about the HTTP `Content-Type` header of this page. A header is a short line of "
    "information sent before the page itself, and this one tells Prometheus which of several formats to parse. "
    "If it is missing or wrong, the scrape fails. Client libraries set it for you.\n\n"
    "Each line of the page is one reading. Next, we'll see what Prometheus builds out of many readings."
)

S[3]["h"] = "A time series is a name plus labels"
S[3]["body"] = (
    "A hospital chart has one row for each patient and each measurement: bed 4's temperature, bed 4's heart rate, "
    "bed 5's temperature. Prometheus works the same way. Everything it stores and queries is a time series, and "
    "each **time series** is identified by its metric name plus the exact set of label values. Change any label "
    "value and you have a different series.\n\n"
    "The app's page shows `hello_responses_total` three times, with three label sets: `/` and 200, `/healthz` and "
    "200, `/` and 500. That is three time series. Each scrape adds one sample to each: a timestamp and a value. "
    "With a 15-second scrape, one minute of the series for `/` and 200 could look like this:\n"
    "- 14:00:00, value 99\n"
    "- 14:00:15, value 167\n"
    "- 14:00:30, value 235\n"
    "- 14:00:45, value 303\n\n"
    "A graph of that series is these points joined by a line. Prometheus keeps only what the counter read at each "
    "scrape, never the single requests in between. The nurse writes down the temperature at each visit, not every "
    "change between visits.\n\n"
    "Prometheus adds two labels of its own when it stores them:\n"
    "- `job`: the job name from `prometheus.yml`, here `hello-devops`.\n"
    "- `instance`: the target's address, here `web:8000`.\n\n"
    "So the full name of one series in the lab is "
    "`hello_responses_total{instance=\"web:8000\", job=\"hello-devops\", path=\"/\", status=\"500\"}`. If you know "
    "databases, the labels work like a combined key, and each scrape adds a row to every key.\n\n"
    "Prometheus also writes a few series per target that the app never showed. `up` is 1 or 0 for each scrape, "
    "and `scrape_duration_seconds` tells you how long it took. When a scrape takes longer than `scrape_timeout` "
    "(10 seconds by default), it fails with `context deadline exceeded`, and `up` becomes 0.\n\n"
    "All series look alike in storage, but they do not all mean the same kind of thing. Next, the four types."
)

S[4]["h"] = "Four kinds of number: counter, gauge, histogram and summary"
S[4]["body"] = (
    "A nurse's chart mixes kinds of numbers. A count of doses given only grows. A temperature goes up and down. "
    "Every metric in Prometheus also has one of four types, and the type tells you which questions it can answer.\n\n"
    "A counter only goes up, or drops to zero when the process restarts. A process is one running copy of a "
    "program. `hello_responses_total` and `process_cpu_seconds_total` are counters. The raw value only says how "
    "many since the process started, so 303 tells you little on its own. The useful number is how fast it grows.\n\n"
    "In the series above, the counter grew by 204 in 45 seconds, about 4.5 requests a second. That is a rate, and "
    "the PromQL function `rate()` (Day 51) works it out for every series, even across restarts.\n\n"
    "A gauge is a value that goes up and down: memory in use, queue length, temperature. For example, the app's "
    "`process_resident_memory_bytes` read 48,803,840 bytes (about 49 MB) in one test run. You read a gauge as it "
    "is. Never take its `rate()`: that function treats every drop as a restart, and a gauge drops all the time.\n\n"
    "A histogram counts measurements into buckets. Each bucket has an upper limit, the `le` label (less than or "
    "equal), and the buckets are cumulative: each one includes all the smaller ones. In one run, the app's `/` "
    "route showed `le=\"0.005\"` 759 and `le=\"0.01\"` 1009. So 759 requests took 5 ms or less, and 1009 took 10 ms "
    "or less. Next to the buckets come `_sum` (all the seconds added up) and `_count` (how many).\n\n"
    "Each bucket is itself a counter. Day 51 takes their rates to estimate a percentile, and the buckets of many "
    "servers can be added up first.\n\n"
    "A summary computes percentiles inside the app and shows them with a `quantile` label. Prometheus itself has "
    "one: `go_gc_duration_seconds{quantile=\"0.5\"}`. Summaries from several servers cannot be combined, because you "
    "cannot average percentiles. That is why the [docs](https://prometheus.io/docs/practices/histograms/) usually "
    "point you to histograms.\n\n"
    "Quick rule: counting events, use a counter; measuring a level, a gauge; timing things or sizes, a histogram.\n\n"
    "Histograms are the most useful type, and also the hungriest. Next, we'll count what they cost."
)

S[5]["h"] = "Why user IDs never go in labels: cardinality"
S[5]["body"] = (
    "Imagine the hospital decides to add a chart row for every visitor, not just every patient. Nobody notices on "
    "the first day. By the end of the month the chart room is full and the nurse cannot finish a round.\n\n"
    "A label is one extra word in your code, so it looks free. In Prometheus, each new label value creates new "
    "series. Prometheus holds every active series in memory, and each one also costs disk and query time. The "
    "number of series a metric creates is its cardinality.\n\n"
    "Count the app's histogram. It has one label, `path`, and the default buckets give 15 `le` values. Each path "
    "therefore costs 15 bucket series plus `_sum`, `_count` and `_created`, and the counter adds 2 more. In the "
    "lab, one request to a new route took the `hello_*` series from 44 to 64.\n\n"
    "Suppose someone adds a `user_id` label so they can see requests per user. With 10,000 users, that is 200,000 "
    "series for one route, from one copy of the app. The [instrumentation "
    "guide](https://prometheus.io/docs/practices/instrumentation/) suggests keeping most metrics under 10 series. "
    "It says to look hard at anything that could pass 100.\n\n"
    "**A label with no fixed list of values is a leak with a slow start. Keep labels small and fixed.**\n\n"
    "Rules that keep you safe:\n"
    "- Labels hold small, fixed sets of values: status code, HTTP method, route pattern.\n"
    "- Never put user IDs, email addresses, request IDs or raw URLs in labels.\n"
    "- Record the route pattern, not the URL. `red_metrics.py` uses Flask's rule, so `/nope` and `/admin.php` both become `unmatched`.\n"
    "- Details about single requests belong in logs and traces (Part 14).\n\n"
    "Flask is the small Python web framework hello-devops is built on, and a rule is its name for a route "
    "pattern. For scale: the whole lab, with all four jobs, holds about 2,200 series.\n\n"
    "Series pile up over time as well as across labels. Next, we'll see where they are kept, and for how long."
)

S[6]["h"] = "Where the chart is kept: storage, retention and Prometheus 3"
S[6]["body"] = (
    "The TSDB keeps the newest samples in memory. It also appends each one to a write-ahead log on disk, a "
    "running diary written before anything else, so a crash does not lose them. Later it writes them to disk in "
    "two-hour blocks, and merges old blocks in the background.\n\n"
    "How long data is kept is called retention. By default it is 15 days (`--storage.tsdb.retention.time`); the "
    "lab keeps 7. The [storage docs](https://prometheus.io/docs/prometheus/latest/storage/) say plainly that local "
    "storage is not clustered or replicated. In plain words, there is one copy, on one machine. For months of "
    "history or a backup, you send data elsewhere, which Day 52 covers.\n\n"
    "Prometheus 3.0 came out in November 2024, the first major version in seven years. Two changes matter for "
    "this course:\n"
    "- A new web UI. The Query page has Table, Graph and Explain tabs, and Explore metrics in its menu lists every metric name.\n"
    "- Some old flags were removed. Tutorials written for Prometheus 2 may show flags that no longer start.\n\n"
    "A flag is an option you add to a command, such as the retention setting above. Go deeper lists the other "
    "changes, which matter once you mix Prometheus with OpenTelemetry. The details are in the [Prometheus 3.0 "
    "announcement](https://prometheus.io/blog/2024/11/14/prometheus-3-0/).\n\n"
    "That one copy on one machine is the honest limit of today's setup. It also cannot do anything with what it "
    "stores until we ask it the right questions. We have the chart, but so far we have only glanced at it. Next "
    "time we'll learn PromQL and turn those rows of counters into rates, error ratios and percentiles."
)

# The hospital round carries the analogy; the cardinality section carries the label mistake.
L.pop("analogy", None)
L.pop("mistake", None)
L["real_world"] = (
    "Cardinality is easiest to catch before the code is merged. Picture a payments company where every service "
    "has a /metrics page, and Prometheus finds the pods through Kubernetes service discovery. Its code review "
    "checklist asks one question about every new label: how many values can it have? A `merchant_id` label would "
    "mean one series per merchant per route per bucket, so merchant-level detail goes into logs instead."
)

W = L["worked"]["steps"]
W[0]["say"] = (
    "Start only the services this lesson needs, from the `observability` folder, and keep a request loop running "
    "in a second terminal. Compose starts Redis too, because `web` depends on it."
)
W[1]["say"] = (
    "Read one metric family straight from the app. One name, three label combinations, so three time series. "
    "Redis had been stopped for a few minutes earlier, which is where the 500 line comes from."
)
W[2]["say"] = (
    "Ask Prometheus how many `hello_*` series it stores. A small shell function saves typing. It runs `promtool`, "
    "the command line tool inside the Prometheus container, against the server's API."
)
W[3]["say"] = (
    "Split that count by metric name. The buckets are the big part: 2 routes (`/` and `/healthz`) times 15 `le` "
    "values is 30."
)
W[4]["say"] = (
    "Now add one new label value: call a route nobody had called yet, then count again after the next scrape. One "
    "request to `/readyz` added 20 series."
)
W[5]["say"] = (
    "Do the maths for a `user_id` label with 10,000 users on one route, then compare with the whole lab. One "
    "careless label would make this single app 90 times bigger than everything Prometheus stores today."
)

T = L["task"]
T["steps"] = [
    "Add the three files above to `observability/` in your repo, then start `web`, `prometheus` and `node-exporter` with Compose. Stop the Day 21 stack first if it is still running, because both use port 8000.",
    "Open Status, then Target health in the Prometheus UI. Find the four jobs. One of them is down: read its error message and explain why it is down today.",
    "Run `curl -s localhost:8000/metrics` and find one counter, one gauge and one histogram. Write down the `# TYPE` line for each.",
    "In the Query page, run `up` in the Table tab. Then stop node-exporter with Compose, wait 30 seconds and run it again.",
    "Start node-exporter again. Run `count by (job) ({__name__=~\".+\"})` and note which job has the most series.",
    "Change `scrape_interval` in `prometheus.yml` from 15s to 5s, check the file with promtool, reload Prometheus and confirm the new value on the Status, Configuration page.",
    "Set the interval back to 15s and reload again.",
]
T["hints"] = [
    "The down target's error mentions a lookup that failed. Which service in compose.yaml did you not start?",
    "`process_resident_memory_bytes` is a gauge, and anything ending in `_bucket` belongs to a histogram.",
    "Reloading needs `curl -X POST`; a plain GET to `/-/reload` is refused.",
]
T["done_when"] = (
    "Target health shows hello-devops, node and prometheus as UP, you can explain why alertmanager is DOWN, and you "
    "have one counter, one gauge and one histogram from the app's page."
)

L["explain_back"]["prompt"] = (
    "Explain to a teammate in 3 to 4 sentences how a number in app.py ends up stored in Prometheus. Mention the "
    "/metrics page, the scrape, labels and what makes one time series different from another."
)
L["explain_back"]["answer"] = (
    "The app keeps counters in memory and prints their current values on its /metrics page in a simple text "
    "format. Every 15 seconds Prometheus scrapes that page, adds job and instance labels, and stores one "
    "timestamped sample per series. A series is the metric name plus one exact set of label values, so "
    "hello_responses_total with status 200 and with status 500 are two series. That is why every new label value "
    "costs a new series, and why user IDs never go in labels."
)

L["recap"] = [
    "Prometheus pulls: it scrapes each target's /metrics page on a timer and records up = 0 when a scrape fails.",
    "One server scrapes, stores samples, runs rules and answers PromQL; exporters give /metrics pages to things that have none.",
    "A time series is a metric name plus one exact set of label values; Prometheus adds job and instance.",
    "Counters only go up, gauges go up and down, histograms count into cumulative buckets, and summaries cannot be combined.",
    "Every new label value is a new series, so keep labels to small fixed sets and never use user IDs or raw URLs.",
    "Data stays on one machine's disk for 15 days by default, in a single copy; longer history has to go elsewhere.",
]

C = L["check"]
C[0]["q"] = (
    "A metric `orders_total` has labels `country` (40 values) and `payment_method` (5 values), and it runs on 3 "
    "instances. At most how many series can it create?"
)
C[0]["why"] = "Series multiply across labels: 40 times 5 times 3 instances is 600."
C[1]["q"] = "You want to track how many jobs are waiting in a queue right now. Which metric type fits?"
C[1]["why"] = "Queue length goes up and down, which is what a gauge measures."
C[2]["q"] = (
    "A nightly backup script runs for 30 seconds and then exits. Prometheus scrapes every minute. What is the usual "
    "way to get its result into Prometheus?"
)
C[2]["why"] = (
    "A short batch job may finish between scrapes, and recording its result is the main case the Pushgateway "
    "exists for."
)

I = L["interview"]
I[0]["a"] = (
    "With pull, Prometheus knows the full list of targets, so a target that stops answering shows up at once as "
    "up = 0. Pull also keeps the app simple: it only holds counters in memory and serves a page, and a slow "
    "monitoring server cannot block it. You can debug by opening the same page with curl. Push is still right for "
    "short batch jobs, through the Pushgateway, and Prometheus 3 can also accept OTLP pushes from OpenTelemetry."
)
I[1]["a"] = (
    "Cardinality is the number of time series a metric creates, which is the product of the number of values of "
    "each label. Every series costs memory in the server and work for every query that touches it. A label with "
    "unbounded values, such as user IDs or raw URLs, can turn one metric into hundreds of thousands of series. "
    "That can slow or crash Prometheus. I keep labels to small fixed sets and put per-request details in logs or "
    "traces."
)
I[2]["a"] = (
    "Almost always, for request latency. A histogram exposes bucket counters, so you can add them up across all "
    "instances and then compute a percentile with histogram_quantile. A summary computes percentiles inside each "
    "process, and you cannot average percentiles from several processes into a correct total. Summaries can still "
    "make sense for one process when you need an exact percentile and never combine them. The trade-off of a "
    "histogram is that its accuracy depends on the bucket limits you choose."
)

L["deeper"]["body"] = (
    "Why does the lab run gunicorn with one worker process and four threads, when the Dockerfile from Day 22 runs "
    "two workers? Because of how counters live in memory. Gunicorn is the program that runs the app's web server, "
    "and a thread is a line of work inside one process.\n\n"
    "Gunicorn starts separate worker processes. Each Python process has its own copy of every counter, and each "
    "scrape of `/metrics` is answered by whichever worker is free. In a test run, the plain image with two workers "
    "got 10 requests at once, and `/metrics` was read six times:\n"
    "- `hello_requests_total{path=\"/\"} 3.0`\n"
    "- `hello_requests_total{path=\"/\"} 7.0`\n"
    "- then 3, 3, 3 and 7 again.\n\n"
    "Neither number is the truth (10). Worse, Prometheus sees the counter drop from 7 to 3, treats it as a "
    "restart, and `rate()` counts the jump as new requests. Your request rate looks higher than it is, and it "
    "jumps around.\n\n"
    "The [Python client docs](https://github.com/prometheus/client_python/blob/master/docs/content/multiprocess/_index.md) "
    "say it directly: client libraries assume a threaded model, where all workers share the metrics. You have "
    "three fixes:\n"
    "- One process per container, with threads for concurrency. The lab does this, and Kubernetes adds more pods when you need more capacity.\n"
    "- The client's multiprocess mode: every worker writes to files in a shared folder, and `/metrics` adds them up. It has limits, listed in that doc.\n"
    "- A language whose runtime is one process with many threads, such as the JVM. A Spring Boot app has one set of counters however many requests it serves at once.\n\n"
    "The threads matter for a second reason. In another test with one worker and one thread, Redis was frozen "
    "with `docker compose pause redis`. Every request to `/` then hung for more than 10 seconds while the Redis "
    "client waited and retried. The scrape of `/metrics` waited behind them, failed after 10 seconds with "
    "`context deadline exceeded`, and `up` went to 0. The app was alive but Prometheus was blind, and the error "
    "counters it needed never arrived. With four threads, one thread can answer the scrape while others wait on "
    "Redis.\n\n"
    "Try the first experiment yourself: `docker run --rm -p 8001:8000 hello-devops:1.0.0` runs the image's own "
    "two-worker command. Send a burst of parallel requests with "
    "`for i in $(seq 10); do curl -s localhost:8001/ > /dev/null & done`, then read `/metrics` a few times.\n\n"
    "Last, the other Prometheus 3 changes. Metric and label names may use any UTF-8 characters, such as dots from "
    "OpenTelemetry, and such names need quotes in PromQL. An OTLP receiver, turned on with "
    "`--web.enable-otlp-receiver`, lets OpenTelemetry apps push metrics in. Native histograms, a more precise kind "
    "of histogram, are stable since 3.8 but stay off unless you turn them on."
)

L["closing"] = (
    "We started on a night ward, with a screen that only knew the present and a doctor who wanted the past. Now "
    "hello-devops has its nurse: Prometheus walks to `/metrics` every 15 seconds, writes each reading into a time "
    "series, and notes `up = 0` when a bed is empty. In the lab, open the app's `/metrics` page and count the label "
    "values on one histogram; that count is what every new route costs.\n\n"
    "Next, we'll learn to read the chart. How do you turn a counter that only goes up into requests per second, "
    "an error ratio and a p95?"
)

P.write_text(json.dumps(d, indent=1, ensure_ascii=False) + "\n")
print("d50 written")
