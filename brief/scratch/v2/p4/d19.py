"""Day 19: A real CI pipeline: test, lint, cache, matrix (first edition d11)."""
from common import T, box, cap, line, link, refs, scratch, sources, svg

DIAGRAM = svg(216, "A pull request starts a lint job and two test jobs, one per Python version; the build job needs all three; the merge is allowed only when every check is green", [
    box(8, 88, 128, 44, "bxo", "Pull request"),
    line(136, 110, 172, 42),
    line(136, 110, 172, 110),
    line(136, 110, 172, 178),
    box(176, 20, 112, 44, "bxt", "lint"),
    box(176, 88, 112, 44, "bxt", "test 3.13"),
    box(176, 156, 112, 44, "bxt", "test 3.14"),
    line(288, 42, 324, 102),
    line(288, 110, 324, 110),
    line(288, 178, 324, 118),
    box(328, 88, 88, 44, "bxt", "build"),
    cap(372, 152, "needs all three"),
    line(416, 110, 444, 110),
    box(448, 88, 104, 44, "bxg", "Can merge"),
    cap(500, 152, "all checks green"),
    cap(372, 34, "run in parallel"),
])

S1 = T("""
Today you grow the Day 18 `ci.yml` into a real pipeline. Right now it runs the tests once. A real pipeline checks more, and it has to be quick, because people wait for it before they merge. So cheap checks go first and slow ones last.

The lab's pipeline has three jobs:

1. `lint`: ruff checks style and likely bugs. It takes seconds.
2. `test`: pytest, once for each Python version you support.
3. `build`: builds the Docker image. It is the slowest, so it waits for the other two.

Jobs run in parallel by default, so `lint` and both `test` jobs start at the same moment on separate runners. The `needs` key makes a job wait: with `needs: [lint, test]`, `build` starts only after all of them succeed. If one fails, `build` is skipped, and you get the bad news without paying for the slow part.

The triggers change too. CI now runs on pull requests, which test the merged result, and on pushes to `main`. It no longer runs on pushes to every branch, because then each commit on a PR branch would be tested twice. One more line, `permissions: contents: read`, makes the job's token read-only. Day 21 explains why that matters.
""")

S2 = T("""
A linter reads your code without running it and flags problems such as unused imports or undefined names. This course uses ruff, which does both linting and formatting:

- `ruff check .` finds lint problems, and `ruff check --fix .` fixes the safe ones.
- `ruff format --check .` fails if a file is not formatted, and `ruff format .` formats it.

Both exit with code 1 when they find a problem, so they fail the step the same way `pytest` does.

Next comes a test report. `pytest --junitxml=reports/junit.xml` also writes the results as JUnit XML, a format most CI tools can read. The runner is deleted after the job, so you keep the report as an artifact: a file a job uploads and you download later, from the run page or with `gh run download`. Artifacts stay 90 days by default. The lab keeps test reports for 7.

Since version 4, `actions/upload-artifact` has two rules worth knowing. An artifact cannot be changed after upload, and names must be unique within a run. Two matrix jobs that both upload `junit` would clash, so the lab puts the Python version in the name. The upload step also has `if: ${{ !cancelled() }}`. Normally GitHub skips every step after one fails; this condition still uploads the report after a test failure, which is when you need it most. Day 20 explains these conditions properly.
""")

S3 = T("""
Every job starts on an empty machine, so `pip install` downloads every package again on every run. A cache saves files from one run and restores them in the next. Each entry is stored under a cache key: a string that describes what is inside, so a job can tell whether the saved files still fit.

`actions/setup-python` has pip caching built in: set `cache: pip`. The key it builds is made of the runner's OS and CPU, the Python version and a hash of your requirements files. It looks roughly like `setup-python-Linux-x64-24.04-Ubuntu-python-3.14.<patch>-pip-<hash>`. `cache-dependency-path: requirements*.txt` says which files to hash, so changing either file gives a new key.

When the job starts, one of three things happens:

- Exact hit: a cache with the same key exists. The log says "Cache restored from key".
- Partial hit: no exact match, but a key with the same start (same OS and Python, older hash). Those older files are restored, and pip downloads only what changed.
- Miss: the log says "pip cache is not found", and pip downloads everything.

A job that missed saves a new entry when it finishes. Scope matters here. A run can restore caches from its own branch and from `main`, but a cache saved by a pull request stays with that pull request. That is one reason CI also runs on pushes to `main`: it keeps a fresh cache that every new PR starts from. GitHub deletes caches nobody used for 7 days and keeps at most 10 GB per repository. Treat the cache as a speed-up that can vanish, and never put secrets in a cached folder.
""")

S4 = T("""
A matrix runs one job definition several times with different values. Your app should work on Python 3.13 and 3.14, so:

- `strategy: matrix: python-version: ["3.13", "3.14"]` creates two jobs from one definition.
- `${{ matrix.python-version }}` passes each value to setup-python and into the artifact name.
- `fail-fast: false` lets both finish even if one fails. The default cancels the others at the first failure, which hides whether a bug only affects one version.

The two jobs run at the same time, so the matrix adds almost no waiting. They show up as two checks, `test (3.13)` and `test (3.14)`. Remember those exact names, because the ruleset needs them later today.

A matrix can have several dimensions. Add `os: [ubuntu-latest, ubuntu-24.04-arm]` next to the Python list and you get four jobs, one per combination. `include` adds one extra combination and `exclude` removes one. A single matrix can create at most 256 jobs. For hello-devops, two is right: every extra job costs runner time and adds one more check to keep green.
""")

S5 = T("""
Your Dockerfile is code too, and it can break. A wrong `COPY` path, or a package that no longer installs, only shows up when you build. So CI builds the image for every change, without pushing it anywhere.

The `build` job uses Docker's own actions:

- `docker/setup-buildx-action` starts a BuildKit builder, the build engine from Part 3.
- `docker/build-push-action` builds the image; with `push: false` it only builds.
- `cache-from: type=gha` and `cache-to: type=gha,mode=max` keep image layers in the Actions cache.

The layer cache works like the one on your laptop from Day 13. If `requirements.txt` did not change, the `pip install` layer comes back from the cache and the build takes seconds. `mode=max` also saves the layers of the build stage of your multi-stage Dockerfile, not only the final image.

Since June 2026, runs started by untrusted triggers, such as `pull_request_target` and `issue_comment`, may read the default branch's cache but not write to it. Docker's docs say to keep `cache-from` and drop `cache-to` in such workflows. Your `pull_request` workflow is not affected, because its cache never reaches `main` anyway. On Day 21, a second workflow uses the same actions with `push: true`.
""")

S6 = T("""
CI only protects you if a red result stops the merge. On GitHub you get that with a **ruleset** on `main`: a named list of rules for branches or tags. The older feature, branch protection rules, still works. Rulesets are more flexible, since several can apply at once, and anyone with read access can see them.

For `main`, start with these rules:

- Require a pull request before merging, so nobody pushes to `main` directly.
- Require status checks to pass: `lint`, `test (3.13)`, `test (3.14)` and `build`.
- Block force pushes, which is on by default.

Most people get caught by at least one of these details:

- On the Free plan, rulesets are only enforced on public repositories.
- A new ruleset starts as Disabled. Set its enforcement status to Active.
- A check only shows up in the ruleset's search after it ran in the repository during the last seven days.
- A job skipped because its `needs` failed counts as passed. That is why you require the lint and test checks too, and not only `build`.

You work alone, so leave required approvals at zero. GitHub does not let you approve your own pull request.
""")

S7 = T("""
Slow CI changes how people work. They stop waiting for it, or they bundle many changes into one big PR. These settings keep it quick:

- `concurrency` with `cancel-in-progress` cancels a stale run when you push again to the same branch or PR.
- `timeout-minutes` stops a hung job early, instead of after the default 360 minutes.
- `paths-ignore` on `push` skips runs when a push only changes Markdown files.
- The pip and Docker layer caches keep installs and builds short.

On `main` the lab lets every run finish, so each merge gets a full result. And never put path filters on `pull_request` when its checks are required. A workflow skipped by a filter never reports, so its checks stay Pending and block the merge.

For deploys, cancelling is the wrong move. By default a concurrency group holds one running and one waiting run, and a newer waiting run replaces the older one. `queue: max` lets up to 100 runs wait in line instead. The Terraform workflow on Day 29 uses a group that never cancels.

Two tools help before you push. {actionlint} checks workflow files for mistakes such as typos in keys, bad expressions and unsafe use of untrusted input. {act} runs workflows on your laptop in Docker containers. It is handy for quick tries, but it does not match GitHub's runners exactly, so the real test is still a push.
""").format(actionlint=link("actionlint", "actionlint"), act=link("act", "act"))

LESSON = {
    "id": "d19",
    "title": "A real CI pipeline: test, lint, cache, matrix",
    "minutes": 50,
    "goal": "By the end you can build a CI pipeline that lints, tests on two Python versions, keeps a test report and checks the Docker build, runs fast with caches, and blocks red pull requests from merging.",
    "guess": {
        "q": "Your CI has lint, test and build jobs, and build has `needs: [lint, test]`. A ruleset requires only the build check. A test fails on a pull request. What happens?",
        "options": [
            "The merge is blocked, because build never ran",
            "GitHub reruns the tests until they pass",
            "It can merge, because a skipped build counts as passed",
            "Build runs anyway, because test is not required",
        ],
        "answer": 2,
        "why": "GitHub treats a check that was skipped because its needs failed as passed, so the merge goes through. Require the lint and test checks as well.",
    },
    "terms": [
        {"term": "Lint", "plain": "An automatic check for style problems and likely bugs that reads code without running it."},
        {"term": "Matrix", "plain": "One job definition that GitHub expands into several jobs, one per value, such as Python versions."},
        {"term": "Cache", "plain": "Files saved by an earlier run, such as downloaded packages, and restored to save time."},
        {"term": "Cache key", "plain": "The name a cache entry is stored under, built from things like the OS and a hash of lockfiles."},
        {"term": "Artifact", "plain": "A file a job uploads, such as a test report, that you can download after the run."},
        {"term": "Required status check", "plain": "A check that must pass on a pull request before GitHub allows the merge."},
        {"term": "Ruleset", "plain": "A named set of rules for branches or tags, such as 'main needs passing checks'."},
        {"term": "Concurrency group", "plain": "A name that lets only one run per group go ahead, cancelling or queueing the others."},
    ],
    "sections": [
        {"h": "What a good pipeline does, and in what order", "body": S1, "refs": refs("use_jobs", "python")},
        {"h": "Lint, tests and a test report", "body": S2, "refs": refs("artifacts", "upload_artifact")},
        {"h": "Caching, and how cache keys work", "body": S3, "refs": refs("caching_ref", "setup_python", "caching")},
        {"h": "A matrix: one job, many versions", "body": S4, "refs": refs("matrix", "v_kk2")},
        {"h": "Check that the image builds", "body": S5, "refs": refs("build_push", "docker_gha_cache")},
        {"h": "Stop broken code from merging", "body": S6, "refs": refs("rulesets", "rulesets_create", "req_checks")},
        {"h": "Keep CI fast and cheap", "body": S7, "refs": refs("concurrency", "actionlint", "act")},
    ],
    "analogy": "CI is like the final inspection line in a car factory. Quick checks such as the lights and the horn come first, and only cars that pass them get the slow road test. The matrix is the same road test on two kinds of road at once. The ruleset is the guard at the gate who lets no car out without a fully signed sheet. One difference: CI inspects a car that does not exist yet, the merged result of your branch and main.",
    "diagram": DIAGRAM,
    "diagram_caption": "Lint and the tests run in parallel, the build waits for all of them, and the ruleset allows the merge only when every check is green.",
    "worked": {
        "title": "A red lint check, fixed in two minutes",
        "steps": [
            {
                "say": "A teammate's PR adds `import json` to `app.py` but never uses it. The `lint` check turns red, both test checks pass, and `build` is skipped. You read the failure from the terminal.",
                "code": T("""
                    $ gh pr checks
                    $ gh run view --log-failed
                """),
                "lang": "console",
            },
            {
                "say": "The log ends with ruff's report, followed by a suggested fix and `Found 1 error.`. F401 is the rule for unused imports, and `[*]` means ruff can fix it. The step failed because ruff exited with code 1.",
                "code": T('''
                    F401 [*] `json` imported but unused
                     --> app.py:3:8
                      |
                    1 | """hello-devops: the tiny web app you ship all through the course."""
                    2 |
                    3 | import json
                      |        ^^^^
                    4 | import os
                    5 | import socket
                      |
                    help: Remove unused import: `json`
                '''),
                "lang": "console",
            },
            {
                "say": "Check out the PR branch and run the same command on your laptop. The concise format gives one line per problem. You get the same answer in a second, without waiting for CI.",
                "code": T("""
                    $ gh pr checkout 7
                    $ ruff check . --output-format concise
                    app.py:3:8: F401 [*] `json` imported but unused
                    Found 1 error.
                    [*] 1 fixable with `--fix`.
                """),
                "lang": "console",
            },
            {
                "say": "Let ruff fix it, then run everything CI runs, in the same order. All three commands now exit with 0.",
                "code": T("""
                    $ ruff check --fix .
                    Found 1 error (1 fixed, 0 remaining).
                    $ ruff format --check .
                    2 files already formatted
                    $ pytest -q
                    ...                                                                      [100%]
                    3 passed in 0.30s
                """),
                "lang": "console",
            },
            {
                "say": "Commit and push to the same branch, which starts a new run. If the old run were still going, concurrency would cancel it. Once all four checks are green, the ruleset lets you merge.",
                "code": T("""
                    $ git commit -am "Remove unused import"
                    $ git push
                    $ gh pr checks --watch
                """),
                "lang": "console",
            },
        ],
    },
    "code": [
        {
            "lang": "yaml",
            "title": ".github/workflows/ci.yml (Day 19 version)",
            "src": scratch("ci-day19.yml"),
            "run": "ruff check . && ruff format --check . && pytest -q && git push && gh pr checks --watch",
        },
    ],
    "commands": [
        {"cmd": "ruff check .", "what": "Lint every Python file; exits with 1 if it finds a problem."},
        {"cmd": "ruff check --fix .", "what": "Fix the lint problems that are safe to fix automatically."},
        {"cmd": "ruff format .", "what": "Format all Python files in place."},
        {"cmd": "pytest -q --junitxml=reports/junit.xml", "what": "Run the tests and also write a JUnit XML report."},
        {"cmd": "gh pr checks --watch", "what": "Watch the checks of the current branch's PR until they finish."},
        {"cmd": "gh run download --name junit-py3.14", "what": "Download one artifact from a run; gh asks which run."},
        {"cmd": "gh cache list", "what": "List the Actions caches of this repository, with key, size and last use."},
        {"cmd": "gh cache delete --all", "what": "Delete every cache, for example to test a cold start."},
        {"cmd": "gh repo view --json visibility", "what": "Show whether your repository is public or private."},
        {"cmd": "brew install actionlint && actionlint", "what": "Install the workflow linter, then check every file in .github/workflows."},
        {"cmd": "brew install act", "what": "Install act, which runs workflows locally in Docker containers."},
        {"cmd": "act -l -W .github/workflows/ci.yml", "what": "List the jobs of one workflow and the stage each runs in, without running anything."},
    ],
    "mistake": "A path filter on the `pull_request` trigger looks like an easy way to save minutes. Then a PR that only touches docs never runs CI, its required checks wait as Pending forever, and the merge stays blocked. Filter only `push`, as the lab does, or skip the expensive work inside the job instead.",
    "real_world": "The checkout service at PayLoop has a ruleset on main that requires one review and green checks for lint, tests and the image build. The team treats ten minutes as the limit for CI. When a run creeps above that, someone adds caching or splits slow tests. Nobody is on the bypass list for main, not even admins.",
    "task": {
        "title": "Build the full pipeline and protect main",
        "steps": [
            "Check that your repository is public with `gh repo view --json visibility`. On the Free plan, rulesets only work on public repos.",
            "On a branch `ci-pipeline`, grow `ci.yml` into the Day 19 version in the Files section one piece at a time: triggers, concurrency, permissions, lint job, matrix, cache, report, build.",
            "Before you push, run `actionlint`, `ruff check .`, `ruff format --check .` and `pytest -q` on your laptop.",
            "Push, open a PR, and watch it with `gh pr checks --watch`. Expect four checks: `lint`, `test (3.13)`, `test (3.14)` and `build`.",
            "Open the log of one test job and find the setup-python step. Does it say \"pip cache is not found\" or \"Cache restored from key\"? Push an empty commit (`git commit --allow-empty -m retry`) and compare.",
            "Download one JUnit report with `gh run download` and open the XML file.",
            "Merge the PR. Then, in Settings, open Rulesets and create a branch ruleset for `main`: require a pull request and the four status checks, and set enforcement to Active.",
            "Prove it works. On a new branch, break a test, open a PR, and confirm that GitHub blocks the merge. Then fix the test and merge.",
        ],
        "hints": [
            "A check name only shows up in the ruleset search after it has run in the repository recently, so let the pipeline run first.",
            "In the ruleset, the default branch is the easiest target to add.",
            "If `build` fails while tests pass, run `docker build .` locally to see the same error.",
        ],
        "done_when": "A PR with a failing test shows the merge as blocked, and the fixed PR merges with four green checks.",
    },
    "explain_back": {
        "prompt": "Explain how your CI pipeline keeps broken code out of main, in 3 to 4 sentences. Mention needs, the matrix and the ruleset.",
        "answer": "Every pull request starts the ci workflow. Lint and the tests run first, the tests once per Python version through the matrix, and the build job waits for all of them with needs. A ruleset on main requires a pull request plus all four checks, so the merge stays blocked until they are green. I list the lint and test checks by name because a build skipped after a failure would otherwise count as passed.",
    },
    "recap": [
        "Order checks from cheap to slow: lint and tests in parallel, then the Docker build with needs.",
        "cache: pip keys the cache on OS, Python version and a hash of the requirements files; the gha cache does the same for image layers.",
        "A matrix runs one job per Python version, and each one becomes its own check.",
        "Artifact names must be unique per run; upload test reports with if: ${{ !cancelled() }}.",
        "A ruleset on main with all required checks blocks red pull requests; set it to Active.",
        "concurrency, timeout-minutes and a push-only paths-ignore keep CI quick and cheap.",
    ],
    "check": [
        {
            "q": "Next year you add Python 3.15 to the matrix. What else must change so the new version protects main?",
            "options": [
                "Nothing, rulesets pick up new checks on their own",
                "Add test (3.15) to the ruleset's required checks",
                "Rename the job to test-3.15",
                "Turn fail-fast back on",
            ],
            "answer": 1,
            "why": "Required checks are matched by exact name, so a new matrix check is not required until you add it.",
        },
        {
            "q": "A PR only changes README.md. The pull_request trigger has a paths-ignore filter for Markdown, and the checks are required. What happens?",
            "options": [
                "The PR merges at once, because nothing ran",
                "CI runs anyway, because filters never apply to PRs",
                "The required checks wait as Pending, and the merge stays blocked",
                "GitHub marks the checks as skipped and passed",
            ],
            "answer": 2,
            "why": "A workflow skipped by a path filter never reports, so its required checks stay Pending.",
        },
        {
            "q": "You bump flask in requirements.txt. On the next PR run, what does the setup-python pip cache do?",
            "options": [
                "Finds no exact key, restores the older pip cache by prefix, and pip downloads only what changed",
                "Fails the job, because the cache no longer matches",
                "Restores the exact old cache, so the new flask is never installed",
                "Skips caching for the rest of the week",
            ],
            "answer": 0,
            "why": "The hash of the requirements files changed, so the exact key misses. The restore key with the same OS and Python matches, and pip fetches only the new package.",
        },
    ],
    "interview": [
        {
            "q": "How would you speed up a slow CI pipeline?",
            "a": "First I measure where the time goes, using the job and step timings on the run page. Then I cache what does not change, such as package downloads and Docker layers. I run independent jobs in parallel, put cheap checks such as lint first, and cancel stale runs with concurrency. If tests are the slow part, I split them across parallel jobs and move slow end-to-end tests to a later stage.",
        },
        {
            "q": "What are required status checks, and what can go wrong with them?",
            "a": "They are checks named in a ruleset or branch protection rule that must pass before a pull request can merge. GitHub matches them by exact name, so renaming a job or changing a matrix can drop protection until you update the list. A workflow skipped by a path or branch filter leaves its checks Pending and blocks the merge. And a job skipped because its dependency failed counts as success, so you must also require the earlier jobs.",
        },
        {
            "q": "What is the difference between a cache and an artifact in GitHub Actions?",
            "a": "A cache is a speed-up for future runs, such as downloaded packages, stored under a key and restored when the key matches. It is best effort: GitHub evicts entries unused for 7 days. An artifact is an output of one run, such as a test report or a build, that people or later jobs download. Since upload-artifact v4, artifacts cannot be changed after upload and need unique names per run.",
        },
    ],
    "deeper": {
        "minutes": 12,
        "body": T("""
            Listing every matrix check in the ruleset works, but it can break quietly. Add Python 3.15 next year and forget the ruleset, and the new check is not required. Rename a job, and the old required name never reports again, so every PR waits forever.

            Many teams fix this with one gate job at the end of the workflow, and they require only that job. The gate has:

            - `needs: [lint, test, build]`, so it waits for every other job.
            - `if: ${{ always() }}`, so it runs even when a needed job failed or was skipped.
            - One step that runs `exit 1` when `contains(needs.*.result, 'failure')` or `contains(needs.*.result, 'cancelled')` is true.

            `needs.*.result` is a list with the result of each needed job: `success`, `failure`, `cancelled` or `skipped`. The gate turns that list into one answer. Using `always()` is safe here, because the gate only reads results and runs nothing risky. Day 20 explains `always()` and the `needs` context in detail.

            Why not a gate with plain `needs` and no `if`? A failed test would then skip the gate, and a skipped gate counts as passed. It is the same trap as before, one level further down. With `always()`, the gate runs every time and reports what really happened.

            For a small repository with four checks, a gate is overkill and listing the checks is clearer, so the lab does that. Reach for a gate when your matrix grows or when some jobs only run sometimes.

            Caches deserve one more look, because they are shared between runs. Anything a job writes into a cached folder, a later run restores and may execute. That is why GitHub limits who can write caches for the default branch, and why the docs tell you never to cache secrets. Since 2026 you can also set a `cache-mode` key on a job (`read`, `write`, `write-only` or `none`) to give it only the cache access it needs, for example `read` for a job that handles untrusted input. See the {ref}.

            Read more about required checks in {checks}.
        """).format(ref=link("caching_ref", "dependency caching reference"), checks=link("req_checks", "Troubleshooting required status checks")),
    },
    "sources": sources("python", "caching_ref", "rulesets", "req_checks"),
}
