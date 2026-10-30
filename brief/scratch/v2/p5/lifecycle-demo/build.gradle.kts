println("2. configuration: running build.gradle.kts")

tasks.register("hello") {
    println("2b. configuration: setting up the hello task")
    doLast { println("3. execution: hello runs its action") }
}

tasks.register("bad") {
    doLast { println("version is ${project.version}") } // reads the project while running
}

tasks.register("good") {
    val v = project.version.toString() // read during configuration instead
    doLast { println("version is $v") }
}
