# hello-devops

The tiny web app you ship all through "DevOps, from zero". This folder is the finished
reference: every file the lessons build, already tested. Use it to check your work, not to copy.

| Path | Built on |
|---|---|
| `app.py`, `test_app.py`, `requirements*.txt` | Day 2 (starter files) |
| `Dockerfile`, `.dockerignore` | Days 6 and 8 (pip removed on Day 22) |
| `compose.yaml` | Day 7 |
| `.github/pull_request_template.md` | Day 9 |
| `.github/workflows/ci.yml` | Days 10 and 11 |
| `.github/workflows/release.yml`, `.github/dependabot.yml` | Days 12 and 22 |
| `infra/local/` | Days 13 and 14 |
| `infra/aws/`, `.github/workflows/terraform.yml` | Day 15 |
| `kind-config.yaml`, `k8s/` | Days 16 to 18 |
| `chart/hello-devops/`, `chart/kind-values.yaml`, `k8s/gateway/` | Day 19 |
| `argocd/` | Day 20 |
| `observability/` | Day 21 |
| `policy/` | Day 22 (and Day 23 for the AI agent policy) |

Run it locally:

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt
pytest -q
python app.py   # then open http://localhost:8000
```
