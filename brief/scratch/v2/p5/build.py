#!/usr/bin/env python3
"""Build content/p5.json (Part 5: Builds with Gradle) from d22.py, d23.py and d24.py."""
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import d22  # noqa: E402
import d23  # noqa: E402
import d24  # noqa: E402

PART = {
    "part": 5,
    "title": "Builds with Gradle",
    "intro": (
        "You use Gradle every day through IntelliJ, but in DevOps work you run builds where there is no IDE: on CI runners and inside Docker builds. "
        "This part teaches Gradle's model from the ground up with a new lab, hello-jvm, a small Kotlin web service that mirrors hello-devops. "
        "It comes after Docker and GitHub Actions because Day 24 uses both to build, cache and ship that service."
    ),
    "lessons": [d22.L, d23.L, d24.L],
    "recap": [
        "The Gradle Wrapper pins one Gradle version per project, so always run `./gradlew`.",
        "Every run has three phases; build scripts set up tasks, and only task actions do the work.",
        "Gradle skips a task whose inputs and outputs did not change (UP-TO-DATE) or copies its outputs from the build cache (FROM-CACHE).",
        "Default to `implementation`; use `api` only for types that appear in your public functions.",
        "A version conflict resolves to the highest version, and `dependencyInsight` tells you why.",
        "A version catalog names versions in one file; a BOM moves a family of libraries together.",
        "Convention plugins in a `build-logic` included build replace copied build logic.",
        "In GitHub Actions, setup-java plus setup-gradle give you wrapper validation and caching; `cache-provider: basic` keeps it fully open source.",
        "Ship JVM apps on a JRE image with the `installDist` output, a non-root user and `MaxRAMPercentage`.",
    ],
    "flashcards": [
        {"front": "Which four files make up the Gradle Wrapper?", "back": "gradlew, gradlew.bat, gradle/wrapper/gradle-wrapper.jar and gradle/wrapper/gradle-wrapper.properties. Commit all four."},
        {"front": "Name Gradle's three build phases in order.", "back": "Initialization (settings), configuration (build scripts and task graph), execution (task actions)."},
        {"front": "Which part of a registered task runs at execution time?", "back": "Only the doLast (or doFirst) actions. The rest of the register block runs during configuration."},
        {"front": "What does UP-TO-DATE mean on a task line?", "back": "Gradle compared the task's inputs and outputs with the last run, found no change, and skipped it."},
        {"front": "What does FROM-CACHE mean on a task line?", "back": "The task's inputs matched a build cache entry, so Gradle copied the outputs in instead of running it."},
        {"front": "Which two tasks does `build` run?", "back": "assemble (makes the outputs) and check (runs the tests and other checks)."},
        {"front": "implementation or api: which reaches the compile classpath of consumers?", "back": "api. implementation stays private at compile time and only reaches consumers at runtime."},
        {"front": "How does Gradle resolve a version conflict by default?", "back": "It picks the highest requested version for the whole graph."},
        {"front": "Which command explains why a library has a certain version?", "back": "./gradlew :app:dependencyInsight --dependency <name> --configuration runtimeClasspath"},
        {"front": "Where does the version catalog live, and how do scripts use it?", "back": "gradle/libs.versions.toml; build scripts refer to entries as libs.<name> and libs.plugins.<name>."},
        {"front": "What does platform(...) add to a build?", "back": "A BOM: recommended versions for a family of libraries, so they move together."},
        {"front": "Where should setup shared by many projects live?", "back": "In a convention plugin inside a build-logic included build, applied by id."},
        {"front": "Configuration cache or build cache: which stores the task graph?", "back": "The configuration cache. The build cache stores task outputs."},
        {"front": "How do you see which JDKs Gradle can compile with?", "back": "./gradlew -q javaToolchains. The build's jvmToolchain(21) picks one, not the java in your terminal."},
        {"front": "In GitHub Actions, which action should own Gradle caching?", "back": "gradle/actions/setup-gradle. Do not also use setup-java's cache: gradle or actions/cache on ~/.gradle."},
        {"front": "How do you keep setup-gradle v6 caching fully open source?", "back": "Set cache-provider: basic, the MIT-licensed provider built on actions/cache."},
        {"front": "What is the JVM's default maximum heap inside a container?", "back": "25% of the container's memory limit. Raise it with -XX:MaxRAMPercentage."},
        {"front": "Which task produces bin/ and lib/ for a container image?", "back": "installDist from the application plugin, in app/build/install/app."},
        {"front": "Why does Jib 3.5.4 need --no-configuration-cache?", "back": "Its task reads project at execution time, which the configuration cache does not allow."},
        {"front": "Dependency locking or verification: which checks file checksums?", "back": "Verification (gradle/verification-metadata.xml). Locking pins which versions resolve (gradle.lockfile)."},
    ],
    "resources": [
        {"title": "Gradle User Manual", "url": "https://docs.gradle.org", "kind": "docs", "why": "The official reference; start from the lifecycle, dependency and caching chapters linked in the lessons."},
        {"title": "What's new in Gradle 9", "url": "https://gradle.org/whats-new/gradle-9/", "kind": "read", "why": "What changed in the Gradle 9 line, so you can spot advice in older tutorials that no longer works."},
        {"title": "Gradle docs: Best practices for performance", "url": "https://docs.gradle.org/current/userguide/best_practices_performance.html", "kind": "docs", "why": "Gradle's own checklist for fast builds, written for current versions."},
        {"title": "DPE University: free Gradle courses", "url": "https://blog.gradle.org/dpe-university-and-gradle-courses", "kind": "read", "why": "Gradle's free self-paced courses, if you want structured exercises after this part."},
        {"title": "Gradle course for beginners (Tom Gregory)", "url": "https://www.youtube.com/watch?v=R6Z-Sxb837I", "kind": "watch", "why": "An hour-long beginner course that builds a project step by step; check details against Gradle 9."},
        {"title": "Understanding Gradle video series (Jendrik Johannes)", "url": "https://www.youtube.com/@jjohannes", "kind": "watch", "why": "Short videos by a former Gradle engineer on one concept each: settings, plugins, catalogs, caching."},
        {"title": "setup-gradle documentation (gradle/actions)", "url": "https://github.com/gradle/actions/blob/main/docs/setup-gradle.md", "kind": "docs", "why": "Every option of the CI action: cache providers, read-only branches, encryption keys and Build Scans."},
        {"title": "Kotlin docs: Configure a Gradle project", "url": "https://kotlinlang.org/docs/gradle-configure-project.html", "kind": "docs", "why": "The Kotlin side of the build: toolchains, compatible Gradle versions and plugin setup."},
        {"title": "Jib Gradle plugin README", "url": "https://github.com/GoogleContainerTools/jib/tree/master/jib-gradle-plugin", "kind": "docs", "why": "All Jib settings, including base images, platforms and pushing without Docker."},
        {"title": "JVMs in containers: best practices (David Delabassee)", "url": "https://www.youtube.com/watch?v=QCpMoQsZTa0", "kind": "watch", "why": "A talk on how the JVM sees container limits and which flags matter."},
        {"title": "Now in Android: build-logic README", "url": "https://github.com/android/nowinandroid/blob/main/build-logic/README.md", "kind": "read", "why": "A real, well-known project that uses convention plugins the way Day 23 does."},
    ],
    "quiz": [
        {
            "q": "Which command should a CI job use to build a Gradle project?",
            "options": ["`gradle build`", "`./gradlew build`", "`mvn package`", "`./gradlew build --rerun-tasks`"],
            "answer": 1,
            "why": "The wrapper runs the Gradle version the project pins, so CI matches every laptop; rerunning all tasks only wastes time.",
        },
        {
            "q": "A task is `tasks.register(\"count\") { val n = fileTree(\"src\").files.size; doLast { println(n) } }`. When does Gradle count the files?",
            "options": [
                "Only when the doLast action runs",
                "Every time any Gradle task runs",
                "When the task is configured, before execution",
                "Only the first time the wrapper runs",
            ],
            "answer": 2,
            "why": "Everything in the register block outside doLast runs while Gradle configures the task, which happens before execution.",
        },
        {
            "q": "You fix a typo inside a function body in library `core`. `app` depends on `core`. Which task is most likely UP-TO-DATE on the next build?",
            "options": ["`:app:compileKotlin`", "`:core:compileKotlin`", "`:core:jar`", "`:app:test`"],
            "answer": 0,
            "why": "core's public API did not change, so compile avoidance skips recompiling app, while core itself and app's tests still run.",
        },
        {
            "q": "`./gradlew :app:dependencies` shows `guava:31.0-jre -> 33.2.1-jre`, but app's build file says 31.0-jre. Why?",
            "options": [
                "Gradle always fetches the newest release",
                "The catalog silently overrides build files",
                "31.0-jre was removed from Maven Central",
                "Another dependency needs 33.2.1-jre, and highest wins",
            ],
            "answer": 3,
            "why": "Two paths requested different versions, and Gradle's default conflict resolution picks the highest.",
        },
        {
            "q": "You want to upgrade Kotlin for every project in hello-jvm with one edit. Which file do you change?",
            "options": ["`gradle.properties`", "`gradle/libs.versions.toml`", "`gradle-wrapper.properties`", "`app/build.gradle.kts`"],
            "answer": 1,
            "why": "The catalog's kotlin version feeds the Kotlin Gradle plugin that the convention plugin applies to every project.",
        },
        {
            "q": "A Dockerfile does `COPY . .` and then `RUN ./gradlew installDist`. Every code change downloads Gradle again. What is the best fix?",
            "options": [
                "Add `--no-daemon` to the RUN line",
                "Switch the build stage to a JRE image",
                "Copy and run the wrapper in an earlier layer",
                "Delete the .dockerignore file",
            ],
            "answer": 2,
            "why": "A layer that only depends on the wrapper files stays cached across code changes, so Gradle is downloaded once.",
        },
        {
            "q": "Your pull request builds never save anything to setup-gradle's cache. Why?",
            "options": [
                "By default only the default branch writes the cache",
                "Pull requests cannot use the Actions cache at all",
                "Caching only works with `cache-provider: basic`",
                "Gradle turns caching off when a test fails",
            ],
            "answer": 0,
            "why": "setup-gradle writes the cache from the default branch and only reads it elsewhere, which fits GitHub's cache scoping rules.",
        },
        {
            "q": "You set `-XX:MaxRAMPercentage=100` in a container with a 2 GB limit. What is the risk?",
            "options": [
                "The JVM refuses to start with that value",
                "The heap can never grow past 512 MB",
                "Docker ignores JVM flags in containers",
                "Total memory passes 2 GB and it gets killed",
            ],
            "answer": 3,
            "why": "Threads, class metadata and the JIT use memory outside the heap, so a heap as large as the limit pushes the process over it.",
        },
        {
            "q": "hello-jvm's Dockerfile ends with `ENTRYPOINT [\"/app/bin/app\"]`, and the start script ends with `exec java ...`. Why does `docker stop` finish in under a second?",
            "options": [
                "The JRE image ships a faster kernel",
                "Java becomes PID 1 and receives SIGTERM",
                "Docker sends SIGKILL to Java at once",
                "The healthcheck stops the app first",
            ],
            "answer": 1,
            "why": "Exec form plus exec in the script leaves java as process 1, so it gets the SIGTERM, runs its shutdown hook and exits with code 143.",
            "from": "Part 3",
        },
        {
            "q": "In jvm-ci.yml the `image` job has `needs: build`. What does that do?",
            "options": [
                "image starts only after build succeeds",
                "Both jobs start at the same time",
                "image runs on the same runner as build",
                "build is skipped when image fails",
            ],
            "answer": 0,
            "why": "needs makes a job wait for the listed jobs and skips it if they fail, so no image is built from code that failed its tests.",
            "from": "Part 4",
        },
    ],
}

out = pathlib.Path("/home/user/devops-from-zero/content/p5.json")
out.write_text(json.dumps(PART, indent=1, ensure_ascii=False) + "\n")
print("wrote", out)
