"""Day 37: Packaging with Helm and Kustomize."""
from svg import arrow, box, cap, svg


def diagram():
    h = 44
    p = [
        box(16, 20, 128, h, "bx", "templates"),
        box(16, 76, 128, h, "bx", "values.yaml"),
        box(184, 48, 104, h, "bxo", "helm"),
        box(16, 148, 128, h, "bx", "k8s/ base"),
        box(16, 204, 128, h, "bx", "overlays/prod"),
        box(184, 176, 104, h, "bxg", "kustomize"),
        box(320, 112, 112, h, "bxt", "plain YAML"),
        box(456, 112, 96, h, "bxp", "cluster"),
        arrow(144, 42, 182, 62), arrow(144, 98, 182, 80),
        arrow(144, 170, 182, 190), arrow(144, 226, 182, 208),
        arrow(288, 74, 318, 124), arrow(288, 194, 318, 146),
        arrow(432, 134, 454, 134),
        cap(236, 108, "fill the blanks"), cap(236, 238, "apply patches"),
    ]
    return svg(262, "Helm fills templates with values and Kustomize patches a base with an overlay; both produce plain YAML for the cluster", p)


WORKED_BUILD = """$ docker build --build-arg APP_VERSION=1.1.0 -t hello-devops:1.1.0 .
$ kind load docker-image hello-devops:1.1.0 --name devops"""

DEV_RENDER = """$ kubectl kustomize overlays/dev | grep -E "GREETING|image: hello|replicas: [0-9]|type: ClusterIP"
  GREETING: Hello from dev!
  type: ClusterIP
  replicas: 1
        image: hello-devops:1.1.0
  replicas: 1"""

PROD_RENDER = """$ kubectl kustomize overlays/prod | grep -E "GREETING|image: hello|replicas: [0-9]|type: ClusterIP"
  GREETING: Hello from prod!
  type: ClusterIP
  replicas: 4
        image: hello-devops:1.0.0
  replicas: 1
$ kubectl kustomize overlays/prod | grep "^kind:" | sort | uniq -c
   1 kind: ConfigMap
   2 kind: Deployment
   1 kind: HorizontalPodAutoscaler
   1 kind: Namespace
   1 kind: PodDisruptionBudget
   2 kind: Service"""

CYCLE = """$ kubectl kustomize k8s/overlays/prod
error: accumulating resources: accumulation err='accumulating resources from '../../':
  ... cycle detected: candidate root '/Users/you/code/hello-devops/k8s'
  contains visited root '/Users/you/code/hello-devops/k8s/overlays/prod'"""

APPLY = """$ kubectl apply -k overlays/dev
namespace/hello-dev created
configmap/hello-config created
service/hello-devops created
service/redis created
deployment.apps/hello-devops created
deployment.apps/redis created
horizontalpodautoscaler.autoscaling/hello-devops created
$ kubectl apply -k overlays/prod"""

PODS = """$ kubectl get pods -A -l app=hello-devops -L env
NAMESPACE    NAME                            READY   STATUS    RESTARTS   AGE   ENV
hello        hello-devops-6c9f8b7d4-2qkzt    1/1     Running   0          2d
hello        hello-devops-6c9f8b7d4-8hx7m    1/1     Running   0          2d
hello        hello-devops-6c9f8b7d4-tr5vn    1/1     Running   0          2d
hello-dev    hello-devops-7f5d6c9b8-xm4rp    1/1     Running   0          50s   dev
hello-prod   hello-devops-5b8c7d6f9-4wq9z    1/1     Running   0          35s   prod
hello-prod   hello-devops-5b8c7d6f9-9kdlp    1/1     Running   0          35s   prod
hello-prod   hello-devops-5b8c7d6f9-hb2nx    1/1     Running   0          35s   prod
hello-prod   hello-devops-5b8c7d6f9-t7m4c    1/1     Running   0          35s   prod"""

CURL = """$ kubectl -n hello-dev port-forward svc/hello-devops 8082:80 &
$ curl -s localhost:8082 | jq .
{
  "host": "hello-devops-7f5d6c9b8-xm4rp",
  "message": "Hello from dev!",
  "version": "1.1.0",
  "visits": 1
}"""

LESSON = {
    "id": "d37",
    "title": "Packaging with Helm and Kustomize",
    "minutes": 50,
    "goal": "By the end you can package hello-devops as a Helm chart, install, upgrade and roll back releases with Helm 4, and build dev and prod versions of the plain YAML with Kustomize overlays.",
    "guess": {
        "q": "Revision 3 of your Helm release is bad, so you run `helm rollback shop 1`. What does `helm history shop` show afterwards?",
        "options": [
            "Revisions 2 and 3 are gone, and 1 is current again",
            "A new revision 4 that has the same content as revision 1",
            "Revision 1 marked deployed, with no new revision",
            "Nothing changes until you also run `helm upgrade`",
        ],
        "answer": 1,
        "why": "Helm never rewrites history. A rollback applies what revision 1 had and records it as a new revision 4, described as \"Rollback to 1\".",
    },
    "terms": [
        {"term": "Helm chart", "plain": "A package of templated Kubernetes YAML plus default values, in one folder."},
        {"term": "Values", "plain": "The settings that fill a chart's templates, from values.yaml, -f files or --set."},
        {"term": "Release", "plain": "One installed copy of a chart in a namespace, with its own name."},
        {"term": "Revision", "plain": "One numbered version of a release; every install, upgrade or rollback adds one."},
        {"term": "Kustomize", "plain": "A tool built into kubectl that builds YAML from a base plus changes, without templates."},
        {"term": "Overlay", "plain": "A Kustomize folder that points at a base and lists the changes for one environment."},
        {"term": "Patch", "plain": "A small description of changes to an object, applied on top of the base."},
        {"term": "OCI registry", "plain": "A registry such as ghcr.io that stores images, and also Helm charts."},
    ],
    "sections": [
        {
            "h": "Why package manifests at all",
            "body": (
                "hello-devops now has more than ten YAML files. Imagine running it three times, for dev, staging and prod. "
                "Each copy needs a different image tag, replica count and greeting, and prod also wants a disruption budget. "
                "If you copy the folder three times, the copies drift apart. Someone fixes a probe in prod and forgets dev. "
                "Six months later, nobody knows which differences are on purpose.\n\n"
                "There are two popular answers, and they come from opposite directions:\n"
                "- Templating, with Helm: write the YAML once with blanks, such as `replicas: {{ .Values.replicaCount }}`, and fill the blanks per environment from a values file.\n"
                "- Patching, with Kustomize: keep plain, valid YAML as a base, and describe each environment as a small set of changes on top of it.\n\n"
                "Both end the same way. They render ordinary Kubernetes YAML, and the API server never knows which tool made it. "
                "That is also why Argo CD (Day 39) can deploy with either one.\n\n"
                "You will use both at work, often in the same cluster. Helm is how most third-party software ships. "
                "Kustomize is a common choice for a team's own services. This lesson builds one of each for hello-devops."
            ),
            "refs": [
                {"title": "Helm vs Kustomize: the fight between templating and patching (DevOps Toolkit)", "url": "https://www.youtube.com/watch?v=ZMFYSm0ldQ0", "kind": "watch"},
                {"title": "Using Helm", "url": "https://helm.sh/docs/intro/using_helm/", "kind": "docs"},
            ],
        },
        {
            "h": "A Helm chart from the inside",
            "body": (
                "Helm is the package manager for Kubernetes, a bit like Homebrew for apps in a cluster. A package is called a **chart**, and a chart is a folder:\n"
                "- `Chart.yaml`: the chart's name, its own `version`, and the `appVersion` it deploys by default.\n"
                "- `values.yaml`: the default settings.\n"
                "- `templates/`: YAML files with placeholders in Go template syntax.\n"
                "- `templates/_helpers.tpl`: named snippets that other templates reuse. Files that start with `_` render no objects.\n"
                "- `templates/NOTES.txt`: text Helm prints after an install, such as how to reach the app.\n\n"
                "Inside a template, `{{ .Values.greeting }}` reads a value, `{{ .Release.Name }}` is the name you gave this install, and `{{ .Chart.AppVersion }}` comes from `Chart.yaml`. "
                "A pipe changes a value: `{{ .Values.greeting | quote }}` wraps it in quotes. "
                "A line such as `{{- if .Values.httpRoute.enabled }}` leaves a whole object out unless the value is true. The `-` trims the blank line the tag would leave.\n\n"
                "The lab chart puts the same labels on every object with one helper: `{{- include \"hello-devops.labels\" . | nindent 4 }}`. "
                "The `include` function renders the helper, and `nindent 4` starts a new line indented by 4 spaces, which YAML needs. "
                "Indentation is where most template bugs come from, so render before you install. "
                "`helm template hello chart/hello-devops` prints the final YAML, and `helm lint` checks the chart for mistakes. Neither touches the cluster.\n\n"
                "The chart also has a small trick from the [Helm tips page](https://helm.sh/docs/howto/charts_tips_and_tricks/). "
                "A `checksum/config` annotation on the Pod template holds a hash of the ConfigMap. Change the greeting, the hash changes, and the Deployment rolls out new Pods that read it."
            ),
            "refs": [
                {"title": "Chart template guide: named templates", "url": "https://helm.sh/docs/chart_template_guide/named_templates/", "kind": "docs"},
                {"title": "Chart tips and tricks", "url": "https://helm.sh/docs/howto/charts_tips_and_tricks/", "kind": "docs"},
                {"title": "What is Helm in Kubernetes? Helm and Helm charts explained (TechWorld with Nana; its Tiller part is Helm 2 history)", "url": "https://www.youtube.com/watch?v=-ykwb1d0DXU", "kind": "watch"},
            ],
        },
        {
            "h": "Releases, revisions and rollbacks",
            "body": (
                "When you install a chart, Helm creates a release: one named copy of the chart in one namespace. You can install the same chart many times under different names. "
                "Every install, upgrade or rollback adds a numbered revision, and Helm stores each revision as a Secret in the release's namespace.\n\n"
                "The commands follow a release's life:\n"
                "1. `helm install hello chart/hello-devops -f chart/kind-values.yaml` renders with your values, applies, and records revision 1.\n"
                "2. `helm upgrade hello chart/hello-devops -f chart/kind-values.yaml` renders again and applies the difference as revision 2.\n"
                "3. `helm history hello` lists the revisions and their status.\n"
                "4. `helm rollback hello 1` applies what revision 1 had, recorded as a new revision 3. History is never rewritten.\n"
                "5. `helm uninstall hello` deletes every object the release created.\n\n"
                "`helm upgrade --install` installs when the release does not exist yet and upgrades when it does. CI pipelines use it so one command works both times.\n\n"
                "One rule surprises nearly everyone. If you pass any values on `helm upgrade`, Helm starts from the chart's defaults plus only the values you pass now. "
                "Values you passed at install time are dropped. With no values at all, it reuses the last ones. "
                "So keep your settings in a values file and pass it with `-f` every time.\n\n"
                "By default, `helm install` returns once the API server has the objects, before the Pods are ready. "
                "Add `--wait` to wait for them, and `--rollback-on-failure` to undo an upgrade that fails."
            ),
            "refs": [
                {"title": "Using Helm: install, upgrade and rollback", "url": "https://helm.sh/docs/intro/using_helm/", "kind": "docs"},
            ],
        },
        {
            "h": "What changed in Helm 4",
            "body": (
                "Helm 4.0 came out in November 2025, the first major version in six years. Day to day it feels like Helm 3, and charts with `apiVersion: v2` work unchanged. "
                "A few changes matter to you:\n"
                "- Server-side apply is the default for new releases. The API server merges the changes and tracks which tool owns each field. Upgrades and rollbacks keep the method the release started with, so old Helm 3 releases stay on client-side apply.\n"
                "- Two flags were renamed: `--atomic` is now `--rollback-on-failure`, and `--force` is now `--force-replace`. The old names still work but print a warning, and older blog posts use them.\n"
                "- `--wait` uses kstatus to tell when objects are really ready.\n"
                "- You can install a chart by digest, `oci://...@sha256:...`, so you get exactly the bytes you tested.\n"
                "- Post-renderers are now plugins, and `helm registry login` takes only the host name.\n\n"
                "Helm 3 is at the end of its life. Its last feature release came out on September 9, 2026, and its security fixes stop on February 10, 2027. "
                "Install Helm 4 and learn its flag names.\n\n"
                "A new chart format, Charts v3, is experimental and hidden behind `HELM_EXPERIMENTAL_CHART_V3=1`. You can ignore it for now."
            ),
            "refs": [
                {"title": "Helm 4 overview", "url": "https://helm.sh/docs/overview", "kind": "docs"},
                {"title": "Helm 3 end of life (Helm blog)", "url": "https://helm.sh/blog/helm-v3-end-of-life", "kind": "read"},
                {"title": "Helm 4 released (Helm blog)", "url": "https://helm.sh/blog/helm-4-released", "kind": "read"},
            ],
        },
        {
            "h": "Charts in OCI registries",
            "body": (
                "You can share a chart through the same kind of registry that stores your images. "
                "Helm calls this OCI support, after the Open Container Initiative standard that registries follow.\n\n"
                "The flow has three commands:\n"
                "1. `helm package chart/hello-devops` makes `hello-devops-0.2.0.tgz`, named after the chart version.\n"
                "2. `helm push hello-devops-0.2.0.tgz oci://ghcr.io/<your-github-user>/charts` uploads it to GitHub's registry, next to your image from Day 21.\n"
                "3. `helm install hello oci://ghcr.io/<your-github-user>/charts/hello-devops --version 0.2.0` installs it on any cluster.\n\n"
                "Log in once with `helm registry login ghcr.io -u <your-github-user>` and a GitHub token that can write packages. "
                "Always pin `--version`, for the same reason you never deploy `:latest` images: you want the same chart today and next month. "
                "Most third-party projects publish this way now. Envoy Gateway's chart on Day 36 came from `oci://docker.io/envoyproxy/gateway-helm`.\n\n"
                "Your `Chart.yaml` holds two version numbers, and people mix them up. "
                "The `version` field is the chart's own version: bump it on every change to the chart, so one number always means the same files. "
                "The `appVersion` field is the version of the app inside, which the lab chart uses as the default image tag."
            ),
            "refs": [
                {"title": "Use OCI-based registries (Helm docs)", "url": "https://helm.sh/docs/topics/registries/", "kind": "docs"},
            ],
        },
        {
            "h": "Kustomize: a base and overlays",
            "body": (
                "Kustomize is built into kubectl, and you have already used it: `kubectl apply -k k8s` reads `k8s/kustomization.yaml`. "
                "That folder is the base. An **overlay** is another folder with its own `kustomization.yaml` that points at the base and lists changes:\n"
                "- `resources: [../../k8s]` pulls in the base. An overlay can add files too, such as prod's `pdb.yaml`.\n"
                "- `namespace: hello-prod` moves every object into one namespace, and renames the Namespace object as well.\n"
                "- `images` changes an image tag without touching the Deployment file.\n"
                "- `replicas` sets a Deployment's replica count, and `labels` adds a label such as `env: prod` to every object and Pod.\n"
                "- `patches` changes anything else.\n\n"
                "Patches come in two styles. A strategic merge patch looks like a small piece of the object with only the changed fields; prod's `deployment-patch.yaml` is one. "
                "A JSON patch is a list of operations, such as \"replace `/spec/minReplicas` with 4\". "
                "JSON patches suit one exact field, or removing one, like the `nodePort` that both overlays drop.\n\n"
                "Kustomize has a layout rule that trips people up. An overlay cannot live inside its base folder. "
                "An overlay at `k8s/overlays/prod` that points at `../../` fails with \"cycle detected\", because the base would contain the overlay. "
                "That is why the lab keeps `overlays/` next to `k8s/`.\n\n"
                "Three commands do the work: `kubectl kustomize overlays/prod` prints the result, `kubectl diff -k overlays/prod` shows what would change in the cluster, and `kubectl apply -k overlays/prod` applies it."
            ),
            "refs": [
                {"title": "Declarative management of Kubernetes objects using Kustomize", "url": "https://kubernetes.io/docs/tasks/manage-kubernetes-objects/kustomization/", "kind": "docs"},
                {"title": "Should we template or patch Kubernetes manifests? Helm vs Kustomize side by side", "url": "https://www.youtube.com/watch?v=Q19x62ZrR-U", "kind": "watch"},
            ],
        },
        {
            "h": "Helm or Kustomize, or both",
            "body": (
                "Pick the tool that matches the job:\n"
                "- Someone else's software, such as Envoy Gateway, metrics-server or a monitoring stack: Helm. That is how those projects ship, and their values are the supported way to configure them.\n"
                "- Your own app with a few differences per environment: either works. Kustomize keeps every file as plain YAML that anyone can read.\n"
                "- Your own app installed by many teams with many settings: Helm, because values give each team one clear place to set things.\n\n"
                "They also combine. You can render a chart with `helm template` and keep the output as a Kustomize base. "
                "Kustomize can also render charts itself through its `helmCharts` field, with the `--enable-helm` flag. "
                "Argo CD (Day 39) renders both straight from git, and Day 40 promotes a release by changing `newTag` in an overlay.\n\n"
                "Each tool has a way to go wrong. Helm templates get hard to read once every field becomes a value; a `values.yaml` that repeats the whole Deployment has gone too far. "
                "Kustomize gets confusing when an overlay changes half the base; then the base is wrong, and should change instead.\n\n"
                "My default for a team's own services is Kustomize with one base and small overlays, and Helm for everything installed from outside."
            ),
            "refs": [
                {"title": "Kustomize with kubectl (Kubernetes docs)", "url": "https://kubernetes.io/docs/tasks/manage-kubernetes-objects/kustomization/", "kind": "docs"},
            ],
        },
    ],
    "analogy": (
        "Helm is a recipe card with blanks: \"___ grams of sugar, bake for ___ minutes\". The `values.yaml` file holds the usual amounts, and your values file changes a few. "
        "The kitchen logbook, the release history, lets you bake an earlier version again. "
        "Kustomize is a master drawing with sheets of tracing paper on top: the drawing stays as it is, and each sheet adds the changes for one environment. "
        "Where it breaks: a recipe makes a new cake each time, while `helm upgrade` changes the cake that is already on the table."
    ),
    "diagram": diagram(),
    "diagram_caption": "Two roads to the same place: Helm fills blanks, Kustomize patches a base. The cluster only sees plain YAML.",
    "worked": {
        "title": "One base, two environments with Kustomize",
        "steps": [
            {"say": "The dev overlay runs a newer image, so build it and load it into kind first. The build arg bakes the version into the app's answer.", "code": WORKED_BUILD, "lang": "console"},
            {"say": "Render dev without touching the cluster. The greeting, the tag, the replica count and the Service type all come from the overlay. The second `replicas: 1` belongs to Redis, which the overlay leaves alone.", "code": DEV_RENDER, "lang": "console"},
            {"say": "Render prod. Same base, different answers, plus one extra object: the PodDisruptionBudget that only `overlays/prod` adds.", "code": PROD_RENDER, "lang": "console"},
            {"say": "Why `overlays/` sits next to `k8s/` and not inside it: Kustomize refuses an overlay inside its own base. This is the error you would get (long paths shortened).", "code": CYCLE, "lang": "console"},
            {"say": "Apply both. Each overlay creates its own namespace, so dev, prod and the base app in `hello` run side by side. Both overlays switched the Service to ClusterIP, because NodePort 30080 is already taken by the base app.", "code": APPLY, "lang": "console"},
            {"say": "List every hello-devops Pod in the cluster with its `env` label. The base app has no label; dev has 1 Pod and prod has 4.", "code": PODS, "lang": "console"},
            {"say": "Call dev through a port-forward. The new version and the dev greeting prove that the overlay's changes reached the running app.", "code": CURL, "lang": "console"},
        ],
    },
    "code_files": [
        ("yaml", "chart/hello-devops/Chart.yaml", "helm lint chart/hello-devops"),
        ("yaml", "chart/hello-devops/values.yaml", "helm lint chart/hello-devops"),
        ("text", "chart/hello-devops/templates/_helpers.tpl", "helm template hello chart/hello-devops"),
        ("yaml", "chart/hello-devops/templates/configmap.yaml", "helm template hello chart/hello-devops"),
        ("yaml", "chart/hello-devops/templates/deployment.yaml", "helm template hello chart/hello-devops"),
        ("yaml", "chart/hello-devops/templates/service.yaml", "helm template hello chart/hello-devops"),
        ("yaml", "chart/hello-devops/templates/hpa.yaml", "helm template hello chart/hello-devops --set autoscaling.enabled=true"),
        ("yaml", "chart/hello-devops/templates/httproute.yaml", "helm template hello chart/hello-devops --set httpRoute.enabled=true"),
        ("text", "chart/hello-devops/templates/NOTES.txt", "helm install hello chart/hello-devops -n hello-helm --create-namespace --dry-run=client"),
        ("text", "chart/hello-devops/.helmignore", "helm package chart/hello-devops"),
        ("yaml", "chart/kind-values.yaml", "helm install hello chart/hello-devops -n hello-helm --create-namespace -f chart/kind-values.yaml"),
        ("yaml", "overlays/dev/kustomization.yaml", "kubectl kustomize overlays/dev"),
        ("yaml", "overlays/prod/kustomization.yaml", "kubectl kustomize overlays/prod"),
        ("yaml", "overlays/prod/deployment-patch.yaml", "kubectl kustomize overlays/prod"),
        ("yaml", "overlays/prod/pdb.yaml", "kubectl kustomize overlays/prod"),
    ],
    "commands": [
        {"cmd": "helm lint chart/hello-devops", "what": "Check a chart for mistakes."},
        {"cmd": "helm template hello chart/hello-devops -f chart/kind-values.yaml", "what": "Print the YAML the chart would create, without touching the cluster."},
        {"cmd": "helm install hello chart/hello-devops -n hello-helm --create-namespace -f chart/kind-values.yaml", "what": "Install the chart as a release named hello (revision 1)."},
        {"cmd": "helm upgrade hello chart/hello-devops -n hello-helm -f chart/kind-values.yaml", "what": "Apply changed values or templates as a new revision."},
        {"cmd": "helm upgrade --install hello chart/hello-devops -n hello-helm -f chart/kind-values.yaml --wait --rollback-on-failure", "what": "Install or upgrade, wait for ready Pods, and roll back on failure (the CI form)."},
        {"cmd": "helm history hello -n hello-helm", "what": "List a release's revisions and their status."},
        {"cmd": "helm rollback hello 1 -n hello-helm", "what": "Return to revision 1; Helm records it as a new revision."},
        {"cmd": "helm get values hello -n hello-helm", "what": "Show the values the release uses now."},
        {"cmd": "helm list -A", "what": "List every release in every namespace."},
        {"cmd": "helm uninstall hello -n hello-helm", "what": "Delete the release and every object it created."},
        {"cmd": "helm package chart/hello-devops", "what": "Pack the chart into a versioned .tgz file."},
        {"cmd": "helm push hello-devops-0.2.0.tgz oci://ghcr.io/<your-github-user>/charts", "what": "Upload a packaged chart to an OCI registry."},
        {"cmd": "kubectl kustomize overlays/prod", "what": "Print what an overlay builds, without applying it."},
        {"cmd": "kubectl diff -k overlays/prod", "what": "Show what applying the overlay would change in the cluster."},
        {"cmd": "kubectl apply -k overlays/dev", "what": "Build the dev overlay and apply it."},
    ],
    "mistake": (
        "You run `helm upgrade` with one new `--set`, and settings you gave at install time quietly disappear. "
        "When you pass any values on an upgrade, Helm starts from the chart's defaults plus only those values. "
        "Keep your settings in a values file such as `chart/kind-values.yaml`, pass it with `-f` on every install and upgrade, and check with `helm get values`."
    ),
    "real_world": (
        "At PayLite, everything installed from outside, such as Envoy Gateway and the monitoring stack, comes from Helm charts pinned to exact versions in an OCI registry. "
        "Each in-house service has one Kustomize base and overlays for dev, staging and prod. "
        "Promoting a release means a pull request that changes `newTag` in the next overlay, which Argo CD then applies."
    ),
    "task": {
        "title": "Ship hello-devops as a Helm release",
        "steps": [
            "Write the chart in `chart/hello-devops/` and `chart/kind-values.yaml` from the files above, then run `helm lint chart/hello-devops`.",
            "Render it with `helm template` and your values file. Find the labels from the helper, the image tag and the HTTPRoute in the output.",
            "Install it as release `hello` in namespace `hello-helm` with `chart/kind-values.yaml`, and read the NOTES that Helm prints.",
            "With the Envoy port-forward from Day 36 running, call `curl -H \"Host: helm.local\" localhost:8888` and check the greeting.",
            "Change the greeting in `chart/kind-values.yaml`, run `helm upgrade` with the same file, and watch the Pods roll. Then run `helm history`.",
            "Roll back to revision 1, run `helm history` again, and curl once more.",
            "Upgrade with your values file plus `--set autoscaling.enabled=true`. Use `helm get manifest` to confirm that an HPA appeared and `replicas` left the Deployment.",
            "Package the chart with `helm package`. Optional: log in to GHCR, push it, and install it from `oci://` into a new namespace.",
            "Clean up with `helm uninstall`, and delete the `hello-dev` and `hello-prod` namespaces from the worked example.",
        ],
        "hints": [
            "Release names are unique per namespace, and most helm commands need `-n hello-helm`. `helm list -A` shows every release in the cluster.",
            "Greeting back to the chart default after an upgrade? You passed values without the file. `helm get values hello -n hello-helm` shows what the release really uses.",
            "Curl returns the base app's greeting instead of Helm's? Your request did not match the chart's route. Check the Host header and `kubectl get httproute -A`.",
        ],
        "done_when": "`helm history hello -n hello-helm` shows install, upgrade and a \"Rollback to 1\" revision, and the curl through the Gateway shows the greeting from revision 1.",
    },
    "explain_back": {
        "prompt": "Explain in 3 to 4 sentences how Helm and Kustomize each turn one set of files into a dev and a prod version of an app. Say which you would use for hello-devops and why.",
        "answer": (
            "Helm keeps templates with blanks and fills them from a values file. Dev and prod are then two values files for the same chart, and each install is a release with revisions. "
            "Kustomize keeps plain YAML as a base and puts each environment's changes in an overlay folder, as patches, image tags and replica counts. "
            "Both produce ordinary YAML that the cluster applies. "
            "For hello-devops I would use Kustomize, because the differences are small and the files stay readable, and keep Helm for the third-party tools I install."
        ),
    },
    "recap": [
        "Helm templates with values; Kustomize patches a plain base. Both render ordinary YAML.",
        "A chart is Chart.yaml, values.yaml, templates, helpers and NOTES; render with `helm template` before installing.",
        "Every install, upgrade and rollback is a revision; rollback adds a new one instead of rewriting history.",
        "Passing values on upgrade drops earlier ones, so pass the same values file every time.",
        "Helm 4: server-side apply for new releases, `--rollback-on-failure` and `--force-replace`; Helm 3 security fixes end February 10, 2027.",
        "Overlays point at a base with `resources`, then set namespace, images, replicas, labels and patches; never put them inside the base.",
    ],
    "check": [
        {
            "q": "A chart's `values.yaml` says `replicaCount: 2`. You installed with `-f prod.yaml`, which sets 5. Now you run `helm upgrade web ./chart --set image.tag=1.2.0` only. How many replicas run afterwards?",
            "options": [
                "5, because Helm keeps install values forever",
                "6, because Helm adds the counts together",
                "1, because `--set` resets every value to 1",
                "2, because the upgrade starts from the chart defaults",
            ],
            "answer": 3,
            "why": "Passing any values on upgrade means chart defaults plus only the new values, so prod.yaml's 5 is dropped and the default 2 applies.",
        },
        {
            "q": "Prod needs a bigger memory limit on the base Deployment's `web` container, and nothing else changes. What do you add to the prod overlay?",
            "options": [
                "A strategic merge patch with only that container's resources",
                "A full copy of deployment.yaml with the new limit",
                "An `images` entry with a new tag",
                "A `configMapGenerator` with a MEMORY key",
            ],
            "answer": 0,
            "why": "A strategic merge patch names the Deployment and container and lists only the changed fields; Kustomize merges it into the base.",
        },
        {
            "q": "An old CI script runs `helm upgrade --install api ./chart --atomic`. What happens with Helm 4?",
            "options": [
                "It fails, because Helm 4 removed the flag",
                "It ignores the flag and never rolls back",
                "It works, with a warning to use the new name",
                "It switches the release to client-side apply",
            ],
            "answer": 2,
            "why": "Helm 4 renamed `--atomic` to `--rollback-on-failure` and keeps the old name working with a deprecation warning.",
        },
    ],
    "interview": [
        {
            "q": "When would you choose Helm, and when Kustomize?",
            "a": (
                "Helm is a package manager with templates and release history, and it is the standard way to install and upgrade third-party software. "
                "Kustomize keeps plain YAML and adds per-environment overlays, which suits a team's own services with small differences. "
                "Helm's templates are powerful but get hard to read, while Kustomize gets messy if overlays rewrite most of the base. "
                "Many teams use Helm for platform tools and Kustomize for their own apps, and GitOps tools such as Argo CD render both."
            ),
        },
        {
            "q": "What is a Helm release, and how does a rollback work?",
            "a": (
                "A release is one installed copy of a chart, with a name, a namespace and a numbered history of revisions stored as Secrets. "
                "Each install, upgrade or rollback adds a revision. It holds the rendered manifest and the values used. "
                "`helm rollback` re-applies an earlier revision's manifest and records it as a new revision, so history is never lost. "
                "In Helm 4 it also keeps the apply method the release started with, client-side or server-side."
            ),
        },
        {
            "q": "How do you manage different settings for dev, staging and prod?",
            "a": (
                "I keep one source of truth for the app and express each environment as a small difference. "
                "With Helm that is one values file per environment; with Kustomize, one overlay per environment. "
                "Image tags are pinned per environment, so promotion is a reviewed change that copies a tag from one environment to the next. "
                "Secrets stay out of those files and come from a secret manager. "
                "Rendering every environment in CI, with `helm template` or `kubectl kustomize`, catches mistakes before they reach a cluster."
            ),
        },
    ],
    "deeper": {
        "minutes": 12,
        "body": (
            "Helm keeps its memory inside the cluster. Each revision of a release is a Secret of type `helm.sh/release.v1` in the release's namespace, named like `sh.helm.release.v1.hello.v3`. "
            "List them with `kubectl get secrets -n hello-helm -l owner=helm`. "
            "Each one holds the chart, the values and the rendered manifest, compressed and encoded. "
            "Helm keeps the last 10 revisions per release by default; `--history-max` changes that.\n\n"
            "This design has a consequence: Helm only knows what it applied, not what is in the cluster now. "
            "If someone runs `kubectl edit` on a Deployment that Helm manages, Helm does not notice until the next upgrade. "
            "What happens then depends on the apply method:\n"
            "- With server-side apply, the default for new Helm 4 releases, the API server tracks which manager owns each field. A field changed by hand now has a different owner, and Helm reports a conflict instead of silently overwriting it. `--force-conflicts` takes the field back.\n"
            "- With client-side apply, Helm compares the old manifest, the new one and the live object, and patches the difference. Hand edits to fields the chart does not set survive; edits to fields it does set are overwritten.\n\n"
            "Either way, hand edits make the next upgrade harder to predict. Argo CD (Day 39) fixes this by watching for drift all the time and showing it.\n\n"
            "Two Helm features you will meet in third-party charts:\n"
            "- Hooks: templates with a `helm.sh/hook` annotation run at set points, such as a database migration Job before an upgrade.\n"
            "- Tests: Pods with the `test` hook that `helm test <release>` runs after an install, to check the app answers.\n\n"
            "On the Kustomize side, look at `configMapGenerator`. It builds a ConfigMap from literals or files and adds a hash of the content to its name, such as `hello-config-h622489h5k`. "
            "Kustomize also updates every reference to that name. Change a value, the name changes, the Pod template changes, and the Deployment rolls out by itself. "
            "It is the Kustomize version of the chart's `checksum/config` trick."
        ),
    },
    "sources": [
        {"title": "Helm 4 overview", "url": "https://helm.sh/docs/overview"},
        {"title": "Using Helm", "url": "https://helm.sh/docs/intro/using_helm/"},
        {"title": "Declarative management of Kubernetes objects using Kustomize", "url": "https://kubernetes.io/docs/tasks/manage-kubernetes-objects/kustomization/"},
        {"title": "Use OCI-based registries (Helm docs)", "url": "https://helm.sh/docs/topics/registries/"},
    ],
}
