package hello.app

import com.sun.net.httpserver.HttpExchange
import com.sun.net.httpserver.HttpServer
import hello.greeting.Greeting
import hello.greeting.jsonObject
import java.net.InetAddress
import java.net.InetSocketAddress
import java.util.concurrent.Executors
import java.util.concurrent.atomic.AtomicLong

/** Settings come from environment variables, so the same image runs anywhere. */
data class Settings(
    val version: String = System.getenv("APP_VERSION") ?: "dev",
    val greeting: String = System.getenv("GREETING") ?: "Hello, JVM!",
    val port: Int = System.getenv("PORT")?.toIntOrNull() ?: 8080,
)

/** Starts the web server and returns it. Port 0 means "any free port" (the tests use that). */
fun startServer(settings: Settings, port: Int = settings.port): HttpServer {
    val visits = AtomicLong()
    val host = InetAddress.getLocalHost().hostName // which container or pod answered

    val server = HttpServer.create(InetSocketAddress(port), 0)
    server.createContext("/") { exchange ->
        // "/" matches every path, so answer 404 for anything that is not exactly "/".
        if (exchange.requestURI.path != "/") {
            exchange.sendJson(404, jsonObject("error" to "not found"))
        } else {
            val reply = Greeting(settings.greeting, settings.version, host, visits.incrementAndGet())
            exchange.sendJson(200, reply.toJson())
        }
    }
    server.createContext("/healthz") { exchange ->
        // Liveness: the process is up and can answer.
        exchange.sendJson(200, jsonObject("status" to "ok"))
    }
    // One cheap virtual thread per request (Java 21).
    server.executor = Executors.newVirtualThreadPerTaskExecutor()
    server.start()
    return server
}

private fun HttpExchange.sendJson(status: Int, body: String) {
    val bytes = body.toByteArray()
    responseHeaders.add("Content-Type", "application/json")
    sendResponseHeaders(status, bytes.size.toLong())
    responseBody.use { it.write(bytes) }
}

fun main() {
    val settings = Settings()
    val server = startServer(settings)
    // docker stop sends SIGTERM. The JVM then runs this hook and stops the server cleanly.
    Runtime.getRuntime().addShutdownHook(Thread { server.stop(1) })
    println("hello-jvm ${settings.version} listening on port ${server.address.port}")
}
