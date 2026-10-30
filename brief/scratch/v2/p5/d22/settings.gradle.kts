// settings.gradle.kts: read first. It names the build and lists its projects.

plugins {
    // Lets Gradle download a matching JDK when none is installed (used by toolchains).
    id("org.gradle.toolchains.foojay-resolver-convention") version "1.0.0"
}

rootProject.name = "hello-jvm"

dependencyResolutionManagement {
    // Every project gets its libraries from Maven Central.
    repositories {
        mavenCentral()
    }
}

include("app")
