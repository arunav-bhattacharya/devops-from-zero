#!/usr/bin/env python3
"""Build content/p4.json (Part 4, Python scripts for automation) for the third edition.

Run from anywhere: python3 brief/scratch/v3/python/build_p4.py
Code blocks are read from labs/python-ops, so the lesson always matches the lab.
"""

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from common import ROOT  # noqa: E402
from d15 import D15  # noqa: E402
from d16 import D16  # noqa: E402

PART = {
    "part": 4,
    "title": "Python scripts for automation",
    "intro": "Day 7 left you with Bash scripts that fail loudly, and a rule to switch to Python once a script grows. This part is that switch. Day 15 writes scripts from the standard library alone and runs them with uv. Day 16 calls the GitHub API and AWS, tests both without a network, and installs the result as commands. Every script lives in labs/python-ops, and its 30 tests run offline in about ten seconds.",
    "lessons": [D15, D16],
    "recap": [
        "Python takes over from Bash when a script needs data structures, JSON, APIs, error handling or tests.",
        "uv installs Python, keeps .venv in sync with uv.lock, runs commands with uv run, and runs one-file scripts with a PEP 723 block.",
        "Every script has the same shape: small functions that return data, main(argv) -> int, and sys.exit(main()).",
        "One exit-code contract everywhere: 0 all good, 1 the check found a problem, 2 the script could not do its job.",
        "Reports go to stdout, messages for people go to stderr through logging, and secrets go nowhere.",
        "Keep datetimes aware, call programs with a list of arguments and check=True, and never use shell=True with outside input.",
        "HTTP calls get a timeout, raise_for_status, retries with backoff for 429 and 5xx, and pagination through the Link header.",
        "boto3 starts from a session (profile and region), uses clients, paginators and waiters, and separates ClientError from BotoCoreError.",
        "pytest with tmp_path, monkeypatch and capsys tests scripts; responses fakes HTTP and moto fakes AWS.",
        "[project.scripts], uv tool install, ruff and a short CI workflow turn a folder of scripts into a team tool.",
    ],
    "flashcards": [
        {"front": "Which signs say a Bash script should become Python?", "back": "It needs data structures, JSON or APIs, different handling for different errors, or tests."},
        {"front": "What does `uv run` do before it runs your command?", "back": "It makes .venv match uv.lock (creating or fixing it if needed), then runs the command inside it."},
        {"front": "What is a PEP 723 block?", "back": "A `# /// script` comment block at the top of a file that lists requires-python and dependencies, so `uv run` can build its environment."},
        {"front": "Why does `main()` return an int?", "back": "`sys.exit(main())` turns it into the exit code, and tests can call main([...]) and assert on the number."},
        {"front": "What exit code does an uncaught Python exception give?", "back": "1, with a traceback on stderr."},
        {"front": "What exit code does argparse use for bad arguments?", "back": "2, after printing the usage line."},
        {"front": "Where do log messages go, and why?", "back": "To stderr, so stdout holds only the report or JSON that other programs read."},
        {"front": "How do you get the current time safely in Python?", "back": "`datetime.now(UTC)`: an aware datetime. `utcnow()` is naive and deprecated since 3.12."},
        {"front": "Name the four arguments that make subprocess.run safe.", "back": "A list of arguments, check=True, capture_output=True with text=True, and a timeout."},
        {"front": "What does requests do if you pass no timeout?", "back": "It waits forever for a server that never answers."},
        {"front": "Which HTTP answers deserve a retry?", "back": "429 and 5xx such as 502, 503 and 504, for idempotent methods only; never 401 or 404."},
        {"front": "How do you find the next page in the GitHub REST API?", "back": "Follow the `next` URL in the Link header; requests exposes it as response.links[\"next\"][\"url\"]."},
        {"front": "What is the difference between ClientError and BotoCoreError?", "back": "ClientError: AWS answered with an error code. BotoCoreError: no usable answer, such as missing credentials or an expired sign-in."},
        {"front": "What does a boto3 waiter do?", "back": "It polls a describe call until a resource reaches a state, such as instance_running, then raises WaiterError after the last attempt."},
        {"front": "What do tmp_path, monkeypatch and capsys give a test?", "back": "A fresh folder, temporary changes to env vars and attributes, and the captured stdout and stderr."},
        {"front": "What two rules keep moto tests safe?", "back": "Set fake credentials first, and start mock_aws() before any boto3 client is created."},
        {"front": "What does `uv tool install --editable .` do?", "back": "It puts the project's [project.scripts] commands on your PATH, and code edits apply without reinstalling."},
    ],
    "resources": [
        {"title": "uv documentation", "url": "https://docs.astral.sh/uv/", "kind": "docs", "why": "The guides on scripts, projects and tools cover every uv command this part uses."},
        {"title": "UV: a faster, all-in-one package manager to replace pip and venv (Corey Schafer)", "url": "https://www.youtube.com/watch?v=AMdG7IjgSPM", "kind": "watch", "why": "A calm walk through uv projects, lock files and scripts, compared with pip and venv."},
        {"title": "The Python Standard Library", "url": "https://docs.python.org/3/library/index.html", "kind": "docs", "why": "The reference for pathlib, argparse, json, csv, datetime, logging and subprocess."},
        {"title": "Python for DevOps (O'Reilly)", "url": "https://www.oreilly.com/library/view/python-for-devops/9781492057680/", "kind": "read", "why": "A whole book of Python for Linux admin, CI, cloud and Kubernetes work; older tools, same habits."},
        {"title": "Automate the Boring Stuff with Python (free online)", "url": "https://www.automatetheboringstuff.com", "kind": "read", "why": "Gentle chapters on files, regular expressions and CSV if any of the basics feel shaky."},
        {"title": "requests: Advanced usage", "url": "https://requests.readthedocs.io/en/latest/user/advanced/", "kind": "docs", "why": "Sessions, timeouts and retries straight from the library's own docs."},
        {"title": "boto3: Paginators", "url": "https://docs.aws.amazon.com/boto3/latest/guide/paginators.html", "kind": "docs", "why": "How pages, page sizes and JMESPath filtering work for every AWS list call."},
        {"title": "Moto: getting started", "url": "https://docs.getmoto.org/en/latest/docs/getting_started.html", "kind": "docs", "why": "The decorator, context manager, pytest fixtures and the import-order trap, with examples."},
        {"title": "pytest: How-to guides", "url": "https://docs.pytest.org/en/stable/how-to/monkeypatch.html", "kind": "docs", "why": "monkeypatch in depth; the sidebar leads to tmp_path, capsys and fixtures."},
        {"title": "Please learn how to write tests in Python: pytest tutorial (Tech With Tim)", "url": "https://www.youtube.com/watch?v=EgpLj86ZHFQ", "kind": "watch", "why": "A practical tour of pytest, fixtures and mocking for when the test files feel new."},
        {"title": "The Ruff linter", "url": "https://docs.astral.sh/ruff/linter/", "kind": "docs", "why": "How rule selection works, and where to look up any rule code ruff reports."},
    ],
    "quiz": [
        {
            "q": "A teammate's 300-line Bash script parses JSON with five jq calls and keeps a list of hosts with settings. What is the strongest reason to rewrite it in Python?",
            "options": [
                "Python scripts always run faster than Bash scripts do",
                "Its data and JSON are easier to handle and test in Python",
                "Bash scripts cannot run in GitHub Actions workflows",
                "Python needs no installation on a Mac or on Linux",
            ],
            "answer": 1,
            "why": "Data structures, JSON and tests are where Bash gets fragile and Python is strong; speed is not the reason.",
        },
        {
            "q": "You run `uv run scripts/report.py` inside a project, and the script starts with a `# /// script` block. Which packages does it get?",
            "options": [
                "The project's dependencies plus the block's",
                "Only the project's dependencies from uv.lock",
                "Only the packages listed in the script's block",
                "None, until you activate .venv",
            ],
            "answer": 2,
            "why": "A script with inline metadata ignores the project and runs in its own environment built from its block.",
        },
        {
            "q": "A summarizer prints a JSON report and also prints progress lines with `print()`. `| jq` fails. What is the right fix?",
            "options": [
                "Send the progress lines to stderr with logging",
                "Add the `--raw-output` flag to the jq command",
                "Print the whole JSON report on a single line",
                "Remove the progress lines and the exit code",
            ],
            "answer": 0,
            "why": "stdout must hold only the data; messages for people belong on stderr, where jq never sees them.",
        },
        {
            "q": "Which exit-code contract lets CI tell 'the check failed' apart from 'the script could not run'?",
            "options": [
                "0 on success, and 1 for every kind of failure",
                "0 all good, 1 the check found a problem, 2 the script could not do its job",
                "Always exit 0 and print FAILED when something is wrong",
                "Exit with the number of problems found, up to 1000",
            ],
            "answer": 1,
            "why": "Separate codes let a caller react differently to a real finding and to a broken run; codes also stop at 255.",
        },
        {
            "q": "GitHub answers your script with 403 and `x-ratelimit-remaining: 0`. What should the script do?",
            "options": [
                "Retry straight away, up to three more times",
                "Switch the request to the newest API version",
                "Treat it as a bad token and print the token",
                "Stop and report when x-ratelimit-reset says it resets",
            ],
            "answer": 3,
            "why": "Retrying before the reset time cannot succeed; say when it resets and exit non-zero.",
        },
        {
            "q": "A test sets fake AWS keys with monkeypatch and starts `mock_aws()`, but the module under test created `s3 = boto3.client(\"s3\")` at import time. What is the risk?",
            "options": [
                "moto runs slower than usual",
                "pytest refuses to import the module",
                "The fake keys leak into other tests",
                "The client may not be mocked and can call real AWS",
            ],
            "answer": 3,
            "why": "moto must be active before a client is created; an earlier client may bypass the mock.",
        },
        {
            "q": "Which ruff rule in the lab flags `requests.get(url)` with no timeout, and what does it miss?",
            "options": [
                "S113; it does not see calls made on a requests Session",
                "DTZ005; it misses POST requests",
                "PLW1510; it misses calls inside tests",
                "S602; it misses calls with headers",
            ],
            "answer": 0,
            "why": "S113 checks module-level requests calls, so `session.get` without a timeout still needs your own habit.",
        },
        {
            "q": "Why does the lab's CI run `uv sync --locked` instead of `uv sync`?",
            "options": [
                "It installs the packages faster from the cache",
                "It skips the dev group so CI images stay small",
                "It fails when uv.lock no longer matches pyproject.toml",
                "It upgrades every package to the newest version",
            ],
            "answer": 2,
            "why": "--locked turns a stale lock file into a red build instead of quietly resolving new versions in CI.",
        },
        {
            "q": "A Bash script with `set -euo pipefail` runs `grep -q FATAL app.log` and the log has no FATAL lines. What happens?",
            "options": [
                "The script carries on, because grep printed nothing",
                "grep prints an error and the script carries on",
                "The script stops, because grep exits 1 when nothing matches",
                "pipefail turns the result into exit code 0",
            ],
            "answer": 2,
            "why": "grep exits 1 on no match, and `-e` stops the script; write `|| true` when no match is fine. Python's check=True behaves the same way.",
            "from": "Part 1",
        },
        {
            "q": "Your retry policy covers 503 answers. Which request is safe to retry automatically?",
            "options": [
                "POST /payments without an idempotency key",
                "GET /api/orders/1001",
                "POST /deployments",
                "PATCH /accounts/7 that adds 10 to a balance",
            ],
            "answer": 1,
            "why": "GET is idempotent, so repeating it changes nothing; the others can charge, deploy or add twice (Day 11).",
            "from": "Part 3",
        },
    ],
}


def main() -> int:
    out = ROOT / "content" / "p4.json"
    out.write_text(json.dumps(PART, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"wrote {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
