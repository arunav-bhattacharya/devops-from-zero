"""Fifth pass (book voice) for d22."""
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from common import load, apply, save

path, P, L, OL = load(5, "d22")
new = {}

new["goal"] = r"""By the end you can turn the Day 19 image into a multi-stage, non-root image with a health check, scan it, keep build secrets out of it, and push it to GHCR for two CPU types."""

new["opening"] = r"""Picture your small lunch kitchen landing its first big customer: an office that wants 200 boxes a day. On day one their buyer opens a box to check it. Next to the lunch she finds a kitchen knife and a half-empty bag of flour. Taped under the lid is the key to your back door.

Nobody packed those on purpose. They were on the counter while the lunch was made, so they went into the box. Images fill up the same way, and the trap is easy to miss, because the app inside works perfectly. Last time, one Compose file started hello-devops and Redis on your laptop. The image inside still runs as root, carries pip, the tool that installed its packages, and has never been checked for known bugs. In this lesson, we'll leave the tools in the kitchen and make the app run as a normal user. Then we'll add a health check, scan the result, keep secrets out, and ship it to a registry for two kinds of CPU.

Before we start, make a guess, and keep it in mind."""

new["guess_q"] = r"""A token is a secret string that works like a password. A Dockerfile has `ARG NPM_TOKEN`, and you build with `--build-arg NPM_TOKEN=abc123`. Where can someone who pulls the image find the token?"""
new["guess_why"] = r"""Docker records the ARG values each RUN step used in the image history, so anyone with the image can read them: the key taped under the lid. Build secrets need a secret mount instead."""

new["terms"] = {
    "Multi-stage build": "A Dockerfile with several FROM lines, where only the last stage becomes the image you ship.",
    "Virtual environment": "A self-contained folder of Python packages (a venv) that a program can use on its own.",
    "Non-root user": "A normal user (not user ID 0, root) that the app runs as, so a break-in gets fewer rights.",
    "Health check": "A command Docker runs inside a container on a schedule; exit code 0 means the app works.",
    "CVE": "A public ID for one known security bug in a piece of software, such as CVE-2025-47273.",
    "Vulnerability scanner": "A tool that lists the packages in an image and reports which ones have known CVEs.",
    "Distroless image": "An image with only a language runtime and the code it needs: no shell and no package installer.",
    "Build secret": "A password or token a build step needs, passed in a way that never stores it in the image.",
}

S = []
S.append(("Two stages: cook in the kitchen, ship only the lunch", r"""The Day 19 image has one stage, so everything used to build the app ships with it. pip is there, and so is anything a compiler step would leave behind. None of it helps at run time, but all of it needs patching and shows up in scan reports. An attacker who gets into the container can use those tools as well. That is the knife in the lunchbox.

A multi-stage build fixes that. One Dockerfile holds several `FROM` lines, and each starts a new stage from a clean base. A later stage copies what it needs from an earlier one with `COPY --from=<stage>`. Only the last stage becomes the image. The others stay behind in the build cache, like tools left in the kitchen.

The lab's final Dockerfile, in Files, has two stages:

1. `build` starts from `python:3.14-slim`, makes a virtual environment in `/venv`, installs the requirements into it, and removes pip from it.
2. The final stage starts from a fresh `python:3.14-slim`, removes the base image's own pip, and copies in `/venv` and `app.py`.

A virtual environment, or venv, is a folder that holds a set of Python packages. That makes it easy to move: one `COPY --from=build /venv /venv` brings every installed package across. `ENV PATH="/venv/bin:$PATH"` makes the venv's `gunicorn` the one that runs.

Here is an honest result. For this small Python app the size barely moves: the content size went from 51.8 MB to 49.6 MB. What you gain is an image without pip or build leftovers. For a service written in Kotlin the difference is large. Its build stage holds a JDK and Gradle, big build tools, while the final stage needs only a Java runtime and the jar (the packed program). Day 30 builds that image.

The final stage still starts from somebody's base image. Which one, and which exact bytes?"""))

S.append(("Choosing and pinning a base image", r"""The base image decides most of what is in your image, and so most of what a scanner finds. For a Python app the usual choices are:

- `python:3.14`: full Debian with compilers and many tools. Big, and easy to debug.
- `python:3.14-slim`: Debian with only what Python needs. The lab uses this one.
- `python:3.14-alpine`: Alpine Linux, which uses a smaller C library called musl. Some packages with C code need extra work there.
- Distroless images: only the runtime, with no shell and no package manager.
- Docker Hardened Images (Day 18): distroless runtime images plus `-dev` variants with a shell for build stages.

Smaller bases mean fewer packages, faster pulls and shorter scan reports. You pay for that when you debug: with no shell inside, `docker exec web sh` has nothing to run, so you need other ways to look inside.

Then pin what you chose. A tag moves when the publisher pushes an update, so `FROM python:3.14-slim` can mean different bytes next week. Add the digest (Day 18's fingerprint) to fix it: `FROM python:3.14-slim@sha256:cd89c30e...`, written with all 64 characters. The worked example shows how to find it. Every build then starts from the same base.

Pinning has a cost too: security fixes stop arriving by themselves. Teams let a bot such as Dependabot or Renovate open a pull request (a proposed change for review) when a new digest appears, and review it like any other change.

The base is chosen. Next: who the app runs as inside it."""))

S.append(("Run as a normal user", r"""A container runs as root, user ID 0, unless the image says otherwise. The Day 19 image did: `whoami` printed `root`. Namespaces fence the process in, but it is still root on a shared kernel. If an attacker breaks out through a bug in the kernel or in Docker, they arrive with root's rights.

Two lines in the final stage fix it:

- `RUN useradd --uid 10001 --no-create-home appuser` creates a normal user with no home folder.
- `USER 10001` makes every later step, and the running container, use that user.

Root in a container is still root to the kernel. Run as a number, such as USER 10001.

Write the number in `USER`, not the name. A name means nothing until someone reads the image's `/etc/passwd`, while `10001` is plainly not 0. So Kubernetes can check that an image runs as non-root without looking inside it. The files you copied in still belong to root, so the app can read its own code but cannot change it, and neither can anyone who breaks into it.

The missing home folder made one thing fail in public. Gunicorn 26 tries to open a control socket, a special file that other programs can use to send it commands, in the user's home folder. Without a flag, our test container logged `Control server error: [Errno 13] Permission denied: '/home/appuser'` at startup. The app still answered, but every start began with an error. The lab's `CMD` adds `--no-control-socket`, which turns that feature off.

The app runs safely now. But "running" still doesn't tell you it works."""))

S.append(("Tell Docker how to test the app", r"""`docker ps` says `Up` as long as the main process lives. A process can be alive and still broken, for example stuck or failing every request, like a cook who is at work but has burned every dish. A `HEALTHCHECK` instruction tells Docker how to test the app from inside the container.

The lab's check runs a one-line Python command every 30 seconds that requests `/healthz`, with a 3-second timeout. It uses Python because the slim image has no curl. Exit code 0 counts as a pass, and anything else as a failure. The status moves through three states:

1. `starting`, until the first check has run.
2. `healthy`, once a check passes.
3. `unhealthy`, after 3 failures in a row, the default.

`docker inspect -f '{{json .State.Health}}' web` shows the latest results with their exit codes and output.

What happens next depends on who reads the status:

- Plain Docker only reports it. It does not restart an unhealthy container.
- Compose uses it for `depends_on` with `condition: service_healthy` (Day 21).
- Kubernetes ignores `HEALTHCHECK`. It has its own probes, which Day 43 points at the same `/healthz` and `/readyz` endpoints.

Keep the check cheap and local. It should test that this process can answer, not that every database behind it is up.

The image is smaller, safer and self-testing. How many known bugs does it still carry?"""))

S.append(("Scanning: less inside means less to patch", r"""A CVE is a public ID for one known security bug, such as `CVE-2025-47273`. A vulnerability scanner lists every package in an image and checks each one against databases of CVEs, like a food inspector checking each ingredient against a recall list. Two scanners come up in this course:

- Trivy, an open source scanner. Install it with `brew install trivy`.
- Docker Scout, which comes with Docker Desktop: `docker scout quickview` gives a summary, and `docker scout cves` the full list.

Read the results with care. Each finding has a severity from LOW to CRITICAL, and a status:

- `fixed` means a newer version of the package fixes the bug. You can act on it.
- `affected` means no fix exists yet. You can only wait and rebuild.

On the day we scanned, all 44 HIGH findings in the Debian base were unfixed, and `--ignore-unfixed` dropped them to zero. Those come from the base image, so the fix is to rebuild once Debian ships patched packages. A smaller base would have fewer of them to begin with.

Removing pip took away 5 more HIGH findings. They sat in libraries that pip carries inside itself, such as urllib3 and msgpack. The app never runs pip, so the lab uninstalls it in both stages.

New CVEs are published every day, so your numbers will differ from ours, and CI scans again on every build. Day 63 sets that up.

The image is ready to leave your laptop."""))

S.append(("Two CPU types, and a push to GHCR", r"""Your Mac builds arm64 images, and most servers run amd64. The command `docker buildx build --platform linux/amd64,linux/arm64` builds both and pushes one index with a manifest for each, as on Day 18. The `RUN` steps for the other CPU type run through emulation, so the amd64 half of the build is slower on your Mac.

GitHub Container Registry, `ghcr.io`, keeps images next to your code. Pushing there takes three things:

1. A personal access token (classic) with the `write:packages` scope, the one permission it needs. GitHub Packages accepts only classic tokens.
2. `docker login ghcr.io -u <your-github-user> --password-stdin`, with the token piped in so it never appears in your shell history.
3. An image name of the form `ghcr.io/<your-github-user>/hello-devops:1.0.0`.

Two details save you a search later:

- A new package on GHCR is private at first. You can change its visibility in the package settings.
- The label `org.opencontainers.image.source`, set to your repo's URL, links the package to the repo.

A token on your laptop is fine for one manual push. Day 27 moves this push into GitHub Actions, which uses a short-lived token instead.

That token is a secret you typed at your own terminal. Some secrets, though, have to reach the build itself."""))

S.append(("Secrets at build time", r"""Sometimes a build step needs a secret, such as a token to download a private package. The obvious ways all leak:

- `ARG` with `--build-arg`: `docker history` shows the value.
- `ENV`: the value is stored in the image config, so anyone who pulls the image can read it.
- `COPY` a token file and `RUN rm` it later: the file stays in its layer, as Day 18 showed.

In the worked example, `docker history` printed our fake token twice for the `ARG` version. That is the back door key under the lid, readable by anyone who pulls the image.

BuildKit has a safe way. `RUN --mount=type=secret,id=api_token,env=API_TOKEN` hands the secret to the temporary container of that one `RUN` step (Day 19), as an environment variable. Leave out `env=` and it appears as a file under `/run/secrets/` instead. You pass the secret to the build in one of two ways:

- `--secret id=api_token,env=API_TOKEN` reads it from your shell's environment.
- `--secret id=npmrc,src=$HOME/.npmrc` reads it from a file.

The value never lands in a layer, the cache or the history. If a token ever did go in as an ARG, treat it as leaked and replace it.

**A secret in ARG, ENV or a deleted file ships with the image. Mount it instead.**

Run-time secrets, such as a database password, are a separate problem. They come from the environment when the container starts, never from the image. Day 42 shows how Kubernetes handles them.

That is the limit of this part: every build, scan and push so far happened by hand, on one laptop. Part 6 hands the same steps to CI, so they run the same way on every change."""))
new["sections"] = S

new["drop"] = ["analogy", "mistake"]
new["real_world"] = r"""Most services need the same hardening, so the platform team at PayFlow, a made-up payments company, keeps a template Dockerfile. It is multi-stage, with a pinned base digest, a numeric non-root user and a health check. CI builds each image once, scans it, and fails the build on any CRITICAL finding that has a fix. A bot opens pull requests when a base image digest changes, so rebuilding with patches is a routine review."""

new["diagram_caption"] = "Only /venv crosses from the build stage; the final stage adds app.py and runs as user 10001."

new["worked"] = [
    r"""Start from the Day 19 image. Tag it `hello-devops:simple` with `docker tag hello-devops:1.0.0 hello-devops:simple` so you can compare. It runs as root, and its content is 6 MB bigger than the base image it starts from.""",
    r"""Replace your Dockerfile with the final version from Files and build with the same tag, so later days use the hardened image. The steps now carry stage names: `build` for the first stage and `stage-1` for the unnamed final one. (Output trimmed to the build steps.)""",
    r"""Check the gains. The app now runs as uid 10001, pip is gone from the venv, and the content size dropped a little.""",
    r"""Run it and watch the health status. For the first 30 seconds it says `health: starting`; after the first check passes it says `healthy`.""",
    r"""Scan both images with Trivy (output trimmed to the totals). The 5 Python findings came with pip and left with it. The 44 Debian findings had no fix on the day we ran this, so `--ignore-unfixed` hides them all. Your numbers will differ.""",
    r"""Find the digest to pin the base image. `imagetools inspect` asks the registry without pulling anything. The digest names the whole multi-platform index.""",
    r"""The secret demo runs in `~/code/docker-play`, with the two Dockerfiles from Files. The `ARG` version leaks the token into the history. The secret mount uses the token in the build, hides the token behind stars in the log, and stores nothing.""",
]

new["task"] = {
    "steps": [
        r"""Create a GitHub personal access token (classic) with only the `write:packages` scope and a short expiry. GitHub's docs give the link `https://github.com/settings/tokens/new?scopes=write:packages` for this.""",
        r"""Log in to ghcr.io with your GitHub user name and the token. Keep the token out of files and out of your shell history.""",
        r"""Tag your local `hello-devops:1.0.0` with its GHCR name and push it. Copy the digest from the last line.""",
        r"""Find the package on your GitHub profile under Packages, and check its visibility.""",
        r"""Delete the local GHCR-tagged image, pull it back by digest, run it, and curl it.""",
        r"""Build and push both CPU types in one command with `docker buildx build`.""",
        r"""Check the pushed tag with `docker buildx imagetools inspect` and find both platforms.""",
        r"""Scan the pushed image with `docker scout quickview` or `trivy image`, and write down the counts.""",
        r"""Commit the multi-stage Dockerfile and push.""",
    ],
    "hints": [
        r"""Add `--label org.opencontainers.image.source=https://github.com/<your-github-user>/hello-devops` to your build to link the package to your repo.""",
        r"""If Docker says the builder cannot build several platforms, create one with `docker buildx create --name multi --driver docker-container --use`.""",
        r"""On Day 27 a workflow pushes here. If it gets a permission error, add your repo under Manage Actions access in the package settings.""",
    ],
    "done_when": r"""You are done when `docker buildx imagetools inspect ghcr.io/<your-github-user>/hello-devops:1.0.0` lists both linux/amd64 and linux/arm64.""",
}

new["explain_back"] = {
    "prompt": r"""Explain to a teammate in 3 to 4 sentences what makes the lab's final image safer than the Day 19 image. Mention the stages, the user, pip and the health check.""",
    "answer": r"""The final Dockerfile installs packages into a venv in a build stage and copies only that venv and app.py into a fresh final stage, so build leftovers never ship. It removes pip from both the venv and the base, which took away five known CVEs that pip carried with it. The app runs as user 10001 instead of root, so a break-in gets far fewer rights. A HEALTHCHECK lets Docker and Compose see whether the app actually answers, not only whether its process is alive.""",
}

new["recap"] = [
    "A multi-stage build ships only the last stage; build tools stay behind.",
    "Pick a small base and pin it by digest, then let a bot propose updates.",
    "Run as a numeric non-root user, such as USER 10001.",
    "HEALTHCHECK reports whether the app answers; Compose uses it, Kubernetes uses its own probes.",
    "Scan every build, and read severity and fix status before you panic.",
    "Never pass secrets with ARG or ENV; use RUN --mount=type=secret. So far all of this runs by hand; Part 6 moves it to CI.",
]

new["check"] = [
    (r"""A team's single-stage image is 900 MB because it contains the Go compiler (Go is a programming language) and its module cache. Which change shrinks it the most?""",
     r"""Only the last stage ships, so the compiler and cache stay in the build stage; deleting them later only hides them in an earlier layer."""),
    (r"""A build must read `~/.npmrc`, a settings file that holds a token, to install private packages. Which approach keeps the token out of the image?""",
     r"""A secret mount exists only during that RUN step and is never written to a layer, the cache or the history."""),
    (r"""A scan reports 30 HIGH CVEs, all with status `affected` and no fixed version, in your Debian base image. What is the sensible next step?""",
     r"""No patched package exists yet, so an upgrade changes nothing; you rebuild when one ships, and a smaller base has fewer such packages at all."""),
]

new["interview"] = [
    (r"""What makes a container image production-ready?""",
     r"""I build it in stages, so only the runtime and the app ship, from a small base pinned by digest. It runs as a numeric non-root user, has a health check, and holds no secrets: build secrets go through secret mounts and run-time secrets come from the environment. CI scans every build and fails on serious findings that have a fix. Finally it is tagged with a real version, pushed for every CPU type we run, and deployed by digest."""),
    (r"""Why should a container not run as root?""",
     r"""Containers share the host's kernel, so root in a container is still root to that kernel, only fenced in by namespaces. If an attacker gets code running in the app and then finds a kernel or runtime bug, root makes the escape much worse. Running as a normal user also stops the app from changing its own code or installing tools. Writing the user as a number lets Kubernetes enforce non-root without inspecting the image."""),
    (r"""How do you give a Docker build a secret, such as a token for a private package registry?""",
     r"""I use BuildKit secret mounts: `RUN --mount=type=secret,id=token,env=TOKEN` in the Dockerfile and `docker build --secret id=token,env=TOKEN` on the command line. The secret exists only while that one RUN step runs and never lands in a layer or the history. ARG, ENV and copying a file then deleting it all leave the value in the image. In CI the secret comes from the CI system's secret store, passed the same way."""),
]

new["closing"] = r"""We started with a lunchbox that held a knife, a bag of flour and the key to the back door. Our final image leaves pip in the build stage, runs as user 10001, tests itself every 30 seconds, and keeps the token out of its history. Pick an image you use and run `docker history --no-trunc` on it, then search the output for words such as TOKEN, PASSWORD or KEY. If anything turns up, that key is taped under the lid for everyone who pulls it.

Next, we'll stop doing all of this by hand. How does a team agree on a change, and let CI build, test and ship it every time?"""

apply(L, new)
save(path, P, L, OL)
