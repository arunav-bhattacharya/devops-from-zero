#!/usr/bin/env python3
"""Build content/p8.json (Part 8: GitOps with Argo CD), second edition.

Run: python3 brief/scratch/v2/p8/build_p8.py
Lab files are read from labs/hello-devops so the lesson code always matches the lab.
"""
import json
import pathlib
import textwrap

ROOT = pathlib.Path(__file__).resolve().parents[4]
LAB = ROOT / "labs/hello-devops"
OUT = ROOT / "content/p8.json"


def t(s):
    """Dedent a triple-quoted block and trim it."""
    return textwrap.dedent(s).strip("\n")


def lab(path):
    return (LAB / path).read_text().rstrip("\n")


def ref(title, url, kind):
    return {"title": title, "url": url, "kind": kind}


# ---------------------------------------------------------------- links
D = "https://argo-cd.readthedocs.io/en/stable/"
L = {
    "getting_started": D + "getting_started/",
    "cli_install": D + "cli_installation/",
    "core": D + "core_concepts/",
    "arch": D + "operator-manual/architecture/",
    "tracking": D + "user-guide/resource_tracking/",
    "auto_sync": D + "user-guide/auto_sync/",
    "diffing": D + "user-guide/diffing/",
    "best": D + "user-guide/best_practices/",
    "health": D + "operator-manual/health/",
    "faq": D + "faq/",
    "rollback_cmd": D + "user-guide/commands/argocd_app_rollback/",
    "appset": D + "operator-manual/applicationset/",
    "list_gen": D + "operator-manual/applicationset/Generators-List/",
    "bootstrap": D + "operator-manual/cluster-bootstrapping/",
    "hydrator": D + "user-guide/source-hydrator/",
    "waves": D + "user-guide/sync-waves/",
    "secrets": D + "operator-manual/secret-management/",
    "projects": D + "user-guide/projects/",
    "rbac": D + "operator-manual/rbac/",
    "principles": "https://github.com/open-gitops/documents/blob/main/PRINCIPLES.md",
    "opengitops": "https://opengitops.dev/",
    "k8s_controller": "https://kubernetes.io/docs/concepts/architecture/controller/",
    "git_revert": "https://git-scm.com/docs/git-revert",
    "gh_revert_pr": "https://docs.github.com/en/pull-requests/how-tos/merge-and-close-pull-requests/reverting-a-pull-request",
    "gh_token": "https://docs.github.com/en/actions/concepts/security/github_token",
    "gh_actions_settings": "https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/enabling-features-for-your-repository/managing-github-actions-settings-for-a-repository",
    "gh_manual_run": "https://docs.github.com/en/actions/how-tos/manage-workflow-runs/manually-run-a-workflow",
    "image_updater": "https://github.com/argoproj-labs/argocd-image-updater",
    "image_updater_docs": "https://argocd-image-updater.readthedocs.io/en/stable/",
    "sealed": "https://github.com/bitnami-labs/sealed-secrets",
    "eso": "https://github.com/external-secrets/external-secrets",
    "sops": "https://github.com/getsops/sops",
    "flux": "https://github.com/fluxcd/flux2",
    "flux_ui": "https://fluxoperator.dev/web-ui/",
    "kargo": "https://github.com/akuity/kargo",
    "promoter": "https://github.com/argoproj-labs/gitops-promoter",
    "codefresh": "https://learning.codefresh.io",
    "kustomize_k8s": "https://kubernetes.io/docs/tasks/manage-kubernetes-objects/kustomization/",
    # Videos (all came back in YouTube search results in this task)
    "v_nana": "https://www.youtube.com/watch?v=MeU5_k9ssrs",
    "v_farcic_principles": "https://www.youtube.com/watch?v=797ptFfuL5g",
    "v_farcic_intro": "https://www.youtube.com/watch?v=iQB5j_2rSBA",
    "v_akuity_aoa": "https://www.youtube.com/watch?v=2pvGL0zqf9o",
    "v_kargo": "https://www.youtube.com/watch?v=og5JbumZpbs",
    "v_tgik_sealed": "https://www.youtube.com/watch?v=x-cDk8DIvwE",
}

# ======================================================================
# Day 39
# ======================================================================
D39_SECTIONS = [
    {
        "h": "Why applying from a laptop stops working",
        "body": t("""
            Since Day 30 you have deployed with `kubectl apply -k k8s` from your laptop. For one person and one cluster, that is fine. Add a few colleagues and it breaks in quiet ways:
            - Someone fixes a Deployment by hand at night and never tells git.
            - Two people apply from two branches, and the last one wins.
            - Nobody can say which commit is running right now.
            - Every laptop or pipeline that deploys holds a key that can change the cluster.

            A difference between git and what really runs is called **drift**. You met it with Terraform on Day 27. A hand change made the real world differ from the code, and Terraform noticed only when you ran `plan` again.

            **GitOps** closes that gap from the other side. Git becomes the only place where changes happen. A program inside the cluster keeps the cluster equal to git, all the time, whether or not anyone deploys. The [OpenGitOps project](https://opengitops.dev/), part of the CNCF, sums it up in four principles. The desired state must be:
            - Declarative: you describe what you want, not the steps to get there.
            - Versioned and immutable: it is stored with its full history, and old versions never change.
            - Pulled automatically: software agents fetch it by themselves.
            - Continuously reconciled: agents keep comparing the real system with it and fix differences.

            Two of these should feel familiar. Kubernetes YAML is declarative, and on Day 30 you watched controllers reconcile: they compare what you asked for with what exists, then close the gap. GitOps runs the same kind of loop one level up, with git as the thing you asked for.
        """),
        "refs": [
            ref("OpenGitOps principles (GitHub)", L["principles"], "read"),
            ref("The objectives and the principles behind GitOps (Viktor Farcic)", L["v_farcic_principles"], "watch"),
            ref("Kubernetes docs: controllers and the control loop", L["k8s_controller"], "docs"),
        ],
    },
    {
        "h": "Push deploys and pull deploys",
        "body": t("""
            A new version can reach a cluster in two ways.

            In a push deploy, something outside the cluster sends the change in. Your CI pipeline ends with `kubectl apply` or `helm upgrade`. So CI holds a key that can write to the cluster, and any workflow that can read that secret can change production. The deploy also happens only while the pipeline runs. If someone edits the cluster an hour later, nothing notices.

            In a pull deploy, an agent runs inside the cluster. It reads git and applies what it finds. CI builds the image and changes a file in git, and that is all CI does. The pull model gives you:
            - No cluster keys in CI, because the agent already lives in the cluster.
            - A deploy log at no extra cost: `git log` shows who changed what, and when.
            - Review before deploy, because every change can be a pull request.
            - Rollback with `git revert`.
            - Drift detection all day, even when nobody is deploying.

            The price is one more system to install, upgrade and learn. On your laptop that means seven extra Pods. For any cluster that more than one person touches, I think the pull model is worth that price.

            One thing does not change: CI still tests the code and builds the image, exactly as in Part 4. GitOps replaces only the last step, the one that touches the cluster.
        """),
        "refs": [
            ref("Argo CD docs: automated sync (why pipelines no longer need cluster access)", L["auto_sync"], "docs"),
            ref("OpenGitOps", L["opengitops"], "read"),
        ],
    },
    {
        "h": "What Argo CD is made of",
        "body": t("""
            Argo CD is a GitOps agent for Kubernetes, part of the Argo project in the CNCF. It runs as a set of Pods in its own namespace, `argocd`. After the install you will see seven:
            - `argocd-server`: the API server behind the web UI and the `argocd` command line tool.
            - `argocd-repo-server`: clones your repo and turns a folder into plain YAML. It understands Kustomize and Helm (Argo CD 3.5 ships with Helm 4).
            - `argocd-application-controller`: compares the cluster with that YAML and applies the difference. This is the reconcile loop.
            - `argocd-applicationset-controller`: makes many Applications from one template (Day 40).
            - `argocd-redis`: a cache for rendered YAML and app state.
            - `argocd-dex-server`: connects Argo CD to single sign-on, such as GitHub or Google accounts.
            - `argocd-notifications-controller`: sends messages, for example to Slack when a sync fails.

            You tell Argo CD what to deploy with an Application. It is a custom resource: a new object type that a tool adds to Kubernetes. You write it as YAML and apply it like a Deployment. It has three main parts:
            - A source: the repo URL, the branch (`targetRevision`) and the folder (`path`).
            - A destination: which cluster and which namespace.
            - A project: rules about what this app may touch. Everything starts in the project called `default`.

            How does Argo CD remember which objects belong to which app? Since version 3.0 it writes an annotation on every object it applies, `argocd.argoproj.io/tracking-id`. Older versions used a label for this, and many blog posts still say so. The worked example below shows the annotation on a real object.
        """),
        "refs": [
            ref("Argo CD docs: architecture overview", L["arch"], "docs"),
            ref("Argo CD docs: core concepts", L["core"], "docs"),
            ref("Argo CD docs: resource tracking", L["tracking"], "docs"),
        ],
    },
    {
        "h": "Installing Argo CD on kind",
        "body": t("""
            The install is one long YAML file from the Argo CD project. The Commands list below has the exact command. Its flags look odd, so here is why.

            `kubectl apply --server-side` lets the API server work out the changes. You need it because one of Argo CD's custom resource definitions, the one for ApplicationSets, is too big for normal apply. Normal (client-side) apply stores a full copy of each object in an annotation, and annotations are limited to 262 KB in total. Server-side apply keeps no such copy. `--force-conflicts` lets the install take over fields that an earlier apply set, which matters when you upgrade.

            This trips up many people who follow older videos. They show a plain `kubectl apply -n argocd -f install.yaml`, and on Argo CD 3.x that fails with an error about annotations that are too long.

            The install URL points at the `stable` branch, which is fine on a laptop. At work you pin a version, with a tag such as `v3.5.6` in the URL instead of `stable`. Then an install today and an install next month give the same result.

            Argo CD's web UI is not reachable from outside the cluster. On a laptop, `kubectl port-forward` is the simplest way in. Use local port 8443, because 8080 may still be busy from your Terraform work in Part 6. The browser warns about the certificate, because the install makes a self-signed one. That is expected here.

            Log in as `admin` with the password from `argocd admin initial-password -n argocd`. Out of the box, `admin` is the only user, and it may do everything. Teams connect single sign-on and give people narrower roles; Day 40 shows the pieces. Install the `argocd` CLI with Homebrew and log it in through the same port-forward.
        """),
        "refs": [
            ref("Argo CD docs: getting started", L["getting_started"], "docs"),
            ref("ArgoCD tutorial for beginners (TechWorld with Nana, older install flags)", L["v_nana"], "watch"),
            ref("Argo CD docs: installing the CLI", L["cli_install"], "docs"),
        ],
    },
    {
        "h": "Two statuses: sync and health",
        "body": t("""
            Every Application shows two separate statuses. Beginners often read them as one.

            Sync status answers one question: does the cluster match git?
            - `Synced`: every object Argo CD manages matches the YAML in git.
            - `OutOfSync`: at least one object differs, is missing, or should be gone.

            Health answers a different question: does it work?
            - `Healthy`: for a Deployment, all replicas are updated and available.
            - `Progressing`: not healthy yet but still moving, such as a rollout in progress.
            - `Degraded`: failed, for example a rollout that ran past its deadline.
            - `Missing`: in git, but not in the cluster yet.
            - `Suspended` and `Unknown` show up less often.

            The two are independent. Push a typo in an image tag, and the app is Synced (the cluster has exactly what git says) but not Healthy (the new Pods cannot pull the image). Make a hand edit to a label, and the app is OutOfSync but still Healthy. The health of a whole app is the worst health of its parts.

            How fast does Argo CD see a new commit? By default it checks git about every three minutes: 120 seconds plus a random delay of up to 60 seconds, so that many apps do not all ask at once. Press Refresh in the UI, or run `argocd app get hello-devops --refresh`, to check now. Teams whose Argo CD has a public address add a git webhook, so a push triggers a check at once. GitHub cannot reach your kind cluster, so here you poll.

            Changes inside the cluster are different. The controller watches the objects it manages, so it sees a `kubectl edit` within seconds.
        """),
        "refs": [
            ref("Argo CD docs: resource health", L["health"], "docs"),
            ref("Argo CD FAQ: how often Argo CD checks git", L["faq"], "docs"),
        ],
    },
    {
        "h": "Automated sync, self-heal and prune",
        "body": t("""
            Out of the box, Argo CD only reports differences. You press Sync, in the UI or with `argocd app sync`, and it applies git. Automated sync applies new commits by itself. Two more switches decide how strict it is:
            - `selfHeal: true` undoes changes made in the cluster but not in git, such as a `kubectl edit`.
            - `prune: true` deletes objects you removed from git. Without it, they stay, and Argo CD only marks them for pruning.

            Both are off by default, a careful choice for a tool that can delete things. With automated sync alone, a hand edit makes the app OutOfSync and stays in place until the next commit. The lab's `argocd/application.yaml` turns both on.

            This part trips most people up: Argo CD is not the only controller that changes your objects. On Day 35 you added a HorizontalPodAutoscaler (HPA), which raises the replica count under load. Argo CD sees 5 replicas where git says 3 and, with self-heal on, sets it back. The HPA raises it again. They fight for as long as the load lasts.

            There are two ways out:
            - Leave `replicas` out of the Deployment in git, so there is nothing to compare. The [Argo CD best practices](https://argo-cd.readthedocs.io/en/stable/user-guide/best_practices/) page suggests this.
            - Tell Argo CD to ignore that one field. The lab does this with `ignoreDifferences` on `/spec/replicas`, plus the sync option `RespectIgnoreDifferences=true` so that a sync leaves the field alone too.

            The lab takes the second way because `k8s/deployment.yaml` keeps `replicas: 3`. That keeps `kubectl apply -k k8s` working on its own, without Argo CD.
        """),
        "refs": [
            ref("Argo CD docs: automated sync, prune and self-heal", L["auto_sync"], "docs"),
            ref("Argo CD docs: diffing customization (ignoreDifferences)", L["diffing"], "docs"),
            ref("Argo CD docs: best practices", L["best"], "docs"),
        ],
    },
    {
        "h": "Rolling back with git revert",
        "body": t("""
            With GitOps, a rollback is a commit. You undo the bad change in git, and Argo CD deploys the state from before:
            1. `git log --oneline -3` shows the recent commits.
            2. `git revert <sha>` makes a new commit that undoes the bad one. History stays intact.
            3. `git push`, then wait for the next check or run `argocd app sync hello-devops`.

            Why not `kubectl rollout undo` from Day 32? It changes the cluster but not git, so with self-heal on, Argo CD puts the bad version straight back. Argo CD has its own `argocd app rollback` command, which redeploys an earlier entry from `argocd app history`. It refuses to run while automated sync is on, for the same reason: git must stay the source of truth.

            In a real emergency, follow this order:
            1. Turn off automated sync for that one app.
            2. Fix the cluster by hand, and write down every change.
            3. Put the same fix into git.
            4. Turn automated sync back on.

            Skip step 3, and the next sync quietly undoes your fix.
        """),
        "refs": [
            ref("Git docs: git revert", L["git_revert"], "docs"),
            ref("Argo CD CLI reference: argocd app rollback", L["rollback_cmd"], "docs"),
        ],
    },
]

D39_DIAGRAM = (
    '<svg viewBox="0 0 560 200" xmlns="http://www.w3.org/2000/svg" role="img" '
    'aria-label="GitOps flow: you push to git, Argo CD pulls from git, applies to the cluster and keeps watching the live state">'
    '<rect class="bx" x="16" y="60" width="90" height="48" rx="10"/>'
    '<text class="t" x="61" y="89" font-size="13" text-anchor="middle">You</text>'
    '<rect class="bxt" x="146" y="60" width="110" height="48" rx="10"/>'
    '<text class="tk" x="201" y="89" font-size="13" text-anchor="middle">Git repo</text>'
    '<rect class="bxo" x="296" y="60" width="110" height="48" rx="10"/>'
    '<text class="tk" x="351" y="89" font-size="13" text-anchor="middle">Argo CD</text>'
    '<rect class="bxp" x="446" y="60" width="98" height="48" rx="10"/>'
    '<text class="tk" x="495" y="89" font-size="13" text-anchor="middle">Cluster</text>'
    '<line class="ln" x1="108" y1="84" x2="142" y2="84" marker-end="url(#ar)"/>'
    '<text class="ts" x="126" y="50" font-size="11" text-anchor="middle">push</text>'
    '<line class="ln" x1="258" y1="84" x2="292" y2="84" marker-end="url(#ar)"/>'
    '<text class="ts" x="276" y="50" font-size="11" text-anchor="middle">pull</text>'
    '<line class="ln" x1="408" y1="84" x2="442" y2="84" marker-end="url(#ar)"/>'
    '<text class="ts" x="426" y="50" font-size="11" text-anchor="middle">apply</text>'
    '<text class="ts" x="201" y="128" font-size="11" text-anchor="middle">desired state</text>'
    '<line class="lnd" x1="495" y1="110" x2="495" y2="150"/>'
    '<line class="lnd" x1="495" y1="150" x2="351" y2="150"/>'
    '<line class="lnd" x1="351" y1="150" x2="351" y2="113" marker-end="url(#ar)"/>'
    '<text class="ts" x="423" y="170" font-size="11" text-anchor="middle">watch live state</text>'
    "</svg>"
)

D39 = {
    "id": "d39",
    "title": "GitOps with Argo CD",
    "minutes": 50,
    "goal": "By the end you can install Argo CD on your kind cluster, let it deploy hello-devops from your GitHub repo, and fix drift and roll back using only git.",
    "guess": {
        "q": "Argo CD deploys your app from git, with its default settings. A teammate then changes the app by hand with kubectl. What happens to that hand edit?",
        "options": [
            "Argo CD undoes it within a few seconds",
            "It stays, and Argo CD shows the app as OutOfSync",
            "kubectl refuses the edit, because git owns the app",
            "Argo CD copies the change back into git",
        ],
        "answer": 1,
        "why": "By default Argo CD only reports drift. Undoing hand edits is a separate setting called self-heal, and it stays off until you turn it on.",
    },
    "terms": [
        {"term": "GitOps", "plain": "Running systems from git: git holds the desired state, and an agent keeps the real system equal to it."},
        {"term": "Desired state", "plain": "What you want running, written down as files, here the YAML in your repo."},
        {"term": "Drift", "plain": "A difference between what git says and what really runs, often caused by a change made by hand."},
        {"term": "Reconcile", "plain": "Compare what runs with what is wanted, then change what runs until the two match."},
        {"term": "Argo CD Application", "plain": "A Kubernetes object that tells Argo CD which repo folder to deploy to which cluster and namespace."},
        {"term": "Sync", "plain": "Argo CD applying the YAML from git to the cluster, so the two match."},
        {"term": "Self-heal", "plain": "An Argo CD setting that undoes changes made in the cluster but not in git."},
        {"term": "Prune", "plain": "An Argo CD setting that deletes objects from the cluster after you delete them from git."},
    ],
    "sections": D39_SECTIONS,
    "analogy": "Picture a shop with a floor plan pinned up in the back office. The plan says which shelf holds which product. Every few minutes a staff member walks the aisles and puts anything misplaced back where the plan says. If you want the shop to change, you change the plan, and the staff move the products. Where it breaks: a real person would ask why a customer moved something, while Argo CD just puts it back, even when the plan itself is wrong.",
    "diagram": D39_DIAGRAM,
    "diagram_caption": "You change git. Argo CD pulls it, applies it, and keeps comparing.",
    "worked": {
        "title": "Watch Argo CD undo a hand edit",
        "steps": [
            {
                "say": "Start from where the task below ends: Argo CD runs on your kind cluster and deploys hello-devops with self-heal on. An Application is an ordinary Kubernetes object, so kubectl lists it with both statuses.",
                "code": "$ kubectl -n argocd get applications\nNAME           SYNC STATUS   HEALTH STATUS\nhello-devops   Synced        Healthy",
                "lang": "console",
            },
            {
                "say": "See how Argo CD marks what it owns. Every object it applied carries a tracking annotation: the app name, then group and kind, then namespace and name. A ConfigMap belongs to the core group, which has an empty name, so nothing stands before the slash.",
                "code": "$ kubectl -n hello get configmap hello-config \\\n    -o jsonpath='{.metadata.annotations.argocd\\.argoproj\\.io/tracking-id}'\nhello-devops:/ConfigMap:hello/hello-config",
                "lang": "console",
            },
            {
                "say": "Now play the colleague who fixes things by hand. Change the greeting in the live ConfigMap and skip git. A `kubectl scale` would make a poor demo, because the lab tells Argo CD to ignore the replica count.",
                "code": "$ kubectl -n hello patch configmap hello-config --type merge \\\n    -p '{\"data\":{\"GREETING\":\"Edited by hand\"}}'\nconfigmap/hello-config patched",
                "lang": "console",
            },
            {
                "say": "The application controller watches every object it manages, so it sees the change at once. If you are quick, you catch the app OutOfSync. It stays Healthy, because the app still runs fine. Self-heal then syncs git's version back after a short pause.",
                "code": "$ kubectl -n argocd get applications\nNAME           SYNC STATUS   HEALTH STATUS\nhello-devops   OutOfSync     Healthy",
                "lang": "console",
            },
            {
                "say": "Wait a few seconds and read the value again. Git's text is back, and you did nothing.",
                "code": "$ kubectl -n hello get configmap hello-config -o jsonpath='{.data.GREETING}'\nHello from Kubernetes!",
                "lang": "console",
            },
            {
                "say": "To change the greeting for good, change git. Edit `k8s/configmap.yaml`, commit and push, then sync instead of waiting up to three minutes. Pods read environment variables only when they start (Day 34), so restart the Deployment to see the new text.",
                "code": "$ git commit -am \"Change the greeting\"\n$ git push\n$ argocd app sync hello-devops\n$ kubectl -n hello rollout restart deployment hello-devops",
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
        }
    ],
    "commands": [
        {"cmd": "kubectl create namespace argocd", "what": "Create the namespace where Argo CD runs."},
        {"cmd": "kubectl apply -n argocd --server-side --force-conflicts -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml", "what": "Install Argo CD. Server-side apply is required because one of its definitions is too big for normal apply."},
        {"cmd": "kubectl -n argocd get pods", "what": "Check that all seven Argo CD Pods are Running."},
        {"cmd": "kubectl -n argocd port-forward svc/argocd-server 8443:443", "what": "Open the UI at https://localhost:8443. Accept the self-signed certificate warning."},
        {"cmd": "brew install argocd", "what": "Install the argocd command line tool on your Mac."},
        {"cmd": "argocd admin initial-password -n argocd", "what": "Print the first password of the admin user."},
        {"cmd": "argocd login localhost:8443 --username admin --insecure", "what": "Log the CLI in through the port-forward. --insecure accepts the self-signed certificate."},
        {"cmd": "kubectl -n argocd get applications", "what": "List Applications with their sync and health status."},
        {"cmd": "argocd app get hello-devops --refresh", "what": "Check git now, then show the app's source, status and every object it manages."},
        {"cmd": "argocd app diff hello-devops", "what": "Show what differs between git and the cluster, like a git diff."},
        {"cmd": "argocd app sync hello-devops", "what": "Apply git now instead of waiting for the next check."},
        {"cmd": "argocd app history hello-devops", "what": "List past syncs with the git commit each one deployed."},
        {"cmd": "argocd app set hello-devops --sync-policy automated --self-heal --auto-prune", "what": "Turn on automated sync, self-heal and prune from the CLI."},
        {"cmd": "git revert HEAD", "what": "Make a new commit that undoes the last one. Push it, and Argo CD rolls back."},
    ],
    "mistake": "Fixing something in the cluster by hand and expecting the fix to stay. With self-heal on, Argo CD undoes `kubectl edit`, `kubectl scale` and even `kubectl delete` within seconds. With self-heal off, the fix lasts only until the next sync. Make the change in git and let Argo CD apply it. In a real emergency, turn off automated sync for that app first, and put the fix into git before you turn it back on.",
    "real_world": "A payments team might keep one config repo with a folder per environment. Merging a pull request into the prod folder is the deploy, and the review is the approval. When a release breaks at night, the on-call engineer reverts that pull request. Argo CD rolls the cluster back, and git records who did what, and why.",
    "task": {
        "title": "Put hello-devops under GitOps",
        "steps": [
            "Start your kind cluster from Day 30 if it is not running (`kind get clusters` should list `devops`). Push your latest `k8s/` folder to GitHub.",
            "Install Argo CD with the first two commands in the Commands list. Wait until all seven Pods in namespace `argocd` are Running.",
            "Start the port-forward, open the UI, and log in as `admin` with the initial password. Then log the CLI in too.",
            "Add `argocd/application.yaml` to your repo with your GitHub user name in `repoURL`. Commit, push, and apply it with kubectl.",
            "Watch the app until it shows Synced and Healthy. Click it in the UI and follow the tree from Deployment to ReplicaSet to Pods.",
            "Break a release on purpose: set the image in `k8s/deployment.yaml` to `hello-devops:9.9.9`, then commit, push and sync. Check that the app is Synced but not Healthy.",
            "Roll back with `git revert HEAD`, push and sync. Check that the app returns to Healthy.",
            "Test prune: remove `hpa.yaml` from the `resources` list in `k8s/kustomization.yaml`, commit and push. Watch Argo CD delete the HorizontalPodAutoscaler, then bring it back with another `git revert HEAD`.",
        ],
        "hints": [
            "If the app shows a repository error, Argo CD cannot read your repo. A public repo needs no password. For a private one, run `argocd repo add https://github.com/<you>/hello-devops --username <you> --password <token>` with a fine-grained token that can only read that repo.",
            "Argo CD checks git about every three minutes. Press Refresh in the UI, or run `argocd app sync hello-devops`, to skip the wait.",
            "kind has no image called `hello-devops:9.9.9`, so the new Pod tries Docker Hub and fails. `kubectl -n hello get pods` shows ImagePullBackOff, while the old Pods keep serving (Day 38).",
        ],
        "done_when": "After your last revert, `kubectl -n hello get hpa` lists hello-devops again, and `kubectl -n argocd get applications` shows it Synced and Healthy.",
    },
    "explain_back": {
        "prompt": "Explain GitOps to a teammate in 3 to 4 sentences. Mention who applies changes, what self-heal does, and how you roll back.",
        "answer": "With GitOps, git holds the desired state of the cluster, and an agent inside the cluster, Argo CD here, applies it. Nobody runs kubectl apply by hand: a change is a commit, usually through a pull request, and CI never needs a cluster key. Argo CD keeps comparing the cluster with git, and self-heal undoes changes that skipped git. To roll back, you revert the commit, and Argo CD deploys the old state.",
    },
    "recap": [
        "GitOps: git holds the desired state, and an agent in the cluster pulls it and keeps the cluster equal to it.",
        "Pull deploys keep cluster keys out of CI, and git gives you review, history and rollback.",
        "An Application links a repo folder to a cluster and namespace. Install Argo CD 3.x with server-side apply.",
        "Sync status says whether the cluster matches git; health says whether it works. They are independent.",
        "Automated sync applies commits, self-heal undoes hand edits, prune deletes what left git. The last two are off by default.",
        "Roll back with git revert, and tell Argo CD to ignore fields other controllers own, such as HPA replicas.",
    ],
    "check": [
        {
            "q": "The hello-devops app shows Synced and Degraded. What does that tell you?",
            "options": [
                "The cluster matches git, but what git describes does not work",
                "Someone edited the cluster by hand since the last sync",
                "Argo CD cannot reach your GitHub repo right now",
                "Prune is off, so old objects are still in the cluster",
            ],
            "answer": 0,
            "why": "Synced means live equals git; Degraded means the objects fail, so the problem is in what you committed, such as a bad image tag.",
        },
        {
            "q": "You delete `redis.yaml` from git and push. Automated sync is on, but prune is off. What happens to Redis in the cluster?",
            "options": [
                "It is deleted at the next sync",
                "Argo CD puts redis.yaml back into your repo",
                "It keeps running, and Argo CD marks it for pruning",
                "The sync fails and nothing else deploys",
            ],
            "answer": 2,
            "why": "Without prune, automated sync never deletes anything. The object stays, flagged as no longer in git, until someone prunes it.",
        },
        {
            "q": "A bad release is live, and self-heal is on. A colleague runs `kubectl rollout undo` (Day 32) to fix it fast. What happens next?",
            "options": [
                "The rollback stays until the next commit",
                "Argo CD writes the older version into git",
                "The Deployment is deleted and created again",
                "Argo CD puts the bad version back, because git still says so",
            ],
            "answer": 3,
            "why": "Self-heal makes the cluster match git, and git still holds the bad version. Revert in git instead.",
        },
    ],
    "interview": [
        {
            "q": "What is GitOps, and how is it different from a CI pipeline that runs kubectl apply?",
            "a": "GitOps keeps the desired state of a system in git, and an agent such as Argo CD or Flux pulls it and keeps the system equal to it. A push pipeline runs kubectl apply from outside, so it needs cluster credentials, and it only acts while it runs. The GitOps agent runs inside the cluster, keeps reconciling, and can undo drift. Every change is a commit, so review, history and rollback come from normal git tools.",
        },
        {
            "q": "How do you roll back a bad deploy in an Argo CD setup?",
            "a": "I revert the commit, or the pull request, that introduced the change and push, so git again describes the last good state. Argo CD syncs, and the cluster follows. Argo CD has its own rollback command, but it refuses to run while automated sync is on, and it would leave the cluster different from git. A git revert keeps one source of truth and leaves an audit trail.",
        },
        {
            "q": "What do sync status and health status mean in Argo CD?",
            "a": "Sync status compares the cluster with git: Synced means they match, OutOfSync means something differs. Health says whether the objects work, for example whether a Deployment's replicas are updated and available. They are independent. A bad image tag gives Synced but Degraded, and a harmless hand edit gives OutOfSync but Healthy. I check both before I call a deploy done.",
        },
    ],
    "deeper": {
        "minutes": 12,
        "body": t("""
            On Day 30 you saw that a controller has to know which objects are its own. A ReplicaSet uses labels and owner references. Argo CD has the same problem on a bigger scale: one cluster can hold objects from many Applications, plus objects that other controllers create.

            Since 3.0, Argo CD tracks objects with the annotation `argocd.argoproj.io/tracking-id`, in the form `app:group/Kind:namespace/name`. Before 3.0 the default was the label `app.kubernetes.io/instance`. That label caused two kinds of trouble:
            - Other tools copy labels, for example from a Deployment onto the Pods it makes, so a copied label could confuse Argo CD about what it owned.
            - Label values may be at most 63 characters, so long app names were cut short.

            The annotation names the exact object it sits on. If a tool copies it onto a different object, the name inside no longer matches, and Argo CD ignores the copy. You can still switch to label tracking in the `argocd-cm` ConfigMap, but there is rarely a reason to.

            Argo CD also ignores some objects on purpose. Since 3.0 its default settings exclude kinds that change all the time, such as EndpointSlice, Endpoints and Lease. EndpointSlices change every time a Pod becomes ready or not ready (Day 33). Watching all of them would load the API server for no benefit, because nobody keeps them in git anyway.

            Inside one object, Argo CD skips the `status` part by default, since the cluster writes it. You add your own exceptions with `ignoreDifferences`, as the lab does for replicas. Use it narrowly. Each ignored field is a place where git no longer tells the whole truth.

            Finally, an object that lives in the app's namespace but in no Application is an orphaned resource. Argo CD never deletes it, because it never created it. A project can turn on warnings for orphaned resources with `orphanedResources`. That is a cheap way to spot leftovers from hand-made experiments, as long as the namespaces are small.

            For hello-devops this all runs quietly in the background. It starts to matter when a second tool, such as a service mesh or an operator, writes to the same objects as Argo CD. Then `ignoreDifferences` and tracking decide who wins.
        """),
    },
    "sources": [
        {"title": "Argo CD: getting started", "url": L["getting_started"]},
        {"title": "Argo CD: automated sync policy", "url": L["auto_sync"]},
        {"title": "OpenGitOps principles", "url": L["principles"]},
        {"title": "Argo CD: resource tracking", "url": L["tracking"]},
    ],
}

# ======================================================================
# Day 40
# ======================================================================
# Real output captured with kustomize v5.8.3 against the lab overlays
# (see check_outputs.sh in this folder).
OVERLAY = {
    "dev_ns": "hello-dev",
    "prod_ns": "hello-prod",
}

D40_SECTIONS = [
    {
        "h": "Where the deployment files live",
        "body": t("""
            So far hello-devops keeps everything in one repo: the app code at the top, the Kubernetes YAML in `k8s/`. Teams usually pick one of three layouts:
            - One repo per app, with code and YAML together. This is what you have now.
            - An app repo for the code, plus a separate config repo that holds only YAML for every environment.
            - A monorepo: one big repo for many apps, with a folder per app and per environment.

            The [Argo CD best practices](https://argo-cd.readthedocs.io/en/stable/user-guide/best_practices/) page recommends a separate config repo. Its reasons, in short:
            - You can change a replica count without starting a full CI build.
            - The config history reads like a deploy log, without code commits in between.
            - One config repo can deploy an app built from several code repos as one unit.
            - Access can differ: many people may change code, while few may change prod.
            - CI that commits YAML into the code repo can trigger itself in a loop.

            That last point needs care in GitHub Actions. A push made with the workflow's own `GITHUB_TOKEN` does not start new workflow runs, which stops most loops. A push made with a personal token does start them.

            For one person and a laptop cluster, one repo is fine, and this lesson keeps it. The cost is small: a commit that changes only `k8s/` still runs `ci.yml` on main. If that bothers you, add `k8s/**` to the `paths-ignore` list of its push trigger.
        """),
        "refs": [
            ref("Argo CD docs: best practices (config repo vs code repo)", L["best"], "docs"),
            ref("GitHub docs: GITHUB_TOKEN and which events it triggers", L["gh_token"], "docs"),
        ],
    },
    {
        "h": "One app, many environments",
        "body": t("""
            An environment is one running copy of the app with one purpose. Dev is where new versions land first, and prod is what users see. Real teams usually give prod its own cluster. Here both live in your kind cluster, in the namespaces `hello-dev` and `hello-prod`.

            On Day 37 you met Kustomize overlays, and the lab has two: `k8s/overlays/dev` and `k8s/overlays/prod`. Each one takes the shared files and changes a few things, such as the namespace, the replica count or the image tag. `kubectl kustomize k8s/overlays/prod` prints exactly what prod gets.

            Argo CD needs one Application per environment. You could copy `application.yaml` twice and change three lines in each copy. An **ApplicationSet** writes those copies for you. It has two parts:
            - Generators produce a list of values. The lab uses the list generator with two entries, `env: dev` and `env: prod`.
            - A template is an ordinary Application with placeholders such as `{{.env}}`. The controller fills it in once per entry.

            Apply `argocd/applicationset.yaml`, and two Applications appear: `hello-devops-dev` and `hello-devops-prod`. Add a third entry, and a third app appears. Delete the ApplicationSet, and its Applications go too, along with everything they deployed. Other generators read their list from elsewhere: folders in a git repo, the clusters Argo CD knows, or open pull requests.

            You will also meet app of apps: one parent Application whose folder holds only other Application files. It came first, and it still works. The Argo CD docs recommend ApplicationSets for most cases. They call app of apps an admin-only tool, because anyone who can push to that folder can create apps in any project.
        """),
        "refs": [
            ref("Argo CD docs: ApplicationSet controller", L["appset"], "docs"),
            ref("Argo CD docs: the list generator", L["list_gen"], "docs"),
            ref("Argo CD tutorial: app of apps in 8 minutes (Akuity)", L["v_akuity_aoa"], "watch"),
        ],
    },
    {
        "h": "Promotion is a pull request",
        "body": t("""
            **Promotion** means moving a version that passed in one environment on to the next. In GitOps it is a small change to text in git:
            1. CI builds `ghcr.io/<you>/hello-devops:1.2.0` once, when you push the tag `v1.2.0` (Day 21).
            2. A pull request sets the dev overlay to `1.2.0`. You merge it, and Argo CD deploys dev.
            3. You test dev.
            4. A second pull request sets the prod overlay to the same `1.2.0`. Someone reviews and merges it, and Argo CD deploys prod.

            The image never gets rebuilt. Prod runs the exact bytes that dev ran, which is the build once, deploy many idea from Day 17. The pull request gives you a review, a record of who approved it, and a clean undo: the Revert button on a merged pull request opens a new one that puts the old tag back.

            This only works if a tag always means the same image. Never deploy `latest`. It points at different images over time, so git no longer tells you what runs, and a revert cannot bring the old version back. That breaks the "versioned and immutable" principle from Day 39. A version tag such as `1.2.0` is good. A digest such as `@sha256:...` is stronger, because nobody can move it, and the `images` field in a kustomization accepts a `digest` too.

            Some teams want reviewers to see the final YAML, not just a changed tag. Argo CD's Source Hydrator renders each environment and commits the plain YAML to git before it syncs. It is a Beta feature since Argo CD 3.5 and off by default. Tools such as [Kargo](https://github.com/akuity/kargo) and [GitOps Promoter](https://github.com/argoproj-labs/gitops-promoter) go further and automate the promotion steps themselves.
        """),
        "refs": [
            ref("GitHub docs: reverting a pull request", L["gh_revert_pr"], "docs"),
            ref("Argo CD docs: Source Hydrator (Beta)", L["hydrator"], "docs"),
            ref("Kargo demo: GitOps promotion across environments with Argo CD", L["v_kargo"], "watch"),
        ],
    },
    {
        "h": "Getting a new tag into git",
        "body": t("""
            Argo CD deploys only what git says, so something has to write each new tag into a file. Teams use two common ways.

            The first is a CI job that edits the file and opens a pull request. The lab's `bump-image.yml` workflow does this. You give it an environment and a version, and it:
            1. Checks out the repo.
            2. Runs `kustomize edit set image hello-devops=ghcr.io/<you>/hello-devops:1.2.0` inside that environment's overlay.
            3. Pushes a branch and opens a pull request with the `gh` CLI.

            New personal repos do not let workflows open pull requests. You allow it once, under Settings, Actions, General, Workflow permissions. Also know that `kustomize edit` rewrites the whole file in its own style. It drops comments at the end of lines and changes how lists are indented. Keep comments at the top of the file, and the first bump will not surprise you.

            The second way is [Argo CD Image Updater](https://github.com/argoproj-labs/argocd-image-updater), a separate add-on. It watches your registry, and when a version that matches your rule appears, it writes the new tag for you. Since its 1.0 release you configure it with its own custom resource, `ImageUpdater`; the lab's optional `argocd/image-updater.yaml` is one. With the `git` write-back method it commits straight to the branch, with no pull request. Its README says it is under active development and not yet recommended for critical production workloads.

            My advice: start with the CI pull request for every environment. If the dev pull requests turn into busywork, let Image Updater handle dev, and keep prod on pull requests.
        """),
        "refs": [
            ref("GitHub docs: allowing workflows to create pull requests", L["gh_actions_settings"], "docs"),
            ref("Argo CD Image Updater (GitHub)", L["image_updater"], "docs"),
            ref("GitHub docs: manually running a workflow", L["gh_manual_run"], "docs"),
        ],
    },
    {
        "h": "Putting things in order: sync waves and hooks",
        "body": t("""
            Argo CD applies everything in one sync, in a sensible default order: Namespaces first, then other built-in kinds, then custom resources. Sometimes you need more control. Redis should be ready before the app starts, or a database migration must finish before new code arrives.

            A sync wave is an annotation on any object: `argocd.argoproj.io/sync-wave: "-1"`. Argo CD applies the lowest wave first and waits until it is in sync and healthy before it starts the next. Objects without the annotation are in wave 0, and negative numbers are allowed. Argo CD also pauses for 2 seconds between waves.

            A hook is an object, usually a Job, that runs at a set point of the sync. You mark it with the annotation `argocd.argoproj.io/hook`:
            - `PreSync` runs before anything is applied. If it fails, the sync stops. Use it for a database migration.
            - `Sync` runs together with the normal objects.
            - `PostSync` runs after everything is applied and Healthy. Use it for a smoke test.
            - `SyncFail` runs when the sync fails, for clean-up or an alert.

            The lab's `gitops/smoke-test.yaml` is a PostSync hook. It calls `/healthz` once with curl. If curl gets an error, Argo CD marks the sync as failed, and you see it in the UI. A second annotation, `argocd.argoproj.io/hook-delete-policy`, decides when Argo CD deletes the finished Job.

            One catch: hooks do not run during a selective sync, when you sync only some of an app's objects. Sync the whole app when you want the hooks.
        """),
        "refs": [
            ref("Argo CD docs: sync phases, waves and hooks", L["waves"], "docs"),
        ],
    },
    {
        "h": "Secrets in a GitOps repo",
        "body": t("""
            Anyone with access to the repo can read everything in it, and git keeps every old version. A plain Kubernetes Secret is only base64 encoded (Day 34), so committing one is the same as committing the password. Three common ways out:
            - Sealed Secrets: you encrypt a Secret on your laptop with `kubeseal` and the cluster's public key, then commit the result, a SealedSecret. Only the controller in that cluster holds the private key that turns it back into a Secret.
            - External Secrets Operator: git holds only a pointer, an ExternalSecret that names an entry in a store such as AWS Secrets Manager or Vault. The operator copies the value into a Secret in the cluster.
            - SOPS: encrypts the values inside a YAML file with a key from age or a cloud key service. The keys of the file stay readable; the values do not. Flux can decrypt SOPS files itself, while Argo CD needs a plugin.

            Argo CD's [secret management](https://argo-cd.readthedocs.io/en/stable/operator-manual/secret-management/) page strongly recommends the styles where the Secret is created in the destination cluster, such as the first two. Argo CD never sees the value. It cautions against plugins that inject secrets while Argo CD renders the YAML, because those values then sit in Argo CD's Redis cache in plain text.

            hello-devops has no real secrets yet, so the lab needs none of this today. Day 53 goes deeper into secrets, access and policy.
        """),
        "refs": [
            ref("Argo CD docs: secret management", L["secrets"], "docs"),
            ref("Sealed Secrets (GitHub)", L["sealed"], "docs"),
            ref("TGI Kubernetes 132: Sealed Secrets", L["v_tgik_sealed"], "watch"),
        ],
    },
    {
        "h": "Projects, access and Flux",
        "body": t("""
            Everything on Day 39 used the `default` project, which allows any repo, any cluster, any namespace and any kind of object. An AppProject narrows that down for a group of apps. The lab's `argocd/project.yaml` allows:
            - One source repo: yours.
            - Three namespaces in the local cluster: `hello`, `hello-dev` and `hello-prod`.
            - No cluster-wide objects except Namespaces.

            Point an app in this project at another repo, or at `kube-system`, and Argo CD refuses to sync it. Projects also hold roles: the lab's `viewer` role may look at the apps and read logs, nothing more.

            Who may do what in the UI and CLI is Argo CD's own RBAC, separate from Kubernetes RBAC (Day 38). A fresh install has one user, `admin`, who may do everything. Teams connect single sign-on and map groups to roles, either the built-in `role:readonly` and `role:admin` or their own. Argo CD 3.x changed two defaults that older guides get wrong. The right to update or delete an Application no longer covers the objects inside it, and reading Pod logs needs its own `logs` permission.

            [Flux](https://github.com/fluxcd/flux2) is the other big GitOps tool. Like Argo CD it is a graduated CNCF project, and the ideas from these two days carry over. The differences are mostly about style:
            - Flux is a set of small controllers that you drive with YAML and the `flux` CLI. Its core has no web UI; the separate [Flux Operator](https://fluxoperator.dev/web-ui/) adds one.
            - Flux usually runs inside every cluster it manages, while one Argo CD often manages many clusters from one place.
            - Flux has image automation and SOPS decryption built in; Argo CD uses Image Updater and plugins.

            Choose Argo CD when people want a UI to see and sync apps. Choose Flux when the team wants everything as YAML and no central server. Both are sound choices.
        """),
        "refs": [
            ref("Argo CD docs: projects", L["projects"], "docs"),
            ref("Argo CD docs: RBAC configuration", L["rbac"], "docs"),
            ref("Introduction to GitOps, Argo CD, and Flux (Viktor Farcic)", L["v_farcic_intro"], "watch"),
        ],
    },
]

D40_DIAGRAM = (
    '<svg viewBox="0 0 560 214" xmlns="http://www.w3.org/2000/svg" role="img" '
    'aria-label="Promotion: a new image is bumped into the dev overlay by pull request, then promoted to the prod overlay by pull request; Argo CD syncs each overlay to its namespace">'
    '<rect class="bxg" x="16" y="30" width="120" height="48" rx="10"/>'
    '<text class="tk" x="76" y="59" font-size="13" text-anchor="middle">New image</text>'
    '<rect class="bxt" x="220" y="30" width="120" height="48" rx="10"/>'
    '<text class="tk" x="280" y="59" font-size="13" text-anchor="middle">dev overlay</text>'
    '<rect class="bxt" x="424" y="30" width="120" height="48" rx="10"/>'
    '<text class="tk" x="484" y="59" font-size="13" text-anchor="middle">prod overlay</text>'
    '<line class="ln" x1="138" y1="54" x2="216" y2="54" marker-end="url(#ar)"/>'
    '<text class="ts" x="177" y="44" font-size="11" text-anchor="middle">bump PR</text>'
    '<line class="ln" x1="342" y1="54" x2="420" y2="54" marker-end="url(#ar)"/>'
    '<text class="ts" x="381" y="44" font-size="11" text-anchor="middle">promote PR</text>'
    '<text class="ts" x="76" y="98" font-size="11" text-anchor="middle">built once</text>'
    '<line class="ln" x1="280" y1="80" x2="280" y2="146" marker-end="url(#ar)"/>'
    '<text class="ts" x="320" y="117" font-size="11" text-anchor="middle">Argo CD</text>'
    '<line class="ln" x1="484" y1="80" x2="484" y2="146" marker-end="url(#ar)"/>'
    '<text class="ts" x="522" y="117" font-size="11" text-anchor="middle">Argo CD</text>'
    '<rect class="bxo" x="220" y="150" width="120" height="48" rx="10"/>'
    '<text class="tk" x="280" y="179" font-size="13" text-anchor="middle">hello-dev</text>'
    '<rect class="bxo" x="424" y="150" width="120" height="48" rx="10"/>'
    '<text class="tk" x="484" y="179" font-size="13" text-anchor="middle">hello-prod</text>'
    '<text class="ts" x="76" y="179" font-size="11" text-anchor="middle">in the cluster</text>'
    "</svg>"
)

D40 = {
    "id": "d40",
    "title": "GitOps in practice: environments, promotion and image updates",
    "minutes": 50,
    "goal": "By the end you can run hello-devops as dev and prod from one ApplicationSet, promote a tested version from dev to prod with a pull request, and pick a safe way to keep secrets out of a GitOps repo.",
    "guess": {
        "q": "Version 1.2.0 runs well in dev. In a GitOps setup, how do you move it to prod?",
        "options": [
            "Rebuild the image from the main branch for prod",
            "Run `kubectl set image` in the prod namespace",
            "Copy the 1.2.0 tag into the prod folder with a pull request",
            "Click Sync on the prod app in the Argo CD UI",
        ],
        "answer": 2,
        "why": "Promotion is a change in git: prod gets the exact tag that dev already runs. A rebuild could ship different bytes, a kubectl edit gets undone, and Sync only applies what git already says.",
    },
    "terms": [
        {"term": "Config repo", "plain": "A git repo that holds only deployment files, kept apart from the app's source code."},
        {"term": "Environment", "plain": "One running copy of the app with one purpose, such as dev for testing or prod for users."},
        {"term": "Overlay", "plain": "A Kustomize folder that takes the shared base files and changes a few settings for one environment."},
        {"term": "Promotion", "plain": "Moving a tested version to the next environment, in GitOps by changing its tag in git."},
        {"term": "ApplicationSet", "plain": "An Argo CD object that creates many Applications from one template and a list of values."},
        {"term": "AppProject", "plain": "An Argo CD object that limits which repos, namespaces and kinds of objects a group of apps may use."},
        {"term": "Sync wave", "plain": "An annotation that sets the order in which Argo CD applies objects, lowest number first."},
        {"term": "Sealed Secret", "plain": "An encrypted Secret that is safe to commit, because only a controller in the cluster can decrypt it."},
    ],
    "sections": D40_SECTIONS,
    "analogy": "Think of a book on its way to print. The same text file goes from the editor to the proofreader to the printer, and each hand-over needs a signature. Nobody retypes the book at each step, so the printer prints exactly what the proofreader approved. Where it breaks: environments are not perfect copies, since prod gets more replicas than dev, while every copy of a book is meant to be the same.",
    "diagram": D40_DIAGRAM,
    "diagram_caption": "One image, two pull requests. Argo CD deploys each overlay to its own namespace.",
    "worked": {
        "title": "Promote 1.1.0 from dev to prod by hand",
        "steps": [],  # filled in below from real outputs
    },
    "code": [
        {
            "lang": "yaml",
            "title": "argocd/project.yaml",
            "src": lab("argocd/project.yaml"),
            "run": "kubectl apply -n argocd -f argocd/project.yaml",
        },
        {
            "lang": "yaml",
            "title": "argocd/applicationset.yaml",
            "src": lab("argocd/applicationset.yaml"),
            "run": "kubectl apply -n argocd -f argocd/applicationset.yaml",
        },
        {
            "lang": "yaml",
            "title": ".github/workflows/bump-image.yml",
            "src": lab("gitops/bump-image.yml"),
            "run": "gh workflow run bump-image.yml -f environment=dev -f version=1.2.0",
        },
        {
            "lang": "yaml",
            "title": "gitops/smoke-test.yaml",
            "src": lab("gitops/smoke-test.yaml"),
            "run": "cp gitops/smoke-test.yaml k8s/overlays/dev/",
        },
        {
            "lang": "yaml",
            "title": "argocd/image-updater.yaml (optional)",
            "src": lab("argocd/image-updater.yaml"),
            "run": "kubectl apply -n argocd -f argocd/image-updater.yaml",
        },
    ],
    "commands": [
        {"cmd": "kubectl -n argocd delete application hello-devops", "what": "Remove the Day 39 app and everything it deployed, before dev and prod take over."},
        {"cmd": "kubectl apply -n argocd -f argocd/project.yaml -f argocd/applicationset.yaml", "what": "Create the project, then the ApplicationSet that makes the dev and prod apps."},
        {"cmd": "kubectl -n argocd get applicationsets", "what": "List ApplicationSets."},
        {"cmd": "kubectl -n argocd get applications -L env", "what": "List Applications with an extra column for their env label."},
        {"cmd": "argocd proj get hello", "what": "Show the project's allowed repos, destinations and roles."},
        {"cmd": "kubectl kustomize k8s/overlays/prod", "what": "Print the exact YAML that prod gets, without touching the cluster."},
        {"cmd": "brew install kustomize", "what": "Install the standalone kustomize tool, which has the edit commands."},
        {"cmd": "kustomize edit set image hello-devops=ghcr.io/<your-github-user>/hello-devops:1.2.0", "what": "Run inside an overlay folder. Writes the image name and tag into its kustomization.yaml."},
        {"cmd": "gh workflow run bump-image.yml -f environment=dev -f version=1.2.0", "what": "Start the bump workflow from your terminal with its two inputs."},
        {"cmd": "gh run watch", "what": "Follow a workflow run live until it finishes."},
        {"cmd": "gh pr list", "what": "List open pull requests, including the ones the workflow opened."},
        {"cmd": "gh pr merge <number> --squash --delete-branch", "what": "Merge a pull request as one commit and delete its branch."},
        {"cmd": "kubectl -n hello-prod get deployment hello-devops -o jsonpath='{.spec.template.spec.containers[0].image}'", "what": "Print the image that prod runs right now."},
    ],
    "mistake": "Deploying `latest` and expecting GitOps to handle versions. If an overlay says `latest`, git does not change when the image does, so Argo CD sees nothing to sync and a revert brings nothing back. Give every release its own version tag (or pin a digest), and promote by changing that tag in git.",
    "real_world": "A payments team might run dev, staging and prod clusters from one config repo, with one ApplicationSet per app that uses the cluster generator. CI opens the dev pull request after every release and merges it once checks pass. Prod needs a second pull request, approved by someone on the on-call rotation, and a PostSync smoke test fails the sync if checkout stops answering.",
    "task": {
        "title": "Run dev and prod from one ApplicationSet",
        "steps": [
            "Make sure at least one release exists in GHCR from Day 21, for example `1.0.0`. Open the package settings on GitHub and make it public, so kind can pull it without a password.",
            "Delete the Day 39 Application, so its NodePort and namespace do not clash with the new apps.",
            "Add `argocd/project.yaml` and `argocd/applicationset.yaml` with your GitHub user name. Commit, push, and apply both.",
            "Check that two Applications appear and both turn Synced and Healthy.",
            "Add `.github/workflows/bump-image.yml`, push it, and allow workflows to create pull requests in the repo settings.",
            "Tag and push a new release (for example `v1.1.0`), wait for `release.yml` to finish, then run the bump workflow for dev with that version.",
            "Review and merge the pull request. Confirm that dev runs the new tag and prod still runs the old one.",
            "Promote: run the bump workflow again for prod with the same version, merge, and confirm both environments now match.",
            "Optional: add the smoke-test hook to the dev overlay, then break its URL and watch the dev sync fail.",
        ],
        "hints": [
            "The workflow opens the pull request with `GITHUB_TOKEN`, so `ci.yml` waits for you to approve its run on that pull request. Look for the banner in the merge box.",
            "If a new Pod shows ImagePullBackOff, check the image name in `kubectl kustomize k8s/overlays/dev` and that the GHCR package is public.",
            "Not sure what changed? `kubectl kustomize k8s/overlays/dev > /tmp/dev.yaml` before and after the bump, then `diff` the two files.",
        ],
        "done_when": "You are done when the jsonpath command from the Commands list prints the same new tag for `hello-dev` and `hello-prod`, and both apps show Synced and Healthy.",
    },
    "explain_back": {
        "prompt": "Explain to a teammate, in 3 to 4 sentences, how version 1.3.0 travels from a git tag to prod in this setup. Mention who builds the image, what changes in git, and what Argo CD does.",
        "answer": "Pushing the tag v1.3.0 starts release.yml, which builds the image once and pushes it to GHCR as 1.3.0. A workflow then opens a pull request that sets the dev overlay to 1.3.0; after the merge, Argo CD sees the commit and deploys dev. When dev looks good, a second pull request copies the same tag into the prod overlay, someone reviews it, and Argo CD deploys prod. If prod breaks, reverting that pull request puts the old tag back.",
    },
    "recap": [
        "Deployment YAML lives in git, in the app repo or a separate config repo with cleaner history and access.",
        "Each environment gets one overlay and one Application; an ApplicationSet writes the Applications from one template.",
        "Promotion is a pull request that copies a tested, immutable tag to the next overlay. Never deploy latest.",
        "CI writes new tags with kustomize edit set image and a pull request; Image Updater can do it for dev.",
        "Sync waves order objects, hooks run Jobs before or after a sync, and secrets stay out of git as Sealed or External Secrets.",
        "AppProjects limit repos, namespaces and kinds. Flux is the main alternative to Argo CD.",
    ],
    "check": [
        {
            "q": "You add `env: staging, namespace: hello-staging` to the list generator and create `k8s/overlays/staging`. The new app appears but never syncs. Why?",
            "options": [
                "The hello project does not allow the hello-staging namespace",
                "An ApplicationSet can make at most two Applications",
                "Staging needs its own Argo CD install to work",
                "The overlay folder must be named stage, not staging",
            ],
            "answer": 0,
            "why": "The AppProject lists the allowed destinations, so you also have to add hello-staging to project.yaml.",
        },
        {
            "q": "Image Updater runs with the lab's settings and finds a new version 1.4.0. What appears in your repo?",
            "options": [
                "A pull request that waits for your review",
                "Nothing; it patches only the live Deployment",
                "A new git tag v1.4.0 on the main branch",
                "A commit on main that changes the dev kustomization",
            ],
            "answer": 3,
            "why": "With git write-back and the kustomization target, it commits straight to the tracked branch, with no pull request.",
        },
        {
            "q": "A Job marked `argocd.argoproj.io/hook: PreSync` runs a database migration and fails. What happens to the new app version?",
            "options": [
                "Argo CD applies it anyway and marks the sync failed",
                "The sync stops before the other objects are applied",
                "Argo CD retries the Job until the migration passes",
                "The Job is skipped and the sync carries on as usual",
            ],
            "answer": 1,
            "why": "A failed PreSync hook stops the whole sync, so new code never meets an old database schema.",
        },
    ],
    "interview": [
        {
            "q": "How do you promote a release between environments with GitOps?",
            "a": "CI builds the image once and tags it with a version, never latest. Each environment has its own folder, for example a Kustomize overlay, and promotion is a pull request that copies the tested tag or digest from one folder to the next. The review is the approval, and the merge is the deploy, because Argo CD or Flux syncs the change. Rolling back is a revert of that pull request.",
        },
        {
            "q": "How do you handle secrets when everything lives in git?",
            "a": "I never commit plain Secrets, because base64 is not encryption and git keeps history forever. I either commit encrypted SealedSecrets that only the in-cluster controller can decrypt, or I commit ExternalSecret references and let the External Secrets Operator fetch the values from a store such as Vault or AWS Secrets Manager. Argo CD recommends these destination-cluster styles. I avoid plugins that inject secrets while Argo CD renders manifests, because those values land in its cache.",
        },
        {
            "q": "When would you choose Flux over Argo CD?",
            "a": "Both are graduated CNCF projects that pull from git and reconcile, so the core idea is the same. I would pick Argo CD when people want a web UI to see app health and sync by hand, or when one central instance should manage many clusters. I would pick Flux when the team prefers everything as YAML and the CLI, runs one controller set per cluster, and wants image automation and SOPS decryption built in. Either way, the repo layout and promotion flow look much the same.",
        },
    ],
    "deeper": {
        "minutes": 12,
        "body": t("""
            Your setup is one cluster with two namespaces. A company with fifty clusters uses the same ideas, only generated.

            Start with the generator. The cluster generator makes one Application per cluster that Argo CD knows. It can filter by labels on those clusters, such as `env: prod` or `region: eu`. Register a new cluster with the right labels, and every matching ApplicationSet deploys to it. The [Argo CD docs on cluster bootstrapping](https://argo-cd.readthedocs.io/en/stable/operator-manual/cluster-bootstrapping/) recommend exactly this for new clusters. The matrix generator combines two generators, for example every folder under `apps/` times every cluster labelled `env: dev`.

            Then decide where Argo CD itself runs:
            - Hub and spoke: one Argo CD in a management cluster deploys to all the others. You get one UI and one place for access rules. If the hub is down, nothing new deploys, though running apps keep running.
            - One Argo CD per cluster: no single point of failure, but more installs to upgrade. This is also the usual Flux model.

            Changing fifty clusters at once is risky. ApplicationSet Progressive Syncs, a Beta feature, update the generated apps in steps. For example, dev clusters go first, then a few prod clusters, then the rest, and each step waits until the previous one is healthy.

            Last, the rendered manifests pattern. With overlays and charts, a one-line change in a base can change the YAML of every environment, and the pull request does not show it. The Source Hydrator (Beta since Argo CD 3.5, off by default) renders each environment, commits the plain YAML to a separate branch, and syncs from there. Reviewers then read the exact YAML that will run, and `git diff` between two commits shows exactly what changed in prod.

            You can get a cheap version of this today. In a pull request check, run `kubectl kustomize` for each overlay on both the main branch and the pull request branch, and post the diff as a comment. A reviewer who sees "prod: replicas 3 to 6" catches mistakes that "base/deployment.yaml: one line changed" hides.
        """),
    },
    "sources": [
        {"title": "Argo CD: ApplicationSet controller", "url": L["appset"]},
        {"title": "Argo CD: best practices", "url": L["best"]},
        {"title": "Argo CD: sync phases and waves", "url": L["waves"]},
        {"title": "Argo CD: secret management", "url": L["secrets"]},
    ],
}

# Worked example for Day 40: real kustomize and git output, captured by
# check_outputs.sh into outputs/ (see that script). Argo CD and gh output
# is the documented format, because kind cannot start a cluster here.
OUTS = pathlib.Path(__file__).resolve().parent / "outputs"


def out(name):
    return (OUTS / name).read_text().rstrip("\n")


D40["worked"]["steps"] = [
    {
        "say": "Ask git, not the cluster, what each environment should run. `kubectl kustomize` renders an overlay on your laptop and never touches the cluster. Here dev and prod still run the same release.",
        "code": out("01-images-before.txt"),
        "lang": "console",
    },
    {
        "say": "Bump dev. Run kustomize inside the dev overlay; it edits only that folder's `kustomization.yaml`. Read the diff before you commit: one line changes.",
        "code": out("02-bump-dev.txt"),
        "lang": "console",
    },
    {
        "say": "Ship it like any other change: a branch, a commit and a pull request. Argo CD watches only `main`, so nothing deploys until you merge.",
        "code": "$ git switch -c bump/dev-1.1.0\n$ git commit -am \"Deploy hello-devops 1.1.0 to dev\"\n$ git push -u origin bump/dev-1.1.0\n$ gh pr create --fill\n$ gh pr merge --squash --delete-branch",
        "lang": "console",
    },
    {
        "say": "Within about three minutes Argo CD picks up the merge. Only the dev app syncs, because only the dev folder changed. Prod keeps the old tag.",
        "code": "$ kubectl -n hello-dev get deployment hello-devops \\\n    -o jsonpath='{.spec.template.spec.containers[0].image}'\nghcr.io/<you>/hello-devops:1.1.0\n$ kubectl -n hello-prod get deployment hello-devops \\\n    -o jsonpath='{.spec.template.spec.containers[0].image}'\nghcr.io/<you>/hello-devops:1.0.0",
        "lang": "console",
    },
    {
        "say": "Test dev. When you trust 1.1.0, make the same edit in the prod overlay. The diff is again one line, which makes the prod review quick. Open the pull request, get it approved, and merge.",
        "code": out("03-promote-prod.txt"),
        "lang": "console",
    },
    {
        "say": "If prod misbehaves after the merge, press Revert on the merged pull request and merge the revert. Argo CD puts the old tag back in prod, and dev keeps 1.1.0 for more testing.",
    },
]

# ======================================================================
# Part extras
# ======================================================================
PART = {
    "part": 8,
    "title": "GitOps with Argo CD",
    "intro": "In Part 7 you ran hello-devops on Kubernetes by typing kubectl commands. Part 8 hands the deploying to Argo CD: git holds the desired state, and a controller in the cluster keeps the cluster equal to it. Day 39 sets up Argo CD and shows drift, self-heal and rollback. Day 40 adds dev and prod, promotion by pull request, and the habits teams use for image updates, secrets and access.",
    "lessons": [D39, D40],
    "recap": [
        "GitOps: git holds the desired state, and an agent in the cluster pulls it and reconciles.",
        "Pull deploys keep cluster credentials out of CI and turn every deploy into a commit.",
        "Argo CD 3.x installs with server-side apply and tracks its objects with an annotation.",
        "Sync status (does it match git?) and health (does it work?) are separate signals.",
        "Self-heal and prune are off by default; ignore fields that other controllers own.",
        "Roll back with git revert or the Revert button on the pull request.",
        "One overlay and one Application per environment; an ApplicationSet generates the Applications.",
        "Promotion copies a tested, immutable tag to the next environment through a pull request.",
        "Secrets stay out of git through Sealed Secrets, External Secrets or SOPS; AppProjects and RBAC limit who deploys where.",
    ],
    "flashcards": [
        {"front": "What are the four OpenGitOps principles?", "back": "Declarative; versioned and immutable; pulled automatically; continuously reconciled."},
        {"front": "Push deploy or pull deploy: which one needs a cluster key in CI?", "back": "Push. In a pull deploy, an agent inside the cluster fetches from git and applies."},
        {"front": "Why does installing Argo CD 3.x need kubectl apply --server-side?", "back": "The ApplicationSet definition is too big for the annotation that client-side apply writes."},
        {"front": "Sync status vs health status?", "back": "Sync: does the cluster match git? Health: do the objects work?"},
        {"front": "What does selfHeal do, and is it on by default?", "back": "It undoes changes made in the cluster but not in git. It is off by default."},
        {"front": "What does prune do, and is it on by default?", "back": "It deletes objects you removed from git. It is off by default."},
        {"front": "How does Argo CD 3.x remember which app owns an object?", "back": "The annotation argocd.argoproj.io/tracking-id on that object."},
        {"front": "How often does Argo CD check git by default?", "back": "About every 3 minutes (120 s plus up to 60 s of jitter). A webhook makes it immediate."},
        {"front": "Why does the lab ignore /spec/replicas?", "back": "So Argo CD and the autoscaler do not fight over the replica count."},
        {"front": "How do you roll back an app that Argo CD syncs automatically?", "back": "Revert the commit or pull request in git. Argo CD deploys the old state."},
        {"front": "What is an ApplicationSet?", "back": "A template plus generators that create many Applications, for example one per environment."},
        {"front": "What is promotion in GitOps?", "back": "A pull request that copies a tested image tag from one environment's folder to the next."},
        {"front": "Why never deploy the latest tag with GitOps?", "back": "Git does not change when the image does, so you cannot see or revert what runs."},
        {"front": "What does kustomize edit set image do?", "back": "It writes a new image name and tag into the kustomization.yaml of the current folder."},
        {"front": "When does a PostSync hook run?", "back": "After all objects are applied and Healthy. A smoke test is a typical use."},
        {"front": "Which secret styles does Argo CD recommend?", "back": "Ones that create the Secret in the cluster, such as Sealed Secrets or External Secrets Operator."},
        {"front": "What does an AppProject limit?", "back": "Which repos, clusters, namespaces and kinds of objects its apps may use."},
        {"front": "Main style difference between Flux and Argo CD?", "back": "Flux: controllers in each cluster, driven by YAML and CLI. Argo CD: often one central server with a web UI."},
    ],
    "resources": [
        {"title": "Argo CD: getting started", "url": L["getting_started"], "kind": "docs", "why": "The official install and first-app guide, kept current for Argo CD 3.x."},
        {"title": "OpenGitOps principles", "url": L["principles"], "kind": "read", "why": "The four GitOps principles in one short page, written by the CNCF working group."},
        {"title": "ArgoCD tutorial for beginners (TechWorld with Nana)", "url": L["v_nana"], "kind": "watch", "why": "A clear visual walk-through of Argo CD; its install command predates the 3.x server-side flag."},
        {"title": "Introduction to GitOps, Argo CD, and Flux (Viktor Farcic)", "url": L["v_farcic_intro"], "kind": "watch", "why": "A conversation that puts Argo CD and Flux side by side and explains why GitOps exists."},
        {"title": "Argo CD tutorial: app of apps in 8 minutes (Akuity)", "url": L["v_akuity_aoa"], "kind": "watch", "why": "A short demo of the parent-app pattern you will see in many company repos."},
        {"title": "Argo CD: ApplicationSet controller", "url": L["appset"], "kind": "docs", "why": "Every generator, with examples you can adapt for more environments or clusters."},
        {"title": "Argo CD: best practices", "url": L["best"], "kind": "docs", "why": "Short and practical: config repos, replicas and HPAs, and pinning remote bases."},
        {"title": "Argo CD: secret management", "url": L["secrets"], "kind": "docs", "why": "Why the project prefers in-cluster secret tools over render-time plugins."},
        {"title": "Argo CD Image Updater", "url": L["image_updater"], "kind": "docs", "why": "The add-on that writes new image tags for you, configured with its ImageUpdater resource."},
        {"title": "Flux (GitHub)", "url": L["flux"], "kind": "docs", "why": "The other graduated GitOps project, with links to its guides on image updates and SOPS."},
        {"title": "GitOps certification with Argo (Codefresh)", "url": L["codefresh"], "kind": "read", "why": "A free course with hosted labs; it was built on Argo CD 2.x, but the GitOps ideas hold."},
    ],
    "quiz": [
        {
            "q": "Automated sync is on and selfHeal is off. A teammate edits the live ConfigMap by hand. What do you see in Argo CD?",
            "options": [
                "The edit is undone within a few seconds",
                "The app shows OutOfSync, and the edit stays for now",
                "The app shows Degraded until someone syncs it",
                "Argo CD commits the edit into git for you",
            ],
            "answer": 1,
            "why": "Without self-heal, live changes do not trigger a sync. The drift is reported and stays until the next commit is synced.",
        },
        {
            "q": "Which Argo CD component turns your Kustomize folder into plain YAML?",
            "options": [
                "The application controller",
                "The API server",
                "The repository server",
                "The Dex server",
            ],
            "answer": 2,
            "why": "The repo server clones the repo and renders Kustomize or Helm; the controller then compares and applies.",
        },
        {
            "q": "You follow an old video and run plain `kubectl apply -n argocd -f install.yaml`. It fails on the ApplicationSet definition. What is the fix?",
            "options": [
                "Add --server-side --force-conflicts to the apply",
                "Install an older Kubernetes version in kind",
                "Delete the ApplicationSet definition from the file",
                "Run the same command again until it passes",
            ],
            "answer": 0,
            "why": "That definition is too large for client-side apply's annotation; server-side apply does not write that annotation.",
        },
        {
            "q": "After a tag change in git, your app stays Synced and Progressing for many minutes. What is the most likely cause?",
            "options": [
                "Argo CD cannot reach the git repository",
                "Self-heal is fighting with the autoscaler",
                "The project forbids the destination namespace",
                "The new Pods cannot start, for example the image cannot be pulled",
            ],
            "answer": 3,
            "why": "Synced means the cluster has what git says; a rollout that never finishes points at the new Pods themselves.",
        },
        {
            "q": "Why does promotion copy the same image tag to prod instead of building a fresh image for prod?",
            "options": [
                "GHCR allows only one push per version",
                "Prod then runs exactly the bytes that were tested in dev",
                "Building twice would cost extra GitHub Actions minutes only",
                "Argo CD cannot deploy images built from a branch",
            ],
            "answer": 1,
            "why": "Build once, deploy many: a rebuild could pick up new dependencies and ship something nobody tested.",
            "from": "Part 4",
        },
        {
            "q": "Argo CD synced a new GREETING into hello-config, but curl still returns the old greeting. Why?",
            "options": [
                "Argo CD has not pruned the old ConfigMap yet",
                "The ConfigMap needs a sync wave of -1",
                "The Pods read env variables only at start, so they need a restart",
                "The Service still points at the old ReplicaSet",
            ],
            "answer": 2,
            "why": "Environment variables from a ConfigMap are read when the container starts; restart the Deployment, or generate a new ConfigMap name.",
            "from": "Part 7",
        },
        {
            "q": "How should a database password for hello-devops reach the cluster in a GitOps setup?",
            "options": [
                "Commit an encrypted SealedSecret that only the cluster can decrypt",
                "Commit a normal Secret, since base64 hides the value",
                "Put it in the ConfigMap, then use a private repo",
                "Type it with kubectl create secret and leave it out of git",
            ],
            "answer": 0,
            "why": "A SealedSecret is safe in git and is decrypted only in the cluster; a hand-made Secret works but drifts outside git.",
        },
        {
            "q": "You want a staging environment between dev and prod in this lab. What is the least you must add?",
            "options": [
                "A second Argo CD install in a staging namespace",
                "A copy of application.yaml for every Kubernetes object",
                "A new branch called staging with its own k8s folder",
                "An overlay folder, a generator entry, and the namespace in the project",
            ],
            "answer": 3,
            "why": "The ApplicationSet makes the app from the new entry, the overlay holds its settings, and the project must allow the namespace.",
        },
        {
            "q": "Which statement about Flux and Argo CD is accurate?",
            "options": [
                "Only Argo CD can deploy Kustomize overlays",
                "Both pull from git and reconcile; Flux has image automation built in",
                "Flux pushes changes from CI into the cluster",
                "Argo CD is a CNCF project, while Flux is not",
            ],
            "answer": 1,
            "why": "Both are graduated CNCF GitOps tools. Flux ships image automation controllers; Argo CD uses the separate Image Updater.",
        },
    ],
}


def main():
    OUT.write_text(json.dumps(PART, indent=1, ensure_ascii=False) + "\n")
    print("wrote", OUT)


if __name__ == "__main__":
    main()
