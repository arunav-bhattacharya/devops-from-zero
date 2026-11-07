#!/usr/bin/env python3
"""Human-writing pass (blog mode) for p7 lessons d30 to d34 (editor p7a).

Reads the lessons from content/p7.json, rewrites prose fields only, and writes
the five edited lesson objects as a JSON list to brief/scratch/v3/p7a/lessons.json.
It never writes content/p7.json (another editor works on d35 to d38 and the part
fields at the same time; the lead merges).

Each edit is either a full replacement string or a list of (old, new) pairs.
Every old string must occur exactly once in the field, or the script stops.
"""
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[4]
SRC = ROOT / "content/p7.json"
OUT = ROOT / "brief/scratch/v3/p7a/lessons.json"
IDS = ["d30", "d31", "d32", "d33", "d34"]

EDITS = {
    # ------------------------------------------------------------------ d30
    "d30": {
        "sections.0.body": [
            ("Now picture a real product: 40 services, several copies of each, spread over 20 servers.",
             "A real product is bigger: say 40 services, several copies of each, spread over 20 servers."),
            ("Compose cannot answer them. It knows one machine, and it only acts when you run it. **Kubernetes** answers all of them.",
             "Compose cannot answer them: it knows one machine, and it only acts when you run it. **Kubernetes** answers every one."),
            ("The real change is in how you work. You stop logging in to servers and starting things. You write down the result you want, and Kubernetes keeps making it true.",
             "For you, that means no more logging in to servers to start things. You write down the result you want, and Kubernetes keeps making it true."),
        ],
        "sections.1.body": [
            ("Two things follow from this, and both surprise people at first:",
             "The loop has two effects that surprise beginners:"),
        ],
        "sections.2.body": [
            ("One word before we go on. Kubernetes never runs a bare container. It runs Pods. A Pod wraps one container, sometimes a few, and gives it an IP address. Tomorrow is all about Pods.",
             "Kubernetes never runs a bare container. It runs Pods: a Pod wraps one container, sometimes a few, and gives it an IP address. Tomorrow's lesson is all about Pods, and today you only need that much."),
            ("The control plane has four main components. For each one, it helps to ask what breaks if it stops:",
             "The control plane has four main components. Each one is easiest to remember by what breaks when it stops:"),
            ("This design is why a component can crash, restart, read the current state again and carry on as if nothing happened.",
             "So any component can crash, restart, read the current state again and carry on as if nothing happened."),
        ],
        "sections.3.body": [
            ("Every node runs a few programs:", "Each node runs three programs of its own:"),
            ("A cluster also runs a few add-ons as ordinary Pods:", "Two add-ons run as ordinary Pods:"),
            ("One current detail matters if a cluster ever refuses to start. Linux limits",
             "If a cluster ever refuses to start, check cgroups. Linux limits"),
        ],
        "sections.4.body": [
            ("This is the most useful picture to carry around, and a classic interview question. Say you apply a Deployment that asks for two copies of nginx. A Deployment is an object that keeps a set number of Pods running (Day 32 covers it). Here is the chain:",
             "Say you apply a Deployment that asks for two copies of nginx. A Deployment is an object that keeps a set number of Pods running (Day 32 covers it). Interviewers love to ask what happens next, so learn this chain well:"),
            ("Notice who talks to whom. Every arrow goes through the API server, and each component acts on what it sees there. Nobody sends orders to anybody. Each step also leaves a short record called an event, so you can watch the whole chain with `kubectl get events`. The worked example below does exactly that.",
             "Look at who talks to whom: every step goes through the API server. Each component acts on what it finds there, and none sends orders to another. The steps also leave short records called events, so `kubectl get events` shows the whole chain. The worked example below runs it."),
        ],
        "sections.5.body": [
            ("Cloud providers sell managed Kubernetes instead. They run and upgrade the control plane, and you run your apps on the nodes:",
             "Cloud providers sell managed Kubernetes instead: they run and upgrade the control plane, and you run your apps on the nodes. The three you will hear about most:"),
        ],
        "sections.6.body": [
            ("kind has a few limits worth knowing now:", "Three limits of kind will matter soon:"),
            ("Creating the cluster takes a minute or two, and deleting it takes seconds. You can always start fresh.",
             "Creating the cluster takes a minute or two and deleting it takes seconds, so starting fresh is always cheap."),
        ],
        "analogy": (
            "A busy restaurant kitchen runs much like a cluster. Waiters never talk to cooks: they pin order tickets on a rail "
            "(the API server, with etcd as the rail's memory). The head chef reads new tickets and assigns each dish to a station "
            "(the scheduler). Each station cook makes only the dishes assigned to them (the kubelet). A manager keeps checking that "
            "every table got what it ordered, and has dropped plates remade (the controllers). A real kitchen also improvises when "
            "it runs out of something. Kubernetes never does that; it only works toward exactly what the ticket says."
        ),
        "real_world": (
            "A payments company's platform team runs three managed clusters on EKS: dev, staging and production. Product teams "
            "never touch the control plane. When a release misbehaves, the first thing anyone runs is `kubectl get events` in the "
            "team's namespace, because the events say which component gave up and why."
        ),
    },
    # ------------------------------------------------------------------ d31
    "d31": {
        "sections.0.body": [
            ("A typo in a field name does not slip through, either. kubectl validates strictly by default, so",
             "kubectl also catches typos in field names. It validates strictly by default, so"),
            ("YAML has a few traps.", "YAML has traps of its own."),
            ("Kubernetes 1.37 made KYAML stable for exactly this reason. It is a stricter style of YAML",
             "Those traps are the reason for KYAML, which Kubernetes 1.37 made stable. It is a stricter style of YAML"),
        ],
        "sections.1.body": [
            ("Kubernetes never runs a bare container. It runs Pods. A **Pod** is one or more containers that are placed on one node together and share a few things:",
             "A **Pod** is the unit Kubernetes runs: one or more containers that are placed on one node together. They share three things:"),
            ("Most Pods hold exactly one container. Think of the Pod as a thin wrapper that gives your container an address and a place in the cluster. Inside the Pod, the host name is the Pod's name. That is why the `host` field in hello-devops' JSON will show the Pod name.",
             "Most Pods hold exactly one container, and the Pod is then a thin wrapper that gives it an address and a place in the cluster. Inside the Pod, the host name is the Pod's name, so the `host` field in hello-devops' JSON will show the Pod name."),
        ],
        "sections.2.body": [
            ("Most people mix these up at first, so when STATUS looks odd, read `kubectl describe pod`.",
             "When STATUS looks odd, read `kubectl describe pod`, which lists the phase and each container's state separately."),
        ],
        "sections.3.body": [
            ("Sometimes your container needs a helper. Kubernetes has two kinds of extra containers for that.",
             "When your app needs a helper, a Pod can hold two kinds of extra container."),
        ],
        "sections.5.body": [
            ("Think of namespaces as folders, not walls. A Pod in one namespace can still reach a Pod in another over the network, and blocking that takes a NetworkPolicy (Day 33).",
             "Namespaces group names the way folders group files, and they do not isolate the network. A Pod in one namespace can still reach a Pod in another, and blocking that takes a NetworkPolicy (Day 33)."),
            ("Check it before anything risky with `kubectl config current-context`. This matters more than it sounds. Docker Desktop can run its own Kubernetes with a context called `docker-desktop`, and at work you will have contexts for real clusters.",
             "Check it before anything risky with `kubectl config current-context`, because it is not always the cluster you think. Docker Desktop can run its own Kubernetes with a context called `docker-desktop`, and at work you will have contexts for real clusters."),
        ],
        "sections.6.body": [
            ("Most days you need about a dozen kubectl commands. Here they are, grouped by the question they answer:",
             "About a dozen kubectl commands cover most days. Grouped by the question they answer:"),
        ],
        "analogy": (
            "A Pod is like a shared hotel room. Everyone in it has the same room number (one IP address), can use the same desk "
            "(shared volumes) and checks in and out together. The init container is the cleaner who must finish before guests enter, "
            "and the sidecar is the assistant who arrives first and leaves last. Hotel guests can ask for another room, though. "
            "A Pod never moves: Kubernetes throws it away and builds a new one, with a new number."
        ),
        "real_world": (
            "Engineers on a busy team rarely write Pod YAML from scratch. A checkout Pod at a payments company might hold the app, "
            "a native sidecar that ships logs to the central log system, and an init container that waits for the database during "
            "start-up. The team copies a template like that from its repo, checks unknown fields with `kubectl explain`, and diffs "
            "it against `kubectl get -o yaml` when something behaves differently than expected."
        ),
        "deeper.body": [
            ("One more current detail. Kubernetes 1.35 moved finer restart rules to beta.",
             "Kubernetes 1.35 also moved finer restart rules to beta."),
        ],
    },
    # ------------------------------------------------------------------ d32
    "d32": {
        "sections.0.body": [
            ("The names tell the story.", "You can read the chain in the names."),
            ("You will rarely touch ReplicaSets yourself. Think of them as the Deployment's shift supervisors: one per version of the template.",
             "You will rarely touch ReplicaSets yourself. The Deployment keeps one per version of the template and tells each one how many Pods to run."),
        ],
        "sections.1.body": [
            ("A dead node takes longer than most people expect.", "A dead node takes longer than you might expect."),
            ("Handy for pulling a Pod aside to debug it, and confusing if done by accident.",
             "That is handy for pulling a Pod aside to debug it, and confusing when it happens by accident."),
        ],
        "sections.4.body": [
            ("\"Wait until the new Pod is ready\" carries the whole safety of a rolling update. A Pod is ready",
             "A rolling update is safe only because each step waits for a new Pod to be ready. A Pod is ready"),
        ],
        "analogy": (
            "A rolling update is how you would replace a call center's staff during working hours. The supervisor (the Deployment) "
            "hires one new operator, waits until they are trained and taking calls, then sends one old operator home, and repeats "
            "until the whole team is new. If the new hires keep failing training, the old team keeps working. A new operator can "
            "still look up past calls, though, and a new Pod starts with nothing. Anything worth keeping must live outside the Pod, "
            "the way hello-devops keeps its counter in Redis."
        ),
        "real_world": (
            "Card payments cannot stop for a release. So a checkout service might run as a Deployment with 6 replicas spread over "
            "three nodes, `maxUnavailable: 0` and a readiness probe. The CI job runs `kubectl rollout status --timeout=5m` and fails "
            "the release if the rollout stalls. The on-call rule is short: if errors jump after a release, roll back first and "
            "investigate afterwards."
        ),
        "deeper.body": [
            ("A few more fields are worth knowing by name:", "You will also meet three fields by name:"),
        ],
    },
    # ------------------------------------------------------------------ d33
    "d33": {
        "sections.0.body": [
            ("On Day 14 you met Docker networks: containers on one machine, on a private network, with ports published to the host.",
             "The Docker networks of Day 14 put containers on one machine on a private network, with ports published to the host."),
            ("There is a catch. Pod IPs do not last.", "Pod IPs do not last, though."),
            ("So never put a Pod IP in a config file. That is the problem Services solve.",
             "So never put a Pod IP in a config file. Put a Service in front of the Pods instead."),
        ],
        "sections.2.body": [
            ("and mixing them up is the most common Service bug. Here is the lab's Service, from the outside in:",
             "and mixing them up is a very common Service bug. From the outside in, the lab's Service has:"),
        ],
        "sections.3.body": [
            ("LoadBalancer on a laptop needs a note. kind has no cloud,",
             "On a laptop, LoadBalancer is awkward. kind has no cloud,"),
        ],
        "sections.4.body": [
            ("It has a few modes:", "It can run in three modes:"),
            ("A few consequences matter in practice:", "In practice this has three effects:"),
        ],
        "sections.6.body": [
            ("Here is how the rules work. The second one is the one people miss:",
             "The rules are short, and the second one is the one people miss:"),
        ],
        "analogy": (
            "A Service is like a company's main phone number. Callers dial one number and get whichever agent is free. Agents can "
            "join, leave or change desks, and nobody updates a phone book. CoreDNS is the phone book that maps the company name to "
            "that one number, and a NetworkPolicy is the receptionist's list of who may be put through. A good phone system also "
            "sends each call to the least busy agent. kube-proxy cannot: it picks a Pod per connection and does not know how busy "
            "each Pod is."
        ),
        "mistake": (
            "Blaming the network when a Service \"does not work\". Most of the time the selector does not match the Pod labels "
            "exactly, or `targetPort` is not the port the app listens on. Check `kubectl get endpointslices` first: no addresses "
            "means a selector or readiness problem, and addresses that refuse connections mean a port problem."
        ),
        "real_world": (
            "Auditors at a payments company like to see that the database accepts connections only from Pods labeled "
            "`app: payments-api`. A deny-all ingress policy in each team's namespace, plus one allow rule, shows exactly that. "
            "Every app gets a ClusterIP Service, and only the Gateway is exposed outside the cluster. Apps call each other by "
            "`service.namespace` names, so the same config works in dev, staging and production clusters."
        ),
        "deeper.body": [
            ("Most apps never need to touch it. It is worth knowing when someone says DNS in the cluster is slow.",
             "Most apps never need to touch it, but remember it the day someone says DNS in the cluster is slow."),
            ("A second detail: where does the client's IP address go?", "Where does the client's IP address go?"),
            ("A third: Services can be dual-stack,", "Services can also be dual-stack,"),
            ("Finally, the old `Endpoints` object still exists", "The old `Endpoints` object still exists"),
        ],
    },
    # ------------------------------------------------------------------ d34
    "d34": {
        "sections.2.body": [
            ("Most people get this wrong the first time. Changing a ConfigMap never restarts anything, and what a running Pod sees depends on how it reads the value:",
             "Changing a ConfigMap never restarts anything. What a running Pod sees depends on how it reads the value:"),
            ("There is a neater trick that tools use. Put something that changes with the config into the Pod template:",
             "Tools use a neater trick. They put something that changes with the config into the Pod template:"),
        ],
        "sections.3.body": [
            ("This is exactly what Kustomize's hash suffix does for you: every content change is a new, versioned name. For the lab, one plain ConfigMap and `rollout restart` are enough. Know the pattern for when config changes start causing incidents.",
             "Kustomize's hash suffix does this for you: every content change gets a new, versioned name. For the lab, one plain ConfigMap and `rollout restart` are enough. Reach for versioned names once config changes start causing incidents."),
        ],
        "sections.4.body": [
            ("So what is different about a Secret? A few real things:",
             "A Secret does get some protection that a ConfigMap does not:"),
        ],
        "sections.5.body": [
            ("The Kubernetes docs list the steps that actually protect Secrets. Here they are, plus one that people often forget (number 3):",
             "The Kubernetes docs list the steps that actually protect Secrets, and number 3 is the one people often forget:"),
            ("None of this changes one rule. A Secret manifest with real values must never go into git,",
             "Whatever you turn on in the cluster, a Secret manifest with real values must never go into git,"),
        ],
        "sections.6.body": [
            ("Teams pick one of a few patterns:", "Teams pick one of four patterns:"),
        ],
        "analogy": (
            "A ConfigMap read as env vars is like a note in a new employee's locker on their first day. They read it once and never "
            "look again, so a changed note only reaches the next new hire. A mounted file is the notice board in the hallway, which "
            "people see whenever they walk past. A Secret is the same note in an envelope marked confidential. The envelope is not "
            "sealed, which is all base64 gives you. The office picture is too kind in one place, though: in a namespace, anyone "
            "allowed to create Pods can read every Secret, as if anyone allowed to hire staff could open every envelope the team holds."
        ),
        "real_world": (
            "Config should roll back with the code, and database passwords should never touch git. One payments team gets both. "
            "Each service's non-secret settings live in a ConfigMap generated by Kustomize, so every config change rolls the Pods "
            "and can be rolled back with the code. The passwords live in AWS Secrets Manager, External Secrets Operator syncs them "
            "into the cluster every hour, and the clusters have KMS encryption at rest turned on."
        ),
        "deeper.body": [
            ("Secrets have a few more corners worth knowing:", "Three more details about Secrets:"),
            ("Finally, a word on size and count. A Secret, like a ConfigMap,", "A Secret, like a ConfigMap,"),
        ],
    },
}


def walk(obj, path):
    """Return (parent, key) for a dotted path such as 'sections.2.body'."""
    parts = path.split(".")
    for p in parts[:-1]:
        obj = obj[int(p)] if isinstance(obj, list) else obj[p]
    last = parts[-1]
    return obj, (int(last) if isinstance(obj, list) else last)


def main():
    data = json.loads(SRC.read_text())
    lessons = {L["id"]: L for L in data["lessons"]}
    out = []
    for lid in IDS:
        L = json.loads(json.dumps(lessons[lid]))  # deep copy
        for path, edit in EDITS.get(lid, {}).items():
            parent, key = walk(L, path)
            text = parent[key]
            if isinstance(edit, str):
                text = edit
            else:
                for old, new in edit:
                    n = text.count(old)
                    if n != 1:
                        sys.exit(f"{lid} {path}: expected 1 match, found {n}: {old[:60]!r}")
                    text = text.replace(old, new)
            parent[key] = text
        out.append(L)
    OUT.write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n")
    print(f"wrote {OUT} with {len(out)} lessons")


if __name__ == "__main__":
    main()
