#!/usr/bin/env python3
"""Human-writing pass (v3, blog mode) for Part 5 (Gradle) and Part 8 (Argo CD).

Loads the current content/p5.json and content/p8.json, replaces prose only, and writes them back.
Each edit is (path, old, new). `old` must occur exactly once in that field; old=None replaces the
whole field. Paths: "part/intro", "part/quiz/6/why", "d22/sections/3/body", "d22/analogy",
"d22/worked/steps/5/say", "d22/task/steps/1", "d22/interview/0/a", "d22/deeper/body", ...
"""
import json
import pathlib
import sys

ROOT = pathlib.Path("/home/user/devops-from-zero")

P5 = []
P8 = []


def e(lst, path, old, new):
    lst.append((path, old, new))


# ---------------------------------------------------------------- Part 5: part level
e(P5, "part/intro", None,
  "You use Gradle every day through IntelliJ. In DevOps work the builds run where there is no IDE: "
  "on CI runners and inside Docker builds. There you have to know what Gradle is doing without "
  "IntelliJ's help. This part explains Gradle's model step by step with a new lab, hello-jvm: a small "
  "Kotlin web service that mirrors hello-devops. It comes after Docker and GitHub Actions because "
  "Day 24 uses both to cache the build and ship the service as an image.")

e(P5, "part/quiz/6/why", None,
  "By default setup-gradle saves the cache only on the default branch and just reads it on other "
  "branches. That choice fits how GitHub scopes caches between branches.")

# ---------------------------------------------------------------- d22
e(P5, "d22/sections/0/body",
  "you already use it every day through IntelliJ. This lesson opens the box. In DevOps work you run "
  "builds where there is no IDE: on CI runners, in Docker build stages and in release jobs. There you "
  "need to know what Gradle is doing and why.",
  "you already use it every day through IntelliJ. In DevOps work the build runs where there is no IDE: "
  "on CI runners, in Docker build stages and in release jobs. When a build fails there, the log is all "
  "you get, so you need your own picture of what Gradle is doing and why.")

e(P5, "d22/sections/1/body",
  "Declaring inputs and outputs pays off on the second run.",
  "Declaring inputs and outputs is what makes the second run fast.")

e(P5, "d22/sections/3/body",
  "This is the idea that trips up most people, so take it slowly. Every Gradle run goes through three "
  "phases, in this order:",
  "Every Gradle run goes through three phases, in this order:")
e(P5, "d22/sections/3/body",
  "Here is the trap. A build script does not do the work; it describes the work. Code at the top level",
  "Take this part slowly, because a build script looks like a program that does the build. It only "
  "describes the work. Code at the top level")
e(P5, "d22/sections/3/body",
  "Still, keep slow work out of configuration. No network calls, no big file reads, no running programs "
  "at the top level. Configuration happens on every run that is not cached, even `./gradlew help`.",
  "Top-level code is not lazy. It runs every time Gradle configures the build, which is every run that "
  "is not cached, even `./gradlew help`. So keep network calls, big file reads and calls to other "
  "programs out of it.")
# factual: the configuration cache is older than Gradle 9 (9.0 made it the preferred mode and
# `gradle init` turns it on); "Gradle 9 adds the configuration cache" was wrong.
e(P5, "d22/sections/3/body",
  "Gradle 9 adds the configuration cache. It saves the result of phases 1 and 2, and the next run",
  "The configuration cache saves the result of phases 1 and 2. Gradle 9 calls it the preferred mode, "
  "and hello-jvm turns it on in `gradle.properties`. The next run")

e(P5, "d22/sections/4/body",
  "Think of it as a lockfile for the build tool.",
  "It does for Gradle what a lockfile does for libraries.")

e(P5, "d22/analogy",
  "Where it breaks: a cook judges by eye, while Gradle compares exact fingerprints of every input file, "
  "so one changed byte means the task runs again.",
  "A real cook decides that by eye. Gradle compares exact fingerprints of every input file, and one "
  "changed byte is enough to make the task run again.")

e(P5, "d22/worked/steps/5/say",
  "The fix: read the value during configuration and keep only the result.",
  "To fix it, read the value during configuration and keep only the result.")

e(P5, "d22/mistake", None,
  "`gradle build` runs whatever Gradle you installed last, while `./gradlew build` runs the version the "
  "project pins. Use the global one, and the build can pass for you and fail in CI, or the other way "
  "round. Always run `./gradlew`, and keep IntelliJ on the wrapper (its default). Use a global Gradle "
  "only to create the wrapper once.")

e(P5, "d22/real_world", None,
  "A payments ledger service with many Gradle projects runs `./gradlew build` in CI on every pull "
  "request. The wrapper pins Gradle, so laptops and runners agree, and a Gradle upgrade is an ordinary "
  "pull request that changes `gradle-wrapper.properties`. When CI gets slow, the team's first move is "
  "to read which tasks did work and which were UP-TO-DATE or FROM-CACHE.")

e(P5, "d22/task/steps/1",
  "You only need it for the next step but one.",
  "You need it for one thing only: creating the wrapper in step 4.")

# factual: with distributionSha256Sum set, an upgrade changes the URL and the checksum (two lines),
# and `./gradlew wrapper` can also refresh the scripts and the jar, so it is not a one-line change.
e(P5, "d22/interview/0/a",
  "I also set `distributionSha256Sum`, so a tampered download is refused, and upgrades become a "
  "reviewed one-line change.",
  "I also set `distributionSha256Sum`, so a tampered download is refused. An upgrade is then a small "
  "change that goes through review like any other.")

e(P5, "d22/deeper/body",
  "Gradle does not guess when it skips a task. Ask it why a task ran with `--info`. After adding a "
  "comment to `Main.kt`, `./gradlew :app:compileKotlin --info` printed:",
  "Gradle will tell you why a task ran if you add `--info`. After we added a comment to `Main.kt`, "
  "`./gradlew :app:compileKotlin --info` printed:")
e(P5, "d22/deeper/body",
  "This explains a few things you will see. A task with no declared outputs, like `hello` in the worked "
  "example, always runs.",
  "A task with no declared outputs, like `hello` in the worked example, always runs, because there is "
  "nothing to compare.")
e(P5, "d22/deeper/body",
  "One more habit worth building now: when a build surprises you, read the task lines before you read "
  "the error.",
  "When a build surprises you, read the task lines before you read the error.")

# ---------------------------------------------------------------- d23
e(P5, "d23/sections/4/body",
  "Here is why. `kotlin(\"test\")` pulls in `kotlin-test-junit5`, which asks for JUnit 5.10.1.",
  "It needs one because `kotlin(\"test\")` pulls in `kotlin-test-junit5`, which asks for JUnit 5.10.1.")

e(P5, "d23/analogy",
  "Where it breaks: a private member truly stays inside, but an `implementation` dependency still "
  "travels to consumers at runtime, on their runtime classpath.",
  "A Kotlin `private` really is private, though. An `implementation` dependency is hidden only while "
  "consumers compile; at runtime it still travels to them, on their runtime classpath.")

e(P5, "d23/worked/steps/0/say",
  "Plain coordinate strings are fine for an experiment; for keeps they go in the catalog.",
  "Plain coordinate strings are fine for an experiment; in the real build they belong in the catalog.")

e(P5, "d23/mistake",
  "Trusting the version in your build file. With highest-wins,",
  "Do not trust the version in your build file. With highest-wins,")

e(P5, "d23/real_world", None,
  "A security scan at a payments company flagged an old JSON library that no build file mentioned. "
  "`dependencyInsight` showed that it came in through a client SDK. The team added the fixed version to "
  "the catalog and declared it in the affected project, and highest-wins lifted every path to it.")

e(P5, "d23/deeper/body",
  "Day 24 adds two more tools on top of all this. Dependency locking records the exact result of "
  "resolution in a file. Dependency verification checks the bytes of every downloaded jar.",
  "Day 24 adds two more tools. Dependency locking records the exact result of resolution in a file, "
  "and dependency verification checks the bytes of every downloaded jar.")

# ---------------------------------------------------------------- d24
e(P5, "d24/sections/0/body",
  "A slow build costs you on every run, on your laptop and on every CI job. Gradle's answer is to avoid "
  "repeating work, and it has four separate tricks. Keep them apart in your head:",
  "Gradle has four separate ways to avoid repeating work. They are easy to mix up, so keep them apart:")

e(P5, "d24/sections/2/body",
  "the classic fix when builds act strangely after a JDK change",
  "the usual fix when builds act strangely after a JDK change")

e(P5, "d24/sections/3/body",
  "Speed is half the job. The other half is knowing exactly what went into a build.",
  "Speed aside, you want to know exactly what went into a build.")

e(P5, "d24/sections/4/body",
  "Three things to know about that cache:",
  "That cache has rules of its own:")

e(P5, "d24/sections/5/body",
  "The image needs a JRE and your jars, nothing more. The JDK, Gradle and the Kotlin compiler are build "
  "tools. That is the multi-stage pattern",
  "The image you ship needs a JRE and your jars. The JDK, Gradle and the Kotlin compiler are only needed "
  "to build, so they stay in an earlier stage. That is the multi-stage pattern")
e(P5, "d24/sections/5/body",
  "Two more things. The cache mount lives in your local builder",
  "The cache mount lives in your local builder")
e(P5, "d24/sections/5/body",
  "And on an Apple Silicon Mac, `docker build` makes an arm64 image.",
  "On an Apple Silicon Mac, `docker build` makes an arm64 image.")

e(P5, "d24/analogy", None,
  "At a coat check you hand over your coat and get a ticket. The build cache does the same with task "
  "outputs. When a task finishes, Gradle hangs its outputs on a hook and keeps the ticket: a fingerprint "
  "of everything that went in. When the same ticket comes up again, in any folder or on any machine that "
  "shares the cloakroom, Gradle hands the coat back and the task does not run. A real coat check only "
  "ever gives you your own coat. The build cache will happily give you outputs that a different build "
  "made, and that is safe only because the ticket covers every input.")

e(P5, "d24/mistake", None,
  "Writing `./gradlew clean build` in CI to be safe slows it down, and so does adding `actions/cache` "
  "next to setup-gradle. On a fresh runner `clean` has nothing to delete, and on a reused machine it "
  "throws away outputs Gradle could have skipped. Two caching systems on one folder also conflict with "
  "each other. Run `./gradlew build` and let setup-gradle do the caching. If you distrust a cache hit, "
  "the real fix is a task input that is missing from the build logic.")

e(P5, "d24/real_world", None,
  "On a big team, a fresh clone of main should not have to compile everything again. At Paylane, a "
  "made-up payments company, CI on main writes to a remote build cache and laptops only read from it. "
  "A fresh clone there is mostly FROM-CACHE. Every service image uses the same two-stage Dockerfile with "
  "`MaxRAMPercentage` set, and the team tunes memory limits with a load test instead of guessing.")

# ---------------------------------------------------------------- Part 8: part level
e(P8, "part/intro", None,
  "In Part 7 you deployed hello-devops to Kubernetes by typing kubectl commands. In this part Argo CD "
  "takes over the deploying: git holds the desired state, and a controller in the cluster keeps the "
  "cluster equal to it. On Day 39 you install it and watch it undo drift and roll back a bad release. "
  "Day 40 runs the app as dev and prod, promotes a version by pull request, and covers how teams handle "
  "image updates, secrets and access.")

# ---------------------------------------------------------------- d39
e(P8, "d39/sections/1/body",
  "The price is one more system to install, upgrade and learn. On your laptop that means seven extra Pods.",
  "The price is one more system that you have to learn and keep upgraded. On your laptop it is seven "
  "extra Pods.")

e(P8, "d39/sections/3/body",
  "The browser warns about the certificate, because the install makes a self-signed one. That is "
  "expected here.",
  "Expect a certificate warning in the browser, because the install makes a self-signed one.")

e(P8, "d39/sections/5/body",
  "This part trips most people up: Argo CD is not the only controller that changes your objects.",
  "Self-heal gets tricky because Argo CD is not the only controller that changes your objects.")

e(P8, "d39/analogy",
  "Where it breaks: a real person would ask why a customer moved something, while Argo CD just puts it "
  "back, even when the plan itself is wrong.",
  "A real staff member would ask why a customer moved something. Argo CD never asks: it puts things "
  "back, even when the plan itself is wrong.")

e(P8, "d39/mistake",
  "Fixing something in the cluster by hand and expecting the fix to stay. With self-heal on,",
  "A fix made by hand in the cluster will not last. With self-heal on,")

e(P8, "d39/real_world", None,
  "A release breaks at night. With one config repo and a folder per environment, the on-call engineer "
  "reverts the pull request that changed the prod folder, and Argo CD rolls the cluster back. Every "
  "deploy in that setup is a merged pull request, so the review is the approval, and git records who "
  "did what, and why.")

# ---------------------------------------------------------------- d40
e(P8, "d40/sections/0/body",
  "So far hello-devops keeps everything in one repo:",
  "Right now hello-devops keeps everything in one repo:")
e(P8, "d40/sections/0/body",
  "Its reasons, in short:",
  "It gives these reasons:")

e(P8, "d40/sections/1/body",
  "An environment is one running copy of the app with one purpose. Dev is where new versions land "
  "first, and prod is what users see.",
  "Dev is where new versions land first, and prod is what users see. Each one is an environment: a "
  "running copy of the app with one purpose.")

e(P8, "d40/sections/2/body",
  "**Promotion** means moving a version that passed in one environment on to the next. In GitOps it is "
  "a small change to text in git:",
  "Moving a version that passed in one environment on to the next is called **promotion**. In GitOps "
  "it is a small text change in git:")

e(P8, "d40/sections/4/body",
  "Argo CD applies everything in one sync, in a sensible default order:",
  "Within one sync, Argo CD already applies objects in a sensible order:")

e(P8, "d40/sections/5/body",
  "Three common ways out:",
  "Three tools solve this:")

e(P8, "d40/analogy", None,
  "A book on its way to print goes from the editor to the proofreader to the printer, and each "
  "hand-over needs a signature. Nobody retypes the book at each step, so the printer prints exactly what "
  "the proofreader approved. Promotion moves an image tag through dev and prod the same way. "
  "Environments are not perfect copies, though. Prod gets more replicas than dev, while every printed "
  "copy of a book is meant to be the same.")

e(P8, "d40/worked/steps/1/say", None,
  "Try `kustomize edit set image` first. It sets the tag, but look at the size of the change. It "
  "rewrote the whole file: comments at line ends are gone and lists are re-indented. A reviewer would "
  "have to hunt for the one line that matters, so throw that edit away.")

e(P8, "d40/real_world", None,
  "With dev, staging and prod clusters, a payments team can run everything from one config repo: one "
  "ApplicationSet per app, using the cluster generator. CI opens the dev pull request after every "
  "release and merges it once checks pass. Prod needs a second pull request, approved by someone on the "
  "on-call rotation, and a PostSync smoke test fails the sync if checkout stops answering.")


# ---------------------------------------------------------------- apply
def resolve(doc, path):
    parts = path.split("/")
    if parts[0] == "part":
        obj, rest = doc, parts[1:]
    else:
        obj = next(L for L in doc["lessons"] if L["id"] == parts[0])
        rest = parts[1:]
    for p in rest[:-1]:
        obj = obj[int(p)] if isinstance(obj, list) else obj[p]
    last = rest[-1]
    return obj, (int(last) if isinstance(obj, list) else last)


def apply(fname, edits):
    path = ROOT / "content" / fname
    doc = json.loads(path.read_text())
    for p, old, new in edits:
        obj, key = resolve(doc, p)
        cur = obj[key]
        if old is None:
            obj[key] = new
        else:
            n = cur.count(old)
            if n != 1:
                sys.exit(f"{fname} {p}: old text found {n} times: {old[:60]!r}")
            obj[key] = cur.replace(old, new)
    with open(path, "w") as f:
        json.dump(doc, f, ensure_ascii=False, indent=1)
        f.write("\n")
    print(f"{fname}: {len(edits)} edits applied")


if __name__ == "__main__":
    apply("p5.json", P5)
    apply("p8.json", P8)
