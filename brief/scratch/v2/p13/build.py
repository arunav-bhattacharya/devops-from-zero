#!/usr/bin/env python3
"""Build content/p13.json (Part 13: DevSecOps) from the lesson modules in this folder.
Lab files (policy/, security/, release.yml) are read at build time, so lessons and lab stay in sync."""
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

import d52  # noqa: E402
import d53  # noqa: E402

OUT = pathlib.Path("/home/user/devops-from-zero/content/p13.json")

part = {
    "part": 13,
    "title": "DevSecOps",
    "intro": (
        "Part 13 adds security to everything you have built. "
        "Day 52 follows the software supply chain from a git tag to a signed image you can verify, with three real attacks as the map. "
        "Day 53 protects what runs: secrets, access rights, and rules the cluster checks at the door. "
        "It comes this late on purpose, because you can only secure a pipeline and a cluster you understand."
    ),
    "lessons": [d52.lesson, d53.lesson],
    "recap": [
        "Your supply chain is every library, image, tool and CI action between your keyboard and production.",
        "xz-utils (2024), tj-actions (2025) and Trivy (2026) hit a maintainer, an action's tags and a security tool.",
        "Pin actions to full commit SHAs and images to digests, and let Dependabot keep the pins fresh.",
        "SBOMs list what you ship; scanners match them against CVEs at build time and again later.",
        "cosign keyless signing and GitHub attestations prove who built an image and how (SLSA Build L2).",
        "Verification makes all of it count: cosign verify, gh attestation verify, and later an admission policy.",
        "A Secret is only base64, anyone who can create Pods in its namespace can read it, and leaked values must be rotated.",
        "Real values live in a secrets manager; ESO, Sealed Secrets or SOPS bring them in without plain values in git.",
        "RBAC decides who may act; Pod Security Admission and Kyverno decide which objects are acceptable.",
    ],
    "flashcards": [
        {"front": "Why is a version tag like @v4 not enough to trust an action?", "back": "A tag is a movable pointer. Whoever controls the repository can point it at new code."},
        {"front": "What does a full commit SHA guarantee?", "back": "It always names the same code, because it is a hash of the commit's content."},
        {"front": "What is an SBOM?", "back": "A machine-readable list of every package and version inside an artifact."},
        {"front": "What are the two standard SBOM formats?", "back": "SPDX and CycloneDX."},
        {"front": "Why re-scan an old SBOM?", "back": "New CVEs are published every day against packages you already shipped."},
        {"front": "What makes cosign signing keyless?", "back": "A 10-minute certificate tied to the workflow's OIDC identity, so no private key is stored."},
        {"front": "What are Fulcio and Rekor?", "back": "Sigstore's certificate authority, and its public log of signing events."},
        {"front": "Which SLSA build level do GitHub artifact attestations give?", "back": "Build L2. Building in a shared reusable workflow can reach L3."},
        {"front": "What does provenance record?", "back": "How an artifact was built: repository, commit, workflow and build platform."},
        {"front": "Is a Kubernetes Secret encrypted?", "back": "No. Its values are base64 encoded, and etcd stores them unencrypted by default."},
        {"front": "Who can read a Secret without get on secrets?", "back": "Anyone who can create Pods or workloads in its namespace, and anyone with list or watch on Secrets."},
        {"front": "A token was committed, then deleted in the next commit. What now?", "back": "Rotate it. Git history keeps it, in every clone and fork."},
        {"front": "gitleaks dir or gitleaks git: which finds a deleted secret?", "back": "gitleaks git, because it reads the whole history. dir only reads current files."},
        {"front": "With External Secrets Operator, which file goes in git?", "back": "The ExternalSecret. It names a key in the secrets manager, not the value."},
        {"front": "Why avoid * in RBAC rules?", "back": "It also grants every resource type that is added to the cluster later."},
        {"front": "What are the three Pod Security levels?", "back": "privileged, baseline and restricted."},
        {"front": "Does Pod Security enforce mode reject a bad Deployment?", "back": "No. It accepts the Deployment and rejects its Pods. Warn mode shows the problem at apply time."},
        {"front": "Kyverno: Audit or Deny, which one blocks the request?", "back": "Deny. Audit allows it and records a failure in a PolicyReport."},
        {"front": "Which Kyverno type replaces ClusterPolicy for validation?", "back": "ValidatingPolicy (policies.kyverno.io/v1), with checks written in CEL."},
    ],
    "resources": [
        {"title": "Aqua advisory: Trivy ecosystem compromise (CVE-2026-33634)", "url": "https://github.com/aquasecurity/trivy/security/advisories/GHSA-69fq-xp46-6x23", "kind": "read",
         "why": "The attacked vendor's own timeline, with exposure windows, safe versions and what to rotate."},
        {"title": "XZ Exploit (Computerphile)", "url": "https://www.youtube.com/watch?v=LY8_35a_DEA", "kind": "watch",
         "why": "A calm explanation of how a trusted contributor hid a backdoor in a library almost every Linux system uses."},
        {"title": "GitHub Docs: secure use reference for Actions", "url": "https://docs.github.com/en/actions/reference/security/secure-use", "kind": "docs",
         "why": "GitHub's own rules for third-party actions: SHA pins, lockfiles, and checking that a SHA is not from a fork."},
        {"title": "SLSA spec: build track basics", "url": "https://github.com/slsa-framework/slsa/blob/main/spec/build-track-basics.md", "kind": "docs",
         "why": "What each build level promises and which attacks it stops, straight from the spec."},
        {"title": "cosign README", "url": "https://github.com/sigstore/cosign/blob/main/README.md", "kind": "docs",
         "why": "Keyless signing and verification in a few commands, plus the warnings about digests and public logs."},
        {"title": "From Cosign to an ecosystem: the evolution of Sigstore (Cody Soyland, GitHub)", "url": "https://www.youtube.com/watch?v=hsHeZRFj5jc", "kind": "watch",
         "why": "How Sigstore grew from one signing tool into the base of GitHub's artifact attestations."},
        {"title": "Kubernetes docs: role-based access control good practices", "url": "https://kubernetes.io/docs/concepts/security/rbac-good-practices/", "kind": "docs",
         "why": "The official list of rights that are more powerful than they look, such as creating Pods."},
        {"title": "Kubernetes security best practices you need to know (TechWorld with Nana)", "url": "https://www.youtube.com/watch?v=oBf5lrmquYI", "kind": "watch",
         "why": "A visual tour of image scanning, RBAC, network policies and secrets on Kubernetes."},
        {"title": "Kyverno quick start (source on GitHub)", "url": "https://github.com/kyverno/website/blob/main/src/content/docs/docs/introduction/quick-start.md", "kind": "docs",
         "why": "Install Kyverno and write a first CEL ValidatingPolicy, in the current 1.19 style."},
        {"title": "Open Policy Agent intro and deep dive, KubeCon EU 2026 (Charlie Egan and Anders Eknert)", "url": "https://www.youtube.com/watch?v=TENlj4r6IXk", "kind": "watch",
         "why": "The maintainers explain Rego and Gatekeeper, the main alternative to Kyverno."},
        {"title": "External Secrets Operator: getting started", "url": "https://github.com/external-secrets/external-secrets/blob/main/docs/introduction/getting-started.md", "kind": "docs",
         "why": "How SecretStores and ExternalSecrets fit together, and how to install the operator with Helm."},
    ],
    "quiz": [
        {
            "q": "Which step in the lab's release.yml stops a release whose image has a HIGH CVE with a fix available?",
            "options": ["The cosign signing step", "The Trivy scan step", "The SBOM step", "The attestation step"],
            "answer": 1,
            "why": "The Trivy step runs with severity HIGH and CRITICAL, ignore-unfixed and exit code 1, before anything is pushed.",
        },
        {
            "q": "Your image passed the scan with zero findings on release day. Two months later, what tells you whether it is still safe?",
            "options": ["Re-scanning its stored SBOM", "Checking its cosign signature", "Reading the old workflow log", "Comparing the image size"],
            "answer": 0,
            "why": "New CVEs appear after release, so you match the stored SBOM against today's vulnerability data.",
        },
        {
            "q": "You run cosign verify with the identity of release.yml at tag v1.2.0, but the image was signed by the run for v1.2.1. What happens?",
            "options": [
                "It passes, because the repository matches",
                "It passes, but prints a warning",
                "It fails: no matching signature",
                "It signs the image again for v1.2.0",
            ],
            "answer": 2,
            "why": "The certificate identity includes the git ref, so a signature from another tag does not match.",
        },
        {
            "q": "Which statement about GitHub artifact attestations is true?",
            "options": [
                "They prove the image has no vulnerabilities",
                "They give SLSA Build L2, if someone verifies",
                "They need a private key stored as a secret",
                "They only work in private repositories",
            ],
            "answer": 1,
            "why": "They are keyless Sigstore attestations at Build L2, and GitHub says they add nothing until they are verified.",
        },
        {
            "q": "A developer may create Pods in namespace billing but has no rule for Secrets. Can they learn the database password stored there?",
            "options": [
                "No, RBAC blocks every path to it",
                "Only if they are a cluster admin",
                "Only if etcd encryption is off",
                "Yes, by mounting it in a Pod",
            ],
            "answer": 3,
            "why": "A Pod they create can load any Secret in the namespace, so Pod creation implies Secret access.",
        },
        {
            "q": "Which of these files is safe to commit to a public repository?",
            "options": [
                "A Secret YAML with base64 values",
                "A .env file with the real token",
                "An ExternalSecret that names a key",
                "A kubeconfig with a token inside",
            ],
            "answer": 2,
            "why": "An ExternalSecret only points at a key in the secrets manager; the value never enters git.",
        },
        {
            "q": "You want to stop :latest images in namespace hello, but only after teams fix their manifests. How do you start?",
            "options": [
                "A ValidatingPolicy in Audit mode",
                "A ValidatingPolicy in Deny mode",
                "A Pod Security enforce label",
                "A Role without the create verb",
            ],
            "answer": 0,
            "why": "Audit records failures in PolicyReports without blocking, so teams can fix things before you switch to Deny.",
        },
        {
            "q": "Kyverno is installed. Which question can it answer that RBAC cannot?",
            "options": [
                "May this user create Pods here?",
                "Does this Pod's image use a fixed tag?",
                "Which groups does this user belong to?",
                "Who issued this user's certificate?",
            ],
            "answer": 1,
            "why": "RBAC checks who may do which verb on which resource type; admission policies look inside the object itself.",
        },
        {
            "q": "In GitHub Actions, why does the release job declare its own permissions: block?",
            "options": [
                "To give its token only the rights it needs",
                "To make the job start faster on the runner",
                "Because GHCR rejects read-only tokens",
                "Because OIDC tokens require write-all",
            ],
            "answer": 0,
            "why": "Least privilege: the default stays read-only, and only this job may push packages, mint OIDC tokens and write attestations.",
            "from": "Part 4",
        },
        {
            "q": "A Deployment's Pods are refused by Pod Security, so none start. Which command shows the reason fastest?",
            "options": [
                "kubectl logs on the Deployment",
                "kubectl top pods in the namespace",
                "kubectl rollout undo on it",
                "kubectl get events in the namespace",
            ],
            "answer": 3,
            "why": "No Pod exists to have logs; the ReplicaSet's FailedCreate event carries the Pod Security message.",
            "from": "Part 7",
        },
    ],
}

OUT.write_text(json.dumps(part, indent=1, ensure_ascii=False) + "\n")
print(f"wrote {OUT}")
