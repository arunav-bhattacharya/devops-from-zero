from svg import svg, box, arrow, note
from labfiles import lab, scratch

diagram = svg(240, "Release job: build, scan, push, sign and attest; the image in the registry then passes a Kyverno admission check before it runs in the cluster", [
    note(276, 26, "CI release job"),
    box(12, 40, 88, 44, "bx", "Build"),
    box(122, 40, 88, 44, "bxo", "Scan"),
    box(232, 40, 88, 44, "bx", "Push"),
    box(342, 40, 88, 44, "bxg", "Sign"),
    box(452, 40, 88, 44, "bxg", "Attest"),
    arrow(102, 62, 118, 62),
    arrow(212, 62, 228, 62),
    arrow(322, 62, 338, 62),
    arrow(432, 62, 448, 62),
    arrow(276, 86, 276, 146),
    box(232, 150, 88, 44, "bx", "Registry"),
    box(342, 150, 88, 44, "bxp", "Kyverno"),
    box(452, 150, 88, 44, "bxt", "Cluster"),
    arrow(322, 172, 338, 172),
    arrow(432, 172, 448, 172),
    note(386, 214, "admission check"),
])

trivy_before = """$ trivy image --severity HIGH,CRITICAL --ignore-unfixed hello-devops:1.0.0
...
Python (python-pkg)
===================
Total: 5 (HIGH: 5, CRITICAL: 0)

│ msgpack    │ CVE-2026-114613     │ HIGH     │ fixed  │ 1.1.2             │ 1.2.3
│            │ GHSA-6v7p-g79w-8964 │          │        │                   │ 1.2.1
│ setuptools │ CVE-2025-47273      │          │        │ 70.3.0            │ 78.1.1
│ urllib3    │ CVE-2026-97687      │          │        │ 2.7.0             │ 2.8.0
│            │ CVE-2026-97689      │          │        │                   │"""

lesson = {
    "id": "d22",
    "title": "DevSecOps and the software supply chain",
    "minutes": 40,
    "goal": "By the end you can scan, list and sign the hello-devops image in CI, verify its signature and provenance, and block risky Pods with a Kyverno policy.",
    "guess": {
        "q": "Your workflow uses a popular action as some-org/some-action@v4. An attacker steals the maintainer's token. What can happen on your next run?",
        "options": [
            "Nothing, because a version tag can never point to new code",
            "GitHub scans the action and blocks the run for you",
            "Only forks of your repo would run the bad code",
            "Your run executes the attacker's code, because tags can move",
        ],
        "answer": 3,
        "why": "A git tag is a pointer that can be moved. In the 2025 tj-actions/changed-files attack, tags were moved to a malicious commit; pinning to a full commit SHA prevents this.",
    },
    "terms": [
        {"term": "Supply chain attack", "plain": "An attack on something you depend on (a library, a tool, a build step) instead of on your own code."},
        {"term": "SBOM", "plain": "Software bill of materials: a list of every package and version inside an artifact, like an ingredient label."},
        {"term": "CVE", "plain": "A public ID for one known security bug, such as CVE-2024-3094."},
        {"term": "Keyless signing", "plain": "Signing with a short-lived certificate tied to an identity, such as a CI workflow, so there is no long-lived private key."},
        {"term": "Provenance", "plain": "A signed record of how, where and from which source an artifact was built."},
        {"term": "SLSA", "plain": "Supply-chain Levels for Software Artifacts: a framework that grades how trustworthy a build is, in levels."},
        {"term": "Admission policy", "plain": "A rule the Kubernetes API checks before it stores an object, used to block risky settings."},
    ],
    "sections": [
        {
            "h": "Shift left: security as part of the pipeline",
            "body": (
                "In many companies, a security team used to look at a release once, near the end. "
                "DevSecOps moves that work into the daily routine of everyone who writes and ships code.\n\n"
                "Shift left means moving checks earlier, to the left side of the pipeline drawing. "
                "A leaked password caught before `git push` costs you a minute. The same leak found in production can cost a weekend of rotating keys. "
                "So you put cheap, automatic checks where code is written and built:\n"
                "- Secret scanning before the push and on every commit.\n"
                "- Dependency and image scanning in CI.\n"
                "- Signing and provenance at release time.\n"
                "- Policies when objects enter the cluster.\n\n"
                "The other big idea is least privilege: every person, token and pod gets only the rights it needs, for only as long as it needs them. "
                "You have done this three times already: the `permissions` block (Day 12), OIDC instead of stored cloud keys (Day 15), and a non-root user in the Dockerfile (Day 8)."
            ),
            "refs": [
                {"title": "GitHub Docs: security hardening for GitHub Actions", "url": "https://docs.github.com/en/actions/security-guides/security-hardening-for-github-actions", "kind": "docs"},
            ],
        },
        {
            "h": "Real supply chain attacks",
            "body": (
                "Attackers often skip your code and go after something you trust. Three recent cases:\n"
                "- xz-utils (2024): a trusted maintainer account hid a backdoor in the release files of a compression library.\n"
                "- tj-actions/changed-files (March 2025): attackers moved an action's version tags to code that printed CI secrets into logs.\n"
                "- Trivy (March 2026): with stolen credentials, attackers force-pushed 76 of 77 `trivy-action` tags and shipped a malicious release.\n\n"
                "The xz backdoor could reach the SSH server on some Linux systems. "
                "A developer, Andres Freund, noticed SSH logins using too much CPU and traced the cause to xz. "
                "GitHub's advisory on tj-actions says over 23,000 repositories used that action. "
                "And Trivy is the scanner you add to your pipeline today.\n\n"
                "The defenses are simple habits. Pin actions to a full commit SHA, verify what you download, keep CI tokens narrow, and rotate secrets after an incident. "
                "That is why the new `release.yml` pins `trivy-action` to a commit, not a tag."
            ),
            "refs": [
                {"title": "GitHub advisory: xz backdoor (CVE-2024-3094)", "url": "https://github.com/advisories/GHSA-rxwq-x6h5-x525", "kind": "read"},
                {"title": "GitHub advisory: tj-actions/changed-files (CVE-2025-30066)", "url": "https://github.com/advisories/GHSA-mrrh-fwg8-r2c3", "kind": "read"},
                {"title": "Aqua Security advisory: Trivy supply chain compromise (CVE-2026-33634)", "url": "https://github.com/aquasecurity/trivy/security/advisories/GHSA-69fq-xp46-6x23", "kind": "read"},
            ],
        },
        {
            "h": "Know what is inside: SBOMs and scanning",
            "body": (
                "Your image holds about 100 packages: Debian packages from the base image, Python itself, and your app's libraries. You wrote none of them. "
                "An SBOM (software bill of materials) lists them all with their versions. "
                "The two standard formats are SPDX and CycloneDX, and the tool `syft` writes either one. "
                "When the next big bug is announced, you search your SBOMs instead of guessing which images are affected.\n\n"
                "A vulnerability scanner compares those packages with public lists of known bugs. Each bug has a CVE ID. "
                "Trivy scans images with `trivy image`. With `trivy config`, it checks files such as Dockerfiles, Kubernetes YAML and Terraform for risky settings.\n\n"
                "Scanners report a lot, so decide up front what stops the pipeline. "
                "A rule I like: fail on HIGH and CRITICAL issues that already have a fixed version, and track the rest. "
                "Failing on every LOW finding mostly teaches people to ignore the scanner.\n\n"
                "Secrets need their own scanner. GitHub push protection blocks known secret formats when you push. "
                "For your own account it is on by default for public repos. On your laptop, `gitleaks git` scans your whole git history."
            ),
            "refs": [
                {"title": "Syft: SBOM generator", "url": "https://github.com/anchore/syft", "kind": "docs"},
                {"title": "Trivy: vulnerability and config scanner", "url": "https://github.com/aquasecurity/trivy", "kind": "docs"},
                {"title": "Gitleaks: secret scanner", "url": "https://github.com/gitleaks/gitleaks", "kind": "docs"},
            ],
        },
        {
            "h": "Signing and provenance",
            "body": (
                "A scan tells you what is inside. A signature tells you who made it, and that nobody changed it since. "
                "With **keyless signing** from cosign (part of the Sigstore project), you never store a private key:\n"
                "1. The release job asks GitHub for an OIDC token that says \"this is release.yml in this repo, on tag v1.2.0\".\n"
                "2. Fulcio, Sigstore's certificate authority, trades it for a certificate that is valid for about ten minutes.\n"
                "3. cosign signs the image digest and stores the signature in the registry, next to the image.\n"
                "4. The signing event goes into Rekor, a public log that nobody can quietly edit.\n\n"
                "Later, anyone can run `cosign verify` and demand that exact workflow identity.\n\n"
                "Provenance goes one step further. It is a signed statement of how the image was built: which repo, which commit, which workflow. "
                "SLSA (say \"salsa\") grades builds in levels. Level 1 means provenance exists. At Level 2, a hosted build platform creates and signs it. "
                "Level 3 adds a build platform hardened against tampering. "
                "GitHub artifact attestations give you Build Level 2, and building inside a shared reusable workflow can reach Level 3."
            ),
            "refs": [
                {"title": "cosign on GitHub", "url": "https://github.com/sigstore/cosign", "kind": "docs"},
                {"title": "SLSA: build track levels", "url": "https://slsa.dev/spec/v1.2/build-track-basics", "kind": "read"},
                {"title": "GitHub Docs: artifact attestations for build provenance", "url": "https://docs.github.com/en/actions/security-guides/using-artifact-attestations-to-establish-provenance-for-builds", "kind": "docs"},
            ],
        },
        {
            "h": "Policy as code at the cluster door",
            "body": (
                "CI checks only cover images that go through CI. Anyone with access can still run `kubectl run` with any image. So you also check at the cluster door.\n\n"
                "Before the Kubernetes API server stores an object, it can ask admission webhooks whether to accept it. "
                "A policy engine answers. Its rules are code, and you keep them in git. The two common engines:\n"
                "- Kyverno: policies are Kubernetes YAML, with checks written in CEL, a short expression language that Kubernetes also uses.\n"
                "- OPA Gatekeeper: policies are written in Rego, a general policy language.\n\n"
                "For a Kubernetes-only shop I would pick Kyverno, because the policies look like the YAML you already write. "
                "The lab's `policy/` folder has two Kyverno policies. One rejects images tagged `:latest` or with no tag at all. "
                "The other reports Pods that do not set `runAsNonRoot: true`.\n\n"
                "Each policy has a mode. Audit allows the object but records a failure in a PolicyReport. Deny blocks it. "
                "Roll out a new rule in Audit, fix what it finds, then switch to Deny. "
                "In Kyverno 1.19 the older ClusterPolicy type is deprecated, with removal planned for 1.20, so the lab uses the newer ValidatingPolicy type."
            ),
            "refs": [
                {"title": "Kyverno: ValidatingPolicy", "url": "https://kyverno.io/docs/policy-types/validating-policy", "kind": "docs"},
                {"title": "Announcing Kyverno 1.19", "url": "https://kyverno.io/blog/2026/08/20/announcing-kyverno-release-1.19", "kind": "read"},
            ],
        },
    ],
    "analogy": (
        "Think of packaged food. The ingredient label is the SBOM, and the safety inspection is the vulnerability scan. "
        "A tamper-evident seal with the factory's stamp is the signature, and the farm-to-shelf record is the provenance. "
        "The shop's rule \"no product without a seal\" is the admission policy. "
        "Where it breaks: a seal proves who packed the food and that nobody opened it. It says nothing about whether the food is good, and a signed image can still contain a bug."
    ),
    "diagram": diagram,
    "diagram_caption": "Checks in CI, then one last check at the cluster door.",
    "worked": {
        "title": "Triage a scan of your own image",
        "steps": [
            {
                "say": "Install the tools with Homebrew. syft writes SBOMs and trivy scans for known bugs. Both read images straight from Docker Desktop.",
                "code": "$ brew install syft trivy",
                "lang": "console",
            },
            {
                "say": "Write an SBOM of the image you built on Day 8, then look for your main packages. The full list has about 100 entries, and most of them come from Debian.",
                "code": "$ syft hello-devops:1.0.0 -o spdx-json=sbom.spdx.json\n$ syft hello-devops:1.0.0 -q | grep -E '^(NAME|flask|gunicorn|redis) '\nNAME                     VERSION                            TYPE\nflask                    3.1.3                              python\ngunicorn                 26.2.0                             python\nredis                    8.1.0                              python",
                "lang": "console",
            },
            {
                "say": "Scan it, and show only HIGH and CRITICAL issues that have a fix. My run on 30 October 2026 found 5, all in one group (trimmed).",
                "code": trivy_before,
                "lang": "console",
            },
            {
                "say": "Read the names before you fix anything. msgpack, setuptools and urllib3 are not in your requirements.txt. Instead, pip, the installer, carries its own copies of them. The app needs pip to install packages, not to run. So the fix is to remove pip from the final image.",
            },
            {
                "say": "Add the two `pip uninstall` lines from the Dockerfile in Files, rebuild as 1.2.0, and scan again. The flag `--exit-code 1` makes trivy fail the shell on a finding, the same way it fails CI. Exit code 0 means clean.",
                "code": "$ docker build -t hello-devops:1.2.0 --build-arg APP_VERSION=1.2.0 .\n$ trivy image --severity HIGH,CRITICAL --ignore-unfixed --exit-code 1 hello-devops:1.2.0\n...\n$ echo $?\n0",
                "lang": "console",
            },
            {
                "say": "New CVEs appear every day, so your numbers will differ. When a scan fails, first update: a newer base image or package. Next, remove what you do not need. Only then accept the risk in a `.trivyignore` file, with a reason and a date to look again.",
            },
        ],
    },
    "code": [
        {
            "lang": "yaml",
            "title": ".github/workflows/release.yml (Day 22: scan, SBOM, sign, attest)",
            "src": scratch("release.yml"),
            "run": "git tag v1.2.0 && git push origin v1.2.0",
        },
        {
            "lang": "dockerfile",
            "title": "Dockerfile (Day 22: pip removed from the final image)",
            "src": scratch("Dockerfile"),
            "run": "docker build -t hello-devops:1.2.0 --build-arg APP_VERSION=1.2.0 .",
        },
        {
            "lang": "yaml",
            "title": "policy/disallow-latest-tag.yaml",
            "src": lab("policy/disallow-latest-tag.yaml"),
            "run": "kubectl apply -f policy/disallow-latest-tag.yaml",
        },
        {
            "lang": "yaml",
            "title": "policy/require-run-as-nonroot.yaml",
            "src": lab("policy/require-run-as-nonroot.yaml"),
            "run": "kubectl apply -f policy/require-run-as-nonroot.yaml",
        },
    ],
    "commands": [
        {"cmd": "brew install syft trivy cosign gitleaks", "what": "Install the SBOM, scanning, signing and secret-scanning tools."},
        {"cmd": "syft hello-devops:1.2.0 -o spdx-json=sbom.spdx.json", "what": "Write an SBOM of a local image in SPDX JSON format."},
        {"cmd": "trivy image --severity HIGH,CRITICAL --ignore-unfixed hello-devops:1.2.0", "what": "Scan an image for serious known bugs that already have a fix."},
        {"cmd": "trivy config k8s/", "what": "Check Kubernetes YAML (or a Dockerfile, or Terraform) for risky settings."},
        {"cmd": "gitleaks git -v", "what": "Scan the whole git history of the current repo for secrets."},
        {"cmd": "cosign verify ghcr.io/<your-github-user>/hello-devops:1.2.0 --certificate-identity https://github.com/<your-github-user>/hello-devops/.github/workflows/release.yml@refs/tags/v1.2.0 --certificate-oidc-issuer https://token.actions.githubusercontent.com",
         "what": "Check that the image was signed by your release workflow for tag v1.2.0."},
        {"cmd": "gh attestation verify oci://ghcr.io/<your-github-user>/hello-devops:1.2.0 --owner <your-github-user>",
         "what": "Check the build provenance attestation with the GitHub CLI."},
        {"cmd": "helm repo add kyverno https://kyverno.github.io/kyverno/", "what": "Add the Kyverno chart repository to Helm."},
        {"cmd": "helm install kyverno kyverno/kyverno -n kyverno --create-namespace", "what": "Install Kyverno in its own namespace."},
        {"cmd": "kubectl get validatingpolicies", "what": "List Kyverno ValidatingPolicies and whether they are ready."},
        {"cmd": "kubectl -n hello get policyreports -o wide", "what": "Show pass and fail counts per object from Audit mode policies."},
    ],
    "mistake": (
        "Switching a new policy straight to Deny for the whole cluster. It can block your own deploys, including tools such as Argo CD or the monitoring stack. "
        "Start in Audit and read the PolicyReports for a few days. Fix what they find, then switch to Deny, and scope each policy to the namespaces it is meant for."
    ),
    "real_world": (
        "A payments company has to show auditors what runs in production and where it came from. "
        "CI stores an SBOM and a signed provenance attestation for every release, and the cluster only accepts images signed by the company's release workflow. "
        "When a new critical CVE is announced, the security team searches the stored SBOMs and quickly finds the affected services."
    ),
    "task": {
        "title": "Ship a signed release and guard the cluster",
        "steps": [
            "Update your `Dockerfile` and `.github/workflows/release.yml` to the versions in Files. Build locally and check that trivy passes with `--exit-code 1`.",
            "Commit and push, then tag `v1.2.0` and push the tag. Watch the release run in the Actions tab.",
            "Make the hello-devops package public in its package settings on GitHub, so your kind cluster can pull it later.",
            "Verify the signature with `cosign verify` and the provenance with `gh attestation verify`.",
            "Install Kyverno with Helm, then apply both files from `policy/`.",
            "Run `kubectl -n hello run test --image=nginx:latest` and read the rejection message.",
            "Run `kubectl -n hello get policyreports -o wide`. Which objects fail the runAsNonRoot policy, and why?",
            "Optional: add `securityContext:` with `runAsNonRoot: true` to the Pod spec in `k8s/deployment.yaml`, push, and watch the hello-devops result turn to pass.",
        ],
        "hints": [
            "Artifact attestations are free for public repositories only. On a private repo the attest steps fail, so make the repo public or remove those two steps.",
            "If cosign verify finds no matching signatures, check the identity: your user name, the file name and the tag must match the run exactly.",
            "Redis also fails the runAsNonRoot report. Do not just add the setting: its image starts as root, so the kubelet would refuse to start it. That is why the policy starts in Audit.",
        ],
        "done_when": "`cosign verify` confirms the signature on your 1.2.0 image, and Kyverno rejects the `:latest` Pod.",
    },
    "explain_back": {
        "prompt": "Explain in 3 to 4 sentences how your release now protects the supply chain. Mention scanning, signing and the cluster policy.",
        "answer": (
            "Before anything is pushed, CI scans the image with trivy and stops on serious bugs that have a fix. "
            "After the push, it stores an SBOM and signs the image digest with cosign keyless signing. The signature is tied to my release workflow, and there is no key to leak. "
            "CI also attaches a signed provenance attestation that says which repo, commit and workflow built the image. "
            "In the cluster, Kyverno checks every Pod at admission, so even a hand-made Pod with a :latest image is rejected."
        ),
    },
    "recap": [
        "Shift left: put cheap, automatic security checks where code is written and built, and give everything least privilege.",
        "Supply chain attacks hit what you trust; xz-utils, tj-actions and trivy-action are why you pin and verify.",
        "An SBOM lists every package in an image; trivy finds known bugs and risky configuration.",
        "cosign keyless signing ties a signature to your workflow identity, with no private key to leak.",
        "Provenance records how an artifact was built; GitHub attestations reach SLSA Build Level 2.",
        "Kyverno policies check objects at admission: start in Audit, then switch to Deny.",
    ],
    "check": [
        {
            "q": "A new critical bug is announced in a popular Python library. What answers \"which of our images contain it?\" fastest?",
            "options": [
                "The Dockerfile of each service",
                "The SBOMs stored for each release",
                "The cosign signatures of each image",
                "The Kyverno PolicyReports",
            ],
            "answer": 1,
            "why": "An SBOM lists every package and version in each image, so you can search them directly.",
        },
        {
            "q": "A teammate wants to sign images with a cosign key pair stored as a GitHub secret. What does keyless signing improve?",
            "options": [
                "It makes the image smaller to download",
                "It encrypts the image so nobody can read it",
                "It removes the need for a registry",
                "There is no long-lived key to leak or rotate",
            ],
            "answer": 3,
            "why": "Keyless signing uses a short-lived certificate tied to the workflow's OIDC identity, so no private key is stored anywhere.",
        },
        {
            "q": "You add a policy that blocks Pods without runAsNonRoot, in Deny mode, for all namespaces. What is the most likely problem?",
            "options": [
                "New Pods of tools that run as root are blocked too",
                "Kyverno deletes all running Pods at once",
                "Your images stop being signed in CI",
                "Prometheus can no longer scrape any metrics",
            ],
            "answer": 0,
            "why": "An admission policy applies to every new Pod it matches, so start in Audit and scope it to the right namespaces.",
        },
    ],
    "interview": [
        {
            "q": "What is a software supply chain attack, and how do you defend a CI/CD pipeline against one?",
            "a": (
                "It is an attack on something you depend on, such as a library, a build tool or a CI action, so that your own build ships the attacker's code. "
                "The xz-utils backdoor and the tj-actions/changed-files tag hijack are two recent examples. "
                "I pin third-party actions to commit SHAs, keep workflow tokens to least privilege, and use OIDC instead of long-lived keys. "
                "I also generate SBOMs, scan images, sign them with provenance, and verify signatures before deploying."
            ),
        },
        {
            "q": "What do SBOMs, signatures and provenance each prove?",
            "a": (
                "An SBOM lists what is inside an artifact, which helps you find vulnerable packages fast. "
                "A signature proves who produced the artifact and that it has not changed since. "
                "Provenance says how it was built: which source, commit and build system. SLSA levels describe how far you can trust that record. "
                "None of them proves the code is free of bugs; together they make the path from source to running image checkable."
            ),
        },
    ],
    "deeper": {
        "minutes": 12,
        "body": (
            "Signing only helps if something checks the signature. Today you verify by hand with `cosign verify`. "
            "The next step is to let the cluster check every Pod.\n\n"
            "Kyverno has a policy type for this, ImageValidatingPolicy. You give it:\n"
            "- Which images it covers, for example `ghcr.io/<your-github-user>/*`.\n"
            "- Who must have signed them: your release workflow's identity and the GitHub OIDC issuer, as in `cosign verify`.\n"
            "- Optionally, which attestations must exist, such as SLSA provenance.\n\n"
            "When a Pod arrives, Kyverno looks up the signature in the registry and checks it against those rules. "
            "An unsigned image, or one signed by another workflow, is rejected. "
            "The policy can also replace the tag with the digest it verified, so the node runs exactly the bytes that were checked. Some practical points:\n"
            "- Kyverno needs network access to the registry and to the Sigstore services.\n"
            "- Results are cached, but the first check of a new image adds a short delay.\n"
            "- Start in Audit mode, like any new policy. A typo in the identity would block every deploy.\n\n"
            "Kyverno is not the only option. The Sigstore policy-controller is an admission controller made just for cosign signatures, "
            "and some managed Kubernetes services have their own image trust features.\n\n"
            "Finally, try `trivy config k8s/` on the lab. It flags both Deployments because neither sets a security context, for example: "
            "`KSV-0118 (HIGH): deployment hello-devops in hello namespace is using the default security context, which allows root privileges`. "
            "The runAsNonRoot policy reports the same gap, only later, at the cluster door. "
            "I like having the rule in both places: CI catches it before merge, and the cluster catches whatever skipped CI."
        ),
    },
    "sources": [
        {"title": "SLSA: build track levels", "url": "https://slsa.dev/spec/v1.2/build-track-basics"},
        {"title": "cosign on GitHub", "url": "https://github.com/sigstore/cosign"},
        {"title": "GitHub Docs: artifact attestations for build provenance", "url": "https://docs.github.com/en/actions/security-guides/using-artifact-attestations-to-establish-provenance-for-builds"},
        {"title": "Kyverno: ValidatingPolicy", "url": "https://kyverno.io/docs/policy-types/validating-policy"},
    ],
}
