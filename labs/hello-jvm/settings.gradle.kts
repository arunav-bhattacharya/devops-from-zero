// settings.gradle.kts: read first, during the initialization phase.
// It names the build and lists which projects take part.

pluginManagement {
    // Our own convention plugins live in the build-logic folder (an included build).
    includeBuild("build-logic")
}

plugins {
    // Lets Gradle download a matching JDK when none is installed (used by toolchains).
    id("org.gradle.toolchains.foojay-resolver-convention") version "1.0.0"
}

rootProject.name = "hello-jvm"

dependencyResolutionManagement {
    // One place for repositories. A project that adds its own fails the build.
    repositoriesMode = RepositoriesMode.FAIL_ON_PROJECT_REPOS
    repositories {
        mavenCentral()
    }
}

include("app", "greeting")
