# Prometheus and Grafana for a beginner DevOps course (research notes, as of 30 October 2026)

How these notes were verified. Versions come from `git ls-remote --tags` on each GitHub repo, from CHANGELOG files read on raw.githubusercontent.com, and from the Docker Hub tags API, which also gave each image's push date and CPU architectures. Docs were read from the source repos (`prometheus/docs`, `prometheus/prometheus/docs`, `grafana/grafana/docs/sources`, `grafana/loki/docs`), cloned with git. prometheus.io, grafana.com, sre.google and youtube.com could not be fetched from this sandbox, so every URL on those domains comes from WebSearch results. URLs are tagged: **[S]** means it appeared in a search result, **[G]** means the file was opened through git or raw.githubusercontent.com, and **[H]** means it was checked with the Docker Hub API. **[R]** marks something I ran in this sandbox: Prometheus 3.15.1, Alertmanager 0.34.2 and node_exporter 1.12.1 as linux-amd64 binaries, plus prometheus_client 0.26.0 with Flask 3.1.3, plus the `grafana/grafana:13.3.0` container. These are the same versions as the images, but the run was on x86_64 Linux, not a Mac. YouTube channel names could not be confirmed (the oEmbed lookup and page fetches were blocked), so the notes give video titles as search results showed them and mark any attribution as unconfirmed.

## Lesson 1 – Observability foundations (monitoring vs observability, signals, golden signals, RED/USE, SLIs/SLOs/error budgets, alerting on symptoms)

### Takeaway
Start with the user's experience. The four golden signals, RED and USE are three lenses on the same question. SLOs turn "is it good enough?" into a number with a budget. Pages should fire on symptoms users feel (high error rate or latency, budget burning fast), not on causes (high CPU).

### Cited Findings

#### Concepts in teaching order (one line plus an intuition each)
1. **Monitoring vs observability.** Monitoring means collecting and alerting on known signals so you can tell whether a system is healthy. Observability means you can ask new questions of the telemetry when something unexpected breaks. The SRE book's monitoring chapter separates white-box from black-box monitoring and symptoms from causes. *Intuition:* monitoring is a car's dashboard warning lights; observability is being able to plug in and ask why. — SRE book ch. 6 "Monitoring Distributed Systems" (URL named in a search summary but not opened: https://sre.google/sre-book/monitoring-distributed-systems/); secondary summary at [SRE book notes](https://bitmaybewise.substack.com/p/sre-book-notes-monitoring-distributed) [S]
2. **The signals.** Metrics are cheap numeric time series. Logs are timestamped event text. Traces follow one request across services. Profiles show where CPU and memory go in the code. Grafana's all-in-one dev image bundles "Prometheus (metrics), Tempo (traces), Loki (logs), Pyroscope (profiles), and Grafana", and Alloy describes itself as supporting "metrics, logs, traces, and profiles". *Intuition:* metrics tell you *that* something is wrong, traces *where*, logs *what happened*, profiles *which line of code is expensive*. — [docker-otel-lgtm README](https://github.com/grafana/docker-otel-lgtm) [S][G]; [Alloy README](https://github.com/grafana/alloy) [G]
3. **Four golden signals: latency, traffic, errors, saturation.** "If you can only measure four metrics of your user-facing system, focus on these four." These come from SRE book ch. 6, written by Rob Ewaschuk. — [Distributed Monitoring 101](https://medium.com/forepaas/distributed-monitoring-101-the-four-golden-signals-305bbbc33d35) [S]; [Grafana dashboard best practices](https://grafana.com/docs/grafana/latest/dashboards/build-dashboards/best-practices/) [S] (source: [best-practices/index.md](https://github.com/grafana/grafana/blob/main/docs/sources/visualizations/dashboards/build-dashboards/best-practices/index.md) [G]) lists them as "Latency – time taken to serve a request; Traffic – how much demand; Errors – rate of requests that are failing; Saturation – how 'full' your system is".
4. **RED (for services): Rate, Errors, Duration.** Tom Wilkie devised it around 2015 as a microservices counterpart to USE. The golden signals are roughly RED plus saturation. — [The RED Method (Grafana blog)](https://grafana.com/blog/the-red-method-how-to-instrument-your-services/) [S]
5. **USE (for resources): Utilization, Saturation, Errors.** For every resource (CPU, memory, disk, NIC) check utilization (the time the resource was busy), saturation (extra work it can't service, often queued) and errors (count of error events). Gregg notes that any non-zero saturation adds latency. — [The USE Method](https://www.brendangregg.com/usemethod.html) [S]; [USE Linux checklist](https://brendangregg.com/USEmethod/use-linux.html) [S]
6. **How RED and USE fit together.** Grafana's guidance: "The USE method tells you how happy your machines are, the RED method tells you how happy your users are. USE reports on causes of issues. RED reports on user experience and is more likely to report symptoms… alerting should be done on RED dashboards." — [best-practices/index.md](https://github.com/grafana/grafana/blob/main/docs/sources/visualizations/dashboards/build-dashboards/best-practices/index.md) [G]
7. **SLI, SLO, SLA.** An SLI is a measured indicator, such as the fraction of successful requests. An SLO is the target for that SLI. An SLA is the contract with consequences. SRE book ch. 4 recommends allowing "an error budget — a rate at which the SLOs can be missed — and track that on a daily or weekly basis". — [SRE book: Service Level Objectives](https://sre.google/sre-book/service-level-objectives/) [S]
8. **Error budget = 1 − SLO.** The book's example: a 99.999% SLO gives an error budget of a 0.001% failure rate per quarter. Releases continue while budget remains and "are temporarily halted" once it is spent. *Intuition:* the budget is permission to take risks such as deploys and experiments. — [SRE book: Embracing Risk](https://sre.google/sre-book/embracing-risk/) [S]
9. **Alert on symptoms, and on burn rate.** Prometheus's own guidance: "keep alerting simple, alert on symptoms, have good consoles to allow pinpointing causes, and avoid having pages where there is nothing to do… Only page on latency at one point in a stack." For batch jobs, page if the job hasn't succeeded recently, allowing at least 2 full runs. — [prometheus/docs practices/alerting.md](https://github.com/prometheus/docs/blob/main/docs/practices/alerting.md) [G]. Multiwindow, multi-burn-rate alerting fires only when the burn rate is over threshold in both a long and a short window. A common pair pages at 14.4x burn over 1h with a 5m short window (2% of a 30-day budget gone in an hour) and opens a ticket at about 6x over 6h (5%). — [How to alert on SLOs (Google Cloud, Medium)](https://medium.com/google-cloud/how-to-alert-on-slos-2a5ce8c4e7dd) [S]; original source is SRE Workbook "Alerting on SLOs" (URL named in a search summary but not opened: https://sre.google/workbook/alerting-on-slos/)

#### Misconceptions to address
- "More alerts = safer." Prometheus docs: "Aim to have as few alerts as possible, by alerting on symptoms that are associated with end-user pain rather than trying to catch every possible way that pain could be caused." — [practices/alerting.md](https://github.com/prometheus/docs/blob/main/docs/practices/alerting.md) [G]
- "Aim for 100%." The SRE book argues against 100% reliability targets and treats the availability target as both a minimum and a maximum. — [Embracing Risk](https://sre.google/sre-book/embracing-risk/) [S]
- "CPU at 90% is an outage." That is a USE/cause signal and belongs on dashboards; users feel RED/symptom signals. — [Grafana best practices](https://grafana.com/docs/grafana/latest/dashboards/build-dashboards/best-practices/) [S]

#### Worked example (SLO burn-rate rule for the lab's Flask app; checked with `promtool check rules` on 3.15.1 [R], "SUCCESS: 3 rules found")
```yaml
groups:
  - name: hello-slo
    rules:
      - record: job:hello_request_errors:ratio_rate5m
        expr: sum by (job) (rate(hello_requests_total{status=~"5.."}[5m])) / sum by (job) (rate(hello_requests_total[5m]))
      - record: job:hello_request_errors:ratio_rate1h
        expr: sum by (job) (rate(hello_requests_total{status=~"5.."}[1h])) / sum by (job) (rate(hello_requests_total[1h]))
      # SLO: 99.9% of requests succeed over 30 days -> error budget 0.1%
      - alert: HelloErrorBudgetFastBurn
        expr: |
          job:hello_request_errors:ratio_rate1h > (14.4 * 0.001)
          and
          job:hello_request_errors:ratio_rate5m > (14.4 * 0.001)
        labels: {severity: page}
        annotations:
          summary: "hello is burning its 30-day error budget at >14x (2% of budget per hour)"
```
Burn-rate thresholds are from the Medium/SRE Workbook material above. Rule syntax follows the [recording rules](https://prometheus.io/docs/practices/rules/) [S] and [alerting tutorial](https://prometheus.io/docs/tutorials/alerting_based_on_metrics/) [S] docs.

#### Hands-on exercise ideas
- Classify 10 candidate alerts ("CPU > 80%", "p99 latency > 1s for 10m", "disk 90% full", "5xx ratio > 2%", "pod restarted") as symptom or cause, and as page, ticket or dashboard-only.
- Compute error budgets: 99.9% over 30 days is 43.2 minutes of total failure (0.001 × 43,200 min); 99.99% is 4.32 minutes. Discuss what each allows for deploys.
- Draw RED for the Flask app and USE for the laptop's CPU, memory and disk, then map each to a node_exporter metric in Lesson 2.

#### Resources (curated)
- SRE book, Monitoring Distributed Systems: https://sre.google/sre-book/monitoring-distributed-systems/ (named in a search summary; not opened)
- SRE book, Service Level Objectives: https://sre.google/sre-book/service-level-objectives/ [S]
- SRE book, Embracing Risk: https://sre.google/sre-book/embracing-risk/ [S]
- Medium (Google Cloud), How to alert on SLOs: https://medium.com/google-cloud/how-to-alert-on-slos-2a5ce8c4e7dd [S]
- Tom Wilkie, The RED Method: https://grafana.com/blog/the-red-method-how-to-instrument-your-services/ [S]
- Brendan Gregg, The USE Method: https://www.brendangregg.com/usemethod.html [S]
- Grafana dashboard best practices (golden signals, RED and USE side by side): https://grafana.com/docs/grafana/latest/dashboards/build-dashboards/best-practices/ [S]

### Inferences
- RED, USE and the golden signals overlap heavily: golden signals ≈ RED + saturation. One way to frame it: RED for anything that serves requests, USE for anything that gets consumed, and golden signals as Google's name for the combination.
- Profiles are the newest of the four signals for most learners. A single mention plus a Pyroscope demo in Lesson 6 is enough at beginner level.

### Gaps
- Could not open sre.google pages (DNS blocked here), so I couldn't confirm exact quotes or the SRE Workbook's tier table. Burn-rate numbers come from a Google Cloud Medium article and search summaries. The lesson writer should check https://sre.google/workbook/alerting-on-slos/ directly.
- No YouTube video specifically on RED/USE/SLOs turned up in the searches I ran.

## Lesson 2 – Prometheus architecture and data model

### Takeaway
Prometheus is a pull-based, single-binary TSDB. It scrapes HTTP `/metrics` endpoints (targets) on an interval and stores each unique set of metric name + labels as its own time series. Labels give the power and drive the cost. Current release: **3.15.1 (2026-10-21)**. LTS lines: 3.5, with patches through 3.5.5 on 2026-07-08; 3.13 is still getting patches (3.13.5 on 2026-10-21).

### Cited Findings

#### Current versions (verified 30 Oct 2026)
| Component | Latest | Release date | Docker image (arm64 verified [H]) |
|---|---|---|---|
| Prometheus | v3.15.1 | 2026-10-21 | `prom/prometheus:v3.15.1` |
| Alertmanager | v0.34.2 | 2026-10-29 | `prom/alertmanager:v0.34.2` |
| node_exporter | v1.12.1 | 2026-07-14 | `prom/node-exporter:v1.12.1` |
| blackbox_exporter | v0.29.1 | 2026-10-21 | `prom/blackbox-exporter:v0.29.1` |
| Pushgateway | v1.11.5 | (image pushed 2026-10-21) | `prom/pushgateway:v1.11.5` |
| client_python | v0.26.0 | — | `pip install prometheus-client` |
Dates come from each project's CHANGELOG: [Prometheus](https://github.com/prometheus/prometheus/blob/main/CHANGELOG.md), [Alertmanager](https://github.com/prometheus/alertmanager/blob/main/CHANGELOG.md), [node_exporter](https://github.com/prometheus/node_exporter/blob/master/CHANGELOG.md) and [blackbox](https://github.com/prometheus/blackbox_exporter/blob/master/CHANGELOG.md) [G]. Image tags were checked on Docker Hub [H]. macOS arm64 tarballs exist for Prometheus, Alertmanager and node_exporter on GitHub releases (HTTP 200 checked) [G].
- LTS policy: "selected releases of Prometheus that receive selected bug fixes for an extended period of one year… Every 6 weeks, a new Prometheus minor release cycle begins". — [release-cycle.md](https://github.com/prometheus/docs/blob/main/docs/introduction/release-cycle.md) [G]

#### Concepts in teaching order
1. **Pull model.** "time series collection happens via a pull model over HTTP; pushing time series is supported via an intermediary gateway" for short-lived jobs. *Intuition:* Prometheus calls your service; your service doesn't call Prometheus. A failed scrape is itself a signal: `up == 0`. — [overview.md](https://github.com/prometheus/docs/blob/main/docs/introduction/overview.md) [G]. "Usually, the only valid use case for the Pushgateway is for capturing the outcome of a service-level batch job." — [practices/pushing.md](https://github.com/prometheus/docs/blob/main/docs/practices/pushing.md) [G]
2. **Targets, jobs and the scrape config.** `global.scrape_interval` defaults to **1m**, `scrape_timeout` to 10s and `evaluation_interval` to 1m. Most tutorials set 15s. — [configuration.md](https://github.com/prometheus/prometheus/blob/main/docs/configuration/configuration.md) [G]
3. **Service discovery.** Prometheus finds targets dynamically from Kubernetes, AWS, Docker, file_sd, http_sd and others. Recent releases show active SD work: unified AWS SD added in 3.8.0, Docker SD gained `__meta_docker_container_image` in 3.15.0, and the UI shows relabeling steps per target since 3.8.0. — [Prometheus CHANGELOG](https://github.com/prometheus/prometheus/blob/main/CHANGELOG.md) [G]
4. **Exporters.** These translate third-party systems into Prometheus metrics. node_exporter exposes host metrics on port **9100**. Its collectors cover Linux and also Darwin (cpu, diskstats, filesystem, loadavg…). Running it in a container "for host monitoring" needs `--net=host --pid=host`, a `/:/host` bind mount and `--path.rootfs=/host`. — [node_exporter README](https://github.com/prometheus/node_exporter) [G]. blackbox_exporter probes endpoints from the outside on port **9115** (`/probe?target=…&module=http_2xx`). — [blackbox_exporter README](https://github.com/prometheus/blackbox_exporter) [G]. Guidance on writing exporters: https://prometheus.io/docs/instrumenting/writing_exporters/ [S]
5. **Time series = metric name + labels.** "Every time series is uniquely identified by its metric name and optional key-value pairs called labels." Since 3.0, names "MAY use any UTF-8 characters" but "SHOULD match `[a-zA-Z_:][a-zA-Z0-9_:]*`" for compatibility; other names must be quoted in PromQL. — [data_model.md](https://github.com/prometheus/docs/blob/main/docs/concepts/data_model.md) [G]
6. **Exposition format.** This is the text you see at `/metrics`: `# HELP`, `# TYPE`, then `name{labels} value`. Since 3.0, a missing or invalid Content-Type fails the scrape instead of silently falling back; the `fallback_scrape_protocol` setting covers it. 3.15.0 added the OpenMetrics 2.0 scrape format. — [exposition formats](https://prometheus.io/docs/instrumenting/exposition_formats/) [S]; [CHANGELOG](https://github.com/prometheus/prometheus/blob/main/CHANGELOG.md) [G]
7. **Four metric types.** *Counter*: only goes up, resets on restart, so "use the rate() function". *Gauge*: a snapshot value that can go up or down; "never take a rate() of a gauge". *Histogram*: bucketed counts that can be aggregated across instances. *Summary*: quantiles computed client-side that can't be aggregated, so the docs generally favor histograms. — [Understanding metric types](https://prometheus.io/docs/tutorials/understanding_metric_types/) [S]; [Histograms and summaries](https://prometheus.io/docs/practices/histograms/) [S]; [metric_types.md](https://github.com/prometheus/docs/blob/main/docs/concepts/metric_types.md) [G]
8. **Naming.** Use base units (seconds, bytes), expose ratios rather than percentages, use the `_total` suffix for counters, never build names procedurally (use labels instead), and reserve `_sum`, `_count` and `_bucket` for histograms and summaries. — [naming.md](https://github.com/prometheus/docs/blob/main/docs/practices/naming.md) [G]; [Instrumentation](https://prometheus.io/docs/practices/instrumentation/) [S]
9. **TSDB and retention.** Samples are grouped into **two-hour blocks** plus a write-ahead log (WAL). Blocks are compacted in the background, up to 10% of retention time. `--storage.tsdb.retention.time` defaults to **15d** if neither it nor `retention.size` is set. — [storage.md](https://github.com/prometheus/prometheus/blob/main/docs/storage.md) [G]
10. **Cardinality.** "try to keep the cardinality of your metrics below 10… If you have a metric that has a cardinality over 100 or the potential to grow that large, investigate alternate solutions." "Do not use labels to store dimensions with high cardinality… such as user IDs, email addresses". — [instrumentation.md](https://github.com/prometheus/docs/blob/main/docs/practices/instrumentation.md) [G]; [naming.md](https://github.com/prometheus/docs/blob/main/docs/practices/naming.md) [G]. Brian Brazil: performance "almost always comes down to one thing: label cardinality", and per-customer labels tend to fail once customers number in the hundreds or thousands. — [Cardinality is key](https://www.robustperception.io/cardinality-is-key/) [S]

#### Example config (the lab's `prometheus.yml`; validated with `promtool check config` [R])
```yaml
global:
  scrape_interval: 15s       # default is 1m
  evaluation_interval: 15s   # how often rules are evaluated (default 1m)
rule_files:
  - /etc/prometheus/rules.yml
alerting:
  alertmanagers:
    - static_configs:
        - targets: ["alertmanager:9093"]
scrape_configs:
  - job_name: prometheus
    static_configs: [{targets: ["localhost:9090"]}]
  - job_name: node
    static_configs: [{targets: ["node-exporter:9100"]}]
  - job_name: hello
    static_configs: [{targets: ["app:8000"]}]
```
Observed output [R], `up` after the first scrapes:
```
up{instance="localhost:9100", job="node"}       1
up{instance="localhost:9090", job="prometheus"} 1
up{instance="localhost:8000", job="hello"}      1
```
Observed `/metrics` from the Flask app [R]. The Python client adds `_total` to counters automatically ([counter docs](https://github.com/prometheus/client_python/blob/master/docs/content/instrumenting/counter.md) [G]) and by default also emits a `_created` series. You can turn that off with `PROMETHEUS_DISABLE_CREATED_SERIES=True` or `disable_created_metrics()` ([instrumenting docs](https://github.com/prometheus/client_python/blob/master/docs/content/instrumenting/_index.md) [G]).
```
# HELP hello_requests_total Hello requests served
# TYPE hello_requests_total counter
hello_requests_total{path="/",status="200"} 11.0
# HELP hello_requests_created Hello requests served
# TYPE hello_requests_created gauge
hello_request_duration_seconds_bucket{le="0.05",path="/"} 3.0
```
Cardinality in the toy lab [R]: `count({__name__=~".+"})` returned **1600** series (Prometheus self-metrics plus node_exporter plus app). `topk(3, count by (__name__) ({__name__=~".+"}))` returned `prometheus_http_requests_total` 64, `node_scrape_collector_duration_seconds` 49 and `node_scrape_collector_success` 49.

#### Misconceptions
- "Prometheus is a log/event store." It stores numeric samples. Per-event detail such as user IDs belongs in logs or traces. — [naming.md](https://github.com/prometheus/docs/blob/main/docs/practices/naming.md) [G]
- "Use Pushgateway to push metrics from my service." It is meant only for service-level batch jobs. — [pushing.md](https://github.com/prometheus/docs/blob/main/docs/practices/pushing.md) [G]
- "Prometheus keeps data forever." The default is 15 days, after which you need remote storage (Lesson 4). — [storage.md](https://github.com/prometheus/prometheus/blob/main/docs/storage.md) [G]
- "node_exporter in Docker on my Mac shows my Mac." See Inferences.

#### Hands-on exercise ideas
- Open `localhost:9090/targets`, stop the app container and watch `up` go to 0. Restart it and watch the counter reset to 0, which motivates `rate()` in Lesson 3.
- `curl localhost:8000/metrics`: find HELP/TYPE lines, the `_total` suffix, `_created` and the histogram `_bucket{le=…}` lines.
- Add a `user_id` label to the counter, hit the app with 1,000 random IDs, and re-run `count({__name__=~"hello.*"})` to see series explode. Then revert.
- Add blackbox_exporter and probe `http://app:8000/` with module `http_2xx`, using the `/probe` pattern from its README.

#### Resources (curated)
- Docs, Understanding metric types: https://prometheus.io/docs/tutorials/understanding_metric_types/ [S]
- Docs, Instrumentation best practices: https://prometheus.io/docs/practices/instrumentation/ [S]
- Docs source, data model: https://github.com/prometheus/docs/blob/main/docs/concepts/data_model.md [G]
- Docs source, storage/retention: https://github.com/prometheus/prometheus/blob/main/docs/storage.md [G]
- Robust Perception, Cardinality is key: https://www.robustperception.io/cardinality-is-key/ [S]
- Video, "Introduction to the Prometheus Monitoring System": https://www.youtube.com/watch?v=STVMGrYIlfg [S]. The search summary describes it as "straight from the co-founder of Prometheus"; channel not confirmed.
- Video, "How Prometheus Monitoring works": https://www.youtube.com/watch?v=h4Sl21AKiDg [S]. Beginner architecture overview (server, Pushgateway, Alertmanager, pull vs push). Believed to be TechWorld with Nana, but the channel is unconfirmed. Related playlist "Prometheus Monitoring Full Tutorial": https://www.youtube.com/playlist?list=PLy7NrYWoggjxCF3av5JKwyG7FFF9eLeL4 [S]
- PromLabs YouTube channel ("Prometheus Monitoring with Julius"): https://www.youtube.com/@PromLabs [S]

### Inferences
- **Mac caveat:** on Docker Desktop, containers run inside a Linux VM, so a `prom/node-exporter` container reports that VM's CPU, memory and disk, not macOS. The README's container instructions (`--pid=host`, `/:/host`) assume a Linux host. To monitor the Mac itself, run the `darwin-arm64` node_exporter binary natively; its Darwin collectors are listed in the README. Present the containerized one as "monitoring the Docker VM", which is still fine for learning PromQL. Scraping a native exporter from containerized Prometheus usually goes via `host.docker.internal:9100` on Docker Desktop. I did not verify that hostname in this session.
- Python's automatic `_total` and `_created` series surprise beginners. Show them on purpose in the `/metrics` walkthrough.

### Gaps
- Could not read the generated LTS table on prometheus.io. I'm inferring "3.5 = LTS (patched to 3.5.5 on 2026-07-08); 3.13 = next LTS" from tag activity: 3.13.x gets patches alongside 3.15.x while 3.14.x does not. Confirm at prometheus.io/docs/introduction/release-cycle/.
- Did not confirm whether prometheus_client 0.26.0 can expose native histograms.

## Lesson 3 – PromQL from zero

### Takeaway
Teach in this order: selectors → instant vs range vectors → `rate()` on counters → aggregate after rate (`sum by`) → `histogram_quantile` over summed buckets → `offset` and binary ops → recording rules. The lab run produced concrete, surprising outputs: a `[10s]` range returns nothing, `increase()` is fractional, a fresh `rate5m` under-reports, and p95 estimates exceed the real max. Those make memorable teaching moments.

### Cited Findings

#### Concepts in teaching order
1. **Instant vector vs range vector.** An instant vector is "a single sample for each time series, all sharing the same timestamp". A range vector is "a range of data points over time for each time series". — [querying/basics.md](https://github.com/prometheus/prometheus/blob/main/docs/querying/basics.md) [G]. *Intuition:* a photo vs a short video clip of every series.
2. **Selectors and matchers:** `=`, `!=`, `=~`, `!~`. Regexes are fully anchored, and since 3.0 `.` matches all characters. UTF-8 names use the quoted form, e.g. `{"http.server.request.duration", "service.name"="api"}`. — [basics.md](https://github.com/prometheus/prometheus/blob/main/docs/querying/basics.md) [G]; [CHANGELOG 3.0.0](https://github.com/prometheus/prometheus/blob/main/CHANGELOG.md) [G]
3. **Lookback and staleness.** An instant selector returns the newest sample less than **5 minutes** old (`--query.lookback-delta`). Series that disappear are marked stale. — [basics.md](https://github.com/prometheus/prometheus/blob/main/docs/querying/basics.md) [G]
4. **`rate()`** is "the per-second average rate of increase… Breaks in monotonicity (such as counter resets due to target restarts) are automatically adjusted for… extrapolates to the ends of the time range". It is "best suited for alerting, and for graphing of slow-moving counters", and you should "always take a rate() first, then aggregate". — [functions](https://prometheus.io/docs/prometheus/latest/querying/functions/) [S]; [functions.md](https://github.com/prometheus/prometheus/blob/main/docs/querying/functions.md) [G]
5. **`irate()`** uses only the last two samples. Use it "only… when graphing volatile, fast-moving counters. Use rate for alerts… as brief changes in the rate can reset the FOR clause". — [functions.md](https://github.com/prometheus/prometheus/blob/main/docs/querying/functions.md) [G]; [Avoid irate() in alerts](https://www.robustperception.io/avoid-irate-in-alerts/) [S]; counterpoint [Irate graphs are better graphs](https://www.robustperception.io/irate-graphs-are-better-graphs/) [S]
6. **`increase()`** is rate × window seconds, "syntactic sugar" for readability; use `rate` in recording rules. Because of extrapolation it can return non-integers even for integer counters. — [functions](https://prometheus.io/docs/prometheus/latest/querying/functions/) [S]; [PromLabs: How exactly does PromQL calculate rates?](https://promlabs.com/blog/2021/01/29/how-exactly-does-promql-calculate-rates/) [S]
7. **Range size.** The rule of thumb is a range of at least 4× the scrape interval. — [What range should I use with rate()?](https://www.robustperception.io/what-range-should-i-use-with-rate/) [S]
8. **Aggregation:** `sum by (…)`, `sum without (…)`, `avg`, `max`, `count`, `topk(k, …)`. "Rate then sum, never sum then rate." — [Rate then sum…](https://www.robustperception.io/rate-then-sum-never-sum-then-rate/) [S]
9. **`histogram_quantile`** over classic buckets: `histogram_quantile(0.9, sum by (job, le) (rate(http_request_duration_seconds_bucket[10m])))`. Keep `le` in the `by` clause. Averaging precomputed quantiles (`avg(…{quantile="0.95"})`) is explicitly flagged as **BAD**. With native histograms there is no `le`: `histogram_quantile(0.9, sum by (job) (rate(http_request_duration_seconds[10m])))`. — [Histograms and summaries](https://prometheus.io/docs/practices/histograms/) [S]; [Native histograms spec](https://prometheus.io/docs/specs/native_histograms/) [S]; [How does a Prometheus Histogram work?](https://www.robustperception.io/how-does-a-prometheus-histogram-work/) [S]
10. **`offset`** shifts a selector back in time, e.g. `http_requests_total offset 5m`. — [basics.md](https://github.com/prometheus/prometheus/blob/main/docs/querying/basics.md) [G]
11. **Binary operators and vector matching:** arithmetic and comparisons between vectors, matched on labels, with `on`/`ignoring` and `group_left`/`group_right`. New in **3.10.0** (2026-02-24): `fill()`, `fill_left()` and `fill_right()` modifiers supply default values for missing series. — [CHANGELOG](https://github.com/prometheus/prometheus/blob/main/CHANGELOG.md) [G]
12. **Recording rules** precompute expensive queries. Name them `level:metric:operations` and drop `_total` for rate-based rules. — [Recording rules](https://prometheus.io/docs/practices/rules/) [S]
13. **Newer, optional extras** (mention only): `anchored` and `smoothed` range modifiers (experimental behind `promql-extended-range-selectors` since 3.7.0; the main-branch feature-flag docs now say that flag "is now a no-op" and both are on by default) and duration expressions (on by default since 3.14.0). — [feature_flags.md](https://github.com/prometheus/prometheus/blob/main/docs/feature_flags.md) [G]; [CHANGELOG](https://github.com/prometheus/prometheus/blob/main/CHANGELOG.md) [G]

#### Queries with observed output (Prometheus 3.15.1 [R]; ~10 req/s of traffic, ~5% synthetic 500s, scrape every 15s, run about 85s after start)
```
hello_requests_total
  {job="hello",path="/",status="200"} 491
  {job="hello",path="/",status="500"} 21
hello_requests_total[1m]                       -> 4 samples per series (15s scrape)
rate(hello_requests_total[1m])                 -> status=200: 5.42   status=500: 0.222
irate(hello_requests_total[1m])                -> status=200: 5.47   status=500: 0.067   (noisier)
increase(hello_requests_total[1m])             -> status=200: 325.33 status=500: 13.33   (non-integer!)
sum by (job) (rate(hello_requests_total[1m]))  -> {job="hello"} 5.64
sum without (instance, path) (rate(hello_requests_total[1m])) -> {job="hello",status="200"} 5.42, {…status="500"} 0.222
histogram_quantile(0.95, sum by (le) (rate(hello_request_duration_seconds_bucket[1m]))) -> 0.211
job:hello_requests:rate5m   (recording rule over [5m])  -> 1.69   (vs 5.64 from the [1m] query)
job:hello_request_errors:ratio_rate5m                   -> 0.035
100 * (1 - avg by (instance) (rate(node_cpu_seconds_total{mode="idle"}[1m]))) -> 33.45
rate(hello_requests_total[10s])                         -> (empty result)
hello_requests_total offset 1m                          -> 200: 165, 500: 9
```
Recording rules used (validated with promtool [R]):
```yaml
- record: job:hello_requests:rate5m
  expr: sum by (job) (rate(hello_requests_total[5m]))
- record: job:hello_request_errors:ratio_rate5m
  expr: |
    sum by (job) (rate(hello_requests_total{status=~"5.."}[5m]))
    /
    sum by (job) (rate(hello_requests_total[5m]))
```

#### Misconceptions (with the lab evidence)
- **Range too short:** `rate(x[10s])` with a 15s scrape returned *nothing* [R]. A range needs at least two samples, so use ≥4× the scrape interval. — [RP: what range](https://www.robustperception.io/what-range-should-i-use-with-rate/) [S]
- **Sum then rate:** breaks counter-reset handling. — [functions.md](https://github.com/prometheus/prometheus/blob/main/docs/querying/functions.md) [G]
- **Averaging percentiles** (`avg` of a `quantile` label) is mathematically wrong; aggregate buckets, then compute the quantile. — [Histograms and summaries](https://prometheus.io/docs/practices/histograms/) [S]
- **Raw counter graphs:** they look like ever-rising lines with sawtooth drops at restarts; rate them. — [Understanding metric types](https://prometheus.io/docs/tutorials/understanding_metric_types/) [S]
- **irate in alerts:** a brief dip resets `for:`. — [RP](https://www.robustperception.io/avoid-irate-in-alerts/) [S]
- **Expecting integers from `increase()`:** see the observed 325.33 above. — [PromLabs](https://promlabs.com/blog/2021/01/29/how-exactly-does-promql-calculate-rates/) [S]

#### Hands-on exercise ideas
- "Fix my query" set: `rate(x[10s])`, `rate(sum(x)[5m])` (needs a subquery and is wrong anyway), `avg(quantile)`, `sum(rate(bucket[5m]))` without `le`.
- Compare `rate` and `irate` on a 1h graph in the Prometheus UI and describe the difference.
- Use the 3.x UI's "Explain" tab and PromLens-style tree view to dissect `histogram_quantile(0.95, sum by (le) (rate(...)))`. (The new UI has had these since 3.0 — [CHANGELOG](https://github.com/prometheus/prometheus/blob/main/CHANGELOG.md) [G].)
- Write the error-ratio recording rule, reload with `curl -X POST localhost:9090/-/reload` (needs `--web.enable-lifecycle`), and query the new series.

#### Resources (curated)
- Query functions: https://prometheus.io/docs/prometheus/latest/querying/functions/ [S]
- Query examples: https://prometheus.io/docs/prometheus/latest/querying/examples/ [S]
- Histograms and summaries: https://prometheus.io/docs/practices/histograms/ [S]
- PromLabs, How exactly does PromQL calculate rates?: https://promlabs.com/blog/2021/01/29/how-exactly-does-promql-calculate-rates/ [S]
- Robust Perception, Rate then sum, never sum then rate: https://www.robustperception.io/rate-then-sum-never-sum-then-rate/ [S]
- Video, "Intro to PromQL with Julius Volz": https://www.youtube.com/watch?v=MPN0SLE5YWk [S]
- Video, "Introduction to Prometheus, PromQL, & PromLens" (Rawkode with Julius Volz per a Class Central listing): https://www.youtube.com/watch?v=GDWZisTxnQ8 [S]
- Video, "Taking the Guesswork out of Your PromQL – Julius Volz": https://www.youtube.com/watch?v=3hKdcFwMozI [S]

### Inferences
- **Why rate5m = 1.69 while rate1m = 5.64:** the series had only existed for about 85s of the 300s window. `rate()` extrapolates only a little past the first sample and then divides by the full range, so new series under-report until the window fills. 5.64 × ~92s / 300s ≈ 1.7, which matches. This lines up with the extrapolation behavior PromLabs describes. Takeaway for students: right after a deploy or restart, long-window rates read low.
- **Why p95 = 0.211s when the app never sleeps more than 0.12s:** the 95th percentile fell inside the `(0.1, 0.25]` bucket and `histogram_quantile` interpolates linearly within the bucket. Bucket choice sets accuracy. This is a good lead-in to native histograms (Lesson 4).

### Gaps
- Didn't confirm which release will (or did) flip extended range selectors to on by default. The 3.15.0 changelog still calls them "experimental", while main-branch docs say the flag is a no-op.

## Lesson 4 – Alerting, Prometheus on Kubernetes, instrumentation, long-term storage, Prometheus 3 changes

### Takeaway
Prometheus evaluates alerting rules, and a `for:` duration filters out blips. Alertmanager then dedupes, groups, routes, inhibits and silences before notifying receivers. On Kubernetes, use kube-prometheus-stack (chart **92.16.0**, operator **v0.94.2**) and add scrape targets with ServiceMonitor/PodMonitor custom resources. A frequent gotcha: by default they must carry the Helm release label. Prometheus 3.x changes worth teaching: the new UI, UTF-8 names, the OTLP receiver, native histograms (stable since 3.8, still opt-in) and Remote Write 2.0.

### Cited Findings

#### Concepts in teaching order
1. **Alerting rules:** `alert`, `expr`, `for`, `labels`, `annotations`. Prometheus loads them via `rule_files` and sends them to Alertmanager via the `alerting` block. — [Alerting based on metrics tutorial](https://prometheus.io/docs/tutorials/alerting_based_on_metrics/) [S]. *Intuition for `for:`:* the condition must hold continuously for that long. Until then the alert is "pending", which absorbs blips.
2. **Alertmanager** "deduplicates them, groups them, and routes them to receivers", and also handles silencing and inhibition. — [Alertmanager overview](https://prometheus.io/docs/alerting/latest/alertmanager/) [S]
3. **Routing tree:** `route` with `receiver`, `group_by` and child `routes` with `matchers`; children inherit parent settings. Defaults: `group_wait` **30s**, `group_interval` **5m**, `repeat_interval` **4h**. — [configuration.md](https://github.com/prometheus/alertmanager/blob/main/docs/configuration.md) [G]; [Configuration](https://prometheus.io/docs/alerting/latest/configuration/) [S]
4. **Grouping** turns 50 alerts during an outage into one notification. **Inhibition** mutes target alerts while a source alert fires (e.g. "cluster down" mutes per-service alerts). **Silences** are temporary mutes created in the UI or `amtool`, not in the config file. — [Alertmanager overview](https://prometheus.io/docs/alerting/latest/alertmanager/) [S]
5. **Receivers** include `webhook_configs`, Slack, PagerDuty, email and others. Validate the config with `amtool check-config`. — [Configuration](https://prometheus.io/docs/alerting/latest/configuration/) [S]
6. **Instrumenting an app.** For Flask, mount `make_wsgi_app()` at `/metrics` with Werkzeug's `DispatcherMiddleware`. — [client_python Flask doc](https://github.com/prometheus/client_python/blob/master/docs/content/exporting/http/flask.md) [G]; docs site https://prometheus.github.io/client_python (linked from the [README](https://github.com/prometheus/client_python) [G])
7. **kube-prometheus-stack.** Install with `helm install [RELEASE_NAME] oci://ghcr.io/prometheus-community/charts/kube-prometheus-stack` (the README now leads with the OCI registry). Chart.yaml: `version: 92.16.0`, `appVersion: v0.94.2`. Dependencies: kube-state-metrics 8.8.0, prometheus-node-exporter 4.60.1, and **grafana 14.2.0 from `oci://ghcr.io/grafana-community/helm-charts`**. values.yaml pins Prometheus `v3.15.1-distroless`, Alertmanager `v0.34.2` and Thanos `v0.42.5`. — [kube-prometheus-stack chart](https://github.com/prometheus-community/helm-charts/tree/main/charts/kube-prometheus-stack) [G]
8. **Prometheus Operator CRDs:** `Prometheus`, `PrometheusAgent`, `Alertmanager`, `ServiceMonitor` ("declaratively specifies how groups of Kubernetes services should be monitored"), `PodMonitor`, `Probe`, `ScrapeConfig` (for targets outside the cluster), `PrometheusRule` and `AlertmanagerConfig`. — [Prometheus Operator README](https://github.com/prometheus-operator/prometheus-operator) [G]; [getting started (ServiceMonitors/PodMonitors)](https://github.com/prometheus-operator/prometheus-operator/blob/main/Documentation/developer/getting-started.md) (linked from the chart README [G])
9. **The selector gotcha:** "By default, Prometheus discovers PodMonitors and ServiceMonitors within its namespace, that are labeled with the same release tag as the prometheus-operator release". To select all of them, set `prometheus.prometheusSpec.serviceMonitorSelectorNilUsesHelmValues=false` (and the same for podMonitor). Both default to `true` in values.yaml. — [chart README / values.yaml](https://github.com/prometheus-community/helm-charts/tree/main/charts/kube-prometheus-stack) [G]
10. **Long-term storage and remote write.** Thanos is "a set of components that can be composed into a highly available metric system with unlimited storage capacity… on top of existing Prometheus deployments", storing blocks in object storage with a global query view (CNCF Incubating). Latest is v0.42.5. — [Thanos README](https://github.com/thanos-io/thanos) [G]. Grafana Mimir provides "scalable long-term storage for Prometheus", with a monolithic single-binary mode, object storage, multi-tenancy and HA. Latest is **mimir-3.2.3**. — [Mimir README](https://github.com/grafana/mimir) [G]. Prometheus sends samples out via `remote_write`. Remote Write 2.0 receiving follows spec 2.0-rc.4 as of 3.8.0, which renamed "created timestamp" to "start timestamp". — [CHANGELOG](https://github.com/prometheus/prometheus/blob/main/CHANGELOG.md) [G]; [Remote write tuning](https://github.com/prometheus/docs/blob/main/docs/practices/remote_write.md) [G]
11. **What changed in Prometheus 3.x**, from the [CHANGELOG](https://github.com/prometheus/prometheus/blob/main/CHANGELOG.md) [G] and the [Prometheus 3.0 blog](https://prometheus.io/blog/2024/11/14/prometheus-3-0/) [S]:
    - **3.0.0 (2024-11-14):** "first new major version in seven years". It brought a **new UI** (PromLens-style tree view, metrics explorer, "Explain" tab; the old UI is available via `--enable-feature=old-ui`, which is still in feature_flags.md) and **UTF-8 metric and label names on by default**. The **OTLP receiver** is enabled with `--web.enable-otlp-receiver`, at endpoint `/api/v1/otlp/v1/metrics` (per the blog summary). Also: agent mode stable (`--agent`); range selectors and lookback became left-open; `holt_winters` renamed `double_exponential_smoothing`; scrapes fail on a missing Content-Type unless `fallback_scrape_protocol` is set; GOMAXPROCS and GOMEMLIMIT are set automatically. Migration guide: https://prometheus.io/docs/prometheus/3.0/migration/ (linked from the CHANGELOG [G]).
    - **3.5.0 (2025-07-14):** experimental `__type__` and `__unit__` labels (`type-and-unit-labels`); OTLP resource-attribute promotion options.
    - **3.8.0 (2025-11-28):** "Native histograms are now a stable, but optional feature, use the `scrape_native_histograms` config setting." **3.9.0 (2026-01-06):** the `native-histogram` feature flag became a no-op. `scrape_native_histograms` still defaults to `false` ([configuration.md](https://github.com/prometheus/prometheus/blob/main/docs/configuration/configuration.md) [G]).
    - **3.10.0 (2026-02-24):** `fill()` binop modifiers. **3.12.0 (2026-05-28):** start-timestamp-aware `rate()` behind a flag. **3.14.0 (2026-08-17):** duration expressions on by default. **3.15.0 (2026-09-24):** OpenMetrics 2.0 scrape format, scraping over Unix domain sockets, XOR2 chunk encoding stabilized, runtime log level via config. **3.15.1 (2026-10-21):** security fixes.
    - OTLP and UTF-8 how-tos: [OpenTelemetry guide](https://github.com/prometheus/docs/blob/main/docs/guides/opentelemetry.md) and [UTF-8 guide](https://github.com/prometheus/docs/blob/main/docs/guides/utf8.md) [G].

#### Example configs (validated and run [R])
`rules.yml` (alert part; `promtool check rules` → "SUCCESS: 4 rules found"):
```yaml
- alert: HelloTargetDown
  expr: up{job="hello"} == 0
  for: 1m
  labels: {severity: page}
  annotations:
    summary: "hello app on {{ $labels.instance }} is not being scraped"
- alert: HelloHighErrorRatio
  expr: job:hello_request_errors:ratio_rate5m > 0.02
  for: 5m
  labels: {severity: ticket}
  annotations:
    summary: "More than 2% of hello requests are failing ({{ $value | humanizePercentage }})"
```
`alertmanager.yml` (`amtool check-config` SUCCESS; `amtool config routes` printed the tree below [R]):
```yaml
route:
  receiver: tickets              # default receiver for anything not matched below
  group_by: ["alertname", "job"]
  group_wait: 10s                # default 30s
  group_interval: 1m             # default 5m
  repeat_interval: 1h            # default 4h
  routes:
    - matchers: ['severity="page"']
      receiver: pager
receivers:
  - name: pager
    webhook_configs: [{url: "http://webhook:5001/alert?team=pager", send_resolved: true}]
  - name: tickets
    webhook_configs: [{url: "http://webhook:5001/alert?team=tickets", send_resolved: true}]
inhibit_rules:
  - source_matchers: ['alertname="HelloTargetDown"']
    target_matchers: ['alertname="HelloHighErrorRatio"']
    equal: ["job"]
```
```
$ amtool config routes --config.file=alertmanager.yml
└── default-route  receiver: tickets
    └── {severity="page"}  receiver: pager
$ amtool config routes test --config.file=alertmanager.yml alertname=HelloTargetDown severity=page   ->  pager
$ amtool config routes test ... alertname=HelloHighErrorRatio severity=ticket                         ->  tickets
```
Observed end to end [R], with `for:` shortened to 20–30s for the demo:
```
# webhook receiver stdout
WEBHOOK status=firing alertname=HelloHighErrorRatio labels={'alertname': 'HelloHighErrorRatio', 'job': 'hello', 'severity': 'ticket'} summary=More than 2% of hello requests are failing (3.125%)
# ...after stopping the app:
WEBHOOK status=firing alertname=HelloTargetDown labels={'alertname': 'HelloTargetDown', 'instance': 'localhost:8000', 'job': 'hello', 'severity': 'page'} ...
# Alertmanager API: inhibition worked
HelloTargetDown      state=active
HelloHighErrorRatio  state=suppressed  inhibitedBy=[...]
# silence
$ amtool silence add alertname=HelloTargetDown --duration=1h --comment="planned maintenance" --author=student
HelloTargetDown      state=suppressed  silencedBy=[...]
```
Rule unit test (`promtool test rules rules_test.yml` → `SUCCESS` [R]):
```yaml
rule_files: [rules.yml]
evaluation_interval: 15s
tests:
  - interval: 15s
    input_series:
      - series: 'up{job="hello", instance="app:8000"}'
        values: '1 1 1 0 0 0 0 0 0'
    alert_rule_test:
      - eval_time: 2m
        alertname: HelloTargetDown
        exp_alerts:
          - exp_labels: {job: hello, instance: "app:8000", severity: page}
            exp_annotations: {summary: "hello app on app:8000 is not being scraped"}
```
ServiceMonitor for the app on kind (**not run**: assembled from the Operator README and chart docs; `release:` must match your Helm release name because of the selector default above):
```yaml
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: hello
  namespace: monitoring
  labels:
    release: kps            # = helm release name
spec:
  namespaceSelector: {matchNames: [default]}
  selector: {matchLabels: {app: hello}}
  endpoints:
    - port: http            # named port on the Service
      path: /metrics
      interval: 15s
```

#### Misconceptions
- **Alerting on causes**, e.g. "CPU > 80%". See Lesson 1. — [practices/alerting.md](https://github.com/prometheus/docs/blob/main/docs/practices/alerting.md) [G]
- **No `for:`, or `irate` in alert expressions.** Both make alerts flap. — [RP: Avoid irate() in alerts](https://www.robustperception.io/avoid-irate-in-alerts/) [S]
- **"Silences go in alertmanager.yml."** They don't: silences are runtime objects. — [Alertmanager overview](https://prometheus.io/docs/alerting/latest/alertmanager/) [S]
- **"My ServiceMonitor is ignored."** This is usually the missing `release` label. — [chart README](https://github.com/prometheus-community/helm-charts/tree/main/charts/kube-prometheus-stack) [G]
- **"Prometheus is HA, long-term storage out of the box."** It isn't: default retention is 15d on local disk. Use Thanos, Mimir or a remote-write backend. — [storage.md](https://github.com/prometheus/prometheus/blob/main/docs/storage.md) [G]

#### Hands-on exercise ideas
- Lab: the error-ratio alert fires and goes to `tickets`. Stop the app and HelloTargetDown fires to `pager` while inhibiting the error-ratio alert. Add a silence, then restart the app and see `status=resolved`.
- Write a `promtool test rules` file for HelloHighErrorRatio.
- kind + kube-prometheus-stack: install, port-forward Grafana, deploy the hello app with a Service and ServiceMonitor, and confirm it appears under Status → Targets.
- Discussion: when would you pick Thanos (sidecar on existing Prometheus plus object storage) over Mimir (remote-write into a multi-tenant cluster) or Grafana Cloud?

#### Resources (curated)
- Alertmanager overview: https://prometheus.io/docs/alerting/latest/alertmanager/ [S]
- Alertmanager configuration: https://prometheus.io/docs/alerting/latest/configuration/ [S]
- Tutorial, Alerting based on metrics (webhook receiver): https://prometheus.io/docs/tutorials/alerting_based_on_metrics/ [S]
- kube-prometheus-stack chart: https://github.com/prometheus-community/helm-charts/tree/main/charts/kube-prometheus-stack [G]
- Prometheus Operator: https://github.com/prometheus-operator/prometheus-operator [G]
- Prometheus 3.0 announcement: https://prometheus.io/blog/2024/11/14/prometheus-3-0/ [S]
- Video, "Setup Prometheus Monitoring on Kubernetes using Helm and Prometheus Operator": https://www.youtube.com/watch?v=QoDqxm7ybLc [S] (I believe it's TechWorld with Nana, but couldn't confirm the channel. It is likely several years old, so chart values and versions will differ.)
- Video, "PromCon 2017: Best Practices and Beastly Pitfalls – Julius Volz": https://www.youtube.com/watch?v=_MNYuTNfTb4 [S] (old but still relevant on pitfalls)

### Inferences
- For a beginner course, show native histograms as "the future". Keep labs on classic histograms, since `scrape_native_histograms` defaults to false and Python client support wasn't confirmed.
- The kube-prometheus-stack's Grafana subchart now comes from a `grafana-community` OCI registry. Older tutorials that use `grafana/helm-charts` URLs or `helm repo add` will look different from the current README, which leads with OCI.
- Keep the webhook receiver in a separate container from the app. Otherwise the "app down" alert has nowhere to go (I hit this while designing the lab).

### Gaps
- Did not run kind + kube-prometheus-stack here: Docker Hub rate-limited (HTTP 429) most pulls. The ServiceMonitor YAML is untested, and resource needs on a Mac (Docker Desktop memory) are unverified.
- No KodeKloud YouTube result surfaced for Prometheus or Grafana in my searches.

## Lesson 5 – Grafana dashboards (data sources, panels, queries, transformations, variables, JSON, provisioning, design)

### Takeaway
Grafana is the UI layer. Data sources supply queries, panels visualize the results, transformations reshape them client-side, and variables make one dashboard serve many hosts or services. Teach "dashboard = JSON = code" early and provision it from files. Current release is **Grafana 13.3.0 (2026-10-27)**. Use the image `grafana/grafana:13.3.0` (OSS) or `grafana/grafana-enterprise:13.3.0` (free; Grafana's recommended default). `grafana/grafana-oss` is no longer updated after 12.4.0.

### Cited Findings

#### Concepts in teaching order
1. **Data sources.** Grafana queries existing stores (Prometheus, Loki, Tempo, SQL…); it doesn't store metrics itself. — [Data sources](https://grafana.com/docs/grafana/latest/datasources/) [S]
2. **Panels and visualizations, queries per panel (refId A, B…), units and thresholds.** See the lab dashboard below.
3. **Transformations** reshape query results in Grafana (join, filter fields, sort by…). Variables are interpolated before transformations run. — [Transform data](https://grafana.com/docs/grafana/latest/panels-visualizations/query-transform-data/transform-data/) [S]
4. **Variables and templating.** "Prevent sprawl by using template variables. For example, you don't need a separate dashboard for each node… you can make the data source a template variable too." Chained variables narrow one another, but each extra layer slows refresh, so list independent variables first. — [Best practices](https://grafana.com/docs/grafana/latest/dashboards/build-dashboards/best-practices/) [S]; [Advanced variables](https://grafana.com/docs/grafana/latest/visualizations/dashboards/variables/advanced-variables/) [S]
5. **Dashboard JSON and the v2 schema.** Classic dashboards are JSON (uid, title, panels with gridPos/targets, templating). Grafana 12 introduced a v2 schema and Kubernetes-style resources (`apiVersion: dashboard.grafana.app/v1`), and "You must use the Kubernetes resource format to provision dashboards v2 / dynamic dashboards." — [provisioning doc](https://github.com/grafana/grafana/blob/main/docs/sources/administration/provisioning/index.md) [G]; [What's new v12.0](https://github.com/grafana/grafana/blob/main/docs/sources/whatsnew/whats-new-in-v12/whats-new-in-v12-0.md) [G]
6. **Provisioning as code.** YAML files under `/etc/grafana/provisioning/{datasources,dashboards}` with `apiVersion: 1`. A dashboard provider points at a folder of JSON files. With `updateIntervalSeconds` ≤ 10 Grafana relies on filesystem watch events, which "Docker bind mounts" may not deliver, so set it above 10 to force polling. With `allowUiUpdates: false` you "can't save changes to a provisioned dashboard"; if UI edits are allowed, they're overwritten on the next file change. A UID in the JSON keeps URLs stable across instances. — [Provision Grafana](https://grafana.com/docs/grafana/latest/administration/provisioning/) [S]; [provisioning source](https://github.com/grafana/grafana/blob/main/docs/sources/administration/provisioning/index.md) [G]
7. **Good dashboard design.** "A dashboard should tell a story or answer a question"; "Dashboards should reduce cognitive load". Use a RED layout (request and error rate on the left, latency on the right, one row per service, ordered by data flow). "Compare like to like", normalize axes, and use hierarchical drill-down dashboards. In mature teams there is "No editing in the browser" and dashboards are generated by scripting libraries. The doc also describes low, medium and high maturity levels. — [best-practices/index.md](https://github.com/grafana/grafana/blob/main/docs/sources/visualizations/dashboards/build-dashboards/best-practices/index.md) [G]
8. **Images.** "Starting with Grafana release 12.4.0, the grafana/grafana-oss Docker Hub repository will no longer be updated… use the grafana/grafana Docker Hub repository". Editions are `grafana/grafana-enterprise` (the recommended default, free) and `grafana/grafana` (OSS). — [Docker install doc](https://github.com/grafana/grafana/blob/main/docs/sources/setup-grafana/installation/docker/index.md) [G]. Docker Hub: `grafana/grafana:13.3.0` and `grafana/grafana-enterprise:13.3.0` exist with amd64/arm/arm64 (pushed 2026-10-27); `grafana/grafana-oss:13.3.0` → 404. [H]

#### Example provisioning (run on `grafana/grafana:13.3.0` [R]: datasource provisioned, dashboard landed in folder "Course" with `provisioned: true`, variable `job` present, `/api/health` → `"version": "13.3.0"`, and a datasource query through `/api/ds/query` returned per-status series)
`grafana/provisioning/datasources/prometheus.yml`
```yaml
apiVersion: 1
datasources:
  - name: Prometheus
    type: prometheus
    uid: prometheus
    access: proxy
    url: http://prometheus:9090
    isDefault: true
```
`grafana/provisioning/dashboards/provider.yml`
```yaml
apiVersion: 1
providers:
  - name: course-dashboards
    folder: Course
    type: file
    allowUiUpdates: false
    updateIntervalSeconds: 30     # >10 forces polling; fs events may not cross Docker bind mounts
    options:
      path: /var/lib/grafana/dashboards
```
`grafana/dashboards/hello-red.json` (abridged; three panels = RED)
```json
{
  "uid": "hello-red", "title": "Hello app - RED", "schemaVersion": 41,
  "templating": {"list": [{"name": "job", "type": "query",
    "datasource": {"type": "prometheus", "uid": "prometheus"},
    "query": "label_values(hello_requests_total, job)", "refresh": 1}]},
  "panels": [
    {"type": "timeseries", "title": "Rate: requests per second by status",
     "fieldConfig": {"defaults": {"unit": "reqps"}},
     "targets": [{"refId": "A", "expr": "sum by (status) (rate(hello_requests_total{job=\"$job\"}[$__rate_interval]))", "legendFormat": "{{status}}"}]},
    {"type": "stat", "title": "Errors: share of requests failing",
     "fieldConfig": {"defaults": {"unit": "percentunit",
       "thresholds": {"mode": "absolute", "steps": [{"color": "green", "value": null}, {"color": "red", "value": 0.02}]}}},
     "targets": [{"refId": "A", "expr": "sum(rate(hello_requests_total{job=\"$job\",status=~\"5..\"}[$__rate_interval])) / sum(rate(hello_requests_total{job=\"$job\"}[$__rate_interval]))"}]},
    {"type": "timeseries", "title": "Duration: p50 / p95 latency", "fieldConfig": {"defaults": {"unit": "s"}},
     "targets": [
       {"refId": "A", "expr": "histogram_quantile(0.5, sum by (le) (rate(hello_request_duration_seconds_bucket{job=\"$job\"}[$__rate_interval])))", "legendFormat": "p50"},
       {"refId": "B", "expr": "histogram_quantile(0.95, sum by (le) (rate(hello_request_duration_seconds_bucket{job=\"$job\"}[$__rate_interval])))", "legendFormat": "p95"}]}
  ]
}
```
(The full tested file also includes `gridPos` and `datasource` per panel.) Observed API check [R]:
```
GET /api/search?query=Hello -> "Hello app - RED"  uid=hello-red  folder=Course
POST /api/ds/query  sum by (status) (increase(hello_requests_total[5m]))  -> {status="200"} 568.17, {status="500"} 22.17
```

#### Misconceptions
- **Giant dashboards / dashboard sprawl:** "Lots of copied dashboards… One-off dashboards that hang around forever" is the low-maturity state. — [best practices](https://grafana.com/docs/grafana/latest/dashboards/build-dashboards/best-practices/) [S]
- **Editing provisioned dashboards in the UI** and expecting the changes to persist: they don't write back to the files. — [provisioning](https://grafana.com/docs/grafana/latest/administration/provisioning/) [S]
- **A `$` in provisioning files:** environment-variable expansion means literal dollar signs must be escaped as `$$`. — [provisioning](https://grafana.com/docs/grafana/latest/administration/provisioning/) [S]
- **Using `grafana/grafana-oss` from old tutorials:** it stopped updating at 12.4.0. — [Docker install doc](https://github.com/grafana/grafana/blob/main/docs/sources/setup-grafana/installation/docker/index.md) [G]

#### Hands-on exercise ideas
- Build the RED dashboard by hand in the UI, export the JSON, diff it with the provisioned version, then delete the UI copy and keep the file.
- Add a `instance` variable chained to `job`, and a data-source variable.
- Use the "Organize fields" and "Sort by" transformations on a table of `topk(10, count by (__name__)({__name__=~".+"}))` to build a cardinality explorer.
- Critique a deliberately bad 40-panel dashboard against the best-practices checklist, then cut it to 6 panels that answer one question.

#### Resources (curated)
- Grafana dashboard best practices: https://grafana.com/docs/grafana/latest/dashboards/build-dashboards/best-practices/ [S]
- Provision Grafana: https://grafana.com/docs/grafana/latest/administration/provisioning/ [S]
- Transform data: https://grafana.com/docs/grafana/latest/panels-visualizations/query-transform-data/transform-data/ [S]
- Advanced variable configurations: https://grafana.com/docs/grafana/latest/visualizations/dashboards/variables/advanced-variables/ [S]
- Prometheus docs, Visualizing metrics using Grafana (tutorial source): https://github.com/prometheus/docs/blob/main/docs/tutorials/visualizing_metrics_using_grafana.md [G]
- Video, "Grafana 13 Deep Dive: Suggested Dashboards, Dynamic Dashboards, SQL Expressions, and More!": https://www.youtube.com/watch?v=giocvyAXO28&vl=fr [S] (GrafanaCON 2026 session; channel unconfirmed)
- Video, "Grafana Tutorial for Beginners": https://www.youtube.com/watch?v=vf5MJLoXUG0 [S] (channel and date unknown; preview before use)

### Inferences
- `$__rate_interval` is the usual Grafana recommendation for `rate()` inside panels because it adapts to the scrape interval and the zoom level. I used it in the tested dashboard, but none of the sources I read in this session documented it, so check the Grafana Prometheus data source docs before teaching specifics.
- With Grafana 13 moving to v2 and Kubernetes-format dashboards and Git Sync, teach classic JSON plus file provisioning first (it is simple and works offline), then show Git Sync and the v2 format as the direction of travel.

### Gaps
- The best-practices page is old: one search snippet describes it as about 1,400 days old. Newer guidance, such as dynamic dashboards (tabs, rows, conditional rendering), isn't reflected in it.
- I didn't test the dashboard v2 (`dashboard.grafana.app`) provisioning format.

## Lesson 6 – Grafana beyond dashboards (alerting, Loki/LogQL, Tempo, Pyroscope, Alloy, LGTM, Grafana Cloud free tier, dashboards as code, Grafana 12/13)

### Takeaway
LGTM means **L**oki (logs), **G**rafana, **T**empo (traces), **M**imir (metrics), with Pyroscope adding profiles and Alloy as the collector. For a laptop, the single `grafana/otel-lgtm` container (0.38.1, arm64) is the fastest way to see all signals. Grafana Alerting reuses the Prometheus alerting model (rules → instances → contact points and notification policies). Dashboards as code in 2026 means Git Sync (GA in 13.0), the Foundation SDK, the Terraform provider (v4.53.0), the Grafana Operator and the new `gcx` CLI. Grizzly and grafanactl are deprecated, and Grafonnet is still marked experimental.

### Cited Findings

#### Current versions [G tags/CHANGELOGs, H images]
| Component | Latest | Image |
|---|---|---|
| Grafana | 13.3.0 (2026-10-27) | `grafana/grafana:13.3.0` |
| Loki | 3.7.9 (image pushed 2026-10-20) | `grafana/loki:3.7.9` |
| Tempo | 3.1.1 (3.0.0 image pushed 2026-05-28) | `grafana/tempo:3.1.1` |
| Pyroscope | 2.4.2 | `grafana/pyroscope:2.4.2` |
| Alloy | v1.21.3 (1.21.0 released 2026-10-16) | `grafana/alloy:v1.21.3` |
| Mimir | 3.2.3 | `grafana/mimir:3.2.3` |
| otel-lgtm | 0.38.1 (2026-10-26) | `grafana/otel-lgtm:0.38.1` |
| Thanos | v0.42.5 | `thanosio/thanos:v0.42.5` |
| Terraform provider | v4.53.0 | — |
| Foundation SDK | v0.0.22 | — |
| gcx CLI | v1.7.1 | — |
All images listed have arm64 builds [H].

#### Concepts in teaching order
1. **Grafana Alerting.** It is "Built on the Prometheus alerting model". It evaluates rules on a schedule. Each rule can produce multiple **alert instances** (one per series; e.g. `sum by(cpu)(rate(node_cpu_seconds_total{mode!="idle"}[1m]))` yields one instance per CPU). Notifications go to **contact points** directly or via **notification policies**. — [alerting fundamentals](https://github.com/grafana/grafana/blob/main/docs/sources/alerting/fundamentals/_index.md) [G]. 12.0 made Grafana-managed alerts and recording rules GA. 12.1 added importing rules from Prometheus YAML. 13.3 added **importing Alertmanager configuration into Grafana Alerting** and "manage Prometheus, Mimir and Loki alerting with a dedicated plugin". — [What's new v12.0](https://github.com/grafana/grafana/blob/main/docs/sources/whatsnew/whats-new-in-v12/whats-new-in-v12-0.md), [v12.1](https://github.com/grafana/grafana/blob/main/docs/sources/whatsnew/whats-new-in-v12/whats-new-in-v12-1.md), [v13.3](https://github.com/grafana/grafana/blob/main/docs/sources/whatsnew/whats-new-in-v13/whats-new-in-v13-3.md) [G]
2. **Loki and LogQL.** "Loki indexes the timestamp and labels, but not the rest of the log line." Queries take the form `{ log stream selector } | log pipeline`, e.g. `{service_name="nginx", status="500"}`, where `service_name` is a default label Loki tries to populate. LogQL "is based on PromQL". Metric queries: `rate({job="mysql"}[5m])`, `count_over_time(...)`, `bytes_rate(...)`, and `sum by (host) (rate({job="mysql"} |= "error" != "timeout" | json | duration > 10s [1m]))`. Unwrapped ranges (`| unwrap latency`) turn extracted values into samples. — [Loki query docs](https://github.com/grafana/loki/blob/main/docs/sources/query/_index.md) [G]; [metric queries](https://github.com/grafana/loki/blob/main/docs/sources/query/metric_queries.md) [G]. *Intuition:* Loki is "Prometheus for logs". Labels pick streams and grep does the rest, so the cardinality rules from Lesson 2 apply to log labels too.
3. **Loki quickstart.** A Docker Compose stack runs Loki (monolithic), Grafana, Alloy and the `flog` log generator. Alloy's UI is at `localhost:12345`. First queries look like `{container="evaluate-loki-flog-1"} |= "GET"`. There is also a browser sandbox on Killercoda. — [Loki quickstart](https://grafana.com/docs/loki/latest/get-started/quick-start/tutorial/) [S]; [quick-start (next)](https://grafana.com/docs/loki/next/get-started/quick-start/quick-start/) [S]
4. **Tempo** is "an open source, easy-to-use, and high-scale distributed tracing backend… requiring only object storage to operate". Traces Drilldown gives a "queryless" UI. Tempo 3.0 brought many breaking config changes (e.g. the OpenCensus receiver was removed). — [Tempo README](https://github.com/grafana/tempo) [G]; [Tempo CHANGELOG](https://github.com/grafana/tempo/blob/main/CHANGELOG.md) [G]; [Tempo docs](https://grafana.com/docs/tempo/latest/) [S]
5. **Pyroscope (profiles).** "Pyroscope 2.0 makes the new v2 architecture the default. Profiles are written directly to object storage." The Grafana Pyroscope data source shows flame graphs and does not support alerting. — [Pyroscope README](https://github.com/grafana/pyroscope) [G]; [Pyroscope data source](https://grafana.com/docs/grafana/latest/datasources/pyroscope/) [S]
6. **Grafana Alloy** is "an open source OpenTelemetry Collector distribution with built-in Prometheus pipelines and support for metrics, logs, traces, and profiles". It has programmable pipelines and "big tent" support for many backends. When running Alloy in Docker, OTLP receivers must bind to `0.0.0.0`, not the default localhost. — [Alloy README](https://github.com/grafana/alloy) [G]; [Introduction to Alloy](https://grafana.com/docs/alloy/latest/introduction/) [S]; [Alloy as Tempo collector](https://grafana.com/docs/tempo/latest/set-up-for-tracing/instrument-send/set-up-collector/grafana-alloy/) [S]; [OTel → LGTM with Alloy](https://grafana.com/docs/alloy/latest/collect/opentelemetry-to-lgtm-stack/) [S]
7. **LGTM in one container.** `grafana/otel-lgtm` bundles the OpenTelemetry Collector, Prometheus, Tempo, Loki, Pyroscope and Grafana. It is for "development, demo, and testing" only. Run it with `docker run -p 3000:3000 -p 4317:4317 -p 4318:4318 --rm -ti grafana/otel-lgtm` (OTLP gRPC on 4317, HTTP on 4318; Grafana admin/admin). macOS works with Docker or Podman via `./run-lgtm.sh` and also with Apple Container (memory defaults to 2G; OBI eBPF is unsupported there). — [docker-otel-lgtm](https://github.com/grafana/docker-otel-lgtm) [S][G]; [Grafana blog intro](https://grafana.com/blog/2024/03/13/an-opentelemetry-backend-in-a-docker-image-introducing-grafana-otel-lgtm) [S]
8. **Grafana Cloud free tier:** 10k active metric series, 50 GB logs, 50 GB traces, 14-day retention, 3 active users. Pro starts at $19/month plus usage. A 50 GB profiles figure appears in third-party pages but isn't confirmed on Grafana's own page. — [Grafana pricing](https://grafana.com/pricing/?pg=pricing) [S]; [Grafana Cloud pricing](https://grafana.com/products/cloud/pricing/) [S]; summarized by [Last9](https://last9.io/blog/grafana-cloud-pricing/) [S]. An older press article cites 3,000 series and is out of date.
9. **Dashboards as code.** Grafana's "As code and provisioning" docs list **Git Sync**, on-prem file provisioning, **Terraform**, **Ansible**, the **Grafana Operator** and the **Foundation SDK**. — [as-code index](https://github.com/grafana/grafana/blob/main/docs/sources/as-code/_index.md) [G]
   - The Foundation SDK provides "strongly typed code" builders in Go, TypeScript, Python, PHP and Java (`go get github.com/grafana/grafana-foundation-sdk/go@latest`, `npm install @grafana/grafana-foundation-sdk`). Starter repo: https://github.com/grafana/intro-to-foundation-sdk. — [Foundation SDK docs](https://grafana.com/docs/grafana/latest/as-code/foundation-sdk/) (canonical URL in the opened source [G]); [grafana-foundation-sdk](https://github.com/grafana/grafana-foundation-sdk) [G]
   - Grafonnet (Jsonnet) is now generated from the Foundation SDK's schemas and is labelled "**This library is experimental**". — [grafonnet README](https://github.com/grafana/grafonnet) [G]
   - Grizzly "has been marked for deprecation and will be superseded by grafanactl". grafanactl "is being deprecated… new, improved CLI tool gcx… This repository will be archived on June 1st, 2026". gcx is "generally available" and works with Grafana Cloud, Enterprise and OSS. — [grizzly](https://github.com/grafana/grizzly), [grafanactl](https://github.com/grafana/grafanactl), [gcx](https://github.com/grafana/gcx) READMEs [G]
   - Terraform provider `grafana/grafana`, latest v4.53.0. — [terraform-provider-grafana](https://github.com/grafana/terraform-provider-grafana) [G tags]
10. **What changed in Grafana 12 and 13.** Release dates are from the [Grafana CHANGELOG](https://github.com/grafana/grafana/blob/main/CHANGELOG.md) [G]; features from [whatsnew v12](https://github.com/grafana/grafana/tree/main/docs/sources/whatsnew/whats-new-in-v12) and [v13](https://github.com/grafana/grafana/tree/main/docs/sources/whatsnew/whats-new-in-v13) [G]:
    - **12.0 (2025-05-05):** GA for Grafana Drilldown (Metrics, Logs and Traces Drilldown, formerly Explore Metrics/Logs/Traces), Grafana-managed alerts and recording rules, and the Cloud migration assistant. Introduced Git Sync (experimental), the new dashboard schema (v2), dynamic dashboards, SQL expressions and a faster table panel. **Breaking:** Angular plugins removed, and `editors_can_admin` removed.
    - **12.1 (2025-07-23):** Grafana Advisor, import of Prometheus rule YAML, regression-analysis transformation. **12.2 (2025-09-23):** SQL expressions, new table GA, saved queries, new dashboard APIs on by default. **12.3 (2025-11-19):** compare time ranges in one panel, export dashboards as images, new logs panel. **12.4 (2026-02-24):** Git Sync public preview, dynamic dashboards, dashboard templates, suggested dashboards; `grafana-oss` image no longer updated.
    - **13.0 (2026-04-14, the GrafanaCON 2026 release):** **Git Sync GA**, **dynamic dashboards GA**, restore deleted dashboards GA, ad hoc filters renamed "filters", visualization suggestions GA, Grafana Assistant available on-prem, Grafana Advisor GA. **Breaking:** `grafana-cli` and `grafana-server` removed (use `grafana cli` and `grafana server`), unified storage for folders and dashboards, Image Renderer plugin support removed, HTTP compression on by default, legacy `/api` endpoints deprecated. — [upgrade-v13.0](https://github.com/grafana/grafana/blob/main/docs/sources/upgrade-guide/upgrade-v13/upgrade-v13.0/index.md) [G]
    - **13.1 (2026-06-23):** Git Sync UI import, variables on rows and tabs, revamped query editor preview. **13.2 (2026-08-18):** saved queries GA, revamped homepage, Git Sync for GitHub Enterprise and GitLab/Bitbucket webhooks. **13.3 (2026-10-27):** "our biggest visual refresh since Grafana 7", **Notebooks** for investigations, cross-dashboard variables ("define variables once"), panel subtitles, Alertmanager config import.

#### Example LogQL (from the Loki docs; not run here)
```logql
{service_name="hello"}                                   # stream selector
{service_name="hello"} |= "ERROR" != "healthcheck"        # line filters
{service_name="hello"} | json | status >= 500             # parse, then label filter
sum by (status) (rate({service_name="hello"} | json [5m]))   # metric query: lines/sec
count_over_time({job="mysql"}[5m] offset 5m)              # offset goes inside the range (docs mark the other form INVALID)
```
— [metric_queries.md](https://github.com/grafana/loki/blob/main/docs/sources/query/metric_queries.md) [G]

#### Misconceptions
- **"Loki is Elasticsearch."** It indexes only labels, so putting request IDs or user IDs in labels recreates the cardinality problem. Keep them in the line and filter with `|=` or `| json`. — [Loki query docs](https://github.com/grafana/loki/blob/main/docs/sources/query/_index.md) [G]
- **"otel-lgtm is a production stack."** It's for dev, demo and test only. — [docker-otel-lgtm](https://github.com/grafana/docker-otel-lgtm) [G]
- **"Use Grizzly / grafana-cli / grafana-oss images"** from older tutorials. All are deprecated, removed or frozen (see above).
- **"Alerting must be in Grafana or Prometheus, pick one."** Grafana Alerting can import Prometheus rules (12.1) and Alertmanager config (13.3), so teams can start in Prometheus and consolidate later. — [whatsnew v12.1](https://github.com/grafana/grafana/blob/main/docs/sources/whatsnew/whats-new-in-v12/whats-new-in-v12-1.md), [v13.3](https://github.com/grafana/grafana/blob/main/docs/sources/whatsnew/whats-new-in-v13/whats-new-in-v13-3.md) [G]

#### Hands-on exercise ideas
- Run the official Loki quickstart, then write 5 LogQL queries of increasing complexity, ending with a `sum by (...) (rate(...))` panel next to the Prometheus RED panels.
- Run `grafana/otel-lgtm`, point an OpenTelemetry-instrumented sample app at `localhost:4318`, and follow one slow request from metric to trace to log to profile.
- Recreate the Lesson 4 HelloHighErrorRatio rule as a Grafana-managed alert with a webhook contact point, and compare the experience.
- Generate the RED dashboard with the Foundation SDK (TypeScript or Go) or Terraform, and commit it. Optionally try Git Sync against a personal GitHub repo.
- Sign up for the Grafana Cloud free tier and remote-write the lab Prometheus to it. Watch the active-series count against the 10k limit.

#### Resources (curated)
- Loki quickstart (Docker Compose + Alloy): https://grafana.com/docs/loki/latest/get-started/quick-start/tutorial/ [S]
- Introduction to Grafana Alloy: https://grafana.com/docs/alloy/latest/introduction/ [S]
- docker-otel-lgtm (all-in-one): https://github.com/grafana/docker-otel-lgtm [S][G]
- Grafana Tempo docs: https://grafana.com/docs/tempo/latest/ [S]
- Grafana Cloud pricing: https://grafana.com/pricing/?pg=pricing [S]
- Video, "OpenTelemetry Looks Good To Me: Loki, Grafana, Tempo, Mimir": https://www.youtube.com/watch?v=0MPDPFt-t4I [S]
- Video, "Getting started with Pyroscope: Intro to continuous profiling": https://www.youtube.com/watch?v=XL2yTCPy2e0 [S]
- Video, GrafanaCON 2026 keynote livestream: https://www.youtube.com/watch?v=UazoZQHW0kI [S]; session playlist: https://www.youtube.com/playlist?list=PLDGkOdUX1UjoSfz1IRj5c0xetw8tl8iin [S]. Barcelona per search snippets.
- Extra: "Building scalable OSS observability with Mimir, Loki, Tempo, and Pyroscope": https://www.youtube.com/watch?v=YZ3B2aSmA9o [S]; Grafana channel: https://www.youtube.com/c/Grafana [S]

### Inferences
- For a 40-minute lesson, spend about 15 minutes on Loki/LogQL (closest to what was just learned), about 10 on the LGTM container tour (traces and profiles as "look, it's there"), about 10 on dashboards as code, and about 5 on Grafana Cloud. Tempo and Pyroscope internals are out of scope for beginners.
- The as-code landscape changed fast in 2025–26. Teach the principle (dashboards and alerts live in Git and deploy via CI) plus one tool: Terraform for infra-minded learners, or the Foundation SDK for developers. Mention Git Sync as the GUI-first path.

### Gaps
- The Loki CHANGELOG on `main` has a "3.8.0 (2026-06-08)" entry, but there is no `v3.8.0` git tag and no `grafana/loki:3.8.0` image (404). The latest tag and image are 3.7.9. The 3.8.0 entry may be a release-please artifact; treat 3.7.9 as current.
- Couldn't confirm the end-of-life dates for Grafana Agent and Promtail (both superseded by Alloy) from the sources read here. Check before stating dates.
- Grafana Cloud free-tier numbers come from search snippets of grafana.com/pricing and third-party summaries; the page itself couldn't be opened.
- A GrafanaCON 2026 talk "Pyroscope 2.0: Continuous Profiling Architecture Deep Dive" is linked in the Pyroscope README (https://www.youtube.com/watch?v=vseSm-pzgmc). It did not appear in search results, so per the brief it is listed here only as a lead to verify.

## Key question: What intuitions help?

### Takeaway
A few mental models carry most of the course: counters only go up, so you read their slope; labels make a family of series and every label value costs money; aggregate after rate; percentiles can't be averaged; alert on what users feel; dashboards and alerts are code.

### Cited Findings
- **"A counter only goes up, so look at its rate."** Counters "can only go up (and reset…)… Raw counters are rarely useful. Use the rate() function". `rate()` handles resets automatically. — [Understanding metric types](https://prometheus.io/docs/tutorials/understanding_metric_types/) [S]; [functions](https://prometheus.io/docs/prometheus/latest/querying/functions/) [S]. Lab evidence [R]: the raw counter read 491; its 1m rate read 5.42/s, which is the number a human cares about.
- **"Labels make a metric a family of time series."** "Every time series is uniquely identified by its metric name and… labels." The lab's single counter `hello_requests_total` became 2 series (`status="200"`, `status="500"`). — [data_model.md](https://github.com/prometheus/docs/blob/main/docs/concepts/data_model.md) [G]; [R]
- **"Cardinality is a cost."** Series count multiplies across label values (e.g. 3 statuses × 5 actions = 15 series). Keep most metrics label-free and under ~10 series, and investigate anything over 100. — [instrumentation.md](https://github.com/prometheus/docs/blob/main/docs/practices/instrumentation.md) [G]; [Cardinality is key](https://www.robustperception.io/cardinality-is-key/) [S]. Grafana Cloud's free tier is priced in *active series* (10k), which makes the cost concrete. — [Grafana pricing](https://grafana.com/pricing/?pg=pricing) [S]
- **"Rate, then sum."** Aggregating first hides counter resets. — [RP](https://www.robustperception.io/rate-then-sum-never-sum-then-rate/) [S]
- **"Histograms are counters per bucket; quantiles are estimates."** Buckets are cumulative counters, so you `rate` and `sum` them, keeping `le`. — [RP: histograms are cumulative](https://www.robustperception.io/why-are-prometheus-histograms-cumulative/) [S]; [Histograms and summaries](https://prometheus.io/docs/practices/histograms/) [S]
- **"Pull means 'up' is free."** A failed scrape gives `up == 0`, a built-in health signal. — [overview.md](https://github.com/prometheus/docs/blob/main/docs/introduction/overview.md) [G]; lab [R]
- **"RED = how happy users are; USE = how happy machines are."** — [Grafana best practices](https://github.com/grafana/grafana/blob/main/docs/sources/visualizations/dashboards/build-dashboards/best-practices/index.md) [G]
- **"Loki = Prometheus for logs."** LogQL is "based on PromQL", and only labels are indexed. — [Loki query docs](https://github.com/grafana/loki/blob/main/docs/sources/query/_index.md) [G]
- **"Error budget = permission to take risk."** 1 − SLO is the budget, and releases pause when it's spent. — [Embracing Risk](https://sre.google/sre-book/embracing-risk/) [S]

### Inferences
- Useful analogies for software engineers: a counter is an odometer and `rate()` is the speedometer. Labels are a composite primary key (each unique combination is a row in a very long table). A histogram is a set of odometers, one per speed band. The `for:` clause is a debounce.
- Make cardinality tangible by having students compute series counts before adding a label, e.g. `path` (10) × `status` (5) × `instance` (3) = 150, and then add `user_id`.

### Gaps
- No controlled study exists of which analogies work best for learners; these are teaching judgments.

## Key question: What do beginners get wrong?

### Takeaway
The classic errors are all well documented and most can be reproduced in the lab: rate windows that are too short, sum before rate, averaging percentiles, `irate` in alerts, high-cardinality labels, alerting on causes, missing `for:`, giant copy-pasted dashboards, plus 2026-specific traps from outdated tutorials (old images, removed CLIs, label selectors in kube-prometheus-stack).

### Cited Findings
- **Rate over too short a range:** use ≥4× the scrape interval. Lab: `rate(x[10s])` at a 15s scrape → empty [R]. — [RP](https://www.robustperception.io/what-range-should-i-use-with-rate/) [S]
- **Sum then rate:** breaks reset detection. — [functions.md](https://github.com/prometheus/prometheus/blob/main/docs/querying/functions.md) [G]
- **Averaging percentiles:** `avg(http_request_duration_seconds{quantile="0.95"})` is flagged "BAD"; aggregate histogram buckets instead. — [Histograms and summaries](https://prometheus.io/docs/practices/histograms/) [S]
- **Dropping `le` when summing buckets** before `histogram_quantile`. — [RP: How does a Prometheus Histogram work?](https://www.robustperception.io/how-does-a-prometheus-histogram-work/) [S]
- **High-cardinality labels** (user IDs, emails). — [naming.md](https://github.com/prometheus/docs/blob/main/docs/practices/naming.md) [G]; churn and cardinality debugging with `promtool tsdb analyze`: [RP](https://www.robustperception.io/using-tsdb-analyze-to-investigate-churn-and-cardinality/) [S]
- **`rate()` on a gauge:** "You should never take a rate() of a gauge." — [Understanding metric types](https://prometheus.io/docs/tutorials/understanding_metric_types/) [S]
- **Wrong units and names:** e.g. milliseconds or percentages instead of base units and ratios; type words in names. — [naming best practices](https://github.com/prometheus/docs/blob/main/docs/practices/naming.md) [G]
- **Alerting on causes, too many pages, no runbook or console link.** — [practices/alerting.md](https://github.com/prometheus/docs/blob/main/docs/practices/alerting.md) [G]
- **`irate` in alerts and no `for:`:** flapping. — [RP: Avoid irate() in alerts](https://www.robustperception.io/avoid-irate-in-alerts/) [S]
- **Pushgateway as a general push mechanism.** — [pushing.md](https://github.com/prometheus/docs/blob/main/docs/practices/pushing.md) [G]
- **Giant dashboards and sprawl, editing in the browser, no version control.** — [Grafana best practices](https://grafana.com/docs/grafana/latest/dashboards/build-dashboards/best-practices/) [S]
- **Provisioned dashboards not updating on Docker for Mac:** filesystem watch events may not cross bind mounts when `updateIntervalSeconds` ≤ 10. — [provisioning source](https://github.com/grafana/grafana/blob/main/docs/sources/administration/provisioning/index.md) [G]
- **ServiceMonitor not picked up:** missing `release` label. — [kube-prometheus-stack README](https://github.com/prometheus-community/helm-charts/tree/main/charts/kube-prometheus-stack) [G]
- **Outdated tutorial artifacts in 2026:** `grafana/grafana-oss` image (frozen after 12.4.0) [G Docker doc]; `grafana-cli`/`grafana-server` (removed in 13.0) [G upgrade guide]; Angular panels (removed in 12.0) [G whatsnew v12.0]; Grizzly and grafanactl (deprecated) [G]; Prometheus 2.x flags removed in 3.0, e.g. `--storage.tsdb.retention`, `--enable-feature=agent` → `--agent`, `--enable-feature=otlp-write-receiver` → `--web.enable-otlp-receiver`. — [Prometheus CHANGELOG 3.0.0](https://github.com/prometheus/prometheus/blob/main/CHANGELOG.md) [G]

### Inferences
- Two more traps came up in this session's lab and are worth calling out. (1) Long-window rates read low right after start or deploy (the observed 1.69 vs 5.64). (2) `histogram_quantile` can report a p95 above the true maximum when buckets are coarse (observed 0.211s vs max ~0.12s). Both look like bugs to beginners.
- On Apple Silicon, "node_exporter shows the wrong machine" will confuse people unless you explain that Docker Desktop's VM is the host.

### Gaps
- Didn't find a primary source that quantifies how common each mistake is. The list is drawn from maintainers' guidance and their blogs.

## Key question: Which free local labs work on a Mac (Docker Compose or kind), with exact current image names and versions?

### Takeaway
Everything needed is free, open source and published for **arm64**. Recommended labs: (A) a Compose stack with Prometheus 3.15.1 + node_exporter 1.12.1 + Alertmanager 0.34.2 + Grafana 13.3.0 + a Flask app exposing `hello_requests_total` + a local webhook receiver. I validated and ran the configs (natively, same versions) and ran Grafana 13.3.0 in Docker with provisioning. (B) The official Loki quickstart Compose. (C) The `grafana/otel-lgtm:0.38.1` single container. (D) kind v0.33.0 + kube-prometheus-stack 92.16.0 (not run here).

### Cited Findings

#### Exact images (Docker Hub API, 30 Oct 2026; all list `arm64`) [H]
```
prom/prometheus:v3.15.1          (pushed 2026-10-21)   # likely-LTS alternative (inferred from patch activity): v3.13.5; 3.5.x last patched as 3.5.5
prom/alertmanager:v0.34.2        (2026-10-29)
prom/node-exporter:v1.12.1       (2026-07-14)
prom/blackbox-exporter:v0.29.1   (2026-10-21)
prom/pushgateway:v1.11.5         (2026-10-21)
grafana/grafana:13.3.0           (2026-10-27)          # or grafana/grafana-enterprise:13.3.0 (free); NOT grafana/grafana-oss
grafana/loki:3.7.9               (2026-10-20)
grafana/alloy:v1.21.3            (2026-10-28)
grafana/tempo:3.1.1              (2026-10-21)
grafana/pyroscope:2.4.2          (2026-10-26)
grafana/mimir:3.2.3              (2026-10-22)
grafana/otel-lgtm:0.38.1         (2026-10-26)
thanosio/thanos:v0.42.5          (2026-10-27)
python:3.13-slim                 (2026-10-28)
kindest/node:v1.37.0             (2026-08-26)          # kind CLI latest tag v0.33.0 [G]
```
Helm chart: `oci://ghcr.io/prometheus-community/charts/kube-prometheus-stack`, version 92.16.0 (operator v0.94.2). — [chart README and Chart.yaml](https://github.com/prometheus-community/helm-charts/tree/main/charts/kube-prometheus-stack) [G]

#### Lab A – Compose stack (files tested as described)
Layout: `compose.yaml`, `app/{app.py,webhook.py,requirements.txt,Dockerfile}`, `prometheus/{prometheus.yml,rules.yml}` (Lesson 2/3/4 sections), `alertmanager/alertmanager.yml` (Lesson 4), `grafana/provisioning/{datasources,dashboards}/…` and `grafana/dashboards/hello-red.json` (Lesson 5). `docker compose config -q` passed [R].
```yaml
# compose.yaml
services:
  app:
    build: ./app
    ports: ["8000:8000"]
  webhook:
    build: ./app
    command: ["python", "webhook.py"]
    ports: ["5001:5001"]
  prometheus:
    image: prom/prometheus:v3.15.1
    volumes:
      - ./prometheus:/etc/prometheus:ro
    command:
      - --config.file=/etc/prometheus/prometheus.yml
      - --web.enable-lifecycle          # allows POST /-/reload
    ports: ["9090:9090"]
  alertmanager:
    image: prom/alertmanager:v0.34.2
    volumes:
      - ./alertmanager:/etc/alertmanager:ro
    command: ["--config.file=/etc/alertmanager/alertmanager.yml"]
    ports: ["9093:9093"]
  node-exporter:
    image: prom/node-exporter:v1.12.1   # on a Mac this reports the Docker Desktop VM
    ports: ["9100:9100"]
  grafana:
    image: grafana/grafana:13.3.0
    ports: ["3000:3000"]
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    volumes:
      - ./grafana/provisioning:/etc/grafana/provisioning:ro
      - ./grafana/dashboards:/var/lib/grafana/dashboards:ro
```
```python
# app/app.py  (pattern from the client_python Flask doc: DispatcherMiddleware + make_wsgi_app)
import random, time
from flask import Flask
from werkzeug.middleware.dispatcher import DispatcherMiddleware
from prometheus_client import Counter, Histogram, make_wsgi_app

app = Flask(__name__)

# Exposed as hello_requests_total (the client adds _total to counters)
REQUESTS = Counter("hello_requests", "Hello requests served", ["path", "status"])
LATENCY = Histogram("hello_request_duration_seconds", "Hello request latency", ["path"],
                    buckets=(0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0))

@app.route("/")
def hello():
    start = time.perf_counter()
    time.sleep(random.uniform(0.005, 0.12))              # fake work
    status = "500" if random.random() < 0.05 else "200"  # ~5% errors
    REQUESTS.labels(path="/", status=status).inc()
    LATENCY.labels(path="/").observe(time.perf_counter() - start)
    return ("oops\n", 500) if status == "500" else "hello\n"

app.wsgi_app = DispatcherMiddleware(app.wsgi_app, {"/metrics": make_wsgi_app()})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
```
```python
# app/webhook.py  – minimal Alertmanager webhook receiver
from flask import Flask, request
app = Flask(__name__)

@app.route("/alert", methods=["POST"])
def alert():
    body = request.get_json(force=True)
    for a in body.get("alerts", []):
        print(f"WEBHOOK status={a['status']} alertname={a['labels'].get('alertname')} "
              f"labels={a['labels']} summary={a['annotations'].get('summary')}", flush=True)
    return "ok\n"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
```
```dockerfile
# app/Dockerfile                      # app/requirements.txt: flask==3.1.3, prometheus_client==0.26.0
FROM python:3.13-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app.py webhook.py ./
CMD ["python", "app.py"]
```
Drive traffic with `while true; do curl -s localhost:8000/ >/dev/null; sleep 0.1; done`. Then open Prometheus at :9090, Alertmanager at :9093, Grafana at :3000 (admin/admin), and run `docker compose logs -f webhook` to watch alerts arrive. Expected outputs are in Lessons 2–5 above [R].
- Sources for the patterns: [client_python Flask doc](https://github.com/prometheus/client_python/blob/master/docs/content/exporting/http/flask.md) [G]; [alerting tutorial with webhook receiver](https://prometheus.io/docs/tutorials/alerting_based_on_metrics/) [S]; [Grafana Docker compose doc](https://github.com/grafana/grafana/blob/main/docs/sources/setup-grafana/installation/docker/index.md) [G]; [node_exporter README](https://github.com/prometheus/node_exporter) [G].

#### Lab B – Logs: the official Loki quickstart (Compose with Loki, Grafana, Alloy and flog). Also available as a Killercoda browser sandbox. — https://grafana.com/docs/loki/latest/get-started/quick-start/tutorial/ [S]

#### Lab C – All signals in one container: `docker run -p 3000:3000 -p 4317:4317 -p 4318:4318 --rm -ti grafana/otel-lgtm:0.38.1`. Use admin/admin at :3000 and send OTLP to :4317/:4318. OBI auto-instrumentation needs Linux kernel features and isn't supported on Apple Container. — https://github.com/grafana/docker-otel-lgtm [S][G]

#### Lab D – kind + kube-prometheus-stack (assembled, not run)
```bash
kind create cluster --name obs                     # kind v0.33.0
helm install kps oci://ghcr.io/prometheus-community/charts/kube-prometheus-stack \
  --version 92.16.0 -n monitoring --create-namespace
kubectl -n monitoring port-forward svc/kps-grafana 3000:80
kubectl -n monitoring port-forward svc/kps-kube-prometheus-stack-prometheus 9090:9090
# then: build the hello image, `kind load docker-image hello:dev --name obs`, deploy + Service + ServiceMonitor (label release: kps)
```
The install command form is from the [chart README](https://github.com/prometheus-community/helm-charts/tree/main/charts/kube-prometheus-stack) [G]. The service names (`kps-grafana`, `kps-kube-prometheus-stack-prometheus`) are my guess at the chart's naming and **not verified**; students should run `kubectl -n monitoring get svc`.

#### Free hosted option
Grafana Cloud free tier (10k series, 50 GB logs, 50 GB traces, 14-day retention, 3 users) as a remote-write target for Lab A. — [Grafana pricing](https://grafana.com/pricing/?pg=pricing) [S]

### Inferences
- Lab A runs comfortably on any Apple Silicon Mac, since every image has an arm64 manifest. The webhook receiver must be a separate service so that "app down" alerts can still be delivered.
- If students want real Mac host metrics, add a native `node_exporter-1.12.1.darwin-arm64` (release asset verified) and a scrape target such as `host.docker.internal:9100`. That hostname is Docker Desktop behavior I didn't verify here.
- For classes on low-memory laptops, prefer Lab A and Lab C over kind + kube-prometheus-stack, which deploys many components (operator, Prometheus, Alertmanager, Grafana, kube-state-metrics, node-exporter DaemonSet).

### Gaps
- **Not tested on an actual Mac.** Lab A configs were run natively on x86_64 Linux with the same component versions, and Grafana 13.3.0 ran in Docker there. A full `docker compose up` was blocked: Docker Hub returned HTTP 429 on most pulls, and pip inside `docker build` had no network in this sandbox.
- Lab D (kind) was not executed. Chart service names and the memory needed on Docker Desktop are unverified.
- I didn't verify the latest Helm CLI version or kind's default node image for v0.33.0.
