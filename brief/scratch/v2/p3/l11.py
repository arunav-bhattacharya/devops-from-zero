from common import cap, join, lab, lines, ref, src, step, v1_step

C = lambda k: cap("d11", k)

SVG = (
    '<svg viewBox="0 0 560 262" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="The docker command on your Mac talks through a socket to Docker Engine inside a Linux VM; the engine starts containers, which share the VM\'s Linux kernel; -p 8080:80 connects localhost:8080 to the web container">'
    # VM outline
    '<line class="lnd" x1="168" y1="24" x2="552" y2="24"/><line class="lnd" x1="168" y1="252" x2="552" y2="252"/>'
    '<line class="lnd" x1="168" y1="24" x2="168" y2="252"/><line class="lnd" x1="552" y1="24" x2="552" y2="252"/>'
    '<text class="ts" x="360" y="246" font-size="11" text-anchor="middle">Linux VM (Docker Desktop)</text>'
    '<text class="ts" x="76" y="32" font-size="11" text-anchor="middle">your Mac</text>'
    # boxes
    '<rect class="bx" x="8" y="44" width="136" height="46" rx="10"/><text class="t" x="76" y="72" font-size="13" text-anchor="middle">docker CLI</text>'
    '<rect class="bx" x="8" y="110" width="136" height="46" rx="10"/><text class="t" x="76" y="138" font-size="13" text-anchor="middle">localhost:8080</text>'
    '<rect class="bxp" x="186" y="44" width="140" height="46" rx="10"/><text class="tk" x="256" y="72" font-size="13" text-anchor="middle">Docker Engine</text>'
    '<rect class="bxt" x="396" y="44" width="140" height="46" rx="10"/><text class="tk" x="466" y="72" font-size="13" text-anchor="middle">cache (redis)</text>'
    '<rect class="bxt" x="396" y="110" width="140" height="46" rx="10"/><text class="tk" x="466" y="138" font-size="13" text-anchor="middle">web (nginx)</text>'
    '<rect class="bxg" x="186" y="184" width="350" height="40" rx="10"/><text class="tk" x="361" y="209" font-size="13" text-anchor="middle">Linux kernel, shared by all</text>'
    # arrows
    '<line class="ln" x1="144" y1="67" x2="182" y2="67" marker-end="url(#ar)"/><text class="ts" x="163" y="104" font-size="11" text-anchor="middle">socket</text>'
    '<line class="ln" x1="326" y1="67" x2="392" y2="67" marker-end="url(#ar)"/><text class="ts" x="360" y="60" font-size="11" text-anchor="middle">starts</text>'
    '<line class="ln" x1="326" y1="86" x2="392" y2="122" marker-end="url(#ar)"/>'
    '<line class="ln" x1="144" y1="148" x2="392" y2="148" marker-end="url(#ar)"/><text class="ts" x="268" y="168" font-size="11" text-anchor="middle">-p 8080:80</text>'
    "</svg>"
)

LESSON = {
    "id": "d11",
    "title": "Containers: your first docker run",
    "minutes": 45,
    "goal": "By the end you can explain what a container is and how it differs from a VM, and run, inspect, stop and remove containers made from public images.",
    "guess": {
        "q": "You run `docker run -p 8080:80 nginx` on your Mac. Which kernel runs the nginx process?",
        "options": [
            "Its own Debian kernel, booted inside the container",
            "The macOS kernel, directly",
            "The Linux kernel of a small VM that Docker Desktop runs",
            "No kernel: Docker interprets the image like a JVM",
        ],
        "answer": 2,
        "why": "A container never boots a kernel of its own; it uses the host's Linux kernel. A Mac has no Linux kernel, so Docker Desktop runs one small Linux VM, and every container shares that VM's kernel.",
    },
    "terms": [
        {"term": "Image", "plain": "A read-only package of an app and everything it needs to run: files, libraries and settings."},
        {"term": "Container", "plain": "A running, isolated process started from an image."},
        {"term": "Kernel", "plain": "The core of an operating system. It runs processes, hands out memory and talks to the hardware."},
        {"term": "Namespace", "plain": "A Linux kernel feature that gives a process its own private view of processes, network, hostname or files."},
        {"term": "cgroup", "plain": "A Linux kernel feature (control group) that caps how much CPU and memory a group of processes can use."},
        {"term": "Docker Engine", "plain": "The background service that pulls images and creates, runs and stops containers."},
        {"term": "Port mapping", "plain": "A rule that sends traffic from a port on your computer to a port inside a container."},
        {"term": "Exit code", "plain": "The number a process returns when it ends. 0 means success; anything else means something went wrong."},
    ],
    "sections": [
        {
            "h": "The problem: it works on my machine",
            "body": (
                "Your code is only one part of what runs in production. The app also needs:\n\n"
                "- a language runtime, such as Python 3.14\n"
                "- libraries, such as Flask and gunicorn\n"
                "- system packages from the operating system, such as OpenSSL\n"
                "- settings, such as environment variables\n\n"
                "Your laptop has one mix of these. The CI server has another, and the production server a third. "
                "A test passes on your Mac with Python 3.14 and fails in CI, where the runner has Python 3.12. "
                "Nothing in your code changed. The setup around it did.\n\n"
                "Docker ships the setup together with the code. You build one package that holds the app and everything it needs. "
                "That exact package then runs on your Mac, on a CI runner and on a cloud server. On the Day 1 map, this is the package step.\n\n"
                "The package is called an **image**: your app, its files and its settings, frozen and read-only. "
                "A running copy of an image is a **container**. Today you run images other people built. On Day 13 you build your own."
            ),
            "refs": ref("c_container", "nana_crash"),
        },
        {
            "h": "A container is a process with blinkers and a budget",
            "body": (
                "A virtual machine (VM) pretends to be a whole computer. It has virtual hardware and boots a full operating system with its own kernel. "
                "The kernel is the core of an operating system: it starts processes, hands out memory and talks to the hardware. "
                "Booting all of that takes many seconds, and each VM holds on to its own share of memory.\n\n"
                "A container skips all of that. It is a normal Linux process, the same kind you listed with `ps` on Day 6. "
                "The kernel just gives it two extra things:\n\n"
                "- Namespaces give the process a private view of the system: its own process list, network, hostname and files.\n"
                "- cgroups (control groups) give it a budget: a cap on how much CPU and memory it may use.\n\n"
                "So a container is a process with blinkers (namespaces) and a budget (cgroups). You can watch the blinkers work. "
                "`docker run --rm alpine ps` lists exactly one process, `ps` itself, running as PID 1. "
                "The machine runs hundreds of processes, and the container sees none of them.\n\n"
                "No second kernel has to boot, so a container starts in about a second. The price is that every container on a host shares one kernel. "
                "A kernel bug can affect all of them. A container can also only run programs built for that kernel and that CPU."
            ),
            "refs": ref("jvns_container", "jvns_zine"),
        },
        {
            "h": "On a Mac, Docker runs a small Linux VM",
            "body": (
                "macOS has its own kernel, and it is not Linux. So Docker Desktop starts one small Linux VM in the background, and every container you run lives inside it. "
                "Three pieces work together:\n\n"
                "1. The `docker` command runs on your Mac. It is only a client that sends requests.\n"
                "2. Docker Engine, a background program called `dockerd`, runs inside the VM. It pulls images and creates, starts and stops containers.\n"
                "3. The VM's Linux kernel runs the container processes.\n\n"
                "The client reaches the engine through a socket, the connection you set up on Day 2. "
                "Run `docker version` and it prints both halves: a Client section for the command on your Mac and a Server section that says `linux/arm64`.\n\n"
                "That `arm64` is your CPU type, which Linux calls `aarch64`. Most cloud servers use amd64, also called `x86_64`. "
                "Popular images carry a variant for each CPU, and Docker picks the one that matches yours. "
                "An amd64-only image still runs on your Mac through emulation, only slower. "
                "On an amd64 server, an image with only arm64 code fails with `exec format error`. "
                "Day 12 shows how one image name can hold both variants.\n\n"
                "Docker Desktop is free for personal use, education and small businesses. Companies with more than 250 employees or more than $10 million in yearly revenue need a paid subscription. "
                "Sign in with a free Docker account anyway: Docker Hub then lets you pull 200 images every 6 hours instead of 100."
            ),
            "refs": ref("mac_install", "pulls"),
        },
        {
            "h": "Images and containers: a class and its objects",
            "body": (
                "An image and a container relate like a class and an object in Kotlin. The image is the class, a read-only definition. "
                "A container is an object made from it, with its own state. You can start ten containers from one image, and they do not affect each other.\n\n"
                "Each container gets a thin writable layer on top of its image, and every file the app writes lands there. "
                "Remove the container and that layer goes with it. The image stays exactly as it was. Day 12 opens an image up and shows how the layers stack.\n\n"
                "Images live in a registry, a server that stores images and hands them out. Docker Hub is the default one. "
                "When you run an image you do not have yet, Docker pulls (downloads) it first. "
                "An image name looks like `redis:8-alpine`: a name, a colon, and a tag that names a version. "
                "Leave the tag out and Docker uses `latest`, which is only a default label and does not promise the newest version."
            ),
            "refs": ref("c_image", "c_registry"),
        },
        {
            "h": "The docker run command, flag by flag",
            "body": (
                "`docker run` creates a container from an image and starts it. Its shape is `docker run [options] image [command]`. "
                "Take `docker run -d --name web -p 8080:80 -e TZ=UTC nginx`. Each option changes one thing:\n\n"
                "- `-d` (detached) runs it in the background and prints the container ID.\n"
                "- `--name web` names it, so later commands can say `web` instead of an ID.\n"
                "- `-p 8080:80` publishes a port, explained in the next section.\n"
                "- `-e TZ=UTC` sets an environment variable inside the container.\n"
                "- `--rm` deletes the container when it stops, which suits one-off commands.\n"
                "- `-it` connects your keyboard and a terminal, so you can type into a shell.\n\n"
                "Anything after the image name replaces the image's default command. `docker run --rm alpine uname -m` runs `uname -m` instead of Alpine's shell. "
                "`docker run -it --rm ubuntu:24.04 bash` gives you the Ubuntu practice box from Part 1.\n\n"
                "Once a container runs, three commands answer most questions:\n\n"
                "- `docker ps` lists running containers.\n"
                "- `docker logs web` shows what the main process printed, and `-f` keeps following it.\n"
                "- `docker exec web <command>` runs an extra command inside the running container. `docker exec -it web sh` opens a shell there."
            ),
            "refs": ref("ref_run", "ref_exec"),
        },
        {
            "h": "Port mapping, explained",
            "body": (
                "Each container has its own network namespace, and with it its own set of ports. Inside its container, nginx listens on port 80, where nothing on your Mac can reach it yet.\n\n"
                "`-p 8080:80` connects the two. Read it as host first, then container: traffic to port 8080 on your Mac goes to port 80 in the container. "
                "Most people get this order backwards at first, so say it out loud a few times. `docker ps` shows the rule in its PORTS column as `0.0.0.0:8080->80/tcp`.\n\n"
                "A few rules follow from this:\n\n"
                "- Two containers can both use port 80 inside, because each has its own namespace.\n"
                "- A port on your Mac can belong to only one container at a time.\n"
                "- The app inside must listen on `0.0.0.0`, as you saw on Day 8. An app bound to `127.0.0.1` only hears its own container.\n\n"
                "That `0.0.0.0` in the PORTS column means Docker publishes the port on every network address of your Mac, so other devices on your Wi-Fi might reach it. "
                "On a laptop, `-p 127.0.0.1:8080:80` is the safer habit, because it keeps the port private to your Mac."
            ),
            "refs": ref("c_ports", "port_pub"),
        },
        {
            "h": "The container lifecycle",
            "body": (
                "A container moves through a few states:\n\n"
                "1. Created: Docker has set it up but not started its process (`docker create`).\n"
                "2. Running: its main process is alive.\n"
                "3. Paused: the kernel has frozen its processes (`docker pause`). You will rarely need this.\n"
                "4. Exited: the main process ended, by itself or because you stopped it.\n"
                "5. Removed: `docker rm` deleted it and its writable layer.\n\n"
                "A container lives exactly as long as its main process, PID 1. When that process ends, the container exits, and its exit code tells you how. "
                "0 means success. `docker ps -a` shows any other number, as in `Exited (3)`, and `docker logs` still shows what the process printed before it died.\n\n"
                "`docker stop` sends SIGTERM to PID 1, waits 10 seconds, then sends SIGKILL. You met these signals on Day 6, and Kubernetes stops containers the same way. "
                "A process killed by SIGKILL exits with 137, which is 128 plus 9, the number of SIGKILL. "
                "In the worked example, `sleep` runs as PID 1, ignores SIGTERM and ends with exactly that code after 10 seconds. Day 13 explains why.\n\n"
                "Stopping deletes nothing. An exited container keeps its files, and `docker start` runs it again. Only `docker rm` throws it away."
            ),
            "refs": ref("ref_stop", "nana_full"),
        },
    ],
    "analogy": (
        "A container is like an apartment in a big building. Each apartment has its own front door, address and mailbox, so the people inside cannot see their neighbours: those are the namespaces. "
        "Each one also has its own meters for water and power, with a limit: those are the cgroups. "
        "All apartments stand on one foundation and share the building's pipes, which is the kernel. "
        "The picture fails on speed. Nobody builds an apartment in one second, and Docker builds a container that fast because nothing new has to be built, only fenced off."
    ),
    "diagram": SVG,
    "diagram_caption": "The docker command talks to Docker Engine in a Linux VM; every container shares that VM's kernel.",
    "worked": {
        "title": "Run nginx, look inside, follow its life",
        "steps": [
            step("Start nginx in the background. Docker does not have the image yet, so it pulls it from Docker Hub first. The long line at the end is the new container's ID.",
                 v1_step("d05", 0)),
            step("Check that it runs. Read the PORTS column from left to right: port 8080 on every address of your Mac goes to port 80 in the container.",
                 v1_step("d05", 1)),
            step("Send a request through the mapped port, then read the last log line. nginx writes each request to its standard output, and `docker logs` shows that output. The address at the start will differ on your Mac.",
                 join(C("curl"), C("logs"))),
            step("`docker exec` runs a command inside the running container. Even on a Mac, the container sees a Linux system, here Debian. The second command lists the files nginx serves.",
                 join(C("osrel"), C("ls"))),
            step("Stop it, find it in the list of all containers, then remove it. `docker stop` sent SIGTERM, so nginx shut down cleanly and exited with code 0.",
                 v1_step("d05", 4)),
            step("Now walk one container through every state. `sleep 300` is the main process here. Notice how long `docker stop` takes: `sleep` ignores SIGTERM, so Docker waits the full 10 seconds and then sends SIGKILL, hence exit code 137.",
                 C("lifecycle")),
            step("A process that fails leaves its exit code behind. This one prints a line and exits with 3. The container is gone from `docker ps`, but `docker ps -a` and `docker logs` still tell you what happened. Remove it with `docker rm oops` when you are done.",
                 join(C("oops"), C("oops_ps"), C("oops_logs"))),
        ],
    },
    "code": [
        {
            "lang": "bash",
            "title": "check-docker.sh (keep it in ~/code, outside the repo)",
            "src": (
                "#!/usr/bin/env bash\n"
                "# Checks that Docker works and shows which CPU type your containers use.\n"
                "set -euo pipefail\n\n"
                "echo \"Docker client and server:\"\n"
                "docker version --format 'client {{.Client.Version}}, server {{.Server.Version}} ({{.Server.Os}}/{{.Server.Arch}})'\n\n"
                "echo \"CPU type inside a container:\"\n"
                "docker run --rm alpine uname -m\n\n"
                "echo \"Processes a container can see:\"\n"
                "docker run --rm alpine ps\n\n"
                "echo \"Containers on this machine (running and stopped):\"\n"
                "docker ps -a --format '{{.Names}}  {{.Image}}  {{.Status}}'"
            ),
            "run": "bash check-docker.sh",
        }
    ],
    "commands": [
        {"cmd": "docker run -d --name web -p 8080:80 nginx", "what": "Start nginx in the background, named web, with Mac port 8080 sent to container port 80."},
        {"cmd": "docker run -it --rm ubuntu:24.04 bash", "what": "Open an interactive shell in a throwaway Ubuntu container (type exit to leave)."},
        {"cmd": "docker ps", "what": "List running containers."},
        {"cmd": "docker ps -a", "what": "List all containers, including stopped ones, with their exit codes."},
        {"cmd": "docker logs --tail 20 -f web", "what": "Show the last 20 lines of a container's output and keep following it (Ctrl+C to quit)."},
        {"cmd": "docker exec -it web sh", "what": "Open a shell inside a running container."},
        {"cmd": "docker stop web", "what": "Stop a container: SIGTERM first, SIGKILL after 10 seconds."},
        {"cmd": "docker start web", "what": "Start a stopped container again, with its files intact."},
        {"cmd": "docker rm -f web", "what": "Delete a container and its writable layer; -f stops it first if it runs."},
        {"cmd": "docker inspect -f '{{.State.Status}} {{.State.ExitCode}}' web", "what": "Show one container's state and last exit code."},
        {"cmd": "docker images", "what": "List the images stored on your machine."},
        {"cmd": "docker pull redis:8-alpine", "what": "Download an image without running it."},
        {"cmd": "docker stats --no-stream", "what": "Show CPU and memory use of running containers once."},
        {"cmd": "docker version", "what": "Show the client on your Mac and the engine in the VM, with their CPU types."},
    ],
    "mistake": (
        "The most common slip is writing the port mapping backwards, such as `-p 80:8080` for an app that listens on port 80 inside. "
        "The rule is `-p HOST:CONTAINER`: the left number is on your Mac, and the right number is where the app listens in the container. "
        "If curl gets no answer, run `docker ps` and read the PORTS column from left to right."
    ),
    "real_world": (
        "At PayFlow, a made-up payments company, laptops, CI runners and production all run the same images. "
        "A new engineer starts Postgres and Redis with `docker run` on day one instead of installing them by hand. "
        "When a bug shows up only in production, engineers pull the exact image tag that production runs and reproduce the bug locally."
    ),
    "task": {
        "title": "Run Redis and follow a container's life",
        "steps": [
            "Pull `redis:8-alpine` and list your images. Note its size.",
            "Start it in the background with the name `cache`. Skip `-p`: you will talk to Redis from inside the container.",
            "Use `docker exec` to run `redis-cli ping`, then store a value with `redis-cli SET color blue` and read it back with `GET`.",
            "Stop the container, start it again with `docker start`, and read the key. Is it still there?",
            "Remove the container, run a new one with the same name, and read the key again.",
            "Start an nginx on Mac port 8081, bound to 127.0.0.1 only, with an env var of your choice. Find the variable inside with `docker exec` and `env`.",
            "Run a container that exits with code 7 on purpose, then find that code with `docker ps -a`.",
            "Run `check-docker.sh` from the Files section and note which CPU type your containers use.",
            "Clean up: remove every container you created, then check that `docker ps -a` no longer lists them.",
        ],
        "hints": [
            "`docker exec cache redis-cli GET color` runs one command inside the running container.",
            "A stopped container keeps its files; a removed one does not. Day 14 shows how to keep data on purpose.",
            "`sh -c 'exit 7'` as the command makes a container exit with code 7.",
        ],
        "done_when": "You are done when you can show that the key survives `docker stop` and `docker start`, but is gone after `docker rm` and a new `docker run`.",
    },
    "explain_back": {
        "prompt": "Explain to a teammate what happens when you type `docker run -d -p 8080:80 nginx` on a Mac, in 3 to 4 sentences. Mention the image, the registry, the Linux VM, namespaces and the port mapping.",
        "answer": (
            "Docker looks for the nginx image on my machine and, if it is missing, pulls it from Docker Hub, the default registry. "
            "Docker Engine then starts a container inside the small Linux VM that Docker Desktop runs, because containers need a Linux kernel. "
            "The container is just an nginx process that namespaces fence off and cgroups can limit. "
            "The `-d` flag runs it in the background, and `-p 8080:80` sends traffic from port 8080 on my Mac to port 80 inside the container, where nginx listens."
        ),
    },
    "recap": [
        "A container is an isolated Linux process made from an image, and it shares the host's kernel.",
        "Namespaces decide what a process can see; cgroups decide how much CPU and memory it can use.",
        "On a Mac, Docker Desktop runs one Linux VM, and the docker command talks to the engine inside it.",
        "Image is to container as class is to object: one image, many independent containers.",
        "`-p HOST:CONTAINER` publishes a port; `-p 127.0.0.1:8080:80` keeps it private to your Mac.",
        "`docker stop` sends SIGTERM, then SIGKILL after 10 seconds; exit code 137 means the process was killed.",
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
            "q": "A batch job container shows `Exited (137)` after someone ran `docker stop` on it. What does that tell you?",
            "options": [
                "The job ignored SIGTERM and was killed with SIGKILL",
                "The job finished its work and exited normally",
                "Docker ran out of disk space while stopping it",
                "The image was built for a different CPU type",
            ],
            "answer": 0,
            "why": "137 is 128 plus 9, and signal 9 is SIGKILL, which Docker sends when SIGTERM did not end the process within 10 seconds.",
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
                "If the process is still running after the wait, Docker sends SIGKILL, which ends it at once and can lose work; the exit code is then 137. "
                "Kubernetes stops pods the same way, so the same SIGTERM handling protects you in both places."
            ),
        },
        {
            "q": "Why does an image built on an Apple Silicon Mac sometimes fail on a cloud server?",
            "a": (
                "Containers run on the host's kernel and CPU, so the code inside must match the server's CPU type. "
                "A Mac builds arm64 code by default, while most cloud servers are amd64. "
                "If the image only holds arm64 code, the server fails with `exec format error`. "
                "The fix is a multi-platform image that holds a variant for each CPU, which `docker buildx build --platform linux/amd64,linux/arm64` creates."
            ),
        },
    ],
    "deeper": {
        "minutes": 12,
        "body": (
            "Three small experiments let you watch namespaces, cgroups and CPU types at work.\n\n"
            "Start with the process namespace. Run `docker run --rm alpine ps`. The output lists exactly one process: `ps` itself, as PID 1. "
            "Your Mac and the Linux VM run hundreds of processes, but the container cannot see any of them. "
            "Now run `docker run --rm alpine hostname`. You get a random-looking name such as `89851d1cc476`, the container's short ID. "
            "The container has its own hostname namespace too. "
            "Then `docker run --rm alpine ip addr` shows a third namespace: the container has its own loopback and its own `eth0` with a private address such as `172.17.0.3`.\n\n"
            "For cgroups, start Redis with a memory limit: `docker run -d --name capped -m 64m redis:8-alpine`. "
            "Then run `docker stats --no-stream capped`. When we ran it, the MEM USAGE / LIMIT column said `8.633MiB / 64MiB`. "
            "If Redis tried to use more than 64 MB, the kernel would stop it. Remove it with `docker rm -f capped`. "
            "The Kubernetes memory limits on Day 35 use this same kernel feature.\n\n"
            "For CPU types, run `docker run --rm --platform linux/amd64 alpine uname -m` on your Mac. It prints `x86_64`. "
            "The container really runs amd64 code, translated as it runs by an emulator inside Docker Desktop. "
            "That is fine for a quick test and too slow for heavy work. "
            "Without an emulator, the same trick fails. On an amd64 Linux server with no emulator installed, `docker run --platform linux/arm64 alpine uname -m` printed `exec /bin/uname: exec format error`. "
            "That is the exact error a server shows when someone ships an arm64-only image to it.\n\n"
            "Docker Desktop has two settings worth knowing here. Under Settings, General, you can choose the virtual machine manager. "
            "Another setting uses Apple's Rosetta to speed up amd64 emulation. "
            "Docker Desktop is also not your only choice. OrbStack and Colima run a Linux VM too and give you the same `docker` command, so this course works with them as well. "
            "For a friendly tour of the kernel features behind all this, read [Julia Evans' post on containers](https://jvns.ca/blog/2016/10/10/what-even-is-a-container/)."
        ),
    },
    "sources": src("c_container", "ref_run", "mac_install", "jvns_container"),
}
