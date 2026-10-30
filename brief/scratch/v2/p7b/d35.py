"""Day 35: Health checks, resources and scaling."""
from svg import arrow, box, cap, svg


def diagram():
    h = 44
    p = [
        box(16, 103, 96, h, "bxt", "kubelet"),
        box(152, 24, 136, h, "bx", "startup", "GET /healthz"),
        box(152, 103, 136, h, "bx", "liveness", "GET /healthz"),
        box(152, 182, 136, h, "bx", "readiness", "GET /readyz"),
        box(368, 24, 180, h, "bxg", "Others wait"),
        box(368, 103, 180, h, "bxo", "Restart container"),
        box(368, 182, 180, h, "bxp", "No Service traffic"),
        arrow(112, 116, 150, 50), arrow(112, 125, 150, 125), arrow(112, 134, 150, 200),
        arrow(288, 46, 366, 46), cap(327, 38, "until pass"),
        arrow(288, 125, 366, 125), cap(327, 117, "3 misses"),
        arrow(288, 204, 366, 204), cap(327, 196, "2 misses"),
    ]
    return svg(242, "The kubelet runs three probes: startup holds the others back, liveness restarts the container, readiness removes the Pod from Service traffic", p)


WORKED_POD = """$ kubectl apply -n hello -f - <<'EOF'
apiVersion: v1
kind: Pod
metadata:
  name: hog
spec:
  containers:
    - name: hog
      image: hello-devops:1.0.0
      command: ["python", "-c", "import time; data = bytearray(150 * 1024 * 1024); print('got 150 MB'); time.sleep(3600)"]
      resources:
        limits:
          memory: 100Mi
EOF
pod/hog created"""

LESSON = {
    "id": "d35",
    "title": "Health checks, resources and scaling",
    "minutes": 50,
    "goal": "By the end you can give hello-devops health checks and resource settings that match what it needs, autoscale it with an HPA, and control where its Pods run and how many may be down at once.",
    "guess": {
        "q": "A container uses more CPU than its CPU limit for a few seconds. What does Kubernetes do?",
        "options": [
            "Kills the container and starts a new one",
            "Slows it down, and it keeps running",
            "Moves the Pod to a node with more CPU",
            "Marks the Pod not ready until it calms down",
        ],
        "answer": 1,
        "why": "CPU can be handed out in smaller slices, so the kernel throttles the container and it runs slower. Only going over the memory limit gets a container killed.",
    },
    "terms": [
        {"term": "Liveness probe", "plain": "A regular check of a container; after enough failures in a row, the kubelet restarts it."},
        {"term": "Readiness probe", "plain": "A regular check; while it fails, the Pod gets no traffic from Services, but keeps running."},
        {"term": "Startup probe", "plain": "A check that holds back the other probes until a slow app has finished starting."},
        {"term": "Resource request", "plain": "The CPU and memory the scheduler reserves for a container on a node."},
        {"term": "Resource limit", "plain": "The most CPU or memory a container may use; over the memory limit it is killed."},
        {"term": "QoS class", "plain": "Guaranteed, Burstable or BestEffort: decides which Pods a short node evicts first."},
        {"term": "HorizontalPodAutoscaler (HPA)", "plain": "An object that changes a Deployment's number of Pods based on metrics such as CPU."},
        {"term": "PodDisruptionBudget (PDB)", "plain": "A rule that limits how many Pods of an app planned work, such as a node drain, may take down at once."},
    ],
    "sections": [
        {
            "h": "Running is not the same as healthy",
            "body": (
                "Since Day 31, Kubernetes has restarted your containers when their process exits. That covers crashes. "
                "It does not cover an app that is still running but stuck, or one that is up but cannot reach its database. "
                "From the outside, both look like a healthy process.\n\n"
                "A **probe** is a small check that the kubelet runs against a container on a timer. "
                "The kubelet is the agent on each node (Day 30), so the check runs right next to the container. "
                "The lab uses HTTP probes: the kubelet sends a GET request, and any status from 200 to 399 counts as a pass. "
                "A probe can also run a command in the container (`exec`), open a TCP connection (`tcpSocket`) or call a gRPC health check.\n\n"
                "There are three probes. Each asks a different question, and a failure leads to a different action:\n"
                "- Startup probe: \"Have you finished starting?\" Until it passes, the other two wait. If it never passes, the container is restarted.\n"
                "- Liveness probe: \"Are you stuck?\" After enough failures in a row, the kubelet kills the container and starts a new one.\n"
                "- Readiness probe: \"Can you take traffic right now?\" While it fails, the Pod leaves the Service's endpoints. Nothing restarts.\n\n"
                "hello-devops has two endpoints made for this. The `/healthz` endpoint answers as long as the Python process can serve a request. "
                "The `/readyz` endpoint also pings Redis and returns 503 when Redis is down. "
                "Today you add all three probes to `k8s/deployment.yaml`: startup and liveness on `/healthz`, readiness on `/readyz`. "
                "Redis already has one: `k8s/redis.yaml` from Day 34 runs `redis-cli ping` as an `exec` readiness probe.\n\n"
                "One surprise: Kubernetes does not run the `HEALTHCHECK` line from your Dockerfile (Part 3). "
                "That line only matters when you run the image with plain Docker. In a cluster, probes take its place."
            ),
            "refs": [
                {"title": "Liveness, readiness and startup probes", "url": "https://kubernetes.io/docs/concepts/workloads/pods/probes/", "kind": "docs"},
                {"title": "Configure liveness, readiness and startup probes", "url": "https://kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes/", "kind": "docs"},
                {"title": "Kubernetes health probes explained (Tech Tutorials with Piyush, CKA series)", "url": "https://www.youtube.com/watch?v=x2e6pIBLKzw", "kind": "watch"},
            ],
        },
        {
            "h": "Probe timing, and the liveness trap",
            "body": (
                "Every probe has the same four timing settings, and you should be able to read them:\n"
                "- `periodSeconds`: how often to check. Default 10.\n"
                "- `timeoutSeconds`: how long one check may take. Default 1.\n"
                "- `failureThreshold`: how many failures in a row before the kubelet acts. Default 3.\n"
                "- `initialDelaySeconds`: how long to wait after the container starts. Default 0.\n\n"
                "Multiply them to see how fast each probe acts. In the lab's Deployment, the startup probe allows 30 failures, 2 seconds apart, so the app gets up to 60 seconds to boot. "
                "The liveness probe needs 3 misses 10 seconds apart, so a stuck container is replaced after about 30 seconds. "
                "The readiness probe checks every 5 seconds and acts after 2 misses, so a Pod leaves the Service within about 10 seconds.\n\n"
                "Now the trap, which catches many teams. Never make the liveness probe depend on something outside the container, such as a database. "
                "Picture Redis going down for a minute while `/healthz` checks Redis. Every hello-devops Pod fails liveness at about the same time, and the kubelet restarts all of them. "
                "The restarts cannot fix Redis, and while they happen no Pod can serve anything. "
                "The [probes docs](https://kubernetes.io/docs/concepts/workloads/pods/probes/) warn that a wrong liveness probe \"can lead to cascading failures\".\n\n"
                "Readiness is the right place for dependency checks, because failing it only pauses traffic. Even there, be careful. "
                "If every Pod fails readiness at once, the Service has no endpoints left and users get errors. "
                "That is why the lab's readiness probe allows a 2-second timeout and 2 failures instead of the tightest values.\n\n"
                "Readiness also guards rollouts. On Day 32 a rolling update waited for new Pods to become ready before it removed old ones. That wait is this probe."
            ),
            "refs": [
                {"title": "Configure liveness, readiness and startup probes", "url": "https://kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes/", "kind": "docs"},
                {"title": "7 common Kubernetes pitfalls (Kubernetes blog)", "url": "https://kubernetes.io/blog/2025/10/20/seven-kubernetes-pitfalls-and-how-to-avoid/", "kind": "read"},
            ],
        },
        {
            "h": "Requests and limits: what you reserve and what you may use",
            "body": (
                "Each container can say how much CPU and memory it needs. CPU is counted in cores: `100m` means 100 millicores, a tenth of one core. "
                "Memory is counted in bytes: `128Mi` means 128 mebibytes.\n\n"
                "There are two numbers, and they do different jobs:\n"
                "- A request is what the scheduler reserves. It puts a Pod only on a node whose unreserved room fits the request. If no node fits, the Pod stays `Pending`.\n"
                "- A limit is the most the container may use. The Linux kernel enforces it while the container runs, with cgroups (the kernel feature Docker also uses to limit containers).\n\n"
                "What happens at the limit depends on the resource, and this trips most people up. "
                "CPU time can be handed out in smaller slices, so a container at its CPU limit is throttled: it keeps running, only slower. "
                "Memory cannot be taken back once a process holds it. A container that goes over its memory limit is killed by the kernel's out-of-memory (OOM) killer. "
                "Kubernetes then shows `OOMKilled` and exit code 137. The 137 means the process got signal 9, SIGKILL (128 + 9).\n\n"
                "A short way to remember it: too much CPU makes you slow, too much memory gets you killed.\n\n"
                "The Deployment you update today asks for `100m` CPU and `128Mi` memory, and limits memory to `256Mi`. It sets no CPU limit on purpose. "
                "A CPU limit throttles a container even when the node has idle cores, which shows up as slow responses that are hard to explain. "
                "For a web app like this one, I would skip the CPU limit and rely on the request.\n\n"
                "Requests are a different story: always set them. The scheduler, the autoscaler and the eviction order all depend on them. "
                "Skipping them is the first pitfall in the Kubernetes blog's [7 common pitfalls](https://kubernetes.io/blog/2025/10/20/seven-kubernetes-pitfalls-and-how-to-avoid/). "
                "One more rule from the docs: if you set a limit but no request, Kubernetes copies the limit into the request."
            ),
            "refs": [
                {"title": "Resource management for Pods and containers", "url": "https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/", "kind": "docs"},
                {"title": "Assign memory resources to containers and Pods", "url": "https://kubernetes.io/docs/tasks/configure-pod-container/assign-memory-resource/", "kind": "docs"},
                {"title": "Kubernetes requests and limits (Tech Tutorials with Piyush, CKA series)", "url": "https://www.youtube.com/watch?v=Q-mk6EZVX_Q", "kind": "watch"},
            ],
        },
        {
            "h": "QoS classes, LimitRanges and ResourceQuotas",
            "body": (
                "Your requests and limits also put each Pod into a quality of service (QoS) class. "
                "When a node runs short of memory, the kubelet evicts whole Pods to protect itself, and the class decides who goes first:\n"
                "- BestEffort: no requests or limits at all. Evicted first.\n"
                "- Burstable: at least one request or limit, but not Guaranteed. The lab's Pods are here.\n"
                "- Guaranteed: every container has CPU and memory requests equal to its limits. Evicted last.\n\n"
                "Eviction is different from an OOM kill. An OOM kill hits one container that broke its own limit. "
                "Eviction removes Pods because the node as a whole is short, and their Deployment recreates them on another node. "
                "Read a Pod's class with `kubectl get pod <name> -n hello -o jsonpath='{.status.qosClass}'`.\n\n"
                "In a shared cluster, admins add two guard rails per namespace:\n"
                "- A LimitRange sets default requests and limits for containers that set none, plus a minimum and maximum per container.\n"
                "- A ResourceQuota caps the total for the whole namespace, such as 4 CPUs of requests, 8Gi of memory or 20 Pods.\n\n"
                "With a quota on CPU or memory, the API server may reject any Pod that does not state those requests. "
                "A LimitRange with defaults fixes that for teams who forget. "
                "You will not need either on your laptop. You will meet both at work, often as an error message the first time you deploy to a new namespace."
            ),
            "refs": [
                {"title": "Pod quality of service classes", "url": "https://kubernetes.io/docs/concepts/workloads/pods/pod-qos/", "kind": "docs"},
                {"title": "Limit ranges", "url": "https://kubernetes.io/docs/concepts/policy/limit-range/", "kind": "docs"},
                {"title": "Resource quotas", "url": "https://kubernetes.io/docs/concepts/policy/resource-quotas/", "kind": "docs"},
            ],
        },
        {
            "h": "Scaling out with the HorizontalPodAutoscaler",
            "body": (
                "A HorizontalPodAutoscaler (HPA) changes the number of replicas of a Deployment for you. "
                "It is one more control loop, like the ones from Day 30. Every 15 seconds it does this:\n"
                "1. Reads the current CPU use of each Pod from the metrics API (more on that below).\n"
                "2. Turns it into a percentage of the Pod's CPU request, and averages it.\n"
                "3. Works out how many replicas would bring the average back to the target.\n"
                "4. Sets the Deployment's replica count, between `minReplicas` and `maxReplicas`.\n\n"
                "Step 3 is one line of math: `desired = ceil(currentReplicas * currentValue / targetValue)`. "
                "The lab's `k8s/hpa.yaml` targets 70% of the 100m request, so 70m per Pod. "
                "Say 3 Pods average 140m under load. That is twice the target, so the HPA asks for ceil(3 * 140 / 70) = 6 Pods. "
                "It ignores changes within 10% of the target, so the count does not jump around.\n\n"
                "It scales up at once, but scales down slowly on purpose. By default it wants 5 minutes of lower numbers before it removes Pods. "
                "The lab shortens that to 2 minutes with `behavior.scaleDown.stabilizationWindowSeconds: 120`, so you can watch it happen.\n\n"
                "The numbers come from metrics-server, a small add-on that asks each kubelet for CPU and memory use. kind does not ship it. "
                "After you install it, you add one flag, `--kubelet-insecure-tls`, because kind's kubelets use self-signed certificates. "
                "The [metrics-server README](https://github.com/kubernetes-sigs/metrics-server) says this flag is for testing only. "
                "Until metrics arrive, `kubectl get hpa` shows `cpu: <unknown>/70%`.\n\n"
                "Three more rules. Without a CPU request the HPA cannot compute a percentage, so it does nothing. "
                "The Deployment's `replicas` field fights the HPA on every `kubectl apply`. The HPA docs suggest removing it; the lab keeps it equal to `minReplicas`, so the two agree when the app is quiet. "
                "And scale to zero exists since Kubernetes 1.37 as a beta, but only for object or external metrics such as a queue length, never for CPU."
            ),
            "refs": [
                {"title": "Horizontal Pod autoscaling", "url": "https://kubernetes.io/docs/concepts/workloads/autoscaling/horizontal-pod-autoscale/", "kind": "docs"},
                {"title": "HorizontalPodAutoscaler walkthrough", "url": "https://kubernetes.io/docs/tasks/run-application/horizontal-pod-autoscale-walkthrough/", "kind": "docs"},
                {"title": "Kubernetes autoscaling explained: HPA vs VPA (Tech Tutorials with Piyush, CKA series)", "url": "https://www.youtube.com/watch?v=afUL5jGoLx0", "kind": "watch"},
            ],
        },
        {
            "h": "Scaling up: the VPA and in-place resize",
            "body": (
                "The HPA adds Pods. The other direction is to make each Pod bigger, which is called vertical scaling.\n\n"
                "The Vertical Pod Autoscaler (VPA) watches real CPU and memory use over time and recommends requests. "
                "It is an add-on: you install its CRDs and controllers yourself, and it reads the same metrics API as the HPA. "
                "Its `updateMode` decides how far it goes:\n"
                "- `Off`: only write recommendations. A safe way to learn what your app needs.\n"
                "- `Initial`: set requests when Pods are created, never later.\n"
                "- `Recreate`: evict Pods whose requests are far off, so they come back with new numbers.\n"
                "- `InPlaceOrRecreate` and `InPlace`: change running Pods without a restart when the node allows it.\n\n"
                "Do not let a VPA and an HPA both act on CPU for the same Deployment. "
                "The VPA raises the request, which lowers the HPA's percentage, and the two keep undoing each other's work.\n\n"
                "Those last two modes rest on in-place Pod resize, which became stable in Kubernetes 1.35. "
                "Before it, a Pod's resources were fixed for its whole life. "
                "Now you can patch the `resize` subresource of a running Pod with `kubectl patch pod <name> --subresource resize --patch '...'`. "
                "Each container's `resizePolicy` says whether a change needs a restart. The default, `NotRequired`, applies the new numbers to the running container.\n\n"
                "This works on single Pods. Changing the resources in a Deployment's template still rolls out new Pods, as on Day 32. "
                "Day to day you change the Deployment. In-place resize matters most for tools like the VPA, and for Pods that are slow or costly to restart."
            ),
            "refs": [
                {"title": "Vertical Pod autoscaling", "url": "https://kubernetes.io/docs/concepts/workloads/autoscaling/vertical-pod-autoscale/", "kind": "docs"},
                {"title": "Resize CPU and memory resources assigned to containers", "url": "https://kubernetes.io/docs/tasks/configure-pod-container/resize-container-resources/", "kind": "docs"},
            ],
        },
        {
            "h": "Where Pods land, and how many may leave",
            "body": (
                "The scheduler picks a node for each Pod from the nodes that fit its requests. You can steer that choice. From simple to strong:\n"
                "1. `nodeSelector`: run only on nodes with this label, such as `disktype: ssd`.\n"
                "2. Node affinity: the same idea with more operators. A `required` rule must match; a `preferred` rule is a wish the scheduler weighs.\n"
                "3. Pod affinity and anti-affinity: place Pods near or away from other Pods, by their labels. Anti-affinity on `kubernetes.io/hostname`, a label every node has, spreads replicas over nodes.\n"
                "4. Taints and tolerations: a taint on a node keeps Pods away, and a toleration on a Pod lets it in anyway.\n\n"
                "You already have a taint. kind's control-plane node carries `node-role.kubernetes.io/control-plane:NoSchedule`. "
                "That is why your app Pods only ever land on the two workers. "
                "`kubectl describe node devops-control-plane | grep Taints` shows it. The prod overlay on Day 37 uses anti-affinity, so one node failure is less likely to take every Pod.\n\n"
                "Last, the PodDisruptionBudget (PDB). Kubernetes splits disruptions into two kinds. "
                "Voluntary ones are planned, such as a `kubectl drain` before node maintenance, or a cluster upgrade. "
                "Involuntary ones just happen: a node crashes or loses power. A PDB limits only the voluntary kind.\n\n"
                "With `minAvailable: 2`, a drain evicts hello-devops Pods one at a time. Each eviction waits until enough replacements are ready elsewhere, so at least 2 keep serving. "
                "A PDB cannot stop a crash. Replicas spread over several nodes are your answer to that."
            ),
            "refs": [
                {"title": "Assigning Pods to nodes", "url": "https://kubernetes.io/docs/concepts/scheduling-eviction/assign-pod-node/", "kind": "docs"},
                {"title": "Taints and tolerations", "url": "https://kubernetes.io/docs/concepts/scheduling-eviction/taint-and-toleration/", "kind": "docs"},
                {"title": "Disruptions and PodDisruptionBudgets", "url": "https://kubernetes.io/docs/concepts/workloads/pods/disruptions/", "kind": "docs"},
            ],
        },
    ],
    "analogy": (
        "A shop manager checks a new clerk in three ways. On the first morning she gives them time to settle in before judging anything: that is the startup probe. "
        "Every few minutes she checks that they are awake at all, and if not, sends them home and calls someone new: liveness. "
        "And she checks whether they can serve customers right now; if their till is broken, she puts a closed sign on that counter but keeps the clerk: readiness. "
        "Where it breaks: the manager can ask why, while the kubelet only sees pass or fail from one URL."
    ),
    "diagram": diagram(),
    "diagram_caption": "Three probes, three different actions: wait, restart, or stop sending traffic.",
    "worked": {
        "title": "Cause an OOMKill and read the evidence",
        "steps": [
            {"say": "Start a Pod that grabs 150 MB of memory but may use only 100Mi. It runs Python from the hello-devops image, which your kind nodes already have, so nothing is downloaded.", "code": WORKED_POD, "lang": "console"},
            {"say": "Watch it. Within seconds the kernel kills it. Kubernetes restarts it, it dies again, and the waits between restarts grow: that is `CrashLoopBackOff`. Press Ctrl+C to stop watching.", "code": "$ kubectl get pod hog -n hello -w\nNAME   READY   STATUS              RESTARTS     AGE\nhog    0/1     ContainerCreating   0            1s\nhog    0/1     OOMKilled           0            3s\nhog    0/1     OOMKilled           1 (2s ago)   5s\nhog    0/1     CrashLoopBackOff    1 (3s ago)   6s", "lang": "console"},
            {"say": "`describe` keeps the reason of the last crash under Last State. `OOMKilled` with exit code 137 means the kernel sent SIGKILL because the container went over its memory limit.", "code": "$ kubectl describe pod hog -n hello | grep -A 3 \"Last State\"\n    Last State:     Terminated\n      Reason:       OOMKilled\n      Exit Code:    137\n      Started:      Fri, 30 Oct 2026 10:12:03 +0000", "lang": "console"},
            {"say": "The crashed container's log is empty. Python never reached its print line, and a process killed from outside gets no chance to write an error. An empty log plus exit code 137 points at memory, not at your code.", "code": "$ kubectl logs hog -n hello --previous\n$", "lang": "console"},
            {"say": "Look at what Kubernetes stored. You set only a memory limit, so it copied the limit into the memory request. With no CPU numbers at all, the Pod is Burstable, not Guaranteed.", "code": "$ kubectl get pod hog -n hello -o jsonpath='{.spec.containers[0].resources}{\"\\n\"}'\n{\"limits\":{\"memory\":\"100Mi\"},\"requests\":{\"memory\":\"100Mi\"}}\n$ kubectl get pod hog -n hello -o jsonpath='{.status.qosClass}{\"\\n\"}'\nBurstable", "lang": "console"},
            {"say": "Fix it. A bare Pod's resources only change through the resize subresource, so the simple path is delete and recreate. Run the command from step 1 again with `memory: 256Mi`. A Deployment would do this replace for you.", "code": "$ kubectl delete pod hog -n hello\npod \"hog\" deleted from hello namespace\n$ # run the command from step 1 again, with memory: 256Mi\n$ kubectl get pod hog -n hello\nNAME   READY   STATUS    RESTARTS   AGE\nhog    1/1     Running   0          8s\n$ kubectl logs hog -n hello\ngot 150 MB", "lang": "console"},
            {"say": "Clean up. In real work you would pick the new limit from measured use, with `kubectl top pod`.", "code": "$ kubectl delete pod hog -n hello\npod \"hog\" deleted from hello namespace", "lang": "console"},
        ],
    },
    "code_files": [
        ("yaml", "k8s/deployment.yaml", "kubectl apply -k k8s", "k8s/deployment.yaml (final version: Day 35 adds the probes and resources)"),
        ("yaml", "k8s/hpa.yaml", "kubectl apply -k k8s"),
        ("yaml", "k8s/kustomization.yaml", "kubectl apply -k k8s", "k8s/kustomization.yaml (Day 35 version: adds hpa.yaml)"),
    ],
    "commands": [
        {"cmd": "kubectl describe pod <pod-name> -n hello", "what": "Show a Pod's probes, resources, Last State and Events."},
        {"cmd": "kubectl get pod <pod-name> -n hello -o jsonpath='{.status.qosClass}'", "what": "Print a Pod's QoS class: Guaranteed, Burstable or BestEffort."},
        {"cmd": "kubectl scale deployment redis -n hello --replicas=0", "what": "Stop Redis, to watch the readiness probe take Pods out of the Service."},
        {"cmd": "kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml", "what": "Install the latest metrics-server, which the HPA and kubectl top need."},
        {"cmd": "kubectl patch deployment metrics-server -n kube-system --type=json -p '[{\"op\":\"add\",\"path\":\"/spec/template/spec/containers/0/args/-\",\"value\":\"--kubelet-insecure-tls\"}]'", "what": "On kind only: let metrics-server accept the kubelets' self-signed certificates."},
        {"cmd": "kubectl top pods -n hello", "what": "Show the current CPU and memory use of each Pod."},
        {"cmd": "kubectl top nodes", "what": "Show CPU and memory use per node."},
        {"cmd": "kubectl get hpa -n hello -w", "what": "Watch the autoscaler's current CPU, target and replica count."},
        {"cmd": "kubectl describe hpa hello-devops -n hello", "what": "Show the HPA's conditions and recent scaling events, to see why it did or did not scale."},
        {"cmd": "kubectl run load -n hello --image=busybox:1.37 --restart=Never -- /bin/sh -c \"while true; do wget -q -O- http://hello-devops > /dev/null; done\"", "what": "Start a Pod that sends requests in a loop, to give the HPA some CPU to react to."},
        {"cmd": "kubectl create poddisruptionbudget hello-pdb -n hello --selector=app=hello-devops --min-available=2", "what": "Create a PDB: planned work must leave at least 2 hello-devops Pods running."},
        {"cmd": "kubectl get pdb -n hello", "what": "List PDBs and how many disruptions each allows right now."},
        {"cmd": "kubectl drain devops-worker --ignore-daemonsets --delete-emptydir-data", "what": "Mark a node unschedulable and evict its Pods, respecting PDBs."},
        {"cmd": "kubectl uncordon devops-worker", "what": "Let the scheduler use the node again after a drain."},
        {"cmd": "kubectl describe node devops-control-plane | grep Taints", "what": "Show a node's taints, such as the control-plane NoSchedule taint."},
    ],
    "mistake": (
        "The liveness probe checks something outside the container, such as the database. "
        "When the database has a short problem, every Pod fails liveness at once and restarts, which turns a small outage into a full one. "
        "Keep liveness to \"is this process alive\" (`/healthz`) and put dependency checks in readiness (`/readyz`)."
    ),
    "real_world": (
        "At PayLite, a made-up payments company, each service's requests come from a week of real usage in monitoring, reviewed after every big release. "
        "An HPA adds checkout Pods as traffic climbs during sales, and a PDB lets node upgrades take down only one checkout Pod at a time. "
        "Probe changes go through code review like alert rules, because a bad liveness probe can restart every Pod at once."
    ),
    "task": {
        "title": "Probes, autoscaling and a safe drain on the lab app",
        "steps": [
            "Add the three probes and the resources to `k8s/deployment.yaml` (the file above) and apply with `kubectl apply -k k8s`. Work out from the timing settings how long each probe takes to act, and check the probes in `kubectl describe pod`.",
            "In a second terminal, run `kubectl get pods -n hello -w`. Scale Redis to 0 replicas and watch the hello-devops Pods go to `0/1` READY while RESTARTS stays at 0. Try `curl localhost:8081`.",
            "Scale Redis back to 1 and watch the app Pods become ready again on their own.",
            "Install metrics-server, add the `--kubelet-insecure-tls` flag, and wait until `kubectl top pods -n hello` prints numbers.",
            "Write `k8s/hpa.yaml`, add it to `k8s/kustomization.yaml`, and apply with `kubectl apply -k k8s`. Check that `kubectl get hpa -n hello` shows a real percentage instead of `<unknown>`.",
            "Start the load generator Pod from the commands list and watch `kubectl get hpa -n hello -w` until REPLICAS goes above 3. Delete the load Pod and watch the count return to 3 after about 2 quiet minutes.",
            "Create a PodDisruptionBudget for hello-devops with `minAvailable` 2 and read ALLOWED DISRUPTIONS in `kubectl get pdb -n hello`.",
            "Drain the node `devops-worker` while you watch the Pods move, then make it schedulable again with `kubectl uncordon`.",
            "Print the QoS class of one hello-devops Pod and of the Redis Pod, and explain each from their resources.",
        ],
        "hints": [
            "No scale-up? One load Pod may not be enough on a fast Mac. Start a second one with another name, and check `kubectl top pods -n hello`.",
            "The drain needs `--ignore-daemonsets` (kindnet and kube-proxy run on every node) and `--delete-emptydir-data` (metrics-server keeps scratch files in an emptyDir).",
            "HPA still `<unknown>`? Look at `kubectl logs -n kube-system deployment/metrics-server`. A missing `--kubelet-insecure-tls` flag shows up there as certificate errors.",
        ],
        "done_when": "`kubectl get hpa -n hello` showed more than 3 replicas under load, and `kubectl drain` moved the app Pods without ever leaving fewer than 2 ready.",
    },
    "explain_back": {
        "prompt": "Explain in 3 to 4 sentences why the hello-devops Pods went to 0/1 READY but did not restart when you scaled Redis to zero. Mention both probes and what each one checks.",
        "answer": (
            "The readiness probe calls `/readyz`, which pings Redis, so it started returning 503 and the Pods left the Service's endpoints. "
            "The liveness probe calls `/healthz`, which only checks that the process answers, so it kept passing and the kubelet had no reason to restart anything. "
            "When Redis came back, `/readyz` passed again and the Pods rejoined the Service without anyone touching them. "
            "If liveness had checked Redis, every Pod would have restarted for nothing."
        ),
    },
    "recap": [
        "Startup holds back the other probes, liveness restarts a stuck container, readiness only stops traffic.",
        "Keep dependencies out of liveness; a shared outage would restart every Pod at once.",
        "Requests decide placement; over the memory limit means OOMKilled (exit 137), at the CPU limit means throttling.",
        "Requests and limits set the QoS class, which decides eviction order when a node runs short.",
        "An HPA needs metrics-server (with `--kubelet-insecure-tls` on kind) and CPU requests; it scales up fast and down slowly.",
        "Taints, affinity and nodeSelector steer scheduling; a PDB limits planned disruptions such as a drain.",
    ],
    "check": [
        {
            "q": "A Spring Boot service needs about 90 seconds to start. Its liveness probe kills it after 30 seconds, again and again. What is the best fix?",
            "options": [
                "Add a startup probe that allows more than 90 seconds",
                "Raise the container's memory limit",
                "Point the readiness probe at `/healthz` too",
                "Add more replicas to the Deployment",
            ],
            "answer": 0,
            "why": "A startup probe holds the liveness probe back until the app has started, so slow starts are not mistaken for a stuck process.",
        },
        {
            "q": "metrics-server works and `kubectl top pods` prints numbers, but the HPA still shows `cpu: <unknown>/70%`. What is the most likely cause?",
            "options": [
                "The HPA needs a memory metric as well",
                "The cluster has too few worker nodes",
                "The Pods have no CPU request to compute a percentage from",
                "The Deployment's `replicas` is set higher than `maxReplicas`",
            ],
            "answer": 2,
            "why": "A utilization target is a percentage of the CPU request, so without a request the HPA has nothing to divide by.",
        },
        {
            "q": "A Deployment has 3 replicas and a PDB with `minAvailable: 3`. You run `kubectl drain` on the node that holds one of them. What happens?",
            "options": [
                "The Pod is evicted at once, and the PDB is ignored for drains",
                "The node is deleted and the Pod moves with it",
                "Kubernetes adds a fourth replica first, then evicts",
                "The eviction is refused and drain keeps retrying",
            ],
            "answer": 3,
            "why": "With all 3 required, the budget allows 0 disruptions, so every eviction is refused until you change the PDB or add replicas.",
        },
    ],
    "interview": [
        {
            "q": "What is the difference between liveness, readiness and startup probes?",
            "a": (
                "A liveness probe checks whether the container is stuck; after repeated failures the kubelet restarts it. "
                "A readiness probe checks whether the Pod can take traffic; while it fails, the Pod is removed from Service endpoints but keeps running. "
                "A startup probe protects slow starters by holding the other two back until it passes. "
                "Liveness should test only the process itself, while readiness may check dependencies such as a database."
            ),
        },
        {
            "q": "How do requests and limits work, and what happens when a container goes over them?",
            "a": (
                "Requests are what the scheduler reserves, so they decide which node a Pod can go on, and the HPA computes percentages from them. "
                "Limits are the most a container may use, enforced by the kernel through cgroups. "
                "Over the memory limit the container is OOMKilled with exit code 137; at the CPU limit it is only throttled. "
                "I always set requests and a memory limit, and think twice before adding a CPU limit to a latency-sensitive service."
            ),
        },
        {
            "q": "An HPA is not scaling. How do you find out why?",
            "a": (
                "First `kubectl get hpa` to see the current value: `<unknown>` means no metrics, so check that metrics-server runs and that the Pods have CPU requests. "
                "Then `kubectl describe hpa` shows conditions such as AbleToScale and ScalingActive, plus events that explain each decision. "
                "If metrics look fine, check whether the count is already at `maxReplicas`, or whether the target is so high that the load never crosses it. "
                "Last, look for a second controller, such as a VPA on CPU or a deploy tool resetting `replicas`."
            ),
        },
    ],
    "deeper": {
        "minutes": 12,
        "body": (
            "Picking good numbers is most of the work with resources, and guessing goes wrong in both directions. "
            "Requests that are too high waste nodes and make the HPA react late, because each Pod looks idle. "
            "Requests that are too low pack too many Pods onto a node and make the HPA scale early and often.\n\n"
            "A simple way to start from data:\n"
            "1. Run the app under normal load for a day and look at its use with `kubectl top pods`, or a Grafana dashboard once you reach Part 10.\n"
            "2. Set the memory request near normal use and the memory limit with room for peaks, often about twice the request.\n"
            "3. Set the CPU request near normal use. The HPA's percentage is based on it, so this number also sets when scaling starts.\n"
            "4. Run a VPA in `Off` mode next to the app. Its recommendations are a second opinion that costs nothing.\n"
            "5. Check again after big changes to the app, such as a new framework version or a new cache.\n\n"
            "CPU is not always the right signal to scale on. A worker that reads jobs from a queue may sit at low CPU while thousands of jobs wait. "
            "KEDA, a CNCF project, scales Deployments on events such as queue length, and can scale to zero when there is no work. "
            "Kubernetes 1.37 also lets an HPA scale to zero by itself as a beta, when it uses an object or external metric.\n\n"
            "All of this scales Pods. When the nodes are full, new Pods stay `Pending`. "
            "Node autoscalers, such as the Cluster Autoscaler or Karpenter on a cloud, notice those Pending Pods and add nodes. "
            "When nodes are under-used, they drain and remove them, and that drain respects your PDBs. "
            "A kind cluster cannot add nodes, so on your laptop the ceiling is the memory you gave Docker Desktop.\n\n"
            "Probes deserve the same care as numbers. Tune them like alerts: a probe acts on its own, often when nobody is watching. "
            "Before you tighten a timeout, ask what happens if every Pod fails that probe in the same minute."
        ),
    },
    "sources": [
        {"title": "Liveness, readiness and startup probes", "url": "https://kubernetes.io/docs/concepts/workloads/pods/probes/"},
        {"title": "Resource management for Pods and containers", "url": "https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/"},
        {"title": "Horizontal Pod autoscaling", "url": "https://kubernetes.io/docs/concepts/workloads/autoscaling/horizontal-pod-autoscale/"},
        {"title": "metrics-server (GitHub)", "url": "https://github.com/kubernetes-sigs/metrics-server"},
    ],
}
