NEW = {}

NEW["goal"] = "By the end you can find out why a workload is broken with a fixed order of kubectl commands, read the common failure states, test from inside Pods that have no tools, and tell an RBAC \"forbidden\" from a bug."

NEW["opening"] = """Picture a Saturday night, and a guest who says the food never came. The new manager runs into the kitchen, restarts the oven, resets the card reader and moves two cooks to other stations. Ten minutes later the soup arrives. Nobody knows which of the three changes fixed it, or whether any of them did. Next Saturday it happens again.

Last time, we packaged hello-devops with Helm and Kustomize, and everything worked. Real clusters are less kind. Under pressure, doing something feels better than reading, and Kubernetes makes that worse: it restarts things on its own, so the clues can vanish while you guess.

In this lesson, we'll learn a fixed order of checks and read the common failure states. Then we'll look inside Pods that have no tools, and learn to tell a locked door from a broken one. The lab breaks five services for you to fix. Before we start, make a guess, and keep it in mind."""

NEW["guess"] = (
    "A Pod is in CrashLoopBackOff: its container keeps crashing and restarting. `kubectl logs` on it shows nothing useful. Where is the error message most likely to be?",
    "After a restart, `kubectl logs` shows the new container, which may have printed nothing yet. `--previous` shows the container that crashed, error and all.",
)

NEW["terms"] = [
    "A short record that a Kubernetes part wrote about an object, such as a failed check; kept about an hour.",
    "A container keeps stopping, and Kubernetes waits longer before each restart, up to 5 minutes.",
    "The node failed to get the image and now waits longer between tries.",
    "The image is there, but the container's settings cannot be put together, usually because of a missing ConfigMap or Secret.",
    "A temporary extra container that kubectl debug adds to a running Pod for checks.",
    "Role-based access control: rules that say who may do which actions on which objects.",
    "A Role lists allowed actions in one namespace; a RoleBinding gives that Role to someone.",
    "An identity for a program, such as a CI job or a Pod that calls the Kubernetes API.",
]

S = []

S.append(("A method beats guessing", """
When something breaks, the urge is to change three things and hope, like the manager in the opening. Kubernetes punishes that. Many parts react on their own, so a guess can change the evidence before you have read it. Restarting or deleting the broken Pod "to see if it helps" throws away the crashed container's logs, its last state and often the newest events. A fixed order of checks is faster, even when you think you already know the answer.

**Read the evidence before you change anything. A restart deletes clues.**

Work from the bottom up, because each layer depends on the one below it:
1. The Pod: is it scheduled, running, ready, restarting?
2. The Service: does it select those Pods, and does its `targetPort` match the port the app listens on?
3. The route: does the Gateway or Ingress send traffic to that Service?
4. The node: if many Pods fail together, is one node short of memory or not ready?

In the restaurant, that is the table, then the host's list, then the front door, then the whole kitchen. The node sits under every Pod, yet it comes last. A sick node shows up as many Pods failing at once, so a single broken Pod rarely points there.

For each layer, the commands are nearly always the same:
1. `kubectl get` for STATUS, READY and RESTARTS.
2. `kubectl describe`, reading the Events at the bottom first.
3. `kubectl logs`, with `--previous` if the container restarted.
4. `kubectl get events` for the whole namespace, sorted by time.
5. `kubectl exec`, `port-forward` or `debug` to test from inside.

Two habits matter more than any tool. Change one thing at a time and watch what happens. And test layers one by one. For example, `kubectl port-forward pod/<pod>` skips the Service, so if the Pod answers there and not through the Service, you know which layer to read. With the method in hand, we start at the bottom, with Pods that never get going.
"""))

S.append(("Pods that never start", """
In these four states the container has not run yet, so `kubectl logs` has nothing to show. The cook never lit the stove, so there is no smoke to read. The answer is in `kubectl describe pod`, under Events:
- `Pending`: no node will take the Pod. Usual causes: requests larger than any node's free room, a PVC (storage claim) that cannot bind, or a nodeSelector, affinity or taint that rules out every node.
- `ContainerCreating` for more than a minute: the node is still setting the Pod up. Usually a volume that will not mount, or a large image still downloading.
- `ErrImagePull`, then `ImagePullBackOff`: the node cannot get the image. Check the name and tag, the registry login for private images, and on kind whether you ran `kind load docker-image`.
- `CreateContainerConfigError`: the image is there, but the kubelet (the helper program on each node) cannot put the container's settings together. Almost always a missing ConfigMap or Secret, or a missing key in one.

The states follow the chain from Day 38. `Pending` means the scheduler found no node. In the other three, a node was chosen, and its kubelet is stuck preparing the container.

"BackOff" in a status only means the kubelet now waits longer between tries. It is never the cause. Look for the first error in the Events.

For `Pending`, read the scheduler's `FailedScheduling` event slowly, because it accounts for every node. Take a message that starts `0/3 nodes are available: 1 node(s) had untolerated taint(s), 2 Insufficient cpu`. It counts all three nodes. One is ruled out by a taint (kind's control plane, Day 43), and two lack free CPU for the request. Lower the request, remove other workloads, or add a node.

Those Pods never ran. Next, Pods that run and then fail, which at least leave clues.
"""))

S.append(("Pods that start, then fail", """
Here the container ran at least once, so there is evidence in its logs and in its last state:
- `CrashLoopBackOff`: the container keeps stopping, and the kubelet waits longer before each restart: 10 seconds, then 20, 40, up to 5 minutes. It is a symptom. Read `kubectl logs --previous` for the app's own error, then `Last State` in describe.
- `OOMKilled`: `Last State` shows `Reason: OOMKilled` and `Exit Code: 137`. The container went over its memory limit (Day 43).
- Restarts with clean logs: often a liveness probe that fails. The Events say `Liveness probe failed` and then that the container will be restarted. The app was fine; the check was wrong.
- `Running` but `0/1` READY: the readiness probe fails, so the Pod gets no traffic. The Events show `Readiness probe failed` with a status code or an error.
- All Pods ready, but the Service still fails: the Service matches no Pods. `kubectl get endpointslices -l kubernetes.io/service-name=<svc>` shows `<unset>` under ENDPOINTS.

That last case fools people, because every Pod looks healthy. It is a full kitchen with a host whose list has the wrong names on it. Compare the Service's selector (`kubectl describe service`) with the Pods' labels (`kubectl get pods --show-labels`), and check that `targetPort` is the port the app listens on.

The STATUS column is a summary that kubectl writes for you. `CrashLoopBackOff` is not a Pod phase; the phase is still `Running`. When the column confuses you, `kubectl get pod <name> -o yaml` shows the real fields under `status`.

Two of those bullets sent you to the Events and the logs. Next, we learn to read both well.
"""))

S.append(("Events, logs and exit codes", """
Events are the kitchen's incident notebook. They are short records that Kubernetes parts write about objects: the scheduler placed a Pod, the kubelet pulled an image, a probe failed. The API server keeps them for about an hour by default, and then the page is torn out. So read them early.

Three ways to read them:
- `kubectl describe pod <name>` shows one object's events at the bottom.
- `kubectl get events -n <ns> --sort-by=.metadata.creationTimestamp` lists the namespace's events, oldest first.
- `kubectl events -n <ns> --for pod/<name>` is the newer command. It sorts by time on its own, and `--types=Warning` hides the routine ones.

Logs are what the container wrote to standard output and standard error, the two text streams every program can print to. `kubectl logs <pod>` reads the current container. Right after a crash, that is a fresh container that may not have printed anything yet. That is the answer to the guess. `--previous` reads the one before, the one that crashed: the note left by the cook who just went home. Add `-c <container>` when a Pod has more than one container, and `-f` to follow new lines.

The exit code under `Last State`, the number a program leaves behind when it stops, narrows things down fast:
- 0: the process finished on purpose. In a Deployment that still counts as a restart, because a web app should never finish.
- 1, or another small number: the app exited with its own error. Read the logs.
- 137: killed with SIGKILL (128 + 9), the stop-now signal. Most often the OOM killer, or an app that ignored the polite stop signal until its grace period ran out.
- 143: stopped with SIGTERM (128 + 15), the polite stop signal Kubernetes sends first.

Sometimes the notebook and the logs are not enough, and you need to stand inside the Pod. That is next.
"""))

S.append(("Looking inside: exec, port-forward and kubectl debug", """
Some questions can only be answered from inside the cluster. Can this Pod look up a name, reach a port or see a file?

The command `kubectl exec -it <pod> -- sh` opens a shell, a text window for commands, in a running container. That only works if the image has a shell and the tools you need, and small images often do not. The hello-devops image has `sh` and Python, but no `nslookup`, `curl` or `wget`. Distroless images, which hold only the app and what it needs to run, have no shell at all.

`kubectl debug` gets around that. It adds an ephemeral container to a running Pod: a temporary extra container with an image you choose. That can be `busybox`, or `nicolaka/netshoot`, a large image full of network tools. Picture sending a helper with a toolbox to stand next to the cook. It shares the Pod's network, so it sees names and ports exactly as the app does. With `--target=web` it also sees the processes of the `web` container. Ephemeral containers are never restarted, and they go away when the Pod is deleted. Two more forms:
- `kubectl debug <pod> -it --copy-to=<pod>-debug --container=web -- sh` makes a copy of the Pod with a shell, for a container that crashes too fast to inspect.
- `kubectl debug node/<node> -it --image=ubuntu` starts a Pod on that node with the node's files mounted at `/host`.

In production, images often have no shell and your access may be read-only, so `kubectl debug` is the normal way to look inside. Fixes still go through Git and, from Day 47, Argo CD.

For name and network checks you often do not need the broken Pod at all. A throwaway Pod is enough: `kubectl run net-test -n hello --rm -it --image=busybox:1.37 --restart=Never -- nslookup redis.hello.svc.cluster.local`. NXDOMAIN, the "no such name" answer, means the name is wrong or the Service does not exist. If the name resolves but connections fail, check the Service's endpoints next.

One more failure looks like a bug and is not one at all. Next, the locked door.
"""))

S.append(("Forbidden: RBAC basics", """
`Error from server (Forbidden)` means the API server understood your request and refused it. Your YAML is fine. The person or program behind the request lacks permission. It is a key that does not open a door, not a broken door.

The API server works in two steps. First it checks who is asking. On kind, your kubeconfig holds a client certificate, a file that proves who you are. A program in a Pod sends the ServiceAccount token that Kubernetes mounts into the Pod. Then the API server checks whether that identity may do this.

Kubernetes decides with role-based access control (RBAC), and four kinds of object do the work:
- A Role lists allowed actions in one namespace, such as `get`, `list` and `watch` on `pods`. A ClusterRole does the same for the whole cluster.
- A RoleBinding gives a Role to subjects in one namespace. A ClusterRoleBinding gives a ClusterRole everywhere.
- Subjects are users, groups and ServiceAccounts. A ServiceAccount is an identity for a program, such as a CI job or a Pod that calls the API.

Permissions only add up. There are no deny rules, so "forbidden" always means that nothing allowed the action.

The error tells you exactly what was missing, for example: `User "system:serviceaccount:hello:viewer" cannot delete resource "pods" in API group "" in the namespace "hello"`. Read it as subject, verb, resource, API group and namespace. The API group is the part of `apiVersion` before the slash: `apps` for Deployments, and empty for core kinds such as Pods. Then ask the cluster directly:
- `kubectl auth can-i delete pods -n hello` answers yes or no for you.
- Add `--as=system:serviceaccount:hello:viewer` to ask on behalf of someone else. Your kind admin user is allowed to do that.

Fix it with the smallest Role that does the job. Binding a robot to `cluster-admin` makes the error go away, and also gives that robot every key in the building. RBAC is also how you keep Secrets private (Day 42): very few Roles should allow `get` or `list` on `secrets`.

You now have the whole method. Last, a few tools that make it faster, and the one layer we left for the end.
"""))

S.append(("Faster tools, and when the node is the problem", """
A few tools save time once the method is in your head:
- `kubectl top pods` and `kubectl top nodes` show live CPU and memory use, from the metrics-server you installed on Day 43. Check them before you raise a limit.
- k9s is a terminal UI (a screen you drive with the keyboard) over the same API. You move between Pods, logs, events and describe output with a few keys. Install it with `brew install derailed/k9s/k9s` and run `k9s -n debug-lab`.
- Headlamp is a graphical alternative. The old Kubernetes Dashboard project has been archived, and the [Kubernetes blog](https://kubernetes.io/blog/2026/06/01/dashboard-to-headlamp/) points to Headlamp instead.

Learn the plain kubectl commands first anyway. k9s is not installed on every machine you will log in to; kubectl is. A typical on-call runbook, a team's written checklist for incidents, starts with the same ladder: get, describe, logs `--previous`, events, endpoints.

If many Pods fail at once, and all on one node, look at the node. That is the whole kitchen, not one table. The command `kubectl get nodes` shows `NotReady` when a kubelet stops reporting. Then `kubectl describe node <name>` shows conditions such as `MemoryPressure` and `DiskPressure`, and lists the Pods on the node with their requests. On kind, a node is a Docker container. Run `docker stats` on your Mac to see whether Docker Desktop itself is short of memory; its settings let you give it more.

The limit of all this is plain: the method finds causes, but only in what Kubernetes can see. A bug inside your app's code still needs the app's own logs and, later in the course, metrics and traces. The worked example now runs the method on a real mistake.
"""))

NEW["sections"] = S

NEW["drop"] = ["analogy", "real_world", "mistake"]

NEW["diagram_caption"] = "Debug in the order traffic depends on: Pod first, then Service, then route; check the node when failures pile up together."

NEW["worked"] = [
    "Set this up on purpose: change `REDIS_HOST` in the lab's ConfigMap to `rediss`, one letter too many, and restart the Deployment so new Pods read it. This is a typical real mistake.",
    "The symptom: the rollout never finishes. One new Pod is Running but not ready. The three old Pods keep serving, because the Deployment uses `maxUnavailable: 0` and readiness holds the rollout back. Users see nothing wrong yet.",
    "Ask the new Pod's events. Readiness fails with 503, and the app returns 503 from `/readyz` when it cannot reach Redis. Yet Redis itself is Running and ready, so the problem is between the two.",
    "Check what the new Pod was given. The value looks almost right. You want to test the name from inside the Pod's network, but the app image has no DNS tools.",
    "Add an ephemeral busybox container to the same Pod. It shares the Pod's network, so its DNS answers are the app's DNS answers. The name `rediss` does not exist.",
    "The correct name resolves to the Redis Service's address. That confirms it: the ConfigMap has a typo, and Redis and the network are fine.",
    "Fix the value and roll again. In a real team you would fix it in git, not with `kubectl patch`; on Day 47, Argo CD makes git the normal path.",
]

NEW["task"] = (
    [
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
    [
        "If `kubectl logs` shows nothing, ask whether the container ever started. If it never did, the answer is in the Events.",
        "`kubectl get pod <pod> -n debug-lab -o jsonpath='{.status.containerStatuses[0].lastState}'` prints the last crash on one line.",
        "For RBAC you need three commands: `kubectl create serviceaccount`, `kubectl create role` and `kubectl create rolebinding`. The commands list has the last two.",
    ],
    "All five Pods in `debug-lab` are Running and 1/1 Ready with no new restarts, `net-test` gets JSON from search, and `kubectl auth can-i delete pods -n debug-lab --as=system:serviceaccount:debug-lab:viewer` says no.",
)

NEW["explain_back"] = (
    "Explain in 3 to 4 sentences how you would find out why a Pod is in CrashLoopBackOff. Mention which commands you run, in which order, and what each one can tell you.",
    "First `kubectl get pods` to see the status and how many restarts there have been. Then `kubectl describe pod` and read the Events and `Last State`: the exit code tells me whether it was the app's own error, an OOM kill (137) or a failed liveness probe. Then `kubectl logs --previous`, because the current container may have printed nothing yet, while the crashed one has the error. If that is still not enough, I compare the config the Pod got, such as environment variables, ConfigMaps and probes, with what the app expects.",
)

NEW["recap"] = [
    "Debug bottom-up: Pod, then Service, then route, then node. Change one thing at a time.",
    "Pending, ContainerCreating, ImagePullBackOff and CreateContainerConfigError: no logs yet, read the Events.",
    "CrashLoopBackOff is a symptom; `logs --previous` and the exit code in Last State show the cause.",
    "Healthy Pods but a failing Service usually means a selector or targetPort mismatch: check EndpointSlices.",
    "`kubectl debug` adds an ephemeral container with tools; a throwaway busybox Pod checks DNS.",
    "A Forbidden error comes from RBAC: read the message, ask `kubectl auth can-i`, grant the smallest Role.",
]

NEW["closing"] = """We started with a manager who changed three things at once and learned nothing. The method in this lesson does the opposite: read the Pod, the Service, the route and then the node, and change one thing at a time. In the break-and-fix lab, write down the one line of output that proves each cause before you touch the file; that habit is the real skill. This part has used `kubectl apply` and `kubectl patch` by hand, though, and every hand change can drift away from Git. Next, we'll let the cluster follow Git on its own. What if the repo were the only way to change production?"""

NEW["check"] = [
    ("A new Pod stays Pending. Its event says `0/3 nodes are available: 1 node(s) had untolerated taint(s), 2 Insufficient memory`. What is the most likely fix?",
     "The two workers lack free memory for the request, and scheduling uses requests, so the request must shrink or room must appear."),
    ("A Pod shows `CreateContainerConfigError` and `kubectl logs` prints nothing. Why are the logs empty?",
     "The kubelet could not put the container's settings together, usually because a ConfigMap or Secret is missing, so no process ever ran."),
    ("A CI job's ServiceAccount `deployer` in namespace `ci` gets Forbidden when it applies a Deployment to namespace `shop`. Which command checks the permission directly?",
     "`kubectl auth can-i create deployments -n shop --as=system:serviceaccount:ci:deployer` asks the API server about that exact subject, action and namespace."),
]

NEW["interview"] = [
    ("A Pod is in CrashLoopBackOff. Walk me through how you debug it.",
     "I start with `kubectl get pods` for the restart count, then `kubectl describe pod` for the Events and the Last State with its exit code. Exit code 137 with OOMKilled points at memory, and a failed liveness probe shows up in the Events. A small code such as 1 means the app exited with its own error. Then `kubectl logs --previous` shows what the crashed container printed. If the image has no tools, I use `kubectl debug` with an ephemeral container to check config, DNS or files from inside the Pod."),
    ("The Pods are healthy, but requests to the Service fail. What do you check?",
     "First the Service's endpoints with `kubectl get endpointslices -l kubernetes.io/service-name=<svc>`; empty endpoints mean the selector matches no ready Pods. Then I compare the selector with `kubectl get pods --show-labels`, and check that `targetPort` matches the container's port. Next I test from inside the cluster with a throwaway busybox Pod, using the Service's DNS name, to rule out DNS. If all of that works, I look at NetworkPolicies and then at the Gateway or Ingress route in front of the Service."),
    ("What is RBAC in Kubernetes, and how do you debug a Forbidden error?",
     "RBAC is role-based access control: Roles and ClusterRoles list allowed verbs on resources, and bindings give them to users, groups or ServiceAccounts. Permissions only add up; there are no deny rules. The Forbidden message names the subject, verb, resource and namespace, and `kubectl auth can-i` with `--as` confirms it. Then I add the smallest Role and RoleBinding that allow exactly that action, rather than a broad ClusterRole."),
]

NEW["deeper"] = """
Five more failures, each with the first thing to check:
- `exec format error` in the logs, right at start: the image was built for another kind of CPU. On an Apple Silicon Mac, an image built only for amd64 cannot run on arm64 kind nodes. Build multi-platform images (Part 5) or pick an image that has an arm64 variant.
- `Init:CrashLoopBackOff` or `Init:0/1` for a long time: an init container fails or waits. Its logs need `-c <init-container-name>`.
- `Terminating` that never ends: something holds the object, often a finalizer (a "do not delete yet" mark) waiting for a controller that is gone. `kubectl get pod <name> -o jsonpath='{.metadata.finalizers}'` shows it. Do not force-delete before you know what the finalizer protects.
- `Evicted` or `ContainerStatusUnknown` Pods left behind: the node ran short of memory or disk and evicted them (Day 43). The Deployment already replaced them; read the eviction message, then delete the leftovers.
- `Unable to connect to the server` from kubectl itself: the cluster is down or you are on the wrong context. `kubectl config current-context` should say `kind-devops`, and `docker ps` should show the kind node containers.

When the problem looks like the network, check in order: the name, the endpoints, the port, and then policy. A NetworkPolicy (Day 41) that selects a Pod blocks all traffic its rules do not allow. If `nslookup` works and the endpoints are there but connections time out, look for a policy with `kubectl get networkpolicy -n <ns>`.

At work, write each incident down: the symptom, the command that showed the cause, the fix. After a few months that file is your team's best runbook. In production, a `kubectl patch` is for emergencies only, and someone writes it up afterwards. Automate the boring part too: the `kubectl events --types=Warning` view and a few saved k9s shortcuts often find the problem before anyone opens a dashboard.

Kubernetes' own parts write logs too. On kind, `docker exec devops-control-plane crictl ps` lists the control plane containers, and `kind export logs` collects logs from every node into a folder for you to read or attach to a bug report.
"""
