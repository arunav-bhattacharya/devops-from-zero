"""Day 23 rework: Pull requests, code review and CI/CD ideas.

Starts from the current Day 23 in content/p6.json (copied to p6.orig.json) and replaces
the Git basics that moved to Days 8 and 9. Keeps the id, the diagram, the PR template,
the CI/CD, deployment and semver content, and the facts other lessons rely on
(the payments team and checkout service, build once deploy many, version numbers).
"""
import copy
import json
import pathlib

from common import L, mcq, ref, src, step

HERE = pathlib.Path(__file__).resolve().parent
ORIG = json.loads((HERE / "p6.orig.json").read_text())
OLD = next(x for x in ORIG["lessons"] if x["id"] == "d23")
OLD_SEC = {s["h"]: s for s in OLD["sections"]}

SECTIONS = [
    {
        "h": "From branch to merged pull request",
        "body": (
            "Day 9 left you with a clean branch on your laptop. A pull request (PR) is the GitHub page that asks to merge it into `main`, "
            "and it is where the review and the CI checks meet. The loop most teams run:\n\n"
            "1. Start from a fresh main: `git switch main && git pull`, then `git switch -c add-pr-template`.\n"
            "2. Commit in small steps and push the branch with `git push -u origin add-pr-template`.\n"
            "3. Open the PR: click Compare & pull request in the yellow banner on the repository page, or run `gh pr create --fill`.\n"
            "4. Not ready yet? Make it a draft with `gh pr create --draft --fill`. Nobody can merge a draft, and `gh pr ready` ends the draft stage.\n"
            "5. Wait for the checks. From Day 24 on, CI runs on every push, and `gh pr checks --watch` follows it from the terminal.\n"
            "6. Answer the review by pushing more commits to the same branch. The PR updates itself.\n"
            "7. Merge, for example with Squash and merge and Delete branch, or `gh pr merge --squash --delete-branch`. Then `git switch main && git pull`.\n\n"
            "On the PR page, base is the branch you merge into and compare is yours. "
            "The Files changed tab shows a three-dot diff, `git diff main...your-branch`: only what your branch changed since it left main, counted from the merge base you met on Day 9.\n\n"
            "Two facts about CI on pull requests explain today's worked example. For a `pull_request` run, CI checks out a temporary merge of your branch into the current main, not your branch alone. "
            "And the checks run again only when the PR changes (opened, new commits, reopened), not when main moves. "
            "So a PR that was green yesterday may be red against today's main. The Update branch button on the PR brings main into your branch and runs CI again. "
            "While a PR has a merge conflict, its `pull_request` workflows do not run at all."
        ),
        "refs": [
            ref("About pull requests", L["gh_about_pr"], "docs"),
            ref("Creating a pull request", L["gh_create_pr"], "docs"),
            ref("How to create a pull request in 4 minutes (GitHub, GitHub for Beginners)", L["gh_pr_video"], "watch"),
        ],
    },
    {
        "h": "Code review that helps",
        "body": (
            "A review goes well when both sides do their part. As the author:\n\n"
            "- Keep the PR small. Fifty lines tend to get careful comments; two thousand tend to get a quick \"looks good\".\n"
            "- Say why in the description, and how you tested it. The PR template in today's Files section asks both questions.\n"
            "- Read your own diff on GitHub before you ask anyone. You will catch the stray debug line yourself.\n"
            "- Answer every comment, even with \"done\", and re-request the review once you have pushed the changes.\n\n"
            "As the reviewer, read the description first, then the tests, then the code. In Files changed, click the blue comment icon next to a line, or drag across several lines. "
            "The suggestion button in a comment lets you write the exact replacement, and the author applies it with Commit suggestion. "
            "Tick Viewed on each file you finish. When you are done, click Review changes and choose Comment, Approve or Request changes. "
            "Request changes only blocks the merge when a ruleset requires pull requests, and then it blocks until that same reviewer approves.\n\n"
            "Ask questions instead of giving orders: \"what happens here if Redis is down?\" Mark polish with a \"Nit:\" prefix, so the author knows it can wait. "
            "[Google's code review guide](https://google.github.io/eng-practices/review/) gives a simple rule: approve a change once it clearly improves the code, even if it isn't perfect. "
            "Be kind to the person and strict about the code. GitHub never lets you approve your own pull request, so on a team someone else always approves."
        ),
        "refs": [
            ref("Reviewing proposed changes in a pull request", L["gh_review_changes"], "docs"),
            ref("Google engineering practices: code review", L["google_review"], "read"),
            ref("GitHub Skills: Review pull requests (hands-on course)", L["skills_review"], "read"),
        ],
    },
    {
        "h": "CODEOWNERS: the right reviewers, automatically",
        "body": (
            "A `CODEOWNERS` file maps paths to the people or teams responsible for them. "
            "When a PR changes a file that has an owner, GitHub requests that owner's review automatically, except while the PR is a draft. The rules:\n\n"
            "- Put the file in `.github/CODEOWNERS`. GitHub also looks in the root and in `docs/`, and uses the first one it finds.\n"
            "- Each line is a pattern, much like in `.gitignore`, followed by owners such as `@username` or `@org/team-name`.\n"
            "- The last matching line wins, so put the broad `*` line first and the specific paths below it.\n"
            "- Owners need write access to the repository, or their line does nothing.\n"
            "- GitHub reads the file from the PR's base branch, so a change to it counts only after it is merged.\n\n"
            "On its own the file only requests reviews. To make an owner's approval required, turn on Require review from Code Owners in a ruleset; Day 25 builds the ruleset for main. "
            "An approval from any one of a line's owners is enough. Give the file itself an owner too, with a line for `/.github/CODEOWNERS`, "
            "or a PR could change who owns what without the owners seeing it.\n\n"
            "Code owners work in public repositories on the Free plan; private ones need a paid plan. "
            "In your solo hello-devops every line names you, and you can't approve your own PR, so the file has no effect yet. "
            "Add it anyway: GitHub highlights any line with bad syntax when you open the file."
        ),
        "refs": [
            ref("About code owners", L["gh_codeowners"], "docs"),
        ],
    },
]

# Keep these three sections as they are: other lessons rely on their facts.
for h in ("Trunk-based development and GitFlow",
          "CI, continuous delivery and continuous deployment",
          "Deployment strategies: how a new version reaches users"):
    SECTIONS.append(copy.deepcopy(OLD_SEC[h]))

SECTIONS.append({
    "h": "Semantic versions and release tags",
    "body": (
        "A version number tells users how much changed. [Semantic versioning](https://github.com/semver/semver/blob/master/semver.md) uses three numbers, MAJOR.MINOR.PATCH:\n\n"
        "- MAJOR goes up when you break compatibility, as in 2.0.0.\n"
        "- MINOR goes up when you add a feature that stays compatible, as in 1.3.0.\n"
        "- PATCH goes up for a compatible bug fix, as in 1.2.1.\n\n"
        "A pre-release adds a label after a dash, as in `1.3.0-rc.1`, and counts as older than `1.3.0`.\n\n"
        "Day 9 covered the mechanics: an annotated tag such as `git tag -a v1.2.0 -m \"...\"` is a fixed name for one commit, "
        "and `git push origin v1.2.0` sends it, because a plain push does not. In this course a tag is what starts a release. "
        "On Day 27, pushing the tag `v1.0.0` starts a workflow that builds and publishes the image `1.0.0`. The git tag, the image tag and the app's `version` field then all match. "
        "Tag `main` after the PR is merged, never a feature branch, so the release points at a commit CI already tested on main."
    ),
    "refs": [
        ref("Semantic Versioning 2.0.0 specification", L["semver"], "read"),
        ref("About releases", L["gh_releases"], "docs"),
    ],
})

WORKED = {
    "title": "Two green pull requests, one broken main",
    "steps": [
        step(
            "Make a scratch clone of hello-devops, so your real repo stays clean, and turn on your venv from Day 2. "
            "Play teammate A: on a branch, rename `count_visit` to `record_visit` in `app.py` (the function and its one caller), then commit and test.",
            r"""
$ git clone -q ~/code/hello-devops ~/code/pr-demo && cd ~/code/pr-demo
$ source ~/code/hello-devops/.venv/bin/activate
$ git switch -c rename-visit
Switched to a new branch 'rename-visit'
$ git commit -qam "Rename count_visit to record_visit" && pytest -q | tail -1
3 passed in 0.17s
""",
        ),
        step(
            "Now play teammate B, who starts from the same main with `git switch main && git switch -c hello-name`. "
            "B adds an endpoint and a test. B uses the old name, which was correct that morning.",
            r"""
# app.py, just above: if __name__ == "__main__":
@app.get("/hello/<name>")
def hello(name):
    REQUESTS.labels(path="/hello").inc()
    return jsonify(message=f"Hello, {name}!", visits=count_visit())


# test_app.py, at the end
def test_hello_by_name():
    client = app.test_client()
    response = client.get("/hello/Ana")
    assert response.status_code == 200
    assert response.get_json()["message"] == "Hello, Ana!"
""",
            "python",
        ),
        step(
            "Commit and test B's branch: green as well. Each PR's Files changed tab would show the three-dot diff, only what that branch changed since it left main. "
            "Neither diff touches the other's lines.",
            r"""
$ git commit -qam "Add /hello/<name>" && pytest -q | tail -1
4 passed in 0.19s
$ git diff --stat main...rename-visit
 app.py | 4 ++--
 1 file changed, 2 insertions(+), 2 deletions(-)
$ git diff --stat main...hello-name
 app.py      | 6 ++++++
 test_app.py | 7 +++++++
 2 files changed, 13 insertions(+)
""",
        ),
        step(
            "Merge both the way the Merge pull request button does, with `--no-ff`. Git reports no conflict, because the branches changed different lines.",
            r"""
$ git switch main
$ git merge -q --no-ff -m "Merge pull request #12 from rename-visit" rename-visit
$ git merge --no-ff -m "Merge pull request #13 from hello-name" hello-name
Auto-merging app.py
Merge made by the 'ort' strategy.
 app.py      | 6 ++++++
 test_app.py | 7 +++++++
 2 files changed, 13 insertions(+)
""",
        ),
        step(
            "Run the tests on main. The new endpoint calls a function that no longer exists. "
            "This is a semantic conflict: the text merged cleanly and the meaning did not. `git grep` finds the stale call.",
            r"""
$ pytest -q 2>&1 | grep -E 'NameError|FAILED|failed'
NameError: name 'count_visit' is not defined
FAILED test_app.py::test_hello_by_name - assert 500 == 200
1 failed, 3 passed in 0.19s
$ git grep -n count_visit
app.py:68:    return jsonify(message=f"Hello, {name}!", visits=count_visit())
""",
        ),
        step(
            "On a shared main you undo with a new commit, as on Day 8. A merge commit has two parents, so `-m 1` tells revert to keep the first one, main's side. "
            "The Revert button on a merged PR does the same thing, as a new PR.",
            r"""
$ git revert -m 1 --no-edit HEAD
[main 45bf9f5] Revert "Merge pull request #13 from hello-name"
 Date: Sat Nov 7 17:33:58 2026 +0000
 2 files changed, 13 deletions(-)
$ pytest -q | tail -1
3 passed in 0.21s
""",
        ),
        step(
            "What would have caught it is the ruleset option Require branches to be up to date before merging (Day 25). "
            "PR #13 would have had to take in the new main first. CI would then have run on the result, and the test would have failed on the PR instead of on main. "
            "Clean up with `deactivate`, `cd ~` and `rm -rf ~/code/pr-demo`."
        ),
    ],
}

CODEOWNERS = """# .github/CODEOWNERS: who reviews what.
# GitHub reads this file from the base branch of each pull request.
# The last pattern that matches a file wins. Replace your-github-user with your username.
# In a team you would name teams instead, such as @your-org/platform-team.

# Everything, unless a line further down matches
*                    @your-github-user

# The pipeline and the infrastructure get the people who run them
/.github/workflows/  @your-github-user
/infra/              @your-github-user
/k8s/                @your-github-user

# Protect this file itself, so nobody can quietly change the owners
/.github/CODEOWNERS  @your-github-user"""

COMMANDS = [
    {"cmd": "git push -u origin add-pr-template", "what": "Push a new branch to GitHub and link it, so later pushes need no names."},
    {"cmd": "gh pr create --fill", "what": "Open a pull request. `--fill` takes the title and body from your commits."},
    {"cmd": "gh pr create --draft --fill", "what": "Open a draft pull request: visible and testable, but not mergeable yet."},
    {"cmd": "gh pr ready", "what": "Mark the current branch's draft pull request as ready for review."},
    {"cmd": "gh pr checks --watch", "what": "Follow the CI checks of the current pull request until they finish."},
    {"cmd": "gh pr view --web", "what": "Open the pull request for the current branch in your browser."},
    {"cmd": "gh pr checkout 7", "what": "Check out the branch of pull request number 7, for example to test it locally."},
    {"cmd": "gh pr review 7 --comment -b \"What happens if Redis is down?\"", "what": "Leave a review comment on pull request 7 from the terminal."},
    {"cmd": "gh pr review 7 --approve", "what": "Approve pull request 7 (not possible on your own pull request)."},
    {"cmd": "gh pr merge --squash --delete-branch", "what": "Merge the PR as one commit, then delete the branch locally and on GitHub."},
    {"cmd": "git switch main && git pull", "what": "Go back to main and download the merged result."},
    {"cmd": "git diff main...HEAD", "what": "Show what a pull request from this branch would show: changes since it left main."},
    {"cmd": "git revert -m 1 <merge-commit>", "what": "Undo a merged pull request with a new commit, keeping main's side."},
    {"cmd": "git tag -a v0.1.0 -m \"First tagged version\"", "what": "Create an annotated tag on the current commit."},
    {"cmd": "git push origin v0.1.0", "what": "Send one tag to GitHub. A plain `git push` does not send tags."},
    {"cmd": "gh pr list --state merged", "what": "List pull requests that were merged."},
]


def build():
    L23 = copy.deepcopy(OLD)
    L23["title"] = "Pull requests, code review and CI/CD ideas"
    L23["goal"] = (
        "By the end you can take a change from branch to merged pull request with gh, give a review that helps, "
        "route reviews with CODEOWNERS, tag a version, and tell continuous integration, delivery and deployment apart."
    )
    L23["terms"] = [
        {"term": "Pull request (PR)", "plain": "A GitHub page that asks to merge one branch into another, with review and checks."},
        {"term": "Draft pull request", "plain": "A pull request marked not ready: nobody can merge it, and code owners are not asked to review yet."},
        {"term": "Code owner", "plain": "A person or team that a CODEOWNERS file names for some paths; GitHub requests their review automatically."},
        {"term": "Squash merge", "plain": "Merging a pull request as one new commit on main that holds all of the branch's changes."},
        OLD["terms"][4],  # Continuous integration (CI)
        OLD["terms"][5],  # Continuous delivery
        OLD["terms"][6],  # Continuous deployment
        OLD["terms"][7],  # Semantic versioning
    ]
    assert [t["term"] for t in L23["terms"][4:]] == [
        "Continuous integration (CI)", "Continuous delivery", "Continuous deployment", "Semantic versioning"]
    L23["sections"] = SECTIONS
    L23["analogy"] = (
        "A pull request works like a suggested edit in a shared document. You write on your own copy, a colleague reads the suggestion and comments in the margin, "
        "and the owner accepts it into the main text. CI is a spell checker that runs on every suggestion before anyone reads it, and CODEOWNERS decides whose desk the suggestion lands on. "
        "A shared document checks each suggestion against the text as it is now. GitHub checks a PR only when the PR changes, "
        "so two suggestions that were each fine can still clash once both are accepted."
    )
    L23["worked"] = WORKED
    L23["code"] = [
        OLD["code"][0],
        {
            "lang": "text",
            "title": ".github/CODEOWNERS",
            "src": CODEOWNERS,
            "run": "git add .github/CODEOWNERS && git commit -m \"Add code owners\"",
        },
    ]
    assert L23["code"][0]["title"] == ".github/pull_request_template.md"
    L23["commands"] = COMMANDS
    L23["mistake"] = OLD["mistake"]
    L23["real_world"] = (
        "Every change to the checkout service at PayLoop, a made-up payments company, goes through a pull request. "
        "CODEOWNERS sends anything under `payments/` to the payments team, and the merge button turns on only after one of them approves and CI is green. "
        "Merges to `main` deploy to staging on their own. The same image reaches production when an engineer clicks approve, and that human click is why this counts as continuous delivery."
    )
    L23["task"] = {
        "title": "Your first pull request with gh, with a template and code owners",
        "steps": [
            "In `~/code/hello-devops`, switch to `main` and pull, so you start from the latest code.",
            "Create a branch called `add-pr-template`. Add `.github/pull_request_template.md` and `.github/CODEOWNERS` from the Files section, with your GitHub username in CODEOWNERS. Commit each file on its own, with a message that says why.",
            "Push the branch and open a draft pull request with `gh pr create --draft --fill`.",
            "Open the PR in the browser. Review it as if a teammate wrote it: mark each file Viewed, leave one line comment, and leave one suggested change.",
            "Apply your suggestion with Commit suggestion, then run `git pull` on your laptop so your branch has that commit too.",
            "Mark the PR ready with `gh pr ready`, then merge it with squash and delete the branch, using `gh pr merge`.",
            "Update your local `main`. Open `.github/CODEOWNERS` on GitHub and check that no line is flagged as an error.",
            "Create the annotated tag `v0.1.0` on main and push it.",
            "Start a second branch, change one line, and push it. On the repository page, click Compare & pull request: the description box now starts from your template. Close that PR with `gh pr close` if you don't need it.",
        ],
        "hints": [
            "If `gh pr create` asks where to push the branch, pick your own repository.",
            "The template and CODEOWNERS only take effect once they are on `main`, the base branch.",
            "To suggest a change, open a line comment and click the suggestion button in the comment box's toolbar.",
        ],
        "done_when": "You are done when `gh pr list --state merged` shows your PR, `git ls-remote --tags origin` lists `v0.1.0`, and GitHub shows no errors in your CODEOWNERS file.",
    }
    L23["recap"] = [
        "A pull request puts the diff, the review and the CI checks on one page; open it early as a draft.",
        "CI tests the PR merged with main, and only reruns when the PR changes, so update stale branches before merging.",
        "Good reviews start with small PRs and a clear why; reviewers ask questions and mark polish as \"Nit:\".",
        "CODEOWNERS requests the right reviewers automatically; the last matching line wins.",
        "Trunk-based development keeps main releasable with small daily merges; GitFlow suits rare, big releases.",
        "CI tests every change, continuous delivery keeps it ready, continuous deployment ships it; build once, deploy many, and tag releases with semantic versions.",
    ]
    old_checks = OLD["check"]
    L23["check"] = [
        old_checks[0],
        old_checks[1],
        mcq(
            "A CODEOWNERS file has `* @ana` on the first line and `/infra/ @platform-team` below it. A PR changes only `infra/main.tf`. Whose review does GitHub request?",
            [
                "Only @ana, because `*` matches every file",
                "Both @ana and @platform-team",
                "Nobody, because the two lines conflict",
                "Only @platform-team, the last matching line",
            ],
            3,
            "In CODEOWNERS the last matching pattern wins, so `/infra/` overrides the catch-all `*` for that file.",
        ),
    ]
    assert L23["check"][0]["answer"] == 1 and L23["check"][1]["answer"] == 2
    L23["interview"] = [
        OLD["interview"][0],
        OLD["interview"][1],
        {
            "q": "How do you make code reviews faster and more useful?",
            "a": (
                "I keep pull requests small and focused, and the description says why the change exists and how I tested it. "
                "I read my own diff before I ask anyone, and I open a draft early when I want feedback on the approach. "
                "As a reviewer I start with the description and the tests, ask questions instead of giving orders, and label polish as \"Nit:\" so it does not block. "
                "CODEOWNERS routes each PR to the people who know that code, and CI handles style, so humans spend their time on design and behaviour."
            ),
        },
    ]
    L23["deeper"] = {
        "minutes": 12,
        "body": (
            "Today's worked example showed the problem: two pull requests that each pass CI, merge without a conflict, and break main together. "
            "Git works on lines, not on what the code means, so only a test run on the real combination can catch it. GitHub gives you two tools against it.\n\n"
            "- Require branches to be up to date before merging. This is a ruleset setting (Day 25). PR B must take in the newest main and pass its checks again before it can merge. "
            "It is simple and safe, but on a busy repository people keep updating their branches and rerunning CI.\n"
            "- A merge queue. You press merge, and GitHub puts your PR in a queue. It builds a temporary branch with main plus the PRs ahead of yours, runs the required checks there, "
            "and merges only when they pass. Workflows must also listen to the `merge_group` event, or their required checks never report for the queue. "
            "Merge queues are available for repositories owned by an organization, so you will meet them at work rather than in your own account.\n\n"
            "For a team of five, the up-to-date rule is usually enough. A merge queue pays off when many PRs land every hour. "
            "See [Managing a merge queue](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/configuring-pull-request-merges/managing-a-merge-queue).\n\n"
            "While you are in the merge settings, pick one merge method for the repository:\n\n"
            "- Create a merge commit: keeps every commit from the branch and adds a merge commit, like the `--no-ff` merges in the worked example.\n"
            "- Squash and merge: turns all the branch's commits into one new commit on `main`.\n"
            "- Rebase and merge: replays each commit on top of `main`, with no merge commit.\n\n"
            "Many trunk-based teams allow only squash. One PR becomes one commit on `main`, so `git log` stays readable and `git revert` undoes a whole PR in one step. "
            "The small commits are still visible on the PR page. Two side effects are worth knowing. "
            "After a squash merge, `git branch -d` on your laptop says the branch is not fully merged, because main got one new commit instead of yours; `git branch -D` is safe then. "
            "And Rebase and merge creates new commits on GitHub's side, so commits you signed on Day 9 lose their Verified badge. "
            "See [About merge methods on GitHub](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/configuring-pull-request-merges/about-merge-methods-on-github)."
        ),
    }
    L23["sources"] = [
        src("GitHub flow", L["gh_flow"]),
        src("About pull requests", L["gh_about_pr"]),
        src("About code owners", L["gh_codeowners"]),
        src("Semantic Versioning 2.0.0 specification", L["semver"]),
    ]
    return L23
