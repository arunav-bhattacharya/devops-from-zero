package hello.app

import com.sun.net.httpserver.HttpExchange
import com.sun.net.httpserver.HttpServer
import java.net.InetAddress
import java.net.InetSocketAddress
import java.util.concurrent.atomic.AtomicLong

/** The JSON for GET /. A plain function, so a test can call it without a server. */
fun reply(message: String, version: String, host: String, visits: Long): String =
    """{"message":"$message","version":"$version","host":"$host","visits":$visits}"""

fun main() {
    // Settings come from environment variables, with defaults for your laptop.
    val version = System.getenv("APP_VERSION") ?: "dev"
    val message = System.getenv("GREETING") ?: "Hello, JVM!"
    val port = System.getenv("PORT")?.toIntOrNull() ?: 8080
    val host = InetAddress.getLocalHost().hostName
    val visits = AtomicLong()

    // The JDK's built-in web server: no framework, no extra downloads.
    val server = HttpServer.create(InetSocketAddress(port), 0)
    server.createContext("/") { it.sendJson(reply(message, version, host, visits.incrementAndGet())) }
    server.createContext("/healthz") { it.sendJson("""{"status":"ok"}""") }
    server.start()
    println("hello-jvm $version listening on port $port")
}

private fun HttpExchange.sendJson(body: String) {
    val bytes = body.toByteArray()
    responseHeaders.add("Content-Type", "application/json")
    sendResponseHeaders(200, bytes.size.toLong())
    responseBody.use { it.write(bytes) }
}
