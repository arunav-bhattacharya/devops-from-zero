"""Day 31: Pods, kubectl and YAML."""
from svg import box, arrow, line, cap, svg

DIAGRAM = svg(232, "A Pod starts its init container, then its sidecar, then the app container; all share one IP and volumes", [
    cap(86, 28, "runs once, exits 0"),
    cap(262, 28, "starts, keeps running"),
    cap(438, 28, "your app"),
    box(16, 40, 140, 44, "bxp", "init container"),
    box(192, 40, 140, 44, "bxo", "sidecar"),
    box(368, 40, 140, 44, "bxt", "app container"),
    arrow(156, 62, 190, 62),
    arrow(332, 62, 366, 62),
    line(86, 84, 86, 138, dashed=True),
    line(262, 84, 262, 138, dashed=True),
    line(438, 84, 438, 138, dashed=True),
    box(16, 140, 492, 44, "bxg", "Pod: one IP, shared volumes"),
    cap(262, 210, "The kubelet starts them left to right on one node"),
])

L = {
    "id": "d31",
    "title": "Pods, kubectl and YAML",
    "minutes": 50,
    "goal": "By the end you can read and generate a Pod manifest, run your own image in a Pod on kind, explain its phase and restarts, and use the everyday kubectl commands to inspect, reach and remove it.",
    "guess": {
        "q": "A Pod's STATUS column shows `CrashLoopBackOff`. What is the Pod's phase, the value Kubernetes stores in `status.phase`?",
        "options": ["CrashLoopBackOff", "Failed", "Running", "Unknown"],
        "answer": 2,
        "why": "`CrashLoopBackOff` is a word kubectl shows for a container that keeps crashing and waits longer between restarts. The phase stays `Running`, because the Pod is on a node and the kubelet keeps restarting its container.",
    },
    "terms": [
        {"term": "Pod", "plain": "The smallest unit Kubernetes runs: one or more containers that share one IP address and can share files."},
        {"term": "Manifest", "plain": "A YAML file that describes an object, with apiVersion, kind, metadata and spec."},
        {"term": "Init container", "plain": "A container that runs to completion before the app containers in its Pod start."},
        {"term": "Sidecar container", "plain": "A helper container that starts before the app container and runs beside it for the Pod's whole life."},
        {"term": "Label", "plain": "A key=value tag on an object, such as app=web, that selectors use to find it."},
        {"term": "Annotation", "plain": "A key=value note on an object for people and tools; selectors ignore it."},
        {"term": "Namespace", "plain": "A named group of objects inside a cluster, like a folder; names must be unique inside it."},
        {"term": "Context", "plain": "A saved cluster, user and default namespace that kubectl sends its commands to."},
    ],
    "sections": [
        {
            "h": "A manifest, and how to get one without typing it",
            "body": """Everything in Kubernetes is an object: a Pod, a Service, a Namespace. You describe objects in a manifest, a YAML file with four top-level fields:
- `apiVersion`: which version of the API defines this kind. A Pod is `v1`, a Deployment is `apps/v1`.
- `kind`: the type of object, such as `Pod` or `Service`.
- `metadata`: identity. The `name` and `namespace`, plus `labels` and `annotations`.
- `spec`: your desired state. Its shape depends on the kind.

You never write the fifth field, `status`. Kubernetes fills it in. A typo in a field name does not slip through, either. kubectl validates strictly by default, so `imagePullPolicyy` fails with an error that names the unknown field.

Nobody types manifests from memory. Three tricks do most of the work:
1. `--dry-run=client -o yaml` prints the object kubectl would create, without creating it. Redirect it to a file and edit from there.
2. `kubectl explain pod.spec.restartPolicy` prints the docs for one field, straight from your cluster's API, so it always matches your version. For this field it shows the type (`<string>`), the allowed values `Always`, `Never` and `OnFailure`, and a description. Add `--recursive` to see a whole tree.
3. `kubectl get pod hello -o yaml` shows a live object in full. It is longer than what you wrote, because the API server fills in defaults and `status`.

YAML has a few traps. Indent with spaces, never tabs. A `- ` starts a list item, and `containers:` is a list even with one container. Some bare words change type: `yes` and `on` can become true, and `8000` is a number. An environment variable value must be a string, so write `\"8000\"` in quotes.

Kubernetes 1.37 made KYAML stable for exactly this reason. It is a stricter style of YAML that quotes every string and uses brackets, so indentation cannot break it, and it is still valid YAML. Try `kubectl get pod hello -o kyaml`.""",
            "refs": [
                {"title": "Objects in Kubernetes", "url": "https://kubernetes.io/docs/concepts/overview/working-with-objects/", "kind": "docs"},
                {"title": "kubectl explain", "url": "https://kubernetes.io/docs/reference/kubectl/generated/kubectl_explain/", "kind": "docs"},
                {"title": "How to pretty-print Kubernetes YAML as KYAML (Kubernetes blog)", "url": "https://kubernetes.io/blog/2026/08/11/how-to-pretty-print-kubernetes-yaml-as-kyaml/", "kind": "read"},
            ],
        },
        {
            "h": "Pods: the smallest thing Kubernetes runs",
            "body": """Kubernetes never runs a bare container. It runs Pods. A **Pod** is one or more containers that are placed on one node together and share a few things:
- One IP address and one set of ports. Containers in a Pod reach each other on `localhost`.
- Volumes, if the Pod defines them. Two containers can read and write the same folder.
- One life. They start on the same node and are removed together.

Most Pods hold exactly one container. Think of the Pod as a thin wrapper that gives your container an address and a place in the cluster. Inside the Pod, the host name is the Pod's name. That is why the `host` field in hello-devops' JSON will show the Pod name.

Pods are disposable. If a node dies, its Pods die with it, and nothing brings a bare Pod back. Delete a Pod and it is gone. A new Pod made from the same YAML is a different Pod, with a new IP address.

So you rarely create Pods yourself. You create a controller, usually a Deployment (Day 32), and it creates and replaces Pods for you. Today you make bare Pods anyway, because that is the clearest way to see what a Pod is.""",
            "refs": [
                {"title": "Pods", "url": "https://kubernetes.io/docs/concepts/workloads/pods/", "kind": "docs"},
                {"title": "Complete Kubernetes course, beginner to pro (DevOps Directive)", "url": "https://www.youtube.com/watch?v=2T86xAtR6Fo", "kind": "watch"},
            ],
        },
        {
            "h": "Phases, container states and restarts",
            "body": """A Pod's life is summed up in `status.phase`. There are only five phases:
- `Pending`: accepted, but not running yet. It may be waiting for a node or pulling an image.
- `Running`: on a node, containers created, at least one running or restarting.
- `Succeeded`: all containers exited with code 0 and will not restart.
- `Failed`: all containers have stopped, and at least one failed.
- `Unknown`: the node stopped reporting, so nobody knows.

A normal start shows up in STATUS as `Pending` (no node yet), then `ContainerCreating` (node chosen, image being pulled, phase still `Pending`), then `Running`.

Each container also has a state of its own: `Waiting`, `Running` or `Terminated`, with a reason such as `ImagePullBackOff` or `Completed`. The STATUS column of `kubectl get pods` squeezes all this into one word. `CrashLoopBackOff` and `Terminating` show up there, but they are not phases. Most people mix these up at first, so when STATUS looks odd, read `kubectl describe pod`.

What happens when a container exits depends on the Pod's `restartPolicy`:
- `Always` (the default): restart it, whatever the exit code. Right for servers.
- `OnFailure`: restart it only after a non-zero exit code. Right for batch work.
- `Never`: leave it stopped.

The kubelet restarts the container inside the same Pod, on the same node. It waits longer each time: 10 seconds, then 20, then 40, up to five minutes. That growing wait is the back-off in `CrashLoopBackOff`. If the container then runs for ten minutes without trouble, the wait resets.""",
            "refs": [
                {"title": "Pod lifecycle", "url": "https://kubernetes.io/docs/concepts/workloads/pods/pod-lifecycle/", "kind": "docs"},
            ],
        },
        {
            "h": "Init containers and sidecars",
            "body": """Sometimes your container needs a helper. Kubernetes has two kinds of extra containers for that.

Init containers run first, one at a time, in order. Each must exit with code 0 before the next one starts. Only when all of them have finished do the app containers start. Use them for setup:
- Wait until a database answers.
- Download or render a config file into a shared volume.
- Fix file permissions on a volume.

A sidecar is a helper that runs beside your app for the Pod's whole life. Typical sidecars ship logs, add TLS in front of the app, or refresh certificates. Native sidecars have been stable since Kubernetes 1.33. You declare one as an init container with `restartPolicy: Always`, and Kubernetes then:
1. Starts it in init order, before the app containers.
2. Moves on as soon as it is running, without waiting for it to exit.
3. Restarts it if it crashes.
4. Stops it only after the app containers have stopped.

That order fixes two old problems. A log shipper that started late missed the first lines, and one that stopped early lost the last ones. The READY column of kubectl counts sidecars too, so a Pod with one sidecar and one app shows `2/2`.

Put containers in one Pod only when they must share a node, an IP address or files. An app and its database belong in separate Pods, so you can scale and replace each one on its own.""",
            "refs": [
                {"title": "Init containers", "url": "https://kubernetes.io/docs/concepts/workloads/pods/init-containers/", "kind": "docs"},
                {"title": "Sidecar containers", "url": "https://kubernetes.io/docs/concepts/workloads/pods/sidecar-containers/", "kind": "docs"},
                {"title": "Multi-container Pods: an overview (Kubernetes blog)", "url": "https://kubernetes.io/blog/2025/04/22/multi-container-pods-overview/", "kind": "read"},
            ],
        },
        {
            "h": "Labels, annotations and selectors",
            "body": """Labels are how Kubernetes objects find each other. A label is a key=value pair in `metadata.labels`, such as `app: hello-devops` or `tier: frontend`. A selector is a query over labels. Deployments find their Pods with selectors, and so do Services and NetworkPolicies (Day 33).

You use selectors with kubectl too:
- `kubectl get pods -l app=web` matches one label exactly.
- `kubectl get pods -l 'app=web,tier!=db'` combines rules, and all must hold.
- `kubectl get pods -l 'env in (dev,test)'` matches a set of values.
- `kubectl get pods --show-labels` prints every label, and `-L app` adds one label as a column.

Annotations look the same but have a different job. They hold notes for people and tools, and selectors ignore them. You will meet these soon:
- `kubernetes.io/change-cause`, the reason shown in a Deployment's rollout history (Day 32).
- `kubectl.kubernetes.io/last-applied-configuration`, which `kubectl apply` writes to remember what you applied.
- Argo CD's tracking annotation, which marks the objects it manages (Day 39).

A simple rule: if you will ever select by it, make it a label. If it is long, or only a tool reads it, make it an annotation. Kubernetes also recommends a shared set of labels, such as `app.kubernetes.io/name`, that many tools understand.""",
            "refs": [
                {"title": "Labels and selectors", "url": "https://kubernetes.io/docs/concepts/overview/working-with-objects/labels/", "kind": "docs"},
                {"title": "Annotations", "url": "https://kubernetes.io/docs/concepts/overview/working-with-objects/annotations/", "kind": "docs"},
                {"title": "Recommended labels", "url": "https://kubernetes.io/docs/concepts/overview/working-with-objects/common-labels/", "kind": "docs"},
            ],
        },
        {
            "h": "Namespaces, kubeconfig and contexts",
            "body": """A namespace is a named group of objects inside one cluster. Names must be unique inside a namespace, not across the cluster. A new cluster starts with four:
- `default`: where objects go when you name no namespace.
- `kube-system`: the cluster's own parts, such as CoreDNS.
- `kube-public` and `kube-node-lease`: used by the system. Leave them alone.

Think of namespaces as folders, not walls. A Pod in one namespace can still reach a Pod in another over the network, and blocking that takes a NetworkPolicy (Day 33). Teams attach access rules and quotas to namespaces. Deleting a namespace deletes everything in it, which makes cleanup easy and mistakes expensive.

Which cluster does kubectl talk to? It reads a kubeconfig file: `~/.kube/config` by default, or the files listed in the `KUBECONFIG` variable. The file has three lists:
- clusters: each API server's address and certificate.
- users: your credentials.
- contexts: a cluster plus a user plus a default namespace, under one name.

One context is current, and every kubectl command goes there. `kubectl config get-contexts` lists them all and marks the current one with a star. Check it before anything risky with `kubectl config current-context`. This matters more than it sounds. Docker Desktop can run its own Kubernetes with a context called `docker-desktop`, and at work you will have contexts for real clusters. To stop typing `-n hello` on every command, set a default namespace with `kubectl config set-context --current --namespace=hello`.""",
            "refs": [
                {"title": "Namespaces", "url": "https://kubernetes.io/docs/concepts/overview/working-with-objects/namespaces/", "kind": "docs"},
                {"title": "Organizing cluster access using kubeconfig files", "url": "https://kubernetes.io/docs/concepts/configuration/organize-cluster-access-kubeconfig/", "kind": "docs"},
            ],
        },
        {
            "h": "Everyday kubectl, and getting your image into kind",
            "body": """Most days you need about a dozen kubectl commands. Here they are, grouped by the question they answer:
- What is there? `kubectl get pods`. Add `-o wide` for IPs and nodes, `-w` to keep watching, `-l` to filter by label, `-A` for all namespaces.
- What happened? `kubectl describe pod hello` shows details, with recent Events at the bottom. Read the Events first.
- What did it print? `kubectl logs hello`. Add `-f` to follow, `-c` to pick a container, and `--previous` for the last crashed run.
- Let me in: `kubectl exec -it hello -- sh` opens a shell inside the container, if the image has one.
- Let me reach it: `kubectl port-forward pod/hello 8000:8000` tunnels a port on your Mac to the Pod until you press Ctrl+C.
- Remove it: `kubectl delete pod hello`, or `kubectl delete -f pod.yaml`.
- Just one field, please: `-o jsonpath='{.status.phase}'` prints a single value, which is handy in scripts.

`kubectl create -f` and `kubectl apply -f` both make objects from a file, but they think differently. The `create` command is a one-time order, and it fails if the object already exists. The `apply` command is declarative: it creates the object or updates it to match the file, so you can run it again and again. Use `apply` for anything you keep in git.

Your own image needs one more step. Each kind node runs its own containerd with its own image store, separate from Docker on your Mac. So `docker build` alone is not enough. Copy the image in with `kind load docker-image hello-devops:1.0.0 --name devops`.

Give it a real tag. With `:latest` or no tag, Kubernetes sets `imagePullPolicy: Always`, tries Docker Hub, and the Pod ends in `ImagePullBackOff`.""",
            "refs": [
                {"title": "kubectl quick reference", "url": "https://kubernetes.io/docs/reference/kubectl/quick-reference/", "kind": "docs"},
                {"title": "Images and imagePullPolicy", "url": "https://kubernetes.io/docs/concepts/containers/images/", "kind": "docs"},
                {"title": "kind quick start: loading an image", "url": "https://kind.sigs.k8s.io/docs/user/quick-start/", "kind": "docs"},
            ],
        },
    ],
    "analogy": "A Pod is like a shared hotel room. Everyone in it has the same room number (one IP address), can use the same desk (shared volumes) and checks in and out together. The init container is the cleaner who must finish before guests enter, and the sidecar is the assistant who arrives first and leaves last. The picture breaks on moving: a hotel guest can change rooms, but a Pod never moves. Kubernetes throws it away and builds a new one with a new number.",
    "diagram": DIAGRAM,
    "diagram_caption": "Init containers finish first, the sidecar starts next and keeps running, then the app starts. All of them share the Pod's IP and volumes.",
    "worked": {
        "title": "Watch an init container and a sidecar start",
        "steps": [
            {
                "say": "Make a scratch namespace for experiments, so cleanup is one command later. Apply the example Pod from the lab repo. It has an init container that writes a web page, a sidecar that tails the access log, and nginx.",
                "code": "$ kubectl create namespace scratch\nnamespace/scratch created\n$ kubectl apply -n scratch -f k8s/examples/pod-sidecar.yaml\npod/web created",
                "lang": "console",
            },
            {
                "say": "Watch the Pod start. `Init:0/2` means the first of two init containers is running. When it finishes, the sidecar starts and counts as ready (`1/2`) while nginx is still being created. Then nginx starts and READY becomes `2/2`, because READY counts the sidecar.",
                "code": "$ kubectl get pod web -n scratch -w\nNAME   READY   STATUS            RESTARTS   AGE\nweb    0/2     Init:0/2          0          1s\nweb    0/2     Init:1/2          0          4s\nweb    1/2     PodInitializing   0          5s\nweb    2/2     Running           0          11s",
                "lang": "console",
            },
            {
                "say": "Ask nginx for its page from inside the Pod. Because the Pod has three containers, say which one with `-c`. The page is the file the init container wrote into the shared volume before nginx existed.",
                "code": "$ kubectl exec -n scratch web -c nginx -- curl -s localhost\nhello from the init container",
                "lang": "console",
            },
            {
                "say": "Next, request a page that does not exist and read the sidecar's logs. Both requests went into `access.log` in the shared volume, and the sidecar printed them.",
                "code": "$ kubectl exec -n scratch web -c nginx -- curl -s -o /dev/null localhost/nope\n$ kubectl logs -n scratch web -c log-tailer\n127.0.0.1 - - [30/Oct/2026:09:14:02 +0000] \"GET / HTTP/1.1\" 200 30 \"-\" \"curl/8.14.1\" \"-\"\n127.0.0.1 - - [30/Oct/2026:09:14:20 +0000] \"GET /nope HTTP/1.1\" 404 153 \"-\" \"curl/8.14.1\" \"-\"",
                "lang": "console",
            },
            {
                "say": "Look at how kubectl sees the Pod as data. The labels and the annotation from the manifest are there, plus everything Kubernetes added. KYAML quotes every string, so a value like `on` can never turn into true by accident.",
                "code": "$ kubectl get pod web -n scratch --show-labels\nNAME   READY   STATUS    RESTARTS   AGE   LABELS\nweb    2/2     Running   0          3m    app=web\n$ kubectl get pod web -n scratch -o kyaml | head -6\n{\n  apiVersion: \"v1\",\n  kind: \"Pod\",\n  metadata: {\n    annotations: {\n      example.com/owner: \"team-a\",",
                "lang": "console",
            },
            {
                "say": "Clean up. Deleting the file's objects removes the Pod. Keep the `scratch` namespace; you will use it again.",
                "code": "$ kubectl delete -n scratch -f k8s/examples/pod-sidecar.yaml\npod \"web\" deleted from scratch namespace",
                "lang": "console",
            },
        ],
    },
    "code": [
        {
            "lang": "yaml",
            "title": "k8s/examples/pod-sidecar.yaml",
            "src": open("/home/user/devops-from-zero/labs/hello-devops/k8s/examples/pod-sidecar.yaml").read().rstrip("\n"),
            "run": "kubectl apply -n scratch -f k8s/examples/pod-sidecar.yaml",
        },
    ],
    "commands": [
        {"cmd": "kind load docker-image hello-devops:1.0.0 --name devops", "what": "Copy an image from Docker on your Mac into every node of the `devops` cluster."},
        {"cmd": "kubectl run hello --image=hello-devops:1.0.0 --port=8000 --dry-run=client -o yaml > pod.yaml", "what": "Write a Pod manifest to a file without creating anything."},
        {"cmd": "kubectl explain pod.spec.containers", "what": "Show the built-in docs for a field, straight from the cluster's API."},
        {"cmd": "kubectl apply -f pod.yaml", "what": "Create the objects in a file, or update them to match it."},
        {"cmd": "kubectl get pods -o wide", "what": "List Pods with their IP address and the node each one runs on."},
        {"cmd": "kubectl get pods -A", "what": "List Pods in every namespace."},
        {"cmd": "kubectl get pods -w", "what": "Keep watching Pods and print a new line whenever one changes."},
        {"cmd": "kubectl get pods -l app=web --show-labels", "what": "List only Pods with the label app=web, and show all their labels."},
        {"cmd": "kubectl describe pod hello", "what": "Show a Pod's details and recent events. Read the Events at the bottom first."},
        {"cmd": "kubectl logs hello -f", "what": "Follow what the Pod's container prints. Add `-c NAME` in a Pod with several containers."},
        {"cmd": "kubectl logs crashy --previous", "what": "Show the output of the last run that crashed, not the current one."},
        {"cmd": "kubectl exec -it hello -- sh", "what": "Open a shell inside the Pod's container."},
        {"cmd": "kubectl port-forward pod/hello 8000:8000", "what": "Forward localhost:8000 on your Mac to port 8000 in the Pod until you press Ctrl+C."},
        {"cmd": "kubectl get pod hello -o kyaml", "what": "Print the live object as KYAML, a stricter style of YAML."},
        {"cmd": "kubectl config get-contexts", "what": "List your contexts; the current one has a star."},
        {"cmd": "kubectl config set-context --current --namespace=hello", "what": "Make `hello` the default namespace for the current context."},
    ],
    "mistake": "Running kubectl against the wrong cluster. A new laptop often has a `docker-desktop` context too, and at work you will have real clusters in the same kubeconfig. One `kubectl delete` can then land somewhere you did not mean. Run `kubectl config current-context` before anything that changes or deletes, and give production contexts names that stand out.",
    "real_world": "At PayLite, the checkout Pod runs the app plus a native sidecar that ships logs to the central log system. An init container waits for the database during start-up. Engineers rarely write YAML from scratch. They copy a template from the team's repo, check unknown fields with `kubectl explain`, and diff it against `kubectl get -o yaml` when something behaves differently than expected.",
    "task": {
        "title": "Run hello-devops in a Pod, then break one on purpose",
        "steps": [
            "In `~/code/hello-devops`, build the image with its version baked in: `docker build --build-arg APP_VERSION=1.0.0 -t hello-devops:1.0.0 .` Then load it into the `devops` cluster.",
            "Generate `pod.yaml` for a Pod named `hello` with `--dry-run=client -o yaml`. Change its label to `app: hello`, add `imagePullPolicy: IfNotPresent`, delete `resources: {}` and `status: {}`, and apply it.",
            "Check the Pod with `-o wide`. Which worker did the scheduler pick, and what IP did the Pod get?",
            "Port-forward port 8000 to the Pod and `curl localhost:8000` from a second terminal. Follow the logs in a third terminal and watch each request appear.",
            "Open a shell in the Pod and run `hostname` and `printenv APP_VERSION`. Why does the `host` field in the JSON show `hello`?",
            "Start a Pod that crashes: `kubectl run crashy --image=busybox:1.37 -- sh -c \"echo starting; sleep 3; exit 1\"`. Watch it for two minutes with `-w`. How do STATUS and RESTARTS change?",
            "Read the crashed run's output with `logs --previous`, and print the Pod's phase with a jsonpath query.",
            "Repeat with `--restart=Never` and the name `once`. What are its STATUS and phase now, and why?",
            "Delete all three Pods. Keep `pod.yaml` out of git (it was practice); the cluster stays for tomorrow.",
        ],
        "hints": [
            "`kubectl get pod crashy -o jsonpath='{.status.phase}'` prints only the phase.",
            "If `kind load` fails with `content digest ... not found`, Docker is using its containerd image store. Save the image with `docker image save --platform linux/arm64 -o hello.tar hello-devops:1.0.0`, then run `kind load image-archive hello.tar --name devops`.",
            "Pod stuck in `ErrImagePull`? Check the tag, `imagePullPolicy`, and that you loaded the image into the `devops` cluster, not another one.",
        ],
        "done_when": "With port-forward running, `curl localhost:8000` returns JSON with `host` `hello` and `version` `1.0.0`, and you can name the phase of `crashy` (Running) and of `once` (Failed).",
    },
    "explain_back": {
        "prompt": "Explain in 3 to 4 sentences what a Pod is and why you rarely create one by hand. Mention the shared IP address, init containers or sidecars, and what happens when a node dies.",
        "answer": "A Pod is the smallest thing Kubernetes runs: one or more containers on one node that share an IP address and can share volumes. Most Pods have one container, and helpers come as init containers that finish before the app starts or sidecars that run beside it. Pods are disposable: if a node dies, its bare Pods are gone, and nothing recreates them. That is why you normally let a controller such as a Deployment create and replace Pods for you.",
    },
    "recap": [
        "A manifest has apiVersion, kind, metadata and spec; Kubernetes adds status.",
        "Generate YAML with `--dry-run=client -o yaml` and look up fields with `kubectl explain`.",
        "A Pod is one or more containers with one IP address; bare Pods are not replaced when they die.",
        "Phase is one of five values; `CrashLoopBackOff` is a container state shown in STATUS, not a phase.",
        "Init containers run first and must succeed; sidecars are init containers with `restartPolicy: Always`.",
        "Labels are for selecting, annotations are notes, and the current context decides which cluster kubectl changes.",
    ],
    "check": [
        {
            "q": "A Pod has two init containers and one app container. The second init container exits with code 1. What do you expect?",
            "options": [
                "The app container starts anyway, and the error shows in its logs",
                "The first init container runs again, then the app starts",
                "The init container is retried, and the app never starts until it succeeds",
                "Kubernetes deletes the Pod and schedules a new one",
            ],
            "answer": 2,
            "why": "App containers start only after every init container exits with 0; with the default restart policy the kubelet keeps retrying the failed init container.",
        },
        {
            "q": "You want a log shipper that starts before your app and is still running when the app writes its last lines on shutdown. How do you declare it?",
            "options": [
                "As a second entry under `containers`",
                "As an init container with `restartPolicy: Always`",
                "As a separate Pod with the same labels",
                "As an init container with `restartPolicy: OnFailure`",
            ],
            "answer": 1,
            "why": "A native sidecar is an init container with `restartPolicy: Always`, which Kubernetes starts before and stops after the app containers.",
        },
        {
            "q": "`kubectl get pods` shows nothing, but a teammate swears their Pod is running. They use namespace `payments`. What do you run first?",
            "options": [
                "`kubectl describe nodes`",
                "`kubectl logs payments`",
                "`kind load docker-image payments`",
                "`kubectl get pods -n payments`",
            ],
            "answer": 3,
            "why": "Without `-n`, kubectl only looks in the current context's default namespace, so you must ask for the right namespace (or use `-A`).",
        },
    ],
    "interview": [
        {
            "q": "What is a Pod, and why does Kubernetes not just run containers?",
            "a": "A Pod is a group of one or more containers that are scheduled together on one node and share a network namespace and volumes. It gives tightly coupled helpers, such as a log shipper or a proxy, a way to run next to the app with the same IP address and shared files. It also gives Kubernetes one unit to schedule, track and replace. In practice most Pods have one container and are managed by a controller such as a Deployment.",
        },
        {
            "q": "What is the difference between an init container and a sidecar container?",
            "a": "An init container runs to completion before the app containers start, in order, and must exit with code 0; it is for setup work. A sidecar runs for the Pod's whole life beside the app. Native sidecars have been stable since Kubernetes 1.33. You declare them as init containers with `restartPolicy: Always`. They start before the app, are restarted if they crash, and stop after the app. That ordering avoids losing logs or proxy traffic at start-up and shutdown.",
        },
        {
            "q": "What is the difference between kubectl create and kubectl apply?",
            "a": "The `kubectl create` command is imperative: it creates the object and fails if it already exists. The `kubectl apply` command is declarative. It creates the object if needed, or updates it to match the file. It also records what you applied in an annotation, so it can work out the changes next time. You can run apply repeatedly with the same result, which is why files in git are applied, not created. For large teams and GitOps tools, server-side apply does the same tracking on the API server.",
        },
    ],
    "deeper": {
        "minutes": 12,
        "body": """How do two containers in a Pod share one IP address? Linux namespaces, the same feature that isolates Docker containers.

When the kubelet starts a Pod, containerd first creates a tiny sandbox container, often called the pause container. Its only job is to hold the Pod's network namespace: one network interface, one IP address, one set of ports. Every container in the Pod then joins that namespace. So they share `localhost`, and two of them cannot both listen on port 80. Each container still has its own file system and its own processes. Files are shared only through volumes.

You can see the sandboxes on a kind node:
- `docker exec devops-worker crictl pods` lists Pod sandboxes.
- `docker exec devops-worker crictl ps` lists the containers inside them.

Restarts happen inside this sandbox. When a container crashes, the kubelet starts a new container in the same Pod, with the same IP address and the same volumes. An `emptyDir` volume survives a container restart, but not the Pod. That is why `kubectl logs --previous` can still find the last run: the old container's log file stays on the node until the next restart.

The STATUS column is built from several fields, in roughly this order of priority:
1. Is the Pod being deleted? Then `Terminating`.
2. Is an init container failing or still running? Then `Init:Error`, `Init:CrashLoopBackOff` or `Init:1/2`.
3. Is an app container waiting? Then its reason, such as `ImagePullBackOff` or `CrashLoopBackOff`.
4. Otherwise the phase, such as `Running` or `Completed`.

So STATUS is a summary for humans. Scripts and alerts should read the real fields: `status.phase`, `status.conditions` and `status.containerStatuses`. The `Ready` condition is what Services use to decide whether a Pod gets traffic (Day 33).

One more current detail. Kubernetes 1.35 moved finer restart rules to beta. A single container can have its own `restartPolicy`, plus rules such as "restart only if the exit code is 42". You will not need it for hello-devops. It helps batch jobs where some exit codes mean "try again" and others mean "give up".

To go further, read the [Pod lifecycle](https://kubernetes.io/docs/concepts/workloads/pods/pod-lifecycle/) page. It is long, but it defines every word you see in the STATUS column.""",
    },
    "sources": [
        {"title": "Pods", "url": "https://kubernetes.io/docs/concepts/workloads/pods/"},
        {"title": "Pod lifecycle", "url": "https://kubernetes.io/docs/concepts/workloads/pods/pod-lifecycle/"},
        {"title": "Sidecar containers", "url": "https://kubernetes.io/docs/concepts/workloads/pods/sidecar-containers/"},
        {"title": "kubectl quick reference", "url": "https://kubernetes.io/docs/reference/kubectl/quick-reference/"},
    ],
}
