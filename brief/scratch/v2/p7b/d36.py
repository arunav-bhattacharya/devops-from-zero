"""Day 36: Traffic and storage: Gateway API, Ingress and volumes."""
from svg import arrow, box, cap, svg


def diagram():
    h = 44
    p = [
        box(16, 24, 128, h, "bxp", "GatewayClass"),
        box(192, 24, 112, h, "bxp", "Gateway"),
        box(368, 24, 112, h, "bxg", "HTTPRoute"),
        arrow(192, 46, 146, 46, dashed=True), cap(169, 38, "uses"),
        arrow(368, 46, 306, 46, dashed=True), cap(337, 38, "attaches"),
        box(16, 150, 112, h, "bx", "curl :8888"),
        box(176, 150, 128, h, "bxo", "Envoy proxy"),
        box(368, 110, 136, h, "bxt", "hello-devops"),
        box(368, 190, 136, h, "bxt", "hello-canary"),
        arrow(128, 172, 174, 172),
        cap(72, 212, "port-forward"),
        arrow(248, 68, 240, 148, dashed=True), cap(212, 112, "creates"),
        arrow(424, 68, 292, 148, dashed=True), cap(420, 100, "rules"),
        arrow(304, 164, 366, 136), cap(344, 168, "90%"),
        arrow(304, 180, 366, 208), cap(326, 210, "10%"),
    ]
    return svg(250, "Gateway API on kind: GatewayClass, Gateway and HTTPRoute configure an Envoy proxy that splits requests 90 to 10 between two Services", p)


LESSON = {
    "id": "d36",
    "title": "Traffic and storage: Gateway API, Ingress and volumes",
    "minutes": 50,
    "goal": "By the end you can route outside traffic to hello-devops through a Gateway, send a small share of it to a canary, end TLS at the Gateway, and give a Pod storage that outlives it.",
    "guess": {
        "q": "On a fresh kind cluster with nothing extra installed, you run `kubectl apply` on a Gateway and an HTTPRoute. What happens?",
        "options": [
            "Traffic starts flowing, because Kubernetes ships a default proxy",
            "The apply fails, because the cluster does not know these object types",
            "Kubernetes downloads Envoy and starts it for you",
            "The objects are saved, and the old Ingress controller serves them",
        ],
        "answer": 1,
        "why": "The Gateway API is not built in. Until you install its CRDs, the API server rejects the objects with \"no matches for kind\", and even then nothing routes until a controller such as Envoy Gateway runs.",
    },
    "terms": [
        {"term": "Ingress", "plain": "The older Kubernetes object for HTTP routing into a cluster; its API is now frozen."},
        {"term": "Gateway API", "plain": "The newer official routing objects (GatewayClass, Gateway, HTTPRoute), installed as CRDs."},
        {"term": "Gateway", "plain": "An entry point with listeners, such as HTTP on port 80, run by a proxy that a controller starts."},
        {"term": "HTTPRoute", "plain": "Rules that match requests by path, header or host and send them to Services, with optional weights."},
        {"term": "PersistentVolumeClaim (PVC)", "plain": "An app's request for storage of a given size and access mode."},
        {"term": "PersistentVolume (PV)", "plain": "A piece of real storage in the cluster that a claim binds to."},
        {"term": "StorageClass", "plain": "A type of storage the cluster can create on demand when a claim asks for it."},
        {"term": "StatefulSet", "plain": "Like a Deployment, but each Pod keeps a stable name and its own volume."},
    ],
    "sections": [
        {
            "h": "Getting traffic in from outside",
            "body": (
                "So far you have reached hello-devops in two ways: the NodePort that kind maps to localhost:8081 (Day 33), and `kubectl port-forward`. "
                "Both are fine on a laptop. Neither is how real users arrive.\n\n"
                "Traffic that enters the cluster from outside is called north-south traffic. Traffic between Services inside the cluster is east-west. "
                "For north-south HTTP traffic you usually want:\n"
                "- One entry point for many apps, so you pay for one load balancer instead of ten.\n"
                "- Routing by host name and path, such as `shop.example.com/api` to one Service and `/` to another.\n"
                "- TLS in one place, so each app does not handle its own certificates.\n"
                "- Gradual releases, such as sending 10% of requests to a new version.\n\n"
                "A Service of type LoadBalancer gives you an address, but it works with connections (layer 4). It never looks at a URL path or a header. "
                "For that you need a proxy that understands HTTP (layer 7), plus a Kubernetes object that tells the proxy what to do. "
                "Kubernetes has two such APIs: the older Ingress and the newer Gateway API."
            ),
            "refs": [
                {"title": "Service (Kubernetes docs)", "url": "https://kubernetes.io/docs/concepts/services-networking/service/", "kind": "docs"},
                {"title": "What is Gateway API for Kubernetes? Find out in ten minutes", "url": "https://www.youtube.com/watch?v=yWD_FGMJOCw", "kind": "watch"},
            ],
        },
        {
            "h": "Ingress, and why it is fading",
            "body": (
                "An Ingress is a Kubernetes object with HTTP routing rules: host names, paths and the Service each one goes to. "
                "It has been stable since Kubernetes 1.19, and you will see it in many clusters and tutorials. "
                "An Ingress does nothing by itself. An Ingress controller, a proxy running in the cluster, reads the objects and does the routing.\n\n"
                "Two things changed:\n"
                "- The Ingress API is frozen. It stays supported, but it gets no new features, and the [Ingress docs](https://kubernetes.io/docs/concepts/services-networking/ingress/) recommend Gateway instead.\n"
                "- ingress-nginx, the most popular community controller, was retired on March 24, 2026. Existing installs keep running, with no more releases, bug fixes or security patches.\n\n"
                "Ingress was small on purpose: hosts, paths and TLS. Everything else, such as rewrites, timeouts or canary weights, went into annotations that each controller defined its own way. "
                "A config written for one controller rarely worked on another.\n\n"
                "If you meet ingress-nginx at work, treat it as a migration. `kubectl get pods -A -l app.kubernetes.io/name=ingress-nginx` finds it. "
                "[Ingress2Gateway](https://kubernetes.io/blog/2026/03/20/ingress2gateway-1-0-release/) translates Ingress objects and many ingress-nginx annotations into Gateway API objects, and warns about what it cannot translate. "
                "Do not confuse ingress-nginx with F5's NGINX Ingress Controller, which is a separate product."
            ),
            "refs": [
                {"title": "Ingress", "url": "https://kubernetes.io/docs/concepts/services-networking/ingress/", "kind": "docs"},
                {"title": "Ingress NGINX retirement: what you need to know", "url": "https://kubernetes.io/blog/2025/11/11/ingress-nginx-retirement/", "kind": "read"},
                {"title": "Before you migrate: five surprising Ingress-NGINX behaviors", "url": "https://kubernetes.io/blog/2026/02/27/ingress-nginx-before-you-migrate/", "kind": "read"},
            ],
        },
        {
            "h": "The Gateway API: one object per role",
            "body": (
                "The **Gateway API** is the newer, official set of objects for routing traffic into a cluster. "
                "It is not built into Kubernetes. You install it as CRDs (custom resource definitions: new object types that the API server learns), plus a controller that implements them. "
                "Until the CRDs exist, applying a Gateway fails with \"no matches for kind\".\n\n"
                "It splits the job by who owns what:\n"
                "- GatewayClass: which controller handles Gateways of this class. The platform team creates it once per cluster.\n"
                "- Gateway: an entry point with one or more listeners, such as \"HTTP on port 80\". The controller starts a proxy for it.\n"
                "- HTTPRoute: routing rules for one app, such as \"`/` goes to Service `hello-devops` on port 80\". App teams own these and attach them to a Gateway.\n\n"
                "A Gateway's `allowedRoutes` decides which namespaces may attach routes. The lab allows all of them, which is easy on a laptop. At work you would pick `Same` or a label selector.\n\n"
                "Features that Ingress hid in annotations are real fields here: header matching, weights, redirects, rewrites and timeouts. "
                "Because they are fields, they behave the same across implementations such as Envoy Gateway, Istio, Cilium, Traefik and the cloud providers' load balancers.\n\n"
                "The Gateway API ships on its own schedule, separate from Kubernetes. Version 1.7 is the newest. "
                "Each release has a Standard channel (stable) and an Experimental channel. Stick to Standard: everything in this lesson has been Standard since 1.0."
            ),
            "refs": [
                {"title": "Gateway API (Kubernetes docs)", "url": "https://kubernetes.io/docs/concepts/services-networking/gateway/", "kind": "docs"},
                {"title": "Gateway API project site", "url": "https://gateway-api.sigs.k8s.io/", "kind": "docs"},
                {"title": "Mastering Kubernetes Gateway API (Is it Observable)", "url": "https://www.youtube.com/watch?v=HLXyrQT8zV0", "kind": "watch"},
            ],
        },
        {
            "h": "Envoy Gateway on kind, step by step",
            "body": (
                "To try it you need one implementation. This course uses Envoy Gateway, an open source controller that runs the Envoy proxy (Envoy itself is a CNCF project). "
                "One `helm install` brings the controller and its own copy of the Gateway API CRDs. "
                "Envoy Gateway 1.9 bundles Gateway API 1.6, which is fine, because the lab uses only Standard features.\n\n"
                "When you run `kubectl apply -k k8s/gateway`, this happens:\n"
                "1. The GatewayClass `eg` names the controller `gateway.envoyproxy.io/gatewayclass-controller`. Envoy Gateway sees its own name and accepts the class.\n"
                "2. The Gateway `hello-gateway` uses class `eg`, so Envoy Gateway creates an Envoy proxy Deployment and Service for it in `envoy-gateway-system`.\n"
                "3. The HTTPRoute `hello-devops` attaches to `hello-gateway` and points at the `hello-devops` Service.\n"
                "4. Envoy Gateway turns the route into Envoy settings and sends them to the proxy, which starts forwarding.\n\n"
                "kind has one catch. The proxy's Service has type LoadBalancer. On a cloud, that creates a real load balancer with an address. "
                "A kind cluster has no cloud, so the Service never gets one. "
                "As a result, `kubectl get gateway -n hello` shows PROGRAMMED `False` with the message \"No addresses have been assigned to the Gateway\". "
                "This is expected. The routing behind it works, and you reach the proxy with `kubectl port-forward`, as the [Envoy Gateway quickstart](https://gateway.envoyproxy.io/docs/tasks/quickstart/) does.\n\n"
                "If you want a real address on kind, a small tool called [cloud-provider-kind](https://github.com/kubernetes-sigs/cloud-provider-kind) acts as a cloud load balancer for kind clusters. "
                "On a Mac it exposes the address through a port on localhost. For one app on a laptop, port-forward is enough."
            ),
            "refs": [
                {"title": "Envoy Gateway quickstart", "url": "https://gateway.envoyproxy.io/docs/tasks/quickstart/", "kind": "docs"},
                {"title": "Experimenting with Gateway API using kind (Kubernetes blog)", "url": "https://kubernetes.io/blog/2026/01/28/experimenting-gateway-api-with-kind/", "kind": "read"},
            ],
        },
        {
            "h": "Matching, canary weights and TLS",
            "body": (
                "An HTTPRoute holds a list of rules, and each rule has matches and backends. A match can test:\n"
                "- The path, such as `PathPrefix /api` or `Exact /healthz`.\n"
                "- Headers, such as `x-canary: always`.\n"
                "- The HTTP method and query parameters.\n\n"
                "When several rules match one request, the most specific one wins. A longer path beats a shorter one, and with equal paths, more header matches win. "
                "You do not need to order rules by hand.\n\n"
                "A rule can send traffic to more than one backend, with weights. Weights 90 and 10 send about 9 of every 10 requests to the first Service and 1 to the second. "
                "That is a canary release: a new version gets a small share of real traffic while you watch its errors and latency. "
                "If it looks good, you move the weights. If not, you set the canary to 0. "
                "The lab's `k8s/gateway/httproute-canary.yaml` does this, and adds a header rule so testers can always reach the canary.\n\n"
                "TLS is set on the Gateway, not on each route. An HTTPS listener with `tls.mode: Terminate` decrypts at the proxy, with a certificate and key from a Secret of type `kubernetes.io/tls`. "
                "The proxy then sends plain HTTP to your Pods inside the cluster. Apps stay simple, and one team manages certificates in one place. "
                "At work, cert-manager usually creates and renews those Secrets. In the lab you make a self-signed certificate with `openssl`, so `curl` needs `-k` to accept it."
            ),
            "refs": [
                {"title": "HTTPRoute traffic splitting (Envoy Gateway)", "url": "https://gateway.envoyproxy.io/docs/tasks/traffic/http-traffic-splitting/", "kind": "docs"},
                {"title": "Secure gateways with TLS (Envoy Gateway)", "url": "https://gateway.envoyproxy.io/docs/tasks/security/secure-gateways/", "kind": "docs"},
            ],
        },
        {
            "h": "Storage: volumes that outlive Pods",
            "body": (
                "Containers lose their files when they restart, because each start begins again from the image. "
                "A volume is a folder that Kubernetes mounts into a container. Some volumes are short-lived: an `emptyDir` is created with its Pod and deleted with it. "
                "It suits scratch files and sharing files between containers in one Pod.\n\n"
                "For data that must survive the Pod, there are three objects:\n"
                "- A **PersistentVolume** (PV) is a piece of real storage: a cloud disk, a network share or a folder on a node.\n"
                "- A PersistentVolumeClaim (PVC) is an app's request for storage: \"1Gi that one node can read and write\".\n"
                "- A StorageClass is a type of storage the cluster can create on demand.\n\n"
                "You mostly write PVCs. When a PVC names a StorageClass, or the cluster has a default one, the class's provisioner creates a matching PV. "
                "That is called dynamic provisioning. kind's default class is called `standard`. It uses the local-path provisioner, which makes a folder on a node. "
                "Two of its settings matter:\n"
                "- `volumeBindingMode: WaitForFirstConsumer`: the PV is created only when a Pod uses the claim, on that Pod's node.\n"
                "- `reclaimPolicy: Delete`: deleting the PVC also deletes the PV and the data.\n\n"
                "Access modes say who may mount a volume. The mode `ReadWriteOnce` (RWO) means one node at a time, the usual case for disks. "
                "The mode `ReadWriteMany` (RWX) needs network storage such as NFS. Two more modes exist: `ReadOnlyMany` and `ReadWriteOncePod`."
            ),
            "refs": [
                {"title": "Persistent volumes", "url": "https://kubernetes.io/docs/concepts/storage/persistent-volumes/", "kind": "docs"},
                {"title": "Storage classes", "url": "https://kubernetes.io/docs/concepts/storage/storage-classes/", "kind": "docs"},
                {"title": "Volumes", "url": "https://kubernetes.io/docs/concepts/storage/volumes/", "kind": "docs"},
            ],
        },
        {
            "h": "StatefulSets, and why managed databases often win",
            "body": (
                "A Deployment treats its Pods as interchangeable. They get random names, and any one can replace any other. "
                "A database cannot work like that: replica 0 might be the primary, and each replica needs its own disk.\n\n"
                "A StatefulSet gives each Pod:\n"
                "- A stable name with a number, such as `redis-0` and `redis-1`.\n"
                "- Its own PVC from a `volumeClaimTemplates` section, such as `data-redis-0`. A replacement Pod gets the same PVC back.\n"
                "- A stable DNS name through a headless Service (Day 33), such as `redis-0.redis.hello.svc.cluster.local`.\n"
                "- Ordered start and stop: `redis-0` first, then `redis-1`.\n\n"
                "Deleting a StatefulSet does not delete its PVCs. That protects your data, and it means you clean up by hand.\n\n"
                "You can run databases this way. Operators (controllers built for one database, such as CloudNativePG for Postgres) automate a lot of the work. "
                "Still, backups, upgrades, replication and failover become your job. "
                "Many teams keep the cluster for stateless apps and pay for a managed database such as Amazon RDS or Cloud SQL. "
                "My rule of thumb: if losing the data would hurt the business, start with a managed database, and move it into the cluster only for a real reason. "
                "The lab's Redis has no volume at all, because it only holds a demo counter. Go deeper below to give it one."
            ),
            "refs": [
                {"title": "StatefulSets", "url": "https://kubernetes.io/docs/concepts/workloads/controllers/statefulset/", "kind": "docs"},
            ],
        },
    ],
    "analogy": (
        "The Gateway is the reception desk of an office building, and the GatewayClass is the company that staffs it. "
        "Each HTTPRoute is a line in the visitor book that a tenant writes: \"visitors for Acme go to floor 3, testers with a blue badge go to floor 4\". "
        "Tenants add their own lines without touching the desk. "
        "Where it breaks: a receptionist can use judgment, while the proxy follows the most specific matching rule and nothing else."
    ),
    "diagram": diagram(),
    "diagram_caption": "The objects on top configure the proxy below, which splits real requests between two Services.",
    "worked": {
        "title": "Data that survives its Pod",
        "steps": [
            {"say": "Check which storage the cluster offers. kind has one class, `standard`, marked as the default. It makes folders on nodes and deletes them with their claim.", "code": "$ kubectl get storageclass\nNAME                 PROVISIONER             RECLAIMPOLICY   VOLUMEBINDINGMODE      ALLOWVOLUMEEXPANSION   AGE\nstandard (default)   rancher.io/local-path   Delete          WaitForFirstConsumer   false                  3d", "lang": "console"},
            {"say": "Apply the demo file: a namespace, a 1Gi claim and a Pod that mounts it at `/data`. Because of `WaitForFirstConsumer`, the claim stays `Pending` until the Pod is scheduled; here that takes a few seconds.", "code": "$ kubectl apply -f k8s/storage/pvc-demo.yaml\nnamespace/storage-demo created\npersistentvolumeclaim/notes created\npod/writer created\n$ kubectl get pvc -n storage-demo\nNAME    STATUS   VOLUME                                     CAPACITY   ACCESS MODES   STORAGECLASS   VOLUMEATTRIBUTESCLASS   AGE\nnotes   Bound    pvc-3f1c2a9e-8d7b-4c55-9a0e-6b2f4d1e7c80   1Gi        RWO            standard       <unset>                 12s", "lang": "console"},
            {"say": "The provisioner created a PV for the claim and named it after the claim's ID. Nobody wrote a PV by hand: that is dynamic provisioning.", "code": "$ kubectl get pv\nNAME                                       CAPACITY   ACCESS MODES   RECLAIM POLICY   STATUS   CLAIM                STORAGECLASS   VOLUMEATTRIBUTESCLASS   REASON   AGE\npvc-3f1c2a9e-8d7b-4c55-9a0e-6b2f4d1e7c80   1Gi        RWO            Delete           Bound    storage-demo/notes   standard       <unset>                          14s", "lang": "console"},
            {"say": "The Pod adds one line to `/data/starts.log` each time it starts, then prints the file. One start so far.", "code": "$ kubectl logs writer -n storage-demo\nstarted at Fri Oct 30 10:20:11 UTC 2026", "lang": "console"},
            {"say": "Delete the Pod and create it again. The delete takes up to 30 seconds, because `sleep` ignores the polite stop signal. The new Pod mounts the same claim and finds the old line still there.", "code": "$ kubectl delete pod writer -n storage-demo\npod \"writer\" deleted from storage-demo namespace\n$ kubectl apply -f k8s/storage/pvc-demo.yaml\nnamespace/storage-demo unchanged\npersistentvolumeclaim/notes unchanged\npod/writer created\n$ kubectl logs writer -n storage-demo\nstarted at Fri Oct 30 10:20:11 UTC 2026\nstarted at Fri Oct 30 10:23:47 UTC 2026", "lang": "console"},
            {"say": "Find the data. On kind a node is a Docker container, and local-path keeps each volume in a folder under `/var/local-path-provisioner`, named after the PV, namespace and claim.", "code": "$ kubectl get pod writer -n storage-demo -o jsonpath='{.spec.nodeName}{\"\\n\"}'\ndevops-worker2\n$ docker exec devops-worker2 ls /var/local-path-provisioner\npvc-3f1c2a9e-8d7b-4c55-9a0e-6b2f4d1e7c80_storage-demo_notes", "lang": "console"},
            {"say": "Clean up. Deleting the namespace deletes the claim, and the `Delete` reclaim policy then removes the PV and its folder. With `Retain`, the PV and data would stay for you to recover.", "code": "$ kubectl delete namespace storage-demo\nnamespace \"storage-demo\" deleted\n$ kubectl get pv\nNo resources found", "lang": "console"},
        ],
    },
    "code_files": [
        ("yaml", "k8s/gateway/kustomization.yaml", "kubectl apply -k k8s/gateway"),
        ("yaml", "k8s/gateway/gatewayclass.yaml", "kubectl apply -k k8s/gateway"),
        ("yaml", "k8s/gateway/gateway.yaml", "kubectl apply -k k8s/gateway"),
        ("yaml", "k8s/gateway/httproute.yaml", "kubectl apply -k k8s/gateway"),
        ("yaml", "k8s/gateway/canary.yaml", "kubectl apply -f k8s/gateway/canary.yaml"),
        ("yaml", "k8s/gateway/httproute-canary.yaml", "kubectl apply -f k8s/gateway/httproute-canary.yaml"),
        ("yaml", "k8s/gateway/gateway-https.yaml", "kubectl apply -f k8s/gateway/gateway-https.yaml"),
        ("yaml", "k8s/storage/pvc-demo.yaml", "kubectl apply -f k8s/storage/pvc-demo.yaml"),
    ],
    "commands": [
        {"cmd": "helm install eg oci://docker.io/envoyproxy/gateway-helm --version v1.9.3 -n envoy-gateway-system --create-namespace", "what": "Install Envoy Gateway and its Gateway API CRDs. Check the quickstart for the current version."},
        {"cmd": "kubectl wait --timeout=5m -n envoy-gateway-system deployment/envoy-gateway --for=condition=Available", "what": "Wait until the Envoy Gateway controller is running."},
        {"cmd": "kubectl apply -k k8s/gateway", "what": "Create the GatewayClass, the Gateway and the HTTPRoute."},
        {"cmd": "kubectl get gatewayclass,gateway,httproute -A", "what": "List the Gateway API objects in all namespaces, with their status columns."},
        {"cmd": "kubectl describe httproute hello-devops -n hello", "what": "Show a route's conditions, such as Accepted and ResolvedRefs."},
        {"cmd": "ENVOY_SVC=$(kubectl get svc -n envoy-gateway-system -l gateway.envoyproxy.io/owning-gateway-name=hello-gateway -o name)", "what": "Find the Envoy proxy Service that belongs to hello-gateway."},
        {"cmd": "kubectl -n envoy-gateway-system port-forward $ENVOY_SVC 8888:80", "what": "Reach the Gateway on localhost:8888 (kind has no cloud load balancer)."},
        {"cmd": "kubectl apply -f k8s/gateway/canary.yaml -f k8s/gateway/httproute-canary.yaml", "what": "Start the canary Deployment and replace the route with a 90/10 split."},
        {"cmd": "curl -H \"x-canary: always\" localhost:8888", "what": "Send a request that the header rule always routes to the canary."},
        {"cmd": "openssl req -x509 -newkey rsa:2048 -nodes -days 30 -subj \"/CN=hello.local\" -keyout tls.key -out tls.crt", "what": "Make a self-signed certificate and key for local TLS tests."},
        {"cmd": "kubectl create secret tls hello-tls -n hello --cert=tls.crt --key=tls.key", "what": "Store the certificate and key as a TLS Secret the Gateway can use."},
        {"cmd": "kubectl get pods -A -l app.kubernetes.io/name=ingress-nginx", "what": "Check whether a cluster still runs the retired ingress-nginx controller."},
        {"cmd": "kubectl get storageclass", "what": "List the types of storage the cluster offers (kind has `standard`)."},
        {"cmd": "kubectl get pvc,pv -A", "what": "List storage claims and the volumes bound to them."},
    ],
    "mistake": (
        "You write an HTTPRoute, curl the Gateway and get a 404 or 500, then start changing the Gateway. "
        "Usually the route never attached or points at a Service name or port that does not exist. "
        "Run `kubectl describe httproute` first: the Accepted condition says whether the Gateway took the route, and ResolvedRefs says whether its backends exist."
    ),
    "real_world": (
        "At PayLite, the platform team owns one shared Gateway per cluster, with its TLS certificates renewed by cert-manager. "
        "Each product team writes HTTPRoutes for its own paths, and new versions of the card service start at 5% of traffic before the weights move. "
        "The card database is a managed service outside the cluster; only caches and queues run as StatefulSets."
    ),
    "task": {
        "title": "Put hello-devops behind a Gateway and run a canary",
        "steps": [
            "Install Envoy Gateway with Helm (check its quickstart for the current version) and wait until the `envoy-gateway` Deployment is Available.",
            "Write the four files in `k8s/gateway/` (kustomization, GatewayClass, Gateway, HTTPRoute) and apply them. Read `kubectl get gatewayclass,gateway,httproute -A` and explain the PROGRAMMED column.",
            "Find the Envoy proxy Service for your Gateway and port-forward local port 8888 to its port 80. Leave that terminal open.",
            "Run `curl localhost:8888` and check that hello-devops answers through the Gateway with its ConfigMap greeting.",
            "Apply `canary.yaml` and `httproute-canary.yaml`. Send 50 requests and count how many came from each version.",
            "Send a few requests with the header `x-canary: always` and check that the canary answers every one.",
            "Change the weights to 50 and 50, apply, and count again. Then restore the plain route with `kubectl apply -k k8s/gateway` and delete the canary with `kubectl delete -f k8s/gateway/canary.yaml`.",
            "Optional: make a self-signed certificate, store it as the Secret `hello-tls` in namespace `hello`, apply `gateway-https.yaml`, port-forward 8443 to 443, and run `curl -k https://localhost:8443`.",
            "Run the ingress-nginx check from the commands list and confirm your cluster has no retired controller.",
        ],
        "hints": [
            "`kubectl get svc -n envoy-gateway-system -l gateway.envoyproxy.io/owning-gateway-name=hello-gateway -o name` prints the Service in a form `kubectl port-forward` accepts.",
            "To count answers: `for i in $(seq 1 50); do curl -s localhost:8888 | jq -r .message; done | sort | uniq -c`. Expect roughly 45 and 5, never exact numbers.",
            "Route not working? `kubectl describe httproute hello-devops -n hello` shows Accepted and ResolvedRefs. A ResolvedRefs of False usually means a Service name or port is wrong.",
        ],
        "done_when": "`curl localhost:8888` answers through the Gateway, and 50 requests show mostly the main greeting with a few from the canary.",
    },
    "explain_back": {
        "prompt": "Explain in 3 to 4 sentences how one `curl localhost:8888` request can end up at the canary Pod. Mention the Gateway, the HTTPRoute, the weights and the Service.",
        "answer": (
            "Port-forward sends the request to the Envoy proxy that Envoy Gateway started for `hello-gateway`. "
            "Envoy checks the HTTPRoutes attached to that Gateway; my request has no `x-canary` header, so the 90/10 rule matches. "
            "Envoy picks a backend by weight, and about one request in ten goes to the `hello-canary` Service. "
            "That Service sends it to one of its ready Pods, which answers with the canary greeting."
        ),
    },
    "recap": [
        "Services give an address; HTTP routing by host, path and header needs Ingress or the Gateway API.",
        "The Ingress API is frozen, and ingress-nginx was retired on March 24, 2026 with no more security fixes.",
        "Gateway API roles: GatewayClass (controller), Gateway (listeners, TLS), HTTPRoute (app rules and weights).",
        "On kind, Envoy Gateway routes for real; PROGRAMMED stays False without a load balancer, so use port-forward.",
        "A PVC asks for storage, a StorageClass creates the PV, and `reclaimPolicy` decides what happens to the data.",
        "StatefulSets give each replica a stable name and its own PVC; many teams still prefer managed databases.",
    ],
    "check": [
        {
            "q": "A shop needs `/api` sent to Service `api` and every other path to Service `web`, through one Gateway. What do you write?",
            "options": [
                "A second GatewayClass for the API traffic",
                "Two Gateways, one for each Service",
                "An HTTPRoute with two rules that match on path",
                "A LoadBalancer Service with two ports",
            ],
            "answer": 2,
            "why": "Routing rules live in an HTTPRoute; the `/api` prefix rule is more specific, so it wins for those requests and `/` takes the rest.",
        },
        {
            "q": "On kind, `kubectl get gateway` shows PROGRAMMED False, \"No addresses have been assigned\", but curl through the port-forward works. What should you fix?",
            "options": [
                "Nothing: kind has no cloud load balancer to give the Gateway an address",
                "The HTTPRoute, because it did not attach to the Gateway",
                "The GatewayClass, because its controller name is wrong",
                "The Service, because its targetPort does not match",
            ],
            "answer": 0,
            "why": "Programmed is False only because the proxy's LoadBalancer Service never got an address; routing works, as the curl shows.",
        },
        {
            "q": "A Postgres Pod on kind keeps its data on a PVC from the `standard` class. You delete the whole namespace. What happens to the data?",
            "options": [
                "It stays on the PV until you delete the PV by hand",
                "It is deleted, because the class's reclaim policy is Delete",
                "It is saved into etcd until a new claim asks for it",
                "It moves to another node with free space",
            ],
            "answer": 1,
            "why": "Deleting the namespace deletes the PVC, and with `reclaimPolicy: Delete` the PV and its folder go too.",
        },
    ],
    "interview": [
        {
            "q": "Why is the Gateway API replacing Ingress?",
            "a": (
                "Ingress covered only hosts, paths and TLS, so every controller added its own annotations, and configs did not move between controllers. "
                "The Gateway API makes features such as header matching, weights and timeouts real fields that behave the same everywhere. "
                "It also splits ownership: the platform team runs GatewayClasses and Gateways, and app teams write Routes. "
                "On top of that, the Ingress API is frozen and ingress-nginx was retired in March 2026, so new clusters should start with Gateway API."
            ),
        },
        {
            "q": "Explain PV, PVC and StorageClass, and how dynamic provisioning works.",
            "a": (
                "A PVC is an app's request for storage, a PV is the actual storage, and a StorageClass describes a kind of storage and the provisioner that creates it. "
                "With dynamic provisioning, the app only writes a PVC; the class's provisioner creates a matching PV and the two are bound. "
                "The binding mode decides when that happens, often only once a Pod is scheduled, and the reclaim policy decides whether the data is deleted or kept with the claim. "
                "Access modes such as ReadWriteOnce limit how many nodes can mount it at once."
            ),
        },
        {
            "q": "Would you run your database in Kubernetes?",
            "a": (
                "It depends on the team and the data. A StatefulSet gives stable names and one volume per replica, and operators such as CloudNativePG automate failover and backups. "
                "But the team then owns backups, restores, upgrades and capacity, and has to test them. "
                "For business-critical data and a small team, I would start with a managed database and keep the cluster for stateless services and caches. "
                "I would move a database in only for a clear reason, such as cost at scale or a platform team that already runs operators well."
            ),
        },
    ],
    "deeper": {
        "minutes": 15,
        "body": (
            "The lab's Redis forgets the visit count every time its Pod restarts. A StatefulSet with a volume fixes that. "
            "Treat these steps as a sketch to try in a copy of `k8s/redis.yaml`, not as a change to the base:\n"
            "1. Change `kind: Deployment` to `kind: StatefulSet`, and add `serviceName: redis` under `spec`.\n"
            "2. Add a `volumeClaimTemplates` section with one template named `data`: access mode `ReadWriteOnce` and a request of `1Gi`. The StatefulSet makes one PVC per Pod, called `data-redis-0`.\n"
            "3. Mount the `data` volume at `/data` in the Redis container. The official Redis image keeps its files there.\n"
            "4. Turn on saving: run Redis with `redis-server --appendonly yes`, so each write also goes to disk.\n"
            "5. Apply it, count a few visits, then delete the Pod `redis-0`. It comes back with the same name and the same PVC, and the count carries on.\n\n"
            "Check the pieces with `kubectl get pvc -n hello` and `kubectl get pv`. On kind the PV is a folder inside a node container, so deleting the cluster deletes the data. For practice that is fine.\n\n"
            "Things that surprise people:\n"
            "- Deleting a StatefulSet leaves its PVCs behind. You delete them yourself when you are sure.\n"
            "- A local-path volume lives on one node, so `redis-0` can only ever be scheduled there. If that node goes away, the Pod stays `Pending`. A cloud disk can attach to another node; a local folder cannot.\n"
            "- A StatefulSet wants a headless Service (`clusterIP: None`) so each Pod gets its own DNS name. Your existing `redis` Service is a normal one; for one replica that still works.\n"
            "- Scaling down does not delete the PVCs of removed Pods, so scaling back up finds the old data.\n\n"
            "Kubernetes 1.37 also changed two StatefulSet details you may read about. The `maxUnavailable` setting for rolling updates is on by default again. A new `Recreate` update strategy exists as an alpha feature.\n\n"
            "The traffic side has its own next step. cloud-provider-kind can give the Gateway a real address on your laptop. "
            "It runs on your Mac, watches the cluster, and exposes each LoadBalancer Service through a port on localhost. "
            "With it running, `kubectl get gateway` shows an address and PROGRAMMED True, which matches what you will see on a cloud. "
            "Read its README before you install it, because it needs permission to open ports on your machine."
        ),
    },
    "sources": [
        {"title": "Gateway API (Kubernetes docs)", "url": "https://kubernetes.io/docs/concepts/services-networking/gateway/"},
        {"title": "Envoy Gateway quickstart", "url": "https://gateway.envoyproxy.io/docs/tasks/quickstart/"},
        {"title": "Ingress NGINX retirement: what you need to know", "url": "https://kubernetes.io/blog/2025/11/11/ingress-nginx-retirement/"},
        {"title": "Persistent volumes", "url": "https://kubernetes.io/docs/concepts/storage/persistent-volumes/"},
    ],
}
