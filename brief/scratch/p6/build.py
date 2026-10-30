#!/usr/bin/env python3
"""Build content/p6.json (Part 6: Modern DevOps) from the lesson modules in this folder."""
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

import d20  # noqa: E402
import d21  # noqa: E402
import d22  # noqa: E402
import d23  # noqa: E402

OUT = pathlib.Path("/home/user/devops-from-zero/content/p6.json")

part = {
    "part": 6,
    "title": "Modern DevOps: what's trending",
    "intro": (
        "Part 6 connects everything you built and looks at where DevOps is heading. "
        "You let Argo CD deploy from git, watch hello-devops with Prometheus and Grafana, and lock down your supply chain with scanning, signing and policies. "
        "Then you meet platform engineering, FinOps and AI agents, and ship hello-devops end to end in the capstone."
    ),
    "lessons": [d20.lesson, d21.lesson, d22.lesson, d23.lesson],
    "recap": [
        "GitOps keeps the desired state in git; Argo CD pulls it, applies it and undoes drift.",
        "New versions ship by changing an image tag in git, and roll back with git revert.",
        "Prometheus scrapes metrics, Grafana shows them, and a ServiceMonitor tells Prometheus where to look.",
        "Logs go to stdout and on to a store like Loki; traces and OpenTelemetry show one request's path.",
        "SLOs and error budgets turn reliability into a number the team can plan with.",
        "Your release now scans, writes an SBOM, signs keylessly and attests provenance; Kyverno checks Pods at the door.",
        "Platform engineering, FinOps and AI agents with guardrails are where many teams are heading.",
        "The capstone ships hello-devops from a commit to a signed, observed, GitOps-managed deploy.",
    ],
    "flashcards": [
        {"front": "What are the four OpenGitOps principles?", "back": "Declarative; versioned and immutable; pulled automatically; continuously reconciled."},
        {"front": "In Argo CD, what does selfHeal do?", "back": "It undoes changes made in the cluster that are not in git."},
        {"front": "In Argo CD, what does prune do?", "back": "It deletes objects from the cluster after you remove them from git."},
        {"front": "How do you roll back an app that Argo CD syncs automatically?", "back": "Revert the commit in git and push. Argo CD deploys the old state."},
        {"front": "Why does the lab's Application ignore /spec/replicas?", "back": "So Argo CD does not fight the autoscaler, which changes replicas while the app runs."},
        {"front": "Does Prometheus push or pull metrics?", "back": "It pulls: it scrapes each target's /metrics page on a schedule."},
        {"front": "What does rate(hello_requests_total[5m]) return?", "back": "Requests per second, averaged over the last 5 minutes."},
        {"front": "Why can kube-prometheus-stack ignore your ServiceMonitor?", "back": "It lacks the release label of the Helm release, or its selector matches no Service."},
        {"front": "What are the four golden signals?", "back": "Latency, traffic, errors and saturation."},
        {"front": "What is an error budget?", "back": "The failure an SLO allows, such as 0.1% of requests for a 99.9% SLO."},
        {"front": "What is an SBOM?", "back": "A list of every package and version inside an artifact."},
        {"front": "What makes cosign signing keyless?", "back": "A short-lived certificate tied to the workflow's OIDC identity, so no private key is stored."},
        {"front": "Which SLSA build level do GitHub artifact attestations give?", "back": "Build Level 2. A shared reusable workflow can reach Level 3."},
        {"front": "Audit or Deny: which mode blocks the object in a Kyverno policy?", "back": "Deny blocks it. Audit allows it and records a failure in a PolicyReport."},
        {"front": "What is a golden path?", "back": "A supported, ready-made way to do a common task, offered as self-service."},
        {"front": "Name three guardrails for AI agents.", "back": "Read-only by default, narrow short-lived credentials, and human review of every change."},
    ],
    "quiz": [
        {
            "q": "A teammate changes a Deployment's image by hand to test a fix. Argo CD has selfHeal on. What happens next?",
            "options": [
                "The hand edit stays until the next git commit",
                "Argo CD puts git's image back shortly after",
                "Argo CD deletes the Deployment for good",
                "The app stays OutOfSync until someone clicks Sync",
            ],
            "answer": 1,
            "why": "Self-heal syncs the live object back to git's version, so hand edits do not last.",
        },
        {
            "q": "Prometheus shows hello_requests_total jumping between 5 and 1 on each scrape. What is the likely cause?",
            "options": [
                "Two gunicorn workers each keep their own counter",
                "Grafana is caching old values from yesterday",
                "The ServiceMonitor interval is far too short",
                "Redis is down, so the counter is lost",
            ],
            "answer": 0,
            "why": "Each worker process has its own counter and a scrape reaches only one; run one worker per pod or use multiprocess mode.",
        },
        {
            "q": "Which signal best shows where one slow checkout request spent its time across three services?",
            "options": [
                "A gauge of memory in use",
                "A counter of total requests",
                "Logs from the load balancer only",
                "A trace made of spans",
            ],
            "answer": 3,
            "why": "A trace follows one request through every service, with a timed span for each step.",
        },
        {
            "q": "Your release fails at the trivy step with three HIGH issues that have fixes. What is the best first move?",
            "options": [
                "Delete the trivy step from the workflow",
                "Find which packages they are in, then update or remove them",
                "Set exit-code to 0 so it never fails again",
                "Sign the image anyway and fix it next month",
            ],
            "answer": 1,
            "why": "Triage first: update or remove the affected packages, and accept a risk only on purpose, with a reason.",
        },
        {
            "q": "Which command proves that your release workflow signed the image?",
            "options": [
                "docker inspect ghcr.io/you/app:1.2.0",
                "trivy image ghcr.io/you/app:1.2.0",
                "cosign verify ghcr.io/you/app:1.2.0 plus identity flags",
                "syft ghcr.io/you/app:1.2.0 -o spdx-json",
            ],
            "answer": 2,
            "why": "cosign verify checks the signature against the expected workflow identity and the GitHub OIDC issuer.",
        },
        {
            "q": "Why does release.yml pin trivy-action to a full commit SHA instead of @v0.36.0?",
            "options": [
                "A SHA makes the workflow run faster",
                "GitHub no longer accepts tags in uses:",
                "Dependabot can only update SHA pins",
                "A tag can be moved to new code; a SHA cannot",
            ],
            "answer": 3,
            "why": "Tags are movable pointers, as the tj-actions and trivy-action attacks showed; a full SHA always means the same code.",
            "from": "Part 3",
        },
        {
            "q": "Argo CD syncs hello-devops with selfHeal on, and nothing is ignored. Under load, the HPA raises replicas to 5. What happens?",
            "options": [
                "Argo CD and the HPA keep changing the count back and forth",
                "The HPA stops working until you restart it",
                "Kubernetes deletes the HPA to resolve the conflict",
                "Nothing, because Argo CD never compares replicas",
            ],
            "answer": 0,
            "why": "Both controllers want to own spec.replicas; ignoring that field in Argo CD lets the HPA own it.",
            "from": "Part 5",
        },
        {
            "q": "Which setup lets an AI agent help on-call without putting production at risk?",
            "options": [
                "A cluster admin key, kept for emergencies",
                "A shared human account with MFA turned off",
                "Read-only access, short-lived token, reviewed changes",
                "Full access, plus a prompt that says be careful",
            ],
            "answer": 2,
            "why": "Narrow, short-lived, read-only access plus human review limits damage, whatever the agent is told.",
        },
    ],
}

OUT.write_text(json.dumps(part, ensure_ascii=False, indent=1) + "\n")
print(f"wrote {OUT}")
