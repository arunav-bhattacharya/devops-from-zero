def sub(path, pairs):
    s = open(path).read()
    for a, b in pairs:
        if a not in s:
            raise SystemExit(f"{path}: not found: {a[:70]}")
        s = s.replace(a, b, 1)
    open(path, 'w').write(s)

sub('d32.py', [
    ("The picture breaks on memory. A new operator can look up past calls, but a new Pod starts empty, so anything worth keeping must live outside it, the way hello-devops keeps its counter in Redis.",
     "The picture breaks on memory. A new operator can look up past calls, but a new Pod starts empty. Anything worth keeping must live outside it, the way hello-devops keeps its counter in Redis."),
])
sub('d31.py', [
    ("Each container also has a state of its own:",
     "A normal start shows up in STATUS as `Pending` (no node yet), then `ContainerCreating` (node chosen, image being pulled, phase still `Pending`), then `Running`.\n\nEach container also has a state of its own:"),
    ("One context is current, and every kubectl command goes there.",
     "One context is current, and every kubectl command goes there. `kubectl config get-contexts` lists them all and marks the current one with a star."),
    ("- Remove it: `kubectl delete pod hello`, or `kubectl delete -f pod.yaml`.",
     "- Remove it: `kubectl delete pod hello`, or `kubectl delete -f pod.yaml`.\n- Just one field, please: `-o jsonpath='{.status.phase}'` prints a single value, which is handy in scripts."),
])
sub('d33.py', [
    ("A Service gives a changing set of Pods one stable virtual IP address and one DNS name.",
     "A **Service** gives a changing set of Pods one stable virtual IP address and one DNS name."),
    ("A `curl` loop opens a new connection each time, so it spreads.",
     "A `curl` loop opens a new connection each time, so it spreads.\n- If one client must keep talking to the same Pod, set `sessionAffinity: ClientIP` on the Service. kube-proxy then pins each client IP to one Pod for a while."),
    ("A normal Service name resolves to its one ClusterIP. A headless Service name resolves to every ready Pod IP behind it, which the worked example shows.",
     "A normal Service name resolves to its one ClusterIP. A headless Service name resolves to every ready Pod IP behind it, which the worked example shows. With a StatefulSet, each Pod also gets its own stable name, such as `db-0.db.hello.svc.cluster.local` (Day 36)."),
    ("- Rules match sources by Pod labels, namespace labels or IP ranges, plus ports.",
     "- Rules match sources by Pod labels, namespace labels or IP ranges, plus ports. Every namespace carries the label `kubernetes.io/metadata.name` with its own name, so a rule can allow, say, the whole `monitoring` namespace."),
])
print('ok')
