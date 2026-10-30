import re
def sub(path, pairs):
    s = open(path).read()
    for a, b in pairs:
        if a not in s:
            raise SystemExit(f"{path}: not found: {a[:70]}")
        s = s.replace(a, b, 1)
    open(path, 'w').write(s)

sub('d30.py', [
    ('"h": "kind: a real cluster on your laptop"', '"h": "A real cluster on your laptop with kind"'),
    ("inside. kind uses kubeadm, the official setup tool,", "inside. The kind tool uses kubeadm, the official setup tool,"),
    ("Waiters never talk to cooks: they pin order tickets on a rail (the API server, with etcd as the rail's memory). The head chef reads new tickets and assigns each dish to a station (the scheduler), each station cook makes only the dishes assigned to them (the kubelet), and a manager keeps checking that every table got what it ordered and has dropped plates remade (the controllers).",
     "Waiters never talk to cooks: they pin order tickets on a rail (the API server, with etcd as the rail's memory). The head chef reads new tickets and assigns each dish to a station (the scheduler). Each station cook makes only the dishes assigned to them (the kubelet). A manager keeps checking that every table got what it ordered, and has dropped plates remade (the controllers)."),
    ("Two things follow from this design, and both surprise people at first:", "Two things follow from this, and both surprise people at first:"),
])

sub('d31.py', [
    ("That order fixes two old problems: a log shipper that started late and missed the first lines, and one that stopped early and lost the last ones. kubectl's READY column counts sidecars too, so a Pod with one sidecar and one app shows `2/2`.",
     "That order fixes two old problems. A log shipper that started late missed the first lines, and one that stopped early lost the last ones. The READY column of kubectl counts sidecars too, so a Pod with one sidecar and one app shows `2/2`."),
    ("but they think differently. `create` is a one-time order, and it fails if the object already exists. `apply` is declarative:",
     "but they think differently. The `create` command is a one-time order, and it fails if the object already exists. The `apply` command is declarative:"),
    ("Running kubectl against the wrong cluster. A new laptop often has a `docker-desktop` context too, and at work you will have real clusters in the same kubeconfig, so a `kubectl delete` can land somewhere you did not mean.",
     "Running kubectl against the wrong cluster. A new laptop often has a `docker-desktop` context too, and at work you will have real clusters in the same kubeconfig. One `kubectl delete` can then land somewhere you did not mean."),
    ("At PayLite, the checkout Pod runs the app plus a native sidecar that ships logs to the central log system, and an init container that waits for the database during start-up.",
     "At PayLite, the checkout Pod runs the app plus a native sidecar that ships logs to the central log system. An init container waits for the database during start-up."),
    ("Make one more request for a page that does not exist, then read the sidecar's logs. nginx wrote both requests to `access.log` in the shared volume, and the sidecar printed them.",
     "Next, request a page that does not exist and read the sidecar's logs. Both requests went into `access.log` in the shared volume, and the sidecar printed them."),
    ("Since Kubernetes 1.33 native sidecars are stable: you declare them as init containers with `restartPolicy: Always`, so they start before the app, are restarted if they crash, and stop after the app.",
     "Native sidecars have been stable since Kubernetes 1.33. You declare them as init containers with `restartPolicy: Always`. They start before the app, are restarted if they crash, and stop after the app."),
    ("\"a\": \"`kubectl create` is imperative: it creates the object and fails if it already exists. `kubectl apply` is declarative: it creates the object if needed, or updates it to match the file, and records what you applied in an annotation so it can work out changes next time.",
     "\"a\": \"The `kubectl create` command is imperative: it creates the object and fails if it already exists. The `kubectl apply` command is declarative. It creates the object if needed, or updates it to match the file. It also records what you applied in an annotation, so it can work out the changes next time."),
    ("This trips up most people, so when STATUS looks odd, read `kubectl describe pod`.",
     "Most people mix these up at first, so when STATUS looks odd, read `kubectl describe pod`."),
    # more depth: explain output and strict validation
    ("2. `kubectl explain pod.spec.restartPolicy` prints the docs for one field, straight from your cluster's API, so it always matches your version. Add `--recursive` to see a whole tree.",
     "2. `kubectl explain pod.spec.restartPolicy` prints the docs for one field, straight from your cluster's API, so it always matches your version. For this field it shows the type (`<string>`), the allowed values `Always`, `Never` and `OnFailure`, and a description. Add `--recursive` to see a whole tree."),
    ("You never write the fifth field, `status`. Kubernetes fills it in.",
     "You never write the fifth field, `status`. Kubernetes fills it in. A typo in a field name does not slip through, either. kubectl validates strictly by default, so `imagePullPolicyy` fails with an error that names the unknown field."),
])

sub('d32.py', [
    ("Blue-green and canary releases, where you shift traffic gradually or flip it all at once, need extra tools such as Argo Rollouts, or traffic rules at a Gateway (Day 36).",
     "Canary and blue-green releases need extra tools. A canary shifts traffic to the new version a little at a time, and blue-green flips all traffic at once. Argo Rollouts can do both, and so can traffic rules at a Gateway (Day 36)."),
    ("The picture breaks on memory: a new operator can look up past calls, but a new Pod starts empty, so anything worth keeping must live outside it, the way hello-devops keeps its counter in Redis.",
     "The picture breaks on memory. A new operator can look up past calls, but a new Pod starts empty, so anything worth keeping must live outside it, the way hello-devops keeps its counter in Redis."),
    ("A dead node takes longer, and this surprises people.", "A dead node takes longer than most people expect."),
    ("Each object points to its owner in `metadata.ownerReferences`. Delete the Deployment and the garbage collector removes its ReplicaSets and Pods too.",
     "Each object points to its owner in `metadata.ownerReferences`. Delete the Deployment and the garbage collector removes its ReplicaSets and Pods too. You can follow the chain yourself: `kubectl get pod NAME -o jsonpath='{.metadata.ownerReferences[0].name}'` prints the ReplicaSet that owns a Pod."),
    ("Each ReplicaSet gets a revision number in an annotation.",
     "To know before you apply whether a change will roll, run `kubectl diff -k k8s`. If the diff touches lines under `template:`, expect new Pods.\n\nEach ReplicaSet gets a revision number in an annotation."),
    ("`minReadySeconds` adds one more guard.",
     "For hello-devops, a version that crashes on start never becomes ready, and you get the stuck rollout from the worked example. A version that starts but answers every request with an error is worse. Without a probe it looks ready, and the rollout completes.\n\n`minReadySeconds` adds one more guard."),
])

sub('d33.py', [
    ('"h": "port, targetPort and nodePort"', '"h": "Three ports: port, targetPort and nodePort"'),
    ('"h": "kube-proxy turns Services into packet rules"', '"h": "How kube-proxy turns Services into packet rules"'),
    ("If the selector matches no Pods, for example because of a typo in a label, the Service exists but leads nowhere. `kubectl get endpointslices -l kubernetes.io/service-name=hello-devops` tells you which case you are in, and it is the first thing to check when a Service \\\"does not work\\\".",
     "If the selector matches no Pods, for example because of a typo in a label, the Service exists but leads nowhere. Run `kubectl get endpointslices -l kubernetes.io/service-name=hello-devops` to see which case you are in. It is the first thing to check when a Service \\\"does not work\\\"."),
    ("On a Mac, though, the address it hands out (172.18.x.x) lives inside Docker Desktop's VM, and your Mac cannot reach it. cloud-provider-kind works around this with a proxy container named `kindccm-...` that publishes a port on localhost.",
     "On a Mac, though, the address it hands out (172.18.x.x) lives inside Docker Desktop's VM, and your Mac cannot reach it. The tool works around this with a proxy container named `kindccm-...` that publishes a port on localhost."),
    ("Policies need a network plugin that enforces them, and some plugins accept the objects and silently ignore them. kind's kindnet does enforce them, so you can test the real thing on your laptop.",
     "Policies need a network plugin that enforces them. Some plugins accept the objects and silently ignore them. The kindnet plugin that kind installs does enforce them, so you can test the real thing on your laptop."),
    ("Here is how the rules work. The second one trips up most people:", "Here is how the rules work. The second one is the one people miss:"),
    ("Two things follow from this design, and both surprise people:", "Two consequences matter in practice:"),
    ("A Service is like a company's main phone number. Callers dial one number and get whichever agent is free, and agents can join, leave or change desks without anyone updating a phone book; CoreDNS is the phone book that maps the company name to that number.",
     "A Service is like a company's main phone number. Callers dial one number and get whichever agent is free. Agents can join, leave or change desks, and nobody updates a phone book. CoreDNS is the phone book that maps the company name to that one number."),
    ("The picture breaks on fairness: a phone system can route each call to the least busy agent, while kube-proxy picks a Pod per connection and does not know how busy each Pod is.",
     "The picture breaks on fairness. A phone system can route each call to the least busy agent, while kube-proxy picks a Pod per connection and does not know how busy each Pod is."),
    ("\"answer\": \"kind's port mapping forwards localhost:8081 on the Mac to port 30080 on the control-plane node container. kube-proxy has written kernel rules on every node that catch traffic on the NodePort and on the Service's ClusterIP port 80. Those rules pick one ready Pod from the Service's EndpointSlice and send the packet to that Pod's IP on port 8000, even if the Pod runs on another node. The app answers, and the reply goes back along the same path.\"",
     "\"answer\": \"The port mapping in kind-config.yaml forwards localhost:8081 on the Mac to port 30080 on the control-plane node container. On every node, kube-proxy has written kernel rules that catch traffic on the NodePort and on the Service's ClusterIP. Those rules pick one ready Pod from the Service's EndpointSlice. The packet goes to that Pod's IP on port 8000, even if the Pod runs on another node, and the reply comes back the same way.\""),
    ("in EndpointSlices. kube-proxy on every node watches Services and EndpointSlices and programs kernel rules (iptables or nftables) that rewrite traffic for the ClusterIP or NodePort to one ready Pod.",
     "in EndpointSlices. On every node, kube-proxy watches Services and EndpointSlices. It programs kernel rules (iptables or nftables) that rewrite traffic for the ClusterIP or NodePort to one ready Pod."),
    ("A third: Services can be dual-stack, with both IPv4 and IPv6 addresses, if the cluster supports it. kind can create IPv6 and dual-stack clusters through its config file, which is a cheap way to test an app before a real IPv6 rollout.",
     "A third: Services can be dual-stack, with both IPv4 and IPv6 addresses, if the cluster supports it. The kind tool can create IPv6 and dual-stack clusters from its config file. That is a cheap way to test an app before a real IPv6 rollout."),
    ("On kind, each node gets its own slice of the Pod range 10.244.0.0/16.",
     "On kind, each node gets its own slice of the Pod range 10.244.0.0/16. `kubectl get nodes -o jsonpath='{.items[*].spec.podCIDR}'` prints them, for example `10.244.0.0/24 10.244.1.0/24 10.244.2.0/24`."),
])

sub('d34.py', [
    ("A ConfigMap mounted as an env var is like a note pinned inside a new employee's locker on their first day: they read it once and never look again, so a changed note only reaches the next new hire.",
     "A ConfigMap read as env vars is like a note in a new employee's locker on their first day. They read it once and never look again, so a changed note only reaches the next new hire."),
    ("The comparison breaks on reach: anyone allowed to hire staff into a team can hand that new hire every envelope the team has, just as anyone who can create Pods in a namespace can read its Secrets.",
     "The comparison breaks on reach. Anyone who can create Pods in a namespace can read all its Secrets, as if anyone allowed to hire staff could open every envelope the team holds."),
    ("To make every Pod use new env values, run `kubectl rollout restart`, which changes the Pod template and so starts a normal rolling update; tools like Kustomize do the same by giving each config version a new name.",
     "To make every Pod use new env values, run `kubectl rollout restart`, which changes the Pod template and starts a normal rolling update. Tools like Kustomize get the same effect by giving each config version a new name."),
    ("This is where most people get surprised.", "Most people get this wrong the first time."),
    ('"nginx restarts with the new config at once",\n                "The file changes after a short delay, but nginx keeps the old config until it reloads",\n                "Nothing changes until the Pod is deleted",\n                "The Pod fails, because a mounted ConfigMap is read-only",',
     '"nginx notices the change and restarts with the new config",\n                "The file changes soon, but nginx uses it only after a reload",\n                "Nothing changes until someone deletes and recreates the Pod",\n                "The Pod fails, because mounted ConfigMap files are read-only",'),
    ('"True, as long as the cluster runs Kubernetes 1.30 or newer",\n                "True, because kubectl hides Secret values from everyone",\n                "False, because Secrets cannot hold binary data",\n                "False, because base64 decodes in one command; safety comes from encryption at rest and access rules",',
     '"True, as long as the cluster runs Kubernetes 1.30 or newer",\n                "True, because kubectl hides Secret values from every user",\n                "False, because Secrets cannot hold binary data like keys",\n                "False: anyone can decode base64; encryption and access rules protect them",'),
])

sub('build_p7a.py', [
    ("You build a real three-node cluster on your Mac with kind, learn how its parts work together, and then add one object at a time: Pods, Deployments, Services, config and Secrets, health checks, traffic, packaging and debugging.",
     "You build a real three-node cluster on your Mac with kind and learn how its parts work together. Then you add one object at a time: Pods, Deployments, Services, config and Secrets, health checks, traffic, packaging and debugging."),
])
print("ok")
