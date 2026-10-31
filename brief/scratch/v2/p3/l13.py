from common import V1, cap, join, lab, lines, ref, src, step, v1_step

C = lambda k: cap("d13", k)

# The cached rebuild, trimmed to the lines that tell the story.
REBUILD = "\n".join(
    l for l in C("build2").split("\n")
    if l.startswith("$") or "[+] Building" in l or "/5]" in l or l.startswith(" => exporting to image")
)

V1D06 = next(x for x in V1["lessons"] if x["id"] == "d06")
SVG = V1D06["diagram"]

LESSON = {
    "id": "d13",
    "title": "Dockerfiles: package your own app",
    "minutes": 50,
    "goal": "By the end you can write a Dockerfile for hello-devops, explain every instruction in it, order the steps so rebuilds are fast, and choose between CMD and ENTRYPOINT.",
    "guess": {
        "q": "A Dockerfile does `COPY . .` and then `RUN pip install -r requirements.txt`. You change one comment in app.py and rebuild. What happens?",
        "options": [
            "Only app.py is copied again; pip install is reused",
            "pip install runs again, because a layer above it changed",
            "Docker rebuilds everything, including the base image",
            "Nothing changes until you delete the old image",
        ],
        "answer": 1,
        "why": "A changed layer invalidates every layer after it, and `COPY . .` changes whenever any file changes. Copy requirements.txt and install first, then copy the code, so code edits skip the slow install.",
    },
    "terms": [
        {"term": "Dockerfile", "plain": "A text file of instructions that tells Docker how to build an image, read from top to bottom."},
        {"term": "Base image", "plain": "The image a Dockerfile starts from with FROM, such as python:3.14-slim."},
        {"term": "Build context", "plain": "The folder you pass to docker build; COPY can only take files from inside it."},
        {"term": "Build cache", "plain": "Layers saved from earlier builds, reused when an instruction and everything before it are unchanged."},
        {"term": "Exec form", "plain": "Writing CMD or ENTRYPOINT as a JSON list, so the program runs directly as PID 1 with no shell in between."},
        {"term": "ENTRYPOINT", "plain": "The fixed program a container runs; arguments from docker run are added after it."},
        {"term": "Build argument", "plain": "A variable declared with ARG and set with --build-arg; it exists only while the image builds."},
    ],
    "sections": [
        {
            "h": "A Dockerfile is a recipe Docker follows from top to bottom",
            "body": (
                "Docker builds an image by following a plain text file named `Dockerfile`. "
                "It runs the instructions in order, and each one starts from the result of the one before. "
                "Each instruction that changes files adds a layer, exactly the layers you inspected on Day 12.\n\n"
                "The Dockerfile lives in git next to the app, and teammates review changes to it like any other code. "
                "That is the Day 1 idea of everything as code, applied to packaging.\n\n"
                "You build with `docker build -t hello-devops:1.0.0 .`. The `-t` flag names and tags the result, and the final dot is the build context, which has its own section below. "
                "The builder behind `docker build` is called BuildKit. It is the default in Docker Desktop and Docker Engine, and it is the program that prints the `[+] Building` progress you will see in the worked example.\n\n"
                "Today you write a Dockerfile with one stage that runs as root. "
                "It is the right first step, because every line is easy to see. Day 16 turns it into the multi-stage, non-root version that the lab ships."
            ),
            "refs": ref("c_dockerfile", "fireship"),
        },
        {
            "h": "The instructions you will use",
            "body": (
                "Most Dockerfiles use a handful of instructions:\n\n"
                "- `FROM` picks the base image to start from, such as `python:3.14-slim`.\n"
                "- `WORKDIR` sets the folder that later instructions work in, and creates it.\n"
                "- `COPY` copies files from the build context into the image. `ADD` can also fetch URLs and unpack archives; prefer `COPY` unless you need that.\n"
                "- `RUN` runs a command at build time, such as `pip install`, and saves the result as a layer.\n"
                "- `ENV` sets an environment variable for later steps and for the running container.\n"
                "- `ARG` declares a variable that exists only during the build.\n"
                "- `EXPOSE` documents the port the app listens on. It publishes nothing; `-p` does that.\n"
                "- `CMD` and `ENTRYPOINT` set what the container runs when it starts.\n\n"
                "Two more arrive on Day 16. The `USER` instruction picks the user the app runs as, and `HEALTHCHECK` tells Docker how to test the app. "
                "The `LABEL` instruction adds key and value notes to the image, such as a link to its source repo.\n\n"
                "Read the Day 13 Dockerfile in the Files section with this list next to it. Every line is one of these instructions, with a comment that says why it is there."
            ),
            "refs": ref("dockerfile"),
        },
        {
            "h": "The build context and .dockerignore",
            "body": (
                "The dot in `docker build -t hello-devops:1.0.0 .` is the **build context**: the folder whose files the build may use. "
                "A `COPY` can only take files from inside it, so `COPY ../secrets.txt .` fails. "
                "Docker also looks for the file named `Dockerfile` in that folder, unless you name another one with `-f`.\n\n"
                "A `.dockerignore` file in that folder lists files the build must never see, with patterns like `.gitignore`. The lab's file keeps out:\n\n"
                "- `.git` and `.github`, the repo's history and workflows\n"
                "- `.venv` and Python caches, which belong to your Mac only\n"
                "- folders for later days, such as `infra`, `k8s` and `chart`\n"
                "- Markdown files, which the app does not need\n\n"
                "Our Dockerfile copies two files by name, so for now the ignore file is a safety net. "
                "It starts to matter the day someone writes `COPY . .`. "
                "In a test, a folder with a 10 MB `.venv` sent `10.00MB` of context to the builder on every build. "
                "After adding `.venv` to `.dockerignore`, the same build sent 100 bytes. "
                "Without the ignore file, `COPY . .` would also bake your `.git` folder and any local secret files into the image."
            ),
            "refs": ref("context"),
        },
        {
            "h": "The build cache, and why order matters",
            "body": (
                "Docker keeps every layer it builds in its build cache. On the next build it checks each instruction in order. "
                "If the instruction and everything before it are unchanged, Docker reuses the saved layer and prints `CACHED`. "
                "If something changed, Docker rebuilds that layer and every layer after it, even ones whose instructions did not change. "
                "That second half trips most people up. Think of a row of dominoes: tip one over and everything after it falls.\n\n"
                "What counts as changed depends on the instruction:\n\n"
                "- For `COPY` and `ADD`, Docker checks the contents of the files. Their modification time is ignored, so `touch app.py` changes nothing.\n"
                "- For `RUN`, Docker only compares the command text. `RUN apt-get update` stays cached for months, even if new packages exist.\n\n"
                "So order the steps from rarely changed to often changed:\n\n"
                "1. `FROM` the base image.\n"
                "2. `COPY requirements.txt` on its own.\n"
                "3. `RUN pip install`, the slow step.\n"
                "4. `COPY app.py`, which changes all the time.\n\n"
                "With this order, a code edit rebuilds only the last small layer. In the worked example that rebuild takes 0.3 seconds, against about 10 seconds for a fresh pip install."
            ),
            "refs": ref("c_cache", "cache_inval", "cache_opt"),
        },
        {
            "h": "CMD, ENTRYPOINT and who is PID 1",
            "body": (
                "`CMD` and `ENTRYPOINT` both say what runs when a container starts. They differ in how `docker run` arguments treat them:\n\n"
                "- `CMD` is a default. Anything you type after the image name replaces it.\n"
                "- `ENTRYPOINT` is fixed. Anything you type after the image name is added to it as arguments.\n"
                "- With both, `ENTRYPOINT` is the program and `CMD` gives its default arguments.\n\n"
                "A tiny image with `ENTRYPOINT [\"echo\", \"Hello,\"]` and `CMD [\"world\"]` shows it. `docker run greeter` printed `Hello, world`, and `docker run greeter Ana` printed `Hello, Ana`. "
                "`--entrypoint` swaps the program itself. For a web app, `CMD` alone is the simple choice.\n\n"
                "Write both in exec form, a JSON list such as `[\"gunicorn\", \"app:app\"]`. Then your app runs directly as PID 1 and receives the SIGTERM from `docker stop`. "
                "In shell form, `CMD gunicorn app:app`, Docker runs `/bin/sh -c \"gunicorn app:app\"`. The shell becomes PID 1 and does not pass SIGTERM on. "
                "We measured both. The shell-form container needed 10.2 seconds to stop and ended with code 137. The exec-form one stopped in 0.6 seconds with code 0. "
                "PID 1 is also special in Linux: it gets no default signal handlers, which is why `sleep` ignored SIGTERM on Day 11."
            ),
            "refs": ref("json_args", "dockerfile"),
        },
        {
            "h": "ARG, ENV and config from the environment",
            "body": (
                "`ARG` and `ENV` both set variables, at different times:\n\n"
                "- `ARG` exists only while the image builds. You set it with `--build-arg NAME=value`.\n"
                "- `ENV` is stored in the image and is present when the container runs. `docker run -e NAME=value` overrides it.\n\n"
                "A test image showed the difference. With `--build-arg BUILD_NOTE=hello`, a `RUN` step printed `at build time: hello`, and the running container printed `at run time: not set`. "
                "To keep a build value, copy it: `ARG APP_VERSION` followed by `ENV APP_VERSION=$APP_VERSION`, as our Dockerfile does.\n\n"
                "One warning before you reach for either one: `docker history` shows ARG values in plain text, so never pass passwords or tokens this way. Day 16 shows the safe way.\n\n"
                "Why put settings in the environment at all? [The Twelve-Factor App](https://12factor.net/config) is a well-known set of rules for web apps. "
                "Its config rule says to keep settings that change between deploys out of the code, in environment variables. "
                "Then one image runs in every environment, and only the variables differ. hello-devops reads four of them:\n\n"
                "- `APP_VERSION`, the version it reports\n"
                "- `GREETING`, the message it returns\n"
                "- `REDIS_HOST`, where Redis runs (empty means count in memory)\n"
                "- `PORT`, used only when you run `python app.py`\n\n"
                "`PYTHONUNBUFFERED=1` is not one of the app's settings. It makes Python print log lines at once, so `docker logs` shows them as they happen."
            ),
            "refs": ref("variables", "twelve"),
        },
        {
            "h": "Tags, build checks and docker init",
            "body": (
                "Tag your own images with real versions, such as `1.0.0`; Day 17 explains version numbers. "
                "Leave the tag out and Docker uses `latest`, which only means whatever was built last. "
                "In `FROM`, name a specific base such as `python:3.14-slim`, never bare `python`, or your build gets whatever `latest` points to on the day you build. "
                "One image can carry several tags: `docker tag hello-devops:1.0.0 hello-devops:stable` adds a second name and copies nothing.\n\n"
                "`docker build --check .` lints a Dockerfile without building it. "
                "We ran it on a file with three common slips, and it named each with a line number:\n\n"
                "- `FromAsCasing`: `FROM ... as base` mixes upper and lower case\n"
                "- `LegacyKeyValueFormat`: `ENV GREETING Hello` should be `ENV GREETING=Hello`\n"
                "- `JSONArgsRecommended`: a shell-form `CMD`, with the signal problem from above\n\n"
                "`docker init`, which ships with Docker Desktop, writes a starter `Dockerfile`, `.dockerignore`, `compose.yaml` and `README.Docker.md` for a project. "
                "It has templates for Python, Go, Java, Node and more. It is a fine way to get a second opinion, but read every line before you keep it. Run it in an empty folder, because it overwrites files and you cannot get them back."
            ),
            "refs": ref("checks", "init"),
        },
    ],
    "analogy": (
        "Picture a layered cake, with the build cache as a fridge full of finished layers. "
        "Change only the decoration on top, and every lower layer comes out of the fridge ready. "
        "Change the sponge at the bottom, and every layer above it has to be baked again. "
        "A real baker could keep an upper layer after changing a lower one. Docker never does: everything after the first change gets rebuilt."
    ),
    "diagram": SVG,
    "diagram_caption": "Each instruction is a layer; after an edit to app.py, only the top layer is rebuilt.",
    "worked": {
        "title": "Package hello-devops and run it",
        "steps": [
            step("In your hello-devops folder, create the Dockerfile and .dockerignore from the Files section, then build. `--build-arg` fills the ARG, and the final dot is the build context. The first build is the slow one, because it downloads the base image and runs pip install.",
                 v1_step("d06", 0)),
            step("Run it like any other image: publish port 8000 and call two endpoints. The host field is the container's ID, because each container has its own hostname.",
                 join(C("run"), C("curl1"), C("curl2"))),
            step("Add a comment line to app.py and build again. The three steps above the code say CACHED, and only `COPY app.py` runs, so the whole build takes 0.3 seconds. (Output trimmed to the build steps.) Remove the comment afterwards.",
                 REBUILD),
            step("`docker history` lists the layers, newest first. The pip install layer holds the weight. CMD, EXPOSE, ENV and ARG only change settings, so they are 0B. Notice that the ARG value is visible here.",
                 C("hist")),
            step("Settings come from the environment, so the same image behaves differently without a rebuild. Start a second container with another greeting on another port.",
                 join(C("run2"), C("curl3"))),
            step("Check what the image will run and which variables the app sees. `-e GREETING=Hi` overrode nothing in the image; it added a value at run time. Then clean up with `docker rm -f hello hello2`.",
                 join(C("insp"), C("insp_env"))),
        ],
    },
    "code": [
        {
            "lang": "dockerfile",
            "title": "Dockerfile (Day 13 version: one stage; the lab keeps it as docker/Dockerfile.simple)",
            "src": "# Day 13 version: one stage, runs as root. Day 16 replaces it.\nFROM " + lab("docker/Dockerfile.simple").split("\nFROM ", 1)[1],
            "run": "docker build --build-arg APP_VERSION=1.0.0 -t hello-devops:1.0.0 . && docker run --rm -p 8000:8000 hello-devops:1.0.0",
        },
        {
            "lang": "text",
            "title": ".dockerignore",
            "src": lab(".dockerignore"),
            "run": "docker build --build-arg APP_VERSION=1.0.0 -t hello-devops:1.0.0 .",
        },
    ],
    "commands": [
        {"cmd": "docker build -t hello-devops:1.0.0 .", "what": "Build an image from the Dockerfile in this folder and tag it."},
        {"cmd": "docker build --build-arg APP_VERSION=1.0.0 -t hello-devops:1.0.0 .", "what": "Build and pass a value to an ARG in the Dockerfile."},
        {"cmd": "docker build -f Dockerfile.slow -t hello-devops:slow .", "what": "Build from a Dockerfile with a different file name."},
        {"cmd": "docker build --check .", "what": "Lint the Dockerfile and report problems without building."},
        {"cmd": "docker build --no-cache -t hello-devops:1.0.0 .", "what": "Build again from scratch, ignoring the cache."},
        {"cmd": "docker history hello-devops:1.0.0", "what": "Show an image's layers, their sizes and the instruction that made each one."},
        {"cmd": "docker image inspect --format '{{json .Config.Cmd}}' hello-devops:1.0.0", "what": "Show one setting of an image, here its default command."},
        {"cmd": "docker run --rm -p 8000:8000 -e GREETING=Hi hello-devops:1.0.0", "what": "Run the image with one setting overridden by an env var."},
        {"cmd": "docker run --rm hello-devops:1.0.0 ls -a", "what": "Run another command instead of CMD, here to list the /app folder."},
        {"cmd": "docker run --rm --entrypoint sh hello-devops:1.0.0 -c 'id'", "what": "Replace the image's entrypoint for one run."},
        {"cmd": "docker tag hello-devops:1.0.0 hello-devops:stable", "what": "Give an image a second name; nothing is copied."},
        {"cmd": "docker image prune", "what": "Delete dangling images (old builds with no tag) to free disk space."},
        {"cmd": "docker init", "what": "Generate a starter Dockerfile, .dockerignore and compose.yaml (Docker Desktop; run it in an empty folder)."},
    ],
    "mistake": (
        "The classic mistake is `COPY . .` before `RUN pip install`. "
        "Every code change, even a comment, then invalidates the cache and reinstalls every package, and any junk in the folder lands in the image. "
        "Copy only `requirements.txt` first, install, and copy the code last."
    ),
    "real_world": (
        "PayFlow keeps each service's Dockerfile in that service's repo, and changes to it go through code review. "
        "CI builds the image once per commit, and that same image moves from testing to production with only the environment variables changing. "
        "Reviewers watch Dockerfile order closely, because one misplaced COPY makes every build reinstall all dependencies."
    ),
    "task": {
        "title": "Break the cache, leak a file, then fix both",
        "steps": [
            "Create the Dockerfile and .dockerignore from Files in your hello-devops folder. Build `hello-devops:1.0.0`, run it, and curl `/metrics`.",
            "Copy the Dockerfile to `Dockerfile.slow`. In the copy, replace both COPY lines with one `COPY . .` placed before `RUN pip install`.",
            "Build the slow image with `-f Dockerfile.slow`, add a comment to app.py, and build it again. Note which steps rerun and how long it takes.",
            "Make the same kind of edit and rebuild with your real Dockerfile. Compare the two.",
            "Create a file `secret.txt` with some fake text. Rebuild the slow image and list its files with `docker run --rm`. Is the file there?",
            "Add `secret.txt` to .dockerignore, rebuild the slow image, and check again.",
            "Run `docker build --check .` on both Dockerfiles and fix anything it reports.",
            "Run your real image with different `GREETING` and `APP_VERSION` values and confirm the JSON changes without a rebuild.",
            "Delete `Dockerfile.slow`, `secret.txt`, its .dockerignore line and the slow image. Commit the Dockerfile and .dockerignore, and push.",
        ],
        "hints": [
            "`docker run --rm IMAGE ls -a` runs `ls -a` in the image's WORKDIR instead of the normal CMD.",
            "A step says CACHED only when its instruction, the files it copies, and every step above it are unchanged.",
            "If you add the same comment text you used before, the build may still say CACHED: the cache matches file contents, and that content was built before.",
        ],
        "done_when": "You are done when the slow Dockerfile reruns pip install after a comment change, your real one shows it as CACHED, and secret.txt is no longer in the slow image.",
    },
    "explain_back": {
        "prompt": "Explain in 3 to 4 sentences why the order of lines in a Dockerfile matters for build speed, and why CMD should use exec form. Mention layers, the cache and PID 1.",
        "answer": (
            "Each Dockerfile instruction creates a layer, and Docker caches each layer. "
            "When an instruction or the files it copies change, Docker rebuilds that layer and every layer after it. "
            "So I copy requirements.txt and run pip install before I copy the code. "
            "A code change then rebuilds only the last small layer. "
            "I write CMD as a JSON list so my app runs as PID 1 and gets the SIGTERM from docker stop. "
            "With shell form, a shell sits in between and the container is killed after 10 seconds."
        ),
    },
    "recap": [
        "A Dockerfile lists the steps that build an image; keep it in git next to the app.",
        "A change rebuilds that layer and every layer after it, so put slow, stable steps first.",
        "COPY checks file contents, not times; RUN only compares the command text.",
        "The build context is the folder you pass to docker build; .dockerignore keeps junk and secrets out.",
        "Use exec form for CMD and ENTRYPOINT, so the app is PID 1 and stops cleanly.",
        "ARG exists only at build time and shows in the history; ENV reaches the running container.",
    ],
    "check": [
        {
            "q": "A Kotlin service's Dockerfile copies `build.gradle.kts`, downloads dependencies, then copies `src/` and compiles. Which change makes the next build slowest?",
            "options": [
                "Editing one class in src/",
                "Running the same build twice in a row",
                "Changing a file listed in .dockerignore",
                "Adding a dependency to build.gradle.kts",
            ],
            "answer": 3,
            "why": "The dependency file is copied early, so changing it invalidates the download layer and everything after it.",
        },
        {
            "q": "An image has `ENTRYPOINT [\"curl\"]` and `CMD [\"--help\"]`. What runs for `docker run img -s https://example.com`?",
            "options": [
                "`curl -s https://example.com`",
                "`curl --help -s https://example.com`",
                "`-s https://example.com` on its own",
                "`curl --help` only",
            ],
            "answer": 0,
            "why": "Arguments after the image name replace CMD and are added to the fixed ENTRYPOINT.",
        },
        {
            "q": "A teammate's container takes exactly 10 seconds to stop every time and exits with 137. Its Dockerfile ends with `CMD python server.py`. What is the most likely fix?",
            "options": [
                "Add EXPOSE for the server's port",
                "Run the container with more memory",
                "Write CMD as [\"python\", \"server.py\"]",
                "Move the CMD line to the top of the file",
            ],
            "answer": 2,
            "why": "In shell form a shell is PID 1 and does not forward SIGTERM, so Docker waits 10 seconds and sends SIGKILL; exec form makes Python PID 1.",
        },
    ],
    "interview": [
        {
            "q": "What is the difference between CMD and ENTRYPOINT?",
            "a": (
                "Both define what runs when a container starts. ENTRYPOINT sets the program, and arguments given to `docker run` are added after it. "
                "CMD sets the default command or default arguments, and anything you type after the image name replaces it. "
                "A common pattern is ENTRYPOINT for the binary and CMD for its default flags. "
                "Either way, use the exec form, a JSON list, so the app runs as PID 1 and receives signals like SIGTERM."
            ),
        },
        {
            "q": "How do you make Docker builds fast?",
            "a": (
                "Order instructions from least to most often changed, so the cache gets reused: base image, dependency files, install, then source code. "
                "Copy only the files you need and keep a .dockerignore, so unrelated changes stop breaking the cache and the context stays small. "
                "A small base image means less to download and push. "
                "In CI, share the build cache between runs, because every fresh runner starts with an empty one."
            ),
        },
        {
            "q": "What is the difference between ARG and ENV?",
            "a": (
                "ARG is a build-time variable that you set with `--build-arg`; it is gone when the container runs. "
                "ENV is stored in the image and is present in every container, where `docker run -e` can override it. "
                "To keep a build value at run time, copy it from ARG into ENV. "
                "Neither is safe for secrets, because both show up in the image history or config; build secrets go through secret mounts instead."
            ),
        },
    ],
    "deeper": {
        "minutes": 12,
        "body": (
            "Run the PID 1 experiment yourself. Make a folder with a two-line Dockerfile: `FROM hello-devops:1.0.0` and then `CMD gunicorn --bind 0.0.0.0:8000 --workers 2 app:app`, in shell form. "
            "Build it as `shell:1.0` and start one container from it and one from your real image. "
            "Then look at PID 1 in each with `docker exec <name> cat /proc/1/cmdline | tr '\\0' ' '`:\n\n"
            "- In the shell-form container, PID 1 was `/bin/sh -c gunicorn --bind 0.0.0.0:8000 --workers 2 app:app`.\n"
            "- In the real image, PID 1 was `/usr/local/bin/python3.14 /usr/local/bin/gunicorn --bind 0.0.0.0:8000 --workers 2 app:app`.\n\n"
            "Now time `docker stop` on each with `time docker stop <name>`. When we tried it, the shell-form container took 10.2 seconds and ended as `Exited (137)`. "
            "The exec-form container stopped in 0.6 seconds and ended as `Exited (0)`. "
            "The shell got the SIGTERM and did nothing with it, so after 10 seconds Docker sent SIGKILL. "
            "In production, every deploy then waits 10 extra seconds per container, and requests in flight are cut off.\n\n"
            "Sometimes you need a shell script as the entry point, for example to wait for a database or to build a config file first. "
            "End such a script with `exec \"$@\"` or `exec gunicorn ...`. The `exec` replaces the shell with your app, so the app becomes PID 1. "
            "Another option is `docker run --init`, which adds a tiny init program as PID 1 that forwards signals.\n\n"
            "One more cache detail surprised us while testing. We added a comment to app.py, rebuilt, removed it, and later added the very same comment again. "
            "The second time, the `COPY app.py` step said CACHED. The cache is keyed by file contents, so a version of the file that was built before matches its old layer, even after other builds in between. "
            "That is also why `touch` alone never triggers a rebuild.\n\n"
            "The [Dockerfile reference](https://docs.docker.com/reference/dockerfile/) has a table that shows every combination of CMD and ENTRYPOINT in exec and shell form."
        ),
    },
    "sources": src("dockerfile", "cache_opt", "context", "twelve"),
}
