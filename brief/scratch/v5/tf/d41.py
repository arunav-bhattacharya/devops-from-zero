NEW = {}

NEW["goal"] = "By the end you can explain how a request reaches a Pod in Kubernetes, put a Service in front of hello-devops, find it by its DNS name, and lock a namespace down with NetworkPolicies."

NEW["opening"] = """Picture a friend who loves the restaurant and asks for one waiter's direct phone number. It works on Monday. On Wednesday the waiter changes shift, and on Friday they move to another branch. Your friend calls the number and a stranger answers, or nobody does. The restaurant's own number would have worked every time, because it always reaches whoever is on the floor.

Last time, a Deployment changed shifts one waiter at a time, and every new Pod came with a new address. That is the trap. An address you copied from `kubectl get pods` works today, so it feels safe to put it in a settings file.

In this lesson, we'll give our Pods one number that never changes. We'll follow a request from your Mac to a Pod, find the app by name, and then put a guest list on the doors. Before we start, make a guess, and keep it in mind."""

NEW["guess"] = (
    "Two Pods run in different namespaces (named groups of objects), `shop` and `billing`, and there are no NetworkPolicies. Can the Pod in `shop` open a connection to the Pod in `billing`?",
    "The Kubernetes network is flat: every Pod gets its own IP address and can reach every other Pod. Namespaces only group names; a NetworkPolicy is what blocks traffic.",
)

NEW["terms"] = [
    "The network add-on that gives every Pod an IP address and connects Pods across nodes.",
    "An object that gives a changing group of Pods one fixed IP address and one DNS name.",
    "A Service's made-up IP address, which only programs inside the cluster can reach.",
    "A Service type that also opens the same port, from 30000 to 32767, on every node.",
    "An object that lists the IP addresses and ports of the Pods behind a Service, and which of them are ready.",
    "The program on each node that turns Services into traffic rules inside Linux.",
    "The cluster's name service, which turns Service names into IP addresses.",
    "A set of rules that says which traffic may reach, or leave, the Pods it picks.",
]

S = []

S.append(("Every waiter has a direct line: Pod IP addresses", """
Start with how Pods talk at all. Each Pod gets its own IP address, the number that names it on a network, much like a street address. On Day 20, Docker networks connected containers on one machine through a private network, and you published ports to reach them. A port is a numbered door on a machine where a program waits. Kubernetes runs Pods on many machines, so its network is bigger, and simpler to use. The rules:
- Every Pod gets its own IP address. The containers in a Pod share it.
- Every Pod can reach every other Pod by that address, on any node, with no address translation (NAT) in between.
- Programs on a node, such as the kubelet, can reach every Pod on that node.

That ends Docker's port juggling. Two Pods on one node can both listen on 8000, because each has its own address. Nothing needs publishing to the machine.

Kubernetes itself does not build this network. A network plugin does, through a standard called CNI. The plugin hands out Pod addresses and sets up routes, the paths packets take between nodes. kind uses a small plugin called kindnet. Clouds have plugins that give Pods real addresses in your VPC (your private network in the cloud). Calico and Cilium are popular choices elsewhere.

On kind, the Pod range is 10.244.0.0/16, which means every address that starts with 10.244. Each node gets its own slice of it. `kubectl get nodes -o jsonpath='{.items[*].spec.podCIDR}'` prints the slices, for example `10.244.0.0/24 10.244.1.0/24 10.244.2.0/24`. Pods on `devops-worker` might get 10.244.1.x, and Pods on `devops-worker2` 10.244.2.x. Look at `kubectl get pods -o wide`, and you can often tell the node from the address.

But Pod addresses do not last. Every new Pod gets a new one, and rollouts, scaling and failures replace Pods all the time. A Pod address in a settings file is the waiter's direct number from the opening. Next, we get the restaurant's own number.
"""))

S.append(("One number for the whole floor: Services", """
Guests at a busy restaurant never hunt for one waiter. They go to the host stand at the door, and the host sends them to a waiter who is on duty and free. A **Service** is that host stand. It gives a changing group of Pods one fixed virtual IP address and one DNS name. DNS is the system that turns a name into an address. A Service finds its Pods with a label selector, a question about labels, just like a Deployment.

The lab's `service.yaml` says, in plain words: take every ready Pod labeled `app: hello-devops`, and give them the name `hello-devops` and port 80. Three pieces work together behind it:
1. The Service holds the selector and the ports. The API server gives it a virtual IP from the Service range, 10.96.0.0/16 on kind. That address is its ClusterIP.
2. The EndpointSlice controller watches Pods. An EndpointSlice lists the addresses and ports of the matching Pods, and marks each one ready or not. Whenever a Pod comes, goes or changes readiness, the controller updates the list. It is the host's clipboard.
3. kube-proxy, on every node, watches both and rewrites traffic rules inside Linux, the operating system on each node, to match.

The virtual IP lives on no network card, so `ping`, the command that checks if an address answers, gets no reply. It exists only as rules that say: traffic for 10.96.171.215 port 80 goes to one of these Pod addresses on port 8000.

Only ready Pods get visitors. A Pod that fails its readiness check keeps running, but its endpoint is marked not ready and the rules skip it (Day 43). If the selector matches no Pods, the Service exists but leads nowhere. A typo in a label is enough. Run `kubectl get endpointslices -l kubernetes.io/service-name=hello-devops` to see which case you are in.

No addresses there means a selector or readiness problem. Addresses that refuse connections mean a port problem. Either way, it is rarely the network itself.

**When a Service fails, read its EndpointSlice before you blame the network.**

That port problem deserves its own section, because one Service has three port numbers.
"""))

S.append(("Three ports on one ticket: port, targetPort and nodePort", """
A NodePort Service has three port numbers, and mixing them up is one of the most common Service bugs. From the outside in, the lab's Service has:
- `nodePort: 30080`: the port opened on every node. NodePorts come from the range 30000 to 32767.
- `port: 80`: the Service's own port on its ClusterIP. Other Pods call `http://hello-devops`, which means port 80.
- `targetPort: 8000`: the port on the Pod where the app listens. Leave it out and it equals `port`.

There is also `containerPort` in the Deployment. It mostly documents the port, and it lets you give it a name. The lab names it `http`, so a Service could say `targetPort: http` and keep working if the number ever changed.

Now follow one `curl localhost:8081` from your Mac to a Pod. (`curl` fetches a web address and prints the answer.)
1. Docker Desktop forwards localhost:8081 into the control-plane node container, on port 30080. That is the `extraPortMappings` entry in `kind-config.yaml`.
2. kube-proxy's rules on that node catch port 30080 and pick one ready endpoint of the Service.
3. The packet goes to that Pod's address on port 8000, possibly on another node.
4. gunicorn, the web server program that runs hello-devops in its container, answers. The reply travels back the same way.

So one mapped port on one node reaches Pods on every node. That is why kind needs only a single port mapping. Not every Service should be open to your Mac, though, and that choice has a field of its own.
"""))

S.append(("Who may call: Service types", """
A restaurant has an internal phone line between kitchen and bar, and a public number for guests. The `type` field makes the same choice for a Service:
- `ClusterIP` (the default): a virtual IP reachable only inside the cluster. Right for most services, such as Redis, the small database in the lab.
- `NodePort`: a ClusterIP, plus the same port opened on every node. Fine for labs and simple setups.
- `LoadBalancer`: a NodePort, plus a request to the cloud controller manager (Day 38) for an outside load balancer with its own address. A load balancer spreads incoming visitors over several machines.
- `ExternalName`: no traffic handling at all, only a DNS alias (a second name) for an outside name, such as a database a cloud runs for you.

A headless Service sets `clusterIP: None`. It gets no virtual IP and no kube-proxy rules. Its DNS name returns the Pod addresses themselves, one record per ready Pod. Clients that must talk to each member use it, such as copies of a database that each hold data. StatefulSets, which give each Pod a fixed name, need one (Day 44).

On a laptop, LoadBalancer is awkward. kind has no cloud, so `EXTERNAL-IP` shows `<pending>` forever. The kind project's add-on cloud-provider-kind fills that gap, with some extra steps on a Mac that Go deeper describes. For one app on your laptop, the NodePort or `kubectl port-forward` is simpler.

For web traffic from users, teams rarely give every app its own load balancer. They put one Gateway, a shared front entrance, in front of many ClusterIP Services (Day 44). Picture a payments company: every app gets a ClusterIP Service, and only the Gateway is open to the outside world.

We keep saying "kube-proxy's rules". Next, we look at what those rules are.
"""))

S.append(("The rules at every door: how kube-proxy works", """
kube-proxy runs on every node as a DaemonSet, an object that runs one Pod per node. It does not carry any traffic itself. It is more like a sign painter than a host: it watches Services and EndpointSlices and writes rules into the Linux kernel, the core of the operating system. The kernel then sends each new connection to one Pod. kube-proxy can work in three modes, named after the kernel feature it writes to:
- `iptables`: Linux's classic rules for filtering packets. The long-time default, and still kind's default.
- `nftables`: the newer kernel firewall that replaces iptables, stable since Kubernetes 1.33 and the recommended mode on new Linux nodes.
- `ipvs`: the kernel's built-in load balancer, now deprecated (on its way out). Do not build new clusters on it; Go deeper has the dates.

Some network plugins, such as Cilium, replace kube-proxy and do the same job with eBPF: small programs loaded into the kernel (Day 60).

Three things about this matter in practice. First, balancing happens per connection, not per request. The kernel picks a Pod on a connection's first packet and remembers it until the connection closes. A client that reuses one connection for many requests can talk to one Pod for a long time. HTTP keep-alive, which keeps one web connection open for many requests, does that. gRPC, a framework for calls between services over HTTP/2, does it by design. A `curl` loop opens a new connection each time, so it spreads.

Second, if one client must keep talking to the same Pod, set `sessionAffinity: ClientIP` on the Service. kube-proxy then pins each client address to one Pod for a while.

Third, `kubectl port-forward svc/hello-devops` skips all of it. kubectl picks one Pod and tunnels to it through the API server. Good for debugging, useless for testing balance.

On kind you can see the mode in the kube-proxy ConfigMap, an object of settings: `kubectl -n kube-system get configmap kube-proxy -o yaml | grep mode`. The rules handle addresses. Names come from somewhere else, and that is next.
"""))

S.append(("The phone book: CoreDNS and Service names", """
Inside the cluster, Pods find Services by name, the way you look up a restaurant in a phone book. CoreDNS is that phone book. It runs as a Deployment in `kube-system`, behind a Service that is still called `kube-dns` for historical reasons. Its ClusterIP is 10.96.0.10 on kind. The kubelet writes that address into every Pod's `/etc/resolv.conf`, the file that tells a program where to look up names.

Every Service gets a DNS name of this form: `<service>.<namespace>.svc.cluster.local`. The lab's Service is `hello-devops.hello.svc.cluster.local`. You rarely type all of it, because each Pod's resolv.conf has a search list: endings the lookup tries, in order, after a short name. For a Pod in namespace `hello` the list is `hello.svc.cluster.local svc.cluster.local cluster.local`. So:
- From the same namespace, the short name works: `http://hello-devops`. That is how the app finds Redis tomorrow, with `REDIS_HOST=redis`.
- From another namespace, add the namespace: `http://hello-devops.hello`.
- The full name works from anywhere in the cluster.

A normal Service name resolves to its one ClusterIP. A headless Service name resolves to every ready Pod address behind it, which the worked example shows. With a StatefulSet, each Pod also gets its own fixed name, such as `db-0.db.hello.svc.cluster.local` (Day 44).

`cluster.local` is only a default, and a cluster admin can change it. So in app settings, prefer the short name or `name.namespace`. Then the same settings work in the development, testing and production clusters.

Every Pod can now find every other Pod, by number or by name. That is handy, and it is also a risk. Next, we put a guest list on the doors.
"""))

S.append(("The guest list: NetworkPolicies", """
By default every Pod accepts traffic from anywhere in the cluster, and namespaces do not change that. That is the answer to the guess. So an attacker who breaks into any one Pod can talk straight to Redis or a database. A NetworkPolicy is a guest list for the Pods it selects. The object does nothing by itself: the network plugin watches policies and turns them into packet filters on each node. The rules are short, and the second one is the one people miss:
- A Pod that no policy selects allows all traffic.
- Once any policy selects a Pod for `Ingress` (incoming traffic), that Pod accepts only what some policy allows. `Egress` (outgoing traffic) works the same way.
- Policies only add permissions. There is no deny rule. You get "deny" by selecting Pods and allowing nothing.
- Rules match sources by Pod labels, namespace labels or address ranges, plus ports. Every namespace carries the label `kubernetes.io/metadata.name` with its own name, so a rule can allow, say, the whole `monitoring` namespace.

The usual pattern has two steps. First, one deny-all policy: `podSelector: {}` selects every Pod in the namespace, with `policyTypes: [Ingress]` and no rules. Then small allow policies, one per real need. The lab's examples let anyone reach the app on port 8000 and let only the app reach Redis on 6379. Auditors, the people who check a company's safety rules, like exactly this kind of proof: the database accepts connections only from Pods with one label.

The port in a policy is the Pod's port (8000), not the Service's (80). Policies check traffic after the Service has picked a Pod.

Not every network plugin enforces policies. Some accept the objects and silently ignore them. The kindnet plugin that kind installs does enforce them, so you can test the real thing on your laptop. Traffic from a Pod's own node is always allowed, which keeps health checks working. If you ever restrict egress, allow DNS (port 53) to CoreDNS, or every name lookup fails. The worked example now looks at all of this from inside the cluster.
"""))

NEW["sections"] = S

NEW["drop"] = ["analogy", "real_world", "mistake"]

NEW["diagram_caption"] = "curl on your Mac reaches node port 30080 through kind's port mapping. kube-proxy's rules send it to one ready Pod from the Service's EndpointSlice."

NEW["worked"] = [
    "With the lab Service applied, list the Service and its EndpointSlice together. The Service has a ClusterIP and maps port 80 to node port 30080. The slice lists the three Pod addresses on port 8000.",
    "Look at DNS from inside an app Pod. Its resolv.conf points at CoreDNS and lists the search endings. The app image has Python, so Python can look up the short name, which comes back as the full name and the ClusterIP.",
    "Add the headless Service from the examples folder and look up its name the same way. There is no virtual IP, so DNS returns one address per ready Pod.",
    "Scale the Deployment to 5 and read the EndpointSlice again. The controller added the two new Pods as soon as they were ready. kubectl shows the first three addresses and counts the rest.",
    "Call the Service from a throwaway Pod in another namespace. The short name fails there, because the search list starts with `default`. Adding the namespace works. `--rm` deletes the Pod when you leave its shell.",
    "Tidy up: scale back to 3 and remove the headless Service. The `visits` number above counts only calls to that one Pod; tomorrow Redis makes the counter shared.",
]

NEW["task"] = (
    [
        "Write `k8s/service.yaml` (NodePort 30080), add it to `k8s/kustomization.yaml`, and apply with `kubectl apply -k k8s`.",
        "Call `curl localhost:8081` six times in a loop. Watch `host` change between Pods. Why do the `visits` numbers jump around?",
        "Break the Service on purpose: change its selector to `app: hello-devop` and apply. What does curl do now, and what do the EndpointSlices show? Fix it and apply again.",
        "Start a test web server in the namespace with `kubectl run whoami -n hello --image=nginx:1.28 --port=80 --expose`. From a throwaway busybox Pod, fetch both `http://whoami` and `http://hello-devops`.",
        "Apply `k8s/examples/netpol-deny-all.yaml`. Try `curl -m 3 localhost:8081` from your Mac and `wget -T 3 http://whoami` from a busybox Pod. What happened to each, and why does the deny-all block your Mac too?",
        "Apply `k8s/examples/netpol-allow.yaml`. Which of the two calls works again, and which stays blocked?",
        "Read the policies in plain words with `kubectl describe networkpolicy -n hello`.",
        "Clean up: delete the `whoami` Pod and Service and both policy files, so later days start with an open namespace. Commit `service.yaml` and the kustomization.",
    ],
    [
        "In zsh: `for i in {1..6}; do curl -s localhost:8081; done` (the app ends each answer with a new line).",
        "A wrong selector gives an EndpointSlice with no endpoints. The Service object itself still looks fine in `kubectl get svc`.",
        "Policies can take a few seconds to take effect. If nothing changes at all, check that the policy's namespace is `hello`.",
    ],
    "With both policies applied, `curl localhost:8081` answers while `wget -T 3 http://whoami` from a busybox Pod times out; after cleanup, `kubectl get networkpolicy -n hello` shows nothing.",
)

NEW["explain_back"] = (
    "Explain in 3 to 4 sentences how a request from `curl localhost:8081` on your Mac reaches a hello-devops Pod. Mention the port mapping, the NodePort, kube-proxy and the EndpointSlice.",
    "The port mapping in kind-config.yaml forwards localhost:8081 on the Mac to port 30080 on the control-plane node container. On every node, kube-proxy has written kernel rules that catch traffic on the NodePort and on the Service's ClusterIP. Those rules pick one ready Pod from the Service's EndpointSlice. The packet goes to that Pod's address on port 8000, even if the Pod runs on another node, and the reply comes back the same way.",
)

NEW["recap"] = [
    "Every Pod gets its own IP address from the CNI plugin, and by default every Pod can reach every other Pod.",
    "A Service selects Pods by label and gives them a fixed ClusterIP and DNS name; EndpointSlices list the ready Pods.",
    "nodePort is on every node, port is on the Service, targetPort is on the Pod.",
    "A limit to remember: kube-proxy balances per connection, not per request, so long connections stick to one Pod.",
    "DNS names follow `<service>.<namespace>.svc.cluster.local`; short names work inside the same namespace.",
    "A NetworkPolicy that selects a Pod blocks everything it does not allow; kind's kindnet enforces them.",
]

NEW["closing"] = """We started with a waiter's direct number that stopped working by Friday. A Service is the restaurant's own number: one name and one address, with a clipboard of whoever is ready right now. When a Service seems broken in the task, read its EndpointSlice first; an empty list almost always means a label that does not match. Our app still counts visits inside each Pod, though, which is why the numbers jumped around. Next, we'll give it Redis and its settings from outside the image. How do you change an app's settings, and keep a password safe, without building a new image?"""

NEW["check"] = [
    ("A Service for `api` exists, but calls to it fail. `kubectl get endpointslices -l kubernetes.io/service-name=api` shows no endpoints, while the Pods are Running. What is the most likely cause?",
     "Endpoints come from Pods that match the selector and are ready; Running Pods with no endpoints point to a label mismatch (or failing readiness)."),
    ("A Pod in namespace `web` must call the Service `orders` in namespace `shop` on port 8080. Which address works?",
     "From another namespace you need at least `<service>.<namespace>`, here `orders.shop`; the short name works only inside `shop`."),
    ("You apply a deny-all ingress policy and an allow rule for Pods labeled `app: api` on port 8080. Next week a teammate deploys a new `worker` Pod into the same namespace. Who can connect to the worker?",
     "`podSelector: {}` matches every Pod in the namespace at any time, and nothing allows traffic to the worker."),
]

NEW["interview"] = [
    ("What Service types does Kubernetes have, and when do you use each?",
     "ClusterIP is the default and is reachable only inside the cluster; most internal services use it. NodePort opens the same port on every node, which suits labs and simple setups. LoadBalancer asks a cloud controller for an outside load balancer, the usual way to expose one TCP service in a cloud. ExternalName is only a DNS alias, and a headless Service (`clusterIP: None`) returns Pod IPs directly, which StatefulSets need. For web traffic to many apps, teams put a Gateway in front of ClusterIP Services."),
    ("How does a Service actually route traffic to Pods?",
     "The EndpointSlice controller watches the Pods matching the Service's selector and records their IPs, ports and readiness in EndpointSlices. On every node, kube-proxy watches Services and EndpointSlices. It writes kernel rules (iptables or nftables) that send traffic for the ClusterIP or NodePort to one ready Pod. The choice is made per connection, so long-lived connections stick to one Pod. Some CNI plugins, such as Cilium, replace kube-proxy with eBPF."),
    ("How do NetworkPolicies work, and what is a common pitfall?",
     "A NetworkPolicy selects Pods and lists allowed ingress or egress traffic by Pod labels, namespace labels, IP blocks and ports. Pods that no policy selects allow everything; once selected for a direction, only allowed traffic passes, and policies only add permissions. A common pitfall is a default-deny egress policy that forgets DNS, so every lookup fails. Another is a CNI plugin that does not enforce policies at all, so the YAML is accepted but has no effect."),
]

NEW["deeper"] = """
Look again at the resolv.conf from the worked example. The last line says `options ndots:5`. It changes how every name lookup in the Pod works.

ndots means: if a name has fewer than 5 dots, try the search list first. So when the app looks up `api.github.com` (two dots), it first asks for:
1. `api.github.com.hello.svc.cluster.local`
2. `api.github.com.svc.cluster.local`
3. `api.github.com.cluster.local`
4. Then, finally, `api.github.com` itself.

Each try is a round trip to CoreDNS, often twice (for IPv4 and IPv6 addresses). For an app that calls outside services all the time, this adds load and a little delay. Two common fixes:
- Write outside names with a trailing dot, `api.github.com.`, which means the name is complete.
- Lower `ndots` for that Pod with `spec.dnsConfig.options`.

Kubernetes sets 5 so that names like `orders.shop.svc` still go through the search list. Most apps never need to touch it, but remember it the day someone says DNS in the cluster is slow.

Where does the client's address go? With a NodePort and the default `externalTrafficPolicy: Cluster`, a request can arrive on one node and be sent to a Pod on another. To make the reply come back the same way, kube-proxy replaces the source address with the node's address. Your app then logs a node address, not the real client's. Setting `externalTrafficPolicy: Local` keeps the client address. The cost is that traffic only goes to Pods on the node that received it, and nodes without such a Pod drop it. Cloud load balancers handle this with health checks.

Two dates for kube-proxy's modes: `ipvs` (IP Virtual Server) has been deprecated since 1.35. The plan is to switch it off by default around 1.40 and remove it around 1.43.

LoadBalancer on a Mac: the address cloud-provider-kind hands out (172.18.x.x) lives inside Docker Desktop's VM, and your Mac cannot reach it. The tool works around this with a proxy container named `kindccm-...` that publishes a port on localhost. It must run with `sudo`.

The old `Endpoints` object still exists but has been deprecated since 1.33 in favor of EndpointSlices. A slice holds at most 100 endpoints by default, so a Service with 250 Pods has three slices. `kubectl get endpoints` still works and prints a deprecation warning. Services can also be dual-stack, with both IPv4 and IPv6 addresses, and kind can create such clusters from its config file.

To see the whole picture with diagrams, read [Virtual IPs and Service proxies](https://kubernetes.io/docs/reference/networking/virtual-ips/) in the Kubernetes docs.
"""
