"""Fifth pass (book voice) for d64, Secrets, access and policy as code. Writer: ti.
Replaces only prose fields of d64 in content/p17.json."""
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[4]
PATH = ROOT / "content/p17.json"
P = json.loads(PATH.read_text())
L = next(x for x in P["lessons"] if x["id"] == "d64")

L["goal"] = ("By the end you can keep passwords out of git and out of plain sight, give each person and program only the access "
             "it needs, and make the cluster refuse risky objects with Kyverno policies.")

L["opening"] = """Your jam shop has grown. There are two helpers now, a safe in the office, and a back door where deliveries arrive. One evening a helper writes the safe's code on a page of the order book, so the morning shift can open it. The next day you cross it out. Two weeks later, cash goes missing, and the order book has been in five people's hands.

That mistake is easy to make. Each helper only wanted the morning to go smoothly, and crossing out a note feels like fixing it.

Last time, we sealed every jar and checked the seal before it left the shop. A seal protects what you ship. It does nothing about the keys to the shop itself. In this lesson, we'll find out who can really read the hello-devops passwords, move them somewhere safe, hand out keys carefully, and post a guard at the back door. Before we start, make a guess, and keep it in mind."""

L["guess"]["q"] = ("You store a database password in a Kubernetes Secret, the cluster's place for passwords, in namespace hello. "
                   "By default, who can read the password?")
L["guess"]["why"] = ("Base64 only writes the value in another alphabet, and the cluster's database (etcd) stores Secrets unencrypted by default. "
                     "Anyone who may start a Pod in the namespace can load the Secret into it and print it.")

plain = {
    "Kubernetes Secret": "A Kubernetes record for small private values, such as passwords. The values are only written in another alphabet (base64) and, by default, stored unencrypted.",
    "Secrets manager": "One service that stores, hands out, replaces and cancels secrets, and logs every read, such as Vault, OpenBao or AWS Secrets Manager.",
    "Secret scanning": "Searching files and their whole history for passwords and tokens, ideally before they leave your laptop.",
    "RBAC": "Role-based access control: rules that say which identity may do which action on which kind of Kubernetes object.",
    "ServiceAccount": "A Kubernetes identity for a program, such as a running app, a CI job or an AI agent.",
    "Admission control": "The cluster's last check on a request, which can change or refuse an object before it is saved.",
    "Pod Security Standards": "Three built-in levels (privileged, baseline, restricted) that say how locked down a running app must be.",
    "Policy as code": "Rules about what objects may look like, kept in git, tested automatically and enforced by the cluster.",
}
for t in L["terms"]:
    t["plain"] = plain[t["term"]]

S = L["sections"]

S[0]["h"] = "A Kubernetes Secret is not locked"
S[0]["body"] = """In the shop, the safe's code could at least go in an envelope. Kubernetes has an envelope too, and it is thinner than it looks. Kubernetes is the system from Part 10 that runs your containers on a group of machines, called a cluster.

A Secret is the Kubernetes object for small private values, such as a database password. An object is a record you hand to Kubernetes that describes what you want. Day 42 showed that a Secret's values are base64 encoded. Base64 only writes the same bytes in another alphabet, and anyone can undo it with `base64 -d`. The [Kubernetes docs](https://kubernetes.io/docs/concepts/configuration/secret/) call such a value obscured but not secret.

Two facts make the group of readers bigger than you think. First, Secrets are stored unencrypted by default in etcd, the cluster's database. Anyone with access to etcd or its backups can read them.

Second, anyone who may create a Pod in a namespace can read every Secret in that namespace. A Pod is one running copy of an app. A namespace is a named room inside the cluster, and hello-devops lives in the room called `hello`. They never need the right to read Secrets (`get secrets`). They start a Pod that loads the Secret and prints it. The same holds for anyone who may create a Deployment, the object that keeps Pods running.

This works because of who checks what. The API server is the cluster's front desk: every request, from people or programs, passes through it. It only checks that they may create the Pod. Then the kubelet, the helper on each machine that starts Pods, fetches the Secret for the Pod. Nobody checks the creator's rights to Secrets. In the shop, you may not open the safe, but you may send the cook an order that says "bring me what's in the safe". The worked example below does it on your own cluster.

So protect Secrets in layers:
1. On a real cluster, turn on encryption at rest for Secrets (Day 42), so etcd and its backups hold only encrypted values.
2. Keep short the list of people and programs that can create Pods in a namespace. The namespace is the real boundary.
3. Keep the real values in a secrets manager and copy them into the cluster only where they are needed.
4. Never put the value in git, not even for one commit.

The last layer sounds the easiest, yet teams break it most often, so we start there."""

S[1]["h"] = "Why deleting a leaked password from git fixes nothing"
S[1]["body"] = """Git, the tool that keeps your code's history, works like that order book. Every commit is a saved snapshot of your files, and git keeps them all. Commit a token (a secret string that works like a key card), delete it in the next commit, and the token is still in history. It is also in every copy of the repository that anyone made.

Deleting the file fixes nothing. You have to rotate: revoke the leaked value where it was issued, so it stops working, and create a new one. Treat anything that reached a remote, the copy of your repository on a server such as GitHub, as public. **A deleted secret is still a leaked secret. Rotate it.**

Watch a scanner miss it, then catch it. Gitleaks is a secret scanner: a tool that searches files for passwords and tokens. In a test repository, one commit added a GitHub token in `.env.local`, and the next commit deleted the file. A scan with `gitleaks dir` looks only at the files as they are now, and it said `no leaks found`. A scan with `gitleaks git` reads the whole history, and it said `leaks found: 1`, with the commit, the file and the line.

Better still, catch secrets before they reach the remote, with a pre-commit hook on your laptop: a script git runs before it records each commit. If the script fails, git makes no commit. The pre-commit tool installs such hooks from a settings file, and gitleaks ships a ready one. So you get two layers:
- gitleaks on your laptop as a pre-commit hook, so the bad commit never happens. Run `gitleaks git -v` once on every old repository too.
- GitHub push protection on the server. It blocks a push (an upload of commits) that contains a known secret format, such as cloud keys, tokens and private keys. For your own account it is on by default when you push to public repositories.

Both layers have holes. Scanners look for known formats and random-looking strings, so a plain password such as `summer2026` can slip through. Anyone can skip the hook by putting `SKIP=gitleaks` in front of `git commit`, and push protection lets you continue if you give a reason.

Treat them as a safety net, and keep secrets out of files in the first place. Local values go in a `.env` file, which the lab's `.gitignore` already tells git to ignore. So if secrets don't live in git, where do they live?"""

S[2]["h"] = "Where secrets should live, and how they reach the cluster"
S[2]["body"] = """Without one home, a secret spreads: a `.env` file on three laptops, a setting in the automatic build, a message in chat. When it leaks, nobody knows who had it, and rotating it means finding every copy. A secrets manager is one place that stores secrets, hands them out, rotates them and revokes them. Every read is logged, like the sign-in book at a bank's safe room. The common ones:
- HashiCorp Vault, the best-known one (Go deeper covers its license).
- OpenBao, an open source fork (a copy that went its own way) of Vault 1.14.
- Your cloud's own manager: AWS Secrets Manager, Google Secret Manager or Azure Key Vault.

The values live there, but Kubernetes still wants a Secret object, so something has to carry each value into the cluster. Three patterns are common. For each one, ask which file you can safely commit:
- External Secrets Operator (ESO). You commit an ExternalSecret that names a key in the manager. A controller fetches the value, writes a normal Secret, and fetches again on a timer. Git holds no secret at all.
- Sealed Secrets. `kubeseal` encrypts a Secret with the cluster controller's public key, and only that controller can decrypt it. You commit the SealedSecret.
- SOPS. It encrypts the values in a YAML settings file, leaving the field names readable, with age, PGP or a cloud key service. You commit the encrypted file and decrypt at deploy time.

A controller is a program in the cluster that keeps doing one job, over and over. A public key is the half of a key pair that anyone may hold, and it can lock but never open.

At work my default is ESO plus the cloud's secret manager. Rotation happens in one place, and nothing secret ever enters git. Sealed Secrets suits a small team with one cluster and no cloud manager. The lab's `security/external-secret-fake.yaml` practises the ESO pattern with ESO's fake provider, so you need no cloud account. Next: who may touch them?"""

S[3]["h"] = "RBAC: who gets which keys"
S[3]["body"] = """The new helper in the shop gets a key to the front room and the storeroom, but not to the office. Kubernetes hands out keys with RBAC, role-based access control. For every request it asks one question: may this identity do this verb on this resource? A verb is an action such as get, list or create. A resource is a kind of object, such as pods or secrets. RBAC uses four objects:
- A Role lists rules, such as get, list and watch on pods, inside one namespace.
- A ClusterRole is the same, for the whole cluster.
- A RoleBinding gives a Role, or a ClusterRole, to a subject in one namespace.
- A ClusterRoleBinding gives a ClusterRole to a subject everywhere.

The subject is whoever gets the rights: a user, a group or a ServiceAccount. A ServiceAccount is an identity for a program: a Pod, a CI job, an AI agent.

The [official good practices](https://kubernetes.io/docs/concepts/security/rbac-good-practices/) fit in four lines:
1. Bind inside a namespace with a RoleBinding whenever you can.
2. Avoid wildcards. A `*` grants every resource type that exists today and every type added later.
3. Do not use `cluster-admin`, the built-in role that may do everything, for daily work.
4. Know the rights that are bigger than they look: creating Pods, `get` on `nodes/proxy`, and the verbs that change RBAC itself (`escalate`, `bind`, `impersonate`).

Each is a master key in disguise. A Pod creator can mount any Secret in the namespace and run the Pod as any of its ServiceAccounts. Access to `nodes/proxy` reaches the kubelet's own API, which can run commands in every Pod on that machine. The RBAC verbs let an identity hand itself more rights, or act as someone else. Even `list` or `watch` on Secrets reveals the values, because a list returns the full objects.

Two habits for ServiceAccounts. Give each app its own, never the namespace's `default`. Also, Kubernetes puts a token for the Pod's ServiceAccount into every container by default, as a file. Code in the Pod uses it to call the API. If the app never calls the Kubernetes API (hello-devops does not), set `automountServiceAccountToken: false`, so a broken-into Pod has no token to steal.

Test a rule before you rely on it. The command `kubectl auth can-i` (kubectl is the Kubernetes command-line tool) with `--as=system:serviceaccount:<namespace>:<name>` asks the API server directly what an identity may do. RBAC decides who may act. It can't look inside what they send, and that is the next gate."""

S[4]["h"] = "Admission control: a guard at the back door"
S[4]["body"] = """At the shop's back door, a guard checks every delivery against the house rules (no glass, every box labelled), whoever sent it. Kubernetes has one too. Every request to the Kubernetes API passes three gates, in order:
1. Authentication: who are you? A certificate or a token answers.
2. Authorization: may you do this? RBAC answers.
3. Admission: is this particular object acceptable?

Admission control is that third gate. Admission controllers can change an object (mutating) or reject it (validating) before it is stored in etcd. RBAC decides whether you may create Deployments at all. Admission decides whether this Deployment is allowed, say one with `privileged: true` (full power over the machine) or an image tagged `:latest`.

Kubernetes has a built-in admission check made for Pod hardening: Pod Security Admission. It enforces the Pod Security Standards, which have three levels:
- privileged: no restrictions.
- baseline: blocks known ways to escape to the node (the machine), such as privileged containers and sharing the host's network.
- restricted: current hardening practice. Run as non-root, no privilege escalation, drop all Linux capabilities, use a seccomp profile.

Root is the all-powerful admin user on Linux. The restricted rules use three more Linux ideas:
- Capabilities split root's powers into named pieces, such as `NET_BIND_SERVICE` for ports below 1024.
- Privilege escalation is a process gaining more rights than its parent, for example by running `sudo`.
- seccomp filters the system calls a program may make, its requests to the kernel. `RuntimeDefault` is the runtime's standard filter.

You switch it on per namespace with labels such as `pod-security.kubernetes.io/enforce: baseline`. There are three modes: `enforce` rejects, `warn` shows the user a warning, and `audit` writes to the audit log.

Enforce mode has a trap: it checks Pods, never Deployments. A Deployment that breaks the rule is accepted, and then its Pods are refused, so `kubectl apply` says `configured` and nothing starts. Warn mode does check Deployments. I set `warn` one level stricter than `enforce`, so I see what would break next before anything does. Pod Security covers hardening and nothing else. Your own rules need one more tool."""

S[5]["h"] = "Writing your own house rules with Kyverno"
S[5]["body"] = """A rule of your own, such as "no `:latest` tags" or "every workload has a team label", needs a policy engine: a program that checks objects against rules you write. With policy as code, those rules are files in git. You review them in pull requests, test them in CI (the automatic checks on every change), and the cluster enforces them. In the shop, the house rules move from the guard's memory into a binder that anyone can read.

The engine runs in the cluster as an admission webhook, a small web service. At the third gate, the API server sends it each matching request and waits for the answer: allow or deny. There are two common engines:
- Kyverno. Policies are Kubernetes YAML, and the checks are written in CEL, the short expression language Kubernetes itself uses.
- OPA Gatekeeper. Policies are written in Rego, a general policy language. A good fit where a company already uses OPA.

For a Kubernetes-only team I would pick Kyverno, because its policies look like the YAML files you already write. One warning: most Kyverno tutorials use `kind: ClusterPolicy`. [Kyverno 1.19](https://github.com/kyverno/website/blob/main/src/content/blog/announcing-kyverno-release-1.19/index.md) (August 2026) deprecated ClusterPolicy, and removal is planned for 1.20. The lab uses the CEL-based `ValidatingPolicy`.

Read `policy/disallow-latest-tag.yaml` in Files from the top:
- `validationActions: [Deny]` rejects a bad request. `Audit` lets it through and records a failure in a PolicyReport.
- `matchConstraints` picks namespace hello, and Pods plus the workloads that create Pods.
- `variables` finds the Pod spec (the part that describes the containers) inside any of those objects.
- `validations` are CEL expressions that must be true, each with a message for the user.

A guard follows the binder exactly, typos included. Switch a new policy straight to Deny for the whole cluster, and it blocks your own tools too. Argo CD syncs, the monitoring stack and even add-ons in kube-system get refused. **A new rule can lock out everyone, you included. Start in Audit.** Scope each policy to the namespaces it is meant for. Read the reports for a few days, fix what fails, and only then switch to Deny. Now let's gather all of Part 17 into one list."""

S[6]["h"] = "A security checklist for hello-devops"
S[6]["body"] = """Part 17 fits in a list you can tick, and you can prove each item with one command or one file:
1. No secrets in history: `gitleaks git -v` finds nothing, and push protection is on.
2. Pinned CI: every third-party action uses a full commit SHA, and Dependabot watches them.
3. Least-privilege CI: every workflow declares `permissions:`, and only the release job may write packages and attestations.
4. Known contents: every release has an SBOM, a passing scan and a signature, and `security/verify-release.sh` passes.
5. Secrets from a store: no Secret with a real value in git. ESO or Sealed Secrets creates them.
6. Narrow identities: each app has its own ServiceAccount, no token is mounted where it is not needed, and no Role uses `*`.
7. Hardened Pods: namespace hello warns on the restricted standard, and the hello-devops Deployment passes it.
8. Rules at the door: Kyverno denies `:latest`, and audits non-root and team labels.

Day 68 folds this list into your capstone. Every item makes an attack harder, and none makes it impossible. A person with the right keys can still make a bad change, and a policy only catches what someone thought to write down. Those limits matter more once the helper making changes is a program that writes code for you, and that is where the next part goes."""

L["aside"] = {
    "title": "If base64 hides nothing, why does Kubernetes use it?",
    "body": ("Base64 is there for carrying data, not for hiding it. A Secret can hold binary data, such as a certificate file, "
             "and raw bytes don't fit neatly inside a text format like YAML or JSON. Base64 turns any bytes into plain letters, "
             "digits and a few symbols, so they travel safely in a text file. Kubernetes also accepts plain text in a field called "
             "`stringData` and encodes it for you."),
    "after": 0,
}

for k in ("analogy", "mistake", "real_world"):
    L.pop(k, None)

L["diagram_caption"] = "RBAC decides who may act; admission decides whether this object is acceptable."

W = L["worked"]["steps"]
W[0]["say"] = ("Create a Secret in namespace hello and read it back. The value comes out base64 encoded, "
               "and one more command turns it back into the password.")
W[1]["say"] = ("Make a developer identity that may run Pods but has no rule about Secrets at all (`security/rbac-pod-creator.yaml` in Files). "
               "Then ask the API server what it may do. The `--as` flag acts as that identity for one request.")
W[2]["say"] = "Reading the Secret directly is refused, just as the Role intends."
W[3]["say"] = ("Now the same identity creates a Pod that loads the Secret into an environment variable (a named setting the program can read) and prints it. "
               "The API server accepts it, because creating Pods is allowed. The kubelet fetches the Secret on the Pod's behalf.")
W[4]["say"] = "Read the Pod's log, still as the developer. The password that the RBAC rule was meant to protect is right there."
W[5]["say"] = ("So the real boundary is the namespace, and the Secret rule alone protects nothing. "
               "Keep Secrets in namespaces where few people and programs can create Pods, and keep the real values in a secrets manager. "
               "Then clean up the demo.")

T = L["task"]
T["steps"] = [
    "Run `gitleaks git -v` in your hello-devops repository. Then make a throwaway repository and commit a fake GitHub token: `ghp_` followed by 36 random letters and digits. Delete it in the next commit, and compare `gitleaks dir` with `gitleaks git`.",
    "Install Kyverno with Helm on your kind cluster and apply `policy/disallow-latest-tag.yaml` and `policy/require-run-as-nonroot.yaml`.",
    "Run `kubectl -n hello run test --image=nginx:latest` and read the message. Try again with `busybox:1.37`, then delete the test Pod.",
    "Read the PolicyReports in namespace hello. Which workloads fail the non-root rule, and why?",
    "Label namespace hello with `warn=restricted` and `enforce=baseline`, apply `k8s/deployment.yaml` again, and read the Pod Security warning.",
    "Harden the hello-devops Deployment: a Pod `securityContext` with `runAsNonRoot: true` and a `RuntimeDefault` seccomp profile, and a container `securityContext` that blocks privilege escalation and drops all capabilities. Apply until the warning is gone.",
    "Install External Secrets Operator with Helm, apply `security/external-secret-fake.yaml` and decode the Secret it creates. Change `version: v1` to `v2`, apply, and watch the value change within a minute.",
]
T["hints"] = [
    "The warning lists every missing field, for example `allowPrivilegeEscalation != false` and `seccompProfile`. Fix them one at a time. The image already runs as user 10001 (Day 22), so `runAsNonRoot: true` works without `runAsUser`.",
    "Leave Redis failing for now. Its image starts as root, so with `runAsNonRoot: true` the kubelet would refuse to start it. That is why the policy is in Audit mode.",
    "If the ExternalSecret shows `SecretSyncedError`, run `kubectl -n hello describe externalsecret hello-api-token` and read the events at the bottom.",
]
T["done_when"] = "Kyverno rejects the `nginx:latest` Pod, the hello-devops Deployment applies with no Pod Security warning, and the Secret made by ESO decodes to `demo-token-v2`."

L["explain_back"]["answer"] = ("The password never goes into git. It lives in a secrets manager, and git holds only an ExternalSecret that names the key. "
                               "External Secrets Operator fetches the value and writes a normal Kubernetes Secret in the namespace, where it is only base64 encoded. "
                               "So RBAC matters twice: who may read Secrets, and who may create Pods in that namespace, because a Pod creator can mount and print any Secret there. "
                               "Admission policies such as Pod Security and Kyverno then check every Pod that wants to use it, so a risky Pod is rejected before it ever runs.")

L["recap"] = [
    "A Secret is base64, not encrypted, and anyone who can create Pods in its namespace can read it.",
    "Deleting a leaked secret does not remove it from history: scan with gitleaks, use push protection, and rotate.",
    "Real values live in a secrets manager. ESO, Sealed Secrets or SOPS bring them into the cluster without plain values in git.",
    "RBAC: namespaced Roles, no wildcards, no daily cluster-admin, one ServiceAccount per app, and test with kubectl auth can-i.",
    "Admission control checks each object. Pod Security Admission enforces the standards, and Kyverno runs your own rules.",
    "Limits: scanners miss plain passwords, and a policy only catches what you wrote down. Roll out every policy in Audit first, then Deny.",
]

C = L["check"]
C[0]["q"] = "A teammate removes a leaked API key from the repository with a new commit and says the problem is solved. What should you do first?"
C[0]["why"] = "Anything that reached a remote may already be copied. Rotating the key is the only real fix, and cleaning up history comes after."
C[1]["q"] = "Namespace payments enforces the restricted Pod Security level. You apply a Deployment whose Pods run as root. What do you see?"
C[1]["why"] = "Enforce mode checks Pods, not workloads, so the Deployment is stored and the Pods it tries to create are refused."
C[2]["q"] = "A CI job only needs to update the image of Deployments in namespace shop. Which RBAC setup fits least privilege best?"
C[2]["why"] = "A Role inside the namespace, with only the verbs and resource the job uses, gives it nothing more than it needs."

I = L["interview"]
I[0]["a"] = ("I keep the real values in a secrets manager, such as Vault, OpenBao or the cloud provider's service, and never in git. "
             "External Secrets Operator syncs them into Kubernetes Secrets on a timer, so rotation happens in one place. "
             "In the cluster I turn on encryption at rest, limit who can read Secrets or create Pods per namespace, and give each app its own ServiceAccount. "
             "On the developer side, gitleaks runs as a pre-commit hook and push protection is on, and a leaked value is always rotated, not only deleted.")
I[1]["a"] = ("RBAC is authorization: it decides whether an identity may use a verb on a resource type, for example create Deployments in a namespace. "
             "Admission control runs after that and looks at the object itself, for example whether its image uses `:latest` or its Pod runs as root. "
             "Kyverno and Gatekeeper plug into admission and let you write those rules as code. "
             "You need both, and Kyverno's own docs say it does not replace RBAC.")
I[2]["a"] = ("I write it as code in git, with test cases for good and bad objects, and review it like any change. "
             "I deploy it in Audit mode, scoped to the namespaces it is meant for, and read the PolicyReports to see what would fail. "
             "I share the results with the owning teams, help them fix their manifests, and add exceptions only with a reason and an owner. "
             "When the reports are clean, I switch to Deny, and I watch the policy engine's health because it now sits in the deploy path.")

L["deeper"]["body"] = """First, two facts the main text left out. HashiCorp Vault has been source-available under the Business Source License since version 1.15, now with IBM as licensor. You may run it in production, unless you offer it to others as a service that competes with IBM's paid versions. OpenBao, the open source (MPL-2.0) fork of Vault 1.14, is hosted by the OpenSSF. And Kyverno became a CNCF graduated project in March 2026. Its CEL stands for Common Expression Language.

Two small details from the main text. The ServiceAccount token sits in each container under `/var/run/secrets/kubernetes.io/serviceaccount/`. In the lab's CEL, `.?` reads a field only if it exists, and `orValue()` gives the fallback.

Kubernetes has its own CEL policies. Since Kubernetes 1.30, ValidatingAdmissionPolicy is built in and stable. You write CEL checks in one object and bind them to resources with a ValidatingAdmissionPolicyBinding. The API server then runs them itself, with no webhook. Kyverno's ValidatingPolicy can do everything that one does, and more: background scans of existing objects, PolicyReports, exceptions, a command-line tool for tests, and calls to outside data. Kyverno can even turn a simple ValidatingPolicy into a built-in ValidatingAdmissionPolicy, so the API server runs it.

The CEL in the lab's two policies was tested exactly that way. The expressions went into a built-in policy on a test API server, which then got 17 test objects. It denied `nginx:latest`, a bare `nginx`, `localhost:5000/hello-devops` with no tag, and a `:latest` init container. It allowed a digest, a registry port with a tag, and anything in other namespaces. Testing a policy against good and bad examples costs very little. Make it a habit. In CI, the Kyverno CLI does the same job with `kyverno apply` and `kyverno test`.

Admission webhooks have a cost. Kyverno and Gatekeeper run as webhooks, so the API server calls them over the network for every matching request. If the webhook is down and its failure policy is Fail, matching requests fail too, including your own fixes. If the failure policy is Ignore, requests pass unchecked while it is down. You choose which risk to carry, and three habits make both smaller:
- Match only the resources and namespaces a policy needs. Never match everything in the cluster.
- Run more than one replica of the policy engine in production, and watch its health in Prometheus like any other service.
- Keep the policy engine's own namespace and kube-system out of its rules, so you can always repair the cluster.

Gatekeeper takes a different shape. A ConstraintTemplate holds Rego code and declares a new kind of object, for example one for required labels. A Constraint of that kind then says where the rule applies and with which settings. Gatekeeper ships a shared library of ready-made templates. Rego is a real language that takes time to learn. In return, the same OPA engine also decides for Terraform, Docker, SSH and your own APIs, which is why companies that already use OPA tend to stay with Gatekeeper."""

L["closing"] = """We started with a safe code written in the order book and crossed out the next day. Now the passwords live in one logged store, git holds only the name of each key, and each key holder has just the doors they need. A guard checks every delivery against rules kept in git.

Look at one namespace you use today and run `kubectl auth can-i --list` as its app's ServiceAccount. Anything on that list you can't explain is a key to take back.

Next, we'll bring a new kind of helper into the shop: an AI assistant that writes code quickly and sometimes confidently wrong. How do you get its speed without trusting its every word?"""

new = {}
for k in L:
    if k in ("opening", "closing", "aside"):
        continue
    new[k] = L[k]
    if k == "goal":
        new["opening"] = L["opening"]
    if k == "sections":
        new["aside"] = L["aside"]
    if k == "deeper":
        new["closing"] = L["closing"]
P["lessons"][P["lessons"].index(L)] = new
PATH.write_text(json.dumps(P, ensure_ascii=False, indent=1) + "\n")
print("d64 written")
