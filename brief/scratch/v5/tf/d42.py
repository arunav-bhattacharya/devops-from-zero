NEW = {}

NEW["goal"] = "By the end you can give hello-devops its settings from a ConfigMap, predict when a running Pod sees a changed value, roll the Deployment to pick changes up, and explain what does and does not protect a Secret."

NEW["opening"] = """Picture the restaurant at two in the afternoon. The manager changes today's soup from tomato to pumpkin and writes it on the board in the office. The waiters on the floor started at noon, and they heard the specials once, at the start of their shift. So they keep offering tomato soup, and the kitchen keeps saying it has none. Nobody did anything wrong. The news reached the board, but not the people who had already heard the old version.

Last time, a Service gave our Pods one fixed number, and we noticed that each Pod still counted visits on its own. Today the app gets Redis and its settings from outside the image, and we meet the same trap as the waiters.

In this lesson, we'll hand settings to hello-devops, change them and see who notices. Then we'll look hard at passwords: what protects them, and what only looks like it does. Before we start, make a guess, and keep it in mind."""

NEW["guess"] = (
    "Your Deployment gives each Pod a setting, `GREETING`, from a ConfigMap (an object that holds settings), through `envFrom`. You change the value in the ConfigMap and apply it. What do the running Pods see?",
    "Environment variables are set once, when the container starts. Only files mounted from a ConfigMap are updated in place; for environment variables you restart the Pods, for example with `kubectl rollout restart`.",
)

NEW["terms"] = [
    "An object that stores plain settings as key-value pairs, for Pods to read as environment variables or files.",
    "An object like a ConfigMap, meant for passwords, tokens and keys, whose values are stored in base64.",
    "A container setting that turns every key of a ConfigMap or Secret into an environment variable.",
    "A way to write any bytes as plain letters and digits; anyone can turn it back, so it hides nothing.",
    "Locking data where it is stored, here Secrets inside etcd, so a copy of the disk reveals nothing.",
    "A ConfigMap with `immutable: true`, whose data can never be changed, only deleted and made again.",
    "A kubectl command that replaces a Deployment's Pods a few at a time, so they start with fresh settings.",
    "A tool that copies secrets from a vault, such as AWS Secrets Manager, into Kubernetes Secrets.",
]

S = []

S.append(("Settings belong outside the image", """
Since Part 5 you have built one image and changed how it behaves with environment variables. An image is the packed bundle a container starts from. An environment variable is a named setting a program reads when it starts. Our app, hello-devops, reads `GREETING` and `REDIS_HOST` this way. (Redis is the small database that will keep our shared visit count.)

The same image then runs on your laptop, in staging (the test copy) and in production, and only the settings differ. That is the twelve-factor rule, from a well-known list of habits for web apps: store config in the environment.

In Kubernetes you could write `env:` values straight into the Deployment. Most teams put them in a **ConfigMap** instead: a small object with a `data` section of keys and text values. It is the specials board in the office. The Deployment then stays the same in every environment, and only the ConfigMap differs. Several apps can share one, and whole config files fit too. Typical keys:
- Plain settings, such as a greeting, a log level or a switch that turns a feature on.
- Addresses of other services, such as `REDIS_HOST: redis`.
- Whole config files, such as an `application.yaml` for a Java service or an `nginx.conf`, stored as one long value.

Two limits to remember. A ConfigMap holds at most 1 MiB of data, about a million characters. And it is not secret at all: anyone who can read objects in the namespace can read it. Passwords go in a Secret, later in this lesson.

You can write a ConfigMap as YAML, or let kubectl build it from what you have:
- `--from-literal=GREETING=hi` for single values.
- `--from-file=app.yaml` for a whole file, with the file name as the key.
- `--from-env-file=.env` for a file of KEY=value lines.

Add `--dry-run=client -o yaml` to any of them, and you get a file to keep in Git instead of a change made only in the cluster. A board is no use until the staff read it. Next, we see the ways a container can.
"""))

S.append(("Three ways to hand a ConfigMap to a container", """
A Pod can use a ConfigMap in three ways, and you can mix them:
- `env` with `configMapKeyRef`: one key becomes one environment variable, and you can rename it on the way.
- `envFrom` with `configMapRef`: every key becomes an environment variable with the same name. The lab uses this, so `GREETING` and `REDIS_HOST` arrive as environment variables.
- A volume: every key becomes a file in a folder you choose. `items` picks only some keys, and `mountPath` says where the folder appears.

Environment variables are the briefing at the start of a shift: right for short values your code reads once, at start. Files are the board on the kitchen wall: right for whole config files and anything your code may read again later. A Spring Boot service (a popular Java web framework), for example, can read a mounted `application.yaml` from a folder.

What if the ConfigMap does not exist? The Pod cannot start. Its STATUS shows `CreateContainerConfigError`, and `kubectl describe pod` names the missing ConfigMap. Mark a reference `optional: true` if the app can live without it. Day 46 returns to this error.

The lab's `configmap.yaml` holds two keys, and `deployment.yaml` gains four lines of `envFrom`. Adding `envFrom` changes the Pod template, the recipe for each Pod, so applying it starts a normal rolling update. After it, every Pod has both settings, and `REDIS_HOST=redis` makes all Pods share one counter in Redis.

Now the question from the opening: what happens when the board changes during a shift?
"""))

S.append(("What happens when a ConfigMap changes", """
A ConfigMap is only data. No controller acts on it, and the Deployment controller watches its own Pod template, not the ConfigMaps the template names. The kubelet, the helper program on each node, reads it at two moments. It reads it when it starts a container, to fill in environment variables. And it reads it on its regular sync, a check it runs every so often, to refresh mounted files. So changing a ConfigMap never restarts anything. What a running Pod sees depends on how it reads the value:
- Environment variables are set once, when the container starts. They never change while it runs.
- Mounted files are updated in place. The kubelet notices the change on its next sync and swaps the files, usually within a minute or so.
- A file mounted with `subPath` (one file placed into an existing folder) is never updated.
- Even an updated file only helps if your app reads it again. Most apps read config once at start.

That is the answer to the guess, and it is our noon shift still selling tomato soup. For hello-devops, which uses environment variables, a new greeting needs new Pods. The tool for that is `kubectl rollout restart deployment/hello-devops`. It writes the current time into an annotation (a note) in the Pod template. The template changed, so the Deployment does a normal rolling update, and every new Pod starts with the new values.

Tools use a neater trick. They put something that changes with the config into the Pod template:
- Kustomize's `configMapGenerator` adds a hash (a short code worked out from the content) to the ConfigMap's name, such as `hello-config-7g2m9dfk8t`. New content means a new name and a new template, so a rollout happens by itself.
- Helm charts often put a checksum (the same kind of code) of the config into a template annotation, with the same effect.

Day 45 covers both tools. The hash in a name hints at a bigger idea, and the next section follows it.
"""))

S.append(("Immutable ConfigMaps and versioned names", """
Editing a ConfigMap in place has a hidden cost. A Deployment rollback brings back the old Pod template, but not the old ConfigMap. If you changed both and then roll back, the old code runs with the new settings. It is like reprinting last week's menu but leaving this week's prices on it.

The fix is to treat config like images: never change a version, make a new one.
1. Create `hello-config-v2` next to `hello-config-v1`.
2. Point the Deployment's `envFrom` at `hello-config-v2`. That is a template change, so a rollout starts.
3. To roll back, `kubectl rollout undo` brings back the template that points at `v1`, and `v1` still exists.

Kubernetes helps you keep that promise with `immutable: true`. Once set, nobody can change the data, and it cannot be switched off again. You can only delete the object and create a new one. Immutable ConfigMaps and Secrets also save work for the API server, because kubelets stop watching them for changes. That matters in clusters with thousands of them.

Kustomize's hash suffix does this for you: every content change gets a new, versioned name. For the lab, one plain ConfigMap and `rollout restart` are enough. Reach for versioned names once config changes start causing incidents.

So far every value was harmless: a greeting, a host name. Next, values that must stay hidden.
"""))

S.append(("Secrets, and why base64 is not encryption", """
A Secret looks like a ConfigMap, but it is meant for sensitive values: passwords, API tokens and TLS keys. A token is a long password that a program uses, and a TLS key is the private half of a web server's encryption. Pods use it the same three ways: `env` with `secretKeyRef`, `envFrom` with `secretRef`, or a volume.

Its values sit in `data`, written in base64. Base64 is a way to write any bytes as plain letters, so binary keys fit in YAML. It is not encryption. It is an envelope that was never sealed: anyone can reverse it with one command, as the worked example shows. You can also write plain text in a `stringData` field, and the API server converts it for you.

**Base64 hides a value from a glance, not from a person. Protect Secrets in other ways.**

Secrets have a `type` that tells tools what keys to expect:
- `Opaque`: anything you like. The default.
- `kubernetes.io/dockerconfigjson`: login details for a private registry (an image store) such as GHCR, used through `imagePullSecrets`.
- `kubernetes.io/tls`: a certificate and its private key, used by Gateways (Day 44).
- `kubernetes.io/basic-auth` and `kubernetes.io/ssh-auth`: a user and password, or an SSH key.

A Secret does get some protection that a ConfigMap does not:
- Kubernetes sends a Secret only to nodes that run a Pod that needs it.
- On the node, the kubelet keeps mounted Secrets in memory (tmpfs), never on disk.
- `kubectl describe` shows the size of each value, not the value.
- Access rules (RBAC, role-based access control) can allow reading ConfigMaps but not Secrets.

By default, though, Secrets are stored unencrypted in etcd, the cluster's database. And anyone who can create a Pod in a namespace can mount, and so read, every Secret in it. That is like letting anyone who may hire staff open every envelope in the office. Next, we close those gaps.
"""))

S.append(("Protecting Secrets inside the cluster", """
The Kubernetes docs list the steps that actually protect Secrets, and number 3 is the one people often forget:
1. Turn on encryption at rest. The API server then encrypts Secrets before writing them to etcd, so a stolen backup or disk shows nothing.
2. Limit who can read Secrets with RBAC (Day 46). Very few people and programs need `get` or `list` on Secrets.
3. Limit who can create Pods in namespaces that hold important Secrets, because a Pod can mount any Secret in its namespace.
4. Give each container only the Secrets it needs.

On a cluster you run yourself, encryption at rest means an `EncryptionConfiguration` file for the API server. The best setups use a KMS (key management service) provider, such as AWS KMS, which holds the real key outside the cluster. Managed clusters such as EKS, AKS and GKE, where the cloud runs the control plane, offer this with their own key services. Some turn it on by default, so check your provider's docs.

How the app reads a Secret matters too. Many teams prefer mounted files to environment variables, because environment variables are easy to leak. A crash report, a debug page or a `printenv` in a support session can print them all. A file is read only when the code asks for it.

Whatever you turn on in the cluster, a Secret manifest with real values must never go into Git, not even in a private repo. A team that commits one "because it is encoded" has published the value to everyone who can read the repo, and Git keeps every old version forever. If it happens, change the password or token at once, then move to one of the tools in the next section.

That leaves a puzzle: if Secrets cannot live in Git, how does a deploy from Git get them?
"""))

S.append(("Keeping Secrets out of Git", """
The first two answers below add a controller to the cluster along with a new kind of object, and the controller runs the Day 38 loop on it. A controller packaged like that is often called an operator. Teams pick one of these four:
- External Secrets Operator: the real value lives in a vault, a service built to store secrets, such as AWS Secrets Manager, Google Secret Manager or HashiCorp Vault. You commit an `ExternalSecret` object that says which value to fetch. A controller in the cluster fetches it, writes a normal Secret and refreshes it when the vault changes.
- Sealed Secrets: you lock a Secret with the cluster's public key, using the `kubeseal` tool, and commit the resulting `SealedSecret`. Only the controller in the cluster holds the private key that opens it.
- SOPS: you encrypt the values inside YAML files with a cloud key or an age key (age is a small file-encryption tool). The files go into Git, and your deploy tool decrypts them on the way in.
- The Secrets Store CSI Driver, a volume plugin. It mounts the vault's values straight into the Pod as files, often without creating a Kubernetes Secret at all.

Which one? If your company already has a vault, External Secrets Operator is the common choice, because the vault stays the single place to change a password. For a small team without one, Sealed Secrets is the simplest to start with.

Picture a payments team that wants config to roll back with the code, and database passwords never in Git. Each service's plain settings live in a ConfigMap generated by Kustomize, so every config change rolls the Pods and rolls back with the code. The passwords live in AWS Secrets Manager. External Secrets Operator copies them into the cluster every hour, and the clusters have KMS encryption at rest turned on.

hello-devops has no real secrets yet, so the lab has no Secret file. Day 48 shows how these tools fit into GitOps, and Day 64 goes deeper into secrets and access. Now the worked example lets you watch a change arrive, or not.
"""))

NEW["sections"] = S

NEW["drop"] = ["analogy", "real_world", "mistake"]

NEW["diagram_caption"] = "Both objects reach a container as environment variables (set once at start) or as mounted files (kept up to date by the kubelet)."

NEW["worked"] = [
    "Apply the demo from the examples folder in the scratch namespace (create it again with `kubectl create namespace scratch` if you deleted it). It creates a ConfigMap with `COLOR: blue` and a Pod that prints the value as an environment variable and as a file every 5 seconds.",
    "Change the value in the ConfigMap, then follow the logs. For a while nothing changes. After the kubelet's next sync, the file shows the new value. The environment variable never does.",
    "See how the kubelet swaps the file safely. The real data sits in a folder named after the time, and `..data` is a link (a pointer) to it. On a change, the kubelet writes a new folder and moves the link in one step, so the app never reads half a file. This link trick is also why `subPath` mounts never update.",
    "A bare Pod has no `rollout restart`, so replace it: `replace --force` deletes the Pod and creates it again from the same spec. The new container starts with the new environment variable.",
    "Now a Secret. Create one from a literal value, read the stored field, then decode it. Base64 kept the value out of sight for exactly one command.",
    "Delete the scratch namespace. Everything in it goes: the demo ConfigMap, the Pod and the Secret.",
]

NEW["task"] = (
    [
        "Write `k8s/configmap.yaml` and `k8s/redis.yaml`. Add `envFrom` to `k8s/deployment.yaml`, add both new files to `k8s/kustomization.yaml`, and run `kubectl apply -k k8s`.",
        "Follow the rollout that `envFrom` started. Then call `curl localhost:8081` several times: the greeting comes from the ConfigMap, and `visits` now counts up by one on every call, whichever Pod answers.",
        "Check what one container really has with `kubectl exec ... -- printenv GREETING`.",
        "Change `GREETING` in `configmap.yaml` and apply again. Call curl. Which greeting do you get, and why?",
        "Pick up the change with `kubectl rollout restart` and follow the rollout. Confirm that curl shows the new greeting.",
        "Find what `rollout restart` changed in the Pod template: print the template's annotations with a jsonpath query.",
        "Create a Secret named `hello-secret` in namespace `hello` with a key `API_TOKEN` and any fake value. Read it back with `-o yaml`, then decode it. Compare with what `kubectl describe secret` shows.",
        "Write down who in a real cluster could read that token. Then delete the Secret and commit the four files (not the Secret).",
    ],
    [
        "`kubectl get deploy hello-devops -n hello -o jsonpath='{.spec.template.metadata.annotations}'` prints the template's annotations.",
        "Pods stuck in `CreateContainerConfigError`? The name in `envFrom` must match the ConfigMap's `metadata.name` exactly, in the same namespace.",
        "`visits` still jumps around? Check that `REDIS_HOST` reached the Pods and that the Redis Pod is Running.",
    ],
    "After a rollout restart, `curl localhost:8081` shows your new greeting, and `visits` goes up by exactly one on each call no matter which Pod answers.",
)

NEW["explain_back"] = (
    "Explain in 3 to 4 sentences what happens to a running Deployment when you change its ConfigMap, and how you make the Pods use the new values. Mention env vars, mounted files and rollout restart.",
    "Changing a ConfigMap does not restart any Pod. Containers that read it as environment variables keep the old values, because those are set only when a container starts. Containers that mount it as files see the new content after the kubelet's next sync, if the app reads the file again. To make every Pod use new values, run `kubectl rollout restart`, which changes the Pod template and starts a normal rolling update. Tools like Kustomize get the same effect by giving each config version a new name.",
)

NEW["recap"] = [
    "ConfigMaps hold plain settings outside the image; Pods read them as env vars, envFrom or files.",
    "Env vars never change in a running container; mounted files update, except with subPath.",
    "`kubectl rollout restart` or a new ConfigMap name in the template moves Pods onto new config.",
    "Immutable, versioned ConfigMaps make config changes safe to roll back with the code.",
    "The limit of a Secret: base64 is not encryption, so add encryption at rest, RBAC and care about who can create Pods.",
    "Keep real secret values out of git with External Secrets Operator, Sealed Secrets or SOPS.",
]

NEW["closing"] = """We started with waiters who kept selling tomato soup after the board said pumpkin. Environment variables behave the same way: a running container keeps the briefing it got at the start, and only a new shift, a rollout restart, hears the change. Secrets added a second lesson: base64 is an unsealed envelope, and real protection comes from encryption and from who may open things. In your own repos, search for `kind: Secret` and check that no real value sits in Git. Next, we'll teach Kubernetes to tell a healthy Pod from a sick one. How does it know your app is ready, or stuck?"""

NEW["check"] = [
    ("An nginx Pod mounts `nginx.conf` from a ConfigMap as a whole folder. You change the ConfigMap. What happens?",
     "Mounted files are updated in place, but a program that read its config at start must reload it (or be restarted) to use the new file."),
    ("A teammate says: \"Our Secrets are safe, the YAML shows only base64.\" What is the best answer?",
     "Base64 is a format anyone can reverse; real protection is encrypting etcd and limiting who can read Secrets or create Pods."),
    ("You change both the image and the ConfigMap data of a Deployment, then roll back with `kubectl rollout undo`. Which combination runs now?",
     "Undo brings back the old Pod template, but a ConfigMap edited in place is not part of it, so the old code meets the new settings."),
]

NEW["interview"] = [
    ("What is the difference between a ConfigMap and a Secret?",
     "Both store key-value data that Pods read as environment variables or files. ConfigMaps are for settings that are not sensitive and are shown in plain text. Secrets are for sensitive data: values are base64-encoded, sent only to nodes that need them, kept in memory (tmpfs) on nodes and can be restricted separately with RBAC. They are not encrypted by default, so production clusters turn on encryption at rest, often with a KMS provider."),
    ("How do you make Pods pick up a changed ConfigMap?",
     "Environment variables are fixed at container start, so the Pods must be recreated, usually with `kubectl rollout restart`, which changes a template annotation and starts a rolling update. Mounted files update in place after the kubelet syncs, but the app has to reload them, and subPath mounts never update. A cleaner pattern is versioned or hash-suffixed ConfigMap names, as Kustomize's configMapGenerator does, so a config change is a template change and can be rolled back."),
    ("How would you manage secrets for apps deployed with GitOps?",
     "Never commit plain Secret manifests, because base64 is readable and git history is permanent. With an existing vault, I would use External Secrets Operator: git holds an ExternalSecret reference, and the controller syncs the real value from AWS Secrets Manager or Vault. Without one, Sealed Secrets or SOPS let you commit encrypted values that only the cluster or the deploy tool can decrypt. On top of that: encryption at rest, tight RBAC on Secrets and on Pod creation, and changing the value at once when anything leaks."),
]

NEW["deeper"] = """
A mounted ConfigMap updates after the kubelet's sync period plus the delay of its cache (its short-term copy). The docs give that formula instead of a number. By default the kubelet watches ConfigMaps, so the cache delay is small, and the sync period is about a minute. In practice, plan for up to a minute or two, and never for "instantly".

Projected volumes let one folder hold data from several sources. A `projected` volume can combine keys from ConfigMaps, Secrets, the Downward API and a short-lived ServiceAccount token. The Downward API gives facts about the Pod itself, such as its name and labels. The token is the Pod's own login for the API server. It all appears as files in one place, which is tidy for apps that expect a single config folder.

Three more details about Secrets:
- Environment variables from a Secret are visible to anything that can read the process environment. Inside the container that includes every child process. On the node, it includes anyone who can inspect the container.
- `kubectl get secret -o yaml` prints the values for anyone with `get` permission. The `describe` output hides them, but that is a convenience, not a control.
- A ServiceAccount used to get a long-lived token Secret automatically. Since Kubernetes 1.24 that no longer happens. Pods get short-lived tokens through a projected volume, and those expire and renew on their own.

Encryption at rest works like this on a self-managed cluster. You give the API server an `EncryptionConfiguration` file that lists providers for the `secrets` resource:
- `identity` means no encryption, which is the default.
- `aescbc`, `aesgcm` and `secretbox` encrypt with a key kept in the same file on the control-plane node.
- `kms` (version 2) asks an outside key service to wrap the data keys, so the real key never sits on the node.

The first provider in the list encrypts new writes, and all listed providers can decrypt. Existing Secrets stay as they were until they are written again. So after you turn encryption on, you rewrite every Secret once, for example with `kubectl get secrets -A -o json | kubectl replace -f -`.

On kind you could try this by mounting a config file into the control-plane node with `extraMounts` and a kubeadm patch. It is a good weekend exercise, not something you need for this course.

A Secret, like a ConfigMap, is limited to 1 MiB. If you find yourself storing large files in either, a volume or an object store is usually the better place.
"""
