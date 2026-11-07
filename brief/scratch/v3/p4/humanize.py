#!/usr/bin/env python3
"""Human-writing pass (v3, blog mode) for content/p4.json.

Loads the current JSON, rewrites prose fields only, and writes it back.
Two kinds of edit:
  rep(path, old, new): replace one exact passage inside a prose field (must occur once)
  put(path, new):      replace a whole prose field
Paths start with a lesson id ("d17") or "part", then keys and list indexes.
"""
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[4]
FILE = ROOT / "content" / "p4.json"

data = json.loads(FILE.read_text())
lessons = {L["id"]: L for L in data["lessons"]}

# Only these leaf fields may be touched.
PROSE_LEAVES = {"intro", "why", "back", "goal", "plain", "body", "analogy", "mistake", "real_world",
                "say", "done_when", "prompt", "answer", "a"}
PROSE_LISTS = {"recap", "steps", "hints"}


def locate(path):
    head, *rest = path
    node = data if head == "part" else lessons[head]
    for k in rest[:-1]:
        node = node[k]
    last = rest[-1]
    parent_key = rest[-2] if len(rest) >= 2 else None
    ok = (isinstance(last, str) and last in PROSE_LEAVES) or (isinstance(last, int) and parent_key in PROSE_LISTS)
    if not ok:
        sys.exit(f"refusing to edit non-prose path {path}")
    if isinstance(last, int) and parent_key == "steps" and isinstance(node[last], dict):
        sys.exit(f"refusing to edit worked step object {path}")
    return node, last


def put(path, new):
    node, k = locate(path)
    if not isinstance(node[k], str):
        sys.exit(f"{path} is not a string")
    node[k] = new


def rep(path, old, new):
    node, k = locate(path)
    n = node[k].count(old)
    if n != 1:
        sys.exit(f"{path}: expected 1 match, found {n}: {old[:60]!r}")
    node[k] = node[k].replace(old, new)


# ---------------------------------------------------------------- part level
put(("part", "intro"),
    "Until now you ran every check and build for hello-devops yourself. In this part GitHub runs them for you. "
    "Every pull request gets linted, tested and built, a red one cannot merge, and a version tag publishes a "
    "multi-platform image. Part 3 left you with a tested app and a production-ready image, and a pipeline needs "
    "nothing more to start.")
put(("part", "resources", 0, "why"),
    "Every topic in this part has a page here, from your first workflow to the security reference.")
put(("part", "resources", 4, "why"),
    "Its branching chapters explain merge and rebase with clear pictures.")

# ---------------------------------------------------------------- d17
rep(("d17", "sections", 1, "body"),
    "So the rule is simple: rebase only branches that nobody else uses.",
    "So rebase only branches that nobody else uses.")
rep(("d17", "sections", 1, "body"),
    "One thing git never checks is whether the merged code still works. The worked example shows why that is the tests' job.",
    "Git never checks whether the merged code still works. In the worked example below, git accepts the fixed merge and a test still fails.")
put(("d17", "analogy"),
    "A pull request works like a suggested edit in a shared document. You write on your own copy, a colleague reads "
    "the suggestion and comments, and the owner accepts it into the main text. CI is a spell checker that runs on "
    "every suggestion before anyone reads it. A shared document only ever has one text, though. Git keeps many "
    "parallel copies and combines them line by line, which is how two people end up in a merge conflict.")
put(("d17", "mistake"),
    "Don't let a branch live for days and end as one huge pull request. Reviewers can only skim it, and conflicts "
    "pile up while it waits. When a test fails, you can't tell which change broke it. Make one small branch per "
    "change, open the PR early (as a draft if it is not ready), and merge within a day or two.")
put(("d17", "real_world"),
    "Every change to the checkout service at PayLoop, a made-up payments company, goes through a pull request. The "
    "merge button turns on only after one approving review and green CI. Merges to `main` deploy to staging on their "
    "own. The same image reaches production when an engineer clicks approve, and that human click is why this counts "
    "as continuous delivery.")
rep(("d17", "deeper", "body"),
    "Here is a puzzle. Pull request A renames",
    "Pull request A renames")
put(("d17", "explain_back", "prompt"),
    "A new teammate keeps mixing up continuous integration, continuous delivery and continuous deployment. Set them "
    "straight in 3 to 4 sentences, and say where a human decides.")

# ---------------------------------------------------------------- d18
rep(("d18", "sections", 0, "body"),
    "so one failing test turns the whole run red.\n\nThat is the whole trick behind CI. Tools exit non-zero when "
    "something is wrong, and a machine reads the exit code for you on every change.",
    "so one failing test turns the whole run red. Most of CI rests on that convention: tools exit non-zero when "
    "something is wrong, and GitHub reads the exit code for you on every change.")
rep(("d18", "sections", 1, "body"),
    "YAML trips most people up at first. These are the traps that bite in workflows:",
    "YAML gives almost everyone trouble in their first workflows. Watch for these traps:")
put(("d18", "analogy"),
    "A workflow is like an order ticket in a restaurant kitchen. An order comes in (the event), a cook gets a clean, "
    "empty station (the runner) and follows the ticket line by line (the steps). Two cooks can work on two tickets at "
    "once (two jobs). When the dish is done, the station is wiped for the next order. A real kitchen would put the "
    "leftovers in the fridge. A runner throws everything away unless you save it as a cache or an artifact (Day 19).")
put(("d18", "real_world"),
    "Engineers on the payments team from Day 17 rarely open the Actions tab while everything is green. A red cross on "
    "a pull request sends them straight to the failed step's log. Every new service there starts from the same CI "
    "template, so tests run on every push from its first day. The team keeps the pipeline under ten minutes, so "
    "nobody is tempted to skip it.")
put(("d18", "explain_back", "prompt"),
    "Explain how a push turns into a green tick in GitHub Actions, in 3 to 4 sentences. Use the words event, "
    "workflow, job, runner and step.")

# ---------------------------------------------------------------- d19
rep(("d19", "sections", 0, "body"),
    "If one fails, `build` is skipped, and you get the bad news without paying for the slow part.",
    "If one fails, `build` is skipped, so you hear about the failure without waiting for the slow part.")
rep(("d19", "sections", 1, "body"),
    "has two rules worth knowing. An artifact",
    "has two rules. An artifact")
rep(("d19", "sections", 2, "body"),
    "A job that missed saves a new entry when it finishes. Scope matters here. A run can restore",
    "A job that missed saves a new entry when it finishes. A run can restore")
rep(("d19", "sections", 5, "body"),
    "Most people get caught by at least one of these details:",
    "Four details catch people out:")
rep(("d19", "analogy"),
    "One difference: CI inspects a car that does not exist yet, the merged result of your branch and main.",
    "Unlike the factory, CI inspects a car that does not exist yet: the merged result of your branch and main.")
put(("d19", "real_world"),
    "A ruleset that nobody can bypass, not even admins, guards main on the checkout service from Day 17. It requires "
    "one review and green checks for lint, tests and the image build. The team treats ten minutes as the limit for "
    "CI. When a run creeps above that, someone adds caching or splits slow tests.")
put(("d19", "explain_back", "prompt"),
    "In 3 to 4 sentences, explain how your CI pipeline keeps broken code out of main. Cover needs, the matrix and "
    "the ruleset.")

# ---------------------------------------------------------------- d20
rep(("d20", "sections", 0, "body"),
    "Everything in this lesson gets easier once you see that a workflow is read at two different moments.",
    "A workflow is read at two different moments, by two different programs.")
rep(("d20", "sections", 0, "body"),
    "Two consequences follow, and both trip people up:",
    "Two things follow from this:")
rep(("d20", "sections", 2, "body"),
    "Here is the part that catches almost everyone. Every `if:` that does not contain a status function gets an "
    "invisible `success()` added to it.",
    "Every `if:` that does not contain a status function gets an invisible `success()` added to it, and almost "
    "everyone is caught by it.")
rep(("d20", "sections", 4, "body"),
    "Two details matter. The `inputs` context",
    "The `inputs` context")
rep(("d20", "sections", 5, "body"),
    "The limits worth knowing:",
    "A few limits apply:")
put(("d20", "analogy"),
    "Go back to the kitchen from Day 18 and add a head chef, who prepares every ticket before service. Expressions "
    "are the blanks the chef fills in ahead of time (\"table 12, no salt\"), so the cook only ever sees the finished "
    "ticket. Step outputs are notes the cook leaves for the next cook at the same station, and job outputs are notes "
    "passed through the kitchen hatch to another station. A composite action is a sub-recipe card, such as \"make "
    "the sauce\", used inside any dish. A real chef can still walk over and change a ticket while the cook works. "
    "GitHub never changes an expression once the job has started.")
put(("d20", "mistake"),
    "You put `if: github.ref == 'refs/heads/main'` on a cleanup or notify step and expect it to run after a "
    "failure, because the condition looks true. The hidden `success()` skips it every time something earlier fails, "
    "which is exactly when you wanted it. Write the status function yourself: `failure()` for 'only after a "
    "failure', `!cancelled()` for 'whatever happened'.")
put(("d20", "real_world"),
    "Copying the same build steps into every service means fixing every bug in every copy. The platform team at the "
    "payments company from Day 17 keeps a few composite actions instead, such as one that sets up the JVM and the "
    "Gradle cache. It also keeps two reusable workflows: one builds and scans an image, and one deploys through an "
    "environment with approvals. Each service's own workflow is about thirty lines of calls. Services pin the "
    "reusable workflows to a commit, so a fix to the scan step reaches a service when it moves its pin. That is "
    "slower, but a bad change cannot spread everywhere at once.")
rep(("d20", "deeper", "body"),
    "Section one said pasted text becomes code. Here is what that looks like, so you recognise it in other people's "
    "workflows.\n\nTake a step meant",
    "Take a step meant")
put(("d20", "explain_back", "prompt"),
    "A value is made in one job and needed in another. In 3 to 4 sentences, explain how it gets there through "
    "GITHUB_OUTPUT, the job's outputs block and needs, and say why GITHUB_ENV is not enough.")

# ---------------------------------------------------------------- d21
rep(("d21", "sections", 1, "body"),
    "One property surprises people. A commit or tag pushed",
    "A commit or tag pushed")
rep(("d21", "sections", 3, "body"),
    "You work alone, so leave Prevent self-review switched off. With it on, you could never approve your own release.",
    "Leave Prevent self-review switched off. You are the only reviewer, so with it on you could never approve your "
    "own release.")
rep(("d21", "sections", 6, "body"),
    "The trigger you choose decides a lot.",
    "For pull requests from forks, the trigger you pick decides whether that can happen.")
rep(("d21", "sections", 6, "body"),
    "The classic mistake is to check out the PR's head commit and then run its build script or tests.",
    "It goes wrong when the job checks out the PR's head commit and runs its build script or tests.")
put(("d21", "analogy"),
    "The GITHUB_TOKEN is like a hotel key card. The front desk makes a new card for each stay, it opens only the "
    "doors you booked, and it stops working at checkout. A long-lived cloud key is more like a copied master key: it "
    "opens many doors for years, so losing it is a disaster. OIDC is showing your passport at the desk to get a "
    "fresh card each time. A key card belongs to one guest, though. The token has no owner like that: every action "
    "in the job can pick it up and use it.")
rep(("d21", "worked", "steps", 0, "say"),
    "Here is a deploy workflow like ones you may find in older repositories.",
    "You may find deploy workflows like this one in older repositories.")
rep(("d21", "worked", "steps", 1, "say"),
    "It says nothing about the other four, because they are valid YAML. Tools catch some problems; you catch the rest.",
    "It says nothing about the other four, because they are valid YAML, so finding those is up to you.")
put(("d21", "real_world"),
    "Only one workflow on the payments team from Day 17 may push images: the release workflow, and it runs only for "
    "version tags. Production deploys wait in a protected environment until an engineer from the on-call rotation "
    "approves. No CI system there holds long-lived cloud keys. Each job gets short-lived AWS credentials through "
    "OIDC, with one role per environment. Dependabot's weekly action updates go through the same CI and review as "
    "any other change.")
put(("d21", "interview", 1, "a"),
    "Every third-party action is pinned to a full commit SHA, so a moved tag cannot change the code I run. Dependabot "
    "proposes updates only a few days after each release, and I review those PRs. The GITHUB_TOKEN stays read-only "
    "by default, with write access only in the job that needs it. Deploy credentials live in environments behind "
    "approvals, and I prefer OIDC over stored keys. Where a short shell step will do, I use that instead of another "
    "action.")
put(("d21", "explain_back", "prompt"),
    "Someone asks how your release workflow keeps credentials safe. Answer in 3 to 4 sentences that cover "
    "GITHUB_TOKEN permissions, the environment and SHA pinning.")

FILE.write_text(json.dumps(data, ensure_ascii=False, indent=1))
print(f"wrote {FILE}")
