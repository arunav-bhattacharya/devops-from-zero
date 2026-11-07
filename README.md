# hello-jvm

A small Kotlin web service built with Gradle, for Part 5 of "DevOps, from zero" (Days 22 to 24).
It mirrors hello-devops: `/` returns JSON `{message, version, host, visits}` and `/healthz` returns
`{"status":"ok"}`. It uses the JDK's built-in web server (`com.sun.net.httpserver`), so there is no
web framework to download.

This folder is the finished reference: every file the lessons build, already tested. Use it to check
your work, not to copy.

| Path | Built on |
|---|---|
| `settings.gradle.kts`, `gradle.properties`, `.gitignore`, `.gitattributes` | Day 22 (flags extended on Day 24) |
| `gradlew`, `gradlew.bat`, `gradle/wrapper/*` (the Gradle Wrapper, commit all four) | Day 22 |
| `app/` (the web service, `application` plugin) | Day 22 (split on Day 23) |
| `greeting/` (a library: builds and escapes the JSON) | Day 23 |
| `gradle/libs.versions.toml` (version catalog) | Day 23 (Jib entry added on Day 24) |
| `build-logic/` (included build with the `hello.kotlin-jvm` convention plugin) | Day 23 |
| `Dockerfile`, `.dockerignore` | Day 24 |
| `.github/workflows/jvm-ci.yml` | Day 24 |

## Run it locally

You need a JDK 17 or newer to run Gradle 9 (`java -version`). The build compiles with Java 21
through a toolchain; if you have no JDK 21, Gradle downloads one (the foojay plugin in settings).

```bash
./gradlew build                 # compile, test and package both projects
./gradlew :app:run              # start the service on port 8080 (Ctrl+C to stop)
curl localhost:8080             # in a second terminal
./gradlew :app:installDist      # bin/ and lib/ in app/build/install/app
app/build/install/app/bin/app   # run it without Gradle
```

Settings come from environment variables: `APP_VERSION` (default `dev`), `GREETING`
(default `Hello, JVM!`) and `PORT` (default `8080`).

## Build the image

```bash
docker build --build-arg APP_VERSION=1.0.0 -t hello-jvm:1.0.0 .
docker run --rm -p 8080:8080 -m 512m hello-jvm:1.0.0
```

Base images: `eclipse-temurin:21-jdk` for the build stage and `eclipse-temurin:21-jre` for the
run stage. Both are official Docker Hub images with `linux/amd64` and `linux/arm64` variants, so
they run natively on an Apple Silicon Mac. On a Mac, `docker build` makes an arm64 image; add
`--platform linux/amd64` (Day 16) when the image must run on amd64 servers. If Docker Hub limits
your pulls, run `docker login` first.

The first build downloads Gradle and every dependency (a few minutes). Later builds reuse the
wrapper layer and the BuildKit cache mount for `~/.gradle/caches`, so a code change rebuilds in
about half a minute.

## Optional: Jib

Day 24 shows Jib, which builds the image from Gradle without a Dockerfile. The catalog already has
the `jib` plugin entry; the lesson shows the lines to add to `app/build.gradle.kts`. Jib 3.5.4 is
not compatible with Gradle's configuration cache, so run it with
`./gradlew :app:jibDockerBuild --no-configuration-cache`.

## CI

`.github/workflows/jvm-ci.yml` runs `./gradlew build` with `gradle/actions/setup-gradle@v6`, which
validates the wrapper jar and caches Gradle's downloads, then builds the image without pushing.
The default cache provider of setup-gradle v6 is free for public repositories. In a private
repository, set `cache-provider: basic` to use the open-source (MIT) provider.

## How this lab was tested

Tested on 2026-10-30 and 2026-10-31 with Gradle 9.8.2 (wrapper), OpenJDK 21 and Docker 29.9 on Linux amd64:
`./gradlew build` (5 tests pass), `:app:run` with curl, `jibDockerBuild --no-configuration-cache`,
the full multi-stage `docker build` and `docker run` (non-root user, healthcheck healthy,
`docker stop` in under a second), and `actionlint` on the workflow. The test machine could not
pull from Docker Hub, so the same images came from `mirror.gcr.io/library/eclipse-temurin`, and
the build stage had three extra test-only lines to trust and use the machine's network proxy.
