from svg import svg, box, arrow, note
from labfiles import lab

diagram = svg(256, "The operator turns a ServiceMonitor into Prometheus settings; Prometheus scrapes the hello-devops pods, Grafana queries Prometheus, and alerts go to Alertmanager", [
    box(16, 20, 150, 40, "bx", "ServiceMonitor"),
    box(214, 20, 120, 40, "bxp", "Operator"),
    arrow(168, 40, 210, 40),
    arrow(274, 62, 274, 106), note(282, 88, "config", "start"),
    box(16, 110, 136, 48, "bxt", "hello-devops"),
    box(212, 110, 124, 48, "bxo", "Prometheus"),
    box(396, 110, 110, 48, "bxg", "Grafana"),
    arrow(210, 134, 156, 134), note(182, 124, "scrape"),
    arrow(394, 134, 340, 134), note(366, 124, "query"),
    note(84, 176, "/metrics"),
    arrow(274, 160, 274, 196), note(282, 182, "alerts", "start"),
    box(208, 200, 132, 40, "bx", "Alertmanager"),
])

prometheus_yml = """# prometheus.yml: scrape the container named "hello" every 5 seconds.
global:
  scrape_interval: 5s
scrape_configs:
  - job_name: hello
    static_configs:
      - targets: ["hello:8000"]"""

lesson = {
    "id": "d21",
    "title": "Observability: metrics, logs and traces",
    "minutes": 40,
    "goal": "By the end you can install Prometheus and Grafana on kind, scrape hello-devops with a ServiceMonitor, write a basic PromQL query, and explain logs, traces and SLOs.",
    "guess": {
        "q": "How does Prometheus usually get metrics from your app?",
        "options": [
            "Your app sends each number to Prometheus as it happens",
            "Grafana collects the numbers and stores them for Prometheus",
            "Prometheus calls the app's /metrics page every few seconds",
            "Kubernetes saves app metrics in etcd for Prometheus to read",
        ],
        "answer": 2,
        "why": "Prometheus pulls: it scrapes an HTTP page such as /metrics on a schedule. Grafana only draws charts from the data Prometheus stores.",
    },
    "terms": [
        {"term": "Observability", "plain": "How well you can understand what a system is doing inside by looking at what it outputs."},
        {"term": "Metric", "plain": "A number measured over time, such as requests per second or memory in use."},
        {"term": "Scrape", "plain": "Prometheus fetching the current metric values from a target's /metrics page."},
        {"term": "Counter", "plain": "A metric that only goes up (or drops to zero on restart), such as total requests served."},
        {"term": "Trace", "plain": "The path of one request through all the services it touches, made of timed steps called spans."},
        {"term": "SLO", "plain": "Service level objective: a target for how good a service must be, such as 99.9% of requests succeed."},
        {"term": "Error budget", "plain": "The amount of failure an SLO allows, such as 0.1% of requests over 30 days."},
    ],
    "sections": [
        {
            "h": "Monitoring and observability",
            "body": (
                "Monitoring means watching for problems you already know about. Is the pod up? Is the disk full? You set a check and an alert for each one.\n\n"
                "**Observability** goes further. It is how well you can answer new questions about a running system from what it outputs, without shipping new code. "
                "\"Why are requests from one country slow since 14:00?\" is an observability question. Systems output four kinds of signals:\n"
                "- Metrics: numbers over time. Cheap to store, good for graphs and alerts.\n"
                "- Logs: lines of text about single events, such as one failed request.\n"
                "- Traces: the path of one request through many services, with timings.\n"
                "- Profiles: where the code spends CPU and memory. This is the newest signal, and OpenTelemetry support for it is still in an early (alpha) stage.\n\n"
                "Each signal answers a different question. Metrics tell you that something is wrong. Logs and traces help you find where and why."
            ),
            "refs": [
                {"title": "What is OpenTelemetry? (observability basics)", "url": "https://opentelemetry.io/docs/what-is-opentelemetry/", "kind": "docs"},
                {"title": "What is OpenTelemetry? (video from the OpenTelemetry docs)", "url": "https://www.youtube.com/watch?v=iEEIabOha8U", "kind": "watch"},
            ],
        },
        {
            "h": "Metrics with Prometheus",
            "body": (
                "Prometheus is the standard metrics system on Kubernetes. It works by pulling. "
                "Every few seconds it scrapes each target: it calls a page such as `/metrics` and stores the numbers with a timestamp. "
                "Your app already serves this page. Each line is one time series: a name, some labels (key and value pairs), and a value:\n\n"
                "`hello_requests_total{path=\"/\"} 90.0`\n\n"
                "The main metric types are:\n"
                "- Counter: only goes up, like `hello_requests_total`.\n"
                "- Gauge: goes up and down, like memory in use or the length of a queue.\n"
                "- Histogram: counts values in buckets, such as how many requests took under 100 ms. You use it for latency.\n\n"
                "You ask questions with PromQL, the Prometheus query language. A raw counter only grows, so you usually want its speed. "
                "`rate(hello_requests_total[5m])` gives requests per second, averaged over the last 5 minutes. "
                "`sum(rate(hello_requests_total[5m]))` adds up all pods. Grafana runs queries like these and draws the results as dashboards."
            ),
            "refs": [
                {"title": "Prometheus: metric types", "url": "https://prometheus.io/docs/concepts/metric_types/", "kind": "docs"},
                {"title": "Prometheus: querying basics (PromQL)", "url": "https://prometheus.io/docs/prometheus/latest/querying/basics/", "kind": "docs"},
            ],
        },
        {
            "h": "kube-prometheus-stack and the ServiceMonitor",
            "body": (
                "On Kubernetes you rarely install Prometheus by hand. The kube-prometheus-stack Helm chart installs a full set in one go:\n"
                "- Prometheus, to scrape and store metrics.\n"
                "- Grafana, with ready-made dashboards for the cluster.\n"
                "- Alertmanager, to send alerts to email or chat.\n"
                "- The Prometheus Operator, which runs Prometheus and Alertmanager for you.\n"
                "- Exporters that publish metrics about nodes and Kubernetes objects.\n\n"
                "An operator is a controller that runs a piece of software for you, driven by custom resources. "
                "The custom resource you need is the ServiceMonitor. It says: find Services with these labels, then scrape this port and path. "
                "The operator turns it into Prometheus settings.\n\n"
                "This trips most people up. By default, this Prometheus only reads ServiceMonitors that carry the label `release` with the Helm release name. "
                "The lab installs the chart as `monitoring`, so `observability/servicemonitor.yaml` has `release: monitoring`. "
                "Forget the label and nothing fails. Your app just never shows up."
            ),
            "refs": [
                {"title": "kube-prometheus-stack Helm chart", "url": "https://github.com/prometheus-community/helm-charts/tree/main/charts/kube-prometheus-stack", "kind": "docs"},
                {"title": "Prometheus Operator", "url": "https://github.com/prometheus-operator/prometheus-operator", "kind": "docs"},
            ],
        },
        {
            "h": "Logs: write to stdout, ship with an agent",
            "body": (
                "In a container, your app should write logs to standard output (stdout), one event per line. "
                "It should not manage log files itself. Kubernetes keeps each container's output on the node, and `kubectl logs` reads it.\n\n"
                "That works for one pod and a few minutes. It does not work for 30 pods on 3 nodes, or for a pod deleted an hour ago. "
                "So teams add a log pipeline:\n"
                "1. An agent runs on every node, for example Grafana Alloy or Fluent Bit.\n"
                "2. It reads the container logs, adds labels such as namespace and pod, and sends them on.\n"
                "3. A log store keeps them. [Loki](https://grafana.com/docs/loki/latest/get-started/overview/) is a common choice next to Prometheus.\n"
                "4. You search them in Grafana with LogQL, a query language that looks like PromQL.\n\n"
                "Loki indexes only the labels, not the full text, which keeps storage cheap. "
                "Write logs as JSON when you can, so fields such as `status` and `path` are easy to filter."
            ),
            "refs": [
                {"title": "Grafana Loki overview", "url": "https://grafana.com/docs/loki/latest/get-started/overview/", "kind": "docs"},
            ],
        },
        {
            "h": "Traces and OpenTelemetry",
            "body": (
                "A trace follows one request. Say a checkout call goes through an API, a payment service and a database. "
                "The trace shows each step as a span, with its start time and duration. "
                "You see at once that most of the time was spent waiting for the database.\n\n"
                "To get traces, code must create spans and pass a trace ID along with each call. "
                "[OpenTelemetry](https://opentelemetry.io/docs/what-is-opentelemetry/), often called OTel, is the open standard for this. "
                "It is a CNCF project and gives you:\n"
                "- APIs and SDKs for many languages, including Python and Java.\n"
                "- Automatic instrumentation for common libraries, so you write less code.\n"
                "- OTLP, one protocol for traces, metrics and logs.\n"
                "- The Collector, a service that receives telemetry, processes it (for example, batching or filtering) and exports it.\n\n"
                "OpenTelemetry is vendor neutral, and it does not store anything itself. "
                "You send its data to a backend such as Jaeger, Grafana Tempo, Prometheus or a paid service, and you can switch without changing your code."
            ),
            "refs": [
                {"title": "OpenTelemetry: what it is and is not", "url": "https://opentelemetry.io/docs/what-is-opentelemetry/", "kind": "docs"},
                {"title": "OpenTelemetry Collector", "url": "https://opentelemetry.io/docs/collector/", "kind": "docs"},
            ],
        },
        {
            "h": "Golden signals, SLOs and alerts",
            "body": (
                "What should you measure first? [Google's SRE book](https://sre.google/sre-book/monitoring-distributed-systems/) names four golden signals:\n"
                "- Latency: how long requests take.\n"
                "- Traffic: how many requests arrive.\n"
                "- Errors: how many requests fail.\n"
                "- Saturation: how full the system is, such as CPU or memory.\n\n"
                "For a single service, the [RED method](https://grafana.com/blog/the-red-method-how-to-instrument-your-services/) keeps the three that users feel: rate, errors and duration.\n\n"
                "Next, decide what good means. An SLI (service level indicator) is a measurement, such as the share of requests that succeed. "
                "An SLO is the target for it, such as 99.9% over 30 days. The rest is the error budget: "
                "a 99.9% target allows about 43 minutes of full downtime in 30 days. While budget remains, ship at normal speed. When it runs out, fix reliability first.\n\n"
                "Alert on symptoms users feel, such as many errors or slow responses. High CPU alone should not wake anyone up. "
                "After an incident, the team writes a blameless postmortem: what happened and how to prevent it, without blaming a person."
            ),
            "refs": [
                {"title": "Google SRE book: Monitoring distributed systems", "url": "https://sre.google/sre-book/monitoring-distributed-systems/", "kind": "read"},
                {"title": "Google SRE book: Service level objectives", "url": "https://sre.google/sre-book/service-level-objectives/", "kind": "read"},
                {"title": "Google SRE book: Postmortem culture", "url": "https://sre.google/sre-book/postmortem-culture/", "kind": "read"},
            ],
        },
    ],
    "analogy": (
        "A car gives you three views of a drive. The gauges on the dashboard are metrics: speed and fuel, always on and quick to read. "
        "The trip log is like logs: one line for each stop. A GPS replay of one drive is a trace: every turn, and how long each part took. "
        "Where it breaks: a car has one driver, while your app serves thousands of requests at once, so you must choose what to record and how long to keep it."
    ),
    "diagram": diagram,
    "diagram_caption": "Prometheus pulls metrics; a ServiceMonitor tells it where to look.",
    "worked": {
        "title": "Query a counter with PromQL, no cluster needed",
        "steps": [
            {
                "say": "You can see the whole pull model with two containers. Start the app with a single gunicorn worker. With two workers, each keeps its own counter, and Go deeper explains why that confuses Prometheus.",
                "code": "$ docker network create obs\n$ docker run -d --name hello --network obs -p 8000:8000 hello-devops:1.0.0 \\\n    gunicorn --bind 0.0.0.0:8000 --workers 1 app:app",
                "lang": "console",
            },
            {
                "say": "Tell Prometheus what to scrape. Save this as `prometheus.yml` in an empty folder. On Kubernetes, a ServiceMonitor generates settings like these for you.",
                "code": prometheus_yml,
                "lang": "yaml",
            },
            {
                "say": "Run Prometheus from Docker Hub with your file mounted. It finds the app by its container name, thanks to the shared network (Day 7).",
                "code": "$ docker run -d --name prom --network obs -p 9090:9090 \\\n    -v \"$PWD/prometheus.yml:/etc/prometheus/prometheus.yml\" prom/prometheus",
                "lang": "console",
            },
            {
                "say": "Send 60 requests, one per second, so there is something to measure.",
                "code": "$ for i in $(seq 1 60); do curl -s localhost:8000/ > /dev/null; sleep 1; done",
                "lang": "console",
            },
            {
                "say": "Ask for the raw counter through the HTTP API. The web UI at http://localhost:9090 shows the same. I had sent 30 requests earlier, so mine says 90. Prometheus added the `job` and `instance` labels.",
                "code": "$ curl -s localhost:9090/api/v1/query --data-urlencode 'query=hello_requests_total'\n{\"status\":\"success\",\"data\":{\"resultType\":\"vector\",\"result\":[{\"metric\":{\"__name__\":\"hello_requests_total\",\"instance\":\"hello:8000\",\"job\":\"hello\",\"path\":\"/\"},\"value\":[1793331673.198,\"90\"]}]}}",
                "lang": "console",
            },
            {
                "say": "Now ask for the speed. `rate(...[1m])` is the increase per second over the last minute: about 1, because you sent one request per second.",
                "code": "$ curl -s localhost:9090/api/v1/query --data-urlencode 'query=rate(hello_requests_total[1m])'\n{\"status\":\"success\",\"data\":{\"resultType\":\"vector\",\"result\":[{\"metric\":{\"instance\":\"hello:8000\",\"job\":\"hello\",\"path\":\"/\"},\"value\":[1793331673.187,\"1.0000000000000002\"]}]}}",
                "lang": "console",
            },
            {
                "say": "Clean up both containers and the network.",
                "code": "$ docker rm -f hello prom\n$ docker network rm obs",
                "lang": "console",
            },
        ],
    },
    "code": [
        {
            "lang": "yaml",
            "title": "observability/values.yaml",
            "src": lab("observability/values.yaml"),
            "run": "helm install monitoring oci://ghcr.io/prometheus-community/charts/kube-prometheus-stack --namespace monitoring --create-namespace -f observability/values.yaml",
        },
        {
            "lang": "yaml",
            "title": "observability/servicemonitor.yaml",
            "src": lab("observability/servicemonitor.yaml"),
            "run": "kubectl apply -f observability/servicemonitor.yaml",
        },
    ],
    "commands": [
        {"cmd": "helm install monitoring oci://ghcr.io/prometheus-community/charts/kube-prometheus-stack --namespace monitoring --create-namespace -f observability/values.yaml",
         "what": "Install Prometheus, Grafana, Alertmanager and the operator as one Helm release named monitoring."},
        {"cmd": "kubectl -n monitoring get pods", "what": "Wait until every monitoring pod is Running."},
        {"cmd": "kubectl apply -f observability/servicemonitor.yaml", "what": "Tell Prometheus to scrape hello-devops."},
        {"cmd": "kubectl -n hello get servicemonitors", "what": "List the ServiceMonitors in the app's namespace."},
        {"cmd": "kubectl -n hello get svc --show-labels", "what": "Show the Services and their labels, to compare with a ServiceMonitor selector."},
        {"cmd": "kubectl -n monitoring port-forward svc/monitoring-kube-prometheus-prometheus 9090:9090",
         "what": "Open Prometheus at http://localhost:9090. Its Status menu lists every target and whether it is up."},
        {"cmd": "kubectl -n monitoring port-forward svc/monitoring-grafana 3000:80", "what": "Open Grafana at http://localhost:3000."},
        {"cmd": "kubectl -n monitoring get secret monitoring-grafana -o jsonpath=\"{.data.admin-password}\" | base64 -d",
         "what": "Print the generated Grafana password. The user name is admin."},
        {"cmd": "curl -s localhost:9090/api/v1/query --data-urlencode 'query=sum(rate(hello_requests_total[5m]))'",
         "what": "Run a PromQL query from the terminal: total requests per second over 5 minutes."},
        {"cmd": "kubectl -n hello logs deploy/hello-devops --tail=20", "what": "Show the last 20 log lines of one hello-devops pod."},
        {"cmd": "helm uninstall monitoring -n monitoring", "what": "Remove the stack. Its custom resource definitions stay; the chart README shows how to delete them."},
    ],
    "mistake": (
        "Creating a ServiceMonitor without the `release: monitoring` label, or with a selector that matches no Service. "
        "Nothing errors, and your app simply never appears in Prometheus. "
        "Check the target list in Prometheus first, then compare labels with `kubectl -n hello get svc --show-labels`."
    ),
    "real_world": (
        "A payments team might set an SLO such as 99.95% of card payments succeed within 2 seconds, and page someone only when the error budget burns too fast. "
        "Every service shows the same RED dashboard, so anyone on call can read any service. "
        "Traces from OpenTelemetry show which call to a partner bank made a slow payment slow."
    ),
    "task": {
        "title": "Watch hello-devops in Grafana",
        "steps": [
            "Make sure your kind cluster runs and hello-devops is deployed, by Argo CD (Day 20) or with kubectl.",
            "Add `observability/values.yaml` to your repo and install kube-prometheus-stack with Helm as the release `monitoring`.",
            "Check that `k8s/service.yaml` has the label `app: hello-devops` and a port named `http`, then apply `observability/servicemonitor.yaml`.",
            "Port-forward Prometheus and confirm that three hello-devops targets are up.",
            "Port-forward Grafana, read the admin password from its Secret, and log in.",
            "In Grafana, open Explore, choose the Prometheus data source, and run `sum(rate(hello_requests_total[5m]))`.",
            "Send traffic with a curl loop against http://localhost:8081 and watch the line rise. Save the query as a panel on a new dashboard.",
        ],
        "hints": [
            "No target? The labels do not match. Compare the ServiceMonitor with `kubectl -n hello get svc --show-labels`, and check its `release` label.",
            "rate() needs at least two scrapes inside its window. Wait a minute after the first traffic.",
            "If pods stay Pending, Docker Desktop is short of memory. Give it more under Settings, then Resources.",
        ],
        "done_when": "Your Grafana panel shows `sum(rate(hello_requests_total[5m]))` rising while your curl loop runs.",
    },
    "explain_back": {
        "prompt": "Explain to a teammate how hello-devops metrics end up in a Grafana chart, in 3 to 4 sentences. Mention scrape, ServiceMonitor and PromQL.",
        "answer": (
            "The app serves its counters on /metrics. Prometheus scrapes that page every 15 seconds and stores each value with a timestamp. "
            "It knows where to look because the Prometheus Operator turns our ServiceMonitor, which matches the hello-devops Service by label, into scrape settings. "
            "Grafana then runs a PromQL query such as sum(rate(hello_requests_total[5m])) and draws the result."
        ),
    },
    "recap": [
        "Monitoring watches for known problems; observability lets you ask new questions from a system's outputs.",
        "Metrics, logs and traces each answer a different question; profiles are a newer fourth signal.",
        "Prometheus pulls: it scrapes /metrics on a schedule and stores time series with labels.",
        "Use rate() on counters to get per-second speed, and let Grafana draw PromQL results.",
        "A ServiceMonitor tells the Prometheus Operator what to scrape, and it needs the release label.",
        "Set SLOs on what users feel, alert on symptoms, and learn from incidents with blameless postmortems.",
    ],
    "check": [
        {
            "q": "You want a graph of how many requests per second hello-devops serves. Which query fits?",
            "options": [
                "hello_requests_total",
                "rate(hello_requests_total[5m])",
                "max(hello_requests_total)",
                "count(hello_requests_total)",
            ],
            "answer": 1,
            "why": "A counter only grows; rate() turns it into speed per second over the window.",
        },
        {
            "q": "Your new ServiceMonitor applies without errors, but Prometheus shows no hello-devops target. What do you check first?",
            "options": [
                "Whether Grafana has the right data source",
                "Whether the app writes its logs to stdout",
                "Whether the pods have enough CPU requests",
                "Whether its labels and selector match the release and the Service",
            ],
            "answer": 3,
            "why": "Prometheus only reads ServiceMonitors with the release label, and the selector must match the Service's labels. A mismatch fails silently.",
        },
        {
            "q": "Your SLO is 99.9% of requests succeed over 30 days. Halfway through the month, 0.08% of requests have failed. What does this tell you?",
            "options": [
                "Most of the error budget is gone, so slow down risky changes",
                "The SLO is met, so you can stop measuring for now",
                "The error budget is still untouched",
                "You should alert on CPU instead of errors",
            ],
            "answer": 0,
            "why": "The budget is 0.1%, and 0.08% is already used with half the month left, so reliability work comes first.",
        },
    ],
    "interview": [
        {
            "q": "What is the difference between monitoring and observability?",
            "a": (
                "Monitoring watches for known failures with checks and alerts, such as a pod being down or a disk filling up. "
                "Observability is how well you can understand a system's inner state from its outputs, including questions you did not plan for. "
                "In practice you get it from good metrics, structured logs and traces that share labels and IDs. "
                "Monitoring tells you that something is wrong; observability helps you find out why."
            ),
        },
        {
            "q": "What are SLOs and error budgets, and how do they change how a team works?",
            "a": (
                "An SLI measures service quality, like the share of successful requests, and an SLO is the target for it over a time window, like 99.9% over 30 days. "
                "The error budget is what the SLO allows to fail, here 0.1%. "
                "While the budget lasts, the team ships features at normal speed; when it is spent, effort moves to reliability. "
                "Alerts then fire on fast budget burn instead of on raw CPU or memory."
            ),
        },
    ],
    "deeper": {
        "minutes": 12,
        "body": (
            "Our image runs gunicorn with two worker processes. Each worker is a separate Python process with its own copy of `hello_requests_total`. "
            "When Prometheus scrapes `/metrics`, gunicorn hands the request to one worker, and you only see that worker's number. "
            "Try it: send 6 requests, then fetch `/metrics` a few times. I saw 5, then 1, then 5 again.\n\n"
            "Prometheus sees a counter that went down and treats it as a restart. `rate()` then counts the jumps as new requests, so the speed looks higher than it is. "
            "That is why the worked example ran one worker. Real apps fix this in one of two ways:\n"
            "- Run one worker per container and add more pods. Kubernetes already handles scaling.\n"
            "- Use the multiprocess mode of the Python client. Each worker writes to a shared folder set by `PROMETHEUS_MULTIPROC_DIR`, and `/metrics` adds them up.\n\n"
            "Now latency. A counter tells you how many, not how fast. For speed, use a histogram. "
            "It counts requests into buckets: under 0.1 seconds, under 0.25 seconds, and so on. "
            "In Python you would add `Histogram(\"hello_request_seconds\", \"Request time\")` and time the handler with it. PromQL can then estimate a percentile:\n\n"
            "`histogram_quantile(0.95, sum by (le) (rate(hello_request_seconds_bucket[5m])))`\n\n"
            "This reads: the time within which 95% of requests finished, over the last 5 minutes. Percentiles beat averages. "
            "If 99 requests take 10 ms and one takes 5 seconds, the average looks fine, but one user waited 5 seconds.\n\n"
            "Last, alerts. An alerting rule is a PromQL expression plus a duration. "
            "For example: fire when more than 5% of requests fail for 10 minutes. "
            "kube-prometheus-stack reads rules from PrometheusRule objects, found by the same `release` label as ServiceMonitors. "
            "Alertmanager then groups the alerts and sends them to chat, email or a paging tool."
        ),
    },
    "sources": [
        {"title": "Prometheus: metric types", "url": "https://prometheus.io/docs/concepts/metric_types/"},
        {"title": "kube-prometheus-stack Helm chart", "url": "https://github.com/prometheus-community/helm-charts/tree/main/charts/kube-prometheus-stack"},
        {"title": "What is OpenTelemetry?", "url": "https://opentelemetry.io/docs/what-is-opentelemetry/"},
        {"title": "Google SRE book: Monitoring distributed systems", "url": "https://sre.google/sre-book/monitoring-distributed-systems/"},
    ],
}
