"""Fifth pass (book voice) for d19."""
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from common import load, apply, save

path, P, L, OL = load(5, "d19")
new = {}

new["goal"] = r"""By the end you can write a Dockerfile for hello-devops, explain every instruction in it, order the steps so rebuilds are fast, and choose between CMD and ENTRYPOINT."""

new["opening"] = r"""Picture packing your lunch every morning from a written list. Cook the rice, which takes forty minutes. Add the curry. Pack a napkin. One morning you want a blue napkin instead of a white one, and your list has a strange rule: change any step, and you must redo every step after it. If the napkin line came first, you would cook the rice again just to swap a napkin.

Docker's recipe for an image has exactly that rule, and the trap is easy to walk into, because the slow way and the fast way contain the same lines. Only the order differs. Last time, you opened other people's images and saw their layers. In this lesson, we'll write our own recipe, a Dockerfile, for hello-devops. That is the course's tiny web app, which answers every visit with a greeting and a count of visits so far. We'll order it so a code change rebuilds in under a second, and make sure the app stops politely when asked.

Before we start, make a guess, and keep it in mind."""

new["guess_q"] = r"""A Dockerfile does `COPY . .` (copy every file in the folder) and then `RUN pip install -r requirements.txt` (install the app's packages, the slow step). You change one comment in app.py and rebuild. What happens?"""
new["guess_why"] = r"""A changed layer invalidates every layer after it, and `COPY . .` changes whenever any file changes. Copy requirements.txt and install first, then copy the code, so code edits skip the slow install: the napkin goes at the end of the list."""

new["terms"] = {
    "Dockerfile": "A text file of instructions that tells Docker how to build an image, read from top to bottom.",
    "Base image": "The image a Dockerfile starts from with FROM, such as python:3.14-slim.",
    "Build context": "The folder you pass to docker build; COPY can only take files from inside it.",
    "Build cache": "Layers saved from earlier builds, reused when an instruction and everything before it are unchanged.",
    "Exec form": "Writing CMD or ENTRYPOINT as a list in square brackets, so the program runs directly as PID 1 with no shell in between.",
    "ENTRYPOINT": "The fixed program a container runs; words typed after the image name in docker run are added after it.",
    "Build argument": "A variable declared with ARG and set with --build-arg; it exists only while the image builds.",
}

S = []
S.append(("A packing list Docker follows from the top", r"""Docker builds an image by following a plain text file named `Dockerfile`. It runs the instructions in order, and each one starts from the result of the one before. Each instruction that changes files adds a layer, the same kind of read-only layer you inspected on Day 18.

Each `RUN` step runs in a container of its own. The builder starts a temporary container from the layers built so far, runs the command in it, and saves the files that changed as the next layer. So `RUN pip install -r requirements.txt` sees only what earlier steps put in the image. pip is Python's package installer, and `requirements.txt` is the app's list of packages. If no `COPY` brought `requirements.txt` in first, pip cannot find it.

You build with `docker build -t hello-devops:1.0.0 .`. The `-t` flag names and tags the result, and the final dot is the build context, which has its own section below. The builder behind `docker build` is called BuildKit. It is the default in Docker Desktop and Docker Engine, and it prints the `[+] Building` progress you will see in the worked example.

Today you write a Dockerfile with one stage that runs as root, the all-powerful user. It is the right first step, because every line is easy to see. Day 22 turns it into the multi-stage, non-root version that the lab ships.

First, the words you can write on the list."""))

S.append(("The handful of instructions you'll use", r"""Most Dockerfiles use a handful of instructions. Keep this list next to the Day 19 Dockerfile in the Files section, because you will come back to it:

- `FROM` picks the base image to start from, such as `python:3.14-slim`.
- `WORKDIR` sets and creates the folder later steps work in, so `COPY app.py .` lands in `/app`, not `/`.
- `COPY` copies files from the build context into the image. `ADD` can also fetch URLs and unpack archives; prefer `COPY` unless you need that.
- `RUN` runs a command at build time, such as `pip install`, and saves the result as a layer.
- `ENV` sets an environment variable (a named setting) for later steps and for the running container.
- `ARG` declares a variable that exists only during the build.
- `EXPOSE` documents the port the app listens on. It publishes nothing; `-p` does that.
- `CMD` and `ENTRYPOINT` set what the container runs when it starts.

Day 22 adds `USER`, which picks the user the app runs as, and `HEALTHCHECK`, which tells Docker how to test the app. You will also see `LABEL`, which adds key and value notes to the image, such as a link to its source repo.

Every line of the Day 19 Dockerfile is one of these instructions, with a comment that says why it is there. The first one to look at closely is `COPY`, because it can only reach so far."""))

S.append(("What the builder can see: the build context and .dockerignore", r"""The dot in `docker build -t hello-devops:1.0.0 .` is the build context: the folder whose files the build may use. The builder runs inside Docker's Linux VM, not on your Mac. The `docker` command gives it this one folder, and the builder loads files from it as it needs them. Nothing outside it exists for the build, so `COPY ../secrets.txt .` fails. Docker also looks for the file named `Dockerfile` in that folder, unless you name another one with `-f`.

A `.dockerignore` file in that folder lists files the build must never see, with patterns like `.gitignore` (Day 8). The lab's file keeps out:

- `.git` and `.github`, the repo's history and workflows
- `.venv` and Python caches, which belong to your Mac only
- folders for later days, such as `infra`, `k8s` and `chart`
- Markdown files, which the app does not need

Our Dockerfile copies two files by name, so for now the ignore file is a safety net. It starts to matter the day someone writes `COPY . .`. In a test, a folder with a 10 MB `.venv` sent `10.00MB` of context to the builder on every build. After adding `.venv` to `.dockerignore`, the same build sent 100 bytes. Without the ignore file, `COPY . .` would also bake your `.git` folder and any local secret files into the image.

The context decides what the builder sees. The cache decides what it has to redo."""))

S.append(("The build cache, and why order matters", r"""Docker keeps every layer it builds in its build cache. On the next build it checks each instruction in order. If the instruction and everything before it are unchanged, Docker reuses the saved layer and prints `CACHED`. If something changed, Docker rebuilds that layer and every layer after it, even ones whose instructions did not change. That is the packing list's strange rule from the opening, and it has a reason. Each layer holds the changes one step made on top of the exact layers below it. If a lower layer changes, Docker cannot know whether a later `RUN pip install` would give the same result without running it again.

What counts as changed depends on the instruction:

- For `COPY` and `ADD`, Docker checks the contents of the files. Their modification time is ignored, so `touch app.py` changes nothing.
- For `RUN`, Docker only compares the command text. `RUN apt-get update` stays cached for months, even if new packages exist.

The naive order is `COPY . .` and then `RUN pip install`. Every code edit, even a comment, changes the copied files, so pip reinstalls every package. The hands-on task makes you watch it happen. Order the steps from rarely changed to often changed instead:

1. `FROM` the base image.
2. `COPY requirements.txt` on its own.
3. `RUN pip install`, the slow step.
4. `COPY app.py`, which changes all the time.

With this order, a code edit rebuilds only the last small layer. In the worked example that rebuild takes 0.3 seconds, against about 10 seconds for a fresh pip install, roughly thirty times faster.

**Put what changes least at the top. Copy the code last.**

The image now builds fast. The next question is what it does when it starts, and when it is asked to stop."""))

S.append(("CMD, ENTRYPOINT and who is PID 1", r"""`CMD` and `ENTRYPOINT` both say what runs when a container starts. They differ in how the words you type after the image name in `docker run` treat them:

- `CMD` is a default. Anything you type after the image name replaces it.
- `ENTRYPOINT` is fixed. Anything you type after the image name is added to it as arguments.
- With both, `ENTRYPOINT` is the program and `CMD` gives its default arguments.

A tiny image with `ENTRYPOINT ["echo", "Hello,"]` and `CMD ["world"]` shows it. `docker run greeter` printed `Hello, world`, and `docker run greeter Ana` printed `Hello, Ana`. `--entrypoint` swaps the program itself. For a web app, `CMD` alone is the simple choice.

Write both in exec form, a JSON list such as `["gunicorn", "app:app"]`. Then your app runs directly as PID 1 (the container's first process) and receives the SIGTERM from `docker stop`. In shell form, `CMD gunicorn app:app`, Docker runs `/bin/sh -c "gunicorn app:app"`. The shell becomes PID 1 and does not pass SIGTERM on. We measured both. The shell-form container needed 10.2 seconds to stop and ended with code 137. The exec-form one stopped in 0.6 seconds with code 0.

PID 1 is also special in Linux. A handler is code that reacts to a signal. The kernel drops any signal that PID 1 has no handler for, SIGKILL aside. `sleep` sets up no handler, which is why it ignored SIGTERM on Day 17. So exec form is only half the fix, and the app must also handle SIGTERM itself. Gunicorn, the web server that runs hello-devops, does. A bare Python script does not: as PID 1 it waited out the full 10 seconds in our test, just like `sleep`.

The app starts and stops cleanly. What it says when it starts comes from its settings."""))

S.append(("ARG, ENV and settings from the environment", r"""`ARG` and `ENV` both set variables, at different times:

- `ARG` exists only while the image builds. You set it with `--build-arg NAME=value`.
- `ENV` is stored in the image and is present when the container runs. `docker run -e NAME=value` overrides it.

A test image showed the difference. With `--build-arg BUILD_NOTE=hello`, a `RUN` step printed `at build time: hello`, and the running container printed `at run time: not set`. To keep a build value, copy it: `ARG APP_VERSION` followed by `ENV APP_VERSION=$APP_VERSION`, as our Dockerfile does.

One warning before you reach for either one: `docker history` shows ARG values in plain text, so never pass passwords or tokens this way. Day 22 shows the safe way.

Why put settings in the environment at all? [The Twelve-Factor App](https://12factor.net/config) is a well-known set of rules for web apps. Its config rule says to keep settings that change between deploys out of the code, in environment variables. Then one image runs in every environment, and only the variables differ. It is one lunchbox recipe with a note on top that says "extra spicy". hello-devops reads four of them:

- `APP_VERSION`, the version it reports
- `GREETING`, the message it returns
- `REDIS_HOST`, where Redis runs (empty means count in memory)
- `PORT`, used only when you run `python app.py`

`PYTHONUNBUFFERED=1` is not one of the app's settings. It makes Python print log lines at once, so `docker logs` shows them as they happen.

One last group of habits keeps the finished image easy to find and the recipe easy to trust."""))

S.append(("Tags, build checks and docker init", r"""Tag your own images with real versions, such as `1.0.0`; Day 23 explains version numbers. Leave the tag out and Docker uses `latest`, which only means whatever was built last. In `FROM`, name a specific base such as `python:3.14-slim`, never bare `python`, or your build gets whatever `latest` points to on the day you build. One image can carry several tags: `docker tag hello-devops:1.0.0 hello-devops:stable` adds a second name and copies nothing.

`docker build --check .` lints a Dockerfile, which means it reads it for likely mistakes without building it. We ran it on a file with three common slips, and it named each with a line number:

- `FromAsCasing`: `FROM ... as base` mixes upper and lower case
- `LegacyKeyValueFormat`: `ENV GREETING Hello` should be `ENV GREETING=Hello`
- `JSONArgsRecommended`: a shell-form `CMD`, with the signal problem from above

`docker init`, which ships with Docker Desktop, writes a starter `Dockerfile`, `.dockerignore`, `compose.yaml` and `README.Docker.md` for a project. It has templates for Python, Go, Java, Node and more. It is a fine way to get a second opinion, but read every line before you keep it. Run it in an empty folder, because it overwrites files and you cannot get them back.

This Dockerfile has limits we'll fix later: it runs as root, and the app still runs alone, keeping its visit count in memory. Stop the container and the count is gone. Next, we give containers a place to keep data and a way to find each other."""))
new["sections"] = S

new["drop"] = ["analogy", "mistake"]
new["real_world"] = r"""One misplaced COPY makes every build reinstall all dependencies, so reviewers check the order of Dockerfile lines closely. Each service keeps its Dockerfile in its own repo, next to the code, and changes to it go through code review. CI builds the image once per commit, and that same image moves from testing to production with only the environment variables changing."""

new["diagram_caption"] = "Each instruction is a layer; after an edit to app.py, only the top layer is rebuilt."

new["worked"] = [
    r"""In your hello-devops folder, create the Dockerfile and .dockerignore from the Files section, then build. `--build-arg` fills the ARG, and the final dot is the build context. The first build is the slow one, because it downloads the base image and runs pip install.""",
    r"""Run it like any other image: publish port 8000 and call two endpoints (addresses the app answers). The host field is the container's ID, because each container has its own hostname.""",
    r"""Add a comment line to app.py and build again. The three steps above the code say CACHED, and only `COPY app.py` runs, so the whole build takes 0.3 seconds. (Output trimmed to the build steps.) Remove the comment afterwards.""",
    r"""`docker history` lists the layers, newest first. The pip install layer holds the weight. CMD, EXPOSE, ENV and ARG only change settings, so they are 0B. Notice that the ARG value is visible here.""",
    r"""Settings come from the environment, so the same image behaves differently without a rebuild. Start a second container with another greeting on another port.""",
    r"""Check what the image will run and which variables the app sees. `-e GREETING=Hi` overrode nothing in the image; it added a value at run time. Then clean up with `docker rm -f hello hello2`.""",
]

new["task"] = {
    "steps": [
        r"""Create the Dockerfile and .dockerignore from Files in your hello-devops folder. Build `hello-devops:1.0.0`, run it, and curl `/metrics`.""",
        r"""Copy the Dockerfile to `Dockerfile.slow`. In the copy, replace both COPY lines with one `COPY . .` placed before `RUN pip install`.""",
        r"""Build the slow image with `-f Dockerfile.slow`, add a comment to app.py, and build it again. Note which steps rerun and how long it takes.""",
        r"""Make the same kind of edit and rebuild with your real Dockerfile. Compare the two.""",
        r"""Create a file `secret.txt` with some fake text. Rebuild the slow image and list its files with `docker run --rm`. Is the file there?""",
        r"""Add `secret.txt` to .dockerignore, rebuild the slow image, and check again.""",
        r"""Run `docker build --check .` on both Dockerfiles and fix anything it reports.""",
        r"""Run your real image with different `GREETING` and `APP_VERSION` values and confirm the JSON changes without a rebuild.""",
        r"""Delete `Dockerfile.slow`, `secret.txt`, its .dockerignore line and the slow image. Commit the Dockerfile and .dockerignore, and push.""",
    ],
    "hints": [
        r"""`docker run --rm IMAGE ls -a` runs `ls -a` in the image's WORKDIR instead of the normal CMD.""",
        r"""A step says CACHED only when its instruction, the files it copies, and every step above it are unchanged.""",
        r"""If you add the same comment text you used before, the build may still say CACHED: the cache matches file contents, and that content was built before.""",
    ],
    "done_when": r"""You are done when the slow Dockerfile reruns pip install after a comment change, your real one shows it as CACHED, and secret.txt is no longer in the slow image.""",
}

new["explain_back"] = {
    "prompt": r"""Explain in 3 to 4 sentences why the order of lines in a Dockerfile matters for build speed, and why CMD should use exec form. Mention layers, the cache and PID 1.""",
    "answer": r"""Each Dockerfile instruction creates a layer, and Docker caches each layer. When an instruction or the files it copies change, Docker rebuilds that layer and every layer after it. So I copy requirements.txt and run pip install before I copy the code, and a code change then rebuilds only the last small layer. I write CMD as a JSON list so my app runs as PID 1 and gets the SIGTERM from docker stop. With shell form, a shell sits in between and the container is killed after 10 seconds.""",
}

new["recap"] = [
    "A Dockerfile lists the steps that build an image; keep it in git next to the app.",
    "A change rebuilds that layer and every layer after it, so put slow, stable steps first.",
    "COPY checks file contents, not times; RUN only compares the command text.",
    "The build context is the folder you pass to docker build; .dockerignore keeps junk and secrets out.",
    "Use exec form for CMD and ENTRYPOINT, so the app is PID 1 and stops cleanly.",
    "ARG exists only at build time and shows in the history; ENV reaches the running container. Today's image still runs as root and keeps no data.",
]

new["check"] = [
    (r"""A service written in Kotlin builds with Gradle, which lists its dependencies in `build.gradle.kts`. Its Dockerfile copies that file, downloads the dependencies, then copies the code folder `src/` and compiles. Which change makes the next build slowest?""",
     r"""The dependency file is copied early, so changing it invalidates the download layer and everything after it."""),
    (r"""An image has `ENTRYPOINT ["curl"]` and `CMD ["--help"]`. What runs for `docker run img -s https://example.com`?""",
     r"""Words after the image name replace CMD and are added to the fixed ENTRYPOINT."""),
    (r"""A teammate's container takes exactly 10 seconds to stop every time and exits with 137. Its Dockerfile ends with `CMD python server.py`. What is the most likely fix?""",
     r"""A shell as PID 1 drops SIGTERM, so Docker sends SIGKILL after 10 seconds. Exec form makes Python PID 1, so a server that handles SIGTERM stops cleanly."""),
]

new["interview"] = [
    (r"""What is the difference between CMD and ENTRYPOINT?""",
     r"""Both define what runs when a container starts. ENTRYPOINT sets the program, and arguments given to `docker run` are added after it. CMD sets the default command or default arguments, and anything you type after the image name replaces it. A common pattern is ENTRYPOINT for the program and CMD for its default flags. Either way, use the exec form, a JSON list, so the app runs as PID 1 and receives signals like SIGTERM."""),
    (r"""How do you make Docker builds fast?""",
     r"""Order instructions from least to most often changed, so the cache gets reused: base image, dependency files, install, then source code. Copy only the files you need and keep a .dockerignore, so unrelated changes stop breaking the cache and the context stays small. A small base image means less to download and push. In CI, share the build cache between runs, because every fresh runner starts with an empty one."""),
    (r"""What is the difference between ARG and ENV?""",
     r"""ARG is a build-time variable that you set with `--build-arg`; it is gone when the container runs. ENV is stored in the image and is present in every container, where `docker run -e` can override it. To keep a build value at run time, copy it from ARG into ENV. Neither is safe for secrets, because both show up in the image history or config; build secrets go through secret mounts instead."""),
]

new["deeper"] = r"""Run the PID 1 experiment yourself. Make a folder with a two-line Dockerfile: `FROM hello-devops:1.0.0` and then `CMD gunicorn --bind 0.0.0.0:8000 --workers 2 app:app`, in shell form. Build it as `shell:1.0` and start one container from it and one from your real image. Then look at PID 1 in each with `docker exec <name> cat /proc/1/cmdline | tr '\0' ' '`:

- In the shell-form container, PID 1 was `/bin/sh -c gunicorn --bind 0.0.0.0:8000 --workers 2 app:app`.
- In the real image, PID 1 was `/usr/local/bin/python3.14 /usr/local/bin/gunicorn --bind 0.0.0.0:8000 --workers 2 app:app`.

Now time `docker stop` on each with `time docker stop <name>`. When we tried it, the shell-form container took 10.2 seconds and ended as `Exited (137)`. The exec-form container stopped in 0.6 seconds and ended as `Exited (0)`. The shell got the SIGTERM and did nothing with it, so after 10 seconds Docker sent SIGKILL. In production, every deploy then waits 10 extra seconds per container, and requests in flight are cut off.

Sometimes you need a shell script as the entry point, for example to wait for a database or to build a config file first. End such a script with `exec "$@"` or `exec gunicorn ...`. The `exec` replaces the shell with your app, so the app becomes PID 1. Another option is `docker run --init`, which adds a tiny init program as PID 1 that forwards signals.

One more cache detail surprised us while testing. We added a comment to app.py, rebuilt, removed it, and later added the very same comment again. The second time, the `COPY app.py` step said CACHED. The cache is keyed by file contents, so a version of the file that was built before matches its old layer, even after other builds in between. For the same reason, `touch` alone never triggers a rebuild.

The [Dockerfile reference](https://docs.docker.com/reference/dockerfile/) has a table that shows every combination of CMD and ENTRYPOINT in exec and shell form."""

new["closing"] = r"""We started with a packing list that made you cook the rice again to change a napkin. Our Dockerfile puts the napkin last. A code edit rebuilds in 0.3 seconds instead of reinstalling every package, and the app stops in 0.6 seconds instead of being killed after 10. Open any Dockerfile you can find, in the lab or elsewhere, and check two things. Does `COPY . .` come before the install? Is `CMD` written as a list?

Next, we'll give containers somewhere to keep data and a way to talk to each other. Why does the visit counter reset every time the container is replaced?"""

apply(L, new)
save(path, P, L, OL)
