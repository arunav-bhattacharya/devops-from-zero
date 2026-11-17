"""Fifth pass (book voice) for the part fields of p17, p18 and p19. Writer: ti.
Rewrites intro, recap, flashcard fronts and backs, quiz q and why, and resource why. Options and answers stay."""
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[4]


def load(n):
    return json.loads((ROOT / f"content/p{n}.json").read_text())


def save(n, P):
    (ROOT / f"content/p{n}.json").write_text(json.dumps(P, ensure_ascii=False, indent=1) + "\n")


def apply(P, intro, recap, cards, res_why, quiz):
    P["intro"] = intro
    P["recap"] = recap
    assert len(cards) == len(P["flashcards"])
    for f, (front, back) in zip(P["flashcards"], cards):
        f["front"], f["back"] = front, back
    assert len(res_why) == len(P["resources"])
    for r, w in zip(P["resources"], res_why):
        r["why"] = w
    assert len(quiz) == len(P["quiz"])
    for q, (qq, why) in zip(P["quiz"], quiz):
        q["q"], q["why"] = qq, why


# ---------- Part 17 ----------
P = load(17)
apply(P,
      intro=("Part 17 goes back over everything you have built and asks how an attacker would get in. "
             "Day 63 follows the software from other people's code to a signed image you can check, using three real attacks from 2024 to 2026. "
             "Day 64 covers what happens inside the cluster: where passwords live, who may do what, and the rules the cluster checks before it saves anything. "
             "Security comes this late because you can only protect a pipeline and a cluster you already understand."),
      recap=[
          "Your supply chain is every library, image, tool and ready-made CI step between your keyboard and production.",
          "xz-utils (2024), tj-actions (2025) and Trivy (2026) each hit a different link: a maintainer, an action's tags and a security tool.",
          "Pin actions to full commit SHAs and images to digests, and let Dependabot keep the pins fresh.",
          "An SBOM lists what you ship, and scanners match it against known holes (CVEs) at build time and again later.",
          "cosign keyless signing and GitHub attestations prove who built an image and how (SLSA Build L2).",
          "None of it helps until something checks it: cosign verify, gh attestation verify, and later a rule in the cluster.",
          "A Secret is only base64, anyone who can create Pods in its namespace can read it, and leaked values must be replaced.",
          "Real values live in a secrets manager. ESO, Sealed Secrets or SOPS bring them in without plain values in git.",
          "RBAC decides who may act. Pod Security Admission and Kyverno decide which objects are acceptable.",
      ],
      cards=[
          ("Why is a version tag like @v4 not enough to trust an action?", "A tag is a name that can be moved. Whoever controls the repository can point it at new code."),
          ("What does a full commit SHA guarantee?", "It always names the same code, because it is a fingerprint of the commit's content."),
          ("What is an SBOM?", "A list, written for computers to read, of every package and version inside an artifact."),
          ("What are the two standard SBOM formats?", "SPDX and CycloneDX."),
          ("Why scan an old SBOM again?", "New CVEs are published every day against packages you already shipped."),
          ("What makes cosign signing keyless?", "A 10-minute certificate tied to the workflow's OIDC identity, so no private key is stored."),
          ("What are Fulcio and Rekor?", "Sigstore's certificate authority, and its public log of signing events."),
          ("Which SLSA build level do GitHub artifact attestations give?", "Build L2. Building in a shared reusable workflow can reach L3."),
          ("What does provenance record?", "How an artifact was built: repository, commit, workflow and build platform."),
          ("Is a Kubernetes Secret encrypted?", "No. Its values are base64 encoded, and etcd, the cluster's database, stores them unencrypted by default."),
          ("Who can read a Secret without get on secrets?", "Anyone who can create Pods or workloads in its namespace, and anyone with list or watch on Secrets."),
          ("A token was committed, then deleted in the next commit. What now?", "Rotate it: cancel it and make a new one. Git history keeps it, in every clone and fork."),
          ("gitleaks dir or gitleaks git: which finds a deleted secret?", "gitleaks git, because it reads the whole history. dir only reads the current files."),
          ("With External Secrets Operator, which file goes in git?", "The ExternalSecret. It names a key in the secrets manager, never the value."),
          ("Why avoid * in RBAC rules?", "It also grants every resource type that is added to the cluster later."),
          ("What are the three Pod Security levels?", "privileged, baseline and restricted."),
          ("Does Pod Security enforce mode reject a bad Deployment?", "No. It accepts the Deployment and rejects its Pods. Warn mode shows the problem at apply time."),
          ("Kyverno: Audit or Deny, which one blocks the request?", "Deny. Audit allows it and records a failure in a PolicyReport."),
          ("Which Kyverno type replaces ClusterPolicy for validation?", "ValidatingPolicy (policies.kyverno.io/v1), with checks written in CEL."),
      ],
      res_why=[
          "The attacked company's own timeline, with when you were exposed, which versions are safe and what to replace.",
          "A calm walk through how a trusted contributor hid a backdoor in a library that almost every Linux system has.",
          "GitHub's own rules for ready-made actions: SHA pins, lockfiles, and checking that a SHA is not from a fork.",
          "What each build level promises and which attacks it stops, in the spec's own words.",
          "Keyless signing and checking in a few commands, plus the warnings about digests and public logs.",
          "How Sigstore grew from one signing tool into the base of GitHub's artifact attestations.",
          "The official list of rights that are more powerful than they look, such as creating Pods.",
          "A visual tour of image scanning, RBAC, network policies and secrets on Kubernetes.",
          "Install Kyverno and write a first CEL ValidatingPolicy, in the current 1.19 style.",
          "The maintainers explain Rego and Gatekeeper, the main alternative to Kyverno.",
          "How SecretStores and ExternalSecrets fit together, and how to install the operator with Helm.",
      ],
      quiz=[
          ("Which step in the lab's release.yml stops a release whose image has a HIGH CVE with a fix available?",
           "The Trivy step runs with severity HIGH and CRITICAL, ignore-unfixed and exit code 1, before anything is pushed."),
          ("Your image passed the scan with zero findings on release day. Two months later, what tells you whether it is still safe?",
           "New CVEs appear after release, so you match the stored SBOM against today's list of known holes."),
          ("You run cosign verify with the identity of release.yml at tag v1.2.0, but the image was signed by the run for v1.2.1. What happens?",
           "The certificate's identity includes the tag, so a signature from another tag does not match."),
          ("Which statement about GitHub artifact attestations is true?",
           "They are keyless Sigstore attestations at Build L2, and GitHub says they add nothing until someone verifies them."),
          ("A developer may create Pods in namespace billing but has no rule for Secrets. Can they learn the database password stored there?",
           "A Pod they create can load any Secret in the namespace, so the right to create Pods includes reading Secrets."),
          ("Which of these files is safe to commit to a public repository?",
           "An ExternalSecret only points at a key in the secrets manager. The value never enters git."),
          ("You want to stop :latest images in namespace hello, but only after teams fix their files. How do you start?",
           "Audit records failures in PolicyReports without blocking, so teams can fix things before you switch to Deny."),
          ("Kyverno is installed. Which question can it answer that RBAC cannot?",
           "RBAC checks who may do which action on which kind of object. Admission policies look inside the object itself."),
          ("In GitHub Actions, why does the release job declare its own permissions: block?",
           "Least privilege: the default stays read-only, and only this job may push packages, ask for OIDC tokens and write attestations."),
          ("A Deployment's Pods are refused by Pod Security, so none start. Which command shows the reason fastest?",
           "No Pod exists to have logs. The ReplicaSet's FailedCreate event carries the Pod Security message."),
      ])
save(17, P)

# ---------- Part 18 ----------
P = load(18)
apply(P,
      intro=("Part 18 covers the AI tools you will meet at work, and be asked about in interviews. "
             "Day 65 uses AI assistants and coding agents to draft YAML, Terraform and scripts. "
             "It builds the habit that makes this safe: every answer passes a check you trust before it reaches the main branch. "
             "Day 66 gives agents real tools, through MCP and in CI, and fences them in with the least privilege from Part 17. "
             "It comes after security on purpose, because an agent is one more identity to lock down."),
      recap=[
          "Language models predict likely text: good at common shapes, unreliable on exact flags, fields, versions and packages.",
          "The verify loop: draft, check with a tool you trust, feed the errors back, review the diff, then merge.",
          "kubeconform -strict, a server dry run, terraform validate and plan, actionlint, shellcheck and the tests do the checking.",
          "AGENTS.md gives every agent the build and test commands and your rules. Keep it short.",
          "Never paste secrets or customer data, and check every package an AI suggests, because of slopsquatting.",
          "An agent is a model in a loop. The host runs its tool calls with credentials you chose.",
          "MCP connects hosts to servers that offer tools, resources and prompts, over stdio or Streamable HTTP.",
          "Read-only flags shorten the menu. RBAC, token scopes and IAM set the real limit.",
          "Agents that read untrusted text get no write access and no secrets, which breaks the lethal trifecta.",
          "GPU workloads are ops work too: device plugins or DRA, tainted GPU nodes, scaling on queues, and idle cost.",
      ],
      cards=[
          ("What is a hallucination in an AI answer?", "An answer that sounds right but is made up, such as a flag, field, package or version that does not exist."),
          ("Why does an AI answer's confidence tell you nothing?", "Models sound just as sure when they are wrong. Only a check you trust decides."),
          ("What does kubeconform -strict add?", "It also rejects fields the schema does not know, such as an invented `timeout` on a probe."),
          ("kubeconform passes, but a server dry run fails. Why?", "Some rules live only in the API server, such as a selector that must match the Pod template's labels."),
          ("What goes into AGENTS.md?", "Set-up, build, test and run commands, the project's rules, what agents must never do, and what done means."),
          ("How does Claude Code use a shared AGENTS.md?", "Through a one-line CLAUDE.md that imports it with `@AGENTS.md`."),
          ("What is slopsquatting?", "Registering package names that AI tools invent, so people who install the suggestion get malware."),
          ("What must never go into a prompt?", "Secrets such as tokens and kubeconfig files, customer data, and anything your company's rules keep inside."),
          ("What are the three MCP roles?", "The host (the AI application), a client inside it for each server, and the server that wraps one system."),
          ("What can an MCP server offer?", "Tools the model can call, resources the host can read, and prompts a person can pick."),
          ("What are the two standard MCP transports?", "stdio for a local server that the host starts itself, and Streamable HTTP for a server that runs elsewhere."),
          ("Does `read_only = true` stop an MCP server from reading Secrets?", "No. Read tools can read whatever the credentials allow. Only RBAC stops that."),
          ("How do you check whether an identity may exec into Pods?", "`kubectl auth can-i create pods --subresource=exec --as=<identity>`"),
          ("What is prompt injection?", "Text in data the agent reads, such as an issue or a log line, written to give it new orders."),
          ("What is the lethal trifecta?", "Private data, untrusted content and a way to send data out in one agent. Remove one, and that attack stops."),
          ("How should an AI review workflow be split?", "A read-only job runs the model. A separate job with pull-requests: write posts the comment."),
          ("How does a container ask for a GPU?", "In `limits`, for example `nvidia.com/gpu: 1`, once a device plugin reports the node's GPUs."),
          ("Why scale inference on queue length instead of CPU?", "The model works on the GPU, so CPU says little about the real load."),
      ],
      res_why=[
          "The protocol itself: roles, features, transports and its security principles, in the current version.",
          "Safe defaults for MCP servers on your laptop: where they come from, how to shut them in, credentials and network.",
          "Every setting the lab's TOML file uses, and the project's own explanation of why RBAC is the real control.",
          "Read-only mode, toolsets and lockdown mode for the server most DevOps agents use first.",
          "The format, real examples and the list of tools that read it, in one short page.",
          "The clearest explanation of why prompt injection turns into data theft, and which leg to remove.",
          "The security community's list of the main risks in applications built on language models.",
          "The study behind slopsquatting: how often code models invent packages, and what reduces it.",
          "The people who designed MCP explain why it exists and how hosts, clients and servers fit together.",
          "A short, plain explanation of prompt injection and the defences that actually limit it.",
          "A widely watched talk on working with language models, with good advice on keeping them on a short leash.",
          "Agents in GitHub Actions with read-only, sandboxed jobs and checked safe outputs, from GitHub.",
      ],
      quiz=[
          ("An assistant suggests `kubectl rollout restart deploy/hello-devops --grace=30s`. You have never seen `--grace`. What do you do?",
           "An unfamiliar flag from a model is a guess until the tool's own help or docs confirm it."),
          ("kubeconform -strict passes, but `kubectl apply --dry-run=server` fails with \"selector does not match template labels\". What does that show?",
           "A schema checks fields and types. Rules that compare two fields of an object live in the API server's own checks."),
          ("Where should the one command that runs every check live, so coding agents use it too?",
           "Agents read AGENTS.md on every task, and a script in the repository gives people, agents and CI the same definition of done."),
          ("An MCP server runs with `read_only = true` but uses your admin kubeconfig. What can a fooled agent still do?",
           "read_only hides write tools, but the read tools run with admin credentials, so anything readable is exposed."),
          ("Why does the lab's AI review use two jobs instead of one?",
           "Splitting keeps the model, the untrusted input and the write token apart, so a fooled agent has nothing to write with."),
          ("A triage agent reads public issues, can read your private repositories, and can comment in public. Which leg is easiest to remove?",
           "Triage needs the public issues and a way to comment, but not private repositories, so that leg goes."),
          ("A GPU node pool sits almost unused every night. Which step fits first?",
           "An idle GPU costs as much as a busy one, so the cheapest fix is not to run it."),
          ("An agent's change edits `ai/check.sh` so the failing kubeconform step is skipped. What should happen?",
           "Weakening a check to make it pass hides the problem. A change to a check must be argued for on its own."),
          ("Day 64's checklist says no Role should use `*`. Why does that matter for an agent's Role?",
           "A `*` grants every resource type that exists now and every type added later, so the agent's access grows by itself."),
          ("Why should an AI review workflow use `pull_request` and not `pull_request_target`?",
           "pull_request_target runs with the base repository's secrets and a write token, so untrusted code there can steal both."),
      ])
save(18, P)

# ---------- Part 19 ----------
P = load(19)
apply(P,
      intro=("Part 19 is the last part. Day 67 shows what happens when many teams need what you built: "
             "platform teams turn it into golden paths, ready-made ways to do common jobs. "
             "FinOps then gives every cost an owner. "
             "Day 68 is your capstone. One change travels through every part of the course with a check at each stage, "
             "and you finish with a plan for what to learn next."),
      recap=[
          "Platform engineering turns repeated DevOps work into self-service golden paths, run as a product for developers.",
          "Backstage is a framework for developer portals. The platform is the templates, pipelines and clusters behind it.",
          "The CNCF maturity model scores five aspects on four levels. Pick your next step instead of aiming for level 4 everywhere.",
          "FinOps loops through inform, optimize and operate, and starts with an owner label on every cost.",
          "Showback comes first: each team sees its own cost, and idle cost gets its own line.",
          "A golden path ships its guardrails: pinned actions, signed images, narrow RBAC, policies and owner labels.",
          "The capstone runs one change through the tools of every part, with a runnable check for each stage.",
          "Game days, runbooks, a clear README and a short demo turn the capstone into a portfolio.",
          "Choose certifications from the official curricula: CKAD suits a developer, and CKA gives troubleshooting 30%.",
      ],
      cards=[
          ("What is an internal developer platform?", "The self-service tools a platform team offers, such as templates, build pipelines, environments and dashboards."),
          ("What is a golden path?", "A supported, ready-made way to do a common task, made easier than doing it alone."),
          ("Is a golden path the only allowed path?", "No. Teams may leave it with a reason, and many teams leaving tells you the path is wrong."),
          ("What is Backstage?", "An open source framework for developer portals: software catalog, templates, TechDocs and plugins."),
          ("What are the five aspects of the CNCF platform maturity model?", "Investment, adoption, interfaces, operations and measurement."),
          ("Adoption by order or adoption by choice: which maturity levels?", "Pushed by mandate is level 2. Pulled by teams who want it is level 3."),
          ("What are the three FinOps phases?", "Inform, optimize and operate, repeated as a loop."),
          ("What comes first in FinOps?", "Allocation: give every cost an owner, with tags in the cloud and labels in Kubernetes."),
          ("Why do Kubernetes requests drive cost?", "The scheduler reserves what a Pod requests, whether it uses it or not."),
          ("Showback or chargeback: what is the difference?", "Showback reports each team's cost while the money stays central. Chargeback moves the cost into each team's budget."),
          ("What is idle cost in a Kubernetes cluster?", "What you pay for node capacity that no workload requested."),
          ("Why track cost per request instead of the total bill?", "Totals grow with the business. Cost per request shows whether each unit of work got cheaper."),
          ("What does `owner` in catalog-info.yaml say?", "Which team owns the service in the developer portal: the same idea as the team label on its Pods."),
          ("What does `gh repo create --template` do?", "It creates a new repository with a copy of a template repository's files and a fresh history."),
          ("What makes a good acceptance check?", "It looks at the running system, gives pass or fail, and runs with one command."),
          ("What is a game day?", "A planned session where you break things on purpose and compare what happens with what you expected."),
          ("Which domain carries the most weight in the CKA curriculum?", "Troubleshooting, at 30%."),
          ("What does HashiCorp publish about the Terraform Associate (004) exam?", "Multiple choice, one hour, online proctored, US$70.50 plus taxes, valid for two years."),
      ],
      res_why=[
          "The definition of a platform and what it offers, from the CNCF's app delivery group, with no product to sell.",
          "The full table of five aspects and four levels, to score your own platform honestly.",
          "A short tour of the catalog, templates and TechDocs, from the project itself.",
          "The official overview, with the problems Backstage solves and its CNCF status.",
          "How showback and chargeback differ, and why every FinOps practice starts with showback.",
          "A free CNCF tool that splits Kubernetes and cloud cost by namespace, label and workload.",
          "How a template with a form creates a repository and adds it to the catalog.",
          "How inform, optimize and operate repeat, from the foundation that maintains the framework.",
          "The official topic areas and weights for KCNA, CKAD, CKA, CKS and the newer exams.",
          "A free full course for the KCNA, linked from the official KCNA curriculum.",
          "Free online, and the best next read on running systems reliably. One chapter a week is a good pace.",
          "Format, price and study path for the Terraform exam, straight from HashiCorp.",
      ],
      quiz=[
          ("Which sign shows that a platform has reached \"intrinsic pull\" adoption?",
           "In the CNCF model, pull means teams adopt the platform because it helps them, not because they were told to."),
          ("A platform team ships a Backstage portal with no templates or self-service behind it. What have they built?",
           "Backstage is a framework for the portal. The value is in what the portal lets teams do."),
          ("A team's Pods request 4 CPUs in total but use 0.5 on average. Which FinOps lever fits first?",
           "Requests reserve capacity whether used or not, so matching them to real use frees the most for the least effort."),
          ("You create payments-api from the hello-devops template and rename it with sed. `helm lint` now fails: there is no Chart.yaml in chart/payments-api. What did the rename miss?",
           "sed changes what is inside files, not folder names, so the chart folder still has the old name. The template's instructions must say so."),
          ("Finance wants every team to see its cluster cost each month, but budgets stay central for now. Which practice is that?",
           "Showback reports cost per team without moving money between budgets. Chargeback would move it."),
          ("Which of these is a binary, runnable acceptance check for the capstone?",
           "It looks at the running system, takes one command, and returns pass or fail."),
          ("On game day you scale Redis to 0. Where do you expect the first visible sign in hello-devops?",
           "The readiness endpoint returns 503 when Redis is set but down, so Kubernetes stops sending traffic to those Pods."),
          ("You want to prove Kubernetes security skills, including supply chain security. Which exam's curriculum has a Supply Chain Security domain at 20%?",
           "The CKS curriculum lists Supply Chain Security at 20%, next to cluster and system hardening."),
          ("A bad release was synced automatically by Argo CD with self-heal on. How do you roll back?",
           "Git is the source of truth. Self-heal would undo a rollback by hand, while a revert commit is synced like any change."),
          ("Prometheus on kind has no hello_requests_total at all. What is the most likely cause?",
           "Prometheus only scrapes what a ServiceMonitor selects, so a label mismatch means no target and no data."),
      ])
save(19, P)
print("parts written")
