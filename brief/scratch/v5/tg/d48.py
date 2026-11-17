"""Book-voice rewrite of d48 (GitOps in practice). Writer: tg."""
import json, pathlib

P = pathlib.Path("/home/user/devops-from-zero/content/p11.json")
d = json.loads(P.read_text())
L = next(x for x in d["lessons"] if x["id"] == "d48")

L["goal"] = (
    "By the end you can run hello-devops as dev and prod from one ApplicationSet, promote a tested version from "
    "dev to prod with a pull request, and pick a safe way to keep secrets out of a GitOps repo."
)

L["opening"] = (
    "Picture the restaurant from last time, now with a second room. The owner has opened a small test kitchen "
    "next door, where new dishes are tried on a few regulars before they reach the main dining room. On Tuesday a "
    "new soup is a hit there. On Friday the main kitchen cooks it from memory: a little more salt, a different "
    "stock. The regulars ask why it tastes wrong.\n\n"
    "The trap is easy to fall into, because it really feels like the same soup. Same name, same pot, same cooks. "
    "Last time, a board on the wall and a careful manager kept one room in step with git. That left an open "
    "question: how do you run two rooms from one board, and move a dish from one to the other without it changing "
    "on the way?\n\n"
    "In this lesson, we'll run hello-devops as two copies, try a version in one, and move that exact version to "
    "the other with a reviewed change in git.\n\n"
    "Before we start, make a guess, and keep it in mind."
)

L["guess"]["q"] = (
    "Version 1.2.0 runs well in dev, the test copy of your app. In a GitOps setup, how do you move it to prod, "
    "the copy your users see?"
)
L["guess"]["why"] = (
    "Promotion is a change in git: prod gets the exact version that dev already runs. A rebuild could produce a "
    "slightly different app, a hand edit with kubectl gets undone, and Sync only applies what git already says."
)

plains = {
    "Config repo": "A git repo that holds only the files that describe deployments, kept apart from the app's own code.",
    "Environment": "One running copy of the app with one purpose, such as dev for testing or prod for real users.",
    "Overlay": "A folder that takes the shared deployment files and changes a few settings for one environment.",
    "Promotion": "Moving a tested version on to the next environment; in GitOps, by changing its version in git.",
    "ApplicationSet": "An Argo CD object that writes many Applications from one template and a list of values.",
    "AppProject": "An Argo CD object that limits which repos, namespaces and kinds of objects a group of apps may use.",
    "Sync wave": "A note on an object that sets the order in which Argo CD applies things, lowest number first.",
    "Sealed Secret": "A locked copy of a secret that is safe to put in git, because only a program in the cluster can open it.",
}
for t in L["terms"]:
    t["plain"] = plains[t["term"]]

S = L["sections"]

S[0]["h"] = "Where the deployment files should live"
S[0]["body"] = (
    "Before we add a second room, we have to decide where the board hangs. Right now hello-devops, the tiny web "
    "app that answers every visit with a greeting and a count, keeps everything in one repo. A repo is a folder "
    "that git tracks, with its full history. The app's code sits at the top. The YAML files that tell Kubernetes, "
    "the system that runs your app, what to run sit in `k8s/`.\n\n"
    "Teams pick one of three layouts:\n"
    "- One repo per app, with code and YAML together. This is what you have now.\n"
    "- An app repo for the code, plus a separate config repo that holds only YAML for every environment.\n"
    "- A monorepo: one big repo for many apps, with a folder per app and per environment.\n\n"
    "An environment is one running copy of the app with one purpose, such as a test copy or the live copy. The "
    "first layout keeps the board inside the recipe book; the second gives it a wall of its own.\n\n"
    "The [Argo CD best practices](https://argo-cd.readthedocs.io/en/stable/user-guide/best_practices/) page "
    "recommends the separate config repo. It gives these reasons:\n"
    "- You can change a replica count (how many copies run) without a full CI build (the automatic test and build run from Part 6).\n"
    "- The config history reads like a deploy log, without code commits in between.\n"
    "- One config repo can deploy an app built from several code repos as one unit.\n"
    "- Access can differ: many people may change code, while few may change prod.\n"
    "- CI that commits YAML into the code repo can trigger itself in a loop: its own push starts CI again.\n\n"
    "That last point needs care in GitHub Actions, the CI service you used. Each workflow gets a built-in key called `GITHUB_TOKEN`. A push made with that key "
    "does not start new workflow runs, which stops most loops. A push made with a personal token does start them.\n\n"
    "For one person and a laptop cluster, one repo is fine, and this lesson keeps it. (Go deeper has "
    "one small cost of that choice.)\n\n"
    "The board has a home. Next, we'll make it serve two rooms."
)

S[1]["h"] = "Two rooms from one board: dev, prod and the ApplicationSet"
S[1]["body"] = (
    "The test kitchen has one cook and the main room has four, but they serve the same menu. Software teams "
    "keep the same pair. Dev is where new versions land first, and prod is "
    "what users see. Real teams usually give prod its own cluster, its own group of machines. Here both live in your kind cluster, in the "
    "namespaces `hello-dev` and `hello-prod`, two named areas kept apart from each other.\n\n"
    "On Day 45 you built two Kustomize overlays, `overlays/dev` and `overlays/prod`. Kustomize is a tool that takes "
    "shared YAML and lays small changes on top. Each overlay is one such set of changes over the shared files in "
    "`k8s/`.\n\n"
    "Dev runs one Pod (one running copy of the app) and answers \"Hello from dev!\". Prod runs four, with more "
    "memory and a PodDisruptionBudget, a rule that keeps enough Pods alive during maintenance. Both turn their "
    "Service, the stable address in front of the Pods, into a ClusterIP that works only inside the cluster. So "
    "they do not fight last time's app over NodePort 30080. `kubectl kustomize overlays/prod` prints exactly what prod gets.\n\n"
    "Argo CD, the program from last time that keeps the cluster equal to git, needs one Application per "
    "environment. That is the short file saying which folder to deploy where. You could copy `application.yaml` twice and change three "
    "lines in each copy. That works until someone forgets a line. An ApplicationSet "
    "writes those copies for you. It has two parts:\n"
    "- Generators produce a list of values. The lab uses the list generator with two entries, `env: dev` and `env: prod`.\n"
    "- A template is an ordinary Application with placeholders such as `{{.env}}`. One of Argo CD's own programs fills it in once per entry.\n\n"
    "In the restaurant, the template is a blank board with gaps, and the list says which words go in the gaps for "
    "each room.\n\n"
    "Apply `argocd/applicationset.yaml`, and two Applications appear: `hello-devops-dev` and `hello-devops-prod`. "
    "Add a third entry, and a third app appears. Delete the ApplicationSet, and its Applications go too, along "
    "with everything they deployed.\n\n"
    "Two rooms now run from one board. Next, we'll move a version from one room to the other."
)

S[2]["h"] = "Moving a version from dev to prod with a pull request"
S[2]["body"] = (
    "Back to the soup. The restaurant's fix is simple. The test kitchen writes the exact recipe on a card, and "
    "the head chef signs it. The main kitchen cooks from that card and nothing else. Moving a version that passed "
    "in one environment on to the next is called promotion.\n\n"
    "Two words first. An image is your app packed with everything it needs to run (Part 5). Its tag is the "
    "version label after the colon, such as `1.2.0`. In GitOps, promotion is a small text change in git:\n"
    "1. CI builds `ghcr.io/<you>/hello-devops:1.2.0` once, when you push the tag `v1.2.0` (Day 27).\n"
    "2. A pull request sets the dev overlay to `1.2.0`. You merge it, and Argo CD deploys dev.\n"
    "3. You test dev.\n"
    "4. A second pull request sets the prod overlay to the same `1.2.0`. Someone reviews and merges it, and Argo CD deploys prod.\n\n"
    "A pull request is a proposed change that a teammate reviews. Merging it joins it to the main branch, the "
    "line of history Argo CD watches. It is the head chef's signature.\n\n"
    "The image never gets rebuilt. Prod runs the exact bytes that dev ran, which is the build once, deploy many "
    "idea from Day 23. The pull request gives you a review and a record of who approved it. It also gives you a "
    "clean undo: the Revert button on a merged pull request opens a new one that puts the old tag back.\n\n"
    "**A rebuilt image is a new soup with an old name. Build once, and move that same image.**\n\n"
    "This only works if a tag always means the same image. Never deploy `latest`. It points at different images "
    "over time, so git no longer tells you what runs, and a revert cannot bring the old version back. That breaks "
    "the \"versioned and immutable\" principle from last time.\n\n"
    "A version tag such as `1.2.0` is good. A digest such as `@sha256:...` is stronger. A digest is a fingerprint "
    "worked out from the image's contents, so nobody can move it to a different image. The `images` field in a "
    "kustomization accepts a `digest` too.\n\n"
    "Next, we'll let a robot write the new tag, and see why the obvious tool makes a mess."
)

S[3]["h"] = "Getting a new tag into git without a messy diff"
S[3]["body"] = (
    "Argo CD deploys only what git says, so something has to write each new tag into a file. Teams use two "
    "common ways.\n\n"
    "The first is a CI job that edits the file and opens a pull request. The classic tool for the edit is "
    "`kustomize edit set image`, run inside an overlay folder. It works, but it rewrites the whole file in its own "
    "style. On the lab's prod overlay it changed 80 lines to set one tag, because it drops comments at line ends "
    "and re-indents lists. Picture a reviewer hunting for one changed word on a page that someone retyped from "
    "scratch.\n\n"
    "So the lab's `bump-image.yml` workflow uses `yq`, a command line tool for YAML, which changes only the fields "
    "you name. You give the workflow an environment and a version, and it:\n"
    "1. Checks that the version looks like `1.2.0`.\n"
    "2. Sets `newName` and `newTag` of the `hello-devops` image in that environment's overlay.\n"
    "3. Pushes a branch and opens a pull request with the `gh` CLI, GitHub's command line tool.\n\n"
    "New personal repos do not let workflows open pull requests. You allow it once, under Settings, Actions, "
    "General, Workflow permissions.\n\n"
    "The second way is [Argo CD Image Updater](https://github.com/argoproj-labs/argocd-image-updater), a separate "
    "add-on. It watches your registry, the online store that holds your images. When a version that matches your "
    "rule appears, it writes the new tag for you. You configure it with its own custom resource (a new kind of "
    "Kubernetes object), `ImageUpdater`. The lab's optional `argocd/image-updater.yaml` is one.\n\n"
    "With the `git` write-back method, Image Updater commits straight to the branch, with no pull request and no "
    "signature. Its README says it is under active development and not yet recommended for critical production "
    "workloads.\n\n"
    "My advice: start with the CI pull request for every environment. If the dev pull requests turn into "
    "busywork, let Image Updater handle dev, and keep prod on pull requests.\n\n"
    "New versions now reach git cleanly. Next, we'll control the order in which one sync applies things."
)

S[4]["h"] = "Putting things in order: sync waves and hooks"
S[4]["body"] = (
    "A kitchen does not cook everything at once. The stock goes on first, the sauce waits for the stock, and "
    "someone tastes the dish before it leaves. A sync, Argo CD's act of applying git to the cluster, has "
    "the same needs. Argo CD already applies Namespaces first, then other built-in kinds, then custom "
    "resources. Sometimes you need more control. Redis, the small database that counts the "
    "visits, should be ready before the app starts. Or a database migration, a script that changes how stored "
    "data is laid out, must finish before new code arrives.\n\n"
    "A sync wave is an annotation on any object: `argocd.argoproj.io/sync-wave: \"-1\"`. An annotation is a note "
    "on an object that tools can read. Argo CD applies the lowest wave first and waits until it is in sync and "
    "healthy before it starts the next. Objects without the annotation are in wave 0, and negative numbers are "
    "allowed.\n\n"
    "A hook is an object that runs at a set point of the sync. It is usually a Job: an object that runs a Pod "
    "until its command finishes, instead of keeping it running. You mark it with the annotation "
    "`argocd.argoproj.io/hook`:\n"
    "- `PreSync` runs before anything is applied. If it fails, the sync stops. Use it for a database migration.\n"
    "- `Sync` runs together with the normal objects.\n"
    "- `PostSync` runs after everything is applied and Healthy. Use it for a smoke test.\n"
    "- `SyncFail` runs when the sync fails, for clean-up or an alert.\n\n"
    "A smoke test is a quick check that the app answers at all: tasting the soup. The lab's "
    "`gitops/smoke-test.yaml` is a PostSync hook. It calls `/healthz`, the app's \"are you alive?\" address, once "
    "with curl, a tool that fetches a web address. If curl gets an error, Argo CD marks the sync as failed, and "
    "you see it in the web page. A second annotation, `argocd.argoproj.io/hook-delete-policy`, decides when Argo "
    "CD deletes the finished Job.\n\n"
    "One catch: hooks do not run during a selective sync, when you sync only some of an app's objects. Sync the "
    "whole app when you want the hooks.\n\n"
    "Next comes the one kind of file that must never sit in git as plain text."
)

S[5]["h"] = "Keeping secrets out of a GitOps repo"
S[5]["body"] = (
    "Every restaurant has a safe, and nobody writes its code on the board that every cook and driver can read. A "
    "GitOps repo has the same problem. Anyone with access to the repo can read everything in it, and git keeps "
    "every old version.\n\n"
    "A plain Kubernetes Secret, the object that holds passwords and keys, is only base64 encoded (Day 42). Base64 "
    "writes any data as plain letters, and anyone can turn it back. So committing a Secret is the same as "
    "committing the password.\n\n"
    "Three tools solve this. The first uses a key pair: a public key that can only lock, and a matching private "
    "key that is the only way to open the lock again.\n"
    "- Sealed Secrets: you encrypt a Secret on your laptop with `kubeseal` and the cluster's public key, then commit the result, a SealedSecret. Only the controller in that cluster holds the private key that turns it back into a Secret.\n"
    "- External Secrets Operator: git holds only a pointer, an ExternalSecret that names an entry in a store such as AWS Secrets Manager or Vault. The operator copies the value into a Secret in the cluster.\n"
    "- SOPS: encrypts the values inside a YAML file with a key from age (a small encryption tool) or a cloud key service. The keys of the file stay readable; the values do not.\n\n"
    "Argo CD's [secret management](https://argo-cd.readthedocs.io/en/stable/operator-manual/secret-management/) "
    "page strongly recommends the styles where the Secret is created in the destination cluster, such as the "
    "first two. Then Argo CD never sees the value. It cautions against plugins that inject secrets while Argo CD "
    "renders the YAML, because those values then sit in Argo CD's Redis cache in plain text.\n\n"
    "**A password in git is no longer a secret. Commit only locked secrets, or pointers to them.**\n\n"
    "hello-devops has no real secrets yet, so the lab needs none of this today. Day 64 goes deeper into secrets, "
    "access and policy.\n\n"
    "The last question is who may change which board, and whether Argo CD is the only tool for the job."
)

S[6]["h"] = "Who may change what, and the other GitOps tool, Flux"
S[6]["body"] = (
    "The manager of the test kitchen may change the test kitchen's board, but not the main room's. Argo CD draws "
    "those lines with projects. Everything last time used the `default` project, which allows any repo, any "
    "cluster, any namespace and any kind of object. An AppProject narrows that down for a group of apps. The "
    "lab's `argocd/project.yaml` allows:\n"
    "- One source repo: yours.\n"
    "- Three namespaces in the local cluster: `hello`, `hello-dev` and `hello-prod`.\n"
    "- No cluster-wide objects except Namespaces.\n\n"
    "Point an app in this project at another repo, or at `kube-system`, where Kubernetes keeps its own parts, and "
    "Argo CD refuses to sync it. Projects also hold roles: the lab's `viewer` role may look at the apps and read "
    "logs, nothing more.\n\n"
    "Who may do what in the web page and CLI is set by Argo CD's own RBAC, rules that give each role its "
    "permissions. It is separate from Kubernetes RBAC (Day 46). A fresh install has one user, `admin`, who may "
    "do everything. Teams connect single sign-on, so people log in with their work account, and map groups to "
    "roles such as the built-in `role:readonly`.\n\n"
    "[Flux](https://github.com/fluxcd/flux2) is the other big GitOps tool. Like Argo CD it is a graduated CNCF "
    "project, which means the foundation behind Kubernetes rates it as mature. The ideas from these two lessons "
    "carry over. The differences are mostly about style:\n"
    "- Flux is a set of small controllers that you drive with YAML and the `flux` CLI. Its core has no web UI; the separate [Flux Operator](https://fluxoperator.dev/web-ui/) adds one.\n"
    "- Flux usually runs inside every cluster it manages, while one Argo CD often manages many clusters from one place.\n"
    "- Flux ships its own image automation controllers and can decrypt SOPS files itself; Argo CD uses Image Updater and plugins.\n\n"
    "Choose Argo CD when people want a web page to see and sync apps. Choose Flux when the team wants everything "
    "as YAML and no central server.\n\n"
    "Both tools stop at the same place. They make sure the cluster runs what git says. A Synced, "
    "Healthy app can still be slow, or fail for one user in ten. Seeing that needs a different set of tools, and "
    "the next part starts building them."
)

L["aside"] = {
    "title": "What is \"app of apps\", which so many blog posts use?",
    "body": (
        "It is one parent Application whose folder holds only other Application files. Argo CD deploys the parent, "
        "and the parent deploys the children. It came before ApplicationSets, and it still works. The Argo CD docs "
        "recommend ApplicationSets for most cases. They call app of apps an admin-only tool, because anyone who can "
        "push to that folder can create apps in any project."
    ),
    "after": 1,
}

# The soup story carries the analogy, and section 3 carries the `latest` mistake (lead's notes).
L.pop("analogy", None)
L.pop("mistake", None)
L["real_world"] = (
    "Picture a payments team with three clusters: dev, staging and prod. One config repo runs them all, with one "
    "ApplicationSet per app that uses the cluster generator. CI opens the dev pull request after every release "
    "and merges it once the checks pass. Prod needs a second pull request, approved by someone on the on-call "
    "rotation (the people who answer alerts). A PostSync smoke test fails the sync if checkout stops answering."
)

W = L["worked"]["steps"]
W[0]["say"] = (
    "Ask git, not the cluster, what each environment should run. `kubectl kustomize` builds an overlay's final "
    "YAML on your laptop and never touches the cluster. Dev already runs 1.1.0, and prod still runs 1.0.0. Both "
    "are local images in your kind cluster."
)
W[1]["say"] = (
    "Try `kustomize edit set image` first. It sets the tag, but look at the size of the change: it rewrote the "
    "whole file. Comments at line ends are gone, and lists are re-indented. A reviewer would have to hunt for the "
    "one line that matters, so throw that edit away."
)
W[2]["say"] = (
    "`yq` changes only the field you name and keeps everything else, comments included. Now the diff is one "
    "line, and the review takes seconds. (`-U1` shows one line of context instead of three.)"
)
W[3]["say"] = (
    "Check the result before you commit: build prod's YAML again and confirm the new tag. This catches a typo "
    "before Argo CD ever sees it."
)
W[4]["say"] = (
    "Ship it like any other change: a branch, a commit and a pull request. Argo CD watches only `main`, so "
    "nothing deploys until someone reviews and merges."
)
W[5]["say"] = (
    "Within about three minutes Argo CD syncs `hello-devops-prod`, and the rollout replaces the four prod Pods one "
    "at a time. Dev was not touched, because its folder did not change. If prod misbehaves, press Revert on the "
    "merged pull request and merge the revert: Argo CD puts 1.0.0 back."
)

T = L["task"]
T["steps"] = [
    "Add `argocd/project.yaml` and `argocd/applicationset.yaml` with your GitHub user name. Commit, push, and apply both. Last time's app can stay, because the overlays use ClusterIP Services.",
    "Check that `hello-devops-dev` and `hello-devops-prod` appear and both turn Synced and Healthy. Dev uses the local image `hello-devops:1.1.0`; if kind lacks it, run `kind load docker-image hello-devops:1.1.0 --name devops`.",
    "Port-forward to the dev and the prod Service in turn, and check with curl that each one greets you differently.",
    "Add `.github/workflows/bump-image.yml`, push it, and allow workflows to create pull requests in the repo settings.",
    "Push a new release tag, for example `v1.2.0`, and wait for `release.yml` to finish. Make the package public in GHCR (GitHub's image store), so kind can pull it without a password.",
    "Run the bump workflow for dev with version `1.2.0`. Read the pull request: it should change two lines in `overlays/dev/kustomization.yaml`. Merge it.",
    "Confirm that dev now runs `ghcr.io/<you>/hello-devops:1.2.0` while prod still runs its old tag.",
    "Promote: run the workflow again for prod with the same version, merge, and confirm that both environments match.",
    "Optional: add the smoke-test hook to the dev overlay, then break its URL and watch the dev sync fail.",
]
T["hints"] = [
    "Checks may not start on their own for a pull request that the workflow opened with `GITHUB_TOKEN`; GitHub does this to stop workflow loops. If the merge box asks you to approve the workflow runs, approve them.",
    "ImagePullBackOff after a bump usually means the GHCR package is still private, or the tag does not exist. `kubectl -n hello-dev describe pod` names the exact image it tried.",
    "Unsure what a bump will change? Save the output of `kubectl kustomize overlays/dev` to a file before and after, then compare the two with `diff`.",
]
T["done_when"] = (
    "You are done when the jsonpath command from the Commands list prints the same `ghcr.io/.../hello-devops:1.2.0` "
    "image for `hello-dev` and `hello-prod`, and both apps are Synced and Healthy."
)

L["explain_back"]["prompt"] = (
    "Explain to a teammate, in 3 to 4 sentences, how version 1.3.0 travels from a git tag to prod in this setup. "
    "Mention who builds the image, what changes in git, and what Argo CD does."
)
L["explain_back"]["answer"] = (
    "Pushing the tag v1.3.0 starts release.yml, which builds the image once and pushes it to GHCR as 1.3.0. A "
    "workflow then opens a pull request that sets the dev overlay to 1.3.0. After the merge, Argo CD sees the "
    "commit and deploys dev. When dev looks good, a second pull request copies the same tag into the prod overlay, "
    "someone reviews it, and Argo CD deploys prod. If prod breaks, reverting that pull request puts the old tag back."
)

L["recap"] = [
    "Deployment YAML lives in git, in the app repo or in a separate config repo with cleaner history and access.",
    "Each environment gets one overlay and one Application; an ApplicationSet writes the Applications from one template.",
    "Promotion is a pull request that copies a tested, fixed tag to the next overlay. Never deploy latest.",
    "CI writes the new tag with a small edit (yq rather than kustomize edit set image) and opens a pull request; Image Updater can do it for dev.",
    "Sync waves order objects, hooks run Jobs before or after a sync, and secrets stay out of git as Sealed or External Secrets.",
    "AppProjects limit what apps may touch, and Flux is the main alternative. Neither tool can tell you whether users are happy.",
]

C = L["check"]
C[0]["q"] = (
    "You add `env: staging, namespace: hello-staging` to the list generator and create `overlays/staging`. The new "
    "app appears but never syncs. Why?"
)
C[0]["why"] = "The AppProject lists the places its apps may deploy to, so you also have to add hello-staging to project.yaml."
C[1]["q"] = "Image Updater runs with the lab's settings and finds a new version 1.4.0. What appears in your repo?"
C[1]["why"] = "With git write-back and the kustomization target, it commits straight to the branch Argo CD watches, with no pull request."
C[2]["q"] = (
    "A Job marked `argocd.argoproj.io/hook: PreSync` runs a database migration and fails. What happens to the new "
    "app version?"
)
C[2]["why"] = "A failed PreSync hook stops the whole sync, so new code never meets data in the old layout."

I = L["interview"]
I[0]["a"] = (
    "CI builds the image once and tags it with a version, never latest. Each environment has its own folder, for "
    "example a Kustomize overlay. Promotion is a pull request that copies the tested tag or digest from one folder "
    "to the next. The review is the approval, and the merge is the deploy, because Argo CD or Flux syncs the "
    "change. Rolling back is a revert of that pull request."
)
I[1]["a"] = (
    "I never commit plain Secrets, because base64 is not encryption and git keeps history forever. One option is "
    "to commit encrypted SealedSecrets that only the controller in the cluster can decrypt. The other is to commit "
    "ExternalSecret references and let the External Secrets Operator fetch the values from a store such as Vault "
    "or AWS Secrets Manager. Argo CD recommends these styles, where the Secret is made in the destination cluster. "
    "I avoid plugins that inject secrets while Argo CD renders manifests, because those values land in its cache."
)
I[2]["a"] = (
    "Both are graduated CNCF projects that pull from git and reconcile, so the core idea is the same. I would pick "
    "Argo CD when people want a web UI to see app health and sync by hand, or when one central install should "
    "manage many clusters. I would pick Flux when the team prefers everything as YAML and the CLI, runs one set of "
    "controllers per cluster, and wants image automation and SOPS decryption built in. Either way, the repo layout "
    "and promotion flow look much the same."
)

L["deeper"]["body"] = (
    "Your setup is one cluster with two namespaces. A company with fifty clusters uses the same ideas, only "
    "generated.\n\n"
    "Start with the generator. The list generator is only one of several; others read their list from folders in "
    "a git repo, from the clusters Argo CD knows, or from open pull requests. The cluster generator makes one "
    "Application per cluster. It can filter by labels on those clusters, such as `env: prod` or `region: eu`. "
    "Register a new cluster with the right labels, and every matching ApplicationSet deploys to it. The [Argo CD "
    "docs on cluster bootstrapping](https://argo-cd.readthedocs.io/en/stable/operator-manual/cluster-bootstrapping/) "
    "recommend exactly this for new clusters. The matrix generator combines two generators, for example every "
    "folder under `apps/` times every cluster labelled `env: dev`.\n\n"
    "Then decide where Argo CD itself runs:\n"
    "- Hub and spoke: one Argo CD in a management cluster deploys to all the others. You get one UI and one place for access rules. If the hub is down, nothing new deploys, though running apps keep running.\n"
    "- One Argo CD per cluster: no single point of failure, but more installs to upgrade. This is also the usual Flux model.\n\n"
    "Changing fifty clusters at once is risky. ApplicationSet Progressive Syncs, a Beta feature, update the "
    "generated apps in steps. For example, dev clusters go first, then a few prod clusters, then the rest, and "
    "each step waits until the previous one is healthy.\n\n"
    "Promotion itself can be automated too. Tools such as [Kargo](https://github.com/akuity/kargo) and [GitOps "
    "Promoter](https://github.com/argoproj-labs/gitops-promoter) run the promotion steps for you: they open the "
    "pull requests, wait for checks, and move a version from stage to stage.\n\n"
    "Next, the rendered manifests pattern. With overlays and charts, a one-line change in a base can change the "
    "YAML of every environment, and the pull request does not show it. The Source Hydrator (Beta since Argo CD "
    "3.5, off by default) renders each environment, commits the plain YAML to a separate branch, and syncs from "
    "there. Reviewers then read the exact YAML that will run, and `git diff` between two commits shows exactly "
    "what changed in prod.\n\n"
    "You can get a cheap version of this today. In a pull request check, run `kubectl kustomize` for each overlay "
    "on both the main branch and the pull request branch, and post the diff as a comment. A reviewer who sees "
    "\"prod: replicas 3 to 6\" catches mistakes that \"k8s/deployment.yaml: one line changed\" hides.\n\n"
    "Why does deleting an ApplicationSet remove so much? The controller marks each Application as owned by the "
    "set. It also adds the finalizer from last time's `application.yaml`. A finalizer is a note that makes "
    "Kubernetes run a clean-up step before it removes an object, and this one deletes an app's objects together "
    "with the app.\n\n"
    "Keeping one repo has a small cost: a commit that changes only `overlays/` still runs `ci.yml` on main. If "
    "that bothers you, add `overlays/**` to the `paths-ignore` list of its push trigger, the list of folders "
    "whose changes should not start it.\n\n"
    "One small timing detail: between sync waves, Argo CD pauses for 2 seconds.\n\n"
    "Last, two access defaults changed in Argo CD 3.x, and older guides get them wrong. The right to update or "
    "delete an Application no longer covers the objects inside it. And reading Pod logs needs its own `logs` "
    "permission."
)

L["closing"] = (
    "We started with a soup that changed on its way from the test kitchen to the main room. Now one board template "
    "serves both rooms, and a dish moves only as a signed card: a pull request that copies the exact tag dev "
    "already ran. In your lab, open `overlays/prod/kustomization.yaml` and check that its tag is a real version, "
    "never `latest`.\n\n"
    "Next, we'll stop asking whether the cluster runs what git says, and start asking a harder question: is the "
    "app actually working well for the people who use it?"
)

P.write_text(json.dumps(d, indent=1, ensure_ascii=False) + "\n")
print("d48 written")
