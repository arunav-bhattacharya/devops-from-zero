"""Book-voice rewrite of d51 (PromQL from zero). Writer: tg."""
import json, pathlib

P = pathlib.Path("/home/user/devops-from-zero/content/p12.json")
d = json.loads(P.read_text())
L = next(x for x in d["lessons"] if x["id"] == "d51")

L["opening"] = (
    "Picture a car whose speedometer has broken. Only the odometer still works, the counter of every kilometre "
    "the car has ever driven. It reads 52,310. Are you going too fast? The number cannot tell you. But note it "
    "now, note it again a minute later, and divide the difference by the time. Now you know your speed.\n\n"
    "It is tempting to stare at the big number and feel informed, because it is precise and it keeps moving. Our "
    "app's counters are odometers: 303 requests since the app started says almost nothing about right now.\n\n"
    "Last time, Prometheus started writing down hello-devops's numbers every 15 seconds. In this lesson, we'll "
    "learn to ask that pile of numbers questions. We'll start from one bare name and build, step by step, the "
    "three queries that say how the app is doing: how busy, how broken, how slow. Along the way we'll see why a "
    "query sometimes returns nothing at all, and why that is not the same as zero.\n\n"
    "Before we start, make a guess, and keep it in mind."
)

L["guess"]["q"] = (
    "Prometheus scrapes, or reads, the app every 15 seconds. What does the query "
    "rate(hello_responses_total[10s]) return?"
)
L["guess"]["why"] = (
    "rate() needs at least two readings inside the time range. A 10-second window usually holds only one reading "
    "when Prometheus reads every 15 seconds, so the series quietly drops out of the result, with no error."
)

plains = {
    "PromQL": "Prometheus's query language: you pick series by name and labels, then do maths on them.",
    "Instant vector": "A set of series with one value each, all for the same moment.",
    "Range vector": "A set of series with all their readings over a time window, such as the last 5 minutes.",
    "Label matcher": "A filter on a label inside braces: = and != for exact values, =~ and !~ for text patterns.",
    "rate()": "The average growth per second of a counter over a time range, with restarts handled.",
    "Aggregation": "Combining many series into fewer with sum, avg, max, count or topk, grouped by labels.",
    "histogram_quantile()": "Estimates a percentile, such as p95, from the rates of histogram buckets.",
    "Recording rule": "A query Prometheus runs on a schedule and stores as a new series that is cheap to read.",
}
for t in L["terms"]:
    t["plain"] = plains[t["term"]]

S = L["sections"]

S[0]["h"] = "Where to type PromQL, and what comes back"
S[0]["body"] = (
    "PromQL is the language you use to ask Prometheus questions. Each question is called a query, and you can type "
    "it in two places. The web page at `localhost:9090` has a Query page with three tabs:\n"
    "- Table shows the current value of each series.\n"
    "- Graph draws the series over time.\n"
    "- Explain breaks a query into its parts.\n\n"
    "In the terminal, the `q` function from last time runs the same query through `promtool`, Prometheus's command "
    "line tool.\n\n"
    "Every query works on the time series from last time. A series is a metric name plus labels, with one sample "
    "per scrape: a timestamp and a value. Our lab app, hello-devops, is the tiny web app that greets every visitor "
    "and counts the visits, and its series are what we will query. A query does two jobs. It picks series by name "
    "and labels, and then it does maths on their samples.\n\n"
    "The simplest query is a metric name. `hello_responses_total` returned three series in one test run, one per "
    "label set:\n"
    "- `{path=\"/\", status=\"200\"} 303`\n"
    "- `{path=\"/healthz\", status=\"200\"} 3`\n"
    "- `{path=\"unmatched\", status=\"404\"} 1`\n\n"
    "The `job` and `instance` labels are left out here to keep the lines short. That result is an instant vector: "
    "one value per series, all for the same moment. It is like asking every car in a car park for its odometer "
    "reading right now.\n\n"
    "Scrapes rarely land exactly on the moment you ask about, so Prometheus takes the newest sample that is at most "
    "5 minutes old. A series nobody has scraped for 5 minutes drops out.\n\n"
    "Add a duration in square brackets and you get a range vector: every sample in that window. "
    "`hello_responses_total{path=\"/\"}[1m]` returned four samples, 99, 167, 235 and 303, 15 seconds apart. Those four "
    "numbers already hold the request rate. The counter grew by 204 in 45 seconds, about 4.5 a second. The "
    "`rate()` function below does that subtraction and division for you.\n\n"
    "The Graph tab cannot draw a range vector, because each point on a graph needs one value per series, not a "
    "list. Functions such as `rate()` take it as input and turn it back into one value per series.\n\n"
    "Before we do maths, we need to pick the right series. Next, filters."
)

S[1]["h"] = "Choosing series with label matchers"
S[1]["body"] = (
    "In the car park, you rarely want every car. You want the red ones, or every car except the vans. Braces after "
    "a metric name filter by label in the same way. There are four matchers:\n"
    "- `=` exact: `{path=\"/\"}` keeps only the root route.\n"
    "- `!=` not equal: `{path!=\"/\"}` returned `/healthz` and `unmatched`.\n"
    "- `=~` regex: `{status=~\"5..\"}` means any 5xx status.\n"
    "- `!~` regex, negated: `{path!~\"/|/healthz\"}` keeps every other route.\n\n"
    "A regex, short for regular expression, is a pattern for matching text. In `5..`, each dot stands for any one "
    "character, so it matches 500, 503 and every other 5xx status, the codes that mean the server failed.\n\n"
    "Regexes match the whole value, as if they started with `^` and ended with `$`. So `{path=~\"/health\"}` "
    "returned nothing, while `{path=~\"/health.*\"}` found `/healthz`. In the shell, wrap the whole query in single "
    "quotes so the double quotes inside survive.\n\n"
    "An empty result is not zero, and the two are easy to confuse. Empty means no series matched. Before the app "
    "had ever failed, `hello_responses_total{status=~\"5..\"}` returned nothing, because no series with a 5xx label "
    "existed yet.\n\n"
    "Any maths with an empty side is empty too, so an error ratio showed nothing instead of 0. Adding "
    "`or vector(0)` to the error part gives a real zero. It is the difference between a chart that says \"no "
    "errors\" and a chart with the page torn out.\n\n"
    "Now we can pick the series. Next, we'll turn an odometer into a speedometer."
)

S[2]["h"] = "Counters need rate(): from odometer to speed"
S[2]["body"] = (
    "A raw counter is an odometer. It only tells you how many requests the process, the running copy of the app, "
    "served since it started. It also falls back to zero on every restart. When the `web` container was recreated "
    "in one test, the counter went from 2370 to 11.\n\n"
    "`rate(hello_responses_total{path=\"/\"}[1m])` gives the average increase per second over the last minute. It "
    "read 4.56 in that run, from a loop sending about 4.5 requests a second. Roughly, it subtracts the first sample "
    "in the window from the last and divides by the seconds between them. Go deeper shows the small correction it "
    "makes at the edges.\n\n"
    "It treats any drop as a restart, like a mechanic who sees a lower odometer reading and knows the odometer was "
    "replaced. When 2370 was followed by 11, it counted those 11 as new requests, not as a fall of 2359. After that "
    "restart, `resets()` counted 1 reset and `rate()` still read 3.3 per second.\n\n"
    "**A counter on its own says almost nothing. Ask for its rate.**\n\n"
    "Choose the range carefully:\n"
    "- Use at least 4 times the scrape interval. The function needs two samples in the window, and four intervals leave enough when a scrape fails. With a 15-second scrape, `[10s]` returned nothing and `[1m]` worked.\n"
    "- Longer ranges are smoother but slower to react. Dashboards often use `[5m]`.\n"
    "- Right after a start, long ranges read low. At two minutes old, `[5m]` gave 1.55 while `[1m]` gave 4.44. Five minutes later they agreed: 4.49 and 4.56.\n\n"
    "That first point answers the guess. With only one reading in the window, there is nothing to subtract, and the "
    "series simply leaves the result.\n\n"
    "`rate()` has two relatives:\n"
    "- `increase(x[1m])` is the rate times 60: \"how many in the last minute\". It returned 266.67, not a whole number, because it estimates to the edges of the window. Once it even said 1216.6 for a counter that read 1175.\n"
    "- `irate(x[1m])` uses only the last two samples. It is jumpy, fine for a zoomed-in graph and wrong for alerts.\n\n"
    "One rate per series is often too many lines. Next, we'll add them up."
)

S[3]["h"] = "Adding series up: sum, by and without"
S[3]["body"] = (
    "A taxi company does not want each car's speed. It wants the distance the whole fleet covers per hour, or per "
    "city. `rate()` returns one result per series, and adding them up is called aggregation. "
    "For example, `sum(rate(hello_responses_total[5m]))` added everything into one number: 3.53 requests a second.\n\n"
    "Add `by` to keep some labels, or `without` to drop some:\n"
    "- `sum by (path) (rate(hello_responses_total[5m]))` gave `/` 3.51, `/healthz` 0.028 and `unmatched` 0.\n"
    "- `sum without (instance, status) (...)` drops only those two labels and keeps `job` and `path`.\n\n"
    "The `/healthz` line is traffic you may not have known about. It is the Docker health check from Day 22, a "
    "small \"are you alive?\" request every 30 seconds, so about 0.03 a second.\n\n"
    "Other aggregations work the same way:\n"
    "- `avg`, `min` and `max`, such as `max by (job) (process_resident_memory_bytes)`.\n"
    "- `count`, such as `count by (job) (up)` for the number of targets per job.\n"
    "- `topk(2, ...)` and `bottomk`, for the largest or smallest few series.\n\n"
    "**Take the rate of each series first, then add them up. Never the other way round.**\n\n"
    "Here is why. Each instance's counter restarts on its own, the way each taxi gets its own odometer replaced. "
    "Only `rate()` can see a restart, and only one series at a time. If you sum first, a restart of one instance "
    "makes the total dip. Then `rate()` mistakes the dip for a reset of the whole sum and shows a false spike. "
    "Robust Perception's post [Rate then sum](https://www.robustperception.io/rate-then-sum-never-sum-then-rate/) "
    "shows what goes wrong otherwise.\n\n"
    "Sums tell us how busy the app is. To know how broken it is, we need to divide one sum by another. That is "
    "next."
)

S[4]["h"] = "Maths between series: ratios, filters and matching"
S[4]["body"] = (
    "If 3 taxis in 100 broke down today, the useful number is 3%, not 3. You can divide one query by another in "
    "the same way. The error ratio is failed responses per second divided by all responses per second: "
    "`sum(rate(hello_responses_total{status=~\"5..\"}[5m])) / sum(rate(hello_responses_total[5m]))`.\n\n"
    "Between two sets of series, Prometheus pairs series whose labels are exactly the same. Try a per-path error "
    "ratio with `sum by (path, status) (...)` on the left and `sum by (path) (...)` on the right. The result is "
    "empty, because the left side has a `status` label the right side lacks.\n\n"
    "Adding `/ ignoring(status)` between them, or `/ on(path)`, gave `/` 0.054 and `/readyz` NaN. NaN means \"not "
    "a number\", the answer to 0 divided by 0: nobody called `/readyz` in that window.\n\n"
    "Comparison operators filter. These examples use the saved error ratio, "
    "`job:hello_responses_errors:ratio_rate5m`, one of the recording rules at the end of this lesson:\n"
    "- `job:hello_responses_errors:ratio_rate5m > 0.02` keeps series above 2% and drops the rest. Alert rules use this form.\n"
    "- `... > bool 0.02` returns 1 or 0 for every series instead.\n\n"
    "Three more tools:\n"
    "- `offset` looks back in time. `hello_responses_total{path=\"/\"} offset 5m` read 30 while the live value was 1380.\n"
    "- `up == 0` lists every target whose last scrape failed.\n"
    "- `absent(up{job=\"payments\"})` returns 1 when no such series exists at all. It catches a job that vanished, which `up == 0` cannot.\n\n"
    "That last one is the empty-bed problem from last time, seen from the other side. The query `up == 0` finds a "
    "patient who did not answer. `absent()` notices that the bed itself has gone from the list.\n\n"
    "We have busy and broken. The third question is how slow, and it needs the histogram."
)

S[5]["h"] = "How slow? Latency from histograms"
S[5]["body"] = (
    "Picture a post office that sorts parcels by weight into boxes marked \"up to 1 kg\", \"up to 2 kg\", \"up to 5 "
    "kg\". It never writes down each parcel's exact weight, only how many landed in each box. A histogram does the "
    "same with request times, and each box is a bucket.\n\n"
    "Each histogram bucket is a counter, so you treat it like one. Over the window, `rate()` turns each bucket's "
    "total since start into \"requests per second that took this long or less\". Then you add the buckets up while "
    "keeping `le`, the label that holds each bucket's limit. Finally `histogram_quantile()` estimates the "
    "percentile:\n"
    "`histogram_quantile(0.95, sum by (le) (rate(hello_request_duration_seconds_bucket{path=\"/\"}[5m])))`\n\n"
    "In one healthy run that gave a p95 of 0.018 seconds, a p50 of 0.0036 and a p99 of 0.045. A p95 of 0.018 means "
    "95% of requests took 0.018 seconds or less. The average comes from the other two series: "
    "`rate(..._sum[5m]) / rate(..._count[5m])` gave 0.0060. Drop `le` from the `by` clause and the result is empty, "
    "because the function needs the bucket limits.\n\n"
    "The answer is an estimate. Say 100 requests a second arrive: 80 finish within 0.01 seconds and 97 within "
    "0.025. The 95th request falls in the bucket between those limits, which holds 17 requests. The function "
    "assumes they are spread evenly. So it answers 0.01 plus 15/17 of the bucket's 0.015-second width: about 0.023 "
    "seconds. Both of these happened in the lab:\n"
    "- Prometheus's own query API answered in a few milliseconds, but its first bucket is 0 to 0.1 seconds. The p95 came out at exactly 0.095.\n"
    "- During a Redis outage, hello-devops's p95 read 6.12 seconds: somewhere in the 5 to 7.5 second bucket.\n\n"
    "If most requests are slower than the largest finite bucket, the function can only return that bucket's limit, "
    "10 seconds for the default buckets. So choose bucket limits around the latencies you care about. And never "
    "average percentiles from several servers. Sum the buckets, then compute the percentile once, as the "
    "[histograms guide](https://prometheus.io/docs/practices/histograms/) explains.\n\n"
    "We now have all three answers. Next, we'll put them together and save them."
)

S[6]["h"] = "RED for hello-devops, saved as recording rules"
S[6]["body"] = (
    "Put the pieces together and you have RED for hello-devops, per job. RED is the checklist from two lessons "
    "ago: rate, errors and duration.\n"
    "- Rate: `sum by (job) (rate(hello_responses_total[5m]))`\n"
    "- Errors: `sum by (job) (rate(hello_responses_total{status=~\"5..\"}[5m])) / sum by (job) (rate(hello_responses_total[5m]))`\n"
    "- Duration: `histogram_quantile(0.95, sum by (job, le) (rate(hello_request_duration_seconds_bucket[5m])))`\n\n"
    "Dashboards and alerts will run these every few seconds, forever. A car's trip computer works out the average "
    "speed once and shows the result, so the driver never redoes the sum. A recording rule does the same. It runs a "
    "query on Prometheus's schedule (every 15 seconds in the lab) and stores the answer as a new series. Reading "
    "that series is cheap, and every dashboard and alert gets the same number.\n\n"
    "The lab keeps them in `observability/prometheus/rules/recording.yml`. The names follow the [naming "
    "convention](https://prometheus.io/docs/practices/rules/) `level:metric:operations`. For example, "
    "`job:hello_responses:rate5m` is grouped by job, built from `hello_responses`, and holds a 5-minute rate.\n\n"
    "`prometheus.yml` loads every file in `rules/`. After an edit, check the file with `promtool`, reload "
    "Prometheus, and query the new name. Status, Rule health in the UI shows each rule and its last error.\n\n"
    "These queries answer only when someone asks. At 3 a.m. nobody is typing PromQL, and a broken app can sit there "
    "with a perfect error query that nobody runs. The numbers need a way to come and find us. That is alerting, "
    "and it is where the next lesson goes."
)

# The odometer story carries the analogy; section 3 carries the short-range mistake.
L.pop("analogy", None)
L.pop("mistake", None)
L["real_world"] = (
    "In an incident review, a strange graph often gets one question first: was that a real change, or an empty "
    "result, a NaN or a range that was too short? A payments company with many services might also give every "
    "service the same three RED recording rules from a shared template. Then dashboards and alerts read cheap, "
    "ready-made series, and every team gets the same number for its error ratio."
)

W = L["worked"]["steps"]
W[0]["say"] = (
    "Start with Rate, split by status. The loop from last time sends about 4.5 requests a second, and all of them "
    "succeed. Every query here runs with the `q` function from last time."
)
W[1]["say"] = (
    "Errors. The recording rule returns nothing, because no 5xx series exists yet. With `or vector(0)` on the error "
    "side, the same ratio returns a real 0."
)
W[2]["say"] = "Duration. 95% of requests to `/` finished within about 9.5 ms."
W[3]["say"] = (
    "Break the app's dependency next, and wait about 90 seconds. Every request to `/` now fails, and the rate falls "
    "from 4.5 to 0.24 a second. Each failure takes about 4 seconds, and the loop waits for each one before it sends "
    "the next."
)
W[4]["say"] = (
    "The error ratio over 5 minutes is only 2.4%, although every request fails right now. The window still holds "
    "the healthy minutes, and the failing minutes carry far fewer requests. The 1-hour ratio is the same because "
    "the lab is younger than an hour."
)
W[5]["say"] = (
    "Duration over the last minute jumped from milliseconds to 6.1 seconds. That is an estimate inside the 5 to 7.5 "
    "second bucket, because the Redis client keeps retrying before it gives up."
)
W[6]["say"] = "Bring Redis back. The next lesson uses this same outage to fire real alerts."

T = L["task"]
T["steps"] = [
    "With the lab running, open Explore metrics from the Query page menu and find `prometheus_http_requests_total` and `prometheus_http_request_duration_seconds_bucket`. Note their labels.",
    "Rate: write a query for requests per second per `handler`, showing only handlers with traffic.",
    "Make some errors on purpose: run `curl 'localhost:9090/api/v1/query?query=rate(up'` a few times every minute for two minutes. Each call returns HTTP 400.",
    "Errors: write the share of 4xx and 5xx responses per handler.",
    "Duration: write the p95 for `handler=\"/api/v1/query\"`, then explain the number by looking at that handler's `_bucket` series in the Table tab.",
    "USE for the node: write CPU busy as a percentage, memory in use as a share, and compare `node_load1` with the number of CPUs.",
    "Save one of your queries as a recording rule in a new group in `recording.yml`, check the file with promtool, reload, and query it by its new name.",
]
T["hints"] = [
    "A new series starts at its first scraped value, so rate() never sees the jump from nothing to your first few 400s. Keep sending bad queries for a minute or two.",
    "CPU busy is 1 minus the idle rate: `100 * (1 - avg by (instance) (rate(node_cpu_seconds_total{mode=\"idle\"}[1m])))`.",
    "If your p95 is a round number, look at which bucket holds 95% of the requests.",
]
T["done_when"] = (
    "You have three working queries for Prometheus's own API (rate per handler, share of errors, p95), you can "
    "explain why the p95 is a round number, and one query answers under its recording-rule name."
)

L["explain_back"]["prompt"] = (
    "Explain in 3 to 4 sentences how the p95 latency query for hello-devops works, from the inside out. Mention "
    "buckets, rate(), the le label and why the answer is an estimate."
)
L["explain_back"]["answer"] = (
    "The histogram stores a counter per bucket, such as how many requests took 0.1 seconds or less. First rate() "
    "turns each bucket counter into a per-second rate over the window. Then sum by (le) adds those rates across "
    "routes and instances, and keeps the bucket limits. The histogram_quantile(0.95, ...) function finds the bucket "
    "where 95% of requests are reached and estimates a point inside it. Because it only knows bucket counts, the "
    "result can be off by up to a bucket's width, so bucket limits should sit near the latencies you care about."
)

L["recap"] = [
    "A bare name returns an instant vector; adding [5m] returns a range vector that functions such as rate() use.",
    "Matchers are =, !=, =~ and !~; regexes match the whole value, and an empty result means no series matched, not zero.",
    "Use rate() on counters with a range of at least 4 scrape intervals; increase() is an estimate and irate() is for zoomed-in graphs only.",
    "Take the rate first, then add up with sum, avg, max, count or topk, using by or without.",
    "p95 = histogram_quantile(0.95, sum by (le) (rate(..._bucket[5m]))), an estimate whose accuracy depends on the buckets.",
    "Save common queries as recording rules. A query still answers only when someone asks; alerts come next.",
]

C = L["check"]
C[0]["q"] = (
    "You want the share of requests per instance that failed. Your query "
    "`sum by (instance, status) (rate(errors[5m])) / sum by (instance) (rate(requests[5m]))` returns nothing. What "
    "fixes it?"
)
C[0]["why"] = (
    "The left side has a status label that the right side lacks, so no pairs match until you tell Prometheus to "
    "ignore it."
)
C[1]["q"] = (
    "A service scraped every 30 seconds shows gaps in a graph of `rate(http_requests_total[45s])`. What is the most "
    "likely cause?"
)
C[1]["why"] = "At a 30-second scrape, a 45-second window often holds one sample, so the series drops out. Use at least 2m."
C[2]["q"] = (
    "Three instances each report their own p99 latency through a summary: 0.2 s, 0.3 s and 2.0 s. What is the p99 "
    "across all three?"
)
C[2]["why"] = (
    "Percentiles cannot be averaged or combined. You need the full spread of request times, which a histogram's "
    "buckets provide."
)

I = L["interview"]
I[0]["a"] = (
    "The rate() function gives the average per-second increase of a counter over the whole range, and it handles "
    "counter resets. That makes it the default for graphs and alerts. With irate(), only the last two samples in "
    "the range count, so it reacts fast but is noisy: fine for a zoomed-in graph, wrong for an alert. As for "
    "increase(), it is rate() multiplied by the range in seconds, so it reads as a count but can return fractions. "
    "All three need at least two samples in the range."
)
I[1]["a"] = (
    "You take rate() of the histogram's _bucket series, sum them by le (plus any labels you want to keep), and pass "
    "that to histogram_quantile(0.95, ...). Pitfalls: dropping le from the sum gives an empty result, averaging "
    "percentiles from summaries is mathematically wrong, and the answer is an estimate inside one bucket. If the "
    "buckets are coarse, the p95 can be far from the truth. If requests are slower than the largest finite bucket, "
    "you only get that bucket's limit."
)
I[2]["a"] = (
    "A recording rule runs an expensive query on a fixed schedule and stores the result as a new series. Dashboards "
    "and alerts then read that series cheaply, and everyone uses exactly the same definition, for example of the "
    "error ratio. They are also needed for long windows, such as 6-hour or 3-day ratios for SLO alerts, which would "
    "be slow to compute from raw data every time. The convention is to name them level:metric:operations, such as "
    "job:http_requests:rate5m."
)

L["deeper"]["body"] = (
    "Why did `increase()` return 266.67 requests in a minute instead of a whole number? Because `rate()` and "
    "`increase()` estimate what happened at the edges of the window.\n\n"
    "Inside a one-minute window at a 15-second scrape there are about four samples, for example 99, 167, 235 and "
    "303. The first one is a few seconds after the window starts and the last one a few seconds before it ends. The "
    "samples only cover about 45 seconds of the 60. So Prometheus takes the growth it can see (204) and extends the "
    "line to both edges of the window. It does that as long as each gap is no more than 1.1 times the usual spacing "
    "between samples. The result is 204 scaled up to the full minute, roughly 266. PromLabs' post [How exactly does "
    "PromQL calculate rates?](https://promlabs.com/blog/2021/01/29/how-exactly-does-promql-calculate-rates/) walks "
    "through the exact rules.\n\n"
    "Real data is messier than a neat table, too. The rows never line up perfectly, because each target is scraped "
    "at a slightly different moment, so these estimates happen at the edge of every window.\n\n"
    "This explains two other numbers from this lesson.\n"
    "- A five-minute increase once said 1216.6 for a counter that read 1175. The counter was younger than the window, and the estimate added a little at each end.\n"
    "- A two-minute-old series showed a 5-minute rate of 1.55 while the 1-minute rate was 4.44. When the gap to the window's start is larger than that, Prometheus decides the series began inside the window and stretches the line only half a scrape interval. Then it divides about two minutes of growth by five minutes of time.\n\n"
    "It also explains a trap from the task. A counter series that appears for the first time with the value 6 has "
    "no earlier sample. So `rate()` cannot know whether those 6 happened just now or an hour ago, and it ignores "
    "them. Only increases between two scrapes count. That is why well-written apps create their error series at 0 "
    "when they start, before any error happens. In Python you call `.labels(...)` once at startup for the label "
    "values you expect.\n\n"
    "None of this matters much for dashboards and alerts over 5 minutes or more. It matters when you compare "
    "Prometheus with exact counts from logs, or alert on increase() of something rare. There, reach for longer "
    "windows, and remember the result is an estimate."
)

L["closing"] = (
    "We started with a broken speedometer and an odometer that only went up. Now the odometer has become a "
    "speedometer: `rate()` turns counters into requests per second, a division turns them into an error ratio, and "
    "the buckets give a p95. Recording rules save all three for everyone. In the lab, find one query you wrote "
    "today that might go empty, and decide whether it needs `or vector(0)`.\n\n"
    "Next, we'll make the numbers come to us. How does Prometheus decide that something is wrong, and how does the "
    "right person hear about it, once?"
)

P.write_text(json.dumps(d, indent=1, ensure_ascii=False) + "\n")
print("d51 written")
