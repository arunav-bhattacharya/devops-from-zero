#!/usr/bin/env python3
"""Build content/p12.json (Part 12: Dynatrace) for the second edition."""
import json
import pathlib

import svg

ROOT = pathlib.Path(__file__).resolve().parents[4]
LAB = ROOT / "labs/hello-devops/dynatrace"
OUT = ROOT / "content/p12.json"


def ref(title, url, kind):
    return {"title": title, "url": url, "kind": kind}


def mcq(q, options, answer, why, frm=None):
    d = {"q": q, "options": options, "answer": answer, "why": why}
    if frm:
        d["from"] = frm
    return d


# Every URL below came from the research notes or from searches and repo checks in this task.
U = {
    "get_started": "https://docs.dynatrace.com/docs/discover-dynatrace/get-started",
    "try_free": "https://www.dynatrace.com/try-free",
    "tech_support": "https://docs.dynatrace.com/docs/ingest-from/technology-support",
    "purepath": "https://docs.dynatrace.com/docs/observe-and-explore/purepath-distributed-traces",
    "rca": "https://docs.dynatrace.com/docs/shortlink/next-gen-ai-analytics",
    "capability_map": "https://docs.dynatrace.com/docs/platform/upgrade/foundations/capability-mapping-classic-to-latest",
    "assist_blog": "https://www.dynatrace.com/news/blog/dynatrace-assist-ask-analyze-and-act-with-dynatrace-intelligence/",
    "intel_pr": "https://www.dynatrace.com/news/press-release/dynatrace-intelligence-redefines-observability/",
    "managed": "https://docs.dynatrace.com/managed/upgrade/unavailable-in-managed",
    "quickstart_blog": "https://www.dynatrace.com/news/blog/get-real-service-insights-in-minutes-with-the-quickstart-app-dynatrace-free-trial-and-dtwiz-cli/",
    "operator_gh": "https://github.com/Dynatrace/dynatrace-operator",
    "appmon_sample": "https://github.com/Dynatrace/dynatrace-operator/blob/v1.11.1/assets/samples/dynakube/v1beta6/applicationMonitoring.yaml",
    "k8s_deploy": "https://docs.dynatrace.com/docs/ingest-from/setup-on-k8s/deployment",
    "dynakube_params": "https://docs.dynatrace.com/docs/ingest-from/setup-on-k8s/reference/dynakube-parameters",
    "tokens_upgrade": "https://docs.dynatrace.com/docs/platform/upgrade/set-up-your-environment/upgrade-from-access-tokens-classic",
    "dql_use": "https://docs.dynatrace.com/docs/shortlink/dql-use-queries",
    "dql_compare": "https://docs.dynatrace.com/docs/platform/grail/dynatrace-query-language/dql-comparison",
    "dql_best": "https://docs.dynatrace.com/docs/platform/grail/dynatrace-query-language/dql-best-practices",
    "dql_agg": "https://docs.dynatrace.com/docs/discover-dynatrace/platform/grail/dynatrace-query-language/commands/aggregation-commands",
    "dt_for_ai": "https://github.com/Dynatrace/dynatrace-for-ai",
    "srg_docs": "https://docs.dynatrace.com/docs/deliver/quality-gates",
    "automation": "https://docs.dynatrace.com/docs/discover-dynatrace/platform/automationengine",
    "slo_hub": "https://www.dynatrace.com/hub/detail/service-level-objectives",
    "otlp": "https://docs.dynatrace.com/docs/ingest-from/opentelemetry/otlp-api",
    "pricing": "https://docs.dynatrace.com/docs/license/how-pricing-works",
    "pricing_faq": "https://www.dynatrace.com/pricing/frequently-asked-questions/",
    "university": "https://www.dynatrace.com/dynatrace-university/",
    "obslab": "https://github.com/Dynatrace/obslab-release-validation",
    "dtctl": "https://github.com/dynatrace-oss/dtctl",
    "workflow_samples": "https://github.com/Dynatrace/dynatrace-workflow-samples",
    "otel_delta": "https://community.dynatrace.com/t/how-to-set-up-opentelemetry-metrics-with-delta-temporality/50106",
    # Videos (from YouTube search results in this task; the SRG video is also linked from Dynatrace's obslab repo)
    "v_smartscape": "https://www.youtube.com/watch?v=ujSWwuyvCVE",
    "v_davis": "https://www.youtube.com/watch?v=Tud2K3zyync",
    "v_assist": "https://www.youtube.com/watch?v=_XgzpUBZK08",
    "v_intel": "https://www.youtube.com/watch?v=Hr7c4DTPDa0",
    "v_srg": "https://www.youtube.com/watch?v=91t_NWnTFWA",
    "v_dql_guide": "https://www.youtube.com/watch?v=F2VbVqNlswk",
    "v_dql_query": "https://www.youtube.com/watch?v=sCJbl4guvVI",
    "v_dql_metrics": "https://www.youtube.com/watch?v=-uEFITJAb64",
}

QUERIES = (LAB / "queries.dql").read_text()
DYNAKUBE = (LAB / "dynakube.yaml").read_text()

# The Day 50 version of queries.dql: a short header plus part A of the final file.
_part_a = QUERIES.split("// ======================================================================\n// Day 51, part B")[0]
_part_a = _part_a[_part_a.index("// ======================================================================\n// Day 50"):]
QUERIES_D50 = (
    "// DQL queries from Day 50 of \"DevOps, from zero\". Day 51 adds parts B to D.\n"
    "// Run ONE query at a time: open the Notebooks app, add a DQL section, paste, run.\n"
    "// The Playground (free, sample data) is enough for all of part A.\n\n\n"
    + _part_a.rstrip() + "\n"
)

HELM = ("helm upgrade --install dynatrace-operator oci://public.ecr.aws/dynatrace/dynatrace-operator "
        "--version 1.11.1 --namespace dynatrace --create-namespace --set csidriver.enabled=false --rollback-on-failure")
SECRET = ("kubectl -n dynatrace create secret generic dynakube --from-env-file=<(printf 'apiToken=%s\\ndataIngestToken=%s\\n' "
          "\"$DT_API_TOKEN\" \"$DT_DATA_INGEST_TOKEN\") --dry-run=client -o yaml | kubectl apply -f -")
SED_DRY = 'sed "s/ENVIRONMENTID/$DT_ENV_ID/" dynatrace/dynakube.yaml | kubectl apply --dry-run=server -f -'
SED_APPLY = 'sed "s/ENVIRONMENTID/$DT_ENV_ID/" dynatrace/dynakube.yaml | kubectl apply -f -'

# ---------------------------------------------------------------- Day 50
d50 = {
    "id": "d50",
    "title": "Dynatrace: one platform for every signal",
    "minutes": 45,
    "goal": "By the end you can explain what OneAgent, ActiveGate, Smartscape, PurePath and Davis do, compare Dynatrace "
            "with the open-source stack from Parts 9 to 11, and find a problem's root cause in the free Playground.",
    "guess": mcq(
        "Your Grafana stack fires 30 alerts at 10:02. Dynatrace opens one problem and names a root cause. How does "
        "Davis, its analysis engine, pick that root cause?",
        [
            "It picks whichever metric started to rise first",
            "It follows recorded dependencies and traces between components",
            "A chat model reads all the logs and writes a guess",
            "It uses alert rules that your team wrote in advance",
        ],
        1,
        "Davis starts at the affected component and follows the dependencies and traces that OneAgent recorded, then "
        "runs a fault-tree analysis. Timing alone is not enough, and the chat assistant is a separate tool.",
    ),
    "terms": [
        {"term": "Dynatrace", "plain": "A commercial observability platform, run for you as SaaS, that keeps metrics, logs, traces and events together."},
        {"term": "OneAgent", "plain": "Dynatrace's agent. It finds the processes on a host or in a pod and records their data without code changes."},
        {"term": "ActiveGate", "plain": "A Dynatrace relay that forwards agent traffic and reads APIs, such as the Kubernetes API."},
        {"term": "Entity", "plain": "Anything Dynatrace monitors and gives an ID: a host, a process, a service, a Kubernetes pod."},
        {"term": "Smartscape", "plain": "The live map of entities and their links, drawn automatically from what OneAgent sees."},
        {"term": "PurePath", "plain": "Dynatrace's name for a trace recorded by OneAgent, down to method and database calls."},
        {"term": "Davis", "plain": "The engine that spots anomalies, groups related ones into one problem and names the likely root cause."},
        {"term": "Grail", "plain": "Dynatrace's data store. It holds every signal in one place, and you read it with DQL."},
    ],
    "sections": [
        {
            "h": "What an all-in-one platform buys you",
            "body": (
                "In Parts 9 to 11 you built an observability stack from open-source parts. Count them:\n"
                "- Prometheus and Alertmanager for metrics and alerts (Part 9)\n"
                "- Grafana for dashboards (Part 10)\n"
                "- Elasticsearch, Kibana and Fluent Bit for logs (Part 11)\n"
                "- the OpenTelemetry Collector and Jaeger for traces (Part 11)\n\n"
                "That is eight programs to run, upgrade and keep alive, before you count exporters. Most have their own query "
                "language: "
                "PromQL, KQL or ES|QL, and Jaeger's search form. When something breaks, you jump between tabs and match "
                "things up by hand. This trace ID, that pod name, the same minute on three graphs.\n\n"
                "Dynatrace takes the opposite approach. It is a commercial observability platform that Dynatrace runs for "
                "you as SaaS (software as a service: you use it in the browser, they run the servers). One agent "
                "collects the data. One store, called Grail, keeps every signal. One query language, DQL, reads all of "
                "it. And the platform links the signals for you, because each log line, span and metric is tied to the "
                "same host, process or service.\n\n"
                "You pay for that in three ways:\n"
                "- Money. Billing follows usage, and data sent, data kept and data queried all count (Day 51).\n"
                "- Lock-in. Your dashboards, queries and alert setup only work in Dynatrace.\n"
                "- Control. Your telemetry leaves your network and lives on Dynatrace's servers.\n\n"
                "For a handful of services, the stack you built is plenty. A platform like this starts to pay off when "
                "you run hundreds of services and nobody can keep the whole dependency map in their head."
            ),
            "refs": [
                ref("Get started with Dynatrace (Dynatrace docs)", U["get_started"], "docs"),
                ref("Dynatrace Intelligence announcement (Dynatrace press release)", U["intel_pr"], "read"),
            ],
        },
        {
            "h": "OneAgent and ActiveGate: install once, see a lot",
            "body": (
                "**OneAgent** is Dynatrace's agent. You install it once per host. On Kubernetes, the Dynatrace Operator "
                "adds it to your pods for you (Day 51). Then it does three jobs without code changes:\n"
                "1. It finds every process and works out what it is: a JVM, a Node.js server, a database.\n"
                "2. It loads a small code module into supported processes. The module records each request as it passes "
                "through, which gives you traces.\n"
                "3. It sends metrics, logs and traces to Dynatrace.\n\n"
                "Compare that with Day 49. There you started hello-devops with `opentelemetry-instrument`, one service "
                "at a time, and ran a Collector to forward the data. OneAgent moves that work from each service to the "
                "host. Your Kotlin app from Part 5 is the classic case: Java needs no agent flag in the Dockerfile and "
                "no SDK in the Gradle build. Python support arrived later, so check the "
                f"[technology support pages]({U['tech_support']}) for your runtime and version before you count on it.\n\n"
                "One rule trips people up. OneAgent cannot add itself to a process that is already running. After you "
                "install it, restart the apps you want to see.\n\n"
                "ActiveGate is the second piece. It is a relay between your network and Dynatrace. It also talks to "
                "things OneAgent cannot sit inside, such as the Kubernetes API or a cloud provider's API. On Kubernetes "
                "you switch these jobs on as capabilities. `routing` relays OneAgent traffic. `kubernetes-monitoring` "
                "reads nodes, workloads and events."
            ),
            "refs": [
                ref("Technology support: what OneAgent can instrument (Dynatrace docs)", U["tech_support"], "docs"),
                ref("Dynatrace Operator: modes and ActiveGate capabilities (GitHub)", U["operator_gh"], "read"),
            ],
        },
        {
            "h": "Entities and Smartscape: a map nobody draws",
            "body": (
                "Dynatrace calls each thing it monitors an entity, and gives each one an ID. The common types are:\n"
                "- host: a machine or VM\n"
                "- process: one running program on a host, such as gunicorn\n"
                "- service: what a process offers to callers, such as the hello-devops web endpoints\n"
                "- Kubernetes cluster, namespace, workload and pod\n\n"
                "Smartscape is the live map of these entities and how they connect. Nobody draws it. OneAgent sees which "
                "process runs on which host and which service calls which, and Smartscape records it.\n\n"
                "The map runs in two directions. Vertical links say what runs on what: a service runs in a process, and "
                "the process runs on a host. Horizontal links say who calls whom: checkout calls payments, and payments "
                "calls a database.\n\n"
                "This matters because every metric, log line and span carries the ID of the entity it came from. That shared ID is "
                "how Dynatrace joins your signals without join logic from you. It is also the map Davis walks when "
                "something breaks.\n\n"
                "You can query the map with DQL, the language you learn on Day 51. `smartscapeNodes \"SERVICE\"` lists "
                "services, and `smartscapeEdges \"calls\"` lists who calls whom. Fields that point at an entity start "
                "with `dt.smartscape.`, for example `dt.smartscape.host`. Older queries use `dt.entity.*`. Those fields "
                "are deprecated, so do not copy them into new work."
            ),
            "refs": [
                ref("How to query Smartscape on Grail (video)", U["v_smartscape"], "watch"),
                ref("Dynatrace for AI: DQL essentials and Smartscape notes (Dynatrace, GitHub)", U["dt_for_ai"], "read"),
            ],
        },
        {
            "h": "PurePath traces and the services view",
            "body": (
                "On Day 49 you met traces: one request's path through many services, made of spans that share a trace "
                "ID. PurePath is Dynatrace's name for the traces OneAgent records. They often go deeper than hand-made "
                "spans. A PurePath can show the method calls and database statements inside a service, with timings, "
                "and nobody wrote a line of tracing code.\n\n"
                "Spans from OpenTelemetry are welcome too. They land in Grail next to the ones OneAgent captured, and "
                "you query both the same way.\n\n"
                "You rarely start from a single trace. You start from the Services app. It lists each service with the "
                "numbers from the RED method on Day 41:\n"
                "- request rate (requests per minute)\n"
                "- failure rate (the share of requests that failed)\n"
                "- response time, including slow percentiles such as p95\n\n"
                "The usual path goes like this:\n"
                "1. Pick the service with a bad number.\n"
                "2. Filter its requests: the slow ones, the failed ones, or one endpoint.\n"
                "3. Open one trace from that list.\n"
                "4. Find the span that takes most of the time, and the service that owns it.\n\n"
                "The process and host views work the same way for CPU, memory and restarts."
            ),
            "refs": [
                ref("Distributed tracing with PurePath (Dynatrace docs)", U["purepath"], "docs"),
            ],
        },
        {
            "h": "Davis: one problem instead of thirty alerts",
            "body": (
                "**Davis** is the engine that watches all of this. It does two jobs.\n\n"
                "First, it detects anomalies. It learns a baseline for a metric, which is what normal looks like for "
                "this service at this time. When the value leaves the baseline, it raises an event. You can also set "
                "fixed thresholds, as you did with Prometheus alert rules.\n\n"
                "Second, it groups related events into one problem and names the most likely root cause. This is where "
                "it differs from your Part 9 stack. Davis starts at the affected entity and follows the Smartscape links "
                "and the traces to what that entity depends on. Graphs that spiked in the same minute are not enough "
                "on their own. Then it runs a fault-tree analysis to pick the most probable cause.\n\n"
                "A problem holds:\n"
                "- an ID such as `P-12345` and a title\n"
                "- the root-cause entity and the evidence: events, metric changes, deployments\n"
                "- the affected entities and, where Dynatrace can tell, the affected users\n\n"
                "Two limits matter. Davis can only follow dependencies that OneAgent or your OpenTelemetry data shows. "
                "A service nobody instruments is invisible to it. And Davis does not know what you promised your users. "
                "The SLOs from Day 41 are still yours to write."
            ),
            "refs": [
                ref("Root cause analysis (Dynatrace docs)", U["rca"], "docs"),
                ref("Analyze incidents with Davis AI (video)", U["v_davis"], "watch"),
            ],
        },
        {
            "h": "The 2026 names: Latest Dynatrace, Dynatrace Intelligence and Assist",
            "body": (
                "Dynatrace renamed a lot recently, and old screenshots will confuse you.\n\n"
                "Latest Dynatrace is the current platform. You reach it at an address like "
                "`https://abc12345.apps.dynatrace.com` and work in apps such as Notebooks, Dashboards, Problems, "
                "Services, Kubernetes and Workflows. Dynatrace Classic is the older generation. Some of its screens "
                "still exist as classic apps with \"Classic\" in the name, such as Dashboards Classic. If a screenshot "
                "does not match your screen, it is probably Classic. Look for the app with the same name.\n\n"
                "A few classic ideas have new names. Management zones, the classic way to slice data by team or "
                "environment, became segments.\n\n"
                "In January 2026 Dynatrace put all of its AI under one name, Dynatrace Intelligence:\n"
                "- Davis is the root-cause and anomaly engine you just read about.\n"
                "- Dynatrace Assist is the chat assistant that replaced Davis CoPilot. Ask a question in plain English "
                "and it can write the DQL for you.\n"
                "- Agents act on what they find, inside rules and approvals that you set.\n\n"
                "Old names live on in APIs and data. Problems are stored as `dt.davis.problems`, and some docs still "
                "say Davis CoPilot. Read the DQL that Assist writes the way you would read a colleague's draft.\n\n"
                "Two apps get most of your time. Notebooks are for exploring: you write DQL step by step and see each "
                "result. Dashboards are for sharing a view with the team, and you can pin a Notebook result to one.\n\n"
                "Dynatrace Managed is a self-hosted edition for companies that must keep data on their own servers. "
                "Grail, and with it DQL, Notebooks and Workflows, only exists on SaaS. This course uses SaaS."
            ),
            "refs": [
                ref("Capability mapping from Classic to Latest Dynatrace (Dynatrace docs)", U["capability_map"], "docs"),
                ref("Dynatrace Assist: ask, analyze and act (Dynatrace blog)", U["assist_blog"], "read"),
                ref("How to get started with Dynatrace Assist (video)", U["v_assist"], "watch"),
            ],
        },
        {
            "h": "How it compares, and how to try it for free",
            "body": (
                "These are the options you are likely to meet:\n"
                "- Your open-source stack: free software, full control, runs anywhere. You instrument each service and "
                "link the signals yourself.\n"
                "- Datadog and New Relic: also SaaS, agent-based and all-in-one. Compare them on your own services "
                "during a trial, since the differences are in the details and the price list.\n"
                "- Elastic Observability: grew out of the log search stack from Day 47. You can run it yourself or in "
                "Elastic's cloud.\n"
                "- Dynatrace: it pushes hardest on the self-drawn Smartscape map, root cause through dependencies, and "
                "one store with one query language.\n\n"
                "You can learn Dynatrace without paying, in this order:\n"
                "1. The Playground. It is a public sandbox with sample data, so there is nothing to install and no data "
                "to send. Sign-up needs an email address. Use it today and for the DQL part of Day 51.\n"
                "2. The free trial: 15 days of your own SaaS environment. Dynatrace's sign-up page says no credit card "
                "is needed. The clock starts at sign-up, so wait until you are ready for Day 51's hands-on part.\n"
                "3. Optional: during the trial, install the Dynatrace Operator on your kind cluster (Day 51). Kind and "
                "Apple Silicon Macs are not officially supported, so treat it as an experiment that may fail.\n\n"
                f"Both the Playground and the trial start from the [try-free page]({U['try_free']})."
            ),
            "refs": [
                ref("Two ways to get started: Playground and free trial (Dynatrace)", U["try_free"], "read"),
                ref("Dynatrace Intelligence: the agentic AI platform (video)", U["v_intel"], "watch"),
            ],
        },
    ],
    "analogy": (
        "Picture an office building where one water pipe cracks on the fifth floor. Ten rooms below report wet "
        "ceilings, and a simple alarm system gives you ten alarms. Dynatrace is like a building with sensors fitted "
        "in every pipe and an up-to-date plumbing plan. The engineer follows the pipes up from the wet ceilings to "
        "the one cracked joint. OneAgent is the sensors, Smartscape is the plan, and Davis is the engineer. Where it "
        "breaks: real pipes stay put, but services and pods come and go every minute, so the plan is redrawn all the "
        "time. And a pipe without a sensor is invisible to the engineer."
    ),
    "diagram": svg.d50(),
    "diagram_caption": "OneAgent and ActiveGate fill Grail; Davis walks the map and the traces to one root cause.",
    "worked": {
        "title": "One slow checkout, two ways to find it",
        "steps": [
            {
                "say": "Take a made-up shop with three services. `web` calls `checkout`, `checkout` calls `payments`, "
                       "and `payments` uses a Postgres database. At 10:02 the database connection pool fills up, and "
                       "database calls start to wait.",
            },
            {
                "say": "In your Part 9 stack, each symptom fires its own rule within a minute. You get something like the "
                       "list below. Every alert is true, and none of them says which one caused the others.",
                "code": (
                    "FIRING  HighLatency    service=web       p95=2.4s\n"
                    "FIRING  HighLatency    service=checkout  p95=2.3s\n"
                    "FIRING  HighErrorRate  service=checkout  errors=5%\n"
                    "FIRING  HighErrorRate  service=payments  errors=6%"
                ),
                "lang": "text",
            },
            {
                "say": "So you start digging. You open the Grafana RED dashboard and see that all three services went "
                       "bad together. You open Jaeger, find a slow trace and notice the long database span inside "
                       "`payments`. Then you search Kibana for that trace ID. You reach the cause, but it takes three tools.",
            },
            {
                "say": "In Dynatrace, OneAgent already recorded the calls, so Smartscape knows the chain "
                       "web, checkout, payments, database. Davis sees the same symptoms as events, each one measured "
                       "against that service's own baseline.",
            },
            {
                "say": "Davis starts from `web` and follows the call links and the traces downward. The time in the traces "
                       "piles up in the database calls made by `payments`, so the fault tree ends there. It opens one "
                       "problem. The root cause is `payments`, and `web` and `checkout` are listed as affected.",
            },
            {
                "say": "You can read that problem in a Notebook with query A5 from the lab file. On this incident it "
                       "would return one row: an ID like `P-12345`, the category `SLOWDOWN`, and `payments` as the root "
                       "cause. Now remove OneAgent from `payments` in your head. Davis would stop at `checkout`, because it "
                       "cannot follow a call into something nobody instruments.",
                "code": (
                    "fetch dt.davis.problems, from: now() - 2h\n"
                    "| filter not(dt.davis.is_duplicate) and event.status == \"ACTIVE\"\n"
                    "| fields event.start, display_id, event.name, event.category, root_cause_entity_name\n"
                    "| sort event.start desc"
                ),
                "lang": "text",
            },
        ],
    },
    "code": [
        {
            "lang": "text",
            "title": "dynatrace/queries.dql (Day 50 version)",
            "src": QUERIES_D50,
            "run": "Open the Notebooks app in the Playground, add a DQL section, paste one query and run it.",
        }
    ],
    "commands": [
        {"cmd": "mkdir -p dynatrace", "what": "Create the folder for this part's files in your hello-devops repo."},
        {"cmd": "fetch dt.system.data_objects | fields name, display_name, type",
         "what": "DQL: list the kinds of data this environment holds."},
        {"cmd": "smartscapeNodes \"*\" | dedup type | fields type", "what": "DQL: list the entity types in the Smartscape map."},
        {"cmd": "smartscapeNodes \"SERVICE\" | fields name, id", "what": "DQL: list services with their entity IDs."},
        {"cmd": "smartscapeNodes \"HOST\"", "what": "DQL: list the hosts Dynatrace knows about."},
        {"cmd": "smartscapeEdges \"calls\" | limit 20", "what": "DQL: show who calls whom, as edges of the map."},
        {"cmd": "fetch dt.davis.problems, from: now() - 2h | filter event.status == \"ACTIVE\"",
         "what": "DQL: show problems Davis opened in the last 2 hours that are still open."},
        {"cmd": "fetch spans, from: -15m | limit 10", "what": "DQL: look at ten raw spans (pieces of traces) from the last 15 minutes."},
        {"cmd": "git add dynatrace/queries.dql && git commit -m \"Add Dynatrace queries\"",
         "what": "Keep your queries in git, like any other code."},
    ],
    "mistake": (
        "Thinking that automatic discovery means you no longer have to decide what good looks like. Davis compares "
        "each service with its own past, so a service that has always been slow looks normal to it. Write SLOs for the "
        "user journeys that matter (Day 41), and let Davis help you find causes when they break."
    ),
    "real_world": (
        "Picture a payments product with a few hundred microservices. When it breaks at night, the on-call engineer "
        "starts from the problem Davis opened. They check the root cause and the affected services, then open a trace "
        "from the evidence instead of five dashboards. A platform team owns the agents and the cost budget, and each "
        "app team owns its own SLOs."
    ),
    "task": {
        "title": "Tour the Playground and read one problem",
        "steps": [
            "Sign up for the Dynatrace Playground from the try-free page. Do not start the trial yet. Check that the "
            "address ends in `.apps.dynatrace.com`, which means Latest Dynatrace.",
            "Open the Services app and pick one service with traffic. Write down its request rate, failure rate and "
            "response time.",
            "From that service, find the process it runs in and the host under it. Sketch the chain on paper: service, "
            "process, host.",
            "Create `dynatrace/queries.dql` in your hello-devops repo with the Day 50 queries. Run A1 to A4 in a "
            "Notebook and find your service in the A3 result.",
            "Open the Problems app and pick one problem. Write down the root-cause entity, two affected entities and "
            "one piece of evidence.",
            "Open one trace for your service. Find the slowest span and the service that owns it.",
            "Ask Dynatrace Assist to show error logs from the last hour. Read the DQL it writes before you run it, and "
            "note one thing you would change.",
            "Commit `dynatrace/queries.dql`.",
        ],
        "hints": [
            "If an app in the steps is missing, search for its name from the Dynatrace menu, and prefer the one without "
            "\"Classic\" in its name.",
            "Zero rows usually means the time range is too short. Widen the timeframe before you change anything else.",
            "Assist may not be switched on in every environment. If you cannot find it, skip that step.",
        ],
        "done_when": "You have a sketch of service, process and host for one service, a note with one problem's root "
                     "cause, and `dynatrace/queries.dql` committed.",
    },
    "explain_back": {
        "prompt": "Explain to a teammate who knows Prometheus how Dynatrace finds a root cause, in 3 to 4 sentences. "
                  "Mention OneAgent, Smartscape, traces and Davis.",
        "answer": (
            "OneAgent runs on each host or in each pod and records processes, services and every call between them "
            "without code changes. From that, Smartscape keeps a live map of what runs on what and who calls whom. When "
            "metrics leave their baselines, Davis starts at the affected service and follows the map and the traces "
            "downward to the component where the time or the errors start. It opens one problem with that root cause, "
            "where Prometheus would have fired one alert per symptom."
        ),
    },
    "recap": [
        "Dynatrace swaps the eight open-source parts for one SaaS platform, and you pay in money, lock-in and control.",
        "OneAgent instruments hosts and supported processes without code changes; restart apps after you install it.",
        "ActiveGate relays agent traffic and reads APIs such as the Kubernetes API.",
        "Smartscape is a self-drawn map of entities; every signal carries an entity ID, which links them.",
        "Davis groups related anomalies into one problem and walks dependencies to the root cause.",
        "Learn for free in the Playground first; start the 15-day trial only when you are ready for Day 51.",
    ],
    "check": [
        mcq(
            "Your team adds a new Go service with no OneAgent and no OpenTelemetry. It starts failing and slows down "
            "the service that calls it. What is Davis most likely to report?",
            [
                "The Go service as root cause, with full evidence",
                "A slowdown in the caller, with no root cause past it",
                "Nothing, because problems need SLOs to be defined",
                "One separate problem for each slow service",
            ],
            1,
            "Davis can only follow dependencies it can see, so the trail ends at the last instrumented service.",
        ),
        mcq(
            "A 2022 blog post tells you to filter by management zone and to use `dt.entity.service` in DQL. You use "
            "Latest Dynatrace. What do you do?",
            [
                "Switch to Dynatrace Classic to follow the post",
                "Follow it exactly, since the names never change",
                "Ask Assist to turn the post into a dashboard",
                "Use segments and the `dt.smartscape.*` fields",
            ],
            3,
            "Management zones became segments, and `dt.entity.*` fields are deprecated in favour of `dt.smartscape.*`.",
        ),
        mcq(
            "You install OneAgent on a VM where a Java app is already running, and you restart nothing. What do you see?",
            [
                "The host and its processes, but no traces from the app yet",
                "Full traces from the app straight away",
                "Nothing at all until the VM itself reboots",
                "Only logs, because traces need an SDK in the app",
            ],
            0,
            "OneAgent sees the host right away, but it can only add its code module to a process when that process starts.",
        ),
    ],
    "interview": [
        {
            "q": "When would you choose Dynatrace over Prometheus and Grafana?",
            "a": (
                "When the number of services is large enough that nobody can hold the dependency map, and incidents "
                "turn into hunts across many tools. Dynatrace gives you automatic instrumentation, a self-drawn "
                "topology and root-cause analysis in one place, which saves on-call time. The price is a usage-based "
                "licence, lock-in to its agent, queries and dashboards, and telemetry stored on a vendor's servers. "
                "For a small system, or when data must stay on your own servers, the open-source stack is often the "
                "better choice."
            ),
        },
        {
            "q": "What is the difference between an alert and a problem in Dynatrace?",
            "a": (
                "An alert or event says one thing crossed a threshold or left its baseline, for one entity. A problem is "
                "what Davis builds from many such events when they share a root cause. It names the root-cause entity, "
                "lists the affected entities and keeps the evidence. So one incident becomes one problem to work on, "
                "instead of dozens of separate alerts."
            ),
        },
        {
            "q": "How does Dynatrace get traces without code changes, and what are the limits?",
            "a": (
                "OneAgent loads a code module into supported runtimes when a process starts, and the module records "
                "each request, including method and database calls. On Kubernetes, the Operator's webhook adds OneAgent "
                "to pods as they are created. The limits: the runtime must be supported, running processes must be "
                "restarted, and anything uninstrumented is a blind spot. OpenTelemetry data can fill some of those gaps, "
                "because Dynatrace accepts OTLP."
            ),
        },
    ],
    "deeper": {
        "minutes": 12,
        "body": (
            "How does a wobbly metric turn into a problem with a root cause? Dynatrace's own alerting notes describe a "
            "pipeline in four stages.\n\n"
            "1. Something raises an event. Dynatrace lists five kinds of source. There are DQL-based detectors that run on "
            "a schedule, OneAgent itself, and rules on the ingest pipeline. There are also synthetic checks and external "
            "events sent by API or by a workflow.\n"
            "2. Each event is stored in Grail, one per trigger and entity. You can query them with "
            "`fetch dt.davis.events`.\n"
            "3. Events that share the same root cause and impact graph are merged into one problem. Dynatrace calls "
            "this denoising.\n"
            "4. The new problem can trigger a workflow that sends a notification: email, Slack, ServiceNow or a webhook.\n\n"
            "The detectors in step 1 come in three models:\n"
            "- Static threshold: fire above a fixed value. Use it for hard limits, such as an SLO target or a disk "
            "that must stay under 90%.\n"
            "- Adaptive baseline: learn normal from the recent past and fire when the value drifts away. Use it for "
            "metrics with no natural limit, such as request rate.\n"
            "- Seasonal baseline: learn daily and weekly patterns, so a Monday morning peak is not an anomaly.\n\n"
            "Compare this with Alertmanager from Day 44. Alertmanager groups alerts by labels you choose, such as "
            "`service` or `cluster`. That works when the labels match the shape of the incident. Davis groups by the "
            "dependency graph instead. Two alerts on different services land in one problem if one service calls the "
            "other and the traces show the time is spent there. Neither approach reads your mind. Labels need care "
            "from you, and the graph needs instrumentation everywhere.\n\n"
            "Baselines have a trap. A baseline learns whatever happened, including bad behaviour. If a service has "
            "returned 3% errors for a month, 3% is normal to an adaptive model. That is one more reason to keep a "
            "static threshold on the few numbers you promised to users.\n\n"
            "To see which events fire most in an environment, try this in a Notebook: "
            "`fetch dt.davis.events, from: now() - 24h | summarize events = count(), by: {event.name} | sort events desc`. "
            "A long tail of noisy event names is the Dynatrace version of alert fatigue from Day 41."
        ),
    },
    "sources": [
        {"title": "Root cause analysis (Dynatrace docs)", "url": U["rca"]},
        {"title": "Distributed tracing with PurePath (Dynatrace docs)", "url": U["purepath"]},
        {"title": "Capability mapping from Classic to Latest Dynatrace (Dynatrace docs)", "url": U["capability_map"]},
        {"title": "Dynatrace for AI: alerting, problems and DQL skills (Dynatrace, GitHub)", "url": U["dt_for_ai"]},
    ],
}

# ---------------------------------------------------------------- Day 51
d51 = {
    "id": "d51",
    "title": "Dynatrace in practice: Kubernetes, Grail and DQL",
    "minutes": 50,
    "goal": "By the end you can install the Dynatrace Operator and a DynaKube on kind (or say exactly why it failed), "
            "write DQL from fetch to timeseries without SQL habits, and explain how a query becomes an SLO or a release check.",
    "guess": mcq(
        "You know SQL well. Which DQL query counts ERROR log records per Kubernetes namespace?",
        [
            "fetch logs | filter loglevel = \"ERROR\" | summarize count(), by: k8s.namespace.name",
            "SELECT k8s.namespace.name, count(*) FROM logs WHERE loglevel == \"ERROR\"",
            "fetch logs | filter loglevel == \"ERROR\" | summarize n = count(), by: {k8s.namespace.name}",
            "fetch logs | summarize count(), by: {k8s.namespace.name} | filter loglevel == \"ERROR\"",
        ],
        2,
        "DQL compares with `==`, wraps the `by:` list in braces and runs top to bottom, so the filter must come before "
        "the summarize. The first option carries two SQL habits; the last filters on a field that summarize removed.",
    ),
    "terms": [
        {"term": "Dynatrace Operator", "plain": "A Kubernetes operator that installs and updates OneAgent and ActiveGate in a cluster."},
        {"term": "DynaKube", "plain": "The custom resource that tells the Dynatrace Operator what to deploy and where."},
        {"term": "applicationMonitoring", "plain": "The DynaKube mode that puts OneAgent into application pods only, never onto the nodes."},
        {"term": "DQL", "plain": "Dynatrace Query Language: commands joined by `|` that run top to bottom over data in Grail."},
        {"term": "Notebook", "plain": "A Dynatrace app where you write and run DQL step by step and see tables and charts."},
        {"term": "makeTimeseries", "plain": "A DQL command that turns records, such as log lines, into a series you can chart."},
        {"term": "Workflow", "plain": "A Dynatrace automation: a trigger, such as a problem or a schedule, followed by steps."},
        {"term": "Site Reliability Guardian", "plain": "A Dynatrace app that checks a release against objectives and returns pass, warning or fail."},
    ],
    "sections": [
        {
            "h": "Three ways in, and a token for each",
            "body": (
                "Dynatrace only knows what you send it. There are three common ways in:\n"
                "- OneAgent on a VM or server: one installer, then it watches the host and its processes.\n"
                "- The Dynatrace Operator on Kubernetes: it puts OneAgent into the cluster for you.\n"
                "- OpenTelemetry: send OTLP from your own instrumentation or Collector, as on Day 49.\n\n"
                "Each way needs a token, a secret key with a list of permissions called scopes. New environments use "
                "platform tokens, which start with `dt0s16.`. Older ones use access tokens, which start with "
                "`dt0c01.`. Give a token only the scopes its job needs, keep it out of git, and delete it when you are "
                "done. The easiest way to get the right scopes for Kubernetes is to let the trial's onboarding page "
                "create the token, as `dynatrace/README.md` explains.\n\n"
                "Your environment ID is the first part of your address: in `https://abc12345.apps.dynatrace.com` it is "
                "`abc12345`. People use the `.apps.` address in the browser. Agents and APIs use "
                "`https://abc12345.live.dynatrace.com`. Mixing them up is a classic cause of 404 errors."
            ),
            "refs": [
                ref("From access tokens to platform tokens (Dynatrace docs)", U["tokens_upgrade"], "docs"),
                ref("QuickStart app and the free trial (Dynatrace blog)", U["quickstart_blog"], "read"),
            ],
        },
        {
            "h": "The Operator and the DynaKube on kind",
            "body": (
                "On Day 44 you met an operator: a controller that runs software for you, driven by a custom resource. "
                "The Dynatrace Operator works the same way. You install it once with Helm, then write a "
                "**DynaKube**, the custom resource that says what you want. Its biggest choice is the mode:\n"
                "- `cloudNativeFullStack`: OneAgent in app pods and on every node. Dynatrace recommends it for normal "
                "clusters. It needs a CSI driver, a storage plugin that runs on each node.\n"
                "- `applicationMonitoring`: OneAgent in app pods only, added by a webhook as each pod starts. It is the "
                "only choice where you cannot touch the nodes, such as EKS Fargate.\n"
                "- `hostMonitoring`: the nodes only.\n"
                "- `classicFullStack`: the older style, still supported but no longer recommended.\n\n"
                "The lab's `dynatrace/dynakube.yaml` uses `applicationMonitoring`. Kind nodes are Docker containers on "
                "your Mac, and a node agent expects a real Linux host underneath, so app-only injection is the safer "
                "bet. The file adds one ActiveGate with `routing` and `kubernetes-monitoring` and only injects into "
                "namespaces labelled `monitoring: dynatrace`. The official sample asks 6Gi of memory for the "
                "ActiveGate, which would leave the pod Pending on Docker Desktop. The lab asks for 512Mi, like "
                "Dynatrace's own setup examples.\n\n"
                "A few minutes after you apply it and restart hello-devops, you should see:\n"
                "- `Running` from `kubectl -n dynatrace get dynakube` (`Deploying` first, `Error` if something is wrong)\n"
                "- the operator, webhook and `dynakube-activegate-0` pods in the `dynatrace` namespace\n"
                "- an extra init container called `dynatrace-operator` in each new hello-devops pod (old pods never get one)\n"
                "- a cluster called `kind-devops` in the Kubernetes app, with nodes, namespaces, workloads and events\n"
                "- hello-devops in the Services app, if OneAgent can instrument your Python version\n\n"
                "Dynatrace does not list kind or Apple Silicon Macs as supported. The images "
                "exist for arm64, and Dynatrace tests its Operator on kind (on Linux machines), so it may work. If it "
                "does not, the README lists the usual causes, and the trial with Dynatrace's Codespaces lab is the "
                "fallback."
            ),
            "refs": [
                ref("Set up Dynatrace on Kubernetes: deployment options (Dynatrace docs)", U["k8s_deploy"], "docs"),
                ref("The official applicationMonitoring sample, v1.11.1 (GitHub)", U["appmon_sample"], "read"),
                ref("DynaKube parameters reference (Dynatrace docs)", U["dynakube_params"], "docs"),
            ],
        },
        {
            "h": "Grail and the shape of a DQL query",
            "body": (
                "Grail is the store behind everything. It keeps logs, spans, events, problems and metrics side by side, "
                "and you read all of it with **DQL**, the Dynatrace Query Language.\n\n"
                "A DQL query is a pipeline, like the shell pipelines from Day 5. The first command produces records. Each "
                "`|` hands them to the next command, which filters, reshapes or counts them. You read it top to bottom, "
                "in the order it runs. That is the biggest change if you think in SQL, where SELECT comes first and the "
                "database picks the order.\n\n"
                "The first command decides what kind of data you get:\n"
                "- `fetch logs`, `fetch spans`, `fetch events`, `fetch dt.davis.problems`: records, one row per log "
                "line, span or event\n"
                "- `timeseries`: stored metrics, as series of numbers over time\n"
                "- `smartscapeNodes` and `smartscapeEdges`: the topology map\n"
                "- `data`: a small table you type into the query, good for practice\n\n"
                "Every query also has a timeframe. The Notebook has a time picker, and you can set it in the query "
                "with `from:` and `to:`, as in `fetch logs, from: -1h`. Use the shortest window that answers the "
                "question. Grail charges queries by the data they scan, so `from: -30d` over all logs costs real "
                "money on a paid environment. `fetch` also takes `scanLimitGBytes:` as a safety cap.\n\n"
                "You will write DQL in a Notebook. Add a section, choose DQL, type, run. The result appears as a table "
                "or a chart under the query. When a query is worth keeping, pin it to a dashboard or save it in "
                "`dynatrace/queries.dql`."
            ),
            "refs": [
                ref("How to use DQL queries (Dynatrace docs)", U["dql_use"], "docs"),
                ref("Query your data in DQL: the fetch command (video)", U["v_dql_query"], "watch"),
            ],
        },
        {
            "h": "A DQL ladder, one command at a time",
            "body": (
                "Climb this ladder in a Notebook, one rung per run. Each rung is in `dynatrace/queries.dql`, part C.\n\n"
                "1. `fetch logs, from: -1h | limit 10` returns ten raw log records. Read the field names; you need them "
                "for every later rung.\n"
                "2. Add `| filter loglevel == \"ERROR\"`. Only error records stay. The severity field is `loglevel` and "
                "the message is `content`.\n"
                "3. Add `| fields timestamp, loglevel, content`. Same rows, now three columns.\n"
                "4. Swap that line for `| summarize errors = count(), by: {k8s.namespace.name}`. You get one row per "
                "namespace with a count, like GROUP BY in SQL.\n"
                "5. Add `| sort errors desc`. Biggest first.\n"
                "6. Swap summarize for `| makeTimeseries {total = count(), errors = countIf(loglevel == \"ERROR\")}, "
                "interval: 5m`. You get one row whose fields are arrays with one value per 5 minutes. The Notebook "
                "draws them as lines.\n"
                "7. Metrics have their own first command. `timeseries requests = sum(dt.service.request.count), by: "
                "{dt.service.name}` returns one series per service.\n\n"
                "Two details make rungs 6 and 7 click. A series is an array, so math on every point uses `[]`: "
                "`errors[] * 100.0 / total[]` gives an error percentage for each 5-minute slot. To squash a series "
                "into one number, use an array function such as `arrayAvg(cpu)` or `arrayMax(cpu)`.\n\n"
                "Traces work the same way with `fetch spans`. Query C6 counts requests and failures and takes the p95 "
                "duration per service in one `summarize`. That is the RED method from Day 41 in a few lines. On Day 43 "
                "you built RED from counters the app had already counted. Here you count the span records yourself."
            ),
            "refs": [
                ref("Aggregation commands: summarize and makeTimeseries (Dynatrace docs)", U["dql_agg"], "docs"),
                ref("Query your metrics in DQL: the timeseries command (video)", U["v_dql_metrics"], "watch"),
            ],
        },
        {
            "h": "SQL habits that break in DQL",
            "body": (
                "These trip up almost everyone who knows SQL. The worst part is that several of them do not fail. They "
                "quietly return zero rows, and zero rows looks like \"no errors\".\n"
                "- Equality is `==`. A single `=` gives a field a name, as in `errors = count()`.\n"
                "- A list in `by:` needs braces: `by: {a, b}`, never `by: a, b`.\n"
                "- Order matters. After `summarize`, only the summarized fields exist, so filter first.\n"
                "- Metric values come from `timeseries`. There is no `fetch` for them.\n"
                "- Name an aggregate before you sort by it: `summarize n = count() | sort n desc`. `sort count() desc` fails.\n"
                "- A fixed list uses braces: `in(loglevel, {\"ERROR\", \"WARN\"})`. Square brackets hold a subquery.\n"
                "- Field names are not guessable. It is `loglevel`, not `log.level`, and spans have `start_time`, not "
                "`timestamp`.\n"
                "- Do not wrap a field in `lower()` to compare it. Write `contains(content, \"timeout\", caseSensitive: "
                "false)`. `lower()` stops Grail from using its index, so it scans far more data.\n\n"
                "When a query returns nothing, check the field names and the operators before you decide nothing "
                f"happened. Dynatrace keeps a [comparison of DQL and SQL]({U['dql_compare']}) side by side."
            ),
            "refs": [
                ref("DQL compared to SQL and more (Dynatrace docs)", U["dql_compare"], "docs"),
                ref("DQL best practices (Dynatrace docs)", U["dql_best"], "docs"),
                ref("A practical guide to DQL (video)", U["v_dql_guide"], "watch"),
            ],
        },
        {
            "h": "From queries to action: SLOs, workflows and release checks",
            "body": (
                "A query you run by hand helps once. These features run it without you.\n\n"
                "An SLO in Dynatrace is a query plus a target. You decide the promise: say, 99.5% of hello-devops "
                "requests succeed in under 3 seconds over 28 days. Query C9 in the lab file computes that kind of "
                "number from spans. The Service-Level Objectives app stores the definition and evaluates it over time "
                "against your target. The error budget idea from Day 41 applies unchanged.\n\n"
                "A workflow is \"when this happens, do these steps\". Workflows run on Dynatrace's AutomationEngine. "
                "The trigger can be a schedule, an event or a problem. The steps can send email or a Slack message, "
                "call a webhook, or run a guardian. This is also how problems reach people: a problem opens, and a "
                "workflow routes it to the right team.\n\n"
                "Site Reliability Guardian (SRG) is a release gate built from objectives. It fits the pipelines from "
                "Part 4:\n"
                "1. The pipeline deploys a new version and runs a load test.\n"
                "2. It sends an event to Dynatrace: version 1.4.0 of checkout was tested.\n"
                "3. A workflow triggered by that event runs the guardian over the test's time window.\n"
                "4. The guardian checks each objective, such as error rate and p95 latency, and returns pass, warning "
                "or fail.\n"
                "5. The pipeline reads the result and promotes the release or stops it.\n\n"
                "Dynatrace has ready integrations for GitHub Actions, GitLab, Azure DevOps and Argo CD. Its Codespaces "
                "lab walks through this whole flow, including a release that fails the gate.\n\n"
                "OpenTelemetry fits in as well. Dynatrace accepts OTLP over HTTP at "
                "`https://<env-id>.live.dynatrace.com/api/v2/otlp`. The hello-devops setup from Day 49 can send its "
                "traces there by changing environment variables only. Go deeper shows how."
            ),
            "refs": [
                ref("Release validation with Site Reliability Guardian (Dynatrace docs)", U["srg_docs"], "docs"),
                ref("Release validation for DevOps engineers with SRG (Dynatrace video)", U["v_srg"], "watch"),
                ref("Release validation lab in GitHub Codespaces (Dynatrace, GitHub)", U["obslab"], "read"),
            ],
        },
        {
            "h": "Cost, the trial's limits and what to learn next",
            "body": (
                "Dynatrace sells the Dynatrace Platform Subscription (DPS). You commit to a yearly amount, and usage "
                "draws it down against a rate card. Use more and you pay the extra at the same rates. Almost "
                "everything is metered:\n"
                "- monitoring time for hosts, pods and other entities\n"
                "- data you send in, such as GiB of logs\n"
                "- how long you keep data\n"
                "- data your queries scan\n\n"
                "No prices here. The public rate card changes, and each company's contract sets its own rates. Keep "
                "the idea instead: in Dynatrace, a careless query over a month of logs costs money, just as shipping "
                "every debug line does. Query D3 in the lab file lists the billing usage events your environment "
                "records.\n\n"
                "The trial is the place to learn this without risk. It lasts 15 days from sign-up, and Dynatrace does "
                "not publish all of its limits in a place this course could check. Plan your hands-on time before you "
                "start it.\n\n"
                "To keep learning:\n"
                f"- [Dynatrace University]({U['university']}) is the official training site.\n"
                "- The Dynatrace Associate certification is the entry-level exam. Third-party sites describe a paid, "
                "online, proctored exam, but check Dynatrace University for the official price and format.\n"
                "- The open-source [Dynatrace for AI]({0}) skills include a compact list of DQL pitfalls, and "
                "`dtctl` runs DQL from your terminal.".format(U["dt_for_ai"])
            ),
            "refs": [
                ref("How pricing works (Dynatrace docs)", U["pricing"], "docs"),
                ref("Dynatrace pricing FAQ (Dynatrace)", U["pricing_faq"], "read"),
                ref("Dynatrace University (Dynatrace)", U["university"], "read"),
            ],
        },
    ],
    "analogy": (
        "A DQL query works like a sorting line in a post office. The first station empties one sack onto the belt "
        "(`fetch logs`). Each later station does one job: drop letters for other cities (`filter`), keep only the "
        "address label (`fields`), or sort letters into one bin per street and count them (`summarize`). A station "
        "only sees what the one before it passed on, so swapping two stations changes the result. Where it breaks: a "
        "post office pays per letter handled, but Grail charges by how much the first station has to scan. A narrow "
        "time window at the start matters more than anything later on the belt."
    ),
    "diagram": svg.d51(),
    "diagram_caption": "The Operator turns your DynaKube into a webhook and an ActiveGate; data lands in Grail, and you read it with DQL.",
    "worked": {
        "title": "DQL from zero on a table you type",
        "steps": [
            {
                "say": "Open a Notebook (the Playground is fine), add a DQL section and run query B1. The `data` command "
                       "builds a six-row table inside the query. Everyone gets the same result, and Grail scans nothing.",
                "code": (
                    "data record(path = \"/\", status = 200, ms = 12),\n"
                    "     record(path = \"/\", status = 200, ms = 18),\n"
                    "     record(path = \"/\", status = 200, ms = 20),\n"
                    "     record(path = \"/\", status = 500, ms = 350),\n"
                    "     record(path = \"/healthz\", status = 200, ms = 2),\n"
                    "     record(path = \"/readyz\", status = 503, ms = 1001)\n\n"
                    "Result: 6 rows with the columns path, status, ms."
                ),
                "lang": "text",
            },
            {
                "say": "Add a filter on a new line. Records flow down the pipe, and `filter` keeps the ones where the "
                       "condition is true. Note the `>=`; equality would be `==`.",
                "code": (
                    "| filter status >= 500\n\n"
                    "path      status  ms\n"
                    "/         500     350\n"
                    "/readyz   503     1001"
                ),
                "lang": "text",
            },
            {
                "say": "Replace the filter with a summarize. It groups the records by `path` and computes one row per "
                       "group. Each result gets a name with a single `=`, and the `by:` list sits in braces. The rows can "
                       "come back in any order until you sort them.",
                "code": (
                    "| summarize requests = count(), errors = countIf(status >= 500),\n"
                    "            avg_ms = avg(ms), by: {path}\n\n"
                    "path      requests  errors  avg_ms\n"
                    "/         4         1       100\n"
                    "/healthz  1         0       2\n"
                    "/readyz   1         1       1001"
                ),
                "lang": "text",
            },
            {
                "say": "Add a computed field and sort by it. `fieldsAdd` keeps every column and adds one. Sort by the "
                       "name you gave the field, not by an expression.",
                "code": (
                    "| fieldsAdd error_pct = errors * 100.0 / requests\n"
                    "| sort error_pct desc\n\n"
                    "path      requests  errors  avg_ms  error_pct\n"
                    "/readyz   1         1       1001    100\n"
                    "/         4         1       100     25\n"
                    "/healthz  1         0       2       0"
                ),
                "lang": "text",
            },
            {
                "say": "Now make two SQL mistakes on purpose, one at a time, and read the messages. Both runs fail. The "
                       "first uses `=` where DQL wants a true or false test. In the second, `by:` without braces takes "
                       "only `path`, and `status` is read as one more aggregation, which it is not.",
                "code": (
                    "| filter status = 500\n"
                    "| summarize requests = count(), by: path, status"
                ),
                "lang": "text",
            },
            {
                "say": "Put `fetch logs, from: -1h` where `data` was, and the same commands work on real logs. Only the "
                       "first line changed. The commands below it do not care where the records came from.",
            },
        ],
    },
    "code": [
        {
            "lang": "yaml",
            "title": "dynatrace/dynakube.yaml",
            "src": DYNAKUBE,
            "run": SED_DRY,
        },
        {
            "lang": "text",
            "title": "dynatrace/queries.dql (final version)",
            "src": QUERIES,
            "run": "Open the Notebooks app, add a DQL section, paste one query and run it. Part D needs your trial.",
        },
    ],
    "commands": [
        {"cmd": "read -rs DT_API_TOKEN && export DT_API_TOKEN",
         "what": "Paste a token into a variable without showing it or saving it in your shell history."},
        {"cmd": HELM, "what": "Install the Dynatrace Operator from its OCI Helm chart, without the CSI driver, and roll back if it fails."},
        {"cmd": SECRET, "what": "Create the `dynakube` secret from your tokens without putting them on the command line."},
        {"cmd": "kubectl label namespace hello monitoring=dynatrace", "what": "Opt the hello namespace in to OneAgent injection."},
        {"cmd": SED_DRY, "what": "Fill in your environment ID and let the Operator's webhook check the DynaKube without saving it."},
        {"cmd": SED_APPLY, "what": "Apply the DynaKube for real."},
        {"cmd": "kubectl -n hello rollout restart deployment/hello-devops", "what": "Start new pods so the webhook can add OneAgent to them."},
        {"cmd": "kubectl -n dynatrace get dynakube", "what": "Show the DynaKube's status: Deploying, Running or Error."},
        {"cmd": "kubectl -n dynatrace get pods", "what": "List the operator, webhook and ActiveGate pods."},
        {"cmd": "kubectl -n dynatrace logs deploy/dynatrace-operator", "what": "Read the Operator's log when the DynaKube shows an error."},
        {"cmd": "kubectl -n dynatrace delete dynakube --all", "what": "First uninstall step: let the Operator remove what it created."},
        {"cmd": "helm uninstall dynatrace-operator -n dynatrace", "what": "Remove the Operator after the DynaKube is gone."},
        {"cmd": "brew install dynatrace-oss/tap/dtctl", "what": "Install dtctl, Dynatrace's command-line tool for SaaS environments."},
        {"cmd": "dtctl auth login --context trial --environment \"https://$DT_ENV_ID.apps.dynatrace.com\"",
         "what": "Log dtctl in to your trial environment in the browser."},
        {"cmd": "dtctl query \"fetch logs | limit 10\"", "what": "Run a DQL query from the terminal."},
    ],
    "mistake": (
        "Trusting an empty result. `filter log.level == \"ERROR\"` runs without complaint and returns nothing, because "
        "the field is called `loglevel`. Start each new query with `limit 10` to see the real field names, then add one "
        "command at a time and check the row count after each."
    ),
    "real_world": (
        "In a payments product running many clusters, a platform team keeps one DynaKube per cluster in git, and Argo "
        "CD applies it. App teams opt in by labelling their namespaces. Release pipelines send a deployment event and "
        "wait for the guardian's verdict before they promote a build, and someone reviews the billing usage query "
        "every week."
    ),
    "task": {
        "title": "Monitor hello-devops on kind, or practise DQL in the Playground",
        "steps": [
            "Choose your path. If you will not start the trial now, do steps 6 and 7 in the Playground and skip the rest.",
            "Start the 15-day trial, note your environment ID, and get a token as step 1 of `dynatrace/README.md` explains.",
            "Install the Operator with Helm and create the `dynakube` secret (README steps 2 and 3).",
            "Label the `hello` namespace, dry-run the DynaKube, apply it and restart hello-devops (README step 4).",
            "Check that the DynaKube shows `Running` and that a new hello-devops pod has the `dynatrace-operator` init "
            "container. Send traffic with `curl localhost:8081` a few times.",
            "In a Notebook, climb rungs C1 to C7 from `dynatrace/queries.dql`. Write one line per rung on what it returned.",
            "Break one query with each SQL habit from this lesson. Note which ones fail with an error and which return "
            "zero rows.",
            "Run D1 and D2 and find `kind-devops` and hello-devops in the results.",
            "Uninstall in the README's order, then delete the token in Dynatrace.",
        ],
        "hints": [
            "If `dynakube-activegate-0` stays Pending, describe the pod. An insufficient memory message means Docker "
            "Desktop needs more memory.",
            "Zero rows on your own data? Check the time picker first, because your data is only minutes old.",
            "If the install fails on your Mac, write down the exact error. That is a known risk, and the Codespaces lab "
            "runs on Linux machines instead.",
        ],
        "done_when": "You have one note line per ladder rung, and either `smartscapeNodes \"K8S_CLUSTER\"` lists "
                     "`kind-devops` or you have written down the exact error that stopped the install.",
    },
    "explain_back": {
        "prompt": "Explain how DQL differs from SQL to a teammate who writes SQL every day, in 3 to 4 sentences. "
                  "Mention the pipeline order, fetch versus timeseries, and two syntax traps.",
        "answer": (
            "A DQL query starts from a source and runs top to bottom: each `|` passes the records to the next command, "
            "so you filter before you summarize. Records such as logs and spans come from `fetch`, while stored metrics "
            "come from `timeseries`, never from `fetch`. Equality is `==` because a single `=` names a field, and a "
            "`by:` list needs braces. Many mistakes return zero rows instead of an error, so check field names with "
            "`limit 10` first."
        ),
    },
    "recap": [
        "The Dynatrace Operator reads a DynaKube; for kind, use applicationMonitoring with a small ActiveGate.",
        "Kind and Apple Silicon are not officially supported, so the local install may fail; the Playground always works.",
        "DQL runs top to bottom: fetch, filter, fields, summarize, sort, with makeTimeseries for charts.",
        "Metrics come from timeseries; `==` compares; `by:` lists need braces; empty results often mean a wrong field name.",
        "SLOs, workflows and Site Reliability Guardian turn queries into targets, automation and release gates.",
        "Ingest, retention and query scans are all metered, so keep time windows short and filter early.",
    ],
    "check": [
        mcq(
            "You need the average CPU per host over the last hour. Which query starts the right way?",
            [
                "fetch dt.host.cpu.usage | summarize avg(value)",
                "timeseries avg(dt.host.cpu.usage), by: {dt.smartscape.host}",
                "fetch logs | filter metric == \"cpu\" | summarize avg()",
                "smartscapeNodes \"HOST\" | summarize avg(cpu.usage)",
            ],
            1,
            "Metric values are read with `timeseries`; there is no `fetch` for them.",
        ),
        mcq(
            "Your company runs its pods on EKS Fargate, where you cannot run anything on the nodes. Which DynaKube mode fits?",
            [
                "cloudNativeFullStack",
                "classicFullStack",
                "hostMonitoring",
                "applicationMonitoring",
            ],
            3,
            "Only app-only injection works where the nodes are off-limits; the other modes need an agent on each node.",
        ),
        mcq(
            "A query `fetch logs, from: -30d | filter contains(lower(content), \"refund\")` is slow and costly. What "
            "is the best first change?",
            [
                "Shorten the window and use caseSensitive: false",
                "Add `| limit 10` at the very end of the query",
                "Move the filter so it runs after a summarize",
                "Switch the first command to `fetch spans`",
            ],
            0,
            "The cost comes from scanning: a shorter window scans less, and dropping `lower()` lets Grail use its index.",
        ),
    ],
    "interview": [
        {
            "q": "How would you roll out Dynatrace to a Kubernetes cluster?",
            "a": (
                "Install the Dynatrace Operator with its Helm chart, create a secret with a scoped token, and apply a "
                "DynaKube that picks the mode and the ActiveGate capabilities. On normal nodes I would use "
                "cloudNativeFullStack, which Dynatrace recommends. Where nodes are off-limits, such as Fargate, I would "
                "use applicationMonitoring. I would keep the DynaKube in git, let teams opt in with a namespace label, "
                "and restart workloads so the webhook can inject OneAgent."
            ),
        },
        {
            "q": "What is the difference between fetch, timeseries and makeTimeseries in DQL?",
            "a": (
                "The `fetch` command reads records such as logs, spans and events, one row per record. The `timeseries` "
                "command reads stored metrics and returns arrays of values over time. The `makeTimeseries` command sits "
                "later in a pipeline and turns fetched records into a series, for example error logs per 5 minutes. So "
                "metrics start with `timeseries`, and counts from records end with `makeTimeseries` when you want a chart."
            ),
        },
        {
            "q": "How can Dynatrace act as a quality gate in a CI/CD pipeline?",
            "a": (
                "The pipeline deploys to a test environment, runs a load test and sends an event to Dynatrace. A "
                "workflow triggered by that event runs a Site Reliability Guardian over the test window. The guardian "
                "checks objectives such as error rate and p95 latency and returns pass, warning or fail. The pipeline "
                "reads that result and promotes the build or stops it, so the decision rests on measured behaviour."
            ),
        },
    ],
    "deeper": {
        "minutes": 13,
        "body": (
            "You do not need OneAgent to get traces into Dynatrace. On Day 49 you ran hello-devops under "
            "`opentelemetry-instrument` and sent the spans to a Collector and Jaeger. Point the same run at "
            "Dynatrace by setting these environment variables first:\n"
            "- `OTEL_SERVICE_NAME=hello-devops`\n"
            "- `OTEL_EXPORTER_OTLP_ENDPOINT=https://<env-id>.live.dynatrace.com/api/v2/otlp`\n"
            "- `OTEL_EXPORTER_OTLP_PROTOCOL=http/protobuf`\n"
            "- `OTEL_EXPORTER_OTLP_HEADERS=Authorization=Api-Token%20<token>` for an access token, or "
            "`Authorization=Bearer%20<token>` for a platform token\n"
            "- `OTEL_EXPORTER_OTLP_METRICS_TEMPORALITY_PREFERENCE=delta`\n\n"
            "The endpoint uses `.live.`, not `.apps.`. Dynatrace's docs warn that the `.apps` form returns 404 errors. "
            "The SDK adds the signal path, such as `/v1/traces`, by itself.\n\n"
            "The protocol is OTLP over HTTP with binary protobuf, which is what the Dynatrace docs show for this "
            "endpoint.\n\n"
            "The header value contains a space, and an environment variable for OTLP headers should encode it as `%20`. "
            "The OpenTelemetry Python SDK decodes that back to a space. Which word comes first depends on the token: "
            "`Api-Token` for tokens that start with `dt0c01.`, `Bearer` for tokens that start with `dt0s16.`. The "
            "token needs ingest scopes for the signals you send, and nothing more.\n\n"
            "The temporality line matters if you also send metrics. Prometheus counters from Day 42 are cumulative: "
            "they only go up, and the server works out the change. Dynatrace's OTLP endpoint only accepts deltas, the "
            "change since the last export, so the SDK must send them. Without that setting, Dynatrace rejects cumulative "
            "points. If an SDK ignores the variable, set the temporality in code or let a Collector convert it.\n\n"
            "You can keep your Collector from Day 49 too. Add a second exporter of type `otlphttp` with the same "
            "endpoint and header, and list both exporters in the traces pipeline. Now every span goes to Jaeger and "
            "to Dynatrace at once. That is a cheap way to compare the two views of the same request.\n\n"
            "On Kubernetes, the Operator can do this wiring for you. A DynaKube can run a Dynatrace build of the "
            "OpenTelemetry Collector (`telemetryIngest`) and can set the OTLP variables in your pods "
            "(`otlpExporterConfiguration`). Both have samples in the Operator's repo.\n\n"
            "Then, in a Notebook: `fetch spans, from: -15m | filter service.name == \"hello-devops\" | limit 20`. "
            "OpenTelemetry spans and OneAgent spans sit in the same table, so every query from this lesson works on both."
        ),
    },
    "sources": [
        {"title": "Dynatrace Operator: code, DynaKube samples and releases (GitHub)", "url": U["operator_gh"]},
        {"title": "How to use DQL queries (Dynatrace docs)", "url": U["dql_use"]},
        {"title": "Dynatrace OTLP API endpoints (Dynatrace docs)", "url": U["otlp"]},
        {"title": "Release validation with Site Reliability Guardian (Dynatrace docs)", "url": U["srg_docs"]},
    ],
}

# ---------------------------------------------------------------- Part
part = {
    "part": 12,
    "title": "Dynatrace",
    "intro": (
        "In Parts 9 to 11 you assembled observability from open-source parts. Dynatrace is the commercial, all-in-one "
        "version: one agent collects the data, one store keeps every signal, and one query language reads it. Day 50 "
        "explains how it thinks, in a free sandbox. Day 51 gets your own data in and teaches DQL from zero."
    ),
    "lessons": [d50, d51],
    "recap": [
        "Dynatrace is a SaaS observability platform: one agent, one store (Grail), one query language (DQL).",
        "OneAgent instruments hosts and supported processes without code changes; ActiveGate relays data and reads APIs.",
        "Smartscape is a self-drawn map of entities, and every signal carries an entity ID.",
        "Davis turns many related anomalies into one problem by walking dependencies and traces.",
        "Latest Dynatrace lives at <id>.apps.dynatrace.com; agents and APIs use <id>.live.dynatrace.com.",
        "On kind, the lab uses an applicationMonitoring DynaKube with a small ActiveGate, and it may fail on a Mac.",
        "DQL runs top to bottom; metrics come from timeseries, and SQL habits often return zero rows silently.",
        "Ingest, retention and query scans all cost money after the trial; learn in the Playground first.",
    ],
    "flashcards": [
        {"front": "What does OneAgent do?", "back": "It finds processes on a host or in a pod and records metrics, logs and traces without code changes."},
        {"front": "What is ActiveGate for?", "back": "It relays agent traffic to Dynatrace and reads APIs such as the Kubernetes API."},
        {"front": "What is Smartscape?", "back": "The live map of entities and how they depend on each other, drawn from what OneAgent sees."},
        {"front": "What is a PurePath?", "back": "A trace recorded by OneAgent, down to method and database calls."},
        {"front": "How does Davis find a root cause?", "back": "It follows dependencies and traces from the affected entity, then runs a fault-tree analysis."},
        {"front": "What is Dynatrace Assist?", "back": "The chat assistant in Dynatrace Intelligence that replaced Davis CoPilot; it can write DQL."},
        {"front": "Which address is the web UI, and which do agents and APIs use?", "back": "UI: <id>.apps.dynatrace.com. Agents and APIs: <id>.live.dynatrace.com."},
        {"front": "Which DynaKube mode does the course use on kind?", "back": "applicationMonitoring, with one small ActiveGate."},
        {"front": "Why restart pods after applying a DynaKube?", "back": "The webhook adds OneAgent only when a pod is created."},
        {"front": "What does a token starting with dt0s16. mean?", "back": "It is a platform token, the kind new Dynatrace environments use."},
        {"front": "How do you compare for equality in DQL?", "back": "With ==. A single = gives a field a name."},
        {"front": "How do you group by two fields in DQL?", "back": "summarize ..., by: {field1, field2}, with braces."},
        {"front": "How do you read metric values in DQL?", "back": "With timeseries, never with fetch."},
        {"front": "What does makeTimeseries do?", "back": "It turns records, such as logs, into a series you can chart."},
        {"front": "What do DQL queries cost on a paid environment?", "back": "They are billed by data scanned, so short windows and early filters save money."},
        {"front": "What is Site Reliability Guardian?", "back": "A release gate that checks objectives and returns pass, warning or fail."},
    ],
    "resources": [
        {"title": "Two ways to get started: Playground and free trial (Dynatrace)", "url": U["try_free"], "kind": "read",
         "why": "The entry point for the free sandbox and the 15-day trial, with the current terms."},
        {"title": "Get started with Dynatrace (Dynatrace docs)", "url": U["get_started"], "kind": "docs",
         "why": "The official starting point for the platform's apps and concepts."},
        {"title": "How to use DQL queries (Dynatrace docs)", "url": U["dql_use"], "kind": "docs",
         "why": "The official walk through fetch, filter, summarize and friends."},
        {"title": "DQL compared to SQL and more (Dynatrace docs)", "url": U["dql_compare"], "kind": "docs",
         "why": "Side-by-side examples for when your SQL habits get in the way."},
        {"title": "Dynatrace for AI skills (Dynatrace, GitHub)", "url": U["dt_for_ai"], "kind": "read",
         "why": "Dynatrace's own compact notes on DQL pitfalls, problems, Kubernetes and costs."},
        {"title": "Dynatrace Operator (GitHub)", "url": U["operator_gh"], "kind": "docs",
         "why": "The source, the DynaKube samples for every mode, and the release notes."},
        {"title": "Release validation lab in GitHub Codespaces (Dynatrace, GitHub)", "url": U["obslab"], "kind": "read",
         "why": "A guided trial lab that runs on GitHub's machines, so your Mac's chip does not matter."},
        {"title": "Release validation for DevOps engineers with SRG (Dynatrace video)", "url": U["v_srg"], "kind": "watch",
         "why": "The overview video for that lab: a release gate that fails, and why."},
        {"title": "A practical guide to DQL (video)", "url": U["v_dql_guide"], "kind": "watch",
         "why": "A longer DQL walk-through to watch after the ladder in Day 51."},
        {"title": "How to get started with Dynatrace Assist (video)", "url": U["v_assist"], "kind": "watch",
         "why": "Shows the chat assistant writing and explaining DQL."},
        {"title": "Dynatrace University (Dynatrace)", "url": U["university"], "kind": "read",
         "why": "Official courses and the path to the Associate certification."},
        {"title": "dtctl, the Dynatrace command line (GitHub)", "url": U["dtctl"], "kind": "read",
         "why": "Run DQL and manage workflows and dashboards from your terminal, kubectl style."},
    ],
    "quiz": [
        mcq(
            "Which part of Dynatrace keeps the live map of which service calls which, and what runs on what?",
            ["Grail", "Smartscape", "ActiveGate", "Dynatrace Assist"],
            1,
            "Smartscape is the self-drawn topology map; Grail stores the data, and ActiveGate relays it.",
        ),
        mcq(
            "In the course's DynaKube, what does the ActiveGate's `kubernetes-monitoring` capability do?",
            [
                "It injects OneAgent into every pod in the cluster",
                "It reads nodes, workloads and events from the Kubernetes API",
                "It replaces kube-proxy with a faster version",
                "It stores the cluster's logs inside the cluster",
            ],
            1,
            "The webhook injects OneAgent; the ActiveGate reads the Kubernetes API and relays data to Dynatrace.",
        ),
        mcq(
            "During an incident, Alertmanager would send 30 notifications. What does Davis aim to give you instead?",
            [
                "30 alerts sorted by how fast each metric rose",
                "A dashboard with one panel per alert",
                "One problem that names the root cause",
                "A daily summary email of all anomalies",
            ],
            2,
            "Davis merges events that share a root cause and impact into one problem.",
        ),
        mcq(
            "Your DynaKube has `apiUrl: https://abc12345.apps.dynatrace.com/api` and the Operator cannot connect. What "
            "is the most likely fix?",
            [
                "Use https://abc12345.live.dynatrace.com/api instead",
                "Remove the /api suffix from the address",
                "Add a second ActiveGate with the routing capability",
                "Switch the mode to cloudNativeFullStack",
            ],
            0,
            "The `.apps.` address is for the web UI; agents and APIs use `.live.dynatrace.com/api`.",
        ),
        mcq(
            "Which DQL query draws ERROR logs as a line over the last two hours?",
            [
                "fetch logs, from: -2h | summarize n = count(), by: {loglevel}",
                "timeseries errors = count(logs), filter: loglevel == \"ERROR\"",
                "fetch logs, from: -2h | sort timestamp desc | limit 120",
                "fetch logs, from: -2h | makeTimeseries n = countIf(loglevel == \"ERROR\")",
            ],
            3,
            "makeTimeseries turns fetched records into a series; timeseries only reads stored metrics.",
        ),
        mcq(
            "On a Dynatrace Platform Subscription, which of these costs money?",
            [
                "Only the hosts and pods that run OneAgent",
                "Only the logs and traces that you send in",
                "Monitoring, ingest, retention and query scans",
                "Nothing, while your queries stay under 1 GB",
            ],
            2,
            "DPS meters monitoring time, ingest, retention and query scans; the Playground is a separate free sandbox.",
        ),
        mcq(
            "You want to learn Dynatrace for free with the least risk. What order makes sense?",
            [
                "Playground, then the 15-day trial, then the optional kind install",
                "Trial first, then the Playground once the trial ends",
                "Kind install first, then the Playground to check it",
                "Buy a small subscription, then try the Playground",
            ],
            0,
            "The Playground needs no install and has no clock; start the 15-day trial only when you are ready to use it.",
        ),
        mcq(
            "How does Site Reliability Guardian fit into a release pipeline?",
            [
                "It replaces GitHub Actions as the CI system",
                "It builds and signs the container image for you",
                "It deploys the new release to the Kubernetes cluster",
                "It checks objectives and returns pass, warning or fail",
            ],
            3,
            "The pipeline sends an event, a workflow runs the guardian, and the pipeline acts on its verdict.",
        ),
        mcq(
            "A teammate wants to add a `user_id` label to `hello_requests_total`. What is the main problem?",
            [
                "Counters cannot have labels at all",
                "Every user creates a new time series, so cardinality explodes",
                "Grafana cannot show labels that contain digits",
                "Prometheus would scrape the app once per user",
            ],
            1,
            "Each distinct label value is a separate series, so user IDs make memory and storage grow without limit.",
            "Part 9",
        ),
        mcq(
            "What does `kubectl -n hello rollout restart deployment/hello-devops` actually do?",
            [
                "Restarts the containers inside the existing pods",
                "Reboots the kind nodes one at a time, in order",
                "Deletes the Deployment and then creates it again",
                "Rolls out new pods to replace the old ones",
            ],
            3,
            "It changes the pod template, so the Deployment rolls out new pods; that is why new pods get OneAgent.",
            "Part 7",
        ),
    ],
}

OUT.write_text(json.dumps(part, indent=1, ensure_ascii=False) + "\n")
print("wrote", OUT)
