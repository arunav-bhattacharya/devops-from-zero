#!/usr/bin/env python3
"""Human-writing pass (blog mode) over content/p13.json and content/p14.json.

Each edit is either
  ("set", path, new_text)          replace a whole prose field, or
  ("sub", path, old, new)          replace one exact substring (must occur once).
Only prose fields are touched. It reads and writes the live JSON files, so restore the originals first:
  cp p13.orig.json ../../../../content/p13.json; cp p14.orig.json ../../../../content/p14.json
"""
import json
import pathlib
import sys

ROOT = pathlib.Path("/home/user/devops-from-zero")


def get(obj, path):
    for k in path.split("."):
        obj = obj[int(k)] if isinstance(obj, list) else obj[k]
    return obj


def put(obj, path, value):
    *head, last = path.split(".")
    for k in head:
        obj = obj[int(k)] if isinstance(obj, list) else obj[k]
    if isinstance(obj, list):
        obj[int(last)] = value
    else:
        if last not in obj:
            raise KeyError(path)
        obj[last] = value


def apply(doc, edits, name):
    for e in edits:
        kind, path = e[0], e[1]
        cur = get(doc, path)
        if not isinstance(cur, str):
            sys.exit(f"{name} {path}: not a string")
        if kind == "set":
            put(doc, path, e[2].strip())
        elif kind == "sub":
            old, new = e[2], e[3]
            n = cur.count(old)
            if n != 1:
                sys.exit(f"{name} {path}: expected 1 match, found {n}: {old[:60]!r}")
            put(doc, path, cur.replace(old, new))
        else:
            sys.exit(f"bad edit kind {kind}")


L52, L53 = "lessons.0", "lessons.1"
L54, L55 = "lessons.0", "lessons.1"

# ----------------------------------------------------------------------------------------------
# Part 13: DevSecOps
# ----------------------------------------------------------------------------------------------
P13 = [
    ("set", "intro", """
Part 13 goes back over everything you have built and asks how an attacker would get in. Day 52 follows the supply chain from a git tag to a signed image you can verify, using three real attacks from 2024 to 2026. Day 53 covers what runs in the cluster: secrets, access rights, and the rules the cluster checks before it stores an object. Security comes this late because you can only secure a pipeline and a cluster you already understand.
"""),
    ("set", "recap.5", "None of it helps until something checks it: cosign verify, gh attestation verify, and later an admission policy."),
    ("set", "resources.1.why", "A calm walk through how a trusted contributor hid a backdoor in a library that almost every Linux system has."),
    ("set", "resources.3.why", "What each build level promises and which attacks it stops, in the spec's own words."),

    # ---------------- d52 ----------------
    ("set", f"{L52}.guess.why", "A git tag is a movable pointer, and attackers moved tj-actions tags in 2025 and trivy-action tags in 2026. Nobody can move a full commit SHA."),

    ("sub", f"{L52}.sections.0.body",
     "All of this together is your software supply chain: every piece your code passes through between your keyboard and production.",
     "That whole set is your software supply chain: every piece your code passes through between your keyboard and production."),
    ("sub", f"{L52}.sections.0.body",
     "DevSecOps means building security checks into that chain as automatic steps, owned by the people who ship. Two ideas carry most of it:",
     "DevSecOps means building security checks into that chain as automatic steps, owned by the people who ship. Most of it comes down to two ideas:"),

    ("sub", f"{L52}.sections.1.body",
     "Real incidents teach this better than any diagram. Each of these hit a different link, and none of them touched the victims' own code.",
     "The three attacks below each hit a different link in the chain. None of them touched the victims' own code."),
    ("sub", f"{L52}.sections.1.body",
     "Three lessons follow:\n",
     "Each attack leaves you a rule you can act on:\n"),

    ("set", f"{L52}.sections.2.body", """
When you write `uses: some-org/action@v4`, it reads like a fixed version. The `v4` is a git tag, though: a name that points at one commit, like a sticky note on a page. Anyone with push rights to that repository can peel the note off and stick it on a different commit. Your next run then executes the new code, and nothing in your own repository changed.

A commit SHA is a 40-character hash of the commit's content: its files, its parent commit, its author and its message. Change one byte and you get a different SHA, so `uses: some-org/action@<full-sha>` always means the same code. In March 2026 the attacker moved 76 `trivy-action` tags, and every old SHA still pointed at the code it always had.

Look at the scan step in the lab's `release.yml`:
`uses: aquasecurity/trivy-action@ed142fd0673e97e23eac54620cfb913e5ce36c25 # v0.36.0`

GitHub runs the SHA. The comment is only for humans, and Dependabot (Day 21) updates both when a new release appears. Pinning has a price: pinned code never changes by itself, so you need a bot to bring you fixes and a person to review them.

Image tags move too. Someone can push `hello-devops:1.2.0` again with new content, but a digest (`@sha256:` followed by 64 hex characters) cannot change. So the workflow signs the digest.

One gap in the lab: `actions/checkout@v7` and `actions/attest@v4` still use tags. They come from GitHub itself, and many teams accept that risk. Stricter teams pin them too, and for a release workflow I would.
"""),

    ("sub", f"{L52}.sections.3.body",
     "Why keep a list? Picture the morning the next xz is announced. Without SBOMs, every team pulls and inspects its images to find out whether they are affected.",
     "You need that list most on the morning the next xz is announced. Without SBOMs, every team pulls and inspects its images to find out whether they are affected."),
    ("sub", f"{L52}.sections.3.body",
     "My rule: fail on HIGH and CRITICAL findings that already have a fixed version, and track the rest. That is exactly what the release workflow does with",
     "My rule: fail on HIGH and CRITICAL findings that already have a fixed version, and track the rest. The release workflow does this with"),

    ("set", f"{L52}.sections.4.body", """
A scan tells you what is inside. A signature answers two other questions: who made this artifact, and has anyone changed it since? Classic signing needs a private key, and a private key in CI is one more secret that can leak.

**Keyless signing** with cosign, from the Sigstore project, removes the stored key. When the release job signs, five things happen:
1. The job asks GitHub for an OIDC token: a short signed note that says "I am release.yml in this repository, running for tag v1.2.0". You met OIDC on Day 21, for cloud logins.
2. cosign makes a fresh key pair that lives only in memory.
3. Fulcio, Sigstore's certificate authority, checks the token and issues a certificate for that key. It is valid for 10 minutes and has the workflow identity written inside.
4. cosign signs the image digest and stores the signature in the registry, next to the image.
5. The signing event goes into Rekor, a public log that only grows. Nobody can quietly remove or rewrite an entry.

To verify, you name the identity you expect. `cosign verify` takes `--certificate-identity` (your workflow file and tag) and `--certificate-oidc-issuer` (GitHub's token service). An image signed by anyone else fails. A pass tells you where the image came from and that nobody changed it. It says nothing about quality, and a signed image can still be full of bugs.

The [cosign README](https://github.com/sigstore/cosign/blob/main/README.md) adds two warnings. Sign the digest, never a tag, or you might sign something you did not intend. And when you sign as a person, your email goes into the public log, where it cannot be removed.
"""),

    ("sub", f"{L52}.sections.5.body",
     "It is a signed statement in a standard format (in-toto), bound to the artifact's digest. Think of a delivery note that names the factory and the production line, with a stamp on it.\n\nSLSA (say \"salsa\") turns this into levels. The build track of the [SLSA spec](https://github.com/slsa-framework/slsa/blob/main/spec/build-track-basics.md):",
     "It is a signed statement in a standard format (in-toto), bound to the artifact's digest.\n\nSLSA (say \"salsa\") grades how far you can trust that statement. The build track of the [SLSA spec](https://github.com/slsa-framework/slsa/blob/main/spec/build-track-basics.md) has four levels:"),
    ("sub", f"{L52}.sections.5.body",
     "Now the step most teams skip. [GitHub's own docs](https://docs.github.com/en/actions/concepts/security/artifact-attestations) say that generating attestations alone gives no security benefit. Someone has to verify them, for example with `gh attestation verify`. Until a person or a machine checks it, an attestation is a receipt nobody reads.",
     "Most teams stop there, and [GitHub's own docs](https://docs.github.com/en/actions/concepts/security/artifact-attestations) warn that generating attestations alone gives no security benefit. A person or a machine has to verify them, for example with `gh attestation verify` before a deploy."),

    ("sub", f"{L52}.sections.6.body",
     "follow one tag push through it. The order is on purpose:",
     "follow one tag push through it. Each step sits where it does for a reason:"),
    ("sub", f"{L52}.sections.6.body",
     "Every step after the push uses `${IMAGE}@${DIGEST}`, never a tag. And every third-party action is pinned to a SHA, including the scanner that was attacked in March 2026. The workflow is the same file you wrote on Day 21. Today adds steps 2, 3, 5, 6 and 7, and the two rights they need.",
     "Every step after the push uses `${IMAGE}@${DIGEST}`, never a tag, and every third-party action is pinned to a SHA. That includes the scanner that was attacked in March 2026. You wrote this file on Day 21; today adds steps 2, 3, 5, 6 and 7, and the two rights they need."),

    ("set", f"{L52}.analogy", """
A jar of jam on a shop shelf goes through the same checks. The ingredient label is the SBOM, and checking that label against the food recall list is the scan. The tamper-evident seal with the factory's stamp is the signature. The delivery note that names the factory and the production line is the provenance, and the shop's rule "no seal, no sale" is verification before deploy. The seal tells you who packed the jar and that nobody opened it. It cannot tell you whether the jam is any good, and a signature cannot either.
"""),

    ("set", f"{L52}.worked.steps.1.say", "Now you are the attacker, holding a stolen token. Change the code, commit, and move the tag with `-f`. A workflow that says `@v1` would now run the new code, and its own file did not change at all."),
    ("set", f"{L52}.worked.steps.3.say", "Next, check a real pin. `git ls-remote` asks GitHub what a tag points to, without cloning. Release tags are often annotated: a small tag object of their own. The line ending in `^{}` is the commit underneath, and that commit's SHA is the one in the lab's workflow."),

    ("set", f"{L52}.mistake", """
You generate signatures, SBOMs and attestations, and then nothing ever checks them. GitHub's docs say attestations give no security benefit until someone verifies them. So put a verify step in front of every deploy: `security/verify-release.sh` before a manual deploy, and later an admission policy in the cluster (see Go deeper).
"""),
    ("set", f"{L52}.real_world", """
Auditors at a payments company ask two questions about every release: what is in it, and who built it? A release pipeline that stores an SBOM and a signed provenance attestation per image answers both. When a critical CVE is announced, the security team searches the stored SBOMs and opens pull requests for the affected services, instead of asking every team to check by hand.
"""),

    ("sub", f"{L52}.deeper.body",
     "Three ideas take today's work further.\n\nFirst, look one level down. `trivy-action` is a composite action: it runs another action, `aquasecurity/setup-trivy`, to install the Trivy binary. Your SHA pin fixes the outer code. What about the inner one? Open the action's `action.yaml` at the SHA you pinned, and you find:",
     "Start one level down. `trivy-action` is a composite action: it runs another action, `aquasecurity/setup-trivy`, to install the Trivy binary. Your SHA pin fixes the outer code, so check what that code pulls in. Open the action's `action.yaml` at the SHA you pinned, and you find:"),
    ("sub", f"{L52}.deeper.body",
     "Second, a caveat on SHAs.",
     "SHAs come with a caveat of their own."),
    ("sub", f"{L52}.deeper.body",
     "Third, let the cluster do the verifying.",
     "Finally, you can let the cluster do the verifying."),

    # ---------------- d53 ----------------
    ("set", f"{L53}.guess.why", "Base64 is an encoding, not encryption, and etcd stores Secrets unencrypted by default. Anyone who may create a Pod in the namespace can mount the Secret and print it."),

    ("set", f"{L53}.sections.0.body", """
Day 34 showed that a Secret's values are base64 encoded. Base64 only writes the same bytes in another alphabet, and anyone can undo it with `base64 -d`. The [Kubernetes docs](https://kubernetes.io/docs/concepts/configuration/secret/) call such a value obscured but not secret.

Two less obvious facts make the group of readers bigger than you think:
- By default, Secrets are stored unencrypted in etcd, the cluster's database. Anyone with access to etcd or its backups can read them.
- Anyone who may create a Pod in a namespace can read every Secret in that namespace. They never need `get secrets`. They start a Pod that loads the Secret and prints it. The same holds for anyone who may create a Deployment.

If the second one sounds unlikely, the worked example below does it on your own cluster. The RBAC docs add one more detail: `list` and `watch` on Secrets also reveal the values, because a list returns the full objects.

So the protection has layers:
1. On a real cluster, turn on encryption at rest for Secrets.
2. Keep the list of people and programs that can create Pods in a namespace short. The namespace is the real boundary.
3. Keep the real values in a secrets manager and copy them into the cluster only where they are needed.
4. Never put the value in git, not even for one commit.
"""),

    ("sub", f"{L53}.sections.1.body",
     "Git never forgets. Commit a token, delete it in the next commit, and the token is still in history, in every clone and every fork. So deleting the file fixes nothing. The fix is to rotate: revoke the leaked value where it was issued and create a new one.",
     "Commit a token, delete it in the next commit, and the token is still in history, in every clone and every fork. Deleting the file fixes nothing. You have to rotate: revoke the leaked value where it was issued and create a new one."),

    ("sub", f"{L53}.sections.2.body",
     "The values live there, but Kubernetes still wants a Secret object. Something has to carry the value into the cluster. There are three common patterns, and the question to ask is which file is safe to commit:",
     "The values live there, but Kubernetes still wants a Secret object, so something has to carry each value into the cluster. Three patterns are common, and for each one the question is which file you can safely commit:"),

    ("sub", f"{L53}.sections.3.body",
     "Test before you trust. `kubectl auth can-i`",
     "Before you rely on a rule, test it. `kubectl auth can-i`"),

    ("sub", f"{L53}.sections.4.body",
     "Here is the trap: enforce checks Pods, not Deployments. A Deployment that breaks the rule is accepted, and then its Pods are refused. `kubectl apply` says `configured` and nothing starts. Warn mode does check Deployments, so I set `warn` one level stricter than `enforce`. You see what would break next, before anything does.",
     "Enforce mode has a trap. It checks Pods, and it does not check Deployments. A Deployment that breaks the rule is accepted, and then its Pods are refused, so `kubectl apply` says `configured` and nothing starts. Warn mode does check Deployments. I set `warn` one level stricter than `enforce`, so I see what would break next before anything does."),

    ("sub", f"{L53}.sections.5.body",
     "Pod Security Admission covers Pod hardening and nothing else. Your own rules need a policy engine. Think of rules such as \"no `:latest` tags\" or \"every workload has a team label\". With **policy as code**, those rules are files in git: reviewed in pull requests, tested in CI, and enforced by an admission controller.",
     "Pod Security Admission covers Pod hardening and nothing else. A rule of your own, such as \"no `:latest` tags\" or \"every workload has a team label\", needs a policy engine. With **policy as code**, those rules are files in git. You review them in pull requests and test them in CI, and an admission controller enforces them."),

    ("sub", f"{L53}.sections.6.body",
     "Here is Part 13 as a list you can tick. Each item is something you can show with one command or one file:",
     "Part 13 fits in a list you can tick, and you can prove each item with one command or one file:"),

    ("set", f"{L53}.analogy", """
A night club has a version of each of these. RBAC is the guest list: it decides who gets in and which rooms each guest may enter. Admission control is the bouncer who also checks what you carry (no glass bottles), whoever you are. The secrets manager is the cloakroom, with a ticket for every coat and a log of who took what. A bouncer might wave a friend through, but an admission policy never does. It treats every request the same, so one typo in a Deny policy can lock out everybody, you included.
"""),

    ("set", f"{L53}.mistake", """
Switching a new policy straight to Deny for the whole cluster blocks your own tools too: Argo CD syncs, the monitoring stack, even add-ons in kube-system. Scope each policy to the namespaces it is meant for and start in Audit. Read the PolicyReports for a few days, fix what they find, and only then switch to Deny.
"""),
    ("set", f"{L53}.real_world", """
Product teams want to hear about a policy failure in their pull request, long before anything blocks a deploy. So a platform team keeps a small set of Kyverno policies in a git repository, reviews changes like code, and shows failures in PolicyReports and pull request checks. Database passwords live in the cloud's secret manager and ESO copies them into each namespace, so rotating a password is one change in one place.
"""),

    ("sub", f"{L53}.deeper.body",
     "Two tools from today deserve a closer look before you use them at work.\n\nKubernetes has its own CEL policies.",
     "Kubernetes has its own CEL policies."),
    ("sub", f"{L53}.deeper.body",
     "That is a cheap habit worth copying: test a policy against good and bad examples before it guards a real cluster.",
     "Testing a policy against good and bad examples before it guards a real cluster costs very little, and I would make it a habit."),
    ("sub", f"{L53}.deeper.body",
     "If the failure policy is Ignore, requests pass unchecked while it is down. Neither is free. Three habits help:",
     "If the failure policy is Ignore, requests pass unchecked while it is down. You choose which risk to carry, and three habits make both smaller:"),
]

# ----------------------------------------------------------------------------------------------
# Part 14: Platform engineering, AI and your capstone
# ----------------------------------------------------------------------------------------------
P14 = [
    ("set", "intro", """
Part 14 is the last part. Day 54 shows what happens when many teams need what you built. Platform teams build golden paths, FinOps gives every cost an owner, and AI agents work inside the same guardrails as people. Day 55 is your capstone. One change travels through every part of the course with a check at each stage, and you finish with a plan for what to learn next.
"""),
    ("set", "resources.10.why", "Free online, and the best next read on running systems reliably. One chapter a week is a good pace."),

    # ---------------- d54 ----------------
    ("set", f"{L54}.sections.0.body", """
List what hello-devops needs by now. A Dockerfile, two workflows with pinned actions, Kubernetes YAML and an Argo CD Application. A ServiceMonitor, a dashboard, log shipping and tracing. Policies, and a way to get secrets. You learned all of it in this course. Now picture 40 product teams, each building that alone. They solve the same problems 40 times, in 40 slightly different ways, and whoever is on call has to learn every one.

Most large companies answer this with platform engineering. A platform team builds an internal developer platform (IDP): the self-service capabilities that product teams use to build, ship and run software. The [CNCF platforms white paper](https://tag-app-delivery.cncf.io/whitepapers/platforms/) puts self-service at the centre. A developer gets an environment, a database or a pipeline without filing a ticket and waiting a week.

The team runs the platform as a product, with developers as its customers. In practice, a platform team:
- Talks to its users and watches where they get stuck.
- Publishes a roadmap and takes feature requests.
- Measures success by adoption and speed, never by the number of tools installed.

A classic operations team does work for other teams, through tickets. A platform team builds things so that other teams can do the work themselves. DevOps ideas such as shared ownership and automation still apply; the platform makes them the easy option.
"""),

    ("sub", f"{L54}.sections.1.body",
     "built on compliant and tested patterns. Two of those words carry weight:",
     "built on compliant and tested patterns. Each of those two words is a promise:"),

    ("sub", f"{L54}.sections.2.body",
     "The adoption row teaches the most. A platform that teams use because a manager said so sits at level 2. A platform that teams choose because it is faster sits at level 3.",
     "Start with the adoption row, which says the most about whether the platform helps. A platform that teams use because a manager said so sits at level 2. One that teams choose because it is faster sits at level 3."),

    ("set", f"{L54}.sections.4.body", """
About 90% of the nearly 5,000 technology professionals in Google's DORA survey used AI at work, according to its [2025 report on AI-assisted software development](https://dora.dev/dora-report-2025/). Its main finding is that AI is an amplifier: it makes strong teams stronger and struggling teams worse. More AI use now goes with higher delivery throughput, and it still goes with less stable delivery.

You meet AI in three places:
- Coding agents. [GitHub's docs](https://docs.github.com/en/copilot/concepts/agent-capabilities/about-agents/about-github-copilot-agents) define an agent as a system that can plan a task, use tools, inspect the results and adjust. You assign an issue, the agent works on a branch, and it opens a pull request.
- CI and operations. Explaining a failed build, drafting a fix, summarizing a Terraform plan, sorting new issues. GitHub Agentic Workflows run such agents inside GitHub Actions, with read-only tokens by default.
- Incident response. Pulling together logs, metrics and runbooks, and drafting a timeline. A human should still decide on rollbacks, customer messages and the final root cause.

Agents reach your tools through MCP, the [Model Context Protocol](https://github.com/modelcontextprotocol/modelcontextprotocol): an open standard for connecting an AI assistant to other systems. An MCP server wraps one system and offers its actions as tools that the agent can call. There are MCP servers for GitHub, for Terraform from HashiCorp, and for Kubernetes.

GitHub's docs leave three jobs with you: you define the goal and the limits, you grant the access, and you review the work.
"""),

    ("sub", f"{L54}.sections.5.body",
     "Why a custom Role, and not the built-in `view` ClusterRole? The built-in role would work today, but it is aggregated. Tools such as Argo CD or Kyverno can add their own rules to it when you install them. A Role that lists every action stays exactly as written.\n\nThis is where the GitOps setup from Part 8 pays off again. With Argo CD applying git, an agent never needs write access to the cluster.",
     "The lab writes its own Role instead of binding the built-in `view` ClusterRole. The built-in role would work today, but it is aggregated: tools such as Argo CD or Kyverno can add their own rules to it when you install them. A Role that lists every action stays exactly as written.\n\nThe GitOps setup from Part 8 helps here too. Argo CD applies whatever is in git, so an agent never needs write access to the cluster."),

    ("set", f"{L54}.analogy", """
A platform works like the shared services in a big office building. Every company in the building uses the same reception, mail room, network and security desk, so no tenant builds its own. A golden path is the standard office fit-out: you move in on Monday and start work on Monday. Buildings change slowly, though, and a platform has to change every month as its users do. A tenant who tears out the standard fit-out is also telling the landlord something about it.
"""),

    ("set", f"{L54}.mistake", """
Don't adopt every trending tool at once. Each tool in this lesson solves a problem you only feel at a certain size. Backstage pays off with many teams, not one repository, and a FinOps tool is useless until workloads carry owner labels. Get the basics solid on one real project, then add a tool when you can name the pain it removes.
"""),
    ("set", f"{L54}.real_world", """
When a team needs a new service, the platform team's golden path sets up CI, signing, an Argo CD app, dashboards and a team label in one go. Finance gets a weekly cost report per team from those labels, and the teams with the biggest unused requests get a pull request that right-sizes them. An AI agent with a read-only identity drafts the routine upgrade pull requests, and humans review and merge them through the same pipeline.
"""),

    ("sub", f"{L54}.deeper.body",
     "You now have a service with every DevOps piece in place, which makes it a good template. Here is how a platform team would turn it into a golden path, at small scale:",
     "Your hello-devops repository now has every DevOps piece in place, so it makes a good template. A platform team would turn it into a small golden path in four steps:"),

    # ---------------- d55 ----------------
    ("set", f"{L55}.sections.0.body", """
A capstone is one final project that uses every part of a course together. Yours has a simple story: one small code change travels from your laptop to users, and at every step you can prove it got there.

Each lesson already had a task, so why one more project? Knowledge sticks when you use it again, later and in a new mix. Each part taught one tool in a clean room. The capstone puts them all in one room, where they get in each other's way as they do at work. A Kyverno policy blocks your Argo CD sync, or a port-forward you forgot makes Prometheus look empty. You cannot practise fixing that kind of clash one tool at a time.

You work with both lab apps:
- hello-devops, the Python app you have shipped since Day 2, through the full pipeline to kind.
- hello-jvm, the Kotlin build from Part 5, built and tested by Gradle in its own CI.

Three rules keep it manageable:
1. Go in order. Each stage depends on the ones before it.
2. A stage is done when its acceptance check passes, not when it looks fine.
3. Commit after each stage, so you can always go back to the last green point.

Expect several sittings, perhaps a week or two of your usual 45 minutes a day. Nothing in it is new material, so all of that time goes into practice.
"""),

    ("sub", f"{L55}.sections.2.body",
     "The second one can fail, and that is what makes it useful.",
     "The weak version cannot clearly fail, so passing it tells you nothing."),
    ("sub", f"{L55}.sections.2.body",
     "Run it after every stage, not only after the one you just did. Adding a later stage often breaks an earlier one: a new policy that rejects Redis, or a port-forward that grabbed port 8081. An older line that turns red tells you exactly where to look, which is the same idea as running the whole test suite and not only the newest test.",
     "Run it after every stage, and read every line, not only the one for the stage you just finished. Adding a later stage often breaks an earlier one: a new policy that rejects Redis, or a port-forward that grabbed port 8081. An older line that turns red points you straight at the cause. You run the whole test suite for the same reason, not only the newest test."),

    ("set", f"{L55}.sections.3.body", """
A game day is a planned session where you break things on purpose and watch how the system, and you, respond. So far you have only seen hello-devops working, which tells you little about what happens when Redis dies. Before each drill, write down what you expect to see. Afterwards, write down what happened. Wherever the two differ, your picture of the system was wrong, and that is what you write up.

Five drills, each testing a different part of the course:
1. Deploy an image tagged `:latest` through git. Expect Kyverno to reject it and Argo CD to show the sync error.
2. Delete one hello-devops Pod. Expect the Deployment to replace it and the dashboard to show only a blip.
3. Scale Redis to 0. Expect `/readyz` to return 503, the Pods to go unready, an alert to fire, error logs in Kibana and a failed span in Jaeger.
4. Change the Deployment by hand with `kubectl edit`. Expect Argo CD's self-heal to put git's version back.
5. Release a version that fails its readiness probe. Expect the rollout to stall, then fix it with `git revert` alone.

If you only have time for one, do drill 3. A single fault shows up in metrics, logs and traces at once, which is why you built all three.

For each drill, write a short runbook: how you noticed, what you checked, what fixed it. Then write one blameless postmortem (Day 41) for the drill that surprised you most. Interviewers like these, because they show how you think when something is broken.
"""),

    ("sub", f"{L55}.sections.4.body",
     "Point 5 matters most. Write each decision as a short architecture decision record (ADR): the situation, the options, what you chose and what it costs. Anyone can install a tool by following a tutorial. Explaining why you chose it, and what you gave up, shows judgment.",
     "Spend the most time on point 5. Write each decision as a short architecture decision record (ADR): the situation, the options, what you chose and what it costs. Anyone can follow a tutorial to install a tool. Your reasons for choosing it, and what you gave up, are what show judgment."),
    ("sub", f"{L55}.sections.4.body",
     "A concrete story about a Redis outage in your own cluster beats a list of 20 tools on a CV.",
     "A story about a Redis outage in your own cluster tells an interviewer more than a list of 20 tools on a CV."),

    ("sub", f"{L55}.sections.6.body",
     "Here is the plan I would follow, at your current pace of 30 to 45 minutes a day:",
     "At your current pace of 30 to 45 minutes a day, this is the plan I would follow:"),
    ("sub", f"{L55}.sections.6.body",
     "At work, look for the place where this course meets your Kotlin and Gradle day job. A Gradle build cache in CI, a signed JVM image, a team label on a service, or an alert on an SLO. One improvement your team uses is worth more than three new tools on your laptop.",
     "At work, look for places where this course meets your Kotlin and Gradle day job, for example:\n- A Gradle build cache in CI.\n- A signed JVM image.\n- A team label on a service.\n- An alert on an SLO.\n\nShip one of those for your team before you install another tool on your laptop."),

    ("set", f"{L55}.analogy", """
The capstone is your driving test after months of lessons in an empty car park. Each lesson taught one skill alone, such as steering, mirrors or parking. The test puts them all on a real road at once, with traffic, and the examiner ticks specific boxes on a sheet. Yours is kinder than a real test: you can run `capstone-check.sh` as often as you like, and failing it costs nothing.
"""),

    ("set", f"{L55}.worked.steps.4.say", "Run the whole script at this early point, with the app address set to the container. Almost everything fails, which is normal this early. Read the output as your to-do list, in order."),

    ("set", f"{L55}.mistake", """
Building all 14 stages first and testing at the end leaves you with five broken things at once, and you cannot tell which one causes the others. Finish one stage, make its check pass, commit, and only then start the next.
"""),
    ("set", f"{L55}.real_world", """
A new platform engineer's first project can look a lot like this capstone. They take one service from commit to production on the golden path, with every check green, and present it to the team. The team learns where the path is rough, and the new engineer learns the whole system in two weeks instead of six months.
"""),

    ("sub", f"{L55}.deeper.body",
     "Here is the strongest capstone test I know: delete the cluster and rebuild it from git.",
     "The hardest capstone test I know is to delete the cluster and rebuild it from git."),
    ("sub", f"{L55}.deeper.body",
     "Two things will bite you.",
     "Two things usually go wrong."),
    ("sub", f"{L55}.deeper.body",
     "In an interview, \"the whole platform rebuilds from git in N minutes\" gets attention. It shows that you understand GitOps, infrastructure as code and recovery at once.",
     "In an interview, \"the whole platform rebuilds from git in N minutes\" covers GitOps, infrastructure as code and disaster recovery in one sentence."),
]


def main():
    for name, edits in (("p13", P13), ("p14", P14)):
        path = ROOT / "content" / f"{name}.json"
        doc = json.loads(path.read_text())
        apply(doc, edits, name)
        with open(path, "w") as f:
            json.dump(doc, f, ensure_ascii=False, indent=1)
        print(f"{path}: {len(edits)} edits applied")


if __name__ == "__main__":
    main()
