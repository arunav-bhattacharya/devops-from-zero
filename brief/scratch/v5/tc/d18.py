"""Fifth pass (book voice) for d18."""
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from common import load, apply, save

path, P, L, OL = load(5, "d18")
new = {}

new["goal"] = r"""By the end you can explain what an image is made of, inspect its layers with docker history and dive, and pull, tag and push images by tag and by digest."""

new["opening"] = r"""Picture packing a stacked lunchbox, the kind with several tiers that click together. You put a heavy jar of soup in the bottom tier. Then you change your mind, so you add a tier on top with a sticker that says "no soup". Your friend lifts the box and frowns: it is just as heavy as before.

That sounds silly with soup, yet software images work exactly this way, and smart people get caught. Deleting a file feels like removing it. Last time, you ran containers from images and treated each image as one sealed box. In this lesson, we'll open the box. You'll see its tiers (layers), the fingerprints that name every part, and why a deleted file still costs space. You'll also see how a name such as `nginx` can mean one image today and another tomorrow.

Before we start, make a guess, and keep it in mind."""

new["guess_q"] = r"""A Dockerfile is the recipe that builds an image, one step per line. One step downloads a 50 MB file with `RUN curl -o /big.bin ...`, and the next step deletes it with `RUN rm /big.bin`. How big is the image compared with the same image without the download?"""
new["guess_why"] = r"""Each RUN adds a read-only layer. The rm only adds a marker that hides the file, while the 50 MB stay in the earlier layer and ship with the image: the soup jar under the sticker."""

new["terms"] = {
    "Layer": "A read-only set of file changes (added, changed or deleted files) that stacks on the layers below it.",
    "Image config": "A small settings file inside an image: default command, environment variables, user and the list of layers.",
    "Manifest": "A small file that lists an image's config and layers by their digests.",
    "Digest": "A sha256 fingerprint of some content, such as a layer or a manifest; the same content always has the same digest.",
    "Copy-on-write": "The rule that a file from the image is copied up into the container's own layer the first time it changes.",
    "Image index": "A list of manifests, one per CPU type, behind one image name; also called a manifest list.",
    "Registry": "A server that stores images and hands them out, such as Docker Hub or ghcr.io.",
    "Tag": "A movable, human-friendly label for an image, such as 1.0.0 or latest.",
}

S = []
S.append(("Opening the sealed box: what an image holds", r"""An image holds a whole small Linux system: `python:3.14-slim` unpacks to about 135 MB of Debian and Python files. Debian is one of the popular flavours of Linux. If all of that were one big archive (a single packed file), each change to your app would mean shipping all of it again. Ten Python images would also store Python ten times. So an image looks like one thing when you pull it, but inside it is a small bundle of parts:

- Layers: each layer is an archive of file changes compared with the layer below. Files can be added, changed or deleted. These are the tiers of the lunchbox.
- A config: a JSON file with the image's settings, such as the default command, environment variables, working folder and user. It also lists the layers in order.
- A manifest: a JSON file that points to the config and to every layer by their digest, which the next section explains.

Images are built from a Dockerfile, a text file of build steps that Day 19 covers in full. Two kinds of steps matter today. Steps that change files each create a layer: `RUN` runs a shell command during the build, and `COPY` copies files in from your laptop. Steps that only change settings, such as `CMD` (the default command), `ENV` (a variable) and `EXPOSE` (a note about a port), only edit the config. In `docker history` they show a size of 0B.

Try it on the base image you will use on Day 19. The command `docker image inspect python:3.14-slim --format '{{json .RootFS.Layers}}'` printed four layer digests on the day we checked. Then `docker history python:3.14-slim` shows which step made each one: 87.7 MB of Debian files at the bottom, 42.1 MB for the Python build, and two small layers.

The manifest works much like a git commit from Day 8: it names its parts by their fingerprints, so it cannot point at the wrong ones. One difference: a layer holds only the changes its step made, while a git commit points at a full snapshot.

Those fingerprints do more work than you might guess."""))

S.append(("Every part is named by its fingerprint", r"""A hash is a short fingerprint computed from a pile of bytes. A digest is a sha256 hash, one common kind, written as `sha256:` followed by 64 hexadecimal characters (the digits 0 to 9 and the letters a to f). Docker names every layer, config and manifest by its digest. This is called content addressing: the name comes from the content itself. Three things follow:

- The same content gets the same name on every machine.
- Change one byte, and the name changes.
- Docker can check a download by hashing it again and comparing.

Content addressing also lets images share layers. Real lunchboxes can't share a tier, but images can. Two images built `FROM python:3.14-slim` start with the same four layers, so your disk and the registry store those layers once. We built two such images, each adding one small file. `docker system df -v` listed each at about 178 MB, but only 16.84 kB of each was unique. The other 178.3 MB were shared.

Pushes and pulls skip shared layers too. In the worked example you will see `Already exists` and `Layer already exists` instead of a download.

The same rule makes the order of a Dockerfile matter, as Day 19 shows: Docker reuses a layer only when everything below it is identical.

The layers so far are all read-only. Yet a running container writes files all the time. Where do they go?"""))

S.append(("The container's own tier: copy-on-write", r"""Image layers are read-only. When Docker starts a container, it adds one thin writable layer on top, a fresh tier that belongs to this one container. A union filesystem then shows all the layers as one folder tree. On Linux that is OverlayFS: it stacks the image layers under the container layer and shows you the merged view. That merged view is the `/` that the container's process sees, as on Day 17.

Reads and writes follow four rules:

1. A read looks from the top layer down and uses the first copy of the file it finds.
2. The first write to a file from the image copies the whole file up into the container layer. Later writes change that copy. This is copy-on-write.
3. A new file goes straight into the container layer.
4. A delete adds a small marker called a whiteout, which hides the file below. The bytes below stay where they are: the "no soup" sticker.

`docker diff` lists what a container changed, with A for added, C for changed and D for deleted. We edited `nginx.conf`, created a file in `/tmp` and deleted `50x.html` in an nginx container. The diff showed those three changes, plus files nginx wrote at startup, such as `/run/nginx.pid`. Then `docker ps --size` reported that container layer as `106kB (virtual 177MB)`: 106 kB of its own on top of 177 MB of shared image.

Copy-on-write has a cost. Copying a big file up is slow, and the layer dies with the container, so databases keep their files in volumes instead (Day 20).

Rule 4 is the soup jar from the opening. It deserves a closer look, because it costs real megabytes."""))

S.append(("Deleting a file never makes the box lighter", r"""Suppose one `RUN` step creates a 50 MB file, and the next `RUN` step deletes it. The second layer only adds a whiteout. The 50 MB still sit in the first layer and ship with every pull.

We built both versions on `alpine:3.22`. The image that created and deleted the file in two steps had a content size of 53.8 MB. The one that did both in a single `RUN` had 3.8 MB. That is about fourteen times bigger, for a file nobody can even see. There are two fixes:

- Create and clean up in the same `RUN`, joined with `&&`.
- Use a multi-stage build (Day 22) and copy only the results into a fresh stage.

**A delete in a later step only hides the file. Clean up in the same step.**

[dive](https://github.com/wagoodman/dive) makes waste visible. It walks an image layer by layer, shows what each layer adds, and estimates wasted space. Install it with `brew install dive`. With `CI=true` it prints a pass or fail report, and for the two-step image it said: efficiency 14%, 50 MB wasted in `/big.bin`, FAIL.

`docker image ls` shows two sizes on current Docker. CONTENT SIZE is the compressed data, close to what you download and push. DISK USAGE also counts the unpacked copy on disk, so it is bigger.

Image size costs you in three places:

- Every deploy and every CI run pulls the image.
- It takes disk space on every machine that runs it.
- Every extra package is one more thing to patch.

So far we have looked at images on your own machine. Most of the time, though, they live somewhere else."""))

S.append(("Registries, tags and digests: the shop and its labels", r"""A registry stores images and hands them out, like a shop that stocks sealed lunchboxes. You will meet:

- Docker Hub (`docker.io`), the default
- GitHub Container Registry (`ghcr.io`), next to your code on GitHub
- cloud registries: Amazon ECR, Azure Container Registry and Google Artifact Registry
- a registry you run yourself, such as the `registry:3` image in the worked example

A full image name can have five parts, as in `ghcr.io/ana/hello-devops:1.0.0@sha256:...`: the registry, a namespace (user or organisation), the repository (one image's shelf), a tag and a digest. Leave parts out and Docker fills in defaults, so `nginx` means `docker.io/library/nginx:latest`. The `library` namespace holds Docker Official Images.

A tag is a movable label, a sticker on the shelf. Anyone who can push can point `1.0` at a different image tomorrow, and the worked example does just that.

An image's digest is the hash of its manifest, and that one hash pins every byte. The manifest lists the config and each layer by digest. Change one byte in a layer, and that layer's digest changes, so the manifest changes, and so does its digest. `docker pull nginx@sha256:...` gives you the same bytes every time. Teams pin digests in deploy files so the image they tested is the image that runs. A tag works like a git branch name from Day 8, a pointer that moves, and a digest like a commit SHA.

**Tags move and digests don't. Deploy the digest you tested.**

Publishing takes three commands: `docker login` to the registry, `docker tag` to give the image its full name, and `docker push`. The push prints the digest on its last line. Day 22 pushes hello-devops to ghcr.io.

Docker Hub limits pulls per 6 hours: 100 without signing in, counted per IP address (your internet address), and 200 when you are signed in.

One name, one image? Not quite. Your Mac and a cloud server can pull the same name and get different bytes."""))

S.append(("One name, many CPUs: the image index", r"""Remember from Day 17 that a program is built for one CPU type. A multi-platform image adds one more JSON file on top: an image index, also called a manifest list. It lists one manifest per platform, meaning an operating system plus a CPU type. When you pull, the registry sends the index first, and Docker picks the manifest for your machine. On your Mac that is `linux/arm64`.

`docker buildx imagetools inspect python:3.14-slim` reads the index straight from the registry without pulling anything. On the day we checked, it listed eight platforms, among them `linux/amd64`, `linux/arm64/v8`, `linux/arm/v7` and `linux/s390x`. Next to each platform sat an entry marked `unknown/unknown`. Those are attestations: records of how the image was built, which Docker's builder adds by default. Day 63 uses them.

If your CPU is missing from the index, the image runs only through emulation, or not at all, and fails with `exec format error`. The worked example builds a small two-platform image and shows its index, so you can watch Docker write one manifest per platform and a list that ties them together.

Now you can read any image. The last question is which ones to trust."""))

S.append(("Choosing a base you can trust: official and hardened images", r"""You would not build a packed lunch on food from an unlabelled jar. Every image you build starts from someone else's image, and everything in that base ships inside yours, old packages with known bugs included. So pick bases you can trust. On Docker Hub, look for these labels:

- Docker Official Images, such as `python`, `nginx` and `redis`, in the `library` namespace.
- Verified Publisher images, which software vendors publish themselves.

Docker Hardened Images (DHI) are a newer option. Docker sold them from May 2025 and made the catalog free and open source, under the Apache 2.0 licence, in December 2025. From Docker's docs:

- They come from `dhi.io`. You run `docker login dhi.io` with a free Docker account, then pull images such as `dhi.io/python:3.13`.
- Runtime images are distroless: no shell and no package manager (the tool that installs software). They run as a non-root user by default, not as the all-powerful root account.
- `-dev` variants add a shell and package manager for build stages.
- Every image comes with signed records of what is inside it and how it was built.

Docker says this approach cuts the attack surface, the code an attacker could try to use, by up to 95%. That figure is Docker's own claim, not an independent measurement. Day 22 shows how a hardened base would change the hello-devops Dockerfile.

Today's limit is that every image you used was built by someone else. You can open them, weigh them and pin them, but not yet pack your own. Day 19 does exactly that."""))
new["sections"] = S

new["drop"] = ["analogy", "mistake"]
new["real_world"] = r"""A deploy file that says `payments-api:latest` can run a different build every time it pulls. So CI pushes each build with a version tag, and the deploy file pins the digest that CI printed. What ran in tests is then byte for byte what runs in production. A weekly job rebuilds base images, and a pull request (a proposed change that teammates review) updates the pinned digests, so nobody gets a new base by surprise."""

new["diagram_caption"] = "A tag points to an index, the index to one manifest per CPU, and the manifest to read-only layers; a container adds a writable layer on top."

new["worked"] = [
    r"""Run your own registry on your Mac. Use port 5001, because macOS often uses port 5000 for AirPlay Receiver. If you do not have `registry:3` yet, Docker pulls it first; the last line is the container ID.""",
    r"""Make two tiny Dockerfiles in `~/code/docker-play` from the Files section: `v1` prints one message and `v2` another. Build v1 with its full registry name, push it, and run it. The last line of the push is the digest.""",
    r"""Now build v2 and push it under the same tag. The base layer is already in the registry, so the push skips it. The tag `1.0` now points to a new digest: the shop moved the sticker.""",
    r"""Delete your local copy of the tag, then run by digest and by tag. The old digest still gives you version one. The tag gives you whatever it points to today.""",
    r"""`docker images --digests` shows both images side by side. The old one has lost its tag, shown as `<none>`, but its digest still names it.""",
    r"""Build one image for two CPU types and push it. There are no RUN steps here, so no emulation is needed. The builder writes one manifest and one config per platform, then a manifest list that ties them together. (Output trimmed to those lines.)""",
    r"""Read the index from the registry. It lists one manifest per platform. Below these two (cut here) come two more entries marked `unknown/unknown`, one attestation per platform. When you are done, remove the registry with `docker rm -fv registry`; the `-v` also deletes its storage.""",
]

new["task"] = {
    "steps": [
        r"""Create `~/code/docker-play/bloat/Dockerfile` from the Files section. Build it as `bloat:1.0` and read `docker history bloat:1.0`. Which row holds the 50 MB?""",
        r"""Install dive with `brew install dive`. Run `CI=true dive bloat:1.0` and note the efficiency and wasted bytes.""",
        r"""Run `dive bloat:1.0` without CI and browse the layers. Find `/big.bin` in one layer and its removal in the next.""",
        r"""Write a second Dockerfile, `lean`, that creates and deletes the file in a single RUN. Build it as `lean:1.0` and compare both images with `docker image ls`.""",
        r"""Start an nginx container, change one file, add one and delete one with `docker exec`, then read `docker diff`.""",
        r"""Count the layers of `python:3.14-slim` with `docker image inspect`. Build any small image FROM it and check that its first layer digests match.""",
        r"""Use `docker buildx imagetools inspect redis:8-alpine` to find the digest of the arm64 manifest. Pull that digest and run `redis-server --version` from it.""",
        r"""Clean up the images and containers you made.""",
    ],
    "hints": [
        r"""In dive, Tab switches between the layer list and the file tree, and Ctrl+U shows only unmodified files.""",
        r"""`&&` runs the second command only if the first succeeds, so one RUN can create, use and delete a file.""",
        r"""The `--raw` flag of imagetools prints the index JSON; `jq` can pick out `.manifests[]`.""",
    ],
    "done_when": r"""You are done when `CI=true dive lean:1.0` says PASS and `docker image ls` shows the lean image at under 5 MB of content.""",
}

new["explain_back"] = {
    "prompt": r"""Explain in 3 to 4 sentences what happens when you pull `nginx` on your Mac and then start two containers from it. Mention the index, layers, digests and the writable layer.""",
    "answer": r"""Docker reads `nginx` as `docker.io/library/nginx:latest` and asks Docker Hub for that tag, which points to an image index. From the index it picks the manifest for linux/arm64, then downloads the config and every layer it does not already have, checking each by its digest. Both containers share those read-only layers on disk, and each gets its own thin writable layer on top. Anything a container writes goes into its own layer through copy-on-write, so the two never see each other's changes and the image never changes.""",
}

new["recap"] = [
    "An image is read-only layers plus a config, tied together by a manifest.",
    "Everything is named by a sha256 digest of its content, so identical layers are stored and sent once.",
    "A container adds one writable layer; the first write to an image file copies it up.",
    "Deleting a file in a later layer hides it but never shrinks the image.",
    "Tags move and digests do not; pin a digest when you need the exact same image.",
    "An image index holds one manifest per CPU type; so far, though, every image came from someone else.",
]

new["check"] = [
    (r"""Two teammates build different services, both `FROM python:3.14-slim`, and push them to the same registry. What does the registry store for the base layers?""",
     r"""Layers are named by their content digest, so the identical base layers are stored once and only referenced twice."""),
    (r"""A deploy file says `image: shop:2.3`. Last night someone pushed a broken build with the same tag. What would have protected the deploy?""",
     r"""A tag can be moved to any image, while a digest names one exact manifest and cannot change."""),
    (r"""A database runs in a container without a volume, and its 2 GB data file changes all day. What does copy-on-write mean for it?""",
     r"""The first write copies the whole file into the container's writable layer, which is slow for big files and is deleted along with the container."""),
]

new["interview"] = [
    (r"""What is an image layer, and why do layers matter?""",
     r"""A layer is a read-only set of file changes, usually made by one Dockerfile instruction, and named by the sha256 digest of its content. An image is a stack of layers plus a config, listed in a manifest. Because layers are content-addressed, identical layers are stored once and skipped on push and pull, which saves disk and time. They also explain two common surprises: deleting a file in a later layer does not shrink the image, and a change in one layer forces every later layer to rebuild."""),
    (r"""What is the difference between a tag and a digest?""",
     r"""A tag is a human-friendly name such as `1.0.0` or `latest`, and anyone with push rights can move it to a different image. A digest is the sha256 hash of the image's manifest, so it always means exactly the same content. Deploying by digest makes deploys repeatable and protects you from a tag that changed underneath you. Teams often keep both: a readable tag for people and a digest in deploy files."""),
    (r"""How can one image name work on both an Apple Silicon laptop and an Intel server?""",
     r"""The name points to an image index, also called a manifest list, rather than a single manifest. The index has one manifest per platform, such as linux/amd64 and linux/arm64, each with its own config and layers. When a machine pulls, Docker reads the index and downloads only the variant for its own CPU. You build such an image with `docker buildx build --platform linux/amd64,linux/arm64 --push`."""),
]

new["deeper"] = r"""A registry is just a web server with a small HTTP API, so you can read an image by hand with curl. Day 11's HTTP skills apply directly. Start the registry from the worked example again and push the two-platform `hello:multi` image to it.

First ask for the index. The `Accept` header tells the registry which JSON format you want:

`curl -s -H 'Accept: application/vnd.oci.image.index.v1+json' localhost:5001/v2/hello/manifests/multi | jq '.manifests[].platform.architecture'`

When we did this, the answer listed `amd64`, `arm64` and two `unknown` entries, which are the attestations. Each entry also has a `digest`. Copy the arm64 digest and ask for that manifest, this time with the header `Accept: application/vnd.oci.image.manifest.v1+json`, at `localhost:5001/v2/hello/manifests/<digest>`. The manifest names one config digest and two layer digests: the Alpine base and the layer that holds `hello.txt`.

Finally fetch the config itself from `localhost:5001/v2/hello/blobs/<config digest>` and pipe it into `jq '{architecture, os}'`. Ours said `"architecture": "arm64"` and `"os": "linux"`, with the command `cat /hello.txt`. Every object came from a URL that ends in its own digest, so the client can hash what it got and check it against the name it asked for.

A few more details explain output you will see on current Docker.

- Docker Engine 29 changed where images live. Fresh installs and Docker Desktop use the containerd image store. That means containerd, the helper program from Day 17, keeps the images, and it can hold several platforms of one image. `docker image ls --tree` shows them as a tree under each name.
- With the containerd image store, an image's ID is the digest of its index. So `docker build` output ends with `exporting manifest list sha256:...` and `docker history` shows the same first 12 characters.
- `docker image ls` on Engine 29 hides untagged images and collapses platforms; add `--all` or `--tree` to see everything.

The [OverlayFS driver page](https://docs.docker.com/engine/storage/drivers/overlayfs-driver/) shows how the layers become one folder tree on disk."""

new["closing"] = r"""We started with a lunchbox that stayed heavy after the soup was "removed". Now you know why: a later layer can hide a file but never take it out, and you saw the 53.8 MB against 3.8 MB to prove it. Before you move on, run `docker history` on an image you use often and look for a big row followed by a small one that deletes something. That pair is wasted space.

Next, we'll stop opening other people's boxes and pack our own. How do you write a Dockerfile that builds fast and stays small?"""

apply(L, new)
save(path, P, L, OL)
