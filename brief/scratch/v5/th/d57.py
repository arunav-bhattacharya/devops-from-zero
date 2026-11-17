"""Book-voice rewrite of d57 (Distributed tracing with OpenTelemetry). Writer: th."""
import sys
sys.path.insert(0, "/home/user/devops-from-zero/brief/scratch/v5/th")
from common import apply, load, lesson

OPENING = """Picture a birthday present you ordered for a friend. The shop promised two days, and it took five. You call the shop, and they say it left on time. The delivery company says it arrived. Every depot on the way kept its own logbook, and every logbook says "a parcel passed through, all fine". Nobody can say where your parcel sat for three days.

Then you notice the tracking number on the label. Each depot scanned it as the parcel came and went. Put in order, the scans show two days on a shelf in one depot. One number, copied along the whole road, turned a pile of logbooks into a story.

Last time, every log line learned to say which pod wrote it. That still leaves the parcel's question: when one request passes through many programs, where did its time go? Today we put a tracking number on every request to hello-devops, without changing its code, and find a slow step we planted ourselves.

Before we start, make a guess, and keep it in mind."""

S1 = """Our lab app, hello-devops, is a tiny web app that answers every visit with a greeting and a count of visits so far. It keeps that count in Redis, a small, fast database. Each visit is a request: a message from a browser asking for a page, which the app answers.

Now picture a bigger request on a shop's website, a checkout. It enters an API service, a program that answers requests from other programs. That service calls a fraud check, which calls a card partner, while the API also writes to a database. Each of these is a separate service with its own job. The customer waited three seconds. Which hop took them?

Try the tools we already have. Metrics give you numbers per service. The fraud check's 95th percentile (the time that 95 of every 100 requests beat) went up. Logs give you lines per service, each with its own timestamp, and you have to guess which lines belong to this one request. Neither says that this request spent 2.6 of its 3 seconds waiting for the card partner. They are the depots' logbooks.

A trace does say it. A trace is the story of one request, told as a tree of timed steps. Each step is a span: a name, a start time, an end time, and some facts about what happened. Draw the spans on a timeline, one row each, and the slow step is the longest bar with nothing underneath it. That picture is called a waterfall. Jaeger, the tracing tool in our lab, draws it for you.

A trace helps even with hello-devops, which is one service and Redis. In the lab test, Redis writes were paused for 800 ms (milliseconds, thousandths of a second), and one request was sent. The trace showed `GET /` taking 835 ms, and its child span `INCRBY` taking 832 ms of them. `INCRBY` is the Redis command that adds to the count. Without the trace, you see a slow request. With it, you see a slow Redis call, and you know where to look next.

In practice the signals split the work. A metric alert says something is wrong, a trace shows where, and the logs of that one request explain why.

Next, we'll open a span and see what it holds."""

S2 = """A span records one operation. In OpenTelemetry, the tracing standard we use today, every span has:
- a name, such as `GET /` or `INCRBY`
- a start and end time, so a duration
- a trace ID, shared by every span in the same trace
- its own span ID, and the span ID of its parent
- attributes: key and value facts, such as `http.response.status_code = 200`
- events: timestamped notes inside the span, such as an exception (an error the code raised)
- a status: Unset, Ok or Error
- a kind: server (it handled a call), client (it made one), internal, or producer and consumer for message queues

A message queue is a waiting line of messages between services. The parent span IDs make the tree. The first span of a request has no parent and is called the root span.

In the lab, a normal request gives two spans with the same trace ID. Both come from instrumentation, ready-made code that makes spans for a tool:
- `GET /`, kind server, 6.5 ms, from the Flask instrumentation. Flask is the toolkit hello-devops is built with. This span is the root.
- `INCRBY`, kind client, 3.4 ms, from the Redis instrumentation. Its parent is the `GET /` span.

When Redis was stopped, both spans got status Error. Each also got an `exception` event with the type `redis.exceptions.ConnectionError`, its message and the stack trace, the list of code lines that led to the error. The trace carries the error with it, so you do not have to find the matching log line first.

Attribute names follow shared rules called semantic conventions, so every tool agrees that the HTTP method is `http.request.method`. Python instrumentation still uses older names unless you opt in with `OTEL_SEMCONV_STABILITY_OPT_IN=http,database`, which the lab sets. Without it you see `http.method` and `net.peer.ip` instead. Tutorials use both, so do not be surprised by either.

One request, one service, two spans. Next, we'll see how spans from different services find each other."""

S3 = """Spans from different services only join into one trace if each service tells the next one which trace it is in. That hand-over is called context propagation. It is the tracking number copied onto every new label. The caller injects the context into the outgoing request. The receiver extracts it and starts its own span as a child.

The context travels in a header, an extra line of information sent with every web request. For HTTP, OpenTelemetry uses the W3C Trace Context header by default. The W3C is the group that writes web standards. The header looks like this:

`traceparent: 00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-01`

It has four parts, split by dashes. Hex characters are the digits 0 to 9 and the letters a to f:
1. `00` is the version of the format.
2. `4bf92f3577b34da6a3ce929d0e0e4736` is the trace ID: 32 hex characters (16 bytes).
3. `00f067aa0ba902b7` is the parent span ID: 16 hex characters, the caller's current span.
4. `01` is the flags. `01` means sampled: the caller is recording this trace.

You can play the caller yourself with curl, the terminal command that sends web requests, and the worked example does exactly that. Send that header to hello-devops, and Jaeger files the `GET /` span under trace `4bf92f...` with parent `00f067aa0ba902b7`. Jaeger also warns that this parent is not in the trace, which is true: curl never reported a span.

You rarely write this header by hand. Instrumented HTTP clients (the code an app uses to call other services), such as Python's `requests`, add it to every outgoing call. The trouble starts at hops that do not pass it on. A proxy (a program that forwards requests) may strip unknown headers. A message queue may have no instrumentation, or a team may use a homemade HTTP client. The trace then breaks into two traces that look unrelated. It is a parcel that got a fresh label with a new number. **A trace is only as long as its chain of headers. When it stops early, look for the hop that dropped it.**

Next, we'll see what makes those spans and headers appear in an app that has no tracing code."""

S4 = """OpenTelemetry, OTel for short, is a project of the CNCF, a non-profit foundation for cloud tools. It standardizes how apps produce telemetry, the data a program reports about itself: metrics, logs and traces. It is not a backend, the place that stores and shows that data. OpenTelemetry stores nothing. It gives you these parts:
- the API: the functions your code calls to start spans
- the SDK: the engine behind the API, which samples, batches and exports
- instrumentation libraries, which create spans for frameworks such as Flask, Redis or JDBC
- OTLP, one protocol (a shared format for sending data) for traces, metrics and logs
- the Collector, covered in the next section

For many apps you write no tracing code. In Python, zero-code instrumentation takes three steps, and `tracing/Dockerfile.otel` does all three. That file is the recipe Docker uses to build the traced version of the app:
1. `pip install opentelemetry-distro opentelemetry-exporter-otlp` installs the pieces. pip is Python's package installer.
2. `opentelemetry-bootstrap -a install` looks at your installed packages and adds the matching instrumentation. For hello-devops it found Flask, Redis and a dozen others.
3. Prefix your start command with `opentelemetry-instrument`. The lab runs `opentelemetry-instrument gunicorn ...`, and `app.py`, the app's code, stays untouched.

How do spans appear with no tracing code? `opentelemetry-instrument` starts the SDK before your app's code runs. Then each instrumentation library wraps functions of its own framework, such as Flask's request handling or the Redis client's command method. Every call to them now starts and ends a span, like a depot scanner that beeps each time a parcel goes past.

Settings come from `OTEL_` environment variables, settings handed to a program when it starts. The names are the same in every language:
- `OTEL_SERVICE_NAME=hello-devops` names the service in every backend.
- `OTEL_EXPORTER_OTLP_ENDPOINT=http://otel-collector:4317` says where to send.
- `OTEL_TRACES_EXPORTER=console` prints spans to the terminal, handy when no backend runs.

Auto-instrumentation covers the framework calls. For business steps, such as "price the basket", you add a manual span with the API, for example `with tracer.start_as_current_span("price-basket"):` in Python. One caveat from the OTel docs applies to gunicorn, the web server that runs several copies (workers) of the app. Several workers are fine for traces but break auto-instrumented metrics, which is why the lab switches metrics off.

The app now makes spans. Next, we'll see where it sends them."""

S5 = """Apps can send spans straight to a backend. Most teams put an OpenTelemetry Collector in between, a program that receives telemetry, changes it and passes it on. There are three reasons:
- One place to change data: drop noise, remove personal data, add attributes.
- Apps stay simple: they send OTLP to one address and never learn about the backend.
- You can switch or add backends by editing one config file, without redeploying apps.

A Collector config has the same shape as Fluent Bit's pipeline from Day 55. Receivers take data in, processors change it, exporters send it out, and `service.pipelines` wires them together per signal. The lab's `tracing/otel-collector.yaml` reads like this:
1. The `otlp` receiver listens on 4317 (gRPC, a fast way for programs to call each other) and 4318 (HTTP).
2. `memory_limiter` refuses data before the Collector runs out of memory.
3. `transform/scrub` hashes `client.address`, because an IP address (a computer's number on the network) is personal data. It also deletes `user_agent.original`.
4. The `otlp_grpc/jaeger` exporter sends batches to Jaeger, and `debug` prints a line per batch in the Collector's log.

In the lab, the hashed address really arrived in Jaeger as a 64-character hex string. The same caller always gets the same hash, so you can still count unique callers without storing who they are.

Now the naive move: copy a Collector config from an older tutorial. On a current Collector it fails or warns. A `jaeger:` exporter stops the Collector with `'exporters' unknown type: "jaeger"`, because that exporter no longer exists: Jaeger speaks OTLP now. The `otlp:` exporter still works but logs `"otlp" alias is deprecated; use "otlp_grpc" instead`, because Collector v0.144 renamed it. So send OTLP to Jaeger with the `otlp_grpc` exporter. Run `otelcol validate` on every config change before you deploy it.

There are two main Collector images (ready-to-run packages). The core image, `otel/opentelemetry-collector`, is small and has the basics. The contrib image has the much larger set of components, including tail sampling.

Every span now flows through one place. Next, we'll ask whether we should keep them all."""

S6 = """Tracing every request costs CPU (the computer's processing power) in your app, plus network and storage. At high traffic most teams keep only some traces, which is called sampling. The OpenTelemetry docs say that for high-volume systems a rate of 1% or lower often represents the rest very well.

The SDK's default sampler is `parentbased_always_on`. It follows the caller's decision if there is one, and otherwise keeps everything. That is right for a lab and usually wrong for a busy production service.

Head sampling decides when the trace starts, from the trace ID. Set `OTEL_TRACES_SAMPLER=parentbased_traceidratio` and `OTEL_TRACES_SAMPLER_ARG=0.1`, and about 1 trace in 10 is kept. Trace IDs are random, so the sampler can read each one as a number and keep the traces whose number falls in the lowest tenth. In a lab run of 200 requests that way, Jaeger held 17 of them. The decision then travels in the sampled flag of `traceparent`, so every service keeps or drops the same trace. The lab showed that too: a request with flag `00` left no trace at all.

Head sampling has a blind spot. It decides before anything has happened, so it cannot promise to keep the traces you care about most, the failed and the slow ones. It is like choosing which parcels to track before they leave the warehouse.

Tail sampling decides after the trace is complete. A Collector buffers the spans for a few seconds, holding them in memory, looks at the whole trace, and applies rules such as:
- keep every trace with an error
- keep every trace slower than 500 ms
- keep 10% of everything else

The price is memory and a design rule: all spans of one trace must reach the same Collector instance. **Head sampling is cheap but blind. Tail sampling sees the whole trace, and pays for it in memory.** Tail sampling lives in the contrib Collector, and the deeper section shows a config.

We keep the traces that matter. Next, we'll store them, and tie them to the logs and metrics we already have."""

S7 = """The Collector sends spans somewhere that stores and shows them. The common open-source choices are:
- Jaeger. Version 2 is built on the OpenTelemetry Collector itself, and version 1 has reached end of life. The all-in-one image you run in the lab keeps traces in memory, so they vanish on restart. For real use it stores to Elasticsearch, OpenSearch, Cassandra or ClickHouse, which are all databases.
- Grafana Tempo, from Day 54. It needs only object storage (cheap storage for big files) and is queried with TraceQL.
- Commercial platforms. Dynatrace (Day 61) and Elastic both accept OTLP, so the same Collector config can send there.

Traces get most useful when the signals point at each other, and the trace ID is what connects them:
- In logs: write the trace ID on every line. For Python, `OTEL_PYTHON_LOG_CORRELATION=true` adds the trace and span IDs to log records. Then a Kibana search for one trace ID returns every log line of that request, across services.
- In metrics: Prometheus can attach a trace ID to a histogram sample (one of its timing counts). That link is called an exemplar, and it lets a latency spike on a Grafana graph open an example trace.
- In the UI: Grafana and Kibana can link from a span to its logs and back.

So when you add a log line in a service that is traced, make sure the trace ID ends up in it. It costs a few bytes per line. In return, "errors went up" becomes "here is request 4bf92f..., and here is every line it wrote".

Tracing has its limits, too. It shows you the slow or failing call between two services, but it does not fix it. Timeouts, retries and encryption for those calls still live in each app's own code, written again in every language. The next part moves that work out of the apps."""

CLOSING = """We started with a present that took five days and a pile of logbooks that all said "fine". One tracking number, copied from service to service in the `traceparent` header, turned hello-devops' slow visit into a waterfall with one long bar: `INCRBY`, 832 of 835 ms. In the lab, open that slow trace in Jaeger and find the span. In your own logs, check whether each line carries a trace ID.

Next, we'll start a new part about the calls between services themselves. When a call is slow or fails, who decides to wait, retry or give up?"""

ASIDE = {
    "title": "What about apps written in Java?",
    "body": "The idea is the same. You add the OpenTelemetry Java agent when you start the program, with `-javaagent:opentelemetry-javaagent.jar`, and set the same `OTEL_` variables. Java programs run on the JVM, the Java engine, as compiled code called bytecode. The agent rewrites the bytecode of known libraries as their classes load, so Spring, JDBC and HTTP clients get spans. Spring is a popular toolkit for Java services, and JDBC is Java's standard way to talk to databases.",
    "after": 3,
}

L = lesson(load(14), "d57")
deeper = L["deeper"]["body"]
EXTRA = "\n\nTwo version notes for when you copy Collector configs. Collector v0.144 also renamed the `otlphttp` exporter to `otlp_http`; the old names still work but log a deprecation warning. And the core image's `attributes` processor warned that it leaves the core distribution in v0.167, which is why the lab uses `transform`."
if EXTRA.strip() not in deeper:
    deeper += EXTRA

new = {
    "goal": "By the end you can explain spans, traces and context propagation, run hello-devops under opentelemetry-instrument with a Collector and Jaeger, and use a trace to find the slow step of a request.",
    "opening": OPENING,
    "guess": (
        "One request to hello-devops took 835 ms. Its access log line says status 200 (success), and the error rate on your dashboard is 0%. What shows you where those 835 ms went?",
        "Logs and metrics tell you that the request happened and how often. Only a trace records each step of one request with its own start time and duration, so you can see which step was slow.",
    ),
    "terms": [
        "The record of one request's whole path, made of spans that share one trace ID.",
        "One timed operation inside a trace, such as handling GET / or sending one Redis command.",
        "Passing the trace ID and the current span ID on to the next service, usually in a web request header.",
        "The standard web request header that carries a version, the trace ID, the parent span ID and a sampled flag.",
        "Keeping only some traces to save money. Head sampling decides at the start, tail sampling after the end.",
        "The OpenTelemetry Protocol for sending telemetry: gRPC on port 4317, HTTP on port 4318.",
        "A program that receives telemetry, changes it and sends it on to one or more backends.",
        "A free, open-source tracing tool that stores traces and shows them on a web page.",
    ],
    "sections": [
        ("Why logs and metrics cannot find the slow step", S1),
        ("What a span holds, and how spans make a trace", S2),
        ("Passing the tracking number: the traceparent header", S3),
        ("OpenTelemetry: tracing an app without touching its code", S4),
        ("The Collector, and a config copied from an old tutorial", S5),
        ("Sampling: deciding early or deciding late", S6),
        ("Storing traces, and joining them to logs and metrics", S7),
    ],
    "aside": ASIDE,
    "diagram_caption": "The real slow trace from the lab: the GET / server span lasted 835 ms, and its Redis child span INCRBY used 832 ms of that, so Redis is the slow step.",
    "say": [
        "Start the tracing lab. Compose builds the instrumented image from `tracing/Dockerfile.otel`, then starts Jaeger, the Collector, the app and Redis. A normal request answers as always: the app does not know it is being traced.",
        "Now pretend to be an upstream service, one earlier in the chain, that is already tracing this request. You choose the trace ID and your own span ID, and set the sampled flag to `01`. The Flask instrumentation extracts the header and makes its server span a child of yours.",
        "Ask Jaeger's API for that exact trace ID, and let jq from Day 2 print each span's name, own ID and parent ID. The `GET /` span has your fake caller `00f067aa0ba902b7` as its parent, and `INCRBY` hangs under it. Three services would chain the same way. Open http://localhost:16686/trace/4bf92f3577b34da6a3ce929d0e0e4736 to see the waterfall.",
        "Read the server span's attributes. They use the stable names. `client.address` arrived as a hash, because the Collector's transform processor replaced the IP address, and `user_agent.original` is gone. The last line is Jaeger noticing that the parent span never arrived, which is true: curl sent no span.",
        "Send a second made-up trace with the flag `00`, meaning 'the caller decided not to sample'. The app's sampler is parent-based, so it obeys and records nothing, and Jaeger has no such trace. This is how one sampling decision is kept across every service of a request.",
    ],
    "task": (
        [
            "Add the three `tracing/` files from this lesson to your hello-devops repo, next to `app.py` one folder up.",
            "Start the tracing lab and send 20 requests to http://localhost:8000/.",
            "In the Jaeger UI, open one normal trace and note the duration of each span.",
            "Pause Redis writes for 800 ms and send one request straight after.",
            "Search Jaeger for traces of hello-devops longer than 500 ms, open the one you made, and say which span took the time and how much of the total.",
            "Stop Redis, send a request, start Redis again, and find the error trace. Read the exception event on the span that failed.",
            "Stretch: run the app with a 10% ratio sampler, send 200 requests, and count how many traces Jaeger kept.",
        ],
        [
            "The Jaeger search form has Min Duration and Max Duration fields.",
            "`CLIENT PAUSE` only lasts for the milliseconds you give it, so have the curl command ready to run.",
            "For the stretch, the sampler is set with two `OTEL_TRACES_SAMPLER` variables in compose.yaml.",
        ],
        "You are done when you can point at the INCRBY span in a trace of about 800 ms and say it used almost all of the request's time.",
    ),
    "explain_back": (
        "Explain to a teammate how two services end up in the same trace in Jaeger, in 3 to 4 sentences. Mention spans, the traceparent header and the Collector.",
        "Each service creates spans, timed records of its own work, and every span carries a trace ID plus the ID of its parent span. When service A calls service B, its instrumentation puts the trace ID and A's current span ID into the traceparent header. B reads that header and starts its own span as a child in the same trace. Both services send their spans over OTLP to the Collector. The Collector can clean or sample them, then exports them to Jaeger, where they appear as one waterfall.",
    ),
    "recap": [
        "A trace is one request's story: a tree of timed spans that share a trace ID.",
        "The traceparent header carries the trace ID, the parent span ID and the sampled flag between services.",
        "OpenTelemetry gives you the API, SDK, auto-instrumentation, OTLP and the Collector, but no storage.",
        "opentelemetry-instrument traces a Python app with no code change, configured by OTEL_ variables.",
        "The Collector scrubs, samples and routes in one place; tail sampling there can keep every error and slow trace.",
        "Tracing shows the slow or failing call, but timeouts and retries still live in every app's own code.",
    ],
    "closing": CLOSING,
    "check": [
        ("A trace in Jaeger shows the frontend span, but the payment service's spans for the same request appear as a separate trace. What is the most likely cause?",
         "Without the propagated trace ID and parent span ID, the payment service starts a new trace of its own."),
        ("You must keep every trace that contains an error, but only about 5% of the successful ones. Where do you decide?",
         "Only a decision made after the trace ends can know whether it contained an error. The flag only says sampled or not."),
        ("You are about to add `user.email` as a span attribute so support can find a customer's requests. What does today's lab suggest instead?",
         "Personal data in telemetry spreads to every backend. The lab's transform processor shows how to hash or delete it in one place."),
    ],
    "interview": [
        ("What is the difference between a trace and a span, and how does context propagation work?",
         "A span is one timed operation, such as an HTTP handler or a database call, with attributes, events and a status. A trace is all the spans of one request, linked by a shared trace ID and parent span IDs into a tree. When a service calls another, its instrumentation writes the trace ID and its current span ID into a header, by default the W3C traceparent header. The receiver reads it and makes its spans children of the caller's span, so both appear in one trace."),
        ("Head sampling or tail sampling: what is the difference and when do you use each?",
         "Head sampling decides at the start of a trace, usually from the trace ID and a ratio, and the decision travels with the request so all services agree. It is cheap but blind: it may drop the rare error or slow trace. Tail sampling waits until a trace is complete, in a Collector, and can keep every error and slow trace plus a share of the rest. It needs memory for buffering, and all spans of a trace must reach the same Collector. So I use head sampling to cut volume, and tail sampling where error and latency traces matter."),
        ("Why put an OpenTelemetry Collector between your apps and the tracing backend?",
         "Apps then only know one OTLP endpoint, so changing or adding a backend is a Collector config change instead of a redeploy of every app. The Collector is also the one place to process data: batching, retries, memory limits, removing personal data and tail sampling. That work moves out of the app process. The cost is one more component to run and monitor, which is why small setups sometimes send straight to the backend."),
    ],
    "deeper": deeper,
    "drop": ["analogy", "mistake", "real_world"],
}

apply(14, "d57", new)
