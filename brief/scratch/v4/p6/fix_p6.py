"""First-principles review of Part 6 (Days 23 to 27): exact prose replacements.
Run from the repo root: python3 brief/scratch/v4/p6/fix_p6.py
Each edit names a lesson, a field path and an exact old string that must occur once."""
import json
import pathlib

ORIG = pathlib.Path("brief/scratch/v4/orig/p6.json")  # always start from the original
PATH = pathlib.Path("content/p6.json")
data = json.loads(ORIG.read_text())
lessons = {L["id"]: L for L in data["lessons"]}

EDITS = [
    # ---------------- Day 23 ----------------
    ("d23", ("sections", 0, "body"),
     "Day 9 left you with a clean branch on your laptop. A pull request (PR) is the GitHub page that asks to merge it into `main`, and it is where the review and the CI checks meet. The loop most teams run:",
     "Day 9 left you with a clean branch on your laptop. You could merge it into `main` yourself and push. Then nobody else reads the change before it lands, and no test runs on it unless you ran one. A pull request (PR) fixes both. It is a page on GitHub that asks to merge your branch into `main`. Teammates review the diff there, and checks run on it: automatic tests that show a green tick or a red cross. Those checks are CI, explained later today, and Day 24 sets them up. The loop most teams run:"),
    ("d23", ("sections", 0, "body"),
     "counted from the merge base you met on Day 9.",
     "counted from the merge base you met on Day 9. Squash and merge, in step 7, turns all of the branch's commits into one new commit on `main`; Go deeper compares the three merge methods."),
    ("d23", ("sections", 0, "body"),
     "Two facts about CI on pull requests explain today's worked example. For a `pull_request` run, CI checks out a temporary merge of your branch into the current main, not your branch alone. And the checks run again only when the PR changes (opened, new commits, reopened), not when main moves. So a PR that was green yesterday may be red against today's main. The Update branch button on the PR brings main into your branch and runs CI again. While a PR has a merge conflict, its `pull_request` workflows do not run at all.",
     "Two facts about CI on pull requests explain today's worked example. First, GitHub builds a temporary merge commit of your branch into the current main, and CI tests that combination. Second, CI starts only when something happens to the PR itself: it is opened, gets new commits, or is reopened. A new commit on main is not an event on your PR, so nothing reruns, and a PR that was green yesterday may be red against today's main. The Update branch button brings main into your branch and runs CI again. While a PR has a merge conflict, GitHub cannot build that temporary merge, so CI does not run at all."),
    ("d23", ("sections", 1, "body"),
     "A review goes well when both sides do their part. As the author:",
     "CI runs the tests the author wrote. A reviewer catches what nobody thought to test, such as a missing error case or a name that will confuse the next reader. A review goes well when both sides do their part. As the author:"),
    ("d23", ("sections", 1, "body"),
     "Request changes only blocks the merge when a ruleset requires pull requests, and then it blocks until that same reviewer approves.",
     "Request changes only blocks the merge when a ruleset requires pull requests. A ruleset is a set of rules for a branch, such as \"main only changes through a reviewed PR\", and Day 25 builds one. With that rule on, Request changes blocks until that same reviewer approves."),
    ("d23", ("sections", 2, "body"),
     "A `CODEOWNERS` file maps paths to the people or teams responsible for them. When a PR changes",
     "On a bigger team, the author has to know who should look at each change. A new teammate who edits `infra/` may not know a platform team exists, and the change merges without the people who know that code. A `CODEOWNERS` file maps paths to the people or teams responsible for them. When a PR changes"),
    ("d23", ("sections", 2, "body"),
     "- GitHub reads the file from the PR's base branch, so a change to it counts only after it is merged.",
     "- GitHub reads the file from the PR's base branch, so a change to it counts only after it is merged. A PR cannot pick its own reviewers."),
    ("d23", ("sections", 4, "body"),
     "Continuous integration (CI) means everyone merges small changes often, and a server builds and tests every change automatically. You hear about a broken test minutes after you push, while you still remember what you changed.",
     "Continuous integration (CI), which Day 1 sketched, means everyone merges small changes often, and a server builds and tests every change automatically. Without it, people test on their own laptops, and the combined code first meets a test when someone tries to release. With CI you hear about a broken test minutes after you push, while you still remember what you changed. On GitHub, that server is a fresh virtual machine that GitHub starts for the test and deletes afterwards (Day 24)."),
    ("d23", ("sections", 4, "body"),
     "4. Deploy: release that image to staging, then to production.",
     "4. Deploy: release that image to staging (a copy of production for a last check), then to production."),
    ("d23", ("sections", 5, "body"),
     "Deploying means swapping the old version for the new one while users keep working. Four ways are common:",
     "Deploying means swapping the old version for the new one while users keep working. The naive way stops the old version, then starts the new one. Users get errors during the gap, and if the new version is broken, every user hits it at once. Four common ways avoid one or both problems:"),

    # ---------------- Day 24 ----------------
    ("d24", ("sections", 0, "body"),
     "You describe a task in a YAML file, and GitHub runs it when something happens in your repository. That is GitHub Actions, the automation built into GitHub. CI is its most common use. It can also publish releases, label issues or run a check every night.\n\nThe pieces fit inside each other. From the outside in:\n\n1. An event happens, for example you push a commit.\n2. GitHub finds every **workflow** that listens for that event and starts a run of each one.\n3. A run starts one or more jobs. Jobs run in parallel unless one needs another.\n4. Each job gets a runner, a machine that executes the job's steps in order.\n5. Each step is a shell command or a ready-made action.",
     "On Day 23, nothing tested a pull request unless you ran `pytest` on your laptop first. CI needs a machine that is nobody's laptop: one that runs the same commands for every push and posts the result on the commit. GitHub Actions, the automation built into GitHub, gives you that machine. You write the commands in a YAML file in your repository, and GitHub runs them when something happens there. CI is its most common use. It can also publish releases, label issues or run a check every night.\n\nA `git push` sets off this chain:\n\n1. GitHub records an event for your repository: a push of this commit to this branch.\n2. It reads `.github/workflows/` in the commit you pushed and starts a run of every **workflow** that listens for `push`.\n3. A run starts one or more jobs. Jobs run in parallel unless one needs another.\n4. For each job, GitHub starts a new virtual machine (Day 17), the runner. It comes with Ubuntu (or the system the job asks for) and common tools, but none of your files.\n5. The runner application, a program on that machine, runs the job's steps in order. Each step is a shell command or a ready-made action.\n6. The result, a green tick or a red cross, appears on the commit and its PR, and GitHub deletes the machine.\n\nSo your laptop takes no part, and no file survives from one job to the next unless you save it (Day 25 shows how)."),
    ("d24", ("sections", 1, "body"),
     "Workflows live in `.github/workflows/` at the root of your repository. GitHub treats",
     "Workflows are YAML, the `key: value` format of `compose.yaml` on Day 21, and they live in `.github/workflows/` at the root of your repository. GitHub treats"),
    ("d24", ("sections", 2, "body"),
     "Schedules have the most rules. They use UTC unless you set a time zone, and the shortest interval is every 5 minutes. They run only on the default branch, and they can start late",
     "Schedules have the most rules. A schedule is written in cron syntax: five fields for minute, hour, day of month, month and day of week, where `*` means every. So `\"30 6 * * 1\"` means 06:30 every Monday. Times are in UTC unless you set a time zone, and the shortest interval is every 5 minutes. A timer has no commit of its own, so schedules run on the latest commit of the default branch. They can start late"),
    ("d24", ("sections", 3, "body"),
     "Never attach a self-hosted runner to a public repository. Anyone can open a pull request, and a workflow could then run a stranger's code on your machine.",
     "Never attach a self-hosted runner to a public repository. Anyone can open a pull request, and a workflow could then run a stranger's code on your machine. Unlike a hosted runner, your machine is not wiped after each job unless you set that up, so whatever that code leaves behind waits for your next job."),
    ("d24", ("sections", 4, "body"),
     "The part after `@` is the version, usually a git tag. You pass inputs",
     "The part after `@` is the version, usually a git tag. The name before it is a GitHub repository, owner `actions` and repository `checkout`. When the job starts, the runner downloads that repository at that tag (the log shows it under Set up job), and your step runs its code. You pass inputs"),
    ("d24", ("sections", 4, "body"),
     "Each runner starts empty. Your code is not on it until a step puts it there, so nearly every job begins with `actions/checkout`, which copies your repository into the job's working folder.",
     "The runner starts with none of your files, so nearly every job begins with `actions/checkout`, which copies your repository into the job's working folder."),
    ("d24", ("sections", 5, "body"),
     "Copy values such as the branch name into `env` and use `\"$BRANCH\"` in scripts; Day 26 explains why that habit matters.",
     "The workflow file can also read these facts as expressions, such as `${{ github.ref_name }}`. GitHub replaces each `${{ ... }}` with its value before the step starts, and Day 26 covers expressions. The worked example copies the branch name into `env` and uses `\"$BRANCH\"` in the script; Day 26 explains why that habit matters."),
    ("d24", ("sections", 5, "body"),
     "To get the extra detail on every run, set the repository variable `ACTIONS_STEP_DEBUG` to `true`.",
     "To get the extra detail on every run, set the repository variable `ACTIONS_STEP_DEBUG` to `true` with `gh variable set ACTIONS_STEP_DEBUG --body true` (Day 27 covers variables)."),

    # ---------------- Day 25 ----------------
    ("d25", ("sections", 0, "body"),
     "The lab's pipeline has three jobs:",
     "The lab's pipeline splits the work into three jobs. Each job runs on its own runner and shows up on the PR as its own check, so you see at a glance which part broke:"),
    ("d25", ("sections", 0, "body"),
     "One more line, `permissions: contents: read`, makes the job's token read-only. Day 27 explains why that matters.",
     "One more line, `permissions: contents: read`, limits the token that GitHub gives every job for talking to your repository: it may read the code and change nothing. Day 27 explains why that matters."),
    ("d25", ("sections", 0, "body"),
     "Jobs run in parallel by default, so `lint` and both `test` jobs start at the same moment on separate runners.",
     "Jobs run in parallel by default, so `lint` and both `test` jobs start at the same moment."),
    ("d25", ("sections", 2, "body"),
     "A run can restore caches from its own branch and from `main`, but a cache saved by a pull request stays with that pull request. That is one reason CI also runs on pushes to `main`: it keeps a fresh cache that every new PR starts from.",
     "A run can restore caches from its own branch and from `main`. A cache saved by a pull request stays with that pull request, so no PR can plant files in the runs of `main` or of other PRs. Every new PR therefore starts from `main`'s cache, which is one reason CI also runs on pushes to `main`: it keeps that cache fresh."),
    ("d25", ("sections", 4, "body"),
     "Since June 2026, runs started by untrusted triggers, such as `pull_request_target` and `issue_comment`, may read the default branch's cache but not write to it.",
     "Since June 2026, runs started by untrusted triggers may read the default branch's cache but not write to it. These are events that someone outside the repository can set off, such as `pull_request_target` and `issue_comment`, but that run on your default branch (Day 27)."),
    ("d25", ("sections", 5, "body"),
     "Rulesets are more flexible, since several can apply at once, and anyone with read access can see them.",
     "Rulesets are more flexible, since several can apply at once, and anyone with read access can see them. When someone tries to merge, GitHub compares the checks on the PR's newest commit with the check names the ruleset requires."),
    ("d25", ("sections", 6, "body"),
     "It is handy for quick tries, but it does not match GitHub's runners exactly, so the real test is still a push.",
     "It is handy for quick tries. Each job runs in a container image you pick, which usually holds fewer tools than a GitHub runner, so the real test is still a push."),

    # ---------------- Day 26 ----------------
    ("d26", ("sections", 0, "h"),
     "Two moments: GitHub reads, then the runner runs",
     "Two moments: expressions first, then the shell"),
    ("d26", ("sections", 0, "body"),
     "A workflow is read at two different moments, by two different programs.\n\nFirst, GitHub reads the YAML on its own servers. It decides which jobs to start, works out every `${{ ... }}` expression, and pastes the results into the text. Only then does it send a job to a runner. Second, the runner runs your steps, and the shell expands `$VARIABLES` while each script runs.",
     "A workflow's text is filled in at two different moments, by different programs.\n\nFirst, the `${{ ... }}` expressions are worked out and their results pasted into the text. GitHub's servers do this for job-level keys, such as a job's `if:` and `runs-on:`, before any runner exists. The runner application does it for each step, just before that step starts. Second, the shell gets the finished script and expands `$VARIABLES` while it runs."),
    ("d26", ("sections", 2, "body"),
     "Every `if:` that does not contain a status function gets an invisible `success()` added to it. This rule catches almost everyone. `success()` is true only when everything before it succeeded.",
     "Every `if:` that does not contain a status function gets an invisible `success()` added to it. A step or job with no `if:` at all behaves the same way. `success()` is true only when everything before it succeeded. That is how a job stops at its first failure: the later steps are skipped, because their hidden `success()` is now false."),
    ("d26", ("sections", 3, "body"),
     "To pass a value along, you append it to one of the files the runner gives every step. Their paths are in environment variables:",
     "To pass a value along, you append it to one of the files the runner gives every step. When the step ends, the runner reads the file and records what you wrote. The paths are in environment variables:"),
    ("d26", ("sections", 3, "body"),
     "Under the job's `outputs:`, map a name to a step output. A job that `needs` it then reads",
     "Under the job's `outputs:`, map a name to a step output. When the job ends, the runner sends those outputs to GitHub, which hands them to every job that `needs` this one. That job reads"),
    ("d26", ("analogy",),
     "Go back to the kitchen from Day 24 and add a head chef, who prepares every ticket before service. Expressions are the blanks the chef fills in ahead of time (\"table 12, no salt\"), so the cook only ever sees the finished ticket.",
     "Go back to the kitchen from Day 24 and add a head chef. Expressions are the blanks on a ticket, such as \"table 12, no salt\". The chef fills in each line just before the cook reads it, so the cook only ever sees finished lines."),
    ("d26", ("analogy",),
     "A real chef can still walk over and change a ticket while the cook works. GitHub never changes an expression once the job has started.",
     "A real chef can still walk over and change a line while the cook works on it. GitHub never changes a step's expressions once that step has started."),

    # ---------------- Day 27 ----------------
    ("d27", ("sections", 0, "body"),
     "Passwords, API keys and cloud credentials must never sit in your code. GitHub stores them as secrets instead.",
     "Passwords, API keys and cloud credentials must never sit in your code. Everyone who can read the repository would see them, and git keeps them in its history even after you delete the line (Day 8). GitHub stores them as secrets instead."),
    ("d27", ("sections", 0, "body"),
     "GitHub hides known secret values in logs as `***`, but don't count on it. A secret that a script changes,",
     "The runner hides secret values in logs as `***`. It knows the exact values it received for this job and replaces every exact match in the log. Don't count on it, though. A secret that a script changes,"),
    ("d27", ("sections", 0, "body"),
     "rotate it: create a new one and revoke the old. Two kinds of runs cannot read your secrets at all: pull requests from forks, and pull requests opened by Dependabot.",
     "rotate it: create a new one and revoke the old.\n\nTwo kinds of runs cannot read your secrets at all: pull requests from forks (copies of your repository under another account, Day 9), and pull requests opened by Dependabot."),
    ("d27", ("sections", 1, "body"),
     "Every action in the job can use it, even if you never pass it on, so whatever the token may do, every action in the job may do.",
     "Every action in the job can use it, even if you never pass it on. `actions/checkout`, for example, uses it by default to fetch your code. So whatever the token may do, every action in the job may do."),
    ("d27", ("sections", 2, "body"),
     "2. The QEMU and Buildx actions prepare a builder that can produce amd64 (most servers) and arm64 (your Mac) images.",
     "2. QEMU, an emulator, lets this amd64 runner run arm64 build steps. Buildx then builds for amd64 (most servers) and arm64 (your Mac)."),
    ("d27", ("sections", 3, "body"),
     "An environment is a named deploy target, such as `staging` or `production`; Day 26 gave you a first look.",
     "Without a gate, every `v*` tag you push ships at once, even one you pushed by mistake. An environment is a named deploy target, such as `staging` or `production`; Day 26 gave you a first look."),
    ("d27", ("sections", 4, "body"),
     "4. AWS checks GitHub's signature and compares the facts with the role's trust policy.",
     "4. AWS checks the signature with GitHub's public key, then compares the facts with the role's trust policy."),
]

# Part-level flashcard that repeated the old model of when expressions are filled in.
PART_EDITS = [
    (("flashcards", 12, "back"),
     "Before the step runs, on GitHub's side, by pasting the value into the text.",
     "Before the shell sees the script: GitHub's servers fill in job-level ones, and the runner fills in each step's just before it starts."),
]


def get(obj, path):
    for p in path[:-1]:
        obj = obj[p]
    return obj, path[-1]


def apply(obj, path, old, new, where):
    parent, key = get(obj, path)
    text = parent[key]
    if new in text:
        print(f"already applied: {where} {path}")
        return
    n = text.count(old)
    assert n == 1, f"{where} {path}: old text found {n} times: {old[:70]!r}"
    parent[key] = text.replace(old, new)


for lid, path, old, new in EDITS:
    apply(lessons[lid], path, old, new, lid)
for path, old, new in PART_EDITS:
    apply(data, path, old, new, "part")

PATH.write_text(json.dumps(data, indent=1, ensure_ascii=False) + "\n")
print(f"applied {len(EDITS) + len(PART_EDITS)} edits")
