"""Book-voice rewrite of Part 11's own fields. Writer: tg."""
import json, pathlib

P = pathlib.Path("/home/user/devops-from-zero/content/p11.json")
d = json.loads(P.read_text())

d["intro"] = (
    "In Part 10 you deployed hello-devops to Kubernetes by typing commands yourself. In this part a program called "
    "Argo CD takes over that job: git holds the plan, and Argo CD keeps the cluster equal to it, all day long. "
    "First you install it and watch it undo a hand edit and roll back a bad release. Then you run the app as a "
    "test copy and a live copy, and move a version between them with a pull request. Along the way you see how "
    "teams handle new versions, secrets and access."
)

d["recap"] = [
    "GitOps: git holds what should run, and a program in the cluster pulls it and keeps the cluster equal to it.",
    "Pull deploys keep cluster keys out of CI, and every deploy becomes a commit you can review and revert.",
    "Argo CD 3.x installs with server-side apply and marks the objects it owns with an annotation.",
    "Sync status (does it match git?) and health (does it work?) are two separate signals.",
    "Self-heal and prune are off by default. Tell Argo CD to ignore fields that another controller owns.",
    "Roll back with git revert, or the Revert button on the pull request.",
    "Each environment gets one overlay and one Application, and an ApplicationSet writes the Applications.",
    "Promotion copies a tested, fixed image tag to the next environment through a pull request.",
    "Secrets stay out of git with Sealed Secrets, External Secrets or SOPS; AppProjects and roles limit who deploys where.",
]

cards = [
    ("What are the four OpenGitOps principles?", "Declarative; versioned and immutable; pulled automatically; continuously reconciled."),
    ("Push deploy or pull deploy: which one needs a cluster key in CI?", "Push. In a pull deploy, a program inside the cluster fetches from git and applies."),
    ("Why does installing Argo CD 3.x need kubectl apply --server-side?", "The ApplicationSet definition is too big for the annotation that normal (client-side) apply writes."),
    ("Sync status or health status: which one asks \"does it work?\"", "Health. Sync status asks whether the cluster matches git."),
    ("What does selfHeal do, and is it on by default?", "It undoes changes made in the cluster but not in git. It is off by default."),
    ("What does prune do, and is it on by default?", "It deletes objects you removed from git. It is off by default."),
    ("How does Argo CD 3.x remember which app owns an object?", "With the annotation argocd.argoproj.io/tracking-id on that object."),
    ("How often does Argo CD check git by default?", "About every 3 minutes (120 s plus up to 60 s of random delay). A webhook makes it immediate."),
    ("Why does the lab ignore /spec/replicas?", "So Argo CD and the autoscaler do not fight over the number of copies."),
    ("How do you roll back an app that Argo CD syncs automatically?", "Revert the commit or pull request in git. Argo CD then deploys the old state."),
    ("What is an ApplicationSet?", "A template plus generators that write many Applications, for example one per environment."),
    ("What is promotion in GitOps?", "A pull request that copies a tested image tag from one environment's folder to the next."),
    ("Why never deploy the latest tag with GitOps?", "Git does not change when the image does, so you cannot see or revert what runs."),
    ("What does kustomize edit set image do, and what is the catch?", "It sets an image name and tag in the kustomization.yaml of the current folder, but rewrites the whole file and drops comments at line ends."),
    ("When does a PostSync hook run?", "After all objects are applied and Healthy. A quick smoke test is a typical use."),
    ("Which secret styles does Argo CD recommend?", "Ones that create the Secret inside the cluster, such as Sealed Secrets or External Secrets Operator."),
    ("What does an AppProject limit?", "Which repos, clusters, namespaces and kinds of objects its apps may use."),
    ("What is the main style difference between Flux and Argo CD?", "Flux: small controllers in each cluster, driven by YAML and its CLI. Argo CD: often one central server with a web UI."),
]
assert len(cards) == len(d["flashcards"])
for f, (front, back) in zip(d["flashcards"], cards):
    f["front"], f["back"] = front, back

whys = [
    "The official guide to installing Argo CD and deploying a first app, kept current for 3.x.",
    "The four GitOps principles on one short page, written by the CNCF working group.",
    "A clear, visual tour of Argo CD; its install command is older than the 3.x server-side flag.",
    "A conversation that puts Argo CD and Flux side by side and explains why GitOps exists.",
    "A short demo of the parent-app pattern that you will meet in many company repos.",
    "Every generator, with examples you can adapt for more environments or clusters.",
    "Short and practical advice: config repos, replicas and autoscalers, and pinning shared files.",
    "Why the project prefers secret tools that work inside the cluster over plugins that work at render time.",
    "The add-on that writes new image tags into git for you, set up with its ImageUpdater resource.",
    "The other graduated GitOps project, with links to its guides on image updates and SOPS.",
    "A free course with hosted labs; it was built on Argo CD 2.x, but the GitOps ideas still hold.",
]
assert len(whys) == len(d["resources"])
for r, w in zip(d["resources"], whys):
    r["why"] = w

quiz = [
    ("Automated sync is on and selfHeal is off. A teammate edits the live ConfigMap by hand. What do you see in Argo CD?",
     "Without self-heal, a change in the cluster does not start a sync. Argo CD reports the drift, and the edit stays until the next commit is synced."),
    ("Which Argo CD part turns your Kustomize folder into plain YAML?",
     "The repo server copies the repo and builds the YAML from Kustomize or Helm; the controller then compares and applies it."),
    ("You follow an old video and run plain `kubectl apply -n argocd -f install.yaml`. It fails on the ApplicationSet definition. What is the fix?",
     "That definition is too big for the annotation that client-side apply writes, and server-side apply does not write it."),
    ("After a tag change in git, your app stays Synced and Progressing for many minutes. What is the most likely cause?",
     "Synced means the cluster has what git says. A rollout that never finishes points at the new Pods themselves."),
    ("Why does promotion copy the same image tag to prod instead of building a fresh image for prod?",
     "Build once, deploy many: a rebuild could pick up new parts and ship something nobody tested."),
    ("Argo CD synced a new GREETING into hello-config, but curl still returns the old greeting. Why?",
     "A container reads settings from a ConfigMap only when it starts. Restart the Deployment, or give the ConfigMap a new name."),
    ("How should a database password for hello-devops reach the cluster in a GitOps setup?",
     "A SealedSecret is safe in git and is unlocked only in the cluster. A Secret made by hand works, but it lives outside git and drifts."),
    ("You want a staging environment between dev and prod in this lab. What is the least you must add?",
     "The ApplicationSet makes the app from the new entry, the overlay holds its settings, and the project must allow the namespace."),
    ("Which statement about Flux and Argo CD is accurate?",
     "Both are graduated CNCF GitOps tools. Flux ships its own image automation; Argo CD uses the separate Image Updater."),
]
assert len(quiz) == len(d["quiz"])
for q, (qq, why) in zip(d["quiz"], quiz):
    q["q"], q["why"] = qq, why

P.write_text(json.dumps(d, indent=1, ensure_ascii=False) + "\n")
print("p11 part fields written")
