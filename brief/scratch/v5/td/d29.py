"""Book-voice rewrite of d29 (fifth pass, writer td). Replaces prose fields only."""
from common import load, save, set_list, drop_extras

path, P, L = load(7, "d29")

L["goal"] = ("By the end you can declare dependencies in the right configuration, explain which version Gradle picked and why, "
             "and split a build into projects that share a version catalog and a convention plugin.")

L["opening"] = """Picture our bakery buying ready-made croissant dough to save time. One morning a dairy announces a recall: a batch of its butter is unsafe. The head baker checks the shopping list and relaxes. Butter is not on it. Then someone reads the small print on the dough: made with butter from that very dairy.

The list was honest. It just showed only what the bakery bought, and nothing about what came inside. Software has the same blind spot. The libraries you list bring their own libraries, and a security warning about one of those can arrive for something your files never mention.

Last time, Gradle planned tasks like a careful baker, but hello-jvm used no outside libraries at all. In this lesson, we'll add some. We'll see where libraries come from, which version actually ends up in your program and why, and how to split hello-jvm into two projects that share one setup. Before we start, make a guess, and keep it in mind."""

L["guess"]["q"] = ("Your app asks for the library commons-lang3 at version 3.17.0. Another library your app uses needs commons-lang3 3.18.0. "
                   "Which version does the app run with?")
L["guess"]["why"] = ("When two versions of one library meet, Gradle picks the highest by default. Maven picks the declaration nearest your project "
                     "instead, so the same dependencies can resolve differently there.")

set_list(L["terms"], "plain", [
    "A server that stores published libraries and plugins, such as Maven Central.",
    "The group, name and version that identify a library, written as group:name:version.",
    "A named bucket such as implementation or api that decides which classpaths a dependency joins.",
    "A library you get because a library you asked for needs it.",
    "Gradle's rule for picking one version when several are requested; by default the highest version wins.",
    "The file gradle/libs.versions.toml, which names your libraries and plugins and their versions in one place.",
    "A published list of versions for a family of libraries, added with platform(...) so they move together.",
    "Your own small plugin, kept in build-logic, that holds setup shared by several projects.",
])

S = L["sections"]

S[0]["h"] = "Where libraries come from: repositories and coordinates"
S[0]["body"] = """A dependency is a library your code needs, such as JUnit, Java's best-known test library, or a JSON parser, a library that reads JSON text. To fetch one, Gradle needs two facts: where to look and what to ask for. A bakery needs the same two: which supplier, and which product code.

Where to look is a repository, a server that stores published jars with their metadata. A jar, from last lesson, is a zip file of compiled code. The metadata is a small file next to each jar, a Maven `.pom` or Gradle's own `.module`, which lists the library's own dependencies: the small print on the dough. You will meet three kinds of repository:

- Maven Central (`mavenCentral()`), where most open-source JVM libraries live
- the Gradle Plugin Portal (`gradlePluginPortal()`), where most Gradle plugins live
- your company's own repository, often a mirror of both (Nexus or Artifactory)

A mirror is a copy kept close to home, and Nexus and Artifactory are products for running one. What to ask for is the coordinates: group, name and version in one string. `org.junit:junit-bom:6.1.3` has the group `org.junit`, the name `junit-bom` and the version `6.1.3`.

Maven, the other build tool from last lesson, uses the same coordinates. Gradle downloads each file once into `~/.gradle/caches/modules-2` and reuses it in every project on your laptop.

Declare repositories once, in `settings.gradle.kts`. In hello-jvm, `repositoriesMode = RepositoriesMode.FAIL_ON_PROJECT_REPOS` fails the build if a project adds its own. That sounds strict, but at work it is what you want. There is one place to point at the company mirror, and no project can quietly pull from a random server. Once a library arrives, the next question is who gets to see it."""

S[1]["h"] = "Who gets to see a library: configurations"
S[1]["body"] = """You never add a dependency to a project in general. You add it to a configuration, and the configuration decides which classpaths it joins. A classpath, from last lesson, is the list of jars that the compiler or the JVM can see.

Each project has one classpath for compiling the main code, one for running it, and the same two for tests. Gradle names them `compileClasspath`, `runtimeClasspath`, `testCompileClasspath` and `testRuntimeClasspath`, and fills each one from the configurations below. The reports in this lesson ask for them by those names. The configurations you will use:

- `implementation`: needed to compile and run this project. Projects that use yours cannot see it when they compile.
- `api`: like `implementation`, but also on the compile classpath of every project that uses yours. The Kotlin plugin offers it; a plain Java project needs the `java-library` plugin.
- `compileOnly`: needed to compile, but provided by someone else at runtime, such as the Servlet API inside an application server.
- `runtimeOnly`: needed only when the program runs, such as a database driver.
- `testImplementation` and `testRuntimeOnly`: the same ideas, for the tests.

Runtime means while the program runs. A database driver is the small library that lets a program talk to one kind of database. The Servlet API is a set of Java features that a server program already provides.

A kitchen picture helps with the first two. If you sell a sauce, the stock inside is your business, and customers never handle it: that is `implementation`. If your label says "serve on Brand X crackers", the crackers are part of what you promise, and customers need them too: that is `api`.

Make `implementation` your default. It keeps a library's insides private: a consumer cannot import a class from a library you only use internally. It also saves build time. When you upgrade an `implementation` dependency, the projects that use yours do not recompile.

Use `api` only when a type from that library appears in your public functions. A function is a named piece of code that other code calls, and a type is a kind of value, such as a number or an amount of money. If your function returns a `Money` from a money library, every caller needs that library to compile, so it is part of your API. **Default to implementation. Use api only for types that your public functions show.** Libraries bring their own libraries, though, and that is where versions start to clash."""

S[2]["h"] = "Ingredients inside ingredients, and highest-wins"
S[2]["body"] = """Libraries have dependencies of their own. Ask for `commons-text` and you also get `commons-lang3`, because the metadata file of `commons-text` lists it. Gradle then reads the metadata of `commons-lang3`, and so on down the tree. These are transitive dependencies, the butter inside the dough, and in a real service they often outnumber the ones you declared.

Sooner or later, two paths ask for different versions of the same library. Picture two recipes that ask for different editions of the same spice blend, when the kitchen stocks only one jar. Gradle settles this conflict with one rule: the highest version wins. Your own declaration gets no extra weight.

The bet is that the library asking for the newer version may need something only it has. Code written for the older one usually runs on the newer too. This surprises people who know Maven, where the declaration nearest your project wins.

Two reports show what really happened:

- `./gradlew :app:dependencies --configuration runtimeClasspath` prints the whole tree. An arrow such as `3.17.0 -> 3.18.0` means one version was asked for and another was chosen. `(*)` marks a subtree already printed above.
- `./gradlew :app:dependencyInsight --dependency commons-lang3 --configuration runtimeClasspath` explains one library: the version picked, the reason (such as `By conflict resolution`) and every path that asked for it.

Gradle resolves each classpath separately. So the compile classpath can hold 3.17.0 while the runtime classpath holds 3.18.0. The worked example shows exactly that, and the deeper section shows how to make the two agree.

Back to the recall. When a scanner reports a vulnerable version that no build file mentions, run `dependencyInsight` to see which path brings it in. Then declare the fixed version yourself, and highest-wins lifts every path to it. Declaring versions in many build files gets messy, though, and the next section gives them one home."""

S[3]["h"] = "One shopping list: the version catalog"
S[3]["body"] = """In a build with ten projects, the same version string ends up in ten build files, and one upgrade means ten edits. A kitchen keeps one master shopping list instead. A version catalog is that list. It is a file at `gradle/libs.versions.toml`, written in TOML, the simple format of `pyproject.toml` on Day 15. Gradle reads it automatically. It has up to four sections:

- `[versions]`: named version numbers, such as `kotlin = "2.4.21"`
- `[libraries]`: short names for coordinates, such as `junit-bom`
- `[bundles]`: groups of libraries you often add together
- `[plugins]`: names for plugins and their versions

From it Gradle generates an object named `libs`, so build scripts say `libs.junit.bom` instead of `"org.junit:junit-bom:6.1.3"`, and `alias(libs.plugins.jib)` for a plugin. Dashes in names become dots. IntelliJ, the code editor, completes these names, and a typo fails the build at once instead of fetching the wrong thing.

Know what a catalog does not do. It only gives names to coordinates. It does not force any version onto the dependency graph, so highest-wins still decides the transitive ones. A shopping list says what you buy, not what is inside what you buy. That job belongs to platforms, next."""

S[4]["h"] = "Versions that move together: platforms and BOMs"
S[4]["body"] = """Some libraries come as a family of modules that must share one version, like the parts of a stand mixer that only fit the same model year. JUnit is one: `junit-jupiter-api`, `junit-jupiter-engine` and `junit-platform-launcher` have to match, or tests fail in confusing ways.

A BOM (bill of materials) is a published list of recommended versions for such a family. Gradle calls it a platform, and you add it like a dependency, wrapped in `platform(...)`. hello-jvm does this in its convention plugin: `testImplementation(platform(...junit-bom...))`.

It needs one because `kotlin("test")` pulls in `kotlin-test-junit5`, which asks for JUnit 5.10.1. The JUnit 6.1.3 BOM moves every JUnit module to 6.1.3. The dependency report shows it as `junit-jupiter-engine:5.10.1 -> 6.1.3`, with lines marked `(c)` for the BOM's constraints.

A constraint is a version rule that applies only when something else brings that library in. A BOM is a list of constraints, so it adds no jars of its own.

You will see BOMs all over the JVM world. Spring Boot and Jackson both publish one. A normal `platform()` takes part in highest-wins like everything else. `enforcedPlatform()` forces its versions, even downward. Use it rarely, because it can silently downgrade something a library needs. With the pantry in order, we can split the kitchen."""

S[5]["h"] = "Splitting the build into projects"
S[5]["body"] = """So far hello-jvm has one project. hello-jvm is this part's lab, a tiny Kotlin web service that answers every visit with a greeting and a count of visits so far. Today you split it in two, the way a big kitchen gives pastry its own section:

- `greeting` is a library. It builds the JSON reply, escapes text properly, and knows nothing about HTTP.
- `app` is the web service. It depends on `greeting` and adds the server.

Why bother for a tiny service? The Day 28 version builds JSON by gluing strings. Start it with a `GREETING` that contains a double quote and `curl` returns `{"message":"Say "hi"",...}`, which no JSON parser accepts. To escape text is to mark special characters such as quotes so they are read as plain text.

Escaping is exactly the kind of logic that deserves its own module and its own tests. In a big codebase the same split gives clear boundaries and faster builds, because a change in `app` never recompiles `greeting`.

The wiring is two lines. `include("app", "greeting")` in the settings file declares both projects. `implementation(project(":greeting"))` in `app/build.gradle.kts` makes `app` use `greeting` like any library. The difference is that Gradle puts the tasks that build `greeting` into the task graph ahead of the tasks of `app`.

Task paths matter now:

- `./gradlew build` at the root builds both projects.
- `./gradlew :greeting:test` tests only the library.
- `./gradlew :app:build` builds `app` and only the parts of `greeting` it needs, such as its jar.
- `./gradlew projects` prints the tree.

Two projects, though, means two build scripts that start to look alike. The last section deals with that."""

S[6]["h"] = "Shared setup in a convention plugin"
S[6]["body"] = """Split a build and the build scripts start repeating themselves. Both projects need the Kotlin plugin, `jvmToolchain(21)`, kotlin.test, the JUnit BOM and `useJUnitPlatform()`. Copy that into ten projects and the copies drift apart.

Older builds put shared setup in `allprojects {}` or `subprojects {}` blocks in the root script. Gradle now advises against that, because it ties every project to the root. With such a block, `app/build.gradle.kts` no longer shows how `app` is built, and every edit to the root script affects every project.

The current answer is a convention plugin: your own small plugin that holds the shared setup, like a house standards sheet every section follows. In hello-jvm it lives in `build-logic`, a separate little Gradle build inside the repository. It has to be separate, because its plugins must be compiled before Gradle can run the build scripts that apply them:

1. `settings.gradle.kts` says `pluginManagement { includeBuild("build-logic") }`, so Gradle builds `build-logic` first and offers its plugins.
2. `build-logic/build.gradle.kts` applies `kotlin-dsl`, which turns each `*.gradle.kts` file in `src/main/kotlin` into a plugin.
3. The file `hello.kotlin-jvm.gradle.kts` becomes the plugin `hello.kotlin-jvm`.
4. Each project applies it with `id("hello.kotlin-jvm")`, and keeps only what is special about it.

Older projects often use a `buildSrc` folder for this. It works, but Gradle's best-practice guide prefers an included build like `build-logic`, partly because any change in `buildSrc` makes the whole build out of date.

Publishing a library takes one more plugin, `maven-publish`. Give `greeting` a `group` and `version`, and `./gradlew :greeting:publishToMavenLocal` installs it in `~/.m2`; other publish tasks push to a company repository. In the generated `pom.xml`, `api` dependencies get `compile` scope and `implementation` ones get `runtime` scope, so Maven users see the same split.

The build is correct now, and it has a limit. On a fresh CI runner, every run downloads every library and compiles everything again, and nothing yet packs hello-jvm into an image. Day 30 makes the build fast in CI and ships it in a container."""

L["closing"] = """We started with butter that came inside the dough, and a recall for something the shopping list never mentioned. You can now read the small print. `dependencies` shows the whole tree, `dependencyInsight` explains one library, and highest-wins tells you which version runs.

In your hello-jvm, find `5.10.1 -> 6.1.3` in greeting's `testRuntimeClasspath` and say in one sentence who asked for each version.

Next, we'll take hello-jvm to CI and into a container. How do we stop a fresh runner from downloading and compiling everything on every push?"""

drop_extras(L)

set_list(L["worked"]["steps"], "say", [
    "Work in a scratch copy of the two-project hello-jvm; the finished one is in `~/code/devops-from-zero/labs/hello-jvm`. Add two real libraries. `greeting` uses `commons-text` internally, and `app` asks for `commons-lang3` 3.17.0 directly. Plain coordinate strings are fine for an experiment; in the real build they belong in the catalog.",
    "Print the runtime classpath. `commons-text` brings `commons-lang3` 3.18.0 along. `app` asked for 3.17.0, and the arrow shows it got 3.18.0: highest wins.",
    "Ask Gradle why. The reason is conflict resolution, and the two trees at the bottom are the two paths that asked for the library.",
    "Now the compile classpath. `commons-text` is missing, because `greeting` declared it as `implementation`. And `commons-lang3` is still 3.17.0 here, because each classpath is resolved on its own.",
    "So `app` cannot use `commons-text` itself. Add a file in `app` that imports `org.apache.commons.text.WordUtils`, and the compiler says so. The stock inside someone else's sauce is not yours to use.",
    "If `greeting` really returned `commons-text` types from public functions, `api` would be right. Change that one line to `api(...)` and the compile classpath gains `commons-text`. Then throw the experiment away: the real `greeting` has no outside dependencies.",
])

L["task"]["steps"] = [
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
]
L["task"]["hints"] = [
    "If Gradle cannot find plugin `hello.kotlin-jvm`, check the file name in `build-logic/src/main/kotlin` and that `includeBuild` sits inside `pluginManagement`.",
    "The convention plugin already applies the Kotlin plugin, so each subproject's plugins block needs only `id(\"hello.kotlin-jvm\")` plus `application` or `java-library`.",
]
L["task"]["done_when"] = "You are done when `./gradlew build` passes and `curl -s localhost:8080 | python3 -m json.tool` prints valid JSON that contains your quoted greeting."

L["explain_back"]["answer"] = ("Both put a library on my project's own compile and runtime classpaths. "
                               "An `api` dependency also lands on the compile classpath of every project that uses mine, while an `implementation` one reaches them only at runtime. "
                               "So with `implementation`, consumers cannot import that library by accident, and upgrading it does not force them to recompile. "
                               "I use `api` only when the library's types appear in my public functions, because then callers need it to compile.")

L["recap"] = [
    "Repositories say where to look, coordinates (group:name:version) say what to fetch; declare repositories once in settings.",
    "The configuration decides the classpath: default to `implementation`, use `api` only for types in your public functions.",
    "On a version conflict the highest version wins; `dependencies` and `dependencyInsight` show what you really got.",
    "A version catalog names coordinates in one file; a platform (BOM) actually moves a family of versions together.",
    "`include` plus `project(\":x\")` make a multi-project build, and shared setup belongs in a convention plugin in `build-logic`.",
    "The limit: a fresh CI runner still downloads and compiles everything on every run, which Day 30 fixes.",
]

C = L["check"]
C[0]["why"] = "Callers need the Money type to compile code that calls billing, so the library is part of billing's API."
C[1]["why"] = "Something else asked for 2.18.2, and conflict resolution picked the highest version for every path."
C[2]["why"] = "A convention plugin keeps one copy of the setup that each project applies by id, without tying projects to the root script."

I = L["interview"]
I[0]["a"] = ("Both make a dependency available to the project that declares it. "
             "An `api` dependency is also exposed on the compile classpath of consumers, while `implementation` keeps it internal and only ships it at runtime. "
             "The `implementation` configuration is the default because it prevents accidental use of a library's internals and means fewer projects recompile when it changes. "
             "I use `api` only for libraries whose types appear in public signatures. "
             "The Kotlin plugin provides `api`; a plain Java project needs the `java-library` plugin.")
I[1]["a"] = ("By default Gradle picks the highest requested version for the whole graph, unlike Maven's nearest-wins. "
             "I run `dependencies` on the relevant classpath to see arrows like `1.2 -> 1.4`, then `dependencyInsight` on that one module to get the selection reason and every path that asked for it. "
             "If the result is wrong, I declare the version I need, use a platform for families of libraries, or as a last resort a strict version.")
I[2]["a"] = ("I would write convention plugins as precompiled script plugins in an included build called `build-logic`, and apply them by id in each project. "
             "Versions go in the version catalog, which `build-logic` can read too. "
             "I avoid `allprojects` and `subprojects` blocks, because they couple every project to the root. "
             "Each project's own build script then only holds what is special about it.")

L["deeper"]["body"] = """The worked example left a loose end. `app` compiled against commons-lang3 3.17.0 but ran with 3.18.0. Usually that is harmless, because libraries try to stay compatible within a major version. But if 3.18.0 changed a method (a function that belongs to a class) you call, the code compiles fine and then fails at runtime with `NoSuchMethodError`. That is the worst kind of failure, because no build catches it.

You can make Gradle use the runtime versions when it compiles too. Add this to `app/build.gradle.kts`:

`java { consistentResolution { useRuntimeClasspathVersions() } }`

With that block, the compile classpath report for the same experiment showed `org.apache.commons:commons-lang3:3.17.0 -> 3.18.0`. `dependencyInsight` on the compile classpath gave a new reason: `By constraint: version resolved in configuration ':app:runtimeClasspath' by consistent resolution`. Now the compiler sees the jar that will really run.

Gradle has more tools for taking control of versions. Reach for them in this order:

1. Declare the version you need directly. Highest-wins then lifts every path in that project to it. This is the usual fix for a security alert.
2. Add a dependency constraint, such as `constraints { implementation("group:name:1.4.2") }`. It sets a version for a library you do not use directly, without adding it as a dependency. `gradle init` writes one of these in its generated builds.
3. Use a platform for a whole family, as hello-jvm does for JUnit.
4. As a last resort, use a strict version or `enforcedPlatform`, which can force a version downward. Check the graph afterwards, because you may have broken a library that needed the newer one.

There is also a switch for teams that want to decide every conflict by hand. With `configurations.runtimeClasspath { resolutionStrategy.failOnVersionConflict() }` in `app`, the dependency report marked both commons-lang3 entries `FAILED`. Put the same rule on every configuration with `configurations.all` and it fails first on the Kotlin compiler's own classpath, so keep it to the classpaths you care about.

Day 30 adds two more tools. Dependency locking records the exact result of resolution in a file, and dependency verification checks the bytes of every downloaded jar."""

save(path, P)
print("d29 written")
