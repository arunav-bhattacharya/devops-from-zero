"""Fifth pass (book voice) for d16."""
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from common import load, apply, save

path, P, L, OL = load(4, "d16")

new = {}
new["goal"] = r"""By the end you can call the GitHub API and AWS from Python with timeouts, retries and pagination, test both without a network, and install the result as a command."""

new["opening"] = r"""Picture the helper's new morning job: phone the supplier and ask which of yesterday's orders went wrong. Most days that takes a minute. One morning the supplier picks up, says nothing, and never hangs up. The helper was told to "call and wait for the answer", so it stands there with the phone at its ear until you come back at noon. There is no report, and no error either.

It's an easy trap, because a call that never ends doesn't look like a failure. It just looks slow. Last time, our helper read a log file on your own laptop and reported done or failed. Today it calls services over the internet: GitHub, where code and its automatic checks live, and AWS, Amazon's cloud. We'll teach it to hang up in time, call back only when that can help, and read long answers to the last page. Then it rehearses with stand-ins, so its tests need no network.

Before we start, make a guess, and keep it in mind."""

new["guess_q"] = r"""Your script calls `requests.get(url)` without a timeout. The server accepts the connection and then never answers. How long does your script wait?"""
new["guess_why"] = r"""requests has no default timeout, so the call can hang for as long as the connection stays open, like the helper holding a silent phone. Always pass `timeout=`, for example `timeout=(3.05, 10)`."""

new["terms"] = {
    "REST API": "A web service that programs call with web requests to addresses (URLs), usually trading data as JSON text.",
    "Timeout": "The longest your code waits for a connection or an answer before it gives up with an error.",
    "Exponential backoff": "Waiting longer after each failed try, for example 2 seconds, then 4, then 8, so a busy server can recover.",
    "Pagination": "Splitting a long list into pages, so you ask for the next page until there is none.",
    "boto3 client": "A Python object for one AWS service, with one method for each thing the service can do, such as `s3.list_buckets()`.",
    "Paginator": "A boto3 helper that fetches every page of a list for you.",
    "Waiter": "A boto3 helper that checks with AWS again and again until something reaches a state, such as a server that is running.",
    "Mock": "A stand-in that answers in place of a real service during a test, so the test runs offline.",
}

S = []
S.append(("A call that never ends: requests and four habits", r"""The helper's phone call has a computer version. An API is a door that a web service opens for programs instead of people. A program knocks with HTTP, the language browsers and web servers speak. It sends a request to a URL (a web address). The answer has a status code, such as 200 for fine or 404 for not found, and a body, often JSON.

The Day 15 health checker used `urllib.request` from the standard library. That is fine for a status code. Once you need JSON, headers (labels sent with each request), sessions and retries, use a library: a package of ready-made code. For ops scripts, pick requests today. Its API has barely changed in years, and a mocking library, `responses`, is made for it. A newer library, httpx, looks almost the same; Go deeper explains why the course stays with requests.

Four habits make every call safe:

1. Always pass `timeout=`. Requests has no default, so a server that accepts the connection and never answers hangs your script forever: the silent phone from the opening. The value `timeout=(3.05, 10)` waits up to 3.05 seconds to connect, then up to 10 seconds of silence while the answer arrives. It does not limit the whole download.
2. Call `response.raise_for_status()`. A 404 or a 500 is not an exception (an error that stops the code) in requests until you ask for one.
3. Read the body with `response.json()`, after the status check.
4. Use a `requests.Session` for more than one call. It keeps the connection open, so later calls skip the TCP and TLS handshakes (Days 10 and 11), the greetings two computers trade before they talk. It also sends the same headers every time.

**A call without a timeout is a promise to wait forever. Always set one.**

With a safe call in hand, the helper can phone its first real service: GitHub."""))

S.append(("Calling GitHub: a key card, polite retries and pages", r"""GitHub Actions is GitHub's CI service: it runs your checks on every change, and each time it does is called a run. The lab's first tool, `gh-runs`, lists a repo's (a project's) recent runs and exits 1 when one of them failed. It asks with `GET https://api.github.com/repos/OWNER/REPO/actions/runs`, where GET is the HTTP method for reading. Three headers go with every request:

- `Accept: application/vnd.github+json`, the format GitHub recommends.
- `X-GitHub-Api-Version: 2026-03-10`, the newest API version. Pinning it keeps a later version from changing the JSON under your script.
- `Authorization: Bearer <token>`. A token is a long secret string that proves who you are, like a key card: whoever bears (holds) it gets in. The script reads it from the `GITHUB_TOKEN` environment variable.

Locally, `export GITHUB_TOKEN="$(gh auth token)"` borrows the token the gh command-line tool got on Day 2. In GitHub Actions, the same variable can come from the built-in token (Day 27). The script never prints the token and never takes it as a flag, because flags end up in your shell history and in `ps`, the list of running programs. Without a token you get 60 requests an hour, and with one you get 5,000.

Back to the supplier's phone. When the line is busy, calling back later helps. When the supplier says "no such order", calling back gets the same answer. So retry only a 429 (too many requests), a 502, 503 or 504, or a dropped connection. Never retry a 401 (bad token) or a 404, because the answer will not change. Retry only idempotent methods (Day 11), where asking twice does no more than asking once: a repeated GET is harmless, while a repeated POST may start two deploys.

Requests does none of this by default. Underneath, it sends every call through urllib3, a lower-level library with a `Retry` class. The lab attaches one to the session with `session.mount("https://", ...)`, using `status_forcelist=[429, 500, 502, 503, 504]` and `allowed_methods=["GET"]`. With `backoff_factor=1` it waits 0, then 2, then 4 seconds, and it obeys a `Retry-After` header when the server sends one.

One request returns one page: 30 runs unless you ask for more with `per_page`, and never more than 100. GitHub puts the next page's address in the `Link` header, and requests parses it into `response.links["next"]["url"]`. The `list_runs` function follows it until there is no next page or it has enough runs.

GitHub was one supplier. Next comes a much bigger one."""))

S.append(("Talking to AWS: sessions, profiles and clients", r"""AWS rents out computers, storage and much more, and each service has an API. Boto3 is AWS's SDK (software development kit) for Python, a library that turns each method call into an HTTPS (encrypted HTTP) request to an AWS API. The request is signed with your credentials, the secret keys that prove who you are, so AWS knows who is asking.

Every script starts from a session, which holds one set of credentials and one region (the part of the world where your resources live):

- `boto3.Session(profile_name="learn")` uses the `learn` profile from Day 13, a named set of sign-in settings. Run `aws login --profile learn` first, and boto3 picks up the same sign-in. That needs the `boto3[crt]` add-on, which the lab's `pyproject.toml` asks for.
- Leave the profile out, and boto3 searches in order. It tries environment variables such as `AWS_PROFILE`, then the files in `~/.aws`, and finally the role of the container or server it runs on (Day 14).
- `session.client("s3")` gives you a client for one service. It has one method per API call, in snake_case (lowercase words joined by `_`), so ListBuckets becomes `list_buckets()`.

Answers are plain dictionaries (sets of named values), shaped like the JSON the AWS CLI printed on Day 13. Errors come in two families:

- `botocore.exceptions.ClientError`: AWS answered with an error. `err.response["Error"]["Code"]` holds a code such as `AccessDenied` or `NoSuchBucket`, and you decide per code.
- `botocore.exceptions.BotoCoreError`: no useful answer at all. No credentials, an unknown profile and an expired sign-in all land here.

Now picture the helper phoning the wrong branch and reading your orders to strangers. Start every AWS script with `sts.get_caller_identity()` and log the account and identity it returns. It is the Python twin of `aws sts get-caller-identity`, it needs no permissions, and it catches "wrong account" before anything else runs.

The helper can ask AWS questions now. But AWS, like GitHub, answers long lists one page at a time."""))

S.append(("Every page, and waiting for a server: a read-only report", r"""Ask the supplier for all 5,000 orders, and they read you the first 1,000 and stop. Most AWS list calls behave the same. S3 is AWS's file storage, where each named storage box is a bucket and each file is an object. The call `list_objects_v2` returns at most 1,000 keys (object names) and a token for the next page. A script that forgets this sees 1,000 objects in a bucket that holds 5,000.

A paginator asks for every page for you. EC2 is AWS's service for rented servers, called instances. The call `ec2.get_paginator("describe_instances").paginate(Filters=[...])` gives you the pages one after another. Then `pages.search("Reservations[].Instances[]")` pulls every instance out of them with JMESPath, the same query language as `--query` on Day 13.

Waiting is the other trap. When you call `run_instances`, AWS answers while the new instance is still `pending`, so code that uses it at once fails. A waiter polls, asking again and again, until a resource reaches a state. The waiter from `ec2.get_waiter("instance_running")` calls DescribeInstances every 15 seconds, up to 40 times, then raises `WaiterError`. The lab uses waiters wherever code creates something and must wait for it: in `seed_moto.py` and in the tests.

The lab's second tool, `aws-report`, puts the pieces together. It only reads, and it needs three permissions: `s3:ListAllMyBuckets`, `s3:GetBucketVersioning` and `ec2:DescribeInstances`. It reports two things:

- S3 buckets where versioning is off or suspended. Versioning keeps old copies of objects, so an overwrite or a delete can be undone, which is why Day 13's bucket has it on.
- EC2 instances that still exist and have no `owner` tag (a label you attach), so nobody knows whom to ask before stopping them. Stopped instances count, because their disks still cost money.

A bucket the script may not read becomes a finding, `cannot read versioning (AccessDenied)`, instead of a crash. A report that dies on bucket 3 of 200 tells you nothing about the other 197.

Both tools work today. How do we know they still work next month, without phoning the real services every time?"""))

S.append(("Rehearsing with pytest", r"""A script that runs at 3 a.m. deserves tests as much as the app it watches. A test is a small piece of code that runs your code and checks the result. The pytest runner finds files named `test_*.py` and runs every function named `test_*`. An `assert` line states what must be true, and when one fails, pytest shows the values on both sides. In the lab, `uv run pytest` runs 30 tests in about 8 seconds, offline.

The `main(argv) -> int` shape from Day 15 is what makes this easy: call `main(["access", str(path)])` and assert on the number it returns. A fixture is something pytest prepares for a test that names it as an argument. Three built-in fixtures do most of the rest:

- `tmp_path` is a fresh empty folder for this one test. Write a three-line log into it, with one broken line, instead of depending on real files.
- `monkeypatch` changes things for one test only. `monkeypatch.setenv("LOGSUM_MAX_ERROR_RATE", "50")` and `monkeypatch.delenv("GITHUB_TOKEN")` are undone when the test ends, so no test leaks settings into the next.
- `capsys` captures what the code printed. `out, err = capsys.readouterr()` lets you check that the report went to stdout and the reason went to stderr.

You can write your own fixtures with `@pytest.fixture`, and code after a `yield` inside one runs as cleanup. The file `test_healthcheck.py` uses that to start a real web server on 127.0.0.1, your own machine, for each test. The server shuts down afterwards, so the 503 (service unavailable) and timeout cases are real without leaving the laptop.

What deserves a test in an ops script? The exit codes, the parsing of realistic input including one malformed line, and every error message a tired person will read. Leave argparse and requests alone; their own authors test them.

A web server on your laptop is easy to start. GitHub and AWS are not, so for those we need stand-ins."""))

S.append(("A friend plays the supplier: responses and moto", r"""You can't ask the real supplier to be busy on Tuesday at ten so the helper can practise. A friend can play the supplier on the phone, though, and say whatever you wrote down. Tests that call the real GitHub or AWS are slow and flaky (they fail now and then for reasons outside your code), and they need secrets in CI. So replace the service with a stand-in, a mock, and keep your code as it is.

`responses` steps in where requests hands data to the network, so registered URLs get prepared answers. Inside a test marked `@responses.activate`, `responses.get(url, json={...}, status=200)` registers one answer. A request to any URL you did not register raises `ConnectionError`, so a test cannot reach the internet by accident. Matchers are small checks on what you sent, such as the `Authorization` header. `registries.OrderedRegistry` hands out answers in order, a 502 and then a 200, which proves the retry works. Pass `backoff=0` in that test so it does not sleep.

Moto does the same for AWS. Inside `with mock_aws():`, moto catches each boto3 request just before it would be sent and answers it from a fake AWS that lives only in memory. That fake starts empty for each test. The test creates the buckets and instances it needs, then calls the real function. Two rules from the moto docs:

1. Set fake credentials first, `AWS_ACCESS_KEY_ID=testing` and the rest, with `monkeypatch.setenv`. If your shell holds real keys, this makes sure they are never used.
2. Start the mock before you create any client. A client made earlier, for example when the file is first imported, is not mocked.

Moto is a model of AWS, not AWS. It does not check IAM permissions (AWS's rules for who may do what) unless you ask it to, so a test passes even when the real role would be denied. Run a new check once against a real account before you trust it.

**A fake proves your logic, not your permissions. Try the real thing once.**

The same moto also runs as a server (`moto_server -p 5050`) that boto3 reaches through `AWS_ENDPOINT_URL`, the same idea as `--endpoint-url` on Day 13.

The tools are tested. The last step is handing them to your teammates."""))

S.append(("Ship it: a real command, a code checker and CI", r"""A folder of scripts becomes a tool when teammates can install it and type its name. `pyproject.toml` lists commands under `[project.scripts]`. The line `gh-runs = "python_ops.gh_runs:main"` means: make a command named `gh-runs` that calls `main` in that module. When uv installs the project, with `uv sync` or `uv tool install`, it writes a tiny `gh-runs` launcher into that environment's `bin` folder. The launcher imports the module and runs `sys.exit(main())`, so your exit codes reach the shell. Three ways to use the commands:

- `uv run gh-runs ...` inside the project folder.
- `uv tool install --editable .` installs the project into one environment of its own and links both commands into `~/.local/bin` (`uv tool update-shell` puts that folder on your PATH). With `--editable`, your code changes apply without reinstalling.
- `uv tool install git+https://github.com/YOU/python-ops` installs them for a teammate straight from git.

ruff lints and formats in one fast tool. Linting means reading code for likely bugs without running it: `uv run ruff check` does that, and `uv run ruff format` fixes the layout. The lab turns on a few rule groups that suit ops code, each explained in `pyproject.toml`. Three of them catch this part's own lessons:

- `S113` flags `requests.get(url)` without a timeout. It does not see calls on a `Session`, so the habit still matters.
- `S602` flags `shell=True`, and `PLW1510` flags `subprocess.run` without `check=`.
- `DTZ` flags naive datetimes such as `datetime.now()`.

Last comes CI. The lab's `ci.yml` installs uv with `astral-sh/setup-uv`, runs `uv sync --locked`, then ruff and pytest. `--locked` fails the job when `uv.lock` no longer matches `pyproject.toml`. Each step fails the job through its exit code, just like the scripts themselves. Day 25 builds a full pipeline.

These tools have one limit left: each machine that runs them needs Python and the right packages first. Part 5 packs an app and everything it needs into one box that runs the same everywhere."""))
new["sections"] = S

new["aside"] = {
    "title": "Why 3.05 seconds, and not just 3?",
    "body": r"""The requests docs suggest a connect timeout just above a multiple of 3. They call 3 seconds the default TCP retransmission window: the wait before an unanswered packet (a small piece of a message) is sent again. A value a little above 3 leaves room for that second try to get through. The read timeout, the 10, has no such rule; pick what your slowest honest answer needs.""",
    "after": 0,
}

new["drop"] = ["analogy", "mistake"]

new["real_world"] = r"""Untagged instances are the ones nobody dares to stop, and buckets without versioning are the ones nobody can restore. So platform teams often run a read-only report like `aws-report` on a schedule in every account. It uses a role that can only list and describe, and it posts the findings to the owning team's chat channel. The report has moto tests in CI, so a change to it cannot break the Monday run."""

new["diagram_caption"] = "The same code talks to the real service in a normal run and to a stand-in under pytest."

new["worked"] = [
    r"""Look at the raw answer before you write code. The tool curl sends web requests from the terminal; here it asks for two runs, and jq picks a few fields out of the JSON. The answer has a total and a list of runs, and the `Link` header holds the next page. Public repos need no token; your numbers will differ.""",
    r"""Now the tool. Borrow the gh CLI's token through an environment variable and ask for five runs. Every run passed, so the exit code is 0.""",
    r"""`-v` turns on DEBUG logging, and urllib3 then logs every HTTP request it sends. It is the quickest way to see the query string, the pages and any retries.""",
    r"""Ask for more runs and the old failures appear. The table stays on stdout and the links to the failed runs go to stderr. The exit code turns 1, which is what a scheduled CI job would act on. (Output trimmed.)""",
    r"""A wrong token, a used-up rate limit or a 502 are hard to cause on purpose, so the tests cause them with `responses`. All eight run in a tenth of a second, with no network.""",
    r"""Let ruff catch the classic slip. In a scratch file, a bare `requests.get` without a timeout is flagged as S113. Then install the commands for everyday use; `--editable` keeps them pointing at your folder. (Output trimmed.)""",
]

new["task"] = {
    "steps": [
        r"""In terminal 1, start a fake AWS: `uvx --from "moto[server]" moto_server -p 5050`.""",
        r"""In terminal 2, in `~/code/python-ops`, export `AWS_ENDPOINT_URL=http://localhost:5050`, `AWS_ACCESS_KEY_ID=testing`, `AWS_SECRET_ACCESS_KEY=testing` and `AWS_DEFAULT_REGION=eu-central-1`. Then run `uv run scripts/seed_moto.py` and `uv run aws-report`.""",
        r"""A security group is a list of rules for which traffic may reach a server. In moto, create one that allows port 22 (SSH, remote login) from `0.0.0.0/0`, meaning any address. Use the AWS CLI from Day 13: `aws ec2 create-security-group` and `aws ec2 authorize-security-group-ingress`, with the same endpoint.""",
        r"""Add a function `ssh_open_to_world(ec2)` to `aws_report.py`. It goes through every security group with a paginator and reports groups whose rules allow port 22 from `0.0.0.0/0` or `::/0` (any address, in the newer IPv6 format).""",
        r"""Call it from `main`, print the findings in text and JSON, and include them in the exit code.""",
        r"""Write a moto test with three groups: SSH from `0.0.0.0/0`, SSH from `10.0.0.0/8` and HTTPS from `0.0.0.0/0`. Only the first may be reported.""",
        r"""Run `uv run pytest` and `uv run ruff check`, and fix anything they report.""",
        r"""Run `uv run aws-report` against the moto server again and check that your group appears and the exit code is 1.""",
        r"""Optional, with a real account: run `aws login --profile learn`, then `uv run aws-report --profile learn`. It only reads, so it costs nothing.""",
    ],
    "hints": [
        r"""`describe_security_groups` has a paginator. Each group has `IpPermissions`, and each permission has `FromPort`, `ToPort`, `IpRanges` and `Ipv6Ranges`.""",
        r"""An `IpProtocol` of `"-1"` means all traffic, and then there is no `FromPort`, so read the ports with `.get()`.""",
        r"""moto creates a `default` group in every VPC; your function must not report it.""",
    ],
    "done_when": r"""You are done when `uv run pytest` passes with your new test, and `aws-report` against the seeded moto server lists your open SSH group and exits 1.""",
}

new["explain_back"] = {
    "prompt": r"""Explain in 3 to 4 sentences how you make a script that calls an API safe to run in CI, and how you test it without the network. Mention timeouts, retries and mocks.""",
    "answer": r"""Every call gets a timeout, so a silent server cannot hang the job. Retries go only to errors that may pass, such as 429 and 5xx, only for idempotent methods, with growing waits, and never for 401 or 404. Errors become one clear line on stderr and a non-zero exit code, and the token comes from an environment variable. In tests, responses answers in place of the HTTP API and moto in place of AWS, so pytest can check retries, failures and exit codes offline.""",
}

new["recap"] = [
    "Use requests for scripts, and always pass a timeout and call raise_for_status().",
    "Retry 429 and 5xx with backoff on idempotent methods only; never retry 401 or 404.",
    "Follow the Link header or a boto3 paginator, or you only see the first page.",
    "A boto3 session holds one profile and region; catch ClientError and BotoCoreError separately.",
    "Test with tmp_path, monkeypatch and capsys, and fake HTTP with responses and AWS with moto.",
    "The limit: moto skips IAM checks by default, so run a new check once against a real account.",
]

new["check"] = [
    (r"""A cleanup script lists objects with `s3.list_objects_v2(Bucket=b)` and deletes the old ones. The bucket holds 4,000 objects. What happens?""",
     r"""A single call returns at most 1,000 keys; use `get_paginator("list_objects_v2")` to get every page."""),
    (r"""A script sends `POST /deployments` through a session whose urllib3 `Retry` lists 502 in `status_forcelist` but keeps the default allowed methods. The API answers 502. What happens?""",
     r"""urllib3 retries only idempotent methods by default, because repeating a POST could create two deployments."""),
    (r"""A test marked `@responses.activate` registers only `/actions/runs`, but the code also calls `/rate_limit`. What happens in the test?""",
     r"""responses refuses every URL you did not register, so a test can never reach the network by accident."""),
]

new["interview"] = [
    (r"""How do you make HTTP calls from a script reliable?""",
     r"""Every call has a timeout, because requests waits forever by default. I use a Session so headers and connections are reused, and I mount a retry policy that retries 429 and 5xx answers with exponential backoff and honours Retry-After. Only idempotent methods are retried, and 401 or 404 never are. After the call I check the status with raise_for_status, and I turn errors into a clear message and a non-zero exit code."""),
    (r"""How do you test code that calls AWS?""",
     r"""For unit tests I use moto's mock_aws, which fakes AWS in memory. I set fake credentials first, so real ones can never be used. Each test creates the resources it needs and then calls the real function, with every client created after the mock starts. Moto does not check IAM by default, so I also run new checks once against a sandbox account with a least-privilege role. For error paths that are hard to fake, I raise a ClientError myself with monkeypatch or use botocore's Stubber."""),
    (r"""What are boto3 paginators and waiters for?""",
     r"""Many AWS list calls return one page of results plus a token, so code that makes one call silently misses data. A paginator follows the tokens for you, and its search method can pull items out of every page with JMESPath. A waiter polls a describe call until a resource reaches a state, such as an instance running. It waits a fixed delay between tries and gives up after a maximum number of attempts. Both replace hand-written loops that are easy to get wrong."""),
]

new["deeper"] = r"""Kubernetes has an official Python client too, the `kubernetes` package. Part 10 teaches clusters with kubectl; this is what the same questions look like from Python, once you have a cluster.

The client reads the same kubeconfig as kubectl:

1. `config.load_kube_config()` loads `~/.kube/config` and its current context, exactly like kubectl on your laptop.
2. `v1 = client.CoreV1Api()` gives an API object for the core resources: pods, services, namespaces.
3. `v1.list_pod_for_all_namespaces(watch=False)` returns objects with attributes, so `pod.metadata.name` and `pod.status.phase` work without any JSON parsing.

Inside a pod, use `config.load_incluster_config()` instead. It reads the token and the CA certificate that Kubernetes mounts for the pod's service account, so no kubeconfig file is needed. What the script may do is then decided by RBAC rules for that service account (Day 64). A read-only report needs only `get` and `list` on the resources it reads.

A report in the style of today's tools would list pods that are not Ready: for each pod, look at `pod.status.conditions` for the condition of type `Ready` with status `False`. Then print a table, return 1 when the list is not empty, and test it with a fake object instead of a cluster. Because the client returns objects, a test can build a few with `client.V1Pod(...)` and pass them to your function, with no network at all.

The client also supports watching. `watch.Watch().stream(v1.list_namespace, _request_timeout=60)` yields an event every time a namespace is added, changed or deleted. Set a timeout here too, for the same reason as with requests.

When should you use the client rather than `subprocess.run(["kubectl", "get", "pods", "-o", "json"], ...)` plus `json.loads`? The kubectl route is fine for a quick script on your laptop, and its output matches what you see in the terminal. The client wins for anything that runs inside the cluster, needs watches, or should not depend on a kubectl binary being installed. Its major version follows Kubernetes releases, and its README has a compatibility table, so pick the version that matches your cluster, as you did with kubectl itself. Start from the examples in the [Kubernetes Python client README](https://github.com/kubernetes-client/python); they run against the kind cluster you build in Part 10.

Four smaller notes on today's tools:

- Why not httpx? It has almost the same API as requests, plus async code and HTTP/2. But the httpx project has had no stable release since 0.28.1 in December 2024. Its 1.0 has been out only as development releases that change the API, and Pydantic now maintains a fork named httpx2 that keeps the old one. Until that split settles, a script that runs from cron for three years is better off on requests. Reach for httpx2 when you really need async or HTTP/2.
- Without the `X-GitHub-Api-Version` header, GitHub picks a version for you; it answered with `2022-11-28` when we left it out.
- Use boto3 clients, not the older `boto3.resource` interface, which the boto3 docs say will get no new features.
- Since uv 0.12, `uv init` creates a packaged project like the lab's by default, with the code under `src/` and uv's own build backend."""

new["closing"] = r"""We started with a helper holding a silent phone until noon. Our tools can't do that any more. Every call has a timeout, a busy line gets a polite call back, a "no" is taken as final, and long lists are read to the last page. The tests rehearse it all with stand-ins, offline. In your own scripts, or in the lab's `src/` folder, search for `requests.get(` and check that each one has a `timeout=`. Then look for an AWS list call without a paginator.

Next, we'll leave Python and pack an app into a container. It answers an old question: why does an app that works on your laptop fail on someone else's?"""

apply(L, new)
save(path, P, L, OL)
