#!/usr/bin/env python3
"""Rework Day 67 and the part fields of content/p19.json for the third edition.

AI in DevOps moved to Part 18 (Days 65 and 66). This script starts from the saved
original (brief/scratch/v3/ai/p19.orig.json), so it can be re-run safely:
- part title becomes "Platform engineering and your capstone"
- Day 67 becomes "Platform engineering and FinOps": the two AI sections are replaced
  by platform content and a short pointer, and every AI-centred field is replaced
- Day 68 (the capstone) is copied unchanged
Run: python3 brief/scratch/v3/ai/build_p19.py
"""
import copy
import json
import pathlib

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[3]
ORIG = json.loads((HERE / "p19.orig.json").read_text())
OUT = ROOT / "content/p19.json"
LAB = ROOT / "labs/hello-devops"

P = copy.deepcopy(ORIG)
d67 = P["lessons"][0]
assert d67["id"] == "d67"
osec = {s["h"]: s for s in ORIG["lessons"][0]["sections"]}


def ref(title, url, kind):
    return {"title": title, "url": url, "kind": kind}


P["title"] = "Platform engineering and your capstone"
P["intro"] = (
    "Part 19 is the last part. Day 67 shows what happens when many teams need what you built: "
    "platform teams turn it into golden paths, and FinOps gives every cost an owner. "
    "Day 68 is your capstone. One change travels through every part of the course with a check at each stage, "
    "and you finish with a plan for what to learn next."
)

d67["title"] = "Platform engineering and FinOps"
d67["goal"] = (
    "By the end you can explain what a platform team builds and how to tell if it works, "
    "turn hello-devops into a golden path template, and make cluster cost visible per team."
)

# Terms: keep the six platform and FinOps terms, replace the two AI terms.
d67["terms"] = [t for t in ORIG["lessons"][0]["terms"] if t["term"] not in ("AI agent", "MCP")] + [
    {"term": "Showback", "plain": "A report that shows each team the cost of what it used, while the money stays in a central budget."},
    {"term": "Idle cost", "plain": "What you pay for capacity that no workload requested, such as empty space on nodes."},
]

new_s5 = {
    "h": "Showback, idle cost and cost per request",
    "body": (
        "Once every cost has an owner, you can show each team its bill. The FinOps Foundation separates two ways to do that:\n"
        "- Showback: each team gets a report of what it used, and the money stays in a central budget.\n"
        "- Chargeback: the cost moves into each team's own budget in the finance system.\n\n"
        "The framework calls showback something every FinOps practice needs, and chargeback a choice that depends on how the company does its accounting. Start with showback. Teams change what they run once they see the numbers next to their own name.\n\n"
        "In Kubernetes the report needs one more line: idle cost. A node costs the same whether its Pods request 10% of it or 90%. Capacity that nobody requested still appears on the bill. A tool such as OpenCost, a CNCF project, splits the price of each node by the CPU, memory and GPU each workload requests, and shows what is left as idle. Give that line an owner too, usually the platform team, or every team argues about it.\n\n"
        "Totals grow when the business grows, so they make poor targets. A unit cost works better: cost per request served, per customer, or per build. If traffic doubles and the bill grows by 40%, each request got cheaper, even though the bill went up. hello-devops already has both inputs. Prometheus counts requests in `hello_requests_total` (Day 50), and the `team` label says whose cost it is. Divide one by the other each month, and you have a number a product manager can read."
    ),
    "refs": [
        ref("FinOps Foundation: invoicing and chargeback (showback and chargeback)", "https://www.finops.org/framework/capabilities/invoicing-chargeback/", "read"),
        ref("OpenCost (README): cost allocation for Kubernetes", "https://github.com/opencost/opencost", "docs"),
    ],
}

new_s6 = {
    "h": "Guardrails belong on the golden path",
    "body": (
        "A golden path is easy to follow because the platform team already made the hard choices. Security and policy belong in that set, built in from the start. For hello-devops, a new service made from the template starts with:\n"
        "- pinned actions and least-privilege `permissions:` in every workflow (Days 27 and 63)\n"
        "- a signed image with an SBOM, built by the release workflow\n"
        "- its own ServiceAccount with no token mounted, and Pods that pass the restricted standard (Day 64)\n"
        "- the Kyverno policies, including the `team` label that FinOps needs\n"
        "- a dashboard and alerts for its own metrics\n\n"
        "The cluster enforces the same rules for everyone, so a team that leaves the path still meets them. Roll policies out in Audit mode first, then Deny, as on Day 64. Budgets work the same way: the platform sends the cost alert, and the owning team receives it.\n\n"
        "AI coding agents are one more kind of user of the path, and Days 65 and 66 cover how to use them and fence them in. For a platform team they change one thing. An agent follows AGENTS.md and the template's checks as literally as CI does, so a good template produces good agent changes, and a messy one produces mess faster."
    ),
    "refs": [
        ref("Kubernetes docs: RBAC good practices", "https://kubernetes.io/docs/concepts/security/rbac-good-practices/", "docs"),
        ref("Kubernetes docs: Pod Security Standards", "https://kubernetes.io/docs/concepts/security/pod-security-standards/", "docs"),
    ],
}

d67["sections"] = [
    osec["Why platform teams exist"],
    osec["Golden paths and developer portals"],
    osec["Is the platform working? Maturity and developer experience"],
    osec["FinOps: every cost gets an owner"],
    new_s5,
    new_s6,
    osec["Other trends worth a line each"],
]

d67["diagram"] = (
    '<svg viewBox="0 0 560 186" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="A golden path template creates a new repository with a team label; CI and policy check it; it runs on the cluster, which reserves the requests; a showback report shows cost per owner, and the report and teams that leave the path feed back into the template.">'
    '<text class="ts" x="280" y="24" font-size="11" text-anchor="middle">one template, the same checks, every cost with an owner</text>'
    '<rect class="bxo" x="8" y="40" width="88" height="44" rx="10"/><text class="tk" x="52" y="67" font-size="13" text-anchor="middle">Template</text>'
    '<text class="ts" x="52" y="104" font-size="11" text-anchor="middle">pinned, signed</text>'
    '<line class="ln" x1="98" y1="62" x2="116" y2="62" marker-end="url(#ar)"/>'
    '<rect class="bx" x="120" y="40" width="88" height="44" rx="10"/><text class="t" x="164" y="67" font-size="13" text-anchor="middle">New repo</text>'
    '<text class="ts" x="164" y="104" font-size="11" text-anchor="middle">team label</text>'
    '<line class="ln" x1="210" y1="62" x2="228" y2="62" marker-end="url(#ar)"/>'
    '<rect class="bxt" x="232" y="40" width="104" height="44" rx="10"/><text class="tk" x="284" y="67" font-size="13" text-anchor="middle">CI, policy</text>'
    '<text class="ts" x="284" y="104" font-size="11" text-anchor="middle">Kyverno, RBAC</text>'
    '<line class="ln" x1="338" y1="62" x2="356" y2="62" marker-end="url(#ar)"/>'
    '<rect class="bx" x="360" y="40" width="80" height="44" rx="10"/><text class="t" x="400" y="67" font-size="13" text-anchor="middle">Cluster</text>'
    '<text class="ts" x="400" y="104" font-size="11" text-anchor="middle">requests</text>'
    '<line class="ln" x1="442" y1="62" x2="460" y2="62" marker-end="url(#ar)"/>'
    '<rect class="bxg" x="464" y="40" width="88" height="44" rx="10"/><text class="tk" x="508" y="67" font-size="13" text-anchor="middle">Showback</text>'
    '<text class="ts" x="508" y="104" font-size="11" text-anchor="middle">per owner</text>'
    '<line class="lnd" x1="508" y1="116" x2="508" y2="146"/>'
    '<line class="lnd" x1="508" y1="146" x2="52" y2="146"/>'
    '<line class="lnd" x1="52" y1="146" x2="52" y2="118" marker-end="url(#ar)"/>'
    '<text class="ts" x="280" y="170" font-size="11" text-anchor="middle">cost reports, and teams that leave the path, feed back into the template</text>'
    '</svg>'
)
d67["diagram_caption"] = "A golden path carries its checks and its owner label from the template all the way to the cost report."

CATALOG = (
    "# Backstage catalog entry for this service (Day 67). Put it at the repository root.\n"
    "# A developer portal reads it to list the service, its owner and its links.\n"
    "apiVersion: backstage.io/v1alpha1\n"
    "kind: Component\n"
    "metadata:\n"
    "  name: hello-devops\n"
    "  description: The course's demo web app, with its whole delivery pipeline\n"
    "  annotations:\n"
    "    # Lets Backstage plugins find the repository on GitHub.\n"
    "    github.com/project-slug: <your-github-user>/hello-devops\n"
    "spec:\n"
    "  type: service\n"
    "  lifecycle: production\n"
    "  # The owning team: the same name as the team label on the Pods.\n"
    "  owner: web"
)

d67["worked"] = {
    "title": "Turn hello-devops into a golden path template",
    "steps": [
        {
            "say": "Mark the repository as a template. GitHub then shows a \"Use this template\" button, and every repository made from it starts with a copy of the files and a fresh history.",
            "code": "gh repo edit <your-github-user>/hello-devops --template",
            "lang": "bash",
        },
        {
            "say": "Find every file that hard-codes the service name. Each one is a line a new team must change, and the list is the first draft of your template's instructions. In the course's reference repository, the core folders alone have 27 such files.",
            "code": "$ grep -rl hello-devops k8s chart .github argocd | wc -l\n27",
            "lang": "console",
        },
        {
            "say": "Add a catalog file, so a portal such as Backstage can list the service and its owner. The catalog's `owner` and the Pods' `team` label are the same promise: nothing ships without a name on it. The full file is in Files.",
            "code": "spec:\n  type: service\n  lifecycle: production\n  owner: web",
            "lang": "yaml",
        },
        {
            "say": "Now play the new team. Create a service from the template, and clone it.",
            "code": "gh repo create <your-github-user>/payments-api --template <your-github-user>/hello-devops --private --clone\ncd payments-api",
            "lang": "bash",
        },
        {
            "say": "Replace the old name everywhere, then check that none is left. `sed -i ''` is the macOS form; on Linux, leave out the `''`.",
            "code": "$ grep -rl hello-devops --exclude-dir=.git . | xargs sed -i '' 's/hello-devops/payments-api/g'\n$ grep -rl hello-devops --exclude-dir=.git . | wc -l\n0",
            "lang": "console",
        },
        {
            "say": "Run the same checks as the original, with `ai/check.sh` from Day 65. One fails, and it is a real template bug: sed renamed the chart inside its files, but not its folder. Fix it, and then fix the template's instructions too, so the next team never meets it. (Output trimmed.)",
            "code": "$ ai/check.sh\nPASS  ruff lint\nPASS  ruff format\nPASS  pytest\nPASS  kubeconform k8s/\nFAIL  helm lint\n      ==> Linting chart/payments-api\n      Error unable to check Chart.yaml file in chart: stat chart/payments-api/Chart.yaml: no such file or directory\n$ git mv chart/hello-devops chart/payments-api\n$ ai/check.sh | tail -1\n8 passed, 0 failed, 0 skipped",
            "lang": "console",
        },
    ],
}

orig_code = {c["title"]: c for c in ORIG["lessons"][0]["code"]}
d67["code"] = [
    orig_code["policy/require-team-label.yaml"],
    {"lang": "yaml", "title": "catalog-info.yaml", "src": CATALOG, "run": "git add catalog-info.yaml && git commit -m \"Add a catalog entry\""},
]
assert d67["code"][0]["src"].strip() == (LAB / "policy/require-team-label.yaml").read_text().strip()

orig_cmd = {c["cmd"]: c for c in ORIG["lessons"][0]["commands"]}
d67["commands"] = [
    {"cmd": "gh repo edit <your-github-user>/hello-devops --template", "what": "Mark a repository as a template, so new repositories can start from it."},
    {"cmd": "gh repo create <your-github-user>/payments-api --template <your-github-user>/hello-devops --private --clone", "what": "Create a new repository from the template and clone it."},
    {"cmd": "grep -rl hello-devops --exclude-dir=.git .", "what": "List every file that names the service."},
    {"cmd": "grep -rl hello-devops --exclude-dir=.git . | xargs sed -i '' 's/hello-devops/payments-api/g'", "what": "Rename the service in every file (macOS sed; on Linux use sed -i)."},
    {"cmd": "ai/check.sh", "what": "Run every check in the repository, the same ones the original passes."},
    orig_cmd["kubectl apply -f policy/require-team-label.yaml"],
    {"cmd": "kubectl -n hello get policyreports -o wide", "what": "Read the policy results, including which workloads lack a team label."},
    orig_cmd["kubectl get pods -A -L team"],
    next(c for c in ORIG["lessons"][0]["commands"] if c["cmd"].startswith("kubectl get pods -A -o json | jq")),
    orig_cmd["kubectl top pods -n hello"],
]

d67["real_world"] = (
    "The platform team's golden path gives every new service CI, signing, an Argo CD app, dashboards and a team label, all set up in one go. "
    "Finance gets a weekly cost report per team from those labels, and the teams with the biggest unused requests get a pull request that right-sizes them. "
    "When the template changes, a bot opens the same small upgrade pull request in every service, and each team reviews and merges its own."
)

task = d67["task"]
assert task["steps"][-1].startswith("Optional: make an agent kubeconfig")
task["steps"][-1] = (
    "Optional: add `catalog-info.yaml` from Files to your repository, with your own team as `owner`, "
    "and check that it matches the `team` label on your Pods."
)

d67["explain_back"] = {
    "prompt": "Explain in 3 to 4 sentences what a golden path is and how you would know if yours works. Mention self-service, adoption and cost.",
    "answer": (
        "A golden path is a supported, ready-made way to do a common job, such as creating a service with CI, signing, deploys, dashboards and policies already wired up. "
        "Developers use it by themselves, with no ticket, and the platform team keeps it current like a product. "
        "I know it works when teams choose it because it is faster, so I watch adoption, the time from new service to first deploy, and why teams leave it. "
        "Every service on the path carries an owner label, so its cost shows up per team in a showback report."
    ),
}

recap = list(ORIG["lessons"][0]["recap"])
assert recap[4].startswith("DORA 2025") and recap[5].startswith("AI guardrails")
recap[4] = "Showback comes first: each team sees its own cost, and idle cost gets its own line and an owner."
recap[5] = "A golden path ships its guardrails: pinned actions, signed images, narrow RBAC, policies and owner labels."
d67["recap"] = recap

checks = copy.deepcopy(ORIG["lessons"][0]["check"])
assert "MCP" in checks[2]["q"]
checks[2] = {
    "q": "Traffic to a service doubled this quarter, and its share of the cluster bill grew by 40%. What happened to its cost per request?",
    "options": [
        "It rose, so the team overspent",
        "It stayed the same, by definition",
        "Nothing can be said without prices",
        "It fell by about 30%",
    ],
    "answer": 3,
    "why": "1.4 times the cost for 2 times the requests is 0.7 times the cost per request: the bill grew, and each request got cheaper.",
}
d67["check"] = checks

iv = copy.deepcopy(ORIG["lessons"][0]["interview"])
assert "AI agent" in iv[2]["q"]
iv[2] = {
    "q": "How do you keep a golden path template from going stale?",
    "a": (
        "I treat the template as a product with its own CI, so every change to it runs the checks a real service would. "
        "Dependabot keeps its pinned actions, base images and chart versions current, and template changes reach existing services as small pull requests that each team reviews. "
        "I let teams change what they need, because a path nobody can adjust gets copied once and then drifts. "
        "And I measure it: time to first deploy, how many teams use it, and why the others left."
    ),
}
d67["interview"] = iv

d67["deeper"] = {
    "minutes": 15,
    "body": (
        "A GitHub template repository copies files, and the new team does the rest by hand, as in the worked example. A Backstage software template does more in one form. It is a YAML file of kind `Template` (apiVersion `scaffolder.backstage.io/v1beta3`) that asks for parameters, such as the service name and the owning team, and then runs steps:\n"
        "1. `fetch:template` copies a skeleton folder and fills the parameters into it.\n"
        "2. `publish:github` creates the repository and pushes the result.\n"
        "3. `catalog:register` adds the new service's `catalog-info.yaml` to the catalog.\n\n"
        "The scaffolder fills in the name only where the template's author put a placeholder. So the worked example's bug becomes a question for the author: does every place that needs the name, folder names included, have one? Test the template the way you tested the copy, by creating a service from it and running every check.\n\n"
        "Then find out whether the path helps. The questions I would ask after three months:\n"
        "- How long does it take from \"new service\" to the first production deploy, on the path and off it?\n"
        "- How many teams use the path, and why did the others leave it?\n"
        "- Do the DORA metrics from Day 1 look better for services on the path?\n\n"
        "Watch for two failure modes. If teams cannot change anything in a template, they copy it once and drift away. And templates age: base images, action SHAs and chart versions go stale. Keep the template under CI and Dependabot, so every new service starts current, and send template changes to existing services as pull requests.\n\n"
        "Finally, connect the path to cost. Every service the template creates gets its owner in two places: `spec.owner` in the catalog and the `team` label on its Pods. Then the showback report and the catalog agree on who owns what, and a cost spike has a team's name next to it on the first day."
    ),
}

d67["sources"] = [
    {"title": "CNCF Platform Engineering Maturity Model (source)", "url": "https://github.com/cncf/tag-app-delivery/blob/main/platforms-maturity-model/v1/index.md"},
    {"title": "Backstage docs: what is Backstage?", "url": "https://backstage.io/docs/overview/what-is-backstage"},
    {"title": "Backstage docs: software templates", "url": "https://backstage.io/docs/features/software-templates/"},
    {"title": "FinOps Foundation: invoicing and chargeback", "url": "https://www.finops.org/framework/capabilities/invoicing-chargeback/"},
]

# ---- part fields ----
recap = list(ORIG["recap"])
assert recap[4].startswith("DORA 2025") and recap[5].startswith("AI agents")
recap[4] = "Showback comes first: each team sees its own cost, and idle cost gets its own line."
recap[5] = "A golden path ships its guardrails: pinned actions, signed images, narrow RBAC, policies and owner labels."
P["recap"] = recap

ai_fronts = {
    "What did the 2025 DORA report conclude about AI?",
    "What is MCP?",
    "Does a read-only MCP flag make admin credentials safe?",
    "How do you cut off every token of a Kubernetes ServiceAccount at once?",
    "What is prompt injection?",
}
cards = [c for c in ORIG["flashcards"] if c["front"] not in ai_fronts]
assert len(cards) == len(ORIG["flashcards"]) - 5
new_cards = [
    {"front": "Showback or chargeback: what is the difference?", "back": "Showback reports each team's cost while the money stays central; chargeback moves the cost into each team's budget."},
    {"front": "What is idle cost in a Kubernetes cluster?", "back": "What you pay for node capacity that no workload requested."},
    {"front": "Why track cost per request instead of the total bill?", "back": "Totals grow with the business; cost per request shows whether each unit of work got cheaper."},
    {"front": "What does `owner` in catalog-info.yaml say?", "back": "Which team owns the service in the developer portal: the same idea as the team label on its Pods."},
    {"front": "What does `gh repo create --template` do?", "back": "It creates a new repository with a copy of a template repository's files and a fresh history."},
]
P["flashcards"] = cards[:9] + new_cards + cards[9:]

drop = {"https://dora.dev/dora-report-2025/", "https://www.youtube.com/watch?v=DIBzCc6sE9M", "https://github.com/github/github-mcp-server/blob/main/README.md"}
res = [r for r in ORIG["resources"] if r["url"] not in drop]
assert len(res) == len(ORIG["resources"]) - 3
res[4:4] = [
    {"title": "FinOps Foundation: invoicing and chargeback", "url": "https://www.finops.org/framework/capabilities/invoicing-chargeback/", "kind": "read", "why": "How showback and chargeback differ, and why every FinOps practice starts with showback."},
    {"title": "OpenCost", "url": "https://github.com/opencost/opencost", "kind": "docs", "why": "An open source CNCF tool that splits Kubernetes and cloud cost by namespace, label and workload."},
    {"title": "Backstage docs: software templates", "url": "https://backstage.io/docs/features/software-templates/", "kind": "docs", "why": "How a form-driven template creates a repository and registers it in the catalog."},
]
P["resources"] = res

quiz = copy.deepcopy(ORIG["quiz"])
assert "AI agent" in quiz[3]["q"] and "ignore your rules" in quiz[4]["q"]
quiz[3] = {
    "q": "You create payments-api from the hello-devops template and rename it with sed. `helm lint` now fails: there is no Chart.yaml in chart/payments-api. What did the rename miss?",
    "options": [
        "The Helm repository's URL",
        "The image tag in values.yaml",
        "The team label on the Pods",
        "The chart folder's own name",
    ],
    "answer": 3,
    "why": "sed changes file contents, not folder names, so the chart folder still has the old name; the template's instructions must say so.",
}
quiz[4] = {
    "q": "Finance wants every team to see its cluster cost each month, but budgets stay central for now. Which practice is that?",
    "options": [
        "Showback",
        "Chargeback",
        "Reserved capacity",
        "Spot pricing",
    ],
    "answer": 0,
    "why": "Showback reports cost per team without moving money between budgets; chargeback would move it.",
}
P["quiz"] = quiz

assert P["lessons"][1] == ORIG["lessons"][1], "Day 68 must stay unchanged"
OUT.write_text(json.dumps(P, ensure_ascii=False, indent=1) + "\n")
print(f"wrote {OUT}")
