#!/usr/bin/env python3
"""Build content/p3.json: Part 3, CI/CD with GitHub Actions (d09 to d12).

Run: python3 brief/scratch/p3/build_p3.py
Lab files (ci.yml, release.yml, dependabot.yml, PR template) are read from
labs/hello-devops so the lesson code always matches the tested lab.
"""
import json
import pathlib
import textwrap

ROOT = pathlib.Path(__file__).resolve().parents[3]
LAB = ROOT / "labs/hello-devops"
OUT = ROOT / "content/p3.json"


def T(s):
    """Dedent and strip a triple-quoted block."""
    return textwrap.dedent(s).strip("\n").rstrip()


def lab(path):
    return (LAB / path).read_text().rstrip("\n")


# ---------------------------------------------------------------- svg helpers
SVG_ITEMS = []  # (kind, x1, y1, x2, y2, label) for overlap checks


def svg(h, label, parts):
    return (f'<svg viewBox="0 0 560 {h}" xmlns="http://www.w3.org/2000/svg" role="img" '
            f'aria-label="{label}">' + "".join(parts) + "</svg>")


def box(x, y, w, h, cls, text):
    assert w >= 8 * len(text) + 24, f"box too narrow for {text!r}"
    tcls = "t" if cls == "bx" else "tk"
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="10" class="{cls}"/>'
            f'<text x="{x + w / 2:g}" y="{y + h / 2 + 5:g}" class="{tcls}" font-size="13" '
            f'text-anchor="middle">{text}</text>')


def cap(x, y, text):
    return f'<text x="{x}" y="{y}" class="ts" font-size="11" text-anchor="middle">{text}</text>'


def line(x1, y1, x2, y2, dashed=False, arrow=True):
    cls = "lnd" if dashed else "ln"
    m = ' marker-end="url(#ar)"' if arrow else ""
    return f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" class="{cls}"{m}/>'


D09 = svg(210, "A change moves from a branch to a pull request with CI checks and review, then merges to main and gets a version tag", [
    box(8, 24, 88, 44, "bx", "Branch"),
    line(96, 46, 120, 46),
    box(124, 24, 128, 44, "bxo", "Pull request"),
    line(252, 46, 276, 46),
    box(280, 24, 136, 44, "bxt", "Merge to main"),
    line(416, 46, 440, 46),
    box(444, 24, 108, 44, "bxg", "Tag v1.2.0"),
    cap(52, 88, "short-lived"),
    cap(348, 88, "main stays green"),
    cap(498, 88, "a fixed release"),
    box(96, 128, 112, 44, "bxt", "CI checks"),
    box(228, 128, 120, 44, "bxp", "Code review"),
    line(152, 128, 170, 72, dashed=True),
    line(288, 128, 220, 72, dashed=True),
    cap(152, 192, "runs on every push"),
    cap(288, 192, "a teammate reads it"),
])

D10 = svg(230, "A push event starts the ci.yml workflow, whose test job runs checkout, setup-python and pytest in order on a fresh runner", [
    box(8, 93, 72, 44, "bxo", "push"),
    line(80, 115, 100, 115),
    box(104, 93, 88, 44, "bx", "ci.yml"),
    line(192, 115, 212, 115),
    box(216, 93, 104, 44, "bxt", "job: test"),
    cap(44, 156, "event"),
    cap(148, 156, "workflow"),
    cap(268, 156, "fresh VM"),
    line(320, 115, 376, 42, dashed=True, arrow=False),
    line(320, 115, 376, 115, dashed=True, arrow=False),
    line(320, 115, 376, 188, dashed=True, arrow=False),
    box(376, 20, 168, 44, "bxp", "1 checkout"),
    box(376, 93, 168, 44, "bxp", "2 setup-python"),
    box(376, 166, 168, 44, "bxp", "3 pytest"),
    line(460, 64, 460, 89),
    line(460, 137, 460, 162),
])

D11 = svg(210, "A pull request starts two test jobs, one per Python version; the build job needs both; the merge is allowed only when all checks are green", [
    box(8, 83, 128, 44, "bxo", "Pull request"),
    line(136, 105, 172, 50),
    line(136, 105, 172, 160),
    box(176, 24, 112, 44, "bxt", "test 3.13"),
    box(176, 142, 112, 44, "bxt", "test 3.14"),
    cap(232, 109, "matrix: 2 jobs"),
    line(288, 46, 324, 98),
    line(288, 164, 324, 112),
    box(328, 83, 88, 44, "bxt", "build"),
    cap(372, 146, "needs: test"),
    line(416, 105, 444, 105),
    box(448, 83, 104, 44, "bxg", "Can merge"),
    cap(500, 146, "all checks green"),
])

D12 = svg(200, "Pushing a version tag waits for approval in the production environment, then builds amd64 and arm64 images and pushes them to ghcr.io using a short-lived GITHUB_TOKEN", [
    cap(62, 30, "you push"),
    cap(190, 30, "production env"),
    cap(328, 30, "amd64 + arm64"),
    cap(484, 30, "1.0.0, sha, latest"),
    box(8, 42, 108, 44, "bxo", "Tag v1.0.0"),
    line(116, 64, 136, 64),
    box(140, 42, 100, 44, "bxp", "Approval"),
    line(240, 64, 260, 64),
    box(264, 42, 128, 44, "bxt", "Build + push"),
    line(392, 64, 412, 64),
    box(416, 42, 136, 44, "bxg", "ghcr.io"),
    box(264, 136, 128, 40, "bx", "GITHUB_TOKEN"),
    line(328, 136, 328, 90, dashed=True),
    cap(190, 161, "short-lived"),
    cap(470, 161, "packages: write"),
])

# ---------------------------------------------------------------- links
GH = "https://docs.github.com/en/"
R = {
    "about_git": ("About Git", GH + "get-started/using-git/about-git", "docs"),
    "conflict_cli": ("Resolving a merge conflict using the command line", GH + "pull-requests/how-tos/merge-and-close-pull-requests/resolving-a-merge-conflict-using-the-command-line", "docs"),
    "skill_conflicts": ("GitHub Skills: Resolve merge conflicts (hands-on course)", "https://github.com/skills/resolve-merge-conflicts", "read"),
    "about_prs": ("About pull requests", GH + "pull-requests/get-started/about-pull-requests", "docs"),
    "review_qs": ("Reviewing pull requests quickstart", GH + "pull-requests/get-started/reviewing-pull-requests-quickstart", "docs"),
    "gh_flow": ("GitHub flow", GH + "get-started/using-github/github-flow", "docs"),
    "merge_methods": ("About merge methods on GitHub", GH + "repositories/configuring-branches-and-merges-in-your-repository/configuring-pull-request-merges/about-merge-methods-on-github", "docs"),
    "ci": ("About continuous integration", GH + "actions/get-started/continuous-integration", "docs"),
    "cd": ("About continuous deployment", GH + "actions/get-started/continuous-deployment", "docs"),
    "rollouts": ("Argo Rollouts: blue/green and canary for Kubernetes", "https://github.com/argoproj/argo-rollouts", "read"),
    "sre": ("Google's SRE book (see the release engineering chapter)", "https://sre.google/sre-book/table-of-contents/", "read"),
    "semver": ("Semantic Versioning 2.0.0 specification", "https://github.com/semver/semver/blob/master/semver.md", "read"),
    "releases": ("About releases", GH + "repositories/releasing-projects-on-github/about-releases", "docs"),
    "understand": ("Understanding GitHub Actions", GH + "actions/get-started/understand-github-actions", "docs"),
    "quickstart": ("GitHub Actions quickstart", GH + "actions/get-started/quickstart", "docs"),
    "skill_hello": ("GitHub Skills: Hello GitHub Actions (hands-on course)", "https://github.com/skills/hello-github-actions", "read"),
    "syntax": ("Workflow syntax for GitHub Actions", GH + "actions/reference/workflows-and-actions/workflow-syntax", "docs"),
    "events": ("Events that trigger workflows", GH + "actions/reference/workflows-and-actions/events-that-trigger-workflows", "docs"),
    "hosted": ("GitHub-hosted runners", GH + "actions/concepts/runners/github-hosted-runners", "docs"),
    "billing": ("GitHub Actions billing", GH + "billing/concepts/product-billing/github-actions", "docs"),
    "contexts": ("Contexts reference", GH + "actions/reference/workflows-and-actions/contexts", "docs"),
    "variables": ("Variables reference", GH + "actions/reference/workflows-and-actions/variables", "docs"),
    "secure_use": ("Secure use reference", GH + "actions/reference/security/secure-use", "docs"),
    "logs": ("Using workflow run logs", GH + "actions/how-tos/monitor-workflows/use-workflow-run-logs", "docs"),
    "use_jobs": ("Using jobs in a workflow (needs)", GH + "actions/how-tos/write-workflows/choose-what-workflows-do/use-jobs", "docs"),
    "python": ("Building and testing Python", GH + "actions/tutorials/build-and-test-code/python", "docs"),
    "artifacts": ("Workflow artifacts", GH + "actions/concepts/workflows-and-actions/workflow-artifacts", "docs"),
    "upload_artifact": ("actions/upload-artifact README", "https://github.com/actions/upload-artifact", "read"),
    "caching": ("Dependency caching", GH + "actions/concepts/workflows-and-actions/dependency-caching", "docs"),
    "matrix": ("Running variations of jobs in a workflow (matrix)", GH + "actions/how-tos/write-workflows/choose-what-workflows-do/run-job-variations", "docs"),
    "setup_python": ("actions/setup-python README", "https://github.com/actions/setup-python", "read"),
    "build_push": ("docker/build-push-action README", "https://github.com/docker/build-push-action", "read"),
    "rulesets": ("About rulesets", GH + "repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/about-rulesets", "docs"),
    "rulesets_create": ("Creating rulesets for a repository", GH + "repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/creating-rulesets-for-a-repository", "docs"),
    "req_checks": ("Troubleshooting required status checks", GH + "pull-requests/how-tos/merge-and-close-pull-requests/troubleshooting-required-status-checks", "docs"),
    "concurrency": ("Control the concurrency of workflows and jobs", GH + "actions/how-tos/write-workflows/choose-when-workflows-run/control-workflow-concurrency", "docs"),
    "skip_runs": ("Skipping workflow runs", GH + "actions/how-tos/manage-workflow-runs/skip-workflow-runs", "docs"),
    "actionlint": ("actionlint: a linter for workflow files", "https://github.com/rhysd/actionlint", "read"),
    "act": ("act: run your GitHub Actions locally", "https://github.com/nektos/act", "read"),
    "secrets": ("About secrets", GH + "actions/concepts/security/secrets", "docs"),
    "use_secrets": ("Using secrets in GitHub Actions", GH + "actions/how-tos/write-workflows/choose-what-workflows-do/use-secrets", "docs"),
    "token": ("GITHUB_TOKEN", GH + "actions/concepts/security/github_token", "docs"),
    "token_tut": ("Use GITHUB_TOKEN for authentication in workflows", GH + "actions/tutorials/authenticate-with-github_token", "docs"),
    "publish_images": ("Publishing Docker images", GH + "actions/tutorials/publish-packages/publish-docker-images", "docs"),
    "ghcr": ("Working with the Container registry", GH + "packages/working-with-a-github-packages-registry/working-with-the-container-registry", "docs"),
    "pkg_visibility": ("Configuring a package's access control and visibility", GH + "packages/learn-github-packages/configuring-a-packages-access-control-and-visibility", "docs"),
    "skill_docker": ("GitHub Skills: Publish Docker images (hands-on course)", "https://github.com/skills/publish-docker-images", "read"),
    "envs": ("Deployment environments", GH + "actions/concepts/workflows-and-actions/deployment-environments", "docs"),
    "manage_envs": ("Managing environments for deployment", GH + "actions/how-tos/deploy/configure-and-manage-deployments/manage-environments", "docs"),
    "oidc": ("OpenID Connect", GH + "actions/concepts/security/openid-connect", "docs"),
    "oidc_aws": ("Configuring OpenID Connect in Amazon Web Services", GH + "actions/how-tos/secure-your-work/security-harden-deployments/oidc-in-aws", "docs"),
    "oidc_ref": ("OpenID Connect reference", GH + "actions/reference/security/oidc", "docs"),
    "aws_action": ("aws-actions/configure-aws-credentials README", "https://github.com/aws-actions/configure-aws-credentials", "read"),
    "reuse": ("Reusing workflow configurations", GH + "actions/concepts/workflows-and-actions/reusing-workflow-configurations", "docs"),
    "prt": ("Securely using pull_request_target", GH + "actions/reference/security/securely-using-pull_request_target", "docs"),
    "dependabot": ("Keeping your actions up to date with Dependabot", GH + "code-security/how-tos/secure-your-supply-chain/secure-your-dependencies/auto-update-actions", "docs"),
    "metadata": ("docker/metadata-action README", "https://github.com/docker/metadata-action", "read"),
}


def refs(*keys):
    return [{"title": R[k][0], "url": R[k][1], "kind": R[k][2]} for k in keys]


def sources(*keys):
    return [{"title": R[k][0], "url": R[k][1]} for k in keys]


# ---------------------------------------------------------------- code files
HELLO_YML = T("""
    name: hello

    # Run on every push to any branch, and from a button in the Actions tab.
    on:
      push:
      workflow_dispatch:

    # Workflow-level env: every job and step can read it.
    env:
      GREETING: Hello from GitHub Actions

    jobs:
      say-hello:
        runs-on: ubuntu-latest
        # Job-level env: only steps in this job can read it.
        env:
          JOB_NOTE: I run on a fresh virtual machine
        steps:
          - name: Print facts about this run
            # Step-level env: copy context values into plain shell variables.
            env:
              BRANCH: ${{ github.ref_name }}
              EVENT: ${{ github.event_name }}
            run: |
              echo "$GREETING"
              echo "$JOB_NOTE"
              echo "Commit: ${{ github.sha }}"
              echo "Branch or tag: $BRANCH"
              echo "Started by: $EVENT"
          - name: Look around the runner
            run: |
              uname -sm
              python3 --version
              docker --version
""")

CI_V1_YML = T("""
    name: ci

    # Day 10 version: run the tests on every push, or from a button.
    on:
      push:
      workflow_dispatch:

    jobs:
      test:
        runs-on: ubuntu-latest
        steps:
          - uses: actions/checkout@v7
          - uses: actions/setup-python@v7
            with:
              python-version: "3.14"
          - name: Install dependencies
            run: pip install -r requirements-dev.txt
          - name: Run tests
            run: pytest -q
""")

# ================================================================= d09
d09 = {
    "id": "d09",
    "title": "Git, pull requests and CI/CD ideas",
    "minutes": 35,
    "goal": "By the end you can open, review and merge a pull request with gh, tag a version, and explain CI, continuous delivery and continuous deployment in plain words.",
    "guess": {
        "q": "Your new team says it practices continuous deployment. What does that mean?",
        "options": [
            "Everyone merges code into main at least once a day",
            "Every change is ready to release, and a person clicks to ship it",
            "Every change that passes the pipeline reaches production with no human step",
            "The production servers are never switched off",
        ],
        "answer": 2,
        "why": "Continuous deployment releases every passing change automatically. Merging daily is continuous integration, and a human release click is continuous delivery.",
    },
    "terms": [
        {"term": "Branch", "plain": "A movable label on a line of commits, so you can work without touching main."},
        {"term": "Pull request (PR)", "plain": "A GitHub page that asks to merge one branch into another, with review and checks."},
        {"term": "Merge conflict", "plain": "Two branches changed the same lines, so git asks a person to pick the result."},
        {"term": "Continuous integration (CI)", "plain": "Merging small changes often, with an automatic build and test for every change."},
        {"term": "Continuous delivery", "plain": "Every change that passes the pipeline is ready to release, and a person decides when."},
        {"term": "Continuous deployment", "plain": "Every change that passes the pipeline goes to production with no human step."},
        {"term": "Semantic versioning", "plain": "Version numbers in the form MAJOR.MINOR.PATCH that show how big a change is."},
    ],
    "sections": [
        {"h": "Git for teams: branches, commits and merges", "body": T("""
            On your own, you can commit straight to `main`. In a team, that breaks fast. Two people change the same file, and someone's work gets lost or the app stops working.

            Git solves this with branches. A **branch** is a movable label that points at a line of commits. You commit on your branch, and `main` stays untouched until you merge.

            The everyday loop looks like this:

            1. Create a branch from the latest `main`, for example `git switch -c add-pr-template`.
            2. Change files and commit in small steps.
            3. Push the branch to GitHub.
            4. Merge it into `main` once it is reviewed and tested.

            A merge combines two lines of work. Most of the time git does it alone. When both branches changed the same lines, git stops and asks you to choose. That is a merge conflict. Git marks the clash in the file with `<<<<<<<`, `=======` and `>>>>>>>`. You edit the file to the right result, then add and commit it. Small, short-lived branches make conflicts rare and easy to fix.
        """), "refs": refs("about_git", "conflict_cli", "skill_conflicts")},
        {"h": "Pull requests and code review", "body": T("""
            A pull request (PR) is a GitHub page that says: please merge my branch into `main`. It shows the diff (the lines you changed), a conversation, and the results of automatic checks.

            A pull request gives a team three things:

            - Review: a teammate reads the change and comments on single lines.
            - Checks: CI runs the tests and shows a green tick or a red cross.
            - A record: months later, you can see why a line changed and who agreed.

            Keep PRs small, so a reviewer can read one in ten minutes. Say what changed and how you tested it. A PR template, which you add today, reminds everyone to do that. Review the code and be kind to the person who wrote it.

            You can open and merge PRs in the browser. Today you use `gh`, the GitHub CLI from Day 2, because it is fast and you can script it.
        """), "refs": refs("about_prs", "review_qs")},
        {"h": "Trunk-based development and GitFlow", "body": T("""
            A team also agrees on a branching strategy: how long branches live and where releases come from. Two styles are common.

            In trunk-based development, everyone merges small branches into one main branch, the trunk, at least once a day. Branches live for hours, or a day or two. `main` is always in a state you could release. Unfinished features hide behind feature flags, which you meet below.

            GitFlow uses several long-lived branches:

            - `main` holds released code only.
            - `develop` collects finished features.
            - `feature/...` branches start from `develop`.
            - `release/...` and `hotfix/...` branches prepare and patch releases.

            GitFlow fits software that ships big versions a few times a year. Teams that deploy often mostly prefer trunk-based development. Long-lived branches drift apart, and merging them back is slow and risky. GitHub's own [GitHub flow](https://docs.github.com/en/get-started/using-github/github-flow) is a simple trunk-based style, and this course uses it.
        """), "refs": refs("gh_flow")},
        {"h": "CI, continuous delivery and continuous deployment", "body": T("""
            Continuous integration (CI) means you merge small changes often, and a server builds and tests every change automatically. The goal is fast feedback. A broken test shows up minutes after your push, while the change is still fresh in your head.

            CD has two meanings, and people mix them up:

            - Continuous delivery: every change that passes is ready to release. A person clicks a button to put it in production.
            - Continuous deployment: every change that passes goes to production automatically. There is no human step.

            The steps a change goes through are called a pipeline. A typical pipeline runs in this order:

            1. Build: install dependencies and package the code.
            2. Test: run linters and automated tests.
            3. Publish: build a container image and push it to a registry.
            4. Deploy: release that image to staging, then to production.

            One rule matters a lot: **build once, deploy many**. You build the image one time, and the very same image (same digest) moves from staging to production. You never rebuild for production. A rebuild can pull newer packages, so what you tested would not be what you ship.
        """), "refs": refs("ci", "cd")},
        {"h": "Deployment strategies: how new versions reach users", "body": T("""
            Deploying means swapping the old version for the new one while users keep working. There are four common ways to do it:

            - Rolling: replace servers or containers a few at a time. Kubernetes does this by default (Day 17).
            - Blue/green: run the new version (green) next to the old one (blue), then switch all traffic at once.
            - Canary: send a small share of traffic, say 5%, to the new version, then grow it step by step.
            - Feature flags: ship new code switched off, then turn it on for some users with a setting.

            Each one is a trade-off. Rolling needs no extra servers, but old and new versions run side by side for a while. Blue/green makes rollback instant, but needs double the capacity during the switch. Canary limits the damage of a bad release, but needs good metrics to judge it (Day 21). Feature flags need no deploy at all, but leave `if` branches in the code that you must clean up later.

            Tools such as [Argo Rollouts](https://github.com/argoproj/argo-rollouts) automate blue/green and canary releases on Kubernetes.
        """), "refs": refs("rollouts", "sre")},
        {"h": "Semantic versions and git tags", "body": T("""
            A version number tells users how much changed. [Semantic versioning](https://github.com/semver/semver/blob/master/semver.md) uses three numbers, MAJOR.MINOR.PATCH:

            - MAJOR goes up when you break compatibility, as in 2.0.0.
            - MINOR goes up when you add a feature that stays compatible, as in 1.3.0.
            - PATCH goes up for a compatible bug fix, as in 1.2.1.

            A git tag is a name that points at one commit for good, such as `v1.2.0`. A branch label moves with each new commit, while a tag stays where you put it. Use annotated tags (`git tag -a`). They store who made the tag, when, and a message.

            Tags connect git to releases. On Day 12, pushing a tag such as `v1.0.0` starts a workflow that builds and publishes the image `1.0.0`. The git tag, the image tag and the app's `version` field then all match. Note that a plain `git push` does not send tags. You push each tag by name.
        """), "refs": refs("semver", "releases")},
    ],
    "analogy": "A pull request is like a suggested edit in a shared document. You write on your own copy, a colleague reads the suggestion and comments, and the owner accepts it into the main text. CI is a spell checker that runs on every suggestion before anyone reads it. The analogy breaks because git keeps many parallel copies and combines them line by line, while a document has only one text.",
    "diagram": D09,
    "diagram_caption": "One change: a short branch, a pull request with checks and review, a merge, then a tag for the release.",
    "worked": {"title": "Resolve a merge conflict", "steps": [
        {"say": "Two branches changed the same line of `app.py`. On `main`, a teammate changed the default greeting to 'Hello, DevOps team!'. On your branch `friendly`, you changed it to 'Hi there, DevOps!'. Git cannot keep both by itself.", "code": T("""
            $ git switch main
            $ git merge friendly
            Auto-merging app.py
            CONFLICT (content): Merge conflict in app.py
            Automatic merge failed; fix conflicts and then commit the result.
        """), "lang": "console"},
        {"say": "`git status` shows `UU`, which means both sides changed the file and it is not merged yet. Look at the clash.", "code": T("""
            $ git status --short
            UU app.py
            $ grep -n -A4 "<<<<<<<" app.py
            3:<<<<<<< HEAD
            4-GREETING = os.getenv("GREETING", "Hello, DevOps team!")
            5-=======
            6-GREETING = os.getenv("GREETING", "Hi there, DevOps!")
            7->>>>>>> friendly
        """), "lang": "console"},
        {"say": "Read the markers. Above `=======` is your current branch (HEAD, here `main`). Below it is the incoming branch. You decide the result: here you combine both ideas, and you delete all three marker lines.", "code": 'GREETING = os.getenv("GREETING", "Hi there, DevOps team!")', "lang": "python"},
        {"say": "Mark the conflict as solved by adding the file, then commit. The graph shows the two lines of work joined by a merge commit.", "code": T("""
            $ git add app.py
            $ git commit -m "Merge friendly: keep both ideas"
            $ git log --oneline --graph
            *   763f293 Merge friendly: keep both ideas
            |\\
            | * d4ba8e1 Friendlier greeting
            * | 024c024 Greet the team
            |/
            * 7142d7d Add greeting
        """), "lang": "console"},
        {"say": "Run the tests before you push. Git only checks that the text merged cleanly, so it cannot tell if the code still works. Here the teammate's test still expects 'Hello, DevOps team!', so you update `test_app.py` in the same merge. Catching this kind of break is exactly the job of CI.", "code": T("""
            $ pytest -q | tail -2
            FAILED test_app.py::test_index_says_hello - AssertionError: assert 'Hi there,...
            1 failed, 2 passed in 0.20s
        """), "lang": "console"},
    ]},
    "code": [
        {"lang": "text", "title": ".github/pull_request_template.md", "src": lab(".github/pull_request_template.md"),
         "run": "git add .github/pull_request_template.md && git commit -m \"Add a pull request template\""},
    ],
    "commands": [
        {"cmd": "git switch -c add-pr-template", "what": "Create a new branch from where you are and switch to it."},
        {"cmd": "git push -u origin add-pr-template", "what": "Push the branch to GitHub and remember the link, so later pushes need no names."},
        {"cmd": "gh pr create --fill", "what": "Open a pull request. `--fill` uses your commit message as the title and body."},
        {"cmd": "gh pr view --web", "what": "Open the pull request for the current branch in your browser."},
        {"cmd": "gh pr merge --squash --delete-branch", "what": "Merge the PR as one commit, then delete the branch locally and on GitHub."},
        {"cmd": "git switch main && git pull", "what": "Go back to main and download the merged result."},
        {"cmd": "git log --oneline --graph", "what": "Show history as a compact graph of branches and merges."},
        {"cmd": "git tag -a v0.1.0 -m \"First tagged version\"", "what": "Create an annotated tag on the current commit."},
        {"cmd": "git push origin v0.1.0", "what": "Send one tag to GitHub. A plain `git push` does not send tags."},
        {"cmd": "gh pr list --state merged", "what": "List pull requests that were merged."},
    ],
    "mistake": "Working on one big branch for days, then opening a huge pull request. Reviews get shallow, conflicts pile up, and a failing test is hard to trace. Make one small branch per change, open the PR early (as a draft if needed), and merge within a day or two.",
    "real_world": "At PayLoop, a made-up payments company, every change to the checkout service goes through a pull request. The merge button only turns on after one approving review and green CI. Merges to `main` deploy to staging automatically, and the same image reaches production when an engineer clicks approve, which is continuous delivery.",
    "task": {
        "title": "Your first pull request with gh",
        "steps": [
            "In `~/code/hello-devops`, switch to `main` and pull, so you start from the latest code.",
            "Create a branch called `add-pr-template`.",
            "Create `.github/pull_request_template.md` with the content from the Files section, and commit it with a clear message.",
            "Push the branch and open a pull request with `gh pr create --fill`.",
            "Open the PR in the browser. Read the Files changed tab as a reviewer would, and leave one comment on a line.",
            "Merge the PR with squash and delete the branch, using `gh pr merge`.",
            "Update your local `main`, then create the annotated tag `v0.1.0` and push it.",
            "Start a second branch, change one line, push it, and run `gh pr create --web`. The description box now starts from your template. Close that PR if you do not need it.",
        ],
        "hints": [
            "If `gh pr create` asks where to push the branch, pick your own repository.",
            "Tags travel separately: push them by name, as in `git push origin v0.1.0`.",
            "The template only fills new PRs after it is merged into `main`.",
        ],
        "done_when": "`gh pr list --state merged` shows your PR, and `git ls-remote --tags origin` lists `v0.1.0`.",
    },
    "explain_back": {
        "prompt": "Explain continuous integration, continuous delivery and continuous deployment to a teammate in 3 to 4 sentences. Say where a human decides.",
        "answer": "Continuous integration means everyone merges small changes often, and every change is built and tested automatically, so problems show up within minutes. Continuous delivery adds the rest of the pipeline: every change that passes is packaged and ready to release, and a person decides when it goes to production. Continuous deployment removes that last human step, so every passing change goes live on its own. In all three, you build the artifact once and promote that same artifact through each stage.",
    },
    "recap": [
        "Work on short-lived branches and merge them through pull requests with review and checks.",
        "A merge conflict means two branches changed the same lines; you pick the result and commit.",
        "Trunk-based development keeps main releasable with small daily merges; GitFlow uses long-lived branches.",
        "CI tests every change; continuous delivery keeps it releasable; continuous deployment releases it automatically.",
        "Build once, deploy many: promote one tested image instead of rebuilding for each environment.",
        "Semantic versions and annotated git tags such as v1.2.0 name exact releases.",
    ],
    "check": [
        {"q": "Your team merges to main many times a day, and every passing change is ready to ship. A product manager clicks Release every Friday. What is this?",
         "options": ["Continuous deployment", "Continuous delivery", "GitFlow", "Blue/green deployment"],
         "answer": 1, "why": "Every change is releasable and a human picks the moment, which is continuous delivery."},
        {"q": "You fix a bug in version 2.4.1, and nobody has to change how they call your API. What is the next version?",
         "options": ["3.0.0", "2.5.0", "2.4.2", "2.4.1-fix"],
         "answer": 2, "why": "A compatible bug fix raises only the PATCH number."},
        {"q": "You want to try a new checkout page on 5% of real users first, and roll back fast if errors rise. Which strategy fits best?",
         "options": ["Canary release", "Rolling update", "Rebuild the image for production", "A long-lived release branch"],
         "answer": 0, "why": "A canary sends a small share of traffic to the new version and grows it only while the metrics look good."},
    ],
    "interview": [
        {"q": "What is the difference between continuous delivery and continuous deployment?",
         "a": "Both build, test and package every change automatically, so main is always releasable. In continuous delivery, a person decides when a release goes to production, often with one click or an approval. In continuous deployment, every change that passes the pipeline goes to production with no human step. Continuous deployment needs strong automated tests, good monitoring and fast rollback, because nobody looks at each release by hand."},
        {"q": "Why do many teams prefer trunk-based development to GitFlow?",
         "a": "Trunk-based development keeps branches small and short-lived, so merges are easy and conflicts are rare. Main is always releasable, which fits CI and frequent deploys. GitFlow's long-lived develop and release branches drift apart, so merges get big and risky. GitFlow still fits products that ship versioned releases a few times a year, or that must patch several old versions."},
    ],
    "deeper": {"minutes": 12, "body": T("""
        When you merge a pull request on GitHub, you pick one of three methods. Each one leaves a different history on `main`:

        - Create a merge commit: keeps every commit from the branch and adds one merge commit with two parents.
        - Squash and merge: combines all branch commits into one new commit on `main`.
        - Rebase and merge: replays each branch commit on top of `main`, with no merge commit.

        Many trunk-based teams choose squash. One PR becomes one commit, so `git log` stays readable and `git revert` can undo a whole PR in one step. The small commits inside the PR are still visible on the PR page. Admins can switch methods on or off in the repository settings, so the whole team uses one style. See [About merge methods on GitHub](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/configuring-pull-request-merges/about-merge-methods-on-github).

        How does git merge text at all? It uses a three-way merge. First it finds the merge base: the last commit both branches share. Then it compares each side with that base, region by region:

        1. If only one side changed a region, git takes that change.
        2. If both sides made the same change, git takes it once.
        3. If both sides changed the same region in different ways, git marks a conflict.

        This explains why small, short branches conflict less. The fewer lines each side changed since the merge base, the smaller the chance that they touch the same region.

        It also explains a trap. Git can merge two changes cleanly that still break each other. One branch renames a function, and another branch adds a new call to the old name. No lines clash, so git is happy, but the code is broken. Only tests catch this. That is why CI runs on the merged result of a pull request, which Day 10 shows in the `pull_request` event.

        Last, rebasing. `git rebase main` replays your branch's commits on top of the newest `main`, so your branch looks as if you started it today. It rewrites your commits with new IDs. Only rebase branches that nobody else works on, and push afterwards with `git push --force-with-lease`, which refuses to overwrite work you have not seen.
    """)},
    "sources": sources("gh_flow", "about_prs", "ci", "semver"),
}

# ================================================================= d10
d10 = {
    "id": "d10",
    "title": "GitHub Actions: your first workflow",
    "minutes": 35,
    "goal": "By the end you can write a workflow file, start it with a push or a button, read its logs, and run pytest on every push.",
    "guess": {
        "q": "A job in your workflow says `runs-on: ubuntu-latest`. Where does it run?",
        "options": [
            "On your laptop, inside Docker Desktop",
            "On the GitHub server that stores your code",
            "On the same server as last time, with its old files",
            "On a fresh virtual machine made just for this job",
        ],
        "answer": 3,
        "why": "GitHub-hosted runners are new virtual machines for every job, so nothing from the last run is left. That is why almost every job starts with checkout and setup steps.",
    },
    "terms": [
        {"term": "Workflow", "plain": "A YAML file in .github/workflows that describes an automated process."},
        {"term": "Event", "plain": "Something that starts a workflow, such as a push, a pull request or a timer."},
        {"term": "Job", "plain": "A group of steps that runs on one runner; jobs run in parallel unless linked."},
        {"term": "Step", "plain": "One task in a job: a shell command (run) or a ready-made action (uses)."},
        {"term": "Runner", "plain": "The machine that runs a job; GitHub-hosted runners are fresh virtual machines."},
        {"term": "Action", "plain": "A published, reusable step such as actions/checkout, called with uses."},
        {"term": "Context", "plain": "Facts about the current run, such as github.sha, read with ${{ }}."},
    ],
    "sections": [
        {"h": "What GitHub Actions is", "body": T("""
            GitHub Actions is the automation built into GitHub. You describe a task in a YAML file, and GitHub runs it when something happens in your repository. CI is the most common use. You can also automate releases, issue labels or nightly checks.

            Everything fits in a small hierarchy:

            1. An event happens, for example you push a commit.
            2. GitHub finds every **workflow** that listens for that event.
            3. Each workflow starts one or more jobs. Jobs run in parallel unless one needs another.
            4. Each job runs on a **runner**, a machine that executes the job's steps in order.
            5. Each step is a shell command or a ready-made action.

            If a step fails, the job stops and is marked as failed. Remember exit codes from Day 3. A command that ends with a non-zero code fails its step. `pytest` exits with 1 when a test fails, so a failing test turns the job red.
        """), "refs": refs("understand", "skill_hello")},
        {"h": "Anatomy of a workflow file", "body": T("""
            Workflows live in `.github/workflows/` at the root of your repository. Every `.yml` or `.yaml` file there is a workflow. These top-level keys are the ones you use most:

            - `name`: the label shown in the Actions tab.
            - `on`: the events that start the workflow.
            - `env`: environment variables for all jobs (optional).
            - `jobs`: a map from job IDs, such as `test`, to job settings.

            Inside a job, `runs-on` picks the runner and `steps` lists the work. Give steps a `name`, so the logs are easy to read.

            YAML trips most people up at first. Indentation carries meaning, so use spaces and never tabs. A list item starts with a dash and a space. Strings with special characters, such as `*` or `:`, need quotes. Versions need quotes too: YAML reads `3.10` as the number 3.1, so write `"3.10"`. The YAML extension in VS Code from Day 2 flags many mistakes while you type.
        """), "refs": refs("syntax", "quickstart")},
        {"h": "Events: when a workflow runs", "body": T("""
            The `on` key lists the events. You will use these four a lot:

            - `push`: a commit or tag is pushed. Filters such as `branches: [main]` or `tags: ["v*"]` narrow it down.
            - `pull_request`: a PR is opened, gets new commits, or is reopened.
            - `workflow_dispatch`: adds a Run workflow button to the Actions tab.
            - `schedule`: runs on a timer written in cron syntax.

            Some details matter later. A `pull_request` run tests the result of merging your branch into the target branch, so it catches clashes with other people's work. The Run workflow button only appears once the workflow file is on the default branch. Schedules use UTC unless you set a time zone, and the shortest interval is every 5 minutes. They only run from the default branch, can start late when GitHub is busy, and are switched off in public repos after 60 days without activity.

            You can list several events at once. `on: [push, workflow_dispatch]` runs on every push and also gives you the button.
        """), "refs": refs("events")},
        {"h": "Runners, and uses versus run", "body": T("""
            A runner is the machine that runs a job. There are two kinds:

            - GitHub-hosted: a fresh virtual machine for every job, with git, Docker, Python and many tools installed. In public repos the standard Linux runner has 4 CPUs and 16 GB of memory.
            - Self-hosted: a machine you run yourself and register with GitHub. Useful for special hardware or private networks, but you must patch and secure it.

            Billing in short: standard GitHub-hosted runners are free in public repositories. Private repos on the Free plan get a monthly allowance, at the time of writing $12 of compute, which is about 2,000 Linux minutes. Check the [current billing page](https://docs.github.com/en/billing/concepts/product-billing/github-actions) before you rely on these numbers.

            A step does its work in one of two ways. `run:` executes shell commands, with bash on Linux. `uses:` calls an action: packaged code that someone published, such as `actions/checkout@v7`. The part after `@` is the version. You pass inputs to an action under `with:`. Each runner starts empty, so nearly every job begins with `actions/checkout`, which copies your repository onto the runner.
        """), "refs": refs("hosted", "billing")},
        {"h": "Contexts, expressions and env", "body": T("""
            A context is a set of facts about the current run. You read it with an expression written as `${{ ... }}`. GitHub replaces the expression with its value before the step runs. Some examples:

            - `${{ github.sha }}`: the full commit ID that started the run.
            - `${{ github.ref_name }}`: the branch or tag name, such as `main` or `v1.2.0`.
            - `${{ github.event_name }}`: the event, such as `push`.
            - `${{ runner.os }}`: the runner's operating system, such as `Linux`.

            You set environment variables with `env` at three levels: the whole workflow, one job, or one step. The most specific level wins, so a step's value beats the job's value. GitHub also sets default variables in every step, such as `GITHUB_SHA` and `GITHUB_REF_NAME`.

            Start one safety habit now. Some values are text that other people control, like branch names or PR titles. Do not paste their expressions straight into a `run:` script, because the text becomes part of your script. Copy the value into `env` first and use the shell variable, as the hello workflow does. Day 12 explains why.
        """), "refs": refs("contexts", "variables", "secure_use")},
        {"h": "Reading runs in the Actions tab", "body": T("""
            Every run appears in your repository's Actions tab. Click a run to see a graph of its jobs, then click a job to see the log of each step. A green tick means success, a red cross means failure, and a grey icon means skipped or cancelled.

            When a run fails, open the first red step and read the last lines of its log. That is usually where the error is. The `gh` CLI does the same from your terminal:

            - `gh run list` shows recent runs and their status.
            - `gh run watch` follows a run live until it finishes.
            - `gh run view --log-failed` prints only the logs of failed steps.
            - `gh run rerun --failed` runs the failed jobs again.

            Logs are kept for a limited time, and anyone who can read the repository can read them. So never print a secret, not even for a quick test.
        """), "refs": refs("logs")},
    ],
    "analogy": "A workflow is like an order ticket in a restaurant kitchen. When an order comes in (the event), a cook gets a clean, empty station (the runner) and follows the ticket line by line (the steps). When the dish is done, the station is wiped for the next order. The analogy breaks at the end. A kitchen keeps its leftovers, while a runner keeps nothing unless you save it as a cache or an artifact (Day 11).",
    "diagram": D10,
    "diagram_caption": "A push starts the workflow; its job gets a fresh runner and runs the steps in order.",
    "worked": {"title": "Your first workflow: hello.yml", "steps": [
        {"say": "Work on a branch so you can experiment safely. The folder name matters: GitHub only reads workflows from `.github/workflows/`.", "code": T("""
            cd ~/code/hello-devops
            git switch -c try-actions
            mkdir -p .github/workflows
            code .github/workflows/hello.yml
        """), "lang": "bash"},
        {"say": "Paste `hello.yml` from the Files section. It runs on every push and from a button, sets `env` at three levels, and prints facts about the run. Notice that the branch name goes through `env` before the script uses it.", "code": T("""
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
        """), "lang": "yaml"},
        {"say": "Commit and push. The push is the event, so the run starts within seconds. `gh run watch` lets you pick the run and follows it until it ends.", "code": T("""
            $ git add .github/workflows/hello.yml
            $ git commit -m "Add a hello workflow"
            $ git push -u origin try-actions
            $ gh run watch
        """), "lang": "console"},
        {"say": "Open the run with `gh run view --web`, click the job, and expand the first step. You see lines like these, with your own commit ID. Each `env` level fed one line.", "code": T("""
            Hello from GitHub Actions
            I run on a fresh virtual machine
            Commit: 9f2c1e7d0b6a4c3e8f5a1b2c3d4e5f6a7b8c9d0e
            Branch or tag: try-actions
            Started by: push
        """), "lang": "text"},
        {"say": "Expand the second step. `uname -sm` prints `Linux x86_64`, and the Python and Docker versions follow. The runner already has these tools, so your CI only has to pick a Python version and install your packages.", "code": "Linux x86_64", "lang": "text"},
        {"say": "The hello workflow was practice. Delete the branch here and on GitHub, so it never runs again.", "code": T("""
            $ git switch main
            $ git branch -D try-actions
            $ git push origin --delete try-actions
        """), "lang": "console"},
    ]},
    "code": [
        {"lang": "yaml", "title": ".github/workflows/hello.yml (practice, deleted at the end)", "src": HELLO_YML,
         "run": "git add .github/workflows/hello.yml && git commit -m \"Add a hello workflow\" && git push"},
        {"lang": "yaml", "title": ".github/workflows/ci.yml (Day 10 version)", "src": CI_V1_YML,
         "run": "git add .github/workflows/ci.yml && git commit -m \"Run tests in CI\" && git push && gh run watch"},
    ],
    "commands": [
        {"cmd": "gh run list", "what": "Show the latest workflow runs and their status."},
        {"cmd": "gh run watch", "what": "Pick a run and follow it live until it finishes."},
        {"cmd": "gh run view --web", "what": "Open a run in the browser."},
        {"cmd": "gh run view --log-failed", "what": "Print the logs of only the failed steps of a run."},
        {"cmd": "gh run rerun --failed", "what": "Run the failed jobs of a run again."},
        {"cmd": "gh workflow list", "what": "List the workflows in this repository."},
        {"cmd": "gh workflow run ci.yml", "what": "Start a workflow that has `workflow_dispatch`, like pressing Run workflow."},
        {"cmd": "git push origin --delete try-actions", "what": "Delete a branch on GitHub."},
    ],
    "mistake": "Saving the workflow in the wrong folder, such as `.github/workflow/` or `github/workflows/`. GitHub ignores it silently: nothing runs and no error appears. The folder must be exactly `.github/workflows/` at the root of the repository.",
    "real_world": "At PayLoop, every new service starts from the same CI template, so it runs tests on every push from its first day. Engineers rarely open the Actions tab when things are green. When a pull request shows a red cross, they jump straight to the failed step's log.",
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
            "Open a PR, merge it into `main`, and press Run workflow for `ci` in the Actions tab.",
        ],
        "hints": [
            "Your file has the same shape as `hello.yml`, with different steps.",
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
        "Workflows are YAML files in .github/workflows, and the events under on start them.",
        "A workflow has jobs, a job has steps, and each job runs on its own fresh runner.",
        "run executes shell commands; uses calls a published action, with inputs under with.",
        "Expressions such as ${{ github.sha }} read contexts; env can be set per workflow, job or step.",
        "A non-zero exit code fails the step, the job and the run.",
        "Debug from the first red step, in the Actions tab or with gh run view --log-failed.",
    ],
    "check": [
        {"q": "You want a workflow to run every night at 02:00 UTC and also from a button. Which on block fits?",
         "options": ["schedule with cron \"0 2 * * *\", plus workflow_dispatch", "push with branches: [nightly]", "pull_request with types: [scheduled]", "schedule with cron \"2 0 * * *\" only"],
         "answer": 0, "why": "Cron fields start with the minute, then the hour, so \"0 2 * * *\" is 02:00, and workflow_dispatch adds the button."},
        {"q": "Job test has three steps. Step 2 runs pip install and exits with code 1. What happens?",
         "options": ["Step 3 still runs, and the job passes", "The job stops, is marked failed, and step 3 is skipped", "GitHub retries step 2 until it passes", "Only a warning appears, because install steps cannot fail"],
         "answer": 1, "why": "By default a non-zero exit code fails the step and stops the job."},
        {"q": "A step must print the branch name, and branch names can contain odd characters. What is the safest way?",
         "options": ["Paste ${{ github.ref_name }} into the run script", "Store the branch name as a repository secret", "Copy it into env as BRANCH, then use \"$BRANCH\"", "Hard-code main in the script"],
         "answer": 2, "why": "A value passed through env reaches the shell as data, so it is never run as code."},
    ],
    "interview": [
        {"q": "What is the difference between a job and a step in GitHub Actions?",
         "a": "A job is a group of steps that runs on one runner. The steps in a job run in order and share the same machine and files. Different jobs run on different runners, in parallel by default, and share nothing unless you pass artifacts or outputs. You use `needs` to make one job wait for another."},
        {"q": "When would you choose self-hosted runners over GitHub-hosted ones?",
         "a": "GitHub-hosted runners are fresh, patched virtual machines that you do not maintain, and they are free for public repos. Self-hosted runners make sense when you need special hardware, access to a private network, or lower cost at very high volume. The price is work: you patch, scale and secure them yourself. GitHub recommends self-hosted runners only for private repositories, because a pull request from a fork could run code on your machine."},
    ],
    "deeper": {"minutes": 12, "body": T("""
        A `run:` step looks like a list of commands. GitHub actually saves it as a script file and runs that file with a shell. The shell and its options decide how failures behave.

        On Linux runners, if you do not set `shell`, GitHub runs `bash -e {0}`, where `{0}` is the script file. The `-e` flag is the `set -e` from Day 3: the script stops at the first command that fails, and the step fails with that exit code.

        If you write `shell: bash` yourself, GitHub runs `bash --noprofile --norc -eo pipefail {0}` instead. The extra `pipefail` matters for pipes. Without it, a pipe returns the exit code of its last command. So `pytest -q | tee test.log` passes even when tests fail, because `tee` worked fine. With `pipefail`, the failing `pytest` fails the whole pipe, and the step goes red as it should.

        You can set the shell once for every step. Add a `defaults` block at the top of the workflow with `run: shell: bash` inside it. Many teams do this to get `pipefail` everywhere.

        A few more facts that save debugging time:

        - Each `run:` step starts a new shell. A variable you `export` in one step is gone in the next one.
        - To hand a value to later steps, append a line like `NAME=value` to the file named in `$GITHUB_ENV`.
        - All steps in a job share one disk, so a file written in step 2 is still there in step 3.
        - `working-directory: app` runs a step inside a subfolder.
        - `continue-on-error: true` lets a step fail without failing the job. Use it rarely, because it hides problems.

        The supported shells table in the [workflow syntax reference](https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax) lists the exact command line for each shell. When a script behaves one way on your laptop and another way in CI, these flags are a likely reason.
    """)},
    "sources": sources("understand", "syntax", "events", "skill_hello"),
}

# ================================================================= d11
d11 = {
    "id": "d11",
    "title": "A real CI pipeline: test, lint, cache, matrix",
    "minutes": 40,
    "goal": "By the end you can build a fast CI pipeline with lint, tests on two Python versions, a test report and a Docker build check, and stop red pull requests from merging.",
    "guess": {
        "q": "Your CI has a test job and a build job with `needs: test`. A ruleset requires only the build check. A test fails on a pull request. What happens?",
        "options": [
            "The merge is blocked, because build never ran",
            "GitHub reruns the tests until they pass",
            "It can merge, because a skipped build counts as passed",
            "Build runs anyway, because test is not required",
        ],
        "answer": 2,
        "why": "GitHub treats a skipped check as passed, so a skipped build does not block the merge. Require the test checks too.",
    },
    "terms": [
        {"term": "Lint", "plain": "An automatic check for style problems and likely bugs that reads code without running it."},
        {"term": "Matrix", "plain": "One job definition that GitHub expands into several jobs, one per value, such as Python versions."},
        {"term": "Cache", "plain": "Files saved by an earlier run, such as downloaded packages, and restored to save time."},
        {"term": "Artifact", "plain": "A file a job uploads, such as a test report, that you can download after the run."},
        {"term": "Required status check", "plain": "A check that must pass on a pull request before GitHub allows the merge."},
        {"term": "Ruleset", "plain": "A named set of rules for branches or tags, such as 'main needs passing checks'."},
        {"term": "Concurrency group", "plain": "A name that lets only one run per group go ahead, cancelling or queueing the others."},
    ],
    "sections": [
        {"h": "What a good CI pipeline does", "body": T("""
            Your Day 10 workflow runs the tests. A real pipeline answers more questions on every change. Is the code clean? Does it work on every Python version you support? Does the Docker image still build? It also answers fast, because people wait for CI before they merge.

            A good order is cheap checks first and slow checks last:

            1. Lint and format check: seconds, and it catches typos and unused code.
            2. Unit tests: seconds to minutes.
            3. Docker build: the slowest part, so it only runs after the tests pass.

            Jobs run in parallel by default. The `needs` key makes a job wait. With `needs: test` on the `build` job, the build starts only after every test job succeeds. If a test fails, the build is skipped, and you get feedback without paying for the slow part.

            Today you grow `ci.yml` into the lab's final version, one piece at a time.
        """), "refs": refs("use_jobs", "python")},
        {"h": "Lint, tests and a test report", "body": T("""
            A linter reads your code without running it and flags problems such as unused imports or undefined names. This course uses ruff. Two commands cover lint and formatting:

            - `ruff check .` finds lint problems, and `ruff check --fix .` fixes the safe ones.
            - `ruff format --check .` fails if a file is not formatted, and `ruff format .` formats it.

            Both exit with code 1 when they find a problem, so they fail the step, just like `pytest`.

            Next, a test report. `pytest --junitxml=reports/junit.xml` also writes the results as JUnit XML, a format most tools can read. The runner is deleted after the job, so you save the report as an artifact with `actions/upload-artifact`. You can download it from the run page or with `gh run download`.

            Add `if: ${{ !cancelled() }}` to the upload step. Normally a step is skipped once an earlier step has failed. This condition makes the upload run even after a test failure, which is exactly when you want the report. Artifact names must be unique within a run, so the name includes the Python version.
        """), "refs": refs("artifacts", "upload_artifact")},
        {"h": "Speed up with a cache, widen with a matrix", "body": T("""
            Every job starts on an empty machine, so `pip install` downloads every package again. A cache fixes that. `actions/setup-python` has one built in: set `cache: pip`. It saves pip's download folder after the job, under a key made from a hash of your requirements files. The next run with the same files restores it in seconds. Set `cache-dependency-path: requirements*.txt`, so a change to either requirements file starts a fresh cache.

            A matrix runs one job definition several times with different values. Your app should work on Python 3.13 and 3.14:

            - `matrix: python-version: ["3.13", "3.14"]` under `strategy` creates two jobs.
            - `${{ matrix.python-version }}` passes each value to setup-python.
            - `fail-fast: false` lets both finish, even if one fails. The default cancels the rest.

            The two jobs run at the same time, so the matrix adds almost no waiting. They show up as two separate checks, `test (3.13)` and `test (3.14)`. You need these exact names for the ruleset later today.
        """), "refs": refs("caching", "matrix", "setup_python")},
        {"h": "Check that the Docker image builds", "body": T("""
            Your Dockerfile is code too, and it can break. A wrong `COPY` path, or a package that no longer installs, only shows up when you build. So CI builds the image for every change, without pushing it anywhere.

            The `build` job uses Docker's own actions:

            - `docker/setup-buildx-action` starts a BuildKit builder.
            - `docker/build-push-action` builds the image; with `push: false` it only builds.
            - `cache-from: type=gha` and `cache-to: type=gha,mode=max` keep image layers in the Actions cache.

            The layer cache works like the one on your laptop from Day 6. If `requirements.txt` did not change, the `pip install` layer comes back from the cache, and the build takes seconds. On Day 12, a second workflow uses the same actions with `push: true`.
        """), "refs": refs("build_push")},
        {"h": "Stop broken code from merging", "body": T("""
            CI only protects you if a red result stops the merge. On GitHub you get that with a **ruleset** on `main`, a named list of rules for branches or tags. The older feature, branch protection rules, still works. Rulesets are more flexible: several can apply at once, and anyone with read access can see them.

            A good starter ruleset for `main` has three rules:

            - Require a pull request before merging, so nobody pushes to `main` directly.
            - Require status checks to pass: `test (3.13)`, `test (3.14)` and `build`.
            - Block force pushes, which is on by default.

            Three details trip most people up:

            - On the Free plan, rulesets are only enforced on public repositories.
            - A new ruleset starts as Disabled, so set its enforcement status to Active.
            - A job skipped because its `needs` failed counts as passed, so require the test checks too.

            Since you work alone, leave required approvals at zero. GitHub does not let you approve your own pull request.
        """), "refs": refs("rulesets", "rulesets_create", "req_checks")},
        {"h": "Keep CI fast and cheap", "body": T("""
            Slow CI changes how people work. They stop waiting for it, or they bundle many changes into one big PR. These settings keep it quick:

            - `concurrency` cancels a stale run when you push again to the same branch or PR.
            - `timeout-minutes` stops a hung job early. The default is 360 minutes.
            - `paths-ignore` on `push` skips runs when a push only changes Markdown files.
            - The pip and Docker layer caches keep installs and builds short.

            Never put path filters on `pull_request` when its checks are required. A workflow that is skipped never reports, so its checks stay Pending and block the merge for good. On `main`, the lab lets every run finish, so each merge gets a full result.

            Two tools help before you push. [actionlint](https://github.com/rhysd/actionlint) checks workflow files for mistakes such as typos in keys or bad expressions. [act](https://github.com/nektos/act) runs workflows on your laptop in Docker containers. It is handy for quick tries, but it does not match GitHub's runners exactly, so the real test is still a push.
        """), "refs": refs("concurrency", "skip_runs", "actionlint")},
    ],
    "analogy": "CI is like the final inspection line in a car factory. Quick checks such as the lights and the horn come first, and the slow road test runs only for cars that passed them. The matrix is the same road test on two kinds of road at the same time. The ruleset is the guard at the gate who lets no car out without a fully signed sheet. The analogy breaks because CI inspects a car that does not exist yet: the merged result of your branch and main.",
    "diagram": D11,
    "diagram_caption": "Tests run once per Python version, the build waits for them, and the ruleset allows the merge only when every check is green.",
    "worked": {"title": "A red lint check, fixed in two minutes", "steps": [
        {"say": "A teammate's PR adds `import json` to `app.py` but never uses it. The check `test (3.14)` turns red at the Lint and format check step, and `build` is skipped. You read the failure from the terminal.", "code": T("""
            $ gh pr checks
            $ gh run view --log-failed
        """), "lang": "console"},
        {"say": "The log ends with ruff's report. F401 is the rule for unused imports, and the `[*]` means ruff can fix it. The step failed because ruff exited with code 1.", "code": T("""
            F401 [*] `json` imported but unused
             --> app.py:3:8
              |
            1 | \"\"\"hello-devops: the tiny web app you ship all through the course.\"\"\"
            2 |
            3 | import json
              |        ^^^^
            4 | import os
              |
            Found 1 error.
            [*] 1 fixable with `--fix`.
        """), "lang": "console"},
        {"say": "Check out the PR branch and run the same command locally. You get the same answer in a second, with no waiting for CI.", "code": T("""
            $ gh pr checkout 7
            $ ruff check . --output-format concise
            app.py:3:8: F401 [*] `json` imported but unused
            Found 1 error.
            [*] 1 fixable with `--fix`.
        """), "lang": "console"},
        {"say": "Let ruff fix it, then run everything CI runs, in the same order. All three commands now exit with 0.", "code": T("""
            $ ruff check --fix .
            Found 1 error (1 fixed, 0 remaining).
            $ ruff format --check .
            2 files already formatted
            $ pytest -q
            ...                                                    [100%]
            3 passed in 0.23s
        """), "lang": "console"},
        {"say": "Commit and push to the same branch. The push starts a new run. If the old run were still going, concurrency would cancel it. When all three checks are green, the ruleset unlocks the merge button.", "code": T("""
            $ git commit -am "Remove unused import"
            $ git push
            $ gh pr checks --watch
        """), "lang": "console"},
    ]},
    "code": [
        {"lang": "yaml", "title": ".github/workflows/ci.yml", "src": lab(".github/workflows/ci.yml"),
         "run": "ruff check . && ruff format --check . && pytest -q && git push && gh pr checks --watch"},
    ],
    "commands": [
        {"cmd": "ruff check .", "what": "Lint every Python file; exits with 1 if it finds a problem."},
        {"cmd": "ruff check --fix .", "what": "Fix the lint problems that are safe to fix automatically."},
        {"cmd": "ruff format .", "what": "Format all Python files in place."},
        {"cmd": "pytest -q --junitxml=reports/junit.xml", "what": "Run the tests and also write a JUnit XML report."},
        {"cmd": "gh pr checks --watch", "what": "Watch the checks of the current branch's PR until they finish."},
        {"cmd": "gh pr checkout 7", "what": "Check out the branch of pull request number 7."},
        {"cmd": "gh run download --name junit-py3.14", "what": "Download one artifact from a run; gh asks which run."},
        {"cmd": "gh repo view --json visibility", "what": "Show whether your repository is public or private."},
        {"cmd": "brew install actionlint && actionlint", "what": "Install the workflow linter, then check every file in .github/workflows."},
        {"cmd": "brew install act", "what": "Install act, which runs workflows locally in Docker containers."},
    ],
    "mistake": "Adding a path filter to the `pull_request` trigger to save minutes. A PR that only touches docs then never runs CI, its required checks wait as Pending forever, and the merge stays blocked. Filter only `push`, as the lab does, or skip the expensive work inside the job instead.",
    "real_world": "At PayLoop, the checkout service has a ruleset on main that requires one review and green checks for lint, tests and the image build. The team treats ten minutes as the limit for CI; when it creeps above that, someone adds caching or splits slow tests. Nobody, not even admins, is on the bypass list for main.",
    "task": {
        "title": "Build the full pipeline and protect main",
        "steps": [
            "Check that your repository is public with `gh repo view --json visibility`. On the Free plan, rulesets only work on public repos.",
            "On a branch `ci-pipeline`, grow `ci.yml` into the version in the Files section, one piece at a time: triggers, concurrency, permissions, matrix, cache, lint, report, build.",
            "Before you push, run `ruff check .`, `ruff format --check .` and `pytest -q` on your laptop.",
            "Push, open a PR, and watch it with `gh pr checks --watch`. Expect three checks: `test (3.13)`, `test (3.14)` and `build`.",
            "Download one JUnit report with `gh run download` and open the XML file.",
            "Merge the PR.",
            "In Settings, open Rulesets and create a branch ruleset for `main`: require a pull request and the three status checks, then set enforcement to Active.",
            "Prove it: on a new branch, break a test, open a PR, and confirm that GitHub blocks the merge. Then fix the test and merge.",
        ],
        "hints": [
            "A check name can only be picked once it has run in the repository recently, so merge the pipeline first.",
            "In the ruleset, the default branch is the easiest target to add.",
            "If `build` fails while tests pass, run `docker build .` locally to see the same error.",
        ],
        "done_when": "A PR with a failing test shows the merge as blocked, and the fixed PR merges with three green checks.",
    },
    "explain_back": {
        "prompt": "Explain how your CI pipeline keeps broken code out of main, in 3 to 4 sentences. Mention needs, the matrix and the ruleset.",
        "answer": "Every pull request starts the ci workflow. Lint and tests run first, once per Python version through the matrix, and the build job waits for them with needs. A ruleset on main requires a pull request plus all three checks, test (3.13), test (3.14) and build, so the merge button stays locked until they are green. I list the test checks by name because a skipped build would otherwise count as passed.",
    },
    "recap": [
        "Order checks from cheap to slow: lint, tests, then the Docker build with needs: test.",
        "cache: pip and the gha layer cache make repeat runs fast.",
        "A matrix runs one job per Python version, and each becomes its own check.",
        "Upload test reports with if: ${{ !cancelled() }} so failed runs still leave a report.",
        "A ruleset on main with required checks blocks red pull requests; set it to Active.",
        "concurrency, timeout-minutes and a push-only paths-ignore keep CI quick and cheap.",
    ],
    "check": [
        {"q": "Next year you add Python 3.15 to the matrix. What else must change so the new version protects main?",
         "options": ["Nothing, rulesets pick up new checks on their own", "Add test (3.15) to the ruleset's required checks", "Rename the job to test-3.15", "Turn fail-fast back on"],
         "answer": 1, "why": "Required checks are matched by exact name, so a new matrix check is not required until you add it."},
        {"q": "A PR only changes README.md. The pull_request trigger has a paths-ignore filter for Markdown, and the checks are required. What happens?",
         "options": ["The PR merges at once, because nothing ran", "CI runs anyway, because filters never apply to PRs", "The required checks wait as Pending, and the merge stays blocked", "GitHub marks the checks as skipped and passed"],
         "answer": 2, "why": "A workflow skipped by a path filter never reports, so its required checks stay Pending."},
        {"q": "Your tests pass, but every run spends 90 seconds in pip install. What is the simplest fix?",
         "options": ["Set cache: pip on actions/setup-python", "Add a third Python version to the matrix", "Raise timeout-minutes to 30", "Move pip install into the build job"],
         "answer": 0, "why": "The pip cache restores downloaded packages, so installs take seconds while the requirements files are unchanged."},
    ],
    "interview": [
        {"q": "How would you speed up a slow CI pipeline?",
         "a": "First I measure where the time goes, using the job and step timings on the run page. Then I cache what does not change, such as package downloads and Docker layers. I run independent jobs in parallel, put cheap checks such as lint first, and cancel stale runs with concurrency. If tests are the slow part, I split them across parallel jobs and move slow end-to-end tests to a later stage."},
        {"q": "What are required status checks, and what can go wrong with them?",
         "a": "They are checks named in a ruleset or branch protection rule that must pass before a pull request can merge. They are matched by exact name, so renaming a job or changing a matrix can drop protection until you update the list. A workflow skipped by a path or branch filter leaves its checks Pending and blocks the merge. A job skipped because its dependency failed counts as success, so you must also require the earlier jobs."},
    ],
    "deeper": {"minutes": 12, "body": T("""
        Listing every matrix check in the ruleset works, but it can break quietly. Add Python 3.15 next year and forget the ruleset, and the new check is not required. Rename a job, and the old required name never reports again, so every PR waits forever.

        Many teams fix this with one gate job at the end of the workflow, and they require only that job. The gate has three parts:

        - `needs: [test, build]` makes it wait for every other job.
        - `if: ${{ always() }}` makes it run even when a needed job failed or was skipped.
        - One step runs `exit 1` when `contains(needs.*.result, 'failure')` or `contains(needs.*.result, 'cancelled')` is true.

        `needs.*.result` is a list with the result of each needed job: `success`, `failure`, `cancelled` or `skipped`. The gate turns that list into one clear answer. Here `always()` is a safe choice, because the gate only reads results and runs nothing risky.

        Why not a gate with plain `needs` and no `if`? A failed test would then skip the gate, and a skipped gate counts as passed. That is the same trap as before, one level further down. The `always()` makes the gate honest.

        When is a gate overkill? For a small repository with three checks, listing them is clearer, so the lab does that. Reach for a gate when your matrix grows or when some jobs only run sometimes.

        Two more ruleset settings matter as a team grows. Require branches to be up to date before merging (strict mode) makes each PR pass its checks on top of the newest `main`. It is safer, but a busy repository re-runs CI often. A merge queue solves that at scale. GitHub tests queued PRs together on a temporary branch and merges them in order. Workflows then also need the `merge_group` event, or their required checks never report for the queue.

        Read more in [Troubleshooting required status checks](https://docs.github.com/en/pull-requests/how-tos/merge-and-close-pull-requests/troubleshooting-required-status-checks).
    """)},
    "sources": sources("python", "rulesets", "req_checks", "caching"),
}

# ================================================================= d12
d12 = {
    "id": "d12",
    "title": "Ship it: build and push images safely",
    "minutes": 40,
    "goal": "By the end you can publish a versioned image to GHCR from a git tag, using a least-privilege token, an approval gate and pinned actions.",
    "guess": {
        "q": "Your workflow uses `${{ secrets.GITHUB_TOKEN }}`. Where does that token come from?",
        "options": [
            "You create it once in Settings and paste it in as a secret",
            "GitHub creates a fresh one for each job, and it expires when the job ends",
            "It is your personal password, reused by GitHub",
            "It is shared by all your repositories and never expires",
        ],
        "answer": 1,
        "why": "GitHub makes a new GITHUB_TOKEN at the start of every job, limited to the current repository and the permissions you allow. It stops working when the job finishes.",
    },
    "terms": [
        {"term": "Secret", "plain": "An encrypted value stored in GitHub and given to a workflow only when it asks by name."},
        {"term": "GITHUB_TOKEN", "plain": "A short-lived token GitHub creates for each job, limited to the current repository."},
        {"term": "Least privilege", "plain": "Giving a token or a person only the access the task needs, and nothing more."},
        {"term": "Environment", "plain": "A named deploy target, such as production, that can hold secrets and require approval."},
        {"term": "OIDC (OpenID Connect)", "plain": "A way for a workflow to prove who it is to a cloud and get short-lived keys."},
        {"term": "Reusable workflow", "plain": "A workflow that other workflows call like a function, through on: workflow_call."},
        {"term": "SHA pinning", "plain": "Using an action by its full 40-character commit ID, which nobody can move to other code."},
    ],
    "sections": [
        {"h": "Secrets and variables", "body": T("""
            Some values must never sit in your code: passwords, API keys, cloud credentials. GitHub stores them as secrets. A secret is encrypted, and a workflow only gets it when it asks for it by name, as in `${{ secrets.NAME }}`.

            Secrets and plain variables can live at three levels:

            - Repository: every workflow in the repository can read them.
            - Environment: only jobs that use that environment, such as `production`, can read them.
            - Organization: shared by several repositories, for teams.

            Variables hold settings that are not secret, such as a region or a bucket name. You read them with `${{ vars.NAME }}`. Set both in Settings, or with `gh secret set` and `gh variable set`.

            GitHub hides known secret values in logs as `***`, but do not rely on that. A secret that is changed, for example base64 encoded, is not hidden. Never `echo` a secret, never put a whole JSON file in one secret, and rotate any secret that leaks. Pull requests from forks get no secrets at all.
        """), "refs": refs("secrets", "use_secrets")},
        {"h": "GITHUB_TOKEN and least privilege", "body": T("""
            Every job gets a token without asking: the `GITHUB_TOKEN`. GitHub creates it when the job starts, and it expires when the job ends. It only works on the current repository. Actions in the job can use it even if you never pass it to them, so its power matters.

            **Least privilege** means a token gets only the access its task needs. You control that with the `permissions` key:

            - At the top of the workflow, set the default for every job, such as `contents: read`.
            - In a job that needs more, set its own `permissions`, such as `packages: write`.
            - Any permission you do not list is set to `none`.

            So the release job can push images, while every other job can only read code. If an action in a read-only job is ever compromised, it cannot push a fake image or change your code. Your `ci.yml` from Day 11 already starts with `contents: read` for this reason.
        """), "refs": refs("token", "token_tut")},
        {"h": "From a git tag to an image in GHCR", "body": T("""
            Now the payoff. When you push a tag such as `v1.0.0`, `release.yml` builds the image and pushes it to GitHub Container Registry (GHCR), at `ghcr.io/<you>/hello-devops`. The job runs these steps:

            1. `actions/checkout` fetches the code at the tag.
            2. The QEMU and Buildx setup actions prepare a builder for amd64 and arm64 images.
            3. `docker/login-action` logs in to `ghcr.io` with the `GITHUB_TOKEN`.
            4. `docker/metadata-action` turns the git tag into the image tags `1.0.0`, `sha-<commit>` and `latest`.
            5. `docker/build-push-action` builds both architectures with `APP_VERSION=1.0.0` and pushes them.

            The image is built once, from the tag. Later stages deploy this exact image by its digest, which the last step writes to the run summary. Day 22 adds a scan, an SBOM and a signature to this job.

            A new GHCR package is private, even when the repository is public. To pull it, make it public in its package settings, or log in with a personal access token (classic) that has the `read:packages` scope.
        """), "refs": refs("publish_images", "ghcr", "pkg_visibility")},
        {"h": "Environments: a human approval gate", "body": T("""
            An environment is a named deploy target, such as `staging` or `production`. A job opts in with `environment: production`. Before that job starts, GitHub checks the environment's protection rules:

            - Required reviewers: up to six people or teams, and one approval lets the job go on.
            - Wait timer: a delay before the job may start.
            - Deployment branches and tags: for example, only tags matching `v*` may deploy.

            Environment secrets are only handed over after the rules pass. So the approval is also a gate for credentials.

            Plan limits matter here. On the Free, Pro and Team plans, required reviewers only work in public repositories. Private repositories need GitHub Enterprise for them. If a workflow names an environment that does not exist yet, GitHub creates it with no rules, and the job runs right away.
        """), "refs": refs("envs", "manage_envs")},
        {"h": "OIDC: cloud access without stored keys", "body": T("""
            To deploy to a cloud such as AWS, a workflow needs credentials. The old way is to store an access key as a secret. That key lives for months, works from anywhere, and is painful to rotate.

            OpenID Connect (OIDC) removes the stored key. It works in five steps:

            1. The job asks GitHub for a signed ID token, which needs `id-token: write` in `permissions`.
            2. The token states facts: this repository, this branch or environment, this workflow.
            3. The job sends the token to AWS and asks to use an IAM role.
            4. AWS checks the signature and compares the facts with the role's trust policy.
            5. If they match, AWS returns keys that expire after one hour by default.

            The `aws-actions/configure-aws-credentials` action handles steps 1, 3 and 5 for you. You give it the role ARN and a region. The worked example shows the workflow side, and Day 15 creates the IAM role and its trust policy for real.
        """), "refs": refs("oidc", "oidc_aws", "aws_action")},
        {"h": "Reuse and supply-chain safety", "body": T("""
            As workflows grow, two features stop copy and paste:

            - A reusable workflow has `on: workflow_call`. Other workflows call it as a job, with `uses:` and the file path.
            - A composite action bundles several steps in an `action.yml` file, used as one step.

            Every action you call is someone else's code, running with your token and your secrets. Three habits protect you:

            - Pin third-party actions to a full commit SHA, and keep the version in a comment.
            - Turn on Dependabot for `github-actions`, so it opens PRs that update versions and pins.
            - Avoid `pull_request_target` together with code from the pull request.

            Why a SHA? A tag such as `v4` can be moved to different code by anyone who controls the action's repository. A commit SHA always means the same code. Why avoid `pull_request_target`? It runs with secrets and a write token, even for pull requests from forks. If the job then runs the fork's build script, a stranger's code gets your secrets. GitHub is adding guard rails, but the safe choice is plain `pull_request`. Day 22 shows real attacks where these habits would have helped.
        """), "refs": refs("reuse", "secure_use", "prt")},
    ],
    "analogy": "The GITHUB_TOKEN is like a hotel key card. The front desk makes a new card for each stay, it only opens the doors you booked, and it stops working at checkout. A long-lived cloud key is like a copied master key: it opens many doors for years, so losing it is a disaster. OIDC is showing your passport at the desk to get a fresh card each time. The analogy breaks because one guest holds a key card, while every action in a job can use the token.",
    "diagram": D12,
    "diagram_caption": "A version tag starts the release: an approval gate, then an amd64 and arm64 build pushed to GHCR with a write-scoped, short-lived token.",
    "worked": {"title": "Make a risky deploy workflow safe", "steps": [
        {"say": "Here is a deploy workflow like ones you may find in older repositories. Look for problems before you read on.", "code": T("""
            name: deploy
            on: push
            permissions: write-all
            jobs:
              deploy:
                runs-on: ubuntu-latest
                steps:
                  - uses: actions/checkout@v7
                  - run: echo "Using key ${{ secrets.AWS_ACCESS_KEY_ID }}"
                  - run: aws s3 sync ./site s3://hello-devops-site
                    env:
                      AWS_ACCESS_KEY_ID: ${{ secrets.AWS_ACCESS_KEY_ID }}
                      AWS_SECRET_ACCESS_KEY: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
        """), "lang": "yaml"},
        {"say": "It deploys from any branch, its token can write everything, it prints a secret, and it uses long-lived AWS keys. Fix the trigger and the default permissions first.", "code": T("""
            name: deploy
            on:
              push:
                branches: [main]
            permissions:
              contents: read
        """), "lang": "yaml"},
        {"say": "Give the job an environment, so it waits for approval. Then grant only the extra permission OIDC needs. `id-token: write` lets the job ask for an ID token; it gives no write access to your repository.", "code": T("""
            jobs:
              deploy:
                runs-on: ubuntu-latest
                environment: production
                permissions:
                  contents: read
                  id-token: write
        """), "lang": "yaml"},
        {"say": "Replace the stored keys with OIDC. This third-party action receives cloud access, so pin it to a full SHA. Settings that are not secret come from variables, and the bucket name reaches the shell through `env`.", "code": T("""
                steps:
                  - uses: actions/checkout@v7
                  - uses: aws-actions/configure-aws-credentials@e1253824e5c10ff9df46874f81ed3ec929e19cfd # v6.3.0
                    with:
                      role-to-assume: ${{ vars.AWS_ROLE_ARN }}
                      aws-region: eu-west-1
                  - run: aws s3 sync ./site "s3://$BUCKET"
                    env:
                      BUCKET: ${{ vars.SITE_BUCKET }}
        """), "lang": "yaml"},
        {"say": "Finish the switch. The IAM role's trust policy accepts only tokens from this repository's production environment (Day 15 builds it). Then delete the old key secrets here, and deactivate the keys in AWS, so a leaked copy is useless.", "code": T("""
            $ gh variable set AWS_ROLE_ARN --body arn:aws:iam::123456789012:role/hello-devops-deploy
            $ gh variable set SITE_BUCKET --body hello-devops-site
            $ gh secret delete AWS_ACCESS_KEY_ID
            $ gh secret delete AWS_SECRET_ACCESS_KEY
        """), "lang": "console"},
    ]},
    "code": [
        {"lang": "yaml", "title": ".github/workflows/release.yml", "src": lab(".github/workflows/release.yml"),
         "run": "git tag -a v1.0.0 -m \"Release 1.0.0\" && git push origin v1.0.0 && gh run watch"},
        {"lang": "yaml", "title": ".github/dependabot.yml", "src": lab(".github/dependabot.yml"),
         "run": "git add .github/dependabot.yml && git commit -m \"Let Dependabot update actions\" && git push"},
    ],
    "commands": [
        {"cmd": "git tag -a v1.0.0 -m \"Release 1.0.0\"", "what": "Create an annotated version tag on the current commit."},
        {"cmd": "git push origin v1.0.0", "what": "Push the tag, which starts release.yml."},
        {"cmd": "gh run watch", "what": "Follow the release run; it waits while the approval is pending."},
        {"cmd": "gh secret set API_KEY", "what": "Store a repository secret; gh asks for the value, so it stays out of your shell history."},
        {"cmd": "gh variable set AWS_REGION --body eu-west-1", "what": "Store a plain variable that is not secret."},
        {"cmd": "docker pull ghcr.io/<you>/hello-devops:1.0.0", "what": "Download your released image from GHCR."},
        {"cmd": "docker buildx imagetools inspect ghcr.io/<you>/hello-devops:1.0.0", "what": "Show the digest and the platforms (amd64, arm64) behind a tag."},
        {"cmd": "echo \"$CR_PAT\" | docker login ghcr.io -u <you> --password-stdin", "what": "Log in to GHCR with a classic token; needed to pull a private package."},
        {"cmd": "git ls-remote --tags https://github.com/docker/login-action", "what": "List an action's tags with their commit SHAs, so you can pin by SHA."},
    ],
    "mistake": "The push to GHCR fails with `denied` even though the job has `packages: write`. This usually means the package already exists, for example from your manual push on Day 8, and is not linked to this repository. Open the package settings, add `hello-devops` under Manage Actions access with the Write role, and re-run the job.",
    "real_world": "At PayLoop, only the release workflow may push images, and it only runs for version tags. Production deploys wait in a protected environment until an engineer from the on-call rotation approves. No CI system holds long-lived cloud keys: each job gets short-lived AWS credentials through OIDC, with one role per environment.",
    "task": {
        "title": "Release v1.0.0 to GHCR",
        "steps": [
            "On a branch, add `.github/workflows/release.yml` and `.github/dependabot.yml` from the Files section. Open a PR, let CI pass, and merge it.",
            "In Settings, open Environments and create `production`. Add yourself as a required reviewer, leave Prevent self-review off, and save.",
            "Under Deployment branches and tags, choose Selected branches and tags, and add a tag rule for `v*`.",
            "Update `main` locally, create the annotated tag `v1.0.0`, and push it.",
            "Follow the run. When it waits, open it in the browser, click Review deployments, and approve.",
            "When it is green, read the digest in the run summary, and list the platforms with `docker buildx imagetools inspect`.",
            "Make the package public in its package settings, or log in to GHCR with a classic token that has `read:packages`.",
            "Pull and run the image on your Mac with port 8000 mapped, then call `curl localhost:8000`.",
        ],
        "hints": [
            "If the job never asks for approval, check that the environment name in the workflow matches exactly.",
            "Push tags one at a time. GitHub creates no events when more than three tags are pushed at once.",
            "If you pushed 1.0.0 by hand on Day 8, this release replaces that tag with a new digest.",
        ],
        "done_when": "`curl localhost:8000` against the image you pulled from GHCR shows `\"version\": \"1.0.0\"`.",
    },
    "explain_back": {
        "prompt": "Explain how your release workflow keeps credentials safe, in 3 to 4 sentences. Mention GITHUB_TOKEN permissions, the environment and SHA pinning.",
        "answer": "The workflow gives every job a read-only GITHUB_TOKEN, and only the image job gets packages: write, so nothing else can push. The token is created for that job and expires when it ends, so there is no long-lived password to leak. The job uses the production environment, so it waits for my approval before it runs and before any environment secrets are released. The third-party Docker actions are pinned to full commit SHAs, so nobody can swap their code by moving a tag.",
    },
    "recap": [
        "Secrets are encrypted and read by name; never print them, and rotate any that leak.",
        "Set permissions: contents: read at the top, and grant more only in the job that needs it.",
        "A v* tag triggers release.yml, which builds amd64 and arm64 images and pushes them to GHCR.",
        "Environments with required reviewers pause a job until a person approves it.",
        "OIDC replaces long-lived cloud keys with short-lived ones tied to your repository and environment.",
        "Pin third-party actions to full SHAs, let Dependabot update them, and keep PR code away from pull_request_target.",
    ],
    "check": [
        {"q": "A job only runs tests and then posts a comment on the PR. Which permissions fit least privilege?",
         "options": ["permissions: write-all", "contents: read and pull-requests: write", "contents: write and packages: write", "No permissions key at all"],
         "answer": 1, "why": "The job needs to read code and write one comment, and nothing else."},
        {"q": "A new teammate wants to deploy to AWS by saving an IAM user's access key as a repository secret. What do you suggest?",
         "options": ["Use OIDC with an IAM role and short-lived keys", "Put the key in the workflow file so it gets reviewed", "Base64 encode the key before saving it", "Save the key as a variable so it is easy to see"],
         "answer": 0, "why": "OIDC gives each job keys that expire soon and removes the stored secret."},
        {"q": "Every production release must wait for a human. The repository is public, on the Free plan. What do you use?",
         "options": ["A wait timer of 60 minutes", "A repository secret named APPROVAL", "A schedule trigger", "An environment with required reviewers"],
         "answer": 3, "why": "Required reviewers on an environment pause the job until one of them approves."},
    ],
    "interview": [
        {"q": "Why use OIDC instead of storing cloud access keys in CI?",
         "a": "Stored keys live a long time and work from anywhere, so a leak gives an attacker access until someone notices and rotates them. With OIDC, the workflow proves who it is with a signed token, and the cloud returns credentials that expire soon. The cloud's trust policy can limit access to one repository, branch or environment. There is no secret to rotate or leak, and each role can follow least privilege."},
        {"q": "How do you protect a CI/CD pipeline from a compromised third-party action?",
         "a": "I pin every third-party action to a full commit SHA, so a moved tag cannot change the code I run, and I review Dependabot's update PRs. I keep the GITHUB_TOKEN read-only by default and grant write access only to the job that needs it. I keep deploy credentials in environments behind approvals, and prefer OIDC over stored keys. I also avoid patterns such as pull_request_target that run untrusted code with secrets, and I use fewer actions where a short shell step will do."},
    ],
    "deeper": {"minutes": 13, "body": T("""
        The ID token that GitHub gives your job is a JSON Web Token (JWT): a small JSON document, signed by GitHub and encoded as text. Its fields are called claims. Four of them matter most:

        - `iss` (issuer) is `https://token.actions.githubusercontent.com`, so the cloud knows who signed it.
        - `aud` (audience) says who the token is for; the AWS action asks for `sts.amazonaws.com`.
        - `sub` (subject) says which workflow is calling, for example `repo:octo-org/octo-repo:environment:production`.
        - `exp` says when the token expires.

        The real security lives on the cloud side. The IAM role's trust policy decides which tokens it accepts. A strict policy checks `aud` and the exact `sub`. A loose policy, such as one that matches `repo:octo-org/*`, lets every repository in that account assume the role. Always pin `sub` to one repository, plus a branch or an environment.

        The `sub` value depends on the job:

        - A job with `environment: production` gets a subject ending in `environment:production`.
        - A job running on a branch gets one ending in `ref:refs/heads/main`.
        - A job started by a pull request gets one ending in `pull_request`.

        So you can give the production role only to production jobs, and a read-only role to pull request jobs.

        One recent change affects your repository. Repositories created after July 15, 2026 use an immutable subject format that includes numeric IDs, for example `repo:octo-org@123456/octo-repo@456789:ref:refs/heads/main`. This stops someone who later takes over a deleted account name from matching an old trust policy. Your hello-devops repository is new, so copy the exact format from the [OIDC reference](https://docs.github.com/en/actions/reference/security/oidc) when you write the trust policy on Day 15.

        Two habits complete the picture. Ask for `id-token: write` only in the job that deploys, not for the whole workflow. And pair OIDC with environments: protection rules must pass before the job reaches a runner, so no token exists until a person has approved.
    """)},
    "sources": sources("secure_use", "token", "publish_images", "oidc_aws"),
}

# ================================================================= part
part = {
    "part": 3,
    "title": "CI/CD with GitHub Actions",
    "intro": "Until now you built, tested and packaged hello-devops by hand. In this part GitHub does it for you. Every pull request is linted, tested and built, broken code cannot reach main, and a version tag publishes a release image on its own. It comes now because you have a tested app and a production-ready image, which is exactly what a pipeline needs.",
    "lessons": [d09, d10, d11, d12],
    "recap": [
        "Small branches and pull requests, with review and CI, are how teams change code safely.",
        "CI tests every change; continuous delivery keeps it releasable; continuous deployment releases it automatically.",
        "A workflow is YAML in .github/workflows: events start jobs, and jobs run steps on fresh runners.",
        "The lab's ci.yml lints, tests on Python 3.13 and 3.14, saves a JUnit report and checks the Docker build.",
        "A ruleset with required checks keeps red pull requests out of main.",
        "release.yml turns a v* tag into an amd64 and arm64 image in GHCR, built once and named by digest.",
        "Least privilege everywhere: read-only tokens by default, OIDC instead of stored keys, approvals for production.",
        "Pin third-party actions to commit SHAs and let Dependabot keep them current.",
    ],
    "flashcards": [
        {"front": "Continuous delivery vs continuous deployment?", "back": "Delivery: every change is releasable and a person clicks release. Deployment: every passing change goes live automatically."},
        {"front": "What does 'build once, deploy many' mean?", "back": "Build the image one time and promote that same digest through every environment."},
        {"front": "In semver 2.4.1, which number changes for a compatible bug fix?", "back": "PATCH, so the next version is 2.4.2."},
        {"front": "Canary vs blue/green deployment?", "back": "Canary sends a small share of traffic to the new version first; blue/green switches all traffic between two full copies."},
        {"front": "Where must workflow files live?", "back": "In .github/workflows/ at the repository root, as .yml or .yaml files."},
        {"front": "uses: vs run: in a step?", "back": "uses: calls a published action; run: executes shell commands."},
        {"front": "What makes a step fail?", "back": "A command that ends with a non-zero exit code."},
        {"front": "What does needs: test do on a job?", "back": "The job waits until the test job succeeds; if test fails, the job is skipped."},
        {"front": "Why add if: ${{ !cancelled() }} to an upload step?", "back": "So it runs even after an earlier step failed, unless the run was cancelled."},
        {"front": "Why not require only the last job of a needs chain?", "back": "If an earlier job fails, the last job is skipped, and a skipped check counts as passed."},
        {"front": "Why put paths-ignore on push but not on pull_request?", "back": "A required check skipped by a path filter stays Pending and blocks the merge."},
        {"front": "What does permissions: contents: read at the top of a workflow do?", "back": "Makes every job's GITHUB_TOKEN read-only for code; unlisted permissions become none."},
        {"front": "How long does a GITHUB_TOKEN live?", "back": "From the start of its job until the job ends."},
        {"front": "Which permission lets a job request an OIDC token?", "back": "id-token: write"},
        {"front": "Why pin an action to a full commit SHA?", "back": "A tag can be moved to other code; a commit SHA always means the same code."},
        {"front": "Is a new GHCR package public or private?", "back": "Private. Make it public in its package settings, or pull with a read:packages token."},
    ],
    "quiz": [
        {"q": "A colleague's branch has lived for three weeks and touches 40 files. What problem is most likely at merge time?",
         "options": ["Big merge conflicts and a review nobody can check well", "GitHub refuses branches older than two weeks", "The tags on main move to the branch", "CI stops running on old branches"],
         "answer": 0, "why": "Long-lived, large branches drift from main, so conflicts and shallow reviews pile up."},
        {"q": "Which event lets you start a workflow with a button in the Actions tab?",
         "options": ["schedule", "repository_dispatch", "workflow_dispatch", "pull_request"],
         "answer": 2, "why": "workflow_dispatch adds the Run workflow button once the file is on the default branch."},
        {"q": "Why does the lab's ci.yml put the Python version in the artifact name?",
         "options": ["GitHub sorts artifacts by Python version", "upload-artifact only accepts names with numbers", "It makes the pip cache key match", "Each matrix job needs a unique artifact name"],
         "answer": 3, "why": "Each matrix job uploads its own report, and two artifacts in one run cannot share a name."},
        {"q": "In release.yml, which permission lets the GITHUB_TOKEN push images to GHCR?",
         "options": ["contents: write", "packages: write", "id-token: write", "actions: write"],
         "answer": 1, "why": "GHCR is part of GitHub Packages, so pushing needs packages: write."},
        {"q": "You push the tag v2.3.0. Which image tags does the lab's metadata-action produce?",
         "options": ["v2.3.0, main and latest", "only v2.3.0, exactly as pushed", "2.3.0, sha-<commit> and latest", "2.3, 2 and edge"],
         "answer": 2, "why": "type=semver with {{version}} gives 2.3.0, type=sha gives sha-<commit>, and latest is added for semver tags."},
        {"q": "Why pin docker/login-action to a full commit SHA instead of @v4?",
         "options": ["A tag can be moved; a commit SHA cannot", "SHA pins make the action run faster", "GitHub rejects tags for third-party actions", "Dependabot only works with tags"],
         "answer": 0, "why": "Whoever controls the action's repository can move a tag; a full SHA always names the same code."},
        {"q": "A CI step ends with `grep ERROR app.log`, and the log contains no errors. What happens to the step?",
         "options": ["It passes, because no errors were found", "It fails, because grep exits with 1 when nothing matches", "It passes with a warning about the empty result", "It fails, because grep needs sudo"],
         "answer": 1, "why": "grep returns exit code 1 when it finds no match, and any non-zero exit code fails the step.", "from": "Part 1"},
        {"q": "release.yml pushed ghcr.io/you/hello-devops:1.0.0. Someone later re-pushes that tag with a new build. How should production point at the exact image you tested?",
         "options": ["Use the latest tag", "Rebuild the image during the deploy", "Use the 1.0.0 tag and hope", "Use the image digest, sha256:..."],
         "answer": 3, "why": "Tags can be moved to other images; a digest names exact content and never changes.", "from": "Part 2"},
    ],
}

OUT.write_text(json.dumps(part, ensure_ascii=False, indent=1) + "\n")
print("wrote", OUT)
