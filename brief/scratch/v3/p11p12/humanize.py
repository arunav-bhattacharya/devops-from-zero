#!/usr/bin/env python3
"""Human-writing pass (blog mode) for Part 11 (d47-d49) and Part 12 (d50-d51).
Loads content/p11.json and content/p12.json, rewrites prose fields only, writes them back.
Each edit is either a full field replacement (SET) or an exact substring swap that must
match exactly once (SUB), so a stale edit fails loudly instead of silently."""
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[4]


def lesson(doc, lid):
    return next(L for L in doc["lessons"] if L["id"] == lid)


def resolve(doc, path):
    """path like ('d47', 'sections', 0, 'body') or ('intro',) or ('resources', 2, 'why')."""
    obj = doc
    keys = list(path)
    if isinstance(keys[0], str) and keys[0].startswith("d") and keys[0][1:].isdigit():
        obj = lesson(doc, keys.pop(0))
    for k in keys[:-1]:
        obj = obj[k]
    return obj, keys[-1]


def SET(doc, path, new):
    obj, k = resolve(doc, path)
    assert isinstance(obj[k], str), path
    obj[k] = new


def SUB(doc, path, old, new):
    obj, k = resolve(doc, path)
    n = obj[k].count(old)
    assert n == 1, f"{path}: expected 1 match, found {n}: {old[:60]!r}"
    obj[k] = obj[k].replace(old, new)


# ---------------------------------------------------------------- Part 11

def part11(d):
    SET(d, ("intro",),
        "Parts 9 and 10 tell you when hello-devops is unhealthy, but not which request failed or where its time went. "
        "Logs and traces answer those two questions. Days 47 and 48 collect every log line into Elasticsearch with "
        "Fluent Bit, first with Docker Compose on your laptop and then as a DaemonSet on kind. Day 49 traces "
        "hello-devops with OpenTelemetry, without changing its code, and finds a slow Redis call in Jaeger.")

    # ---- d47
    SUB(d, ("d47", "sections", 0, "body"),
        "The copy outlives the container, so you stop asking where the log is and start asking what it says.",
        "The copy outlives the container, so the pod that handled the 14:02 payment can be gone and you can still read what it printed.")
    SUB(d, ("d47", "sections", 0, "body"),
        "One detail matters: the engine opens that connection, not a container. That is why the address is "
        "`localhost:24224`, the port Fluent Bit publishes on your laptop, and why `fluentd-async` is set.",
        "The engine opens that connection, not a container, so the address is `localhost:24224`, the port Fluent Bit "
        "publishes on your laptop. The lab also sets `fluentd-async`.")
    SUB(d, ("d47", "sections", 2, "body"),
        "That explains two surprises you will hit in the lab:",
        "If you are used to grep, which matches any substring, this gives you two surprises in the lab:")
    SUB(d, ("d47", "sections", 2, "body"),
        "\n\nThis trips most people up, because grep matches any substring and Elasticsearch matches whole tokens.", "")
    SUB(d, ("d47", "sections", 4, "body"),
        "Two rules follow, and both surprise people:",
        "Two rules follow from this:")
    SUB(d, ("d47", "sections", 5, "body"),
        "You need neither Logstash nor Fluentd: Fluent Bit sends straight to Elasticsearch, as in the lab. On Kubernetes "
        "a shipper runs on every node, so a small footprint matters, and that is the job Fluent Bit was built for.",
        "For this course you need neither Logstash nor Fluentd, because Fluent Bit sends straight to Elasticsearch. "
        "On Kubernetes a shipper runs on every node, so you pay for its memory once on every node. That is the job "
        "Fluent Bit was built for.")
    SUB(d, ("d47", "sections", 5, "body"),
        "For you, two facts matter. The lab images are free to run. And OpenSearch is close enough to Elasticsearch "
        "that today's ideas carry over.",
        "None of this changes what you do today. The lab images are free to run, and OpenSearch is close enough to "
        "Elasticsearch that today's ideas carry over.")
    SET(d, ("d47", "analogy"),
        "In a newspaper archive, old papers do not sit in a reporter's desk drawer, where they would be thrown out "
        "with the desk (a container). Every issue is filed in one building, one shelf per day (one index per day). "
        "The archive keeps a card catalogue of every word and the issues it appears in (the inverted index), so you "
        "find every mention of 'declined' without opening a single paper. A human archivist would help you when you "
        "ask for half a word or a plural. The catalogue will not: it lists whole words exactly as they were filed, "
        "and anything else comes back empty.")
    SET(d, ("d47", "real_world"),
        "When a merchant reports a failed payment, on-call filters Kibana on its `order_id` and reads the whole story "
        "across services in a minute. That works because every service writes JSON logs with the same field names "
        "(`service`, `level`, `order_id`, `trace_id`), so one query covers all of them. Card numbers and tokens are "
        "masked inside the app before the line is printed, and a review checks new log statements for personal data.")
    SUB(d, ("d47", "deeper", "body"),
        "The Elastic sizing guide puts it plainly: searching a thousand 50 MB shards is much more expensive than "
        "searching one 50 GB shard with the same data.",
        "The Elastic sizing guide gives an example: searching a thousand 50 MB shards costs much more than searching "
        "one 50 GB shard with the same data.")
    SUB(d, ("d47", "deeper", "body"),
        "Now the refresh. A new document first lands in an in-memory buffer.",
        "The one-second delay from earlier comes from the refresh. A new document first lands in an in-memory buffer.")

    # ---- d48
    SUB(d, ("d48", "sections", 0, "body"),
        "Two more tail settings matter:",
        "Two more things about the tail input:")
    SUB(d, ("d48", "sections", 4, "body"),
        "A simple way to think about the bill: what you store is roughly the daily volume, times one plus the number "
        "of replicas, times the days you keep it. Every one of those three is a lever.",
        "Roughly, what you store is the daily volume, times one plus the number of replicas, times the days you keep "
        "it. You can cut any of the three.")
    SUB(d, ("d48", "sections", 5, "body"),
        "Should alerts come from logs or from metrics? Prefer metrics for rates and latency: Prometheus from Part 9 "
        "is cheaper and faster for those. Use log alerts for events that only exist in logs. Good examples are a "
        "specific error message, a failed login burst or a payment provider's error code. One alert source per "
        "symptom keeps on-call sane.",
        "Should alerts come from logs or from metrics? For rates and latency, use metrics: Prometheus from Part 9 is "
        "cheaper and faster for those. Use log alerts for events that only exist in logs, such as a specific error "
        "message, a failed login burst or a payment provider's error code. Whichever you pick, give each symptom one "
        "alert source, so on-call is not paged twice for the same thing.")
    SUB(d, ("d48", "sections", 6, "body"),
        "Day 46 introduced Grafana Loki. It makes the opposite trade-off to Elasticsearch, so it is worth comparing "
        "them directly.\n\nElasticsearch indexes every word",
        "Day 46 introduced Grafana Loki, which makes the opposite trade-off. Elasticsearch indexes every word")
    SET(d, ("d48", "analogy"),
        "A DaemonSet of Fluent Bit is like a mail room on every floor of an office building. Each floor's mail room "
        "collects the letters its offices put out. It stamps each one with the sender's floor and department (the "
        "Kubernetes filter) and sends the sacks to one central archive (Elasticsearch). The archive's rules decide "
        "which shelf a letter goes on (the index template) and when old boxes go to the shredder (ILM). Unlike a real "
        "mail room, Fluent Bit does not know who sits in which office. It has to ask the Kubernetes API for pod "
        "labels, and in a very large building all those questions add up.")
    SET(d, ("d48", "mistake"),
        "You install the Fluent Bit chart with its default config and wait for logs that never arrive. The default "
        "output sends to a host named `elasticsearch-master`, which only exists if you installed Elastic's old chart, "
        "and it does not set `suppress_type_name`. Elasticsearch 8 and 9 answer that output with HTTP 400 and "
        "`Action/metadata line [1] contains an unknown parameter [_type]`, and with unlimited retries Fluent Bit "
        "keeps trying forever. Always set the output yourself, and read one Fluent Bit pod's log with `kubectl logs` "
        "before you open Kibana.")
    SET(d, ("d48", "real_world"),
        "Each service's logs should arrive with the same Kubernetes fields, wherever the service runs. A payments "
        "company gets that by running Fluent Bit as a DaemonSet in every cluster, with one shared Helm values file. The "
        "platform team owns the index templates and lifecycle policies. Application logs stay 14 days, while audit "
        "logs go to a separate data stream kept much longer in a cheaper tier. When a team adds a noisy debug log, "
        "the weekly 'biggest indices' report shows it, and they fix it before it shows up on the bill.")
    SUB(d, ("d48", "deeper", "body"),
        "You can point Fluent Bit at a data stream instead of daily indices, and it is a good way to see Elastic's "
        "defaults at work. I tested this trick against the lab.",
        "You can point Fluent Bit at a data stream instead of daily indices, which shows you Elastic's defaults at "
        "work. I tested this against the lab.")

    # ---- d49
    SUB(d, ("d49", "sections", 0, "body"),
        "Even hello-devops, one service and Redis, benefits.",
        "A trace helps even with hello-devops, which is one service and Redis.")
    SUB(d, ("d49", "sections", 0, "body"),
        "In Part 9 you met the signals, and here is how they divide the work in practice. A metric alert says "
        "something is wrong. A trace says where. The logs of that one request say why.",
        "You met the signals in Part 9. In practice they split the work: a metric alert says something is wrong, a "
        "trace shows where, and the logs of that one request explain why.")
    SUB(d, ("d49", "sections", 3, "body"),
        "Auto-instrumentation shows the plumbing. For business steps,",
        "Auto-instrumentation covers the framework calls. For business steps,")
    SUB(d, ("d49", "sections", 4, "body"),
        "Version drift bites here. Collector v0.144 renamed",
        "Check the version of any Collector config you copy. Collector v0.144 renamed")
    SUB(d, ("d49", "sections", 5, "body"),
        "The SDK's default sampler is `parentbased_always_on`. In plain words: follow the caller's decision if there "
        "is one, otherwise keep everything.",
        "The SDK's default sampler is `parentbased_always_on`. It follows the caller's decision if there is one, and "
        "otherwise keeps everything.")
    SUB(d, ("d49", "sections", 6, "body"),
        "Traces get most useful when the three signals point at each other. The thread that ties them together is "
        "the trace ID:",
        "Traces get most useful when the signals point at each other, and the trace ID is what connects them:")
    SUB(d, ("d49", "sections", 6, "body"),
        "A habit worth building: when you add a log line in a service that is traced, make sure the trace ID ends up "
        "in it. It costs a few bytes per line, and it is the difference between 'errors went up' and 'here is "
        "request 4bf92f..., and here is everything it did'.",
        "So when you add a log line in a service that is traced, make sure the trace ID ends up in it. It costs a "
        "few bytes per line. In return, 'errors went up' becomes 'here is request 4bf92f..., and here is every line "
        "it wrote'.")
    SET(d, ("d49", "analogy"),
        "A trace is a parcel's tracking history. The tracking number on the label (the trace ID in `traceparent`) "
        "is copied onto every new label as the parcel moves on. Each depot adds a scan with its arrival and "
        "departure times (a span). Looking at all the scans for one number shows where the parcel sat for two days. "
        "A courier keeps the history of every parcel, though. A busy system usually samples and keeps only some "
        "traces, so the request you care about may never have been recorded.")
    SET(d, ("d49", "mistake"),
        "A Collector config copied from an older tutorial either fails or warns on a current Collector. A `jaeger:` "
        "exporter now stops the Collector with `'exporters' unknown type: \"jaeger\"`, and `otlp:` still works but "
        "logs `\"otlp\" alias is deprecated; use \"otlp_grpc\" instead`. Send OTLP to Jaeger with the `otlp_grpc` "
        "exporter, and run `otelcol validate` (the `validate` command in the worked commands) on every config change "
        "before you deploy it.")
    SET(d, ("d49", "real_world"),
        "On-call gets the checkout latency alert, opens an example slow trace and sees the time spent in the call "
        "to the card partner. Then they search the logs by that trace ID. On a payments team this works "
        "because every service is traced with OpenTelemetry. The Collector tier tail-samples: it keeps all traces "
        "with an error, all slower than two seconds, and 5% of the rest. It also hashes client IPs and removes "
        "card-related attributes before anything leaves the cluster.")
    SUB(d, ("d49", "deeper", "body"),
        "Two consequences are worth thinking through before you run this in production.",
        "In production, this costs you in two places.")
    SUB(d, ("d49", "deeper", "body"),
        "Just remember that anything head sampling dropped is gone for good, errors included.",
        "Anything head sampling dropped is gone for good, though, errors included.")


# ---------------------------------------------------------------- Part 12

def part12(d):
    SET(d, ("intro",),
        "In Parts 9 to 11 you assembled observability from open-source parts. Dynatrace does the same job as one "
        "commercial product: its agent collects the data, its store keeps every signal, and you read all of it with "
        "one query language. Day 50 explains how it thinks, using a free sandbox. Day 51 gets your own data in and "
        "teaches DQL from zero.")
    SET(d, ("resources", 2, "why"),
        "The official walk through fetch, filter, summarize and the other basic commands.")
    SET(d, ("resources", 3, "why"),
        "Side-by-side DQL and SQL examples, for when a SQL habit gives you the wrong result.")

    # ---- d50
    SUB(d, ("d50", "sections", 0, "body"),
        "When something breaks, you jump between tabs and match things up by hand. This trace ID, that pod name, the "
        "same minute on three graphs.",
        "When something breaks, you jump between tabs and match things up by hand: this trace ID, that pod name, the "
        "same minute on three graphs.")
    SUB(d, ("d50", "sections", 0, "body"),
        "One agent collects the data. One store, called Grail, keeps every signal. One query language, DQL, reads "
        "all of it. And the platform links the signals for you,",
        "A single agent collects the data, a store called Grail keeps every signal, and one query language, DQL, "
        "reads all of it. The platform also links the signals for you,")
    SUB(d, ("d50", "sections", 1, "body"),
        "One rule trips people up. OneAgent cannot add itself to a process that is already running. After you "
        "install it, restart the apps you want to see.",
        "OneAgent cannot add itself to a process that is already running. After you install it, restart the apps "
        "you want to see. Until then they show up as processes with no traces.")
    SUB(d, ("d50", "sections", 2, "body"),
        "Smartscape is the live map of these entities and how they connect. Nobody draws it. OneAgent sees which "
        "process runs on which host and which service calls which, and Smartscape records it.",
        "Smartscape is the live map of these entities and how they connect. OneAgent sees which process runs on "
        "which host and which service calls which, and Smartscape records what it sees.")
    SUB(d, ("d50", "sections", 2, "body"),
        "This matters because every metric, log line and span carries the ID of the entity it came from. That shared "
        "ID is how Dynatrace joins your signals without join logic from you. It is also the map Davis walks when "
        "something breaks.",
        "Every metric, log line and span carries the ID of the entity it came from. That shared ID is how Dynatrace "
        "joins your signals without join logic from you. And when something breaks, this map is what Davis walks.")
    SUB(d, ("d50", "sections", 4, "body"),
        "Two limits matter. Davis can only follow dependencies",
        "Davis has two limits. It can only follow dependencies")
    SUB(d, ("d50", "sections", 5, "body"),
        "A few classic ideas have new names. Management zones,",
        "Some classic ideas were renamed as well. Management zones,")
    SET(d, ("d50", "analogy"),
        "One water pipe cracks on the fifth floor of an office building. Ten rooms below report wet ceilings, and a "
        "simple alarm system gives you ten alarms. Dynatrace is like a building with sensors fitted in every pipe "
        "and an up-to-date plumbing plan. The engineer follows the pipes up from the wet ceilings to the one cracked "
        "joint. OneAgent is the sensors, Smartscape is the plan, and Davis is the engineer. In a real building the "
        "pipes stay where they were built. Services and pods come and go every minute, so this plan is redrawn all "
        "the time. And a pipe without a sensor does not exist for the engineer at all.")
    SET(d, ("d50", "mistake"),
        "Leaving it to Davis to decide what good looks like. Davis compares each service with its own past, so a "
        "service that has always been slow looks normal to it. Automatic discovery does not make that decision for "
        "you. Write SLOs for the user journeys that matter (Day 41), and let Davis help you find causes when they "
        "break.")
    SET(d, ("d50", "real_world"),
        "A night page in a system with a few hundred microservices starts from the problem Davis opened. The "
        "on-call engineer checks the root cause and the affected services, then opens a trace from the evidence "
        "instead of five dashboards. Behind that, a platform team owns the agents and the cost budget, and each app "
        "team owns its own SLOs.")
    SUB(d, ("d50", "deeper", "body"),
        "Neither approach reads your mind. Labels need care from you, and the graph needs instrumentation everywhere.",
        "Both need work from you: labels need care, and the graph needs instrumentation everywhere.")

    # ---- d51
    SUB(d, ("d51", "sections", 0, "body"),
        "Mixing them up is a classic cause of 404 errors.",
        "Mixing them up is a common cause of 404 errors.")
    SUB(d, ("d51", "sections", 1, "body"),
        "so app-only injection is the safer bet.",
        "so app-only injection is the safer choice.")
    SUB(d, ("d51", "sections", 3, "body"),
        "Two details make rungs 6 and 7 click. A series is an array,",
        "Rungs 6 and 7 need two more facts. A series is an array,")
    SUB(d, ("d51", "sections", 4, "body"),
        "These trip up almost everyone who knows SQL. The worst part is that several of them do not fail.",
        "If you write SQL every day, expect to make most of these at least once. Several of them do not even fail.")
    SUB(d, ("d51", "sections", 6, "body"),
        "No prices here. The public rate card changes, and each company's contract sets its own rates. Keep the idea "
        "instead:",
        "This lesson gives no prices, because the public rate card changes and each company's contract sets its own "
        "rates. Remember the idea instead:")
    SET(d, ("d51", "analogy"),
        "A DQL query works like a sorting line in a post office. The first station empties one sack onto the belt "
        "(`fetch logs`). Each later station does one job: drop letters for other cities (`filter`), keep only the "
        "address label (`fields`), or sort letters into one bin per street and count them (`summarize`). A station "
        "only sees what the one before it passed on, so swapping two stations changes the result. The bill works "
        "differently. A post office pays per letter handled, while Grail charges by how much the first station has to "
        "scan. So a narrow time window at the start matters more than anything later on the belt.")
    SET(d, ("d51", "real_world"),
        "Once a company runs many clusters, its Dynatrace setup lives in git like any other config. A platform team "
        "keeps one DynaKube per cluster there, and Argo CD applies it. App teams opt in by labelling their "
        "namespaces. Release pipelines send a deployment event and wait for the guardian's verdict before they "
        "promote a build, and someone reviews the billing usage query every week.")
    # Factual fix: Day 49 and the lab use the current exporter name; otlphttp is a deprecated alias since v0.144.
    SUB(d, ("d51", "deeper", "body"),
        "Add a second exporter of type `otlphttp` with the same endpoint and header,",
        "Add a second exporter of type `otlp_http` with the same endpoint and header,")


def main():
    for name, fn in (("p11", part11), ("p12", part12)):
        path = ROOT / "content" / f"{name}.json"
        doc = json.loads(path.read_text())
        fn(doc)
        with open(path, "w") as f:
            json.dump(doc, f, ensure_ascii=False, indent=1)
            f.write("\n")
        print("wrote", path)


if __name__ == "__main__":
    main()
