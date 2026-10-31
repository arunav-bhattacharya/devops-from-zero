from common import lab, svg, box, arrow, line, cap

diagram = svg(200, "Multi-stage image: source code goes into a JDK 21 build stage that uses a Gradle cache mount, produces bin and lib, and only those are copied into a JRE 21 run stage", "".join([
    box(12, 44, 112, 40, "bx", "source code"),
    box(148, 44, 128, 40, "bxt", "build: JDK 21"),
    box(300, 44, 96, 40, "bxg", "bin + lib"),
    box(420, 44, 112, 40, "bxo", "run: JRE 21"),
    arrow(126, 64, 145, 64),
    arrow(278, 64, 297, 64),
    arrow(398, 64, 417, 64),
    cap(212, 30, "stage 1"),
    cap(476, 30, "stage 2"),
    cap(348, 104, "app/build/install"),
    cap(476, 104, "the image you ship"),
    box(152, 144, 120, 40, "bxp", "Gradle cache"),
    line(212, 142, 212, 86, dashed=True),
    cap(222, 120, "cache mount", "start"),
]))

L = {
    "id": "d24",
    "title": "Fast builds, CI and containers for JVM apps",
    "minutes": 50,
    "goal": "By the end you can explain and use Gradle's caches, run the build in GitHub Actions with setup-gradle, and package a JVM app in a small, non-root image with sensible memory settings.",
    "guess": {
        "q": "The build cache is on. You run `./gradlew clean build`. What happens to `compileKotlin`?",
        "options": [
            "It compiles again, since clean deleted its output",
            "Gradle copies its output back and marks it FROM-CACHE",
            "It is UP-TO-DATE, because the source did not change",
            "It fails until you turn the build cache off",
        ],
        "answer": 1,
        "why": "`clean` deleted the outputs, so the task is not up to date. But its inputs match a stored cache entry, so Gradle restores the outputs instead of compiling.",
    },
    "terms": [
        {"term": "Build cache", "plain": "A store of task outputs, keyed by a hash of each task's inputs, that any later build with the same inputs can reuse."},
        {"term": "Configuration cache", "plain": "A saved task graph that lets a repeat run skip the initialization and configuration phases."},
        {"term": "Gradle Daemon", "plain": "A background JVM that Gradle keeps running between builds, so each build starts faster."},
        {"term": "Toolchain", "plain": "The JDK version a build asks for to compile and test, chosen separately from the JDK that runs Gradle."},
        {"term": "Compile avoidance", "plain": "Not recompiling a project when a dependency changed only inside function bodies, not in its public API."},
        {"term": "Build Scan", "plain": "A web report of one build, with task timings, tests and dependencies, published to a Develocity server."},
        {"term": "Jib", "plain": "A Gradle and Maven plugin from Google that builds container images for JVM apps without a Dockerfile."},
        {"term": "MaxRAMPercentage", "plain": "A JVM flag that sets the largest heap as a percentage of the memory the container may use."},
    ],
    "sections": [
        {
            "h": "Four ways Gradle skips work",
            "body": (
                "A slow build costs you on every run, on your laptop and on every CI job. Gradle's answer is to avoid repeating work, and it has four separate tricks. Keep them apart in your head:\n\n"
                "- Up-to-date checks skip a task whose inputs and outputs did not change since the last run in the same folder (Day 22).\n"
                "- The build cache copies a task's outputs from an earlier run anywhere, even in another folder or on another machine, when the inputs match.\n"
                "- The configuration cache skips running the build scripts when they did not change.\n"
                "- The daemon keeps a warm JVM between builds, so Gradle itself starts fast.\n\n"
                "The Kotlin plugin adds compile avoidance on top. We changed `greeting` in three ways and watched `app`:\n\n"
                "1. Add a comment: only `:greeting:compileKotlin` ran. It produced the same class files, so the jar and everything in `app` stayed UP-TO-DATE.\n"
                "2. Change a function body: the `greeting` jar and both test tasks ran, but `:app:compileKotlin` stayed UP-TO-DATE. The ABI (the public signatures other code compiles against) had not changed.\n"
                "3. Add a public function: now `:app:compileKotlin` ran too.\n\n"
                "So a change behind a stable public API does not ripple through the build. That is one more reason to split code into projects and to prefer `implementation`."
            ),
            "refs": [
                {"title": "Gradle docs: Improve the performance of Gradle builds", "url": "https://docs.gradle.org/current/userguide/performance.html", "kind": "docs"},
                {"title": "Understanding Gradle #23: caching (Jendrik Johannes)", "url": "https://www.youtube.com/watch?v=nHb0kIcTrFE", "kind": "watch"},
            ],
        },
        {
            "h": "The build cache and the configuration cache",
            "body": (
                "Turn the **build cache** on with `org.gradle.caching=true` in `gradle.properties`. Before a cacheable task runs, Gradle hashes all its inputs into a cache key. If the cache already holds outputs for that key, Gradle copies them in and prints `FROM-CACHE`. The folder path is not part of the key, so a fresh clone in another folder gets hits too. A fresh clone of hello-jvm on the same laptop built with `20 actionable tasks: 8 executed, 12 from cache`.\n\n"
                "The local cache lives in `~/.gradle/caches/build-cache-1`. Many teams also run a remote cache, an HTTP server that every build can read. The usual setup is that CI writes to it and laptops only read. Pull main in the morning, and most of it is already compiled. Develocity, Gradle's commercial server, is one common choice.\n\n"
                "The configuration cache is a different thing. It stores the task graph from Day 22's first two phases, keyed by your build files and the tasks you asked for. Gradle 9 calls it the preferred mode and plans to turn it on by default in Gradle 10. Two things to know:\n\n"
                "- Some plugins are not compatible yet. They fail with `Invocation of 'Task.project' ... is unsupported with the configuration cache`, and `--no-configuration-cache` turns the cache off for one run.\n"
                "- Entries can hold values from your build, including secrets, so treat the project's `.gradle` folder as private.\n"
                "- A miss is only slower, never wrong: Gradle runs the scripts again and stores a new entry."
            ),
            "refs": [
                {"title": "Gradle docs: Build cache", "url": "https://docs.gradle.org/current/userguide/build_cache.html", "kind": "docs"},
                {"title": "Gradle docs: Adopting the configuration cache", "url": "https://docs.gradle.org/current/userguide/configuration_cache_adoption.html", "kind": "docs"},
            ],
        },
        {
            "h": "The daemon, parallel builds and toolchains",
            "body": (
                "The daemon is the background JVM behind `./gradlew`. The first build of the day starts one, which is why it is the slowest. Later builds reuse it, with classes already loaded and code already JIT-compiled. It stops after three idle hours. `./gradlew --status` lists daemons and `./gradlew --stop` stops them, the classic fix when builds act strangely after a JDK change. In CI, setup-gradle stops them at the end of a job that saves the cache.\n\n"
                "`org.gradle.parallel=true` lets Gradle run tasks from different projects at the same time. hello-jvm is too small to notice. A build with dozens of projects can finish much sooner, because many projects only depend on a few others.\n\n"
                "A toolchain separates the JDK that compiles your code from the JDK that runs Gradle. `kotlin { jvmToolchain(21) }` in the convention plugin asks for Java 21:\n\n"
                "1. Gradle first looks for an installed JDK 21 (`./gradlew -q javaToolchains` lists what it found).\n"
                "2. If there is none, the foojay plugin in `settings.gradle.kts` downloads one.\n"
                "3. Compiling and testing then use that JDK, whatever `java -version` says in your terminal.\n\n"
                "So your laptop can run Gradle on a newer Java and still compile for 21, and CI compiles with exactly the same version. This also explains the \"works in IntelliJ, fails in the terminal\" puzzle: there are two JDKs, and only one of them compiles your code."
            ),
            "refs": [
                {"title": "Gradle docs: Toolchains for JVM projects", "url": "https://docs.gradle.org/current/userguide/toolchains.html", "kind": "docs"},
                {"title": "Kotlin docs: Configure a Gradle project (jvmToolchain)", "url": "https://kotlinlang.org/docs/gradle-configure-project.html", "kind": "docs"},
            ],
        },
        {
            "h": "Trust: checksums, locking and Build Scans",
            "body": (
                "Speed is half the job. The other half is knowing exactly what went into a build. Gradle has three tools for that, and each answers a different question:\n\n"
                "- Is this the right Gradle? The wrapper's `distributionSha256Sum` refuses a download that does not match. We broke one character on purpose and got `Verification of Gradle distribution failed!`.\n"
                "- Are these the same versions as last week? Dependency locking writes the exact resolved version of every library to `gradle.lockfile`. Turn it on with `dependencyLocking { lockAllConfigurations() }`, run `./gradlew dependencies --write-locks`, and commit the file. A new version then fails the build, for example `Resolved 'org.opentest4j:opentest4j:1.3.0' which is not part of the dependency lock state`, until you update the lock on purpose.\n"
                "- Are these the same bytes? Dependency verification keeps a SHA-256 checksum of every downloaded file in `gradle/verification-metadata.xml`. Create it with `./gradlew --write-verification-metadata sha256 help`. A swapped jar then fails the build.\n\n"
                "When a build is slow or flaky, a Build Scan shows why. `./gradlew build --scan` uploads a report of the run, with task timings, test results and the dependency graph, and prints a link. The free service is scans.gradle.com. It asks you to accept its terms first, and your build data goes to Gradle's servers, so keep it for open code. Companies run their own Develocity server for private code, and since Gradle 9.5 `--develocity-url` points a build at one without editing it."
            ),
            "refs": [
                {"title": "Gradle docs: Locking versions", "url": "https://docs.gradle.org/current/userguide/dependency_locking.html", "kind": "docs"},
                {"title": "Gradle docs: Verifying dependencies", "url": "https://docs.gradle.org/current/userguide/dependency_verification.html", "kind": "docs"},
            ],
        },
        {
            "h": "Gradle in GitHub Actions",
            "body": (
                "In CI you run the same command as on your laptop, `./gradlew build`. The workflow only prepares the runner, and `.github/workflows/jvm-ci.yml` does that in two steps:\n\n"
                "1. `actions/setup-java` installs JDK 21, so the toolchain finds it and nothing extra is downloaded.\n"
                "2. `gradle/actions/setup-gradle` does the Gradle work. It checks `gradle-wrapper.jar` against the checksums of real Gradle releases, so a tampered wrapper fails. It caches downloaded libraries, the wrapper's Gradle and the local build cache between runs. And it writes a Job Summary listing every Gradle command and its result.\n\n"
                "Three details save you pain. The cache is written only from the default branch; other branches only read it. Do not also turn on `cache: gradle` in setup-java or add an `actions/cache` step for `~/.gradle`, because they get in the way of setup-gradle. And since CI runs `./gradlew`, it reads the same `gradle.properties`, so the build cache and configuration cache work there too.\n\n"
                "Version 6 of setup-gradle changed the licensing. The default cache provider is closed-source: free for public repositories, a free preview for private ones, with paid tiers planned for large companies. To stay fully open source, set `cache-provider: basic`, an MIT-licensed provider built on `actions/cache`. hello-jvm's workflow has that line ready, commented out, for private repositories."
            ),
            "refs": [
                {"title": "setup-gradle documentation (gradle/actions)", "url": "https://github.com/gradle/actions/blob/main/docs/setup-gradle.md", "kind": "docs"},
                {"title": "gradle/actions: distribution and licensing", "url": "https://github.com/gradle/actions/blob/main/DISTRIBUTION.md", "kind": "read"},
            ],
        },
        {
            "h": "A Dockerfile for a JVM app",
            "body": (
                "The image needs a JRE and your jars, nothing more. The JDK, Gradle and the Kotlin compiler are build tools. That is the multi-stage pattern from Day 16, and hello-jvm's Dockerfile has two stages:\n\n"
                "1. The build stage starts from `eclipse-temurin:21-jdk` and runs `./gradlew :app:installDist`. That task leaves `bin/app` (a start script) and `lib/` (every jar) in `app/build/install/app`.\n"
                "2. The run stage starts from `eclipse-temurin:21-jre`, copies only that folder, adds a non-root user and a healthcheck, and starts `/app/bin/app`.\n\n"
                "Layer order matters, as on Day 13. The wrapper files are copied and run first, so the layer that downloads Gradle (about 170 MB) stays cached until you change the Gradle version. The build line also uses a BuildKit cache mount: `RUN --mount=type=cache,target=/root/.gradle/caches`. That folder of downloaded libraries survives between builds, even when the layer itself has to rerun after a code change. In our test, the first build downloaded everything; after a one-line change in `Main.kt`, the whole image rebuilt in 25 seconds with no downloads.\n\n"
                "Two more things. The cache mount lives in your local builder, so a fresh CI runner starts with it empty; `cache-from: type=gha` still saves the Gradle layer. And on an Apple Silicon Mac, `docker build` makes an arm64 image. Both temurin images ship amd64 and arm64 variants, so add `--platform linux/amd64` when the image must run on amd64 servers."
            ),
            "refs": [
                {"title": "Docker docs: Optimize cache usage in builds (cache mounts)", "url": "https://docs.docker.com/build/cache/optimize/", "kind": "docs"},
                {"title": "Docker docs: Multi-stage builds", "url": "https://docs.docker.com/build/building/multi-stage/", "kind": "docs"},
            ],
        },
        {
            "h": "JVM memory in containers, and images without a Dockerfile",
            "body": (
                "The JVM reads the container's memory limit and sizes its heap from it. By default the largest heap is only 25% of that limit. We checked in a 512 MB container: `MaxHeapSize` was 134217728 bytes (128 MB). With `-XX:MaxRAMPercentage=75.0` it became 402653184 (384 MB). The Dockerfile sets that flag in `JAVA_OPTS`, which the start script passes to `java`. Stay well below 100%: threads, class metadata and the JIT need memory outside the heap. If the total crosses the limit, the kernel kills the container (Day 35 covers memory limits in Kubernetes).\n\n"
                "You do not always need a Dockerfile:\n\n"
                "- Jib is a Gradle plugin that builds the image itself, with separate layers for dependencies and for your classes. `jibDockerBuild` loads the image into Docker, and `jib` pushes to a registry with no Docker at all. By default it uses an `eclipse-temurin` JRE base and builds for amd64 only.\n"
                "- Spring Boot's Gradle plugin has a `bootBuildImage` task that builds an image with Cloud Native Buildpacks.\n"
                "- Quarkus has container-image extensions (Jib, Docker, Podman, Buildpacks) that build the image as part of the Quarkus build.\n\n"
                "Jib has a catch today. Version 3.5.4 does not work with the configuration cache, so you run it with `--no-configuration-cache`, and Gradle warns that the build will break on Gradle 10. For learning, the Dockerfile wins, because you can see every step. At work, use what your framework and platform team already use."
            ),
            "refs": [
                {"title": "JVMs in containers: best practices (David Delabassee)", "url": "https://www.youtube.com/watch?v=QCpMoQsZTa0", "kind": "watch"},
                {"title": "Jib Gradle plugin README", "url": "https://github.com/GoogleContainerTools/jib/tree/master/jib-gradle-plugin", "kind": "docs"},
                {"title": "Spring Boot docs: Packaging OCI images (bootBuildImage)", "url": "https://docs.spring.io/spring-boot/gradle-plugin/packaging-oci-image.html", "kind": "docs"},
            ],
        },
    ],
    "analogy": (
        "The build cache works like a coat check. When a task finishes, Gradle hangs its outputs on a hook and keeps the ticket: a fingerprint of everything that went in. "
        "When the same ticket comes up again, in any folder or on any machine that shares the cloakroom, Gradle hands back the coat instead of making a new one. "
        "Where it breaks: a coat check returns your own coat, while the build cache happily gives you outputs that another build made. That is safe only because the ticket covers every input."
    ),
    "diagram": diagram,
    "diagram_caption": "The JDK, Gradle and its cache stay in stage 1. Only bin/ and lib/ reach the JRE image you ship.",
    "worked": {
        "title": "Watch each speed-up, then put the JVM in a box",
        "steps": [
            {
                "say": "Start cold: delete the outputs and switch the build cache off for one run. Every task does its work.",
                "code": "$ ./gradlew clean build --no-build-cache\n...\nBUILD SUCCESSFUL in 7s\n13 actionable tasks: 13 executed",
                "lang": "console",
            },
            {
                "say": "Same command with the cache on, as hello-jvm's `gradle.properties` sets it. `clean` deleted the outputs, but the inputs match stored entries, so compiling and testing come back FROM-CACHE. The jars and zips are rebuilt, because copying files is cheaper than caching them.",
                "code": "$ ./gradlew clean build\n> Task :greeting:compileKotlin FROM-CACHE\n> Task :app:compileKotlin FROM-CACHE\n> Task :greeting:compileTestKotlin FROM-CACHE\n> Task :greeting:test FROM-CACHE\n> Task :app:compileTestKotlin FROM-CACHE\n> Task :app:test FROM-CACHE\nBUILD SUCCESSFUL in 1s\n13 actionable tasks: 7 executed, 6 from cache",
                "lang": "console",
            },
            {
                "say": "Clone the repository into a second folder and build there. The path is not part of the cache key, so even the convention plugin in build-logic comes from the cache. A remote cache does the same across machines.",
                "code": "$ git clone ~/code/hello-jvm /tmp/hello-jvm-2 && cd /tmp/hello-jvm-2\n$ ./gradlew build\n> Task :build-logic:compileKotlin FROM-CACHE\n> Task :greeting:compileKotlin FROM-CACHE\n> Task :app:compileKotlin FROM-CACHE\n> Task :greeting:test FROM-CACHE\n> Task :app:test FROM-CACHE\n...\nBUILD SUCCESSFUL in 24s\n20 actionable tasks: 8 executed, 12 from cache",
                "lang": "console",
            },
            {
                "say": "Now the JVM in a container. Give a plain JRE container 512 MB and print the heap limit, first with defaults, then with the flag from the Dockerfile. 134217728 bytes is 128 MB (25%); 402653184 is 384 MB (75%).",
                "code": "$ docker run --rm -m 512m eclipse-temurin:21-jre java -XX:+PrintFlagsFinal -version | grep -E ' MaxHeapSize| MaxRAMPercentage'\n   size_t MaxHeapSize                              = 134217728                                 {product} {ergonomic}\n   double MaxRAMPercentage                         = 25.000000                                 {product} {default}\n$ docker run --rm -m 512m eclipse-temurin:21-jre java -XX:MaxRAMPercentage=75.0 -XX:+PrintFlagsFinal -version | grep -E ' MaxHeapSize| MaxRAMPercentage'\n   size_t MaxHeapSize                              = 402653184                                 {product} {ergonomic}\n   double MaxRAMPercentage                         = 75.000000                                 {product} {command line}",
                "lang": "console",
            },
            {
                "say": "Try Jib as the Dockerfile-free option. Load the plugin once in a root `build.gradle.kts` with `apply false`: without that line Gradle warned that the Kotlin plugin was loaded multiple times in different subprojects. Then add `alias(libs.plugins.jib)` to app's plugins block, plus this block.",
                "code": "// build.gradle.kts (root)\nplugins { alias(libs.plugins.jib) apply false }\n\n// app/build.gradle.kts\njib {\n    from { image = \"eclipse-temurin:21-jre\" }\n    to { image = \"hello-jvm:jib\" }\n    container {\n        ports = listOf(\"8080\")\n        jvmFlags = listOf(\"-XX:MaxRAMPercentage=75.0\")\n        user = \"10001\"\n    }\n}",
                "lang": "text",
            },
            {
                "say": "Run it. With the configuration cache on, Jib fails, because its task reads `project` while it runs (the Day 22 error). Turn the cache off for this one command and it works, with a warning about Gradle 10.",
                "code": "$ ./gradlew :app:jibDockerBuild\n> Task :app:jibDockerBuild FAILED\n...\n> Invocation of 'Task.project' by task ':app:jibDockerBuild' at execution time is unsupported with the configuration cache.\n$ ./gradlew :app:jibDockerBuild --no-configuration-cache\nContainerizing application to Docker daemon as hello-jvm:jib...\n...\nBuilding dependencies layer...\nBuilding project dependencies layer...\nBuilding classes layer...\nBuilding jvm arg files layer...\n...\nContainer entrypoint set to [java, -XX:MaxRAMPercentage=75.0, -cp, @/app/jib-classpath-file, hello.app.MainKt]\nBuilt image to Docker daemon as hello-jvm:jib\nDeprecated Gradle features were used in this build, making it incompatible with Gradle 10.\nBUILD SUCCESSFUL in 21s",
                "lang": "console",
            },
        ],
    },
    "code": [
        {"lang": "dockerfile", "title": "Dockerfile", "src": lab("Dockerfile"), "run": "docker build --build-arg APP_VERSION=1.0.0 -t hello-jvm:1.0.0 . && docker run --rm -p 8080:8080 -m 512m hello-jvm:1.0.0"},
        {"lang": "text", "title": ".dockerignore", "src": lab(".dockerignore"), "run": "docker build -t hello-jvm:1.0.0 ."},
        {"lang": "ini", "title": "gradle.properties (adds the build cache and parallel execution)", "src": lab("gradle.properties"), "run": "./gradlew clean build"},
        {"lang": "ini", "title": "gradle/libs.versions.toml (adds the optional Jib plugin)", "src": lab("gradle/libs.versions.toml"), "run": "./gradlew build"},
        {"lang": "yaml", "title": ".github/workflows/jvm-ci.yml", "src": lab(".github/workflows/jvm-ci.yml"), "run": "git add .github && git commit -m 'Add JVM CI' && git push"},
    ],
    "commands": [
        {"cmd": "./gradlew clean build", "what": "Rebuild from nothing; with the build cache on, look for FROM-CACHE."},
        {"cmd": "./gradlew clean build --no-build-cache", "what": "Rebuild without the build cache, to compare times."},
        {"cmd": "./gradlew build --no-configuration-cache", "what": "Run once without the configuration cache, for a plugin that does not support it."},
        {"cmd": "./gradlew --status", "what": "List the Gradle daemons and whether they are busy or idle."},
        {"cmd": "./gradlew --stop", "what": "Stop all daemons of this Gradle version."},
        {"cmd": "./gradlew -q javaToolchains", "what": "Show the JDKs Gradle found and whether it may download more."},
        {"cmd": "./gradlew build --scan", "what": "Publish a Build Scan of this build to scans.gradle.com, after accepting the terms."},
        {"cmd": "./gradlew dependencies --write-locks", "what": "Write gradle.lockfile with the exact versions (needs dependencyLocking turned on)."},
        {"cmd": "./gradlew --write-verification-metadata sha256 help", "what": "Create gradle/verification-metadata.xml with a checksum for every dependency."},
        {"cmd": "docker build --build-arg APP_VERSION=1.0.0 -t hello-jvm:1.0.0 .", "what": "Build the two-stage image with a version baked in."},
        {"cmd": "docker run -d --name hello-jvm -p 8080:8080 -m 512m hello-jvm:1.0.0", "what": "Run it in the background with a 512 MB memory limit."},
        {"cmd": "docker build --platform linux/amd64 -t hello-jvm:1.0.0-amd64 .", "what": "On an Apple Silicon Mac, build an image for amd64 servers."},
        {"cmd": "docker exec hello-jvm sh -c 'java $JAVA_OPTS -XX:+PrintFlagsFinal -version | grep -w MaxHeapSize'", "what": "Print the heap limit the JVM picks inside the running container."},
        {"cmd": "./gradlew :app:jibDockerBuild --no-configuration-cache", "what": "Build the image with Jib instead of a Dockerfile (Jib 3.5.4 needs the flag)."},
        {"cmd": "openssl rand -base64 16", "what": "Make a key for setup-gradle's cache-encryption-key secret."},
    ],
    "mistake": (
        "Writing `./gradlew clean build` in CI to be safe, and adding `actions/cache` next to setup-gradle. `clean` throws away the outputs the caches exist to reuse, and two caching systems on one folder get in each other's way. "
        "Run `./gradlew build` and let setup-gradle do the caching. If you distrust a cache hit, the real fix is a task input that is missing from the build logic."
    ),
    "real_world": (
        "At Paylane (a made-up payments company), CI on main writes to a remote build cache and developers' laptops only read from it, so a fresh clone of main is mostly FROM-CACHE. "
        "Every service image uses the same two-stage Dockerfile pattern with `MaxRAMPercentage` set, and memory limits are tuned with a load test, not guessed."
    ),
    "task": {
        "title": "Ship hello-jvm in a container, with CI",
        "steps": [
            "Add `org.gradle.caching=true` and `org.gradle.parallel=true` to `gradle.properties`. Run `./gradlew clean build` twice and find the FROM-CACHE lines in the second run.",
            "Create the `Dockerfile` and `.dockerignore` from Files.",
            "Build `hello-jvm:1.0.0` with `APP_VERSION=1.0.0` and note how long it takes. Change one line in `Main.kt`, rebuild, and compare.",
            "Run the image with a 512 MB limit on port 8080. Call `/` and `/healthz`, wait for `docker ps` to say healthy, and check the user with `docker exec <name> id`.",
            "Print the heap limit inside the container and check it is about 75% of 512 MB.",
            "Stop the container and check how long `docker stop` takes and which exit code it leaves.",
            "Add `.github/workflows/jvm-ci.yml`, push, and open the run on GitHub. Read the Job Summary that setup-gradle wrote.",
            "Push a second, small commit and compare the run time of the build job with the first run.",
        ],
        "hints": [
            "`docker stop` should take well under a second and leave exit code 143 (SIGTERM). If it takes 10 seconds, check that ENTRYPOINT uses the exec form (Day 13).",
            "The first CI run starts with an empty cache, so it is always the slowest. The cache is saved only from main.",
        ],
        "done_when": "`docker ps` shows the container as healthy, `curl localhost:8080` reports version 1.0.0, and the jvm-ci workflow is green on GitHub.",
    },
    "explain_back": {
        "prompt": "Explain the difference between the build cache and the configuration cache in 3 to 4 sentences. Say what each one stores and what a hit looks like in the output.",
        "answer": (
            "The build cache stores task outputs, such as compiled classes and test results, under a key made from a hash of the task's inputs. When another build has the same inputs, even in another folder or on CI, Gradle copies the outputs back and marks the task FROM-CACHE. "
            "The configuration cache stores the task graph that the build scripts produced, so a repeat run can skip running the scripts. A hit prints `Reusing configuration cache.` at the start, and tasks then run or are skipped as usual."
        ),
    },
    "recap": [
        "Up-to-date checks, the build cache, the configuration cache and the daemon each skip a different kind of work.",
        "Compile avoidance means a change inside function bodies does not recompile the projects that depend on yours.",
        "A toolchain picks the JDK that compiles your code, separate from the JDK that runs Gradle.",
        "In GitHub Actions, use setup-java plus setup-gradle and nothing else for Gradle caching; set `cache-provider: basic` to stay fully open source.",
        "Build in a JDK stage, ship `installDist` output on a JRE image, run as non-root, and set `MaxRAMPercentage` (the default heap is 25%).",
        "Jib, `bootBuildImage` and Quarkus extensions build images without a Dockerfile; Jib 3.5.4 needs `--no-configuration-cache`.",
    ],
    "check": [
        {
            "q": "On a fresh clone, a colleague's build shows `> Task :core:compileKotlin FROM-CACHE`. What happened?",
            "options": [
                "Its inputs matched a stored cache entry",
                "Its old outputs were still in build/",
                "Gradle reused last run's task graph",
                "It failed, so old classes were used",
            ],
            "answer": 0,
            "why": "FROM-CACHE means the inputs hashed to a key that the build cache already had, so Gradle copied the outputs in instead of compiling.",
        },
        {
            "q": "A JVM service runs with `docker run -m 1g` and no memory flags at all. Roughly how large can its heap grow?",
            "options": [
                "About 1 GB, the whole limit",
                "About 750 MB, three quarters",
                "About 256 MB, a quarter",
                "As much as the host has free",
            ],
            "answer": 2,
            "why": "The JVM sees the container limit and by default caps the heap at 25% of it, which is why images set MaxRAMPercentage.",
        },
        {
            "q": "A workflow uses setup-java with `cache: gradle` and also setup-gradle. Caching behaves oddly. What should you change?",
            "options": [
                "Add an `actions/cache` step for `~/.gradle`",
                "Run `./gradlew clean build` on every push",
                "Add `--no-daemon` to every Gradle command",
                "Remove `cache: gradle` from setup-java",
            ],
            "answer": 3,
            "why": "setup-gradle should own the Gradle cache; a second mechanism on the same folder interferes with it.",
        },
    ],
    "interview": [
        {
            "q": "A Gradle build in CI is slow. How do you speed it up?",
            "a": "First I look at which tasks actually ran, using the console output or a Build Scan. Then I make sure caching works: setup-gradle restoring Gradle User Home, the build cache on, ideally a remote cache that CI writes and laptops read, and no `clean` in the CI command. I turn on the configuration cache and parallel execution, and fix plugins that break them. If one project dominates, I look at compile avoidance: splitting modules and preferring `implementation` stops changes from rippling.",
        },
        {
            "q": "How do you package a JVM service as a container image?",
            "a": "With a multi-stage Dockerfile: a JDK stage runs the Gradle wrapper and `installDist`, and a JRE stage gets only the start script and jars. I copy the wrapper first so the Gradle download stays in a cached layer, and use a BuildKit cache mount for dependencies. The run stage uses a non-root user, an exec-form ENTRYPOINT so SIGTERM reaches the JVM, and `-XX:MaxRAMPercentage` so the heap fits the container limit. Jib or Spring Boot's `bootBuildImage` are good alternatives when a team prefers no Dockerfile.",
        },
        {
            "q": "What is the difference between dependency locking and dependency verification?",
            "a": "Locking records which versions were resolved, in a `gradle.lockfile`, so a build fails if the graph changes until someone updates the lock. Verification records checksums or signatures of the files themselves, in `verification-metadata.xml`, so a tampered or swapped jar fails the build. Locking guards against drift and surprise upgrades; verification guards against supply-chain tampering. You can use both together.",
        },
    ],
    "deeper": {
        "minutes": 12,
        "body": (
            "The cache mount that made local rebuilds fast does not help much on a fresh CI runner. Each runner starts with an empty BuildKit cache, so the build stage downloads every library again whenever the source changed. In our test the mount held about 900 MB after one build: libraries, the Kotlin compiler, transformed jars and the local build cache. `cache-from: type=gha` brings back image layers, including the 170 MB Gradle layer, but not the contents of a cache mount.\n\n"
            "Teams handle this in one of three ways:\n\n"
            "1. Accept it. For a small service, the image job takes a minute or two longer than it could. hello-jvm's workflow does this, because the Dockerfile stays simple and the same everywhere.\n"
            "2. Build outside Docker, and only package inside it. The build job runs `./gradlew build :app:installDist` with setup-gradle's warm cache, and a one-stage Dockerfile copies `app/build/install/app` onto the JRE image. The trade-off is that the image now depends on what the runner built, so laptops and CI must use the same steps.\n"
            "3. Use Jib in CI. It runs inside Gradle, so it shares setup-gradle's cache, and `jib` pushes without a Docker daemon. Today that means `--no-configuration-cache` for that step.\n\n"
            "The configuration cache has a CI angle too. Gradle 9.1 added a read-only mode, `-Dorg.gradle.configuration-cache.read-only=true`, meant for builds that should use entries but not write them, such as pull request builds. And because entries can contain secrets, setup-gradle can encrypt them in the GitHub Actions cache with a key you give it. Make one with `openssl rand -base64 16`, store it as a repository secret, and pass it as `cache-encryption-key: ${{ secrets.GRADLE_ENCRYPTION_KEY }}`.\n\n"
            "Finally, the remote build cache is where large teams win the most time. The setup-gradle documentation recommends the usual pattern: CI builds push to the remote cache and switch off the local one, and local builds then read what CI wrote. The same pattern works with Develocity or any other HTTP build cache server."
        ),
    },
    "sources": [
        {"title": "Gradle docs: Build cache", "url": "https://docs.gradle.org/current/userguide/build_cache.html"},
        {"title": "Gradle docs: Configuration cache", "url": "https://docs.gradle.org/current/userguide/configuration_cache.html"},
        {"title": "setup-gradle documentation (gradle/actions)", "url": "https://github.com/gradle/actions/blob/main/docs/setup-gradle.md"},
        {"title": "Quarkus guide: Container images", "url": "https://quarkus.io/guides/container-image/"},
    ],
}
