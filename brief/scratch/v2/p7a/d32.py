"""Day 32: Deployments and rollouts."""
from svg import box, arrow, cap, svg

DIAGRAM = svg(250, "A Deployment scales a new ReplicaSet up and the old ReplicaSet down, one Pod at a time", [
    box(16, 103, 128, 44, "bxg", "Deployment"),
    cap(80, 168, "image: 1.1.0"),
    box(208, 36, 144, 44, "bxp", "ReplicaSet v1"),
    box(208, 170, 144, 44, "bxt", "ReplicaSet v2"),
    arrow(144, 118, 206, 64),
    arrow(144, 132, 206, 186),
    cap(280, 100, "pods: 3, 2, 1, 0"),
    cap(280, 234, "pods: 0, 1, 2, 3"),
    box(408, 36, 136, 44, "bx", "old Pods"),
    box(408, 170, 136, 44, "bx", "new Pods"),
    arrow(352, 58, 406, 58, dashed=True),
    arrow(352, 192, 406, 192, dashed=True),
    cap(476, 128, "Service sends"),
    cap(476, 142, "traffic to ready"),
    cap(476, 156, "Pods of both"),
])

DEPLOY_V1 = """# Runs 3 copies (pods) of hello-devops and replaces any that die.
# Day 32 writes this first version, Day 34 adds envFrom, Day 35 adds probes and resources.
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
      maxSurge: 1 # add at most 1 extra pod at a time
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
              containerPort: 8000"""

KUSTOMIZATION_V1 = """# The list of files that make up the app. Apply them all with: kubectl apply -k k8s
# Day 32 version: Days 33 to 35 add one file at a time.
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization
resources:
  - namespace.yaml
  - deployment.yaml"""

L = {
    "id": "d32",
    "title": "Deployments and rollouts",
    "minutes": 50,
    "goal": "By the end you can run hello-devops as a Deployment, explain how its ReplicaSets heal and scale it, roll a new version out step by step, and roll back when a version is bad.",
    "guess": {
        "q": "A Deployment runs 4 Pods of version 1 with the default settings. You switch the image to version 2, but version 2 can never start. What do users notice?",
        "options": [
            "Downtime: all old Pods stop before any new one starts",
            "Errors: Kubernetes sends traffic to the broken Pods",
            "Nothing: Kubernetes rolls back to version 1 on its own",
            "Little: most old Pods keep serving, and the rollout stalls",
        ],
        "answer": 3,
        "why": "A rolling update removes old Pods only as far as maxUnavailable allows, and broken Pods never become ready, so they get no traffic. Kubernetes does not roll back by itself; the rollout waits until you fix it or run `kubectl rollout undo`.",
    },
    "terms": [
        {"term": "Deployment", "plain": "An object that keeps a set number of identical Pods running and replaces them step by step when you change them."},
        {"term": "ReplicaSet", "plain": "The object a Deployment creates for each version of its Pod template, to keep exactly N of those Pods running."},
        {"term": "Replicas", "plain": "The number of identical Pods you want, set in `spec.replicas`."},
        {"term": "Rollout", "plain": "The process of moving a Deployment's Pods from one version of the Pod template to the next."},
        {"term": "Rolling update", "plain": "A rollout that replaces old Pods with new ones a few at a time, so the app stays up."},
        {"term": "maxSurge", "plain": "How many Pods above the desired count a rolling update may create at once."},
        {"term": "maxUnavailable", "plain": "How many Pods below the desired count may be unavailable during a rolling update."},
        {"term": "Revision", "plain": "A numbered version of a Deployment's Pod template that you can roll back to."},
    ],
    "sections": [
        {
            "h": "From a bare Pod to a Deployment",
            "body": """Yesterday's Pod had no guardian. Delete it and it was gone, and a dead node would take it along. Real apps run under a **Deployment** instead. You give it a Pod template (image, ports, settings) and a number of copies. The Deployment does not create Pods itself. It works through a chain:
- Deployment: owns the update strategy and the list of past versions.
- ReplicaSet: keeps exactly N Pods from one template running.
- Pod: runs your container.

Each object points to its owner in `metadata.ownerReferences`. Delete the Deployment and the garbage collector removes its ReplicaSets and Pods too.

The names tell the story. A Pod called `hello-devops-698679bfb-7l7h8` belongs to the ReplicaSet `hello-devops-698679bfb`, which belongs to the Deployment `hello-devops`. The middle part is a hash of the Pod template. Kubernetes also stores it as a label, `pod-template-hash`, on the ReplicaSet and its Pods. That label keeps the Pods of two versions apart, so their ReplicaSets never fight over each other's Pods.

You will rarely touch ReplicaSets yourself. Think of them as the Deployment's shift supervisors: one per version of the template.""",
            "refs": [
                {"title": "Deployments", "url": "https://kubernetes.io/docs/concepts/workloads/controllers/deployment/", "kind": "docs"},
                {"title": "Kubernetes course, full beginners tutorial (freeCodeCamp)", "url": "https://www.youtube.com/watch?v=d6WC5n9G_sM", "kind": "watch"},
            ],
        },
        {
            "h": "Self-healing and scaling are one loop",
            "body": """A ReplicaSet runs the control loop from Day 30 with one number in it. It counts the Pods that match its selector and compares the count with `replicas`. Too few, and it creates Pods. Too many, and it deletes some. Everything else follows from that:
- Delete a Pod by hand, and a new one appears within seconds, with a new name and a new IP address.
- Change `replicas` from 3 to 5, and two Pods appear. That is all scaling is.
- A container crashes, and the kubelet restarts it in place. The Pod still exists, so the ReplicaSet does nothing.

A dead node takes longer, and this surprises people. The node stops reporting, and Kubernetes marks it not ready. By default, its Pods stay bound to it for five more minutes, in case the node comes back. Only then are they evicted, and the ReplicaSet creates replacements on healthy nodes. So spread replicas over several nodes, and do not expect instant failover.

The count uses labels, not names. Remove the `app` label from one running Pod, and the ReplicaSet no longer counts it. It creates a replacement, while the relabelled Pod keeps running with no owner. Handy for pulling a Pod aside to debug it, and confusing if done by accident. For the same reason, a Deployment's `selector` cannot be changed after creation.""",
            "refs": [
                {"title": "ReplicaSet", "url": "https://kubernetes.io/docs/concepts/workloads/controllers/replicaset/", "kind": "docs"},
                {"title": "Taints and tolerations (the 5-minute default)", "url": "https://kubernetes.io/docs/concepts/scheduling-eviction/taint-and-toleration/", "kind": "docs"},
            ],
        },
        {
            "h": "What starts a rollout",
            "body": """A rollout happens if, and only if, you change the Pod template: anything under `spec.template`. These all start one:
- A new image tag, the everyday case.
- A changed environment variable, port, probe or resource setting.
- A new label or annotation inside the template.

These do not:
- Changing `replicas`. Scaling is not a new version.
- Changing labels or annotations on the Deployment itself, outside the template.
- Changing a ConfigMap that the Pods read. The template did not change, so nothing rolls (Day 34 shows the fix).

For each new template, the Deployment creates a new ReplicaSet and moves Pods from the old one to the new one. The old ReplicaSet is not deleted. It stays, scaled to 0, as a record of that version. That record is what makes rollback fast. By default the Deployment keeps the last 10 old ReplicaSets, set by `revisionHistoryLimit`.

Each ReplicaSet gets a revision number in an annotation. `kubectl rollout history` lists them. Only template changes create revisions, so the history stays a clean list of versions you actually shipped.""",
            "refs": [
                {"title": "Updating a Deployment", "url": "https://kubernetes.io/docs/concepts/workloads/controllers/deployment/#updating-a-deployment", "kind": "docs"},
            ],
        },
        {
            "h": "Rolling updates, step by step",
            "body": """The default strategy is `RollingUpdate`. Two settings control its pace:
- `maxSurge`: how many extra Pods may exist above `replicas` during the update.
- `maxUnavailable`: how many Pods may be missing below `replicas`.

Both default to 25%. Percentages are turned into whole Pods: surge rounds up, unavailable rounds down. With 4 replicas, that is 1 extra and 1 missing. So during the update you have at least 3 available Pods and at most 5 Pods in total. Both cannot be 0, or nothing could ever move.

The lab picks `maxSurge: 1` and `maxUnavailable: 0` for its 3 replicas. In words: add one new Pod, wait until it is ready, then remove one old Pod. Here is the whole update:
1. The new ReplicaSet scales to 1. There are 4 Pods: 3 old, 1 new.
2. The new Pod becomes ready. The old ReplicaSet scales to 2.
3. The new ReplicaSet scales to 2, and waits for that Pod to be ready.
4. The old ReplicaSet scales to 1, the new one to 3, and finally the old one to 0.

You never have fewer than 3 ready Pods. The price is speed and room: one extra Pod at a time needs spare CPU and memory on some node. With a big Deployment, a larger surge such as 25% finishes faster.

During the update, both versions serve traffic at once. A Service (Day 33) sends requests to every ready Pod with the right label, old or new. So version 2 must work alongside version 1, for example with the same database schema.""",
            "refs": [
                {"title": "Performing a rolling update", "url": "https://kubernetes.io/docs/tasks/run-application/update-deployment-rolling/", "kind": "docs"},
            ],
        },
        {
            "h": "Readiness decides when each step happens",
            "body": """\"Wait until the new Pod is ready\" carries the whole safety of a rolling update. A Pod is ready when all its containers are running and pass their readiness checks. Day 35 adds a readiness probe to hello-devops, a URL that the kubelet calls every few seconds.

Without a readiness probe, a Pod counts as ready as soon as its container starts. The app may still be loading, or broken in a way that only shows on the first request. The Deployment cannot tell, and it moves on. This is the main reason to add readiness probes before you rely on rolling updates.

When new Pods never become ready, because of a bad image or a crash at start, the rollout stalls:
- The old Pods keep serving. With `maxUnavailable: 0`, none of them is removed.
- After `progressDeadlineSeconds` (600 seconds by default), the Deployment reports the condition `ProgressDeadlineExceeded`.
- `kubectl rollout status` then exits with an error, so a CI job can notice and act.
- Kubernetes does not roll back on its own. You fix the image or run `kubectl rollout undo`.

`minReadySeconds` adds one more guard. A new Pod must stay ready for that many seconds before it counts as available. That catches apps that start fine and crash a few seconds later.""",
            "refs": [
                {"title": "Deployment status and failed rollouts", "url": "https://kubernetes.io/docs/concepts/workloads/controllers/deployment/#deployment-status", "kind": "docs"},
            ],
        },
        {
            "h": "History, undo, and set image versus editing YAML",
            "body": """Four `kubectl rollout` subcommands cover most days:
- `rollout status`: follow the rollout until it finishes or fails.
- `rollout history`: list the revisions. Add `--revision=2` to see one template in full.
- `rollout undo`: go back to the previous revision, or to any kept revision with `--to-revision=N`.
- `rollout pause` and `rollout resume`: batch several changes into one rollout.

The CHANGE-CAUSE column in the history is empty unless you set the annotation `kubernetes.io/change-cause` on the Deployment, for example with `kubectl annotate`. Teams that use it write the ticket or the reason.

An undo is itself a rollout. Kubernetes copies the old template back, and the old revision moves to a new number. Revision 2 disappears from the list and comes back as revision 4.

There are two ways to change the image, and they look the same for a minute:
- `kubectl set image deployment/hello-devops web=hello-devops:1.1.0` changes the live object. Quick, and good for experiments.
- Edit `image:` in `k8s/deployment.yaml` and apply the file. Slower, but git now records the change, and someone can review it.

Mixing them causes drift. The next `kubectl apply` of an old file quietly undoes your `set image`. From Day 39, Argo CD undoes it within minutes. Experiment with `set image`, then make the real change in the file.""",
            "refs": [
                {"title": "Rolling back a Deployment", "url": "https://kubernetes.io/docs/concepts/workloads/controllers/deployment/#rolling-back-a-deployment", "kind": "docs"},
                {"title": "kubectl rollout", "url": "https://kubernetes.io/docs/reference/kubectl/generated/kubectl_rollout/", "kind": "docs"},
            ],
        },
        {
            "h": "Recreate: when two versions must never overlap",
            "body": """The other strategy is `Recreate`. It stops every old Pod first, and only then starts the new ones. There is always a gap with no Pods at all, so users see downtime.

That sounds bad, and for most web apps it is. Recreate exists for apps where two versions running side by side would be worse than a short outage:
- The app holds an exclusive lock, such as a single writer to a file or a queue.
- Its Pods use a disk that only one Pod can mount at a time (a ReadWriteOnce volume, Day 36).
- The new version changes the database in a way the old version cannot handle.

For hello-devops, a rolling update is right. The app is stateless, and Redis holds the shared counter, so any number of versions can run side by side.

Rolling update and Recreate are the only two strategies a Deployment has. Blue-green and canary releases, where you shift traffic gradually or flip it all at once, need extra tools such as Argo Rollouts, or traffic rules at a Gateway (Day 36).""",
            "refs": [
                {"title": "Deployment strategy", "url": "https://kubernetes.io/docs/concepts/workloads/controllers/deployment/#strategy", "kind": "docs"},
            ],
        },
    ],
    "analogy": "Think of replacing the staff of a call center during working hours. The supervisor (the Deployment) hires one new operator, waits until they are trained and taking calls, then sends one old operator home, and repeats until the whole team is new. If the new hires keep failing training, the old team simply keeps working. The picture breaks on memory: a new operator can look up past calls, but a new Pod starts empty, so anything worth keeping must live outside it, the way hello-devops keeps its counter in Redis.",
    "diagram": DIAGRAM,
    "diagram_caption": "During a rollout the Deployment scales the new ReplicaSet up and the old one down. The Service sends traffic to ready Pods of both versions.",
    "worked": {
        "title": "Roll out a good version, then a broken one",
        "steps": [
            {
                "say": "In the scratch namespace, create a Deployment of nginx 1.27 with 4 replicas. One ReplicaSet appears, named after the Deployment plus the template hash.",
                "code": "$ kubectl create deployment web --image=nginx:1.27 --replicas=4 -n scratch\ndeployment.apps/web created\n$ kubectl get rs -n scratch\nNAME             DESIRED   CURRENT   READY   AGE\nweb-6d8c7fb5d9   4         4         4       25s",
                "lang": "console",
            },
            {
                "say": "Change the image. `kubectl create deployment` named the container after the image, so it is `nginx`. Follow the rollout: with the defaults for 4 replicas (1 extra, 1 missing), two new Pods start at once.",
                "code": "$ kubectl set image deployment/web nginx=nginx:1.28 -n scratch\ndeployment.apps/web image updated\n$ kubectl rollout status deployment/web -n scratch\nWaiting for deployment \"web\" rollout to finish: 2 out of 4 new replicas have been updated...\nWaiting for deployment \"web\" rollout to finish: 3 out of 4 new replicas have been updated...\nWaiting for deployment \"web\" rollout to finish: 1 old replicas are pending termination...\ndeployment \"web\" successfully rolled out",
                "lang": "console",
            },
            {
                "say": "Two ReplicaSets now exist. The old one is kept at 0 for rollback. Record why you made the change, then look at the history.",
                "code": "$ kubectl get rs -n scratch\nNAME             DESIRED   CURRENT   READY   AGE\nweb-6d8c7fb5d9   0         0         0       3m\nweb-7b9f4c8d6c   4         4         4       40s\n$ kubectl annotate deployment/web -n scratch kubernetes.io/change-cause=\"nginx 1.28\"\ndeployment.apps/web annotated\n$ kubectl rollout history deployment/web -n scratch\ndeployment.apps/web\nREVISION  CHANGE-CAUSE\n1         <none>\n2         nginx 1.28",
                "lang": "console",
            },
            {
                "say": "Now ship a tag that does not exist. The new Pods cannot pull their image. The Deployment removed only one old Pod (maxUnavailable is 1), so three old Pods keep serving.",
                "code": "$ kubectl set image deployment/web nginx=nginx:1.99-typo -n scratch\ndeployment.apps/web image updated\n$ kubectl annotate deployment/web -n scratch kubernetes.io/change-cause=\"typo on purpose\" --overwrite\ndeployment.apps/web annotated\n$ kubectl get pods -n scratch\nNAME                   READY   STATUS             RESTARTS   AGE\nweb-5f6d9c7b8d-h2l5m   0/1     ImagePullBackOff   0          40s\nweb-5f6d9c7b8d-tq9wz   0/1     ErrImagePull       0          40s\nweb-7b9f4c8d6c-4kq8z   1/1     Running            0          3m\nweb-7b9f4c8d6c-9sd2w   1/1     Running            0          3m\nweb-7b9f4c8d6c-xv7nt   1/1     Running            0          3m",
                "lang": "console",
            },
            {
                "say": "`rollout status` with a timeout fails instead of waiting, which is what a CI job wants. Kubernetes will not fix this by itself, so roll back.",
                "code": "$ kubectl rollout status deployment/web -n scratch --timeout=30s\nWaiting for deployment \"web\" rollout to finish: 2 out of 4 new replicas have been updated...\nerror: timed out waiting for the condition\n$ kubectl rollout undo deployment/web -n scratch\ndeployment.apps/web rolled back\n$ kubectl rollout status deployment/web -n scratch\ndeployment \"web\" successfully rolled out",
                "lang": "console",
            },
            {
                "say": "Read the history once more. Revision 2 moved to the new number 4, because the undo copied its template back as a new rollout. Delete the Deployment when you are done; its ReplicaSets and Pods go with it.",
                "code": "$ kubectl rollout history deployment/web -n scratch\ndeployment.apps/web\nREVISION  CHANGE-CAUSE\n1         <none>\n3         typo on purpose\n4         nginx 1.28\n$ kubectl delete deployment web -n scratch\ndeployment.apps \"web\" deleted from scratch namespace",
                "lang": "console",
            },
        ],
    },
    "code": [
        {
            "lang": "yaml",
            "title": "k8s/namespace.yaml",
            "src": open("/home/user/devops-from-zero/labs/hello-devops/k8s/namespace.yaml").read().rstrip("\n"),
            "run": "kubectl apply -f k8s/namespace.yaml",
        },
        {
            "lang": "yaml",
            "title": "k8s/deployment.yaml (first version; Day 34 adds config, Day 35 adds probes and resources)",
            "src": DEPLOY_V1,
            "run": "kubectl apply -f k8s/deployment.yaml",
        },
        {
            "lang": "yaml",
            "title": "k8s/kustomization.yaml (Day 32 version)",
            "src": KUSTOMIZATION_V1,
            "run": "kubectl apply -k k8s",
        },
    ],
    "commands": [
        {"cmd": "kubectl apply -k k8s", "what": "Apply every file listed in `k8s/kustomization.yaml`."},
        {"cmd": "kubectl get deploy,rs,pods -n hello", "what": "Show the Deployment, its ReplicaSets and its Pods together."},
        {"cmd": "kubectl get pods -n hello -l app=hello-devops --show-labels", "what": "List the app's Pods with all labels, including `pod-template-hash`."},
        {"cmd": "kubectl scale deployment hello-devops --replicas=5 -n hello", "what": "Change the desired number of Pods (for experiments; the file should say the same)."},
        {"cmd": "kubectl set image deployment/hello-devops web=hello-devops:1.1.0 -n hello", "what": "Change the image of container `web`, which starts a rollout."},
        {"cmd": "kubectl rollout status deployment/hello-devops -n hello", "what": "Follow a rollout until it finishes or fails."},
        {"cmd": "kubectl rollout history deployment/hello-devops -n hello", "what": "List the revisions the Deployment remembers."},
        {"cmd": "kubectl rollout history deployment/hello-devops -n hello --revision=2", "what": "Show the full Pod template of one revision."},
        {"cmd": "kubectl rollout undo deployment/hello-devops -n hello", "what": "Go back to the previous revision. Add `--to-revision=N` for an older one."},
        {"cmd": "kubectl annotate deployment/hello-devops -n hello kubernetes.io/change-cause=\"ship 1.1.0\"", "what": "Record why you changed it, shown in the history's CHANGE-CAUSE column."},
        {"cmd": "kubectl diff -k k8s", "what": "Show what `apply` would change in the cluster, without changing it."},
        {"cmd": "kubectl port-forward deployment/hello-devops 8080:8000 -n hello", "what": "Forward localhost:8080 to one of the Deployment's Pods."},
    ],
    "mistake": "Pushing every release as `:latest` (or reusing the same tag). The Pod template does not change, so Kubernetes sees nothing to roll out, and the history cannot tell versions apart. Give every build a unique tag, such as the version or the git commit, and change the tag in the manifest to release.",
    "real_world": "PayLite's checkout service runs as a Deployment with 6 replicas spread over three nodes, `maxUnavailable: 0` and a readiness probe, so card payments keep flowing during a release. The CI job runs `kubectl rollout status --timeout=5m` and fails the release if the rollout stalls. The on-call rule is simple: if errors jump after a release, roll back first and investigate afterwards.",
    "task": {
        "title": "Ship hello-devops 1.1.0 with a Deployment, and roll back",
        "steps": [
            "Write `k8s/namespace.yaml`, the first `k8s/deployment.yaml` (3 replicas, `maxSurge: 1`, `maxUnavailable: 0`) and `k8s/kustomization.yaml`. Apply them with `kubectl apply -k k8s`.",
            "Look at the Deployment, ReplicaSet and Pods together, and find the `pod-template-hash` in the names and labels.",
            "In a second terminal, watch the Pods with `-w`. Delete one Pod by name and watch the replacement appear. Then scale to 5 and back to 3.",
            "Build `hello-devops:1.1.0` with `--build-arg APP_VERSION=1.1.0` and load it into the `devops` cluster.",
            "Roll out 1.1.0 with `kubectl set image` while you watch the ReplicaSets with `kubectl get rs -n hello -w` in the second terminal. Count how many Pods exist at most.",
            "Port-forward to the Deployment and confirm with `curl` that `version` is now `1.1.0`. Then read the rollout history.",
            "Roll back with `kubectl rollout undo` and confirm the version is `1.0.0` again.",
            "Now ship 1.1.0 the declarative way: change the tag in `k8s/deployment.yaml`, check `kubectl diff -k k8s`, apply, and follow `rollout status`.",
            "Set the tag back to `1.0.0` in the file, apply it, and commit the three files.",
        ],
        "hints": [
            "The container in the lab Deployment is named `web`, so `set image` needs `web=hello-devops:1.1.0`.",
            "`kubectl port-forward deployment/hello-devops 8080:8000 -n hello` picks one Pod; that is fine for checking the version.",
            "If new Pods sit in `ErrImagePull`, the 1.1.0 image is not in the cluster yet: run `kind load docker-image` again with `--name devops`.",
        ],
        "done_when": "`kubectl rollout history deployment/hello-devops -n hello` shows several revisions, `curl` through port-forward returns `version` `1.0.0`, and `k8s/deployment.yaml` in git says `1.0.0`.",
    },
    "explain_back": {
        "prompt": "Explain in 3 to 4 sentences how a Deployment rolls out a new image without downtime. Mention ReplicaSets, maxSurge or maxUnavailable, and readiness.",
        "answer": "When the Pod template changes, the Deployment creates a new ReplicaSet for the new template. It scales the new ReplicaSet up and the old one down a few Pods at a time, staying within maxSurge extra Pods and maxUnavailable missing Pods. It only removes old Pods once new ones are ready, so if the new version never becomes ready, the rollout stalls while the old Pods keep serving. The old ReplicaSet stays at zero replicas, which makes `kubectl rollout undo` quick.",
    },
    "recap": [
        "A Deployment owns ReplicaSets, and each ReplicaSet keeps N Pods of one template running.",
        "Self-healing and scaling are the same loop: count matching Pods, then fix the difference.",
        "Only changes to `spec.template` start a rollout and create a revision.",
        "maxSurge and maxUnavailable set the pace; readiness decides when each step may happen.",
        "Stuck rollouts do not roll back on their own: use `rollout status` with a timeout and `rollout undo`.",
        "Use `set image` to experiment, but make real changes in the YAML in git.",
    ],
    "check": [
        {
            "q": "A Deployment has `replicas: 4`, `maxSurge: 1` and `maxUnavailable: 0`. During a rollout, what is the largest number of Pods that can exist at once?",
            "options": ["4", "5", "6", "8"],
            "answer": 1,
            "why": "maxSurge 1 allows one Pod above the desired 4, and maxUnavailable 0 means no old Pod leaves until a new one is ready.",
        },
        {
            "q": "You run `kubectl scale deployment web --replicas=10`. What does `kubectl rollout history deployment/web` show afterwards?",
            "options": [
                "A new revision with the CHANGE-CAUSE `scale`",
                "Ten new revisions, one per Pod",
                "The same revisions as before",
                "Only revision 1, because history resets on scale",
            ],
            "answer": 2,
            "why": "Scaling changes `replicas`, not the Pod template, so no new ReplicaSet or revision is created.",
        },
        {
            "q": "A new version starts, passes no readiness probe (there is none), and then fails every real request. What happens during the rolling update?",
            "options": [
                "The rollout finishes and every Pod runs the broken version",
                "The rollout stalls after the first Pod, so users are safe",
                "Kubernetes notices the errors and rolls back by itself",
                "The Service skips the new Pods because they return errors",
            ],
            "answer": 0,
            "why": "Without a readiness probe a Pod counts as ready once its container starts, so the Deployment keeps replacing old Pods with broken ones.",
        },
    ],
    "interview": [
        {
            "q": "How does a rolling update work in Kubernetes, and how do you roll back?",
            "a": "Changing the Pod template makes the Deployment create a new ReplicaSet. It scales the new one up and the old one down within maxSurge and maxUnavailable, waiting for new Pods to be ready (and available for minReadySeconds) before going on. Old ReplicaSets are kept at zero replicas, up to revisionHistoryLimit, so `kubectl rollout undo` can scale the previous one back up. In a GitOps setup you would revert the commit instead, so git and the cluster agree.",
        },
        {
            "q": "What is the relationship between a Deployment, a ReplicaSet and a Pod?",
            "a": "A Deployment manages ReplicaSets, one per version of its Pod template, and handles rollouts and history. A ReplicaSet keeps a set number of identical Pods running by counting the Pods its selector matches and creating or deleting Pods to fix the count. Pods carry an ownerReference to their ReplicaSet and a pod-template-hash label that keeps versions apart. You normally work only with the Deployment.",
        },
        {
            "q": "When would you use the Recreate strategy instead of RollingUpdate?",
            "a": "When two versions must never run at the same time. Examples are an app that needs exclusive access to a ReadWriteOnce volume, a single-writer process, or a release that changes data in a way the old version cannot handle. Recreate stops all old Pods before starting new ones, so you accept a short outage. For stateless web services, RollingUpdate with readiness probes is almost always the better choice.",
        },
    ],
    "deeper": {
        "minutes": 12,
        "body": """How does the Deployment controller decide each step? On every pass of its loop, it works out two numbers.

The first is how many Pods may exist in total: `replicas + maxSurge`. With 10 replicas and the default 25% surge, that is 10 + 3 (2.5 rounded up) = 13. The new ReplicaSet may grow until the total of old and new Pods reaches 13.

The second is how many Pods must stay available: `replicas - maxUnavailable`. With the default 25%, that is 10 - 2 (2.5 rounded down) = 8. The old ReplicaSets may shrink only while at least 8 Pods are available.

Available is stricter than running. A Pod is available when it is ready and has stayed ready for `minReadySeconds`. So readiness, more than anything else, decides how fast a rollout moves. A rollout of a slow-starting Java service with a startup time of 40 seconds takes much longer than one of a Python service. Teams with big Deployments raise `maxSurge` to finish faster, if the nodes have room.

What if you change the template again in the middle of a rollout? The Deployment does not wait for the first rollout to finish. It creates a third ReplicaSet at once and starts scaling down both older ones. The docs call this rollover. It means a hotfix can replace a bad release that is still rolling out.

A few more fields are worth knowing by name:
- `spec.paused`: set by `kubectl rollout pause`. While paused, template changes pile up without starting a rollout. Resume, and they ship as one revision.
- `status.conditions`: `Available` and `Progressing` tell you, and your tools, how things stand. Argo CD's health check (Day 39) reads them.
- `metadata.annotations["deployment.kubernetes.io/revision"]`: the revision number on each ReplicaSet.

`kubectl rollout restart` is also a template change. It writes the current time into the annotation `kubectl.kubernetes.io/restartedAt` inside the Pod template. The template is now different, so a normal rolling update replaces every Pod. Day 34 uses this to make Pods pick up new config.

Finally, where do canary and blue-green releases fit? A Deployment cannot send 10% of traffic to a new version on purpose. During a rolling update the share of traffic simply follows the share of ready Pods. For controlled traffic shifting, teams use Argo Rollouts or Flagger, or weights on Gateway API routes (Day 36).""",
    },
    "sources": [
        {"title": "Deployments", "url": "https://kubernetes.io/docs/concepts/workloads/controllers/deployment/"},
        {"title": "ReplicaSet", "url": "https://kubernetes.io/docs/concepts/workloads/controllers/replicaset/"},
        {"title": "Performing a rolling update", "url": "https://kubernetes.io/docs/tasks/run-application/update-deployment-rolling/"},
    ],
}
