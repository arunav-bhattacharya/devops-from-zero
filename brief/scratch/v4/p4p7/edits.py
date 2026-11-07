#!/usr/bin/env python3
"""First-principles review edits for Days 15-16 (content/p4.json) and Days 28-30 (content/p7.json).
Each edit is an exact old -> new replacement inside one prose field. The script refuses to run
an edit whose old text does not occur exactly once, so it is safe to re-run on the originals.
It always starts from brief/scratch/v4/orig/pN.json, so re-running gives the same result.
Usage: python3 brief/scratch/v4/p4p7/edits.py"""
import json
import pathlib
import sys

ROOT = pathlib.Path("/home/user/devops-from-zero")

# (part file, lesson id, path inside the lesson, old, new)
EDITS = [
    # ---------------- Day 15 ----------------
    ("p4", "d15", ("sections", 1, "body"),
     r'''It does the jobs of those three tools, and a few more:''',
     r'''It does the jobs of Homebrew's Python, venv and pip, and a few more:'''),
    ("p4", "d15", ("sections", 1, "body"),
     r'''- `uv run <command>` first makes `.venv` match the lock file, then runs the command inside it. You never activate anything.''',
     r'''- `uv run <command>` first makes `.venv` match the lock file, then starts the command with `.venv/bin` at the front of its PATH (Day 7). That is most of what `activate` does, so you never activate anything.'''),
    ("p4", "d15", ("sections", 1, "body"),
     r'''A **virtual environment** is still underneath: uv creates''',
     r'''A **virtual environment** (Day 2) is still underneath: uv creates'''),
    ("p4", "d15", ("sections", 1, "body"),
     r'''PEP 723 defines inline script metadata:''',
     r'''PEP 723 (a Python Enhancement Proposal, one of the documents that set Python's standards) defines inline script metadata:'''),
    ("p4", "d15", ("sections", 1, "body"),
     r'''you can also start it as `./logsum.py`. Read a script''',
     r'''you can also start it as `./logsum.py`. The `-S` makes `env` split `uv run --script` into three words; without it, `env` looks for one program with that whole name. Read a script'''),
    ("p4", "d15", ("sections", 2, "body"),
     r'''That last line runs `main` only when you start the file as a program. When a test imports the file, nothing runs. The test calls `main(["access", "x.log"])` itself and checks the number it gets back, which is what Day 16 does.''',
     r'''That last line runs `main` only when you start the file as a program. Python sets `__name__` to `"__main__"` in the file you ran, and to the module's name, `"logsum"`, in a file that is imported. So when a test imports the file, nothing runs. With `argv=None`, argparse reads the real command line from `sys.argv`. A test passes its own list instead, `main(["access", "x.log"])`, and checks the number it gets back, which is what Day 16 does.'''),
    ("p4", "d15", ("sections", 2, "body"),
     r'''A flag beats the variable, and the variable beats the built-in default.''',
     r'''Because argparse uses a default only when the flag is missing, a flag beats the variable, and the variable beats the built-in `1.0`.'''),
    ("p4", "d15", ("sections", 3, "body"),
     r'''so Python leaves its backslashes alone.''',
     r'''so Python leaves its backslashes alone. In a normal string, `"\b"` becomes a backspace character instead of the regex word boundary.'''),
    ("p4", "d15", ("sections", 3, "body"),
     r'''`paths[path] += 1` needs no setup, and `paths.most_common(5)` returns the top five.''',
     r'''A missing key reads as 0, so `paths[path] += 1` works the first time a path appears, where a plain dict would raise `KeyError`. And `paths.most_common(5)` returns the top five.'''),
    ("p4", "d15", ("sections", 3, "body"),
     r'''It also counts more honestly. The summarizer strips the query string, so `/api/products` has 75 requests. The awk top list splits the same path into 34 for `/api/products` and 24 for `/api/products?page=3`.''',
     r'''It also counts more honestly, because it strips the query string before counting a path. The worked example shows how far apart the two top lists end up.'''),
    ("p4", "d15", ("sections", 3, "body"),
     r'''Memory then stays flat, as the Go deeper section measures.''',
     r'''The file object hands you one line at a time, so memory stays flat, as the Go deeper section measures.'''),
    ("p4", "d15", ("sections", 4, "body"),
     r'''The quiet bug is a naive local time compared with UTC log times, which is off by an hour or two and never complains.''',
     r'''The quiet bug is two naive values from different zones. Say you drop the `+0000` while parsing a UTC log time, then compare it with `datetime.now()`, which is your Mac's local time. Every answer is off by your offset from UTC, and nothing complains.'''),
    ("p4", "d15", ("sections", 5, "body"),
     r'''CI, cron, systemd and Kubernetes exec probes decide success or failure from your script's exit code alone.''',
     r'''CI, systemd (Day 6), cron (the Unix scheduler for timed jobs) and Kubernetes exec probes (Day 43) decide success or failure from the exit code alone.'''),
    ("p4", "d15", ("sections", 5, "body"),
     r'''Output goes to two places. The report goes to stdout.''',
     r'''Output goes to two places. The report goes to stdout, the only stream a pipe (Day 5) passes on.'''),
    ("p4", "d15", ("sections", 5, "body"),
     r'''`logging.basicConfig(stream=sys.stderr, ...)`, and its levels let a `-v` flag turn on DEBUG messages.''',
     r'''`logging.basicConfig(stream=sys.stderr, ...)`. Each message has a level, from DEBUG up to ERROR, and messages below the level you set are dropped. The summarizer sets INFO, and `-v` lowers it to DEBUG.'''),
    ("p4", "d15", ("sections", 6, "body"),
     r'''`["git", "rev-parse", "--short", "HEAD"]`, so no shell ever reads them.''',
     r'''`["git", "rev-parse", "--short", "HEAD"]`, which Python hands straight to the program, so no shell ever reads them.'''),
    ("p4", "d15", ("sections", 6, "body"),
     r'''`shell=True` with outside input is how scripts get hijacked. With `name = "x; echo pwned"`, the call `subprocess.run(f"ls {name}", shell=True)` printed `pwned`, because the shell ran the second command.''',
     r'''`shell=True` with outside input is how scripts get hijacked. With it, Python passes one string to `/bin/sh`, and the shell reads a `;` inside it as the start of a second command. With `name = "x; echo pwned"`, the call `subprocess.run(f"ls {name}", shell=True)` printed `pwned`.'''),

    ("p4", "d15", ("sections", 1, "body"),
     r''' The first run printed `Installed 5 packages in 4ms`, and the second printed nothing extra.''',
     r''''''),
    ("p4", "d15", ("sections", 1, "body"),
     r'''Python 3.15 came out in October 2026. The course stays on 3.14, the version in its Docker images and CI, and the lab pins it in `.python-version`.''',
     r'''The lab pins Python 3.14, the version in the course's Docker images and CI, in `.python-version`.'''),
    ("p4", "d15", ("sections", 3, "body"),
     r''' before you trust it on 238 lines; the worked example does exactly that.''',
     r''' before you trust it on 238 lines.'''),

    # ---------------- Day 16 ----------------
    ("p4", "d16", ("sections", 0, "body"),
     r'''The value `timeout=(3.05, 10)` waits 3.05 seconds to connect and 10 seconds for each part of the answer. The requests docs suggest a connect value slightly above a multiple of 3, the default TCP retransmission window.''',
     r'''The value `timeout=(3.05, 10)` waits up to 3.05 seconds to connect, then up to 10 seconds of silence while the answer arrives. It does not limit the whole download. The requests docs suggest a connect value just above a multiple of 3. They call 3 seconds the default TCP retransmission window: the wait before an unanswered packet is sent again.'''),
    ("p4", "d16", ("sections", 0, "body"),
     r'''It keeps the connection open and sends the same headers every time.''',
     r'''It keeps the connection open, so later calls skip the TCP and TLS handshakes (Days 10 and 11), and it sends the same headers every time.'''),
    ("p4", "d16", ("sections", 1, "body"),
     r'''`gh-runs` asks GitHub for a repo's recent Actions runs with `GET https://api.github.com/repos/OWNER/REPO/actions/runs`.''',
     r'''The lab's first tool, `gh-runs`, lists a repo's recent GitHub Actions runs and exits 1 when one of them failed. It asks with `GET https://api.github.com/repos/OWNER/REPO/actions/runs`.'''),
    ("p4", "d16", ("sections", 1, "body"),
     r'''the newest API version. Without the header,''',
     r'''the newest API version. Pinning it keeps a later version from changing the JSON under your script. Without the header,'''),
    ("p4", "d16", ("sections", 1, "body"),
     r'''- `Authorization: Bearer <token>`, with the token''',
     r'''- `Authorization: Bearer <token>` (whoever bears, or holds, the token gets in), with the token'''),
    ("p4", "d16", ("sections", 1, "body"),
     r'''Requests does none of this by default. The lab mounts urllib3's `Retry` on the session with''',
     r'''Requests does none of this by default. Under the hood it sends every call through urllib3, a lower-level HTTP library with a `Retry` class. The lab attaches one to the session with `session.mount("https://", ...)`, using'''),
    ("p4", "d16", ("sections", 1, "body"),
     r'''GitHub returns at most 100 items per page and puts the next page's address in the `Link` header.''',
     r'''One request returns one page: 30 runs unless you ask for more with `per_page`, and never more than 100. GitHub puts the next page's address in the `Link` header.'''),
    ("p4", "d16", ("sections", 2, "body"),
     r'''Boto3 is AWS's SDK for Python. Every script starts''',
     r'''Boto3 is AWS's SDK (software development kit) for Python. Each method call becomes an HTTPS request to an AWS API, signed with your credentials so AWS knows who is asking. Every script starts'''),
    ("p4", "d16", ("sections", 2, "body"),
     r'''That needs boto3's `crt` extra, which the lab's''',
     r'''That needs boto3's `crt` extra, an optional add-on installed as `boto3[crt]`, which the lab's'''),
    ("p4", "d16", ("sections", 3, "body"),
     r'''A waiter polls until a resource reaches a state.''',
     r'''When you call `run_instances`, AWS answers while the new instance is still `pending`, so code that uses it at once fails. A waiter polls until a resource reaches a state.'''),
    ("p4", "d16", ("sections", 3, "body"),
     r'''Each client lists its waiters in `waiter_names`; S3 has four, including `bucket_exists`. The lab uses''',
     r'''The lab uses'''),
    ("p4", "d16", ("sections", 3, "body"),
     r'''`aws-report` puts the pieces together.''',
     r'''The lab's second tool, `aws-report`, puts the pieces together.'''),
    ("p4", "d16", ("sections", 5, "body"),
     r'''`responses` patches requests so that registered URLs get canned answers.''',
     r'''`responses` replaces the step where requests hands data to the network, so registered URLs get canned answers instead.'''),
    ("p4", "d16", ("sections", 5, "body"),
     r'''Inside `with mock_aws():`, every boto3 call goes to an in-memory fake AWS that starts empty for each test.''',
     r'''Inside `with mock_aws():`, moto catches each boto3 request just before it would be sent and answers it from an in-memory fake AWS. That fake starts empty for each test.'''),
    ("p4", "d16", ("sections", 5, "body"),
     r'''It also has quirks: in the lab, a bucket named `logs` failed in moto with a 404, and a rename fixed it. Run a new check''',
     r'''Run a new check'''),
    ("p4", "d16", ("sections", 6, "body"),
     r'''make a command named `gh-runs` that calls `main` in that module.''',
     r'''make a command named `gh-runs` that calls `main` in that module. When uv installs the project, with `uv sync` or `uv tool install`, it writes a tiny `gh-runs` launcher into that environment's `bin` folder. It imports the module and runs `sys.exit(main())`, so your exit codes reach the shell.'''),
    ("p4", "d16", ("sections", 6, "body"),
     r'''`uv init` creates this kind of project by default, with the code under `src/` and uv's own build backend.''',
     r'''`uv init` creates this kind of project by default. It puts the code under `src/` and packages it with uv's own build backend.'''),
    ("p4", "d16", ("sections", 6, "body"),
     r'''Day 25 builds a full pipeline with caching and a matrix; this one is a short preview you can push today.''',
     r'''Day 25 builds a full pipeline with caching and a matrix.'''),
    ("p4", "d16", ("sections", 2, "body"),
     r'''Use clients rather than the older resource interface (`boto3.resource`). The boto3 docs say AWS does not intend to add new features to resources.''',
     r'''Use clients, not the older `boto3.resource` interface, which the boto3 docs say will get no new features.'''),
    ("p4", "d16", ("sections", 6, "body"),
     r'''- `uv tool install --editable .` puts `gh-runs` and `aws-report` on your PATH, each in its own environment.''',
     r'''- `uv tool install --editable .` installs the project into one environment of its own and links both commands into `~/.local/bin` (`uv tool update-shell` puts that folder on your PATH).'''),
    ("p4", "d16", ("sections", 6, "body"),
     r'''ruff lints and formats in one fast tool: `uv run ruff check` finds likely bugs, and `uv run ruff format` fixes the layout.''',
     r'''ruff lints and formats in one fast tool. Linting means reading code for likely bugs without running it: `uv run ruff check` does that, and `uv run ruff format` fixes the layout.'''),

    # ---------------- Day 28 ----------------
    ("p7", "d28", ("sections", 0, "body"),
     r'''Then the classpath grows to 40 jars, a teammate has another JDK,''',
     r'''Then the classpath (the list of jars the compiler and the JVM can see) grows to 40 jars. A teammate has another JDK,'''),
    ("p7", "d28", ("sections", 1, "body"),
     r'''Before a task runs, Gradle fingerprints its inputs and outputs and compares them with the last run.''',
     r'''Before a task runs, Gradle fingerprints its inputs and outputs: it hashes their contents, the same idea as Git's SHA hashes on Day 8. It compares those hashes with the ones it saved in the project's `.gradle` folder after the last run.'''),
    ("p7", "d28", ("sections", 2, "body"),
     r'''This is the Kotlin DSL: the build files are real Kotlin,''',
     r'''This is the Kotlin DSL, short for domain-specific language: Kotlin shaped for describing builds. The build files are real Kotlin,'''),
    ("p7", "d28", ("sections", 3, "body"),
     r'''Every Gradle run goes through three phases, in this order:''',
     r'''Gradle wants the whole plan before it does any work. Only then can it order the tasks, skip the ones that are up to date and run independent ones side by side. So every Gradle run goes through three phases, in this order:'''),
    ("p7", "d28", ("sections", 3, "body"),
     r'''a running task may not reach back into `project`, the live build model. The worked example''',
     r'''a running task may not reach back into `project`, the live build model. On a cache hit the build scripts never ran and that model does not exist, so Gradle forbids it on every run, hit or miss. The worked example'''),
    ("p7", "d28", ("sections", 4, "body"),
     r'''On the first run, `./gradlew` downloads that version into `~/.gradle/wrapper/dists`. After that, you,''',
     r'''The `gradlew` script starts the small jar with your JDK. The jar reads the properties file and, on the first run, downloads that version into `~/.gradle/wrapper/dists`. Then it hands your command to that Gradle. So you,'''),
    ("p7", "d28", ("worked", "steps", 0, "say"),
     r'''into it from hello-jvm, and put''',
     r'''into it from `~/code/devops-from-zero/labs/hello-jvm`, and put'''),

    # ---------------- Day 29 ----------------
    ("p7", "d29", ("sections", 0, "body"),
     r'''a server that stores published jars with their metadata.''',
     r'''a server that stores published jars with their metadata. That is a small file next to each jar, a Maven `.pom` or Gradle's own `.module`, which lists the library's own dependencies.'''),
    ("p7", "d29", ("sections", 1, "body"),
     r'''and the same two for tests. The configurations you will use:''',
     r'''and the same two for tests. Gradle names them `compileClasspath`, `runtimeClasspath`, `testCompileClasspath` and `testRuntimeClasspath`, and fills each one from the configurations below. The reports in this lesson ask for them by those names. The configurations you will use:'''),
    ("p7", "d29", ("sections", 1, "body"),
     r'''but also on the compile classpath of every project that uses yours. It needs the `java-library` plugin.''',
     r'''but also on the compile classpath of every project that uses yours. The Kotlin plugin offers it; a plain Java project needs the `java-library` plugin.'''),
    ("p7", "d29", ("sections", 1, "body"),
     r'''- `compileOnly`: needed to compile, but provided by someone else at runtime.''',
     r'''- `compileOnly`: needed to compile, but provided by someone else at runtime, such as the Servlet API inside an application server.'''),
    ("p7", "d29", ("sections", 2, "body"),
     r'''Ask for `commons-text` and you also get `commons-lang3`, because `commons-text` needs it.''',
     r'''Ask for `commons-text` and you also get `commons-lang3`, because the metadata file of `commons-text` lists it. Gradle then reads the metadata of `commons-lang3`, and so on down the tree.'''),
    ("p7", "d29", ("sections", 2, "body"),
     r'''Your own declaration gets no extra weight.''',
     r'''Your own declaration gets no extra weight. The bet: the library asking for the newer version may need something only it has, while code written for the older one usually runs on the newer too.'''),
    ("p7", "d29", ("sections", 3, "body"),
     r'''It is a TOML file at `gradle/libs.versions.toml`, and Gradle reads it automatically.''',
     r'''It is a file at `gradle/libs.versions.toml`, written in TOML, the simple format of `pyproject.toml` on Day 15. Gradle reads it automatically.'''),
    ("p7", "d29", ("sections", 3, "body"),
     r'''Build scripts then say `libs.junit.bom` instead of''',
     r'''From it Gradle generates an object named `libs`, so build scripts say `libs.junit.bom` instead of'''),
    ("p7", "d29", ("sections", 4, "body"),
     r'''with lines marked `(c)` for the BOM's constraints.''',
     r'''with lines marked `(c)` for the BOM's constraints. A constraint is a version rule that applies only when something else brings that library in. A BOM is a list of constraints, so it adds no jars of its own.'''),
    ("p7", "d29", ("sections", 5, "body"),
     r'''like any library, except that Gradle builds it first.''',
     r'''like any library. The difference is that Gradle puts the tasks that build `greeting` into the task graph ahead of the tasks of `app`.'''),
    ("p7", "d29", ("sections", 6, "body"),
     r'''Gradle now advises against that, because it ties every project to the root.''',
     r'''Gradle now advises against that, because it ties every project to the root. With such a block, `app/build.gradle.kts` no longer shows how `app` is built, and every edit to the root script affects every project.'''),
    ("p7", "d29", ("sections", 6, "body"),
     r'''a separate little Gradle build inside the repository:''',
     r'''a separate little Gradle build inside the repository. It has to be separate, because its plugins must be compiled before Gradle can run the build scripts that apply them:'''),
    ("p7", "d29", ("worked", "steps", 0, "say"),
     r'''In a scratch copy of hello-jvm, add two real libraries.''',
     r'''Work in a scratch copy of the two-project hello-jvm; the finished one is in `~/code/devops-from-zero/labs/hello-jvm`. Add two real libraries.'''),
    ("p7", "d29", ("interview", 0, "a"),
     r'''It needs the `java-library` plugin.''',
     r'''The Kotlin plugin provides `api`; a plain Java project needs the `java-library` plugin.'''),

    # ---------------- Day 30 ----------------
    ("p7", "d30", ("sections", 0, "body"),
     r'''The ABI (the public signatures other code compiles against)''',
     r'''The ABI (application binary interface: the public signatures other code compiles against)'''),
    ("p7", "d30", ("sections", 1, "body"),
     r'''The usual setup is that CI writes to it and laptops only read.''',
     r'''The Gradle docs recommend that CI fills it from clean builds and laptops only read, so half-finished local changes never reach the shared cache.'''),
    ("p7", "d30", ("sections", 2, "body"),
     r'''with classes already loaded and code already JIT-compiled.''',
     r'''with classes already loaded and hot code already turned into machine code by the JIT (just-in-time) compiler.'''),
    ("p7", "d30", ("sections", 2, "body"),
     r'''2. If there is none, the foojay plugin in `settings.gradle.kts` downloads one.''',
     r'''2. If there is none, the foojay resolver plugin in `settings.gradle.kts` finds one through foojay, the JDK download service of the Friends of OpenJDK community, and downloads it.'''),
    ("p7", "d30", ("sections", 3, "body"),
     r'''Dependency locking writes the exact resolved version''',
     r'''Versions can also move without anyone editing a build file: a range such as `1.+` resolves to whatever is newest on the day. Dependency locking stops that. It writes the exact resolved version'''),
    ("p7", "d30", ("sections", 4, "body"),
     r'''so a tampered wrapper fails.''',
     r'''so a tampered wrapper fails. That jar runs on every build, and nobody can review a binary file in a pull request.'''),
    ("p7", "d30", ("sections", 4, "body"),
     r'''- It is written only from the default branch. Other branches only read it.''',
     r'''- It is written only from the default branch. Other branches only read it, and by the Day 25 rule every branch can restore what main saved.'''),
    ("p7", "d30", ("sections", 6, "body"),
     r'''The JVM reads the container's memory limit and sizes its heap from it.''',
     r'''The JVM reads the container's memory limit from its cgroup (Day 17) and sizes its heap from it.'''),
    ("p7", "d30", ("sections", 6, "body"),
     r'''Jib puts your dependencies and your classes in separate layers.''',
     r'''Jib puts your dependencies and your classes in separate layers, so a code change rebuilds and pushes only the small classes layer (Day 18).'''),
]


def get(obj, path):
    for k in path:
        obj = obj[k]
    return obj


def put(obj, path, value):
    for k in path[:-1]:
        obj = obj[k]
    obj[path[-1]] = value


def main():
    parts = {}
    for part in sorted({e[0] for e in EDITS}):
        src = ROOT / "brief/scratch/v4/orig" / f"{part}.json"
        text = src.read_text()
        parts[part] = (json.loads(text), text.endswith("\n"))
    applied = 0
    for part, lid, path, old, new in EDITS:
        data = parts[part][0]
        lesson = next(L for L in data["lessons"] if L["id"] == lid)
        field = get(lesson, path)
        n = field.count(old)
        if n != 1:
            sys.exit(f"{lid} {path}: old text found {n} times: {old[:60]!r}")
        put(lesson, path, field.replace(old, new))
        applied += 1
    for part, (data, nl) in parts.items():
        out = json.dumps(data, indent=1, ensure_ascii=False) + ("\n" if nl else "")
        (ROOT / "content" / f"{part}.json").write_text(out)
    print(f"{applied} edits applied of {len(EDITS)}")


if __name__ == "__main__":
    main()
