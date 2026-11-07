# Do you need a service mesh? A checklist (Day 60)

Answer the questions in order. Stop at the first section that settles it.

## 1. Can you do without one?

You probably do not need a mesh yet if all of these are true:

- [ ] You run fewer than about ten services, owned by one or two teams.
- [ ] Most services are written in one or two languages, so a shared client library
      (for example Resilience4j on the JVM) can do retries and timeouts.
- [ ] NetworkPolicies (Day 41) already limit which Pods may talk to which.
- [ ] One Gateway (Day 44) handles TLS and routing for traffic from outside.
- [ ] OpenTelemetry (Day 57) and Prometheus (Day 50) already show you per-service errors
      and latency.
- [ ] No auditor or customer requires encryption and identity on every internal call.

If you ticked every box, write down what would change your mind and revisit in six months.

## 2. What would a mesh give you that you lack today?

Tick the ones you need now, not some day:

- [ ] mTLS between every pair of services, with identities you can write policy about
- [ ] The same golden metrics (requests, errors, latency) for every service, with no code
- [ ] Traffic splitting for canaries between services inside the cluster
- [ ] Retries, timeouts and circuit breaking set the same way for every language
- [ ] Authorization by caller identity and HTTP path
- [ ] Traffic between several clusters

No ticks: go back to section 1. One or two ticks: check whether a smaller tool covers them
(Cilium as your CNI, a client library, cert-manager). Three or more: read on.

## 3. Which one?

- Linkerd: you want mTLS and golden metrics with the fewest moving parts, and you are
  fine with sidecars. Check the release model: open source edge releases, or a vendor
  distribution for stable releases.
- Istio, ambient mode: you want the widest feature set (fault injection, rich routing,
  egress control, VMs) with no sidecars, and you can start with L4 only.
- Istio, sidecar mode: as above, when you need a feature that ambient mode does not
  support yet, or multi-cluster support at the Stable level.
- Cilium: you already use Cilium as the CNI, or want to, and your L7 needs are modest.
  Check the status of the mTLS features you need: some are still beta.
- Consul: you have many services outside Kubernetes (VMs) and already run Consul.

## 4. Can you afford it?

- [ ] Someone owns the mesh: upgrades, certificates, incidents. Name the person or team.
- [ ] You have measured the latency and memory it adds, on your own traffic.
- [ ] You have a plan for upgrades. In sidecar mode, every Pod restarts to get the new proxy.
- [ ] You know where the trust anchor lives and when it expires.
- [ ] On-call engineers can tell a 503 from the proxy from a 503 from the app.

## 5. Roll it out in steps

1. Install it in a test cluster and mesh one namespace. Watch the metrics only.
2. Mesh more namespaces with mTLS in permissive mode (plain text still allowed).
3. Check that every caller of a service is meshed, then switch that namespace to strict.
4. Add authorization policies, starting with "deny nothing, log everything" where the
   mesh supports an audit mode.
5. Only now add traffic policies: retries, timeouts, canaries, fault injection tests.
