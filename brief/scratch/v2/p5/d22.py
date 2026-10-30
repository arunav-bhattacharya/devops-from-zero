from common import d22, demo, svg, box, arrow, line, cap

SUM = "21bd5da2de49b642904077f38c0efdc7778e92b3ed0889392dca61b97e389607"

diagram = svg(170, "Gradle's three phases: the settings file is read, build scripts build the task graph, then tasks run; a configuration cache hit jumps straight to the task graph", "".join([
    box(8, 66, 128, 40, "bx", "settings file"),
    box(160, 66, 128, 40, "bxt", "build scripts"),
    box(312, 66, 112, 40, "bxg", "task graph"),
    box(448, 66, 104, 40, "bxo", "run tasks"),
    arrow(138, 86, 157, 86),
    arrow(290, 86, 309, 86),
    arrow(426, 86, 445, 86),
    line(72, 62, 72, 34, dashed=True),
    line(72, 34, 368, 34, dashed=True),
    arrow(368, 34, 368, 62, dashed=True),
    cap(220, 26, "configuration cache hit"),
    cap(72, 128, "1 initialization"),
    cap(292, 128, "2 configuration"),
    cap(500, 128, "3 execution"),
    cap(72, 148, "which projects?"),
    cap(292, 148, "register and set up tasks"),
    cap(500, 148, "doLast code runs"),
]))

L = {
    "id": "d22",
    "title": "What a build tool does, and how Gradle thinks",
    "minutes": 50,
    "goal": "By the end you can explain Gradle's model of projects, tasks and phases, create a project with the Gradle Wrapper, and predict which tasks a build will run or skip.",
    "guess": {
        "q": "You run `./gradlew test`, change nothing, and run it again. What does Gradle do with the tests the second time?",
        "options": [
            "Compiles everything again and reruns every test",
            "Reruns only the tests that failed last time",
            "Skips the test task and marks it UP-TO-DATE",
            "Asks you whether the tests should run again",
        ],
        "answer": 2,
        "why": "Gradle fingerprints every task's inputs and outputs. Nothing changed, so the last results still hold and the task is skipped; `--rerun` forces it to run.",
    },
    "terms": [
        {"term": "Build tool", "plain": "A program that turns source code and libraries into tested, packaged software, the same way every time."},
        {"term": "Task", "plain": "One named unit of work in Gradle, such as compileKotlin or test, with declared inputs and outputs."},
        {"term": "Task graph", "plain": "The tasks Gradle needs for what you asked, ordered so each one runs after the tasks it depends on."},
        {"term": "Plugin", "plain": "A package of build logic that adds tasks and settings to a project, such as the application plugin."},
        {"term": "Project", "plain": "One buildable unit in a Gradle build, usually a folder with its own build.gradle.kts file."},
        {"term": "Configuration phase", "plain": "The step where Gradle runs the build scripts to set up tasks, before any task does real work."},
        {"term": "Gradle Wrapper", "plain": "The gradlew script and its files, which download and run the exact Gradle version a project pins."},
        {"term": "UP-TO-DATE", "plain": "A task label: Gradle compared the task's inputs and outputs with the last run, found no change, and skipped it."},
    ],
    "sections": [
        {
            "h": "What a build tool does",
            "body": (
                "Turning Kotlin source into something you can ship takes more steps than it looks. For one small web service you have to:\n\n"
                "- download the libraries it uses, and the libraries those libraries use\n"
                "- compile the Kotlin code against them\n"
                "- compile and run the tests\n"
                "- package the classes into a jar, with start scripts\n"
                "- do all of it the same way on your laptop and on the CI server\n\n"
                "A shell script that calls `kotlinc` and `java` works for one file. Then the classpath grows to 40 jars, a teammate has another JDK, and every run recompiles everything because the script cannot tell what changed.\n\n"
                "A **build tool** does these jobs from a description of the project that lives in git. Gradle is the one most Kotlin and Android projects use, and you already use it every day through IntelliJ. This lesson opens the box. In DevOps work you run builds where there is no IDE: on CI runners, in Docker build stages and in release jobs. There you need to know what Gradle is doing and why."
            ),
            "refs": [
                {"title": "Gradle course for beginners (Tom Gregory)", "url": "https://www.youtube.com/watch?v=R6Z-Sxb837I", "kind": "watch"},
                {"title": "What's new in Gradle 9", "url": "https://gradle.org/whats-new/gradle-9/", "kind": "read"},
            ],
        },
        {
            "h": "Tasks and the task graph",
            "body": (
                "Gradle's unit of work is a task. A task has a name such as `compileKotlin`, `test` or `jar`. It also declares its inputs (source files, the classpath, compiler flags) and its outputs (class files, a jar, a test report).\n\n"
                "Tasks depend on other tasks. `jar` needs compiled classes, so it depends on `classes`, which depends on `compileKotlin`. When you ask for `build`, Gradle collects every task it needs and puts them in a task graph. The graph is a DAG (directed acyclic graph): the arrows point one way and never loop back. Gradle runs each task once, in an order that respects the arrows. `build` itself does no work. It groups `assemble`, which makes the outputs, and `check`, which runs the tests.\n\n"
                "Declaring inputs and outputs pays off on the second run. Before a task runs, Gradle fingerprints its inputs and outputs and compares them with the last run. If nothing changed, it prints `UP-TO-DATE` and skips the task. You will see these labels on task lines:\n\n"
                "- `UP-TO-DATE`: nothing changed since the last run, so the task was skipped.\n"
                "- `NO-SOURCE`: there was nothing to work on, like `compileJava` in a Kotlin-only project.\n"
                "- `SKIPPED`: skipped on purpose, for example under `--dry-run`.\n"
                "- `FROM-CACHE`: the outputs were copied from the build cache (Day 24).\n\n"
                "No label means the task did real work."
            ),
            "refs": [
                {"title": "Gradle docs: Incremental builds and build caching basics", "url": "https://docs.gradle.org/current/userguide/gradle_optimizations.html", "kind": "docs"},
            ],
        },
        {
            "h": "Projects, plugins and the build files",
            "body": (
                "A Gradle build is a set of projects. A project is usually one folder with its own build script. Today your hello-jvm build has a root project and one subproject, `app`. Tomorrow you add a second one.\n\n"
                "Three files describe the build:\n\n"
                "- `settings.gradle.kts` is read first, once per build. It names the build, lists the projects with `include(...)`, and says where libraries come from.\n"
                "- `build.gradle.kts` is the build script of one project. It applies plugins and lists the libraries the project needs.\n"
                "- `gradle.properties` holds flags for Gradle itself, such as turning on the configuration cache.\n\n"
                "The `.kts` ending means Kotlin script. This is the Kotlin DSL: the build files are real Kotlin, so IntelliJ autocompletes them and the compiler catches typos. Older projects use `build.gradle` files written in Groovy. They do the same job with looser syntax. Since Gradle 8, `gradle init` writes Kotlin build files by default.\n\n"
                "On its own a build script does very little. Plugins bring the tasks. In `app/build.gradle.kts`, `kotlin(\"jvm\")` adds `compileKotlin`, `test` and `jar`, and the `application` plugin adds `run`, `installDist` and start scripts. That is why `./gradlew tasks` lists more than 30 tasks for a build script with a dozen real lines."
            ),
            "refs": [
                {"title": "Understanding Gradle #01: the settings file (Jendrik Johannes)", "url": "https://www.youtube.com/watch?v=Ajs8pTbg8as", "kind": "watch"},
                {"title": "Understanding Gradle #02: the build files (Jendrik Johannes)", "url": "https://www.youtube.com/watch?v=OKjE_Lt_66U", "kind": "watch"},
            ],
        },
        {
            "h": "Three phases: initialization, configuration, execution",
            "body": (
                "This is the idea that trips up most people, so take it slowly. Every Gradle run goes through three phases, in this order:\n\n"
                "1. Initialization. Gradle reads `settings.gradle.kts` and decides which projects take part.\n"
                "2. Configuration. Gradle runs the build scripts of those projects. The scripts register tasks and set their properties, and Gradle builds the task graph for what you asked.\n"
                "3. Execution. Gradle runs the actions of the tasks in the graph, in dependency order.\n\n"
                "Here is the trap. A build script does not do the work; it describes the work. Code at the top level of `build.gradle.kts` runs during configuration. So does code inside `tasks.register(\"x\") { ... }`. Only the code inside `doLast { ... }` runs when the task executes. A `println` at the top of a build script prints before any task starts.\n\n"
                "`tasks.register` is lazy: Gradle only sets up a task when the graph needs it. Still, keep slow work out of configuration. No network calls, no big file reads, no running programs at the top level. Configuration happens on every run that is not cached, even `./gradlew help`.\n\n"
                "Gradle 9 adds the configuration cache. It saves the result of phases 1 and 2, and the next run with the same scripts and tasks goes straight to execution. In return, a running task may not reach back into `project`, the live build model. The worked example shows the error and the fix."
            ),
            "refs": [
                {"title": "Gradle docs: Build lifecycle", "url": "https://docs.gradle.org/current/userguide/build_lifecycle.html", "kind": "docs"},
                {"title": "Gradle docs: Configuration cache", "url": "https://docs.gradle.org/current/userguide/configuration_cache.html", "kind": "docs"},
            ],
        },
        {
            "h": "The Gradle Wrapper: one Gradle version per project",
            "body": (
                "You will almost never type `gradle`. You type `./gradlew`. That script is the **Gradle Wrapper**, and it is why a fresh clone builds the same way on every machine. The wrapper is four files, and you commit all of them:\n\n"
                "- `gradlew`, a shell script for macOS and Linux\n"
                "- `gradlew.bat`, the same for Windows\n"
                "- `gradle/wrapper/gradle-wrapper.jar`, a small program that downloads Gradle\n"
                "- `gradle/wrapper/gradle-wrapper.properties`, which names the exact Gradle version\n\n"
                "On the first run, `./gradlew` downloads that version into `~/.gradle/wrapper/dists`. After that, you, your teammates and every CI runner use the same Gradle. Think of it as a lockfile for the build tool. A global `gradle` from Homebrew is whatever version you installed last, and Gradle 9 removed several old APIs. A build can pass on 8.14 and fail on 9.8, or the other way round.\n\n"
                "You need a global Gradle only once, to create the wrapper in a new project with `gradle wrapper` (or `gradle init`). Add `--gradle-distribution-sha256-sum` and the wrapper checks every download against that checksum and refuses anything else. To upgrade later, run `./gradlew wrapper --gradle-version <new version>`.\n\n"
                "Two JDKs are in play. Gradle 9 itself needs Java 17 or newer to run. The JDK that compiles your code is picked separately, by `kotlin { jvmToolchain(21) }` in the build script. Day 24 covers toolchains."
            ),
            "refs": [
                {"title": "Gradle docs: The Gradle Wrapper", "url": "https://docs.gradle.org/current/userguide/gradle_wrapper.html", "kind": "docs"},
                {"title": "Gradle docs: Best practices for security", "url": "https://docs.gradle.org/current/userguide/best_practices_security.html", "kind": "docs"},
            ],
        },
        {
            "h": "Running tasks and reading the output",
            "body": (
                "Run any task by name: `./gradlew build`, `./gradlew test`, `./gradlew clean`. In a build with several projects, a bare name runs that task in every project that has it. A path picks one project: `./gradlew :app:run` runs `run` in `app` only. The first colon means the root project, like `/` in a file path.\n\n"
                "These options come up every week:\n\n"
                "- `./gradlew tasks` lists the tasks you can run, by group. `--all` shows every task.\n"
                "- `./gradlew help --task :app:run` explains one task and its options.\n"
                "- `--dry-run` lists what would run, without running it.\n"
                "- `--task-graph` prints the graph as a tree.\n"
                "- `-q` hides everything except errors and your program's own output.\n"
                "- `--console=plain` prints one plain line per task, which reads better in CI logs.\n"
                "- `--args=\"...\"` passes arguments to your program in `./gradlew :app:run`.\n\n"
                "Read the output from the bottom. `BUILD SUCCESSFUL in 7s` or `BUILD FAILED` comes last. Above it, a line like `7 actionable tasks: 7 executed` says how many tasks did work and how many were up to date. When a test fails, Gradle prints the path of an HTML report, such as `app/build/reports/tests/test/index.html`. Open it in your browser: it shows each test, its output and the stack trace."
            ),
            "refs": [
                {"title": "Gradle docs: Command-line interface", "url": "https://docs.gradle.org/current/userguide/command_line_interface.html", "kind": "docs"},
            ],
        },
        {
            "h": "Gradle and Maven, briefly",
            "body": (
                "You will meet Maven at work, often in older Java services. Both tools download from the same repositories, such as Maven Central, and both produce the same kind of jar. The model is what differs:\n\n"
                "- Maven describes a project in XML (`pom.xml`) and runs a fixed list of phases, such as `compile`, `test`, `package` and `install`. `mvn package` runs every phase up to `package`.\n"
                "- Gradle builds a graph of tasks from Kotlin or Groovy scripts, and skips each task whose inputs did not change.\n"
                "- Maven has a wrapper too, `mvnw`, for the same reason Gradle has `gradlew`.\n"
                "- Rough mapping: `mvn package` is close to `./gradlew assemble`, `mvn verify` is close to `./gradlew build`, and `mvn dependency:tree` is `./gradlew dependencies`.\n\n"
                "For one plain service, neither tool is clearly better. Gradle pulls ahead in big builds, because it reuses so much earlier work (Day 24 shows how). Android builds require Gradle. Spring Initializr offers both, so the choice was usually made before you joined the team. As a DevOps engineer you need to read both and run both in CI."
            ),
            "refs": [
                {"title": "Gradle vs Maven (Gradle's own comparison)", "url": "https://gradle.org/maven-vs-gradle", "kind": "read"},
            ],
        },
    ],
    "analogy": (
        "Gradle works like a careful cook with a recipe book. First the cook reads the recipes for tonight's menu and writes down which dish needs which (configuration). Then the cook works through that list in order (execution). "
        "If a sauce from an hour ago was made from exactly the same ingredients, the cook uses it again instead of making it twice (UP-TO-DATE). "
        "Where it breaks: a cook judges by eye, while Gradle compares exact fingerprints of every input file, so one changed byte means the task runs again."
    ),
    "diagram": diagram,
    "diagram_caption": "Every run reads settings, runs the build scripts to build the task graph, then runs task actions. A configuration cache hit skips the first two phases.",
    "worked": {
        "title": "Watch the three phases happen",
        "steps": [
            {
                "say": "Make a folder `lifecycle-demo`, copy `gradlew` and the `gradle/wrapper/` folder into it from hello-jvm, and put `org.gradle.configuration-cache=true` in `gradle.properties`. Then write a settings file that prints one line. It runs in the initialization phase.",
                "code": "$ cat settings.gradle.kts\n" + demo("settings.gradle.kts"),
                "lang": "console",
            },
            {
                "say": "The build script prints at the top level, inside the setup block of `hello`, and inside `doLast`. A second task, `bad`, reads `project` inside `doLast`. Before you run anything, predict which lines print for `./gradlew hello`.",
                "code": "\n".join(demo("build.gradle.kts").splitlines()[:10]),
                "lang": "text",
            },
            {
                "say": "First run. Lines 1 and 2 print before any task starts, and line 2b prints because the graph needs `hello`. Only line 3 comes from the task's action.",
                "code": "$ ./gradlew hello --console=plain\nCalculating task graph as no cached configuration is available for tasks: hello\n1. initialization: reading settings.gradle.kts\n\n> Configure project :\n2. configuration: running build.gradle.kts\n2b. configuration: setting up the hello task\n\n> Task :hello\n3. execution: hello runs its action\n\nBUILD SUCCESSFUL in 2s\n1 actionable task: 1 executed\nConfiguration cache entry stored.",
                "lang": "console",
            },
            {
                "say": "Same command again. The configuration cache saved the task graph, so Gradle skipped initialization and configuration. Nothing from the scripts printed. The task still ran: it declares no outputs, so Gradle cannot call it up to date.",
                "code": "$ ./gradlew hello --console=plain\nReusing configuration cache.\n\n> Task :hello\n3. execution: hello runs its action\n\nBUILD SUCCESSFUL in 1s\n1 actionable task: 1 executed\nConfiguration cache entry reused.",
                "lang": "console",
            },
            {
                "say": "Now run `bad`. Line 2b is missing: Gradle never set up `hello`, because `register` is lazy. Then `bad` fails. With the configuration cache on, a running task may not touch `project`.",
                "code": "$ ./gradlew bad --console=plain\n1. initialization: reading settings.gradle.kts\n\n> Configure project :\n2. configuration: running build.gradle.kts\n\n> Task :bad FAILED\n...\n* What went wrong:\nExecution failed for task ':bad' (registered in build file 'build.gradle.kts').\n> Invocation of 'Task.project' by task ':bad' at execution time is unsupported with the configuration cache.",
                "lang": "console",
            },
            {
                "say": "The fix: read the value during configuration and keep only the result. Add a `good` task and run it. `unspecified` is what a project's version is when nobody set one.",
                "code": "$ tail -4 build.gradle.kts\n" + "\n".join(demo("build.gradle.kts").splitlines()[-4:]) + "\n$ ./gradlew good -q\nversion is unspecified",
                "lang": "console",
            },
        ],
    },
    "code": [
        {"lang": "text", "title": "settings.gradle.kts", "src": d22("settings.gradle.kts"), "run": "./gradlew projects"},
        {"lang": "ini", "title": "gradle.properties", "src": d22("gradle.properties"), "run": "./gradlew help"},
        {"lang": "text", "title": ".gitignore", "src": d22(".gitignore"), "run": "git status --short"},
        {"lang": "ini", "title": "gradle/wrapper/gradle-wrapper.properties (written by the wrapper task, do not edit by hand)", "src": "distributionBase=GRADLE_USER_HOME\ndistributionPath=wrapper/dists\ndistributionSha256Sum=" + SUM + "\ndistributionUrl=https\\://services.gradle.org/distributions/gradle-9.8.2-bin.zip\nnetworkTimeout=10000\nretries=0\nretryBackOffMs=500\nvalidateDistributionUrl=true\nzipStoreBase=GRADLE_USER_HOME\nzipStorePath=wrapper/dists", "run": "./gradlew --version"},
        {"lang": "text", "title": "app/build.gradle.kts", "src": d22("app/build.gradle.kts"), "run": "./gradlew :app:tasks"},
        {"lang": "text", "title": "app/src/main/kotlin/hello/app/Main.kt", "src": d22("app/src/main/kotlin/hello/app/Main.kt"), "run": "./gradlew :app:run"},
        {"lang": "text", "title": "app/src/test/kotlin/hello/app/MainTest.kt", "src": d22("app/src/test/kotlin/hello/app/MainTest.kt"), "run": "./gradlew test"},
    ],
    "commands": [
        {"cmd": "brew install gradle", "what": "Install a global Gradle once. You only use it to create the wrapper in a new project."},
        {"cmd": "curl -s https://services.gradle.org/versions/current", "what": "Show the newest Gradle version and the SHA-256 checksum of its download."},
        {"cmd": "gradle wrapper --gradle-version 9.8.2 --gradle-distribution-sha256-sum " + SUM, "what": "Create gradlew, gradlew.bat and gradle/wrapper/, pinned to one version and checksum."},
        {"cmd": "./gradlew --version", "what": "Show the Gradle, Kotlin and JVM versions the wrapper uses."},
        {"cmd": "./gradlew build", "what": "Compile, test and package every project: assemble plus check."},
        {"cmd": "./gradlew test", "what": "Compile the code and run the tests only."},
        {"cmd": "./gradlew :app:run", "what": "Run main() of the app project (added by the application plugin)."},
        {"cmd": "./gradlew :app:installDist", "what": "Put start scripts and all jars in app/build/install/app."},
        {"cmd": "./gradlew clean", "what": "Delete the build folders."},
        {"cmd": "./gradlew tasks --all", "what": "List every task you can run, grouped."},
        {"cmd": "./gradlew help --task :app:run", "what": "Explain one task: its type, group and options."},
        {"cmd": "./gradlew build --dry-run", "what": "List the tasks a build would run, without running them."},
        {"cmd": "./gradlew :app:assemble --task-graph", "what": "Print the task graph as a tree, without running it."},
        {"cmd": "./gradlew test --rerun", "what": "Run a task even when it is up to date."},
        {"cmd": "./gradlew :app:compileKotlin --info", "what": "Show detail, including why a task was not up to date."},
        {"cmd": "./gradlew wrapper --gradle-version 9.8.2", "what": "Change the Gradle version the wrapper pins (run it again to refresh the scripts)."},
    ],
    "mistake": (
        "Running `gradle build` with a global Gradle instead of `./gradlew build`. The global one is whatever version you installed last, so the build can pass for you and fail in CI, or the other way round. "
        "Always run `./gradlew`, and keep IntelliJ on the wrapper (its default). Use a global Gradle only to create the wrapper once."
    ),
    "real_world": (
        "At a payments company (call it Paylane), the ledger service has many Gradle projects, and CI runs `./gradlew build` on every pull request. "
        "The wrapper pins Gradle, so laptops and runners agree, and a Gradle upgrade is an ordinary pull request that changes `gradle-wrapper.properties`. "
        "When CI gets slow, the first thing the team reads is which tasks did work and which were UP-TO-DATE or FROM-CACHE."
    ),
    "task": {
        "title": "Start hello-jvm",
        "steps": [
            "Check that you have a JDK 17 or newer with `java -version`. If not, install one, for example `brew install --cask temurin@21`.",
            "Install Gradle once with `brew install gradle`. You only need it for the next step but one.",
            "Create `~/code/hello-jvm` and add `settings.gradle.kts`, `gradle.properties`, `.gitignore` and `app/build.gradle.kts` from Files. Create the `app` folder before you run Gradle: Gradle 9 refuses to set up a project whose folder does not exist.",
            "Create the wrapper with `gradle wrapper`, pinning version 9.8.2 and its checksum. Check it with `./gradlew --version`.",
            "Add `Main.kt` and `MainTest.kt` from Files. Run `./gradlew build` and read which tasks ran and which had NO-SOURCE.",
            "Run `./gradlew build` again and count the UP-TO-DATE tasks. Then change only `MainTest.kt`, predict which tasks will run, and check.",
            "Start the service with `./gradlew :app:run` and call `curl localhost:8080` a few times from a second terminal. Stop it with Ctrl+C.",
            "Run `./gradlew :app:installDist`, then start the service without Gradle: `app/build/install/app/bin/app`.",
            "Run `git init`, commit everything (including the four wrapper files), create a `hello-jvm` repository on GitHub and push.",
        ],
        "hints": [
            "`curl -s https://services.gradle.org/versions/current` prints the version and the checksum to pass with `--gradle-distribution-sha256-sum`.",
            "A test-only change should leave `compileKotlin` and `jar` UP-TO-DATE. Only test compilation and the tests do work.",
        ],
        "done_when": "The second `./gradlew build` ends with `7 actionable tasks: 7 up-to-date`, and `curl localhost:8080` shows `visits` going up.",
    },
    "explain_back": {
        "prompt": "Explain Gradle's three phases in 3 to 4 sentences. Mention when a `println` at the top of build.gradle.kts runs, and what the configuration cache lets Gradle skip.",
        "answer": (
            "First Gradle reads the settings file to find out which projects are in the build. Then it runs the build scripts of those projects, which register and set up tasks, and it builds a graph of the tasks I asked for. "
            "Only after that does it run the tasks' actions, in dependency order. A `println` at the top of a build script runs in the configuration phase, before any task starts. "
            "The configuration cache saves the task graph, so a repeat run with the same scripts skips the first two phases and goes straight to execution."
        ),
    },
    "recap": [
        "A build tool turns source and libraries into tested, packaged software, the same way every time.",
        "Plugins add tasks; `build` pulls in `assemble` (outputs) and `check` (tests).",
        "Every run has three phases: initialization (settings), configuration (build scripts) and execution (task actions).",
        "Build scripts describe the work; only `doLast` code runs when a task executes.",
        "A task whose inputs and outputs did not change is skipped as UP-TO-DATE.",
        "Always run `./gradlew`: the wrapper pins the Gradle version and can check its checksum.",
    ],
    "check": [
        {
            "q": "A teammate puts `val token = File(\"/tmp/token\").readText()` at the top of build.gradle.kts. When is the file read?",
            "options": [
                "Only when a task that uses `token` runs",
                "During configuration, before any task runs",
                "Only during `./gradlew build`, not `test`",
                "Once, when the wrapper first downloads Gradle",
            ],
            "answer": 1,
            "why": "Top-level script code runs in the configuration phase of every run that is not served from the configuration cache.",
        },
        {
            "q": "CI runs `gradle build` with Gradle 8.14 from the runner image. Your laptop runs `./gradlew build` on 9.8.2. CI fails on a removed API. What is the best fix?",
            "options": [
                "Install Gradle 9.8.2 on the CI image",
                "Delete gradle-wrapper.properties from git",
                "Add `--rerun` to the CI command",
                "Change CI to run `./gradlew build`",
            ],
            "answer": 3,
            "why": "The wrapper makes CI download and use the version the project pins, so it can never drift from laptops again.",
        },
        {
            "q": "`./gradlew :app:jar` prints `> Task :app:compileKotlin UP-TO-DATE` and then `> Task :app:jar` with no label. What happened?",
            "options": [
                "Compiling was skipped; the jar was rebuilt",
                "Compiling failed without an error message",
                "Neither task did any work this time",
                "Both outputs came from another machine",
            ],
            "answer": 0,
            "why": "UP-TO-DATE means skipped because nothing changed, and a task line with no label did real work (here, perhaps because the old jar was deleted).",
        },
    ],
    "interview": [
        {
            "q": "What is the Gradle Wrapper, and why commit it?",
            "a": "The wrapper is the `gradlew` script, a small jar and a properties file that names one Gradle version. Running `./gradlew` downloads exactly that version and uses it, so every developer and CI runner builds with the same Gradle. You commit all four files so a fresh clone needs only a JDK. I also set `distributionSha256Sum`, so a tampered download is refused, and upgrades become a reviewed one-line change.",
        },
        {
            "q": "Walk me through Gradle's build lifecycle.",
            "a": "Initialization reads the settings file and decides which projects take part. Configuration runs their build scripts, which register tasks, and Gradle builds the task graph for the requested tasks. Execution runs the task actions in dependency order and skips tasks whose inputs and outputs are unchanged. The common mistake is heavy work at configuration time, which slows every run, even `help`. The configuration cache skips the first two phases when nothing relevant changed.",
        },
        {
            "q": "How does Gradle decide that a task is UP-TO-DATE?",
            "a": "Each task declares inputs, such as source files, the classpath and flags, and outputs, such as class files. After a run, Gradle stores fingerprints of both. Next time it compares fresh fingerprints with the stored ones, and if nothing differs and the outputs are still there, it skips the task. A task that declares no outputs can never be up to date, so it always runs.",
        },
    ],
    "deeper": {
        "minutes": 12,
        "body": (
            "Gradle does not guess when it skips a task. Ask it why a task ran with `--info`. After adding a comment to `Main.kt`, `./gradlew :app:compileKotlin --info` printed:\n\n"
            "- `Task ':app:compileKotlin' is not up-to-date because:`\n"
            "- `Input property 'sources' file .../app/src/main/kotlin/hello/app/Main.kt has changed.`\n\n"
            "So what goes into the comparison? Four things:\n\n"
            "1. Input files, by content hash. Timestamps do not matter: `touch Main.kt` leaves all 7 tasks up to date, while one changed byte does not.\n"
            "2. Input properties, such as the JVM target or compiler flags.\n"
            "3. The task's own code. Upgrade the Kotlin plugin and every Kotlin compile task runs again.\n"
            "4. Output files. Delete `app/build/libs/app.jar` and only `jar` runs again. The tasks after it stay up to date, because Gradle 9 builds the same jar byte for byte.\n\n"
            "This explains a few things you will see. A task with no declared outputs, like `hello` in the worked example, always runs. A test-only change runs `compileTestKotlin` and `test`, but `compileKotlin` and `jar` stay up to date, because their inputs are the main source files only. And a task's outputs are the next task's inputs. If `compileKotlin` runs but produces byte-for-byte the same class files, the tasks after it can still be skipped. Day 24 uses that to explain compile avoidance across projects.\n\n"
            "Two flags force work. `--rerun` reruns the one task you name, for example `./gradlew test --rerun` when you suspect a flaky test. `--rerun-tasks` reruns every task in the graph, which is slow and almost never what you want. If you reach for it often, a task is probably missing an input, and the real fix is in the build logic.\n\n"
            "One more habit worth building now: when a build surprises you, read the task lines before you read the error. They tell you what Gradle thought had changed. If you want to see the whole graph first, `--task-graph` prints it without running anything."
        ),
    },
    "sources": [
        {"title": "Gradle docs: Build lifecycle", "url": "https://docs.gradle.org/current/userguide/build_lifecycle.html"},
        {"title": "Gradle docs: The Gradle Wrapper", "url": "https://docs.gradle.org/current/userguide/gradle_wrapper.html"},
        {"title": "Gradle docs: Command-line interface", "url": "https://docs.gradle.org/current/userguide/command_line_interface.html"},
        {"title": "What's new in Gradle 9", "url": "https://gradle.org/whats-new/gradle-9/"},
    ],
}
