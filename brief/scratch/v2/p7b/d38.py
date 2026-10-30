"""Day 38: Troubleshooting Kubernetes."""
from svg import arrow, box, cap, svg


def diagram():
    h = 44
    p = [
        box(16, 40, 140, h, "bxt", "1. Pod"),
        box(210, 40, 140, h, "bxg", "2. Service"),
        box(404, 40, 140, h, "bxp", "3. Route"),
        arrow(156, 62, 208, 62), arrow(350, 62, 402, 62),
        cap(86, 24, "start here"),
        cap(86, 104, "get, describe"), cap(86, 118, "logs --previous"),
        cap(280, 104, "endpointslices"), cap(280, 118, "selector, targetPort"),
        cap(474, 104, "httproute status"), cap(474, 118, "port-forward test"),
        box(210, 150, 140, h, "bxo", "4. Node"),
        arrow(140, 84, 226, 148, dashed=True),
        cap(280, 214, "describe node"), cap(280, 228, "top nodes"),
    ]
    return svg(242, "Debug bottom-up: first the Pod, then the Service, then the route, and the node when many Pods fail together", p)


BREAK = """$ kubectl patch configmap hello-config -n hello --type merge -p '{"data":{"REDIS_HOST":"rediss"}}'
configmap/hello-config patched
$ kubectl rollout restart deployment/hello-devops -n hello
deployment.apps/hello-devops restarted"""

STUCK = """$ kubectl rollout status deployment/hello-devops -n hello --timeout=60s
Waiting for deployment "hello-devops" rollout to finish: 1 out of 3 new replicas have been updated...
error: timed out waiting for the condition
$ kubectl get pods -n hello -l app=hello-devops
NAME                            READY   STATUS    RESTARTS   AGE
hello-devops-5d8f7c6b9-4kq2w    0/1     Running   0          75s
hello-devops-6c9f8b7d4-2qkzt    1/1     Running   0          2d
hello-devops-6c9f8b7d4-8hx7m    1/1     Running   0          2d
hello-devops-6c9f8b7d4-tr5vn    1/1     Running   0          2d"""

EVENTS = """$ kubectl events -n hello --for pod/hello-devops-5d8f7c6b9-4kq2w --types=Warning
LAST SEEN           TYPE      REASON      OBJECT                             MESSAGE
3s (x14 over 68s)   Warning   Unhealthy   Pod/hello-devops-5d8f7c6b9-4kq2w   Readiness probe failed: HTTP probe failed with statuscode: 503
$ kubectl get pods -n hello -l app=redis
NAME                     READY   STATUS    RESTARTS   AGE
redis-7c6d9f5b8d-q2l8v   1/1     Running   0          2d"""

ENV = """$ kubectl exec hello-devops-5d8f7c6b9-4kq2w -n hello -- printenv REDIS_HOST
rediss
$ kubectl exec hello-devops-5d8f7c6b9-4kq2w -n hello -- nslookup rediss
error: Internal error occurred: ... OCI runtime exec failed: exec failed: unable to start container process: exec: "nslookup": executable file not found in $PATH: unknown"""

DEBUG = """$ kubectl debug -it hello-devops-5d8f7c6b9-4kq2w -n hello --image=busybox:1.37 --target=web
Targeting container "web". If you don't see processes from this container it may be because the container runtime doesn't support this feature.
Defaulting debug container name to debugger-qz8vt.
All commands and output from this session will be recorded in container logs, including credentials and sensitive information passed through the command prompt.
If you don't see a command prompt, try pressing enter.
/ # nslookup rediss.hello.svc.cluster.local
Server:		10.96.0.10
Address:	10.96.0.10:53

** server can't find rediss.hello.svc.cluster.local: NXDOMAIN

** server can't find rediss.hello.svc.cluster.local: NXDOMAIN
"""

DEBUG2 = """/ # nslookup redis.hello.svc.cluster.local
Server:		10.96.0.10
Address:	10.96.0.10:53

Name:	redis.hello.svc.cluster.local
Address: 10.96.84.21

/ # exit"""

FIX = """$ kubectl patch configmap hello-config -n hello --type merge -p '{"data":{"REDIS_HOST":"redis"}}'
configmap/hello-config patched
$ kubectl rollout restart deployment/hello-devops -n hello
deployment.apps/hello-devops restarted
$ kubectl rollout status deployment/hello-devops -n hello
deployment "hello-devops" successfully rolled out"""

LESSON = {
    "id": "d38",
    "title": "Troubleshooting Kubernetes",
    "minutes": 50,
    "goal": "By the end you can find out why a workload is broken with a fixed order of kubectl commands, read the common failure states, test from inside Pods that have no tools, and tell an RBAC \"forbidden\" from a bug.",
    "guess": {
        "q": "A Pod is in CrashLoopBackOff, and `kubectl logs` on it shows nothing useful. Where is the error message most likely to be?",
        "options": [
            "Nowhere: a crashing app never writes its error",
            "In the previous container's log: `kubectl logs --previous`",
            "Only in etcd, which kubectl cannot read",
            "In the node's disk, which you must open with SSH",
        ],
        "answer": 1,
        "why": "After a restart, `kubectl logs` shows the new container, which may have printed nothing yet. `--previous` shows the container that crashed, error and all.",
    },
    "terms": [
        {"term": "Event", "plain": "A short record that a Kubernetes part wrote about an object, such as a failed probe; kept about an hour."},
        {"term": "CrashLoopBackOff", "plain": "A container keeps exiting, and Kubernetes waits longer before each restart, up to 5 minutes."},
        {"term": "ImagePullBackOff", "plain": "The node failed to get the image and now waits longer between tries."},
        {"term": "CreateContainerConfigError", "plain": "The image is there, but the container's settings cannot be built, usually a missing ConfigMap or Secret."},
        {"term": "Ephemeral container", "plain": "A temporary extra container that kubectl debug adds to a running Pod for checks."},
        {"term": "RBAC", "plain": "Role-based access control: rules that say who may do which actions on which objects."},
        {"term": "Role and RoleBinding", "plain": "A Role lists allowed actions in one namespace; a RoleBinding gives that Role to someone."},
        {"term": "ServiceAccount", "plain": "An identity for a program, such as a CI job or a Pod that calls the Kubernetes API."},
    ],
    "sections": [
        {
            "h": "A method beats guessing",
            "body": (
                "When something breaks, the urge is to change three things and hope. Kubernetes punishes that. "
                "Many parts react on their own, so a guess can change the evidence before you have read it. "
                "A fixed order of checks is faster, even when you think you already know the answer.\n\n"
                "Work from the bottom up, because each layer depends on the one below it:\n"
                "1. The Pod: is it scheduled, running, ready, restarting?\n"
                "2. The Service: does it select those Pods, and does its `targetPort` match the port the app listens on?\n"
                "3. The route: does the Gateway or Ingress send traffic to that Service?\n"
                "4. The node: if many Pods fail together, is one node short of memory or not ready?\n\n"
                "For each layer, the commands are nearly always the same:\n"
                "1. `kubectl get` for STATUS, READY and RESTARTS.\n"
                "2. `kubectl describe`, reading the Events at the bottom first.\n"
                "3. `kubectl logs`, with `--previous` if the container restarted.\n"
                "4. `kubectl get events` for the whole namespace, sorted by time.\n"
                "5. `kubectl exec`, `port-forward` or `debug` to test from inside.\n\n"
                "Two habits help more than any tool. Change one thing at a time, then watch what happens. "
                "And test layers one by one: `kubectl port-forward pod/<pod>` skips the Service, so if the Pod answers there and not through the Service, you know which layer to read."
            ),
            "refs": [
                {"title": "A visual guide on troubleshooting Kubernetes deployments (Learnkube)", "url": "https://learnkube.com/troubleshooting-deployments", "kind": "read"},
                {"title": "Debug Pods", "url": "https://kubernetes.io/docs/tasks/debug/debug-application/debug-pods/", "kind": "docs"},
                {"title": "Troubleshooting Pods in CrashLoopBackOff, Pending and ImagePullBackOff", "url": "https://www.youtube.com/watch?v=ULitVDnqy8Y", "kind": "watch"},
            ],
        },
        {
            "h": "Pods that never start",
            "body": (
                "In these four states the container has not run yet, so `kubectl logs` has nothing to show. "
                "The answer is in `kubectl describe pod`, under Events:\n"
                "- `Pending`: no node will take the Pod. Usual causes: requests larger than any node's free room, a PVC that cannot bind, or a nodeSelector, affinity or taint that rules out every node.\n"
                "- `ContainerCreating` for more than a minute: the node is still setting the Pod up. Usually a volume that will not mount, or a large image still downloading.\n"
                "- `ErrImagePull`, then `ImagePullBackOff`: the node cannot get the image. Check the name and tag, the registry login for private images, and on kind whether you ran `kind load docker-image`.\n"
                "- `CreateContainerConfigError`: the image is there, but the kubelet cannot build the container's settings. Almost always a missing ConfigMap or Secret, or a missing key in one.\n\n"
                "\"BackOff\" in a status only means the kubelet now waits longer between tries. It is never the cause. Look for the first error in the Events.\n\n"
                "For `Pending`, the scheduler writes a `FailedScheduling` event, and it pays to read it slowly. "
                "A message that starts `0/3 nodes are available: 1 node(s) had untolerated taint(s), 2 Insufficient cpu` counts all three nodes. "
                "One is ruled out by a taint (kind's control plane, Day 35), and two lack free CPU for the request. "
                "Lower the request, remove other workloads, or add a node."
            ),
            "refs": [
                {"title": "Debug Pods", "url": "https://kubernetes.io/docs/tasks/debug/debug-application/debug-pods/", "kind": "docs"},
                {"title": "Images: pull policy and errors", "url": "https://kubernetes.io/docs/concepts/containers/images/", "kind": "docs"},
            ],
        },
        {
            "h": "Pods that start, then fail",
            "body": (
                "Here the container ran at least once, so there is evidence in its logs and in its last state:\n"
                "- `CrashLoopBackOff`: the container keeps exiting, and the kubelet waits longer before each restart: 10 seconds, then 20, 40, up to 5 minutes. It is a symptom. Read `kubectl logs --previous` for the app's own error, then `Last State` in describe.\n"
                "- `OOMKilled`: `Last State` shows `Reason: OOMKilled` and `Exit Code: 137`. The container went over its memory limit (Day 35).\n"
                "- Restarts with clean logs: often a liveness probe that fails. The Events say `Liveness probe failed` and then that the container will be restarted. The app was fine; the check was wrong.\n"
                "- `Running` but `0/1` READY: the readiness probe fails, so the Pod gets no traffic. The Events show `Readiness probe failed` with a status code or an error.\n"
                "- All Pods ready, but the Service still fails: the Service matches no Pods. `kubectl get endpointslices -l kubernetes.io/service-name=<svc>` shows `<unset>` under ENDPOINTS.\n\n"
                "For that last case, compare the Service's selector (`kubectl describe service`) with the Pods' labels (`kubectl get pods --show-labels`), and check that `targetPort` is the port the app listens on. "
                "This one fools people, because every Pod looks healthy.\n\n"
                "Remember that the STATUS column is a summary kubectl writes for you. `CrashLoopBackOff` is not a Pod phase; the phase is still `Running`. "
                "When the column confuses you, `kubectl get pod <name> -o yaml` shows the real fields under `status`."
            ),
            "refs": [
                {"title": "Pod lifecycle", "url": "https://kubernetes.io/docs/concepts/workloads/pods/pod-lifecycle/", "kind": "docs"},
                {"title": "Debug Services", "url": "https://kubernetes.io/docs/tasks/debug/debug-application/debug-service/", "kind": "docs"},
            ],
        },
        {
            "h": "Events, logs and exit codes",
            "body": (
                "**Events** are short records that Kubernetes parts write about objects: the scheduler placed a Pod, the kubelet pulled an image, a probe failed. "
                "The API server keeps them for about an hour by default, so read them early.\n\n"
                "Three ways to read them:\n"
                "- `kubectl describe pod <name>` shows one object's events at the bottom.\n"
                "- `kubectl get events -n <ns> --sort-by=.metadata.creationTimestamp` lists the namespace's events, oldest first.\n"
                "- `kubectl events -n <ns> --for pod/<name>` is the newer command. It sorts by time on its own, and `--types=Warning` hides the routine ones.\n\n"
                "Logs are what the container wrote to standard output and standard error. `kubectl logs <pod>` reads the current container. "
                "Right after a crash, that is a fresh container that may not have printed anything yet. `--previous` reads the one before, the one that crashed. "
                "Add `-c <container>` when a Pod has more than one container, and `-f` to follow new lines.\n\n"
                "The exit code under `Last State` narrows things down fast:\n"
                "- 0: the process finished on purpose. In a Deployment that still counts as a restart, because a web app should never finish.\n"
                "- 1, or another small number: the app exited with its own error. Read the logs.\n"
                "- 137: killed with SIGKILL (128 + 9). Most often the OOM killer, or an app that ignored the stop signal until its grace period ran out.\n"
                "- 143: stopped with SIGTERM (128 + 15), the polite stop signal Kubernetes sends first."
            ),
            "refs": [
                {"title": "Determine the reason for Pod failure", "url": "https://kubernetes.io/docs/tasks/debug/debug-application/determine-reason-pod-failure/", "kind": "docs"},
                {"title": "Debug running Pods", "url": "https://kubernetes.io/docs/tasks/debug/debug-application/debug-running-pod/", "kind": "docs"},
            ],
        },
        {
            "h": "Looking inside: exec, port-forward and kubectl debug",
            "body": (
                "Sometimes you need to test from inside the cluster. Can this Pod resolve a name, reach a port, see a file?\n\n"
                "`kubectl exec -it <pod> -- sh` opens a shell in a running container. It only works if the image has a shell and the tools you need, and small images often do not. "
                "hello-devops has `sh` and Python, but no `nslookup`, `curl` or `wget`. Distroless images have no shell at all.\n\n"
                "That is what `kubectl debug` is for. It adds an **ephemeral container** to a running Pod: a temporary extra container with an image you choose, such as `busybox`, or `nicolaka/netshoot`, a large image full of network tools. "
                "It shares the Pod's network, so it sees DNS and ports exactly as the app does. With `--target=web` it also sees the processes of the `web` container. "
                "Ephemeral containers are never restarted, and they go away when the Pod is deleted. Two more forms:\n"
                "- `kubectl debug <pod> -it --copy-to=<pod>-debug --container=web -- sh` makes a copy of the Pod with a shell, for a container that crashes too fast to inspect.\n"
                "- `kubectl debug node/<node> -it --image=ubuntu` starts a Pod on that node with the node's files mounted at `/host`.\n\n"
                "For DNS and network checks you often do not need the broken Pod at all. A throwaway Pod is enough: "
                "`kubectl run net-test -n hello --rm -it --image=busybox:1.37 --restart=Never -- nslookup redis.hello.svc.cluster.local`. "
                "NXDOMAIN means the name is wrong or the Service does not exist. If the name resolves but connections fail, check the Service's endpoints next."
            ),
            "refs": [
                {"title": "Debug running Pods (kubectl debug)", "url": "https://kubernetes.io/docs/tasks/debug/debug-application/debug-running-pod/", "kind": "docs"},
                {"title": "Debugging DNS resolution", "url": "https://kubernetes.io/docs/tasks/administer-cluster/dns-debugging-resolution/", "kind": "docs"},
                {"title": "Debugging with ephemeral containers (DevOpsDays Seattle 2022 talk)", "url": "https://www.youtube.com/watch?v=xE_nlt8Lyk4", "kind": "watch"},
            ],
        },
        {
            "h": "Forbidden: RBAC basics",
            "body": (
                "Sooner or later you will see `Error from server (Forbidden)`. That is not a bug in your YAML. "
                "The API server understood the request and refused it, because the person or program behind it lacks permission.\n\n"
                "Kubernetes decides with role-based access control (RBAC), and four kinds of object do the work:\n"
                "- A Role lists allowed actions in one namespace, such as `get`, `list` and `watch` on `pods`. A ClusterRole does the same for the whole cluster.\n"
                "- A RoleBinding gives a Role to subjects in one namespace. A ClusterRoleBinding gives a ClusterRole everywhere.\n"
                "- Subjects are users, groups and ServiceAccounts. A ServiceAccount is an identity for a program, such as a CI job or a Pod that calls the API.\n\n"
                "Permissions only add up. There are no deny rules, so \"forbidden\" always means that nothing allowed the action.\n\n"
                "The error tells you exactly what was missing, for example: `User \"system:serviceaccount:hello:viewer\" cannot delete resource \"pods\" in API group \"\" in the namespace \"hello\"`. "
                "Read it as subject, verb, resource, API group and namespace. Then ask the cluster directly:\n"
                "- `kubectl auth can-i delete pods -n hello` answers yes or no for you.\n"
                "- Add `--as=system:serviceaccount:hello:viewer` to ask on behalf of someone else. Your kind admin user is allowed to do that.\n\n"
                "Fix it with the smallest Role that does the job. Binding a robot to `cluster-admin` makes the error go away, and also opens the whole cluster to that robot."
            ),
            "refs": [
                {"title": "Using RBAC authorization", "url": "https://kubernetes.io/docs/reference/access-authn-authz/rbac/", "kind": "docs"},
                {"title": "Configure service accounts for Pods", "url": "https://kubernetes.io/docs/tasks/configure-pod-container/configure-service-account/", "kind": "docs"},
            ],
        },
        {
            "h": "Faster tools, and when the node is the problem",
            "body": (
                "A few tools save time once the method is in your head:\n"
                "- `kubectl top pods` and `kubectl top nodes` show live CPU and memory use, from the metrics-server you installed on Day 35. Check them before you raise a limit.\n"
                "- k9s is a terminal UI over the same API. You move between Pods, logs, events and describe output with a few keys. Install it with `brew install derailed/k9s/k9s` and run `k9s -n debug-lab`.\n"
                "- Headlamp is a graphical alternative. The old Kubernetes Dashboard project has been archived, and the [Kubernetes blog](https://kubernetes.io/blog/2026/06/01/dashboard-to-headlamp/) points to Headlamp instead.\n\n"
                "Learn the plain kubectl commands first anyway. k9s is not installed on every machine you will log in to; kubectl is.\n\n"
                "If many Pods fail at once, and all on one node, look at the node. "
                "`kubectl get nodes` shows `NotReady` when a kubelet stops reporting. "
                "`kubectl describe node <name>` shows conditions such as `MemoryPressure` and `DiskPressure`, and lists the Pods on the node with their requests. "
                "On kind, a node is a Docker container, so `docker stats` on your Mac shows whether Docker Desktop itself is short of memory, and Docker Desktop's settings let you give it more."
            ),
            "refs": [
                {"title": "k9s (GitHub)", "url": "https://github.com/derailed/k9s", "kind": "docs"},
                {"title": "From Kubernetes Dashboard to Headlamp (Kubernetes blog)", "url": "https://kubernetes.io/blog/2026/06/01/dashboard-to-headlamp/", "kind": "read"},
            ],
        },
    ],
    "analogy": (
        "A good mechanic with a car that will not start does not swap parts at random. "
        "They check in a fixed order: is there fuel, does the engine turn, does it keep running, do the wheels get power. Each answer rules out a whole layer. "
        "kubectl get, describe, logs and events are that checklist for a cluster. "
        "Where it breaks: a car waits for the mechanic, while Kubernetes keeps restarting things as you look, so read the Events and `--previous` logs before they change."
    ),
    "diagram": diagram(),
    "diagram_caption": "Debug in the order traffic depends on: Pod first, then Service, then route; check the node when failures cluster.",
    "worked": {
        "title": "A stuck rollout and a DNS name with a typo",
        "steps": [
            {"say": "Set this up on purpose: change `REDIS_HOST` in the lab's ConfigMap to `rediss`, one letter too many, and restart the Deployment so new Pods read it. This is a typical real mistake.", "code": BREAK, "lang": "console"},
            {"say": "The symptom: the rollout never finishes. One new Pod is Running but not ready. The three old Pods keep serving, because the Deployment uses `maxUnavailable: 0` and readiness gates the rollout. Users see nothing wrong yet.", "code": STUCK, "lang": "console"},
            {"say": "Ask the new Pod's events. Readiness fails with 503, and the app returns 503 from `/readyz` when it cannot reach Redis. Yet Redis itself is Running and ready, so the problem is between the two.", "code": EVENTS, "lang": "console"},
            {"say": "Check what the new Pod was given. The value looks almost right. You want to test the name from inside the Pod's network, but the app image has no DNS tools.", "code": ENV, "lang": "console"},
            {"say": "Add an ephemeral busybox container to the same Pod. It shares the Pod's network, so its DNS answers are the app's DNS answers. The name `rediss` does not exist.", "code": DEBUG, "lang": "console"},
            {"say": "The correct name resolves to the Redis Service's IP. Hypothesis confirmed: a typo in the ConfigMap, not a broken Redis and not a network problem.", "code": DEBUG2, "lang": "console"},
            {"say": "Fix the value and roll again. In a real team you would fix it in git, not with `kubectl patch`; on Day 39 Argo CD makes that the only path.", "code": FIX, "lang": "console"},
        ],
    },
    "code_files": [
        ("text", "k8s-broken/README.md", "kubectl apply -f k8s-broken/"),
        ("yaml", "k8s-broken/00-namespace.yaml", "kubectl apply -f k8s-broken/"),
        ("yaml", "k8s-broken/01-catalog.yaml", "kubectl apply -f k8s-broken/"),
        ("yaml", "k8s-broken/02-checkout.yaml", "kubectl apply -f k8s-broken/"),
        ("yaml", "k8s-broken/03-search.yaml", "kubectl apply -f k8s-broken/"),
        ("yaml", "k8s-broken/04-reports.yaml", "kubectl apply -f k8s-broken/"),
        ("yaml", "k8s-broken/05-profile.yaml", "kubectl apply -f k8s-broken/"),
    ],
    "commands": [
        {"cmd": "kubectl get pods -n debug-lab -o wide", "what": "Show STATUS, READY, RESTARTS and the node of each Pod."},
        {"cmd": "kubectl describe pod <pod> -n debug-lab", "what": "Show a Pod's settings, Last State and Events; read the Events first."},
        {"cmd": "kubectl logs <pod> -n debug-lab --previous", "what": "Show what the crashed container printed before it died."},
        {"cmd": "kubectl get events -n debug-lab --sort-by=.metadata.creationTimestamp", "what": "List the namespace's events, oldest first."},
        {"cmd": "kubectl events -n debug-lab --for pod/<pod> --types=Warning", "what": "Show only the warnings for one Pod, sorted by time."},
        {"cmd": "kubectl get endpointslices -n debug-lab -l kubernetes.io/service-name=search", "what": "Show which Pod IPs a Service sends traffic to; `<unset>` means none."},
        {"cmd": "kubectl get pods -n debug-lab --show-labels", "what": "Show each Pod's labels, to compare with a Service's selector."},
        {"cmd": "kubectl port-forward pod/<pod> 8095:8000 -n debug-lab", "what": "Reach one Pod directly, skipping the Service."},
        {"cmd": "kubectl exec -it <pod> -n debug-lab -- sh", "what": "Open a shell in a running container, if its image has one."},
        {"cmd": "kubectl debug -it <pod> -n debug-lab --image=busybox:1.37 --target=web", "what": "Add an ephemeral busybox container to a running Pod for checks."},
        {"cmd": "kubectl run net-test -n debug-lab --rm -it --image=busybox:1.37 --restart=Never -- wget -qO- -T 3 http://search", "what": "Call a Service from a throwaway Pod inside the cluster."},
        {"cmd": "kubectl run tmp-shell --rm -it --image=nicolaka/netshoot", "what": "Start a throwaway Pod with many network tools (dig, curl, tcpdump)."},
        {"cmd": "kubectl auth can-i delete pods -n debug-lab --as=system:serviceaccount:debug-lab:viewer", "what": "Ask whether a ServiceAccount may do something; prints yes or no."},
        {"cmd": "kubectl create role pod-reader -n debug-lab --verb=get,list,watch --resource=pods", "what": "Create a Role that may only read Pods in one namespace."},
        {"cmd": "kubectl create rolebinding viewer-reads-pods -n debug-lab --role=pod-reader --serviceaccount=debug-lab:viewer", "what": "Give that Role to the ServiceAccount viewer."},
        {"cmd": "brew install derailed/k9s/k9s", "what": "Install k9s, a terminal UI for Kubernetes."},
    ],
    "mistake": (
        "Deleting or restarting the broken Pod first, to see if it helps. "
        "A new Pod wipes the evidence you needed: the crashed container's logs, its Last State and often the newest Events. "
        "Run describe and `logs --previous` before you delete anything, and write down what you saw."
    ),
    "real_world": (
        "PayLite's on-call runbook starts with the same ladder: get, describe, logs `--previous`, events, endpoints. "
        "Most engineers have read-only RBAC in production, and the images are distroless, so `kubectl debug` with an ephemeral container is the normal way to look inside. "
        "Fixes go through git and Argo CD; a `kubectl patch` in production is only for emergencies and is written up afterwards."
    ),
    "task": {
        "title": "Break-and-fix: five broken services",
        "steps": [
            "Check that `hello-devops:1.0.0` is loaded into kind and metrics-server is running. Copy the `k8s-broken/` folder into your repo.",
            "Apply the whole folder with `kubectl apply -f k8s-broken/` and watch `kubectl get pods -n debug-lab -w` for two minutes. Note each Pod's STATUS and RESTARTS.",
            "For each of the five services, follow the method from the README: get, describe with the Events first, `logs --previous`, events. Write one sentence per service: the cause, and the line of output that proves it.",
            "For search, show that the Service has no endpoints, and compare its selector with the Pods' labels.",
            "For reports, use `kubectl top pods` on a healthy hello-devops Pod to choose a sensible memory limit.",
            "Fix one file at a time, apply it, and wait until that Pod is healthy before you move to the next.",
            "Prove that search works with the `net-test` busybox command from the README.",
            "RBAC: create a ServiceAccount `viewer` in `debug-lab`, a Role that may only get, list and watch Pods, and a RoleBinding. Check with `kubectl auth can-i` that it may list Pods but not delete them, then trigger the Forbidden error with `--as`.",
            "Compare your notes with `SOLUTIONS.md` in the lab folder, then delete the `debug-lab` namespace.",
        ],
        "hints": [
            "If `kubectl logs` shows nothing, ask whether the container ever started. If it never did, the answer is in the Events.",
            "`kubectl get pod <pod> -n debug-lab -o jsonpath='{.status.containerStatuses[0].lastState}'` prints the last crash on one line.",
            "For RBAC you need three commands: `kubectl create serviceaccount`, `kubectl create role` and `kubectl create rolebinding`. The commands list has the last two.",
        ],
        "done_when": "All five Pods in `debug-lab` are Running and 1/1 Ready with no new restarts, `net-test` gets JSON from search, and `kubectl auth can-i delete pods -n debug-lab --as=system:serviceaccount:debug-lab:viewer` says no.",
    },
    "explain_back": {
        "prompt": "Explain in 3 to 4 sentences how you would find out why a Pod is in CrashLoopBackOff. Mention which commands you run, in which order, and what each one can tell you.",
        "answer": (
            "First `kubectl get pods` to see the status and how many restarts there have been. "
            "Then `kubectl describe pod` and read the Events and `Last State`: the exit code tells me whether it was the app's own error, an OOM kill (137) or a failed liveness probe. "
            "Then `kubectl logs --previous`, because the current container may have printed nothing yet, while the crashed one has the error. "
            "If that is still not enough, I compare the config the Pod got, such as env vars, ConfigMaps and probes, with what the app expects."
        ),
    },
    "recap": [
        "Debug bottom-up: Pod, then Service, then route, then node. Change one thing at a time.",
        "Pending, ContainerCreating, ImagePullBackOff and CreateContainerConfigError: no logs yet, read the Events.",
        "CrashLoopBackOff is a symptom; `logs --previous` and the exit code in Last State show the cause.",
        "Healthy Pods but a failing Service usually means a selector or targetPort mismatch: check EndpointSlices.",
        "`kubectl debug` adds an ephemeral container with tools; a throwaway busybox Pod checks DNS.",
        "Forbidden is RBAC, not a bug: read the message, ask `kubectl auth can-i`, grant the smallest Role.",
    ],
    "check": [
        {
            "q": "A new Pod stays Pending. Its event says `0/3 nodes are available: 1 node(s) had untolerated taint(s), 2 Insufficient memory`. What is the most likely fix?",
            "options": [
                "Raise the Pod's memory limit",
                "Remove the taint from every node",
                "Lower the Pod's memory request, or free up room on the workers",
                "Add a readiness probe so the scheduler can test it",
            ],
            "answer": 2,
            "why": "The two workers lack free memory for the request, and scheduling uses requests, so the request must shrink or room must appear.",
        },
        {
            "q": "A Pod shows `CreateContainerConfigError` and `kubectl logs` prints nothing. Why are the logs empty?",
            "options": [
                "The container never started, so there is nothing to log; the Events explain why",
                "The logs were deleted when the Pod restarted",
                "The app writes logs to a file instead of standard output",
                "kubectl needs `--previous` for every Pod with an error",
            ],
            "answer": 0,
            "why": "The kubelet could not build the container's settings, usually because a ConfigMap or Secret is missing, so no process ever ran.",
        },
        {
            "q": "A CI job's ServiceAccount `deployer` in namespace `ci` gets Forbidden when it applies a Deployment to namespace `shop`. Which command checks the permission directly?",
            "options": [
                "`kubectl describe deployment -n shop`",
                "`kubectl get events -n ci`",
                "`kubectl logs -n ci deployer`",
                "`kubectl auth can-i create deployments -n shop --as=system:serviceaccount:ci:deployer`",
            ],
            "answer": 3,
            "why": "`auth can-i` with `--as` asks the API server whether that exact subject may do that exact action in that namespace.",
        },
    ],
    "interview": [
        {
            "q": "A Pod is in CrashLoopBackOff. Walk me through how you debug it.",
            "a": (
                "I start with `kubectl get pods` for the restart count, then `kubectl describe pod` for the Events and the Last State with its exit code. "
                "Exit code 137 with OOMKilled points at memory, a failed liveness probe shows up in the Events, and a small code like 1 means the app exited with its own error. "
                "Then `kubectl logs --previous` shows what the crashed container printed. "
                "If the image has no tools, I use `kubectl debug` with an ephemeral container to check config, DNS or files from inside the Pod."
            ),
        },
        {
            "q": "The Pods are healthy, but requests to the Service fail. What do you check?",
            "a": (
                "First the Service's endpoints with `kubectl get endpointslices -l kubernetes.io/service-name=<svc>`; empty endpoints mean the selector matches no ready Pods. "
                "Then I compare the selector with `kubectl get pods --show-labels`, and check that `targetPort` matches the container's port. "
                "Next I test from inside the cluster with a throwaway busybox Pod, using the Service's DNS name, to rule out DNS. "
                "If all of that works, I look at NetworkPolicies and then at the Gateway or Ingress route in front of the Service."
            ),
        },
        {
            "q": "What is RBAC in Kubernetes, and how do you debug a Forbidden error?",
            "a": (
                "RBAC is role-based access control: Roles and ClusterRoles list allowed verbs on resources, and bindings give them to users, groups or ServiceAccounts. "
                "Permissions only add up; there are no deny rules. "
                "The Forbidden message names the subject, verb, resource and namespace, and `kubectl auth can-i` with `--as` confirms it. "
                "Then I add the smallest Role and RoleBinding that allow exactly that action, rather than a broad ClusterRole."
            ),
        },
    ],
    "deeper": {
        "minutes": 12,
        "body": (
            "Five more failures you will meet sooner or later, each with its first check:\n"
            "- `exec format error` in the logs, right at start: the image was built for another CPU. On an Apple Silicon Mac, an image built only for amd64 cannot run on arm64 kind nodes. Build multi-platform images (Part 3) or pick an image that has an arm64 variant.\n"
            "- `Init:CrashLoopBackOff` or `Init:0/1` for a long time: an init container fails or waits. Its logs need `-c <init-container-name>`.\n"
            "- `Terminating` that never ends: something holds the object, often a finalizer waiting for a controller that is gone. `kubectl get pod <name> -o jsonpath='{.metadata.finalizers}'` shows it. Do not force-delete before you know what the finalizer protects.\n"
            "- `Evicted` or `ContainerStatusUnknown` Pods left behind: the node ran short of memory or disk and evicted them (Day 35). The Deployment already replaced them; read the eviction message, then delete the leftovers.\n"
            "- `Unable to connect to the server` from kubectl itself: the cluster is down or you are on the wrong context. `kubectl config current-context` should say `kind-devops`, and `docker ps` should show the kind node containers.\n\n"
            "When the problem looks like the network, check in order: the name, the endpoints, the port, and then policy. "
            "A NetworkPolicy (Day 33) that selects a Pod blocks all traffic its rules do not allow. "
            "If `nslookup` works and the endpoints are there but connections time out, look for a policy with `kubectl get networkpolicy -n <ns>`.\n\n"
            "At work, two more habits help. Write each incident down: the symptom, the command that showed the cause, the fix. "
            "After a few months that file is your team's best runbook. "
            "And automate the boring part: the `kubectl events --types=Warning` view and a few saved k9s shortcuts often find the problem before anyone opens a dashboard.\n\n"
            "Finally, know where Kubernetes' own logs live. On kind, `docker exec devops-control-plane crictl ps` lists the control plane containers, and `kind export logs` collects logs from every node into a folder for you to read or attach to a bug report."
        ),
    },
    "sources": [
        {"title": "Debug Pods", "url": "https://kubernetes.io/docs/tasks/debug/debug-application/debug-pods/"},
        {"title": "Debug running Pods", "url": "https://kubernetes.io/docs/tasks/debug/debug-application/debug-running-pod/"},
        {"title": "Debug Services", "url": "https://kubernetes.io/docs/tasks/debug/debug-application/debug-service/"},
        {"title": "Using RBAC authorization", "url": "https://kubernetes.io/docs/reference/access-authn-authz/rbac/"},
    ],
}
