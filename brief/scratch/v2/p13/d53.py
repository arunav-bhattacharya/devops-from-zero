"""Day 53: Secrets, access and policy as code (Part 13, DevSecOps)."""
import pathlib

from svg import arrow, box, note, svg

LAB = pathlib.Path("/home/user/devops-from-zero/labs/hello-devops")


def lab(path):
    return (LAB / path).read_text().rstrip("\n")


def diagram():
    p = [note(280, 20, "one API request, left to right")]
    xs = [8, 120, 232, 344, 472]
    ws = [80, 80, 80, 96, 80]
    labels = ["kubectl", "Login", "RBAC", "Admission", "etcd"]
    classes = ["bx", "bx", "bxt", "bxo", "bx"]
    captions = ["apply", "who are you?", "may you?", "is it OK?", "stored"]
    for i in range(5):
        p.append(note(xs[i] + ws[i] / 2, 50, captions[i]))
        p.append(box(xs[i], 60, ws[i], 44, classes[i], labels[i]))
        if i < 4:
            p.append(arrow(xs[i] + ws[i] + 2, 82, xs[i + 1] - 4, 82))
    p.append(box(296, 152, 80, 40, "bxp", "PSA"))
    p.append(box(392, 152, 96, 40, "bxp", "Kyverno"))
    p.append(arrow(340, 150, 376, 108, dashed=True))
    p.append(arrow(436, 150, 404, 108, dashed=True))
    p.append(note(392, 214, "both plug into admission and can reject"))
    return svg(228, "A kubectl request passes login, then RBAC, then admission, and only then is stored in etcd. "
               "Pod Security Admission and Kyverno plug into the admission step and can reject the object.", p)


SECTIONS = [
    {
        "h": "A Kubernetes Secret is not locked",
        "body": (
            "Day 34 showed that a Secret's values are base64 encoded. Base64 is a different alphabet, not a lock: anyone can run `base64 -d`. "
            "The [Kubernetes docs](https://kubernetes.io/docs/concepts/configuration/secret/) call such a value obscured but not secret.\n\n"
            "Two less obvious facts make the group of readers bigger than you think:\n"
            "- By default, Secrets are stored unencrypted in etcd, the cluster's database. Anyone with access to etcd or its backups can read them.\n"
            "- Anyone who may create a Pod in a namespace can read every Secret in that namespace. "
            "They never need `get secrets`. They start a Pod that loads the Secret and prints it. The same holds for anyone who may create a Deployment.\n\n"
            "This trips up most people, so the worked example below proves it on your own cluster. "
            "One more detail from the RBAC docs: `list` and `watch` on Secrets also reveal the values, because a list returns the full objects.\n\n"
            "So the protection has layers:\n"
            "1. On a real cluster, turn on encryption at rest for Secrets.\n"
            "2. Keep the list of people and programs that can create Pods in a namespace short. The namespace is the real boundary.\n"
            "3. Keep the real values in a secrets manager and copy them into the cluster only where they are needed.\n"
            "4. Never put the value in git, not even for one commit."
        ),
        "refs": [
            {"title": "Kubernetes docs: Secrets", "url": "https://kubernetes.io/docs/concepts/configuration/secret/", "kind": "docs"},
            {"title": "Kubernetes docs: good practices for Secrets", "url": "https://kubernetes.io/docs/concepts/security/secrets-good-practices/", "kind": "docs"},
            {"title": "Kubernetes security best practices you need to know (TechWorld with Nana)", "url": "https://www.youtube.com/watch?v=oBf5lrmquYI", "kind": "watch"},
        ],
    },
    {
        "h": "Keep secrets out of git",
        "body": (
            "Git never forgets. Commit a token, delete it in the next commit, and the token is still in history, in every clone and every fork. "
            "So deleting the file fixes nothing. The fix is to rotate: revoke the leaked value where it was issued and create a new one. "
            "Treat anything that reached a remote as public.\n\n"
            "I tested this with gitleaks on a small repository. One commit added a GitHub token in `.env.local`, and the next commit deleted the file. "
            "`gitleaks dir` looks only at the files as they are now, and it said `no leaks found`. "
            "`gitleaks git` reads the whole history, and it said `leaks found: 1`, with the commit, the file and the line.\n\n"
            "Catch secrets before they reach the remote, with two layers:\n"
            "- gitleaks on your laptop, ideally as a pre-commit hook, so the bad commit never happens. Run `gitleaks git -v` once on every old repository too.\n"
            "- GitHub push protection on the server. It blocks a push that contains a known secret format, such as cloud keys, tokens and private keys. "
            "For your own account it is on by default when you push to public repositories.\n\n"
            "Both layers have holes. Scanners look for known formats and random-looking strings, so a plain password such as `summer2026` can slip through. "
            "A person can skip the hook with `SKIP=gitleaks`, and push protection lets you continue if you give a reason. "
            "Use them as a safety net, and keep secrets out of files in the first place: local values go in a `.env` file, which the lab's `.gitignore` already ignores."
        ),
        "refs": [
            {"title": "Gitleaks: scan git history, folders and stdin (README)", "url": "https://github.com/gitleaks/gitleaks/blob/master/README.md", "kind": "docs"},
            {"title": "GitHub Docs: push protection", "url": "https://docs.github.com/en/code-security/concepts/secret-security/push-protection", "kind": "docs"},
        ],
    },
    {
        "h": "Where secrets should live, and how they reach the cluster",
        "body": (
            "A secrets manager is one audited place that stores secrets, hands them out, rotates them and revokes them. Every read is logged. The common ones:\n"
            "- HashiCorp Vault. Since version 1.15 it is source-available under the Business Source License, now with IBM as licensor. "
            "You may run it in production, unless you offer it to others as a service that competes with IBM's paid versions.\n"
            "- OpenBao. An open source (MPL-2.0) fork of Vault 1.14, hosted by the OpenSSF.\n"
            "- Your cloud's own manager: AWS Secrets Manager, Google Secret Manager or Azure Key Vault.\n\n"
            "The values live there, but Kubernetes still wants a Secret object. Something has to carry the value into the cluster. "
            "There are three common patterns, and the question to ask is which file is safe to commit:\n"
            "- External Secrets Operator (ESO). You commit an ExternalSecret that names a key in the manager. A controller fetches the value, writes a normal Secret, and fetches again on a timer. Git holds no secret at all.\n"
            "- Sealed Secrets. `kubeseal` encrypts a Secret with the cluster controller's public key, and only that controller can decrypt it. You commit the SealedSecret.\n"
            "- SOPS. It encrypts the values in a YAML file, leaving the keys readable, with age, PGP or a cloud key service. You commit the encrypted file and decrypt at deploy time.\n\n"
            "At work my default is ESO plus the cloud's secret manager. Rotation happens in one place, and nothing secret ever enters git. "
            "Sealed Secrets suits a small team with one cluster and no cloud manager. "
            "The lab's `security/external-secret-fake.yaml` practises the ESO pattern with ESO's fake provider, so you need no cloud account."
        ),
        "refs": [
            {"title": "External Secrets Operator: the fake provider", "url": "https://github.com/external-secrets/external-secrets/blob/main/docs/provider/fake.md", "kind": "docs"},
            {"title": "Streamline your Kubernetes secrets with External Secrets Operator (CNCF Minutes)", "url": "https://www.youtube.com/watch?v=V40tXvvKh5Y", "kind": "watch"},
            {"title": "Introduction to HashiCorp Vault with Armon Dadgar (HashiCorp)", "url": "https://www.youtube.com/watch?v=VYfl-DpZ5wM", "kind": "watch"},
        ],
    },
    {
        "h": "RBAC: who may do what",
        "body": (
            "RBAC (role-based access control) answers one question for every request: may this identity do this verb on this resource? It uses four objects:\n"
            "- A Role lists rules, such as get, list and watch on pods, inside one namespace.\n"
            "- A ClusterRole is the same, for the whole cluster.\n"
            "- A RoleBinding gives a Role, or a ClusterRole, to a subject in one namespace.\n"
            "- A ClusterRoleBinding gives a ClusterRole to a subject everywhere.\n\n"
            "The subject is a user, a group or a ServiceAccount. A ServiceAccount is an identity for a program: a Pod, a CI job, an AI agent. "
            "Day 38 taught you to read `forbidden` errors. Today you write the rules.\n\n"
            "The official good practices fit in four lines:\n"
            "1. Bind inside a namespace with a RoleBinding whenever you can.\n"
            "2. Avoid wildcards. A `*` grants every resource type that exists today and every type added later.\n"
            "3. Do not use `cluster-admin` for daily work.\n"
            "4. Know the rights that are bigger than they look: creating Pods, `get` on `nodes/proxy`, and the verbs that change RBAC itself (`escalate`, `bind`, `impersonate`).\n\n"
            "Two habits for ServiceAccounts. Give each app its own, never the namespace's `default`. "
            "And if the app never calls the Kubernetes API (hello-devops does not), set `automountServiceAccountToken: false`, so a broken-into Pod has no token to steal.\n\n"
            "Test before you trust. `kubectl auth can-i` with `--as=system:serviceaccount:<namespace>:<name>` asks the API server directly what an identity may do."
        ),
        "refs": [
            {"title": "Kubernetes docs: role-based access control good practices", "url": "https://kubernetes.io/docs/concepts/security/rbac-good-practices/", "kind": "docs"},
            {"title": "Kubernetes docs: using RBAC authorization", "url": "https://kubernetes.io/docs/reference/access-authn-authz/rbac/", "kind": "docs"},
        ],
    },
    {
        "h": "Admission control: the last check before etcd",
        "body": (
            "Every request to the Kubernetes API passes three gates, in order:\n"
            "1. Authentication: who are you? A certificate or a token answers.\n"
            "2. Authorization: may you do this? RBAC answers.\n"
            "3. Admission: is this particular object acceptable?\n\n"
            "**Admission control** is that third gate. Admission controllers can change an object (mutating) or reject it (validating) before it is stored in etcd. "
            "RBAC decides whether you may create Deployments at all. Admission decides whether this Deployment, with `privileged: true` or an image tagged `:latest`, is allowed.\n\n"
            "Kubernetes ships one admission check you can use today: Pod Security Admission. It enforces the Pod Security Standards, which have three levels:\n"
            "- privileged: no restrictions.\n"
            "- baseline: blocks known ways to escape to the node, such as privileged containers and sharing the host's network.\n"
            "- restricted: current hardening practice. Run as non-root, no privilege escalation, drop all Linux capabilities, use a seccomp profile.\n\n"
            "You switch it on per namespace with labels such as `pod-security.kubernetes.io/enforce: baseline`. "
            "There are three modes: `enforce` rejects, `warn` shows the user a warning, and `audit` writes to the audit log.\n\n"
            "Here is the trap: enforce checks Pods, not Deployments. A Deployment that breaks the rule is accepted, and then its Pods are refused. "
            "`kubectl apply` says `configured` and nothing starts. Warn mode does check Deployments, so I set `warn` one level stricter than `enforce`. "
            "You see what would break next, before anything does."
        ),
        "refs": [
            {"title": "Kubernetes docs: Pod Security Standards", "url": "https://kubernetes.io/docs/concepts/security/pod-security-standards/", "kind": "docs"},
            {"title": "Kubernetes docs: Pod Security Admission", "url": "https://kubernetes.io/docs/concepts/security/pod-security-admission/", "kind": "docs"},
            {"title": "Kubernetes docs: admission control", "url": "https://kubernetes.io/docs/reference/access-authn-authz/admission-controllers/", "kind": "docs"},
        ],
    },
    {
        "h": "Policy as code with Kyverno",
        "body": (
            "Pod Security Admission covers Pod hardening and nothing else. Your own rules, such as \"no `:latest` tags\" or \"every workload has a team label\", need a policy engine. "
            "**Policy as code** means those rules are files in git: reviewed in pull requests, tested in CI, and enforced by an admission controller.\n\n"
            "There are two common engines:\n"
            "- Kyverno. Policies are Kubernetes YAML, and the checks are written in CEL, the short expression language Kubernetes itself uses. Kyverno became a CNCF graduated project in March 2026.\n"
            "- OPA Gatekeeper. Policies are written in Rego, a general policy language, as ConstraintTemplates, and switched on as Constraints. A good fit where a company already uses OPA.\n\n"
            "For a Kubernetes-only team I would pick Kyverno, because its policies look like the YAML you already write. "
            "One warning before you search the web: most Kyverno tutorials use `kind: ClusterPolicy`. "
            "[Kyverno 1.19](https://github.com/kyverno/website/blob/main/src/content/blog/announcing-kyverno-release-1.19/index.md) (August 2026) deprecated ClusterPolicy, and removal is planned for 1.20. "
            "The lab uses the CEL-based `ValidatingPolicy`.\n\n"
            "Read `policy/disallow-latest-tag.yaml` in Files from the top:\n"
            "- `validationActions: [Deny]` rejects a bad request. `Audit` lets it through and records a failure in a PolicyReport.\n"
            "- `matchConstraints` picks namespace hello, and Pods plus the workloads that create Pods.\n"
            "- `variables` finds the Pod spec inside any of those objects.\n"
            "- `validations` are CEL expressions that must be true, each with a message for the user.\n\n"
            "Roll out every new rule the same way: Audit first, read the reports, fix what fails, then switch to Deny."
        ),
        "refs": [
            {"title": "Kyverno docs: ValidatingPolicy", "url": "https://kyverno.io/docs/policy-types/validating-policy/", "kind": "docs"},
            {"title": "Kyverno 1.16: advancing policy as code with CEL (CNCF Cloud Native Live)", "url": "https://www.youtube.com/watch?v=QNODJ_5qo68", "kind": "watch"},
            {"title": "OPA Gatekeeper (README)", "url": "https://github.com/open-policy-agent/gatekeeper/blob/master/README.md", "kind": "docs"},
        ],
    },
    {
        "h": "A security checklist for hello-devops",
        "body": (
            "Here is Part 13 as a list you can tick. Each item is something you can show with one command or one file:\n"
            "1. No secrets in history: `gitleaks git -v` finds nothing, and push protection is on.\n"
            "2. Pinned CI: every third-party action uses a full commit SHA, and Dependabot watches them.\n"
            "3. Least-privilege CI: every workflow declares `permissions:`, and only the release job may write packages and attestations.\n"
            "4. Known contents: every release has an SBOM, a passing scan and a signature, and `security/verify-release.sh` passes.\n"
            "5. Secrets from a store: no Secret with a real value in git. ESO or Sealed Secrets creates them.\n"
            "6. Narrow identities: each app has its own ServiceAccount, no token is mounted where it is not needed, and no Role uses `*`.\n"
            "7. Hardened Pods: namespace hello warns on the restricted standard, and the hello-devops Deployment passes it.\n"
            "8. Rules at the door: Kyverno denies `:latest`, and audits non-root and team labels.\n\n"
            "Day 55 folds this list into your capstone."
        ),
        "refs": [
            {"title": "Kubernetes docs: enforce Pod Security Standards with namespace labels", "url": "https://kubernetes.io/docs/tasks/configure-pod-container/enforce-standards-namespace-labels/", "kind": "docs"},
        ],
    },
]

WORKED = {
    "title": "Prove that Pod creators can read Secrets",
    "steps": [
        {
            "say": "Create a Secret in namespace hello and read it back. The value comes out base64 encoded, and one command turns it back into the password.",
            "code": (
                "$ kubectl -n hello create secret generic db-password --from-literal=password=hunter2-example\n"
                "secret/db-password created\n"
                "$ kubectl -n hello get secret db-password -o jsonpath='{.data.password}'\n"
                "aHVudGVyMi1leGFtcGxl\n"
                "$ kubectl -n hello get secret db-password -o jsonpath='{.data.password}' | base64 -d\n"
                "hunter2-example"
            ),
            "lang": "console",
        },
        {
            "say": "Make a developer identity that may run Pods but has no rule about Secrets at all (`security/rbac-pod-creator.yaml` in Files). "
                   "Then ask the API server what it may do. `--as` acts as that identity for one request.",
            "code": (
                "$ kubectl apply -f security/rbac-pod-creator.yaml\n"
                "serviceaccount/dev created\n"
                "role.rbac.authorization.k8s.io/pod-creator created\n"
                "rolebinding.rbac.authorization.k8s.io/dev-pod-creator created\n"
                "$ kubectl auth can-i get secrets -n hello --as=system:serviceaccount:hello:dev\n"
                "no\n"
                "$ kubectl auth can-i create pods -n hello --as=system:serviceaccount:hello:dev\n"
                "yes"
            ),
            "lang": "console",
        },
        {
            "say": "Reading the Secret directly is refused, as the Role intends.",
            "code": (
                "$ kubectl -n hello get secret db-password --as=system:serviceaccount:hello:dev\n"
                "Error from server (Forbidden): secrets \"db-password\" is forbidden: User \"system:serviceaccount:hello:dev\" "
                "cannot get resource \"secrets\" in API group \"\" in the namespace \"hello\""
            ),
            "lang": "console",
        },
        {
            "say": "Now the same identity creates a Pod that loads the Secret into an environment variable and prints it. "
                   "The API server accepts it, because creating Pods is allowed. The kubelet fetches the Secret on the Pod's behalf.",
            "code": (
                "$ kubectl -n hello apply --as=system:serviceaccount:hello:dev -f - <<'EOF'\n"
                "apiVersion: v1\n"
                "kind: Pod\n"
                "metadata: {name: peek}\n"
                "spec:\n"
                "  restartPolicy: Never\n"
                "  containers:\n"
                "    - name: peek\n"
                "      image: busybox:1.37\n"
                "      command: [\"sh\", \"-c\", \"echo The password is $PASSWORD\"]\n"
                "      env:\n"
                "        - {name: PASSWORD, valueFrom: {secretKeyRef: {name: db-password, key: password}}}\n"
                "EOF\n"
                "pod/peek created"
            ),
            "lang": "console",
        },
        {
            "say": "Read the Pod's log, still as the developer. The password that the RBAC rule was meant to protect is right there.",
            "code": (
                "$ kubectl -n hello logs peek --as=system:serviceaccount:hello:dev\n"
                "The password is hunter2-example"
            ),
            "lang": "console",
        },
        {
            "say": "So the real boundary is the namespace, not the Secret rule. Keep Secrets in namespaces where few people and programs can create Pods, "
                   "and keep the real values in a secrets manager. Clean up the demo.",
            "code": (
                "$ kubectl -n hello delete pod/peek secret/db-password\n"
                "pod \"peek\" deleted from hello namespace\n"
                "secret \"db-password\" deleted from hello namespace\n"
                "$ kubectl delete -f security/rbac-pod-creator.yaml"
            ),
            "lang": "console",
        },
    ],
}

CODE = [
    {"lang": "yaml", "title": "policy/disallow-latest-tag.yaml", "src": lab("policy/disallow-latest-tag.yaml"),
     "run": "kubectl apply -f policy/disallow-latest-tag.yaml"},
    {"lang": "yaml", "title": "policy/require-run-as-nonroot.yaml", "src": lab("policy/require-run-as-nonroot.yaml"),
     "run": "kubectl apply -f policy/require-run-as-nonroot.yaml"},
    {"lang": "yaml", "title": "security/rbac-pod-creator.yaml", "src": lab("security/rbac-pod-creator.yaml"),
     "run": "kubectl apply -f security/rbac-pod-creator.yaml"},
    {"lang": "yaml", "title": "security/external-secret-fake.yaml", "src": lab("security/external-secret-fake.yaml"),
     "run": "kubectl apply -f security/external-secret-fake.yaml"},
]

COMMANDS = [
    {"cmd": "brew install gitleaks", "what": "Install the gitleaks secret scanner."},
    {"cmd": "gitleaks git -v", "what": "Scan the whole git history of the current repository for secrets."},
    {"cmd": "gitleaks dir -v .", "what": "Scan the files as they are now, ignoring history."},
    {"cmd": "kubectl -n hello get secret db-password -o jsonpath='{.data.password}' | base64 -d", "what": "Decode one value of a Secret. Base64 is not encryption."},
    {"cmd": "kubectl auth can-i create pods -n hello --as=system:serviceaccount:hello:dev", "what": "Ask whether an identity may do one thing. Answers yes or no."},
    {"cmd": "kubectl auth can-i --list -n hello --as=system:serviceaccount:hello:dev", "what": "List everything an identity may do in a namespace."},
    {"cmd": "kubectl label --overwrite ns hello pod-security.kubernetes.io/warn=restricted pod-security.kubernetes.io/enforce=baseline", "what": "Enforce the baseline Pod Security level, and warn about anything that breaks restricted."},
    {"cmd": "helm repo add kyverno https://kyverno.github.io/kyverno/ && helm repo update", "what": "Add the Kyverno chart repository to Helm."},
    {"cmd": "helm install kyverno kyverno/kyverno -n kyverno --create-namespace", "what": "Install Kyverno in its own namespace."},
    {"cmd": "kubectl apply -f policy/", "what": "Apply every policy file in the folder."},
    {"cmd": "kubectl get validatingpolicies", "what": "List Kyverno ValidatingPolicies and whether they are ready."},
    {"cmd": "kubectl -n hello get policyreports -o wide", "what": "Show pass and fail counts per object, from Audit and background checks."},
    {"cmd": "helm repo add external-secrets https://charts.external-secrets.io", "what": "Add the External Secrets Operator chart repository."},
    {"cmd": "helm install external-secrets external-secrets/external-secrets -n external-secrets --create-namespace", "what": "Install External Secrets Operator and its CRDs."},
    {"cmd": "kubectl -n hello get externalsecret hello-api-token", "what": "Check that ESO synced the Secret (STATUS SecretSynced, READY True)."},
]

DEEPER = (
    "Two tools from today deserve a closer look before you use them at work.\n\n"
    "Kubernetes has its own CEL policies. Since Kubernetes 1.30, ValidatingAdmissionPolicy is built in: you write CEL validations in one object, "
    "bind them to resources with a ValidatingAdmissionPolicyBinding, and the API server runs them itself, with no webhook. "
    "Kyverno's ValidatingPolicy is a superset of it. It adds background scans of existing objects, PolicyReports, exceptions, a CLI for tests, and calls to outside data. "
    "Kyverno can even generate a built-in ValidatingAdmissionPolicy from a simple ValidatingPolicy, so the API server evaluates it. "
    "I tested the CEL in the lab's two policies exactly that way: I copied the expressions into a built-in policy on a test API server and sent it 17 test objects. "
    "It denied `nginx:latest`, a bare `nginx`, `localhost:5000/hello-devops` with no tag, and a `:latest` init container. "
    "It allowed a digest, a registry port with a tag, and anything in other namespaces. "
    "That is a cheap habit worth copying: test a policy against good and bad examples before it guards a real cluster. "
    "In CI, the Kyverno CLI does the same job with `kyverno apply` and `kyverno test`.\n\n"
    "Admission webhooks have a cost. Kyverno and Gatekeeper run as webhooks: the API server calls them over the network for every matching request. "
    "If the webhook is down and its failure policy is Fail, matching requests fail too, including your own fixes. "
    "If the failure policy is Ignore, requests pass unchecked while it is down. Neither is free. Three habits help:\n"
    "- Match only the resources and namespaces a policy needs. Never match everything in the cluster.\n"
    "- Run more than one replica of the policy engine in production, and watch its health in Prometheus like any other service.\n"
    "- Keep the policy engine's own namespace and kube-system out of its rules, so you can always repair the cluster.\n\n"
    "Gatekeeper takes a different shape. A ConstraintTemplate holds Rego code and declares a new kind of object, for example one for required labels. "
    "A Constraint of that kind then says where the rule applies and with which parameters, and Gatekeeper ships a shared library of ready-made templates. "
    "Rego is a real language with a learning curve. In return, the same OPA engine also decides for Terraform, Docker, SSH and your own APIs, "
    "which is why companies that already use OPA tend to stay with Gatekeeper."
)

lesson = {
    "id": "d53",
    "title": "Secrets, access and policy as code",
    "minutes": 50,
    "goal": "By the end you can keep secrets out of git and out of plain sight, give each identity only the access it needs, and make the cluster refuse risky objects with Kyverno policies.",
    "guess": {
        "q": "You store a database password in a Kubernetes Secret in namespace hello. By default, who can read the password?",
        "options": [
            "Only Pods that mount it, since Secrets are encrypted",
            "Nobody, because the value is base64 encoded",
            "Anyone who may read Secrets or create Pods there",
            "Only cluster admins, whatever the RBAC rules say",
        ],
        "answer": 2,
        "why": "Base64 is an encoding, not encryption, and etcd stores Secrets unencrypted by default. Anyone who may create a Pod in the namespace can mount the Secret and print it.",
    },
    "terms": [
        {"term": "Kubernetes Secret", "plain": "An object for small sensitive values. They are base64 encoded and, by default, stored unencrypted."},
        {"term": "Secrets manager", "plain": "One audited service that stores, hands out, rotates and revokes secrets, such as Vault, OpenBao or AWS Secrets Manager."},
        {"term": "Secret scanning", "plain": "Searching files and git history for passwords and tokens, ideally before they are pushed."},
        {"term": "RBAC", "plain": "Role-based access control: rules that say which identity may use which verbs on which Kubernetes resources."},
        {"term": "ServiceAccount", "plain": "A Kubernetes identity for a program, such as a Pod, a CI job or an AI agent."},
        {"term": "Admission control", "plain": "The API server's last check, which can change or reject an object before it is stored."},
        {"term": "Pod Security Standards", "plain": "Three built-in levels (privileged, baseline, restricted) that say how locked down a Pod must be."},
        {"term": "Policy as code", "plain": "Rules about what objects may look like, kept in git, tested in CI and enforced by the cluster."},
    ],
    "sections": SECTIONS,
    "analogy": (
        "Think of a club. RBAC is the guest list: it decides who gets in and which rooms each guest may enter. "
        "Admission control is the bouncer who also checks what you carry, such as no glass bottles, whoever you are. "
        "The secrets manager is the cloakroom, with a ticket for every coat and a log of who took what. "
        "Where it breaks: a bouncer can make an exception for a friend, while an admission policy treats every request exactly the same, so one typo in a Deny policy can lock out everybody, you included."
    ),
    "diagram": diagram(),
    "diagram_caption": "RBAC decides who may act; admission decides whether this object is acceptable.",
    "worked": WORKED,
    "code": CODE,
    "commands": COMMANDS,
    "mistake": (
        "Switching a new policy straight to Deny for the whole cluster. It blocks your own tools as well: Argo CD syncs, the monitoring stack, even add-ons in kube-system. "
        "Scope each policy to the namespaces it is meant for, start in Audit, read the PolicyReports for a few days, fix what they find, and only then switch to Deny."
    ),
    "real_world": (
        "At a payments company, the platform team keeps a small set of Kyverno policies in a git repository and reviews changes like code. "
        "Product teams see failures in PolicyReports and in pull request checks long before anything is blocked. "
        "Database passwords live in the cloud's secret manager, ESO copies them into each namespace, and rotating a password is one change in one place."
    ),
    "task": {
        "title": "Lock down namespace hello",
        "steps": [
            "Run `gitleaks git -v` in your hello-devops repository. Then make a throwaway repository, commit a fake token in one commit, delete it in the next, and compare `gitleaks dir` with `gitleaks git`.",
            "Install Kyverno with Helm on your kind cluster and apply `policy/disallow-latest-tag.yaml` and `policy/require-run-as-nonroot.yaml`.",
            "Run `kubectl -n hello run test --image=nginx:latest` and read the message. Try again with `busybox:1.37`, then delete the test Pod.",
            "Read the PolicyReports in namespace hello. Which workloads fail the non-root rule, and why?",
            "Label namespace hello with `warn=restricted` and `enforce=baseline`, re-apply `k8s/deployment.yaml`, and read the Pod Security warning.",
            "Harden the hello-devops Deployment: a Pod `securityContext` with `runAsNonRoot: true` and a `RuntimeDefault` seccomp profile, and a container `securityContext` that blocks privilege escalation and drops all capabilities. Apply until the warning is gone.",
            "Install External Secrets Operator with Helm, apply `security/external-secret-fake.yaml` and decode the Secret it creates. Change `version: v1` to `v2`, apply, and watch the value change within a minute.",
        ],
        "hints": [
            "The warning lists every missing field, for example `allowPrivilegeEscalation != false` and `seccompProfile`. Fix them one at a time. The image already runs as user 10001 (Day 16), so `runAsNonRoot: true` works without `runAsUser`.",
            "Leave Redis failing for now. Its image starts as root, so with `runAsNonRoot: true` the kubelet would refuse to start it. That is why the policy is in Audit mode.",
            "If the ExternalSecret shows `SecretSyncedError`, run `kubectl -n hello describe externalsecret hello-api-token` and read the events at the bottom.",
        ],
        "done_when": "Kyverno rejects the `nginx:latest` Pod, the hello-devops Deployment applies with no Pod Security warning, and the Secret made by ESO decodes to `demo-token-v2`.",
    },
    "explain_back": {
        "prompt": "Explain in 3 to 4 sentences how a password should travel from its owner to the hello-devops Pod, and who can read it on the way. Mention git, the secrets manager, RBAC and admission.",
        "answer": (
            "The password never goes into git; it lives in a secrets manager, and git holds only an ExternalSecret that names the key. "
            "External Secrets Operator fetches the value and writes a normal Kubernetes Secret in the namespace, where it is only base64 encoded. "
            "So RBAC matters twice: who may read Secrets, and who may create Pods in that namespace, because a Pod creator can mount and print any Secret there. "
            "Admission policies such as Pod Security and Kyverno then check every Pod that wants to use it, so a risky Pod is rejected before it ever runs."
        ),
    },
    "recap": [
        "A Secret is base64, not encrypted, and anyone who can create Pods in its namespace can read it.",
        "Deleting a leaked secret does not remove it from history: scan with gitleaks, use push protection, and rotate.",
        "Real values live in a secrets manager; ESO, Sealed Secrets or SOPS bring them into the cluster without plain values in git.",
        "RBAC: namespaced Roles, no wildcards, no daily cluster-admin, one ServiceAccount per app, and test with kubectl auth can-i.",
        "Admission control checks each object; Pod Security Admission enforces the standards, and Kyverno runs your own rules.",
        "Roll out every policy in Audit first, then Deny; ClusterPolicy is deprecated, so write ValidatingPolicy.",
    ],
    "check": [
        {
            "q": "A teammate removes a leaked API key from the repository with a new commit and says the problem is solved. What should you do first?",
            "options": [
                "Revoke the key and issue a new one",
                "Rewrite history so the key disappears",
                "Make the repository private for a while",
                "Run gitleaks dir to confirm it is gone",
            ],
            "answer": 0,
            "why": "Anything that reached a remote may already be copied; rotating the key is the only real fix, and history cleanup comes after.",
        },
        {
            "q": "Namespace payments enforces the restricted Pod Security level. You apply a Deployment whose Pods run as root. What do you see?",
            "options": [
                "kubectl apply fails with a Forbidden error",
                "The Pods start and an audit event is written",
                "Kubernetes changes the Pods to run as non-root",
                "The Deployment is accepted, but no Pods appear",
            ],
            "answer": 3,
            "why": "Enforce mode checks Pods, not workloads, so the Deployment is stored and its ReplicaSet's Pods are refused.",
        },
        {
            "q": "A CI job only needs to update the image of Deployments in namespace shop. Which RBAC setup fits least privilege best?",
            "options": [
                "A ClusterRoleBinding to the built-in edit role",
                "A Role in shop with get and patch on deployments",
                "A Role in shop with all verbs on all resources",
                "The cluster-admin role, but only for CI runs",
            ],
            "answer": 1,
            "why": "A namespaced Role with only the verbs and resource the job uses gives it nothing more than it needs.",
        },
    ],
    "interview": [
        {
            "q": "How do you manage secrets for applications on Kubernetes?",
            "a": (
                "I keep the real values in a secrets manager, such as Vault, OpenBao or the cloud provider's service, and never in git. "
                "External Secrets Operator syncs them into Kubernetes Secrets on a timer, so rotation happens in one place. "
                "In the cluster I turn on encryption at rest, limit who can read Secrets or create Pods per namespace, and give each app its own ServiceAccount. "
                "On the developer side, gitleaks runs as a pre-commit hook and push protection is on, and a leaked value is always rotated, not only deleted."
            ),
        },
        {
            "q": "What is the difference between RBAC and an admission policy engine like Kyverno?",
            "a": (
                "RBAC is authorization: it decides whether an identity may use a verb on a resource type, for example create Deployments in a namespace. "
                "Admission control runs after that and looks at the object itself, for example whether its image uses `:latest` or its Pod runs as root. "
                "Kyverno and Gatekeeper plug into admission and let you write those rules as code. "
                "You need both: Kyverno's own docs say it does not replace RBAC."
            ),
        },
        {
            "q": "How would you roll out a new security policy without breaking teams?",
            "a": (
                "I write it as code in git, with test cases for good and bad objects, and review it like any change. "
                "I deploy it in Audit mode, scoped to the namespaces it is meant for, and read the PolicyReports to see what would fail. "
                "I share the results with the owning teams, help them fix their manifests, and add exceptions only with a reason and an owner. "
                "When the reports are clean, I switch to Deny, and I watch the policy engine's health because it now sits in the deploy path."
            ),
        },
    ],
    "deeper": {"minutes": 12, "body": DEEPER},
    "sources": [
        {"title": "Kubernetes docs: role-based access control good practices", "url": "https://kubernetes.io/docs/concepts/security/rbac-good-practices/"},
        {"title": "Kubernetes docs: Pod Security Admission", "url": "https://kubernetes.io/docs/concepts/security/pod-security-admission/"},
        {"title": "Announcing Kyverno 1.19 (source on GitHub)", "url": "https://github.com/kyverno/website/blob/main/src/content/blog/announcing-kyverno-release-1.19/index.md"},
        {"title": "External Secrets Operator: getting started", "url": "https://github.com/external-secrets/external-secrets/blob/main/docs/introduction/getting-started.md"},
    ],
}
