"""Day 47: Centralized logging and the Elastic stack."""
from common import lab, ref
import svg

L = {
    "id": "d47",
    "title": "Centralized logging and the Elastic stack",
    "minutes": 50,
    "goal": "By the end you can explain why teams centralize logs, run Elasticsearch, Kibana and Fluent Bit on your laptop, and find hello-devops errors in Kibana with KQL and ES|QL.",
    "guess": {
        "q": "A log line says `redis.exceptions.ConnectionError: Error -2 connecting to redis:6379`. You search Elasticsearch for `ConnectionError` and get zero hits. Why?",
        "options": [
            "New logs need a few minutes before Elasticsearch can search them",
            "Elasticsearch stored `redis.exceptions.connectionerror` as one word, and search matches whole words",
            "Search is case-sensitive, so you have to type `connectionerror` in lower case",
            "Elasticsearch only searches the first 256 characters of each log line",
        ],
        "answer": 1,
        "why": "Elasticsearch splits text into words (tokens) and searches those, not substrings. Dots between letters do not split a word, so the whole dotted name became one token, and `ConnectionError` on its own is not in the index.",
    },
    "terms": [
        {"term": "Centralized logging", "plain": "Copying the logs of every app and server to one place where you can search them together."},
        {"term": "Structured log", "plain": "A log line written as data with named fields, usually one JSON object per line."},
        {"term": "Document", "plain": "One JSON object stored in Elasticsearch. In logging, one document is usually one log event."},
        {"term": "Index (Elasticsearch)", "plain": "A named collection of documents, such as hello-logs-2026.10.30, that you write to and search."},
        {"term": "Inverted index", "plain": "A table from each word to the documents that contain it, like the index at the back of a book."},
        {"term": "Mapping", "plain": "The list of fields in an index and the type of each one, such as text, keyword, long or date."},
        {"term": "Shard and replica", "plain": "A shard is one slice of an index. A replica is a copy of a shard kept on a different node."},
        {"term": "Fluent Bit", "plain": "A small open-source program that collects logs, parses them into fields and sends them on."},
    ],
    "sections": [
        {
            "h": "Why logs need one home",
            "body": """In Part 3 you read a container's output with `docker logs`. That works for one app on one laptop. Now picture hello-devops on Kubernetes: three pods on three nodes, replaced on every deploy. A customer says a payment failed at 14:02. Which pod handled it? That pod may not exist any more, and its logs left with it.

Centralized logging fixes this. Every line every container prints is copied, as it is written, to one store you can search. The copy outlives the container, so you stop asking where the log is and start asking what it says.

Metrics from Part 9 tell you that errors went up. Logs tell you which request failed and why. You need both, and you usually read them in that order.

A log pipeline has four jobs. The lab gives each one to a different program:
1. The app prints one event per line to stdout. hello-devops already does.
2. A shipper collects the lines, parses them into fields and sends them on. Here that is Fluent Bit.
3. A store indexes every field so search is fast. Here that is Elasticsearch.
4. A web UI lets people search and chart. Here that is Kibana.

In the lab, Docker itself hands each line to Fluent Bit. The compose file sets the `fluentd` logging driver on the web container, so the Docker engine sends every line to port 24224 as well as keeping its own copy. One detail matters: the engine opens that connection, not a container. That is why the address is `localhost:24224`, the port Fluent Bit publishes on your laptop, and why `fluentd-async` is set. Without it, a container stops at once when it cannot reach its log collector.""",
            "refs": [
                ref("OpenTelemetry: observability primer", "https://opentelemetry.io/docs/concepts/observability-primer/", "docs"),
                ref("Docker: Fluentd logging driver", "https://docs.docker.com/engine/logging/drivers/fluentd/", "docs"),
            ],
        },
        {
            "h": "Write logs a machine can read",
            "body": """Compare two lines from the lab. Gunicorn prints this when it starts a worker:

`[2026-10-30 05:03:07 +0000] [8] [INFO] Booting worker with pid: 8`

And this is one line of the access log the lab turns on:

`{"level":"INFO","logger":"access","method":"GET","path":"/","status":200,"duration_ms":8}`

The first is fine for a human. A machine has to guess where the level ends and the message starts, and every program formats it a little differently. The second is a structured log: data with named fields. Fluent Bit turns each key into a field, so you can ask for `status >= 500` or the slowest `path` without writing a regular expression.

You did not change `app.py` to get this. The lab's compose file gives gunicorn an `--access-logformat` that prints JSON. In your own services, use a JSON logging library and write one event per line.

Every event also carries a level. Most teams use these four:
- DEBUG: detail for developers. Usually off in production, because it is loud.
- INFO: normal events, such as a request served or a job finished.
- WARN: something odd that has not failed yet, such as a retry.
- ERROR: a request or job failed, and someone may need to act.

Some things never belong in a log, because many people read the log store and it keeps data for weeks. The OWASP Logging Cheat Sheet says to remove, mask or hash these before they are written:
- passwords, access tokens and session IDs
- database connection strings and encryption keys
- payment card and bank account data
- personal data, such as names, email addresses and home addresses

A token in a log is a security incident. Deleting it later from every copy and backup is slow, painful work, so scrub at the source.""",
            "refs": [
                ref("OWASP Logging Cheat Sheet", "https://github.com/OWASP/CheatSheetSeries/blob/master/cheatsheets/Logging_Cheat_Sheet.md", "read"),
                ref("OpenTelemetry: logs", "https://opentelemetry.io/docs/concepts/signals/logs/", "docs"),
            ],
        },
        {
            "h": "Documents, indices and the inverted index",
            "body": """Elasticsearch stores JSON documents. A document is one JSON object, and in logging one document is one log event. Each document gets an `_id`, and Elasticsearch keeps the exact JSON you sent in a field called `_source`.

Documents live in an index, a named collection such as `hello-logs-2026.10.30`. You write to one index and can search many at once with a pattern like `hello-logs-*`. The lab makes one index per day, which keeps old days easy to delete.

Search is fast because of the **inverted index**. When a document arrives, Elasticsearch splits each text field into words, called tokens, and lowercases them. Then it records, for every token, which documents contain it. It works like the index at the back of a book: to find "declined" you look it up once instead of reading every page.

Here is what the default analyzer did with a message in the worked example:

`Payment FAILED for order 42: card declined` became `payment`, `failed`, `for`, `order`, `42`, `card` and `declined`.

That explains two surprises you will hit in the lab:
- A search for `payments` finds nothing. Only `payment` was stored, and the default analyzer does not reduce words to a common stem.
- `redis.exceptions.ConnectionError` stays one token, because dots between letters do not split words. Search for `ConnectionError` and you get zero hits. Search for the phrase `"service not known"` from the same error and you find it at once.

This trips most people up, because grep matches any substring and Elasticsearch matches whole tokens.

New documents are not searchable in the same instant. Elasticsearch makes them visible within about one second, in a step called a refresh. The Elastic docs call this near real-time search.""",
            "refs": [
                ref("Elastic: index basics", "https://www.elastic.co/docs/manage-data/data-store/index-basics", "docs"),
                ref("Elastic: near real-time search", "https://www.elastic.co/docs/manage-data/data-store/near-real-time-search", "docs"),
            ],
        },
        {
            "h": "Mappings: text, keyword and the first guess",
            "body": """Each index has a **mapping**: the type of every field and how it is indexed. You can write one yourself, or let Elasticsearch guess from the first document that contains a field. That guess is called dynamic mapping, and it sticks.

The two types you will meet most in logs are:
- `text`: split into tokens for full-text search. Good for `message` or `log`.
- `keyword`: stored whole, for exact filters, sorting and counting. Good for `level`, `path` or `service`.

A keyword is matched exactly, capitals included. In the worked example the `level` field held `ERROR`, so a search for `error` on it found nothing.

For strings, dynamic mapping makes both: a `text` field plus a `.keyword` sub-field. That is why the lab's index shows `path` and also `path.keyword`. Whole numbers become `long`, so `status` and `duration_ms` are numbers you can compare and average.

The guess is only as good as the first document:
- A service sends `"duration_ms": "120"` as a string. The field becomes text, and you can never average it in that index.
- A later document sends a value the mapped type cannot hold. Elasticsearch rejects it with a `document_parsing_exception` and HTTP status 400.
- Someone logs request headers as keys. Every new header becomes a new field. The Elastic docs warn that too many fields, a mapping explosion, can run the cluster out of memory.

The fix is an explicit mapping. On Day 48 you put one into an index template, so every new daily index starts with the right types.""",
            "refs": [
                ref("Elastic: mapping", "https://www.elastic.co/docs/manage-data/data-store/mapping", "docs"),
            ],
        },
        {
            "h": "Shards, replicas and the yellow cluster",
            "body": """One running Elasticsearch process is a node. Nodes that work together form a cluster. Your lab is a cluster of one node.

An index is split into shards. Each shard is a complete small Lucene index (Lucene is the Java search library under Elasticsearch) holding part of the documents. Shards let one index spread over many nodes, so more machines can store and search it in parallel.

There are two kinds:
- A primary shard holds the original documents. Each document belongs to exactly one primary.
- A replica shard is a copy of a primary on another node. If that node dies, the copy takes over. Replicas also answer searches.

Two rules follow, and both surprise people:
1. The number of primary shards is fixed when the index is created. The number of replicas can change at any time.
2. Elasticsearch never puts a replica on the same node as its primary.

So on your laptop, an index with one replica is yellow: all data is there, but a copy is missing. Green means every shard is placed. Red means a primary is missing, so some data cannot be searched. The lab's daily index starts yellow for exactly this reason, because new indices get one replica by default. On Day 48 you set replicas to 0 for it.

More shards are not free. Each search runs on one thread per shard, and every shard costs memory. The Elastic sizing guide suggests shards between 10 GB and 50 GB. A lab that stores a few megabytes a day needs one shard per index.""",
            "refs": [
                ref("Elastic: clusters, nodes and shards", "https://www.elastic.co/docs/deploy-manage/distributed-architecture/clusters-nodes-shards", "docs"),
                ref("Elastic: red or yellow cluster health", "https://www.elastic.co/docs/troubleshoot/elasticsearch/red-yellow-cluster-status", "docs"),
                ref("Elastic: size your shards", "https://www.elastic.co/docs/deploy-manage/production-guidance/optimize-performance/size-shards", "docs"),
            ],
        },
        {
            "h": "ELK, EFK and OpenSearch",
            "body": """ELK is the classic name for three Elastic products used together:
- Elasticsearch stores and searches.
- Logstash collects and reshapes data. It runs on the JVM and can do heavy transformations on the way in.
- Kibana is the web UI.

Elastic later added Beats, small single-purpose shippers such as Filebeat, and then Elastic Agent, one agent you manage centrally with Fleet. Elastic now calls the whole family the Elastic Stack.

EFK swaps the L for an F: Fluentd or Fluent Bit. Both are open-source CNCF graduated projects, not Elastic products. Fluentd came first and is written in C and Ruby. Fluent Bit is written in C for small machines. Its docs compare the two like this:
- Memory: Fluentd needs more than 60 MB, Fluent Bit about 450 KB.
- Plugins: Fluentd has over 1,000 external plugins, Fluent Bit over 100 built in.

You need neither Logstash nor Fluentd: Fluent Bit sends straight to Elasticsearch, as in the lab. On Kubernetes a shipper runs on every node, so a small footprint matters, and that is the job Fluent Bit was built for.

The licence history explains the other product name you will meet:
1. Until January 2021, Elasticsearch and Kibana were open source under Apache 2.0.
2. Elastic then switched to a choice of SSPL or the Elastic License, and neither counts as an open source licence. The stated aim was to stop cloud providers selling Elasticsearch as a service.
3. AWS forked the last Apache 2.0 code as OpenSearch. It is still Apache 2.0 and has been under the Linux Foundation since September 2024.
4. In August 2024 Elastic added AGPLv3 as a third option. It sits next to the other two, and the binaries did not change.

For you, two facts matter. The lab images are free to run. And OpenSearch is close enough to Elasticsearch that today's ideas carry over.""",
            "refs": [
                ref("Elastic: the Elastic Stack", "https://www.elastic.co/docs/get-started/the-stack", "docs"),
                ref("Fluent Bit: Fluentd and Fluent Bit", "https://docs.fluentbit.io/manual/about/fluentd-and-fluent-bit", "docs"),
                ref("DevClass: Elasticsearch will be open source again (2024)", "https://devclass.com/2024/09/02/elasticsearch-will-be-open-source-again-as-cto-declares-changed-landscape/", "read"),
            ],
        },
        {
            "h": "Searching in Kibana: Discover, KQL and ES|QL",
            "body": """Kibana's Discover page is where you read logs. It has two query modes.

Classic mode needs a data view: a saved name pattern such as `hello-logs-*` plus the time field `@timestamp`. You type KQL, the Kibana Query Language, into the search bar. Each condition is a field, an operator and a value:
- `status >= 500` shows failed requests. It works because `status` is a number.
- `path: "/readyz" and not status: 200` combines two conditions.
- `log: "service not known"` finds a phrase inside a Python traceback.
- `not path: "/healthz"` hides the health checks Docker sends every 30 seconds.

ES|QL mode needs no data view. You write a pipeline, like a Unix pipe over your logs, where each step works on the rows from the step before. This query counts failed requests per path:

`FROM hello-logs-* | WHERE status >= 500 | STATS errors = COUNT(*) BY path | SORT errors DESC`

On the lab it returned 5 for `/readyz` and 3 for `/`. My rule of thumb: KQL to narrow down what you are looking at, ES|QL when the question needs counting, grouping or math. You can even mix them, because ES|QL accepts KQL inside `WHERE KQL("status >= 500")`.

Two habits save time:
- Check the time picker first. Discover shows the last 15 minutes by default, so older logs look missing.
- Add the fields you care about (`path`, `status`, `duration_ms`) as columns. Otherwise each row is one long summary.""",
            "refs": [
                ref("Exploring and querying your data with Kibana (Elastic)", "https://www.youtube.com/watch?v=t3cebUxRliA", "watch"),
                ref("Elastic: Kibana Query Language (KQL)", "https://www.elastic.co/docs/explore-analyze/query-filter/languages/kql", "docs"),
                ref("Elastic: ES|QL in Kibana", "https://www.elastic.co/docs/explore-analyze/query-filter/languages/esql-kibana", "docs"),
            ],
        },
    ],
    "analogy": "Picture a newspaper archive. Old papers do not sit in a reporter's desk drawer, which can be thrown out with the desk (a container). Every issue is filed in one building, one shelf per day (one index per day). The archive keeps a card catalogue of every word and the issues it appears in (the inverted index). So you find every mention of 'declined' without opening a single paper. Where it breaks: the catalogue lists only whole words, exactly as it filed them. A search for part of a word, or for a plural it never saw, comes back empty.",
    "diagram": svg.d47(),
    "diagram_caption": "One log line's road in the lab: printed by the app, handed over by Docker, parsed by Fluent Bit, indexed by Elasticsearch, searched in Kibana.",
    "worked": {
        "title": "Elasticsearch from zero with curl",
        "steps": [
            {
                "say": "Start only Elasticsearch from the lab and ask who it is. A GET on the root returns the cluster name and version. `filter_path` trims the answer to the fields you name, which keeps output readable.",
                "code": """$ cd logging
$ docker compose up -d elasticsearch
$ curl -s 'localhost:9200/?filter_path=cluster_name,version.number,version.lucene_version,tagline'
{
  "cluster_name" : "docker-cluster",
  "version" : {
    "number" : "9.5.5",
    "lucene_version" : "10.5.1"
  },
  "tagline" : "You Know, for Search"
}""",
                "lang": "console",
            },
            {
                "say": "Create an index with an explicit mapping, so nothing is left to guessing: `level` and `service` are keywords, `message` is full text. Ask for 1 primary shard and 1 replica, on purpose, because step 6 needs the replica.",
                "code": """$ curl -s -X PUT localhost:9200/demo-logs -H 'Content-Type: application/json' -d '{
  "settings": {"number_of_shards": 1, "number_of_replicas": 1},
  "mappings": {"properties": {
    "@timestamp": {"type": "date"},
    "level":      {"type": "keyword"},
    "service":    {"type": "keyword"},
    "message":    {"type": "text"}
  }}
}'
{"acknowledged":true,"shards_acknowledged":true,"index":"demo-logs"}""",
                "lang": "console",
            },
            {
                "say": "Store three log events. Elasticsearch picks each `_id`. Look at `_shards`: 2 copies were wanted (primary and replica) but only 1 was written, a first hint that the replica has nowhere to live. The last write asks for `refresh=true` so the next search sees all three at once.",
                "code": """$ curl -s -X POST localhost:9200/demo-logs/_doc -H 'Content-Type: application/json' -d '{"@timestamp":"2026-10-30T10:00:00Z","level":"ERROR","service":"checkout","message":"Payment FAILED for order 42: card declined"}'
{"_index":"demo-logs","_id":"MSBHi6EBJ7eB7uT9Rb6E","_version":1,"result":"created","_shards":{"total":2,"successful":1,"failed":0},"_seq_no":0,"_primary_term":1}
$ curl -s -X POST localhost:9200/demo-logs/_doc -H 'Content-Type: application/json' -d '{"@timestamp":"2026-10-30T10:00:05Z","level":"INFO","service":"checkout","message":"Payment accepted for order 43"}' > /dev/null
$ curl -s -X POST 'localhost:9200/demo-logs/_doc?refresh=true' -H 'Content-Type: application/json' -d '{"@timestamp":"2026-10-30T10:00:09Z","level":"WARN","service":"cart","message":"Cart 7 is slow to load"}' > /dev/null""",
                "lang": "console",
            },
            {
                "say": "Look inside the inverted index. `_analyze` shows the tokens a field would store. The text field splits and lowercases. The keyword field keeps the value whole, capitals and all.",
                "code": """$ curl -s -X POST 'localhost:9200/demo-logs/_analyze?filter_path=tokens.token' -H 'Content-Type: application/json' -d '{"field": "message", "text": "Payment FAILED for order 42: card declined"}'
{"tokens":[{"token":"payment"},{"token":"failed"},{"token":"for"},{"token":"order"},{"token":"42"},{"token":"card"},{"token":"declined"}]}
$ curl -s -X POST 'localhost:9200/demo-logs/_analyze?filter_path=tokens.token' -H 'Content-Type: application/json' -d '{"field": "level", "text": "ERROR"}'
{"tokens":[{"token":"ERROR"}]}""",
                "lang": "console",
            },
            {
                "say": "Now search, and predict each answer before you read it. `payment` finds both payment events. `payments` finds nothing, because that token was never stored. A `term` query for `error` on the keyword field also finds nothing: the stored value is `ERROR`.",
                "code": """$ curl -s 'localhost:9200/demo-logs/_search?filter_path=hits.total.value,hits.hits._source.message' -H 'Content-Type: application/json' -d '{"query": {"match": {"message": "payment"}}}'
{"hits":{"total":{"value":2},"hits":[{"_source":{"message":"Payment accepted for order 43"}},{"_source":{"message":"Payment FAILED for order 42: card declined"}}]}}
$ curl -s 'localhost:9200/demo-logs/_search?filter_path=hits.total.value,hits.hits._source.message' -H 'Content-Type: application/json' -d '{"query": {"match": {"message": "payments"}}}'
{"hits":{"total":{"value":0}}}
$ curl -s 'localhost:9200/demo-logs/_search?filter_path=hits.total.value' -H 'Content-Type: application/json' -d '{"query": {"term": {"level": "error"}}}'
{"hits":{"total":{"value":0}}}""",
                "lang": "console",
            },
            {
                "say": "Find the missing copy. `_cat/shards` lists the primary (`p`) as STARTED and the replica (`r`) as UNASSIGNED, so the index is yellow. Replicas are a setting you can change on a live index, so set them to 0 and it turns green.",
                "code": """$ curl -s 'localhost:9200/_cat/shards/demo-logs?v&h=index,shard,prirep,state,docs'
index     shard prirep state      docs
demo-logs 0     p      STARTED       3
demo-logs 0     r      UNASSIGNED
$ curl -s -X PUT localhost:9200/demo-logs/_settings -H 'Content-Type: application/json' -d '{"index": {"number_of_replicas": 0}}'
{"acknowledged":true}
$ curl -s 'localhost:9200/_cat/indices/demo-logs?v&h=health,index,pri,rep,docs.count'
health index     pri rep docs.count
green  demo-logs   1   0          3""",
                "lang": "console",
            },
            {
                "say": "Watch dynamic mapping guess, then watch a mapping say no. A new index sees `\"120\"` with quotes and maps `duration_ms` as text, for good. Then a date field refuses a value that is not a date (jq from Day 2 trims the long error). Delete both indices when you are done.",
                "code": """$ curl -s -X POST 'localhost:9200/demo-guess/_doc?refresh=true' -H 'Content-Type: application/json' -d '{"duration_ms": "120"}' > /dev/null
$ curl -s 'localhost:9200/demo-guess/_mapping?filter_path=*.mappings.properties.duration_ms.type'
{"demo-guess":{"mappings":{"properties":{"duration_ms":{"type":"text"}}}}}
$ curl -s -X POST localhost:9200/demo-logs/_doc -H 'Content-Type: application/json' -d '{"@timestamp": "soon"}' | jq -c '{status, error: .error.type}'
{"status":400,"error":"document_parsing_exception"}
$ curl -s -X DELETE localhost:9200/demo-logs,demo-guess
{"acknowledged":true}""",
                "lang": "console",
            },
        ],
    },
    "code": [
        {"lang": "yaml", "title": "logging/compose.yaml", "src": lab("logging/compose.yaml"), "run": "cd logging && docker compose up -d --build"},
        {"lang": "yaml", "title": "logging/fluent-bit.yaml", "src": lab("logging/fluent-bit.yaml"), "run": "docker run --rm -v \"$PWD/fluent-bit.yaml:/f.yaml:ro\" fluent/fluent-bit:5.1.5 -c /f.yaml --dry-run"},
    ],
    "commands": [
        {"cmd": "cd logging && docker compose up -d --build", "what": "Start Elasticsearch, Kibana, Fluent Bit, hello-devops and Redis in the background."},
        {"cmd": "docker compose ps", "what": "Show each container's state. Wait until elasticsearch says healthy."},
        {"cmd": "docker compose logs -f fluent-bit", "what": "Follow Fluent Bit's own log, including every record it sends on (the stdout output)."},
        {"cmd": "curl -s localhost:9200", "what": "Ask Elasticsearch for its cluster name and version."},
        {"cmd": "curl -s 'localhost:9200/_cat/health?v'", "what": "Show cluster health: green, yellow or red, plus shard counts."},
        {"cmd": "curl -s 'localhost:9200/_cat/indices/hello-logs-*?v'", "what": "List the daily log indices with their health, replicas and document counts."},
        {"cmd": "curl -s 'localhost:9200/hello-logs-*/_mapping?pretty'", "what": "Show the fields and types Elasticsearch created for your logs."},
        {"cmd": "curl -s -X POST 'localhost:9200/_analyze?filter_path=tokens.token' -H 'Content-Type: application/json' -d '{\"analyzer\": \"standard\", \"text\": \"Payment FAILED for order 42\"}'", "what": "Show the tokens the standard analyzer makes from a piece of text."},
        {"cmd": "curl -s 'localhost:9200/hello-logs-*/_search?q=status:500&size=1&pretty'", "what": "Quick search from the terminal: one document whose status is 500."},
        {"cmd": "curl -s -X POST 'localhost:9200/_query?format=txt' -H 'Content-Type: application/json' -d '{\"query\": \"FROM hello-logs-* | WHERE status >= 500 | STATS errors = COUNT(*) BY path\"}'", "what": "Run an ES|QL query and print the result as a text table."},
        {"cmd": "docker compose stop redis", "what": "Stop Redis so hello-devops returns errors you can search for. `docker compose start redis` brings it back."},
        {"cmd": "docker compose logs web", "what": "Read the app's lines locally. This still works with the fluentd driver, because Docker keeps a local copy."},
        {"cmd": "docker compose down -v", "what": "Stop the stack and delete the volume, which removes every stored log."},
    ],
    "mistake": "Treating the Kibana search box like grep. You search for part of a word, such as `ConnectionError` inside `redis.exceptions.ConnectionError`, get zero hits, and decide the error never happened. Elasticsearch matches whole tokens. Search for a phrase that really appears as words (`\"service not known\"`), or filter on structured fields such as `status >= 500`. Check the tokens with `_analyze` before you trust an empty result.",
    "real_world": "On a payments team, every service writes JSON logs with the same field names (`service`, `level`, `order_id`, `trace_id`), so one Kibana query works across all of them. Card numbers and tokens are masked inside the app before the line is printed, and a review checks new log statements for personal data. When a merchant reports a failed payment, on-call filters on `order_id` and reads the whole story across services in a minute.",
    "task": {
        "title": "Find hello-devops errors in Kibana",
        "steps": [
            "Give Docker Desktop at least 6 GB of memory (Settings, Resources). Add `logging/compose.yaml` and `logging/fluent-bit.yaml` from this lesson to your hello-devops repo.",
            "Start the stack from the `logging` folder and wait until Elasticsearch is healthy.",
            "Send 20 requests to http://localhost:8000/ and confirm that a `hello-logs-*` index exists and its document count grows.",
            "Stop Redis, call `/` and `/readyz` a few times to create failures, then start Redis again.",
            "Open Kibana at http://localhost:5601, create a data view for `hello-logs-*` with the time field `@timestamp`, and open Discover.",
            "Use KQL to show only the failed requests, with `path`, `status` and `duration_ms` as columns.",
            "Find the document that holds the Python traceback for one of the 500s and read which line of `app.py` failed.",
            "Switch Discover to ES|QL and count failed requests per path. Keep the stack running if you go on to Day 48, or stop it with `docker compose down -v`.",
        ],
        "hints": [
            "`status` is a number field, so comparison operators such as `>=` work on it.",
            "The traceback is in the `log` field. Search for a phrase from the error message, not for one long dotted word.",
            "If Discover is empty, widen the time picker before you suspect Fluent Bit.",
        ],
        "done_when": "You are done when Discover shows only the 500 and 503 requests and you have found the traceback line `File \"/app/app.py\", line 27, in count_visit`.",
    },
    "explain_back": {
        "prompt": "Explain to a teammate how a line that hello-devops prints ends up searchable in Kibana, in 3 to 4 sentences. Mention the logging driver, Fluent Bit, the index and the inverted index.",
        "answer": "The app prints each event as a line on stdout, and Docker's fluentd logging driver sends every line to Fluent Bit on port 24224. Fluent Bit glues tracebacks back together, turns JSON lines into fields and sends the records to Elasticsearch, which stores each one as a document in that day's hello-logs index. While storing it, Elasticsearch splits text fields into tokens and records which documents contain each token: the inverted index. Kibana's queries look tokens up in that table, which is why search is fast and why it matches whole words, not substrings.",
    },
    "recap": [
        "Centralized logging copies every line to one store, so logs outlive the containers that wrote them.",
        "Structured JSON logs give you fields to filter on. Never log secrets or personal data.",
        "Elasticsearch stores JSON documents in indices and finds them through an inverted index of tokens.",
        "Mappings decide field types. Text is split into words, keyword is matched whole, and the first guess sticks.",
        "Replicas never share a node with their primary, so a one-node lab with replicas is yellow.",
        "ELK uses Logstash, EFK uses Fluentd or Fluent Bit, and OpenSearch is the Apache 2.0 fork.",
    ],
    "check": [
        {
            "q": "Your logs get a new field, `customer_tier`, with values like `gold` and `silver`. You want to filter on it and count requests per tier. Which mapping type fits?",
            "options": ["text", "short", "boolean", "keyword"],
            "answer": 3,
            "why": "Exact filters and counts need the whole value stored as one term, which is what keyword does.",
        },
        {
            "q": "On your one-node lab you create an index with 2 primary shards and 2 replicas. What health do you expect for it?",
            "options": [
                "Green, because one node can hold all shards",
                "Yellow, because the replicas cannot share the node with their primaries",
                "Red, because there are more shards than nodes",
                "Green after one minute, once the replicas copy over",
            ],
            "answer": 1,
            "why": "All primaries are placed, so no data is missing (not red), but no replica can be placed on the same node as its primary.",
        },
        {
            "q": "You must ship logs from 200 small gateways with very little memory to Elasticsearch, with light JSON parsing on the way. Which shipper fits best?",
            "options": ["Logstash on every gateway", "Fluent Bit on every gateway", "Kibana on every gateway", "Elasticsearch on every gateway"],
            "answer": 1,
            "why": "Fluent Bit is a small C program built for exactly this, while Logstash runs on the JVM and needs far more memory.",
        },
    ],
    "interview": [
        {
            "q": "What is an inverted index, and why does it make Elasticsearch fast?",
            "a": "An inverted index maps each token to the list of documents that contain it, like the index at the back of a book. When a document is stored, Elasticsearch analyzes its text fields (splits them into words and usually lowercases them) and adds each token to that table. A search then looks up a few tokens and intersects their lists instead of scanning every document. The trade-off is that search matches tokens, so analyzers, mappings and phrase queries decide what you can find.",
        },
        {
            "q": "What is the difference between ELK and EFK, and when would you choose Fluent Bit?",
            "a": "Both use Elasticsearch to store and Kibana to search. ELK collects with Logstash, a JVM program that can do heavy transformations; EFK collects with Fluentd or Fluent Bit. I choose Fluent Bit when the shipper runs on many machines, such as every Kubernetes node. It is small (about 450 KB of memory against Fluentd's 60 MB or more) and can send straight to Elasticsearch. I would add Logstash or Fluentd as a central aggregator only if the pipeline needs transformations Fluent Bit cannot do.",
        },
        {
            "q": "What should never go into logs, and how do you enforce it?",
            "a": "Passwords, tokens, session IDs, connection strings, keys, payment card data and personal data such as emails should be removed, masked or hashed before the line is written. I enforce it in layers. The app's logging helpers mask known fields, code review checks new log statements, and a filter in the shipper is the last safety net. Scrubbing at the source matters most, because deleting a secret later from every index, replica and backup is hard.",
        },
    ],
    "deeper": {
        "minutes": 12,
        "body": """What happens when you run a search on `hello-logs-*`? The node that receives the request becomes the coordinator for that search, and it works in two rounds.

1. Query phase: the coordinator sends the query to one copy of every shard involved, primary or replica. Each shard searches its own inverted index on one thread and returns only the IDs and sort values of its best matches.
2. Fetch phase: the coordinator merges those short lists, picks the overall top results, and asks the right shards for the full documents.

This is why the shard count matters even on small data. A search over 30 daily indices with 1 shard each touches 30 shards. With 5 shards each it touches 150, and each one costs a thread and some memory. The Elastic sizing guide puts it plainly: searching a thousand 50 MB shards is much more expensive than searching one 50 GB shard with the same data. Most logging trouble with Elasticsearch at scale starts here, with too many small indices and shards (oversharding), for example one index per service per namespace per day.

Now the refresh. A new document first lands in an in-memory buffer. A refresh writes the buffer into a new segment, which is a small inverted index of its own, and opens it for search. By default Elasticsearch refreshes every second, but only on indices that received a search in the last 30 seconds. That is why the worked example added `?refresh=true` to its last write: it forced a refresh, so the very next search saw all three documents. For logs you never need that. A delay of a second is fine, and forcing refreshes on every write makes indexing slower.

The `_score` you saw in search results is relevance: how well a document matches the words you searched for. Product search lives on it. Logging mostly ignores it, because Kibana sorts log results by `@timestamp`, newest first.

One last check you can do right now: run `curl -s 'localhost:9200/_cat/segments/hello-logs-*?v'` while the lab takes traffic. Each line is a segment. Run it again later and the list may be shorter, because Lucene merges small segments into bigger ones in the background to keep searches cheap.""",
    },
    "sources": [
        {"title": "Elastic: index basics", "url": "https://www.elastic.co/docs/manage-data/data-store/index-basics"},
        {"title": "Elastic: clusters, nodes and shards", "url": "https://www.elastic.co/docs/deploy-manage/distributed-architecture/clusters-nodes-shards"},
        {"title": "Fluent Bit: Elasticsearch output", "url": "https://docs.fluentbit.io/manual/pipeline/outputs/elasticsearch"},
        {"title": "Elastic: Kibana Query Language (KQL)", "url": "https://www.elastic.co/docs/explore-analyze/query-filter/languages/kql"},
    ],
}
