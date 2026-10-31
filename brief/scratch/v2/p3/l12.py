from cap import ttymap
from common import cap, join, lines, ref, src, step

C = lambda k: cap("d12", k)

MULTI = ttymap(C("multi_build_raw"), {"localhost:18510": "localhost:5001", "docker:default": "docker:desktop-linux"})
MULTI_STEPS = "\n".join(
    ["$ docker buildx build --platform linux/amd64,linux/arm64 -t localhost:5001/hello:multi --push multi"]
    + [l for l in MULTI.split("\n") if any(s in l for s in ("[+] Building", "2/2] COPY", "exporting manifest", "exporting config", "exporting attestation", "pushing manifest"))]
)
INSPECT = lines(C("multi_inspect"), slice(0, 13))

SVG = (
    '<svg viewBox="0 0 560 246" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="A tag points to an image index, which points to one manifest per CPU type; a manifest lists a config and read-only layers; a running container adds one writable layer on top">'
    '<rect class="bx" x="8" y="12" width="200" height="38" rx="10"/><text class="t" x="108" y="36" font-size="13" text-anchor="middle">tag: nginx:latest</text>'
    '<line class="ln" x1="108" y1="50" x2="108" y2="70" marker-end="url(#ar)"/>'
    '<rect class="bxp" x="8" y="74" width="200" height="38" rx="10"/><text class="tk" x="108" y="98" font-size="13" text-anchor="middle">image index</text>'
    '<line class="ln" x1="108" y1="112" x2="108" y2="132" marker-end="url(#ar)"/><text class="ts" x="118" y="126" font-size="11" text-anchor="start">pick arm64</text>'
    '<rect class="bxp" x="8" y="136" width="200" height="38" rx="10"/><text class="tk" x="108" y="160" font-size="13" text-anchor="middle">manifest</text>'
    '<line class="ln" x1="108" y1="174" x2="108" y2="194" marker-end="url(#ar)"/>'
    '<rect class="bx" x="8" y="198" width="200" height="38" rx="10"/><text class="t" x="108" y="222" font-size="13" text-anchor="middle">config + layers</text>'
    '<line class="ln" x1="208" y1="217" x2="296" y2="190" marker-end="url(#ar)"/>'
    '<rect class="bxo" x="300" y="12" width="240" height="38" rx="10"/><text class="tk" x="420" y="36" font-size="13" text-anchor="middle">container layer (writable)</text>'
    '<rect class="bxt" x="300" y="62" width="240" height="38" rx="10"/><text class="tk" x="420" y="86" font-size="13" text-anchor="middle">layer: COPY app.py</text>'
    '<rect class="bxt" x="300" y="112" width="240" height="38" rx="10"/><text class="tk" x="420" y="136" font-size="13" text-anchor="middle">layer: RUN pip install</text>'
    '<rect class="bxg" x="300" y="162" width="240" height="38" rx="10"/><text class="tk" x="420" y="186" font-size="13" text-anchor="middle">layers: base image</text>'
    '<text class="ts" x="420" y="224" font-size="11" text-anchor="middle">read-only, shared by images</text>'
    "</svg>"
)

LESSON = {
    "id": "d12",
    "title": "Images, layers and registries",
    "minutes": 45,
    "goal": "By the end you can explain what an image is made of, inspect its layers with docker history and dive, and pull, tag and push images by tag and by digest.",
    "guess": {
        "q": "A Dockerfile has `RUN curl -o /big.bin ...` (a 50 MB download), then `RUN rm /big.bin`. How big is the image compared with the same image without the download?",
        "options": [
            "The same size, because the file is gone",
            "Smaller, because rm also cleans the cache",
            "It depends on whether you run docker image prune",
            "About 50 MB bigger, even though the file is deleted",
        ],
        "answer": 3,
        "why": "Each RUN adds a read-only layer. The rm only adds a marker that hides the file, while the 50 MB stay in the earlier layer and ship with the image.",
    },
    "terms": [
        {"term": "Layer", "plain": "A read-only set of file changes (added, changed or deleted files) that stacks on the layers below it."},
        {"term": "Image config", "plain": "A JSON file in an image with its settings: default command, environment variables, user and the list of layers."},
        {"term": "Manifest", "plain": "A JSON file that lists an image's config and layers by their digests."},
        {"term": "Digest", "plain": "A sha256 hash of some content, such as a layer or a manifest; the same content always has the same digest."},
        {"term": "Copy-on-write", "plain": "The rule that a file from the image is copied up into the container's own layer the first time it changes."},
        {"term": "Image index", "plain": "A list of manifests, one per CPU type, behind one image name; also called a manifest list."},
        {"term": "Registry", "plain": "A server that stores images and hands them out, such as Docker Hub or ghcr.io."},
        {"term": "Tag", "plain": "A movable, human-friendly label for an image, such as 1.0.0 or latest."},
    ],
    "sections": [
        {
            "h": "What is inside an image",
            "body": (
                "When you pull an image it looks like one thing. Inside, it is a small bundle of parts:\n\n"
                "- Layers: each layer is an archive of file changes compared with the layer below. Files can be added, changed or deleted.\n"
                "- A config: a JSON file with the image's settings, such as the default command, environment variables, working folder and user. It also lists the layers in order.\n"
                "- A manifest: a JSON file that points to the config and to every layer by their digest, which the next section explains.\n\n"
                "Dockerfile instructions that change files, such as `RUN` and `COPY`, each create a layer. "
                "Instructions that only change settings, such as `CMD`, `ENV` and `EXPOSE`, only edit the config. "
                "That is why `docker history` lists them with a size of 0B.\n\n"
                "Try it on the base image you will use on Day 13. "
                "The command `docker image inspect python:3.14-slim --format '{{json .RootFS.Layers}}'` printed four layer digests on the day we checked. "
                "Then `docker history python:3.14-slim` shows which instruction made each one: 87.7 MB of Debian files at the bottom, 42.1 MB for the Python build, and two small layers.\n\n"
                "If you know git, the picture is familiar. Layers are like immutable snapshots of changes, and the manifest is like a commit that points at them."
            ),
            "refs": ref("c_layers", "ref_history", "images_deep"),
        },
        {
            "h": "Layers are named by their content",
            "body": (
                "A digest is a sha256 hash of some bytes, written as `sha256:` followed by 64 hexadecimal characters. "
                "Docker names every layer, config and manifest by its digest. This is called content addressing: the name comes from the content itself. Three things follow:\n\n"
                "- The same content gets the same name on every machine.\n"
                "- Change one byte, and the name changes.\n"
                "- Docker can check a download by hashing it again and comparing.\n\n"
                "The big win is sharing. Two images built `FROM python:3.14-slim` start with the same four layers, so your disk and the registry store them once. "
                "We built two such images, each adding one small file. `docker system df -v` listed each at 178 MB, but only 16.84 kB of each was unique. The other 178.3 MB were shared.\n\n"
                "Pushes and pulls skip shared layers too. In the worked example you will see `Already exists` and `Layer already exists` instead of a download.\n\n"
                "This is also why the order of a Dockerfile matters, as Day 13 shows. Docker reuses a layer only when everything below it is identical."
            ),
            "refs": ref("drivers"),
        },
        {
            "h": "The container layer and copy-on-write",
            "body": (
                "Image layers are read-only. When Docker starts a container, it adds one thin writable layer on top. "
                "A union filesystem then shows all the layers as one folder tree. On Linux that is OverlayFS: it stacks the image layers under the container layer and shows you the merged view.\n\n"
                "Reads and writes follow four rules:\n\n"
                "1. A read looks from the top layer down and uses the first copy of the file it finds.\n"
                "2. The first write to a file from the image copies the whole file up into the container layer. Later writes change that copy. This is **copy-on-write**.\n"
                "3. A new file goes straight into the container layer.\n"
                "4. A delete adds a small marker called a whiteout, which hides the file below. The bytes below stay where they are.\n\n"
                "`docker diff` lists what a container changed, with A for added, C for changed and D for deleted. "
                "We edited `nginx.conf`, created a file in `/tmp` and deleted `50x.html` in an nginx container. The diff showed exactly those, plus files nginx wrote at startup, such as `/run/nginx.pid`. "
                "Then `docker ps --size` reported that container layer as `106kB (virtual 177MB)`: 106 kB of its own on top of 177 MB of shared image.\n\n"
                "Copy-on-write has a cost. Copying a big file up is slow, and the layer dies with the container. That is why databases keep their files in volumes (Day 14)."
            ),
            "refs": ref("overlay", "ref_diff"),
        },
        {
            "h": "Deleting a file never shrinks an image",
            "body": (
                "Here is the trap that follows from layers. One `RUN` step creates a 50 MB file, and the next `RUN` step deletes it. "
                "The second layer only adds a whiteout. The 50 MB still sit in the first layer and ship with every pull.\n\n"
                "We built both versions on `alpine:3.22`. The image that created and deleted the file in two steps had a content size of 53.8 MB. "
                "The one that did both in a single `RUN` had 3.8 MB. There are two fixes:\n\n"
                "- Create and clean up in the same `RUN`, joined with `&&`.\n"
                "- Use a multi-stage build (Day 16) and copy only the results into a fresh stage.\n\n"
                "[dive](https://github.com/wagoodman/dive) makes waste visible. It walks an image layer by layer, shows what each layer adds, and estimates wasted space. "
                "Install it with `brew install dive`. With `CI=true` it prints a pass or fail report, and for the two-step image it said: efficiency 14%, 50 MB wasted in `/big.bin`, FAIL.\n\n"
                "`docker image ls` shows two sizes on current Docker. CONTENT SIZE is the compressed data, close to what you download and push. "
                "DISK USAGE also counts the unpacked copy on disk, so it is bigger.\n\n"
                "Size is worth watching for three reasons:\n\n"
                "- Every deploy and every CI run pulls the image.\n"
                "- It takes disk space on every machine that runs it.\n"
                "- Every extra package is one more thing to patch."
            ),
            "refs": ref("dive", "ref_imagels"),
        },
        {
            "h": "Registries, repositories, tags and digests",
            "body": (
                "A registry stores images and hands them out. You will meet:\n\n"
                "- Docker Hub (`docker.io`), the default\n"
                "- GitHub Container Registry (`ghcr.io`), next to your code on GitHub\n"
                "- cloud registries: Amazon ECR, Azure Container Registry and Google Artifact Registry\n"
                "- a registry you run yourself, such as the `registry:3` image in the worked example\n\n"
                "A full image name can have five parts, as in `ghcr.io/ana/hello-devops:1.0.0@sha256:...`: the registry, a namespace (user or organisation), the repository, a tag and a digest. "
                "Leave parts out and Docker fills in defaults, so `nginx` means `docker.io/library/nginx:latest`. The `library` namespace holds Docker Official Images.\n\n"
                "A tag is a movable label. Anyone who can push can point `1.0` at a different image tomorrow, and the worked example does exactly that. "
                "A digest is the hash of the manifest, so it always means one exact image. `docker pull nginx@sha256:...` gives you the same bytes every time. "
                "Teams pin digests in deploy files so the image they tested is the image that runs. Think of a tag as a git branch name and a digest as a commit SHA.\n\n"
                "Publishing takes three commands: `docker login` to the registry, `docker tag` to give the image its full name, and `docker push`. "
                "The push prints the digest on its last line. Day 16 pushes hello-devops to ghcr.io.\n\n"
                "Docker Hub limits pulls per 6 hours: 100 without signing in, counted per IP address, and 200 when you are signed in."
            ),
            "refs": ref("c_registry", "pulls"),
        },
        {
            "h": "One name, many CPUs: the image index",
            "body": (
                "A multi-platform image adds one more JSON file on top: an image index, also called a manifest list. "
                "It lists one manifest per platform, meaning an operating system plus a CPU type. "
                "When you pull, the registry sends the index first, and Docker picks the manifest for your machine. On your Mac that is `linux/arm64`.\n\n"
                "`docker buildx imagetools inspect python:3.14-slim` reads the index straight from the registry without pulling anything. "
                "On the day we checked, it listed eight platforms, among them `linux/amd64`, `linux/arm64/v8`, `linux/arm/v7` and `linux/s390x`. "
                "Next to each platform sat an entry marked `unknown/unknown`. Those are attestations: records of how the image was built, which Docker's builder adds by default. Day 52 uses them.\n\n"
                "If your CPU is missing from the index, the image runs only through emulation, or not at all, and fails with `exec format error`. "
                "The worked example builds a small two-platform image and shows its index.\n\n"
                "Docker Engine 29 also changed where images live. Fresh installs and Docker Desktop use the containerd image store, which can keep several platforms of one image on your machine. "
                "`docker image ls --tree` shows them as a tree under each name."
            ),
            "refs": ref("multiplat", "imagetools", "containerd"),
        },
        {
            "h": "Official images and Docker Hardened Images",
            "body": (
                "Every image you build starts from someone else's image, so pick bases you can trust. On Docker Hub, look for these labels:\n\n"
                "- Docker Official Images, such as `python`, `nginx` and `redis`, in the `library` namespace.\n"
                "- Verified Publisher images, which software vendors publish themselves.\n\n"
                "Docker Hardened Images (DHI) are a newer option. Docker sold them from May 2025 and made the catalog free and open source, under the Apache 2.0 licence, in December 2025. From Docker's docs:\n\n"
                "- They come from `dhi.io`. You run `docker login dhi.io` with a free Docker account, then pull images such as `dhi.io/python:3.13`.\n"
                "- Runtime images are distroless: no shell and no package manager, and they run as a non-root user by default.\n"
                "- `-dev` variants add a shell and package manager for build stages.\n"
                "- Every image comes with signed records of what is inside it and how it was built.\n\n"
                "Docker says this approach cuts the attack surface by up to 95%. That figure is Docker's own claim, not an independent measurement. "
                "Day 16 shows how a hardened base would change the hello-devops Dockerfile."
            ),
            "refs": ref("dhi", "dhi_start"),
        },
    ],
    "analogy": (
        "Think of an overhead projector with a stack of transparent sheets. Each sheet adds some drawings, and the screen shows all of them at once: those are the layers. "
        "A container adds one blank sheet on top for its own notes. "
        "To erase a line drawn on a lower sheet, you can only stick a white patch over it on a higher sheet. "
        "The line is hidden but still there, and the stack is no lighter. "
        "The picture breaks on sharing: a real sheet sits in one stack at a time, while Docker uses the same layer in many images at once."
    ),
    "diagram": SVG,
    "diagram_caption": "A tag points to an index, the index to one manifest per CPU, and the manifest to read-only layers; a container adds a writable layer.",
    "worked": {
        "title": "Watch a tag move while a digest stays put",
        "steps": [
            step("Run your own registry on your Mac. Use port 5001, because macOS often uses port 5000 for AirPlay Receiver. If you do not have `registry:3` yet, Docker pulls it first; the last line is the container ID.",
                 C("reg_run")),
            step("Make two tiny Dockerfiles in `~/code/docker-play` from the Files section: `v1` prints one message and `v2` another. Build v1 with its full registry name, push it, and run it. The last line of the push is the digest.",
                 join(C("v1_build"), C("v1_push"), C("v1_run"))),
            step("Now build v2 and push it under the same tag. The base layer is already in the registry, so the push skips it. The tag `1.0` now points to a new digest.",
                 join(C("v2_build"), C("v2_push"))),
            step("Delete your local copy of the tag, then run by digest and by tag. The old digest still gives you version one. The tag gives you whatever it points to today.",
                 join(C("rmi"), C("by_digest"), C("by_tag"))),
            step("`docker images --digests` shows both images side by side. The old one has lost its tag, shown as `<none>`, but its digest still names it.",
                 C("digests")),
            step("Build one image for two CPU types and push it. There are no RUN steps here, so no emulation is needed. The builder writes one manifest and one config per platform, then a manifest list that ties them together. (Output trimmed to those lines.)",
                 MULTI_STEPS),
            step("Read the index from the registry. It lists one manifest per platform. Below these two (cut here) come two more entries marked `unknown/unknown`, one attestation per platform. When you are done, remove the registry with `docker rm -fv registry`; the `-v` also deletes its storage.",
                 INSPECT),
        ],
    },
    "code": [
        {
            "lang": "dockerfile",
            "title": "~/code/docker-play/v1/Dockerfile (v2 is the same with \"two\")",
            "src": 'FROM alpine:3.22\nCMD ["echo", "hello from version one"]',
            "run": "cd ~/code/docker-play && docker build -t localhost:5001/hello:1.0 v1",
        },
        {
            "lang": "dockerfile",
            "title": "~/code/docker-play/multi/Dockerfile (next to a hello.txt file)",
            "src": 'FROM alpine:3.22\nCOPY hello.txt /hello.txt\nCMD ["cat", "/hello.txt"]',
            "run": "cd ~/code/docker-play && docker buildx build --platform linux/amd64,linux/arm64 -t localhost:5001/hello:multi --push multi",
        },
        {
            "lang": "dockerfile",
            "title": "~/code/docker-play/bloat/Dockerfile (for the hands-on task)",
            "src": (
                "FROM alpine:3.22\n"
                "# Download a 50 MB file in one step...\n"
                "RUN head -c 50000000 /dev/urandom > /big.bin\n"
                "# ...and delete it in the next. Does the image shrink?\n"
                "RUN rm /big.bin"
            ),
            "run": "cd ~/code/docker-play && docker build -t bloat:1.0 bloat && docker history bloat:1.0",
        },
    ],
    "commands": [
        {"cmd": "docker history python:3.14-slim", "what": "List an image's layers, newest first, with the instruction and size of each."},
        {"cmd": "docker image inspect python:3.14-slim --format '{{json .RootFS.Layers}}'", "what": "Print the digests of an image's layers."},
        {"cmd": "docker diff web", "what": "Show files a container added (A), changed (C) or deleted (D) in its writable layer."},
        {"cmd": "docker ps --size", "what": "Show each container's writable layer size and the image size below it."},
        {"cmd": "docker system df -v", "what": "Show disk use per image, including the shared and unique parts."},
        {"cmd": "dive bloat:1.0", "what": "Browse an image layer by layer and find wasted space (CI=true for a pass or fail report)."},
        {"cmd": "docker image ls --tree", "what": "List images with the platforms stored under each name."},
        {"cmd": "docker images --digests", "what": "List images with their digests."},
        {"cmd": "docker pull nginx@sha256:<digest>", "what": "Pull one exact image by digest."},
        {"cmd": "docker buildx imagetools inspect python:3.14-slim", "what": "Read an image index from the registry without pulling it; add --raw for the JSON."},
        {"cmd": "docker tag hello:1.0 localhost:5001/hello:1.0", "what": "Give an image a second name, here its full registry name; nothing is copied."},
        {"cmd": "docker push localhost:5001/hello:1.0", "what": "Upload an image to its registry; the last line shows the digest."},
        {"cmd": "docker login ghcr.io", "what": "Sign in to a registry before you push to it."},
        {"cmd": "docker run -d --name registry -p 127.0.0.1:5001:5000 registry:3", "what": "Run a private registry on your Mac for practice."},
    ],
    "mistake": (
        "The classic mistake is trying to slim an image by deleting files in a later step, such as `RUN rm -rf /var/lib/apt/lists/*` on its own line. "
        "The files are hidden but still stored in the earlier layer, so the image stays just as big. "
        "Clean up in the same `RUN` that created the files, or build in one stage and copy only the results into a fresh one."
    ),
    "real_world": (
        "PayFlow's deploy files never say `payments-api:latest`. CI pushes each build with a version tag, and the deploy file pins the digest that CI printed. What ran in tests is then byte for byte what runs in production. "
        "A weekly job rebuilds base images, and a pull request updates the pinned digests, so nobody gets a new base by surprise."
    ),
    "task": {
        "title": "Find the waste in an image, then remove it",
        "steps": [
            "Create `~/code/docker-play/bloat/Dockerfile` from the Files section. Build it as `bloat:1.0` and read `docker history bloat:1.0`. Which row holds the 50 MB?",
            "Install dive with `brew install dive`. Run `CI=true dive bloat:1.0` and note the efficiency and wasted bytes.",
            "Run `dive bloat:1.0` without CI and browse the layers. Find `/big.bin` in one layer and its removal in the next.",
            "Write a second Dockerfile, `lean`, that creates and deletes the file in a single RUN. Build it as `lean:1.0` and compare both images with `docker image ls`.",
            "Start an nginx container, change one file, add one and delete one with `docker exec`, then read `docker diff`.",
            "Count the layers of `python:3.14-slim` with `docker image inspect`. Build any small image FROM it and check that its first layer digests match.",
            "Use `docker buildx imagetools inspect redis:8-alpine` to find the digest of the arm64 manifest. Pull that digest and run `redis-server --version` from it.",
            "Clean up the images and containers you made.",
        ],
        "hints": [
            "In dive, Tab switches between the layer list and the file tree, and Ctrl+U shows only unmodified files.",
            "`&&` runs the second command only if the first succeeds, so one RUN can create, use and delete a file.",
            "The `--raw` flag of imagetools prints the index JSON; `jq` can pick out `.manifests[]`.",
        ],
        "done_when": "You are done when `CI=true dive lean:1.0` says PASS and `docker image ls` shows the lean image at under 5 MB of content.",
    },
    "explain_back": {
        "prompt": "Explain in 3 to 4 sentences what happens when you pull `nginx` on your Mac and then start two containers from it. Mention the index, layers, digests and the writable layer.",
        "answer": (
            "Docker reads `nginx` as `docker.io/library/nginx:latest` and asks Docker Hub for that tag, which points to an image index. "
            "From the index it picks the manifest for linux/arm64, then downloads the config and every layer it does not already have, checking each by its digest. "
            "Both containers share those read-only layers on disk, and each gets its own thin writable layer on top. "
            "Anything a container writes goes into its own layer through copy-on-write, so the two never see each other's changes and the image never changes."
        ),
    },
    "recap": [
        "An image is read-only layers plus a config, tied together by a manifest.",
        "Everything is named by a sha256 digest of its content, so identical layers are stored and sent once.",
        "A container adds one writable layer; the first write to an image file copies it up.",
        "Deleting a file in a later layer hides it but never shrinks the image.",
        "Tags move and digests do not; pin a digest when you need the exact same image.",
        "An image index holds one manifest per CPU type, and Docker picks yours when it pulls.",
    ],
    "check": [
        {
            "q": "Two teammates build different services, both `FROM python:3.14-slim`, and push them to the same registry. What does the registry store for the base layers?",
            "options": [
                "One copy, shared by both images",
                "Two copies, one per repository",
                "Nothing; registries store only your own layers",
                "A compressed diff between the two images",
            ],
            "answer": 0,
            "why": "Layers are named by their content digest, so the identical base layers are stored once and only referenced twice.",
        },
        {
            "q": "A deploy file says `image: shop:2.3`. Last night someone pushed a broken build with the same tag. What would have protected the deploy?",
            "options": [
                "Using the tag latest instead",
                "Running docker image prune before deploying",
                "Pinning the image by its digest",
                "Adding a second tag such as stable",
            ],
            "answer": 2,
            "why": "A tag can be moved to any image, while a digest names one exact manifest and cannot change.",
        },
        {
            "q": "A database runs in a container without a volume, and its 2 GB data file changes all day. What does copy-on-write mean for it?",
            "options": [
                "Docker compresses the file on each write",
                "The file is copied up into the container layer and lost with the container",
                "Writes go back into the image, which grows each day",
                "Docker refuses to write to files that came from the image",
            ],
            "answer": 1,
            "why": "The first write copies the whole file into the container's writable layer, which is slow for big files and is deleted along with the container.",
        },
    ],
    "interview": [
        {
            "q": "What is an image layer, and why do layers matter?",
            "a": (
                "A layer is a read-only set of file changes, usually made by one Dockerfile instruction, and named by the sha256 digest of its content. "
                "An image is a stack of layers plus a config, listed in a manifest. "
                "Because layers are content-addressed, identical layers are stored once and skipped on push and pull, which saves disk and time. "
                "They also explain two common surprises: deleting a file in a later layer does not shrink the image, and a change in one layer forces every later layer to rebuild."
            ),
        },
        {
            "q": "What is the difference between a tag and a digest?",
            "a": (
                "A tag is a human-friendly name such as `1.0.0` or `latest`, and anyone with push rights can move it to a different image. "
                "A digest is the sha256 hash of the image's manifest, so it always means exactly the same content. "
                "Deploying by digest makes deploys repeatable and protects you from a tag that changed underneath you. "
                "Teams often keep both: a readable tag for people and a digest in deploy files."
            ),
        },
        {
            "q": "How can one image name work on both an Apple Silicon laptop and an Intel server?",
            "a": (
                "The name points to an image index, also called a manifest list, rather than a single manifest. "
                "The index has one manifest per platform, such as linux/amd64 and linux/arm64, each with its own config and layers. "
                "When a machine pulls, Docker reads the index and downloads only the variant for its own CPU. "
                "You build such an image with `docker buildx build --platform linux/amd64,linux/arm64 --push`."
            ),
        },
    ],
    "deeper": {
        "minutes": 15,
        "body": (
            "A registry is just a web server with a small HTTP API, so you can read an image by hand with curl. Day 9's HTTP skills apply directly. "
            "Start the registry from the worked example again and push the two-platform `hello:multi` image to it.\n\n"
            "First ask for the index. The `Accept` header tells the registry which JSON format you want:\n\n"
            "`curl -s -H 'Accept: application/vnd.oci.image.index.v1+json' localhost:5001/v2/hello/manifests/multi | jq '.manifests[].platform.architecture'`\n\n"
            "When we did this, the answer listed `amd64`, `arm64` and two `unknown` entries, which are the attestations. "
            "Each entry also has a `digest`. Copy the arm64 digest and ask for that manifest, this time with the header `Accept: application/vnd.oci.image.manifest.v1+json`, at `localhost:5001/v2/hello/manifests/<digest>`. "
            "The manifest names one config digest and two layer digests: the Alpine base and the layer that holds `hello.txt`.\n\n"
            "Finally fetch the config itself from `localhost:5001/v2/hello/blobs/<config digest>` and pipe it into `jq '{architecture, os}'`. "
            "Ours said `\"architecture\": \"arm64\"` and `\"os\": \"linux\"`, with the command `cat /hello.txt`. "
            "Every object came from a URL that ends in its own digest. That is content addressing in practice: the client can hash what it got and check it against the name it asked for.\n\n"
            "Two more details are worth knowing on current Docker.\n\n"
            "- With the containerd image store, an image's ID is the digest of its index. That is why `docker build` output ends with `exporting manifest list sha256:...` and `docker history` shows the same first 12 characters.\n"
            "- `docker image ls` on Engine 29 hides untagged images and collapses platforms; add `--all` or `--tree` to see everything.\n\n"
            "The [OverlayFS driver page](https://docs.docker.com/engine/storage/drivers/overlayfs-driver/) shows how the layers become one folder tree on disk."
        ),
    },
    "sources": src("c_layers", "overlay", "multiplat", "dhi"),
}
