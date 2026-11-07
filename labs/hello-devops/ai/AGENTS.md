# AGENTS.md for hello-devops

Instructions for AI coding agents, and for new teammates, who work in this repository.
Copy this file to the root of your hello-devops repository (Day 65). Agents that read
AGENTS.md pick it up from there. For Claude Code, add a one-line `CLAUDE.md` that says
`@AGENTS.md`. Keep this file short: agents read it on every task.

## What this repository is

hello-devops is a small Flask web app from the course "DevOps, from zero", plus
everything that builds, ships and runs it.

- `app.py`: the app. Endpoints `/`, `/healthz`, `/readyz` and `/metrics`.
- `test_app.py`: the pytest tests.
- `Dockerfile`, `compose.yaml`: the image, and the local stack (app and Redis).
- `.github/workflows/`: `ci.yml`, `release.yml` and `terraform.yml`.
- `k8s/`, `chart/`, `overlays/`, `argocd/`: Kubernetes YAML, the Helm chart, Kustomize overlays, Argo CD.
- `infra/`: Terraform.
- `policy/`, `security/`: Kyverno policies, RBAC, and security scripts.
- `ai/`: this file's original, the review checklist, `check.sh` and the agent examples.

## Set up

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt
```

## Build, test and run

- Lint: `ruff check .` and `ruff format --check .`
- Test: `pytest -q`
- Run the app: `python app.py`, then open http://localhost:8000
- Build the image: `docker build -t hello-devops:dev .`
- Run the stack: `docker compose up --build`
- Every check at once: `ai/check.sh`. Run it before you say a change is done.

## Rules

1. Keep changes small: one task per branch and pull request. Propose a plan first for anything that touches more than a few files.
2. Every change to `app.py` comes with a test in `test_app.py`. Never delete or weaken a test to make it pass.
3. The app listens on port 8000 in its container and reads settings only from the environment: `APP_VERSION`, `GREETING`, `REDIS_HOST` and `PORT`.
4. Do not add a dependency without saying so in the pull request. Check that the package exists on PyPI under that exact name, and pin it in `requirements.txt` like the others (`name==X.*`).
5. Never use `:latest`. Pin images to a version tag. Pin third-party GitHub Actions to a full commit SHA, with the version in a comment.
6. Every workflow keeps a `permissions:` block with the least it needs. Never use `pull_request_target` to run code from a pull request.
7. Kubernetes YAML must pass `kubeconform -strict`. Keep the probes and resource requests.
8. Never commit secrets, tokens, kubeconfig files, `.env` files or customer data. Never print a secret in a log.
9. Do not run commands that change shared systems: no `kubectl apply` or `kubectl delete` against a cluster, no `terraform apply`, no `git push --force`, no releases. Propose the command; a person runs it.
10. If you are not sure that a version, flag or field exists, say so and check it (`--help`, `kubectl explain`, the official docs). Do not guess.

## Done means

- `ai/check.sh` prints no FAIL.
- The pull request says what changed, why, and how you tested it (`.github/pull_request_template.md`).
