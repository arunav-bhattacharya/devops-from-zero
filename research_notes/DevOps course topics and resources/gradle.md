# Gradle for a DevOps course (as of 30 October 2026): research notes for 3 lessons

How things were checked (read this first):
- **Run in this sandbox.** Every build output quoted below came from running **Gradle 9.8.2** (wrapper, Linux amd64, OpenJDK 21.0.12) on 2026-10-30. The Kotlin projects used the Kotlin Gradle plugin (KGP) 2.4.21, JUnit 6.1.3 through a BOM, and Jib 3.5.4 against a real Docker 29.9.2 daemon. These outputs are marked **(sandbox run)**. On an Apple Silicon Mac the output is the same apart from paths, timings and daemon PIDs. The test projects are in the scratchpad: `/tmp/claude-0/-home-user/5a31be1b-d2d7-5096-8c55-314d3e3b0058/scratchpad/try/mini` (app plus library), `.../try/life` (lifecycle demo) and `.../try/initdemo` (output of `gradle init`).
- **Versions came from primary sources.** These were `git ls-remote --tags` against github.com, a blobless clone of `gradle/actions` and `GoogleContainerTools/jib` for tag dates, `https://services.gradle.org/versions/current` and `/versions/all`, Maven metadata on plugins.gradle.org and repo.maven.apache.org, and kotlinlang.org pages fetched with curl.
- **Gradle docs were read from source.** docs.gradle.org is blocked here (curl gets 403 on CONNECT). The user-manual and release-note sources were read from the `gradle/gradle` repo on raw.githubusercontent.com at tags `v9.0.0` to `v9.8.2`, path `platforms/documentation/docs/src/docs/...`. Those raw links are the ones cited. docs.gradle.org URLs are listed only when they appeared in search results. They are marked "(search result)".
- **Blocked or unreliable hosts (useful for a writer who wants to test here):**
  - `services.gradle.org` **works**: the wrapper downloaded the 9.8.2 distribution in about 5 s.
  - `plugins.gradle.org` **works**.
  - `repo.maven.apache.org` / `repo1.maven.org` (Maven Central) are **reachable but rate-limited**. They often return `HTTP 429 Too Many Requests` ("Your ip has exceeded rate limits"). A clean Kotlin build needed about 12 to 15 retries of `./gradlew build` before every artifact was in `~/.gradle/caches`. Each retry got further, and after that the builds ran offline from the cache.
  - Docker Hub (`registry-1.docker.io`) also returned `429 TOOMANYREQUESTS` for an unauthenticated pull of `eclipse-temurin:21-jre`. `gcr.io` worked (`gcr.io/distroless/java21-debian12` was pulled by Jib).
  - Blocked: docs.gradle.org, scans.gradle.com, dl.google.com, youtube.com, and github.com web pages (git over HTTPS works, but blob pages return 403).
  - A probe of third-party Maven mirrors was refused by the sandbox's permission system, so none were tested.
  - The sandbox also has a system Gradle 8.14.3 at `/opt/gradle/bin/gradle` and Docker 29.9.2.

---

## Key question 1: What is the current Gradle version, and what changed that matters to beginners?

### Takeaway
The current release is **Gradle 9.8.2** (19 Oct 2026). The 9.x line began with **9.0.0 in July/August 2025**. For beginners, Gradle 9 changed six things:
- **Configuration cache:** it is the *preferred* mode. `gradle init` turns it on, and Gradle aims to make it the default in Gradle 10.
- **Kotlin DSL:** it has been the default for new builds since 8.0, and it now uses Kotlin 2 (the K2 compiler).
- **Java:** Gradle itself needs **Java 17+** to run, while toolchains can still compile for Java 8+.
- **Version numbers:** releases use SemVer `9.x.y`.
- **Removed APIs:** many old APIs are gone (`jcenter()`, `-b/-c`, conventions, `project.exec`, the `"name"()` task syntax).
- **Tests:** a `test` task that finds no tests now fails.

### Cited Findings
**Current version and cadence**
- `services.gradle.org/versions/current` reports `"version" : "9.8.2"`, buildTime `20261019162926+0000`, and gives the distribution `https://services.gradle.org/distributions/gradle-9.8.2-bin.zip` with SHA-256 `21bd5da2de49b642904077f38c0efdc7778e92b3ed0889392dca61b97e389607` — [services.gradle.org/versions/current](https://services.gradle.org/versions/current) (opened with curl)
- The Gradle releases page lists 9.8.2 (Oct 19, 2026), 8.14.6 (Oct 08, 2026) and 9.8.1 (Oct 07, 2026). The 8.14 line is still getting patch releases — [gradle.org/releases](https://gradle.org/releases/) (opened with curl)
- Build timestamps of the 9.x releases: 9.0.0 2025-07-31, 9.1.0 2025-09-18, 9.2.0 2025-10-29, 9.3.0 2026-01-16, 9.4.0 2026-03-04, 9.5.0 2026-04-28, 9.6.0 2026-06-18, 9.7.0 2026-08-06, 9.8.0 2026-09-24, 9.8.1 2026-10-07, 9.8.2 2026-10-19. That is roughly one minor release every 6 to 8 weeks — [services.gradle.org/versions/all](https://services.gradle.org/versions/all) (opened with curl). The git tags `v9.0.0` to `v9.8.2` match — `git ls-remote --tags https://github.com/gradle/gradle`
- `./gradlew --version` on 9.8.2 prints `Kotlin: 2.4.10`, `Groovy: 4.0.33`, `Launcher JVM: 21.0.12.1`, `Daemon JVM: ... (no Daemon JVM specified, using current Java home)` — (sandbox run)

**Gradle 9.0.0 (July 2025) changes that matter to beginners** — [9.0.0 release notes source](https://raw.githubusercontent.com/gradle/gradle/v9.0.0/platforms/documentation/docs/src/docs/release/notes.md) (opened); [docs.gradle.org/9.0.0/release-notes.html](https://docs.gradle.org/9.0.0/release-notes.html) (search result)
- "The Configuration Cache is the preferred mode of execution. While not yet required, Gradle encourages adoption by prompting users and gradually phasing out incompatible APIs." If a build has no known incompatibilities, Gradle suggests enabling it at the end of the build. You can silence the prompt with `org.gradle.configuration-cache=false` — same source
- "Graceful fallback": Gradle falls back to non-configuration-cache mode instead of failing when it meets unsupported core features (for example Maven Publish, Ivy Publish, the IDE plugins). This applies to *core* plugins — same source
- What's New in Gradle 9: "For newly generated projects, when using gradle init, the Configuration Cache is now enabled by default", with "a goal of enabling Configuration Cache by default in Gradle 10" — [gradle.org/whats-new/gradle-9](https://gradle.org/whats-new/gradle-9/) (opened with curl). Confirmed: `gradle init` on 9.8.2 wrote `gradle.properties` containing `org.gradle.configuration-cache=true` — (sandbox run)
- "Gradle requires a Java Virtual Machine (JVM) version 17 or higher to start the Gradle daemon … Gradle still supports compiling, testing and running other JVM-based tools with Java 8 and higher" through toolchains — 9.0.0 release notes source (above)
- Gradle 9 embeds Kotlin 2.2.x and uses Kotlin language version 2.2 for `.gradle.kts` scripts. Gradle 8.x used language version 1.8. It also moved to Groovy 4 and JSpecify nullability annotations on the API — 9.0.0 release notes source
- SemVer: "Starting with Gradle 9, all Gradle releases follow … `MAJOR.MINOR.PATCH`". `./gradlew wrapper --gradle-version=9` resolves to the latest 9.x.y — 9.0.0 release notes source
- Archive tasks (Jar, Zip, Tar…) produce reproducible archives by default, with fixed file order and timestamps — 9.0.0 release notes source
- `JAVA_HOME` is now used for toolchain auto-detection — 9.0.0 release notes source
- A new [Gradle Best Practices guide](https://raw.githubusercontent.com/gradle/gradle/v9.8.2/platforms/documentation/docs/src/docs/userguide/best-practices/best_practices_general.adoc) was written "in partnership with JetBrains and Google" — 9.0.0 release notes source

**Removed or changed in 9.0 (from the major-version upgrade guide)** — [upgrading_major_version_9.adoc](https://raw.githubusercontent.com/gradle/gradle/v9.8.0/platforms/documentation/docs/src/docs/userguide/releases/upgrading/upgrading_major_version_9.adoc) (opened)
- The minimum Kotlin Gradle Plugin is now 2.0.0. It was 1.6.10 on Gradle 8.x
- `jcenter()` was removed. The closest replacement is `mavenCentral()`
- The `-c/--settings-file` and `-b/--build-file` options were removed
- The `Convention` API was removed. Use extensions instead, for example `project.base` instead of `archivesBaseName`
- `Project#exec` and `Project#javaexec` (and the script-level versions) were removed. They were deprecated in 8.11
- The Kotlin DSL `"name"()` task reference syntax was removed. Use `named("name")`
- Referencing `libraries` or `bundles` from a version catalog inside `plugins {}` was removed
- "`test` task fails when no tests are discovered". You can opt out with `failOnNoDiscoveredTests = false`
- A custom `Test` task registered without its own classpath now *silently runs no tests*. The old fallback to the `test` source set is gone

**JUnit Platform launcher (an 8.x change that still bites in 9.x)**
- "If using JUnit 5, an explicit `runtimeOnly` dependency on `junit-platform-launcher` is required in addition to the existing `implementation` dependency on the test engine" — [upgrading_version_8.adoc](https://raw.githubusercontent.com/gradle/gradle/v9.8.0/platforms/documentation/docs/src/docs/userguide/releases/upgrading/upgrading_version_8.adoc) (opened). `gradle init` 9.8.2 accordingly generates `testRuntimeOnly("org.junit.platform:junit-platform-launcher")` — (sandbox run)

**Notable 9.1 to 9.8 additions** (from the release-note sources: [9.1](https://raw.githubusercontent.com/gradle/gradle/v9.1.0/platforms/documentation/docs/src/docs/release/notes.md), [9.2](https://raw.githubusercontent.com/gradle/gradle/v9.2.0/platforms/documentation/docs/src/docs/release/notes.md), [9.4](https://raw.githubusercontent.com/gradle/gradle/v9.4.0/platforms/documentation/docs/src/docs/release/notes.md), [9.5](https://raw.githubusercontent.com/gradle/gradle/v9.5.0/platforms/documentation/docs/src/docs/release/notes.md), [9.6](https://raw.githubusercontent.com/gradle/gradle/v9.6.0/platforms/documentation/docs/src/docs/release/notes.md), [9.7](https://raw.githubusercontent.com/gradle/gradle/v9.7.0/platforms/documentation/docs/src/docs/release/notes.md), [9.8](https://raw.githubusercontent.com/gradle/gradle/v9.8.0/platforms/documentation/docs/src/docs/release/notes.md); all opened)
- 9.1:
  - `--task-graph` prints the task graph without running anything. It became stable in 9.4.
  - A configuration cache **read-only mode** (`-Dorg.gradle.configuration-cache.read-only=true`) "may speed up CI builds that do not contribute their results to caches", for example PR builds.
  - `gradle init` generates `kotlin-test` instead of `kotlin-test-junit5` "so the test framework variant … can be inferred automatically".
  - Java 25 support.
- 9.2: Windows on ARM support. The **daemon toolchain** (`gradle/gradle-daemon-jvm.properties`, the `updateDaemonJvm` task) is now stable.
- 9.4: Java 26 support. Bearer-token auth for wrapper downloads. Better configuration cache hit rates when `gradle.properties` changes.
- 9.5:
  - `./gradlew --develocity-url https://develocity.example.com build` publishes a Build Scan without editing the build.
  - Wrapper downloads now retry automatically.
- 9.6:
  - Non-interactive mode and `NO_COLOR` support.
  - Implicit lookup of properties and methods in *parent* projects is deprecated.
- 9.7: **Isolated Projects** moves from experimental to incubating (parallel project configuration).
- 9.8:
  - Java 27 support for the daemon and toolchains.
  - `org.gradle.mirror.maven.settings=true` reuses Maven `settings.xml` mirror settings.
  - Maven POM generation now takes part in up-to-date checks.
  - Problem locations in the terminal are clickable.

**Kotlin DSL default**
- "Since Gradle 8.0, Kotlin DSL is the default for new builds created with `gradle init`". The best-practices guide says "Prefer the Kotlin DSL (`build.gradle.kts`) over the Groovy DSL" for strict typing, IDE completion and a single-language stack — [best_practices_general.adoc](https://raw.githubusercontent.com/gradle/gradle/v9.8.2/platforms/documentation/docs/src/docs/userguide/best-practices/best_practices_general.adoc) (opened)

### Inferences
- For a Mac or Apple Silicon learner, two consequences matter. The JDK that *runs* Gradle must be 17+. The JDK that *compiles* their code is chosen separately by `kotlin { jvmToolchain(21) }`. Teaching the split early heads off "it works in IntelliJ but not in the terminal" confusion.
- Course examples can assume the configuration cache is on (as `gradle init` does). The course should then teach *why* a task that touches `project` at execution time fails. That is now the most common beginner error message in a fresh build (see Key question 3).
- Anything the learner copies from pre-2025 blog posts may break on Gradle 9. The usual culprits are `jcenter()`, `buildDir`-style conventions, `"test"()` syntax, `exec {}` in scripts, and Kotlin 1.x-era `kotlinOptions`. Tell learners to check the date of any tutorial.

### Gaps
- No primary source gives an exact Gradle 10 release date. The What's New page only states the goal of making the configuration cache the default in Gradle 10.
- Gradle 8.14.x patch releases continue (8.14.6 on Oct 08, 2026), but this session found no end-of-support date for the 8.x line.

---

## Key question 2: What intuitions and analogies work?

### Takeaway
Use five pictures:
- **A Makefile that knows its inputs and outputs:** tasks are nodes in a graph (a DAG), and a task is skipped when its inputs and outputs have not changed.
- **A recipe evaluated before cooking:** configuration builds the graph, and execution runs it.
- **The wrapper as a lockfile for the tool itself.**
- **`api` and `implementation` as public and private visibility for dependencies.**
- **The caches as memoisation:** a cache key is a hash of the task's inputs.

### Cited Findings
- Gradle has three phases. *Initialization* finds the settings file and decides which projects take part. *Configuration* registers tasks and builds the task graph for the requested tasks, and "tasks that were not requested are not configured". *Execution* runs the selected tasks in dependency order — [build_lifecycle.html](https://docs.gradle.org/current/userguide/build_lifecycle.html) (search result); tutorial: [part2_build_lifecycle.html](https://docs.gradle.org/current/userguide/part2_build_lifecycle.html) (search result)
- With the configuration cache, "the three phases stay the same, but whether they run on a given build depends on a cache hit or miss" — [configuration_cache.html](https://docs.gradle.org/current/userguide/configuration_cache.html) (search result, summarised by the search tool)
- The lifecycle demo below shows all three phases and the configuration cache skipping the first two on the second run — (sandbox run)
- "Since a task describes all of its inputs and outputs, Gradle can compute a build cache key that uniquely defines the task's outputs based on its inputs." The same inputs drive up-to-date checks. "The task path is not an input to the build cache key" — [build_cache.adoc](https://raw.githubusercontent.com/gradle/gradle/v9.8.2/platforms/documentation/docs/src/docs/userguide/optimizing-builds/build-cache/build_cache.adoc) (opened)
- Wrapper: `gradle-wrapper.properties` pins `distributionUrl=https\://services.gradle.org/distributions/gradle-9.8.2-bin.zip`, and the scripts download that exact version into `GRADLE_USER_HOME/wrapper/dists` — (sandbox run, generated file). The wrapper task supports `--gradle-distribution-sha256-sum`. "When … gradlew … need to download Gradle, they will check the SHA-256 hash … If there is a mismatch, that ZIP will not be unpacked" — [gradle_wrapper.adoc](https://raw.githubusercontent.com/gradle/gradle/v9.8.2/platforms/documentation/docs/src/docs/userguide/reference/runtime-configuration/gradle_wrapper.adoc) (opened); [best_practices_security.html](https://docs.gradle.org/current/userguide/best_practices_security.html) (search result)
- `api` vs `implementation`: "the api configuration should be used to declare dependencies which are exported by the library API, whereas the implementation configuration should be used to declare dependencies which are internal to the component". `api` dependencies "will appear on the compile classpath of consumers" — [java_library_plugin.html](https://docs.gradle.org/current/userguide/java_library_plugin.html) (search result); [Tom Gregory: api vs implementation](https://tomgregory.com/how-to-use-gradle-api-vs-implementation-dependencies-with-the-java-library-plugin) (search result)
- The daemon is a long-lived background JVM. It stops after "Daemon has been idle for 3 hours". `gradle --status` lists running daemons. Changing JVM args spawns a new daemon — [gradle_daemon.adoc](https://raw.githubusercontent.com/gradle/gradle/v9.8.2/platforms/documentation/docs/src/docs/userguide/reference/runtime-configuration/gradle_daemon.adoc) (opened)

### Inferences
Analogies that fit the facts above. They are the author's suggestions, built on the cited mechanics.

| Concept | Plain explanation | Analogy |
|---|---|---|
| Build tool | Turns source plus dependencies into tested, packaged artifacts, the same way every time | A kitchen's written recipe plus a sous-chef who never skips a step |
| Task | One unit of work with declared inputs and outputs (`compileKotlin`, `test`, `jar`) | A Makefile target, but the "is it stale?" check uses content hashes, not timestamps |
| Task graph | The DAG of tasks needed for what you asked (`build` pulls in `compileKotlin`, `test`, `jar`…) | `make` dependency resolution. `--task-graph` lets you see it |
| Plugin | A bundle that adds tasks, conventions and extensions (`kotlin("jvm")`, `application`) | A "starter kit" that installs a standard set of recipes |
| Project / subproject | One buildable unit, usually one directory with a `build.gradle.kts` | A module in IntelliJ. One Maven module |
| Settings file | Declares *which* projects exist and where plugins and repos come from | The guest list read at the door (initialization) |
| Configuration phase | Running every build script to *describe* the graph. No real work should happen here | Reading the whole recipe book before turning on the stove. Slow if each page does heavy work |
| Configuration cache | Saves the computed task graph, so the next identical invocation skips init and configuration | Saving the prepared mise en place |
| Up-to-date check | Same inputs and outputs as last time means skip | Memoisation keyed on the input hash |
| Build cache | Reuse outputs produced by *another* build or checkout (local dir or remote server) | A shared memo table across machines |
| Wrapper | A small script plus a jar that downloads one pinned Gradle version | `.nvmrc`/`.tool-versions`, or a lockfile for the build tool |
| Daemon | A warm JVM kept between builds, so you don't pay JVM startup and JIT warm-up each time | A running dev server vs cold-starting a CLI each time |
| `implementation` vs `api` | Private vs public dependency of a library | `private` vs `public` visibility, applied to your dependencies |
| Version catalog | One TOML file of names to coordinates and versions | A typed address book for dependencies |
| Platform / BOM | A set of versions that must move together | A "compatible parts list" for a family of libraries |

- The best single demo of "smarter than make" is the compile-avoidance run in Lesson 1. Add a comment to a library source file. That library's `compileKotlin` re-runs, but its jar and every downstream compile stay `UP-TO-DATE`, because the class files did not change.

### Gaps
- No official Gradle page using the "Makefile" analogy surfaced in the searches. The analogy is the author's framing.

---

## Key question 3: What do beginners get wrong?

### Takeaway
The classic mistakes are:
- running a global `gradle` instead of `./gradlew`
- doing real work at configuration time, which also breaks the configuration cache
- putting copy-pasted logic in every `build.gradle.kts` instead of convention plugins
- using `api` everywhere, or `implementation` where `api` is needed
- assuming that the version they declared is the one they got (conflict resolution)
- CI caches that never hit, or that leak secrets

New in the Gradle 9 era are configuration cache failures from third-party plugins (Jib 3.5.4 is one) and empty test runs that now fail the build.

### Cited Findings
- **Global `gradle` vs `./gradlew`.** The `setup-gradle` docs say "The recommended way to execute any Gradle build is with the help of the Gradle Wrapper" — [gradle/actions README](https://raw.githubusercontent.com/gradle/actions/main/README.md) (opened). The sandbox's system `gradle` is 8.14.3, while the project wrapper is 9.8.2. Running the global one would build with a different major version — (sandbox run). Gradle 8.14.3's `gradle wrapper` in an empty folder fails with "Directory … does not contain a Gradle build … should contain one of the possible settings files". You need a `settings.gradle.kts` first, or `gradle init` — (sandbox run)
- **Work at configuration time.** Top-level `println` and work inside `tasks.register { … }` but outside `doLast` run during configuration. Only `doLast` runs at execution. With `register` (lazy), a task that was not requested is not configured: running `bad` did not print the `hello` task's configuration line. Running `tasks` *does* configure all tasks — (sandbox run, lifecycle demo below). The best practices list "Avoid `afterEvaluate`" — [best_practices_general.adoc](https://raw.githubusercontent.com/gradle/gradle/v9.8.2/platforms/documentation/docs/src/docs/userguide/best-practices/best_practices_general.adoc) (opened)
- **Touching `project` inside a task action.** With the configuration cache on, `doLast { println(project.version) }` fails: "Invocation of 'Task.project' by task ':bad' at execution time is unsupported with the configuration cache" — (sandbox run)
- **Third-party plugins that are not compatible with the configuration cache.** `./gradlew :app:jibDockerBuild` with Jib 3.5.4 and `org.gradle.configuration-cache=true` failed with "Invocation of 'Task.project' by task ':app:jibDockerBuild' at execution time is unsupported…". It worked with `--no-configuration-cache`, but printed "Invocation of Task.project at execution time has been deprecated. This will fail with an error in Gradle 10" — (sandbox run). The Jib 3.5.x changelog lists Gradle 9 fixes (3.5.2 and 3.5.3) but no configuration cache support — [jib-gradle-plugin CHANGELOG](https://raw.githubusercontent.com/GoogleContainerTools/jib/master/jib-gradle-plugin/CHANGELOG.md) (opened)
- **Logic in build scripts / `buildSrc`.** Best practices: "Use Convention Plugins for Common Build Logic" and "Favor `build-logic` Composite Builds for Build Logic … **not** in `buildSrc`". Reasons given: "Any change in `buildSrc` causes the entire build to become out-of-date", and `buildSrc` has classloader differences — [best_practices_structuring_builds.adoc](https://raw.githubusercontent.com/gradle/gradle/v9.8.2/platforms/documentation/docs/src/docs/userguide/best-practices/best_practices_structuring_builds.adoc) (opened). Note that `gradle init --split-project` in 9.8.2 still generates `buildSrc/` convention plugins — (sandbox run)
- **Repositories in every project.** "Set up your Dependency Repositories in the Settings file". The same guide includes "Don't Explicitly Depend on the Kotlin Standard Library" and "Use Version Catalogs to Centralize Dependency Versions" — [best_practices_dependencies.adoc](https://raw.githubusercontent.com/gradle/gradle/v9.8.2/platforms/documentation/docs/src/docs/userguide/best-practices/best_practices_dependencies.adoc) (opened)
- **Settings and gradle.properties.** "Set Build Flags in `gradle.properties`", "Name Your Root Project", "Do not use `gradle.properties` in subprojects", "Apply Plugins Using the `plugins` Block" — [best_practices_general.adoc](https://raw.githubusercontent.com/gradle/gradle/v9.8.2/platforms/documentation/docs/src/docs/userguide/best-practices/best_practices_general.adoc) (opened)
- **`api` vs `implementation`.** If `greeting` declares `implementation(commons-text)`, then `app` code that imports `org.apache.commons.text.WordUtils` fails with `Unresolved reference 'text'`. Switching to `api(...)` makes it compile — (sandbox run). With `implementation`, changes to that dependency don't force consumers to recompile — [java_library_plugin.html](https://docs.gradle.org/current/userguide/java_library_plugin.html) (search result)
- **The version you declared is not the version you get.** `app` declares `commons-lang3:3.17.0`. The runtime classpath resolves `3.17.0 -> 3.18.0` "By conflict resolution: between versions 3.18.0 and 3.17.0" (Gradle picks the highest). Meanwhile the *compile* classpath still shows 3.17.0, because each classpath is resolved separately — (sandbox run, outputs in Lesson 2)
- **Kotlin test framework mismatch.** `kotlin("test")` plus `useJUnitPlatform()` pulls `kotlin-test-junit5:2.4.21`, which brings **JUnit 5.10.1** by default. Adding `platform("org.junit:junit-bom:6.1.3")` aligns it to 6.1.3 — (sandbox run). Gradle 9 fails a `test` task that discovers no tests, for example when tests are written for one framework but the task uses another — [upgrading_major_version_9.adoc](https://raw.githubusercontent.com/gradle/gradle/v9.8.0/platforms/documentation/docs/src/docs/userguide/releases/upgrading/upgrading_major_version_9.adoc) (opened)
- **CI caching mistakes.**
  - Don't combine `setup-gradle` with `actions/cache` on `~/.gradle` or with `setup-java`'s `cache: gradle`. "Using either of these mechanisms may interfere with the caching provided by this action."
  - By default the cache is written only from the default branch, and other branches only read it.
  - Gradle-home cache keys can't be computed deterministically from build files. setup-gradle keys on OS, job id, a hash of the matrix and workflow name, and the git SHA, then restores the closest match. The basic provider instead hashes `**/*.gradle*`, `gradle-wrapper.properties`, `gradle/*.versions.toml`, etc.
  - Source: [setup-gradle.md](https://raw.githubusercontent.com/gradle/actions/main/docs/setup-gradle.md) (opened)
- **Configuration cache entries can contain secrets.** setup-gradle offers `cache-encryption-key` (a base64 AES key, generated with `openssl rand -base64 16`) "to encrypt configuration-cache data stored in the GitHub Actions cache" — [setup-gradle.md](https://raw.githubusercontent.com/gradle/actions/main/docs/setup-gradle.md) (opened)
- **Unpinned wrapper download.** The `gradle-wrapper.properties` generated by `gradle wrapper` contains no `distributionSha256Sum` line unless you pass `--gradle-distribution-sha256-sum` — (sandbox run); [gradle_wrapper.adoc](https://raw.githubusercontent.com/gradle/gradle/v9.8.2/platforms/documentation/docs/src/docs/userguide/reference/runtime-configuration/gradle_wrapper.adoc) (opened)

### Inferences
- **"Slow configuration phase" symptoms to teach:**
  - `./gradlew help` taking seconds
  - network calls or `exec` at the top level of a script
  - `tasks.create` or eager `getByName` instead of `register` or `named`
  - `allprojects {}` / `subprojects {}` blocks
  - The fix ladder: lazy APIs, then convention plugins, then the configuration cache.
- **Apple Silicon specific.** Jib's default `platforms` is `amd64/linux`, so an image built on an M-series Mac is amd64 and runs under emulation locally unless `jib.from.platforms` adds `arm64`. Docker Desktop on Mac builds `linux/arm64` by default, so a multi-stage Dockerfile image won't run on amd64 CI or cluster nodes without `--platform`/buildx. (The Jib default is cited in Lesson 3. The Docker Desktop behaviour is the author's understanding and was not verified this session.)

### Gaps
- No single "top 10 beginner mistakes" source from Gradle Inc. was found. The list above is assembled from the best-practices guide and the sandbox runs.

---

## Key question 4: What is the smallest realistic Kotlin project, and what are the current versions?

### Takeaway
Use a two-project build: `app` (application plugin) depending on `greeting` (`java-library`), with a version catalog, the foojay toolchain resolver, `kotlin.test` on the JUnit Platform, and `gradle.properties` turning on the configuration cache, build cache and parallel execution. On Gradle 9.8.2 with KGP 2.4.21 it built, tested and ran with no warnings. Current versions: **Gradle 9.8.2, Kotlin/KGP 2.4.21, JUnit 6.1.3, `gradle/actions/setup-gradle@v6` (v6.4.1), Jib 3.5.4, foojay resolver 1.0.0, Develocity plugin 4.6.1**.

### Cited Findings
**Versions (as of 2026-10-30)**

| Component | Current stable | Evidence |
|---|---|---|
| Gradle | 9.8.2 (2026-10-19). Also 8.14.6 (2026-10-08) for the 8.x line | [services.gradle.org/versions/current](https://services.gradle.org/versions/current); [gradle.org/releases](https://gradle.org/releases/); git tag `v9.8.2` |
| Kotlin and KGP | 2.4.21 (released Oct 8, 2026). 2.4.0 was released June 3, 2026. 2.4.20 on Sep 7, 2026. 2.5.0 is "planned for December 2026" and 2.5.0-Beta2 is on the plugin portal | [kotlinlang.org/docs/releases.html](https://kotlinlang.org/docs/releases.html) (opened); git tag `v2.4.21` in JetBrains/kotlin; plugin portal metadata for `org.jetbrains.kotlin.jvm` |
| KGP and Gradle compatibility | KGP 2.4.20 to 2.4.21 is "fully supported" on Gradle **7.6.3 to 9.7.0** (AGP 8.5.2 to 9.3.1) | [kotlinlang.org/docs/gradle-configure-project.html](https://kotlinlang.org/docs/gradle-configure-project.html) (opened). On 9.8.2 it still built with no warnings (sandbox run) |
| Kotlin embedded in Gradle 9.8.2 | 2.4.10 (used for `.gradle.kts` scripts. `gradle init` also pins KGP to this) | `./gradlew --version` and the generated `libs.versions.toml` (sandbox run) |
| JUnit | 6.1.3 (`org.junit:junit-bom` metadata lastUpdated 2026-08-07). `gradle init` 9.8.2 still writes 6.0.1 | git tag `r6.1.3` in junit-team/junit-framework; [junit-bom maven-metadata.xml](https://repo.maven.apache.org/maven2/org/junit/junit-bom/maven-metadata.xml) (opened); sandbox `gradle init` output |
| kotlin-test default JUnit | `kotlin-test-junit5:2.4.21` brings JUnit Jupiter and the Platform launcher **5.10.1** unless a BOM overrides it | sandbox run (`dependencies --configuration testRuntimeClasspath`) |
| gradle/actions | **v6.4.1** (tag 2026-10-28). The moving `v6` tag points to it. v6.0.0 was released 2026-03-23, v5 is from 2026-02-23 | blobless clone of github.com/gradle/actions, `for-each-ref --sort=-creatordate` |
| actions used in the README example | `actions/checkout@v6`, `actions/setup-java@v5`, `gradle/actions/setup-gradle@v6` | [gradle/actions README](https://raw.githubusercontent.com/gradle/actions/main/README.md) (opened) |
| foojay toolchain resolver | `org.gradle.toolchains.foojay-resolver-convention` 1.0.0 (portal lastUpdated 2025-05-19). This is what `gradle init` 9.8.2 generates | plugin portal metadata (opened); sandbox `gradle init` output |
| Jib Gradle plugin | 3.5.4 (tag `v3.5.4-gradle` 2026-07-14) | plugin portal metadata; git tags in GoogleContainerTools/jib |
| Develocity Gradle plugin | `com.gradle.develocity` 4.6.1 (portal lastUpdated 2026-10-20) | plugin portal metadata (opened) |
| Spring Boot Gradle plugin | 4.1.2 latest stable. 4.2.0-RC1 is published | plugin portal metadata for `org.springframework.boot` (opened) |
| Quarkus Gradle plugin | 3.40.1.1 latest stable. 4.0.0.Beta2 is published | plugin portal metadata for `io.quarkus` (opened) |
| Shadow (fat jar) | `com.gradleup.shadow` 9.6.1 | plugin portal metadata (opened) |

- Kotlin docs show the toolchain set with `kotlin { jvmToolchain(17) }`, and "setting a toolchain via the kotlin extension updates the toolchain for Java compile tasks as well". They also say "If you use Gradle 8.0.2 or higher, you also need to add a toolchain resolver plugin", with the example `id("org.gradle.toolchains.foojay-resolver-convention") version("1.0.0")` — [kotlinlang.org/docs/gradle-configure-project.html](https://kotlinlang.org/docs/gradle-configure-project.html) (opened)
- Version catalog: Gradle auto-imports `gradle/libs.versions.toml`. Libraries are used as `libs.<alias>` and plugins as `libs.plugins.<alias>`. Dashes in aliases become dots — [version_catalogs.html](https://docs.gradle.org/current/userguide/version_catalogs.html) (search result)

**The project (built and run in the sandbox).** Layout:
```
hello-gradle/
├── settings.gradle.kts
├── build.gradle.kts
├── gradle.properties
├── gradle/libs.versions.toml
├── gradle/wrapper/gradle-wrapper.{jar,properties}
├── gradlew, gradlew.bat
├── app/build.gradle.kts         app/src/main/kotlin/demo/app/Main.kt      app/src/test/kotlin/demo/app/MainTest.kt
└── greeting/build.gradle.kts    greeting/src/main/kotlin/demo/greeting/Greeter.kt   greeting/src/test/kotlin/demo/greeting/GreeterTest.kt
```
`settings.gradle.kts`
```kotlin
plugins {
    // Lets Gradle download a matching JDK if none is installed locally
    id("org.gradle.toolchains.foojay-resolver-convention") version "1.0.0"
}

rootProject.name = "hello-gradle"

dependencyResolutionManagement {
    // One place for repositories; projects may not add their own
    repositoriesMode = RepositoriesMode.FAIL_ON_PROJECT_REPOS
    repositories { mavenCentral() }
}

include("app", "greeting")
```
`gradle/libs.versions.toml`
```toml
[versions]
kotlin = "2.4.21"
commons-text = "1.14.0"
junit = "6.1.3"

[libraries]
commons-text = { module = "org.apache.commons:commons-text", version.ref = "commons-text" }
commons-lang3 = { module = "org.apache.commons:commons-lang3", version = "3.17.0" }
junit-bom = { module = "org.junit:junit-bom", version.ref = "junit" }

[plugins]
kotlin-jvm = { id = "org.jetbrains.kotlin.jvm", version.ref = "kotlin" }
jib = { id = "com.google.cloud.tools.jib", version = "3.5.4" }
```
`gradle.properties`
```properties
org.gradle.configuration-cache=true
org.gradle.caching=true
org.gradle.parallel=true
```
`build.gradle.kts` (root)
```kotlin
// Root project: declare plugin versions once, apply them in subprojects
plugins {
    alias(libs.plugins.kotlin.jvm) apply false
}
```
`greeting/build.gradle.kts`
```kotlin
plugins {
    alias(libs.plugins.kotlin.jvm)
    `java-library`
}

kotlin { jvmToolchain(21) }

dependencies {
    implementation(libs.commons.text)   // internal detail: not leaked to consumers
    testImplementation(kotlin("test"))  // kotlin.test, runs on JUnit Platform
    testImplementation(platform(libs.junit.bom)) // BOM: align all JUnit modules to one version
}

tasks.test { useJUnitPlatform() }
```
`app/build.gradle.kts`
```kotlin
plugins {
    alias(libs.plugins.kotlin.jvm)
    application
}

kotlin { jvmToolchain(21) }

dependencies {
    implementation(project(":greeting"))
    implementation(libs.commons.lang3)  // asks for 3.17.0; greeting pulls a newer one transitively
    testImplementation(kotlin("test"))
}

application { mainClass = "demo.app.MainKt" }

tasks.test { useJUnitPlatform() }
```
`greeting/src/main/kotlin/demo/greeting/Greeter.kt`
```kotlin
package demo.greeting

import org.apache.commons.text.WordUtils

class Greeter(private val name: String) {
    fun greet(): String = "Hello, ${WordUtils.capitalizeFully(name)}!"
}
```
`greeting/src/test/kotlin/demo/greeting/GreeterTest.kt`
```kotlin
package demo.greeting

import kotlin.test.Test
import kotlin.test.assertEquals

class GreeterTest {
    @Test
    fun capitalisesTheName() {
        assertEquals("Hello, Ada Lovelace!", Greeter("ada lovelace").greet())
    }
}
```
`app/src/main/kotlin/demo/app/Main.kt`
```kotlin
package demo.app

import demo.greeting.Greeter

fun main(args: Array<String>) {
    val name = args.joinToString(" ").ifBlank { "gradle learner" }
    println(Greeter(name).greet())
}
```
(`app/src/test/.../MainTest.kt` asserts `Greeter("x").greet().startsWith("Hello")`.)

The wrapper was created with `gradle wrapper --gradle-version 9.8.2` (needs a settings file to exist first). The pinned, verified form is `./gradlew wrapper --gradle-version 9.8.2 --gradle-distribution-sha256-sum 21bd5da2de49b642904077f38c0efdc7778e92b3ed0889392dca61b97e389607`. The checksum comes from services.gradle.org; the flag comes from [gradle_wrapper.adoc](https://raw.githubusercontent.com/gradle/gradle/v9.8.2/platforms/documentation/docs/src/docs/userguide/reference/runtime-configuration/gradle_wrapper.adoc).

**Observed outputs (sandbox run)**
- First `./gradlew build`: `BUILD SUCCESSFUL in 16s` / `11 actionable tasks: 11 executed` / `Configuration cache entry stored.` Each project ran 1 test with 0 failures, per the XML results.
- `./gradlew :app:run --args="grace hopper" -q` printed `Hello, Grace Hopper!`
- `greeting` tests on JUnit 6.1.3 via the BOM: `BUILD SUCCESSFUL`, `tests="1" skipped="0" failures="0"`.

**`gradle init` reference output (9.8.2, sandbox run).** This was `./gradlew init --type kotlin-application --dsl kotlin --test-framework junit-jupiter --project-name demo --package demo --split-project --java-version 21 --no-incubating`. It generated:
- `app/`, `list/`, `utilities/`
- `buildSrc/` holding `buildlogic.kotlin-{common,application,library}-conventions.gradle.kts`
- `gradle/libs.versions.toml` with `kotlin-gradle-plugin = "2.4.10"`
- `gradle.properties` with `org.gradle.configuration-cache=true`
- settings with foojay 1.0.0
- convention plugins with `testImplementation("org.junit.jupiter:junit-jupiter:6.0.1")` and `testRuntimeOnly("org.junit.platform:junit-platform-launcher")`

`--test-framework kotlintest` was rejected ("Supported frameworks: 'junit-jupiter'"). `:app:run` printed `Hello World!`.

### Inferences
- The two-project layout is the smallest one that still shows every Lesson 2 idea for real: project dependency, `api`/`implementation`, conflict resolution, a catalog and a BOM. Use `kotlin("test")` (assertions from kotlin.test, runner from the JUnit Platform) rather than raw JUnit APIs. It's idiomatic Kotlin and needs no explicit launcher dependency, because `kotlin-test-junit5` brings one.
- For Lesson 2's convention-plugin step, move the repeated `kotlin { jvmToolchain(21) }` and `tasks.test { useJUnitPlatform() }` into `build-logic/src/main/kotlin/kotlin-conventions.gradle.kts`, included via `pluginManagement { includeBuild("build-logic") }`. This sketch follows the documented pattern but was **not** run in this session.
- Pin KGP to 2.4.21 in the course while noting that Gradle 9.8 is newer than KGP's tested maximum (9.7.0). It worked here, but if a learner sees a KGP compatibility warning, this is the reason.

### Gaps
- The exact date of JUnit 6.1.3's release was not checked. Only the tag and the Maven metadata timestamp were.
- `settings.gradle.kts` `repositoriesMode` uses Kotlin property assignment syntax. It compiled on 9.8.2, but its stability status (incubating or not) was not checked.

---

## Key question 5: How does Gradle compare with Maven, so a learner knows when each appears?

### Takeaway
Maven is a declarative XML (POM) build with a fixed lifecycle. It is predictable, ubiquitous in enterprise Java, and easy to read. Gradle is a programmable build: a task graph with Kotlin or Groovy DSLs, incremental builds, and build and configuration caches. It is the only option for Android and Kotlin Multiplatform, and common for Kotlin, Spring and large monorepos. Expect to *read* both in a DevOps job.

### Cited Findings
- Gradle Inc.'s comparison claims Gradle is "at least twice as fast for nearly every scenario (100x faster for large builds using the build cache)". This is a vendor claim — [gradle.org/maven-vs-gradle](https://gradle.org/maven-vs-gradle) (search result)
- Third-party comparisons agree that Gradle is more flexible, because logic can go straight into build scripts. Maven is more rigid and may need auxiliary plugins or scripts, and build.gradle files can "become cluttered with logic". An older JBoss community test found Gradle "about the same or a little slower". That is informal and likely dated — summarised from the search results at [gradle.org/maven-vs-gradle](https://gradle.org/maven-vs-gradle) and [developer.jboss.org DOC-13764](https://developer.jboss.org/docs/DOC-13764) (search results)
- Gradle can import Maven BOMs: "Gradle … derives a platform variant from every Maven POM it consumes, so any POM with a `<dependencyManagement>` block can be imported as a platform" — [platforms.adoc](https://raw.githubusercontent.com/gradle/gradle/v9.8.2/platforms/documentation/docs/src/docs/userguide/reference/dependency-management/centralizing-dependencies/platforms.adoc) (opened)
- Gradle 9.8 can reuse Maven's mirror settings (`org.gradle.mirror.maven.settings=true`) "in organizations that use both Maven and Gradle build tools with an internal repository mirror" — [9.8.0 release notes source](https://raw.githubusercontent.com/gradle/gradle/v9.8.0/platforms/documentation/docs/src/docs/release/notes.md) (opened)
- The `api` and `implementation` split maps onto POM scopes: the generated POM puts `api` dependencies in `compile` scope and `implementation` dependencies in `runtime` scope — [java_library_plugin.html](https://docs.gradle.org/current/userguide/java_library_plugin.html) (search result summary)
- The Kotlin Gradle plugin's compatibility table covers both Gradle and the Android Gradle Plugin (AGP 8.5.2 to 9.3.1 for KGP 2.4.20+). Android builds are Gradle builds — [kotlinlang.org/docs/gradle-configure-project.html](https://kotlinlang.org/docs/gradle-configure-project.html) (opened)

### Inferences
Quick mapping for learners, from the author's knowledge; the Maven side is not separately sourced this session:

| Maven | Gradle |
|---|---|
| `pom.xml` | `build.gradle.kts` plus `settings.gradle.kts` |
| `mvnw` | `gradlew` |
| phases (`compile`, `test`, `package`, `install`) | tasks (`compileKotlin`, `test`, `jar`/`assemble`, `publishToMavenLocal`), and `build` = `assemble` + `check` |
| `<scope>compile</scope>` | `api` / `implementation` |
| `provided` | `compileOnly` |
| `runtime` | `runtimeOnly` |
| `test` | `testImplementation` |
| `<dependencyManagement>`/BOM import | `platform(...)` |
| parent POM | convention plugin |
| `mvn dependency:tree` | `./gradlew dependencies` / `dependencyInsight` |
| multi-module reactor | multi-project build |

- Maven's "nearest wins" resolution differs from Gradle's "highest version wins". The same dependency set can resolve differently in the two tools, which matters when migrating.
- When each appears:
  - **Gradle:** Android (mandatory), Kotlin Multiplatform, most new Kotlin backends, Spring Initializr projects (both are offered), large monorepos that want remote caching.
  - **Maven:** long-lived enterprise Java services, Quarkus and Jakarta EE shops (both supported), and teams that value convention over configuration.

### Gaps
- No neutral, recent (2025 or 2026) benchmark comparing Maven 4 and Gradle 9 was found within the search budget.

---

## Key question 6 (Lesson 1 plan): what a build tool does and Gradle's model — projects, tasks, plugins, the task graph and lifecycle, settings and build scripts, the Wrapper, running tasks

### Takeaway
Teach the model in this order: tasks → task graph → lifecycle → files → wrapper → running tasks. Make it concrete with two runnable demos, a 10-line lifecycle build and the app-plus-library project. Learners should leave able to predict which tasks run and why a second build says `UP-TO-DATE`.

### Cited Findings
**Concepts in teaching order (one-liners, with sources)**
1. **Build tool.** It automates compile, test and package, and resolves dependencies, reproducibly. `build` = `assemble` + `check` (from the `> Task :app:assemble`, `:app:check` and `:app:build` lines in the sandbox output).
2. **Task.** A named action with inputs and outputs. Labels you will see:
   - `UP-TO-DATE`: inputs and outputs unchanged
   - `NO-SOURCE`: nothing to do
   - `FROM-CACHE`: outputs taken from the build cache
   - `SKIPPED`: the task was skipped (with `--dry-run`, every task shows `SKIPPED`)
   - Source: [build_cache.adoc](https://raw.githubusercontent.com/gradle/gradle/v9.8.2/platforms/documentation/docs/src/docs/userguide/optimizing-builds/build-cache/build_cache.adoc); sandbox run.
3. **Task graph.** Tasks depend on tasks. Gradle builds the DAG for the requested tasks, and `--task-graph` (9.1+, stable in 9.4) prints it without running anything — [9.1 notes](https://raw.githubusercontent.com/gradle/gradle/v9.1.0/platforms/documentation/docs/src/docs/release/notes.md), [9.4 notes](https://raw.githubusercontent.com/gradle/gradle/v9.4.0/platforms/documentation/docs/src/docs/release/notes.md).
4. **Lifecycle.** Initialization (settings, which projects), then configuration (run build scripts, build the graph; only requested tasks are configured), then execution (run actions in dependency order) — [build_lifecycle.html](https://docs.gradle.org/current/userguide/build_lifecycle.html) (search result).
5. **Projects.** The root plus subprojects declared with `include(...)` in `settings.gradle.kts`. `./gradlew projects` shows the tree — sandbox run.
6. **Plugins.** They add tasks and conventions, applied in `plugins {}`. Examples: `application`, `java-library`, `org.jetbrains.kotlin.jvm`. Best practice is "Apply Plugins Using the `plugins` Block" — [best_practices_general.adoc](https://raw.githubusercontent.com/gradle/gradle/v9.8.2/platforms/documentation/docs/src/docs/userguide/best-practices/best_practices_general.adoc).
7. **Kotlin DSL files.**
   - `settings.gradle.kts` (once per build): plugin and dependency repositories, project list, root name.
   - `build.gradle.kts` (per project).
   - `gradle.properties`: flags such as caching. Best practice is "Set Build Flags in `gradle.properties`".
   - Source: same guide.
8. **Wrapper.**
   - Files: `gradlew`, `gradlew.bat`, `gradle/wrapper/gradle-wrapper.jar`, `gradle/wrapper/gradle-wrapper.properties`. Commit all four.
   - Upgrade with `./gradlew wrapper --gradle-version=9.8.2` (9.0 notes show `./gradlew wrapper --gradle-version=@version@ && ./gradlew wrapper`; 9.8 shows `./gradlew :wrapper …`).
   - Pin it with `distributionSha256Sum`.
   - Sources: [gradle_wrapper.adoc](https://raw.githubusercontent.com/gradle/gradle/v9.8.2/platforms/documentation/docs/src/docs/userguide/reference/runtime-configuration/gradle_wrapper.adoc); [9.0.0 notes](https://raw.githubusercontent.com/gradle/gradle/v9.0.0/platforms/documentation/docs/src/docs/release/notes.md).
9. **Running tasks.**
   - Run tasks by name or path: `./gradlew build`, `./gradlew :app:run`, `./gradlew :greeting:test`.
   - `./gradlew tasks [--all]`, `./gradlew help --task <t>`, `--dry-run`, `--task-graph`, `--console=plain`, `-q`, `--args=`.
   - The `tasks` report says "To see all tasks and more detail, run gradlew tasks --all / To see more detail about a task, run gradlew help --task <task>" — sandbox run.

**Demo A: lifecycle (sandbox run, `try/life`)**

`settings.gradle.kts`:
```kotlin
println("1. initialization: settings.gradle.kts evaluated")
rootProject.name = "lifecycle-demo"
```
`build.gradle.kts`:
```kotlin
println("2. configuration: build.gradle.kts evaluated")

tasks.register("hello") {
    group = "demo"
    description = "Prints a greeting"
    println("2b. configuration: hello task configured")
    doLast { println("3. execution: Hello from the hello task") }
}

tasks.register("bad") {
    doLast { println("version is ${project.version}") }  // touches Project at execution time
}
```
`gradle.properties`: `org.gradle.configuration-cache=true`

Output of `./gradlew hello --console=plain`, run 1:
```
Calculating task graph as no cached configuration is available for tasks: hello
1. initialization: settings.gradle.kts evaluated
> Configure project :
2. configuration: build.gradle.kts evaluated
2b. configuration: hello task configured
> Task :hello
3. execution: Hello from the hello task
BUILD SUCCESSFUL in 1s
1 actionable task: 1 executed
Configuration cache entry stored.
```
Run 2 (configuration cache hit, so steps 1 and 2 are skipped):
```
Reusing configuration cache.
> Task :hello
3. execution: Hello from the hello task
BUILD SUCCESSFUL in 797ms
1 actionable task: 1 executed
Configuration cache entry reused.
```
`./gradlew bad`:
```
> Task :bad FAILED
1 problem was found storing the configuration cache.
- Task `:bad` of type `org.gradle.api.DefaultTask`: invocation of 'Task.project' at execution time is unsupported with the configuration cache.
...
Configuration cache entry discarded with 1 problem.
```
Running `bad` did not print "2b", so `hello` was never configured (lazy `register`). `./gradlew tasks --group demo` did print "2b", because the report configures every task.

**Demo B: the task graph and incremental build (sandbox run)**

`./gradlew :app:assemble --task-graph` (trimmed):
```
Tasks graph for: :app:assemble
\--- :app:assemble (org.gradle.api.DefaultTask)
     +--- :app:distTar (org.gradle.api.tasks.bundling.Tar)
     |    +--- :app:jar (org.gradle.api.tasks.bundling.Jar)
     |    |    +--- :app:classes (org.gradle.api.DefaultTask)
     |    |    |    +--- :app:compileJava (org.gradle.api.tasks.compile.JavaCompile)
     |    |    |    |    +--- :app:compileKotlin (org.jetbrains.kotlin.gradle.tasks.KotlinCompile)
     |    |    |    |    |    +--- :greeting:compileJava (...)
     |    |    |    |    |    |    \--- :greeting:compileKotlin (...)
     ...
     |    +--- :app:startScripts (org.gradle.api.tasks.application.CreateStartScripts)
     |    |    \--- :greeting:jar (org.gradle.api.tasks.bundling.Jar)
```
These steps ran on the `gradle init` project:
- Second `./gradlew build` with nothing changed: `BUILD SUCCESSFUL in 951ms` / `13 actionable tasks: 13 up-to-date` / `Configuration cache entry reused.`
- After appending a comment to `list/src/main/kotlin/demo/list/LinkedList.kt`: `Reusing configuration cache.` and `:list:compileKotlin` re-executed. `:list:jar`, `:utilities:compileKotlin` and `:app:compileKotlin` stayed `UP-TO-DATE`. Summary: `13 actionable tasks: 1 executed, 12 up-to-date`.
- `./gradlew --status` shows `PID STATUS INFO / 25476 IDLE 9.8.2`.

### Inferences
**Misconceptions to address in Lesson 1:**
- "The build script runs top to bottom when I run a task." No: scripts *configure*, and actions run later.
- "`gradle` and `./gradlew` are the same."
- "`build` only compiles." No: it also runs tests and other checks.
- "UP-TO-DATE means nothing happened." It means Gradle verified that inputs and outputs are unchanged.
- "The JDK in my terminal is the one compiling my code." That is not true once toolchains are set.
- "I need to install Gradle." Only once, to bootstrap a new build. After that, always use the wrapper.

**Hands-on exercises:**
1. Run Demo A. Predict which lines print for `hello`, `bad`, `tasks` and a second `hello`, then check. Fix `bad` by capturing `val v = project.version.toString()` at configuration time and using `v` inside `doLast`.
2. Run `./gradlew :app:assemble --task-graph` and draw the DAG by hand. Then run `./gradlew build --dry-run`.
3. Create the wrapper, then look at `gradle-wrapper.properties`. Add `distributionSha256Sum` using the checksum from `services.gradle.org/versions/current`. Then break one character and watch the download get refused. (The refusal behaviour is from the docs and was not run here.)
4. Build twice. Change a comment, a function body, then a public signature in `greeting`, and record which tasks re-run each time.
5. Run `./gradlew --status`, `./gradlew --stop`, then time a cold build against a warm one.

**Resources (Lesson 1):**
- [Gradle docs: Build Lifecycle](https://docs.gradle.org/current/userguide/build_lifecycle.html) (search result)
- [Gradle tutorial Part 2: The Build Lifecycle](https://docs.gradle.org/current/userguide/part2_build_lifecycle.html) (search result)
- [What's new in Gradle 9](https://gradle.org/whats-new/gradle-9/) (opened)
- [Road to Gradle 9 (Gradle blog)](https://blog.gradle.org/road-to-gradle-9) (search result; not opened)
- [Gradle wrapper reference (source)](https://raw.githubusercontent.com/gradle/gradle/v9.8.2/platforms/documentation/docs/src/docs/userguide/reference/runtime-configuration/gradle_wrapper.adoc) (opened)
- Video: [Gradle Course for Beginners](https://www.youtube.com/watch?v=R6Z-Sxb837I) (search result for "Tom Gregory Gradle beginners course". Not opened because youtube.com is blocked. Older than Gradle 9, so the DSL details may be dated)
- Video: [Gradle Tutorial — why you should use it and how to get started](https://www.youtube.com/watch?v=ojx49J1JCdQ) (search result. The snippet links Tom Gregory's quick-start guide. Not opened)
- Video: [Gradle Build Tool in 100 Seconds](https://www.youtube.com/watch?v=kNswjy2hPHI) (search result. Channel and date not verified)

### Gaps
- The docs.gradle.org pages could not be opened, so the exact current headings and wording of the lifecycle page are known only from search snippets and the GitHub sources.
- No official Gradle YouTube channel video (for example from DPE Summit or Devoxx) appeared in the search results. The Gradle site navigation lists a "YouTube Channel" link, but its URL was not captured.

---

## Key question 7 (Lesson 2 plan): dependencies and multi-project builds

### Takeaway
Dependencies are declared per **configuration** (`implementation`, `api`, `compileOnly`, `runtimeOnly`, `testImplementation`) and resolved into separate classpaths. When versions conflict, the highest wins by default, and `dependencyInsight` explains why. Centralise versions in a catalog and align families with platforms (BOMs). Share build logic with convention plugins in an included `build-logic` build, and publish with `maven-publish`.

### Cited Findings
**Concepts in teaching order**
1. **Repositories.** Where artifacts come from: `mavenCentral()`, `gradlePluginPortal()`, internal mirrors. Best practice: "Set up your Dependency Repositories in the Settings file" and "Use Content Filtering with multiple Repositories" — [best_practices_dependencies.adoc](https://raw.githubusercontent.com/gradle/gradle/v9.8.2/platforms/documentation/docs/src/docs/userguide/best-practices/best_practices_dependencies.adoc). `jcenter()` is gone in 9.0 — [upgrading_major_version_9.adoc](https://raw.githubusercontent.com/gradle/gradle/v9.8.0/platforms/documentation/docs/src/docs/userguide/releases/upgrading/upgrading_major_version_9.adoc). Intro: [dependency_management_basics.html](https://docs.gradle.org/userguide/dependency_management_basics.html) (search result).
2. **Configurations.**
   - `implementation`: needed to compile and run, hidden from consumers.
   - `api`: part of your public surface, so it lands on consumers' compile classpath. Requires the `java-library` plugin.
   - `compileOnly`: needed only to compile, for example annotations or a provided servlet API.
   - `runtimeOnly`: needed only at runtime, for example a JDBC driver.
   - `testImplementation` / `testRuntimeOnly`.
   - Source: [java_library_plugin.html](https://docs.gradle.org/current/userguide/java_library_plugin.html) (search result); [Tom Gregory](https://tomgregory.com/how-to-use-gradle-api-vs-implementation-dependencies-with-the-java-library-plugin) (search result).
3. **Transitive dependencies and conflict resolution.** Gradle walks the graph. When two versions of a module meet, it picks the highest — sandbox `dependencyInsight` ("By conflict resolution"). Constraints, `strictly`, rich versions: [dependency_constraints_conflicts.adoc](https://raw.githubusercontent.com/gradle/gradle/v9.8.2/platforms/documentation/docs/src/docs/userguide/reference/dependency-management/basics/dependency_constraints_conflicts.adoc) (path from the 9.8.2 repo tree, URL checked to return 200; content not read).
4. **Inspecting.** `./gradlew :app:dependencies --configuration runtimeClasspath` and `./gradlew :app:dependencyInsight --dependency <name> --configuration <cfg>`. The report suggests "A web-based, searchable dependency report is available by adding the --scan option." — sandbox run.
5. **Version catalogs.**
   - `gradle/libs.versions.toml` has `[versions]`, `[libraries]`, `[bundles]` and `[plugins]` sections, used as `libs.x.y` / `alias(libs.plugins.x)`.
   - You can add extra catalogs in settings.
   - A catalog can be published.
   - Source: [version_catalogs.html](https://docs.gradle.org/current/userguide/version_catalogs.html) (search result).
   - Best practices: "Use Version Catalogs to Centralize Dependency Versions" and "Name Version Catalog Entries Appropriately" — [best_practices_dependencies.adoc](https://raw.githubusercontent.com/gradle/gradle/v9.8.2/platforms/documentation/docs/src/docs/userguide/best-practices/best_practices_dependencies.adoc).
   - A forum thread notes older pages show the file at the repo root, while the current convention is `gradle/` — [discuss.gradle.org thread](https://discuss.gradle.org/t/libs-version-toml-documentation-confusion/52056) (search result).
6. **Platforms and BOMs.** `implementation(platform("group:bom:ver"))` imports recommended versions. `enforcedPlatform` "converts every version constraint from the BOM into a `strictly` declaration". Any POM with `<dependencyManagement>` can be used as a platform. Custom platforms use the `java-platform` plugin and can be published as BOMs — [platforms.adoc](https://raw.githubusercontent.com/gradle/gradle/v9.8.2/platforms/documentation/docs/src/docs/userguide/reference/dependency-management/centralizing-dependencies/platforms.adoc) (opened).
7. **Multi-project builds.** `include("app", "greeting")`, `project(":greeting")` dependencies, task paths such as `:greeting:test`, running `build` from the root builds all projects. Best practices: "Modularize Your Builds", "Do Not Put Source Files in the Root Project", "Avoid Unintentionally Creating Empty Projects" — [best_practices_structuring_builds.adoc](https://raw.githubusercontent.com/gradle/gradle/v9.8.2/platforms/documentation/docs/src/docs/userguide/best-practices/best_practices_structuring_builds.adoc) (opened).
8. **Convention plugins (build-logic, included builds).**
   - "The preferred location for build logic is an included build (typically named `build-logic`), **not** in `buildSrc`." Included builds "are complete Gradle builds", "treated just like external dependencies".
   - Settings plugins belong in a separate minimal included build such as `build-logic-settings` — [best_practices_structuring_builds.adoc](https://raw.githubusercontent.com/gradle/gradle/v9.8.2/platforms/documentation/docs/src/docs/userguide/best-practices/best_practices_structuring_builds.adoc) (opened).
   - Official sample: [sample_sharing_convention_plugins_with_build_logic](https://docs.gradle.org/current/samples/sample_sharing_convention_plugins_with_build_logic.html) (search result).
   - Real-world example: [Now in Android build-logic README](https://github.com/android/nowinandroid/blob/main/build-logic/README.md) (search result). It keeps one-off logic in the module's own build script.
   - Gotcha from the forums: a build-logic plugin needing a custom repository must also declare it in `pluginManagement` of the consuming settings — [discuss.gradle.org](https://discuss.gradle.org/t/migrating-from-buildsrc-to-build-logic-for-convention-plugins-with-multiple-repositories/47028) (search result).
   - `gradle init --split-project` generates precompiled script plugins named `buildlogic.kotlin-common-conventions` etc. under `buildSrc/src/main/kotlin`, applied with `id("buildlogic.kotlin-library-conventions")`. Its `buildSrc/settings.gradle.kts` reuses the main catalog: `versionCatalogs { create("libs") { from(files("../gradle/libs.versions.toml")) } }` — sandbox run.
9. **Publishing.** The `maven-publish` plugin. 9.8 makes POM generation take part in up-to-date checks ("`> Task :generatePomFileForMavenPublication UP-TO-DATE`"), unless a `withXml` action is registered — [9.8.0 notes](https://raw.githubusercontent.com/gradle/gradle/v9.8.0/platforms/documentation/docs/src/docs/release/notes.md). Maven Publish is a core plugin with only limited configuration cache support, so it triggers the graceful fallback — [9.0.0 notes](https://raw.githubusercontent.com/gradle/gradle/v9.0.0/platforms/documentation/docs/src/docs/release/notes.md). Setup reference: `publishing_setup.adoc` exists in the 9.8.2 docs tree (not opened).

**Observed outputs (sandbox run, `try/mini`)**

`./gradlew :app:dependencies --configuration runtimeClasspath`:
```
runtimeClasspath - Runtime classpath of 'main'.
+--- org.jetbrains.kotlin:kotlin-stdlib:2.4.21
|    \--- org.jetbrains:annotations:13.0
+--- project ':greeting'
|    +--- org.jetbrains.kotlin:kotlin-stdlib:2.4.21 (*)
|    \--- org.apache.commons:commons-text:1.14.0
|         \--- org.apache.commons:commons-lang3:3.18.0
\--- org.apache.commons:commons-lang3:3.17.0 -> 3.18.0
```
`./gradlew :app:dependencies --configuration compileClasspath`. Note that commons-text is absent (it is `implementation` in greeting) and lang3 is still 3.17.0:
```
compileClasspath - Compile classpath for 'main'.
+--- org.jetbrains.kotlin:kotlin-stdlib:2.4.21
|    \--- org.jetbrains:annotations:13.0
+--- project ':greeting'
|    \--- org.jetbrains.kotlin:kotlin-stdlib:2.4.21 (*)
\--- org.apache.commons:commons-lang3:3.17.0
```
`./gradlew :app:dependencyInsight --dependency commons-lang3 --configuration runtimeClasspath` (trimmed):
```
org.apache.commons:commons-lang3:3.18.0
  Variant runtime:
    | Attribute Name                     | Provided     | Requested    |
    | org.gradle.usage                   | java-runtime | java-runtime |
    | org.gradle.jvm.version             |              | 21           |
   Selection reasons:
      - By conflict resolution: between versions 3.18.0 and 3.17.0
org.apache.commons:commons-lang3:3.18.0
\--- org.apache.commons:commons-text:1.14.0
     \--- project ':greeting'
          \--- runtimeClasspath
org.apache.commons:commons-lang3:3.17.0 -> 3.18.0
\--- runtimeClasspath
```
BOM in action (`greeting` testRuntimeClasspath after adding `testImplementation(platform(libs.junit.bom))`):
```
+--- org.jetbrains.kotlin:kotlin-test -> 2.4.21
|    \--- org.jetbrains.kotlin:kotlin-test-junit5:2.4.21
|         +--- org.junit.jupiter:junit-jupiter-engine:5.10.1 -> 6.1.3
|         |    +--- org.junit:junit-bom:6.1.3
|         |    |    +--- org.junit.jupiter:junit-jupiter-engine:6.1.3 (c)
|         |    |    +--- org.junit.platform:junit-platform-launcher:6.1.3 (c)
```
`implementation` leakage test. Adding `import org.apache.commons.text.WordUtils` in `app` gives:
```
> Task :app:compileKotlin FAILED
e: file:///.../app/src/main/kotlin/demo/app/Leak.kt:3:27 Unresolved reference 'text'.
e: file:///.../app/src/main/kotlin/demo/app/Leak.kt:5:24 Unresolved reference 'WordUtils'.
```
After changing greeting to `api(libs.commons.text)`: `BUILD SUCCESSFUL`.

### Inferences
**Misconceptions:**
- "`api` is the safe default." It isn't: it leaks dependencies and causes more recompilation. Default to `implementation`, and use `api` only for types that appear in your public signatures.
- "The version in my build file is the version at runtime." Show the `->` arrow and `dependencyInsight`.
- "The compile and runtime classpaths are the same." The demo above shows lang3 3.17.0 at compile time and 3.18.0 at runtime. Mention `java { consistentResolution { useCompileClasspathVersions() } }` as the fix (from the author's knowledge, not verified here).
- "A version catalog enforces versions." It doesn't: a catalog only *names* coordinates. Platforms and constraints *influence resolution*.
- "buildSrc is the recommended place for shared logic." Gradle now recommends `build-logic`.
- "`allprojects {}`/`subprojects {}` is how you share config." Use convention plugins instead.

**Hands-on exercises:**
1. Run `dependencies` and `dependencyInsight` on the demo, and explain each `->` and `(*)`.
2. Flip `implementation` to `api` and watch the compile error disappear. Then discuss which one is right.
3. Add `junit-bom` as a platform and see 5.10.1 become 6.1.3. Then try `enforcedPlatform` with an older BOM and observe the downgrade.
4. Extract the repeated toolchain and test config into `build-logic` (`build-logic/settings.gradle.kts`, `build-logic/build.gradle.kts` with `` `kotlin-dsl` ``, `src/main/kotlin/kotlin-conventions.gradle.kts`). Wire it with `pluginManagement { includeBuild("build-logic") }`. Edit the convention and see which tasks re-run.
5. Add `maven-publish` to `greeting`, run `./gradlew :greeting:publishToMavenLocal`, then inspect the POM scopes (`compile` vs `runtime`).

**Resources (Lesson 2):**
- [Java Library plugin (api vs implementation)](https://docs.gradle.org/current/userguide/java_library_plugin.html) (search result)
- [Version catalogs](https://docs.gradle.org/current/userguide/version_catalogs.html) (search result)
- [Platforms and BOMs (source)](https://raw.githubusercontent.com/gradle/gradle/v9.8.2/platforms/documentation/docs/src/docs/userguide/reference/dependency-management/centralizing-dependencies/platforms.adoc) (opened)
- [Sample: sharing convention plugins with build-logic](https://docs.gradle.org/current/samples/sample_sharing_convention_plugins_with_build_logic.html) (search result)
- [Best practices: structuring builds (source)](https://raw.githubusercontent.com/gradle/gradle/v9.8.2/platforms/documentation/docs/src/docs/userguide/best-practices/best_practices_structuring_builds.adoc) (opened)
- [Tom Gregory: api vs implementation](https://tomgregory.com/how-to-use-gradle-api-vs-implementation-dependencies-with-the-java-library-plugin) (search result)
- [Now in Android build-logic README](https://github.com/android/nowinandroid/blob/main/build-logic/README.md) (search result. A real-world convention-plugin layout)
- Video: [Gradle for Beginners Series (playlist)](https://www.youtube.com/playlist?list=PL0UJI1nZ56yDZSgsL1Gf4_krgTMhuotYM) (search result for the Tom Gregory query. Channel not verified)

### Gaps
- The convention-plugin (`build-logic`) and `maven-publish` steps were not executed in the sandbox. The file sketches follow the documented pattern but are untested.
- Dependency *constraints*, rich versions and `resolutionStrategy` were not explored in depth, beyond the docs tree paths.

---

## Key question 8 (Lesson 3 plan): fast, reliable builds in CI and containers

### Takeaway
Speed comes from not redoing work:
- up-to-date checks within a workspace
- the build cache across workspaces and machines
- the configuration cache for the configuration phase
- the daemon for a warm JVM
- parallel project execution

Reliability comes from pinning everything: the wrapper checksum, toolchains, dependency locking and verification. In GitHub Actions, use `gradle/actions/setup-gradle@v6` and nothing else for Gradle caching. To containerise, choose a multi-stage Dockerfile, Jib (no Dockerfile or daemon needed to push, though not configuration-cache compatible), Spring Boot `bootBuildImage` (buildpacks), or Quarkus container-image extensions.

### Cited Findings
**Concepts in teaching order**
1. **Incremental builds and up-to-date checks.** Tasks declare inputs and outputs, and unchanged ones are skipped. Compile avoidance means ABI-identical class files don't recompile consumers — sandbox demo (Lesson 1). Missing inputs cause wrong cache hits: "Missing task inputs can cause incorrect cache hits" — [build_cache.adoc](https://raw.githubusercontent.com/gradle/gradle/v9.8.2/platforms/documentation/docs/src/docs/userguide/optimizing-builds/build-cache/build_cache.adoc) (opened).
2. **Build cache.**
   - Turn it on with `--build-cache` or `org.gradle.caching=true`. A hit shows as `FROM-CACHE` — same source.
   - Sandbox: `./gradlew clean build` with the cache on gave `13 actionable tasks: 7 executed, 6 from cache` (`compileKotlin`, `compileTestKotlin` and `test` all `FROM-CACHE`).
   - Remote cache: CI pushes and developers pull. Develocity tutorials show the local cache disabled and the remote set to push on CI — [docs.gradle.com/develocity/get-started](https://docs.gradle.com/develocity/get-started) and the [legacy caching tutorial](https://docs.gradle.com/develocity/tutorials/caching) (search results. The tutorial uses the older `remote(HttpBuildCache)` syntax).
   - setup-gradle recommends: "Enable remote build-cache push for your GitHub Actions builds. Disable local build-cache for your GitHub Actions build" when a remote cache exists — [setup-gradle.md](https://raw.githubusercontent.com/gradle/actions/main/docs/setup-gradle.md) (opened).
3. **Configuration cache.**
   - Caches the task graph, so a hit skips settings and build-script evaluation (sandbox lifecycle demo).
   - It is the preferred mode in 9.x, and the goal is to make it the default in Gradle 10 — [9.0.0 notes](https://raw.githubusercontent.com/gradle/gradle/v9.0.0/platforms/documentation/docs/src/docs/release/notes.md); [gradle.org/whats-new/gradle-9](https://gradle.org/whats-new/gradle-9/).
   - Read-only mode for PR builds: `-Dorg.gradle.configuration-cache.read-only=true` (9.1).
   - Entries are encrypted (since 8.1, per What's New). setup-gradle can carry them between CI runs with `cache-encryption-key`.
   - Adoption guide: [configuration_cache_adoption.html](https://docs.gradle.org/current/userguide/configuration_cache_adoption.html) (search result).
4. **Daemon.**
   - On by default (`org.gradle.daemon=true`). Stops after 3 idle hours. `--status` and `--stop`.
   - New JVM args mean a new daemon — [gradle_daemon.adoc](https://raw.githubusercontent.com/gradle/gradle/v9.8.2/platforms/documentation/docs/src/docs/userguide/reference/runtime-configuration/gradle_daemon.adoc) (opened).
   - Daemon JVM criteria: `./gradlew updateDaemonJvm --jvm-version=17` writes `gradle/gradle-daemon-jvm.properties`. Stable since 9.2 — same source and the [9.2 notes](https://raw.githubusercontent.com/gradle/gradle/v9.2.0/platforms/documentation/docs/src/docs/release/notes.md).
   - In CI, setup-gradle "will stop all running Gradle daemons in the post-action step, before saving the Gradle User Home state". It does not do this if caching is disabled or read-only — [setup-gradle.md](https://raw.githubusercontent.com/gradle/actions/main/docs/setup-gradle.md).
5. **Parallel execution.**
   - `org.gradle.parallel=true` runs tasks in *different* projects in parallel.
   - `org.gradle.jvmargs=-Xmx2048M` is shown as a tuning knob.
   - Relying on `org.gradle.tooling.parallel` defaulting from `org.gradle.parallel` is deprecated.
   - Source: [performance.adoc](https://raw.githubusercontent.com/gradle/gradle/v9.8.2/platforms/documentation/docs/src/docs/userguide/optimizing-builds/performance.adoc) (opened).
   - 9.7's Isolated Projects (incubating) extends parallelism to configuration — [9.7 notes](https://raw.githubusercontent.com/gradle/gradle/v9.7.0/platforms/documentation/docs/src/docs/release/notes.md).
6. **Toolchains.**
   - `kotlin { jvmToolchain(21) }` or `java { toolchain { languageVersion = JavaLanguageVersion.of(21) } }`.
   - Auto-provisioning "only kicks in when auto-detection fails to find a matching JDK" and needs a resolver plugin such as foojay.
   - Turn it off with `org.gradle.java.installations.auto-download=false`.
   - Source: [toolchains.adoc](https://raw.githubusercontent.com/gradle/gradle/v9.8.2/platforms/documentation/docs/src/docs/userguide/reference/platforms/jvm/toolchains.adoc) (opened); [Kotlin Gradle docs](https://kotlinlang.org/docs/gradle-configure-project.html) (opened).
7. **Build Scans and Develocity.**
   - `--scan` publishes to the free scans.gradle.com after you accept the terms. Every failure footer in 9.8.2 says "Run with --scan to get full insights from a Build Scan (powered by Develocity)" — sandbox run.
   - In CI, use `build-scan-publish: true` plus `build-scan-terms-of-use-url: 'https://gradle.com/terms-of-service'` and `build-scan-terms-of-use-agree: 'yes'` — [setup-gradle.md](https://raw.githubusercontent.com/gradle/actions/main/docs/setup-gradle.md).
   - 9.5's `--develocity-url` publishes to a private server without changing the build — [9.5 notes](https://raw.githubusercontent.com/gradle/gradle/v9.5.0/platforms/documentation/docs/src/docs/release/notes.md).
   - The plugin is `com.gradle.develocity` (4.6.1), applied in settings — [Develocity get-started](https://docs.gradle.com/develocity/get-started) (search result); plugin portal.
   - Gradle Inc. now brands itself "Gradle by Develocity" ("Gradle Technologies is now Develocity") — [gradle.org/whats-new/gradle-9](https://gradle.org/whats-new/gradle-9/) page title (opened); [gradle.org/maven-and-gradle](https://gradle.org/maven-and-gradle) search-result title.
8. **Dependency verification and locking.**
   - **Verification:** `gradle/verification-metadata.xml` turns on automatically when present. Generate it with `./gradlew --write-verification-metadata sha256 help` (a dry-run mode exists). Trusted PGP keys can be recorded. Checksums must be updated on every dependency upgrade — [dependency_verification.html](https://docs.gradle.org/current/userguide/dependency_verification.html) (search result); [Android: dependency verification](https://developer.android.com/build/dependency-verification) (search result). 9.7 lets you document "the origin and reason of trusted PGP keys" — [9.7 notes](https://raw.githubusercontent.com/gradle/gradle/v9.7.0/platforms/documentation/docs/src/docs/release/notes.md).
   - **Locking:**
     - Turn it on with `dependencyLocking { lockAllConfigurations() }` (or `activateDependencyLocking()` per configuration).
     - Write locks with `./gradlew dependencies --write-locks`. They go to a `gradle.lockfile` per project, plus `buildscript-gradle.lockfile`.
     - Update selectively with `--update-locks org.apache.commons:commons-lang3,...`.
     - Source: [dependency_locking.adoc](https://raw.githubusercontent.com/gradle/gradle/v9.8.2/platforms/documentation/docs/src/docs/userguide/reference/dependency-management/dependency-management/dependency_locking.adoc) (opened).
   - **Wrapper:** `distributionSha256Sum` (above). setup-gradle validates `gradle-wrapper.jar` checksums on every run (since v4). A standalone `gradle/actions/wrapper-validation@v6` also exists — [gradle/actions README](https://raw.githubusercontent.com/gradle/actions/main/README.md).
9. **Gradle in GitHub Actions (`gradle/actions/setup-gradle@v6`).**
   - It configures env vars and init scripts, so every later `./gradlew` step benefits. It caches part of Gradle User Home (dependencies, wrapper dists, local build cache) and writes only from the default branch.
   - It generates Job Summaries and captures Build Scan links. It can submit a dependency graph (`gradle/actions/dependency-submission@v6`) for Dependabot alerts.
   - Source: [setup-gradle.md](https://raw.githubusercontent.com/gradle/actions/main/docs/setup-gradle.md); [README](https://raw.githubusercontent.com/gradle/actions/main/README.md) (opened).
   - **v6 licensing change.** The default `cache-provider: enhanced` uses the *proprietary* `gradle-actions-caching` library. It is "free for all public repositories" and in a "Free Preview" for private repositories, with "usage-based pricing for large-scale commercial organizations in the future". `cache-provider: basic` is MIT-licensed, a thin wrapper over `actions/cache` keyed on build-file hashes with no restore keys. `external` turns off its caching — [DISTRIBUTION.md](https://raw.githubusercontent.com/gradle/actions/main/DISTRIBUTION.md); [README](https://raw.githubusercontent.com/gradle/actions/main/README.md) (opened).
10. **Containerising a JVM app.**
    - **Jib:**
      - Builds OCI images without a Dockerfile. `jib` pushes to a registry with no Docker daemon needed. `jibDockerBuild` loads into the local daemon. `jibBuildTar` writes `build/jib-image.tar`.
      - The default base is `eclipse-temurin:{8,11,17,21,25}-jre`. The default `platforms` is `architecture amd64, os linux`.
      - Source: [jib-gradle-plugin README](https://raw.githubusercontent.com/GoogleContainerTools/jib/master/jib-gradle-plugin/README.md) (opened).
      - The default base image was distroless before Jib 3.0 — [Jib FAQ mirror](https://www.github.com/r4b3rt/jib/blob/master/docs/faq.md) (search result, third-party copy).
    - **Spring Boot:** `bootBuildImage` builds an OCI image with Cloud Native Buildpacks (Paketo). It needs a Docker daemon, and images run as non-root. The 4.2 docs list `paketobuildpacks/builder-noble-java-tiny:latest` as the default builder — [Spring Boot Gradle plugin: Packaging OCI Images](https://docs.spring.io/spring-boot/gradle-plugin/packaging-oci-image.html) (search result).
    - **Quarkus:**
      - The extensions are `quarkus-container-image-jib`, `-docker`, `-podman` and `-buildpack`. Add one with `./gradlew addExtension --extensions='container-image-jib'`, and build with `-Dquarkus.container-image.build=true` (push with `...push=true`).
      - Don't combine several builder extensions.
      - The docker extension uses the generated Dockerfiles in `src/main/docker`, and can build multi-arch images with buildx.
      - Source: [quarkus.io/guides/container-image](https://quarkus.io/guides/container-image) (search result).

**Observed outputs (sandbox run)**
- Jib added via the catalog (`jib = { id = "com.google.cloud.tools.jib", version = "3.5.4" }`) and configured in `app/build.gradle.kts`:
  ```kotlin
  plugins { /* ... */ alias(libs.plugins.jib) }
  jib {
      from { image = "gcr.io/distroless/java21-debian12" }
      to { image = "hello-gradle:0.1.0" }
  }
  ```
  `./gradlew :app:jibDockerBuild` with the configuration cache on: **failed** ("Invocation of 'Task.project' by task ':app:jibDockerBuild' at execution time is unsupported with the configuration cache", plus "cannot serialize object of type 'org.gradle.api.internal.project.DefaultProject'").
  `./gradlew :app:jibDockerBuild --no-configuration-cache`:
  ```
  Invocation of Task.project at execution time has been deprecated. This will fail with an error in Gradle 10. ...
  Containerizing application to Docker daemon as hello-gradle:0.1.0...
  Base image 'gcr.io/distroless/java21-debian12' does not use a specific image digest - build may not be reproducible
  Building dependencies layer...
  Building classes layer...
  Using base image with digest: sha256:f34fd3e4e2d7a246d764d0614f5e6ffb3a735930723fac4cfc25a72798950262
  Container entrypoint set to [java, -cp, @/app/jib-classpath-file, demo.app.MainKt]
  Built image to Docker daemon as hello-gradle:0.1.0
  BUILD SUCCESSFUL in 9s
  ```
  `docker images hello-gradle`: `hello-gradle:0.1.0 … 267MB disk / 65.8MB content`. `docker run --rm hello-gradle:0.1.0 "from a container"` printed `Hello, From A Container!`
  The first attempt with the default-style base `eclipse-temurin:21-jre` failed with Docker Hub `429 Too Many Requests … unauthenticated pull rate limit` (a sandbox network limit, not a Jib bug).
- The build cache hit after `clean` (above): `13 actionable tasks: 7 executed, 6 from cache`.

### Inferences
**GitHub Actions workflow for the demo project.** This is composed from the README example, adapted to Java 21 so it matches `jvmToolchain(21)` and foojay does not download a JDK. **Not run here.**
```yaml
name: ci
on:
  push:
    branches: [main]
  pull_request:
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v6
      - uses: actions/setup-java@v5
        with:
          distribution: temurin
          java-version: 21
      - uses: gradle/actions/setup-gradle@v6
        with:
          cache-encryption-key: ${{ secrets.GRADLE_ENCRYPTION_KEY }}  # lets configuration-cache entries be reused safely
          # cache-provider: basic   # opt out of the proprietary enhanced cache
      - run: ./gradlew build
```
Teaching points:
- Don't add `cache: gradle` to setup-java.
- PR branches only read the cache.
- `./gradlew build` reads `gradle.properties`, so the configuration cache, build cache and parallel flags apply in CI too.

**Multi-stage Dockerfile.** This is the author's sketch and was **not built here**. Docker Hub rate limits and the container's lack of the sandbox proxy CA prevented a test.
```dockerfile
# syntax=docker/dockerfile:1
FROM eclipse-temurin:21-jdk AS build
WORKDIR /src
# 1) wrapper + build scripts first: this layer changes rarely
COPY gradlew settings.gradle.kts build.gradle.kts gradle.properties ./
COPY gradle ./gradle
COPY app/build.gradle.kts app/
COPY greeting/build.gradle.kts greeting/
RUN ./gradlew --no-daemon help          # downloads Gradle + plugins into the image layer
# 2) sources: changes often
COPY app/src app/src
COPY greeting/src greeting/src
RUN --mount=type=cache,target=/root/.gradle/caches \
    ./gradlew --no-daemon :app:installDist
FROM eclipse-temurin:21-jre
WORKDIR /app
COPY --from=build /src/app/build/install/app/ ./
ENTRYPOINT ["./bin/app"]
```
Why it is shaped this way:
- Layer ordering keeps dependency downloads cached across source edits.
- `--no-daemon` because the container is single-use.
- The JRE-only runtime image is smaller.
- `installDist` (from the `application` plugin) gives `bin/` and `lib/` with no fat jar needed.
- On an M-series Mac, add `--platform linux/amd64` to `docker build` if the target cluster is amd64.

**Which container option when:**
- Multi-stage Dockerfile: universal and transparent, and the best for teaching.
- Jib: fast, reproducible layers and no Dockerfile. Pushes need no daemon. Today it needs `--no-configuration-cache` on Gradle 9 and will break on Gradle 10 unless updated.
- `bootBuildImage`: zero-config for Spring Boot, opinionated buildpacks, needs Docker.
- Quarkus: use its container-image extension, matched to the native or JVM mode.

**Misconceptions:**
- "The build cache and dependency cache are the same thing." The first caches task outputs; the second caches downloaded jars in `~/.gradle/caches/modules-2`.
- "CI should run `--no-daemon` and `clean build` every time." The `clean` throws away exactly what the caches save.
- "Configuration cache = build cache."
- "A cache key from `hashFiles('**/*.gradle*')` is enough." setup-gradle explains why it isn't.
- "Locking and verification are the same." Locking pins *which* version is used; verification checks the *bytes* are the expected ones.
- "Jib needs Docker." Only `jibDockerBuild` does.

**Hands-on exercises:**
1. Time `./gradlew clean build` with and without `--build-cache`, and count `FROM-CACHE`.
2. Turn the configuration cache on and fix the `bad` task.
3. Add `dependencyLocking { lockAllConfigurations() }`. Run `./gradlew dependencies --write-locks`, commit the `gradle.lockfile`, then bump a catalog version and watch the build fail until `--update-locks`.
4. Generate `verification-metadata.xml` with `--write-verification-metadata sha256 help`, then tamper with a checksum.
5. Push the workflow and read the Job Summary. Compare the first run (cache miss) with the second.
6. Build the image three ways (Dockerfile, `jibDockerBuild --no-configuration-cache`, and `bootBuildImage` for a Spring variant). Compare size, build time and layers (`docker history`).
7. On a Mac, set `jib.from.platforms` to arm64 and run natively, then compare with the default amd64.

**Resources (Lesson 3):**
- [Build cache (source)](https://raw.githubusercontent.com/gradle/gradle/v9.8.2/platforms/documentation/docs/src/docs/userguide/optimizing-builds/build-cache/build_cache.adoc) (opened)
- [Configuration cache](https://docs.gradle.org/current/userguide/configuration_cache.html) and [adoption guide](https://docs.gradle.org/current/userguide/configuration_cache_adoption.html) (search results)
- [setup-gradle documentation](https://raw.githubusercontent.com/gradle/actions/main/docs/setup-gradle.md) and [gradle/actions DISTRIBUTION.md](https://raw.githubusercontent.com/gradle/actions/main/DISTRIBUTION.md) (opened)
- [Dependency verification](https://docs.gradle.org/current/userguide/dependency_verification.html) (search result) and [dependency locking (source)](https://raw.githubusercontent.com/gradle/gradle/v9.8.2/platforms/documentation/docs/src/docs/userguide/reference/dependency-management/dependency-management/dependency_locking.adoc) (opened)
- [Toolchains (source)](https://raw.githubusercontent.com/gradle/gradle/v9.8.2/platforms/documentation/docs/src/docs/userguide/reference/platforms/jvm/toolchains.adoc) (opened)
- [Jib Gradle plugin README](https://raw.githubusercontent.com/GoogleContainerTools/jib/master/jib-gradle-plugin/README.md) (opened)
- [Spring Boot: Packaging OCI Images](https://docs.spring.io/spring-boot/gradle-plugin/packaging-oci-image.html) and [Quarkus: Container Images](https://quarkus.io/guides/container-image) (search results)
- [Develocity: get started](https://docs.gradle.com/develocity/get-started) (search result)
- Video: [Gradle project properties best practices (don't be that guy)](https://m.youtube.com/watch?v=BvXjlxJg2II) (search result for the Tom Gregory query. Not opened)

### Gaps
- The Dockerfile and the GitHub Actions workflow above were not executed. The workflow syntax comes from the gradle/actions README, and the Dockerfile is a sketch.
- No source this session confirms which `eclipse-temurin` tags are multi-arch (arm64). This is relevant for Apple Silicon.
- `bootBuildImage` and the Quarkus extensions were not run. Their details come from search-result summaries of the official docs, not from opened pages. The Spring search summary said 4.1.1 docs are "latest stable", while plugin-portal metadata shows 4.1.2. Trust the portal.
- No Build Scan was published (scans.gradle.com is blocked here), so no example scan URL is available.
- The current Develocity remote-cache Kotlin DSL syntax (`remote(develocity.buildCache)`) was mentioned in a search summary but not confirmed from a primary page.
- YouTube: none of the video URLs could be opened (youtube.com is blocked). Channel attribution relies on search snippets. No official Gradle channel, JetBrains or Devoxx talk on Gradle 9 surfaced within the search budget. Other video URLs from the search results, attribution unverified: ["How to do a Maven to Gradle migration on a Java Spring Boot project"](https://www.youtube.com/watch?v=izZ5_plW6tY&vl=en) and ["Build Java Software With Gradle Like a Pro"](https://www.youtube.com/watch?v=SJKXJHKTRX8).
