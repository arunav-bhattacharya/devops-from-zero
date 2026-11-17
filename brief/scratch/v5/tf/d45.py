NEW = {}

NEW["goal"] = "By the end you can package hello-devops as a Helm chart, install, upgrade and roll back releases with Helm 4, and build dev and prod versions of the plain YAML with Kustomize overlays."

NEW["opening"] = """Picture the restaurant opening a second branch, then a third. The quickest plan is to photocopy the recipe binder for each kitchen. It works for a month. Then one branch cuts the salt in the soup, another changes the oven time, and a year later the three soups taste different. Nobody can say which changes were on purpose and which were accidents.

Last time, we added a front door and a disk, and our `k8s` folder grew to many files. Running the app for development, testing and production now means three copies of that folder. Copying is the fastest start, which is exactly why so many teams end up with three folders that slowly drift apart.

In this lesson, we'll try the two common cures. One is a recipe card with blanks that each branch fills in. The other is one master recipe with a few sticky notes per branch. Before we start, make a guess, and keep it in mind."""

NEW["guess"] = (
    "Helm, a tool that installs packaged apps, keeps a numbered history of each install. Revision 3 of your install is bad, so you run `helm rollback shop 1`. What does `helm history shop` show afterwards?",
    "Helm never rewrites history. A rollback applies what revision 1 had and records it as a new revision 4, described as \"Rollback to 1\".",
)

NEW["terms"] = [
    "A package of Kubernetes YAML with blanks to fill in, plus default values, in one folder.",
    "The settings that fill a chart's blanks, from values.yaml, -f files or --set.",
    "One installed copy of a chart in a namespace, with its own name.",
    "One numbered version of a release; every install, upgrade or rollback adds one.",
    "A tool built into kubectl that builds YAML from a base plus changes, with no blanks to fill in.",
    "A Kustomize folder that points at a base and lists the changes for one environment.",
    "A small description of changes to an object, applied on top of the base.",
    "An image store, such as ghcr.io, that can also store Helm charts.",
]

S = []

S.append(("Why package manifests at all", """
hello-devops now has more than ten YAML files, the plain text files that describe our objects. Running it for dev, staging and prod means three copies. Each copy needs its own image tag (the version label of the image), replica count and greeting, and prod also wants a disruption budget (Day 43). Copy the folder three times and the copies drift apart. Someone fixes a probe in prod and forgets dev. Six months later, nobody knows which differences are on purpose. That is the photocopied binder.

There are two popular answers, and they come from opposite directions:
- Templating, with Helm: write the YAML once with blanks, such as `replicas: {{ .Values.replicaCount }}`, and fill the blanks per environment from a values file. It is a recipe card with blanks for the amounts.
- Patching, with Kustomize: keep plain, valid YAML as a base, and describe each environment as a small set of changes on top of it. It is a master recipe with sticky notes.

Either way the result is ordinary Kubernetes YAML, and the API server never knows which tool made it. Argo CD (Day 47), a tool that deploys from Git, can use either one for the same reason.

At work you will meet both, often in the same cluster. Most outside software ships as Helm charts, and Kustomize is a common choice for a team's own services. Today you build one of each for hello-devops, starting with the recipe card.
"""))

S.append(("A Helm chart from the inside", """
Helm is the package manager for Kubernetes: a tool that installs, upgrades and removes packaged software, a bit like an app store for a cluster. A package is called a **chart**, and a chart is a folder:
- `Chart.yaml`: the chart's name, its own `version`, and the `appVersion` it deploys by default.
- `values.yaml`: the default settings.
- `templates/`: YAML files with blanks written in Go template syntax, a fill-in-the-blanks language.
- `templates/_helpers.tpl`: named snippets that other templates reuse. Files that start with `_` create no objects.
- `templates/NOTES.txt`: text Helm prints after an install, such as how to reach the app.

Inside a template, `{{ .Values.greeting }}` reads a value, `{{ .Release.Name }}` is the name you gave this install, and `{{ .Chart.AppVersion }}` comes from `Chart.yaml`. A pipe changes a value: `{{ .Values.greeting | quote }}` wraps it in quotes. A line such as `{{- if .Values.httpRoute.enabled }}` leaves a whole object out unless the value is true. The `-` trims the blank line the tag would leave.

The lab chart puts the same labels on every object with one helper: `{{- include "hello-devops.labels" . | nindent 4 }}`. The `include` function fills in the helper, and `nindent 4` starts a new line indented by 4 spaces, which YAML needs. Indentation is where most template bugs come from, so look at the result before you install. `helm template hello chart/hello-devops` prints the final YAML, and `helm lint` checks the chart for mistakes. Neither touches the cluster.

The chart borrows one trick from the [Helm tips page](https://helm.sh/docs/howto/charts_tips_and_tricks/). A `checksum/config` annotation on the Pod template holds a hash (a short code worked out from the content) of the ConfigMap. Change the greeting, the hash changes, and the Deployment rolls out new Pods that read it. You met the same idea on Day 42.

A chart is only a folder until you install it. Next, we follow what happens when you do.
"""))

S.append(("Releases, revisions and rollbacks", """
When you install a chart, Helm creates a release: one named copy of the chart in one namespace, like one branch's copy of the recipe card. You can install the same chart many times under different names. Every install, upgrade or rollback adds a numbered revision, and Helm stores each revision as a Secret in the release's namespace. Helm has no server of its own, so the cluster is its memory. Any laptop or CI job (the automatic checks that run on every change) with access sees the same history.

The commands follow a release's life:
1. `helm install hello chart/hello-devops -f chart/kind-values.yaml` fills the blanks with your values, applies, and records revision 1.
2. `helm upgrade hello chart/hello-devops -f chart/kind-values.yaml` fills them again and applies the difference as revision 2.
3. `helm history hello` lists the revisions and their status.
4. `helm rollback hello 1` applies what revision 1 had, recorded as a new revision 3. History is never rewritten, which is the answer to the guess.
5. `helm uninstall hello` deletes every object the release created.

`helm upgrade --install` installs when the release does not exist yet and upgrades when it does. CI pipelines use it so one command works both times.

Helm builds the values from layers, in order: the chart's `values.yaml`, then each `-f` file, then `--set`. When two layers set the same key, the later one wins. Now the surprise. If you pass any values on `helm upgrade`, Helm starts from the chart's defaults plus only the values you pass now. Say you installed with a values file and later run an upgrade with one new `--set`. The settings from install time quietly disappear. With no values at all, Helm reuses the last ones.

**Keep your settings in a values file, and pass it with `-f` every time.** `helm get values` shows what a release uses now.

By default, `helm install` returns once the API server has the objects, before the Pods are ready. Add `--wait` to wait for them, and `--rollback-on-failure` to undo an upgrade that fails. That last flag has a new name in Helm 4, which is next.
"""))

S.append(("What changed in Helm 4", """
Helm 4.0 came out in November 2025, the first major version in six years. Day to day it feels like Helm 3, and charts with `apiVersion: v2` work unchanged. The changes you will notice:
- Server-side apply is the default for new releases. Helm 3 worked out each change itself; now the API server merges the changes and tracks which tool owns each field. Upgrades and rollbacks keep the method the release started with, so old Helm 3 releases stay on client-side apply.
- Two flags were renamed: `--atomic` is now `--rollback-on-failure`, and `--force` is now `--force-replace`. The old names still work but print a warning, and older blog posts use them.
- `--wait` is smarter about when each kind of object is ready.
- You can install a chart by digest, `oci://...@sha256:...`. A digest is a fingerprint of the exact file, so you get exactly the bytes you tested.

Helm 3 is at the end of its life. Its last feature release came out on September 9, 2026, and its security fixes stop on February 10, 2027. Install Helm 4 and learn its flag names. A few smaller changes are in Go deeper.

A new chart format, Charts v3, is experimental and hidden behind `HELM_EXPERIMENTAL_CHART_V3=1`. You can ignore it for now.

The digest bullet mentioned `oci://`. That address points to a place you already know from Day 27, and the next section explains how.
"""))

S.append(("Charts in OCI registries", """
Charts have long been shared through chart repositories: web servers with an `index.yaml` that lists every chart, added with `helm repo add`. You can also share a chart through the same kind of registry that stores your images. Helm calls this OCI support, after the Open Container Initiative standard that registries follow. Your images and charts then share one registry and one login.

The flow has three commands:
1. `helm package chart/hello-devops` makes `hello-devops-0.2.0.tgz`, a packed file named after the chart version.
2. `helm push hello-devops-0.2.0.tgz oci://ghcr.io/<your-github-user>/charts` uploads it to GitHub's registry, next to your image from Day 27.
3. `helm install hello oci://ghcr.io/<your-github-user>/charts/hello-devops --version 0.2.0` installs it on any cluster.

Log in once with `helm registry login ghcr.io -u <your-github-user>` and a GitHub token (a long password for programs) that can write packages. Always pin `--version`, for the same reason you never deploy `:latest` images: you want the same chart today and next month. Most outside projects publish this way now. Envoy Gateway's chart on Day 44 came from `oci://docker.io/envoyproxy/gateway-helm`.

Your `Chart.yaml` holds two version numbers, and people mix them up. The `version` field is the chart's own version: bump it on every change to the chart, so one number always means the same files. The `appVersion` field is the version of the app inside, which the lab chart uses as the default image tag. One is the edition of the recipe card, the other is the dish it makes.

That is the recipe card. Next, the master recipe with sticky notes.
"""))

S.append(("Kustomize: a base and overlays", """
Kustomize is built into kubectl, and you have already used it: `kubectl apply -k k8s` reads `k8s/kustomization.yaml`. That folder is the base, the master recipe. An overlay is another folder with its own `kustomization.yaml` that points at the base and lists changes. It is one branch's sticky notes:
- `resources: [../../k8s]` pulls in the base. An overlay can add files too, such as prod's `pdb.yaml`.
- `namespace: hello-prod` moves every object into one namespace, and renames the Namespace object as well.
- `images` finds every container that uses a given image name and changes its tag, without touching the Deployment file.
- `replicas` sets a Deployment's replica count, and `labels` adds a label such as `env: prod` to every object and Pod.
- `patches` changes anything else.

Patches come in two styles. A strategic merge patch looks like a small piece of the object with only the changed fields; prod's `deployment-patch.yaml` is one. Kustomize finds the object to patch by its kind and name. In lists such as `containers`, it matches items by their `name`, so a patch for `web` leaves other containers alone. A JSON patch is a list of steps, such as "replace `/spec/minReplicas` with 4". JSON patches suit one exact field, or removing one, like the `nodePort` that both overlays drop.

An overlay cannot live inside its base folder, even though that looks like the natural place for it. An overlay at `k8s/overlays/prod` that points at `../../` fails with "cycle detected", because the base would contain the overlay. So the lab keeps `overlays/` next to `k8s/`.

Three commands cover daily use:
- `kubectl kustomize overlays/prod` prints the result.
- `kubectl diff -k overlays/prod` shows what would change in the cluster.
- `kubectl apply -k overlays/prod` applies it.

Two tools, one goal. Next, how to choose between them.
"""))

S.append(("Helm or Kustomize, or both", """
Which tool fits depends mostly on whose software it is:
- Someone else's software, such as Envoy Gateway, metrics-server or a monitoring stack: Helm. Those projects ship as charts, and their values are the supported way to configure them.
- Your own app with a few differences per environment: either works. Kustomize keeps every file as plain YAML that anyone can read.
- Your own app installed by many teams with many settings: Helm, because values give each team one clear place to set things.

They also combine. You can fill in a chart with `helm template` and keep the output as a Kustomize base. Kustomize can also fill in charts itself through its `helmCharts` field, with the `--enable-helm` flag. Argo CD (Day 47) builds both straight from Git, and Day 48 builds on these overlays to move a release from one environment to the next.

Picture a team that works this way. Outside tools such as Envoy Gateway and the monitoring stack come in as Helm charts, pinned to exact versions in an OCI registry. Each in-house service gets one Kustomize base, with overlays for dev, staging and prod. Promoting a release is a pull request (a proposed change that teammates review) that changes `newTag` in the next overlay, and Argo CD applies it.

Each tool has a limit. Helm templates get hard to read once every field becomes a value; a `values.yaml` that repeats the whole Deployment has gone too far. Kustomize gets confusing when an overlay changes half the base. At that point the base is wrong, and it should change instead.

My default for a team's own services is Kustomize with one base and small overlays, and Helm for everything installed from outside. The worked example builds two branches from one base.
"""))

NEW["sections"] = S

NEW["drop"] = ["analogy", "real_world", "mistake"]

NEW["diagram_caption"] = "Two roads to the same place: Helm fills blanks, Kustomize patches a base. The cluster only sees plain YAML."

NEW["worked"] = [
    "The dev overlay runs a newer image, so build it and load it into kind first. The build arg bakes the version into the app's answer.",
    "Build dev without touching the cluster. The greeting, the tag, the replica count and the Service type all come from the overlay. The second `replicas: 1` belongs to Redis, which the overlay leaves alone.",
    "Build prod. Same base, different answers, plus one extra object: the PodDisruptionBudget that only `overlays/prod` adds.",
    "Why `overlays/` sits next to `k8s/` and not inside it: Kustomize refuses an overlay inside its own base. This is the error you would get (long paths shortened).",
    "Apply both. Each overlay creates its own namespace, so dev, prod and the base app in `hello` run side by side. Both overlays switched the Service to ClusterIP, because NodePort 30080 is already taken by the base app.",
    "List every hello-devops Pod in the cluster with its `env` label. The base app has no label; dev has 1 Pod and prod has 4.",
    "Call dev through a port-forward. The new version and the dev greeting prove that the overlay's changes reached the running app.",
]

NEW["task"] = (
    [
        "Write the chart in `chart/hello-devops/` and `chart/kind-values.yaml` from the files above, then run `helm lint chart/hello-devops`.",
        "Render it with `helm template` and your values file. Find the labels from the helper, the image tag and the HTTPRoute in the output.",
        "Install it as release `hello` in namespace `hello-helm` with `chart/kind-values.yaml`, and read the NOTES that Helm prints.",
        "With the Envoy port-forward from Day 44 running, call `curl -H \"Host: helm.local\" localhost:8888` and check the greeting.",
        "Change the greeting in `chart/kind-values.yaml`, run `helm upgrade` with the same file, and watch the Pods roll. Then run `helm history`.",
        "Roll back to revision 1, run `helm history` again, and curl once more.",
        "Upgrade with your values file plus `--set autoscaling.enabled=true`. Use `helm get manifest` to confirm that an HPA appeared and `replicas` left the Deployment.",
        "Package the chart with `helm package`. Optional: log in to GHCR, push it, and install it from `oci://` into a new namespace.",
        "Clean up with `helm uninstall`, and delete the `hello-dev` and `hello-prod` namespaces from the worked example.",
    ],
    [
        "Release names are unique per namespace, and most helm commands need `-n hello-helm`. `helm list -A` shows every release in the cluster.",
        "Greeting back to the chart default after an upgrade? You passed values without the file. `helm get values hello -n hello-helm` shows what the release uses now.",
        "Curl returns the base app's greeting instead of Helm's? Your request did not match the chart's route. Check the Host header and `kubectl get httproute -A`.",
    ],
    "`helm history hello -n hello-helm` shows install, upgrade and a \"Rollback to 1\" revision, and the curl through the Gateway shows the greeting from revision 1.",
)

NEW["explain_back"] = (
    "Explain in 3 to 4 sentences how Helm and Kustomize each turn one set of files into a dev and a prod version of an app. Say which you would use for hello-devops and why.",
    "Helm keeps templates with blanks and fills them from a values file. Dev and prod are then two values files for the same chart, and each install is a release with revisions. Kustomize keeps plain YAML as a base and puts each environment's changes in an overlay folder, as patches, image tags and replica counts. Both produce ordinary YAML that the cluster applies. For hello-devops I would use Kustomize, because the differences are small and the files stay readable, and keep Helm for the outside tools I install.",
)

NEW["recap"] = [
    "Helm fills blanks from values; Kustomize patches a plain base. Both produce ordinary YAML.",
    "A chart is Chart.yaml, values.yaml, templates, helpers and NOTES; render with `helm template` before installing.",
    "Every install, upgrade and rollback is a revision; rollback adds a new one instead of rewriting history.",
    "A limit to remember: passing values on upgrade drops earlier ones, so pass the same values file every time.",
    "Helm 4: server-side apply for new releases, `--rollback-on-failure` and `--force-replace`; Helm 3 security fixes end February 10, 2027.",
    "Overlays point at a base with `resources`, then set namespace, images, replicas, labels and patches; never put them inside the base.",
]

NEW["closing"] = """We started with a photocopied recipe binder and three soups that slowly tasted different. Helm answers with one recipe card and a values file per branch, plus a logbook of every install. Kustomize answers with one master recipe and a few sticky notes per branch. When you upgrade in the task, run `helm get values` afterwards and make sure nothing you set earlier went missing. All of this still assumes the cluster behaves. Next, we'll break it on purpose, in many small ways, and learn to read the clues. When a Pod will not start, where do you look first?"""

NEW["check"] = [
    ("A chart's `values.yaml` says `replicaCount: 2`. You installed with `-f prod.yaml`, which sets 5. Now you run `helm upgrade web ./chart --set image.tag=1.2.0` only. How many replicas run afterwards?",
     "Passing any values on upgrade means chart defaults plus only the new values, so prod.yaml's 5 is dropped and the default 2 applies."),
    ("Prod needs a bigger memory limit on the base Deployment's `web` container, and nothing else changes. What do you add to the prod overlay?",
     "A strategic merge patch names the Deployment and container and lists only the changed fields; Kustomize merges it into the base."),
    ("An old CI script runs `helm upgrade --install api ./chart --atomic`. What happens with Helm 4?",
     "Helm 4 renamed `--atomic` to `--rollback-on-failure` and keeps the old name working with a warning that it is going away."),
]

NEW["interview"] = [
    ("When would you choose Helm, and when Kustomize?",
     "Helm is a package manager with templates and release history, and it is the standard way to install and upgrade outside software. Kustomize keeps plain YAML and adds per-environment overlays, which suits a team's own services with small differences. Helm's templates are powerful but get hard to read, while Kustomize gets messy if overlays rewrite most of the base. Many teams use Helm for platform tools and Kustomize for their own apps, and GitOps tools such as Argo CD render both."),
    ("What is a Helm release, and how does a rollback work?",
     "A release is one installed copy of a chart, with a name, a namespace and a numbered history of revisions stored as Secrets. Each install, upgrade or rollback adds a revision. It holds the rendered manifest and the values used. `helm rollback` re-applies an earlier revision's manifest and records it as a new revision, so history is never lost. In Helm 4 it also keeps the apply method the release started with, client-side or server-side."),
    ("How do you manage different settings for dev, staging and prod?",
     "I keep one source of truth for the app and express each environment as a small difference. With Helm that is one values file per environment; with Kustomize, one overlay per environment. Image tags are pinned per environment, so promotion is a reviewed change that copies a tag from one environment to the next. Secrets stay out of those files and come from a secret manager. Rendering every environment in CI, with `helm template` or `kubectl kustomize`, catches mistakes before they reach a cluster."),
]

NEW["deeper"] = """
Helm keeps its memory inside the cluster. Each revision of a release is a Secret of type `helm.sh/release.v1` in the release's namespace, named like `sh.helm.release.v1.hello.v3`. List them with `kubectl get secrets -n hello-helm -l owner=helm`. Each one holds the chart, the values and the rendered manifest, compressed and encoded. Helm keeps the last 10 revisions per release by default; `--history-max` changes that.

Because Helm works from these records, it knows what it applied but not what is in the cluster now. If someone runs `kubectl edit` on a Deployment that Helm manages, Helm does not notice until the next upgrade. What happens then depends on the apply method:
- With server-side apply, the default for new Helm 4 releases, the API server tracks which manager owns each field. A field changed by hand now has a different owner, so Helm can report a conflict instead of silently overwriting it. `--force-conflicts` takes the field back.
- With client-side apply, Helm compares the old manifest, the new one and the live object, and patches the difference. Hand edits to fields the chart does not set survive; edits to fields it does set are overwritten.

Either way, hand edits make the next upgrade harder to predict. Argo CD (Day 47) fixes this by watching for drift all the time and showing it.

Three smaller Helm 4 changes: `--wait` now uses kstatus, a status library, to judge readiness. Post-renderers (programs that edit Helm's output before it is applied, often Kustomize) are now plugins. And `helm registry login` takes only the host name.

Two Helm features you will meet in outside charts:
- Hooks: templates with a `helm.sh/hook` annotation run at set points, such as a database migration Job (a Pod that runs once, to completion) before an upgrade.
- Tests: Pods with the `test` hook that `helm test <release>` runs after an install, to check the app answers.

On the Kustomize side, look at `configMapGenerator`. It builds a ConfigMap from literals or files and adds a hash of the content to its name, such as `hello-config-h622489h5k`. Kustomize also updates every reference to that name. Change a value, the name changes, the Pod template changes, and the Deployment rolls out by itself. It is the Kustomize version of the chart's `checksum/config` trick.
"""
