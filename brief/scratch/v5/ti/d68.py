"""Fifth pass (book voice) for d68, Your capstone, and what to learn next. Writer: ti.
Replaces only prose fields of d68 in content/p19.json."""
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[4]
PATH = ROOT / "content/p19.json"
P = json.loads(PATH.read_text())
L = next(x for x in P["lessons"] if x["id"] == "d68")

L["goal"] = ("By the end you can take hello-devops and hello-jvm through every part of the course as one capstone, "
             "prove each stage with a check, present the result, and plan your next certification and three months of learning.")

L["opening"] = """The new path through the park opens on Saturday. On Friday evening, the keeper walks it once more, from the gate to the station, with a clipboard. Does every lamp come on at dusk? Does the little bridge hold a heavy bin lorry? Does the drain by the pond take a bucket of water? Each part passed its own test when it was built. The walk is the first time they all have to work together.

Skipping that walk is tempting. Every piece was checked, so the whole thing must be fine. That is exactly how a lamp ends up wired to the same switch as the sprinklers.

Last time, we turned hello-devops into a paved path for other teams. In this lesson, you walk the whole path yourself: one change, every part of the course, a check at every step. Then we'll plan what comes after the course. Before we start, make a guess, and keep it in mind."""

L["guess"]["q"] = "You want to show an interviewer that you can do DevOps work. Which gives the strongest evidence?"
L["guess"]["why"] = ("A working repository with checks shows you can connect the pieces and prove it. "
                     "Certificates help get past job filters, but even the CKA exam's official list of topics gives troubleshooting the biggest weight, and projects teach that.")

plain = {
    "Capstone": "One final project that uses every part of a course together, end to end.",
    "Acceptance check": "A test you can run that proves one piece of work is done, with a clear pass or fail.",
    "Game day": "A planned session where you break something on purpose and watch how the system and you respond.",
    "Runbook": "Short written steps for one known problem: how to notice it, check it and fix it.",
    "ADR": "Architecture decision record: a short note on one technical decision, the options and why you chose one.",
    "Curriculum": "The official list of an exam's topic areas and how much each one counts, published by the exam's owner.",
}
for t in L["terms"]:
    t["plain"] = plain[t["term"]]

S = L["sections"]

S[0]["h"] = "What the capstone is, and why it works"
S[0]["body"] = """A capstone is one final project that uses every part of a course together. Yours has a simple story: one small code change travels from your laptop to users, and at every step you can prove it got there. That is the keeper's walk from the gate to the station.

Each lesson already had a task, so why one more project? Knowledge sticks when you use it again, later and in a new mix. Each part taught one tool in a clean room. The capstone puts them all in one room, where they get in each other's way as they do at work. A Kyverno policy blocks your Argo CD sync, or a port-forward you forgot makes Prometheus look empty. You cannot practise fixing that kind of clash one tool at a time.

Teams know this too. A new platform engineer's first project can look a lot like this capstone: one service from commit to production on the golden path, every check green. The team learns where the path is rough, and the newcomer learns the whole system in weeks instead of months.

You work with both lab apps:
- hello-devops, the Python app you have shipped since Day 2, through the full pipeline to kind.
- hello-jvm, the Kotlin build from Part 7, built and tested by Gradle in its own CI.

hello-devops is the tiny web app that answers every visit with a greeting and a count of visits so far. kind is the practice Kubernetes cluster on your laptop. Gradle is the build tool for Kotlin, and CI is the automatic build and checks on every change.

Three rules keep it manageable:
1. Go in order. Each stage depends on the ones before it.
2. A stage is done when its acceptance check passes, not when it looks fine.
3. Commit after each stage, so you can always go back to the last green point.

Expect several sittings, perhaps a week or two at 45 minutes a day. Nothing in it is new material, so all of that time goes into practice. So what exactly is on the keeper's clipboard?"""

S[1]["h"] = "The checklist: 14 stages, each with a check"
S[1]["body"] = """Each line is one stage, the part it comes from, and the acceptance check that proves it. Every tool was taught in the part named next to it, and the short notes after the list remind you what each one does:
1. Foundations (Parts 0 to 3): `pytest -q` and `ruff check .` pass, and you can explain every line of `curl -v localhost:8000/healthz`.
2. Containers (Part 5): `docker compose up` counts visits through Redis, and the image runs as user 10001.
3. CI (Part 6): a pull request runs `ci.yml`, a red check blocks the merge, and tag `v1.2.0` pushes an image to GHCR.
4. JVM build (Part 7): in hello-jvm, `./gradlew build` passes from a clean clone, its CI is green, and its image answers `/healthz`.
5. Infrastructure (Part 8): right after `terraform apply` in `infra/local`, `terraform plan` reports no changes.
6. Kubernetes (Part 10): the hello-devops rollout completes on kind, and `curl localhost:8081` shows visits counting up.
7. GitOps (Part 11): a merged change reaches the cluster with no kubectl, Argo CD shows Synced and Healthy, and `git revert` rolls back.
8. Metrics (Part 12): Prometheus returns a value for `sum(rate(hello_requests_total[5m]))`, and one of your Day 52 alerts fires when you break something.
9. Dashboards (Part 13): your RED dashboard, provisioned from files, shows a burst of traffic within a minute.
10. Logs (Part 14): Kibana finds hello-devops log lines from the last five minutes.
11. Traces (Part 14): Jaeger shows a trace for hello-devops, and you can name its slowest span.
12. Dynatrace (Part 16, optional): during a trial, Dynatrace shows the hello-devops service from kind, and a DQL query returns its logs.
13. Security (Part 17): `security/verify-release.sh` passes for 1.2.0, gitleaks finds nothing, and Kyverno rejects `:latest`.
14. AI and platform (Parts 18 and 19): the Day 66 agent kubeconfig can read but not delete. Every workload has a team label, and you can print CPU per team.

The short notes. pytest runs the tests and ruff checks the code's style. Redis is the small database that keeps the count, and GHCR is GitHub's store for images. Terraform builds infrastructure from files, and Argo CD applies what is in git to the cluster. Prometheus stores metrics, and a RED dashboard shows rate, errors and duration. Kibana searches logs, Jaeger shows traces, and a span is one timed step inside a trace. Kyverno checks every object against your rules.

Stage 12 is optional because the Dynatrace trial is time-limited. Do it last, so the trial clock starts when everything else already works.

Git and Python have no stage of their own because every stage uses them. AWS, Ansible and a service mesh are optional extras here, since the capstone runs on kind. If you want them, add one stage for each:
- AWS (Days 13 and 14): hello-devops answers on an EC2 instance, and your cleanup script removes it.
- Ansible (Part 9): the second run of your playbook reports no changes.
- Service mesh (Part 15): you can measure a canary split through Envoy or a mesh.

A list of stages is only as good as its checks, so next we look at what makes a check worth trusting."""

S[2]["h"] = "Acceptance checks you can run"
S[2]["body"] = """"The dashboard looks fine" is not a check. A good acceptance check has three properties:
- It is observable: it looks at the running system, not at your memory of setting it up.
- It is binary: anyone who runs it gets PASS or FAIL, with no judgment call.
- It is runnable: one command, so you can repeat it after every change.

Compare two versions of stage 7. The weak one says "Argo CD works". The strong one says that after a merge, with no kubectl, `kubectl -n argocd get application hello-devops` reports Synced and Healthy. The weak version cannot clearly fail, so passing it tells you nothing. **A check that cannot fail proves nothing. Make every check able to say FAIL.**

The lab's `security/capstone-check.sh` turns 11 of the 14 stages into such checks. Each prints PASS, FAIL or SKIP. SKIP means a tool or address is missing, for example cosign (the signing tool from Part 17) not installed. The script ends with a count and exits with 1 if anything failed, so the same file could run in CI later.

Run it after every stage, and read every line, not only the one for the stage you just finished. Adding a later stage often breaks an earlier one: a new policy that rejects Redis, or a port-forward that grabbed port 8081. An older line that turns red points you straight at the cause. You run the whole test suite for the same reason, not only the newest test.

The keeper switches on every lamp, not just the one fitted today. Checks prove the path works when things go right. Next, we find out what happens when they go wrong."""

S[3]["h"] = "Break it on purpose: a game day"
S[3]["body"] = """A game day is a planned session where you break things on purpose and watch how the system, and you, respond. It is the keeper pouring a bucket into the drain before the first storm. So far you have only seen hello-devops working, which tells you little about what happens when Redis dies.

Before each drill, write down what you expect to see. Afterwards, write down what happened. Wherever the two differ, your picture of the system was wrong, and that is what you write up.

Five drills, each testing a different part of the course:
1. Deploy an image tagged `:latest` through git. Expect Kyverno to reject it and Argo CD to show the sync error.
2. Delete one hello-devops Pod. Expect the Deployment to replace it and the dashboard to show only a blip.
3. Scale Redis to 0. Expect `/readyz` to return 503, the Pods to go unready, an alert to fire, error logs in Kibana and a failed span in Jaeger.
4. Change the Deployment by hand with `kubectl edit`. Expect Argo CD's self-heal to put git's version back.
5. Release a version that fails its readiness probe. Expect the rollout to stall, then fix it with `git revert` alone.

A Pod is one running copy of the app, and a Deployment keeps the right number of them running. A readiness probe is the regular check that tells Kubernetes a Pod may receive traffic.

If you only have time for one, do drill 3. A single fault shows up in metrics, logs and traces at once, which is why you built all three.

For each drill, write a short runbook: how you noticed, what you checked, what fixed it. Then write one blameless postmortem (Day 49) for the drill that surprised you most. A postmortem is a write-up of what went wrong, and blameless means it looks for causes, not culprits. Interviewers like these, because they show how you think when something is broken. Your notes are now worth sharing, which brings us to presenting the work."""

S[4]["h"] = "Present it like an engineer"
S[4]["body"] = """Your repository is now your portfolio, so give it a README that an engineer can read in five minutes. A README is the front page of a repository, the file GitHub shows first. Yours needs six parts:
1. What it is, in two sentences.
2. An architecture diagram, like the one in this lesson.
3. How to run it: one command per stage, in order.
4. What the pipeline proves: tests, a scan, an SBOM, a keyless signature and SLSA Build L2 provenance (Part 17).
5. Two or three decisions with their trade-offs, for example Kyverno over Gatekeeper, or kind over a cloud cluster.
6. What you would do next with more time.

Spend the most time on point 5. Write each decision as a short architecture decision record (ADR): the situation, the options, what you chose and what it costs. Anyone can follow a tutorial to install a tool. Your reasons for choosing it, and what you gave up, are what show judgment.

Then record a five-minute demo. Make a one-line change, open a pull request, merge it, and show the new version in `curl`, on the dashboard, in Kibana and in a trace. Five minutes is enough to show the whole loop and short enough that people watch it.

For interviews, turn your game day into stories. Describe what broke, what you saw first, what you checked and what fixed it. A story about a Redis outage in your own cluster tells an interviewer more than a list of 20 tools on a CV. Many job filters also look for a certificate, so that is the next thing to plan."""

S[5]["h"] = "Certifications: what they test"
S[5]["body"] = """A certification gives your learning a shape and a deadline, and some job filters look for one. Your capstone shows what you can actually do. You want both, and the capstone is good exam practice.

The CNCF, the foundation behind Kubernetes and many tools in this course, publishes the official curriculum for each of its exams on [GitHub](https://github.com/cncf/curriculum). Each curriculum lists the exam's domains (topic areas) and how much each one counts:
- KCNA (Kubernetes and Cloud Native Associate): the beginner-friendly one. Kubernetes fundamentals 44%, orchestration 28%, app delivery 16%, architecture 12%.
- CKAD (Certified Kubernetes Application Developer): app design and build, deployment, observability, config and security, networking. The best fit for a developer.
- CKA (Certified Kubernetes Administrator): troubleshooting is the biggest domain at 30%, which is Day 46 and your game day.
- CKS (Certified Kubernetes Security Specialist): supply chain security is 20%, which is Part 17. You need a passed CKA to take it.
- Newer associate exams (the final A means Associate) match later parts: PCA (Prometheus), OTCA (OpenTelemetry), ICA (Istio), CBA (Backstage), KCA (Kyverno), CNPA (platform engineering).

The CKA and CKAD curricula follow Kubernetes v1.37 now. Third-party guides, not the Linux Foundation pages, describe KCNA as multiple choice and CKA, CKAD and CKS as hands-on tasks in a terminal. Check formats and prices on the Linux Foundation's exam pages before you book, and look out for discounts, which are frequent.

Two other vendors publish their facts openly. HashiCorp's [Terraform Associate (004)](https://developer.hashicorp.com/certifications/terraform-associate) is multiple choice, one hour, online proctored (watched by an examiner over your webcam), US$70.50 plus local taxes, and valid for two years. GitHub offers certifications for Foundations, Actions, Advanced Security, Administration and Copilot. AWS and Red Hat (whose RHCE exam is built on Ansible) run their own programs, so check their pages for the current list. An exam is one milestone. The months around it matter more."""

S[6]["h"] = "Your next three months"
S[6]["body"] = """At 30 to 45 minutes a day, this is the plan I would follow:
1. Weeks 1 to 4, Kubernetes depth. Work through the CKAD curriculum on your kind cluster, one domain a week. Redo the Day 46 break-and-fix lab without notes. Book the exam if a date helps you.
2. Weeks 5 to 8, one real cloud. Start from your Day 13 account and deploy hello-devops to one managed Kubernetes service with Terraform (Part 8), OIDC from GitHub Actions, and a budget alert. Destroy it at the end of every session.
3. Weeks 9 to 12, one specialty. Choose observability (SLOs, PCA or OTCA), platform engineering (a Backstage template, CNPA) or security (KCSA, the Kubernetes and Cloud Native Security Associate, then CKS after CKA).

A managed Kubernetes service is a cluster that a cloud company runs for you. OIDC lets GitHub Actions log in to the cloud without a stored password (Day 27).

Every week, whatever the stage:
- Read one chapter of [Google's SRE book](https://sre.google/sre-book/table-of-contents/), free online.
- Ship one small change to a real project, your capstone or a work repository.
- Write down one thing you learned, in your own words. That note is the cheapest retrieval practice there is.

If you already work in software, look for places where this course meets your day job, for example:
- A Gradle build cache in CI.
- A signed JVM image.
- A team label on a service.
- An alert on an SLO.

Ship one of those for your team before you install another tool on your laptop. One limit is worth saying out loud: the capstone runs on kind, so real traffic, a real cloud bill and a night on call are still ahead of you. That is exactly what the next three months are for."""

L["aside"] = {
    "title": "Why not build all 14 stages, then test once at the end?",
    "body": ("Because you would end up with five broken things at once, and no way to tell which one causes the others. "
             "A missing Pod makes Prometheus look empty, which makes the dashboard look broken, which hides the real fault two stages back. "
             "Finish one stage, make its check pass, commit, and only then start the next. "
             "Each green stage is solid ground for the one after it."),
    "after": 1,
}

for k in ("analogy", "mistake", "real_world"):
    L.pop(k, None)

L["diagram_caption"] = "Every part of the course on one path, and the tools that watch it."

W = L["worked"]["steps"]
W[0]["say"] = "Take stage 2: the image reports its version and runs as non-root (not as the all-powerful admin user). Start the container from the 1.2.0 image and ask it."
W[1]["say"] = ("Check the user without trusting your memory of the Dockerfile. "
               "`--entrypoint id` replaces gunicorn, the program that normally runs the app, with the `id` command, inside the same image.")
W[2]["say"] = ("Look ahead to stage 8 while you are here. This is the counter Prometheus will scrape (collect), "
               "so if it is missing now, no dashboard can fix it later.")
W[3]["say"] = "Now make one of these binary. This `if` prints PASS or FAIL, and it is the pattern every line of `capstone-check.sh` follows."
W[4]["say"] = ("Run the whole script at this early point, with the app address set to the container. "
               "Almost everything fails, which is normal this early. Read the output as your to-do list, in order.")
W[5]["say"] = ("That run is trimmed to six of the eleven lines. Four of the other five fail because kind is not running yet, and one more skips. "
               "Work down the list, run the script after each stage, and commit whenever a line turns green. Stop the container with `docker rm -f capstone`.")

T = L["task"]
T["steps"] = [
    "Copy the 14-stage checklist into a `CAPSTONE.md` in your repository, one line per stage, each with its acceptance check.",
    "Work through stages 1 to 7 in order. Run `security/capstone-check.sh` after each stage, and commit when its lines pass.",
    "Add stages 8 to 11. Start the port-forwards or Compose stacks so the endpoints answer on ports 9090, 3000, 9200 and 16686.",
    "Do stages 13 and 14. Leave stage 12, Dynatrace, for last, or skip it.",
    "Run a game day with at least three of the five drills. Write what you expect first, then what happened, then a runbook for each.",
    "Write the README: what it is, a diagram, how to run it, what the pipeline proves, two decisions with trade-offs, and what comes next.",
    "Record a five-minute demo: a one-line change goes from pull request to production, and you show it in curl, on the dashboard, in Kibana and in a trace.",
]
T["hints"] = [
    "Fix stages in order. One red early stage often explains several red later ones.",
    "If a check fails because of an address, override it with an environment variable, for example `PROM_URL=http://localhost:9091`.",
    "A laptop has limits. Run the observability tools either in Compose or in the cluster, not both at once.",
]
T["done_when"] = "`security/capstone-check.sh` ends with `0 failed`, your README explains the system, and your demo shows one change from commit to dashboard."

L["explain_back"]["answer"] = ("A pull request runs CI, which lints and tests the code and must be green before merge. A version tag then runs the release workflow. "
                               "The release scans the image, pushes it to GHCR, writes an SBOM and signs it, and I verify that with `verify-release.sh`. "
                               "A commit that changes the image tag in git tells Argo CD what to run. "
                               "I know the deploy worked when Argo CD shows Synced and Healthy and the rollout completes. "
                               "Then Prometheus and Grafana show traffic and errors, Kibana shows the logs and Jaeger shows traces, so I can see that users actually get the new version.")

L["recap"] = [
    "The capstone sends one change through every part of the course, with hello-devops and hello-jvm.",
    "A stage is done when its runnable, binary acceptance check passes, not when it looks fine.",
    "capstone-check.sh runs 11 checks. Run it again after every stage, because new stages break old ones.",
    "A game day with written expectations turns broken things into runbooks and interview stories.",
    "Present with a README, a diagram, decisions with trade-offs and a five-minute demo.",
    "Limits: the capstone runs on kind, so real traffic, cost and on-call are still ahead. Pick certifications from the official curricula and keep shipping.",
]

C = L["check"]
C[0]["why"] = "Stages depend on earlier ones. If the app is not deployed, Prometheus has nothing to scrape."
C[1]["why"] = "It looks at the running system, gives pass or fail, and tests the actual promise of GitOps."
C[2]["why"] = "The CKAD curriculum is built around application design, deployment, configuration and observability."

I = L["interview"]
I[0]["a"] = ("I built a small Python service and a Kotlin service and took them end to end. "
             "Pull requests run CI, and a tag builds a multi-arch image that is scanned, signed with cosign and attested. Argo CD deploys it to Kubernetes from git. "
             "Prometheus, Grafana, an EFK stack and Jaeger observe it, and Kyverno and RBAC guard the cluster. "
             "Every stage has an acceptance check in one script, and I ran game days, for example taking Redis down and following the failure through metrics, logs and traces.")
I[1]["a"] = ("I check in layers. First the rollout completes and the readiness probes pass, and in GitOps Argo CD shows Synced and Healthy. "
             "Then a smoke test calls the service and checks the version it reports. "
             "Then the user-facing signals: error rate and latency against the SLO in Prometheus and Grafana, plus logs and traces for anything odd. "
             "If those move the wrong way, I roll back with git revert before I start debugging.")
I[2]["a"] = ("I would start with the CKAD, because I come from application development and its curriculum is about designing, deploying and configuring apps on Kubernetes. "
             "Then the CKA, because troubleshooting is its biggest domain at 30%, and that is the skill that matters most on call. "
             "I would check the format and price on the Linux Foundation's page before booking. "
             "In parallel I would keep the capstone running, because the exam and the project practise the same skills.")

L["deeper"]["body"] = """The hardest capstone test worth trying is to delete the cluster and rebuild it from git.

Everything you deploy now lives in files: the kind config, Helm values, Kyverno policies, the Argo CD Application, the ExternalSecret. In theory that means `kind delete cluster` loses nothing that matters. In practice, most first attempts fail, because some step only ever happened by hand. Maybe you installed Kyverno from your shell history, or labelled the namespace with `kubectl label` and never wrote it down. Every one of those steps is a gap in your disaster recovery, your plan for getting back after losing everything.

Try it like this:
1. Write a `bootstrap.sh` that creates the kind cluster, installs Argo CD, and applies one Argo CD Application.
2. Let Argo CD install everything else from git: Kyverno, External Secrets Operator, kube-prometheus-stack, Fluent Bit and the app. The [app-of-apps pattern](https://argo-cd.readthedocs.io/en/stable/operator-manual/cluster-bootstrapping/) from Day 48 is made for this.
3. Time it: run `kind delete cluster --name devops`, start a stopwatch, run the bootstrap script, and stop when `security/capstone-check.sh` shows 0 failed.
4. Every time the rebuild needs a manual step, move that step into git and run the test again.

Two things usually go wrong. Order matters: Kyverno's policies need Kyverno's CRDs first, and the app needs its namespace labels before Pod Security can judge it. Argo CD sync waves (Day 48) solve this, by giving each Application a number and syncing low numbers first. And state outside git does not come back: the Redis counter, Prometheus history and Elasticsearch logs are gone. That is fine for a lab, and it is the reason real teams keep data in managed services or back it up separately.

When the rebuild is one command and the check is green, write the time in your README. In an interview, "the whole platform rebuilds from git in N minutes" covers GitOps, infrastructure as code and disaster recovery in one sentence."""

L["closing"] = """We started with a park keeper walking the new path at dusk, clipboard in hand, the night before it opened. Your capstone is that walk: one change from your laptop to users, with a lamp to switch on at every stage and a bucket of water for every drain.

Run `security/capstone-check.sh` now, even if most lines say FAIL. That list is your route for the next two weeks.

This is the last lesson, so the next step is yours. Next, you'll pick one of the three months above and start it this week. Which part of the path do you want to walk again, more slowly?"""

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
print("d68 written")
