"""Book-voice rewrite of d23 (fifth pass, writer td). Replaces prose fields only."""
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[4]
PATH = ROOT / "content/p6.json"
P = json.loads(PATH.read_text())
ORIG = json.loads((ROOT / "brief/scratch/v5/orig/p6.json").read_text())
IDX = next(i for i, x in enumerate(P["lessons"]) if x["id"] == "d23")
P["lessons"][IDX] = next(x for x in ORIG["lessons"] if x["id"] == "d23")  # start from the original each run
L = P["lessons"][IDX]

L["goal"] = ("By the end you can take a change from branch to merged pull request with gh, give a review that helps, "
             "send each change to the right reviewers with CODEOWNERS, tag a version, and tell continuous integration, "
             "delivery and deployment apart.")

L["opening"] = """Picture a restaurant kitchen on a Friday morning. Two cooks improve the house recipe book before lunch. The first moves the spare stock into a new green pot and fixes every card that mentioned the old blue pot. The second works from the cards as they were at breakfast. Their new soup card says to take one ladle from the blue pot. At noon, the new soup reaches for an empty pot.

Nobody was careless. Each cook checked their own work, and the two changes never touched the same card. That is why the trap is easy to fall into: the trouble lives in the combination, and nobody tasted the combination.

Production-ready images left us with an image good enough to ship, and a question: how does a change reach it safely when other people change the same code? In this lesson, we'll follow one change through a pull request, a review and a merge. Then we'll name the ideas (CI, CD, rollouts, versions) that the rest of this part automates. Before we start, make a guess, and keep it in mind."""

L["guess"]["q"] = "You join a new team, and they say they practice continuous deployment. What do they mean?"
L["guess"]["why"] = ("With continuous deployment, every change that passes the automatic checks goes live, and nobody clicks anything. "
                     "Merging daily is continuous integration, and a person clicking to release is continuous delivery.")

plains = [
    "A page on GitHub that asks to add one branch's changes to another, so people and tests can check them first.",
    "A pull request marked as not ready: nobody can merge it, and code owners are not asked to review it yet.",
    "A person or team that a CODEOWNERS file names for some files; GitHub asks for their review automatically.",
    "Merging a pull request as one new commit on main that holds all the changes from the branch.",
    "Merging small changes often, with an automatic build and test for every change.",
    "Every change that passes the automatic checks is ready to release, and a person decides when.",
    "Every change that passes the automatic checks goes to the live system with no person in between.",
    "Version numbers in the form MAJOR.MINOR.PATCH that show how big a change is.",
]
for t, p in zip(L["terms"], plains):
    t["plain"] = p

S = L["sections"]

S[0]["h"] = "One change, from your laptop to main"
S[0]["body"] = """Git, the tool from Part 2 that records every change to files, keeps tonight's recipe book on a branch called `main`. A branch is a separate line of saved changes, where you can work without touching what others use. Each saved change is a commit.

Day 9 left you with a clean branch on your laptop. You could merge it into `main` yourself (add its commits there) and push it, sending your commits to GitHub, the website that holds the team's shared copy (the repository). But then nobody else reads the change before it lands, and no test runs on it unless you ran one.

A pull request (PR) fixes both. It is a page on GitHub that asks to merge your branch into `main`. Teammates read the diff there, the list of lines you added and removed. Checks run on it too: automatic tests that show a green tick or a red cross. Those checks are CI, explained below; Day 24 sets them up. In kitchen terms, the PR is your page on the head chef's desk, and the checks are a taster.

Most teams run this loop, typed in the terminal (the window for text commands) with `gh`, GitHub's command-line tool from Day 2:

1. Start from a fresh main: `git switch main && git pull`, then `git switch -c add-pr-template`.
2. Commit in small steps and push the branch with `git push -u origin add-pr-template`.
3. Open the PR: click Compare & pull request in the yellow banner on the repository page, or run `gh pr create --fill`.
4. Not ready yet? Make it a draft with `gh pr create --draft --fill`. Nobody can merge a draft, and `gh pr ready` ends the draft stage.
5. Wait for the checks. From Day 24 on, CI runs on every push, and `gh pr checks --watch` follows it from the terminal.
6. Answer the review by pushing more commits to the same branch. The PR updates itself.
7. Merge, for example with Squash and merge and Delete branch, or `gh pr merge --squash --delete-branch`. Then `git switch main && git pull`.

Squash and merge, in step 7, turns all of the branch's commits into one new commit on `main`; Go deeper compares the three merge methods.

Two facts about CI on pull requests explain our kitchen. First, GitHub builds a temporary merge commit of your branch into the current main, and CI tests that combination. Second, CI starts only when something happens to the PR itself: it is opened, gets new commits, or is reopened.

So a new commit on main is not an event on your PR, and nothing reruns. A PR that was green yesterday may be red against today's main, like a soup card written before the pots moved. The Update branch button brings main into your branch and runs CI again. While a PR has a merge conflict (changes to the same lines that Git cannot combine alone), GitHub cannot build that temporary merge, so CI does not run at all.

Next, we'll see what a human reviewer adds that a green tick cannot."""

L["aside"] = {
    "title": "What exactly does the Files changed tab show?",
    "body": "On the PR page, base is the branch you merge into, and compare is yours. The Files changed tab shows a three-dot diff, the same as `git diff main...your-branch` on your laptop. It lists only what your branch changed since it left main. Git counts from the merge base you met on Day 9: the newest commit that both main and your branch contain. Anything other people added to main after that point stays out of the view. That keeps the review about your work, and it is why two PRs can each look harmless alone.",
    "after": 0,
}

S[1]["h"] = "What a reviewer catches that tests miss"
S[1]["body"] = """The kitchen taster checks the salt, because that is its job. The head chef notices the card that never says how much stock to use. In code, CI runs the tests the author wrote. A reviewer catches what nobody thought to test, such as a missing error case or a confusing name.

As the author:

- Keep the PR small. Fifty lines tend to get careful comments; two thousand tend to get a quick "looks good".
- Say why in the description, and how you tested it. The PR template in today's Files section asks both questions.
- Read your own diff on GitHub before you ask anyone. You will catch the stray debug line yourself.
- Answer every comment, even with "done", and re-request the review once you have pushed the changes.

The easy trap is a branch that lives for a week and ends as one huge PR. Reviewers can only skim it, and conflicts pile up while it waits. When a test fails, you can't tell which change broke it. Make one small branch per change, open the PR early (as a draft if it is not ready), and merge within a day or two.

**A small pull request gets a real review. Keep yours small.**

As the reviewer, read the description first, then the tests, then the code. In Files changed, click the blue comment icon next to a line, or drag across several lines. The suggestion button in a comment lets you write the exact replacement, and the author applies it with Commit suggestion. Tick Viewed on each file you finish. When you are done, click Review changes and choose Comment, Approve or Request changes.

Request changes only blocks the merge when a ruleset requires pull requests. A ruleset is a set of rules for a branch, such as "main only changes through a reviewed PR", and Day 25 builds one. With that rule on, Request changes blocks until that same reviewer approves.

Our lab app, hello-devops, is a tiny web app that greets every visitor and counts the visits. Redis is a small database where it can keep that count. A good comment asks instead of ordering: "what happens here if Redis is down?"

Mark polish with a "Nit:" prefix, so the author knows it can wait. [Google's code review guide](https://google.github.io/eng-practices/review/) gives a simple rule: approve a change once it clearly improves the code, even if it isn't perfect. Be kind to the person and strict about the code. GitHub never lets you approve your own pull request, so on a team someone else always approves. Next, we'll let GitHub pick that someone for each file."""

S[2]["h"] = "Sending each change to the people who know that code"
S[2]["body"] = """In a big kitchen, every new dessert goes past the pastry chef, and nobody has to remember to ask. In software, a new teammate who edits `infra/`, the folder that describes the servers, may not know a platform team exists, so the change merges without them.

A `CODEOWNERS` file writes the rule down. It maps paths (files and folders in the repository) to the people or teams responsible for them. When a PR changes a file that has an owner, GitHub requests that owner's review automatically, except while the PR is a draft. The rules:

- Put the file in `.github/CODEOWNERS`. GitHub also looks in the root and in `docs/`, and uses the first one it finds.
- Each line is a pattern, much like in `.gitignore` (the Part 2 file that lists what Git ignores), then owners such as `@username` or `@org/team-name`.
- The last matching line wins, so put the broad `*` line first and the specific paths below it.
- Owners need write access (permission to change the repository), or their line does nothing.
- GitHub reads the file from the PR's base branch, so a change to it counts only after it is merged. A PR cannot pick its own reviewers.

On its own the file only requests reviews. To make an owner's approval required, turn on Require review from Code Owners in a ruleset; Day 25 builds the ruleset for main. An approval from any one of a line's owners is enough. Give the file itself an owner too, with a line for `/.github/CODEOWNERS`. Otherwise a PR could change who owns what without the owners seeing it.

Code owners work in public repositories on the Free plan; private ones need a paid plan. In your solo hello-devops every line names you, and you can't approve your own PR, so the file has no effect yet. Add it anyway: GitHub highlights any line with bad syntax when you open the file.

Owners decide who reads a change. Next: how long may a change wait on its branch?"""

S[3]["h"] = "How long should a branch live?"
S[3]["body"] = """Imagine two ways to keep the recipe book. In one, every cook adds small, tested edits to the same book all day. In the other, next season's menu grows in a separate book for months, then gets copied back in one long afternoon. You can guess which afternoon goes badly.

A team's answer, including where releases come from, is its branching strategy. Two styles are common.

In trunk-based development, everyone merges small branches into one main branch, the trunk, at least once a day. A branch lives for hours or a day or two, and `main` is always in a state you could release. Unfinished work is merged too, but switched off behind a feature flag: a setting that turns code on or off without a new deploy. To deploy is to put a new version where users can reach it.

GitFlow uses several long-lived branches:

- `main` holds released code only.
- `develop` collects finished features.
- `feature/...` branches start from `develop`.
- `release/...` and `hotfix/...` branches prepare and patch releases.

GitFlow fits software that ships a big version a few times a year, or that must patch several old versions at once. If you deploy every week or more often, it gets in your way. Long-lived branches drift apart, and merging them back is slow and risky.

For a web service like hello-devops I would pick trunk-based every time. This course uses [GitHub flow](https://docs.github.com/en/get-started/using-github/github-flow), GitHub's own simple version of it: branch, pull request, review, merge.

Small, frequent merges stay safe only if something tests every one. That something is CI."""

S[4]["h"] = "Integration, delivery, deployment: three words that sound alike"
S[4]["body"] = """In the kitchen, CI is the taster who tries each dish the moment it is ready. Continuous delivery keeps every tasted dish plated until the head chef sends it out. Continuous deployment sends it straight to the table.

Continuous integration (CI), which Day 1 sketched, means everyone merges small changes often, and a server builds and tests every change automatically. A server is a computer that runs programs for others. Without CI, people test on their own laptops, and the combined code first meets a test when someone tries to release. With CI you hear about a broken test minutes after you push, while you still remember what you changed.

On GitHub, that server is a fresh virtual machine (a computer simulated in software) that GitHub starts for the test and deletes afterwards (Day 24). [Martin Fowler's article on continuous integration](https://martinfowler.com/articles/continuousIntegration.html) is the classic description and worth an evening.

CD has two meanings, often mixed up:

- Continuous delivery: every change that passes is ready to release. A person decides when it goes to production, often with one click.
- Continuous deployment: every change that passes goes to production on its own. Nobody clicks anything.

The steps a change goes through form a pipeline. A typical one runs in this order:

1. Build: install dependencies and package the code.
2. Test: run linters and automated tests.
3. Publish: build a container image and push it to a registry.
4. Deploy: release that image to staging (a copy of production for a last check), then to production.

Dependencies are other people's code your app needs; linters are programs that check code for style and common mistakes. An image, from Part 5, is your app packed with everything it needs to run; a registry is an online store for images. Production is the real system your users use.

Build the image once, at the publish step. This rule is called **build once, deploy many**: the very same image, with the same digest from Day 18, moves from staging to production. A digest is a fingerprint of the image's exact contents. If you rebuilt it for production, the build could pull newer packages, and what you ship would no longer be what you tested.

Automating these steps also moves the DORA metrics from Day 1, which measure how teams deliver: how often you deploy, how long a change takes to reach users, and more. Next: how the new version replaces the old one while users keep clicking."""

S[5]["h"] = "Swapping versions while people keep using the app"
S[5]["body"] = """Picture changing the menu mid-dinner by closing the doors, swapping every recipe and opening again. The naive software deploy works the same way: it stops the old version, then starts the new one. Users get errors during the gap, and if the new version is broken, every user hits it at once. Four common ways avoid one or both problems:

- Rolling: replace servers or containers a few at a time. Kubernetes does this by default (Day 40).
- Blue/green: run the new version (green) next to the old one (blue), then switch all traffic at once.
- Canary: send a small share of traffic, say 5%, to the new version, then grow it step by step.
- Feature flags: ship new code switched off, then turn it on for some users with a setting.

A container is one running copy of an image. Kubernetes, which Part 10 teaches, runs containers across many servers and replaces them for you. Traffic means the requests users send. So a canary is the new soup offered to a few tables first.

Each one has a cost. Rolling needs no extra servers, but for a few minutes old and new versions serve users side by side, so both must work with the same database. Blue/green gives you an instant rollback (a quick return to the old version) and costs double the capacity during the switch. A canary limits the damage of a bad release, as long as you have good metrics to judge it (Part 12 builds them). Metrics are numbers measured over time, such as errors per minute. Feature flags need no deploy at all. You pay for them later, with `if` branches in the code that someone has to clean up.

On Kubernetes, [Argo Rollouts](https://github.com/argoproj/argo-rollouts), an add-on tool, automates blue/green and canary releases. For hello-devops, the rolling update Kubernetes gives you for free is plenty.

Next, we'll give each new version a name everyone agrees on."""

S[6]["h"] = "Version numbers that say how much changed"
S[6]["body"] = """A reprinted menu marked "second printing" tells regulars that little changed. A version number does that job for software. [Semantic versioning](https://github.com/semver/semver/blob/master/semver.md) uses three numbers, MAJOR.MINOR.PATCH:

- MAJOR goes up when you break compatibility, as in 2.0.0.
- MINOR goes up when you add a feature that stays compatible, as in 1.3.0.
- PATCH goes up for a compatible bug fix, as in 1.2.1.

Compatible means code that worked with the old version still works with the new one. A pre-release adds a label after a dash, as in `1.3.0-rc.1`, and counts as older than `1.3.0`.

A tag, from Day 9, is a fixed name for one commit. An annotated tag such as `git tag -a v1.2.0 -m "..."` also stores a message. The command `git push origin v1.2.0` sends it, because a plain push does not.

In this course a tag is what starts a release. On Day 27, pushing the tag `v1.0.0` starts a workflow (a list of automated steps that GitHub runs) that builds and publishes the image `1.0.0`. The git tag, the image tag and the app's `version` field then all match. Tag `main` after the PR is merged, never a feature branch, so the release points at a commit CI already tested on main.

One gap remains. Every green tick we talked about assumes something runs the checks, and in your repository nothing does yet. A pull request alone is a chef's desk with no taster."""

L["closing"] = """We started with two cooks whose changes were each fine and who broke lunch together. You now have the pieces that stop that: small branches, pull requests, reviewers chosen by CODEOWNERS, and the habit of testing what two changes do together. The worked example replayed that failure in real code.

Open your hello-devops repository on GitHub. Check that your first PR shows as merged, that `v0.1.0` appears under Tags, and that CODEOWNERS shows no errors.

Next, we'll write our first workflow in GitHub Actions, GitHub's built-in way to run commands for you. It answers the question this lesson left open: who actually tastes the dish?"""

L["analogy"] = ("A pull request also works like a suggested edit in a shared document. You write on your own copy, a colleague comments in the margin, "
                "and the owner accepts it into the main text. CI is a spell checker that runs on every suggestion before anyone reads it, "
                "and CODEOWNERS decides whose desk the suggestion lands on. A shared document checks each suggestion against the text as it is now. "
                "GitHub checks a PR only when the PR changes, so two suggestions that were each fine can still clash once both are accepted.")
L["mistake"] = ("Putting the catch-all `*` line at the bottom of CODEOWNERS looks tidy, and it quietly breaks every line above it. "
                "The last matching line wins, so `*` now matches every file, and the platform team never hears about `infra/`. "
                "Put `*` first, then the specific paths below it.")
L["real_world"] = ("Picture the checkout service of PayLoop, a made-up payments company. Every change goes through a pull request. "
                   "CODEOWNERS sends anything under `payments/` to the payments team, and the merge button turns on only after one of them approves and CI is green. "
                   "Merges to `main` deploy to staging on their own. The same image reaches production when an engineer clicks approve, "
                   "and that human click is why this counts as continuous delivery.")

says = [
    "Now the two cooks from the opening, in real code. Make a scratch clone of hello-devops (a full copy in a new folder), so your real repository stays clean. Turn on the virtual environment from Day 2, the project's private set of Python packages. Then play teammate A, the cook who moves the stock. On a branch, rename `count_visit` to `record_visit` in `app.py` (the function and its one caller), then commit and run the tests.",
    "Now play teammate B, who starts from the same main with `git switch main && git switch -c hello-name`. B adds an endpoint, a new web address the app answers, and a test for it. B uses the old name, which was correct that morning. This is the new soup card that still says blue pot.",
    "Commit and test B's branch: green as well. Each PR's Files changed tab would show the three-dot diff, only what that branch changed since it left main. Neither diff touches the other's lines, so a reviewer of either PR would see nothing wrong.",
    "Merge both the way the Merge pull request button does, with `--no-ff`, which always records a merge commit. Git reports no conflict, because the branches changed different lines.",
    "Run the tests on main. The new endpoint calls a function that no longer exists, so the app answers with an error (status 500) instead of a greeting. This is a semantic conflict: the text merged cleanly, and the meaning did not. `git grep` searches the files and finds the stale call.",
    "On a shared main you undo with a new commit, as on Day 8, so nobody else's copy of the history changes under them. A merge commit has two parents, so `-m 1` tells revert to keep the first one, main's side. The Revert button on a merged PR does the same thing, as a new PR.",
    "What would have caught it is the ruleset option Require branches to be up to date before merging (Day 25). PR #13 would have had to take in the new main first. CI would then have run on the result, and the test would have failed on the PR instead of on main. Clean up with `deactivate`, `cd ~` and `rm -rf ~/code/pr-demo`.",
]
for st, s in zip(L["worked"]["steps"], says):
    st["say"] = s

L["task"]["steps"] = [
    "In `~/code/hello-devops`, switch to `main` and pull, so you start from the latest code.",
    "Create a branch called `add-pr-template`. Add `.github/pull_request_template.md` and `.github/CODEOWNERS` from the Files section, with your GitHub username in CODEOWNERS. Commit each file on its own, with a message that says why.",
    "Push the branch and open a draft pull request with `gh pr create --draft --fill`.",
    "Open the PR in the browser. Review it as if a teammate wrote it: mark each file Viewed, leave one line comment, and leave one suggested change.",
    "Apply your suggestion with Commit suggestion, then run `git pull` on your laptop so your branch has that commit too.",
    "Mark the PR ready with `gh pr ready`. Then merge it as one squashed commit and delete the branch, using `gh pr merge`.",
    "Update your local `main`. Open `.github/CODEOWNERS` on GitHub and check that no line is flagged as an error.",
    "Create the annotated tag `v0.1.0` on main and push it.",
    "Start a second branch, change one line, and push it. On the repository page, click Compare & pull request: the description box now starts from your template. Close that PR with `gh pr close` if you don't need it.",
]
L["task"]["hints"] = [
    "If `gh pr create` asks where to push the branch, pick your own repository.",
    "The template and CODEOWNERS only take effect once they are on `main`, the base branch.",
    "To suggest a change, open a line comment and click the suggestion button in the comment box's toolbar.",
]

L["explain_back"]["prompt"] = ("A new teammate keeps mixing up continuous integration, continuous delivery and continuous deployment. "
                               "Set them straight in 3 to 4 sentences, and say where a person decides.")
L["explain_back"]["answer"] = ("Continuous integration means we all merge small changes often, and a server builds and tests each one, so we hear about a break within minutes. "
                               "Continuous delivery carries every passing change through the rest of the pipeline, so it is packaged and ready to release, and a person decides when it goes to production. "
                               "Continuous deployment drops that last human step, and every passing change goes live on its own. "
                               "In both kinds of CD, the package is built once, and that same package moves through each stage.")

L["recap"] = [
    "A pull request puts the change, the review and the automatic checks on one page; open it early as a draft.",
    "CI tests the PR merged with main, and reruns only when the PR changes, so update stale branches before merging.",
    "Small PRs get real reviews; CODEOWNERS sends each one to the right people, and the last matching line wins.",
    "Trunk-based development keeps main releasable with small daily merges; GitFlow suits rare, big releases.",
    "CI tests every change, continuous delivery keeps it ready, continuous deployment ships it; build once, deploy many, and tag releases with semantic versions.",
    "The limit: a pull request tests nothing by itself, so the green tick means little until a workflow runs the checks (Day 24).",
]

C = L["check"]
C[0]["q"] = ("Your team merges to main many times a day, and every passing change is ready to ship. "
             "A product manager clicks Release every Friday. What is this?")
C[0]["why"] = "Every change is ready to ship, and a person picks the moment. That is continuous delivery."
C[1]["q"] = "You fix a bug in version 2.4.1, and nobody has to change how they call your API. What is the next version?"
C[1]["why"] = "A bug fix that keeps everything compatible raises only the PATCH number."
C[2]["why"] = "In CODEOWNERS the last matching pattern wins, so `/infra/` overrides the catch-all `*` for that file."

I = L["interview"]
I[0]["a"] = ("Both build, test and package every change automatically, so main is always releasable. "
             "In continuous delivery, a person decides when a release goes to production, often with one click or an approval. "
             "In continuous deployment, every change that passes the pipeline goes to production with no human step. "
             "That only works with strong automated tests, good monitoring and fast rollback, because nobody looks at each release by hand.")
I[1]["a"] = ("Trunk-based development keeps branches small and short-lived, so merges are easy and conflicts are rare. "
             "Main stays releasable, which fits CI and frequent deploys. "
             "In GitFlow, the long-lived develop and release branches drift apart, and merges get big and risky. "
             "GitFlow still fits products that ship versioned releases a few times a year, or that must patch several old versions.")
I[2]["a"] = ("I keep pull requests small and focused, and the description says why the change exists and how I tested it. "
             "I read my own diff before I ask anyone, and I open a draft early when I want feedback on the approach. "
             "As a reviewer I start with the description and the tests, ask questions instead of giving orders, and label polish as \"Nit:\" so it does not block. "
             "CODEOWNERS sends each PR to the people who know that code, and CI handles style, so people spend their review time on design and behaviour.")

L["deeper"]["body"] = """The worked example showed the problem: two pull requests that each pass CI, merge without a conflict, and break main together. Git works on lines of text. It does not know what the code means, so only a test run on the real combination can catch it. Back in the kitchen, someone has to cook the new soup in today's kitchen, with today's pots. GitHub gives you two tools for that.

- Require branches to be up to date before merging. This is a ruleset setting (Day 25). PR B must take in the newest main and pass its checks again before it can merge. It is simple and safe, but on a busy repository people keep updating their branches and rerunning CI.
- A merge queue. You press merge, and GitHub puts your PR in a queue. It builds a temporary branch with main plus the PRs ahead of yours, runs the required checks there, and merges only when they pass. Workflows must also listen to the `merge_group` event, or their required checks never report for the queue. Merge queues are available for repositories owned by an organization, so you will meet them at work rather than in your own account.

For a team of five, the up-to-date rule is usually enough. A merge queue pays off when many PRs land every hour. See [Managing a merge queue](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/configuring-pull-request-merges/managing-a-merge-queue).

While you are in the merge settings, pick one merge method for the repository:

- Create a merge commit: keeps every commit from the branch and adds a merge commit, like the `--no-ff` merges in the worked example.
- Squash and merge: turns all the branch's commits into one new commit on `main`.
- Rebase and merge: replays each commit on top of `main`, with no merge commit.

Many trunk-based teams allow only squash. One PR becomes one commit on `main`, so `git log` stays readable and `git revert` undoes a whole PR in one step. The small commits are still visible on the PR page.

Two side effects are worth knowing. After a squash merge, `git branch -d` on your laptop says the branch is not fully merged, because main got one new commit instead of yours; `git branch -D` is safe then. And Rebase and merge creates new commits on GitHub's side, so commits you signed on Day 9 lose their Verified badge. See [About merge methods on GitHub](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/configuring-pull-request-merges/about-merge-methods-on-github)."""

PATH.write_text(json.dumps(P, indent=1, ensure_ascii=False) + "\n")
print("d23 written")
