"""Day 16 lesson content. Imported by build_p4.py."""

from common import lab, svg, svg_box, svg_line, svg_text

D16_DIAGRAM = svg(
    216,
    "Your script calls requests or boto3; in a real run they talk to GitHub or AWS, under pytest they talk to responses or moto",
    [
        svg_box("bx", 16, 88, 120, 40, "your script"),
        svg_box("bxp", 172, 88, 160, 40, "requests / boto3"),
        svg_box("bxt", 392, 24, 152, 40, "GitHub / AWS"),
        svg_box("bxg", 392, 148, 152, 40, "responses / moto"),
        svg_line(136, 108, 168, 108),
        svg_line(332, 100, 388, 50),
        svg_line(332, 116, 388, 166, dashed=True),
        svg_text("ts", 76, 146, "gh-runs, aws-report"),
        svg_text("ts", 252, 146, "timeouts, retries"),
        svg_text("ts", 468, 82, "real run: network, cost"),
        svg_text("ts", 468, 206, "pytest: offline, fast"),
    ],
)

D16 = {
    "id": "d16",
    "title": "Python and APIs: HTTP, AWS with boto3, and testing your scripts",
    "minutes": 50,
    "goal": "By the end you can call the GitHub API and AWS from Python with timeouts, retries and pagination, test both without a network, and install the result as a command.",
    "guess": {
        "q": "Your script calls `requests.get(url)` without a timeout. The server accepts the connection and then never answers. How long does your script wait?",
        "options": [
            "30 seconds, the requests default",
            "It retries three times, then raises",
            "Forever, unless something kills it",
            "Until TCP gives up after two minutes",
        ],
        "answer": 2,
        "why": "requests has no default timeout, so the call can hang for as long as the connection stays open. Always pass `timeout=`, for example `timeout=(3.05, 10)`.",
    },
    "terms": [
        {"term": "REST API", "plain": "A web service you call with HTTP methods on URLs, usually sending and receiving JSON."},
        {"term": "Timeout", "plain": "The longest your code waits for a connection or an answer before it gives up with an error."},
        {"term": "Exponential backoff", "plain": "Waiting longer after each failed try, for example 2 seconds, then 4, then 8, so a busy server can recover."},
        {"term": "Pagination", "plain": "An API returns a long list in pages, and you ask for the next page until there is none."},
        {"term": "boto3 client", "plain": "A Python object for one AWS service, with one method per API call, such as `s3.list_buckets()`."},
        {"term": "Paginator", "plain": "A boto3 helper that fetches every page of a list call for you."},
        {"term": "Waiter", "plain": "A boto3 helper that asks AWS again and again until a resource reaches a state, such as running."},
        {"term": "Mock", "plain": "A stand-in that answers in place of a real service during a test, so the test runs offline."},
    ],
    "sections": [
        {
            "h": "The requests library is still the default for scripts",
            "body": """The Day 15 health checker used `urllib.request` from the standard library. That is fine for a status code. Once you need JSON, headers, sessions and retries, use a library. There are two serious choices:

- requests: synchronous, with an API that has barely changed in years, and a mocking library, `responses`, made for it.
- httpx: almost the same API, plus async code and HTTP/2.

For ops scripts, pick requests today. The httpx project has had no stable release since 0.28.1 in December 2024. Its 1.0 has been out only as development releases that change the API, and Pydantic now maintains a fork named httpx2 that keeps the old one. That split will settle. Until it does, a script that runs from cron for three years is better off on the library that does not move. Reach for httpx2 when you really need async or HTTP/2.

Four habits make every call safe:

1. Always pass `timeout=`. Requests has no default, so a server that accepts the connection and never answers hangs your script forever. The value `timeout=(3.05, 10)` waits 3.05 seconds to connect and 10 seconds for each part of the answer. The requests docs suggest a connect value slightly above a multiple of 3, the default TCP retransmission window.
2. Call `response.raise_for_status()`. A 404 or a 500 is not an exception in requests until you ask for one.
3. Read the body with `response.json()`, after the status check.
4. Use a `requests.Session` for more than one call. It keeps the connection open and sends the same headers every time.""",
            "refs": [
                {"title": "requests: Advanced usage (timeouts, sessions, retries)", "url": "https://requests.readthedocs.io/en/latest/user/advanced/", "kind": "docs"},
                {"title": "Python Requests tutorial (Corey Schafer)", "url": "https://www.youtube.com/watch?v=tb8gHvYlCFs", "kind": "watch"},
                {"title": "httpx2, Pydantic's continuation of httpx", "url": "https://github.com/pydantic/httpx2", "kind": "read"},
            ],
        },
        {
            "h": "Tokens, retries and pages: the GitHub API",
            "body": """`gh-runs` asks GitHub for a repo's recent Actions runs with `GET https://api.github.com/repos/OWNER/REPO/actions/runs`. Three headers go with every request:

- `Accept: application/vnd.github+json`, the media type GitHub recommends.
- `X-GitHub-Api-Version: 2026-03-10`, the newest API version. Without the header, GitHub picks one for you; it answered with `2022-11-28` when we left it out.
- `Authorization: Bearer <token>`, with the token read from the `GITHUB_TOKEN` environment variable.

Locally, `export GITHUB_TOKEN="$(gh auth token)"` borrows the token the gh CLI got on Day 2. In GitHub Actions, the same variable can come from the built-in token (Day 27). The script never prints the token and never takes it as a flag, because flags end up in your shell history and in `ps` output. Without a token you get 60 requests an hour, and with one you get 5,000.

Retry only when asking again can help: a 429 (too many requests), a 502, 503 or 504, or a dropped connection. Never retry a 401 or a 404, because the answer will not change. Retry only idempotent methods (Day 11): a repeated GET is harmless, while a repeated POST may start two deploys. Requests does none of this by default. The lab mounts urllib3's `Retry` on the session with `status_forcelist=[429, 500, 502, 503, 504]` and `allowed_methods=["GET"]`. With `backoff_factor=1` it waits 0, then 2, then 4 seconds, and it obeys a `Retry-After` header when the server sends one.

GitHub returns at most 100 items per page and puts the next page's address in the `Link` header. Requests parses that header into `response.links["next"]["url"]`. The `list_runs` function follows it until there is no next page or it has enough runs.""",
            "refs": [
                {"title": "GitHub REST API: using pagination", "url": "https://docs.github.com/en/rest/using-the-rest-api/using-pagination-in-the-rest-api", "kind": "docs"},
                {"title": "GitHub REST API: rate limits", "url": "https://docs.github.com/en/rest/using-the-rest-api/rate-limits-for-the-rest-api", "kind": "docs"},
                {"title": "GitHub REST API: workflow runs", "url": "https://docs.github.com/en/rest/actions/workflow-runs", "kind": "docs"},
            ],
        },
        {
            "h": "AWS from Python: boto3 sessions, profiles and clients",
            "body": """Boto3 is AWS's SDK for Python. Every script starts from a session, which holds one set of credentials and one region:

- `boto3.Session(profile_name="learn")` uses the `learn` profile from Day 13. Run `aws login --profile learn` first, and boto3 picks up the same sign-in. That needs boto3's `crt` extra, which the lab's `pyproject.toml` asks for.
- Leave the profile out and boto3 searches the usual places in order: environment variables such as `AWS_PROFILE`, the files in `~/.aws`, and finally a container or instance role (Day 14).
- `session.client("s3")` gives you a client. It has one method per API call, in snake_case, so ListBuckets becomes `list_buckets()`.

Answers are plain dictionaries, shaped like the JSON the CLI printed on Day 13. Errors come in two families:

- `botocore.exceptions.ClientError`: AWS answered with an error. `err.response["Error"]["Code"]` holds a code such as `AccessDenied` or `NoSuchBucket`, and you decide per code.
- `botocore.exceptions.BotoCoreError`: no useful answer at all. No credentials, an unknown profile and an expired sign-in all land here.

Start every AWS script with `sts.get_caller_identity()` and log the account and identity it returns. It is the Python twin of `aws sts get-caller-identity`, it needs no permissions, and it catches "wrong account" before anything else runs.

Use clients rather than the older resource interface (`boto3.resource`). The boto3 docs say AWS does not intend to add new features to resources.""",
            "refs": [
                {"title": "boto3: Low-level clients (and waiters)", "url": "https://docs.aws.amazon.com/boto3/latest/guide/clients.html", "kind": "docs"},
                {"title": "boto3: Error handling", "url": "https://docs.aws.amazon.com/boto3/latest/guide/error-handling.html", "kind": "docs"},
            ],
        },
        {
            "h": "Paginators, waiters and a read-only report",
            "body": """Most AWS list calls return one page at a time. For example, `list_objects_v2` returns at most 1,000 keys and a token for the next page. A script that forgets this sees 1,000 objects in a bucket that holds 5,000. A paginator asks for every page for you. The call `ec2.get_paginator("describe_instances").paginate(Filters=[...])` gives an iterator of pages. Then `pages.search("Reservations[].Instances[]")` pulls every instance out of them with JMESPath, the same language as `--query` on Day 13.

A waiter polls until a resource reaches a state. The waiter from `ec2.get_waiter("instance_running")` calls DescribeInstances every 15 seconds, up to 40 times, then raises `WaiterError`. Each client lists its waiters in `waiter_names`; S3 has four, including `bucket_exists`. The lab uses waiters wherever code creates something and must wait for it: in `seed_moto.py` and in the tests.

`aws-report` puts the pieces together. It only reads, and it needs three permissions: `s3:ListAllMyBuckets`, `s3:GetBucketVersioning` and `ec2:DescribeInstances`. It reports two things:

- S3 buckets where versioning is off or suspended. Versioning keeps old copies of objects, so an overwrite or a delete can be undone, which is why Day 13's bucket has it on.
- EC2 instances that still exist and have no `owner` tag, so nobody knows whom to ask before stopping them. Stopped instances count, because their disks still cost money.

A bucket the script may not read becomes a finding, `cannot read versioning (AccessDenied)`, instead of a crash. A report that dies on bucket 3 of 200 tells you nothing about the other 197.""",
            "refs": [
                {"title": "boto3: Paginators", "url": "https://docs.aws.amazon.com/boto3/latest/guide/paginators.html", "kind": "docs"},
                {"title": "AWS SDKs: service-specific endpoints (AWS_ENDPOINT_URL)", "url": "https://docs.aws.amazon.com/sdkref/latest/guide/feature-ss-endpoints.html", "kind": "docs"},
            ],
        },
        {
            "h": "Testing scripts with pytest",
            "body": """A script that runs at 3 a.m. deserves tests as much as the app it watches. The pytest runner finds files named `test_*.py` and runs every function named `test_*`. When an `assert` fails, it shows the values on both sides. In the lab, `uv run pytest` runs 30 tests in about 8 seconds, offline.

The `main(argv) -> int` shape from Day 15 is what makes this easy: call `main(["access", str(path)])` and assert on the number it returns. Three built-in fixtures do most of the rest. A fixture is something pytest prepares for a test that names it as an argument:

- `tmp_path` is a fresh empty folder for this one test. Write a three-line log into it, with one broken line, instead of depending on real files.
- `monkeypatch` changes things for one test only. `monkeypatch.setenv("LOGSUM_MAX_ERROR_RATE", "50")` and `monkeypatch.delenv("GITHUB_TOKEN")` are undone when the test ends, so no test leaks settings into the next.
- `capsys` captures what the code printed. `out, err = capsys.readouterr()` lets you check that the report went to stdout and the reason went to stderr.

You can write your own fixtures with `@pytest.fixture`, and code after a `yield` inside one runs as cleanup. The file `test_healthcheck.py` uses that to start a real web server on 127.0.0.1 for each test. The server shuts down afterwards, so the 503 and timeout cases are real without leaving the laptop.

What deserves a test in an ops script? The exit codes, the parsing of realistic input including one malformed line, and every error message a tired person will read. Leave argparse and requests alone; their own authors test them.""",
            "refs": [
                {"title": "pytest: How to monkeypatch/mock modules and environments", "url": "https://docs.pytest.org/en/stable/how-to/monkeypatch.html", "kind": "docs"},
                {"title": "pytest: How to use temporary directories and files", "url": "https://docs.pytest.org/en/stable/how-to/tmp_path.html", "kind": "docs"},
                {"title": "Please learn how to write tests in Python: pytest tutorial (Tech With Tim)", "url": "https://www.youtube.com/watch?v=EgpLj86ZHFQ", "kind": "watch"},
            ],
        },
        {
            "h": "Fake services: responses for HTTP, moto for AWS",
            "body": """Tests that call the real GitHub or AWS are slow and flaky, and they need secrets in CI. Replace the service and keep your code as it is.

`responses` patches requests so that registered URLs get canned answers. Inside a test marked `@responses.activate`, `responses.get(url, json={...}, status=200)` registers one answer. A request to any URL you did not register raises `ConnectionError`, so a test cannot reach the internet by accident. Matchers check what you sent, such as the `Authorization` header. `registries.OrderedRegistry` hands out answers in order, a 502 and then a 200, which proves the retry works. Pass `backoff=0` in that test so it does not sleep.

Moto does the same for AWS. Inside `with mock_aws():`, every boto3 call goes to an in-memory fake AWS that starts empty for each test. The test creates the buckets and instances it needs, then calls the real function. Two rules from the moto docs:

1. Set fake credentials first, `AWS_ACCESS_KEY_ID=testing` and the rest, with `monkeypatch.setenv`. If your shell holds real keys, this makes sure they are never used.
2. Start the mock before you create any client. A client made earlier, for example at import time, is not mocked.

Moto is a model of AWS, not AWS. It does not check IAM permissions unless you ask it to, so a test passes even when the real role would be denied. It also has quirks: in the lab, a bucket named `logs` failed in moto with a 404, and a rename fixed it. Run a new check once against a real account before you trust it. The same moto also runs as a server (`moto_server -p 5050`) that boto3 reaches through `AWS_ENDPOINT_URL`, the same idea as `--endpoint-url` on Day 13.""",
            "refs": [
                {"title": "Moto: getting started", "url": "https://docs.getmoto.org/en/latest/docs/getting_started.html", "kind": "docs"},
                {"title": "responses: mock the requests library", "url": "https://github.com/getsentry/responses", "kind": "read"},
            ],
        },
        {
            "h": "Ship it: a command, ruff and CI",
            "body": """A folder of scripts becomes a tool when teammates can install it. `pyproject.toml` lists commands under `[project.scripts]`. The line `gh-runs = "python_ops.gh_runs:main"` means: make a command named `gh-runs` that calls `main` in that module. Since uv 0.12, `uv init` creates this kind of project by default, with the code under `src/` and uv's own build backend. Three ways to use the commands:

- `uv run gh-runs ...` inside the project folder.
- `uv tool install --editable .` puts `gh-runs` and `aws-report` on your PATH, each in its own environment. With `--editable`, your code changes apply without reinstalling.
- `uv tool install git+https://github.com/YOU/python-ops` installs them for a teammate straight from git.

ruff lints and formats in one fast tool: `uv run ruff check` finds likely bugs, and `uv run ruff format` fixes the layout. The lab turns on a few rule groups that suit ops code, each explained in `pyproject.toml`. Three of them earn their place:

- `S113` flags `requests.get(url)` without a timeout. It does not see calls on a `Session`, so the habit still matters.
- `S602` flags `shell=True`, and `PLW1510` flags `subprocess.run` without `check=`.
- `DTZ` flags naive datetimes such as `datetime.now()`.

Last comes CI. The lab's `ci.yml` installs uv with `astral-sh/setup-uv`, runs `uv sync --locked`, then ruff and pytest. `--locked` fails the job when `uv.lock` no longer matches `pyproject.toml`. Each step fails the job through its exit code, just like the scripts themselves. Day 25 builds a full pipeline with caching and a matrix; this one is a short preview you can push today.""",
            "refs": [
                {"title": "uv: Using tools (uv tool install)", "url": "https://docs.astral.sh/uv/guides/tools/", "kind": "docs"},
                {"title": "uv: Using uv in GitHub Actions", "url": "https://docs.astral.sh/uv/guides/integration/github/", "kind": "docs"},
                {"title": "The Ruff linter", "url": "https://docs.astral.sh/ruff/linter/", "kind": "docs"},
            ],
        },
    ],
    "analogy": "The responses and moto libraries work like a flight simulator. Pilots practise an engine failure in the simulator, because nobody can arrange one on a real flight. Your tests practise a 502, an expired token or an untagged instance the same way. A simulator is only as good as its model of the aircraft, though. Moto does not check IAM permissions by default, so a test can pass while the real call would be denied. One flight in the real thing is still part of the training.",
    "diagram": D16_DIAGRAM,
    "diagram_caption": "The same code talks to the real service in a run and to a fake one under pytest.",
    "worked": {
        "title": "gh-runs, from a raw request to a tested command",
        "steps": [
            {
                "say": "Look at the raw answer before you write code. The JSON has a total and a list of runs, and the `Link` header holds the next page. Public repos need no token; your numbers will differ.",
                "code": "$ curl -s -H \"Accept: application/vnd.github+json\" -H \"X-GitHub-Api-Version: 2026-03-10\" \\\n    \"https://api.github.com/repos/arunav-bhattacharya/devops-from-zero/actions/runs?per_page=2\" \\\n    | jq -c '{total_count, first: (.workflow_runs[0] | {run_number, name, conclusion, head_branch})}'\n{\"total_count\":21,\"first\":{\"run_number\":19,\"name\":\"deploy\",\"conclusion\":\"success\",\"head_branch\":\"main\"}}\n$ curl -sI -H \"X-GitHub-Api-Version: 2026-03-10\" \"https://api.github.com/repos/arunav-bhattacharya/devops-from-zero/actions/runs?per_page=2\" | grep -i '^link'\nLink: <https://api.github.com/repositories/1439251123/actions/runs?per_page=2&page=2>; rel=\"next\", <https://api.github.com/repositories/1439251123/actions/runs?per_page=2&page=11>; rel=\"last\"",
                "lang": "console",
            },
            {
                "say": "Now the tool. Borrow the gh CLI's token through an environment variable and ask for five runs. Every run passed, so the exit code is 0.",
                "code": "$ cd ~/code/python-ops\n$ export GITHUB_TOKEN=\"$(gh auth token)\"\n$ uv run gh-runs arunav-bhattacharya/devops-from-zero --limit 5\n#19    success    main                 2026-11-07 17:08:47  deploy\n#18    success    main                 2026-11-07 17:08:26  deploy\n#17    success    main                 2026-11-07 17:07:16  deploy\n#16    success    main                 2026-11-07 17:02:26  deploy\n#15    success    main                 2026-11-07 16:46:25  deploy\n5 runs, 0 failed\n$ echo $?\n0",
                "lang": "console",
            },
            {
                "say": "`-v` turns on DEBUG logging, and urllib3 then logs every HTTP request it sends. It is the quickest way to see the query string, the pages and any retries.",
                "code": "$ uv run gh-runs arunav-bhattacharya/devops-from-zero --limit 2 -v\nurllib3.connectionpool: Starting new HTTPS connection (1): api.github.com:443\nurllib3.connectionpool: https://api.github.com:443 \"GET /repos/arunav-bhattacharya/devops-from-zero/actions/runs?per_page=2 HTTP/1.1\" 200 None\n#19    success    main                 2026-11-07 17:08:47  deploy\n#18    success    main                 2026-11-07 17:08:26  deploy\n2 runs, 0 failed",
                "lang": "console",
            },
            {
                "say": "Ask for more runs and the old failures appear. The table stays on stdout and the links to the failed runs go to stderr. The exit code turns 1, which is what a scheduled CI job would act on. (Output trimmed.)",
                "code": "$ uv run gh-runs arunav-bhattacharya/devops-from-zero --limit 25\n...\n#2     failure    main                 2026-10-31 23:13:08  deploy\n#1     failure    main                 2026-10-31 23:05:20  deploy\n21 runs, 4 failed\ngh-runs: failed: deploy #4 https://github.com/arunav-bhattacharya/devops-from-zero/actions/runs/42391569154\ngh-runs: failed: deploy #3 https://github.com/arunav-bhattacharya/devops-from-zero/actions/runs/41251679651\ngh-runs: failed: deploy #2 https://github.com/arunav-bhattacharya/devops-from-zero/actions/runs/41251586511\ngh-runs: failed: deploy #1 https://github.com/arunav-bhattacharya/devops-from-zero/actions/runs/41251021139\n$ echo $?\n1",
                "lang": "console",
            },
            {
                "say": "A wrong token, a used-up rate limit or a 502 are hard to cause on purpose, so the tests cause them with `responses`. All eight run in a tenth of a second, with no network.",
                "code": "$ uv run pytest tests/test_gh_runs.py -v\ntests/test_gh_runs.py::test_sends_token_and_version_headers PASSED       [ 12%]\ntests/test_gh_runs.py::test_follows_the_link_header_to_the_next_page PASSED [ 25%]\ntests/test_gh_runs.py::test_failed_run_exits_1_and_names_it PASSED       [ 37%]\ntests/test_gh_runs.py::test_run_in_progress_shows_its_status PASSED      [ 50%]\ntests/test_gh_runs.py::test_retries_a_502_then_succeeds PASSED           [ 62%]\ntests/test_gh_runs.py::test_bad_token_exits_2_with_a_hint PASSED         [ 75%]\ntests/test_gh_runs.py::test_rate_limit_says_when_it_resets PASSED        [ 87%]\ntests/test_gh_runs.py::test_no_token_warns PASSED                        [100%]\n============================== 8 passed in 0.12s ===============================",
                "lang": "console",
            },
            {
                "say": "Let ruff catch the classic slip. In a scratch file, a bare `requests.get` without a timeout is flagged as S113. Then install the commands for everyday use; `--editable` keeps them pointing at your folder. (Output trimmed.)",
                "code": "$ uv run ruff check --output-format concise scratch.py\nscratch.py:3:5: S113 Probable use of `requests` call without timeout\nFound 1 error.\n$ uv tool install --editable .\nInstalled 2 executables: aws-report, gh-runs\n$ gh-runs --help | head -n 1\nusage: gh-runs [-h] [--branch BRANCH] [--limit LIMIT] [--per-page PER_PAGE]",
                "lang": "console",
            },
        ],
    },
    "code": [
        {"lang": "ini", "title": "pyproject.toml (in labs/python-ops)", "src": lab("pyproject.toml"), "run": "uv sync && uv run pytest && uv run ruff check"},
        {"lang": "python", "title": "src/python_ops/gh_runs.py", "src": lab("src/python_ops/gh_runs.py"), "run": "GITHUB_TOKEN=\"$(gh auth token)\" uv run gh-runs YOUR-USER/hello-devops --limit 10"},
        {"lang": "python", "title": "src/python_ops/aws_report.py", "src": lab("src/python_ops/aws_report.py"), "run": "uv run aws-report --profile learn"},
        {"lang": "python", "title": "tests/test_gh_runs.py", "src": lab("tests/test_gh_runs.py"), "run": "uv run pytest tests/test_gh_runs.py -v"},
        {"lang": "python", "title": "tests/test_aws_report.py", "src": lab("tests/test_aws_report.py"), "run": "uv run pytest tests/test_aws_report.py -v"},
        {"lang": "python", "title": "scripts/seed_moto.py", "src": lab("scripts/seed_moto.py"), "run": "AWS_ENDPOINT_URL=http://localhost:5050 AWS_ACCESS_KEY_ID=testing AWS_SECRET_ACCESS_KEY=testing uv run scripts/seed_moto.py"},
        {"lang": "yaml", "title": ".github/workflows/ci.yml", "src": lab(".github/workflows/ci.yml"), "run": "git add .github/workflows/ci.yml && git commit -m 'Add CI' && git push"},
    ],
    "commands": [
        {"cmd": "uv add requests \"boto3[crt]\"", "what": "Add runtime dependencies to pyproject.toml and uv.lock."},
        {"cmd": "uv add --dev pytest ruff responses \"moto[ec2,s3]\"", "what": "Add tools only needed while developing, in the dev group."},
        {"cmd": "export GITHUB_TOKEN=\"$(gh auth token)\"", "what": "Hand the gh CLI's token to scripts through an environment variable."},
        {"cmd": "uv run gh-runs OWNER/REPO --limit 20 -v", "what": "List recent workflow runs and log every HTTP request."},
        {"cmd": "aws login --profile learn", "what": "Sign in the Day 13 profile, so the CLI and boto3 get short-lived credentials."},
        {"cmd": "uv run aws-report --profile learn --format json", "what": "Run the read-only AWS report and print JSON."},
        {"cmd": "uvx --from \"moto[server]\" moto_server -p 5050", "what": "Start a local fake AWS on port 5050 (Ctrl+C stops it and forgets everything)."},
        {"cmd": "export AWS_ENDPOINT_URL=http://localhost:5050", "what": "Send every boto3 and AWS CLI call to that local endpoint."},
        {"cmd": "uv run pytest -q", "what": "Run all tests quietly."},
        {"cmd": "uv run pytest -k retries -v", "what": "Run only the tests whose names contain 'retries', one line each."},
        {"cmd": "uv run ruff check --fix", "what": "Lint the code and fix what can be fixed safely."},
        {"cmd": "uv run ruff format", "what": "Rewrite the code in ruff's standard layout."},
        {"cmd": "uv tool install --editable .", "what": "Put the project's commands on your PATH; code edits apply at once."},
        {"cmd": "uv tool list", "what": "Show installed tools and the commands each one provides."},
        {"cmd": "uv sync --locked", "what": "Install exactly what uv.lock says, and fail if it is out of date (for CI)."},
    ],
    "mistake": "Creating a boto3 client at the top of a module, `s3 = boto3.client(\"s3\")`, and then starting moto inside the test. The client already exists when the mock starts, so moto may not intercept it, and the test can reach real AWS with whatever credentials your shell had. Create clients inside functions, or pass them in, and start `mock_aws()` with fake credentials before any client is made.",
    "real_world": "Untagged instances are the ones nobody dares to stop, and buckets without versioning are the ones nobody can restore. Platform teams run a read-only report like `aws-report` on a schedule in every account. It assumes a role that can only list and describe, and it posts the findings to the owning team's channel. The report has moto tests in CI, so a change to it cannot break the Monday run.",
    "task": {
        "title": "Teach aws-report to find SSH open to the world",
        "steps": [
            "In terminal 1, start a fake AWS: `uvx --from \"moto[server]\" moto_server -p 5050`.",
            "In terminal 2, in `~/code/python-ops`, export `AWS_ENDPOINT_URL=http://localhost:5050`, `AWS_ACCESS_KEY_ID=testing`, `AWS_SECRET_ACCESS_KEY=testing` and `AWS_DEFAULT_REGION=eu-central-1`. Then run `uv run scripts/seed_moto.py` and `uv run aws-report`.",
            "Create a security group that allows port 22 from `0.0.0.0/0` in moto with the AWS CLI from Day 13: `aws ec2 create-security-group` and `aws ec2 authorize-security-group-ingress`, with the same endpoint.",
            "Add a function `ssh_open_to_world(ec2)` to `aws_report.py`. It goes through every security group with a paginator and reports groups whose rules allow port 22 from `0.0.0.0/0` or `::/0`.",
            "Call it from `main`, print the findings in text and JSON, and include them in the exit code.",
            "Write a moto test with three groups: SSH from `0.0.0.0/0`, SSH from `10.0.0.0/8` and HTTPS from `0.0.0.0/0`. Only the first may be reported.",
            "Run `uv run pytest` and `uv run ruff check`, and fix anything they report.",
            "Run `uv run aws-report` against the moto server again and check that your group appears and the exit code is 1.",
            "Optional, with a real account: run `aws login --profile learn`, then `uv run aws-report --profile learn`. It only reads, so it costs nothing.",
        ],
        "hints": [
            "`describe_security_groups` has a paginator; each group has `IpPermissions`, and each permission has `FromPort`, `ToPort`, `IpRanges` and `Ipv6Ranges`.",
            "`IpProtocol` of `\"-1\"` means all traffic, and then there is no `FromPort`; read the ports with `.get()`.",
            "moto creates a `default` group in every VPC; your function must not report it.",
        ],
        "done_when": "You are done when `uv run pytest` passes with your new test, and `aws-report` against the seeded moto server lists your open SSH group and exits 1.",
    },
    "explain_back": {
        "prompt": "Explain in 3 to 4 sentences how you make a script that calls an API safe to run in CI, and how you test it without the network. Mention timeouts, retries and mocks.",
        "answer": "Every call gets a timeout, so a silent server cannot hang the job. Retries go only to errors that may pass, such as 429 and 5xx, only for idempotent methods, with growing waits, and never for 401 or 404. Errors become one clear line on stderr and a non-zero exit code, and the token comes from an environment variable. In tests, responses answers in place of the HTTP API and moto in place of AWS, so pytest can check retries, failures and exit codes offline.",
    },
    "recap": [
        "Use requests for scripts, and always pass a timeout and call raise_for_status().",
        "Retry 429 and 5xx with backoff on idempotent methods only; never retry 401 or 404.",
        "Follow the Link header or a boto3 paginator, or you only see the first page.",
        "A boto3 session holds one profile and region; catch ClientError and BotoCoreError separately.",
        "Test with tmp_path, monkeypatch and capsys; fake HTTP with responses and AWS with moto.",
        "[project.scripts] plus `uv tool install` turns scripts into commands; ruff and CI keep them honest.",
    ],
    "check": [
        {
            "q": "A cleanup script lists objects with `s3.list_objects_v2(Bucket=b)` and deletes the old ones. The bucket holds 4,000 objects. What happens?",
            "options": [
                "It sees every object, since boto3 pages automatically",
                "It raises an error asking for a paginator",
                "It only sees the first 1,000 objects",
                "It sees nothing until versioning is enabled",
            ],
            "answer": 2,
            "why": "A single call returns at most 1,000 keys; use `get_paginator(\"list_objects_v2\")` to get every page.",
        },
        {
            "q": "A script sends `POST /deployments` through a session whose urllib3 `Retry` lists 502 in `status_forcelist` but keeps the default allowed methods. The API answers 502. What happens?",
            "options": [
                "It returns the 502, since POST is not retried by default",
                "It retries the POST three times with backoff",
                "It turns the POST into a GET and retries",
                "It retries once, and only after waiting 60 seconds",
            ],
            "answer": 0,
            "why": "urllib3 retries only idempotent methods by default, because repeating a POST could create two deployments.",
        },
        {
            "q": "A test marked `@responses.activate` registers only `/actions/runs`, but the code also calls `/rate_limit`. What happens in the test?",
            "options": [
                "The call goes to the real api.github.com",
                "requests returns an empty 200 answer",
                "The test is skipped with a warning",
                "requests raises ConnectionError for the unregistered URL",
            ],
            "answer": 3,
            "why": "responses refuses every URL you did not register, so a test can never reach the network by accident.",
        },
    ],
    "interview": [
        {
            "q": "How do you make HTTP calls from a script reliable?",
            "a": "Every call has a timeout, because requests waits forever by default. I use a Session so headers and connections are reused, and I mount a retry policy that retries 429 and 5xx answers with exponential backoff and honours Retry-After. Only idempotent methods are retried, and 401 or 404 never are. After the call I check the status with raise_for_status, and I turn errors into a clear message and a non-zero exit code.",
        },
        {
            "q": "How do you test code that calls AWS?",
            "a": "For unit tests I use moto's mock_aws, which fakes AWS in memory. I set fake credentials first, so real ones can never be used. Each test creates the resources it needs and then calls the real function, with every client created after the mock starts. Moto does not check IAM by default, so I also run new checks once against a sandbox account with a least-privilege role. For error paths that are hard to fake, I raise a ClientError myself with monkeypatch or use botocore's Stubber.",
        },
        {
            "q": "What are boto3 paginators and waiters for?",
            "a": "Many AWS list calls return one page of results plus a token, so code that makes one call silently misses data. A paginator follows the tokens for you, and its search method can pull items out of every page with JMESPath. A waiter polls a describe call until a resource reaches a state, such as an instance running. It waits a fixed delay between tries and gives up after a maximum number of attempts. Both replace hand-written loops that are easy to get wrong.",
        },
    ],
    "deeper": {
        "minutes": 15,
        "body": """Kubernetes has an official Python client too, the `kubernetes` package. Part 10 teaches clusters with kubectl; this is what the same questions look like from Python, once you have a cluster.

The client reads the same kubeconfig as kubectl:

1. `config.load_kube_config()` loads `~/.kube/config` and its current context, exactly like kubectl on your laptop.
2. `v1 = client.CoreV1Api()` gives an API object for the core resources: pods, services, namespaces.
3. `v1.list_pod_for_all_namespaces(watch=False)` returns objects with attributes, so `pod.metadata.name` and `pod.status.phase` work without any JSON parsing.

Inside a pod, use `config.load_incluster_config()` instead. It reads the token and the CA certificate that Kubernetes mounts for the pod's service account, so no kubeconfig file is needed. What the script may do is then decided by RBAC rules for that service account (Day 64). A read-only report needs only `get` and `list` on the resources it reads.

A report in the style of today's tools would list pods that are not Ready: for each pod, look at `pod.status.conditions` for the condition of type `Ready` with status `False`. Then print a table, return 1 when the list is not empty, and test it with a fake object instead of a cluster. Because the client returns objects, a test can build a few with `client.V1Pod(...)` and pass them to your function, with no network at all.

The client also supports watching. `watch.Watch().stream(v1.list_namespace, _request_timeout=60)` yields an event every time a namespace is added, changed or deleted. Set a timeout here too, for the same reason as with requests.

When should you use the client rather than `subprocess.run(["kubectl", "get", "pods", "-o", "json"], ...)` plus `json.loads`? The kubectl route is fine for a quick script on your laptop, and its output matches what you see in the terminal. The client wins for anything that runs inside the cluster, needs watches, or should not depend on a kubectl binary being installed. The package's major version follows Kubernetes releases, and its README has a compatibility table, so pick the version that matches your cluster, as you did with kubectl itself.

Start from the examples in the [Kubernetes Python client README](https://github.com/kubernetes-client/python). They run against the kind cluster you build in Part 10.""",
    },
    "sources": [
        {"title": "requests: Advanced usage", "url": "https://requests.readthedocs.io/en/latest/user/advanced/"},
        {"title": "boto3: Paginators", "url": "https://docs.aws.amazon.com/boto3/latest/guide/paginators.html"},
        {"title": "Moto: getting started", "url": "https://docs.getmoto.org/en/latest/docs/getting_started.html"},
        {"title": "pytest: How to monkeypatch/mock modules and environments", "url": "https://docs.pytest.org/en/stable/how-to/monkeypatch.html"},
    ],
}
