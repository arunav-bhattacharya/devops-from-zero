// Convention plugin "hello.kotlin-jvm": the setup every Kotlin project in hello-jvm shares.
// A project applies it with: plugins { id("hello.kotlin-jvm") }

plugins {
    id("org.jetbrains.kotlin.jvm")
}

// Compile and test with JDK 21, whatever JDK runs Gradle itself.
kotlin {
    jvmToolchain(21)
}

// Read the junit-bom entry from gradle/libs.versions.toml.
val libs = versionCatalogs.named("libs")

dependencies {
    // kotlin.test assertions, run by JUnit.
    testImplementation(kotlin("test"))
    // The BOM moves every JUnit module to the version in the catalog.
    testImplementation(platform(libs.findLibrary("junit-bom").get()))
}

tasks.test {
    // Run tests on the JUnit Platform.
    useJUnitPlatform()
}
