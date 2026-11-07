"""Day 15 lesson content. Imported by build_p4.py."""

from common import lab, svg_box, svg_line, svg_text, svg

D15_DIAGRAM = svg(
    236,
    "A script takes arguments, environment variables and a log file, and gives back a report on stdout, messages on stderr and an exit code",
    [
        svg_box("bx", 16, 24, 130, 34, "arguments"),
        svg_box("bx", 16, 98, 130, 34, "env vars"),
        svg_box("bx", 16, 172, 130, 34, "log file"),
        svg_box("bxo", 215, 98, 130, 34, "logsum.py"),
        svg_box("bxt", 414, 24, 130, 34, "stdout"),
        svg_box("bxt", 414, 98, 130, 34, "stderr"),
        svg_box("bxt", 414, 172, 130, 34, "exit code"),
        svg_line(146, 41, 211, 107),
        svg_line(146, 115, 211, 115),
        svg_line(146, 189, 211, 123),
        svg_line(345, 107, 410, 41),
        svg_line(345, 115, 410, 115),
        svg_line(345, 123, 410, 189),
        svg_text("ts", 479, 74, "report or JSON"),
        svg_text("ts", 479, 148, "messages for people"),
        svg_text("ts", 479, 222, "0, 1 or 2 for CI"),
        svg_text("ts", 81, 222, "the script reads"),
        svg_text("ts", 280, 148, "main() returns"),
    ],
)

D15 = {
    "id": "d15",
    "title": "Python for ops scripts: files, JSON, arguments and exit codes",
    "minutes": 50,
    "goal": "By the end you can write a Python script that reads logs, takes arguments and environment variables, reports on stdout and stderr, and returns exit codes that CI can act on, and you can run it with uv.",
    "guess": {
        "q": 'Your Python script calls `subprocess.run(["git", "pull"])` and git fails with a merge conflict. What does your script do next?',
        "options": [
            "Python raises an exception and the script stops",
            "It carries on to the next line as if git had worked",
            "Python prints git's error and exits with code 1",
            "It waits until someone fixes the conflict",
        ],
        "answer": 1,
        "why": "`run()` only records git's exit code in the result it returns. Unless you pass `check=True` or look at `returncode`, the script carries on, like bash without `set -e`.",
    },
    "terms": [
        {"term": "uv", "plain": "A fast tool from Astral that installs Python versions, creates virtual environments and runs scripts and projects."},
        {"term": "Virtual environment", "plain": "A folder with its own Python and packages for one project, so projects cannot break each other."},
        {"term": "Inline script metadata", "plain": "A `# /// script` comment block at the top of a Python file that lists the Python version and packages it needs (PEP 723)."},
        {"term": "Exit code", "plain": "The number a program returns when it ends: 0 means success, any other number means a kind of failure."},
        {"term": "argparse", "plain": "Python's standard module that reads command-line arguments and flags and writes the --help text."},
        {"term": "Standard error (stderr)", "plain": "The output stream for messages to people, kept apart from the real output on stdout."},
        {"term": "Aware datetime", "plain": "A Python date and time that carries its time zone, so comparing and converting it gives correct answers."},
        {"term": "subprocess.run", "plain": "The standard function that starts another program, waits for it to finish, and returns its exit code and output."},
    ],
    "sections": [
        {
            "h": "When a Bash script should become Python",
            "body": """Day 7 ended with a rule of thumb: once a script needs real data structures or grows past about a hundred lines, write it in Python. Bash is very good at starting programs and wiring their output together. It gets painful as soon as you need to keep data around and make decisions about it.

Move to Python when a script needs any of these:

- Data you look things up in, such as counts per path. The bash 3.2 on your Mac has no associative arrays at all.
- JSON or an HTTP API. One `jq` call is fine. Five of them glued together with `$(...)` are a program in disguise.
- Different handling for different errors: a missing file, a timeout, a 404.
- Tests. pytest (Day 16) is far easier than testing a shell script.
- The same behaviour on macOS and Linux. `sed -i` and `date -d` differ between the two; Python's `re` and `datetime` do not.

Keep Bash for short glue: a five-line CI step, a `RUN` line in a Dockerfile, or `healthcheck.sh` from Day 7. Keep the Day 7 habits too. A Python script also needs a clear exit code, messages on stderr and a loud failure, and most of today is about doing that well.

Python is already installed on GitHub's Ubuntu runners and on Ubuntu and Amazon Linux servers. Its standard library covers files, JSON, CSV, regular expressions, time zones and running other programs, and today's scripts use nothing else. Day 16 adds the two outside packages most ops scripts need: requests and boto3.""",
            "refs": [
                {"title": "Python for DevOps (Gift, Behrman, Deza, Gheorghiu; O'Reilly)", "url": "https://www.oreilly.com/library/view/python-for-devops/9781492057680/", "kind": "read"},
                {"title": "The Python Standard Library", "url": "https://docs.python.org/3/library/index.html", "kind": "docs"},
            ],
        },
        {
            "h": "Python versions, environments and one-file scripts with uv",
            "body": """On Day 2 you set up hello-devops the classic way: Homebrew's Python, `python3 -m venv .venv`, `source .venv/bin/activate`, then `pip install -r requirements-dev.txt`. That still works, and hello-devops keeps it, because its Dockerfile and its CI (Day 25) use pip.

For new tools this course uses uv, one program from Astral, the company that also makes ruff. It does the jobs of those three tools, and a few more:

- `uv python install 3.14` downloads a Python version, so you stop depending on what Homebrew has.
- `uv init` starts a project with a `pyproject.toml`, the standard file for a project's name, Python version and dependencies.
- `uv add requests` adds a dependency and writes the exact version of every package to `uv.lock`. Commit that file, so CI and teammates get the versions you tested.
- `uv run <command>` first makes `.venv` match the lock file, then runs the command inside it. You never activate anything.
- `uvx ruff check` runs a tool in a throwaway environment.

A **virtual environment** is still underneath: uv creates the same kind of `.venv` folder that `python3 -m venv` makes. You just stop managing it by hand.

A single script does not even need a project. PEP 723 defines inline script metadata: a comment block at the top of the file. It names the Python version and the packages the script needs. The command `uv init --script check.py --python 3.14` creates the block, and `uv add --script check.py requests` adds a package to it. Then `uv run check.py` builds a cached environment with those packages and runs the script. The first run printed `Installed 5 packages in 4ms`, and the second printed nothing extra.

The lab's `scripts/logsum.py` has such a block with an empty package list. Inside a project, a script with a block ignores the project and uses only its own list. With the shebang `#!/usr/bin/env -S uv run --script` and `chmod +x`, you can also start it as `./logsum.py`. Read a script from the internet before you `uv run` it, because uv installs whatever its block asks for.

Python 3.15 came out in October 2026. The course stays on 3.14, the version in its Docker images and CI, and the lab pins it in `.python-version`.""",
            "refs": [
                {"title": "uv: Running scripts", "url": "https://docs.astral.sh/uv/guides/scripts/", "kind": "docs"},
                {"title": "PEP 723: Inline script metadata", "url": "https://peps.python.org/pep-0723/", "kind": "read"},
                {"title": "UV: a faster, all-in-one package manager to replace pip and venv (Corey Schafer)", "url": "https://www.youtube.com/watch?v=AMdG7IjgSPM", "kind": "watch"},
            ],
        },
        {
            "h": "The skeleton every ops script shares",
            "body": """Open `scripts/logsum.py` in the Files section. Every script in the lab has the same shape, top to bottom:

1. The shebang and the PEP 723 block.
2. A docstring with examples and the exit codes. It is the first thing a tired person reads.
3. Imports, then constants such as the regex for one log line.
4. Small functions that each do one job and return data. `parse_access` never prints.
5. `main(argv=None) -> int`, which reads the arguments, calls the functions, prints, and returns an exit code.
6. `if __name__ == "__main__": sys.exit(main())` as the last line.

That last line runs `main` only when you start the file as a program. When a test imports the file, nothing runs. The test calls `main(["access", "x.log"])` itself and checks the number it gets back, which is what Day 16 does.

`argparse` turns `sys.argv` into named values and writes `--help` for you. The summarizer uses four of its features:

- Positional arguments (`file`) and options (`--top 5`), each with a `type` that converts the text and rejects bad values.
- `choices=["text", "json"]`, so `--format xml` fails at once.
- Subcommands, like git's: `logsum access FILE` and `logsum app FILE` share their common options through a parent parser.
- Defaults from the environment: `default=os.environ.get("LOGSUM_MAX_ERROR_RATE", "1.0")`. A flag beats the variable, and the variable beats the built-in default.

On a bad argument, argparse prints the usage line and exits with 2, the same "you called me wrong" code that `healthcheck.sh` used on Day 7. Read settings with `os.environ.get("NAME", default)`. Plain `os.environ["NAME"]` raises `KeyError` when the variable is missing, which is right only for a setting the script cannot run without.""",
            "refs": [
                {"title": "Argparse tutorial (Python docs)", "url": "https://docs.python.org/3/howto/argparse.html", "kind": "docs"},
                {"title": "argparse reference", "url": "https://docs.python.org/3/library/argparse.html", "kind": "docs"},
            ],
        },
        {
            "h": "Log lines into numbers: pathlib, re and Counter",
            "body": """`pathlib.Path` is how current Python handles files. `Path.home() / "code" / "linux-lab"` joins the parts with `/` on any OS. `path.read_text()`, `path.exists()` and `path.glob("*.log")` replace most uses of `open`, `os.path` and `ls`.

A regular expression (Day 4) with named groups turns one access log line into a dictionary. You name a group with `(?P<name>...)`. Write the pattern as a raw string, `r"..."`, so Python leaves its backslashes alone. Try the pattern on one line in the REPL before you trust it on 238 lines; the worked example does exactly that.

`collections.Counter` is a dictionary made for counting. `paths[path] += 1` needs no setup, and `paths.most_common(5)` returns the top five. With it, one pass over the file collects everything at once: requests per path, per status class and per server error.

How does that compare with Day 5? The pipeline `awk '$9 >= 500 {print $9, $7}' access.log | sort | uniq -c | sort -rn` prints the same three lines as the summarizer, starting with `6 500 /api/checkout`. For one question, awk is shorter and much faster. The Python version pays off once you want several answers from one pass, a time window, JSON output, a limit and tests.

It also counts more honestly. The summarizer strips the query string, so `/api/products` has 75 requests. The awk top list splits the same path into 34 for `/api/products` and 24 for `/api/products?page=3`.

For big files, loop over the open file with `for line in f:` instead of reading it all with `read_text()`. Memory then stays flat, as the Go deeper section measures.""",
            "refs": [
                {"title": "Regular expression HOWTO (Python docs)", "url": "https://docs.python.org/3/howto/regex.html", "kind": "docs"},
                {"title": "pathlib: object-oriented filesystem paths", "url": "https://docs.python.org/3/library/pathlib.html", "kind": "docs"},
                {"title": "collections.Counter", "url": "https://docs.python.org/3/library/collections.html#collections.Counter", "kind": "docs"},
            ],
        },
        {
            "h": "Dates, JSON and CSV without surprises",
            "body": """Time zones are where ops scripts go quietly wrong. A Python `datetime` is either naive, with no time zone, or **aware**, with one. Comparing a naive one with an aware one raises `TypeError: can't compare offset-naive and offset-aware datetimes`, which is at least loud. The quiet bug is a naive local time compared with UTC log times, which is off by an hour or two and never complains.

Three habits prevent it:

- Parse the zone the log gives you. `%z` in `strptime(text, "%d/%b/%Y:%H:%M:%S %z")` reads the `+0000`. `datetime.fromisoformat("2026-10-30T09:00:01Z")` understands the `Z` since Python 3.11.
- Ask for the current time as `datetime.now(UTC)`. `datetime.utcnow()` returns a naive value and has been deprecated since Python 3.12.
- Convert only for display. `when.astimezone(ZoneInfo("Europe/Berlin"))` turned 09:00:08 UTC into 10:00:08+01:00. The summarizer's `--tz` option does that.

JSON is the format for other programs. `json.dumps(report, indent=2)` writes it, and `json.loads(text)` reads it. For JSON Lines, such as `events.jsonl` from Day 5, call `json.loads` once per line. When a script prints JSON, print nothing else to stdout, so `| jq` keeps working.

CSV is for people with spreadsheets. Use the `csv` module instead of `",".join(...)`, because it quotes values that contain commas. Open the file with `newline=""`, as the `csv` docs ask, or an extra `\\r` ends up in each line on Windows.""",
            "refs": [
                {"title": "datetime: aware and naive objects", "url": "https://docs.python.org/3/library/datetime.html", "kind": "docs"},
                {"title": "zoneinfo: IANA time zone support", "url": "https://docs.python.org/3/library/zoneinfo.html", "kind": "docs"},
                {"title": "json: JSON encoder and decoder", "url": "https://docs.python.org/3/library/json.html", "kind": "docs"},
            ],
        },
        {
            "h": "Exit codes, stderr and errors that say what to do",
            "body": """CI, cron, systemd and Kubernetes exec probes decide success or failure from your script's exit code alone. A Python script ends with a code in one of three ways:

- `sys.exit(main())` turns the number `main` returns into the exit code.
- An uncaught exception prints a traceback and exits with 1.
- argparse exits with 2 on bad arguments.

So the lab uses one contract in every script: 0 means all good, 1 means the check found a problem, and 2 means the script could not do its job. A caller can then tell "the error rate is too high" apart from "the log file is missing".

Output goes to two places. The report goes to stdout. Everything for people, such as warnings, progress and the reason for a failure, goes to stderr. The `logging` module sends messages there after `logging.basicConfig(stream=sys.stderr, ...)`, and its levels let a `-v` flag turn on DEBUG messages. Pass values as arguments, `log.warning("line %d skipped", number)`, so the text is only built when the message is shown.

Catch the errors you expect, by name, and turn each into one clear line. In the summarizer, `except FileNotFoundError` becomes `logsum: ERROR no such file: nope.log` and exit code 2. Let every other exception crash with its traceback, since a traceback is the quickest way to debug something you did not expect. And never log a token or a password, not even at DEBUG.""",
            "refs": [
                {"title": "Logging HOWTO (Python docs)", "url": "https://docs.python.org/3/howto/logging.html", "kind": "docs"},
                {"title": "Logging basics: files, levels and formatting (Corey Schafer)", "url": "https://www.youtube.com/watch?v=-ARI4Cz-awo", "kind": "watch"},
                {"title": "sys.exit", "url": "https://docs.python.org/3/library/sys.html#sys.exit", "kind": "docs"},
            ],
        },
        {
            "h": "Running other programs safely with subprocess",
            "body": """Sooner or later a script calls `git`, `kubectl` or `terraform`. `subprocess.run` starts the program and waits for it. Give it four things every time:

- A list of arguments, `["git", "rev-parse", "--short", "HEAD"]`, so no shell ever reads them.
- `check=True`, so a non-zero exit raises `CalledProcessError` instead of passing silently.
- `capture_output=True, text=True`, to get stdout and stderr back as strings.
- `timeout=30`, so a hung command raises `TimeoutExpired` instead of hanging your script.

In `/tmp`, `subprocess.run(["git", "log", "-1"], check=True, capture_output=True, text=True)` raised `CalledProcessError(128, ['git', 'log', '-1'])`, and `err.stderr` held `fatal: not a git repository`. That message is exactly what to log before you exit with 2.

`shell=True` with outside input is how scripts get hijacked. With `name = "x; echo pwned"`, the call `subprocess.run(f"ls {name}", shell=True)` printed `pwned`, because the shell ran the second command. The list form passed the whole string to `ls` as one argument, and `ls` answered `cannot access 'x; echo pwned'`.

Environment variables flow down to the child, as on Day 7. To add one, copy the current environment: `env={**os.environ, "KUBECONFIG": path}`. Passing `env={"KUBECONFIG": path}` alone gives the child no `PATH` and no `HOME` at all.""",
            "refs": [
                {"title": "subprocess: security considerations", "url": "https://docs.python.org/3/library/subprocess.html", "kind": "docs"},
                {"title": "The subprocess module: wrapping programs with Python (Real Python)", "url": "https://realpython.com/python-subprocess/", "kind": "read"},
            ],
        },
    ],
    "analogy": "A script reports back like a parcel delivery. The tracking status (delivered, failed, unknown address) is the exit code: it is what the depot's systems act on. The note on your door is stderr, written for a person. The parcel itself is stdout, the thing you actually wanted. Unlike a parcel, a script can hand over half its output and still fail, so a caller checks the exit code before trusting what arrived.",
    "diagram": D15_DIAGRAM,
    "diagram_caption": "Inputs come from arguments, environment variables and files; results leave on three separate channels.",
    "worked": {
        "title": "A log summarizer CI can trust",
        "steps": [
            {
                "say": "Get the lab and let uv build its environment. `uv sync` reads `.python-version` and `uv.lock`, downloads Python 3.14 if you do not have it, and fills `.venv`. The sample logs are in `~/code/linux-lab` from Day 3. (Output trimmed.)",
                "code": "$ brew install uv\n$ git -C ~/code/devops-from-zero pull\n$ cp -R ~/code/devops-from-zero/labs/python-ops ~/code/python-ops\n$ cd ~/code/python-ops\n$ uv sync\nUsing CPython 3.14.10\nCreating virtual environment at: .venv\nResolved 29 packages in 1ms\nInstalled 28 packages in 68ms",
                "lang": "console",
            },
            {
                "say": "Before writing any loop, try the pattern on one line. `uv run python` starts the REPL inside the project. `groupdict()` shows what each named group caught. The status comes back as text, so the script converts it with `int()` before comparing.",
                "code": "$ uv run python\n>>> import re\n>>> from pathlib import Path\n>>> line = (Path.home() / \"code/linux-lab/access.log\").read_text().splitlines()[0]\n>>> pat = re.compile(r'(?P<ip>\\S+) \\S+ \\S+ \\[(?P<time>[^\\]]+)\\] \"(?P<method>[A-Z]+) (?P<path>\\S+) [^\"]*\" (?P<status>\\d{3})')\n>>> pat.match(line).groupdict()\n{'ip': '203.0.113.7', 'time': '30/Oct/2026:09:00:08 +0000', 'method': 'GET', 'path': '/api/products?page=3', 'status': '429'}",
                "lang": "console",
            },
            {
                "say": "Run the summarizer. Of 238 requests, 11 were server errors (4.6%), and the default limit is 1%, so it exits with 1. The report went to stdout and the one-line reason to stderr.",
                "code": "$ uv run scripts/logsum.py access ~/code/linux-lab/access.log\naccess.log: 238 requests, 0 skipped\nfrom 2026-10-30 09:00:08 UTC to 2026-10-30 09:48:44 UTC\nstatus: 2xx 181, 3xx 16, 4xx 30, 5xx 11\nerror rate (5xx): 4.6% (limit 1.0%)\n\ntop 5 paths:\n     75  /api/products\n     19  /api/checkout\n     18  /healthz\n     18  /login\n     16  /\n\nserver errors:\n      6  500 /api/checkout\n      3  502 /api/payments/charge\n      2  504 /api/checkout\nlogsum: ERROR error rate 4.6% is above the limit of 1.0%\n$ echo $?\n1",
                "lang": "console",
            },
            {
                "say": "Raise the limit with the flag or the environment variable, and the same log passes. The `--tz` option changes only how times are shown. The log's 09:00 UTC is 10:00 in Berlin, where summer time had ended five days earlier.",
                "code": "$ uv run scripts/logsum.py access ~/code/linux-lab/access.log --max-error-rate 5 --tz Europe/Berlin | head -n 2\naccess.log: 238 requests, 0 skipped\nfrom 2026-10-30 10:00:08 CET to 2026-10-30 10:48:44 CET\n$ LOGSUM_MAX_ERROR_RATE=5 uv run scripts/logsum.py access ~/code/linux-lab/access.log > /dev/null\n$ echo $?\n0",
                "lang": "console",
            },
            {
                "say": "`--format json` is for other programs. Because log messages go to stderr, stdout holds only JSON, and jq can read it without any cleanup.",
                "code": "$ uv run scripts/logsum.py access ~/code/linux-lab/access.log --format json --max-error-rate 5 | jq -c '.error_rate, .status_classes, .top_paths[0]'\n4.62\n{\"2xx\":181,\"3xx\":16,\"4xx\":30,\"5xx\":11}\n[\"/api/products\",75]",
                "lang": "console",
            },
            {
                "say": "Check the numbers against Day 5. The awk pipeline finds the same server errors. Its top paths differ, because awk keeps query strings and splits `/api/products` in two.",
                "code": "$ cd ~/code/linux-lab\n$ awk '$9 >= 500 {print $9, $7}' access.log | sort | uniq -c | sort -rn\n      6 500 /api/checkout\n      3 502 /api/payments/charge\n      2 504 /api/checkout\n$ awk '{print $7}' access.log | sort | uniq -c | sort -rn | head -n 2\n     34 /api/products\n     24 /api/products?page=3",
                "lang": "console",
            },
            {
                "say": "In CI the script is one step, and the exit code is the whole interface. A run above the limit turns the job red; you write no extra code for that.",
                "code": "- name: Error rate gate\n  run: uv run scripts/logsum.py access logs/access.log --max-error-rate 2",
                "lang": "yaml",
            },
        ],
    },
    "code": [
        {
            "lang": "python",
            "title": "scripts/logsum.py (in labs/python-ops)",
            "src": lab("scripts/logsum.py"),
            "run": "uv run scripts/logsum.py access ~/code/linux-lab/access.log",
        },
        {
            "lang": "text",
            "title": "scripts/urls.txt (input for today's hands-on)",
            "src": lab("scripts/urls.txt"),
            "run": "uv run scripts/healthcheck.py scripts/urls.txt",
        },
    ],
    "commands": [
        {"cmd": "brew install uv", "what": "Install uv on a Mac (the uv docs also have a standalone installer)."},
        {"cmd": "uv python install 3.14", "what": "Download and install a Python version that uv manages."},
        {"cmd": "uv python list", "what": "Show the Python versions uv can find or download."},
        {"cmd": "uv sync", "what": "Make the project's .venv match uv.lock exactly, installing Python if needed."},
        {"cmd": "uv run scripts/logsum.py access ~/code/linux-lab/access.log", "what": "Run a script with the right Python and packages, without activating anything."},
        {"cmd": "uv run python", "what": "Start a Python REPL inside the project's environment."},
        {"cmd": "uv init --script check.py --python 3.14", "what": "Create a one-file script with an inline metadata block."},
        {"cmd": "uv add --script check.py requests", "what": "Add a package to a script's inline metadata block."},
        {"cmd": "uv run --python 3.13 check.py", "what": "Run the same script on a different Python version."},
        {"cmd": "uvx ruff check check.py", "what": "Run a tool (here ruff) in a throwaway environment, without installing it."},
        {"cmd": "chmod +x scripts/logsum.py && ./scripts/logsum.py --help", "what": "Make a script with a uv shebang executable, then run it directly."},
        {"cmd": "echo $?", "what": "Print the exit code of the last command."},
        {"cmd": "uv run scripts/logsum.py access ~/code/linux-lab/access.log 2> /dev/null", "what": "Keep the report, drop the log messages on stderr."},
        {"cmd": "nc -l 9998", "what": "Listen on a port and never answer: a test target for timeouts (stop it with Ctrl+C)."},
    ],
    "mistake": "Wrapping the whole script in `try: ... except Exception: pass` turns a crash into a silent success. The script exits 0, CI goes green, and nothing was checked. Catch the exceptions you expect by name, say on stderr what went wrong, return a non-zero code, and let everything else crash with its traceback.",
    "real_world": "An engineer on call at 3 a.m. and a deploy pipeline often need the same check. A script with `--help`, a JSON mode and fixed exit codes serves both: the person reads the text, and the pipeline reads the code. Teams keep such scripts in one repo with a lock file and run ruff and pytest on them in CI. They also agree on one exit-code contract, so alerts and pipelines can act on a result without parsing any text.",
    "task": {
        "title": "A URL health checker in Python",
        "steps": [
            "Make a folder `~/code/ops-scripts`, then run `uv init --script healthcheck.py --python 3.14` in it.",
            "Create `urls.txt` with one URL per line: the `/healthz` and `/readyz` URLs of hello-devops on port 8000, plus `http://localhost:9998/`. Your script skips blank lines and lines that start with `#`.",
            "Use argparse for the file name and a `--timeout` option. Its default comes from a `HEALTHCHECK_TIMEOUT` environment variable, or 5 seconds.",
            "For each URL, call `urllib.request.urlopen(url, timeout=...)` from the standard library and print one line on stdout: OK or FAIL, the URL, and a short reason.",
            "Catch the failures by name and give each its own reason: an HTTP error status, no connection, and a timeout.",
            "Exit with 0 when every URL is fine, 1 when any failed, and 2 for a missing file. Send the summary line to stderr with logging.",
            "Start hello-devops (`python app.py` in its venv from Day 2) and run your checker. Then stop the app and run it again. Check `echo $?` each time.",
            "Run `nc -l 9998` in another terminal, so that URL accepts the connection and never answers. Run the checker with `--timeout 2` and time it.",
            "Run `uvx ruff check healthcheck.py`, fix what it reports, and compare your script with `scripts/healthcheck.py` in the lab.",
        ],
        "hints": [
            "`urlopen` raises `urllib.error.HTTPError` for 4xx and 5xx answers. It is a subclass of `URLError`, so put its `except` first.",
            "A refused connection arrives as `URLError`; look at `err.reason`. A timeout can arrive as `TimeoutError` or inside a `URLError`.",
            "Only allow `http` and `https` URLs: `urlopen` would also open `file:///etc/passwd`.",
        ],
        "done_when": "You are done when your checker prints one line per URL, exits 0 with hello-devops running and 1 with it stopped, and gives up on the `nc` URL after your timeout.",
    },
    "explain_back": {
        "prompt": "Explain in 3 to 4 sentences how a script should report its result to CI and to a person. Mention stdout, stderr and exit codes, and say why a broad `except` is dangerous.",
        "answer": "CI only reads the exit code, so the script returns 0 when all is well, 1 when the check found a problem, and 2 when it could not run. The report or JSON goes to stdout, where another program can read it cleanly. Messages for people, such as warnings and the reason for a failure, go to stderr through logging. A broad `except Exception: pass` hides failures and lets the script exit 0, so CI goes green even though nothing worked.",
    },
    "recap": [
        "Move a script from Bash to Python when it needs data structures, JSON, error handling or tests.",
        "uv installs Python, keeps .venv in sync with uv.lock, and runs commands with `uv run`.",
        "A `# /// script` block lets one file carry its own Python version and packages.",
        "Shape every script as small functions plus `main(argv) -> int` and `sys.exit(main())`.",
        "Keep datetimes aware: parse the zone from the log and use `datetime.now(UTC)`.",
        "Call programs with a list of arguments, `check=True` and a timeout, never `shell=True` with outside input.",
    ],
    "check": [
        {
            "q": "A cron job runs a Python script that hits a `KeyError` nobody catches. What does cron see?",
            "options": [
                "Exit code 0, because Python itself ran",
                "Exit code 2, the code for usage errors",
                "Exit code 1, with a traceback on stderr",
                "No exit code until the job is killed",
            ],
            "answer": 2,
            "why": "An uncaught exception prints a traceback to stderr and ends Python with exit code 1.",
        },
        {
            "q": "A script compares `datetime.now()` with a time parsed from a log line using `%z`. What happens?",
            "options": [
                "Python raises a TypeError about naive and aware datetimes",
                "Python converts both to UTC and compares them correctly",
                "The comparison always returns False",
                "Python assumes the log time is local time",
            ],
            "answer": 0,
            "why": "`datetime.now()` is naive and the parsed value is aware, and Python refuses to compare the two; use `datetime.now(UTC)`.",
        },
        {
            "q": "A script must run `kubectl get pods -n NAME`, where NAME comes from a command-line argument. Which call is safe?",
            "options": [
                "`subprocess.run(f\"kubectl get pods -n {name}\", shell=True)`",
                "`os.system(\"kubectl get pods -n \" + name)`",
                "`subprocess.run(\"kubectl get pods -n \" + name, shell=True, check=True)`",
                "`subprocess.run([\"kubectl\", \"get\", \"pods\", \"-n\", name], check=True, timeout=30)`",
            ],
            "answer": 3,
            "why": "Only the list form keeps NAME as one argument that no shell interprets, and `check` and `timeout` make failures loud.",
        },
    ],
    "interview": [
        {
            "q": "When do you write an ops script in Python instead of Bash?",
            "a": "When it needs data structures, JSON or HTTP, different handling for different errors, or tests. Bash is good glue for a few commands and short CI steps, but its quoting and error handling get fragile as scripts grow. Python's standard library covers files, JSON, regular expressions, time zones and subprocesses, and behaves the same on macOS and Linux. I keep the Bash habits either way: clear exit codes, messages on stderr and failing loudly.",
        },
        {
            "q": "How do you run an external command safely from Python?",
            "a": "I use `subprocess.run` with a list of arguments, so no shell parses them and there is no injection risk. I pass `check=True` so a non-zero exit raises `CalledProcessError`, `capture_output=True, text=True` to read its output, and a `timeout` so a hung command cannot hang my script. I avoid `shell=True`, and never use it with outside input. On failure I log the command's stderr and exit with a clear code.",
        },
        {
            "q": "Why do scripts have a main() function and `if __name__ == \"__main__\"`?",
            "a": "The guard runs `main` only when the file is executed, not when it is imported. That lets tests import the module and call `main([...])` with their own arguments, then assert on the exit code it returns. Having `main` return an int and calling `sys.exit(main())` keeps the exit-code logic in one place. It also keeps parsing and printing apart from the functions that do the work, which makes them easy to test.",
        },
    ],
    "deeper": {
        "minutes": 12,
        "body": """The summarizer reads a whole file into memory with `read_text()`. For a 238-line practice log that is fine. On a server, access logs can grow to gigabytes, so it is worth knowing what that choice costs.

To find out, we repeated `access.log` 4,200 times: 999,600 lines, 158 MB. Then we parsed it in two ways with the same `parse_access` function:

- `parse_access(read_lines(path))`, which reads everything first, peaked at 384 MB of memory.
- `with path.open() as f: parse_access(f)`, which hands over one line at a time, peaked at 15 MB.

`parse_access` already accepts any iterable of lines, so streaming needed no change inside it. That is a good reason to write parsing functions this way. A file, a list in a test, `sys.stdin` and a decompressed stream all work.

Rotated logs are usually compressed, such as `access.log.2.gz`. The call `gzip.open(path, "rt", encoding="utf-8")` opens one as text, and you can loop over it like any file. Our 158 MB test log compressed to 11 MB, though it repeats itself far more than a real log does. To support pipes as well, accept `-` as the file name and read `sys.stdin`. Then `zcat access.log.*.gz | logsum access -` works the way Unix tools do.

Speed is the other cost. Both runs took 11 to 12 seconds for a million lines. The awk filter `awk '$9 >= 500'` went through the same file in under half a second. A quick profile on 100,000 lines showed where the time goes: the regex took 0.05 seconds, while `datetime.strptime` took 0.79 seconds, about three quarters of the total. Two cheap fixes are open to you:

1. Access logs are written in time order, so you only need to parse the first and the last timestamp, not every one.
2. On a busy server many lines share the same second, so caching parsed values with `functools.lru_cache` avoids parsing the same text twice.

That is the general pattern for Python ops scripts. Write the clear version first, measure on realistic data, and fix the one hot spot the profile shows. The command `uv run python -m cProfile -s cumtime scripts/logsum.py access big.log` prints which functions used the time.""",
    },
    "sources": [
        {"title": "uv: Running scripts", "url": "https://docs.astral.sh/uv/guides/scripts/"},
        {"title": "PEP 723: Inline script metadata", "url": "https://peps.python.org/pep-0723/"},
        {"title": "subprocess: Subprocess management", "url": "https://docs.python.org/3/library/subprocess.html"},
        {"title": "Logging HOWTO", "url": "https://docs.python.org/3/howto/logging.html"},
    ],
}
