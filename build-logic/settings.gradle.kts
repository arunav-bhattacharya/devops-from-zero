// build-logic is a small, separate Gradle build that holds our convention plugins.

dependencyResolutionManagement {
    repositories {
        // Plugins and their dependencies come from the Gradle Plugin Portal.
        gradlePluginPortal()
    }
    versionCatalogs {
        // Reuse the main build's version catalog, so versions live in one file.
        create("libs") {
            from(files("../gradle/libs.versions.toml"))
        }
    }
}

rootProject.name = "build-logic"
