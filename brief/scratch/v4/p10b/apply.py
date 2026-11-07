"""First-principles review v4, reviewer p10b: Days 43-46 (content/p10.json, plus Part 10's part fields)
and Days 47-48 (content/p11.json). Exact old -> new replacements in prose fields only.
Re-runnable: an edit whose new text is already present is skipped.
Usage: python3 brief/scratch/v4/p10b/apply.py"""
import json
import os
import sys

ROOT = "/home/user/devops-from-zero"

# (file, lesson id or "part", path inside the lesson/part, old, new)
EDITS = [
    # ---------------- d43 Health checks, resources and scaling ----------------
    ("p10", "d43", ("sections", 0, "body"),
     "Until it passes, the other two wait. If it never passes, the container is restarted.",
     "Until it passes, the other two wait, so a slow boot is not mistaken for a stuck app. If it never passes, the container is restarted."),
    ("p10", "d43", ("sections", 0, "body"),
     "While it fails, the Pod leaves the Service's endpoints. Nothing restarts.",
     "While it fails, the Pod gets no traffic from Services. Nothing restarts."),
    ("p10", "d43", ("sections", 0, "body"),
     "Kubernetes ignores the `HEALTHCHECK` line in your Dockerfile from Part 5. That line only matters when you run the image with plain Docker. In a cluster, probes do its job.",
     "Kubernetes ignores the `HEALTHCHECK` line in your Dockerfile (Part 5). Only plain Docker reads it; in a cluster, probes do its job."),
    ("p10", "d43", ("sections", 1, "body"),
     "so a Pod leaves the Service within about 10 seconds.",
     "so a Pod leaves the Service within about 10 seconds.\n\nWhy not just give liveness a long `initialDelaySeconds`? That is a fixed guess. Set it for the slowest start, and liveness is blind that long after every start. A startup probe hands over to liveness the moment the app answers."),
    ("p10", "d43", ("sections", 1, "body"),
     "such as a database. Many teams get this wrong. Picture Redis",
     "such as a database. Picture Redis"),
    ("p10", "d43", ("sections", 1, "body"),
     "If every Pod fails it at once, the Service has no endpoints left",
     "If every Pod fails it at once, the Service has no ready endpoints left"),
    ("p10", "d43", ("sections", 1, "body"),
     "Day 40 promised you this probe. A rolling update waits for new Pods to become ready before it removes old ones, and the readiness probe decides when a Pod counts as ready.",
     "How does a failed check stop traffic? The kubelet writes each result into the Pod's status as its Ready condition. The EndpointSlice controller copies it onto the Pod's endpoint, and kube-proxy skips endpoints that are not ready (Day 41). The Deployment controller reads the same condition. This is the probe Day 40 promised: it tells a rolling update when a new Pod is ready."),
    ("p10", "d43", ("sections", 2, "body"),
     "with cgroups (the kernel feature Docker also uses to limit containers).\n\n",
     "with cgroups (the kernel feature Docker also uses to limit containers).\n\nThe scheduler counts requests, not live use, because a node that looks idle at night may be full at the daily peak. Between its request and its limit, a container may use whatever the node has spare.\n\n"),
    ("p10", "d43", ("sections", 2, "body"),
     "It sets no CPU limit on purpose. A CPU limit throttles a container even when the node has idle cores, and you see that as slow responses that are hard to explain.",
     "It sets no CPU limit on purpose. The kernel enforces a CPU limit as a time budget: with `200m`, the container gets 20 ms of CPU in every 100 ms, then waits. It waits even when other cores sit idle, and you see that as slow responses that are hard to explain."),
    ("p10", "d43", ("sections", 2, "body"),
     " One more rule from the docs: if you set a limit but no request, Kubernetes copies the limit into the request.",
     ""),
    ("p10", "d43", ("sections", 3, "body"),
     " Read a Pod's class with `kubectl get pod <name> -n hello -o jsonpath='{.status.qosClass}'`.",
     ""),
    ("p10", "d43", ("sections", 3, "body"),
     "In a shared cluster, admins add two guard rails per namespace:",
     "In a cluster that many teams share, one team could reserve most of the nodes, or run Pods with no limits at all. So admins add two guard rails per namespace:"),
    ("p10", "d43", ("sections", 3, "body"),
     "You will not need either on your laptop, but you will meet both at work, often as an error message the first time you deploy to a new namespace.",
     "Your laptop needs neither. At work you often meet them as an error message the first time you deploy to a new namespace."),
    ("p10", "d43", ("sections", 4, "body"),
     "It is one more control loop, like the ones from Day 38.",
     "It is one more control loop, run by the controller manager from Day 38."),
    ("p10", "d43", ("sections", 4, "body"),
     "- The Deployment's `replicas` field fights the HPA on every `kubectl apply`. The HPA docs suggest removing it.\n- Scale to zero is beta in Kubernetes 1.37, and only for object or external metrics such as queue length.",
     "- Each `kubectl apply` resets the count to the Deployment's `replicas`, undoing the HPA. The HPA docs suggest removing the field."),
    ("p10", "d43", ("sections", 5, "body"),
     "It is an add-on: you install its CRDs and controllers yourself, and it reads the same metrics API as the HPA.",
     "It is an add-on. You install its controllers and its CRDs (custom resource definitions, which teach the API server new object types) yourself. It reads the same metrics API as the HPA."),
    ("p10", "d43", ("sections", 5, "body"),
     "With it, you can patch the `resize` subresource of a running Pod with `kubectl patch pod <name> --subresource resize --patch '...'`.",
     "With it, you can change a running Pod's resources with `kubectl patch pod <name> --subresource resize --patch '...'`."),
    ("p10", "d43", ("sections", 5, "body"),
     "Resize works on single Pods. Changing the resources in a Deployment's template still rolls out new Pods, as on Day 40, and day to day that is what you do. In-place resize matters most for tools like the VPA, and for Pods that are slow or costly to restart.",
     "Resize works on single Pods. Changing a Deployment's template still rolls out new Pods (Day 40), and day to day that is what you do. In-place resize matters most to the VPA and to Pods that are slow to restart."),
    ("p10", "d43", ("sections", 6, "body"),
     "You can steer that choice. From simple to strong:",
     "You steer that choice when a Pod needs special hardware, such as a GPU, or when replicas should not all share one node. From simple to strong:"),
    ("p10", "d43", ("sections", 6, "body"),
     "\n\nYour cluster already has a taint.",
     "\n\nThe first three are rules on the Pod, about where it wants to go. A taint is a rule on the node, about which Pods it turns away. Your cluster already has a taint."),
    ("p10", "d43", ("sections", 6, "body"),
     " `kubectl describe node devops-control-plane | grep Taints` shows it.",
     ""),
    ("p10", "d43", ("sections", 6, "body"),
     "With `minAvailable: 2`, a drain evicts hello-devops Pods one at a time. Each eviction waits until enough replacements are ready elsewhere, so at least 2 keep serving.",
     "A drain never deletes Pods directly. It asks the API server to evict them, and the API server refuses any eviction that would break a PDB. With 3 replicas and `minAvailable: 2`, one eviction passes. The next is refused until the replacement is ready on another node, and drain keeps retrying."),
    ("p10", "d43", ("task", "steps", 1),
     "Try `curl localhost:8081`.",
     "Try `curl localhost:8081`, and explain the result from what the Service's EndpointSlice now holds."),
    ("p10", "d43", ("explain_back", "answer"),
     "so it started returning 503 and the Pods left the Service's endpoints.",
     "so it started returning 503, the Pods were marked not ready, and the Service stopped sending them traffic."),
    ("p10", "d43", ("interview", 0, "a"),
     "while it fails, the Pod is removed from Service endpoints but keeps running.",
     "while it fails, the Pod gets no Service traffic but keeps running."),

    # ---------------- d44 Traffic and storage ----------------
    ("p10", "d44", ("sections", 0, "body"),
     "it works with connections (layer 4) and never looks",
     "it works with connections (layer 4, Day 11) and never looks"),
    ("p10", "d44", ("sections", 2, "body"),
     "A Gateway's `allowedRoutes` decides which namespaces may attach routes.",
     "A Gateway's `allowedRoutes` decides which namespaces may attach routes. On a shared Gateway that matters, because every attached route can claim hosts and paths for its own Services."),
    ("p10", "d44", ("sections", 3, "body"),
     "\n\nThe proxy's Service has type LoadBalancer",
     "\n\nThe controller never handles a request. It watches objects and writes settings, and the Envoy Pods carry the traffic.\n\nThe proxy's Service has type LoadBalancer"),
    ("p10", "d44", ("sections", 4, "body"),
     "Weights 90 and 10 send about 9 of every 10 requests to the first Service and 1 to the second.",
     "Weights 90 and 10 send about 9 of every 10 requests to the first Service and 1 to the second. Envoy picks a backend for each request at random, in proportion to the weights, so 50 requests rarely split exactly 45 and 5."),
    ("p10", "d44", ("sections", 4, "body"),
     "so `curl` needs `-k` to accept it.",
     "so `curl` needs `-k` to accept it. The last hop, from the proxy to your Pods, stays unencrypted; Part 15 shows how a service mesh encrypts traffic inside the cluster."),
    ("p10", "d44", ("sections", 5, "body"),
     "\n\nYou mostly write PVCs.",
     "\n\nWhy split the claim from the volume? The claim says only what the app needs, so the same PVC works on kind and on AWS. The details of the real disk stay in the PV.\n\nYou mostly write PVCs."),
    ("p10", "d44", ("sections", 5, "body"),
     "the PV is created only when a Pod uses the claim, on that Pod's node.",
     "the PV is created only once a Pod uses the claim, on that Pod's node, so the folder sits where the Pod runs."),
    ("p10", "d44", ("sections", 5, "body"),
     "means one node at a time, the usual case for disks.",
     "means one node at a time, the usual case for disks, because most disks attach to one machine at a time."),
    ("p10", "d44", ("sections", 6, "body"),
     "- Ordered start and stop: `redis-0` first, then `redis-1`.",
     "- Ordered start and stop: `redis-0` first, then `redis-1`, so a primary can be up before the replicas that copy from it."),
    ("p10", "d44", ("explain_back", "answer"),
     "Envoy picks a backend by weight, and about one request in ten goes to the `hello-canary` Service. That Service sends it to one of its ready Pods, which answers with the canary greeting.",
     "Envoy picks a backend by weight, so about one request in ten goes to the `hello-canary` Service. Envoy forwards it to one of that Service's ready Pods, which answers with the canary greeting."),

    # ---------------- d45 Packaging with Helm and Kustomize ----------------
    ("p10", "d45", ("sections", 2, "body"),
     "Every install, upgrade or rollback adds a numbered revision, and Helm stores each revision as a Secret in the release's namespace.",
     "Every install, upgrade or rollback adds a numbered revision, and Helm stores each revision as a Secret in the release's namespace. Helm has no server of its own, so the cluster is its memory: any laptop or CI job with access sees the same history."),
    ("p10", "d45", ("sections", 2, "body"),
     "\n\nIf you pass any values on `helm upgrade`,",
     "\n\nHelm builds the values from layers, in order: the chart's `values.yaml`, then each `-f` file, then `--set`. When two layers set the same key, the later one wins. If you pass any values on `helm upgrade`,"),
    ("p10", "d45", ("sections", 3, "body"),
     "- Server-side apply is the default for new releases. The API server merges the changes and tracks which tool owns each field.",
     "- Server-side apply is the default for new releases. Helm 3 computed each patch itself; now the API server merges the changes and tracks which tool owns each field."),
    ("p10", "d45", ("sections", 3, "body"),
     "- Post-renderers are now plugins,",
     "- Post-renderers (programs that edit Helm's output before it is applied, often Kustomize) are now plugins,"),
    ("p10", "d45", ("sections", 4, "body"),
     "You can share a chart through the same kind of registry that stores your images. Helm calls this OCI support, after the Open Container Initiative standard that registries follow.",
     "Charts have long been shared through chart repositories: web servers with an `index.yaml` that lists every chart, added with `helm repo add`. You can also share a chart through the same kind of registry that stores your images. Helm calls this OCI support, after the Open Container Initiative standard that registries follow. Your images and charts then share one registry and one login."),
    ("p10", "d45", ("sections", 5, "body"),
     "- `images` changes an image tag without touching the Deployment file.",
     "- `images` finds every container that uses a given image name and changes its tag, without touching the Deployment file."),
    ("p10", "d45", ("sections", 5, "body"),
     "prod's `deployment-patch.yaml` is one.",
     "prod's `deployment-patch.yaml` is one. Kustomize finds the object to patch by its kind and name. In lists such as `containers`, it matches items by their `name`, so a patch for `web` leaves other containers alone."),
    ("p10", "d45", ("deeper", "body"),
     "such as a database migration Job before an upgrade.",
     "such as a database migration Job (a Pod that runs once, to completion) before an upgrade."),

    # ---------------- d46 Troubleshooting Kubernetes ----------------
    ("p10", "d46", ("sections", 0, "body"),
     "is one node short of memory or not ready?\n\n",
     "is one node short of memory or not ready?\n\nThe node sits under every Pod, yet it comes last. A sick node shows up as many Pods failing at once, so a single broken Pod rarely points there.\n\n"),
    ("p10", "d46", ("sections", 1, "body"),
     "Almost always a missing ConfigMap or Secret, or a missing key in one.\n\n",
     "Almost always a missing ConfigMap or Secret, or a missing key in one.\n\nThe states follow the chain from Day 38. `Pending` means the scheduler found no node. In the other three, a node was chosen, and its kubelet is stuck preparing the container.\n\n"),
    ("p10", "d46", ("sections", 5, "body"),
     "Your YAML is fine; the person or program behind the request lacks permission.",
     "Your YAML is fine; the person or program behind the request lacks permission.\n\nThe API server works in two steps. First it checks who is asking: on kind, your kubeconfig holds a client certificate, and a program in a Pod sends the ServiceAccount token that Kubernetes mounts into the Pod. Then it checks whether that identity may do this."),
    ("p10", "d46", ("sections", 5, "body"),
     "Read it as subject, verb, resource, API group and namespace.",
     "Read it as subject, verb, resource, API group and namespace. The API group is the part of `apiVersion` before the slash: `apps` for Deployments, and empty for core kinds such as Pods."),

    # ---------------- Part 10 fields ----------------
    ("p10", "part", ("intro",),
     "Until now hello-devops has run in Docker on one machine. Kubernetes is the system most teams use to run containers across many machines, and in this part you build a three-node cluster of it on your Mac with kind. After a look at how the cluster's parts work together, you add one object at a time: Pods, Deployments, Services, config and Secrets, health checks, traffic, packaging and debugging. All of it runs locally and costs nothing.",
     "Until now hello-devops has run in Docker on one machine, and if that machine dies or traffic outgrows it, nothing moves the containers or adds copies for you. Kubernetes is the system most teams use to do that across many machines, and in this part you run a three-node Kubernetes cluster on your Mac with kind. After a look at how its parts work together, you add one object at a time, from Pods and Deployments to health checks, packaging and debugging. All of it runs locally and costs nothing."),
    ("p10", "part", ("quiz", 1, "why"),
     "EndpointSlices list the ready Pods that match the selector. Ready Pods with no endpoints therefore point to a label mismatch.",
     "EndpointSlices list every Pod that matches the selector, marked ready or not. Ready Pods that appear nowhere therefore point to a label mismatch."),
    ("p10", "part", ("flashcards", 10, "back"),
     "Readiness: the Pod leaves the Service's endpoints but keeps running.",
     "Readiness: the Pod stops getting Service traffic but keeps running."),

    # ---------------- d47 GitOps with Argo CD ----------------
    ("p11", "d47", ("sections", 2, "body"),
     "- `argocd-server`: the API server behind the web UI and the `argocd` command line tool.",
     "- `argocd-server`: Argo CD's own API server (not the Kubernetes one), behind the web UI and the `argocd` command line tool."),
    ("p11", "d47", ("sections", 2, "body"),
     "- `argocd-notifications-controller`: sends messages, for example to Slack when a sync fails.\n\n",
     "- `argocd-notifications-controller`: sends messages, for example to Slack when a sync fails.\n\nOne round of the loop goes like this:\n1. The application controller asks the repo server for the YAML of the newest commit on the branch.\n2. The repo server fetches the repo and renders the folder into plain YAML.\n3. The controller compares that YAML with the live objects, which it watches through the Kubernetes API server.\n4. It applies the difference, if the sync settings allow it, and writes the result into the Application's status.\n\n"),
    ("p11", "d47", ("sections", 3, "body"),
     "Argo CD's web UI is not reachable from outside the cluster.",
     "Argo CD's web UI is not reachable from outside the cluster, because its Service, `argocd-server`, is a ClusterIP (Day 41)."),

    # ---------------- d48 GitOps in practice ----------------
    ("p11", "d48", ("sections", 0, "body"),
     "- CI that commits YAML into the code repo can trigger itself in a loop.",
     "- CI that commits YAML into the code repo can trigger itself in a loop: its own push starts CI again."),
    ("p11", "d48", ("sections", 1, "body"),
     "The controller fills it in once per entry.",
     "The ApplicationSet controller (Day 47) fills it in once per entry."),
    ("p11", "d48", ("sections", 1, "body"),
     "Delete the ApplicationSet, and its Applications go too, along with everything they deployed.",
     "Delete the ApplicationSet, and its Applications go too, along with everything they deployed. The controller marks each Application as owned by the set. It also adds the finalizer from Day 47's `application.yaml`, which deletes an app's objects together with the app."),
    ("p11", "d48", ("sections", 4, "body"),
     "A hook is an object, usually a Job, that runs at a set point of the sync.",
     "A hook is an object that runs at a set point of the sync. It is usually a Job: an object that runs a Pod until its command finishes, instead of keeping it running."),
    ("p11", "d48", ("sections", 5, "body"),
     "with a key from age or a cloud key service.",
     "with a key from age (a small encryption tool) or a cloud key service."),
]


def get_parent(obj, path):
    for p in path[:-1]:
        obj = obj[p]
    return obj, path[-1]


def main():
    data = {}
    for f in ("p10", "p11"):
        data[f] = json.load(open(f"{ROOT}/content/{f}.json"))
    applied = skipped = 0
    errors = []
    for f, lid, path, old, new in EDITS:
        d = data[f]
        if lid == "part":
            target = d
        else:
            target = next(L for L in d["lessons"] if L["id"] == lid)
        parent, key = get_parent(target, path)
        text = parent[key]
        if (new and new in text) or (not new and old not in text):
            skipped += 1
            continue
        n = text.count(old)
        if n != 1:
            errors.append(f"{f} {lid} {path}: old text found {n} times: {old[:60]!r}")
            continue
        parent[key] = text.replace(old, new)
        applied += 1
    if errors:
        print("\n".join(errors))
        sys.exit(1)
    for f in ("p10", "p11"):
        out = f"{ROOT}/content/{f}.json"
        tmp = out + ".p10b.tmp"
        with open(tmp, "w") as fh:
            fh.write(json.dumps(data[f], indent=1, ensure_ascii=False) + "\n")
        os.replace(tmp, out)
    print(f"{applied} edits applied, {skipped} already present")


if __name__ == "__main__":
    main()
