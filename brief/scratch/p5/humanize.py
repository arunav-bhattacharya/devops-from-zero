#!/usr/bin/env python3
"""Voice pass for Part 5 (human-writing skill, blog mode).

Loads the current content/p5.json, replaces prose fields only, and writes it back.
Never touches ids, titles, code, commands, refs, sources, answers, options or diagrams.
Do not rerun build_p5.py after this: it would overwrite these edits."""
import json
import pathlib

P = pathlib.Path("/home/user/devops-from-zero/content/p5.json")
d = json.loads(P.read_text())
L = {x["id"]: x for x in d["lessons"]}


def sec(lid, i, body):
    L[lid]["sections"][i]["body"] = body.strip("\n")


def say(lid, i, text):
    L[lid]["worked"]["steps"][i]["say"] = text


# ---------------------------------------------------------------- part
d["intro"] = (
    "In Part 5 the image you built in Part 2 moves onto Kubernetes, the system most teams use to run "
    "containers across many machines. You build a real three-node cluster on your Mac with kind. Over four "
    "days you add Deployments, Services, config, health checks, autoscaling, a Gateway and a Helm chart, "
    "all of it local and free."
)

# ---------------------------------------------------------------- d16
x = L["d16"]
x["goal"] = (
    "By the end you can run your own app in a Pod on a local kind cluster, and explain which part of "
    "Kubernetes did what to get it running."
)
x["guess"]["why"] = (
    "Kubernetes keeps comparing what you asked for (3 copies) with what is running (2). When the two "
    "differ, it closes the gap, here by starting a copy on a healthy machine."
)

sec("d16", 0, """
In Part 2 you ran hello-devops with `docker run` and Docker Compose. That works well on one computer. Now picture a real product: 40 services, each with several copies, spread over 20 servers.

Someone has to answer questions like these all day:
- Which server has room for this container?
- A container crashed at night. Who starts it again?
- Traffic doubled. Who adds copies, and who removes them later?
- How do you swap version 1 for version 2 without downtime?
- Copies come and go, so how does one service find another?

**Kubernetes** (often written K8s) answers all of them. It is an open-source system that runs containers across a group of machines, called a cluster. You describe the result you want, and Kubernetes keeps working to make it true.

You will run it on your Mac with kind ("Kubernetes in Docker"). Each kind node is a Docker container, so a three-node cluster fits on one laptop.
""")

sec("d16", 1, """
Kubernetes is built around **desired state**. With `docker run` you gave an order, and Docker carried it out once. In Kubernetes you write down the result you want, such as "three copies of hello-devops 1.0.0", and Kubernetes stores it.

Then small programs called controllers run a loop that never ends:
1. Read the desired state (what you asked for).
2. Look at the actual state (what is running now).
3. If they differ, act to make them match.
4. Wait a moment and repeat.

This is called reconciliation, and the loop is a control loop. The [Kubernetes docs](https://kubernetes.io/docs/concepts/architecture/controller/) compare it to a thermostat. You set 21 degrees, and the thermostat keeps checking the room and turns the heating on or off.

That is what happened in the guess at the top. When a machine dies, the actual state drops to two copies. A controller sees the gap and starts a third copy somewhere else, and nobody has to wake up for it.

Terraform also compares your code with what exists, but it acts only when you run `terraform apply`. Kubernetes checks all the time.
""")

sec("d16", 2, """
A cluster has two kinds of parts: the control plane decides what runs where, and the worker nodes run it.

The control plane has four main components:
- API server (`kube-apiserver`): the front door. Every request goes through it, including yours from `kubectl`.
- etcd: a key-value database that stores the whole cluster state.
- Scheduler (`kube-scheduler`): picks a node for each new Pod that has none yet.
- Controller manager (`kube-controller-manager`): runs the built-in control loops.

Every worker node runs three things:
- kubelet: an agent that makes sure the Pods assigned to its node are running.
- kube-proxy: keeps network rules so traffic for a Service reaches the right Pods (Day 17).
- A container runtime such as containerd: the software that actually starts containers.

These parts never call each other directly. They all read and write through the API server. The diagram below follows one `kubectl apply` along that path.
""")

sec("d16", 3, """
A Pod is the smallest thing Kubernetes runs. Most Pods hold one container. Some hold a main container plus a small helper. Containers in one Pod share an IP address and can share files.

Pods are disposable. When a Pod dies, Kubernetes does not repair it. A controller makes a new one, with a new name and a new IP address. So you rarely create Pods by hand, and from tomorrow a Deployment creates them for you.

You describe objects in a manifest, a YAML file. Every manifest has four top-level fields:
- `apiVersion`: which version of the API defines this kind (for a Pod, `v1`).
- `kind`: the type of object, such as `Pod`, `Deployment` or `Service`.
- `metadata`: identity, such as `name`, `namespace` and `labels`.
- `spec`: your desired state for this object.

Once you apply it, Kubernetes adds a fifth part, `status`, which holds the actual state. Controllers work to make `status` match `spec`.
""")

sec("d16", 4, """
`kubectl` is the command-line tool for Kubernetes. It reads `~/.kube/config` to learn which cluster to talk to. That file holds contexts (a cluster plus a user). When kind creates a cluster named `devops`, it adds the context `kind-devops` and switches to it.

You will type these every day:
- `kubectl get pods`: list objects of one type.
- `kubectl describe pod hello`: details and recent events for one object.
- `kubectl logs hello`: what the container printed.
- `kubectl apply -f pod.yaml`: create or update objects from a file.
- `kubectl delete -f pod.yaml`: remove them.
- `kubectl explain pod.spec`: built-in docs for any field.

kind nodes keep their own copy of images, apart from Docker on your Mac. So an image you built locally must be copied in with `kind load docker-image`. Give it a real tag such as `1.0.0`. With `latest`, Kubernetes tries to pull the image from Docker Hub instead.

To reach a Pod from your Mac, run `kubectl port-forward pod/hello 8000:8000`. It opens a tunnel from a local port to the Pod for as long as the command runs. For one Pod on your laptop, that is all you need.
""")

sec("d16", 5, """
In production, few teams run the control plane themselves. Cloud providers sell managed Kubernetes, where they run and upgrade the control plane and you run your apps on the nodes:
- Amazon EKS (Elastic Kubernetes Service) on AWS.
- AKS (Azure Kubernetes Service) on Microsoft Azure.
- GKE (Google Kubernetes Engine) on Google Cloud.

Each one also has a mode where the provider manages the nodes too: EKS Auto Mode, AKS Automatic and GKE Autopilot.

Kubernetes also costs people time. Someone has to learn it, and someone has to keep it upgraded and secure. Skip it when:
- You run one or a few services with steady traffic.
- Your small team has nobody to own the platform.
- A simpler service fits, such as a PaaS or serverless containers (Day 4).

Your manifests work the same on kind, EKS, AKS and GKE, which is why a laptop cluster is real practice. The differences sit at the edges: load balancers, disks and identity.
""")

x["analogy"] = (
    "Think of a restaurant manager whose one rule is \"three cooks in the kitchen\". You never say which cook "
    "works at which station. If a cook goes home sick, the manager calls in another one without asking you. "
    "The stations are the nodes and the cooks are your Pods. The comparison fails on judgment: a real "
    "manager bends rules, while Kubernetes only follows the exact state you wrote down."
)

say("d16", 0, "Create a small throwaway cluster with one node, named `demo`. The first run downloads a node "
              "image, which can take a few minutes. When it finishes, kind points kubectl at the new cluster.")
say("d16", 1, "List the nodes. There is only one, and it is both the control plane and the worker. VERSION is "
              "the Kubernetes version kind installed.")
say("d16", 2, "That node is a Docker container on your Mac, which is how kind fits a whole cluster on a laptop.")
say("d16", 3, "Now find the control plane. In kind its parts run as Pods in the `kube-system` namespace: the API "
              "server, etcd, the scheduler and the controller manager. You also see kube-proxy, CoreDNS (the "
              "cluster's DNS server) and kindnet (the network plugin).")
say("d16", 4, "Ask the cluster what a field means. `kubectl explain` reads the documentation built into the API, "
              "so it always matches your cluster's version. Then delete the practice cluster, which removes the "
              "node container and the `kind-demo` context.")

x["mistake"] = (
    "Do not tag an image `:latest` (or leave the tag off) when you copy it in with `kind load`. With that tag, "
    "Kubernetes defaults to `imagePullPolicy: Always`, so it tries Docker Hub and the Pod gets stuck in "
    "`ErrImagePull`, then `ImagePullBackOff`. Use a real tag like `hello-devops:1.0.0` and set "
    "`imagePullPolicy: IfNotPresent`."
)
x["real_world"] = (
    "At PayLite, a made-up payments company, the platform team runs three managed clusters on EKS: dev, "
    "staging and production. Product teams never touch the control plane. They test their manifests on kind, "
    "open a pull request, and a pipeline applies them."
)
x["task"]["hints"][1] = "The `host` field in the JSON is the Pod's name, because inside a Pod the host name is the Pod's name."

x["deeper"]["body"] = """
Every component you met today talks only to the API server. So how does the scheduler learn that a new Pod exists, when nobody calls it?

It uses a watch. A component asks the API server for a list of objects and keeps the connection open. The API server then streams every change (added, modified, deleted) as it happens:
- The scheduler watches Pods that have no node yet.
- Each kubelet watches Pods assigned to its own node.
- Each controller watches the kinds of objects it cares about.

Controllers are also level-triggered: they act on the current state, not on a list of past events. If a controller crashes and restarts, it lists everything again and carries on. Nothing is lost, because the state lives in etcd, not in the controller's memory.

Two fields in `metadata` will come up later:
- Every object has a `resourceVersion`. If two clients update the same object at once, the second gets a conflict error and must retry. This is called optimistic concurrency.
- Objects can have owners. A Pod made by a ReplicaSet points to it in `metadata.ownerReferences`. Delete the owner, and the garbage collector deletes what it owns.

kind builds a cluster out of containers like this:
1. It starts one Docker container per node from the `kindest/node` image.
2. Inside each container, systemd starts containerd and the kubelet.
3. kind runs kubeadm, the official setup tool, which starts the control plane parts as Pods.
4. It installs a small network plugin (kindnet) and a storage provisioner.
5. It writes a context into `~/.kube/config` so kubectl can connect.

So a kind cluster is a real cluster, running the same Kubernetes binaries as a cloud cluster. What it lacks is cloud integration: there are no real load balancers and no cloud disks. You will run into both gaps on Day 19.

You can watch the stream yourself. Run `kubectl get pods -w` in one terminal, then apply and delete `pod.yaml` in another. Each new line is an event the API server streamed to kubectl, the same way it streams events to the controllers.

To go further, read the [components page](https://kubernetes.io/docs/concepts/overview/components/) on the parts of the control plane. Then run `kubectl describe` on the Pods in `kube-system` and find the flags each component runs with.
""".strip("\n")

# ---------------------------------------------------------------- d17
x = L["d17"]
x["goal"] = (
    "By the end you can run hello-devops as a Deployment of several Pods behind a Service, then roll a new "
    "version out and back."
)

sec("d17", 0, """
Yesterday you created a Pod by hand. When you deleted it, it was gone for good. Nothing brought it back, because no controller owned it.

In real work you create a **Deployment** instead. You give it a Pod template (image, ports, settings) and the number of copies you want. The Deployment does not create Pods itself. It creates a ReplicaSet, and the ReplicaSet creates the Pods:
- Deployment: owns the update strategy and the history of versions.
- ReplicaSet: keeps exactly N Pods from one template running.
- Pod: runs your container.

That chain is where self-healing comes from. If a Pod crashes or a node dies, the ReplicaSet counts fewer Pods than it wants and creates new ones.

Scaling is the same loop with a new number. `kubectl scale deployment hello-devops --replicas=5` changes the desired count, and the ReplicaSet fills the gap. You will rarely touch ReplicaSets yourself, so think of them as the Deployment's helpers.
""")

sec("d17", 1, """
Pod names start with their ReplicaSet's name, but that is not how a ReplicaSet finds its Pods. It uses labels.

A label is a key=value tag on an object. In `deployment.yaml`, the Pod template carries the label `app: hello-devops`. The Deployment's `selector` says "my Pods are the ones with `app: hello-devops`". The two must match, or the API server rejects the Deployment.

Kubernetes objects find each other through labels:
- A Deployment finds its Pods with a selector.
- A Service finds the Pods to send traffic to with a selector.
- You find objects with `kubectl get pods -l app=hello-devops`.

One detail trips up many people. A selector matches labels on Pods as they are right now. If you change a running Pod's label by hand, the ReplicaSet stops counting it and starts a replacement. The old Pod keeps running with no owner. A Deployment's selector also cannot be changed after you create it, so pick your labels with care.
""")

sec("d17", 2, """
To ship a new version, you change the image in the Pod template. Kubernetes then does a rolling update:
1. The Deployment creates a new ReplicaSet for the new template.
2. It scales the new ReplicaSet up by a few Pods.
3. When those Pods are ready, it scales the old ReplicaSet down by a few.
4. It repeats until every Pod runs the new version.

Two settings control the pace. `maxSurge` is how many extra Pods may exist above the desired count, and `maxUnavailable` is how many may be missing. Both default to 25%. The lab uses `maxSurge: 1` and `maxUnavailable: 0`: add one new Pod, wait until it is ready, then remove one old Pod. You never drop below three working Pods.

The old ReplicaSet is kept, scaled to zero. That makes rollback fast: `kubectl rollout undo` scales the previous ReplicaSet back up in the same careful steps. While a rollout runs, `kubectl rollout status` follows it until it finishes, and `kubectl rollout history` lists the revisions.
""")

sec("d17", 3, """
Pods come and go, and each new Pod gets a new IP address. So clients should never call Pods directly. They call a Service, which gets a stable virtual IP and a DNS name and spreads traffic over all ready Pods that match its selector.

You will meet four common types:
- ClusterIP (the default): reachable only inside the cluster.
- NodePort: also opens the same port (30000 to 32767) on every node.
- LoadBalancer: also asks the cloud for an external load balancer. On kind it stays pending, because there is no cloud.
- Headless (`clusterIP: None`): no virtual IP; DNS returns the Pod IPs directly.

The lab Service is a NodePort on port 30080, and your `kind-config.yaml` maps that port to `localhost:8081`. So `curl localhost:8081` goes through the Service, and each request can land on a different Pod.

`service.yaml` has three ports, and they are easy to mix up:
- `port: 80` is the Service's own port.
- `targetPort: 8000` is the container's port.
- `nodePort: 30080` is the port opened on each node.
""")

sec("d17", 4, """
Inside the cluster, Pods find Services by name. A DNS server (CoreDNS) runs in the cluster and gives every Service a name like `<service>.<namespace>.svc.cluster.local`.

So the lab's Service is `hello-devops.hello.svc.cluster.local`. A Pod in the same namespace can use the short name `hello-devops`. A Pod in another namespace needs at least `hello-devops.hello`. Tomorrow the app finds Redis this way, with `REDIS_HOST=redis`.

From your Mac you have two ways in:
- The NodePort, through kind's port mapping. This goes through the Service, so requests are spread over the Pods.
- `kubectl port-forward svc/hello-devops 8080:80 -n hello`. It works for any Service, but it picks one Pod and sends everything there.

Keep port-forward for debugging. Users never reach an app that way, and on Day 19 you add a Gateway for them.
""")

sec("d17", 5, """
A namespace is a named group of objects inside one cluster. Names must be unique inside a namespace, but two namespaces can each hold an object with the same name. Teams use namespaces to separate apps, teams or environments, and to attach access rules and quotas.

A new cluster already has a few:
- `default`: where objects go when you do not name a namespace.
- `kube-system`: the cluster's own parts, such as CoreDNS and kube-proxy.
- `kube-public` and `kube-node-lease`: used by the system; leave them alone.

The lab puts everything in a namespace called `hello`, and each manifest sets `metadata.namespace: hello`. With kubectl, add `-n hello` to each command, or make it your default with `kubectl config set-context --current --namespace=hello`. Deleting a namespace deletes everything inside it, which makes cleanup easy and mistakes costly.
""")

x["analogy"] = (
    "Picture a call center that must always have three operators at the phones. The Deployment is the "
    "supervisor: if one operator goes home, a replacement sits down. The Service is the single public number. "
    "It rings whichever operator is free, so callers never need names. The picture fails on memory: a "
    "replacement operator knows the company's past calls, but a new Pod starts with nothing unless the data "
    "lives outside it, like in Redis."
)

say("d17", 1, "Look at the chain: the Deployment made a ReplicaSet, and the ReplicaSet made two Pods. Each Pod "
              "name starts with the ReplicaSet's name.")
say("d17", 2, "Delete one Pod and list again. Within seconds the ReplicaSet saw one Pod missing and created a "
              "replacement with a new name.")

x["mistake"] = (
    "People change the live cluster with `kubectl set image`, `kubectl scale` or `kubectl edit`, then forget "
    "to change the YAML in git. The next `kubectl apply` (or Argo CD on Day 20) puts the old values back, and "
    "nobody knows why. Experiment with the quick commands, then make the real change in the file and apply that."
)
x["real_world"] = (
    "PayLite's checkout service runs as a Deployment with 6 replicas spread over several nodes. Releases are "
    "rolling updates with `maxUnavailable: 0`, so card payments keep flowing during a deploy. If errors jump "
    "after a release, the on-call engineer rolls back first and investigates afterwards."
)

x["deeper"]["body"] = """
Nothing listens on a Service's IP address, because a Service is not a process. A packet sent to that IP still reaches a Pod, in four steps:
1. A controller watches the Pods that match the Service's selector. It writes their IP addresses and ports into EndpointSlice objects, and marks each one ready or not ready.
2. kube-proxy runs on every node and watches Services and EndpointSlices.
3. kube-proxy writes packet rules into the Linux kernel on its node (iptables or nftables). The rules say: traffic for this virtual IP and port goes to one of these Pod IPs.
4. When a Pod connects to the Service IP, the kernel on that node changes the destination to one ready Pod.

You can see the endpoints yourself with `kubectl get endpointslices -n hello`. Scale the Deployment and run it again, and the list follows the Pods.

Three things follow from this:
- Traffic is spread per connection, not per request. A client that keeps one connection open (HTTP keep-alive) may talk to the same Pod for a long time. Each curl in a loop opens a new connection, so it can land on a new Pod, while a browser might not.
- A Pod that is not ready gets no Service traffic, even though it is running. You will use this on Day 18.
- `kubectl port-forward svc/...` skips all of this. It picks one Pod and tunnels to it through the API server.

NodePort uses the same machinery plus one more rule: traffic that arrives at any node on port 30080 is sent on to the Service. So kind only needs to map one node's port to your Mac.

On the DNS side, each Pod's `/etc/resolv.conf` lists search domains such as `hello.svc.cluster.local`, which is why the short name `redis` works inside namespace `hello`. Check it with `kubectl exec -n hello deploy/hello-devops -- cat /etc/resolv.conf`.

Some network plugins, such as Cilium, replace kube-proxy and do the same job with eBPF programs in the kernel.
""".strip("\n")

# ---------------------------------------------------------------- d18
x = L["d18"]
x["goal"] = (
    "By the end you can run hello-devops with its settings in a ConfigMap, health checks, resource settings "
    "and an autoscaler, and you can debug Pods that will not start."
)

sec("d18", 0, """
In Part 2 you met the twelve-factor idea: build one image, and change its settings with environment variables. A **ConfigMap** is where Kubernetes keeps those settings. It is a simple object with a `data` section of key-value pairs.

Pods can use a ConfigMap in three ways:
- `env` with `configMapKeyRef`: one key becomes one environment variable.
- `envFrom` with `configMapRef`: every key becomes an environment variable. The lab uses this.
- A volume: each key becomes a file in a folder, good for whole config files.

The lab's `configmap.yaml` sets `GREETING` and `REDIS_HOST=redis`. Redis gets its own Deployment and Service in `redis.yaml`, so `redis` is a DNS name inside the `hello` namespace.

Environment variables are read once, when the container starts, and many people forget this. If you change the ConfigMap, running Pods keep the old values. Restart them with `kubectl rollout restart deployment/hello-devops -n hello`. Mounted files do update after a short delay, but the app must read them again.
""")

sec("d18", 1, """
A Secret looks like a ConfigMap, but it is meant for sensitive values: passwords, API tokens and TLS keys. Pods use it the same ways (env, envFrom or a volume).

The values are only base64-encoded. Base64 is an encoding that anyone can reverse with one command, `base64 --decode`. And by default, Kubernetes stores Secrets unencrypted in etcd.

What actually protects them:
- Limit who can read Secrets with RBAC (role-based access control) rules.
- Turn on encryption at rest for etcd. Managed clusters (EKS, AKS, GKE) offer this, often with a cloud key service.
- Never commit Secret YAML with real values to git.
- Keep the real value in a vault and sync it in. External Secrets Operator does this from AWS Secrets Manager, HashiCorp Vault and others.
- Or encrypt it for git with Sealed Secrets, so only a controller in the cluster can decrypt it.

hello-devops needs no secrets yet, so the lab has no Secret file. Try the Secret commands in the list below to see base64 for yourself.
""")

sec("d18", 2, """
A container can be running and still broken: stuck, or unable to reach its database. Without probes, Kubernetes only knows whether the process is running. Probes let the kubelet ask your app how it is doing. The lab uses HTTP probes, where a status code from 200 to 399 counts as a pass.

There are three kinds, and a failure means something different for each:
- Liveness (`/healthz`): "Is the process stuck?" After `failureThreshold` failures in a row, the kubelet restarts the container.
- Readiness (`/readyz`): "Can it do real work now?" While it fails, the Pod gets no Service traffic. It is not restarted.
- Startup: "Has it finished starting?" The other two probes wait until it passes, so a slow start is not killed.

By default a probe runs every 10 seconds (`periodSeconds`), times out after 1 second, and fails after 3 misses in a row.

Do not check the database in the liveness probe. If the database goes down, every Pod restarts at once, and the restarts do not fix the database. The hello-devops app gets this right: `/healthz` checks only the process, and `/readyz` also checks Redis.
""")

sec("d18", 3, """
Each container can say how much CPU and memory it needs. CPU is counted in cores: `100m` means 100 millicores, a tenth of a core. Memory is counted in bytes: `128Mi` means 128 mebibytes.

There are two numbers, with different jobs:
- Requests: what the scheduler reserves. A Pod only goes on a node with that much unreserved room. Ask for too much, and the Pod stays `Pending`.
- Limits: the most the container may use. The Linux kernel enforces them.

What happens at a limit depends on the resource. Memory cannot be taken back, so a container above its memory limit is killed. `kubectl describe pod` then shows `OOMKilled` (out of memory). CPU can be slowed down instead. A container at its CPU limit is throttled: it keeps running, only slower.

The lab sets requests for CPU and memory, and a limit for memory only. Many teams skip CPU limits, because throttling can hurt response times even when the node has spare CPU. Requests are different. Always set them, because the scheduler and the autoscaler both need them.
""")

sec("d18", 4, """
A HorizontalPodAutoscaler (HPA) changes the number of replicas for you. The lab's `hpa.yaml` uses the `autoscaling/v2` API. It keeps average CPU near 70% of the request, with 3 to 6 Pods.

It is one more control loop. About every 15 seconds the HPA:
1. Reads each Pod's CPU use from the metrics API.
2. Compares the average with the target (70% of 100m, so 70m).
3. Works out a new replica count and updates the Deployment.

The numbers come from metrics-server, an add-on that collects CPU and memory from each kubelet. kind does not include it, so you install it with one `kubectl apply`. On kind you must also add the `--kubelet-insecure-tls` flag, because kind's kubelets use self-signed certificates. The [metrics-server docs](https://github.com/kubernetes-sigs/metrics-server) say this flag is for testing only.

Without CPU requests on the Pods, the HPA cannot work out a percentage. It also scales down slowly on purpose, and waits 5 minutes by default. In the lab, `replicas: 3` in the Deployment equals `minReplicas: 3`, so a new `kubectl apply` does not fight the HPA while the app is quiet.
""")

sec("d18", 5, """
Most problems show up in a Pod's status. Learn these four:
- `Pending`: no node can take the Pod yet. Often the requests are too big, or a volume is missing.
- `ErrImagePull`, then `ImagePullBackOff`: the node cannot get the image. Check the name and tag, and on kind, check that you loaded it.
- `CrashLoopBackOff`: the container starts and exits, again and again. Kubernetes waits longer before each restart.
- Running but `0/1` ready: the readiness probe is failing.

The same four commands solve most of them. Run them in this order:
1. `kubectl get pods -n hello`: which Pod, which status, how many restarts.
2. `kubectl describe pod <name> -n hello`: read the Events at the bottom first.
3. `kubectl logs <name> -n hello --previous`: the output of the container that crashed.
4. `kubectl get events -n hello`: everything that happened recently in the namespace.
""")

x["analogy"] = (
    "A shop manager checks on a clerk in two ways. The liveness check asks whether the clerk is awake at all. "
    "If not, the manager sends them home and calls in someone new. The readiness check asks whether the clerk "
    "can serve customers right now. If the till is broken, the manager puts a closed sign on that counter but "
    "keeps the clerk. Unlike the manager, the kubelet cannot ask why: it only sees pass or fail from one URL."
)

say("d18", 2, "Now a container that crashes as it starts. It runs Python with a command that exits with an "
              "error, which is how a missing setting often looks in a real app. Kubernetes restarts it, waits, "
              "restarts it again, and reports `CrashLoopBackOff`.")
say("d18", 3, "`kubectl logs` shows the current container, which may have just restarted and printed nothing "
              "yet. `--previous` shows the last one that crashed, and that is the one you want.")

x["mistake"] = (
    "The liveness probe should never depend on something outside the container, such as the database. If it "
    "does, a database problem makes every Pod fail liveness and restart at once, which makes the outage worse. "
    "Keep liveness to \"is this process alive\" (`/healthz`) and put dependency checks in readiness (`/readyz`)."
)
x["real_world"] = (
    "PayLite sets each service's CPU and memory requests from real usage seen in monitoring, and an HPA adds "
    "checkout Pods as traffic climbs during big sales. Passwords come from AWS Secrets Manager through External "
    "Secrets Operator, so no secret value is ever in git. The on-call runbook starts with the same three "
    "commands: get pods, describe, and logs with `--previous`."
)

x["deeper"]["body"] = """
Requests and limits do one more job you cannot see in the YAML: they put every Pod into a quality of service (QoS) class. When a node runs short of memory, the kubelet uses these classes to choose which Pods to evict first.

There are three classes:
- Guaranteed: every container has CPU and memory requests equal to its limits. These Pods are evicted last.
- Burstable: at least one container has a request or a limit, but the Pod is not Guaranteed.
- BestEffort: no requests or limits at all. These Pods are evicted first.

Check the lab's Pods with `kubectl get pod <name> -n hello -o jsonpath='{.status.qosClass}'`. They are Burstable, because they request CPU and memory but limit only memory. Among Burstable Pods, the ones using the most memory above their request go first.

To pick good numbers, start from measured usage instead of guesses:
1. Run the app under normal load and watch `kubectl top pods` (or a Grafana dashboard on Day 21).
2. Set the memory request near normal use and the memory limit with room for peaks.
3. Set the CPU request near normal use. The HPA's percentage is based on it, so a request that is far too high makes scaling late.
4. Check again after big changes to the app.

Two related tools are worth knowing by name:
- The Vertical Pod Autoscaler (VPA) watches real usage and suggests or sets requests for you. Do not let it and an HPA both act on CPU for the same Deployment, or they fight.
- KEDA scales on events, such as the length of a queue, and can scale a Deployment down to zero Pods when there is no work.

Probes have edge cases too. Say the readiness probe has a short timeout, and a dependency is slow for a moment. Every Pod can fail readiness at once and drop out of the Service, so a short slowdown becomes a full outage. That is why the lab sets `timeoutSeconds: 2` and `failureThreshold: 2` for readiness instead of the tightest values. Tune probes as carefully as alerts, because they act on their own, often when nobody is watching.
""".strip("\n")

# ---------------------------------------------------------------- d19
x = L["d19"]
x["goal"] = (
    "By the end you can route outside traffic to hello-devops through a Gateway, ship the app as a Helm chart "
    "you can upgrade and roll back, and explain how Kubernetes storage works."
)

sec("d19", 0, """
So far you reached the app through a NodePort or `port-forward`. Real users need one public entry point that sends `shop.example.com/api` to one Service and `/` to another. That is HTTP routing.

For years, Kubernetes did this with Ingress. An Ingress object holds routing rules, and an Ingress controller (a proxy running in the cluster) carries them out. The most popular controller was ingress-nginx.

Two things have changed since then:
- The Ingress API is frozen. It still works and will not be removed, but it gets no new features. The Kubernetes docs recommend the Gateway API instead.
- ingress-nginx is retired. Best-effort maintenance ended in March 2026, and its repository is now read-only. Existing installs keep running, but there are no more releases, bug fixes or security patches.

If you meet ingress-nginx at work, treat it as a migration task. [Ingress2Gateway](https://kubernetes.io/blog/2026/03/20/ingress2gateway-1-0-release) converts Ingress objects, including many nginx annotations, into Gateway API objects for you to review.
""")

sec("d19", 1, """
The **Gateway API** is the newer, official way to route traffic into a cluster. It does not come built in. You add it as CRDs (custom resource definitions: new object types the API server learns), plus a controller that carries them out.

It splits the job into objects owned by different people:
- GatewayClass: which controller to use. The platform team sets it up once. Ours is Envoy Gateway.
- Gateway: an entry point with listeners, such as "HTTP on port 80". The controller starts a proxy for it.
- HTTPRoute: routing rules owned by an app team, such as "`/` goes to Service `hello-devops` on port 80".

Features that Ingress pushed into controller-specific annotations are now real fields: header matching, traffic splits by weight, redirects and more. App teams can add routes without touching the shared Gateway. The core features also work the same across implementations, such as Envoy Gateway, Istio, Cilium, Traefik and the big clouds' own gateways. On a new cluster, start with the Gateway API.
""")

sec("d19", 2, """
To try it you need one implementation. This course uses Envoy Gateway, from the CNCF Envoy project. It installs on kind with one Helm command, and its chart brings the Gateway API CRDs too.

When you apply `k8s/gateway/`, this happens in order:
1. The GatewayClass `eg` tells Envoy Gateway that it owns Gateways of this class.
2. The Gateway `hello-gateway` makes Envoy Gateway start an Envoy proxy Deployment and Service in `envoy-gateway-system`.
3. The HTTPRoute attaches to the Gateway and points at the `hello-devops` Service.
4. Envoy Gateway turns the route into proxy settings, and the proxy starts forwarding.

kind has one catch here. The proxy's Service has type LoadBalancer, and on a cloud that creates a real load balancer with a public address. kind has no cloud, so the Gateway gets no address. You reach the proxy with `kubectl port-forward` instead, as the [Envoy Gateway quickstart](https://gateway.envoyproxy.io/docs/tasks/quickstart/) shows, and the routing behind it works for real.

The Gateway files live in `k8s/gateway/`, outside the main kustomization on purpose, because they only work after Envoy Gateway is installed.
""")

sec("d19", 3, """
Containers lose their files when they restart. For data that must survive, Kubernetes has three objects:
- PersistentVolume (PV): a piece of real storage, such as a cloud disk.
- PersistentVolumeClaim (PVC): a request from an app, such as "1Gi that one node can write".
- StorageClass: a type of storage that can create PVs on demand.

You mostly write PVCs. The StorageClass creates a matching PV for you, which is called dynamic provisioning. kind ships a default StorageClass named `standard` that uses a folder on the node. On EKS, AKS or GKE, the default class creates a cloud disk.

Databases need more than a disk, so they run as a StatefulSet instead of a Deployment. Each Pod gets a stable name (`redis-0`, `redis-1`) and its own PVC, and the Pods start in order.

You can run databases in Kubernetes, but then backups, upgrades and failover are your job. Many teams use a managed database (Amazon RDS, Azure Database, Cloud SQL) and keep the cluster for stateless apps. The lab's Redis has no volume, because it only holds a demo counter.
""")

sec("d19", 4, """
hello-devops is now seven YAML files. Imagine ten teams using it, each with a different image tag, replica count and greeting. Ten hand-edited copies of seven files drift apart fast. Helm, the package manager for Kubernetes, lets you write the files once as templates and fill in the differences.

Three words to learn:
- Chart: a folder with templates (YAML with `{{ }}` placeholders), `values.yaml` (the defaults) and `Chart.yaml` (name and version).
- Values: the settings you pass in with `--set key=value` or `-f my-values.yaml`.
- Release: one installed copy of a chart, with a name and numbered revisions.

The commands follow the life of a release:
- `helm install` and `helm upgrade`: render the templates with your values and apply them. Each run makes a new revision.
- `helm rollback`: return to an earlier revision.
- `helm template` and `helm lint`: print or check the YAML without touching the cluster.

Helm 4 is the current version, and day to day it feels like Helm 3. Two changes are worth knowing. New installs use server-side apply, where the API server merges the changes. And the `--atomic` flag is now called `--rollback-on-failure`.
""")

sec("d19", 5, """
Helm is not the only way to vary YAML. Kustomize is built into kubectl, and you already use it: `kubectl apply -k k8s` reads `k8s/kustomization.yaml`.

Kustomize has no templates. You keep plain YAML as a base and add overlays that patch it. A typical layout:
- `k8s/` is the base: the app as it is today.
- `overlays/dev/kustomization.yaml` points at the base and sets 1 replica.
- `overlays/prod/kustomization.yaml` points at the same base and sets 6 replicas and a newer image tag.

`kubectl kustomize overlays/prod` prints the result, and `kubectl apply -k overlays/prod` applies it.

For other people's software, such as databases, monitoring or Argo CD, use Helm, because that is the usual way to install it. For your own apps, Kustomize is popular because the files stay plain YAML. Many teams use both. On Day 20, Argo CD reads your `k8s/` folder with Kustomize.
""")

x["analogy"] = (
    "A Helm chart is like a recipe card with blanks: \"___ grams of sugar, bake for ___ minutes\". "
    "`values.yaml` fills in the usual amounts, and `--set` changes one of them for tonight. The kitchen notes "
    "every bake in a logbook (the release history), so you can make an earlier version again. One difference "
    "matters: a recipe makes a new dish each time, while `helm upgrade` changes the dish that "
    "is already on the table."
)

say("d19", 1, "Change two values. `helm show values` lists every setting a chart accepts, and podinfo has "
              "`replicaCount` and `ui.message` among them. Helm renders the chart again, applies the difference, "
              "and the revision goes up. In real work, also pin the chart with `--version`.")
say("d19", 3, "Roll back to revision 1. Helm does not erase revision 2. It writes a new revision 3 with the same "
              "content as revision 1, so the history still shows everything that happened.")

x["mistake"] = (
    "You run `helm upgrade` with one new `--set`, and the values you set at install time are gone. When you "
    "pass values on an upgrade, Helm starts again from the chart's defaults plus only the values you give now. "
    "Keep your settings in a values file (like `chart/kind-values.yaml`) and pass it with `-f` on every install "
    "and upgrade."
)
x["real_world"] = (
    "Each PayLite cluster has one shared Gateway, owned by the platform team along with the TLS certificates, "
    "and each product team adds HTTPRoutes for its own paths. Third-party tools such as Envoy Gateway and the "
    "monitoring stack are installed from Helm charts pinned to exact versions. PayLite's own services use "
    "Kustomize overlays for dev and prod, and the card database is a managed service outside the cluster."
)

x["deeper"]["body"] = """
The lab's Redis forgets the visit count whenever its Pod restarts. A StatefulSet with a volume fixes that. Treat these steps as a sketch to try on your own, in a copy of `redis.yaml`:
1. Change `kind: Deployment` to `kind: StatefulSet`, and add `serviceName: redis` under `spec`.
2. Add a `volumeClaimTemplates` section: a PVC template named `data`, with access mode `ReadWriteOnce` and a request of `1Gi`. The StatefulSet makes one PVC per Pod, called `data-redis-0`.
3. Mount that volume at `/data` in the Redis container. The official Redis image keeps its files there.
4. Turn on saving: run Redis with `redis-server --appendonly yes`, so each write also goes to disk.
5. Apply it, count a few visits, then delete the Pod `redis-0`. The StatefulSet recreates it with the same name and the same PVC, and the count carries on.

Check the pieces with `kubectl get pvc -n hello` and `kubectl get pv`. On kind, the PV is a folder inside a node container, so deleting the cluster deletes the data. For practice that is fine.

Things that surprise people:
- Deleting a StatefulSet does not delete its PVCs. This protects data, but you must clean up by hand.
- `ReadWriteOnce` means one node at a time. A Pod on another node cannot mount the volume.
- kind's `standard` class uses `volumeBindingMode: WaitForFirstConsumer`. The volume is created only when a Pod needs it, on that Pod's node.
- A StorageClass's `reclaimPolicy` decides what happens to the volume when you delete the PVC. `Delete` removes it, and `Retain` keeps it for manual recovery.

Many teams still keep important data out of the cluster, because a real database needs tested backups, version upgrades, replication and failover. Operators (controllers built for one database, such as CloudNativePG for Postgres) automate much of this. A managed database does it for you, for a price. For a cache or a lab, a StatefulSet with a PVC is enough.

Your chart has one more Helm detail worth a look. `templates/deployment.yaml` has a `checksum/config` annotation that holds a hash of the rendered ConfigMap. When you change the greeting, the hash changes, so the Pod template changes and Kubernetes rolls out new Pods. Without it, `helm upgrade` would update the ConfigMap while the old Pods kept the old greeting. The [Helm tips page](https://helm.sh/docs/howto/charts_tips_and_tricks/) calls this pattern "automatically roll deployments".
""".strip("\n")

P.write_text(json.dumps(d, ensure_ascii=False, indent=1) + "\n")
print("wrote", P)
