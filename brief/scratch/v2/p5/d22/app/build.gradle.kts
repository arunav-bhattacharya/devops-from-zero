// app/build.gradle.kts: the build script for the app project.
plugins {
    // Compiles Kotlin for the JVM. Also adds the java plugin's tasks (jar, test, build).
    kotlin("jvm") version "2.4.21"
    // Adds run, installDist and start scripts for a program with a main().
    application
}

kotlin {
    // Compile and test with JDK 21, whatever JDK runs Gradle itself.
    jvmToolchain(21)
}

dependencies {
    // kotlin.test assertions, run by JUnit.
    testImplementation(kotlin("test"))
}

application {
    // The class Kotlin generates for the top-level main() in Main.kt.
    mainClass = "hello.app.MainKt"
}

tasks.test {
    // Run tests on the JUnit Platform.
    useJUnitPlatform()
}
