"""Fifth pass (book voice) for d67, Platform engineering and FinOps. Writer: ti.
Replaces only prose fields of d67 in content/p19.json."""
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[4]
PATH = ROOT / "content/p19.json"
P = json.loads(PATH.read_text())
L = next(x for x in P["lessons"] if x["id"] == "d67")

L["goal"] = ("By the end you can explain what a platform team builds and how to tell if it works, "
             "turn hello-devops into a golden path template, and make cluster cost visible per team.")

L["opening"] = """Picture a town park with a wide lawn between the houses and the station. People cut across it, and soon muddy tracks run in every direction. The council puts up a "Keep off the grass" sign. Nobody reads it. The next spring, a new park keeper tries something else: paved paths exactly where the tracks were, with lights and benches. Within a month the mud is gone, and nobody needed a sign.

Rules feel like the quick fix for a messy shared space, which is why so many companies reach for them first. A path that people want to walk takes longer to build, and it works.

Last time, we fenced in AI agents with careful identities and checks, and every step needed someone who knew the details. In this lesson, we'll see how a platform team turns this whole course into a paved path that many teams can walk. Then FinOps puts an owner's name on every part of the bill. Before we start, make a guess, and keep it in mind."""

L["guess"]["q"] = "A company installs Backstage, a developer portal (a website where developers find tools and services). Six months later, few teams use it. What is the most likely cause?"
L["guess"]["why"] = ("A portal is only the front gate. Teams adopt a platform when it lets them do real work faster, "
                     "such as creating a service with its build and deploy steps already wired up.")

plain = {
    "Platform engineering": "Building and running internal tools and services so product teams can ship software by themselves.",
    "Internal developer platform": "The self-service tools a platform team offers, such as templates, build pipelines, test environments and dashboards.",
    "Golden path": "A supported, ready-made way to do a common task, such as creating a new service, that is easier than doing it alone.",
    "Developer portal": "A website that is the front door to the platform, with a list of services, templates and docs. Backstage is the best-known one.",
    "FinOps": "The practice of making cloud cost visible and shared between engineering, finance and the business.",
    "Cost allocation": "Giving every cost an owner, usually with tags in the cloud and labels in Kubernetes.",
    "Showback": "A report that shows each team the cost of what it used, while the money stays in a central budget.",
    "Idle cost": "What you pay for capacity that no workload asked for, such as empty space on the machines of a cluster.",
}
for t in L["terms"]:
    t["plain"] = plain[t["term"]]

S = L["sections"]

S[0]["h"] = "Why platform teams exist"
S[0]["body"] = """List what our app needs by now. Our app, hello-devops, is the tiny web app this course builds: it answers every visit with a greeting and a count of visits so far. For one small app, it carries a lot:
- a Dockerfile and two workflows with pinned actions
- Kubernetes YAML and an Argo CD Application
- a ServiceMonitor, a dashboard, log shipping and tracing
- policies, and a way to get secrets

You learned all of it in this course. Now picture 40 product teams, each building that alone. They solve the same problems 40 times, in 40 slightly different ways, and whoever is on call has to learn every one. Those are the muddy tracks across the lawn.

Most large companies answer this with platform engineering. A platform team builds an internal developer platform (IDP): the self-service tools that product teams use to build, ship and run software. Self-service means you get what you need yourself, at once, without asking anyone. The [CNCF platforms white paper](https://tag-app-delivery.cncf.io/whitepapers/platforms/) puts self-service at the centre. A developer gets an environment, a database or a pipeline without filing a ticket (a written request to another team) and waiting a week.

The team runs the platform as a product, with developers as its customers. In practice, a platform team:
- Talks to its users and watches where they get stuck.
- Publishes a roadmap and takes feature requests.
- Measures success by adoption and speed, never by the number of tools installed.

A classic operations team does work for other teams, through tickets. A platform team builds things so that other teams can do the work themselves. DevOps ideas such as shared ownership and automation still apply, and the platform makes them the easy option. **Build the path people already want to walk. A rule alone won't keep them on it.** So what does that path look like for a new service?"""

S[1]["h"] = "Golden paths, and the map at the park gate"
S[1]["body"] = """The platform's main product is the golden path, which some companies call the paved road. It is a supported, ready-made way to do a common job. "Create a new service" is the classic one. You fill in a name and a team. You get a repository, a project folder with its history. It already holds a Dockerfile, CI, a release workflow, Kubernetes YAML, an Argo CD Application and a dashboard, all wired together. CI is the automatic build and checks on every change.

The [CNCF maturity model](https://github.com/cncf/tag-app-delivery/blob/main/platforms-maturity-model/v1/index.md) describes golden paths as documentation and templates built on compliant and tested patterns. Each of those two words is a promise:
- Compliant: security and policy are built in, so the easy way is also the safe way.
- Tested: the platform team keeps the template working, so a new service starts with current versions.

Teams may still leave the path when they have a good reason. If many teams leave it, the path is wrong, and that is the most useful feedback a platform team gets. In the park, a fresh muddy track beside the paving tells the keeper exactly where a path is missing.

Developers find these paths through a developer portal, a website that is the front door to the platform. Backstage is the best-known framework for building one. It has:
- A software catalog: every service, its owner, its docs and what it depends on.
- Software templates: golden paths you start from a form.
- TechDocs: documentation written in Markdown next to the code.
- Plugins that show CI runs, Kubernetes state, costs and more on each service's page.

Backstage is the map at the park gate. The platform is the paths themselves: the templates, pipelines and clusters behind it. With one repository and one team you do not need a portal at all, because a GitHub template repository does the job. With many teams, though, you need to know whether the paths are helping."""

S[2]["h"] = "Is the platform working? Maturity and developer experience"
S[2]["body"] = """The [CNCF Platform Engineering Maturity Model](https://github.com/cncf/tag-app-delivery/blob/main/platforms-maturity-model/v1/index.md) lets a team check where it stands. It scores five aspects, each on four levels: provisional, operational, scalable and optimizing. Each aspect asks one question, and its levels run from least to most mature:
- Investment, or who builds and pays for it: volunteers, a dedicated team, a product, an enabled ecosystem.
- Adoption, or why teams use it: erratic, pushed by mandate, pulled by teams who want it, teams who contribute.
- Interfaces, or how teams reach it: custom processes, standard tools, self-service, integrated services.
- Operations, or how it is planned and maintained: by request, centrally tracked, centrally enabled, managed services.
- Measurement, or how the team learns what works: ad hoc, consistent collection, insights, numbers plus user feedback.

Score each aspect on its own. The model says no level is good or bad in itself: the right one depends on your teams' goals. You do not need level 4 everywhere, and a CNCF blog post from September 2026 notes that many teams stall at level 2 for interfaces.

Start with the adoption row, because it says the most about whether the platform helps. A platform that teams use because a manager said so sits at level 2. That is the "Keep off the grass" sign. One that teams choose because it is faster sits at level 3.

Developer experience (DevEx) is how it feels to ship software in a company. Measure it with a few plain numbers:
- Time from "new service" to its first production deploy.
- How often a developer waits for another team.
- The DORA metrics from Day 1, for teams on the golden path and off it.

A deploy puts a new version where real users reach it, and the DORA metrics are four numbers on how often and how safely a team ships. Then ask the developers directly, every quarter. At the lowest level of the model, users believe their feedback is not considered, so asking and acting on the answers already moves you up. The paths now have users. Next, they get a bill."""

S[3]["h"] = "FinOps: every cost gets an owner"
S[3]["body"] = """The park pays one water bill, and nobody knows which flower bed drinks the most. The cloud is the same. Any engineer can spend money with one command, and the bill arrives a month later with no names on it. FinOps is the practice of making that cost visible and shared between engineering, finance and the business. The FinOps Foundation, a Linux Foundation project, maintains the [framework](https://www.finops.org/framework/lifecycle/) most teams follow. It loops through three phases, again and again:
1. Inform: see who spends what, and give every cost an owner.
2. Optimize: get the same result for less, through better rates and less waste.
3. Operate: make it routine, with budgets, reviews and alerts.

Everything starts with allocation. Until a cost has an owner, every saving is a guess. In the cloud that means tags (Day 12), name and value notes on each resource. In Kubernetes it means labels, the same kind of note on each object, because many teams share one cluster.

A cost tool gives each Pod a share of its node's price. A Pod is one running copy of an app, and a node is one machine in the cluster. The share is based on the CPU and memory the Pod requests, or uses if that is more. Then the tool adds up the shares by label.

Requests count because the scheduler reserves them (Day 43). A request is the amount a Pod asks to have set aside, and the scheduler is the part of Kubernetes that places Pods on nodes. A node full of requests takes no new Pods, even when its CPUs sit idle. The lab's `policy/require-team-label.yaml` audits that every workload in hello carries a `team` label, like a sign with the gardener's name on every bed.

Then the usual levers, roughly from easy to hard:
- Right-size requests from real usage, since you pay for what you reserve.
- Autoscale Pods and nodes, so quiet hours cost less.
- Turn off what nobody uses: dev environments at night, forgotten test clusters.
- Commit to reserved capacity for steady load, and use spot capacity for work that can restart (Day 12).

My advice for any team: put cost on a dashboard next to latency and errors, and look at it every week. Once every cost has a name, you can show each team its bill."""

S[4]["h"] = "Showback, idle cost and cost per request"
S[4]["body"] = """The FinOps Foundation separates two ways to show each team its bill:
- Showback: each team gets a report of what it used, and the money stays in a central budget.
- Chargeback: the cost moves into each team's own budget in the finance system.

The framework calls showback something every FinOps practice needs, and chargeback a choice that depends on how the company does its accounting. Start with showback. Teams change what they run once they see the numbers next to their own name.

In Kubernetes the report needs one more line: idle cost. Picture sprinklers watering an empty field all night. A node costs the same whether its Pods request 10% of it or 90%, so capacity that nobody requested still appears on the bill. A tool such as OpenCost, a CNCF project, splits the price of each node between workloads. Each one pays for the CPU, memory and GPU it requests or uses, whichever is more, and what is left shows as idle. Give that line an owner too, usually the platform team, or every team argues about it.

Totals grow when the business grows, so they make poor targets. A unit cost works better: cost per request served, per customer, or per build. If traffic doubles and the bill grows by 40%, each request got cheaper, even though the bill went up.

hello-devops already has both inputs. Prometheus, the metrics tool from Day 50, counts requests in `hello_requests_total`, and the `team` label says whose cost it is. Divide one by the other each month, and you have a number a product manager can read. Cost is one thing a path can carry from the start. Safety is the other."""

S[5]["h"] = "Guardrails belong on the golden path"
S[5]["body"] = """A golden path is easy to follow because the platform team already made the hard choices. The park's lights and railings come with the path, and nobody has to install their own. Security and policy belong in that set, built in from the start. For hello-devops, a new service made from the template starts with:
- pinned actions and least-privilege `permissions:` in every workflow (Days 27 and 63)
- a signed image with an SBOM, built by the release workflow
- its own ServiceAccount with no token mounted, and Pods that pass the restricted standard (Day 64)
- the Kyverno policies, including the `team` label that FinOps needs
- a dashboard and alerts for its own metrics

An SBOM is the ingredient list of an image, and a ServiceAccount is an identity for a program. Kyverno is the tool from Day 64 that checks every object against your rules.

The cluster enforces the same rules for everyone, so a team that leaves the path still meets them. Roll policies out in Audit mode first, then Deny, as on Day 64. Budgets work the same way: the platform sends the cost alert, and the owning team receives it.

AI coding agents are one more kind of user of the path, and Days 65 and 66 cover how to use them and fence them in. For a platform team they change one thing. An agent follows AGENTS.md and the template's checks as literally as CI does. A good template produces good agent changes, and a messy one produces mess faster. That leaves the new names you will hear around platforms."""

S[6]["h"] = "Other trends worth a line each"
S[6]["body"] = """You will meet these names in job ads and conference talks:
- eBPF runs small, checked programs inside the Linux kernel, which every packet and system call passes through. [Cilium](https://github.com/cilium/cilium) (Day 60) uses it for Kubernetes networking, observability and security, and can replace kube-proxy.
- [OpenTofu](https://github.com/opentofu/opentofu) is the open source fork of Terraform, made after HashiCorp changed Terraform's license in 2023 (Day 31). The commands are nearly the same: `tofu plan` instead of `terraform plan`.
- WebAssembly (Wasm) runs small, sandboxed programs that start very fast. Envoy, the proxy from Part 15, can load a Wasm plugin without being rebuilt, and some edge platforms run Wasm instead of containers.
- Serverless containers, such as Google Cloud Run, AWS Fargate and Azure Container Apps, run your image with no servers or cluster to manage. For one small service, that is often the simplest place to run it.

The kernel is the core of an operating system, the part that talks to the hardware. A packet is one small piece of network traffic, and a system call is a program's request to the kernel.

A fork is a copy of a project that goes its own way. Sandboxed means shut in, so the program can't touch the rest of the machine.

Every tool in this lesson has a limit, and it is the size of the problem. Each one solves a pain you only feel at a certain scale. Backstage pays off with many teams, not one repository, and a FinOps tool is useless until workloads carry owner labels. Get the basics solid on one real project, then add a tool when you can name the pain it removes. That one real project is what the last lesson builds."""

L["aside"] = {
    "title": "Where did Backstage come from?",
    "body": ("Backstage was created at Spotify for its own engineers, and it is now a CNCF incubating project, so many companies build on it together. "
             "That history explains its shape. It is a framework you assemble with plugins, not a finished product you switch on. "
             "Plan for a team to own it, the way you would own any service."),
    "after": 1,
}

for k in ("analogy", "mistake", "real_world"):
    L.pop(k, None)

L["diagram_caption"] = "A golden path carries its checks and its owner label from the template all the way to the cost report."

W = L["worked"]["steps"]
W[0]["say"] = ("Mark the repository as a template. GitHub then shows a \"Use this template\" button. "
               "Every repository made from it starts with a copy of the files and a fresh history.")
W[1]["say"] = ("Find every file that hard-codes the service name. Each one is a line a new team must change, and the list is the first draft of your template's instructions. "
               "In the course's reference repository, the core folders alone have 27 such files.")
W[2]["say"] = ("Add a catalog file, so a portal such as Backstage can list the service and its owner. "
               "The catalog's `owner` and the Pods' `team` label are the same promise: nothing ships without a name on it. The full file is in Files.")
W[3]["say"] = "Now play the new team. Create a service from the template, and clone it (download your own copy)."
W[4]["say"] = "Replace the old name everywhere, then check that none is left. `sed -i ''` is the macOS form; on Linux, leave out the `''`."
W[5]["say"] = ("Run the same checks as the original, with `ai/check.sh` from Day 65. One fails, and it is a real template bug: sed renamed the chart inside its files, but not its folder. "
               "Fix it, and then fix the template's instructions too, so the next team never meets it. (Output trimmed.)")

T = L["task"]
T["steps"] = [
    "Apply `policy/require-team-label.yaml` and read the PolicyReport in hello. Which workloads have no owner?",
    "Add a `team` label to the Pod template of both Deployments, for example `team: web` for hello-devops and `team: data` for Redis. Commit, push, and let Argo CD sync.",
    "Run the per-team CPU one-liner from Commands and write down what each team requests. Add `no-team` to your list: on kind, that is the system Pods.",
    "Compare requests with real use from `kubectl top pods -n hello` (Day 43). Which workload reserves the most CPU it does not use?",
    "Score your own setup on the five aspects of the CNCF maturity model, from 1 to 4. Pick one aspect and write down one change that would move it up a level.",
    "Optional: add `catalog-info.yaml` from Files to your repository, with your own team as `owner`, and check that it matches the `team` label on your Pods.",
]
T["hints"] = [
    "Labels on the Deployment's own metadata do not reach the Pods. Put `team` under `spec.template.metadata.labels`.",
    "Do not add `team` to the Deployment's `selector`. The selector of an existing Deployment cannot be changed, and it does not need to be.",
    "If `kubectl top` says metrics are not available, install metrics-server as on Day 43.",
]
T["done_when"] = "The PolicyReport in hello shows pass for require-team-label on both Deployments, and your one-liner prints CPU per team."

L["explain_back"]["answer"] = ("A golden path is a supported, ready-made way to do a common job, such as creating a service with CI, signing, deploys, dashboards and policies already wired up. "
                               "Developers use it by themselves, with no ticket, and the platform team keeps it current like a product. "
                               "I know it works when teams choose it because it is faster, so I watch adoption, the time from new service to first deploy, and why teams leave it. "
                               "Every service on the path carries an owner label, so its cost shows up per team in a showback report.")

L["recap"] = [
    "Platform teams turn repeated DevOps work into self-service golden paths, run as a product for developers.",
    "Backstage is a portal framework, the map at the gate. The platform is the templates, pipelines and clusters behind it.",
    "The CNCF maturity model scores investment, adoption, interfaces, operations and measurement, each from 1 to 4.",
    "FinOps loops through inform, optimize and operate, and starts with an owner label on every cost.",
    "Showback comes first: each team sees its own cost, and idle cost gets its own line and an owner.",
    "Limits: portals and cost tools only pay off at scale, so add one when you can name the pain it removes.",
]

C = L["check"]
C[0]["why"] = "A golden path makes the good way the easy way through self-service, without forcing teams onto it."
C[1]["why"] = "Allocation comes first. Until each cost has an owner, every saving is a guess."
C[2]["why"] = "1.4 times the cost for 2 times the requests is 0.7 times the cost per request. The bill grew, and each request got cheaper."

I = L["interview"]
I[0]["a"] = ("Platform engineering builds an internal developer platform that product teams use by themselves: templates, pipelines, environments and observability, offered as golden paths. "
             "A classic operations team often does the work for other teams through tickets. "
             "A platform team treats the platform as a product, talks to its users and measures success by adoption and by how quickly and safely teams ship. "
             "The CNCF maturity model is a useful way to check where a platform stands.")
I[1]["a"] = ("I would start with allocation: every workload gets a team label, enforced first in Audit mode by a policy, and every cloud resource gets an owner tag. "
             "With that, a cost tool can split node costs by the CPU and memory each team requests, and finance and engineers look at the same numbers. "
             "Then I would right-size requests from real usage, add autoscaling, and turn off idle environments. "
             "Cost goes on a dashboard next to latency and errors, and teams review it every week.")
I[2]["a"] = ("I treat the template as a product with its own CI, so every change to it runs the checks a real service would. "
             "Dependabot keeps its pinned actions, base images and chart versions current, and template changes reach existing services as small pull requests that each team reviews. "
             "I let teams change what they need, because a path nobody can adjust gets copied once and then drifts. "
             "And I measure it: time to first deploy, how many teams use it, and why the others left.")

L["deeper"]["body"] = """A GitHub template repository copies files, and the new team does the rest by hand, as in the worked example. A Backstage software template does more in one form. It is a YAML file of kind `Template` (apiVersion `scaffolder.backstage.io/v1beta3`) that asks for parameters, such as the service name and the owning team, and then runs steps:
1. `fetch:template` copies a skeleton folder and fills the parameters into it.
2. `publish:github` creates the repository and pushes the result.
3. `catalog:register` adds the new service's `catalog-info.yaml` to the catalog.

The scaffolder fills in the name only where the template's author put a placeholder. So the worked example's bug becomes a question for the author: does every place that needs the name, folder names included, have one? Test the template the way you tested the copy, by creating a service from it and running every check.

Then find out whether the path helps. The questions worth asking after three months:
- How long does it take from "new service" to the first production deploy, on the path and off it?
- How many teams use the path, and why did the others leave it?
- Do the DORA metrics from Day 1 look better for services on the path?

Watch for two failure modes. If teams cannot change anything in a template, they copy it once and drift away. And templates age: base images, action SHAs and chart versions go stale. Keep the template under CI and Dependabot, so every new service starts current, and send template changes to existing services as pull requests.

Connect the path to cost, too. Every service the template creates gets its owner in two places: `spec.owner` in the catalog and the `team` label on its Pods. Then the showback report and the catalog agree on who owns what, and a cost spike has a team's name next to it on the first day.

Finally, the FinOps framework now reaches beyond public cloud bills, to other "scopes" such as SaaS subscriptions and data centers, under the name Cloud+. The same habits apply there: an owner for every cost, and a number you look at every week."""

L["closing"] = """We started with a muddy lawn and a sign nobody read. The paved path worked because it was the easier way to the station, and that is the whole idea of a golden path. Now hello-devops is a template a new team can start from, with its checks built in and a name on its share of the bill.

Run `kubectl get pods -A -L team` on your cluster. Every empty cell in that column is a bed without a gardener.

Next, we'll walk the whole path once more, end to end, in your capstone. Can one change travel from your laptop to production, through every check in this course, without you touching it by hand?"""

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
print("d67 written")
