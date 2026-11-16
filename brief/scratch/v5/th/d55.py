"""Book-voice rewrite of d55 (Centralized logging and the Elastic stack). Writer: th."""
import sys
sys.path.insert(0, "/home/user/devops-from-zero/brief/scratch/v5/th")
from common import apply

OPENING = """Picture a hospital at night. A nurse looks after a patient and writes each step on a clipboard that hangs on the bed: a pill at 2 a.m., a fever at 3. At 4 a.m. the patient moves to another ward. The bed is cleaned, and the clipboard goes out with the old sheets. In the morning a doctor asks why the fever started, and nobody can say.

Nobody did anything wrong. Every note was written at the right moment. The trouble is where the notes were kept. Software has the same trouble: programs write notes about their work, and the place they keep them is thrown away with the program.

In "Grafana beyond dashboards: alerting, Loki and the LGTM stack" we sent those notes to Loki, which indexes only a few labels. Today we try a store that indexes every word. We'll send our lab app's notes to one place, search them, and watch a few searches fail before we see why.

Before we start, make a guess, and keep it in mind."""

S1 = """Every program can write short notes about its own work: started, served a page, could not reach the database. Each note is one line of text, and all the lines together are the program's log. Our lab app, hello-devops, is a tiny web app that answers every visit with a greeting and a count of visits so far. It writes a line for every visit and for every error.

In Part 5 you read those lines with `docker logs`. Docker is the tool that runs each app in a container, a sealed box that holds the app and everything it needs. That works for one app on one laptop. Now picture hello-devops on Kubernetes, the system that runs containers across many machines. It runs as three pods (a pod is Kubernetes' wrapper around a container) on three nodes (the machines), and every deploy replaces all three. A customer says a payment failed at 14:02. Which pod handled it? That pod may not exist any more, and its logs left with it. That is our clipboard, gone with the bed.

Centralized logging is the hospital's central chart. Every line every container prints is copied, as it is written, to one store you can search. The pod that handled the 14:02 payment can be gone, and you can still read what it printed.

Metrics from Part 12 (numbers measured over time, such as errors per second) tell you that errors went up. Logs tell you which request failed and why. You need both, and you usually read them in that order.

A log pipeline has four jobs, and the lab gives each one to a different program:
1. The app prints one event per line to stdout, the standard place where a program writes its text. hello-devops already does.
2. A shipper collects the lines, splits them into fields and sends them on. Here that is Fluent Bit.
3. A store indexes every field so search is fast. Here that is Elasticsearch.
4. A web page lets people search and draw charts. Here that is Kibana.

So how does a line travel from the app to Fluent Bit? Docker carries it. Whatever a container prints goes first to the Docker engine, the background program that runs containers. A logging driver decides where the engine sends it. The default driver, `json-file`, writes it to a file that `docker logs` reads. The lab's compose file (the list of containers that Docker Compose starts together) sets the `fluentd` driver on the web container instead. Now the engine sends every line to port 24224, and it still keeps a local copy.

A port is a numbered door on a computer, and a program listens behind it. The engine opens this connection, not a container, so the address is `localhost:24224`. Localhost means this same computer, and 24224 is the port Fluent Bit publishes on your laptop. The lab also sets `fluentd-async`. Without it, a container stops at once when it cannot reach its log collector.

Fluent Bit is a small pipeline of its own. Its settings file, `fluent-bit.yaml`, is written in YAML (plain text with one name and value per line). It has one block per stage:
- Inputs take records in. `forward` listens on port 24224 for the Docker driver.
- Filters change records. `multiline` glues a traceback, the many-line error report that Python prints, into one record. `parser` turns a line of JSON (named fields in curly braces, shown in the next section) into fields.
- Outputs send records on. `es` writes to Elasticsearch, and `stdout` prints a copy.

Python is the language hello-devops is written in. Each record also carries a tag, a short label, here `hello.` plus the container name. Every filter and output has a `match` pattern and handles only the records whose tag fits it, much as a mail room sorts letters by the name on the envelope.

The road is ready. Next, we'll look at what a good line looks like before it sets out."""

S2 = """Compare two lines from the lab. Gunicorn, the web server program that receives visits and hands them to hello-devops, prints this when it starts a worker:

`[2026-10-30 05:03:07 +0000] [8] [INFO] Booting worker with pid: 8`

And this is one line of the access log the lab turns on, a log with one line per visit:

`{"level":"INFO","logger":"access","method":"GET","path":"/","status":200,"duration_ms":8}`

A person reads the first line easily. A machine has to guess where the level ends and the message starts, and every program formats it a little differently. The second line is JSON, a text format that writes data as names and values inside curly braces. That makes it a structured log: data with named fields. Fluent Bit turns each name into a field, so you can ask for `status >= 500` or the slowest `path`. You never write a regular expression, a text pattern for cutting lines apart that is easy to get wrong.

You did not change `app.py`, the app's code, to get this. The lab's compose file gives gunicorn an `--access-logformat` that prints JSON. In your own services, use a JSON logging library (ready-made code that writes the lines for you) and write one event per line.

Named fields pay off most when many services share them. Say a customer reports a failed payment, and every service writes `service`, `level`, `order_id` and `trace_id`. One filter on that `order_id` then reads the whole story across all of them.

Every event also carries a level, which says how much it matters. Most teams use these four:
- DEBUG: detail for developers. Usually off in production (the real system customers use), because it is loud.
- INFO: normal events, such as a request served or a job finished.
- WARN: something odd that has not failed yet, such as a retry.
- ERROR: a request or job failed, and someone may need to act.

Some things never belong in a log, because many people read the log store and it keeps data for weeks. The OWASP Logging Cheat Sheet comes from a non-profit group that publishes free security advice. It says to remove, mask or hash these before they are written:
- passwords, access tokens and session IDs
- database connection strings and encryption keys
- payment card and bank account data
- personal data, such as names, email addresses and home addresses

A token is a secret string that proves who you are, like a key card. A session ID is the value a website uses to remember that you logged in. Masking hides part of a value behind stars, and hashing turns it into a scrambled code that cannot be turned back. A token in a log is a security incident, and deleting it later from every copy and backup is slow work. **A secret in a log has already leaked. Scrub it at the source.**

Our lines are now clean, named and safe to keep. Next, we'll see what Elasticsearch does with them when they arrive."""

S3 = """The lines now reach Elasticsearch, a program that stores data and finds it again very fast, like a search engine for your own records. It stores JSON documents. A document is one JSON object, and in logging one document is one log event. Each document gets an `_id`, and Elasticsearch keeps the exact JSON you sent in a field called `_source`.

Documents live in an index, a named collection such as `hello-logs-2026.10.30`. You write to one index and can search many at once with a pattern like `hello-logs-*` (the star matches anything). The lab makes one index per day, which keeps old days easy to delete.

Why not just search the text itself? The terminal is the window where you type commands, and grep is a terminal command that prints every line containing some text. With grep, every search reads every line again. That is fine for one file, and far too slow for a week of logs from fifty pods. Elasticsearch does the reading once, when a document arrives, and builds an inverted index. A part called the analyzer splits each text field into words, called tokens, and lowercases them. Then Elasticsearch records, for every token, which documents contain it. It works like the index at the back of a book: to find "declined" you look it up once instead of reading every page.

Here is what the default analyzer did with a message in the worked example:

`Payment FAILED for order 42: card declined` became `payment`, `failed`, `for`, `order`, `42`, `card` and `declined`.

Now let's search the way grep taught us, by any piece of text, and watch two searches fail in the lab:
- A search for `payments` finds nothing. Only `payment` was stored, and the default analyzer does not reduce words to a common stem, so the two stay different words.
- `redis.exceptions.ConnectionError` stays one token, because dots between letters do not split words. Search for `ConnectionError` and you get zero hits. Search for the phrase `"service not known"` from the same error and you find it at once.

Remember the guess at the start? That second failure is its answer. The error means hello-devops could not reach Redis, the small database where it keeps its visit count. The error really happened. Our search simply asked for a word that was never filed. Before you trust an empty result, check the tokens with `_analyze`, as the worked example does. **Search finds whole tokens, never pieces of them. Ask for words that are really there.**

One more surprise: a new document is not searchable in the same instant. Elasticsearch makes new documents visible within about one second, in a step called a refresh. The Elastic docs call this near real-time search.

Tokens explain how text is searched. Next, we'll see how Elasticsearch decides which fields are text in the first place."""

S4 = """Every field has a type, such as text, number or date, and the type decides how the field is stored. Each index has a mapping: the type of every field and how it is indexed. You can write one yourself. Or you can let Elasticsearch guess from the first document that contains a field. That guess is called dynamic mapping, and it sticks.

Why can it not change its mind later? Every stored document was indexed for that type, so Elasticsearch never changes a field's type in place. To fix a type, you create a new index with the right mapping and copy the documents over. That copy is called a reindex.

The two types you will meet most in logs are:
- `text`: split into tokens for full-text search. Good for `message` or `log`.
- `keyword`: stored whole, for exact filters, sorting and counting. Good for `level`, `path` or `service`.

A keyword is matched exactly, capitals included. In the worked example the `level` field held `ERROR`, so a search for `error` on it found nothing. It is the token story again, from the other side: text forgets capitals, and keyword remembers every one.

For strings (pieces of text), dynamic mapping makes both: a `text` field plus a `.keyword` sub-field. That is why the lab's index shows `path` and also `path.keyword`. Whole numbers become `long`, the type for large whole numbers. So `status` and `duration_ms` are numbers you can compare and average.

The guess is only as good as the first document, and it goes wrong in three common ways:
- A service sends `"duration_ms": "120"` with quotes, as a string. The field becomes text, and you can never average it in that index.
- A later document sends a value the mapped type cannot hold. Elasticsearch rejects it with a `document_parsing_exception` and HTTP status 400. HTTP is the language of web requests, and 400 is its code for "your request was wrong".
- Someone logs request headers as keys. Headers are the extra lines of information a browser sends with every request. Every new header becomes a new field, and the Elastic docs warn that too many fields, a mapping explosion, can run the cluster out of memory.

The fix is an explicit mapping, written by you before the first document arrives. On Day 56 you put one into an index template, so every new daily index starts with the right types.

The word "cluster" just slipped in. Next, we'll see what it means, and why the one on your laptop shows yellow."""

S5 = """One running Elasticsearch program is a node. Nodes that work together form a cluster. Your lab is a cluster of one node.

An index is split into shards. Each shard is a complete small Lucene index holding part of the documents. Lucene is the search library under Elasticsearch: ready-made code, written in Java, that builds and reads inverted indices. Shards let one index spread over many nodes, so more machines can store and search it at the same time.

There are two kinds:
- A primary shard holds the original documents. Each document belongs to exactly one primary.
- A replica shard is a copy of a primary on another node. If that node dies, the copy takes over. Replicas also answer searches.

Two rules follow from this:
1. The number of primary shards is fixed when the index is created. Elasticsearch picks each document's shard from a hash of its `_id` and the number of primaries. A hash is a number worked out from the id, always the same for the same id. So a new number of primaries would send lookups to the wrong shard. Replicas can change at any time.
2. Elasticsearch never puts a replica on the same node as its primary, because a copy on the same machine would die with it.

Rule 2 explains a colour you will see on day one. Cluster health works like a traffic light:
- Green: every shard is placed.
- Yellow: all data is there, but a copy is missing.
- Red: a primary is missing, so some data cannot be searched.

On a one-node cluster, an index with one replica is yellow, because its copy has nowhere to live. The lab's daily index starts yellow for exactly this reason: new indices get one replica by default. On Day 56 you set replicas to 0 for it. On a one-node lab, yellow is normal. The cluster is only telling you the truth.

More shards are not free. Each search runs on one thread per shard (a thread is one line of work the computer runs), and every shard costs memory. The Elastic sizing guide suggests shards between 10 GB and 50 GB. A lab that stores a few megabytes a day needs one shard per index.

We now know how Elasticsearch stores and spreads our logs. Next, we'll meet the family of tools around it, and the names you will keep meeting in tutorials."""

S6 = """Elastic is the company that makes Elasticsearch. ELK is the classic name for three of its products used together:
- Elasticsearch stores and searches.
- Logstash collects and reshapes data. It runs on the JVM, the engine that runs Java programs and needs a fair amount of memory. It can do heavy changes on the way in.
- Kibana is the web page you search in.

Elastic later added Beats, small shippers that each do one job, such as Filebeat for log files. Then came Elastic Agent, one agent you manage from a central place called Fleet. An agent here is a program that runs on each machine and collects data. Elastic now calls the whole family the Elastic Stack.

EFK swaps the L for an F: Fluentd or Fluent Bit. Both are open-source projects, which means anyone may read, use and change their code. Neither is an Elastic product. Both are graduated projects of the CNCF, the non-profit foundation that looks after Kubernetes and many tools around it. Graduated is its most mature level. Fluentd came first and is written in C and Ruby, two programming languages. Fluent Bit is written in C for small machines. Its docs compare the two like this:
- Memory: Fluentd needs more than 60 MB, Fluent Bit about 450 KB.
- Plugins (add-ons that bring new inputs, filters or outputs): Fluentd has over 1,000 external plugins, Fluent Bit over 100 built in.

For this course you need neither Logstash nor Fluentd, because Fluent Bit sends straight to Elasticsearch. On Kubernetes a shipper runs on every node, so you pay for its memory once on every node. That is the job Fluent Bit was built for.

You will also meet a third name, OpenSearch. It looks and works much like Elasticsearch, and the box below tells where it came from. None of this changes the lab, and today's ideas carry over to OpenSearch.

Enough family history. Next, we'll open Kibana and find our failed requests."""

S7 = """Kibana is Elastic's web page for reading and charting what Elasticsearch stores. You read logs on its Discover page, which has two query modes. A query is a question you ask the data in a form the computer understands.

Classic mode needs a data view: a saved name pattern such as `hello-logs-*` plus the time field `@timestamp`. You type KQL, the Kibana Query Language, into the search bar. Each condition is a field, an operator such as `>=` or `:`, and a value:
- `status >= 500` shows failed requests. It works because `status` is a number.
- `path: "/readyz" and not status: 200` combines two conditions.
- `log: "service not known"` finds a phrase inside a Python traceback.
- `not path: "/healthz"` hides the health checks Docker sends every 30 seconds.

Status 200 means a request went well, and 500 means the server failed. `/healthz` and `/readyz` are pages the app offers so that tools can ask "are you alive?" and "are you ready?".

ES|QL mode, the Elasticsearch Query Language, needs no data view. You write a pipeline, like a Unix pipe over your logs. A Unix pipe chains terminal commands with `|`, so each one works on the output of the one before. In ES|QL, each step works on the rows from the step before. This query counts failed requests per path:

`FROM hello-logs-* | WHERE status >= 500 | STATS errors = COUNT(*) BY path | SORT errors DESC`

Read it left to right: take the daily indices, keep the failures, count them per path, and put the biggest count first. On the lab it returned 5 for `/readyz` and 3 for `/`.

My rule of thumb: KQL to narrow down what you are looking at, ES|QL when the question needs counting, grouping or math. You can even mix them, because ES|QL accepts KQL inside `WHERE KQL("status >= 500")`.

Two habits save time:
- Check the time picker first. Discover shows the last 15 minutes by default, so older logs look missing.
- Add the fields you care about (`path`, `status`, `duration_ms`) as columns. Otherwise each row is one long summary.

Today's setup has limits. It runs on one laptop with Docker Compose and wants at least 6 GB of memory for Docker. Security is switched off, so anything that can reach port 9200 can read and delete every log. On Kubernetes you also want each line to say which pod wrote it, and old daily indices must go on a schedule. That is where the next lesson picks up."""

CLOSING = """We started with a clipboard thrown out with a hospital bed, and with a container's log lost with the container. Now every line hello-devops prints travels through Docker and Fluent Bit into one daily index, and Kibana finds it long after the container is gone. We also watched two honest searches find nothing, and saw why. In the lab, stop Redis, search for `ConnectionError` and then for `"service not known"`, and run `_analyze` on the error line to see which tokens were filed.

Next, we'll run the same pipeline in "Running EFK on Kubernetes", and answer a new question: when many pods share one log store, how do we know who wrote each line?"""

ASIDE = {
    "title": "Why do Elasticsearch and OpenSearch both exist?",
    "body": "Until January 2021, Elasticsearch and Kibana were open source under Apache 2.0, a licence (the legal terms for using code) that allows almost any use. Elastic then switched to a choice of the Server Side Public License (SSPL) or the Elastic License, and neither counts as an open source licence. The stated aim was to stop cloud providers, the companies that rent out computers over the internet, from selling Elasticsearch as a service. AWS, Amazon's cloud, forked the last Apache 2.0 code as OpenSearch: it took a copy and develops it on its own. OpenSearch is still Apache 2.0 and has been under the Linux Foundation since September 2024. In August 2024 Elastic added the GNU Affero General Public License (AGPLv3), an open source licence, as a third option next to the other two, and the binaries (the programs you download) did not change.",
    "after": 5,
}

new = {
    "goal": "By the end you can explain why teams keep all their logs in one place, run Elasticsearch, Kibana and Fluent Bit on your laptop, and find hello-devops errors in Kibana with KQL and ES|QL.",
    "opening": OPENING,
    "guess": (
        "hello-devops prints an error line that says `redis.exceptions.ConnectionError: Error -2 connecting to redis:6379`. You search Elasticsearch for `ConnectionError` and get zero hits. Why?",
        "Elasticsearch splits text into words, called tokens, and searches for whole tokens, never pieces of them. Dots between letters do not split a word, so the whole dotted name became one token, and `ConnectionError` on its own is not in the index.",
    ),
    "terms": [
        "Copying the logs of every app and machine to one place where you can search them together.",
        "A log line written as named fields with values, such as a status and a path, usually as one JSON object per line.",
        "One record stored in Elasticsearch, written as a JSON object. In logging, one document is usually one log event.",
        "A named collection of documents, such as hello-logs-2026.10.30, that you write to and search.",
        "A table from each word to the documents that contain it, like the index at the back of a book.",
        "The list of fields in an index and the type of each one, such as text, keyword, long or date.",
        "A shard is one slice of an index. A replica is a copy of a shard kept on a different machine.",
        "A small, free program that collects logs, splits them into named fields and sends them on.",
    ],
    "sections": [
        ("Why every log line needs one home", S1),
        ("Write lines a machine can read, and keep secrets out", S2),
        ("Documents, indices and a search that finds nothing", S3),
        ("Mappings: text, keyword and a first guess that sticks", S4),
        ("Shards, replicas and why your laptop shows yellow", S5),
        ("ELK, EFK and OpenSearch: who is who", S6),
        ("Searching in Kibana with KQL and ES|QL", S7),
    ],
    "aside": ASIDE,
    "diagram_caption": "One log line's road in the lab: printed by the app, handed over by Docker, split into fields by Fluent Bit, indexed by Elasticsearch, searched in Kibana.",
    "say": [
        "Start only Elasticsearch from the lab and ask it who it is. `curl` is a terminal command that sends a web request and prints the answer. A GET request (a request that only reads) on the root address returns the cluster name and version. `filter_path` trims the answer to the fields you name, so the output stays short.",
        "Create an index with an explicit mapping, so nothing is left to guessing: `level` and `service` are keywords, and `message` is full text. Ask for 1 primary shard and 1 replica on purpose, because step 6 needs the replica.",
        "Store three log events, and let Elasticsearch pick each `_id`. Look at `_shards` in the answer: 2 copies were wanted (primary and replica), but only 1 was written. That is a first hint that the replica has nowhere to live. The last write asks for `refresh=true`, so the next search sees all three at once.",
        "Look inside the inverted index. `_analyze` shows the tokens a field would store. The text field splits the message and lowercases it. The keyword field keeps the value whole, capitals and all.",
        "Now search, and predict each answer before you read it. `payment` finds both payment events. `payments` finds nothing, because that token was never stored. A `term` query (an exact match on one stored value) for `error` on the keyword field also finds nothing, because the stored value is `ERROR`.",
        "Find the missing copy. `_cat/shards` lists the primary (`p`) as STARTED and the replica (`r`) as UNASSIGNED, so the index is yellow. Replicas are a setting you can change on a live index. Set them to 0, and it turns green.",
        "Watch dynamic mapping guess, and then watch a mapping say no. A new index sees `\"120\"` in quotes and maps `duration_ms` as text, for good. Then a date field refuses a value that is not a date. jq, the JSON tool from Day 2, trims the long error. Delete both indices when you are done.",
    ],
    "task": (
        [
            "Give Docker Desktop, the app that runs Docker on your Mac, at least 6 GB of memory (Settings, Resources). Add `logging/compose.yaml` and `logging/fluent-bit.yaml` from this lesson to your hello-devops repo.",
            "Start the stack from the `logging` folder and wait until Elasticsearch is healthy.",
            "Send 20 requests to http://localhost:8000/ and confirm that a `hello-logs-*` index exists and that its document count grows.",
            "Stop Redis, call `/` and `/readyz` a few times to create failures, then start Redis again.",
            "Open Kibana at http://localhost:5601, create a data view for `hello-logs-*` with the time field `@timestamp`, and open Discover.",
            "Use KQL to show only the failed requests, with `path`, `status` and `duration_ms` as columns.",
            "Find the document that holds the Python traceback for one of the 500s, and read which line of `app.py` failed.",
            "Switch Discover to ES|QL and count failed requests per path. Keep the stack running if you go on to Day 56, or stop it with `docker compose down -v`.",
        ],
        [
            "`status` is a number field, so comparison operators such as `>=` work on it.",
            "The traceback is in the `log` field. Search for a phrase from the error message, not for one long dotted word.",
            "If Discover is empty, widen the time picker before you suspect Fluent Bit.",
        ],
        "You are done when Discover shows only the 500 and 503 requests and you have found the traceback line `File \"/app/app.py\", line 27, in count_visit`.",
    ),
    "explain_back": (
        "Explain to a teammate how a line that hello-devops prints ends up searchable in Kibana, in 3 to 4 sentences. Mention the logging driver, Fluent Bit, the index and the inverted index.",
        "The app prints each event as a line on stdout, and Docker's fluentd logging driver sends every line to Fluent Bit on port 24224. Fluent Bit glues tracebacks back together, turns JSON lines into fields and sends the records to Elasticsearch. Elasticsearch stores each one as a document in that day's hello-logs index. While storing it, it splits text fields into tokens and records which documents contain each token: the inverted index. Kibana's queries look tokens up in that table, which is why search is fast, and why it matches whole words rather than pieces of words.",
    ),
    "recap": [
        "Centralized logging copies every line to one store, so logs outlive the containers that wrote them.",
        "Write structured JSON logs with named fields, and never log secrets or personal data.",
        "Elasticsearch stores each event as a document in an index and finds it through an inverted index of whole tokens.",
        "The mapping sets field types: text is split into words, keyword is matched whole, and the first guess sticks.",
        "ELK collects with Logstash, EFK with Fluentd or Fluent Bit, and OpenSearch is the Apache 2.0 fork.",
        "Today's limit: one laptop, one node, security off, so replicas stay unplaced and the index is yellow.",
    ],
    "closing": CLOSING,
    "check": [
        ("Your logs get a new field, `customer_tier`, with values like `gold` and `silver`. You want to filter on it and count requests per tier. Which mapping type fits?",
         "Exact filters and counts need the whole value stored as one term, and that is what keyword does."),
        ("On your one-node lab you create an index with 2 primary shards and 2 replicas. What health do you expect for it?",
         "All primaries are placed, so no data is missing (not red), but no replica can sit on the same node as its primary."),
        ("You must ship logs to Elasticsearch from 200 small gateways (little boxes at the edge of a network) with very little memory, with light JSON parsing on the way. Which shipper fits best?",
         "Fluent Bit is a small C program built for exactly this, while Logstash runs on the JVM and needs far more memory."),
    ],
    "interview": [
        ("What is an inverted index, and why does it make Elasticsearch fast?",
         "An inverted index maps each token to the list of documents that contain it, like the index at the back of a book. When a document is stored, Elasticsearch analyzes its text fields: it splits them into words and usually lowercases them. Then it adds each token to that table. A search looks up a few tokens and keeps the documents their lists share, instead of scanning every document. The trade-off is that search matches tokens, so analyzers, mappings and phrase queries decide what you can find."),
        ("What is the difference between ELK and EFK, and when would you choose Fluent Bit?",
         "Both use Elasticsearch to store and Kibana to search. ELK collects with Logstash, a JVM program that can do heavy transformations. EFK collects with Fluentd or Fluent Bit. I choose Fluent Bit when the shipper runs on many machines, such as every Kubernetes node: it is small (about 450 KB of memory against Fluentd's 60 MB or more) and can send straight to Elasticsearch. I would add Logstash or Fluentd as a central aggregator only if the pipeline needs transformations Fluent Bit cannot do."),
        ("What should never go into logs, and how do you enforce it?",
         "Passwords, tokens, session IDs, connection strings, keys, payment card data and personal data such as emails should be removed, masked or hashed before the line is written. I enforce it in layers. The app's logging helpers mask known fields, code review checks new log statements, and a filter in the shipper is the last safety net. Scrubbing at the source matters most, because deleting a secret later from every index, replica and backup is hard."),
    ],
    "deeper": """What happens when you run a search on `hello-logs-*`? The node that receives the request becomes the coordinator for that search, and it works in two rounds.

1. Query phase: the coordinator sends the query to one copy of every shard involved, primary or replica. Each shard searches its own inverted index on one thread and returns only the IDs and sort values of its best matches.
2. Fetch phase: the coordinator merges those short lists, picks the overall top results, and asks the right shards for the full documents.

This is why the shard count matters even on small data. A search over 30 daily indices with 1 shard each touches 30 shards. With 5 shards each it touches 150, and each one costs a thread and some memory. The Elastic sizing guide gives an example: searching a thousand 50 MB shards costs much more than searching one 50 GB shard with the same data. Most logging trouble with Elasticsearch at scale starts here, with too many small indices and shards. That problem is called oversharding, and one index per service per namespace (a named area inside a Kubernetes cluster) per day is a typical way to get it.

The one-second delay from earlier comes from the refresh. A new document first lands in a buffer, a holding area in memory. A refresh writes the buffer into a new segment, which is a small inverted index of its own, and opens it for search. By default Elasticsearch refreshes every second, but only on indices that received a search in the last 30 seconds. That is why the worked example added `?refresh=true` to its last write: it forced a refresh, so the very next search saw all three documents. For logs you never need that. A delay of a second is fine, and forcing a refresh on every write makes indexing slower.

The `_score` you saw in search results is relevance: how well a document matches the words you searched for. Product search in an online shop lives on it. Logging mostly ignores it, because Kibana sorts log results by `@timestamp`, newest first.

One last check you can do right now: run `curl -s 'localhost:9200/_cat/segments/hello-logs-*?v'` while the lab takes traffic. Each line is a segment. Run it again later and the list may be shorter, because Lucene merges small segments into bigger ones in the background to keep searches cheap.""",
    "drop": ["analogy", "mistake", "real_world"],
}

apply(14, "d55", new)
