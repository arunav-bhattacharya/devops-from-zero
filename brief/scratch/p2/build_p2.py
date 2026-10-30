#!/usr/bin/env python3
"""Builds content/p2.json (Part 2: Docker). Run: python3 brief/scratch/p2/build_p2.py"""
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[3]
LAB = ROOT / "labs/hello-devops"
HERE = pathlib.Path(__file__).resolve().parent
OUT = ROOT / "content/p2.json"

# Lab files are read from disk so this part always matches the tested lab.
LAB_DOCKERFILE = (LAB / "Dockerfile").read_text().rstrip("\n")
LAB_DOCKERIGNORE = (LAB / ".dockerignore").read_text().rstrip("\n")
LAB_COMPOSE = (LAB / "compose.yaml").read_text().rstrip("\n")
# The Day 6 single-stage Dockerfile and the Day 5 helper were built and run in the sandbox.
SINGLE_DOCKERFILE = (HERE / "build/Dockerfile").read_text().rstrip("\n")
CHECK_SCRIPT = (HERE / "files/check-docker.sh").read_text().rstrip("\n")


def ref(title, url, kind="docs"):
    return {"title": title, "url": url, "kind": kind}


# ---- links (each one confirmed in this task by search results) ----
R = {
    "getstarted": ref("Docker: Get started", "https://docs.docker.com/get-started"),
    "nana_crash": ref("TechWorld with Nana: Docker crash course for absolute beginners", "https://www.youtube.com/watch?v=pg19Z8LL06w", "watch"),
    "nana_compose": ref("TechWorld with Nana: Ultimate Docker Compose tutorial", "https://www.youtube.com/watch?v=SXwC9fSwct8", "watch"),
    "jvns_container": ref("Julia Evans: What even is a container?", "https://jvns.ca/blog/2016/10/10/what-even-is-a-container/", "read"),
    "jvns_zine": ref("Julia Evans: How Containers Work (zine)", "https://wizardzines.com/zines/containers/", "read"),
    "pulls": ref("Docker Hub pull usage and limits", "https://docs.docker.com/docker-hub/usage/pulls/"),
    "running": ref("Running containers", "https://docs.docker.com/engine/containers/run/"),
    "run_ref": ref("docker container run reference", "https://docs.docker.com/reference/cli/docker/container/run/"),
    "exec_ref": ref("docker container exec reference", "https://docs.docker.com/reference/cli/docker/container/exec/"),
    "ports_concept": ref("Publishing and exposing ports", "https://docs.docker.com/get-started/docker-concepts/running-containers/publishing-ports/"),
    "port_publishing": ref("Port publishing and mapping", "https://docs.docker.com/engine/network/port-publishing/"),
    "mac_install": ref("Install Docker Desktop on Mac", "https://docs.docker.com/desktop/setup/install/mac-install/"),
    "vmm": ref("Virtual Machine Manager for Docker Desktop on Mac", "https://docs.docker.com/desktop/vmm"),
    "writing_df": ref("Writing a Dockerfile", "https://docs.docker.com/get-started/docker-concepts/building-images/writing-a-dockerfile/"),
    "df_overview": ref("Dockerfile overview", "https://docs.docker.com/build/concepts/dockerfile/"),
    "df_ref": ref("Dockerfile reference", "https://docs.docker.com/reference/dockerfile/"),
    "build_vars": ref("Build variables (ARG and ENV)", "https://docs.docker.com/build/building/variables/"),
    "cache_concept": ref("Using the build cache", "https://docs.docker.com/get-started/docker-concepts/building-images/using-the-build-cache/"),
    "cache_opt": ref("Optimize cache usage in builds", "https://docs.docker.com/build/cache/optimize/"),
    "context": ref("Build context", "https://docs.docker.com/build/concepts/context/"),
    "best": ref("Building best practices", "https://docs.docker.com/build/building/best-practices/"),
    "twelve": ref("The Twelve-Factor App: III. Config", "https://12factor.net/config", "read"),
    "volumes": ref("Volumes", "https://docs.docker.com/engine/storage/volumes/"),
    "net_overview": ref("Networking overview", "https://docs.docker.com/engine/network/"),
    "bridge": ref("Bridge network driver", "https://docs.docker.com/engine/network/drivers/bridge/"),
    "compose_model": ref("How Compose works", "https://docs.docker.com/compose/intro/compose-application-model/"),
    "compose_services": ref("Define services in Docker Compose", "https://docs.docker.com/reference/compose-file/services/"),
    "startup": ref("Control startup and shutdown order in Compose", "https://docs.docker.com/compose/how-tos/startup-order/"),
    "compose_quick": ref("Docker Compose quickstart", "https://docs.docker.com/compose/gettingstarted/"),
    "interp": ref("Variable interpolation in Compose (.env files)", "https://docs.docker.com/compose/how-tos/environment-variables/variable-interpolation/"),
    "precedence": ref("Environment variables precedence in Compose", "https://docs.docker.com/compose/how-tos/environment-variables/envvars-precedence/"),
    "compose_config": ref("docker compose config reference", "https://docs.docker.com/reference/cli/docker/compose/config/"),
    "multistage": ref("Multi-stage builds", "https://docs.docker.com/build/building/multi-stage/"),
    "dhi": ref("Docker Hardened Images", "https://docs.docker.com/dhi/"),
    "dhi_blog": ref("Docker blog: Hardened Images for everyone", "https://www.docker.com/blog/docker-hardened-images-for-every-developer/", "read"),
    "scout_install": ref("Install Docker Scout", "https://docs.docker.com/scout/install/"),
    "scout_qv": ref("docker scout quickview reference", "https://docs.docker.com/reference/cli/docker/scout/quickview/"),
    "trivy_start": ref("Trivy: first steps", "https://trivy.dev/docs/latest/getting-started/"),
    "ghcr": ref("GitHub Docs: Working with the Container registry", "https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-container-registry"),
    "ghcr_access": ref("GitHub Docs: A package's access control and visibility", "https://docs.github.com/en/packages/learn-github-packages/configuring-a-packages-access-control-and-visibility"),
    "multiplatform": ref("Multi-platform builds", "https://docs.docker.com/build/building/multi-platform/"),
    "secrets": ref("Build secrets", "https://docs.docker.com/build/building/secrets/"),
}


def src(*keys):
    return [{"title": R[k]["title"], "url": R[k]["url"]} for k in keys]


# ------------------------------------------------------------------ diagrams
SVG_D05 = (
    '<svg viewBox="0 0 560 210" xmlns="http://www.w3.org/2000/svg" role="img" '
    'aria-label="docker run pulls an image from Docker Hub, starts a container, and a port map connects localhost:8080 to container port 80">'
    '<rect class="bxp" x="8" y="30" width="140" height="46" rx="10"/>'
    '<text class="tk" x="78" y="58" font-size="13" text-anchor="middle">Docker Hub</text>'
    '<rect class="bxg" x="210" y="30" width="120" height="46" rx="10"/>'
    '<text class="tk" x="270" y="58" font-size="13" text-anchor="middle">Image</text>'
    '<rect class="bxt" x="396" y="30" width="156" height="46" rx="10"/>'
    '<text class="tk" x="474" y="58" font-size="13" text-anchor="middle">Container</text>'
    '<line class="ln" x1="148" y1="53" x2="206" y2="53" marker-end="url(#ar)"/>'
    '<text class="ts" x="178" y="44" font-size="11" text-anchor="middle">pull</text>'
    '<line class="ln" x1="330" y1="53" x2="392" y2="53" marker-end="url(#ar)"/>'
    '<text class="ts" x="362" y="44" font-size="11" text-anchor="middle">run</text>'
    '<rect class="bx" x="8" y="150" width="168" height="46" rx="10"/>'
    '<text class="t" x="92" y="178" font-size="13" text-anchor="middle">localhost:8080</text>'
    '<rect class="bxo" x="228" y="150" width="132" height="46" rx="10"/>'
    '<text class="tk" x="294" y="178" font-size="13" text-anchor="middle">-p 8080:80</text>'
    '<line class="ln" x1="176" y1="173" x2="224" y2="173" marker-end="url(#ar)"/>'
    '<text class="ts" x="200" y="164" font-size="11" text-anchor="middle">curl</text>'
    '<line class="ln" x1="360" y1="173" x2="474" y2="173"/>'
    '<line class="ln" x1="474" y1="173" x2="474" y2="80" marker-end="url(#ar)"/>'
    '<text class="ts" x="484" y="130" font-size="11" text-anchor="start">port 80</text>'
    '</svg>'
)

SVG_D06 = (
    '<svg viewBox="0 0 560 250" xmlns="http://www.w3.org/2000/svg" role="img" '
    'aria-label="Image layers stacked from FROM at the bottom to COPY app.py at the top; only the top layer is rebuilt after a code edit">'
    '<rect class="bxo" x="150" y="16" width="260" height="34" rx="10"/>'
    '<text class="tk" x="280" y="38" font-size="13" text-anchor="middle">COPY app.py</text>'
    '<rect class="bxt" x="150" y="62" width="260" height="34" rx="10"/>'
    '<text class="tk" x="280" y="84" font-size="13" text-anchor="middle">RUN pip install</text>'
    '<rect class="bxt" x="150" y="108" width="260" height="34" rx="10"/>'
    '<text class="tk" x="280" y="130" font-size="13" text-anchor="middle">COPY requirements.txt</text>'
    '<rect class="bxt" x="150" y="154" width="260" height="34" rx="10"/>'
    '<text class="tk" x="280" y="176" font-size="13" text-anchor="middle">WORKDIR /app</text>'
    '<rect class="bxp" x="150" y="200" width="260" height="34" rx="10"/>'
    '<text class="tk" x="280" y="222" font-size="13" text-anchor="middle">FROM python:3.14-slim</text>'
    '<text class="ts" x="424" y="37" font-size="11" text-anchor="start">rebuilt</text>'
    '<text class="ts" x="424" y="83" font-size="11" text-anchor="start">cached</text>'
    '<text class="ts" x="424" y="129" font-size="11" text-anchor="start">cached</text>'
    '<text class="ts" x="424" y="175" font-size="11" text-anchor="start">cached</text>'
    '<text class="ts" x="424" y="221" font-size="11" text-anchor="start">base image</text>'
    '<line class="ln" x1="120" y1="232" x2="120" y2="22" marker-end="url(#ar)"/>'
    '<text class="ts" x="64" y="130" font-size="11" text-anchor="middle">build order</text>'
    '</svg>'
)

SVG_D07 = (
    '<svg viewBox="0 0 560 220" xmlns="http://www.w3.org/2000/svg" role="img" '
    'aria-label="localhost:8000 goes to the web container, which reaches the redis container by name on one network; redis stores data in the redis-data volume">'
    '<line class="lnd" x1="196" y1="24" x2="508" y2="24"/>'
    '<line class="lnd" x1="196" y1="132" x2="508" y2="132"/>'
    '<line class="lnd" x1="196" y1="24" x2="196" y2="132"/>'
    '<line class="lnd" x1="508" y1="24" x2="508" y2="132"/>'
    '<rect class="bx" x="8" y="40" width="144" height="46" rx="10"/>'
    '<text class="t" x="80" y="68" font-size="13" text-anchor="middle">localhost:8000</text>'
    '<rect class="bxt" x="212" y="40" width="100" height="46" rx="10"/>'
    '<text class="tk" x="262" y="68" font-size="13" text-anchor="middle">web</text>'
    '<rect class="bxo" x="392" y="40" width="100" height="46" rx="10"/>'
    '<text class="tk" x="442" y="68" font-size="13" text-anchor="middle">redis</text>'
    '<line class="ln" x1="152" y1="63" x2="208" y2="63" marker-end="url(#ar)"/>'
    '<text class="ts" x="174" y="54" font-size="11" text-anchor="middle">8000</text>'
    '<line class="ln" x1="312" y1="63" x2="388" y2="63" marker-end="url(#ar)"/>'
    '<text class="ts" x="350" y="54" font-size="11" text-anchor="middle">redis:6379</text>'
    '<text class="ts" x="352" y="120" font-size="11" text-anchor="middle">project network</text>'
    '<rect class="bxg" x="382" y="164" width="120" height="46" rx="10"/>'
    '<text class="tk" x="442" y="192" font-size="13" text-anchor="middle">redis-data</text>'
    '<line class="ln" x1="442" y1="86" x2="442" y2="160" marker-end="url(#ar)"/>'
    '<text class="ts" x="452" y="150" font-size="11" text-anchor="start">/data</text>'
    '</svg>'
)

SVG_D08 = (
    '<svg viewBox="0 0 560 200" xmlns="http://www.w3.org/2000/svg" role="img" '
    'aria-label="The build stage installs packages, the run stage copies the venv and runs as a normal user, then the image is pushed to a registry for amd64 and arm64">'
    '<rect class="bxp" x="8" y="30" width="140" height="46" rx="10"/>'
    '<text class="tk" x="78" y="58" font-size="13" text-anchor="middle">Build stage</text>'
    '<rect class="bxt" x="208" y="30" width="140" height="46" rx="10"/>'
    '<text class="tk" x="278" y="58" font-size="13" text-anchor="middle">Run stage</text>'
    '<rect class="bxg" x="400" y="30" width="152" height="46" rx="10"/>'
    '<text class="tk" x="476" y="58" font-size="13" text-anchor="middle">Registry</text>'
    '<line class="ln" x1="148" y1="53" x2="204" y2="53" marker-end="url(#ar)"/>'
    '<text class="ts" x="176" y="44" font-size="11" text-anchor="middle">/venv</text>'
    '<line class="ln" x1="348" y1="53" x2="396" y2="53" marker-end="url(#ar)"/>'
    '<text class="ts" x="372" y="44" font-size="11" text-anchor="middle">push</text>'
    '<text class="ts" x="78" y="96" font-size="11" text-anchor="middle">installs packages</text>'
    '<text class="ts" x="78" y="114" font-size="11" text-anchor="middle">not shipped</text>'
    '<text class="ts" x="278" y="96" font-size="11" text-anchor="middle">venv + app.py</text>'
    '<text class="ts" x="278" y="114" font-size="11" text-anchor="middle">uid 10001</text>'
    '<line class="ln" x1="435" y1="76" x2="435" y2="146" marker-end="url(#ar)"/>'
    '<line class="ln" x1="517" y1="76" x2="517" y2="146" marker-end="url(#ar)"/>'
    '<rect class="bx" x="400" y="150" width="70" height="40" rx="10"/>'
    '<text class="t" x="435" y="175" font-size="13" text-anchor="middle">amd64</text>'
    '<rect class="bx" x="482" y="150" width="70" height="40" rx="10"/>'
    '<text class="t" x="517" y="175" font-size="13" text-anchor="middle">arm64</text>'
    '</svg>'
)

# ================================================================== d05
D05 = {
    "id": "d05",
    "title": "Containers: your first docker run",
    "minutes": 35,
    "goal": "By the end you can explain what a container is, and run, inspect, stop and remove containers made from public images.",
    "guess": {
        "q": "You run `docker run -p 8080:80 nginx` on your Mac. Which kernel runs the nginx process?",
        "options": [
            "Its own Debian kernel, booted inside the container",
            "The macOS kernel, directly",
            "The Linux kernel of a small VM that Docker Desktop runs",
            "No kernel: Docker interprets the image like a JVM",
        ],
        "answer": 2,
        "why": "Containers never boot their own kernel; they share the host's Linux kernel. A Mac has no Linux kernel, so Docker Desktop runs one small Linux VM and every container shares its kernel.",
    },
    "terms": [
        {"term": "Image", "plain": "A read-only package of an app and everything it needs to run: files, libraries and settings."},
        {"term": "Container", "plain": "A running, isolated process started from an image."},
        {"term": "Registry", "plain": "A server that stores images so people and machines can pull them; Docker Hub is the default one."},
        {"term": "Tag", "plain": "The version label after the colon in an image name, such as the 8-alpine in redis:8-alpine."},
        {"term": "Port mapping", "plain": "A rule that sends traffic from a port on your computer to a port inside a container."},
        {"term": "Kernel", "plain": "The core of an operating system: it runs processes and talks to the hardware."},
    ],
    "sections": [
        {
            "h": "The problem: it works on my machine",
            "body": (
                "Your app never runs alone. It also needs:\n\n"
                "- a language runtime, such as Python 3.14\n"
                "- libraries, such as Flask\n"
                "- system packages from the operating system\n"
                "- settings, such as environment variables\n\n"
                "Your laptop has one mix of these. The CI server has another, and the production server a third. "
                "So code that works for you can break on a server, only because the setup differs.\n\n"
                "Docker solves this by packing the app together with everything it needs. You build that package once. "
                "Then it runs the same way on your Mac, on a CI runner and in the cloud. On the Day 1 map, this is the package step.\n\n"
                "Two words carry this whole part. An **image** is the package: your app, its files and its settings, frozen and read-only. "
                "A **container** is a running copy of an image."
            ),
            "refs": [R["getstarted"], R["nana_crash"]],
        },
        {
            "h": "A container is an isolated process",
            "body": (
                "A virtual machine (VM) pretends to be a whole computer. It has virtual hardware and boots a full operating system with its own kernel. "
                "The kernel is the core of an operating system: it runs processes and talks to the hardware. "
                "A VM takes many seconds to boot and often needs gigabytes of memory.\n\n"
                "A container is much lighter. It is a normal Linux process, started by the Docker Engine (the background service that runs containers). "
                "The host's kernel keeps it apart from other processes with two features:\n\n"
                "- Namespaces give a process its own private view of process IDs, network, hostname and files.\n"
                "- cgroups (control groups) limit how much CPU and memory a process can use.\n\n"
                "There is no second kernel to boot, so a container starts in about a second. "
                "The price is that all containers on a host share one kernel.\n\n"
                "Macs do not have a Linux kernel. So Docker Desktop runs one small Linux VM, and all your containers live inside it. "
                "That is why a container on your Mac reports that it runs Linux."
            ),
            "refs": [R["jvns_container"], R["jvns_zine"], R["mac_install"]],
        },
        {
            "h": "Images, containers and registries",
            "body": (
                "Think of a class and an object in Kotlin. The image is the class: a read-only definition. "
                "The container is an object: a live instance with its own state. "
                "You can start many containers from one image, and they do not affect each other.\n\n"
                "Each container gets a thin writable layer on top of its image. Files the app writes go there. "
                "When you remove the container, that layer and its files are gone. The image stays as it was.\n\n"
                "Images live in a registry, a server that stores and serves them. Docker Hub is the default one. "
                "When you run an image you do not have, Docker pulls (downloads) it first. "
                "Image names look like `name:tag`, for example `redis:8-alpine`. The tag names a version. "
                "If you leave the tag out, Docker uses `latest`.\n\n"
                "Docker Hub limits how many images you can pull without logging in. "
                "Run `docker login` to get a higher limit, and see [Docker Hub pull limits](https://docs.docker.com/docker-hub/usage/pulls/) for the current numbers."
            ),
            "refs": [R["running"], R["pulls"]],
        },
        {
            "h": "Your first docker run, flag by flag",
            "body": (
                "`docker run` creates a container from an image and starts it. "
                "A typical command is `docker run -d --name web -p 8080:80 -e TZ=UTC nginx`. Each flag changes one thing:\n\n"
                "- `-d` (detached) runs it in the background and prints the container ID.\n"
                "- `--name web` names it, so later commands can say `web` instead of an ID.\n"
                "- `-p 8080:80` maps a port on your Mac to a port in the container.\n"
                "- `-e TZ=UTC` sets an environment variable inside the container.\n"
                "- `--rm` deletes the container as soon as it stops, which suits one-off commands.\n\n"
                "Once it runs, `docker ps` lists it and `docker logs web` shows what it printed. "
                "`docker exec web <command>` runs an extra command inside it, which is how you look around. "
                "Anything you type after the image name replaces the image's default command, as in `docker run --rm alpine uname -m`."
            ),
            "refs": [R["run_ref"], R["exec_ref"]],
        },
        {
            "h": "Port mapping, explained",
            "body": (
                "Each container has its own network namespace, so it has its own set of ports. "
                "nginx listens on port 80 inside its container. Nothing on your Mac can reach that port yet.\n\n"
                "`-p 8080:80` builds a bridge. Read it as host first, then container: traffic to port 8080 on your Mac goes to port 80 in the container. "
                "This order trips most people up, so say it out loud the first few times.\n\n"
                "Three rules help:\n\n"
                "- Two containers can both use port 80 inside, because each has its own namespace.\n"
                "- Each port on your Mac can belong to only one container at a time.\n"
                "- The app inside must listen on `0.0.0.0`, or forwarded traffic never reaches it (Day 4).\n\n"
                "By default, Docker publishes the port on all of your Mac's network addresses, so other devices on your network might reach it. "
                "Write `-p 127.0.0.1:8080:80` to keep a port private to your Mac."
            ),
            "refs": [R["ports_concept"], R["port_publishing"]],
        },
        {
            "h": "The container lifecycle, and Apple Silicon",
            "body": (
                "A container moves through a few states:\n\n"
                "1. Created: Docker has set it up but not started it.\n"
                "2. Running: its main process is alive.\n"
                "3. Exited: the main process ended, by itself or because you stopped it.\n"
                "4. Removed: `docker rm` deleted it and its writable layer.\n\n"
                "`docker stop` sends SIGTERM to the main process, waits 10 seconds, then sends SIGKILL. "
                "That is the Day 3 pattern, and Kubernetes uses it too. "
                "An exited container still exists. `docker ps -a` shows it, and `docker start` runs it again with its files intact.\n\n"
                "One note about CPUs. Apple Silicon Macs use arm64 CPUs. Most cloud servers use amd64, also called x86_64. "
                "Many images include a variant for each, and Docker picks the one that matches your machine. "
                "An amd64-only image still runs on your Mac through emulation, but more slowly, and some programs misbehave. "
                "Day 8 shows how to build your own images for both."
            ),
            "refs": [R["running"], R["mac_install"]],
        },
    ],
    "analogy": (
        "An image is like a recipe card that comes with sealed, exact ingredients. "
        "A container is one meal cooked from it: you can cook many meals from one card, and spilling one meal does not change the card. "
        "All the cooks share one kitchen, which is the Linux kernel. "
        "Where it breaks: in a real kitchen the cooks can see each other, but namespaces make each container believe it is alone."
    ),
    "diagram": SVG_D05,
    "diagram_caption": "docker run pulls the image and starts a container; -p connects a port on your Mac to the container.",
    "worked": {
        "title": "Run nginx, look inside, clean up",
        "steps": [
            {
                "say": "Start nginx in the background. Docker does not have the image yet, so it pulls it from Docker Hub first. The last line is the new container's ID.",
                "code": (
                    "$ docker run -d --name web -p 8080:80 nginx\n"
                    "Unable to find image 'nginx:latest' locally\n"
                    "latest: Pulling from library/nginx\n"
                    "a670537bed70: Pull complete\n"
                    "9f604dae09b2: Pull complete\n"
                    "c139fe92686d: Pull complete\n"
                    "Digest: sha256:600f7cd45e27aa13e9304c834ab7c1b0ff39df85ee1dcc5087955455d77bc83b\n"
                    "Status: Downloaded newer image for nginx:latest\n"
                    "8ec7c61914116bbc46869d4cb55fa77dbd2ceac798c7a23dc667b99805802e55"
                ),
                "lang": "console",
            },
            {
                "say": "Check that it runs. Read the PORTS column from left to right: port 8080 on every address of your Mac goes to port 80 in the container.",
                "code": (
                    "$ docker ps\n"
                    "CONTAINER ID   IMAGE     COMMAND                  CREATED        STATUS        PORTS                  NAMES\n"
                    "8ec7c6191411   nginx     \"/docker-entrypoint.…\"   1 second ago   Up 1 second   0.0.0.0:8080->80/tcp   web"
                ),
                "lang": "console",
            },
            {
                "say": "Send a request through the mapped port, then read the logs. nginx writes each request to standard output, and `docker logs` shows that output. The address at the start of the log line will differ on your Mac.",
                "code": (
                    "$ curl -s localhost:8080 | grep title\n"
                    "<title>Welcome to nginx!</title>\n"
                    "$ docker logs web | tail -1\n"
                    "172.17.0.1 - - [30/Oct/2026:03:21:20 +0000] \"GET / HTTP/1.1\" 200 896 \"-\" \"curl/8.5.0\" \"-\""
                ),
                "lang": "console",
            },
            {
                "say": "Run commands inside the running container with `docker exec`. Even on a Mac, the container sees a Linux system, here Debian. The second command shows the files nginx serves.",
                "code": (
                    "$ docker exec web cat /etc/os-release | head -2\n"
                    "PRETTY_NAME=\"Debian GNU/Linux 13 (trixie)\"\n"
                    "NAME=\"Debian GNU/Linux\"\n"
                    "$ docker exec web ls /usr/share/nginx/html\n"
                    "50x.html\n"
                    "index.html"
                ),
                "lang": "console",
            },
            {
                "say": "Stop it, find it in the list of all containers, then remove it. `docker stop` sent SIGTERM, so nginx shut down cleanly and exited with code 0.",
                "code": (
                    "$ docker stop web\n"
                    "web\n"
                    "$ docker ps -a\n"
                    "CONTAINER ID   IMAGE     COMMAND                  CREATED         STATUS                              PORTS     NAMES\n"
                    "8ec7c6191411   nginx     \"/docker-entrypoint.…\"   7 seconds ago   Exited (0) Less than a second ago             web\n"
                    "$ docker rm web\n"
                    "web"
                ),
                "lang": "console",
            },
        ],
    },
    "code": [
        {
            "lang": "bash",
            "title": "check-docker.sh (keep it in ~/code, outside the repo)",
            "src": CHECK_SCRIPT,
            "run": "bash check-docker.sh",
        }
    ],
    "commands": [
        {"cmd": "docker run -d --name web -p 8080:80 nginx", "what": "Start nginx in the background, named web, with Mac port 8080 sent to container port 80."},
        {"cmd": "docker ps", "what": "List running containers."},
        {"cmd": "docker ps -a", "what": "List all containers, including stopped ones."},
        {"cmd": "docker logs -f web", "what": "Show a container's output and keep following it (Ctrl+C to quit)."},
        {"cmd": "docker exec -it web bash", "what": "Open an interactive shell inside a running container (type exit to leave)."},
        {"cmd": "docker stop web", "what": "Stop a container: SIGTERM first, SIGKILL after 10 seconds."},
        {"cmd": "docker start web", "what": "Start a stopped container again, with its files intact."},
        {"cmd": "docker rm web", "what": "Delete a stopped container and its writable layer (add -f to stop and delete at once)."},
        {"cmd": "docker images", "what": "List the images stored on your machine."},
        {"cmd": "docker pull redis:8-alpine", "what": "Download an image without running it."},
        {"cmd": "docker run --rm -e NAME=Ana alpine sh -c 'echo \"Hi $NAME\"'", "what": "Run a one-off command with an env var, then delete the container."},
    ],
    "mistake": (
        "Writing the port mapping backwards, such as `-p 80:8080` for an app that listens on port 80 inside. "
        "The rule is `-p HOST:CONTAINER`: the left number is on your Mac, the right number is where the app listens in the container. "
        "If curl gets no answer, run `docker ps` and read the PORTS column from left to right."
    ),
    "real_world": (
        "Teams use containers so that laptops, CI runners and production all run the same images. "
        "At PayFlow, a fake payments company, a new engineer starts Postgres and Redis with `docker run` on day one instead of installing them by hand. "
        "When a bug appears only in production, engineers pull the exact production image tag and run it locally to reproduce it."
    ),
    "task": {
        "title": "Run Redis and follow a container's life",
        "steps": [
            "Pull `redis:8-alpine` and list your images. Note how big it is.",
            "Start it in the background with the name `cache`. Skip `-p`: you will talk to Redis from inside the container.",
            "Use `docker exec` to run `redis-cli ping`, then store a value with `redis-cli SET color blue` and read it back with `GET`.",
            "Stop the container, start it again with `docker start`, and read the key. Is it still there?",
            "Remove the container, run a new one with the same name, and read the key again.",
            "Start a second nginx on Mac port 8081 with an env var of your choice. Use `docker exec` with `env` to find it inside.",
            "Run `check-docker.sh` from the Files section and note which CPU type your containers use.",
            "Clean up: remove every container you created, then check that `docker ps -a` no longer lists them.",
        ],
        "hints": [
            "`docker exec cache redis-cli GET color` runs one command inside the running container.",
            "A stopped container keeps its files; a removed one does not. Day 7 shows how to keep data on purpose.",
            "If Docker says the name is already in use, remove the old container with `docker rm -f cache` first.",
        ],
        "done_when": "You are done when you can show that the key survives `docker stop` and `docker start`, but is gone after `docker rm` and a new `docker run`.",
    },
    "explain_back": {
        "prompt": "Explain to a teammate what happens when you type `docker run -d -p 8080:80 nginx` on a Mac, in 3 to 4 sentences. Mention the image, the registry, the Linux VM and the port mapping.",
        "answer": (
            "Docker looks for the nginx image on my machine and, if it is missing, pulls it from Docker Hub, the default registry. "
            "It then starts a container, which is an isolated Linux process, inside the small Linux VM that Docker Desktop runs, because containers need a Linux kernel. "
            "The `-d` flag runs it in the background. "
            "The `-p 8080:80` flag sends traffic from port 8080 on my Mac to port 80 inside the container, where nginx listens."
        ),
    },
    "recap": [
        "A container is an isolated Linux process made from an image, and it shares the host's kernel.",
        "Namespaces decide what a process can see; cgroups decide how much CPU and memory it can use.",
        "Image is to container as class is to object: one image, many containers.",
        "`-p HOST:CONTAINER` publishes a container port on your machine.",
        "`docker stop` sends SIGTERM; `docker rm` deletes the container and its changes.",
        "Docker Desktop runs a small arm64 Linux VM on your Mac; many cloud servers are amd64.",
    ],
    "check": [
        {
            "q": "You want two web containers that both listen on port 80 inside. Which way of publishing them works?",
            "options": [
                "`-p 80:80` for both containers",
                "`-p 8080:80` for one, `-p 8081:80` for the other",
                "`-p 80:8080` for one, `-p 80:8081` for the other",
                "No `-p` at all; curl port 80 on localhost",
            ],
            "answer": 1,
            "why": "Each host port belongs to one container, while both containers can use port 80 inside their own network namespace.",
        },
        {
            "q": "A teammate edits a config file inside a running container with `docker exec`, then runs `docker rm` and a fresh `docker run` from the same image. Where is the edit?",
            "options": [
                "In the image, because exec writes to the image",
                "On Docker Hub, because Docker syncs changes",
                "Still there, because containers share files",
                "Gone, because it lived in the removed container",
            ],
            "answer": 3,
            "why": "Changes go to the container's writable layer, which `docker rm` deletes; the image never changes.",
        },
        {
            "q": "On an Apple Silicon Mac, what does `docker run --rm alpine uname -m` print?",
            "options": ["aarch64", "x86_64", "darwin", "i386"],
            "answer": 0,
            "why": "The container runs on the arm64 Linux kernel of Docker Desktop's VM, and Linux calls that CPU type aarch64.",
        },
    ],
    "interview": [
        {
            "q": "What is the difference between a container and a virtual machine?",
            "a": (
                "A virtual machine runs a full operating system with its own kernel on virtual hardware, so it is heavy and slow to boot. "
                "A container is a normal process on a Linux host that the kernel isolates with namespaces and limits with cgroups. "
                "Containers share the host kernel, so they start in about a second and use little memory. "
                "The trade-off is weaker isolation: a kernel bug can affect every container on the host, which is why some platforms wrap containers in small VMs."
            ),
        },
        {
            "q": "What happens when you run `docker stop`, and why does it matter?",
            "a": (
                "Docker sends SIGTERM to the container's main process and waits, 10 seconds by default. "
                "A well-written app catches SIGTERM, finishes the requests it is handling and exits cleanly. "
                "If the process is still running after the wait, Docker sends SIGKILL, which ends it at once and can lose work. "
                "Kubernetes stops pods the same way, so handling SIGTERM well matters everywhere."
            ),
        },
    ],
    "deeper": {
        "minutes": 12,
        "body": (
            "You can watch namespaces and cgroups at work with two small experiments.\n\n"
            "First, the process namespace. Run `docker run --rm alpine ps`. The output lists exactly one process: `ps` itself, as PID 1. "
            "Your Mac and the Linux VM run hundreds of processes, but the container cannot see them. "
            "Now run `docker run --rm alpine hostname`. You get a random-looking name, which is the container's short ID. "
            "That is the hostname namespace at work.\n\n"
            "Second, cgroups. Start Redis with a memory limit: `docker run -d --name capped -m 64m redis:8-alpine`. "
            "Then run `docker stats --no-stream capped`. The MEM USAGE / LIMIT column shows something like `5.7MiB / 64MiB`. "
            "If Redis tried to use more than 64 MB, the kernel would stop it. Remove it with `docker rm -f capped`. "
            "Kubernetes memory limits on Day 18 use this same kernel feature.\n\n"
            "Next, look at the VM. `docker version` prints a Client section (the `docker` command on your Mac) and a Server section (the Docker Engine). "
            "On Apple Silicon the server says `linux/arm64`, because the engine runs inside Docker Desktop's Linux VM. "
            "In Docker Desktop, Settings, General, you can choose the virtual machine manager. "
            "For Apple Silicon, Docker's docs list Docker VMM and Apple's Virtualization framework. "
            "There is also a setting to use Rosetta for amd64 emulation, which speeds it up.\n\n"
            "Try emulation yourself: `docker run --rm --platform linux/amd64 alpine uname -m` prints `x86_64` on your arm64 Mac. "
            "The container really runs amd64 code, translated as it runs. That is handy for a quick test, and too slow for heavy work.\n\n"
            "Finally, Docker Desktop is not the only option. OrbStack and Colima also run a Linux VM and give you the same `docker` command. "
            "The commands in this course work with any of them. "
            "For a friendly tour of the kernel features behind all this, read [Julia Evans' post on containers](https://jvns.ca/blog/2016/10/10/what-even-is-a-container/)."
        ),
    },
    "sources": src("running", "ports_concept", "jvns_container", "vmm"),
}

# ================================================================== d06
D06 = {
    "id": "d06",
    "title": "Dockerfiles: package your own app",
    "minutes": 40,
    "goal": "By the end you can write a Dockerfile for hello-devops, build a tagged image, run it with your own settings, and order the steps so rebuilds are fast.",
    "guess": {
        "q": "A Dockerfile does `COPY . .` and then `RUN pip install -r requirements.txt`. You change one line in app.py and rebuild. What happens?",
        "options": [
            "Only app.py is copied again; pip install is reused",
            "pip install runs again, because the layer above it changed",
            "Docker rebuilds everything, including the base image",
            "Nothing changes until you delete the old image",
        ],
        "answer": 1,
        "why": "Each instruction makes a layer, and a changed layer invalidates every layer after it. Copy requirements.txt and install first, then copy the code, so code edits skip the slow install.",
    },
    "terms": [
        {"term": "Dockerfile", "plain": "A text file of instructions that tells Docker how to build an image."},
        {"term": "Base image", "plain": "The image a Dockerfile starts from with FROM, such as python:3.14-slim."},
        {"term": "Layer", "plain": "One saved set of file changes in an image, made by one Dockerfile instruction."},
        {"term": "Build cache", "plain": "Layers Docker saved from earlier builds and reuses when nothing they depend on has changed."},
        {"term": "Build context", "plain": "The folder you pass to docker build; COPY can only take files from inside it."},
        {"term": "Exec form", "plain": "Writing CMD as a JSON list, so the app itself runs as process 1 with no shell in between."},
    ],
    "sections": [
        {
            "h": "A Dockerfile is a recipe written as code",
            "body": (
                "A Dockerfile is a plain text file named `Dockerfile` that lists the steps to build an image. "
                "Docker runs the steps from top to bottom. Each step starts from the result of the step before.\n\n"
                "You keep the Dockerfile in git, next to the app. Teammates review changes to it like any other code. "
                "That is the Day 1 idea of everything as code, applied to packaging.\n\n"
                "The command that runs it is `docker build -t hello-devops:1.0.0 .`. "
                "The `-t` flag gives the new image a name and a tag. "
                "The dot at the end matters too, and you will meet it again below. "
                "Today you write a simple Dockerfile with one stage. Day 8 turns it into the production version."
            ),
            "refs": [R["writing_df"], R["df_overview"]],
        },
        {
            "h": "The instructions you will use",
            "body": (
                "Most Dockerfiles use only a handful of instructions:\n\n"
                "- `FROM` picks the base image to start from, such as `python:3.14-slim`.\n"
                "- `WORKDIR` sets the folder that later steps work in, and creates it.\n"
                "- `COPY` copies files from your project folder into the image.\n"
                "- `RUN` runs a command at build time, such as `pip install`, and saves the result.\n"
                "- `ENV` sets an environment variable for later steps and for the running container.\n"
                "- `ARG` declares a variable you set at build time with `--build-arg`.\n"
                "- `EXPOSE` documents the port the app listens on. It publishes nothing; `-p` does that.\n\n"
                "`CMD` comes last. It is the default command a container runs. "
                "`ENTRYPOINT` is similar, but arguments you give to `docker run` are added to it instead of replacing it. "
                "For a web app, `CMD` alone is the simple choice.\n\n"
                "Write `CMD` in exec form, a JSON list such as `[\"gunicorn\", \"app:app\"]`. "
                "Then your app is process 1 and receives SIGTERM from `docker stop`. "
                "In shell form (`CMD gunicorn app:app`), a shell sits in between and the signal gets lost."
            ),
            "refs": [R["df_ref"], R["build_vars"]],
        },
        {
            "h": "Layers and the build cache",
            "body": (
                "Each instruction that changes files creates a **layer**: a saved set of file changes. "
                "An image is a stack of layers, with the base image at the bottom. "
                "`docker history` lists them with their sizes.\n\n"
                "Docker keeps every layer it builds in its build cache. On the next build, it checks each step in order. "
                "If the instruction and the files it uses are unchanged, Docker reuses the saved layer and prints `CACHED`. "
                "If something changed, Docker rebuilds that layer and every layer after it. "
                "This trips most people up: one early change rebuilds everything below it.\n\n"
                "So order the steps from rarely changed to often changed:\n\n"
                "1. `FROM` the base image.\n"
                "2. `COPY requirements.txt` on its own.\n"
                "3. `RUN pip install`, the slow step.\n"
                "4. `COPY app.py`, which changes all the time.\n\n"
                "Now an edit to `app.py` only rebuilds the last small layer. The install is reused, and the build takes about a second."
            ),
            "refs": [R["cache_concept"], R["cache_opt"]],
        },
        {
            "h": "The build context and .dockerignore",
            "body": (
                "The dot in `docker build -t hello-devops:1.0.0 .` is the **build context**: the folder whose files the build may use. "
                "`COPY` can only copy files from inside it, so a path like `../secrets.txt` fails. "
                "Docker also looks for the file named `Dockerfile` in that folder, unless you name another one with `-f`.\n\n"
                "A `.dockerignore` file in that folder lists files the build must never see. "
                "It uses patterns like `.gitignore` does. Ours keeps out:\n\n"
                "- `.git` and `.github`, the repo's history and workflows\n"
                "- `.venv` and Python caches, which belong to your Mac only\n"
                "- folders for later days, such as `infra`, `k8s` and `chart`\n"
                "- Markdown files, which the app does not need\n\n"
                "Our Dockerfile copies two named files, so the ignore file is a safety net. "
                "It matters the day someone writes `COPY . .`. "
                "Without it, that line copies your `.git` folder, local secrets and other junk into the image. "
                "It also breaks the cache whenever any of those files change."
            ),
            "refs": [R["context"]],
        },
        {
            "h": "Tags and versions",
            "body": (
                "A tag is the part after the colon, as in `hello-devops:1.0.0`. If you leave it out, Docker uses `latest`. "
                "Despite the name, `latest` is just the default label. It does not mean newest, and it can change without warning.\n\n"
                "Two habits avoid surprises:\n\n"
                "- Tag your own images with a real version, such as `1.0.0`. Day 9 explains version numbers.\n"
                "- Name a specific base in `FROM`, such as `python:3.14-slim`, never bare `python`.\n\n"
                "One image can carry several tags. "
                "`docker tag hello-devops:1.0.0 hello-devops:stable` adds a second name without copying anything. "
                "A tag can also be moved to a different image later, by anyone who can push. "
                "Day 8 shows digests, which never move."
            ),
            "refs": [R["best"]],
        },
        {
            "h": "Config through environment variables",
            "body": (
                "[The Twelve-Factor App](https://12factor.net/config) is a well-known set of rules for web apps. "
                "Its config rule says: keep settings that change between deploys in environment variables, outside the code. "
                "Then the same image runs in every place, and only the variables differ.\n\n"
                "hello-devops follows this rule. It reads four variables:\n\n"
                "- `APP_VERSION`, the version it reports\n"
                "- `GREETING`, the message it returns\n"
                "- `REDIS_HOST`, where Redis runs (empty means count in memory)\n"
                "- `PORT`, used only when you run `python app.py`\n\n"
                "In the Dockerfile, `ENV` sets defaults, and `docker run -e GREETING=Hi` overrides them without a rebuild. "
                "The line `ARG APP_VERSION` lets the build stamp a version into the image, and `ENV APP_VERSION=$APP_VERSION` keeps it for run time. "
                "The setting `PYTHONUNBUFFERED=1` makes Python print log lines at once, so `docker logs` shows them. "
                "Never put passwords or keys in `ENV` or `ARG`. Day 8 explains why."
            ),
            "refs": [R["twelve"], R["build_vars"]],
        },
    ],
    "analogy": (
        "A Dockerfile is like a recipe for a layered cake, and the build cache is a fridge full of finished layers. "
        "If you only change the decoration on top, you take every lower layer from the fridge. "
        "If you change the sponge at the bottom, every layer above it must be baked again. "
        "Where it breaks: a real baker could keep an upper layer after changing a lower one, but Docker always rebuilds everything after the first change."
    ),
    "diagram": SVG_D06,
    "diagram_caption": "Each instruction is a layer; after an edit to app.py, only the top layer is rebuilt.",
    "worked": {
        "title": "Package hello-devops and run it",
        "steps": [
            {
                "say": "In your hello-devops folder, create the Dockerfile and .dockerignore from the Files section, then build. The `-t` flag names the image, `--build-arg` fills the ARG, and the final dot is the build context. The first build downloads the base image and runs pip install.",
                "code": (
                    "$ docker build --build-arg APP_VERSION=1.0.0 -t hello-devops:1.0.0 .\n"
                    "[+] Building 11.8s (10/10) FINISHED                    docker:desktop-linux\n"
                    " => [internal] load build definition from Dockerfile                0.0s\n"
                    " => [internal] load metadata for docker.io/library/python:3.14-slim 1.1s\n"
                    " => [internal] load .dockerignore                                   0.0s\n"
                    " => [1/5] FROM docker.io/library/python:3.14-slim@sha256:cd89c30e   0.0s\n"
                    " => [internal] load build context                                   0.0s\n"
                    " => [2/5] WORKDIR /app                                              0.0s\n"
                    " => [3/5] COPY requirements.txt .                                   0.1s\n"
                    " => [4/5] RUN pip install --no-cache-dir -r requirements.txt        9.2s\n"
                    " => [5/5] COPY app.py .                                             0.0s\n"
                    " => exporting to image                                              1.3s\n"
                    " => => naming to docker.io/library/hello-devops:1.0.0               0.0s"
                ),
                "lang": "console",
            },
            {
                "say": "Run it like any other image: publish port 8000 and call two endpoints. The host field is the container's ID, because the hostname namespace gives each container its own name.",
                "code": (
                    "$ docker run -d --name hello -p 8000:8000 hello-devops:1.0.0\n"
                    "9e9c66963d46c0b4a96cc0a9ebc02186318ff1b93670620596c6b066cd14da02\n"
                    "$ curl -s localhost:8000\n"
                    "{\"host\":\"9e9c66963d46\",\"message\":\"Hello, DevOps!\",\"version\":\"1.0.0\",\"visits\":1}\n"
                    "$ curl -s localhost:8000/healthz\n"
                    "{\"status\":\"ok\"}"
                ),
                "lang": "console",
            },
            {
                "say": "Add a comment line to app.py and build again. The three steps above the code say CACHED, so the build takes under a second. Only `COPY app.py` runs. Remove the comment afterwards.",
                "code": (
                    "$ docker build --build-arg APP_VERSION=1.0.0 -t hello-devops:1.0.0 .\n"
                    "[+] Building 0.8s (10/10) FINISHED                     docker:desktop-linux\n"
                    " => [1/5] FROM docker.io/library/python:3.14-slim@sha256:cd89c30e   0.0s\n"
                    " => [internal] load build context                                   0.0s\n"
                    " => => transferring context: 1.75kB                                 0.0s\n"
                    " => CACHED [2/5] WORKDIR /app                                       0.0s\n"
                    " => CACHED [3/5] COPY requirements.txt .                            0.0s\n"
                    " => CACHED [4/5] RUN pip install --no-cache-dir -r requirements.txt 0.0s\n"
                    " => [5/5] COPY app.py .                                             0.1s\n"
                    " => exporting to image                                              0.1s"
                ),
                "lang": "console",
            },
            {
                "say": "`docker history` lists the layers, newest first. The pip install layer holds the real weight. CMD, EXPOSE, ENV and ARG only change settings, so they are 0B. Notice that the ARG value is visible here; remember that on Day 8.",
                "code": (
                    "$ docker history hello-devops:1.0.0\n"
                    "IMAGE          CREATED          CREATED BY                                      SIZE      COMMENT\n"
                    "d1a0f297cfec   47 seconds ago   CMD [\"gunicorn\" \"--bind\" \"0.0.0.0:8000\" \"--w…   0B        buildkit.dockerfile.v0\n"
                    "<missing>      47 seconds ago   EXPOSE [8000/tcp]                               0B        buildkit.dockerfile.v0\n"
                    "<missing>      47 seconds ago   ENV APP_VERSION=1.0.0 PYTHONUNBUFFERED=1        0B        buildkit.dockerfile.v0\n"
                    "<missing>      47 seconds ago   ARG APP_VERSION=1.0.0                           0B        buildkit.dockerfile.v0\n"
                    "<missing>      47 seconds ago   COPY app.py . # buildkit                        12.3kB    buildkit.dockerfile.v0\n"
                    "<missing>      47 seconds ago   RUN /bin/sh -c pip install --no-cache-dir -r…   26.7MB    buildkit.dockerfile.v0\n"
                    "<missing>      54 seconds ago   COPY requirements.txt . # buildkit              12.3kB    buildkit.dockerfile.v0\n"
                    "<missing>      54 seconds ago   WORKDIR /app                                    8.19kB    buildkit.dockerfile.v0\n"
                    "<missing>      2 days ago       CMD [\"python3\"]                                 0B        buildkit.dockerfile.v0"
                ),
                "lang": "console",
            },
            {
                "say": "Settings come from the environment, so the same image can behave differently without a rebuild. Start a second container with another greeting on another port.",
                "code": (
                    "$ docker run -d --name hello2 -p 8001:8000 -e GREETING=\"Hi from a second container\" hello-devops:1.0.0\n"
                    "eec61aec0947375e1b58a090ccb17179e4c4456723c4c86c9adf58e58bd9fd0d\n"
                    "$ curl -s localhost:8001\n"
                    "{\"host\":\"eec61aec0947\",\"message\":\"Hi from a second container\",\"version\":\"1.0.0\",\"visits\":1}"
                ),
                "lang": "console",
            },
            {
                "say": "`docker inspect` shows every setting of an image as JSON. A `--format` template picks out the fields you want. Then clean up both containers.",
                "code": (
                    "$ docker inspect hello-devops:1.0.0 --format '{{json .Config.Cmd}} {{.Config.WorkingDir}}'\n"
                    "[\"gunicorn\",\"--bind\",\"0.0.0.0:8000\",\"--workers\",\"2\",\"app:app\"] /app\n"
                    "$ docker rm -f hello hello2\n"
                    "hello\n"
                    "hello2"
                ),
                "lang": "console",
            },
        ],
    },
    "code": [
        {
            "lang": "dockerfile",
            "title": "Dockerfile (Day 6 version: one stage)",
            "src": SINGLE_DOCKERFILE,
            "run": "docker build --build-arg APP_VERSION=1.0.0 -t hello-devops:1.0.0 . && docker run --rm -p 8000:8000 hello-devops:1.0.0",
        },
        {
            "lang": "text",
            "title": ".dockerignore",
            "src": LAB_DOCKERIGNORE,
            "run": "docker build --build-arg APP_VERSION=1.0.0 -t hello-devops:1.0.0 .",
        },
    ],
    "commands": [
        {"cmd": "docker build -t hello-devops:1.0.0 .", "what": "Build an image from the Dockerfile in this folder and tag it."},
        {"cmd": "docker build --build-arg APP_VERSION=1.0.0 -t hello-devops:1.0.0 .", "what": "Build and pass a value to an ARG in the Dockerfile."},
        {"cmd": "docker build -f Dockerfile.slow -t hello-devops:slow .", "what": "Build from a Dockerfile with a different file name."},
        {"cmd": "docker history hello-devops:1.0.0", "what": "Show an image's layers, their sizes and the instruction that made each one."},
        {"cmd": "docker inspect hello-devops:1.0.0", "what": "Show every setting of an image or container as JSON."},
        {"cmd": "docker inspect --format '{{json .Config.Env}}' hello-devops:1.0.0", "what": "Pick out one field, here the image's environment variables."},
        {"cmd": "docker tag hello-devops:1.0.0 hello-devops:stable", "what": "Give an image a second name; nothing is copied."},
        {"cmd": "docker run --rm -p 8000:8000 -e GREETING=Hi hello-devops:1.0.0", "what": "Run the image with one setting overridden by an env var."},
        {"cmd": "docker run --rm hello-devops:1.0.0 ls -a", "what": "Run another command instead of CMD, here to list the /app folder."},
        {"cmd": "docker image prune", "what": "Delete dangling images (old builds with no tag) to free disk space."},
    ],
    "mistake": (
        "Putting `COPY . .` before `RUN pip install`. "
        "Then every code change, even a comment, invalidates the cache and reinstalls every package. "
        "Copy only `requirements.txt` first, install, and copy the code last."
    ),
    "real_world": (
        "At PayFlow, a fake payments company, every service keeps its Dockerfile in its own repo, and changes to it go through code review. "
        "CI builds the image once per commit, and that same image moves from testing to production with only env vars changing. "
        "Teams also watch Dockerfile order, because one misplaced COPY makes every build reinstall all dependencies."
    ),
    "task": {
        "title": "Break the cache, leak a file, then fix both",
        "steps": [
            "Create the Dockerfile and .dockerignore from Files in your hello-devops folder. Build `hello-devops:1.0.0`, run it, and curl `/metrics`.",
            "Copy the Dockerfile to `Dockerfile.slow`. In the copy, replace both COPY lines with one `COPY . .` placed before `RUN pip install`.",
            "Build the slow image with `-f Dockerfile.slow`, add a comment to app.py, and build it again. Note which steps rerun and how long it takes.",
            "Make the same edit and rebuild with your real Dockerfile. Compare the two.",
            "Create a file `secret.txt` with some fake text. Rebuild the slow image and list its files with `docker run --rm`. Is the file there?",
            "Add `secret.txt` to .dockerignore, rebuild the slow image, and check again.",
            "Run your real image with different `GREETING` and `APP_VERSION` values, and confirm the JSON changes without a rebuild.",
            "Clean up `Dockerfile.slow`, `secret.txt`, its .dockerignore line and the slow image. Commit the Dockerfile and .dockerignore, and push.",
        ],
        "hints": [
            "`docker run --rm IMAGE ls -a` runs `ls -a` in the image's WORKDIR instead of the normal CMD.",
            "A step says CACHED only when its instruction, the files it copies, and every step above it are unchanged.",
        ],
        "done_when": "You are done when the slow Dockerfile reruns pip install after a comment change, your real one shows it as CACHED, and secret.txt is no longer in the slow image.",
    },
    "explain_back": {
        "prompt": "Explain in 3 to 4 sentences why the order of lines in a Dockerfile matters for build speed. Mention layers, the cache and requirements.txt.",
        "answer": (
            "Each Dockerfile instruction creates a layer, and Docker caches each layer. "
            "When an instruction or the files it copies change, Docker rebuilds that layer and every layer after it. "
            "Dependencies change rarely and take long to install, while code changes all the time. "
            "So I copy requirements.txt and run pip install first, then copy the code, and a code change only rebuilds the last small layer."
        ),
    },
    "recap": [
        "A Dockerfile lists the steps that build an image; keep it in git next to the app.",
        "Each instruction adds a layer; a change rebuilds that layer and every layer after it.",
        "Copy requirements.txt and install before you copy the code, so edits reuse the cache.",
        "The build context is the folder you pass to docker build; .dockerignore keeps junk and secrets out.",
        "Tag images with real versions; latest is only a default name.",
        "Settings belong in environment variables, so one image runs everywhere.",
    ],
    "check": [
        {
            "q": "The Dockerfile says `ENV GREETING=Hello`. You start the container with `docker run -e GREETING=Hi image`. What does the app see?",
            "options": [
                "Hello, because the Dockerfile wins",
                "Both values, joined together",
                "Nothing, because ENV only exists at build time",
                "Hi, because -e overrides the image default",
            ],
            "answer": 3,
            "why": "ENV sets a default inside the image, and a value passed with -e at run time replaces it.",
        },
        {
            "q": "A Kotlin service's Dockerfile copies `build.gradle.kts`, downloads dependencies, then copies `src/` and compiles. Which change makes the next build slowest?",
            "options": [
                "Editing one class in src/",
                "Adding a dependency to build.gradle.kts",
                "Changing a file listed in .dockerignore",
                "Running the same build twice in a row",
            ],
            "answer": 1,
            "why": "The dependency file is copied early, so changing it invalidates the download layer and everything after it.",
        },
        {
            "q": "`docker build -t api .` fails on the line `COPY ../shared/config.yml .`. Why?",
            "options": [
                "The file is outside the build context",
                "COPY cannot copy YAML files",
                "The image needs EXPOSE before COPY",
                "COPY only works after a RUN step",
            ],
            "answer": 0,
            "why": "COPY can only read files inside the folder passed to docker build, here the current folder.",
        },
    ],
    "interview": [
        {
            "q": "What is the difference between CMD and ENTRYPOINT?",
            "a": (
                "Both define what runs when a container starts. "
                "ENTRYPOINT sets the program, and arguments given to `docker run` are added after it. "
                "CMD sets the default command or default arguments, and anything you type after the image name replaces it. "
                "A common pattern is ENTRYPOINT for the binary and CMD for its default flags. "
                "Either way, use the exec form, a JSON list, so the app runs as process 1 and receives signals like SIGTERM."
            ),
        },
        {
            "q": "How do you make Docker builds fast?",
            "a": (
                "Order instructions from least to most often changed, so the cache is reused: base image, dependency files, install, then source code. "
                "Copy only the files you need and keep a .dockerignore, so unrelated changes do not break the cache. "
                "Use small base images, so there is less to download and push. "
                "In CI, share the build cache between runs, because fresh runners start with an empty cache."
            ),
        },
    ],
    "deeper": {
        "minutes": 12,
        "body": (
            "Here is a small test that shows why the exec form of CMD matters. "
            "Make a second Dockerfile that starts `FROM hello-devops:1.0.0` and adds one line in shell form: `CMD gunicorn --bind 0.0.0.0:8000 app:app`. "
            "Build it as `hello-devops:shell` and run it. Then look at process 1 in each container with `docker exec <name> cat /proc/1/cmdline | tr '\\0' ' '`:\n\n"
            "- In the shell-form container, process 1 is `/bin/sh -c gunicorn --bind 0.0.0.0:8000 app:app`.\n"
            "- In your real image, process 1 is `/usr/local/bin/python3.14 /usr/local/bin/gunicorn ...`.\n\n"
            "Now time `docker stop` on each, for example with `time docker stop <name>`. "
            "When we tried it, the shell-form container took about 10 seconds and ended as `Exited (137)`. "
            "The exec-form container stopped in under a second, with exit code 0.\n\n"
            "Why the difference? `docker stop` sends SIGTERM to process 1. The shell does not pass it on to gunicorn, so nothing happens. "
            "After 10 seconds Docker gives up and sends SIGKILL. "
            "Exit code 137 is 128 + 9, and 9 is the number of SIGKILL (Day 3). "
            "In production, that means every deploy waits 10 extra seconds per container, and requests in flight are cut off.\n\n"
            "A second detail, about the build context. Docker builds use BuildKit, which only reads the files a build actually needs. "
            "With `COPY app.py .`, a large file elsewhere in your folder costs nothing. "
            "With `COPY . .`, the whole folder, minus the `.dockerignore` entries, is read and sent to the builder. "
            "In our test, a 30 MB `.venv` folder that was not ignored added 30 MB to the context on every build. "
            "That is one more reason to copy named files and keep `.dockerignore` up to date.\n\n"
            "To go further, read the [Dockerfile reference](https://docs.docker.com/reference/dockerfile/) on CMD and ENTRYPOINT. "
            "It has a table that shows how the two combine."
        ),
    },
    "sources": src("df_ref", "cache_opt", "context", "twelve"),
}

# ================================================================== d07
D07 = {
    "id": "d07",
    "title": "Data, networks and Docker Compose",
    "minutes": 40,
    "goal": "By the end you can keep data in volumes, connect containers by name, and run hello-devops with Redis from one compose.yaml.",
    "guess": {
        "q": "You run Postgres in a container, add some rows, then `docker rm` it and start a new container from the same image. Where are your rows?",
        "options": [
            "In the image, so the new container has them",
            "Saved to Docker Hub automatically",
            "Gone, unless the data lived in a volume",
            "In a backup that docker rm makes first",
        ],
        "answer": 2,
        "why": "Data written inside a container lives in its writable layer, which docker rm deletes. Only a volume (or a bind mount) keeps data outside the container's life.",
    },
    "terms": [
        {"term": "Volume", "plain": "Storage that Docker manages, which stays when containers are removed."},
        {"term": "Bind mount", "plain": "A folder from your computer shown inside a container, so both see the same files."},
        {"term": "User-defined network", "plain": "A private network you create; containers on it find each other by name."},
        {"term": "Docker Compose", "plain": "A tool that starts several containers from one YAML file with one command."},
        {"term": "Service", "plain": "One entry in compose.yaml that describes a container to run, such as web or redis."},
        {"term": "Healthcheck", "plain": "A command Docker runs again and again to test whether a container works."},
    ],
    "sections": [
        {
            "h": "Containers come and go, data must stay",
            "body": (
                "A container's own files live in its writable layer. When you remove the container, they are gone. "
                "That is a good thing. You should be able to delete and recreate any container at any moment, for an upgrade or after a crash.\n\n"
                "So data you care about must live outside the container. Docker gives you two ways to do that: volumes and bind mounts. "
                "Both attach outside storage to a folder inside the container.\n\n"
                "hello-devops needs this too. On Day 6 the visit count lived in memory, so every restart reset it to zero. "
                "You may also have seen it jump back now and then. "
                "Gunicorn runs two worker processes, and each one keeps its own count. "
                "Today you move the count into Redis, an in-memory database. "
                "Then all workers share one number, and Redis keeps it in a volume that survives restarts."
            ),
            "refs": [R["volumes"]],
        },
        {
            "h": "Volumes and bind mounts",
            "body": (
                "The two kinds differ in who owns the storage:\n\n"
                "- A volume is storage that Docker creates and manages, as in `-v redis-data:/data`.\n"
                "- A bind mount shows a folder from your Mac inside the container, as in `-v \"$PWD/site\":/usr/share/nginx/html`.\n\n"
                "The left side of `-v` decides which one you get. A plain name means a volume. A path on your Mac means a bind mount. "
                "The right side is always the folder inside the container.\n\n"
                "Use volumes for data the app owns, such as database files. "
                "They survive `docker rm` and stay until you delete them with `docker volume rm`. "
                "Use bind mounts while developing, when you edit files on your Mac and want the container to see each change at once. "
                "On a Mac, bind-mounted files must cross from macOS into Docker's Linux VM, so heavy file work can be slower."
            ),
            "refs": [R["volumes"], R["running"]],
        },
        {
            "h": "Networks: containers find each other by name",
            "body": (
                "Each container gets its own IP address on a Docker network. "
                "On the default network, containers can only reach each other by IP address, and that address can change on every restart.\n\n"
                "A user-defined network fixes this. You create one with `docker network create hello-net`. "
                "Containers you start with `--network hello-net` get a built-in DNS server. "
                "On that network, the name `redis` resolves to the current IP of the container called redis.\n\n"
                "Two details matter:\n\n"
                "- Containers on the same network can reach each other on any port. `-p` is only for traffic from your Mac.\n"
                "- Inside a container, `localhost` means that container itself (Day 4). So `REDIS_HOST=localhost` points the app at its own container, where no Redis runs.\n\n"
                "Containers on different user-defined networks cannot reach each other at all, which keeps unrelated apps apart. "
                "Compose creates a network like this for every project, as you will see next."
            ),
            "refs": [R["bridge"], R["net_overview"]],
        },
        {
            "h": "Docker Compose: the whole app in one file",
            "body": (
                "Running a network, a volume and two containers by hand takes several long commands. "
                "**Docker Compose** puts all of it in one file, `compose.yaml`, and starts it with `docker compose up`.\n\n"
                "The file has a top-level `services` map. Each service describes one container, and its name doubles as its hostname. "
                "Inside a service you will use these keys:\n\n"
                "- `build: .` builds the image from the Dockerfile in this folder.\n"
                "- `image:` uses a ready-made image, such as `redis:8-alpine`.\n"
                "- `ports:` publishes ports, written `\"HOST:CONTAINER\"` in quotes.\n"
                "- `environment:` sets env vars.\n"
                "- `volumes:` mounts volumes or folders.\n"
                "- `depends_on:` controls start order.\n\n"
                "Named volumes are also listed under a top-level `volumes` key. Compose creates a network for the project on its own. "
                "The project name is the folder name, so your containers are called `hello-devops-web-1` and `hello-devops-redis-1`."
            ),
            "refs": [R["compose_model"], R["compose_services"], R["nana_compose"]],
        },
        {
            "h": "Start order and health checks",
            "body": (
                "`depends_on` makes Compose start Redis before web. "
                "Plain `depends_on` only waits for the Redis container to start, though, and Redis may need a moment more before it answers.\n\n"
                "A **healthcheck** closes that gap. It is a command Docker runs again and again inside the container. "
                "Exit code 0 means healthy, and anything else means a failed check (Day 3 exit codes). "
                "Ours runs `redis-cli ping` every 5 seconds, with a 3-second timeout and 5 retries.\n\n"
                "With the long form of `depends_on` and `condition: service_healthy`, Compose waits until Redis is healthy before it starts web. "
                "Your app should still cope when a dependency fails later. "
                "hello-devops does: `/readyz` returns 503 while Redis is down, and Kubernetes will use that on Day 18.\n\n"
                "You can watch the health in `docker compose ps`. "
                "The STATUS column says `(health: starting)` at first, then `(healthy)` once a check passes. "
                "If a check keeps failing, it says `(unhealthy)`, and web never starts."
            ),
            "refs": [R["startup"], R["compose_quick"]],
        },
        {
            "h": ".env files and everyday Compose commands",
            "body": (
                "Compose reads a file named `.env` next to `compose.yaml` and uses it to fill in `${VARIABLE}` placeholders. "
                "For example, `GREETING: \"${GREETING:-Hello, DevOps!}\"` takes `GREETING` from `.env` or your shell. "
                "If neither sets it, Compose uses the default after `:-`. "
                "A variable set in your shell wins over `.env`. "
                "If `.env` ever holds secrets, list it in `.gitignore`. "
                "`docker compose config` prints the final file with every value filled in.\n\n"
                "These commands cover daily work:\n\n"
                "- `docker compose up -d --build` builds and starts everything in the background.\n"
                "- `docker compose ps` shows each container and its health.\n"
                "- `docker compose logs -f web` follows one service's output.\n"
                "- `docker compose exec redis redis-cli GET visits` runs a command in a service.\n"
                "- `docker compose down` removes the containers and the network, and keeps volumes.\n"
                "- `docker compose down -v` also deletes the volumes, and with them your data."
            ),
            "refs": [R["interp"], R["precedence"], R["compose_config"]],
        },
    ],
    "analogy": (
        "A volume is like a locker at a swimming pool. "
        "Swimmers (containers) come and go, and the next swimmer with the same key finds the things left inside. "
        "The network is the front desk: you ask for \"redis\" by name, and it tells you where to go. "
        "Where it breaks: a volume lives on one Docker host, so it does not follow your container to another machine."
    ),
    "diagram": SVG_D07,
    "diagram_caption": "Compose puts web and redis on one network; redis keeps its data in a named volume.",
    "worked": {
        "title": "Wire up web and Redis by hand",
        "steps": [
            {
                "say": "Create a user-defined network and a named volume. Naming them lets you reuse them by name in the next commands.",
                "code": (
                    "$ docker network create hello-net\n"
                    "bf68a33e0bc58f297d719bb2b36f551356a182a8cf0c35892d34b323e24def5d\n"
                    "$ docker volume create redis-data\n"
                    "redis-data"
                ),
                "lang": "console",
            },
            {
                "say": "Start Redis on the network with the volume at /data, the folder where Redis saves its file. Then start hello-devops on the same network and tell it where Redis is. Redis needs no `-p`, because only web talks to it.",
                "code": (
                    "$ docker run -d --name redis --network hello-net -v redis-data:/data redis:8-alpine\n"
                    "3d7c97d4b830736b8f712e850e6016dcda83c109d81fb5227c6ecaa4091b2f51\n"
                    "$ docker run -d --name web --network hello-net -p 8000:8000 -e REDIS_HOST=redis hello-devops:1.0.0\n"
                    "d557ea061207b07259f83ebc114cf87eaf3639cb12df9ab96adc36aa26c6daf3"
                ),
                "lang": "console",
            },
            {
                "say": "Call the app a few times. The count now rises by one each time, because both gunicorn workers share one Redis. Inside the web container, Docker's DNS turns the name redis into Redis's private IP.",
                "code": (
                    "$ for i in 1 2 3; do curl -s localhost:8000; echo; done\n"
                    "{\"host\":\"d557ea061207\",\"message\":\"Hello, DevOps!\",\"version\":\"1.0.0\",\"visits\":1}\n"
                    "{\"host\":\"d557ea061207\",\"message\":\"Hello, DevOps!\",\"version\":\"1.0.0\",\"visits\":2}\n"
                    "{\"host\":\"d557ea061207\",\"message\":\"Hello, DevOps!\",\"version\":\"1.0.0\",\"visits\":3}\n"
                    "$ docker exec web python -c \"import socket; print(socket.gethostbyname('redis'))\"\n"
                    "172.19.0.2"
                ),
                "lang": "console",
            },
            {
                "say": "Now replace Redis. Stop it first (SIGTERM gives Redis time to save its data), then remove it. While it is gone, the readiness endpoint reports the problem.",
                "code": (
                    "$ docker stop redis && docker rm redis\n"
                    "redis\n"
                    "redis\n"
                    "$ curl -s localhost:8000/readyz\n"
                    "{\"status\":\"redis unavailable\"}"
                ),
                "lang": "console",
            },
            {
                "say": "Start a brand-new Redis container with the same volume. The count continues from where it stopped, because the data lived in the volume, not in the old container.",
                "code": (
                    "$ docker run -d --name redis --network hello-net -v redis-data:/data redis:8-alpine\n"
                    "4749454873a6e0ae019d19f1c5e4a101e6e521b6761b20dcd444fbfca9bd7eca\n"
                    "$ curl -s localhost:8000\n"
                    "{\"host\":\"d557ea061207\",\"message\":\"Hello, DevOps!\",\"version\":\"1.0.0\",\"visits\":4}"
                ),
                "lang": "console",
            },
            {
                "say": "Clean up everything. That took five long commands to set up; the hands-on task puts the same app in one compose.yaml.",
                "code": (
                    "$ docker rm -f web redis\n"
                    "web\n"
                    "redis\n"
                    "$ docker network rm hello-net\n"
                    "hello-net\n"
                    "$ docker volume rm redis-data\n"
                    "redis-data"
                ),
                "lang": "console",
            },
        ],
    },
    "code": [
        {
            "lang": "yaml",
            "title": "compose.yaml",
            "src": LAB_COMPOSE,
            "run": "docker compose up -d --build",
        }
    ],
    "commands": [
        {"cmd": "docker volume create redis-data", "what": "Create a named volume."},
        {"cmd": "docker volume ls", "what": "List volumes; they stay after their containers are gone."},
        {"cmd": "docker network create hello-net", "what": "Create a user-defined network where containers find each other by name."},
        {"cmd": "docker run -d --name redis --network hello-net -v redis-data:/data redis:8-alpine", "what": "Run a container on a network with a volume mounted at /data."},
        {"cmd": "docker compose up -d --build", "what": "Build images if needed and start every service in the background."},
        {"cmd": "docker compose ps", "what": "Show the project's containers, ports and health."},
        {"cmd": "docker compose logs -f web", "what": "Follow the output of one service (Ctrl+C to stop)."},
        {"cmd": "docker compose exec redis redis-cli GET visits", "what": "Run a command inside a running service container."},
        {"cmd": "docker compose down", "what": "Stop and remove the containers and the network; named volumes stay."},
        {"cmd": "docker compose down -v", "what": "Also delete the named volumes, and the data in them."},
        {"cmd": "docker compose config", "what": "Print the final Compose file with .env values filled in."},
    ],
    "mistake": (
        "Typing `docker compose down -v` when you meant `docker compose down`. "
        "The `-v` flag deletes the named volumes, so your Redis data, or a whole database, is gone for good. "
        "Use plain `down` day to day, and `down -v` only when you want a clean start."
    ),
    "real_world": (
        "At PayFlow, a fake payments company, every service repo has a compose.yaml, so a new engineer can run the service with its Postgres and Redis using one command. "
        "CI often uses the same file to start real dependencies for integration tests. "
        "In production the same images usually run on Kubernetes (Day 16), and the databases are managed services instead of containers."
    ),
    "task": {
        "title": "Run hello-devops and Redis with Compose",
        "steps": [
            "Create `compose.yaml` in your hello-devops folder with two services: `web`, built from your Dockerfile, and `redis`, from `redis:8-alpine`.",
            "Publish port 8000 for web, set `REDIS_HOST` and `APP_VERSION`, and mount a named volume `redis-data` at `/data` in redis.",
            "Give redis a healthcheck that runs `redis-cli ping`, and make web wait until redis is healthy.",
            "Stop any Day 6 container that still uses port 8000. Run `docker compose up -d --build`, then `docker compose ps`, and wait for (healthy).",
            "Call `curl localhost:8000` five times and check that visits rises by one each time.",
            "Run `docker compose down`, then `docker compose up -d`, and check that the count carries on.",
            "Try a .env file: add `GREETING: \"${GREETING:-Hello, DevOps!}\"` under web's environment, put a greeting in `.env`, add `.env` to .gitignore, and check with `docker compose config`.",
            "Finish with `docker compose down -v`, start again, and see the count reset to 1.",
            "Commit compose.yaml and .gitignore, and push.",
        ],
        "hints": [
            "Compose service names are also hostnames on the project network.",
            "The long form of `depends_on` is a map: the service name, then `condition:` under it.",
            "Compare your file with the one in Files only after it works.",
        ],
        "done_when": "You are done when `docker compose down` followed by `docker compose up -d` keeps the visit count rising instead of starting again at 1.",
    },
    "explain_back": {
        "prompt": "Explain in 3 to 4 sentences how the web container finds Redis, and why the visit count survives `docker compose down`. Mention the network, the service name and the volume.",
        "answer": (
            "Compose creates a network for the project and attaches both services to it. "
            "Docker's DNS on that network turns the service name redis into the Redis container's IP, so REDIS_HOST=redis is all the app needs. "
            "Redis saves its data in /data, and compose.yaml mounts the named volume redis-data there. "
            "Running `docker compose down` removes the containers and the network but keeps named volumes. "
            "So a new Redis container finds the old data, and only `down -v` deletes it."
        ),
    },
    "recap": [
        "A container's own files die with it; keep data you need in a volume.",
        "Volumes are managed by Docker; bind mounts share a folder from your Mac.",
        "On a user-defined network, containers reach each other by name.",
        "compose.yaml describes services, ports, env vars, volumes and start order.",
        "depends_on with service_healthy waits for a healthcheck to pass.",
        "`docker compose down` keeps volumes; `down -v` deletes them.",
    ],
    "check": [
        {
            "q": "Your app container uses `REDIS_HOST=localhost`, and Redis runs in a second container on the same network. Every call fails. Why?",
            "options": [
                "Redis must be published with -p first",
                "Inside a container, localhost is that container itself",
                "Docker DNS only works with IP addresses",
                "Redis refuses connections from other containers",
            ],
            "answer": 1,
            "why": "Each container has its own network namespace, so localhost points at the app's own container, where nothing listens on 6379.",
        },
        {
            "q": "You want to edit HTML files on your Mac and see each change in an nginx container at once. Which option fits?",
            "options": [
                "A named volume mounted at the HTML folder",
                "COPY the files in a Dockerfile and rebuild",
                "A new user-defined network",
                "A bind mount of your folder at the HTML folder",
            ],
            "answer": 3,
            "why": "A bind mount shows your Mac's folder inside the container, so both always see the same files.",
        },
        {
            "q": "A compose.yaml uses `depends_on: [db]` in the short form, and db has no healthcheck. What does Compose wait for before starting the app?",
            "options": [
                "The db container to start, not to be ready",
                "The database to accept connections",
                "The db healthcheck to pass",
                "Nothing; the start order is random",
            ],
            "answer": 0,
            "why": "The short form only orders container starts; waiting for readiness needs a healthcheck and condition: service_healthy.",
        },
    ],
    "interview": [
        {
            "q": "When would you use a volume, and when a bind mount?",
            "a": (
                "I use a named volume for data the app owns, such as a database's files. "
                "Docker manages it, and it does not depend on the host's folder layout. "
                "I use a bind mount when both I and the container need the files, such as source code I edit during development. "
                "In production, bind mounts tie a container to one machine's folders, so they are rare there. "
                "In both cases the data outlives the container."
            ),
        },
        {
            "q": "Is Docker Compose suitable for production?",
            "a": (
                "Compose is great for local development, demos and CI test setups: one file, one command. "
                "It runs containers on a single host, so it cannot spread them over several machines or move them when a machine dies. "
                "Some small apps do run with Compose on one server, but most teams use Kubernetes or a managed container service in production. "
                "The images stay the same either way, which is the real win."
            ),
        },
    ],
    "deeper": {
        "minutes": 12,
        "body": (
            "Why did the count survive when you replaced Redis? And when would it not?\n\n"
            "Redis keeps its data in memory. It writes a snapshot file, `dump.rdb`, to `/data` from time to time, and again when it shuts down cleanly. "
            "Run `docker exec redis redis-cli CONFIG GET save` and you see the snapshot rules: `3600 1 300 100 60 10000`. "
            "Read them in pairs:\n\n"
            "- after 3600 seconds, if at least 1 key changed\n"
            "- after 300 seconds, if at least 100 keys changed\n"
            "- after 60 seconds, if at least 10000 keys changed\n\n"
            "In the worked example you used `docker stop`. That sends SIGTERM, Redis saves a final snapshot, and nothing is lost. "
            "Now try the rough way. Call the app a few more times, then run `docker rm -f redis`. "
            "The `-f` flag sends SIGKILL at once, so Redis has no chance to save. "
            "When we tried it, the count was 9 before the kill. "
            "A fresh Redis on the same volume read the last snapshot and reported 5, the value saved at the last clean stop. "
            "The four visits in between were lost.\n\n"
            "This is the Day 3 lesson about signals, with real data at stake. A few practical rules follow:\n\n"
            "- Stop stateful containers with `docker stop` or `docker compose down`, both of which send SIGTERM first.\n"
            "- For data you cannot lose, turn on Redis's append-only file with `--appendonly yes`, which logs every write.\n"
            "- In production, consider a managed database service, where backups and failover are someone's full-time job.\n\n"
            "Also notice where the data really sits. `docker volume inspect redis-data` shows a mount point under `/var/lib/docker/volumes`. "
            "On a Mac, that path is inside Docker Desktop's Linux VM, so you will not find it in Finder. "
            "If you reset Docker Desktop to factory defaults, your volumes go with it."
        ),
    },
    "sources": src("volumes", "bridge", "startup", "interp"),
}

# ================================================================== d08
D08 = {
    "id": "d08",
    "title": "Production-ready images and registries",
    "minutes": 40,
    "goal": "By the end you can turn hello-devops into a multi-stage, non-root image with a health check, scan it, and push it to GHCR for both arm64 and amd64.",
    "guess": {
        "q": "Your build needs an API key. Which approach keeps the key out of the image?",
        "options": [
            "Set it with ENV, then unset it in a later RUN step",
            "Pass it with --build-arg so it is never in a file",
            "COPY the key file in, use it, then RUN rm it",
            "Use a build secret mount, or pass it at run time",
        ],
        "answer": 3,
        "why": "Every layer ships with the image, and ARG and ENV values show up in its history and metadata. A secret mount never lands in a layer, and run-time secrets never enter the image at all.",
    },
    "terms": [
        {"term": "Multi-stage build", "plain": "A Dockerfile with several FROM stages, where only the last stage becomes the final image."},
        {"term": "Non-root user", "plain": "A normal user with few rights that the app runs as, instead of the all-powerful root."},
        {"term": "CVE", "plain": "A public, numbered record of a known security hole in a piece of software."},
        {"term": "Digest", "plain": "A sha256 hash that names one exact image content and can never point to anything else."},
        {"term": "GHCR", "plain": "GitHub Container Registry: GitHub's image registry at ghcr.io."},
        {"term": "Multi-platform image", "plain": "One image name that holds a variant for each CPU type, such as amd64 and arm64."},
    ],
    "sections": [
        {
            "h": "Multi-stage builds",
            "body": (
                "Building an app often needs tools that running it does not. "
                "A Kotlin service needs a JDK and Gradle to compile, but only a Java runtime to run. "
                "Python packages with C code need a compiler to install.\n\n"
                "A **multi-stage build** has several `FROM` lines in one Dockerfile. Each `FROM` starts a new stage. "
                "Only the last stage becomes your image. "
                "Earlier stages are scratch space: you build there, then copy just the results forward with `COPY --from=<stage>`.\n\n"
                "Our final Dockerfile has two stages:\n\n"
                "1. `build` creates a virtual environment (a venv) in `/venv` and installs the packages into it.\n"
                "2. The run stage starts again from a clean `python:3.14-slim` and copies in `/venv` and `app.py`, nothing else.\n\n"
                "A venv keeps every installed package in one folder, so one `COPY` moves them all. "
                "For hello-devops the size barely changes, because nothing is compiled. "
                "The pattern pays off when a build needs compilers or a JDK, and it keeps the shipped stage short and clear."
            ),
            "refs": [R["multistage"]],
        },
        {
            "h": "Choosing a base image",
            "body": (
                "The base image decides most of your image's size and most of its security findings. "
                "Fewer packages means less to download and less to patch. The common choices for Python:\n\n"
                "- `python:3.14` is full Debian with compilers, about 1.6 GB on disk.\n"
                "- `python:3.14-slim` is Debian with the minimum, about 180 MB. A good default.\n"
                "- `python:3.14-alpine` is about 75 MB, but its C library (musl) differs, so some packages misbehave.\n"
                "- Distroless images hold only a runtime and your app, with no shell, so debugging is harder.\n"
                "- Docker Hardened Images are minimal and run as non-root by default. They are free (Apache 2.0) from `dhi.io`.\n\n"
                "The sizes come from `docker images` on an amd64 machine in October 2026. "
                "Whatever you pick, rebuild often, so your image gets the base image's security fixes."
            ),
            "refs": [R["best"], R["dhi"], R["dhi_blog"]],
        },
        {
            "h": "Run as a normal user, and add a health check",
            "body": (
                "By default, the process in a container runs as root. Inside the container that root is limited, but it is still root on the shared kernel. "
                "If an attacker breaks into your app, root makes the next step easier. "
                "Least privilege (Day 3) says: run as a normal user.\n\n"
                "Our Dockerfile does this in two lines. `RUN useradd --uid 10001 --no-create-home appuser` creates the user. "
                "`USER 10001` makes every later step, and the container, run as that user. "
                "Use the number, not the name: Kubernetes can only prove that an image is non-root when the user is numeric (Day 18).\n\n"
                "`HEALTHCHECK` tells Docker how to test the app. Every 30 seconds, Docker runs a short Python command that calls `/healthz`. "
                "The slim image has no `curl`, so Python does the job. "
                "`docker ps` then shows `(healthy)` or `(unhealthy)`. "
                "Plain Docker and Compose use this line; Kubernetes ignores it and uses its own probes."
            ),
            "refs": [R["df_ref"], R["best"]],
        },
        {
            "h": "Scan images for known vulnerabilities",
            "body": (
                "A vulnerability scanner lists the packages in your image and checks them against public lists of CVEs. "
                "Two scanners are easy to start with:\n\n"
                "- `docker scout` comes with Docker Desktop. `docker scout quickview` gives a summary, and `docker scout cves` lists each finding.\n"
                "- Trivy is a free, open source scanner. Install it with `brew install trivy` and run `trivy image hello-devops:1.0.0`.\n\n"
                "Sign in to Docker before you use Scout, and check its docs for current plan limits.\n\n"
                "Expect a long list the first time. Most findings sit in the base image's packages, and many have no fix yet. "
                "Focus on what you can act on: `--ignore-unfixed` hides findings without a fixed version. "
                "Then update the base image or a package version, and rebuild. "
                "Day 22 adds a scan to the release pipeline, so a serious finding that has a fix stops a release."
            ),
            "refs": [R["scout_install"], R["scout_qv"], R["trivy_start"]],
        },
        {
            "h": "Tags, digests and pushing to a registry",
            "body": (
                "A tag can move: someone can push a new image as `python:3.14-slim` tomorrow. "
                "A digest is a sha256 hash of the image's content, written `name@sha256:...`, and it always means exactly the same image. "
                "Deploy files often pin a digest, so the image you tested is the image that runs.\n\n"
                "To share an image, you push it to a registry. GitHub Container Registry (GHCR) lives at `ghcr.io` and sits next to your repo. The steps:\n\n"
                "1. Create a personal access token (classic) with the `write:packages` scope. GitHub's docs say GHCR needs this token type.\n"
                "2. Log in with `docker login ghcr.io -u <your-github-user>` and paste the token as the password.\n"
                "3. Give the image its full name with `docker tag`, as in `ghcr.io/<your-github-user>/hello-devops:1.0.0`.\n"
                "4. Run `docker push`. Its last line prints the digest.\n\n"
                "Write your user name in lowercase, because image names cannot contain capitals. "
                "New GHCR packages start private. Docker Hub works the same way, with names like `<user>/hello-devops`."
            ),
            "refs": [R["ghcr"], R["ghcr_access"]],
        },
        {
            "h": "Two CPU types, and no secrets inside",
            "body": (
                "Your Mac builds arm64 images, while most cloud servers are amd64. "
                "An arm64-only image fails on such a server with `exec format error`. "
                "The fix is a multi-platform image: one name, with one variant per CPU type.\n\n"
                "`docker buildx build --platform linux/amd64,linux/arm64 -t <name> --push .` builds both and pushes them together. "
                "Docker Desktop builds the amd64 half through emulation, so it takes longer. "
                "When a server pulls the image, the registry hands it the variant for its CPU.\n\n"
                "One last rule: never bake secrets into an image. "
                "Every layer ships with the image, so a key you `COPY` in and later delete still sits in an earlier layer. "
                "Values from `ARG` and `ENV` show up in the image history, as you saw on Day 6. "
                "Give secrets to the container at run time instead. "
                "If a build step truly needs one, use a build secret (`RUN --mount=type=secret`), which never lands in a layer."
            ),
            "refs": [R["multiplatform"], R["secrets"]],
        },
    ],
    "analogy": (
        "A multi-stage build is like a restaurant kitchen and its dining room. "
        "The kitchen is full of knives, flour and hot ovens, but the plate that reaches the guest carries only the finished dish. "
        "You cook in one place and serve only what the guest needs. "
        "Where it breaks: in a restaurant, leftover tools are only untidy, while in an image every extra tool is something an attacker could use and a scanner must check."
    ),
    "diagram": SVG_D08,
    "diagram_caption": "The build stage installs packages; only the run stage ships, for both CPU types.",
    "worked": {
        "title": "Harden the hello-devops image",
        "steps": [
            {
                "say": "Start by looking at the Day 6 image: which user it runs as, and how big it is.",
                "code": (
                    "$ docker run --rm hello-devops:1.0.0 whoami\n"
                    "root\n"
                    "$ docker images hello-devops\n"
                    "IMAGE                ID             DISK USAGE   CONTENT SIZE   EXTRA\n"
                    "hello-devops:1.0.0   d1a0f297cfec        213MB         51.6MB"
                ),
                "lang": "console",
            },
            {
                "say": "Replace your Dockerfile with the multi-stage version from Files and rebuild with the same tag, so later days use the hardened image. The steps now carry stage names: `build` for the first stage, `stage-1` for the unnamed final one.",
                "code": (
                    "$ docker build --build-arg APP_VERSION=1.0.0 -t hello-devops:1.0.0 .\n"
                    " => [build 3/5] RUN python -m venv /venv                                4.2s\n"
                    " => [build 4/5] COPY requirements.txt .                                 0.0s\n"
                    " => [build 5/5] RUN pip install --no-cache-dir -r requirements.txt     44.4s\n"
                    " => [stage-1 3/5] COPY --from=build /venv /venv                         0.2s\n"
                    " => [stage-1 4/5] COPY app.py .                                         0.0s\n"
                    " => [stage-1 5/5] RUN useradd --uid 10001 --no-create-home appuser      0.1s\n"
                    " => exporting to image                                                  1.4s"
                ),
                "lang": "console",
            },
            {
                "say": "Check the user and the size again. The app now runs as appuser (uid 10001). The size barely moved, because this app compiles nothing; the win is a final stage that holds only the venv and app.py.",
                "code": (
                    "$ docker run --rm hello-devops:1.0.0 whoami\n"
                    "appuser\n"
                    "$ docker images hello-devops\n"
                    "IMAGE                ID             DISK USAGE   CONTENT SIZE   EXTRA\n"
                    "hello-devops:1.0.0   e310898d6c0f        217MB         51.8MB"
                ),
                "lang": "console",
            },
            {
                "say": "Start it and wait about 30 seconds for the first health check. Until then STATUS says (health: starting); after that it says (healthy).",
                "code": (
                    "$ docker run -d --name web -p 8000:8000 hello-devops:1.0.0\n"
                    "c3430ac5304685622653fa991a25b60911437e127137c1b895a67e8fb3053350\n"
                    "$ docker ps\n"
                    "CONTAINER ID   IMAGE                COMMAND                  CREATED              STATUS                        PORTS                    NAMES\n"
                    "c3430ac53046   hello-devops:1.0.0   \"gunicorn --bind 0.0…\"   About a minute ago   Up About a minute (healthy)   0.0.0.0:8000->8000/tcp   web"
                ),
                "lang": "console",
            },
            {
                "say": "Scan it with Trivy (output shortened). All 44 Debian findings had no fix yet on the day we ran this, so `--ignore-unfixed` drops them to zero. The five left sit in libraries that pip carries inside itself, not in your requirements. Your numbers will differ, because new CVEs appear every day.",
                "code": (
                    "$ trivy image --severity HIGH,CRITICAL hello-devops:1.0.0\n"
                    "hello-devops:1.0.0 (debian 13.7)\n"
                    "Total: 44 (HIGH: 44, CRITICAL: 0)\n"
                    "Python (python-pkg)\n"
                    "Total: 5 (HIGH: 5, CRITICAL: 0)\n"
                    "$ trivy image --severity HIGH,CRITICAL --ignore-unfixed hello-devops:1.0.0\n"
                    "│ hello-devops:1.0.0 (debian 13.7) │   debian   │  0 │\n"
                    "│ Python                           │ python-pkg │  5 │"
                ),
                "lang": "console",
            },
            {
                "say": "Look at a digest. `imagetools inspect` asks the registry about an image without pulling it. The base image has one digest for the whole set, and a variant for each CPU type. Writing `FROM python:3.14-slim@sha256:cd89...` would pin it.",
                "code": (
                    "$ docker buildx imagetools inspect python:3.14-slim | head -3\n"
                    "Name:      docker.io/library/python:3.14-slim\n"
                    "MediaType: application/vnd.oci.image.index.v1+json\n"
                    "Digest:    sha256:cd89c30eda26ee911a4611b18680086e0ea42e6f5f8cbe653d07fa7958c9cec8\n"
                    "$ docker buildx imagetools inspect python:3.14-slim | grep -E 'Platform: +linux/(amd64|arm64)'\n"
                    "  Platform:    linux/amd64\n"
                    "  Platform:    linux/arm64/v8"
                ),
                "lang": "console",
            },
        ],
    },
    "code": [
        {
            "lang": "dockerfile",
            "title": "Dockerfile (final: multi-stage, non-root)",
            "src": LAB_DOCKERFILE,
            "run": "docker build --build-arg APP_VERSION=1.0.0 -t hello-devops:1.0.0 . && docker run --rm -p 8000:8000 hello-devops:1.0.0",
        }
    ],
    "commands": [
        {"cmd": "docker build --build-arg APP_VERSION=1.0.0 -t hello-devops:1.0.0 .", "what": "Build the multi-stage image with a version stamped in."},
        {"cmd": "docker run --rm hello-devops:1.0.0 whoami", "what": "Show which user the container runs as."},
        {"cmd": "trivy image --severity HIGH,CRITICAL --ignore-unfixed hello-devops:1.0.0", "what": "Scan for serious vulnerabilities that already have a fix."},
        {"cmd": "docker scout quickview hello-devops:1.0.0", "what": "Docker Desktop's scanner: a summary of vulnerabilities and base image updates."},
        {"cmd": "export GH_USER=your-github-user", "what": "Save your GitHub user name, in lowercase, for the commands below."},
        {"cmd": "docker login ghcr.io -u \"$GH_USER\"", "what": "Log in to GHCR; paste your token when it asks for a password."},
        {"cmd": "docker tag hello-devops:1.0.0 ghcr.io/$GH_USER/hello-devops:1.0.0", "what": "Give the image its registry name."},
        {"cmd": "docker push ghcr.io/$GH_USER/hello-devops:1.0.0", "what": "Upload the image; the last line shows its digest."},
        {"cmd": "docker pull ghcr.io/$GH_USER/hello-devops@sha256:<digest>", "what": "Pull one exact image by its digest."},
        {"cmd": "docker buildx build --platform linux/amd64,linux/arm64 --build-arg APP_VERSION=1.0.0 -t ghcr.io/$GH_USER/hello-devops:1.0.0 --push .", "what": "Build for both CPU types and push them as one image."},
        {"cmd": "docker buildx imagetools inspect ghcr.io/$GH_USER/hello-devops:1.0.0", "what": "Show an image's digest and platforms straight from the registry."},
    ],
    "mistake": (
        "Putting a secret into the image with `COPY .env .`, `ENV API_KEY=...` or `ARG TOKEN`, even if a later step deletes it. "
        "Every layer and the image history ship with the image, so anyone who can pull it can read them. "
        "Pass secrets at run time, or use a build secret mount when a build step needs one."
    ),
    "real_world": (
        "At PayFlow, a fake payments company, CI builds each service image once, scans it, and pushes it to a private registry with the version and git commit as tags. "
        "Deploy files reference the image by digest, so production runs exactly what was tested. "
        "A scheduled job rebuilds images every week to pick up base image fixes, and the build fails on fixable critical findings."
    ),
    "task": {
        "title": "Publish hello-devops to GHCR for two CPU types",
        "steps": [
            "Create a GitHub personal access token (classic) with only the `write:packages` scope and a short expiry. GitHub's docs give the link `https://github.com/settings/tokens/new?scopes=write:packages` for this.",
            "Log in to ghcr.io with your GitHub user name and the token. Keep the token out of files and out of your shell history.",
            "Tag your local `hello-devops:1.0.0` with its GHCR name and push it. Copy the digest from the last line.",
            "Find the package on your GitHub profile under Packages, and check its visibility.",
            "Delete the local GHCR-tagged image, pull it back by digest, run it, and curl it.",
            "Build and push both CPU types in one command with `docker buildx build`.",
            "Check the pushed tag with `docker buildx imagetools inspect` and find both platforms.",
            "Scan the pushed image with `docker scout quickview` or `trivy image`, and write down the counts.",
            "Commit the multi-stage Dockerfile and push.",
        ],
        "hints": [
            "Add `--label org.opencontainers.image.source=https://github.com/<your-github-user>/hello-devops` to your build to link the package to your repo.",
            "If Docker says the builder cannot build several platforms, create one with `docker buildx create --name multi --driver docker-container --use`.",
            "On Day 12 a workflow pushes here. If it gets a permission error, add your repo under Manage Actions access in the package settings.",
        ],
        "done_when": "You are done when `docker buildx imagetools inspect ghcr.io/<your-github-user>/hello-devops:1.0.0` lists both linux/amd64 and linux/arm64.",
    },
    "explain_back": {
        "prompt": "Explain in 3 to 4 sentences what makes the final hello-devops image more production-ready than the Day 6 one. Mention the stages, the user, the health check and how you ship it.",
        "answer": (
            "The build has two stages: the first creates a venv and installs the packages, and the second copies only that venv and app.py onto a fresh slim base. "
            "The app runs as user 10001 instead of root, so a bug in the app gives an attacker fewer rights. "
            "A HEALTHCHECK lets Docker mark the container healthy or unhealthy. "
            "I scan it, push it to GHCR for amd64 and arm64, and deploy it by digest, so the exact tested image runs."
        ),
    },
    "recap": [
        "Multi-stage builds keep build tools out of the final image.",
        "Pick a small base image (slim, distroless or hardened) and rebuild often.",
        "Run as a numeric non-root user, and add a HEALTHCHECK.",
        "Scan with docker scout or trivy, and act first on findings that have a fix.",
        "Tags can move and digests cannot, so deploy by digest.",
        "Build linux/amd64 and linux/arm64 with buildx, and never bake secrets into layers.",
    ],
    "check": [
        {
            "q": "A Kotlin service needs a JDK and Gradle to build, but only a Java runtime to run. What does a multi-stage build give you?",
            "options": [
                "A faster JVM at run time",
                "A final image without the JDK and Gradle",
                "Automatic scanning of dependencies",
                "Builds for amd64 and arm64",
            ],
            "answer": 1,
            "why": "Only the last stage ships, so the compile tools stay behind in the build stage.",
        },
        {
            "q": "You pushed an image built on your Apple Silicon Mac. The cloud server logs `exec format error`. What fixes it?",
            "options": [
                "Run the container as root",
                "Pull it by digest instead of by tag",
                "Rebuild for linux/amd64 and linux/arm64, then push",
                "Add a HEALTHCHECK to the Dockerfile",
            ],
            "answer": 2,
            "why": "The server has an amd64 CPU and your image only had arm64 code, so it needs an amd64 variant.",
        },
        {
            "q": "A scan shows 40 HIGH findings in Debian packages, and none has a fixed version yet. What is a sensible next step?",
            "options": [
                "Track them, and rebuild when the base gets fixes",
                "Delete Debian packages from the image by hand",
                "Stop scanning, because the results are noisy",
                "Switch the container to run as root",
            ],
            "answer": 0,
            "why": "You cannot install a fix that does not exist; rebuild regularly so fixes arrive as soon as the base image has them.",
        },
    ],
    "interview": [
        {
            "q": "How do you make a container image more secure?",
            "a": (
                "Start from a small, trusted base image, such as slim, distroless or a hardened image, and rebuild often to pick up fixes. "
                "Use multi-stage builds, so compilers and build tools never ship. "
                "Run as a non-root user and give the container only what it needs. "
                "Scan images in CI and fail on serious findings that have a fix. "
                "Never put secrets in layers, and deploy by digest, so what you scanned is what runs."
            ),
        },
        {
            "q": "What is the difference between a tag and a digest?",
            "a": (
                "A tag is a human-friendly name like 1.0.0 or latest, and anyone with push rights can move it to a different image. "
                "A digest is the sha256 hash of the image's manifest, so it always means exactly the same content. "
                "Deploying by digest makes deploys repeatable and protects you from a tag that changed underneath you. "
                "Teams often keep both: a readable tag for people and a digest in deploy files."
            ),
        },
    ],
    "deeper": {
        "minutes": 12,
        "body": (
            "A multi-platform image is really a small index. "
            "Run `docker buildx imagetools inspect python:3.14-slim` and look at the top: the media type is an image index, with its own digest. "
            "Under Manifests it lists one entry per platform. On the day we checked, the list had eight platforms:\n\n"
            "- linux/amd64 and linux/386 for Intel and AMD CPUs\n"
            "- linux/arm64/v8, linux/arm/v7 and linux/arm/v5 for ARM CPUs\n"
            "- linux/ppc64le, linux/riscv64 and linux/s390x for other server CPUs\n\n"
            "You will also see entries marked `unknown/unknown`. "
            "Those are attestations: small records, added by the build tool, that describe how the image was built. Day 22 uses them.\n\n"
            "When you run `docker pull python:3.14-slim`, Docker reads the index and downloads only the variant for your CPU. "
            "So one tag works on your Mac and on an amd64 server. "
            "When you pin a digest, pin the index digest, so every platform still works.\n\n"
            "Emulation is the easy way to build the other platform, but it is slow for heavy builds. Two faster options exist:\n\n"
            "- Native builders: one builder per CPU type, such as an arm64 runner and an amd64 runner in CI.\n"
            "- Cross-compilation: languages like Go can compile for another CPU without emulation, inside a multi-stage build.\n\n"
            "If you want to try a hardened base, Docker's docs show the flow. "
            "Run `docker login dhi.io` with your Docker account, then pull an image from the [Docker Hardened Images catalog](https://docs.docker.com/dhi/). "
            "Runtime variants have no shell and run as non-root. "
            "So you build in a `-dev` variant, which has a shell and pip, and copy the venv into the runtime variant: the same two-stage pattern you used today. "
            "Two lines of our Dockerfile would change. `RUN useradd` needs a shell, so you would rely on the image's own non-root user. "
            "And the HEALTHCHECK would need the exec form, a JSON list, because its current form runs through a shell."
        ),
    },
    "sources": src("multistage", "best", "ghcr", "multiplatform"),
}

PART = {
    "part": 2,
    "title": "Docker",
    "intro": (
        "This part teaches you to package an app with everything it needs, so it runs the same on your Mac, in CI and in the cloud. "
        "You will run other people's containers, write a Dockerfile for hello-devops, add Redis with Docker Compose, and finish with a small, non-root image in a registry. "
        "Every later part ships the image you build here."
    ),
    "lessons": [D05, D06, D07, D08],
    "recap": [
        "A container is an isolated Linux process started from an image, sharing the host's kernel.",
        "`docker run -d --name x -p HOST:CONTAINER image` is the command you will type most.",
        "A Dockerfile builds an image in layers; order the steps so the cache saves time.",
        "Settings go in environment variables, so one image runs everywhere.",
        "Data lives in volumes, and containers on one network find each other by name.",
        "Compose runs a multi-container app from one compose.yaml.",
        "Production images are multi-stage, non-root, scanned and multi-platform.",
        "Push images to a registry such as GHCR, and deploy them by digest.",
    ],
    "flashcards": [
        {"front": "What does a container share with its host?", "back": "The kernel. A container is an isolated process, not a full operating system."},
        {"front": "What do namespaces and cgroups do?", "back": "Namespaces limit what a process can see; cgroups limit how much CPU and memory it can use."},
        {"front": "Read `-p 8080:80` out loud.", "back": "Port 8080 on my machine goes to port 80 inside the container."},
        {"front": "Why does Docker Desktop run a VM on a Mac?", "back": "Containers need a Linux kernel, and macOS does not have one."},
        {"front": "What makes Docker rebuild a layer?", "back": "A changed instruction or changed copied files; every later layer is rebuilt too."},
        {"front": "Why copy requirements.txt before app.py?", "back": "So code edits reuse the cached pip install layer."},
        {"front": "What does EXPOSE do?", "back": "It documents a port. It publishes nothing; `-p` does that."},
        {"front": "Why write CMD in exec form?", "back": "The app becomes process 1 and gets SIGTERM, so `docker stop` is fast and clean."},
        {"front": "Volume or bind mount for database files?", "back": "A named volume: Docker manages it and it outlives containers."},
        {"front": "How does web reach redis in Compose?", "back": "By the service name redis, through Docker's DNS on the project network."},
        {"front": "`docker compose down` vs `down -v`?", "back": "`down -v` also deletes named volumes and the data in them."},
        {"front": "Why `USER 10001` instead of `USER appuser`?", "back": "Kubernetes can only prove a numeric user is non-root."},
        {"front": "Tag vs digest?", "back": "A tag can move to another image; a digest always names one exact image."},
        {"front": "How do you build one image for Intel servers and Apple Silicon?", "back": "`docker buildx build --platform linux/amd64,linux/arm64 --push`."},
    ],
    "quiz": [
        {
            "q": "You ran `docker run -d --name api my-api:1.0` and the container exits right away. Which command shows why?",
            "options": ["docker logs api", "docker images", "docker pull my-api:1.0", "docker network ls"],
            "answer": 0,
            "why": "The logs hold what the app printed before it exited, usually including the error.",
        },
        {
            "q": "Which Dockerfile order gives the fastest rebuild after a code edit?",
            "options": [
                "COPY . . then RUN pip install",
                "COPY app.py, then requirements.txt, then RUN pip install",
                "COPY requirements.txt, RUN pip install, then COPY app.py",
                "RUN pip install first, then COPY everything",
            ],
            "answer": 2,
            "why": "The slow install sits above the code, so a code edit only rebuilds the last layer.",
        },
        {
            "q": "In compose.yaml, web has `depends_on` with `condition: service_healthy` for redis. What must the redis service have?",
            "options": ["A published port", "A bind mount", "A build section", "A healthcheck"],
            "answer": 3,
            "why": "service_healthy waits for a healthcheck to pass, so the dependency needs one.",
        },
        {
            "q": "Your team's image is 1.2 GB because it ships the compilers used to build it. What helps most?",
            "options": [
                "Splitting RUN steps into more lines",
                "A multi-stage build",
                "A longer, more precise tag",
                "Removing EXPOSE lines",
            ],
            "answer": 1,
            "why": "Compile in an earlier stage and copy only the results into a small final stage.",
        },
        {
            "q": "Which value of REDIS_HOST works for hello-devops when both services run in the same Compose project?",
            "options": ["localhost", "127.0.0.1", "redis", "0.0.0.0"],
            "answer": 2,
            "why": "Compose's network DNS resolves the service name redis; localhost would mean the web container itself.",
        },
        {
            "q": "You must deploy exactly the image that passed the tests last week, even if someone pushed since. What do you reference?",
            "options": ["The latest tag", "The image digest", "The 1.4 tag", "The Dockerfile in git"],
            "answer": 1,
            "why": "A digest names one exact image; tags, including version tags, can be moved.",
        },
        {
            "q": "Inside its container, an app listens on 127.0.0.1:8000. You run it with `-p 8000:8000`, but `curl localhost:8000` on your Mac gets no answer. Why?",
            "options": [
                "The app must listen on 0.0.0.0 inside the container",
                "Port 8000 is reserved by macOS for its own use",
                "curl cannot reach ports that Docker publishes",
                "The image needs EXPOSE 8000 before -p works",
            ],
            "answer": 0,
            "why": "127.0.0.1 inside a container is the container's own loopback; binding to 0.0.0.0 accepts traffic from outside it (Day 4).",
            "from": "Part 1",
        },
        {
            "q": "`docker stop` takes 10 seconds and the container shows `Exited (137)`. What happened?",
            "options": [
                "The app crashed with an error code of 137",
                "Docker ran out of memory while stopping",
                "The image was too large to stop quickly",
                "SIGTERM was ignored, so Docker sent SIGKILL",
            ],
            "answer": 3,
            "why": "137 is 128 + 9, and signal 9 is SIGKILL, which Docker sends when SIGTERM did not stop the process in time (Day 3).",
            "from": "Part 1",
        },
    ],
}

OUT.write_text(json.dumps(PART, ensure_ascii=False, indent=1) + "\n")
print(f"wrote {OUT}")
