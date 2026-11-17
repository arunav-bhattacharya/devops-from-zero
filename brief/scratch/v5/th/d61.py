"""Book-voice rewrite of d61 (Dynatrace: one platform for every signal). Writer: th."""
import sys
sys.path.insert(0, "/home/user/devops-from-zero/brief/scratch/v5/th")
from common import apply

OPENING = """Picture a detective called to an office building at ten in the morning. Ten tenants are waiting, each with a complaint. A wet ceiling on the fourth floor. Flickering lights on the third. A smell of damp on the second. A tidy detective writes ten reports and goes home. A good one walks upstairs and finds one cracked pipe on the fifth floor, which explains all ten.

Ten reports feel like progress. Each complaint is real, and each one gets an answer. What nobody asked is how the complaints connect.

Last time, we asked whether a system needs a mesh at all. Before that, in Parts 12 to 14, we built our own tools to watch a system, one tool per kind of clue. Today we meet Dynatrace, a commercial product that tries to be the good detective. One agent collects every clue, one map shows how things connect, and one engine names the cracked pipe. We'll use its free Playground, so there is nothing to install.

Before we start, make a guess, and keep it in mind."""

S1 = """Observability means being able to tell what a system is doing from the data it reports about itself. In Parts 12 to 14 you built an observability stack from open-source parts. Count them:
- Prometheus and Alertmanager for metrics and alerts (Part 12)
- Grafana for dashboards (Part 13)
- Elasticsearch, Kibana and Fluent Bit for logs (Part 14)
- the OpenTelemetry Collector and Jaeger for traces (Part 14)

That is eight programs to run, upgrade and keep alive, before you count exporters. Most have their own query language: PromQL, KQL or ES|QL, and Jaeger's search form. When something breaks, you jump between browser tabs and match things up by hand: this trace ID, that pod name, the same minute on three graphs. It is ten witnesses, each in a separate room.

Dynatrace takes the opposite approach. It is a commercial observability platform that Dynatrace runs for you as SaaS (software as a service: you use it in the browser, and they run the servers). A single agent, a program on each machine, collects the data. A store called Grail keeps every signal, and one query language, DQL, reads all of it. The platform also links the signals for you, because each log line, span and metric is tied to the same host, process or service.

You pay for that in three ways:
- Money. Billing follows usage, and data sent, data kept and data queried all count (Day 62).
- Lock-in. Your dashboards, queries and alert setup only work in Dynatrace.
- Control. Your telemetry leaves your network and lives on Dynatrace's servers.

For a handful of services, the stack you built is plenty. A platform like this starts to pay off when you run hundreds of services and nobody can keep the whole dependency map in their head.

Next, we'll meet the agent that collects every clue."""

S2 = """OneAgent is Dynatrace's agent. You install it once per host, a machine or virtual machine. On Kubernetes, the Dynatrace Operator adds it to your pods for you (Day 62). An operator is a program that runs inside Kubernetes and manages another tool. Then OneAgent does three jobs without code changes:
1. It finds every process (running program) and works out what it is: a JVM, a Node.js server, a database.
2. It loads a small code module into supported processes. The module records each request as it passes through, which gives you traces.
3. It sends metrics, logs and traces to Dynatrace.

The JVM is the engine that runs Java and Kotlin programs, and Node.js runs JavaScript ones. Compare this with Day 57. There you started hello-devops with `opentelemetry-instrument`, one service at a time, and ran a Collector to forward the data. OneAgent moves that work from each service to the host. Your Kotlin app from Part 7 is the classic case: Java needs no agent flag in the Dockerfile and no SDK in the Gradle build. Python support arrived later, so check the [technology support pages](https://docs.dynatrace.com/docs/ingest-from/technology-support) for your runtime and version before you count on it.

How does it get inside a program it did not start? On Linux, the installer adds a small OneAgent library to the file `/etc/ld.so.preload`. The system's program loader reads that file each time a program starts. It loads the listed libraries before the program's own code runs. The OneAgent library checks what is starting, such as a JVM or a Node.js server, and loads the matching code module.

Now the naive move: install OneAgent on a busy machine and go looking for traces. You find the host and its processes, but no traces. That hook only fires when a process starts, and a process that was already running never passed through it. Until you restart it, it shows up as a process with no traces. **OneAgent only sees a program from its start. Restart the apps you want to trace.**

ActiveGate is the second piece, and it solves two problems. First, many company networks do not let every server reach the internet. The agents send their data to an ActiveGate inside the network, and only that one machine talks to Dynatrace. Second, some data only comes out of an API you have to call, such as the Kubernetes API or a cloud provider's API. An API is a set of requests one program offers to others. ActiveGate makes those calls.

On Kubernetes you switch these jobs on as capabilities. `routing` relays OneAgent traffic. `kubernetes-monitoring` reads nodes, workloads and events.

Next, we'll see the map that OneAgent draws from everything it finds."""

S3 = """Dynatrace calls each thing it monitors an entity, and gives each one an ID. The common types are:
- host: a machine or virtual machine
- process: one running program on a host, such as gunicorn
- service: what a process offers to callers, such as the hello-devops web endpoints
- Kubernetes cluster, namespace, workload and pod

Smartscape is the live map of these entities and how they connect. Part of it is easy: OneAgent knows which host it runs on and which processes it found there. Calls between services take one more step. The code module in the caller adds a trace header to each outgoing request, the same idea as `traceparent` on Day 57. The code module in the receiver reads it, so both ends of the call are linked. Smartscape records each link it sees.

The map runs in two directions. Vertical links say what runs on what: a service runs in a process, and the process runs on a host. Horizontal links say who calls whom: checkout calls payments, and payments calls a database. For our detective, it is the building's plumbing plan, redrawn every minute as pipes come and go.

Every metric, log line and span carries the ID of the entity it came from. A slow span in `payments` and an error log line from the same process carry the same IDs. That shared ID is how Dynatrace joins your signals without join logic from you. And when something breaks, this map is what Davis walks.

You can query the map with DQL, the language you learn on Day 62. `smartscapeNodes "SERVICE"` lists services, and `smartscapeEdges "calls"` lists who calls whom. Fields that point at an entity start with `dt.smartscape.`, for example `dt.smartscape.host`. Older queries use `dt.entity.*`. Those fields are deprecated, so do not copy them into new work.

Next, we'll follow one request along the map."""

S4 = """On Day 57 you met traces: one request's path through many services, made of spans (timed steps) that share a trace ID. PurePath is Dynatrace's name for the traces OneAgent records. They often go deeper than hand-made spans. A PurePath can show the method calls (the small named pieces of code a program runs) and database statements inside a service, with timings. Nobody wrote a line of tracing code.

Spans from OpenTelemetry are welcome too. They land in Grail next to the ones OneAgent captured, and you query both the same way.

You rarely start from a single trace. You start from the Services app. It lists each service with the numbers from the RED method on Day 49:
- request rate (requests per minute)
- failure rate (the share of requests that failed)
- response time, including slow percentiles such as p95 (the time that 95 of every 100 requests beat)

The usual path goes like this:
1. Pick the service with a bad number.
2. Filter its requests: the slow ones, the failed ones, or one endpoint.
3. Open one trace from that list.
4. Find the span that takes most of the time, and the service that owns it.

The process and host views work the same way for CPU, memory and restarts.

That is how a person walks the map. Next, we'll watch Davis walk it for you."""

S5 = """Davis is the engine that watches all of this, and it does two jobs.

First, it detects anomalies, values that are out of the ordinary. It learns a baseline for a metric, which is what normal looks like for this service at this time. When the value leaves the baseline, it raises an event. You can also set fixed thresholds, as you did with Prometheus alert rules.

Second, it groups related events into one problem and names the most likely root cause. This is where it differs from your Part 12 stack. Davis starts at the affected entity and follows the Smartscape links and the traces to what that entity depends on. At each dependency it asks whether that one is unhealthy too. If it is, Davis keeps going down, like the detective climbing from the wet ceiling to the floor above.

Dynatrace calls this walk a fault-tree analysis. The trail ends at an unhealthy component whose own dependencies look fine, and that component is the most probable root cause. Two graphs that spiked in the same minute are not linked by timing alone, which answers the guess.

A problem holds:
- an ID such as `P-12345` and a title
- the root-cause entity and the evidence: events, metric changes, deployments
- the affected entities and, where Dynatrace can tell, the affected users

Davis has two limits. It can only follow dependencies that OneAgent or your OpenTelemetry data shows. A service nobody instruments is invisible to it, a pipe with no sensor. **Davis can only follow what something measured. An unwatched service is where its trail ends.**

And Davis does not know what you promised your users. It compares each service with its own past, so a service that has always been slow looks normal to it. The SLOs from Day 49 are still yours to write. Let Davis find causes when they break.

Next, we'll sort out the names, because Dynatrace renamed a lot recently."""

S6 = """Dynatrace renamed a lot recently, and old screenshots will confuse you.

Latest Dynatrace is the current platform. You reach it at an address like `https://abc12345.apps.dynatrace.com` and work in apps such as Notebooks, Dashboards, Problems, Services, Kubernetes and Workflows. Dynatrace Classic is the older generation. Some of its screens still exist as classic apps with "Classic" in the name, such as Dashboards Classic. If a screenshot does not match your screen, it is probably Classic. Look for the app with the same name.

Some classic ideas were renamed as well. Management zones, the classic way to slice data by team or environment, became segments.

In January 2026 Dynatrace put all of its AI under one name, Dynatrace Intelligence:
- Davis is the root-cause and anomaly engine you just read about.
- Dynatrace Assist is the chat assistant that replaced Davis CoPilot. Ask a question in plain English and it can write the DQL for you.
- Agents act on what they find, inside rules and approvals that you set.

Old names live on in APIs and data. Problems are stored as `dt.davis.problems`, and some docs still say Davis CoPilot. Read the DQL that Assist writes the way you would read a new colleague's draft: probably good, always checked.

Two apps get most of your time. Notebooks are for exploring: you write DQL step by step and see each result. Dashboards are for sharing a view with the team, and you can pin a Notebook result to one.

Next, we'll set Dynatrace next to its rivals, and find the free way in."""

S7 = """These are the options you are likely to meet:
- Your open-source stack: free software, full control, runs anywhere. You instrument each service and link the signals yourself.
- Datadog and New Relic: also SaaS, agent-based and all-in-one. Compare them on your own services during a trial, since the differences are in the details and the price list.
- Elastic Observability: grew out of the log search stack from Day 55. You can run it yourself or in Elastic's cloud.
- Dynatrace: it pushes hardest on the self-drawn Smartscape map, root cause through dependencies, and one store with one query language.

You can learn Dynatrace without paying, in this order:
1. The Playground. It is a public sandbox with sample data, so there is nothing to install and no data to send. Sign-up needs an email address. Use it today and for the DQL part of Day 62.
2. The free trial: 15 days of your own SaaS environment. Dynatrace's sign-up page says no credit card is needed. The clock starts at sign-up, so wait until you are ready for Day 62's hands-on part.
3. Optional: during the trial, install the Dynatrace Operator on your kind cluster (Day 62). Kind and Apple Silicon Macs are not officially supported, so treat it as an experiment that may fail.

Both the Playground and the trial start from the [try-free page](https://www.dynatrace.com/try-free).

Today we only looked around someone else's data. The Playground cannot show you your own services, and reading its screens is not the same as asking your own questions. For that you need your own data inside, and the language that reads it. That is the next lesson."""

CLOSING = """We started with ten complaints and one cracked pipe. Today OneAgent collected the clues, and Smartscape drew the plan of who runs on what and who calls whom. Davis walked that plan down to one root cause instead of thirty alerts. In the Playground, open one problem and follow it from an affected service to its root cause. Then ask what Davis could not see.

Next, we'll get our own data into Dynatrace and learn DQL. How do you ask one question of metrics, logs and traces at once?"""

ASIDE = {
    "title": "Can I run Dynatrace on my own servers?",
    "body": "Yes, in part. Dynatrace Managed is a self-hosted edition for companies that must keep data on their own servers. But Grail, and with it DQL, Notebooks and Workflows, only exists on SaaS. So the Dynatrace this course teaches is the SaaS one.",
    "after": 5,
}

new = {
    "goal": "By the end you can explain what OneAgent, ActiveGate, Smartscape, PurePath and Davis do, compare Dynatrace with the open-source stack from Parts 12 to 14, and find a problem's root cause in the free Playground.",
    "opening": OPENING,
    "guess": (
        "Your Grafana stack fires 30 alerts at 10:02. Dynatrace opens one problem and names a root cause. How does Davis, its analysis engine, pick that root cause?",
        "Davis starts at the affected component and follows the dependencies and traces that OneAgent recorded, then runs a fault-tree analysis. Timing alone is not enough, and the chat assistant is a separate tool.",
    ),
    "terms": [
        "A commercial observability platform, run for you as SaaS, that keeps metrics, logs, traces and events together.",
        "Dynatrace's agent. It finds the programs running on a machine or in a pod and records their data without code changes.",
        "A Dynatrace relay that forwards agent traffic and reads APIs, such as the Kubernetes API.",
        "Anything Dynatrace monitors and gives an ID: a host, a process, a service, a Kubernetes pod.",
        "The live map of entities and their links, drawn automatically from what OneAgent sees.",
        "Dynatrace's name for a trace recorded by OneAgent, down to method and database calls.",
        "The engine that spots anomalies, groups related ones into one problem and names the likely root cause.",
        "Dynatrace's data store. It holds every signal in one place, and you read it with DQL.",
    ],
    "sections": [
        ("What an all-in-one platform buys you", S1),
        ("OneAgent and ActiveGate: install once, see a lot", S2),
        ("Entities and Smartscape: a map nobody draws", S3),
        ("PurePath traces and the services view", S4),
        ("Davis: one problem instead of thirty alerts", S5),
        ("The 2026 names: Latest Dynatrace, Dynatrace Intelligence and Assist", S6),
        ("How it compares, and how to try it for free", S7),
    ],
    "aside": ASIDE,
    "diagram_caption": "OneAgent and ActiveGate fill Grail; Davis walks the map and the traces to one root cause.",
    "say": [
        "Take a made-up shop with three services. `web` calls `checkout`, `checkout` calls `payments`, and `payments` uses a Postgres database. At 10:02 the database connection pool (a fixed set of open connections the app shares) fills up, and database calls start to wait.",
        "In your Part 12 stack, each symptom fires its own rule within a minute. You get something like the list below. Every alert is true, and none of them says which one caused the others.",
        "So you start digging. You open the Grafana RED dashboard and see that all three services went bad together. You open Jaeger, find a slow trace and notice the long database span inside `payments`. Then you search Kibana for that trace ID. You reach the cause, but it takes three tools.",
        "In Dynatrace, OneAgent already recorded the calls, so Smartscape knows the chain web, checkout, payments, database. Davis sees the same symptoms as events, each one measured against that service's own baseline.",
        "Davis starts from `web` and follows the call links and the traces downward. The time in the traces piles up in the database calls made by `payments`. Postgres itself looks healthy, because the waiting happens in the connection pool inside `payments`, so the fault tree ends there. Davis opens one problem with `payments` as the root cause, and `web` and `checkout` listed as affected.",
        "You can read that problem in a Notebook with query A5 from the lab file. On this incident it would return one row: an ID like `P-12345`, the category `SLOWDOWN`, and `payments` as the root cause. Now picture `payments` without OneAgent. Davis would stop at `checkout`, because it cannot follow a call into something nobody instruments.",
    ],
    "task": (
        [
            "Sign up for the Dynatrace Playground from the try-free page. Do not start the trial yet. Check that the address ends in `.apps.dynatrace.com`, which means Latest Dynatrace.",
            "Open the Services app and pick one service with traffic. Write down its request rate, failure rate and response time.",
            "From that service, find the process it runs in and the host under it. Sketch the chain on paper: service, process, host.",
            "Create `dynatrace/queries.dql` in your hello-devops repo with the Day 61 queries. Run A1 to A4 in a Notebook and find your service in the A3 result.",
            "Open the Problems app and pick one problem. Write down the root-cause entity, two affected entities and one piece of evidence.",
            "Open one trace for your service. Find the slowest span and the service that owns it.",
            "Ask Dynatrace Assist to show error logs from the last hour. Read the DQL it writes before you run it, and note one thing you would change.",
            "Commit `dynatrace/queries.dql`.",
        ],
        [
            "If an app in the steps is missing, search for its name from the Dynatrace menu, and prefer the one without \"Classic\" in its name.",
            "Zero rows usually means the time range is too short. Widen the timeframe before you change anything else.",
            "Assist may not be switched on in every environment. If you cannot find it, skip that step.",
        ],
        "You have a sketch of service, process and host for one service, a note with one problem's root cause, and `dynatrace/queries.dql` committed.",
    ),
    "explain_back": (
        "Explain to a teammate who knows Prometheus how Dynatrace finds a root cause, in 3 to 4 sentences. Mention OneAgent, Smartscape, traces and Davis.",
        "OneAgent runs on each host or in each pod and records processes, services and every call between them without code changes. From that, Smartscape keeps a live map of what runs on what and who calls whom. When metrics leave their baselines, Davis starts at the affected service and follows the map and the traces downward to the component where the time or the errors start. It opens one problem with that root cause, where Prometheus would have fired one alert per symptom.",
    ),
    "recap": [
        "Dynatrace swaps the eight open-source parts for one SaaS platform, and you pay in money, lock-in and control.",
        "OneAgent instruments hosts and supported processes without code changes; restart apps after you install it. ActiveGate relays traffic and reads APIs.",
        "Smartscape is a self-drawn map of entities; every signal carries an entity ID, which links them.",
        "Davis groups related anomalies into one problem and walks dependencies to the root cause.",
        "Davis is blind past anything uninstrumented, and it cannot know your SLOs.",
        "Learn for free in the Playground first; start the 15-day trial only when you are ready for Day 62.",
    ],
    "closing": CLOSING,
    "check": [
        ("Your team adds a new Go service with no OneAgent and no OpenTelemetry. It starts failing and slows down the service that calls it. What is Davis most likely to report?",
         "Davis can only follow dependencies it can see, so the trail ends at the last instrumented service."),
        ("A 2022 blog post tells you to filter by management zone and to use `dt.entity.service` in DQL. You use Latest Dynatrace. What do you do?",
         "Management zones became segments, and `dt.entity.*` fields are deprecated in favour of `dt.smartscape.*`."),
        ("You install OneAgent on a VM where a Java app is already running, and you restart nothing. What do you see?",
         "OneAgent sees the host right away, but it can only add its code module to a process when that process starts."),
    ],
    "interview": [
        ("When would you choose Dynatrace over Prometheus and Grafana?",
         "When the number of services is large enough that nobody can hold the dependency map, and incidents turn into hunts across many tools. Dynatrace gives you automatic instrumentation, a self-drawn topology and root-cause analysis in one place, which saves on-call time. The price is a usage-based licence, lock-in to its agent, queries and dashboards, and telemetry stored on a vendor's servers. For a small system, or when data must stay on your own servers, the open-source stack is often the better choice."),
        ("What is the difference between an alert and a problem in Dynatrace?",
         "An alert or event says one thing crossed a threshold or left its baseline, for one entity. A problem is what Davis builds from many such events when they share a root cause. It names the root-cause entity, lists the affected entities and keeps the evidence. So one incident becomes one problem to work on, instead of dozens of separate alerts."),
        ("How does Dynatrace get traces without code changes, and what are the limits?",
         "OneAgent loads a code module into supported runtimes when a process starts, and the module records each request, including method and database calls. On Kubernetes, the Operator's webhook adds OneAgent to pods as they are created. The limits: the runtime must be supported, running processes must be restarted, and anything uninstrumented is a blind spot. OpenTelemetry data can fill some of those gaps, because Dynatrace accepts OTLP."),
    ],
    "drop": ["analogy", "mistake", "real_world"],
}

apply(16, "d61", new)
