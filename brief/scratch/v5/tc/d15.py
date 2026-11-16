"""Fifth pass (book voice) for d15. Replaces prose fields only; key order follows the original file."""
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[4]
PATH = ROOT / "content/p4.json"
ORIG = json.loads((ROOT / "brief/scratch/v5/orig/p4.json").read_text())
P = json.loads(PATH.read_text())
L = next(x for x in P["lessons"] if x["id"] == "d15")
O = next(x for x in ORIG["lessons"] if x["id"] == "d15")

L["goal"] = r"""By the end you can write a Python script that reads a log file, takes arguments and environment variables, reports on stdout and stderr, and returns exit codes that CI can act on, and you can run it with uv."""

L["opening"] = r"""Picture leaving a helper in charge of your small shop for the morning. You hand over a written checklist: open the stock room, count yesterday's visitors in the door book, then leave a note that says done or failed. At lunch the note says "done". Later you find out the stock room key never turned, and the helper simply moved on to the next line.

Nobody lied. The checklist never said what to do when a step fails, and a helper who follows a list exactly will carry on. Computer scripts behave the same way. The trap is easy to miss, because a script that carried on looks just like a script that worked.

In the last lesson, Hands-on AWS 2: a server of your own with EC2, VPC and CloudWatch, Bash scripts such as `server-up.sh` launched a whole server for you. In this lesson, we'll write a helper in Python. It reads a log, counts what matters, and reports done or failed in a way both people and machines can trust.

Before we start, make a guess, and keep it in mind."""

L["guess"]["q"] = r"""Your Python script runs git, the tool that saves versions of your files, with `subprocess.run(["git", "pull"])`. Git fails with a merge conflict (two changes clash). What does your script do next?"""
L["guess"]["why"] = r"""`run()` only writes git's exit code into the result it hands back. Unless you pass `check=True` or look at `returncode`, the script carries on, like the helper with the stuck key, or like bash without `set -e`."""

plain = {
    "uv": "A free tool from the company Astral that installs Python, sets up a private folder of add-ons for each project, and runs your scripts.",
    "Virtual environment": "A folder with its own Python and add-on packages for one project, so two projects cannot break each other.",
    "Inline script metadata": "A `# /// script` comment block at the top of a Python file that says which Python version and packages the file needs (PEP 723).",
    "Exit code": "The number a program hands back when it ends: 0 means success, and any other number means some kind of failure.",
    "argparse": "The part of Python's built-in toolbox that reads the words and options typed after a script's name, and writes its --help text.",
    "Standard error (stderr)": "The output channel for messages meant for people, kept apart from the real results on standard output (stdout).",
    "Aware datetime": "A Python date and time that knows its time zone, so comparing or converting it gives the right answer.",
    "subprocess.run": "The built-in Python function that starts another program, waits for it to finish, and hands back its exit code and output.",
}
for t in L["terms"]:
    t["plain"] = plain[t["term"]]

S = L["sections"]

S[0]["h"] = "When the checklist outgrows Bash"
S[0]["body"] = r"""A script is a text file of instructions that the computer follows from top to bottom, like the helper's checklist. Bash is the language of the terminal, the text window where you type commands. On Day 7 you wrote Bash scripts and met a rule of thumb: once a script needs real data structures or grows past about a hundred lines, write it in Python. Python is a programming language that reads almost like English.

Bash is very good at starting programs and wiring their output together. It gets painful as soon as you need to keep data around and make decisions about it. Move to Python when a script needs any of these:

- Data you look things up in, such as a count for each page of a website. The bash 3.2 on your Mac has no associative arrays (lookup tables) at all.
- JSON, a common text format for data, or an HTTP API, a web address that programs ask for data. One `jq` call is fine (jq reads JSON). Five of them glued together with `$(...)` are a program in disguise.
- Different handling for different errors: a missing file, a timeout, a 404 ("page not found").
- Tests. pytest (Day 16) is far easier than testing a shell script.
- The same behaviour on macOS and Linux. `sed -i` and `date -d` differ between the two; Python's `re` and `datetime` do not.

Keep Bash for short glue: a five-line CI step, a `RUN` line in a Dockerfile (Part 5), or `healthcheck.sh` from Day 7. CI, continuous integration, is a service that runs your checks on every change. Keep the Day 7 habits too: a clear exit code, messages on stderr and a loud failure. Most of today is about doing those well in Python.

Python is already installed on GitHub's Ubuntu runners (the machines that run CI jobs) and on Ubuntu and Amazon Linux servers. Its standard library, the toolbox that comes with Python, covers files, JSON, CSV, regular expressions, time zones and running other programs. Today's scripts use nothing else. Day 16 adds the two outside packages most ops scripts need: requests and boto3.

So Python it is. But which Python, and where do its add-ons live?"""

S[1]["h"] = "One tool for Python, its packages and one-file scripts: uv"
S[1]["body"] = r"""On Day 2 you set up hello-devops, the course's tiny web app that answers every visit with a greeting and a count of visits so far. You did it the classic way: Homebrew's Python, `python3 -m venv .venv`, `source .venv/bin/activate`, then `pip install -r requirements-dev.txt`. That still works, and hello-devops keeps it, because its Dockerfile and its CI (Day 25) use pip. The `.venv` folder is a virtual environment: a private home for one project's packages (ready-made code that other people wrote), so projects cannot break each other.

For new tools this course uses uv, one program from Astral, the company that also makes ruff (a checker for Python code). It does the jobs of Homebrew's Python, venv and pip, and a few more:

- `uv python install 3.14` downloads a Python version, so you stop depending on what Homebrew has.
- `uv init` starts a project with a `pyproject.toml`, the standard file for a project's name, Python version and dependencies (the packages it needs).
- `uv add requests` adds a dependency and writes the exact version of every package to `uv.lock`. Commit that file (save it in Git), so CI and teammates get the versions you tested.
- `uv run <command>` first makes `.venv` match the lock file, then starts the command with `.venv/bin` at the front of its PATH (Day 7), the list of folders searched for programs. That is most of what `activate` does, so you never activate anything.
- `uvx ruff check` runs a tool in a throwaway environment.

Underneath, uv creates the same kind of `.venv` folder that `python3 -m venv` makes. You just stop managing it by hand.

A single script does not even need a project. PEP 723 (a Python Enhancement Proposal, one of the documents that set Python's standards) defines inline script metadata. It is a comment block at the top of the file, like a shopping list taped to a recipe. It names the Python version and the packages the script needs. The command `uv init --script check.py --python 3.14` creates the block, and `uv add --script check.py requests` adds a package to it. Then `uv run check.py` builds a cached environment with those packages and runs the script.

The lab's `scripts/logsum.py` has such a block with an empty package list. Inside a project, a script with a block ignores the project and uses only its own list. Read a script from the internet before you `uv run` it, because uv installs whatever its block asks for. The lab pins Python 3.14, the version in the course's Docker images and CI, in `.python-version`.

With the tools in place, we can open the helper and see how it is built."""

L["aside"] = {
    "title": "Can I start a script without typing uv run?",
    "body": r"""Yes. Make the first line of the file `#!/usr/bin/env -S uv run --script`. That line is a shebang: it tells the system which program should run the file. Then mark the file as runnable with `chmod +x`, and you can start it as `./logsum.py`. The `-S` makes `env` split `uv run --script` into three words; without it, `env` looks for one program with that whole name.""",
    "after": 1,
}

S[2]["h"] = "The shape every helper script shares"
S[2]["body"] = r"""Open `scripts/logsum.py` in the Files section. It is our running example: a log summarizer that counts how many requests to a web server went well and how many failed. Every script in the lab has the same shape, top to bottom:

1. The shebang and the PEP 723 block.
2. A docstring (a note in quotes) with examples and the exit codes. It is the first thing a tired person reads.
3. Imports, which load parts of the standard library, then constants such as the pattern for one log line.
4. Small functions (named blocks of steps) that each do one job and return data. `parse_access` never prints.
5. `main(argv=None) -> int`, which reads the arguments, calls the functions, prints, and returns an exit code as a whole number.
6. `if __name__ == "__main__": sys.exit(main())` as the last line.

That odd last line runs `main` only when you start the file as a program. Python sets `__name__` to `"__main__"` in the file you ran, and to the module's name, `"logsum"`, in a file that is imported. So when a test imports the file, nothing runs. With `argv=None`, argparse reads the real command line from `sys.argv`. A test passes its own list instead, `main(["access", "x.log"])`, and checks the number it gets back, which is what Day 16 does.

Arguments are the words you type after a script's name. `argparse` turns `sys.argv` into named values and writes `--help` for you. The summarizer uses four of its features:

- Positional arguments (`file`) and options (`--top 5`), each with a `type` that converts the text and rejects bad values.
- `choices=["text", "json"]`, so `--format xml` fails at once.
- Subcommands, like git's: `logsum access FILE` and `logsum app FILE` share their common options through a parent parser.
- Defaults from the environment: `default=os.environ.get("LOGSUM_MAX_ERROR_RATE", "1.0")`. Because argparse uses a default only when the flag is missing, a flag beats the variable, and the variable beats the built-in `1.0`.

An environment variable is a named setting that a program inherits from the terminal that started it. Read one with `os.environ.get("NAME", default)`. Plain `os.environ["NAME"]` raises `KeyError` (Python stops with an error) when the variable is missing, which is right only for a setting the script cannot run without. On a bad argument, argparse prints the usage line and exits with 2, the same "you called me wrong" code that `healthcheck.sh` used on Day 7.

The skeleton is ready. Now the helper has to read the log and count."""

S[3]["h"] = "Turning log lines into numbers"
S[3]["body"] = r"""A web server keeps an access log: a text file with one line for every request, each time a browser or program asks it for a page. A line holds who asked, when, which path (such as `/login`) and a status code. That is a three-digit answer: 2xx fine, 3xx sent elsewhere, 4xx the asker's mistake, 5xx the server's failure.

First, the file. `pathlib.Path` is how current Python handles files. `Path.home() / "code" / "linux-lab"` joins the parts with `/` on any OS. `path.read_text()`, `path.exists()` and `path.glob("*.log")` replace most uses of `open`, `os.path` and `ls`.

Next, one line. A regular expression, or regex (Day 4), is a pattern that describes text. With named groups it turns one access log line into a dictionary, a set of named values such as `path` and `status`. You name a group with `(?P<name>...)`. Write the pattern as a raw string, `r"..."`, so Python leaves its backslashes alone. In a normal string, `"\b"` becomes a backspace character instead of the regex word boundary. Try the pattern on one line in the REPL, Python's type-and-see prompt, before you trust it on 238 lines.

Then, the counting. A plain dictionary fails on the very first line: `paths[path] += 1` raises `KeyError`, because that path is not in it yet. `collections.Counter` is a dictionary made for counting. A missing key reads as 0, so the same line just works, and `paths.most_common(5)` returns the top five. One pass over the file now collects everything: requests per path, per status class and per server error.

How does that compare with Day 5? The pipeline `awk '$9 >= 500 {print $9, $7}' access.log | sort | uniq -c | sort -rn` prints the same three lines as the summarizer, starting with `6 500 /api/checkout`. For one question, awk is shorter and much faster. Python pays off once you want several answers from one pass, a time window, JSON output, a limit and tests. It also counts more honestly, because it strips the query string (such as `?page=3`) before counting a path. The worked example shows how far apart the two top lists end up.

For big files, loop over the open file with `for line in f:` instead of `read_text()`. You get one line at a time, so memory stays flat, as the Go deeper section measures.

Every log line also carries a time, and times hide the next trap."""

S[4]["h"] = "Times, JSON and CSV without quiet mistakes"
S[4]["body"] = r"""Picture two clocks on the shop wall with no labels, one on London time and one on Berlin time. Read one, then the other, and you are an hour off without knowing it. Time zones trip up ops scripts in the same quiet way.

A Python `datetime` is either naive, with no time zone, or aware, with one. Comparing a naive one with an aware one raises `TypeError: can't compare offset-naive and offset-aware datetimes`, which is at least loud. The quiet bug is two naive values from different zones. Say you drop the `+0000` while parsing a log time in UTC, the world's reference clock. Then you compare it with `datetime.now()`, which is your Mac's local time. Every answer is off by your offset from UTC, and nothing complains.

Three habits prevent it:

- Parse the zone the log gives you. `%z` in `strptime(text, "%d/%b/%Y:%H:%M:%S %z")` reads the `+0000`. `datetime.fromisoformat("2026-10-30T09:00:01Z")` understands the `Z` since Python 3.11.
- Ask for the current time as `datetime.now(UTC)`. `datetime.utcnow()` returns a naive value and has been deprecated (marked for removal) since Python 3.12.
- Convert only for display. `when.astimezone(ZoneInfo("Europe/Berlin"))` turned 09:00:08 UTC into 10:00:08+01:00. The summarizer's `--tz` option does that.

JSON is the format for other programs. `json.dumps(report, indent=2)` writes it, and `json.loads(text)` reads it. For JSON Lines, one JSON record per line, such as `events.jsonl` from Day 5, call `json.loads` once per line. When a script prints JSON, print nothing else to stdout, its normal output, so `| jq` keeps working.

CSV, plain text with values split by commas, is for people with spreadsheets. Use the `csv` module instead of `",".join(...)`, because it quotes values that contain commas. Open the file with `newline=""`, as the `csv` docs ask, or an extra `\r` ends up in each line on Windows.

The numbers are right now. What's left is the note: how the helper tells you what it found."""

S[5]["h"] = "Reporting back: exit codes, stderr and errors that say what to do"
S[5]["body"] = r"""A person reads the words on the helper's note. A machine reads only one thing: did it work? A program answers that with its exit code.

CI, systemd (Day 6), cron (the Unix scheduler for timed jobs) and Kubernetes exec probes (Day 43) decide success or failure from the exit code alone. A Python script ends with a code in one of three ways:

- `sys.exit(main())` turns the number `main` returns into the exit code.
- An uncaught exception, Python's way of stopping on an error, prints a traceback (the trail of lines that led there) and exits with 1.
- argparse exits with 2 on bad arguments.

So the lab uses one contract in every script: 0 means all good, 1 means the check found a problem, and 2 means the script could not do its job. A caller can then tell "the error rate is too high" apart from "the log file is missing".

Output goes to two places. The report goes to stdout, the only stream a pipe (Day 5) passes on. Everything for people, such as warnings, progress and the reason for a failure, goes to stderr, which shows on your screen but stays out of the pipe. The `logging` module sends messages there after `logging.basicConfig(stream=sys.stderr, ...)`. Each message has a level, from DEBUG up to ERROR, and messages below the level you set are dropped. The summarizer sets INFO, and `-v` lowers it to DEBUG. Pass values as arguments, `log.warning("line %d skipped", number)`, so the text is only built when the message is shown.

Now the naive helper. Wrapping the whole script in `try: ... except Exception: pass` turns a crash into a silent success. The script exits 0, CI goes green, and nothing was checked. That is the stuck key from the opening, written in Python. Instead, catch the errors you expect, by name, and turn each into one clear line. In the summarizer, `except FileNotFoundError` becomes `logsum: ERROR no such file: nope.log` and exit code 2. Let every other exception crash with its traceback, since a traceback is the quickest way to debug something you did not expect. And never log a token or a password, not even at DEBUG.

**A hidden failure looks exactly like success. Catch errors by name.**

The helper can count and report now. Its last skill is asking other programs for help."""

S[6]["h"] = "Asking other programs for help, safely"
S[6]["body"] = r"""Sooner or later a script calls `git`, `kubectl` (which drives Kubernetes) or `terraform` (which builds servers from a plan). `subprocess.run` starts the program and waits for it. Remember the guess: on its own, it only records the exit code and lets your script carry on. Give it four things every time:

- A list of arguments, `["git", "rev-parse", "--short", "HEAD"]`, which Python hands straight to the program, so no shell ever reads them.
- `check=True`, so a non-zero exit raises `CalledProcessError` instead of passing silently.
- `capture_output=True, text=True`, to get stdout and stderr back as strings (pieces of text).
- `timeout=30`, so a hung command raises `TimeoutExpired` instead of hanging your script.

Here is a loud failure. In `/tmp`, `subprocess.run(["git", "log", "-1"], check=True, capture_output=True, text=True)` raised `CalledProcessError(128, ['git', 'log', '-1'])`, and `err.stderr` held `fatal: not a git repository`. That message is exactly what to log before you exit with 2.

Now the dangerous version. A shell, such as Bash, is the program that reads a command line and splits it into commands. `shell=True` with outside input is how scripts get hijacked. With it, Python passes one string to `/bin/sh`, and the shell reads a `;` inside it as the start of a second command. With `name = "x; echo pwned"`, the call `subprocess.run(f"ls {name}", shell=True)` printed `pwned`, proof that a second command ran. The list form passed the whole string to `ls` as one argument, and `ls` answered `cannot access 'x; echo pwned'`.

**Outside input must never reach a shell. Pass a list.**

Environment variables flow down to the child program, as on Day 7. To add one, copy the current environment: `env={**os.environ, "KUBECONFIG": path}`. Passing `env={"KUBECONFIG": path}` alone gives the child no `PATH` and no `HOME` at all.

Today's helper has a limit: it knows only Python's built-in toolbox, and for one quick question awk is still faster. Day 16 adds outside packages, and tests that prove the helper works."""

L["analogy"] = r"""In shop terms, the helper is the script and the checklist is its code. The report sheet is stdout, the note for the manager is stderr, and the thumbs up or down at the end is the exit code. Unlike a person, a script never stops to ask when a step looks wrong, so the checklist itself must say what counts as failure. And a script can hand over half its report and still fail, so a caller checks the exit code before trusting what arrived."""

L["mistake"] = r"""Using `print()` for warnings and progress puts them on stdout, mixed in with the report. The next program in the pipe, such as jq reading your JSON, then fails on a line like "starting...". Send every message for people through `logging` to stderr, and keep stdout for the report alone."""

L["real_world"] = r"""Picture a person on call at 3 a.m. and a deploy pipeline that both need the same check. A script with `--help`, a JSON mode and fixed exit codes serves both: the person reads the text, and the pipeline reads the number. Teams keep such scripts in one repo with a lock file, and run ruff and pytest on them in CI. They also agree on one exit code contract, so alerts and pipelines can act on a result without reading any text."""

L["diagram_caption"] = "The script reads arguments, environment variables and a file, and reports on three separate channels."

W = L["worked"]["steps"]
W[0]["say"] = r"""Get the lab and let uv build its environment. Homebrew, the Mac's installer for command-line tools, installs uv. `uv sync` reads `.python-version` and `uv.lock`, downloads Python 3.14 if you do not have it, and fills `.venv`. The sample logs are in `~/code/linux-lab` from Day 3. (Output trimmed.)"""
W[1]["say"] = r"""Before writing any loop, try the pattern on one line. `uv run python` starts the REPL inside the project. `groupdict()` shows what each named group caught. The status comes back as text, `'429'`, so the script converts it with `int()` before comparing."""
W[2]["say"] = r"""Run the summarizer. Of 238 requests, 11 were server errors (4.6%), and the default limit is 1%, so it exits with 1. The report went to stdout and the one-line reason to stderr. `echo $?` prints the exit code of the last command."""
W[3]["say"] = r"""Raise the limit with the flag or the environment variable, and the same log passes. The `--tz` option changes only how times are shown. The log's 09:00 UTC is 10:00 in Berlin, where summer time had ended five days earlier."""
W[4]["say"] = r"""`--format json` is for other programs. Because log messages go to stderr, stdout holds only JSON, and jq can pick values out of it without any cleanup."""
W[5]["say"] = r"""Check the numbers against Day 5. The awk pipeline finds the same server errors. Its top paths differ, because awk keeps query strings and splits `/api/products` in two."""
W[6]["say"] = r"""In CI the script is one step, and the exit code is the whole interface. A run above the limit turns the job red (failed), and you write no extra code for that."""

T = L["task"]
T["steps"] = [
    r"""Make a folder `~/code/ops-scripts`, then run `uv init --script healthcheck.py --python 3.14` in it.""",
    r"""Create `urls.txt` with one URL (web address) per line: the `/healthz` and `/readyz` URLs of hello-devops on port 8000, plus `http://localhost:9998/`. Your script skips blank lines and lines that start with `#`.""",
    r"""Use argparse for the file name and a `--timeout` option. Its default comes from a `HEALTHCHECK_TIMEOUT` environment variable, or 5 seconds.""",
    r"""For each URL, call `urllib.request.urlopen(url, timeout=...)` from the standard library and print one line on stdout: OK or FAIL, the URL, and a short reason.""",
    r"""Catch the failures by name and give each its own reason: an HTTP error status, no connection, and a timeout.""",
    r"""Exit with 0 when every URL is fine, 1 when any failed, and 2 for a missing file. Send the summary line to stderr with logging.""",
    r"""Start hello-devops (`python app.py` in its venv from Day 2) and run your checker. Then stop the app and run it again. Check `echo $?` each time.""",
    r"""Run `nc -l 9998` in another terminal. It listens on port 9998, accepts the connection and never answers. Run the checker with `--timeout 2` and time it.""",
    r"""Run `uvx ruff check healthcheck.py`, fix what it reports, and compare your script with `scripts/healthcheck.py` in the lab.""",
]
T["hints"] = [
    r"""`urlopen` raises `urllib.error.HTTPError` for 4xx and 5xx answers. It is a special kind of `URLError`, so put its `except` first.""",
    r"""A refused connection arrives as `URLError`; look at `err.reason`. A timeout can arrive as `TimeoutError` or inside a `URLError`.""",
    r"""Only allow `http` and `https` URLs: `urlopen` would also open `file:///etc/passwd`.""",
]
T["done_when"] = r"""You are done when your checker prints one line per URL, exits 0 with hello-devops running and 1 with it stopped, and gives up on the `nc` URL after your timeout."""

L["explain_back"]["prompt"] = r"""Explain in 3 to 4 sentences how a script should report its result to CI and to a person. Mention stdout, stderr and exit codes, and say why a broad `except` is dangerous."""
L["explain_back"]["answer"] = r"""CI reads only the exit code, so the script returns 0 when all is well, 1 when the check found a problem, and 2 when it could not run. The report or JSON goes to stdout, where another program can read it cleanly. Messages for people, such as warnings and the reason for a failure, go to stderr through logging. A broad `except Exception: pass` hides failures and lets the script exit 0, so CI goes green even though nothing was checked."""

L["recap"] = [
    "Move a script from Bash to Python when it needs lookup tables, JSON, different error handling or tests.",
    "uv installs Python, keeps .venv in step with uv.lock, and runs commands with `uv run`.",
    "A `# /// script` block lets one file carry its own Python version and packages.",
    "Shape every script as small functions plus `main(argv) -> int` and `sys.exit(main())`, with 0, 1 and 2 as exit codes.",
    "Keep datetimes aware, and call programs with a list, `check=True` and a timeout, never `shell=True` with outside input.",
    "Today's limit: the standard library alone, and for one quick question awk is far faster; Day 16 adds packages and tests.",
]

C = L["check"]
C[0]["q"] = r"""A cron job runs a Python script that hits a `KeyError` nobody catches. What does cron see?"""
C[0]["why"] = r"""An uncaught exception prints a traceback to stderr and ends Python with exit code 1."""
C[1]["q"] = r"""A script compares `datetime.now()` with a time read from a log line using `%z`. What happens?"""
C[1]["why"] = r"""`datetime.now()` is naive and the parsed value is aware, and Python refuses to compare the two; use `datetime.now(UTC)`."""
C[2]["q"] = r"""A script must run `kubectl get pods -n NAME`, where NAME comes from a command-line argument. Which call is safe?"""
C[2]["why"] = r"""Only the list form keeps NAME as one argument that no shell reads, and `check` and `timeout` make failures loud."""

I = L["interview"]
I[0]["a"] = r"""When it needs data structures, JSON or HTTP, different handling for different errors, or tests. Bash is good glue for a few commands and short CI steps, but its quoting and error handling get fragile as scripts grow. Python's standard library covers files, JSON, regular expressions, time zones and subprocesses, and behaves the same on macOS and Linux. I keep the Bash habits either way: clear exit codes, messages on stderr and failing loudly."""
I[1]["a"] = r"""I use `subprocess.run` with a list of arguments, so no shell reads them and there is no injection risk. I pass `check=True` so a non-zero exit raises `CalledProcessError`, `capture_output=True, text=True` to read its output, and a `timeout` so a hung command cannot hang my script. I avoid `shell=True`, and never use it with outside input. On failure I log the command's stderr and exit with a clear code."""
I[2]["a"] = r"""The guard runs `main` only when the file is executed, not when it is imported. That lets tests import the module, call `main([...])` with their own arguments, and check the exit code it returns. Having `main` return an int and calling `sys.exit(main())` keeps the exit code logic in one place. It also keeps parsing and printing apart from the functions that do the work, which makes those easy to test."""

L["deeper"]["body"] = r"""The summarizer reads a whole file into memory with `read_text()`. For a 238-line practice log that is fine. On a server, access logs can grow to gigabytes, so it is worth knowing what that choice costs.

To find out, we repeated `access.log` 4,200 times: 999,600 lines, 158 MB. Then we parsed it in two ways with the same `parse_access` function:

- `parse_access(read_lines(path))`, which reads everything first, peaked at 384 MB of memory.
- `with path.open() as f: parse_access(f)`, which hands over one line at a time, peaked at 15 MB.

`parse_access` already accepts anything that hands out lines one by one, so streaming needed no change inside it. That is a good reason to write parsing functions this way. A file, a list in a test, `sys.stdin` (the text piped into a script) and a decompressed stream all work.

Old logs are usually rotated (renamed and replaced by a fresh file) and compressed, such as `access.log.2.gz`. The call `gzip.open(path, "rt", encoding="utf-8")` opens one as text, and you can loop over it like any file. Our 158 MB test log compressed to 11 MB, though it repeats itself far more than a real log does. To support pipes as well, accept `-` as the file name and read `sys.stdin`. Then `zcat access.log.*.gz | logsum access -` works the way Unix tools do.

Speed is the other cost. Both runs took 11 to 12 seconds for a million lines. The awk filter `awk '$9 >= 500'` went through the same file in under half a second. A profile measures where a program spends its time. A quick one on 100,000 lines showed the culprit: the regex took 0.05 seconds, while `datetime.strptime` took 0.79 seconds, about three quarters of the total. Two cheap fixes are open to you:

1. Access logs are written in time order, so you only need to parse the first and the last timestamp, not every one.
2. On a busy server many lines share the same second, so caching parsed values with `functools.lru_cache` avoids parsing the same text twice.

That is the general pattern for Python ops scripts. Write the clear version first, measure on realistic data, and fix the one hot spot the profile shows. The command `uv run python -m cProfile -s cumtime scripts/logsum.py access big.log` prints which functions used the time."""

L["closing"] = r"""We started with a helper whose note said "done" while the stock room key was still stuck. Our summarizer can't do that. It counts 238 requests, finds 11 server errors, says why on stderr, and exits with 1, so CI turns red. Look through any script you own, or the lab's `scripts/` folder, for two things: an `except Exception: pass`, and a `subprocess.run(` without `check=True`. Each one is a helper that carries on after a failed step.

Next, we'll let the helper talk to the GitHub API and to AWS. That raises a harder question: how do you test a script that needs the internet, without the internet?"""

# Key order: the original order, with opening after goal and aside, closing at the end.
new = {}
for k in O:
    if k in L:
        new[k] = L[k]
    if k == "goal":
        new["opening"] = L["opening"]
for k in L:
    if k not in new and k not in ("aside", "closing"):
        new[k] = L[k]
new["aside"] = L["aside"]
new["closing"] = L["closing"]
P["lessons"][P["lessons"].index(L)] = new
PATH.write_text(json.dumps(P, ensure_ascii=False, indent=1) + "\n")
print("d15 written")
