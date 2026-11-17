"""Book-voice rewrite of d52 (Alerting and Prometheus on Kubernetes). Writer: tg."""
import json, pathlib

P = pathlib.Path("/home/user/devops-from-zero/content/p12.json")
d = json.loads(P.read_text())
L = next(x for x in d["lessons"] if x["id"] == "d52")

L["opening"] = (
    "Picture a hospital night shift. The power flickers, and twenty bedside monitors beep at once. If each one rang "
    "the doctor's phone, she would get twenty calls about one problem. Worse, a real emergency in bed 12 would be "
    "one more ring in the noise. So hospitals put a nurses' station between the monitors and the doctor.\n\n"
    "It is easy to believe that more alarms mean more safety. Each alarm on its own looks sensible. Together, they "
    "bury the one that matters.\n\n"
    "Last time, we wrote queries that say how busy, how broken and how slow hello-devops is. They answer only when "
    "someone asks. In this lesson, we'll make Prometheus ask by itself, put a nurses' station called Alertmanager "
    "between it and the people, and prove our alarms work before a real outage does. Then we'll set up the same "
    "thing on Kubernetes.\n\n"
    "Before we start, make a guess, and keep it in mind."
)

L["guess"]["q"] = (
    "An alerting rule says for: 10m, so its condition must stay true for 10 minutes. The condition is true for 8 "
    "minutes, false for one check, then true again. When does it fire?"
)
L["guess"]["why"] = (
    "One false check sends the alert back to the start. The 10-minute wait begins again from zero. That is what "
    "for: is for: it filters out alerts that flip on and off."
)

plains = {
    "Alerting rule": "A PromQL condition with a name; every series it returns becomes an alert.",
    "Pending": "An alert whose condition is true but has not yet lasted its for: time.",
    "Alertmanager": "A separate service that groups, mutes and routes alerts from Prometheus to people.",
    "Receiver": "Where Alertmanager sends its messages: a web address, Slack, PagerDuty, email and others.",
    "Inhibition": "A rule that mutes some alerts while another alert is firing.",
    "Silence": "A mute for matching alerts that you set for a while, for example during planned maintenance.",
    "Prometheus Operator": "A Kubernetes program that runs Prometheus and Alertmanager for you, from objects you describe.",
    "ServiceMonitor": "A Kubernetes object that tells the Operator which Services to scrape, on which port and path.",
}
for t in L["terms"]:
    t["plain"] = plains[t["term"]]

S = L["sections"]

S[0]["h"] = "Rules that check by themselves: expr, for, labels, annotations"
S[0]["body"] = (
    "A dashboard helps only while someone is looking at it, and at 3 a.m. nobody is. So Prometheus checks the "
    "conditions itself, like a bedside monitor that beeps without being asked. An alerting rule is a PromQL query "
    "with a name. Prometheus runs it every evaluation interval (15 seconds in the lab), and every series the query "
    "returns is one active alert.\n\n"
    "Our lab app, hello-devops, is the tiny web app that greets every visitor and counts the visits. Here is "
    "`HelloDown` from its `alerts.yml`:\n"
    "- `expr: up{job=\"hello-devops\"} == 0` is the condition. The comparison filters, so the query returns something only when a scrape fails.\n"
    "- `for: 1m` means the condition must stay true for a whole minute. Until then the alert is pending.\n"
    "- `labels: severity: page` is added to the alert. Alertmanager routes on it.\n"
    "- `annotations` hold text for humans. `{{ $labels.instance }}` and `{{ $value }}` fill in the details.\n\n"
    "An alert moves through three states: inactive, pending, firing. If the condition is false for even one "
    "evaluation, the alert goes back to inactive and the wait starts again. That is the answer to the guess. So "
    "`for:` filters out blips, such as one slow scrape during a deploy. A good bedside monitor does the same: it "
    "waits a few seconds before it beeps, so a patient who turns over does not set it off.\n\n"
    "Prometheus also writes every active alert as a series named `ALERTS`, so `ALERTS{alertstate=\"pending\"}` is a "
    "normal query.\n\n"
    "The two SLO alerts turn the plan from two lessons ago into rules. They compare last time's recording rules with "
    "the burn-rate lines:\n"
    "- Page: 14.4 times the budget over 1 hour and 5 minutes, or 6 times over 6 hours and 30 minutes.\n"
    "- Ticket: 1 times the budget over 3 days and 6 hours.\n\n"
    "Prometheus only decides that an alert fires. It sends firing alerts to the Alertmanager listed under "
    "`alerting:` in `prometheus.yml`, and it does not send any message to a person itself.\n\n"
    "So the monitors can beep. Next, we'll build the nurses' station that decides who hears them."
)

S[1]["h"] = "The nurses' station: routes, groups, inhibition and silences"
S[1]["body"] = (
    "Prometheus re-sends each firing alert about once a minute, and one broken database can trip dozens of rules at "
    "the same time. Sent straight to a phone, that would be a flood. Alertmanager is a separate service that turns "
    "this stream into a few useful messages. It does four things:\n"
    "- Grouping: alerts with the same `group_by` labels become one notification. Fifty pods failing at once give one message, not fifty.\n"
    "- Routing: each group walks down a tree of routes, matched on labels, to a receiver. In the lab, `severity=\"page\"` goes to `pager` and everything else to `tickets`.\n"
    "- Inhibition: while one alert fires, it mutes others. The lab mutes ticket alerts for a job while a page fires for the same job.\n"
    "- Silences: temporary mutes you create at run time, in the UI on port 9093 or with `amtool`, its command line tool. They are not in the config file.\n\n"
    "A pod is one running copy of an app in Kubernetes. In the hospital, grouping is the station saying \"twenty "
    "beds, one power flicker\". Routing sends a heart alarm to the doctor and a broken drip to the morning list. "
    "Inhibition keeps quiet about small alarms while a team is already at the bed. A silence covers a planned "
    "procedure.\n\n"
    "Three timers control the pace, and the lab shortens all of them:\n"
    "- `group_wait` (default 30s): wait for more alerts before the first message of a new group.\n"
    "- `group_interval` (default 5m): wait before telling you about changes to a group already sent.\n"
    "- `repeat_interval` (default 4h): resend an alert that is still firing.\n\n"
    "A receiver is the destination. Alertmanager has built-in support for Slack, PagerDuty (a paging service), "
    "email, Microsoft Teams and more, plus a generic webhook. A webhook is a web address that receives a message "
    "whenever something happens. The lab's `webhook.py` is a 34-line Python server that prints what it receives, "
    "so you can see exactly what Slack would get. With `send_resolved: true`, Alertmanager also sends a message when "
    "the alert stops.\n\n"
    "The station follows its rules exactly as written. A wrong route sends the page nowhere, and nobody at the desk "
    "notices. So, next, we'll test the rules before we trust them."
)

S[2]["h"] = "Test alerts before they page anyone"
S[2]["body"] = (
    "An alert you never saw fire is a guess. Hospitals test their alarms; we can test ours. "
    "`promtool test rules` lets you prove a rule does what you think, without waiting for a real outage. A test "
    "file lists:\n"
    "1. The rule files to load.\n"
    "2. Made-up input series. `0+300x90` means start at 0 and add 300 every interval, 90 times.\n"
    "3. A time to check, and the exact alerts expected then, with labels and annotations.\n\n"
    "The lab's `tests/alerts_test.yml` checks three stories:\n"
    "- The app is down for two minutes, and `HelloDown` fires.\n"
    "- Errors start at minute 61 and keep going, and the fast burn pages.\n"
    "- A slow leak of 0.33% errors opens a ticket but does not page.\n\n"
    "Tests can fool you too. An earlier version of this test checked at minute 75. It passed, then failed on a "
    "later run with `4.513%` where it expected `4.762%`. Rule groups run independently, so the alert sometimes read "
    "the error ratio from one evaluation earlier, while errors were still climbing. Checking at minute 130, when "
    "the ratio is steady, fixed it. The promtool output shows the expected and the actual alert side by side, which "
    "makes such bugs quick to spot.\n\n"
    "Test the routing tree too: `amtool config routes test severity=page alertname=HelloDown` prints `pager`.\n\n"
    "**An alert you have never seen fire is only a hope. Test it before it matters.**\n\n"
    "Before you merge a new alert, ask these questions:\n"
    "- Does it fire on a symptom users feel?\n"
    "- Does it have a `for:` long enough to skip blips?\n"
    "- Does it use `rate()`, never `irate()`, so one quiet scrape does not reset it?\n"
    "- Does the annotation say what is wrong, and link to a runbook?\n"
    "- Would the person paged know what to do next?\n\n"
    "A runbook is a short page that says what an alert means and what to check first. The rules are only as good "
    "as the numbers they read, though. Next, we'll look at where those numbers come from inside the app."
)

S[3]["h"] = "Where the numbers come from: counters and histograms in code"
S[3]["body"] = (
    "A monitor can only report what its sensor measures. For an app, the sensors are lines of code. Adding metrics "
    "to your own code is called instrumenting, and you do it with a client library, ready-made code that keeps and "
    "shows the numbers. Python's is `prometheus_client`; other languages have their own, and Go deeper names one.\n\n"
    "hello-devops started with one line: `Counter(\"hello_requests_total\", ...)` and `.labels(path=\"/\").inc()` in "
    "the handler, the function that answers a visit. It counts visits, but it cannot see status codes or time. The "
    "lab adds both in `observability/red_metrics.py`, without touching `app.py`:\n"
    "1. It imports the Flask app and registers two hooks: one runs before every request and notes the start time, one runs after it.\n"
    "2. The after-hook increments `hello_responses_total` with the route and status code.\n"
    "3. It calls `observe()` on the histogram `hello_request_duration_seconds` with the elapsed seconds. No buckets are given, so the client's defaults apply: 5 ms up to 10 s.\n"
    "4. It uses Flask's route pattern as the `path` label, so a scan of random URLs adds only one `unmatched` value.\n\n"
    "Flask is the small Python web framework the app is built on. A hook is a function that the framework calls at "
    "a fixed moment, here before and after each request.\n\n"
    "Both metrics land in the client's default registry, the list of every metric the library knows. The app's "
    "existing `/metrics` route prints that list with `generate_latest()`, so no route changes. Compose mounts the "
    "file into the container and starts gunicorn, the program that runs the app's web server, with "
    "`red_metrics:app`.\n\n"
    "Two choices matter more than the code. First, buckets: put limits near the latencies you care about, such as "
    "your SLO threshold. Last time showed that `histogram_quantile` can only be as precise as the buckets. Second, "
    "the process model: one process per container, with threads, so every scrape sees every request (as the "
    "lesson on Prometheus's data model explained).\n\n"
    "So far all of this runs in Docker Compose on your laptop. Next, we'll move the whole hospital into Kubernetes."
)

S[4]["h"] = "Prometheus on Kubernetes: the Operator and kube-prometheus-stack"
S[4]["body"] = (
    "In a Kubernetes cluster, the group of machines that runs your containers, pods come and go. Each new pod gets "
    "a new IP address, its number on the network. Prometheus can find them with Kubernetes service discovery, but "
    "then every team edits one shared `prometheus.yml`. So on Kubernetes you rarely write that file by hand.\n\n"
    "The usual install is the kube-prometheus-stack Helm chart (Day 45 covered Helm, the tool that installs "
    "packaged apps). With the lab's `values.yaml`, version 92.16.0 rendered 109 objects. The main parts:\n"
    "- The Prometheus Operator, a controller that runs Prometheus and Alertmanager for you.\n"
    "- Prometheus and Alertmanager, described as custom resources and run as StatefulSets.\n"
    "- Grafana with ready-made dashboards for the cluster (Part 13).\n"
    "- node_exporter as a DaemonSet, one pod per node.\n"
    "- kube-state-metrics, which turns Kubernetes objects into metrics.\n"
    "- 134 ready-made alerting rules, such as `KubePodCrashLooping`.\n\n"
    "A few of those words need a line each. A controller is a program in the cluster that keeps things the way you "
    "described them. A StatefulSet runs pods that keep their own stored data. A DaemonSet puts one pod on every "
    "node, and a node is one machine in the cluster.\n\n"
    "The Operator adds custom resources, new kinds of Kubernetes objects (Day 38 showed how controllers work). "
    "Each team creates them next to its own app, and the Operator turns them into Prometheus's config and rule "
    "files:\n"
    "- `ServiceMonitor` and `PodMonitor`: what to scrape, found by labels.\n"
    "- `PrometheusRule`: recording and alerting rules.\n"
    "- `Probe` and `ScrapeConfig`: black-box checks and targets outside the cluster.\n"
    "- `AlertmanagerConfig`: routes and receivers, per namespace.\n\n"
    "In the hospital, each ward now writes its own alarm sheet, and the station collects them. Nobody edits one "
    "giant list.\n\n"
    "Two defaults look like bugs until you know them. One alert, `Watchdog`, always fires on purpose: if it ever "
    "stops arriving, your alerting pipeline is broken. And the chart's default Alertmanager config sends everything "
    "to a receiver named `null`, so nobody is notified until you add a real receiver.\n\n"
    "Next, we'll write the ward's sheet for hello-devops, and meet the one label that decides whether anyone reads "
    "it."
)

S[5]["h"] = "ServiceMonitors, PrometheusRules and the release label"
S[5]["body"] = (
    "`observability/servicemonitor.yaml` says: in namespace `hello`, find Services labelled `app: hello-devops`, and "
    "scrape their port named `http` at `/metrics` every 15 seconds. A Service is the stable address in front of a "
    "group of pods, and a namespace is a named area of the cluster.\n\n"
    "The Operator turns that into scrape settings. Prometheus then asks Kubernetes which pods stand behind the "
    "Service and scrapes each one directly, one target per pod. In Target health they appear under "
    "`serviceMonitor/hello/hello-devops/0`.\n\n"
    "The labels are richer than in Compose. `job` becomes the Service name, `hello-devops`, and the Operator adds "
    "`namespace`, `pod` and `service`. So the same PromQL works in both places, and `sum by (pod)` splits by pod.\n\n"
    "Labels also decide whether Prometheus reads your objects at all. The chart's Prometheus only reads "
    "ServiceMonitors, PodMonitors and PrometheusRules that carry the label `release` with the Helm release name. The "
    "lab installs the release as `monitoring`, so both files have `release: monitoring`.\n\n"
    "Leave it out and nothing fails: no error, no event, and your app never shows up. It is an alarm sheet dropped "
    "in the wrong tray. If a target is missing, check in this order:\n"
    "1. The `release` label on the ServiceMonitor.\n"
    "2. Its selector against `kubectl -n hello get svc --show-labels`.\n"
    "3. The port name: it must match a named port on the Service.\n\n"
    "**Kubernetes accepts a monitor nobody reads without a word. After every apply, check that the target appears.**\n\n"
    "The pods in Kubernetes run the image's own command: two gunicorn workers and no `red_metrics.py`. So the "
    "file `prometheusrule.yaml` alerts only on `up`. The worker problem from the data-model lesson cannot confuse "
    "that one. "
    "`HelloNoPodsUp` uses `absent()`, because a deleted pod leaves the target list instead of reporting `up = 0`.\n\n"
    "The app is watched now. Two last questions are about the cluster itself, and about how long we keep what we "
    "saw."
)

S[6]["h"] = "State metrics, autoscaling metrics and long-term storage"
S[6]["body"] = (
    "Two parts sound alike and do different jobs:\n"
    "- [kube-state-metrics](https://github.com/kubernetes/kube-state-metrics) reads the Kubernetes API and shows the state of objects as metrics: desired and available replicas, pod restarts, job results. Prometheus scrapes it.\n"
    "- [metrics-server](https://github.com/kubernetes-sigs/metrics-server) collects current CPU and memory from each kubelet for `kubectl top` and the autoscaler from Day 43. Its README says it is meant only for autoscaling, not as a source for monitoring.\n\n"
    "A replica is one copy of the app, and the kubelet is the Kubernetes agent on each node. In hospital terms, "
    "kube-state-metrics reads the admissions book. It tells you how many beds should be full, and how many are. "
    "metrics-server is the quick thermometer the ward uses to decide whether to open more beds.\n\n"
    "History is the other limit. One Prometheus keeps its data on local disk, 15 days by default, and the docs say "
    "that storage is not clustered or replicated. In plain words, there is one copy on one machine. Teams that need "
    "months of history, high availability or one view across many clusters add a second layer:\n"
    "- `remote_write` streams every sample to another system as it arrives.\n"
    "- [Thanos](https://github.com/thanos-io/thanos) runs next to existing Prometheus servers and keeps their blocks in object storage, such as S3.\n"
    "- [Grafana Mimir](https://github.com/grafana/mimir) receives remote write into a scalable, multi-tenant store, also backed by object storage.\n"
    "- Hosted services, such as Grafana Cloud, accept remote write too.\n\n"
    "Object storage is cheap online storage for large files, and S3 is Amazon's version. Multi-tenant means many "
    "teams share it while each sees only its own data.\n\n"
    "For one laptop cluster, 15 days of local data is plenty. The question to ask at work is how far back an "
    "incident review needs to look, and whether losing one Prometheus disk would hurt.\n\n"
    "We can now collect, query and alert. What we cannot yet do is see it all at a glance. A wall of PromQL is no "
    "way to start a shift, and that is the job of the dashboards in the next part."
)

# The nurses' station carries the analogy; the release-label mistake is in section 6.
L.pop("analogy", None)
L.pop("mistake", None)
L["real_world"] = (
    "Picture a payments company that ships its monitoring setup in the same Helm chart as the code. Every team puts "
    "a ServiceMonitor and a PrometheusRule next to its Deployment. So monitoring changes go through code review like "
    "any other change, and CI runs promtool test rules on every pull request. Alertmanager routes severity=page to "
    "PagerDuty and everything else to a Slack channel per team. Planned maintenance always starts with a silence "
    "that has a comment and an author."
)

W = L["worked"]["steps"]
W[0]["say"] = (
    "Test first. The promtool command runs the three stories in the test file, and amtool shows the routing tree. "
    "The `am` function runs amtool inside the Alertmanager container, as `q` does for promtool."
)
W[1]["say"] = (
    "Start Alertmanager and the webhook, reload Prometheus so it reads `alerts.yml`, and follow the webhook's output "
    "in a second terminal."
)
W[2]["say"] = (
    "Break it the same way as last time and wait about a minute. Both SLO alerts are pending: the condition is "
    "true, but `for: 2m` has not passed yet."
)
W[3]["say"] = (
    "Two minutes later both fire, and 10 seconds after that (`group_wait`) the webhook prints one line. Only the "
    "page arrived: the inhibition rule muted the ticket for the same job."
)
W[4]["say"] = (
    "You are working on it, so silence the page for an hour. A silence matches labels, has an author and a comment, "
    "and lives in Alertmanager, not in any file."
)
W[5]["say"] = "Fix the cause, then remove the silence so you will hear when the alert resolves."
W[6]["say"] = (
    "Now wait. Four minutes after the fix, the 5-minute ratio was already low, but the 30-minute ratio still held "
    "the outage, so the 6-hour tier kept the page firing. About 25 minutes after the fix the page resolved. In the "
    "same second, Alertmanager released the ticket it had been muting: the outage really did spend budget."
)

T = L["task"]
T["steps"] = [
    "Check that your kind cluster runs hello-devops in namespace `hello` with three ready pods, and that its Service has the label `app: hello-devops` and a port named `http`.",
    "Install kube-prometheus-stack as the release `monitoring` with `observability/values.yaml`, then wait until every pod in `monitoring` is Running.",
    "Apply `servicemonitor.yaml` and `prometheusrule.yaml`.",
    "Port-forward Prometheus. In Status, Target health, find `serviceMonitor/hello/hello-devops/0` and count its targets. Run `up{job=\"hello-devops\"}` and list the labels the Operator added.",
    "In Status, Rule health, find your `hello-devops` group. On the Alerts page, find `Watchdog` and explain why it is firing.",
    "Scale the deployment to 0 replicas. Watch `HelloNoPodsUp` go from pending to firing, then find it in Alertmanager through a second port-forward.",
    "Scale back to 3 replicas and watch the alert resolve.",
    "Remove the `release` label from the ServiceMonitor with `kubectl label`, wait a minute, and check Target health again. Then put the label back.",
]
T["hints"] = [
    "No target at all? Compare the ServiceMonitor's selector and labels with `kubectl -n hello get svc --show-labels`.",
    "At 0 replicas the Day 43 autoscaler stops scaling, and the lab's Argo CD app ignores replica counts, so nothing scales it back until you do.",
    "If pods in `monitoring` stay Pending, Docker Desktop needs more memory: Settings, then Resources.",
]
T["done_when"] = (
    "Target health shows serviceMonitor/hello/hello-devops/0 with three UP targets, and you saw HelloNoPodsUp go "
    "from pending to firing and back."
)

L["explain_back"]["prompt"] = (
    "Explain in 3 to 4 sentences what happens between the moment Redis fails and the moment the on-call engineer is "
    "notified. Mention the rule, for:, Alertmanager, grouping and inhibition."
)
L["explain_back"]["answer"] = (
    "Every 15 seconds Prometheus checks the error budget rule. Once the error ratio crosses the burn-rate line, the "
    "alert becomes pending. If it stays true for the whole for: time it fires, and Prometheus sends it to "
    "Alertmanager. Alertmanager groups it with other alerts of the same name and job, waits group_wait, checks "
    "inhibition rules and silences, and routes it by its severity label. A page goes to the pager receiver, while "
    "the slower ticket alert for the same job is muted until the page resolves."
)

L["recap"] = [
    "An alerting rule is a named PromQL condition; for: keeps it pending until it has been true long enough.",
    "Prometheus only decides that alerts fire; Alertmanager groups, routes, inhibits and silences them before a receiver hears.",
    "promtool test rules and amtool config routes test let you prove alerts and routes before a real outage.",
    "A client library adds metrics to your code; histogram buckets and the process model decide how true your numbers are.",
    "kube-prometheus-stack runs Prometheus through the Operator; ServiceMonitors and PrometheusRules need the release label.",
    "One Prometheus keeps one copy for 15 days; remote write to Thanos or Mimir keeps data longer and safer.",
]

C = L["check"]
C[0]["q"] = (
    "During a network outage, 40 alerts for 40 different services fire within a minute, all with the same "
    "alertname. You want one message. What does that?"
)
C[0]["why"] = "Grouping by alertname puts all 40 into one group, and Alertmanager sends one message per group."
C[1]["q"] = (
    "Tonight you will restart the database, and you know the error alerts will fire for 10 minutes. What is the "
    "right tool?"
)
C[1]["why"] = (
    "Silences are made at run time for exactly this case, end on their own, and leave the rules and config "
    "untouched."
)
C[2]["q"] = (
    "A new ServiceMonitor has `release: monitoring` and the right selector, but its endpoint says `port: web`. The "
    "Service's only port is named http. What happens?"
)
C[2]["why"] = (
    "The port field names a Service port. The object is valid, so kubectl accepts it, but web matches no port and "
    "the Operator creates no targets."
)

I = L["interview"]
I[0]["a"] = (
    "Alerting rules live in Prometheus: each one is a PromQL condition, checked on a schedule, with a for: duration, "
    "labels and annotations. Prometheus decides when an alert is pending, firing or resolved, and sends active "
    "alerts to Alertmanager. Alertmanager never queries metrics. It removes duplicates, groups, inhibits, silences "
    "and routes those alerts to receivers such as PagerDuty or Slack. Splitting them lets several Prometheus "
    "servers share one Alertmanager with one routing policy."
)
I[1]["a"] = (
    "You create a ServiceMonitor or PodMonitor that selects Services or pods by label and names the port and path "
    "to scrape. The Operator watches those objects and writes the matching Kubernetes service discovery config into "
    "Prometheus, which then scrapes every pod behind the Service. The Prometheus resource has selectors that decide "
    "which ServiceMonitors it reads; with kube-prometheus-stack that is the release label by default. Most \"my "
    "target is missing\" problems are a label, selector or port name mismatch."
)
I[2]["a"] = (
    "A good alert fires on a symptom users feel, such as a fast error budget burn, and has a for: or short window to "
    "skip blips. It says clearly what is wrong and links to a runbook. It needs a human now, or it should be a "
    "ticket. A bad alert fires on a cause such as CPU, or flips on and off because it uses irate() or no for:. Worst "
    "of all is an alert that fires often with nothing to do, which teaches people to ignore pages. I also test "
    "alerts with promtool so I know they fire before production proves it."
)

L["deeper"]["body"] = (
    "The lab's error series do not exist until the first error happens. That is why last time's error ratio was "
    "empty instead of 0, and why last time's task lost its first few 400s. The Prometheus [instrumentation "
    "guide](https://prometheus.io/docs/practices/instrumentation/) has a section called Avoid missing metrics: "
    "export a default value such as 0 for any series you know may exist in advance.\n\n"
    "Try it in a copy of `red_metrics.py`. After the two metric definitions, add a few lines that run once at "
    "startup:\n"
    "- `for status in (\"200\", \"500\"): RESPONSES.labels(path=\"/\", status=status)`\n"
    "- `DURATION.labels(path=\"/\")`\n\n"
    "Calling `.labels()` without `.inc()` creates the series at 0. Restart `web`, and "
    "`hello_responses_total{status=\"500\"}` now exists with the value 0. The error ratio returns 0 instead of "
    "nothing, and when the first real error comes, `rate()` sees the step from 0 to 1.\n\n"
    "Only do this for label values you know in advance. Pre-creating series for every possible URL would bring back "
    "the cardinality problem from the data-model lesson.\n\n"
    "Next, look at the buckets. The defaults go 0.005, 0.01, 0.025, 0.05, 0.075, 0.1, 0.25, 0.5, 0.75, 1, 2.5, 5, "
    "7.5 and 10 seconds. If your SLO says 300 ms, no bucket ends at 0.3, so you cannot count requests under 300 ms "
    "exactly. Pass `buckets=(0.01, 0.05, 0.1, 0.3, 1, 3)` to the Histogram to get fewer series and an exact edge at "
    "your threshold. Then `sum(rate(hello_request_duration_seconds_bucket{le=\"0.3\"}[5m])) / "
    "sum(rate(hello_request_duration_seconds_count[5m]))` is a latency SLI, and the burn-rate maths works on it "
    "unchanged.\n\n"
    "Native histograms are the long-term answer to choosing buckets. They are stable since Prometheus 3.8, and they "
    "choose bucket limits automatically and store them in one series. They stay off until you set "
    "`scrape_native_histograms` and use a client that supports them. For this course, classic histograms are what "
    "you will meet in most existing systems.\n\n"
    "Other languages have their own client libraries. On the JVM, the platform that runs Java and Kotlin, it is "
    "Micrometer. Spring Boot's Actuator uses it to record every request as `http.server.requests` and serve it at "
    "`/actuator/prometheus`.\n\n"
    "One gap remains: the Kubernetes pods still run two gunicorn workers. To get correct counters there, the fix "
    "belongs in the Deployment: run one worker with threads, as Compose does, and let the replica count give you "
    "capacity."
)

L["closing"] = (
    "We started on a night shift with twenty monitors beeping about one power flicker. Now hello-devops has the "
    "same calm. Its rules wait their `for:` time, and a station groups, routes and mutes. Tests prove it all works, "
    "and on Kubernetes a ServiceMonitor carries the right label. In the lab, run `am config routes` "
    "and check that every severity you use reaches a real receiver, not `null`.\n\n"
    "Next, we'll turn these numbers into pictures. How do you build a dashboard that tells a tired engineer, in five "
    "seconds, whether things are fine?"
)

P.write_text(json.dumps(d, indent=1, ensure_ascii=False) + "\n")
print("d52 written")
