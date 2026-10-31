from common import L


def res(key, why, title=None, kind=None):
    t, u, k = L[key]
    return {"title": title or t, "url": u, "kind": kind or k, "why": why}


PART = {
    "part": 9,
    "title": "Monitoring with Prometheus",
    "intro": (
        "Part 8 left hello-devops running on kind, deployed by Argo CD. This part teaches you to see how it is doing. "
        "Day 41 builds the ideas every monitoring tool shares: signals, SLOs, error budgets and alerts on what users feel. "
        "Days 42 to 44 put them to work with Prometheus. You run a Compose lab on your laptop, learn PromQL from the first query to a full RED view, "
        "send alerts to a receiver, and finally set up the same on Kubernetes."
    ),
    "recap": [
        "Monitoring watches for known problems; observability lets you ask new questions of metrics, logs, traces and profiles.",
        "RED (rate, errors, duration) describes a service, USE (utilization, saturation, errors) describes a machine.",
        "An SLO is a target for an SLI over a window; the error budget is 100% minus the SLO, and the burn rate decides pages and tickets.",
        "Prometheus pulls each target's /metrics page and stores one series per metric name and label set; up = 0 means a failed scrape.",
        "Counters need rate() over a range of at least 4 scrape intervals; take the rate first, then sum.",
        "Latency percentiles come from histogram_quantile over summed bucket rates that keep the le label, and bucket limits set the accuracy.",
        "Alerting rules wait out their for: time, then Alertmanager groups, routes, inhibits and silences before a receiver is notified.",
        "Test rules with promtool before they page anyone.",
        "On Kubernetes, kube-prometheus-stack reads ServiceMonitors and PrometheusRules only when they carry the release label.",
        "Local storage keeps 15 days by default; remote write to Thanos, Mimir or a hosted service gives long-term history.",
    ],
    "flashcards": [
        {"front": "What does up == 0 mean for a target?", "back": "Prometheus's last scrape of it failed: the target is down, unreachable or too slow to answer."},
        {"front": "What makes two time series different?", "back": "A different metric name or any different label value."},
        {"front": "Which metric type only goes up?", "back": "A counter. It drops to zero only when the process restarts."},
        {"front": "Why must you never take rate() of a gauge?", "back": "rate() treats every drop as a counter reset, so a value that goes up and down gives nonsense."},
        {"front": "Rule of thumb for the range in rate(x[...])?", "back": "At least 4 times the scrape interval, so 1m for a 15s scrape."},
        {"front": "Rate then sum, or sum then rate?", "back": "Rate first, then sum. Summing raw counters first hides restarts."},
        {"front": "Which label must survive when you sum histogram buckets for histogram_quantile?", "back": "le, the bucket's upper limit."},
        {"front": "How do you compute a burn rate?", "back": "The current error ratio divided by the error budget (1 minus the SLO)."},
        {"front": "Error budget of a 99.9% SLO over 30 days, as full outage?", "back": "43.2 minutes."},
        {"front": "What does for: 5m do in an alerting rule?", "back": "The condition must stay true for 5 minutes. Until then the alert is pending, not firing."},
        {"front": "Where do silences live?", "back": "In Alertmanager at run time, made in its UI or with amtool, not in alertmanager.yml."},
        {"front": "What does an inhibition rule do?", "back": "It mutes some alerts while another one fires, such as tickets while a page fires for the same job."},
        {"front": "Your ServiceMonitor applies fine but no target appears. First suspect?", "back": "A missing release label for the Helm release, or a selector or port name that does not match the Service."},
        {"front": "kube-state-metrics or metrics-server: which one does Prometheus scrape for Deployment replica counts?", "back": "kube-state-metrics. metrics-server only serves current CPU and memory to kubectl top and autoscalers."},
        {"front": "Default Prometheus retention?", "back": "15 days, on local disk, not replicated."},
        {"front": "When is the Pushgateway the right tool?", "back": "For the result of a short, service-level batch job that may finish between scrapes."},
    ],
    "resources": [
        res("overview", "The official map of the server, exporters, Pushgateway and Alertmanager, with the architecture picture."),
        res("basics", "The reference for selectors, instant and range vectors, offset and the lookback window."),
        res("functions", "Every PromQL function with its exact behaviour, including how rate() extrapolates."),
        res("histograms", "Why histograms usually beat summaries, and the classic histogram_quantile mistakes."),
        res("am_config", "The full Alertmanager config reference: routes, receivers, inhibition and timing."),
        res("sre_wb_alerting", "The chapter that derives the multiwindow, multi-burn-rate alerts used on Day 44, step by step."),
        res("sre_slo", "Google's original explanation of SLIs, SLOs and SLAs, with examples of choosing targets."),
        res("v_how_prom", "A short, beginner-friendly tour of targets, the pull model, the Pushgateway and Alertmanager."),
        res("v_promql", "One of Prometheus's creators shows PromQL with live examples."),
        res("v_promlabs", "Short videos from Prometheus co-founder Julius Volz on histograms, rates and PromQL details."),
        res("promlabs_rates", "Explains exactly why increase() returns fractions and why young series read low."),
        res("kps_chart", "The README and values for kube-prometheus-stack, the usual way to run Prometheus on Kubernetes."),
    ],
    "quiz": [
        {
            "q": "Prometheus scrapes a target every 30 seconds. What is the smallest sensible range for rate() on its counters?",
            "options": ["[30s]", "[1m]", "[2m]", "[30m]"],
            "answer": 2,
            "why": "The rule of thumb is at least 4 scrape intervals, so rate() always has several samples to work with: 4 times 30s is 2m.",
        },
        {
            "q": "An API answers every request in about 3 ms. Its histogram's first bucket is le=\"0.1\", and the p95 query returns exactly 0.095. Why?",
            "options": [
                "The API is much slower than it looks",
                "Prometheus adds its own network time",
                "The scrape interval is too long",
                "All requests sit in the first bucket",
            ],
            "answer": 3,
            "why": "histogram_quantile only knows bucket counts. With all requests in the 0 to 0.1 bucket, it interpolates linearly to 0.95 of 0.1.",
        },
        {
            "q": "Which query gives hello-devops's share of failed responses correctly?",
            "options": [
                "sum(rate(hello_responses_total{status=~\"5..\"}[5m])) / sum(rate(hello_responses_total[5m]))",
                "avg(hello_responses_total{status=~\"5..\"}) / avg(hello_responses_total)",
                "count(hello_responses_total{status=~\"5..\"}) / count(hello_responses_total)",
                "rate(hello_responses_total{status=~\"5..\"}[10s])",
            ],
            "answer": 0,
            "why": "Take the rate of each counter first, sum, then divide. The others divide raw totals, count series instead of requests, or use a range too short to hold two samples.",
        },
        {
            "q": "An alert has for: 10m. Its condition is true for 8 minutes, false for one evaluation, then true again. When does it fire?",
            "options": [
                "At 10 minutes after it first became true",
                "Right away when the condition comes back",
                "10 minutes after the condition came back",
                "Never, because Alertmanager drops it",
            ],
            "answer": 2,
            "why": "A false evaluation resets the pending state, so the 10-minute wait starts again from the moment the condition is true again.",
        },
        {
            "q": "With kube-prometheus-stack, which object adds your own alerting rules to Prometheus?",
            "options": ["A ServiceMonitor for the app", "A PrometheusRule with the release label", "A ConfigMap named prometheus-rules", "A PodMonitor with the release label"],
            "answer": 1,
            "why": "The Prometheus Operator turns PrometheusRule objects into rule files, but only those its ruleSelector matches, which by default means the release label.",
        },
        {
            "q": "Your team wants a year of metrics and one query view across three clusters. What do you add?",
            "options": [
                "Thanos or Mimir, fed by sidecars or remote write",
                "A retention of 365d on each local Prometheus",
                "A Pushgateway in every cluster",
                "More recording rules on each server",
            ],
            "answer": 0,
            "why": "Local storage is not replicated and each server sees only its own cluster; Thanos and Mimir keep blocks in object storage and query across all of them.",
        },
        {
            "q": "Which alert follows the symptom rule best?",
            "options": [
                "Node CPU above 85% for 10 minutes",
                "More than 2 pod restarts in an hour",
                "2% of the monthly error budget spent in 1 hour",
                "Memory above 90% on any container",
            ],
            "answer": 2,
            "why": "Error budget burn measures failed requests, which users feel. The others are possible causes that often hurt nobody.",
        },
        {
            "q": "On a Mac, the lab's node_exporter container reports node_uname_info with sysname=\"Linux\". Why?",
            "options": [
                "node_exporter cannot read macOS at all",
                "Containers run inside Docker Desktop's Linux VM, so it measures that VM",
                "Prometheus rewrites the label when it stores it",
                "The image was built for Linux servers only by mistake",
            ],
            "answer": 1,
            "why": "Docker Desktop runs every container in a small Linux virtual machine, so a containerised exporter sees that VM, not macOS.",
        },
        {
            "q": "In the lab's compose.yaml, Prometheus scrapes web:8000. Why does the name web work?",
            "options": [
                "Docker adds web to the Mac's /etc/hosts file",
                "Prometheus has a built-in list of service names",
                "web is a reserved name for port 8000",
                "Docker's DNS on the Compose network resolves it",
            ],
            "answer": 3,
            "why": "Compose creates a user-defined network for the project, and Docker's built-in DNS answers each service name with that container's address.",
            "from": "Part 3",
        },
        {
            "q": "node_exporter shows node_load1 = 7.6 on a machine with 4 CPUs. In USE terms, what does that suggest?",
            "options": [
                "Saturation: more processes want to run than there are CPUs",
                "Errors: the CPUs are failing",
                "Low utilization: the CPUs are mostly idle",
                "Nothing, load average only counts disk reads",
            ],
            "answer": 0,
            "why": "Load average counts processes that are running or waiting (on Linux, also those waiting on disk). Well above the CPU count means work is queuing, which is saturation.",
            "from": "Part 1",
        },
    ],
}
