"""Day 34: ConfigMaps and Secrets."""
from svg import box, arrow, cap, svg

DIAGRAM = svg(244, "ConfigMaps and Secrets reach a container as environment variables, read once at start, or as mounted files that the kubelet updates", [
    box(16, 40, 128, 44, "bxg", "ConfigMap"),
    box(16, 156, 128, 44, "bxp", "Secret"),
    box(208, 40, 136, 44, "bx", "env vars"),
    box(208, 156, 136, 44, "bx", "mounted files"),
    box(416, 98, 128, 44, "bxt", "container"),
    arrow(144, 62, 206, 62),
    arrow(144, 72, 206, 168),
    arrow(144, 168, 206, 72),
    arrow(144, 178, 206, 178),
    arrow(344, 62, 414, 112),
    arrow(344, 178, 414, 128),
    cap(276, 28, "read once at start"),
    cap(276, 222, "updated in place"),
    cap(480, 166, "restart for new env"),
])

DEPLOY_V2 = """# Runs 3 copies (pods) of hello-devops and replaces any that die.
# Day 34 version: adds envFrom. Day 35 adds probes and resources.
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
              containerPort: 8000
          envFrom:
            - configMapRef:
                name: hello-config # every key in the ConfigMap becomes an env var"""

KUSTOMIZATION_V3 = """# The list of files that make up the app. Apply them all with: kubectl apply -k k8s
# Day 34 version: adds the ConfigMap and Redis. Day 35 adds hpa.yaml.
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization
resources:
  - namespace.yaml
  - configmap.yaml
  - redis.yaml
  - deployment.yaml
  - service.yaml"""


def lab(name):
    return open(f"/home/user/devops-from-zero/labs/hello-devops/k8s/{name}").read().rstrip("\n")


L = {
    "id": "d34",
    "title": "ConfigMaps and Secrets",
    "minutes": 45,
    "goal": "By the end you can give hello-devops its settings from a ConfigMap, predict when a running Pod sees a changed value, roll the Deployment to pick changes up, and explain what does and does not protect a Secret.",
    "guess": {
        "q": "Your Deployment reads `GREETING` from a ConfigMap through `envFrom`. You change the value in the ConfigMap and apply it. What do the running Pods see?",
        "options": [
            "The old value, until the Pods are restarted",
            "The new value, within about a minute",
            "The new value at once, because apply restarts the Pods",
            "No value at all, until you delete the old ConfigMap",
        ],
        "answer": 0,
        "why": "Environment variables are set once, when the container starts. Only files mounted from a ConfigMap are updated in place; for env vars you restart the Pods, for example with `kubectl rollout restart`.",
    },
    "terms": [
        {"term": "ConfigMap", "plain": "An object that stores plain settings as key-value pairs, for Pods to read as env vars or files."},
        {"term": "Secret", "plain": "An object like a ConfigMap, meant for passwords, tokens and keys; its values are base64-encoded."},
        {"term": "envFrom", "plain": "A container setting that turns every key of a ConfigMap or Secret into an environment variable."},
        {"term": "Base64", "plain": "A way to write any bytes as plain letters and digits; anyone can decode it, so it hides nothing."},
        {"term": "Encryption at rest", "plain": "Encrypting data where it is stored, here Secrets inside etcd, so a copy of the disk reveals nothing."},
        {"term": "Immutable ConfigMap", "plain": "A ConfigMap with `immutable: true`, whose data can never be changed, only deleted and recreated."},
        {"term": "Rollout restart", "plain": "A kubectl command that replaces a Deployment's Pods gradually, so they start with fresh config."},
        {"term": "External Secrets Operator", "plain": "A tool that copies secrets from a vault, such as AWS Secrets Manager, into Kubernetes Secrets."},
    ],
    "sections": [
        {
            "h": "Settings belong outside the image",
            "body": """Since Part 3 you have built one image and changed its behavior with environment variables. hello-devops reads `GREETING` and `REDIS_HOST` this way. The same image then runs on your laptop, in staging and in production, and only the settings differ. That is the twelve-factor rule: store config in the environment.

In Kubernetes, settings live in a **ConfigMap**. It is a small object with a `data` section of keys and string values. Typical keys:
- Plain settings, such as a greeting, a log level or a feature flag.
- Addresses of other services, such as `REDIS_HOST: redis`.
- Whole config files, such as an `application.yaml` for a JVM service or an `nginx.conf`, stored as one long value.

Two limits to remember. A ConfigMap holds at most 1 MiB of data. And it is not secret at all: anyone who can read objects in the namespace can read it. Passwords go in a Secret, later in this lesson.

You can write a ConfigMap as YAML, or let kubectl build it from what you have:
- `--from-literal=GREETING=hi` for single values.
- `--from-file=app.yaml` for a whole file, with the file name as the key.
- `--from-env-file=.env` for a file of KEY=value lines.

Add `--dry-run=client -o yaml` to any of them, and you get a file to keep in git instead of a change made only in the cluster.""",
            "refs": [
                {"title": "ConfigMaps", "url": "https://kubernetes.io/docs/concepts/configuration/configmap/", "kind": "docs"},
                {"title": "Kubernetes components explained, with ConfigMap and Secret (TechWorld with Nana)", "url": "https://www.youtube.com/watch?v=Krpb44XR0bk", "kind": "watch"},
            ],
        },
        {
            "h": "Three ways to hand a ConfigMap to a container",
            "body": """A Pod can use a ConfigMap in three ways, and you can mix them:
- `env` with `configMapKeyRef`: one key becomes one environment variable, and you can rename it on the way.
- `envFrom` with `configMapRef`: every key becomes an environment variable with the same name. The lab uses this, so `GREETING` and `REDIS_HOST` arrive as env vars.
- A volume: every key becomes a file in a folder you choose. `items` picks only some keys, and `mountPath` says where the folder appears.

Env vars suit short values your code reads at start. Files suit whole config files and anything your code may read again later. A Spring Boot service, for example, can read a mounted `application.yaml` from a folder.

What if the ConfigMap does not exist? The Pod cannot start. Its STATUS shows `CreateContainerConfigError`, and `kubectl describe pod` names the missing ConfigMap. Mark a reference `optional: true` if the app can live without it. Day 38 returns to this error.

The lab's `configmap.yaml` holds two keys, and `deployment.yaml` gains four lines of `envFrom`. Adding `envFrom` changes the Pod template, so applying it starts a normal rolling update. After it, every Pod has both env vars, and `REDIS_HOST=redis` makes all Pods share one counter in Redis.""",
            "refs": [
                {"title": "Configure a Pod to use a ConfigMap", "url": "https://kubernetes.io/docs/tasks/configure-pod-container/configure-pod-configmap/", "kind": "docs"},
            ],
        },
        {
            "h": "What happens when a ConfigMap changes",
            "body": """Most people get this wrong the first time. Changing a ConfigMap never restarts anything, and what a running Pod sees depends on how it reads the value:
- Environment variables are set once, when the container starts. They never change while it runs.
- Mounted files are updated in place. The kubelet notices the change on its next sync and swaps the files, usually within a minute or so.
- A file mounted with `subPath` (one file into an existing folder) is never updated.
- Even an updated file only helps if your app reads it again. Most apps read config once at start.

So for hello-devops, which uses env vars, a new greeting needs new Pods. The tool for that is `kubectl rollout restart deployment/hello-devops`. It writes the current time into an annotation in the Pod template. The template changed, so the Deployment does a normal rolling update, and every new Pod starts with the new values.

There is a neater trick that tools use. Put something that changes with the config into the Pod template:
- Kustomize's `configMapGenerator` adds a hash of the content to the ConfigMap's name, such as `hello-config-7g2m9dfk8t`. New content means a new name and a new template, so a rollout happens by itself.
- Helm charts often put a checksum of the config into a template annotation, with the same effect.

Day 37 covers both tools.""",
            "refs": [
                {"title": "ConfigMaps: mounted ConfigMaps are updated automatically", "url": "https://kubernetes.io/docs/concepts/configuration/configmap/#mounted-configmaps-are-updated-automatically", "kind": "docs"},
                {"title": "Managing objects with Kustomize (generators)", "url": "https://kubernetes.io/docs/tasks/manage-kubernetes-objects/kustomization/", "kind": "docs"},
            ],
        },
        {
            "h": "Immutable ConfigMaps and versioned names",
            "body": """Editing a ConfigMap in place has a hidden cost. A Deployment rollback brings back the old Pod template, but not the old ConfigMap. If you changed both and then roll back, the old code runs with the new settings.

The fix is to treat config like images: never change a version, make a new one.
1. Create `hello-config-v2` next to `hello-config-v1`.
2. Point the Deployment's `envFrom` at `hello-config-v2`. That is a template change, so a rollout starts.
3. To roll back, `kubectl rollout undo` brings back the template that points at `v1`, and `v1` still exists.

Kubernetes helps you keep that promise with `immutable: true`. Once set, nobody can change the data, and it cannot be switched off again. You can only delete the object and create a new one. Immutable ConfigMaps and Secrets also save work for the API server, because kubelets stop watching them for changes. That matters in clusters with thousands of them.

This is exactly what Kustomize's hash suffix does for you: every content change is a new, versioned name. For the lab, one plain ConfigMap and `rollout restart` are enough. Know the pattern for when config changes start causing incidents.""",
            "refs": [
                {"title": "Immutable ConfigMaps", "url": "https://kubernetes.io/docs/concepts/configuration/configmap/#configmap-immutable", "kind": "docs"},
            ],
        },
        {
            "h": "Secrets, and why base64 is not encryption",
            "body": """A **Secret** looks like a ConfigMap, but it is meant for sensitive values: passwords, API tokens, TLS keys. Pods use it the same three ways: `env` with `secretKeyRef`, `envFrom` with `secretRef`, or a volume.

Its values sit in `data`, encoded in base64. Base64 is a way to write any bytes as plain letters, so binary keys fit in YAML. It is not encryption. Anyone can reverse it with one command, as the worked example shows. You can also write plain text in a `stringData` field, and the API server encodes it for you.

Secrets have a `type` that tells tools what keys to expect:
- `Opaque`: anything you like. The default.
- `kubernetes.io/dockerconfigjson`: login details for a private registry such as GHCR, used through `imagePullSecrets`.
- `kubernetes.io/tls`: a certificate and its private key, used by Gateways (Day 36).
- `kubernetes.io/basic-auth` and `kubernetes.io/ssh-auth`: a user and password, or an SSH key.

So what is different about a Secret? A few real things:
- Kubernetes sends a Secret only to nodes that run a Pod that needs it.
- On the node, the kubelet keeps mounted Secrets in memory (tmpfs), never on disk.
- `kubectl describe` shows the size of each value, not the value.
- Access rules (RBAC) can allow reading ConfigMaps but not Secrets.

By default, though, Secrets are stored unencrypted in etcd. And anyone who can create a Pod in a namespace can mount, and so read, every Secret in it.""",
            "refs": [
                {"title": "Secrets", "url": "https://kubernetes.io/docs/concepts/configuration/secret/", "kind": "docs"},
                {"title": "Secret types", "url": "https://kubernetes.io/docs/concepts/configuration/secret/#secret-types", "kind": "docs"},
            ],
        },
        {
            "h": "Protecting Secrets inside the cluster",
            "body": """The Kubernetes docs list the steps that actually protect Secrets. Here they are, plus one that people often forget (number 3):
1. Turn on encryption at rest. The API server then encrypts Secrets before writing them to etcd, so a stolen backup or disk shows nothing.
2. Limit who can read Secrets with RBAC (role-based access control, Day 38). Very few people and programs need `get` or `list` on Secrets.
3. Limit who can create Pods in namespaces that hold important Secrets, because a Pod can mount any Secret in its namespace.
4. Give each container only the Secrets it needs.

On a cluster you run yourself, encryption at rest means an `EncryptionConfiguration` file for the API server. The best setups use a KMS provider, where a cloud key service holds the real key. Managed clusters such as EKS, AKS and GKE offer this with their own key services, and some turn it on by default. Check your provider's docs.

How the app reads a Secret matters too. Many teams prefer mounted files to env vars. Env vars are easy to leak: a crash report, a debug page or a `printenv` in a support session can print them all. A file is read only when the code asks for it.

None of this changes one rule. A Secret manifest with real values must never go into git, not even in a private repo. Base64 in git is plain text that stays in the history forever.""",
            "refs": [
                {"title": "Encrypting confidential data at rest", "url": "https://kubernetes.io/docs/tasks/administer-cluster/encrypt-data/", "kind": "docs"},
                {"title": "Good practices for Kubernetes Secrets", "url": "https://kubernetes.io/docs/concepts/security/secrets-good-practices/", "kind": "docs"},
            ],
        },
        {
            "h": "Keeping Secrets out of git",
            "body": """If Secrets cannot live in git, where do they come from when you deploy from git? Teams pick one of a few patterns:
- External Secrets Operator: the real value lives in a vault, such as AWS Secrets Manager, Google Secret Manager or HashiCorp Vault. You commit an `ExternalSecret` object that says which value to fetch. A controller in the cluster fetches it and writes a normal Secret, and refreshes it when the vault changes.
- Sealed Secrets: you encrypt a Secret with the cluster's public key, using the `kubeseal` tool, and commit the resulting `SealedSecret`. Only the controller in the cluster holds the private key, so only it can decrypt.
- SOPS: you encrypt the values inside YAML files with a cloud key or an age key. The files go into git, and your deploy tool decrypts them on the way in.
- The Secrets Store CSI Driver: the vault's values are mounted straight into the Pod as files, often without creating a Kubernetes Secret at all.

Which one? If your company already has a vault, External Secrets Operator is the common choice, because the vault stays the single place to rotate a password. For a small team without one, Sealed Secrets is the simplest to start with.

hello-devops has no real secrets yet, so the lab has no Secret file. Day 40 shows how these tools fit into GitOps, and Day 53 goes deeper into secrets and access.""",
            "refs": [
                {"title": "External Secrets Operator", "url": "https://github.com/external-secrets/external-secrets", "kind": "read"},
                {"title": "Sealed Secrets", "url": "https://github.com/bitnami-labs/sealed-secrets", "kind": "read"},
                {"title": "SOPS", "url": "https://github.com/getsops/sops", "kind": "read"},
            ],
        },
    ],
    "analogy": "A ConfigMap read as env vars is like a note in a new employee's locker on their first day. They read it once and never look again, so a changed note only reaches the next new hire. A mounted file is the notice board in the hallway, which people see whenever they walk past. A Secret is the same note in an envelope marked confidential, but the envelope is not sealed, which is why base64 hides nothing. The comparison breaks on reach. Anyone who can create Pods in a namespace can read all its Secrets, as if anyone allowed to hire staff could open every envelope the team holds.",
    "diagram": DIAGRAM,
    "diagram_caption": "Both objects reach a container as env vars (set once at start) or as mounted files (kept up to date by the kubelet).",
    "worked": {
        "title": "Watch a ConfigMap change reach a Pod, or not",
        "steps": [
            {
                "say": "Apply the demo from the examples folder in the scratch namespace (create it again with `kubectl create namespace scratch` if you deleted it). It creates a ConfigMap with `COLOR: blue` and a Pod that prints the value as an env var and as a file every 5 seconds.",
                "code": "$ kubectl apply -n scratch -f k8s/examples/config-demo.yaml\nconfigmap/demo-config created\npod/config-demo created\n$ kubectl logs -n scratch config-demo\nenv=blue file=blue\nenv=blue file=blue",
                "lang": "console",
            },
            {
                "say": "Change the value in the ConfigMap, then follow the logs. For a while nothing changes. After the kubelet's next sync, the file shows the new value. The env var never does.",
                "code": "$ kubectl patch configmap demo-config -n scratch --type merge -p '{\"data\":{\"COLOR\":\"green\"}}'\nconfigmap/demo-config patched\n$ kubectl logs -n scratch config-demo -f --tail=3\nenv=blue file=blue\nenv=blue file=blue\nenv=blue file=green\nenv=blue file=green\n^C",
                "lang": "console",
            },
            {
                "say": "See how the kubelet swaps the file safely. The real data sits in a timestamped folder, and `..data` is a link to it. On a change, the kubelet writes a new folder and moves the link in one step, so the app never reads half a file. This link trick is also why `subPath` mounts never update.",
                "code": "$ kubectl exec -n scratch config-demo -- ls -la /config\ntotal 12\ndrwxrwxrwx    3 root     root          4096 Oct 30 09:41 .\ndrwxr-xr-x    1 root     root          4096 Oct 30 09:38 ..\ndrwxr-xr-x    2 root     root          4096 Oct 30 09:41 ..2026_10_30_09_41_07.2716545396\nlrwxrwxrwx    1 root     root            32 Oct 30 09:41 ..data -> ..2026_10_30_09_41_07.2716545396\nlrwxrwxrwx    1 root     root            12 Oct 30 09:38 COLOR -> ..data/COLOR",
                "lang": "console",
            },
            {
                "say": "A bare Pod has no `rollout restart`, so replace it: `replace --force` deletes the Pod and creates it again from the same spec. The new container starts with the new env var.",
                "code": "$ kubectl get pod config-demo -n scratch -o yaml | kubectl replace --force -f -\npod \"config-demo\" deleted from scratch namespace\npod/config-demo replaced\n$ kubectl logs -n scratch config-demo\nenv=green file=green",
                "lang": "console",
            },
            {
                "say": "Now a Secret. Create one from a literal value, read the stored field, then decode it. Base64 kept the value out of sight for exactly one command.",
                "code": "$ kubectl create secret generic demo-secret -n scratch --from-literal=password='s3cr3t!'\nsecret/demo-secret created\n$ kubectl get secret demo-secret -n scratch -o jsonpath='{.data.password}'\nczNjcjN0IQ==\n$ kubectl get secret demo-secret -n scratch -o jsonpath='{.data.password}' | base64 --decode\ns3cr3t!",
                "lang": "console",
            },
            {
                "say": "Delete the scratch namespace. Everything in it goes: the demo ConfigMap, the Pod and the Secret.",
                "code": "$ kubectl delete namespace scratch\nnamespace \"scratch\" deleted",
                "lang": "console",
            },
        ],
    },
    "code": [
        {"lang": "yaml", "title": "k8s/configmap.yaml", "src": lab("configmap.yaml"), "run": "kubectl apply -k k8s"},
        {"lang": "yaml", "title": "k8s/redis.yaml", "src": lab("redis.yaml"), "run": "kubectl apply -k k8s"},
        {"lang": "yaml", "title": "k8s/deployment.yaml (Day 34 version; Day 35 adds probes and resources)", "src": DEPLOY_V2, "run": "kubectl apply -k k8s"},
        {"lang": "yaml", "title": "k8s/kustomization.yaml (Day 34 version)", "src": KUSTOMIZATION_V3, "run": "kubectl apply -k k8s"},
        {"lang": "yaml", "title": "k8s/examples/config-demo.yaml", "src": lab("examples/config-demo.yaml"), "run": "kubectl apply -n scratch -f k8s/examples/config-demo.yaml"},
    ],
    "commands": [
        {"cmd": "kubectl create configmap hello-config -n hello --from-literal=GREETING=hi --dry-run=client -o yaml", "what": "Print a ConfigMap as YAML from values on the command line, without creating it."},
        {"cmd": "kubectl get configmap hello-config -n hello -o yaml", "what": "Show a ConfigMap's data as stored in the cluster."},
        {"cmd": "kubectl describe configmap hello-config -n hello", "what": "Show a ConfigMap's keys and values in readable form."},
        {"cmd": "kubectl exec -n hello deploy/hello-devops -- printenv GREETING", "what": "Print the value one running container actually has."},
        {"cmd": "kubectl rollout restart deployment/hello-devops -n hello", "what": "Replace all Pods gradually, so they start with the current config."},
        {"cmd": "kubectl patch configmap demo-config -n scratch --type merge -p '{\"data\":{\"COLOR\":\"green\"}}'", "what": "Change one key of a live ConfigMap (for experiments; real changes go in the file)."},
        {"cmd": "kubectl create secret generic demo-secret -n scratch --from-literal=password='s3cr3t!'", "what": "Create a Secret from a value on the command line (for practice only)."},
        {"cmd": "kubectl get secret demo-secret -n scratch -o jsonpath='{.data.password}' | base64 --decode", "what": "Read a Secret value back, which shows that base64 hides nothing."},
        {"cmd": "kubectl describe secret demo-secret -n scratch", "what": "Show a Secret's type and the size of each value, without the values."},
        {"cmd": "kubectl get secrets -n hello", "what": "List Secrets with their type and number of keys."},
        {"cmd": "kubectl get pod config-demo -n scratch -o yaml | kubectl replace --force -f -", "what": "Delete a bare Pod and create it again from the same spec."},
        {"cmd": "kubectl delete namespace scratch", "what": "Delete a namespace and everything inside it."},
    ],
    "mistake": "Committing a Secret manifest to git because \"it is encoded\". Base64 is not encryption, and git keeps every old version, so the value is public to anyone who can read the repo, forever. If it happens, rotate the password or token at once, then switch to External Secrets Operator, Sealed Secrets or SOPS so real values never reach git.",
    "real_world": "At PayLite, each service's non-secret settings live in a ConfigMap generated by Kustomize, so every config change rolls the Pods automatically and can be rolled back with the code. Database passwords live in AWS Secrets Manager. External Secrets Operator syncs them into the cluster every hour, and the clusters have KMS encryption at rest turned on.",
    "task": {
        "title": "Give hello-devops its config, then change it",
        "steps": [
            "Write `k8s/configmap.yaml` and `k8s/redis.yaml`. Add `envFrom` to `k8s/deployment.yaml`, add both new files to `k8s/kustomization.yaml`, and run `kubectl apply -k k8s`.",
            "Follow the rollout that `envFrom` started. Then call `curl localhost:8081` several times: the greeting comes from the ConfigMap, and `visits` now counts up by one on every call, whichever Pod answers.",
            "Check what one container really has with `kubectl exec ... -- printenv GREETING`.",
            "Change `GREETING` in `configmap.yaml` and apply again. Call curl. Which greeting do you get, and why?",
            "Pick up the change with `kubectl rollout restart` and follow the rollout. Confirm that curl shows the new greeting.",
            "Find what `rollout restart` changed in the Pod template: print the template's annotations with a jsonpath query.",
            "Create a Secret named `hello-secret` in namespace `hello` with a key `API_TOKEN` and any fake value. Read it back with `-o yaml`, then decode it. Compare with what `kubectl describe secret` shows.",
            "Write down who in a real cluster could read that token. Then delete the Secret and commit the four files (not the Secret).",
        ],
        "hints": [
            "`kubectl get deploy hello-devops -n hello -o jsonpath='{.spec.template.metadata.annotations}'` prints the template's annotations.",
            "Pods stuck in `CreateContainerConfigError`? The name in `envFrom` must match the ConfigMap's `metadata.name` exactly, in the same namespace.",
            "`visits` still jumps around? Check that `REDIS_HOST` reached the Pods and that the Redis Pod is Running.",
        ],
        "done_when": "After a rollout restart, `curl localhost:8081` shows your new greeting, and `visits` goes up by exactly one on each call no matter which Pod answers.",
    },
    "explain_back": {
        "prompt": "Explain in 3 to 4 sentences what happens to a running Deployment when you change its ConfigMap, and how you make the Pods use the new values. Mention env vars, mounted files and rollout restart.",
        "answer": "Changing a ConfigMap does not restart any Pod. Containers that read it as environment variables keep the old values, because env vars are set only when a container starts. Containers that mount it as files see the new content after the kubelet's next sync, if the app reads the file again. To make every Pod use new env values, run `kubectl rollout restart`, which changes the Pod template and starts a normal rolling update. Tools like Kustomize get the same effect by giving each config version a new name.",
    },
    "recap": [
        "ConfigMaps hold plain settings outside the image; Pods read them as env vars, envFrom or files.",
        "Env vars never change in a running container; mounted files update, except with subPath.",
        "`kubectl rollout restart` or a new ConfigMap name in the template rolls Pods onto new config.",
        "Immutable, versioned ConfigMaps make config changes safe to roll back with the code.",
        "Secrets are base64-encoded, not encrypted; protect them with encryption at rest, RBAC and care about who can create Pods.",
        "Keep real secret values out of git with External Secrets Operator, Sealed Secrets or SOPS.",
    ],
    "check": [
        {
            "q": "An nginx Pod mounts `nginx.conf` from a ConfigMap as a whole folder. You change the ConfigMap. What happens?",
            "options": [
                "nginx notices the change and restarts with the new config",
                "The file changes soon, but nginx uses it only after a reload",
                "Nothing changes until someone deletes and recreates the Pod",
                "The Pod fails, because mounted ConfigMap files are read-only",
            ],
            "answer": 1,
            "why": "Mounted files are updated in place, but a program that read its config at start must reload it (or be restarted) to use the new file.",
        },
        {
            "q": "A teammate says: \"Our Secrets are safe, the YAML shows only base64.\" What is the best answer?",
            "options": [
                "True, as long as the cluster runs Kubernetes 1.30 or newer",
                "True, because kubectl hides Secret values from every user",
                "False, because Secrets cannot hold binary data like keys",
                "False: anyone can decode base64; encryption and access rules protect them",
            ],
            "answer": 3,
            "why": "Base64 is an encoding anyone can reverse; real protection is encrypting etcd and limiting who can read Secrets or create Pods.",
        },
        {
            "q": "You change both the image and the ConfigMap data of a Deployment, then roll back with `kubectl rollout undo`. Which combination runs now?",
            "options": [
                "Old image with the old ConfigMap data",
                "New image with the old ConfigMap data",
                "Old image with the new ConfigMap data",
                "Nothing, because undo refuses to run",
            ],
            "answer": 2,
            "why": "Undo restores the old Pod template, but a ConfigMap edited in place is not part of it, so the old code meets the new settings.",
        },
    ],
    "interview": [
        {
            "q": "What is the difference between a ConfigMap and a Secret?",
            "a": "Both store key-value data that Pods consume as environment variables or files. ConfigMaps are for non-sensitive settings and are shown in plain text. Secrets are for sensitive data: values are base64-encoded, sent only to nodes that need them, kept in tmpfs on nodes and can be restricted separately with RBAC. They are not encrypted by default, so production clusters enable encryption at rest, often with a KMS provider.",
        },
        {
            "q": "How do you make Pods pick up a changed ConfigMap?",
            "a": "Env vars are fixed at container start, so the Pods must be recreated, usually with `kubectl rollout restart`, which changes a template annotation and triggers a rolling update. Mounted files update in place after the kubelet syncs, but the app has to reload them, and subPath mounts never update. A cleaner pattern is versioned or hash-suffixed ConfigMap names, as Kustomize's configMapGenerator does, so a config change is a template change and can be rolled back.",
        },
        {
            "q": "How would you manage secrets for apps deployed with GitOps?",
            "a": "Never commit plain Secret manifests, because base64 is readable and git history is permanent. With an existing vault, I would use External Secrets Operator: git holds an ExternalSecret reference, and the controller syncs the real value from AWS Secrets Manager or Vault. Without one, Sealed Secrets or SOPS let you commit encrypted values that only the cluster or the deploy tool can decrypt. On top of that: encryption at rest, tight RBAC on Secrets and on Pod creation, and rotation when anything leaks.",
        },
    ],
    "deeper": {
        "minutes": 12,
        "body": """How long does a mounted ConfigMap take to update? The docs give a formula rather than a number: the kubelet's sync period plus the delay of its cache. By default the kubelet watches ConfigMaps, so the cache delay is small, and the sync period is about a minute. In practice, plan for up to a minute or two, and never for \"instantly\".

Projected volumes let one folder hold data from several sources. A `projected` volume can combine keys from ConfigMaps, Secrets, the Downward API (facts about the Pod itself, such as its name and labels) and a short-lived ServiceAccount token. It all appears as files in one place, which is tidy for apps that expect a single config folder.

Secrets have a few more corners worth knowing:
- Environment variables from a Secret are visible to anything that can read the process environment. Inside the container that includes every child process. On the node, it includes anyone who can inspect the container.
- `kubectl get secret -o yaml` prints the values for anyone with `get` permission. The `describe` output hides them, but that is a convenience, not a control.
- A ServiceAccount used to get a long-lived token Secret automatically. Since Kubernetes 1.24 that no longer happens. Pods get short-lived tokens through a projected volume, and those expire and rotate on their own.

Encryption at rest works like this on a self-managed cluster. You give the API server an `EncryptionConfiguration` file that lists providers for the `secrets` resource:
- `identity` means no encryption, which is the default.
- `aescbc`, `aesgcm` and `secretbox` encrypt with a key kept in the same file on the control-plane node.
- `kms` (version 2) asks an outside key service to wrap the data keys, so the real key never sits on the node.

The first provider in the list encrypts new writes, and all listed providers can decrypt. Existing Secrets stay as they were until they are written again. So after you turn encryption on, you rewrite every Secret once, for example with `kubectl get secrets -A -o json | kubectl replace -f -`.

On kind you could try this by mounting a config file into the control-plane node with `extraMounts` and a kubeadm patch. It is a good weekend exercise, not something you need for this course.

Finally, a word on size and count. A Secret, like a ConfigMap, is limited to 1 MiB. If you find yourself storing large files in either, a volume or an object store is usually the better place.""",
    },
    "sources": [
        {"title": "ConfigMaps", "url": "https://kubernetes.io/docs/concepts/configuration/configmap/"},
        {"title": "Secrets", "url": "https://kubernetes.io/docs/concepts/configuration/secret/"},
        {"title": "Encrypting confidential data at rest", "url": "https://kubernetes.io/docs/tasks/administer-cluster/encrypt-data/"},
        {"title": "Good practices for Kubernetes Secrets", "url": "https://kubernetes.io/docs/concepts/security/secrets-good-practices/"},
    ],
}
