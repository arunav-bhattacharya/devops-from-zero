plugins {
    // Turns every *.gradle.kts file in src/main/kotlin into a plugin.
    `kotlin-dsl`
}

dependencies {
    // The convention plugin applies the Kotlin plugin, so it needs it on its classpath.
    implementation(libs.kotlin.gradle.plugin)
}
