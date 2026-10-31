from common import cap, join, lab, lines, ref, src, step
from cap import mapped
import pathlib

C = lambda k: cap("d15", k)
WATCH = pathlib.Path(__file__).with_name("out").joinpath("d15_watch.log").read_text().rstrip("\n").split("\n")
WATCH_TAIL = "\n".join(mapped(l, {"v2p3-hello-devops": "hello-devops"}).rstrip() for l in WATCH[-6:])

SVG = (
    '<svg viewBox="0 0 560 256" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="compose.yaml and compose.override.yaml are merged by docker compose up into one project: a proxy in a profile, web and redis on the project network, and a redis-data volume">'
    '<rect class="bx" x="8" y="60" width="140" height="40" rx="10"/><text class="t" x="78" y="85" font-size="13" text-anchor="middle">compose.yaml</text>'
    '<rect class="bx" x="8" y="116" width="140" height="40" rx="10"/><text class="t" x="78" y="141" font-size="13" text-anchor="middle">override.yaml</text>'
    '<line class="ln" x1="148" y1="80" x2="176" y2="104" marker-end="url(#ar)"/><line class="ln" x1="148" y1="136" x2="176" y2="114" marker-end="url(#ar)"/>'
    '<rect class="bxp" x="180" y="86" width="104" height="46" rx="10"/><text class="tk" x="232" y="106" font-size="13" text-anchor="middle">compose</text><text class="tk" x="232" y="122" font-size="13" text-anchor="middle">up</text>'
    '<line class="ln" x1="284" y1="109" x2="314" y2="109" marker-end="url(#ar)"/>'
    # project outline
    '<line class="lnd" x1="318" y1="12" x2="552" y2="12"/><line class="lnd" x1="318" y1="244" x2="552" y2="244"/>'
    '<line class="lnd" x1="318" y1="12" x2="318" y2="244"/><line class="lnd" x1="552" y1="12" x2="552" y2="244"/>'
    '<rect class="bxo" x="336" y="24" width="132" height="38" rx="10"/><text class="tk" x="402" y="48" font-size="13" text-anchor="middle">proxy</text>'
    '<rect class="bxt" x="336" y="82" width="132" height="38" rx="10"/><text class="tk" x="402" y="106" font-size="13" text-anchor="middle">web</text>'
    '<rect class="bxt" x="336" y="140" width="132" height="38" rx="10"/><text class="tk" x="402" y="164" font-size="13" text-anchor="middle">redis</text>'
    '<rect class="bxg" x="336" y="196" width="132" height="38" rx="10"/><text class="tk" x="402" y="220" font-size="13" text-anchor="middle">redis-data</text>'
    '<line class="ln" x1="402" y1="62" x2="402" y2="78" marker-end="url(#ar)"/><line class="ln" x1="402" y1="120" x2="402" y2="136" marker-end="url(#ar)"/>'
    '<line class="ln" x1="402" y1="178" x2="402" y2="192" marker-end="url(#ar)"/>'
    '<text class="ts" x="510" y="47" font-size="11" text-anchor="middle">:8080</text><text class="ts" x="510" y="61" font-size="11" text-anchor="middle">profile</text>'
    '<text class="ts" x="510" y="105" font-size="11" text-anchor="middle">:8000</text>'
    '<text class="ts" x="510" y="163" font-size="11" text-anchor="middle">healthy?</text>'
    '<text class="ts" x="510" y="219" font-size="11" text-anchor="middle">volume</text>'
    "</svg>"
)

LESSON = {
    "id": "d15",
    "title": "Docker Compose",
    "minutes": 50,
    "goal": "By the end you can describe hello-devops and Redis in one compose.yaml, run and inspect the stack with docker compose, and use .env, profiles, override files and watch for local development.",
    "guess": {
        "q": "You run `docker compose down` on hello-devops, which keeps Redis data in a named volume. What happens to the visit count?",
        "options": [
            "It is lost, because down deletes everything Compose made",
            "It is saved into the web image for next time",
            "It is copied to your Mac before the containers stop",
            "It survives, because down keeps named volumes unless you add -v",
        ],
        "answer": 3,
        "why": "`docker compose down` removes the containers and the network but keeps named volumes. Only `docker compose down -v` deletes them, and the data with them.",
    },
    "terms": [
        {"term": "Docker Compose", "plain": "A tool that runs a multi-container app from one YAML file with one command."},
        {"term": "Service", "plain": "One entry in a Compose file that describes a container to run, such as web or redis."},
        {"term": "Project", "plain": "Everything Compose creates for one app; named after the folder unless you set a name."},
        {"term": "Healthcheck", "plain": "A command Docker runs again and again to test whether a container is working."},
        {"term": "Restart policy", "plain": "A rule that tells Docker whether to start a container again after its process stops."},
        {"term": "Override file", "plain": "A second Compose file, such as compose.override.yaml, whose settings Compose merges on top of the first."},
        {"term": "Profile", "plain": "A label on a service that keeps it switched off until you ask for that profile."},
        {"term": "Compose Watch", "plain": "A Compose mode that copies your code changes into running containers or rebuilds them."},
    ],
    "sections": [
        {
            "h": "Compose describes the app you want",
            "body": (
                "On Day 14 you wired up hello-devops and Redis by hand: a network, a volume and two long `docker run` commands, typed in the right order. "
                "That is imperative: you tell Docker each step. It works, and nobody wants to do it twice.\n\n"
                "Docker Compose is declarative. You describe the finished app in one file, `compose.yaml`, and `docker compose up` works out the steps. "
                "Run it again and Compose changes only what differs from the file. Teammates get the same setup by cloning the repo.\n\n"
                "The file format is the Compose Specification. Two version notes save confusion:\n\n"
                "- The current tool is Compose v5. It works like Compose v2 and adds a Go library for other tools. The version number jumped to avoid confusion with the old file format versions.\n"
                "- You will see `version: \"3.8\"` at the top of old files. Compose ignores that line, so leave it out.\n\n"
                "Compose groups everything it creates into a project, named after the folder. In your `hello-devops` folder that gives a network called `hello-devops_default`, a volume called `hello-devops_redis-data` and containers called `hello-devops-web-1` and `hello-devops-redis-1`. "
                "The `-1` is a counter, because Compose can run several copies of one service."
            ),
            "refs": ref("compose_model", "compose_history", "nana_compose"),
        },
        {
            "h": "Reading the lab's compose.yaml",
            "body": (
                "The lab's file, in the Files section, has two top-level keys. `services` holds one entry per container, and `volumes` declares the named volume. "
                "You do not declare a network: Compose creates one per project and puts every service on it, so service names work as DNS names, just like on Day 14.\n\n"
                "Inside a service you will meet these keys:\n\n"
                "- `build: .` builds the image from the Dockerfile in this folder. `image:` uses a ready-made image instead, such as `redis:8-alpine`.\n"
                "- `ports:` publishes ports, written `\"HOST:CONTAINER\"` in quotes so YAML does not misread them.\n"
                "- `environment:` sets env vars. `env_file:` reads them from a file instead.\n"
                "- `volumes:` mounts named volumes or folders, as `redis-data:/data`.\n"
                "- `depends_on:` controls start order, with an optional health condition.\n"
                "- `healthcheck:` tells Docker how to test the container.\n"
                "- `restart:` says what to do when the process stops.\n\n"
                "Notice what the web service says: `REDIS_HOST: redis`. Redis has no `ports:` entry, because only web talks to it, over the project network. "
                "Only port 8000 is open to your Mac."
            ),
            "refs": ref("compose_services", "compose_net"),
        },
        {
            "h": "Running is not ready: depends_on and healthchecks",
            "body": (
                "`depends_on` makes Compose start Redis before web. In its short form, `depends_on: [redis]`, it only waits until the Redis container is running. "
                "A database can need several more seconds before it accepts connections, so running is not the same as ready.\n\n"
                "A healthcheck closes that gap. It is a command Docker runs inside the container on a schedule, and exit code 0 means healthy (the exit codes from Day 6). "
                "The lab runs `redis-cli ping` every 5 seconds, with a 3-second timeout and 5 retries. "
                "The long form of `depends_on` then waits for it:\n\n"
                "- `condition: service_healthy` waits until the healthcheck passes.\n"
                "- `condition: service_completed_successfully` waits until a one-off job, such as a database migration, exits with 0.\n"
                "- `condition: service_started` is the short form's behaviour.\n\n"
                "In the worked example, `docker compose up -d` showed Redis as `Healthy` after 5.8 seconds and started web only then. "
                "`docker compose ps` shows `(health: starting)`, then `(healthy)`, or `(unhealthy)` if the check keeps failing.\n\n"
                "This only covers startup. When Redis dies later, hello-devops answers `/readyz` with a 503, and `/` returns a 500 error until Redis is back. "
                "Your app must still cope when a dependency fails, and Kubernetes uses that readiness answer on Day 35."
            ),
            "refs": ref("startup"),
        },
        {
            "h": "The everyday commands, and restart policies",
            "body": (
                "These commands cover most days, run in the folder with `compose.yaml`:\n\n"
                "- `docker compose up -d` creates and starts everything in the background; add `--build` to rebuild images first.\n"
                "- `docker compose ps` shows each container, its health and its ports.\n"
                "- `docker compose logs -f web` follows one service's output.\n"
                "- `docker compose exec redis redis-cli GET visits` runs a command in a running service.\n"
                "- `docker compose run --rm redis redis-cli -h redis ping` starts a new one-off container for a command, then removes it.\n"
                "- `docker compose down` removes the containers and the network, and keeps named volumes.\n"
                "- `docker compose down -v` also deletes the named volumes, and with them your data.\n"
                "- `docker compose config` prints the final file after merging and filling in variables.\n\n"
                "A restart policy says what Docker does when a container's process stops:\n\n"
                "- `no`, the default: leave it stopped.\n"
                "- `on-failure`: start it again only if it exited with a non-zero code.\n"
                "- `always`: always start it again.\n"
                "- `unless-stopped`: like always, except after you stopped it yourself.\n\n"
                "The override file in this lesson sets `unless-stopped`. We shut Redis down from inside with `redis-cli shutdown`. "
                "Docker started it again within seconds, its restart count went to 1, and the visit count carried on."
            ),
            "refs": ref("ref_compose_up", "restart"),
        },
        {
            "h": "Variables: .env, environment and env_file",
            "body": (
                "Compose can fill in placeholders in the file itself. Take `GREETING: \"${GREETING:-Hello from Compose}\"`. "
                "Compose looks for `GREETING` in your shell, then in a file named `.env` next to `compose.yaml`, and uses the default after `:-` if neither has it. "
                "We checked all three with `docker compose config | grep GREETING`:\n\n"
                "1. With nothing set, it printed `GREETING: Hello from Compose`.\n"
                "2. With `GREETING=Hi from .env` in `.env`, it printed `Hi from .env`.\n"
                "3. With `GREETING='Hi from my shell'` before the command, the shell won.\n\n"
                "Two files with similar names do different jobs, and this trips most people up:\n\n"
                "- `.env` fills in `${...}` placeholders in the Compose file. Its values do not reach containers unless the file passes them on.\n"
                "- `env_file: web.env` under a service sends every line of that file into the container as environment variables.\n\n"
                "If `.env` ever holds secrets, keep it out of git; the lab's `.gitignore` already lists it. "
                "When something looks wrong, run `docker compose config` first. It shows the file exactly as Compose will use it."
            ),
            "refs": ref("interp", "precedence"),
        },
        {
            "h": "Override files and profiles",
            "body": (
                "Compose reads `compose.yaml` and then, if it exists, `compose.override.yaml` from the same folder, and merges the two. "
                "That lets the base file stay simple and shared, while the override adds things only your laptop needs. The merge follows a few rules:\n\n"
                "- A single value, such as `image` or `command`, is replaced by the override.\n"
                "- Maps, such as `environment`, are merged key by key.\n"
                "- Some lists, such as `ports`, are joined, so an override cannot remove a published port.\n"
                "- Paths are relative to the first file, the base one.\n\n"
                "`-f` picks files by hand. `docker compose -f compose.yaml up -d` uses only the base file, which is what CI should run. "
                "`-f compose.yaml -f compose.ci.yaml` stacks another file on top.\n\n"
                "A profile keeps a service switched off until you ask for it. The lab's override adds nginx in front of web, the reverse proxy you built on Day 9, with `profiles: [\"proxy\"]`. "
                "Plain `docker compose up -d` ignores it; `docker compose --profile proxy up -d` starts it too. "
                "Use profiles for extras such as a proxy, a database admin tool or a load generator.\n\n"
                "One gotcha we hit while testing: plain `docker compose down` left the proxy running, and Compose reported that the network was still in use. "
                "Stop profiled services with the same `--profile` flag you started them with."
            ),
            "refs": ref("merge", "profiles"),
        },
        {
            "h": "Compose Watch for a fast inner loop",
            "body": (
                "The inner loop is the cycle you repeat all day: edit, run, look. With plain Compose, every code change means `docker compose up -d --build`. "
                "Compose Watch shortens that. You list paths under `develop.watch` in the Compose file, run `docker compose watch`, and Compose reacts to every save:\n\n"
                "- `sync` copies the changed files into the running container. Good for apps that reload code by themselves.\n"
                "- `sync+restart` copies the files, then restarts the container. Good for gunicorn without reload.\n"
                "- `rebuild` builds a new image and replaces the container. Use it for `requirements.txt`, because new packages need a new image.\n\n"
                "The lab's override uses `sync+restart` for `app.py` and `rebuild` for `requirements.txt`. "
                "We changed the reply of `/healthz` while watch ran. It printed `Syncing service \"web\" after 1 changes were detected`, restarted web, and the next curl showed the new reply. "
                "The copied file arrived owned by the container's user, so it works with the non-root image from Day 16 too.\n\n"
                "Why not a bind mount of the whole folder? It works, but on a Mac every file read crosses into the VM, and a bind mount also hides what the image had at that path. "
                "Watch copies only what changed and keeps the image's files. Keep bind mounts for files you want both sides to edit."
            ),
            "refs": ref("watch"),
        },
    ],
    "analogy": (
        "compose.yaml is like the stage plan a band sends to a venue. It lists each musician (service), their instruments (images), who must be on stage and tuned before the show starts (depends_on with a health condition), and which microphones face the audience (ports). "
        "The crew reads the plan and sets the stage, and `down` clears it while the storage room (volumes) keeps its boxes. "
        "The picture fails on improvising: a stage crew adapts on the night, while Compose only does exactly what the file says, and only on one machine."
    ),
    "diagram": SVG,
    "diagram_caption": "Compose merges the base file and the override into one project: services on one network, plus a named volume.",
    "worked": {
        "title": "Run the whole stack, then poke at it",
        "steps": [
            step("In your hello-devops folder, with the lab's `compose.yaml` and the override from Files, start everything. Compose creates the volume and network, waits until Redis is healthy, and only then starts web.",
                 C("up")),
            step("Check the containers and call the app. The greeting comes from the override file, and the count rises by one each time, because both gunicorn workers share one Redis.",
                 join(C("ps"), C("curl3"))),
            step("Read web's logs, look inside Redis, and run a one-off container. `run --rm` starts a fresh redis container just for `ping`, talks to the service named redis over the network, and removes itself.",
                 join(C("logs"), C("exec"), C("run"))),
            step("Shut Redis down from inside. The restart policy `unless-stopped` brings it back, and the count carries on, because Redis saved its data to the volume on the way down.",
                 join(C("shutdown"), C("ps_after"), C("restarts"), C("curl_after_restart"))),
            step("Take the stack down. The containers and network go, the volume stays. After `docker compose up -d` the count continues at 5.",
                 join(C("down"), C("vol_after_down"), C("curl_after_down"))),
            step("Start the proxy profile. nginx answers on port 8080 and passes requests to web by its service name; the `Server` header shows who answered.",
                 join(C("up_proxy"), C("curl_proxy"), C("curl_proxy_head"))),
            step("Now the gotcha. Plain `down` ignores profiled services, so the proxy keeps running and holds on to the network. Add the profile to remove everything.",
                 join(C("down_noprofile"), C("left"), C("down_profile"))),
        ],
    },
    "code": [
        {"lang": "yaml", "title": "compose.yaml (the lab's file)", "src": lab("compose.yaml"), "run": "docker compose up -d --build"},
        {"lang": "yaml", "title": "compose.override.yaml (lab: docker/compose.override.yaml; copy it next to compose.yaml)", "src": lab("docker/compose.override.yaml"), "run": "cp docker/compose.override.yaml . && docker compose up -d && docker compose watch"},
        {"lang": "text", "title": "docker/nginx.conf (used by the proxy profile)", "src": lab("docker/nginx.conf"), "run": "docker compose --profile proxy up -d && curl -sI localhost:8080"},
    ],
    "commands": [
        {"cmd": "docker compose up -d", "what": "Create and start every service in the background."},
        {"cmd": "docker compose up -d --build", "what": "Rebuild images that have a build section, then start."},
        {"cmd": "docker compose ps", "what": "Show the project's containers, health and ports."},
        {"cmd": "docker compose logs -f web", "what": "Follow the output of one service (Ctrl+C to stop)."},
        {"cmd": "docker compose exec redis redis-cli GET visits", "what": "Run a command inside a running service container."},
        {"cmd": "docker compose run --rm redis redis-cli -h redis ping", "what": "Run a one-off container of a service, then remove it."},
        {"cmd": "docker compose down", "what": "Remove the containers and the network; named volumes stay."},
        {"cmd": "docker compose down -v", "what": "Also delete the named volumes, and the data in them."},
        {"cmd": "docker compose config", "what": "Print the merged file with every variable filled in."},
        {"cmd": "docker compose config --services", "what": "List the services Compose sees, after merging."},
        {"cmd": "docker compose --profile proxy up -d", "what": "Also start services in the proxy profile."},
        {"cmd": "docker compose --profile proxy down", "what": "Stop and remove everything, including the proxy profile."},
        {"cmd": "docker compose -f compose.yaml up -d", "what": "Use only the base file and skip compose.override.yaml, as CI does."},
        {"cmd": "docker compose watch", "what": "Start the app and copy code changes in, or rebuild, as you save."},
    ],
    "mistake": (
        "It is easy to type `docker compose down -v` when you meant `docker compose down`. "
        "The `-v` deletes the named volumes, so your Redis data, or a whole development database, is gone for good. "
        "Use plain `down` day to day, and keep `down -v` for when you really want a clean start."
    ),
    "real_world": (
        "Every service repo at PayFlow has a compose.yaml, so a new engineer starts the service and its Postgres and Redis with one command. "
        "A compose.override.yaml adds watch and debug tools on laptops, while CI runs `docker compose -f compose.yaml up -d --wait` to get real dependencies for integration tests. "
        "Production looks different: the same images run on Kubernetes (Day 30), and the databases are managed services."
    ),
    "task": {
        "title": "Write the Compose files yourself and use them for development",
        "steps": [
            "In your hello-devops repo, write `compose.yaml` from scratch: a `web` service built from your Dockerfile and a `redis` service from `redis:8-alpine` with a named volume at `/data`.",
            "Publish port 8000 for web only, set `REDIS_HOST` and `APP_VERSION`, and give redis a healthcheck that web waits for.",
            "Stop any Day 14 containers that still use port 8000, then run `docker compose up -d --build` and wait for `(healthy)`.",
            "Call the app five times, run `docker compose down`, start it again, and check that the count continues.",
            "Add `compose.override.yaml` with a `${GREETING:-...}` value and a `develop.watch` section. Put a greeting in `.env` and confirm it with `docker compose config`.",
            "Run `docker compose watch`, change the reply of `/healthz` in app.py, and curl it until you see the change.",
            "Add the nginx proxy as a profile with `docker/nginx.conf`, start it, and reach the app through port 8080.",
            "Finish with `docker compose --profile proxy down -v`, then commit compose.yaml, compose.override.yaml and docker/nginx.conf (not .env).",
        ],
        "hints": [
            "The long form of `depends_on` is a map: the service name, then `condition:` under it.",
            "`docker compose config` is the fastest way to see why a value is not what you expected.",
            "Compare your files with the ones in Files only after yours work.",
        ],
        "done_when": "You are done when a save to app.py shows up in `curl localhost:8000/healthz` without running any docker command yourself.",
    },
    "explain_back": {
        "prompt": "Explain in 3 to 4 sentences what `docker compose up -d` does for hello-devops, and why the visit count survives `docker compose down`. Mention the project network, depends_on and the volume.",
        "answer": (
            "Compose reads compose.yaml and the override, then creates a project network, a named volume and the containers. "
            "Because web depends on redis with condition service_healthy, it starts Redis first and waits until `redis-cli ping` passes. "
            "Docker's DNS on the project network turns the service name redis into the Redis container's IP, so `REDIS_HOST=redis` is enough. "
            "Redis keeps its data in the named volume, and `docker compose down` removes containers and the network but not named volumes, so the count is still there next time."
        ),
    },
    "recap": [
        "compose.yaml describes the whole app; docker compose up makes reality match it.",
        "Every project gets its own network, so service names work as hostnames.",
        "depends_on waits for running; add a healthcheck and service_healthy to wait for ready.",
        "`docker compose down` keeps named volumes; `down -v` deletes them.",
        ".env fills placeholders in the file; env_file sends variables into the container.",
        "Override files, profiles and watch keep the base file simple and the dev loop fast.",
    ],
    "check": [
        {
            "q": "A compose.yaml uses `depends_on: [db]` in the short form, and db has no healthcheck. What does Compose wait for before starting the app?",
            "options": [
                "The database to accept connections",
                "The db container to be running, not ready",
                "The db healthcheck to pass",
                "Nothing; the start order is random",
            ],
            "answer": 1,
            "why": "The short form only orders container starts; waiting for readiness needs a healthcheck and condition: service_healthy.",
        },
        {
            "q": "Your compose.yaml says `image: \"shop:${TAG:-dev}\"`. The `.env` file says `TAG=1.4`, and you run `TAG=1.5 docker compose up -d`. Which image runs?",
            "options": [
                "shop:1.5",
                "shop:1.4",
                "shop:dev",
                "Compose stops with an error about two values",
            ],
            "answer": 0,
            "why": "A variable from your shell wins over the .env file, and the default after :- is used only when neither sets it.",
        },
        {
            "q": "A teammate adds an `adminer` database tool to compose.override.yaml with `profiles: [\"tools\"]`. In CI, the pipeline runs `docker compose -f compose.yaml up -d`. Does adminer start in CI?",
            "options": [
                "Yes, because profiles start by default",
                "Yes, because CI merges every Compose file",
                "No: CI reads only compose.yaml, and the tools profile is off anyway",
                "No, because Compose cannot run database tools",
            ],
            "answer": 2,
            "why": "With -f compose.yaml the override file is not read at all, and a service in a profile only starts when that profile is asked for.",
        },
    ],
    "interview": [
        {
            "q": "Is Docker Compose suitable for production?",
            "a": (
                "For local development, demos and CI test setups, Compose works very well: one file, one command. "
                "It runs containers on a single host, so it cannot spread them over several machines or move them when a machine dies. "
                "Some small apps do run with Compose on one server, and Docker documents how to do that. "
                "Most teams use Kubernetes or a managed container service in production, and the images stay the same either way."
            ),
        },
        {
            "q": "How do you make one service wait until another is really ready in Compose?",
            "a": (
                "Plain `depends_on` only waits until the other container is running. "
                "I give the dependency a healthcheck, such as `pg_isready` for Postgres or `redis-cli ping` for Redis, and use `depends_on` with `condition: service_healthy`. "
                "For one-off jobs such as migrations, `service_completed_successfully` waits for a clean exit. "
                "The app should still retry and report itself unready, because dependencies can fail after startup too."
            ),
        },
        {
            "q": "How do you keep one Compose setup for both laptops and CI?",
            "a": (
                "I keep a lean, shared compose.yaml and put laptop-only settings, such as watch, debug tools and friendly defaults, in compose.override.yaml, which Compose merges automatically. "
                "CI runs `docker compose -f compose.yaml`, so it never sees the override, and can add its own file with a second `-f`. "
                "Optional extras go behind profiles. "
                "`docker compose config` shows the merged result whenever someone is unsure what will run."
            ),
        },
    ],
    "deeper": {
        "minutes": 12,
        "body": (
            "Compose Watch is easiest to understand by watching its output. With the lab's override in place, run `docker compose watch` in one terminal. "
            "It builds the image, starts the stack, then prints `Watch enabled` and waits. In a second terminal, change the reply of `/healthz` in app.py and save. "
            "These are the last lines watch printed in our test:\n\n"
            + "\n".join("- `" + l.strip() + "`" for l in WATCH_TAIL.split("\n")) + "\n\n"
            "Two details matter for real projects. First, list paths you never want copied under `ignore:` in each watch entry, such as test folders. "
            "Second, Docker's docs advise against syncing a dependency folder such as `node_modules`; let a `rebuild` rule install dependencies inside the image instead.\n\n"
            "CI wants a different thing from Compose: start the stack and fail fast if it is not healthy. "
            "`docker compose -f compose.yaml up -d --wait` returns only when every service with a healthcheck is healthy, and fails if one becomes unhealthy. "
            "That makes it a good first step before integration tests.\n\n"
            "You might try `docker compose up -d --scale web=3` to get three copies of web. With the lab's file it fails, because each copy would want host port 8000. "
            "The fix is to stop publishing web at all and let the nginx proxy be the only published service. nginx then reaches the web copies by the name `web` over the project network. "
            "Kubernetes does this job properly on Day 33 with a Service.\n\n"
            "Large setups split Compose files. `include:` pulls another Compose file into this one, and `extends:` reuses one service's settings in another. "
            "Docker's [guide to Compose in production](https://docs.docker.com/compose/how-tos/production/) explains how teams use an extra file for server settings when they do run Compose on a server."
        ),
    },
    "sources": src("compose_model", "startup", "merge", "watch"),
}
