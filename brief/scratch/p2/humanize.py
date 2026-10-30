#!/usr/bin/env python3
"""Rewrites the prose of content/p2.json in a plain, blog-style human voice.

Loads the CURRENT p2.json, replaces prose fields only, and writes it back.
It never touches ids, titles, headings, code, commands, URLs, answers or diagrams.
Guards: inline code spans in new text must already exist in the lesson,
links must stay the same, and no em or en dashes may appear.
Run: python3 brief/scratch/p2/humanize.py
"""
import json
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parents[3]
PATH = ROOT / "content/p2.json"


def T(s):
    return s.strip("\n")


# ---------------------------------------------------------------- part level
PART_INTRO = T(r"""
Docker packs an app with everything it needs, so it runs the same on your Mac, in CI and in the cloud. You start by running other people's containers. By Day 8 you have written a Dockerfile for hello-devops, run it next to Redis with Compose, and pushed a small, non-root version to a registry. Every later part ships that image.
""")

PART_RECAP = {
    0: "A container is an isolated Linux process started from an image, and it shares the host's kernel.",
    3: "Settings go in environment variables, so the same image runs in testing and in production.",
}

FLASH_BACKS = {
    0: "The kernel. A container is an isolated process on the host, with no kernel of its own.",
    4: "A change to the instruction or to the files it copies. Every layer after it is rebuilt too.",
}

# ---------------------------------------------------------------- lessons
L = {}

# ================================================================ d05
L["d05"] = {
    "guess_why": T(r"""
A container never boots a kernel of its own; it uses the host's Linux kernel. A Mac has no Linux kernel, so Docker Desktop runs one small Linux VM, and every container shares that VM's kernel.
"""),
    "sections": [
        T(r"""
Your code is only one part of what runs. The app also needs:

- a language runtime, such as Python 3.14
- libraries, such as Flask
- system packages from the operating system
- settings, such as environment variables

Your laptop has one mix of these. The CI server has another, and the production server a third. So code that works for you can break on a server just because the setup is different.

Docker packs the app together with everything it needs. You build that package once, and it runs the same way on your Mac, on a CI runner and in the cloud. On the Day 1 map, this is the package step.

The package is called an **image**: your app, its files and its settings, frozen and read-only. A running copy of an image is a **container**.
"""),
        T(r"""
A virtual machine (VM) pretends to be a whole computer. It has virtual hardware and boots a full operating system with its own kernel. The kernel is the core of an operating system: it runs processes and talks to the hardware. Booting all of that takes many seconds, and a VM often needs gigabytes of memory.

A container is far lighter, because it is a normal Linux process. The Docker Engine (the background service that runs containers) starts it. Then the host's kernel keeps it apart from other processes with two features:

- Namespaces give a process its own private view of process IDs, network, hostname and files.
- cgroups (control groups) limit how much CPU and memory a process can use.

No second kernel has to boot, so a container starts in about a second. The price is that every container on a host shares that one kernel.

Macs do not have a Linux kernel, so Docker Desktop runs one small Linux VM and all your containers live inside it. Ask a container on your Mac which system it runs, and it answers Linux.
"""),
        T(r"""
An image and a container relate like a class and an object in Kotlin. The image is the class: a read-only definition. A container is an object, a live instance with its own state. You can start many containers from one image, and they do not affect each other.

Each container gets a thin writable layer on top of its image, and every file the app writes lands there. Remove the container and that layer goes with it. The image stays exactly as it was.

Images live in a registry, a server that stores them and hands them out. Docker Hub is the default. When you run an image you do not have yet, Docker pulls (downloads) it first. Image names look like `name:tag`, for example `redis:8-alpine`, where the tag names a version. Leave the tag out and Docker uses `latest`.

Docker Hub limits how many images you can pull without logging in. Run `docker login` to get a higher limit, and check [Docker Hub pull limits](https://docs.docker.com/docker-hub/usage/pulls/) for the current numbers.
"""),
        T(r"""
`docker run` creates a container from an image and starts it. A typical command looks like `docker run -d --name web -p 8080:80 -e TZ=UTC nginx`, and each flag in it changes one thing:

- `-d` (detached) runs it in the background and prints the container ID.
- `--name web` names it, so later commands can say `web` instead of an ID.
- `-p 8080:80` maps a port on your Mac to a port in the container.
- `-e TZ=UTC` sets an environment variable inside the container.

For one-off commands, add `--rm`. It deletes the container as soon as it stops.

Once the container runs, `docker ps` lists it and `docker logs web` shows what it printed. To look around inside, use `docker exec web <command>`, which runs an extra command in the running container. Anything you type after the image name replaces the image's default command, as in `docker run --rm alpine uname -m`.
"""),
        T(r"""
Each container has its own network namespace, and with it its own set of ports. Inside its container, nginx listens on port 80, where nothing on your Mac can reach it yet.

`-p 8080:80` connects the two. Read it as host first, then container: traffic to port 8080 on your Mac goes to port 80 in the container. Most people get this order backwards at first, so say it out loud a few times.

A few rules follow from this:

- Two containers can both use port 80 inside, because each has its own namespace.
- A port on your Mac can belong to only one container at a time.
- The app inside must listen on `0.0.0.0`, or forwarded traffic never reaches it (Day 4).

By default, Docker publishes the port on all of your Mac's network addresses, so other devices on your network might reach it. On a laptop, `-p 127.0.0.1:8080:80` is the safer habit, because it keeps the port private to your Mac.
"""),
        T(r"""
A container moves through a few states:

1. Created: Docker has set it up but not started it.
2. Running: its main process is alive.
3. Exited: the main process ended, by itself or because you stopped it.
4. Removed: `docker rm` deleted it and its writable layer.

`docker stop` sends SIGTERM to the main process, waits 10 seconds, then sends SIGKILL. You met that pattern on Day 3, and Kubernetes stops containers the same way. Stopping deletes nothing. `docker ps -a` still lists an exited container, and `docker start` runs it again with its files intact.

Your Mac and most cloud servers also use different CPUs. Apple Silicon Macs use arm64, while most cloud servers use amd64, also called x86_64. Many images include a variant for each, and Docker picks the one that matches your machine. An amd64-only image still runs on your Mac through emulation, but more slowly, and some programs misbehave. Day 8 shows how to build your own images for both.
"""),
    ],
    "analogy": T(r"""
An image is a recipe card that comes with sealed, exact ingredients. A container is one meal cooked from it. You can cook many meals from one card, and spilling one meal does not change the card. All the cooks share one kitchen, which is the Linux kernel. The picture fails in one place: real cooks can see each other, while namespaces make each container believe it is alone.
"""),
    "worked_say": {
        0: "Start nginx in the background. Docker does not have the image yet, so it pulls it from Docker Hub first. The long line at the end is the new container's ID.",
        2: "Send a request through the mapped port, then read the logs. nginx writes each request to standard output, which is what `docker logs` shows. The address at the start of the log line will be different on your Mac.",
        3: "`docker exec` runs a command inside the running container. Even on a Mac, the container sees a Linux system, here Debian. The second command lists the files nginx serves.",
    },
    "mistake": T(r"""
The most common slip is writing the port mapping backwards, such as `-p 80:8080` for an app that listens on port 80 inside. The rule is `-p HOST:CONTAINER`: the left number is on your Mac, and the right number is where the app listens in the container. If curl gets no answer, run `docker ps` and read the PORTS column from left to right.
"""),
    "real_world": T(r"""
At PayFlow, the made-up payments company from earlier lessons, laptops, CI runners and production all run the same images. A new engineer starts Postgres and Redis with `docker run` on day one instead of installing them by hand. When a bug shows up only in production, engineers pull the exact image tag that production runs and reproduce the bug locally.
"""),
    "interview_a": {
        1: "Docker sends SIGTERM to the container's main process and waits, 10 seconds by default. A well-written app catches SIGTERM, finishes the requests it is handling and exits cleanly. If the process is still running after the wait, Docker sends SIGKILL, which ends it at once and can lose work. Kubernetes stops pods the same way, so the same SIGTERM handling protects you in both places.",
    },
    "deeper": T(r"""
Two small experiments let you watch namespaces and cgroups at work.

Start with the process namespace. Run `docker run --rm alpine ps`. The output lists exactly one process: `ps` itself, as PID 1. Your Mac and the Linux VM run hundreds of processes, but the container cannot see any of them. Now run `docker run --rm alpine hostname`. You get a random-looking name, which is the container's short ID, because the container has its own hostname namespace too.

For cgroups, start Redis with a memory limit: `docker run -d --name capped -m 64m redis:8-alpine`. Then run `docker stats --no-stream capped`. The MEM USAGE / LIMIT column shows something like `5.7MiB / 64MiB`. If Redis tried to use more than 64 MB, the kernel would stop it. Remove it with `docker rm -f capped`. The Kubernetes memory limits on Day 18 use this same kernel feature.

You can see the VM too. `docker version` prints a Client section (the `docker` command on your Mac) and a Server section (the Docker Engine). On Apple Silicon the server says `linux/arm64`, because the engine runs inside Docker Desktop's Linux VM. In Docker Desktop, under Settings, General, you can choose the virtual machine manager. For Apple Silicon, Docker's docs list Docker VMM and Apple's Virtualization framework. Another setting uses Rosetta for amd64 emulation, which makes emulation faster.

To see emulation itself, run `docker run --rm --platform linux/amd64 alpine uname -m`. It prints `x86_64` on your arm64 Mac. The container really runs amd64 code, translated as it runs. That is fine for a quick test and too slow for heavy work.

Docker Desktop is also not your only choice. OrbStack and Colima run a Linux VM too and give you the same `docker` command, and the commands in this course work with any of them. For a friendly tour of the kernel features behind all this, read [Julia Evans' post on containers](https://jvns.ca/blog/2016/10/10/what-even-is-a-container/).
"""),
}

# ================================================================ d06
L["d06"] = {
    "sections": [
        T(r"""
Docker builds an image by following a plain text file named `Dockerfile`. It runs the steps in that file from top to bottom, and each step starts from the result of the one before.

The Dockerfile lives in git next to the app, and teammates review changes to it like any other code. That is the Day 1 idea of everything as code, applied to packaging.

You build the image with `docker build -t hello-devops:1.0.0 .`. The `-t` flag gives the new image a name and a tag. The dot at the end is the build context, which gets its own section below. Today you write a simple Dockerfile with one stage, and Day 8 turns it into the production version.
"""),
        T(r"""
Most Dockerfiles use only these seven instructions, plus a `CMD` at the end:

- `FROM` picks the base image to start from, such as `python:3.14-slim`.
- `WORKDIR` sets the folder that later steps work in, and creates it.
- `COPY` copies files from your project folder into the image.
- `RUN` runs a command at build time, such as `pip install`, and saves the result.
- `ENV` sets an environment variable for later steps and for the running container.
- `ARG` declares a variable you set at build time with `--build-arg`.
- `EXPOSE` documents the port the app listens on. It publishes nothing; `-p` does that.

`CMD` sets the command a container runs by default. `ENTRYPOINT` is similar, but arguments you give to `docker run` are added to it instead of replacing it. For a web app, `CMD` alone is the simple choice.

Write `CMD` in exec form, a JSON list such as `["gunicorn", "app:app"]`. Then your app is process 1 and gets the SIGTERM from `docker stop`. In shell form (`CMD gunicorn app:app`), a shell sits in between and the signal never reaches your app. Go deeper, at the end of this lesson, measures what that costs.
"""),
        T(r"""
Each instruction that changes files creates a **layer**, a saved set of file changes. An image is a stack of layers with the base image at the bottom, and `docker history` lists them with their sizes.

Docker keeps every layer it builds in its build cache. On the next build, it checks each step in order. If the instruction and the files it uses are unchanged, Docker reuses the saved layer and prints `CACHED`. If something changed, Docker rebuilds that layer and every layer after it, even the ones whose steps did not change. That second half is what trips most people up.

So order the steps from rarely changed to often changed:

1. `FROM` the base image.
2. `COPY requirements.txt` on its own.
3. `RUN pip install`, the slow step.
4. `COPY app.py`, which changes all the time.

With this order, an edit to `app.py` rebuilds only the last small layer. Docker reuses the install, and the build takes about a second.
"""),
        T(r"""
The dot in `docker build -t hello-devops:1.0.0 .` is the **build context**: the folder whose files the build may use. A `COPY` can only take files from inside it, so a path like `../secrets.txt` fails. Docker also looks for the file named `Dockerfile` in that folder, unless you name another one with `-f`.

A `.dockerignore` file in that folder lists files the build must never see. It uses patterns the way `.gitignore` does. Ours keeps out:

- `.git` and `.github`, the repo's history and workflows
- `.venv` and Python caches, which belong to your Mac only
- folders for later days, such as `infra`, `k8s` and `chart`
- Markdown files, which the app does not need

Our Dockerfile copies two files by name, so for now the ignore file is a safety net. It starts to matter the day someone writes `COPY . .`. Without it, that one line copies your `.git` folder, local secrets and other junk into the image. It also breaks the cache whenever any of those files change.
"""),
        T(r"""
A tag is the part after the colon, as in `hello-devops:1.0.0`. Leave it out and Docker uses `latest`. Despite the name, `latest` is just the default label. It does not mean newest, and it can change without warning.

So tag your own images with a real version, such as `1.0.0` (Day 9 explains version numbers). In `FROM`, name a specific base such as `python:3.14-slim`, never bare `python`. Otherwise your build gets whatever `latest` points to on the day you build.

One image can carry several tags. `docker tag hello-devops:1.0.0 hello-devops:stable` adds a second name without copying anything. Anyone who can push can also move a tag to a different image later. Digests, which you meet on Day 8, never move.
"""),
        T(r"""
[The Twelve-Factor App](https://12factor.net/config) is a well-known set of rules for web apps. Its config rule says to keep settings that change between deploys in environment variables, outside the code. Then the same image runs in every environment, and only the variables differ.

hello-devops follows this rule and reads four variables:

- `APP_VERSION`, the version it reports
- `GREETING`, the message it returns
- `REDIS_HOST`, where Redis runs (empty means count in memory)
- `PORT`, used only when you run `python app.py`

In the Dockerfile, `ENV` sets defaults, and `docker run -e GREETING=Hi` overrides them without a rebuild. The version also gets a value at build time. `ARG APP_VERSION` takes it from `--build-arg`, and `ENV APP_VERSION=$APP_VERSION` keeps it for run time.

`PYTHONUNBUFFERED=1` makes Python print log lines at once, so `docker logs` shows them as they happen. Never put passwords or keys in `ENV` or `ARG`; Day 8 explains why.
"""),
    ],
    "analogy": T(r"""
Picture a layered cake, with the build cache as a fridge full of finished layers. Change only the decoration on top, and every lower layer comes out of the fridge ready. Change the sponge at the bottom, and every layer above it has to be baked again. A real baker could keep an upper layer after changing a lower one. Docker never does: everything after the first change gets rebuilt.
"""),
    "worked_say": {
        0: "In your hello-devops folder, create the Dockerfile and .dockerignore from the Files section, then build. The `-t` flag names the image, `--build-arg` fills the ARG, and the final dot is the build context. The first build is the slow one, because it downloads the base image and runs pip install.",
        2: "Add a comment line to app.py and build again. The three steps above the code say CACHED and only `COPY app.py` runs, so the build takes under a second. Remove the comment afterwards.",
        3: "`docker history` lists the layers, newest first. The pip install layer is the big one. CMD, EXPOSE, ENV and ARG only change settings, so they are 0B. Notice that the ARG value is visible here; Day 8 comes back to that.",
        5: "`docker inspect` shows every setting of an image as JSON, and a `--format` template picks out the fields you want. Then clean up both containers.",
    },
    "mistake": T(r"""
The classic mistake is `COPY . .` before `RUN pip install`. Every code change, even a comment, then invalidates the cache and reinstalls every package. Copy only `requirements.txt` first, install, and copy the code last.
"""),
    "real_world": T(r"""
PayFlow keeps each service's Dockerfile in that service's repo, and changes to it go through code review. CI builds the image once per commit. That same image moves from testing to production, and only the env vars change. Reviewers watch Dockerfile order closely, because one misplaced COPY makes every build reinstall all dependencies.
"""),
    "interview_a": {
        1: "Order instructions from least to most often changed, so the cache gets reused: base image, dependency files, install, then source code. Copy only the files you need and keep a .dockerignore, and unrelated changes stop breaking the cache. A small base image means less to download and push. In CI, share the build cache between runs, because every fresh runner starts with an empty one.",
    },
    "deeper": T(r"""
One test shows what shell-form CMD costs you. Make a second Dockerfile that starts `FROM hello-devops:1.0.0` and adds one line in shell form: `CMD gunicorn --bind 0.0.0.0:8000 app:app`. Build it as `hello-devops:shell` and run it. Then look at process 1 in each container with `docker exec <name> cat /proc/1/cmdline | tr '\0' ' '`:

- In the shell-form container, process 1 is `/bin/sh -c gunicorn --bind 0.0.0.0:8000 app:app`.
- In your real image, process 1 is `/usr/local/bin/python3.14 /usr/local/bin/gunicorn ...`.

Now time `docker stop` on each, for example with `time docker stop <name>`. When we tried it, the shell-form container took about 10 seconds and ended as `Exited (137)`. The exec-form container stopped in under a second, with exit code 0.

`docker stop` sends SIGTERM to process 1, and in the shell-form container that is the shell. The shell does not pass the signal on to gunicorn, so nothing happens. After 10 seconds Docker gives up and sends SIGKILL. Exit code 137 is 128 + 9, and 9 is the number of SIGKILL (Day 3). In production, every deploy then waits 10 extra seconds per container, and requests in flight are cut off.

The build context has a cost of its own. Docker builds use BuildKit, which only reads the files a build actually needs. With `COPY app.py .`, a large file elsewhere in your folder costs nothing. With `COPY . .`, the whole folder, minus the `.dockerignore` entries, is read and sent to the builder. In our test, a 30 MB `.venv` folder that was not ignored added 30 MB to the context on every build. That is one more reason to copy named files and keep `.dockerignore` up to date.

The [Dockerfile reference](https://docs.docker.com/reference/dockerfile/) covers CMD and ENTRYPOINT in more depth, with a table that shows how the two combine.
"""),
}

# ================================================================ d07
L["d07"] = {
    "terms": {"Healthcheck": "A command Docker runs on a schedule to test whether a container works."},
    "sections": [
        T(r"""
A container's own files live in its writable layer, and they are gone when you remove the container. That is what you want. You should be able to delete and recreate any container at any moment, for an upgrade or after a crash.

So data you care about must live outside the container. Docker gives you two ways to do that, volumes and bind mounts. Both attach outside storage to a folder inside the container.

hello-devops has this problem right now. On Day 6 the visit count lived in memory, so every restart reset it to zero. You may also have seen it jump back now and then. That happens because gunicorn runs two worker processes, and each one keeps its own count. Today you move the count into Redis, an in-memory database. All workers then share one number, and Redis keeps it in a volume that survives restarts.
"""),
        T(r"""
The two kinds differ in who owns the storage:

- A volume is storage that Docker creates and manages, as in `-v redis-data:/data`.
- A bind mount shows a folder from your Mac inside the container, as in `-v "$PWD/site":/usr/share/nginx/html`.

The left side of `-v` decides which one you get: a plain name means a volume, and a path on your Mac means a bind mount. The right side is always the folder inside the container.

Use volumes for data the app owns, such as database files. They survive `docker rm` and stay until you delete them with `docker volume rm`. Use bind mounts while developing, when you edit files on your Mac and want the container to see each change at once. On a Mac, heavy file work through a bind mount can be slower, because the files have to cross from macOS into Docker's Linux VM.
"""),
        T(r"""
Each container gets its own IP address on a Docker network. On the default network, containers can reach each other only by IP address, and that address can change on every restart.

A user-defined network solves this. Create one with `docker network create hello-net`, and every container you start with `--network hello-net` gets a built-in DNS server. On that network, the name `redis` resolves to the current IP of the container called redis.

Containers on the same network can reach each other on any port, so `-p` is only for traffic from your Mac. Inside a container, `localhost` means that container itself (Day 4), and `REDIS_HOST=localhost` would point the app at its own container, where no Redis runs.

Containers on different user-defined networks cannot reach each other at all, which keeps unrelated apps apart. Compose creates a network like this for every project.
"""),
        T(r"""
Setting up a network, a volume and two containers by hand takes several long commands, as the worked example shows. With **Docker Compose**, all of it goes in one file, `compose.yaml`, and `docker compose up` starts it.

The file has a top-level `services` map. Each service describes one container, and its name doubles as its hostname. Inside a service you will use these keys:

- `build: .` builds the image from the Dockerfile in this folder.
- `image:` uses a ready-made image, such as `redis:8-alpine`.
- `ports:` publishes ports, written `"HOST:CONTAINER"` in quotes.
- `environment:` sets env vars.
- `volumes:` mounts volumes or folders.
- `depends_on:` controls start order.

Named volumes also go under a top-level `volumes` key. You do not have to declare a network, because Compose creates one for the project by itself. The project name is the folder name, so your containers are called `hello-devops-web-1` and `hello-devops-redis-1`.
"""),
        T(r"""
`depends_on` makes Compose start Redis before web. In its plain form it only waits for the Redis container to start, and Redis may need a moment more before it answers.

A **healthcheck** fills that gap. It is a command Docker runs inside the container again and again. Exit code 0 means healthy, and anything else is a failed check (the exit codes from Day 3). Ours runs `redis-cli ping` every 5 seconds, with a 3-second timeout and 5 retries.

Use the long form of `depends_on` with `condition: service_healthy`, and Compose waits until Redis is healthy before it starts web. That only covers startup. Your app still has to cope when a dependency fails later, and hello-devops does: `/readyz` returns 503 while Redis is down, which Kubernetes uses on Day 18.

`docker compose ps` shows the health in its STATUS column. It says `(health: starting)` at first, then `(healthy)` once a check passes. If the check keeps failing, it says `(unhealthy)`, and web never starts.
"""),
        T(r"""
Compose reads a file named `.env` next to `compose.yaml` and uses it to fill in `${VARIABLE}` placeholders. Take `GREETING: "${GREETING:-Hello, DevOps!}"`. Compose looks for `GREETING` in your shell and in `.env`, and the shell wins if both set it. If neither does, it uses the default after `:-`. The quickest check is `docker compose config`, which prints the final file with every value filled in. If `.env` ever holds secrets, list it in `.gitignore`.

These commands cover most days:

- `docker compose up -d --build` builds and starts everything in the background.
- `docker compose ps` shows each container and its health.
- `docker compose logs -f web` follows one service's output.
- `docker compose exec redis redis-cli GET visits` runs a command in a service.
- `docker compose down` removes the containers and the network, and keeps volumes.
- `docker compose down -v` also deletes the volumes, and with them your data.
"""),
    ],
    "analogy": T(r"""
A volume works like a locker at a swimming pool. Swimmers (containers) come and go, and the next swimmer with the same key finds what was left inside. The network is the front desk: you ask for "redis" by name, and it tells you where to go. Lockers stay in one building, though, and so do volumes. A volume lives on one Docker host, so it does not follow your container to another machine.
"""),
    "worked_say": {
        0: "Create a user-defined network and a named volume. The next commands refer to both by these names.",
        4: "Start a brand-new Redis container with the same volume. The count picks up where it left off, because the data lived in the volume and removing the old container did not touch it.",
        5: "Clean up everything. That took five long commands to set up, and the hands-on task puts the same app in one compose.yaml.",
    },
    "mistake": T(r"""
It is easy to type `docker compose down -v` when you meant `docker compose down`. The `-v` flag deletes the named volumes, so your Redis data, or a whole database, is gone for good. Use plain `down` day to day, and keep `down -v` for when you really want a clean start.
"""),
    "real_world": T(r"""
Every service repo at PayFlow has a compose.yaml, so a new engineer can start the service with its Postgres and Redis using one command. CI often uses the same file to start real dependencies for integration tests. Production looks different. The same images usually run on Kubernetes there (Day 16), and the databases are managed services instead of containers.
"""),
    "interview_a": {
        1: "For local development, demos and CI test setups, Compose works well: one file, one command. But it runs containers on a single host, so it cannot spread them over several machines or move them when a machine dies. Some small apps do run with Compose on one server. Most teams use Kubernetes or a managed container service in production, and the images stay the same either way.",
    },
    "deeper": T(r"""
The count survived the Redis swap because of how Redis saves its data. A rougher stop would have lost some of it.

Redis keeps its data in memory. It writes a snapshot file, `dump.rdb`, to `/data` from time to time, and again when it shuts down cleanly. To see the rules, set up the worked example again up to step 5, so Redis has had one clean stop. Run `docker exec redis redis-cli CONFIG GET save` and you get `3600 1 300 100 60 10000`. Read the numbers in pairs:

- after 3600 seconds, if at least 1 key changed
- after 300 seconds, if at least 100 keys changed
- after 60 seconds, if at least 10000 keys changed

In step 4 you used `docker stop`. That sends SIGTERM, Redis saves a final snapshot, and nothing is lost. Now try the rough way. Call the app a few more times, then run `docker rm -f redis`. The `-f` flag sends SIGKILL at once, so Redis has no chance to save. Start a fresh Redis on the same volume, as in step 5, and call the app again. When we tried it, the count was 9 before the kill. The new Redis read the last snapshot, which said 5, so the four visits after that snapshot were lost.

That is the Day 3 lesson about signals, with real data at stake. In practice:

- Stop stateful containers with `docker stop` or `docker compose down`, both of which send SIGTERM first.
- For data you cannot lose, turn on Redis's append-only file with `--appendonly yes`, which logs every write.
- In production, consider a managed database service, where backups and failover are someone's full-time job.

The volume itself sits somewhere you might not expect. Run `docker volume inspect redis-data` (with Compose, the name is `hello-devops_redis-data`). It shows a mount point under `/var/lib/docker/volumes`. On a Mac, that path is inside Docker Desktop's Linux VM, so you will not find it in Finder. If you reset Docker Desktop to factory defaults, your volumes go with it.
"""),
}

# ================================================================ d08
L["d08"] = {
    "terms": {"Digest": "A sha256 hash of an image's content that always names that one exact image."},
    "sections": [
        T(r"""
Building an app often needs tools that running it does not. A Kotlin service needs a JDK and Gradle to compile, but only a Java runtime to run. Python packages with C code need a compiler to install.

A **multi-stage build** has several `FROM` lines in one Dockerfile. Each `FROM` starts a new stage, and only the last stage becomes your image. Earlier stages are scratch space: you build there, then copy just the results forward with `COPY --from=<stage>`.

Our final Dockerfile has two stages:

1. `build` creates a virtual environment (a venv) in `/venv` and installs the packages into it.
2. The run stage starts again from a clean `python:3.14-slim` and copies in `/venv` and `app.py`, nothing else.

A venv keeps every installed package in one folder, so one `COPY` moves them all. For hello-devops the size barely changes, because nothing is compiled. The real savings come when a build needs compilers or a JDK. Even here, though, the stage that ships is short and easy to read.
"""),
        T(r"""
The base image decides most of your image's size and most of its security findings. Fewer packages means less to download and less to patch. For Python, the common choices are:

- `python:3.14` is full Debian with compilers, about 1.6 GB on disk.
- `python:3.14-slim` is Debian with the minimum, about 180 MB. A good default.
- `python:3.14-alpine` is about 75 MB. Its different C library (musl) means some packages must compile.
- Distroless images hold only a runtime and your app, with no shell, so debugging is harder.
- Docker Hardened Images are minimal and run as non-root by default. They are free (Apache 2.0) from `dhi.io`.

The sizes come from `docker images` on an amd64 machine in October 2026. Whichever you pick, rebuild often, so your image gets the base image's security fixes.
"""),
        T(r"""
By default, the process in a container runs as root. That root is limited inside the container, but it is still root on the shared kernel. If an attacker breaks into your app, root makes the next step easier, so least privilege (Day 3) says to run as a normal user.

Two lines in our Dockerfile do this. `RUN useradd --uid 10001 --no-create-home appuser` creates the user, and `USER 10001` makes every later step, and the container, run as that user. Use the number rather than the name, because Kubernetes can only prove that an image is non-root when the user is numeric (Day 18).

`HEALTHCHECK` tells Docker how to test the app. Every 30 seconds, Docker runs a short Python command that calls `/healthz`. The slim image has no `curl`, so Python does the job. `docker ps` then shows `(healthy)` or `(unhealthy)`. Only plain Docker and Compose use this line. Kubernetes ignores it and uses its own probes.
"""),
        T(r"""
A vulnerability scanner lists the packages in your image and checks them against public lists of CVEs. Two scanners are easy to start with:

- `docker scout` comes with Docker Desktop. `docker scout quickview` gives a summary, and `docker scout cves` lists each finding.
- Trivy is a free, open source scanner. Install it with `brew install trivy` and run `trivy image hello-devops:1.0.0`.

Sign in to Docker before you use Scout, and check its docs for current plan limits.

Your first scan will print a long list. Most findings sit in the base image's packages, and many have no fix yet. Start with what you can act on. The `--ignore-unfixed` flag hides findings that have no fixed version. For the rest, update the base image or a package version, and rebuild. On Day 22 a scan joins the release pipeline, so a serious finding that has a fix stops the release.
"""),
        T(r"""
A tag can move: someone can push a new image as `python:3.14-slim` tomorrow. A digest is a sha256 hash of the image's content, written `name@sha256:...`, and it always means exactly the same image. Deploy files often pin a digest, so the image you tested is the image that runs.

To share an image, you push it to a registry. GitHub Container Registry (GHCR) lives at `ghcr.io`, next to your repo on GitHub. Pushing takes four steps:

1. Create a personal access token (classic) with the `write:packages` scope. GitHub's docs say GHCR needs this token type.
2. Log in with `docker login ghcr.io -u <your-github-user>` and paste the token as the password.
3. Give the image its full name with `docker tag`, as in `ghcr.io/<your-github-user>/hello-devops:1.0.0`.
4. Run `docker push`. Its last line prints the digest.

Write your user name in lowercase, because image names cannot contain capitals. New GHCR packages start out private. Docker Hub works the same way, with names like `<user>/hello-devops`.
"""),
        T(r"""
Your Mac builds arm64 images, while most cloud servers are amd64. An arm64-only image fails on such a server with `exec format error`. The fix is a multi-platform image: one name, with one variant per CPU type.

`docker buildx build --platform linux/amd64,linux/arm64 -t <name> --push .` builds both and pushes them together. Docker Desktop builds the amd64 half through emulation, so it takes longer. When a server pulls the image, Docker picks the variant for its CPU.

Never bake secrets into an image. Every layer ships with the image, so a key you `COPY` in and delete in a later step still sits in the earlier layer. Values from `ARG` and `ENV` show up in the image history, as you saw on Day 6. Give secrets to the container at run time instead. If a build step truly needs one, use a build secret (`RUN --mount=type=secret`), which never lands in a layer.
"""),
    ],
    "analogy": T(r"""
A multi-stage build is like a restaurant kitchen and its dining room. The kitchen is full of knives, flour and hot ovens, but the plate that reaches the guest carries only the finished dish. The comparison misses one thing. A knife left out in a restaurant is only untidy, while every extra tool in an image is something an attacker could use.
"""),
    "worked_say": {
        0: "First look at the Day 6 image: which user it runs as, and how big it is.",
        2: "Check the user and the size again. The app now runs as appuser (uid 10001). The size barely moved, because this app compiles nothing. What you gained is a final stage that holds only the venv and app.py.",
        5: "Now look at a real digest. `imagetools inspect` asks the registry about an image without pulling it. The base image has one digest for the whole set, plus a variant for each CPU type. Writing `FROM python:3.14-slim@sha256:cd89...` would pin it.",
    },
    "mistake": T(r"""
The worst mistake here is putting a secret into the image with `COPY .env .`, `ENV API_KEY=...` or `ARG TOKEN`, even if a later step deletes it. Every layer and the image history ship with the image, so anyone who can pull it can read them. Pass secrets at run time, or use a build secret mount when a build step needs one.
"""),
    "real_world": T(r"""
PayFlow's CI builds each service image once and scans it. Then it pushes the image to a private registry, tagged with the version and the git commit. Deploy files reference the image by digest, so production runs exactly what was tested. A scheduled job rebuilds the images every week to pick up base image fixes, and the build fails on fixable critical findings.
"""),
    "interview_a": {
        0: "Start from a small, trusted base image (slim, distroless or a hardened image), and rebuild often to pick up fixes. Use a multi-stage build, so compilers and build tools never ship. Run as a non-root user and give the container only what it needs. In CI, scan every image and fail on serious findings that have a fix. Keep secrets out of layers, and deploy by digest, so what you scanned is what runs.",
    },
    "deeper": T(r"""
A multi-platform image is really a small index. Run `docker buildx imagetools inspect python:3.14-slim` and look at the top: the media type is an image index, with its own digest. Under Manifests it lists one entry per platform. On the day we checked, the list had eight platforms:

- linux/amd64 and linux/386 for Intel and AMD CPUs
- linux/arm64/v8, linux/arm/v7 and linux/arm/v5 for ARM CPUs
- linux/ppc64le, linux/riscv64 and linux/s390x for other server CPUs

You will also see entries marked `unknown/unknown`. Those are attestations: small records, added by the build tool, that describe how the image was built. Day 22 uses them.

When you run `docker pull python:3.14-slim`, Docker reads the index and downloads only the variant for your CPU. So one tag works on your Mac and on an amd64 server. If you pin a digest, pin the index digest, so every platform still works.

Emulation is the easy way to build for the other CPU, but it is slow for heavy builds. There are two faster options:

- Native builders, one per CPU type, such as an arm64 runner and an amd64 runner in CI.
- Cross-compilation, where a language like Go compiles for another CPU inside a multi-stage build, with no emulation.

To try a hardened base, follow the flow in Docker's docs. Run `docker login dhi.io` with your Docker account, then pull an image from the [Docker Hardened Images catalog](https://docs.docker.com/dhi/). Runtime variants have no shell and run as non-root. You build in a `-dev` variant instead, which has a shell and build tools, and copy the venv into the runtime variant. That is the same two-stage pattern you used today. Two lines of our Dockerfile would change. The `RUN useradd` line needs tools the runtime image lacks, so you would rely on the image's own non-root user instead. And the HEALTHCHECK would need the exec form, a JSON list, because its current form runs through a shell.
"""),
}


# ---------------------------------------------------------------- apply with guards
CODE = re.compile(r"`([^`]+)`")
LINK = re.compile(r"\]\((https?://[^)]+)\)")
problems = []


def guard(where, old, new, lesson_blob):
    if "—" in new or "–" in new:
        problems.append(f"{where}: dash")
    for span in CODE.findall(new):
        if f"`{span}`" not in lesson_blob:
            problems.append(f"{where}: new code span `{span}`")
    if sorted(LINK.findall(old)) != sorted(LINK.findall(new)):
        problems.append(f"{where}: links changed")


def blob_of(obj):
    # Every string in the object, joined, for code-span lookups.
    out = []

    def walk(x):
        if isinstance(x, str):
            out.append(x)
        elif isinstance(x, dict):
            for v in x.values():
                walk(v)
        elif isinstance(x, list):
            for v in x:
                walk(v)
    walk(obj)
    return "\n".join(out)


def main():
    P = json.loads(PATH.read_text())
    part_blob = blob_of(P)

    guard("part.intro", P["intro"], PART_INTRO, part_blob)
    P["intro"] = PART_INTRO
    for i, txt in PART_RECAP.items():
        guard(f"part.recap{i}", P["recap"][i], txt, part_blob)
        P["recap"][i] = txt
    for i, txt in FLASH_BACKS.items():
        guard(f"part.flash{i}", P["flashcards"][i]["back"], txt, part_blob)
        P["flashcards"][i]["back"] = txt

    for Ls in P["lessons"]:
        lid = Ls["id"]
        E = L.get(lid)
        if not E:
            continue
        lb = blob_of(Ls)

        def put(where, obj, key, txt):
            guard(f"{lid}.{where}", obj[key], txt, lb)
            obj[key] = txt

        if "goal" in E:
            put("goal", Ls, "goal", E["goal"])
        if "guess_why" in E:
            put("guess.why", Ls["guess"], "why", E["guess_why"])
        for term, plain in E.get("terms", {}).items():
            hit = [t for t in Ls["terms"] if t["term"] == term]
            assert len(hit) == 1, (lid, term)
            put(f"term.{term}", hit[0], "plain", plain)
        if "sections" in E:
            assert len(E["sections"]) == len(Ls["sections"]), lid
            for i, body in enumerate(E["sections"]):
                put(f"sec{i + 1}", Ls["sections"][i], "body", body)
        for k in ("analogy", "mistake", "real_world"):
            if k in E:
                put(k, Ls, k, E[k])
        for i, say in E.get("worked_say", {}).items():
            put(f"worked{i}", Ls["worked"]["steps"][i], "say", say)
        for i, a in E.get("interview_a", {}).items():
            put(f"interview{i}", Ls["interview"][i], "a", a)
        if "deeper" in E:
            put("deeper", Ls["deeper"], "body", E["deeper"])

    if problems:
        for p in problems:
            print("GUARD", p)
        raise SystemExit("guards failed; nothing written")
    PATH.write_text(json.dumps(P, ensure_ascii=False, indent=1) + "\n")
    print("wrote", PATH)


if __name__ == "__main__":
    main()
