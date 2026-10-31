"""Build content/p3.json (Part 3: Docker) from the lesson modules l11..l16.

Run: python3 build.py && python3 ../../../validate.py ../../../../content/p3.json
"""
import json
import pathlib

import l11
import l12
import l13
import l14
import l15
import l16
from common import L, ROOT


def res(key, why):
    t, u, k = L[key]
    return {"title": t, "url": u, "kind": k, "why": why}


PART = {
    "part": 3,
    "title": "Docker",
    "intro": (
        "This part teaches containers from the ground up. You run other people's images, open one up to see its layers, and write a Dockerfile for hello-devops. "
        "Then you connect it to Redis with volumes, networks and Compose, and finish with a small, non-root, scanned image on GHCR. "
        "Everything after this, from CI pipelines to Kubernetes, ships the image you build here."
    ),
    "lessons": [l11.LESSON, l12.LESSON, l13.LESSON, l14.LESSON, l15.LESSON, l16.LESSON],
    "recap": [
        "A container is a Linux process fenced in by namespaces and limited by cgroups; on a Mac it runs in a small Linux VM.",
        "An image is read-only layers plus a config, named by digests; a container adds one writable layer.",
        "Tags move and digests do not; one name can hold a variant for each CPU type.",
        "A Dockerfile builds an image step by step; order the steps so the cache saves the slow ones.",
        "Use exec form for CMD so the app is PID 1 and stops cleanly on SIGTERM.",
        "Keep data in volumes, and connect containers on a user-defined network where names work.",
        "compose.yaml describes the whole app; up, down, logs and config cover most days.",
        "Production images are multi-stage, non-root, health-checked, scanned and free of secrets.",
    ],
    "flashcards": [
        {"front": "What two Linux kernel features make a process a container?", "back": "Namespaces (what it can see) and cgroups (how much CPU and memory it can use)."},
        {"front": "Why does Docker Desktop on a Mac run a Linux VM?", "back": "Containers need a Linux kernel, and macOS does not have one."},
        {"front": "In `-p 8080:80`, which number is on your Mac?", "back": "8080. The rule is HOST:CONTAINER."},
        {"front": "What does exit code 137 mean?", "back": "The process was killed with SIGKILL (128 + 9), often after ignoring SIGTERM."},
        {"front": "What is an image made of?", "back": "Read-only layers, a config and a manifest that lists them by digest."},
        {"front": "Why does deleting a file in a later Dockerfile step not shrink the image?", "back": "The file stays in the earlier layer; the later layer only hides it."},
        {"front": "What is the difference between a tag and a digest?", "back": "A tag is a movable name; a digest is the hash of the content and never changes."},
        {"front": "What does `docker buildx imagetools inspect` show without pulling?", "back": "An image's digest and the platforms in its index."},
        {"front": "When does Docker rebuild a cached Dockerfile step?", "back": "When that step or anything before it changed; then every later step rebuilds too."},
        {"front": "CMD or ENTRYPOINT: which one do docker run arguments replace?", "back": "CMD. Arguments are added after ENTRYPOINT."},
        {"front": "Which one reaches the running container: ARG or ENV?", "back": "ENV. ARG exists only during the build."},
        {"front": "Inside a container, what does localhost mean?", "back": "The container itself, never your Mac or another container."},
        {"front": "What do user-defined networks have that the default bridge lacks?", "back": "Docker's DNS server at 127.0.0.11, so containers find each other by name."},
        {"front": "What does `docker compose down -v` delete that `down` keeps?", "back": "The named volumes, and the data in them."},
        {"front": "How do you make a Compose service wait until Redis is ready?", "back": "Give Redis a healthcheck and use depends_on with condition: service_healthy."},
        {"front": "How do you pass a token to a build without storing it?", "back": "RUN --mount=type=secret in the Dockerfile and docker build --secret."},
    ],
    "resources": [
        res("nana_full", "A three-hour course that covers most of this part at a slower pace, with diagrams and a small project."),
        res("nana_compose", "A full walk through Compose files and commands, useful next to Day 15."),
        res("fireship", "A seven-minute overview to watch first or to review the big picture after the part."),
        res("networkchuck", "Shows every Docker network type running, with containers talking to each other on screen."),
        res("bret_prod", "A conference talk on what changes when images go to production: users, health checks and small bases."),
        res("jvns_zine", "A short, paid zine of comics on namespaces, cgroups and the other kernel features behind containers."),
        res("c_container", "Docker's own concepts series: short pages on containers, images, layers, the cache and ports."),
        res("best", "Docker's checklist for writing Dockerfiles, to compare with your own after Day 16."),
        res("dive", "The tool from Day 12 for browsing layers and finding wasted space in any image."),
        res("twelve", "The original rule for keeping config in the environment, which hello-devops follows."),
    ],
    "quiz": [
        {
            "q": "Two containers from the same image both write to /tmp/cache.txt. What does each container see?",
            "options": [
                "The last write from either container",
                "Only its own file, in its own writable layer",
                "An error, because image files are read-only",
                "A shared file that both can append to",
            ],
            "answer": 1,
            "why": "Each container gets its own writable layer on top of the shared image layers, so their changes never meet.",
        },
        {
            "q": "A Dockerfile copies the whole project with `COPY . .` before installing dependencies. A teammate fixes a typo in README.md. What happens on the next build?",
            "options": [
                "Nothing rebuilds, because README.md is not code",
                "Only the COPY step reruns; the install stays cached",
                "Docker reruns the COPY, the install and every later step",
                "Docker re-downloads the base image",
            ],
            "answer": 2,
            "why": "The copied files changed, so that layer and every layer after it rebuild, unless .dockerignore leaves README.md out.",
        },
        {
            "q": "On an amd64 server, a container fails at once with `exec format error`. The image was built on a MacBook. What is the likely cause?",
            "options": [
                "The image holds only arm64 code",
                "The server is out of disk space",
                "The image has no CMD instruction",
                "The tag latest was not pushed",
            ],
            "answer": 0,
            "why": "A Mac builds arm64 code by default; without an amd64 variant in the index, the server cannot run it.",
        },
        {
            "q": "A web container and a Postgres container run on a user-defined network. Which `-p` options do they need for the web app to reach the database?",
            "options": [
                "-p 5432:5432 on the database",
                "-p on both containers",
                "-p 5432:5432 on the web container",
                "None; -p is only for traffic from outside",
            ],
            "answer": 3,
            "why": "Containers on one network reach each other on any port by name; publishing only matters for your Mac or other machines.",
        },
        {
            "q": "You run `docker compose down` and then `docker compose up -d`. Redis keeps its data in a named volume. What happens to the stored data?",
            "options": [
                "It is gone, because down removes everything",
                "It is still there, because named volumes survive down",
                "It is restored from the image's VOLUME line",
                "It survives only if you add --build",
            ],
            "answer": 1,
            "why": "down removes containers and networks; named volumes stay until you add -v or remove them yourself.",
        },
        {
            "q": "A container's STATUS says `Up 5 minutes (unhealthy)`. What does plain Docker do about it?",
            "options": [
                "It restarts the container at once",
                "It removes the container and starts a new one",
                "It stops sending traffic to the container",
                "Nothing; it only reports the status",
            ],
            "answer": 3,
            "why": "Standalone Docker records the health status but takes no action; Compose and other tools decide what to do with it.",
        },
        {
            "q": "Which Dockerfile line keeps a deploy repeatable even if someone pushes a new base image with the same tag?",
            "options": [
                "FROM python:3.14-slim@sha256:<digest>",
                "FROM python:latest",
                "FROM python:3.14-slim AS base",
                "FROM docker.io/library/python:3.14-slim",
            ],
            "answer": 0,
            "why": "A digest names one exact image, while any tag can be moved to different content.",
        },
        {
            "q": "After a scan, 5 HIGH findings sit in libraries inside pip, and the app never uses pip at run time. What is the cleanest fix?",
            "options": [
                "Mark them as accepted in the scanner",
                "Upgrade pip in the final stage",
                "Remove pip from the image you ship",
                "Switch the scanner to a different tool",
            ],
            "answer": 2,
            "why": "A package that is not in the image cannot be attacked or flagged, and the app does not need it.",
        },
        {
            "q": "A container runs as user 10001 and tries to write to a file owned by root with permissions rw-r--r-- (644). What happens?",
            "options": [
                "The write works, because containers ignore permissions",
                "The write fails with Permission denied",
                "The write works only in the image layer",
                "Docker changes the owner to 10001 first",
            ],
            "answer": 1,
            "why": "Only the owner, root, has write permission; everyone else, including uid 10001, can only read.",
            "from": "Part 1",
        },
        {
            "q": "An app inside a container listens on 127.0.0.1:8000, and you started it with `-p 8000:8000`. Why does curl from your Mac get no answer?",
            "options": [
                "Port 8000 is reserved on macOS",
                "The container needs EXPOSE 8000 as well",
                "Docker blocks HTTP traffic by default",
                "The app only accepts connections from inside the container",
            ],
            "answer": 3,
            "why": "127.0.0.1 is the container's own loopback; the app must bind 0.0.0.0 to accept traffic forwarded from outside.",
            "from": "Part 2",
        },
    ],
}

out = ROOT / "content/p3.json"
out.write_text(json.dumps(PART, indent=1, ensure_ascii=False) + "\n")
print("wrote", out)
