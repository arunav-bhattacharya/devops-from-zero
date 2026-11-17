"""Book-voice rewrite of d28 (fifth pass, writer td). Replaces prose fields only."""
from common import load, save, set_list, drop_extras

path, P, L = load(7, "d28")

L["goal"] = ("By the end you can explain Gradle's model of projects, tasks and phases, create a project with the Gradle Wrapper, "
             "and predict which tasks a build will run or skip.")

L["opening"] = """Picture a bakery the night before a wedding order of two hundred sandwiches. The bread needs dough, the dough needs a starter that takes hours, and the sauce needs eggs from a supplier who closes at six. A new baker starts at the top of the list and works down. At midnight the bread is not ready: nobody started the dough first.

The baker worked hard; the trouble was the list: it followed the order of the menu, not the order the work has to happen in. A real kitchen plans backwards from what is needed, and it never makes a sauce twice when this morning's batch is still good.

Last time, our pipeline shipped a Python app, which runs straight from the text you write. This part meets Kotlin, a language that must be translated before a computer can run it. In this lesson, we'll see what that involves, and how Gradle, a build tool, plans the work like a careful baker and skips what is already done. Before we start, make a guess, and keep it in mind."""

L["guess"]["q"] = ("Gradle is the build tool this part teaches. You run its test command, `./gradlew test`, change nothing, "
                   "and run it again. What does Gradle do with the tests the second time?")
L["guess"]["why"] = ("Gradle keeps a fingerprint of everything each task used and made. Nothing changed, so the last results still hold "
                     "and the task is skipped; `--rerun` forces it to run.")

set_list(L["terms"], "plain", [
    "A program that turns source code and libraries into tested, packaged software, the same way every time.",
    "One named piece of work in Gradle, such as compileKotlin or test, with declared inputs and outputs.",
    "The tasks Gradle needs for what you asked, ordered so each one runs after the tasks it depends on.",
    "A package of build logic that adds tasks and settings to a project, such as the application plugin.",
    "One part of a Gradle build that can be built on its own, usually a folder with its own build.gradle.kts file.",
    "The step where Gradle runs the build scripts to set up tasks, before any task does real work.",
    "The gradlew script and its files, which download and run the exact Gradle version a project pins.",
    "A task label: Gradle compared the task's inputs and outputs with the last run, found no change, and skipped it.",
])

S = L["sections"]

S[0]["h"] = "From written code to a program that runs"
S[0]["body"] = """Python, the language of hello-devops, runs straight from the text you write. Kotlin works differently. You write source code, the text of a program that people read and edit. Then a compiler translates it into a compact form that a machine can run quickly. To compile is to do that translation, like rewriting a recipe for people as exact cards for a machine-cook.

For Kotlin, the machine-cook is the JVM, short for Java Virtual Machine. It is a program that runs compiled Java or Kotlin code, so the same compiled files work on a Mac, on Linux and on Windows. The compiled files are class files, and a jar is one zip file that holds many of them, like a boxed set of recipe cards.

Two more words and we can start. The JDK, or Java Development Kit, is the toolbox you install to get a JVM and Java's own tools. A library is code that other people wrote and published for reuse, like ready-made pastry from a supplier.

Turning Kotlin source into something you can ship takes more steps than it looks. For one small web service, a program that answers requests over the network, you have to:

- download the libraries it uses, and the libraries those libraries use
- compile the Kotlin code against them
- compile and run the tests
- package the classes into a jar, with start scripts
- do all of it the same way on your laptop and on the CI server

Tests are small programs that check your code gives the right answers, and CI is the automatic checking from Part 6.

The naive way is a shell script that calls `kotlinc`, the Kotlin compiler, and `java`, the command that starts the JVM. It works for one file. Then the classpath (the list of jars the compiler and the JVM can see) grows to 40 jars. A teammate has another JDK, and every run recompiles everything because the script cannot tell what changed.

A **build tool** does these jobs from a description of the project that lives in git. Gradle is the one most Kotlin and Android projects use. Many developers rarely type a Gradle command, because IntelliJ, a popular code editor with built-in tools (an IDE), runs Gradle for them.

In DevOps work the build runs where there is no IDE: on CI runners, in Docker build stages and in release jobs. When a build fails there, the log is all you get, so you need your own picture of what Gradle is doing and why. This part's lab, hello-jvm, is a tiny Kotlin web service. Like hello-devops, it answers every visit with a greeting and a count of visits so far. Next, we'll see how Gradle splits its build into pieces of work."""

S[1]["h"] = "Tasks, and the order they must run in"
S[1]["body"] = """A baker's prep list has lines such as "make the dough", "let it rise", "bake". Each line needs the one before it. Gradle's version of a line is a task. A task has a name such as `compileKotlin`, `test` or `jar`. It also declares its inputs (source files, the classpath, compiler flags) and its outputs (class files, a jar, a test report).

Tasks depend on other tasks. `jar` needs compiled classes, so it depends on `classes`, which depends on `compileKotlin`. When you ask for `build`, Gradle collects every task it needs and puts them in a task graph, the prep list in the right order.

The graph is a DAG (directed acyclic graph): the arrows point one way and never loop back. Gradle runs each task once, in an order that respects the arrows. `build` itself does no work. It groups `assemble`, which makes the outputs, and `check`, which runs the tests.

Declaring inputs and outputs is what makes the second run fast. Before a task runs, Gradle fingerprints its inputs and outputs: it hashes their contents, the same idea as Git's SHA hashes on Day 8. A hash is a short code computed from the contents, and one changed byte changes it.

Gradle compares those hashes with the ones it saved in the project's `.gradle` folder after the last run. If nothing changed, it prints `UP-TO-DATE` and skips the task. That is the baker using this morning's sauce. You will see these labels on task lines:

- `UP-TO-DATE`: nothing changed since the last run, so the task was skipped.
- `NO-SOURCE`: there was nothing to work on, like `compileJava` in a Kotlin-only project.
- `SKIPPED`: skipped on purpose, for example under `--dry-run`.
- `FROM-CACHE`: the outputs were copied from the build cache (Day 30).

The task `compileJava` compiles Java code, so in a project with only Kotlin it has nothing to do. The build cache is a store of earlier outputs that Day 30 sets up. No label means the task did real work. Tasks live inside projects, and the files that describe those come next."""

S[2]["h"] = "Projects, plugins and the three build files"
S[2]["body"] = """A Gradle build is a set of projects. A project is usually one folder with its own build script, the file that describes how to build it. Today your hello-jvm build has a root project and one subproject, `app`. Tomorrow you add a second one.

Three files describe the build:

- `settings.gradle.kts` is read first, once per build. It names the build, lists the projects with `include(...)`, and says where libraries come from.
- `build.gradle.kts` is the build script of one project. It applies plugins and lists the libraries the project needs.
- `gradle.properties` holds flags for Gradle itself, such as turning on the configuration cache.

Libraries come from online stores such as Maven Central. A flag is an on or off setting, and the configuration cache appears two sections from now.

The `.kts` ending means Kotlin script. This is the Kotlin DSL, short for domain-specific language: Kotlin shaped for describing builds. The build files are real Kotlin, so IntelliJ autocompletes them and the compiler catches typos. Older projects use `build.gradle` files written in Groovy, another language. They do the same job with looser syntax. Since Gradle 8, `gradle init` writes Kotlin build files by default.

On its own a build script does very little. Plugins bring the tasks, like a kitchen gadget that comes with its own recipes. In `app/build.gradle.kts`, `kotlin("jvm")` adds `compileKotlin`, `test` and `jar`. The `application` plugin adds `run`, `installDist` and start scripts, small files that start your program for you.

That is why `./gradlew tasks` lists more than 30 tasks for a build script with a dozen real lines. The files look like a program that does the build. They are not, and the next section shows why that matters."""

S[3]["h"] = "Three phases: initialization, configuration, execution"
S[3]["body"] = """Our careful baker reads tomorrow's orders, writes the prep list, and only then starts cooking. Gradle wants the whole plan before it does any work, for the same reason. Only then can it order the tasks, skip the ones that are up to date and run independent ones side by side. So every Gradle run goes through three phases, in this order:

1. Initialization. Gradle reads `settings.gradle.kts` and decides which projects take part.
2. Configuration. Gradle runs the build scripts of those projects. The scripts register tasks and set their properties, and Gradle builds the task graph for what you asked.
3. Execution. Gradle runs the actions of the tasks in the graph, in dependency order.

Take this part slowly, because a build script looks like a program that does the build. It only describes the work. Code at the top level of `build.gradle.kts` runs during configuration. So does code inside `tasks.register("x") { ... }`. Only the code inside `doLast { ... }` runs when the task executes. A `println`, Kotlin's command to print a line, at the top of a build script prints before any task starts.

`tasks.register` is lazy: Gradle only sets up a task when the graph needs it. Top-level code is not lazy. It runs every time Gradle configures the build, which is every run that is not cached, even `./gradlew help`. So keep network calls, big file reads and calls to other programs out of it.

The configuration cache saves the result of phases 1 and 2, the finished prep list. Gradle 9 calls it the preferred mode, and hello-jvm turns it on in `gradle.properties`. The next run with the same scripts and tasks goes straight to execution.

In return, a running task may not reach back into `project`, the live build model. On a cache hit the build scripts never ran and that model does not exist, so Gradle forbids it on every run, hit or miss. The worked example shows the error and the fix. All of this assumes everyone runs the same Gradle, and the next section makes sure they do."""

S[4]["h"] = "The Gradle Wrapper: one Gradle version per project"
S[4]["body"] = """You will almost never type `gradle`. You type `./gradlew`. That script is the **Gradle Wrapper**, and it is why a fresh clone builds the same way on every machine. The wrapper is four files, and you commit all of them:

- `gradlew`, a shell script for macOS and Linux
- `gradlew.bat`, the same for Windows
- `gradle/wrapper/gradle-wrapper.jar`, a small program that downloads Gradle
- `gradle/wrapper/gradle-wrapper.properties`, which names the exact Gradle version

The `gradlew` script starts the small jar with your JDK. The jar reads the properties file and, on the first run, downloads that version into `~/.gradle/wrapper/dists`. Then it hands your command to that Gradle. So you, your teammates and every CI runner use the same Gradle. It does for Gradle what a lockfile, a file that pins exact versions, does for libraries.

A global `gradle` from Homebrew, the Mac installer from Day 2, is whatever version you installed last. And Gradle 9 removed several old APIs, the features that build scripts call. A build can pass on 8.14 and fail on 9.8, or the other way round.

You need a global Gradle only once, to create the wrapper in a new project with `gradle wrapper` (or `gradle init`). Add `--gradle-distribution-sha256-sum` and the wrapper checks every download against that checksum, a fingerprint of the file, and refuses anything else. To upgrade later, run `./gradlew wrapper --gradle-version <new version>`.

Two JDKs are in play. Gradle 9 itself needs Java 17 or newer to run. The JDK that compiles your code is picked separately, by `kotlin { jvmToolchain(21) }` in the build script. Day 30 covers toolchains. With the right Gradle in place, we can run it and read what it says."""

S[5]["h"] = "Running tasks and reading the output"
S[5]["body"] = """Run any task by name: `./gradlew build`, `./gradlew test`, `./gradlew clean`. In a build with several projects, a bare name runs that task in every project that has it. A path picks one project: `./gradlew :app:run` runs `run` in `app` only. The first colon means the root project, like `/` in a file path.

These options come up every week:

- `./gradlew tasks` lists the tasks you can run, by group. `--all` shows every task.
- `./gradlew help --task :app:run` explains one task and its options.
- `--dry-run` lists what would run, without running it.
- `--task-graph` prints the graph as a tree.
- `-q` hides everything except errors and your program's own output.
- `--console=plain` prints one plain line per task, which reads better in CI logs.
- `--args="..."` passes arguments to your program in `./gradlew :app:run`.

Read the output from the bottom. `BUILD SUCCESSFUL in 7s` or `BUILD FAILED` comes last. Above it, a line like `7 actionable tasks: 7 executed` says how many tasks did work and how many were up to date.

When a test fails, Gradle prints the path of an HTML report, a web page such as `app/build/reports/tests/test/index.html`. Open it in your browser. It shows each test, its output and the stack trace, the list of function calls that led to the error. Gradle is not the only build tool you will meet, though."""

S[6]["h"] = "Gradle and Maven, briefly"
S[6]["body"] = """You will meet Maven at work, often in older Java services. Both tools download from the same repositories, such as Maven Central, and both produce the same kind of jar. The model is what differs:

- Maven describes a project in XML (`pom.xml`) and runs a fixed list of phases, such as `compile`, `test`, `package` and `install`. `mvn package` runs every phase up to `package`.
- Gradle builds a graph of tasks from Kotlin or Groovy scripts, and skips each task whose inputs did not change.
- Maven has a wrapper too, `mvnw`, for the same reason Gradle has `gradlew`.
- Rough mapping: `mvn package` is close to `./gradlew assemble`, `mvn verify` is close to `./gradlew build`, and `mvn dependency:tree` is `./gradlew dependencies`.

XML is an older text format with tags in angle brackets. Maven's fixed phases are a recipe always read from the top, while Gradle's graph is the baker's prep list.

For one plain service, neither tool is clearly better. Gradle pulls ahead in big builds, because it reuses so much earlier work (Day 30 shows how). Android builds require Gradle. Spring Initializr, a website that creates new Java projects, offers both, so the choice was usually made before you joined the team. As a DevOps engineer you need to read both and run both in CI.

Today's build has a limit worth naming. hello-jvm uses no libraries beyond Kotlin's own test library, and it is one project. Real services pull in dozens of libraries that pull in more, and they split their code into several projects. Day 29 shows where those libraries come from, and what happens when two of them want different versions of a third."""

L["closing"] = """We started with a baker who followed the menu instead of the work, and ran out of night. Gradle avoids that trap. It reads the settings, writes the prep list from the build scripts, then runs only the tasks whose inputs changed.

In hello-jvm, run `./gradlew build --console=plain` twice and read the labels. Find the NO-SOURCE line, and count the UP-TO-DATE ones on the second run.

Next, we'll open the pantry. Where do libraries come from, and what does Gradle do when two of them ask for different versions of the same third library?"""

drop_extras(L)

set_list(L["worked"]["steps"], "say", [
    "Make a folder `lifecycle-demo`, copy `gradlew` and the `gradle/wrapper/` folder into it from `~/code/devops-from-zero/labs/hello-jvm`, and put `org.gradle.configuration-cache=true` in `gradle.properties`. Then write a settings file that prints one line. It runs in the initialization phase.",
    "The build script prints at the top level, inside the setup block of `hello`, and inside `doLast`. A second task, `bad`, reads `project` inside `doLast`. Before you run anything, predict which lines print for `./gradlew hello`.",
    "First run. Lines 1 and 2 print before any task starts, and line 2b prints because the graph needs `hello`. Only line 3 comes from the task's action.",
    "Same command again. The configuration cache saved the task graph, so Gradle skipped initialization and configuration. Nothing from the scripts printed. The task still ran: it declares no outputs, so Gradle cannot call it up to date.",
    "Now run `bad`. Line 2b is missing: Gradle never set up `hello`, because `register` is lazy. Then `bad` fails. With the configuration cache on, a running task may not touch `project`.",
    "To fix it, read the value during configuration and keep only the result. Add a `good` task and run it. `unspecified` is what a project's version is when nobody set one.",
])

L["task"]["steps"] = [
    "Check that you have a JDK 17 or newer with `java -version`. If not, install one, for example `brew install --cask temurin@21`.",
    "Install Gradle once with `brew install gradle`. You need it for one thing only: creating the wrapper in step 4.",
    "Create `~/code/hello-jvm` and add `settings.gradle.kts`, `gradle.properties`, `.gitignore` and `app/build.gradle.kts` from Files. Create the `app` folder before you run Gradle: Gradle 9 refuses to set up a project whose folder does not exist.",
    "Create the wrapper with `gradle wrapper`, pinning version 9.8.2 and its checksum. Check it with `./gradlew --version`.",
    "Add `Main.kt` and `MainTest.kt` from Files. Run `./gradlew build` and read which tasks ran and which had NO-SOURCE.",
    "Run `./gradlew build` again and count the UP-TO-DATE tasks. Then change only `MainTest.kt`, predict which tasks will run, and check.",
    "Start the service with `./gradlew :app:run` and call `curl localhost:8080` a few times from a second terminal. Stop it with Ctrl+C.",
    "Run `./gradlew :app:installDist`, then start the service without Gradle: `app/build/install/app/bin/app`.",
    "Run `git init`, commit everything (including the four wrapper files), create a `hello-jvm` repository on GitHub and push.",
]
L["task"]["hints"] = [
    "`curl -s https://services.gradle.org/versions/current` prints the version and the checksum to pass with `--gradle-distribution-sha256-sum`.",
    "A test-only change should leave `compileKotlin` and `jar` UP-TO-DATE. Only test compilation and the tests do work.",
]
L["task"]["done_when"] = "You are done when the second `./gradlew build` ends with `7 actionable tasks: 7 up-to-date`, and `curl localhost:8080` shows `visits` going up."

L["explain_back"]["answer"] = ("First Gradle reads the settings file to find out which projects are in the build. "
                               "Then it runs the build scripts of those projects, which register and set up tasks, and it builds a graph of the tasks I asked for. "
                               "Only after that does it run the tasks' actions, in dependency order. "
                               "A `println` at the top of a build script runs in the configuration phase, before any task starts. "
                               "The configuration cache saves the task graph, so a repeat run with the same scripts skips the first two phases and goes straight to execution.")

L["recap"] = [
    "Kotlin is compiled into class files for the JVM; a build tool turns source and libraries into tested, packaged software, the same way every time.",
    "Plugins add tasks; `build` pulls in `assemble` (outputs) and `check` (tests).",
    "Every run has three phases: initialization (settings), configuration (build scripts) and execution (task actions); only `doLast` code runs when a task executes.",
    "A task whose inputs and outputs did not change is skipped as UP-TO-DATE.",
    "Always run `./gradlew`: the wrapper pins the Gradle version and can check its checksum.",
    "The limit: today's build has one project and no outside libraries, and Day 29 adds both.",
]

C = L["check"]
C[0]["why"] = "Top-level script code runs in the configuration phase of every run that is not served from the configuration cache."
C[1]["why"] = "The wrapper makes CI download and use the version the project pins, so it can never drift from laptops again."
C[2]["why"] = ("UP-TO-DATE means skipped because nothing changed, and a task line with no label did real work "
               "(here, perhaps because the old jar was deleted).")

I = L["interview"]
I[0]["a"] = ("The wrapper is the `gradlew` script, a small jar and a properties file that names one Gradle version. "
             "Running `./gradlew` downloads exactly that version and uses it, so every developer and CI runner builds with the same Gradle. "
             "You commit all four files so a fresh clone needs only a JDK. "
             "I also set `distributionSha256Sum`, so a tampered download is refused. "
             "An upgrade is then a small change that goes through review like any other.")
I[1]["a"] = ("Initialization reads the settings file and decides which projects take part. "
             "Configuration runs their build scripts, which register tasks, and Gradle builds the task graph for the requested tasks. "
             "Execution runs the task actions in dependency order and skips tasks whose inputs and outputs are unchanged. "
             "The common mistake is heavy work at configuration time, which slows every run, even `help`. "
             "The configuration cache skips the first two phases when nothing relevant changed.")
I[2]["a"] = ("Each task declares inputs, such as source files, the classpath and flags, and outputs, such as class files. "
             "After a run, Gradle stores fingerprints of both. "
             "Next time it compares fresh fingerprints with the stored ones, and if nothing differs and the outputs are still there, it skips the task. "
             "A task that declares no outputs can never be up to date, so it always runs.")

L["deeper"]["body"] = """Gradle will tell you why a task ran if you add `--info`. After we added a comment to `Main.kt`, `./gradlew :app:compileKotlin --info` printed:

- `Task ':app:compileKotlin' is not up-to-date because:`
- `Input property 'sources' file .../app/src/main/kotlin/hello/app/Main.kt has changed.`

So what goes into the comparison? Four things:

1. Input files, by content hash. Timestamps do not matter: `touch Main.kt` (which only updates the file's time) leaves all 7 tasks up to date, while one changed byte does not.
2. Input properties, such as the JVM target or compiler flags.
3. The task's own code. Upgrade the Kotlin plugin and every Kotlin compile task runs again.
4. Output files. Delete `app/build/libs/app.jar` and only `jar` runs again. The tasks after it stay up to date, because Gradle 9 builds the same jar byte for byte.

A task with no declared outputs, like `hello` in the worked example, always runs, because there is nothing to compare. A test-only change runs `compileTestKotlin` and `test`, but `compileKotlin` and `jar` stay up to date, because their inputs are the main source files only.

And a task's outputs are the next task's inputs. If `compileKotlin` runs but produces byte-for-byte the same class files, the tasks after it can still be skipped. The baker who remakes the sauce and gets exactly the same sauce need not redo the dish. Day 30 uses that to explain compile avoidance across projects.

Two flags force work. The `--rerun` flag reruns the one task you name, for example `./gradlew test --rerun` when you suspect a flaky test, one that passes and fails at random. The `--rerun-tasks` flag reruns every task in the graph, which is slow and almost never what you want. If you reach for it often, a task is probably missing an input, and the real fix is in the build logic.

When a build surprises you, read the task lines before you read the error. They tell you what Gradle thought had changed. If you want to see the whole graph first, `--task-graph` prints it without running anything."""

save(path, P)
print("d28 written")
