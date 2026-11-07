# labs/python-ops: Python scripts for automation (Part 4, Days 15 and 16)

Small ops tools written the way you want them at 3 a.m.: clear exit codes, messages on
stderr, timeouts on every network call, and tests that run offline.

| Path | What it is | Day |
|---|---|---|
| `scripts/logsum.py` | Summarizes the Part 1 sample logs (`labs/linux`): top paths, status codes, error rate. Exits 1 above a limit | 15 |
| `scripts/healthcheck.py` | Checks a list of URLs with a timeout, exits 1 if any fail (standard library only) | 15 (hands-on answer) |
| `scripts/urls.txt` | Example input for `healthcheck.py` | 15 |
| `scripts/seed_moto.py` | Creates fake buckets and instances in a local moto server, for trying `aws-report` | 16 |
| `src/python_ops/gh_runs.py` | `gh-runs`: recent GitHub Actions runs from the REST API, exits 1 if any failed | 16 |
| `src/python_ops/aws_report.py` | `aws-report`: S3 buckets without versioning, EC2 instances without an owner tag | 16 |
| `tests/` | pytest tests: `tmp_path`, `monkeypatch`, `capsys`, `responses` for HTTP, moto for AWS | 15, 16 |
| `pyproject.toml`, `uv.lock` | The project, its commands, and the pytest and ruff settings | 16 |
| `.github/workflows/ci.yml` | Lint and test in GitHub Actions, once this folder is its own repo | 16 |

## Get it onto your Mac

```bash
brew install uv                       # or see https://docs.astral.sh/uv/getting-started/installation/
git -C ~/code/devops-from-zero pull   # the course repo you cloned on Day 3
cp -R ~/code/devops-from-zero/labs/python-ops ~/code/python-ops
cd ~/code/python-ops
uv sync                               # installs Python 3.14 if needed, then every locked package
```

## Run things

```bash
uv run pytest                          # all tests, offline (about 10 seconds)
uv run ruff check && uv run ruff format --check

uv run scripts/logsum.py access ~/code/linux-lab/access.log
uv run scripts/logsum.py app ~/code/linux-lab/app.log --format json
uv run scripts/healthcheck.py scripts/urls.txt

export GITHUB_TOKEN="$(gh auth token)"
uv run gh-runs YOUR-USER/hello-devops --limit 10

aws login --profile learn              # the sign-in from Day 13
uv run aws-report --profile learn      # read-only; or try it on moto, below
```

## aws-report without an AWS account

```bash
# Terminal 1: a pretend AWS on port 5050 (port 5000 is taken by AirPlay on a Mac)
uvx --from "moto[server]" moto_server -p 5050

# Terminal 2
export AWS_ENDPOINT_URL=http://localhost:5050 AWS_ACCESS_KEY_ID=testing \
       AWS_SECRET_ACCESS_KEY=testing AWS_DEFAULT_REGION=eu-central-1
uv run scripts/seed_moto.py
uv run aws-report
```

Stop the server with Ctrl+C. Everything in it is gone when it stops.

## Install the commands for everyday use

```bash
uv tool install --editable .   # gh-runs and aws-report on your PATH, edits apply at once
uv tool list
uv tool uninstall python-ops
```

Exit codes in every tool: `0` all good, `1` the check found a problem, `2` the tool could not
do its job (bad arguments, missing file, no credentials, network down).
