"""Book-voice rewrite of the part fields of p6 and p7 (fifth pass, writer td). Options and answers stay."""
import json
from common import ROOT, save, set_list

# ---------- Part 6 ----------
path6 = ROOT / "content/p6.json"
P = json.loads(path6.read_text())  # load fresh right before writing

P["intro"] = ("Until now you ran every check and build for hello-devops yourself, which works until the busy day you forget. "
              "In this part GitHub runs them for you, like a taster who tries every dish before it leaves the kitchen. "
              "Every pull request gets linted, tested and built, a red one cannot merge, and a version tag publishes the image. "
              "Part 5 left you with a tested app and a production-ready image, which is all a pipeline needs to start.")

P["recap"] = [
    "Change code on small, short-lived branches, and merge through pull requests that a reviewer and CI both check.",
    "CI tests every change. With continuous delivery a person picks the release moment; with continuous deployment nobody does.",
    "A workflow is a YAML file in .github/workflows: an event starts it, and each job runs its steps on a fresh runner.",
    "The lab's ci.yml lints, tests on Python 3.13 and 3.14, keeps a JUnit report, builds the image and smoke-tests it.",
    "Caches make repeat runs fast but can vanish; artifacts are the files a run keeps, and need unique names.",
    "A ruleset on main with every required check stops red pull requests from merging.",
    "GitHub fills in expressions before the shell runs; every if gets a hidden success() unless you write a status function.",
    "Step outputs, job outputs and needs carry values between steps and jobs; composite actions and reusable workflows remove repetition.",
    "release.yml turns a v* tag into one amd64 and arm64 image in GHCR, after a person approves, with a token that can do only what it must.",
    "Pin third-party actions to commit SHAs, let Dependabot move the pins, and keep pull request code away from pull_request_target.",
]

set_list(P["flashcards"], "front", [
    "Continuous delivery or continuous deployment: in which one does a person click release?",
    "What does 'build once, deploy many' mean?",
    "What does a CODEOWNERS file do by itself, and what makes an owner's review required?",
    "In the version 2.4.1, which number changes for a compatible bug fix?",
    "Where must workflow files live?",
    "Which runner label gives you arm64 Linux, the same processor family as an Apple Silicon Mac?",
    "What do standard GitHub-hosted runners cost in a public repository?",
    "What does needs: [lint, test] do on a job?",
    "Why not require only the last job of a needs chain?",
    "Why put paths-ignore on push but not on pull_request?",
    "What goes into the setup-python pip cache key?",
    "Cache or artifact: which one is a run's output that people download?",
    "When does GitHub work out ${{ }} expressions?",
    "What hidden condition does every if get?",
    "How does a value get from job A to job B?",
    "Composite action or reusable workflow: which one bundles whole jobs?",
    "What does permissions: contents: read at the top of a workflow do?",
    "Which permission lets a job ask for an OIDC token?",
    "Why pin an action to a full commit SHA?",
    "What is a pwn request?",
])
set_list(P["flashcards"], "back", [
    "Continuous delivery: every change is ready, and a person clicks release. With continuous deployment every passing change goes live on its own.",
    "Build the image one time, then move that same digest through every environment.",
    "By itself it only asks the owners of the changed paths to review. A ruleset with Require review from Code Owners makes their approval required.",
    "PATCH, so the next version is 2.4.2.",
    "In .github/workflows/ at the root of the repository, as .yml or .yaml files.",
    "ubuntu-24.04-arm (ubuntu-latest is x64).",
    "Nothing. Private repositories draw from a monthly allowance, $12 on the Free plan.",
    "The job waits for lint and test to succeed. If either fails, this job is skipped.",
    "If an earlier job fails, the last job is skipped, and GitHub counts a skipped check as passed.",
    "A required check skipped by a path filter stays Pending and blocks the merge.",
    "The system and processor, the Python version, and a hash of the requirements files.",
    "The artifact. A cache only speeds up future runs, and GitHub can remove it.",
    "Before the shell sees the script: GitHub's servers fill in job-level ones, and the runner fills in each step's just before it starts.",
    "success(), unless the if already uses a status function such as failure() or always().",
    "A step writes it to $GITHUB_OUTPUT, job A maps it in its outputs, and job B reads it as needs.A.outputs.name.",
    "The reusable workflow, called with on: workflow_call. A composite action is several steps used as one step.",
    "It makes the GITHUB_TOKEN read-only for code in every job, and sets every permission you don't list to none.",
    "id-token: write. It grants no other access.",
    "Whoever controls the action's repository can move a tag to other code. A full commit SHA always means the same code.",
    "A pull_request_target workflow that checks out and runs a pull request's code, so a stranger's code gets your secrets.",
])

Q = P["quiz"]
set_list(Q, "q", [
    "A colleague's branch has lived for three weeks and touches 40 files. What problem is most likely when it is merged?",
    "Which event lets you start a workflow with a button in the Actions tab?",
    "Why does the lab's ci.yml put the Python version in the artifact name?",
    "A pull request run on the branch `fix-typo` looks for a pip cache. Where can the cache it restores come from?",
    "In the lab's build job, the step `Show the app's logs` has `if: ${{ failure() && steps.smoke.outcome == 'failure' }}`. The image build fails, before the smoke test. Does the logs step run?",
    "You want three test jobs in hello-devops to share the same five setup steps. Which tool fits best?",
    "In release.yml, which permission lets the GITHUB_TOKEN push images to GHCR?",
    "Every production release must wait for a person to approve it. The repository is public, on the Free plan. What do you use?",
    "A CI step ends with `grep ERROR app.log`, and the log contains no errors. What happens to the step?",
    "You start hello-devops with `python app.py` and run `curl localhost:8000` in the same second. curl says 'Connection refused'; two seconds later it works. What did the first error tell you?",
])
set_list(Q, "why", [
    "Branches that live long and grow big drift away from main. Conflicts pile up, and reviewers can only skim.",
    "workflow_dispatch adds the Run workflow button, once the workflow file is on the default branch.",
    "Each matrix job uploads its own report, and two artifacts in one run cannot have the same name.",
    "Runs restore caches from their own scope and from the default (or base) branch. A cache saved by one pull request is not shared with others.",
    "failure() is true, but the smoke step never ran, so its outcome is skipped and the second half is false.",
    "Shared steps inside a job are what composite actions are for. A reusable workflow replaces whole jobs.",
    "GHCR is part of GitHub Packages, so the token needs packages: write to push there.",
    "Required reviewers on an environment pause the job until one of them approves.",
    "grep exits with 1 when it finds no match, and any non-zero exit code fails the step.",
    "Connection refused means the machine answered, but no program listened on the port yet. That is why the lab's smoke test retries for a few seconds.",
])

set_list(P["resources"], "why", [
    "Every topic in this part has a page here, from your first workflow to the security reference.",
    "The page you will open most: every key a workflow file can contain, with examples.",
    "A free, guided course that runs inside a real repository and checks your work as you go.",
    "A short guided course that builds and calls a reusable workflow step by step.",
    "Its branching chapters explain merge and rebase with clear pictures.",
    "The classic essay on what continuous integration really asks of a team, rewritten in 2023.",
    "A whole site on trunk-based development: short branches, feature flags and releasing from the main branch.",
    "A clear walk through workflows and a Docker build pipeline; the screens are from 2020, and the ideas still hold.",
    "Matrix, concurrency, timeouts, contexts and expressions, shown on real workflows.",
    "GitHub's own talk on the common security mistakes in workflows and how to avoid them.",
    "The checker that catches typos, bad expressions and unsafe use of untrusted text before you push.",
    "GitHub's checklist for secrets, tokens, third-party actions and untrusted input.",
])

save(path6, P)

# ---------- Part 7 ----------
path7 = ROOT / "content/p7.json"
P = json.loads(path7.read_text())  # load fresh right before writing

P["intro"] = ("Python runs straight from the text you write, but programs in Kotlin and Java must be compiled first, and a build tool does that work. "
              "This part explains Gradle, the build tool most Kotlin projects use, from the very beginning: what it plans, what it skips, and why. "
              "The lab is hello-jvm, a small Kotlin web service that does what hello-devops does. "
              "It comes after Docker and GitHub Actions, because Day 30 uses both to cache the build and ship the service as an image.")

P["recap"] = [
    "Kotlin is compiled for the JVM, and a build tool turns code and libraries into tested, packaged software the same way every time.",
    "The Gradle Wrapper pins one Gradle version per project, so always run `./gradlew`.",
    "Every run has three phases; build scripts set up tasks, and only task actions do the work.",
    "Gradle skips a task whose inputs and outputs did not change (UP-TO-DATE) or copies its outputs from the build cache (FROM-CACHE).",
    "Default to `implementation`; use `api` only for types that appear in your public functions.",
    "A version conflict resolves to the highest version, and `dependencyInsight` tells you why.",
    "A version catalog names versions in one file; a BOM moves a family of libraries together; convention plugins in `build-logic` replace copied setup.",
    "In GitHub Actions, setup-java plus setup-gradle give you wrapper checks and caching; `cache-provider: basic` keeps it fully open source.",
    "Ship JVM apps on a JRE image with the `installDist` output, a non-root user and `MaxRAMPercentage`.",
]

set_list(P["flashcards"], "front", [
    "Which four files make up the Gradle Wrapper?",
    "Name Gradle's three build phases in order.",
    "Which part of a registered task runs when the task executes?",
    "What does UP-TO-DATE mean on a task line?",
    "What does FROM-CACHE mean on a task line?",
    "Which two tasks does `build` run?",
    "implementation or api: which one reaches the compile classpath of projects that use yours?",
    "How does Gradle settle a version conflict by default?",
    "Which command explains why a library has a certain version?",
    "Where does the version catalog live, and how do build scripts use it?",
    "What does platform(...) add to a build?",
    "Where should setup shared by many projects live?",
    "Configuration cache or build cache: which one stores the task graph?",
    "How do you see which JDKs Gradle can compile with?",
    "In GitHub Actions, which action should own Gradle caching?",
    "How do you keep setup-gradle v6 caching fully open source?",
    "What is the JVM's default largest heap inside a container?",
    "Which task makes the bin/ and lib/ folders for a container image?",
    "Why does Jib 3.5.4 need --no-configuration-cache?",
    "Dependency locking or verification: which one checks file checksums?",
])
set_list(P["flashcards"], "back", [
    "gradlew, gradlew.bat, gradle/wrapper/gradle-wrapper.jar and gradle/wrapper/gradle-wrapper.properties. Commit all four.",
    "Initialization (settings), configuration (build scripts and task graph), execution (task actions).",
    "Only the doLast (or doFirst) actions. The rest of the register block runs during configuration.",
    "Gradle compared the task's inputs and outputs with the last run, found no change, and skipped it.",
    "The task's inputs matched a build cache entry, so Gradle copied the outputs in instead of running it.",
    "assemble (makes the outputs) and check (runs the tests and other checks).",
    "api. implementation stays private while others compile, and reaches them only at runtime.",
    "It picks the highest requested version for the whole graph.",
    "./gradlew :app:dependencyInsight --dependency <name> --configuration runtimeClasspath",
    "gradle/libs.versions.toml; build scripts use entries as libs.<name> and libs.plugins.<name>.",
    "A BOM: recommended versions for a family of libraries, so they move together.",
    "In a convention plugin inside a build-logic included build, applied by id.",
    "The configuration cache. The build cache stores task outputs.",
    "./gradlew -q javaToolchains. The build's jvmToolchain(21) picks one, not the java in your terminal.",
    "gradle/actions/setup-gradle. Do not also use setup-java's cache: gradle or actions/cache on ~/.gradle.",
    "Set cache-provider: basic, the MIT-licensed provider built on actions/cache.",
    "25% of the container's memory limit. Raise it with -XX:MaxRAMPercentage.",
    "installDist from the application plugin, in app/build/install/app.",
    "Its task reads project while it runs, which the configuration cache does not allow.",
    "Verification (gradle/verification-metadata.xml). Locking pins which versions resolve (gradle.lockfile).",
])

Q = P["quiz"]
set_list(Q, "q", [
    "Which command should a CI job use to build a Gradle project?",
    "A task is `tasks.register(\"count\") { val n = fileTree(\"src\").files.size; doLast { println(n) } }`. When does Gradle count the files?",
    "You fix a typo inside a function body in the library `core`, and `app` depends on `core`. Which task is most likely UP-TO-DATE on the next build?",
    "`./gradlew :app:dependencies` shows `guava:31.0-jre -> 33.2.1-jre`, but app's build file says 31.0-jre. Why?",
    "You want to upgrade Kotlin for every project in hello-jvm with one edit. Which file do you change?",
    "A Dockerfile does `COPY . .` and then `RUN ./gradlew installDist`. Every code change downloads Gradle again. What is the best fix?",
    "Your pull request builds never save anything to setup-gradle's cache. Why?",
    "You set `-XX:MaxRAMPercentage=100` in a container with a 2 GB limit. What is the risk?",
    "hello-jvm's Dockerfile ends with `ENTRYPOINT [\"/app/bin/app\"]`, and the start script ends with `exec java ...`. Why does `docker stop` finish in under a second?",
    "In jvm-ci.yml the `image` job has `needs: build`. What does that do?",
])
set_list(Q, "why", [
    "The wrapper runs the Gradle version the project pins, so CI matches every laptop; rerunning all tasks only wastes time.",
    "Everything in the register block outside doLast runs while Gradle configures the task, which happens before execution.",
    "core's public API did not change, so compile avoidance skips recompiling app, while core itself and app's tests still run.",
    "Two paths asked for different versions, and Gradle's default conflict resolution picks the highest.",
    "The catalog's kotlin version feeds the Kotlin Gradle plugin that the convention plugin applies to every project.",
    "A layer that depends only on the wrapper files stays cached across code changes, so Gradle is downloaded once.",
    "By default setup-gradle saves the cache only on the default branch and just reads it on other branches. That fits how GitHub shares caches between branches.",
    "Threads, class metadata and the JIT use memory outside the heap, so a heap as large as the limit pushes the process over it.",
    "Exec form plus exec in the script leaves java as process 1, so it gets the SIGTERM stop signal, runs its shutdown code and exits with code 143.",
    "needs makes a job wait for the listed jobs and skips it if they fail, so no image is built from code that failed its tests.",
])

set_list(P["resources"], "why", [
    "The official reference; start from the lifecycle, dependency and caching chapters linked in the lessons.",
    "What changed in the Gradle 9 line, so you can spot advice in older tutorials that no longer works.",
    "Gradle's own checklist for fast builds, written for current versions.",
    "Gradle's free self-paced courses, if you want structured exercises after this part.",
    "An hour-long beginner course that builds a project step by step; check the details against Gradle 9.",
    "Short videos by a former Gradle engineer, each on one idea: settings, plugins, catalogs, caching.",
    "Every option of the CI action: cache providers, read-only branches, encryption keys and Build Scans.",
    "The Kotlin side of the build: toolchains, matching Gradle versions and plugin setup.",
    "All Jib settings, including base images, platforms and pushing without Docker.",
    "A talk on how the JVM sees container memory limits and which flags matter.",
    "A real, well-known project that uses convention plugins the way Day 29 does.",
])

save(path7, P)
print("parts written")
