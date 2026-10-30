# hello-devops

The tiny web app you ship all through "DevOps, from zero". This folder is the finished
reference: every file the lessons build, already tested. Use it to check your work, not to copy.

| Path | Built on |
|---|---|
| `app.py`, `test_app.py`, `requirements*.txt` | Day 2 (starter files) |
| `Dockerfile`, `.dockerignore` | Days 6 and 8 |
| `compose.yaml` | Day 7 |
| `.github/workflows/ci.yml` | Days 10 and 11 |
| `.github/workflows/release.yml` | Days 12 and 22 |
| `infra/local/` | Days 13 and 14 |
| `infra/aws/`, `.github/workflows/terraform.yml` | Day 15 |
| `kind-config.yaml`, `k8s/` | Days 16 to 18 |
| `chart/hello-devops/` | Day 19 |
| `argocd/` | Day 20 |

Run it locally:

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt
pytest -q
python app.py   # then open http://localhost:8000
```
