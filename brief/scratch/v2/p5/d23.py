from common import lab, svg, box, arrow, line, cap

# Day 23 catalog: the lab file without the [plugins] block that Day 24 adds.
CATALOG_D23 = lab("gradle/libs.versions.toml").split("\n[plugins]")[0].rstrip("\n")

diagram = svg(250, "app depends on greeting, which brings commons-text and commons-lang3 3.18.0; app also asks for commons-lang3 3.17.0; Gradle picks 3.18.0", "".join([
    box(16, 20, 104, 40, "bxo", "app"),
    box(200, 20, 120, 40, "bxt", "greeting"),
    box(400, 20, 144, 40, "bx", "commons-text"),
    box(16, 180, 160, 40, "bx", "lang3 3.17.0"),
    box(384, 180, 160, 40, "bxg", "lang3 3.18.0"),
    arrow(122, 40, 197, 40),
    arrow(322, 40, 397, 40),
    arrow(68, 62, 92, 177),
    arrow(472, 62, 466, 177),
    arrow(178, 200, 381, 200, dashed=True),
    cap(160, 32, "implementation"),
    cap(360, 32, "implementation"),
    cap(40, 124, "asks for", "start"),
    cap(476, 124, "needs", "start"),
    cap(280, 192, "highest wins"),
    cap(280, 240, "runtime classpath gets 3.18.0"),
]))

L = {
    "id": "d23",
    "title": "Dependencies and multi-project builds",
    "minutes": 50,
    "goal": "By the end you can declare dependencies in the right configuration, explain which version Gradle picked and why, and split a build into projects that share a version catalog and a convention plugin.",
    "guess": {
        "q": "Your app asks for commons-lang3 3.17.0. A library your app uses needs commons-lang3 3.18.0. Which version is on the app's runtime classpath?",
        "options": [
            "3.17.0, because your own declaration wins",
            "3.18.0, because Gradle picks the highest",
            "Both, each library gets its own copy",
            "Neither: the build stops with a conflict",
        ],
        "answer": 1,
        "why": "When two versions of one library meet, Gradle picks the highest by default. Maven picks the declaration nearest your project instead, so the same dependencies can resolve differently there.",
    },
    "terms": [
        {"term": "Repository", "plain": "A server that stores published libraries and plugins, such as Maven Central."},
        {"term": "Coordinates", "plain": "The group, name and version that identify a library, written as group:name:version."},
        {"term": "Dependency configuration", "plain": "A named bucket such as implementation or api that decides which classpaths a dependency joins."},
        {"term": "Transitive dependency", "plain": "A library you get because a library you asked for needs it."},
        {"term": "Conflict resolution", "plain": "Gradle's rule for picking one version when several are requested; by default the highest version wins."},
        {"term": "Version catalog", "plain": "The file gradle/libs.versions.toml, which names your libraries and plugins and their versions in one place."},
        {"term": "Platform (BOM)", "plain": "A published list of versions for a family of libraries, added with platform(...) so they move together."},
        {"term": "Convention plugin", "plain": "Your own small plugin, kept in build-logic, that holds setup shared by several projects."},
    ],
    "sections": [
        {
            "h": "Repositories and coordinates",
            "body": (
                "A dependency is a library your code needs, such as JUnit or a JSON parser. To fetch one, Gradle needs two facts: where to look and what to ask for.\n\n"
                "Where to look is a repository, a server that stores published jars with their metadata. You will meet three kinds:\n\n"
                "- Maven Central (`mavenCentral()`), where most open-source JVM libraries live\n"
                "- the Gradle Plugin Portal (`gradlePluginPortal()`), where most Gradle plugins live\n"
                "- your company's own repository, often a mirror of both (Nexus or Artifactory)\n\n"
                "What to ask for is the coordinates: group, name and version in one string. `org.junit:junit-bom:6.1.3` has the group `org.junit`, the name `junit-bom` and the version `6.1.3`. Maven uses the same coordinates. Gradle downloads each file once into `~/.gradle/caches/modules-2` and reuses it in every project on your laptop.\n\n"
                "Declare repositories once, in `settings.gradle.kts`. In hello-jvm, `repositoriesMode = RepositoriesMode.FAIL_ON_PROJECT_REPOS` fails the build if a project adds its own. That sounds strict, but at work it is what you want. There is one place to point at the company mirror, and no project can quietly pull from a random server."
            ),
            "refs": [
                {"title": "Gradle docs: Dependency management basics", "url": "https://docs.gradle.org/current/userguide/dependency_management_basics.html", "kind": "docs"},
            ],
        },
        {
            "h": "Configurations: which classpath a dependency joins",
            "body": (
                "You never add a dependency to a project in general. You add it to a configuration, and the configuration decides which classpaths it joins. A classpath is the list of jars that the compiler or the JVM can see. Each project has one for compiling the main code, one for running it, and the same two for tests. The configurations you will use:\n\n"
                "- `implementation`: needed to compile and run this project. Projects that use yours cannot see it when they compile.\n"
                "- `api`: like `implementation`, but also on the compile classpath of every project that uses yours. It needs the `java-library` plugin.\n"
                "- `compileOnly`: needed to compile, but provided by someone else at runtime.\n"
                "- `runtimeOnly`: needed only when the program runs, such as a database driver.\n"
                "- `testImplementation` and `testRuntimeOnly`: the same ideas, for the tests.\n\n"
                "Make `implementation` your default. It keeps a library's insides private: a consumer cannot import a class from a library you only use internally. It also saves build time. When you upgrade an `implementation` dependency, the projects that use yours do not recompile.\n\n"
                "Use `api` only when a type from that library appears in your public functions. If your function returns a `Money` from a money library, every caller needs that library to compile, so it is part of your API."
            ),
            "refs": [
                {"title": "Gradle docs: The Java Library plugin (api and implementation)", "url": "https://docs.gradle.org/current/userguide/java_library_plugin.html", "kind": "docs"},
                {"title": "Tom Gregory: How to use Gradle api vs implementation dependencies", "url": "https://tomgregory.com/how-to-use-gradle-api-vs-implementation-dependencies-with-the-java-library-plugin", "kind": "read"},
            ],
        },
        {
            "h": "Transitive dependencies and highest-wins",
            "body": (
                "Libraries have dependencies of their own. Ask for `commons-text` and you also get `commons-lang3`, because `commons-text` needs it. These are transitive dependencies, and in a real service they often outnumber the ones you declared.\n\n"
                "Sooner or later, two paths ask for different versions of the same library. Gradle settles this conflict with one rule: the highest version wins. Your own declaration gets no extra weight. This surprises people who know Maven, where the declaration nearest your project wins.\n\n"
                "Two reports show what really happened:\n\n"
                "- `./gradlew :app:dependencies --configuration runtimeClasspath` prints the whole tree. An arrow such as `3.17.0 -> 3.18.0` means one version was asked for and another was chosen. `(*)` marks a subtree already printed above.\n"
                "- `./gradlew :app:dependencyInsight --dependency commons-lang3 --configuration runtimeClasspath` explains one library: the version picked, the reason (such as `By conflict resolution`) and every path that asked for it.\n\n"
                "Gradle resolves each classpath separately. So the compile classpath can hold 3.17.0 while the runtime classpath holds 3.18.0. The worked example shows exactly that, and the deeper section shows how to make the two agree."
            ),
            "refs": [
                {"title": "Gradle docs: Viewing dependencies", "url": "https://docs.gradle.org/current/userguide/viewing_debugging_dependencies.html", "kind": "docs"},
                {"title": "Gradle docs: Graph resolution", "url": "https://docs.gradle.org/current/userguide/graph_resolution.html", "kind": "docs"},
            ],
        },
        {
            "h": "Version catalogs: one file for names and versions",
            "body": (
                "In a build with ten projects, the same version string ends up in ten build files, and one upgrade means ten edits. A version catalog fixes that. It is a TOML file at `gradle/libs.versions.toml`, and Gradle reads it automatically. It has up to four sections:\n\n"
                "- `[versions]`: named version numbers, such as `kotlin = \"2.4.21\"`\n"
                "- `[libraries]`: short names for coordinates, such as `junit-bom`\n"
                "- `[bundles]`: groups of libraries you often add together\n"
                "- `[plugins]`: names for plugins and their versions\n\n"
                "Build scripts then say `libs.junit.bom` instead of `\"org.junit:junit-bom:6.1.3\"`, and `alias(libs.plugins.jib)` for a plugin. Dashes in names become dots. IntelliJ completes these names, and a typo fails the build at once instead of fetching the wrong thing.\n\n"
                "Know what a catalog does not do. It only gives names to coordinates. It does not force any version onto the dependency graph, so highest-wins still decides the transitive ones. That job belongs to platforms, next."
            ),
            "refs": [
                {"title": "Gradle docs: Version catalogs", "url": "https://docs.gradle.org/current/userguide/version_catalogs.html", "kind": "docs"},
                {"title": "Understanding Gradle #09: catalogs, platforms and constraints (Jendrik Johannes)", "url": "https://www.youtube.com/watch?v=8044F5gc1dE", "kind": "watch"},
            ],
        },
        {
            "h": "Platforms and BOMs: versions that move together",
            "body": (
                "Some libraries come as a family of modules that must share one version. JUnit is one: `junit-jupiter-api`, `junit-jupiter-engine` and `junit-platform-launcher` have to match, or tests fail in confusing ways.\n\n"
                "A BOM (bill of materials) is a published list of recommended versions for such a family. Gradle calls it a platform, and you add it like a dependency, wrapped in `platform(...)`. hello-jvm does this in its convention plugin: `testImplementation(platform(...junit-bom...))`.\n\n"
                "Here is why. `kotlin(\"test\")` pulls in `kotlin-test-junit5`, which asks for JUnit 5.10.1. The JUnit 6.1.3 BOM moves every JUnit module to 6.1.3. The dependency report shows it as `junit-jupiter-engine:5.10.1 -> 6.1.3`, with lines marked `(c)` for the BOM's constraints.\n\n"
                "You will see BOMs all over the JVM world. Spring Boot and Jackson both publish one. A normal `platform()` takes part in highest-wins like everything else. `enforcedPlatform()` forces its versions, even downward. Use it rarely, because it can silently downgrade something a library needs."
            ),
            "refs": [
                {"title": "Gradle docs: Centralizing dependencies (catalogs and platforms)", "url": "https://docs.gradle.org/current/userguide/centralizing_dependencies.html", "kind": "docs"},
            ],
        },
        {
            "h": "Multi-project builds",
            "body": (
                "So far hello-jvm has one project. Today you split it in two:\n\n"
                "- `greeting` is a library. It builds the JSON reply, escapes text properly, and knows nothing about HTTP.\n"
                "- `app` is the web service. It depends on `greeting` and adds the server.\n\n"
                "Why bother for a tiny service? The Day 22 version builds JSON by gluing strings. Start it with a `GREETING` that contains a double quote and `curl` returns `{\"message\":\"Say \"hi\"\",...}`, which no JSON parser accepts. Escaping is exactly the kind of logic that deserves its own module and its own tests. In a big codebase the same split gives clear boundaries and faster builds, because a change in `app` never recompiles `greeting`.\n\n"
                "The wiring is two lines. `include(\"app\", \"greeting\")` in the settings file declares both projects. `implementation(project(\":greeting\"))` in `app/build.gradle.kts` makes `app` use `greeting` like any library, except that Gradle builds it first.\n\n"
                "Task paths matter now. `./gradlew build` at the root builds both projects. `./gradlew :greeting:test` tests only the library. `./gradlew :app:build` builds `app` and only the parts of `greeting` it needs, such as its jar. `./gradlew projects` prints the tree."
            ),
            "refs": [
                {"title": "Gradle docs: Structuring multi-project builds", "url": "https://docs.gradle.org/current/userguide/multi_project_builds_intermediate.html", "kind": "docs"},
            ],
        },
        {
            "h": "Share setup with a convention plugin",
            "body": (
                "Split a build and the build scripts start repeating themselves. Both projects need the Kotlin plugin, `jvmToolchain(21)`, kotlin.test, the JUnit BOM and `useJUnitPlatform()`. Copy that into ten projects and the copies drift apart. Older builds put shared setup in `allprojects {}` or `subprojects {}` blocks in the root script. Gradle now advises against that, because it ties every project to the root.\n\n"
                "The current answer is a **convention plugin**: your own small plugin that holds the shared setup. In hello-jvm it lives in `build-logic`, a separate little Gradle build inside the repository:\n\n"
                "1. `settings.gradle.kts` says `pluginManagement { includeBuild(\"build-logic\") }`, so Gradle builds `build-logic` first and offers its plugins.\n"
                "2. `build-logic/build.gradle.kts` applies `kotlin-dsl`, which turns each `*.gradle.kts` file in `src/main/kotlin` into a plugin.\n"
                "3. The file `hello.kotlin-jvm.gradle.kts` becomes the plugin `hello.kotlin-jvm`.\n"
                "4. Each project applies it with `id(\"hello.kotlin-jvm\")`, and keeps only what is special about it.\n\n"
                "Older projects often use a `buildSrc` folder for this. It works, but Gradle's best-practice guide prefers an included build like `build-logic`, partly because any change in `buildSrc` makes the whole build out of date.\n\n"
                "Publishing a library takes one more plugin, `maven-publish`. Give `greeting` a `group` and `version`, and `./gradlew :greeting:publishToMavenLocal` installs it in `~/.m2`; other publish tasks push to a company repository. In the generated `pom.xml`, `api` dependencies get `compile` scope and `implementation` ones get `runtime` scope, so Maven users see the same split."
            ),
            "refs": [
                {"title": "Gradle docs: Best practices for structuring builds", "url": "https://docs.gradle.org/current/userguide/best_practices_structuring_builds.html", "kind": "docs"},
                {"title": "Understanding Gradle #03: plugins (Jendrik Johannes)", "url": "https://www.youtube.com/watch?v=N95YI-szd78", "kind": "watch"},
                {"title": "Now in Android: build-logic README (a real convention plugin layout)", "url": "https://github.com/android/nowinandroid/blob/main/build-logic/README.md", "kind": "read"},
            ],
        },
    ],
    "analogy": (
        "`implementation` and `api` work like `private` and `public` in Kotlin, applied to your dependencies. A `private` helper can change freely because no caller can see it; an `implementation` dependency can be upgraded without the projects that use yours recompiling. "
        "An `api` dependency is part of your public face, like a public function's return type, so callers depend on it too. "
        "Where it breaks: a private member truly stays inside, but an `implementation` dependency still travels to consumers at runtime, on their runtime classpath."
    ),
    "diagram": diagram,
    "diagram_caption": "Two paths ask for commons-lang3. Gradle keeps one copy, the highest version, on the runtime classpath.",
    "worked": {
        "title": "Why did I get commons-lang3 3.18.0?",
        "steps": [
            {
                "say": "In a scratch copy of hello-jvm, add two real libraries. `greeting` uses `commons-text` internally, and `app` asks for `commons-lang3` 3.17.0 directly. Plain coordinate strings are fine for an experiment; for keeps they go in the catalog.",
                "code": "// greeting/build.gradle.kts\ndependencies {\n    implementation(\"org.apache.commons:commons-text:1.14.0\")\n}\n\n// app/build.gradle.kts\ndependencies {\n    implementation(project(\":greeting\"))\n    implementation(\"org.apache.commons:commons-lang3:3.17.0\")\n}",
                "lang": "text",
            },
            {
                "say": "Print the runtime classpath. `commons-text` brings `commons-lang3` 3.18.0 along. `app` asked for 3.17.0, and the arrow shows it got 3.18.0: highest wins.",
                "code": "$ ./gradlew :app:dependencies --configuration runtimeClasspath -q\nruntimeClasspath - Runtime classpath of 'main'.\n+--- org.jetbrains.kotlin:kotlin-stdlib:2.4.21\n|    \\--- org.jetbrains:annotations:13.0\n+--- project ':greeting'\n|    +--- org.jetbrains.kotlin:kotlin-stdlib:2.4.21 (*)\n|    \\--- org.apache.commons:commons-text:1.14.0\n|         \\--- org.apache.commons:commons-lang3:3.18.0\n\\--- org.apache.commons:commons-lang3:3.17.0 -> 3.18.0",
                "lang": "console",
            },
            {
                "say": "Ask Gradle why. The reason is conflict resolution, and the two trees at the bottom are the two paths that asked for the library.",
                "code": "$ ./gradlew :app:dependencyInsight --dependency commons-lang3 --configuration runtimeClasspath -q\norg.apache.commons:commons-lang3:3.18.0\n  Variant runtime:\n    ...\n   Selection reasons:\n      - By conflict resolution: between versions 3.18.0 and 3.17.0\n\norg.apache.commons:commons-lang3:3.18.0\n\\--- org.apache.commons:commons-text:1.14.0\n     \\--- project ':greeting'\n          \\--- runtimeClasspath\n\norg.apache.commons:commons-lang3:3.17.0 -> 3.18.0\n\\--- runtimeClasspath",
                "lang": "console",
            },
            {
                "say": "Now the compile classpath. `commons-text` is missing, because `greeting` declared it as `implementation`. And `commons-lang3` is still 3.17.0 here, because each classpath is resolved on its own.",
                "code": "$ ./gradlew :app:dependencies --configuration compileClasspath -q\ncompileClasspath - Compile classpath for 'main'.\n+--- org.jetbrains.kotlin:kotlin-stdlib:2.4.21\n|    \\--- org.jetbrains:annotations:13.0\n+--- project ':greeting'\n|    \\--- org.jetbrains.kotlin:kotlin-stdlib:2.4.21 (*)\n\\--- org.apache.commons:commons-lang3:3.17.0",
                "lang": "console",
            },
            {
                "say": "So `app` cannot use `commons-text` itself. Add a file in `app` that imports `org.apache.commons.text.WordUtils`, and the compiler says so.",
                "code": "$ ./gradlew :app:compileKotlin\n> Task :app:compileKotlin FAILED\ne: file:///Users/you/code/hello-jvm/app/src/main/kotlin/hello/app/Title.kt:3:27 Unresolved reference 'text'.\ne: file:///Users/you/code/hello-jvm/app/src/main/kotlin/hello/app/Title.kt:5:35 Unresolved reference 'WordUtils'.",
                "lang": "console",
            },
            {
                "say": "If `greeting` really returned `commons-text` types from public functions, `api` would be right. Change that one line to `api(...)` and the compile classpath gains `commons-text`. Then throw the experiment away: the real `greeting` has no outside dependencies.",
                "code": "$ ./gradlew :app:dependencies --configuration compileClasspath -q\ncompileClasspath - Compile classpath for 'main'.\n+--- org.jetbrains.kotlin:kotlin-stdlib:2.4.21\n|    \\--- org.jetbrains:annotations:13.0\n+--- project ':greeting'\n|    +--- org.apache.commons:commons-text:1.14.0\n|    |    \\--- org.apache.commons:commons-lang3:3.18.0\n|    \\--- org.jetbrains.kotlin:kotlin-stdlib:2.4.21 (*)\n\\--- org.apache.commons:commons-lang3:3.17.0 -> 3.18.0",
                "lang": "console",
            },
        ],
    },
    "code": [
        {"lang": "text", "title": "settings.gradle.kts", "src": lab("settings.gradle.kts"), "run": "./gradlew projects"},
        {"lang": "ini", "title": "gradle/libs.versions.toml", "src": CATALOG_D23, "run": "./gradlew build"},
        {"lang": "text", "title": "build-logic/settings.gradle.kts", "src": lab("build-logic/settings.gradle.kts"), "run": "./gradlew build"},
        {"lang": "text", "title": "build-logic/build.gradle.kts", "src": lab("build-logic/build.gradle.kts"), "run": "./gradlew build"},
        {"lang": "text", "title": "build-logic/src/main/kotlin/hello.kotlin-jvm.gradle.kts", "src": lab("build-logic/src/main/kotlin/hello.kotlin-jvm.gradle.kts"), "run": "./gradlew build"},
        {"lang": "text", "title": "greeting/build.gradle.kts", "src": lab("greeting/build.gradle.kts"), "run": "./gradlew :greeting:build"},
        {"lang": "text", "title": "greeting/src/main/kotlin/hello/greeting/Greeting.kt", "src": lab("greeting/src/main/kotlin/hello/greeting/Greeting.kt"), "run": "./gradlew :greeting:test"},
        {"lang": "text", "title": "greeting/src/test/kotlin/hello/greeting/GreetingTest.kt", "src": lab("greeting/src/test/kotlin/hello/greeting/GreetingTest.kt"), "run": "./gradlew :greeting:test"},
        {"lang": "text", "title": "app/build.gradle.kts", "src": lab("app/build.gradle.kts"), "run": "./gradlew :app:build"},
        {"lang": "text", "title": "app/src/main/kotlin/hello/app/Main.kt", "src": lab("app/src/main/kotlin/hello/app/Main.kt"), "run": "./gradlew :app:run"},
        {"lang": "text", "title": "app/src/test/kotlin/hello/app/AppTest.kt (replaces MainTest.kt)", "src": lab("app/src/test/kotlin/hello/app/AppTest.kt"), "run": "./gradlew :app:test"},
    ],
    "commands": [
        {"cmd": "./gradlew projects", "what": "Show the projects in the build and any included builds."},
        {"cmd": "./gradlew :app:dependencies --configuration runtimeClasspath", "what": "Print the tree of everything app needs at runtime, with -> where a version changed."},
        {"cmd": "./gradlew :app:dependencies --configuration compileClasspath", "what": "Print what the compiler sees for app's main code."},
        {"cmd": "./gradlew :app:dependencyInsight --dependency commons-lang3 --configuration runtimeClasspath", "what": "Explain one library: the version chosen, why, and who asked for it."},
        {"cmd": "./gradlew :greeting:dependencies --configuration testRuntimeClasspath", "what": "See the test classpath, including what a BOM changed."},
        {"cmd": "./gradlew :greeting:test", "what": "Run only the library's tests."},
        {"cmd": "./gradlew :app:build", "what": "Build app and the parts of greeting it needs."},
        {"cmd": "./gradlew build", "what": "Build and test every project from the root."},
        {"cmd": "./gradlew :greeting:tasks", "what": "List the tasks of one project."},
        {"cmd": "./gradlew buildEnvironment", "what": "Show the plugins and libraries on the build scripts' own classpath."},
        {"cmd": "GREETING='Say \"hi\"' ./gradlew :app:run", "what": "Start the app with a setting from an environment variable."},
        {"cmd": "curl -s localhost:8080 | python3 -m json.tool", "what": "Pretty-print the reply, or fail loudly if the JSON is broken."},
        {"cmd": "./gradlew :greeting:publishToMavenLocal", "what": "With maven-publish applied, install the library into ~/.m2 for other local builds."},
    ],
    "mistake": (
        "Trusting the version in your build file. With highest-wins, the version that runs can be higher than the one you wrote, and a library can sit on the classpath without being in any build file at all. "
        "When a scanner reports a vulnerable version, run `dependencyInsight` to see which path brings it in, then declare the fixed version yourself; highest-wins then lifts every path to it."
    ),
    "real_world": (
        "At Paylane (a made-up payments company), a security scan flagged an old JSON library that no build file mentioned. `dependencyInsight` showed it arrived through a client SDK. "
        "The team added the fixed version to the catalog and declared it in the affected project; highest-wins lifted every path, and a convention plugin made sure all services got the same setup."
    ),
    "task": {
        "title": "Split hello-jvm into app and greeting",
        "steps": [
            "Create the `greeting` project: `Greeting.kt` and `GreetingTest.kt` from Files. In `app`, delete the old `reply()` function and `MainTest.kt`.",
            "Update `settings.gradle.kts`: include both projects, add `pluginManagement { includeBuild(\"build-logic\") }`, and set `repositoriesMode`.",
            "Create `gradle/libs.versions.toml` with the Kotlin and JUnit versions and the two library entries.",
            "Create the `build-logic` build: its settings file, its build file, and the `hello.kotlin-jvm` convention plugin.",
            "Write `greeting/build.gradle.kts` and shrink `app/build.gradle.kts` so each applies the convention plugin plus only what is special to it.",
            "Replace `Main.kt`, add `AppTest.kt`, and run `./gradlew build` until it passes.",
            "Prove the split: run `./gradlew :greeting:test` alone, then find `project ':greeting'` in `./gradlew :app:dependencies --configuration runtimeClasspath`.",
            "Find the BOM at work: look for `5.10.1 -> 6.1.3` in greeting's `testRuntimeClasspath`.",
            "Start the app with `GREETING='Say \"hi\"'` and check the reply with `curl -s localhost:8080 | python3 -m json.tool`.",
            "Commit and push.",
        ],
        "hints": [
            "If Gradle cannot find plugin `hello.kotlin-jvm`, check the file name in `build-logic/src/main/kotlin` and that `includeBuild` sits inside `pluginManagement`.",
            "The convention plugin applies the Kotlin plugin, so subprojects must not ask for `kotlin(\"jvm\")` again in their own plugins blocks.",
        ],
        "done_when": "`./gradlew build` passes and `curl -s localhost:8080 | python3 -m json.tool` prints valid JSON that contains your quoted greeting.",
    },
    "explain_back": {
        "prompt": "Explain the difference between `implementation` and `api` in 3 to 4 sentences. Mention which classpaths each one reaches and why `implementation` is the default.",
        "answer": (
            "Both put a library on my project's own compile and runtime classpaths. An `api` dependency also lands on the compile classpath of every project that uses mine, while an `implementation` one reaches them only at runtime. "
            "So with `implementation`, consumers cannot import that library by accident, and upgrading it does not force them to recompile. "
            "I use `api` only when the library's types appear in my public functions, because then callers need it to compile."
        ),
    },
    "recap": [
        "Repositories say where to look, coordinates (group:name:version) say what to fetch; declare repositories once in settings.",
        "The configuration decides the classpath: default to `implementation`, use `api` only for types in your public functions.",
        "On a version conflict the highest version wins; `dependencies` and `dependencyInsight` show what you really got.",
        "A version catalog names coordinates in one file; a platform (BOM) actually moves a family of versions together.",
        "`include` plus `project(\":x\")` make a multi-project build; task paths like `:greeting:test` pick one project.",
        "Shared setup belongs in a convention plugin in a `build-logic` included build.",
    ],
    "check": [
        {
            "q": "Your library `billing` has a public function that returns `org.joda.money.Money`. Which configuration should `joda-money` use in billing?",
            "options": ["`implementation`", "`compileOnly`", "`api`", "`runtimeOnly`"],
            "answer": 2,
            "why": "Callers need the Money type to compile code that calls billing, so the library is part of billing's API.",
        },
        {
            "q": "`dependencies` prints `jackson-databind:2.17.0 -> 2.18.2`. What does the arrow mean?",
            "options": [
                "2.17.0 was requested and 2.18.2 was chosen",
                "2.18.2 failed to download, so 2.17.0 is used",
                "The app will load both versions at runtime",
                "2.17.0 is in the cache and 2.18.2 is remote",
            ],
            "answer": 0,
            "why": "Something else asked for 2.18.2, and conflict resolution picked the highest version for every path.",
        },
        {
            "q": "Five Kotlin projects repeat the same toolchain, test and BOM setup in their build files. Where should that setup live?",
            "options": [
                "In an `allprojects {}` block in the root",
                "In each project's `gradle.properties`",
                "In the catalog's `[bundles]` section",
                "In a convention plugin in `build-logic`",
            ],
            "answer": 3,
            "why": "A convention plugin keeps one copy of the setup that each project applies by id, without tying projects to the root script.",
        },
    ],
    "interview": [
        {
            "q": "What is the difference between api and implementation in Gradle?",
            "a": "Both make a dependency available to the project that declares it. An `api` dependency is also exposed on the compile classpath of consumers, while `implementation` keeps it internal and only ships it at runtime. `implementation` is the default because it prevents accidental use of a library's internals and means fewer projects recompile when it changes. I use `api` only for libraries whose types appear in public signatures. It needs the `java-library` plugin.",
        },
        {
            "q": "Two libraries need different versions of the same dependency. What does Gradle do, and how do you investigate?",
            "a": "By default Gradle picks the highest requested version for the whole graph, unlike Maven's nearest-wins. I run `dependencies` on the relevant classpath to see arrows like `1.2 -> 1.4`, then `dependencyInsight` on that one module to get the selection reason and every path that asked for it. If the result is wrong, I declare the version I need, use a platform for families of libraries, or as a last resort a strict version.",
        },
        {
            "q": "How would you share build configuration across many Gradle projects?",
            "a": "I would write convention plugins as precompiled script plugins in an included build called `build-logic`, and apply them by id in each project. Versions go in the version catalog, which `build-logic` can read too. I avoid `allprojects` and `subprojects` blocks, because they couple every project to the root. Each project's own build script then only holds what is special about it.",
        },
    ],
    "deeper": {
        "minutes": 12,
        "body": (
            "The worked example left a loose end. `app` compiled against commons-lang3 3.17.0 but ran with 3.18.0. Usually that is harmless, because libraries try to stay compatible within a major version. But if 3.18.0 changed a method you call, the code compiles fine and then fails at runtime with `NoSuchMethodError`. That is the worst kind of failure, because no build catches it.\n\n"
            "You can make Gradle use the runtime versions when it compiles too. Add this to `app/build.gradle.kts`:\n\n"
            "`java { consistentResolution { useRuntimeClasspathVersions() } }`\n\n"
            "With that block, the compile classpath report for the same experiment showed `org.apache.commons:commons-lang3:3.17.0 -> 3.18.0`. `dependencyInsight` on the compile classpath gave a new reason: `By constraint: version resolved in configuration ':app:runtimeClasspath' by consistent resolution`. Now the compiler sees the jar that will really run.\n\n"
            "Gradle has more tools for taking control of versions. Reach for them in this order:\n\n"
            "1. Declare the version you need directly. Highest-wins then lifts every path in that project to it. This is the usual fix for a security alert.\n"
            "2. Add a dependency constraint, such as `constraints { implementation(\"group:name:1.4.2\") }`. It sets a version for a library you do not use directly, without adding it as a dependency. `gradle init` writes one of these in its generated builds.\n"
            "3. Use a platform for a whole family, as hello-jvm does for JUnit.\n"
            "4. As a last resort, use a strict version or `enforcedPlatform`, which can force a version downward. Check the graph afterwards, because you may have broken a library that needed the newer one.\n\n"
            "There is also a switch for teams that want to decide every conflict by hand: `configurations.all { resolutionStrategy.failOnVersionConflict() }` fails the build whenever two versions meet. It is noisy in a big project, but it makes every version choice a reviewed decision.\n\n"
            "Day 24 adds two more tools that sit on top of all this: dependency locking, which records the exact result of resolution in a file, and dependency verification, which checks the bytes of every downloaded jar."
        ),
    },
    "sources": [
        {"title": "Gradle docs: The Java Library plugin", "url": "https://docs.gradle.org/current/userguide/java_library_plugin.html"},
        {"title": "Gradle docs: Viewing dependencies", "url": "https://docs.gradle.org/current/userguide/viewing_debugging_dependencies.html"},
        {"title": "Gradle docs: Version catalogs", "url": "https://docs.gradle.org/current/userguide/version_catalogs.html"},
        {"title": "Gradle docs: Best practices for structuring builds", "url": "https://docs.gradle.org/current/userguide/best_practices_structuring_builds.html"},
    ],
}
