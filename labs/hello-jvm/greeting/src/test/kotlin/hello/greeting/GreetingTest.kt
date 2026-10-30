package hello.greeting

import kotlin.test.Test
import kotlin.test.assertEquals

class GreetingTest {
    @Test
    fun buildsTheJsonReply() {
        val json = Greeting("Hello, JVM!", "1.0.0", "laptop", 3).toJson()
        assertEquals("""{"message":"Hello, JVM!","version":"1.0.0","host":"laptop","visits":3}""", json)
    }

    @Test
    fun escapesQuotesAndNewlines() {
        assertEquals(""""say \"hi\"\nbye"""", quote("say \"hi\"\nbye"))
    }
}
