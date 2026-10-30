"""Part 4 extras: intro, recap, flashcards, resources, quiz."""
from common import R

INTRO = (
    "Until now you ran every check and build for hello-devops yourself. In this part GitHub runs them for you: "
    "every pull request is linted, tested and built, red ones cannot merge, and a version tag publishes a "
    "multi-platform image. It comes now because Part 3 gave you a tested app and a production-ready image, "
    "which is all a pipeline needs."
)

RECAP = [
    "Change code on small, short-lived branches, and merge through pull requests that a reviewer and CI both check.",
    "CI tests every change. With continuous delivery a person picks the release moment; with continuous deployment nobody does.",
    "A workflow is a YAML file in .github/workflows: an event starts it, and each job runs its steps on a fresh runner.",
    "The lab's ci.yml lints, tests on Python 3.13 and 3.14, keeps a JUnit report, builds the image and smoke-tests it.",
    "Caches make repeat runs fast but can vanish; artifacts are a run's outputs and need unique names.",
    "A ruleset on main with every required check stops red pull requests from merging.",
    "Expressions are filled in before the shell runs; every if gets a hidden success() unless you write a status function.",
    "Step outputs, job outputs and needs carry values between steps and jobs; composite actions and reusable workflows remove repetition.",
    "release.yml turns a v* tag into one amd64 and arm64 image in GHCR, behind an approval, with a least-privilege token.",
    "Pin third-party actions to commit SHAs, let Dependabot move the pins, and keep PR code away from pull_request_target.",
]

FLASHCARDS = [
    {"front": "Continuous delivery vs continuous deployment?", "back": "Delivery: every change is ready to release, and a person clicks release. Deployment: every passing change goes live on its own."},
    {"front": "What does 'build once, deploy many' mean?", "back": "Build the image one time, then promote that same digest through every environment."},
    {"front": "Merge vs rebase?", "back": "A merge joins two lines of work with a merge commit. A rebase replays your commits on top of the other branch, with new IDs."},
    {"front": "In semver 2.4.1, which number changes for a compatible bug fix?", "back": "PATCH, so the next version is 2.4.2."},
    {"front": "Where must workflow files live?", "back": "In .github/workflows/ at the repository root, as .yml or .yaml files."},
    {"front": "Which runner label gives you arm64 Linux, like an Apple Silicon Mac?", "back": "ubuntu-24.04-arm (ubuntu-latest is x64)."},
    {"front": "What do standard GitHub-hosted runners cost in a public repository?", "back": "Nothing. Private repositories draw from a monthly allowance, $12 on the Free plan."},
    {"front": "What does needs: [lint, test] do on a job?", "back": "The job waits for lint and test to succeed. If either fails, this job is skipped."},
    {"front": "Why not require only the last job of a needs chain?", "back": "If an earlier job fails, the last job is skipped, and GitHub counts a skipped check as passed."},
    {"front": "Why put paths-ignore on push but not on pull_request?", "back": "A required check skipped by a path filter stays Pending and blocks the merge."},
    {"front": "What goes into the setup-python pip cache key?", "back": "The OS and CPU, the Python version, and a hash of the requirements files."},
    {"front": "Cache vs artifact?", "back": "A cache speeds up future runs and can be evicted. An artifact is an output of one run that people download."},
    {"front": "When does GitHub work out ${{ }} expressions?", "back": "Before the step runs, on GitHub's side, by pasting the value into the text."},
    {"front": "What hidden condition does every if get?", "back": "success(), unless the if already uses a status function such as failure() or always()."},
    {"front": "How does a value get from job A to job B?", "back": "Step output via $GITHUB_OUTPUT, mapped in A's outputs, read in B as needs.A.outputs.name."},
    {"front": "Composite action vs reusable workflow?", "back": "A composite action is several steps used as one step. A reusable workflow is whole jobs called with on: workflow_call."},
    {"front": "What does permissions: contents: read at the top of a workflow do?", "back": "It makes the GITHUB_TOKEN read-only for code in every job, and sets every permission you don't list to none."},
    {"front": "Which permission lets a job request an OIDC token?", "back": "id-token: write. It grants no other access."},
    {"front": "Why pin an action to a full commit SHA?", "back": "Whoever controls the action's repository can move a tag to other code. A full commit SHA always means the same code."},
    {"front": "What is a pwn request?", "back": "A pull_request_target workflow that checks out and runs a pull request's code, so a stranger's code gets your secrets."},
]


def res(key, why, kind=None, title=None):
    t, url, k = R[key]
    return {"title": title or t, "url": url, "kind": kind or k, "why": why}


RESOURCES = [
    res("actions_docs", "The official home for everything in this part, from first workflow to security reference."),
    res("syntax", "The page you will open most: every key a workflow file can contain, with examples."),
    res("skill_hello", "A free, guided course that runs inside a real repository and checks your work as you go."),
    res("skill_reusable", "A short guided course that builds and calls a reusable workflow step by step."),
    res("progit", "The free book on git; the branching chapters explain merge and rebase with clear pictures."),
    res("fowler_ci", "The classic essay on what continuous integration really asks of a team, rewritten in 2023."),
    res("tbd", "A whole site on trunk-based development: short branches, feature flags and releasing from trunk."),
    res("v_nana", "A clear walk through workflows and a Docker build pipeline; the screens are from 2020, the ideas still hold."),
    res("v_kk2", "Matrix, concurrency, timeouts, contexts and expressions, shown on real workflows."),
    res("v_checkout_sec", "GitHub's own talk on the common security mistakes in workflows and how to avoid them."),
    res("actionlint", "The linter that catches typos, bad expressions and script injection before you push."),
    res("secure_use", "GitHub's checklist for secrets, tokens, third-party actions and untrusted input."),
]

QUIZ = [
    {
        "q": "A colleague's branch has lived for three weeks and touches 40 files. What problem is most likely at merge time?",
        "options": [
            "Big merge conflicts and a review nobody can check well",
            "GitHub refuses branches older than two weeks",
            "The tags on main move to the branch",
            "CI stops running on old branches",
        ],
        "answer": 0,
        "why": "Branches that live long and grow big drift away from main. Conflicts pile up, and reviewers can only skim.",
    },
    {
        "q": "Which event lets you start a workflow with a button in the Actions tab?",
        "options": ["schedule", "repository_dispatch", "workflow_dispatch", "pull_request"],
        "answer": 2,
        "why": "workflow_dispatch adds the Run workflow button, once the workflow file is on the default branch.",
    },
    {
        "q": "Why does the lab's ci.yml put the Python version in the artifact name?",
        "options": [
            "GitHub sorts artifacts by Python version",
            "upload-artifact only accepts names with numbers",
            "It makes the pip cache key match",
            "Each matrix job needs a unique artifact name",
        ],
        "answer": 3,
        "why": "Each matrix job uploads its own report, and two artifacts in one run cannot have the same name.",
    },
    {
        "q": "A PR run on branch `fix-typo` looks for a pip cache. Where can the cache it restores come from?",
        "options": [
            "Any branch in the repository, newest first",
            "Its own pull request or the default branch",
            "Only caches made on your laptop",
            "Other open pull requests on the same base",
        ],
        "answer": 1,
        "why": "Runs restore caches from their own scope and from the default (or base) branch. A cache saved by one pull request is not shared with others.",
    },
    {
        "q": "In the lab's build job, the step `Show the app's logs` has `if: ${{ failure() && steps.smoke.outcome == 'failure' }}`. The image build fails. Does the logs step run?",
        "options": [
            "Yes, because failure() is true",
            "Yes, because logs steps always run",
            "No, because the smoke test was skipped, not failed",
            "No, because failure() only works at job level",
        ],
        "answer": 2,
        "why": "failure() is true, but the smoke step never ran, so its outcome is skipped and the second half is false.",
    },
    {
        "q": "You want three test jobs in hello-devops to share the same five setup steps. Which tool fits best?",
        "options": [
            "A composite action in .github/actions",
            "A reusable workflow per test job",
            "A schedule trigger",
            "A new repository for the steps",
        ],
        "answer": 0,
        "why": "Shared steps inside a job are what composite actions are for. A reusable workflow replaces whole jobs.",
    },
    {
        "q": "In release.yml, which permission lets the GITHUB_TOKEN push images to GHCR?",
        "options": ["contents: write", "packages: write", "id-token: write", "actions: write"],
        "answer": 1,
        "why": "GHCR is part of GitHub Packages, so the token needs packages: write to push there.",
    },
    {
        "q": "Every production release must wait for a human. The repository is public, on the Free plan. What do you use?",
        "options": [
            "A wait timer of 60 minutes",
            "A repository secret named APPROVAL",
            "A schedule trigger",
            "An environment with required reviewers",
        ],
        "answer": 3,
        "why": "Required reviewers on an environment pause the job until one of them approves.",
    },
    {
        "q": "A CI step ends with `grep ERROR app.log`, and the log contains no errors. What happens to the step?",
        "options": [
            "It passes, because no errors were found",
            "It fails, because grep exits with 1 when nothing matches",
            "It passes with a warning about the empty result",
            "It fails, because grep needs sudo",
        ],
        "answer": 1,
        "why": "grep exits with 1 when it finds no match, and any non-zero exit code fails the step.",
        "from": "Part 1",
    },
    {
        "q": "You start hello-devops with `python app.py` and run `curl localhost:8000` in the same second. curl says 'Connection refused'; two seconds later it works. What did the first error tell you?",
        "options": [
            "A firewall on your Mac blocked port 8000 for a moment",
            "DNS could not resolve the name localhost yet",
            "Nothing listened on port 8000 yet; the app was starting",
            "The request timed out because the network was slow",
        ],
        "answer": 2,
        "why": "Connection refused means the machine answered but no process listened on the port yet. That is why the lab's smoke test retries for a few seconds.",
        "from": "Part 2",
    },
]
