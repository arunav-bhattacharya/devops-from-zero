"""Book-voice rewrite of d24 (fifth pass, writer td). Replaces prose fields only."""
from common import load, save, set_list, drop_extras

path, P, L = load(6, "d24")

L["goal"] = ("By the end you can write a workflow file, start it with a push or a button, pick a runner, "
             "read its logs, and run pytest on every push.")

L["opening"] = """Picture a small café where the owner tastes every pot of soup herself before it goes out. On a quiet Tuesday, that works. On a busy Saturday, with a queue at the door, she skips one taste, just this once. That is the pot with no salt.

Nobody would call her lazy. A check that lives in a busy person's memory gets skipped exactly when it matters most, on the busy day. Testing code on your own laptop has the same weakness.

Last time, our pull requests got a page, a reviewer and a place for a green tick, but nothing to put the tick there. In this lesson, we'll hire the taster: a small file that tells GitHub to run our tests on its own machine after every push. By the end, a broken test turns red without anyone remembering to check. Before we start, make a guess, and keep it in mind."""

L["guess"]["q"] = "Your workflow file asks GitHub for a machine with `runs-on: ubuntu-latest`. Where do your commands run?"
L["guess"]["why"] = ("GitHub starts a brand-new virtual machine (a computer simulated in software) for every job, so nothing from the last run is left. "
                     "That is why almost every job starts by copying in the code and setting up its tools.")

set_list(L["terms"], "plain", [
    "A text file in .github/workflows that tells GitHub what to run automatically, and when.",
    "Something that happens in a repository and starts a workflow, such as a push, a pull request or a timer.",
    "One time a workflow ran, with its own logs and its own result.",
    "A group of steps that runs on one machine; jobs run at the same time unless one waits for another.",
    "One task in a job: either your own command (run) or a ready-made action (uses).",
    "The machine that runs a job; GitHub's own runners are fresh virtual machines.",
    "A published, reusable step such as actions/checkout, called with uses.",
])

S = L["sections"]

S[0]["h"] = "A tester that is nobody's laptop"
S[0]["body"] = """In the last lesson, nothing tested a pull request unless you ran `pytest` on your laptop first. pytest is the Python tool that runs the lab's tests. The lab is hello-devops, a tiny web app that answers every visit with a greeting and a count of visits so far. Your laptop is a poor taster for a team: it has your settings, your files and your memory.

CI, short for continuous integration, means testing every change automatically. It needs a machine that is nobody's laptop, one that runs the same commands for every push and posts the result on the commit. A push sends your saved changes to GitHub. Each saved change is a commit.

GitHub Actions, the automation built into GitHub, gives you that machine. You write the commands in a YAML file, a plain text format made of `key: value` lines. The file lives in your repository, the project's home on GitHub, and GitHub runs it when something happens there. CI is its most common use, but it can also publish releases, label issues or run a check every night.

A restaurant kitchen works the same way. An order ticket arrives on the rail, a cook gets a clean, empty station and follows the ticket line by line. Two cooks can work on two tickets at once. When the dish is done, the station is wiped for the next order. A `git push` sets off the same chain:

1. GitHub records an event for your repository: a push of this commit to this branch. The ticket arrives.
2. It reads `.github/workflows/` in the commit you pushed and starts a run of every **workflow** that listens for `push`.
3. A run starts one or more jobs, each a group of steps. Jobs run in parallel unless one needs another.
4. For each job, GitHub starts a new virtual machine (Day 17), the runner. That is the clean station.
5. The runner comes with Ubuntu, a popular version of Linux (or the system the job asks for), and common tools, but none of your files.
6. The runner application, a program on that machine, runs the job's steps in order. Each step is a shell command (like those you type in a terminal) or a ready-made action.
7. The result, a green tick or a red cross, appears on the commit and its pull request (the review page from last time), and GitHub deletes the machine.

So your laptop takes no part, and no file survives from one job to the next unless you save it (Day 25 shows how).

How does the machine know a step failed? Every command ends with a number, its exit code, which you met in Part 1. Zero means success, and anything else means trouble. A step fails when its command ends with a non-zero exit code. The job stops there and is marked failed, and so is the run.

`pytest` exits with 1 when a test fails, so one failing test turns the whole run red. Most of CI rests on that convention: tools exit non-zero when something is wrong, and GitHub reads the exit code for you on every change. Next, we'll write the ticket itself."""

S[1]["h"] = "The ticket: what a workflow file looks like"
S[1]["body"] = """A workflow is a YAML file, in the same format as `compose.yaml` from Day 21. It lives in `.github/workflows/` at the root of your repository. GitHub treats every `.yml` or `.yaml` file there as a workflow.

Start with the mistake that costs people the most time. Save the file in `.github/workflow/` (no s), push, and wait. Nothing happens: no run, no error, no warning anywhere, because GitHub never looks in that folder. If no run appears after a push, check that path first.

These top-level keys come up most:

- `name`: the label shown in the Actions tab.
- `on`: the events that start the workflow.
- `env`: environment variables for all jobs (optional).
- `jobs`: a map from job IDs, such as `test`, to job settings.

An environment variable is a named setting that programs can read, such as `GREETING`. A job ID is the short name you give a job. Inside a job, `runs-on` picks the runner and `steps` lists the work. Give each step a `name`, so the log, the record of everything a step printed, is easy to read.

YAML gives almost everyone trouble in their first workflows. Watch for these traps:

- Indentation carries meaning. Use spaces, never tabs.
- A list item starts with a dash and a space.
- Versions need quotes: YAML reads `3.10` as the number 3.1, so write `"3.10"`.
- A plain value cannot contain a colon followed by a space. `run: echo "Result: ok"` is a YAML error.

The last trap is the easiest to fall into, because the line looks like a normal sentence. The error says "mapping values are not allowed in this context" and points at the colon. Fix it with `run: |` and the command on the next line.

You don't have to find these by eye. The VS Code YAML extension from Day 2 and actionlint (Day 25) catch all four before you push. VS Code is the code editor you installed, and actionlint is a checker made for workflow files. Next, we'll fill in `on`, the key that decides when a ticket arrives."""

S[2]["h"] = "What starts a run: events"
S[2]["body"] = """A kitchen ticket arrives for a reason: a guest orders, or the clock says it is time to prepare for lunch. Workflows are the same. The `on` key lists the events that start a workflow, and you will use these four most:

- `push`: commits or tags are pushed. Filters such as `branches: [main]` or `tags: ["v*"]` narrow it down.
- `pull_request`: a PR is opened, gets new commits, or is reopened.
- `workflow_dispatch`: adds a Run workflow button to the Actions tab.
- `schedule`: runs on a timer written in cron syntax.

A tag is a fixed name for one commit, such as `v1.0.0`, and PR is short for pull request. Filters also work on file paths. `paths: ["app.py"]` runs the workflow only when that file changed. Day 25 shows the trap that comes with path filters.

A `pull_request` run tests a temporary merge of your branch into the target branch, so it catches clashes with other people's work. That is the problem of the two cooks from last time, caught before the merge. The Run workflow button only appears once the workflow file is on the default branch, the one GitHub shows first (usually `main`).

Schedules have the most rules. Cron syntax has five fields for minute, hour, day of month, month and day of week, where `*` means every. So `"30 6 * * 1"` means 06:30 every Monday. Times are in UTC, the world's reference clock, unless you set a time zone. The shortest interval is every 5 minutes.

A timer has no commit of its own, so schedules run on the latest commit of the default branch. They can start late when GitHub is busy, especially at the start of each hour. In a public repository, GitHub switches them off after 60 days without activity.

You can list several events at once. `on: [push, workflow_dispatch]` runs on every push and also gives you the button. An event says when a job runs. Next comes where it runs."""

S[3]["h"] = "Runners: a clean station for every job"
S[3]["body"] = """Runners come in two kinds:

- GitHub-hosted: a fresh virtual machine for every job, deleted afterwards. It comes with git, Docker, Python, jq and many other tools.
- Self-hosted: a machine you run yourself and register with GitHub. It helps with special hardware or a private network, but patching and securing it is your job.

You met those tools in earlier parts; Docker, for example, is the container tool from Part 5. You pick a GitHub-hosted runner by its label in `runs-on`. The labels name the system and the processor, the chip that runs the programs:

- `ubuntu-latest`: Linux on x64 (Intel or AMD) processors. Today it means Ubuntu 24.04. The label moves to newer versions over time, so write `ubuntu-24.04` when you need it fixed.
- `ubuntu-24.04-arm`: Linux on arm64, the same processor family as your Apple Silicon Mac.
- `windows-latest` and `macos-latest`: Windows, and macOS on Apple M1 machines.

A public repository is one anyone can see. There, the standard Linux runners have 4 CPUs (processor cores) and 16 GB of memory. Private repositories get 2 CPUs and 8 GB.

**Never attach a self-hosted runner to a public repository.** Anyone can open a pull request, and a workflow could then run a stranger's code on your machine. Unlike a hosted runner, your machine is not wiped after each job unless you set that up. Whatever that code leaves behind waits for your next job, like a dirty station that nobody cleaned. GitHub's own docs recommend self-hosted runners only for private repositories.

For this course, GitHub-hosted runners are all you need. A clean station helps only if the cook knows what to do, so next we'll look at the two kinds of instruction a step can hold."""

S[4]["h"] = "Two kinds of step: your own commands, or someone's action"
S[4]["body"] = """A step does its work in one of two ways.

With `run:`, it executes shell commands, the same kind you type in a terminal. On Linux the default shell is bash with `-e`, so the script stops at the first failing command. For several commands, write `run: |` and put one command per line below it.

With `uses:`, it calls an action: packaged code that someone published, such as `actions/checkout@v7`. The name before `@` is a GitHub repository, owner `actions` and repository `checkout`. The part after `@` is the version, usually a git tag. When the job starts, the runner downloads that repository at that tag (the log shows it under Set up job), and your step runs its code. You pass inputs to the action under `with:`, for example `python-version: "3.14"` for `actions/setup-python@v7`.

Now a failure you will almost certainly meet. The runner starts with none of your files. A job that begins with `pip install -r requirements-dev.txt` fails, because `requirements-dev.txt` does not exist on that machine. pip is Python's package installer, and that file lists the packages the tests need.

So nearly every job begins with `actions/checkout`, which copies your repository into the job's working folder. In the kitchen, that is fetching the ingredients before anyone starts to cook.

By default checkout fetches only the one commit the run is about, with no history and no other branches. That keeps it fast, and it is all a test run needs. A step that needs history, such as `git describe` or a changelog script, needs `fetch-depth: 0` under `with:`.

An action is other people's code running inside your job. Prefer actions from GitHub (`actions/...`) and from the tool's own company (`docker/...`), and look at an action's repository before you use it. Day 27 shows how to pin an action so its code cannot change under you. Steps take settings in and leave logs behind, and those come next."""

S[5]["h"] = "Settings in, logs out"
S[5]["body"] = """Workflows pass settings with environment variables, set with `env` at three levels: the whole workflow, one job, or one step. The most specific level wins, so a step's value beats the job's value.

GitHub also sets default variables in every step, such as `GITHUB_SHA` (the commit) and `GITHUB_REF_NAME` (the branch or tag). The workflow file can read the same facts as expressions, such as `${{ github.ref_name }}`. GitHub replaces each `${{ ... }}` with its value before the step starts, and Day 26 covers expressions. The worked example copies the branch name into `env` and uses `"$BRANCH"` in the script; Day 26 explains why that habit matters.

Every run shows up in your repository's Actions tab. Click a run to see a graph of its jobs, then click a job to see each step's log. A green tick means success, a red cross means failure, and a grey icon means skipped or cancelled. When a run fails, open the first red step and read its last lines. The error is usually there.

The `gh` CLI, GitHub's command-line tool from Day 2, does the same from your terminal:

- `gh run list` shows recent runs and their status.
- `gh run watch` follows a run live until it finishes.
- `gh run view --log-failed` prints only the logs of failed steps.
- `gh run rerun --failed --debug` runs the failed jobs again with extra detail.

To get the extra detail on every run, set the repository variable `ACTIONS_STEP_DEBUG` to `true` with `gh variable set ACTIONS_STEP_DEBUG --body true` (Day 27 covers variables).

One warning belongs with logs. Anyone who can read the repository can read its logs, so never print a secret, such as a password or a token, not even for a quick test. All of this runs on GitHub's machines, which raises a fair question: who pays?"""

S[6]["h"] = "What it costs, and where it stops"
S[6]["body"] = """Standard GitHub-hosted runners are free in public repositories, with no minute limit. Private repositories draw from a monthly allowance that GitHub now counts in dollars. At the time of writing:

- The Free plan includes $12 of compute a month for private repositories.
- A Linux x64 minute costs $0.006, so $12 buys about 2,000 minutes.
- Linux arm64 is a little cheaper ($0.005 a minute), and macOS is about ten times dearer ($0.062).
- Usage is charged to the repository owner, not to the person who pushed.

Check the [current billing page](https://docs.github.com/en/billing/concepts/product-billing/github-actions) before you rely on these numbers. My advice for this course: keep `hello-devops` public (it holds no secrets), and every run is free.

The limits worth knowing:

- A job may run for at most 6 hours. Set `timeout-minutes` much lower, because a hung job otherwise waits the full 360 minutes.
- The Free plan runs up to 20 jobs at the same time, at most 5 of them on macOS.
- Logs and artifacts are kept for 90 days by default. Artifacts are files a run saves for later.

The biggest limit costs no money. The station is wiped after every job, so each run downloads and installs the same packages again from nothing. And today's workflow tests one Python version, with no style checks and no image build. Day 25 turns it into a real pipeline, with a cache that remembers and a matrix that tests several versions."""

L["closing"] = """We started with a café owner who skipped one taste on a busy day. Your repository now has a taster that never skips: every push starts a fresh machine, runs pytest, and posts a tick or a cross.

In your own Actions tab, open the red run from the hands-on task and find the line where the assertion failed. That line is exactly what the taster saw.

Next, we'll grow this one-job workflow into a real CI pipeline. Why does every run take as long as the first one, and how do we test two Python versions at once?"""

drop_extras(L)

set_list(L["worked"]["steps"], "say", [
    "Work on a branch, a separate line of changes, so your experiments stay off `main`. The folder name matters: GitHub only reads workflows from `.github/workflows/`. The last line opens the new file in VS Code.",
    "Paste `hello.yml` from the Files section. It runs on every push and from a button, sets `env` at three levels, and has two jobs. The first job prints facts about the run. Notice that the branch name goes through `env` before the script uses it.",
    "Commit and push. The push is the event, so the run starts within seconds. `gh run watch` asks which run to follow and stays with it until it ends. Both jobs start at the same time, like two cooks with two tickets.",
    "Open the run with `gh run view --web`, click the `say-hello` job, and expand the first step. You see lines like these, with your own commit ID. Line 1 comes from the workflow `env`, line 2 from the job `env`, and the last two from the step `env`.",
    "Compare the processor in the two jobs. In `say-hello`, the step Look around the runner starts with the first line below, then shows the Python and Docker versions that come with the runner. The `on-arm` job prints the second line: `aarch64` is the name Linux uses for arm64. Same workflow, two kinds of machine, and only the `runs-on` label differs.",
    "That was practice. Delete the branch here and on GitHub, so `hello.yml` never runs again.",
])

L["task"]["steps"] = [
    "On a new branch called `add-ci`, create `.github/workflows/ci.yml`.",
    "Write a workflow named `ci` that runs on `push` and `workflow_dispatch`, with one job called `test` on `ubuntu-latest`.",
    "Add steps that check out the code, set up Python 3.14 with `actions/setup-python@v7`, install `requirements-dev.txt`, and run `pytest -q`.",
    "Push the branch and follow the run with `gh run watch` until you see a green tick.",
    "Break a test on purpose: change the expected message in `test_app.py`, then commit and push.",
    "Watch the run turn red, and find the failing assertion with `gh run view --log-failed`.",
    "Fix the test, push again, and see the run turn green.",
    "Open a PR, merge it into `main`, and press Run workflow for `ci` in the Actions tab (or run `gh workflow run ci.yml`).",
]
L["task"]["hints"] = [
    "Your file has the same shape as `hello.yml`. Only the steps differ.",
    "Quote the Python version: `\"3.14\"`.",
    "If no run appears at all, check the folder name and the indentation.",
]
L["task"]["done_when"] = ("You are done when the Actions tab shows a red run for the broken test, a green run after the fix, "
                          "and a green run you started with the Run workflow button.")

L["explain_back"]["answer"] = ("When I push, GitHub creates a push event for my repository. "
                               "Every workflow in .github/workflows that lists push under on starts a run. "
                               "Each job gets a fresh runner, a virtual machine that runs the job's steps in order, such as checkout, setup-python and pytest. "
                               "If every step exits with code 0, the job passes and I see a green tick; a non-zero exit code fails the step, the job and the run.")

L["recap"] = [
    "Workflows are YAML files in .github/workflows, and the events listed under on start them.",
    "A workflow has jobs, a job has steps, and each job runs on its own fresh runner.",
    "runs-on picks the machine: ubuntu-latest for x64, ubuntu-24.04-arm for arm64 like your Mac.",
    "run executes shell commands; uses calls a published action, with inputs under with, and checkout comes first.",
    "A non-zero exit code fails the step, the job and the run; debug from the first red step.",
    "The limit: every run starts from nothing and tests one setup, so Day 25 adds caching and a matrix.",
]

C = L["check"]
C[0]["why"] = "Cron fields start with the minute, then the hour, so \"0 2 * * *\" is 02:00. workflow_dispatch adds the button."
C[1]["why"] = "By default, a non-zero exit code fails the step and stops the job, so later steps are skipped."
C[2]["why"] = "ubuntu-24.04-arm runs Linux on arm64, the processor family of Apple Silicon. ubuntu-latest is x64."

I = L["interview"]
I[0]["a"] = ("A job is a group of steps that runs on one runner. The steps in a job run in order and share the same machine and files. "
             "Different jobs run on different runners, in parallel by default, and share nothing unless you pass artifacts or outputs. "
             "You use `needs` to make one job wait for another.")
I[1]["a"] = ("GitHub-hosted runners are fresh, patched virtual machines that you do not maintain, and they are free for public repos. "
             "Self-hosted runners make sense when you need special hardware, access to a private network, or lower cost at very high volume. "
             "In exchange, you patch, scale and secure them yourself. "
             "GitHub recommends self-hosted runners only for private repositories, because a pull request from a fork could run code on your machine.")

L["deeper"]["body"] = """A `run:` step looks like a list of commands, but GitHub saves it as a script file and runs that file with a shell. The shell and its options decide how failures behave.

On Linux runners, if you do not set `shell`, GitHub runs `bash -e {0}`, where `{0}` is the script file. The `-e` flag is the `set -e` from Part 1: the script stops at the first command that fails, and the step fails with that exit code.

If you write `shell: bash` yourself, GitHub runs `bash --noprofile --norc -eo pipefail {0}` instead. The extra `pipefail` changes how pipes fail. A pipe, written `|`, sends one command's output into the next command. Without `pipefail`, a pipe returns the exit code of its last command. So `pytest -q | tee test.log` passes even when tests fail, because `tee` worked fine. With `pipefail`, the failing `pytest` fails the whole pipe, and the step goes red.

To set the shell once for every step, add a `defaults` block at the top of the workflow with `run: shell: bash` inside it. Many teams do this to get `pipefail` everywhere, and I would too.

Some more facts that save debugging time:

- Each `run:` step starts a new shell. A variable you `export` in one step is gone in the next one.
- To hand a value to later steps, append a line like `NAME=value` to the file named in `$GITHUB_ENV` (Day 26 covers this properly).
- All steps in a job share one disk, so a file written in step 2 is still there in step 3.
- `working-directory: app` runs a step inside a subfolder.
- `continue-on-error: true` lets a step fail without failing the job. Use it rarely, because it hides problems.

One more oddity, for when you read workflow files with your own scripts. Python's PyYAML library follows an old YAML rule and reads the key `on` as the boolean `true`. GitHub's own reader does not, so your workflow is fine; your script just has to look for `True` instead of `"on"`.

The supported shells table in the [workflow syntax reference](https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax) lists the exact command line for each shell. If a script works on your laptop and fails in CI, check these flags early."""

save(path, P)
print("d24 written")
