NEW = {}

NEW["goal"] = "By the end you can run hello-devops as a Deployment, explain how its ReplicaSets heal and scale it, roll a new version out step by step, and roll back when a version is bad."

NEW["opening"] = """Picture the restaurant at noon on a Saturday. A new menu is ready, and the waiters trained for it are waiting at the back door. The simplest plan is to close for an hour, send the old shift home and let the new one in. The street would remember that hour. Swapping everyone at once is no better: if the new waiters cannot find the plates, every table notices together.

Last time, we ran hello-devops in a single Pod and crashed one on purpose. We ended on the hard limit of a bare Pod: when it dies, nothing makes it again. That limit is easy to miss, because a bare Pod looks fine for days.

In this lesson, we'll hand our Pods to a manager that counts them, replaces them and changes shifts one waiter at a time. We'll ship a new version, ship a broken one on purpose and roll back. Before we start, make a guess, and keep it in mind."""

NEW["guess"] = (
    "A Deployment, the manager for a group of identical Pods, runs 4 Pods of version 1 with the default settings. You switch the image to version 2, but version 2 can never start. What do users notice?",
    "A rolling update removes old Pods only as far as maxUnavailable allows, and broken Pods never become ready, so they get no visitors. Kubernetes does not roll back by itself; the rollout waits until you fix it or run `kubectl rollout undo`.",
)

NEW["terms"] = [
    "An object that keeps a set number of identical Pods running and replaces them a few at a time when you change them.",
    "The object a Deployment creates for each version of its Pod template, to keep exactly that many of those Pods running.",
    "The number of identical Pods you want, set in `spec.replicas`.",
    "The process of moving a Deployment's Pods from one version of the Pod template to the next.",
    "A rollout that replaces old Pods with new ones a few at a time, so the app keeps answering.",
    "How many Pods above the wanted number a rolling update may create at once.",
    "How many Pods below the wanted number may be out of service during a rolling update.",
    "A numbered version of a Deployment's Pod template that you can go back to.",
]

S = []

S.append(("From one waiter to a shift manager", """
Our Pod from the last lesson had no one watching over it. Delete it and it was gone, and a dead node (one machine of the cluster) would take it along. Real apps run under a **Deployment** instead. It is the shift manager who keeps every table staffed, whoever calls in sick. You give it a Pod template, the recipe for each Pod (image, ports, settings), and a number of copies.

The Deployment does not create Pods itself. It works through a chain of objects, and each link has its own controller, a small loop that keeps that object true:
- Deployment: owns the update plan and the list of past versions.
- ReplicaSet: keeps exactly the wanted number of Pods from one template running.
- Pod: runs your container. The kubelet, the helper program on each node, looks after it.

Each object knows its owner. Delete the Deployment, and a cleanup controller removes its ReplicaSets and Pods too.

You can read the chain in the names. A Pod called `hello-devops-698679bfb-7l7h8` belongs to the ReplicaSet `hello-devops-698679bfb`, which belongs to the Deployment `hello-devops`. The middle part is a hash of the Pod template: a short code worked out from its contents, so a different template gets a different code. Kubernetes also stores it as a label, `pod-template-hash`, on the ReplicaSet and its Pods. A label is a key=value tag, and this one keeps the Pods of two versions apart. Their ReplicaSets never fight over each other's Pods.

Why two levels? A ReplicaSet knows one template and one number. An update needs the old and the new template alive at once. So the Deployment keeps one ReplicaSet per version and moves the numbers between them, like a manager with two shift lists. You will rarely touch ReplicaSets yourself.

Read the lab's `deployment.yaml` with that chain in mind. Each part of its `spec` is an input to one of the loops:
- `replicas: 3`: the number the ReplicaSet keeps.
- `selector`: how the ReplicaSet finds and counts its Pods, by label.
- `strategy`: how fast the Deployment swaps old Pods for new ones.
- `template`: the Pod to stamp out, with its own labels and containers.

The ReplicaSet's job sounds small: keep a count. Next, we see how much that one count does.
"""))

S.append(("Healing and growing are the same count", """
A ReplicaSet runs the control loop from Day 38 with one number in it. It counts the Pods that match its selector, the label question it asks, and compares the count with `replicas`. Too few, and it creates Pods. Too many, and it deletes some. Everything else follows from that:
- Delete a Pod by hand, and a new one appears within seconds, with a new name and a new IP address.
- Change `replicas` from 3 to 5, and two Pods appear. That is all scaling is.
- A container crashes, and the kubelet restarts it in place. The Pod still exists, so the ReplicaSet does nothing.

A dead node takes longer than you might expect. The node stops reporting, and Kubernetes marks it not ready. By default, its Pods stay bound to it for five more minutes, in case the node comes back. Only then are they evicted (removed from the node), and the ReplicaSet creates replacements on healthy nodes. A manager does not hire a new waiter the moment one is late. So spread replicas over several nodes, and do not expect instant failover, the switch to a healthy copy.

The count uses labels, not names. Remove the `app` label from one running Pod, and the ReplicaSet no longer counts it. It creates a replacement, while the relabelled Pod keeps running with no owner. That is handy for pulling a Pod aside to debug it, and confusing when it happens by accident. For the same reason, a Deployment's `selector` cannot be changed after creation.

Scaling never changes the version. So what does? Next, we find the one change that starts a new shift.
"""))

S.append(("What counts as a new version", """
A rollout happens if, and only if, you change the Pod template: anything under `spec.template`. These all start one:
- A new image tag, the everyday case. A tag is the version label after the colon, such as `1.1.0`.
- A changed environment variable (a named setting the app reads), port, probe or resource setting.
- A new label or annotation inside the template.

These do not:
- Changing `replicas`. Scaling is not a new version.
- Changing labels or annotations on the Deployment itself, outside the template.
- Changing a ConfigMap (an object of settings) that the Pods read. The template did not change, so nothing rolls (Day 42 shows the fix).

That rule explains a common surprise. Say a team pushes every release as `:latest`, or reuses one tag. The Pod template does not change, so Kubernetes sees nothing to roll out, and the history cannot tell versions apart. Give every build a unique tag, such as the version or the Git commit, and change the tag in the manifest to release.

The Deployment controller spots a new version like this. On each pass, it compares `spec.template` with the template inside each ReplicaSet it owns. If none matches, it creates a new ReplicaSet and moves Pods from the old one to the new one. The old ReplicaSet is not deleted. It stays, scaled to 0, as a record of that version, and that record makes rollback fast. By default the Deployment keeps the last 10 old ReplicaSets, set by `revisionHistoryLimit`.

To know before you apply whether a change will roll, run `kubectl diff -k k8s`. The `-k k8s` means every file listed in `k8s/kustomization.yaml`, a list of the app's files (Day 45 explains Kustomize, the tool behind it). If the diff touches lines under `template:`, expect new Pods.

Each ReplicaSet gets a revision number in an annotation. `kubectl rollout history` lists them. Only template changes create revisions, so the history stays a clean list of versions you shipped. Next, we watch one of those changes roll.
"""))

S.append(("Changing shifts one waiter at a time", """
A careful manager changes shifts like this. One new waiter comes in. When they are ready, one old waiter goes home. Repeat until the whole floor is new. The default strategy, `RollingUpdate`, works the same way. Two settings control its pace:
- `maxSurge`: how many extra Pods may exist above `replicas` during the update.
- `maxUnavailable`: how many Pods may be missing below `replicas`.

Both default to 25%. Percentages are turned into whole Pods: surge rounds up, unavailable rounds down. With 4 replicas, that is 1 extra and 1 missing. So during the update you have at least 3 available Pods and at most 5 Pods in total. Both cannot be 0, or nothing could ever move. The rounding is on the safe side: you never lose more Pods than the percentage says, and even a single replica gets one extra Pod to move with.

The lab picks `maxSurge: 1` and `maxUnavailable: 0` for its 3 replicas. In words: add one new Pod, wait until it is ready, then remove one old Pod. Here is the whole update:
1. The new ReplicaSet scales to 1. There are 4 Pods: 3 old, 1 new.
2. The new Pod becomes ready. The old ReplicaSet scales to 2.
3. The new ReplicaSet scales to 2, and waits for that Pod to be ready.
4. The old ReplicaSet scales to 1, the new one to 3, and finally the old one to 0.

You never have fewer than 3 ready Pods. The price is speed and room: one extra Pod at a time needs spare CPU (computing power) and memory on some node. With a big Deployment, a larger surge such as 25% finishes faster.

During the update, both versions serve visitors at once. A Service, the fixed address in front of the Pods (Day 41), sends requests to every ready Pod with the right label, old or new. So version 2 must work alongside version 1. For example, both must understand the same database layout.

Every step above waited for one word: ready. Next, we look at who decides that.
"""))

S.append(("Ready means ready: what each step waits for", """
A rolling update is safe only because each step waits for a new Pod to be ready. A Pod is ready when all its containers are running and pass their readiness checks. Day 43 adds a readiness probe to hello-devops: a web address that the kubelet calls every few seconds to ask "can you take visitors?". The kubelet writes each answer into the Pod's status, and the controllers read it there before each step.

Without a readiness probe, a Pod counts as ready as soon as its container starts. It is a new waiter who counts as ready the moment they walk in, apron or not. The app may still be loading, or broken in a way that only shows on the first request. The Deployment cannot tell, and it moves on.

**A Deployment is only as careful as its readiness check. Add one before you trust rolling updates.**

When new Pods never become ready, because of a bad image or a crash at start, the rollout stalls:
- The old Pods keep serving. With `maxUnavailable: 0`, none of them is removed.
- After `progressDeadlineSeconds` (600 seconds by default), the Deployment reports the condition `ProgressDeadlineExceeded`.
- `kubectl rollout status` then exits with an error, so a CI job (the automatic checks that run on every change) can notice and act.
- Kubernetes does not roll back on its own. You fix the image or run `kubectl rollout undo`.

That is the answer to the guess. For hello-devops, a version that crashes on start never becomes ready, and you get the stuck rollout from the worked example. A version that starts but answers every request with an error is worse. Without a probe it looks ready, and the rollout completes.

`minReadySeconds` adds one more guard. A new Pod must stay ready for that many seconds before it counts as available. That catches apps that start fine and crash a few seconds later.

Picture a payments team whose checkout service runs 6 replicas over three nodes, with `maxUnavailable: 0` and a readiness probe. Its CI job runs `kubectl rollout status --timeout=5m` and fails the release if the rollout stalls. The rule for the person on call is short: if errors jump after a release, roll back first and investigate afterwards. Next, we learn how to do exactly that.
"""))

S.append(("Old menus in the drawer: history and undo", """
A good manager keeps last month's menu in a drawer, in case the new one flops. Four `kubectl rollout` subcommands open that drawer, and they cover most days:
- `rollout status`: follow the rollout until it finishes or fails.
- `rollout history`: list the revisions. Add `--revision=2` to see one template in full.
- `rollout undo`: go back to the previous revision, or to any kept revision with `--to-revision=N`.
- `rollout pause` and `rollout resume`: batch several changes into one rollout.

The CHANGE-CAUSE column in the history is empty unless you set the annotation `kubernetes.io/change-cause` on the Deployment, for example with `kubectl annotate`. Teams that use it write the ticket number or the reason.

An undo is itself a rollout. Kubernetes copies the old template back, and the old revision moves to a new number. Revision 2 disappears from the list and comes back as revision 4. It surprises everyone the first time, and the worked example shows it happening.

There are two ways to change the image, and they look the same for a minute:
- `kubectl set image deployment/hello-devops web=hello-devops:1.1.0` changes the live object. Quick, and good for experiments.
- Edit `image:` in `k8s/deployment.yaml` and apply the file. Slower, but Git now records the change, and someone can review it.

Mixing them causes drift (Day 33): the cluster no longer matches the file. The next `kubectl apply` of an old file quietly undoes your `set image`. From Day 47, Argo CD, a tool that keeps the cluster in line with Git, undoes it within minutes. Experiment with `set image`, then make the real change in the file.

Rolling updates fit almost every app. Next, we meet the one strategy for apps they do not fit.
"""))

S.append(("Closing for an hour: the Recreate strategy", """
Sometimes a restaurant must close to repaint the dining room, because guests and wet paint cannot share a room. The other Deployment strategy, `Recreate`, is that closing. It stops every old Pod first, and only then starts the new ones. There is always a gap with no Pods at all, so users see downtime: minutes when the app does not answer.

That sounds bad, and for most web apps it is. Recreate exists for apps where two versions running side by side would be worse than a short outage:
- The app holds an exclusive lock, such as a single writer to a file or a queue (a waiting line of jobs).
- Its Pods use a disk that only one Pod can attach at a time (a ReadWriteOnce volume, Day 44).
- The new version changes the database in a way the old version cannot handle.

For hello-devops, a rolling update is right. The app is stateless: it keeps nothing it needs inside the Pod. Redis, a small database, holds the shared counter, so any number of versions can run side by side. This matters because a new Pod starts with nothing. A new waiter can read yesterday's notes in the office; a new Pod has no notes at all. Anything worth keeping must live outside it.

Rolling update and Recreate are the only two strategies a Deployment has. Canary and blue-green releases need extra tools. A canary shifts visitors to the new version a little at a time, and blue-green flips all of them at once. Argo Rollouts can do both, and so can traffic rules at a Gateway, the cluster's front entrance (Day 44). Now the worked example puts all of this to work.
"""))

NEW["sections"] = S

NEW["drop"] = ["analogy", "real_world", "mistake"]

NEW["diagram_caption"] = "During a rollout the Deployment scales the new ReplicaSet up and the old one down. The Service sends visitors to ready Pods of both versions."

NEW["worked"] = [
    "In the scratch namespace, create a Deployment of nginx 1.27 (a ready-made web server, handy for tests) with 4 replicas. One ReplicaSet appears, named after the Deployment plus the template hash.",
    "Change the image. `kubectl create deployment` named the container after the image, so it is `nginx`. Follow the rollout: with the defaults for 4 replicas (1 extra, 1 missing), two new Pods start at once. One fills the extra slot, and one replaces the old Pod that may go missing.",
    "Two ReplicaSets now exist. The old one is kept at 0 for rollback. Record why you made the change, then look at the history.",
    "Now ship a tag that does not exist. The new Pods cannot pull (download) their image. The Deployment removed only one old Pod (maxUnavailable is 1), so three old Pods keep serving.",
    "`rollout status` with a timeout fails instead of waiting forever, which is what a CI job wants. Kubernetes will not fix this by itself, so roll back.",
    "Read the history once more. Revision 2 moved to the new number 4, because the undo copied its template back as a new rollout. Delete the Deployment when you are done; its ReplicaSets and Pods go with it.",
]

NEW["task"] = (
    [
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
    [
        "The container in the lab Deployment is named `web`, so `set image` needs `web=hello-devops:1.1.0`.",
        "`kubectl port-forward deployment/hello-devops 8080:8000 -n hello` picks one Pod; that is fine for checking the version.",
        "If new Pods sit in `ErrImagePull`, the 1.1.0 image is not in the cluster yet: run `kind load docker-image` again with `--name devops`.",
    ],
    "`kubectl rollout history deployment/hello-devops -n hello` shows several revisions, `curl` through port-forward returns `version` `1.0.0`, and `k8s/deployment.yaml` in git says `1.0.0`.",
)

NEW["explain_back"] = (
    "Explain in 3 to 4 sentences how a Deployment rolls out a new image without downtime. Mention ReplicaSets, maxSurge or maxUnavailable, and readiness.",
    "When the Pod template changes, the Deployment creates a new ReplicaSet for the new template. It scales the new ReplicaSet up and the old one down a few Pods at a time, staying within maxSurge extra Pods and maxUnavailable missing Pods. It removes old Pods only once new ones are ready, so if the new version never becomes ready, the rollout stalls while the old Pods keep serving. The old ReplicaSet stays at zero replicas, which makes `kubectl rollout undo` quick.",
)

NEW["recap"] = [
    "A Deployment owns ReplicaSets, and each ReplicaSet keeps a set number of Pods of one template running.",
    "Healing and scaling are the same loop: count matching Pods, then fix the difference.",
    "Only changes to `spec.template` start a rollout and create a revision.",
    "maxSurge and maxUnavailable set the pace; readiness decides when each step may happen.",
    "The limit: stuck rollouts never roll back on their own, so use `rollout status` with a timeout and `rollout undo`.",
    "Use `set image` to experiment, but make real changes in the YAML in git.",
]

NEW["closing"] = """We started with a Saturday menu change and two bad plans: close the doors, or swap everyone at once. A Deployment does neither. It brings in one new Pod, waits until it is ready, sends one old Pod home, and keeps the old menu in the drawer. In the task, watch the ReplicaSets during the rollout and count the Pods at their highest; the number should match what maxSurge allows. Our three Pods still have three different addresses, though, and each new Pod gets a new one. Next, we'll give them one fixed address. How do visitors find Pods that keep moving?"""

NEW["check"] = [
    ("A Deployment has `replicas: 4`, `maxSurge: 1` and `maxUnavailable: 0`. During a rollout, what is the largest number of Pods that can exist at once?",
     "maxSurge 1 allows one Pod above the wanted 4, and maxUnavailable 0 means no old Pod leaves until a new one is ready."),
    ("You run `kubectl scale deployment web --replicas=10`. What does `kubectl rollout history deployment/web` show afterwards?",
     "Scaling changes `replicas`, not the Pod template, so no new ReplicaSet or revision is created."),
    ("A new version starts, has no readiness probe, and then fails every real request. What happens during the rolling update?",
     "Without a readiness probe a Pod counts as ready once its container starts, so the Deployment keeps replacing old Pods with broken ones."),
]

NEW["interview"] = [
    ("How does a rolling update work in Kubernetes, and how do you roll back?",
     "Changing the Pod template makes the Deployment create a new ReplicaSet. It scales the new one up and the old one down within maxSurge and maxUnavailable, waiting for new Pods to be ready (and available for minReadySeconds) before going on. Old ReplicaSets are kept at zero replicas, up to revisionHistoryLimit, so `kubectl rollout undo` can scale the previous one back up. In a GitOps setup you would revert the commit instead, so git and the cluster agree."),
    ("What is the relationship between a Deployment, a ReplicaSet and a Pod?",
     "A Deployment manages ReplicaSets, one per version of its Pod template, and handles rollouts and history. A ReplicaSet keeps a set number of identical Pods running by counting the Pods its selector matches and creating or deleting Pods to fix the count. Pods carry an ownerReference to their ReplicaSet and a pod-template-hash label that keeps versions apart. You normally work only with the Deployment."),
    ("When would you use the Recreate strategy instead of RollingUpdate?",
     "When two versions must never run at the same time. Examples are an app that needs sole access to a ReadWriteOnce volume, a single-writer process, or a release that changes data in a way the old version cannot handle. Recreate stops all old Pods before starting new ones, so you accept a short outage. For stateless web services, RollingUpdate with readiness probes is almost always the better choice."),
]

NEW["deeper"] = """
On every pass of its loop, the Deployment controller works out two numbers, and they decide each step.

The first is how many Pods may exist in total: `replicas + maxSurge`. With 10 replicas and the default 25% surge, that is 10 + 3 (2.5 rounded up) = 13. The new ReplicaSet may grow until the total of old and new Pods reaches 13.

The second is how many Pods must stay available: `replicas - maxUnavailable`. With the default 25%, that is 10 - 2 (2.5 rounded down) = 8. The old ReplicaSets may shrink only while at least 8 Pods are available.

Available is stricter than running. A Pod is available when it is ready and has stayed ready for `minReadySeconds`. So readiness, more than anything else, decides how fast a rollout moves. A rollout of a slow-starting Java service with a startup time of 40 seconds takes much longer than one of a Python service. Teams with big Deployments raise `maxSurge` to finish faster, if the nodes have room.

What if you change the template again in the middle of a rollout? The Deployment does not wait for the first rollout to finish. It creates a third ReplicaSet at once and starts scaling down both older ones. The docs call this rollover. It means a hotfix can replace a bad release that is still rolling out.

The owner chain from the first section is stored in each object. A Pod points to its ReplicaSet in `metadata.ownerReferences`, and the garbage collector (one more controller) deletes what an owner leaves behind. `kubectl get pod NAME -o jsonpath='{.metadata.ownerReferences[0].name}'` prints the ReplicaSet that owns a Pod.

You will also meet three fields by name:
- `spec.paused`: set by `kubectl rollout pause`. While paused, template changes pile up without starting a rollout. Resume, and they ship as one revision.
- `status.conditions`: `Available` and `Progressing` tell you, and your tools, how things stand. Argo CD's health check (Day 47) reads them.
- `metadata.annotations["deployment.kubernetes.io/revision"]`: the revision number on each ReplicaSet.

`kubectl rollout restart` is also a template change. It writes the current time into the annotation `kubectl.kubernetes.io/restartedAt` inside the Pod template. The template is now different, so a normal rolling update replaces every Pod. Day 42 uses this to make Pods pick up new config.

Finally, a Deployment cannot send 10% of visitors to a new version on purpose. During a rolling update the share of traffic follows the share of ready Pods. For controlled traffic shifting, teams use Argo Rollouts or Flagger, or weights on Gateway API routes (Day 44).
"""
