# Linkerd lab: automatic mTLS and a GAMMA canary (Day 60)

The same apps as the Istio lab, meshed with Linkerd instead, and the same HTTPRoute
canary. Use a separate kind cluster, so the two meshes never meet.

| File | What it does |
|---|---|
| `namespace.yaml` | `hello-mesh` with the annotation `linkerd.io/inject: enabled` |
| `../istio/apps.yaml` | Reused as is: hello-devops v1, the canary, their Services and the `client` Pod |
| `httproute-canary.yaml` | The Day 59 canary route, plus Linkerd's retry annotations |
| `CHECKLIST.md` | Do you need a mesh, and which one? |

## How these files were checked

They were not run on a cluster: kind cannot start a cluster in the course's test
environment, and the Linkerd CLI was not run. `kubeconform -strict` passed for the built-in
kinds and for the HTTPRoute, against JSON schemas generated from Gateway API v1.5.1 and
v1.6.0 `standard-install.yaml`. The route's spec is identical to `../istio/httproute-canary.yaml`.

## Run it on kind (Mac)

```bash
# 1. A cluster and the Linkerd CLI (the latest edge release)
kind create cluster --name linkerd
curl --proto '=https' --tlsv1.2 -sSfL https://run.linkerd.io/install-edge | sh
export PATH=$HOME/.linkerd2/bin:$PATH
linkerd version

# 2. Gateway API CRDs. Linkerd 2.20 supports Gateway API v1.2.1 to v1.5.1.
kubectl apply --server-side -f https://github.com/kubernetes-sigs/gateway-api/releases/download/v1.5.1/standard-install.yaml

# 3. Check the cluster, install the control plane, check again
linkerd check --pre
linkerd install --crds | kubectl apply -f -
linkerd install | kubectl apply -f -
linkerd check

# 4. The viz extension: metrics and a dashboard
linkerd viz install | kubectl apply -f -
linkerd check

# 5. The apps. The annotation on the namespace makes Linkerd inject its proxy.
kind load docker-image hello-devops:1.0.0 --name linkerd
kubectl apply -f namespace.yaml -f ../istio/apps.yaml
kubectl wait -n hello-mesh --for=condition=Available deployment --all --timeout=180s
linkerd -n hello-mesh check --proxy

# 6. mTLS is already on. Make some traffic, then look at the SECURED column.
kubectl exec -n hello-mesh deploy/client -c curl -- sh -c \
  'for i in $(seq 1 50); do curl -s -o /dev/null http://hello-devops/; done'
linkerd viz -n hello-mesh edges deployment

# 7. The canary
kubectl apply -f httproute-canary.yaml
kubectl exec -n hello-mesh deploy/client -c curl -- sh -c \
  'for i in $(seq 1 200); do curl -s http://hello-devops/; echo; done' | jq -r .version | sort | uniq -c
linkerd viz -n hello-mesh stat-outbound deploy/client

# 8. The dashboard (Ctrl-C to stop)
linkerd viz dashboard

# 9. Clean up
kind delete cluster --name linkerd
```

## Notes

- Releases: the Linkerd project publishes edge releases (`edge-26.11.1` was the newest
  on 2026-11-07). Stable releases such as 2.20 come from vendors, mainly Buoyant
  Enterprise for Linkerd, which Buoyant says is free for companies with fewer than 50
  employees. The code is Apache 2.0 either way.
- `brew install linkerd` installs a CLI built from the `version-2.20` tag (the same code as
  `edge-26.6.3`), not the newest edge. Keep the CLI and the control plane on one release.
- The trust anchor that `linkerd install` creates expires after 365 days. For anything
  that lives longer than a lab, create your own and plan its rotation.
- When a route is attached to a Service, requests that match none of its rules are
  rejected. Rule 2 has no `matches`, which means every path, so nothing falls through.
