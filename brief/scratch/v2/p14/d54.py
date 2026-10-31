"""Day 54: Platform engineering, FinOps and AI in DevOps (Part 14)."""
import pathlib

from svg import arrow, box, note, svg

LAB = pathlib.Path("/home/user/devops-from-zero/labs/hello-devops")


def lab(path):
    return (LAB / path).read_text().rstrip("\n")


def diagram():
    xs = [8, 122, 268, 366, 472]
    ws = [88, 120, 72, 80, 80]
    labels = ["AI agent", "Pull request", "Review", "Argo CD", "Cluster"]
    classes = ["bxp", "bx", "bxg", "bxo", "bxt"]
    captions = ["proposes", "CI and policy", "a human", "syncs git", "runs it"]
    p = [note(280, 22, "every change takes the same path as a human change")]
    for i in range(5):
        p.append(box(xs[i], 40, ws[i], 44, classes[i], labels[i]))
        p.append(note(xs[i] + ws[i] / 2, 104, captions[i]))
        if i < 4:
            p.append(arrow(xs[i] + ws[i] + 2, 62, xs[i + 1] - 4, 62))
    # The only direct line from the agent to the cluster: a read-only token.
    p.append(arrow(52, 112, 52, 150, dashed=True, head=False))
    p.append(arrow(52, 150, 512, 150, dashed=True, head=False))
    p.append(arrow(512, 150, 512, 114, dashed=True))
    p.append(note(282, 170, "read-only token: get, list, watch, nothing else"))
    return svg(186, "An AI agent proposes a pull request; CI and policies check it, a human reviews it, Argo CD syncs it to the cluster. "
               "The agent's only direct line to the cluster is a read-only token.", p)


SECTIONS = [
    {
        "h": "Why platform teams exist",
        "body": (
            "List what hello-devops needs by now. A Dockerfile, two workflows with pinned actions, Kubernetes YAML and an Argo CD Application. "
            "A ServiceMonitor, a dashboard, log shipping and tracing. Policies, and a way to get secrets. You learned all of it in this course. "
            "Now picture 40 product teams, each building that alone. They solve the same problems 40 times, in 40 slightly different ways, "
            "and whoever is on call has to learn every one.\n\n"
            "Platform engineering is the answer most large companies have reached. A platform team builds an internal developer platform (IDP): "
            "the self-service capabilities that product teams use to build, ship and run software. "
            "The [CNCF platforms white paper](https://tag-app-delivery.cncf.io/whitepapers/platforms/) puts self-service at the centre. "
            "A developer gets an environment, a database or a pipeline without filing a ticket and waiting a week.\n\n"
            "The big shift is that the platform is a product, and developers are its customers. That changes the team's week:\n"
            "- It talks to its users and watches where they get stuck.\n"
            "- It publishes a roadmap and takes feature requests.\n"
            "- It measures success by adoption and speed, never by the number of tools installed.\n\n"
            "A classic operations team does work for other teams, through tickets. "
            "A platform team builds things so that other teams can do the work themselves. "
            "DevOps ideas such as shared ownership and automation still apply; the platform makes them the easy option."
        ),
        "refs": [
            {"title": "CNCF platforms white paper", "url": "https://tag-app-delivery.cncf.io/whitepapers/platforms/", "kind": "read"},
            {"title": "Platform engineering in the 2025 DORA report (DORA community discussion)", "url": "https://www.youtube.com/watch?v=s_6gwd4zAwE", "kind": "watch"},
        ],
    },
    {
        "h": "Golden paths and developer portals",
        "body": (
            "The platform's main product is the golden path, which some companies call the paved road. "
            "It is a supported, ready-made way to do a common job. \"Create a new service\" is the classic one. "
            "You fill in a name and a team. You get a repository with a Dockerfile, CI, a release workflow, "
            "Kubernetes YAML, an Argo CD Application and a dashboard, already wired together.\n\n"
            "The [CNCF maturity model](https://github.com/cncf/tag-app-delivery/blob/main/platforms-maturity-model/v1/index.md) describes golden paths as documentation and templates built on compliant and tested patterns. Two of those words carry weight:\n"
            "- Compliant: security and policy are built in, so the easy way is also the safe way.\n"
            "- Tested: the platform team keeps the template working, so a new service starts with current versions.\n\n"
            "Teams may still leave the path when they have a good reason. If many teams leave it, the path is wrong, and that is the most useful feedback a platform team gets.\n\n"
            "Developers find these paths through a developer portal. Backstage, created at Spotify and now a CNCF incubating project, "
            "is the best-known framework for building one. It has:\n"
            "- A software catalog: every service, its owner, its docs and what it depends on.\n"
            "- Software templates: golden paths you start from a form.\n"
            "- TechDocs: documentation written in Markdown next to the code.\n"
            "- Plugins that show CI runs, Kubernetes state, costs and more on each service's page.\n\n"
            "Backstage is the shop front. The platform is the shop behind it: the templates, pipelines and clusters. "
            "With one repository and one team you do not need a portal at all; a GitHub template repository does the job."
        ),
        "refs": [
            {"title": "What is Backstage? (Backstage explainer video)", "url": "https://www.youtube.com/watch?v=85TQEpNCaU0", "kind": "watch"},
            {"title": "Backstage docs: what is Backstage?", "url": "https://backstage.io/docs/overview/what-is-backstage", "kind": "docs"},
            {"title": "Backstage docs: software templates", "url": "https://backstage.io/docs/features/software-templates/", "kind": "docs"},
        ],
    },
    {
        "h": "Is the platform working? Maturity and developer experience",
        "body": (
            "The [CNCF Platform Engineering Maturity Model](https://github.com/cncf/tag-app-delivery/blob/main/platforms-maturity-model/v1/index.md) "
            "lets a team check where it stands. It scores five aspects, each on four levels: provisional, operational, scalable and optimizing.\n"
            "- Investment: from volunteers, to a dedicated team, to a product, to an enabled ecosystem.\n"
            "- Adoption: from erratic, to pushed by mandate, to pulled by teams who want it, to teams who contribute.\n"
            "- Interfaces: from custom processes, to standard tools, to self-service, to integrated services.\n"
            "- Operations: from by request, to centrally tracked, to centrally enabled, to managed services.\n"
            "- Measurement: from ad hoc, to consistent collection, to insights, to numbers plus user feedback.\n\n"
            "Score each aspect on its own. You do not need level 4 everywhere, and a CNCF blog post from September 2026 notes that many teams stall at level 2 for interfaces.\n\n"
            "The adoption row teaches the most. A platform that teams use because a manager said so sits at level 2. "
            "A platform that teams choose because it is faster sits at level 3.\n\n"
            "Developer experience (DevEx) is how it feels to ship software in a company. Measure it with a few plain numbers:\n"
            "- Time from \"new service\" to its first production deploy.\n"
            "- How often a developer waits for another team.\n"
            "- The DORA metrics from Day 1, for teams on the golden path and off it.\n\n"
            "Then ask the developers directly, every quarter. At the lowest level of the model, users believe their feedback is not considered, so asking and acting on the answers already moves you up."
        ),
        "refs": [
            {"title": "CNCF Platform Engineering Maturity Model (source)", "url": "https://github.com/cncf/tag-app-delivery/blob/main/platforms-maturity-model/v1/index.md", "kind": "read"},
            {"title": "Building a platform maturity model (Abby Bangser)", "url": "https://www.youtube.com/watch?v=NL__twwMiGE", "kind": "watch"},
        ],
    },
    {
        "h": "FinOps: every cost gets an owner",
        "body": (
            "In the cloud, any engineer can spend money with one command, and the bill arrives a month later with no names on it. "
            "FinOps is the practice of making that cost visible and shared between engineering, finance and the business. "
            "The FinOps Foundation, a Linux Foundation project, maintains the [framework](https://www.finops.org/framework/lifecycle/) most teams follow. It loops through three phases, again and again:\n"
            "1. Inform: see who spends what, and give every cost an owner.\n"
            "2. Optimize: get the same result for less, through better rates and less waste.\n"
            "3. Operate: make it routine, with budgets, reviews and alerts.\n\n"
            "Everything starts with allocation. Until a cost has an owner, every saving is a guess. In the cloud that means tags (Day 10). "
            "In Kubernetes it means labels, because many teams share one cluster. "
            "A cost tool adds up each Pod's CPU and memory requests and splits the price of the nodes by label. "
            "The lab's `policy/require-team-label.yaml` audits that every workload in hello carries a `team` label.\n\n"
            "Then the usual levers, roughly from easy to hard:\n"
            "- Right-size requests from real usage (Day 35). The scheduler reserves what you request, used or not.\n"
            "- Autoscale Pods and nodes, so quiet hours cost less.\n"
            "- Turn off what nobody uses: dev environments at night, forgotten test clusters.\n"
            "- Commit to reserved capacity for steady load, and use spot capacity for work that can restart.\n\n"
            "The framework now reaches beyond public cloud, through \"scopes\" grouped under the name Cloud+. "
            "My advice for any team: put cost on a dashboard next to latency and errors, and look at it every week."
        ),
        "refs": [
            {"title": "FinOps Foundation: the FinOps lifecycle", "url": "https://www.finops.org/framework/lifecycle/", "kind": "read"},
            {"title": "Microsoft Learn: the FinOps framework explained", "url": "https://learn.microsoft.com/cloud-computing/finops/framework/finops-framework", "kind": "docs"},
        ],
    },
    {
        "h": "AI in DevOps: what the evidence says",
        "body": (
            "AI tools are now part of daily DevOps work. Google's DORA team surveyed nearly 5,000 technology professionals for its "
            "[2025 report on AI-assisted software development](https://dora.dev/dora-report-2025/), and about 90% used AI at work. "
            "The report's main finding is that AI is an amplifier. It makes strong teams stronger and struggling teams worse. "
            "AI use now goes with higher delivery throughput, and still with less stable delivery.\n\n"
            "You meet AI in three places:\n"
            "- Coding agents. [GitHub's docs](https://docs.github.com/en/copilot/concepts/agent-capabilities/about-agents/about-github-copilot-agents) define an agent as a system that can plan a task, use tools, inspect the results and adjust. "
            "You assign an issue, the agent works on a branch, and it opens a pull request.\n"
            "- CI and operations. Explaining a failed build, drafting a fix, summarizing a Terraform plan, sorting new issues. "
            "GitHub Agentic Workflows run such agents inside GitHub Actions, with read-only tokens by default.\n"
            "- Incident response. Pulling together logs, metrics and runbooks, and drafting a timeline. "
            "Practitioners agree that a human still decides on rollbacks, customer messages and the final root cause.\n\n"
            "Agents reach your tools through MCP, the [Model Context Protocol](https://github.com/modelcontextprotocol/modelcontextprotocol): an open standard for connecting an AI assistant to other systems. "
            "An MCP server wraps one system and offers its actions as tools that the agent can call. "
            "There are MCP servers for GitHub, for Terraform from HashiCorp, and for Kubernetes.\n\n"
            "GitHub's docs state the deal plainly. You define the goal and the limits, you grant the access, and you review the work."
        ),
        "refs": [
            {"title": "Announcing the 2025 DORA report (Google Cloud blog)", "url": "https://cloud.google.com/blog/products/ai-machine-learning/announcing-the-2025-dora-report", "kind": "read"},
            {"title": "The DORA 2025 report: key findings and insights (Steve Fenton and Rob Edwards)", "url": "https://www.youtube.com/watch?v=DIBzCc6sE9M", "kind": "watch"},
            {"title": "GitHub Docs: about GitHub Copilot agents", "url": "https://docs.github.com/en/copilot/concepts/agent-capabilities/about-agents/about-github-copilot-agents", "kind": "docs"},
        ],
    },
    {
        "h": "Guardrails: the same rules for a new kind of user",
        "body": (
            "Treat an AI agent like a contractor on day one: quick and useful, and without keys yet. Every guardrail here is one you already built for people and CI:\n"
            "- Read-only by default. The GitHub MCP server's `--read-only` flag wins over any write tool you enable. "
            "The Terraform MCP server keeps tools that need approval off unless you set `ENABLE_TF_OPERATIONS`. The Kubernetes MCP server has `read_only = true`.\n"
            "- Least privilege. A read-only flag limits the tool, not the credentials behind it. "
            "An MCP server running with your admin kubeconfig can still do whatever that kubeconfig allows. "
            "So give the agent its own identity: the lab's `policy/ai-agent-readonly.yaml` can read Pods, logs, events and workloads in hello, and change nothing.\n"
            "- Short-lived credentials. `kubectl create token --duration=1h` makes a token that expires by itself. Deleting the ServiceAccount cuts it off at once.\n"
            "- Human review. The agent proposes a pull request or a `terraform plan`. "
            "A person approves it, and it goes through the same CI, Kyverno policies and Argo CD as any human change.\n"
            "- Untrusted input. A log line, an issue comment or a web page can contain text that tries to give the agent orders. "
            "This is called prompt injection, and your guardrails must hold even when the agent is fooled.\n\n"
            "Why a custom Role, and not the built-in `view` ClusterRole? The built-in role would work today, but it is aggregated. "
            "Tools such as Argo CD or Kyverno can add their own rules to it when you install them. A Role that lists every action stays exactly as written.\n\n"
            "This is where the GitOps setup from Part 8 pays off again. With Argo CD applying git, an agent never needs write access to the cluster. "
            "It opens a pull request, and the pipeline does the rest."
        ),
        "refs": [
            {"title": "GitHub MCP Server: read-only mode and toolsets (README)", "url": "https://github.com/github/github-mcp-server/blob/main/README.md", "kind": "docs"},
            {"title": "Kubernetes MCP server (README)", "url": "https://github.com/containers/kubernetes-mcp-server/blob/main/README.md", "kind": "docs"},
            {"title": "Terraform MCP server (README)", "url": "https://github.com/hashicorp/terraform-mcp-server/blob/main/README.md", "kind": "docs"},
        ],
    },
    {
        "h": "Other trends worth a line each",
        "body": (
            "You will meet these names in job ads and conference talks:\n"
            "- eBPF runs small, checked programs inside the Linux kernel. [Cilium](https://github.com/cilium/cilium) uses it for Kubernetes networking, observability and security, and can replace kube-proxy.\n"
            "- [OpenTofu](https://github.com/opentofu/opentofu) is the open source fork of Terraform (Part 6). The commands are nearly the same: `tofu plan` instead of `terraform plan`.\n"
            "- WebAssembly (Wasm) runs small, sandboxed programs that start very fast, as plugins inside other tools or at the edge.\n"
            "- Serverless containers, such as Google Cloud Run, AWS Fargate and Azure Container Apps, run your image with no servers or cluster to manage. "
            "For one small service, that is often the simplest place to run it."
        ),
        "refs": [
            {"title": "Cilium (README)", "url": "https://github.com/cilium/cilium", "kind": "docs"},
            {"title": "OpenTofu (README)", "url": "https://github.com/opentofu/opentofu", "kind": "docs"},
        ],
    },
]

WORKED = {
    "title": "Give an AI agent a read-only key to your cluster",
    "steps": [
        {
            "say": "Say you want to try a Kubernetes MCP server against your kind cluster. Do not hand it your own kubeconfig: on kind, that is full admin. "
                   "Create a separate identity first, from `policy/ai-agent-readonly.yaml` in Files.",
            "code": (
                "$ kubectl apply -f policy/ai-agent-readonly.yaml\n"
                "serviceaccount/ai-agent created\n"
                "role.rbac.authorization.k8s.io/ai-agent-read created\n"
                "rolebinding.rbac.authorization.k8s.io/ai-agent-read created"
            ),
            "lang": "console",
        },
        {
            "say": "Ask the API server what this identity may do, before anything uses it. The list shows read verbs only, on the resources you debug with (trimmed here).",
            "code": (
                "$ kubectl auth can-i --list -n hello --as=system:serviceaccount:hello:ai-agent\n"
                "Resources                              Non-Resource URLs   Resource Names   Verbs\n"
                "configmaps                             []                  []               [get list watch]\n"
                "events                                 []                  []               [get list watch]\n"
                "pods/log                               []                  []               [get list watch]\n"
                "pods                                   []                  []               [get list watch]\n"
                "deployments.apps                       []                  []               [get list watch]\n"
                "horizontalpodautoscalers.autoscaling   []                  []               [get list watch]"
            ),
            "lang": "console",
        },
        {
            "say": "Check the doors that must stay shut: Secrets, a shell inside a Pod, deletes, and other namespaces.",
            "code": (
                "$ kubectl auth can-i get secrets -n hello --as=system:serviceaccount:hello:ai-agent\n"
                "no\n"
                "$ kubectl auth can-i create pods/exec -n hello --as=system:serviceaccount:hello:ai-agent\n"
                "no\n"
                "$ kubectl auth can-i delete pods -n hello --as=system:serviceaccount:hello:ai-agent\n"
                "no\n"
                "$ kubectl auth can-i list pods -n kube-system --as=system:serviceaccount:hello:ai-agent\n"
                "no"
            ),
            "lang": "console",
        },
        {
            "say": "Make a separate kubeconfig file that holds only a one-hour token for this identity. "
                   "`security/agent-kubeconfig.sh` writes it outside the repository, readable only by you. Then try it.",
            "code": (
                "$ security/agent-kubeconfig.sh 1h\n"
                "Wrote /Users/you/.kube/ai-agent.kubeconfig. The token expires after 1h.\n"
                "Try: KUBECONFIG=/Users/you/.kube/ai-agent.kubeconfig kubectl get pods\n"
                "$ export KUBECONFIG=~/.kube/ai-agent.kubeconfig\n"
                "$ kubectl get deploy\n"
                "NAME           READY   UP-TO-DATE   AVAILABLE   AGE\n"
                "hello-devops   3/3     3            3           2d\n"
                "redis          1/1     1            1           2d"
            ),
            "lang": "console",
        },
        {
            "say": "Whatever the agent is told to do, the API server refuses anything outside the Role.",
            "code": (
                "$ kubectl delete deploy redis\n"
                "Error from server (Forbidden): deployments.apps \"redis\" is forbidden: User \"system:serviceaccount:hello:ai-agent\" "
                "cannot delete resource \"deployments\" in API group \"apps\" in the namespace \"hello\"\n"
                "$ kubectl get secrets\n"
                "Error from server (Forbidden): secrets is forbidden: User \"system:serviceaccount:hello:ai-agent\" "
                "cannot list resource \"secrets\" in API group \"\" in the namespace \"hello\""
            ),
            "lang": "console",
        },
        {
            "say": "Now point the MCP server at this file, in read-only mode, with Secrets denied as a second lock. "
                   "This is the TOML config format from the Kubernetes MCP server's README.",
            "code": (
                "kubeconfig = \"/Users/you/.kube/ai-agent.kubeconfig\"\n"
                "read_only = true\n"
                "toolsets = [\"core\"]\n\n"
                "[[denied_resources]]\n"
                "group = \"\"\n"
                "version = \"v1\"\n"
                "kind = \"Secret\""
            ),
            "lang": "ini",
        },
        {
            "say": "The kill switch: delete the ServiceAccount, and every token made for it stops working at once. Apply the file again when you want the agent back.",
            "code": (
                "$ unset KUBECONFIG\n"
                "$ kubectl -n hello delete serviceaccount ai-agent\n"
                "$ KUBECONFIG=~/.kube/ai-agent.kubeconfig kubectl get deploy\n"
                "error: You must be logged in to the server (Unauthorized)"
            ),
            "lang": "console",
        },
    ],
}

CODE = [
    {"lang": "yaml", "title": "policy/ai-agent-readonly.yaml", "src": lab("policy/ai-agent-readonly.yaml"),
     "run": "kubectl apply -f policy/ai-agent-readonly.yaml"},
    {"lang": "bash", "title": "security/agent-kubeconfig.sh", "src": lab("security/agent-kubeconfig.sh"),
     "run": "security/agent-kubeconfig.sh 1h"},
    {"lang": "yaml", "title": "policy/require-team-label.yaml", "src": lab("policy/require-team-label.yaml"),
     "run": "kubectl apply -f policy/require-team-label.yaml"},
]

COMMANDS = [
    {"cmd": "kubectl apply -f policy/ai-agent-readonly.yaml", "what": "Create a read-only identity for an AI agent in namespace hello."},
    {"cmd": "kubectl auth can-i --list -n hello --as=system:serviceaccount:hello:ai-agent", "what": "List everything that identity may do in hello."},
    {"cmd": "kubectl -n hello create token ai-agent --duration=1h", "what": "Print a token for that identity that expires in one hour."},
    {"cmd": "security/agent-kubeconfig.sh 1h", "what": "Write ~/.kube/ai-agent.kubeconfig with only a one-hour agent token."},
    {"cmd": "KUBECONFIG=~/.kube/ai-agent.kubeconfig kubectl get pods", "what": "Run one command as the agent, without touching your own kubeconfig."},
    {"cmd": "kubectl -n hello delete serviceaccount ai-agent", "what": "Kill switch: every token of that identity stops working at once."},
    {"cmd": "github-mcp-server --read-only --toolsets repos,issues,pull_requests,actions", "what": "Start the GitHub MCP server with read-only tools for a few areas only."},
    {"cmd": "kubectl apply -f policy/require-team-label.yaml", "what": "Audit that every workload in hello has a team label for cost allocation."},
    {"cmd": "kubectl get pods -A -L team", "what": "Show every Pod with its team label as an extra column."},
    {"cmd": "kubectl get pods -A -o json | jq -r '[.items[] | {t: (.metadata.labels.team // \"no-team\"), c: ([.spec.containers[].resources.requests.cpu // \"0\" | if endswith(\"m\") then .[:-1]|tonumber else tonumber*1000 end] | add)}] | group_by(.t)[] | \"\\(.[0].t) \\(map(.c)|add)m CPU\"'", "what": "Add up requested CPU per team label, in millicores."},
    {"cmd": "kubectl top pods -n hello", "what": "Compare what Pods use right now with what they request (needs metrics-server)."},
]

DEEPER = (
    "You now have a service with every DevOps piece in place, which makes it a good template. Here is how a platform team would turn it into a golden path, at small scale:\n"
    "1. Mark the repository as a template in its GitHub settings, so \"Use this template\" creates new repositories from it.\n"
    "2. Replace the names `hello-devops` and `hello` with placeholders, filled in by a script or by Backstage.\n"
    "3. Keep what every service needs: the Dockerfile, both workflows with pinned actions, the Kubernetes YAML, the Argo CD Application, the ServiceMonitor, the policies and the security scripts.\n"
    "4. Write a short README: how to run it locally, how to release, where the dashboard is, and who owns the template.\n\n"
    "Backstage takes this further. A software template shows a form (service name, team, port), creates the repository, fills in the names, and registers the service in the catalog. "
    "The catalog entry is a small file next to the code, usually `catalog-info.yaml`. "
    "It is a `Component` with a name, a `type` such as `service`, a `lifecycle` such as `production`, and an `owner`. "
    "That owner field is the same idea as the `team` label from today: every service, and every cost, belongs to somebody.\n\n"
    "Then check whether the golden path helps. The questions I would ask after three months:\n"
    "- How long does it take from \"new service\" to the first production deploy, on the path and off it?\n"
    "- How many teams use the path, and why did the others leave it?\n"
    "- Do the DORA metrics from Day 1 look better for services on the path?\n\n"
    "Watch for two failure modes. If teams cannot change anything in a template, they copy it once and drift away. "
    "And templates age: base images, action SHAs and chart versions go stale. "
    "Keep the template itself under CI and Dependabot, so every new service starts current.\n\n"
    "AI agents fit well here, inside the guardrails. Keeping 40 services on the path means many small, boring pull requests: bump a base image, update a pinned SHA, add a new required label. "
    "An agent can draft them, CI and Kyverno check them, and a human merges them. "
    "The DORA finding applies: if the path and the pipeline are good, the agent amplifies that. If they are messy, it produces mess faster."
)

lesson = {
    "id": "d54",
    "title": "Platform engineering, FinOps and AI in DevOps",
    "minutes": 45,
    "goal": "By the end you can explain what a platform team builds and how to tell if it works, make cluster cost visible per team, and give an AI agent useful access without handing it the keys.",
    "guess": {
        "q": "A company installs Backstage, a developer portal. Six months later, few teams use it. What is the most likely cause?",
        "options": [
            "Backstage is too slow for large companies",
            "The portal had little real self-service behind it",
            "Developers need a Backstage certificate first",
            "A portal only works after a move to Kubernetes",
        ],
        "answer": 1,
        "why": "A portal is only the front door. Teams adopt a platform when it lets them do real work faster, such as creating a service with CI and deploys already wired up.",
    },
    "terms": [
        {"term": "Platform engineering", "plain": "Building and running internal tools and services so product teams can ship by themselves."},
        {"term": "Internal developer platform", "plain": "The self-service capabilities a platform team offers, such as templates, pipelines, environments and dashboards."},
        {"term": "Golden path", "plain": "A supported, ready-made way to do a common task, such as creating a new service, that is easier than doing it alone."},
        {"term": "Developer portal", "plain": "A web front door to the platform with a service catalog, templates and docs. Backstage is the best-known one."},
        {"term": "FinOps", "plain": "The practice of making cloud cost visible and shared between engineering, finance and the business."},
        {"term": "Cost allocation", "plain": "Giving every cost an owner, usually with tags in the cloud and labels in Kubernetes."},
        {"term": "AI agent", "plain": "An AI tool that plans a task, uses tools such as a shell or an API, checks the results and adjusts."},
        {"term": "MCP", "plain": "Model Context Protocol: an open standard that lets an AI assistant call tools such as GitHub, Terraform or Kubernetes."},
    ],
    "sections": SECTIONS,
    "analogy": (
        "A platform is like the shared services in a big office building. Every company in the building uses the same reception, mail room, network and security desk, so no tenant builds its own. "
        "A golden path is the standard office fit-out: you move in on Monday and start work on Monday. "
        "Where it breaks: a building changes slowly, while a platform must change every month with its users. And a tenant who leaves the fit-out is telling you something about it."
    ),
    "diagram": diagram(),
    "diagram_caption": "Same guardrails, new actor: an agent proposes, a human approves, git deploys.",
    "worked": WORKED,
    "code": CODE,
    "commands": COMMANDS,
    "mistake": (
        "Adopting every trending tool at once. Each tool in this lesson solves a problem you only feel at a certain size. "
        "Backstage pays off with many teams, not one repository, and a FinOps tool is useless until workloads carry owner labels. "
        "Get the basics solid on one real project, then add a tool when you can name the pain it removes."
    ),
    "real_world": (
        "At a payments company, a platform team offers one golden path that creates a service with CI, signing, an Argo CD app, dashboards and a team label already in place. "
        "Finance gets a weekly cost report per team from those labels, and the teams with the biggest unused requests get a pull request that right-sizes them. "
        "An AI agent with a read-only identity drafts the routine upgrade pull requests, and humans review and merge them through the same pipeline."
    ),
    "task": {
        "title": "Make cost visible per team, then score your platform",
        "steps": [
            "Apply `policy/require-team-label.yaml` and read the PolicyReport in hello. Which workloads have no owner?",
            "Add a `team` label to the Pod template of both Deployments, for example `team: web` for hello-devops and `team: data` for Redis. Commit, push, and let Argo CD sync.",
            "Run the per-team CPU one-liner from Commands and write down what each team requests. Add `no-team` to your list: on kind, that is the system Pods.",
            "Compare requests with real use from `kubectl top pods -n hello` (Day 35). Which workload reserves the most CPU it does not use?",
            "Score your own setup on the five aspects of the CNCF maturity model, from 1 to 4. Pick one aspect and write down one change that would move it up a level.",
            "Optional: make an agent kubeconfig with `security/agent-kubeconfig.sh`, point a read-only Kubernetes MCP server at it, and ask your assistant why a Pod restarted. Check that it cannot delete anything.",
        ],
        "hints": [
            "Labels on the Deployment's own metadata do not reach the Pods. Put `team` under `spec.template.metadata.labels`.",
            "Do not add `team` to the Deployment's `selector`. The selector of an existing Deployment cannot be changed, and it does not need to be.",
            "If `kubectl top` says metrics are not available, install metrics-server as on Day 35.",
        ],
        "done_when": "The PolicyReport in hello shows pass for require-team-label on both Deployments, and your one-liner prints CPU per team.",
    },
    "explain_back": {
        "prompt": "Explain in 3 to 4 sentences how you would let an AI agent help with the hello-devops cluster without creating a security risk. Mention identity, credentials, review and GitOps.",
        "answer": (
            "I give the agent its own ServiceAccount with a namespaced Role that can only get, list and watch Pods, logs and events, never Secrets or exec. "
            "Its token lasts one hour and lives in a separate kubeconfig, and deleting the ServiceAccount cuts it off at once. "
            "The MCP server runs in read-only mode too, but I rely on RBAC, because a read-only flag does not shrink the credentials behind it. "
            "Any fix the agent finds becomes a pull request that CI, Kyverno and a human review. Argo CD applies it from git, so the agent never needs write access to the cluster."
        ),
    },
    "recap": [
        "Platform teams turn repeated DevOps work into self-service golden paths, run as a product for developers.",
        "Backstage is a portal framework, the shop front; the platform is the templates, pipelines and clusters behind it.",
        "The CNCF maturity model scores investment, adoption, interfaces, operations and measurement, each from 1 to 4.",
        "FinOps loops through inform, optimize and operate, and starts with an owner label on every cost.",
        "DORA 2025: AI amplifies what a team already is; agents work through MCP and open pull requests.",
        "AI guardrails are old guardrails: own identity, read-only RBAC, short tokens, human review, GitOps.",
    ],
    "check": [
        {
            "q": "Five teams each copy a different CI pipeline and Dockerfile. A new platform team wants to help. What is the best first step?",
            "options": [
                "Ban every pipeline the platform team did not write",
                "Ask each team to build its own Backstage plugin",
                "Offer a golden path template teams can adopt",
                "Move every team to a different cloud provider",
            ],
            "answer": 2,
            "why": "A golden path makes the good way the easy way through self-service, without forcing teams onto it.",
        },
        {
            "q": "Your cluster bill doubled, and nobody knows which team caused it. Which FinOps step comes first?",
            "options": [
                "Label every workload with its owning team",
                "Move every workload to spot instances",
                "Turn off all dev environments today",
                "Rewrite the services to run serverless",
            ],
            "answer": 0,
            "why": "Allocation comes first: until each cost has an owner, every saving is a guess.",
        },
        {
            "q": "An MCP server runs with --read-only, but uses your admin kubeconfig. An issue tells the agent to delete a namespace. What stops it?",
            "options": [
                "The admin kubeconfig refuses AI tools",
                "Kubernetes blocks requests from AI agents",
                "Argo CD blocks deletes in working hours",
                "Only the flag; the credentials allow it",
            ],
            "answer": 3,
            "why": "The flag limits the tool's menu, but the credentials still allow everything, so the real guardrail is a narrow identity.",
        },
    ],
    "interview": [
        {
            "q": "What is platform engineering, and how is it different from a classic operations team?",
            "a": (
                "Platform engineering builds an internal developer platform that product teams use by themselves: templates, pipelines, environments and observability, offered as golden paths. "
                "A classic operations team often does the work for other teams through tickets. "
                "A platform team treats the platform as a product, talks to its users and measures success by adoption and by how quickly and safely teams ship. "
                "The CNCF maturity model is a useful way to check where a platform stands."
            ),
        },
        {
            "q": "How would you start a FinOps practice for a Kubernetes platform?",
            "a": (
                "I would start with allocation: every workload gets a team label, enforced first in Audit mode by a policy, and every cloud resource gets an owner tag. "
                "With that, a cost tool can split node costs by the CPU and memory each team requests, and finance and engineers look at the same numbers. "
                "Then I would right-size requests from real usage, add autoscaling, and turn off idle environments. "
                "Cost goes on a dashboard next to latency and errors, and teams review it every week."
            ),
        },
        {
            "q": "How would you let an AI agent help with infrastructure without creating a security risk?",
            "a": (
                "I give the agent its own identity with narrow, read-only access, such as a namespaced Role in Kubernetes, and short-lived tokens. "
                "Read-only modes in MCP servers help, but I do not rely on them alone, because the credentials behind the server decide what is possible. "
                "Any change goes through a pull request or a Terraform plan that a human reviews, and then through the same CI, policies and GitOps flow as human changes. "
                "I treat everything the agent reads as untrusted, because of prompt injection, and I keep a log of what it did."
            ),
        },
    ],
    "deeper": {"minutes": 15, "body": DEEPER},
    "sources": [
        {"title": "CNCF Platform Engineering Maturity Model (source)", "url": "https://github.com/cncf/tag-app-delivery/blob/main/platforms-maturity-model/v1/index.md"},
        {"title": "Backstage docs: what is Backstage?", "url": "https://backstage.io/docs/overview/what-is-backstage"},
        {"title": "DORA: State of AI-assisted Software Development 2025", "url": "https://dora.dev/dora-report-2025/"},
        {"title": "GitHub Docs: about GitHub Copilot agents", "url": "https://docs.github.com/en/copilot/concepts/agent-capabilities/about-agents/about-github-copilot-agents"},
    ],
}
