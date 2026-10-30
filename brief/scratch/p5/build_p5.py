#!/usr/bin/env python3
"""Build content/p5.json (Part 5: Kubernetes) for "DevOps, from zero".
Run: python3 brief/scratch/p5/build_p5.py   (from anywhere)"""
import json
import pathlib
import re
import textwrap

ROOT = pathlib.Path(__file__).resolve().parents[3]
LAB = ROOT / "labs/hello-devops"
OUT = ROOT / "content/p5.json"


def T(s):
    """Dedent and strip a multi-line text block."""
    return textwrap.dedent(s).strip("\n")


def lab(path):
    return (LAB / path).read_text().rstrip("\n")


def R(title, url, kind="docs"):
    return {"title": title, "url": url, "kind": kind}


# ---------------------------------------------------------------- links (all opened or found in search in this task)
K = "https://kubernetes.io/docs/"
L = {
    "overview": R("Kubernetes overview", K + "concepts/overview/"),
    "nana": R("Kubernetes tutorial for beginners (TechWorld with Nana)", "https://www.youtube.com/watch?v=X48VuDVv0do", "watch"),
    "controller": R("Controllers", K + "concepts/architecture/controller/"),
    "components": R("Kubernetes components", K + "concepts/overview/components/"),
    "architecture": R("Cluster architecture", K + "concepts/architecture/"),
    "pods": R("Pods", K + "concepts/workloads/pods/"),
    "objects": R("Objects in Kubernetes", K + "concepts/overview/working-with-objects/"),
    "kubectl": R("kubectl quick reference", K + "reference/kubectl/quick-reference/"),
    "pf": R("Use port forwarding to access applications in a cluster", K + "tasks/access-application-cluster/port-forward-access-application-cluster/"),
    "eks": R("What is Amazon EKS?", "https://docs.aws.amazon.com/eks/latest/userguide/what-is-eks.html"),
    "aks": R("What is Azure Kubernetes Service (AKS)?", "https://learn.microsoft.com/en-us/azure/aks/what-is-aks"),
    "gke": R("GKE overview", "https://docs.cloud.google.com/kubernetes-engine/docs/concepts/kubernetes-engine-overview"),
    "kind_qs": R("kind quick start", "https://kind.sigs.k8s.io/docs/user/quick-start/"),
    "kind_cfg": R("kind configuration (port mappings)", "https://kind.sigs.k8s.io/docs/user/configuration/"),
    "kind_issues": R("kind known issues", "https://kind.sigs.k8s.io/docs/user/known-issues/"),
    "deploy": R("Deployments", K + "concepts/workloads/controllers/deployment/"),
    "rolling": R("Update a Deployment without downtime", K + "tasks/run-application/update-deployment-rolling/"),
    "labels": R("Labels and selectors", K + "concepts/overview/working-with-objects/labels/"),
    "service": R("Service", K + "concepts/services-networking/service/"),
    "dns": R("DNS for Services and Pods", K + "concepts/services-networking/dns-pod-service/"),
    "ns": R("Namespaces", K + "concepts/overview/working-with-objects/namespaces/"),
    "pf_ref": R("kubectl port-forward", K + "reference/kubectl/generated/kubectl_port-forward/"),
    "cm": R("Configure a Pod to use a ConfigMap", K + "tasks/configure-pod-container/configure-pod-configmap/"),
    "secret": R("Secrets", K + "concepts/configuration/secret/"),
    "secret_gp": R("Good practices for Kubernetes Secrets", K + "concepts/security/secrets-good-practices/"),
    "encrypt": R("Encrypting confidential data at rest", K + "tasks/administer-cluster/encrypt-data/"),
    "probes_task": R("Configure liveness, readiness and startup probes", K + "tasks/configure-pod-container/configure-liveness-readiness-startup-probes/"),
    "probes": R("Liveness, readiness, and startup probes", K + "concepts/configuration/liveness-readiness-startup-probes/"),
    "resources": R("Resource management for Pods and containers", K + "concepts/configuration/manage-resources-containers/"),
    "hpa": R("Horizontal Pod autoscaling", K + "concepts/workloads/autoscaling/horizontal-pod-autoscale/"),
    "metrics": R("metrics-server (GitHub)", "https://github.com/kubernetes-sigs/metrics-server"),
    "debug": R("Debug Pods", K + "tasks/debug/debug-application/debug-pods/"),
    "lifecycle": R("Pod lifecycle", K + "concepts/workloads/pods/pod-lifecycle/"),
    "ingress": R("Ingress", K + "concepts/services-networking/ingress/"),
    "retire": R("Ingress NGINX retirement: what you need to know", "https://kubernetes.io/blog/2025/11/11/ingress-nginx-retirement/", "read"),
    "ingress_nginx": R("ingress-nginx repository (archived)", "https://github.com/kubernetes/ingress-nginx"),
    "i2g": R("Announcing Ingress2Gateway 1.0", "https://kubernetes.io/blog/2026/03/20/ingress2gateway-1-0-release", "read"),
    "gateway": R("Gateway API", K + "concepts/services-networking/gateway/"),
    "gwapi": R("Gateway API project site", "https://gateway-api.sigs.k8s.io/"),
    "eg_qs": R("Envoy Gateway quickstart", "https://gateway.envoyproxy.io/docs/tasks/quickstart/"),
    "eg_helm": R("Install Envoy Gateway with Helm", "https://gateway.envoyproxy.io/docs/install/install-helm/"),
    "pv": R("Persistent volumes", K + "concepts/storage/persistent-volumes/"),
    "sc": R("Storage classes", K + "concepts/storage/storage-classes/"),
    "sts": R("StatefulSets", K + "concepts/workloads/controllers/statefulset/"),
    "using_helm": R("Using Helm", "https://helm.sh/docs/intro/using_helm/"),
    "helm4": R("Helm 4 overview", "https://helm.sh/docs/overview/"),
    "helm_video": R("What is Helm in Kubernetes? Helm and Helm charts explained", "https://www.youtube.com/watch?v=-ykwb1d0DXU", "watch"),
    "helm_tpl": R("Helm chart template guide: getting started", "https://helm.sh/docs/chart_template_guide/getting_started/"),
    "helm_tips": R("Helm chart development tips and tricks", "https://helm.sh/docs/howto/charts_tips_and_tricks/"),
    "kustomize": R("Declarative management of Kubernetes objects using Kustomize", K + "tasks/manage-kubernetes-objects/kustomization/"),
}


def src(*keys):
    return [{"title": L[k]["title"], "url": L[k]["url"]} for k in keys]


# ---------------------------------------------------------------- diagrams
SVG_HEAD = '<svg viewBox="0 0 560 {h}" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="{label}">'


def box(cls, x, y, w, h, label, size=13):
    tcls = "t" if cls == "bx" else "tk"
    return (f'<rect class="{cls}" x="{x}" y="{y}" width="{w}" height="{h}" rx="10"/>'
            f'<text class="{tcls}" x="{x + w // 2}" y="{y + h // 2 + 5}" font-size="{size}" text-anchor="middle">{label}</text>')


def cap(x, y, label):
    return f'<text class="ts" x="{x}" y="{y}" font-size="11" text-anchor="middle">{label}</text>'


def line(x1, y1, x2, y2, dashed=False, arrow=True):
    cls = "lnd" if dashed else "ln"
    m = ' marker-end="url(#ar)"' if arrow else ""
    return f'<line class="{cls}" x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}"{m}/>'


def svg(h, label, parts):
    return SVG_HEAD.format(h=h, label=label) + "".join(parts) + "</svg>"


D16 = svg(300, "How kubectl apply flows from the API server to a Pod on a worker node", [
    box("bx", 16, 36, 116, 44, "kubectl"),
    box("bxo", 172, 36, 116, 44, "API server"),
    box("bxg", 328, 36, 112, 44, "etcd"),
    cap(500, 62, "Control plane"),
    box("bxp", 16, 132, 116, 44, "Scheduler"),
    box("bxp", 328, 132, 112, 44, "Controllers"),
    box("bxt", 172, 236, 116, 44, "kubelet"),
    box("bxt", 328, 236, 112, 44, "containerd"),
    box("bx", 472, 236, 72, 44, "Pod"),
    cap(74, 262, "Worker node"),
    line(132, 58, 170, 58),
    line(288, 58, 326, 58),
    line(110, 132, 190, 82, dashed=True),
    line(350, 132, 270, 82, dashed=True),
    line(230, 80, 230, 234, dashed=True),
    line(288, 258, 326, 258),
    line(440, 258, 470, 258),
])

D17 = svg(256, "A Service spreads traffic over three Pods that a Deployment and its ReplicaSet keep running", [
    box("bx", 16, 106, 96, 44, "Your Mac"),
    box("bxo", 148, 106, 112, 44, "Service"),
    cap(204, 170, "NodePort 30080"),
    box("bxt", 300, 36, 96, 44, "Pod 1"),
    box("bxt", 300, 106, 96, 44, "Pod 2"),
    box("bxt", 300, 176, 96, 44, "Pod 3"),
    cap(348, 242, "app=hello-devops"),
    box("bxg", 432, 36, 112, 44, "Deployment"),
    box("bxp", 432, 106, 112, 44, "ReplicaSet"),
    cap(488, 170, "keeps 3 Pods"),
    line(112, 128, 146, 128),
    line(260, 128, 298, 60),
    line(260, 128, 298, 128),
    line(260, 128, 298, 196),
    line(488, 80, 488, 104),
    line(432, 128, 398, 60, dashed=True),
    line(432, 128, 398, 128, dashed=True),
    line(432, 128, 398, 196, dashed=True),
])

D18 = svg(212, "The kubelet runs two probes: a failed liveness probe restarts the container, a failed readiness probe stops Service traffic", [
    box("bxt", 16, 88, 96, 44, "kubelet"),
    box("bx", 152, 28, 128, 44, "GET /healthz"),
    cap(216, 92, "liveness"),
    box("bx", 152, 148, 128, 44, "GET /readyz"),
    cap(216, 140, "readiness"),
    box("bxo", 368, 28, 176, 44, "Restart container"),
    box("bxp", 368, 148, 176, 44, "No Service traffic"),
    line(112, 100, 150, 54),
    line(112, 120, 150, 166),
    line(280, 50, 366, 50),
    cap(323, 42, "3 misses"),
    line(280, 170, 366, 170),
    cap(323, 162, "2 misses"),
])

D19 = svg(216, "Gateway API on kind: requests go through the Envoy proxy to the Service and Pods, configured by GatewayClass, Gateway and HTTPRoute", [
    box("bxp", 16, 24, 120, 44, "GatewayClass"),
    box("bxp", 168, 24, 120, 44, "Gateway"),
    box("bxg", 320, 24, 104, 44, "HTTPRoute"),
    box("bx", 16, 140, 120, 44, "Your Mac"),
    box("bxo", 168, 140, 120, 44, "Envoy proxy"),
    box("bxt", 320, 140, 104, 44, "Service"),
    box("bxt", 448, 140, 96, 44, "Pods"),
    cap(76, 204, "port-forward 8888"),
    cap(258, 108, "creates"),
    cap(404, 108, "routes to"),
    line(136, 46, 166, 46, dashed=True),
    line(320, 46, 290, 46, dashed=True),
    line(228, 68, 228, 138, dashed=True),
    line(372, 68, 372, 138, dashed=True),
    line(136, 162, 166, 162),
    line(288, 162, 318, 162),
    line(424, 162, 446, 162),
])


def check_svg(name, s):
    """Rough layout check: rects inside the canvas, no rect overlaps, captions clear of rects."""
    h = int(re.search(r'viewBox="0 0 560 (\d+)"', s).group(1))
    rects = [tuple(map(int, m)) for m in re.findall(r'<rect class="\w+" x="(\d+)" y="(\d+)" width="(\d+)" height="(\d+)"', s)]
    for x, y, w, hh in rects:
        assert x >= 8 and y >= 8 and x + w <= 552 and y + hh <= h - 8, (name, "rect near edge", x, y, w, hh)
    for i, a in enumerate(rects):
        for b in rects[i + 1:]:
            if a[0] < b[0] + b[2] + 12 and b[0] < a[0] + a[2] + 12 and a[1] < b[1] + b[3] + 12 and b[1] < a[1] + a[3] + 12:
                raise AssertionError((name, "rects too close", a, b))
    # labels inside boxes must fit: width >= 8 * chars + 24
    for m in re.finditer(r'<rect class="\w+" x="\d+" y="\d+" width="(\d+)" height="\d+" rx="10"/><text class="\w+" x="\d+" y="\d+" font-size="13" text-anchor="middle">([^<]+)</text>', s):
        assert int(m.group(1)) >= 8 * len(m.group(2)) + 24, (name, "box too narrow for", m.group(2))
    for m in re.finditer(r'<text class="ts" x="(\d+)" y="(\d+)" font-size="11" text-anchor="middle">([^<]+)</text>', s):
        cx, cy, label = int(m.group(1)), int(m.group(2)), m.group(3)
        half = len(label) * 6.2 / 2
        x0, x1, y0, y1 = cx - half, cx + half, cy - 10, cy + 2
        assert x0 >= 8 and x1 <= 552 and y1 <= h - 4, (name, "caption off canvas", label)
        for x, y, w, hh in rects:
            if x0 < x + w and x < x1 and y0 < y + hh and y < y1:
                raise AssertionError((name, "caption overlaps rect", label))


for _n, _s in (("d16", D16), ("d17", D17), ("d18", D18), ("d19", D19)):
    check_svg(_n, _s)

# ---------------------------------------------------------------- d16
POD_YAML = T("""
    # pod.yaml: one Pod running hello-devops. A scratch file for Day 16 only.
    # From Day 17 on, a Deployment creates Pods for you.
    apiVersion: v1
    kind: Pod
    metadata:
      name: hello
      labels:
        app: hello
    spec:
      containers:
        - name: web
          image: hello-devops:1.0.0
          imagePullPolicy: IfNotPresent # use the image kind loaded; do not pull it
          ports:
            - containerPort: 8000
""")

d16 = {
    "id": "d16",
    "title": "Why Kubernetes, and how a cluster works",
    "minutes": 40,
    "goal": "By the end you can explain what Kubernetes does, name the parts of a cluster, and run your own app in a Pod on a local kind cluster.",
    "guess": {
        "q": "You tell Kubernetes to run 3 copies of your app. A machine dies and takes 1 copy with it. What happens next?",
        "options": [
            "Nothing happens until you run your deploy command again",
            "It sees 2 running copies and starts a third on a healthy machine",
            "It reboots the dead machine and waits for it to come back",
            "It stops the other 2 copies so that all machines stay in sync",
        ],
        "answer": 1,
        "why": "Kubernetes keeps comparing what you asked for (3 copies) with what is running (2). When they differ, it acts to close the gap, here by starting a copy on a healthy machine.",
    },
    "terms": [
        {"term": "Kubernetes", "plain": "An open-source system that runs and manages containers across a group of machines."},
        {"term": "Cluster", "plain": "A group of machines (nodes) that Kubernetes manages as one system."},
        {"term": "Control plane", "plain": "The part of a cluster that stores what you asked for and decides where things run."},
        {"term": "Node", "plain": "One machine in a cluster that runs your containers; on kind, a node is a Docker container."},
        {"term": "Pod", "plain": "The smallest thing Kubernetes runs: one or more containers that share one network address."},
        {"term": "Manifest", "plain": "A YAML file that describes an object you want, with apiVersion, kind, metadata and spec."},
        {"term": "kubectl", "plain": "The command-line tool that sends your requests to a cluster's API server."},
    ],
    "sections": [
        {
            "h": "The problem: many containers on many machines",
            "body": T("""
                In Part 2 you ran hello-devops with `docker run` and Docker Compose. That works well on one computer. Now picture a real product: 40 services, each with several copies, spread over 20 servers.

                Someone has to answer these questions all day:
                - Placement: which server has room for this container?
                - Restarts: a container crashed at night. Who starts it again?
                - Scaling: traffic doubled. Who adds copies, and who removes them later?
                - Rollouts: how do you swap version 1 for version 2 without downtime?
                - Finding each other: copies come and go, so how does one service find another?

                **Kubernetes** (often written K8s) answers all of these. It is an open-source system that runs containers across a group of machines, called a cluster. You describe what you want. Kubernetes does the work, and keeps doing it.

                In this part you run Kubernetes on your Mac with kind ("Kubernetes in Docker"). Each kind node is a Docker container, so a three-node cluster fits on one laptop.
            """),
            "refs": [L["overview"], L["nana"]],
        },
        {
            "h": "Desired state and control loops",
            "body": T("""
                The central idea in Kubernetes is **desired state**. You do not give orders like "start a container on server 3". You write down the result you want, such as "three copies of hello-devops 1.0.0". Kubernetes stores it.

                Then small programs called controllers run a loop that never ends:
                1. Read the desired state (what you asked for).
                2. Look at the actual state (what is running now).
                3. If they differ, act to make them match.
                4. Wait a moment and repeat.

                This is called reconciliation, and the loop is a control loop. The [Kubernetes docs](https://kubernetes.io/docs/concepts/architecture/controller/) compare it to a thermostat. You set 21 degrees. The thermostat keeps checking the room and turns the heating on or off.

                This explains the guess at the top. When a machine dies, the actual state drops to two copies. A controller sees the gap and starts a third copy somewhere else. Nobody has to wake up.

                You met a similar idea in Terraform, which also compares your code with what exists. The difference: Terraform acts only when you run `terraform apply`. Kubernetes checks all the time.
            """),
            "refs": [L["controller"]],
        },
        {
            "h": "Inside a cluster: control plane and nodes",
            "body": T("""
                A cluster has two kinds of parts. The control plane decides. The worker nodes do the work.

                The control plane has four main components:
                - API server (`kube-apiserver`): the front door. Every request goes through it, including yours from `kubectl`.
                - etcd: a key-value database that stores the whole cluster state.
                - Scheduler (`kube-scheduler`): picks a node for each new Pod that has none yet.
                - Controller manager (`kube-controller-manager`): runs the built-in control loops.

                Every worker node runs three things:
                - kubelet: an agent that makes sure the Pods assigned to its node are running.
                - kube-proxy: keeps network rules so traffic for a Service reaches the right Pods (Day 17).
                - A container runtime such as containerd: the software that actually starts containers.

                The parts never call each other directly. They all read and write through the API server. The diagram below shows the path of one `kubectl apply`.
            """),
            "refs": [L["components"], L["architecture"]],
        },
        {
            "h": "Pods and manifests",
            "body": T("""
                A Pod is the smallest thing Kubernetes runs. Most Pods hold one container. Some hold a main container plus a small helper. Containers in one Pod share an IP address and can share files.

                Pods are disposable. When a Pod dies, Kubernetes does not repair it. A controller makes a new one, with a new name and a new IP address. So you rarely create Pods by hand. Tomorrow a Deployment creates them for you.

                You describe objects in a manifest, a YAML file. Every manifest has four top-level fields:
                - `apiVersion`: which version of the API defines this kind (for a Pod, `v1`).
                - `kind`: the type of object, such as `Pod`, `Deployment` or `Service`.
                - `metadata`: identity, such as `name`, `namespace` and `labels`.
                - `spec`: your desired state for this object.

                After you apply a manifest, Kubernetes adds a fifth part, `status`. It holds the actual state. Controllers work to make `status` match `spec`.
            """),
            "refs": [L["pods"], L["objects"]],
        },
        {
            "h": "Talking to the cluster: kubectl and kind",
            "body": T("""
                `kubectl` is the command-line tool for Kubernetes. It reads `~/.kube/config` to learn which cluster to talk to. That file holds contexts (a cluster plus a user). When kind creates a cluster named `devops`, it adds the context `kind-devops` and switches to it.

                The commands you will use every day:
                - `kubectl get pods`: list objects of one type.
                - `kubectl describe pod hello`: details and recent events for one object.
                - `kubectl logs hello`: what the container printed.
                - `kubectl apply -f pod.yaml`: create or update objects from a file.
                - `kubectl delete -f pod.yaml`: remove them.
                - `kubectl explain pod.spec`: built-in docs for any field.

                kind nodes keep their own copy of images, apart from Docker on your Mac. So an image you built locally must be copied in with `kind load docker-image`. Use a real tag such as `1.0.0`, never `latest`, or Kubernetes tries to pull it from Docker Hub.

                To reach a Pod from your Mac, run `kubectl port-forward pod/hello 8000:8000`. It opens a tunnel from a local port to the Pod while the command runs.
            """),
            "refs": [L["kubectl"], L["kind_qs"], L["pf"]],
        },
        {
            "h": "Managed Kubernetes, and when you do not need it",
            "body": T("""
                In production, few teams run the control plane themselves. Cloud providers sell managed Kubernetes. They run and upgrade the control plane, and you run your apps on the nodes:
                - Amazon EKS (Elastic Kubernetes Service) on AWS.
                - AKS (Azure Kubernetes Service) on Microsoft Azure.
                - GKE (Google Kubernetes Engine) on Google Cloud.

                Each one also has a mode where the provider manages the nodes too: EKS Auto Mode, AKS Automatic and GKE Autopilot.

                Kubernetes is powerful, but it has a real cost. Someone must learn it, upgrade it and secure it. You may not need it when:
                - You run one or a few services with steady traffic.
                - Your small team has nobody to own the platform.
                - A simpler service fits, such as a PaaS or serverless containers (Day 4).

                Your manifests work the same on kind, EKS, AKS and GKE. That is why a laptop cluster is real practice. The differences sit at the edges: load balancers, disks and identity.
            """),
            "refs": [L["eks"], L["aks"], L["gke"]],
        },
    ],
    "analogy": "Kubernetes is like a manager at a busy restaurant who must keep three cooks on the line. You do not say which cook works at which station. If a cook goes home sick, the manager calls in another one without asking you. The stations are the nodes and the cooks are your Pods. Where it breaks: a real manager uses judgment and bends rules, while Kubernetes only follows the exact state you wrote down.",
    "diagram": D16,
    "diagram_caption": "kubectl talks only to the API server. etcd stores the state, the scheduler picks a node, and the kubelet on that node starts the Pod.",
    "worked": {
        "title": "Find the control plane inside a kind cluster",
        "steps": [
            {
                "say": "Create a small throwaway cluster with one node, named `demo`. The first run downloads a node image, which can take a few minutes. At the end, kind points kubectl at the new cluster.",
                "code": "$ kind create cluster --name demo\n$ kubectl config current-context\nkind-demo",
                "lang": "console",
            },
            {
                "say": "List the nodes. There is just one, and it is both the control plane and the worker. VERSION is the Kubernetes version kind installed.",
                "code": "$ kubectl get nodes\nNAME                 STATUS   ROLES           AGE   VERSION\ndemo-control-plane   Ready    control-plane   52s   v1.37.0",
                "lang": "console",
            },
            {
                "say": "The node is a Docker container on your Mac. That is the whole trick behind kind.",
                "code": "$ docker ps --filter name=demo --format '{{.Names}}'\ndemo-control-plane",
                "lang": "console",
            },
            {
                "say": "Now find the control plane parts. In kind they run as Pods in the `kube-system` namespace. You can see the API server, etcd, the scheduler and the controller manager. There is also kube-proxy, CoreDNS (the cluster's DNS server) and kindnet (the network plugin).",
                "code": T("""
                    $ kubectl get pods -n kube-system
                    NAME                                         READY   STATUS    RESTARTS   AGE
                    coredns-7d764666f9-8xk2v                     1/1     Running   0          95s
                    coredns-7d764666f9-tq9bl                     1/1     Running   0          95s
                    etcd-demo-control-plane                      1/1     Running   0          101s
                    kindnet-5wq8h                                1/1     Running   0          95s
                    kube-apiserver-demo-control-plane            1/1     Running   0          101s
                    kube-controller-manager-demo-control-plane   1/1     Running   0          101s
                    kube-proxy-7lq2c                             1/1     Running   0          95s
                    kube-scheduler-demo-control-plane            1/1     Running   0          101s
                """),
                "lang": "console",
            },
            {
                "say": "Ask the cluster what a field means. `kubectl explain` reads the documentation built into the API, so it always matches your cluster's version. Then delete the practice cluster: this removes the node container and the `kind-demo` context.",
                "code": "$ kubectl explain pod.spec.containers.imagePullPolicy\n$ kind delete cluster --name demo",
                "lang": "console",
            },
        ],
    },
    "code": [
        {"lang": "yaml", "title": "kind-config.yaml", "src": lab("kind-config.yaml"), "run": "kind create cluster --name devops --config kind-config.yaml"},
        {"lang": "yaml", "title": "pod.yaml (scratch file, delete it after today)", "src": POD_YAML, "run": "kubectl apply -f pod.yaml"},
    ],
    "commands": [
        {"cmd": "kind create cluster --name devops --config kind-config.yaml", "what": "Create the course cluster (1 control plane node, 2 workers) from the config file."},
        {"cmd": "kind load docker-image hello-devops:1.0.0 --name devops", "what": "Copy an image from Docker on your Mac into every node of the cluster."},
        {"cmd": "kubectl get nodes", "what": "List the machines in the cluster and whether they are Ready."},
        {"cmd": "kubectl apply -f pod.yaml", "what": "Create or update the objects described in a file."},
        {"cmd": "kubectl get pods -o wide", "what": "List Pods with their IP address and the node each one runs on."},
        {"cmd": "kubectl describe pod hello", "what": "Show details and recent events for one Pod. Your first stop when something is wrong."},
        {"cmd": "kubectl logs hello", "what": "Print what the Pod's container wrote to stdout and stderr."},
        {"cmd": "kubectl port-forward pod/hello 8000:8000", "what": "Forward localhost:8000 on your Mac to port 8000 in the Pod, until you press Ctrl+C."},
        {"cmd": "kubectl explain pod.spec.containers", "what": "Show the built-in docs for a field of any object."},
        {"cmd": "kubectl delete -f pod.yaml", "what": "Delete the objects described in a file."},
        {"cmd": "kind delete cluster --name devops", "what": "Delete a whole kind cluster and its node containers."},
    ],
    "mistake": "Using `:latest` (or no tag) for an image you copied in with `kind load`. Kubernetes then defaults to `imagePullPolicy: Always`, tries Docker Hub, and the Pod gets stuck in `ErrImagePull` and then `ImagePullBackOff`. Use a real tag like `hello-devops:1.0.0` and set `imagePullPolicy: IfNotPresent`.",
    "real_world": "At PayLite, a made-up payments company, the platform team runs three managed clusters on EKS: dev, staging and production. Product teams never touch the control plane. They write manifests, open a pull request, and a pipeline applies them, while developers test the same manifests on kind first.",
    "task": {
        "title": "Run hello-devops in a Pod on your own cluster",
        "steps": [
            "In `~/code/hello-devops`, make sure the image carries its version: `docker build --build-arg APP_VERSION=1.0.0 -t hello-devops:1.0.0 .`",
            "Save `kind-config.yaml` in the repo root and create a cluster named `devops` with it.",
            "Check that `kubectl get nodes` shows three nodes, all Ready.",
            "Load `hello-devops:1.0.0` into the cluster. Remember the `--name` flag.",
            "Write `pod.yaml` for a Pod named `hello` that runs your image, and apply it.",
            "Wait until `kubectl get pods -o wide` shows `Running`. Note which worker node the scheduler picked.",
            "Port-forward local port 8000 to the Pod, and run `curl localhost:8000` in a second terminal.",
            "Read the Pod's logs, then delete the Pod and `pod.yaml`. Keep the cluster for tomorrow.",
        ],
        "hints": [
            "If `kind load` fails with `ctr: content digest ... not found`, Docker is using its containerd image store. The kind known issues page shows a fix: `docker image save --platform linux/arm64` (use `linux/amd64` on an Intel Mac or PC) to a file, then `kind load image-archive`.",
            "The `host` field in the JSON is the Pod's name, because a container's host name is its Pod's name.",
            "Pod stuck in `ErrImagePull`? Check the tag and `imagePullPolicy` in `pod.yaml`, and that you loaded the image into the `devops` cluster.",
        ],
        "done_when": "With port-forward running, `curl localhost:8000` returns JSON whose `host` is `hello` and whose `version` is `1.0.0`.",
    },
    "explain_back": {
        "prompt": "Explain in 3 to 4 sentences what happens between `kubectl apply -f pod.yaml` and your container running. Mention the API server, etcd, the scheduler and the kubelet.",
        "answer": "kubectl sends the Pod manifest to the API server, which checks it and stores it in etcd as desired state. The scheduler notices a Pod with no node and assigns it to a node with enough room. The kubelet on that node sees the new Pod, asks the container runtime to start the container, and reports the status back. From then on, the kubelet and the controllers keep comparing desired and actual state and fix any difference.",
    },
    "recap": [
        "Kubernetes runs containers across many machines and keeps them the way you asked.",
        "Controllers run control loops: compare desired state with actual state, then act.",
        "The control plane (API server, etcd, scheduler, controller manager) decides; nodes (kubelet, kube-proxy, runtime) run Pods.",
        "A Pod is the smallest unit: one or more containers that share an IP address.",
        "Every manifest has apiVersion, kind, metadata and spec; Kubernetes adds status.",
        "kind runs a real cluster on your Mac, with each node as a Docker container.",
    ],
    "check": [
        {
            "q": "A teammate wipes the etcd data of a test cluster by mistake. What do you expect?",
            "options": [
                "Running containers lose their images but keep their logs",
                "The cluster forgets every object, such as Pods and Services",
                "Only the scheduler stops, so new Pods stay Pending",
                "kubectl stops, but the kubelet still holds a full copy",
            ],
            "answer": 1,
            "why": "etcd is where the API server stores all cluster state, so losing it means losing the record of every object.",
        },
        {
            "q": "You apply a Pod. Minutes later `kubectl get pods` still shows it as `Pending` with no node. Which component has not done its job?",
            "options": ["kube-proxy", "etcd", "The kubelet", "The scheduler"],
            "answer": 3,
            "why": "Choosing a node for a Pod is the scheduler's job; a Pending Pod without a node means no node fit, or the scheduler is not running.",
        },
        {
            "q": "A small team runs one internal web app with steady traffic, and nobody knows Kubernetes. What is the most sensible first choice?",
            "options": [
                "Build a self-managed Kubernetes cluster on three VMs",
                "Use managed Kubernetes like EKS with autoscaling",
                "Use a simpler service, such as a PaaS or serverless containers",
                "Run kind on a production server",
            ],
            "answer": 2,
            "why": "Kubernetes pays off with many services and people to run it; for one steady app, a simpler managed service costs far less effort.",
        },
    ],
    "interview": [
        {
            "q": "What is the difference between the control plane and the worker nodes?",
            "a": "The control plane is the decision-making part of the cluster. The API server is its front door, etcd stores all state, the scheduler places Pods on nodes, and the controller manager runs the control loops. Worker nodes run the workloads: the kubelet starts and watches Pods, kube-proxy sets up Service networking, and a runtime such as containerd runs the containers. In managed services like EKS or GKE, the provider runs the control plane for you.",
        },
        {
            "q": "What does 'declarative' mean in Kubernetes, and why does it matter?",
            "a": "Declarative means you describe the end state you want, not the steps to reach it. You write a manifest that says 'three copies of this image', and controllers keep working until the cluster matches. Applying the same file twice gives the same result, so changes are repeatable and reviewable. Because controllers keep checking after the first apply, the cluster also heals itself. GitOps builds on this: git holds the desired state.",
        },
    ],
    "deeper": {
        "minutes": 12,
        "body": T("""
            Every component you met today talks only to the API server. None of them calls another directly. So how does the scheduler learn that a new Pod exists?

            The answer is a watch. A component asks the API server for a list of objects, then keeps the connection open. The API server streams every change (added, modified, deleted) as it happens:
            - The scheduler watches Pods that have no node yet.
            - Each kubelet watches Pods assigned to its own node.
            - Each controller watches the kinds of objects it cares about.

            This design has a useful property. Controllers are level-triggered: they act on the current state, not on a list of past events. If a controller crashes and restarts, it lists everything again and carries on. Nothing is lost, because the truth lives in etcd, not in the controller's memory.

            Two more details help later:
            - Every object has a `resourceVersion`. If two clients update the same object at once, the second gets a conflict error and must retry. This is called optimistic concurrency.
            - Objects can have owners. A Pod made by a ReplicaSet points to it in `metadata.ownerReferences`. Delete the owner, and the garbage collector deletes what it owns.

            Here is how kind builds a cluster out of containers:
            1. It starts one Docker container per node from the `kindest/node` image.
            2. Inside each container, systemd starts containerd and the kubelet.
            3. kind runs kubeadm, the official setup tool, which starts the control plane parts as Pods.
            4. It installs a small network plugin (kindnet) and a storage provisioner.
            5. It writes a context into `~/.kube/config` so kubectl can connect.

            So a kind cluster is a real cluster, running the same Kubernetes binaries as a cloud cluster. What kind lacks is cloud integration: there are no real load balancers and no cloud disks. You will meet both gaps on Day 19.

            Try the watch mechanism yourself. Run `kubectl get pods -w` in one terminal. In another, apply and delete `pod.yaml`. Each line that appears is an event the API server streamed to kubectl, exactly as it does for the controllers.

            If you want to go further, read about the parts of the control plane on the [components page](https://kubernetes.io/docs/concepts/overview/components/). Then look at the Pods in `kube-system` with `kubectl describe` and find the flags each component runs with.
        """),
    },
    "sources": src("components", "controller", "kind_qs", "kind_issues"),
}

# ---------------------------------------------------------------- d17
DEPLOY_V1 = T("""
    # Runs 3 copies (pods) of hello-devops and replaces any that die.
    apiVersion: apps/v1
    kind: Deployment
    metadata:
      name: hello-devops
      namespace: hello
      labels:
        app: hello-devops
    spec:
      replicas: 3
      selector:
        matchLabels:
          app: hello-devops # must match the pod labels below
      strategy:
        type: RollingUpdate
        rollingUpdate:
          maxUnavailable: 0 # never drop below 3 ready pods during an update
          maxSurge: 1       # add at most 1 extra pod at a time
      template:
        metadata:
          labels:
            app: hello-devops
        spec:
          containers:
            - name: web
              image: hello-devops:1.0.0
              imagePullPolicy: IfNotPresent # use the image kind loaded; do not pull it
              ports:
                - name: http
                  containerPort: 8000
""")

d17 = {
    "id": "d17",
    "title": "Deployments and Services",
    "minutes": 40,
    "goal": "By the end you can run your app as a Deployment with several Pods, reach it through a Service, and roll a new version out and back.",
    "guess": {
        "q": "A Deployment runs 3 Pods of your app. You delete one Pod by hand. What do you see a few seconds later?",
        "options": [
            "2 Pods: deleted Pods stay gone until you apply again",
            "3 Pods: a new one with a new name replaces it",
            "3 Pods: the same Pod returns with the same name and IP",
            "0 Pods: deleting one Pod stops the whole Deployment",
        ],
        "answer": 1,
        "why": "The ReplicaSet behind the Deployment counts 2 Pods where it wants 3 and creates one more. It is a new Pod, so it gets a new name and a new IP address.",
    },
    "terms": [
        {"term": "Deployment", "plain": "An object that keeps a set number of identical Pods running and updates them step by step."},
        {"term": "ReplicaSet", "plain": "The object a Deployment creates to keep exactly N copies of one Pod template running."},
        {"term": "Label", "plain": "A key=value tag on an object, such as app=hello-devops, used to group objects."},
        {"term": "Selector", "plain": "A rule that picks objects by their labels, such as all Pods with app=hello-devops."},
        {"term": "Service", "plain": "A stable name and IP address that spreads traffic over the Pods its selector matches."},
        {"term": "Rolling update", "plain": "Replacing old Pods with new ones a few at a time, so the app stays up."},
        {"term": "Namespace", "plain": "A named group of objects inside one cluster, used to keep apps and teams apart."},
    ],
    "sections": [
        {
            "h": "From Pods to Deployments",
            "body": T("""
                Yesterday you created a Pod by hand. When you deleted it, it was gone for good. Nothing brought it back, because no controller owned it.

                In real work you create a **Deployment** instead. You give it a Pod template (image, ports, settings) and the number of copies you want. The Deployment does not create Pods itself. It creates a ReplicaSet, and the ReplicaSet creates the Pods:
                - Deployment: owns the update strategy and the history of versions.
                - ReplicaSet: keeps exactly N Pods from one template running.
                - Pod: runs your container.

                This chain gives you self-healing. If a Pod crashes or a node dies, the ReplicaSet counts fewer Pods than it wants and creates new ones.

                Scaling is the same loop with a new number. `kubectl scale deployment hello-devops --replicas=5` changes the desired count, and the ReplicaSet fills the gap. You will rarely touch ReplicaSets yourself. Think of them as the Deployment's helpers.
            """),
            "refs": [L["deploy"], L["nana"]],
        },
        {
            "h": "Labels and selectors tie objects together",
            "body": T("""
                How does a ReplicaSet know which Pods are its own? Not by name. It uses labels.

                A label is a key=value tag on an object. In `deployment.yaml`, the Pod template carries the label `app: hello-devops`. The Deployment's `selector` says "my Pods are the ones with `app: hello-devops`". The two must match, or the API server rejects the Deployment.

                Labels are how Kubernetes objects find each other:
                - A Deployment finds its Pods with a selector.
                - A Service finds the Pods to send traffic to with a selector.
                - You find objects with `kubectl get pods -l app=hello-devops`.

                This trips up many people: selectors match labels on Pods as they are right now. If you change a running Pod's label by hand, the ReplicaSet stops counting it and starts a replacement. The old Pod keeps running with no owner. Also, a Deployment's selector cannot be changed after you create it, so choose labels with care.
            """),
            "refs": [L["labels"]],
        },
        {
            "h": "Rolling updates and rollbacks",
            "body": T("""
                To ship a new version, you change the image in the Pod template. Kubernetes then does a rolling update:
                1. The Deployment creates a new ReplicaSet for the new template.
                2. It scales the new ReplicaSet up by a few Pods.
                3. When those Pods are ready, it scales the old ReplicaSet down by a few.
                4. It repeats until every Pod runs the new version.

                Two settings control the pace. `maxSurge` is how many extra Pods may exist above the desired count. `maxUnavailable` is how many may be missing. Both default to 25%. The lab uses `maxSurge: 1` and `maxUnavailable: 0`: add one new Pod, wait until it is ready, then remove one old Pod. You never drop below three working Pods.

                The old ReplicaSet is kept, scaled to zero. That makes rollback fast: `kubectl rollout undo` scales the previous ReplicaSet back up the same gentle way. `kubectl rollout status` waits until a rollout finishes, and `kubectl rollout history` lists the revisions.
            """),
            "refs": [L["deploy"], L["rolling"]],
        },
        {
            "h": "Services: one stable address for many Pods",
            "body": T("""
                Pods come and go, and each new Pod gets a new IP address. So clients should never call Pods directly. A Service solves this. It gets a stable virtual IP and a DNS name, and it spreads traffic over all ready Pods that match its selector.

                There are four common types:
                - ClusterIP (the default): reachable only inside the cluster.
                - NodePort: also opens the same port (30000 to 32767) on every node.
                - LoadBalancer: also asks the cloud for an external load balancer. On kind it stays pending, because there is no cloud.
                - Headless (`clusterIP: None`): no virtual IP; DNS returns the Pod IPs directly.

                The lab Service is a NodePort on port 30080, and your `kind-config.yaml` maps that port to `localhost:8081`. So `curl localhost:8081` goes through the Service, and each request can land on a different Pod.

                Read the three ports in `service.yaml` carefully. `port: 80` is the Service's own port. `targetPort: 8000` is the container's port. `nodePort: 30080` is the port opened on each node.
            """),
            "refs": [L["service"], L["kind_cfg"]],
        },
        {
            "h": "Cluster DNS and port-forward",
            "body": T("""
                Inside the cluster, Pods find Services by name. A DNS server (CoreDNS) runs in the cluster and gives every Service a name like `<service>.<namespace>.svc.cluster.local`.

                So the lab's Service is `hello-devops.hello.svc.cluster.local`. A Pod in the same namespace can use the short name `hello-devops`. A Pod in another namespace needs at least `hello-devops.hello`. Tomorrow the app finds Redis this way, with `REDIS_HOST=redis`.

                From your Mac you have two ways in:
                - The NodePort, through kind's port mapping. This goes through the Service, so requests are spread over the Pods.
                - `kubectl port-forward svc/hello-devops 8080:80 -n hello`. It works for any Service, but it picks one Pod and sends everything there.

                Port-forward is a debugging tool, not the way users reach an app. On Day 19 you add a Gateway for that.
            """),
            "refs": [L["dns"], L["pf_ref"]],
        },
        {
            "h": "Namespaces",
            "body": T("""
                A namespace is a named group of objects inside one cluster. Names must be unique inside a namespace, not across the whole cluster. Teams use namespaces to separate apps, teams or environments, and to attach access rules and quotas.

                A new cluster already has a few:
                - `default`: where objects go when you do not name a namespace.
                - `kube-system`: the cluster's own parts, such as CoreDNS and kube-proxy.
                - `kube-public` and `kube-node-lease`: used by the system; leave them alone.

                The lab puts everything in a namespace called `hello`, and each manifest sets `metadata.namespace: hello`. With kubectl, add `-n hello`, or make it your default with `kubectl config set-context --current --namespace=hello`. Deleting a namespace deletes everything inside it, which makes cleanup easy and mistakes costly.
            """),
            "refs": [L["ns"]],
        },
    ],
    "analogy": "A Deployment is like a call center manager who must keep three operators at the phones. If one goes home, the manager brings in a replacement. The Service is the single public phone number that rings whichever operator is free, so callers never need names. Where it breaks: a replacement operator remembers the company's past calls, but a new Pod starts with no memory unless the data lives outside it, like in Redis.",
    "diagram": D17,
    "diagram_caption": "Requests reach the Service on NodePort 30080 and go to any Pod labeled app=hello-devops. The Deployment and its ReplicaSet keep three such Pods running.",
    "worked": {
        "title": "Self-healing and scaling, step by step",
        "steps": [
            {
                "say": "Create a scratch namespace and a Deployment with two Pods, without writing YAML. `kubectl create deployment` is handy for experiments. For real work, YAML in git is better, because it can be reviewed and repeated.",
                "code": "$ kubectl create namespace scratch\nnamespace/scratch created\n$ kubectl create deployment web --image=hello-devops:1.0.0 --replicas=2 -n scratch\ndeployment.apps/web created",
                "lang": "console",
            },
            {
                "say": "Look at the chain. The Deployment made a ReplicaSet, and the ReplicaSet made two Pods. Each Pod name starts with the ReplicaSet's name.",
                "code": T("""
                    $ kubectl get deployment,replicaset,pods -n scratch
                    NAME                  READY   UP-TO-DATE   AVAILABLE   AGE
                    deployment.apps/web   2/2     2            2           20s

                    NAME                             DESIRED   CURRENT   READY   AGE
                    replicaset.apps/web-7d4b9c8f6d   2         2         2       20s

                    NAME                       READY   STATUS    RESTARTS   AGE
                    pod/web-7d4b9c8f6d-n7wqz   1/1     Running   0          20s
                    pod/web-7d4b9c8f6d-x2kqp   1/1     Running   0          20s
                """),
                "lang": "console",
            },
            {
                "say": "Delete one Pod and list again. The ReplicaSet saw one Pod missing and created a replacement with a new name within seconds.",
                "code": T("""
                    $ kubectl delete pod web-7d4b9c8f6d-n7wqz -n scratch
                    pod "web-7d4b9c8f6d-n7wqz" deleted from scratch namespace
                    $ kubectl get pods -n scratch
                    NAME                   READY   STATUS    RESTARTS   AGE
                    web-7d4b9c8f6d-q8rtm   1/1     Running   0          4s
                    web-7d4b9c8f6d-x2kqp   1/1     Running   0          75s
                """),
                "lang": "console",
            },
            {
                "say": "Scale to four. Only the number changes, so the same ReplicaSet adds two Pods. The `-l app=web` flag selects Pods by the label that `kubectl create deployment` added.",
                "code": T("""
                    $ kubectl scale deployment web --replicas=4 -n scratch
                    deployment.apps/web scaled
                    $ kubectl get pods -n scratch -l app=web
                    NAME                   READY   STATUS    RESTARTS   AGE
                    web-7d4b9c8f6d-4hfsx   1/1     Running   0          6s
                    web-7d4b9c8f6d-q8rtm   1/1     Running   0          50s
                    web-7d4b9c8f6d-t6zjc   1/1     Running   0          6s
                    web-7d4b9c8f6d-x2kqp   1/1     Running   0          2m1s
                """),
                "lang": "console",
            },
            {
                "say": "Put a Service in front, then call it by its DNS name from inside one of the Pods. The image has Python but no curl, so Python makes the request. The answer can come from any of the four Pods.",
                "code": T("""
                    $ kubectl expose deployment web --port=80 --target-port=8000 -n scratch
                    service/web exposed
                    $ kubectl exec -n scratch deploy/web -- python -c "import urllib.request as u; print(u.urlopen('http://web.scratch.svc.cluster.local').read().decode().strip())"
                    {"host":"web-7d4b9c8f6d-t6zjc","message":"Hello, DevOps!","version":"1.0.0","visits":1}
                """),
                "lang": "console",
            },
            {
                "say": "Clean up. Deleting the namespace deletes everything in it: the Deployment, the ReplicaSet, the Pods and the Service.",
                "code": "$ kubectl delete namespace scratch\nnamespace \"scratch\" deleted",
                "lang": "console",
            },
        ],
    },
    "code": [
        {"lang": "yaml", "title": "k8s/namespace.yaml", "src": lab("k8s/namespace.yaml"), "run": "kubectl apply -f k8s/namespace.yaml"},
        {"lang": "yaml", "title": "k8s/deployment.yaml (first version; Day 18 adds config, probes and resources)", "src": DEPLOY_V1, "run": "kubectl apply -f k8s/deployment.yaml"},
        {"lang": "yaml", "title": "k8s/service.yaml", "src": lab("k8s/service.yaml"), "run": "kubectl apply -f k8s/service.yaml"},
    ],
    "commands": [
        {"cmd": "kubectl apply -f k8s/namespace.yaml -f k8s/deployment.yaml -f k8s/service.yaml", "what": "Create or update the namespace, the Deployment and the Service in one go."},
        {"cmd": "kubectl get deploy,rs,pods -n hello", "what": "Show the Deployment, its ReplicaSets and its Pods together."},
        {"cmd": "kubectl get pods -n hello -l app=hello-devops --show-labels", "what": "List the Pods that match a label, with all their labels."},
        {"cmd": "kubectl scale deployment hello-devops --replicas=5 -n hello", "what": "Change the desired number of Pods."},
        {"cmd": "kubectl set image deployment/hello-devops web=hello-devops:1.1.0 -n hello", "what": "Change the image of container web, which starts a rolling update."},
        {"cmd": "kubectl rollout status deployment/hello-devops -n hello", "what": "Follow a rollout and wait until it finishes."},
        {"cmd": "kubectl rollout history deployment/hello-devops -n hello", "what": "List the revisions the Deployment remembers."},
        {"cmd": "kubectl rollout undo deployment/hello-devops -n hello", "what": "Go back to the previous revision."},
        {"cmd": "kubectl get svc -n hello", "what": "List Services with their type, cluster IP and ports."},
        {"cmd": "kubectl port-forward svc/hello-devops 8080:80 -n hello", "what": "Forward localhost:8080 to the Service (it picks one Pod)."},
        {"cmd": "kubectl config set-context --current --namespace=hello", "what": "Make hello the default namespace for your kubectl commands."},
    ],
    "mistake": "Changing the live cluster with `kubectl set image`, `kubectl scale` or `kubectl edit`, then forgetting to change the YAML in git. The next `kubectl apply` (or Argo CD on Day 20) puts the old values back, and nobody knows why. Use the quick commands to experiment, then make the real change in the file and apply it.",
    "real_world": "At PayLite, the checkout service runs as a Deployment with 6 replicas spread over several nodes. Releases are rolling updates with `maxUnavailable: 0`, so card payments keep flowing during a deploy. If errors jump after a release, the on-call engineer rolls back first and investigates afterwards.",
    "task": {
        "title": "Deploy hello-devops with a Deployment and a Service",
        "steps": [
            "Write `k8s/namespace.yaml`, `k8s/deployment.yaml` (3 replicas) and `k8s/service.yaml` (NodePort 30080). Apply all three with one `kubectl apply` command.",
            "Wait until `kubectl get pods -n hello` shows 3 Pods that are Running and `1/1` ready.",
            "Call `curl localhost:8081` six times in a loop. Watch the `host` field change between Pods.",
            "Build a new version with `docker build --build-arg APP_VERSION=1.1.0 -t hello-devops:1.1.0 .` and load it into kind.",
            "Roll out 1.1.0 with `kubectl set image` and follow it with `kubectl rollout status`.",
            "Check that `curl localhost:8081` now shows version 1.1.0, then look at `kubectl rollout history`.",
            "Roll back with `kubectl rollout undo` and confirm that the version is 1.0.0 again.",
            "In a second terminal run `kubectl get pods -n hello -w`. Delete one Pod by name and watch a new one appear.",
        ],
        "hints": [
            "A loop in zsh: `for i in {1..6}; do curl -s localhost:8081; done` (the app ends each answer with a new line).",
            "The container is named `web` in the YAML, so `set image` needs `web=hello-devops:1.1.0`.",
            "`curl` cannot connect? Check the Service type, `nodePort: 30080`, and that you created the cluster with `kind-config.yaml`.",
        ],
        "done_when": "Six calls to `curl localhost:8081` show at least two different `host` values, and you have rolled from 1.0.0 to 1.1.0 and back.",
    },
    "explain_back": {
        "prompt": "Explain in 3 to 4 sentences how a Deployment, a ReplicaSet and a Service keep hello-devops reachable during a rolling update. Mention labels.",
        "answer": "The Deployment holds the Pod template and creates a ReplicaSet for each version of it. During a rolling update it scales the new ReplicaSet up and the old one down a little at a time, within maxSurge and maxUnavailable. The Service does not care about versions: it sends traffic to every ready Pod whose labels match its selector, old or new. So users keep getting answers while Pods are replaced, and the old ReplicaSet stays around for a quick rollback.",
    },
    "recap": [
        "A Deployment owns ReplicaSets, and a ReplicaSet keeps N identical Pods running.",
        "Self-healing and scaling are the same loop: count the Pods, then fix the difference.",
        "Labels tag objects and selectors pick them; Deployments and Services both find Pods this way.",
        "Rolling updates swap Pods a few at a time; `kubectl rollout undo` goes back.",
        "A Service gives Pods one stable address; its DNS name is `<service>.<namespace>.svc.cluster.local`.",
        "Namespaces group objects, and deleting a namespace deletes everything in it.",
    ],
    "check": [
        {
            "q": "A Deployment has `replicas: 4`, `maxSurge: 1` and `maxUnavailable: 0`. During a rolling update, what is the most Pods that can exist at once?",
            "options": ["3", "4", "5", "8"],
            "answer": 2,
            "why": "maxSurge 1 allows one Pod above the desired 4, and maxUnavailable 0 means no old Pod goes until a new one is ready.",
        },
        {
            "q": "A Service has the selector `app: shop`, but its Pods are labeled `app: shop-web`. What happens when you call the Service?",
            "options": [
                "It works, because Kubernetes matches labels by prefix",
                "The call fails, because the Service has no Pods behind it",
                "The Deployment renames the Pod labels to match",
                "Kubernetes refuses to create the Service",
            ],
            "answer": 1,
            "why": "Selectors match labels exactly, so the Service finds no Pods and has nowhere to send the request.",
        },
        {
            "q": "A Pod in namespace `shop` must call the Service `orders` in namespace `billing`. Which address works?",
            "options": ["http://orders", "http://billing.orders", "http://orders.svc", "http://orders.billing"],
            "answer": 3,
            "why": "The short name only works inside the same namespace; from elsewhere use `<service>.<namespace>`, or the full `orders.billing.svc.cluster.local`.",
        },
    ],
    "interview": [
        {
            "q": "What happens during a Kubernetes rolling update, and how do you roll back?",
            "a": "The Deployment creates a new ReplicaSet with the new Pod template. It scales that one up and the old one down step by step, within maxSurge and maxUnavailable, and it waits for new Pods to be ready before it goes on. Old ReplicaSets are kept at zero replicas, so `kubectl rollout undo` can scale the previous one back up quickly. In a GitOps setup you would revert the commit instead, so git and the cluster stay in sync.",
        },
        {
            "q": "What are the Service types in Kubernetes, and when would you use each?",
            "a": "ClusterIP is the default and is reachable only inside the cluster, which fits most internal services. NodePort opens a fixed port on every node, which is useful for simple setups and local clusters like kind. LoadBalancer asks the cloud provider for an external load balancer, the usual way to expose one service in a cloud. A headless Service has no virtual IP, and its DNS name returns the Pod IPs, which StatefulSets use. For HTTP traffic to many services, teams usually put a Gateway in front of ClusterIP Services.",
        },
    ],
    "deeper": {
        "minutes": 12,
        "body": T("""
            A Service is not a process. Nothing listens on its IP address. So how does a packet sent to a Service reach a Pod?

            It takes four steps:
            1. A controller watches the Pods that match the Service's selector. It writes their IP addresses and ports into EndpointSlice objects, and marks each one ready or not ready.
            2. kube-proxy runs on every node and watches Services and EndpointSlices.
            3. kube-proxy writes packet rules into the Linux kernel on its node (iptables or nftables). The rules say: traffic for this virtual IP and port goes to one of these Pod IPs.
            4. When a Pod connects to the Service IP, the kernel on that node changes the destination to one ready Pod.

            You can see the endpoints yourself with `kubectl get endpointslices -n hello`. Scale the Deployment and run it again: the list follows the Pods.

            Three things follow from this design:
            - Traffic is spread per connection, not per request. A client that keeps one connection open (HTTP keep-alive) may talk to the same Pod for a long time. That is why curl in a loop changes Pods, while a browser might not.
            - Readiness matters. A Pod that is not ready gets no Service traffic, even though it is running. You will use this on Day 18.
            - `kubectl port-forward svc/...` skips all of this. It picks one Pod and tunnels to it through the API server.

            NodePort is the same machinery with one more rule: traffic that arrives at any node on port 30080 is sent on to the Service. That is why kind only needs to map one node's port to your Mac.

            DNS has one more detail. Each Pod's `/etc/resolv.conf` lists search domains such as `hello.svc.cluster.local`. That is why the short name `redis` works inside namespace `hello`. Try it: `kubectl exec -n hello deploy/hello-devops -- cat /etc/resolv.conf`.

            Some network plugins, such as Cilium, replace kube-proxy and do the same job with eBPF programs in the kernel. The idea stays the same: a stable virtual address in front of a changing set of Pods.
        """),
    },
    "sources": src("deploy", "service", "dns", "labels"),
}

# ---------------------------------------------------------------- d18
d18 = {
    "id": "d18",
    "title": "Config, secrets, health checks and scaling",
    "minutes": 40,
    "goal": "By the end you can configure the app with a ConfigMap, add health checks and resource settings, scale it with an autoscaler, and debug Pods that will not start.",
    "guess": {
        "q": "Your app's readiness probe starts failing because its database is down. What does Kubernetes do?",
        "options": [
            "Restarts the container until the database comes back",
            "Stops sending it Service traffic, but leaves it running",
            "Deletes the Pod and schedules a new one on another node",
            "Nothing: probes only write warnings to the log",
        ],
        "answer": 1,
        "why": "A failed readiness probe takes the Pod out of the Service's endpoints. Only a failed liveness or startup probe restarts the container.",
    },
    "terms": [
        {"term": "ConfigMap", "plain": "An object that stores plain settings as key-value pairs for Pods to use."},
        {"term": "Secret", "plain": "An object for sensitive values like passwords; its values are base64-encoded, which is not encryption."},
        {"term": "Liveness probe", "plain": "A regular health check; after several failures, the kubelet restarts the container."},
        {"term": "Readiness probe", "plain": "A regular check; while it fails, the Pod gets no traffic from Services."},
        {"term": "Resource request", "plain": "The CPU and memory the scheduler reserves for a container on a node."},
        {"term": "Resource limit", "plain": "The most CPU or memory a container may use; too much memory gets it killed."},
        {"term": "HorizontalPodAutoscaler", "plain": "An object that changes a Deployment's number of Pods based on metrics such as CPU."},
    ],
    "sections": [
        {
            "h": "Config outside the image: ConfigMaps",
            "body": T("""
                In Part 2 you met the twelve-factor idea: build one image, and change its settings with environment variables. A **ConfigMap** is where Kubernetes keeps those settings. It is a simple object with a `data` section of key-value pairs.

                Pods can use a ConfigMap in three ways:
                - `env` with `configMapKeyRef`: one key becomes one environment variable.
                - `envFrom` with `configMapRef`: every key becomes an environment variable. The lab uses this.
                - A volume: each key becomes a file in a folder, good for whole config files.

                The lab's `configmap.yaml` sets `GREETING` and `REDIS_HOST=redis`. Redis gets its own Deployment and Service in `redis.yaml`, so `redis` is a DNS name inside the `hello` namespace.

                This trips up many people: environment variables are read once, when the container starts. If you change the ConfigMap, running Pods keep the old values. Restart them with `kubectl rollout restart deployment/hello-devops -n hello`. Mounted files do update after a short delay, but the app must read them again.
            """),
            "refs": [L["cm"]],
        },
        {
            "h": "Secrets, and why base64 is not protection",
            "body": T("""
                A Secret looks like a ConfigMap, but it is meant for sensitive values: passwords, API tokens and TLS keys. Pods use it the same ways (env, envFrom or a volume).

                Here is the part people miss. Secret values are base64-encoded. Base64 is an encoding that anyone can reverse with one command, `base64 --decode`. And by default, Secrets are stored unencrypted in etcd.

                What actually protects them:
                - Limit who can read Secrets with RBAC (role-based access control) rules.
                - Turn on encryption at rest for etcd. Managed clusters (EKS, AKS, GKE) offer this, often with a cloud key service.
                - Never commit Secret YAML with real values to git.
                - Keep the real value in a vault and sync it in. External Secrets Operator does this from AWS Secrets Manager, HashiCorp Vault and others.
                - Or encrypt it for git with Sealed Secrets, so only a controller in the cluster can decrypt it.

                hello-devops needs no secrets yet, so the lab has no Secret file. The Secret commands in the list below let you see base64 for yourself.
            """),
            "refs": [L["secret"], L["secret_gp"], L["encrypt"]],
        },
        {
            "h": "Health checks: liveness, readiness and startup probes",
            "body": T("""
                Kubernetes can only fix what it can see. A container can be running but broken: stuck, or unable to reach its database. Probes let the kubelet ask your app how it is doing. The lab uses HTTP probes, where a status code from 200 to 399 counts as a pass.

                There are three kinds, and each failure has a different result:
                - Liveness (`/healthz`): "Is the process stuck?" After `failureThreshold` failures in a row, the kubelet restarts the container.
                - Readiness (`/readyz`): "Can it do real work now?" While it fails, the Pod gets no Service traffic. It is not restarted.
                - Startup: "Has it finished starting?" The other two probes wait until it passes, so a slow start is not killed.

                By default a probe runs every 10 seconds (`periodSeconds`), times out after 1 second, and fails after 3 misses in a row.

                A classic mistake is to check the database in the liveness probe. If the database goes down, every Pod restarts at once, and that does not fix the database. The hello-devops app does it right: `/healthz` checks only the process, and `/readyz` also checks Redis.
            """),
            "refs": [L["probes"], L["probes_task"]],
        },
        {
            "h": "Requests, limits, OOMKilled and throttling",
            "body": T("""
                Each container can say how much CPU and memory it needs. CPU is counted in cores: `100m` means 100 millicores, a tenth of a core. Memory is counted in bytes: `128Mi` means 128 mebibytes.

                There are two numbers, with different jobs:
                - Requests: what the scheduler reserves. A Pod only goes on a node with that much unreserved room. Ask for too much, and the Pod stays `Pending`.
                - Limits: the most the container may use. The Linux kernel enforces them.

                What happens at a limit depends on the resource. Memory cannot be taken back, so a container above its memory limit is killed. `kubectl describe pod` then shows `OOMKilled` (out of memory). CPU can be slowed down instead. A container at its CPU limit is throttled: it keeps running, only slower.

                The lab sets requests for CPU and memory, and a limit for memory only. Many teams skip CPU limits, because throttling can hurt response times even when the node has spare CPU. Always set requests, though: the scheduler and the autoscaler both need them.
            """),
            "refs": [L["resources"]],
        },
        {
            "h": "Autoscaling with the HorizontalPodAutoscaler",
            "body": T("""
                A HorizontalPodAutoscaler (HPA) changes the number of replicas for you. The lab's `hpa.yaml` uses the `autoscaling/v2` API. It says: keep average CPU near 70% of the request, with 3 to 6 Pods.

                It is another control loop. About every 15 seconds the HPA:
                1. Reads each Pod's CPU use from the metrics API.
                2. Compares the average with the target (70% of 100m, so 70m).
                3. Works out a new replica count and updates the Deployment.

                The numbers come from metrics-server, an add-on that collects CPU and memory from each kubelet. kind does not include it, so you install it with one `kubectl apply`. On kind you must also add the `--kubelet-insecure-tls` flag, because kind's kubelets use self-signed certificates. The [metrics-server docs](https://github.com/kubernetes-sigs/metrics-server) say this flag is for testing only.

                The HPA needs CPU requests on the Pods, or it cannot work out a percentage. It also scales down slowly on purpose (it waits 5 minutes by default). In the lab, `replicas: 3` in the Deployment equals `minReplicas: 3`, so a new `kubectl apply` does not fight the HPA while the app is quiet.
            """),
            "refs": [L["hpa"], L["metrics"]],
        },
        {
            "h": "Debugging Pods that will not start",
            "body": T("""
                Most problems show up in a Pod's status. Learn these four:
                - `Pending`: no node can take the Pod yet. Often the requests are too big, or a volume is missing.
                - `ErrImagePull`, then `ImagePullBackOff`: the node cannot get the image. Check the name and tag, and on kind, check that you loaded it.
                - `CrashLoopBackOff`: the container starts and exits, again and again. Kubernetes waits longer before each restart.
                - Running but `0/1` ready: the readiness probe is failing.

                The same four commands solve most of them, in this order:
                1. `kubectl get pods -n hello`: which Pod, which status, how many restarts.
                2. `kubectl describe pod <name> -n hello`: read the Events at the bottom first.
                3. `kubectl logs <name> -n hello --previous`: the output of the container that crashed.
                4. `kubectl get events -n hello`: everything that happened recently in the namespace.
            """),
            "refs": [L["debug"], L["lifecycle"]],
        },
    ],
    "analogy": "Probes are like a shop manager who checks on a clerk in two ways. The first check is liveness: is the clerk awake at all? If not, the manager sends them home and calls in someone new. The second check is readiness: can the clerk serve customers right now? If the till is broken, the manager puts a closed sign on that counter but keeps the clerk. Where it breaks: a real manager can ask why, while the kubelet only sees pass or fail from one URL.",
    "diagram": D18,
    "diagram_caption": "The lab's probes: 3 liveness misses in a row restart the container; 2 readiness misses take the Pod out of the Service until it passes again.",
    "worked": {
        "title": "Debug two broken Pods",
        "steps": [
            {
                "say": "Start a Pod with a typo in the image tag. Tag 1.0.1 does not exist on the nodes, so the kubelet tries Docker Hub, fails, and backs off.",
                "code": T("""
                    $ kubectl run typo -n hello --image=hello-devops:1.0.1
                    pod/typo created
                    $ kubectl get pod typo -n hello
                    NAME   READY   STATUS             RESTARTS   AGE
                    typo   0/1     ImagePullBackOff   0          40s
                """),
                "lang": "console",
            },
            {
                "say": "Read the Events at the bottom of `describe`. They show the kubelet's attempts to pull `hello-devops:1.0.1` and the error it got. The fix is the right tag, or a `kind load` of the image you meant.",
                "code": "$ kubectl describe pod typo -n hello",
                "lang": "console",
            },
            {
                "say": "Now a container that crashes as it starts. This one runs Python with a command that exits with an error, which is how a missing setting often looks in a real app. Kubernetes restarts it, waits, restarts it again, and reports `CrashLoopBackOff`.",
                "code": T("""
                    $ kubectl run crashy -n hello --image=hello-devops:1.0.0 -- python -c "raise SystemExit('REDIS_URL is not set')"
                    pod/crashy created
                    $ kubectl get pod crashy -n hello
                    NAME     READY   STATUS             RESTARTS      AGE
                    crashy   0/1     CrashLoopBackOff   3 (25s ago)   90s
                """),
                "lang": "console",
            },
            {
                "say": "`kubectl logs` shows the current container, which may have just restarted and printed nothing yet. `--previous` shows the last one that crashed, which is the one you care about.",
                "code": "$ kubectl logs crashy -n hello --previous\nREDIS_URL is not set",
                "lang": "console",
            },
            {
                "say": "Clean up both Pods. In real life you would fix the manifest and apply it again.",
                "code": "$ kubectl delete pod typo crashy -n hello\npod \"typo\" deleted from hello namespace\npod \"crashy\" deleted from hello namespace",
                "lang": "console",
            },
        ],
    },
    "code": [
        {"lang": "yaml", "title": "k8s/configmap.yaml", "src": lab("k8s/configmap.yaml"), "run": "kubectl apply -k k8s"},
        {"lang": "yaml", "title": "k8s/redis.yaml", "src": lab("k8s/redis.yaml"), "run": "kubectl apply -k k8s"},
        {"lang": "yaml", "title": "k8s/deployment.yaml (final version)", "src": lab("k8s/deployment.yaml"), "run": "kubectl apply -k k8s"},
        {"lang": "yaml", "title": "k8s/hpa.yaml", "src": lab("k8s/hpa.yaml"), "run": "kubectl apply -k k8s"},
        {"lang": "yaml", "title": "k8s/kustomization.yaml", "src": lab("k8s/kustomization.yaml"), "run": "kubectl apply -k k8s"},
    ],
    "commands": [
        {"cmd": "kubectl apply -k k8s", "what": "Apply every file listed in k8s/kustomization.yaml."},
        {"cmd": "kubectl rollout restart deployment/hello-devops -n hello", "what": "Replace all Pods gradually, for example to pick up a changed ConfigMap."},
        {"cmd": "kubectl create secret generic demo-secret -n hello --from-literal=password=s3cret", "what": "Create a Secret from a value on the command line (for practice only)."},
        {"cmd": "kubectl get secret demo-secret -n hello -o jsonpath='{.data.password}' | base64 --decode", "what": "Read a Secret value back, which shows that base64 hides nothing."},
        {"cmd": "kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml", "what": "Install the latest metrics-server, which the HPA and kubectl top need."},
        {"cmd": "kubectl patch deployment metrics-server -n kube-system --type=json -p '[{\"op\":\"add\",\"path\":\"/spec/template/spec/containers/0/args/-\",\"value\":\"--kubelet-insecure-tls\"}]'", "what": "On kind only: let metrics-server accept the kubelets' self-signed certificates."},
        {"cmd": "kubectl top pods -n hello", "what": "Show the current CPU and memory use of each Pod."},
        {"cmd": "kubectl get hpa -n hello -w", "what": "Watch the autoscaler's current CPU, target and replica count."},
        {"cmd": "kubectl describe pod <pod-name> -n hello", "what": "Show a Pod's details; read the Events at the bottom first."},
        {"cmd": "kubectl logs <pod-name> -n hello --previous", "what": "Show the output of the previous container, the one that crashed."},
        {"cmd": "kubectl get events -n hello --sort-by=.metadata.creationTimestamp", "what": "List recent events in the namespace, oldest first."},
    ],
    "mistake": "Pointing the liveness probe at a check that depends on something else, such as the database. When the database has a problem, every Pod fails liveness and restarts at once, which makes the outage worse. Keep liveness to \"is this process alive\" (`/healthz`) and put dependency checks in readiness (`/readyz`).",
    "real_world": "At PayLite, each service sets CPU and memory requests from real usage seen in monitoring, and an HPA adds checkout Pods before big sales. Passwords come from AWS Secrets Manager through External Secrets Operator, so no secret value is ever in git. The on-call runbook starts with the same three commands: get pods, describe, and logs with `--previous`.",
    "task": {
        "title": "Add config, Redis, health checks and autoscaling",
        "steps": [
            "Write `k8s/configmap.yaml` and `k8s/redis.yaml`, and update `k8s/deployment.yaml` with `envFrom`, the three probes and resources.",
            "Write `k8s/kustomization.yaml` that lists your files (leave `hpa.yaml` out for now), then run `kubectl apply -k k8s`.",
            "Call `curl localhost:8081` a few times. The greeting now comes from the ConfigMap, and `visits` counts up across all Pods.",
            "In a second terminal run `kubectl get pods -n hello -w`. Break Redis with `kubectl scale deployment redis -n hello --replicas=0`.",
            "Watch the app Pods turn `0/1` ready within about 10 seconds, while RESTARTS stays at 0. Try curl: it fails, because no Pod is ready.",
            "Scale Redis back to 1 and watch the app Pods become ready again on their own.",
            "Install metrics-server, add the `--kubelet-insecure-tls` flag, and wait until `kubectl top pods -n hello` shows numbers.",
            "Add `hpa.yaml` to the kustomization and apply again. Create load (see the hints) and watch `kubectl get hpa -n hello -w`.",
            "Stop the load and delete the load Pod. The HPA scales back to 3 after about 5 quiet minutes.",
        ],
        "hints": [
            "A load generator: `kubectl run load -n hello --image=busybox:1.37 --restart=Never -- /bin/sh -c \"while true; do wget -q -O- http://hello-devops > /dev/null; done\"`. Remove it with `kubectl delete pod load -n hello`.",
            "Visits start again from 1 after Redis comes back, because this Redis keeps no data on disk. Day 19 explains storage.",
            "Pods still `0/1` after Redis is back? Read the Events in `kubectl describe pod` for the readiness probe messages.",
        ],
        "done_when": "With Redis at 0 replicas the app Pods show `0/1` ready and 0 restarts, and under load `kubectl get hpa -n hello` shows more than 3 replicas.",
    },
    "explain_back": {
        "prompt": "Explain in 3 to 4 sentences the difference between a liveness probe and a readiness probe. Use what happened when you scaled Redis to zero.",
        "answer": "A liveness probe asks whether the process is still healthy; after repeated failures, the kubelet restarts the container. A readiness probe asks whether the Pod can serve traffic right now; while it fails, the Pod is taken out of the Service but keeps running. When I scaled Redis to zero, the readiness check returned 503, so the app Pods went to 0/1 ready and got no traffic. They did not restart, because `/healthz` still passed. When Redis came back, the Pods became ready again without anyone touching them.",
    },
    "recap": [
        "ConfigMaps hold settings; environment variables from them are read only when a container starts.",
        "Secrets are base64-encoded, not encrypted: limit access, encrypt etcd and keep real values out of git.",
        "A failed liveness probe restarts a container; a failed readiness probe only removes it from Service traffic.",
        "Requests decide placement; above the memory limit means OOMKilled, at the CPU limit means throttling.",
        "An HPA scales replicas from metrics; on kind it needs metrics-server with `--kubelet-insecure-tls`.",
        "Debug with get pods, describe (Events), logs `--previous` and get events.",
    ],
    "check": [
        {
            "q": "A Pod shows `OOMKilled` in `kubectl describe` and has restarted 5 times. What is the most likely fix?",
            "options": [
                "Add a readiness probe to the container",
                "Raise the CPU limit so it runs faster",
                "Lower the memory request on the Pod",
                "Raise the memory limit, or use less memory",
            ],
            "answer": 3,
            "why": "OOMKilled means the container went over its memory limit, so it needs a higher limit or a smaller memory footprint.",
        },
        {
            "q": "A new Pod stays `Pending` for minutes, and `describe` says 'Insufficient cpu'. What does that tell you?",
            "options": [
                "No node has enough unreserved CPU for the Pod's request",
                "The CPU limit is too low, so the app is throttled",
                "The container keeps crashing while it starts",
                "metrics-server is missing, so CPU is unknown",
            ],
            "answer": 0,
            "why": "Scheduling uses requests: if every node has too little unreserved CPU for the request, the Pod waits in Pending.",
        },
        {
            "q": "You change `GREETING` in the ConfigMap and run `kubectl apply -k k8s`. The app still shows the old greeting. Why?",
            "options": [
                "The apply skipped the ConfigMap file",
                "Kubernetes caches ConfigMaps for an hour",
                "Pods read env vars only at start, so they need a restart",
                "The readiness probe still serves old answers",
            ],
            "answer": 2,
            "why": "Environment variables are set when a container starts; `kubectl rollout restart` makes new Pods that read the new values.",
        },
    ],
    "interview": [
        {
            "q": "What is the difference between liveness, readiness and startup probes?",
            "a": "A liveness probe checks whether the container is still healthy, and repeated failures make the kubelet restart it. A readiness probe checks whether the Pod can take traffic; while it fails, the Pod is removed from Service endpoints but keeps running. A startup probe protects slow-starting apps, because the other two probes wait until it passes. A good liveness check tests only the process itself, while readiness may test dependencies such as a database.",
        },
        {
            "q": "How do resource requests and limits work, and what happens when a container goes over them?",
            "a": "Requests are what the scheduler reserves, so they decide which node a Pod can go on. Limits are the most the container may use, and the kernel enforces them through cgroups. Going over the memory limit gets the container killed (OOMKilled), while hitting the CPU limit only slows it down (throttling). Most teams always set requests, set a memory limit, and think carefully before adding CPU limits.",
        },
    ],
    "deeper": {
        "minutes": 12,
        "body": T("""
            Requests and limits do one more job you cannot see in the YAML. They put every Pod into a quality of service (QoS) class. When a node runs short of memory, the kubelet uses these classes to choose which Pods to evict first.

            There are three classes:
            - Guaranteed: every container has CPU and memory requests equal to its limits. These Pods are evicted last.
            - Burstable: at least one container has a request or a limit, but the Pod is not Guaranteed.
            - BestEffort: no requests or limits at all. These Pods are evicted first.

            Check the lab's Pods with `kubectl get pod <name> -n hello -o jsonpath='{.status.qosClass}'`. They are Burstable: they request CPU and memory but limit only memory. Among Burstable Pods, the ones using the most memory above their request go first.

            How do you pick good numbers? Start from data, not guesses:
            1. Run the app under normal load and watch `kubectl top pods` (or a Grafana dashboard on Day 21).
            2. Set the memory request near normal use and the memory limit with room for peaks.
            3. Set the CPU request near normal use. The HPA's percentage is based on it, so a request that is far too high makes scaling late.
            4. Check again after big changes to the app.

            Two related tools are worth knowing by name:
            - The Vertical Pod Autoscaler (VPA) watches real usage and suggests or sets requests for you. Do not let it and an HPA both act on CPU for the same Deployment, or they fight.
            - KEDA scales on events, such as the length of a queue, and can scale a Deployment down to zero Pods when there is no work.

            Probes have edge cases too. A readiness probe that is too strict (a short timeout on a slow dependency) can take every Pod out of the Service during a small hiccup. Then a short slowdown turns into a full outage. That is why the lab sets `timeoutSeconds: 2` and `failureThreshold: 2` for readiness instead of the tightest values. Tune probes with the same care as alerts: they act on their own, at night, without asking you.
        """),
    },
    "sources": src("probes_task", "resources", "hpa", "metrics"),
}

# ---------------------------------------------------------------- d19
CHART = "chart/hello-devops/"
d19 = {
    "id": "d19",
    "title": "Ingress, Gateway API, storage and Helm",
    "minutes": 40,
    "goal": "By the end you can route outside traffic to your app with the Gateway API, explain how Kubernetes storage works, and ship the app as a Helm chart you can install, upgrade and roll back.",
    "guess": {
        "q": "Your company runs ingress-nginx, and that project was retired in March 2026. What happens to your running clusters?",
        "options": [
            "They stop routing traffic on the retirement date",
            "Kubernetes deletes their Ingress objects for you",
            "They keep working, but get no more fixes, even for security bugs",
            "Nothing changes, because it still ships monthly releases",
        ],
        "answer": 2,
        "why": "The maintainers said existing installs keep working, but after retirement there are no releases, bug fixes or security patches. That is why teams are moving to the Gateway API or another controller.",
    },
    "terms": [
        {"term": "Ingress", "plain": "An older Kubernetes object for HTTP routing from outside to Services; its API is now frozen."},
        {"term": "Gateway API", "plain": "The newer, official set of routing objects (GatewayClass, Gateway, HTTPRoute) that replaces Ingress."},
        {"term": "HTTPRoute", "plain": "A Gateway API object with rules, such as host names and paths, that send requests to Services."},
        {"term": "PersistentVolumeClaim", "plain": "An app's request for storage of a given size; Kubernetes finds or creates a volume for it."},
        {"term": "StorageClass", "plain": "A type of storage the cluster offers, which can create volumes on demand."},
        {"term": "Helm chart", "plain": "A package of templated Kubernetes YAML plus default values."},
        {"term": "Release", "plain": "One installed copy of a Helm chart, with a numbered history of revisions."},
    ],
    "sections": [
        {
            "h": "Getting traffic in: Ingress, and why it is fading",
            "body": T("""
                So far you reached the app through a NodePort or `port-forward`. Real users need one public entry point that sends `shop.example.com/api` to one Service and `/` to another. That is HTTP routing.

                For years, Kubernetes did this with Ingress. An Ingress object holds routing rules, and an Ingress controller (a proxy running in the cluster) carries them out. The most popular controller was ingress-nginx.

                Two things have changed:
                - The Ingress API is frozen. It still works and will not be removed, but it gets no new features. The Kubernetes docs recommend the Gateway API instead.
                - ingress-nginx is retired. Best-effort maintenance ended in March 2026, and its repository is now read-only. Existing installs keep running, but there are no more releases, bug fixes or security patches.

                If you meet ingress-nginx at work, treat it as a migration task. [Ingress2Gateway](https://kubernetes.io/blog/2026/03/20/ingress2gateway-1-0-release) converts Ingress objects, including many nginx annotations, into Gateway API objects for you to review.
            """),
            "refs": [L["ingress"], L["retire"], L["ingress_nginx"]],
        },
        {
            "h": "The Gateway API: roles and routes",
            "body": T("""
                The **Gateway API** is the newer, official way to route traffic into a cluster. It does not come built in. You add it as CRDs (custom resource definitions: new object types the API server learns), plus a controller that carries them out.

                It splits the job into objects owned by different people:
                - GatewayClass: which controller to use. The platform team sets it up once. Ours is Envoy Gateway.
                - Gateway: an entry point with listeners, such as "HTTP on port 80". The controller starts a proxy for it.
                - HTTPRoute: routing rules owned by an app team, such as "`/` goes to Service `hello-devops` on port 80".

                Why is this better than Ingress? Features that Ingress pushed into controller-specific annotations are now real fields: header matching, traffic splits by weight, redirects and more. App teams can add routes without touching the shared Gateway. And the core features work the same across implementations, such as Envoy Gateway, Istio, Cilium, Traefik and the big clouds' own gateways.
            """),
            "refs": [L["gateway"], L["gwapi"]],
        },
        {
            "h": "Envoy Gateway on kind",
            "body": T("""
                You need one implementation to try it. This course uses Envoy Gateway, from the CNCF Envoy project. It installs on kind with one Helm command, and its chart brings the Gateway API CRDs too.

                Here is what happens when you apply `k8s/gateway/`:
                1. The GatewayClass `eg` tells Envoy Gateway that it owns Gateways of this class.
                2. The Gateway `hello-gateway` makes Envoy Gateway start an Envoy proxy Deployment and Service in `envoy-gateway-system`.
                3. The HTTPRoute attaches to the Gateway and points at the `hello-devops` Service.
                4. Envoy Gateway turns the route into proxy settings, and the proxy starts forwarding.

                One kind detail: the proxy's Service has type LoadBalancer. On a cloud, that creates a real load balancer with a public address. kind has no cloud, so the Gateway gets no address. You reach the proxy with `kubectl port-forward` instead, as the [Envoy Gateway quickstart](https://gateway.envoyproxy.io/docs/tasks/quickstart/) shows. Everything behind it is real routing.

                The Gateway files live in `k8s/gateway/`, outside the main kustomization on purpose. They only work after Envoy Gateway is installed.
            """),
            "refs": [L["eg_qs"], L["eg_helm"]],
        },
        {
            "h": "Storage: volumes that outlive Pods",
            "body": T("""
                Containers lose their files when they restart. For data that must survive, Kubernetes has three objects:
                - PersistentVolume (PV): a piece of real storage, such as a cloud disk.
                - PersistentVolumeClaim (PVC): a request from an app, such as "1Gi that one node can write".
                - StorageClass: a type of storage that can create PVs on demand.

                You mostly write PVCs. The StorageClass creates a matching PV for you, which is called dynamic provisioning. kind ships a default StorageClass named `standard` that uses a folder on the node. On EKS, AKS or GKE, the default class creates a cloud disk.

                Databases need more than a disk, so they run as a StatefulSet instead of a Deployment. Each Pod gets a stable name (`redis-0`, `redis-1`) and its own PVC, and the Pods start in order.

                Running databases in Kubernetes is possible, but backups, upgrades and failover are then your job. Many teams use a managed database (Amazon RDS, Azure Database, Cloud SQL) and keep the cluster for stateless apps. The lab's Redis has no volume, because it only holds a demo counter.
            """),
            "refs": [L["pv"], L["sc"], L["sts"]],
        },
        {
            "h": "Helm: packages for Kubernetes",
            "body": T("""
                hello-devops is now seven YAML files. Imagine ten teams using it, each with a different image tag, replica count and greeting. Helm, the package manager for Kubernetes, handles this.

                Three words to learn:
                - Chart: a folder with templates (YAML with `{{ }}` placeholders), `values.yaml` (the defaults) and `Chart.yaml` (name and version).
                - Values: the settings you pass in with `--set key=value` or `-f my-values.yaml`.
                - Release: one installed copy of a chart, with a name and numbered revisions.

                The commands follow the life of a release:
                - `helm install` and `helm upgrade`: render the templates with your values and apply them. Each run makes a new revision.
                - `helm rollback`: return to an earlier revision.
                - `helm template` and `helm lint`: print or check the YAML without touching the cluster.

                Helm 4 is the current version, and day to day it feels like Helm 3. Two changes are worth knowing. New installs use server-side apply, where the API server merges the changes. And the `--atomic` flag is now called `--rollback-on-failure`.
            """),
            "refs": [L["using_helm"], L["helm4"], L["helm_video"]],
        },
        {
            "h": "Kustomize: the template-free option",
            "body": T("""
                Helm is not the only way to vary YAML. Kustomize is built into kubectl, and you already use it: `kubectl apply -k k8s` reads `k8s/kustomization.yaml`.

                Kustomize has no templates. You keep plain YAML as a base and add overlays that patch it. A typical layout:
                - `k8s/` is the base: the app as it is today.
                - `overlays/dev/kustomization.yaml` points at the base and sets 1 replica.
                - `overlays/prod/kustomization.yaml` points at the same base and sets 6 replicas and a newer image tag.

                `kubectl kustomize overlays/prod` prints the result, and `kubectl apply -k overlays/prod` applies it.

                Which one should you use? Helm is the usual way to install other people's software, such as databases, monitoring or Argo CD. Kustomize is popular for your own apps, because the files stay plain YAML. Many teams use both. On Day 20, Argo CD reads your `k8s/` folder with Kustomize.
            """),
            "refs": [L["kustomize"]],
        },
    ],
    "analogy": "A Helm chart is like a recipe card with blanks: \"___ grams of sugar, bake for ___ minutes\". `values.yaml` fills in the usual amounts, and `--set` changes one of them for tonight. The kitchen writes each cooking in a logbook (the release history), so you can make an earlier version again. Where it breaks: a recipe makes a new dish each time, while `helm upgrade` changes the dish that is already on the table.",
    "diagram": D19,
    "diagram_caption": "The GatewayClass picks Envoy Gateway, the Gateway makes it create an Envoy proxy, and the HTTPRoute tells the proxy to send requests to the Service.",
    "worked": {
        "title": "Install, upgrade and roll back a public chart",
        "steps": [
            {
                "say": "Install podinfo, a small demo web app, straight from its OCI registry into a new namespace. Helm first prints two lines about the chart it pulled. Then it shows a summary like this one, followed by the chart's notes.",
                "code": T("""
                    $ helm install my-podinfo oci://ghcr.io/stefanprodan/charts/podinfo -n demo --create-namespace
                    NAME: my-podinfo
                    LAST DEPLOYED: Fri Oct 30 10:15:42 2026
                    NAMESPACE: demo
                    STATUS: deployed
                    REVISION: 1
                    DESCRIPTION: Install complete
                """),
                "lang": "console",
            },
            {
                "say": "Change two values. `helm show values` lists every setting a chart accepts; podinfo has `replicaCount` and `ui.message` among them. Helm renders the chart again, applies the difference, and the revision goes up. In real work, also pin the chart with `--version`.",
                "code": T("""
                    $ helm upgrade my-podinfo oci://ghcr.io/stefanprodan/charts/podinfo -n demo --set replicaCount=2 --set ui.message="Hello from Helm"
                    Release "my-podinfo" has been upgraded. Happy Helming!
                    NAME: my-podinfo
                    LAST DEPLOYED: Fri Oct 30 10:18:03 2026
                    NAMESPACE: demo
                    STATUS: deployed
                    REVISION: 2
                """),
                "lang": "console",
            },
            {
                "say": "Look at the history. Each install, upgrade or rollback is a numbered revision. Helm stores them as Secrets in the release's namespace.",
                "code": T("""
                    $ helm history my-podinfo -n demo
                    REVISION  UPDATED                   STATUS      CHART           APP VERSION  DESCRIPTION
                    1         Fri Oct 30 10:15:42 2026  superseded  podinfo-6.17.0  6.17.0       Install complete
                    2         Fri Oct 30 10:18:03 2026  deployed    podinfo-6.17.0  6.17.0       Upgrade complete
                """),
                "lang": "console",
            },
            {
                "say": "Roll back to revision 1. Helm does not erase revision 2. It writes a new revision 3 with the same content as revision 1, so the history stays honest.",
                "code": T("""
                    $ helm rollback my-podinfo 1 -n demo
                    Rollback was a success! Happy Helming!
                    $ helm history my-podinfo -n demo
                    REVISION  UPDATED                   STATUS      CHART           APP VERSION  DESCRIPTION
                    1         Fri Oct 30 10:15:42 2026  superseded  podinfo-6.17.0  6.17.0       Install complete
                    2         Fri Oct 30 10:18:03 2026  superseded  podinfo-6.17.0  6.17.0       Upgrade complete
                    3         Fri Oct 30 10:19:30 2026  deployed    podinfo-6.17.0  6.17.0       Rollback to 1
                """),
                "lang": "console",
            },
            {
                "say": "Remove the release. Helm deletes every object it created. The namespace stays, so delete it too.",
                "code": "$ helm uninstall my-podinfo -n demo\nrelease \"my-podinfo\" uninstalled\n$ kubectl delete namespace demo\nnamespace \"demo\" deleted",
                "lang": "console",
            },
        ],
    },
    "code": [
        {"lang": "yaml", "title": "k8s/gateway/kustomization.yaml", "src": lab("k8s/gateway/kustomization.yaml"), "run": "kubectl apply -k k8s/gateway"},
        {"lang": "yaml", "title": "k8s/gateway/gatewayclass.yaml", "src": lab("k8s/gateway/gatewayclass.yaml"), "run": "kubectl apply -k k8s/gateway"},
        {"lang": "yaml", "title": "k8s/gateway/gateway.yaml", "src": lab("k8s/gateway/gateway.yaml"), "run": "kubectl apply -k k8s/gateway"},
        {"lang": "yaml", "title": "k8s/gateway/httproute.yaml", "src": lab("k8s/gateway/httproute.yaml"), "run": "kubectl apply -k k8s/gateway"},
        {"lang": "yaml", "title": CHART + "Chart.yaml", "src": lab(CHART + "Chart.yaml"), "run": "helm lint chart/hello-devops"},
        {"lang": "yaml", "title": CHART + "values.yaml", "src": lab(CHART + "values.yaml"), "run": "helm lint chart/hello-devops"},
        {"lang": "yaml", "title": CHART + "templates/configmap.yaml", "src": lab(CHART + "templates/configmap.yaml"), "run": "helm template hello chart/hello-devops"},
        {"lang": "yaml", "title": CHART + "templates/deployment.yaml", "src": lab(CHART + "templates/deployment.yaml"), "run": "helm template hello chart/hello-devops"},
        {"lang": "yaml", "title": CHART + "templates/service.yaml", "src": lab(CHART + "templates/service.yaml"), "run": "helm template hello chart/hello-devops"},
        {"lang": "yaml", "title": CHART + "templates/httproute.yaml", "src": lab(CHART + "templates/httproute.yaml"), "run": "helm template hello chart/hello-devops --set httpRoute.enabled=true"},
        {"lang": "text", "title": CHART + "templates/NOTES.txt", "src": lab(CHART + "templates/NOTES.txt"), "run": "helm install hello chart/hello-devops -n hello-helm --create-namespace --dry-run=client"},
        {"lang": "text", "title": CHART + ".helmignore", "src": lab(CHART + ".helmignore"), "run": "helm package chart/hello-devops"},
        {"lang": "yaml", "title": "chart/kind-values.yaml", "src": lab("chart/kind-values.yaml"), "run": "helm install hello chart/hello-devops -n hello-helm --create-namespace -f chart/kind-values.yaml"},
    ],
    "commands": [
        {"cmd": "helm install eg oci://docker.io/envoyproxy/gateway-helm --version v1.9.3 -n envoy-gateway-system --create-namespace", "what": "Install Envoy Gateway and the Gateway API CRDs. Check the quickstart for the current version."},
        {"cmd": "kubectl wait --timeout=5m -n envoy-gateway-system deployment/envoy-gateway --for=condition=Available", "what": "Wait until the Envoy Gateway controller is running."},
        {"cmd": "kubectl apply -k k8s/gateway", "what": "Create the GatewayClass, the Gateway and the HTTPRoute."},
        {"cmd": "kubectl get gateway,httproute -A", "what": "List Gateways and HTTPRoutes in all namespaces."},
        {"cmd": "kubectl get storageclass", "what": "List the types of storage the cluster offers (kind has `standard`)."},
        {"cmd": "helm lint chart/hello-devops", "what": "Check a chart for mistakes."},
        {"cmd": "helm template hello chart/hello-devops -f chart/kind-values.yaml", "what": "Print the YAML the chart would create, without installing anything."},
        {"cmd": "helm install hello chart/hello-devops -n hello-helm --create-namespace -f chart/kind-values.yaml", "what": "Install the chart as a release named hello."},
        {"cmd": "helm upgrade hello chart/hello-devops -n hello-helm -f chart/kind-values.yaml", "what": "Apply changed values or templates as a new revision."},
        {"cmd": "helm history hello -n hello-helm", "what": "List a release's revisions."},
        {"cmd": "helm rollback hello 1 -n hello-helm", "what": "Return to revision 1 (Helm records it as a new revision)."},
        {"cmd": "kubectl kustomize k8s", "what": "Print what Kustomize builds from a folder, without applying it."},
    ],
    "mistake": "Running `helm upgrade` with one new `--set` and losing the values you set at install time. When you pass values on an upgrade, Helm starts again from the chart's defaults plus only the values you give now. Keep your settings in a values file (like `chart/kind-values.yaml`) and pass it with `-f` on every install and upgrade.",
    "real_world": "At PayLite, the platform team owns one shared Gateway per cluster, with the TLS certificates, and each product team adds HTTPRoutes for its own paths. Third-party tools such as Envoy Gateway and the monitoring stack are installed from Helm charts pinned to exact versions. The team's own services use Kustomize overlays for dev and prod, and the card database is a managed service outside the cluster.",
    "task": {
        "title": "Route traffic through a Gateway and ship your own chart",
        "steps": [
            "Install Envoy Gateway with the Helm command from its quickstart, then wait until the `envoy-gateway` Deployment is Available.",
            "Write the files in `k8s/gateway/` and apply them with `kubectl apply -k k8s/gateway`.",
            "Find the Envoy proxy Service for your Gateway and port-forward local port 8888 to its port 80. Keep that terminal open.",
            "Run `curl localhost:8888` and check that hello-devops answers through the Gateway.",
            "Write the chart in `chart/hello-devops/`. Run `helm lint` and `helm template`, and read the YAML it prints.",
            "Write `chart/kind-values.yaml` that turns the route on with host name `helm.local`, and install the chart as release `hello` in namespace `hello-helm`.",
            "Run `curl -H \"Host: helm.local\" localhost:8888`. The greeting should be the chart's, not the ConfigMap's.",
            "Change the greeting in your values file, run `helm upgrade` with it, check `helm history`, then roll back to revision 1 and curl again.",
            "Remove the chart with `helm uninstall hello -n hello-helm`. Keep Envoy Gateway and the cluster.",
        ],
        "hints": [
            "The proxy Service carries two labels: `gateway.envoyproxy.io/owning-gateway-name=hello-gateway` and `gateway.envoyproxy.io/owning-gateway-namespace=hello`. Select on them with `kubectl get svc -n envoy-gateway-system -l ...`.",
            "The values you need are `httpRoute.enabled` and `httpRoute.hostname`. `--create-namespace` saves a step.",
            "Getting the Kubernetes greeting instead of the Helm one? Your request did not match the chart's route. Check the Host header and `kubectl get httproute -A`.",
        ],
        "done_when": "`curl localhost:8888` returns the ConfigMap's greeting, and `curl -H \"Host: helm.local\" localhost:8888` returns the chart's greeting, both through the Gateway.",
    },
    "explain_back": {
        "prompt": "Explain in 3 to 4 sentences how a request from `curl localhost:8888` reaches a hello-devops Pod. Mention the Gateway, the HTTPRoute and the Service.",
        "answer": "Port-forward sends my request to the Envoy proxy that Envoy Gateway started for the Gateway `hello-gateway`. Envoy checks the HTTPRoutes attached to that Gateway and picks the rule that matches the host name and path. That rule's backend is the `hello-devops` Service, so Envoy forwards the request to one of the ready Pods behind it. The GatewayClass only says which controller, Envoy Gateway, builds and runs this proxy.",
    },
    "recap": [
        "The Ingress API is frozen, and ingress-nginx is retired with no security fixes since March 2026.",
        "Gateway API splits roles: GatewayClass (controller), Gateway (entry point), HTTPRoute (app rules).",
        "On kind, Envoy Gateway routes for real, but you reach its proxy with port-forward because there is no cloud load balancer.",
        "PVCs request storage, StorageClasses create volumes, and StatefulSets give databases stable names and disks.",
        "Helm charts are templates plus values; every install, upgrade or rollback is a numbered revision.",
        "Kustomize patches plain YAML with overlays; Helm is the usual way to install third-party software.",
    ],
    "check": [
        {
            "q": "Your team wants requests for `/api` to go to the `api` Service and everything else to `web`. In Gateway API terms, what do you write?",
            "options": [
                "A second GatewayClass for the api traffic",
                "An HTTPRoute with two rules that match on path",
                "A NodePort Service on port 30080",
                "A StorageClass for each Service",
            ],
            "answer": 1,
            "why": "Routing rules live in an HTTPRoute: one rule matches the `/api` prefix and sends it to `api`, another sends `/` to `web`.",
        },
        {
            "q": "You run `helm upgrade shop ./chart -f prod.yaml` with a new image tag. Two minutes later errors spike. What is the quickest way back?",
            "options": [
                "Edit the Deployment with `kubectl edit`",
                "Delete the namespace and install again",
                "`helm uninstall shop`, then install again",
                "`helm rollback shop` to the last good revision",
            ],
            "answer": 3,
            "why": "Helm keeps every revision, so `helm rollback` re-applies the last good one as a new revision, with no reinstall and no downtime.",
        },
        {
            "q": "A Postgres Pod stores its data on a PVC. The Pod is deleted and comes back on the same node. What happens to the data?",
            "options": [
                "It is still there: the PVC and its volume outlive the Pod",
                "It is lost, because container files never survive",
                "It moves into etcd until the new Pod starts",
                "It is copied into the container image",
            ],
            "answer": 0,
            "why": "A PVC's volume has its own life cycle, so a new Pod that mounts the same claim sees the same files.",
        },
    ],
    "interview": [
        {
            "q": "Why is the Gateway API replacing Ingress?",
            "a": "Ingress covered only basic host and path routing, so each controller added its own annotations, and configs did not move between controllers. The Gateway API makes those features real fields, such as header matching and weighted traffic splits. It also splits ownership: platform teams own GatewayClasses and Gateways, and app teams own Routes. The Ingress API is now frozen, and ingress-nginx was retired in March 2026 with no further security fixes, so new clusters should start with a Gateway API implementation.",
        },
        {
            "q": "When would you choose Helm, and when Kustomize?",
            "a": "Helm is a package manager. It is the standard way to install and upgrade third-party software, and it tracks releases so you can roll back. Its templates are powerful but can get hard to read. Kustomize keeps plain YAML and applies overlays, which suits your own apps with a few differences per environment. Many teams use Helm for platform tools and Kustomize for their own services, and GitOps tools like Argo CD support both.",
        },
    ],
    "deeper": {
        "minutes": 15,
        "body": T("""
            The lab's Redis forgets the visit count whenever its Pod restarts. Here is how you would fix that with a StatefulSet and a volume. Treat it as a sketch to try on your own, in a copy of `redis.yaml`.

            1. Change `kind: Deployment` to `kind: StatefulSet`, and add `serviceName: redis` under `spec`.
            2. Add a `volumeClaimTemplates` section: a PVC template named `data`, with access mode `ReadWriteOnce` and a request of `1Gi`. The StatefulSet makes one PVC per Pod, called `data-redis-0`.
            3. Mount that volume at `/data` in the Redis container. The official Redis image keeps its files there.
            4. Turn on saving: run Redis with `redis-server --appendonly yes`, so each write also goes to disk.
            5. Apply it, count a few visits, then delete the Pod `redis-0`. The StatefulSet recreates it with the same name and the same PVC, and the count carries on.

            Check the pieces with `kubectl get pvc -n hello` and `kubectl get pv`. On kind, the PV is a folder inside a node container. Delete the cluster and the data is gone, which is fine for practice.

            Things that surprise people:
            - Deleting a StatefulSet does not delete its PVCs. This protects data, but you must clean up by hand.
            - `ReadWriteOnce` means one node at a time. A Pod on another node cannot mount the volume.
            - kind's `standard` class uses `volumeBindingMode: WaitForFirstConsumer`. The volume is created only when a Pod needs it, on that Pod's node.
            - A StorageClass's `reclaimPolicy` decides what happens to the volume when you delete the PVC. `Delete` removes it, and `Retain` keeps it for manual recovery.

            Why do many teams still avoid this for important data? A real database needs tested backups, version upgrades, replication and failover. Operators (controllers built for one database, such as CloudNativePG for Postgres) automate much of this. A managed database does it for you, for a price. For a cache or a lab, a StatefulSet with a PVC is enough.

            One more Helm detail is worth a look in your chart. `templates/deployment.yaml` has a `checksum/config` annotation that holds a hash of the rendered ConfigMap. When you change the greeting, the hash changes, so the Pod template changes and Kubernetes rolls out new Pods. Without it, `helm upgrade` would update the ConfigMap while the old Pods kept the old greeting. The [Helm tips page](https://helm.sh/docs/howto/charts_tips_and_tricks/) calls this pattern "automatically roll deployments".
        """),
    },
    "sources": src("gateway", "eg_qs", "pv", "using_helm"),
}

# ---------------------------------------------------------------- part
part = {
    "part": 5,
    "title": "Kubernetes",
    "intro": "Part 5 takes the image you built in Part 2 and runs it on Kubernetes, the system most teams use to run containers across many machines. You build a real three-node cluster on your Mac with kind, then add Deployments, Services, config, health checks, autoscaling, a Gateway and a Helm chart. Everything stays local and free.",
    "lessons": [d16, d17, d18, d19],
    "recap": [
        "Kubernetes keeps the actual state of a cluster equal to the desired state you write in YAML.",
        "The control plane decides; kubelets on worker nodes run Pods; kind runs it all in Docker on your Mac.",
        "Deployments give you replicas, self-healing and rolling updates; Services give Pods one stable name.",
        "ConfigMaps and Secrets keep settings out of images, and Secrets need protection beyond base64.",
        "Probes tell Kubernetes when to restart a container and when to stop sending it traffic.",
        "Requests, limits and the HPA control where Pods run, how much they may use and how many there are.",
        "The Gateway API routes outside traffic in; the old ingress-nginx controller is retired.",
        "Helm packages apps as charts with values and releases; Kustomize patches plain YAML.",
    ],
    "flashcards": [
        {"front": "What does a Kubernetes controller do?", "back": "It runs a loop: compare desired state with actual state, then act to close the gap."},
        {"front": "Name the four main control plane components.", "back": "API server, etcd, scheduler and controller manager."},
        {"front": "What runs on every worker node?", "back": "The kubelet, kube-proxy and a container runtime such as containerd."},
        {"front": "Which four top-level fields does every manifest have?", "back": "apiVersion, kind, metadata and spec (Kubernetes adds status)."},
        {"front": "Why do you need `kind load docker-image`?", "back": "kind nodes keep their own images, so an image built on your Mac must be copied in."},
        {"front": "What creates the Pods of a Deployment?", "back": "A ReplicaSet, one for each version of the Pod template."},
        {"front": "What do maxSurge and maxUnavailable control?", "back": "How many extra Pods may exist, and how many may be missing, during a rolling update."},
        {"front": "What is the DNS name of Service `web` in namespace `shop`?", "back": "`web.shop.svc.cluster.local`, or just `web` from inside `shop`."},
        {"front": "What happens when a readiness probe fails? A liveness probe?", "back": "Readiness: the Pod gets no Service traffic. Liveness: the kubelet restarts the container."},
        {"front": "Is a Kubernetes Secret encrypted?", "back": "Not by default: it is base64-encoded, which anyone can decode."},
        {"front": "What does OOMKilled mean?", "back": "The container used more memory than its limit, so the kernel killed it."},
        {"front": "What does an HPA need to work on kind?", "back": "metrics-server (with `--kubelet-insecure-tls` on kind) and CPU requests on the Pods."},
        {"front": "What are the three main Gateway API objects?", "back": "GatewayClass, Gateway and HTTPRoute."},
        {"front": "What is the status of ingress-nginx?", "back": "Retired in March 2026: existing installs run, but get no releases or security fixes."},
        {"front": "What is a Helm release?", "back": "One installed copy of a chart, with a numbered history of revisions."},
        {"front": "PVC or PV: which one does an app write?", "back": "The app writes a PVC (a request); a StorageClass or an admin provides the PV."},
    ],
    "quiz": [
        {
            "q": "A Deployment wants 3 replicas. A node fails and 1 Pod disappears. Which part creates the replacement Pod object?",
            "options": ["The kubelet on the node that failed", "The ReplicaSet controller", "The etcd database", "kube-proxy on each node"],
            "answer": 1,
            "why": "The ReplicaSet controller (in the controller manager) sees 2 Pods where 3 are wanted and creates a new one; the scheduler then places it.",
        },
        {
            "q": "On kind, `kubectl get pods` shows `ImagePullBackOff` for `hello-devops:1.2.0`. What is the most likely cause?",
            "options": [
                "The image was never loaded with `kind load`",
                "The readiness probe path is wrong",
                "The memory limit is too low",
                "The Service selector does not match",
            ],
            "answer": 0,
            "why": "kind nodes only have images you load into them; otherwise the kubelet tries Docker Hub and fails.",
        },
        {
            "q": "Which event makes Kubernetes stop sending traffic to a Pod without restarting it?",
            "options": ["Its liveness probe fails", "It goes over its CPU limit", "Its readiness probe fails", "Its startup probe passes"],
            "answer": 2,
            "why": "A failing readiness probe removes the Pod from the Service's endpoints; a failing liveness probe restarts it.",
        },
        {
            "q": "You need different replica counts for dev and prod, but want plain YAML without a template language. What fits best?",
            "options": [
                "A Helm chart with if-statements",
                "A second cluster per environment",
                "One big YAML file with comments",
                "Kustomize overlays on a shared base",
            ],
            "answer": 3,
            "why": "Kustomize overlays patch a plain YAML base for each environment, without templates.",
        },
        {
            "q": "Outside requests for path `/` must reach Service `web`. With the Gateway API, which object holds that rule?",
            "options": ["HTTPRoute", "GatewayClass", "StorageClass", "ConfigMap"],
            "answer": 0,
            "why": "An HTTPRoute holds matching rules and backends; the Gateway is the entry point, and the GatewayClass picks the controller.",
        },
        {
            "q": "After `helm upgrade app ./chart --set replicas=4`, a setting you passed at install time with `--set` is gone. Why?",
            "options": [
                "Helm upgrades always reset routes",
                "The chart has a bug in its template",
                "Helm used chart defaults plus only the new flags",
                "Kubernetes rejected the old setting",
            ],
            "answer": 2,
            "why": "When you pass values on upgrade, Helm starts from the chart's defaults plus those values, unless you pass the same values file again or use --reuse-values.",
        },
        {
            "q": "You change one line in `app.py` and rebuild the hello-devops image. Why is the `pip install` step fast?",
            "options": [
                "Docker never runs RUN steps twice",
                "Its layer is cached, since requirements.txt did not change",
                "pip reuses packages from your Mac's venv",
                "The base image already includes Flask",
            ],
            "answer": 1,
            "why": "The Dockerfile copies requirements.txt and installs packages before it copies app.py, so that layer's inputs are unchanged and Docker reuses it.",
            "from": "Part 2",
        },
        {
            "q": "Kubernetes and Terraform both compare desired and actual state. What does Terraform use to remember what it created?",
            "options": ["The plan output", "The provider block", "The .tf source files", "The state file"],
            "answer": 3,
            "why": "Terraform records what it manages in its state; `terraform plan` compares your code with that state and the real world. Unlike Kubernetes, it acts only when you run apply.",
            "from": "Part 4",
        },
    ],
}

OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(part, ensure_ascii=False, indent=1) + "\n")
print("wrote", OUT)

# Extra checks: section word counts and the scratch YAML files.
for les in part["lessons"]:
    words = sum(len(re.findall(r"[A-Za-z0-9'`]+", s["body"])) for s in les["sections"])
    print(les["id"], "section words:", words, "deeper words:", len(re.findall(r"[A-Za-z0-9'`]+", les["deeper"]["body"])))
scratch = pathlib.Path(__file__).resolve().parent
(scratch / "pod.yaml").write_text(POD_YAML + "\n")
(scratch / "deployment-v1.yaml").write_text(DEPLOY_V1 + "\n")
