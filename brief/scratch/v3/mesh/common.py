"""Shared helpers and confirmed links for Part 15."""
import pathlib

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[3]
LAB = ROOT / "labs" / "hello-devops" / "mesh"


def lab(path):
    return (LAB / path).read_text().rstrip("\n")


def R(title, url, kind):
    return {"title": title, "url": url, "kind": kind}


def S(title, url):
    return {"title": title, "url": url}


# Envoy docs (source files confirmed in envoyproxy/envoy docs/root; URL pattern confirmed by search)
ENVOY = "https://www.envoyproxy.io/docs/envoy/latest/"
E_WHAT = R("What is Envoy", ENVOY + "intro/what_is_envoy", "docs")
E_LIFE = R("Envoy: life of a request", ENVOY + "intro/life_of_a_request", "docs")
E_OUTLIER = R("Envoy: outlier detection", ENVOY + "intro/arch_overview/upstream/outlier", "docs")
E_CB = R("Envoy: circuit breaking", ENVOY + "intro/arch_overview/upstream/circuit_breaking", "docs")
E_HC = R("Envoy: health checking", ENVOY + "intro/arch_overview/upstream/health_checking", "docs")
E_ROUTING = R("Envoy: HTTP routing, retries and timeouts", ENVOY + "intro/arch_overview/http/http_routing", "docs")
E_XDS = R("Envoy: xDS REST and gRPC protocol", ENVOY + "api-docs/xds_protocol", "docs")
E_DYN = R("Envoy: dynamic configuration", ENVOY + "intro/arch_overview/operations/dynamic_configuration", "docs")
E_ADMIN = R("Envoy: the administration interface", ENVOY + "operations/admin", "docs")
E_FAULT = R("Envoy: fault injection filter", ENVOY + "configuration/http/http_filters/fault_filter", "docs")
E_FLAGS = R("Envoy: access log format and response flags", ENVOY + "configuration/advanced/substitution_formatter", "docs")

# Kubernetes and AWS
K_SIDECAR = R("Kubernetes: sidecar containers", "https://kubernetes.io/docs/concepts/workloads/pods/sidecar-containers/", "docs")
APPMESH = R("What is AWS App Mesh? (end-of-support notice)", "https://docs.aws.amazon.com/app-mesh/latest/userguide/what-is-app-mesh.html", "docs")
CONSUL = R("Consul: service mesh on Kubernetes", "https://developer.hashicorp.com/consul/docs/k8s/connect", "docs")

# Istio docs (source files confirmed in istio/istio.io release-1.31; URL pattern confirmed by search)
ISTIO = "https://istio.io/latest/"
I_AMBIENT = R("Istio: ambient mode overview", ISTIO + "docs/ambient/overview/", "docs")
I_MODES = R("Istio: sidecar or ambient?", ISTIO + "docs/overview/dataplane-modes/", "docs")
I_131 = R("Announcing Istio 1.31", ISTIO + "news/releases/1.31.x/announcing-1.31/", "read")
I_PROFILES = R("Istio: installation configuration profiles", ISTIO + "docs/setup/additional-setup/config-profiles/", "docs")
I_AMB_START = R("Istio: getting started with ambient mode", ISTIO + "docs/ambient/getting-started/", "docs")
I_KIND = R("Istio: platform setup for kind", ISTIO + "docs/setup/platform-setup/kind/", "docs")
I_GWAPI = R("Istio: the Kubernetes Gateway API", ISTIO + "docs/tasks/traffic-management/ingress/gateway-api/", "docs")
I_VS = R("Istio reference: VirtualService", ISTIO + "docs/reference/config/networking/virtual-service/", "docs")
I_DR = R("Istio reference: DestinationRule", ISTIO + "docs/reference/config/networking/destination-rule/", "docs")
I_FAULT = R("Istio task: fault injection", ISTIO + "docs/tasks/traffic-management/fault-injection/", "docs")
I_CB = R("Istio task: circuit breaking", ISTIO + "docs/tasks/traffic-management/circuit-breaking/", "docs")
I_SEC = R("Istio: security concepts", ISTIO + "docs/concepts/security/", "docs")
I_MTLS = R("Istio task: mutual TLS migration", ISTIO + "docs/tasks/security/authentication/mtls-migration/", "docs")
I_AUTHZ = R("Istio reference: AuthorizationPolicy", ISTIO + "docs/reference/config/security/authorization-policy/", "docs")
I_L7 = R("Istio: Layer 7 features in ambient mode", ISTIO + "docs/ambient/usage/l7-features/", "docs")
I_ANALYZE = R("Istio: diagnose your configuration with istioctl analyze", ISTIO + "docs/ops/diagnostic-tools/istioctl-analyze/", "docs")
I_PROXYCMD = R("Istio: debugging Envoy and istiod", ISTIO + "docs/ops/diagnostic-tools/proxy-cmd/", "docs")
I_TRACING = R("Istio: distributed tracing overview", ISTIO + "docs/tasks/observability/distributed-tracing/overview/", "docs")
I_KIALI = R("Istio: Kiali", ISTIO + "docs/ops/integrations/kiali/", "docs")
I_DATAPLANE = R("Istio: ambient data plane", ISTIO + "docs/ambient/architecture/data-plane/", "docs")
I_WAYPOINT = R("Istio: configure waypoint proxies", ISTIO + "docs/ambient/usage/waypoint/", "docs")

# Linkerd docs (source files confirmed in linkerd/website; URLs confirmed by search)
L_START = R("Linkerd: getting started", "https://linkerd.io/2-edge/getting-started/", "docs")
L_ARCH = R("Linkerd: architecture", "https://linkerd.io/2-edge/reference/architecture/", "docs")
L_MTLS = R("Linkerd: automatic mTLS", "https://linkerd.io/2-edge/features/automatic-mtls/", "docs")
L_RELEASES = R("Linkerd: releases and versions", "https://linkerd.io/releases/", "docs")
L_SHIFT = R("Linkerd: traffic shifting", "https://linkerd.io/2-edge/tasks/traffic-shifting/", "docs")
L_VALIDATE = R("Linkerd: validating your mTLS traffic", "https://linkerd.io/2-edge/tasks/validating-your-traffic/", "docs")
L_WHAT = R("Linkerd: what is a service mesh?", "https://linkerd.io/what-is-a-service-mesh/", "read")
BEL_FAQ = R("Buoyant Enterprise for Linkerd: FAQ", "https://docs.buoyant.io/buoyant-enterprise-linkerd/latest/faq", "docs")
BEL_LICENSE = R("How Linkerd licensing actually works (Buoyant)", "https://www.buoyant.io/articles/how-linkerd-licensing-actually-works-apache-2-0-edge-releases-and-what-bel-pays-for", "read")

# Cilium docs (URLs confirmed by search)
C_MESH = R("Cilium: service mesh", "https://docs.cilium.io/en/stable/network/servicemesh/", "docs")
C_GAMMA = R("Cilium: GAMMA support", "https://docs.cilium.io/en/stable/network/servicemesh/gateway-api/gamma/", "docs")
C_HUBBLE = R("Cilium: network observability with Hubble", "https://docs.cilium.io/en/stable/observability/hubble/", "docs")
C_ZTUNNEL = R("Cilium: ztunnel transparent encryption (Beta)", "https://docs.cilium.io/en/latest/security/network/encryption-ztunnel/", "docs")
C_MUTUAL = R("Cilium: mutual authentication (Beta)", "https://docs.cilium.io/en/stable/network/servicemesh/mutual-authentication/mutual-authentication/", "docs")

# Gateway API (URLs confirmed by search)
G_MESH = R("Gateway API for service mesh (GAMMA)", "https://gateway-api.sigs.k8s.io/docs/mesh/mesh-overview/", "docs")
G_FACETS = R("Gateway API: the different facets of a Service", "https://gateway-api.sigs.k8s.io/docs/mesh/service-facets/", "docs")

# Videos (URLs from WebSearch results on youtube.com)
V_NANA = R("Istio and service mesh, simply explained in 15 minutes (TechWorld with Nana)", "https://www.youtube.com/watch?v=16fgzklcF7Y", "watch")
V_XDS = R("It's proxies all the way down: Envoy/xDS 101 (Jacob Taylor, Everything Open 2025)", "https://www.youtube.com/watch?v=kDtcVB53U7o", "watch")
V_AMBIENT = R("Workshop: getting started with ambient mesh (Christian Posta and Jim Barton)", "https://www.youtube.com/watch?v=SyjBSM-3dOY", "watch")
V_ECHO27 = R("eCHO episode 27: eBPF-enabled service mesh (Liz Rice and Thomas Graf)", "https://www.youtube.com/watch?v=nJT0ASbGLvs", "watch")
V_CILIUM_MESH = R("What is Cilium service mesh? Interview with Thomas Graf (eCHO livestream)", "https://www.youtube.com/watch?v=lZskwr3uXn8", "watch")
V_LINKERD = R("Webinar: introduction to Linkerd", "https://www.youtube.com/watch?v=0xYSy6OmjUM", "watch")
V_GAMMA = R("Simplifying Gateway API integration for service meshes through the GAMMA initiative", "https://www.youtube.com/watch?v=T4llZKfoo7w", "watch")
