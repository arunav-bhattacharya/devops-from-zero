"""Book-voice rewrite of d62 (Dynatrace in practice: Kubernetes, Grail and DQL). Writer: th."""
import sys
sys.path.insert(0, "/home/user/devops-from-zero/brief/scratch/v5/th")
from common import apply

OPENING = """Picture the detective from last time with a new assistant. The archive now holds every clue the building ever produced: every note, every alarm, every footstep. The assistant is sharp, and fluent in the archive language of their old job. They ask the clerk for "all reports where level = error", and the clerk comes back empty-handed. The assistant writes "no errors this week" in the case file. In fact there were hundreds. The clerk simply did not understand the question, and said nothing.

That is the trap with a new query language. Old habits look right, and a wrong question often returns an empty answer instead of an error.

Last time, we toured Dynatrace's Playground and watched Davis name a root cause. Today we put our own app in, learn DQL, the language for asking Dynatrace questions, and make the old habits fail on purpose. Then we turn queries into targets and release checks.

Before we start, make a guess, and keep it in mind."""

S1 = """Dynatrace only knows what you send it. There are three common ways in:
- OneAgent on a VM or server: one installer, then it watches the machine and its programs.
- The Dynatrace Operator on Kubernetes: it puts OneAgent into the cluster for you.
- OpenTelemetry: send OTLP, its standard format, from your own instrumentation or Collector, as on Day 57.

Our lab app, hello-devops, is a tiny web app that answers every visit with a greeting and a count of visits so far. Today it runs on kind, a practice Kubernetes cluster inside Docker, and Dynatrace watches it there.

Dynatrace has to know that the sender may write into your environment, so each way needs a token. A token is a secret key with a list of permissions called scopes. New environments use platform tokens, which start with `dt0s16.`. Older ones use access tokens, which start with `dt0c01.`.

Treat a token like a house key. Give it only the scopes its job needs, keep it out of git, and delete it when you are done. The easiest way to get the right scopes for Kubernetes is to let the trial's onboarding page create the token, as `dynatrace/README.md` explains.

Your environment ID is the first part of your address: in `https://abc12345.apps.dynatrace.com` it is `abc12345`. People use the `.apps.` address in the browser. Agents and APIs use `https://abc12345.live.dynatrace.com`. Mixing them up is a common cause of 404 errors, the web's "not found" answer.

Next, we'll let the Operator carry OneAgent into the cluster."""

S2 = """On Day 52 you met an operator: a controller that runs software for you, driven by a custom resource (a new kind of Kubernetes object). The Dynatrace Operator works the same way. You install it once with Helm, the Kubernetes package installer. Then you write a DynaKube, the custom resource that says what you want.

The Helm chart also installs a webhook: a small web server that the API server calls each time a Pod is created. The webhook may change the Pod before it is stored. Istio added its sidecars this way on Day 59, and Day 64 covers these admission webhooks. With the lab's DynaKube, the steps are:
1. The Operator reads the DynaKube and starts an ActiveGate pod.
2. A Pod is created in a labelled namespace, and the API server calls the webhook.
3. The webhook adds an init container, volumes and environment variables to the Pod.
4. The init container fetches the OneAgent code modules into a volume the app container shares.
5. A mounted `/etc/ld.so.preload` file, the hook from Day 61, makes the app load OneAgent as it starts.
6. OneAgent sends the app's data through the ActiveGate to Dynatrace.

An init container runs to the end before the app starts, and a volume is a folder that containers in a Pod share. Pods that existed before never went through the webhook, which is why you restart hello-devops after applying.

The DynaKube's biggest choice is the mode:
- `cloudNativeFullStack`: OneAgent in app pods and on every node. Dynatrace recommends it for normal clusters. It needs a CSI driver, a storage plugin on each node that downloads the code modules once and shares them with every pod there.
- `applicationMonitoring`: OneAgent in app pods only, added by the webhook as each pod is created. It is the only choice where you cannot touch the nodes, such as EKS Fargate, Amazon's service that runs pods on machines you never see.
- `hostMonitoring`: the nodes only.
- `classicFullStack`: the older style, still supported but no longer recommended.

The lab's `dynatrace/dynakube.yaml` uses `applicationMonitoring`. Kind nodes are Docker containers on your Mac, and a node agent expects a real Linux host underneath, so app-only injection is the safer choice. The lab also turns the CSI driver off, so each new pod's init container fetches its own copy of the code modules. That is slower, and fine for one app. The file adds one ActiveGate with `routing` and `kubernetes-monitoring`, and only injects into namespaces labelled `monitoring: dynatrace`.

Copying the official sample as it is would fail quietly. It asks 6Gi of memory for the ActiveGate, which would leave the pod Pending (waiting for room) on Docker Desktop. The lab asks for 512Mi, like Dynatrace's own setup examples.

A few minutes after you apply it and restart hello-devops, you should see:
- `Running` from `kubectl -n dynatrace get dynakube` (`Deploying` first, `Error` if something is wrong)
- the operator, webhook and `dynakube-activegate-0` pods in the `dynatrace` namespace
- an extra init container called `dynatrace-operator` in each new hello-devops pod (old pods never get one)
- a cluster called `kind-devops` in the Kubernetes app, with nodes, namespaces, workloads and events
- hello-devops in the Services app, if OneAgent can instrument your Python version

Dynatrace does not list kind or Apple Silicon Macs as supported. The images exist for arm64, the chip type in those Macs, and Dynatrace tests its Operator on kind (on Linux machines), so it may work. If it does not, the README lists the usual causes, and the trial with Dynatrace's Codespaces lab is the fallback.

Data is flowing in. Next, we'll learn how to ask it questions."""

S3 = """Grail is the store behind everything. It keeps logs, spans, events, problems and metrics side by side, and you read all of it with DQL, the Dynatrace Query Language.

A DQL query is a pipeline, like the shell pipelines from Day 5. The first command produces records. Each `|` hands them to the next command, which filters, reshapes or counts them. You read it top to bottom, in the order it runs. That is the biggest change if you know SQL, the common language for asking databases questions. In SQL, SELECT comes first and the database picks the order.

The first command decides what kind of data you get:
- `fetch logs`, `fetch spans`, `fetch events`, `fetch dt.davis.problems`: records, one row per log line, span or event
- `timeseries`: stored metrics, as series of numbers over time
- `smartscapeNodes` and `smartscapeEdges`: the topology map
- `data`: a small table you type into the query, good for practice

Every query also has a timeframe. The Notebook has a time picker, and you can set it in the query with `from:` and `to:`, as in `fetch logs, from: -1h`. Grail charges queries by the data they scan, so `from: -30d` over all logs costs real money on a paid environment. As a safety cap, `fetch` also takes `scanLimitGBytes:`. **Grail charges for what a query reads. Start with the shortest window that answers the question.**

You will write DQL in a Notebook. Add a section, choose DQL, type, run. The result appears as a table or a chart under the query. When a query is worth keeping, pin it to a dashboard or save it in `dynatrace/queries.dql`.

Next, we'll climb from one raw record to a chart, one command at a time."""

S4 = """Climb this ladder in a Notebook, one rung per run. Each rung is in `dynatrace/queries.dql`, part C.

1. `fetch logs, from: -1h | limit 10` returns ten raw log records. Read the field names; you need them for every later rung.
2. Add `| filter loglevel == "ERROR"`. Only error records stay. The severity field is `loglevel` and the message is `content`.
3. Add `| fields timestamp, loglevel, content`. Same rows, now three columns.
4. Swap that line for `| summarize errors = count(), by: {k8s.namespace.name}`. You get one row per namespace with a count, like GROUP BY in SQL.
5. Add `| sort errors desc`. Biggest first.
6. Swap summarize for `| makeTimeseries {total = count(), errors = countIf(loglevel == "ERROR")}, interval: 5m`. You get one row whose fields are arrays (lists of values) with one value per 5 minutes. The Notebook draws them as lines.
7. Metrics have their own first command, because Grail stores them as data points over time, not as records. `timeseries requests = sum(dt.service.request.count), by: {dt.service.name}` returns one series per service.

Rungs 6 and 7 need two more facts. A series is an array, so math on every point uses `[]`: `errors[] * 100.0 / total[]` gives an error percentage for each 5-minute slot. To squash a series into one number, use an array function such as `arrayAvg(cpu)` or `arrayMax(cpu)`.

Traces work the same way with `fetch spans`, with one catch. A single request can make many spans inside a service, for example one per database call. Query C6 keeps only spans where `request.is_root_span == true`, the span where the request entered the service, so each request counts once. Then it counts requests and failures and takes the p95 duration per service in one `summarize`. That is the RED method from Day 49 in a few lines. On Day 51 you built RED from counters the app had already counted. Here you count the span records yourself.

The ladder works when every word is right. Next, we'll watch what happens when old habits slip in."""

S5 = """If you write SQL every day, expect to make most of these at least once. This is the assistant from the opening. Several of them do not even fail. They quietly return zero rows, and zero rows looks like "no errors".
- Equality is `==`. A single `=` gives a field a name, as in `errors = count()`.
- A list in `by:` needs braces: `by: {a, b}`, never `by: a, b`.
- Order matters. After `summarize`, only the summarized fields exist, so filter first.
- Metric values come from `timeseries`. There is no `fetch` for them.
- Name an aggregate before you sort by it: `summarize n = count() | sort n desc`. `sort count() desc` fails.
- A fixed list uses braces: `in(loglevel, {"ERROR", "WARN"})`. Square brackets hold a subquery.
- Field names are not guessable. It is `loglevel`, not `log.level`, and spans have `start_time`, not `timestamp`.
- Do not wrap a field in `lower()` to compare it. Write `contains(content, "timeout", caseSensitive: false)`. `lower()` stops Grail from using its index, so it scans far more data.

The field name trap is the quietest. `filter log.level == "ERROR"` runs without complaint and returns nothing, because the field is called `loglevel`. So start each new query with `limit 10` to see the real field names. Then add one command at a time and check the row count after each. **Zero rows is not proof. Check the field names before you write "no errors".**

Dynatrace keeps a [comparison of DQL and SQL](https://docs.dynatrace.com/docs/platform/grail/dynatrace-query-language/dql-comparison) side by side.

Next, we'll make queries run without us."""

S6 = """A query you run by hand helps once. These features run it without you.

An SLO in Dynatrace is a query plus a target. You decide the promise: say, 99.5% of hello-devops requests succeed in under 3 seconds over 28 days. Query C9 in the lab file computes that kind of number from spans. The Service-Level Objectives app stores the definition and evaluates it over time against your target. The error budget idea from Day 49, the share of failures your promise still allows, applies unchanged.

A workflow is "when this happens, do these steps". Workflows run on Dynatrace's AutomationEngine. The trigger can be a schedule, an event or a problem. The steps can send email or a Slack message, call a webhook, or run a guardian. This is also how problems reach people: a problem opens, and a workflow routes it to the right team.

After a deploy, someone has to decide whether the new version behaves as well as the old one. By hand, that means watching dashboards, and on a busy day nobody does. Site Reliability Guardian (SRG) makes that decision a pipeline step. It is a release gate built from objectives, and it fits the pipelines from Part 6:
1. The pipeline deploys a new version and runs a load test, a burst of made-up traffic.
2. It sends an event to Dynatrace: version 1.4.0 of checkout was tested.
3. A workflow triggered by that event runs the guardian over the test's time window.
4. The guardian checks each objective, such as error rate and p95 latency, and returns pass, warning or fail.
5. The pipeline reads the result and promotes the release or stops it.

Dynatrace has ready integrations for GitHub Actions, GitLab, Azure DevOps and Argo CD. Its Codespaces lab walks through this whole flow, including a release that fails the gate.

OpenTelemetry fits in as well. Dynatrace accepts OTLP over HTTP at `https://<env-id>.live.dynatrace.com/api/v2/otlp`. The hello-devops setup from Day 57 can send its traces there by changing environment variables only. Go deeper shows how.

All of this runs on someone's bill. Next, we'll see how that bill is counted."""

S7 = """Dynatrace sells the Dynatrace Platform Subscription (DPS). You commit to a yearly amount, and usage draws it down against a rate card, the price list for each unit of usage. Use more and you pay the extra at the same rates. Almost everything is metered:
- monitoring time for hosts, pods and other entities
- data you send in, such as GiB of logs
- how long you keep data
- data your queries scan

This lesson gives no prices, because the public rate card changes and each company's contract sets its own rates. Remember the idea instead: in Dynatrace, a careless query over a month of logs costs money, just as shipping every debug line does. Query D3 in the lab file lists the billing usage events your environment records.

The trial is the place to learn this without risk. It lasts 15 days from sign-up, and Dynatrace does not publish all of its limits in a place this course could check. Plan your hands-on time before you start it.

To keep learning:
- [Dynatrace University](https://www.dynatrace.com/dynatrace-university/) is the official training site.
- The Dynatrace Associate certification is the entry-level exam. Third-party sites describe a paid, online, proctored exam, but check Dynatrace University for the official price and format.
- The open-source [Dynatrace for AI](https://github.com/Dynatrace/dynatrace-for-ai) skills include a compact list of DQL pitfalls, and `dtctl` runs DQL from your terminal.

With this part, the watching is done. We can see metrics, logs, traces and the calls between services, in open-source tools or in one platform. What none of them asks is who else might be inside the building. The next part is about security."""

CLOSING = """We started with an assistant who wrote "no errors" because the clerk did not understand the question. Today we sent hello-devops' data into Grail and climbed DQL from one raw record to a chart. Then we broke queries with SQL habits on purpose, to see which fail loudly and which fail silently. In a Notebook, run `fetch logs, from: -1h | limit 10` and read the real field names before you write anything else.

Next, we'll start a new part on security, with the software supply chain. When most of your image is other people's code, how do you know what you are shipping?"""

new = {
    "goal": "By the end you can install the Dynatrace Operator and a DynaKube on kind (or say exactly why it failed), write DQL from fetch to timeseries without SQL habits, and explain how a query becomes an SLO or a release check.",
    "opening": OPENING,
    "guess": (
        "You know SQL, the common database language, well. Which DQL query counts ERROR log records per Kubernetes namespace?",
        "DQL compares with `==`, wraps the `by:` list in braces and runs top to bottom, so the filter must come before the summarize. The first option carries two SQL habits; the last filters on a field that summarize removed.",
    ),
    "terms": [
        "A Kubernetes operator that installs and updates OneAgent and ActiveGate in a cluster.",
        "The custom resource that tells the Dynatrace Operator what to deploy and where.",
        "The DynaKube mode that puts OneAgent into application pods only, never onto the nodes.",
        "Dynatrace Query Language: commands joined by `|` that run top to bottom over data in Grail.",
        "A Dynatrace app where you write and run DQL step by step and see tables and charts.",
        "A DQL command that turns records, such as log lines, into a series you can chart.",
        "A Dynatrace automation: a trigger, such as a problem or a schedule, followed by steps.",
        "A Dynatrace app that checks a release against objectives and returns pass, warning or fail.",
    ],
    "sections": [
        ("Three ways in, and a token for each", S1),
        ("The Operator and the DynaKube on kind", S2),
        ("Grail and the shape of a DQL query", S3),
        ("A DQL ladder, one command at a time", S4),
        ("SQL habits that break in DQL", S5),
        ("From queries to action: SLOs, workflows and release checks", S6),
        ("Cost, the trial's limits and what to learn next", S7),
    ],
    "diagram_caption": "The Operator turns your DynaKube into a webhook and an ActiveGate; data lands in Grail, and you read it with DQL.",
    "say": [
        "Open a Notebook (the Playground is fine), add a DQL section and run query B1. The `data` command builds a six-row table inside the query. Everyone gets the same result, and Grail scans nothing.",
        "Add a filter on a new line. Records flow down the pipe, and `filter` keeps the ones where the condition is true. Note the `>=`; equality would be `==`.",
        "Replace the filter with a summarize. It groups the records by `path` and computes one row per group. Each result gets a name with a single `=`, and the `by:` list sits in braces. The rows can come back in any order until you sort them.",
        "Add a computed field and sort by it. `fieldsAdd` keeps every column and adds one. Sort by the name you gave the field, not by an expression.",
        "Now make two SQL mistakes on purpose, one at a time, and read the messages. Both runs fail. The first uses `=` where DQL wants a true or false test. In the second, `by:` without braces takes only `path`, and `status` is read as one more aggregation, which it is not.",
        "Put `fetch logs, from: -1h` where `data` was, and the same commands work on real logs. Only the first line changed. The commands below it do not care where the records came from.",
    ],
    "task": (
        [
            "Choose your path. If you will not start the trial now, do steps 6 and 7 in the Playground and skip the rest.",
            "Start the 15-day trial, note your environment ID, and get a token as step 1 of `dynatrace/README.md` explains.",
            "Install the Operator with Helm and create the `dynakube` secret (README steps 2 and 3).",
            "Label the `hello` namespace, dry-run the DynaKube (check it without creating anything), apply it and restart hello-devops (README step 4).",
            "Check that the DynaKube shows `Running` and that a new hello-devops pod has the `dynatrace-operator` init container. Send traffic with `curl localhost:8081` a few times.",
            "In a Notebook, climb rungs C1 to C7 from `dynatrace/queries.dql`. Write one line per rung on what it returned.",
            "Break one query with each SQL habit from this lesson. Note which ones fail with an error and which return zero rows.",
            "Run D1 and D2 and find `kind-devops` and hello-devops in the results.",
            "Uninstall in the README's order, then delete the token in Dynatrace.",
        ],
        [
            "If `dynakube-activegate-0` stays Pending, describe the pod. An insufficient memory message means Docker Desktop needs more memory.",
            "Zero rows on your own data? Check the time picker first, because your data is only minutes old.",
            "If the install fails on your Mac, write down the exact error. That is a known risk, and the Codespaces lab runs on Linux machines instead.",
        ],
        "You have one note line per ladder rung, and either `smartscapeNodes \"K8S_CLUSTER\"` lists `kind-devops` or you have written down the exact error that stopped the install.",
    ),
    "explain_back": (
        "Explain how DQL differs from SQL to a teammate who writes SQL every day, in 3 to 4 sentences. Mention the pipeline order, fetch versus timeseries, and two syntax traps.",
        "A DQL query starts from a source and runs top to bottom: each `|` passes the records to the next command, so you filter before you summarize. Records such as logs and spans come from `fetch`, while stored metrics come from `timeseries`, never from `fetch`. Equality is `==` because a single `=` names a field, and a `by:` list needs braces. Many mistakes return zero rows instead of an error, so check field names with `limit 10` first.",
    ),
    "recap": [
        "The Dynatrace Operator reads a DynaKube; for kind, use applicationMonitoring with a small ActiveGate.",
        "Kind and Apple Silicon are not officially supported, so the local install may fail; the Playground always works.",
        "DQL runs top to bottom: fetch, filter, fields, summarize, sort, with makeTimeseries for charts.",
        "Metrics come from timeseries; `==` compares; `by:` lists need braces; empty results often mean a wrong field name.",
        "SLOs, workflows and Site Reliability Guardian turn queries into targets, automation and release gates.",
        "Ingest, retention and query scans are all metered, so keep time windows short and filter early.",
    ],
    "closing": CLOSING,
    "check": [
        ("You need the average CPU per host over the last hour. Which query starts the right way?",
         "Metric values are read with `timeseries`. There is no `fetch` for them."),
        ("Your company runs its pods on EKS Fargate, where you cannot run anything on the nodes. Which DynaKube mode fits?",
         "Only app-only injection works where the nodes are off-limits. The other modes need an agent on each node."),
        ("A query `fetch logs, from: -30d | filter contains(lower(content), \"refund\")` is slow and costly. What is the best first change?",
         "The cost comes from scanning: a shorter window scans less, and dropping `lower()` lets Grail use its index."),
    ],
    "interview": [
        ("How would you roll out Dynatrace to a Kubernetes cluster?",
         "Install the Dynatrace Operator with its Helm chart, create a secret with a scoped token, and apply a DynaKube that picks the mode and the ActiveGate capabilities. On normal nodes I would use cloudNativeFullStack, which Dynatrace recommends. Where nodes are off-limits, such as Fargate, I would use applicationMonitoring. I would keep the DynaKube in git, let teams opt in with a namespace label, and restart workloads so the webhook can inject OneAgent."),
        ("What is the difference between fetch, timeseries and makeTimeseries in DQL?",
         "The `fetch` command reads records such as logs, spans and events, one row per record. The `timeseries` command reads stored metrics and returns arrays of values over time. The `makeTimeseries` command sits later in a pipeline and turns fetched records into a series, for example error logs per 5 minutes. So metrics start with `timeseries`, and counts from records end with `makeTimeseries` when you want a chart."),
        ("How can Dynatrace act as a quality gate in a CI/CD pipeline?",
         "The pipeline deploys to a test environment, runs a load test and sends an event to Dynatrace. A workflow triggered by that event runs a Site Reliability Guardian over the test window. The guardian checks objectives such as error rate and p95 latency and returns pass, warning or fail. The pipeline reads that result and promotes the build or stops it, so the decision rests on measured behaviour."),
    ],
    "drop": ["analogy", "mistake", "real_world"],
}

apply(16, "d62", new)
