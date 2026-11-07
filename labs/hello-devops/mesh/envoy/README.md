# Envoy lab: one proxy in front of two versions (Days 58 and 59)

Envoy listens on port 10000 and splits traffic 90/10 between two clusters:
`hello_v1` (two copies, `v1a` and `v1b`) and `hello_v2` (one canary, `v2`). It retries
failed requests on another host, gives up after 3 seconds, health-checks every host and
ejects a host that keeps failing. The admin interface is on port 9901.

```text
curl -> :10000 listener -> HTTP connection manager -> route (90/10) -> hello_v1 (v1a, v1b)
                                                                    -> hello_v2 (v2)
```

| File | What it does |
|---|---|
| `envoy.yaml` | Static Envoy config: listener, routes, retries, timeouts, health checks, outlier detection, circuit breakers, a fault filter switched off, and the admin interface |
| `compose.yaml` | Envoy `v1.40.2`, three hello-devops containers and two Redis containers |

## Run it

```bash
docker compose up -d
curl -s localhost:10000/
curl -s -H 'x-canary: always' localhost:10000/
for i in $(seq 1 200); do curl -s localhost:10000/ | jq -r .version; done | sort | uniq -c
curl -s localhost:9901/clusters | grep -E '::(hostname|health_flags|rq_total)::'
curl -s 'localhost:9901/stats?filter=^cluster\.hello_v1\.'
```

Break one copy: `v1b` loses its Redis, so `/` answers 500 there while `/healthz` stays 200.

```bash
docker compose stop redis-b
for i in $(seq 1 20); do curl -s -o /dev/null -w '%{http_code}\n' localhost:10000/; done | sort | uniq -c
curl -s 'localhost:9901/stats?filter=outlier_detection.ejections_active|upstream_rq_retry'
docker compose start redis-b
```

Fault injection at run time (Day 59), then switch it off again:

```bash
curl -s -X POST 'localhost:9901/runtime_modify?fault.http.abort.abort_percent=10&fault.http.delay.fixed_delay_percent=20'
curl -s -X POST 'localhost:9901/runtime_modify?fault.http.abort.abort_percent=0&fault.http.delay.fixed_delay_percent=0'
```

Stop with `docker compose down`.

## Notes

- Tested with Docker Engine 29 and Compose v5 on Linux, `envoyproxy/envoy:v1.40.2`.
  `envoy --mode validate -c envoy.yaml` passes. Real outputs from that run are in the
  Day 58 and Day 59 worked examples.
- `pull_policy: never` makes Compose use your local `hello-devops:1.0.0`. If Compose says
  the image does not exist, build it: `docker build -t hello-devops:1.0.0 ../..`.
- `no_traffic_interval: 5s`: without it, Envoy health-checks a cluster that has had no
  traffic yet only every 60 seconds. In the first test the apps were still starting when
  the first check ran, and every host stayed marked unhealthy for a minute.
- `max_ejection_percent: 50`: the default is 10%, which in a cluster of two hosts lets
  outlier detection eject nobody.
- `successful_active_health_check_uneject_host: false`: otherwise the next passing
  `/healthz` check puts an ejected host straight back.
- The admin interface can change Envoy's state and has no login. Never publish it beyond
  localhost.
