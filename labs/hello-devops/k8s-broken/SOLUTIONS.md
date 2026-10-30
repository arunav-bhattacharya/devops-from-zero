# Solutions for the break-and-fix lab (Day 38)

Read these after you have tried. Each entry has the cause, where the evidence was, and the fix.
Exact messages differ a little between versions; the important words are the same.

## 1. catalog: ImagePullBackOff

- Cause: the image tag `hello-devops:1.0.1` does not exist. Only `1.0.0` was built and loaded into kind.
- Evidence: `kubectl describe pod` Events show `Failed to pull image "hello-devops:1.0.1"`. Because the image
  is not on the node, the kubelet asks Docker Hub, which has no such image, so the pull is refused.
  After a few failures the kubelet waits longer between tries: that waiting is `ImagePullBackOff`.
- Fix: in `01-catalog.yaml` set `image: hello-devops:1.0.0`, then `kubectl apply -f k8s-broken/01-catalog.yaml`.
  (If you really meant a new version, build it, tag it and `kind load docker-image` it first.)

## 2. checkout: CreateContainerConfigError

- Cause: the Deployment reads its settings from a ConfigMap named `checkout-config`, but the ConfigMap in the
  file is called `checkout-settings`. The kubelet cannot build the container's environment, so it never starts it.
  That is also why `kubectl logs` is empty: no process ever ran.
- Evidence: `kubectl describe pod` Events show `Error: configmap "checkout-config" not found`.
- Fix: in `02-checkout.yaml` change `configMapRef.name` to `checkout-settings` (or rename the ConfigMap), then apply.
  The kubelet retries on its own, so the Pod starts within seconds.

## 3. search: Running and Ready, but the Service gets nothing

- Cause: the Service selects Pods with `app: search-api`, but the Pods have the label `app: search`.
  The Service matches no Pods, so it has no endpoints. The Pods are healthy; nothing sends them traffic.
- Evidence:
  - `kubectl get endpointslices -n debug-lab -l kubernetes.io/service-name=search` shows `<unset>` under ENDPOINTS.
  - `kubectl get pods -n debug-lab --show-labels` shows `app=search`, and `kubectl describe service search -n debug-lab` shows `Selector: app=search-api`.
  - A port-forward straight to one Pod (`kubectl port-forward pod/<search-pod> 8095:8000 -n debug-lab`) works, which proves the app is fine.
- Fix: in `03-search.yaml` set the Service selector to `app: search`, then apply. The EndpointSlice fills with two Pod IPs.

## 4. reports: OOMKilled, then CrashLoopBackOff

- Cause: the memory limit is `40Mi`. The app (gunicorn with two workers) needs about 100 MiB to start, so the kernel
  kills the container as soon as it goes over the limit. Kubernetes restarts it, it dies again, and the restarts back off.
- Evidence: `kubectl describe pod` shows `Last State: Terminated`, `Reason: OOMKilled`, `Exit Code: 137`.
  `kubectl logs --previous` shows gunicorn starting normally, then nothing: the process was killed from outside, so it printed no error.
- Fix: in `04-reports.yaml` set the memory request to `128Mi` and the limit to `256Mi` (the same as the main app), then apply.
  With metrics-server installed, `kubectl top pod -n debug-lab` shows the real use, which is how you pick numbers at work.

## 5. profile: restarts every half a minute

- Cause: the liveness probe checks port `8080`, but the app listens on `8000`. Every check fails with "connection refused".
  After 3 failures in a row (`failureThreshold` default 3, every 10 seconds) the kubelet kills the container and starts a new one.
  The readiness probe uses the right port, which is why the Pod looks Ready between restarts.
- Evidence: `kubectl describe pod` Events show `Liveness probe failed: Get "http://10.244.x.y:8080/healthz": dial tcp 10.244.x.y:8080: connect: connection refused`
  and then `Container web failed liveness probe, will be restarted`.
  The logs look normal because the app itself is fine.
- Fix: in `05-profile.yaml` set the liveness probe to `port: http` (the named port, 8000), then apply.
  Using the port name instead of a number avoids this whole class of mistake.

## What to remember

| STATUS or symptom | First place to look | Usual cause |
|---|---|---|
| `ErrImagePull` / `ImagePullBackOff` | describe, Events | wrong name or tag, private registry, image not loaded into kind |
| `CreateContainerConfigError` | describe, Events | a missing ConfigMap, Secret or key |
| `Running`, Ready, but the Service fails | EndpointSlices, labels | the Service selector or `targetPort` does not match the Pods |
| `OOMKilled` / exit code 137 | describe, `Last State` | memory limit too low, or a memory leak |
| Restarts with clean logs | describe, Events | a liveness probe that checks the wrong thing |
