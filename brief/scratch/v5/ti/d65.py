"""Fifth pass (book voice) for d65, AI assistants for DevOps work. Writer: ti.
Replaces only prose fields of d65 in content/p18.json."""
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[4]
PATH = ROOT / "content/p18.json"
P = json.loads(PATH.read_text())
L = next(x for x in P["lessons"] if x["id"] == "d65")

L["goal"] = ("By the end you can use an AI assistant for DevOps chores, give it the context it needs, "
             "and check every answer with a tool you trust before it reaches your repository.")

L["opening"] = """Your jam shop takes on a summer intern. The intern has read every cookbook in the library and can write a recipe card in thirty seconds, in lovely handwriting. On the first morning you ask for the strawberry jam card. It looks perfect. It also says to boil the fruit at a setting your stove doesn't have, and it names a brand of pectin that doesn't exist.

The intern wasn't lying. They wrote what recipe cards usually look like. The trap is easy to fall into, because neat handwriting and a confident tone feel like being right.

Last time, we locked up the keys and posted a guard at the back door. Now a new kind of helper arrives, one that writes code. In this lesson, we'll let an AI assistant draft a Kubernetes file for hello-devops, watch tools catch its mistakes, and build the habit that makes this safe. Before we start, make a guess, and keep it in mind."""

L["guess"]["q"] = ("You ask an AI assistant which flag makes kubeconform, a tool that checks Kubernetes files, reject unknown fields. "
                   "It answers `--strict-mode`, with no sign of doubt. What should you conclude?")
L["guess"]["why"] = ("A model sounds just as sure when it is wrong, and here it was wrong: the real flag is `-strict`. "
                     "The tool's own help text settles the question in seconds.")

plain = {
    "Large language model (LLM)": "A program trained on a huge amount of text to predict the next words. Chat assistants and coding agents run on one.",
    "Hallucination": "An answer that sounds right but is made up, such as a flag, field, package or version that does not exist.",
    "Context": "Everything the model sees when it answers: your question, the files and errors you give it, and the chat so far.",
    "Coding agent": "An assistant that reads files, edits code and runs commands by itself in a loop, asking you before risky steps.",
    "AGENTS.md": "A plain text file in a project that tells coding agents how to build, test and follow the project's rules.",
    "Verify loop": "Draft, check with a tool you trust, fix, check again. Nothing that has failed or skipped a check reaches the main branch.",
    "Schema validation": "Checking a file against the official list of fields and types for its format, as kubeconform does for Kubernetes files.",
    "Slopsquatting": "Registering a package under a name that AI tools tend to invent, so people who install the suggestion get the attacker's code.",
}
for t in L["terms"]:
    t["plain"] = plain[t["term"]]

S = L["sections"]

S[0]["h"] = "What the model is really doing when it writes your YAML"
S[0]["body"] = """An AI assistant is a chat program that answers in plain language and writes code when you ask. Inside it sits a large language model, or LLM: a program trained on a huge amount of text to predict the next words. It writes by predicting likely text, one small piece at a time.

It learned from a huge amount of public code and documentation, up to a cutoff date. It has never seen anything released after that date, such as a flag added last month. A flag is an option you type after a command, like `-strict`.

Now ask it for a Kubernetes Deployment. Kubernetes is the system that runs your containers on a group of machines. A Deployment is the settings file that tells it how to run your app, written in YAML, a plain-text format of names and values. The model is not looking anything up. It produces the shape it has seen thousands of times before, just as the intern writes what recipe cards usually look like.

That explains its strength and its main weakness. Common shapes come out well, because the training data is full of them. Rare or recent details come out as guesses that look exactly like facts:
- a flag that was renamed last year
- a field (one named setting) that exists in a similar tool, but not in this one
- a version number that sounds about right

A chat assistant also cannot see your systems. Our app is hello-devops, the tiny web app this course builds: it answers every visit with a greeting and a count of visits so far. The assistant does not know that it listens on port 8000 (its numbered door for visitors) unless you tell it. A coding agent can read your files and run commands, which helps a lot, but the model inside it guesses in the same way.

None of this makes the tools useless. They save real time on drafts you would otherwise type by hand. It does give this whole lesson one rule. **The model drafts. A tool you trust decides.** So where does a draft save time, and where does it cost you? A map helps."""

S[1]["h"] = "Good at, bad at: a map for ops work"
S[1]["body"] = """Give the intern a week and you learn where to trust them: quick and tidy with the shopping list, shaky with oven settings. An assistant is the same. Here is my map for ops work, the daily running and changing of the systems your apps live on. One word first: a diff is the list of lines a change adds and removes.

It is good at:
- boilerplate you can check: a Dockerfile, a Compose file, a Terraform variable block
- explaining an error message, a stack trace or a confusing log line
- summarizing a long diff, a `terraform plan` or a busy incident channel
- translating between tools, such as a `docker run` command into a Compose service
- first drafts of tests, scripts and runbooks

Boilerplate is the standard text that every file of one kind needs. A stack trace is the list of steps a program was in when it crashed. A runbook is a written guide for a common job, such as restarting a service.

It is bad at:
- exact versions and flags, which change faster than its training data
- fields and options that do not exist, written in the right place with perfect indentation
- old API versions, such as `apps/v1beta1` for Deployments, which Kubernetes removed in 2019
- counting and arithmetic across long files
- saying "I don't know": it sounds just as sure when it is wrong

The second bad item is the one that bites. A made-up field looks exactly like a real one, sitting where a real one would sit.

One plain rule follows from the map. Use AI for work you could check yourself, and never for a file you could not review. A `terraform plan` is Terraform's preview of the changes it will make. If you cannot tell whether a plan is safe, a tool that writes plans faster only makes things worse. Checking, then, is the whole game, so next we turn it into a habit."""

S[2]["h"] = "The verify loop: nothing ships unchecked"
S[2]["body"] = """In the shop, the intern's recipe card never goes straight to the kitchen. Someone checks it against the stove, then cooks a small test batch. For code, the same habit is a loop. Every answer goes round it before it reaches main, the shared branch that releases come from:
1. Ask, with good context (next section).
2. Read the answer. A line you do not understand is a question, not a line to keep.
3. Run a check you trust: a validator, a linter, the tests, a dry run.
4. Paste the exact errors back, or fix them yourself.
5. Repeat until the check passes, then review the whole diff as a pull request.

A validator checks that a file follows its format's rules. A linter looks for common mistakes, and a dry run goes through the motions without changing anything.

A pull request is a proposed change that others review before it joins main. You already know most of these checks from the course. Each kind of file has one:
- Kubernetes YAML: `kubeconform -strict`, then `kubectl apply --dry-run=server` against kind
- Terraform: `terraform fmt -check`, `terraform validate`, and a plan you actually read (Days 31 to 35)
- Workflows: `actionlint` (Day 25)
- Shell scripts: `shellcheck` (Day 7)
- Ansible: `ansible-lint`, and a run with `--check --diff` (Days 36 and 37)
- Dockerfiles: `docker build --check .` (Day 19)
- Python: `ruff check .` and `pytest -q`

kubeconform is new here. It checks each Kubernetes object against the official schema for its kind, without a cluster. A schema is the official list of allowed fields and their types. With `-strict` it also rejects fields the schema does not know, which is the mistake models make most often.

A server dry run covers what a schema cannot. The object goes to the API server, the front desk of a Kubernetes cluster. The API server runs every check of a real apply, admission included (Day 64), and then throws the object away instead of storing it. The trade: kubeconform needs no cluster but knows only the schema. The dry run needs kind, the small practice cluster on your laptop, but it knows your cluster's rules.

Checks prove shape, not intent. kubeconform cannot know that your app listens on 8000, or that `/healthz` is the right path. The review in step 5 covers that part, and the worked example shows both halves. A check catches bad answers. Good context gives you fewer of them, and that comes next."""

S[3]["h"] = "Give it the context a new teammate would need"
S[3]["body"] = """The intern does much better on day two, once you have shown them your stove and your jars. A model works the same way. Context is everything it sees when it answers: your question, the files and errors you give it, and the chat so far.

The model continues the text it sees. With your exact error and versions in it, the likely continuation is about your case. Without them, it falls back on the most common case in its training data, which is often an older version or someone else's setup. Treat the model like a new teammate on their first day: skilled, but new to your setup. Give it:
- the exact error, pasted in full, never retold from memory
- the versions: `kubectl version`, `terraform version`, the image tag
- the file itself, or the lines around the problem
- what you already tried, and what must not change

Then ask for a plan before any code: the files it would change, and why. A plan takes a minute to read, and a wrong plan is cheaper to fix than a wrong diff. After that, go one small step at a time, with a check after each.

Context you give on every task belongs in the repository, the project's folder of files and history. The open format for it is AGENTS.md, a file at the root written in Markdown (plain text with light formatting). It holds the build and test commands, the rules, and what not to touch. An agent reads it at the start of each task and adds it to the model's context, as if you had pasted it in. Many tools read it, and Go deeper lists them.

Two tools have their own file as well:
- Claude Code reads `CLAUDE.md`. A one-line `CLAUDE.md` that says `@AGENTS.md` imports the shared file.
- GitHub Copilot reads `.github/copilot-instructions.md`, and AGENTS.md in some of its features.

The lab's `ai/AGENTS.md` is a real one for hello-devops. Keep yours short. Agents read it on every task, and a long file buries the rules that matter. With the context written down, an agent can do more than chat, so let's meet the agents."""

S[4]["h"] = "Coding agents in the terminal, the editor and the cloud"
S[4]["body"] = """A chat window answers questions. A coding agent does the work: it reads files, edits them and runs commands such as your tests, in a loop, until the task is done or it gets stuck. The tools fall into three groups. The names below are examples, not a ranking. The field changes every few months, and your company may allow only some of them.
- In the terminal (the text window where you type commands): Claude Code, OpenAI Codex CLI, Gemini CLI, GitHub Copilot CLI, Aider, opencode.
- In the editor: GitHub Copilot in VS Code, Cursor, JetBrains Junie, Zed.
- In the cloud: GitHub Copilot cloud agent and OpenAI Codex cloud.

A cloud agent works on its own. You hand it an issue, it works on a branch (a separate line of work in git) in a sandbox, and it opens a pull request. A sandbox is a closed-off machine where mistakes can't reach anything real.

The model inside still only writes text. The agent program around it reads that text and runs the commands the model asks for, so it can stop and ask you first. Every tool above does that before it runs a command or edits a file, unless you switch it off. Keep the approvals on for anything that touches a shared system. A test run on your laptop is fine to allow. `kubectl delete`, `terraform apply` and `git push --force` are not: they delete things in a cluster, change real cloud servers and overwrite shared history.

Three habits help with every agent:
1. Start each task on a new branch, so throwing the work away takes one command.
2. Keep tasks small: one endpoint, one manifest, one failing test.
3. Read the diff with `git diff` before you commit, never only the agent's summary of it.

Day 66 opens up that loop, gives agents tools in your cluster and in CI, and shows how to fence them in. First, though, the diff itself deserves a careful read."""

S[5]["h"] = "Review an AI diff like a teammate's pull request"
S[5]["body"] = """An AI-written change gets the same review as a teammate's pull request (Day 23), plus one extra suspicion. A person who writes a field name usually looked it up. A model may have written it because it sounded right, the way the intern named a brand of pectin that sounded right.

Read every line, and look hard for these:
- changes nobody asked for: renamed variables, reformatted files, a rewritten function
- names that must match: labels and selectors, ports, file paths, env vars
- new dependencies, and whether each one really exists (next section)
- safety that quietly went away: a `permissions:` block, `set -euo pipefail`, a probe, a pin
- escape hatches: `|| true`, `--no-verify`, `continue-on-error`, a skipped test
- tests that pass for the wrong reason, such as an assertion that is always true

A few of those words need a line. Env vars (environment variables) are named settings a program reads when it starts. A dependency is a package of someone else's code that yours needs. An escape hatch is any switch that lets a failure pass quietly.

When something looks odd, ask the agent why it wrote it, and then check the answer. Models write confident explanations for wrong code too.

The lab's `ai/REVIEW-CHECKLIST.md` turns this into boxes to tick, and `ai/check.sh` runs every check in the repository with one command. AGENTS.md tells agents to run that script before they call a task done, so you and the agent share one definition of done.

A good test before you merge: could you explain every line to a teammate? If not, ask, or rewrite that part yourself. Two risks remain that reading the YAML won't catch: what you paste in, and what the model pulls in."""

S[6]["h"] = "Secrets, customer data and invented packages"
S[6]["body"] = """Most assistants run the model on the vendor's servers (the computers of the company that sells the tool), so everything you paste leaves your laptop. Follow your company's AI policy, and use only the tools it has approved. Some things never go in, whatever the tool:
- secrets: tokens, passwords, private keys, kubeconfig files, `.env` files
- customer data, including logs with names, emails or IP addresses
- anything your contracts or your company's data rules keep inside

A kubeconfig file holds your login for a cluster. An IP address is the number that identifies a computer on a network, so it can point to a person. Scrub before you paste: replace a real token with `REDACTED`, and cut a log down to the lines that matter. Agents that read your files send them to the vendor too, so keep secrets outside the repository (Day 64).

The second risk is newer. Models sometimes invent package names that sound real. A package is ready-made code you install from a public store such as PyPI (for Python) or npm (for JavaScript). Attackers noticed, and they register those invented names with malware, harmful code, inside.

The attack is called slopsquatting, and many invented names come back when the same question is asked again. That repeatability is what makes the attack work: an attacker can ask the models common questions, note the names they invent, and register them. So treat every new dependency in an AI diff as unverified until you check it:
1. Does it exist? `pip index versions <name>` lists what PyPI has.
2. Is it the project you meant? Check its page: maintainer, source repository, age and releases.
3. Pin it like the rest, and let Dependabot and the scanners from Day 63 watch it.

MCP servers, which Day 66 installs, need the same care: a name in a registry does not prove who wrote the code. Everything in this lesson keeps a person at every step, which works for one assistant at your desk. It gets harder when an agent runs commands on its own, in your cluster or in CI."""

L["aside"] = {
    "title": "Who first noticed slopsquatting?",
    "body": ("Seth Larson of the Python Software Foundation named slopsquatting in April 2025. "
             "That same year, a USENIX Security 2025 paper by Spracklen and others tested 16 models on 576,000 Python and JavaScript code samples. "
             "It found package hallucination to be a systemic and persistent problem. "
             "Many invented names came back when the same question was asked again, which is the repeatability the attack needs."),
    "after": 6,
}

for k in ("analogy", "mistake", "real_world"):
    L.pop(k, None)

L["diagram_caption"] = "The verify loop: a tool you trust checks every draft, and a person reviews what tools cannot see."

W = L["worked"]["steps"]
W[0]["say"] = ("A replica is one running copy, a liveness probe is a regular check that the app is alive, and Redis is the small database that keeps the visit count. "
               "You ask an assistant to \"write a Kubernetes Deployment for hello-devops in namespace hello, 3 replicas, with a liveness probe and Redis as a backend\". "
               "You give it no files and no versions. It answers in seconds. The lab keeps that answer, unchanged, as `ai/examples/deployment-ai-draft.yaml`. These are the lines that matter.")
W[1]["say"] = ("Run kubeconform with `-strict`. It finds two mistakes that a plain YAML reader would never notice. "
               "`containerPort` must be a number, not a string. And `timeout` is not a probe field at all: the real one is `timeoutSeconds`.")
W[2]["say"] = ("Without `-strict`, kubeconform reports only the port, and the invented field slips through. "
               "The API server's own validation would reject it, but tools that switch validation off drop it silently. "
               "Then the probe keeps the default 1-second timeout. When you doubt a field, ask the cluster's schema with `kubectl explain` (output trimmed to the field list).")
W[3]["say"] = ("Copy the draft to `draft.yaml` and fix those two lines. Now kubeconform is happy. The API server is not. "
               "Some rules live only in the server, and a selector (the labels a Deployment uses to find its Pods) that does not match the Pod labels is one of them. "
               "That is why the loop ends with a server dry run against kind.")
W[4]["say"] = ("Now the review that no tool can do for you. The routes in app.py show the first problem: the probe uses `/health`, but the app serves `/healthz`. "
               "Three more things are wrong for hello-devops. The image is `:latest`, `REDIS_HOST` is `localhost` instead of the Service name `redis`, and there is no readiness probe on `/readyz`. "
               "The draft also sets a CPU limit, which the lab leaves out on purpose (Day 43).")
W[5]["say"] = ("Paste the tool output and your review notes back to the assistant, and ask for a fixed version. Then run the same checks again. "
               "When the result matches the tested `k8s/deployment.yaml`, both checks pass, and only then does it go into a pull request.")

T = L["task"]
T["steps"] = [
    "Copy `ai/AGENTS.md`, `ai/REVIEW-CHECKLIST.md` and `ai/check.sh` from the lab into your hello-devops repository, and put a copy of AGENTS.md at the root. Fix anything that does not match your repository.",
    "If your tool needs its own file, add it: a `CLAUDE.md` with the single line `@AGENTS.md`, or a `.github/copilot-instructions.md` that points to AGENTS.md.",
    "Run `ai/check.sh` yourself, and install missing tools until no check you care about says SKIP.",
    "Start a branch. Ask any assistant to explain, from AGENTS.md alone, how to test the repository. If it gets that wrong, your file is unclear.",
    "Ask for a plan, not code: a `/version` endpoint (a new address the app answers) that returns only `{\"version\": ...}`, with a test. Read the plan and correct it.",
    "Let it build one step at a time. After each step, run `ai/check.sh` and read `git diff`.",
    "Break the endpoint on purpose and watch the new test fail, to prove it tests something. Then undo the break.",
    "Review the whole diff with REVIEW-CHECKLIST.md, open a pull request, and let CI run. Write down one thing the assistant got wrong, or would have got wrong without a check.",
]
T["hints"] = [
    "No AI tool at hand? Use any free chat assistant, and paste the files and errors in yourself.",
    "If the assistant adds a package for a two-line endpoint, ask why. Flask, the web library the app already uses, has everything you need.",
    "app.py already reads `APP_VERSION`, so the new endpoint needs no new setting.",
]
T["done_when"] = "You are done when AGENTS.md sits at your repository root, `/version` has a test you have seen fail, and `ai/check.sh` and CI both pass."

L["explain_back"]["answer"] = ("I give the assistant the exact error, the versions and the file, and I ask for a plan before any code. "
                               "Every answer goes through a check I trust, such as kubeconform -strict, terraform validate and plan, or the tests, and I paste the errors back until it passes. "
                               "Checks only prove the shape, so I still review the diff like a teammate's pull request: matching names, invented fields, new packages and removed safety. "
                               "AGENTS.md holds the commands and rules, so the agent and I run the same checks.")

L["recap"] = [
    "A model predicts likely text: common shapes come out well, while exact flags, fields and versions are guesses.",
    "It sounds just as sure when it is wrong, so its confidence tells you nothing.",
    "The verify loop: draft, check with a tool you trust, feed the errors back, review the diff, then merge.",
    "Limits: schema checks prove shape only. A server dry run and your own review catch the rest.",
    "Give context as you would to a new teammate, and keep the repeated part in AGENTS.md.",
    "Never paste secrets or customer data, and check that every new package exists and is the one you meant.",
]

C = L["check"]
C[0]["why"] = "A schema check proves that fields and types exist. Only you, a dry run and the app's code can say whether the values fit."
C[1]["why"] = "AI tools invent package names that attackers then register, so the registry page and the real need come first. The agent's word is not a check."
C[2]["why"] = "Only a check that gives the same answer every time, such as terraform validate and a plan you read, can tell you what will happen. The model's yes is more predicted text."

I = L["interview"]
I[0]["a"] = ("I use them for first drafts I can check, such as Dockerfiles, YAML, Terraform blocks and scripts, and for explaining errors or summarizing long plans and logs. "
             "I give the exact error, the versions and the file, and I ask for a plan before code. "
             "Nothing reaches main without a check I trust, such as kubeconform, terraform validate and plan, actionlint or the tests, and a normal pull request review. "
             "I never paste secrets or customer data, and I only use tools my company has approved.")
I[1]["a"] = ("Language models sometimes invent package names that sound real, and attackers register those names with malware inside. "
             "Seth Larson of the Python Software Foundation named it in 2025. "
             "I treat every new dependency in an AI-written change as unverified: I check that it exists, who publishes it, its history, and whether we need it at all. "
             "Then I pin it and let Dependabot and the scanners in CI watch it like any other package.")
I[2]["a"] = ("The commands to set up, build, test and run the project, exactly as a newcomer would type them. "
             "The rules that matter most, such as pinning, no secrets in git, and a test with every change. "
             "What an agent must never do, such as apply to a cluster or force-push. "
             "And a short definition of done, ideally one script that runs every check, so people and agents use the same one.")

L["deeper"]["body"] = """First, who reads AGENTS.md. Many tools read it, among them OpenAI Codex, Cursor, Zed and GitHub Copilot. Gemini CLI and Aider read it after a one-line setting. In a monorepo (one repository that holds many projects), the AGENTS.md closest to the edited file wins.

An agent that runs `ai/check.sh` before it finishes is a good start. It is not the end, because an agent can also make a check pass the wrong way. When a test fails, the quickest edit is sometimes to the test: delete it, loosen an assertion, add `# noqa`, or relax a setting in the linter's config. People do this too, under pressure. So the checks that decide must run somewhere the change cannot quietly edit them first.

That place is CI with required checks (Day 25). The pull request runs the same `ruff`, `pytest`, kubeconform and actionlint, and a ruleset blocks the merge while any of them is red. If an AI change edits a test, a linter config or `ai/check.sh` itself, that file is in the diff, and your review catches it. A rule worth adding to AGENTS.md: changes to checks go in their own pull request, with a reason.

Two refinements make the checks sharper:
- Pin the schema to your cluster. `kubeconform -kubernetes-version 1.37.0 -strict` checks against the version you run, so a field that only exists in a newer release is caught too.
- Validate what you really apply. For Helm, pipe `helm template` into kubeconform; for Kustomize, pipe `kubectl kustomize overlays/dev`. A chart can be valid as templates and produce invalid YAML for one set of values.

Also make the output easy to feed back. kubeconform has `-output json`, and most linters print a file and line for each problem. Paste those exact lines into the agent, never your own summary of them. The model fixes "line 31: additional properties 'timeout' not allowed" far more reliably than "the probe looks wrong".

Finally, measure. For a month, note every AI change that a check or a review caught, and what kind of mistake it was. You will see your own map of good at and bad at, which is more useful than mine. It also tells you which check to add next."""

L["closing"] = """We started with an intern's perfect-looking recipe card for a stove you don't own. The AI-written Deployment looked just as neat. Then kubeconform, a dry run and one careful read found a port written as text, an invented field, labels that didn't match and a probe on the wrong path.

Pick one file an assistant wrote for you recently and run its check today: kubeconform, terraform validate, actionlint or shellcheck. You may be surprised.

Next, we'll hand the intern real keys: agents that run tools on their own, in your cluster and in CI. How much can you let them do, and how do you fence them in?"""

new = {}
for k in L:
    if k in ("opening", "closing", "aside"):
        continue
    new[k] = L[k]
    if k == "goal":
        new["opening"] = L["opening"]
    if k == "sections":
        new["aside"] = L["aside"]
    if k == "deeper":
        new["closing"] = L["closing"]
P["lessons"][P["lessons"].index(L)] = new
PATH.write_text(json.dumps(P, ensure_ascii=False, indent=1) + "\n")
print("d65 written")
