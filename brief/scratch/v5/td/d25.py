"""Book-voice rewrite of d25 (fifth pass, writer td). Replaces prose fields only."""
from common import load, save, set_list, drop_extras

path, P, L = load(6, "d25")

L["goal"] = ("By the end you can build a CI pipeline that lints, tests on two Python versions, keeps a test report and checks "
             "the Docker build, runs fast with caches, and blocks red pull requests from merging.")

L["opening"] = """Picture our kitchen on its first Saturday with a real taster at the pass. The taster is careful, and that is the problem: plates pile up while every dish waits its turn. Each morning the stock is boiled again from bones, because the fridge is emptied every night. Then a waiter in a hurry carries one plate out before the taster reaches it. Of course, that is the plate with the wrong sauce.

It is easy to blame the waiter. But a check that is slow gets skipped, and so does a check that is optional. People are not careless; they are busy.

Last time, we hired the taster: a workflow that runs pytest on every push. In this lesson, we'll turn it into a real pipeline. Quick checks go first, the tests run on two Python versions at once, a cache keeps yesterday's downloads, and a rule stops a red pull request from merging. Before we start, make a guess, and keep it in mind."""

L["guess"]["q"] = ("Your CI has three jobs: lint, test and build. Build waits for the other two with `needs: [lint, test]`. "
                   "A ruleset, the merge rule on main, requires only the build check. A test fails on a pull request. What happens?")
L["guess"]["why"] = ("When a job is skipped because a job it needs failed, GitHub counts it as passed, so the merge goes through. "
                     "Require the lint and test checks as well.")

set_list(L["terms"], "plain", [
    "An automatic check that reads code without running it and flags style problems and likely bugs.",
    "One job written once that GitHub runs several times, once per value, such as each Python version.",
    "Files saved by an earlier run, such as downloaded packages, and restored later to save time.",
    "The name a cache is stored under, built from things like the system and a fingerprint of your package lists.",
    "A file a job uploads, such as a test report, that you can download after the run.",
    "A check that must pass on a pull request before GitHub allows the merge.",
    "A named set of rules for branches or tags, such as 'main needs passing checks'.",
    "A name that lets only one run per group go ahead, cancelling or queueing the others.",
])

S = L["sections"]

S[0]["h"] = "Quick checks first, slow ones last"
S[0]["body"] = """A good pass in a kitchen does not taste every plate first. It glances: right table, right dish, still hot? Only plates that pass the glance get the slow taste. A CI pipeline, the chain of automatic checks on every change, works best in the same order. People wait for it before they merge, so cheap checks go first and slow ones last.

Today you grow the Day 24 `ci.yml` into a real pipeline. Right now it runs the tests once. The lab's pipeline splits the work into three jobs, and each job runs on its own runner (the fresh machine from last time). Each job also shows up on the pull request (PR) as its own check, so you see at a glance which part broke:

1. `lint`: ruff checks style and likely bugs. It takes seconds.
2. `test`: pytest, once for each Python version you support.
3. `build`: builds the Docker image. It is the slowest, so it waits for the other two.

Ruff is a Python linter, a tool that reads code without running it. The tool pytest runs the tests of hello-devops, our tiny web app that answers every visit with a greeting and a count of visits so far. The Docker image, from Part 5, is that app packed with everything it needs to run.

Jobs run in parallel by default, so `lint` and both `test` jobs start at the same moment. The `needs` key makes a job wait: with `needs: [lint, test]`, `build` starts only after all of them succeed. If one fails, `build` is skipped, so you hear about the failure without waiting for the slow part.

The triggers change too. CI now runs on pull requests, which test the merged result, and on pushes to `main`. It no longer runs on pushes to every branch, because then each commit on a PR branch would be tested twice.

One more line, `permissions: contents: read`, limits the token that GitHub gives every job. A token is a temporary key for talking to your repository, and this one may read the code and change nothing. Day 27 explains why that matters. Next, we'll fill in the first two jobs."""

S[1]["h"] = "A linter, the tests, and a report that survives"
S[1]["body"] = """A linter reads your code without running it and flags problems such as unused imports or undefined names. An import is a line that loads code from elsewhere, and an unused one is clutter, sometimes a sign of a mistake. This course uses ruff, which does both linting and formatting (laying out the code in one standard style):

- `ruff check .` finds lint problems, and `ruff check --fix .` fixes the safe ones.
- `ruff format --check .` fails if a file is not formatted, and `ruff format .` formats it.

Both exit with code 1 when they find a problem, so they fail the step the same way `pytest` does.

Next comes a test report. `pytest --junitxml=reports/junit.xml` also writes the results as JUnit XML, a file format most CI tools can read. But the runner is deleted after the job, like a kitchen station wiped at the end of the night. A report saved on it disappears with it.

So you keep the report as an artifact: a file a job uploads and you download later, from the run page or with `gh run download`. It is the tasting notes card that survives the wiped station. Artifacts stay 90 days by default. The lab keeps test reports for 7.

Since version 4, `actions/upload-artifact` has two rules. An artifact cannot be changed after upload, and names must be unique within a run. Two matrix jobs (the Python versions, coming soon) that both upload `junit` would clash, so the lab puts the Python version in the name.

The upload step also has `if: ${{ !cancelled() }}`. Normally GitHub skips every step after one fails. This condition still uploads the report after a test failure, which is when you need it most. Day 26 explains these conditions properly.

The tests are correct now, but every run still installs everything from scratch. Next, we'll give the kitchen a fridge."""

S[2]["h"] = "A fridge for downloads: caching and cache keys"
S[2]["body"] = """Every job starts on an empty machine, so `pip install` downloads every package again on every run. That is the stock boiled from bones each morning. A cache saves files from one run and restores them in the next, like a fridge. Each entry is stored under a cache key, a label that describes what is inside, so a job can tell whether the saved files still fit.

A good fridge label says more than "stock". It says which recipe and which day, so nobody uses last week's stock for this week's recipe. Cache keys work the same way. Part of the key is a hash: a short fingerprint computed from a file's contents. Change one letter in the file, and the hash changes.

`actions/setup-python` has pip caching built in: set `cache: pip`. The key it builds is made of the runner's system and processor, the Python version and a hash of your requirements files, the lists of packages to install. It looks roughly like `setup-python-Linux-x64-24.04-Ubuntu-python-3.14.<patch>-pip-<hash>`. `cache-dependency-path: requirements*.txt` says which files to hash, so changing either file gives a new key.

When the job starts, one of three things happens:

- Exact hit: a cache with the same key exists. The log says "Cache restored from key".
- Partial hit: no exact match, but a key with the same start (same system and Python, older hash). Those older files are restored, and pip downloads only what changed.
- Miss: the log says "pip cache is not found", and pip downloads everything.

A job that missed saves a new entry when it finishes. A run can restore caches from its own branch and from `main`. A cache saved by a pull request stays with that pull request, so no PR can plant files in the runs of `main` or of other PRs. Every new PR therefore starts from `main`'s cache. That is one reason CI also runs on pushes to `main`: it keeps that cache fresh.

GitHub deletes caches nobody used for 7 days and keeps at most 10 GB per repository. **A cache is a speed-up that can vanish. Never rely on it, and never put secrets in it.** With installs quick again, we can afford to run the tests more than once."""

S[3]["h"] = "One job, many versions: the matrix"
S[3]["body"] = """A bakery with a gas oven and an electric oven tests a new cake in both, because the same recipe can behave differently in each. Your app should work on Python 3.13 and 3.14 for the same reason. A matrix runs one job definition several times, once per value:

- `strategy: matrix: python-version: ["3.13", "3.14"]` creates two jobs from one definition.
- `${{ matrix.python-version }}` passes each value to setup-python and into the artifact name.
- `fail-fast: false` lets both finish even if one fails. The default cancels the others at the first failure, which hides whether a bug only affects one version.

The two jobs run at the same time, so the matrix adds almost no waiting. They show up as two checks, `test (3.13)` and `test (3.14)`. Remember those exact names, because the ruleset needs them later today.

A matrix can have several dimensions. Add `os: [ubuntu-latest, ubuntu-24.04-arm]` next to the Python list and you get four jobs, one per combination. `include` adds one extra combination and `exclude` removes one. A single matrix can create at most 256 jobs.

For hello-devops, two is right. Every extra job costs runner time and adds one more check to keep green. The code is now tested twice over, but the Dockerfile is code too, and nothing has tested it yet."""

S[4]["h"] = "Does the image still build?"
S[4]["body"] = """The Dockerfile from Part 5 is the recipe Docker follows to build the image. Like any recipe, it can break. A wrong `COPY` path, or a package that no longer installs, only shows up when you build. So CI builds the image for every change, without pushing it anywhere.

The `build` job uses Docker's own actions:

- `docker/setup-buildx-action` starts a BuildKit builder, the build engine from Part 5.
- `docker/build-push-action` builds the image; with `push: false` it only builds.
- `cache-from: type=gha` and `cache-to: type=gha,mode=max` keep image layers in the Actions cache.

An image is built in layers, one per step of the Dockerfile, and an unchanged layer can be reused. The layer cache works like the one on your laptop from Day 19. If `requirements.txt` did not change, the `pip install` layer comes back from the cache and the build takes seconds.

With `mode=max`, the cache also keeps the layers of the build stage of your multi-stage Dockerfile, not only the final image. A multi-stage Dockerfile, from Day 22, builds in one stage and ships only the last.

On Day 27, a second workflow uses the same actions with `push: true`. Everything is checked now, but a red check still does not stop anyone from merging. That is the next fix."""

L["aside"] = {
    "title": "Can an outsider poison the build cache?",
    "body": "GitHub closed that door in June 2026. Since then, runs started by untrusted triggers may read the default branch's cache but not write to it. These are events that someone outside the repository can set off, such as `pull_request_target` and `issue_comment`, but that run on your default branch (Day 27). Docker's docs say to keep `cache-from` and drop `cache-to` in such workflows. Your `pull_request` workflow is not affected, because its cache never reaches `main` anyway.",
    "after": 4,
}

S[5]["h"] = "Making red mean stop: a ruleset on main"
S[5]["body"] = """Remember the waiter who carried a plate out before the taster saw it. CI only protects you if a red result stops the merge. On GitHub you get that with a **ruleset** on `main`: a named list of rules for branches or tags.

The older feature, branch protection rules, still works. Rulesets are more flexible, since several can apply at once, and anyone with read access can see them. When someone tries to merge, GitHub compares the checks on the PR's newest commit with the check names the ruleset requires.

For `main`, start with these rules:

- Require a pull request before merging, so nobody pushes to `main` directly.
- Require status checks to pass: `lint`, `test (3.13)`, `test (3.14)` and `build`.
- Block force pushes, which is on by default.

A force push overwrites the history on GitHub with yours, so blocking it keeps `main`'s past safe. Four details catch people out:

- On the Free plan, rulesets are only enforced on public repositories.
- A new ruleset starts as Disabled. Set its enforcement status to Active.
- A check only shows up in the ruleset's search after it has run successfully in the repository during the last seven days.
- A job skipped because its `needs` failed counts as passed. That is why you require the lint and test checks too, and not only `build`.

The last one is the answer to today's guess. You work alone, so leave required approvals at zero. GitHub does not let you approve your own pull request.

On a team you would also turn on the two options Day 23 pointed to. Require review from Code Owners makes an owner's approval part of the merge rule. Require branches to be up to date before merging makes every pull request pass its checks against the newest `main`, so two green pull requests cannot break it together.

Red now means stop. The last risk is a pipeline so slow that people work around it."""

S[6]["h"] = "Keeping CI fast enough that nobody skips it"
S[6]["body"] = """Slow CI changes how people work. They stop waiting for it, or they bundle many changes into one big PR. These settings keep it quick:

- `concurrency` with `cancel-in-progress` cancels a stale run when you push again to the same branch or PR.
- `timeout-minutes` stops a hung job early, instead of after the default 360 minutes.
- `paths-ignore` on `push` skips runs when a push only changes Markdown files.
- The pip and Docker layer caches keep installs and builds short.

In the kitchen, concurrency is the table that changes its order: you stop cooking the old dish. On `main` the lab lets every run finish, so each merge gets a full result.

A path filter on `pull_request` looks like an easy way to save minutes, and it is a trap when its checks are required. A PR that only touches docs never runs the workflow, so it never reports. Its checks stay Pending forever and block the merge. Filter only `push`, as the lab does.

For deploys, cancelling is the wrong move. By default a concurrency group holds one running and one waiting run. A newer waiting run replaces the older one. `queue: max` lets up to 100 runs wait in line instead. The Terraform workflow on Day 35 uses a group that never cancels.

Two tools help before you push. The linter [actionlint](https://github.com/rhysd/actionlint) checks workflow files for mistakes such as typos in keys, bad expressions and unsafe use of untrusted input. And [act](https://github.com/nektos/act) runs workflows on your laptop in Docker containers. It is handy for quick tries. Each job runs in a container image you pick, which usually holds fewer tools than a GitHub runner, so the real test is still a push.

This pipeline has limits too. The lint and test jobs repeat the same setup steps, and the file grows with every job. And it uses bits we have not explained, such as `${{ !cancelled() }}`. Day 26 deals with both."""

L["closing"] = """We started with plates piling up at the pass, stock boiled from bones every morning, and a waiter who could carry out a plate nobody had tasted. Now quick checks come first, the tests run on both Python versions at once, the cache keeps yesterday's downloads, and the ruleset makes red mean stop.

Open one test job in your newest run and find the setup-python step. Does it say "Cache restored from key"?

Next, we'll learn the small language inside `${{ }}`. Why does a step after a failure sometimes run and sometimes not, and how do jobs hand values to each other?"""

drop_extras(L)

set_list(L["worked"]["steps"], "say", [
    "A teammate's PR adds `import json` to `app.py` but never uses it. The `lint` check turns red, both test checks pass, and `build` is skipped. You read the failure from the terminal with `gh`, GitHub's command-line tool.",
    "The log ends with ruff's report, followed by a suggested fix and `Found 1 error.`. F401 is the rule for unused imports, and `[*]` means ruff can fix it. The step failed because ruff exited with code 1.",
    "Check out the PR branch and run the same command on your laptop. The concise format gives one line per problem. You get the same answer in a second, without waiting for CI.",
    "Let ruff fix it, then run everything CI runs, in the same order. All three commands now exit with 0.",
    "Commit and push to the same branch, which starts a new run. If the old run were still going, concurrency would cancel it. Once all four checks are green, the ruleset lets you merge.",
])

L["task"]["steps"] = [
    "Check that your repository is public with `gh repo view --json visibility`. On the Free plan, rulesets only work on public repos.",
    "On a branch `ci-pipeline`, grow `ci.yml` into the Day 25 version in the Files section one piece at a time: triggers, concurrency, permissions, lint job, matrix, cache, report, build.",
    "Before you push, run `actionlint`, `ruff check .`, `ruff format --check .` and `pytest -q` on your laptop.",
    "Push, open a PR, and watch it with `gh pr checks --watch`. Expect four checks: `lint`, `test (3.13)`, `test (3.14)` and `build`.",
    "Open the log of one test job and find the setup-python step. Does it say \"pip cache is not found\" or \"Cache restored from key\"? Push an empty commit (`git commit --allow-empty -m retry`) and compare.",
    "Download one JUnit report with `gh run download` and open the XML file.",
    "Merge the PR. Then, in Settings, open Rulesets and create a branch ruleset for `main`: require a pull request and the four status checks, and set enforcement to Active.",
    "Prove it works. On a new branch, break a test, open a PR, and confirm that GitHub blocks the merge. Then fix the test and merge.",
]
L["task"]["hints"] = [
    "A check name only shows up in the ruleset search after it has run in the repository recently, so let the pipeline run first.",
    "In the ruleset, the default branch is the easiest target to add.",
    "If `build` fails while tests pass, run `docker build .` locally to see the same error.",
]
L["task"]["done_when"] = "You are done when a PR with a failing test shows the merge as blocked, and the fixed PR merges with four green checks."

L["explain_back"]["answer"] = ("Every pull request starts the ci workflow. "
                               "Lint and the tests run first, the tests once per Python version through the matrix, and the build job waits for all of them with needs. "
                               "A ruleset on main requires a pull request plus all four checks, so the merge stays blocked until they are green. "
                               "I list the lint and test checks by name, because a build skipped after a failure would otherwise count as passed.")

L["recap"] = [
    "Order checks from cheap to slow: lint and tests in parallel, then the Docker build with needs.",
    "cache: pip keys the cache on system, Python version and a hash of the requirements files; the gha cache does the same for image layers.",
    "A matrix runs one job per Python version, and each one becomes its own check.",
    "Artifact names must be unique per run; upload test reports with if: ${{ !cancelled() }}.",
    "A ruleset on main with every required check, set to Active, blocks red pull requests; concurrency and timeouts keep CI quick.",
    "The limit: the file repeats itself and leans on expressions we have not explained yet, which Day 26 covers.",
]

C = L["check"]
C[0]["why"] = "Required checks are matched by exact name, so a new matrix check is not required until you add it."
C[1]["why"] = "A workflow skipped by a path filter never reports, so its required checks stay Pending."
C[2]["why"] = ("The hash of the requirements files changed, so the exact key misses. "
               "The restore key with the same system and Python matches, and pip fetches only the new package.")

I = L["interview"]
I[0]["a"] = ("First I measure where the time goes, using the job and step timings on the run page. "
             "Then I cache what does not change, such as package downloads and Docker layers. "
             "I run independent jobs in parallel, put cheap checks such as lint first, and cancel stale runs with concurrency. "
             "If tests are the slow part, I split them across parallel jobs and move slow end-to-end tests to a later stage.")
I[1]["a"] = ("They are checks named in a ruleset or branch protection rule that must pass before a pull request can merge. "
             "GitHub matches them by exact name, so renaming a job or changing a matrix can drop protection until you update the list. "
             "A workflow skipped by a path or branch filter leaves its checks Pending and blocks the merge. "
             "And a job skipped because its dependency failed counts as success, so you must also require the earlier jobs.")
I[2]["a"] = ("A cache is a speed-up for future runs, such as downloaded packages, stored under a key and restored when the key matches. "
             "It is best effort: GitHub removes entries unused for 7 days. "
             "An artifact is an output of one run, such as a test report or a build, that people or later jobs download. "
             "Since upload-artifact v4, artifacts cannot be changed after upload and need unique names per run.")

L["deeper"]["body"] = """Listing every matrix check in the ruleset works, but it can break quietly. Add Python 3.15 next year and forget the ruleset, and the new check is not required. Rename a job, and the old required name never reports again, so every PR waits forever.

Many teams fix this with one gate job at the end of the workflow, and they require only that job. Picture one person at the kitchen door who reads every station's sign-off before a plate leaves. The gate has:

- `needs: [lint, test, build]`, so it waits for every other job.
- `if: ${{ always() }}`, so it runs even when a needed job failed or was skipped.
- One step that runs `exit 1` when `contains(needs.*.result, 'failure')` or `contains(needs.*.result, 'cancelled')` is true.

`needs.*.result` is a list with the result of each needed job: `success`, `failure`, `cancelled` or `skipped`. The gate turns that list into one answer. Using `always()` is safe here, because the gate only reads results and runs nothing risky. Day 26 explains `always()` and the `needs` context in detail.

Why not a gate with plain `needs` and no `if`? A failed test would then skip the gate, and a skipped gate counts as passed. It is the same trap as before, one level further down. With `always()`, the gate runs every time and reports what really happened.

For a small repository with four checks, a gate is more than you need, and listing the checks is clearer, so the lab does that. Reach for a gate when your matrix grows or when some jobs only run sometimes.

Caches deserve one more look, because they are shared between runs. Anything a job writes into a cached folder, a later run restores and may execute. That is why GitHub limits who can write caches for the default branch, and why the docs tell you never to cache secrets. Since 2026 you can also set a `cache-mode` key on a job: `read`, `write`, `write-only` or `none`. It gives the job only the cache access it needs, for example `read` for a job that handles untrusted input. See the [dependency caching reference](https://docs.github.com/en/actions/reference/workflows-and-actions/dependency-caching).

Read more about required checks in [Troubleshooting required status checks](https://docs.github.com/en/pull-requests/how-tos/merge-and-close-pull-requests/troubleshooting-required-status-checks)."""

save(path, P)
print("d25 written")
