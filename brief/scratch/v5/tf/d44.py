NEW = {}

NEW["goal"] = "By the end you can route outside traffic to hello-devops through a Gateway, send a small share of it to a canary, end TLS at the Gateway, and give a Pod storage that outlives it."

NEW["opening"] = """Picture our restaurant moving into a food hall. Five kitchens share one street door, and guests should not have to know which side door leads to which kitchen. One host at the entrance sends each guest to the right place, checks the booking and, on test nights, sends one table in ten to the new tasting menu. There is a second problem, too. The cook keeps the night's tally on a chalkboard, and every time someone tidies up, the board is wiped.

Last time, probes and autoscaling kept the app healthy and sized for its visitors. But visitors still come in through a side door, a NodePort on one laptop port, and Redis forgets the visit count whenever its Pod restarts. Both feel fine on a laptop, which is why they are easy to leave alone.

In this lesson, we'll build a proper front entrance with routing rules, try a small canary release, lock the door with TLS and give a Pod storage that survives it. Before we start, make a guess, and keep it in mind."""

NEW["guess"] = (
    "On a fresh kind cluster with nothing extra installed, you run `kubectl apply` on a Gateway and an HTTPRoute, two objects for routing web traffic into the cluster. What happens?",
    "The Gateway API is not built in. Until you install its CRDs (new object types), the API server rejects the objects with \"no matches for kind\". Even then, nothing routes until a controller such as Envoy Gateway runs.",
)

NEW["terms"] = [
    "The older Kubernetes object for routing web traffic into a cluster; it gets no new features any more.",
    "The newer official routing objects (GatewayClass, Gateway, HTTPRoute), added to a cluster as new object types.",
    "An entry point with listeners, such as web traffic on port 80, served by a proxy that a controller starts.",
    "Rules that match requests by path, header or host name and send them to Services, with optional weights.",
    "An app's request for storage of a given size and access mode.",
    "A piece of real storage in the cluster that a claim is tied to.",
    "A type of storage the cluster can create on demand when a claim asks for it.",
    "Like a Deployment, but each Pod keeps a fixed name and its own volume.",
]

S = []

S.append(("Getting visitors in from outside", """
So far you have reached hello-devops in two ways. One is the NodePort that kind maps to localhost:8081 (Day 41). The other is `kubectl port-forward`, a tunnel from your Mac to one Pod. Both are fine on a laptop. Neither is how real users arrive.

Traffic that enters the cluster from outside is called north-south traffic. Traffic between Services inside the cluster is east-west. For north-south web traffic you usually want:
- One entry point for many apps, so you pay for one load balancer instead of ten. A load balancer spreads incoming visitors over several machines.
- Routing by host name and path, such as `shop.example.com/api` to one Service and `/` to another.
- TLS, the encryption behind `https://`, in one place, so each app does not handle its own certificates (the files that prove a site is who it says).
- Gradual releases, such as sending 10% of requests to a new version.

A Service of type LoadBalancer gives you an address, but it is a door with no host. It works with connections (layer 4, Day 11) and never looks at a web address or a header. A header is a labelled line of extra information sent with each web request.

Routing on paths and headers needs a proxy that understands web requests (layer 7). A proxy is a program that sits in front of your apps and passes each request on. It also needs a Kubernetes object that tells the proxy what to do. Kubernetes has two such APIs: the older Ingress and the newer Gateway API. We start with the older one, because you will meet it at work.
"""))

S.append(("Ingress, and why it is fading", """
An Ingress is a Kubernetes object with web routing rules: host names, paths and the Service each one goes to. It has been stable since Kubernetes 1.19, and you will see it in many clusters and tutorials. An Ingress does nothing by itself. An Ingress controller, a proxy running in the cluster, reads the objects and does the routing.

Two things changed:
- The Ingress API is frozen. It stays supported, but it gets no new features, and the [Ingress docs](https://kubernetes.io/docs/concepts/services-networking/ingress/) recommend Gateway instead.
- ingress-nginx, the most popular community controller, was retired on March 24, 2026. Existing installs keep running, with no more releases, bug fixes or security patches.

Ingress was small on purpose: hosts, paths and TLS. Everything else, such as rewrites, timeouts or canary weights, went into annotations (notes on the object) that each controller defined its own way. A config written for one controller rarely worked on another. It is like a host's book where every restaurant used its own shorthand in the margins.

If you meet ingress-nginx at work, treat it as a migration. `kubectl get pods -A -l app.kubernetes.io/name=ingress-nginx` finds it. [Ingress2Gateway](https://kubernetes.io/blog/2026/03/20/ingress2gateway-1-0-release/) translates Ingress objects and many ingress-nginx annotations into Gateway API objects, and warns about what it cannot translate. Do not confuse ingress-nginx with F5's NGINX Ingress Controller, which is a separate product.

The margin notes are the problem the newer API set out to fix. Next, we meet it.
"""))

S.append(("The Gateway API: one object per role", """
The **Gateway API** is the newer, official set of objects for routing traffic into a cluster. It is not built into Kubernetes. You install it as CRDs (custom resource definitions: new object types that the API server learns). You also install a controller, a program that reads those objects and acts on them. Until the CRDs exist, applying a Gateway fails with "no matches for kind". That is the answer to the guess.

It splits the job by who owns what, much like a food hall:
- GatewayClass: which controller handles Gateways of this class, like the company that staffs the entrance. The platform team creates it once per cluster.
- Gateway: an entry point with one or more listeners, such as "HTTP on port 80". It is the street door, and the controller starts a proxy for it.
- HTTPRoute: routing rules for one app, such as "`/` goes to Service `hello-devops` on port 80". It is each kitchen's line in the host's book. App teams own these and attach them to a Gateway.

A Gateway's `allowedRoutes` decides which namespaces may attach routes. On a shared Gateway that matters, because every attached route can claim hosts and paths for its own Services. The lab allows all of them, which is easy on a laptop. At work you would pick `Same` or a label selector.

Picture several product teams sharing one cluster through a single Gateway that the platform team owns. Each team writes HTTPRoutes for its own paths and never touches the door itself.

Features that Ingress hid in annotations are real fields here: header matching, weights, redirects, rewrites and timeouts. Because they are fields, they behave the same across implementations such as Envoy Gateway, Istio, Cilium, Traefik and the cloud providers' load balancers.

The Gateway API ships on its own schedule, separate from Kubernetes. Version 1.7 is the newest. Each release has a Standard channel (stable) and an Experimental channel. Stick to Standard: everything in this lesson has been Standard since 1.0. Objects alone route nothing, so next we install a controller.
"""))

S.append(("Envoy Gateway on kind, step by step", """
To try it you need one implementation. This course uses Envoy Gateway, an open source controller that runs the Envoy proxy. One `helm install` brings the controller and its own copy of the Gateway API CRDs. (Helm is a package installer for Kubernetes, and Day 45 covers it.)

When you run `kubectl apply -k k8s/gateway`, this happens:
1. The GatewayClass `eg` names the controller `gateway.envoyproxy.io/gatewayclass-controller`. Envoy Gateway sees its own name and accepts the class.
2. The Gateway `hello-gateway` uses class `eg`, so Envoy Gateway creates an Envoy proxy Deployment and Service for it in `envoy-gateway-system`.
3. The HTTPRoute `hello-devops` attaches to `hello-gateway` and points at the `hello-devops` Service.
4. Envoy Gateway turns the route into Envoy settings and sends them to the proxy, which starts forwarding.

The controller never handles a request. It watches objects and writes settings, and the Envoy Pods carry the traffic. The staffing company trains the host; the host greets the guests.

The proxy's Service has type LoadBalancer, which gives you one confusing status on kind. On a cloud, that type creates a real load balancer with an address. A kind cluster has no cloud, so the Service never gets one. `kubectl get gateway -n hello` then shows PROGRAMMED `False` with the message "No addresses have been assigned to the Gateway". You can ignore it. The routing behind it works, and you reach the proxy with `kubectl port-forward`, as the [Envoy Gateway quickstart](https://gateway.envoyproxy.io/docs/tasks/quickstart/) does.

A different failure looks similar: you write an HTTPRoute, curl the Gateway and get a 404 or 500. It is tempting to start changing the Gateway. Usually the route never attached, or it points at a Service name or port that does not exist. Run `kubectl describe httproute` first. Its Accepted condition says whether the Gateway took the route, and ResolvedRefs says whether its backends exist.

If you want a real address on kind, a small tool called [cloud-provider-kind](https://github.com/kubernetes-sigs/cloud-provider-kind) acts as a cloud load balancer for kind clusters. On a Mac it exposes the address through a port on localhost. For one app on a laptop, port-forward is enough. With the door working, next we teach the host some rules.
"""))

S.append(("Matching, canary weights and TLS", """
An HTTPRoute holds a list of rules, and each rule has matches and backends (the Services that receive the request). A match can test:
- The path, such as `PathPrefix /api` or `Exact /healthz`.
- Headers, such as `x-canary: always`.
- The HTTP method and query parameters (the `?name=value` part of a web address).

When several rules match one request, the most specific one wins. A longer path beats a shorter one, and with equal paths, more header matches win. You do not need to order rules by hand.

A rule can send traffic to more than one backend, with weights. Weights 90 and 10 send about 9 of every 10 requests to the first Service and 1 to the second. Envoy picks a backend for each request at random, in proportion to the weights, so 50 requests rarely split exactly 45 and 5. That is a canary release: a new version gets a small share of real traffic while you watch its errors and response times. It is the tasting menu served to one table in ten. If it looks good, you move the weights. If not, you set the canary to 0. The lab's `k8s/gateway/httproute-canary.yaml` does this, and adds a header rule so testers can always reach the canary.

You set TLS once, on the Gateway, instead of on each route. An HTTPS listener with `tls.mode: Terminate` decrypts at the proxy, with a certificate and key from a Secret of type `kubernetes.io/tls`. The proxy then sends plain web traffic to your Pods inside the cluster, like a host who checks every booking at the door so the kitchens do not have to. Apps stay simple, and one team manages certificates in one place. At work, cert-manager, a tool that requests and renews certificates, usually creates those Secrets. In the lab you make a self-signed certificate with `openssl`, so `curl` needs `-k` to accept it.

The last hop, from the proxy to your Pods, stays unencrypted. Part 15 shows how a service mesh encrypts traffic inside the cluster. That covers the front door. Next, the wiped chalkboard.
"""))

S.append(("Storage: volumes that outlive Pods", """
Containers lose their files when they restart, because each start begins again from the image. That is the chalkboard wiped at closing time. A volume is a folder that Kubernetes mounts into a container. Some volumes are short-lived: an `emptyDir` is created with its Pod and deleted with it. It suits scratch files and sharing files between containers in one Pod.

For data that must survive the Pod, there are three objects. Picture asking the building manager for a locker:
- A PersistentVolume (PV) is a piece of real storage: a cloud disk, a network share or a folder on a node. It is the actual locker.
- A PersistentVolumeClaim (PVC) is an app's request for storage: "1Gi that one node can read and write". It is the request form.
- A StorageClass is a type of storage the cluster can create on demand, like a kind of locker the building can install.

Why split the claim from the volume? The claim says only what the app needs, so the same PVC works on kind and on AWS. The details of the real disk stay in the PV.

You mostly write PVCs. When a PVC names a StorageClass, or the cluster has a default one, the class's provisioner (the program that makes storage) creates a matching PV. That is called dynamic provisioning. kind's default class is called `standard`. It uses the local-path provisioner, which makes a folder on a node. Two of its settings matter:
- `volumeBindingMode: WaitForFirstConsumer`: the PV is created only once a Pod uses the claim, on that Pod's node, so the folder sits where the Pod runs.
- `reclaimPolicy: Delete`: deleting the PVC also deletes the PV and the data.

Access modes say who may mount a volume. The mode `ReadWriteOnce` (RWO) means one node at a time, the usual case, because most disks attach to one machine at a time. The mode `ReadWriteMany` (RWX) needs network storage such as NFS, a way to share files over a network. Two more modes exist: `ReadOnlyMany` and `ReadWriteOncePod`. One locker works for one Pod. Next, apps whose every copy needs its own.
"""))

S.append(("StatefulSets, and why managed databases often win", """
A Deployment treats its Pods as interchangeable. They get random names, and any one can replace any other. A database cannot work like that. Replica 0 might be the primary copy that takes all writes, and each replica needs its own disk.

A StatefulSet gives each Pod:
- A fixed name with a number, such as `redis-0` and `redis-1`.
- Its own PVC from a `volumeClaimTemplates` section, such as `data-redis-0`. A replacement Pod gets the same PVC back.
- A fixed DNS name through a headless Service (Day 41), such as `redis-0.redis.hello.svc.cluster.local`.
- Ordered start and stop: `redis-0` first, then `redis-1`, so a primary can be up before the replicas that copy from it.

In the kitchen, these are named stations, "grill 0" and "grill 1", each with its own fridge that stays put when the cook changes. Deleting a StatefulSet does not delete its PVCs. That protects your data, and it means you clean up by hand.

You can run databases this way. Operators (controllers built for one database, such as CloudNativePG for Postgres) automate a lot of the work. Still, backups, upgrades, copying data between replicas and switching to a healthy copy become your job. Many teams keep the cluster for stateless apps and pay for a managed database such as Amazon RDS or Cloud SQL. Picture a payments product whose card database is a managed service outside the cluster, while only caches and queues run as StatefulSets.

**If losing the data would hurt the business, start with a managed database.** Move it into the cluster only for a real reason. The lab's Redis has no volume at all, because it only holds a demo counter, and Go deeper gives it one. First, the worked example shows a claim outliving its Pod.
"""))

NEW["sections"] = S

NEW["drop"] = ["analogy", "real_world", "mistake"]

NEW["diagram_caption"] = "The objects on top set up the proxy below, which splits real requests between two Services."

NEW["worked"] = [
    "Check which storage the cluster offers. kind has one class, `standard`, marked as the default. It makes folders on nodes and deletes them with their claim.",
    "Apply the demo file: a namespace, a 1Gi claim and a Pod that mounts it at `/data`. Because of `WaitForFirstConsumer`, the claim stays `Pending` until the Pod is scheduled; here that takes a few seconds.",
    "The provisioner created a PV for the claim and named it after the claim's ID. Nobody wrote a PV by hand: that is dynamic provisioning.",
    "The Pod adds one line to `/data/starts.log` each time it starts, then prints the file. One start so far.",
    "Delete the Pod and create it again. The delete takes up to 30 seconds, because `sleep` ignores the polite stop signal. The new Pod mounts the same claim and finds the old line still there.",
    "Find the data. On kind a node is a Docker container, and local-path keeps each volume in a folder under `/var/local-path-provisioner`, named after the PV, namespace and claim.",
    "Clean up. Deleting the namespace deletes the claim, and the `Delete` reclaim policy then removes the PV and its folder. With `Retain`, the PV and data would stay for you to recover.",
]

NEW["task"] = (
    [
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
    [
        "`kubectl get svc -n envoy-gateway-system -l gateway.envoyproxy.io/owning-gateway-name=hello-gateway -o name` prints the Service in a form `kubectl port-forward` accepts.",
        "To count answers: `for i in $(seq 1 50); do curl -s localhost:8888 | jq -r .message; done | sort | uniq -c`. Expect roughly 45 and 5, never exact numbers.",
        "Route not working? `kubectl describe httproute hello-devops -n hello` shows Accepted and ResolvedRefs. A ResolvedRefs of False usually means a Service name or port is wrong.",
    ],
    "`curl localhost:8888` answers through the Gateway, and 50 requests show mostly the main greeting with a few from the canary.",
)

NEW["explain_back"] = (
    "Explain in 3 to 4 sentences how one `curl localhost:8888` request can end up at the canary Pod. Mention the Gateway, the HTTPRoute, the weights and the Service.",
    "Port-forward sends the request to the Envoy proxy that Envoy Gateway started for `hello-gateway`. Envoy checks the HTTPRoutes attached to that Gateway; my request has no `x-canary` header, so the 90/10 rule matches. Envoy picks a backend by weight, so about one request in ten goes to the `hello-canary` Service. Envoy forwards it to one of that Service's ready Pods, which answers with the canary greeting.",
)

NEW["recap"] = [
    "Services give an address; web routing by host, path and header needs Ingress or the Gateway API.",
    "The Ingress API is frozen, and ingress-nginx was retired on March 24, 2026 with no more security fixes.",
    "Gateway API roles: GatewayClass (controller), Gateway (listeners, TLS), HTTPRoute (app rules and weights).",
    "On kind, Envoy Gateway routes for real; PROGRAMMED stays False without a load balancer, so use port-forward.",
    "A PVC asks for storage, a StorageClass creates the PV, and `reclaimPolicy` decides what happens to the data.",
    "The limit: StatefulSets give each replica a fixed name and its own PVC, but backups and failover stay your job.",
]

NEW["closing"] = """We started in a food hall with one street door and a chalkboard that kept getting wiped. The Gateway is the door with a host who reads each kitchen's rules, sends one table in ten to the canary and checks bookings with TLS. A PVC is the locker that keeps the tally when the Pod changes. When a route misbehaves in the task, read `kubectl describe httproute` before you touch the Gateway. Our `k8s` folder has grown to many files, though, and a second environment would mean copying all of them. Next, we'll package it. How do you run the same app in dev and prod without two copies of every file?"""

NEW["check"] = [
    ("A shop needs `/api` sent to Service `api` and every other path to Service `web`, through one Gateway. What do you write?",
     "Routing rules live in an HTTPRoute; the `/api` prefix rule is more specific, so it wins for those requests and `/` takes the rest."),
    ("On kind, `kubectl get gateway` shows PROGRAMMED False, \"No addresses have been assigned\", but curl through the port-forward works. What should you fix?",
     "Programmed is False only because the proxy's LoadBalancer Service never got an address; routing works, as the curl shows."),
    ("A Postgres Pod on kind keeps its data on a PVC from the `standard` class. You delete the whole namespace. What happens to the data?",
     "Deleting the namespace deletes the PVC, and with `reclaimPolicy: Delete` the PV and its folder go too."),
]

NEW["interview"] = [
    ("Why is the Gateway API replacing Ingress?",
     "Ingress covered only hosts, paths and TLS, so every controller added its own annotations, and configs did not move between controllers. The Gateway API makes features such as header matching, weights and timeouts real fields that behave the same everywhere. It also splits ownership: the platform team runs GatewayClasses and Gateways, and app teams write Routes. And the Ingress API is frozen and ingress-nginx was retired in March 2026, so new clusters should start with Gateway API."),
    ("Explain PV, PVC and StorageClass, and how dynamic provisioning works.",
     "A PVC is an app's request for storage, a PV is the actual storage, and a StorageClass describes a kind of storage and the provisioner that creates it. With dynamic provisioning, the app only writes a PVC; the class's provisioner creates a matching PV and the two are bound. The binding mode decides when that happens, often only once a Pod is scheduled, and the reclaim policy decides whether the data is deleted or kept with the claim. Access modes such as ReadWriteOnce limit how many nodes can mount it at once."),
    ("Would you run your database in Kubernetes?",
     "It depends on the team and the data. A StatefulSet gives fixed names and one volume per replica, and operators such as CloudNativePG automate failover and backups. But the team then owns backups, restores, upgrades and capacity, and has to test them. For business-critical data and a small team, I would start with a managed database and keep the cluster for stateless services and caches. I would move a database in only for a clear reason, such as cost at scale or a platform team that already runs operators well."),
]

NEW["deeper"] = """
The lab's Redis forgets the visit count every time its Pod restarts. A StatefulSet with a volume fixes that. Treat these steps as a sketch to try in a copy of `k8s/redis.yaml`, not as a change to the base:
1. Change `kind: Deployment` to `kind: StatefulSet`, and add `serviceName: redis` under `spec`.
2. Add a `volumeClaimTemplates` section with one template named `data`: access mode `ReadWriteOnce` and a request of `1Gi`. The StatefulSet makes one PVC per Pod, called `data-redis-0`.
3. Mount the `data` volume at `/data` in the Redis container. The official Redis image keeps its files there.
4. Turn on saving: run Redis with `redis-server --appendonly yes`, so each write also goes to disk.
5. Apply it, count a few visits, then delete the Pod `redis-0`. It comes back with the same name and the same PVC, and the count carries on.

Check the pieces with `kubectl get pvc -n hello` and `kubectl get pv`. On kind the PV is a folder inside a node container, so deleting the cluster deletes the data. For practice that is fine.

Four things to expect once it runs:
- Deleting a StatefulSet leaves its PVCs behind. You delete them yourself when you are sure.
- A local-path volume lives on one node, so `redis-0` can only ever be scheduled there. If that node goes away, the Pod stays `Pending`. A cloud disk can attach to another node; a local folder cannot.
- A StatefulSet wants a headless Service (`clusterIP: None`) so each Pod gets its own DNS name. Your existing `redis` Service is a normal one; for one replica that still works.
- Scaling down does not delete the PVCs of removed Pods, so scaling back up finds the old data.

Kubernetes 1.37 also changed two StatefulSet details you may read about. The `maxUnavailable` setting for rolling updates is on by default again. A new `Recreate` update strategy exists as an alpha feature.

One version detail from the Envoy Gateway section: Envoy Gateway 1.9 bundles Gateway API 1.6, not the newest 1.7. That is fine, because the lab uses only Standard features. Envoy itself is a CNCF project.

On the traffic side, cloud-provider-kind can give the Gateway a real address on your laptop. It runs on your Mac, watches the cluster, and exposes each LoadBalancer Service through a port on localhost. With it running, `kubectl get gateway` shows an address and PROGRAMMED True, which matches what you will see on a cloud. Read its README before you install it, because it needs permission to open ports on your machine.
"""
