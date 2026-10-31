from common import lab, ref, src

DIAGRAM = (
    '<svg viewBox="0 0 560 300" xmlns="http://www.w3.org/2000/svg" role="img" '
    'aria-label="An alerting rule goes from pending to firing in Prometheus, then Alertmanager groups it, checks '
    'inhibition and silences, and routes it to the pager or tickets receiver">'
    '<rect class="bxo" x="16" y="20" width="150" height="40" rx="10"/>'
    '<text class="tk" x="91" y="45" font-size="13" text-anchor="middle">Rule: expr</text>'
    '<line class="ln" x1="168" y1="40" x2="202" y2="40" marker-end="url(#ar)"/>'
    '<rect class="bx" x="206" y="20" width="148" height="40" rx="10"/>'
    '<text class="t" x="280" y="45" font-size="13" text-anchor="middle">Pending</text>'
    '<text class="ts" x="280" y="78" font-size="11" text-anchor="middle">waits out for: 2m</text>'
    '<line class="ln" x1="356" y1="40" x2="390" y2="40" marker-end="url(#ar)"/>'
    '<rect class="bxo" x="394" y="20" width="150" height="40" rx="10"/>'
    '<text class="tk" x="469" y="45" font-size="13" text-anchor="middle">Firing</text>'
    '<text class="ts" x="469" y="78" font-size="11" text-anchor="middle">sent to Alertmanager</text>'
    '<line class="ln" x1="469" y1="86" x2="469" y2="120" marker-end="url(#ar)"/>'
    '<rect class="bxp" x="350" y="124" width="194" height="40" rx="10"/>'
    '<text class="tk" x="447" y="149" font-size="13" text-anchor="middle">Group by alertname</text>'
    '<line class="ln" x1="348" y1="144" x2="314" y2="144" marker-end="url(#ar)"/>'
    '<rect class="bxp" x="120" y="124" width="190" height="40" rx="10"/>'
    '<text class="tk" x="215" y="149" font-size="13" text-anchor="middle">Inhibit? Silenced?</text>'
    '<line class="ln" x1="215" y1="166" x2="215" y2="196" marker-end="url(#ar)"/>'
    '<rect class="bxp" x="120" y="200" width="190" height="40" rx="10"/>'
    '<text class="tk" x="215" y="225" font-size="13" text-anchor="middle">Route by severity</text>'
    '<line class="ln" x1="312" y1="212" x2="378" y2="196" marker-end="url(#ar)"/>'
    '<line class="ln" x1="312" y1="228" x2="378" y2="252" marker-end="url(#ar)"/>'
    '<rect class="bxt" x="382" y="176" width="162" height="36" rx="10"/>'
    '<text class="tk" x="463" y="199" font-size="13" text-anchor="middle">pager</text>'
    '<rect class="bxt" x="382" y="236" width="162" height="36" rx="10"/>'
    '<text class="tk" x="463" y="259" font-size="13" text-anchor="middle">tickets</text>'
    '<text class="ts" x="215" y="262" font-size="11" text-anchor="middle">severity=page goes to pager</text>'
    "</svg>"
)

LESSON = {
    "id": "d44",
    "title": "Alerting and Prometheus on Kubernetes",
    "minutes": 50,
    "goal": "By the end you can write and unit-test alerting rules, route alerts through Alertmanager to a receiver, read how an app records a histogram, and monitor hello-devops on Kubernetes with a ServiceMonitor and a PrometheusRule.",
    "guess": {
        "q": "An alerting rule has for: 10m. Its condition is true for 8 minutes, false for one evaluation, then true again. When does it fire?",
        "options": [
            "At the 10-minute mark, counted from the first time it became true",
            "Right away, because it was already true for 8 minutes",
            "Never, because one false evaluation cancels the rule",
            "10 minutes after the condition became true again",
        ],
        "answer": 3,
        "why": "One false evaluation sends the alert back to inactive. The pending wait starts again from zero, which is what makes for: a filter against flapping.",
    },
    "terms": [
        {"term": "Alerting rule", "plain": "A PromQL condition with a name; every series it returns becomes an alert."},
        {"term": "Pending", "plain": "An alert whose condition is true but has not yet lasted its for: time."},
        {"term": "Alertmanager", "plain": "A separate service that groups, mutes and routes alerts from Prometheus to people."},
        {"term": "Receiver", "plain": "Where Alertmanager sends notifications: a webhook, Slack, PagerDuty, email and others."},
        {"term": "Inhibition", "plain": "A rule that mutes some alerts while another alert is firing."},
        {"term": "Silence", "plain": "A temporary mute for matching alerts, created at run time for example during maintenance."},
        {"term": "Prometheus Operator", "plain": "A Kubernetes controller that runs Prometheus and Alertmanager from custom resources."},
        {"term": "ServiceMonitor", "plain": "A custom resource that tells the Operator which Services to scrape, on which port and path."},
    ],
    "sections": [
        {
            "h": "Alerting rules: expr, for, labels, annotations",
            "body": (
                "An **alerting rule** is a PromQL query with a name. Prometheus runs it every evaluation interval (15 seconds in the lab), "
                "and every series the query returns is one active alert. Here is `HelloDown` from `alerts.yml`:\n"
                "- `expr: up{job=\"hello-devops\"} == 0` is the condition. The comparison filters, so the query returns something only when a scrape fails.\n"
                "- `for: 1m` means the condition must stay true for a whole minute. Until then the alert is pending.\n"
                "- `labels: severity: page` is added to the alert. Alertmanager routes on it.\n"
                "- `annotations` hold text for humans. `{{ $labels.instance }}` and `{{ $value }}` fill in the details.\n\n"
                "An alert moves through three states: inactive, pending, firing. "
                "If the condition is false for even one evaluation, the alert goes back to inactive and the wait starts again. "
                "So `for:` filters out blips such as one slow scrape during a deploy. "
                "Prometheus also writes every active alert as a series named `ALERTS`, so `ALERTS{alertstate=\"pending\"}` is a normal query.\n\n"
                "The two SLO alerts turn the Day 41 plan into rules. They compare the Day 43 recording rules with the burn-rate lines:\n"
                "- Page: 14.4 times the budget over 1 hour and 5 minutes, or 6 times over 6 hours and 30 minutes.\n"
                "- Ticket: 1 times the budget over 3 days and 6 hours.\n\n"
                "Prometheus only decides that an alert fires. It sends firing alerts to the Alertmanager listed under `alerting:` in `prometheus.yml`, and it does not send any message itself."
            ),
            "refs": [ref("alerting_rules"), ref("alerting_tutorial")],
        },
        {
            "h": "Alertmanager: routes, groups, inhibition and silences",
            "body": (
                "Alertmanager is a separate service. Its job is to turn a stream of alerts into a few useful messages. "
                "It does four things:\n"
                "- Grouping: alerts with the same `group_by` labels become one notification. Fifty pods failing at once give one message, not fifty.\n"
                "- Routing: each group walks down a tree of routes, matched on labels, to a receiver. In the lab, `severity=\"page\"` goes to `pager` and everything else to `tickets`.\n"
                "- Inhibition: while one alert fires, it mutes others. The lab mutes ticket alerts for a job while a page fires for the same job.\n"
                "- Silences: temporary mutes you create at run time, in the UI on port 9093 or with `amtool`. They are not in the config file.\n\n"
                "Three timers control the pace, and the lab shortens all of them:\n"
                "- `group_wait` (default 30s): wait for more alerts before the first message of a new group.\n"
                "- `group_interval` (default 5m): wait before telling you about changes to a group already sent.\n"
                "- `repeat_interval` (default 4h): resend an alert that is still firing.\n\n"
                "A receiver is the destination. Alertmanager has built-in support for Slack, PagerDuty, email, Microsoft Teams and more, plus a generic webhook. "
                "The lab's `webhook.py` is a 30-line Python server that prints what it receives, so you can see exactly what Slack would get. "
                "With `send_resolved: true`, Alertmanager also sends a message when the alert stops."
            ),
            "refs": [ref("am_overview"), ref("am_config")],
        },
        {
            "h": "Test alerts before they page anyone",
            "body": (
                "An alert you never saw fire is a guess. `promtool test rules` lets you prove a rule does what you think, without waiting for a real outage. "
                "A test file lists:\n"
                "1. The rule files to load.\n"
                "2. Made-up input series. `0+300x90` means start at 0 and add 300 every interval, 90 times.\n"
                "3. A time to check, and the exact alerts expected then, with labels and annotations.\n\n"
                "The lab's `tests/alerts_test.yml` checks three stories:\n"
                "- The app is down for two minutes, and `HelloDown` fires.\n"
                "- Errors start at minute 61, and the fast burn pages by minute 75.\n"
                "- A slow leak of 0.33% errors opens a ticket but does not page.\n\n"
                "When I first wrote the second test I guessed the summary would say 4.115%. "
                "The promtool output showed the expected and the actual alert side by side, with `4.762%`, and the fix took ten seconds.\n\n"
                "Test the routing tree too: `amtool config routes test severity=page alertname=HelloDown` prints `pager`.\n\n"
                "Before you merge a new alert, ask these questions:\n"
                "- Does it fire on a symptom users feel?\n"
                "- Does it have a `for:` long enough to skip blips?\n"
                "- Does it use `rate()`, never `irate()`, so one quiet scrape does not reset it?\n"
                "- Does the annotation say what is wrong, and link to a runbook?\n"
                "- Would the person paged know what to do next?"
            ),
            "refs": [ref("unit_tests"), ref("rp_irate"), ref("v_pitfalls")],
        },
        {
            "h": "Instrumenting an app: counters and histograms in code",
            "body": (
                "Instrumenting means adding metrics to your own code with a client library. "
                "Python's is `prometheus_client`; the JVM has Micrometer, which Spring Boot's Actuator uses to record every request as `http.server.requests` and serve it at `/actuator/prometheus`.\n\n"
                "hello-devops started with one line: `Counter(\"hello_requests_total\", ...)` and `.labels(path=\"/\").inc()` in the handler. "
                "It counts visits, but it cannot see status codes or time. "
                "The lab adds both in `observability/red_metrics.py`, without touching `app.py`:\n"
                "1. It imports the Flask app and registers two hooks: one runs before every request and notes the start time, one runs after it.\n"
                "2. The after-hook increments `hello_responses_total` with the route and status code.\n"
                "3. It calls `observe()` on the histogram `hello_request_duration_seconds` with the elapsed seconds. No buckets are given, so the client's defaults apply: 5 ms up to 10 s.\n"
                "4. It uses Flask's route pattern as the `path` label, so a scan of random URLs adds only one `unmatched` value.\n\n"
                "Both metrics land in the client's default registry, which the app's existing `/metrics` route already prints. "
                "Compose mounts the file into the container and starts gunicorn with `red_metrics:app`.\n\n"
                "Two choices matter more than the code. "
                "First, buckets: put limits near the latencies you care about, such as your SLO threshold, because Day 43 showed that `histogram_quantile` can only be as precise as the buckets. "
                "Second, the process model: one process per container, with threads, so every scrape sees every request (Day 42)."
            ),
            "refs": [ref("client_python"), ref("client_hist"), ref("instrumentation")],
        },
        {
            "h": "Prometheus on Kubernetes: the Operator and kube-prometheus-stack",
            "body": (
                "On Kubernetes you rarely write `prometheus.yml` by hand. The usual install is the kube-prometheus-stack Helm chart (Day 37 covered Helm). "
                "With the lab's `values.yaml`, version 92.16.0 rendered 109 objects. The main parts:\n"
                "- The Prometheus Operator, a controller that runs Prometheus and Alertmanager for you.\n"
                "- Prometheus and Alertmanager, described as custom resources and run as StatefulSets.\n"
                "- Grafana with ready-made dashboards for the cluster (Part 10).\n"
                "- node_exporter as a DaemonSet, one pod per node.\n"
                "- kube-state-metrics, which turns Kubernetes objects into metrics.\n"
                "- 134 ready-made alerting rules, such as `KubePodCrashLooping`.\n\n"
                "The Operator adds custom resources (Day 30 showed how controllers work):\n"
                "- `ServiceMonitor` and `PodMonitor`: what to scrape, found by labels.\n"
                "- `PrometheusRule`: recording and alerting rules.\n"
                "- `Probe` and `ScrapeConfig`: black-box checks and targets outside the cluster.\n"
                "- `AlertmanagerConfig`: routes and receivers, per namespace.\n\n"
                "Two defaults surprise people. One alert, `Watchdog`, always fires on purpose: if it ever stops arriving, your alerting pipeline is broken. "
                "And the chart's default Alertmanager config sends everything to a receiver named `null`, so nobody is notified until you add a real receiver."
            ),
            "refs": [ref("kps_chart"), ref("operator"), ref("v_k8s_operator")],
        },
        {
            "h": "ServiceMonitors, PrometheusRules and the release label",
            "body": (
                "`observability/servicemonitor.yaml` says: in namespace `hello`, find Services labelled `app: hello-devops`, and scrape their port named `http` at `/metrics` every 15 seconds. "
                "The Operator turns that into scrape settings. "
                "Prometheus then scrapes each pod behind the Service directly, one target per pod. In Target health they appear under `serviceMonitor/hello/hello-devops/0`.\n\n"
                "The labels are richer than in Compose. `job` becomes the Service name, `hello-devops`, and the Operator adds `namespace`, `pod` and `service`. "
                "So the same PromQL works in both places, and `sum by (pod)` splits by pod.\n\n"
                "This is the gotcha. The chart's Prometheus only reads ServiceMonitors, PodMonitors and PrometheusRules that carry the label `release` with the Helm release name. "
                "The lab installs the release as `monitoring`, so both files have `release: monitoring`. "
                "Leave it out and nothing fails: no error, no event, and your app never shows up. "
                "If a target is missing, check in this order:\n"
                "1. The `release` label on the ServiceMonitor.\n"
                "2. Its selector against `kubectl -n hello get svc --show-labels`.\n"
                "3. The port name: it must match a named port on the Service.\n\n"
                "The pods in Kubernetes run the image's own command: two gunicorn workers and no `red_metrics.py`. "
                "So `prometheusrule.yaml` alerts only on `up`, which the worker problem from Day 42 cannot confuse. "
                "`HelloNoPodsUp` uses `absent()`, because a deleted pod leaves the target list instead of reporting `up = 0`."
            ),
            "refs": [ref("operator_gs"), ref("operator_trouble")],
        },
        {
            "h": "State metrics, autoscaling metrics and long-term storage",
            "body": (
                "Two components sound alike and do different jobs:\n"
                "- [kube-state-metrics](https://github.com/kubernetes/kube-state-metrics) reads the Kubernetes API and exposes the state of objects as metrics: desired and available replicas, pod restarts, job results. Prometheus scrapes it.\n"
                "- [metrics-server](https://github.com/kubernetes-sigs/metrics-server) collects current CPU and memory from each kubelet for `kubectl top` and the autoscaler from Day 35. Its README says it is meant only for autoscaling, not as a source for monitoring.\n\n"
                "Then there is time. One Prometheus keeps its data on local disk, 15 days by default, and the docs say that storage is not clustered or replicated. "
                "Teams that need months of history, high availability or one view across many clusters add a second layer:\n"
                "- `remote_write` streams every sample to another system as it arrives.\n"
                "- [Thanos](https://github.com/thanos-io/thanos) runs next to existing Prometheus servers and keeps their blocks in object storage, such as S3.\n"
                "- [Grafana Mimir](https://github.com/grafana/mimir) receives remote write into a scalable, multi-tenant store, also backed by object storage.\n"
                "- Hosted services, such as Grafana Cloud, accept remote write too.\n\n"
                "For one laptop cluster, 15 days of local data is plenty. "
                "The question to ask at work is how far back an incident review needs to look, and whether losing one Prometheus disk would hurt."
            ),
            "refs": [ref("ksm"), ref("thanos"), ref("mimir")],
        },
    ],
    "analogy": (
        "Prometheus is a smoke detector and Alertmanager is the building's alarm desk. "
        "A detector only decides that there is smoke, and only after it lasts a few seconds (for:). "
        "The desk turns ten detectors on one floor into one call (grouping). "
        "It sends a fire to the fire brigade and a faulty sensor to the caretaker (routing). "
        "It ignores floor alarms while the whole building is already evacuating (inhibition), and stays quiet during a planned fire drill (a silence). "
        "Where it breaks: a real alarm desk is staffed by people, while Alertmanager follows its rules exactly, so a wrong route sends the page nowhere."
    ),
    "diagram": DIAGRAM,
    "diagram_caption": "Prometheus decides that an alert fires; Alertmanager decides who hears about it.",
    "worked": {
        "title": "One outage, from rule to receiver",
        "steps": [
            {
                "say": (
                    "Test first. The promtool command runs the three stories in the test file, and amtool shows the routing tree. "
                    "The `am` function runs amtool inside the Alertmanager container, as `q` does for promtool."
                ),
                "code": "$ docker compose exec prometheus promtool test rules /etc/prometheus/tests/alerts_test.yml\n  SUCCESS\n\n"
                "$ am() { docker compose exec alertmanager amtool --alertmanager.url=http://localhost:9093 \"$@\"; }\n"
                "$ am config routes\nRouting tree:\n.\n└── default-route  receiver: tickets\n    └── {severity=\"page\"}  receiver: pager",
                "lang": "console",
            },
            {
                "say": "Start Alertmanager and the webhook, reload Prometheus so it reads `alerts.yml`, and follow the webhook's output in a second terminal.",
                "code": "$ docker compose up -d alertmanager webhook\n$ curl -X POST localhost:9090/-/reload\n$ docker compose logs -f webhook\nwebhook-1  | webhook: waiting for alerts on port 5001",
                "lang": "console",
            },
            {
                "say": (
                    "Break it the same way as on Day 43 and give it 40 seconds. Both SLO alerts are pending: the condition is true, but `for: 2m` has not passed yet."
                ),
                "code": "$ docker compose stop redis\n$ q 'ALERTS'\n"
                "ALERTS{alertname=\"HelloErrorBudgetFastBurn\", alertstate=\"pending\", job=\"hello-devops\", severity=\"page\"} => 1 @[1793338015.042]\n"
                "ALERTS{alertname=\"HelloErrorBudgetSlowBurn\", alertstate=\"pending\", job=\"hello-devops\", severity=\"ticket\"} => 1 @[1793338015.042]",
                "lang": "console",
            },
            {
                "say": (
                    "Two minutes later both fire, and 10 seconds after that (`group_wait`) the webhook prints one line. "
                    "Only the page arrived: the inhibition rule muted the ticket for the same job."
                ),
                "code": "webhook-1  | [pager] FIRING HelloErrorBudgetFastBurn job=hello-devops severity=page: 4.52% of hello-devops requests fail (fast burn)\n\n"
                "$ am alert query\nAlertname                 Starts At                Summary                                          State\n"
                "HelloErrorBudgetFastBurn  2026-10-30 05:28:09 UTC  4.52% of hello-devops requests fail (fast burn)  active\n"
                "$ am alert query -i\nAlertname                 Starts At                Summary                                          State\n"
                "HelloErrorBudgetSlowBurn  2026-10-30 05:28:09 UTC  4.52% of hello-devops requests fail (slow burn)  suppressed",
                "lang": "console",
            },
            {
                "say": (
                    "You are working on it, so silence the page for an hour. A silence matches labels, has an author and a comment, and lives in Alertmanager, not in any file."
                ),
                "code": "$ am silence add alertname=HelloErrorBudgetFastBurn --duration=1h --comment=\"Redis maintenance\" --author=you\n771e388c-c97a-47c8-9f49-94888cc73862\n"
                "$ am silence query\nID                                    Matchers                              Ends At                  Created By  Comment\n"
                "771e388c-c97a-47c8-9f49-94888cc73862  alertname=\"HelloErrorBudgetFastBurn\"  2026-10-30 06:28:45 UTC  you         Redis maintenance",
                "lang": "console",
            },
            {
                "say": "Fix the cause, then remove the silence so you will hear when the alert resolves.",
                "code": "$ docker compose start redis\n$ am silence expire 771e388c-c97a-47c8-9f49-94888cc73862",
                "lang": "console",
            },
            {
                "say": (
                    "Now wait. Four minutes after the fix, the 5-minute ratio was already low, but the 30-minute ratio still held the outage, so the 6-hour tier kept the page firing. "
                    "About 25 minutes after the fix the page resolved, and in the same second Alertmanager released the ticket it had been muting: the outage really did spend budget."
                ),
                "code": "$ q 'job:hello_responses_errors:ratio_rate5m'\n"
                "job:hello_responses_errors:ratio_rate5m{job=\"hello-devops\"} => 0.004987531172069825 @[1793338404.476]\n"
                "$ q 'job:hello_responses_errors:ratio_rate30m'\n"
                "job:hello_responses_errors:ratio_rate30m{job=\"hello-devops\"} => 0.02371434392731684 @[1793338404.684]\n\n"
                "webhook-1  | [pager] RESOLVED HelloErrorBudgetFastBurn job=hello-devops severity=page: 0.6003% of hello-devops requests fail (fast burn)\n"
                "webhook-1  | [tickets] FIRING HelloErrorBudgetSlowBurn job=hello-devops severity=ticket: 0.6171% of hello-devops requests fail (slow burn)",
                "lang": "console",
            },
        ],
    },
    "code": [
        {
            "lang": "yaml",
            "title": "observability/prometheus/rules/alerts.yml",
            "src": lab("observability/prometheus/rules/alerts.yml"),
            "run": "docker compose exec prometheus promtool check rules /etc/prometheus/rules/alerts.yml && curl -X POST localhost:9090/-/reload",
        },
        {
            "lang": "yaml",
            "title": "observability/prometheus/tests/alerts_test.yml",
            "src": lab("observability/prometheus/tests/alerts_test.yml"),
            "run": "docker compose exec prometheus promtool test rules /etc/prometheus/tests/alerts_test.yml",
        },
        {
            "lang": "yaml",
            "title": "observability/alertmanager/alertmanager.yml",
            "src": lab("observability/alertmanager/alertmanager.yml"),
            "run": "docker compose exec alertmanager amtool check-config /etc/alertmanager/alertmanager.yml",
        },
        {
            "lang": "python",
            "title": "observability/webhook.py",
            "src": lab("observability/webhook.py"),
            "run": "docker compose up -d alertmanager webhook && docker compose logs -f webhook",
        },
        {
            "lang": "yaml",
            "title": "observability/values.yaml",
            "src": lab("observability/values.yaml"),
            "run": "helm install monitoring oci://ghcr.io/prometheus-community/charts/kube-prometheus-stack --version 92.16.0 --namespace monitoring --create-namespace -f observability/values.yaml",
        },
        {
            "lang": "yaml",
            "title": "observability/servicemonitor.yaml",
            "src": lab("observability/servicemonitor.yaml"),
            "run": "kubectl apply -f observability/servicemonitor.yaml",
        },
        {
            "lang": "yaml",
            "title": "observability/prometheusrule.yaml",
            "src": lab("observability/prometheusrule.yaml"),
            "run": "kubectl apply -f observability/prometheusrule.yaml",
        },
    ],
    "commands": [
        {"cmd": "docker compose exec prometheus promtool test rules /etc/prometheus/tests/alerts_test.yml", "what": "Run the alert unit tests inside the Prometheus container."},
        {"cmd": "docker compose exec alertmanager amtool check-config /etc/alertmanager/alertmanager.yml", "what": "Check alertmanager.yml for mistakes."},
        {"cmd": "am() { docker compose exec alertmanager amtool --alertmanager.url=http://localhost:9093 \"$@\"; }", "what": "Define am: run amtool against the lab's Alertmanager."},
        {"cmd": "am config routes test severity=page alertname=HelloDown", "what": "Print which receiver an alert with these labels would reach."},
        {"cmd": "am alert query -i", "what": "List alerts that are currently muted by an inhibition rule."},
        {"cmd": "am silence add alertname=HelloDown --duration=2h --comment=\"planned deploy\" --author=you", "what": "Mute matching alerts for two hours."},
        {"cmd": "am silence query", "what": "List active silences with their IDs."},
        {"cmd": "docker compose logs -f webhook", "what": "Watch the notifications the webhook receiver prints."},
        {"cmd": "helm install monitoring oci://ghcr.io/prometheus-community/charts/kube-prometheus-stack --version 92.16.0 --namespace monitoring --create-namespace -f observability/values.yaml", "what": "Install the whole monitoring stack on kind as the Helm release monitoring."},
        {"cmd": "kubectl -n monitoring get pods", "what": "Wait until every monitoring pod is Running."},
        {"cmd": "kubectl apply -f observability/servicemonitor.yaml -f observability/prometheusrule.yaml", "what": "Tell the Operator what to scrape and which rules to load."},
        {"cmd": "kubectl -n hello get svc --show-labels", "what": "Show the Service labels to compare with the ServiceMonitor's selector."},
        {"cmd": "kubectl -n monitoring port-forward svc/monitoring-kube-prometheus-prometheus 9090:9090", "what": "Open the cluster's Prometheus at localhost:9090."},
        {"cmd": "kubectl -n monitoring port-forward svc/monitoring-kube-prometheus-alertmanager 9093:9093", "what": "Open the cluster's Alertmanager at localhost:9093."},
        {"cmd": "kubectl -n hello scale deploy/hello-devops --replicas=0", "what": "Remove every pod on purpose to make HelloNoPodsUp fire."},
        {"cmd": "helm uninstall monitoring -n monitoring", "what": "Remove the stack. Its CRDs stay; the chart README lists the delete commands."},
    ],
    "mistake": (
        "Creating a ServiceMonitor or PrometheusRule without the release label of the Helm release. "
        "kubectl accepts it, nothing logs an error, and Prometheus simply never sees it. "
        "Check Status, Target health and Rule health in the Prometheus UI after every apply, and compare labels before you debug anything else."
    ),
    "real_world": (
        "At PayFlow, a made-up payments company, every team ships a ServiceMonitor and a PrometheusRule next to its Deployment in the same Helm chart. "
        "So monitoring changes go through code review like any other change. "
        "CI runs promtool test rules on every pull request. "
        "Alertmanager routes severity=page to PagerDuty and everything else to a Slack channel per team, and planned maintenance always starts with a silence that has a comment and an author."
    ),
    "task": {
        "title": "Monitor hello-devops on Kubernetes",
        "steps": [
            "Check that your kind cluster runs hello-devops in namespace `hello` with three ready pods, and that its Service has the label `app: hello-devops` and a port named `http`.",
            "Install kube-prometheus-stack as the release `monitoring` with `observability/values.yaml`, then wait until every pod in `monitoring` is Running.",
            "Apply `servicemonitor.yaml` and `prometheusrule.yaml`.",
            "Port-forward Prometheus. In Status, Target health, find `serviceMonitor/hello/hello-devops/0` and count its targets. Run `up{job=\"hello-devops\"}` and list the labels the Operator added.",
            "In Status, Rule health, find your `hello-devops` group. On the Alerts page, find `Watchdog` and explain why it is firing.",
            "Scale the deployment to 0 replicas. Watch `HelloNoPodsUp` go from pending to firing, then find it in Alertmanager through a second port-forward.",
            "Scale back to 3 replicas and watch the alert resolve.",
            "Remove the `release` label from the ServiceMonitor with `kubectl label`, wait a minute, and check Target health again. Then put the label back.",
        ],
        "hints": [
            "No target at all? Compare the ServiceMonitor's selector and labels with `kubectl -n hello get svc --show-labels`.",
            "At 0 replicas the Day 35 autoscaler stops scaling, and the lab's Argo CD app ignores replica counts, so nothing scales it back until you do.",
            "If pods in `monitoring` stay Pending, Docker Desktop needs more memory: Settings, then Resources.",
        ],
        "done_when": "Target health shows serviceMonitor/hello/hello-devops/0 with three UP targets, and you saw HelloNoPodsUp go from pending to firing and back.",
    },
    "explain_back": {
        "prompt": "Explain in 3 to 4 sentences what happens between the moment Redis fails and the moment the on-call engineer is notified. Mention the rule, for:, Alertmanager, grouping and inhibition.",
        "answer": (
            "Every 15 seconds Prometheus evaluates the error budget rule; once the error ratio crosses the burn-rate line, the alert becomes pending. "
            "If it stays true for the whole for: time it fires, and Prometheus sends it to Alertmanager. "
            "Alertmanager groups it with other alerts of the same name and job, waits group_wait, checks inhibition rules and silences, and routes it by its severity label. "
            "A page goes to the pager receiver, while the slower ticket alert for the same job is muted until the page resolves."
        ),
    },
    "recap": [
        "An alerting rule is a named PromQL condition; for: keeps it pending until it has been true long enough.",
        "Prometheus only decides that alerts fire; Alertmanager groups, routes, inhibits and silences them before a receiver is notified.",
        "promtool test rules and amtool config routes test let you prove alerts and routes before a real outage.",
        "A client library adds metrics to your code; histogram buckets and the process model decide how true your numbers are.",
        "kube-prometheus-stack runs Prometheus through the Operator; ServiceMonitors and PrometheusRules need the release label.",
        "kube-state-metrics turns object state into metrics, metrics-server feeds autoscaling, and remote write to Thanos or Mimir keeps data longer.",
    ],
    "check": [
        {
            "q": "During a network outage, 40 alerts for 40 different services fire within a minute, all with the same alertname. You want one message. What does that?",
            "options": [
                "A longer for: on each rule",
                "A silence on every service",
                "group_by on alertname in Alertmanager",
                "A higher repeat_interval",
            ],
            "answer": 2,
            "why": "Grouping by alertname puts all 40 into one group, and Alertmanager sends one notification per group.",
        },
        {
            "q": "Tonight you will restart the database, and you know the error alerts will fire for 10 minutes. What is the right tool?",
            "options": [
                "A silence in Alertmanager with a comment and an end time",
                "Delete the alert rules and add them back tomorrow",
                "An inhibition rule in alertmanager.yml for tonight",
                "Raise the error threshold to 100% until morning",
            ],
            "answer": 0,
            "why": "Silences are made at run time for exactly this case, expire on their own, and leave the rules and config untouched.",
        },
        {
            "q": "A new ServiceMonitor has `release: monitoring`, the right selector and namespace, but `port: 8000`. The Service port is named http with targetPort 8000. What happens?",
            "options": [
                "Prometheus scrapes port 8000 directly",
                "No target appears, because port must be a Service port name",
                "kubectl rejects the object with a schema error",
                "Prometheus scrapes port 80 instead",
            ],
            "answer": 1,
            "why": "The port field of a ServiceMonitor endpoint names a Service port, so a number matches nothing and the target silently never appears.",
        },
    ],
    "interview": [
        {
            "q": "What is the difference between Prometheus alerting rules and Alertmanager?",
            "a": (
                "Alerting rules live in Prometheus: each one is a PromQL condition, evaluated on a schedule, with a for: duration, labels and annotations. "
                "Prometheus decides when an alert is pending, firing or resolved, and sends active alerts to Alertmanager. "
                "Alertmanager never queries metrics; it deduplicates, groups, inhibits, silences and routes those alerts to receivers such as PagerDuty or Slack. "
                "Splitting them lets several Prometheus servers share one Alertmanager with one routing policy."
            ),
        },
        {
            "q": "How does Prometheus find targets on Kubernetes with the Prometheus Operator?",
            "a": (
                "You create a ServiceMonitor or PodMonitor that selects Services or pods by label and names the port and path to scrape. "
                "The Operator watches those objects and writes the matching Kubernetes service discovery config into Prometheus, which then scrapes every pod behind the Service. "
                "The Prometheus resource has selectors deciding which ServiceMonitors it reads; with kube-prometheus-stack that is the release label by default. "
                "Most \"my target is missing\" problems are a label, selector or port name mismatch."
            ),
        },
        {
            "q": "What makes an alert good or bad?",
            "a": (
                "A good alert fires on a symptom users feel, such as a fast error budget burn, and has a for: or short window to skip blips. "
                "It says clearly what is wrong and links to a runbook. "
                "It needs a human now, or it should be a ticket. "
                "A bad alert fires on a cause such as CPU, or flaps because it uses irate() or no for:. "
                "Worst of all is an alert that fires often with nothing to do, which teaches people to ignore pages. "
                "I also test alerts with promtool so I know they fire before production proves it."
            ),
        },
    ],
    "deeper": {
        "minutes": 12,
        "body": (
            "The lab's error series do not exist until the first error happens. That is why the Day 43 error ratio was empty instead of 0, and why the Day 43 task lost its first few 400s. "
            "The Prometheus [instrumentation guide](https://prometheus.io/docs/practices/instrumentation/) has a section called Avoid missing metrics: export a default value such as 0 for any series you know may exist in advance.\n\n"
            "Try it in a copy of `red_metrics.py`. After the two metric definitions, add a few lines that run once at startup:\n"
            "- `for status in (\"200\", \"500\"): RESPONSES.labels(path=\"/\", status=status)`\n"
            "- `DURATION.labels(path=\"/\")`\n\n"
            "Calling `.labels()` without `.inc()` creates the series at 0. Restart `web`, and `hello_responses_total{status=\"500\"}` now exists with the value 0. "
            "The error ratio returns 0 instead of nothing, and when the first real error comes, `rate()` sees the step from 0 to 1.\n\n"
            "Only do this for label values you know in advance. Pre-creating series for every possible URL would bring back the cardinality problem from Day 42.\n\n"
            "Next, look at the buckets. The defaults go 0.005, 0.01, 0.025, 0.05, 0.075, 0.1, 0.25, 0.5, 0.75, 1, 2.5, 5, 7.5 and 10 seconds. "
            "If your SLO says 300 ms, no bucket ends at 0.3, so you cannot count requests under 300 ms exactly. "
            "Pass `buckets=(0.01, 0.05, 0.1, 0.3, 1, 3)` to the Histogram to get fewer series and an exact edge at your threshold. "
            "Then `sum(rate(hello_request_duration_seconds_bucket{le=\"0.3\"}[5m])) / sum(rate(hello_request_duration_seconds_count[5m]))` is a latency SLI, and the Day 41 burn-rate maths works on it unchanged.\n\n"
            "Native histograms are the long-term answer to choosing buckets. They are stable since Prometheus 3.8, and they choose bucket limits automatically and store them in one series. "
            "They stay off until you set `scrape_native_histograms` and use a client that supports them. "
            "For this course, classic histograms are what you will meet in most existing systems.\n\n"
            "Finally, the Kubernetes pods still run two gunicorn workers. To get correct counters there, the fix belongs in the Deployment: run one worker with threads, as Compose does, and let the replica count give you capacity."
        ),
    },
    "sources": [src("alerting_rules"), src("am_config"), src("unit_tests"), src("kps_chart")],
}
