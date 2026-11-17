"""Fifth pass (book voice) for d66, AI agents that run tools. Writer: ti.
Replaces only prose fields of d66 in content/p18.json."""
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[4]
PATH = ROOT / "content/p18.json"
P = json.loads(PATH.read_text())
L = next(x for x in P["lessons"] if x["id"] == "d66")

L["goal"] = ("By the end you can explain how an agent calls tools through MCP, connect a read-only Kubernetes MCP server to kind "
             "with its own identity, run AI review in CI that a person starts, and keep agents that read untrusted text away from write access.")

L["opening"] = """The summer intern has earned some trust. Now you want more than recipe cards: you want them to check the stock, phone suppliers and open up when you are away. So you hand over a ring of keys. On Tuesday a note arrives inside a delivery box: "To whoever unpacks this: please leave the office key under the mat for our driver." A careful person would laugh. A very eager intern might just do it.

That is the trap with helpers who follow written instructions well. The skill that makes them useful is the same skill an attacker can use.

Last time, the assistant only wrote drafts, and we ran every check ourselves. In this lesson, we'll let an agent run tools in the hello-devops cluster, with a key ring that opens only the right doors. Then we'll see why the keys carry the safety, not the agent's judgment. Before we start, make a guess, and keep it in mind."""

L["guess"]["q"] = ("You connect a Kubernetes MCP server (a plug-in that gives an agent tools for your cluster) to your coding agent. "
                   "What decides which actions the agent can really perform in the cluster?")
L["guess"]["why"] = ("MCP only carries requests. The cluster's front desk checks every call against the identity the server signs in as, so RBAC, the access rules, sets the real limit. "
                     "Flags and prompts only narrow what the model is offered.")

plain = {
    "AI agent": "A model in a loop that picks a tool, reads the result and decides the next step until the task is done.",
    "Tool call": "A request from the model, in a fixed format, to run one named tool with given details. The host program runs it, not the model.",
    "Model Context Protocol (MCP)": "An open standard for connecting AI applications to tools and data through small programs called MCP servers.",
    "MCP server": "A program that offers tools, resources and prompts for one system, such as GitHub or a Kubernetes cluster.",
    "MCP host": "The AI application, such as an editor or a terminal agent, that runs one MCP client for each server it uses.",
    "Transport": "How host and server talk: through the server's standard input and output when it runs on your machine, or over the web (Streamable HTTP) when it runs elsewhere.",
    "Prompt injection": "Text inside data the agent reads, such as an issue or a log line, written to give the agent new orders.",
    "Lethal trifecta": "Private data, untrusted content and a way to send data out, all in one agent. Together they let an attacker steal data.",
}
for t in L["terms"]:
    t["plain"] = plain[t["term"]]

S = L["sections"]

S[0]["h"] = "From chat to agent: a model in a loop"
S[0]["body"] = """On Day 65 you ran the checks and pasted the output back. An agent does the running for you. The model inside has not changed, though: it still only produces text. It cannot open a network connection or start `kubectl`, the Kubernetes command-line tool, by itself.

The program around it, called the host, does that part. The host is the agent program you installed, such as Claude Code or Copilot in VS Code. On every call, the host sends the model your goal, the conversation so far and a list of tools. A tool is one action the host can run, described in plain text: a name, a short description and the arguments (details) it takes. Then a loop starts:
1. The model replies with text. To use a tool, it writes a tool call in a fixed format, for example `pods_list_in_namespace` with `namespace: hello`.
2. The host spots the tool call, asks for your approval if needed, and runs the tool with credentials you configured.
3. The host adds the result, as text, to the conversation and calls the model again.
4. When a reply has no tool call in it, that reply is the answer, and the loop stops.

Credentials are the login details a tool uses. In that example, Pods are running copies of an app, and hello is the namespace, the named room in the cluster where hello-devops lives. The model keeps no memory between calls. Each call carries the whole conversation again, tool results included, which is how it knows what it already tried.

Take hello-devops, the tiny web app this course builds: it answers every visit with a greeting and a count of visits so far. Ask why it keeps restarting. A good agent lists the Pods, reads the events, fetches the logs of the restarting container, and explains what it saw. That is the order you learned on Day 46, done in a few seconds.

Three facts follow from this loop:
- The model can only use tools on the list. A tool the host does not offer cannot run.
- A tool can do only what its credentials allow, whatever the model asks for.
- Everything the model reads, tool results included, is text that can steer its next request.

The third one is the note in the delivery box. First, though, where does the tool list come from?"""

S[1]["h"] = "MCP: one plug between agents and tools"
S[1]["body"] = """Picture five agents and four systems, where each pair needs its own glue code (code that joins two programs): twenty pieces. With a shared protocol, a set of rules both sides follow, each agent speaks it once and each system gets one server: nine pieces. The Model Context Protocol (MCP) is the standard most tools now use. The aside below has its short history.

MCP has three roles:
- The host is the AI application: an editor, a terminal agent, a chat app.
- Inside the host, one client talks to each server.
- A server wraps one system and offers what it can do.

A server can offer three kinds of things:
- Tools: functions the model decides to call, such as `pods_log`.
- Resources: data the host decides to read and attach, such as a file or a record.
- Prompts: ready-made templates a person picks, such as "debug this Pod".

This is where the tool list in the loop comes from:
1. Each client asks its server for its tools with a `tools/list` request.
2. The host merges the answers into the one list it sends the model.
3. When the model writes a tool call, the host passes it to the right client, which sends `tools/call`.
4. The server does the real work, such as a request to the Kubernetes API, and returns the result.

The messages are small JSON objects (Go deeper shows one). Two standard transports, the ways host and server talk, carry them:
- stdio: the host starts the server as a child process on your machine and talks over its stdin and stdout (Day 5).
- Streamable HTTP: the server runs elsewhere, behind one HTTPS address, often with OAuth: a browser sign-in that gives the host a token.

A child process is a program that another program starts. A token is a secret string that works like a key card. The specification says plainly that the protocol cannot enforce security. It puts that job on the host, which must get your consent before it runs any tool. The MCP docs add that a local stdio server is ordinary code running as you, with your files and your environment variables in reach. So which servers can you trust, and how do you plug one into kind safely?"""

S[2]["h"] = "Real MCP servers, and a read-only one for kind"
S[2]["body"] = """Four servers you will meet in DevOps work, each from a known publisher:
- GitHub: `github/github-mcp-server`, hosted by GitHub at `https://api.githubcopilot.com/mcp/` or run from its image. It has read-only mode, toolsets and a lockdown mode.
- Kubernetes: `containers/kubernetes-mcp-server`, a Go program that calls the API server directly, with its settings in a TOML file.
- Grafana: `grafana/mcp-grafana`, with a Grafana service account token. `--disable-write` turns off every tool that creates or updates.
- AWS: the AWS MCP Server, run by AWS.

A server is a dependency, code you rely on, so treat it like one. The MCP Registry, still in preview, ties each name to a verified namespace: only GitHub's organization can publish `io.github.github/github-mcp-server`. A search there for `github-mcp-server` also lists servers from other publishers. Find a server through the vendor's docs, pin its version, and read its tool list once.

Now the key ring. The Kubernetes server signs in with whatever kubeconfig its `KUBECONFIG` variable points to, and `.mcp.json` sets that variable. A kubeconfig is the file that holds a cluster login. On kind, the practice cluster on your laptop, your own kubeconfig is cluster-admin, the role that may do everything. The lab never hands it to a server, and builds a narrow setup instead:
1. `policy/ai-agent-readonly.yaml` creates the `ai-agent` ServiceAccount, read-only in hello. `ai/agents/rbac-readonly.yaml` adds Namespaces, Nodes and Pod metrics.
2. `security/agent-kubeconfig.sh 1h` asks the API server for an `ai-agent` token that expires in an hour, and writes a kubeconfig holding only that token.
3. `ai/agents/kubernetes-mcp.toml` sets `read_only = true`, keeps the `core` tools and denies Secrets.
4. `ai/agents/.mcp.json` starts version 0.1.2 with those two files.

A ServiceAccount is a Kubernetes identity for a program. RBAC is the access rules that say what each identity may do (Day 64).

The server's own docs call `read_only` a best-effort guardrail. It hides tools that write, but a read tool still reads whatever the credentials allow. Its node log tools count as read-only and go through `nodes/proxy`, a right Day 64 warned about. The lab's RBAC does not grant it. **A read-only flag hides tools. Only the credentials limit them.** That covers an agent at your desk. In CI, the text it reads comes from strangers."""

S[3]["h"] = "AI review in CI, started by a person"
S[3]["body"] = """CI is the automatic build and checks that run on every change. There, an agent reads text other people wrote: a pull request's changed lines, title and description. A pull request is a proposed change waiting for review. On a public repository, that can be anyone. The same job may hold a paid API key, the secret that lets it use (and pay for) the model. The setup matters more than the model. Today's options fall into three kinds:
- Built in: GitHub Copilot code review. A ruleset can request it on every pull request.
- An action that runs an agent in a job, with your own API key: `anthropics/claude-code-action`, `openai/codex-action` and `google-github-actions/run-gemini-cli`, each published by its vendor.
- GitHub Agentic Workflows: you write the task in Markdown, and `gh aw` compiles it into a normal workflow. Agent jobs are read-only and sandboxed by default, and writes go through separate, checked jobs called safe outputs.

Whichever you pick, a safe workflow has the same shape. The lab's `ai/agents/ai-review.yml` shows it:
- A person adds the label `ai-review`. That needs triage or write access, so no stranger can start a paid run.
- It runs on `pull_request` and skips forks, which get no secrets there anyway (Day 27).
- `permissions: {}` at the top gives every job an empty token, and each job asks for what it needs.
- The review job reads the untrusted diff, so it gets only the API key and `contents: read`, and the agent runs read-only.
- A second job posts the comment with `pull-requests: write`. It never checks out code, runs the model or sees the key.
- Third-party actions are pinned to a full SHA, and a timeout on every job caps what a runaway agent costs.

A fork is a copy of your repository under someone else's account. A SHA is the fingerprint of one exact version of code, so a pinned action cannot change under you.

AI-driven fixes follow the same rule. An agent may push a branch and open a pull request. It never merges, and it never pushes to main. The review stays advisory: branch protection still asks for a human approval and green CI (Day 25). Why so much care about who reads what? Because the text an agent reads can give it orders."""

S[4]["h"] = "Prompt injection: when the data gives orders"
S[4]["body"] = """Remember the note in the delivery box. The loop at the top of this lesson puts every tool result into the model's context as text, right next to your request. So the model reads instructions and data as one stream. It cannot reliably tell "the person I work for said this" from "this was written in an issue I just read". Prompt injection uses that gap. Someone hides orders in data the agent will read:
- an issue, a pull request description or a code comment
- a log line, an error message or a web page
- a tool description, sent by a malicious MCP server

In May 2025 Invariant Labs showed it with the GitHub MCP server. An attacker opened an issue in a public repository with hidden instructions, and a user asked their agent to look at the open issues. The agent's token could also read the user's private repositories. Following the issue, the agent copied private data into a pull request on the public repository.

Simon Willison calls the dangerous mix the lethal trifecta: private data, untrusted content, and a way to send data out. In the GitHub attack, those were the private repositories, the public issue and the public pull request. An agent with all three can be turned against you. Remove one, and that attack stops.

So design as if the agent will be fooled one day:
- An agent that reads untrusted text gets no write access and no secrets.
- A token reaches only the repositories and namespaces the task needs.
- Filters such as the GitHub server's lockdown mode help, but its README calls lockdown a best-effort filter, not an authorization boundary.

**Assume the agent will be fooled one day. Make sure it holds nothing worth stealing.** The ai-review workflow follows these rules: its one way out is a comment that a person reads. Locks and splits are the base, and a few older habits finish the job."""

S[5]["h"] = "A person decides: approvals, sandboxes, incidents and cost"
S[5]["body"] = """The guardrails that matter most are old ones, applied to a new kind of user. `ai/agents/GUARDRAILS.md` lists them as boxes to tick. Beyond identity and read-only access, three more:
- Human approval before every write. Keep your agent's approval prompts on for commands that change things, and route changes through a pull request and Argo CD.
- Sandboxes and allowlists. Run third-party local servers in a container with only the folder they need, and network access only to the hosts they call.
- An audit trail. Keep the agent's transcript, and use the GitHub audit log, Kubernetes audit logs or CloudTrail to see what it really did.

Argo CD is the tool from Part 11 that applies changes from git to the cluster. An allowlist names the only things allowed, and an audit trail is a record of who did what. CloudTrail is AWS's record of every action in your account.

Incidents are a good use, with a clear split. A read-only agent can pull logs, metrics, recent deploys and the runbook together in minutes, and draft a timeline. A person still decides on the rollback, the message to customers and the root cause.

Every call costs tokens, the small pieces of text a model reads and writes, and adds seconds of waiting. One agent question can mean dozens of calls, and each call resends the whole conversation, so later steps cost more. Skip AI where a plain tool is better. `kubectl rollout undo` needs no model, and a linter or a policy beats a model's opinion every time. Put a spending limit on every API key, and a timeout on every CI job.

So far the model has lived on someone else's servers. Sometimes you must run one yourself."""

S[6]["h"] = "Running AI workloads yourself: GPUs on Kubernetes"
S[6]["body"] = """A team may ask you to run a model, not only call one. Inference (running a trained model to answer requests) on Kubernetes is ordinary ops work with an expensive twist: GPUs. A GPU is a graphics chip, the fast and costly hardware that models need.

Kubernetes does not know about GPUs by itself. A device plugin from the vendor runs on each GPU node (a machine in the cluster). It tells the kubelet, the helper on each node, how many GPUs the node has, and connects a GPU to each container that gets one.

NVIDIA's GPU Operator installs the driver, the device plugin and monitoring for you. A container then asks for whole GPUs in `limits`, for example `nvidia.com/gpu: 1`. The scheduler, the part of Kubernetes that picks a node for each Pod, only places the Pod on a node with one free. Sharing one GPU between Pods needs extra vendor features (Go deeper has a newer option). The rest is the scheduling from Day 43:
- Taint the GPU nodes, so only Pods that need a GPU and tolerate the taint land there.
- Label nodes by GPU type, and pick them with node affinity.
- Put GPU nodes in their own autoscaled pool, so the pool can shrink when idle.

A taint is a mark on a node that keeps ordinary Pods away. Node affinity is a Pod's rule for which nodes it prefers. Model servers such as vLLM load the model and expose an HTTP API, and KServe adds a Kubernetes object for a model service.

Autoscaling is harder than for hello-devops. A new replica must load gigabytes of model weights (the learned numbers that make up the model) before it answers. So scaling up can take minutes, and CPU use says little about load. Scale on queue length or requests in flight instead, for example with KEDA (Day 43).

GPU nodes are the most expensive nodes you will run, and an idle GPU costs as much as a busy one. Give them owner labels, watch their use, and expect Day 67's cost reports to start here. Every safeguard in this part had a person reading, checking or approving. The next part asks how a whole team gets those defaults without reading every lesson first."""

L["aside"] = {
    "title": "Who is behind MCP, and how new is all this?",
    "body": ("Anthropic published the Model Context Protocol in November 2024. In December 2025 it gave MCP to the Linux Foundation's Agentic AI Foundation, "
             "so no single company owns it now. The current version of the specification is 2026-07-28, named after its release date. "
             "Big vendors keep arriving: the AWS MCP Server, for example, has been generally available since May 2026. "
             "Expect names and versions to keep moving, and pin what you use."),
    "after": 1,
}

for k in ("analogy", "mistake", "real_world"):
    L.pop(k, None)

L["diagram_caption"] = "The model only asks. The host runs the tool, and the API server checks the agent's token against RBAC."

W = L["worked"]["steps"]
W[0]["say"] = ("Create the agent's identity: the ServiceAccount and Role from `policy/ai-agent-readonly.yaml`, "
               "plus the extra read rights in `ai/agents/rbac-readonly.yaml`. Nothing uses them yet.")
W[1]["say"] = ("Ask the API server what this identity may do, before any tool uses it. "
               "The list is trimmed to the rows that matter: read verbs only, and no Secrets.")
W[2]["say"] = ("Test the doors that must stay shut. A subresource is a part of an object with its own rights, such as a Pod's `exec` (running a command inside it). "
               "For a subresource such as `exec` or `proxy`, pass `--subresource`. "
               "Writing `pods/exec` would ask about a Pod that happens to be named exec, and the answer would mean nothing.")
W[3]["say"] = ("Write a kubeconfig that holds only a one-hour token for this identity, and check who it really is. "
               "Reads work, and the API server itself refuses every write.")
W[4]["say"] = ("Install the server settings and the host config. `.mcp.json` at the repository root is the project file Claude Code reads. "
               "Other agents take the same command, arguments and env in their own settings file, such as `.vscode/mcp.json` for VS Code. "
               "Remove the `github` entry if you have no read-only token for it. Nothing starts yet: the agent launches the server when it needs it.")
W[5]["say"] = ("Start your agent in the repository and ask: \"Which Pods in hello restarted today, and why?\" "
               "Read each tool call before you approve it: a Pod list, events, logs. Then ask it to scale redis to zero. "
               "A read-only server offers no tool for that, and if one slipped through, the API server would refuse it as you saw in step 4.")
W[6]["say"] = ("The kill switch: delete the ServiceAccount, and every token made for it stops working within seconds. "
               "Apply the policy file again when you want the agent back.")

T = L["task"]
T["steps"] = [
    "Start your kind cluster with hello-devops deployed. Apply `policy/ai-agent-readonly.yaml` and `ai/agents/rbac-readonly.yaml`.",
    "Before you test anything, write down five things the agent must never do. Check each one with `kubectl auth can-i ... --as=system:serviceaccount:hello:ai-agent`.",
    "Make the agent kubeconfig with `security/agent-kubeconfig.sh 1h`, copy the TOML file to `~/.config/hello-devops-k8s-mcp.toml`, and put `.mcp.json` at your repository root.",
    "Open the server in the MCP Inspector or in your agent, and read its tool list. Does any tool write? Which read tools will fail because of RBAC?",
    "Delete one hello-devops Pod from your own terminal, then ask the agent what happened to it. Read every tool call before you approve it.",
    "Prompt-injection drill: run the `kubectl annotate` command from Commands, then ask the agent to describe the Deployment. Note what it says and does, and why nothing changes in the cluster.",
    "Pull the kill switch: delete the ServiceAccount and confirm the agent's next call fails. Apply the policy file again afterwards.",
    "Optional: copy `ai/agents/ai-review.yml` to `.github/workflows/`, add the secret, create the label, and label a small pull request.",
]
T["hints"] = [
    "`kubectl auth can-i` takes a subresource as a flag: `--subresource=exec`, not `pods/exec`.",
    "If the agent finds no tools, check the paths in `.mcp.json`: `${HOME}` must expand, and the TOML file must exist where it points.",
    "An annotation is a plain note on an object that Kubernetes ignores. Only a reader that follows instructions in text can be fooled by it.",
]
T["done_when"] = "You are done when the agent explains the deleted Pod from kind, every action on your list returns `no`, and the agent fails right after you delete its ServiceAccount."

L["explain_back"]["answer"] = ("The agent reaches the cluster through a Kubernetes MCP server that the host starts with a separate kubeconfig. "
                               "That kubeconfig holds a one-hour token for the ai-agent ServiceAccount, whose Roles only get, list and watch Pods, logs, events and workloads, never Secrets, exec or nodes/proxy. "
                               "The server's read_only setting hides write tools too, but I rely on RBAC, because a read-only flag does not shrink the credentials. "
                               "Anything the agent reads, such as logs or annotations, may carry injected orders, so it never gets write access. "
                               "Fixes go through a pull request, CI, a person and Argo CD.")

L["recap"] = [
    "An agent is a model in a loop: the model only writes text, the host runs each tool call with the credentials you gave it, and the result comes back.",
    "MCP connects hosts to servers. Servers offer tools, resources and prompts over stdio or Streamable HTTP.",
    "Limits: read-only flags and lockdown filters are best effort. The credentials and their RBAC decide what can really happen.",
    "AI review in CI: a person starts it, the model job only reads, and a separate job writes the comment.",
    "Prompt injection is data that gives orders, so no agent gets private data, untrusted input and a way out together.",
    "GPUs reach Pods through vendor device plugins. Taint GPU nodes, scale inference on queues, and watch idle cost.",
]

C = L["check"]
C[0]["why"] = "A narrow token removes the private-data and write legs of the trifecta. A prompt asking the model to resist injection is not a control."
C[1]["why"] = "pull_request_target runs with the base repository's secrets and token, so checking out untrusted code there hands both to a stranger (Day 27)."
C[2]["why"] = "The model does its work on the GPU, so CPU says little. A queue or in-flight metric follows the real load."

I = L["interview"]
I[0]["a"] = ("The Model Context Protocol is an open standard that connects AI applications, the hosts, to tools and data through MCP servers. "
             "A server wraps one system, such as GitHub, a Kubernetes cluster or Grafana, and offers tools, resources and prompts, over stdio locally or Streamable HTTP remotely. "
             "For DevOps it means one integration per system instead of glue code for every agent. "
             "It also means every server is a new dependency with credentials, so we pin it, give it its own narrow identity and review its tools.")
I[1]["a"] = ("I start from least privilege: its own identity, read-only RBAC or IAM, short-lived tokens, and a kill switch I have tested. "
             "Writes take the same path as human changes: a pull request, CI, policy checks, a human approval, then GitOps. "
             "I treat everything it reads as untrusted because of prompt injection, so an agent that reads issues or logs never also holds write access or secrets. "
             "Third-party servers run sandboxed with a network allowlist, and audit logs show what the agent did.")
I[2]["a"] = ("A person starts it, for example with a label, and it runs on pull_request, so forks get no secrets. "
             "The job that runs the model has only contents: read and the API key, and the agent runs read-only. "
             "A separate job with pull-requests: write posts the result and never runs code from the pull request. "
             "Actions are pinned by SHA, jobs have timeouts, and the review stays advisory: people still approve the merge.")

L["deeper"]["body"] = """First, some details the main text skipped. MCP messages use JSON-RPC 2.0: each small JSON object names a method, such as `tools/call`, and its parameters. The Kubernetes server has read its settings from a TOML file since version 0.0.68. For GPUs, Dynamic Resource Allocation (DRA), stable since Kubernetes 1.34, adds a richer way to request and share devices. KServe is a CNCF incubating project, and the Gateway API Inference Extension lets a Gateway (Day 44) send each request to the model server with the most room.

Now look at what really travels when an agent calls a tool on a remote server. Since the 2026-07-28 version, each request is a plain HTTPS POST that carries everything the server needs. The release post for that version shows one. Its headers say `MCP-Protocol-Version: 2026-07-28`, `Mcp-Method: tools/call` and `Mcp-Name: search`. Its JSON-RPC body names the tool and its arguments.

That design has two results for ops work. First, remote MCP servers scale like any web service. There is no protocol session to keep, so any request can land on any replica behind a round-robin load balancer. You can run one as a normal Deployment with an HPA, as you did for hello-devops.

Second, something in the middle can see every tool call without reading the body. The method and the tool name sit in headers, and the release post says it directly: a gateway, rate limiter or web application firewall can route and meter on them. That gives you a place to log every `tools/call` for `pods_delete`, to rate-limit it, or to block it for every agent in the company at once.

Tools also carry annotations, small hints such as `readOnlyHint` and `destructiveHint`. The Kubernetes server's `read_only = true` works by keeping only the tools marked `readOnlyHint`. The specification warns that annotations are untrusted unless they come from a server you trust. A malicious server can label a delete tool as read-only, which is one more reason the real limit has to sit in the credentials.

Finally, the protocol is still moving. The 2026-07-28 version removed the old start-up handshake and deprecated three features: roots, sampling and logging. It also promises at least twelve months before a deprecated feature is removed. Pin your server versions, read release notes before you upgrade, and keep the specification's changelog on your reading list."""

L["closing"] = """We started with a note in a delivery box asking the intern to leave the office key under the mat. Our agent can read notes like that all day, in issues, logs and annotations. It can't act on them, because its key ring opens only read-only doors, for one hour, and one command takes the ring back.

Check one token or key that an AI tool of yours holds today. Can it write? Can it reach more than the task needs?

Next, we'll step back from single tools. How does a team give every developer safe defaults like these, without each one reading a whole course first?"""

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
print("d66 written")
