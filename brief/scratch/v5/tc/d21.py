"""Fifth pass (book voice) for d21."""
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from common import load, apply, save

path, P, L, OL = load(5, "d21")
new = {}

new["goal"] = r"""By the end you can describe hello-devops and Redis in one compose.yaml, run and inspect the stack with docker compose, and use .env, profiles, override files and watch for local development."""

new["opening"] = r"""Picture opening a small restaurant kitchen every morning by phoning each cook with step-by-step orders. Light the oven. Now start the sauce. Now open the pantry. It works, until the day you are ill and nobody else knows the order. Or the cook starts the sauce before the oven is hot, because "lit" is not the same as "ready".

The fix is a plan pinned to the kitchen wall: who works which station, and what must be ready before whom. It also says what gets cleared at night (the counters) and what stays (the pantry). Last time, you set up hello-devops and Redis with a network, a volume and two long commands, typed in the right order. In this lesson, we'll write that plan down as one file and start the whole app with one command. Then we'll make the daily loop fast: a saved code change shows up in the running app without typing anything.

Before we start, make a guess, and keep it in mind."""

new["guess_q"] = r"""You run `docker compose down` (the "close the kitchen" command) on hello-devops, which keeps Redis data in a named volume. What happens to the visit count?"""
new["guess_why"] = r"""`docker compose down` removes the containers and the network but keeps named volumes: it clears the counters and leaves the pantry. Only `docker compose down -v` deletes them, and the data with them."""

new["terms"] = {
    "Docker Compose": "A tool that runs an app made of several containers from one YAML file with one command.",
    "Service": "One entry in a Compose file that describes a container to run, such as web or redis.",
    "Project": "Everything Compose creates for one app; named after the folder unless you set a name.",
    "Healthcheck": "A command Docker runs again and again to test whether a container is working.",
    "Restart policy": "A rule that tells Docker whether to start a container again after its process stops.",
    "Override file": "A second Compose file, such as compose.override.yaml, whose settings Compose merges on top of the first.",
    "Profile": "A label on a service that keeps it switched off until you ask for that profile.",
    "Compose Watch": "A Compose mode that copies your code changes into running containers or rebuilds them.",
}

S = []
S.append(("Writing the plan down: Compose describes the app you want", r"""On Day 20 you wired up hello-devops and Redis by hand: a network, a volume and two long `docker run` commands, typed in the right order. That is imperative: you tell Docker each step, like phoning each cook. It works, and nobody wants to do it twice.

Docker Compose is declarative. You describe the finished app in one file, `compose.yaml`, and `docker compose up` works out the steps. The file is YAML, a plain text format of indented `key: value` lines. Teammates get the same setup by cloning the repo.

Compose is only a client. It turns the file into the same requests to Docker Engine that your `docker run` commands made. It also labels every container with its project, its service and a hash (a fingerprint) of that service's settings. Run `up` again and Compose compares those labels with the file. A service that matches keeps running, and one whose settings changed is recreated.

The file format is the Compose Specification. You will see `version: "3.8"` at the top of old files. Compose ignores that line, so leave it out.

Compose groups everything it creates into a project, named after the folder. In your `hello-devops` folder that gives a network called `hello-devops_default`, a volume called `hello-devops_redis-data` and containers called `hello-devops-web-1` and `hello-devops-redis-1`. The `-1` is a counter, because Compose can run several copies of one service.

So what does the plan on the wall actually say? The lab's file shows it."""))

S.append(("Reading the lab's compose.yaml", r"""The lab's file, in the Files section, has two top-level keys. `services` holds one entry per container, one station in the kitchen. `volumes` declares the named volume, the pantry. You do not declare a network. Compose creates one per project and puts every service on it, so service names work as DNS names (names that turn into addresses), just like on Day 20.

Inside a service you will meet these keys:

- `build: .` builds the image from the Dockerfile in this folder. `image:` uses a ready-made image instead, such as `redis:8-alpine`.
- `ports:` publishes ports, written `"HOST:CONTAINER"` in quotes so YAML does not misread them.
- `environment:` sets environment variables. `env_file:` reads them from a file instead.
- `volumes:` mounts named volumes or folders, as `redis-data:/data`.
- `depends_on:` controls start order, with an optional health condition.
- `healthcheck:` tells Docker how to test the container.
- `restart:` says what to do when the process stops.

The web service sets `REDIS_HOST: redis`. Redis has no `ports:` entry, because only web talks to it, over the project network. Only port 8000 is open to your Mac.

One key in that list hides the trap from the opening: `depends_on`."""))

S.append(("Running is not ready: depends_on and healthchecks", r"""`depends_on` makes Compose start Redis before web. In its short form, `depends_on: [redis]`, it only waits until the Redis container is running. A database can need several more seconds before it accepts connections, so web may start and find nobody answering. That is the oven that was lit but not hot.

A healthcheck closes that gap. It is a command Docker runs inside the container on a schedule, and exit code 0 means healthy (the exit codes from Day 6). The lab runs `redis-cli ping` every 5 seconds, with a 3-second timeout and 5 retries. The long form of `depends_on` then waits for it:

- `condition: service_healthy` waits until the healthcheck passes.
- `condition: service_completed_successfully` waits until a one-off job, such as a database migration (a script that updates the database's layout), exits with 0.
- `condition: service_started` is the short form's behaviour.

In the worked example, `docker compose up -d` showed Redis as `Healthy` after 5.8 seconds and started web only then. `docker compose ps` shows `(health: starting)`, then `(healthy)`, or `(unhealthy)` if the check keeps failing.

**Running is not ready. Make the app wait for healthy.**

This only covers startup. When Redis dies later, hello-devops answers `/readyz` with a 503, and `/` returns a 500 error until Redis is back. Your app must still cope when a dependency fails, and Kubernetes uses that readiness answer on Day 43.

With the stack starting in the right order, here are the commands you'll type every day."""))

S.append(("The everyday commands, and restart policies", r"""These commands cover most days, run in the folder with `compose.yaml`:

- `docker compose up -d` creates and starts everything in the background; add `--build` to rebuild images first.
- `docker compose ps` shows each container, its health and its ports.
- `docker compose logs -f web` follows one service's output.
- `docker compose exec redis redis-cli GET visits` runs a command in a running service.
- `docker compose run --rm redis redis-cli -h redis ping` starts a new one-off container for a command, then removes it.
- `docker compose down` removes the containers and the network, and keeps named volumes.
- `docker compose down -v` also deletes the named volumes, and with them your data.
- `docker compose config` prints the final file after merging and filling in variables.

Two of those lines look almost the same and do very different things. Type `down -v` when you meant `down`, and your Redis data, or a whole development database, is gone for good.

**Plain down clears the counters. Down -v empties the pantry too.**

A restart policy says what Docker does when a container's process stops:

- `no`, the default: leave it stopped.
- `on-failure`: start it again only if it exited with a non-zero code.
- `always`: always start it again.
- `unless-stopped`: like always, except after you stopped it yourself.

Docker Engine applies the policy, not Compose. It notices when the main process ends and starts it again, with no compose command running. `docker run --restart unless-stopped` sets the same policy without Compose.

The override file in this lesson sets `unless-stopped`. We shut Redis down from inside with `redis-cli shutdown`. Docker started it again within seconds, its restart count went to 1, and the visit count carried on.

The plan works. Next, a way to change its details without editing it."""))

S.append(("Variables: .env, environment and env_file", r"""Compose can fill in placeholders in the file itself. Take `GREETING: "${GREETING:-Hello from Compose}"`. Compose looks for `GREETING` in your shell, then in a file named `.env` next to `compose.yaml`, and uses the default after `:-` if neither has it. We checked all three with `docker compose config | grep GREETING`:

1. With nothing set, it printed `GREETING: Hello from Compose`.
2. With `GREETING=Hi from .env` in `.env`, it printed `Hi from .env`.
3. With `GREETING='Hi from my shell'` before the command, the shell won.

Two files with similar names do different jobs, and they are easy to mix up:

- `.env` fills in `${...}` placeholders in the Compose file. Its values do not reach containers unless the file passes them on.
- `env_file: web.env` under a service sends every line of that file into the container as environment variables.

If `.env` ever holds secrets, keep it out of git; the lab's `.gitignore` already lists it. When something looks wrong, run `docker compose config` first. It shows the file exactly as Compose will use it.

Variables change values. Sometimes you want to change whole pieces of the plan, for your laptop only."""))

S.append(("Override files and profiles: extras for your laptop", r"""Compose reads `compose.yaml` and then, if it exists, `compose.override.yaml` from the same folder, and merges the two. That lets the base file stay simple and shared, while the override adds things only your laptop needs, like a sticky note on the kitchen plan. The merge follows a few rules:

- A single value, such as `image` or `command`, is replaced by the override.
- Maps (groups of named values), such as `environment`, are merged key by key.
- Some lists, such as `ports`, are joined, so an override cannot remove a published port.
- Paths are relative to the first file, the base one.

`-f` picks files by hand. `docker compose -f compose.yaml up -d` uses only the base file, which is what CI should run. `-f compose.yaml -f compose.ci.yaml` stacks another file on top.

A profile keeps a service switched off until you ask for it. The lab's override adds nginx in front of web, the reverse proxy (a server that passes requests on to another) you built on Day 11, with `profiles: ["proxy"]`. Plain `docker compose up -d` ignores it; `docker compose --profile proxy up -d` starts it too. Use profiles for extras such as a proxy, a database admin tool or a load generator.

One surprise from our testing: plain `docker compose down` left the proxy running, and Compose reported that the network was still in use. Stop profiled services with the same `--profile` flag you started them with.

The last piece makes the edit, run, look cycle fast."""))

S.append(("Compose Watch for a fast inner loop", r"""The inner loop is the cycle you repeat all day: edit, run, look. With plain Compose, every code change means `docker compose up -d --build`. Compose Watch shortens that. You list paths under `develop.watch` in the Compose file, run `docker compose watch`, and Compose reacts to every save:

- `sync` copies the changed files into the running container. Good for apps that reload code by themselves.
- `sync+restart` copies the files, then restarts the container. Good for gunicorn without reload.
- `rebuild` builds a new image and replaces the container. Use it for `requirements.txt`, because new packages need a new image.

The lab's override uses `sync+restart` for `app.py` and `rebuild` for `requirements.txt`. We changed the reply of `/healthz` while watch ran. It printed `Syncing service "web" after 1 changes were detected`, restarted web, and the next curl showed the new reply. The copied file arrived owned by the container's user, so it works with the non-root image from Day 22 too.

Why not a bind mount of the whole folder? It works, but on a Mac every file read crosses into the VM, and a bind mount also hides what the image had at that path. Watch copies only what changed and keeps the image's files. Keep bind mounts for files you want both sides to edit.

Compose has a clear limit: it runs everything on one machine, and it does only what the file says. If that machine dies, so does the app; Kubernetes handles many machines in Part 10. Our image has limits too. It still runs as root and carries more than it needs. Next, we make it ready for production."""))
new["sections"] = S

new["drop"] = ["analogy", "mistake"]
new["real_world"] = r"""A new engineer should be able to clone a service repo and start it, with its Postgres and Redis, in one command. A compose.yaml in every repo makes that work. A compose.override.yaml adds watch and debug tools on laptops, while CI runs `docker compose -f compose.yaml up -d --wait` to get real dependencies for integration tests. Production looks different: the same images run on Kubernetes (Day 38), and the databases are managed services."""

new["diagram_caption"] = "Compose merges the base file and the override into one project: services on one network, plus a named volume."

new["worked"] = [
    r"""In your hello-devops folder, with the lab's `compose.yaml` and the override from Files, start everything. Compose creates the volume and network, waits until Redis is healthy, and only then starts web.""",
    r"""Check the containers and call the app. The greeting comes from the override file, and the count rises by one each time, because both gunicorn workers share one Redis.""",
    r"""Read web's logs, look inside Redis, and run a one-off container. The `run --rm` command starts a fresh redis container just for `ping`. It talks to the service named redis over the network, then removes itself.""",
    r"""Shut Redis down from inside. The restart policy `unless-stopped` brings it back, and the count carries on, because Redis saved its data to the volume on the way down.""",
    r"""Take the stack down. The containers and network go, the volume stays. After `docker compose up -d` the count continues at 5.""",
    r"""Start the proxy profile. nginx answers on port 8080 and passes requests to web by its service name; the `Server` header shows who answered.""",
    r"""Plain `down` ignores profiled services, so the proxy keeps running and holds on to the network. Add the profile to remove everything.""",
]

new["task"] = {
    "steps": [
        r"""In your hello-devops repo, write `compose.yaml` from scratch: a `web` service built from your Dockerfile and a `redis` service from `redis:8-alpine` with a named volume at `/data`.""",
        r"""Publish port 8000 for web only, set `REDIS_HOST` and `APP_VERSION`, and give redis a healthcheck that web waits for.""",
        r"""Stop any Day 20 containers that still use port 8000, then run `docker compose up -d --build` and wait for `(healthy)`.""",
        r"""Call the app five times, run `docker compose down`, start it again, and check that the count continues.""",
        r"""Add `compose.override.yaml` with a `${GREETING:-...}` value and a `develop.watch` section. Put a greeting in `.env` and confirm it with `docker compose config`.""",
        r"""Run `docker compose watch`, change the reply of `/healthz` in app.py, and curl it until you see the change.""",
        r"""Add the nginx proxy as a profile with `docker/nginx.conf`, start it, and reach the app through port 8080.""",
        r"""Finish with `docker compose --profile proxy down -v`, then commit compose.yaml, compose.override.yaml and docker/nginx.conf (not .env).""",
    ],
    "hints": [
        r"""The long form of `depends_on` is a map: the service name, then `condition:` under it.""",
        r"""`docker compose config` is the fastest way to see why a value is not what you expected.""",
        r"""Compare your files with the ones in Files only after yours work.""",
    ],
    "done_when": r"""You are done when a save to app.py shows up in `curl localhost:8000/healthz` without running any docker command yourself.""",
}

new["explain_back"] = {
    "prompt": r"""Explain in 3 to 4 sentences what `docker compose up -d` does for hello-devops, and why the visit count survives `docker compose down`. Mention the project network, depends_on and the volume.""",
    "answer": r"""Compose reads compose.yaml and the override, then creates a project network, a named volume and the containers. Because web depends on redis with condition service_healthy, it starts Redis first and waits until `redis-cli ping` passes. Docker's DNS on the project network turns the service name redis into the Redis container's IP, so `REDIS_HOST=redis` is enough. Redis keeps its data in the named volume, and `docker compose down` removes containers and the network but not named volumes, so the count is still there next time.""",
}

new["recap"] = [
    "compose.yaml describes the whole app; docker compose up makes reality match it.",
    "Every project gets its own network, so service names work as hostnames.",
    "depends_on waits for running; add a healthcheck and service_healthy to wait for ready.",
    "`docker compose down` keeps named volumes; `down -v` deletes them.",
    ".env fills placeholders in the file; env_file sends variables into the container.",
    "Override files, profiles and watch keep the base file simple and the loop fast; but Compose runs on one machine only.",
]

new["check"] = [
    (r"""A compose.yaml uses `depends_on: [db]` in the short form, and db has no healthcheck. What does Compose wait for before starting the app?""",
     r"""The short form only orders container starts; waiting for readiness needs a healthcheck and condition: service_healthy."""),
    (r"""Your compose.yaml says `image: "shop:${TAG:-dev}"`. The `.env` file says `TAG=1.4`, and you run `TAG=1.5 docker compose up -d`. Which image runs?""",
     r"""A variable from your shell wins over the .env file, and the default after :- is used only when neither sets it."""),
    (r"""A teammate adds an `adminer` database tool to compose.override.yaml with `profiles: ["tools"]`. In CI, the pipeline runs `docker compose -f compose.yaml up -d`. Does adminer start in CI?""",
     r"""With -f compose.yaml the override file is not read at all, and a service in a profile only starts when that profile is asked for."""),
]

new["interview"] = [
    (r"""Is Docker Compose suitable for production?""",
     r"""For local development, demos and CI test setups, Compose works very well: one file, one command. It runs containers on a single host, so it cannot spread them over several machines or move them when a machine dies. Some small apps do run with Compose on one server, and Docker documents how to do that. Most teams use Kubernetes or a managed container service in production, and the images stay the same either way."""),
    (r"""How do you make one service wait until another is really ready in Compose?""",
     r"""Plain `depends_on` only waits until the other container is running. I give the dependency a healthcheck, such as `pg_isready` for Postgres or `redis-cli ping` for Redis, and use `depends_on` with `condition: service_healthy`. For one-off jobs such as migrations, `service_completed_successfully` waits for a clean exit. The app should still retry and report itself unready, because dependencies can fail after startup too."""),
    (r"""How do you keep one Compose setup for both laptops and CI?""",
     r"""I keep a lean, shared compose.yaml and put laptop-only settings, such as watch, debug tools and friendly defaults, in compose.override.yaml, which Compose merges automatically. CI runs `docker compose -f compose.yaml`, so it never sees the override, and can add its own file with a second `-f`. Optional extras go behind profiles. `docker compose config` shows the merged result whenever someone is unsure what will run."""),
]

new["deeper"] = OL["deeper"]["body"] + r"""

A note on versions, since you will see different numbers online. The current tool is Compose v5. It works like Compose v2 and adds a Go library for other tools. The version number jumped to avoid confusion with the old file format versions."""

new["closing"] = r"""We started with a kitchen run by phone calls, where the sauce began before the oven was hot. Now one file is the plan on the wall. Redis is healthy before web starts, `down` clears the counters and keeps the pantry, and a saved change reaches the running app by itself. Look at any compose.yaml you come across and check its `depends_on`. If it is the short form with no healthcheck, that app is starting its sauce on a cold oven.

Next, we'll make the image itself ready for production. How do you make it smaller, run it without root, and keep secrets out of it?"""

apply(L, new)
save(path, P, L, OL)
