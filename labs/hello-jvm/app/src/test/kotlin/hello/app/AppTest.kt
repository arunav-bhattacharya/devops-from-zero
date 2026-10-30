package hello.app

import java.net.URI
import java.net.http.HttpClient
import java.net.http.HttpRequest
import java.net.http.HttpResponse
import kotlin.test.AfterTest
import kotlin.test.Test
import kotlin.test.assertContains
import kotlin.test.assertEquals

class AppTest {
    // Start a real server on a free port for each test.
    private val server = startServer(Settings(version = "test", greeting = "Hi"), port = 0)
    private val client = HttpClient.newHttpClient()

    @AfterTest
    fun stop() = server.stop(0)

    private fun get(path: String): HttpResponse<String> {
        val uri = URI("http://localhost:${server.address.port}$path")
        return client.send(HttpRequest.newBuilder(uri).build(), HttpResponse.BodyHandlers.ofString())
    }

    @Test
    fun rootSaysHelloAndCountsVisits() {
        assertContains(get("/").body(), "\"visits\":1")
        val second = get("/")
        assertEquals(200, second.statusCode())
        assertContains(second.body(), "\"message\":\"Hi\"")
        assertContains(second.body(), "\"visits\":2")
    }

    @Test
    fun healthzIsOk() {
        val response = get("/healthz")
        assertEquals(200, response.statusCode())
        assertEquals("""{"status":"ok"}""", response.body())
    }

    @Test
    fun unknownPathIs404() {
        assertEquals(404, get("/nope").statusCode())
    }
}
