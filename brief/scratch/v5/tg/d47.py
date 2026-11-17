"""Book-voice rewrite of d47 (GitOps with Argo CD). Writer: tg."""
import json, pathlib

P = pathlib.Path("/home/user/devops-from-zero/content/p11.json")
d = json.loads(P.read_text())
L = next(x for x in d["lessons"] if x["id"] == "d47")

L["goal"] = "By the end you can install Argo CD on your kind cluster, let it deploy hello-devops from your GitHub repo, and fix drift and roll back using only git."

L["opening"] = (
    "Picture a small restaurant on a busy Friday night. On the kitchen wall hangs a board with tonight's plan: "
    "which dishes are on, how many cooks work the line, which tables are open. Around seven, a waiter joins two "
    "tables for a big group. A cook takes a dish off because the fish ran out. Nobody writes any of it on the board. "
    "By nine, the board and the room tell two different stories, and the next shift believes the board.\n\n"
    "It is an easy mess to get into. Every change made sense at the time, and writing it down felt like extra work. "
    "Last time, you tracked down broken apps on your cluster and fixed them by typing commands by hand. "
    "That left a quiet question: who keeps the board and the room in step?\n\n"
    "In this lesson, we'll hand that job to a program, watch it undo a hand edit, and roll back a bad release "
    "using nothing but the history of your files.\n\n"
    "Before we start, make a guess, and keep it in mind."
)

L["guess"]["q"] = (
    "A program called Argo CD deploys your app from git, the tool that keeps the history of your files. "
    "It runs with its default settings. A teammate then changes the running app by hand with a quick command. "
    "What happens to that hand edit?"
)
L["guess"]["why"] = (
    "By default Argo CD only reports the difference. Undoing hand edits is a separate setting called self-heal, "
    "and it stays off until you turn it on."
)

plains = {
    "GitOps": "A way of running software where files in git say what should run, and a program keeps the real system matching them.",
    "Desired state": "What you want running, written down as files; in this course, the YAML files in your repo.",
    "Drift": "A difference between what the files say and what really runs, often caused by a change made by hand.",
    "Reconcile": "Compare what runs with what is wanted, then change what runs until the two match.",
    "Argo CD Application": "A short file that tells Argo CD which folder of your repo to deploy, and to which cluster and namespace.",
    "Sync": "Argo CD copying what git says into the cluster, so the two match.",
    "Self-heal": "An Argo CD setting that undoes changes made in the cluster but not in git.",
    "Prune": "An Argo CD setting that removes things from the cluster after you delete them from git.",
}
for t in L["terms"]:
    t["plain"] = plains[t["term"]]

S = L["sections"]

S[0]["h"] = "Why deploying from your own laptop stops working"
S[0]["body"] = (
    "Software has the same problem. Kubernetes is the system that runs your app on a group of machines, "
    "called a cluster, and keeps it running. All through Part 10 you ran hello-devops there. It is the tiny web app "
    "from the lab that answers every visit with a greeting and a count of visits so far.\n\n"
    "You told the cluster what to run with one command from your laptop: `kubectl apply -k k8s`. kubectl is the "
    "command line tool that sends your wishes to Kubernetes. The folder `k8s` holds YAML files, plain text files "
    "that describe what should run. For one person, that is fine: one cook writes the board and cooks the food. "
    "Add a few colleagues, and it breaks in quiet ways:\n"
    "- Someone fixes the app by hand at night and never updates the files.\n"
    "- Two people apply different versions of the files, and the last one wins.\n"
    "- Nobody can say which version of the files is running right now.\n"
    "- Every laptop or pipeline that deploys holds a key that can change the cluster.\n\n"
    "A difference between the files and what really runs is called drift. You met it on Day 33 with Terraform, "
    "the tool that builds servers from code: it noticed a hand change only when you ran `plan` again.\n\n"
    "GitOps closes that gap from the other side. Git is the tool that keeps every saved version of your files. "
    "Each saved version is a commit, and the folder with all that history is a repo. With GitOps, git becomes "
    "the only place where changes happen. A program inside the cluster keeps the cluster equal to git, all the "
    "time. In restaurant terms, git is the board, the cluster is the dining room, "
    "and that program is the floor manager.\n\n"
    "The [OpenGitOps project](https://opengitops.dev/), part of the CNCF (the foundation behind Kubernetes), sums "
    "this up in four principles. The desired state, meaning what you want running, must be:\n"
    "- Declarative: you describe what you want, not the steps to get there.\n"
    "- Versioned and immutable: it is stored with its full history, and old versions never change.\n"
    "- Pulled automatically: software agents fetch it by themselves.\n"
    "- Continuously reconciled: agents keep comparing the real system with it and fix differences.\n\n"
    "The last one should feel familiar. On Day 38 you watched controllers, small programs in the cluster, do "
    "exactly that. GitOps runs the same loop one level up, with git as the thing you asked for.\n\n"
    "**A change that is not in git did not happen. Put every change in git.**\n\n"
    "So who carries a change from git into the cluster? There are two answers."
)

S[1]["h"] = "Who carries the change: push deploys and pull deploys"
S[1]["body"] = (
    "A restaurant owner could phone in each change from home, or a manager could read the board every few "
    "minutes. Deploys come in the same two styles.\n\n"
    "In a push deploy, something outside the cluster sends the change in. Usually that is a CI pipeline, the "
    "automatic build and test steps from Part 6 that run every time you push code to GitHub. The pipeline ends "
    "with `kubectl apply`, so the pipeline holds a "
    "key that can write to the cluster. Any workflow that can read that secret can change production, the real "
    "system your users depend on. And if someone edits the cluster after the pipeline ends, nothing notices.\n\n"
    "In a pull deploy, an agent (a program that does its job on its own) runs inside the cluster. It reads git "
    "and applies what it finds. CI builds the image (the packaged app, from Part 5) and changes a file "
    "in git, and that is all CI does. The pull model gives you:\n"
    "- No cluster keys in CI, because the agent already lives in the cluster.\n"
    "- A deploy log at no extra cost: `git log` shows who changed what, and when.\n"
    "- Review before deploy, because every change can be a pull request (Part 6), a change that a teammate approves first.\n"
    "- Rollback with `git revert`.\n"
    "- Drift detection all day, even when nobody is deploying.\n\n"
    "The price of the pull model is one more system to learn and keep upgraded. On your laptop it is "
    "seven extra Pods. A Pod is the smallest thing Kubernetes runs: one or more containers that live together. "
    "For any cluster that more than one person touches, I think the pull model is worth that price.\n\n"
    "CI still tests the code and builds the image. GitOps replaces only the last step, the one that touches "
    "the cluster.\n\n"
    "Our agent is Argo CD. Next, we'll see what it is made of."
)

S[2]["h"] = "What Argo CD is made of"
S[2]["body"] = (
    "Argo CD, a CNCF project, is our floor manager, and like a real manager it has a small team. It runs as a set of Pods in its own namespace, `argocd`. A namespace "
    "is a named area inside a cluster that keeps one group of things apart from the rest. After the install you "
    "will see seven Pods:\n"
    "- `argocd-server`: Argo CD's own API server (a program that answers requests), behind the web page and the `argocd` tool.\n"
    "- `argocd-repo-server`: copies your repo and turns a folder into plain YAML.\n"
    "- `argocd-application-controller`: compares the cluster with that YAML and applies the difference.\n"
    "- `argocd-applicationset-controller`: makes many Applications from one template (Day 48).\n"
    "- `argocd-redis`: a cache, a fast short-term memory for rendered YAML and app state.\n"
    "- `argocd-dex-server`: connects Argo CD to single sign-on, so people log in with GitHub or Google accounts.\n"
    "- `argocd-notifications-controller`: sends messages, for example to the chat app Slack when a sync fails.\n\n"
    "The repo server also understands Kustomize and Helm, two tools that build YAML from smaller pieces (Argo CD "
    "3.5 ships with Helm 4). The application controller runs the reconcile loop. One round goes like this:\n"
    "1. The controller asks the repo server for the YAML of the newest commit on the branch (a named line of commits, usually `main`).\n"
    "2. The repo server fetches the repo and renders the folder into plain YAML.\n"
    "3. The controller compares that YAML with the live objects. It watches them through the Kubernetes API server, the front desk for every request to the cluster.\n"
    "4. It applies the difference, if the sync settings allow it, and writes the result into the Application's status.\n\n"
    "You tell Argo CD what to deploy with an "
    "Application. It is a custom resource: a new kind of object that a tool adds to Kubernetes. It has three main parts:\n"
    "- A source: the repo URL, the branch (`targetRevision`) and the folder (`path`).\n"
    "- A destination: which cluster and which namespace.\n"
    "- A project: rules about what this app may touch. Everything starts in the project called `default`.\n\n"
    "How does Argo CD know which objects in the cluster are its own? Since version 3.0 it writes an annotation, "
    "a note that Kubernetes stores but does not act on, on every object it applies: "
    "`argocd.argoproj.io/tracking-id`. Older versions used a label (a similar tag), and many blog posts still "
    "say so. The worked example shows one.\n\n"
    "Next, we'll install the whole team on your laptop."
)

S[3]["h"] = "Installing Argo CD on kind, and the flag old videos miss"
S[3]["body"] = (
    "kind, from Part 10, runs a small Kubernetes cluster inside Docker on your laptop. Installing Argo CD there "
    "means applying one long YAML file (see the Commands list). Two of its "
    "flags look odd, and older videos leave them out. Their plain `kubectl apply -n argocd -f install.yaml` fails "
    "on Argo CD 3.x with an error about annotations that are too long.\n\n"
    "Here is why. Normal apply, called client-side apply, stores a "
    "full copy of each object in an annotation, so it can compare next time. Annotations on one object are "
    "limited to 262 KB in total. One of Argo CD's custom resource definitions, the one for ApplicationSets, is too "
    "big for that. A custom resource definition is the file that teaches Kubernetes a new kind of object.\n\n"
    "The fix is `kubectl apply --server-side`. It lets the API server work out the changes, and it keeps no such "
    "copy. The second flag, `--force-conflicts`, lets the install take over fields that an earlier apply set, "
    "which matters when you upgrade.\n\n"
    "The install URL points at the `stable` branch, which is fine on a laptop. At work you pin a version, with a "
    "tag such as `v3.5.6` in the URL instead of `stable`. A tag is a fixed name for one exact commit. Then every "
    "install gives the same result.\n\n"
    "Argo CD's web page is not reachable from outside the cluster, because its Service, "
    "`argocd-server`, is a ClusterIP (Day 41). A Service gives Pods one stable address, and a ClusterIP address "
    "works only inside the cluster. On a laptop, `kubectl port-forward` is the simplest way in. It opens a port on "
    "your laptop, a numbered door for network traffic, and passes everything through to the Service. Use local "
    "port 8443, because 8080 may still be busy from your Terraform work in Part 8.\n\n"
    "Expect a warning in the browser. The install makes its own certificate (the proof a website shows that it "
    "is who it says it is), and your browser has never heard of a self-signed one.\n\n"
    "Log in as `admin` with the password from `argocd admin initial-password -n argocd`. Out of the box, `admin` is "
    "the only user, and it may do everything; Day 48 shows how teams give people narrower roles. Install the "
    "`argocd` CLI (a tool you type commands into) with Homebrew, the Mac's installer for such tools, and log it in "
    "through the same port-forward.\n\n"
    "Next, we'll read the two status words that the web page shows for each app."
)

S[4]["h"] = "Two statuses: does it match, and does it work"
S[4]["body"] = (
    "The floor manager asks two things about each table: does it match the board, and are the guests happy? "
    "If the board is wrong, a table can match it and still have unhappy guests. Every Argo CD Application shows the same two statuses, and beginners often read them "
    "as one.\n\n"
    "Sync status answers one question: does the cluster match git?\n"
    "- `Synced`: every object Argo CD manages matches the YAML in git.\n"
    "- `OutOfSync`: at least one object differs, is missing, or should be gone.\n\n"
    "Health answers a different question: does it work? Our example is a Deployment, the Kubernetes object that "
    "keeps a set number of copies of your app running. Each copy is called a replica.\n"
    "- `Healthy`: for a Deployment, all replicas are updated and available.\n"
    "- `Progressing`: not healthy yet but still moving, such as a rollout (a switch to a new version) in progress.\n"
    "- `Degraded`: failed, for example a rollout that ran past its deadline.\n"
    "- `Missing`: in git, but not in the cluster yet.\n"
    "- `Suspended` and `Unknown` show up less often.\n\n"
    "The two are independent. Push a typo in an image tag, the version name of the image, and the app is Synced "
    "but not Healthy. The cluster has exactly what git says, but the new Pods cannot pull an image that does not "
    "exist. Make a hand edit to a label, and the app is OutOfSync but still Healthy. The health of a whole app is "
    "the worst health of its parts.\n\n"
    "How fast does Argo CD see a new commit? By default it checks git about every three minutes: 120 seconds plus "
    "a random delay of up to 60 seconds, so that many apps do not all ask at once. Press Refresh in the web page, or run `argocd app get hello-devops --refresh`, to check now.\n\n"
    "Teams whose Argo CD has a public address add a git webhook, a message GitHub sends the moment you push. "
    "GitHub cannot reach your kind cluster, so here you wait or press Refresh. Changes inside the cluster are different. The "
    "controller watches the objects it manages, so it sees a `kubectl edit` (a change typed straight into a live "
    "object) within seconds.\n\n"
    "Seeing a difference is only half the job. Next, we'll decide what Argo CD should do about it."
)

S[5]["h"] = "Letting Argo CD act: automated sync, self-heal and prune"
S[5]["body"] = (
    "Out of the box, Argo CD is a manager who only takes notes. You press Sync, "
    "in the web page or with `argocd app sync`, and it applies git. Automated sync applies new commits by itself. "
    "Two more switches decide how strict it is:\n"
    "- `selfHeal: true` undoes changes made in the cluster but not in git, such as a `kubectl edit`.\n"
    "- `prune: true` deletes objects you removed from git. Without it, they stay, and Argo CD only marks them for pruning.\n\n"
    "Both are off by default, a careful choice for a tool that can delete things. Remember your guess? With the "
    "default settings, the hand edit stays, and the app only shows OutOfSync. Automated sync alone does not change that. The lab's `argocd/application.yaml` turns both switches on.\n\n"
    "Self-heal gets tricky because Argo CD is not the only controller that changes your objects. On Day 43 you "
    "added a HorizontalPodAutoscaler (HPA). It is a controller that adds replicas when the app is busy and removes "
    "them when it is quiet. Under load, the HPA sets 5 replicas where git says 3. Argo CD sees the difference and, "
    "with self-heal on, sets it back. The HPA raises it again. They fight for as long as the load lasts. In the "
    "restaurant, it is the manager sending home the extra waiters that the head waiter just called in for a rush.\n\n"
    "There are two ways out:\n"
    "- Leave `replicas` out of the Deployment in git, so there is nothing to compare. The [Argo CD best practices](https://argo-cd.readthedocs.io/en/stable/user-guide/best_practices/) page suggests this.\n"
    "- Tell Argo CD to ignore that one field. The lab does this with `ignoreDifferences` on `/spec/replicas`.\n\n"
    "The sync option `RespectIgnoreDifferences=true` makes a sync leave the field alone too. The lab takes the "
    "second way so that `k8s/deployment.yaml` keeps `replicas: 3`, and `kubectl apply -k k8s` still works without "
    "Argo CD.\n\n"
    "**Two controllers fighting over one field never stop. Give each field one owner.**\n\n"
    "Self-heal protects git from hand edits. But what if the mistake is in git itself? Next, we'll roll back."
)

S[6]["h"] = "Rolling back with git revert"
S[6]["body"] = (
    "Sooner or later, a bad change gets through. With GitOps, a rollback is a commit. You undo the bad change "
    "in git, and Argo CD deploys the state from before:\n"
    "1. `git log --oneline -3` shows the recent commits, each with a short id called a sha.\n"
    "2. `git revert <sha>` makes a new commit that undoes the bad one. History stays intact.\n"
    "3. `git push`, then wait for the next check or run `argocd app sync hello-devops`.\n\n"
    "You may be thinking, \"Why not `kubectl rollout undo` from Day 40? It is one command.\" It changes the cluster "
    "but not git, so with self-heal on, Argo CD puts the bad version straight back. Our manager is loyal to the board, even when the board is wrong.\n\n"
    "Argo CD has its own `argocd app rollback` command, which redeploys an earlier entry from "
    "`argocd app history`. It refuses to run while automated sync is on, for the same reason: git must stay the "
    "source of truth.\n\n"
    "In a real emergency, follow this order:\n"
    "1. Turn off automated sync for that one app.\n"
    "2. Fix the cluster by hand, and write down every change.\n"
    "3. Put the same fix into git.\n"
    "4. Turn automated sync back on.\n\n"
    "Skip step 3, and the next sync quietly undoes your fix.\n\n"
    "All of this works for one app in one place. Real teams keep a test copy and a live copy of each app, and "
    "one Application cannot move a version safely from one to the other. The next lesson picks up there."
)

L["aside"] = {
    "title": "If the manager undoes hand edits, can I still use kubectl at all?",
    "body": (
        "Yes. Commands that only read, such as `kubectl get`, `kubectl describe` and `kubectl logs`, change nothing, "
        "so Argo CD has nothing to undo. They stay your main tools for finding problems, as they were last time. "
        "What changes is where writes go. A write to an object Argo CD manages belongs in git, or it "
        "will not last. Objects that Argo CD does not manage, such as a throwaway test Pod, are still yours to "
        "create and delete by hand."
    ),
    "after": 5,
}

L["analogy"] = (
    "The board on the kitchen wall says how the room should look tonight. A floor manager walks the room every few "
    "minutes and puts back anything that does not match. To change the room, you change the board, and the manager "
    "does the rest. A human manager would ask why a waiter moved a table. Argo CD never asks: it puts things back, "
    "even when the board itself is wrong."
)
L["mistake"] = (
    "A fix typed into the cluster by hand will not last. With self-heal on, Argo CD undoes `kubectl edit`, "
    "`kubectl scale` and even `kubectl delete` within seconds. With self-heal off, the fix lasts only until the next "
    "sync. Make the change in git and let Argo CD apply it. In a real emergency, turn off automated sync for that "
    "app first, and put the fix into git before you turn it back on."
)
L["real_world"] = (
    "A release breaks at night, and the engineer on call (the person whose turn it is to answer alerts) has to act. "
    "The team keeps one repo with a folder per environment, so the engineer reverts the pull request that changed "
    "the prod folder, and Argo CD rolls the cluster back. Every deploy is a merged pull request, so the review is "
    "the approval, and git records who did what, and why."
)

W = L["worked"]["steps"]
W[0]["say"] = (
    "Start from where the task below ends: Argo CD runs on your kind cluster and deploys hello-devops with "
    "self-heal on. An Application is an ordinary Kubernetes object, so kubectl can list it, with both statuses."
)
W[1]["say"] = (
    "See how Argo CD marks what it owns. Every object it applied carries a tracking annotation, its name tag. "
    "The tag holds the app name, then the object's group and kind (its family and type), then its namespace and "
    "name. A ConfigMap is a small object that holds settings, such as the greeting. It belongs to the core group, "
    "whose name is empty, so nothing stands before the slash."
)
W[2]["say"] = (
    "Now play the colleague who fixes things by hand. Change the greeting in the live ConfigMap and skip git. A "
    "`kubectl scale` would make a poor demo, because the lab tells Argo CD to ignore the replica count."
)
W[3]["say"] = (
    "The application controller watches every object it manages, so it sees the change at once. If you are quick, "
    "you catch the app OutOfSync. It stays Healthy, because the app still runs fine. Self-heal then puts git's "
    "version back after a short pause."
)
W[4]["say"] = "Wait a few seconds and read the value again. Git's text is back, and you did nothing."
W[5]["say"] = (
    "To change the greeting for good, change git. Edit `k8s/configmap.yaml`, commit and push, then sync instead of "
    "waiting up to three minutes. Pods read their settings (environment variables) only when they start (Day 42), "
    "so restart the Deployment to see the new text."
)

T = L["task"]
T["steps"] = [
    "Start your kind cluster from Day 38 if it is not running (`kind get clusters` should list `devops`). Push your latest `k8s/` folder to GitHub.",
    "Install Argo CD with the first two commands in the Commands list. Wait until all seven Pods in namespace `argocd` show Running.",
    "Start the port-forward, open the web page, and log in as `admin` with the initial password. Then log the CLI in too.",
    "Add `argocd/application.yaml` to your repo with your GitHub user name in `repoURL`. Commit, push, and apply it with kubectl.",
    "Watch the app until it shows Synced and Healthy. Click it in the web page and follow the tree from Deployment to ReplicaSet to Pods.",
    "Break a release on purpose: set the image in `k8s/deployment.yaml` to `hello-devops:9.9.9`, then commit, push and sync. Check that the app is Synced but not Healthy.",
    "Roll back with `git revert HEAD`, push and sync. Check that the app returns to Healthy.",
    "Test prune: remove `hpa.yaml` from the `resources` list in `k8s/kustomization.yaml`, commit and push. Watch Argo CD delete the HorizontalPodAutoscaler, then bring it back with another `git revert HEAD`.",
]
T["hints"] = [
    "If the app shows a repository error, Argo CD cannot read your repo. A public repo needs no password. For a private one, run `argocd repo add https://github.com/<you>/hello-devops --username <you> --password <token>` with a fine-grained token that can only read that repo.",
    "Argo CD checks git about every three minutes. Press Refresh in the web page, or run `argocd app sync hello-devops`, to skip the wait.",
    "kind has no image called `hello-devops:9.9.9`, so the new Pod tries Docker Hub and fails. `kubectl -n hello get pods` shows ImagePullBackOff, while the old Pods keep serving (Day 46).",
]
T["done_when"] = "After your last revert, `kubectl -n hello get hpa` lists hello-devops again, and `kubectl -n argocd get applications` shows it Synced and Healthy."

L["explain_back"]["prompt"] = "Explain GitOps to a teammate in 3 to 4 sentences. Mention who applies changes, what self-heal does, and how you roll back."
L["explain_back"]["answer"] = (
    "With GitOps, git holds the desired state of the cluster, and an agent inside the cluster, here Argo CD, "
    "applies it. Nobody runs kubectl apply by hand. A change is a commit, usually through a pull request, and CI "
    "never needs a cluster key. Argo CD keeps comparing the cluster with git, and self-heal undoes changes that "
    "skipped git. To roll back, you revert the commit, and Argo CD deploys the old state."
)

L["recap"] = [
    "GitOps: git holds the desired state, and an agent in the cluster pulls it and keeps the cluster equal to it.",
    "Pull deploys keep cluster keys out of CI, and git gives you review, history and rollback.",
    "An Application links a repo folder to a cluster and namespace. Install Argo CD 3.x with server-side apply.",
    "Sync status says whether the cluster matches git; health says whether it works. They are independent.",
    "Self-heal undoes hand edits and prune deletes what left git; both are off by default. Give each field one owner, so ignore HPA replicas.",
    "Roll back with git revert. One Application covers one app in one place; moving a version from test to live needs more (next lesson).",
]

C = L["check"]
C[0]["q"] = "The hello-devops app shows Synced and Degraded. What does that tell you?"
C[0]["why"] = "Synced means the cluster equals git. Degraded means the objects fail, so the problem is in what you committed, such as a bad image tag."
C[1]["q"] = "You delete `redis.yaml` from git and push. Automated sync is on, but prune is off. What happens to Redis in the cluster?"
C[1]["why"] = "Without prune, automated sync never deletes anything. The object stays, flagged as no longer in git, until someone prunes it."
C[2]["q"] = "A bad release is live, and self-heal is on. A colleague runs `kubectl rollout undo` (Day 40) to fix it fast. What happens next?"
C[2]["why"] = "Self-heal makes the cluster match git, and git still holds the bad version. Revert in git instead."

I = L["interview"]
I[0]["a"] = (
    "GitOps keeps the desired state of a system in git, and an agent such as Argo CD or Flux pulls it and keeps "
    "the system equal to it. A push pipeline runs kubectl apply from outside, so it needs cluster credentials, and "
    "it only acts while it runs. The GitOps agent runs inside the cluster, keeps reconciling, and can undo drift. "
    "Every change is a commit, so review, history and rollback come from normal git tools."
)
I[1]["a"] = (
    "I revert the commit, or the pull request, that introduced the change and push, so git again describes the "
    "last good state. Argo CD syncs, and the cluster follows. Argo CD has its own rollback command, but it refuses "
    "to run while automated sync is on, and it would leave the cluster different from git. A git revert keeps one "
    "source of truth and leaves a clear record of who changed what."
)
I[2]["a"] = (
    "Sync status compares the cluster with git: Synced means they match, OutOfSync means something differs. "
    "Health says whether the objects work, for example whether a Deployment's replicas are updated and available. "
    "They are independent. A bad image tag gives Synced but Degraded, and a harmless hand edit gives OutOfSync but "
    "Healthy. I check both before I call a deploy done."
)

L["deeper"]["body"] = (
    "On Day 38 you saw that a controller has to know which objects are its own. A ReplicaSet, the object a "
    "Deployment uses to keep its Pods running, does this with labels and owner references. An owner reference is "
    "a field on a Pod that names the object that made it. Argo CD has the same problem on a bigger scale. One "
    "cluster can hold objects from many Applications, plus objects that other controllers create.\n\n"
    "Since 3.0, Argo CD tracks objects with the annotation `argocd.argoproj.io/tracking-id`, in the form "
    "`app:group/Kind:namespace/name`. Before 3.0 the default was the label `app.kubernetes.io/instance`. That "
    "label caused two kinds of trouble:\n"
    "- Other tools copy labels. An operator, a controller that manages one kind of software, may copy its labels onto the objects it creates. A copied label could make Argo CD think it owned those objects.\n"
    "- Label values may be at most 63 characters, so long app names were cut short.\n\n"
    "The annotation names the exact object it sits on. If a tool copies it onto a different object, the name "
    "inside no longer matches, and Argo CD ignores the copy. You can still switch to label tracking in the "
    "`argocd-cm` ConfigMap, where Argo CD keeps its main settings, but there is rarely a reason to.\n\n"
    "Argo CD also ignores some objects on purpose. Since 3.0 its default settings exclude kinds that change all "
    "the time, such as EndpointSlice, Endpoints and Lease. An EndpointSlice is the list of Pod addresses behind a "
    "Service, so it changes every time a Pod becomes ready or not ready (Day 41). A Lease is a small object that "
    "programs renew every few seconds to show they are alive. Watching all of them would load the API server for "
    "no benefit, because nobody keeps them in git anyway.\n\n"
    "Inside one object, Argo CD skips the `status` part by default, since the cluster writes it. You add your own "
    "exceptions with `ignoreDifferences`, as the lab does for replicas. Use it narrowly. Each ignored field is a "
    "place where git no longer tells the whole truth.\n\n"
    "Finally, an object that lives in the app's namespace but in no Application is an orphaned resource. Argo CD "
    "never deletes it, because it never created it. A project can turn on warnings for orphaned resources with "
    "`orphanedResources`. That is a cheap way to spot leftovers from hand-made experiments, as long as the "
    "namespaces are small.\n\n"
    "For hello-devops this all runs quietly in the background. It starts to matter when a second tool, such as a "
    "service mesh or an operator, writes to the same objects as Argo CD. A service mesh is a layer that manages "
    "traffic between apps, and Part 15 covers it. Then `ignoreDifferences` and tracking decide who wins."
)

L["closing"] = (
    "We started with a restaurant board that nobody updated and a room that slowly drifted away from it. Now git "
    "is the board, and Argo CD is the manager. It keeps the cluster equal to git, undoes hand edits, and follows "
    "a revert back to the last good state. In your lab, open `argocd/application.yaml` and find the "
    "`ignoreDifferences` block. Then ask which other field a second controller might change behind Argo CD's back.\n\n"
    "Next, we'll run hello-devops as two copies, dev and prod, and answer the question every team meets: how does "
    "a tested version move safely from one to the other?"
)

# The opening and sections carry the board-and-manager picture and the hand-fix mistake (lead's notes).
L.pop("analogy", None)
L.pop("mistake", None)

P.write_text(json.dumps(d, indent=1, ensure_ascii=False) + "\n")
print("d47 written")
