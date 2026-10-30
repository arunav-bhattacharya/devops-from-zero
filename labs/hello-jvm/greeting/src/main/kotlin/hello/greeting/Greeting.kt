package hello.greeting

/** What GET / returns. It has no web code, so it is easy to test on its own. */
data class Greeting(
    val message: String,
    val version: String,
    val host: String,
    val visits: Long,
) {
    fun toJson(): String =
        jsonObject(
            "message" to message,
            "version" to version,
            "host" to host,
            "visits" to visits,
        )
}

/** Turns pairs into one JSON object. Numbers and booleans stay bare; everything else becomes a string. */
fun jsonObject(vararg fields: Pair<String, Any>): String =
    fields.joinToString(separator = ",", prefix = "{", postfix = "}") { (key, value) ->
        val json = if (value is Number || value is Boolean) value.toString() else quote(value.toString())
        "${quote(key)}:$json"
    }

/** Puts text in double quotes and escapes the characters JSON does not allow as they are. */
fun quote(text: String): String =
    buildString {
        append('"')
        for (c in text) {
            when {
                c == '"' -> append("\\\"")
                c == '\\' -> append("\\\\")
                c == '\n' -> append("\\n")
                c == '\r' -> append("\\r")
                c == '\t' -> append("\\t")
                c < ' ' -> append("\\u%04x".format(c.code))
                else -> append(c)
            }
        }
        append('"')
    }
