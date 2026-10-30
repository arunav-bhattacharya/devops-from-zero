"""Day 18: GitHub Actions: your first workflow (first edition d10)."""
from common import T, box, line, link, refs, scratch, sources, svg

DIAGRAM = svg(230, "A push event starts the ci.yml workflow, whose test job runs checkout, setup-python and pytest in order on a fresh runner", [
    box(8, 93, 72, 44, "bxo", "push"),
    line(80, 115, 100, 115),
    box(104, 93, 88, 44, "bx", "ci.yml"),
    line(192, 115, 212, 115),
    box(216, 93, 104, 44, "bxt", "job: test"),
    '<text x="44" y="156" class="ts" font-size="11" text-anchor="middle">event</text>',
    '<text x="148" y="156" class="ts" font-size="11" text-anchor="middle">workflow</text>',
    '<text x="268" y="156" class="ts" font-size="11" text-anchor="middle">fresh VM</text>',
    line(320, 115, 376, 42, dashed=True, arrow=False),
    line(320, 115, 376, 115, dashed=True, arrow=False),
    line(320, 115, 376, 188, dashed=True, arrow=False),
    box(376, 20, 168, 44, "bxp", "1 checkout"),
    box(376, 93, 168, 44, "bxp", "2 setup-python"),
    box(376, 166, 168, 44, "bxp", "3 pytest"),
    line(460, 64, 460, 89),
    line(460, 137, 460, 162),
])

S1 = T("""
You describe a task in a YAML file, and GitHub runs it when something happens in your repository. That is GitHub Actions, the automation built into GitHub. CI is its most common use. It can also publish releases, label issues or run a check every night.

The pieces fit inside each other. From the outside in:

1. An event happens, for example you push a commit.
2. GitHub finds every **workflow** that listens for that event and starts a run of each one.
3. A run starts one or more jobs. Jobs run in parallel unless one needs another.
4. Each job gets a runner, a machine that executes the job's steps in order.
5. Each step is a shell command or a ready-made action.

A step fails when its command ends with a non-zero exit code, the same exit codes you met in Part 1. The job stops there and is marked failed, and so is the run. `pytest` exits with 1 when a test fails, so one failing test turns the whole run red.

That is the whole trick behind CI. Tools exit non-zero when something is wrong, and a machine reads the exit code for you on every change.
""")

S2 = T("""
Workflows live in `.github/workflows/` at the root of your repository. GitHub treats every `.yml` or `.yaml` file there as a workflow. Get the folder name exactly right: a file in `.github/workflow/` (no s) is ignored without any warning. These top-level keys come up most:

- `name`: the label shown in the Actions tab.
- `on`: the events that start the workflow.
- `env`: environment variables for all jobs (optional).
- `jobs`: a map from job IDs, such as `test`, to job settings.

Inside a job, `runs-on` picks the runner and `steps` lists the work. Give each step a `name`, so the log is easy to read.

YAML trips most people up at first. These are the traps that bite in workflows:

- Indentation carries meaning. Use spaces, never tabs.
- A list item starts with a dash and a space.
- Versions need quotes: YAML reads `3.10` as the number 3.1, so write `"3.10"`.
- A plain value cannot contain a colon followed by a space. `run: echo "Result: ok"` is a YAML error.

I hit the last one while testing this lesson. The error says "mapping values are not allowed in this context" and points at the colon. Fix it with `run: |` and the command on the next line. The VS Code YAML extension from Day 2 and actionlint (Day 19) catch all four before you push.
""")

S3 = T("""
The `on` key lists the events that start a workflow. You will use these four most:

- `push`: commits or tags are pushed. Filters such as `branches: [main]` or `tags: ["v*"]` narrow it down.
- `pull_request`: a PR is opened, gets new commits, or is reopened.
- `workflow_dispatch`: adds a Run workflow button to the Actions tab.
- `schedule`: runs on a timer written in cron syntax.

Filters also work on file paths. `paths: ["app.py"]` runs the workflow only when that file changed. Day 19 shows the trap that comes with path filters.

A `pull_request` run tests a temporary merge of your branch into the target branch, so it catches clashes with other people's work. The Run workflow button only appears once the workflow file is on the default branch.

Schedules have the most rules. They use UTC unless you set a time zone, and the shortest interval is every 5 minutes. They run only on the default branch, and they can start late when GitHub is busy, especially at the start of each hour. In a public repository, GitHub switches them off after 60 days without activity.

You can list several events at once. `on: [push, workflow_dispatch]` runs on every push and also gives you the button.
""")

S4 = T("""
Runners come in two kinds:

- GitHub-hosted: a fresh virtual machine for every job, deleted afterwards. It comes with git, Docker, Python, jq and many other tools.
- Self-hosted: a machine you run yourself and register with GitHub. It helps with special hardware or a private network, but patching and securing it is your job.

You pick a GitHub-hosted runner by its label in `runs-on`:

- `ubuntu-latest`: Linux on x64 (Intel or AMD) processors. Today it means Ubuntu 24.04. The label moves to newer versions over time, so write `ubuntu-24.04` when you need it fixed.
- `ubuntu-24.04-arm`: Linux on arm64, the same processor family as your Apple Silicon Mac.
- `windows-latest` and `macos-latest`: Windows, and macOS on Apple M1 machines.

In public repositories the standard Linux runners have 4 CPUs and 16 GB of memory. Private repositories get 2 CPUs and 8 GB.

Never attach a self-hosted runner to a public repository. Anyone can open a pull request, and a workflow could then run a stranger's code on your machine. GitHub's own docs recommend self-hosted runners only for private repositories. For this course, GitHub-hosted runners are all you need.
""")

S5 = T("""
A step does its work in one of two ways.

With `run:`, it executes shell commands. On Linux the default is bash with `-e`, so the script stops at the first failing command. For several commands, write `run: |` and put one command per line below it.

With `uses:`, it calls an action: packaged code that someone published, such as `actions/checkout@v7`. The part after `@` is the version, usually a git tag. You pass inputs to the action under `with:`, for example `python-version: "3.14"` for `actions/setup-python@v7`.

Each runner starts empty. Your code is not on it until a step puts it there, so nearly every job begins with `actions/checkout`, which copies your repository into the job's working folder. Forget it and the next step fails because `requirements-dev.txt` does not exist.

An action is other people's code running inside your job. Prefer actions from GitHub (`actions/...`) and from the tool's own company (`docker/...`), and look at an action's repository before you use it. Day 21 shows how to pin an action so its code cannot change under you.
""")

S6 = T("""
Workflows pass settings with environment variables, set with `env` at three levels: the whole workflow, one job, or one step. The most specific level wins, so a step's value beats the job's value. GitHub also sets default variables in every step, such as `GITHUB_SHA` (the commit) and `GITHUB_REF_NAME` (the branch or tag). Copy values such as the branch name into `env` and use `"$BRANCH"` in scripts; Day 20 explains why that habit matters.

Every run shows up in your repository's Actions tab. Click a run to see a graph of its jobs, then click a job to see each step's log. A green tick means success, a red cross means failure, and a grey icon means skipped or cancelled. When a run fails, open the first red step and read its last lines. The error is usually there.

The `gh` CLI does the same from your terminal:

- `gh run list` shows recent runs and their status.
- `gh run watch` follows a run live until it finishes.
- `gh run view --log-failed` prints only the logs of failed steps.
- `gh run rerun --failed --debug` runs the failed jobs again with extra detail.

To get the extra detail on every run, set the repository variable `ACTIONS_STEP_DEBUG` to `true`. Anyone who can read the repository can read its logs, so never print a secret, not even for a quick test.
""")

S7 = T("""
Standard GitHub-hosted runners are free in public repositories, with no minute limit. Private repositories draw from a monthly allowance that GitHub now counts in dollars. At the time of writing:

- The Free plan includes $12 of compute a month for private repositories.
- A Linux x64 minute costs $0.006, so $12 buys about 2,000 minutes.
- Linux arm64 is a little cheaper ($0.005 a minute), and macOS is about ten times dearer ($0.062).
- Usage is charged to the repository owner, not to the person who pushed.

Check the {billing} before you rely on these numbers. My advice for this course: keep `hello-devops` public (it holds no secrets), and every run is free.

The limits worth knowing:

- A job may run for at most 6 hours. Set `timeout-minutes` much lower, because a hung job otherwise waits the full 360 minutes.
- The Free plan runs up to 20 jobs at the same time, at most 5 of them on macOS.
- Logs and artifacts are kept for 90 days by default.
""").format(billing=link("billing", "current billing page"))

LESSON = {
    "id": "d18",
    "title": "GitHub Actions: your first workflow",
    "minutes": 45,
    "goal": "By the end you can write a workflow file, start it with a push or a button, pick a runner, read its logs, and run pytest on every push.",
    "guess": {
        "q": "A job in your workflow says `runs-on: ubuntu-latest`. Where does it run?",
        "options": [
            "On your laptop, inside Docker Desktop",
            "On the GitHub server that stores your code",
            "On the same server as last time, with its old files",
            "On a fresh virtual machine made just for this job",
        ],
        "answer": 3,
        "why": "GitHub-hosted runners are brand-new virtual machines for every job, so nothing from the last run is left. That is why almost every job starts with checkout and setup steps.",
    },
    "terms": [
        {"term": "Workflow", "plain": "A YAML file in .github/workflows that describes an automated process."},
        {"term": "Event", "plain": "Something that starts a workflow, such as a push, a pull request or a timer."},
        {"term": "Workflow run", "plain": "One execution of a workflow, with its own logs and its own result."},
        {"term": "Job", "plain": "A group of steps that runs on one runner; jobs run in parallel unless linked."},
        {"term": "Step", "plain": "One task in a job: a shell command (run) or a ready-made action (uses)."},
        {"term": "Runner", "plain": "The machine that runs a job; GitHub-hosted runners are fresh virtual machines."},
        {"term": "Action", "plain": "A published, reusable step such as actions/checkout, called with uses."},
    ],
    "sections": [
        {"h": "What GitHub Actions is", "body": S1, "refs": refs("understand", "skill_hello", "v_gh_actions")},
        {"h": "Anatomy of a workflow file", "body": S2, "refs": refs("syntax", "quickstart")},
        {"h": "Events: when a workflow runs", "body": S3, "refs": refs("events")},
        {"h": "Runners: the machines that run your jobs", "body": S4, "refs": refs("runners_ref", "hosted", "selfhosted")},
        {"h": "Steps: uses versus run", "body": S5, "refs": refs("find_actions", "v_nana")},
        {"h": "Environment variables, and reading runs and logs", "body": S6, "refs": refs("variables", "logs", "debug")},
        {"h": "What it costs, and the limits", "body": S7, "refs": refs("billing", "limits")},
    ],
    "analogy": "A workflow is like an order ticket in a restaurant kitchen. An order comes in (the event), a cook gets a clean, empty station (the runner) and follows the ticket line by line (the steps). Two cooks can work on two tickets at once (two jobs). When the dish is done, the station is wiped for the next order. The kitchen picture fails on leftovers: a kitchen keeps them, and a runner keeps nothing unless you save it as a cache or an artifact (Day 19).",
    "diagram": DIAGRAM,
    "diagram_caption": "A push starts the workflow; its job gets a fresh runner and runs the steps in order.",
    "worked": {
        "title": "Your first workflow: hello.yml",
        "steps": [
            {
                "say": "Work on a branch, so your experiments stay off `main`. The folder name matters: GitHub only reads workflows from `.github/workflows/`.",
                "code": T("""
                    cd ~/code/hello-devops
                    git switch -c try-actions
                    mkdir -p .github/workflows
                    code .github/workflows/hello.yml
                """),
                "lang": "bash",
            },
            {
                "say": "Paste `hello.yml` from the Files section. It runs on every push and from a button, sets `env` at three levels, and has two jobs. The first job prints facts about the run. Notice that the branch name goes through `env` before the script uses it.",
                "code": T("""
                    - name: Print facts about this run
                      env:
                        BRANCH: ${{ github.ref_name }}
                        EVENT: ${{ github.event_name }}
                      run: |
                        echo "$GREETING"
                        echo "$JOB_NOTE"
                        echo "Commit: ${{ github.sha }}"
                        echo "Branch or tag: $BRANCH"
                        echo "Started by: $EVENT"
                """),
                "lang": "yaml",
            },
            {
                "say": "Commit and push. The push is the event, so the run starts within seconds. `gh run watch` asks which run to follow and stays with it until it ends. Both jobs start at the same time.",
                "code": T("""
                    $ git add .github/workflows/hello.yml
                    $ git commit -m "Add a hello workflow"
                    $ git push -u origin try-actions
                    $ gh run watch
                """),
                "lang": "console",
            },
            {
                "say": "Open the run with `gh run view --web`, click the `say-hello` job, and expand the first step. You see lines like these, with your own commit ID. Line 1 comes from the workflow `env`, line 2 from the job `env`, and the last two from the step `env`.",
                "code": T("""
                    Hello from GitHub Actions
                    I run on a fresh virtual machine
                    Commit: 9f2c1e7d0b6a4c3e8f5a1b2c3d4e5f6a7b8c9d0e
                    Branch or tag: try-actions
                    Started by: push
                """),
                "lang": "text",
            },
            {
                "say": "Compare the CPU in the two jobs. In `say-hello`, the step Look around the runner starts with the first line below, then shows the Python and Docker versions that come with the runner. The `on-arm` job prints the second line: `aarch64` is the name Linux uses for arm64. Same workflow, two kinds of machine, and only the `runs-on` label differs.",
                "code": T("""
                    Linux x86_64
                    Linux aarch64
                """),
                "lang": "text",
            },
            {
                "say": "That was practice. Delete the branch here and on GitHub, so `hello.yml` never runs again.",
                "code": T("""
                    $ git switch main
                    $ git branch -D try-actions
                    $ git push origin --delete try-actions
                """),
                "lang": "console",
            },
        ],
    },
    "code": [
        {
            "lang": "yaml",
            "title": ".github/workflows/hello.yml (practice, deleted at the end)",
            "src": scratch("hello.yml"),
            "run": "git add .github/workflows/hello.yml && git commit -m \"Add a hello workflow\" && git push",
        },
        {
            "lang": "yaml",
            "title": ".github/workflows/ci.yml (Day 18 version)",
            "src": scratch("ci-day18.yml"),
            "run": "git add .github/workflows/ci.yml && git commit -m \"Run tests in CI\" && git push && gh run watch",
        },
    ],
    "commands": [
        {"cmd": "gh run list", "what": "Show the latest workflow runs and their status."},
        {"cmd": "gh run watch", "what": "Pick a run and follow it live until it finishes."},
        {"cmd": "gh run view --web", "what": "Open a run in the browser."},
        {"cmd": "gh run view --log-failed", "what": "Print the logs of only the failed steps of a run."},
        {"cmd": "gh run rerun --failed", "what": "Run the failed jobs of a run again."},
        {"cmd": "gh run rerun --failed --debug", "what": "Run the failed jobs again with step debug logging switched on."},
        {"cmd": "gh workflow list", "what": "List the workflows in this repository."},
        {"cmd": "gh workflow run ci.yml", "what": "Start a workflow that has `workflow_dispatch`, like pressing Run workflow."},
        {"cmd": "gh variable set ACTIONS_STEP_DEBUG --body true", "what": "Turn on step debug logging for every run (delete the variable to turn it off)."},
        {"cmd": "git push origin --delete try-actions", "what": "Delete a branch on GitHub."},
    ],
    "mistake": "If you save the workflow in the wrong folder, such as `.github/workflow/` or `github/workflows/`, GitHub ignores it. Nothing runs, and no error appears anywhere. The folder must be exactly `.github/workflows/` at the root of the repository; if no run appears after a push, check that path first.",
    "real_world": "PayLoop starts every new service from the same CI template, so tests run on every push from the service's first day. When everything is green, engineers rarely open the Actions tab. When a pull request shows a red cross, they go straight to the failed step's log, and they keep the pipeline under ten minutes so nobody is tempted to skip it.",
    "task": {
        "title": "Run pytest on every push",
        "steps": [
            "On a new branch called `add-ci`, create `.github/workflows/ci.yml`.",
            "Write a workflow named `ci` that runs on `push` and `workflow_dispatch`, with one job called `test` on `ubuntu-latest`.",
            "Add steps that check out the code, set up Python 3.14 with `actions/setup-python@v7`, install `requirements-dev.txt`, and run `pytest -q`.",
            "Push the branch and follow the run with `gh run watch` until you see a green tick.",
            "Break a test on purpose: change the expected message in `test_app.py`, then commit and push.",
            "Watch the run turn red, and find the failing assertion with `gh run view --log-failed`.",
            "Fix the test, push again, and see the run turn green.",
            "Open a PR, merge it into `main`, and press Run workflow for `ci` in the Actions tab (or run `gh workflow run ci.yml`).",
        ],
        "hints": [
            "Your file has the same shape as `hello.yml`. Only the steps differ.",
            "Quote the Python version: `\"3.14\"`.",
            "If no run appears at all, check the folder name and the indentation.",
        ],
        "done_when": "The Actions tab shows a red run for the broken test, a green run after the fix, and a green run you started with the Run workflow button.",
    },
    "explain_back": {
        "prompt": "Explain how a push turns into a green tick in GitHub Actions, in 3 to 4 sentences. Mention the event, workflow, job, runner and steps.",
        "answer": "When I push, GitHub creates a push event for my repository. Every workflow in .github/workflows that lists push under on starts a run. Each job gets a fresh runner, a virtual machine that runs the job's steps in order, such as checkout, setup-python and pytest. If every step exits with code 0, the job passes and I see a green tick; a non-zero exit code fails the step, the job and the run.",
    },
    "recap": [
        "Workflows are YAML files in .github/workflows, and the events listed under on start them.",
        "A workflow has jobs, a job has steps, and each job runs on its own fresh runner.",
        "runs-on picks the machine: ubuntu-latest for x64, ubuntu-24.04-arm for arm64 like your Mac.",
        "run executes shell commands; uses calls a published action, with inputs under with.",
        "A non-zero exit code fails the step, the job and the run; debug from the first red step.",
        "Standard runners are free in public repositories; private ones draw from a monthly dollar allowance.",
    ],
    "check": [
        {
            "q": "You want a workflow to run every night at 02:00 UTC and also from a button. Which on block fits?",
            "options": [
                "schedule with cron \"0 2 * * *\", plus workflow_dispatch",
                "push with branches: [nightly]",
                "pull_request with types: [scheduled]",
                "schedule with cron \"2 0 * * *\" only",
            ],
            "answer": 0,
            "why": "Cron fields start with the minute, then the hour, so \"0 2 * * *\" is 02:00. workflow_dispatch adds the button.",
        },
        {
            "q": "Job test has three steps. Step 2 runs pip install and exits with code 1. What happens?",
            "options": [
                "Step 3 still runs, and the job passes",
                "The job stops, is marked failed, and step 3 is skipped",
                "GitHub retries step 2 until it passes",
                "Only a warning appears, because install steps cannot fail",
            ],
            "answer": 1,
            "why": "By default, a non-zero exit code fails the step and stops the job.",
        },
        {
            "q": "A teammate's Docker build works on her Apple Silicon Mac and fails in CI on ubuntu-latest. You want CI to also build on the same kind of CPU as her Mac. Which runs-on label do you add?",
            "options": ["ubuntu-latest", "windows-latest", "ubuntu-slim", "ubuntu-24.04-arm"],
            "answer": 3,
            "why": "ubuntu-24.04-arm runs Linux on arm64, the processor family of Apple Silicon. ubuntu-latest is x64.",
        },
    ],
    "interview": [
        {
            "q": "What is the difference between a job and a step in GitHub Actions?",
            "a": "A job is a group of steps that runs on one runner. The steps in a job run in order and share the same machine and files. Different jobs run on different runners, in parallel by default, and share nothing unless you pass artifacts or outputs. You use `needs` to make one job wait for another.",
        },
        {
            "q": "When would you choose self-hosted runners over GitHub-hosted ones?",
            "a": "GitHub-hosted runners are fresh, patched virtual machines that you do not maintain, and they are free for public repos. Self-hosted runners make sense when you need special hardware, access to a private network, or lower cost at very high volume. In exchange, you patch, scale and secure them yourself. GitHub recommends self-hosted runners only for private repositories, because a pull request from a fork could run code on your machine.",
        },
    ],
    "deeper": {
        "minutes": 12,
        "body": T("""
            A `run:` step looks like a list of commands, but GitHub saves it as a script file and runs that file with a shell. The shell and its options decide how failures behave.

            On Linux runners, if you do not set `shell`, GitHub runs `bash -e {0}`, where `{0}` is the script file. The `-e` flag is the `set -e` from Part 1: the script stops at the first command that fails, and the step fails with that exit code.

            If you write `shell: bash` yourself, GitHub runs `bash --noprofile --norc -eo pipefail {0}` instead. The extra `pipefail` changes how pipes fail. Without it, a pipe returns the exit code of its last command. So `pytest -q | tee test.log` passes even when tests fail, because `tee` worked fine. With `pipefail`, the failing `pytest` fails the whole pipe, and the step goes red.

            To set the shell once for every step, add a `defaults` block at the top of the workflow with `run: shell: bash` inside it. Many teams do this to get `pipefail` everywhere, and I would too.

            Some more facts that save debugging time:

            - Each `run:` step starts a new shell. A variable you `export` in one step is gone in the next one.
            - To hand a value to later steps, append a line like `NAME=value` to the file named in `$GITHUB_ENV` (Day 20 covers this properly).
            - All steps in a job share one disk, so a file written in step 2 is still there in step 3.
            - `working-directory: app` runs a step inside a subfolder.
            - `continue-on-error: true` lets a step fail without failing the job. Use it rarely, because it hides problems.

            One more oddity, for when you parse workflow files with your own scripts. Python's PyYAML follows an old YAML rule and reads the key `on` as the boolean `true`. GitHub's own parser does not, so your workflow is fine; your script just has to look for `True` instead of `"on"`.

            The supported shells table in the {syntax} lists the exact command line for each shell. If a script works on your laptop and fails in CI, check these flags early.
        """).format(syntax=link("syntax", "workflow syntax reference")),
    },
    "sources": sources("understand", "syntax", "events", "runners_ref"),
}
