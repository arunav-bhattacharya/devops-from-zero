"""First-principles review fixes for Days 61-62 (content/p16.json) and 63-64 (content/p17.json).
Each entry: (lesson id, field path, exact old text, new text). Paths:
  ("sections", i, "body"), ("worked", "steps", i, "say"), etc.
Run from the repo root: python3 brief/scratch/v4/p16p17/fix.py
Re-running is safe: an entry whose new text is already present is skipped."""
import json
import sys

FIXES = {
    "content/p16.json": [
        # ---------------- Day 61 ----------------
        ("d61", ("sections", 1, "body"),
         "OneAgent cannot add itself to a process that is already running. After you install it, restart the apps you want to see. Until then they show up as processes with no traces.",
         "How does it get inside a program it did not start? On Linux, the installer adds a small OneAgent library to the file `/etc/ld.so.preload`. The system's program loader reads that file each time a program starts, and loads the listed libraries before the program's own code runs. The OneAgent library checks what is starting, such as a JVM or a Node.js server, and loads the matching code module.\n\nThat hook only fires when a process starts. A process that was already running when you installed OneAgent never passed through it. So restart the apps you want to see. Until then they show up as processes with no traces."),
        ("d61", ("sections", 1, "body"),
         "ActiveGate is the second piece. It is a relay between your network and Dynatrace. It also talks to things OneAgent cannot sit inside, such as the Kubernetes API or a cloud provider's API.",
         "ActiveGate is the second piece, and it solves two problems. First, many company networks do not let every server reach the internet. The agents send their data to an ActiveGate inside the network, and only that one machine talks to Dynatrace. Second, some data only comes out of an API you have to call, such as the Kubernetes API or a cloud provider's API. ActiveGate makes those calls."),
        ("d61", ("sections", 2, "body"),
         "Smartscape is the live map of these entities and how they connect. OneAgent sees which process runs on which host and which service calls which, and Smartscape records what it sees.",
         "Smartscape is the live map of these entities and how they connect. Part of it is easy: OneAgent knows which host it runs on and which processes it found there. Calls between services take one more step. The code module in the caller adds a trace header to each outgoing request, the same idea as `traceparent` on Day 57. The code module in the receiver reads it, so both ends of the call are linked. Smartscape records each link it sees."),
        ("d61", ("sections", 2, "body"),
         "Every metric, log line and span carries the ID of the entity it came from. That shared ID",
         "Every metric, log line and span carries the ID of the entity it came from. A slow span in `payments` and an error log line from the same process carry the same IDs. That shared ID"),
        ("d61", ("sections", 4, "body"),
         "Davis starts at the affected entity and follows the Smartscape links and the traces to what that entity depends on. Graphs that spiked in the same minute are not enough on their own. Then it runs a fault-tree analysis to pick the most probable cause.",
         "Davis starts at the affected entity and follows the Smartscape links and the traces to what that entity depends on. At each dependency it asks whether that one is unhealthy too. If it is, Davis keeps going down. Dynatrace calls this walk a fault-tree analysis. The trail ends at an unhealthy component whose own dependencies look fine, and that component is the most probable root cause. Two graphs that spiked in the same minute are not linked by timing alone."),
        ("d61", ("worked", "steps", 4, "say"),
         "The time in the traces piles up in the database calls made by `payments`, so the fault tree ends there. It opens one problem. The root cause is `payments`, and `web` and `checkout` are listed as affected.",
         "The time in the traces piles up in the database calls made by `payments`. Postgres itself looks healthy, because the waiting happens in the connection pool inside `payments`, so the fault tree ends there. Davis opens one problem with `payments` as the root cause, and `web` and `checkout` listed as affected."),

        # ---------------- Day 62 ----------------
        ("d62", ("sections", 0, "body"),
         "Each way needs a token, a secret key with a list of permissions called scopes.",
         "Dynatrace has to know that the sender may write into your environment, so each way needs a token: a secret key with a list of permissions called scopes."),
        ("d62", ("sections", 1, "body"),
         "You install it once with Helm, then write a **DynaKube**, the custom resource that says what you want. Its biggest choice is the mode:",
         "You install it once with Helm, then write a **DynaKube**, the custom resource that says what you want.\n\n"
         "The Helm chart also installs a webhook: a small web server that the API server calls each time a Pod is created. The webhook may change the Pod before it is stored. Istio added its sidecars this way on Day 59, and Day 64 covers these admission webhooks. With the lab's DynaKube, the steps are:\n"
         "1. The Operator reads the DynaKube and starts an ActiveGate pod.\n"
         "2. A Pod is created in a labelled namespace, and the API server calls the webhook.\n"
         "3. The webhook adds an init container, volumes and environment variables to the Pod.\n"
         "4. The init container fetches the OneAgent code modules into a volume the app container shares.\n"
         "5. A mounted `/etc/ld.so.preload` file, the hook from Day 61, makes the app load OneAgent as it starts.\n"
         "6. OneAgent sends the app's data through the ActiveGate to Dynatrace.\n\n"
         "Pods that existed before never went through the webhook, which is why you restart hello-devops after applying.\n\n"
         "The DynaKube's biggest choice is the mode:"),
        ("d62", ("sections", 1, "body"),
         "It needs a CSI driver, a storage plugin that runs on each node.",
         "It needs a CSI driver, a storage plugin on each node that downloads the code modules once and shares them with every pod there."),
        ("d62", ("sections", 1, "body"),
         "OneAgent in app pods only, added by a webhook as each pod starts.",
         "OneAgent in app pods only, added by the webhook as each pod is created."),
        ("d62", ("sections", 1, "body"),
         "so app-only injection is the safer choice.",
         "so app-only injection is the safer choice. The lab also turns the CSI driver off, so each new pod's init container fetches its own copy of the code modules. That is slower, and fine for one app."),
        ("d62", ("sections", 3, "body"),
         "7. Metrics have their own first command. `timeseries",
         "7. Metrics have their own first command, because Grail stores them as data points over time, not as records. `timeseries"),
        ("d62", ("sections", 3, "body"),
         "Traces work the same way with `fetch spans`. Query C6 counts requests and failures and takes the p95 duration per service in one `summarize`.",
         "Traces work the same way with `fetch spans`, with one catch. A single request can make many spans inside a service, for example one per database call. Query C6 keeps only spans where `request.is_root_span == true`, the span where the request entered the service, so each request counts once. Then it counts requests and failures and takes the p95 duration per service in one `summarize`."),
        ("d62", ("sections", 5, "body"),
         "Site Reliability Guardian (SRG) is a release gate built from objectives. It fits the pipelines from Part 6:",
         "After a deploy, someone has to decide whether the new version behaves as well as the old one. By hand, that means watching dashboards, and on a busy day nobody does. Site Reliability Guardian (SRG) makes that decision a pipeline step. It is a release gate built from objectives, and it fits the pipelines from Part 6:"),
        ("d62", ("sections", 6, "body"),
         "and usage draws it down against a rate card.",
         "and usage draws it down against a rate card, the price list for each unit of usage."),
    ],
    "content/p17.json": [
        # ---------------- Day 63 ----------------
        ("d63", ("sections", 1, "body"),
         "The code was not in the git repository. It sat in extra build files inside the tarballs, and on some systems it reached the SSH server.",
         "The code was not in the git repository, where reviewers look. It sat in extra build files inside the tarballs, the .tar.gz archives that Linux distributions download and build from. Some distributions link the SSH server to xz's library indirectly, so on those systems the backdoor ran inside SSH."),
        ("d63", ("sections", 1, "body"),
         "ran a script that printed CI secrets into the build log.",
         "ran a script that printed CI secrets into the build log. In a public repository, anyone can read that log."),
        ("d63", ("sections", 3, "body"),
         "Trivy and grype are the two common free scanners.",
         "Trivy and grype are the two common free scanners. Each downloads a database built from public sources, such as the US National Vulnerability Database and the security notices of Linux distributions. Then it matches every package name and version in the list against that database."),
        ("d63", ("sections", 3, "body"),
         "and track the rest.",
         "and track the rest. A finding with no fix gives you nothing to update to, so failing on it only blocks releases."),
        ("d63", ("sections", 4, "body"),
         "3. Fulcio, Sigstore's certificate authority, checks",
         "3. Fulcio, Sigstore's certificate authority (Day 11), checks"),
        ("d63", ("sections", 4, "body"),
         "An image signed by anyone else fails. A pass tells you",
         "Then cosign checks that the signature matches the digest, that Fulcio issued the certificate, and that the identity inside it is the one you named. An image signed by anyone else fails.\n\nThe certificate expired ten minutes after signing, yet a check next month still passes. The Rekor entry proves when the signature was made, and that was while the certificate was valid. A pass tells you"),
        ("d63", ("sections", 5, "body"),
         "- Build L2: a hosted build platform signs the provenance. It catches tampering after the build.\n- Build L3: a hardened build platform. It catches tampering during the build.",
         "- Build L2: a hosted build platform signs the provenance. Any later edit breaks the signature, so it catches tampering after the build.\n- Build L3: a hardened build platform. Builds are kept apart, and build steps cannot reach the signing key, so it catches tampering during the build."),
        ("d63", ("sections", 6, "body"),
         "The image exists locally, and nothing is pushed yet.",
         "The image exists locally, and nothing is pushed yet. Step 4 pushes as it builds, so this extra build is what lets the job scan first."),

        # ---------------- Day 64 ----------------
        ("d64", ("sections", 0, "body"),
         "If the second one sounds unlikely, the worked example below does it on your own cluster.",
         "The second one works because the API server only checks that they may create the Pod. Then the kubelet fetches the Secret for the Pod, and nobody checks the creator's rights to Secrets. If that sounds unlikely, the worked example below does it on your own cluster."),
        ("d64", ("sections", 0, "body"),
         "1. On a real cluster, turn on encryption at rest for Secrets.",
         "1. On a real cluster, turn on encryption at rest for Secrets (Day 42), so etcd and its backups hold only encrypted values."),
        ("d64", ("sections", 1, "body"),
         "Catch secrets before they reach the remote, with two layers:\n- gitleaks on your laptop, ideally as a pre-commit hook, so the bad commit never happens.",
         "Catch secrets before they reach the remote. On your laptop, the place for that is a pre-commit hook: a script git runs before it records each commit. If the script fails, git makes no commit. The pre-commit tool installs such hooks from a config file, and gitleaks ships a ready one. So you get two layers:\n- gitleaks on your laptop as a pre-commit hook, so the bad commit never happens."),
        ("d64", ("sections", 1, "body"),
         "A person can skip the hook with `SKIP=gitleaks`,",
         "Anyone can skip the hook by putting `SKIP=gitleaks` in front of `git commit`,"),
        ("d64", ("sections", 2, "body"),
         "A secrets manager is one audited place that stores secrets,",
         "Without one home, a secret spreads: a `.env` file on three laptops, a CI setting, a message in chat. When it leaks, nobody knows who had it, and rotating it means finding every copy. A secrets manager is one audited place that stores secrets,"),
        ("d64", ("sections", 2, "body"),
         "It encrypts the values in a YAML file, leaving the keys readable,",
         "It encrypts the values in a YAML file, leaving the field names readable,"),
        ("d64", ("sections", 3, "body"),
         "4. Know the rights that are bigger than they look: creating Pods, `get` on `nodes/proxy`, and the verbs that change RBAC itself (`escalate`, `bind`, `impersonate`).",
         "4. Know the rights that are bigger than they look: creating Pods, `get` on `nodes/proxy`, and the verbs that change RBAC itself (`escalate`, `bind`, `impersonate`).\n\n"
         "A Pod creator can mount any Secret in the namespace and run the Pod as any of its ServiceAccounts. Access to `nodes/proxy` reaches the kubelet's own API, which can run commands in every Pod on that node. The RBAC verbs let an identity hand itself more rights, or act as someone else."),
        ("d64", ("sections", 3, "body"),
         "And if the app never calls the Kubernetes API (hello-devops does not),",
         "Kubernetes also puts a token for the Pod's ServiceAccount into every container by default, as a file under `/var/run/secrets/kubernetes.io/serviceaccount/`. Code in the Pod uses it to call the API. If the app never calls the Kubernetes API (hello-devops does not),"),
        ("d64", ("sections", 4, "body"),
         "use a seccomp profile.\n\n",
         "use a seccomp profile.\n\n"
         "The restricted rules use three Linux ideas that are new here:\n"
         "- Capabilities split root's powers into named pieces, such as `NET_BIND_SERVICE` for ports below 1024.\n"
         "- Privilege escalation is a process gaining more rights than its parent, for example by running `sudo`.\n"
         "- seccomp filters the system calls a program may make, its requests to the kernel. `RuntimeDefault` is the runtime's standard filter.\n\n"),
        ("d64", ("sections", 5, "body"),
         "You review them in pull requests and test them in CI, and an admission controller enforces them.",
         "You review them in pull requests and test them in CI, and an admission controller enforces them. The engine runs in the cluster as an admission webhook. At the third gate, the API server sends it each matching request and waits for the answer: allow or deny."),
        ("d64", ("sections", 5, "body"),
         "the checks are written in CEL, the short",
         "the checks are written in CEL (Common Expression Language), the short"),
        ("d64", ("sections", 5, "body"),
         "- `variables` finds the Pod spec inside any of those objects.",
         "- `variables` finds the Pod spec inside any of those objects. `.?` reads a field only if it exists, and `orValue()` gives the fallback."),
    ],
}


def get_parent(obj, path):
    for k in path[:-1]:
        obj = obj[k]
    return obj, path[-1]


def main():
    bad = 0
    for path, fixes in FIXES.items():
        d = json.load(open(path))
        lessons = {L["id"]: L for L in d["lessons"]}
        applied = skipped = 0
        for lid, fpath, old, new in fixes:
            parent, key = get_parent(lessons[lid], fpath)
            text = parent[key]
            if text.count(old) == 1 and (old not in new or text.count(new) == 0):
                parent[key] = text.replace(old, new)
                applied += 1
            elif new in text:
                skipped += 1
            else:
                print(f"MISS {path} {lid} {fpath}: {old[:70]!r} (found {text.count(old)} times)")
                bad += 1
        with open(path, "w") as f:
            json.dump(d, f, indent=1, ensure_ascii=False)
            f.write("\n")
        print(f"{path}: {applied} applied, {skipped} already present")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
