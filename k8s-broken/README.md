# Break-and-fix lab (Day 38)

A small online shop runs five services. Each one is broken in a different way.
Your job: find out why with `kubectl`, fix the YAML file, apply it again, and check the fix.

Do not open `SOLUTIONS.md` until you have tried each one. The skill you are practising is the
search, not the answer.

## Before you start

- Your kind cluster from Day 30 is running (`kubectl get nodes` shows three Ready nodes).
- The image is loaded into the cluster: `kind load docker-image hello-devops:1.0.0 --name devops`.
- Optional: metrics-server from Day 35, so `kubectl top` works.

## Start the lab

```bash
kubectl apply -f k8s-broken/
kubectl get pods -n debug-lab -w
```

Wait about two minutes before you start. Some problems only show after a few restarts.

## What the shop team reports

| Service | File | What people see |
|---|---|---|
| catalog | `01-catalog.yaml` | The Pod never starts. Its STATUS is `ErrImagePull`, then `ImagePullBackOff`. |
| checkout | `02-checkout.yaml` | The Pod stays `0/1` with STATUS `CreateContainerConfigError`. `kubectl logs` shows nothing. |
| search | `03-search.yaml` | Both Pods are `Running` and `1/1` Ready, but requests to `http://search.debug-lab` fail. |
| reports | `04-reports.yaml` | RESTARTS keeps going up. STATUS switches between `OOMKilled` and `CrashLoopBackOff`. |
| profile | `05-profile.yaml` | The Pod is `Running` and Ready, then restarts every half a minute or so. The logs look normal. |

To test the search service from inside the cluster, start a throwaway Pod:

```bash
kubectl run net-test -n debug-lab --rm -it --image=busybox:1.37 --restart=Never -- wget -qO- -T 3 http://search
```

## The method (use it for every service)

1. `kubectl get pods -n debug-lab`: which Pod, which STATUS, how many RESTARTS.
2. `kubectl describe pod <pod> -n debug-lab`: read the Events at the bottom first, then `Last State`.
3. `kubectl logs <pod> -n debug-lab --previous`: what the crashed container printed before it died.
4. `kubectl get events -n debug-lab --sort-by=.metadata.creationTimestamp`: everything that happened, in order.
5. For a Service: `kubectl get endpointslices -n debug-lab -l kubernetes.io/service-name=<service>`.
6. Compare what you found with the YAML file. Change one thing, `kubectl apply -f` the file, and watch again.

## You are done when

- `kubectl get pods -n debug-lab` shows every Pod `Running`, `1/1` Ready, and RESTARTS no longer going up for two minutes.
- The `net-test` command above prints JSON from the search service.

Clean up with `kubectl delete namespace debug-lab`.
