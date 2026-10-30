#!/usr/bin/env python3
"""Rewrite the prose of content/p3.json so it reads like a person wrote it.

Loads the current JSON, replaces prose fields only (never ids, titles, code,
commands, refs, sources, answers, options or diagrams) and writes it back.
Run: python3 brief/scratch/p3/humanize.py
"""
import json
import pathlib

PATH = pathlib.Path(__file__).resolve().parents[3] / "content" / "p3.json"
P = json.loads(PATH.read_text())


def T(s):
    return s.strip("\n")


def set_list(items, key, new):
    """Replace items[i][key] for each new value; None keeps the old one."""
    assert len(items) == len(new), (key, len(items), len(new))
    for it, val in zip(items, new):
        if val is not None:
            it[key] = T(val)


def set_strs(old, new):
    assert len(old) == len(new), (len(old), len(new))
    return [T(n) if n is not None else o for o, n in zip(old, new)]


# ---------------------------------------------------------------- part level

P["intro"] = T("""
Until now you ran every check and build for hello-devops yourself. In this part GitHub runs them for you. Each pull request gets linted, tested and built, only green ones reach main, and pushing a version tag publishes a release image. You already have a tested app and a production-ready image, and that is all a pipeline needs to start.
""")

P["recap"] = set_strs(P["recap"], [
    "Change code on small, short-lived branches, and merge through pull requests that a reviewer and CI both check.",
    "CI builds and tests every change. With continuous delivery a person picks the release moment; with continuous deployment nobody does.",
    "A workflow is a YAML file in .github/workflows: an event starts it, and each job runs its steps on a fresh runner.",
    "The lab's ci.yml lints, tests on Python 3.13 and 3.14, keeps a JUnit report and checks that the Docker image builds.",
    "A ruleset on main with required checks stops red pull requests from merging.",
    "release.yml turns a v* tag into one amd64 and arm64 image in GHCR, built once and deployed by digest.",
    "Give tokens the least access they need: read-only by default, OIDC instead of stored keys, approval before production.",
    "Pin third-party actions to commit SHAs, and let Dependabot keep the pins current.",
])

set_list(P["flashcards"], "back", [
    "Delivery: every change is ready to release, and a person clicks release. Deployment: every passing change goes live on its own.",
    "Build the image one time, then promote that same digest through every environment.",
    None,
    "A canary gets a small share of traffic first. Blue/green switches all traffic at once between two full copies.",
    None,
    None,
    "Any command that ends with a non-zero exit code.",
    "The job waits for test to succeed. If test fails, this job is skipped.",
    "So the report still uploads after an earlier step failed. It is skipped only when the run was cancelled.",
    "If an earlier job fails, the last job is skipped, and GitHub counts a skipped check as passed.",
    "A required check skipped by a path filter stays Pending and blocks the merge.",
    "It makes the GITHUB_TOKEN read-only for code in every job, and sets every permission you don't list to none.",
    None,
    None,
    "Whoever controls the action's repository can move a tag to other code. A full commit SHA always means the same code.",
    "Private, even in a public repository. Make it public in its package settings, or pull with a read:packages token.",
])

set_list(P["quiz"], "why", [
    "Branches that live long and grow big drift away from main. Conflicts pile up, and reviewers can only skim.",
    "workflow_dispatch adds the Run workflow button, once the workflow file is on the default branch.",
    "Each matrix job uploads its own report, and two artifacts in one run cannot have the same name.",
    "GHCR is part of GitHub Packages, so the token needs packages: write to push there.",
    None,
    "Whoever controls the action's repository can move a tag. A full SHA always names the same code.",
    "grep exits with 1 when it finds no match, and any non-zero exit code fails the step.",
    "A tag can be moved to another image. A digest names the exact content and never changes.",
])

L09, L10, L11, L12 = P["lessons"]
assert [L["id"] for L in P["lessons"]] == ["d09", "d10", "d11", "d12"]


def sections(L, bodies):
    assert len(L["sections"]) == len(bodies)
    for s, b in zip(L["sections"], bodies):
        if b is not None:
            s["body"] = T(b)


# ---------------------------------------------------------------- d09

L = L09
L["goal"] = "By the end you can open, review and merge a pull request with gh, tag a version, and tell continuous integration, delivery and deployment apart."
L["guess"]["why"] = "With continuous deployment, every change that passes the pipeline goes live and nobody clicks anything. Merging daily is continuous integration, and a human release click is continuous delivery."

sections(L, [
"""
When you work alone, you can commit straight to `main`. With a team, that breaks quickly. Two people change the same file, and one person's work gets lost, or `main` ends up with code that does not run.

Branches fix this. A **branch** is a movable label that points at a line of commits. You commit on your branch, and `main` does not change until you merge.

The everyday loop looks like this:

1. Create a branch from the latest `main`, for example `git switch -c add-pr-template`.
2. Change files and commit in small steps.
3. Push the branch to GitHub.
4. Merge it into `main` once it is reviewed and tested.

A merge combines two lines of work, and most of the time git does it alone. It stops only when both branches changed the same lines. That is a merge conflict. Git marks the clash in the file with `<<<<<<<`, `=======` and `>>>>>>>`, and you edit the file until it says what it should. Then you add and commit it. The fewer lines a branch touches, the rarer conflicts get, which is one more reason to keep branches small and short.
""",
"""
A pull request (PR) is a GitHub page that asks to merge your branch into `main`. It shows the diff (the lines you changed), a conversation, and the results of automatic checks. Teams use it for:

- Review: a teammate reads the change and comments on single lines.
- Checks: CI runs the tests and shows a green tick or a red cross.
- A record: months later, you can see why a line changed and who agreed.

Small PRs get better reviews. Aim for one that a reviewer can read in ten minutes. In the description, say what changed and how you tested it. The PR template you add today puts those questions in the box for you. And when you review a teammate's PR, be kind to the person while you are strict about the code.

You can open and merge PRs in the browser. Today you use `gh`, the GitHub CLI from Day 2, because it is fast and you can script it.
""",
"""
Your team also has to agree how long branches live and where releases come from. That agreement is the branching strategy, and two styles are common.

In trunk-based development, everyone merges small branches into one main branch, the trunk, at least once a day. A branch lives for hours, or a day or two, and `main` is always in a state you could release. Unfinished features hide behind feature flags, which come up again below.

GitFlow uses several long-lived branches:

- `main` holds released code only.
- `develop` collects finished features.
- `feature/...` branches start from `develop`.
- `release/...` and `hotfix/...` branches prepare and patch releases.

GitFlow fits software that ships a big version a few times a year. If you deploy often, it gets in your way. Long-lived branches drift apart, and merging them back is slow and risky, so most teams that deploy often use trunk-based development. This course uses [GitHub flow](https://docs.github.com/en/get-started/using-github/github-flow), GitHub's own simple trunk-based style.
""",
"""
Continuous integration (CI) means you merge small changes often, and a server builds and tests every change automatically. You hear about a broken test minutes after your push, while you still remember what you changed.

CD has two meanings, and people mix them up:

- Continuous delivery: every change that passes is ready to release. A person clicks a button to put it in production.
- Continuous deployment: every change that passes goes to production automatically. There is no human step.

The steps a change goes through are called a pipeline. A typical pipeline runs in this order:

1. Build: install dependencies and package the code.
2. Test: run linters and automated tests.
3. Publish: build a container image and push it to a registry.
4. Deploy: release that image to staging, then to production.

Build the image one time and never again. This rule is called **build once, deploy many**: the very same image (same digest) moves from staging to production. If you rebuild for production, the build can pull newer packages, and what you ship is no longer what you tested.
""",
"""
Deploying means swapping the old version for the new one while users keep working. Four ways are common:

- Rolling: replace servers or containers a few at a time. Kubernetes does this by default (Day 17).
- Blue/green: run the new version (green) next to the old one (blue), then switch all traffic at once.
- Canary: send a small share of traffic, say 5%, to the new version, then grow it step by step.
- Feature flags: ship new code switched off, then turn it on for some users with a setting.

None of them is free. Rolling needs no extra servers, but old and new versions serve users side by side for a while. Blue/green gives you an instant rollback and costs double the capacity during the switch. A canary limits the damage of a bad release, as long as you have good metrics to judge it (Day 21). Feature flags need no deploy at all. You pay for them later, with `if` branches in the code that someone has to clean up.

On Kubernetes, tools such as [Argo Rollouts](https://github.com/argoproj/argo-rollouts) automate blue/green and canary releases.
""",
"""
A version number tells users how much changed. [Semantic versioning](https://github.com/semver/semver/blob/master/semver.md) uses three numbers, MAJOR.MINOR.PATCH:

- MAJOR goes up when you break compatibility, as in 2.0.0.
- MINOR goes up when you add a feature that stays compatible, as in 1.3.0.
- PATCH goes up for a compatible bug fix, as in 1.2.1.

A git tag is a name for one commit, such as `v1.2.0`. A branch label moves forward with each new commit, but a tag stays where you put it. Use annotated tags (`git tag -a`), which also store who made the tag, when, and a message.

In this course, a tag is what starts a release. On Day 12, pushing the tag `v1.0.0` starts a workflow that builds and publishes the image `1.0.0`. The git tag, the image tag and the app's `version` field then all match. One catch: a plain `git push` does not send tags, so you push each tag by name.
""",
])

L["analogy"] = T("""
A pull request works like a suggested edit in a shared document. You write on your own copy, a colleague reads the suggestion and comments, and the owner accepts it into the main text. CI is a spell checker that runs on every suggestion before anyone reads it. Where it breaks: a document has one text, while git keeps many parallel copies and combines them line by line.
""")

set_list(L["worked"]["steps"], "say", [
    "Two branches changed the same line of `app.py`. On `main`, a teammate changed the default greeting to 'Hello, DevOps team!'. On your branch `friendly`, you changed it to 'Hi there, DevOps!'. Git cannot keep both on its own.",
    "`git status` shows `UU`: both sides changed the file, and it is not merged yet. Find the clash.",
    "Above `=======` is your current branch (HEAD, here `main`). Below it is the incoming branch. You decide the result. Here you combine both ideas and delete all three marker lines.",
    "Adding the file tells git the conflict is solved. Then commit. The graph shows the two lines of work joined by a merge commit.",
    "Run the tests before you push. Git only checks that the text merged cleanly, and it has no idea whether the code still works. Here the teammate's test still expects 'Hello, DevOps team!', so you fix `test_app.py` and commit again. Breaks like this are what CI is for.",
])

L["mistake"] = T("""
The classic mistake is a big branch that lives for days and ends as one huge pull request. Reviewers can only skim it, conflicts pile up, and when a test fails you can't tell which change broke it. Make one small branch per change, open the PR early (as a draft if it is not ready), and merge within a day or two.
""")

L["real_world"] = T("""
At PayLoop, a made-up payments company, every change to the checkout service goes through a pull request. The merge button turns on only after one approving review and green CI. Merges to `main` deploy to staging on their own. The same image reaches production when an engineer clicks approve, and that human click is what makes it continuous delivery.
""")

L["task"]["steps"] = set_strs(L["task"]["steps"], [
    None,
    None,
    "Create `.github/pull_request_template.md` with the content from the Files section. Commit it with a message that says what it adds.",
    None,
    "Open the PR in the browser. Read the Files changed tab the way a reviewer would, and leave a comment on one line.",
    None,
    None,
    "Start a second branch, change one line, and push it. On the repository page, click Compare & pull request. The description box now starts from your template. Close that PR if you don't need it.",
])

L["explain_back"]["answer"] = T("""
Continuous integration means we all merge small changes often, and a server builds and tests each one, so we hear about a break within minutes. Continuous delivery carries every passing change through the rest of the pipeline, so it is packaged and ready to release, and a person decides when it goes to production. Continuous deployment drops that last human step, and every passing change goes live on its own. In both kinds of CD, the artifact is built once, and that same artifact moves through each stage.
""")

L["recap"] = set_strs(L["recap"], [
    None,
    "A merge conflict means two branches changed the same lines. You pick the result and commit it.",
    "Trunk-based development keeps main releasable with small daily merges. GitFlow uses long-lived branches and suits rare, big releases.",
    "CI builds and tests every change. Continuous delivery keeps it ready to release, and continuous deployment releases it automatically.",
    None,
    None,
])

set_list(L["check"], "why", [
    "Every change is ready to ship and a person picks the moment. That is continuous delivery.",
    None,
    None,
])

set_list(L["interview"], "a", [
    "Both build, test and package every change automatically, so main is always releasable. In continuous delivery, a person decides when a release goes to production, often with one click or an approval. In continuous deployment, every change that passes the pipeline goes to production with no human step. That only works with strong automated tests, good monitoring and fast rollback, because nobody looks at each release by hand.",
    "Trunk-based development keeps branches small and short-lived, so merges are easy and conflicts are rare. Main stays releasable, which fits CI and frequent deploys. In GitFlow, the long-lived develop and release branches drift apart, and merges get big and risky. GitFlow still fits products that ship versioned releases a few times a year, or that must patch several old versions.",
])

L["deeper"]["body"] = T("""
When you merge a pull request on GitHub, you pick one of three methods, and each leaves a different history on `main`:

- Create a merge commit: keeps every commit from the branch and adds one merge commit with two parents.
- Squash and merge: combines all branch commits into one new commit on `main`.
- Rebase and merge: replays each branch commit on top of `main`, with no merge commit.

Many trunk-based teams choose squash, and it is a good default. One PR becomes one commit, so `git log` stays readable and `git revert` can undo a whole PR in one step. The small commits inside the PR are still visible on the PR page. Admins can switch methods on or off in the repository settings, so the whole team uses one style. See [About merge methods on GitHub](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/configuring-pull-request-merges/about-merge-methods-on-github).

How does git merge text at all? It uses a three-way merge. First it finds the merge base: the last commit both branches share. Then it compares each side with that base, region by region:

1. If only one side changed a region, git takes that change.
2. If both sides made the same change, git takes it once.
3. If both sides changed the same region in different ways, git marks a conflict.

So the fewer lines each side changed since the merge base, the smaller the chance that both touch the same region. That is the mechanical reason short branches conflict less.

The same rules hide a trap. Git can cleanly merge two changes that still break each other. Say one branch renames a function, and another branch adds a new call to the old name. No lines clash, so git is happy, and the code is broken anyway. Only tests catch this. That is why CI runs on the merged result of a pull request, which you will see in the `pull_request` event on Day 10.

Last, rebasing. `git rebase main` replays your branch's commits on top of the newest `main`, so your branch looks as if you started it today. It rewrites your commits with new IDs. Only rebase branches that nobody else works on, and push afterwards with `git push --force-with-lease`. That flag refuses to overwrite work you have not seen.
""")

# ---------------------------------------------------------------- d10

L = L10
L["guess"]["why"] = "GitHub-hosted runners are brand-new virtual machines for every job, so nothing from the last run is left. That is why almost every job starts with checkout and setup steps."

sections(L, [
"""
You describe a task in a YAML file, and GitHub runs it when something happens in your repository. That is GitHub Actions, the automation built into GitHub. CI is its most common use. It can also automate releases, label issues or run checks every night.

The pieces fit inside each other, from the outside in:

1. An event happens, for example you push a commit.
2. GitHub finds every **workflow** that listens for that event.
3. Each workflow starts one or more jobs. Jobs run in parallel unless one needs another.
4. Each job runs on a **runner**, a machine that executes the job's steps in order.
5. Each step is a shell command or a ready-made action.

A step fails when its command ends with a non-zero exit code, the same exit codes you met on Day 3. The job then stops and is marked as failed. `pytest` exits with 1 when a test fails, so one failing test turns the job red.
""",
"""
Workflows live in `.github/workflows/` at the root of your repository. GitHub treats every `.yml` or `.yaml` file there as a workflow. You will use these top-level keys most:

- `name`: the label shown in the Actions tab.
- `on`: the events that start the workflow.
- `env`: environment variables for all jobs (optional).
- `jobs`: a map from job IDs, such as `test`, to job settings.

Inside a job, `runs-on` picks the runner and `steps` lists the work. Give your steps a `name`, so the logs are easy to read.

YAML trips most people up at first. Indentation carries meaning, so use spaces and never tabs. A list item starts with a dash and a space. Strings with special characters, such as `*` or `:`, need quotes. Versions need quotes too: YAML reads `3.10` as the number 3.1, so write `"3.10"`. The YAML extension in VS Code from Day 2 flags many of these mistakes while you type.
""",
"""
The `on` key lists the events. You will use these four a lot:

- `push`: a commit or tag is pushed. Filters such as `branches: [main]` or `tags: ["v*"]` narrow it down.
- `pull_request`: a PR is opened, gets new commits, or is reopened.
- `workflow_dispatch`: adds a Run workflow button to the Actions tab.
- `schedule`: runs on a timer written in cron syntax.

A `pull_request` run tests the result of merging your branch into the target branch, so it catches clashes with other people's work. The Run workflow button only appears once the workflow file is on the default branch.

Schedules come with the most rules. They use UTC unless you set a time zone, and the shortest interval is every 5 minutes. They run only from the default branch and can start late when GitHub is busy. In public repos, GitHub switches them off after 60 days without activity.

You can list several events at once. `on: [push, workflow_dispatch]` runs on every push and also gives you the button.
""",
"""
Runners come in two kinds:

- GitHub-hosted: a fresh virtual machine for every job, with git, Docker, Python and many other tools installed. In public repos the standard Linux runner has 4 CPUs and 16 GB of memory.
- Self-hosted: a machine you run yourself and register with GitHub. It helps with special hardware or private networks, but patching and securing it is your job.

This course uses GitHub-hosted runners. The standard ones are free in public repositories. Private repos on the Free plan get a monthly allowance: at the time of writing, $12 of compute, which is about 2,000 Linux minutes. Check the [current billing page](https://docs.github.com/en/billing/concepts/product-billing/github-actions) before you rely on these numbers.

A step does its work in one of two ways. With `run:`, it executes shell commands, with bash on Linux. With `uses:`, it calls an action: packaged code that someone published, such as `actions/checkout@v7`. The part after `@` is the version, and you pass inputs to the action under `with:`. Each runner starts empty, so nearly every job begins with `actions/checkout`, which copies your repository onto the runner.
""",
"""
A context is a set of facts about the current run. You read one with an expression, written as `${{ ... }}`. GitHub replaces the expression with its value before the step runs. You will see these often:

- `${{ github.sha }}`: the full commit ID that started the run.
- `${{ github.ref_name }}`: the branch or tag name, such as `main` or `v1.2.0`.
- `${{ github.event_name }}`: the event, such as `push`.
- `${{ runner.os }}`: the runner's operating system, such as `Linux`.

You can set environment variables with `env` for the whole workflow, for one job, or for one step. The most specific level wins, so a step's value beats the job's value. GitHub also sets default variables in every step, such as `GITHUB_SHA` and `GITHUB_REF_NAME`.

Start one safety habit now. Some values are text that other people control, like branch names or PR titles. If you paste their expressions straight into a `run:` script, that text becomes part of your script, and the shell may run it as code. Copy the value into `env` first and use the shell variable, as the hello workflow does. The shell then treats it as plain data.
""",
"""
Every run shows up in your repository's Actions tab. Click a run to see a graph of its jobs, then click a job to see the log of each step. A green tick means success, a red cross means failure, and a grey icon means skipped or cancelled.

When a run fails, open the first red step and read the last lines of its log. The error is usually there. The `gh` CLI does the same from your terminal:

- `gh run list` shows recent runs and their status.
- `gh run watch` follows a run live until it finishes.
- `gh run view --log-failed` prints only the logs of failed steps.
- `gh run rerun --failed` runs the failed jobs again.

GitHub keeps logs for a limited time, and anyone who can read the repository can read them. Never print a secret, not even for a quick test.
""",
])

L["analogy"] = T("""
A workflow is like an order ticket in a restaurant kitchen. An order comes in (the event), a cook gets a clean, empty station (the runner) and follows the ticket line by line (the steps). When the dish is done, the station is wiped for the next order. The kitchen picture fails on leftovers: a kitchen keeps them, and a runner keeps nothing unless you save it as a cache or an artifact (Day 11).
""")

set_list(L["worked"]["steps"], "say", [
    "Work on a branch, so your experiments stay off `main`. The folder name matters: GitHub only reads workflows from `.github/workflows/`.",
    None,
    "Commit and push. The push is the event, so the run starts within seconds. `gh run watch` asks which run to follow and stays with it until it ends.",
    None,
    "Expand the second step. `uname -sm` prints `Linux x86_64`, followed by the Python and Docker versions. Those tools are already on the runner, so your CI only has to pick a Python version and install your packages.",
    "That was practice. Delete the branch here and on GitHub, so `hello.yml` never runs again.",
])

L["mistake"] = T("""
If you save the workflow in the wrong folder, such as `.github/workflow/` or `github/workflows/`, GitHub ignores it. Nothing runs, and no error appears anywhere. The folder must be exactly `.github/workflows/` at the root of the repository.
""")

L["real_world"] = T("""
PayLoop starts every new service from the same CI template, so tests run on every push from the service's first day. When everything is green, engineers rarely open the Actions tab. When a pull request shows a red cross, they go straight to the failed step's log.
""")

L["task"]["hints"] = set_strs(L["task"]["hints"], [
    "Your file has the same shape as `hello.yml`. Only the steps differ.",
    None,
    None,
])

L["recap"] = set_strs(L["recap"], [
    "Workflows are YAML files in .github/workflows, and the events listed under on start them.",
    None,
    None,
    None,
    None,
    "Debug from the first red step, in the Actions tab or with gh run view --log-failed.",
])

set_list(L["check"], "why", [
    "Cron fields start with the minute, then the hour, so \"0 2 * * *\" is 02:00. workflow_dispatch adds the button.",
    "By default, a non-zero exit code fails the step and stops the job.",
    None,
])

set_list(L["interview"], "a", [
    None,
    "GitHub-hosted runners are fresh, patched virtual machines that you do not maintain, and they are free for public repos. Self-hosted runners make sense when you need special hardware, access to a private network, or lower cost at very high volume. In exchange, you patch, scale and secure them yourself. GitHub recommends self-hosted runners only for private repositories, because a pull request from a fork could run code on your machine.",
])

L["deeper"]["body"] = T("""
A `run:` step looks like a list of commands, but GitHub saves it as a script file and runs that file with a shell. The shell and its options decide how failures behave.

On Linux runners, if you do not set `shell`, GitHub runs `bash -e {0}`, where `{0}` is the script file. The `-e` flag is the `set -e` from Day 3: the script stops at the first command that fails, and the step fails with that exit code.

If you write `shell: bash` yourself, GitHub runs `bash --noprofile --norc -eo pipefail {0}` instead. The extra `pipefail` changes how pipes fail. Without it, a pipe returns the exit code of its last command. So `pytest -q | tee test.log` passes even when tests fail, because `tee` worked fine. With `pipefail`, the failing `pytest` fails the whole pipe, and the step goes red.

To set the shell once for every step, add a `defaults` block at the top of the workflow with `run: shell: bash` inside it. Many teams do this to get `pipefail` everywhere, and I would too.

Some more facts that save debugging time:

- Each `run:` step starts a new shell. A variable you `export` in one step is gone in the next one.
- To hand a value to later steps, append a line like `NAME=value` to the file named in `$GITHUB_ENV`.
- All steps in a job share one disk, so a file written in step 2 is still there in step 3.
- `working-directory: app` runs a step inside a subfolder.
- `continue-on-error: true` lets a step fail without failing the job. Use it rarely, because it hides problems.

The supported shells table in the [workflow syntax reference](https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax) lists the exact command line for each shell. If a script works on your laptop and fails in CI, check these flags early.
""")

# ---------------------------------------------------------------- d11

L = L11
L["guess"]["why"] = "GitHub treats a skipped check as passed, so a skipped build does not block the merge. Require the test checks as well."

sections(L, [
"""
Today you grow the Day 10 `ci.yml` into the lab's final version, one piece at a time. Right now it only runs the tests. A real pipeline checks more, and it has to be quick, because people wait for CI before they merge. Put cheap checks first and slow ones last:

1. Lint and format check: seconds. It catches typos and unused code.
2. Unit tests on each Python version you support: seconds to minutes.
3. Docker build: the slowest part, so it only runs after the tests pass.

Jobs run in parallel by default. The `needs` key makes a job wait. With `needs: test` on the `build` job, the build starts only after every test job succeeds. If a test fails, the build is skipped, and you get the bad news without paying for the slow part.

The triggers change too. On Day 10, CI ran on every push. Now it runs on pull requests, which test the merged result, and on pushes to `main`. Running on pushes to every branch as well would test each PR commit twice. One more line, `permissions: contents: read`, makes the job's token read-only. Day 12 explains why that matters.
""",
"""
A linter reads your code without running it and flags problems such as unused imports or undefined names. This course uses ruff, which handles both lint and formatting:

- `ruff check .` finds lint problems, and `ruff check --fix .` fixes the safe ones.
- `ruff format --check .` fails if a file is not formatted, and `ruff format .` formats it.

Both exit with code 1 when they find a problem, so they fail the step the same way `pytest` does.

Next comes a test report. `pytest --junitxml=reports/junit.xml` also writes the results as JUnit XML, a format most tools can read. The runner is deleted after the job, so you save the report as an artifact with `actions/upload-artifact`. You can download it from the run page or with `gh run download`.

Put `if: ${{ !cancelled() }}` on the upload step. Normally GitHub skips every step after one fails. With this condition, the upload still runs after a test failure, and that is the run where you need the report most. Artifact names must be unique within a run, so the name includes the Python version.
""",
"""
Every job starts on an empty machine, so `pip install` downloads every package again. A cache fixes that, and `actions/setup-python` has one built in: set `cache: pip`. It saves pip's download folder after the job, under a key made from a hash of your requirements files. The next run with the same files restores it in seconds. Set `cache-dependency-path: requirements*.txt` too, so a change to either requirements file starts a fresh cache.

A matrix runs one job definition several times with different values. Your app should work on Python 3.13 and 3.14:

- `matrix: python-version: ["3.13", "3.14"]` under `strategy` creates two jobs.
- `${{ matrix.python-version }}` passes each value to setup-python.
- `fail-fast: false` lets both finish, even if one fails. The default cancels the rest.

The two jobs run at the same time, so the matrix adds almost no waiting. They show up as two separate checks, `test (3.13)` and `test (3.14)`. Remember those exact names, because the ruleset needs them later today.
""",
"""
Your Dockerfile is code too, and it can break. A wrong `COPY` path, or a package that no longer installs, only shows up when you build. So CI builds the image for every change, without pushing it anywhere.

The `build` job uses Docker's own actions:

- `docker/setup-buildx-action` starts a BuildKit builder.
- `docker/build-push-action` builds the image; with `push: false` it only builds.
- `cache-from: type=gha` and `cache-to: type=gha,mode=max` keep image layers in the Actions cache.

The layer cache behaves like the one on your laptop from Day 6. If `requirements.txt` did not change, the `pip install` layer comes back from the cache and the build takes seconds. On Day 12, a second workflow uses the same actions with `push: true`.
""",
"""
CI only protects you if a red result stops the merge. On GitHub you get that with a **ruleset** on `main`: a named list of rules for branches or tags. The older feature, branch protection rules, still works. Rulesets are more flexible, since several can apply at once, and anyone with read access can see them.

For `main`, start with these rules:

- Require a pull request before merging, so nobody pushes to `main` directly.
- Require status checks to pass: `test (3.13)`, `test (3.14)` and `build`.
- Block force pushes, which is on by default.

Most people get caught by at least one of these details:

- On the Free plan, rulesets are only enforced on public repositories.
- A new ruleset starts as Disabled, so set its enforcement status to Active.
- A job skipped because its `needs` failed counts as passed, so require the test checks too.

You work alone, so leave required approvals at zero. GitHub does not let you approve your own pull request.
""",
"""
Slow CI changes how people work. They stop waiting for it, or they bundle many changes into one big PR. These settings keep it quick:

- `concurrency` cancels a stale run when you push again to the same branch or PR.
- `timeout-minutes` stops a hung job early. The default is 360 minutes.
- `paths-ignore` on `push` skips runs when a push only changes Markdown files.
- The pip and Docker layer caches keep installs and builds short.

The lab makes one exception to the cancelling: on `main`, every run finishes, so each merge gets a full result.

Never put path filters on `pull_request` when its checks are required. A workflow that is skipped never reports, so its checks stay Pending and block the merge.

Two tools help before you push. [actionlint](https://github.com/rhysd/actionlint) checks workflow files for mistakes such as typos in keys or bad expressions. [act](https://github.com/nektos/act) runs workflows on your laptop in Docker containers. It is handy for quick tries, but it does not match GitHub's runners exactly, so the real test is still a push.
""",
])

L["analogy"] = T("""
CI is like the final inspection line in a car factory. Quick checks such as the lights and the horn come first, and only cars that pass them get the slow road test. The matrix is the same road test on two kinds of road at once. The ruleset is the guard at the gate who lets no car out without a fully signed sheet. One difference: CI inspects a car that does not exist yet, the merged result of your branch and main.
""")

set_list(L["worked"]["steps"], "say", [
    "A teammate's PR adds `import json` to `app.py` but never uses it. Both test checks turn red at the Lint and format check step, and `build` is skipped. You read the failure from the terminal.",
    "The log ends with ruff's report. F401 is the rule for unused imports, and `[*]` means ruff can fix it. The step failed because ruff exited with code 1.",
    "Check out the PR branch and run the same command on your laptop. You get the same answer in a second, without waiting for CI.",
    None,
    "Commit and push to the same branch, which starts a new run. If the old run were still going, concurrency would cancel it. Once all three checks are green, the ruleset lets you merge.",
])

L["mistake"] = T("""
A path filter on the `pull_request` trigger looks like an easy way to save minutes. Then a PR that only touches docs never runs CI, its required checks wait as Pending forever, and the merge stays blocked. Filter only `push`, as the lab does, or skip the expensive work inside the job instead.
""")

L["real_world"] = T("""
The checkout service at PayLoop has a ruleset on main that requires one review and green checks for lint, tests and the image build. The team treats ten minutes as the limit for CI. When a run creeps above that, someone adds caching or splits slow tests. Nobody is on the bypass list for main, not even admins.
""")

L["task"]["steps"] = set_strs(L["task"]["steps"], [
    "Check that your repository is public with `gh repo view --json visibility`. On the Free plan, rulesets only work on public repos.",
    "On a branch `ci-pipeline`, grow `ci.yml` into the version in the Files section one piece at a time: triggers, concurrency, permissions, matrix, cache, lint, report, build.",
    None,
    None,
    None,
    None,
    None,
    "Prove it works. On a new branch, break a test, open a PR, and confirm that GitHub blocks the merge. Then fix the test and merge.",
])

L["explain_back"]["answer"] = T("""
Every pull request starts the ci workflow. Lint and tests run first, once per Python version through the matrix, and the build job waits for them with needs. A ruleset on main requires a pull request plus all three checks, test (3.13), test (3.14) and build, so the merge stays blocked until they are green. I list the test checks by name because a skipped build would otherwise count as passed.
""")

L["recap"] = set_strs(L["recap"], [
    None,
    None,
    "A matrix runs one job per Python version, and each one becomes its own check.",
    None,
    None,
    "concurrency, timeout-minutes and a push-only paths-ignore keep CI quick and cheap.",
])

set_list(L["check"], "why", [
    "Required checks are matched by exact name, so a new matrix check is not required until you add it.",
    "A workflow skipped by a path filter never reports, so its required checks stay Pending.",
    "The pip cache restores downloaded packages, so installs take seconds as long as the requirements files are unchanged.",
])

set_list(L["interview"], "a", [
    "First I measure where the time goes, using the job and step timings on the run page. Then I cache what does not change, such as package downloads and Docker layers. I run independent jobs in parallel, put cheap checks such as lint first, and cancel stale runs with concurrency. If tests are the slow part, I split them across parallel jobs and move slow end-to-end tests to a later stage.",
    "They are checks named in a ruleset or branch protection rule that must pass before a pull request can merge. GitHub matches them by exact name, so renaming a job or changing a matrix can drop protection until you update the list. A workflow skipped by a path or branch filter leaves its checks Pending and blocks the merge. And a job skipped because its dependency failed counts as success, so you must also require the earlier jobs.",
])

L["deeper"]["body"] = T("""
Listing every matrix check in the ruleset works, but it can break quietly. Add Python 3.15 next year and forget the ruleset, and the new check is not required. Rename a job, and the old required name never reports again, so every PR waits forever.

Many teams fix this with one gate job at the end of the workflow, and they require only that job. The gate needs:

- `needs: [test, build]`, so it waits for every other job.
- `if: ${{ always() }}`, so it runs even when a needed job failed or was skipped.
- One step that runs `exit 1` when `contains(needs.*.result, 'failure')` or `contains(needs.*.result, 'cancelled')` is true.

`needs.*.result` is a list with the result of each needed job: `success`, `failure`, `cancelled` or `skipped`. The gate turns that list into one answer. Using `always()` is safe here, because the gate only reads results and runs nothing risky.

Why not a gate with plain `needs` and no `if`? A failed test would then skip the gate, and a skipped gate counts as passed. It is the same trap as before, one level further down. With `always()`, the gate runs every time and reports what really happened.

For a small repository with three checks, a gate is overkill and listing the checks is clearer, so the lab does that. Reach for a gate when your matrix grows or when some jobs only run sometimes.

As a team grows, two more ruleset settings come up. Require branches to be up to date before merging (strict mode) makes each PR pass its checks on top of the newest `main`. It is safer, but a busy repository re-runs CI often. A merge queue solves that at scale: GitHub tests queued PRs together on a temporary branch and merges them in order. Workflows then also need the `merge_group` event, or their required checks never report for the queue.

Read more in [Troubleshooting required status checks](https://docs.github.com/en/pull-requests/how-tos/merge-and-close-pull-requests/troubleshooting-required-status-checks).
""")

# ---------------------------------------------------------------- d12

L = L12

sections(L, [
"""
Passwords, API keys and cloud credentials must never sit in your code. GitHub stores them as secrets instead. A secret is encrypted, and a workflow gets it only when it asks for it by name, as in `${{ secrets.NAME }}`.

Secrets and plain variables can live at three levels:

- Repository: every workflow in the repository can read them.
- Environment: only jobs that use that environment, such as `production`, can read them.
- Organization: several repositories share them, which suits teams.

Variables hold settings that are not secret, such as a region or a bucket name. You read them with `${{ vars.NAME }}`. Set both in Settings, or with `gh secret set` and `gh variable set`.

GitHub hides known secret values in logs as `***`, but don't count on it. A secret that has been changed, for example base64 encoded, is not hidden. So never `echo` a secret, and never put a whole JSON file in one secret. If a secret leaks, rotate it. Pull requests from forks get no secrets at all.
""",
"""
Every job gets a token without asking: the `GITHUB_TOKEN`. GitHub creates it when the job starts, and it expires when the job ends. It only works on the current repository. Actions in the job can use it even if you never pass it to them, so how much it can do matters.

**Least privilege** means a token gets only the access its task needs. You control that with the `permissions` key:

- At the top of the workflow, set the default for every job, such as `contents: read`.
- In a job that needs more, set its own `permissions`, such as `packages: write`.
- Any permission you do not list is set to `none`.

With that setup the release job can push images, and every other job can only read code. If an action in a read-only job is ever compromised, it cannot push a fake image or change your code. Your `ci.yml` from Day 11 already starts with `contents: read` for this reason.
""",
"""
When you push a tag such as `v1.0.0`, `release.yml` builds the image and pushes it to GitHub Container Registry (GHCR). It lands at `ghcr.io/$GH_USER/hello-devops`, the same package you pushed by hand on Day 8. The job runs these steps:

1. `actions/checkout` fetches the code at the tag.
2. The QEMU and Buildx setup actions prepare a builder for amd64 (most servers) and arm64 (your Mac).
3. `docker/login-action` logs in to `ghcr.io` with the `GITHUB_TOKEN`.
4. `docker/metadata-action` turns the git tag into the image tags `1.0.0`, `sha-<commit>` and `latest`.
5. `docker/build-push-action` builds both architectures with `APP_VERSION=1.0.0` and pushes them.

The image is built once, from the tag. The last step writes its digest to the run summary, and later stages deploy this exact image by that digest. Day 22 adds a scan, an SBOM and a signature to this job.

A new GHCR package is private, even when the repository is public. To pull it, make it public in its package settings, or log in with a personal access token (classic) that has the `read:packages` scope.
""",
"""
An environment is a named deploy target, such as `staging` or `production`. A job opts in with `environment: production`. Before that job starts, GitHub checks the environment's protection rules:

- Required reviewers: up to six people or teams. One approval lets the job go on.
- Wait timer: a delay before the job may start.
- Deployment branches and tags: for example, only tags matching `v*` may deploy.

GitHub hands over environment secrets only after the rules pass, so the approval also guards your credentials.

Whether you get required reviewers depends on your plan. On the Free, Pro and Team plans, they only work in public repositories. Private repositories need GitHub Enterprise for them. Watch out for one more thing: if a workflow names an environment that does not exist yet, GitHub creates it with no rules, and the job runs right away.
""",
"""
To deploy to a cloud such as AWS, a workflow needs credentials. The simple way is to store an access key as a secret. That key lives for months, works from anywhere, and is painful to rotate.

OpenID Connect (OIDC) gets rid of the stored key. It works in five steps:

1. The job asks GitHub for a signed ID token, which needs `id-token: write` in `permissions`.
2. The token states facts: this repository, this branch or environment, this workflow.
3. The job sends the token to AWS and asks to use an IAM role.
4. AWS checks the signature and compares the facts with the role's trust policy.
5. If they match, AWS returns keys that expire after one hour by default.

You don't code any of this yourself. The `aws-actions/configure-aws-credentials` action handles steps 1, 3 and 5, and you give it the role ARN and a region. The worked example shows the workflow side, and Day 15 creates the IAM role and its trust policy for real.
""",
"""
Once you have several workflows, you will want to stop copying steps between them. GitHub has two features for that:

- A reusable workflow has `on: workflow_call`. Other workflows call it as a job, with `uses:` and the file path.
- A composite action bundles several steps in an `action.yml` file, used as one step.

Every action you call is someone else's code, and it runs with your token and your secrets. These habits protect you:

- Pin third-party actions to a full commit SHA, and keep the version in a comment.
- Turn on Dependabot for `github-actions`, so it opens PRs that update versions and pins.
- Avoid `pull_request_target` together with code from the pull request.

Why a SHA? Anyone who controls an action's repository can move a tag such as `v4` to different code. A commit SHA always means the same code.

`pull_request_target` is risky because it runs with secrets and a write token, even for pull requests from forks. If the job then runs the fork's build script, a stranger's code gets your secrets. GitHub is adding guard rails, but plain `pull_request` is the safe choice. Day 22 shows real attacks where these habits would have helped.
""",
])

L["analogy"] = T("""
The GITHUB_TOKEN is like a hotel key card. The front desk makes a new card for each stay, it opens only the doors you booked, and it stops working at checkout. A long-lived cloud key is more like a copied master key: it opens many doors for years, so losing it is a disaster. OIDC is showing your passport at the desk to get a fresh card each time. The comparison falls short in one place: a key card has one guest, while every action in a job can use the token.
""")

set_list(L["worked"]["steps"], "say", [
    None,
    "Four problems: it deploys from any branch, its token can write everything, it prints a secret, and it uses long-lived AWS keys. Fix the trigger and the default permissions first.",
    "Give the job an environment, so it waits for approval. Then grant only the extra permission OIDC needs. `id-token: write` lets the job ask for an ID token. It gives no write access to your repository.",
    None,
    "Finish the switch. The IAM role's trust policy accepts only tokens from this repository's production environment (Day 15 builds it). Delete the old key secrets here and deactivate the keys in AWS, so a leaked copy is useless.",
])

L["mistake"] = T("""
If the push to GHCR fails with `denied` while the job has `packages: write`, the package most likely exists already and is not linked to this repository. Your manual push on Day 8 would do that. Open the package settings, add `hello-devops` under Manage Actions access with the Write role, and re-run the job.
""")

L["real_world"] = T("""
PayLoop lets only the release workflow push images, and that workflow only runs for version tags. Production deploys wait in a protected environment until an engineer from the on-call rotation approves. No CI system there holds long-lived cloud keys. Each job gets short-lived AWS credentials through OIDC, with one role per environment.
""")

L["task"]["hints"] = set_strs(L["task"]["hints"], [
    "If the job never asks for approval, check that the environment name in the workflow matches exactly.",
    "Push tags one at a time. GitHub creates no events when you push more than three tags at once.",
    None,
])

L["explain_back"]["answer"] = T("""
The workflow gives every job a read-only GITHUB_TOKEN, and only the image job gets packages: write, so nothing else can push. That token is created for the job and expires when the job ends, so there is no long-lived password to leak. The job uses the production environment, so it waits for my approval before it runs and before any environment secrets are released. The third-party Docker actions are pinned to full commit SHAs, so nobody can swap their code by moving a tag.
""")

L["recap"] = set_strs(L["recap"], [
    "Secrets are encrypted and read by name. Never print them, and rotate any that leak.",
    None,
    None,
    None,
    None,
    None,
])

set_list(L["check"], "why", [
    "The job needs to read code and write one comment. It needs nothing else.",
    "With OIDC each job gets keys that expire soon, and there is no stored secret left.",
    None,
])

set_list(L["interview"], "a", [
    "Stored keys live a long time and work from anywhere. If one leaks, an attacker has access until someone notices and rotates it. With OIDC, the workflow proves who it is with a signed token, and the cloud returns credentials that expire soon. The cloud's trust policy can limit access to one repository, branch or environment. There is no stored secret to leak or rotate, and each role can follow least privilege.",
    None,
])

L["deeper"]["body"] = T("""
The ID token that GitHub gives your job is a JSON Web Token (JWT): a small JSON document, signed by GitHub and encoded as text. Its fields are called claims. Four of them matter most:

- `iss` (issuer) is `https://token.actions.githubusercontent.com`, so the cloud knows who signed it.
- `aud` (audience) says who the token is for; the AWS action asks for `sts.amazonaws.com`.
- `sub` (subject) says which workflow is calling, for example `repo:octo-org/octo-repo:environment:production`.
- `exp` says when the token expires.

The checking happens on the cloud side. The IAM role's trust policy decides which tokens it accepts. A strict policy checks `aud` and the exact `sub`. A loose policy, such as one that matches `repo:octo-org/*`, lets every repository owned by `octo-org` assume the role. Always pin `sub` to one repository, plus a branch or an environment.

The `sub` value depends on the job:

- A job with `environment: production` gets a subject ending in `environment:production`.
- A job running on a branch gets one ending in `ref:refs/heads/main`.
- A job started by a pull request gets one ending in `pull_request`.

So you can give the production role only to production jobs, and a read-only role to pull request jobs.

One recent change affects your repository. Repositories created after July 15, 2026 use an immutable subject format that includes numeric IDs, for example `repo:octo-org@123456/octo-repo@456789:ref:refs/heads/main`. This stops someone who later takes over a deleted account name from matching an old trust policy. Your hello-devops repository is new, so copy the exact format from the [OIDC reference](https://docs.github.com/en/actions/reference/security/oidc) when you write the trust policy on Day 15.

Ask for `id-token: write` only in the job that deploys, not for the whole workflow. And pair OIDC with environments. Protection rules must pass before the job reaches a runner, so no token exists until a person has approved.
""")

PATH.write_text(json.dumps(P, ensure_ascii=False, indent=1) + "\n")
print("wrote", PATH)
