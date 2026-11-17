"""Book-voice rewrite of d30 (fifth pass, writer td). Replaces prose fields only."""
from common import load, save, set_list, drop_extras

path, P, L = load(7, "d30")

L["goal"] = ("By the end you can explain and use Gradle's caches, run the build in GitHub Actions with setup-gradle, "
             "and package a JVM app in a small, non-root image with sensible memory settings.")

L["opening"] = """Picture our bakery on its busiest morning. The oven went cold overnight and takes forty minutes to heat. The prep list is written again from scratch, though the orders are the same as yesterday. Each branch makes its own croissant dough, though the main branch made the same dough an hour ago. And the van carries the whole kitchen, mixer included, to deliver one box of bread.

None of these looks serious on its own. Each one costs a few minutes, so nobody fixes it, and together they make every delivery late.

Last time, hello-jvm grew into two projects with libraries from outside, and every fresh build did all of the work again. In this lesson, we'll meet the four ways Gradle skips work and run the build in GitHub Actions with a warm cache. Then we'll pack only the bread: a small image with sensible memory settings. Before we start, make a guess, and keep it in mind."""

L["guess"]["q"] = ("Gradle's build cache, a store of earlier results, is switched on. You run `./gradlew clean build`, which first deletes "
                   "the build folders. What happens to the `compileKotlin` task?")
L["guess"]["why"] = ("`clean` deleted the outputs, so the task is not up to date. But its inputs match a stored cache entry, "
                     "so Gradle restores the outputs instead of compiling.")

set_list(L["terms"], "plain", [
    "A store of task outputs, labelled by a fingerprint of each task's inputs, that any later build with the same inputs can reuse.",
    "A saved task graph that lets a repeat run skip the initialization and configuration phases.",
    "A background JVM that Gradle keeps running between builds, so each build starts faster.",
    "The JDK version a build asks for to compile and test, chosen separately from the JDK that runs Gradle.",
    "Not recompiling a project when a project it uses changed only inside function bodies, not in its public API.",
    "A web report of one build, with task timings, tests and dependencies, published to a Develocity server.",
    "A Gradle and Maven plugin from Google that builds container images for JVM apps without a Dockerfile.",
    "A JVM flag that sets the largest heap as a percentage of the memory the container may use.",
])

S = L["sections"]

S[0]["h"] = "Four ways Gradle skips work"
S[0]["body"] = """Each slow habit in the bakery has a Gradle cure, and Gradle has four separate ways to avoid repeating work. They are easy to mix up, so keep them apart:

- Up-to-date checks skip a task whose inputs and outputs did not change since the last run in the same folder (Day 28).
- The build cache copies a task's outputs from an earlier run anywhere, even in another folder or on another machine, when the inputs match.
- The configuration cache skips running the build scripts when they did not change.
- The daemon keeps a warm JVM between builds, so Gradle itself starts fast.

In bakery terms, they are this morning's sauce still in the pot, a shared fridge that every branch can take from, yesterday's prep list, and an oven kept warm. The JVM, from Day 28, is the program that runs compiled Kotlin and Java code.

The Kotlin plugin adds compile avoidance on top. We changed `greeting`, the library project from last lesson, in three ways and watched `app`:

1. Add a comment: only `:greeting:compileKotlin` ran. It produced the same class files, so the jar and everything in `app` stayed UP-TO-DATE.
2. Change a function body: the `greeting` jar and both test tasks ran, but `:app:compileKotlin` stayed UP-TO-DATE. The ABI had not changed.
3. Add a public function: now `:app:compileKotlin` ran too.

The ABI, short for application binary interface, is the set of public signatures other code compiles against. A signature is a function's name, inputs and result type, without the code inside.

So a change behind a stable public API does not ripple through the build. That is one more reason to split code into projects and to prefer `implementation`. Of the four, the build cache saves the most work, so we'll start there."""

S[1]["h"] = "Sharing finished work: the build cache and the configuration cache"
S[1]["body"] = """Turn the build cache on with `org.gradle.caching=true` in `gradle.properties`. Before a cacheable task runs, Gradle hashes all its inputs into a cache key, a label made from their fingerprints. If the cache already holds outputs for that key, Gradle copies them in and prints `FROM-CACHE`.

The folder path is not part of the key, so a fresh clone in another folder gets hits too. A fresh clone of hello-jvm on the same laptop built with `20 actionable tasks: 8 executed, 12 from cache`.

The local cache lives in `~/.gradle/caches/build-cache-1`. Many teams also run a remote cache, an HTTP server that every build can read. That is the shared fridge between branches.

The Gradle docs recommend that CI fills it from clean builds and laptops only read. That way half-finished local changes never reach the shared cache. Pull main in the morning, and most of it is already compiled. Develocity, Gradle's commercial server, is one common choice.

The configuration cache is a different thing. It stores the task graph from Day 28's first two phases, keyed by your build files and the tasks you asked for. Gradle 9 calls it the preferred mode and plans to turn it on by default in Gradle 10. Three things to know:

- Some plugins are not compatible yet. They fail with `Invocation of 'Task.project' ... is unsupported with the configuration cache`, and `--no-configuration-cache` turns the cache off for one run.
- Entries can hold values from your build, including secrets, so treat the project's `.gradle` folder as private.
- A miss is only slower, never wrong: Gradle runs the scripts again and stores a new entry.

Two of the four ways are now covered. The warm oven, and the question of which JDK does the baking, come next."""

S[2]["h"] = "A warm oven, parallel work and the right JDK"
S[2]["body"] = """The daemon is the background JVM behind `./gradlew`. The first build of the day starts one, which is why it is the slowest. Later builds reuse it, with classes already loaded and busy code already turned into fast machine code. It stops after three idle hours.

`./gradlew --status` lists daemons and `./gradlew --stop` stops them, the usual fix when builds act strangely after a JDK change. In CI, setup-gradle stops them at the end of a job that saves the cache.

`org.gradle.parallel=true` lets Gradle run tasks from different projects at the same time, like two bakers at two tables. hello-jvm is too small to notice. A build with dozens of projects can finish much sooner, because many projects only depend on a few others.

A toolchain separates the JDK that compiles your code from the JDK that runs Gradle. The JDK, from Day 28, is the Java toolbox you install. `kotlin { jvmToolchain(21) }` in the convention plugin, the shared setup from last lesson, asks for Java 21:

1. Gradle first looks for an installed JDK 21 (`./gradlew -q javaToolchains` lists what it found).
2. If there is none, the foojay resolver plugin in `settings.gradle.kts` finds one through foojay, a community JDK download service, and downloads it.
3. Compiling and testing then use that JDK, whatever `java -version` says in your terminal.

So your laptop can run Gradle on a newer Java and still compile for 21, and CI compiles with exactly the same version. This also explains the "works in IntelliJ, fails in the terminal" puzzle: there are two JDKs, and only one of them compiles your code. Speed is only half the story, though. You also want to know exactly what went into a build."""

S[3]["h"] = "Knowing exactly what went in: checksums, locks and Build Scans"
S[3]["body"] = """A bakery that sells to a hospital must say exactly which flour went into each loaf. Gradle has three tools for the same job, and each answers a different question:

- Is this the right Gradle? The wrapper checksum answers that.
- Are these the same versions as last week? Dependency locking answers that.
- Are these the same bytes? Dependency verification answers that.

The wrapper's `distributionSha256Sum` refuses a download that does not match. We broke one character on purpose and got `Verification of Gradle distribution failed!`.

Versions can also move without anyone editing a build file: a range such as `1.+` resolves to whatever is newest on the day. Dependency locking stops that. It writes the exact resolved version of every library to `gradle.lockfile`. Turn it on with `dependencyLocking { lockAllConfigurations() }`, run `./gradlew dependencies --write-locks`, and commit the file.

After that, a new version fails the build until you update the lock on purpose. We added one library to `app` and got `Resolved 'org.opentest4j:opentest4j:1.3.0' which is not part of the dependency lock state`.

Dependency verification keeps a SHA-256 checksum, a fingerprint, of every downloaded file in `gradle/verification-metadata.xml`. Create it with `./gradlew --write-verification-metadata sha256 help`, and a swapped jar fails the build.

When a build is slow or flaky, a Build Scan shows why. Run `./gradlew build --scan`, and Gradle uploads a report of the run and prints a link. The report has task timings, test results and the dependency graph.

The free service is scans.gradle.com. It asks you to accept its terms first, and your build data goes to Gradle's servers, so keep it for open code. Companies run their own Develocity server for private code, and since Gradle 9.5 `--develocity-url` points a build at one without editing it. Next, we'll run all of this where it matters most: on a fresh CI runner."""

S[4]["h"] = "Gradle in GitHub Actions"
S[4]["body"] = """In CI you run the same command as on your laptop, `./gradlew build`. CI is the automatic checking from Part 6, and GitHub Actions runs it on a fresh machine, a runner, for every push. The workflow only prepares the runner.

In `.github/workflows/jvm-ci.yml`, `actions/setup-java` installs JDK 21, so the toolchain finds it and downloads nothing. Then `gradle/actions/setup-gradle` does the Gradle work:

- It checks `gradle-wrapper.jar` against the checksums of real Gradle releases, so a tampered wrapper fails. That jar runs on every build, and nobody can review a binary file in a pull request.
- It caches downloaded libraries, the wrapper's Gradle and the local build cache between runs.
- It writes a Job Summary with every Gradle command, its result and any Build Scan links.
- It can publish a Build Scan of every build: set `build-scan-publish: true` and accept the terms of use.

A binary file is one made for machines, not people, so a reviewer cannot read what changed. That cache has rules of its own:

- It is written only from the default branch. Other branches only read it, and by the Day 25 rule every branch can restore what main saved.
- Do not add `cache: gradle` in setup-java or an `actions/cache` step for `~/.gradle`. They conflict with setup-gradle.
- CI reads the same `gradle.properties`, so the build cache and configuration cache work there too.

The second rule is an easy trap, because more caching sounds safer. So does `./gradlew clean build` in CI. On a fresh runner `clean` has nothing to delete, and on a reused machine it throws away outputs Gradle could have skipped. Run `./gradlew build` and let setup-gradle do the caching. If you distrust a cache hit, the real fix is a task input that is missing from the build logic.

The build is fast and trusted now. Next, we'll pack the result for delivery."""

L["aside"] = {
    "title": "Is setup-gradle free to use?",
    "body": "Version 6 of setup-gradle changed the licensing. The default cache provider is closed-source: free for public repositories, a free preview for private ones, with paid tiers planned for large companies. To stay fully open source, set `cache-provider: basic`, an MIT-licensed provider built on `actions/cache`. hello-jvm's workflow has that line ready, commented out, for private repositories.",
    "after": 4,
}

S[5]["h"] = "Packing only the bread: a Dockerfile for a JVM app"
S[5]["body"] = """The van should carry bread, not the mixer. The image you ship needs a JRE and your jars. A JRE, Java Runtime Environment, is the part of the JDK that runs programs, without the tools that build them.

The JDK, Gradle and the Kotlin compiler are only needed to build, so they stay in an earlier stage. That is the multi-stage pattern from Day 22, and hello-jvm's Dockerfile has two stages:

1. The build stage starts from `eclipse-temurin:21-jdk` and runs `./gradlew :app:installDist`. That task leaves `bin/app` (a start script) and `lib/` (every jar) in `app/build/install/app`.
2. The run stage starts from `eclipse-temurin:21-jre`, copies only that folder, adds a non-root user and a healthcheck, and starts `/app/bin/app`.

Eclipse Temurin is a free build of Java, published as Docker images. A non-root user is an ordinary account, so the app does not run with full control of the container.

Layer order matters, as on Day 19. The wrapper files are copied and run first, so the layer that downloads Gradle (about 170 MB) stays cached until you change the Gradle version.

The build line also uses a BuildKit cache mount: `RUN --mount=type=cache,target=/root/.gradle/caches`. That folder of downloaded libraries survives between builds, even when the layer itself has to rerun after a code change. In our test, the first build downloaded everything; after a one-line change in `Main.kt`, the whole image rebuilt in 25 seconds with no downloads.

The cache mount lives in your local builder, so a fresh CI runner starts with it empty; `cache-from: type=gha` still saves the Gradle layer. On an Apple Silicon Mac, `docker build` makes an arm64 image. Both temurin images ship amd64 and arm64 variants, so add `--platform linux/amd64` when the image must run on amd64 servers. One setting inside the image decides how much memory the JVM may take, and its default surprises people."""

S[6]["h"] = "JVM memory in a container, and images without a Dockerfile"
S[6]["body"] = """The heap is the memory where the JVM keeps the program's data. The JVM reads the container's memory limit from its cgroup (Day 17), the kernel feature that sets that limit, and sizes its heap from it. By default the largest heap is only 25% of that limit, like a baker who uses a quarter of the delivery box and leaves the rest empty.

We checked in a 512 MB container: `MaxHeapSize` was 134217728 bytes (128 MB). With `-XX:MaxRAMPercentage=75.0` it became 402653184 (384 MB). The Dockerfile sets that flag in `JAVA_OPTS`, which the start script passes to `java`.

Stay well below 100%. Threads, class metadata and the JIT compiler, which turns busy code into machine code, need memory outside the heap. If the total crosses the limit, the kernel kills the container (Day 43 covers memory limits in Kubernetes).

You do not always need a Dockerfile. Three tools build the image from the build itself:

- Jib, a Gradle and Maven plugin from Google, for any JVM app.
- Spring Boot's `bootBuildImage` task, which uses Cloud Native Buildpacks.
- Quarkus container-image extensions, such as Jib, Docker and Podman.

Spring Boot and Quarkus are popular frameworks, ready-made foundations for writing web services. Jib puts your dependencies and your classes in separate layers, so a code change rebuilds and pushes only the small classes layer (Day 18). The `jibDockerBuild` task loads the image into Docker, and the `jib` task pushes to a registry with no Docker at all. By default it uses an `eclipse-temurin` JRE base and builds for amd64 only.

Jib has a catch today. Version 3.5.4 does not work with the configuration cache, so you run it with `--no-configuration-cache`, and Gradle warns that the build will break on Gradle 10. For learning, the Dockerfile wins, because you can see every step. At work, use what your framework and platform team already use.

This part ends with a fast, trusted build and a small image. It still runs only where you start it by hand. Nothing yet creates the servers or networks it would run on, and Part 8 describes those in code."""

L["closing"] = """We started with a cold oven, a prep list rewritten every morning, branches remaking the same dough, and a van that carried the mixer. Now the daemon keeps the oven warm, the configuration cache keeps the prep list, the build cache shares finished work, and the image carries only a JRE and your jars.

Run `./gradlew clean build` twice in hello-jvm and count the FROM-CACHE lines. Then print the heap limit inside your running container and check it is about 75% of 512 MB.

Next, we'll build the place where images run. How can a few text files describe servers and networks, so a tool creates them the same way every time?"""

drop_extras(L)

set_list(L["worked"]["steps"], "say", [
    "Start cold: delete the outputs and switch the build cache off for one run. Every task does its work.",
    "Same command with the cache on, as hello-jvm's `gradle.properties` sets it. `clean` deleted the outputs, but the inputs match stored entries, so compiling and testing come back FROM-CACHE. The jars and zips are rebuilt, because copying files is cheaper than caching them.",
    "Clone the repository into a second folder and build there. The path is not part of the cache key, so even the convention plugin in build-logic comes from the cache. A remote cache does the same across machines.",
    "Now the JVM in a container. Give a plain JRE container 512 MB and print the heap limit, first with defaults, then with the flag from the Dockerfile. 134217728 bytes is 128 MB (25%); 402653184 is 384 MB (75%).",
    "Try Jib as the Dockerfile-free option. Load the plugin once in a root `build.gradle.kts` with `apply false`: without that line Gradle warned that the Kotlin plugin was loaded multiple times in different subprojects. Then add `alias(libs.plugins.jib)` to app's plugins block, plus this block.",
    "Run it. With the configuration cache on, Jib fails, because its task reads `project` while it runs (the Day 28 error).",
    "Turn the cache off for this one command and it works. Look for the separate layers, the memory flag in the entrypoint, and the warning about Gradle 10.",
])

L["task"]["steps"] = [
    "Add `org.gradle.caching=true` and `org.gradle.parallel=true` to `gradle.properties`. Run `./gradlew clean build` twice and find the FROM-CACHE lines in the second run.",
    "Create the `Dockerfile` and `.dockerignore` from Files.",
    "Build `hello-jvm:1.0.0` with `APP_VERSION=1.0.0` and note how long it takes. Change one line in `Main.kt`, rebuild, and compare.",
    "Run the image with a 512 MB limit on port 8080. Call `/` and `/healthz`, wait for `docker ps` to say healthy, and check the user with `docker exec <name> id`.",
    "Print the heap limit inside the container and check it is about 75% of 512 MB.",
    "Stop the container and check how long `docker stop` takes and which exit code it leaves.",
    "Add `.github/workflows/jvm-ci.yml`, push, and open the run on GitHub. Read the Job Summary that setup-gradle wrote.",
    "Push a second, small commit and compare the run time of the build job with the first run.",
]
L["task"]["hints"] = [
    "`docker stop` should take well under a second and leave exit code 143 (SIGTERM, the polite stop signal). If it takes 10 seconds, check that ENTRYPOINT uses the exec form (Day 19).",
    "The first CI run starts with an empty cache, so it is always the slowest. The cache is saved only from main.",
]
L["task"]["done_when"] = ("You are done when `docker ps` shows the container as healthy, `curl localhost:8080` reports version 1.0.0, "
                          "and the jvm-ci workflow is green on GitHub.")

L["explain_back"]["answer"] = ("The build cache stores task outputs, such as compiled classes and test results, under a key made from a hash of the task's inputs. "
                               "When another build has the same inputs, even in another folder or on CI, Gradle copies the outputs back and marks the task FROM-CACHE. "
                               "The configuration cache stores the task graph that the build scripts produced, so a repeat run can skip running the scripts. "
                               "A hit prints `Reusing configuration cache.` at the start, and tasks then run or are skipped as usual.")

L["recap"] = [
    "Up-to-date checks, the build cache, the configuration cache and the daemon each skip a different kind of work.",
    "Compile avoidance means a change inside function bodies does not recompile the projects that depend on yours; a toolchain picks the JDK that compiles.",
    "In GitHub Actions, use setup-java plus setup-gradle and nothing else for Gradle caching; set `cache-provider: basic` to stay fully open source.",
    "Build in a JDK stage, ship `installDist` output on a JRE image, run as non-root, and set `MaxRAMPercentage` (the default heap is 25%).",
    "Jib, `bootBuildImage` and Quarkus extensions build images without a Dockerfile; Jib 3.5.4 needs `--no-configuration-cache`.",
    "The limit: the image runs only where you start it by hand, and nothing yet creates the servers it would run on.",
]

C = L["check"]
C[0]["why"] = "FROM-CACHE means the inputs hashed to a key that the build cache already had, so Gradle copied the outputs in instead of compiling."
C[1]["why"] = "The JVM sees the container limit and by default caps the heap at 25% of it, which is why images set MaxRAMPercentage."
C[2]["why"] = "setup-gradle should own the Gradle cache; a second mechanism on the same folder interferes with it."

I = L["interview"]
I[0]["a"] = ("First I look at which tasks actually ran, using the console output or a Build Scan. "
             "Then I make sure caching works: setup-gradle restoring Gradle User Home, the build cache turned on, and no `clean` in the CI command. "
             "Ideally there is also a remote cache that CI writes and laptops read. "
             "I turn on the configuration cache and parallel execution, and fix plugins that break them. "
             "If one project dominates, I look at compile avoidance: splitting modules and preferring `implementation` stops changes from rippling.")
I[1]["a"] = ("With a multi-stage Dockerfile: a JDK stage runs the Gradle wrapper and `installDist`, and a JRE stage gets only the start script and jars. "
             "I copy the wrapper first so the Gradle download stays in a cached layer, and use a BuildKit cache mount for dependencies. "
             "The run stage uses a non-root user, an exec-form ENTRYPOINT so SIGTERM reaches the JVM, and `-XX:MaxRAMPercentage` so the heap fits the container limit. "
             "Jib or Spring Boot's `bootBuildImage` are good alternatives when a team prefers no Dockerfile.")
I[2]["a"] = ("Locking records which versions were resolved, in a `gradle.lockfile`, so a build fails if the graph changes until someone updates the lock. "
             "Verification records checksums or signatures of the files themselves, in `verification-metadata.xml`, so a tampered or swapped jar fails the build. "
             "Locking guards against drift and surprise upgrades; verification guards against supply-chain tampering. "
             "You can use both together.")

L["deeper"]["body"] = """The cache mount that made local rebuilds fast does not help much on a fresh CI runner. Each runner starts with an empty BuildKit cache, so the build stage downloads every library again whenever the source changed. In our test the mount held about 900 MB after one build: libraries, the Kotlin compiler, transformed jars and the local build cache. The `cache-from: type=gha` setting brings back image layers, including the 170 MB Gradle layer, but not the contents of a cache mount.

Teams handle this in one of three ways:

1. Accept it. For a small service, the image job takes a minute or two longer than it could. hello-jvm's workflow does this, because the Dockerfile stays simple and the same everywhere.
2. Build outside Docker, and only package inside it. The build job runs `./gradlew build :app:installDist` with setup-gradle's warm cache, and a one-stage Dockerfile copies `app/build/install/app` onto the JRE image. The trade-off is that the image now depends on what the runner built, so laptops and CI must use the same steps.
3. Use Jib in CI. It runs inside Gradle, so it shares setup-gradle's cache, and `jib` pushes without a Docker daemon. Today that means `--no-configuration-cache` for that step.

The configuration cache has a CI angle too. Gradle 9.1 added a read-only mode, `-Dorg.gradle.configuration-cache.read-only=true`, meant for builds that should use entries but not write them, such as pull request builds. And because entries can contain secrets, setup-gradle can encrypt them in the GitHub Actions cache with a key you give it. Make one with `openssl rand -base64 16`, store it as a repository secret, and pass it as `cache-encryption-key: ${{ secrets.GRADLE_ENCRYPTION_KEY }}`.

Finally, the remote build cache is where large teams win the most time: the bakery's shared fridge, at the scale of a whole chain. The setup-gradle documentation recommends the usual pattern: CI builds push to the remote cache and switch off the local one, and local builds then read what CI wrote. The same pattern works with Develocity or any other HTTP build cache server."""

save(path, P)
print("d30 written")
