# hello-devops

The tiny web app you ship all through "DevOps, from zero". This folder is the finished
reference: every file the lessons build, already checked. Use it to compare your work, not to copy.

| Path | Built on |
|---|---|
| `app.py`, `test_app.py`, `requirements*.txt`, `.gitignore` | Day 2 (starter files) |
| `.dockerignore`, `docker/` | Days 13 to 15 |
| `Dockerfile` | Days 13 and 16 (pip removed on Day 52) |
| `compose.yaml` | Day 15 |
| `.github/pull_request_template.md` | Day 17 |
| `.github/workflows/ci.yml`, `.github/actions/` | Days 18 to 20 |
| `.github/workflows/release.yml`, `.github/dependabot.yml` | Days 21 and 52 |
| `infra/local/`, `infra/modules/` | Days 25 to 28 |
| `infra/aws/`, `.github/workflows/terraform.yml` | Day 29 |
| `kind-config.yaml`, `k8s/`, `k8s/examples/` | Days 30 to 35 |
| `k8s/gateway/` | Day 36 |
| `chart/`, `overlays/` | Day 37 |
| `k8s-broken/` | Day 38 (break-and-fix lab) |
| `argocd/`, `gitops/` | Days 39 and 40 |
| `observability/` | Days 42 to 46 (Prometheus, Alertmanager, Grafana, Loki) |
| `logging/` | Days 47 and 48 (Elasticsearch, Kibana, Fluent Bit) |
| `tracing/` | Day 49 (OpenTelemetry Collector, Jaeger) |
| `dynatrace/` | Day 51 |
| `policy/`, `security/` | Day 53 (and Day 54 for the AI agent policy) |

Other lab folders in this repo: `labs/linux/` (Days 3 to 7), `labs/hello-jvm/` (Days 22 to 24),
`labs/terraform-practice/` (Days 26 and 27).

Run it locally:

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt
pytest -q
python app.py   # then open http://localhost:8000
```
