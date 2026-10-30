"""Day 17: Git, pull requests and CI/CD ideas (first edition d09)."""
from common import T, box, cap, lab, line, link, refs, sources, svg

DIAGRAM = svg(210, "A change moves from a branch to a pull request with CI checks and review, then merges to main and gets a version tag", [
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

S1 = T("""
When you work alone, committing straight to `main` is fine. With a team it breaks fast. Two people edit the same file and one person's work disappears. Or `main` ends up with code that does not even start, and everyone who pulls it is stuck.

Branches fix this. A **branch** is a movable label that points at a commit. When you commit on your branch, your label moves forward and the `main` label stays where it was. Nothing on `main` changes until you merge. Creating a branch costs almost nothing: git writes one small file that holds a commit ID.

The everyday loop has four steps:

1. Create a branch from the latest `main`, for example `git switch -c add-pr-template`.
2. Change files and commit in small steps, each with a message that says why.
3. Push the branch to GitHub and open a pull request.
4. Merge it into `main` once it is reviewed and tested, then delete the branch.

Keep branches short. A branch that lives for an afternoon merges easily. A branch that lives for three weeks drifts away from `main`, and every day it gets harder to bring back.
""")

S2 = T("""
While you work, `main` moves on. A teammate merged two pull requests this morning. Git gives you two ways to combine your branch with their work.

A merge joins the two lines of work with a new merge commit that has two parents. Your commits keep their IDs, and the history shows exactly what happened, side branch and all.

A rebase replays your commits on top of the newest `main`, as if you had started your branch today. The history becomes one straight line, but every replayed commit gets a new ID. So the rule is simple: rebase only branches that nobody else uses. After a rebase, push with `git push --force-with-lease`, which refuses to overwrite commits on GitHub that you have not seen.

Either way, git compares both sides with their merge base, the last commit they share. If only one side changed a part of a file, git takes that change. If both sides changed the same lines in different ways, git stops and asks you. That is a merge conflict. Git marks the clash in the file with `<<<<<<<`, `=======` and `>>>>>>>`. You edit the file until it says what it should, then `git add` it and commit. If you get lost, `git merge --abort` puts everything back.

One thing git never checks is whether the merged code still works. The worked example shows why that is the tests' job.
""")

S3 = T("""
A pull request (PR) is a GitHub page that asks to merge your branch into `main`. It shows the diff (the lines you changed), a conversation, and the results of automatic checks. Teams use it for three separate things:

- Review: a teammate reads the change and comments on single lines.
- Checks: CI runs the tests and shows a green tick or a red cross.
- A record: a year later you can see why a line changed and who agreed.

Small pull requests get real reviews. A 40-line change tends to get careful comments, and a 2,000-line change tends to get a quick "looks good". Aim for something a reviewer can read in ten minutes. Open it early as a draft if you want feedback before it is finished. In the description, say what changed and how you tested it. The PR template you add today asks those questions for you.

When you review someone else's PR, read the description first, then the tests, then the code. Ask questions instead of giving orders: "what happens here if Redis is down?" Be kind to the person and strict about the code.

Two details surprise people. GitHub tests a pull request on a temporary merge of your branch into `main`, not on your branch alone. And while a PR has a merge conflict, its `pull_request` workflows do not run at all.
""")

S4 = T("""
Your team also has to agree how long branches live and where releases come from. That agreement is the branching strategy, and two styles are common.

In trunk-based development, everyone merges small branches into one main branch, the trunk, at least once a day. A branch lives for hours or a day or two, and `main` is always in a state you could release. Unfinished work is merged too, but switched off behind a feature flag: a setting that turns code on or off without a new deploy.

GitFlow uses several long-lived branches:

- `main` holds released code only.
- `develop` collects finished features.
- `feature/...` branches start from `develop`.
- `release/...` and `hotfix/...` branches prepare and patch releases.

GitFlow fits software that ships a big version a few times a year, or that must patch several old versions at once. If you deploy every week or more often, it gets in your way. Long-lived branches drift apart, and merging them back is slow and risky. For a web service like hello-devops I would pick trunk-based every time. This course uses {gh_flow}, GitHub's own simple version of it: branch, pull request, review, merge.
""").format(gh_flow=link("gh_flow", "GitHub flow"))

S5 = T("""
Continuous integration (CI) means everyone merges small changes often, and a server builds and tests every change automatically. You hear about a broken test minutes after you push, while you still remember what you changed. {fowler} is the classic description and worth an evening.

CD has two meanings, and people mix them up:

- Continuous delivery: every change that passes is ready to release. A person decides when it goes to production, often with one click.
- Continuous deployment: every change that passes goes to production on its own. Nobody clicks anything.

The steps a change goes through form a pipeline. A typical one runs in this order:

1. Build: install dependencies and package the code.
2. Test: run linters and automated tests.
3. Publish: build a container image and push it to a registry.
4. Deploy: release that image to staging, then to production.

Build the image once, at the publish step. This rule is called **build once, deploy many**: the very same image, with the same digest from Day 12, moves from staging to production. If you rebuilt it for production, the build could pull newer packages, and what you ship would no longer be what you tested. Each step you automate here also moves the DORA metrics from Day 1, such as how often you deploy and how long a change takes to reach users.
""").format(fowler=link("fowler_ci", "Martin Fowler's article on continuous integration"))

S6 = T("""
Deploying means swapping the old version for the new one while users keep working. Four ways are common:

- Rolling: replace servers or containers a few at a time. Kubernetes does this by default (Day 32).
- Blue/green: run the new version (green) next to the old one (blue), then switch all traffic at once.
- Canary: send a small share of traffic, say 5%, to the new version, then grow it step by step.
- Feature flags: ship new code switched off, then turn it on for some users with a setting.

Each one has a cost. Rolling needs no extra servers, but for a few minutes old and new versions serve users side by side, so both must work with the same database. Blue/green gives you an instant rollback and costs double the capacity during the switch. A canary limits the damage of a bad release, as long as you have good metrics to judge it (Part 9 builds them). Feature flags need no deploy at all. You pay for them later, with `if` branches in the code that someone has to clean up.

On Kubernetes, {rollouts} automates blue/green and canary releases. For hello-devops, the rolling update Kubernetes gives you for free is plenty.
""").format(rollouts=link("rollouts", "Argo Rollouts"))

S7 = T("""
A version number tells users how much changed. {semver} uses three numbers, MAJOR.MINOR.PATCH:

- MAJOR goes up when you break compatibility, as in 2.0.0.
- MINOR goes up when you add a feature that stays compatible, as in 1.3.0.
- PATCH goes up for a compatible bug fix, as in 1.2.1.

A pre-release adds a label after a dash, as in `1.3.0-rc.1`, and counts as older than `1.3.0`.

A git tag is a name for one commit, such as `v1.2.0`. A branch label moves forward with each new commit, but a tag stays where you put it. Use annotated tags (`git tag -a`), which also store who made the tag, when, and a message.

In this course a tag is what starts a release. On Day 21, pushing the tag `v1.0.0` starts a workflow that builds and publishes the image `1.0.0`. The git tag, the image tag and the app's `version` field then all match. One catch: a plain `git push` does not send tags. Push each tag by name, as in `git push origin v1.0.0`.
""").format(semver=link("semver", "Semantic versioning"))

LESSON = {
    "id": "d17",
    "title": "Git, pull requests and CI/CD ideas",
    "minutes": 45,
    "goal": "By the end you can open, review and merge a pull request with gh, fix a merge conflict, tag a version, and tell continuous integration, delivery and deployment apart.",
    "guess": {
        "q": "Your new team says it practices continuous deployment. What does that mean?",
        "options": [
            "Everyone merges code into main at least once a day",
            "Every change is ready to release, and a person clicks to ship it",
            "Every change that passes the pipeline reaches production with no human step",
            "The production servers are never switched off",
        ],
        "answer": 2,
        "why": "With continuous deployment, every change that passes the pipeline goes live and nobody clicks anything. Merging daily is continuous integration, and a human release click is continuous delivery.",
    },
    "terms": [
        {"term": "Branch", "plain": "A movable label on a line of commits, so you can work without touching main."},
        {"term": "Pull request (PR)", "plain": "A GitHub page that asks to merge one branch into another, with review and checks."},
        {"term": "Merge conflict", "plain": "Two branches changed the same lines, so git asks a person to pick the result."},
        {"term": "Rebase", "plain": "Replaying your commits on top of another branch, which gives them new IDs."},
        {"term": "Continuous integration (CI)", "plain": "Merging small changes often, with an automatic build and test for every change."},
        {"term": "Continuous delivery", "plain": "Every change that passes the pipeline is ready to release, and a person decides when."},
        {"term": "Continuous deployment", "plain": "Every change that passes the pipeline goes to production with no human step."},
        {"term": "Semantic versioning", "plain": "Version numbers in the form MAJOR.MINOR.PATCH that show how big a change is."},
    ],
    "sections": [
        {"h": "Git for teams: branches and the everyday loop", "body": S1, "refs": refs("about_git", "progit")},
        {"h": "Merge, rebase and conflicts", "body": S2, "refs": refs("progit_rebase", "conflict_cli", "skill_conflicts")},
        {"h": "Pull requests and code review", "body": S3, "refs": refs("about_prs", "review_qs", "v_gh_pr")},
        {"h": "Trunk-based development and GitFlow", "body": S4, "refs": refs("gh_flow", "tbd", "fowler_branching")},
        {"h": "CI, continuous delivery and continuous deployment", "body": S5, "refs": refs("ci", "cd", "fowler_ci")},
        {"h": "Deployment strategies: how a new version reaches users", "body": S6, "refs": refs("rollouts", "sre")},
        {"h": "Semantic versions and git tags", "body": S7, "refs": refs("semver", "releases")},
    ],
    "analogy": "A pull request works like a suggested edit in a shared document. You write on your own copy, a colleague reads the suggestion and comments, and the owner accepts it into the main text. CI is a spell checker that runs on every suggestion before anyone reads it. The picture breaks in one place: a document has one text, while git keeps many parallel copies and combines them line by line.",
    "diagram": DIAGRAM,
    "diagram_caption": "One change: a short branch, a pull request with checks and review, a merge, then a tag for the release.",
    "worked": {
        "title": "Resolve a merge conflict, then catch what git missed",
        "steps": [
            {
                "say": "Two branches changed the same line of `app.py`. On `main`, a teammate changed the default greeting to 'Hello, DevOps team!' and updated the test to match. On your branch `friendly`, you changed it to 'Hi there, DevOps!'. Git cannot keep both on its own, so the merge stops.",
                "code": T("""
                    $ git switch main
                    $ git merge friendly
                    Auto-merging app.py
                    CONFLICT (content): Merge conflict in app.py
                    Automatic merge failed; fix conflicts and then commit the result.
                """),
                "lang": "console",
            },
            {
                "say": "`git status --short` shows `UU`: both sides changed the file, and it is not merged yet. Find the clash with grep.",
                "code": T("""
                    $ git status --short
                    UU app.py
                    $ grep -n -A4 "<<<<<<<" app.py
                    12:<<<<<<< HEAD
                    13-GREETING = os.getenv("GREETING", "Hello, DevOps team!")
                    14-=======
                    15-GREETING = os.getenv("GREETING", "Hi there, DevOps!")
                    16->>>>>>> friendly
                """),
                "lang": "console",
            },
            {
                "say": "Above `=======` is the branch you are on (HEAD, here `main`). Below it is the branch coming in. You decide the result. Here you combine both ideas into one line and delete all three marker lines.",
                "code": 'GREETING = os.getenv("GREETING", "Hi there, DevOps team!")',
                "lang": "python",
            },
            {
                "say": "`git add` tells git the conflict is solved. Commit, and the graph shows the two lines of work joined by a merge commit with two parents.",
                "code": T("""
                    $ git add app.py
                    $ git commit -m "Merge friendly: keep both ideas"
                    $ git log --oneline --graph
                    *   1a190aa Merge friendly: keep both ideas
                    |\\
                    | * d301b30 Friendlier greeting
                    * | 1ab720f Greet the team
                    |/
                    * da23b48 Add greeting
                """),
                "lang": "console",
            },
            {
                "say": "Run the tests before you push. Git only checked that the text merged cleanly. The teammate's test still expects 'Hello, DevOps team!', so it fails. You fix `test_app.py` and commit again. Breaks like this are exactly what CI catches on a pull request.",
                "code": T("""
                    $ pytest -q | tail -2
                    FAILED test_app.py::test_index_says_hello - AssertionError: assert 'Hi there,...
                    1 failed, 2 passed in 0.21s
                """),
                "lang": "console",
            },
        ],
    },
    "code": [
        {
            "lang": "text",
            "title": ".github/pull_request_template.md",
            "src": lab(".github/pull_request_template.md"),
            "run": "git add .github/pull_request_template.md && git commit -m \"Add a pull request template\"",
        },
    ],
    "commands": [
        {"cmd": "git switch -c add-pr-template", "what": "Create a new branch from where you are and switch to it."},
        {"cmd": "git push -u origin add-pr-template", "what": "Push the branch to GitHub and remember the link, so later pushes need no names."},
        {"cmd": "gh pr create --fill", "what": "Open a pull request. `--fill` uses your commit message as the title and body."},
        {"cmd": "gh pr view --web", "what": "Open the pull request for the current branch in your browser."},
        {"cmd": "gh pr checkout 7", "what": "Check out the branch of pull request number 7, for example to review it locally."},
        {"cmd": "gh pr merge --squash --delete-branch", "what": "Merge the PR as one commit, then delete the branch locally and on GitHub."},
        {"cmd": "git switch main && git pull", "what": "Go back to main and download the merged result."},
        {"cmd": "git log --oneline --graph", "what": "Show history as a compact graph of branches and merges."},
        {"cmd": "git merge --abort", "what": "Give up on a merge with conflicts and go back to how things were."},
        {"cmd": "git rebase main", "what": "Replay your branch's commits on top of the newest main (only on your own branch)."},
        {"cmd": "git push --force-with-lease", "what": "Push a rebased branch, but refuse if GitHub has commits you have not seen."},
        {"cmd": "git tag -a v0.1.0 -m \"First tagged version\"", "what": "Create an annotated tag on the current commit."},
        {"cmd": "git push origin v0.1.0", "what": "Send one tag to GitHub. A plain `git push` does not send tags."},
        {"cmd": "gh pr list --state merged", "what": "List pull requests that were merged."},
    ],
    "mistake": "The classic mistake is a big branch that lives for days and ends as one huge pull request. Reviewers can only skim it, conflicts pile up, and when a test fails you can't tell which change broke it. Make one small branch per change, open the PR early (as a draft if it is not ready), and merge within a day or two.",
    "real_world": "At PayLoop, a made-up payments company, every change to the checkout service goes through a pull request. The merge button turns on only after one approving review and green CI. Merges to `main` deploy to staging on their own, and the same image reaches production when an engineer clicks approve. That human click is what makes it continuous delivery.",
    "task": {
        "title": "Your first pull request with gh",
        "steps": [
            "In `~/code/hello-devops`, switch to `main` and pull, so you start from the latest code.",
            "Create a branch called `add-pr-template`.",
            "Create `.github/pull_request_template.md` with the content from the Files section. Commit it with a message that says what it adds.",
            "Push the branch and open a pull request with `gh pr create --fill`.",
            "Open the PR in the browser. Read the Files changed tab the way a reviewer would, and leave a comment on one line.",
            "Merge the PR with squash and delete the branch, using `gh pr merge`.",
            "Update your local `main`, then create the annotated tag `v0.1.0` and push it.",
            "Start a second branch, change one line, and push it. On the repository page, click Compare & pull request. The description box now starts from your template. Close that PR if you don't need it.",
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
        "answer": "Continuous integration means we all merge small changes often, and a server builds and tests each one, so we hear about a break within minutes. Continuous delivery carries every passing change through the rest of the pipeline, so it is packaged and ready to release, and a person decides when it goes to production. Continuous deployment drops that last human step, and every passing change goes live on its own. In both kinds of CD, the artifact is built once, and that same artifact moves through each stage.",
    },
    "recap": [
        "Work on short-lived branches and merge them through pull requests with review and checks.",
        "A merge keeps history as it happened; a rebase makes a straight line with new commit IDs. Rebase only your own branches.",
        "A merge conflict means two branches changed the same lines. You pick the result, and the tests tell you if it still works.",
        "Trunk-based development keeps main releasable with small daily merges. GitFlow uses long-lived branches and suits rare, big releases.",
        "CI tests every change. Continuous delivery keeps it ready to release; continuous deployment releases it with no human step.",
        "Build once, deploy many: promote one tested image, and name releases with semantic versions and annotated tags.",
    ],
    "check": [
        {
            "q": "Your team merges to main many times a day, and every passing change is ready to ship. A product manager clicks Release every Friday. What is this?",
            "options": ["Continuous deployment", "Continuous delivery", "GitFlow", "Blue/green deployment"],
            "answer": 1,
            "why": "Every change is ready to ship and a person picks the moment. That is continuous delivery.",
        },
        {
            "q": "You fix a bug in version 2.4.1, and nobody has to change how they call your API. What is the next version?",
            "options": ["3.0.0", "2.5.0", "2.4.2", "2.4.1-fix"],
            "answer": 2,
            "why": "A compatible bug fix raises only the PATCH number.",
        },
        {
            "q": "You rebased your branch `add-metrics`, which only you use, onto the newest main. A plain `git push` is rejected. What do you do?",
            "options": [
                "Push with git push --force-with-lease",
                "Delete the repository and push again",
                "Merge main into the branch a second time",
                "Run git merge --abort",
            ],
            "answer": 0,
            "why": "A rebase gives your commits new IDs, so GitHub sees different history. `--force-with-lease` replaces it, and refuses if someone else pushed in the meantime.",
        },
    ],
    "interview": [
        {
            "q": "What is the difference between continuous delivery and continuous deployment?",
            "a": "Both build, test and package every change automatically, so main is always releasable. In continuous delivery, a person decides when a release goes to production, often with one click or an approval. In continuous deployment, every change that passes the pipeline goes to production with no human step. That only works with strong automated tests, good monitoring and fast rollback, because nobody looks at each release by hand.",
        },
        {
            "q": "Why do many teams prefer trunk-based development to GitFlow?",
            "a": "Trunk-based development keeps branches small and short-lived, so merges are easy and conflicts are rare. Main stays releasable, which fits CI and frequent deploys. In GitFlow, the long-lived develop and release branches drift apart, and merges get big and risky. GitFlow still fits products that ship versioned releases a few times a year, or that must patch several old versions.",
        },
        {
            "q": "When would you rebase instead of merge?",
            "a": "I rebase my own short-lived branch onto the newest main before I open or update a pull request, so the history is a straight line and the PR shows only my changes. I never rebase a branch that someone else has pulled, because rebasing rewrites commit IDs and their copy no longer matches. After a rebase I push with --force-with-lease, which refuses to overwrite work I have not seen. For combining shared branches, I merge.",
        },
    ],
    "deeper": {
        "minutes": 12,
        "body": T("""
            Here is a puzzle. Pull request A renames the function `count_visit` to `record_visit` and updates every caller. Pull request B, opened the same morning, adds a new endpoint that calls `count_visit`. Both are green, because each was tested against that morning's `main`. A merges first. B merges second with no conflict, because the two PRs never touched the same lines. Now `main` is broken.

            This is a semantic conflict: the text merges cleanly and the meaning does not. Git cannot see it, because git works on lines, not on what the code means. Only a test run on the real combination can catch it.

            GitHub gives you two tools against it:

            - Require branches to be up to date before merging. This is a ruleset setting (Day 19). B's checks must pass again on top of the newest `main` before it can merge. It is simple and safe, but on a busy repository people keep updating their branches and re-running CI.
            - A merge queue. You press merge, and GitHub puts your PR in a queue. It builds a temporary branch with `main` plus the PRs ahead of yours, runs the required checks there, and merges only when they pass. Workflows must also listen to the `merge_group` event, or their required checks never report for the queue. Merge queues are available for repositories owned by an organization, so you will meet them at work rather than in your own account.

            For a team of five, the up-to-date rule is usually enough. A merge queue pays off when many PRs land every hour. See {queue}.

            While you are in the merge settings, pick one merge method for the repository:

            - Create a merge commit: keeps every commit from the branch and adds a merge commit.
            - Squash and merge: turns all the branch's commits into one new commit on `main`.
            - Rebase and merge: replays each commit on top of `main`, with no merge commit.

            Many trunk-based teams allow only squash. One PR becomes one commit on `main`, so `git log` stays readable and `git revert` undoes a whole PR in one step. The small commits are still visible on the PR page. See {methods}.
        """).format(queue=link("merge_queue", "Managing a merge queue"), methods=link("merge_methods", "About merge methods on GitHub")),
    },
    "sources": sources("gh_flow", "about_prs", "ci", "semver"),
}
