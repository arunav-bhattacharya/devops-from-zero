"""Book-voice rewrite of Part 12's own fields. Writer: tg."""
import json, pathlib

P = pathlib.Path("/home/user/devops-from-zero/content/p12.json")
d = json.loads(P.read_text())

d["intro"] = (
    "Part 11 left hello-devops running on kind, deployed by Argo CD. This part shows you how it is doing. The first "
    "lesson covers the ideas every monitoring tool shares: signals, targets for reliability, error budgets, and "
    "alerts on what users feel. The next three put them to work with Prometheus in a Compose lab on your laptop. "
    "You learn its query language up to a full view of rate, errors and duration, send alerts to a receiver, and "
    "then watch the app on Kubernetes the same way."
)

d["recap"] = [
    "Monitoring watches for known problems; observability lets you ask new questions of metrics, logs, traces and profiles.",
    "RED (rate, errors, duration) describes a service, and USE (utilization, saturation, errors) describes a machine.",
    "An SLO is a target for an SLI over a window; the error budget is 100% minus the SLO, and the burn rate decides pages and tickets.",
    "Prometheus pulls each target's /metrics page and stores one series per metric name and label set; up = 0 means a failed scrape.",
    "Counters need rate() over a range of at least 4 scrape intervals; take the rate first, then sum.",
    "Latency percentiles come from histogram_quantile over summed bucket rates that keep the le label; the buckets set the accuracy.",
    "Alerting rules wait out their for: time, then Alertmanager groups, routes, inhibits and silences before anyone hears.",
    "Test rules with promtool before they page anyone.",
    "On Kubernetes, kube-prometheus-stack reads ServiceMonitors and PrometheusRules only when they carry the release label.",
    "Local storage keeps 15 days by default in one copy; remote write to Thanos, Mimir or a hosted service keeps a longer history.",
]

cards = [
    ("What does up == 0 mean for a target?", "Prometheus's last scrape of it failed: the target is down, cannot be reached, or is too slow to answer."),
    ("What makes two time series different?", "A different metric name, or any different label value."),
    ("Which metric type only goes up?", "A counter. It drops to zero only when the process restarts."),
    ("Why must you never take rate() of a gauge?", "rate() treats every drop as a counter reset, so a value that goes up and down gives nonsense."),
    ("Rule of thumb for the range in rate(x[...])?", "At least 4 times the scrape interval, so 1m for a 15s scrape."),
    ("Rate then sum, or sum then rate?", "Rate first, then sum. Adding raw counters first hides restarts."),
    ("Which label must survive when you sum histogram buckets for histogram_quantile?", "le, the bucket's upper limit."),
    ("How do you work out a burn rate?", "The current error ratio divided by the error budget (1 minus the SLO)."),
    ("Error budget of a 99.9% SLO over 30 days, as a full outage?", "43.2 minutes."),
    ("What does for: 5m do in an alerting rule?", "The condition must stay true for 5 minutes. Until then the alert is pending, not firing."),
    ("Where do silences live?", "In Alertmanager while it runs, made in its UI or with amtool, not in alertmanager.yml."),
    ("What does an inhibition rule do?", "It mutes some alerts while another one fires, such as tickets while a page fires for the same job."),
    ("Your ServiceMonitor applies fine but no target appears. First suspect?", "A missing release label for the Helm release, or a selector or port name that does not match the Service."),
    ("kube-state-metrics or metrics-server: which one does Prometheus scrape for Deployment replica counts?", "kube-state-metrics. metrics-server only gives current CPU and memory to kubectl top and autoscalers."),
    ("Default Prometheus retention?", "15 days, on local disk, in a single copy."),
    ("When is the Pushgateway the right tool?", "For the result of a short batch job that may finish between scrapes."),
]
assert len(cards) == len(d["flashcards"])
for f, (front, back) in zip(d["flashcards"], cards):
    f["front"], f["back"] = front, back

whys = [
    "Start here: the official map of the server, exporters, Pushgateway and Alertmanager, with a picture of how they connect.",
    "The reference for choosing series, instant and range vectors, offset and the 5-minute lookback.",
    "Every PromQL function and exactly what it does, including how rate() estimates at the edges.",
    "Why histograms usually beat summaries, and the common histogram_quantile mistakes.",
    "The full Alertmanager settings reference: routes, receivers, inhibition and timing.",
    "The chapter that works out, step by step, the two-window burn-rate alerts this part builds.",
    "Google's original explanation of SLIs, SLOs and SLAs, with examples of choosing targets.",
    "A short, beginner-friendly tour of targets, pulling, the Pushgateway and Alertmanager.",
    "One of Prometheus's creators shows PromQL with live examples.",
    "More from Julius Volz: short videos on histograms, rates and the finer points of PromQL.",
    "Read this when increase() returns a fraction or a young series reads low; it shows the exact maths.",
    "The README and settings for kube-prometheus-stack, the usual way to run Prometheus on Kubernetes.",
]
assert len(whys) == len(d["resources"])
for r, w in zip(d["resources"], whys):
    r["why"] = w

quiz = [
    ("Prometheus scrapes a target every 30 seconds. What is the smallest sensible range for rate() on its counters?",
     "The rule of thumb is at least 4 scrape intervals, so rate() always has several samples to work with: 4 times 30s is 2m."),
    ("An API answers every request in about 3 ms. Its histogram's first bucket is le=\"0.1\", and the p95 query returns exactly 0.095. Why?",
     "histogram_quantile only knows bucket counts. With every request in the 0 to 0.1 bucket, it estimates evenly and lands at 0.95 of 0.1."),
    ("Which query gives hello-devops's share of failed responses correctly?",
     "Take the rate of each counter first, add them up, then divide. The others divide raw totals, count series instead of requests, or use a range too short to hold two samples."),
    ("An alert has for: 10m. Its condition is true for 8 minutes, false for one check, then true again. When does it fire?",
     "A false check resets the pending state, so the 10-minute wait starts again from the moment the condition is true again."),
    ("With kube-prometheus-stack, which object adds your own alerting rules to Prometheus?",
     "The Prometheus Operator turns PrometheusRule objects into rule files, but only those it is set to read, which by default means the release label."),
    ("Your team wants a year of metrics and one query view across three clusters. What do you add?",
     "Local storage keeps one copy, and each server sees only its own cluster. Thanos and Mimir keep the data in object storage and query across all of them."),
    ("Which alert follows the symptom rule best?",
     "Error budget burn measures failed requests, which users feel. The others are possible causes that often hurt nobody."),
    ("On a Mac, the lab's node_exporter container reports node_uname_info with sysname=\"Linux\". Why?",
     "Docker Desktop runs every container in a small Linux virtual machine, so an exporter in a container sees that machine, not macOS."),
    ("In the lab's compose.yaml, Prometheus scrapes web:8000. Why does the name web work?",
     "Compose creates its own network for the project, and Docker's built-in name service answers each service name with that container's address."),
    ("node_exporter shows node_load1 = 7.6 on a machine with 4 CPUs. In USE terms, what does that suggest?",
     "Load average counts processes that are running or waiting (on Linux, also those waiting on disk). Well above the CPU count means work is queuing, which is saturation."),
]
assert len(quiz) == len(d["quiz"])
for q, (qq, why) in zip(d["quiz"], quiz):
    q["q"], q["why"] = qq, why

P.write_text(json.dumps(d, indent=1, ensure_ascii=False) + "\n")
print("p12 part fields written")
