NEW = {}

NEW["goal"] = "By the end you can read and generate a Pod manifest, run your own image in a Pod on kind, explain its phase and restarts, and use the everyday kubectl commands to inspect, reach and remove it."

NEW["opening"] = """Picture your first evening as a waiter. You scribble an order on a ticket, pin it on the rail and hurry off. A minute later the cook hands it back. You wrote "sup" instead of "soup", and this kitchen cooks only what the ticket says, exactly. It feels fussy. But a kitchen that guessed would sometimes guess wrong, and nobody would find out until the plate reached the table.

Last time, we met the cluster's ticket rail, the API server, and the small loops that keep making each ticket come true. We never wrote a ticket ourselves. This is where many newcomers stall: the ideas make sense, and then a blank file and a strict format stand in the way.

In this lesson, we'll write our first tickets, run hello-devops in the smallest thing Kubernetes runs, crash one on purpose and learn the dozen commands you'll use every day. Before we start, make a guess, and keep it in mind."""

NEW["guess"] = (
    "Soon you'll meet a Pod, the box Kubernetes runs your app in. Its STATUS column shows `CrashLoopBackOff`. What is the Pod's phase, the value Kubernetes stores in `status.phase`?",
    "`CrashLoopBackOff` is a word kubectl shows for a container that keeps crashing, with a longer wait before each restart. The phase stays `Running`, because the Pod is on a node and the kubelet keeps restarting its container.",
)

NEW["terms"] = [
    "The smallest thing Kubernetes runs: one or more containers that share one address and can share files.",
    "A YAML file that describes one object, with the fields apiVersion, kind, metadata and spec.",
    "A container that runs to the end and must succeed before the app containers in its Pod start.",
    "A helper container that starts before the app container and runs beside it for the Pod's whole life.",
    "A key=value tag on an object, such as app=web, that Kubernetes uses to find the object.",
    "A key=value note on an object for people and tools, which Kubernetes never uses to find objects.",
    "A named group of objects inside a cluster, like a folder, in which every name must be unique.",
    "A saved choice of cluster, user and default namespace that kubectl sends its commands to.",
]

S = []

S.append(("Writing a ticket the kitchen can read", """
A manifest is how you write down one of the objects Kubernetes stores. It is a file in YAML, a plain text format where each line holds a name, a colon and a value. Indentation (spaces at the start of a line) shows what belongs inside what. You hand the file to kubectl, and kubectl sends it to the API server.

Pods, Services and Namespaces are all objects. Every manifest for them starts with the same four fields, much as every order ticket has the same boxes to fill in:
- `apiVersion`: which version of the rules defines this kind of object. The API server checks your fields against it. A Pod is `v1`, a Deployment is `apps/v1`.
- `kind`: the type of object, such as `Pod` or `Service`. It decides which controllers act on it.
- `metadata`: who the object is. The `name` and `namespace`, plus `labels` and `annotations`.
- `spec`: your desired state, the part the controllers read. Its shape depends on the kind.

You never write the fifth field, `status`. The controllers and the kubelet write it, to report what is really there. Any gap between `spec` and `status` is work the cluster has not finished yet.

Like our strict cook, kubectl catches spelling mistakes in field names before anything is stored. It checks strictly by default. A field written as `imagePullPolicyy`, with one letter too many, fails with an error that names the unknown field. That is annoying for a second and a gift for the rest of the day.

Writing every field from memory would be slow and full of such mistakes. Next, we'll get the computer to write the first draft.
"""))

S.append(("Copying a ticket instead of writing one, and YAML's traps", """
Nobody types manifests from memory. On a busy team, people copy a template from the team's repo (the shared project folder in Git) and change it. Three tricks give you a good first draft:
1. `--dry-run=client -o yaml` prints the object kubectl would create, without creating it. Add `> pod.yaml` to save that output to a file, then edit the file.
2. `kubectl explain pod.spec.restartPolicy` prints the docs for one field, straight from your cluster, so they always match your version. For this field it shows the type (`<string>`, meaning text), the allowed values `Always`, `Never` and `OnFailure`, and a description. Add `--recursive` to see a whole tree of fields.
3. `kubectl get pod hello -o yaml` shows a live object in full. It is longer than what you wrote, because the API server fills in defaults and `status`.

YAML has traps of its own:
- Indent with spaces, never tabs.
- A line that starts with `- ` is one item in a list. `containers:` is a list even when it holds one container.
- Some bare words change type. `yes` and `on` can turn into true, and `8000` becomes a number.

That last trap bites with environment variables, the named settings a program reads when it starts. Their values must be text (a string). So `8000` without quotes is refused, and `"8000"` in quotes works.

Those traps are the reason for KYAML, which Kubernetes 1.37 made stable. KYAML is a stricter style of YAML that quotes every string and uses brackets, so indentation cannot break it. It is still valid YAML. Try `kubectl get pod hello -o kyaml` once you have a Pod.

We keep saying Pod. It is time to look at what one is.
"""))

S.append(("Pods: the smallest thing Kubernetes runs", """
Back in the restaurant, a waiter carries a tray to one table. The tray may hold a main dish and a side, but they always travel together and land on the same table. A **Pod** is that tray. It is one or more containers that Kubernetes places on one node together. They share three things:
- One IP address and one set of ports. Containers in a Pod reach each other on `localhost`, the name a machine uses for itself.
- Volumes, if the Pod defines them. A volume is a folder that the Pod's containers can all read and write.
- One life. They start on the same node and are removed together.

Most Pods hold exactly one container. The Pod is then a thin wrapper that gives the container an address and a place in the cluster. Inside the Pod, the host name (the name a machine calls itself) is the Pod's name. So the `host` field in hello-devops' answer will show the Pod's name.

The wrapper matters for helpers that only work right next to the app. One example is a proxy, a program that sits in front of the app and passes requests to it on `localhost`. Another is a log shipper, which reads the app's log files and sends them to a central place. The Pod keeps such a group together, and the scheduler places the whole Pod on one node.

Pods are also disposable. The kubelet restarts a bare Pod's containers (a Pod you made yourself, with no controller), but no controller counts bare Pods or makes new ones. If a node dies, its Pods die with it, and nothing brings them back. Delete a Pod and it is gone. A new Pod made from the same YAML is a different Pod, with a new IP address.

So you rarely create Pods yourself. You create a controller, usually a Deployment (Day 40), and it creates and replaces Pods for you. Today we make bare Pods anyway, because that is the clearest way to see one. Next, we follow a Pod through its life.
"""))

S.append(("A Pod's life: phases, states and restarts", """
A Pod's life is summed up in one field, `status.phase`. It has only five values:
- `Pending`: accepted, but not running yet. It may be waiting for a node or pulling an image.
- `Running`: on a node, containers created, at least one running or restarting.
- `Succeeded`: all containers exited with code 0 and will not restart.
- `Failed`: all containers have stopped, and at least one failed.
- `Unknown`: the node stopped reporting, so nobody knows.

An exit code is the number a program leaves behind when it stops: 0 means all went well, and anything else means trouble. A normal start shows up in the STATUS column as `Pending` (no node yet), then `ContainerCreating`, then `Running`. During `ContainerCreating` the node is chosen and the image is being pulled, but the phase is still `Pending`.

Each container also has a state of its own: `Waiting`, `Running` or `Terminated`. The state comes with a reason, such as `ImagePullBackOff` or `Completed`. The STATUS column of `kubectl get pods` squeezes all of this into one word. Remember the guess? `CrashLoopBackOff` and `Terminating` show up in STATUS, but they are not phases. When STATUS looks odd, read `kubectl describe pod`, which lists the phase and each container's state separately.

What happens when a container stops depends on the Pod's `restartPolicy`:
- `Always` (the default): restart it, whatever the exit code. Right for servers.
- `OnFailure`: restart it only after a non-zero exit code. Right for batch work, jobs that run once and finish.
- `Never`: leave it stopped.

The kubelet restarts the container inside the same Pod, on the same node. It waits longer each time: 10 seconds, then 20, then 40, up to five minutes. That growing wait is the back-off in `CrashLoopBackOff`. If the container then runs for ten minutes without trouble, the wait resets.

So far each Pod held one container. Next, we give it helpers.
"""))

S.append(("Helpers in the Pod: init containers and sidecars", """
Before a cook starts, a prep cook may chop the onions and lay out the plates, then leave. Meanwhile a runner arrives early, stays all evening and leaves only after the last dish is out. A Pod can hold the same two kinds of helper.

Init containers are the prep cooks. They run first, one at a time, in order. Each must exit with code 0 before the next one starts. Only when all of them have finished do the app containers start. Use them for setup work:
- Wait until a database answers.
- Download or fill in a config file and put it in a shared volume.
- Fix file permissions on a volume (who may read or change its files).

A sidecar is the runner: a helper that runs beside your app for the Pod's whole life. Typical sidecars ship logs or add encryption (TLS) in front of the app. Native sidecars have been stable since Kubernetes 1.33. You declare one as an init container with `restartPolicy: Always`. The init list already starts containers in order, before the app, and that is the order a sidecar needs. For an entry with that policy, Kubernetes:
1. Starts it in init order, before the app containers.
2. Moves on as soon as it is running, without waiting for it to exit.
3. Restarts it if it crashes.
4. Stops it only after the app containers have stopped.

That order fixes two old problems. A log shipper that started late missed the first lines, and one that stopped early lost the last ones. The READY column of kubectl counts sidecars too, so a Pod with one sidecar and one app shows `2/2`.

An app and its database belong in separate Pods. Then you can scale and replace each one on its own.

**Share a Pod only when you must share a node, an address or files.**

A Pod with several helpers raises a new question: how do other objects find the right Pods? Next, we put stickers on them.
"""))

S.append(("Stickers on the plates: labels and selectors", """
A busy kitchen puts colored stickers on plates: green for vegetarian, red for table 4. Then anyone can ask for "every plate with a green sticker" without knowing which plate is which. Labels are those stickers, and they are how Kubernetes objects find each other.

A label is a key=value pair in `metadata.labels`, such as `app: hello-devops` or `tier: frontend`. A selector is a question asked over labels. Deployments find their Pods with selectors. So do Services, which give a group of Pods one fixed address, and NetworkPolicies, which say which Pods may talk to which (both on Day 41).

Why not use names? Controllers replace Pods all the time, and every replacement gets a new name. A selector is a question the controller asks again on every pass of its loop: which objects carry these labels right now?

You use selectors with kubectl too:
- `kubectl get pods -l app=web` matches one label exactly.
- `kubectl get pods -l 'app=web,tier!=db'` combines rules, and all must hold.
- `kubectl get pods -l 'env in (dev,test)'` matches a set of values.
- `kubectl get pods --show-labels` prints every label, and `-L app` adds one label as a column.

Annotations look the same but have a different job. They hold notes for people and tools, and selectors ignore them. Go deeper, at the end of this lesson, lists three you will meet soon.

A simple test: if you will ever select by it, make it a label. If it is long, or only a tool reads it, make it an annotation. Kubernetes also recommends a shared set of labels, such as `app.kubernetes.io/name`, that many tools understand.

Next, we look at the rooms, and at which restaurant kubectl is phoning.
"""))

S.append(("Dining rooms and phone numbers: namespaces and contexts", """
A big restaurant may have several dining rooms, and each room can have its own table 4. A namespace is one of those rooms: a named group of objects inside one cluster. Names must be unique inside a namespace, not across the whole cluster. A new cluster starts with four:
- `default`: where objects go when you name no namespace.
- `kube-system`: the cluster's own parts, such as CoreDNS.
- `kube-public` and `kube-node-lease`: used by the system. Leave them alone.

Namespaces group names the way folders group files. They do not wall off the network, though. A Pod in one namespace can still reach a Pod in another, and blocking that takes a NetworkPolicy (Day 41). Teams attach access rules and quotas (limits on how much a team may use) to namespaces. Deleting a namespace deletes everything in it, which makes cleanup easy and mistakes expensive.

Which cluster does kubectl talk to? It reads a kubeconfig file, `~/.kube/config` by default. You can also list other files in the `KUBECONFIG` environment variable. The file has three lists:
- clusters: each API server's address and certificate (a file that proves the server is the real one).
- users: your credentials.
- contexts: a cluster plus a user plus a default namespace, under one name.

One context is current, and every kubectl command goes there. It is the restaurant you are phoning. Picture placing a large order and only then hearing the wrong branch answer. Docker Desktop can run its own Kubernetes with a context called `docker-desktop`, and at work you will have contexts for real clusters in the same file. One `kubectl delete` can then land somewhere you did not mean.

`kubectl config get-contexts` lists every context and marks the current one with a star. Before anything that changes or deletes, run `kubectl config current-context`, because the current one is not always the one you think. Give production contexts names that stand out. To stop typing `-n hello` on every command, set a default namespace with `kubectl config set-context --current --namespace=hello`.

We know where our commands go. Last, we learn the commands themselves, and get our own image into the cluster.
"""))

S.append(("Everyday kubectl, and getting your image into kind", """
You need about a dozen kubectl commands on a normal day, and each one answers a question:
- What is there? `kubectl get pods`. Add `-o wide` for IPs and nodes, `-w` to keep watching, `-l` to filter by label, `-A` for all namespaces.
- What happened? `kubectl describe pod hello` shows details, with recent Events at the bottom. Read the Events first.
- What did it print? `kubectl logs hello`. Add `-f` to follow, `-c` to pick a container, and `--previous` for the last crashed run.
- Let me in: `kubectl exec -it hello -- sh` opens a shell inside the container, if the image has one. A shell is a text window where you type commands.
- Let me reach it: `kubectl port-forward pod/hello 8000:8000` tunnels a port on your Mac to the Pod until you press Ctrl+C.
- Remove it: `kubectl delete pod hello`, or `kubectl delete -f pod.yaml`.
- Just one field, please: `-o jsonpath='{.status.phase}'` prints a single value, which is handy in scripts.

`kubectl create -f` and `kubectl apply -f` both make objects from a file, but they think differently. The `create` command is a one-time order, and it fails if the object already exists. The `apply` command is declarative: it creates the object or updates it to match the file, so you can run it again and again. Use `apply` for anything you keep in Git.

Your own image needs one more step. Each kind node runs its own containerd with its own store of images, separate from Docker on your Mac. So `docker build` alone is not enough. Copy it in with `kind load docker-image hello-devops:1.0.0 --name devops`.

Give the image a real tag, the version label after the colon. A `:latest` tag, or no tag, can point at a different image any day. So Kubernetes sets `imagePullPolicy: Always` and asks the registry, the online store for images, on every start. Your image exists only inside kind, so the pull from Docker Hub fails and the Pod ends in `ImagePullBackOff`. With any other tag the default is `IfNotPresent`: use the node's copy if there is one.

The worked example below uses several of them on a Pod with helpers.
"""))

NEW["sections"] = S

NEW["drop"] = ["analogy", "real_world", "mistake"]

NEW["diagram_caption"] = "Init containers finish first, the sidecar starts next and keeps running, then the app starts. All of them share the Pod's IP address and volumes."

NEW["worked"] = [
    "Make a scratch namespace for experiments, so cleanup is one command later. Apply the example Pod from the lab repo. It has an init container that writes a web page, a sidecar that follows the access log (the file where nginx notes every visit), and nginx, a web server.",
    "Watch the Pod start. `Init:0/2` means the first of two init containers is running. When it finishes, the sidecar starts and counts as ready (`1/2`) while nginx is still being created. Then nginx starts and READY becomes `2/2`, because READY counts the sidecar.",
    "Ask nginx for its page from inside the Pod. Because the Pod has three containers, say which one with `-c`. The page is the file the init container wrote into the shared volume before nginx existed.",
    "Next, ask for a page that does not exist and read the sidecar's logs. Both requests went into `access.log` in the shared volume, and the sidecar printed them.",
    "Look at how kubectl sees the Pod as data. The labels and the annotation from the manifest are there, plus everything Kubernetes added. KYAML quotes every string, so a value like `on` can never turn into true by accident.",
    "Clean up. Deleting the file's objects removes the Pod. Keep the `scratch` namespace; you will use it again.",
]

NEW["task"] = (
    [
        "In `~/code/hello-devops`, build the image with its version baked in: `docker build --build-arg APP_VERSION=1.0.0 -t hello-devops:1.0.0 .` Then load it into the `devops` cluster.",
        "Generate `pod.yaml` for a Pod named `hello` with `--dry-run=client -o yaml`. Change its label to `app: hello`, add `imagePullPolicy: IfNotPresent`, and delete `resources: {}` and `status: {}` (empty placeholders; `status` is the cluster's to write). Apply it.",
        "Check the Pod with `-o wide`. Which worker did the scheduler pick, and what IP did the Pod get?",
        "Port-forward port 8000 to the Pod and `curl localhost:8000` from a second terminal. Follow the logs in a third terminal and watch each request appear.",
        "Open a shell in the Pod and run `hostname` and `printenv APP_VERSION`. Why does the `host` field in the JSON show `hello`?",
        "Start a Pod that crashes: `kubectl run crashy --image=busybox:1.37 -- sh -c \"echo starting; sleep 3; exit 1\"`. Watch it for two minutes with `-w`. How do STATUS and RESTARTS change?",
        "Read the crashed run's output with `logs --previous`, and print the Pod's phase with a jsonpath query.",
        "Repeat with `--restart=Never` and the name `once`. What are its STATUS and phase now, and why?",
        "Delete all three Pods. Keep `pod.yaml` out of git (it was practice); the cluster stays for tomorrow.",
    ],
    [
        "`kubectl get pod crashy -o jsonpath='{.status.phase}'` prints only the phase.",
        "If `kind load` fails with `content digest ... not found`, Docker is using its containerd image store. Save the image with `docker image save --platform linux/arm64 -o hello.tar hello-devops:1.0.0`, then run `kind load image-archive hello.tar --name devops`.",
        "Pod stuck in `ErrImagePull`? Check the tag, `imagePullPolicy`, and that you loaded the image into the `devops` cluster, not another one.",
    ],
    "With port-forward running, `curl localhost:8000` returns JSON with `host` `hello` and `version` `1.0.0`, and you can name the phase of `crashy` (Running) and of `once` (Failed).",
)

NEW["explain_back"] = (
    "Explain in 3 to 4 sentences what a Pod is and why you rarely create one by hand. Mention the shared IP address, init containers or sidecars, and what happens when a node dies.",
    "A Pod is the smallest thing Kubernetes runs: one or more containers on one node that share an IP address and can share volumes. Most Pods have one container, and helpers come as init containers that finish before the app starts or sidecars that run beside it. Pods are disposable: if a node dies, its bare Pods are gone, and nothing makes them again. That is why you normally let a controller such as a Deployment create and replace Pods for you.",
)

NEW["recap"] = [
    "A manifest has apiVersion, kind, metadata and spec; Kubernetes adds status.",
    "Generate YAML with `--dry-run=client -o yaml` and look up fields with `kubectl explain`.",
    "A Pod is one or more containers with one IP address; the limit is that nothing replaces a bare Pod when it dies.",
    "Phase is one of five values; `CrashLoopBackOff` is a container state shown in STATUS, not a phase.",
    "Init containers run first and must succeed; sidecars are init containers with `restartPolicy: Always`.",
    "Labels are for selecting, annotations are notes, and the current context decides which cluster kubectl changes.",
]

NEW["closing"] = """We started with a cook who handed back a ticket that said "sup". By now that strictness should feel like a friend: kubectl refuses the misspelled field, KYAML refuses the sneaky `on`, and `describe` tells you what really happened. When you run the task, look at the RESTARTS column of `crashy` and watch the gaps between restarts grow. The limit is plain, though: a bare Pod that dies stays dead. Next, we'll hand our Pods to a manager that counts them, replaces them and swaps versions without a pause. How do you change every copy of an app while visitors keep arriving?"""

NEW["check"] = [
    ("A Pod has two init containers and one app container. The second init container exits with code 1. What do you expect?",
     "App containers start only after every init container exits with 0; with the default restart policy, the kubelet keeps retrying the failed init container."),
    ("You want a log shipper that starts before your app and is still running when the app writes its last lines on shutdown. How do you declare it?",
     "A native sidecar is an init container with `restartPolicy: Always`, which Kubernetes starts before the app containers and stops after them."),
    ("`kubectl get pods` shows nothing, but a teammate is sure their Pod is running. They use the namespace `payments`. What do you run first?",
     "Without `-n`, kubectl looks only in the current context's default namespace, so you must ask for the right namespace (or use `-A`)."),
]

NEW["interview"] = [
    ("What is a Pod, and why does Kubernetes not just run containers?",
     "A Pod is a group of one or more containers that are scheduled together on one node and share a network namespace and volumes. It gives closely tied helpers, such as a log shipper or a proxy, a way to run next to the app with the same IP address and shared files. It also gives Kubernetes one unit to schedule, track and replace. In practice most Pods have one container and are managed by a controller such as a Deployment."),
    ("What is the difference between an init container and a sidecar container?",
     "An init container runs to the end before the app containers start, in order, and must exit with code 0; it is for setup work. A sidecar runs for the Pod's whole life beside the app. Native sidecars have been stable since Kubernetes 1.33. You declare them as init containers with `restartPolicy: Always`. They start before the app, are restarted if they crash, and stop after the app. That order avoids losing logs or proxy traffic at start-up and shutdown."),
    ("What is the difference between kubectl create and kubectl apply?",
     "The `kubectl create` command is imperative: it creates the object and fails if it already exists. The `kubectl apply` command is declarative. It creates the object if needed, or updates it to match the file. It also records what you applied in an annotation, so it can work out the changes next time. You can run apply again and again with the same result, which is why files in git are applied, not created. For large teams and GitOps tools, server-side apply does the same tracking on the API server."),
]

NEW["deeper"] = """
How do two containers in a Pod share one IP address? Through Linux namespaces, the same feature that keeps Docker containers apart. (These are a Linux idea, unrelated to Kubernetes namespaces.)

When the kubelet starts a Pod, containerd first creates a tiny sandbox container, often called the pause container. Its only job is to hold the Pod's network namespace: one network interface (a network connection point), one IP address and one set of ports. Every container in the Pod then joins that namespace. So they share `localhost`, and two of them cannot both listen on port 80. Each container still has its own file system and its own processes (running programs). Files are shared only through volumes.

You can see the sandboxes on a kind node:
- `docker exec devops-worker crictl pods` lists Pod sandboxes.
- `docker exec devops-worker crictl ps` lists the containers inside them.

Restarts happen inside this sandbox. When a container crashes, the kubelet starts a new container in the same Pod, with the same IP address and the same volumes. An `emptyDir` volume survives a container restart, but not the Pod. That is why `kubectl logs --previous` can still find the last run: the old container's log file stays on the node until the next restart.

The STATUS column is built from several fields, in roughly this order of priority:
1. Is the Pod being deleted? Then `Terminating`.
2. Is an init container failing or still running? Then `Init:Error`, `Init:CrashLoopBackOff` or `Init:1/2`.
3. Is an app container waiting? Then its reason, such as `ImagePullBackOff` or `CrashLoopBackOff`.
4. Otherwise the phase, such as `Running` or `Completed`.

So STATUS is a summary for humans. Scripts and alerts should read the real fields: `status.phase`, `status.conditions` and `status.containerStatuses`. The `Ready` condition is what Services use to decide whether a Pod gets traffic (Day 41).

Kubernetes 1.35 also moved finer restart rules to beta (ready to try, not yet final). A single container can have its own `restartPolicy`, plus rules such as "restart only if the exit code is 42". You will not need it for hello-devops. It helps batch jobs where some exit codes mean "try again" and others mean "give up".

Three annotations will come up soon:
- `kubernetes.io/change-cause`, the reason shown in a Deployment's rollout history (Day 40).
- `kubectl.kubernetes.io/last-applied-configuration`, which `kubectl apply` writes to remember what you applied.
- Argo CD's tracking annotation, which marks the objects it manages (Day 47).

To go further, read the [Pod lifecycle](https://kubernetes.io/docs/concepts/workloads/pods/pod-lifecycle/) page. It is long, but it defines every word you see in the STATUS column.
"""
