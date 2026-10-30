# Kubernetes and GitOps with Argo CD: what a beginner needs, current as of October 30, 2026

> **How URLs were verified.** Each source is tagged.
> - **[S]**: the URL appeared in a WebSearch result in this session.
> - **[R]**: I opened the URL itself, via `git clone`/`git ls-remote` or `curl` against github.com or raw.githubusercontent.com.
> - **[G]**: I read the page's source file in the project's GitHub repo (cloned this session). The URL is the site's standard mapping of that source path:
>   - kubernetes.io: `content/en/docs/X.md` maps to `https://kubernetes.io/docs/X/`. Blog posts map to `/blog/YYYY/MM/DD/<slug>/` from the front matter. The 1.37 release post links its own blog post that way, and search results show the same pattern.
>   - Argo CD: `docs/X.md` maps to `https://argo-cd.readthedocs.io/en/stable/X/`.
>   - kind: `site/content/docs/user/X.md` maps to `https://kind.sigs.k8s.io/docs/user/X/`.
> - **[L]**: the URL appears as a hyperlink inside a source document I read.
> - Lesson codes: **K1–K9** are the Kubernetes lessons and **G1–G2** are the GitOps lessons.
> - "(doc)" marks expected output copied from official docs. "(illustrative)" marks typical output written from experience, which the writer should confirm on a real cluster.
> - The Argo CD docs were read from the `master` branch (3.7 in development). The "stable" site serves 3.5.x.
> - YouTube was unreachable from the sandbox, so I list only video URLs that appeared in search results. A channel is named only where the search results supported it.

## Q1. What intuitions help, and what should each lesson teach (concepts in teaching order, examples, resources)?

### Takeaway
Four intuitions recur across the whole course:
- Kubernetes is a set of control loops that keep pushing actual state toward a declared desired state (the docs' own analogy is a thermostat).
- Pods are disposable.
- Services give Pods a stable address.
- Labels and selectors are the glue: they connect Deployments to ReplicaSets to Pods, and Services, NetworkPolicies, PDBs and affinity to Pods.

GitOps applies the same control-loop idea one level up: Git holds the desired state, and Argo CD is the controller.

### Cited Findings

#### Cross-lesson intuitions (open K1 with these and keep returning to them)
- **Desired state and control loops.** The docs explain a controller with a thermostat. Setting the temperature declares the *desired state*, the room's temperature is the *current state*, and the thermostat acts to bring current toward desired. Kubernetes objects carry a `spec` field that holds the desired state. — [Controllers](https://kubernetes.io/docs/concepts/architecture/controller/) [G]
- **Pods as cattle.** "Pods are designed as relatively ephemeral, disposable entities." You rarely create Pods directly; controllers create and replace them. — [Pods](https://kubernetes.io/docs/concepts/workloads/pods/) [G]
- **Labels as glue.** Labels are "identifying attributes of objects". Non-identifying data belongs in annotations. — [Labels and Selectors](https://kubernetes.io/docs/concepts/overview/working-with-objects/labels/) [G]; [Annotations](https://kubernetes.io/docs/concepts/overview/working-with-objects/annotations/) [G]
- A ReplicaSet "identifies new Pods to acquire by using its selector". Ownership comes from label matching plus `ownerReferences`. — [ReplicaSet](https://kubernetes.io/docs/concepts/workloads/controllers/replicaset/) [G]
- **Services as stable addresses.** A Service selects Pods by label, and EndpointSlices track the matching Pod IPs. By default each slice holds at most 100 endpoints. — [Service](https://kubernetes.io/docs/concepts/services-networking/service/) [G]; [EndpointSlices](https://kubernetes.io/docs/concepts/services-networking/endpoint-slices/) [G]
- **GitOps as the same loop one level up.** The OpenGitOps principles say desired state must be:
  1. Declarative.
  2. Versioned and Immutable: "stored in a way that enforces immutability, versioning and retains a complete version history".
  3. Pulled Automatically: "software agents automatically pull the desired state declarations from the source".
  4. Continuously Reconciled: agents "continuously observe actual system state and attempt to apply the desired state".
  — [OpenGitOps PRINCIPLES.md](https://github.com/open-gitops/documents/blob/main/PRINCIPLES.md) [R]; [OpenGitOps 1.0 announcement](https://opengitops.dev/blog/1.0-announcement) [S]
- One secondary summary notes that a floating reference such as a `latest` tag is "no longer versioned because there is no way to rollback changes". This ties the `:latest` pitfall to GitOps principle 2. — summarized in search results that cite [OpenGitOps 1.0 announcement](https://opengitops.dev/blog/1.0-announcement) [S]

---

#### K1. Why Kubernetes and cluster architecture

**Concepts in teaching order.** Each has a one-line explanation and an intuition.
1. **The problem.** Many containers on many machines need placement, restarts, networking and safe updates. *Intuition: you stop managing servers and start declaring outcomes.*
2. **Declarative API objects with `spec` (desired) and `status` (observed).** *Intuition: you write a wish, and the cluster writes back a report.* — [Controllers](https://kubernetes.io/docs/concepts/architecture/controller/) [G]
3. **Controllers and control loops.** Each controller watches one kind of object and nudges reality toward its spec. *Intuition: a thermostat.* — same source.
4. **Control plane.** The doc's "Control Plane Components" section covers kube-apiserver, etcd, kube-scheduler, kube-controller-manager and cloud-controller-manager. — [Cluster components](https://kubernetes.io/docs/concepts/overview/components/) [G]
   - API server: the front door. Every client, including kubectl and the controllers, talks only to it.
   - etcd: the cluster's database.
   - Scheduler: picks a node for each unscheduled Pod.
   - Controller manager: runs the built-in loops.
5. **Node components.** The doc's "Node Components" section covers the kubelet (turns Pod specs into running containers via the runtime), the container runtime (containerd) and kube-proxy (programs Service routing).
6. **Addons.** The doc's "Addons" section covers cluster DNS (CoreDNS), the network plugin (CNI) and metrics.
   - CoreDNS has been the default DNS addon since v1.13.
   - kube-dns is deprecated in 1.37, and no new kube-dns packages are expected after v1.40. — [K8s v1.37 release](https://kubernetes.io/blog/2026/08/26/kubernetes-v1-37-release/) [G]
7. **kind ("Kubernetes in Docker").** Each node is a Docker container.
   - kind v0.33.0 (tagged Aug 26, 2026) uses the default node image `kindest/node:v1.37.0`. — [kind repo, `pkg/apis/config/defaults/image.go` at tag v0.33.0](https://github.com/kubernetes-sigs/kind) [R]
   - The release bumped the node image to containerd v2.3.4 and runc v1.4.3 (commit "Bump to containerd v2.3.4 and runc v1.4.3", Aug 19, 2026). — kind git log [R]
8. **Release cadence.** About three minor releases a year:

   | Version | Release date |
   |---|---|
   | v1.33 | Apr 23, 2025 |
   | v1.34 | Aug 27, 2025 |
   | v1.35 | Dec 17, 2025 |
   | v1.36 | Apr 22, 2026 |
   | v1.37 "Garhwal" | Aug 26, 2026 |

   Sources: [1.33](https://kubernetes.io/blog/2025/04/23/kubernetes-v1-33-release/) [G], [1.34](https://kubernetes.io/blog/2025/08/27/kubernetes-v1-34-release/) [G], [1.35](https://kubernetes.io/blog/2025/12/17/kubernetes-v1-35-release/) [G], [1.36](https://kubernetes.io/blog/2026/04/22/kubernetes-v1-36-release/) [G], [1.37](https://kubernetes.io/blog/2026/08/26/kubernetes-v1-37-release/) [G]; [sig-release 1.37 schedule](https://github.com/kubernetes/sig-release/blob/master/releases/release-1.37/README.md) [S].
   - The newest patch tag is v1.37.2. — `git ls-remote` of [kubernetes/kubernetes](https://github.com/kubernetes/kubernetes) [R]

**Example commands.**
```bash
brew install kind            # macOS via Homebrew (kind quick-start)
kind create cluster          # creates context "kind-kind"
kubectl cluster-info --context kind-kind
kind get clusters
docker ps                    # the "node" is a container named kind-control-plane
kubectl get nodes -o wide
kubectl get pods -n kube-system -o wide
kind delete cluster
```
- `brew install kind`, `kind get clusters`, `kubectl cluster-info --context kind-kind` and `kind delete cluster` all appear in the [kind quick start](https://kind.sigs.k8s.io/docs/user/quick-start/) [L]. It also offers a `kind-darwin-arm64` binary for Apple Silicon.
- Expected `kubectl get nodes` output (illustrative):
  ```
  NAME                 STATUS   ROLES           AGE   VERSION
  kind-control-plane   Ready    control-plane   1m    v1.37.0
  ```
- Expected kube-system Pods (illustrative): `etcd-kind-control-plane`, `kube-apiserver-kind-control-plane`, `kube-controller-manager-kind-control-plane`, `kube-scheduler-kind-control-plane`, two `coredns-…`, `kindnet-…`, `kube-proxy-…`. A separate `local-path-storage` namespace holds the storage provisioner.

**Resources**
- [Cluster Architecture: Controllers](https://kubernetes.io/docs/concepts/architecture/controller/) [G]
- [Kubernetes Components](https://kubernetes.io/docs/concepts/overview/components/) [G]
- [kind Quick Start](https://kind.sigs.k8s.io/docs/user/quick-start/) [L]
- [Kubernetes The Hard Way (Kelsey Hightower)](https://github.com/kelseyhightower/kubernetes-the-hard-way) [R]: "optimized for learning". It currently targets Kubernetes v1.32.x, containerd v2.1.x and etcd v3.6.x, and needs four ARM64 or AMD64 machines. Use it as optional reading for the curious, not as a lesson exercise.
- [Kubernetes v1.37 release post](https://kubernetes.io/blog/2026/08/26/kubernetes-v1-37-release/) [G]
- Video: [Complete Kubernetes Tutorial for Beginners (playlist)](https://www.youtube.com/playlist?list=PLy7NrYWoggjziYQIDorlXjTvvwweTYoNC) [S]. The search did not show the channel; it is possibly TechWorld with Nana's series, unverified. TechWorld with Nana's 4-hour course (published November 2020) is described in [Class Central's listing](https://classcentral.com/course/youtube-kubernetes-tutorial-for-beginners-full-course-in-4-hours-108866) [S]. It predates most items in Q3.
- Video: [Kubernetes Tutorial For Beginners (Full Course From KubeAcademy)](https://www.youtube.com/watch?v=JB3bP1RXqYo) [S]

---

#### K2. Pods, kubectl and YAML

**Concepts in teaching order**
1. **Pod.** The smallest deployable unit: one or more containers that share network and storage. *Intuition: a pod of whales, or containers that move together.* Pods are ephemeral and disposable. — [Pods](https://kubernetes.io/docs/concepts/workloads/pods/) [G]
2. **YAML anatomy.** Every object has `apiVersion`, `kind`, `metadata` (name, namespace, labels, annotations) and `spec`. Use `kubectl explain` to discover fields, e.g. `kubectl explain pod.spec.containers.livenessProbe`.
3. **Pod phases.** There are five, and they are the *data model*, not the STATUS column:

   | Phase | Meaning (doc) |
   |---|---|
   | `Pending` | Accepted, but not all containers are set up. Includes scheduling time and image download. |
   | `Running` | Bound to a node and all containers created; at least one running or (re)starting. |
   | `Succeeded` | All containers exited successfully and won't restart. |
   | `Failed` | All containers terminated and at least one failed. |
   | `Unknown` | The Pod's state can't be obtained, usually because the node is unreachable. |

   - `CrashLoopBackOff` and `Terminating` appear in kubectl's STATUS column but are *not phases*. The docs say not to confuse the "Status" display field with the phase. — [Pod Lifecycle](https://kubernetes.io/docs/concepts/workloads/pods/pod-lifecycle/) [G]
4. **Restart policy.** `Always` (default), `OnFailure` or `Never`.
   - The kubelet restarts containers *in the same Pod on the same node* with exponential backoff: 10s, 20s, 40s and so on, capped at 300s (5 min).
   - After a container runs 10 minutes without problems, the backoff resets.
   - Newer: individual containers can override with container-level `restartPolicy` and `restartPolicyRules`, e.g. "only restart if exit code 42". Fine-grained container restart rules are Beta in 1.35. — [Pod Lifecycle](https://kubernetes.io/docs/concepts/workloads/pods/pod-lifecycle/) [G]; [1.35 release](https://kubernetes.io/blog/2025/12/17/kubernetes-v1-35-release/) [G]
5. **Init containers.** They run to completion, in order, before app containers start. Use them for setup work, such as waiting for a dependency or rendering config. — [Init Containers](https://kubernetes.io/docs/concepts/workloads/pods/init-containers/) [G]
6. **Sidecar containers.** These are "a special class of init containers with `restartPolicy: Always`". GA in 1.33.
   - They start before app containers, run for the Pod's whole life and terminate after the main containers exit.
   - They support probes.
   - *Intuition: a helper that rides along (log shipper, proxy).* — [1.33 release](https://kubernetes.io/blog/2025/04/23/kubernetes-v1-33-release/) [G]; [Sidecar Containers](https://kubernetes.io/docs/concepts/workloads/pods/sidecar-containers/) [G]; [Multi-container patterns blog](https://kubernetes.io/blog/2025/04/22/multi-container-pods-overview/) [G]
7. **Labels vs annotations.** Labels are identifying, used by selectors. Annotations are non-identifying metadata used by tools, e.g. `kubernetes.io/change-cause` and Argo CD's tracking annotation. — [Labels](https://kubernetes.io/docs/concepts/overview/working-with-objects/labels/) [G]; [Annotations](https://kubernetes.io/docs/concepts/overview/working-with-objects/annotations/) [G]
8. **Namespaces.** "A mechanism for isolating groups of resources within a single cluster". Names must be unique within a namespace, not across namespaces.
   - Four initial namespaces: `default`, `kube-system`, `kube-public`, `kube-node-lease`.
   - *Intuition: folders, not walls.* Network isolation needs NetworkPolicy (K4). — [Namespaces](https://kubernetes.io/docs/concepts/overview/working-with-objects/namespaces/) [G]
9. **kubeconfig and contexts.** A kubeconfig organizes clusters, users, namespaces and auth. A *context* binds cluster + user + default namespace.
   - kind writes context `kind-kind`.
   - Argo CD's getting-started guide uses `kubectl config set-context --current --namespace=argocd`.
   - Mac pitfall (background knowledge, not verified this session): Docker Desktop has its own optional Kubernetes context, so always check `kubectl config current-context`. — [Organizing Cluster Access Using kubeconfig Files](https://kubernetes.io/docs/concepts/configuration/organize-cluster-access-kubeconfig/) [G]; [Argo CD Getting Started](https://argo-cd.readthedocs.io/en/stable/getting_started/) [G]
10. **kubectl verbs.**
    - `get` (`-o wide`, `-o yaml`, `--show-labels`, `-L`), `describe` (look at Events), `logs` (`-c`, `--previous`, `-f`), `exec -it -- sh`, `explain`.
    - `--dry-run=client -o yaml` generates YAML skeletons.
    - New: `kubectl get -o kyaml` is Stable in 1.37. KYAML is a safer subset of YAML, and every KYAML file is valid YAML. — [1.37 release](https://kubernetes.io/blog/2026/08/26/kubernetes-v1-37-release/) [G]; [KYAML blog](https://kubernetes.io/blog/2026/08/11/how-to-pretty-print-kubernetes-yaml-as-kyaml/) [L]
    - `kubectl run --filename/-f` is being deprecated in 1.37. — [1.37 release](https://kubernetes.io/blog/2026/08/26/kubernetes-v1-37-release/) [G]

**Example manifest.** This is my composition, built from the documented sidecar shape (init container + native sidecar + main container).
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: web
  labels: {app: web, tier: frontend}            # identifying, selectable
  annotations: {example.com/owner: "team-a"}    # non-identifying
spec:
  initContainers:
  - name: init-content                           # runs once, must succeed
    image: busybox:1.36
    command: ["sh", "-c", "echo hello-from-init > /work/index.html"]
    volumeMounts: [{name: work, mountPath: /work}]
  - name: log-tailer                             # native sidecar (GA 1.33)
    image: busybox:1.36
    restartPolicy: Always
    command: ["sh", "-c", "tail -F /logs/access.log"]
    volumeMounts: [{name: logs, mountPath: /logs}]
  containers:
  - name: nginx
    image: nginx:1.27
    ports: [{containerPort: 80}]
    volumeMounts:
    - {name: work, mountPath: /usr/share/nginx/html}
    - {name: logs, mountPath: /var/log/nginx}
  volumes:
  - {name: work, emptyDir: {}}
  - {name: logs, emptyDir: {}}
```
Commands and expected results (illustrative unless marked):
- `kubectl apply -f web.yaml`, then `kubectl get pod web -w`. You'll see `Init:0/2` move to `PodInitializing` and then `Running`. READY should count the sidecar too (e.g. `2/2`); confirm on 1.37.
- `kubectl exec web -c nginx -- curl -s localhost` returns `hello-from-init`. Use `wget -qO-` if curl is absent.
- `kubectl logs web -c log-tailer -f` shows nginx access lines as you curl.
- `kubectl run tmp --image=nginx:1.27 --dry-run=client -o yaml` prints a Pod skeleton without creating anything.
- A doc example of CrashLoopBackOff in the STATUS column (doc): `alessandras-namespace   alessandras-pod    0/1     CrashLoopBackOff   200        2d9h`

**Resources**
- [Pod Lifecycle](https://kubernetes.io/docs/concepts/workloads/pods/pod-lifecycle/) [G]
- [Sidecar Containers](https://kubernetes.io/docs/concepts/workloads/pods/sidecar-containers/) [G]
- [Init Containers](https://kubernetes.io/docs/concepts/workloads/pods/init-containers/) [G]
- [kubectl Quick Reference](https://kubernetes.io/docs/reference/kubectl/quick-reference/) [G] (source `content/en/docs/reference/kubectl/quick-reference.md` exists in the repo)
- [Namespaces](https://kubernetes.io/docs/concepts/overview/working-with-objects/namespaces/) [G]
- [kubeconfig](https://kubernetes.io/docs/concepts/configuration/organize-cluster-access-kubeconfig/) [G]
- Video: [Complete Kubernetes Course – From BEGINNER to PRO](https://www.youtube.com/watch?v=2T86xAtR6Fo) [S] (channel not shown in results)

---

#### K3. Deployments, ReplicaSets and rollouts

**Concepts in teaching order**
1. **Deployment → ReplicaSet → Pods.** You manage the Deployment, which manages ReplicaSets, which manage Pods. *Intuition: manager → shift supervisor → workers.*
2. **`pod-template-hash` label.** The Deployment controller adds this label to each ReplicaSet it creates, which is how ReplicaSets for different template versions don't fight over Pods. Example (doc): `nginx-deployment-75675f5897-7ci7o 1/1 Running 0 18s app=nginx,pod-template-hash=75675f5897`. — [Deployments](https://kubernetes.io/docs/concepts/workloads/controllers/deployment/) [G]
3. **What triggers a rollout.** A rollout (new revision) happens "if and only if the Deployment's Pod template (`.spec.template`) is changed". Scaling does not create a revision. — same source.
4. **RollingUpdate defaults.** 25% max unavailable and 25% max surge. At least 75% of desired Pods stay up and at most 125% exist. `Recreate` is the alternative strategy. — same source.
5. **Rollout commands.** `kubectl rollout status|history|undo|pause|resume`.
6. **Stuck rollouts.** `progressDeadlineSeconds` defaults to 600. When a rollout stalls (bad image), the controller stops scaling up the new ReplicaSet, and `maxUnavailable` protects old Pods. — same source.
7. **Self-healing.** Delete a Pod and its ReplicaSet replaces it with a *new* Pod (new name, new IP).
8. **Labels as glue, demonstrated.** Relabel a Pod so it no longer matches the selector: the ReplicaSet treats it as gone and creates a replacement, and the orphan keeps running. This behaviour follows from selector-based acquisition. — [ReplicaSet](https://kubernetes.io/docs/concepts/workloads/controllers/replicaset/) [G]
9. **Newer details (optional).** Deployment status counts terminating replicas (Beta in 1.35). — [1.35 release](https://kubernetes.io/blog/2025/12/17/kubernetes-v1-35-release/) [G]

**Example commands.** Expected output is illustrative.
```bash
kubectl create deployment web --image=nginx:1.26 --replicas=3
kubectl get deploy,rs,pods -l app=web --show-labels
kubectl set image deployment/web nginx=nginx:1.27
kubectl annotate deployment/web kubernetes.io/change-cause="bump to 1.27"
kubectl rollout status deployment/web     # "deployment "web" successfully rolled out"
kubectl get rs -l app=web                 # old RS at 0 replicas, new RS at 3
kubectl rollout history deployment/web
kubectl set image deployment/web nginx=nginx:does-not-exist
kubectl get pods -l app=web               # 1 new Pod ErrImagePull/ImagePullBackOff, 3 old Pods still Running
kubectl rollout undo deployment/web
kubectl describe deployment web | grep -i strategy   # RollingUpdateStrategy: 25% max unavailable, 25% max surge (doc)
```

**Resources**
- [Deployments](https://kubernetes.io/docs/concepts/workloads/controllers/deployment/) [G]
- [ReplicaSet](https://kubernetes.io/docs/concepts/workloads/controllers/replicaset/) [G]
- [Images: `:latest` and imagePullPolicy](https://kubernetes.io/docs/concepts/containers/images/) [G]
- Video: [Kubernetes Course – Full Beginners Tutorial (Containerize Your Apps!)](https://www.youtube.com/watch?v=d6WC5n9G_sM) [S] (channel not shown)

---

#### K4. Services and cluster networking

**Concepts in teaching order**
1. **The Kubernetes network model.** Every Pod gets its own IP, and Pods can reach each other across nodes without NAT. The network plugin (CNI) implements this. "Flat network model where every Pod can communicate with every other Pod" is summarized in [KodeKloud: Kubernetes networking explained](https://kodekloud.com/blog/kubernetes-networking-explained/) [S].
   - On kind the default CNI is **kindnetd**, "a simple networking implementation … based around standard CNI plugins (`ptp`, `host-local`, …) and simple netlink routes", which also handles IP masquerade. — [kind Configuration](https://kind.sigs.k8s.io/docs/user/configuration/) [G]
   - kind's default Service subnet is `10.96.0.0/16`. — same source.
2. **Pod IPs churn, so Services exist.** A Service selects Pods by label and gives them one stable virtual IP and DNS name. *Intuition: a phone number that forwards to whoever is on shift.* — [Service](https://kubernetes.io/docs/concepts/services-networking/service/) [G]
3. **EndpointSlices.** These are the live list of ready Pod IPs behind a Service, at most 100 endpoints per slice by default.
   - The old Endpoints API was deprecated in 1.33. — [EndpointSlices](https://kubernetes.io/docs/concepts/services-networking/endpoint-slices/) [G]; [1.33 release](https://kubernetes.io/blog/2025/04/23/kubernetes-v1-33-release/) [G]
   - *Teaching point:* a Pod that fails readiness is removed from the endpoints.
4. **Service types.**
   - `ClusterIP` (default): internal only.
   - `NodePort`: opens a port on every node, from the range 30000–32767 by default.
   - `LoadBalancer`: asks a cloud or controller for an external IP.
   - `ExternalName`: a DNS CNAME.
   - **Headless** (`clusterIP: None`): no virtual IP; DNS returns Pod IPs. StatefulSets use it.
   - `.spec.externalIPs` is deprecated in 1.36 (warnings now, removal planned for v1.43; CVE-2020-8554). — [Service](https://kubernetes.io/docs/concepts/services-networking/service/) [G]; [1.36 release](https://kubernetes.io/blog/2026/04/22/kubernetes-v1-36-release/) [G]
5. **CoreDNS and Service DNS.** Names follow the form `<svc>.<ns>.svc.cluster.local`. Pods get a search path (`<ns>.svc.cluster.local svc.cluster.local cluster.local`), so the short name `web` works within a namespace and `web.prod` works across namespaces. — [DNS for Services and Pods](https://kubernetes.io/docs/concepts/services-networking/dns-pod-service/) [G]
6. **kube-proxy.** It watches Services and EndpointSlices and programs node packet rules.
   - The `nftables` backend went GA in 1.33. The recommended Linux replacement for `ipvs` is nftables.
   - `ipvs` mode was deprecated in 1.35. It should be disabled by default by v1.40 and removed by v1.43.
   - 1.37 makes nftables faster by using netlink directly. — [1.33](https://kubernetes.io/blog/2025/04/23/kubernetes-v1-33-release/) [G]; [1.35](https://kubernetes.io/blog/2025/12/17/kubernetes-v1-35-release/) [G]; [1.37](https://kubernetes.io/blog/2026/08/26/kubernetes-v1-37-release/) [G]; [Virtual IPs and Service Proxies](https://kubernetes.io/docs/reference/networking/virtual-ips/) [L]
7. **NetworkPolicy.** Pods are non-isolated by default; all traffic is allowed.
   - A Pod becomes isolated for ingress or egress once *any* policy selects it for that direction. After that, only explicitly allowed traffic flows.
   - Enforcement requires a network plugin that supports it. — [Network Policies](https://kubernetes.io/docs/concepts/services-networking/network-policies/) [G]
   - **On kind it works out of the box:** kindnetd embeds `sigs.k8s.io/kube-network-policies` (v1.1.2) and evaluates standard NetworkPolicies. — kind source `images/kindnetd/go.mod` and `cmd/kindnetd/main.go` [R]
8. **Reaching a Service from your Mac.** Options:
   - `kubectl port-forward svc/web 8080:80`.
   - NodePort plus kind `extraPortMappings` (e.g. `containerPort: 30950`, `hostPort: 80`). — [kind Configuration](https://kind.sigs.k8s.io/docs/user/configuration/) [G]
   - LoadBalancer via **cloud-provider-kind**. On macOS, kind nodes are not reachable from the host, so cloud-provider-kind uses Docker port mapping: a `kindccm-…` container appears and you connect to `localhost:<mapped port>`. — [cloud-provider-kind README](https://github.com/kubernetes-sigs/cloud-provider-kind) [R]; [kind LoadBalancer](https://kind.sigs.k8s.io/docs/user/loadbalancer/) [G]

**Example manifests and commands**
```yaml
apiVersion: v1
kind: Service
metadata: {name: web}
spec:
  selector: {app: web}          # must match Pod labels exactly
  ports: [{port: 80, targetPort: 80}]
---
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata: {name: default-deny-ingress}
spec:
  podSelector: {}               # selects every Pod in the namespace
  policyTypes: [Ingress]        # no ingress rules → all inbound denied
---
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata: {name: allow-from-client}
spec:
  podSelector: {matchLabels: {app: web}}
  ingress: [{from: [{podSelector: {matchLabels: {role: client}}}]}]
```
```bash
kubectl get endpointslices -l kubernetes.io/service-name=web   # shows the 3 Pod IPs
kubectl run tmp --rm -it --image=busybox:1.36 -- sh -c 'nslookup web; wget -qO- http://web'
kubectl scale deploy web --replicas=5 && kubectl get endpointslices -l kubernetes.io/service-name=web -w
# After default-deny: the wget times out. With --labels=role=client on the tmp Pod it works again.
kubectl -n kube-system get configmap kube-proxy -o jsonpath='{.data.config\.conf}' | grep 'mode:'   # (doc command from the 1.37 post)
```

**Resources**
- [Service](https://kubernetes.io/docs/concepts/services-networking/service/) [G]
- [DNS for Services and Pods](https://kubernetes.io/docs/concepts/services-networking/dns-pod-service/) [G]
- [EndpointSlices](https://kubernetes.io/docs/concepts/services-networking/endpoint-slices/) [G]
- [Network Policies](https://kubernetes.io/docs/concepts/services-networking/network-policies/) [G]
- [kind LoadBalancer](https://kind.sigs.k8s.io/docs/user/loadbalancer/) [G]
- [cloud-provider-kind](https://github.com/kubernetes-sigs/cloud-provider-kind) [R]
- [KodeKloud: Kubernetes networking explained](https://kodekloud.com/blog/kubernetes-networking-explained/) [S]
- Video: [Kubernetes Services Explained (ClusterIP, LoadBalancer, NodePort)](https://www.youtube.com/watch?v=BYZgA2BBt4s) [S] (channel not shown)

---

#### K5. ConfigMaps and Secrets

**Concepts in teaching order**
1. **Separate config from the image.** The same image runs in dev and prod; config comes from outside.
2. **ConfigMap.** Holds non-confidential key/value config.
   - "ConfigMap does not provide secrecy or encryption."
   - Data cannot exceed 1 MiB. — [ConfigMaps](https://kubernetes.io/docs/concepts/configuration/configmap/) [G]
3. **Two ways to consume config, which behave differently on update.**
   - **Environment variables** are *not* updated automatically and need a Pod restart.
   - **Mounted volumes** are updated eventually, except a `subPath` mount, which never receives updates. — same source.
   - *Intuition: env vars are read once at birth; files are live-ish.*
4. **Immutable ConfigMaps and Secrets** (`immutable: true`) protect against accidental change and reduce API watch load. — same source.
5. **Secret.** Same shape as a ConfigMap, meant for sensitive data.
   - Secrets are "stored unencrypted in the API server's underlying data store (etcd)". Anyone with API access can read or modify them, and so can anyone with etcd access.
   - The fixes: enable encryption at rest, restrict access with least-privilege RBAC, and so on.
   - base64 "is obscured but not secret". — [Secrets](https://kubernetes.io/docs/concepts/configuration/secret/) [G]; [Encrypting Secret Data at Rest](https://kubernetes.io/docs/tasks/administer-cluster/encrypt-data/) [L]
6. **Rolling out config changes.** Kustomize `configMapGenerator`/`secretGenerator` append a content-hash suffix to the generated name. A config change therefore changes the Pod template and triggers a rollout. — [Kustomize task](https://kubernetes.io/docs/tasks/manage-kubernetes-objects/kustomization/) [G]
7. **Bridge to G2.** Never commit plain Secrets to Git. Use Sealed Secrets, External Secrets Operator or the Secrets Store CSI driver. — [Argo CD Secret Management](https://argo-cd.readthedocs.io/en/stable/operator-manual/secret-management/) [G]
8. **1.37 footnote.** Static Pods can no longer reference Secrets or ConfigMaps. — [1.37 release](https://kubernetes.io/blog/2026/08/26/kubernetes-v1-37-release/) [G]

**Example commands.** Expected output is illustrative.
```bash
kubectl create configmap app-config --from-literal=GREETING=hello --from-literal=COLOR=blue
kubectl create secret generic db-cred --from-literal=password='s3cr3t!'
kubectl get secret db-cred -o yaml          # data.password: czNjcjN0IQ==
kubectl get secret db-cred -o jsonpath='{.data.password}' | base64 -d   # s3cr3t!  ← the "aha" moment
```
```yaml
# in a Pod/Deployment container spec
envFrom: [{configMapRef: {name: app-config}}]
env: [{name: DB_PASSWORD, valueFrom: {secretKeyRef: {name: db-cred, key: password}}}]
volumeMounts: [{name: cfg, mountPath: /etc/app}]
# volumes: [{name: cfg, configMap: {name: app-config}}]
```

**Resources**
- [ConfigMaps](https://kubernetes.io/docs/concepts/configuration/configmap/) [G]
- [Secrets](https://kubernetes.io/docs/concepts/configuration/secret/) [G]
- [Encrypting Secret Data at Rest](https://kubernetes.io/docs/tasks/administer-cluster/encrypt-data/) [L]
- [Managing objects with Kustomize (generators)](https://kubernetes.io/docs/tasks/manage-kubernetes-objects/kustomization/) [G]
- [Sealed Secrets](https://github.com/bitnami-labs/sealed-secrets) [L]
- [External Secrets Operator](https://github.com/external-secrets/external-secrets) [L]

---

#### K6. Health, resources, autoscaling and scheduling

**Concepts in teaching order**
1. **Probes.**
   - **Readiness:** am I ready for traffic? Failing removes the Pod from Service endpoints.
   - **Liveness:** am I stuck? Failing restarts the container.
   - **Startup:** am I still booting? Holds off the other probes.
   - The docs warn: "Incorrect implementation of liveness probes can lead to cascading failures", meaning restarts under high load, failed client requests and more load on the remaining Pods. — [Probes](https://kubernetes.io/docs/concepts/workloads/pods/probes/) [G]; [Configure probes task](https://kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes/) [G]
2. **Requests vs limits.**
   - *Requests* are what the scheduler reserves.
   - *Limits* are enforced at runtime. CPU limits are enforced by **throttling**; memory limits by the kernel's **OOM kill**. — [Resource Management for Pods and Containers](https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/) [G]
   - *Intuition: CPU is compressible (you slow down); memory is not (you die).*
3. **OOMKilled.** Example from the docs (doc):
   ```
   memory-demo-2   0/1       OOMKilled   1          24s
   ```
   The container status shows `exitCode: 137` and `reason: OOMKilled`. — [Assign Memory Resources](https://kubernetes.io/docs/tasks/configure-pod-container/assign-memory-resource/) [G]
4. **QoS classes.** *Guaranteed* (requests = limits for every container), *Burstable* (some requests or limits) and *BestEffort* (none). Under node pressure, the kubelet evicts BestEffort first, then Burstable, then Guaranteed. — [Pod QoS Classes](https://kubernetes.io/docs/concepts/workloads/pods/pod-qos/) [G]
5. **HPA.**
   - Formula: `desiredReplicas = ceil(currentReplicas × currentMetricValue / desiredMetricValue)`.
   - The loop runs every 15s by default, with a default tolerance of 10%.
   - Scale-down examples use `stabilizationWindowSeconds: 300`.
   - CPU and memory metrics need **metrics-server**. — [HPA concept](https://kubernetes.io/docs/concepts/workloads/autoscaling/horizontal-pod-autoscale/) [G]; [HPA walkthrough](https://kubernetes.io/docs/tasks/run-application/horizontal-pod-autoscale-walkthrough/) [G]
   - 1.37: the `metrics.k8s.io` API is Stable.
   - 1.37: HPA **scale-to-zero** is Beta and on by default, but *only* for object or external metrics, not CPU or memory (`minReplicas: 0`; `ScaledToZero` condition).
   - 1.37: configurable HPA tolerance is Stable. — [1.37 release](https://kubernetes.io/blog/2026/08/26/kubernetes-v1-37-release/) [G]; [HPA scale-to-zero beta post](https://kubernetes.io/blog/2026/09/02/kubernetes-v1-37-hpa-scale-to-zero-beta/) [G]
6. **VPA (brief).** A separately installed CRD add-on, not part of core. Update modes are `Off`, `Initial`, `Recreate`, `InPlaceOrRecreate` and `InPlace`. It reads `metrics.k8s.io`. — [Vertical Pod Autoscaling](https://kubernetes.io/docs/concepts/workloads/autoscaling/vertical-pod-autoscale/) [G]
7. **In-place Pod resize.** **GA in 1.35** (Beta in 1.33).
   - Change CPU and memory without recreating the Pod: `kubectl patch pod <p> --subresource resize --patch '…'`. The `--subresource=resize` flag needs kubectl v1.32+.
   - `resizePolicy` per resource: `NotRequired` (default, no restart) or `RestartContainer`.
   - Status conditions: `PodResizePending` and `PodResizeInProgress`.
   - 1.37 adds Alpha scheduler preemption for in-place resize. — [Resize CPU and Memory Resources assigned to Containers](https://kubernetes.io/docs/tasks/configure-pod-container/resize-container-resources/) [G]; [1.35 release](https://kubernetes.io/blog/2025/12/17/kubernetes-v1-35-release/) [G]; [1.37 release](https://kubernetes.io/blog/2026/08/26/kubernetes-v1-37-release/) [G]
8. **Scheduling, in order.**
   1. `nodeSelector` (simple label match).
   2. Node affinity: required or preferred.
   3. Pod affinity and anti-affinity: spread or co-locate.
   4. Taints and tolerations. "Taints are the opposite [of affinity] -- they allow a node to repel a set of pods." Effects are `NoSchedule`, `PreferNoSchedule` and `NoExecute`. Example: `kubectl taint nodes node1 key1=value1:NoSchedule`, with a trailing `-` to remove. — [Assigning Pods to Nodes](https://kubernetes.io/docs/concepts/scheduling-eviction/assign-pod-node/) [G]; [Taints and Tolerations](https://kubernetes.io/docs/concepts/scheduling-eviction/taint-and-toleration/) [G]
   - *Intuition: affinity is the Pod's preference; a taint is the node's "keep out" sign; a toleration is a permit.*
9. **PodDisruptionBudgets.** These limit *voluntary* disruptions such as `kubectl drain` and upgrades, via `minAvailable` or `maxUnavailable`. They cannot prevent involuntary ones, such as a node crash. — [Disruptions](https://kubernetes.io/docs/concepts/workloads/pods/disruptions/) [G]; [Configure a PDB](https://kubernetes.io/docs/tasks/run-application/configure-pdb/) [G]

**Example snippet**
```yaml
containers:
- name: app
  image: nginx:1.27                          # any HTTP app; the HPA walkthrough uses its own php-apache manifest
  resources:
    requests: {cpu: 200m, memory: 128Mi}
    limits:   {memory: 256Mi}                # many teams omit CPU limits; discuss throttling trade-off
  startupProbe:   {httpGet: {path: /, port: 80}, failureThreshold: 30, periodSeconds: 2}
  readinessProbe: {httpGet: {path: /, port: 80}, periodSeconds: 5}
  livenessProbe:  {httpGet: {path: /, port: 80}, periodSeconds: 10, failureThreshold: 3}
```
- Installing metrics-server on kind: `kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml`. Then add `--kubelet-insecure-tls`, which "Do[es] not verify the CA of serving certificates presented by Kubelets. For testing purposes only." — [metrics-server README](https://github.com/kubernetes-sigs/metrics-server) [R]
- The HPA walkthrough uses `kubectl apply -f https://k8s.io/examples/application/php-apache.yaml`, then a busybox `load-generator` Pod. — [HPA walkthrough](https://kubernetes.io/docs/tasks/run-application/horizontal-pod-autoscale-walkthrough/) [G]

**Resources**
- [Probes](https://kubernetes.io/docs/concepts/workloads/pods/probes/) [G]
- [Resource Management](https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/) [G]
- [Pod QoS](https://kubernetes.io/docs/concepts/workloads/pods/pod-qos/) [G]
- [HPA walkthrough](https://kubernetes.io/docs/tasks/run-application/horizontal-pod-autoscale-walkthrough/) [G]
- [In-place resize task](https://kubernetes.io/docs/tasks/configure-pod-container/resize-container-resources/) [G]
- [Taints and Tolerations](https://kubernetes.io/docs/concepts/scheduling-eviction/taint-and-toleration/) [G]
- [Disruptions/PDB](https://kubernetes.io/docs/concepts/workloads/pods/disruptions/) [G]
- [7 Common Kubernetes Pitfalls (K8s blog, Oct 2025)](https://kubernetes.io/blog/2025/10/20/seven-kubernetes-pitfalls-and-how-to-avoid/) [G]

---

#### K7. Gateway API, Ingress and storage

**Concepts in teaching order (traffic)**
1. **North-south traffic.** HTTP routing by host and path into Services. *Intuition: Services are internal phone numbers; Ingress/Gateway is the front desk that routes visitors.*
2. **Ingress (legacy but everywhere).** Stable since v1.19.
   - The docs say "The Kubernetes project recommends using Gateway instead of Ingress. The Ingress API has been frozen." It remains GA and supported. — [Ingress](https://kubernetes.io/docs/concepts/services-networking/ingress/) [G]
   - Ingress needs a separately installed *controller*.
3. **ingress-nginx retirement.** The community Ingress-NGINX controller was **retired on March 24, 2026**: no releases, bugfixes or security fixes since then.
   - Existing installs keep working, and charts and images remain available.
   - Check with `kubectl get pods --all-namespaces --selector app.kubernetes.io/name=ingress-nginx`.
   - "Ingress-NGINX" (community) and F5's "NGINX Ingress" are different projects. — [1.36 release](https://kubernetes.io/blog/2026/04/22/kubernetes-v1-36-release/) [G]; [Retirement announcement, Nov 11, 2025](https://kubernetes.io/blog/2025/11/11/ingress-nginx-retirement/) [S]; [Steering/SRC statement, Jan 29, 2026](https://kubernetes.io/blog/2026/01/29/ingress-nginx-statement/) [S]; [Five surprising Ingress-NGINX behaviors](https://kubernetes.io/blog/2026/02/27/ingress-nginx-before-you-migrate/) [G]
   - Example quirk: with `use-regex`, Ingress-NGINX regex matches are prefix-based and case-insensitive. Envoy-based Gateway implementations (Istio, Envoy Gateway, kgateway) do full case-sensitive matches. — same source.
   - **Ingress2Gateway 1.0** (Mar 20, 2026) translates Ingress plus 30+ Ingress-NGINX annotations to Gateway API and warns about untranslatable config. — [Ingress2Gateway 1.0](https://kubernetes.io/blog/2026/03/20/ingress2gateway-1-0-release/) [G]
4. **Gateway API.** "Role-oriented":
   - **GatewayClass**: which controller, managed by the infrastructure provider.
   - **Gateway**: a listener (ports, hostnames, TLS), managed by the cluster operator.
   - **HTTPRoute** (and GRPCRoute, TLSRoute, TCPRoute, UDPRoute): routing rules owned by app developers.
   - A Gateway is associated with exactly one GatewayClass. — [Gateway API concept (k8s docs)](https://kubernetes.io/docs/concepts/services-networking/gateway/) [G]; [gateway-api.sigs.k8s.io](https://gateway-api.sigs.k8s.io/) [L]
5. **Gateway API versions.** Gateway API ships as CRDs, separate from Kubernetes releases.
   - **v1.6.0 (June 30, 2026):** TCPRoute and UDPRoute graduated to Standard (`v1`). Experimental resources moved to their own API group `gateway.networking.x-k8s.io` with an `X` prefix. — [Gateway API v1.6 blog](https://kubernetes.io/blog/2026/08/03/gateway-api-v1-6-release/) [G]
   - **v1.7.0 (tagged Oct 29, 2026):** HTTPRoute retries (GEP-1731) graduated to Standard. New Experimental features include TelemetryPolicy, pre-routing filters and session persistence on `XBackend`. — [v1.7 CHANGELOG](https://github.com/kubernetes-sigs/gateway-api/blob/main/CHANGELOG/1.7-CHANGELOG.md) [R]
   - Teach the **Standard** channel only.
6. **Gateway on kind.** **cloud-provider-kind** provides a LoadBalancer controller *and* a Gateway API controller. It auto-installs the Gateway API CRDs and provisions a GatewayClass named `cloud-provider-kind`. Since its v0.9.0 it also serves plain Ingress natively.
   - The newest cloud-provider-kind tag is v0.12.0 (`git ls-remote` [R]).
   - [Experimenting with Gateway API using kind (K8s blog, Jan 28, 2026)](https://kubernetes.io/blog/2026/01/28/experimenting-gateway-api-with-kind/) [G]; [kind Ingress guide](https://kind.sigs.k8s.io/docs/user/ingress/) [G]; [Migrating from Ingress](https://gateway-api.sigs.k8s.io/guides/getting-started/migrating-from-ingress/) [L]

**Example (from the K8s blog Gateway-on-kind walkthrough, abridged)**
```yaml
apiVersion: gateway.networking.k8s.io/v1
kind: Gateway
metadata: {name: gateway, namespace: gateway-infra}
spec:
  gatewayClassName: cloud-provider-kind
  listeners:
  - name: default
    hostname: "*.exampledomain.example"
    port: 80
    protocol: HTTP
    allowedRoutes: {namespaces: {from: All}}   # blog notes: prefer Same/Selector in real clusters
---
apiVersion: gateway.networking.k8s.io/v1
kind: HTTPRoute
metadata: {name: echo, namespace: demo}
spec:
  parentRefs: [{name: gateway, namespace: gateway-infra}]
  hostnames: ["some.exampledomain.example"]
  rules:
  - matches: [{path: {type: PathPrefix, value: /}}]
    backendRefs: [{name: echo, port: 3000}]
```
- Expected output of `kubectl get gateway -n gateway-infra gateway` (doc):
  ```
  NAME      CLASS                 ADDRESS      PROGRAMMED   AGE
  gateway   cloud-provider-kind   172.18.0.3   True         5m6s
  ```
- Test (doc): `curl --resolve some.exampledomain.example:80:${GW_ADDR} http://some.exampledomain.example` returns echo JSON with `"namespace": "demo"`.
- **Mac caveat:** the 172.18.x address is not reachable from macOS. Use the `kindccm-…` container's localhost port mapping. — [cloud-provider-kind README](https://github.com/kubernetes-sigs/cloud-provider-kind) [R]

**Concepts in teaching order (storage)**
7. **Volumes.**
   - `emptyDir`: dies with the Pod.
   - **PersistentVolume (PV)**: a piece of storage.
   - **PersistentVolumeClaim (PVC)**: a request for storage.
   - **StorageClass**: a recipe for dynamic provisioning.
   - *Intuition: the PVC is the order ticket, the PV is the delivered disk, the StorageClass is the supplier's catalogue.*
   - Access modes: RWO, ROX, RWX, RWOP (ReadWriteOncePod).
   - Reclaim policy: `Retain` or `Delete`. Dynamically provisioned PVs inherit theirs from the StorageClass. — [Persistent Volumes](https://kubernetes.io/docs/concepts/storage/persistent-volumes/) [G]; [Storage Classes](https://kubernetes.io/docs/concepts/storage/storage-classes/) [G]
8. **kind storage.** kind installs a default StorageClass named `standard` backed by Rancher's local-path-provisioner. kind v0.33 bumped that provisioner image. — kind source `pkg/cluster/internal/create/actions/installstorage` [R]; kind git log [R]
9. **StatefulSet.** Gives:
   - Stable, unique network identifiers (`web-0`, `web-1`).
   - Stable, persistent storage via `volumeClaimTemplates`.
   - Ordered, graceful deployment and scaling.
   - It requires a **headless Service**.
   - *Intuition: Deployments run cattle; StatefulSets run named pets with their own disks.* — [StatefulSets](https://kubernetes.io/docs/concepts/workloads/controllers/statefulset/) [G]
   - 1.37 changes: `maxUnavailable` for StatefulSets is back on by default, and a new Alpha `Recreate` update strategy was added. — [1.37 release](https://kubernetes.io/blog/2026/08/26/kubernetes-v1-37-release/) [G]

**Resources**
- [Gateway API concept page](https://kubernetes.io/docs/concepts/services-networking/gateway/) [G]
- [Experimenting with Gateway API using kind](https://kubernetes.io/blog/2026/01/28/experimenting-gateway-api-with-kind/) [G]
- [Ingress NGINX retirement](https://kubernetes.io/blog/2025/11/11/ingress-nginx-retirement/) [S]
- [Ingress2Gateway 1.0](https://kubernetes.io/blog/2026/03/20/ingress2gateway-1-0-release/) [G]
- [Persistent Volumes](https://kubernetes.io/docs/concepts/storage/persistent-volumes/) [G]
- [StatefulSets](https://kubernetes.io/docs/concepts/workloads/controllers/statefulset/) [G]
- Video: [What is Gateway API for Kubernetes? Find out in ten minutes!](https://www.youtube.com/watch?v=yWD_FGMJOCw) [S] (channel not shown)
- Video: [What's new in the Kubernetes Gateway API](https://www.youtube.com/watch?v=_Mc7CNFS0X0) [S] (channel and date not shown; likely older than v1.6)

---

#### K8. Helm and Kustomize

**Concepts in teaching order**
1. **The problem.** The same app needs slightly different YAML per environment. There are two philosophies: *templating* (Helm) and *patching* (Kustomize). A video title from the search frames it as "The Fight Between Templating and Patching". — [YouTube result](https://www.youtube.com/watch?v=ZMFYSm0ldQ0) [S]
2. **Kustomize.** Plain YAML in a `base/` plus `overlays/<env>/` with patches, name prefixes, image tag overrides and generators.
   - Built into kubectl since 1.14: `kubectl kustomize <dir>` and `kubectl apply -k <dir>`.
   - `configMapGenerator`/`secretGenerator` add hash suffixes, which you can disable with `disableNameSuffixHash`. — [Kustomize task](https://kubernetes.io/docs/tasks/manage-kubernetes-objects/kustomization/) [G]
   - *Intuition: tracing paper over a master drawing.*
3. **Helm.**
   - A **chart** is a package: templates plus `values.yaml`.
   - A **release** is an installed instance; each upgrade is a **revision** you can roll back.
   - *Intuition: apt/brew for Kubernetes apps, plus a templating engine.*
   - Commands: `helm create`, `helm template` (render locally), `helm install`, `helm upgrade --install`, `helm history`, `helm rollback`, `helm uninstall`.
4. **Helm 4 (current major).** v4.0.0 was released Nov 12, 2025, at KubeCon NA, the first major in 6 years. The latest tag is v4.3.1 (`git ls-remote` of [helm/helm](https://github.com/helm/helm) [R]). Changes a beginner will meet:
   - **Server-side apply is the default for new installs.** Upgrades and rollbacks "latch" to the release's previous method, so Helm 3-created releases keep client-side apply unless `--server-side` is set.
   - Flags renamed: `--atomic` → `--rollback-on-failure` and `--force` → `--force-replace`. The old flags still work with deprecation warnings.
   - Post-renderers are now plugins; you can no longer pass an executable.
   - `helm registry login` takes the domain only.
   - New features: kstatus-based waiting, install by OCI digest (`oci://…@sha256:…`), multi-document values, and an optional WebAssembly plugin runtime.
   - **Charts v3** are experimental behind `HELM_EXPERIMENTAL_CHART_V3=1`. `apiVersion: v2` charts work unchanged.
   - Sources: [Helm 4 Overview](https://helm.sh/docs/overview) [S]; [Helm 4 Released](https://helm.sh/blog/helm-4-released) [L]
5. **Helm 3 end of life.** The final Helm 3 feature release was **Sept 9, 2026**, and security fixes end **Feb 10, 2027** (extended from Nov 2026). Teach Helm 4 only. — [Helm 3 End of Life](https://helm.sh/blog/helm-v3-end-of-life) [S]
6. **Choosing between them.** Kustomize suits your own app's environment variants. Helm suits installing third-party software and parameterized packages. Both render to plain YAML, and Argo CD can render both (G1).

**Example layout and commands.** Expected output is illustrative.
```
app/
  base/        deployment.yaml service.yaml kustomization.yaml
  overlays/
    dev/       kustomization.yaml   # replicas: 1, images: newTag: 1.27.0
    prod/      kustomization.yaml   # replicas: 3, namePrefix: prod-, resource patch
```
```yaml
# overlays/prod/kustomization.yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization
resources: [../../base]
namespace: prod
images: [{name: nginx, newTag: "1.27.0"}]
replicas: [{name: web, count: 3}]
```
```bash
kubectl kustomize app/overlays/prod | less    # render only
kubectl diff -k app/overlays/prod             # what would change
kubectl apply -k app/overlays/prod
helm create mychart && helm template demo ./mychart | head -40
helm install demo ./mychart && helm upgrade demo ./mychart --set replicaCount=3
helm history demo        # REVISION 1 deployed→superseded, 2 deployed
helm rollback demo 1 && helm history demo   # revision 3 = rollback to 1
```

**Resources**
- [Helm 4 Overview](https://helm.sh/docs/overview) [S]
- [Helm 3 End of Life](https://helm.sh/blog/helm-v3-end-of-life) [S]
- [Kustomize with kubectl](https://kubernetes.io/docs/tasks/manage-kubernetes-objects/kustomization/) [G]
- Video: [Helm vs Kustomize – The Fight Between Templating and Patching in Kubernetes](https://www.youtube.com/watch?v=ZMFYSm0ldQ0) [S] (channel not shown; the style suggests DevOps Toolkit, unverified)
- Video: [Should We Template or Patch Kubernetes Manifests? (Helm vs Kustomize side by side)](https://www.youtube.com/watch?v=Q19x62ZrR-U) [S] (channel not shown)

---

#### K9. Troubleshooting Kubernetes

**Concepts in teaching order**
1. **A systematic flow, bottom-up.** Pods first, then Service, then Ingress/Gateway. A Service routes to *Pods*, not Deployments, so selector labels and `targetPort` must match. `kubectl port-forward` tests each layer in isolation. — [Learnk8s (Learnkube) visual troubleshooting guide](https://learnkube.com/troubleshooting-deployments) [S]
   - Suggested ladder: `get` (status, restarts) → `describe` (Events at bottom) → `logs` (`--previous` for the crashed instance) → `get events --sort-by=.lastTimestamp` → `exec` / `kubectl debug` → check Service endpoints → check the route.
2. **Common failure states and first checks.**

   | State | Meaning and first checks | Source |
   |---|---|---|
   | `Pending` | Can't be scheduled. Usually insufficient resources, an unbound PVC, or taints and affinity. Check `describe` Events for `FailedScheduling`. | [Debug Pods](https://kubernetes.io/docs/tasks/debug/debug-application/debug-pods/) [G] |
   | `ErrImagePull` / `ImagePullBackOff` | Wrong name or tag, a private registry, or (on kind) an image that was never `kind load`ed. | |
   | `CrashLoopBackOff` | Causes: app errors, config errors (bad env, missing files), resource constraints, failing liveness or startup probes. Investigate with `logs`, then `describe`, then review config. | [Pod Lifecycle](https://kubernetes.io/docs/concepts/workloads/pods/pod-lifecycle/) [G] |
   | `OOMKilled` | `exitCode: 137`. | [Assign Memory Resources](https://kubernetes.io/docs/tasks/configure-pod-container/assign-memory-resource/) [G] |
   | `Running` but `0/1` READY | The readiness probe is failing, so the Service has no endpoints. | |
   | `CreateContainerConfigError` | Usually a missing ConfigMap or Secret key. Not verified in docs this session. | |
3. **`kubectl debug`.**
   - Ephemeral container into a running Pod: `kubectl debug -it ephemeral-demo --image=busybox:1.28 --target=ephemeral-demo`. Useful for distroless images with no shell.
   - Copy with a shell: `kubectl debug myapp -it --copy-to=myapp-debug --container=myapp -- sh`.
   - Swap images: `--set-image=*=ubuntu`.
   - Node debugging: `kubectl debug node/mynode -it --image=ubuntu`.
   - Profiles: `--profile=sysadmin`. — [Debug Running Pods](https://kubernetes.io/docs/tasks/debug/debug-application/debug-running-pod/) [G]
4. **Service debugging.** Check endpoints, DNS and `targetPort`. — [Debug Services](https://kubernetes.io/docs/tasks/debug/debug-application/debug-service/) [G]
5. **k9s.** A terminal UI; latest tag v0.51.0. Install on Mac with `brew install derailed/k9s/k9s`. — [k9s](https://github.com/derailed/k9s) [R]
   - GUI alternative: **Headlamp**. The Kubernetes Dashboard project "has now been archived". — [From Kubernetes Dashboard to Headlamp (K8s blog, Jun 1, 2026)](https://kubernetes.io/blog/2026/06/01/dashboard-to-headlamp/) [G]
6. **RBAC basics.**
   - Subjects are users, groups and ServiceAccounts.
   - A **Role** is namespaced and a **ClusterRole** is cluster-wide. Each is bound with a RoleBinding or ClusterRoleBinding.
   - "Permissions are purely additive (there are no 'deny' rules)."
   - Test with `kubectl auth can-i create deployments --namespace dev`, adding `--as=system:serviceaccount:<ns>:<sa>` to impersonate. — [RBAC](https://kubernetes.io/docs/reference/access-authn-authz/rbac/) [G]; [Authorization overview](https://kubernetes.io/docs/reference/access-authn-authz/authorization/) [G]
   - A `Forbidden` error is an RBAC problem, not a bug.

**Resources**
- [Learnkube visual troubleshooting guide](https://learnkube.com/troubleshooting-deployments) [S]
- [Debug Pods](https://kubernetes.io/docs/tasks/debug/debug-application/debug-pods/) [G]
- [Debug Running Pods (kubectl debug)](https://kubernetes.io/docs/tasks/debug/debug-application/debug-running-pod/) [G]
- [Debug Services](https://kubernetes.io/docs/tasks/debug/debug-application/debug-service/) [G]
- [RBAC](https://kubernetes.io/docs/reference/access-authn-authz/rbac/) [G]
- [k9s](https://github.com/derailed/k9s) [R]
- Video: [Troubleshooting Kubernetes Pods in CrashLoopBackOff, Pending and ImagePullBackOff state](https://www.youtube.com/watch?v=ULitVDnqy8Y) [S] (channel not shown)
- Video: [What is a CrashLoopBackoff? – Understanding the Kubernetes error](https://www.youtube.com/watch?v=iA5bMPNsj94) [S] (channel not shown)

---

#### G1. Argo CD basics

**Concepts in teaching order**
1. **GitOps.** The four OpenGitOps principles (see the intuitions above). *Intuition: Git is the source of truth, and Argo CD is a controller whose "spec" lives in Git.*
   - Push vs pull: a CI pipeline that runs `kubectl apply` *pushes*; an in-cluster agent *pulls*.
2. **Application CRD.** It holds a **source** (repoURL, path, targetRevision; Git, Helm repo or OCI) and a **destination** (cluster server plus namespace), inside a **Project** (`default`).
   - Argo CD renders plain YAML, Kustomize, Helm and Jsonnet, then compares the result with the live state. — [Argo CD Getting Started](https://argo-cd.readthedocs.io/en/stable/getting_started/) [G]; [Core concepts](https://argo-cd.readthedocs.io/en/stable/core_concepts/) [G]
3. **Two independent statuses.**
   - **Sync status:** does live match Git? (`Synced` / `OutOfSync`)
   - **Health status:** is it working? (`Healthy` / `Progressing` / `Degraded` / `Missing` …)
   - 3.4 changed how `Missing` health is treated. — [Argo CD upgrading 3.3→3.4](https://argo-cd.readthedocs.io/en/stable/operator-manual/upgrading/3.3-3.4/) [G]
4. **Install (3.x).**
   ```
   kubectl create namespace argocd
   kubectl apply -n argocd --server-side --force-conflicts -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml
   ```
   `--server-side` is *required* because some CRDs (ApplicationSet) exceed the 262 KB annotation limit of client-side apply.
   - Access the UI with `kubectl port-forward svc/argocd-server -n argocd 8080:443`.
   - Get the admin password with `argocd admin initial-password -n argocd`.
   - Install the CLI with `brew install argocd`. `argocd login --core` skips the API server. — [Getting Started](https://argo-cd.readthedocs.io/en/stable/getting_started/) [G]; [CLI installation](https://argo-cd.readthedocs.io/en/stable/cli_installation/) [G]
5. **First app.**
   ```
   argocd app create guestbook --repo https://github.com/argoproj/argocd-example-apps.git --path guestbook --dest-server https://kubernetes.default.svc --dest-namespace default
   ```
   Then `argocd app get guestbook` and `argocd app sync guestbook`. — [Getting Started](https://argo-cd.readthedocs.io/en/stable/getting_started/) [G]
6. **Detection.** Argo CD polls Git every ~3 min by default (`timeout.reconciliation: 120s` plus up to 60s jitter). Webhooks make it instant. — [Argo CD FAQ](https://argo-cd.readthedocs.io/en/stable/faq/) [G]
7. **Automated sync, prune and self-heal.**
   - Automated sync can be explicitly toggled with `spec.syncPolicy.automated.enabled`.
   - **Prune is off by default.** Deleting a file from Git does *not* delete the resource unless `prune: true` is set.
   - **Self-heal is off by default.** Live edits do *not* trigger a sync unless `selfHeal: true` is set. — [Automated Sync Policy](https://argo-cd.readthedocs.io/en/stable/user-guide/auto_sync/) [G]
8. **Resource tracking.** Since 3.0, annotation-based tracking is the default; it was label-based before. — [Upgrading 2.14→3.0](https://argo-cd.readthedocs.io/en/stable/operator-manual/upgrading/2.14-3.0/) [G]
9. **Leave room for imperativeness.** If an HPA owns `replicas`, omit `replicas` from Git; otherwise Git and the HPA fight. — [Argo CD Best Practices](https://argo-cd.readthedocs.io/en/stable/user-guide/best_practices/) [G]

**Example Application with auto-sync**
```yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata: {name: web-dev, namespace: argocd}
spec:
  project: default
  source:
    repoURL: https://github.com/<you>/k8s-config.git
    targetRevision: main
    path: app/overlays/dev            # Kustomize auto-detected
  destination: {server: https://kubernetes.default.svc, namespace: dev}
  syncPolicy:
    automated: {prune: true, selfHeal: true}
    syncOptions: [CreateNamespace=true]
```

**Resources**
- [Argo CD Getting Started](https://argo-cd.readthedocs.io/en/stable/getting_started/) [G]
- [Automated Sync Policy](https://argo-cd.readthedocs.io/en/stable/user-guide/auto_sync/) [G]
- [Best Practices](https://argo-cd.readthedocs.io/en/stable/user-guide/best_practices/) [G]
- [OpenGitOps principles](https://github.com/open-gitops/documents/blob/main/PRINCIPLES.md) [R]
- Video: [ArgoCD Tutorial for Beginners](https://www.youtube.com/watch?v=MeU5_k9ssrs) [S]. TechWorld with Nana, per search summaries and matching video ID on [Class Central](https://classcentral.com/course/youtube-argocd-tutorial-for-beginners-gitops-cd-for-kubernetes-108860) [S]. It predates Argo CD 3.x, so install flags differ.
- Video: [GitOps with ArgoCD on kind — Complete Hands-On Tutorial](https://www.youtube.com/watch?v=bgpy8-FWXmk) [S] (channel not shown)
- Video: [Introduction to Argo CD & GitOps](https://www.youtube.com/watch?v=8YLsQIG2Svo) [S] (Kunal Kushwaha, 44 min, per a Class Central listing in search results)

---

#### G2. GitOps in practice

**Concepts in teaching order**
1. **Repo structure.** Keep a separate config repo from app source, for five reasons:
   1. Change config without triggering CI.
   2. A cleaner audit log.
   3. Multi-repo apps deployed as one unit.
   4. Separate access: who can push to prod.
   5. Avoid CI loops where CI commits manifests and retriggers builds.
   — [Argo CD Best Practices](https://argo-cd.readthedocs.io/en/stable/user-guide/best_practices/) [G]
   - Typical layout: `apps/<app>/base` plus `apps/<app>/overlays/{dev,staging,prod}`, with one Argo CD Application per app per environment.
2. **Environments and promotion.** Promotion is a Git change: a PR that copies an image tag or version from the dev overlay to staging, then prod. Pin immutable tags or digests; never `latest`, since it violates "versioned and immutable".
   - Tooling options:
     - **Argo CD Image Updater** (argoproj-labs). Since v1.0 it is configured by an `ImageUpdater` CRD (previously annotations); the latest tag is v1.4.0. It has two write-back methods: `argocd` (patch the Application) and `git` (commit `.argocd-source-<appName>.yaml`). The project describes itself as "under active development". — [argocd-image-updater](https://github.com/argoproj-labs/argocd-image-updater) [R]
     - **GitOps Promoter** (`PromotionStrategy` / `ChangeTransferPolicy` resources). Argo CD 3.6 adds health checks for these. — [Upgrading 3.5→3.6](https://argo-cd.readthedocs.io/en/latest/operator-manual/upgrading/3.5-3.6/) [G]
3. **Rendered manifests and the Source Hydrator.** Argo CD can push fully rendered ("hydrated") manifests to Git before syncing, so reviewers see the exact YAML. It is Beta since v3.5.0 and disabled by default. — [Source Hydrator](https://argo-cd.readthedocs.io/en/stable/user-guide/source-hydrator/) [G]; [Feature maturity](https://argo-cd.readthedocs.io/en/stable/operator-manual/feature-maturity/) [G]
4. **ApplicationSets.** One template stamps out many Applications from **generators**: List, Cluster, Git (directories or files), Matrix, Merge, SCM Provider, Pull Request, Cluster Decision Resource, Plugin, OCI, and Post Selector.
   - Progressive Syncs (staged rollout across generated apps) are Beta.
   - The Argo CD docs recommend ApplicationSets (especially the cluster generator) for cluster bootstrapping. — [ApplicationSet docs](https://argo-cd.readthedocs.io/en/stable/operator-manual/applicationset/) [G]; [List generator](https://argo-cd.readthedocs.io/en/stable/operator-manual/applicationset/Generators-List/) [G]; [Cluster bootstrapping](https://argo-cd.readthedocs.io/en/stable/operator-manual/cluster-bootstrapping/) [G]
5. **App-of-apps.** One parent Application whose source contains only child Application manifests.
   - Documented as an *alternative* to ApplicationSets, with a warning: "App of Apps is an admin-only tool". Whoever can push to the parent repo can create Applications in arbitrary Projects. — [Cluster Bootstrapping](https://argo-cd.readthedocs.io/en/stable/operator-manual/cluster-bootstrapping/) [G]
   - Video: [Argo CD Tutorial: App of Apps in 8 Minutes](https://www.youtube.com/watch?v=2pvGL0zqf9o) [S] (Akuity, per search summary)
6. **Sync waves.** The `argocd.argoproj.io/sync-wave: "<int>"` annotation orders resources.
   - The default wave is 0, and waves can be negative.
   - Resources apply lowest wave first.
   - There is a 2-second delay between waves, configurable with `ARGOCD_SYNC_WAVE_DELAY`. — [Sync Phases and Waves](https://argo-cd.readthedocs.io/en/stable/user-guide/sync-waves/) [G]
7. **Hooks.**
   - `PreSync`: before apply. Use it for DB migrations or checks; if it fails, the sync stops.
   - `Sync`: alongside apply.
   - `PostSync`: after all resources are Healthy, e.g. smoke tests or notifications.
   - `SyncFail`: cleanup on failure.
   - `PreDelete` and `PostDelete`: around Application deletion; PostDelete since v2.10.
   - Delete policies: `HookSucceeded`, `HookFailed`, `BeforeHookCreation`.
   - Hooks don't run during selective sync. — same source.
8. **Secrets in GitOps.** Argo CD "strongly recommend[s]" *destination-cluster* secret management: Sealed Secrets, External Secrets Operator, Secrets Store CSI Driver or Vault Secrets Operator.
   - It "strongly caution[s] against" manifest-generation injection, such as argocd-vault-plugin. Argo CD caches generated manifests in **plaintext in Redis**, which couples secret updates to app syncs and breaks the rendered-manifests pattern. — [Argo CD Secret Management](https://argo-cd.readthedocs.io/en/stable/operator-manual/secret-management/) [G]
9. **Flux comparison.**
   - Both are CNCF Graduated GitOps controllers.
   - Argo CD ships a built-in web UI and uses a centralized hub model; Flux has no built-in UI and runs per cluster.
   - Argo CD's full stack (API server, repo-server, controller, Redis, Dex) uses more resources.
   - Argo CD needs the separate Image Updater for automatic image bumps. — vendor blog comparison [OneUptime, Feb 2026](https://oneuptime.com/blog/post/2026-02-26-argocd-vs-fluxcd-2026/view) [S]. Treat it as secondary: it's a vendor blog, and the search tool itself flagged possible bias.
   - The latest Flux tag is v2.10.0. — [fluxcd/flux2](https://github.com/fluxcd/flux2) [R]
   - Video: [Introduction to GitOps, Argo CD, and Flux](https://www.youtube.com/watch?v=iQB5j_2rSBA) [S] (Viktor Farcic with Saim Safder, per search snippet)

**Example: sync-wave ordering with a PostSync smoke test**
```yaml
apiVersion: v1
kind: ConfigMap
metadata: {name: app-config, annotations: {argocd.argoproj.io/sync-wave: "-1"}}
data: {GREETING: hello}
---
apiVersion: batch/v1
kind: Job
metadata:
  name: smoke-test
  annotations:
    argocd.argoproj.io/hook: PostSync
    argocd.argoproj.io/hook-delete-policy: HookSucceeded
spec:
  backoffLimit: 0
  template:
    spec:
      restartPolicy: Never
      containers: [{name: curl, image: curlimages/curl:8.10.1, args: ["-fsS", "http://web"]}]
```

**Example ApplicationSet (list generator, abridged from the docs).** It uses `goTemplate: true` and `{{.cluster}}` placeholders. Adapt `elements` to `env: dev|staging|prod` and `path: app/overlays/{{.env}}`. — [List generator](https://argo-cd.readthedocs.io/en/stable/operator-manual/applicationset/Generators-List/) [G]

**Resources**
- [Best Practices (config repo separation)](https://argo-cd.readthedocs.io/en/stable/user-guide/best_practices/) [G]
- [ApplicationSet](https://argo-cd.readthedocs.io/en/stable/operator-manual/applicationset/) [G]
- [Cluster Bootstrapping / App of Apps](https://argo-cd.readthedocs.io/en/stable/operator-manual/cluster-bootstrapping/) [G]
- [Sync Phases and Waves](https://argo-cd.readthedocs.io/en/stable/user-guide/sync-waves/) [G]
- [Secret Management](https://argo-cd.readthedocs.io/en/stable/operator-manual/secret-management/) [G]
- [Argo CD Image Updater](https://github.com/argoproj-labs/argocd-image-updater) [R]
- Video: [The Objectives And The Principles Behind GitOps – Viktor Farcic, Codefresh](https://www.youtube.com/watch?v=797ptFfuL5g) [S]
- Channel: [DevOps & AI Toolkit (Viktor Farcic)](https://www.youtube.com/@DevOpsToolkit) [S]

### Inferences
- The strongest single teaching thread is "everything is a control loop". kubelet, ReplicaSet, HPA, kube-proxy and Argo CD all reconcile spec vs status. GitOps is then "the same idea with Git as the spec", which makes G1 feel like a natural capstone rather than a new tool.
- Teach Gateway API as the default for new HTTP routing, and Ingress as "frozen, still common, read it but don't start with it". This follows from the Ingress API freeze, the ingress-nginx retirement, and cloud-provider-kind making Gateway API free on kind.
- Teach Helm 4 commands only, and mention the `--atomic` → `--rollback-on-failure` rename because learners will see the old flag in older blogs. Helm 3 is out of feature support.
- For a Mac learner, `kubectl port-forward` is the most reliable way to reach anything. cloud-provider-kind's localhost port mapping is the "real LoadBalancer" bonus step, because Docker Desktop's VM hides the 172.18.x network.

### Gaps
- I could not open the kind v0.33.0 GitHub release page; the proxy blocked the release HTML and API for that repo. The v0.32.0..v0.33.0 commit log shows Kubernetes 1.37.0, containerd v2.3.4 and runc v1.4.3, removal of the kindnet CPU limit, and Podman 6 label handling. It shows **no cgroup-specific change**. The cgroup notes I found belong to **kind v0.31.0** (Dec 2025): node images for Kubernetes versions that still use cgroup v1 drop support, and kind "strongly recommend[s] migrating to cgroup v2". — [newreleases.io summary of v0.31.0](https://newreleases.io/project/github/kubernetes-sigs/kind/release/v0.31.0) [S]. If the course brief has a specific "v0.33 cgroup note" in mind, the writer should check the GitHub release page manually.
- I didn't confirm that kubectl's READY column counts native sidecars (e.g. `2/2`); check on a 1.37 cluster.
- No iximiuz.com article surfaced in search, so I list none.
- The component descriptions in K1 come from the `components.md` headings plus standard knowledge; I did not quote the body text.

## Q2. What do beginners get wrong?

### Takeaway
Most beginner failures come from treating Kubernetes like a VM host:
- Mutable `latest` images.
- No resource requests.
- Aggressive liveness probes that restart Pods instead of fixing them.
- Believing base64 Secrets are encrypted.
- Hand-editing live objects that Git (or a controller) owns.

The official docs and blog warn about all of these explicitly.

### Cited Findings
- **`:latest` tags (K2, K3, G2).** "You should avoid using the `:latest` tag when deploying containers in production." With `:latest` (or no tag), `imagePullPolicy` is automatically set to `Always`. — [Images](https://kubernetes.io/docs/concepts/containers/images/) [G]
  - kind's own example loads `my-custom-image:unique-tag`, not latest. — [kind Quick Start](https://kind.sigs.k8s.io/docs/user/quick-start/) [L]
  - In GitOps, a floating tag breaks "Versioned and Immutable". — [OpenGitOps](https://github.com/open-gitops/documents/blob/main/PRINCIPLES.md) [R]
- **No requests or limits (K6).** "Skipping resource requests and limits" is pitfall #1 in the K8s blog's "7 Common Kubernetes Pitfalls". — [K8s blog](https://kubernetes.io/blog/2025/10/20/seven-kubernetes-pitfalls-and-how-to-avoid/) [G]
  - Pods with no requests or limits are BestEffort and are evicted first under node pressure. — [Pod QoS](https://kubernetes.io/docs/concepts/workloads/pods/pod-qos/) [G]
- **Confusing CPU and memory limits (K6).** CPU over its limit is throttled, not killed; memory over its limit is OOM-killed (exit 137). — [Resource Management](https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/) [G]; [Assign Memory](https://kubernetes.io/docs/tasks/configure-pod-container/assign-memory-resource/) [G]
- **Liveness probes that kill healthy Pods (K6).** "Incorrect implementation of liveness probes can lead to cascading failures." — [Probes](https://kubernetes.io/docs/concepts/workloads/pods/probes/) [G]
  - Probes are pitfall #2 in the blog list. — [7 pitfalls](https://kubernetes.io/blog/2025/10/20/seven-kubernetes-pitfalls-and-how-to-avoid/) [G]
  - Liveness and startup failures are a listed cause of CrashLoopBackOff. — [Pod Lifecycle](https://kubernetes.io/docs/concepts/workloads/pods/pod-lifecycle/) [G]
- **"Secrets are encrypted" (K5, G2).** By default Secrets are stored unencrypted in etcd, and anyone with API access can read them. The `.dockerconfigjson` `auth` value "is obscured but not secret". — [Secrets](https://kubernetes.io/docs/concepts/configuration/secret/) [G]
  - In GitOps, injecting secrets during manifest generation leaves them in plaintext in Argo CD's Redis cache. — [Argo CD Secret Management](https://argo-cd.readthedocs.io/en/stable/operator-manual/secret-management/) [G]
- **Editing live objects in a GitOps cluster (G1, G2).**
  - Without self-heal, a `kubectl edit` makes the app OutOfSync and *stays* changed until the next sync: "changes that are made to the live cluster will not trigger automated sync" by default.
  - With `selfHeal: true`, Argo CD reverts the change.
  - Without `prune: true`, deleting YAML from Git leaves orphaned resources. — [Automated Sync Policy](https://argo-cd.readthedocs.io/en/stable/user-guide/auto_sync/) [G]
- **Fighting a controller (K6, G1).** Keeping `replicas` in Git while an HPA manages it causes a tug-of-war; omit it. — [Argo CD Best Practices](https://argo-cd.readthedocs.io/en/stable/user-guide/best_practices/) [G]
- **ConfigMap updates that never arrive (K5).** Env-var consumers need a restart, and `subPath` mounts never update. — [ConfigMaps](https://kubernetes.io/docs/concepts/configuration/configmap/) [G]
- **Reading STATUS as phase (K2).** `CrashLoopBackOff` and `Terminating` are kubectl display strings, not phases. — [Pod Lifecycle](https://kubernetes.io/docs/concepts/workloads/pods/pod-lifecycle/) [G]
- **Thinking namespaces isolate network traffic (K2, K4).** By default every Pod accepts all traffic until a NetworkPolicy selects it, and enforcement requires a supporting network plugin. — [Network Policies](https://kubernetes.io/docs/concepts/services-networking/network-policies/) [G]
- **Expecting a Deployment edit to roll back on its own.** Only `.spec.template` changes create revisions, and a bad image leaves a stuck rollout until you `rollout undo` or fix it (default deadline 600s). — [Deployments](https://kubernetes.io/docs/concepts/workloads/controllers/deployment/) [G]
- **A Service selector typo means "the network is broken" (K4, K9).** Services route to Pods by label, so selectors and `targetPort` must match. — [Learnkube troubleshooting](https://learnkube.com/troubleshooting-deployments) [S]
- **Starting new work on ingress-nginx (K7).** It was retired Mar 24, 2026 with no further security fixes. Translations are not drop-in, because of quirks such as prefix and case-insensitive regex. — [1.36 release](https://kubernetes.io/blog/2026/04/22/kubernetes-v1-36-release/) [G]; [Five surprising behaviors](https://kubernetes.io/blog/2026/02/27/ingress-nginx-before-you-migrate/) [G]
- **Going too light on RBAC (K9).** Pitfall #7 in the blog. RBAC has no deny rules; grant minimally. — [7 pitfalls](https://kubernetes.io/blog/2025/10/20/seven-kubernetes-pitfalls-and-how-to-avoid/) [G]; [RBAC](https://kubernetes.io/docs/reference/access-authn-authz/rbac/) [G]
- **Treating app-of-apps as safe for everyone (G2).** "App of Apps is an admin-only tool." — [Cluster Bootstrapping](https://argo-cd.readthedocs.io/en/stable/operator-manual/cluster-bootstrapping/) [G]
- **Old tutorials (all lessons).** Argo CD 3.x requires `--server-side --force-conflicts` on install because the ApplicationSet CRD is too large for client-side apply. Older videos show plain `kubectl apply`. — [Getting Started](https://argo-cd.readthedocs.io/en/stable/getting_started/) [G]; [Upgrading 3.2→3.3](https://argo-cd.readthedocs.io/en/stable/operator-manual/upgrading/3.2-3.3/) [G]
  - Helm 4 renamed `--atomic` and `--force`. — [Helm 4 Overview](https://helm.sh/docs/overview) [S]

### Inferences
- Present each misconception as a "break it on purpose" lab. Learners remember an OOMKilled Pod they caused far better than a slide.
- "Don't `kubectl edit` in prod" makes a good bridge sentence from K9 into G1: GitOps is the fix for configuration drift.

### Gaps
- No primary source quantifies how common each mistake is; the ranking is editorial.

## Q3. What is current in Kubernetes 1.37 and nearby releases, and in the surrounding tools (Gateway API, ingress-nginx, kind, Helm 4, Argo CD 3.x)?

### Takeaway
As of Oct 30, 2026, the current versions are:

| Project | Current version | Released |
|---|---|---|
| Kubernetes | v1.37 (patch v1.37.2) | Aug 26, 2026 |
| kind | v0.33.0, node image v1.37.0 | Aug 26, 2026 |
| Gateway API | v1.7.0 | tagged Oct 29, 2026 |
| Helm | v4.3.1 | |
| Argo CD | v3.5.6 stable (v3.6.0-rc4 in release candidate) | |

The beginner-relevant shifts since early 2025:
- Native sidecars are GA (1.33).
- In-place Pod resize is GA (1.35).
- cgroup v1 is off by default (1.35).
- ingress-nginx is retired (Mar 2026), and Gateway API is the recommended path.
- Helm 4 has replaced Helm 3.
- Argo CD 3.x changed its install method, resource tracking, RBAC and bundled Helm version.

### Cited Findings

**Kubernetes timeline (beginner-relevant items only)**

| Release (date) | Item | Source |
|---|---|---|
| 1.33 (Apr 23, 2025) | Sidecar containers **GA**. In-place resize **Beta**. nftables kube-proxy **GA**. Endpoints API deprecated (use EndpointSlices). `.kuberc` Alpha. | [1.33 post](https://kubernetes.io/blog/2025/04/23/kubernetes-v1-33-release/) [G] |
| 1.34 (Aug 27, 2025) | Core DRA GA. KYAML Alpha. Pod-level resource requests/limits Beta. `.kuberc` Beta. | [1.34 post](https://kubernetes.io/blog/2025/08/27/kubernetes-v1-34-release/) [G] |
| 1.35 (Dec 17, 2025) | **In-place Pod resource update GA**. Fine-grained container restart rules Beta. KYAML Beta. **cgroup v1 support removed by default**: `failCgroupV1` defaults to true, so the kubelet refuses to start on cgroup v1 nodes unless overridden. **kube-proxy `ipvs` deprecated**. | [1.35 post](https://kubernetes.io/blog/2025/12/17/kubernetes-v1-35-release/) [G]; [cgroup v2 shift blog, Oct 6, 2026](https://kubernetes.io/blog/2026/10/06/kubernetes-cgroups-v2-shift/) [G] |
| 1.36 (Apr 22, 2026) | Ingress NGINX retirement noted. **`Service.spec.externalIPs` deprecated** (removal v1.43). `gitRepo` volume permanently disabled. User Namespaces GA. HPA scale-to-zero Alpha. | [1.36 post](https://kubernetes.io/blog/2026/04/22/kubernetes-v1-36-release/) [G] |
| 1.37 "Garhwal" (Aug 26, 2026) | 16 enhancements to Stable. **KYAML Stable** (`kubectl get -o kyaml`). **metrics.k8s.io v1 Stable**. **HPA scale-to-zero Beta**, on by default, object/external metrics only. Memory QoS (cgroup v2) Beta. StatefulSet `maxUnavailable` back on by default. StatefulSet `Recreate` strategy Alpha. Scheduler preemption for in-place resize Alpha. **kube-dns deprecated**. `ipvs` deprecation timeline (off by default by v1.40, removed by v1.43). `kubectl run -f` deprecated. Static Pods can't reference Secrets or ConfigMaps. cgroup v1 override still exists but removal is planned. | [1.37 post](https://kubernetes.io/blog/2026/08/26/kubernetes-v1-37-release/) [G]; [sig-release 1.37](https://github.com/kubernetes/sig-release/blob/master/releases/release-1.37/README.md) [S] |

**Ingress and Gateway**
- **ingress-nginx:** announced Nov 11, 2025; retired Mar 24, 2026; repos read-only; artifacts remain. — [Announcement](https://kubernetes.io/blog/2025/11/11/ingress-nginx-retirement/) [S]; [1.36 post](https://kubernetes.io/blog/2026/04/22/kubernetes-v1-36-release/) [G]
  - The Jan 29, 2026 Steering/SRC statement warns that, unless you check, you may not know you're affected until compromised. — [Statement](https://kubernetes.io/blog/2026/01/29/ingress-nginx-statement/) [S]
- **Ingress API:** frozen; Gateway recommended. — [Ingress docs](https://kubernetes.io/docs/concepts/services-networking/ingress/) [G]
- **Gateway API v1.x:** described as "the standard for modern, role-oriented, and expressive service networking in Kubernetes".
  - v1.6.0 (Jun 30, 2026): TCPRoute and UDPRoute to Standard `v1`; experimental API group split. — [v1.6 post](https://kubernetes.io/blog/2026/08/03/gateway-api-v1-6-release/) [G]
  - v1.7.0 (Oct 29, 2026): HTTPRoute retries to Standard. — [v1.7 CHANGELOG](https://github.com/kubernetes-sigs/gateway-api/blob/main/CHANGELOG/1.7-CHANGELOG.md) [R]
  - Ingress2Gateway 1.0 (Mar 20, 2026). — [post](https://kubernetes.io/blog/2026/03/20/ingress2gateway-1-0-release/) [G]

**kind**
- v0.33.0 (Aug 26, 2026): default `kindest/node:v1.37.0`, containerd v2.3.4, runc v1.4.3, Go 1.26.7. kindnet's CPU limit removed. — kind git log and `image.go` at tag [R]
- v0.32.0 was tagged Jun 2, 2026 [R].
- cgroup note: kind v0.31.0 (Dec 2025, default K8s 1.35.0) announced that node images for Kubernetes versions still using cgroup v1 drop support, and recommends migrating to cgroup v2. — [newreleases.io v0.31.0](https://newreleases.io/project/github/kubernetes-sigs/kind/release/v0.31.0) [S]
- This matches Kubernetes 1.35's `failCgroupV1: true` default. — [1.35 post](https://kubernetes.io/blog/2025/12/17/kubernetes-v1-35-release/) [G]
- You can check the runtime's cgroup version with `docker info`, looking for `Cgroup Version: 2`. — [kind rootless docs](https://kind.sigs.k8s.io/docs/user/rootless/) [G]
- cloud-provider-kind (latest tag v0.12.0) now covers LoadBalancer, Gateway API and Ingress on kind. — [README](https://github.com/kubernetes-sigs/cloud-provider-kind) [R]; [kind Ingress](https://kind.sigs.k8s.io/docs/user/ingress/) [G]

**Helm**
- 4.0.0 released Nov 12, 2025; latest v4.3.1. SSA default for new releases; flag renames; post-renderer plugins; Wasm plugins; kstatus; OCI digests; Charts v3 experimental.
- Helm 3: final feature release Sep 9, 2026; security fixes end Feb 10, 2027.
- Sources: [Helm 4 Overview](https://helm.sh/docs/overview) [S]; [Helm 3 EOL](https://helm.sh/blog/helm-v3-end-of-life) [S]

**Argo CD 3.x**, from tags and upgrade guides [R][G]:
- **3.0.0 (May 6, 2025):**
  - Fine-grained RBAC: `update`/`delete` no longer cascade to managed resources.
  - `logs` RBAC enforced.
  - Default `resource.exclusions` for high-churn kinds (Endpoints, EndpointSlice, Lease, …).
  - **Annotation-based resource tracking by default.**
  - Legacy repo config in `argocd-cm` removed.
  - Helm 3.17.1.
  - [2.14→3.0](https://argo-cd.readthedocs.io/en/stable/operator-manual/upgrading/2.14-3.0/) [G]
- **3.1:** OIDC PKCE handled server-side; v1 Actions API deprecated; Helm 3.18.4; Kustomize 5.7.0. — [3.0→3.1](https://argo-cd.readthedocs.io/en/stable/operator-manual/upgrading/3.0-3.1/) [G]
- **3.2:** Hydration paths must be non-root; Kustomize version respected in `.argocd-source.yaml`. — [3.1→3.2](https://argo-cd.readthedocs.io/en/stable/operator-manual/upgrading/3.1-3.2/) [G]
- **3.3:** The ApplicationSet CRD exceeds the client-side apply size, so install with server-side apply; Helm 3.19.2; Kustomize 5.8.0. — [3.2→3.3](https://argo-cd.readthedocs.io/en/stable/operator-manual/upgrading/3.2-3.3/) [G]
- **3.4:** Cluster version format change; `Missing` health handling fixed. — [3.3→3.4](https://argo-cd.readthedocs.io/en/stable/operator-manual/upgrading/3.3-3.4/) [G]
- **3.5.0 (Aug 4, 2026):**
  - **Helm upgraded to 4.2.0.** `spec.source.helm.version: v3` is now ignored, and plain-HTTP OCI registries need explicit flags.
  - Source Hydrator Beta.
  - GnuPG verification replaced by "Source Integrity".
  - mTLS for repo-server.
  - [3.4→3.5](https://argo-cd.readthedocs.io/en/stable/operator-manual/upgrading/3.4-3.5/) [G]; [Source Hydrator](https://argo-cd.readthedocs.io/en/stable/user-guide/source-hydrator/) [G]
- **3.6 (rc4, Oct 22, 2026; not yet GA):** `ServerSideApply=true` now implies Server-Side Diff; default local include paths now cover Helm template helpers and `Chart.lock`; GitOps Promoter health checks. — [3.5→3.6](https://argo-cd.readthedocs.io/en/latest/operator-manual/upgrading/3.5-3.6/) [G]

**Other tools**
- Kubernetes Dashboard archived; Headlamp recommended. — [K8s blog Jun 1, 2026](https://kubernetes.io/blog/2026/06/01/dashboard-to-headlamp/) [G]
- Argo CD Image Updater is now CRD-based (v1.x, latest v1.4.0). — [repo](https://github.com/argoproj-labs/argocd-image-updater) [R]
- Flux latest v2.10.0. — [repo](https://github.com/fluxcd/flux2) [R]
- k9s latest v0.51.0. — [repo](https://github.com/derailed/k9s) [R]

### Inferences
- **"Must update in the lesson" list for anything adapted from pre-2025 material:**
  - Sidecars as `initContainers` with `restartPolicy: Always`.
  - Gateway API instead of ingress-nginx.
  - `--server-side --force-conflicts` for the Argo CD install.
  - Helm 4 flags.
  - Annotation tracking in Argo CD.
  - kubeconfig context `kind-kind` on kind v0.33 / K8s 1.37.
- Docker Desktop on Apple Silicon should already be cgroup v2, so the cgroup v1 removal is a non-issue for this audience. Still include `docker info | grep -i cgroup` as a 10-second sanity check, since the course says "kind v0.33 cgroup notes". This is inference: I did not verify Docker Desktop's cgroup version in a primary source.
- Gateway API v1.7.0 is one day old. Lessons should pin to the Standard channel features available since v1.0 (Gateway, HTTPRoute) so they don't depend on the latest release.

### Gaps
- The official Gateway API v1.7 announcement blog post wasn't found; it was probably not yet published, given the tag dates from Oct 29, 2026.
- Release dates for Argo CD 3.1 to 3.4 and for Helm 4.1 to 4.3 were not collected; only the tags were.
- I don't know the newest standalone Kustomize release, only that Argo CD 3.3 bundles Kustomize 5.8.0.
- Argo CD's "tested Kubernetes versions" table is generated at release time and was empty in the source tree, so I can't state which K8s versions Argo CD 3.5 officially tests.

## Q4. Which free local exercises on kind build intuition for each lesson?

### Takeaway
Every lesson can run free on one laptop:
- kind v0.33 on Docker Desktop (Apple Silicon, arm64 binary from Homebrew).
- metrics-server for HPA.
- cloud-provider-kind for LoadBalancer, Gateway and Ingress.
- A free GitHub repo (or in-cluster Git) for Argo CD.

The best exercises are "break it, observe, fix it" loops that make the control loop visible.

### Cited Findings

**Setup facts for Mac with Apple Silicon and Docker Desktop**
- Install: `brew install kind` (or the `kind-darwin-arm64` binary). Load local images with `kind load docker-image my-app:tag`. List node images with `docker exec -it <node> crictl images`. — [kind Quick Start](https://kind.sigs.k8s.io/docs/user/quick-start/) [L]
- Docker Desktop memory: kind recommends at least 6 GB, preferably 8 GB, for node-image builds. Increase Docker's limits if clusters misbehave. — [kind Quick Start](https://kind.sigs.k8s.io/docs/user/quick-start/) [L]; [kind Known Issues](https://kind.sigs.k8s.io/docs/user/known-issues/) [G]
- Multi-node clusters: add `- role: worker` lines to a kind config. Multiple control-plane nodes simulate HA. — [kind Configuration](https://kind.sigs.k8s.io/docs/user/configuration/) [G]
- Host access to a NodePort: `extraPortMappings` (`containerPort: 30950` → `hostPort: 80`) with `nodePort: 30950`. — [kind Configuration](https://kind.sigs.k8s.io/docs/user/configuration/) [G]
- LoadBalancer, Gateway and Ingress: install with `brew install cloud-provider-kind`, or run it as a container.
  - On Mac, LB IPs are exposed via a port-mapped `kindccm-…` container on `localhost`.
  - It needs permission to listen on privileged ports.
  - [cloud-provider-kind README](https://github.com/kubernetes-sigs/cloud-provider-kind) [R]
- metrics-server needs `--kubelet-insecure-tls` on kind (testing only). — [metrics-server README](https://github.com/kubernetes-sigs/metrics-server) [R]
- NetworkPolicy works on default kind, because kindnetd embeds kube-network-policies. — kind source [R]

**Exercises by lesson.** Expected observations are illustrative unless marked (doc).

| Lesson | Exercise (≈40-min lesson budget: 15–20 min hands-on) | What it teaches |
|---|---|---|
| K1 | (a) `kind create cluster`. Then `docker ps` (one container = one node) and `docker exec -it kind-control-plane crictl ps` (control-plane components are just containers). (b) `kubectl -n kube-system delete pod -l k8s-app=kube-dns` and watch new CoreDNS Pods appear with `-w`. (c) Create a 1 control-plane + 2 worker cluster from a config file. | Nodes are machines (here, containers). Controllers recreate what you delete. |
| K2 | (a) Generate YAML with `--dry-run=client -o yaml`, edit and apply. (b) Apply the init + sidecar Pod from Q1/K2 and watch `Init:0/2 → Running`. (c) Make a Pod that runs `sh -c "exit 1"` and watch STATUS go `Error → CrashLoopBackOff` with growing back-off (10s, 20s, 40s … cap 5 min, doc). Repeat with `restartPolicy: Never` to see phase `Failed`. (d) `kubectl explain pod.spec --recursive \| less`. (e) Create namespaces dev and prod, the same Pod name in both, and switch with `kubectl config set-context --current --namespace=dev`. | Phase vs STATUS. Restart policy. Init and sidecar ordering. Namespaces as folders. Contexts. |
| K3 | (a) Deploy nginx:1.26 ×3, `set image` to 1.27, and watch with `kubectl get rs -w` (two ReplicaSets trade replicas within 25%/25%). (b) Roll out a non-existent tag, see a stuck rollout and `ImagePullBackOff` while old Pods keep serving, then `rollout undo`. (c) Delete a Pod and see a new name. (d) `kubectl label pod <one> app-` to remove the label; the RS creates a replacement and the orphan lives on. | Desired-state loop. Rollouts are ReplicaSet swaps. Labels are glue. |
| K4 | (a) ClusterIP Service + busybox client: `nslookup web`, `wget`. (b) Watch EndpointSlices as you scale and as a readiness probe fails. (c) Break the selector with a typo, see 0 endpoints, fix it. (d) Default-deny NetworkPolicy, then allow `role=client`. (e) NodePort via `extraPortMappings`. (f) Bonus: LoadBalancer via cloud-provider-kind, reached through localhost on Mac. | Stable address over churning Pods. DNS. kube-proxy and EndpointSlices. Isolation needs policy. |
| K5 | (a) ConfigMap as env and as a volume. Edit it: the file changes after a short delay, the env var doesn't until `kubectl rollout restart`. (b) Create a Secret, `-o yaml`, `base64 -d`: "this is not encryption". (c) Optional: `docker exec kind-control-plane` and use etcdctl inside the etcd Pod to show the Secret stored in the clear. Advanced, needs the etcd certs path. (d) Kustomize `configMapGenerator` and observe the hash-suffixed name and automatic rollout. | Config injection semantics. Secret reality. |
| K6 | (a) Memory hog over its limit gives `OOMKilled`, exit 137 (doc example `memory-demo-2`). (b) CPU hog with a CPU limit gives throttling (watch `kubectl top pod`, it doesn't die). (c) `kubectl get pod -o jsonpath='{.status.qosClass}'` for three Pods, one per QoS class. (d) HPA walkthrough: php-apache + load-generator, watch `kubectl get hpa -w` scale out and, after ~5 min of stabilization, back in. (e) In-place resize: `kubectl patch pod … --subresource resize` and confirm the restart count stays 0. (f) Liveness probe pointing at a slow endpoint gives a restart storm; switch it to a startup probe. (g) 3-node kind: taint a worker `NoSchedule`, add a toleration, use `nodeSelector`. Add a PDB `minAvailable: 2` and see `kubectl drain kind-worker --ignore-daemonsets` block. | Requests/limits/QoS. Probe semantics. HPA loop. Scheduling controls. PDB. |
| K7 | (a) Follow the K8s blog Gateway-on-kind walkthrough: `kubectl get gateway` shows `PROGRAMMED True` (doc). On Mac, reach it through the `kindccm` port mapping. (b) Add a second HTTPRoute that splits traffic 90/10 with `backendRefs` weights. (c) Write a classic Ingress for the same app, compare, and run `ingress2gateway` on it. (d) PVC on the `standard` StorageClass: write a file, delete the Pod, re-mount, data survives. (e) StatefulSet + headless Service: Pods `web-0`, `web-1`; `nslookup web-0.<svc>`; delete `web-0` and the same name and PVC come back; delete the StatefulSet and the PVCs remain. | Front-door routing roles. Ingress vs Gateway. Persistent identity and storage. |
| K8 | (a) Convert K3/K4 YAML into `base/` + `overlays/{dev,prod}`, then `kubectl kustomize`, `kubectl diff -k` and `apply -k`. (b) `helm create`, `helm template`, install, upgrade with `--set`, `history`, `rollback`. Try `--rollback-on-failure` with a deliberately broken value. (c) Discuss: render Helm output then patch with Kustomize. | Templating vs patching. Releases and revisions. |
| K9 | "Break-it bingo". The instructor applies 6 broken manifests: bad tag, bad command, missing ConfigMap key, oversized request (Pending), wrong readiness port (0 endpoints), Service selector typo. Learners follow the bottom-up flow (get → describe → logs --previous → events → endpoints → port-forward). Then `kubectl debug -it <pod> --image=busybox:1.36 --target=<container>` on a distroless Pod. Then k9s. Then RBAC: ServiceAccount + Role (get/list pods) + RoleBinding, verified with `kubectl auth can-i … --as=system:serviceaccount:…`. | A repeatable diagnosis method. Ephemeral debug containers. RBAC basics. |
| G1 | Install Argo CD with `--server-side --force-conflicts`, port-forward, log in, and create the guestbook app (doc command). Then: (a) manual sync; (b) enable auto-sync; `kubectl scale` the deployment live gives OutOfSync, then turn on `selfHeal` and watch it revert; (c) delete a manifest in your fork, nothing is pruned until `prune: true`. | Git as desired state. Sync vs health. Drift and self-heal. |
| G2 | In your own free GitHub repo: `apps/web/base` + `overlays/{dev,staging,prod}`. (a) ApplicationSet (list generator over env) creates 3 Apps. (b) Promote by PR: bump `newTag` in dev, then copy it to staging and prod. (c) Add a sync-wave −1 ConfigMap and a PostSync smoke-test Job. Break the smoke test and watch the sync fail. (d) App-of-apps "root" Application bootstrapping the ApplicationSet. (e) Install Sealed Secrets, `kubeseal` a Secret, commit the SealedSecret, and see it decrypted only in-cluster. (f) Optional: Argo CD Image Updater with `git` write-back. | Environments, promotion, multi-app management, ordering, safe secrets. |

### Inferences
- Use one cluster config for the whole course: 1 control-plane + 2 workers, with `extraPortMappings` for 80/443. K6 scheduling and PDB exercises need workers, and this config also keeps the K1 "nodes are containers" lesson concrete. Recreate the cluster freely (`kind delete cluster`), since it takes about a minute.
- For G1/G2, a public GitHub repo is the simplest free Git server. Running Gitea in-cluster avoids needing a GitHub account but adds a moving part. I did not research Gitea's Helm chart this session.
- On Apple Silicon, choose multi-arch images (`nginx`, `busybox`, `registry.k8s.io/*`, `curlimages/curl`). Older single-arch amd64 demo images fail with `exec format error`. This is general knowledge, not verified per image this session.

### Gaps
- I did not test any exercise on an actual kind v0.33 / Docker Desktop cluster. Commands and outputs come from docs, or are marked illustrative.
- I don't know whether cloud-provider-kind under Docker Desktop on macOS needs `sudo` for ports below 1024 in its current version. The README says it "needs permissions … to listen on privileged ports", so the writer should test.
- Gitea, Kargo, and SOPS with Argo CD were not researched.
- **Video channel attribution.** YouTube was blocked (oEmbed returned 403), so channels are named only where search snippets said so:
  - TechWorld with Nana for `MeU5_k9ssrs`.
  - Kunal Kushwaha for `8YLsQIG2Svo`.
  - Viktor Farcic for `iQB5j_2rSBA` and `797ptFfuL5g`.
  - Akuity for `2pvGL0zqf9o`.

  All other video URLs are listed by title only. TechWorld with Nana's flagship 4-hour Kubernetes course (ID `X48VuDVv0do`) appeared only on aggregator sites, not as a youtube.com URL, so it is not listed as a link. No KodeKloud or official CNCF/KubeCon beginner video URL surfaced in the searches.
