# Tracing lab: OpenTelemetry Collector and Jaeger (Day 49)

hello-devops runs under `opentelemetry-instrument`, with no change to `app.py`. Its spans
go to an OpenTelemetry Collector, which hashes the caller's IP address and forwards them
to Jaeger. You look at the traces in the Jaeger UI.

```text
hello-devops --OTLP:4317--> OpenTelemetry Collector --OTLP--> Jaeger (UI on 16686)
```

| File | What it does |
|---|---|
| `Dockerfile.otel` | Builds hello-devops plus `opentelemetry-distro` and the OTLP exporter, then runs `opentelemetry-bootstrap -a install` to add the Flask and Redis instrumentation |
| `otel-collector.yaml` | Collector pipeline: `otlp` receiver, `memory_limiter` and `transform` processors, `otlp_grpc` and `debug` exporters |
| `compose.yaml` | Jaeger, the Collector, the instrumented app and Redis |

## Run it

```bash
cd tracing
docker compose up -d --build
for i in $(seq 1 10); do curl -s localhost:8000/ > /dev/null; done
```

Open http://localhost:16686, pick the service `hello-devops` and select Find Traces.
Each trace has a `GET /` span from Flask and an `INCRBY` span from the Redis client.

Make one request slow by pausing Redis writes for 800 ms, then find it in Jaeger
(set Min Duration to 500ms):

```bash
docker compose exec redis redis-cli CLIENT PAUSE 800 WRITE
curl -s localhost:8000/
```

Make an error trace by stopping Redis:

```bash
docker compose stop redis
curl -s localhost:8000/          # 500
docker compose start redis
```

Stop with `docker compose down`. Jaeger all-in-one keeps traces in memory only, so they
are gone after a restart.

## Notes

- Images: `jaegertracing/jaeger:2.22.0` is Jaeger v2 from Docker Hub. The Jaeger docs
  pull the same image from `cr.jaegertracing.io/jaegertracing/jaeger`. The Collector is
  the core distribution, `otel/opentelemetry-collector:0.164.0`. The tail sampling
  processor is only in the larger contrib image, `otel/opentelemetry-collector-contrib`.
- Exporter names: Collector v0.144 renamed `otlp` to `otlp_grpc` and `otlphttp` to
  `otlp_http`. The old names still work but log `"otlp" alias is deprecated`.
  The old `jaeger` exporter is gone: send OTLP to Jaeger instead.
- `OTEL_SEMCONV_STABILITY_OPT_IN=http,database` makes the Python instrumentation use the
  stable attribute names (`http.request.method`, `http.response.status_code`,
  `client.address`, `db.system.name`). Without it you get the older names
  (`http.method`, `net.peer.ip`).
- Jaeger's HTTP API: `curl -s localhost:16686/api/v3/services` lists the services, and
  `curl -s localhost:16686/api/v3/traces/<trace id>` returns one trace as JSON.
- Metrics are switched off (`OTEL_METRICS_EXPORTER=none`). The OpenTelemetry docs list
  gunicorn with several workers as fine for traces but broken for metrics, and the course
  gets metrics from Prometheus anyway.
- Memory: the four containers used about 150 MB together on the test machine.
- Tested with Docker Engine 29 and Compose v5. The test build added a proxy certificate
  for `pip`, which you do not need on your laptop.
