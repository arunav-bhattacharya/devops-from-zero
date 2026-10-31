from common import lab, ref, src

DIAGRAM = (
    '<svg viewBox="0 0 560 284" xmlns="http://www.w3.org/2000/svg" role="img" '
    'aria-label="How a p95 latency query is built: select the bucket series, take a 5 minute range, apply rate, '
    'sum by le, then histogram_quantile">'
    '<rect class="bx" x="24" y="12" width="210" height="36" rx="10"/>'
    '<text class="t" x="129" y="35" font-size="13" text-anchor="middle">Selector</text>'
    '<text class="ts" x="250" y="35" font-size="11" text-anchor="start">hello_request_duration_seconds_bucket</text>'
    '<line class="ln" x1="129" y1="49" x2="129" y2="64" marker-end="url(#ar)"/>'
    '<rect class="bxt" x="24" y="68" width="210" height="36" rx="10"/>'
    '<text class="tk" x="129" y="91" font-size="13" text-anchor="middle">Range [5m]</text>'
    '<text class="ts" x="250" y="91" font-size="11" text-anchor="start">20 samples per series at 15s</text>'
    '<line class="ln" x1="129" y1="105" x2="129" y2="120" marker-end="url(#ar)"/>'
    '<rect class="bxt" x="24" y="124" width="210" height="36" rx="10"/>'
    '<text class="tk" x="129" y="147" font-size="13" text-anchor="middle">rate()</text>'
    '<text class="ts" x="250" y="147" font-size="11" text-anchor="start">per-second growth of each bucket</text>'
    '<line class="ln" x1="129" y1="161" x2="129" y2="176" marker-end="url(#ar)"/>'
    '<rect class="bxo" x="24" y="180" width="210" height="36" rx="10"/>'
    '<text class="tk" x="129" y="203" font-size="13" text-anchor="middle">sum by (le)</text>'
    '<text class="ts" x="250" y="203" font-size="11" text-anchor="start">add up paths and instances, keep le</text>'
    '<line class="ln" x1="129" y1="217" x2="129" y2="232" marker-end="url(#ar)"/>'
    '<rect class="bxp" x="24" y="236" width="210" height="36" rx="10"/>'
    '<text class="tk" x="129" y="259" font-size="13" text-anchor="middle">histogram_quantile</text>'
    '<text class="ts" x="250" y="259" font-size="11" text-anchor="start">0.95: p95 = 0.0095 s in my healthy run</text>'
    "</svg>"
)

LESSON = {
    "id": "d43",
    "title": "PromQL from zero",
    "minutes": 50,
    "goal": "By the end you can write PromQL from a bare metric name up to the three RED queries for hello-devops, say why a query returns nothing, and save the queries you use most as recording rules.",
    "guess": {
        "q": "Prometheus scrapes every 15 seconds. What does rate(hello_responses_total[10s]) return?",
        "options": [
            "Requests per second over the last 10 seconds",
            "Zero for every series",
            "An error about the range being too short",
            "Nothing at all: an empty result",
        ],
        "answer": 3,
        "why": "rate() needs at least two samples inside the range. A 10-second window usually holds only one sample at a 15-second scrape, so the series drops out of the result without any error.",
    },
    "terms": [
        {"term": "PromQL", "plain": "Prometheus's query language: you select series by name and labels, then do maths on them."},
        {"term": "Instant vector", "plain": "A set of series with one value each, all for the same moment."},
        {"term": "Range vector", "plain": "A set of series with all their samples over a time window, such as the last 5 minutes."},
        {"term": "Label matcher", "plain": "A filter on a label inside braces: = and != for exact values, =~ and !~ for regular expressions."},
        {"term": "rate()", "plain": "The average per-second growth of a counter over a range, with restarts handled."},
        {"term": "Aggregation", "plain": "Combining many series into fewer with sum, avg, max, count or topk, grouped by labels."},
        {"term": "histogram_quantile()", "plain": "Estimates a percentile, such as p95, from the rates of histogram buckets."},
        {"term": "Recording rule", "plain": "A query Prometheus runs on a schedule and stores as a new, cheap-to-read series."},
    ],
    "sections": [
        {
            "h": "Where to type PromQL, and what comes back",
            "body": (
                "PromQL is the language you use to ask Prometheus questions. You can type it in two places. "
                "The web UI at `localhost:9090` has a Query page with three tabs:\n"
                "- Table shows the current value of each series.\n"
                "- Graph draws the series over time.\n"
                "- Explain breaks a query into its parts.\n\n"
                "In the terminal, the `q` function from Day 42 runs the same query through `promtool`.\n\n"
                "The simplest query is a metric name. `hello_responses_total` returned three series in my run, one per label set:\n"
                "- `{path=\"/\", status=\"200\"} 303`\n"
                "- `{path=\"/healthz\", status=\"200\"} 3`\n"
                "- `{path=\"unmatched\", status=\"404\"} 1`\n\n"
                "(I left out the `job` and `instance` labels to keep the lines short.) "
                "That result is an instant vector: one value per series, all for the same moment. "
                "Prometheus takes the newest sample that is at most 5 minutes old. A series nobody has scraped for 5 minutes drops out.\n\n"
                "Add a duration in square brackets and you get a range vector: every sample in that window. "
                "`hello_responses_total{path=\"/\"}[1m]` returned four samples, 99, 167, 235 and 303, 15 seconds apart. "
                "The Graph tab cannot draw a range vector. Functions such as `rate()` take it as input and turn it back into one value per series."
            ),
            "refs": [ref("basics"), ref("v_promql")],
        },
        {
            "h": "Choosing series with label matchers",
            "body": (
                "Braces after the name filter by label. There are four matchers:\n"
                "- `=` exact: `{path=\"/\"}` keeps only the root route.\n"
                "- `!=` not equal: `{path!=\"/\"}` returned `/healthz` and `unmatched`.\n"
                "- `=~` regex: `{status=~\"5..\"}` means any 5xx status.\n"
                "- `!~` regex, negated: `{path!~\"/|/healthz\"}` keeps every other route.\n\n"
                "Regexes match the whole value, as if they started with `^` and ended with `$`. "
                "So `{path=~\"/health\"}` returned nothing, while `{path=~\"/health.*\"}` found `/healthz`. "
                "In the shell, wrap the whole query in single quotes so the double quotes inside survive.\n\n"
                "An empty result is not zero. It means no series matched, and this trips most people up. "
                "Before the app had ever failed, `hello_responses_total{status=~\"5..\"}` returned nothing, because no series with a 5xx label existed yet. "
                "Any maths with an empty side is empty too, so an error ratio showed nothing instead of 0. "
                "Adding `or vector(0)` to the error part gives a real zero."
            ),
            "refs": [ref("basics"), ref("operators")],
        },
        {
            "h": "Counters need rate()",
            "body": (
                "A raw counter only tells you how many requests the process served since it started. "
                "It also falls back to zero on every restart: when I recreated the `web` container, the counter went from 2370 to 11.\n\n"
                "`rate(hello_responses_total{path=\"/\"}[1m])` gives the average increase per second over the last minute: 4.56 in my run, from a loop sending about 4.5 requests a second. "
                "It treats a drop as a restart and adds the new count on top. After that restart, `resets()` counted 1 reset and `rate()` still read 3.3 per second.\n\n"
                "Choose the range carefully:\n"
                "- Use at least 4 times the scrape interval. With a 15-second scrape, `[10s]` returned nothing and `[1m]` worked.\n"
                "- Longer ranges are smoother but slower to react. Dashboards often use `[5m]`.\n"
                "- Right after a start, long ranges read low. At two minutes old, `[5m]` gave 1.55 while `[1m]` gave 4.44. Five minutes later they agreed: 4.49 and 4.56.\n\n"
                "Two relatives:\n"
                "- `increase(x[1m])` is the rate times 60: \"how many in the last minute\". It returned 266.67, not a whole number, because it estimates to the edges of the window. Once it even said 1216.6 for a counter that read 1175.\n"
                "- `irate(x[1m])` uses only the last two samples. It is jumpy, fine for a zoomed-in graph and wrong for alerts."
            ),
            "refs": [ref("functions"), ref("rp_rate_range"), ref("promlabs_rates")],
        },
        {
            "h": "Aggregation: sum, by and without",
            "body": (
                "`rate()` returns one result per series. Usually you want fewer lines. "
                "`sum(rate(hello_responses_total[5m]))` added everything into one number: 3.53 requests a second.\n\n"
                "Add `by` to keep some labels, or `without` to drop some:\n"
                "- `sum by (path) (rate(hello_responses_total[5m]))` gave `/` 3.51, `/healthz` 0.028 and `unmatched` 0.\n"
                "- `sum without (instance, status) (...)` drops only those two labels and keeps `job` and `path`.\n\n"
                "The `/healthz` line is the Docker health check from Day 16: one request every 30 seconds is about 0.03 a second. "
                "Aggregation shows you traffic you did not know about.\n\n"
                "Other aggregations work the same way:\n"
                "- `avg`, `min` and `max`, such as `max by (job) (process_resident_memory_bytes)`.\n"
                "- `count`, such as `count by (job) (up)` for the number of targets per job.\n"
                "- `topk(2, ...)` and `bottomk`, for the largest or smallest few series.\n\n"
                "Always take the rate first, then sum. Each instance's counter restarts on its own, and only `rate()` can see that, one series at a time. "
                "Robust Perception's post [Rate then sum](https://www.robustperception.io/rate-then-sum-never-sum-then-rate/) shows what goes wrong otherwise."
            ),
            "refs": [ref("operators"), ref("rp_rate_then_sum")],
        },
        {
            "h": "Maths between series: ratios, filters and matching",
            "body": (
                "You can divide one query by another. The error ratio is failed responses per second divided by all responses per second: "
                "`sum(rate(hello_responses_total{status=~\"5..\"}[5m])) / sum(rate(hello_responses_total[5m]))`.\n\n"
                "Between two vectors, Prometheus pairs series whose labels are exactly the same. "
                "For a per-path error ratio I wrote `sum by (path, status) (...)` on the left and `sum by (path) (...)` on the right. "
                "The result was empty, because the left side has a `status` label the right side lacks. "
                "Adding `/ ignoring(status)` between them, or `/ on(path)`, gave `/` 0.054 and `/readyz` NaN. "
                "NaN is 0 divided by 0: nobody called `/readyz` in that window.\n\n"
                "Comparison operators filter:\n"
                "- `job:hello_responses_errors:ratio_rate5m > 0.02` keeps series above 2% and drops the rest. Alert rules use this form.\n"
                "- `... > bool 0.02` returns 1 or 0 for every series instead.\n\n"
                "Three more tools:\n"
                "- `offset` looks back in time. `hello_responses_total{path=\"/\"} offset 5m` read 30 while the live value was 1380.\n"
                "- `up == 0` lists every target whose last scrape failed.\n"
                "- `absent(up{job=\"payments\"})` returns 1 when no such series exists at all. It catches a job that vanished, which `up == 0` cannot."
            ),
            "refs": [ref("operators"), ref("examples")],
        },
        {
            "h": "Latency from histograms",
            "body": (
                "Each histogram bucket is a counter, so you treat it like one. "
                "Take the rate of every bucket, add them up while keeping `le`, then let `histogram_quantile()` estimate the percentile:\n"
                "`histogram_quantile(0.95, sum by (le) (rate(hello_request_duration_seconds_bucket{path=\"/\"}[5m])))`\n\n"
                "In my healthy run that gave a p95 of 0.018 seconds, a p50 of 0.0036 and a p99 of 0.045. "
                "The average comes from the other two series: `rate(..._sum[5m]) / rate(..._count[5m])` gave 0.0060. "
                "Drop `le` from the `by` clause and the result is empty, because the function needs the bucket limits.\n\n"
                "The answer is an estimate. The function finds the bucket that holds the 95th percentile and assumes requests are spread evenly inside it. "
                "Two real examples:\n"
                "- Prometheus's own query API answered in a few milliseconds, but its first bucket is 0 to 0.1 seconds. The p95 came out at exactly 0.095.\n"
                "- During a Redis outage, hello-devops's p95 read 6.12 seconds: somewhere in the 5 to 7.5 second bucket.\n\n"
                "If most requests are slower than the largest finite bucket, the function can only return that bucket's limit, 10 seconds for the default buckets. "
                "So choose bucket limits around the latencies you care about. "
                "And never average percentiles from several servers. Sum the buckets, then compute the percentile once, as the [histograms guide](https://prometheus.io/docs/practices/histograms/) explains."
            ),
            "refs": [ref("histograms"), ref("rp_hist"), ref("v_hist")],
        },
        {
            "h": "RED for hello-devops, saved as recording rules",
            "body": (
                "Put the pieces together and you have RED for hello-devops, per job:\n"
                "- Rate: `sum by (job) (rate(hello_responses_total[5m]))`\n"
                "- Errors: `sum by (job) (rate(hello_responses_total{status=~\"5..\"}[5m])) / sum by (job) (rate(hello_responses_total[5m]))`\n"
                "- Duration: `histogram_quantile(0.95, sum by (job, le) (rate(hello_request_duration_seconds_bucket[5m])))`\n\n"
                "Dashboards and alerts will run these every few seconds, forever. A recording rule runs a query on Prometheus's schedule (every 15 seconds in the lab) and stores the answer as a new series. "
                "Reading that series is cheap, and every dashboard and alert gets the same number.\n\n"
                "The lab keeps them in `observability/prometheus/rules/recording.yml`. "
                "The names follow the [naming convention](https://prometheus.io/docs/practices/rules/) `level:metric:operations`, for example `job:hello_responses:rate5m`: grouped by job, from `hello_responses`, a 5-minute rate. "
                "`prometheus.yml` loads every file in `rules/`. "
                "After an edit, check the file with `promtool`, reload Prometheus, and query the new name. "
                "Status, Rule health in the UI shows each rule and its last error."
            ),
            "refs": [ref("recording_rules"), ref("rules_practice"), ref("v_guesswork")],
        },
    ],
    "analogy": (
        "Picture a huge spreadsheet: one column per series, one row per scrape. "
        "A selector picks columns, and a range like [5m] picks the last rows. "
        "Then rate() is the slope of each column, and sum by (path) is a pivot table that adds columns together. "
        "Where it breaks: real rows do not line up perfectly, because each target is scraped at a slightly different moment, so Prometheus estimates values at the edges of every window."
    ),
    "diagram": DIAGRAM,
    "diagram_caption": "A p95 query, inside out: select, take a range, rate, sum by le, then estimate the quantile.",
    "worked": {
        "title": "RED for hello-devops, before and during an outage",
        "steps": [
            {
                "say": (
                    "Start with Rate, split by status. The loop from Day 42 sends about 4.5 requests a second, and all of them succeed. "
                    "I run every query with the `q` function from Day 42."
                ),
                "code": "$ q 'sum by (status) (rate(hello_responses_total{path=\"/\"}[1m]))'\n{status=\"200\"} => 4.5777777777777775 @[1793337924.539]",
                "lang": "console",
            },
            {
                "say": (
                    "Errors. The recording rule returns nothing, because no 5xx series exists yet. "
                    "With `or vector(0)` on the error side, the same ratio returns a real 0."
                ),
                "code": "$ q 'job:hello_responses_errors:ratio_rate5m'\n$ q '(sum(rate(hello_responses_total{status=~\"5..\"}[5m])) or vector(0)) / sum(rate(hello_responses_total[5m]))'\n{} => 0 @[1793337924.939]",
                "lang": "console",
            },
            {
                "say": "Duration. 95% of requests to `/` finished within about 9.5 ms.",
                "code": "$ q 'histogram_quantile(0.95, sum by (le) (rate(hello_request_duration_seconds_bucket{path=\"/\"}[5m])))'\n{} => 0.00947887323943662 @[1793337925.15]",
                "lang": "console",
            },
            {
                "say": (
                    "Now break the app's dependency and wait about 90 seconds. "
                    "Every request to `/` now fails, and the rate falls from 4.5 to 0.24 a second. "
                    "Each failure takes about 4 seconds, and the loop waits for each one before it sends the next."
                ),
                "code": "$ docker compose stop redis\n$ q 'sum by (status) (rate(hello_responses_total{path=\"/\"}[1m]))'\n{status=\"200\"} => 0 @[1793338015.637]\n{status=\"500\"} => 0.2444444444444444 @[1793338015.637]",
                "lang": "console",
            },
            {
                "say": (
                    "The error ratio over 5 minutes is only 2.4%, although every request fails right now. "
                    "The window still holds the healthy minutes, and the failing minutes carry far fewer requests. The 1-hour ratio is the same because the lab is younger than an hour."
                ),
                "code": "$ q 'job:hello_responses_errors:ratio_rate5m'\njob:hello_responses_errors:ratio_rate5m{job=\"hello-devops\"} => 0.023764204114522652 @[1793338015.243]\n$ q 'job:hello_responses_errors:ratio_rate1h'\njob:hello_responses_errors:ratio_rate1h{job=\"hello-devops\"} => 0.023764204114522652 @[1793338015.436]",
                "lang": "console",
            },
            {
                "say": (
                    "Duration over the last minute jumped from milliseconds to 6.1 seconds. "
                    "That is an estimate inside the 5 to 7.5 second bucket, because the Redis client keeps retrying before it gives up."
                ),
                "code": "$ q 'histogram_quantile(0.95, sum by (le) (rate(hello_request_duration_seconds_bucket{path=\"/\"}[1m])))'\n{} => 6.124999999999999 @[1793338015.836]",
                "lang": "console",
            },
            {
                "say": "Bring Redis back. Day 44 uses this same outage to fire real alerts.",
                "code": "$ docker compose start redis",
                "lang": "console",
            },
        ],
    },
    "code": [
        {
            "lang": "yaml",
            "title": "observability/prometheus/rules/recording.yml",
            "src": lab("observability/prometheus/rules/recording.yml"),
            "run": "docker compose exec prometheus promtool check rules /etc/prometheus/rules/recording.yml && curl -X POST localhost:9090/-/reload",
        }
    ],
    "commands": [
        {"cmd": "q() { docker compose exec prometheus promtool query instant http://localhost:9090 \"$1\"; }", "what": "Define q: run one PromQL query from the observability folder."},
        {"cmd": "q 'hello_responses_total{status=~\"5..\"}'", "what": "Select series with a regex matcher: every 5xx status."},
        {"cmd": "q 'rate(hello_responses_total{path=\"/\"}[1m])'", "what": "Requests per second to / over the last minute."},
        {"cmd": "q 'sum by (path) (rate(hello_responses_total[5m]))'", "what": "Rate first, then add up per path."},
        {"cmd": "q 'topk(3, count by (__name__) ({__name__=~\".+\"}))'", "what": "The three metric names with the most series."},
        {"cmd": "q 'histogram_quantile(0.95, sum by (le) (rate(hello_request_duration_seconds_bucket[5m])))'", "what": "The 95th percentile request time across all routes."},
        {"cmd": "q 'absent(up{job=\"hello-devops\"})'", "what": "Returns 1 only if the hello-devops job has vanished completely."},
        {"cmd": "curl -s localhost:9090/api/v1/query --data-urlencode 'query=up' | jq -c '.data.result[] | {job: .metric.job, value: .value[1]}'", "what": "Run a query through the HTTP API and keep only the job and value with jq."},
        {"cmd": "docker compose exec prometheus promtool check rules /etc/prometheus/rules/recording.yml", "what": "Check a rule file for mistakes before loading it."},
        {"cmd": "curl -X POST localhost:9090/-/reload", "what": "Load the new rules without restarting Prometheus."},
        {"cmd": "open http://localhost:9090/rules", "what": "Status, Rule health: every rule, when it last ran and any error."},
        {"cmd": "docker compose stop redis", "what": "Cause a real outage so the error and latency queries have something to show."},
        {"cmd": "docker compose start redis", "what": "End the outage."},
    ],
    "mistake": (
        "Using a range that is too short for rate(), such as [10s] or [15s] with a 15-second scrape. "
        "The query does not fail; series just disappear from the result now and then, and a graph shows gaps or nothing at all. "
        "Use at least 4 times the scrape interval, and in Grafana use its $__rate_interval variable (Day 45)."
    ),
    "real_world": (
        "At PayFlow, a made-up payments company, every service gets the same three RED recording rules from a shared template, so dashboards and alerts read cheap precomputed series. "
        "In incident reviews, the first question about a strange graph is often: was that a real change, or an empty result, a NaN or a too-short range?"
    ),
    "task": {
        "title": "RED for Prometheus itself, plus USE for the node",
        "steps": [
            "With the lab running, open Explore metrics from the Query page menu and find `prometheus_http_requests_total` and `prometheus_http_request_duration_seconds_bucket`. Note their labels.",
            "Rate: write a query for requests per second per `handler`, showing only handlers with traffic.",
            "Make some errors on purpose: run `curl 'localhost:9090/api/v1/query?query=rate(up'` a few times every minute for two minutes. Each call returns HTTP 400.",
            "Errors: write the share of 4xx and 5xx responses per handler.",
            "Duration: write the p95 for `handler=\"/api/v1/query\"`, then explain the number by looking at that handler's `_bucket` series in the Table tab.",
            "USE for the node: write CPU busy as a percentage, memory in use as a share, and compare `node_load1` with the number of CPUs.",
            "Save one of your queries as a recording rule in a new group in `recording.yml`, check the file with promtool, reload, and query it by its new name.",
        ],
        "hints": [
            "A new series starts at its first scraped value, so rate() never sees the jump from nothing to your first few 400s. Keep sending bad queries for a minute or two.",
            "CPU busy is 1 minus the idle rate: `100 * (1 - avg by (instance) (rate(node_cpu_seconds_total{mode=\"idle\"}[1m])))`.",
            "If your p95 is a round number, look at which bucket holds 95% of the requests.",
        ],
        "done_when": "You have three working queries for Prometheus's own API (rate per handler, share of errors, p95), you can explain why the p95 is a round number, and one query answers under its recording-rule name.",
    },
    "explain_back": {
        "prompt": "Explain in 3 to 4 sentences how the p95 latency query for hello-devops works, from the inside out. Mention buckets, rate(), the le label and why the answer is an estimate.",
        "answer": (
            "The histogram stores a counter per bucket, such as how many requests took 0.1 seconds or less. "
            "First rate() turns each bucket counter into a per-second rate over the window. "
            "Then sum by (le) adds those rates across routes and instances while keeping the bucket limits. "
            "histogram_quantile(0.95, ...) finds the bucket where 95% of requests are reached and interpolates inside it. "
            "Because it only knows bucket counts, the result can be off by up to a bucket's width, so bucket limits should sit near the latencies you care about."
        ),
    },
    "recap": [
        "A bare selector returns an instant vector; adding [5m] returns a range vector that functions such as rate() consume.",
        "Matchers are =, !=, =~ and !~; regexes match the whole value, and an empty result means no series matched, not zero.",
        "Use rate() on counters with a range of at least 4 scrape intervals; increase() is an estimate and irate() is for zoomed-in graphs only.",
        "Take the rate first, then aggregate with sum, avg, max, count or topk, using by or without.",
        "Binary operators pair series with identical labels; use ignoring() or on() when one side has extra labels.",
        "p95 = histogram_quantile(0.95, sum by (le) (rate(..._bucket[5m]))), an estimate whose accuracy depends on the buckets; save common queries as recording rules.",
    ],
    "check": [
        {
            "q": "You want the share of requests per instance that failed. Your query `sum by (instance, status) (rate(errors[5m])) / sum by (instance) (rate(requests[5m]))` returns nothing. What fixes it?",
            "options": [
                "Change the range from [5m] to [1h]",
                "Add `ignoring(status)` after the division sign",
                "Replace rate() with irate()",
                "Put the left side in absent()",
            ],
            "answer": 1,
            "why": "The left side has a status label that the right side lacks, so no pairs match until you tell Prometheus to ignore it.",
        },
        {
            "q": "A service scraped every 30 seconds shows gaps in a graph of `rate(http_requests_total[45s])`. What is the most likely cause?",
            "options": [
                "The counter was reset at startup",
                "The service has too many labels",
                "The range holds too few samples",
                "rate() cannot draw a graph line",
            ],
            "answer": 2,
            "why": "At a 30-second scrape, a 45-second window often holds one sample, so the series drops out. Use at least 2m.",
        },
        {
            "q": "Three instances each report their own p99 latency through a summary: 0.2 s, 0.3 s and 2.0 s. What is the p99 across all three?",
            "options": [
                "You cannot tell from these numbers",
                "0.83 s, the average of the three",
                "2.0 s, the largest of the three",
                "0.3 s, the middle value of the three",
            ],
            "answer": 0,
            "why": "Percentiles cannot be averaged or combined; you need the underlying distribution, which a histogram's buckets provide.",
        },
    ],
    "interview": [
        {
            "q": "What is the difference between rate(), irate() and increase()?",
            "a": (
                "The rate() function gives the average per-second increase of a counter over the whole range and handles counter resets. "
                "That makes it the default for graphs and alerts. "
                "The irate() function uses only the last two samples in the range, which reacts fast but is noisy, so it suits zoomed-in graphs and not alerts. "
                "The increase() function is rate() multiplied by the range in seconds, so it reads as a count, but it can return fractions. "
                "All three need at least two samples in the range."
            ),
        },
        {
            "q": "How do you compute a p95 latency in Prometheus, and what are the pitfalls?",
            "a": (
                "You take rate() of the histogram's _bucket series, sum them by le (plus any labels you want to keep), and pass that to histogram_quantile(0.95, ...). "
                "Pitfalls: dropping le from the sum gives an empty result, averaging percentiles from summaries is mathematically wrong, and the answer is an interpolation inside one bucket. "
                "If the buckets are coarse, the p95 can be far from the truth, and if requests are slower than the largest finite bucket you only get that bucket's limit."
            ),
        },
        {
            "q": "Why use recording rules?",
            "a": (
                "A recording rule evaluates an expensive query on a fixed schedule and stores the result as a new series. "
                "Dashboards and alerts then read that series cheaply, and everyone uses exactly the same definition, for example of the error ratio. "
                "They are also needed for long windows, such as 6-hour or 3-day ratios for SLO alerts, which would be slow to compute on every evaluation from raw data. "
                "The convention is to name them level:metric:operations, such as job:http_requests:rate5m."
            ),
        },
    ],
    "deeper": {
        "minutes": 12,
        "body": (
            "Why did `increase()` return 266.67 requests in a minute instead of a whole number? Because `rate()` and `increase()` estimate what happened at the edges of the window.\n\n"
            "Inside a one-minute window at a 15-second scrape there are about four samples, for example 99, 167, 235 and 303. "
            "The first one is a few seconds after the window starts and the last one a few seconds before it ends. "
            "The samples only cover about 45 seconds of the 60. "
            "So Prometheus takes the growth it can see (204) and extends the line to both edges of the window. "
            "It does that as long as each gap is no more than 1.1 times the usual spacing between samples. "
            "The result is 204 scaled up to the full minute, roughly 266. "
            "PromLabs' post [How exactly does PromQL calculate rates?](https://promlabs.com/blog/2021/01/29/how-exactly-does-promql-calculate-rates/) walks through the exact rules.\n\n"
            "This explains two other numbers from this lesson.\n"
            "- A five-minute increase once said 1216.6 for a counter that read 1175. The counter was younger than the window, and the estimate added a little at each end.\n"
            "- A two-minute-old series showed a 5-minute rate of 1.55 while the 1-minute rate was 4.44. When the gap to the window's start is larger than that, Prometheus decides the series began inside the window and stretches the line only half a scrape interval. "
            "Then it divides about two minutes of growth by five minutes of time.\n\n"
            "It also explains a trap from the task. A counter series that appears for the first time with the value 6 has no earlier sample. "
            "So `rate()` cannot know whether those 6 happened just now or an hour ago, and it ignores them. "
            "Only increases between two scrapes count. "
            "That is why well-written apps create their error series at 0 when they start, before any error happens. "
            "In Python you call `.labels(...)` once at startup for the label values you expect.\n\n"
            "None of this matters much for dashboards and alerts over 5 minutes or more. "
            "It matters when you compare Prometheus with exact counts from logs, or alert on increase() of something rare. "
            "There, reach for longer windows, and remember the result is an estimate."
        ),
    },
    "sources": [src("basics"), src("functions"), src("operators"), src("histograms")],
}
