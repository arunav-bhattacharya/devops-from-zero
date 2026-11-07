#!/usr/bin/env python3
"""Human-writing pass (blog mode) for Part 7, second half: d35 to d38 plus the part-level fields.
Loads content/p7.json, rewrites prose fields only, writes it back. d30 to d34 are never touched.
Each edit is either ("sub", [(old, new), ...]) on one field, where every old string must occur exactly
once, or ("set", new_text). Run it again and it stops with an error, because the old strings are gone."""
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[4]
PATH = ROOT / "content/p7.json"
MINE = {"d35", "d36", "d37", "d38"}


def get_parent(obj, path):
    keys = [int(k) if k.isdigit() else k for k in path.split(".")]
    for k in keys[:-1]:
        obj = obj[k]
    return obj, keys[-1]


def apply(obj, path, edit, where):
    parent, last = get_parent(obj, path)
    old_text = parent[last]
    assert isinstance(old_text, str), f"{where} {path} is not text"
    kind, payload = edit
    if kind == "set":
        new_text = payload
    else:
        new_text = old_text
        for old, new in payload:
            n = new_text.count(old)
            if n != 1:
                sys.exit(f"{where} {path}: expected 1 match, found {n}: {old[:70]!r}")
            new_text = new_text.replace(old, new)
    parent[last] = new_text


S = lambda *pairs: ("sub", list(pairs))
SET = lambda text: ("set", text)

LESSONS = {
    # ------------------------------------------------------------------ d35
    "d35": {
        "guess.why": SET(
            "The kernel throttles the container, so it runs slower but keeps going. "
            "A container gets killed only when it goes over its memory limit."),
        "terms.5.plain": SET("Guaranteed, Burstable or BestEffort; it decides which Pods a node evicts first when it runs short."),
        "terms.7.plain": SET("A rule for planned work, such as a node drain: at most this many of an app's Pods may be down at once."),
        "sections.0.body": S(
            ("Since Day 31, Kubernetes has restarted your containers when their process exits. That covers crashes. "
             "It does not cover an app that is still running but stuck, or one that is up but cannot reach its database.",
             "Since Day 31, Kubernetes has restarted your containers whenever their process exits, so crashes are handled. "
             "An app can also stay up and still be useless: stuck, or running but unable to reach its database."),
            ("hello-devops has two endpoints made for this.", "hello-devops already has two endpoints for this."),
            ("Redis already has one: `k8s/redis.yaml`", "Redis has one already: `k8s/redis.yaml`"),
            ("One surprise: Kubernetes does not run the `HEALTHCHECK` line from your Dockerfile (Part 3). "
             "That line only matters when you run the image with plain Docker. In a cluster, probes take its place.",
             "Kubernetes ignores the `HEALTHCHECK` line in your Dockerfile from Part 3. "
             "That line only matters when you run the image with plain Docker. In a cluster, probes do its job."),
        ),
        "sections.1.body": S(
            ("Every probe has the same four timing settings, and you should be able to read them:",
             "Every probe takes the same four timing settings:"),
            ("Now the trap, which catches many teams. Never make the liveness probe depend on something outside the container, such as a database.",
             "Never make the liveness probe depend on something outside the container, such as a database. Many teams get this wrong."),
            ("Readiness is the right place for dependency checks, because failing it only pauses traffic. Even there, be careful. "
             "If every Pod fails readiness at once, the Service has no endpoints left and users get errors. "
             "That is why the lab's readiness probe",
             "Dependency checks belong in readiness, because failing it only pauses traffic. Readiness has a limit too. "
             "If every Pod fails it at once, the Service has no endpoints left and users get errors. "
             "So the lab's readiness probe"),
            ("Readiness also guards rollouts. On Day 32 a rolling update waited for new Pods to become ready before it removed old ones. That wait is this probe.",
             "Day 32 promised you this probe. A rolling update waits for new Pods to become ready before it removes old ones, and the readiness probe decides when a Pod counts as ready."),
        ),
        "sections.2.body": S(
            ("What happens at the limit depends on the resource, and this trips most people up. CPU time can be handed out in smaller slices, so a container",
             "At the limit, the two resources behave very differently: too much CPU makes you slow, and too much memory gets you killed. "
             "The kernel can share out CPU time in small slices, so a container"),
            ("Kubernetes then shows `OOMKilled` and exit code 137. The 137 means the process got signal 9, SIGKILL (128 + 9).\n\n"
             "A short way to remember it: too much CPU makes you slow, too much memory gets you killed.\n\n",
             "Kubernetes then shows `OOMKilled` and exit code 137, which means the process got signal 9, SIGKILL (128 + 9).\n\n"),
            ("even when the node has idle cores, which shows up as slow responses that are hard to explain.",
             "even when the node has idle cores, and you see that as slow responses that are hard to explain."),
        ),
        "sections.3.body": S(
            ("You will not need either on your laptop. You will meet both at work,",
             "You will not need either on your laptop, but you will meet both at work,"),
        ),
        "sections.4.body": S(
            ("Three more rules. Without a CPU request the HPA cannot compute a percentage, so it does nothing. "
             "The Deployment's `replicas` field fights the HPA on every `kubectl apply`. "
             "The HPA docs suggest removing it; the lab keeps it equal to `minReplicas`, so the two agree when the app is quiet. "
             "And scale to zero exists since Kubernetes 1.37 as a beta, but only for object or external metrics such as a queue length, never for CPU.",
             "Before you trust the HPA, check these:\n"
             "- Without a CPU request on the Pods, it has no percentage to compute, so it does nothing.\n"
             "- The Deployment's `replicas` field fights the HPA on every `kubectl apply`. The HPA docs suggest removing it.\n"
             "- Scale to zero is beta in Kubernetes 1.37, and only for object or external metrics such as queue length.\n\n"
             "The lab keeps `replicas` equal to `minReplicas`, so the two agree when the app is quiet."),
        ),
        "sections.5.body": S(
            ("Those last two modes rest on in-place Pod resize, which became stable in Kubernetes 1.35. "
             "Before it, a Pod's resources were fixed for its whole life. Now you can patch",
             "Those last two modes rest on in-place Pod resize, stable since Kubernetes 1.35. "
             "Before it, a Pod kept the same resources for its whole life. With it, you can patch"),
            ("This works on single Pods. Changing the resources in a Deployment's template still rolls out new Pods, as on Day 32. "
             "Day to day you change the Deployment.",
             "Resize works on single Pods. Changing the resources in a Deployment's template still rolls out new Pods, as on Day 32, "
             "and day to day that is what you do."),
        ),
        "sections.6.body": S(
            ("You already have a taint. kind's control-plane node carries `node-role.kubernetes.io/control-plane:NoSchedule`. "
             "That is why your app Pods only ever land on the two workers.",
             "Your cluster already has a taint. kind's control-plane node carries `node-role.kubernetes.io/control-plane:NoSchedule`, "
             "so your app Pods only ever land on the two workers."),
            ("Last, the PodDisruptionBudget (PDB). Kubernetes splits",
             "A PodDisruptionBudget (PDB) answers a different question: how many Pods may be gone at once. Kubernetes splits"),
            ("A PDB cannot stop a crash. Replicas spread over several nodes are your answer to that.",
             "A PDB cannot stop a crash. For that, spread the replicas over several nodes."),
        ),
        "analogy": S(
            ("Where it breaks: the manager can ask why, while the kubelet only sees pass or fail from one URL.",
             "A real manager would also ask the clerk what is wrong. The kubelet never asks. It only sees whether one URL passed or failed."),
        ),
        "worked.steps.5.say": S(
            ("A Deployment would do this replace for you.", "A Deployment would replace the Pod for you."),
        ),
        "real_world": SET(
            "A checkout service sees traffic climb during sales, so its HPA adds Pods as the load grows. "
            "A PDB lets node upgrades take down only one checkout Pod at a time. "
            "Its CPU and memory requests come from a week of real usage in monitoring, and get reviewed after every big release. "
            "Probe changes go through code review like alert rules, because a bad liveness probe can restart every Pod at once."),
        "interview.1.a": S(
            ("I always set requests and a memory limit, and think twice before adding a CPU limit to a latency-sensitive service.",
             "I always set requests and a memory limit. I am careful with CPU limits on a latency-sensitive service, "
             "because they throttle it even when the node has idle CPU."),
        ),
        "deeper.body": S(
            ("Probes deserve the same care as numbers. Tune them like alerts: a probe acts on its own, often when nobody is watching.",
             "Treat probe settings like alert rules, because a probe acts on its own, often when nobody is watching."),
        ),
    },
    # ------------------------------------------------------------------ d36
    "d36": {
        "sections.0.body": S(
            ("A Service of type LoadBalancer gives you an address, but it works with connections (layer 4). "
             "It never looks at a URL path or a header. For that you need a proxy",
             "A Service of type LoadBalancer gives you an address, but it works with connections (layer 4) "
             "and never looks at a URL path or a header. Routing on those needs a proxy"),
        ),
        "sections.3.body": S(
            ("kind has one catch. The proxy's Service has type LoadBalancer. On a cloud, that creates a real load balancer with an address. "
             "A kind cluster has no cloud, so the Service never gets one. As a result, `kubectl get gateway -n hello` shows PROGRAMMED `False` "
             "with the message \"No addresses have been assigned to the Gateway\". This is expected. The routing behind it works,",
             "The proxy's Service has type LoadBalancer, which gives you one confusing status on kind. "
             "On a cloud, that type creates a real load balancer with an address. A kind cluster has no cloud, so the Service never gets one. "
             "`kubectl get gateway -n hello` then shows PROGRAMMED `False` with the message \"No addresses have been assigned to the Gateway\". "
             "You can ignore it. The routing behind it works,"),
        ),
        "sections.4.body": S(
            ("TLS is set on the Gateway, not on each route.", "You set TLS once, on the Gateway, instead of on each route."),
        ),
        "sections.6.body": S(
            ("Go deeper below to give it one.", "The Go deeper section gives it one."),
        ),
        "analogy": S(
            ("Where it breaks: a receptionist can use judgment, while the proxy follows the most specific matching rule and nothing else.",
             "A human receptionist might bend a rule for a lost visitor. "
             "The proxy has no such judgment: it follows the most specific matching line and nothing else."),
        ),
        "real_world": SET(
            "Several product teams can share one cluster through a single Gateway that the platform team owns, "
            "with TLS certificates renewed by cert-manager. Each team writes HTTPRoutes for its own paths. "
            "On a payments product, a new version of the card service starts at 5% of traffic before anyone moves the weights. "
            "The card database is a managed service outside the cluster; only caches and queues run as StatefulSets."),
        "interview.0.a": S(
            ("On top of that, the Ingress API is frozen", "And the Ingress API is frozen"),
        ),
        "deeper.body": S(
            ("Things that surprise people:\n", "Four things to expect once it runs:\n"),
            ("The traffic side has its own next step. cloud-provider-kind can give the Gateway a real address on your laptop.",
             "On the traffic side, cloud-provider-kind can give the Gateway a real address on your laptop."),
        ),
    },
    # ------------------------------------------------------------------ d37
    "d37": {
        "sections.0.body": S(
            ("hello-devops now has more than ten YAML files. Imagine running it three times, for dev, staging and prod. "
             "Each copy needs a different image tag, replica count and greeting, and prod also wants a disruption budget. "
             "If you copy the folder three times, the copies drift apart.",
             "hello-devops now has more than ten YAML files. Running it for dev, staging and prod means three copies. "
             "Each needs its own image tag, replica count and greeting, and prod also wants a disruption budget. "
             "Copy the folder three times and the copies drift apart."),
            ("Both end the same way. They render ordinary Kubernetes YAML, and the API server never knows which tool made it. "
             "That is also why Argo CD (Day 39) can deploy with either one.",
             "Either way the result is ordinary Kubernetes YAML, and the API server never knows which tool made it. "
             "Argo CD (Day 39) can deploy with either one for the same reason."),
            ("You will use both at work, often in the same cluster. Helm is how most third-party software ships. "
             "Kustomize is a common choice for a team's own services. This lesson builds one of each for hello-devops.",
             "At work you will meet both, often in the same cluster. Most third-party software ships as Helm charts, "
             "and Kustomize is a common choice for a team's own services. Today you build one of each for hello-devops."),
        ),
        "sections.1.body": S(
            ("The chart also has a small trick from the [Helm tips page]", "The chart borrows one trick from the [Helm tips page]"),
        ),
        "sections.2.body": S(
            ("One rule surprises nearly everyone. If you pass any values on `helm upgrade`, Helm starts from the chart's defaults plus only the values you pass now. "
             "Values you passed at install time are dropped.",
             "If you pass any values on `helm upgrade`, Helm starts from the chart's defaults plus only the values you pass now. "
             "The values you passed at install time are dropped, which surprises nearly everyone the first time."),
        ),
        "sections.3.body": S(
            ("A few changes matter to you:", "The changes you will notice:"),
        ),
        "sections.5.body": S(
            ("Kustomize has a layout rule that trips people up. An overlay cannot live inside its base folder. "
             "An overlay at `k8s/overlays/prod` that points at `../../` fails with \"cycle detected\", because the base would contain the overlay. "
             "That is why the lab keeps `overlays/` next to `k8s/`.\n\n"
             "Three commands do the work: `kubectl kustomize overlays/prod` prints the result, "
             "`kubectl diff -k overlays/prod` shows what would change in the cluster, and `kubectl apply -k overlays/prod` applies it.",
             "An overlay cannot live inside its base folder, even though that looks like the natural place for it. "
             "An overlay at `k8s/overlays/prod` that points at `../../` fails with \"cycle detected\", because the base would contain the overlay. "
             "So the lab keeps `overlays/` next to `k8s/`.\n\n"
             "Three commands cover daily use:\n"
             "- `kubectl kustomize overlays/prod` prints the result.\n"
             "- `kubectl diff -k overlays/prod` shows what would change in the cluster.\n"
             "- `kubectl apply -k overlays/prod` applies it."),
        ),
        "sections.6.body": S(
            ("Pick the tool that matches the job:", "Which tool fits depends mostly on whose software it is:"),
            ("Helm. That is how those projects ship, and their values", "Helm. Those projects ship as charts, and their values"),
            ("Each tool has a way to go wrong. Helm templates get hard to read", "Helm templates get hard to read"),
            ("Kustomize gets confusing when an overlay changes half the base; then the base is wrong, and should change instead.",
             "Kustomize gets confusing when an overlay changes half the base. At that point the base is wrong, and it should change instead."),
        ),
        "analogy": S(
            ("Where it breaks: a recipe makes a new cake each time, while `helm upgrade` changes the cake that is already on the table.",
             "The recipe card misses one thing: baking makes a new cake each time, while `helm upgrade` changes the cake already on the table."),
        ),
        "real_world": SET(
            "Third-party tools such as Envoy Gateway and the monitoring stack come in as Helm charts, pinned to exact versions in an OCI registry. "
            "Each in-house service gets one Kustomize base, with overlays for dev, staging and prod. "
            "Promoting a release is then a pull request that changes `newTag` in the next overlay, and Argo CD applies it."),
        "deeper.body": S(
            ("This design has a consequence: Helm only knows what it applied, not what is in the cluster now.",
             "Because Helm works from these records, it knows what it applied but not what is in the cluster now."),
        ),
    },
    # ------------------------------------------------------------------ d38
    "d38": {
        "sections.0.body": S(
            ("Kubernetes punishes that. Many parts react on their own, so a guess",
             "Kubernetes punishes that: many parts react on their own, so a guess"),
            ("Two habits help more than any tool. Change one thing at a time, then watch what happens. And test layers one by one: "
             "`kubectl port-forward pod/<pod>` skips the Service,",
             "Two habits matter more than any tool: change one thing at a time and watch what happens, and test layers one by one. "
             "For example, `kubectl port-forward pod/<pod>` skips the Service,"),
        ),
        "sections.1.body": S(
            ("For `Pending`, the scheduler writes a `FailedScheduling` event, and it pays to read it slowly.",
             "For `Pending`, read the scheduler's `FailedScheduling` event slowly, because it accounts for every node."),
        ),
        "sections.2.body": S(
            ("For that last case, compare the Service's selector (`kubectl describe service`) with the Pods' labels (`kubectl get pods --show-labels`), "
             "and check that `targetPort` is the port the app listens on. This one fools people, because every Pod looks healthy.\n\n"
             "Remember that the STATUS column is a summary kubectl writes for you.",
             "That last case fools people, because every Pod looks healthy. Compare the Service's selector (`kubectl describe service`) "
             "with the Pods' labels (`kubectl get pods --show-labels`), and check that `targetPort` is the port the app listens on.\n\n"
             "The STATUS column is a summary that kubectl writes for you."),
        ),
        "sections.4.body": S(
            ("Sometimes you need to test from inside the cluster. Can this Pod resolve a name, reach a port, see a file?",
             "Some questions can only be answered from inside the cluster: can this Pod resolve a name, reach a port or see a file?"),
            ("That only works if the image has a shell and the tools you need. Small images often do not.",
             "That only works if the image has a shell and the tools you need, and small images often do not."),
            ("That is what `kubectl debug` is for. It adds", "`kubectl debug` gets around that. It adds"),
        ),
        "sections.5.body": S(
            ("Sooner or later you will see `Error from server (Forbidden)`. That is not a bug in your YAML. "
             "The API server understood the request and refused it, because the person or program behind it lacks permission.",
             "`Error from server (Forbidden)` means the API server understood your request and refused it. "
             "Your YAML is fine; the person or program behind the request lacks permission."),
        ),
        "analogy": SET(
            "A good mechanic with a car that will not start checks it in a fixed order. Is there fuel, does the engine turn, "
            "does it keep running, do the wheels get power? Each answer rules out a whole layer, and kubectl get, describe, logs "
            "and events are that checklist for a cluster. The car, at least, sits still while the mechanic works. "
            "Kubernetes keeps restarting things as you look, so read the Events and `--previous` logs before they change."),
        "worked.steps.5.say": S(
            ("Hypothesis confirmed: a typo in the ConfigMap, not a broken Redis and not a network problem.",
             "That confirms it: the ConfigMap has a typo, and Redis and the network are fine."),
        ),
        "mistake": SET(
            "Restarting or deleting the broken Pod to see if it helps throws away the evidence you needed: "
            "the crashed container's logs, its Last State and often the newest Events. "
            "Run describe and `logs --previous` before you delete anything, and write down what you saw."),
        "real_world": SET(
            "A typical on-call runbook starts with this same ladder: get, describe, logs `--previous`, events, endpoints. "
            "In production you often have read-only RBAC, and distroless images have no shell, "
            "so `kubectl debug` with an ephemeral container is the normal way to look inside. "
            "Fixes go through git and Argo CD. A `kubectl patch` in production is for emergencies only, and someone writes it up afterwards."),
        "deeper.body": S(
            ("Five more failures you will meet sooner or later, each with its first check:",
             "Five more failures, each with the first thing to check:"),
            ("At work, two more habits help. Write each incident down: the symptom, the command that showed the cause, the fix.",
             "At work, write each incident down: the symptom, the command that showed the cause, the fix."),
            ("And automate the boring part:", "Automate the boring part too:"),
            ("Finally, know where Kubernetes' own logs live. On kind,", "Kubernetes' own components write logs too. On kind,"),
        ),
    },
}

PART = {
    "intro": SET(
        "Until now hello-devops has run in Docker on one machine. Kubernetes is the system most teams use to run containers "
        "across many machines, and in this part you build a three-node cluster of it on your Mac with kind. "
        "After a look at how the cluster's parts work together, you add one object at a time: Pods, Deployments, Services, "
        "config and Secrets, health checks, traffic, packaging and debugging. All of it runs locally and costs nothing."),
    "quiz.1.why": SET(
        "EndpointSlices list the ready Pods that match the selector. Ready Pods with no endpoints therefore point to a label mismatch."),
    "quiz.7.why": SET(
        "Pods that are ready but absent from the endpoints were never selected, so compare the selector with the Pod labels "
        "(and check the targetPort)."),
    "resources.0.why": SET("The official explanation of every object in this part, from the people who build Kubernetes."),
    "resources.3.why": SET("Covers the same ground as this part with a different teacher, useful when one explanation is not enough."),
    "resources.5.why": SET("Builds a cluster by hand, one component at a time, so you see every moving part."),
    "resources.10.why": SET("Both tools on the same app, side by side, to help you choose."),
}


def main():
    data = json.loads(PATH.read_text())
    for L in data["lessons"]:
        if L["id"] in LESSONS:
            assert L["id"] in MINE
            for path, edit in LESSONS[L["id"]].items():
                apply(L, path, edit, L["id"])
    for path, edit in PART.items():
        assert not path.startswith("lessons")
        apply(data, path, edit, "part")
    with open(PATH, "w") as f:
        json.dump(data, f, ensure_ascii=False, indent=1)
    print("wrote", PATH)


if __name__ == "__main__":
    main()
