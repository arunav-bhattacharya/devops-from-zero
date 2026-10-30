"""Day 30: Why Kubernetes, and how a cluster works."""
from svg import box, arrow, cap, svg

DIAGRAM = svg(300, "How kubectl apply flows from the API server to a Pod on a worker node", [
    box(16, 36, 116, 44, "bx", "kubectl"),
    box(172, 36, 116, 44, "bxo", "API server"),
    box(328, 36, 112, 44, "bxg", "etcd"),
    cap(500, 62, "Control plane"),
    box(16, 132, 116, 44, "bxp", "Scheduler"),
    box(328, 132, 112, 44, "bxp", "Controllers"),
    box(172, 236, 116, 44, "bxt", "kubelet"),
    box(328, 236, 112, 44, "bxt", "containerd"),
    box(472, 236, 72, 44, "bx", "Pod"),
    cap(74, 262, "Worker node"),
    arrow(132, 58, 170, 58),
    arrow(288, 58, 326, 58),
    arrow(110, 132, 190, 82, dashed=True),
    arrow(350, 132, 270, 82, dashed=True),
    arrow(230, 80, 230, 234, dashed=True),
    arrow(288, 258, 326, 258),
    arrow(440, 258, 470, 258),
    cap(100, 108, "watch"),
    cap(372, 110, "watch"),
    cap(266, 200, "watch"),
])

L = {
    "id": "d30",
    "title": "Why Kubernetes, and how a cluster works",
    "minutes": 45,
    "goal": "By the end you can explain what each part of a Kubernetes cluster does, follow one `kubectl apply` from your terminal to a running container, and run the course's three-node cluster on your Mac with kind.",
    "guess": {
        "q": "You run `kubectl apply -f app.yaml` and it prints `deployment.apps/web created` in under a second. What has happened at that moment?",
        "options": [
            "The containers are already running on a node",
            "The request is stored, and other parts start the containers soon after",
            "kubectl has copied the image to every node in the cluster",
            "The scheduler has picked a node and waits for your approval",
        ],
        "answer": 1,
        "why": "The API server checks your request, saves it in etcd and answers straight away. Controllers, the scheduler and the kubelet act on it over the next seconds, which is why you check with `kubectl get pods` afterwards.",
    },
    "terms": [
        {"term": "Cluster", "plain": "A group of machines that Kubernetes runs and manages as one system."},
        {"term": "Node", "plain": "One machine in a cluster that runs containers. On kind, each node is a Docker container."},
        {"term": "Control plane", "plain": "The part of a cluster that stores what you asked for and decides what runs where."},
        {"term": "Desired state", "plain": "What you ask for in a manifest, such as three copies of an image. Kubernetes keeps working to match it."},
        {"term": "Controller", "plain": "A program that keeps comparing desired state with actual state and acts to close any gap."},
        {"term": "kubelet", "plain": "The agent on each node that starts the containers assigned to that node and reports their status."},
        {"term": "kind", "plain": "A tool that runs a real Kubernetes cluster on your laptop, using Docker containers as nodes."},
    ],
    "sections": [
        {
            "h": "The problem Kubernetes solves",
            "body": """On Day 15 you ran hello-devops and Redis with Docker Compose. One `docker compose up` on one laptop, and it worked. Now picture a real product: 40 services, several copies of each, spread over 20 servers.

Someone has to answer these questions all day:
- Which server has room for this container?
- A container crashed at 3 in the morning. Who starts it again?
- A server died. Who moves its containers somewhere else?
- Traffic doubled. Who adds copies, and who removes them later?
- How do you replace version 1 with version 2 without downtime?
- Copies come and go. How does one service find another?

Compose cannot answer them. It knows one machine, and it only acts when you run it. **Kubernetes** answers all of them. It is an open-source system that runs containers across a group of machines called a cluster. People often write it K8s: a K, eight letters, then an s.

Google built Kubernetes from what it learned running its internal system, Borg, and released it as open source in 2014. Today the Cloud Native Computing Foundation (CNCF) looks after it, and every big cloud sells it.

The real change is in how you work. You stop logging in to servers and starting things. You write down the result you want, and Kubernetes keeps making it true.""",
            "refs": [
                {"title": "Kubernetes overview", "url": "https://kubernetes.io/docs/concepts/overview/", "kind": "docs"},
                {"title": "Kubernetes tutorial for beginners, full course (KubeAcademy)", "url": "https://www.youtube.com/watch?v=JB3bP1RXqYo", "kind": "watch"},
            ],
        },
        {
            "h": "Desired state and control loops",
            "body": """With `docker run` you give an order, and Docker carries it out once. Kubernetes works the other way round. You describe the end state, and Kubernetes stores that description as your **desired state**.

Small programs called controllers then run the same loop forever:
1. Read the desired state: what you asked for.
2. Observe the actual state: what is really running.
3. If the two differ, act to make them match.
4. Repeat.

This loop is called reconciliation. The [Kubernetes docs](https://kubernetes.io/docs/concepts/architecture/controller/) compare it to a thermostat. You set 21 degrees, and the thermostat keeps reading the room and switches the heating on or off. You never tell it to heat for ten minutes.

You can see the loop in every object. Each object you write has a `spec` field: your wish. Kubernetes fills in a `status` field: its report on what is real. Controllers work to make status match spec.

Two things follow from this design, and both surprise people at first:
- Kubernetes fixes problems you never told it about. A crashed container or a dead node is just one more gap to close.
- A change made behind Kubernetes' back does not stick. Stop a container directly on a node, and Kubernetes sees the gap and starts it again.

Terraform (Part 6) also compares code with reality, but only when you run `terraform apply`. Kubernetes checks all the time, with nobody at the keyboard.""",
            "refs": [
                {"title": "Controllers", "url": "https://kubernetes.io/docs/concepts/architecture/controller/", "kind": "docs"},
            ],
        },
        {
            "h": "The control plane decides",
            "body": """A cluster has two kinds of parts. The control plane stores your desired state and makes decisions. The nodes run your containers.

One word before we go on. Kubernetes never runs a bare container. It runs Pods. A Pod wraps one container, sometimes a few, and gives it an IP address. Tomorrow is all about Pods.

The control plane has four main components. For each one, it helps to ask what breaks if it stops:
- API server (`kube-apiserver`): the front door. Every request goes through it, from `kubectl` and from the other components. If it stops, `kubectl` fails, but containers that already run keep running.
- etcd: a key-value database that holds the whole cluster state. Only the API server talks to it. Lose etcd without a backup, and the cluster forgets every object.
- Scheduler (`kube-scheduler`): picks a node for each new Pod. If it stops, new Pods wait in `Pending` forever.
- Controller manager (`kube-controller-manager`): runs the built-in control loops, such as the one that keeps three copies running. If it stops, nothing heals itself any more.

Clusters in a cloud add a fifth part, the cloud controller manager. It talks to the cloud provider, for example to create a load balancer.

These components never call each other. They all read and write objects through the API server, and they watch it for changes. This design is why a component can crash, restart, read the current state again and carry on as if nothing happened.""",
            "refs": [
                {"title": "Kubernetes components", "url": "https://kubernetes.io/docs/concepts/overview/components/", "kind": "docs"},
                {"title": "Cluster architecture", "url": "https://kubernetes.io/docs/concepts/architecture/", "kind": "docs"},
            ],
        },
        {
            "h": "The nodes do the work",
            "body": """Every node runs a few programs:
- kubelet: an agent that watches the API server for Pods assigned to its node. It starts their containers, checks on them and reports their status.
- A container runtime, usually containerd: it pulls images and starts containers. The kubelet talks to it through a standard called the CRI (Container Runtime Interface).
- kube-proxy: sets up network rules so traffic sent to a Service reaches the right Pods. Day 33 explains Services.

Your Docker images run here even though the node has no Docker. A Docker image follows the OCI image standard, and containerd runs any OCI image. Kubernetes removed its built-in Docker support (called dockershim) in version 1.24, and image builds did not change at all.

A cluster also runs a few add-ons as ordinary Pods:
- CoreDNS: the cluster's DNS server, so Pods can find Services by name.
- A network plugin (CNI, Container Network Interface): it gives every Pod an IP address and connects Pods across nodes. kind uses a small one called kindnet.

One current detail matters if a cluster ever refuses to start. Linux limits the CPU and memory of containers with a feature called cgroups, which comes in two versions. Since Kubernetes 1.35, the kubelet refuses by default to start on hosts that still use the old cgroup v1. Docker Desktop on a Mac uses cgroup v2, so you are fine, and `docker info | grep -i cgroup` confirms it in seconds.""",
            "refs": [
                {"title": "Nodes", "url": "https://kubernetes.io/docs/concepts/architecture/nodes/", "kind": "docs"},
                {"title": "The cgroups v2 shift (Kubernetes blog)", "url": "https://kubernetes.io/blog/2026/10/06/kubernetes-cgroups-v2-shift/", "kind": "read"},
            ],
        },
        {
            "h": "What happens when you run kubectl apply",
            "body": """This is the most useful picture to carry around, and a classic interview question. Say you apply a Deployment that asks for two copies of nginx. A Deployment is an object that keeps a set number of Pods running (Day 32 covers it). Here is the chain:

1. kubectl reads `~/.kube/config` to find the cluster and your credentials. It sends the YAML to the API server over HTTPS.
2. The API server checks who you are and whether you may do this. It validates the object and stores it in etcd. Then it answers `created`, and kubectl exits.
3. The Deployment controller sees the new Deployment through its watch. It creates a ReplicaSet, a helper object that keeps a set number of identical Pods.
4. The ReplicaSet controller sees the ReplicaSet and creates two Pod objects. They have no node yet.
5. The scheduler sees two Pods without a node. It filters out nodes that cannot take them, scores the rest, and writes a node name into each Pod.
6. The kubelet on each chosen node sees a Pod assigned to it. It asks containerd to pull the image and start the container.
7. The kubelet reports back: the Pod is running, and here is its IP address. The API server stores that in the Pod's status.

Notice who talks to whom. Every arrow goes through the API server, and each component acts on what it sees there. Nobody sends orders to anybody. Each step also leaves a short record called an event, so you can watch the whole chain with `kubectl get events`. The worked example below does exactly that.""",
            "refs": [
                {"title": "Kubernetes scheduler", "url": "https://kubernetes.io/docs/concepts/scheduling-eviction/kube-scheduler/", "kind": "docs"},
                {"title": "Objects in Kubernetes", "url": "https://kubernetes.io/docs/concepts/overview/working-with-objects/", "kind": "docs"},
            ],
        },
        {
            "h": "Managed Kubernetes, and when to skip Kubernetes",
            "body": """In production, few teams run the control plane themselves. Keeping etcd safe, upgrading the cluster a few times a year and patching security holes is real work. Cloud providers sell managed Kubernetes instead. They run and upgrade the control plane, and you run your apps on the nodes:
- Amazon EKS (Elastic Kubernetes Service) on AWS.
- AKS (Azure Kubernetes Service) on Microsoft Azure.
- GKE (Google Kubernetes Engine) on Google Cloud.

Each one also has a mode where the provider runs the nodes too: EKS Auto Mode, AKS Automatic and GKE Autopilot.

Kubernetes still costs people time. Someone must learn it, keep it upgraded and keep it secure. Skip it when:
- You run one or a few services with steady traffic.
- Your small team has nobody to own the platform.
- A simpler service fits, such as a PaaS or serverless containers (Day 10).

A useful test: can you name the person who will upgrade the cluster next spring? If not, start with something simpler.

Your manifests work the same on kind, EKS, AKS and GKE, so practice on a laptop is real practice. The differences sit at the edges: load balancers, disks and identity.""",
            "refs": [
                {"title": "What is Amazon EKS?", "url": "https://docs.aws.amazon.com/eks/latest/userguide/what-is-eks.html", "kind": "docs"},
                {"title": "What is Azure Kubernetes Service (AKS)?", "url": "https://learn.microsoft.com/en-us/azure/aks/what-is-aks", "kind": "docs"},
                {"title": "GKE overview", "url": "https://docs.cloud.google.com/kubernetes-engine/docs/concepts/kubernetes-engine-overview", "kind": "docs"},
            ],
        },
        {
            "h": "kind: a real cluster on your laptop",
            "body": """kind stands for Kubernetes in Docker. Each node is a Docker container that runs its own containerd and kubelet inside. kind uses kubeadm, the official setup tool, to start a real control plane in the first node. So you get the same Kubernetes as a cloud cluster, minus the cloud parts.

The course uses one config file, `kind-config.yaml`, in the root of your repo. It asks for:
- One control-plane node and two workers, so you can watch Pods spread over machines.
- A port mapping from port 30080 on the control-plane node to port 8081 on your Mac. On Day 33 a Service listens on node port 30080, and `curl localhost:8081` reaches it.

When kind creates a cluster called `devops`, it writes a context called `kind-devops` into `~/.kube/config` and switches kubectl to it. A context is a saved pair of cluster and user (Day 31 shows how to list and switch them).

kind has a few limits worth knowing now:
- No cloud load balancers. A Service of type LoadBalancer waits forever unless you add a helper (Day 33).
- The nodes live inside Docker Desktop's Linux VM. Their 172.18.x.x addresses are not reachable from your Mac, so you use port mappings and `kubectl port-forward`.
- It shares your laptop's memory. If nodes turn `NotReady` or Pods get evicted, give Docker Desktop more memory in its settings.

Creating the cluster takes a minute or two, and deleting it takes seconds. You can always start fresh.""",
            "refs": [
                {"title": "kind quick start", "url": "https://kind.sigs.k8s.io/docs/user/quick-start/", "kind": "docs"},
                {"title": "kind configuration", "url": "https://kind.sigs.k8s.io/docs/user/configuration/", "kind": "docs"},
            ],
        },
    ],
    "analogy": "Think of a busy restaurant kitchen. Waiters never talk to cooks: they pin order tickets on a rail (the API server, with etcd as the rail's memory). The head chef reads new tickets and assigns each dish to a station (the scheduler), each station cook makes only the dishes assigned to them (the kubelet), and a manager keeps checking that every table got what it ordered and has dropped plates remade (the controllers). The picture breaks on judgment: a real kitchen improvises when it runs out of something, while Kubernetes only ever works toward exactly what the ticket says.",
    "diagram": DIAGRAM,
    "diagram_caption": "kubectl talks only to the API server. The scheduler, the controllers and the kubelet all watch the API server and act on what they see.",
    "worked": {
        "title": "Watch one apply travel through a cluster",
        "steps": [
            {
                "say": "Create a small throwaway cluster with one node, named `demo`. The first run downloads the node image, which can take a few minutes. kind then points kubectl at the new cluster.",
                "code": "$ kind create cluster --name demo\n...\nSet kubectl context to \"kind-demo\"\n$ kubectl get nodes\nNAME                 STATUS   ROLES           AGE   VERSION\ndemo-control-plane   Ready    control-plane   48s   v1.37.0",
                "lang": "console",
            },
            {
                "say": "Find the control plane. In kind its parts run as Pods in the `kube-system` namespace: the API server, etcd, the scheduler and the controller manager. You also see kube-proxy, CoreDNS and kindnet.",
                "code": "$ kubectl get pods -n kube-system\nNAME                                         READY   STATUS    RESTARTS   AGE\ncoredns-7d764666f9-8xk2v                     1/1     Running   0          95s\ncoredns-7d764666f9-tq9bl                     1/1     Running   0          95s\netcd-demo-control-plane                      1/1     Running   0          101s\nkindnet-5wq8h                                1/1     Running   0          95s\nkube-apiserver-demo-control-plane            1/1     Running   0          101s\nkube-controller-manager-demo-control-plane   1/1     Running   0          101s\nkube-proxy-7lq2c                             1/1     Running   0          95s\nkube-scheduler-demo-control-plane            1/1     Running   0          101s",
                "lang": "console",
            },
            {
                "say": "Ask for two copies of nginx, then look straight away. kubectl came back at once, but the containers are still being created. That is the guess from the top of the page.",
                "code": "$ kubectl create deployment hello-nginx --image=nginx:1.28 --replicas=2\ndeployment.apps/hello-nginx created\n$ kubectl get pods\nNAME                          READY   STATUS              RESTARTS   AGE\nhello-nginx-5d8f6b7c9-qm4zt   0/1     ContainerCreating   0          2s\nhello-nginx-5d8f6b7c9-x7k2p   0/1     ContainerCreating   0          2s",
                "lang": "console",
            },
            {
                "say": "Now read the events in the order they were created, with a column for the component that wrote each one. You can see the chain from the lesson: Deployment controller, ReplicaSet controller, scheduler, then the kubelet. The output below keeps the kubelet lines for one Pod only.",
                "code": "$ kubectl get events --sort-by=.metadata.creationTimestamp \\\n    -o custom-columns=FROM:.reportingComponent,REASON:.reason,MESSAGE:.message\nFROM                    REASON              MESSAGE\ndeployment-controller   ScalingReplicaSet   Scaled up replica set hello-nginx-5d8f6b7c9 from 0 to 2\nreplicaset-controller   SuccessfulCreate    Created pod: hello-nginx-5d8f6b7c9-x7k2p\nreplicaset-controller   SuccessfulCreate    Created pod: hello-nginx-5d8f6b7c9-qm4zt\ndefault-scheduler       Scheduled           Successfully assigned default/hello-nginx-5d8f6b7c9-x7k2p to demo-control-plane\ndefault-scheduler       Scheduled           Successfully assigned default/hello-nginx-5d8f6b7c9-qm4zt to demo-control-plane\nkubelet                 Pulling             Pulling image \"nginx:1.28\"\nkubelet                 Pulled              Successfully pulled image \"nginx:1.28\" in 6.1s (6.1s including waiting). Image size: 72218103 bytes.\nkubelet                 Created             Container created\nkubelet                 Started             Container started",
                "lang": "console",
            },
            {
                "say": "Watch the control loop work. Delete one Pod. The ReplicaSet now counts one Pod where it wants two, so it creates a replacement with a new name.",
                "code": "$ kubectl delete pod hello-nginx-5d8f6b7c9-x7k2p\npod \"hello-nginx-5d8f6b7c9-x7k2p\" deleted from default namespace\n$ kubectl get pods\nNAME                          READY   STATUS    RESTARTS   AGE\nhello-nginx-5d8f6b7c9-qm4zt   1/1     Running   0          2m10s\nhello-nginx-5d8f6b7c9-w9tn6   1/1     Running   0          5s",
                "lang": "console",
            },
            {
                "say": "Delete the practice cluster. This removes the node container and the `kind-demo` context, so kubectl no longer points at it.",
                "code": "$ kind delete cluster --name demo\nDeleting cluster \"demo\" ...",
                "lang": "console",
            },
        ],
    },
    "code": [
        {
            "lang": "yaml",
            "title": "kind-config.yaml",
            "src": open("/home/user/devops-from-zero/labs/hello-devops/kind-config.yaml").read().rstrip("\n"),
            "run": "kind create cluster --name devops --config kind-config.yaml",
        },
    ],
    "commands": [
        {"cmd": "docker info | grep -i cgroup", "what": "Check that Docker uses cgroup v2. You want to see `Cgroup Version: 2`."},
        {"cmd": "kind create cluster --name devops --config kind-config.yaml", "what": "Create the course cluster: one control-plane node and two workers."},
        {"cmd": "kind get clusters", "what": "List the kind clusters on this machine."},
        {"cmd": "kubectl config current-context", "what": "Show which cluster kubectl talks to right now, such as `kind-devops`."},
        {"cmd": "kubectl cluster-info", "what": "Print the address of the API server for the current context."},
        {"cmd": "kubectl get nodes -o wide", "what": "List the nodes with their status, version, internal IP and container runtime."},
        {"cmd": "docker ps --filter name=devops", "what": "Show the Docker containers that are the nodes of the `devops` cluster."},
        {"cmd": "kubectl get pods -n kube-system -o wide", "what": "List the control plane and add-on Pods, with the node each one runs on."},
        {"cmd": "docker exec devops-control-plane crictl ps", "what": "List the containers that containerd runs inside one node."},
        {"cmd": "kubectl get events --sort-by=.metadata.creationTimestamp", "what": "List recent events in the namespace, oldest first."},
        {"cmd": "kubectl api-resources", "what": "List every kind of object this cluster knows, with short names."},
        {"cmd": "kind delete cluster --name demo", "what": "Delete a kind cluster, its node containers and its kubectl context."},
    ],
    "mistake": "Reaching past Kubernetes to fix things: `docker exec` into a kind node and stopping a container with `crictl`, or restarting a process by hand on a server. The kubelet sees the gap between desired and actual state and undoes your change, or your fix quietly disappears with the next Pod. Change the desired state through the API instead: edit the manifest and apply it.",
    "real_world": "At PayLite, a made-up payments company, the platform team runs three managed clusters on EKS: dev, staging and production. Product teams never touch the control plane. When a release misbehaves, the first thing anyone runs is `kubectl get events` in the team's namespace, because the events say which component gave up and why.",
    "task": {
        "title": "Build the course cluster and look inside it",
        "steps": [
            "Run `docker info | grep -i cgroup` and confirm Docker uses cgroup v2.",
            "Save `kind-config.yaml` in the root of `~/code/hello-devops` and create a cluster named `devops` with it.",
            "Confirm that kubectl now uses the `kind-devops` context and that `kubectl get nodes` shows three nodes, all `Ready`.",
            "Find the three node containers with `docker ps`. Which one publishes port 8081, and why that one?",
            "List the `kube-system` Pods with `-o wide`. Which node runs the API server? Which Pods run once on every node?",
            "Go one level down: list the containers that containerd runs inside the control-plane node.",
            "In one terminal, watch the `kube-system` Pods with `-w`. In a second terminal, delete the CoreDNS Pods by their label `k8s-app=kube-dns`.",
            "Commit `kind-config.yaml` and push it. Keep the cluster running for tomorrow.",
        ],
        "hints": [
            "`docker exec <node-container> crictl ps` runs crictl inside a node; the node container names start with `devops-`.",
            "`kubectl delete pod -n kube-system -l k8s-app=kube-dns` deletes every Pod with that label at once.",
            "If `kind create cluster` hangs or nodes stay `NotReady`, give Docker Desktop more memory and try again after `kind delete cluster --name devops`.",
        ],
        "done_when": "`kubectl get nodes` lists `devops-control-plane`, `devops-worker` and `devops-worker2` as Ready, and you watched new CoreDNS Pods replace the ones you deleted.",
    },
    "explain_back": {
        "prompt": "Explain in 3 to 4 sentences what happens between `kubectl apply` of a Deployment and a container running. Mention the API server, etcd, a controller, the scheduler and the kubelet.",
        "answer": "kubectl sends the manifest to the API server, which checks it, stores it in etcd and answers straight away. Controllers watching the API server see the new Deployment and create a ReplicaSet and then Pod objects. The scheduler sees Pods without a node and assigns each one to a node that has room. The kubelet on that node sees the Pod, asks containerd to pull the image and start the container, and reports the status back to the API server.",
    },
    "recap": [
        "Kubernetes runs containers across many machines and keeps them the way you described.",
        "Controllers run control loops: compare desired state with actual state, then act on the difference.",
        "The control plane (API server, etcd, scheduler, controller manager) decides; nodes (kubelet, containerd, kube-proxy) run Pods.",
        "Every component talks only to the API server and watches it for changes.",
        "Managed services such as EKS, AKS and GKE run the control plane for you; small, steady apps may not need Kubernetes at all.",
        "kind runs a real cluster on your Mac, with each node as a Docker container.",
    ],
    "check": [
        {
            "q": "The API server of a test cluster crashes for ten minutes. What happens to the web app that was already running there?",
            "options": [
                "It stops at once, because Pods need the API server",
                "It keeps serving, but nothing new can be scheduled or changed",
                "It moves to another cluster until the API server is back",
                "It restarts every Pod as soon as the API server returns",
            ],
            "answer": 1,
            "why": "Kubelets keep running the containers they already have; only changes, scheduling and kubectl need the API server.",
        },
        {
            "q": "A container inside a Pod crashes. Which component notices and starts it again on the same node?",
            "options": ["The scheduler", "The controller manager", "kube-proxy", "The kubelet"],
            "answer": 3,
            "why": "The kubelet runs and watches the containers on its own node, so it restarts a crashed container in place.",
        },
        {
            "q": "A worker node loses power. Which chain of components gets its Pods running again somewhere else?",
            "options": [
                "Controllers create new Pods, then the scheduler places them on healthy nodes",
                "The kubelet on the dead node moves its Pods before it shuts down",
                "etcd copies the Pods to the node with the most free memory",
                "kube-proxy sends the Pods' traffic to another node, so no new Pods are needed",
            ],
            "answer": 0,
            "why": "Controllers notice that Pods are lost and create replacements, and the scheduler assigns those new Pods to nodes that are still up.",
        },
    ],
    "interview": [
        {
            "q": "Walk me through what happens when you run kubectl apply for a Deployment.",
            "a": "kubectl sends the object to the API server, which authenticates and authorizes the request, validates the object and stores it in etcd. The Deployment controller sees it through a watch and creates a ReplicaSet, and the ReplicaSet controller creates the Pod objects. The scheduler assigns each unscheduled Pod to a node, and the kubelet on that node tells the container runtime to pull the image and start the containers. Every step goes through the API server; no component calls another directly.",
        },
        {
            "q": "What is the difference between the control plane and the worker nodes?",
            "a": "The control plane makes decisions and stores state. The API server is its front door, etcd holds the data, the scheduler places Pods and the controller manager runs the control loops. Worker nodes run the workloads: the kubelet starts and watches Pods, a runtime such as containerd runs containers, and kube-proxy programs Service routing. In EKS, AKS or GKE the provider runs the control plane for you.",
        },
        {
            "q": "What does declarative mean in Kubernetes, and why does it matter?",
            "a": "You describe the end state you want, not the steps to get there. Controllers compare that desired state with what is running and keep closing the gap, so the cluster heals itself after crashes. Applying the same file twice gives the same result, which makes changes repeatable and reviewable in git. GitOps tools such as Argo CD build on exactly this idea.",
        },
    ],
    "deeper": {
        "minutes": 12,
        "body": """Every component you met today talks only to the API server. So how does the scheduler learn about a new Pod when nobody calls it?

It uses a watch. A component asks the API server for a list of objects and keeps the connection open. The API server then streams every change (added, modified, deleted) as it happens:
- The scheduler watches Pods that have no node yet.
- Each kubelet watches Pods assigned to its own node.
- Each controller watches the kinds of objects it cares about.

Controllers are also level-triggered. They act on the current state, not on a list of past events. If a controller crashes and restarts, it lists everything again and carries on. Nothing is lost, because the state lives in etcd, not in the controller's memory. This is why Kubernetes copes so well with its own parts failing.

Two fields in `metadata` will come up again:
- Every object has a `resourceVersion`. If two clients update the same object at once, the second one gets a conflict error and must read the object again. This is called optimistic concurrency.
- Objects can have owners. A Pod made by a ReplicaSet points to it in `metadata.ownerReferences`. Delete the owner, and the garbage collector deletes what it owns.

In production the control plane itself is made highly available. Teams run three (or five) control-plane nodes. The API servers are all active behind a load balancer. etcd keeps working while a majority of its members agree, so three members survive the loss of one. The scheduler and controller manager run on every control-plane node, but only one copy of each is active at a time. They pick the leader with a lock stored in the API server.

kind builds a cluster like this:
1. It starts one Docker container per node from the `kindest/node` image.
2. Inside each container, systemd starts containerd and the kubelet.
3. kind runs kubeadm, which starts the control plane parts as static Pods: Pods the kubelet runs straight from files on disk.
4. It installs kindnet and a small storage provisioner.
5. It writes a context into `~/.kube/config` so kubectl can connect.

You can watch the stream yourself. Run `kubectl get pods -w` in one terminal, then create and delete a Pod in another. Each new line is an event the API server pushed to kubectl, the same way it pushes events to controllers.

If you want to see every moving part, [Kubernetes The Hard Way](https://github.com/kelseyhightower/kubernetes-the-hard-way) by Kelsey Hightower builds a cluster by hand. It needs four machines and an afternoon, so treat it as optional reading.""",
    },
    "sources": [
        {"title": "Kubernetes components", "url": "https://kubernetes.io/docs/concepts/overview/components/"},
        {"title": "Controllers", "url": "https://kubernetes.io/docs/concepts/architecture/controller/"},
        {"title": "kind quick start", "url": "https://kind.sigs.k8s.io/docs/user/quick-start/"},
        {"title": "Kubernetes v1.37 release", "url": "https://kubernetes.io/blog/2026/08/26/kubernetes-v1-37-release/"},
    ],
}
