"""First-principles review fixes for Days 65-68 (content/p18.json, content/p19.json).
Each fix is an exact old -> new replacement inside one prose field. The script asserts that
every old string occurs exactly once in its field, so it fails loudly instead of guessing.
Run from the repo root on the ORIGINAL files:
  cp brief/scratch/v4/orig/p18.json content/p18.json
  cp brief/scratch/v4/orig/p19.json content/p19.json
  python3 brief/scratch/v4/p18p19/fix.py
"""
import json

FIXES = []


def fix(part, lid, path, old, new):
    FIXES.append((part, lid, path, old, new))


# ---------------------------------------------------------------- Day 65
# S0: why a cutoff date matters, concretely.
fix(18, "d65", ("sections", 0, "body"),
    "It learned from a huge amount of public code and documentation, up to a cutoff date. When it writes",
    "It learned from a huge amount of public code and documentation, up to a cutoff date. It has never seen anything released after that date, such as a flag added last month. When it writes")

# S2: what a server dry run is, and why the loop needs both kinds of check.
fix(18, "d65", ("sections", 2, "body"),
    "which is the mistake models make most often.\n\nChecks prove shape",
    "which is the mistake models make most often.\n\nA server dry run covers what a schema cannot. The object goes to the API server, which runs every check of a real apply, admission included (Day 64), and then throws it away instead of storing it. The trade: kubeconform needs no cluster but knows only the schema, and the dry run needs kind but knows your cluster's rules.\n\nChecks prove shape")

# S3: the mechanism behind "context matters".
fix(18, "d65", ("sections", 3, "body"),
    "The quality of an answer follows the quality of the context. Treat the model",
    "The quality of an answer follows the quality of the context. The model continues the text it sees: with your exact error and versions in it, the likely continuation is about your case. Without them, it falls back on the most common case in its training data, which is often an older version or someone else's setup. Treat the model")

# S3: how an agent uses AGENTS.md (so "keep it short" has a reason).
fix(18, "d65", ("sections", 3, "body"),
    "the rules, and what not to touch. Many tools read it,",
    "the rules, and what not to touch. An agent reads it at the start of each task and adds it to the model's context, as if you had pasted it in. Many tools read it,")

# S4: the model still only writes text; the agent program runs commands, which is why it can ask first.
fix(18, "d65", ("sections", 4, "body"),
    "All of them ask before they run a command or edit a file, unless you switch that off.",
    "The model inside still only writes text. The agent program around it reads that text and runs the commands the model asks for, so it can stop and ask you first. Every tool above does that before it runs a command or edits a file, unless you switch it off.")
fix(18, "d65", ("sections", 4, "body"),
    "Day 66 gives agents tools in your cluster and in CI, and shows how to fence them in.",
    "Day 66 opens up that loop, gives agents tools in your cluster and in CI, and shows how to fence them in.")

# S6: why pasted text leaves the laptop, and why slopsquatting works for an attacker.
fix(18, "d65", ("sections", 6, "body"),
    "Everything you paste into an assistant leaves your laptop.",
    "Most assistants run the model on the vendor's servers, so everything you paste leaves your laptop.")
fix(18, "d65", ("sections", 6, "body"),
    "Agents that read your files raise the same question, so keep secrets outside the repository (Day 64).",
    "Agents that read your files send them to the vendor too, so keep secrets outside the repository (Day 64).")
fix(18, "d65", ("sections", 6, "body"),
    "It found package hallucination to be a systemic and persistent problem.",
    "It found package hallucination to be a systemic and persistent problem. Many invented names also came back when the same question was asked again. That repeatability is what makes the attack work: an attacker can ask the models common questions, note the names they invent, and register them.")

# ---------------------------------------------------------------- Day 66
# S0: build the agent loop from "the model only produces text" before MCP and guardrails.
fix(18, "d66", ("sections", 0, "body"),
    """On Day 65 the assistant wrote text and you ran the checks. An agent runs things itself. The model gets a goal and a list of tools, each with a name, a description and its arguments. Then a loop starts:

1. The model picks a tool and its arguments, for example `pods_list_in_namespace` with `namespace: hello`.
2. The host program, the agent you installed, asks for your approval if needed, then runs the tool.
3. The result goes back into the model's context.
4. The model chooses the next step, or answers.

Ask "why does hello-devops keep restarting?" and a good agent lists the Pods, reads the events, fetches the logs of the restarting container, and explains what it saw. That is the order you learned on Day 46, done in a few seconds.

Notice who does what. The model only writes requests. The host runs them, with credentials you configured. So the question that matters most is what those credentials allow. A model that is wrong, or fooled, can only do what its tools and their credentials let it do.""",
    """On Day 65 you ran the checks and pasted the output back. An agent does the running for you. The model inside has not changed, though: it still only produces text. It cannot open a network connection or start `kubectl` by itself.

The program around it, called the host, does that part: the agent you installed, such as Claude Code or Copilot in VS Code. On every call, the host sends the model your goal, the conversation so far and a list of tools. Each tool is plain text too: a name, a short description and the arguments it takes. Then a loop starts:

1. The model replies with text. To use a tool, it writes a tool call in a fixed format, for example `pods_list_in_namespace` with `namespace: hello`.
2. The host spots the tool call, asks for your approval if needed, and runs the tool with credentials you configured.
3. The host adds the result, as text, to the conversation and calls the model again.
4. When a reply has no tool call in it, that reply is the answer, and the loop stops.

The model keeps no memory between calls. Each call carries the whole conversation again, tool results included, which is how it knows what it already tried.

Ask "why does hello-devops keep restarting?" and a good agent lists the Pods, reads the events, fetches the logs of the restarting container, and explains what it saw. That is the order you learned on Day 46, done in a few seconds.

Three facts follow from this loop:
- The model can only use tools on the list. A tool the host does not offer cannot run.
- A tool can do only what its credentials allow, whatever the model asks for.
- Everything the model reads, tool results included, is text that can steer its next request.""")

# S1: the problem MCP solves in numbers, who controls each primitive, how tools reach the model,
# what JSON-RPC and OAuth are, and the consent rule stated without staging.
fix(18, "d66", ("sections", 1, "body"),
    "Every agent needs tools, and every system needs a way in. Without a standard, each pair needs its own glue code. The",
    "Every agent needs tools, and every system needs a way in. Without a standard, five agents and four systems need twenty pieces of glue code. With a shared protocol, each agent speaks it once and each system gets one server: nine pieces. The")
fix(18, "d66", ("sections", 1, "body"),
    """- Tools: functions the model can call, such as `pods_log`.
- Resources: data the host can read, such as a file or a record.
- Prompts: ready-made templates a person picks, such as "debug this Pod".

Two standard transports carry the messages, which are JSON-RPC 2.0:
- stdio: the host starts the server on your machine and talks to it over standard input and output.
- Streamable HTTP: the server runs elsewhere, behind one HTTPS address, often with OAuth sign-in.

The specification is honest about its limits. The protocol cannot enforce security, so hosts must ask before they run a tool. The MCP docs add a warning worth remembering: a local stdio server""",
    """- Tools: functions the model decides to call, such as `pods_log`.
- Resources: data the host decides to read and attach, such as a file or a record.
- Prompts: ready-made templates a person picks, such as "debug this Pod".

This is where the tool list in the loop comes from:
1. Each client asks its server for its tools with a `tools/list` request.
2. The host merges the answers into the one list it sends the model.
3. When the model writes a tool call, the host passes it to the right client, which sends `tools/call`.
4. The server does the real work, such as a request to the Kubernetes API, and returns the result.

The messages are JSON-RPC 2.0: small JSON objects that name a method, such as `tools/call`, and its parameters. Two standard transports carry them:
- stdio: the host starts the server as a child process on your machine and talks over its stdin and stdout (Day 5).
- Streamable HTTP: the server runs elsewhere, behind one HTTPS address, often with OAuth: a browser sign-in that gives the host a token.

The specification says plainly that the protocol cannot enforce security. It puts that job on the host, which must get your consent before it runs any tool. The MCP docs add that a local stdio server""")

# S2: how the server knows which identity to use, and what the kubeconfig script does.
fix(18, "d66", ("sections", 2, "body"),
    "On kind your own kubeconfig is cluster-admin, so the lab never hands it to a server.",
    "The Kubernetes server signs in with whatever kubeconfig its `KUBECONFIG` variable points to, and `.mcp.json` sets that variable. On kind your own kubeconfig is cluster-admin, so the lab never hands it to a server.")
fix(18, "d66", ("sections", 2, "body"),
    "2. `security/agent-kubeconfig.sh 1h` writes a kubeconfig whose token expires in an hour.",
    "2. `security/agent-kubeconfig.sh 1h` asks the API server for an `ai-agent` token that expires in an hour, and writes a kubeconfig holding only that token.")
fix(18, "d66", ("sections", 2, "body"),
    "go through `nodes/proxy`, which the lab's RBAC does not grant.",
    "go through `nodes/proxy`, a right Day 64 warned about, which the lab's RBAC does not grant.")

# S3: the problem first, and the reason behind each rule of the workflow.
fix(18, "d66", ("sections", 3, "body"),
    "CI is where agents meet other people's text, so the setup matters more than the model.",
    "In CI an agent reads text other people wrote: a pull request's diff, title and description. On a public repository, that can be anyone. The same job may hold a paid API key, so the setup matters more than the model.")
fix(18, "d66", ("sections", 3, "body"),
    """- A person starts it by adding the label `ai-review`, which needs triage or write access.
- It runs on `pull_request`, and skips forks, which get no secrets there anyway.
- `permissions: {}` at the top, then each job asks for what it needs.
- The review job holds the API key and `contents: read`, and the agent runs read-only.
- A second job posts the comment with `pull-requests: write`. It never checks out code or sees the key.
- Third-party actions are pinned to a full SHA, and every job has a timeout.""",
    """- A person adds the label `ai-review`. That needs triage or write access, so no stranger can start a paid run.
- It runs on `pull_request` and skips forks, which get no secrets there anyway (Day 27).
- `permissions: {}` at the top gives every job an empty token, and each job asks for what it needs.
- The review job reads the untrusted diff, so it gets only the API key and `contents: read`, and the agent runs read-only.
- A second job posts the comment with `pull-requests: write`. It never checks out code, runs the model or sees the key.
- Third-party actions are pinned to a full SHA, and a timeout on every job caps what a runaway agent costs.""")

# S4: tie prompt injection to the loop, and map the trifecta onto the real attack.
fix(18, "d66", ("sections", 4, "body"),
    "A model reads instructions and data as one stream of text. It cannot reliably tell",
    "The loop at the top of this lesson puts every tool result into the model's context as text, right next to your request. So the model reads instructions and data as one stream. It cannot reliably tell")
fix(18, "d66", ("sections", 4, "body"),
    "This has happened with real tools. In May 2025",
    "In May 2025")
fix(18, "d66", ("sections", 4, "body"),
    "private data, untrusted content, and a way to send data out. An agent with all three",
    "private data, untrusted content, and a way to send data out. In the GitHub attack, those were the private repositories, the public issue and the public pull request. An agent with all three")
fix(18, "d66", ("sections", 4, "body"),
    "The ai-review workflow follows these rules. Its review job reads untrusted diffs, so it holds only a read token and the model key, and its one way out is a comment that a person reads.",
    "The ai-review workflow follows these rules: its one way out is a comment that a person reads.")

# S5: why agent cost grows with every step.
fix(18, "d66", ("sections", 5, "body"),
    "One agent question can mean dozens of calls.",
    "One agent question can mean dozens of calls, and each call resends the whole conversation, so later steps cost more.")
fix(18, "d66", ("sections", 5, "body"),
    " Observability vendors ship such assistants, Dynatrace among them (Day 62).",
    "")

# S6: what a device plugin actually does, how the scheduler finds a GPU, and how to scale on queues.
fix(18, "d66", ("sections", 6, "body"),
    "A node's GPUs reach Pods through a device plugin from the vendor. NVIDIA's GPU Operator",
    "Kubernetes does not know about GPUs by itself. A device plugin from the vendor runs on each GPU node, tells the kubelet how many GPUs the node has, and connects a GPU to each container that gets one. NVIDIA's GPU Operator")
fix(18, "d66", ("sections", 6, "body"),
    "for example `nvidia.com/gpu: 1`. Sharing",
    "for example `nvidia.com/gpu: 1`, and the scheduler only places the Pod on a node with one free. Sharing")
fix(18, "d66", ("sections", 6, "body"),
    "Scale on queue length or requests in flight instead.",
    "Scale on queue length or requests in flight instead, for example with KEDA (Day 43).")

# Trims to stay under 2,200 words: side details only.
fix(18, "d66", ("sections", 1, "body"),
    "Anthropic published it in November 2024, and in December 2025 gave it to the Agentic AI Foundation, part of the Linux Foundation.",
    "Anthropic published it in November 2024 and gave it to the Linux Foundation's Agentic AI Foundation in December 2025.")
fix(18, "d66", ("sections", 2, "body"),
    "It is on 0.x versions, and since 0.0.68 reads its settings from a TOML file.",
    "Since 0.0.68 it reads its settings from a TOML file.")
fix(18, "d66", ("sections", 3, "body"),
    " It became generally available on 28 October 2026.",
    "")

fix(18, "d66", ("sections", 2, "body"),
    " More servers, such as one for EKS, live in `awslabs/mcp`.",
    "")
fix(18, "d66", ("sections", 5, "body"),
    "Then cost and value. Every call costs tokens,",
    "Every call costs tokens,")

# Recap: the model only writes text, and the credentials are the ones you gave it, not yours.
fix(18, "d66", ("recap", 0),
    "An agent is a model in a loop: it picks a tool, the host runs it with your credentials, and the result comes back.",
    "An agent is a model in a loop: the model only writes text, the host runs each tool call with the credentials you gave it, and the result comes back.")

# ---------------------------------------------------------------- Day 67
# S2: what each maturity aspect asks, and why no level is a target in itself.
fix(19, "d67", ("sections", 2, "body"),
    """It scores five aspects, each on four levels: provisional, operational, scalable and optimizing.
- Investment: from volunteers, to a dedicated team, to a product, to an enabled ecosystem.
- Adoption: from erratic, to pushed by mandate, to pulled by teams who want it, to teams who contribute.
- Interfaces: from custom processes, to standard tools, to self-service, to integrated services.
- Operations: from by request, to centrally tracked, to centrally enabled, to managed services.
- Measurement: from ad hoc, to consistent collection, to insights, to numbers plus user feedback.

Score each aspect on its own. You do not need""",
    """It scores five aspects, each on four levels: provisional, operational, scalable and optimizing. Each aspect asks one question, and its levels run from least to most mature:
- Investment, or who builds and pays for it: volunteers, a dedicated team, a product, an enabled ecosystem.
- Adoption, or why teams use it: erratic, pushed by mandate, pulled by teams who want it, teams who contribute.
- Interfaces, or how teams reach it: custom processes, standard tools, self-service, integrated services.
- Operations, or how it is planned and maintained: by request, centrally tracked, centrally enabled, managed services.
- Measurement, or how the team learns what works: ad hoc, consistent collection, insights, numbers plus user feedback.

Score each aspect on its own. The model says no level is good or bad in itself: the right one depends on your teams' goals. You do not need""")

# S3: how a cost tool splits a node's price (max of request and usage), and why requests count.
fix(19, "d67", ("sections", 3, "body"),
    "A cost tool adds up each Pod's CPU and memory requests and splits the price of the nodes by label.",
    "A cost tool gives each Pod a share of its node's price, based on the CPU and memory it requests, or uses if that is more. Then it adds up the shares by label. Requests count because the scheduler reserves them (Day 43): a node full of requests takes no new Pods, even when its CPUs sit idle.")
fix(19, "d67", ("sections", 3, "body"),
    "- Right-size requests from real usage (Day 43). The scheduler reserves what you request, used or not.",
    "- Right-size requests from real usage, since you pay for what you reserve.")
fix(19, "d67", ("sections", 3, "body"),
    "use spot capacity for work that can restart.",
    "use spot capacity for work that can restart (Day 12).")
fix(19, "d67", ("sections", 3, "body"),
    "The framework now reaches beyond public cloud, through \"scopes\" grouped under the name Cloud+.",
    "The framework now reaches beyond public cloud bills, to other \"scopes\" such as SaaS subscriptions and data centers, under the name Cloud+.")

# S4: fact fix. OpenCost charges max(request, usage), not requests alone (OpenCost spec v0.1).
fix(19, "d67", ("sections", 4, "body"),
    "splits the price of each node by the CPU, memory and GPU each workload requests, and shows what is left as idle.",
    "splits the price of each node between workloads. Each one pays for the CPU, memory and GPU it requests or uses, whichever is more, and what is left shows as idle.")

# S6: why each trend matters, with pointers to the days that taught the basics.
fix(19, "d67", ("sections", 6, "body"),
    "- eBPF runs small, checked programs inside the Linux kernel. [Cilium](https://github.com/cilium/cilium) uses it for Kubernetes networking,",
    "- eBPF runs small, checked programs inside the Linux kernel, which every packet and system call passes through. [Cilium](https://github.com/cilium/cilium) (Day 60) uses it for Kubernetes networking,")
fix(19, "d67", ("sections", 6, "body"),
    "is the open source fork of Terraform (Part 8).",
    "is the open source fork of Terraform, made after HashiCorp changed Terraform's license in 2023 (Day 31).")
fix(19, "d67", ("sections", 6, "body"),
    "- WebAssembly (Wasm) runs small, sandboxed programs that start very fast, as plugins inside other tools or at the edge.",
    "- WebAssembly (Wasm) runs small, sandboxed programs that start very fast. Envoy, for example, can load a Wasm plugin without being rebuilt, and some edge platforms run Wasm instead of containers.")

# ---------------------------------------------------------------- Day 68
# S4: pointer for the supply chain terms.
fix(19, "d68", ("sections", 4, "body"),
    "a keyless signature and SLSA Build L2 provenance.",
    "a keyless signature and SLSA Build L2 provenance (Part 17).")

# S5: expand the exam acronyms once, and say why CKS comes after CKA.
fix(19, "d68", ("sections", 5, "body"),
    "- CKAD (Application Developer):",
    "- CKAD (Certified Kubernetes Application Developer):")
fix(19, "d68", ("sections", 5, "body"),
    "- CKA (Administrator):",
    "- CKA (Certified Kubernetes Administrator):")
fix(19, "d68", ("sections", 5, "body"),
    "- CKS (Security Specialist): supply chain security is 20%, which is Part 17.",
    "- CKS (Certified Kubernetes Security Specialist): supply chain security is 20%, which is Part 17. You need a passed CKA to take it.")
fix(19, "d68", ("sections", 5, "body"),
    "- Newer exams match later parts:",
    "- Newer associate exams (the final A means Associate) match later parts:")

# S6: expand KCSA.
fix(19, "d68", ("sections", 6, "body"),
    "security (KCSA, then CKS after CKA).",
    "security (KCSA, the Kubernetes and Cloud Native Security Associate, then CKS after CKA).")


def get(obj, path):
    for p in path:
        obj = obj[p]
    return obj


def put(obj, path, value):
    for p in path[:-1]:
        obj = obj[p]
    obj[path[-1]] = value


def main():
    parts = {}
    for part in sorted({f[0] for f in FIXES}):
        parts[part] = json.load(open(f"content/p{part}.json"))
    for part, lid, path, old, new in FIXES:
        L = next(x for x in parts[part]["lessons"] if x["id"] == lid)
        cur = get(L, path)
        n = cur.count(old)
        assert n == 1, f"p{part} {lid} {path}: expected 1 match, found {n}: {old[:70]!r}"
        put(L, path, cur.replace(old, new))
    for part, d in parts.items():
        with open(f"content/p{part}.json", "w") as f:
            f.write(json.dumps(d, indent=1, ensure_ascii=False) + "\n")
    print(f"applied {len(FIXES)} fixes")


if __name__ == "__main__":
    main()
