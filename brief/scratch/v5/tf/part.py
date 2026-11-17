"""Rewrite Part 10's own prose fields (intro, recap, flashcards, quiz q/why, resource why)."""
import json
import pathlib

PART = pathlib.Path(__file__).resolve().parents[4] / "content/p10.json"
d = json.loads(PART.read_text())

d["intro"] = "Until now hello-devops has run in Docker on one machine. If that machine dies, or visitors outgrow it, nothing moves the containers or adds copies for you. Kubernetes is the system most teams use to do that across many machines, much like a restaurant manager who keeps every table staffed whoever calls in sick. In this part you run a three-node cluster on your Mac with kind, see how its parts work together, then add one object at a time: Pods, Deployments, Services, settings, health checks, storage, packaging and debugging. All of it runs locally and costs nothing."

d["recap"] = [
    "Kubernetes stores what you asked for and runs control loops that keep the cluster matching it.",
    "Every part talks only to the API server: etcd stores the state, the scheduler places Pods, kubelets run them.",
    "A Pod is one or more containers with one IP address; Deployments create, replace and roll out Pods through ReplicaSets.",
    "Services give changing Pods a fixed name and address, and NetworkPolicies decide who may connect.",
    "ConfigMaps and Secrets keep settings out of the image; environment variables need a restart, and base64 is not encryption.",
    "Probes decide when to wait, restart or stop traffic; requests place Pods and drive the HPA, and memory over the limit means OOMKilled.",
    "The Gateway API (GatewayClass, Gateway, HTTPRoute) replaces the frozen Ingress API; ingress-nginx was retired in March 2026.",
    "PVCs ask for storage, StorageClasses create it, and StatefulSets give each replica a fixed name and its own disk.",
    "Helm packages an app as a chart with values and numbered releases; Kustomize builds each environment as an overlay on a plain base.",
    "Debug bottom-up with get, describe, logs `--previous`, events and EndpointSlices; Forbidden means RBAC, checked with `kubectl auth can-i`.",
]

cards = [
    ("What does a Kubernetes controller do?", "It compares what you asked for with what really runs, again and again, and acts to close the gap."),
    ("Which part of the cluster is the only one that talks to etcd?", "The API server."),
    ("A Pod stays Pending with no node assigned. Which part should have acted?", "The scheduler."),
    ("Label or annotation: which one do selectors use?", "Labels. Annotations are notes for people and tools."),
    ("How do you declare a native sidecar container?", "As an init container with `restartPolicy: Always`."),
    ("Which Deployment changes create a new revision?", "Only changes to the Pod template, `spec.template`. Scaling does not."),
    ("In a NodePort Service, what are port, targetPort and nodePort?", "port is the Service's port, targetPort is the Pod's port, nodePort is opened on every node."),
    ("What is the DNS name of Service `redis` in namespace `hello`?", "`redis.hello.svc.cluster.local` (or just `redis` from inside `hello`)."),
    ("You changed a ConfigMap that Pods read through envFrom. What else must you do?", "Restart the Pods, for example with `kubectl rollout restart deployment/NAME`."),
    ("Does base64 protect a Secret?", "No. Anyone can decode it; encryption at rest and RBAC protect Secrets."),
    ("What happens when a readiness probe fails? And a liveness probe?", "Readiness: the Pod stops getting Service traffic but keeps running. Liveness: the kubelet restarts the container."),
    ("A container shows OOMKilled and exit code 137. What happened?", "It used more memory than its limit, so Linux killed it with SIGKILL (128 + 9)."),
    ("What happens to a container at its CPU limit?", "It is throttled: it keeps running, only slower. It is not killed."),
    ("What two things does a CPU-based HPA need?", "metrics-server (with `--kubelet-insecure-tls` on kind) and CPU requests on the Pods."),
    ("What does a PodDisruptionBudget protect against, and what not?", "It limits planned disruptions such as `kubectl drain`; it cannot stop a node crash."),
    ("Name the three main Gateway API objects and who usually owns each.", "GatewayClass (platform team), Gateway (cluster operators), HTTPRoute (app teams)."),
    ("What does kind's `standard` StorageClass do when you delete a PVC?", "Its reclaim policy is Delete, so the PV and the data folder are deleted too."),
    ("What does `helm rollback app 1` write into the history?", "A new revision with the content of revision 1, described as \"Rollback to 1\"."),
    ("Why can a Kustomize overlay not live inside its base folder?", "Kustomize refuses it as a cycle: the base would contain the overlay."),
    ("A Pod is in CreateContainerConfigError and its logs are empty. Where do you look?", "In the Events of `kubectl describe pod`: usually a missing ConfigMap, Secret or key."),
]
assert len(cards) == len(d["flashcards"])
for f, (front, back) in zip(d["flashcards"], cards):
    f["front"], f["back"] = front, back

quiz = [
    ("On Day 21, Docker Compose ran hello-devops and Redis on your laptop. Which job can Kubernetes do that Compose cannot?",
     "Compose knows one machine. Kubernetes controllers notice lost Pods, and the scheduler places replacements on healthy nodes."),
    ("A Service's Pods are Running and Ready, but `kubectl get endpointslices` for it lists no addresses. What is the most likely cause?",
     "EndpointSlices list every Pod that matches the selector, marked ready or not. Ready Pods that appear nowhere therefore point to a label mismatch."),
    ("A setup step must finish before the app starts, and both need the same files. What fits best?",
     "Init containers run to the end before app containers start, and an emptyDir volume lets them hand files to the app."),
    ("You roll out a new image, then run `kubectl rollout undo`. Which revision number does the restored version get?",
     "An undo copies the old template back as a new rollout, so the old revision comes back under the next number."),
    ("A teammate pushed a Secret manifest with base64 values to a shared repo. What should happen first?",
     "Base64 is readable and Git keeps history, so treat the values as public and change them."),
    ("An HPA targets 70m CPU per Pod (70% of a 100m request). 4 Pods now average 105m. How many replicas will it ask for, if `maxReplicas` is 10?",
     "ceil(4 * 105 / 70) = ceil(6.0) = 6."),
    ("You want 20% of requests to reach a new version of the checkout service, through the existing Gateway. Which object do you change?",
     "Splitting traffic is a routing rule, so it lives in the HTTPRoute as weighted backends."),
    ("On your kind cluster, a Pod for `hello-devops:0.1.0`, an image you built on your laptop, shows `ErrImagePull` and then `ImagePullBackOff`. `docker images` lists that exact tag. What is the most likely fix?",
     "A kind node is a container with its own image store, so an image on your laptop is not on the node until you load it. The container never started, so there are no logs to read."),
    ("Your team installs Envoy Gateway and a monitoring stack, and also deploys its own small service to dev and prod. Which split fits best?",
     "Outside projects ship and support Helm charts, while overlays keep a team's own few differences as plain, readable YAML."),
    ("Helm stores every revision of a release in the cluster, so it can show history and roll back. Which part of Terraform plays the same role of remembering what was deployed?",
     "Terraform's state records what it created, just as Helm's release Secrets record what each revision applied."),
]
assert len(quiz) == len(d["quiz"])
for q, (qq, why) in zip(d["quiz"], quiz):
    q["q"], q["why"] = qq, why

whys = {
    "Kubernetes documentation: concepts": "The official explanation of every object in this part, from the people who build Kubernetes.",
    "kind quick start": "How to create local clusters, load images into them and delete them, which you do all through this part.",
    "kubectl quick reference": "A one-page list of kubectl commands to keep open while you work.",
    "Kubernetes tutorial for beginners, full course (KubeAcademy)": "The same ground as this part with a different teacher, useful when one explanation is not enough.",
    "Kubernetes Services explained (TechWorld with Nana)": "A clear walk through Service types, selectors and ports, the part people mix up most.",
    "Kubernetes The Hard Way (Kelsey Hightower)": "Builds a cluster by hand, one part at a time, so you see every moving piece.",
    "Debug Pods (Kubernetes docs)": "The official checklist for Pods that will not start or keep crashing, with example output.",
    "A visual guide on troubleshooting Kubernetes deployments (Learnkube)": "One big flowchart from Pod to Service to Ingress that you can keep open while debugging.",
    "Gateway API project site": "Guides for every route type, the Standard and Experimental channels, and a list of implementations.",
    "Helm 4 overview": "What changed from Helm 3, including server-side apply and the renamed flags you will meet in old scripts.",
    "Helm vs Kustomize: the fight between templating and patching (DevOps Toolkit)": "Both tools on the same app, side by side, to help you choose.",
    "7 common Kubernetes pitfalls (Kubernetes blog)": "Missing requests, bad probes and loose access rules, each with what to do instead.",
}
for r in d["resources"]:
    r["why"] = whys[r["title"]]

PART.write_text(json.dumps(d, indent=1, ensure_ascii=False) + "\n")
print("part fields patched")
