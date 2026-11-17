"""Fifth pass (book voice) for d17."""
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from common import load, apply, save

path, P, L, OL = load(5, "d17")
new = {}

new["goal"] = r"""By the end you can explain what a container is and how it differs from a VM, and run, inspect, stop and remove containers made from public images."""

new["opening"] = r"""Picture cooking your best dish for a friend's party. At home it comes out perfect every time. At your friend's house the oven runs hotter, there is no fresh garlic, and the salt is a different kind. The dish fails, and you stand in their kitchen saying, "But it works at home."

Software has the same problem, and it is easy to miss, because the code itself never changed. Everything around it did. Last time, our Python helper learned to talk to GitHub and AWS, but every machine that runs it still needs the right Python and packages first. In this lesson, we'll pack an app like a lunchbox: the meal plus its own fork, salt and napkin, sealed so it opens the same way anywhere. You'll run your first boxes, look inside them, and follow one from start to finish.

Before we start, make a guess, and keep it in mind."""

new["guess_q"] = r"""The kernel is the core of an operating system, the part that runs every program. You run `docker run -p 8080:80 nginx` (a web server) on your Mac. Which kernel runs the nginx process?"""
new["guess_why"] = r"""A container never boots a kernel of its own; it uses the Linux kernel of the machine it runs on. A Mac has no Linux kernel, so Docker Desktop runs one small Linux VM (a pretend computer), and every container shares that VM's kernel."""

new["terms"] = {
    "Image": "A read-only package of an app and everything it needs to run: files, ready-made code and settings.",
    "Container": "A running program started from an image and fenced off from the rest of the computer.",
    "Kernel": "The core of an operating system. It runs programs, hands out memory and talks to the hardware.",
    "Namespace": "A Linux kernel feature that gives a program its own private view of other programs, the network, its name and its files.",
    "cgroup": "A Linux kernel feature (control group) that caps how much processor time and memory a group of programs can use.",
    "Docker Engine": "The background program that downloads images and creates, runs and stops containers.",
    "Port mapping": "A rule that sends traffic from a port (a numbered door) on your computer to a port inside a container.",
    "Exit code": "The number a program hands back when it ends. 0 means success; anything else means something went wrong.",
}

S = []
S.append(("It works in my kitchen", r"""Your code is only one part of what runs in production, the real servers your users reach. The app also needs:

- a language runtime, the program that runs your code, such as Python 3.14
- libraries, ready-made code such as Flask and gunicorn
- system packages from the operating system, such as OpenSSL
- settings, such as environment variables

That is the kitchen around the dish. Your laptop has one mix of these. The CI server, which runs your tests on every change, has another, and the production server a third. So a test can pass on your Mac with Python 3.14 and fail in CI, where the runner (the CI machine) has Python 3.12. Nobody touched the code.

Docker ships the kitchen together with the dish. You build one package that holds the app and everything it needs, and that exact package runs on your Mac, on a CI runner and on a cloud server. On the Day 1 map, this is the package step.

The package is called an image: your app, its files and its settings, frozen and read-only, like a lunchbox packed and sealed. A running copy of an image is a container, the lunchbox opened and in use. Today you run images other people built. On Day 19 you build your own.

So what is actually running when a container runs? Less than you might expect."""))

S.append(("A container is a program with walls and a budget", r"""The older way to give an app a clean kitchen of its own is a virtual machine (VM). A VM pretends to be a whole computer. It has virtual hardware and boots a full operating system with its own kernel. The kernel is the core of an operating system: it starts processes (running programs), hands out memory and talks to the hardware. Booting all of that takes many seconds, and each VM holds on to its own share of memory.

A container has none of that. It is a normal Linux process, the same kind you listed with `ps` on Day 6. The kernel gives it two extra things:

- Namespaces give the process a private view of the system: its own process list, network, hostname (the machine's name) and files.
- cgroups (control groups) give it a budget: a cap on CPU and memory. Past the memory cap, the kernel kills it.

Namespaces work like the walls of a lunchbox: the food inside can't see the other boxes in the fridge. You can watch them work with Alpine, a tiny Linux image. The command `docker run --rm alpine ps` lists a single process, `ps` itself, running as PID 1. A PID is the number Linux gives each process, and 1 goes to the first one (Day 6). The machine runs hundreds of processes, and the container sees none of them. In the same way, `docker run --rm alpine ls /` lists Alpine's own folders. Those files come from the image, and none of the VM's files show up.

No second kernel has to boot, so a container starts in about a second. You pay for that speed by sharing. Every container on a host (the machine it runs on) uses the same kernel, like lunches that all go through one office microwave. A kernel bug can affect all of them. A container can also only run programs built for that kernel and that CPU, the computer's processor.

That raises a question for Mac users, because a Mac has no Linux kernel at all."""))

S.append(("On a Mac, Docker quietly runs a small Linux VM", r"""macOS has its own kernel, and it is not Linux. So Docker Desktop, the Mac app that installs Docker, starts one small Linux VM in the background, and every container you run lives inside it. Three pieces work together:

1. The `docker` command runs on your Mac. It is only a client: it sends requests and shows the answers.
2. Docker Engine, a background program called `dockerd`, runs inside the VM. It pulls (downloads) images and creates, starts and stops containers.
3. The VM's Linux kernel runs the container processes.

The client reaches the engine through a socket, the connection you set up on Day 2. Run `docker version` and it prints both halves: a Client section for the command on your Mac and a Server section that says `linux/arm64`.

That `arm64` is your CPU type, which Linux calls `aarch64`. Most cloud servers use amd64, also called `x86_64`. A program is built for one CPU type, the way a recipe is written in one language. Popular images carry a variant for each CPU, and Docker picks the one that matches yours. An amd64-only image still runs on your Mac through emulation (software that translates the code as it runs), only slower. On an amd64 server, an image with only arm64 code fails with `exec format error`. Day 18 shows how one image name can hold both variants.

Docker Desktop is free for personal use, education and small businesses. Companies with more than 250 employees or more than $10 million in yearly revenue need a paid subscription. Sign in with a free Docker account anyway: Docker Hub, the public store of images, then lets you pull 200 images every 6 hours instead of 100.

The machinery is in place. Now for the two words you'll use every day: image and container."""))

S.append(("Images and containers: the sealed box and the opened one", r"""Picture a shop that sells one kind of sealed lunchbox. Every box is packed from the same list, and ten people can each open one without touching anyone else's lunch. An image is the sealed, read-only box. A container is one opened copy, with its own state. You can start ten containers from one image, and they do not affect each other.

Each container gets a thin writable layer on top of its image, and every file the app writes lands there. It is the ketchup you add after opening: it belongs to your copy only. Remove the container and that layer goes with it. The image itself never changes. Day 18 opens an image up and shows how the layers stack.

Images live in a registry, a server that stores images and hands them out, like the shop. Docker Hub is the default one. When you run an image you do not have yet, Docker pulls it first. An image name looks like `redis:8-alpine`: a name, a colon, and a tag that names a version. Leave the tag out and Docker uses `latest`, which is only a default label and does not promise the newest version.

Put together, `docker run nginx` does five things, in this order:

1. The `docker` command on your Mac sends the request to Docker Engine in the VM.
2. The engine checks whether it already has the image, and pulls it if not.
3. It puts a fresh writable layer on top of the image's files. That merged folder tree becomes the container's `/`, its top folder.
4. It asks the kernel for new namespaces and a cgroup.
5. It starts the image's default command inside them, as PID 1. For nginx that is the nginx web server, for Alpine the shell `/bin/sh`, a program that reads typed commands.

The engine hands steps 3 to 5 to two helper programs, containerd and runc. Their names show up in error messages, as the next section shows."""))

S.append(("The docker run command, one option at a time", r"""`docker run` creates a container from an image and starts it. Its shape is `docker run [options] image [command]`. Take `docker run -d --name web -p 8080:80 -e TZ=UTC nginx`. Each option changes one thing:

- `-d` (detached) runs it in the background and prints its ID, instead of tying your terminal to the app's output.
- `--name web` names it, so later commands can say `web` instead of an ID.
- `-p 8080:80` publishes a port, explained in the next section.
- `-e TZ=UTC` sets an environment variable (a named setting) inside the container.
- `--rm` deletes the container when it stops, so one-off runs do not pile up in `docker ps -a`.
- `-it` connects your keyboard and a terminal, so you can type into a shell.

Anything after the image name replaces the image's default command. `docker run --rm alpine uname -m` runs `uname -m` instead of Alpine's shell. `docker run -it --rm ubuntu:24.04 bash` gives you the Ubuntu practice box from Part 1.

Now a run that fails in public. The program you name must exist inside the image, because the container sees only the image's files. Alpine has no bash, so `docker run --rm alpine bash` fails. The error says `runc create failed` and ends with `executable file not found in $PATH`. That's runc, one of the helpers from the last section, telling you it searched the image's `$PATH` folders (Day 7) and found no `bash`.

Once a container runs, three commands answer most questions:

- `docker ps` lists running containers.
- `docker logs web` shows what the main process printed, and `-f` keeps following it.
- `docker exec web <command>` runs an extra command inside the running container. `docker exec -it web sh` opens a shell there.

The nginx in that example listens on port 80. Yet you reach it on 8080. Why the two numbers?"""))

S.append(("Port mapping: two numbers, read from your side", r"""A port is a numbered door that a program listens behind, like an apartment number in a building (Part 3). Each container has its own network namespace, and with it its own set of ports: a building of its own. Inside its container, nginx listens on port 80, where nothing on your Mac can reach it yet.

`-p 8080:80` connects the two. Read it as host first, then container: traffic to port 8080 on your Mac goes to port 80 in the container. Docker Desktop carries that traffic into the VM, and the engine forwards it to the container's own network address. Most people get this order backwards at first, so say it out loud a few times. `docker ps` shows the rule in its PORTS column as `0.0.0.0:8080->80/tcp`.

**The left number is on your Mac. The right number is where the app listens.**

A few rules follow from this:

- Two containers can both use port 80 inside, because each has its own namespace.
- A port on your Mac can belong to only one container at a time.
- The app inside must listen on `0.0.0.0`, meaning every address it has (Day 10). Forwarded traffic arrives at the container's address, never at its `127.0.0.1`, the address that means "this machine only".

That `0.0.0.0` in the PORTS column means Docker publishes the port on every network address of your Mac, so other devices on your Wi-Fi might reach it. On a laptop, `-p 127.0.0.1:8080:80` is the safer habit, because it keeps the port private to your Mac.

You can start a container and reach it now. What happens when it ends?"""))

S.append(("The life of a container, from created to removed", r"""A container moves through a few states:

1. Created: Docker has set it up but not started its process (`docker create`).
2. Running: its main process is alive.
3. Paused: the kernel has frozen its processes (`docker pause`). You will rarely need this.
4. Exited: the main process ended, by itself or because you stopped it.
5. Removed: `docker rm` deleted it and its writable layer.

A container lives exactly as long as its main process, PID 1. That follows from what a container is: when PID 1 ends, the kernel also ends every other process in its namespace. So the container exits, and the exit code of PID 1 tells you how. 0 means success. `docker ps -a` shows any other number, as in `Exited (3)`, and `docker logs` still shows what the process printed before it died.

**A container lives as long as its main process. Watch PID 1.**

`docker stop` sends SIGTERM to PID 1, waits 10 seconds, then sends SIGKILL. You met these signals on Day 6: SIGTERM politely asks a program to finish, and SIGKILL ends it at once. Kubernetes, which runs containers across many machines, stops containers the same way. A process killed by SIGKILL exits with 137, which is 128 plus 9, the number of SIGKILL. In the worked example, `sleep` runs as PID 1 and ignores SIGTERM, for reasons Day 19 explains, so it ends with that code after 10 seconds.

Stopping deletes nothing. An exited container keeps its files, and `docker start` runs it again. Only `docker rm` throws it away.

That is today's limit: whatever a container writes lives only in its own thin layer, and `docker rm` takes it away (Day 20 keeps data on purpose). Every image you ran was also built by someone else. Next, we open one up to see how it is made."""))
new["sections"] = S

new["drop"] = ["analogy", "mistake"]
new["real_world"] = r"""When a bug shows up only in production, an engineer pulls the exact image tag that production runs and reproduces the bug on a laptop. That works because laptops, CI runners and production all run the same images. New engineers also start databases such as Postgres and Redis on their first day with `docker run`, instead of installing them by hand."""

new["diagram_caption"] = "The docker command talks to Docker Engine in a Linux VM; every container shares that VM's kernel."

new["worked"] = [
    r"""Start nginx in the background. Docker does not have the image yet, so it pulls it from Docker Hub first. The long line at the end is the new container's ID.""",
    r"""Check that it runs. Read the PORTS column from left to right: port 8080 on every address of your Mac goes to port 80 in the container.""",
    r"""Send a request through the mapped port with curl, then read the last log line. The nginx server writes each request to its standard output (stdout, its normal output), and `docker logs` shows that output. The address at the start will differ on your Mac.""",
    r"""`docker exec` runs a command inside the running container. Even on a Mac, the container sees a Linux system, here Debian. The second command lists the files nginx serves.""",
    r"""Stop it, find it in the list of all containers, then remove it. `docker stop` sent SIGTERM, so nginx shut down cleanly and exited with code 0.""",
    r"""Now walk one container through every state. `sleep 300` is the main process here. Notice how long `docker stop` takes: `sleep` ignores SIGTERM, so Docker waits the full 10 seconds and then sends SIGKILL, hence exit code 137.""",
    r"""A process that fails leaves its exit code behind. This one prints a line and exits with 3. The container is gone from `docker ps`, but `docker ps -a` and `docker logs` still tell you what happened. Remove it with `docker rm oops` when you are done.""",
]

new["task"] = {
    "steps": [
        r"""Pull `redis:8-alpine` (Redis is a small database that keeps data in memory) and list your images. Note its size.""",
        r"""Start it in the background with the name `cache`. Skip `-p`: you will talk to Redis from inside the container.""",
        r"""Use `docker exec` to run `redis-cli ping`, then store a value with `redis-cli SET color blue` and read it back with `GET`.""",
        r"""Stop the container, start it again with `docker start`, and read the key. Is it still there?""",
        r"""Remove the container, run a new one with the same name, and read the key again.""",
        r"""Start an nginx on Mac port 8081, bound to 127.0.0.1 only, with an environment variable of your choice. Find the variable inside with `docker exec` and `env`.""",
        r"""Run a container that exits with code 7 on purpose, then find that code with `docker ps -a`.""",
        r"""Run `check-docker.sh` from the Files section and note which CPU type your containers use.""",
        r"""Clean up: remove every container you created, then check that `docker ps -a` no longer lists them.""",
    ],
    "hints": [
        r"""`docker exec cache redis-cli GET color` runs one command inside the running container.""",
        r"""A stopped container keeps its files; a removed one does not. Day 20 shows how to keep data on purpose.""",
        r"""`sh -c 'exit 7'` as the command makes a container exit with code 7.""",
    ],
    "done_when": r"""You are done when you can show that the key survives `docker stop` and `docker start`, but is gone after `docker rm` and a new `docker run`.""",
}

new["explain_back"] = {
    "prompt": r"""Explain to a teammate what happens when you type `docker run -d -p 8080:80 nginx` on a Mac, in 3 to 4 sentences. Mention the image, the registry, the Linux VM, namespaces and the port mapping.""",
    "answer": r"""Docker looks for the nginx image on my machine and, if it is missing, pulls it from Docker Hub, the default registry. Docker Engine then starts a container inside the small Linux VM that Docker Desktop runs, because containers need a Linux kernel. The container is just an nginx process that namespaces fence off and cgroups can limit. The `-d` flag runs it in the background, and `-p 8080:80` sends traffic from port 8080 on my Mac to port 80 inside the container, where nginx listens.""",
}

new["recap"] = [
    "A container is a fenced-off Linux process made from an image, and it shares the host's kernel.",
    "Namespaces decide what a process can see; cgroups decide how much CPU and memory it can use.",
    "On a Mac, Docker Desktop runs one Linux VM, and the docker command talks to the engine inside it.",
    "One read-only image can start many independent containers, like one packing list and many lunchboxes.",
    "`-p HOST:CONTAINER` publishes a port; `-p 127.0.0.1:8080:80` keeps it private to your Mac.",
    "`docker stop` sends SIGTERM, then SIGKILL after 10 seconds (exit code 137); and what a container writes is lost with `docker rm`.",
]

new["check"] = [
    (r"""You want two web containers that both listen on port 80 inside. Which way of publishing them works?""",
     r"""Each host port belongs to one container, while both containers can use port 80 inside their own network namespace."""),
    (r"""A teammate edits a settings file inside a running container with `docker exec`, then runs `docker rm` and a fresh `docker run` from the same image. Where is the edit?""",
     r"""Changes go to the container's writable layer, which `docker rm` deletes; the image never changes."""),
    (r"""A batch job container shows `Exited (137)` after someone ran `docker stop` on it. What does that tell you?""",
     r"""137 is 128 plus 9, and signal 9 is SIGKILL, which Docker sends when SIGTERM did not end the process within 10 seconds."""),
]

new["interview"] = [
    (r"""What is the difference between a container and a virtual machine?""",
     r"""A virtual machine runs a full operating system with its own kernel on virtual hardware, so it is heavy and slow to boot. A container is a normal process on a Linux host that the kernel isolates with namespaces and limits with cgroups. Containers share the host kernel, so they start in about a second and use little memory. The trade-off is weaker isolation: a kernel bug can affect every container on the host, which is why some platforms wrap containers in small VMs."""),
    (r"""What happens when you run `docker stop`, and why does it matter?""",
     r"""Docker sends SIGTERM to the container's main process and waits, 10 seconds by default. A well-written app catches SIGTERM, finishes the requests it is handling and exits cleanly. If the process is still running after the wait, Docker sends SIGKILL, which ends it at once and can lose work; the exit code is then 137. Kubernetes stops pods the same way, so the same SIGTERM handling protects you in both places."""),
    (r"""Why does an image built on an Apple Silicon Mac sometimes fail on a cloud server?""",
     r"""Containers run on the host's kernel and CPU, so the code inside must match the server's CPU type. A Mac builds arm64 code by default, while most cloud servers are amd64. If the image only holds arm64 code, the server fails with `exec format error`. The fix is a multi-platform image that holds a variant for each CPU, which `docker buildx build --platform linux/amd64,linux/arm64` creates."""),
]

new["deeper"] = r"""You can see the process namespace with one command: `docker run --rm alpine ps`. The output lists one process: `ps` itself, as PID 1. Your Mac and the Linux VM run hundreds of processes, but the container cannot see any of them. Now run `docker run --rm alpine hostname`. You get a random-looking name such as `89851d1cc476`, the container's short ID. The container has its own hostname namespace too. Then `docker run --rm alpine ip addr` shows a third namespace: the container has its own loopback (the "this machine only" address) and its own `eth0` network card with a private address such as `172.17.0.3`.

For cgroups, start Redis with a memory limit: `docker run -d --name capped -m 64m redis:8-alpine`. Then run `docker stats --no-stream capped`. When we ran it, the MEM USAGE / LIMIT column said `8.633MiB / 64MiB`. If Redis tried to use more than 64 MB, the kernel would stop it. Remove it with `docker rm -f capped`. The Kubernetes memory limits on Day 43 use this same kernel feature.

For CPU types, run `docker run --rm --platform linux/amd64 alpine uname -m` on your Mac. It prints `x86_64`. The container really runs amd64 code, translated as it runs by an emulator inside Docker Desktop. That is fine for a quick test and too slow for heavy work. Without an emulator, the same trick fails. On an amd64 Linux server with no emulator installed, `docker run --platform linux/arm64 alpine uname -m` printed `exec /bin/uname: exec format error`. A server shows the same error when someone ships it an arm64-only image.

Docker Desktop has two related settings. Under Settings, General, you can choose the virtual machine manager. Another setting uses Apple's Rosetta to speed up amd64 emulation. Docker Desktop is also not your only choice. OrbStack and Colima run a Linux VM too and give you the same `docker` command, so this course works with them as well. For a friendly tour of the kernel features behind all this, read [Julia Evans' post on containers](https://jvns.ca/blog/2016/10/10/what-even-is-a-container/)."""

new["closing"] = r"""We started with a dish that only worked at home. A container packs the kitchen with the dish, so the same nginx image runs on your Mac today and on a server tomorrow. Before you move on, run `docker ps -a` and read the STATUS column. Every `Exited` line is a container that still holds its files, waiting for `docker rm`, and its exit code says how it ended.

Next, we'll open an image and look at the layers inside. How can two images share most of their files, and where do images live when they are not on your laptop?"""

apply(L, new)
save(path, P, L, OL)
