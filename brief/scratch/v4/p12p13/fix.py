"""First-principles review of Days 49 to 54 (p12 Prometheus, p13 Grafana).

Exact old -> new replacements in prose fields only. Re-runnable: an edit whose
new text is already in place is skipped. Start from the originals in
brief/scratch/v4/orig/ (p12.json, p13.json). Run from the repo root:
    python3 brief/scratch/v4/p12p13/fix.py
"""

import json
import sys

FILES = {"p12": "content/p12.json", "p13": "content/p13.json"}

# (part, lesson id, path inside the lesson, old, new)
EDITS = [
    # ---------------- Day 49 ----------------
    ("p12", "d49", ("sections", 1, "body"),
     "Metrics are cheap because they are already summed up. A thousand requests a second become one counter that Prometheus reads every 15 seconds.",
     "Metrics are cheap because they are already summed up. The app keeps a counter, one number in memory, and adds 1 to it for every request. A thousand requests a second still make one number, which Prometheus (Day 50) reads every 15 seconds."),
    ("p12", "d49", ("sections", 2, "body"),
     "Three well-known checklists tell you which few numbers to watch first, and they overlap a lot.\n\nThe four golden signals come from the SRE book: latency, traffic, errors and saturation. Its advice is blunt:",
     "One Linux server can report hundreds of different numbers, and nobody can watch them all. Three well-known checklists tell you which few to watch first, and they overlap a lot.\n\nThe four golden signals come from the SRE book:\n- Latency: how long requests take.\n- Traffic: how many requests arrive.\n- Errors: how many of them fail.\n- Saturation: how full the service is, such as a queue that keeps growing.\n\nIts advice is blunt:"),
    ("p12", "d49", ("sections", 4, "body"),
     "page at 14.4 over one hour or 6 over six hours, and open a ticket at 1 over three days. Day 52 turns them into Prometheus alerts.",
     "page at 14.4 over one hour or 6 over six hours, and open a ticket at 1 over three days. The odd 14.4 comes from working backwards: page once a single hour has spent 2% of the budget. 2% of the 720 hours in 30 days is 14.4 hours of budget, and burning that in one hour is burn rate 14.4. Day 52 turns them into Prometheus alerts."),
    ("p12", "d49", ("worked", "steps", 1, "say"),
     "Pick a target and a window, then let the Day 49 script do the arithmetic.",
     "Pick a target and a window, then let this lesson's `error_budget.py` do the arithmetic."),

    # ---------------- Day 50 ----------------
    ("p12", "d50", ("sections", 0, "body"),
     "Prometheus is a server that collects numbers from your programs every few seconds and stores them with a timestamp. It does this by pulling.",
     "hello-devops already counts its visits in memory and shows the number on its `/metrics` page. That page only shows the value right now. Nothing remembers what it was ten minutes ago, so you cannot tell whether traffic is rising or when errors started.\n\nPrometheus is a server that collects numbers from your programs every few seconds and stores them with a timestamp. That stored history is what you graph and alert on. Prometheus collects by pulling."),
    ("p12", "d50", ("sections", 1, "body"),
     "In a big system you do not type addresses. Service discovery",
     "In a big system you do not type addresses: containers and servers come and go, and each new one has a new address. Service discovery"),
    ("p12", "d50", ("sections", 2, "body"),
     "- The Python client adds `process_*` metrics",
     "- The Python client library, `prometheus_client`, adds `process_*` metrics"),
    ("p12", "d50", ("sections", 2, "body"),
     "Prometheus 3 is strict about the HTTP `Content-Type` header of this page. If it is missing",
     "Prometheus 3 is strict about the HTTP `Content-Type` header of this page, because the header tells it which of several formats to parse. If it is missing"),
    ("p12", "d50", ("sections", 3, "body"),
     "That is three time series. Each scrape adds one sample to each: a timestamp and a value.\n\n",
     "That is three time series. Each scrape adds one sample to each: a timestamp and a value. With a 15-second scrape, one minute of the series for `/` and 200 could look like this:\n- 14:00:00, value 99\n- 14:00:15, value 167\n- 14:00:30, value 235\n- 14:00:45, value 303\n\nA graph of that series is these points joined by a line. Prometheus keeps only what the counter read at each scrape, never the single requests in between.\n\n"),
    ("p12", "d50", ("sections", 4, "body"),
     "The raw value is rarely useful; you ask how fast it grows, which is `rate()` on Day 51.",
     "The raw value only says how many since the process started, so 303 tells you little on its own. The useful number is how fast it grows. In the series above, the counter grew by 204 in 45 seconds, about 4.5 requests a second. That is a rate, and the PromQL function `rate()` (Day 51) works it out for every series, even across restarts."),
    ("p12", "d50", ("sections", 4, "body"),
     "You read a gauge as it is, and you never take its `rate()`.",
     "You read a gauge as it is. Never take its `rate()`: that function treats every drop as a restart, and a gauge drops all the time."),
    ("p12", "d50", ("sections", 4, "body"),
     "Next to the buckets come `_sum` (all the seconds added up) and `_count` (how many). From these, Prometheus can estimate percentiles and add them up across many servers.",
     "Next to the buckets come `_sum` (all the seconds added up) and `_count` (how many). Each bucket is itself a counter. Day 51 takes their rates to estimate a percentile, and the buckets of many servers can be added up first."),
    ("p12", "d50", ("sections", 5, "body"),
     "In Prometheus, each new label value creates new series, and series cost memory, disk and query time.",
     "In Prometheus, each new label value creates new series. Prometheus holds every active series in memory, and each one also costs disk and query time."),
    ("p12", "d50", ("sections", 6, "body"),
     "The TSDB keeps recent samples in memory and in a write-ahead log, then writes them to disk in two-hour blocks.",
     "The TSDB keeps the newest samples in memory. It also appends each one to a write-ahead log on disk, so a crash does not lose them. Later it writes them to disk in two-hour blocks."),

    # ---------------- Day 51 ----------------
    ("p12", "d51", ("sections", 0, "body"),
     "In the terminal, the `q` function from Day 50 runs the same query through `promtool`.\n\n",
     "In the terminal, the `q` function from Day 50 runs the same query through `promtool`.\n\nEvery query works on the time series from Day 50. Each series is a name plus labels, with one sample per scrape: a timestamp and a value. A query does two jobs. It picks series by name and labels, and then it does maths on their samples.\n\n"),
    ("p12", "d51", ("sections", 0, "body"),
     "one value per series, all for the same moment. Prometheus takes the newest sample",
     "one value per series, all for the same moment. Scrapes rarely land exactly on the moment you ask about, so Prometheus takes the newest sample"),
    ("p12", "d51", ("sections", 0, "body"),
     "returned four samples, 99, 167, 235 and 303, 15 seconds apart. The Graph tab cannot draw a range vector. Functions",
     "returned four samples, 99, 167, 235 and 303, 15 seconds apart. Those four numbers already hold the request rate: the counter grew by 204 in 45 seconds, about 4.5 a second. The `rate()` function below does that subtraction and division for you.\n\nThe Graph tab cannot draw a range vector, because each point on a graph needs one value per series, not a list. Functions"),
    ("p12", "d51", ("sections", 2, "body"),
     "from a loop sending about 4.5 requests a second. It treats a drop as a restart and adds the new count on top. After that restart,",
     "from a loop sending about 4.5 requests a second. Roughly, it subtracts the first sample in the window from the last and divides by the seconds between them. Go deeper shows the small correction it makes at the edges.\n\nIt treats any drop as a restart. When 2370 was followed by 11, it counted those 11 as new requests, not as a fall of 2359. After that restart,"),
    ("p12", "d51", ("sections", 2, "body"),
     "- Use at least 4 times the scrape interval. With a 15-second scrape,",
     "- Use at least 4 times the scrape interval. The function needs two samples in the window, and four intervals leave enough when a scrape fails. With a 15-second scrape,"),
    ("p12", "d51", ("sections", 3, "body"),
     "Each instance's counter restarts on its own, and only `rate()` can see that, one series at a time.",
     "Each instance's counter restarts on its own, and only `rate()` can see that, one series at a time. If you sum first, a restart of one instance makes the total dip. Then `rate()` mistakes the dip for a reset of the whole sum and shows a false spike."),
    ("p12", "d51", ("sections", 4, "body"),
     "Comparison operators filter:\n",
     "Comparison operators filter. These examples use the saved error ratio, `job:hello_responses_errors:ratio_rate5m`, one of the recording rules at the end of this lesson:\n"),
    ("p12", "d51", ("sections", 5, "body"),
     "Each histogram bucket is a counter, so you treat it like one. Take the rate of every bucket, add them up while keeping `le`, then let `histogram_quantile()` estimate the percentile:",
     "Each histogram bucket is a counter, so you treat it like one. Over the window, `rate()` turns each bucket's total since start into \"requests per second that took this long or less\". Then you add the buckets up while keeping `le`, and `histogram_quantile()` estimates the percentile:"),
    ("p12", "d51", ("sections", 5, "body"),
     "The answer is an estimate. The function finds the bucket that holds the 95th percentile and assumes requests are spread evenly inside it. Both of these happened in the lab:",
     "The answer is an estimate. Say 100 requests a second arrive: 80 finish within 0.01 seconds and 97 within 0.025. The 95th request falls in the bucket between those limits, which holds 17 requests. The function assumes they are spread evenly, so it answers 0.01 plus 15/17 of the bucket's 0.015-second width: about 0.023 seconds. Both of these happened in the lab:"),

    # ---------------- Day 52 ----------------
    ("p12", "d52", ("sections", 0, "body"),
     "An **alerting rule** is a PromQL query with a name.",
     "A dashboard helps only while someone is looking at it, and at 3 a.m. nobody is. So Prometheus checks the conditions itself. An **alerting rule** is a PromQL query with a name."),
    ("p12", "d52", ("sections", 1, "body"),
     "Alertmanager is a separate service. Its job is to turn a stream of alerts into a few useful messages. It does four things:",
     "Prometheus re-sends each firing alert about once a minute, and one broken database can trip dozens of rules at the same time. Sent straight to a phone, that would be a flood. Alertmanager is a separate service that turns this stream into a few useful messages. It does four things:"),
    ("p12", "d52", ("sections", 1, "body"),
     "in the UI on port 9093 or with `amtool`. They are not",
     "in the UI on port 9093 or with `amtool`, its command-line tool. They are not"),
    ("p12", "d52", ("sections", 3, "body"),
     "Both metrics land in the client's default registry, which the app's existing `/metrics` route already prints.",
     "Both metrics land in the client's default registry, the list of every metric the library knows. The app's existing `/metrics` route prints that list with `generate_latest()`, so no route changes."),
    ("p12", "d52", ("sections", 4, "body"),
     "On Kubernetes you rarely write `prometheus.yml` by hand. The usual install",
     "In a cluster, pods come and go, and each new pod gets a new IP. Prometheus can find them with Kubernetes service discovery, but then every team edits one shared `prometheus.yml`. So on Kubernetes you rarely write that file by hand. The usual install"),
    ("p12", "d52", ("sections", 4, "body"),
     "The Operator adds custom resources (Day 38 showed how controllers work):",
     "The Operator adds custom resources (Day 38 showed how controllers work). Each team creates them next to its own app, and the Operator turns them into Prometheus's config and rule files:"),
    ("p12", "d52", ("sections", 5, "body"),
     "Prometheus then scrapes each pod behind the Service directly, one target per pod.",
     "Prometheus then asks Kubernetes which pods stand behind the Service and scrapes each one directly, one target per pod."),

    # ---------------- Day 53 ----------------
    ("p13", "d53", ("sections", 0, "body"),
     "Grafana is a web app for looking at data that lives somewhere else.",
     "During an incident you want a dozen graphs ready on one page, with names, units and colors the whole team agrees on. Prometheus's Query page answers one query at a time.\n\nGrafana is a web app for looking at data that lives somewhere else."),
    ("p13", "d53", ("sections", 2, "body"),
     "Why not write `[1m]`? Because the right range depends on how far you zoom out. On a 30-minute graph, Grafana asks Prometheus for a point every 15 seconds, and `[1m]` is fine. On a 7-day graph the points are many minutes apart. A one-minute window then looks at one minute out of every ten and misses the spikes in between. The `$__rate_interval` variable grows with the gap between points. Grafana takes the larger of two values:\n- the gap between points plus one scrape interval;",
     "Why not write `[1m]`? A graph panel sends a range query: Prometheus runs the same PromQL once for each point, at evenly spaced times. The gap between points is the step, and Grafana picks it from the time range and the panel's width. On the lab's 30-minute graph the step is 15 seconds, and `[1m]` is fine. On a 7-day graph the points are many minutes apart. A one-minute window then looks at one minute out of every ten and misses the spikes in between. The `$__rate_interval` variable grows with the step. Grafana takes the larger of two values:\n- the step plus one scrape interval;"),

    ("p13", "d53", ("sections", 6, "body"),
     "Every dashboard is a JSON document. Open the dashboard settings,",
     "A dashboard built only by clicking lives in Grafana's own database. Nobody reviews its changes, and if that database is lost, so is the dashboard. Underneath, every dashboard is a JSON document. Open the dashboard settings,"),

    # ---------------- Day 54 ----------------
    ("p13", "d54", ("sections", 0, "body"),
     "Expression C is a threshold: is A above 0.05?",
     "Expression C is a calculation Grafana does itself on A's result, here a threshold: is A above 0.05?"),
    ("p13", "d54", ("sections", 2, "body"),
     "Loki is Grafana Labs' log store, and its main idea comes from Prometheus.",
     "So far you have read logs with `docker compose logs` (Day 21). That works on one machine, while the containers exist. Remove a container and its logs go with it, and with ten servers you would search in ten places.\n\nLoki is Grafana Labs' log store, one place for the logs of every container, and its main idea comes from Prometheus."),
    ("p13", "d54", ("sections", 4, "body"),
     "Something has to read the logs and push them to Loki. In the lab that is Grafana Alloy, Grafana Labs' collector. It is a distribution of the OpenTelemetry Collector with",
     "Something has to read the logs and push them to Loki. Loki does not scrape like Prometheus: a log is a stream of events, with no current value to read, so a collector sends the lines as they appear. In the lab that is Grafana Alloy, Grafana Labs' collector. It is a distribution of the OpenTelemetry Collector (Day 57) with"),
    ("p13", "d54", ("sections", 4, "body"),
     "Alloy talks to Docker through its socket, `/var/run/docker.sock`, mounted into the container.",
     "Alloy talks to Docker through `/var/run/docker.sock`, the socket file the `docker` command also uses to reach the Docker daemon (Day 17). The lab mounts it into the container."),
]


def get(obj, path):
    for p in path[:-1]:
        obj = obj[p]
    return obj, path[-1]


def main():
    data = {k: json.load(open(v)) for k, v in FILES.items()}
    done = skipped = 0
    for part, lid, path, old, new in EDITS:
        lesson = next(L for L in data[part]["lessons"] if L["id"] == lid)
        parent, key = get(lesson, path)
        text = parent[key]
        if new in text:  # already applied (new may contain old, so test new first)
            skipped += 1
            continue
        n = text.count(old)
        if n != 1:
            sys.exit(f"{lid} {path}: old text found {n} times: {old[:60]!r}")
        parent[key] = text.replace(old, new)
        done += 1
    for k, v in FILES.items():
        with open(v, "w") as f:
            json.dump(data[k], f, ensure_ascii=False, indent=1)
            f.write("\n")
    print(f"{done} edits applied, {skipped} already in place")


if __name__ == "__main__":
    main()
