from svg import svg, box, arrow, note
from labfiles import lab

ARGO_STABLE = "https://argo-cd.readthedocs.io/en/stable"

diagram = svg(200, "GitOps flow: you push to git, Argo CD pulls from git, applies to the cluster and keeps watching the live state", [
    box(16, 60, 90, 48, "bx", "You"),
    box(146, 60, 110, 48, "bxt", "Git repo"),
    box(296, 60, 110, 48, "bxo", "Argo CD"),
    box(446, 60, 98, 48, "bxp", "Cluster"),
    arrow(108, 84, 142, 84), note(126, 50, "push"),
    arrow(258, 84, 292, 84), note(276, 50, "pull"),
    arrow(408, 84, 442, 84), note(426, 50, "apply"),
    note(201, 128, "desired state"),
    arrow(495, 110, 495, 150, dashed=True, head=False),
    arrow(495, 150, 351, 150, dashed=True, head=False),
    arrow(351, 150, 351, 113, dashed=True),
    note(423, 170, "watch live state"),
])

lesson = {
    "id": "d20",
    "title": "GitOps with Argo CD",
    "minutes": 40,
    "goal": "By the end you can install Argo CD on your kind cluster, let it deploy hello-devops from your GitHub repo, and fix drift and roll back using only git.",
    "guess": {
        "q": "With GitOps, how does a new version of your app usually reach the cluster?",
        "options": [
            "Your CI pipeline runs kubectl apply with an admin key",
            "A tool inside the cluster pulls the desired state from git",
            "Someone logs in to a server and runs a deploy script",
            "The container registry pushes the new image into the cluster",
        ],
        "answer": 1,
        "why": "In GitOps an agent such as Argo CD runs inside the cluster and pulls from git. CI only changes git, so it never needs keys to the cluster.",
    },
    "terms": [
        {"term": "GitOps", "plain": "Running systems from git: the desired state lives in a repo, and an agent keeps the system equal to it."},
        {"term": "Desired state", "plain": "What you want running, written down as files, here the YAML in your repo."},
        {"term": "Drift", "plain": "A difference between what git says and what really runs, often caused by a change made by hand."},
        {"term": "Argo CD Application", "plain": "A Kubernetes object that tells Argo CD which repo folder to deploy to which cluster and namespace."},
        {"term": "Sync", "plain": "Argo CD applying the files from git to the cluster, so the two match."},
        {"term": "Self-heal", "plain": "An Argo CD setting that undoes changes made in the cluster but not in git."},
        {"term": "Prune", "plain": "An Argo CD setting that deletes objects from the cluster after you delete them from git."},
    ],
    "sections": [
        {
            "h": "What GitOps means",
            "body": (
                "So far you deployed with `kubectl apply` from your laptop. It works, but nothing stops the cluster from changing later. "
                "Someone edits a Deployment by hand, and now git and the cluster disagree. Nobody knows which one is right.\n\n"
                "**GitOps** fixes this by making git the one place where changes happen. "
                "The [OpenGitOps project](https://opengitops.dev/), a CNCF project, defines four principles. The desired state must be:\n"
                "- Declarative: you describe what you want, not the steps to get there.\n"
                "- Versioned and immutable: it lives in git, with a full history that nobody rewrites.\n"
                "- Pulled automatically: software agents fetch it from git by themselves.\n"
                "- Continuously reconciled: agents keep comparing the real system with git and fix differences.\n\n"
                "You already know two of these from Kubernetes (Day 16). YAML is declarative, and controllers reconcile. "
                "GitOps adds git as the source of truth and an agent that watches it."
            ),
            "refs": [
                {"title": "OpenGitOps: the GitOps principles", "url": "https://opengitops.dev/", "kind": "read"},
                {"title": "OpenGitOps principles and glossary on GitHub", "url": "https://github.com/open-gitops/documents", "kind": "docs"},
            ],
        },
        {
            "h": "Push deploys and pull deploys",
            "body": (
                "There are two ways a new version can reach a cluster.\n\n"
                "In a push deploy, your CI pipeline runs `kubectl apply` or `helm upgrade` against the cluster. "
                "To do that, CI needs a key with write access to the cluster. Every workflow that can read that secret can change production.\n\n"
                "In a pull deploy, an agent runs inside the cluster. It reads git and applies what it finds. "
                "CI only builds the image and changes a file in git. The pull model gives you:\n"
                "- No cluster keys in CI. The agent already lives in the cluster.\n"
                "- An audit log with no extra work. `git log` shows who changed what, and when.\n"
                "- Easy rollback. `git revert` puts back the old desired state.\n"
                "- Drift repair. The agent notices hand edits and can undo them.\n\n"
                "The cost is one more system to run and learn. For a laptop cluster, that cost is small."
            ),
            "refs": [
                {"title": "Argo CD: automated sync policy", "url": f"{ARGO_STABLE}/user-guide/auto_sync/", "kind": "docs"},
            ],
        },
        {
            "h": "How Argo CD works",
            "body": (
                "Argo CD is a GitOps agent for Kubernetes. It runs as a few pods in its own namespace, `argocd`. Three parts matter:\n"
                "- The API server serves the web UI and the `argocd` command line tool.\n"
                "- The repository server clones your repo and turns a folder into plain YAML. It understands Kustomize and Helm too.\n"
                "- The application controller compares the cluster with that YAML and applies the difference.\n\n"
                "You tell Argo CD what to deploy with an Application. It is a custom resource: a new object type that a tool adds to Kubernetes. "
                "So you write it as YAML and apply it like any other object. It names a source (repo, branch, folder) and a destination (cluster, namespace).\n\n"
                "By default, Argo CD checks git every two to three minutes. A git webhook can make it react within seconds. "
                "Each app has two statuses. Sync status says whether the cluster matches git: Synced or OutOfSync. "
                "Health says whether the objects work, for example Healthy or Progressing."
            ),
            "refs": [
                {"title": "Argo CD: getting started", "url": f"{ARGO_STABLE}/getting_started/", "kind": "docs"},
                {"title": "Argo CD: architecture overview", "url": f"{ARGO_STABLE}/operator-manual/architecture/", "kind": "docs"},
            ],
        },
        {
            "h": "Sync, self-heal and prune",
            "body": (
                "By default Argo CD only shows differences, and you press Sync to apply them. "
                "With automated sync, it applies new commits by itself. Two more switches decide how strict it is:\n"
                "- `selfHeal: true` undoes changes made in the cluster but not in git. Someone runs `kubectl edit`, and seconds later git's version is back.\n"
                "- `prune: true` deletes objects you removed from git. Without it, they stay in the cluster as leftovers.\n\n"
                "Both are off by default for safety. The lab's `argocd/application.yaml` turns both on.\n\n"
                "This trips most people up: other controllers change objects too. The autoscaler from Day 18 raises the number of replicas under load. "
                "Argo CD sees a difference from git and, with self-heal on, sets it back. The two then fight. "
                "The fix is `ignoreDifferences` for `/spec/replicas`, which the lab file includes.\n\n"
                "Rollback works through git as well. Revert the bad commit and push, and Argo CD deploys the old state. "
                "Argo CD's own rollback command refuses to run while automated sync is on, because git must stay the source of truth."
            ),
            "refs": [
                {"title": "Argo CD: automated sync, prune and self-heal", "url": f"{ARGO_STABLE}/user-guide/auto_sync/", "kind": "docs"},
                {"title": "Argo CD: ignoring differences", "url": f"{ARGO_STABLE}/user-guide/diffing/", "kind": "docs"},
            ],
        },
        {
            "h": "Getting a new image version into git",
            "body": (
                "Argo CD only deploys what git says. So something must write the new image tag into a file and commit it. The usual flow:\n"
                "1. You push code. CI tests it and builds an image, such as `ghcr.io/you/hello-devops:1.2.0`.\n"
                "2. A step writes the new tag into git. Your `k8s/` folder uses Kustomize, so `kustomize edit set image` adds it to `kustomization.yaml`.\n"
                "3. CI or a person commits that change, often as a pull request.\n"
                "4. Argo CD sees the new commit and rolls out the new image.\n\n"
                "Some teams skip step 2 and use [Argo CD Image Updater](https://github.com/argoproj-labs/argocd-image-updater). "
                "It watches the registry and writes new tags back to git for you. It works with Kustomize and Helm apps. "
                "Its README says it is not yet recommended for critical production use.\n\n"
                "One catch for the lab: the cluster must be able to pull the image. A new package on GitHub is private by default. "
                "For this demo app, make the package public in its settings."
            ),
            "refs": [
                {"title": "Argo CD: Kustomize apps", "url": f"{ARGO_STABLE}/user-guide/kustomize/", "kind": "docs"},
                {"title": "Argo CD Image Updater", "url": "https://github.com/argoproj-labs/argocd-image-updater", "kind": "docs"},
            ],
        },
        {
            "h": "Flux, ApplicationSets and app of apps",
            "body": (
                "Argo CD is one of two big GitOps tools. The other is [Flux](https://github.com/fluxcd/flux2), also a graduated CNCF project. "
                "Flux is a set of small controllers that you drive with YAML and the `flux` command, while Argo CD puts a web UI at the center. "
                "Both pull from git and reconcile, so today's ideas carry over.\n\n"
                "Two Argo CD patterns appear once you have many apps. An ApplicationSet is a template that creates many Applications, "
                "for example one per cluster or one per folder in a repo. App of apps is one Application whose folder holds more Application files, "
                "so a single sync can set up a whole cluster. You do not need either for hello-devops."
            ),
            "refs": [
                {"title": "Flux on GitHub", "url": "https://github.com/fluxcd/flux2", "kind": "docs"},
                {"title": "Argo CD: cluster bootstrapping and ApplicationSets", "url": f"{ARGO_STABLE}/operator-manual/cluster-bootstrapping/", "kind": "docs"},
            ],
        },
    ],
    "analogy": (
        "Think of a shop with a floor plan pinned up in the back office. The plan says which shelf holds which product. "
        "Every few minutes a staff member walks the aisles and puts anything misplaced back where the plan says. "
        "To change the shop, you change the plan, not the shelves. "
        "Where it breaks: a real person would ask why a customer moved something, while Argo CD just puts it back, even when the plan itself is wrong."
    ),
    "diagram": diagram,
    "diagram_caption": "You change git. Argo CD pulls it, applies it, and keeps comparing.",
    "worked": {
        "title": "Watch Argo CD undo a hand edit",
        "steps": [
            {
                "say": "Suppose Argo CD already runs on your kind cluster and deploys hello-devops with self-heal on (the task below sets this up). An Application is a normal Kubernetes object, so kubectl can show its two statuses.",
                "code": "$ kubectl -n argocd get applications\nNAME           SYNC STATUS   HEALTH STATUS\nhello-devops   Synced        Healthy",
                "lang": "console",
            },
            {
                "say": "Now play the colleague who fixes things by hand. Change the greeting in the live ConfigMap and skip git. (A `kubectl scale` would not work as a demo here: the lab tells Argo CD to ignore replicas.)",
                "code": "$ kubectl -n hello patch configmap hello-config --type merge \\\n    -p '{\"data\":{\"GREETING\":\"Edited by hand\"}}'\nconfigmap/hello-config patched",
                "lang": "console",
            },
            {
                "say": "The application controller watches every object it manages, so it sees the change at once. The app turns OutOfSync. Self-heal waits a few seconds (5 by default) and then syncs git's version back.",
            },
            {
                "say": "Check the value. Git's text is back, and you did nothing.",
                "code": "$ kubectl -n hello get configmap hello-config -o jsonpath='{.data.GREETING}'\nHello from Kubernetes!",
                "lang": "console",
            },
            {
                "say": "The lasting way to change the greeting is a commit. Edit `k8s/configmap.yaml`, then commit and push. Argo CD applies it at its next check, or at once with `argocd app sync`. Pods read environment variables only when they start, so restart the Deployment to see the new greeting.",
                "code": "$ git add k8s/configmap.yaml\n$ git commit -m \"Change the greeting\"\n$ git push\n$ argocd app sync hello-devops\n$ kubectl -n hello rollout restart deployment hello-devops",
                "lang": "console",
            },
        ],
    },
    "code": [
        {
            "lang": "yaml",
            "title": "argocd/application.yaml",
            "src": lab("argocd/application.yaml"),
            "run": "kubectl apply -n argocd -f argocd/application.yaml",
        },
    ],
    "commands": [
        {"cmd": "kubectl create namespace argocd", "what": "Create the namespace where Argo CD runs."},
        {"cmd": "kubectl apply -n argocd --server-side --force-conflicts -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml",
         "what": "Install Argo CD from its official manifest. Server-side apply is needed because some of its definitions are very large."},
        {"cmd": "kubectl -n argocd get pods", "what": "Check that all Argo CD pods are Running."},
        {"cmd": "kubectl -n argocd port-forward svc/argocd-server 8443:443", "what": "Open the Argo CD UI at https://localhost:8443 and accept the self-signed certificate warning."},
        {"cmd": "brew install argocd", "what": "Install the argocd command line tool on your Mac."},
        {"cmd": "argocd admin initial-password -n argocd", "what": "Print the first password of the admin user."},
        {"cmd": "argocd login localhost:8443 --username admin --insecure", "what": "Log the CLI in through the port-forward. --insecure accepts the self-signed certificate."},
        {"cmd": "kubectl -n argocd get applications", "what": "List Applications with their sync and health status."},
        {"cmd": "argocd app get hello-devops", "what": "Show one app: repo, path, status and every object it manages."},
        {"cmd": "argocd app sync hello-devops", "what": "Sync now instead of waiting for the next check of git."},
        {"cmd": "kustomize edit set image hello-devops=ghcr.io/<your-github-user>/hello-devops:1.2.0",
         "what": "Run inside k8s/ (install with brew install kustomize). Writes a new image name and tag into kustomization.yaml."},
        {"cmd": "git revert HEAD", "what": "Make a new commit that undoes the last one. Push it, and Argo CD rolls back."},
    ],
    "mistake": (
        "Fixing things in the cluster by hand and expecting the fix to stay. With self-heal on, Argo CD undoes `kubectl edit` and `kubectl delete` within seconds. "
        "Make every change in git and let Argo CD apply it. In a real emergency, turn off automated sync for that app first, and write down what you changed."
    ),
    "real_world": (
        "A payments team might keep one config repo with a folder per environment: dev, staging and prod. "
        "Merging a pull request into the prod folder is the deploy, and the review is the approval. "
        "When something breaks at night, the on-call engineer reverts the commit, and Argo CD rolls back with a record of who did what."
    ),
    "task": {
        "title": "Put hello-devops under GitOps",
        "steps": [
            "Start your kind cluster from Day 16 if it is not running, and make sure your latest `k8s/` folder is pushed to GitHub.",
            "Install Argo CD with the first two commands in the Commands list. Wait until every pod in namespace `argocd` is Running.",
            "Open the UI with a port-forward and log in as `admin` with the initial password.",
            "Add `argocd/application.yaml` to your repo with your GitHub user name in `repoURL`. Commit, push, and apply it.",
            "Watch the app in the UI until it shows Synced and Healthy. Click it and look at the tree of objects.",
            "Remove `hpa.yaml` from the `resources` list in `k8s/kustomization.yaml`, then commit and push. Watch prune delete the HorizontalPodAutoscaler.",
            "Undo that with `git revert HEAD` and push. Watch the HorizontalPodAutoscaler come back.",
        ],
        "hints": [
            "If the app shows a repository error, Argo CD cannot read your repo. A public repo needs no password; for a private one, run `argocd repo add` with a read-only token.",
            "Argo CD checks git every few minutes. Press Refresh in the UI, or run `argocd app sync hello-devops`, to skip the wait.",
        ],
        "done_when": "After your revert, `kubectl -n hello get hpa` lists hello-devops again, and Argo CD shows the app as Synced and Healthy.",
    },
    "explain_back": {
        "prompt": "Explain GitOps to a teammate in 3 to 4 sentences. Mention who applies changes, what self-heal does, and how you roll back.",
        "answer": (
            "With GitOps, git holds the desired state of the cluster, and an agent inside the cluster applies it. "
            "Nobody runs kubectl apply by hand; a change is a commit, usually through a pull request. "
            "Argo CD keeps comparing the cluster with git, and self-heal undoes changes that skipped git. "
            "To roll back, you revert the commit, and Argo CD deploys the old state."
        ),
    },
    "recap": [
        "GitOps: git holds the desired state, and an agent in the cluster pulls it and keeps the cluster equal to it.",
        "Pull deploys keep cluster keys out of CI and give you an audit log and rollback through git.",
        "An Argo CD Application links a repo folder to a cluster and a namespace.",
        "Automated sync applies new commits, self-heal undoes hand edits, and prune deletes what you removed from git.",
        "Tell Argo CD to ignore fields that other controllers own, such as replicas set by an autoscaler.",
        "A new version ships when CI changes the image tag in git, for example with kustomize edit set image.",
    ],
    "check": [
        {
            "q": "A teammate scales hello-devops to 10 pods with kubectl. Your Application has selfHeal on and ignores /spec/replicas. What does Argo CD do?",
            "options": [
                "It sets the count back to 3 within seconds",
                "It leaves it alone; only the autoscaler may change it",
                "It deletes the Deployment and creates it again",
                "It marks the app Degraded and stops syncing",
            ],
            "answer": 1,
            "why": "ignoreDifferences tells Argo CD not to compare /spec/replicas, so the change is not drift to it. The autoscaler still applies its own limit of 6.",
        },
        {
            "q": "You delete redis.yaml from git and push. Automated sync is on, but prune is off. What happens to Redis in the cluster?",
            "options": [
                "It is deleted at the next sync",
                "Argo CD puts redis.yaml back into your repo",
                "It keeps running, and Argo CD flags it as needing a prune",
                "The sync fails and nothing else deploys",
            ],
            "answer": 2,
            "why": "Without prune, automated sync never deletes. The object stays, marked as no longer in git, until you prune it.",
        },
        {
            "q": "Your CI pipeline holds a cluster admin key and runs kubectl apply after every build. What is the main GitOps improvement?",
            "options": [
                "CI only updates the tag in git, and Argo CD applies it",
                "CI runs kubectl apply twice to be sure it worked",
                "Developers apply from their laptops instead of CI",
                "The cluster pulls images from Docker Hub, not GHCR",
            ],
            "answer": 0,
            "why": "Moving the apply into the cluster removes the powerful key from CI and makes git the record of every deploy.",
        },
    ],
    "interview": [
        {
            "q": "What is GitOps, and how is it different from a CI pipeline that runs kubectl apply?",
            "a": (
                "GitOps keeps the desired state of a system in git and uses an agent, such as Argo CD or Flux, to pull it and keep the system equal to it. "
                "A push pipeline runs kubectl apply from outside, so it needs cluster credentials and only acts when it runs. "
                "With GitOps the agent runs inside the cluster, keeps reconciling, and can undo drift. "
                "Every change is a commit, so you get review, history and rollback with normal git tools."
            ),
        },
        {
            "q": "How do you roll back a bad deploy in an Argo CD setup?",
            "a": (
                "I revert the commit that introduced the change and push, so git again describes the last good state. "
                "Argo CD syncs and the cluster follows. "
                "Argo CD has its own rollback command, but it cannot run while automated sync is on, and it would leave the cluster different from git. "
                "Reverting in git keeps one source of truth and leaves an audit trail."
            ),
        },
    ],
    "deeper": {
        "minutes": 12,
        "body": (
            "When CI writes to git, two design questions come up: which repo, and who writes the tag.\n\n"
            "With one repo, code and YAML live together, like hello-devops. It is simple, but every tag bump becomes a commit in the code history. "
            "CI must also avoid triggering itself: a commit that only changes `k8s/` should not build a new image. A paths filter on the workflow (Day 11) handles that.\n\n"
            "With two repos, the app repo holds code and a config repo holds the YAML for every environment. "
            "CI in the app repo builds the image, then opens a pull request in the config repo. Teams like this because:\n"
            "- Permissions are clear: many people can change code, fewer can change production.\n"
            "- The config repo history reads like a deploy log.\n"
            "- One config repo can describe many apps and clusters.\n\n"
            "Who writes the tag? The options, from manual to automatic:\n"
            "1. A person edits the tag in a pull request. Slow, but very clear.\n"
            "2. CI runs `kustomize edit set image`, or edits a Helm values file, and opens a pull request. This needs a token that can write to the config repo, so keep that token narrow.\n"
            "3. Argo CD Image Updater watches the registry and writes the tag for you. It can follow rules such as \"the newest 1.x version\".\n\n"
            "Promotion between environments works the same way. To move version 1.2.0 from staging to prod, you copy the tag from one folder to the other in a pull request. "
            "The image is built once and promoted by changing text. That is the \"build once, deploy many\" idea from Day 9.\n\n"
            "One more tip: pin by digest when it matters. A tag such as `1.2.0` can be pushed again by mistake. "
            "A digest such as `@sha256:...` always means the same bytes. The `images` field in `kustomization.yaml` accepts a `digest` value for this."
        ),
    },
    "sources": [
        {"title": "Argo CD: getting started", "url": f"{ARGO_STABLE}/getting_started/"},
        {"title": "Argo CD: automated sync policy", "url": f"{ARGO_STABLE}/user-guide/auto_sync/"},
        {"title": "OpenGitOps principles", "url": "https://opengitops.dev/"},
    ],
}
