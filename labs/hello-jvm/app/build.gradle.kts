// app: the runnable web service.
plugins {
    id("hello.kotlin-jvm")
    application
}

dependencies {
    // Use the greeting library from this same build.
    implementation(project(":greeting"))
}

application {
    // The class Kotlin generates for the top-level main() in Main.kt.
    mainClass = "hello.app.MainKt"
}
