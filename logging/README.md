# Logging lab: Elasticsearch, Kibana and Fluent Bit (Days 47 and 48)

A local EFK stack for learning. hello-devops prints its logs, Docker hands every line
to Fluent Bit, Fluent Bit turns them into JSON documents and sends them to
Elasticsearch, and you search them in Kibana.

**Local learning only.** Elasticsearch security is switched off (`xpack.security.enabled=false`),
so there are no passwords and no TLS. Anything that can reach port 9200 can read and
delete every log. Never run this compose file on a server.

| File | What it does | Day |
|---|---|---|
| `compose.yaml` | Elasticsearch, Kibana, Fluent Bit, hello-devops (with a JSON access log) and Redis | 47 |
| `fluent-bit.yaml` | The Fluent Bit pipeline: forward input, multiline and JSON parsing, Elasticsearch output | 47, 48 |
| `fluent-bit-values.yaml` | Helm values to run Fluent Bit as a DaemonSet on kind, sending to this Elasticsearch | 48 |

## Run it

```bash
cd logging
docker compose up -d --build
docker compose ps                     # wait until elasticsearch is "healthy"
curl -s localhost:9200                # Elasticsearch answers with its version
for i in $(seq 1 20); do curl -s localhost:8000/ > /dev/null; done
curl -s 'localhost:9200/_cat/indices/hello-logs-*?v'
```

Kibana takes a minute or two to start. Then open http://localhost:5601, go to
Discover, and create a data view with the index pattern `hello-logs-*` and the
timestamp field `@timestamp`.

To make some errors to search for, stop Redis and call the app:

```bash
docker compose stop redis
curl -s localhost:8000/          # 500: the app cannot reach Redis
curl -s localhost:8000/readyz    # 503
docker compose start redis
```

Stop everything and delete the stored logs with `docker compose down -v`.

## Memory notes

Elasticsearch and Kibana are the heavy parts. What `docker stats` showed on the test
machine with a little traffic:

| Container | Limit in compose.yaml | Used |
|---|---|---|
| elasticsearch | 2 GB (Java heap fixed at 1 GB) | about 1.6 GB |
| kibana | 2 GB | about 0.8 GB |
| fluent-bit | none | about 5 MB |
| web (hello-devops) | none | about 90 MB |

- Give Docker Desktop at least 6 GB of memory (Settings, Resources, Memory).
  Elastic's own docs ask for at least 4 GB for Elasticsearch alone.
- If you also run the tracing lab or a kind cluster at the same time, give it 8 GB.
- Kibana prints "running below the recommended minimum of 2GB of memory" when its
  limit is lower, which is why its limit is 2 GB.
- If Elasticsearch stops with exit code 137, it ran out of memory. Raise the Docker
  Desktop limit and run `docker compose up -d` again.
- On Linux, Elasticsearch may log a warning that `vm.max_map_count` is too low. In this
  single-node mode it is only a warning and it keeps running.

## Images

The files use Docker Hub images: `elasticsearch:9.5.5` and `kibana:9.5.5` (official
images that Elastic builds from its `elastic/dockerfiles` repository) and
`fluent/fluent-bit:5.1.5`. Elastic's docs pull the same images from
`docker.elastic.co/elasticsearch/elasticsearch:9.5.5` and
`docker.elastic.co/kibana/kibana:9.5.5`, and the Fluent Bit docs use
`cr.fluentbit.io/fluent/fluent-bit`. Either registry works. The lab was tested with the
Docker Hub images because the vendor registries were blocked on the test machine.
Elasticsearch and Kibana must always have the same version.

## Troubleshooting

- Nothing in Kibana? Run `docker compose logs fluent-bit`. If you see your records
  there, Elasticsearch is rejecting them, and `trace_error` prints its answer. If you
  see nothing, the web container is not reaching Fluent Bit on port 24224.
- Check the time picker in Discover. The default is the last 15 minutes.
- The web container uses the `fluentd` logging driver. Without `fluentd-async`, a
  container whose log collector is down stops immediately. `docker logs` still works,
  because Docker keeps a local copy of the lines.
- If your disk is almost full, Elasticsearch blocks writes to protect itself (it logs
  "flood stage disk watermark [95%] exceeded"). Free some disk space.

## Kubernetes (Day 48)

`fluent-bit-values.yaml` installs Fluent Bit on your kind cluster with the official Helm
chart. Elasticsearch and Kibana keep running from this compose file on your laptop, and
the DaemonSet sends to `host.docker.internal:9200`. On Linux, replace that host with the
gateway address of the `kind` Docker network (`docker network inspect kind`).

```bash
docker compose up -d elasticsearch kibana
helm repo add fluent https://fluent.github.io/helm-charts
helm upgrade --install fluent-bit fluent/fluent-bit \
  --namespace logging --create-namespace -f fluent-bit-values.yaml
kubectl -n logging get pods -o wide   # one pod per node
```

Then create a data view `k8s-logs-*` in Kibana. Fluent Bit only reads lines written
after it starts, so send some traffic to the app first.

The values were checked with `helm lint`, `helm template` and `kubeconform` against chart
version 0.58.3, and the pipeline was run with Fluent Bit 5.1.5 against sample container
log files. A kind cluster could not run on the test machine, so try it and report back
if the DaemonSet cannot reach Elasticsearch.
