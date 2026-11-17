NEW = {}

NEW["goal"] = "By the end you can give hello-devops health checks and resource settings that match what it needs, autoscale it with an HPA, and control where its Pods run and how many may be down at once."

NEW["opening"] = """Picture a Friday night again. The manager's clipboard says four waiters are on the floor, and that is true. But one of them has stood frozen at the coffee machine for ten minutes, and another cannot take orders because their card reader is broken. The count is right, and guests are still waiting. Being present is not the same as working.

Last time, hello-devops got its settings from a ConfigMap and started sharing one visit counter in Redis. That made it more useful, and also more fragile: if Redis stops answering, the app is up but cannot do its job. Kubernetes sees a running process and counts it as fine, which is exactly the clipboard's mistake.

In this lesson, we'll teach Kubernetes to tell a working Pod from a frozen one. Then we'll give each Pod the room it needs, add Pods when visitors pile up and keep enough on the floor during planned work. Before we start, make a guess, and keep it in mind."""

NEW["guess"] = (
    "A container uses more CPU (computing power) than its CPU limit, the most it is allowed, for a few seconds. What does Kubernetes do?",
    "Linux slows the container down (throttles it), so it runs slower but keeps going. A container gets killed only when it goes over its memory limit.",
)

NEW["terms"] = [
    "A regular check of a container; after enough failures in a row, the kubelet restarts it.",
    "A regular check; while it fails, the Pod gets no visitors from Services, but keeps running.",
    "A check that holds back the other checks until a slow app has finished starting.",
    "The CPU and memory the scheduler sets aside for a container on a node.",
    "The most CPU or memory a container may use; over the memory limit it is killed.",
    "Guaranteed, Burstable or BestEffort; it decides which Pods a node removes first when it runs short.",
    "An object that changes a Deployment's number of Pods based on measurements such as CPU use.",
    "A rule for planned work, such as emptying a node: at most this many of an app's Pods may be down at once.",
]

S = []

S.append(("Running is not the same as healthy", """
Since Day 39, Kubernetes has restarted your containers whenever their process (the running program) exits, so crashes are handled. But an app can stay up and still be useless. It can be stuck, like the waiter at the coffee machine. Or it can be running but unable to reach its database, like the waiter with the broken card reader. From the outside, both look like a healthy process.

A **probe** is a small check that the kubelet, the helper program on each node, runs against a container on a timer. The check runs right next to the container. The lab uses HTTP probes: the kubelet asks for a web address, and any status code from 200 to 399 counts as a pass. A status code is the number a web server sends back, such as 200 for "OK" or 503 for "not available".

There are three probes. Each asks a different question, and a failure leads to a different action:
- Startup probe: "Have you finished starting?" Until it passes, the other two wait, so a slow start is not mistaken for a stuck app. If it never passes, the container is restarted.
- Liveness probe: "Are you stuck?" After enough failures in a row, the kubelet kills the container and starts a new one. The frozen waiter goes home, and a fresh one comes in.
- Readiness probe: "Can you take visitors right now?" While it fails, the Pod gets no visitors from Services. Nothing restarts. The waiter with the broken reader stays, but no new tables go to them.

Our app, hello-devops, already has two addresses for this. The `/healthz` address answers as long as the Python process can serve a request. The `/readyz` address also checks Redis and returns 503 when Redis is down. Today you add all three probes to `k8s/deployment.yaml`: startup and liveness on `/healthz`, readiness on `/readyz`. Redis has one already: `k8s/redis.yaml` from Day 42 runs `redis-cli ping` as a readiness probe.

Three questions, three actions. Next, we set how quickly each one acts, and meet the mistake that turns a small problem into a big one.
"""))

S.append(("Probe timing, and the liveness trap", """
Every probe takes the same four timing settings:
- `periodSeconds`: how often to check. Default 10.
- `timeoutSeconds`: how long one check may take. Default 1.
- `failureThreshold`: how many failures in a row before the kubelet acts. Default 3.
- `initialDelaySeconds`: how long to wait after the container starts. Default 0.

Multiply them to see how fast each probe acts. In the lab's Deployment, the startup probe allows 30 failures, 2 seconds apart, so the app gets up to 60 seconds to start. The liveness probe needs 3 misses 10 seconds apart, so a stuck container is replaced after about 30 seconds. The readiness probe checks every 5 seconds and acts after 2 misses, so a Pod stops getting visitors within about 10 seconds.

You may be thinking, "Why not just give liveness a long `initialDelaySeconds`?" That is a fixed guess. Set it for the slowest start, and liveness is blind that long after every start. A startup probe hands over to liveness the moment the app answers.

Now the trap. Picture Redis going down for a minute while `/healthz` checks Redis. Every hello-devops Pod fails liveness at about the same time, and the kubelet restarts all of them. The restarts cannot fix Redis, and while they happen no Pod can serve anything. The [probes docs](https://kubernetes.io/docs/concepts/workloads/pods/probes/) warn that a wrong liveness probe "can lead to cascading failures", one failure setting off the next.

**Liveness asks about the container alone. Leave the database out of it.**

Checks on other services belong in readiness, because failing it only pauses visitors. Readiness has a limit too. If every Pod fails it at once, the Service has no ready Pods left and users get errors. So the lab's readiness probe allows a 2-second timeout and 2 failures, not the tightest values.

How does a failed check stop visitors? The kubelet writes each result into the Pod's status as its Ready condition. The EndpointSlice controller copies it onto the Pod's entry in the Service's list, and kube-proxy skips entries that are not ready (Day 41). The Deployment controller reads the same condition. This is the probe Day 40 promised: it tells a rolling update when a new Pod is ready.

Probes tell Kubernetes whether a Pod works. Next, we tell it how much room each Pod needs.
"""))

S.append(("Requests and limits: what you reserve and what you may use", """
When a party books a table, the restaurant sets aside chairs for them, and there is also a most that the room can take. Each container can state the same two things for CPU and memory. CPU is counted in cores: `100m` means 100 millicores, a tenth of one core. Memory is counted in bytes: `128Mi` means 128 mebibytes, a little over 128 million bytes.

The two numbers do different jobs:
- A request is what the scheduler sets aside. It puts a Pod only on a node whose free room fits the request. If no node fits, the Pod stays `Pending`.
- A limit is the most the container may use. Linux enforces it while the container runs, with cgroups (the feature Docker also uses to limit containers).

The scheduler counts requests, not live use, because a node that looks idle at night may be full at the daily peak. Between its request and its limit, a container may use whatever the node has spare.

At the limit, the two resources behave very differently: too much CPU makes you slow, and too much memory gets you killed. Linux can share out CPU time in small slices, so a container at its CPU limit is throttled: it keeps running, only slower. Memory cannot be taken back once a program holds it. A container that goes over its memory limit is killed by the out-of-memory (OOM) killer. Kubernetes then shows `OOMKilled` and exit code 137. That is the answer to the guess, and the worked example shows the memory side.

The Deployment you update today asks for `100m` CPU and `128Mi` memory, and limits memory to `256Mi`. It sets no CPU limit on purpose. Linux enforces a CPU limit as a time budget: with `200m`, the container gets 20 ms of CPU in every 100 ms, then waits. It waits even when other cores sit idle, and you see that as slow answers that are hard to explain. For a web app like this one, I would skip the CPU limit and rely on the request.

Requests are a different story: always set them. The scheduler, the autoscaler and the order of removal all depend on them. Skipping them is the first pitfall in the Kubernetes blog's [7 common pitfalls](https://kubernetes.io/blog/2025/10/20/seven-kubernetes-pitfalls-and-how-to-avoid/). That order of removal is next.
"""))

S.append(("QoS classes, LimitRanges and ResourceQuotas", """
When a room is overfull, someone has to leave, and a restaurant asks walk-ins first and booked guests last. A node does the same. Your requests and limits put each Pod into a quality of service (QoS) class. When a node runs short of memory, the kubelet evicts (removes) whole Pods to protect itself, and the class decides who goes first:
- BestEffort: no requests or limits at all. Evicted first.
- Burstable: at least one request or limit, but not Guaranteed. The lab's Pods are here.
- Guaranteed: every container has CPU and memory requests equal to its limits. Evicted last.

Eviction is different from an OOM kill. An OOM kill hits one container that broke its own limit. Eviction removes Pods because the node as a whole is short, and their Deployment recreates them on another node.

In a cluster that many teams share, one team could reserve most of the nodes, or run Pods with no limits at all. So admins add two guard rails per namespace:
- A LimitRange sets default requests and limits for containers that set none, plus a minimum and maximum per container.
- A ResourceQuota caps the total for the whole namespace, such as 4 CPUs of requests, 8Gi of memory or 20 Pods.

With a quota on CPU or memory, the API server may reject any Pod that does not state those requests. A LimitRange with defaults fixes that for teams who forget. Your laptop needs neither. At work you often meet them as an error message the first time you deploy to a new namespace.

So far the number of Pods was fixed. Next, we let Kubernetes change it.
"""))

S.append(("Calling in more waiters: the HorizontalPodAutoscaler", """
When the queue at the door grows, a good manager calls in extra waiters, and sends them home only once it has been quiet for a while. A HorizontalPodAutoscaler (HPA) does that for a Deployment. It is one more control loop, run by the controller manager from Day 38. Every 15 seconds it does this:
1. Reads the current CPU use of each Pod from the metrics API (more on that below).
2. Turns it into a percentage of the Pod's CPU request, and averages it.
3. Works out how many replicas would bring the average back to the target.
4. Sets the Deployment's replica count, between `minReplicas` and `maxReplicas`.

Step 3 is one line of math: `desired = ceil(currentReplicas * currentValue / targetValue)`, where `ceil` rounds up. The lab's `k8s/hpa.yaml` targets 70% of the 100m request, so 70m per Pod. Say 3 Pods average 140m under load. That is twice the target, so the HPA asks for ceil(3 * 140 / 70) = 6 Pods. It ignores changes within 10% of the target, so the count does not jump around.

It scales up at once, but scales down slowly on purpose. By default it wants 5 minutes of lower numbers before it removes Pods. The lab shortens that to 2 minutes with `behavior.scaleDown.stabilizationWindowSeconds: 120`, so you can watch it happen.

The numbers come from metrics-server, a small add-on that asks each kubelet for CPU and memory use. kind does not ship it. After you install it, you add one flag, `--kubelet-insecure-tls`, because kind's kubelets use certificates they signed themselves. The [metrics-server README](https://github.com/kubernetes-sigs/metrics-server) says this flag is for testing only. Until numbers arrive, `kubectl get hpa` shows `cpu: <unknown>/70%`.

Before you trust the HPA, check two things:
- Without a CPU request on the Pods, it has no percentage to compute, so it does nothing.
- Each `kubectl apply` resets the count to the Deployment's `replicas`, undoing the HPA. The HPA docs suggest removing the field. The lab keeps `replicas` equal to `minReplicas` instead, so the two agree when the app is quiet.

More waiters is one answer. Next, the other: bigger sections for the same waiters.
"""))

S.append(("Growing each Pod: the VPA and in-place resize", """
The HPA adds Pods. The other direction is to make each Pod bigger, which is called vertical scaling.

The Vertical Pod Autoscaler (VPA) watches real CPU and memory use over time and recommends requests. It is an add-on. You install its controllers and its CRDs yourself. A CRD (custom resource definition) teaches the API server a new kind of object. The VPA reads the same metrics API as the HPA. Its `updateMode` decides how far it goes:
- `Off`: only write recommendations. A safe way to learn what your app needs.
- `Initial`: set requests when Pods are created, never later.
- `Recreate`: evict Pods whose requests are far off, so they come back with new numbers.
- `InPlaceOrRecreate` and `InPlace`: change running Pods without a restart when the node allows it.

Do not let a VPA and an HPA both act on CPU for the same Deployment. The VPA raises the request, which lowers the HPA's percentage, and the two keep undoing each other's work, like two managers moving the same waiter back and forth.

Those last two modes rest on in-place Pod resize, stable since Kubernetes 1.35. Before it, a Pod kept the same resources for its whole life. With it, you can change a running Pod's resources with `kubectl patch pod <name> --subresource resize --patch '...'`. Each container's `resizePolicy` says whether a change needs a restart. The default, `NotRequired`, applies the new numbers to the running container.

Resize works on single Pods. Changing a Deployment's template still rolls out new Pods (Day 40), and day to day that is what you do. In-place resize matters most to the VPA and to Pods that are slow to restart.

We know how many Pods run and how big each is. Last, we decide where they go, and how many may leave at once.
"""))

S.append(("Where Pods land, and how many may leave", """
A restaurant seats some guests only on the terrace, keeps a few tables for staff and never wants all its waiters on one side of the room. The scheduler picks a node for each Pod from the nodes that fit its requests, and you can steer that choice in the same ways. You need this when a Pod needs special hardware, such as a GPU (a graphics chip), or when replicas should not all share one node. From simple to strong:
1. `nodeSelector`: run only on nodes with this label, such as `disktype: ssd`.
2. Node affinity: the same idea with more operators. A `required` rule must match; a `preferred` rule is a wish the scheduler weighs.
3. Pod affinity and anti-affinity: place Pods near or away from other Pods, by their labels. Anti-affinity on `kubernetes.io/hostname`, a label every node has, spreads replicas over nodes.
4. Taints and tolerations: a taint on a node keeps Pods away, and a toleration on a Pod lets it in anyway.

The first three are rules on the Pod, about where it wants to go. A taint is a rule on the node, about which Pods it turns away: a "staff only" sign. Your cluster already has one. kind's control-plane node carries `node-role.kubernetes.io/control-plane:NoSchedule`, so your app Pods only ever land on the two workers. The prod overlay on Day 45 uses anti-affinity, so one node failure is less likely to take every Pod.

A PodDisruptionBudget (PDB) answers a different question: how many Pods may be gone at once. Kubernetes splits disruptions into two kinds. Voluntary ones are planned, such as a `kubectl drain` (emptying a node) before maintenance, or a cluster upgrade. Involuntary ones just happen: a node crashes or loses power. A PDB limits only the voluntary kind, like a rule that training sessions never take more than one waiter off the floor.

A drain never deletes Pods directly. It asks the API server to evict them, and the API server refuses any eviction that would break a PDB. With 3 replicas and `minAvailable: 2`, one eviction passes. The next is refused until the replacement is ready on another node, and drain keeps retrying. A PDB cannot stop a crash. For that, spread the replicas over several nodes. The worked example now breaks a memory limit on purpose, so you know the evidence when you see it.
"""))

NEW["sections"] = S

NEW["drop"] = ["analogy", "real_world", "mistake"]

NEW["diagram_caption"] = "Three probes, three different actions: wait, restart, or stop sending visitors."

NEW["worked"] = [
    "Start a Pod that grabs 150 MB of memory but may use only 100Mi. It runs Python from the hello-devops image, which your kind nodes already have, so nothing is downloaded.",
    "Watch it. Within seconds Linux kills it. Kubernetes restarts it, it dies again, and the waits between restarts grow: that is `CrashLoopBackOff`. Press Ctrl+C to stop watching.",
    "The `describe` output keeps the reason of the last crash under Last State. The reason `OOMKilled` with exit code 137 means Linux sent SIGKILL, the stop-now signal, because the container went over its memory limit.",
    "The crashed container's log is empty. Python never reached its print line, and a program killed from outside gets no chance to write an error. An empty log plus exit code 137 points at memory, not at your code.",
    "Look at what Kubernetes stored. You set only a memory limit, so it copied the limit into the memory request. With no CPU numbers at all, the Pod is Burstable, not Guaranteed.",
    "Fix it. A bare Pod's resources only change through the resize subresource, so the simple path is delete and recreate. Run the command from step 1 again with `memory: 256Mi`. A Deployment would replace the Pod for you.",
    "Clean up. In real work you would pick the new limit from measured use, with `kubectl top pod`.",
]

NEW["task"] = (
    [
        "Add the three probes and the resources to `k8s/deployment.yaml` (the file above) and apply with `kubectl apply -k k8s`. Work out from the timing settings how long each probe takes to act, and check the probes in `kubectl describe pod`.",
        "In a second terminal, run `kubectl get pods -n hello -w`. Scale Redis to 0 replicas and watch the hello-devops Pods go to `0/1` READY while RESTARTS stays at 0. Try `curl localhost:8081`, and explain the result from what the Service's EndpointSlice now holds.",
        "Scale Redis back to 1 and watch the app Pods become ready again on their own.",
        "Install metrics-server, add the `--kubelet-insecure-tls` flag, and wait until `kubectl top pods -n hello` prints numbers.",
        "Write `k8s/hpa.yaml`, add it to `k8s/kustomization.yaml`, and apply with `kubectl apply -k k8s`. Check that `kubectl get hpa -n hello` shows a real percentage instead of `<unknown>`.",
        "Start the load generator Pod from the commands list and watch `kubectl get hpa -n hello -w` until REPLICAS goes above 3. Delete the load Pod and watch the count return to 3 after about 2 quiet minutes.",
        "Create a PodDisruptionBudget for hello-devops with `minAvailable` 2 and read ALLOWED DISRUPTIONS in `kubectl get pdb -n hello`.",
        "Drain the node `devops-worker` while you watch the Pods move, then make it schedulable again with `kubectl uncordon`.",
        "Print the QoS class of one hello-devops Pod and of the Redis Pod, and explain each from their resources.",
    ],
    [
        "No scale-up? One load Pod may not be enough on a fast Mac. Start a second one with another name, and check `kubectl top pods -n hello`.",
        "The drain needs `--ignore-daemonsets` (kindnet and kube-proxy run on every node) and `--delete-emptydir-data` (metrics-server keeps scratch files in an emptyDir).",
        "HPA still `<unknown>`? Look at `kubectl logs -n kube-system deployment/metrics-server`. A missing `--kubelet-insecure-tls` flag shows up there as certificate errors.",
    ],
    "`kubectl get hpa -n hello` showed more than 3 replicas under load, and `kubectl drain` moved the app Pods without ever leaving fewer than 2 ready.",
)

NEW["explain_back"] = (
    "Explain in 3 to 4 sentences why the hello-devops Pods went to 0/1 READY but did not restart when you scaled Redis to zero. Mention both probes and what each one checks.",
    "The readiness probe calls `/readyz`, which checks Redis, so it started returning 503, the Pods were marked not ready, and the Service stopped sending them visitors. The liveness probe calls `/healthz`, which only checks that the process answers, so it kept passing and the kubelet had no reason to restart anything. When Redis came back, `/readyz` passed again and the Pods rejoined the Service without anyone touching them. If liveness had checked Redis, every Pod would have restarted for nothing.",
)

NEW["recap"] = [
    "Startup holds back the other probes, liveness restarts a stuck container, readiness only stops visitors.",
    "Keep dependencies out of liveness; a shared outage would restart every Pod at once.",
    "Requests decide placement; over the memory limit means OOMKilled (exit 137), at the CPU limit means throttling.",
    "Requests and limits set the QoS class, which decides eviction order when a node runs short.",
    "An HPA needs metrics-server (with `--kubelet-insecure-tls` on kind) and CPU requests; it scales up fast and down slowly.",
    "A limit to remember: a PDB guards only planned work such as a drain; against crashes, spread replicas over nodes.",
]

NEW["closing"] = """We started with a clipboard that counted four waiters while two of them could not serve. Probes fixed the count: liveness sends the frozen one home, readiness stops seating guests with the one whose reader broke. Requests, limits and the HPA then decide how much room each Pod gets and how many there are. In the task, scale Redis to zero and watch READY drop while RESTARTS stays still; that quiet gap is the whole point. Visitors still reach us through a NodePort on one laptop port, though. Next, we'll build a real front entrance and give Redis a disk. How do many apps share one door, and how does data survive a restart?"""

NEW["check"] = [
    ("A Spring Boot service needs about 90 seconds to start. Its liveness probe kills it after 30 seconds, again and again. What is the best fix?",
     "A startup probe holds the liveness probe back until the app has started, so a slow start is not mistaken for a stuck process."),
    ("metrics-server works and `kubectl top pods` prints numbers, but the HPA still shows `cpu: <unknown>/70%`. What is the most likely cause?",
     "A utilization target is a percentage of the CPU request, so without a request the HPA has nothing to divide by."),
    ("A Deployment has 3 replicas and a PDB with `minAvailable: 3`. You run `kubectl drain` on the node that holds one of them. What happens?",
     "With all 3 required, the budget allows 0 disruptions, so every eviction is refused until you change the PDB or add replicas."),
]

NEW["interview"] = [
    ("What is the difference between liveness, readiness and startup probes?",
     "A liveness probe checks whether the container is stuck; after repeated failures the kubelet restarts it. A readiness probe checks whether the Pod can take traffic; while it fails, the Pod gets no Service traffic but keeps running. A startup probe protects slow starters by holding the other two back until it passes. Liveness should test only the process itself, while readiness may check dependencies such as a database."),
    ("How do requests and limits work, and what happens when a container goes over them?",
     "Requests are what the scheduler reserves, so they decide which node a Pod can go on, and the HPA computes percentages from them. Limits are the most a container may use, enforced by the kernel through cgroups. Over the memory limit the container is OOMKilled with exit code 137; at the CPU limit it is only throttled. I always set requests and a memory limit. I am careful with CPU limits on a service where response time matters, because they throttle it even when the node has idle CPU."),
    ("An HPA is not scaling. How do you find out why?",
     "First `kubectl get hpa` to see the current value: `<unknown>` means no metrics, so check that metrics-server runs and that the Pods have CPU requests. Then `kubectl describe hpa` shows conditions such as AbleToScale and ScalingActive, plus events that explain each decision. If metrics look fine, check whether the count is already at `maxReplicas`, or whether the target is so high that the load never crosses it. Last, look for a second controller, such as a VPA on CPU or a deploy tool resetting `replicas`."),
]

NEW["deeper"] = """
Picking good numbers is most of the work with resources, and guessing goes wrong in both directions. Requests that are too high waste nodes and make the HPA react late, because each Pod looks idle. Requests that are too low pack too many Pods onto a node and make the HPA scale early and often.

A simple way to start from data:
1. Run the app under normal load for a day and look at its use with `kubectl top pods`, or a Grafana dashboard once you reach Part 13.
2. Set the memory request near normal use and the memory limit with room for peaks, often about twice the request.
3. Set the CPU request near normal use. The HPA's percentage is based on it, so this number also sets when scaling starts.
4. Run a VPA in `Off` mode next to the app. Its recommendations are a second opinion that costs nothing.
5. Check again after big changes to the app, such as a new framework version or a new cache.

A few details the sections skipped. A probe can also run a command in the container (`exec`), open a TCP connection (`tcpSocket`) or call a gRPC health check. Kubernetes ignores the `HEALTHCHECK` line in your Dockerfile (Part 5); only plain Docker reads it, and in a cluster probes do its job. And exit code 137 means the process got signal 9, SIGKILL (128 + 9).

CPU is not always the right signal to scale on. A worker that reads jobs from a queue may sit at low CPU while thousands of jobs wait. KEDA, a CNCF project, scales Deployments on events such as queue length, and can scale to zero when there is no work. Kubernetes 1.37 also lets an HPA scale to zero by itself as a beta, when it uses an object or external metric.

All of this scales Pods. When the nodes are full, new Pods stay `Pending`. Node autoscalers, such as the Cluster Autoscaler or Karpenter on a cloud, notice those Pending Pods and add nodes. When nodes are under-used, they drain and remove them, and that drain respects your PDBs. A kind cluster cannot add nodes, so on your laptop the ceiling is the memory you gave Docker Desktop.

Treat probe settings like alert rules, because a probe acts on its own, often when nobody is watching. On a busy team, probe changes go through code review for that reason. Before you tighten a timeout, ask what happens if every Pod fails that probe in the same minute.
"""
