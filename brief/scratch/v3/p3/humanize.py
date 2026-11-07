#!/usr/bin/env python3
"""Human-writing pass (blog mode) over content/p3.json, Docker d11 to d16 plus part fields.

Loads the untouched copy saved in this folder (p3.orig.json, a copy of content/p3.json taken
before the pass), so the script can be rerun. Each edit names a field and either replaces one
exact substring (which must occur once) or the whole field. Only prose fields are touched.
"""
import json
import pathlib

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[3]
SRC = HERE / "p3.orig.json"
DST = ROOT / "content/p3.json"

d = json.loads(SRC.read_text())
L = {x["id"]: x for x in d["lessons"]}


def node(where):
    return d if where == "part" else L[where]


def get(where, path):
    o = node(where)
    for p in path[:-1]:
        o = o[p]
    return o, path[-1]


def sub(where, path, old, new):
    """Replace one exact substring inside a prose field."""
    o, k = get(where, path)
    n = o[k].count(old)
    assert n == 1, f"{where} {path}: found {n} times: {old[:60]!r}"
    o[k] = o[k].replace(old, new)


def full(where, path, start, new):
    """Replace a whole prose field; `start` must match the beginning of the old text."""
    o, k = get(where, path)
    assert o[k].startswith(start), f"{where} {path}: starts {o[k][:60]!r}"
    o[k] = new


# ---------------------------------------------------------------- part level
full("part", ["intro"], "This part teaches containers",
     "Every CI pipeline and Kubernetes deploy later in the course ships one thing: the hello-devops image you build in this part. "
     "You start by running other people's images and opening one up to see its layers. "
     "Then you write a Dockerfile for hello-devops and connect it to Redis with volumes, networks and Compose. "
     "The part ends with a small, non-root, scanned image on GHCR.")
full("part", ["recap", 2], "Tags move", "Tags move and digests do not, and one name can hold a variant for each CPU type.")
full("part", ["recap", 3], "A Dockerfile builds",
     "Order Dockerfile steps from rarely changed to often changed, so the cache saves the slow ones.")
full("part", ["resources", 0, "why"], "A three-hour",
     "Covers most of this part at a slower pace over three hours, with diagrams and a small project.")
full("part", ["resources", 1, "why"], "A full walk",
     "Goes through Compose files and commands from start to end. Watch it next to Day 15.")
full("part", ["resources", 2, "why"], "A seven-minute",
     "Seven minutes long. Watch it before the part, or after it to see how the pieces fit.")
full("part", ["resources", 4, "why"], "A conference talk",
     "Bret Fisher on what changes when images go to production: users, health checks and small bases.")
full("part", ["resources", 5, "why"], "A short, paid zine",
     "Short comics (a paid zine) on namespaces, cgroups and the other kernel features behind containers.")
full("part", ["resources", 7, "why"], "Docker's checklist",
     "Docker's checklist for writing Dockerfiles. Hold your own Dockerfile up against it after Day 16.")

# ---------------------------------------------------------------- d11
sub("d11", ["sections", 0, "body"],
    "A test passes on your Mac with Python 3.14 and fails in CI, where the runner has Python 3.12. Nothing in your code changed. The setup around it did.",
    "So a test can pass on your Mac with Python 3.14 and fail in CI, where the runner has Python 3.12, without anyone touching the code.")
sub("d11", ["sections", 0, "body"],
    "You build one package that holds the app and everything it needs. That exact package then runs",
    "You build one package that holds the app and everything it needs, and that exact package runs")
full("d11", ["sections", 1, "body"], "A virtual machine (VM) pretends",
     "A virtual machine (VM) pretends to be a whole computer. It has virtual hardware and boots a full operating system with its own kernel. "
     "The kernel is the core of an operating system: it starts processes, hands out memory and talks to the hardware. "
     "Booting all of that takes many seconds, and each VM holds on to its own share of memory.\n\n"
     "A container has none of that. It is a normal Linux process, the same kind you listed with `ps` on Day 6. "
     "The kernel gives it two extra things:\n\n"
     "- Namespaces give the process a private view of the system: its own process list, network, hostname and files.\n"
     "- cgroups (control groups) give it a budget: a cap on how much CPU and memory it may use.\n\n"
     "Namespaces work like the blinkers on a horse, the flaps that stop it seeing to the side. You can watch them work. "
     "`docker run --rm alpine ps` lists a single process, `ps` itself, running as PID 1. "
     "The machine runs hundreds of processes, and the container sees none of them.\n\n"
     "No second kernel has to boot, so a container starts in about a second. "
     "You pay for that speed by sharing: every container on a host uses the same kernel, so a kernel bug can affect all of them. "
     "A container can also only run programs built for that kernel and that CPU.")
sub("d11", ["sections", 3, "body"], "The image stays exactly as it was.", "The image itself never changes.")
sub("d11", ["sections", 6, "body"], "ends with exactly that code after 10 seconds", "ends with that code after 10 seconds")
full("d11", ["analogy"], "A container is like an apartment",
     "A container is like an apartment in a big building. Its own front door and mailbox keep the people inside from seeing their neighbours; those are the namespaces. "
     "Its water and power meters have a limit; those are the cgroups. "
     "Every apartment stands on one foundation and shares the building's pipes, and that shared plumbing is the kernel. "
     "A real apartment takes a long time to build, though. "
     "Docker makes a container in about a second because it builds nothing new: it only puts fences around a process.")
full("d11", ["mistake"], "The most common slip",
     "Writing `-p 80:8080` for an app that listens on port 80 inside gets the mapping backwards. "
     "The rule is `-p HOST:CONTAINER`: the left number is on your Mac, and the right number is where the app listens in the container. "
     "If curl gets no answer, run `docker ps` and read the PORTS column from left to right.")
full("d11", ["real_world"], "At PayFlow",
     "When a bug shows up only in production, an engineer pulls the exact image tag that production runs and reproduces the bug on a laptop. "
     "That works because laptops, CI runners and production all run the same images. "
     "New engineers also start Postgres and Redis on their first day with `docker run`, instead of installing them by hand.")
sub("d11", ["deeper", "body"],
    "Three small experiments let you watch namespaces, cgroups and CPU types at work.\n\nStart with the process namespace. Run `docker run --rm alpine ps`. The output lists exactly one process:",
    "The process namespace is the easiest one to see. Run `docker run --rm alpine ps`. The output lists one process:")
sub("d11", ["deeper", "body"],
    "That is the exact error a server shows when someone ships an arm64-only image to it.",
    "A server shows the same error when someone ships it an arm64-only image.")
sub("d11", ["deeper", "body"], "Docker Desktop has two settings worth knowing here.", "Docker Desktop has two related settings.")

# ---------------------------------------------------------------- d12
sub("d12", ["sections", 0, "body"],
    "That is why `docker history` lists them with a size of 0B.",
    "`docker history` lists those with a size of 0B.")
sub("d12", ["sections", 0, "body"],
    "If you know git, the picture is familiar. Layers are like immutable snapshots of changes,",
    "If you know git, layers are like immutable snapshots of changes,")
sub("d12", ["sections", 1, "body"],
    "The big win is sharing. Two images built `FROM python:3.14-slim` start with the same four layers, so your disk and the registry store them once.",
    "Content addressing also lets images share layers. Two images built `FROM python:3.14-slim` start with the same four layers, so your disk and the registry store those layers once.")
sub("d12", ["sections", 1, "body"],
    "This is also why the order of a Dockerfile matters, as Day 13 shows. Docker reuses a layer only when everything below it is identical.",
    "The same rule makes the order of a Dockerfile matter, as Day 13 shows: Docker reuses a layer only when everything below it is identical.")
sub("d12", ["sections", 2, "body"], "The diff showed exactly those, plus", "The diff showed those three changes, plus")
sub("d12", ["sections", 2, "body"],
    "Copying a big file up is slow, and the layer dies with the container. That is why databases keep their files in volumes (Day 14).",
    "Copying a big file up is slow, and the layer dies with the container, so databases keep their files in volumes instead (Day 14).")
sub("d12", ["sections", 3, "body"],
    "Here is the trap that follows from layers. One `RUN` step creates a 50 MB file, and the next `RUN` step deletes it.",
    "Say one `RUN` step creates a 50 MB file, and the next `RUN` step deletes it.")
sub("d12", ["sections", 3, "body"], "Size is worth watching for three reasons:", "Image size costs you in three places:")
sub("d12", ["sections", 4, "body"],
    "and the worked example does exactly that.", "and the worked example does just that.")
sub("d12", ["sections", 4, "body"],
    "Think of a tag as a git branch name and a digest as a commit SHA.",
    "A tag works like a git branch name, and a digest like a commit SHA.")
full("d12", ["analogy"], "Think of an overhead projector",
     "An image works like a stack of transparent sheets on an overhead projector. "
     "Each sheet adds some drawings, and the screen shows all of them at once; the sheets are the layers. "
     "A container adds one blank sheet on top for its own notes. "
     "To erase a line on a lower sheet, you can only stick a white patch over it on a higher sheet. "
     "The line is hidden but still there, and the stack is no lighter. "
     "A real sheet can sit in only one stack at a time, though, while Docker puts the same layer into many images at once.")
full("d12", ["mistake"], "The classic mistake",
     "A `RUN rm -rf /var/lib/apt/lists/*` on its own line looks as if it slims the image, and it saves nothing. "
     "The files are hidden but still stored in the earlier layer. "
     "Clean up in the same `RUN` that created the files, or build in one stage and copy only the results into a fresh one.")
full("d12", ["real_world"], "PayFlow's deploy files",
     "A deploy file that says `payments-api:latest` can run a different build every time it pulls. "
     "So CI pushes each build with a version tag, and the deploy file pins the digest that CI printed. "
     "What ran in tests is then byte for byte what runs in production. "
     "A weekly job rebuilds base images, and a pull request updates the pinned digests, so nobody gets a new base by surprise.")
sub("d12", ["deeper", "body"],
    "Every object came from a URL that ends in its own digest. That is content addressing in practice: the client can hash what it got and check it against the name it asked for.",
    "Every object came from a URL that ends in its own digest, so the client can hash what it got and check it against the name it asked for.")
sub("d12", ["deeper", "body"],
    "Two more details are worth knowing on current Docker.",
    "Two more details explain output you will see on current Docker.")
sub("d12", ["deeper", "body"],
    "an image's ID is the digest of its index. That is why `docker build` output ends with",
    "an image's ID is the digest of its index. So `docker build` output ends with")

# ---------------------------------------------------------------- d13
sub("d13", ["sections", 0, "body"],
    "Each instruction that changes files adds a layer, exactly the layers you inspected on Day 12.",
    "Each instruction that changes files adds a layer, the same kind of layer you inspected on Day 12.")
sub("d13", ["sections", 1, "body"],
    "Two more arrive on Day 16. The `USER` instruction picks the user the app runs as, and `HEALTHCHECK` tells Docker how to test the app. The `LABEL` instruction adds key and value notes to the image, such as a link to its source repo.",
    "Day 16 adds `USER`, which picks the user the app runs as, and `HEALTHCHECK`, which tells Docker how to test the app. "
    "You will also see `LABEL`, which adds key and value notes to the image, such as a link to its source repo.")
sub("d13", ["sections", 3, "body"],
    "That second half trips most people up. Think of a row of dominoes: tip one over and everything after it falls.",
    "The second half is the one that surprises people. It works like a row of dominoes: tip one over and every one after it falls too.")
full("d13", ["mistake"], "The classic mistake",
     "Putting `COPY . .` before `RUN pip install` ties the slow install to every file in the folder. "
     "Every code change, even a comment, then invalidates the cache and reinstalls every package, and any junk in the folder lands in the image. "
     "Copy only `requirements.txt` first, install, and copy the code last.")
full("d13", ["real_world"], "PayFlow keeps",
     "One misplaced COPY makes every build reinstall all dependencies, so reviewers read Dockerfile changes as closely as code. "
     "Each service keeps its Dockerfile in its own repo, and changes to it go through the same code review. "
     "CI builds the image once per commit, and that same image moves from testing to production with only the environment variables changing.")
sub("d13", ["deeper", "body"],
    "That is also why `touch` alone never triggers a rebuild.",
    "For the same reason, `touch` alone never triggers a rebuild.")

# ---------------------------------------------------------------- d14
sub("d14", ["sections", 0, "body"],
    "which `docker rm` deletes. That is what you want. You should be able to throw away any container and start a fresh one, for an upgrade or after a crash.",
    "which `docker rm` deletes. You want it that way, because you should be able to throw away any container and start a fresh one, for an upgrade or after a crash.")
sub("d14", ["sections", 1, "body"],
    "A few behaviours are worth knowing before they surprise you:",
    "Four behaviours tend to surprise people the first time:")
sub("d14", ["sections", 1, "body"],
    "The lab's `docker/volume-backup.sh` does exactly that,",
    "The lab's `docker/volume-backup.sh` works this way,")
sub("d14", ["sections", 2, "body"], "Two things bite people:", "Two things often go wrong:")
sub("d14", ["sections", 3, "body"],
    "Docker's own docs say user-defined networks are better, and the next section shows why.",
    "Docker's own docs recommend user-defined networks instead, for the reasons in the next section.")
sub("d14", ["sections", 4, "body"],
    "That is how you build a proxy that talks to the outside on one network and to private services on another.",
    "A proxy uses this to talk to the outside on one network and to private services on another.")
full("d14", ["analogy"], "Think of an office building",
     "Docker networking works like an office building. "
     "The default bridge is an open-plan floor with no phone directory: you can call a colleague only if you know their extension, and extensions change when people move desks. "
     "A user-defined network is a floor with a receptionist who knows everyone on that floor by name. "
     "Volumes are the storage room in the basement, where the boxes stay while people come and go. "
     "Nobody can reach that room from another building, though: a volume stays on the one Docker host where you made it, and it does not follow your container to another machine.")
full("d14", ["mistake"], "The most common mistake",
     "Setting `REDIS_HOST=localhost` in a web container points the app at itself. "
     "Inside a container, `localhost` is that container, and nothing there listens on Redis's port. "
     "Put both containers on one user-defined network and use the other container's name, such as `REDIS_HOST=redis`.")
full("d14", ["real_world"], "PayFlow's developers",
     "An upgrade means `docker rm` and a fresh container, so developers run Postgres on their laptops with a named volume that the upgrade never touches. "
     "In production the databases are managed cloud services with backups and failover, rather than containers on one machine. "
     "CI jobs run integration tests on a fresh user-defined network per job, so parallel jobs on the same runner never see each other's containers.")
full("d14", ["worked", "steps", 6, "say"], "Clean up:",
     "Clean up: `docker rm -f web a b`, then `docker network rm demo` and `docker volume rm site`. "
     "Docker never deletes a named volume by itself; you always remove it on purpose.")
sub("d14", ["deeper", "body"],
    "That is the Day 6 lesson about signals, with real data at stake.",
    "This is Day 6's lesson about signals again, with real data at stake.")

# ---------------------------------------------------------------- d15
sub("d15", ["sections", 1, "body"],
    "Notice what the web service says: `REDIS_HOST: redis`. Redis has no `ports:` entry,",
    "The web service sets `REDIS_HOST: redis`. Redis has no `ports:` entry,")
sub("d15", ["sections", 4, "body"],
    "Two files with similar names do different jobs, and this trips most people up:",
    "Two files with similar names do different jobs, and they are easy to mix up:")
sub("d15", ["sections", 5, "body"], "One gotcha we hit while testing:", "One surprise from our testing:")
full("d15", ["analogy"], "compose.yaml is like the stage plan",
     "compose.yaml is like the stage plan a band sends to a venue. "
     "It lists each musician (service) and their instruments (images). "
     "It says who must be on stage and tuned before the show starts (depends_on with a health condition), and which microphones face the audience (ports). "
     "The crew reads the plan and sets the stage, and `down` clears it while the storage room (volumes) keeps its boxes. "
     "A real crew can improvise when something goes wrong on the night. "
     "Compose does only what the file says, and only on one machine.")
full("d15", ["mistake"], "It is easy to type",
     "Typing `docker compose down -v` when you meant `docker compose down` deletes the named volumes. "
     "Your Redis data, or a whole development database, is then gone for good. "
     "Use plain `down` day to day, and keep `down -v` for when you really want a clean start.")
full("d15", ["real_world"], "Every service repo at PayFlow",
     "A new engineer should be able to clone a service repo and start it, with its Postgres and Redis, in one command. "
     "A compose.yaml in every repo makes that work. "
     "A compose.override.yaml adds watch and debug tools on laptops, while CI runs `docker compose -f compose.yaml up -d --wait` to get real dependencies for integration tests. "
     "Production looks different: the same images run on Kubernetes (Day 30), and the databases are managed services.")
full("d15", ["worked", "steps", 6, "say"], "Now the gotcha.",
     "Plain `down` ignores profiled services, so the proxy keeps running and holds on to the network. "
     "Add the profile to remove everything.")

# ---------------------------------------------------------------- d16
sub("d16", ["sections", 0, "body"],
    "None of it helps at run time. Each extra file is one more thing to patch, one more thing a scanner flags, and one more tool an attacker can use.",
    "None of it helps at run time, but all of it needs patching and shows up in scan reports. "
    "An attacker who gets into the container can use those tools as well.")
sub("d16", ["sections", 0, "body"],
    "The gain is in what is missing. For a Kotlin service",
    "What you gain is an image without pip or build leftovers. For a Kotlin service")
sub("d16", ["sections", 0, "body"], "Day 24 builds exactly that.", "Day 24 builds that image.")
sub("d16", ["sections", 1, "body"],
    "The price is comfort. With no shell inside, `docker exec web sh` has nothing to run, so you need other ways to look inside.",
    "You pay for that when you debug: with no shell inside, `docker exec web sh` has nothing to run, so you need other ways to look inside.")
sub("d16", ["sections", 1, "body"],
    "Every build then starts from exactly the same base. The catch is that security fixes stop arriving by themselves.",
    "Every build then starts from the same base. Pinning has a cost too: security fixes stop arriving by themselves.")
sub("d16", ["sections", 2, "body"],
    "The files you copied in still belong to root, so the app can read its own code but cannot change it. That is what you want.",
    "The files you copied in still belong to root, so the app can read its own code but cannot change it, and neither can anyone who breaks into it.")
sub("d16", ["sections", 3, "body"], "Who acts on the status matters:", "What happens next depends on who reads the status:")
sub("d16", ["sections", 4, "body"], "Two scanners are worth knowing:", "Two scanners come up in this course:")
sub("d16", ["sections", 4, "body"],
    "That is why CI scans on every build, which Day 52 sets up.",
    "So CI scans on every build; Day 52 sets that up.")
full("d16", ["analogy"], "A multi-stage build is like",
     "A multi-stage build is like making a table in a workshop and delivering only the table. "
     "The saws, the glue and the sawdust stay in the workshop, and the customer gets a clean piece of furniture with nothing sharp attached. "
     "Docker's workshop does not go away, though. "
     "The build stage stays in the build cache on the machine that built it, so a secret you copied into that stage still sits there.")
full("d16", ["mistake"], "The most common mistake",
     "Passing a token with `--build-arg` or `ENV`, just for the build, puts it in the image history or config. "
     "Every registry and laptop that pulls the image then has a copy. "
     "Use `RUN --mount=type=secret` with `docker build --secret`, and rotate any token that ever went in as an ARG.")
full("d16", ["real_world"], "PayFlow's platform team",
     "Most services need the same hardening, so the platform team at PayFlow, a made-up payments company, keeps a template Dockerfile. "
     "It is multi-stage, with a pinned base digest, a numeric non-root user and a health check. "
     "CI builds each image once, scans it, and fails the build on any CRITICAL finding that has a fix. "
     "A bot opens pull requests when a base image digest changes, so rebuilding with patches is a routine review.")
full("d16", ["worked", "steps", 6, "say"], "Now the secret demo",
     "The secret demo runs in `~/code/docker-play`, with the two Dockerfiles from Files. "
     "The `ARG` version leaks the token into the history. "
     "The secret mount uses the token in the build, shows `****` in the log, and stores nothing.")
sub("d16", ["deeper", "body"],
    "That is the cost of a user with no home folder, and why the flag is in the lab's `CMD`.",
    "A user with no home folder costs you this error, which is why the lab's `CMD` has the flag.")

DST.write_text(json.dumps(d, ensure_ascii=False, indent=1) + "\n")
print("wrote", DST)
