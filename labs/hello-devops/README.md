# hello-devops

The tiny web app you ship all through "DevOps, from zero". This folder is the finished
reference: every file the lessons build, already checked. Use it to compare your work, not to copy.

| Path | Built on |
|---|---|
| `app.py`, `test_app.py`, `requirements*.txt`, `.gitignore` | Day 2 (starter files) |
| `.dockerignore`, `docker/` | Days 19 to 21 |
| `Dockerfile` | Days 19 and 22 (pip removed on Day 63) |
| `compose.yaml` | Day 21 |
| `.github/pull_request_template.md` | Day 23 |
| `.github/workflows/ci.yml`, `.github/actions/` | Days 24 to 26 |
| `.github/workflows/release.yml`, `.github/dependabot.yml` | Days 27 and 63 |
| `infra/local/`, `infra/modules/` | Days 31 to 34 |
| `infra/aws/`, `.github/workflows/terraform.yml` | Day 35 |
| `kind-config.yaml`, `k8s/`, `k8s/examples/` | Days 38 to 43 |
| `k8s/gateway/` | Day 44 |
| `chart/`, `overlays/` | Day 45 |
| `k8s-broken/` | Day 46 (break-and-fix lab) |
| `argocd/`, `gitops/` | Days 47 and 48 |
| `observability/` | Days 50 to 54 (Prometheus, Alertmanager, Grafana, Loki) |
| `logging/` | Days 55 and 56 (Elasticsearch, Kibana, Fluent Bit) |
| `tracing/` | Day 57 (OpenTelemetry Collector, Jaeger) |
| `mesh/` | Days 58 to 60 (Envoy with Compose; Istio sidecar and ambient manifests; Linkerd GAMMA route and checklist) |
| `dynatrace/` | Day 62 |
| `policy/`, `security/` | Day 64 (and Day 66 for the AI agent policy and kubeconfig) |
| `ai/` | Days 65 and 66 (AGENTS.md, review checklist, MCP config, read-only RBAC, AI review workflow) |

Other lab folders in this repo: `labs/linux/` (Days 3 to 7), `labs/hello-jvm/` (Days 28 to 30),
`labs/terraform-practice/` (Days 32 and 33).

Run it locally:

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt
pytest -q
python app.py   # then open http://localhost:8000
```
