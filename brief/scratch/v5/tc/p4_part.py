"""Fifth pass (book voice) for the Part 4 fields."""
import json, pathlib
ROOT = pathlib.Path(__file__).resolve().parents[4]
path = ROOT / "content/p4.json"
P = json.loads(path.read_text())

P["intro"] = r"""This part builds a helper that works from a written checklist and always reports back: done, or failed and why. On Day 7 you wrote Bash scripts and met a rule: once a script grows, switch to Python. Day 15 writes Python scripts from the standard library alone and runs them with uv. Day 16 calls GitHub and Amazon's cloud, tests both without a network, and installs the result as commands. Every script lives in labs/python-ops, and its 30 tests run offline in about ten seconds."""

P["recap"] = [
    "Python takes over from Bash when a script needs data structures, JSON, APIs, different error handling or tests.",
    "uv installs Python, keeps .venv in step with uv.lock, runs commands with uv run, and runs one-file scripts with a PEP 723 block.",
    "Every script has the same shape: small functions that return data, main(argv) -> int, and sys.exit(main()).",
    "One exit code contract everywhere: 0 all good, 1 the check found a problem, 2 the script could not do its job.",
    "Reports go to stdout, messages for people go to stderr through logging, and secrets go nowhere.",
    "Keep datetimes aware, call programs with a list of arguments and check=True, and never use shell=True with outside input.",
    "Every HTTP call gets a timeout and raise_for_status; retry 429 and 5xx with backoff, and follow the Link header to the next page.",
    "boto3 starts from a session (profile and region), uses clients, paginators and waiters, and separates ClientError from BotoCoreError.",
    "pytest with tmp_path, monkeypatch and capsys tests scripts; responses stands in for HTTP and moto for AWS.",
    "[project.scripts], uv tool install, ruff and a short CI workflow turn a folder of scripts into a tool the team can install.",
]

cards = [
    ("Which signs say a Bash script should become Python?", "It needs data structures, JSON or APIs, different handling for different errors, or tests."),
    ("What does `uv run` do before it runs your command?", "It makes .venv match uv.lock (creating or fixing it if needed), then runs the command inside it."),
    ("What is a PEP 723 block?", "A `# /// script` comment block at the top of a file that lists requires-python and dependencies, so `uv run` can build its environment."),
    ("Why does `main()` return a number?", "`sys.exit(main())` turns it into the exit code, and tests can call main([...]) and check the number."),
    ("What exit code does an uncaught Python exception give?", "1, with a traceback on stderr."),
    ("What exit code does argparse use for bad arguments?", "2, after printing the usage line."),
    ("Where do log messages go, and why?", "To stderr, so stdout holds only the report or JSON that other programs read."),
    ("How do you get the current time safely in Python?", "`datetime.now(UTC)`, which knows its time zone. `utcnow()` does not, and has been deprecated since 3.12."),
    ("Name the four arguments that make subprocess.run safe.", "A list of arguments, check=True, capture_output=True with text=True, and a timeout."),
    ("What does requests do if you pass no timeout?", "It waits forever for a server that never answers."),
    ("Which HTTP answers deserve a retry?", "429 and 5xx such as 502, 503 and 504, for idempotent methods only; never 401 or 404."),
    ("How do you find the next page in the GitHub REST API?", "Follow the `next` URL in the Link header; requests gives it to you as response.links[\"next\"][\"url\"]."),
    ("What is the difference between ClientError and BotoCoreError?", "ClientError: AWS answered with an error code. BotoCoreError: no usable answer, such as missing credentials or an expired sign-in."),
    ("What does a boto3 waiter do?", "It asks a describe call again and again until a resource reaches a state, such as instance_running, and raises WaiterError after the last try."),
    ("What do tmp_path, monkeypatch and capsys give a test?", "A fresh folder, temporary changes to environment variables and attributes, and the captured stdout and stderr."),
    ("What two rules keep moto tests safe?", "Set fake credentials first, and start mock_aws() before any boto3 client is created."),
    ("What does `uv tool install --editable .` do?", "It puts the project's [project.scripts] commands on your PATH, and code edits apply without reinstalling."),
]
assert len(cards) == len(P["flashcards"])
for f, (a, b) in zip(P["flashcards"], cards):
    f["front"], f["back"] = a, b

whys = [
    "The guides on scripts, projects and tools cover every uv command this part uses.",
    "A calm walk through uv projects, lock files and scripts, side by side with pip and venv.",
    "The reference for pathlib, argparse, json, csv, datetime, logging and subprocess.",
    "A whole book of Python for server, CI, cloud and Kubernetes work; some tools are older, the habits are the same.",
    "Gentle chapters on files, regular expressions and CSV, for when any of the basics feel shaky.",
    "Sessions, timeouts and retries, straight from the library's own docs.",
    "How pages, page sizes and JMESPath filtering work for every AWS list call.",
    "The decorator, the context manager, pytest fixtures and the import-order trap, with examples.",
    "monkeypatch in depth; the sidebar leads to tmp_path, capsys and fixtures.",
    "A practical tour of pytest, fixtures and mocking, for when test files still feel new.",
    "How rule selection works, and where to look up any rule code ruff reports.",
]
assert len(whys) == len(P["resources"])
for r, w in zip(P["resources"], whys):
    r["why"] = w

quiz = [
    ("A teammate's 300-line Bash script reads JSON with five jq calls and keeps a list of servers with their settings. What is the strongest reason to rewrite it in Python?",
     "Data structures, JSON and tests are where Bash gets fragile and Python is strong; speed is not the reason."),
    ("You run `uv run scripts/report.py` inside a project, and the script starts with a `# /// script` block. Which packages does it get?",
     "A script with inline metadata ignores the project and runs in its own environment, built from its block."),
    ("A summarizer prints a JSON report and also prints progress lines with `print()`. Now `| jq` fails. What is the right fix?",
     "stdout must hold only the data; messages for people belong on stderr, where jq never sees them."),
    ("Which exit code contract lets CI tell 'the check failed' apart from 'the script could not run'?",
     "Separate codes let a caller react differently to a real finding and to a broken run; also, exit codes stop at 255."),
    ("GitHub answers your script with 403 and `x-ratelimit-remaining: 0`. What should the script do?",
     "Retrying before the reset time cannot succeed; say when the limit resets and exit non-zero."),
    ("A test sets fake AWS keys with monkeypatch and starts `mock_aws()`, but the module under test created `s3 = boto3.client(\"s3\")` when it was first imported. What is the risk?",
     "moto must be active before a client is created; a client made earlier may slip past the mock."),
    ("Which ruff rule in the lab flags `requests.get(url)` with no timeout, and what does it miss?",
     "S113 checks calls made straight on the requests module, so `session.get` without a timeout still needs your own habit."),
    ("Why does the lab's CI run `uv sync --locked` instead of `uv sync`?",
     "--locked turns a stale lock file into a red build, instead of quietly picking new versions in CI."),
    ("A Bash script with `set -euo pipefail` runs `grep -q FATAL app.log`, and the log has no FATAL lines. What happens?",
     "grep exits 1 when nothing matches, and `-e` stops the script; write `|| true` when no match is fine. Python's check=True behaves the same way."),
    ("Your retry policy covers 503 answers. Which request is safe to retry automatically?",
     "GET is idempotent, so repeating it changes nothing; the others can charge, deploy or add twice (Day 11)."),
]
assert len(quiz) == len(P["quiz"])
for q, (a, b) in zip(P["quiz"], quiz):
    q["q"], q["why"] = a, b

path.write_text(json.dumps(P, ensure_ascii=False, indent=1) + "\n")
print("p4 part fields written")
