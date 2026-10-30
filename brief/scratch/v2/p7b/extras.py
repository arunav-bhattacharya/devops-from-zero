"""Part-level items proposed for the second half of Part 7 (Days 35 to 38)."""

EXTRAS = {
    "recap": [
        "Probes decide when to wait, restart or stop traffic; requests place Pods and drive the HPA, and memory over the limit means OOMKilled.",
        "The Gateway API (GatewayClass, Gateway, HTTPRoute) replaces the frozen Ingress API; ingress-nginx was retired in March 2026.",
        "PVCs ask for storage, StorageClasses create it, and StatefulSets give each replica a stable name and its own disk.",
        "Helm packages an app as a chart with values and versioned releases; Kustomize builds each environment as an overlay on a plain base.",
        "Debug bottom-up with get, describe, logs `--previous`, events and EndpointSlices; Forbidden means RBAC, checked with `kubectl auth can-i`.",
    ],
    "flashcards": [
        {"front": "What happens when a readiness probe fails? And a liveness probe?", "back": "Readiness: the Pod leaves the Service's endpoints but keeps running. Liveness: the kubelet restarts the container."},
        {"front": "A container shows OOMKilled and exit code 137. What happened?", "back": "It used more memory than its limit, so the kernel killed it with SIGKILL (128 + 9)."},
        {"front": "What does a container at its CPU limit experience?", "back": "Throttling: it keeps running, only slower. It is not killed."},
        {"front": "What two things does a CPU-based HPA need?", "back": "metrics-server (with `--kubelet-insecure-tls` on kind) and CPU requests on the Pods."},
        {"front": "What does a PodDisruptionBudget protect against, and what not?", "back": "It limits planned disruptions such as `kubectl drain`; it cannot stop a node crash."},
        {"front": "Name the three main Gateway API objects and who usually owns each.", "back": "GatewayClass (platform team), Gateway (cluster operators), HTTPRoute (app teams)."},
        {"front": "What does kind's `standard` StorageClass do when you delete a PVC?", "back": "Its reclaim policy is Delete, so the PV and the data folder are deleted too."},
        {"front": "What does `helm rollback app 1` write into the history?", "back": "A new revision with the content of revision 1, described as \"Rollback to 1\"."},
        {"front": "Why can a Kustomize overlay not live inside its base folder?", "back": "Kustomize refuses it as a cycle: the base would contain the overlay."},
        {"front": "A Pod is in CreateContainerConfigError and its logs are empty. Where do you look?", "back": "In `kubectl describe pod` Events: usually a missing ConfigMap, Secret or key."},
    ],
    "quiz": [
        {
            "q": "An HPA targets 70m CPU per Pod (70% of a 100m request). 4 Pods now average 105m. How many replicas will it ask for, if `maxReplicas` is 10?",
            "options": ["4", "5", "6", "8"],
            "answer": 2,
            "why": "ceil(4 * 105 / 70) = ceil(6.0) = 6.",
        },
        {
            "q": "You want 20% of requests to reach a new version of the checkout service, through the existing Gateway. Which object do you change?",
            "options": [
                "The HTTPRoute: two backendRefs with weights 80 and 20",
                "The GatewayClass: a second controller for the new version",
                "The Gateway: a second listener on another port",
                "The Deployment: replicas set to 20% of the old count",
            ],
            "answer": 0,
            "why": "Traffic splitting is a routing rule, so it lives in the HTTPRoute as weighted backends.",
        },
        {
            "q": "Every Pod of a Service is Running and 1/1 Ready, but requests to the Service fail, and its EndpointSlice shows `<unset>`. What is the most likely cause?",
            "options": [
                "The readiness probe is too strict",
                "The memory limit is too low",
                "The image tag does not exist",
                "The Service selector does not match the Pods' labels",
            ],
            "answer": 3,
            "why": "Ready Pods that are missing from the endpoints are not selected at all, which points at the selector (or the targetPort).",
        },
        {
            "q": "Your team installs Envoy Gateway and a monitoring stack, and also deploys its own small service to dev and prod. Which split fits best?",
            "options": [
                "Kustomize for everything, including the third-party tools",
                "Helm charts for the third-party tools, Kustomize overlays for your service",
                "Copies of every YAML file per environment",
                "One Helm chart that bundles all three together",
            ],
            "answer": 1,
            "why": "Third-party projects ship and support Helm charts, while overlays keep a team's own few differences as plain, readable YAML.",
        },
        {
            "q": "Helm stores every revision of a release in the cluster, so it can show history and roll back. Which part of Terraform plays the same role of remembering what was deployed?",
            "options": [
                "The provider block",
                "The `.terraform.lock.hcl` file",
                "The state file",
                "The variables file",
            ],
            "answer": 2,
            "why": "Terraform's state records what it created, just as Helm's release Secrets record what each revision applied.",
            "from": "Part 6",
        },
    ],
    "resources": [
        {"title": "Debug Pods (Kubernetes docs)", "url": "https://kubernetes.io/docs/tasks/debug/debug-application/debug-pods/", "kind": "docs", "why": "The official checklist for Pods that will not start or keep crashing, with example output."},
        {"title": "A visual guide on troubleshooting Kubernetes deployments (Learnkube)", "url": "https://learnkube.com/troubleshooting-deployments", "kind": "read", "why": "One big flowchart from Pod to Service to Ingress that you can keep open while debugging."},
        {"title": "Gateway API project site", "url": "https://gateway-api.sigs.k8s.io/", "kind": "docs", "why": "Guides for every route type, the Standard and Experimental channels, and a list of implementations."},
        {"title": "Helm 4 overview", "url": "https://helm.sh/docs/overview", "kind": "docs", "why": "What changed from Helm 3, including server-side apply and the renamed flags you will meet in old scripts."},
        {"title": "Helm vs Kustomize: the fight between templating and patching (DevOps Toolkit)", "url": "https://www.youtube.com/watch?v=ZMFYSm0ldQ0", "kind": "watch", "why": "A side-by-side look at both tools on the same app, to help you choose."},
        {"title": "7 common Kubernetes pitfalls (Kubernetes blog)", "url": "https://kubernetes.io/blog/2025/10/20/seven-kubernetes-pitfalls-and-how-to-avoid/", "kind": "read", "why": "Missing requests, bad probes and loose RBAC, each with what to do instead."},
    ],
}
