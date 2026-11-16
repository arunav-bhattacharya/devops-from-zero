OPENING = """Picture a hospital at night. A nurse looks after a patient and writes each step on a clipboard that hangs on the bed: a pill at 2 a.m., a fever at 3. At 4 a.m. the patient moves to another ward. The bed is cleaned, and the clipboard goes out with the old sheets. In the morning a doctor asks why the fever started, and nobody can say.

Nobody did anything wrong. Every note was written at the right moment. The trouble is where the notes were kept. Software has the same trouble: programs write notes about their work, and the place they keep them is thrown away with the program.

Last time, we sent those notes to Loki, a log store that indexes only a few labels. Today we try a store that indexes every word. We'll send our lab app's notes to one place, search them, and watch a few searches fail before we see why.

Before we start, make a guess, and keep it in mind."""

S1 = """Every program can write short notes about its work: started, served a page, could not reach the database. Those lines are its log. Our lab app, hello-devops, is a tiny web app that answers every visit with a greeting and a count of visits so far. It logs each visit and each error.

In Part 5 you read those lines with `docker logs`. Docker runs each app in a container, a sealed box that holds the app and all it needs. On one laptop that is enough. Now run hello-devops on Kubernetes, the system that spreads containers across many machines. Three copies run on three machines, and every new release replaces all three. A customer says a payment failed at 14:02. Which copy handled it? It may be gone, and its log with it, like the clipboard with the bed.

Centralized logging is the hospital's central chart. Every line every container prints is copied, as it is written, to one store you can search. Metrics from Part 12 say that errors went up. Logs say which request failed and why.

In the lab, each line passes through four programs, one job each:
1. The app prints one event per line to stdout, a program's standard text output.
2. A shipper, Fluent Bit, collects the lines, splits them into fields and sends them on.
3. A store, Elasticsearch, indexes every field so search is fast.
4. A web page, Kibana, lets people search and draw charts.

The first hand-off is Docker's. Whatever a container prints goes first to the Docker engine, the background program that runs containers. A setting called the logging driver decides where the engine sends it next. By default it writes to a file that `docker logs` reads. The lab's compose file (the list of containers Docker Compose starts) picks the `fluentd` driver for the web container instead. Now the engine sends every line to Fluent Bit and still keeps a local copy.

The engine finds Fluent Bit at `localhost:24224`. Localhost means this same computer. 24224 is the port, a numbered door that Fluent Bit listens behind. The engine opens this connection itself, not a container, so it knocks on the door Fluent Bit publishes on your laptop.

Inside Fluent Bit, the line passes three stages, each a block in its settings file, `fluent-bit.yaml`:
1. An input takes it in. `forward` listens on port 24224 for the Docker driver.
2. Filters change it. `multiline` glues a traceback (the many-line report of a crash) into one record, and `parser` turns a JSON line into fields.
3. Outputs send it on. `es` writes to Elasticsearch, and `stdout` prints a copy.

Each record carries a tag, here `hello.` plus the container name. A filter or output handles only the records whose tag fits its `match` pattern, the way a mail room sorts letters by name.

Next, we'll look at what a good line looks like before it sets out."""

S2 = """Compare two lines from the lab. Gunicorn, the web server that hands visits to hello-devops, prints this when it starts a worker:

`[2026-10-30 05:03:07 +0000] [8] [INFO] Booting worker with pid: 8`

And this is a line of the access log (one line per visit) that the lab turns on:

`{"level":"INFO","logger":"access","method":"GET","path":"/","status":200,"duration_ms":8}`

A machine has to guess where the first line's level ends and its message starts, and every program formats it a little differently. The second line is JSON, a text format of names and values inside curly braces. That makes it a structured log: data with named fields. Fluent Bit turns each name into a field, so you can ask for `status >= 500` or the slowest `path`. Nobody has to write a fragile pattern to cut the text apart.

You did not change `app.py`, the app's code, to get this. The lab's compose file gives gunicorn an `--access-logformat` that prints JSON. In your own services, use a JSON logging library and write one event per line. The payoff grows with every service that uses the same field names. If they all write `order_id`, one filter on it reads a failed payment's whole story.

Every event also carries a level, which says how much it matters. Most teams use these four:
- DEBUG: detail for developers. Usually off in production (the real system customers use), because it is loud.
- INFO: normal events, such as a request served or a job finished.
- WARN: something odd that has not failed yet, such as a retry.
- ERROR: a request or job failed, and someone may need to act.

Some things never belong in a log, because many people read the log store and it keeps data for weeks. Picture a password that a debug line printed on Monday. By Friday it sits in every copy and every backup of the store. A well-known security guide, the OWASP Logging Cheat Sheet, says to remove, mask or hash these before they are written:
- passwords, access tokens and session IDs
- database connection strings and encryption keys
- payment card and bank account data
- personal data, such as names, email addresses and home addresses

Tokens and session IDs are secret values that prove who you are, like a key card. Masking hides part of a value behind stars, and hashing turns it into a code that cannot be turned back. A token in a log is a security incident, and deleting it later is slow work. **A secret in a log has already leaked. Scrub it at the source.**

Next, we'll see what Elasticsearch does with these clean lines."""

S3 = """Elasticsearch is a search engine for your own data. Each log event arrives as a document, one JSON object. Elasticsearch gives it an `_id` and keeps the exact JSON you sent in a field called `_source`.

Documents live in an index, a named collection such as `hello-logs-2026.10.30`. You write to one index and can search many at once with a pattern like `hello-logs-*`, where the star matches anything. The lab makes one index per day, which keeps old days easy to delete.

Why not just search the text? The grep command, which you type in a terminal window, prints every line of a file that contains some text. It reads every line again on every search, which is far too slow for a week of logs from fifty containers. Elasticsearch does the reading once, when a document arrives. A part called the analyzer splits each text field into words, called tokens, and lowercases them. Elasticsearch then notes which documents contain each token. The result is an inverted index. It works like the index at the back of a book: to find "declined", you look it up once instead of reading every page.

In the worked example, the analyzer turned `Payment FAILED for order 42: card declined` into `payment`, `failed`, `for`, `order`, `42`, `card` and `declined`.

Now try searching the grep way, by any piece of text. A search for `payments` finds nothing. Only `payment` was stored, and the default analyzer does not reduce words to a common stem. Next, stop Redis, the small database that keeps the app's visit count. The app now fails with `redis.exceptions.ConnectionError`. Search for `ConnectionError` and you get zero hits. Dots between letters do not split words, so the whole dotted name is one token. Search for the phrase `"service not known"` from the same error and you find it at once.

That was the guess at the start. The error happened, but our search asked for a word that was never filed. Before you trust an empty result, check the tokens with `_analyze`. **Search finds whole tokens, never pieces of them. Ask for words that are really there.**

One more surprise: new documents are not searchable in the same instant. Elasticsearch makes them visible within about one second, in a step called a refresh. The Elastic docs call this near real-time search.

Next, we'll see who decides which fields are text."""

S4 = """Each index has a mapping: the type of every field and how it is indexed. You can write the mapping yourself. Or you can let Elasticsearch guess each type from the first document that has the field. That guess is called dynamic mapping, and it sticks. Every stored document was indexed for that type, so Elasticsearch never changes a field's type in place. To fix one, you create a new index with the right mapping and copy the documents over, a reindex.

The two types you will meet most in logs are:
- `text`: split into tokens for full-text search. Good for `message` or `log`.
- `keyword`: stored whole, for exact filters, sorting and counting. Good for `level`, `path` or `service`.

A keyword is matched exactly, capitals included. In the worked example the `level` field held `ERROR`, so a search for `error` on it found nothing.

For strings (pieces of text), dynamic mapping makes both: a `text` field plus a `.keyword` sub-field. That is why the lab's index shows `path` and also `path.keyword`. Whole numbers become `long`, so `status` and `duration_ms` are numbers you can compare and average.

The guess is only as good as the first document. Imagine a new service whose first line sends `"duration_ms": "120"` in quotes, as a string. The field becomes text, and you can never average it in that index. Later, a document sends a value the mapped type cannot hold. Elasticsearch rejects it with a `document_parsing_exception` and HTTP status 400, the web's code for "your request was wrong". Then someone logs request headers, the extra details a browser sends with each request, as keys. Every new header becomes a new field. The Elastic docs warn that too many fields, a mapping explosion, can run the cluster out of memory.

The fix is an explicit mapping. On Day 56 you put one into an index template, so every new daily index starts with the right types.

Next, we'll see what a cluster is, and why yours shows yellow."""

S5 = """One running Elasticsearch program is a node. Nodes that work together form a cluster. Your lab is a cluster of one node.

An index is split into shards. Each shard holds part of the documents, with a small inverted index of its own. Shards let one index spread over many nodes, so more machines can store and search it in parallel.

Each document belongs to exactly one primary shard, which holds the original. A replica shard is a copy of a primary on another node. If that node dies, the copy takes over. Replicas also help answer searches.

Two rules follow:
1. The number of primary shards is fixed when the index is created. Elasticsearch picks each document's shard from a hash of its `_id` (a number always worked out the same way from it) and the number of primaries. A new number would send lookups to the wrong shard. Replicas can change at any time.
2. Elasticsearch never puts a replica on the same node as its primary, because a copy on the same machine would die with it.

Cluster health works like a traffic light. Green means every shard is placed. Yellow means all data is there, but a copy is missing. Red means a primary is missing, so some data cannot be searched. Rule 2 is why the lab's daily index starts yellow on your laptop: new indices get one replica by default, and it has nowhere to go. On Day 56 you set replicas to 0 for it. On one node, yellow is normal.

More shards are not free. Each search runs on one thread per shard (a thread is one line of work the computer runs), and every shard costs memory. The Elastic sizing guide suggests shards between 10 GB and 50 GB. A lab that stores a few megabytes a day needs one shard per index.

Next, we'll meet the family of tools around Elasticsearch."""

S6 = """Read a few logging tutorials and you meet a jumble of letters. ELK is the classic one: three products of Elastic, the company behind Elasticsearch. Elasticsearch stores and searches, and Kibana is the web page. The L is Logstash, which collects and reshapes data and can do heavy changes on the way in. It runs on the JVM, the engine that runs Java programs, and needs a fair amount of memory. Elastic now calls the whole family, newer shippers included, the Elastic Stack.

EFK swaps the L for an F: Fluentd or Fluent Bit. Both are open source, so anyone may read, use and change the code, and neither is an Elastic product. Fluentd came first. Fluent Bit is written in C for small machines. Its docs compare the two:
- Memory: Fluentd needs more than 60 MB, Fluent Bit about 450 KB.
- Plugins (add-ons): Fluentd has over 1,000 external plugins, Fluent Bit over 100 built in.

This course needs neither Logstash nor Fluentd, because Fluent Bit sends straight to Elasticsearch. On Kubernetes a shipper runs on every node, so you pay for its memory once on every node. Fluent Bit was built for that job.

You will also meet OpenSearch, a close cousin of Elasticsearch. The box below tells its story. None of this changes the lab, and today's ideas carry over to it.

Next, we'll open Kibana and find our failed requests."""

S7 = """Kibana is Elastic's web page for reading and charting what Elasticsearch stores. You read logs on its Discover page, which offers two query languages. A query is a question you ask the data.

The classic language is KQL. It needs a data view first: a saved name pattern such as `hello-logs-*` plus the time field `@timestamp`. Then you type conditions into the search bar, each one a field, an operator and a value:
- `status >= 500` shows failed requests (500 is the code for a server failure). It works because `status` is a number.
- `path: "/readyz" and not status: 200` combines two conditions. Status 200 means all went well.
- `log: "service not known"` finds a phrase inside a traceback.
- `not path: "/healthz"` hides the health checks Docker sends every 30 seconds.

The newer language, ES|QL, needs no data view. You write a pipeline: steps joined by `|`, each working on the rows from the step before. This query counts failed requests per path:

`FROM hello-logs-* | WHERE status >= 500 | STATS errors = COUNT(*) BY path | SORT errors DESC`

It takes the daily indices, keeps the failures, counts them per path and puts the biggest count first. On the lab it returned 5 for `/readyz` and 3 for `/`.

My rule of thumb: KQL to narrow down what you are looking at, ES|QL when the question needs counting, grouping or math. You can even mix them, because ES|QL accepts KQL inside `WHERE KQL("status >= 500")`.

Two habits save time:
- Check the time picker first. Discover shows the last 15 minutes by default, so older logs look missing.
- Add the fields you care about (`path`, `status`, `duration_ms`) as columns. Otherwise each row is one long summary.

Today's setup has limits. It runs on one laptop and wants at least 6 GB of memory for Docker. Security is off, so anything that reaches port 9200 can read and delete every log. On Kubernetes, each line must also name the copy that wrote it, and old indices must go on a schedule. That is the next lesson."""

CLOSING = """We started with a clipboard thrown out with a hospital bed, and with a container's log lost with the container. Now every line hello-devops prints travels through Docker and Fluent Bit into one daily index, and Kibana finds it long after the container is gone. We also watched two honest searches find nothing, and saw why. In the lab, stop Redis, search for `ConnectionError` and then for `"service not known"`, and run `_analyze` on the error line to see which tokens were filed.

Next, we'll run the same pipeline on Kubernetes. When many copies of an app share one log store, how do we know who wrote each line?"""
