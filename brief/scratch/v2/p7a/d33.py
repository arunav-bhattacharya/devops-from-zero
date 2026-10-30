"""Day 33: Services and cluster networking."""
from svg import box, arrow, cap, svg

DIAGRAM = svg(236, "A request from the Mac goes through the kind port mapping and the NodePort to the Service, then to one ready Pod", [
    box(8, 92, 112, 44, "bx", "curl :8081"),
    box(152, 92, 120, 44, "bxo", "node :30080"),
    box(304, 92, 116, 44, "bxg", "Service :80"),
    box(448, 36, 104, 44, "bxt", "Pod :8000"),
    box(448, 148, 104, 44, "bxt", "Pod :8000"),
    arrow(120, 114, 150, 114),
    arrow(272, 114, 302, 114),
    arrow(420, 106, 446, 62),
    arrow(420, 122, 446, 166),
    cap(64, 160, "your Mac"),
    cap(212, 160, "port mapping"),
    cap(212, 174, "in kind-config"),
    cap(362, 160, "kube-proxy rules"),
    cap(362, 174, "pick a ready Pod"),
    cap(430, 216, "chosen from the EndpointSlice"),
])

SERVICE = open("/home/user/devops-from-zero/labs/hello-devops/k8s/service.yaml").read().rstrip("\n")

KUSTOMIZATION_V2 = """# The list of files that make up the app. Apply them all with: kubectl apply -k k8s
# Day 33 version: adds the Service.
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization
resources:
  - namespace.yaml
  - deployment.yaml
  - service.yaml"""


def ex(name):
    return open(f"/home/user/devops-from-zero/labs/hello-devops/k8s/examples/{name}").read().rstrip("\n")


L = {
    "id": "d33",
    "title": "Services and cluster networking",
    "minutes": 50,
    "goal": "By the end you can explain how a request reaches a Pod in Kubernetes, put a Service in front of hello-devops, find it by its DNS name, and lock a namespace down with NetworkPolicies.",
    "guess": {
        "q": "Two Pods run in different namespaces, `shop` and `billing`, and there are no NetworkPolicies. Can the Pod in `shop` open a connection to the Pod in `billing`?",
        "options": [
            "No, because a namespace is a network boundary",
            "Only through a Service of type NodePort",
            "Only if both namespaces carry the same label",
            "Yes, by default every Pod can reach every Pod",
        ],
        "answer": 3,
        "why": "The Kubernetes network is flat: every Pod gets its own IP and can reach every other Pod. Namespaces only group names; a NetworkPolicy is what blocks traffic.",
    },
    "terms": [
        {"term": "CNI plugin", "plain": "The network plugin that gives every Pod an IP address and connects Pods across nodes."},
        {"term": "Service", "plain": "An object that gives a changing set of Pods one stable IP address and DNS name."},
        {"term": "ClusterIP", "plain": "A Service's virtual IP address, reachable only from inside the cluster."},
        {"term": "NodePort", "plain": "A Service type that also opens the same port, from 30000 to 32767, on every node."},
        {"term": "EndpointSlice", "plain": "An object that lists the IP addresses and ports of the Pods behind a Service, and which are ready."},
        {"term": "kube-proxy", "plain": "The program on each node that turns Services into packet rules in the Linux kernel."},
        {"term": "CoreDNS", "plain": "The cluster's DNS server, which turns Service names into IP addresses."},
        {"term": "NetworkPolicy", "plain": "A set of firewall rules that says which traffic may reach, or leave, the Pods it selects."},
    ],
    "sections": [
        {
            "h": "Every Pod gets its own IP address",
            "body": """On Day 14 you met Docker networks: containers on one machine, on a private network, with ports published to the host. Kubernetes runs Pods on many machines, so its network model is bigger, and simpler to use. The rules:
- Every Pod gets its own IP address. The containers in a Pod share it.
- Every Pod can reach every other Pod by that address, on any node, with no address translation (NAT) in between.
- Programs on a node, such as the kubelet, can reach every Pod on that node.

Kubernetes itself does not build this network. A network plugin does, through a standard called CNI (Container Network Interface). The plugin hands out Pod IPs and sets up routes between nodes. kind uses a small plugin called kindnet. Clouds have plugins that give Pods real addresses in your VPC, and Calico and Cilium are popular choices elsewhere.

On kind, each node gets its own slice of the Pod range 10.244.0.0/16. `kubectl get nodes -o jsonpath='{.items[*].spec.podCIDR}'` prints them, for example `10.244.0.0/24 10.244.1.0/24 10.244.2.0/24`. Pods on `devops-worker` might get 10.244.1.x, and Pods on `devops-worker2` 10.244.2.x. Look at `kubectl get pods -o wide`, and you can often tell the node from the IP.

There is a catch. Pod IPs do not last. Every new Pod gets a new IP, and rollouts, scaling and failures replace Pods all the time. So never put a Pod IP in a config file. That is the problem Services solve.""",
            "refs": [
                {"title": "Services, load balancing and networking", "url": "https://kubernetes.io/docs/concepts/services-networking/", "kind": "docs"},
                {"title": "Cluster networking", "url": "https://kubernetes.io/docs/concepts/cluster-administration/networking/", "kind": "docs"},
                {"title": "Kubernetes networking explained (KodeKloud)", "url": "https://kodekloud.com/blog/kubernetes-networking-explained/", "kind": "read"},
            ],
        },
        {
            "h": "Services: one stable address for many Pods",
            "body": """A **Service** gives a changing set of Pods one stable virtual IP address and one DNS name. It finds its Pods with a label selector, just like a Deployment. The lab's `service.yaml` says, in plain words: take every ready Pod labeled `app: hello-devops`, and give them the name `hello-devops` and port 80.

Three pieces work together behind every Service:
1. The Service holds the selector and the ports. The API server gives it a virtual IP from the Service range, 10.96.0.0/16 on kind. That address is its ClusterIP.
2. A controller keeps EndpointSlices up to date. An EndpointSlice lists the IP addresses and ports of the matching Pods, and marks each one ready or not.
3. kube-proxy, on every node, reads both and writes packet rules into the node's Linux kernel.

The virtual IP lives on no network card, so `ping` gets no answer. It exists only as rules that say: traffic for 10.96.171.215 port 80 goes to one of these Pod IPs on port 8000.

Only ready Pods get traffic. A Pod that fails its readiness check keeps running, but its endpoint is marked not ready and the rules skip it (Day 35). If the selector matches no Pods, for example because of a typo in a label, the Service exists but leads nowhere. Run `kubectl get endpointslices -l kubernetes.io/service-name=hello-devops` to see which case you are in. It is the first thing to check when a Service \"does not work\".""",
            "refs": [
                {"title": "Service", "url": "https://kubernetes.io/docs/concepts/services-networking/service/", "kind": "docs"},
                {"title": "EndpointSlices", "url": "https://kubernetes.io/docs/concepts/services-networking/endpoint-slices/", "kind": "docs"},
                {"title": "Kubernetes Services explained (TechWorld with Nana)", "url": "https://www.youtube.com/watch?v=T4Z7visMM4E", "kind": "watch"},
            ],
        },
        {
            "h": "Three ports: port, targetPort and nodePort",
            "body": """A NodePort Service has three port numbers, and mixing them up is the most common Service bug. Here is the lab's Service, from the outside in:
- `nodePort: 30080`: the port opened on every node. NodePorts come from the range 30000 to 32767.
- `port: 80`: the Service's own port on its ClusterIP. Other Pods call `http://hello-devops`, which means port 80.
- `targetPort: 8000`: the port on the Pod where the app listens. Leave it out and it equals `port`.

There is also `containerPort` in the Deployment. It mostly documents the port, and it lets you name it. The lab names it `http`, so a Service could say `targetPort: http` and keep working if the number ever changed.

Now follow one `curl localhost:8081` from your Mac to a Pod:
1. Docker Desktop forwards localhost:8081 into the control-plane node container, on port 30080. That is the `extraPortMappings` entry in `kind-config.yaml`.
2. kube-proxy's rules on that node catch port 30080 and pick one ready endpoint of the Service.
3. The packet goes to that Pod's IP on port 8000, possibly on another node.
4. gunicorn answers, and the reply travels back the same way.

So one mapped port on one node reaches Pods on every node. That is why kind needs only a single port mapping.""",
            "refs": [
                {"title": "Service: port definitions", "url": "https://kubernetes.io/docs/concepts/services-networking/service/#field-spec-ports", "kind": "docs"},
                {"title": "kind configuration: extra port mappings", "url": "https://kind.sigs.k8s.io/docs/user/configuration/", "kind": "docs"},
            ],
        },
        {
            "h": "Service types: who can reach it",
            "body": """The `type` field decides who can reach a Service:
- `ClusterIP` (the default): a virtual IP reachable only inside the cluster. Right for most services, such as Redis in the lab.
- `NodePort`: a ClusterIP, plus the same port opened on every node. Fine for labs and simple setups.
- `LoadBalancer`: a NodePort, plus a request to a cloud controller for an external load balancer with its own address.
- `ExternalName`: no proxying at all, only a DNS alias for an outside name, such as a managed database.

A headless Service sets `clusterIP: None`. It gets no virtual IP and no kube-proxy rules. Its DNS name returns the Pod IPs themselves, one record per ready Pod. Clients that must talk to each member, such as database replicas, use it. StatefulSets need one (Day 36).

LoadBalancer on a laptop needs a note. kind has no cloud, so `EXTERNAL-IP` shows `<pending>` forever. The kind project's add-on cloud-provider-kind fills that gap. On a Mac, though, the address it hands out (172.18.x.x) lives inside Docker Desktop's VM, and your Mac cannot reach it. The tool works around this with a proxy container named `kindccm-...` that publishes a port on localhost. It must run with `sudo`. For one app on your laptop, the NodePort or `kubectl port-forward` is simpler.

For HTTP traffic from users, teams rarely give every app its own load balancer. They put one Gateway in front of many ClusterIP Services (Day 36).""",
            "refs": [
                {"title": "Service types", "url": "https://kubernetes.io/docs/concepts/services-networking/service/#publishing-services-service-types", "kind": "docs"},
                {"title": "kind LoadBalancer guide", "url": "https://kind.sigs.k8s.io/docs/user/loadbalancer/", "kind": "docs"},
                {"title": "cloud-provider-kind", "url": "https://github.com/kubernetes-sigs/cloud-provider-kind", "kind": "read"},
            ],
        },
        {
            "h": "How kube-proxy turns Services into packet rules",
            "body": """kube-proxy runs on every node as a DaemonSet, an object that runs one Pod per node. It does not carry traffic itself. It watches Services and EndpointSlices and programs the Linux kernel, which then sends each new connection to one Pod. It has a few modes:
- `iptables`: the long-time default, and still kind's default.
- `nftables`: the newer kernel firewall, stable since Kubernetes 1.33 and the recommended mode on new Linux nodes.
- `ipvs`: deprecated since 1.35. The plan is to switch it off by default around 1.40 and remove it around 1.43, so do not build new clusters on it.

Some network plugins, such as Cilium, replace kube-proxy and do the same job with eBPF programs in the kernel.

A few consequences matter in practice:
- Balancing happens per connection, not per request. A client that keeps a connection open (HTTP keep-alive, gRPC) can talk to one Pod for a long time. A `curl` loop opens a new connection each time, so it spreads.
- If one client must keep talking to the same Pod, set `sessionAffinity: ClientIP` on the Service. kube-proxy then pins each client IP to one Pod for a while.
- `kubectl port-forward svc/hello-devops` skips all of it. kubectl picks one Pod and tunnels to it through the API server. Good for debugging, useless for testing balance.

On kind you can see the mode in the kube-proxy ConfigMap with `kubectl -n kube-system get configmap kube-proxy -o yaml | grep mode`.""",
            "refs": [
                {"title": "Virtual IPs and service proxies", "url": "https://kubernetes.io/docs/reference/networking/virtual-ips/", "kind": "docs"},
            ],
        },
        {
            "h": "CoreDNS and Service names",
            "body": """Inside the cluster, Pods find Services by name. CoreDNS runs as a Deployment in `kube-system`, behind a Service that is still called `kube-dns` for historical reasons. Its ClusterIP is 10.96.0.10 on kind. The kubelet writes that address into every Pod's `/etc/resolv.conf`.

Every Service gets a DNS name of this form: `<service>.<namespace>.svc.cluster.local`. The lab's Service is `hello-devops.hello.svc.cluster.local`. You rarely type all of it, because each Pod's resolv.conf has a search list. For a Pod in namespace `hello` the list is `hello.svc.cluster.local svc.cluster.local cluster.local`. So:
- From the same namespace, the short name works: `http://hello-devops`. That is how the app finds Redis tomorrow, with `REDIS_HOST=redis`.
- From another namespace, add the namespace: `http://hello-devops.hello`.
- The full name works from anywhere in the cluster.

A normal Service name resolves to its one ClusterIP. A headless Service name resolves to every ready Pod IP behind it, which the worked example shows. With a StatefulSet, each Pod also gets its own stable name, such as `db-0.db.hello.svc.cluster.local` (Day 36).

`cluster.local` is only a default, and a cluster admin can change it. So in app config, prefer the short name or `name.namespace`.""",
            "refs": [
                {"title": "DNS for Services and Pods", "url": "https://kubernetes.io/docs/concepts/services-networking/dns-pod-service/", "kind": "docs"},
            ],
        },
        {
            "h": "NetworkPolicies: firewall rules for Pods",
            "body": """By default every Pod accepts traffic from anywhere in the cluster, and namespaces do not change that. A NetworkPolicy is a set of firewall rules for the Pods it selects. Here is how the rules work. The second one is the one people miss:
- A Pod that no policy selects allows all traffic.
- Once any policy selects a Pod for `Ingress` (incoming traffic), that Pod accepts only what some policy allows. `Egress` (outgoing traffic) works the same way.
- Policies only add permissions. There is no deny rule. You get \"deny\" by selecting Pods and allowing nothing.
- Rules match sources by Pod labels, namespace labels or IP ranges, plus ports. Every namespace carries the label `kubernetes.io/metadata.name` with its own name, so a rule can allow, say, the whole `monitoring` namespace.

The usual pattern has two steps. First, one deny-all policy: `podSelector: {}` selects every Pod in the namespace, with `policyTypes: [Ingress]` and no rules. Then small allow policies, one per real need. The lab's examples let anyone reach the app on port 8000 and let only the app reach Redis on 6379.

The port in a policy is the Pod's port (8000), not the Service's (80). Policies check traffic after the Service has picked a Pod.

Policies need a network plugin that enforces them. Some plugins accept the objects and silently ignore them. The kindnet plugin that kind installs does enforce them, so you can test the real thing on your laptop. Traffic from a Pod's own node is always allowed, which keeps probes working. If you ever restrict egress, allow DNS (port 53) to CoreDNS, or every name lookup fails.""",
            "refs": [
                {"title": "Network policies", "url": "https://kubernetes.io/docs/concepts/services-networking/network-policies/", "kind": "docs"},
                {"title": "Kubernetes Services explained: ClusterIP, NodePort, LoadBalancer (video)", "url": "https://www.youtube.com/watch?v=BYZgA2BBt4s", "kind": "watch"},
            ],
        },
    ],
    "analogy": "A Service is like a company's main phone number. Callers dial one number and get whichever agent is free. Agents can join, leave or change desks, and nobody updates a phone book. CoreDNS is the phone book that maps the company name to that one number. A NetworkPolicy is the receptionist's list of who may be put through. The picture breaks on fairness. A phone system can route each call to the least busy agent, while kube-proxy picks a Pod per connection and does not know how busy each Pod is.",
    "diagram": DIAGRAM,
    "diagram_caption": "curl on your Mac reaches node port 30080 through kind's port mapping. kube-proxy's rules send it to one ready Pod from the Service's EndpointSlice.",
    "worked": {
        "title": "Look at a Service from inside the cluster",
        "steps": [
            {
                "say": "With the lab Service applied, list the Service and its EndpointSlice together. The Service has a ClusterIP and maps port 80 to node port 30080. The slice lists the three Pod IPs on port 8000.",
                "code": "$ kubectl get svc,endpointslices -n hello\nNAME                   TYPE       CLUSTER-IP      EXTERNAL-IP   PORT(S)        AGE\nservice/hello-devops   NodePort   10.96.171.215   <none>        80:30080/TCP   2m\n\nNAME                                                ADDRESSTYPE   PORTS   ENDPOINTS                          AGE\nendpointslice.discovery.k8s.io/hello-devops-kgnk9   IPv4          8000    10.244.1.3,10.244.2.4,10.244.1.5   2m",
                "lang": "console",
            },
            {
                "say": "Look at DNS from inside an app Pod. Its resolv.conf points at CoreDNS and lists the search domains. The app image has Python, so Python can resolve the short name, which comes back as the full name and the ClusterIP.",
                "code": "$ kubectl exec -n hello deploy/hello-devops -- cat /etc/resolv.conf\nsearch hello.svc.cluster.local svc.cluster.local cluster.local\nnameserver 10.96.0.10\noptions ndots:5\n$ kubectl exec -n hello deploy/hello-devops -- python -c \"import socket; print(socket.gethostbyname_ex('hello-devops'))\"\n('hello-devops.hello.svc.cluster.local', [], ['10.96.171.215'])",
                "lang": "console",
            },
            {
                "say": "Add the headless Service from the examples folder and resolve its name the same way. There is no virtual IP, so DNS returns one address per ready Pod.",
                "code": "$ kubectl apply -f k8s/examples/headless-service.yaml\nservice/hello-devops-headless created\n$ kubectl exec -n hello deploy/hello-devops -- python -c \"import socket; print(socket.gethostbyname_ex('hello-devops-headless'))\"\n('hello-devops-headless.hello.svc.cluster.local', [], ['10.244.1.3', '10.244.1.5', '10.244.2.4'])",
                "lang": "console",
            },
            {
                "say": "Scale the Deployment to 5 and read the EndpointSlice again. The controller added the two new Pods as soon as they were ready. kubectl shows the first three addresses and counts the rest.",
                "code": "$ kubectl scale deployment hello-devops -n hello --replicas=5\ndeployment.apps/hello-devops scaled\n$ kubectl get endpointslices -n hello -l kubernetes.io/service-name=hello-devops\nNAME                 ADDRESSTYPE   PORTS   ENDPOINTS                                      AGE\nhello-devops-kgnk9   IPv4          8000    10.244.1.3,10.244.2.4,10.244.1.5 + 2 more...   4m",
                "lang": "console",
            },
            {
                "say": "Call the Service from a throwaway Pod in another namespace. The short name fails there, because the search list starts with `default`. Adding the namespace works. `--rm` deletes the Pod when you leave the shell.",
                "code": "$ kubectl run tmp -n default --rm -it --restart=Never --image=busybox:1.37 -- sh\n/ # wget -qO- -T 3 http://hello-devops\nwget: bad address 'hello-devops'\n/ # wget -qO- -T 3 http://hello-devops.hello\n{\"host\":\"hello-devops-698679bfb-qjd64\",\"message\":\"Hello, DevOps!\",\"version\":\"1.0.0\",\"visits\":3}\n/ # exit\npod \"tmp\" deleted from default namespace",
                "lang": "console",
            },
            {
                "say": "Tidy up: scale back to 3 and remove the headless Service. The `visits` number above only counts calls to that one Pod; tomorrow Redis makes the counter shared.",
                "code": "$ kubectl scale deployment hello-devops -n hello --replicas=3\ndeployment.apps/hello-devops scaled\n$ kubectl delete -f k8s/examples/headless-service.yaml\nservice \"hello-devops-headless\" deleted from hello namespace",
                "lang": "console",
            },
        ],
    },
    "code": [
        {"lang": "yaml", "title": "k8s/service.yaml", "src": SERVICE, "run": "kubectl apply -k k8s"},
        {"lang": "yaml", "title": "k8s/kustomization.yaml (Day 33 version)", "src": KUSTOMIZATION_V2, "run": "kubectl apply -k k8s"},
        {"lang": "yaml", "title": "k8s/examples/headless-service.yaml", "src": ex("headless-service.yaml"), "run": "kubectl apply -f k8s/examples/headless-service.yaml"},
        {"lang": "yaml", "title": "k8s/examples/netpol-deny-all.yaml", "src": ex("netpol-deny-all.yaml"), "run": "kubectl apply -f k8s/examples/netpol-deny-all.yaml"},
        {"lang": "yaml", "title": "k8s/examples/netpol-allow.yaml", "src": ex("netpol-allow.yaml"), "run": "kubectl apply -f k8s/examples/netpol-allow.yaml"},
    ],
    "commands": [
        {"cmd": "kubectl get svc -n hello", "what": "List Services with their type, ClusterIP and ports."},
        {"cmd": "kubectl get endpointslices -n hello -l kubernetes.io/service-name=hello-devops", "what": "Show the Pod IPs and ports behind one Service."},
        {"cmd": "kubectl describe svc hello-devops -n hello", "what": "Show a Service's selector, ports, ClusterIP and endpoints."},
        {"cmd": "for i in {1..6}; do curl -s localhost:8081; done", "what": "Call the app six times through the NodePort; each call can land on another Pod."},
        {"cmd": "kubectl run tmp -n hello --rm -it --restart=Never --image=busybox:1.37 -- sh", "what": "Start a throwaway Pod with a shell for network tests; it is deleted when you exit."},
        {"cmd": "wget -qO- -T 3 http://hello-devops", "what": "Inside a busybox Pod: fetch a URL, giving up after 3 seconds."},
        {"cmd": "kubectl exec -n hello deploy/hello-devops -- cat /etc/resolv.conf", "what": "Show the DNS server and search list a Pod uses."},
        {"cmd": "kubectl port-forward svc/hello-devops 8080:80 -n hello", "what": "Tunnel localhost:8080 to the Service (kubectl picks one Pod)."},
        {"cmd": "kubectl run whoami -n hello --image=nginx:1.28 --port=80 --expose", "what": "Start a test Pod and a ClusterIP Service for it in one command."},
        {"cmd": "kubectl get networkpolicy -n hello", "what": "List the NetworkPolicies in a namespace."},
        {"cmd": "kubectl describe networkpolicy allow-web -n hello", "what": "Explain in words which Pods a policy selects and what it allows."},
        {"cmd": "kubectl -n kube-system get configmap kube-proxy -o yaml | grep mode", "what": "Show which mode kube-proxy runs in; kind uses iptables unless you ask for nftables."},
    ],
    "mistake": "When a Service \"does not work\", people blame the network. Most of the time the selector does not match the Pod labels exactly, or `targetPort` is not the port the app listens on. Check `kubectl get endpointslices` first: no addresses means a selector or readiness problem, and addresses that refuse connections mean a port problem.",
    "real_world": "At PayLite, every app gets a ClusterIP Service, and only the Gateway is exposed outside the cluster. Each team's namespace starts with a deny-all ingress policy, and the payments database accepts connections only from Pods labeled `app: payments-api`, which auditors like to see. Apps call each other by `service.namespace` names, so the same config works in dev, staging and production clusters.",
    "task": {
        "title": "Put a Service in front of the app, then lock the namespace",
        "steps": [
            "Write `k8s/service.yaml` (NodePort 30080), add it to `k8s/kustomization.yaml`, and apply with `kubectl apply -k k8s`.",
            "Call `curl localhost:8081` six times in a loop. Watch `host` change between Pods. Why do the `visits` numbers jump around?",
            "Break the Service on purpose: change its selector to `app: hello-devop` and apply. What does curl do now, and what do the EndpointSlices show? Fix it and apply again.",
            "Start a test web server in the namespace with `kubectl run whoami -n hello --image=nginx:1.28 --port=80 --expose`. From a throwaway busybox Pod, fetch both `http://whoami` and `http://hello-devops`.",
            "Apply `k8s/examples/netpol-deny-all.yaml`. Try `curl -m 3 localhost:8081` from your Mac and `wget -T 3 http://whoami` from a busybox Pod. What happened to each, and why does the deny-all block your Mac too?",
            "Apply `k8s/examples/netpol-allow.yaml`. Which of the two calls works again, and which stays blocked?",
            "Read the policies in plain words with `kubectl describe networkpolicy -n hello`.",
            "Clean up: delete the `whoami` Pod and Service and both policy files, so later days start with an open namespace. Commit `service.yaml` and the kustomization.",
        ],
        "hints": [
            "In zsh: `for i in {1..6}; do curl -s localhost:8081; done` (the app ends each answer with a new line).",
            "A wrong selector gives an EndpointSlice with no endpoints. The Service object itself still looks fine in `kubectl get svc`.",
            "Policies can take a few seconds to take effect. If nothing changes at all, check that the policy's namespace is `hello`.",
        ],
        "done_when": "With both policies applied, `curl localhost:8081` answers while `wget -T 3 http://whoami` from a busybox Pod times out; after cleanup, `kubectl get networkpolicy -n hello` shows nothing.",
    },
    "explain_back": {
        "prompt": "Explain in 3 to 4 sentences how a request from `curl localhost:8081` on your Mac reaches a hello-devops Pod. Mention the port mapping, the NodePort, kube-proxy and the EndpointSlice.",
        "answer": "The port mapping in kind-config.yaml forwards localhost:8081 on the Mac to port 30080 on the control-plane node container. On every node, kube-proxy has written kernel rules that catch traffic on the NodePort and on the Service's ClusterIP. Those rules pick one ready Pod from the Service's EndpointSlice. The packet goes to that Pod's IP on port 8000, even if the Pod runs on another node, and the reply comes back the same way.",
    },
    "recap": [
        "Every Pod gets its own IP from the CNI plugin, and by default every Pod can reach every other Pod.",
        "A Service selects Pods by label and gives them a stable ClusterIP and DNS name; EndpointSlices list the ready Pods.",
        "nodePort is on every node, port is on the Service, targetPort is on the Pod.",
        "kube-proxy turns Services into kernel rules and balances per connection, not per request.",
        "DNS names follow `<service>.<namespace>.svc.cluster.local`; short names work inside the same namespace.",
        "A NetworkPolicy that selects a Pod blocks everything it does not allow; kind's kindnet enforces them.",
    ],
    "check": [
        {
            "q": "A Service for `api` exists, but calls to it fail. `kubectl get endpointslices -l kubernetes.io/service-name=api` shows no endpoints, while the Pods are Running. What is the most likely cause?",
            "options": [
                "kube-proxy runs in iptables mode",
                "The nodePort is outside 30000 to 32767",
                "CoreDNS is down in kube-system",
                "The selector does not match the Pod labels",
            ],
            "answer": 3,
            "why": "Endpoints come from Pods that match the selector and are ready; Running Pods with no endpoints point to a label mismatch (or failing readiness).",
        },
        {
            "q": "A Pod in namespace `web` must call the Service `orders` in namespace `shop` on port 8080. Which URL works?",
            "options": [
                "http://orders:8080",
                "http://shop.orders:8080",
                "http://orders.shop:8080",
                "http://orders.svc:8080",
            ],
            "answer": 2,
            "why": "From another namespace you need at least `<service>.<namespace>`, here `orders.shop`; the short name only works inside `shop`.",
        },
        {
            "q": "You apply a deny-all ingress policy and an allow rule for Pods labeled `app: api` on port 8080. Next week a teammate deploys a new `worker` Pod into the same namespace. Who can connect to the worker?",
            "options": [
                "Nobody, because the deny-all policy selects every Pod, new ones included",
                "Everybody, because the policies were written before the Pod existed",
                "Only Pods labeled `app: api`, because of the allow rule",
                "Only Pods in other namespaces",
            ],
            "answer": 0,
            "why": "`podSelector: {}` matches every Pod in the namespace at any time, and nothing allows traffic to the worker.",
        },
    ],
    "interview": [
        {
            "q": "What Service types does Kubernetes have, and when do you use each?",
            "a": "ClusterIP is the default and is reachable only inside the cluster; most internal services use it. NodePort opens the same port on every node, which suits labs and simple setups. LoadBalancer asks a cloud controller for an external load balancer, the usual way to expose one TCP service in a cloud. ExternalName is only a DNS alias, and a headless Service (`clusterIP: None`) returns Pod IPs directly, which StatefulSets need. For HTTP traffic to many apps, teams put a Gateway in front of ClusterIP Services.",
        },
        {
            "q": "How does a Service actually route traffic to Pods?",
            "a": "The EndpointSlice controller watches the Pods matching the Service's selector and records their IPs, ports and readiness in EndpointSlices. On every node, kube-proxy watches Services and EndpointSlices. It programs kernel rules (iptables or nftables) that rewrite traffic for the ClusterIP or NodePort to one ready Pod. The choice is made per connection, so long-lived connections stick to one Pod. Some CNIs, such as Cilium, replace kube-proxy with eBPF.",
        },
        {
            "q": "How do NetworkPolicies work, and what is a common pitfall?",
            "a": "A NetworkPolicy selects Pods and lists allowed ingress or egress traffic by Pod labels, namespace labels, IP blocks and ports. Pods not selected by any policy allow everything; once selected for a direction, only allowed traffic passes, and policies only add permissions. A common pitfall is a default-deny egress policy that forgets DNS, so every lookup fails. Another is a CNI that does not enforce policies at all, so the YAML is accepted but has no effect.",
        },
    ],
    "deeper": {
        "minutes": 13,
        "body": """Look again at the resolv.conf from the worked example. The last line says `options ndots:5`. It changes how every name lookup in the Pod works.

ndots means: if a name has fewer than 5 dots, try the search list first. So when the app looks up `api.github.com` (two dots), the resolver first asks for:
1. `api.github.com.hello.svc.cluster.local`
2. `api.github.com.svc.cluster.local`
3. `api.github.com.cluster.local`
4. Then, finally, `api.github.com` itself.

Each try is a round trip to CoreDNS, often twice (for IPv4 and IPv6 addresses). For an app that calls outside APIs all the time, this adds load and a little latency. Two common fixes:
- Write outside names with a trailing dot, `api.github.com.`, which means the name is complete.
- Lower `ndots` for that Pod with `spec.dnsConfig.options`.

Kubernetes sets 5 so that names like `orders.shop.svc` still go through the search list. Most apps never need to touch it. It is worth knowing when someone says DNS in the cluster is slow.

A second detail: where does the client's IP address go? With a NodePort and the default `externalTrafficPolicy: Cluster`, a request can arrive on one node and be sent to a Pod on another. To make the reply come back the same way, kube-proxy replaces the source address with the node's address. Your app then logs a node IP, not the real client IP. Setting `externalTrafficPolicy: Local` keeps the client IP. The cost is that traffic only goes to Pods on the node that received it, and nodes without such a Pod drop it. Cloud load balancers handle this with health checks.

A third: Services can be dual-stack, with both IPv4 and IPv6 addresses, if the cluster supports it. The kind tool can create IPv6 and dual-stack clusters from its config file. That is a cheap way to test an app before a real IPv6 rollout.

Finally, the old `Endpoints` object still exists but has been deprecated since 1.33 in favor of EndpointSlices. A slice holds at most 100 endpoints by default, so a Service with 250 Pods has three slices. Tools that read endpoints should read slices. `kubectl get endpoints` still works and prints a deprecation warning.

To see the whole picture with diagrams, read [Virtual IPs and Service proxies](https://kubernetes.io/docs/reference/networking/virtual-ips/) in the Kubernetes docs.""",
    },
    "sources": [
        {"title": "Service", "url": "https://kubernetes.io/docs/concepts/services-networking/service/"},
        {"title": "DNS for Services and Pods", "url": "https://kubernetes.io/docs/concepts/services-networking/dns-pod-service/"},
        {"title": "Network policies", "url": "https://kubernetes.io/docs/concepts/services-networking/network-policies/"},
        {"title": "kind configuration", "url": "https://kind.sigs.k8s.io/docs/user/configuration/"},
    ],
}
