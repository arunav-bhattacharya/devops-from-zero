"""p10a first-principles review of Days 38 to 42 (Part 10, Kubernetes).

Takes lessons d38..d42 from brief/scratch/v4/orig/p10.json (identical to content/p10.json for these five),
applies exact old -> new prose replacements, and writes them as a JSON list to brief/scratch/v4/p10a/lessons.json.
It also writes p10.merged.json: the live content/p10.json with these five lessons swapped in, for the checks.
content/p10.json is never written.
Re-run from the repo root: python3 brief/scratch/v4/p10a/edit.py
"""
import copy
import json
import pathlib

ROOT = pathlib.Path("/home/user/devops-from-zero")
SRC = ROOT / "content/p10.json"
ORIG = ROOT / "brief/scratch/v4/orig/p10.json"
OUT = ROOT / "brief/scratch/v4/p10a"
MINE = ["d38", "d39", "d40", "d41", "d42"]

# (lesson id, path to a string field, old, new). Each old must occur exactly once in that field.
E = []


def sec(lid, i, old, new):
    E.append((lid, ("sections", i, "body"), old, new))


# ---------------------------------------------------------------- d38
sec("d38", 0,
    "Compose cannot answer them: it knows one machine, and it only acts when you run it. **Kubernetes** answers every one.",
    "Compose handles a few of these, on one machine. Its restart policy (Day 21) brings a crashed container back, "
    "and its DNS finds services by name. Nothing in it moves work off a dead server, spreads copies over 20 machines "
    "or adds copies when traffic grows. **Kubernetes** answers every one.")
sec("d38", 1,
    "You describe the end state, and Kubernetes stores that description as your **desired state**.",
    "You describe the end state, and Kubernetes stores that description as an object: a record in its database "
    "that says, for example, \"run three copies of `hello-devops:1.0.0`\". What your objects describe is your "
    "**desired state**.")
sec("d38", 1,
    "2. Observe the actual state: what is really running.",
    "2. Observe the actual state: what is really running, as the nodes report it.")
sec("d38", 1,
    "This loop is called reconciliation. The [Kubernetes docs]",
    "This loop is called reconciliation. Say you asked for three copies of hello-devops, and someone deletes one by "
    "mistake. On its next pass the loop reads three wanted, counts two running and starts one more. Nobody wrote a "
    "script for that case. The [Kubernetes docs]")
sec("d38", 1,
    "Controllers work to make status match spec.\n\n",
    "Controllers work to make status match spec.\n\n"
    "Most kinds of object have a controller, sometimes several, whose job is to make objects of that kind come true. "
    "So when you meet a new kind in this part, ask two questions. What does its spec ask for, and which controller "
    "makes that happen? Learn the fields after that: they are the inputs the controller reads.\n\n")
sec("d38", 1,
    "Terraform (Part 8) also compares code with reality, but only when you run `terraform apply`.",
    "Terraform (Part 8) and Ansible (Part 9) also compare code with reality, but only while `terraform apply` or a "
    "playbook runs.")
sec("d38", 2,
    "and they watch it for changes. So any component",
    "and they watch it for changes. A watch is one long-lived request: the API server streams every change down it "
    "as it happens. So any component")
sec("d38", 3,
    "kube-proxy: sets up network rules so traffic sent to a Service reaches the right Pods.",
    "kube-proxy: sets up network rules so traffic sent to a Service (one stable address for a group of Pods) "
    "reaches one of those Pods.")
sec("d38", 3,
    "A Docker image follows the OCI image standard",
    "A Docker image follows the OCI (Open Container Initiative) image standard")
sec("d38", 4,
    "so `kubectl get events` shows the whole chain. The worked example below runs it.",
    "so `kubectl get events` shows the whole chain, and the worked example below runs it. If a step cannot happen, "
    "the chain stops there. A Pod that fits on no node stays `Pending` with no node name, and its events say why "
    "(Day 46 debugs such cases).")
sec("d38", 6,
    "If nodes turn `NotReady` or Pods get evicted, give Docker Desktop more memory in its settings.",
    "If nodes turn `NotReady`, or the kubelet evicts Pods (stops them to free memory), give Docker Desktop more "
    "memory in its settings.")
E.append(("d38", ("worked", "steps", 1, "say"),
          "Find the control plane. In kind its parts run as Pods in the `kube-system` namespace: the API server, etcd, "
          "the scheduler and the controller manager. You also see kube-proxy, CoreDNS and kindnet.",
          "Find the control plane. In kind its parts run as Pods in `kube-system`, a namespace (a named group of "
          "objects, Day 39) kept for the cluster itself. There you find the API server, etcd, the scheduler and the "
          "controller manager, plus kube-proxy, CoreDNS and kindnet."))
E.append(("d38", ("task", "hints", 0),
          "`docker exec <node-container> crictl ps` runs crictl inside a node;",
          "`crictl` is a small command-line client that talks to a node's container runtime through the CRI. "
          "`docker exec <node-container> crictl ps` runs it inside a node;"))

# ---------------------------------------------------------------- d39
sec("d39", 0,
    "Everything in Kubernetes is an object: a Pod, a Service, a Namespace. You describe objects in a manifest, "
    "a YAML file with four top-level fields:\n"
    "- `apiVersion`: which version of the API defines this kind. A Pod is `v1`, a Deployment is `apps/v1`.\n"
    "- `kind`: the type of object, such as `Pod` or `Service`.\n",
    "Day 38 showed the cluster as a store of objects, with controllers that make each one come true. A manifest is "
    "how you write an object down: a YAML file that kubectl sends to the API server. Pods, Services and Namespaces "
    "are all objects, and every manifest has the same four top-level fields:\n"
    "- `apiVersion`: which version of the API defines this kind. The API server checks your fields against it. "
    "A Pod is `v1`, a Deployment is `apps/v1`.\n"
    "- `kind`: the type of object, such as `Pod` or `Service`. It decides which controllers act on it.\n")
sec("d39", 0,
    "- `spec`: your desired state. Its shape depends on the kind.\n\n"
    "You never write the fifth field, `status`. Kubernetes fills it in. ",
    "- `spec`: your desired state, the part the controllers read. Its shape depends on the kind.\n\n"
    "You never write the fifth field, `status`. The controllers and the kubelet write it, to report the actual "
    "state. Any gap between `spec` and `status` is work the cluster has not finished yet.\n\n")
sec("d39", 0,
    "kubectl also catches typos in field names.",
    "kubectl catches typos in field names before anything is stored.")
sec("d39", 1,
    "will show the Pod name.\n\n",
    "will show the Pod name.\n\n"
    "The wrapper matters for helpers that only work right next to the app: a proxy that reaches it on `localhost`, "
    "or a log shipper that reads its files. The Pod keeps such a group together, and the scheduler places the "
    "whole Pod on one node.\n\n")
sec("d39", 1,
    "Pods are disposable. If a node dies, its Pods die with it, and nothing brings a bare Pod back.",
    "Pods are disposable. The kubelet restarts a bare Pod's containers, but no controller counts bare Pods or makes "
    "new ones. If a node dies, its Pods die with it, and nothing brings them back.")
sec("d39", 3,
    "You declare one as an init container with `restartPolicy: Always`, and Kubernetes then:",
    "You declare one as an init container with `restartPolicy: Always`. The init list already starts containers in "
    "order before the app, which is the order a sidecar needs. For an entry with that policy, Kubernetes:")
sec("d39", 4,
    "Deployments find their Pods with selectors, and so do Services and NetworkPolicies (Day 41).\n\n",
    "Deployments find their Pods with selectors, and so do Services and NetworkPolicies (Day 41).\n\n"
    "Names would not work here. Controllers replace Pods all the time, and every replacement gets a new name. "
    "A selector is a question the controller asks again on every pass of its loop: which objects carry these "
    "labels right now?\n\n")
sec("d39", 6,
    "Give it a real tag. With `:latest` or no tag, Kubernetes sets `imagePullPolicy: Always`, tries Docker Hub, "
    "and the Pod ends in `ImagePullBackOff`.",
    "Give it a real tag. A `:latest` tag, or no tag, can point at a different image any day, so Kubernetes sets "
    "`imagePullPolicy: Always` and asks the registry on every start. Your image exists only inside kind, so the "
    "pull from Docker Hub fails and the Pod ends in `ImagePullBackOff`. With any other tag the default is "
    "`IfNotPresent`: use the node's copy if there is one.")
E.append(("d39", ("task", "steps", 1),
          "add `imagePullPolicy: IfNotPresent`, delete `resources: {}` and `status: {}`, and apply it.",
          "add `imagePullPolicy: IfNotPresent`, and delete `resources: {}` and `status: {}` (empty placeholders; "
          "`status` is the cluster's to write). Apply it."))

# ---------------------------------------------------------------- d40
sec("d40", 0,
    "Yesterday's Pod had no guardian.",
    "Yesterday's Pod had no controller watching over it.")
sec("d40", 0,
    "The Deployment does not create Pods itself. It works through a chain:",
    "The Deployment does not create Pods itself. It works through a chain. The Deployment and the ReplicaSet each "
    "have a controller in the controller manager (Day 38), and the kubelet looks after the Pod:")
sec("d40", 0,
    "Delete the Deployment and the garbage collector removes its ReplicaSets and Pods too.",
    "Delete the Deployment, and the garbage collector (one more controller) removes its ReplicaSets and Pods too.")
sec("d40", 0,
    "You will rarely touch ReplicaSets yourself. The Deployment keeps one per version of the template and tells "
    "each one how many Pods to run.",
    "Why two levels? A ReplicaSet knows one template and one number. An update needs the old and the new template "
    "alive at once, so the Deployment keeps one ReplicaSet per version and moves the numbers between them. You will "
    "rarely touch ReplicaSets yourself.\n\n"
    "Read the lab's `deployment.yaml` with that chain in mind. Each part of its `spec` is an input to one of the "
    "loops:\n"
    "- `replicas: 3`: the number the ReplicaSet keeps.\n"
    "- `selector`: how the ReplicaSet finds and counts its Pods, by label.\n"
    "- `strategy`: how fast the Deployment swaps old Pods for new ones.\n"
    "- `template`: the Pod to stamp out, with its own labels and containers.")
sec("d40", 2,
    "- Changing a ConfigMap that the Pods read.",
    "- Changing a ConfigMap (an object of settings) that the Pods read.")
sec("d40", 2,
    "For each new template, the Deployment creates a new ReplicaSet and moves Pods from the old one to the new one.",
    "The Deployment controller spots a new version like this: on each pass, it compares `spec.template` with the "
    "template inside each ReplicaSet it owns. If none matches, it creates a new ReplicaSet and moves Pods from the "
    "old one to the new one.")
sec("d40", 2,
    "run `kubectl diff -k k8s`. If the diff",
    "run `kubectl diff -k k8s`. The `-k k8s` means every file listed in `k8s/kustomization.yaml` (Day 45 explains "
    "Kustomize). If the diff")
sec("d40", 3,
    "Both cannot be 0, or nothing could ever move.",
    "Both cannot be 0, or nothing could ever move. The rounding errs on the safe side: you never lose more Pods "
    "than the percentage says, and even a single replica gets one extra Pod to move with.")
sec("d40", 3,
    "A Service (Day 41) sends requests to every ready Pod",
    "A Service, the stable address in front of the Pods (Day 41), sends requests to every ready Pod")
sec("d40", 4,
    "a URL that the kubelet calls every few seconds.",
    "a URL that the kubelet calls every few seconds. The kubelet writes each result into the Pod's status, and the "
    "controllers read it there before each step.")
sec("d40", 5,
    "Mixing them causes drift. The next",
    "Mixing them causes drift (Day 33): the cluster no longer matches the file. The next")
E.append(("d40", ("worked", "steps", 1, "say"),
          "two new Pods start at once.",
          "two new Pods start at once. One fills the extra slot, and one replaces the old Pod that may go missing."))

# ---------------------------------------------------------------- d41
sec("d41", 0,
    "- Programs on a node, such as the kubelet, can reach every Pod on that node.\n\n",
    "- Programs on a node, such as the kubelet, can reach every Pod on that node.\n\n"
    "That ends the port juggling of Docker. Two Pods on one node can both listen on 8000, because each has its own "
    "address, and nothing needs publishing to the host.\n\n")
sec("d41", 1,
    "2. A controller keeps EndpointSlices up to date. An EndpointSlice lists the IP addresses and ports of the "
    "matching Pods, and marks each one ready or not.\n"
    "3. kube-proxy, on every node, reads both and writes packet rules into the node's Linux kernel.",
    "2. The EndpointSlice controller watches Pods. An EndpointSlice lists the IP addresses and ports of the matching "
    "Pods, and marks each one ready or not. Whenever a Pod comes, goes or changes readiness, the controller updates "
    "the list.\n"
    "3. kube-proxy, on every node, watches both and rewrites packet rules in the node's Linux kernel to match.")
sec("d41", 3,
    "plus a request to a cloud controller for an external load balancer",
    "plus a request to the cloud controller manager (Day 38) for an external load balancer")
sec("d41", 3,
    "StatefulSets need one (Day 44).",
    "StatefulSets, which give each Pod a stable name, need one (Day 44).")
sec("d41", 4,
    "It can run in three modes:\n"
    "- `iptables`: the long-time default, and still kind's default.\n"
    "- `nftables`: the newer kernel firewall, stable since Kubernetes 1.33",
    "It can run in three modes, named after the kernel feature it programs:\n"
    "- `iptables`: Linux's classic packet-filtering rules. The long-time default, and still kind's default.\n"
    "- `nftables`: the newer kernel firewall that replaces iptables, stable since Kubernetes 1.33")
sec("d41", 4,
    "- `ipvs`: deprecated since 1.35.",
    "- `ipvs`: the kernel's built-in load balancer (IP Virtual Server), deprecated since 1.35.")
sec("d41", 4,
    "do the same job with eBPF programs in the kernel.",
    "do the same job with eBPF: small programs loaded into the kernel (Day 60).")
sec("d41", 4,
    "- Balancing happens per connection, not per request. A client",
    "- Balancing happens per connection, not per request. The kernel picks a Pod on a connection's first packet "
    "and remembers it until the connection closes. A client")
sec("d41", 4,
    "A client that keeps a connection open (HTTP keep-alive, gRPC) can talk to one Pod for a long time.",
    "A client that reuses one connection for many requests can talk to one Pod for a long time. HTTP keep-alive "
    "does that, and gRPC, a framework for calls between services over HTTP/2, does it by design.")
sec("d41", 5,
    "each Pod's resolv.conf has a search list. For a Pod",
    "each Pod's resolv.conf has a search list: suffixes the resolver tries, in order, after a short name. For a Pod")
sec("d41", 6,
    "and namespaces do not change that. A NetworkPolicy is a set of firewall rules for the Pods it selects.",
    "and namespaces do not change that. So an attacker who gets into any one Pod can talk straight to Redis or a "
    "database. A NetworkPolicy is a set of firewall rules for the Pods it selects. The object does nothing by "
    "itself: the network plugin watches policies and turns them into packet filters on each node.")
sec("d41", 6,
    "Policies need a network plugin that enforces them. Some plugins accept the objects and silently ignore them.",
    "Not every network plugin enforces policies. Some accept the objects and silently ignore them.")

# ---------------------------------------------------------------- d42
sec("d42", 0,
    "In Kubernetes, settings live in a **ConfigMap**. It is a small object with a `data` section of keys and "
    "string values.",
    "In Kubernetes you could write `env:` values straight into the Deployment. Most teams put them in a "
    "**ConfigMap** instead: a small object with a `data` section of keys and string values. The Deployment then "
    "stays the same in every environment, and only the ConfigMap differs. Several apps can share one, and whole "
    "config files fit too.")
sec("d42", 2,
    "Changing a ConfigMap never restarts anything. What a running Pod sees depends on how it reads the value:",
    "A ConfigMap is only data. No controller acts on it, and the Deployment controller watches its own Pod "
    "template, not the ConfigMaps the template names. The kubelet reads it at two moments: when it starts a "
    "container, to fill in env vars, and on its regular sync, to refresh mounted files. So changing a ConfigMap "
    "never restarts anything. What a running Pod sees depends on how it reads the value:")
sec("d42", 4,
    "- Access rules (RBAC) can allow",
    "- Access rules (RBAC, role-based access control) can allow")
sec("d42", 5,
    "with RBAC (role-based access control, Day 46).",
    "with RBAC (Day 46).")
sec("d42", 5,
    "The best setups use a KMS provider, where a cloud key service holds the real key.",
    "The best setups use a KMS (key management service) provider, such as AWS KMS, which holds the real key "
    "outside the cluster.")
sec("d42", 6,
    "Teams pick one of four patterns:\n",
    "The first two patterns below add a controller to the cluster along with a new kind of object, and the "
    "controller runs the Day 38 loop on it. A controller packaged like that is often called an operator. Teams "
    "pick one of these four:\n")
sec("d42", 6,
    "- SOPS: you encrypt the values inside YAML files with a cloud key or an age key.",
    "- SOPS (Secrets OPerationS): you encrypt the values inside YAML files with a cloud key or an age key "
    "(age is a small file-encryption tool).")
sec("d42", 6,
    "- The Secrets Store CSI Driver: the vault's values are mounted straight into the Pod as files,",
    "- The Secrets Store CSI Driver, a volume plugin (CSI is the Container Storage Interface). It mounts the "
    "vault's values straight into the Pod as files,")


def get(obj, path):
    for k in path:
        obj = obj[k]
    return obj


def put(obj, path, val):
    for k in path[:-1]:
        obj = obj[k]
    obj[path[-1]] = val


def main():
    part = json.loads(SRC.read_text())
    orig = json.loads(ORIG.read_text())
    lessons = {L["id"]: copy.deepcopy(L) for L in orig["lessons"] if L["id"] in MINE}
    n = 0
    for lid, path, old, new in E:
        cur = get(lessons[lid], path)
        c = cur.count(old)
        assert c == 1, f"{lid} {path}: old text found {c} times: {old[:70]!r}"
        put(lessons[lid], path, cur.replace(old, new))
        n += 1
    out = [lessons[i] for i in MINE]
    (OUT / "lessons.json").write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n")
    merged = copy.deepcopy(part)
    merged["lessons"] = [lessons.get(L["id"], L) for L in part["lessons"]]
    (OUT / "p10.merged.json").write_text(json.dumps(merged, ensure_ascii=False, indent=2) + "\n")
    print(f"{n} replacements applied to {', '.join(MINE)}")


if __name__ == "__main__":
    main()
