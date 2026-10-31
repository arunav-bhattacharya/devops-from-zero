import pathlib

from common import cap, join, lab, lines, ref, src, step, v1_step

C = lambda k: cap("d16", k)
SP = pathlib.Path("/tmp/claude-0/-home-user/5a31be1b-d2d7-5096-8c55-314d3e3b0058/scratchpad/v2p3/d16")
OUT = pathlib.Path(__file__).with_name("out")

# The final multi-stage build, trimmed to the build steps.
BUILD = "\n".join(
    l for l in C("build_final").split("\n")
    if l.startswith("$") or "[+] Building" in l or "[build " in l or "[stage-1 " in l
)

# Day 13 image versus the base image (rows: header, base, simple).
LS_SIMPLE = "\n".join(["$ docker image ls --filter reference=python:3.14-slim --filter reference=hello-devops:simple"] + C("ls").split("\n")[1:3] + C("ls").split("\n")[4:5])


def trivy_totals(name, shown):
    """The target and Total lines of a saved Trivy report, with the test image name mapped."""
    out = []
    for l in (OUT / name).read_text().split("\n"):
        if l.startswith("Total:") or (l and not l.startswith(("│", "├", "└", "┌", "=", "Legend", "-", "Report")) and ("(debian" in l or l.startswith("Python"))):
            out.append(l.replace("v2p3-hello-devops:simple", shown).replace("v2p3-hello-devops:final", shown))
    return "\n".join(out)


def trivy_row(name, shown):
    """The debian row of the summary table, without the table drawing."""
    for l in (OUT / name).read_text().split("\n"):
        if "(debian" in l and l.startswith("│"):
            cells = [c.strip() for c in l.strip("│").split("│")]
            return "│ " + " │ ".join([cells[0].replace("v2p3-hello-devops:final", shown)] + cells[1:]) + " │"


TRIVY = join(
    "$ trivy image --severity HIGH,CRITICAL hello-devops:simple",
    trivy_totals("trivy-simple.txt", "hello-devops:simple"),
    "$ trivy image --severity HIGH,CRITICAL hello-devops:1.0.0",
    trivy_totals("trivy-final.txt", "hello-devops:1.0.0"),
    "$ trivy image --severity HIGH,CRITICAL --ignore-unfixed hello-devops:1.0.0",
    trivy_row("trivy-final-fixed.txt", "hello-devops:1.0.0"),
)

SVG = (
    '<svg viewBox="0 0 560 236" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="A multi-stage build: the build stage installs packages into /venv; COPY --from copies only /venv into a fresh final stage, which adds app.py and runs as user 10001; the build stage is left behind">'
    # build stage outline
    '<line class="lnd" x1="8" y1="12" x2="232" y2="12"/><line class="lnd" x1="8" y1="226" x2="232" y2="226"/>'
    '<line class="lnd" x1="8" y1="12" x2="8" y2="226"/><line class="lnd" x1="232" y1="12" x2="232" y2="226"/>'
    '<text class="ts" x="120" y="216" font-size="11" text-anchor="middle">build stage, left behind</text>'
    '<rect class="bx" x="32" y="28" width="176" height="38" rx="10"/><text class="t" x="120" y="52" font-size="13" text-anchor="middle">python:3.14-slim</text>'
    '<rect class="bxp" x="32" y="88" width="176" height="38" rx="10"/><text class="tk" x="120" y="112" font-size="13" text-anchor="middle">pip install</text>'
    '<rect class="bxt" x="32" y="148" width="176" height="38" rx="10"/><text class="tk" x="120" y="172" font-size="13" text-anchor="middle">/venv</text>'
    '<line class="ln" x1="120" y1="66" x2="120" y2="84" marker-end="url(#ar)"/><line class="ln" x1="120" y1="126" x2="120" y2="144" marker-end="url(#ar)"/>'
    # final stage outline
    '<line class="lnd" x1="328" y1="12" x2="552" y2="12"/><line class="lnd" x1="328" y1="226" x2="552" y2="226"/>'
    '<line class="lnd" x1="328" y1="12" x2="328" y2="226"/><line class="lnd" x1="552" y1="12" x2="552" y2="226"/>'
    '<text class="ts" x="440" y="216" font-size="11" text-anchor="middle">final stage, shipped</text>'
    '<rect class="bx" x="352" y="28" width="176" height="38" rx="10"/><text class="t" x="440" y="52" font-size="13" text-anchor="middle">python:3.14-slim</text>'
    '<rect class="bxt" x="352" y="88" width="176" height="38" rx="10"/><text class="tk" x="440" y="112" font-size="13" text-anchor="middle">/venv, app.py</text>'
    '<rect class="bxo" x="352" y="148" width="176" height="38" rx="10"/><text class="tk" x="440" y="172" font-size="13" text-anchor="middle">USER 10001</text>'
    '<line class="ln" x1="440" y1="66" x2="440" y2="84" marker-end="url(#ar)"/><line class="ln" x1="440" y1="126" x2="440" y2="144" marker-end="url(#ar)"/>'
    # copy across
    '<line class="ln" x1="208" y1="167" x2="348" y2="109" marker-end="url(#ar)"/>'
    '<text class="ts" x="280" y="182" font-size="11" text-anchor="middle">COPY --from</text>'
    "</svg>"
)

LESSON = {
    "id": "d16",
    "title": "Production-ready images",
    "minutes": 50,
    "goal": "By the end you can turn the Day 13 image into a multi-stage, non-root image with a health check, scan it, keep build secrets out of it, and push it to GHCR for two CPU types.",
    "guess": {
        "q": "A Dockerfile has `ARG NPM_TOKEN`, and you build with `--build-arg NPM_TOKEN=abc123`. Where can someone who pulls the image find the token?",
        "options": [
            "Nowhere, because ARG values vanish after the build",
            "In `docker history`, next to the steps that used it",
            "Only in the build log on the machine that built it",
            "Only if a later ENV line copies it into the image",
        ],
        "answer": 1,
        "why": "Docker records the ARG values each RUN step used in the image history, so anyone with the image can read them. Build secrets need a secret mount instead.",
    },
    "terms": [
        {"term": "Multi-stage build", "plain": "A Dockerfile with several FROM lines, where only the last stage becomes the image you ship."},
        {"term": "Virtual environment", "plain": "A self-contained folder of Python packages (a venv) that a program can use on its own."},
        {"term": "Non-root user", "plain": "A normal user (not user ID 0) that the app runs as, so a break-in gets fewer rights."},
        {"term": "Health check", "plain": "A command Docker runs inside a container on a schedule; exit code 0 means the app works."},
        {"term": "CVE", "plain": "A public ID for one known security bug in a piece of software, such as CVE-2025-47273."},
        {"term": "Vulnerability scanner", "plain": "A tool that lists the packages in an image and reports which ones have known CVEs."},
        {"term": "Distroless image", "plain": "An image with only a language runtime and its libraries: no shell and no package manager."},
        {"term": "Build secret", "plain": "A password or token a build step needs, passed in a way that never stores it in the image."},
    ],
    "sections": [
        {
            "h": "Two stages: build with tools, ship without them",
            "body": (
                "The Day 13 image has one stage, so everything used to build the app ships with it. pip is there, and so is anything a compiler step would leave behind. "
                "None of it helps at run time. Each extra file is one more thing to patch, one more thing a scanner flags, and one more tool an attacker can use.\n\n"
                "A **multi-stage build** fixes that. One Dockerfile holds several `FROM` lines, and each starts a new stage from a clean base. "
                "A later stage copies what it needs from an earlier one with `COPY --from=<stage>`. Only the last stage becomes the image. The others stay behind in the build cache.\n\n"
                "The lab's final Dockerfile, in Files, has two stages:\n\n"
                "1. `build` starts from `python:3.14-slim`, makes a virtual environment in `/venv`, installs the requirements into it, and removes pip from it.\n"
                "2. The final stage starts from a fresh `python:3.14-slim`, removes the base image's own pip, and copies in `/venv` and `app.py`.\n\n"
                "A virtual environment, or venv, is a folder that holds a set of Python packages. That makes it easy to move: one `COPY --from=build /venv /venv` brings every installed package across. "
                "`ENV PATH=\"/venv/bin:$PATH\"` makes the venv's `gunicorn` the one that runs.\n\n"
                "For this small Python app the size barely moves: the content size went from 51.8 MB to 49.6 MB. The gain is in what is missing. "
                "For a Kotlin service the difference is large, because the build stage holds a JDK and Gradle and the final stage needs only a Java runtime and the jar. Day 24 builds exactly that."
            ),
            "refs": ref("c_multistage", "multistage", "bret_prod"),
        },
        {
            "h": "Choosing and pinning a base image",
            "body": (
                "The base image decides most of what is in your image, and so most of what a scanner finds. For a Python app the usual choices are:\n\n"
                "- `python:3.14`: full Debian with compilers and many tools. Big, and easy to debug.\n"
                "- `python:3.14-slim`: Debian with only what Python needs. The lab uses this one.\n"
                "- `python:3.14-alpine`: Alpine Linux, which uses a smaller C library called musl. Some packages with C code need extra work there.\n"
                "- Distroless images: only the runtime, with no shell and no package manager.\n"
                "- Docker Hardened Images (Day 12): distroless runtime images plus `-dev` variants with a shell for build stages.\n\n"
                "Smaller bases mean fewer packages, faster pulls and shorter scan reports. The price is comfort. With no shell inside, `docker exec web sh` has nothing to run, so you need other ways to look inside.\n\n"
                "Then pin what you chose. A tag moves when the publisher pushes an update, so `FROM python:3.14-slim` can mean different bytes next week. "
                "Add the digest to fix it: `FROM python:3.14-slim@sha256:cd89c30e...`, written with all 64 characters. The worked example shows how to find it. "
                "Every build then starts from exactly the same base. The catch is that security fixes stop arriving by themselves. "
                "Teams let a bot such as Dependabot or Renovate open a pull request when a new digest appears, and review it like any other change."
            ),
            "refs": ref("best", "dhi_use"),
        },
        {
            "h": "Run as a normal user",
            "body": (
                "A container runs as root, user ID 0, unless the image says otherwise. The Day 13 image did: `whoami` printed `root`. "
                "Namespaces fence the process in, but it is still root on a shared kernel. If an attacker breaks out through a bug in the kernel or in Docker, they arrive with root's rights.\n\n"
                "Two lines in the final stage fix it:\n\n"
                "- `RUN useradd --uid 10001 --no-create-home appuser` creates a normal user with no home folder.\n"
                "- `USER 10001` makes every later step, and the running container, use that user.\n\n"
                "Write the number in `USER`, not the name. Kubernetes can then check that an image runs as non-root without looking inside it. "
                "The files you copied in still belong to root, so the app can read its own code but cannot change it. That is what you want.\n\n"
                "The missing home folder has one side effect. Gunicorn 26 tries to open a control socket, a small file it listens on for admin commands, in the user's home folder. "
                "Without the flag, our test container logged `Control server error: [Errno 13] Permission denied: '/home/appuser'` at startup. The app still answered, but every start began with an error. "
                "The lab's `CMD` adds `--no-control-socket`, which turns that feature off."
            ),
            "refs": ref("best", "dockerfile"),
        },
        {
            "h": "Tell Docker how to test the app",
            "body": (
                "`docker ps` says `Up` as long as the main process lives. A process can be alive and still broken, for example stuck or failing every request. "
                "A `HEALTHCHECK` instruction tells Docker how to test the app from inside the container.\n\n"
                "The lab's check runs a one-line Python command every 30 seconds that requests `/healthz`, with a 3-second timeout. It uses Python because the slim image has no curl. "
                "Exit code 0 counts as a pass, and anything else as a failure. The status moves through three states:\n\n"
                "1. `starting`, until the first check has run.\n"
                "2. `healthy`, once a check passes.\n"
                "3. `unhealthy`, after 3 failures in a row, the default.\n\n"
                "`docker inspect -f '{{json .State.Health}}' web` shows the latest results with their exit codes and output.\n\n"
                "Who acts on the status matters:\n\n"
                "- Plain Docker only reports it. It does not restart an unhealthy container.\n"
                "- Compose uses it for `depends_on` with `condition: service_healthy` (Day 15).\n"
                "- Kubernetes ignores `HEALTHCHECK`. It has its own probes, which Day 35 points at the same `/healthz` and `/readyz` endpoints.\n\n"
                "Keep the check cheap and local. It should test that this process can answer, not that every database behind it is up."
            ),
            "refs": ref("dockerfile", "bret_prod"),
        },
        {
            "h": "Scanning: less inside means less to patch",
            "body": (
                "A CVE is a public ID for one known security bug, such as `CVE-2025-47273`. A vulnerability scanner lists every package in an image and checks each one against databases of CVEs. Two scanners are worth knowing:\n\n"
                "- Trivy, an open source scanner. Install it with `brew install trivy`.\n"
                "- Docker Scout, which comes with Docker Desktop: `docker scout quickview` gives a summary, and `docker scout cves` the full list.\n\n"
                "Read the results with care. Each finding has a severity from LOW to CRITICAL, and a status:\n\n"
                "- `fixed` means a newer version of the package fixes the bug. You can act on it.\n"
                "- `affected` means no fix exists yet. You can only wait and rebuild.\n\n"
                "On the day we scanned, all 44 HIGH findings in the Debian base were unfixed, and `--ignore-unfixed` dropped them to zero. "
                "Those come from the base image, so the fix is to rebuild once Debian ships patched packages. A smaller base would have fewer of them to begin with.\n\n"
                "Removing pip took away 5 more HIGH findings. They sat in libraries that pip carries inside itself, such as urllib3 and msgpack. "
                "The app never runs pip, so the lab uninstalls it in both stages.\n\n"
                "New CVEs are published every day, so your numbers will differ from ours. That is why CI scans on every build, which Day 52 sets up."
            ),
            "refs": ref("trivy", "scout_install"),
        },
        {
            "h": "Two CPU types, and a push to GHCR",
            "body": (
                "Your Mac builds arm64 images, and most servers run amd64. `docker buildx build --platform linux/amd64,linux/arm64` builds both and pushes one index with a manifest for each, as on Day 12. "
                "`RUN` steps for the other CPU type run through emulation, so the amd64 half of the build is slower on your Mac.\n\n"
                "GitHub Container Registry, `ghcr.io`, keeps images next to your code. Pushing there takes three things:\n\n"
                "1. A personal access token (classic) with the `write:packages` scope. GitHub Packages accepts only classic tokens.\n"
                "2. `docker login ghcr.io -u <your-github-user> --password-stdin`, with the token piped in so it never appears in your shell history.\n"
                "3. An image name of the form `ghcr.io/<your-github-user>/hello-devops:1.0.0`.\n\n"
                "Two details save you a search later:\n\n"
                "- A new package on GHCR is private at first. You can change its visibility in the package settings.\n"
                "- The label `org.opencontainers.image.source`, set to your repo's URL, links the package to the repo.\n\n"
                "A token on your laptop is fine for one manual push. Day 21 moves this push into GitHub Actions, which uses a short-lived token instead."
            ),
            "refs": ref("multiplat", "gh_ghcr", "gh_vis"),
        },
        {
            "h": "Secrets at build time",
            "body": (
                "Sometimes a build step needs a secret, such as a token to download a private package. The obvious ways all leak:\n\n"
                "- `ARG` with `--build-arg`: `docker history` shows the value.\n"
                "- `ENV`: the value is stored in the image config, so anyone who pulls the image can read it.\n"
                "- `COPY` a token file and `RUN rm` it later: the file stays in its layer, as Day 12 showed.\n\n"
                "In the worked example, `docker history` printed our fake token twice for the `ARG` version.\n\n"
                "BuildKit has a safe way. `RUN --mount=type=secret,id=api_token,env=API_TOKEN` hands the secret to that one `RUN` step, as an environment variable. "
                "Leave out `env=` and it appears as a file under `/run/secrets/` instead. You pass the secret to the build in one of two ways:\n\n"
                "- `--secret id=api_token,env=API_TOKEN` reads it from your shell's environment.\n"
                "- `--secret id=npmrc,src=$HOME/.npmrc` reads it from a file.\n\n"
                "The value never lands in a layer, the cache or the history. Run-time secrets, such as a database password, are a separate problem. "
                "They come from the environment when the container starts, never from the image. Day 34 shows how Kubernetes handles them."
            ),
            "refs": ref("secrets"),
        },
    ],
    "analogy": (
        "A multi-stage build is like building a table in a workshop and delivering only the table. "
        "The saws, the glue and the sawdust stay in the workshop, and the customer gets a clean piece of furniture with nothing sharp attached. "
        "The picture breaks in one place: Docker keeps the workshop (the build stage) in its cache on the machine that built it, so a secret you copied into the build stage still sits there."
    ),
    "diagram": SVG,
    "diagram_caption": "Only /venv crosses from the build stage; the final stage adds app.py and runs as user 10001.",
    "worked": {
        "title": "Harden the image, then check each gain",
        "steps": [
            step("Start from the Day 13 image. Tag it `hello-devops:simple` with `docker tag hello-devops:1.0.0 hello-devops:simple` so you can compare. It runs as root, and its content is 6 MB bigger than the base image it starts from.",
                 join(C("who_simple"), LS_SIMPLE)),
            step("Replace your Dockerfile with the final version from Files and build with the same tag, so later days use the hardened image. The steps now carry stage names: `build` for the first stage and `stage-1` for the unnamed final one. (Output trimmed to the build steps.)",
                 BUILD),
            step("Check the gains. The app now runs as uid 10001, pip is gone from the venv, and the content size dropped a little.",
                 join(C("who_final"), C("pip_gone2"), C("ls2"))),
            step("Run it and watch the health status. For the first 30 seconds it says `health: starting`; after the first check passes it says `healthy`.",
                 join(C("h_run"), C("h_ps1"), C("h_ps2"), C("h_curl"))),
            step("Scan both images with Trivy (output trimmed to the totals). The 5 Python findings came with pip and left with it. The 44 Debian findings had no fix on the day we ran this, so `--ignore-unfixed` hides them all. Your numbers will differ.",
                 TRIVY),
            step("Find the digest to pin the base image. `imagetools inspect` asks the registry without pulling anything. The digest names the whole multi-platform index.",
                 v1_step("d08", 5)),
            step("Now the secret demo, in `~/code/docker-play` with the two Dockerfiles from Files. The `ARG` version leaks the token into the history. The secret mount uses the token in the build, shows `****` in the log, and stores nothing.",
                 join(C("leak_build"), C("leak_hist"), C("safe_build"), C("safe_hist"))),
        ],
    },
    "code": [
        {
            "lang": "dockerfile",
            "title": "Dockerfile (the lab's final version)",
            "src": lab("Dockerfile"),
            "run": "docker build --build-arg APP_VERSION=1.0.0 -t hello-devops:1.0.0 .",
        },
        {
            "lang": "dockerfile",
            "title": "~/code/docker-play/leak/Dockerfile (the wrong way, for the demo)",
            "src": (SP / "leak/Dockerfile").read_text().rstrip("\n"),
            "run": "cd ~/code/docker-play && docker build -q --build-arg API_TOKEN=s3cr3t-demo-token -t leak leak && docker history --no-trunc leak",
        },
        {
            "lang": "dockerfile",
            "title": "~/code/docker-play/safe/Dockerfile (the right way)",
            "src": (SP / "safe/Dockerfile").read_text().rstrip("\n"),
            "run": "cd ~/code/docker-play && API_TOKEN=s3cr3t-demo-token docker build --progress=plain --secret id=api_token,env=API_TOKEN -t safe safe",
        },
    ],
    "commands": [
        {"cmd": "docker build --build-arg APP_VERSION=1.0.0 -t hello-devops:1.0.0 .", "what": "Build the multi-stage image; only the last stage is kept."},
        {"cmd": "docker run --rm hello-devops:1.0.0 id", "what": "Show which user and group the image runs as."},
        {"cmd": "docker inspect -f '{{json .State.Health}}' web", "what": "Show a container's health status and its latest check results."},
        {"cmd": "docker history --no-trunc hello-devops:1.0.0", "what": "Show every layer's full instruction, including ARG values used."},
        {"cmd": "trivy image --severity HIGH,CRITICAL hello-devops:1.0.0", "what": "Scan an image for known HIGH and CRITICAL CVEs."},
        {"cmd": "trivy image --severity HIGH,CRITICAL --ignore-unfixed hello-devops:1.0.0", "what": "Scan, but list only findings that have a fixed version."},
        {"cmd": "docker scout quickview hello-devops:1.0.0", "what": "Show a short vulnerability summary with Docker Scout."},
        {"cmd": "docker scout cves hello-devops:1.0.0", "what": "List every CVE Docker Scout finds in the image."},
        {"cmd": "docker buildx imagetools inspect python:3.14-slim", "what": "Show an image's digest and platforms without pulling it."},
        {"cmd": "docker build --secret id=api_token,env=API_TOKEN -t safe safe", "what": "Pass a secret from your shell's environment to RUN --mount steps only."},
        {"cmd": "echo \"$CR_PAT\" | docker login ghcr.io -u <your-github-user> --password-stdin", "what": "Log in to GHCR with a token read from stdin."},
        {"cmd": "docker tag hello-devops:1.0.0 ghcr.io/<your-github-user>/hello-devops:1.0.0", "what": "Give the image its full GHCR name."},
        {"cmd": "docker push ghcr.io/<your-github-user>/hello-devops:1.0.0", "what": "Upload the image; the last line shows its digest."},
        {"cmd": "docker buildx build --platform linux/amd64,linux/arm64 -t ghcr.io/<your-github-user>/hello-devops:1.0.0 --push .", "what": "Build for both CPU types and push one multi-platform image."},
        {"cmd": "docker buildx create --name multi --driver docker-container --use", "what": "Create a builder that can build several platforms, if the default one cannot."},
    ],
    "mistake": (
        "The most common mistake is passing a token with `--build-arg` or `ENV` just for the build. "
        "The value ends up in the image history or config, and every registry and laptop that pulls the image has a copy. "
        "Use `RUN --mount=type=secret` with `docker build --secret`, and rotate any token that ever went in as an ARG."
    ),
    "real_world": (
        "PayFlow's platform team keeps a template Dockerfile: multi-stage, a pinned base digest, a numeric non-root user and a health check. "
        "CI builds each image once, scans it, and fails the build on any CRITICAL finding that has a fix. "
        "A bot opens pull requests when a base image digest changes, so rebuilding with patches is a routine review."
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
            "On Day 21 a workflow pushes here. If it gets a permission error, add your repo under Manage Actions access in the package settings.",
        ],
        "done_when": "You are done when `docker buildx imagetools inspect ghcr.io/<your-github-user>/hello-devops:1.0.0` lists both linux/amd64 and linux/arm64.",
    },
    "explain_back": {
        "prompt": "Explain to a teammate in 3 to 4 sentences what makes the lab's final image safer than the Day 13 image. Mention the stages, the user, pip and the health check.",
        "answer": (
            "The final Dockerfile installs packages into a venv in a build stage and copies only that venv and app.py into a fresh final stage, so build leftovers never ship. "
            "It removes pip from both the venv and the base, which took away five known CVEs that pip carried with it. "
            "The app runs as user 10001 instead of root, so a break-in gets far fewer rights. "
            "A HEALTHCHECK lets Docker and Compose see whether the app actually answers, not only whether its process is alive."
        ),
    },
    "recap": [
        "A multi-stage build ships only the last stage; build tools stay behind.",
        "Pick a small base and pin it by digest, then let a bot propose updates.",
        "Run as a numeric non-root user, such as USER 10001.",
        "HEALTHCHECK reports whether the app answers; Compose uses it, Kubernetes uses its own probes.",
        "Scan every build, and read severity and fix status before you panic.",
        "Never pass secrets with ARG or ENV; use RUN --mount=type=secret.",
    ],
    "check": [
        {
            "q": "A Go team's single-stage image is 900 MB because it contains the Go compiler and module cache. Which change shrinks it the most?",
            "options": [
                "Add the module cache folder to .dockerignore",
                "Delete the compiler in a later RUN step",
                "Build the binary in one stage, copy it into a small one",
                "Build with --no-cache so old layers are not reused",
            ],
            "answer": 2,
            "why": "Only the last stage ships, so the compiler and cache stay in the build stage; deleting them later only hides them in an earlier layer.",
        },
        {
            "q": "A build must read `~/.npmrc`, which holds a token, to install private packages. Which approach keeps the token out of the image?",
            "options": [
                "COPY .npmrc, install, then RUN rm .npmrc",
                "Pass it with --secret and a RUN --mount=type=secret step",
                "Set ENV NPM_TOKEN in the build stage only",
                "Read it in an ARG and unset it after the install",
            ],
            "answer": 1,
            "why": "A secret mount exists only during that RUN step and is never written to a layer, the cache or the history.",
        },
        {
            "q": "A scan reports 30 HIGH CVEs, all with status `affected` and no fixed version, in your Debian base image. What is the sensible next step?",
            "options": [
                "Add an apt-get upgrade step and ship today",
                "Stop scanning, because the results cannot be fixed",
                "Rewrite the app in another language",
                "Track them, rebuild when fixes ship, and consider a smaller base",
            ],
            "answer": 3,
            "why": "No patched package exists yet, so an upgrade changes nothing; you rebuild when one ships, and a smaller base has fewer such packages at all.",
        },
    ],
    "interview": [
        {
            "q": "What makes a container image production-ready?",
            "a": (
                "I build it in stages, so only the runtime and the app ship, from a small base pinned by digest. "
                "It runs as a numeric non-root user, has a health check, and holds no secrets: build secrets go through secret mounts and run-time secrets come from the environment. "
                "CI scans every build and fails on serious findings that have a fix. "
                "Finally it is tagged with a real version, pushed for every CPU type we run, and deployed by digest."
            ),
        },
        {
            "q": "Why should a container not run as root?",
            "a": (
                "Containers share the host's kernel, so root in a container is still root to that kernel, only fenced in by namespaces. "
                "If an attacker gets code running in the app and then finds a kernel or runtime bug, root makes the escape much worse. "
                "Running as a normal user also stops the app from changing its own code or installing tools. "
                "Writing the user as a number lets Kubernetes enforce non-root without inspecting the image."
            ),
        },
        {
            "q": "How do you give a Docker build a secret, such as a token for a private package registry?",
            "a": (
                "I use BuildKit secret mounts: `RUN --mount=type=secret,id=token,env=TOKEN` in the Dockerfile and `docker build --secret id=token,env=TOKEN` on the command line. "
                "The secret exists only while that one RUN step runs and never lands in a layer or the history. "
                "ARG, ENV and copying a file then deleting it all leave the value in the image. "
                "In CI the secret comes from the CI system's secret store, passed the same way."
            ),
        },
    ],
    "deeper": {
        "minutes": 15,
        "body": (
            "Three experiments take the lab's Dockerfile further.\n\n"
            "First, the control socket. Run the final image with gunicorn started by hand and no `--no-control-socket` flag: "
            "`docker run -d --name nosock hello-devops:1.0.0 gunicorn --bind 0.0.0.0:8000 app:app`. "
            "Then read `docker logs nosock`. Ours ended with `[ERROR] Control server error: [Errno 13] Permission denied: '/home/appuser'`, while the container stayed up. "
            "That is the cost of a user with no home folder, and why the flag is in the lab's `CMD`. Remove it with `docker rm -f nosock`.\n\n"
            "Second, a small waste we found in the final stage. `docker history hello-devops:1.0.0` shows the `RUN pip uninstall -y pip` layer in the final stage at 4.85 MB, which is odd for a step that deletes things. "
            "Running pip makes Python save compiled `.pyc` files for every module it loads. `find /usr/local/lib/python3.14 -name '*.pyc' | wc -l` counted 0 in the base image and 150 in ours. "
            "Writing the line as `RUN PYTHONDONTWRITEBYTECODE=1 pip uninstall -y pip` stops that, and the same layer measured 28.7 kB. Try it and compare the two histories.\n\n"
            "Third, a hardened base. Docker's migration guide for Python uses `dhi.io/python:3.13-alpine3.23-dev` for the build stage and `dhi.io/python:3.13-alpine3.23` for the final one. "
            "You need `docker login dhi.io` with a free Docker account first. Moving the lab to such a base changes four things:\n\n"
            "- The final stage has no shell, so every `RUN` line there fails. Drop the `pip uninstall` and `useradd` lines.\n"
            "- The runtime image already runs as a non-root user and ships without pip.\n"
            "- The lab's `HEALTHCHECK` is in shell form, which `docker history` shows as `CMD-SHELL`. It needs `/bin/sh`, so rewrite it in exec form as a JSON list.\n"
            "- Debugging changes too: `docker exec web sh` has no shell to start.\n\n"
            "We did not build this version here, because pulling from dhi.io needs a login. "
            "Read [Use a Docker Hardened Image](https://docs.docker.com/dhi/how-to/use/) before you try, and compare the scan results with your slim image."
        ),
    },
    "sources": src("multistage", "secrets", "best", "trivy"),
}
