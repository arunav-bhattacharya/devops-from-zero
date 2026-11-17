NEW = {}

NEW["goal"] = "By the end you can explain what each part of a Kubernetes cluster does, follow one `kubectl apply` from your terminal to a running container, and run the course's three-node cluster on your Mac with kind."

NEW["opening"] = """Picture a Friday night in a busy restaurant. You are the manager, and every table needs a waiter and every order needs a cook. At six, a cook calls in sick. At seven, a fridge stops working. At eight, a party of thirty walks in without a booking. In a small café you could fix each problem yourself. With twenty stations and a full room, you cannot be in twenty places at once.

Software has the same Friday night. Last time, a careful checklist set up our servers, and we could run it twice without harm. But it stopped watching them the moment it finished. So who starts our app again when it crashes at 3 in the morning?

In this lesson, we'll meet a manager for programs that never goes home. We'll open each of its parts, follow one request from your keyboard to a running program, and build a practice version on your laptop. Before we start, make a guess, and keep it in mind."""

NEW["guess"] = (
    "Soon you will type `kubectl apply -f app.yaml`, a command that asks a cluster to run an app. It prints `deployment.apps/web created` in under a second. What has happened at that moment?",
    "The cluster's front desk, the API server, checks your request, saves it in its database (etcd) and answers at once. Other parts do the actual work over the next few seconds, which is why you check with `kubectl get pods` afterwards.",
)

NEW["terms"] = [
    "A group of machines that Kubernetes runs and manages as one system.",
    "One machine in a cluster that runs your programs; on kind, each node is a container on your laptop.",
    "The part of a cluster that stores what you asked for and decides what runs where.",
    "What you write down that you want, such as three copies of an app, which Kubernetes keeps working to match.",
    "A small program that keeps comparing what you asked for with what really runs, and acts to close any gap.",
    "The helper program on each node that starts the work given to that node and reports how it is going.",
    "A tool that runs a real Kubernetes cluster on your laptop, with containers playing the part of machines.",
]

S = []

S.append(("From one laptop to twenty servers", """
A home kitchen with one cook needs no manager, but a full restaurant does. Software grows in the same way.

Our running example is hello-devops, a tiny web app that answers every visit with a greeting and a count of visits so far. On Day 21 you ran it in a container. A container is a program packed with everything it needs, so it runs the same on any machine. Next to it ran Redis, a small database that kept the visit count.

Docker is the tool that builds and runs containers. Its helper, Docker Compose, starts several containers on one computer from one file. One `docker compose up` on one laptop, and it worked.

A real product is bigger. Say it is made of 40 small apps that work together, called services. Each one runs in several copies, spread over 20 servers. A server is a computer that runs programs for other people, usually in a data center. Someone has to answer these questions all day:
- Which server has room for this container?
- A container crashed at 3 in the morning. Who starts it again?
- A server died. Who moves its containers somewhere else?
- Visitors doubled. Who adds copies, and who removes them later?
- How do you replace version 1 with version 2 while the app keeps answering?
- Copies come and go. How does one service find another?

Compose handles a few of these, on one machine. Its restart policy (Day 21) brings a crashed container back. It also lets one container find another by name, such as `redis`. But nothing in Compose moves work off a dead server, spreads copies over 20 machines or adds copies when traffic (the stream of visitors) grows.

**Kubernetes** answers every one of those questions. It is a free, open-source system, so anyone may read and use its code. It runs containers across a group of machines, and that group is called a cluster. People often write it K8s: a K, eight letters, then an s.

You write down the result you want, and Kubernetes keeps making it true. How does it keep that promise? That comes next.
"""))

S.append(("A wish list and a loop that never stops", """
With `docker run`, the command that starts one container, you give an order and Docker carries it out once. If the container dies an hour later, Docker has already done its job. Kubernetes works the other way round.

You describe the end state, and Kubernetes stores that description as an object: a record in its database. One object might say "run three copies of `hello-devops:1.0.0`". That name points to the app's image, the packed bundle a container starts from, at version 1.0.0. What your objects describe is called your desired state.

Small programs called controllers then loop forever:
1. Read the desired state: what you asked for.
2. Observe the actual state: what is really running, as the nodes report it.
3. If the two differ, act to make them match.
4. Repeat.

This loop is called reconciliation, which means bringing two lists back into agreement. It is our restaurant manager walking the floor. She holds a list of what each table should have, counts what is really there and sends for anything missing.

Say you asked for three copies of hello-devops, and someone deletes one. On its next pass the loop reads three wanted, counts two running and starts one more. Nobody wrote a script for that case. The [Kubernetes docs](https://kubernetes.io/docs/concepts/architecture/controller/) compare it to a thermostat. You set 21 degrees, and it keeps reading the room and switching the heating on or off. You never tell it to heat for ten minutes.

You can see the loop in every object. Each object you write has a `spec` field: your wish. Kubernetes fills in a `status` field: its report on what is real. Controllers work to make status match spec.

Most kinds of object have a controller, sometimes several, whose job is to make objects of that kind come true. So when you meet a new kind in this part, ask two questions. What does its spec ask for, and which controller makes that happen?

The loop has two effects that surprise beginners:
- Kubernetes fixes problems you never told it about. A crashed container or a dead node is one more gap to close.
- A change made behind its back does not stick. Stop a container directly on a node, and Kubernetes sees the gap and starts it again. Edit the manifest and apply it instead.

**Kubernetes undoes changes it was not told about. Change the wish, not the container.**

Terraform (Part 8) builds servers from a written plan, and Ansible (Part 9) runs a checklist, called a playbook, on them. Both compare code with reality, but only while `terraform apply` or a playbook runs. Kubernetes checks all the time, with nobody at the keyboard. Next, we open the manager's office.
"""))

S.append(("The manager's office: the control plane", """
A cluster has two kinds of parts. The control plane stores your desired state and makes decisions. The nodes, the machines that do the work, run your containers.

Kubernetes never runs a bare container. It runs Pods: a Pod wraps one container, sometimes a few, and gives it an IP address. An IP address is a number that names one machine or program on a network, much like a street address. Tomorrow's lesson is all about Pods.

The control plane has four main parts. Each one is easiest to remember by what breaks when it stops:
- API server (`kube-apiserver`): the front door. Every request goes through it, from `kubectl` and from the other parts. If it stops, `kubectl` fails, but containers that already run keep running.
- etcd: a key-value database (it stores each value under a name) that holds the whole cluster state. Only the API server talks to it. Lose etcd without a backup, and the cluster forgets every object.
- Scheduler (`kube-scheduler`): picks a node for each new Pod. If it stops, new Pods wait in `Pending` forever.
- Controller manager (`kube-controller-manager`): runs the built-in control loops, such as the one that keeps three copies running. If it stops, nothing heals itself any more.

`kubectl` is the command you type in the terminal, the text window where you give your computer commands, to talk to a cluster. In restaurant terms, the control plane is the manager's office and the nodes are the cooking stations. The API server is the rail where order tickets hang, and etcd is its memory. The scheduler is the head chef who hands each dish to a station. The controller manager is the floor manager with the list.

Clusters in a cloud (computers you rent over the internet) add a fifth part, the cloud controller manager. It talks to the cloud provider, for example to create a load balancer. A load balancer is a service that spreads incoming visitors over several machines.

These parts never call each other. They all read and write objects through the API server, and they watch it for changes. A watch is one long-lived request: the API server streams every change down it as it happens. Picture a cook who keeps one eye on the ticket rail instead of waiting to be called. So any part can crash, restart, read the current state again and carry on as if nothing happened.

Next, we walk into the kitchen, where the work gets done.
"""))

S.append(("The kitchen stations: what runs on each node", """
Walk over to one cooking station and watch a node at work. Three programs run there.

The first is the kubelet, the station cook. It keeps an eye on the API server for Pods given to its node. It never decides what to make. When a Pod with its node's name appears, it gets to work, and later it reports back how that Pod is doing.

The kubelet does not start containers with its own hands. It passes that job to a container runtime, usually containerd. This program pulls (downloads) images and starts containers from them.

You may be thinking, "But my images were built with Docker, and these nodes have no Docker." They still run here. Docker images follow a shared format, and containerd runs any image in that format. The Go deeper part at the end of this lesson explains why.

The third program is kube-proxy, the station's runner. It sets up network rules so that traffic sent to a Service reaches one of its Pods. A Service is one fixed address for a group of Pods, and Day 41 explains it.

Two more helpers run as ordinary Pods, like staff shared by the whole kitchen. CoreDNS is the cluster's phone book: it turns a name, such as a Service's name, into an address. The network plugin gives every Pod an IP address and connects Pods across nodes. kind uses a small one called kindnet.

One last thing can stop a station from opening at all. Linux is the operating system almost every server runs. Inside it, a feature called cgroups limits how much CPU (computing power) and memory each container may use. It comes in two versions. Since Kubernetes 1.35, the kubelet refuses by default to start on hosts that still use the old cgroup v1. Docker Desktop on a Mac uses cgroup v2, so you are fine, and `docker info | grep -i cgroup` confirms it in seconds.

Next, we follow one order from the door to the stove.
"""))

S.append(("Following one order from the door to the stove", """
Say you send Kubernetes a Deployment that asks for two copies of nginx. A Deployment is an object that keeps a set number of Pods running (Day 40 covers it). nginx is a popular web server program, handy as a test app.

You write the Deployment in YAML, a plain text format for settings. A file like that is called a manifest. Interviewers love to ask what happens next, so learn this chain well:

1. kubectl reads `~/.kube/config`, a settings file with the cluster's address and your credentials (proof of who you are). It sends the YAML to the API server over HTTPS, the encrypted way programs talk on a network.
2. The API server checks who you are and whether you may do this. It validates the object and stores it in etcd. Then it answers `created`, and kubectl exits.
3. The Deployment controller sees the new Deployment through its watch. It creates a ReplicaSet, a helper object that keeps a set number of identical Pods.
4. The ReplicaSet controller sees the ReplicaSet and creates two Pod objects. They have no node yet.
5. The scheduler sees two Pods without a node. It filters out nodes that cannot take them, scores the rest, and writes a node name into each Pod.
6. The kubelet on each chosen node sees a Pod given to it. It asks containerd to pull the image and start the container.
7. The kubelet reports back: the Pod is running, and here is its IP address. The API server stores that in the Pod's status.

Remember the guess at the top of the page? When kubectl printed `created`, we were only at step 2. The ticket was on the rail, and no cook had touched it yet.

Every step goes through the API server. Each part acts on what it finds there, and none sends orders to another. The steps also leave short records called events, so `kubectl get events` shows the whole chain. The worked example below runs it, and on a team it is often the first command anyone runs after a bad release.

If a step cannot happen, the chain stops there. A Pod that fits on no node stays `Pending` with no node name, and its events say why (Day 46 debugs cases like that).

Next, we ask whether you should run a cluster yourself, rent one, or skip it.
"""))

S.append(("Renting the restaurant, or not opening one", """
In production, the real system that real users depend on, few teams run the control plane themselves. Keeping etcd safe, upgrading the cluster a few times a year and patching security holes is real work. Cloud providers sell managed Kubernetes instead. They run and upgrade the control plane, and you run your apps on the nodes. It is like renting a restaurant whose owner looks after the building, the gas and the fire checks, while you bring the cooks and the menu. The three you will hear about most:
- Amazon EKS (Elastic Kubernetes Service) on AWS.
- AKS (Azure Kubernetes Service) on Microsoft Azure.
- GKE (Google Kubernetes Engine) on Google Cloud.

Each one also has a mode where the provider runs the nodes too: EKS Auto Mode, AKS Automatic and GKE Autopilot.

Kubernetes still costs people time. Someone must learn it, keep it upgraded and keep it secure. A café with three tables does not need a shift planner. Skip Kubernetes when:
- You run one or a few services with steady traffic.
- Your small team has nobody to own the platform.
- A simpler service fits, such as a PaaS or serverless containers (Day 12).

Both of those run your app for you. A PaaS (platform as a service) takes your app and its settings. Serverless containers take one container and hide every server from you. A useful test: can you name the person who will upgrade the cluster next spring? If not, start with something simpler.

Your manifests work the same on kind, EKS, AKS and GKE, so practice on a laptop is real practice. The differences sit at the edges: load balancers, disks and identity (how the cluster proves who is allowed to do what). Next, we build that laptop cluster.
"""))

S.append(("A practice kitchen on your laptop with kind", """
kind stands for Kubernetes in Docker. Each node is a Docker container that runs its own containerd and kubelet inside. The kind tool uses kubeadm, the official setup tool, to start a real control plane in the first node. So you get the same Kubernetes as a cloud cluster, minus the cloud parts. It is a practice kitchen with real stoves.

The course uses one config file, `kind-config.yaml`, in the root of your repo (the project folder that Git tracks). It asks for:
- One control-plane node and two workers, so you can watch Pods spread over machines.
- A port mapping from port 30080 on the control-plane node to port 8081 on your Mac.

A port is a numbered door on a machine where a program waits for visitors. On Day 41 a Service listens on node port 30080, and `curl localhost:8081` reaches it. (`curl` is a command that fetches a web address and prints the answer.)

When kind creates a cluster called `devops`, it writes a context called `kind-devops` into `~/.kube/config` and switches kubectl to it. A context is a saved pair of cluster and user (Day 39 shows how to list and switch them).

Three limits of kind will matter soon:
- No cloud load balancers. A Service of type LoadBalancer waits forever unless you add a helper (Day 41).
- The nodes live inside Docker Desktop's Linux VM, a pretend computer that runs inside your Mac. Their 172.18.x.x addresses are not reachable from your Mac, so you use port mappings and `kubectl port-forward`.
- It shares your laptop's memory. If nodes turn `NotReady`, or the kubelet evicts Pods (stops them to free memory), give Docker Desktop more memory in its settings.

Creating the cluster takes a minute or two and deleting it takes seconds, so starting fresh is always cheap. Next, the worked example below sends a kitchen like this its first order.
"""))

NEW["sections"] = S

NEW["aside"] = {
    "title": "Why not write a script that checks every minute?",
    "body": "You could, and many teams once did. The first version is short: if the app is not running, start it. Then a server dies, and the script must move work to another one. Then it must spread copies, swap versions without downtime and tell services where the others went. Soon the script is a large system of its own that someone has to run and fix. Kubernetes is that system, written once and shared, with one loop for each job.",
    "after": 1,
}




NEW["drop"] = ["analogy", "real_world", "mistake"]

NEW["diagram_caption"] = "kubectl talks only to the API server. The scheduler, the controllers and the kubelet all watch the API server and act on what they see."

NEW["worked"] = [
    "Create a small throwaway cluster with one node, named `demo`. The first run downloads the node image (the bundle each node container starts from), which can take a few minutes. The output is trimmed to its last line, where kind points kubectl at the new cluster.",
    "Find the control plane. In kind its parts run as Pods in `kube-system`, a namespace kept for the cluster itself. A namespace is a named group of objects (Day 39). There you find the API server, etcd, the scheduler and the controller manager, plus kube-proxy, CoreDNS and kindnet.",
    "Ask for two copies of nginx, then look straight away. kubectl came back at once, but the containers are still being created. That is the guess from the top of the page.",
    "Now read the events in the order they were made, with a column for the part that wrote each one. You can see the chain from the lesson: Deployment controller, ReplicaSet controller, scheduler, then the kubelet. The output keeps the kubelet lines for one Pod only.",
    "Watch the control loop work. Delete one Pod. The ReplicaSet now counts one Pod where it wants two, so it creates a replacement with a new name.",
    "Delete the practice cluster. This removes the node container and the `kind-demo` context, so kubectl no longer points at it.",
]

NEW["task"] = (
    [
        "Run `docker info | grep -i cgroup` and confirm Docker uses cgroup v2.",
        "Save `kind-config.yaml` in the root of `~/code/hello-devops` and create a cluster named `devops` with it.",
        "Confirm that kubectl now uses the `kind-devops` context and that `kubectl get nodes` shows three nodes, all `Ready`.",
        "Find the three node containers with `docker ps`. Which one publishes port 8081, and why that one?",
        "List the `kube-system` Pods with `-o wide`. Which node runs the API server? Which Pods run once on every node?",
        "Go one level down: list the containers that containerd runs inside the control-plane node.",
        "In one terminal, watch the `kube-system` Pods with `-w`. In a second terminal, delete the CoreDNS Pods by their label `k8s-app=kube-dns` (a label is a name tag on an object).",
        "Commit `kind-config.yaml` and push it. Keep the cluster running for tomorrow.",
    ],
    [
        "`crictl` is a small command-line tool that talks to a node's container runtime through the CRI. `docker exec <node-container> crictl ps` runs it inside a node; the node container names start with `devops-`.",
        "`kubectl delete pod -n kube-system -l k8s-app=kube-dns` deletes every Pod with that label at once.",
        "If `kind create cluster` hangs or nodes stay `NotReady`, give Docker Desktop more memory and try again after `kind delete cluster --name devops`.",
    ],
    "`kubectl get nodes` lists `devops-control-plane`, `devops-worker` and `devops-worker2` as Ready, and you watched new CoreDNS Pods replace the ones you deleted.",
)

NEW["explain_back"] = (
    "Explain in 3 to 4 sentences what happens between `kubectl apply` of a Deployment and a container running. Mention the API server, etcd, a controller, the scheduler and the kubelet.",
    "kubectl sends the manifest to the API server, which checks it, stores it in etcd and answers straight away. Controllers watching the API server see the new Deployment and create a ReplicaSet and then Pod objects. The scheduler sees Pods without a node and gives each one to a node that has room. The kubelet on that node sees the Pod, asks containerd to pull the image and start the container, and reports the status back to the API server.",
)

NEW["recap"] = [
    "Kubernetes runs containers across many machines and keeps them the way you described.",
    "Controllers run control loops: compare desired state with actual state, then act on the difference.",
    "The control plane (API server, etcd, scheduler, controller manager) decides; nodes (kubelet, containerd, kube-proxy) run Pods.",
    "Every part talks only to the API server and watches it for changes.",
    "Managed services such as EKS, AKS and GKE run the control plane for you.",
    "Kubernetes costs people time, so a few steady apps may not need it; kind runs a real cluster on your Mac for practice.",
]

NEW["closing"] = """We started on a Friday night with a manager who could not be in twenty places at once. Kubernetes solves that with a written wish list and many small loops that keep checking it, all talking through one front door. When your `devops` cluster is up, list the Pods in `kube-system` and name the job of each one: the front door, the memory, the head chef, the floor manager. Next, we'll look at the smallest thing Kubernetes runs, the Pod, and write our first manifest by hand. What exactly goes into a wish that Kubernetes can read?"""

NEW["check"] = [
    ("The API server of a test cluster crashes for ten minutes. What happens to the web app that was already running there?",
     "The kubelets keep running the containers they already have; only changes, scheduling and kubectl need the API server."),
    ("A container inside a Pod crashes. Which part notices and starts it again on the same node?",
     "The kubelet runs and watches the containers on its own node, so it restarts a crashed container in place."),
    ("A worker node loses power. Which chain of parts gets its Pods running again somewhere else?",
     "Controllers notice that Pods are lost and create replacements, and the scheduler gives those new Pods to nodes that are still up."),
]

NEW["interview"] = [
    ("Walk me through what happens when you run kubectl apply for a Deployment.",
     "kubectl sends the object to the API server, which checks who you are and what you may do, validates the object and stores it in etcd. The Deployment controller sees it through a watch and creates a ReplicaSet, and the ReplicaSet controller creates the Pod objects. The scheduler gives each unscheduled Pod a node, and the kubelet on that node tells the container runtime to pull the image and start the containers. Every step goes through the API server; no part calls another directly."),
    ("What is the difference between the control plane and the worker nodes?",
     "The control plane makes decisions and stores state. The API server is its front door, etcd holds the data, the scheduler places Pods and the controller manager runs the control loops. Worker nodes run the workloads: the kubelet starts and watches Pods, a runtime such as containerd runs containers, and kube-proxy sets up the routing for Services. In EKS, AKS or GKE the provider runs the control plane for you."),
    ("What does declarative mean in Kubernetes, and why does it matter?",
     "You describe the end state you want, not the steps to get there. Controllers compare that desired state with what is running and keep closing the gap, so the cluster heals itself after crashes. Applying the same file twice gives the same result, which makes changes repeatable and easy to review in git. GitOps tools such as Argo CD build on exactly this idea."),
]

NEW["deeper"] = """
Every part you met today talks only to the API server. So how does the scheduler learn about a new Pod when nobody calls it?

It uses a watch. A part asks the API server for a list of objects and keeps the connection open. The API server then streams every change (added, modified, deleted) as it happens:
- The scheduler watches Pods that have no node yet.
- Each kubelet watches Pods given to its own node.
- Each controller watches the kinds of objects it cares about.

Controllers are also level-triggered: they act on the current state, not on a list of past events. If a controller crashes and restarts, it lists everything again and carries on. Nothing is lost, because the state lives in etcd, not in the controller's memory. This is why Kubernetes copes so well with its own parts failing.

Two fields in `metadata`, the part of an object that holds its name and labels, will come up again:
- Every object has a `resourceVersion`. If two clients update the same object at once, the second one gets a conflict error and must read the object again. This is called optimistic concurrency.
- Objects can have owners. A Pod made by a ReplicaSet points to it in `metadata.ownerReferences`. Delete the owner, and the garbage collector (a cleanup controller) deletes what it owns.

In production the control plane itself is made highly available, so it keeps working when one machine fails. Teams run three (or five) control-plane nodes. The API servers are all active behind a load balancer. etcd keeps working while a majority of its members agree, so three members survive the loss of one. The scheduler and controller manager run on every control-plane node, but only one copy of each is active at a time. They pick that leader with a lock stored in the API server.

kind builds a cluster like this:
1. It starts one Docker container per node from the `kindest/node` image.
2. Inside each container, systemd (the Linux program that starts other programs) starts containerd and the kubelet.
3. kind runs kubeadm, which starts the control plane parts as static Pods: Pods the kubelet runs straight from files on disk.
4. It installs kindnet and a small storage provisioner, which hands out disk space to Pods.
5. It writes a context into `~/.kube/config` so kubectl can connect.

You can watch the stream yourself. Run `kubectl get pods -w` in one terminal, then create and delete a Pod in another. Each new line is an event the API server pushed to kubectl, the same way it pushes events to controllers.

Two short stories finish the picture. First, where Kubernetes came from. Google built it from what it learned running its own internal system, Borg, and released it as open source in 2014. Today the Cloud Native Computing Foundation (CNCF), a non-profit group, looks after it, and every big cloud sells it.

Second, why Docker images run on nodes without Docker. A Docker image follows the OCI (Open Container Initiative) image standard, and containerd runs any OCI image. The kubelet talks to containerd through another standard, the CRI (Container Runtime Interface). Kubernetes removed its built-in Docker support (called dockershim) in version 1.24, and image builds did not change at all.

If you want to see every moving part, [Kubernetes The Hard Way](https://github.com/kelseyhightower/kubernetes-the-hard-way) by Kelsey Hightower builds a cluster by hand. It needs four machines and an afternoon, so treat it as optional reading.
"""
