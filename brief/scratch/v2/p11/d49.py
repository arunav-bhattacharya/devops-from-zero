"""Day 49: Distributed tracing with OpenTelemetry."""
from common import lab, ref
import svg

TP = "00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-01"

L = {
    "id": "d49",
    "title": "Distributed tracing with OpenTelemetry",
    "minutes": 50,
    "goal": "By the end you can explain spans, traces and context propagation, run hello-devops under opentelemetry-instrument with a Collector and Jaeger, and use a trace to find the slow step of a request.",
    "guess": {
        "q": "One request to hello-devops took 835 ms. Its access log line says status 200, and the error rate on your dashboard is 0%. What shows you where those 835 ms went?",
        "options": [
            "The gunicorn access log line for the request",
            "The Prometheus counter hello_requests_total",
            "The container's CPU graph for that minute",
            "A trace of the request, split into timed spans",
        ],
        "answer": 3,
        "why": "Logs and metrics tell you that the request happened and how often. Only a trace records each step of one request with its own start time and duration, so you can see which step was slow.",
    },
    "terms": [
        {"term": "Trace", "plain": "The record of one request's whole path, made of spans that share one trace ID."},
        {"term": "Span", "plain": "One timed operation inside a trace, such as handling GET / or sending one Redis command."},
        {"term": "Context propagation", "plain": "Passing the trace ID and the current span ID to the next service, usually in an HTTP header."},
        {"term": "traceparent", "plain": "The W3C HTTP header that carries a version, the trace ID, the parent span ID and a sampled flag."},
        {"term": "Sampling", "plain": "Keeping only some traces to save money. Head sampling decides at the start, tail sampling after the end."},
        {"term": "OTLP", "plain": "The OpenTelemetry Protocol for sending telemetry: gRPC on port 4317, HTTP on port 4318."},
        {"term": "OpenTelemetry Collector", "plain": "A service that receives telemetry, processes it and exports it to one or more backends."},
        {"term": "Jaeger", "plain": "An open-source tracing backend that stores traces and shows them in a web UI."},
    ],
    "sections": [
        {
            "h": "Why logs and metrics cannot find the slow step",
            "body": """Picture a checkout request on a payments site. It enters an API service, which calls a fraud check, which calls a card partner, while the API also writes to a database. The customer waited three seconds. Which hop took them?

Metrics give you averages per service: the 95th percentile of the fraud check went up. Logs give you lines per service, each with its own timestamp, and you have to guess which lines belong to this one request. Neither tells you that this request spent 2.6 of its 3 seconds waiting for the card partner.

A trace does. It is the story of one request, told as a tree of timed steps. Each step is a span: a name, a start time, an end time, and some facts about what happened. Draw the spans on a timeline, one row each, and the slow step is the longest bar with nothing underneath it. That picture is called a waterfall, and it is what Jaeger shows you.

Even hello-devops, one service and Redis, benefits. In the lab I paused Redis writes for 800 ms and sent one request. The trace showed `GET /` taking 835 ms, and its child span `INCRBY` taking 832 ms of them. Without the trace you see a slow request. With it you see a slow Redis call, and you know where to look next.

In Part 9 you met the signals, and here is how they divide the work in practice. A metric alert says something is wrong. A trace says where. The logs of that one request say why.""",
            "refs": [
                ref("OpenTelemetry: traces", "https://opentelemetry.io/docs/concepts/signals/traces/", "docs"),
            ],
        },
        {
            "h": "Spans and traces",
            "body": """A span records one operation. In OpenTelemetry every span has:
- a name, such as `GET /` or `INCRBY`
- a start and end time, so a duration
- a trace ID, shared by every span in the same trace
- its own span ID, and the span ID of its parent
- attributes: key and value facts, such as `http.response.status_code = 200`
- events: timestamped notes inside the span, such as an exception
- a status: Unset, Ok or Error
- a kind: server, client, internal, producer or consumer

The parent span IDs make the tree. The first span of a request has no parent and is called the root span. In the lab, a normal request gives two spans with the same trace ID:
- `GET /`, kind server, 6.5 ms, from the Flask instrumentation. It is the root.
- `INCRBY`, kind client, 3.4 ms, from the Redis instrumentation. Its parent is the `GET /` span.

When Redis was stopped, both spans got status Error and an `exception` event with the type `redis.exceptions.ConnectionError`, its message and the stack trace. The trace carries the error with it, so you do not have to find the matching log line first.

Attribute names follow shared rules called semantic conventions, so every tool agrees that the HTTP method is `http.request.method`. Python instrumentation still uses older names unless you opt in with `OTEL_SEMCONV_STABILITY_OPT_IN=http,database`, which the lab sets. Without it you see `http.method` and `net.peer.ip` instead. Tutorials use both, so do not be surprised by either.""",
            "refs": [
                ref("OpenTelemetry: traces", "https://opentelemetry.io/docs/concepts/signals/traces/", "docs"),
                ref("OpenTelemetry Python: semantic convention stability", "https://opentelemetry.io/docs/languages/python/instrumentation/", "docs"),
            ],
        },
        {
            "h": "Context propagation and the traceparent header",
            "body": """Spans from different services only join into one trace if each service tells the next one which trace it is in. That hand-over is context propagation. The caller injects the context into the outgoing request, and the receiver extracts it and starts its own span as a child.

For HTTP, OpenTelemetry uses the W3C Trace Context header by default:

`traceparent: 00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-01`

It has four parts, split by dashes:
1. `00` is the version of the format.
2. `4bf92f3577b34da6a3ce929d0e0e4736` is the trace ID: 32 hex characters (16 bytes).
3. `00f067aa0ba902b7` is the parent span ID: 16 hex characters, the caller's current span.
4. `01` is the flags. `01` means sampled: the caller is recording this trace.

You can play the caller yourself with curl, which is what the worked example does. Send that header to hello-devops, and Jaeger files the `GET /` span under trace `4bf92f...` with parent `00f067aa0ba902b7`. Jaeger also warns that this parent is not in the trace, which is true: curl never reported a span.

You rarely write this header by hand. Instrumented HTTP clients, such as Python's `requests` or the Java agent's HTTP clients, add it to every outgoing call. The trouble starts at hops that do not pass it on: a proxy that strips unknown headers, a message queue without instrumentation, or a homemade HTTP client. The trace then breaks into two traces that look unrelated. When a trace stops early in Jaeger, look for that hop first.""",
            "refs": [
                ref("OpenTelemetry: context propagation", "https://opentelemetry.io/docs/concepts/context-propagation/", "docs"),
                ref("W3C Trace Context", "https://www.w3.org/TR/trace-context/", "read"),
            ],
        },
        {
            "h": "OpenTelemetry: API, SDK, instrumentation",
            "body": """OpenTelemetry, OTel for short, is a CNCF project that standardizes how apps produce telemetry. It is not a backend: it stores nothing. It gives you these parts:
- the API: the functions your code calls to start spans
- the SDK: the engine behind the API, which samples, batches and exports
- instrumentation libraries, which create spans for frameworks such as Flask, Redis or JDBC
- OTLP, one protocol for traces, metrics and logs
- the Collector, covered in the next section

For many apps you write no tracing code. In Python, zero-code instrumentation takes three steps, and `tracing/Dockerfile.otel` does all three:
1. `pip install opentelemetry-distro opentelemetry-exporter-otlp`
2. `opentelemetry-bootstrap -a install` looks at your installed packages and adds the matching instrumentation. For hello-devops it found Flask, Redis and a dozen others.
3. Prefix your start command with `opentelemetry-instrument`. The lab runs `opentelemetry-instrument gunicorn ...` and `app.py` stays untouched.

Settings come from `OTEL_` environment variables, the same names in every language:
- `OTEL_SERVICE_NAME=hello-devops` names the service in every backend.
- `OTEL_EXPORTER_OTLP_ENDPOINT=http://otel-collector:4317` says where to send.
- `OTEL_TRACES_EXPORTER=console` prints spans to the terminal, handy when no backend runs.

For your JVM services the idea is the same: add the OpenTelemetry Java agent with `-javaagent:opentelemetry-javaagent.jar`, set the same variables, and Spring, JDBC and HTTP clients get spans.

Auto-instrumentation shows the plumbing. For business steps, such as "price the basket", you add a manual span with the API, for example `with tracer.start_as_current_span("price-basket"):` in Python. One caveat from the OTel docs: gunicorn with several workers is fine for traces but breaks auto-instrumented metrics, which is why the lab switches metrics off.""",
            "refs": [
                ref("OpenTelemetry: Python zero-code instrumentation", "https://opentelemetry.io/docs/zero-code/python/", "docs"),
                ref("OpenTelemetry: Java agent", "https://opentelemetry.io/docs/zero-code/java/agent/", "docs"),
                ref("OpenTelemetry: the vision, reality, and how to get started (Dotan Horovits, KubeCon NA 2022)", "https://www.youtube.com/watch?v=qE1ggEmvz2Y", "watch"),
            ],
        },
        {
            "h": "The Collector: receivers, processors, exporters",
            "body": """Apps can send spans straight to a backend. Most teams put an OpenTelemetry Collector in between, for three reasons:
- One place to change data: drop noise, remove personal data, add attributes.
- Apps stay simple: they send OTLP to one address and never learn about the backend.
- You can switch or add backends by editing one config file, without redeploying apps.

A Collector config has the same shape as Fluent Bit's pipeline from Day 47. Receivers take data in, processors change it, exporters send it out, and `service.pipelines` wires them together per signal. The lab's `tracing/otel-collector.yaml` reads like this:
1. The `otlp` receiver listens on 4317 (gRPC) and 4318 (HTTP).
2. `memory_limiter` refuses data before the Collector runs out of memory.
3. `transform/scrub` hashes `client.address`, because an IP address is personal data, and deletes `user_agent.original`.
4. The `otlp_grpc/jaeger` exporter sends batches to Jaeger, and `debug` prints a line per batch in the Collector's log.

In the lab, the hashed address really arrived in Jaeger as a 64-character hex string. The same caller always gets the same hash, so you can still count unique callers without storing who they are.

Version drift bites here. Collector v0.144 renamed the `otlp` exporter to `otlp_grpc` and `otlphttp` to `otlp_http`. The old names still work but log a deprecation warning. Older tutorials also show a `jaeger` exporter, which no longer exists. Jaeger speaks OTLP now. Even the core image's `attributes` processor warned that it leaves the core distribution in v0.167, which is why the lab uses `transform`.

There are two main Collector images. The core image, `otel/opentelemetry-collector`, is small and has the basics. The contrib image has the much larger set of components, including tail sampling.""",
            "refs": [
                ref("OpenTelemetry: Collector configuration", "https://opentelemetry.io/docs/collector/configuration/", "docs"),
                ref("OpenTelemetry: transforming telemetry", "https://opentelemetry.io/docs/collector/transforming-telemetry/", "docs"),
            ],
        },
        {
            "h": "Sampling: head and tail",
            "body": """Tracing every request costs CPU in your app, network and storage. At high traffic most teams keep only some traces, which is sampling. The OpenTelemetry docs say that for high-volume systems a rate of 1% or lower often represents the rest very well.

The SDK's default sampler is `parentbased_always_on`. In plain words: follow the caller's decision if there is one, otherwise keep everything. That is right for a lab and usually wrong for a busy production service.

Head sampling decides when the trace starts, from the trace ID. Set `OTEL_TRACES_SAMPLER=parentbased_traceidratio` and `OTEL_TRACES_SAMPLER_ARG=0.1`, and about 1 trace in 10 is kept. I ran 200 requests that way against the lab and Jaeger held 17 of them. The decision then travels in the sampled flag of `traceparent`, so every service keeps or drops the same trace. You saw that in the lab too: a request with flag `00` left no trace at all.

Head sampling has a blind spot. It decides before anything has happened, so it cannot promise to keep the traces you care about most, the failed and the slow ones.

Tail sampling decides after the trace is complete. A Collector buffers the spans for a few seconds, looks at the whole trace, and applies rules such as:
- keep every trace with an error
- keep every trace slower than 500 ms
- keep 10% of everything else

The price is memory and a design rule: all spans of one trace must reach the same Collector instance. Tail sampling lives in the contrib Collector, and the deeper section shows a config.""",
            "refs": [
                ref("OpenTelemetry: sampling", "https://opentelemetry.io/docs/concepts/sampling/", "docs"),
                ref("OpenTelemetry: SDK configuration (samplers)", "https://opentelemetry.io/docs/languages/sdk-configuration/general/", "docs"),
            ],
        },
        {
            "h": "Backends, and joining traces to logs and metrics",
            "body": """The Collector sends spans somewhere that stores and shows them. The common open-source choices:
- Jaeger. Version 2 is built on the OpenTelemetry Collector itself, and version 1 has reached end of life. The all-in-one image you run in the lab keeps traces in memory, so they vanish on restart. For real use it stores to Elasticsearch, OpenSearch, Cassandra or ClickHouse.
- Grafana Tempo, from Day 46. It needs only object storage and is queried with TraceQL.
- Commercial platforms. Dynatrace (Day 50) and Elastic both accept OTLP, so the same Collector config can send there.

Traces get most useful when the three signals point at each other. The thread that ties them together is the trace ID:
- In logs: write the trace ID on every line. For Python, `OTEL_PYTHON_LOG_CORRELATION=true` adds the trace and span IDs to log records. Then a Kibana search for one trace ID returns every log line of that request, across services.
- In metrics: Prometheus can attach a trace ID to a histogram sample, called an exemplar, so a latency spike on a Grafana graph links to an example trace.
- In the UI: Grafana and Kibana can link from a span to its logs and back.

A habit worth building: when you add a log line in a service that is traced, make sure the trace ID ends up in it. It costs a few bytes per line, and it is the difference between 'errors went up' and 'here is request 4bf92f..., and here is everything it did'.""",
            "refs": [
                ref("Jaeger: getting started (v2)", "https://www.jaegertracing.io/docs/2.22/getting-started/", "docs"),
                ref("Jaeger v2 unveiled: tracing powered by OpenTelemetry (OpenObservability Talks, with Yuri Shkuro)", "https://www.youtube.com/watch?v=lICivVwm-F8", "watch"),
            ],
        },
    ],
    "analogy": "A trace is a parcel's tracking history. The tracking number on the label (the trace ID in `traceparent`) is copied onto every new label as the parcel moves on. Each depot adds a scan with its arrival and departure times (a span). Looking at all the scans for one number shows where the parcel sat for two days. Where it breaks: a courier keeps every parcel's history. A busy system usually samples and keeps only some traces, so the request you care about may never have been recorded.",
    "diagram": svg.d49(),
    "diagram_caption": "The real slow trace from the lab: the GET / server span lasted 835 ms, and its Redis child span INCRBY used 832 ms of that, so Redis is the slow step.",
    "worked": {
        "title": "Follow a traceparent header into Jaeger",
        "steps": [
            {
                "say": "Start the tracing lab. Compose builds the instrumented image from `tracing/Dockerfile.otel`, then starts Jaeger, the Collector, the app and Redis. A normal request answers as always: the app does not know it is being traced.",
                "code": """$ cd tracing
$ docker compose up -d --build
$ curl -s localhost:8000/
{"host":"7b9644166a1a","message":"Hello, DevOps!","version":"1.0.0","visits":1}""",
                "lang": "console",
            },
            {
                "say": "Now pretend to be an upstream service that is already tracing this request. You choose the trace ID and your own span ID, and set the sampled flag to `01`. The Flask instrumentation extracts the header and makes its server span a child of yours.",
                "code": f"""$ curl -s -o /dev/null -w '%{{http_code}}\\n' -H 'traceparent: {TP}' localhost:8000/
200""",
                "lang": "console",
            },
            {
                "say": "Ask Jaeger's API for that exact trace ID, and let jq from Day 2 print each span's name, own ID and parent ID. The `GET /` span has your fake caller `00f067aa0ba902b7` as its parent, and `INCRBY` hangs under it. Three services would chain the same way. Open http://localhost:16686/trace/4bf92f3577b34da6a3ce929d0e0e4736 to see the waterfall.",
                "code": """$ curl -s localhost:16686/api/v3/traces/4bf92f3577b34da6a3ce929d0e0e4736 \\
    | jq -r '.result.resourceSpans[].scopeSpans[].spans[] | [.name, .spanId, (.parentSpanId // "-")] | @tsv'
GET /	3ac93496b7a0eb5b	00f067aa0ba902b7
INCRBY	0d6fc47a7154a749	3ac93496b7a0eb5b""",
                "lang": "console",
            },
            {
                "say": "Read the server span's attributes. They use the stable names, `client.address` arrived as a hash because the Collector's transform processor replaced the IP, and `user_agent.original` is gone. The last line is Jaeger noticing that the parent span never arrived, which is true: curl sent no span.",
                "code": """$ curl -s localhost:16686/api/v3/traces/4bf92f3577b34da6a3ce929d0e0e4736 \\
    | jq -r '.result.resourceSpans[].scopeSpans[].spans[] | select(.name == "GET /") | .attributes[] | "\\(.key) = \\(.value | to_entries[0].value)"'
client.address = 79f1ed7c3831720253675dcf97a9714711e3e0ec94b6abf77f5bbf0280dc9c0d
client.port = 43298
http.request.method = GET
http.response.status_code = 200
http.route = /
network.protocol.version = 1.1
server.address = localhost:8000
server.port = 8000
url.path = /
url.scheme = http
@jaeger@warnings = {"values":[{"stringValue":"parent span ID=00f067aa0ba902b7 is not in the trace; skipping clock skew adjustment"}]}""",
                "lang": "console",
            },
            {
                "say": "Send a second made-up trace with the flag `00`, meaning 'the caller decided not to sample'. The app's sampler is parent-based, so it obeys and records nothing. Jaeger has no such trace. This is how one sampling decision is kept across every service of a request.",
                "code": """$ curl -s -o /dev/null -H 'traceparent: 00-0af7651916cd43dd8448eb211c80319c-b7ad6b7169203331-00' localhost:8000/
$ curl -s localhost:16686/api/v3/traces/0af7651916cd43dd8448eb211c80319c
{"error":{"httpCode":404,"message":"No traces found"}}""",
                "lang": "console",
            },
        ],
    },
    "code": [
        {"lang": "dockerfile", "title": "tracing/Dockerfile.otel", "src": lab("tracing/Dockerfile.otel"), "run": "docker build -f tracing/Dockerfile.otel -t hello-devops:otel ."},
        {"lang": "yaml", "title": "tracing/otel-collector.yaml", "src": lab("tracing/otel-collector.yaml"),
         "run": "docker run --rm -v \"$PWD/tracing/otel-collector.yaml:/c.yaml:ro\" otel/opentelemetry-collector:0.164.0 validate --config=/c.yaml"},
        {"lang": "yaml", "title": "tracing/compose.yaml", "src": lab("tracing/compose.yaml"), "run": "cd tracing && docker compose up -d --build"},
    ],
    "commands": [
        {"cmd": "cd tracing && docker compose up -d --build", "what": "Build the instrumented app and start Jaeger, the Collector, the app and Redis."},
        {"cmd": "docker compose logs -f otel-collector", "what": "Follow the Collector's log. The debug exporter prints one line per batch of spans."},
        {"cmd": "open http://localhost:16686", "what": "Open the Jaeger UI on your Mac. Pick the service hello-devops and select Find Traces."},
        {"cmd": "curl -s -H 'traceparent: 00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-01' localhost:8000/", "what": "Send a request that joins a trace you chose, as an upstream service would."},
        {"cmd": "curl -s localhost:16686/api/v3/services", "what": "List the services Jaeger has seen spans from."},
        {"cmd": "curl -s localhost:16686/api/v3/traces/<trace-id> | jq .", "what": "Fetch one trace from Jaeger as JSON."},
        {"cmd": "docker compose exec redis redis-cli CLIENT PAUSE 800 WRITE", "what": "Hold Redis writes for 800 ms, so the next request has a slow span to find."},
        {"cmd": "docker compose stop redis", "what": "Stop Redis so requests fail and produce error spans. Start it again with `docker compose start redis`."},
        {"cmd": "docker run --rm -v \"$PWD/otel-collector.yaml:/c.yaml:ro\" otel/opentelemetry-collector:0.164.0 validate --config=/c.yaml", "what": "Check a Collector config without starting it. No output means it is valid."},
        {"cmd": "pip install opentelemetry-distro opentelemetry-exporter-otlp && opentelemetry-bootstrap -a install", "what": "Add zero-code OpenTelemetry to a Python environment, with instrumentation for the packages it finds."},
        {"cmd": "OTEL_SERVICE_NAME=hello-devops OTEL_TRACES_EXPORTER=console OTEL_METRICS_EXPORTER=none opentelemetry-instrument python app.py", "what": "Run the app locally and print every span to the terminal, with no backend at all."},
        {"cmd": "docker compose down", "what": "Stop the tracing lab. Jaeger's in-memory traces are gone after this."},
    ],
    "mistake": "Copying a Collector config from an older tutorial. A `jaeger:` exporter now stops the Collector with `'exporters' unknown type: \"jaeger\"`, and `otlp:` still works but logs `\"otlp\" alias is deprecated; use \"otlp_grpc\" instead`. Send OTLP to Jaeger with the `otlp_grpc` exporter, and run `otelcol validate` (the `validate` command in the worked commands) on every config change before you deploy it.",
    "real_world": "A payments team traces every service with OpenTelemetry. Its Collector tier uses tail sampling to keep all traces with an error, all slower than two seconds, and 5% of the rest. The Collector also hashes client IPs and removes card-related attributes before anything leaves the cluster. When the checkout latency alert fires, on-call opens an example slow trace and sees the time spent in the call to the card partner. Then they search the logs by that trace ID.",
    "task": {
        "title": "Find the slow span",
        "steps": [
            "Add the three `tracing/` files from this lesson to your hello-devops repo, next to `app.py` one folder up.",
            "Start the tracing lab and send 20 requests to http://localhost:8000/.",
            "In the Jaeger UI, open one normal trace and note the duration of each span.",
            "Pause Redis writes for 800 ms and send one request straight after.",
            "Search Jaeger for traces of hello-devops longer than 500 ms, open the one you made, and say which span took the time and how much of the total.",
            "Stop Redis, send a request, start Redis again, and find the error trace. Read the exception event on the span that failed.",
            "Stretch: run the app with a 10% ratio sampler, send 200 requests, and count how many traces Jaeger kept.",
        ],
        "hints": [
            "The Jaeger search form has Min Duration and Max Duration fields.",
            "`CLIENT PAUSE` only lasts for the milliseconds you give it, so have the curl command ready to run.",
            "For the stretch, the sampler is set with two `OTEL_TRACES_SAMPLER` variables in compose.yaml.",
        ],
        "done_when": "You are done when you can point at the INCRBY span in a trace of about 800 ms and say it used almost all of the request's time.",
    },
    "explain_back": {
        "prompt": "Explain to a teammate how two services end up in the same trace in Jaeger, in 3 to 4 sentences. Mention spans, the traceparent header and the Collector.",
        "answer": "Each service creates spans, timed records of its own work, and every span carries a trace ID plus the ID of its parent span. When service A calls service B, its instrumentation puts the trace ID and A's current span ID into the traceparent header. B reads that header and starts its own span as a child in the same trace. Both services send their spans over OTLP to the Collector, which can clean or sample them and then exports them to Jaeger, where they appear as one waterfall.",
    },
    "recap": [
        "A trace is one request's story: a tree of timed spans that share a trace ID.",
        "The traceparent header carries the trace ID, the parent span ID and the sampled flag between services.",
        "OpenTelemetry gives you the API, SDK, auto-instrumentation, OTLP and the Collector, but no storage.",
        "opentelemetry-instrument traces a Python app with no code change, configured by OTEL_ variables.",
        "The Collector's receivers, processors and exporters let you scrub, sample and route in one place.",
        "Head sampling decides at the start; tail sampling in the Collector can keep every error and slow trace.",
    ],
    "check": [
        {
            "q": "A trace in Jaeger shows the frontend span, but the payment service's spans for the same request appear as a separate trace. What is the most likely cause?",
            "options": [
                "Jaeger's in-memory storage dropped half of the spans",
                "The two services use different service names",
                "The call between them did not carry the traceparent header",
                "The payment service samples at 100% and the frontend at 10%",
            ],
            "answer": 2,
            "why": "Without the propagated trace ID and parent span ID, the payment service starts a new trace of its own.",
        },
        {
            "q": "You must keep every trace that contains an error, but only about 5% of the successful ones. Where do you decide?",
            "options": [
                "In each app's SDK, with a 5% ratio sampler",
                "In a Collector with tail sampling, after the traces complete",
                "In Jaeger, by deleting successful traces every night",
                "In the traceparent header, by setting the flag to 05",
            ],
            "answer": 1,
            "why": "Only a decision made after the trace ends can know whether it contained an error; the flag is just sampled or not.",
        },
        {
            "q": "You are about to add `user.email` as a span attribute so support can find a customer's requests. What does today's lab suggest instead?",
            "options": [
                "Add it, because span attributes are internal debug data",
                "Add it as the service name so it is easy to filter",
                "Put it in the traceparent header so every service sees it",
                "Hash or drop it in the Collector, or log a non-personal customer ID",
            ],
            "answer": 3,
            "why": "Personal data in telemetry spreads to every backend; the lab's transform processor shows how to hash or delete it in one place.",
        },
    ],
    "interview": [
        {
            "q": "What is the difference between a trace and a span, and how does context propagation work?",
            "a": "A span is one timed operation, such as an HTTP handler or a database call, with attributes, events and a status. A trace is all the spans of one request, linked by a shared trace ID and parent span IDs into a tree. When a service calls another, its instrumentation writes the trace ID and its current span ID into a header, by default the W3C traceparent header. The receiver reads it and makes its spans children of the caller's span, so both appear in one trace.",
        },
        {
            "q": "Head sampling or tail sampling: what is the difference and when do you use each?",
            "a": "Head sampling decides at the start of a trace, usually from the trace ID and a ratio, and the decision travels with the request so all services agree. It is cheap but blind: it may drop the rare error or slow trace. Tail sampling waits until a trace is complete, in a Collector, and can keep every error and slow trace plus a share of the rest. It needs memory for buffering, and all spans of a trace must reach the same Collector. So I use head sampling to cut volume, and tail sampling where error and latency traces matter.",
        },
        {
            "q": "Why put an OpenTelemetry Collector between your apps and the tracing backend?",
            "a": "Apps then only know one OTLP endpoint, so changing or adding a backend is a Collector config change instead of a redeploy of every app. The Collector is also the one place to process data: batching, retries, memory limits, removing personal data and tail sampling. It moves that work out of the app process. The cost is one more component to run and monitor, which is why small setups sometimes send straight to the backend.",
        },
    ],
    "deeper": {
        "minutes": 14,
        "body": """Tail sampling needs the contrib Collector (`otel/opentelemetry-collector-contrib`), because the `tail_sampling` processor is not in the core image. You add it to the processors of the traces pipeline, after `memory_limiter`. Its settings, from the processor's README:
- `decision_wait`: how long to buffer a trace's spans before deciding. The default is 30 seconds; 10 seconds is a common choice.
- `num_traces`: how many traces to hold in memory while waiting.
- `policies`: a list of rules. If any policy votes to sample, the trace is kept, unless a policy explicitly votes to drop it.

A policy list that matches the lesson looks like this, written in YAML under `policies`:
- `{name: errors, type: status_code, status_code: {status_codes: [ERROR]}}` keeps every trace with an error span.
- `{name: slow, type: latency, latency: {threshold_ms: 500}}` keeps every trace longer than 500 ms, measured from the earliest span start to the latest span end.
- `{name: some-of-the-rest, type: probabilistic, probabilistic: {sampling_percentage: 10}}` keeps 10% of everything else, chosen by hashing the trace ID.

Two consequences are worth thinking through before you run this in production.

First, memory. The Collector holds every span of every trace in flight for `decision_wait`. At 1,000 requests a second with 10 spans each, a 10-second wait means about 100,000 spans in memory at once. That is why `memory_limiter` comes first in the pipeline and why tail sampling Collectors get their own resource limits.

Second, scale-out. The README says all spans of a trace must be received by the same Collector instance. With three Collector replicas behind a normal load balancer, each one sees a third of every trace and decides badly. The usual fix is two tiers of Collectors. The first tier only forwards, with the load-balancing exporter, which routes spans by trace ID. The second tier does the tail sampling. The OpenTelemetry docs on scaling the Collector describe this layout.

Head and tail sampling can work together. A service can head-sample at 50% to cut the load on its own process, and the Collector then tail-samples what arrives. Just remember that anything head sampling dropped is gone for good, errors included. If you need every error, the SDK has to keep every trace, and only the Collector may sample.

For hello-devops there is a simple way to see the effect. Run the contrib image with these three policies, send 100 normal requests and 5 slow ones (with `CLIENT PAUSE`), and count traces in Jaeger. You should find all 5 slow ones and roughly 10 of the fast ones.""",
    },
    "sources": [
        {"title": "OpenTelemetry: traces", "url": "https://opentelemetry.io/docs/concepts/signals/traces/"},
        {"title": "OpenTelemetry: sampling", "url": "https://opentelemetry.io/docs/concepts/sampling/"},
        {"title": "OpenTelemetry: Collector configuration", "url": "https://opentelemetry.io/docs/collector/configuration/"},
        {"title": "Jaeger: getting started (v2)", "url": "https://www.jaegertracing.io/docs/2.22/getting-started/"},
    ],
}
