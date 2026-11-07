# Istio lab: canary, circuit breaking, mTLS and fault injection (Day 59)

hello-devops and a canary run in the namespace `hello-mesh` with Envoy sidecars. A
`client` Pod calls them from inside the mesh. The manifests use sidecar mode, where every
API here is stable. The `ambient/` folder has the three files that change for ambient mode.

| File | What it does |
|---|---|
| `namespace.yaml` | `hello-mesh` (label `istio-injection=enabled`) and `outside` (not in the mesh) |
| `apps.yaml` | ServiceAccounts, hello-devops v1 (2 Pods), the canary (1 Pod), their Services, and a `client` Pod with curl |
| `httproute-canary.yaml` | Gateway API HTTPRoute on the `hello-devops` Service: 90/10 split, `x-canary: always` header, 3s timeout |
| `destinationrule.yaml` | Circuit breaking: connection pool limits and outlier detection |
| `peerauthentication.yaml` | mTLS `STRICT` for the namespace |
| `authorizationpolicy.yaml` | DENY `/metrics` outside `monitoring`; ALLOW only the `client` identity to GET three paths |
| `virtualservice-fault.yaml` | Istio API: delay and abort faults for requests with `x-fault: on`; timeout and retries for the rest |
| `ambient/namespace.yaml` | Ambient variant of the namespace (ztunnel plus a waypoint) |
| `ambient/waypoint.yaml` | The waypoint proxy, as a Gateway of class `istio-waypoint` |
| `ambient/authorizationpolicy.yaml` | Ambient variant of the ALLOW policy, attached to the waypoint with `targetRefs` |

## How these files were checked

They were not run on a cluster. In the course's test environment kind cannot start a
cluster, and istioctl was not run. They were checked offline:

- `kubeconform -strict` with its built-in schemas for Namespace, ServiceAccount,
  Deployment and Service.
- `kubeconform -strict` with JSON schemas generated from the CRD files that the projects
  publish: Istio 1.31 (`kubernetes/customresourcedefinitions.gen.yaml` on the
  `release-1.31` branch of istio/api) and Gateway API v1.6.0 `standard-install.yaml`.
- A hand check of the CEL rules in those CRDs (durations, `selector` or `targetRefs`
  but not both, ports on Service references), because kubeconform skips CEL.

Run `istioctl analyze --use-kube=false *.yaml` on your Mac for Istio's own offline checks.

## Run it on kind (Mac, sidecar mode)

Give Docker Desktop at least 8 GB of memory. Then, from this folder:

```bash
# 1. A cluster and istioctl (or: curl -L https://istio.io/downloadIstio | sh -)
kind create cluster --name mesh
brew install istioctl
istioctl x precheck

# 2. Gateway API CRDs (Istio 1.31's docs install v1.6.0), then Istio's control plane only
kubectl get crd gateways.gateway.networking.k8s.io &> /dev/null || \
  kubectl apply --server-side -f https://github.com/kubernetes-sigs/gateway-api/releases/download/v1.6.0/standard-install.yaml
istioctl install --set profile=minimal -y

# 3. The apps. The namespace label makes Istio add a sidecar to each new Pod.
kind load docker-image hello-devops:1.0.0 --name mesh
kubectl apply -f namespace.yaml -f apps.yaml
kubectl wait -n hello-mesh --for=condition=Available deployment --all --timeout=180s
istioctl proxy-status          # every Pod in hello-mesh should be listed as SYNCED

# 4. The canary: count which version answers 200 calls made from inside the mesh
kubectl apply -f httproute-canary.yaml
kubectl exec -n hello-mesh deploy/client -c curl -- sh -c \
  'for i in $(seq 1 200); do curl -s http://hello-devops/; echo; done' | jq -r .version | sort | uniq -c
kubectl exec -n hello-mesh deploy/client -c curl -- curl -s -H 'x-canary: always' http://hello-devops/

# 5. Circuit breaking, then mTLS. First call from outside the mesh: it works (PERMISSIVE).
kubectl apply -f destinationrule.yaml
kubectl run curl -n outside --image=curlimages/curl:8.22.0 --rm -it --restart=Never -- \
  curl -sS -m 3 http://hello-devops.hello-mesh/
kubectl apply -f peerauthentication.yaml
# The same call again now fails: plain text is refused under STRICT.
kubectl run curl -n outside --image=curlimages/curl:8.22.0 --rm -it --restart=Never -- \
  curl -sS -m 3 http://hello-devops.hello-mesh/

# 6. Authorization: / works for the client, /metrics answers 403 "RBAC: access denied"
kubectl apply -f authorizationpolicy.yaml
kubectl exec -n hello-mesh deploy/client -c curl -- curl -s -o /dev/null -w '%{http_code}\n' http://hello-devops/
kubectl exec -n hello-mesh deploy/client -c curl -- curl -s http://hello-devops/metrics

# 7. Fault injection. Remove the HTTPRoute first: one routing API per Service.
kubectl delete -f httproute-canary.yaml
kubectl apply -f virtualservice-fault.yaml
kubectl exec -n hello-mesh deploy/client -c curl -- sh -c \
  'for i in $(seq 1 20); do curl -s -o /dev/null -w "%{http_code} %{time_total}\n" -H "x-fault: on" http://hello-devops/; done'

# 8. Look inside the client's sidecar: the same Envoy objects as Day 58
istioctl analyze -n hello-mesh
istioctl proxy-config listener deployment/client -n hello-mesh
istioctl proxy-config route deployment/client -n hello-mesh
istioctl proxy-config cluster deployment/client -n hello-mesh | grep hello
istioctl proxy-config endpoint deployment/client -n hello-mesh | grep hello
istioctl proxy-config secret deployment/hello-devops -n hello-mesh
istioctl dashboard envoy deployment/client -n hello-mesh   # the Envoy admin page

# 9. Clean up
kind delete cluster --name mesh
```

With native sidecars (the default since Istio 1.27 on Kubernetes 1.33 and later),
`istio-proxy` runs as an init container that keeps running. That is why `-c curl` picks
the app container explicitly in the `kubectl exec` commands.

## The ambient variant

Install with `istioctl install --set profile=ambient --skip-confirmation` instead of
step 2's `minimal` profile. Then use `ambient/namespace.yaml` instead of `namespace.yaml`,
apply `ambient/waypoint.yaml` (or run `istioctl waypoint apply -n hello-mesh`), and use
`ambient/authorizationpolicy.yaml` instead of the ALLOW policy in `authorizationpolicy.yaml`.
The HTTPRoute, DestinationRule and PeerAuthentication work unchanged. Skip
`virtualservice-fault.yaml`: VirtualService on a waypoint is still Alpha in Istio 1.31.
Look at ztunnel with `istioctl ztunnel-config workload` and `istioctl ztunnel-config certificate`.

## Metrics and the Kiali graph (optional)

```bash
kubectl apply -f https://raw.githubusercontent.com/istio/istio/release-1.31/samples/addons/prometheus.yaml
kubectl apply -f https://raw.githubusercontent.com/istio/istio/release-1.31/samples/addons/kiali.yaml
istioctl dashboard kiali
```

The metric to start with in Prometheus is `istio_requests_total`.
