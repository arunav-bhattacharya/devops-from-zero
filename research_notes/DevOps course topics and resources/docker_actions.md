# Docker and GitHub Actions beyond the basics: research notes (as of 30 October 2026)

How sources were verified (read this before reusing a URL):
- **Docs repos (primary sources).** I read docker/docs at commit `6a5bbde` (29 Oct 2026) and github/docs at commit `6cbe641` (29 Oct 2026) with a sparse `git clone`. Every `github.com/docker/docs/blob/main/...` and `github.com/github/docs/blob/main/...` link below was checked to exist (HTTP 200 from raw.githubusercontent.com on 30 Oct 2026). The published pages live on docs.docker.com and docs.github.com. Neither host resolved from this sandbox, so I did not open the published versions. The path rule is: docker/docs `content/manuals/engine/storage/_index.md` becomes `docs.docker.com/engine/storage/`, and github/docs `content/actions/reference/limits.md` becomes `docs.github.com/en/actions/reference/limits`. The lesson writer should spot-check any derived URL before publishing it. github/docs files contain Liquid templating (`{% ifversion fpt %}`). Where a fact differs by product, I used the GitHub.com (`fpt`) branch.
- **Action and tool repos.** I read the READMEs of actions/checkout, actions/cache, actions/upload-artifact, nektos/act and wagoodman/dive from clones, and checked each link with raw.githubusercontent.com. Latest version tags were read with `git ls-remote` on 30 Oct 2026.
- **(search)** marks a URL that appeared in a WebSearch result and was not opened. I only have the search engine's summary of it.
- **(cited in docs)** marks a URL that appeared inside a docs file I read.
- YouTube URLs all came from search results. youtube.com was blocked, so I could not confirm channels myself. A channel is named only when the search result title or summary named it.

---

## Q1. How do image layers, the union filesystem, the build cache, manifests and multi-platform images actually work?

### Takeaway
An image is three kinds of things: a stack of read-only, content-addressed filesystem diffs ("layers"), a JSON config, and a manifest that lists them by digest. A multi-platform image adds one more level, an index (manifest list) that points to one manifest per OS and architecture. A container is that stack plus one thin writable layer, merged into a single view by a union filesystem (OverlayFS). The build cache is a chain: if one instruction's inputs change, that layer and every layer after it rebuild.

### Cited Findings
**Layers and the container layer**
- "A Docker image is built up from a series of layers. Each layer represents an instruction in the image's Dockerfile." Each layer holds only the differences from the layer before it. Adding files and removing files both create a new layer. `CMD` only changes image metadata and does not create a layer. — [docker/docs: storage drivers](https://github.com/docker/docs/blob/main/content/manuals/engine/storage/drivers/_index.md)
- A new container adds a writable "container layer" on top of the image layers. All changes go there, it is deleted with the container, and many containers can share the same image layers because each has its own writable layer. — [docker/docs: storage drivers](https://github.com/docker/docs/blob/main/content/manuals/engine/storage/drivers/_index.md)
- "Layering is made possible by content-addressable storage and union filesystems." When a container runs, a union filesystem stacks the layers into one unified view. A separate directory is created for the running container's own changes. — [docker/docs: Understanding image layers (concepts guide)](https://github.com/docker/docs/blob/main/content/get-started/docker-concepts/building-images/understanding-image-layers.md)
- OverlayFS is a union filesystem. The image layers are `lowerdir`, the container layer is `upperdir`, and the unified view is `merged`. A file in the upper layer hides a file with the same name in a lower layer. — [docker/docs: OverlayFS driver](https://github.com/docker/docs/blob/main/content/manuals/engine/storage/drivers/overlayfs-driver.md)
- Copy-on-write: the first write to a file that came from the image triggers a `copy_up` of the whole file into `upperdir`, even if only a few bytes change. Later writes go to the copy. — [docker/docs: OverlayFS driver](https://github.com/docker/docs/blob/main/content/manuals/engine/storage/drivers/overlayfs-driver.md)
- Image filesystems record incremental changes as layers, and a "whiteout" file in a layer marks a lower-layer file as deleted. This comes from a search summary of iximiuz Labs' "How Container Images Actually Work", which surfaced only as a third-party mirror. — [mirror of the iximiuz article (search)](https://fooqux.com/article/3360)

**Where the daemon keeps layers (changed in Engine 29)**
- The containerd image store is the default storage backend for fresh installs of Docker Engine 29.0 and later. Upgraded daemons keep using the legacy graph drivers (overlay2) until you switch. containerd uses "snapshotters" instead of storage drivers. This enables local multi-platform images, attestations, Wasm, and lazy-pulling snapshotters (stargz, nydus). The containerd store is not available with `userns-remap`. — [docker/docs: containerd image store](https://github.com/docker/docs/blob/main/content/manuals/engine/storage/containerd.md); [docker/docs: Engine 29 release notes](https://github.com/docker/docs/blob/main/content/manuals/engine/release-notes/29.md)

**Build cache**
- "Once a layer changes, then all downstream layers need to be rebuilt as well. Even if they wouldn't build anything differently, they still need to re-run." — [docker/docs: build cache](https://github.com/docker/docs/blob/main/content/manuals/build/cache/_index.md)
- For `ADD`, `COPY` and `RUN --mount=type=bind`, the cache key includes a checksum of file metadata, but **not `mtime`**. For other instructions, cache checking only compares the instruction string. — [docker/docs: cache invalidation](https://github.com/docker/docs/blob/main/content/manuals/build/cache/invalidation.md)
- The cache for `RUN` is not invalidated automatically between builds. `RUN apk add curl` rebuilt a week later still gives the old `curl`. To force a re-run, change an earlier layer or clear the cache with `docker builder prune`. — [docker/docs: cache invalidation](https://github.com/docker/docs/blob/main/content/manuals/build/cache/invalidation.md)
- The optimization techniques, in the docs' order: order your layers, keep the context small, use bind mounts, use cache mounts (`RUN --mount=type=cache,target=/root/.npm npm install`, Go module/build caches, apt with `sharing=locked`), and use an external cache. — [docker/docs: optimize cache](https://github.com/docker/docs/blob/main/content/manuals/build/cache/optimize.md)
- BuildKit is the default builder for Docker Desktop and Docker Engine users. — [docker/docs: BuildKit](https://github.com/docker/docs/blob/main/content/manuals/build/buildkit/_index.md)

**Manifests and multi-platform images**
- Single-platform image: "a single manifest that points to a single configuration and a single set of layers". Multi-platform image: "a manifest list, pointing to multiple manifests, each of which points to a different configuration and set of layers". On pull, the registry returns the manifest list and Docker picks the variant that matches the host's architecture. — [docker/docs: multi-platform builds](https://github.com/docker/docs/blob/main/content/manuals/build/building/multi-platform.md)
- Containers share the host kernel, so a `linux/amd64` container cannot run on an arm64 host without emulation. — [docker/docs: multi-platform builds](https://github.com/docker/docs/blob/main/content/manuals/build/building/multi-platform.md)
- Docker Desktop and Engine 29.0+ default to the containerd image store, which supports multi-platform images with no extra setup. There are three build strategies: QEMU emulation (easiest, but "can be much slower"), a builder with multiple native nodes, and cross-compilation in multi-stage builds. Official BuildKit releases bundle QEMU user-mode emulators. — [docker/docs: multi-platform builds](https://github.com/docker/docs/blob/main/content/manuals/build/building/multi-platform.md)
- `docker buildx imagetools inspect` shows "details of an image in the registry", and `--raw` prints the raw manifest JSON. — [docker/docs CLI ref: imagetools inspect](https://github.com/docker/docs/blob/main/data/cli/buildx/docker_buildx_imagetools_inspect.yaml)
- `docker image ls --tree` lists multi-platform images as a tree. In Engine 29.0, `docker image ls` uses this view (collapsed) by default and hides untagged images unless you pass `--all`. — [docker/docs CLI ref: image ls](https://github.com/docker/docs/blob/main/data/cli/engine/docker_image_ls.yaml); [Engine 29 release notes](https://github.com/docker/docs/blob/main/content/manuals/engine/release-notes/29.md)
- Engine 29.0 added multi-platform `docker image save/load --platform linux/amd64,linux/arm64`. — [Engine 29 release notes](https://github.com/docker/docs/blob/main/content/manuals/engine/release-notes/29.md)
- BuildKit attaches provenance attestations at `mode=min` to images by default. Use `--provenance=mode=max`, `--provenance=false` and `--sbom` to change this. — [docker/docs: attestations](https://github.com/docker/docs/blob/main/content/manuals/build/metadata/attestations/_index.md)
- iximiuz Labs has a hands-on challenge, "Inspect OCI Image Layout of Single- and Multi-Platform Images". According to the search summary, it shows that an image index lists platform-specific manifests rather than layers, and that each platform's config blob determines its ImageID. — [iximiuz Labs challenge (search)](https://labs.iximiuz.com/challenges/inspect-oci-image-layout); see also [iximiuz Labs: container image from scratch (search)](https://labs.iximiuz.com/tutorials/container-image-from-scratch)
- Registries store blobs addressed by digest, and a manifest ties blobs together under a tag. This is from a search summary of iximiuz's "How Container Registries Work: Pushing and Pulling Images By Hand", via a mirror. — [mirror (search)](https://fooqux.com/article/5345)

### Inferences
- Intuition for engineers: layers are like git objects for a filesystem. Each is an immutable diff named by its hash. The image config plus manifest is like a commit that lists blob hashes. A tag is like a branch name pointing at a manifest digest, so tags move and digests don't. An index is a menu: "for arm64 use manifest A, for amd64 use manifest B".
- The container layer is like scratch paper laid over a stack of transparencies. Reads fall through to the first transparency that has the file. A write copies the whole file onto the scratch paper first, which is why writing big files into the container layer is slow and why databases belong on volumes.
- Deleting a file in a later `RUN` hides it but never shrinks the image, because the earlier layer still holds the bytes. This is the main reason for `&&`-chaining cleanup in one `RUN` and for multi-stage builds. It follows from "adding and removing files both result in a new layer".
- On an Apple Silicon Mac, `docker pull nginx` silently picks the `linux/arm64` manifest. That is a good "aha" moment when paired with `imagetools inspect --raw`.

### Gaps
- I could not open the official iximiuz article "How Container Images Actually Work: Layers, Configs, Manifests, Indexes, and More". Only a third-party mirror URL appeared in search, so the lesson writer should look up the canonical labs.iximiuz.com URL before linking it.
- The OCI image-spec repo was not opened. The descriptions of manifests and indexes rely on Docker's docs and the iximiuz summaries.

---

## Q2. Docker networking modes, container DNS, and volumes vs bind mounts vs tmpfs

### Takeaway
Always use a **user-defined bridge network**. It gives containers DNS by name through Docker's embedded DNS server at `127.0.0.11`, and it isolates each stack. The default `bridge` network only resolves by IP. Storage choice comes down to who owns the data: Docker owns **volumes** (persistent, fast, portable), you own **bind mounts** (a host path shared both ways), and **tmpfs** is RAM-only and disappears when the container stops. Engine 29 made **image mounts** (read-only contents of another image) generally available.

### Cited Findings
**Networking**
- On Linux, the built-in drivers are `bridge` (the default), `host` (no network isolation from the host), `none` (fully isolated), `overlay` (Swarm, across daemons), `ipvlan` (external VLANs) and `macvlan` (containers appear as devices on the host's network). — [docker/docs: networking overview](https://github.com/docker/docs/blob/main/content/manuals/engine/network/_index.md)
- "User-defined bridge networks are superior to the default `bridge` network." User-defined bridges give automatic DNS resolution by name or alias. Containers on the default bridge can only reach each other by IP unless you use the legacy `--link`. User-defined bridges also isolate better: every container started without `--network` lands on the default bridge, where unrelated stacks can talk to each other. You can attach and detach containers on the fly, and each user-defined network creates its own configurable bridge. — [docker/docs: bridge driver](https://github.com/docker/docs/blob/main/content/manuals/engine/network/drivers/bridge.md)
- DNS: by default containers inherit the host's `/etc/resolv.conf`, and containers on the default bridge get a copy of it. Containers on custom networks use Docker's **embedded DNS server at `127.0.0.11`**, which forwards external lookups to the host's DNS servers. — [docker/docs: networking overview, "DNS services"](https://github.com/docker/docs/blob/main/content/manuals/engine/network/_index.md)
- Ports: every port of a container on a bridge network is reachable from the Docker host and from containers on the same network, but not from outside the host. `-p` publishes a port. "Publishing container ports is insecure by default": without an IP, a published port is open to the outside world. `-p 127.0.0.1:8080:80` limits it to the host. Before 28.0.0, hosts on the same L2 segment could still reach ports published to localhost. — [docker/docs: networking overview](https://github.com/docker/docs/blob/main/content/manuals/engine/network/_index.md); [docker/docs: port publishing](https://github.com/docker/docs/blob/main/content/manuals/engine/network/port-publishing.md)
- Host networking: the container shares the host's network stack and `-p` is ignored. It works on Docker Engine on Linux and on Docker Desktop 4.34 and later. On Desktop you must turn it on under Settings > Resources > Network > "Enable host networking", and you must be signed in. — [docker/docs: host driver](https://github.com/docker/docs/blob/main/content/manuals/engine/network/drivers/host.md)
- Engine 29.0 networking changes: experimental nftables support (`firewall-backend: nftables`), new iptables rules (the `DOCKER-ISOLATION-STAGE-1/2` chains were removed), and environment variables from legacy links are no longer added. — [Engine 29 release notes](https://github.com/docker/docs/blob/main/content/manuals/engine/release-notes/29.md); [docker/docs: nftables](https://github.com/docker/docs/blob/main/content/manuals/engine/network/firewall-nftables.md)
- Compose creates one network named `<project-name>_default`, attaches every service to it, and registers each service's name for discovery. That is why `db` works as a hostname. — [docker/docs: Compose networking](https://github.com/docker/docs/blob/main/content/manuals/compose/how-tos/networking.md)

**Storage**
- Files written inside a container go to the writable container layer. They are lost when the container is removed and are hard to get out. — [docker/docs: storage overview](https://github.com/docker/docs/blob/main/content/manuals/engine/storage/_index.md)
- **Volumes** are persistent storage managed by the Docker daemon. They survive container removal and perform the same as the host filesystem. Touching volume data directly on the host is "unsupported, undefined behavior". **Bind mounts** link a host path into the container, and both host processes and the container can modify the files; use them when both sides need access. **tmpfs** mounts live in host memory, never touch disk, and are lost when the container stops; they suit caches and sensitive data. **Image mounts** expose another image's contents read-only; they need the containerd image store. — [docker/docs: storage overview](https://github.com/docker/docs/blob/main/content/manuals/engine/storage/_index.md)
- Image mounts are no longer experimental as of Engine 29.7.0. — [Engine 29 release notes](https://github.com/docker/docs/blob/main/content/manuals/engine/release-notes/29.md)
- Mounting onto a non-empty directory hides the files that were there, like mounting a USB drive over `/mnt`. A new, empty volume mounted at a path that has content in the image is **pre-populated** with that content (`volume-nocopy` turns this off). Anonymous volumes get random names and persist after the container is removed unless it was started with `--rm`. — [docker/docs: volumes](https://github.com/docker/docs/blob/main/content/manuals/engine/storage/volumes.md); [docker/docs: bind mounts](https://github.com/docker/docs/blob/main/content/manuals/engine/storage/bind-mounts.md)
- `--mount type=bind,...,bind-create-src` creates a missing host source directory. By default `--mount` errors if the path does not exist. This arrived in Engine 29.3.0. — [docker/docs: bind mounts](https://github.com/docker/docs/blob/main/content/manuals/engine/storage/bind-mounts.md); [Engine 29 release notes](https://github.com/docker/docs/blob/main/content/manuals/engine/release-notes/29.md)
- Docker Desktop on Mac uses VirtioFS file sharing by default (gRPC FUSE is the alternative), lets you choose the VMM, and offers "Use Rosetta for x86_64/amd64 emulation on Apple Silicon". The settings table lists Rosetta's default as Disabled. — [docker/docs: Desktop settings](https://github.com/docker/docs/blob/main/content/manuals/desktop/settings-and-maintenance/settings.md)

### Inferences
- On a Mac, "the host" in all of these docs is Docker Desktop's Linux VM, not macOS. Bind mounts cross the VM boundary through VirtioFS, so hot paths with many small files (for example `node_modules`) are better as volumes or synced with Compose Watch. The Compose Watch docs advise against syncing `node_modules`.
- Teaching heuristic: if Docker should own the data (database files), use a volume. If you own the data (source code being edited), use a bind mount. If nobody should keep it (secrets, scratch), use tmpfs.
- Most "container can't reach the other container" bugs on the course's Mac setup come from three things: using the default bridge, using `localhost` (which means the container itself), or publishing a port when a shared network was the fix.

### Gaps
- I did not find primary performance numbers for VirtioFS bind mounts versus volumes on Apple Silicon.
- The Desktop docs list Rosetta's default as "Disabled". Older Desktop versions may have defaulted differently, and I did not check the history.

---

## Q3. What changed recently in Docker (Engine 29, Compose v5, BuildKit, DHI, docker init, docker debug, Desktop licensing)?

### Takeaway
The big shifts since late 2025:
- Engine 29 (November 2025) made the **containerd image store the default** for fresh installs and deprecated cgroup v1. It has since gone through 29.9.2 (20 Oct 2026).
- **Compose v5** is Compose v2 plus an official Go SDK, renumbered to avoid confusion with the old file formats.
- **Docker Hardened Images** went from paid (May 2025) to a free, open-source catalog (Dec 2025) served from `dhi.io`.
- **`docker debug`** became free (Oct 2025).
- Desktop licensing has not changed: free for personal, education and small business use, paid for large companies.

### Cited Findings
**Docker Engine 29**
- 29.0.0 was released 10 Nov 2025 with "several breaking changes and deprecations":
  - containerd image store is the default for fresh installs
  - experimental nftables support
  - the daemon requires API v1.44+ (lowered back to v1.40 in 29.3.0)
  - **cgroup v1 deprecated**, with support "until at least May 2029"
  - Docker Content Trust removed from the CLI
  - the Go module `github.com/docker/docker` deprecated in favour of `github.com/moby/moby/client` and `/api`
  - `docker image ls` uses the new tree view by default
  - containerd updated to v2.1.5

  — [Engine 29 release notes](https://github.com/docker/docs/blob/main/content/manuals/engine/release-notes/29.md)
- Later 29.x additions (dates from the same file):
  - 29.2.0 (26 Jan 2026): experimental NRI, plus an image `Identity` field in inspect showing where an image came from
  - 29.3.0 (5 Mar 2026): `bind-create-src`
  - 29.5.0 (14 May 2026): rootless gets a new default `gvisor-tap-vsock` network driver; private time namespace on by default
  - 29.6.0 (18 Jun 2026): `GET /images/{name}/attestations` endpoint for SLSA provenance and SBOM
  - 29.7.0 (30 Jul 2026): image mounts GA, experimental `embedded-containerd`, `default-stop-timeout` daemon option
  - 29.8.0 (3 Sep 2026): `--umask` flag
  - 29.9.2 (20 Oct 2026) is the latest

  — [Engine 29 release notes](https://github.com/docker/docs/blob/main/content/manuals/engine/release-notes/29.md)

**Compose v5**
- "Compose v5, released in 2025, is functionally identical to Compose v2. Its primary distinction is the introduction of an official Go SDK." The version jumped straight to v5 "to avoid confusion with the legacy Compose file formats labeled 'v2' and 'v3'". Compose v2 and v5 follow the rolling Compose Specification, so the top-level `version:` element is optional and ignored. — [docker/docs: Compose history](https://github.com/docker/docs/blob/main/content/manuals/compose/intro/history.md); same page published at [docs.docker.com/compose/intro/history/ (search)](https://docs.docker.com/compose/intro/history/)
- The Compose release notes page redirects to GitHub releases. The latest docker/compose tag on 30 Oct 2026 was **v5.6.1** (from `git ls-remote`). — [Compose release notes (search)](https://docs.docker.com/release-notes/docker-compose); [docker/compose repo](https://github.com/docker/compose)
- Compose features worth teaching:
  - `depends_on` with `condition: service_healthy`, `service_completed_successfully` or `service_started`. Compose waits for "running", not "ready", unless you use a healthcheck condition. — [docker/docs: startup order](https://github.com/docker/docs/blob/main/content/manuals/compose/how-tos/startup-order.md); [Compose file reference: services](https://github.com/docker/docs/blob/main/content/reference/compose-file/services.md)
  - Compose Watch with actions `sync` (hot reload), `rebuild` and `sync+restart`. — [docker/docs: file watch](https://github.com/docker/docs/blob/main/content/manuals/compose/how-tos/file-watch.md)

**BuildKit and Buildx**
- The latest tags on 30 Oct 2026 were moby/buildkit **v0.34.1** and docker/buildx **v0.38.1** (`git ls-remote`). — [moby/buildkit](https://github.com/moby/buildkit); [docker/buildx](https://github.com/docker/buildx)
- **Build checks** arrived with Dockerfile 1.8. They are linting, or a dry run, for the Dockerfile and build options (`docker build --check`). — [docker/docs: build checks](https://github.com/docker/docs/blob/main/content/manuals/build/checks.md)
- Build secrets: "Build arguments and environment variables are inappropriate for passing secrets to your build, because they persist in the final image." Use secret mounts (`--secret` / `RUN --mount=type=secret`) instead. — [docker/docs: build secrets](https://github.com/docker/docs/blob/main/content/manuals/build/building/secrets.md)
- The `docker/docs` Build manual now has a "policies" section (validate images and git sources). I saw the files but did not study them. — [docker/docs: build policies intro](https://github.com/docker/docs/blob/main/content/manuals/build/policies/intro.md)

**Docker Hardened Images (DHI)**
- DHI launched commercially in May 2025. In December 2025 Docker made more than 1,000 hardened images free and open source under Apache 2.0, with enterprise tiers still sold. BleepingComputer covered this on 21 Dec 2025. The "up to 95% fewer vulnerabilities" figure is Docker's own claim. — [BleepingComputer (search)](https://bleepingcomputer.com/news/security/docker-hardened-images-now-open-source-and-available-for-free)
- Current docs: DHI **Community** images come from `dhi.io/<image>:<tag>` after `docker login dhi.io` with a free Docker account, for example `docker pull dhi.io/python:3.13`. Select and Enterprise subscribers mirror images into their own org namespace. — [docker/docs: DHI get started](https://github.com/docker/docs/blob/main/content/manuals/dhi/get-started.md); [docker/docs: use DHI](https://github.com/docker/docs/blob/main/content/manuals/dhi/how-to/use.md)
- DHI runtime images are distroless: no shell, no package manager, **non-root by default**. Use the `-dev` tags in build stages that need a shell or package manager, and `static` images for compiled binaries. The builds meet **SLSA Build Level 3** and ship signed SBOM and provenance attestations. — [docker/docs: use DHI](https://github.com/docker/docs/blob/main/content/manuals/dhi/how-to/use.md); [docker/docs: what is DHI](https://github.com/docker/docs/blob/main/content/manuals/dhi/explore/what.md)
- The DHI troubleshooting guide recommends `docker debug <container>` for shell-less images. — [docker/docs: DHI troubleshoot](https://github.com/docker/docs/blob/main/content/manuals/dhi/how-to/troubleshoot.md)

**docker init and docker debug**
- `docker init` (provided by Docker Desktop) writes `.dockerignore`, `Dockerfile`, `compose.yaml` and `README.Docker.md`. Templates cover ASP.NET Core, Go, Java (Maven uber-jar), Node, PHP with Apache, Python, Rust and Other. It warns that overwritten files cannot be recovered. — [docker/docs CLI ref: docker init](https://github.com/docker/docs/blob/main/data/cli/init/docker_init.yaml)
- `docker debug` gives you a shell inside any container or image, "even if they don't contain a shell", without changing the image. It brings a toolbox (vim, nano, htop, curl), lets you `install` Nix packages, and has an `entrypoint` builtin that prints, lints or runs the entrypoint. Changes are thrown away for images and stopped containers, but are visible inside running containers. — [docker/docs CLI ref: docker debug](https://github.com/docker/docs/blob/main/data/cli/debug/docker_debug.yaml)
- "Docker Debug is now free for all users", as of Docker Desktop 4.49.0 (23 Oct 2025). — [docker/docs: Desktop release notes](https://github.com/docker/docs/blob/main/content/manuals/desktop/release-notes.md)

**Docker Desktop and Hub**
- Docker Desktop 4.97.0 is the latest release (26 Oct 2026). On Mac it adds a setting to expose privileged ports (1–1024) to other machines on the LAN. — [Desktop release notes](https://github.com/docker/docs/blob/main/content/manuals/desktop/release-notes.md)
- Licensing: "Commercial use of Docker Desktop in larger enterprises (more than 250 employees or more than $10 million USD in annual revenue) requires a paid subscription". It is free for small businesses, personal use, education and non-commercial open source. Desktop supports the current and two previous major macOS releases. — [docker/docs: install on Mac](https://github.com/docker/docs/blob/main/content/manuals/desktop/setup/install/mac-install.md)
- Docker Hub pull limits, per 6 hours: unauthenticated users get 100 per IPv4 address or IPv6 /64, Personal (signed in) users get 200, and Pro, Team and Business are unlimited. — [docker/docs: Hub pull limits](https://github.com/docker/docs/blob/main/content/manuals/docker-hub/usage/pulls.md)

### Inferences
- For the course: tell learners to sign in to Docker Desktop. That doubles their Hub pull allowance and unlocks host networking. It is also needed for `dhi.io`.
- Because Engine 29 changed defaults only for **fresh installs**, two learners on "the same version" can see different `docker image ls` and storage behaviour. Lesson text should say "on a fresh install".
- Compose v5 is a renumbering, not a rewrite, so existing Compose content stays valid. The useful update is to drop `version:` from examples.

### Gaps
- I could not open Docker's own DHI announcement blog post. The free/open-source facts come from press coverage plus current docs, and the press and docs agree.
- I did not research alternatives to Docker Desktop on Mac (OrbStack, Colima, Podman Desktop) or their licences.
- I found no dedicated Docker blog post for the Compose v5 launch. The docs history page is the source.

---

## Q4. GitHub Actions in 2026: major features and limits

### Takeaway
GitHub.com now gives an **included compute usage in dollars** rather than minutes: $12/month on Free, which at $0.006/min is about 2,000 Linux x64 minutes. Standard runners stay **free for public repos** and self-hosted runners are free. **arm64 Linux and Windows runners** are standard labels for public and private repos. The other notable changes:
- Caching is 10 GB per repo by default, with 7-day eviction. Since mid-2026, untrusted triggers get read-only cache access.
- Artifacts from upload-artifact v4+ are immutable, and v7 can upload a single file unzipped.
- Reusable workflows nest 10 levels deep, with up to 50 unique workflows per run.
- Concurrency groups can now queue up to 100 pending runs.
- In supply-chain hygiene, the new items are immutable releases, Actions policies, and **workflow dependency lockfiles** (public preview, 14 Oct 2026).

### Cited Findings
**Billing, free usage and runners**
- Included usage per month on GitHub.com: Free $12, Pro $18, Free for organizations $12, Team $18, Enterprise Cloud $300. Artifact storage: 500 MB, 1 GB, 500 MB, 2 GB and 50 GB respectively. Cache storage: 10 GB per repository on every plan. GitHub Enterprise Server docs still describe the included amounts in minutes (2,000 / 3,000 / 50,000). — [github/docs: included quotas](https://github.com/github/docs/blob/main/data/reusables/billing/actions-included-quotas.md)
- Standard per-minute rates: Linux 1-core $0.002, Linux 2-core x64 $0.006, Linux 2-core **arm64 $0.005**, Windows x64 or arm64 $0.010, macOS $0.062. — [github/docs: runner prices](https://github.com/github/docs/blob/main/data/reusables/billing/actions-standard-runner-prices.md)
- "Actions usage is free for standard GitHub-hosted runners in public repositories, and for self-hosted runners." Larger runners are billed even in public repos. Usage is charged to the repository owner, not the person who triggered the run. A 10-minute Linux job costs $0.06 of the allowance. — [github/docs: actions-billing](https://github.com/github/docs/blob/main/data/reusables/actions/actions-billing.md); [github/docs: compute allowance model](https://github.com/github/docs/blob/main/data/reusables/billing/compute-allowance-model.md); [github/docs: Actions billing](https://github.com/github/docs/blob/main/content/billing/concepts/product-billing/github-actions.md)
- Price history:
  - Hosted-runner prices fell by up to 39% on 1 Jan 2026.
  - A $0.002/min "cloud platform charge" for self-hosted runners, due from 1 Mar 2026, was **postponed** on 17 Dec 2025.
  - Coverage disagrees on whether the postponement is indefinite or temporary. Current docs list self-hosted usage as free.

  — [The Register (search)](https://www.theregister.com/2025/12/17/github_charge_dev_own_hardware/?td=rt-3a); [Techzine (search)](https://www.techzine.eu/news/devops/137396/github-bends-to-criticism-and-delays-paid-self-hosting-of-runners/)
- Standard runner labels (from the runner table, 29 Oct 2026):
  - **Public repos**, Linux x64 with 4 vCPU and 16 GB RAM: `ubuntu-latest`/`ubuntu-24.04`, `ubuntu-22.04`, `ubuntu-26.04`.
  - **Linux arm64**: `ubuntu-24.04-arm`, `ubuntu-22.04-arm`, `ubuntu-26.04-arm`.
  - **Windows arm64**: `windows-11-arm`.
  - **macOS on M1** (3 cores, 7 GB): `macos-latest`, `macos-14`, `macos-15`, `macos-26`.
  - **macOS Intel**: `macos-15-intel`, `macos-26-intel`.
  - **Private repos** get 2 vCPU and 8 GB for Linux and Windows, and **arm64 Linux is listed for private repos too**.
  - `ubuntu-slim` is 1 vCPU and 5 GB.

  — [github/docs: supported GitHub-hosted runners](https://github.com/github/docs/blob/main/data/reusables/actions/supported-github-runners.md)
- Limits:
  - Job execution: 6 h on GitHub-hosted runners, 5 days self-hosted.
  - Workflow run: 35 days, including waiting for approvals; environment approval gates wait up to 30 days.
  - Matrix: 256 jobs per run.
  - Re-runs: 50.
  - Workflow file: 500 KB.
  - Self-hosted queue time: 24 h.
  - Concurrent jobs on standard runners: Free 20 (5 macOS), Pro 40, Team 60, Enterprise 500 (50 macOS).
  - Cache: 200 uploads/min and 1,500 downloads/min per repo.
  - GitHub-hosted runners pulling **public** Docker Hub images are not rate-limited.

  — [github/docs: Actions limits](https://github.com/github/docs/blob/main/content/actions/reference/limits.md)

**Caching**
- Cache entries not accessed for **7 days** are removed. The total is limited to **10 GB per repo** by default. Repos owned by users can raise it to 10 TB, with storage above 10 GB billed. If a budget is exceeded, the cache becomes read-only. — [github/docs: dependency caching reference](https://github.com/github/docs/blob/main/content/actions/reference/workflows-and-actions/dependency-caching.md)
- Lookup order: exact `key` in the current branch, then prefix matches, then each `restore-keys` entry in order. After that it repeats the search on the default or base branch. For a PR from `feature` into `main`, the search goes `feature` first, then `main`. The `setup-node`, `setup-python` and `setup-java` actions do caching for you. — [github/docs: dependency caching reference](https://github.com/github/docs/blob/main/content/actions/reference/workflows-and-actions/dependency-caching.md)
- `actions/cache@v5` runs on Node 24 and needs runner ≥ 2.327.1. v4 and later use the rewritten cache service (v2 APIs). The latest tag is **v6.1.0**. — [actions/cache README](https://github.com/actions/cache/blob/main/README.md)
- New in 2026: `issue_comment` and `pull_request_target` runs in the default-branch context get **read-only** cache access by default. So do `pull_request` runs with `types: [closed]`. Docker's GHA cache guide says to keep `cache-from: type=gha` and drop `cache-to` in those workflows. — [docker/docs: GitHub Actions cache](https://github.com/docker/docs/blob/main/content/manuals/build/ci/github-actions/cache.md), which links GitHub's changelog [read-only Actions cache for untrusted triggers, 26 Jun 2026 (cited in docs)](https://github.blog/changelog/2026-06-26-read-only-actions-cache-for-untrusted-triggers/)

**Artifacts**
- upload-artifact v4+ artifacts are **immutable**. "Uploading to the same artifact via multiple jobs is _not_ supported". `overwrite: true` replaces an artifact, which gives it a new ID. A job can create at most **500 artifacts**. Zipping loses file permissions (directories become 755, files 644), so tar first if you need them. `archive: false` (shown with `@v7`) uploads one file unzipped. The latest tag is **v7.0.2**. — [actions/upload-artifact README](https://github.com/actions/upload-artifact/blob/main/README.md)
- upload-artifact returns a SHA-256 `digest`, and download-artifact checks it and warns if it doesn't match. Artifacts and logs are kept for 90 days by default. — [github/docs: store and share data](https://github.com/github/docs/blob/main/content/actions/tutorials/store-and-share-data.md); [github/docs: retention statement](https://github.com/github/docs/blob/main/data/reusables/actions/artifact-log-retention-statement.md)

**Reuse: reusable workflows, composite actions, anchors**
- On GitHub.com, reusable workflows can nest up to **10 levels** and a workflow file can call up to **50 unique reusable workflows** (Enterprise Server: 4 and 20). `env` set at the caller's workflow level is **not** passed to the called workflow; use `vars`. In nested workflows, `GITHUB_TOKEN` permissions can only stay the same or get narrower. — [github/docs: reusable workflow reference](https://github.com/github/docs/blob/main/content/actions/reference/workflows-and-actions/reusing-workflow-configurations.md)
- Reusable workflows compared with composite actions:

  | Reusable workflow | Composite action |
  | --- | --- |
  | Called at job level | Runs as a step |
  | Can contain multiple jobs | Contains no jobs |
  | Each step logged | Logged as one step |
  | Can use secrets | Cannot use secrets |
  | Cannot be published to Marketplace | Can be published |
  | Nests 10 levels | Up to 10 composite actions per workflow |

  — [github/docs: reusing workflow configurations (concepts)](https://github.com/github/docs/blob/main/content/actions/concepts/workflows-and-actions/reusing-workflow-configurations.md)
- **YAML anchors and aliases** (`&`/`*`) are supported in workflows on GitHub.com. — [github/docs: reusing workflow configurations (concepts)](https://github.com/github/docs/blob/main/content/actions/concepts/workflows-and-actions/reusing-workflow-configurations.md)
- Billing for a reusable workflow goes to the caller. — [github/docs: billing and usage (actions concepts)](https://github.com/github/docs/blob/main/content/actions/concepts/billing-and-usage.md)

**Concurrency**
- `concurrency.queue`:
  - `single` is the default. At most one run is *pending* per group, and a new pending run cancels and replaces the older pending one.
  - `max` lets up to **100** runs wait, in FIFO order.
  - `queue: max` together with `cancel-in-progress: true` is a validation error.
  - Group names are case-insensitive.

  — [github/docs: concurrency reusable](https://github.com/github/docs/blob/main/data/reusables/actions/actions-group-concurrency.md); [github/docs: control concurrency](https://github.com/github/docs/blob/main/content/actions/how-tos/write-workflows/choose-when-workflows-run/control-workflow-concurrency.md); limit in [Actions limits](https://github.com/github/docs/blob/main/content/actions/reference/limits.md)

**Environments, rulesets, policies, immutability, lockfiles**
- Environments, environment secrets and protection rules work in **public** repos on every current plan. In private repos you need Pro, Team or Enterprise. On Free, Pro and Team, wait timers and required reviewers work **only in public repos**. — [github/docs: environments availability](https://github.com/github/docs/blob/main/data/reusables/gated-features/environments.md)
- "Ruleset workflows" (the successor to required workflows) are set at the **organization** or enterprise level to require workflows to pass before a PR can merge. — [github/docs: ruleset workflows](https://github.com/github/docs/blob/main/data/reusables/repositories/rulest-workflows-intro-paragraph.md)
- **Actions policies** ("workflow execution protections") can be set at enterprise, org and repo level. They have actor rules (who can trigger workflows) and event rules (which events are allowed, e.g. block `pull_request_target` or limit `workflow_dispatch`). — [github/docs: about Actions policies](https://github.com/github/docs/blob/main/content/actions/concepts/about-actions-policies.md)
- **Immutable releases**: if an action repo enables them, a GitHub release's tag (for example `v1.0.0`) cannot be moved. Maintainers who want a movable major tag like `v1` create it as a plain git tag without a release. — [github/docs: immutable releases for actions](https://github.com/github/docs/blob/main/content/actions/how-tos/create-and-publish-actions/using-immutable-releases-and-tags-to-manage-your-actions-releases.md)
- **Workflow dependency lockfiles**:
  - The file `.github/workflows/actions.lock` is generated by the `gh actions-lock` CLI extension.
  - It pins every action, **including transitive dependencies**, to a commit, and records `owner_id`/`repo_id` so a renamed or squatted repo is detected.
  - It does not pin reusable workflow calls. Pin those by SHA.
  - GitHub's docs say SHA pinning inside workflow files "is no longer necessary" for repos that adopt the lockfile.
  - Locked dependencies satisfy the "Require actions to be pinned to a full-length commit SHA" policy.

  — [github/docs: workflow dependency lockfiles](https://github.com/github/docs/blob/main/content/actions/concepts/security/workflow-dependency-lockfiles.md); [github/docs: lockfile and SHA policy](https://github.com/github/docs/blob/main/data/reusables/actions/lockfile-allowed-actions-sha.md)
- Lockfiles were announced in public preview on 14 Oct 2026. Sources disagree on plan eligibility: one summary says Enterprise Cloud only, and another notes a same-day editor's note changing the plans. GitHub calls the tool's behaviour subject to change. — [GitHub changelog (search)](https://github.blog/changelog/2026-10-14-github-actions-workflow-lockfiles-in-public-preview/); [github/gh-actions-lock (search)](https://github.com/github/gh-actions-lock)
- `actions/checkout` v6 stores credentials from `persist-credentials` in a separate file under `$RUNNER_TEMP` instead of `.git/config`. **v7** refuses to check out fork PR code under `pull_request_target` or `workflow_run` unless you set `allow-unsafe-pr-checkout: true`. The latest tag is **v7.0.1**. — [actions/checkout README](https://github.com/actions/checkout/blob/main/README.md)

### Inferences
- Updated beginner arithmetic: on a Free plan, $12 ÷ $0.006 ≈ 2,000 Linux x64 minutes, ≈ 2,400 arm64 minutes, or ≈ 193 macOS minutes for private repos. Public repos are free, so **put the course's practice repos in public** unless they hold secrets.
- arm64 runners now match an Apple Silicon laptop's architecture. That makes them a nice way to teach "build natively on each arch, then merge into a multi-platform image".
- Several official docs examples still show older major versions (`actions/cache@v4`, `actions/checkout@v6`) while the actions are at v6 and v7. The lesson writer should state versions explicitly and explain how to check the latest tag.

### Gaps
- I could not open the GitHub changelog for the lockfile plan eligibility because github.blog would not resolve.
- I found no post-January-2026 primary source on whether the self-hosted runner charge is permanently cancelled.
- I did not verify the "immutable actions" (OCI-packaged actions on ghcr) programme from 2024–2025. The current docs talk about immutable *releases* and lockfiles instead.

---

## Q5. Common beginner mistakes in GitHub Actions (secrets in logs, pull_request_target, unpinned actions, cache keys) and the 2025–2026 security changes

### Takeaway
Most real-world Actions compromises follow one pattern: **untrusted input reaches a context that has secrets**. Examples are a fork's code under `pull_request_target`, a PR title interpolated into `run:`, or a moved tag on a third-party action. GitHub responded in 2026 with secure defaults: checkout v7 refuses fork checkouts, a default policy blocks `pull_request_target` in public repos (enforcement due 2 Dec 2026 per the docs), untrusted triggers get read-only cache, and lockfiles arrived. Learners still need the basics: least-privilege `permissions:`, OIDC instead of stored cloud keys, and secrets passed through `env:`, never inlined.

### Cited Findings
**Secrets in logs**
- Redaction of secrets "is not guaranteed" because values can be transformed. Never store structured data (JSON, XML, YAML blobs) as a secret, because redaction needs an exact match. Register derived or encoded values (Base64, URL-encoded) with `::add-mask::`. Runners can only redact secrets used in the current job. — [github/docs: secure use reference](https://github.com/github/docs/blob/main/content/actions/reference/security/secure-use.md); [github/docs: secrets concepts](https://github.com/github/docs/blob/main/content/actions/concepts/security/secrets.md)
- "With the exception of `GITHUB_TOKEN`, secrets are not passed to the runner when a workflow is triggered from a forked repository." — [github/docs: forked secrets](https://github.com/github/docs/blob/main/data/reusables/actions/forked-secrets.md)
- Dependabot PR runs behave like fork runs, with a read-only `GITHUB_TOKEN`. — [github/docs: Dependabot note](https://github.com/github/docs/blob/main/data/reusables/actions/workflow-runs-dependabot-note.md)

**pull_request_target and "pwn requests"**
- `pull_request_target` runs with the base repo's `GITHUB_TOKEN` and secrets. The workflow file, and any `actions/checkout` without a `ref`, come from the **default branch**, which is what makes it safe by default.
- The risk comes from overriding that. The insecure pattern is checking out `github.event.pull_request.head.sha` and then running `make test`. Fetching fork code by other means (`gh pr checkout`, downloading a fork's artifact) is just as dangerous. `issue_comment` and `workflow_run` have the same problem.

  — [github/docs: securely using pull_request_target](https://github.com/github/docs/blob/main/content/actions/reference/security/securely-using-pull_request_target.md); GitHub Security Lab's [Preventing pwn requests (cited in docs)](https://securitylab.github.com/resources/github-actions-preventing-pwn-requests/)
- **Default policy**: GitHub adds a default policy that blocks `pull_request_target` in **public** repos that have no event policy of their own. It currently runs in "evaluate" mode, where runs continue and policy insights show what would be blocked. The docs say: "On December 2, 2026, GitHub will enforce the default policy for affected repositories". Private and internal repos are not affected. — [github/docs: securely using pull_request_target](https://github.com/github/docs/blob/main/content/actions/reference/security/securely-using-pull_request_target.md); feature flag on for GitHub.com: [default-pull-req-target-policy.yml](https://github.com/github/docs/blob/main/data/features/default-pull-req-target-policy.yml)
- **Conflict:** press coverage gives the enforcement date as **2 November 2026**. — [devactivity summary (search)](https://devactivity.com/posts/apps-tools/proactive-security-performance-navigating-github-actions-pull-request-target-changes); [Socket blog (search)](https://socket.dev/blog/github-actions-checkout-blocks-pull-request-target-checkouts). The docs repo (updated 29 Oct 2026) says **2 December 2026**, and that is the date I'd use.
- checkout v7 blocks fork PR checkouts under `pull_request_target`/`workflow_run` by default. — [actions/checkout README](https://github.com/actions/checkout/blob/main/README.md)

**Script injection**
- Attackers control parts of the `github` context, especially fields ending in `body`, `title`, `head_ref` and similar. `title="${{ github.event.pull_request.title }}"` inside `run:` lets a PR title containing `"` break out and run commands. The fix is to pass the value through an intermediate `env:` variable. — [github/docs: script injections](https://github.com/github/docs/blob/main/content/actions/concepts/security/script-injections.md)

**Unpinned actions and the supply chain**
- Tags and branches can move. If an upstream maintainer is compromised and a tag is repointed, your workflows run the attacker's code. — [github/docs: workflow dependency lockfiles](https://github.com/github/docs/blob/main/content/actions/concepts/security/workflow-dependency-lockfiles.md)
- Case study: **tj-actions/changed-files** (CVE-2025-30066). On 14 Mar 2025 its tags were repointed to a malicious commit that printed CI secrets into workflow logs. CISA issued an alert on 18 Mar 2025, and the related reviewdog/action-setup compromise is tracked as CVE-2025-30154. — [CISA alert (search)](https://www.cisa.gov/news-events/alerts/2025/03/18/supply-chain-compromise-third-party-github-action-cve-2025-30066)

**GITHUB_TOKEN permissions and OIDC**
- Since 2 Feb 2023, new repositories on personal accounts get a **read-only** `GITHUB_TOKEN` by default, and new org repos inherit the org setting. Existing repos were not changed, so older repos may still default to read/write. — [GitHub changelog 2023-02-02 (search)](https://github.blog/changelog/2023-02-02-github-actions-updating-the-default-github_token-permissions-to-read-only/)
- `permissions:` at workflow or job level adjusts the token, starting from the enterprise, org or repo default. — [github/docs: workflow syntax](https://github.com/github/docs/blob/main/content/actions/reference/workflows-and-actions/workflow-syntax.md)
- OIDC: the job needs `permissions: id-token: write`, which only allows requesting the JWT and grants no other write access. The cloud provider swaps it for a **short-lived** token valid for that job only, so you store no long-lived cloud secrets. — [github/docs: OIDC reference](https://github.com/github/docs/blob/main/content/actions/reference/security/oidc.md); [github/docs: OIDC concepts](https://github.com/github/docs/blob/main/content/actions/concepts/security/openid-connect.md)

**Cache key design and cache poisoning**
- Don't put tokens or credentials in cached paths: "Anyone with read access can create a pull request on a repository and access the contents of a cache." Keys should be ordered from most to least specific in `restore-keys`, and `hashFiles()` is the usual way to fingerprint lockfiles. — [github/docs: dependency caching reference](https://github.com/github/docs/blob/main/content/actions/reference/workflows-and-actions/dependency-caching.md); [github/docs: expressions (hashFiles)](https://github.com/github/docs/blob/main/content/actions/reference/workflows-and-actions/expressions.md)
- Untrusted triggers now get read-only cache. — see Q4; [docker/docs: GHA cache](https://github.com/docker/docs/blob/main/content/manuals/build/ci/github-actions/cache.md)

**Other gotchas**
- Every `if:` gets an implicit `success()` unless it contains a status function. To run after a failure you must include `failure()`. `always()` also runs when the run is cancelled, and the docs warn not to use it on critical steps such as getting sources, because the workflow may hang until it times out. — [github/docs: expressions](https://github.com/github/docs/blob/main/content/actions/reference/workflows-and-actions/expressions.md)
- Job outputs are written with `echo "name=value" >> "$GITHUB_OUTPUT"`. — [github/docs: pass job outputs](https://github.com/github/docs/blob/main/content/actions/how-tos/write-workflows/choose-what-workflows-do/pass-job-outputs.md)

### Inferences
Beginner mistakes to teach explicitly, in rough order of how often a new user will hit them:
1. Interpolating `${{ }}` straight into `run:`.
2. Leaving `permissions:` unset on an old repo, so the token is read/write.
3. Using `@main` or a movable tag for third-party actions.
4. Choosing `pull_request_target` "to get secrets on fork PRs".
5. A cache key without `runner.os` and a lockfile hash, which gives cross-OS or stale caches.
6. Uploading the same artifact name from every matrix leg, which breaks in v4+.
7. Expecting top-level `env` to reach a reusable workflow.
8. Using `concurrency` for deployments without knowing that the default `single` queue silently cancels older pending runs.

### Gaps
- I did not look at third-party linters (actionlint, zizmor) or StepSecurity Harden-Runner in primary sources. Harden-Runner is only mentioned in tj-actions search coverage.
- No primary GitHub source was opened on whether `set-output`/`save-state` workflow commands are fully disabled in 2026.

---

## Q6. Small, free, local exercises that build intuition

### Takeaway
Everything below runs on an Apple Silicon Mac with Docker Desktop (free for personal use) plus Homebrew. For Actions, use `act` locally and a **public** GitHub repo for free real runs. Each exercise targets one mental model: layers, cache chain, manifest/index, DNS on user-defined networks, the volume lifecycle, and the trust boundaries in workflows.

### Cited Findings
**Docker**
1. **Layers by hand.** Docker's concepts guide has you build layers with `docker container commit -m "Add node" base-container node-base` and inspect them with `docker image history node-base`. — [docker/docs: understanding image layers](https://github.com/docker/docs/blob/main/content/get-started/docker-concepts/building-images/understanding-image-layers.md); [CLI ref: image history](https://github.com/docker/docs/blob/main/data/cli/engine/docker_image_history.yaml)
2. **dive.** Install with `brew install dive`. It shows each layer's contents and an "image efficiency" or wasted-space estimate (files duplicated or deleted across layers). `CI=true dive <image>` gives a pass/fail result using `lowestEfficiency` and `highestWastedBytes` rules. The latest tag is v0.13.1. — [wagoodman/dive README](https://github.com/wagoodman/dive/blob/main/README.md)
3. **Cache chain.** Write a Dockerfile that `COPY . .` *before* installing dependencies, change one source file, and watch everything rebuild. Then reorder so the dependency manifest is copied first, and add `RUN --mount=type=cache,target=/root/.npm`. — [docker/docs: optimize cache](https://github.com/docker/docs/blob/main/content/manuals/build/cache/optimize.md); [docker/docs: using the build cache (concepts guide)](https://github.com/docker/docs/blob/main/content/get-started/docker-concepts/building-images/using-the-build-cache.md)
4. **Inspect a manifest and index.** Run `docker buildx imagetools inspect --raw <multi-arch image>` to see the index JSON, then inspect one platform's manifest, then `docker image ls --tree`. — [CLI ref: imagetools inspect](https://github.com/docker/docs/blob/main/data/cli/buildx/docker_buildx_imagetools_inspect.yaml); [CLI ref: image ls](https://github.com/docker/docs/blob/main/data/cli/engine/docker_image_ls.yaml)
5. **Multi-platform build locally.** Run `docker buildx build --platform linux/amd64,linux/arm64 .`, which works out of the box with the containerd store on Desktop. Compare QEMU emulation speed with a cross-compiled multi-stage build. — [docker/docs: multi-platform](https://github.com/docker/docs/blob/main/content/manuals/build/building/multi-platform.md)
6. **Two-container network.** Start two containers on the default bridge and show that pinging by name fails. Create `docker network create app`, rerun both containers on it, and show that ping by name works. `cat /etc/resolv.conf` inside shows `nameserver 127.0.0.11`. Then show that `-p 8080:80` binds every interface and `-p 127.0.0.1:8080:80` does not. — [docker/docs: bridge](https://github.com/docker/docs/blob/main/content/manuals/engine/network/drivers/bridge.md); [docker/docs: networking DNS](https://github.com/docker/docs/blob/main/content/manuals/engine/network/_index.md); [docker/docs: port publishing](https://github.com/docker/docs/blob/main/content/manuals/engine/network/port-publishing.md)
7. **Volume lifecycle.**
   - Mount an empty named volume at `/usr/share/nginx/html` and watch it pre-populate from the image.
   - Bind-mount an empty host directory to the same path and watch it hide the content.
   - Remove the container with and without `--rm` to compare anonymous-volume leftovers.
   - Write to a tmpfs, then stop the container.

   — [docker/docs: volumes](https://github.com/docker/docs/blob/main/content/manuals/engine/storage/volumes.md); [docker/docs: storage overview](https://github.com/docker/docs/blob/main/content/manuals/engine/storage/_index.md)
8. **Hardened image and docker debug.**
   - Pull `dhi.io/python:3.13` after `docker login dhi.io`.
   - Try `docker exec ... sh`, which fails because there is no shell.
   - Then `docker debug <container>` succeeds.
   - Compare CVEs with `docker scout compare dhi.io/python:3.13 --to python:3.13`. The DHI quickstart shows this comparison.

   — [docker/docs: DHI get started](https://github.com/docker/docs/blob/main/content/manuals/dhi/get-started.md); [docker debug ref](https://github.com/docker/docs/blob/main/data/cli/debug/docker_debug.yaml)
9. **Scaffolding and linting.** Run `docker init` in a toy app, then critique and modify the generated Dockerfile. Run `docker build --check .`. — [docker init ref](https://github.com/docker/docs/blob/main/data/cli/init/docker_init.yaml); [build checks](https://github.com/docker/docs/blob/main/content/manuals/build/checks.md)
10. **Secrets leak demo.** Pass a fake token via `ARG`, find it with `docker history`, then redo the build with `RUN --mount=type=secret`. — [docker/docs: build secrets](https://github.com/docker/docs/blob/main/content/manuals/build/secrets.md) (path note: the file is at `content/manuals/build/building/secrets.md`, see [verified link](https://github.com/docker/docs/blob/main/content/manuals/build/building/secrets.md))
11. **iximiuz Labs.** The "Inspect OCI Image Layout of Single- and Multi-Platform Images" challenge works in the browser. I could not confirm whether it is free. — [iximiuz challenge (search)](https://labs.iximiuz.com/challenges/inspect-oci-image-layout)

**GitHub Actions**
1. **act.**
   - It reads `.github/workflows/` and uses the Docker API to pull or build the images it needs.
   - `act -l` lists workflows. `act pull_request` simulates an event and `act -j <job>` runs a single job.
   - `--secret-file` (default `.secrets`), `--var-file` (default `.vars`) and `--artifact-server-path` supply secrets, variables and an artifact server.
   - On **Apple M-series** chips, act warns you to run with `--container-architecture linux/amd64` if things fail.
   - Images: `catthehacker/ubuntu:act-latest` (Ubuntu-based). `nektos/act-environments-ubuntu` was last updated Feb 2020.
   - The latest tag is v0.2.92.

   — [nektos/act README](https://github.com/nektos/act/blob/main/README.md); [act cmd/root.go flags](https://github.com/nektos/act/blob/main/cmd/root.go); [act IMAGES.md](https://github.com/nektos/act/blob/main/IMAGES.md); user guide at [nektosact.com (cited in README)](https://nektosact.com)
   - act is for development and debugging and does not replace GitHub's runners. Do final validation on GitHub. — [search summary of act resources (search)](https://docsearch.algolia.com/mcp/docs/website/nektosact.com)
2. **Free real runs.** Standard runners in a public repo cost nothing. — [github/docs: actions-billing](https://github.com/github/docs/blob/main/data/reusables/actions/actions-billing.md)
3. **Cache-key lab.**
   - Key `${{ runner.os }}-npm-${{ hashFiles('**/package-lock.json') }}` with restore-keys `${{ runner.os }}-npm-`.
   - Run twice to see a hit, change the lockfile to see a miss with a partial restore, then delete the cache in the UI.
   - Push from a branch to see the branch-then-default-branch lookup order.

   — [github/docs: dependency caching](https://github.com/github/docs/blob/main/content/actions/reference/workflows-and-actions/dependency-caching.md)
4. **Matrix and artifacts lab.** Run a 2×2 matrix (`ubuntu-latest`, `ubuntu-24.04-arm` × two runtime versions) that uploads the same artifact name and fails on v4+. Fix it with `name: report-${{ matrix.os }}-${{ matrix.v }}`. — [actions/upload-artifact README](https://github.com/actions/upload-artifact/blob/main/README.md); [github/docs: run job variations](https://github.com/github/docs/blob/main/content/actions/how-tos/write-workflows/choose-what-workflows-do/run-job-variations.md)
5. **Script injection lab (own repo only).** Open a PR whose title contains `"; echo pwned; #` against a workflow that inlines the title, then fix it with `env:`. — [github/docs: script injections](https://github.com/github/docs/blob/main/content/actions/concepts/security/script-injections.md)
6. **Concurrency lab.** Push three commits quickly with the default `single` queue (the middle one is cancelled), then with `queue: max` (all three run in order). — [github/docs: control concurrency](https://github.com/github/docs/blob/main/content/actions/how-tos/write-workflows/choose-when-workflows-run/control-workflow-concurrency.md)
7. **Pinning lab.** Replace `@v4` tags with full SHAs. Optionally, if eligible, run `gh actions-lock` to generate `.github/workflows/actions.lock` and look at its transitive entries. — [github/docs: lockfiles](https://github.com/github/docs/blob/main/content/actions/concepts/security/workflow-dependency-lockfiles.md)

### Inferences
- Pair every Docker exercise with a "predict, then run" prompt, for example: "Will the second build use the cache? Which layer breaks it?" The cache chain and DNS-by-name are counter-intuitive enough to make good prediction tasks.
- Because act defaults to amd64 images on Apple Silicon (hence the warning), learners meet emulation in practice. That ties back to the multi-platform lesson.

### Gaps
- I couldn't confirm the pricing or free tier of iximiuz Labs challenges.
- I did not test act's fidelity for `services:`, OIDC, or cache and artifact actions in 2026. These are known areas where local emulation differs, but I found no primary source in this pass.

---

## Q7. Lesson-by-lesson teaching notes (Docker 1–6, GitHub Actions 1–5)

### Takeaway
Each lesson below gives concepts in teaching order (each with a one-line explanation and an intuition), the misconceptions to pre-empt, current facts with sources, exercises (cross-referenced to Q6), and 3–8 curated resources with exact, verified URLs. The intuitions are my pedagogy, not sourced facts. The facts link back to Q1–Q6.

### Cited Findings

#### Docker Lesson 1: Containers and first run
**Concepts in teaching order**
1. *Container = an isolated process on a shared kernel.* Intuition: not a tiny VM, but a normal Linux process wearing blinkers (namespaces) and a budget (cgroups). Source for the kernel features: Julia Evans' zine covers cgroups, namespaces, seccomp-bpf, overlay filesystems and pivot_root — [wizardzines: How Containers Work! (search)](https://wizardzines.com/zines/containers/).
2. *On a Mac there is a Linux VM.* Docker Desktop runs Linux containers in a VM. You choose the VMM, and Rosetta can accelerate amd64 binaries. — [Desktop settings](https://github.com/docker/docs/blob/main/content/manuals/desktop/settings-and-maintenance/settings.md)
3. *Image vs container.* The image is read-only layers. The container adds a writable layer that dies with it. Intuition: class vs instance. — [storage drivers](https://github.com/docker/docs/blob/main/content/manuals/engine/storage/drivers/_index.md)
4. *Lifecycle: run, ps, logs, exec, stop, rm, `--rm`.*
5. *Debugging minimal containers with `docker debug`* (free since Desktop 4.49.0). — [docker debug ref](https://github.com/docker/docs/blob/main/data/cli/debug/docker_debug.yaml); [Desktop release notes](https://github.com/docker/docs/blob/main/content/manuals/desktop/release-notes.md)

**Misconceptions**
- "Containers are lightweight VMs." They share the host kernel, which is why an amd64 image needs emulation on arm64. — [multi-platform](https://github.com/docker/docs/blob/main/content/manuals/build/building/multi-platform.md)
- "Data I write in a container is saved." It is lost when the container is removed. — [storage overview](https://github.com/docker/docs/blob/main/content/manuals/engine/storage/_index.md)
- "Docker Desktop is paid." It is free for personal use, education, and businesses under 250 employees and $10M revenue. — [Mac install](https://github.com/docker/docs/blob/main/content/manuals/desktop/setup/install/mac-install.md)

**Current facts**
- Desktop is at 4.97.0 (26 Oct 2026), and Engine 29.9.2 is the latest Engine. See Q3.

**Exercises**
- Run `nginx` with `--rm -p 127.0.0.1:8080:80`. Write a file inside, then `rm` the container and look for the file.
- `docker debug` into a distroless or DHI container (Q6 #8).

**Resources**
- [docker/docs: What is a container? (concepts guide)](https://github.com/docker/docs/blob/main/content/get-started/docker-concepts/the-basics/what-is-a-container.md)
- [Julia Evans, "New zine: How Containers Work!" (search)](https://jvns.ca/blog/2020/04/27/new-zine-how-containers-work/) and [container networking comic (search)](https://wizardzines.com/comics/container-networking)
- Video: "Docker Crash Course for Absolute Beginners [NEW]". The search summary attributes it to TechWorld with Nana, about 3h25m, roughly 3 years old. — [YouTube (search)](https://www.youtube.com/watch?v=pg19Z8LL06w)
- Video: "Docker Tutorial for Beginners - A Full DevOps Course on How to Run Applications in Containers". The title matches the freeCodeCamp/KodeKloud course, but the channel was not confirmed. — [YouTube (search)](https://www.youtube.com/watch?v=fqMOX6JJhGo)
- Video: "Docker Full Course for Beginners (2026)", channel not identified. — [YouTube (search)](https://www.youtube.com/watch?v=ekiGWd-Wark)

#### Docker Lesson 2: Images, layers and registries
**Concepts in teaching order**
1. *Layer = a filesystem diff named by its hash.* Intuition: a git commit for files. — [concepts: image layers](https://github.com/docker/docs/blob/main/content/get-started/docker-concepts/building-images/understanding-image-layers.md)
2. *Union filesystem.* OverlayFS stacks `lowerdir` layers under the container's `upperdir` into one `merged` view. Intuition: transparencies on an overhead projector. — [OverlayFS](https://github.com/docker/docs/blob/main/content/manuals/engine/storage/drivers/overlayfs-driver.md)
3. *Copy-up.* The first write to an image file copies the whole file up. — [OverlayFS](https://github.com/docker/docs/blob/main/content/manuals/engine/storage/drivers/overlayfs-driver.md)
4. *Manifest, config, tag, digest.* A tag is a movable name and a digest is immutable. Intuition: a branch vs a commit SHA.
5. *Index (manifest list) and multi-platform.* The client picks the matching architecture. — [multi-platform](https://github.com/docker/docs/blob/main/content/manuals/build/building/multi-platform.md)
6. *Registries and pull limits.* Docker Hub allows 100 pulls per 6 h unauthenticated and 200 when signed in. — [Hub pulls](https://github.com/docker/docs/blob/main/content/manuals/docker-hub/usage/pulls.md)
7. *Image store.* The containerd store is the default on fresh Engine 29 installs and on Desktop. — [containerd store](https://github.com/docker/docs/blob/main/content/manuals/engine/storage/containerd.md)

**Misconceptions**
- "`RUN rm` makes my image smaller." The bytes stay in the earlier layer, because removing files adds a layer. — [storage drivers](https://github.com/docker/docs/blob/main/content/manuals/engine/storage/drivers/_index.md)
- "`:latest` means newest." It is just a tag name. (Inference.)
- "An image is one file." It is a manifest plus a config plus layer blobs, and an index on top for multi-platform images.

**Current facts**
- `docker image ls` shows the tree view and hides untagged images by default in Engine 29. — [Engine 29 notes](https://github.com/docker/docs/blob/main/content/manuals/engine/release-notes/29.md)
- Provenance attestations at `mode=min` are attached by default. — [attestations](https://github.com/docker/docs/blob/main/content/manuals/build/metadata/attestations/_index.md)

**Exercises**
- Q6 #1 (commit and history), #2 (dive), #4 (imagetools inspect), and pulling the same tag by digest.

**Resources**
- [docker/docs: Understanding image layers](https://github.com/docker/docs/blob/main/content/get-started/docker-concepts/building-images/understanding-image-layers.md)
- [docker/docs: What is a registry?](https://github.com/docker/docs/blob/main/content/get-started/docker-concepts/the-basics/what-is-a-registry.md)
- [docker/docs: OverlayFS storage driver](https://github.com/docker/docs/blob/main/content/manuals/engine/storage/drivers/overlayfs-driver.md)
- [iximiuz Labs: container image from scratch (search)](https://labs.iximiuz.com/tutorials/container-image-from-scratch)
- [iximiuz Labs challenge: inspect OCI image layout (search)](https://labs.iximiuz.com/challenges/inspect-oci-image-layout)
- [wagoodman/dive](https://github.com/wagoodman/dive)

#### Docker Lesson 3: Dockerfiles
**Concepts in teaching order**
1. *Instruction → layer, metadata-only instructions don't create layers.* — [storage drivers](https://github.com/docker/docs/blob/main/content/manuals/engine/storage/drivers/_index.md)
2. *Build context and `.dockerignore`.* Keep the context small. — [optimize](https://github.com/docker/docs/blob/main/content/manuals/build/cache/optimize.md)
3. *Cache chain.* A changed layer invalidates everything after it. `COPY` checks file metadata but not mtime. `RUN` is not re-run automatically. Intuition: falling dominoes. — [cache](https://github.com/docker/docs/blob/main/content/manuals/build/cache/_index.md); [invalidation](https://github.com/docker/docs/blob/main/content/manuals/build/cache/invalidation.md)
4. *Order layers: dependencies first, source last.*
5. *Cache mounts and bind mounts in `RUN`.* — [optimize](https://github.com/docker/docs/blob/main/content/manuals/build/cache/optimize.md)
6. *CMD vs ENTRYPOINT, exec form.* (Not researched in this pass; see Gaps.)
7. *Build checks* with `docker build --check`. — [checks](https://github.com/docker/docs/blob/main/content/manuals/build/checks.md)
8. *`docker init` as a starting point to critique.* — [docker init](https://github.com/docker/docs/blob/main/data/cli/init/docker_init.yaml)

**Misconceptions**
- "Docker notices when packages update." `RUN apk add` is cached until something before it changes. — [invalidation](https://github.com/docker/docs/blob/main/content/manuals/build/cache/invalidation.md)
- "`touch`ing a file busts the cache." mtime is ignored. — [invalidation](https://github.com/docker/docs/blob/main/content/manuals/build/cache/invalidation.md)
- "`ARG`/`ENV` are fine for tokens." They persist in the image, so use secret mounts. — [build secrets](https://github.com/docker/docs/blob/main/content/manuals/build/building/secrets.md)

**Exercises**
- Q6 #3 (cache chain), #9 (init and check), #10 (ARG secret leak).

**Resources**
- [docker/docs: Using the build cache (concepts)](https://github.com/docker/docs/blob/main/content/get-started/docker-concepts/building-images/using-the-build-cache.md)
- [docker/docs: Writing a Dockerfile (concepts)](https://github.com/docker/docs/blob/main/content/get-started/docker-concepts/building-images/writing-a-dockerfile.md)
- [docker/docs: Optimize cache usage](https://github.com/docker/docs/blob/main/content/manuals/build/cache/optimize.md)
- [docker/docs: Cache invalidation](https://github.com/docker/docs/blob/main/content/manuals/build/cache/invalidation.md)
- [docker/docs: Build checks](https://github.com/docker/docs/blob/main/content/manuals/build/checks.md)
- Video: "Learn Docker in 7 Easy Steps - Full Beginner's Tutorial", channel not identified in results. — [YouTube (search)](https://www.youtube.com/watch?v=gAkwW2tuIqE)

#### Docker Lesson 4: Volumes and networks
**Concepts in teaching order**
1. *Writable layer is ephemeral.* — [storage overview](https://github.com/docker/docs/blob/main/content/manuals/engine/storage/_index.md)
2. *Volume vs bind mount vs tmpfs vs image mount.* Ask who owns the data. — [storage overview](https://github.com/docker/docs/blob/main/content/manuals/engine/storage/_index.md)
3. *Mount-over hides content, and empty volumes pre-populate from the image.* — [volumes](https://github.com/docker/docs/blob/main/content/manuals/engine/storage/volumes.md)
4. *Named vs anonymous volumes.* — [volumes](https://github.com/docker/docs/blob/main/content/manuals/engine/storage/volumes.md)
5. *Network drivers: bridge, host, none (overlay, macvlan, ipvlan only mentioned).* — [network overview](https://github.com/docker/docs/blob/main/content/manuals/engine/network/_index.md)
6. *Default vs user-defined bridge, and DNS at `127.0.0.11`.* Intuition: the default bridge is an office with no phone directory, and a user-defined network adds a receptionist who knows everyone's name. — [bridge](https://github.com/docker/docs/blob/main/content/manuals/engine/network/drivers/bridge.md)
7. *Publishing ports and the `127.0.0.1:` binding.* — [port publishing](https://github.com/docker/docs/blob/main/content/manuals/engine/network/port-publishing.md)
8. *Host networking on Desktop (4.34+, opt-in).* — [host](https://github.com/docker/docs/blob/main/content/manuals/engine/network/drivers/host.md)

**Misconceptions**
- "`localhost` inside a container is my Mac." It is the container itself. (Inference, from network isolation.)
- "`-p 8080:80` is local only." It is exposed on all interfaces unless you bind an IP. — [port publishing](https://github.com/docker/docs/blob/main/content/manuals/engine/network/port-publishing.md)
- "Containers on the default bridge find each other by name." Only on user-defined networks. — [bridge](https://github.com/docker/docs/blob/main/content/manuals/engine/network/drivers/bridge.md)
- "Editing files under the volume path on the host is fine." Docker calls this undefined behaviour. — [storage overview](https://github.com/docker/docs/blob/main/content/manuals/engine/storage/_index.md)

**Exercises**
- Q6 #6 (two-container network), #7 (volume lifecycle). Also run Julia Evans-style experiments: `docker network inspect` and `cat /etc/resolv.conf`.

**Resources**
- [docker/docs: Storage overview](https://github.com/docker/docs/blob/main/content/manuals/engine/storage/_index.md)
- [docker/docs: Volumes](https://github.com/docker/docs/blob/main/content/manuals/engine/storage/volumes.md)
- [docker/docs: Networking overview](https://github.com/docker/docs/blob/main/content/manuals/engine/network/_index.md)
- [docker/docs: Bridge network driver](https://github.com/docker/docs/blob/main/content/manuals/engine/network/drivers/bridge.md)
- [docker/docs: Persisting container data (concepts)](https://github.com/docker/docs/blob/main/content/get-started/docker-concepts/running-containers/persisting-container-data.md)
- [Julia Evans comic: container networking (search)](https://wizardzines.com/comics/container-networking)

#### Docker Lesson 5: Docker Compose
**Concepts in teaching order**
1. *A Compose file describes the desired state of a multi-container app.* Compose v5 is v2 plus a Go SDK, and `version:` is obsolete. — [Compose history](https://github.com/docker/docs/blob/main/content/manuals/compose/intro/history.md)
2. *Project name and `<project>_default` network, with service names as DNS names.* — [Compose networking](https://github.com/docker/docs/blob/main/content/manuals/compose/how-tos/networking.md)
3. *Named volumes in Compose.*
4. *Startup order: `depends_on` + `healthcheck` + `condition: service_healthy`.* Intuition: "running" is not "ready". — [startup order](https://github.com/docker/docs/blob/main/content/manuals/compose/how-tos/startup-order.md)
5. *Dev loop with `docker compose watch` (sync, rebuild, sync+restart).* — [file watch](https://github.com/docker/docs/blob/main/content/manuals/compose/how-tos/file-watch.md)
6. *Profiles, multiple Compose files, env vars, secrets.* The how-to pages exist (`profiles.md`, `multiple-compose-files/`, `environment-variables/`, `use-secrets.md`), but I did not study them.

**Misconceptions**
- "`depends_on` waits for the database to be ready." It waits for "running" unless you add a healthcheck condition. — [startup order](https://github.com/docker/docs/blob/main/content/manuals/compose/how-tos/startup-order.md)
- "I need `version: '3.8'`." It is optional and ignored by v2 and v5. — [Compose history](https://github.com/docker/docs/blob/main/content/manuals/compose/intro/history.md)
- "Compose v5 is a new file format." It is the same Compose Specification. — [Compose history](https://github.com/docker/docs/blob/main/content/manuals/compose/intro/history.md)

**Exercises**
- Run web + Postgres with a healthcheck. Break the healthcheck and watch the web service wait.
- Add `develop.watch` with a `sync` action and show hot reload without a bind mount.
- Run `docker init` to get a starting `compose.yaml`.

**Resources**
- [docker/docs: Compose networking](https://github.com/docker/docs/blob/main/content/manuals/compose/how-tos/networking.md)
- [docker/docs: Control startup order](https://github.com/docker/docs/blob/main/content/manuals/compose/how-tos/startup-order.md)
- [docker/docs: Compose Watch](https://github.com/docker/docs/blob/main/content/manuals/compose/how-tos/file-watch.md)
- [docs.docker.com: Compose history and versions (search)](https://docs.docker.com/compose/intro/history/)
- Video playlist: "'Ultimate Docker Compose Tutorial' by TechWorld with Nana". — [YouTube playlist (search)](https://www.youtube.com/playlist?list=PLpm99KpnMKpY_TlyFbQPaG6RSnGGDEKbR)
- Video: "The Future of Compose, Hosted by Bret Fisher". — [YouTube (search)](https://www.youtube.com/watch?v=2uU_dPFwPnk)

#### Docker Lesson 6: Production-ready images
**Concepts in teaching order**
1. *Multi-stage builds.* Build tools stay in the builder stage and only artifacts are copied out. Intuition: a kitchen vs the plate. — [concepts: multi-stage builds](https://github.com/docker/docs/blob/main/content/get-started/docker-concepts/building-images/multi-stage-builds.md); [manual: multi-stage](https://github.com/docker/docs/blob/main/content/manuals/build/building/multi-stage.md)
2. *Minimal or distroless bases, non-root, and Docker Hardened Images.* `dhi.io` Community images are free. Use `-dev` variants for builders and `static` for compiled binaries. — [DHI use](https://github.com/docker/docs/blob/main/content/manuals/dhi/how-to/use.md)
3. *Build secrets, not ARG/ENV.* — [build secrets](https://github.com/docker/docs/blob/main/content/manuals/build/building/secrets.md)
4. *Multi-platform images (amd64 + arm64).* Strategies are QEMU, native nodes, or cross-compile. — [multi-platform](https://github.com/docker/docs/blob/main/content/manuals/build/building/multi-platform.md)
5. *Supply-chain metadata.* SBOM and provenance attestations (min by default), plus the Engine 29.6 attestations API. — [attestations](https://github.com/docker/docs/blob/main/content/manuals/build/metadata/attestations/_index.md); [Engine 29 notes](https://github.com/docker/docs/blob/main/content/manuals/engine/release-notes/29.md)
6. *Pin bases by digest, scan, and measure size with dive.* — [dive](https://github.com/wagoodman/dive/blob/main/README.md)
7. *Debugging shell-less images with `docker debug`.* — [DHI troubleshoot](https://github.com/docker/docs/blob/main/content/manuals/dhi/how-to/troubleshoot.md)
8. *Bridge to CI.* Docker's GHA cache backends (`type=gha`, registry), and the read-only cache for untrusted triggers. — [Docker GHA cache](https://github.com/docker/docs/blob/main/content/manuals/build/ci/github-actions/cache.md)

**Misconceptions**
- "Smaller image = secure image." Size helps, but non-root, a minimal package set and patched bases matter more. DHI's claim is about attack surface, and the "95%" figure is vendor-stated. — [DHI what](https://github.com/docker/docs/blob/main/content/manuals/dhi/explore/what.md)
- "I can't debug distroless." `docker debug` works. — [docker debug ref](https://github.com/docker/docs/blob/main/data/cli/debug/docker_debug.yaml)
- "One image works everywhere." Not without a multi-platform index. On Apple Silicon, an amd64-only production image runs under emulation locally. — [multi-platform](https://github.com/docker/docs/blob/main/content/manuals/build/building/multi-platform.md)

**Exercises**
- Shrink a Node or Python app from a full base to a multi-stage DHI build. Measure with `docker images` and `dive`, and compare CVEs with `docker scout compare`.
- Build `linux/amd64,linux/arm64` and inspect the resulting index.

**Resources**
- [docker/docs: Multi-stage builds (concepts)](https://github.com/docker/docs/blob/main/content/get-started/docker-concepts/building-images/multi-stage-builds.md)
- [docker/docs: Multi-platform builds](https://github.com/docker/docs/blob/main/content/manuals/build/building/multi-platform.md)
- [docker/docs: DHI get started](https://github.com/docker/docs/blob/main/content/manuals/dhi/get-started.md)
- [docker/docs: Build secrets](https://github.com/docker/docs/blob/main/content/manuals/build/building/secrets.md)
- [docker/docs: Attestations](https://github.com/docker/docs/blob/main/content/manuals/build/metadata/attestations/_index.md)
- Video: "Docker Production Best Practices from Bret Fisher at DockerCon". It dates from 2017, so present it as principles, not current commands. — [YouTube (search)](https://www.youtube.com/watch?v=V4f_sHTzvCI)
- Video: "Docker Multi-stage for Production-ready Container Images", presenter not identified. — [YouTube (search)](https://www.youtube.com/watch?v=EkOCLmvwEhc)
- [BleepingComputer: DHI now free and open source (search)](https://bleepingcomputer.com/news/security/docker-hardened-images-now-open-source-and-available-for-free)

#### GitHub Actions Lesson 1: Git, pull requests and CI/CD ideas
**Concepts in teaching order**
1. *CI = every change is built and tested automatically. CD = it is releasable or deployed automatically.* — [github/docs: understand GitHub Actions](https://github.com/github/docs/blob/main/content/actions/get-started/understand-github-actions.md)
2. *The PR is the unit of review, and CI status checks gate the merge.* Org-level ruleset workflows can require workflows to pass. — [ruleset workflows](https://github.com/github/docs/blob/main/data/reusables/repositories/rulest-workflows-intro-paragraph.md)
3. *Vocabulary: event → workflow → job → step → action, and runner.* Intuition: event = doorbell, workflow = recipe, job = cook on a separate stove (VM), step = recipe line.
4. *Trust boundaries.* Fork PRs don't get secrets. Intuition: strangers can propose changes but don't get the house keys. — [forked secrets](https://github.com/github/docs/blob/main/data/reusables/actions/forked-secrets.md)
5. *Cost model.* Public repos run free. Private repos draw from a $12/month allowance on Free. — [quotas](https://github.com/github/docs/blob/main/data/reusables/billing/actions-included-quotas.md)

**Misconceptions**
- "CI is just running tests on a server." It is also the gate on merging and the audit trail.
- "Actions minutes are unlimited." Only in public repos on standard runners. — [actions-billing](https://github.com/github/docs/blob/main/data/reusables/actions/actions-billing.md)

**Exercises**
- Create a public repo, open a PR from a branch, and add a trivial check that must pass.

**Resources**
- [github/docs: Understanding GitHub Actions](https://github.com/github/docs/blob/main/content/actions/get-started/understand-github-actions.md)
- [github/docs: Continuous integration](https://github.com/github/docs/blob/main/content/actions/get-started/continuous-integration.md)
- [github/docs: Continuous deployment](https://github.com/github/docs/blob/main/content/actions/get-started/continuous-deployment.md)
- Video: "GitHub Actions Tutorial - Basic Concepts and CI/CD Pipeline with Docker", TechWorld with Nana, about 32 min, Oct 2020, so the UI is dated. — [YouTube embed (search)](https://www.youtube.com/embed/R8_veQiYBjI)

#### GitHub Actions Lesson 2: First workflow
**Concepts in teaching order**
1. *Workflow file location and anatomy: `on`, `jobs`, `runs-on`, `steps`, `uses` vs `run`.* — [workflow syntax](https://github.com/github/docs/blob/main/content/actions/reference/workflows-and-actions/workflow-syntax.md)
2. *Choosing a runner label.* `ubuntu-latest` is 24.04. There are arm64 labels (`ubuntu-24.04-arm`) and `ubuntu-slim`. — [runner table](https://github.com/github/docs/blob/main/data/reusables/actions/supported-github-runners.md)
3. *Every job is a fresh VM.* Nothing carries over without artifacts or cache. Intuition: each job is a new hotel room.
4. *Triggers: push, pull_request, workflow_dispatch, schedule.* — [events](https://github.com/github/docs/blob/main/content/actions/reference/workflows-and-actions/events-that-trigger-workflows.md)
5. *Pinning action versions.* Major tags vs SHAs. Current majors are checkout v7, cache v6 and upload-artifact v7 (`git ls-remote`, 30 Oct 2026).
6. *Running locally with act.* — [act README](https://github.com/nektos/act/blob/main/README.md)

**Misconceptions**
- "Jobs share a filesystem." They don't. Each job gets its own runner.
- "`ubuntu-latest` never changes." It is an alias that moves (currently 24.04, with 26.04 available). — [runner table](https://github.com/github/docs/blob/main/data/reusables/actions/supported-github-runners.md)
- "act is identical to GitHub." It is an approximation. Validate on GitHub. — [act resources (search)](https://docsearch.algolia.com/mcp/docs/website/nektosact.com)

**Exercises**
- A hello-world workflow on push with `workflow_dispatch` inputs. Run it with act (`act -l`, `act -j`, and `--container-architecture linux/amd64` on an M-series Mac), then on GitHub.

**Resources**
- [github/docs: Quickstart](https://github.com/github/docs/blob/main/content/actions/get-started/quickstart.md)
- [github/docs: Create an example workflow](https://github.com/github/docs/blob/main/content/actions/tutorials/create-an-example-workflow.md)
- [github/docs: Workflow syntax](https://github.com/github/docs/blob/main/content/actions/reference/workflows-and-actions/workflow-syntax.md)
- [nektos/act](https://github.com/nektos/act) and its user guide at [nektosact.com (cited in README)](https://nektosact.com)
- [freeCodeCamp: Learn to use GitHub Actions step by step (search)](https://www.freecodecamp.org/news/learn-to-use-github-actions-step-by-step-guide/)
- Video: "GitHub Actions Crash Course", attributed to freeCodeCamp.org in the search summary. — [YouTube (search)](https://www.youtube.com/watch?v=1oJQRlz1v94)

#### GitHub Actions Lesson 3: A real CI pipeline (caching, matrix, artifacts)
**Concepts in teaching order**
1. *Cache vs artifact.* A cache speeds up future runs and is best-effort, evicted after 7 days, and capped at 10 GB. An artifact is a run's output, immutable from v4, and kept 90 days by default. Intuition: the cache is a pantry, the artifact is the delivered meal. — [dependency caching](https://github.com/github/docs/blob/main/content/actions/reference/workflows-and-actions/dependency-caching.md); [workflow artifacts](https://github.com/github/docs/blob/main/content/actions/concepts/workflows-and-actions/workflow-artifacts.md)
2. *Cache keys.* Use `runner.os` plus `hashFiles(lockfile)`, with restore-keys from specific to general, branch scope, and the `setup-*` built-in caching. — [dependency caching](https://github.com/github/docs/blob/main/content/actions/reference/workflows-and-actions/dependency-caching.md)
3. *Matrix.* `include`/`exclude`, `fail-fast`, `max-parallel`, up to 256 jobs. Add an arm64 leg. — [run job variations](https://github.com/github/docs/blob/main/content/actions/how-tos/write-workflows/choose-what-workflows-do/run-job-variations.md); [limits](https://github.com/github/docs/blob/main/content/actions/reference/limits.md)
4. *Artifacts v4+.* Use unique names per matrix leg, `overwrite`, `archive: false`, the 500-per-job limit, and digest verification. — [upload-artifact README](https://github.com/actions/upload-artifact/blob/main/README.md)
5. *Service containers* (Postgres or Redis for integration tests). — [github/docs: PostgreSQL service containers](https://github.com/github/docs/blob/main/content/actions/tutorials/use-containerized-services/create-postgresql-service-containers.md)
6. *Building Docker images in CI with the GHA cache backend.* — [Docker GHA cache](https://github.com/docker/docs/blob/main/content/manuals/build/ci/github-actions/cache.md)

**Misconceptions**
- "The cache is guaranteed." Entries are evicted after 7 days unused or under size pressure, and untrusted triggers now get read-only access. — [dependency caching](https://github.com/github/docs/blob/main/content/actions/reference/workflows-and-actions/dependency-caching.md); [Docker GHA cache](https://github.com/docker/docs/blob/main/content/manuals/build/ci/github-actions/cache.md)
- "Artifacts are for passing dependencies between runs." That is what caches are for. Artifacts are outputs.
- "All matrix legs can append to one artifact." Not since v4. — [upload-artifact README](https://github.com/actions/upload-artifact/blob/main/README.md)

**Exercises**
- Q6 GHA #3 (cache-key lab), #4 (matrix and artifacts lab). Then add a Postgres service container.

**Resources**
- [github/docs: Dependency caching reference](https://github.com/github/docs/blob/main/content/actions/reference/workflows-and-actions/dependency-caching.md)
- [github/docs: Store and share data with artifacts](https://github.com/github/docs/blob/main/content/actions/tutorials/store-and-share-data.md)
- [github/docs: Run job variations (matrix)](https://github.com/github/docs/blob/main/content/actions/how-tos/write-workflows/choose-what-workflows-do/run-job-variations.md)
- [actions/upload-artifact README](https://github.com/actions/upload-artifact/blob/main/README.md)
- [actions/cache README](https://github.com/actions/cache/blob/main/README.md)
- [docker/docs: Cache management with GitHub Actions](https://github.com/docker/docs/blob/main/content/manuals/build/ci/github-actions/cache.md)
- Video: "CI/CD Tutorial with GitHub Actions - Basic Concepts and Pipeline", channel not identified. — [YouTube (search)](https://www.youtube.com/watch?v=56kP5a6w_Kk)

#### GitHub Actions Lesson 4: Advanced workflows (expressions, contexts, conditions, job outputs, reusable workflows, composite actions, concurrency)
**Concepts in teaching order**
1. *Contexts* (`github`, `env`, `vars`, `secrets`, `matrix`, `needs`, `runner`, `job`, `steps`). Each one is available only in certain places. — [contexts concepts](https://github.com/github/docs/blob/main/content/actions/concepts/workflows-and-actions/contexts.md); [contexts reference](https://github.com/github/docs/blob/main/content/actions/reference/workflows-and-actions/contexts.md)
2. *Expressions and functions* (`contains`, `startsWith`, `format`, `toJSON`/`fromJSON`, `hashFiles`). — [expressions](https://github.com/github/docs/blob/main/content/actions/reference/workflows-and-actions/expressions.md)
3. *Conditions.* An implicit `success()`. `failure()` must be explicit, and use `always()` carefully. — [expressions](https://github.com/github/docs/blob/main/content/actions/reference/workflows-and-actions/expressions.md)
4. *Job outputs.* Write to `$GITHUB_OUTPUT`, then read through `needs.<job>.outputs`. — [pass job outputs](https://github.com/github/docs/blob/main/content/actions/how-tos/write-workflows/choose-what-workflows-do/pass-job-outputs.md)
5. *Reusable workflows.* `workflow_call`, 10 nesting levels, 50 unique per run, `env` not propagated, permissions only narrow. — [reuse reference](https://github.com/github/docs/blob/main/content/actions/reference/workflows-and-actions/reusing-workflow-configurations.md); [reuse how-to](https://github.com/github/docs/blob/main/content/actions/how-tos/reuse-automations/reuse-workflows.md)
6. *Composite actions.* Use them at step level, and compare with reusable workflows using the table in Q4. — [create a composite action](https://github.com/github/docs/blob/main/content/actions/tutorials/create-actions/create-a-composite-action.md)
7. *YAML anchors* for small repetition. — [reuse concepts](https://github.com/github/docs/blob/main/content/actions/concepts/workflows-and-actions/reusing-workflow-configurations.md)
8. *Concurrency.* Groups, `cancel-in-progress`, and the new `queue: max`. Intuition: one pump at a petrol station. `single` lets one car wait and sends older waiters away, while `max` forms a real queue of up to 100. — [concurrency](https://github.com/github/docs/blob/main/data/reusables/actions/actions-group-concurrency.md)

**Misconceptions**
- "`if: failure() || steps.x.outcome == 'success'` is like any boolean." Status-function semantics apply. — [expressions](https://github.com/github/docs/blob/main/content/actions/reference/workflows-and-actions/expressions.md)
- "A reusable workflow sees my workflow's `env`." It doesn't. — [reuse reference](https://github.com/github/docs/blob/main/content/actions/reference/workflows-and-actions/reusing-workflow-configurations.md)
- "Composite actions can read secrets directly." They can't. Pass values as inputs. — [reuse concepts](https://github.com/github/docs/blob/main/content/actions/concepts/workflows-and-actions/reusing-workflow-configurations.md)
- "Concurrency queues by default." The default keeps only one pending run. — [concurrency](https://github.com/github/docs/blob/main/data/reusables/actions/actions-group-concurrency.md)

**Exercises**
- Build a pipeline: a `version` job outputs a tag, a `build` job consumes it, and `deploy` runs only on `main` with `if:`.
- Extract the test steps into a composite action and the deploy into a reusable workflow.
- Q6 GHA #6 (concurrency lab).

**Resources**
- [github/docs: Contexts reference](https://github.com/github/docs/blob/main/content/actions/reference/workflows-and-actions/contexts.md)
- [github/docs: Expressions](https://github.com/github/docs/blob/main/content/actions/reference/workflows-and-actions/expressions.md)
- [github/docs: Reuse workflows](https://github.com/github/docs/blob/main/content/actions/how-tos/reuse-automations/reuse-workflows.md)
- [github/docs: Create a composite action](https://github.com/github/docs/blob/main/content/actions/tutorials/create-actions/create-a-composite-action.md)
- [github/docs: Control workflow concurrency](https://github.com/github/docs/blob/main/content/actions/how-tos/write-workflows/choose-when-workflows-run/control-workflow-concurrency.md)
- [github/docs: Reusing workflow configurations (concepts)](https://github.com/github/docs/blob/main/content/actions/concepts/workflows-and-actions/reusing-workflow-configurations.md)

#### GitHub Actions Lesson 5: Shipping safely (secrets, GITHUB_TOKEN permissions, environments, OIDC, supply-chain hygiene)
**Concepts in teaching order**
1. *Threat model: untrusted input + secrets = compromise.* Use the tj-actions case study. — [CISA (search)](https://www.cisa.gov/news-events/alerts/2025/03/18/supply-chain-compromise-third-party-github-action-cve-2025-30066)
2. *Secrets: scope (repo, environment, org), redaction limits, `::add-mask::`, no structured secrets.* — [secure use](https://github.com/github/docs/blob/main/content/actions/reference/security/secure-use.md)
3. *Script injection and the `env:` indirection.* — [script injections](https://github.com/github/docs/blob/main/content/actions/concepts/security/script-injections.md)
4. *GITHUB_TOKEN least privilege.* Set `permissions:` per workflow or job. New repos since Feb 2023 default to read-only. — [workflow syntax](https://github.com/github/docs/blob/main/content/actions/reference/workflows-and-actions/workflow-syntax.md); [changelog 2023 (search)](https://github.blog/changelog/2023-02-02-github-actions-updating-the-default-github_token-permissions-to-read-only/)
5. *`pull_request` vs `pull_request_target`.* Cover pwn requests, checkout v7's refusal, and the default policy (evaluate now, enforced 2 Dec 2026 per docs). — [pull_request_target guide](https://github.com/github/docs/blob/main/content/actions/reference/security/securely-using-pull_request_target.md); [checkout README](https://github.com/actions/checkout/blob/main/README.md)
6. *Environments.* Protection rules, required reviewers and wait timers. Free, Pro and Team get these only in public repos. — [environments availability](https://github.com/github/docs/blob/main/data/reusables/gated-features/environments.md); [deployment environments concepts](https://github.com/github/docs/blob/main/content/actions/concepts/workflows-and-actions/deployment-environments.md)
7. *OIDC.* `id-token: write` and short-lived, per-job cloud credentials. Intuition: a single-use visitor badge instead of a copied master key. — [OIDC concepts](https://github.com/github/docs/blob/main/content/actions/concepts/security/openid-connect.md); [OIDC reference](https://github.com/github/docs/blob/main/content/actions/reference/security/oidc.md)
8. *Supply-chain hygiene.* Pin to SHAs or adopt a lockfile (`gh actions-lock`, preview). Cover immutable releases, Actions policies (actor and event rules), artifact attestations, and Dependabot for actions. — [lockfiles](https://github.com/github/docs/blob/main/content/actions/concepts/security/workflow-dependency-lockfiles.md); [immutable releases](https://github.com/github/docs/blob/main/content/actions/how-tos/create-and-publish-actions/using-immutable-releases-and-tags-to-manage-your-actions-releases.md); [Actions policies](https://github.com/github/docs/blob/main/content/actions/concepts/about-actions-policies.md)
9. *Cache poisoning awareness.* Untrusted triggers get read-only cache, and caches must never hold secrets. — [dependency caching](https://github.com/github/docs/blob/main/content/actions/reference/workflows-and-actions/dependency-caching.md)

**Misconceptions**
- "Secrets are always masked in logs." Not when transformed or structured. — [secure use](https://github.com/github/docs/blob/main/content/actions/reference/security/secure-use.md)
- "`pull_request_target` is just `pull_request` with secrets." It runs base-branch code with full trust. Checking out the PR head turns it into a pwn request. — [pull_request_target guide](https://github.com/github/docs/blob/main/content/actions/reference/security/securely-using-pull_request_target.md)
- "`@v4` is a fixed version." Tags can be moved, and that is exactly how tj-actions was exploited. — [lockfiles](https://github.com/github/docs/blob/main/content/actions/concepts/security/workflow-dependency-lockfiles.md); [CISA (search)](https://www.cisa.gov/news-events/alerts/2025/03/18/supply-chain-compromise-third-party-github-action-cve-2025-30066)
- "OIDC needs a cloud secret too." No long-lived cloud secret is stored. — [OIDC concepts](https://github.com/github/docs/blob/main/content/actions/concepts/security/openid-connect.md)
- "`id-token: write` grants write access." It only allows requesting the JWT. — [OIDC reference](https://github.com/github/docs/blob/main/content/actions/reference/security/oidc.md)

**Exercises**
- Q6 GHA #5 (script injection), #7 (pinning or lockfile).
- Set `permissions: {}` at the top and add back only what is needed.
- Create a `production` environment with a required reviewer in a public repo.
- Publish an image to GHCR with `GITHUB_TOKEN` (`packages: write`). — [github/docs: publish Docker images](https://github.com/github/docs/blob/main/content/actions/tutorials/publish-packages/publish-docker-images.md)
- OIDC to a cloud provider is optional, because free and local practice is limited. See Gaps.

**Resources**
- [github/docs: Secure use reference](https://github.com/github/docs/blob/main/content/actions/reference/security/secure-use.md)
- [github/docs: Securely using pull_request_target](https://github.com/github/docs/blob/main/content/actions/reference/security/securely-using-pull_request_target.md)
- [github/docs: Script injections](https://github.com/github/docs/blob/main/content/actions/concepts/security/script-injections.md)
- [github/docs: OpenID Connect](https://github.com/github/docs/blob/main/content/actions/concepts/security/openid-connect.md)
- [github/docs: Workflow dependency lockfiles](https://github.com/github/docs/blob/main/content/actions/concepts/security/workflow-dependency-lockfiles.md)
- [GitHub Security Lab: Preventing pwn requests (cited in docs)](https://securitylab.github.com/resources/github-actions-preventing-pwn-requests/)
- [CISA alert on tj-actions/changed-files (search)](https://www.cisa.gov/news-events/alerts/2025/03/18/supply-chain-compromise-third-party-github-action-cve-2025-30066)
- [Socket: actions/checkout blocks pull_request_target checkouts (search)](https://socket.dev/blog/github-actions-checkout-blocks-pull-request-target-checkouts)

### Inferences
- **Suggested additions to the existing course.** These are the 2025–2026 changes most likely missing from older material:
  1. Engine 29's containerd store and `image ls` tree view (Docker L2).
  2. Free DHI and `docker debug` (Docker L6).
  3. Compose v5 naming and dropping `version:` (Docker L5).
  4. The dollar-based Actions allowance and arm64 runners in private repos (GHA L1–L2).
  5. `queue: max` concurrency (GHA L4).
  6. checkout v7, the `pull_request_target` default policy, read-only cache for untrusted triggers, and lockfiles (GHA L5).
- **Cross-course thread.** "Content addressing beats mutable names" ties together image digests (Docker L2), SHA-pinned actions and lockfiles (GHA L5), and artifact digests (GHA L3). One recurring analogy (branch name vs commit SHA) can carry all three.
- **Apple Silicon thread.** The architecture mismatch shows up in Docker L1, L2 and L6 (emulation, indexes), in act on M-series (GHA L2), and in arm64 runners (GHA L3). A small "architectures" sidebar would serve all of them.

### Gaps
- **Video channels.** youtube.com could not be opened. Channel names come only from search titles and summaries. The TechWorld with Nana GitHub Actions video is from 2020 and the Bret Fisher DockerCon talk from 2017, so both are dated. I found no official Docker or GitHub YouTube channel videos, and none from DevOps Toolkit (Viktor Farcic) or KodeKloud, within the search budget.
- **Not researched in this pass:**
  - CMD vs ENTRYPOINT, signal handling, `HEALTHCHECK` in Dockerfiles, and `.dockerignore` specifics.
  - Compose profiles, multiple Compose files and `include`.
  - GitHub artifact attestations in depth.
  - Free, local practice for OIDC. It needs a cloud account, so it may not be fully free or local.
- **Fresh-install defaults.** Whether Docker Desktop for Mac 4.97 uses the containerd image store by default on upgrade (as opposed to fresh install) was not checked. The multi-platform doc says Desktop uses it "by default".
