from common import V1, cap, join, lab, lines, ref, src, step

C = lambda k: cap("d14", k)
V1D07 = next(x for x in V1["lessons"] if x["id"] == "d07")

SVG = (
    '<svg viewBox="0 0 560 262" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="On the demo network, a client reaches the web container by name through Docker\'s DNS; a container on the default bridge cannot; web serves files from the site volume, which outlives the container">'
    # demo network outline
    '<line class="lnd" x1="8" y1="12" x2="352" y2="12"/><line class="lnd" x1="8" y1="150" x2="352" y2="150"/>'
    '<line class="lnd" x1="8" y1="12" x2="8" y2="150"/><line class="lnd" x1="352" y1="12" x2="352" y2="150"/>'
    '<text class="ts" x="180" y="140" font-size="11" text-anchor="middle">demo network, DNS at 127.0.0.11</text>'
    # default bridge outline
    '<line class="lnd" x1="376" y1="12" x2="552" y2="12"/><line class="lnd" x1="376" y1="150" x2="552" y2="150"/>'
    '<line class="lnd" x1="376" y1="12" x2="376" y2="150"/><line class="lnd" x1="552" y1="12" x2="552" y2="150"/>'
    '<text class="ts" x="464" y="140" font-size="11" text-anchor="middle">default bridge</text>'
    # boxes
    '<rect class="bxt" x="24" y="44" width="104" height="46" rx="10"/><text class="tk" x="76" y="72" font-size="13" text-anchor="middle">client</text>'
    '<rect class="bxo" x="216" y="44" width="120" height="46" rx="10"/><text class="tk" x="276" y="72" font-size="13" text-anchor="middle">web</text>'
    '<rect class="bx" x="414" y="44" width="100" height="46" rx="10"/><text class="t" x="464" y="72" font-size="13" text-anchor="middle">b</text>'
    '<rect class="bxg" x="216" y="196" width="120" height="46" rx="10"/><text class="tk" x="276" y="224" font-size="13" text-anchor="middle">site volume</text>'
    # arrows
    '<line class="ln" x1="128" y1="67" x2="212" y2="67" marker-end="url(#ar)"/><text class="ts" x="170" y="60" font-size="11" text-anchor="middle">http://web</text>'
    '<line class="lnd" x1="414" y1="67" x2="340" y2="67" marker-end="url(#ar)"/><text class="ts" x="464" y="112" font-size="11" text-anchor="middle">bad address</text>'
    '<line class="ln" x1="276" y1="90" x2="276" y2="192" marker-end="url(#ar)"/><text class="ts" x="288" y="176" font-size="11" text-anchor="start">mounted</text>'
    "</svg>"
)

LESSON = {
    "id": "d14",
    "title": "Volumes and networks",
    "minutes": 50,
    "goal": "By the end you can keep data safe in volumes, choose between volumes, bind mounts and tmpfs, and connect containers on a user-defined network where they find each other by name.",
    "guess": {
        "q": "Two containers, `api` and `db`, run on Docker's default network. Inside api, `ping db` runs. What happens?",
        "options": [
            "It fails with a bad address: the default network has no lookup by name",
            "It works, because Docker registers every container name",
            "It works, but only if db was started with -p",
            "It works on a Mac and fails on Linux",
        ],
        "answer": 0,
        "why": "Only user-defined networks have Docker's built-in DNS server. On the default bridge, containers can reach each other by IP address only.",
    },
    "terms": [
        {"term": "Volume", "plain": "Storage that Docker creates and manages, which outlives the containers that use it."},
        {"term": "Bind mount", "plain": "A folder from your computer shown inside a container, so both sides see the same files."},
        {"term": "tmpfs mount", "plain": "Storage in memory only; it disappears when the container stops."},
        {"term": "Anonymous volume", "plain": "A volume without a name, given a random ID by Docker; easy to forget and leave behind."},
        {"term": "Bridge network", "plain": "A private virtual network on one Docker host; containers on it get their own IP addresses."},
        {"term": "User-defined network", "plain": "A bridge network you create yourself; containers on it find each other by name."},
        {"term": "Embedded DNS server", "plain": "Docker's name server at 127.0.0.11 inside containers on user-defined networks."},
        {"term": "Publish a port", "plain": "Make a container port reachable from the host with -p; EXPOSE only documents a port."},
    ],
    "sections": [
        {
            "h": "Containers are disposable, so where does data live?",
            "body": (
                "On Day 12 you saw where a container's own files go: into its thin writable layer, which `docker rm` deletes. "
                "That is what you want. You should be able to throw away any container and start a fresh one, for an upgrade or after a crash.\n\n"
                "So data you care about must live outside the container. Docker gives you three kinds of mounts, which attach storage at a folder inside the container. "
                "Pick by asking who owns the data:\n\n"
                "- Docker owns it, such as a database's files: use a volume.\n"
                "- You own it, such as source code you edit on your Mac: use a bind mount.\n"
                "- Nobody should keep it, such as a temporary token: use a tmpfs mount.\n\n"
                "Volumes also fix a speed problem. Writes into the container layer go through copy-on-write, which is slow for big, busy files. "
                "A volume skips the layers and writes straight to the disk.\n\n"
                "hello-devops has a data problem right now. The visit count lives in memory, so every restart resets it to zero. "
                "gunicorn also runs two worker processes, and each keeps its own count, so the number can jump back. "
                "Moving the count into Redis fixes both: the workers share one number, and Redis keeps it in a volume."
            ),
            "refs": ref("storage", "c_persist"),
        },
        {
            "h": "Volumes: storage Docker manages",
            "body": (
                "A named volume is created with `docker volume create notes`, or on the fly by `docker run -v notes:/data ...`. "
                "The left side of `-v` is the volume name and the right side is the folder inside the container. "
                "The same volume can be mounted into a new container later, and the data is still there.\n\n"
                "A few behaviours are worth knowing before they surprise you:\n\n"
                "- A new, empty volume mounted over a folder that has files in the image gets a copy of those files. Mount an empty volume at nginx's html folder, and `index.html` and `50x.html` appear in it.\n"
                "- `-v /data` with no name creates an anonymous volume with a random 64-character ID. Some images, such as `registry:3`, declare one in their Dockerfile, so you get one without asking.\n"
                "- Anonymous volumes stay behind after `docker rm`. Use `--rm`, or `docker rm -v`, to delete them with the container.\n"
                "- `docker volume inspect` shows a mount point under `/var/lib/docker/volumes`. On a Mac that path is inside Docker Desktop's VM, and Docker's docs say not to touch it directly.\n\n"
                "`--mount type=volume,source=notes,target=/data` is the long form of the same thing. It is wordier and harder to get wrong, so many teams use it in scripts.\n\n"
                "To back up a volume, mount it into a throwaway container next to a folder from your Mac and run `tar` there. "
                "The lab's `docker/volume-backup.sh` does exactly that, and it restores the archive into another volume too."
            ),
            "refs": ref("volumes", "c_persist"),
        },
        {
            "h": "Bind mounts, tmpfs and file ownership",
            "body": (
                "A bind mount shows a folder from your Mac inside the container: `-v \"$PWD/site\":/usr/share/nginx/html`. "
                "A path on the left side means a bind mount, and a plain name means a volume. "
                "Both sides see every change at once, which is great while you edit code. Add `:ro` to make the mount read-only inside the container.\n\n"
                "Two things bite people:\n\n"
                "- A bind mount hides whatever the image had at that path. Mount an empty folder over nginx's html folder, and nginx serves nothing.\n"
                "- On a Mac, files cross from macOS into Docker's Linux VM through a file sharing layer called VirtioFS. Folders with many small files can be slower than a volume.\n\n"
                "File ownership works by user ID numbers, not names. On a Linux machine, such as a CI runner, a container running as user 10001 tried to write into a bind-mounted folder owned by root. "
                "It failed with `touch: /out/from-10001.txt: Permission denied`. A file written by a root container showed up on the host owned by uid 0. "
                "Docker Desktop on a Mac hides most of this, because its file sharing makes files look like yours. "
                "So a setup that works on your laptop can still fail in CI. Day 6's permission rules explain every case.\n\n"
                "A tmpfs mount, `--tmpfs /scratch`, lives in memory only. We wrote a file to one, restarted the container, and the folder was empty again. "
                "Use it for scratch files and secrets that must never reach a disk."
            ),
            "refs": ref("bind", "tmpfs"),
        },
        {
            "h": "How containers talk: the default bridge",
            "body": (
                "Every container gets its own network namespace, so it has its own network card, IP address and `localhost`. "
                "Inside a container, `localhost` means that container itself, never your Mac and never another container. "
                "To reach a service on your Mac from a container, Docker Desktop offers the special name `host.docker.internal`.\n\n"
                "Docker connects containers through a bridge, a virtual network switch inside the Linux VM. "
                "Any container you start without `--network` joins the default network, called `bridge`, and gets an address such as `172.17.0.5`.\n\n"
                "The default bridge is old and limited:\n\n"
                "- Containers can reach each other only by IP address. `ping b` from container `a` printed `ping: bad address 'b'`, while `ping 172.17.0.5` worked.\n"
                "- Those addresses change when containers restart, so you cannot hard-code them.\n"
                "- Every container started without `--network` lands on it, so unrelated apps can talk to each other.\n\n"
                "For DNS, containers on the default bridge get a copy of the host's DNS settings. That lets them resolve names on the internet, but not each other. "
                "Docker's own docs say user-defined networks are better, and the next section shows why."
            ),
            "refs": ref("network", "bridge", "networkchuck"),
        },
        {
            "h": "User-defined networks: names that work",
            "body": (
                "Create a network with `docker network create demo` and start containers with `--network demo`. Three things improve at once:\n\n"
                "- Every container gets a DNS server at `127.0.0.11`, Docker's embedded DNS server. It answers with the current IP of any container on the same network, by name.\n"
                "- Containers on different user-defined networks cannot reach each other, so each app gets its own private network.\n"
                "- You can attach a running container to a network, or detach it, with `docker network connect` and `docker network disconnect`.\n\n"
                "In the worked example, `wget http://web` from a container on `demo` returned the page, and `cat /etc/resolv.conf` showed `nameserver 127.0.0.11`. "
                "The same request from a container on the default bridge failed with `bad address 'web'`.\n\n"
                "A container can sit on several networks, with one network card for each. That is how you build a proxy that talks to the outside on one network and to private services on another. "
                "`--network-alias api` gives a container an extra DNS name on a network, which helps when one name should point at several containers.\n\n"
                "Containers on the same network reach each other on any port. They need no `-p` at all, because `-p` is only for traffic from outside. "
                "Docker Compose creates one user-defined network per project, so everything in Day 15 gets name lookup for free."
            ),
            "refs": ref("bridge", "network"),
        },
        {
            "h": "host and none, and publishing versus exposing",
            "body": (
                "`bridge` is one of several network drivers. Two more matter on day one:\n\n"
                "- `--network none` gives a container no network at all. `ip addr` inside showed only the loopback `lo`. Good for batch jobs that must not talk to anything.\n"
                "- `--network host` skips the namespace and shares the host's network, so `-p` is ignored. On Docker Desktop it is off by default: you turn it on under Settings, Resources, Network, and you must be signed in.\n\n"
                "Others, such as `overlay`, `macvlan` and `ipvlan`, connect containers across machines or straight onto a physical network. You will not need them for this course.\n\n"
                "Publishing and exposing sound alike and do different things:\n\n"
                "- `EXPOSE 80` in a Dockerfile is documentation. `docker image inspect nginx` lists `{\"80/tcp\":{}}`, and nothing listens on your Mac because of it.\n"
                "- `-p 127.0.0.1:8080:80` publishes: it opens port 8080 on your Mac and forwards it. `docker port` then prints `80/tcp -> 127.0.0.1:8080`.\n"
                "- `-P` publishes every exposed port on a random free port of the host.\n\n"
                "A common mistake is to publish ports just so two containers can talk. Put them on one user-defined network instead, and publish only what a person or another machine must reach."
            ),
            "refs": ref("port_pub", "host", "none"),
        },
    ],
    "analogy": (
        "Think of an office building. The default bridge is an open-plan floor with no phone directory: you can call a colleague only if you know their extension number, and the numbers change when people move desks. "
        "A user-defined network is a floor with a receptionist who knows everyone on that floor by name. "
        "Volumes are the storage room in the basement: people come and go, and the boxes stay. "
        "The picture fails at the building's edge, because a volume stays on the one Docker host where it was made and does not follow your container to another machine."
    ),
    "diagram": SVG,
    "diagram_caption": "On a user-defined network, Docker's DNS turns names into IPs; the default bridge has no names. The volume outlives the container.",
    "worked": {
        "title": "Serve a page from a volume, reach it by name",
        "steps": [
            step("Create a named volume and mount it, still empty, over nginx's html folder in a throwaway container. Docker copies the image's files into the empty volume, so `ls` finds them.",
                 join(C("w_vol"), C("w_prepop"))),
            step("Replace the page with your own, using a second throwaway container that mounts the same volume. Then create a network and start nginx on it, named `web`, with the volume mounted. No `-p`: only containers will talk to it.",
                 join(C("w_write"), C("w_net"), C("w_web"))),
            step("Ask for the page by name from two places. From the default bridge, the name means nothing. From the `demo` network, Docker's DNS server at 127.0.0.11 answers.",
                 join(C("w_default"), C("w_named"), C("w_resolv"))),
            step("`nslookup` shows the answer the DNS server gave, and `docker network inspect` shows who is on the network and which subnet Docker picked.",
                 join(C("w_nslookup"), C("w_inspect"))),
            step("Throw the container away and start a new one with the same volume. The new container has a new ID, and the page is still there, because it lives in the volume.",
                 join(C("w_rm"), C("w_web2"), C("w_named2"))),
            step("Connect one container to two networks. Start two idle containers, `a` and `b`, on the default bridge with `docker run -d --name a alpine sleep 600`. They cannot find each other by name. After `docker network connect`, `a` has a second network card and can reach `web`; `b` still cannot.",
                 join(C("b_byname"), C("two_connect"), C("two_ip"), C("two_wget"), C("two_wget_b"))),
            step("Clean up: `docker rm -f web a b`, then `docker network rm demo` and `docker volume rm site`. A volume is never deleted by accident; you always remove it on purpose."),
        ],
    },
    "code": [
        {
            "lang": "bash",
            "title": "docker/network-demo.sh (in the lab repo)",
            "src": lab("docker/network-demo.sh"),
            "run": "bash docker/network-demo.sh",
        },
        {
            "lang": "bash",
            "title": "docker/volume-backup.sh (in the lab repo)",
            "src": lab("docker/volume-backup.sh"),
            "run": "bash docker/volume-backup.sh backup redis-data",
        },
    ],
    "commands": [
        {"cmd": "docker volume create redis-data", "what": "Create a named volume."},
        {"cmd": "docker volume ls", "what": "List volumes; they stay after their containers are gone."},
        {"cmd": "docker volume inspect redis-data", "what": "Show where a volume lives and when it was made."},
        {"cmd": "docker volume rm redis-data", "what": "Delete a volume and the data in it."},
        {"cmd": "docker run -d --name redis --network hello-net -v redis-data:/data redis:8-alpine", "what": "Run a container on a network with a volume mounted at /data."},
        {"cmd": "docker run --rm -v \"$PWD\":/work -w /work alpine ls", "what": "Bind-mount the current folder into a container and work in it."},
        {"cmd": "docker run -d --tmpfs /scratch alpine sleep 600", "what": "Give a container a memory-only folder."},
        {"cmd": "docker network create hello-net", "what": "Create a user-defined network where containers find each other by name."},
        {"cmd": "docker network ls", "what": "List networks, including bridge, host and none."},
        {"cmd": "docker network inspect hello-net", "what": "Show a network's subnet and the containers on it."},
        {"cmd": "docker network connect hello-net web", "what": "Attach a running container to one more network."},
        {"cmd": "docker port web", "what": "Show which host ports a container publishes."},
        {"cmd": "docker rm -v anon", "what": "Remove a container together with its anonymous volumes."},
    ],
    "mistake": (
        "The most common mistake is pointing one container at another with `localhost`, such as `REDIS_HOST=localhost`. "
        "Inside a container, `localhost` is that container itself, where nothing listens on Redis's port. "
        "Put both containers on one user-defined network and use the other container's name, such as `REDIS_HOST=redis`."
    ),
    "real_world": (
        "PayFlow's developers run Postgres in a container with a named volume, so `docker rm` during an upgrade never touches the data. "
        "In production, the databases are managed cloud services with backups and failover, not containers on one machine. "
        "CI jobs run integration tests on a fresh user-defined network per job, so parallel jobs on the same runner never see each other's containers."
    ),
    "task": {
        "title": "Run hello-devops and Redis by hand, with no Compose",
        "steps": [
            "Build your Day 13 image again if you removed it: `hello-devops:1.0.0`.",
            "Create a user-defined network `hello-net` and a named volume `redis-data`.",
            "Start `redis:8-alpine` named `redis` on that network, with the volume at `/data`. Do not publish its port.",
            "Start hello-devops named `web` on the same network, published on port 8000, with `REDIS_HOST` set so it finds Redis.",
            "Call the app five times and check that visits rises by one each time, even with two gunicorn workers.",
            "Stop and remove the Redis container, then call `/` and `/readyz`. Note the status codes.",
            "Start a brand-new Redis container on the same network and volume. Does the count carry on?",
            "Back up the volume with `docker/volume-backup.sh` and list what is inside the archive with `tar tzf`.",
            "Clean up the containers, the network and the volume.",
        ],
        "hints": [
            "The container name is the DNS name: `-e REDIS_HOST=redis`.",
            "`curl -s -o /dev/null -w '%{http_code}\\n' localhost:8000/readyz` prints only the status code.",
            "Stop Redis with `docker stop`, not `docker rm -f`, so it can save its data first.",
        ],
        "done_when": "You are done when a new Redis container on the same volume continues the visit count instead of starting again at 1.",
    },
    "explain_back": {
        "prompt": "Explain in 3 to 4 sentences how a web container finds a Redis container, and where Redis's data lives. Mention the user-defined network, the DNS server and the volume.",
        "answer": (
            "Both containers join one user-defined network, so each gets Docker's embedded DNS server at 127.0.0.11. "
            "When the app connects to the name redis, that DNS server answers with the Redis container's current IP address, so `REDIS_HOST=redis` is all the app needs. "
            "Redis writes its data to /data, where a named volume is mounted, so the data lives outside the container. "
            "I can remove and replace the Redis container, and the new one finds the same data in the volume."
        ),
    },
    "recap": [
        "A container's own files die with it; keep data you need in a volume.",
        "Volumes belong to Docker, bind mounts share a folder from your Mac, tmpfs lives in memory.",
        "File ownership in mounts follows user ID numbers, which matters most on Linux and in CI.",
        "The default bridge has no name lookup; a user-defined network adds DNS at 127.0.0.11.",
        "Inside a container, localhost is the container itself.",
        "EXPOSE documents a port; -p publishes it, and containers on one network need no -p.",
    ],
    "check": [
        {
            "q": "You want to edit HTML files on your Mac and see each change in an nginx container at once. Which option fits?",
            "options": [
                "A named volume mounted at the HTML folder",
                "COPY the files in a Dockerfile and rebuild",
                "A bind mount of your folder at the HTML folder",
                "A tmpfs mount at the HTML folder",
            ],
            "answer": 2,
            "why": "A bind mount shows your Mac's folder inside the container, so both always see the same files.",
        },
        {
            "q": "An app container and a Postgres container share a user-defined network. Which address should the app use for the database?",
            "options": [
                "localhost:5432",
                "the Postgres container's name, port 5432",
                "the IP from docker inspect, hard-coded",
                "host.docker.internal:5432",
            ],
            "answer": 1,
            "why": "Docker's DNS on the network resolves container names, and the IP may change on restart; localhost would be the app container itself.",
        },
        {
            "q": "A CI job runs `docker run -d -v /cache myjob` hundreds of times a day and later removes each container with `docker rm -f`. Why does the runner's disk fill up?",
            "options": [
                "docker rm -f also deletes the image each time",
                "The /cache folder is stored in the image",
                "tmpfs mounts never free their memory",
                "Each run leaves an anonymous volume behind",
            ],
            "answer": 3,
            "why": "`-v /cache` without a name creates an anonymous volume, and `docker rm` keeps it unless you add -v or start the container with --rm.",
        },
    ],
    "interview": [
        {
            "q": "When would you use a volume, a bind mount or a tmpfs mount?",
            "a": (
                "I use a named volume for data the app owns, such as database files: Docker manages it and it outlives the container. "
                "I use a bind mount when I and the container both need the files, such as source code during development. "
                "I use tmpfs for scratch files or secrets that should never touch a disk. "
                "In production, bind mounts tie a container to one machine's folders, so they are rare there."
            ),
        },
        {
            "q": "Why should containers use a user-defined network instead of the default bridge?",
            "a": (
                "A user-defined network gives every container Docker's embedded DNS server, so containers find each other by name instead of by changing IP addresses. "
                "It also isolates the app, because containers on other networks cannot reach it. "
                "You can connect and disconnect running containers too. "
                "The default bridge has none of that, and every container started without --network shares it."
            ),
        },
    ],
    "deeper": {
        "minutes": 12,
        "body": V1D07["deeper"]["body"]
        .replace("set up the worked example again up to step 5", "set up the hands-on task again up to the step where you replace Redis")
        .replace("In step 4 you used `docker stop`.", "In the task you used `docker stop`.")
        .replace("Start a fresh Redis on the same volume, as in step 5,", "Start a fresh Redis on the same volume")
        .replace("That is the Day 3 lesson about signals", "That is the Day 6 lesson about signals")
        .replace("The count survived the Redis swap", "In the hands-on task, the count survived the Redis swap"),
    },
    "sources": src("storage", "volumes", "bridge", "network"),
}
