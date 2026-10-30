println("2. configuration: running build.gradle.kts")

tasks.register("hello") {
    group = "demo"
    description = "Prints a greeting"
    println("2b. configuration: setting up the hello task")
    doLast {
        println("3. execution: hello runs its action")
    }
}

tasks.register("bad") {
    doLast {
        println("version is ${project.version}") // reads the project while the task runs
    }
}

tasks.register("good") {
    val version = project.version.toString() // read the project now, at configuration time
    doLast {
        println("version is $version") // use only the captured value at execution time
    }
}
