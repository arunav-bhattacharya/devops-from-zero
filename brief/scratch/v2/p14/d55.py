"""Day 55: Your capstone, and what to learn next (Part 14)."""
import pathlib

from svg import arrow, box, note, svg

LAB = pathlib.Path("/home/user/devops-from-zero/labs/hello-devops")


def lab(path):
    return (LAB / path).read_text().rstrip("\n")


def diagram():
    p = [note(280, 18, "one change, end to end")]
    # Top row: from the laptop to the cluster.
    top = [(8, 88, "bx", "git push"), (124, 96, "bxt", "CI, Gradle"), (248, 88, "bxo", "Release"), (364, 80, "bxg", "GHCR"), (472, 80, "bxo", "Argo CD")]
    for i, (x, w, c, t) in enumerate(top):
        p.append(box(x, 32, w, 44, c, t))
        if i < len(top) - 1:
            nx = top[i + 1][0]
            p.append(arrow(x + w + 2, 54, nx - 4, 54))
    p.append(note(292, 94, "test, scan, sign"))
    # Argo CD applies to kind.
    p.append(arrow(512, 78, 512, 116))
    p.append(note(470, 100, "applies", anchor="end"))
    # Middle: the cluster with its guards.
    p.append(box(408, 120, 144, 44, "bxp", "kind cluster"))
    p.append(box(232, 120, 160, 44, "bxg", "Kyverno, RBAC"))
    p.append(arrow(394, 142, 404, 142, head=False))
    # Bottom row: what watches it.
    bottom = [(8, 120, "bxt", "Prometheus"), (144, 88, "bxt", "Grafana"), (248, 64, "bxt", "EFK"), (328, 80, "bxt", "Jaeger"), (424, 128, "bx", "Dynatrace")]
    for x, w, c, t in bottom:
        p.append(box(x, 232, w, 44, c, t))
    p.append(arrow(480, 166, 480, 198, dashed=True, head=False))
    p.append(arrow(480, 198, 68, 198, dashed=True, head=False))
    for x, w, _, _ in bottom:
        p.append(arrow(x + w / 2, 198, x + w / 2, 228, dashed=True))
    p.append(note(280, 300, "metrics, dashboards, logs, traces (Dynatrace optional)"))
    return svg(316, "The capstone flow: git push, CI and Gradle, release with scan and sign, GHCR, Argo CD applies to a kind cluster guarded by Kyverno and RBAC; "
               "Prometheus, Grafana, EFK, Jaeger and optionally Dynatrace watch it.", p)


SECTIONS = [
    {
        "h": "What the capstone is, and why it works",
        "body": (
            "A capstone is one final project that uses every part of a course together. Yours has a simple story: "
            "one small code change travels from your laptop to users, and at every step you can prove it got there.\n\n"
            "Why bother, when each lesson already had a task? Because using knowledge again, later and in a new mix, is how it sticks. "
            "Each part taught one tool in a clean room. The capstone puts them in the same room, where they interfere with each other the way they do at work. "
            "A Kyverno policy blocks your Argo CD sync. A port-forward you forgot makes Prometheus look empty. "
            "Those surprises are the real lessons.\n\n"
            "You work with both lab apps:\n"
            "- hello-devops, the Python app you have shipped since Day 2, through the full pipeline to kind.\n"
            "- hello-jvm, the Kotlin build from Part 5, built and tested by Gradle in its own CI.\n\n"
            "Three rules keep it manageable:\n"
            "1. Go in order. Each stage depends on the ones before it.\n"
            "2. A stage is done when its acceptance check passes, not when it looks fine.\n"
            "3. Commit after each stage, so you can always go back to the last green point.\n\n"
            "Expect it to take several sittings, perhaps a week or two of your usual 45 minutes a day. That is fine. "
            "Nothing in it is new; all of it is practice."
        ),
        "refs": [
            {"title": "Complete DevOps roadmap: master these 4 levels (TechWorld with Nana)", "url": "https://www.youtube.com/watch?v=1J2YOV6LcwY", "kind": "watch"},
            {"title": "Google SRE book: table of contents", "url": "https://sre.google/sre-book/table-of-contents/", "kind": "read"},
        ],
    },
    {
        "h": "The checklist: 14 stages, each with a check",
        "body": (
            "Each line is one stage, the part it comes from, and the acceptance check that proves it:\n"
            "1. Foundations (Parts 0 to 2): `pytest -q` and `ruff check .` pass, and you can explain every line of `curl -v localhost:8000/healthz`.\n"
            "2. Containers (Part 3): `docker compose up` counts visits through Redis, and the image runs as user 10001.\n"
            "3. CI (Part 4): a pull request runs `ci.yml`, a red check blocks the merge, and tag `v1.2.0` pushes an image to GHCR.\n"
            "4. JVM build (Part 5): in hello-jvm, `./gradlew build` passes from a clean clone, its CI is green, and its image answers `/healthz`.\n"
            "5. Infrastructure (Part 6): right after `terraform apply` in `infra/local`, `terraform plan` reports no changes.\n"
            "6. Kubernetes (Part 7): the hello-devops rollout completes on kind, and `curl localhost:8081` shows visits counting up.\n"
            "7. GitOps (Part 8): a merged change reaches the cluster with no kubectl, Argo CD shows Synced and Healthy, and `git revert` rolls back.\n"
            "8. Metrics (Part 9): Prometheus returns a value for `sum(rate(hello_requests_total[5m]))`, and one of your Day 44 alerts fires when you break something.\n"
            "9. Dashboards (Part 10): your RED dashboard, provisioned from files, shows a burst of traffic within a minute.\n"
            "10. Logs (Part 11): Kibana finds hello-devops log lines from the last five minutes.\n"
            "11. Traces (Part 11): Jaeger shows a trace for hello-devops, and you can name its slowest span.\n"
            "12. Dynatrace (Part 12, optional): during a trial, Dynatrace shows the hello-devops service from kind, and a DQL query returns its logs.\n"
            "13. Security (Part 13): `security/verify-release.sh` passes for 1.2.0, gitleaks finds nothing, and Kyverno rejects `:latest`.\n"
            "14. Platform and AI (Part 14): every workload has a team label, you can print CPU per team, and the agent kubeconfig can read but not delete.\n\n"
            "Stage 12 is optional because the Dynatrace trial is time-limited. Do it last, so the trial clock starts when everything else already works."
        ),
        "refs": [
            {"title": "Argo CD docs: getting started", "url": "https://argo-cd.readthedocs.io/en/stable/getting_started/", "kind": "docs"},
            {"title": "Prometheus docs: querying basics", "url": "https://prometheus.io/docs/prometheus/latest/querying/basics/", "kind": "docs"},
        ],
    },
    {
        "h": "Acceptance checks you can run",
        "body": (
            "\"The dashboard looks fine\" is not a check. A good acceptance check has three properties:\n"
            "- It is observable: it looks at the running system, not at your memory of setting it up.\n"
            "- It is binary: anyone who runs it gets PASS or FAIL, with no judgment call.\n"
            "- It is runnable: one command, so you can repeat it after every change.\n\n"
            "Compare two versions of stage 7. Weak: \"Argo CD works.\" Strong: \"After a merge, with no kubectl, "
            "`kubectl -n argocd get application hello-devops` reports Synced and Healthy.\" The second one can fail, and that is what makes it useful.\n\n"
            "The lab's `security/capstone-check.sh` turns 11 of the 14 stages into such checks. Each prints PASS, FAIL or SKIP. "
            "SKIP means a tool or address is missing, for example cosign not installed. "
            "The script ends with a count and exits with 1 if anything failed, so the same file could run in CI later.\n\n"
            "Run it after every stage, not only after the one you just did. Adding a later stage often breaks an earlier one: "
            "a new policy that rejects Redis, or a port-forward that grabbed port 8081. "
            "An older line that turns red tells you exactly where to look, which is the same idea as running the whole test suite and not only the newest test."
        ),
        "refs": [
            {"title": "Kubernetes docs: kubectl rollout status", "url": "https://kubernetes.io/docs/reference/kubectl/generated/kubectl_rollout/kubectl_rollout_status/", "kind": "docs"},
        ],
    },
    {
        "h": "Break it on purpose: a game day",
        "body": (
            "A system you have only seen working is a system you do not understand yet. A game day is a planned session where you break things on purpose "
            "and watch how the system, and you, respond. Before each drill, write down what you expect to see. Afterwards, write down what happened. "
            "The gap between the two is what you learn.\n\n"
            "Five drills, each testing a different part of the course:\n"
            "1. Deploy an image tagged `:latest` through git. Expect Kyverno to reject it and Argo CD to show the sync error.\n"
            "2. Delete one hello-devops Pod. Expect the Deployment to replace it and the dashboard to show only a blip.\n"
            "3. Scale Redis to 0. Expect `/readyz` to return 503, the Pods to go unready, an alert to fire, error logs in Kibana and a failed span in Jaeger.\n"
            "4. Change the Deployment by hand with `kubectl edit`. Expect Argo CD's self-heal to put git's version back.\n"
            "5. Release a version that fails its readiness probe. Expect the rollout to stall, then fix it with `git revert` alone.\n\n"
            "Drill 3 is the best one. A single fault shows up in metrics, logs and traces at once, which is exactly why you built all three.\n\n"
            "For each drill, write a short runbook: how you noticed, what you checked, what fixed it. "
            "Then write one blameless postmortem (Day 41) for the drill that surprised you most. "
            "Interviewers love these, because they show how you think when something is broken."
        ),
        "refs": [
            {"title": "Google SRE book: postmortem culture", "url": "https://sre.google/sre-book/postmortem-culture/", "kind": "read"},
            {"title": "Argo CD docs: automated sync and self-heal", "url": "https://argo-cd.readthedocs.io/en/stable/user-guide/auto_sync/", "kind": "docs"},
        ],
    },
    {
        "h": "Present it like an engineer",
        "body": (
            "Your repository is now your portfolio, so give it a README that an engineer can read in five minutes:\n"
            "1. What it is, in two sentences.\n"
            "2. An architecture diagram, like the one in this lesson.\n"
            "3. How to run it: one command per stage, in order.\n"
            "4. What the pipeline proves: tests, a scan, an SBOM, a keyless signature and SLSA Build L2 provenance.\n"
            "5. Two or three decisions with their trade-offs, for example Kyverno over Gatekeeper, or kind over a cloud cluster.\n"
            "6. What you would do next with more time.\n\n"
            "Point 5 matters most. Write each decision as a short architecture decision record (ADR): the situation, the options, what you chose and what it costs. "
            "Anyone can install a tool by following a tutorial. Explaining why you chose it, and what you gave up, shows judgment.\n\n"
            "Then record a five-minute demo. Make a one-line change, open a pull request, merge it, and show the new version in `curl`, "
            "on the dashboard, in Kibana and in a trace. Five minutes is enough to show the whole loop and short enough that people watch it.\n\n"
            "For interviews, turn your game day into stories. Describe what broke, what you saw first, what you checked and what fixed it. "
            "A concrete story about a Redis outage in your own cluster beats a list of 20 tools on a CV."
        ),
        "refs": [
            {"title": "GitHub Docs: about READMEs", "url": "https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-readmes", "kind": "docs"},
        ],
    },
    {
        "h": "Certifications: what they test",
        "body": (
            "A certification gives your learning a shape and a deadline, and some job filters look for one. Your capstone shows what you can actually do. "
            "You want both, and the capstone is good exam practice.\n\n"
            "The CNCF publishes the official curriculum for each of its exams on [GitHub](https://github.com/cncf/curriculum), with the weight of each domain:\n"
            "- KCNA (Kubernetes and Cloud Native Associate): the beginner-friendly one. Kubernetes fundamentals 44%, orchestration 28%, app delivery 16%, architecture 12%.\n"
            "- CKAD (Application Developer): app design and build, deployment, observability, config and security, networking. The best fit for a developer.\n"
            "- CKA (Administrator): troubleshooting is the biggest domain at 30%, which is Day 38 and your game day.\n"
            "- CKS (Security Specialist): supply chain security is 20%, which is Part 13.\n"
            "- Newer exams match later parts: PCA (Prometheus), OTCA (OpenTelemetry), CBA (Backstage), KCA (Kyverno), CNPA (platform engineering).\n\n"
            "The CKA and CKAD curricula follow Kubernetes v1.37 now. "
            "Third-party guides, not the Linux Foundation pages, describe KCNA as multiple choice and CKA, CKAD and CKS as hands-on tasks in a terminal. "
            "Check formats and prices on the Linux Foundation's exam pages before you book; discounts are frequent.\n\n"
            "Two other vendors publish their facts openly. HashiCorp's Terraform Associate (004) is multiple choice, one hour, online proctored, "
            "US$70.50 plus local taxes, and valid for two years. "
            "GitHub offers certifications for Foundations, Actions, Advanced Security, Administration and Copilot."
        ),
        "refs": [
            {"title": "CNCF curriculum for all CNCF exams", "url": "https://github.com/cncf/curriculum", "kind": "docs"},
            {"title": "HashiCorp: Terraform Associate certification", "url": "https://developer.hashicorp.com/certifications/terraform-associate", "kind": "docs"},
            {"title": "CNCF Kubernetes and Cloud Native Associate course, KCNA (freeCodeCamp)", "url": "https://www.youtube.com/watch?v=AplluksKvzI", "kind": "watch"},
        ],
    },
    {
        "h": "Your next three months",
        "body": (
            "Here is the plan I would follow, at your current pace of 30 to 45 minutes a day:\n"
            "1. Weeks 1 to 4, Kubernetes depth. Work through the CKAD curriculum on your kind cluster, one domain a week. Redo the Day 38 break-and-fix lab without notes. Book the exam if a date helps you.\n"
            "2. Weeks 5 to 8, one real cloud. Deploy hello-devops to one managed Kubernetes service with Terraform (Part 6), OIDC from GitHub Actions, and a budget alert. Destroy it at the end of every session.\n"
            "3. Weeks 9 to 12, one specialty. Choose observability (SLOs, PCA or OTCA), platform engineering (a Backstage template, CNPA) or security (KCSA, then CKS after CKA).\n\n"
            "Every week, whatever the stage:\n"
            "- Read one chapter of [Google's SRE book](https://sre.google/sre-book/table-of-contents/), free online.\n"
            "- Ship one small change to a real project, your capstone or a work repository.\n"
            "- Write down one thing you learned, in your own words. That note is the cheapest retrieval practice there is.\n\n"
            "At work, look for the place where this course meets your Kotlin and Gradle day job. "
            "A Gradle build cache in CI, a signed JVM image, a team label on a service, or an alert on an SLO. "
            "One improvement your team uses is worth more than three new tools on your laptop."
        ),
        "refs": [
            {"title": "CKAD curriculum (CNCF)", "url": "https://github.com/cncf/curriculum/blob/master/ckad/README.md", "kind": "docs"},
            {"title": "GitHub Docs: about GitHub Certifications", "url": "https://docs.github.com/en/get-started/showcase-your-expertise-with-github-certifications/about-github-certifications", "kind": "docs"},
        ],
    },
]

WORKED = {
    "title": "From a checklist line to a check you can run",
    "steps": [
        {
            "say": "Take stage 2: the image reports its version and runs as non-root. Start the container from the 1.2.0 image and ask it.",
            "code": (
                "$ docker run -d --name capstone -p 8000:8000 hello-devops:1.2.0\n"
                "$ curl -s localhost:8000/ | jq\n"
                "{\n"
                "  \"host\": \"738841dd8ef1\",\n"
                "  \"message\": \"Hello, DevOps!\",\n"
                "  \"version\": \"1.2.0\",\n"
                "  \"visits\": 1\n"
                "}"
            ),
            "lang": "console",
        },
        {
            "say": "Check the user without trusting your memory of the Dockerfile. `--entrypoint id` replaces gunicorn with the `id` command, inside the same image.",
            "code": "$ docker run --rm --entrypoint id hello-devops:1.2.0 -u\n10001",
            "lang": "console",
        },
        {
            "say": "Look ahead to stage 8 while you are here. This is the counter Prometheus will scrape, so if it is missing now, no dashboard can fix it later.",
            "code": "$ curl -s localhost:8000/metrics | grep '^hello_requests_total'\nhello_requests_total{path=\"/\"} 2.0",
            "lang": "console",
        },
        {
            "say": "Now make one of these binary. This `if` prints PASS or FAIL, and it is the pattern every line of `capstone-check.sh` follows.",
            "code": (
                "$ got=$(curl -s localhost:8000/ | jq -r .version)\n"
                "$ if [[ \"$got\" == \"1.2.0\" ]]; then echo \"PASS  app reports 1.2.0\"; else echo \"FAIL  app reports '$got'\"; fi\n"
                "PASS  app reports 1.2.0"
            ),
            "lang": "console",
        },
        {
            "say": "Run the whole script at this early point, with the app address set to the container. Almost everything fails, and that is the point: the output is your to-do list, in order.",
            "code": (
                "$ APP_URL=http://localhost:8000/ GITHUB_USER=you VERSION=1.2.0 security/capstone-check.sh\n"
                "FAIL  Deployment hello-devops is not ready (kubectl -n hello get pods)\n"
                "PASS  App at http://localhost:8000/ reports version 1.2.0\n"
                "FAIL  Argo CD Application hello-devops not found in namespace argocd\n"
                "SKIP  cosign not installed (brew install cosign)\n"
                "FAIL  Prometheus at http://localhost:9090 has no hello_requests_total (is the port-forward running?)\n"
                "FAIL  Jaeger at http://localhost:16686 has no services yet (send some requests first)\n"
                "1 passed, 8 failed, 2 skipped"
            ),
            "lang": "console",
        },
        {
            "say": "That run is trimmed to six of the eleven lines; the others fail the same way, because kind is not running yet. "
                   "Work down the list, run the script after each stage, and commit whenever a line turns green. Stop the container with `docker rm -f capstone`.",
        },
    ],
}

CODE = [
    {"lang": "bash", "title": "security/capstone-check.sh", "src": lab("security/capstone-check.sh"),
     "run": "GITHUB_USER=<your-github-user> VERSION=1.2.0 security/capstone-check.sh"},
]

COMMANDS = [
    {"cmd": "GITHUB_USER=<your-github-user> VERSION=1.2.0 security/capstone-check.sh", "what": "Run all capstone acceptance checks and print PASS, FAIL or SKIP for each."},
    {"cmd": "docker run --rm --entrypoint id hello-devops:1.2.0 -u", "what": "Print the user ID the image runs as. Expect 10001, not 0."},
    {"cmd": "curl -s localhost:8081/ | jq -r .version", "what": "Ask the app on kind which version it runs."},
    {"cmd": "kubectl -n hello rollout status deploy/hello-devops --timeout=60s", "what": "Wait until the rollout is complete, or fail after 60 seconds."},
    {"cmd": "kubectl -n argocd get application hello-devops -o jsonpath='{.status.sync.status}/{.status.health.status}'", "what": "Print Argo CD's sync and health status, for example Synced/Healthy."},
    {"cmd": "kubectl -n hello run capstone-latest --image=nginx:latest --restart=Never --dry-run=server", "what": "Send a :latest Pod through admission without creating it. Kyverno should reject it."},
    {"cmd": "curl -sG localhost:9090/api/v1/query --data-urlencode 'query=sum(hello_requests_total)' | jq -r '.data.result[0].value[1]'", "what": "Ask Prometheus for the total request count."},
    {"cmd": "curl -s localhost:16686/api/v3/services | jq -r '.services[]'", "what": "List the services Jaeger has received traces from."},
    {"cmd": "curl -s localhost:9200/_count | jq .count", "what": "Count the documents (log lines) stored in Elasticsearch."},
    {"cmd": "gh run list --repo <your-github-user>/hello-jvm --limit 1", "what": "Show the result of the last hello-jvm CI run."},
    {"cmd": "kubectl -n hello scale deploy/redis --replicas=0", "what": "Game day drill: take Redis away and watch every signal react."},
    {"cmd": "git revert HEAD && git push", "what": "Undo the last commit with a new commit; Argo CD rolls the cluster back."},
]

DEEPER = (
    "Here is the strongest capstone test I know: delete the cluster and rebuild it from git.\n\n"
    "Everything you deploy now lives in files: the kind config, Helm values, Kyverno policies, the Argo CD Application, the ExternalSecret. "
    "In theory that means `kind delete cluster` loses nothing that matters. In practice, most first attempts fail, because some step only ever happened by hand. "
    "Maybe you installed Kyverno from your shell history, or labelled the namespace with `kubectl label` and never wrote it down. "
    "Every one of those steps is a gap in your disaster recovery.\n\n"
    "Try it like this:\n"
    "1. Write a `bootstrap.sh` that creates the kind cluster, installs Argo CD, and applies one Argo CD Application.\n"
    "2. Let Argo CD install everything else from git: Kyverno, External Secrets Operator, kube-prometheus-stack, Fluent Bit and the app. "
    "The app-of-apps pattern from Day 40 is made for this.\n"
    "3. Time it: run `kind delete cluster --name devops`, start a stopwatch, run the bootstrap script, and stop when `security/capstone-check.sh` shows 0 failed.\n"
    "4. Every time the rebuild needs a manual step, move that step into git and run the test again.\n\n"
    "Two things will bite you. Order matters: Kyverno's policies need Kyverno's CRDs first, and the app needs its namespace labels before Pod Security can judge it. "
    "Argo CD sync waves (Day 40) solve this, by giving each Application a number and syncing low numbers first. "
    "And state outside git does not come back: the Redis counter, Prometheus history and Elasticsearch logs are gone. "
    "That is fine for a lab, and it is the reason real teams keep data in managed services or back it up separately.\n\n"
    "When the rebuild is one command and the check is green, write the time in your README. "
    "\"The whole platform rebuilds from git in N minutes\" is a sentence that gets attention in an interview, because it shows you understand GitOps, infrastructure as code and recovery at once."
)

lesson = {
    "id": "d55",
    "title": "Your capstone, and what to learn next",
    "minutes": 50,
    "goal": "By the end you can take hello-devops and hello-jvm through every part of the course as one capstone, prove each stage with a check, present the result, and plan your next certification and three months of learning.",
    "guess": {
        "q": "You want to show an interviewer that you can do DevOps work. Which gives the strongest evidence?",
        "options": [
            "A list of 20 tools on your CV",
            "A certificate from a multiple-choice exam",
            "A repo where a commit becomes a checked deploy",
            "A screenshot of a busy Grafana dashboard",
        ],
        "answer": 2,
        "why": "A working repository with checks shows you can connect the pieces and prove it. Certificates help with filters, but even the CKA curriculum gives troubleshooting the biggest weight, and projects teach that.",
    },
    "terms": [
        {"term": "Capstone", "plain": "One final project that uses every part of a course together, end to end."},
        {"term": "Acceptance check", "plain": "A runnable test that proves one piece of work is done, with a clear pass or fail."},
        {"term": "Game day", "plain": "A planned session where you break something on purpose and watch how the system and you respond."},
        {"term": "Runbook", "plain": "Short written steps for one known problem: how to notice it, check it and fix it."},
        {"term": "ADR", "plain": "Architecture decision record: a short note on one technical decision, the options and why you chose one."},
        {"term": "Curriculum", "plain": "The official list of an exam's domains and their weights, published by the exam's owner."},
    ],
    "sections": SECTIONS,
    "analogy": (
        "The capstone is a driving test after months of lessons in an empty car park. Each lesson taught one skill alone: steering, mirrors, parking. "
        "The test puts them on a real road at the same time, with traffic, and the examiner checks specific things, not a general feeling. "
        "Where it breaks: a driving test happens once, while your capstone check runs as often as you like, and failing it costs nothing."
    ),
    "diagram": diagram(),
    "diagram_caption": "Every part of the course on one path, and the tools that watch it.",
    "worked": WORKED,
    "code": CODE,
    "commands": COMMANDS,
    "mistake": (
        "Building all 14 stages first and testing at the end. When five things are broken at once, you cannot tell which one causes the others. "
        "Finish one stage, make its check pass, commit, and only then start the next."
    ),
    "real_world": (
        "At a payments company, a new platform engineer's first project looks a lot like this capstone: take one service from commit to production on the golden path, "
        "with every check green, and present it to the team. "
        "The team learns where the path is rough, and the new engineer learns the whole system in two weeks instead of six months."
    ),
    "task": {
        "title": "Run your capstone end to end",
        "steps": [
            "Copy the 14-stage checklist into a `CAPSTONE.md` in your repository, one line per stage, each with its acceptance check.",
            "Work through stages 1 to 7 in order. Run `security/capstone-check.sh` after each stage, and commit when its lines pass.",
            "Add stages 8 to 11. Start the port-forwards or Compose stacks so the endpoints answer on ports 9090, 3000, 9200 and 16686.",
            "Do stages 13 and 14. Leave stage 12, Dynatrace, for last, or skip it.",
            "Run a game day with at least three of the five drills. Write what you expect first, then what happened, then a runbook for each.",
            "Write the README: what it is, a diagram, how to run it, what the pipeline proves, two decisions with trade-offs, and what comes next.",
            "Record a five-minute demo: a one-line change goes from pull request to production, and you show it in curl, on the dashboard, in Kibana and in a trace.",
        ],
        "hints": [
            "Fix stages in order. One red early stage often explains several red later ones.",
            "If a check fails because of an address, override it with an environment variable, for example `PROM_URL=http://localhost:9091`.",
            "A laptop has limits. Run the observability tools either in Compose or in the cluster, not both at once.",
        ],
        "done_when": "`security/capstone-check.sh` ends with `0 failed`, your README explains the system, and your demo shows one change from commit to dashboard.",
    },
    "explain_back": {
        "prompt": "Explain in 3 to 4 sentences the path of one code change through your capstone, from git push to a user, and how you know at each step that it worked. Mention CI, the registry, Argo CD and observability.",
        "answer": (
            "A pull request runs CI, which lints and tests the code and must be green before merge; a version tag then runs the release workflow. "
            "The release scans the image, pushes it to GHCR, writes an SBOM and signs it, and I verify that with `verify-release.sh`. "
            "A commit that changes the image tag in git tells Argo CD what to run, and I know the deploy worked when Argo CD shows Synced and Healthy and the rollout completes. "
            "Then Prometheus and Grafana show traffic and errors, Kibana shows the logs and Jaeger shows traces, so I can see that users actually get the new version."
        ),
    },
    "recap": [
        "The capstone sends one change through every part of the course, with hello-devops and hello-jvm.",
        "A stage is done when its runnable, binary acceptance check passes, not when it looks fine.",
        "capstone-check.sh runs 11 checks; rerun it after every stage, because new stages break old ones.",
        "A game day with written expectations turns broken things into runbooks and interview stories.",
        "Present with a README, a diagram, decisions with trade-offs and a five-minute demo.",
        "Pick certifications from the official curricula, check prices on the owner's site, and keep shipping.",
    ],
    "check": [
        {
            "q": "Your capstone check shows FAIL for Argo CD (OutOfSync) and FAIL for Prometheus. What do you fix first?",
            "options": [
                "Prometheus, since metrics come first",
                "Argo CD, since the deploy feeds the rest",
                "Both at once, in two terminals",
                "Neither: rerun until they pass",
            ],
            "answer": 1,
            "why": "Stages depend on earlier ones: if the app is not deployed, Prometheus has nothing to scrape.",
        },
        {
            "q": "Which is the best acceptance check for stage 7, GitOps?",
            "options": [
                "Synced/Healthy after a merge, with no kubectl",
                "Argo CD is installed and looks fine",
                "The team agrees that GitOps works",
                "The Argo CD web page loads in a browser",
            ],
            "answer": 0,
            "why": "It looks at the running system, gives pass or fail, and tests the actual promise of GitOps.",
        },
        {
            "q": "You build apps at work and want a Kubernetes certification about running your own apps. Which curriculum fits best?",
            "options": [
                "KCNA: broad, beginner-friendly basics",
                "CKS: securing clusters and supply chains",
                "CKAD: designing, deploying and configuring apps",
                "CKA: running clusters, 30% troubleshooting",
            ],
            "answer": 2,
            "why": "The CKAD curriculum is built around application design, deployment, configuration and observability.",
        },
    ],
    "interview": [
        {
            "q": "Walk me through a project that shows your DevOps skills.",
            "a": (
                "I built a small Python service and a Kotlin service and took them end to end. "
                "Pull requests run CI; a tag builds a multi-arch image that is scanned, signed with cosign and attested; Argo CD deploys it to Kubernetes from git. "
                "Prometheus, Grafana, an EFK stack and Jaeger observe it, and Kyverno and RBAC guard the cluster. "
                "Every stage has an acceptance check in one script, and I ran game days, for example taking Redis down and following the failure through metrics, logs and traces."
            ),
        },
        {
            "q": "How do you know a deployment actually worked?",
            "a": (
                "I check in layers. First the rollout completes and the readiness probes pass, and in GitOps Argo CD shows Synced and Healthy. "
                "Then a smoke test calls the service and checks the version it reports. "
                "Then the user-facing signals: error rate and latency against the SLO in Prometheus and Grafana, plus logs and traces for anything odd. "
                "If those move the wrong way, I roll back with git revert before I start debugging."
            ),
        },
        {
            "q": "Which certification would you take next, and why?",
            "a": (
                "I would start with the CKAD, because I come from application development and its curriculum is about designing, deploying and configuring apps on Kubernetes. "
                "Then the CKA, because troubleshooting is its biggest domain at 30%, and that is the skill that matters most on call. "
                "I would check the format and price on the Linux Foundation's page before booking. "
                "In parallel I would keep the capstone running, because the exam and the project practise the same skills."
            ),
        },
    ],
    "deeper": {"minutes": 15, "body": DEEPER},
    "sources": [
        {"title": "CNCF curriculum for all CNCF exams", "url": "https://github.com/cncf/curriculum"},
        {"title": "HashiCorp: Terraform Associate certification", "url": "https://developer.hashicorp.com/certifications/terraform-associate"},
        {"title": "GitHub Docs: about GitHub Certifications", "url": "https://docs.github.com/en/get-started/showcase-your-expertise-with-github-certifications/about-github-certifications"},
        {"title": "Google SRE book", "url": "https://sre.google/sre-book/table-of-contents/"},
    ],
}
