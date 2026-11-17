"""Fifth pass (book voice) for the Part 5 fields."""
import json, pathlib
ROOT = pathlib.Path(__file__).resolve().parents[4]
path = ROOT / "content/p5.json"
P = json.loads(path.read_text())

P["intro"] = r"""This part packs an app like a lunchbox: the meal plus everything it needs, sealed so it opens the same way anywhere. Every CI pipeline and Kubernetes deploy later in the course ships one thing: the hello-devops image you build here. You start by running other people's images and opening one up, then write a Dockerfile for hello-devops and connect it to Redis with volumes, networks and Compose. The part ends with a small, non-root, scanned image on GHCR."""

P["recap"] = [
    "A container is a Linux process fenced in by namespaces and limited by cgroups; on a Mac it runs in a small Linux VM.",
    "An image is read-only layers plus a config, named by digests; a container adds one writable layer.",
    "Tags move and digests do not, and one name can hold a variant for each CPU type.",
    "Order Dockerfile steps from rarely changed to often changed, so the cache saves the slow ones.",
    "Write CMD in exec form so the app is PID 1 and stops cleanly on SIGTERM.",
    "Keep data in volumes, and connect containers on a user-defined network where names work.",
    "compose.yaml describes the whole app; up, down, logs and config cover most days.",
    "Production images are multi-stage, non-root, health-checked, scanned and free of secrets.",
]

cards = [
    ("What two Linux kernel features make a process a container?", "Namespaces (what it can see) and cgroups (how much CPU and memory it can use)."),
    ("Why does Docker Desktop on a Mac run a Linux VM?", "Containers need a Linux kernel, and macOS does not have one."),
    ("In `-p 8080:80`, which number is on your Mac?", "8080. The rule is HOST:CONTAINER."),
    ("What does exit code 137 mean?", "The process was killed with SIGKILL (128 + 9), often after ignoring SIGTERM."),
    ("What is an image made of?", "Read-only layers, a config and a manifest that lists them by digest."),
    ("Why does deleting a file in a later Dockerfile step not shrink the image?", "The file stays in the earlier layer; the later layer only hides it."),
    ("What is the difference between a tag and a digest?", "A tag is a movable name; a digest is the hash of the content and never changes."),
    ("What does `docker buildx imagetools inspect` show without pulling?", "An image's digest and the platforms in its index."),
    ("When does Docker rebuild a cached Dockerfile step?", "When that step or anything before it changed; then every later step rebuilds too."),
    ("CMD or ENTRYPOINT: which one do the words after the image name in docker run replace?", "CMD. They are added after ENTRYPOINT."),
    ("Which one reaches the running container: ARG or ENV?", "ENV. ARG exists only during the build."),
    ("Inside a container, what does localhost mean?", "The container itself, never your Mac or another container."),
    ("What do user-defined networks have that the default bridge lacks?", "Docker's DNS server at 127.0.0.11, so containers find each other by name."),
    ("What does `docker compose down -v` delete that `down` keeps?", "The named volumes, and the data in them."),
    ("How do you make a Compose service wait until Redis is ready?", "Give Redis a healthcheck and use depends_on with condition: service_healthy."),
    ("How do you pass a token to a build without storing it?", "RUN --mount=type=secret in the Dockerfile and docker build --secret."),
]
assert len(cards) == len(P["flashcards"])
for f, (a, b) in zip(P["flashcards"], cards):
    f["front"], f["back"] = a, b

whys = [
    "Covers most of this part at a slower pace over three hours, with diagrams and a small project.",
    "Goes through Compose files and commands from start to end. Watch it next to Day 21.",
    "Seven minutes long. Watch it before the part, or after it to see how the pieces fit.",
    "Shows every Docker network type running, with containers talking to each other on screen.",
    "Bret Fisher on what changes when images go to production: users, health checks and small bases.",
    "Short comics (a paid zine) on namespaces, cgroups and the other kernel features behind containers.",
    "Docker's own short pages on containers, images, layers, the cache and ports, in plain words.",
    "Docker's checklist for writing Dockerfiles. Hold your own Dockerfile up against it after Day 22.",
    "The tool from Day 18 for browsing layers and finding wasted space in any image.",
    "The original rule for keeping settings in the environment, which hello-devops follows.",
]
assert len(whys) == len(P["resources"])
for r, w in zip(P["resources"], whys):
    r["why"] = w

quiz = [
    ("Two containers from the same image both write to /tmp/cache.txt. What does each container see?",
     "Each container gets its own writable layer on top of the shared image layers, so their changes never meet."),
    ("A Dockerfile copies the whole project with `COPY . .` before installing dependencies. A teammate fixes a typo in README.md. What happens on the next build?",
     "The copied files changed, so that layer and every layer after it rebuild, unless .dockerignore leaves README.md out."),
    ("On an amd64 server, a container fails at once with `exec format error`. The image was built on a MacBook. What is the likely cause?",
     "A Mac builds arm64 code by default; without an amd64 variant in the index, the server cannot run it."),
    ("A web container and a Postgres database container run on a user-defined network. Which `-p` options do they need for the web app to reach the database?",
     "Containers on one network reach each other on any port by name; publishing only matters for your Mac or other machines."),
    ("You run `docker compose down` and then `docker compose up -d`. Redis keeps its data in a named volume. What happens to the stored data?",
     "down removes containers and networks; named volumes stay until you add -v or remove them yourself."),
    ("A container's STATUS says `Up 5 minutes (unhealthy)`. What does plain Docker do about it?",
     "Plain Docker records the health status but takes no action; Compose and other tools decide what to do with it."),
    ("Which Dockerfile line keeps a deploy repeatable even if someone pushes a new base image with the same tag?",
     "A digest names one exact image, while any tag can be moved to different content."),
    ("After a scan, 5 HIGH findings sit in libraries inside pip, and the app never uses pip at run time. What is the cleanest fix?",
     "A package that is not in the image cannot be attacked or flagged, and the app does not need it."),
    ("A container runs as user 10001 and tries to write to a file owned by root with permissions rw-r--r-- (644). What happens?",
     "Only the owner, root, has write permission; everyone else, including uid 10001, can only read."),
    ("An app inside a container listens on 127.0.0.1:8000, and you started it with `-p 8000:8000`. Why does curl from your Mac get no answer?",
     "127.0.0.1 is the container's own loopback address; the app must listen on 0.0.0.0 to accept traffic forwarded from outside."),
]
assert len(quiz) == len(P["quiz"])
for q, (a, b) in zip(P["quiz"], quiz):
    q["q"], q["why"] = a, b

path.write_text(json.dumps(P, ensure_ascii=False, indent=1) + "\n")
print("p5 part fields written")
