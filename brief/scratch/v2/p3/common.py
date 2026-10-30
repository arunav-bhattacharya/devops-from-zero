"""Shared helpers for the Part 3 lesson modules.

Console blocks come from real runs saved in out/*.json (see cap.py and dNN*.py),
or from the first edition (content/v1/p2.json), which was tested on this machine.
"""
import json
import pathlib

from cap import load

ROOT = pathlib.Path(__file__).resolve().parents[4]
V1 = json.loads((ROOT / "content/v1/p2.json").read_text())
LAB = ROOT / "labs/hello-devops"


def v1_step(lesson_id, idx):
    """The code of one worked step from the first edition."""
    L = next(x for x in V1["lessons"] if x["id"] == lesson_id)
    return L["worked"]["steps"][idx]["code"]


def lab(path):
    return (LAB / path).read_text().rstrip("\n")


def cap(name, key):
    return load(name)[key]


def lines(block, keep):
    """Keep selected lines (list of indexes or a slice) of a console block."""
    ls = block.split("\n")
    if isinstance(keep, slice):
        return "\n".join(ls[keep])
    return "\n".join(ls[i] for i in keep)


def join(*blocks):
    return "\n".join(b for b in blocks if b)


def step(say, code=None, lang="console"):
    d = {"say": say}
    if code:
        d["code"] = code
        d["lang"] = lang
    return d


# Links checked in this task (docker/docs repo at 6a5bbde, github/docs, search results).
DOCS = "https://docs.docker.com"
L = {
    # videos (YouTube URLs from WebSearch results in this task)
    "nana_crash": ("Docker crash course for absolute beginners (TechWorld with Nana)", "https://www.youtube.com/watch?v=pg19Z8LL06w", "watch"),
    "nana_full": ("Docker tutorial for beginners, full course in 3 hours (TechWorld with Nana)", "https://www.youtube.com/watch?v=3c-iBn73dDE", "watch"),
    "nana_compose": ("Ultimate Docker Compose tutorial (TechWorld with Nana)", "https://www.youtube.com/watch?v=SXwC9fSwct8", "watch"),
    "fireship": ("Learn Docker in 7 easy steps (Fireship)", "https://www.youtube.com/watch?v=gAkwW2tuIqE", "watch"),
    "networkchuck": ("Docker networking is crazy, all network types explained (NetworkChuck)", "https://www.youtube.com/watch?v=bKFMS5C4CG0", "watch"),
    "images_deep": ("Docker images explained: layers, tags and security (YouTube deep dive)", "https://www.youtube.com/watch?v=CjyJYopE890", "watch"),
    "bret_prod": ("Docker production best practices, DockerCon 2017 talk (Bret Fisher)", "https://www.youtube.com/watch?v=V4f_sHTzvCI", "watch"),
    # reading
    "jvns_container": ("Julia Evans: what even is a container?", "https://jvns.ca/blog/2016/10/10/what-even-is-a-container/", "read"),
    "jvns_zine": ("Julia Evans: How Containers Work (zine)", "https://jvns.ca/blog/2020/04/27/new-zine-how-containers-work/", "read"),
    "twelve": ("The Twelve-Factor App: III. Config", "https://12factor.net/config", "read"),
    "dive": ("dive: a tool for exploring image layers (GitHub)", "https://github.com/wagoodman/dive", "read"),
    "trivy": ("Trivy: first steps", "https://trivy.dev/latest/getting-started", "docs"),
    "gh_ghcr": ("GitHub Docs: Working with the Container registry", "https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-container-registry", "docs"),
    "gh_vis": ("GitHub Docs: A package's access control and visibility", "https://docs.github.com/en/packages/learn-github-packages/configuring-a-packages-access-control-and-visibility", "docs"),
    # Docker docs (source files checked in the docker/docs repo)
    "c_container": ("Docker concepts: What is a container?", DOCS + "/get-started/docker-concepts/the-basics/what-is-a-container/", "docs"),
    "c_image": ("Docker concepts: What is an image?", DOCS + "/get-started/docker-concepts/the-basics/what-is-an-image/", "docs"),
    "c_registry": ("Docker concepts: What is a registry?", DOCS + "/get-started/docker-concepts/the-basics/what-is-a-registry/", "docs"),
    "c_layers": ("Docker concepts: Understanding the image layers", DOCS + "/get-started/docker-concepts/building-images/understanding-image-layers/", "docs"),
    "c_dockerfile": ("Docker concepts: Writing a Dockerfile", DOCS + "/get-started/docker-concepts/building-images/writing-a-dockerfile/", "docs"),
    "c_cache": ("Docker concepts: Using the build cache", DOCS + "/get-started/docker-concepts/building-images/using-the-build-cache/", "docs"),
    "c_ports": ("Docker concepts: Publishing and exposing ports", DOCS + "/get-started/docker-concepts/running-containers/publishing-ports/", "docs"),
    "c_persist": ("Docker concepts: Persisting container data", DOCS + "/get-started/docker-concepts/running-containers/persisting-container-data/", "docs"),
    "c_multistage": ("Docker concepts: Multi-stage builds", DOCS + "/get-started/docker-concepts/building-images/multi-stage-builds/", "docs"),
    "restart": ("Start containers automatically (restart policies)", DOCS + "/engine/containers/start-containers-automatically/", "docs"),
    "ref_run": ("docker container run reference", DOCS + "/reference/cli/docker/container/run/", "docs"),
    "ref_exec": ("docker container exec reference", DOCS + "/reference/cli/docker/container/exec/", "docs"),
    "ref_stop": ("docker container stop reference", DOCS + "/reference/cli/docker/container/stop/", "docs"),
    "mac_install": ("Install Docker Desktop on Mac", DOCS + "/desktop/setup/install/mac-install/", "docs"),
    "pulls": ("Docker Hub usage and pull limits", DOCS + "/docker-hub/usage/pulls/", "docs"),
    "port_pub": ("Port publishing and mapping", DOCS + "/engine/network/port-publishing/", "docs"),
    "drivers": ("Storage drivers: images, layers and the container layer", DOCS + "/engine/storage/drivers/", "docs"),
    "overlay": ("OverlayFS storage driver", DOCS + "/engine/storage/drivers/overlayfs-driver/", "docs"),
    "containerd": ("containerd image store with Docker Engine", DOCS + "/engine/storage/containerd/", "docs"),
    "multiplat": ("Multi-platform builds", DOCS + "/build/building/multi-platform/", "docs"),
    "imagetools": ("docker buildx imagetools inspect reference", DOCS + "/reference/cli/docker/buildx/imagetools/inspect/", "docs"),
    "ref_history": ("docker image history reference", DOCS + "/reference/cli/docker/image/history/", "docs"),
    "ref_diff": ("docker container diff reference", DOCS + "/reference/cli/docker/container/diff/", "docs"),
    "ref_imagels": ("docker image ls reference", DOCS + "/reference/cli/docker/image/ls/", "docs"),
    "dhi": ("Docker Hardened Images", DOCS + "/dhi/", "docs"),
    "dhi_start": ("Docker Hardened Images quickstart", DOCS + "/dhi/get-started/", "docs"),
    "dhi_use": ("Use a Docker Hardened Image", DOCS + "/dhi/how-to/use/", "docs"),
    "dockerfile": ("Dockerfile reference", DOCS + "/reference/dockerfile/", "docs"),
    "context": ("Build context", DOCS + "/build/concepts/context/", "docs"),
    "cache_inval": ("Build cache invalidation", DOCS + "/build/cache/invalidation/", "docs"),
    "cache_opt": ("Optimize cache usage in builds", DOCS + "/build/cache/optimize/", "docs"),
    "variables": ("Build variables (ARG and ENV)", DOCS + "/build/building/variables/", "docs"),
    "checks": ("Checking your build configuration (build checks)", DOCS + "/build/checks/", "docs"),
    "json_args": ("Build check: JSONArgsRecommended", DOCS + "/reference/build-checks/json-args-recommended/", "docs"),
    "init": ("docker init reference", DOCS + "/reference/cli/docker/init/", "docs"),
    "best": ("Building best practices", DOCS + "/build/building/best-practices/", "docs"),
    "storage": ("Storage overview", DOCS + "/engine/storage/", "docs"),
    "volumes": ("Volumes", DOCS + "/engine/storage/volumes/", "docs"),
    "bind": ("Bind mounts", DOCS + "/engine/storage/bind-mounts/", "docs"),
    "tmpfs": ("tmpfs mounts", DOCS + "/engine/storage/tmpfs/", "docs"),
    "network": ("Networking overview", DOCS + "/engine/network/", "docs"),
    "bridge": ("Bridge network driver", DOCS + "/engine/network/drivers/bridge/", "docs"),
    "desktop_net": ("Docker Desktop networking how-tos", DOCS + "/desktop/features/networking/networking-how-tos/", "docs"),
    "host": ("Host network driver", DOCS + "/engine/network/drivers/host/", "docs"),
    "none": ("None network driver", DOCS + "/engine/network/drivers/none/", "docs"),
    "compose_model": ("How Compose works", DOCS + "/compose/intro/compose-application-model/", "docs"),
    "compose_history": ("Compose history and versions", DOCS + "/compose/intro/history/", "docs"),
    "compose_services": ("Compose file reference: services", DOCS + "/reference/compose-file/services/", "docs"),
    "compose_net": ("Networking in Compose", DOCS + "/compose/how-tos/networking/", "docs"),
    "startup": ("Control startup and shutdown order in Compose", DOCS + "/compose/how-tos/startup-order/", "docs"),
    "interp": ("Variable interpolation in Compose", DOCS + "/compose/how-tos/environment-variables/variable-interpolation/", "docs"),
    "precedence": ("Environment variables precedence in Compose", DOCS + "/compose/how-tos/environment-variables/envvars-precedence/", "docs"),
    "merge": ("Merge Compose files", DOCS + "/compose/how-tos/multiple-compose-files/merge/", "docs"),
    "profiles": ("Using profiles with Compose", DOCS + "/compose/how-tos/profiles/", "docs"),
    "watch": ("Use Compose Watch", DOCS + "/compose/how-tos/file-watch/", "docs"),
    "compose_prod": ("Use Compose in production", DOCS + "/compose/how-tos/production/", "docs"),
    "ref_compose_config": ("docker compose config reference", DOCS + "/reference/cli/docker/compose/config/", "docs"),
    "ref_compose_up": ("docker compose up reference", DOCS + "/reference/cli/docker/compose/up/", "docs"),
    "multistage": ("Multi-stage builds", DOCS + "/build/building/multi-stage/", "docs"),
    "secrets": ("Build secrets", DOCS + "/build/building/secrets/", "docs"),
    "attest": ("Build attestations", DOCS + "/build/metadata/attestations/", "docs"),
    "scout_install": ("Install Docker Scout", DOCS + "/scout/install/", "docs"),
    "debug": ("docker debug reference", DOCS + "/reference/cli/docker/debug/", "docs"),
}


def ref(*keys):
    return [{"title": L[k][0], "url": L[k][1], "kind": L[k][2]} for k in keys]


def src(*keys):
    return [{"title": L[k][0], "url": L[k][1]} for k in keys]
