# Centralized logging (ELK/EFK) and distributed tracing (OpenTelemetry), as of October 2026

Research notes for 2 logging lessons and 1 tracing lesson (about 40 minutes each). Audience: an experienced software engineer new to observability, working on an Apple Silicon Mac, with free local practice only.

**How sources were verified (read this first).** The sandbox blocked WebFetch to elastic.co (DNS failure), YouTube oEmbed, and the GitHub REST API. So most facts come from the **source repositories of the official docs**, cloned with `git` and read locally on 2026-10-30:
- `fluent/fluent-bit-docs` (master, last commit 2026-10-28)
- `elastic/docs-content` (main, 2026-10-29), which is the source of www.elastic.co/docs
- `open-telemetry/opentelemetry.io` (main, 2026-10-29)
- `jaegertracing/documentation` (main, 2026-10-08)
- `grafana/loki` and `grafana/tempo` (main, 2026-10-30)
- `docker/docs` (main)
- `OWASP/CheatSheetSeries`
- `w3c/trace-context`

Citations point to the GitHub file I read. Versions come from `git ls-remote --tags` on each project repo. Release dates are the commit dates of the release tags, fetched with a shallow `git fetch`. Other URLs appeared in WebSearch results and are marked "(search result)". Published-site equivalents of the docs-content files follow the pattern `https://www.elastic.co/docs/<path-without-.md>`; Fluent Bit's own docs link to Elastic pages in that form. I did not open those published pages. YouTube links come only from search results, and I could not confirm their channels (oEmbed was blocked). Config and query examples marked **[author example, untested]** are mine, built from the cited docs. **Run them before publishing a lesson.**

---

## Lesson 1 blueprint: Centralized logging and the Elastic stack (concepts, misconceptions, examples, exercises, resources)

### Takeaway
Teach this order: why centralize, then logs as structured events, then the pipeline (ship, parse, store and index, search), then Elasticsearch internals (document, index, mapping, inverted index, shards and replicas, nodes and cluster, near real-time), then the shipper options (Logstash, Beats, Elastic Agent, Fluent Bit or Fluentd), then Kibana Discover with KQL and ES|QL, and finally the licence history that produced OpenSearch. Elasticsearch and Kibana are at 9.5.5. In 9.x, Discover has an ES|QL mode next to the "classic" KQL mode, and new `logs-*-*` data streams use the space-saving logsdb mode by default.

### Cited Findings

**Concepts in teaching order (each with a plain explanation and an intuition)**
1. **Why centralize.** On Kubernetes, a log agent "needs to run on every node to collect logs from every pod". Fluent Bit is deployed as a DaemonSet for that reason, and it adds pod metadata to every record — [fluent-bit-docs: Kubernetes](https://github.com/fluent/fluent-bit-docs/blob/master/installation/downloads/kubernetes.md). *Intuition:* containers are disposable hotel rooms. If the guest's diary stays in the room, housekeeping throws it away. Ship it to the front desk.
2. **Logs as events, structured.** The OpenTelemetry primer says logs "aren't necessarily associated with" a request, and "become far more useful when they are included as part of a span, or when they are correlated with a trace and a span" — [OTel observability primer](https://github.com/open-telemetry/opentelemetry.io/blob/main/content/en/docs/concepts/observability-primer.md). Charity Majors (Honeycomb) argues for "arbitrarily-wide structured log events" as the single source of truth: "You aggregate at read time, and preserve raw events for ad hoc querying" — [Honeycomb whitepaper (search result)](https://www.honeycomb.io/resources/whitepapers/bridge-from-observability1dot0-2dot0-logs-not-metrics); [charity.wtf Aug 2024 (search result)](https://charity.wtf/2024/08/). This is vendor advocacy, so present it as one view.
3. **Document.** "Elasticsearch serializes and stores data in the form of JSON documents. A document is a set of fields". Each document has an `_id`, and `_source` holds "the original document body as submitted" — [docs-content: index basics](https://github.com/elastic/docs-content/blob/main/manage-data/data-store/index-basics.md). *Intuition:* one log line is one JSON row.
4. **Index.** "To store a document, you add it to a specific index. To search, you target one or more indices". You can also target an alias or a data stream — [index basics](https://github.com/elastic/docs-content/blob/main/manage-data/data-store/index-basics.md). *Intuition:* a named collection. In logging, usually one per day or one backing index per rollover.
5. **Mapping.** "Each index has a mapping that defines the data type for each field, how the field should be indexed, and how it should be stored". Mappings are explicit or dynamic — [index basics](https://github.com/elastic/docs-content/blob/main/manage-data/data-store/index-basics.md). "Defining too many fields in an index can lead to a mapping explosion, which can cause out of memory errors and difficult situations from which to recover" — [docs-content: mapping](https://github.com/elastic/docs-content/blob/main/manage-data/data-store/mapping.md). *Intuition:* the schema Elasticsearch infers from the first document it sees. It guesses, and the guesses stick.
6. **Inverted index and near real-time search.** Elasticsearch is built on Lucene. "A *segment* is similar to an inverted index". A document "is indexed and fully searchable in near real-time — within 1 second" — [docs-content: near real-time search](https://github.com/elastic/docs-content/blob/main/manage-data/data-store/near-real-time-search.md). *Intuition:* the index at the back of a book. Each word lists the pages it appears on, so a search never reads every page.
7. **Shards and replicas.** Each shard "is a self-contained Lucene index containing a subset of the documents". "Each document in an index belongs to one primary shard. A replica shard is a copy of a primary shard". "The number of primary shards in an index is fixed at the time that an index is created, but the number of replica shards can be changed at any time" — [docs-content: clusters, nodes, shards](https://github.com/elastic/docs-content/blob/main/deploy-manage/distributed-architecture/clusters-nodes-shards.md). *Intuition:* an encyclopedia split into volumes (shards), with a photocopy of each volume kept in another building (replicas).
8. **Nodes and cluster.** "You can add servers (*nodes*) to a cluster to increase capacity, and Elasticsearch automatically distributes your data and query load across all of the available nodes". For learning, "you can use a cluster with a single node and create indices with only one shard" — [clusters, nodes, shards](https://github.com/elastic/docs-content/blob/main/deploy-manage/distributed-architecture/clusters-nodes-shards.md).
9. **The stack.** Kibana is "the user interface with dashboards, visualizations, and management tools". Logstash is "the data ingestion and transformation engine, often used for more complex ETL ... pipelines" — [docs-content: the stack](https://github.com/elastic/docs-content/blob/main/get-started/the-stack.md). Beats are "data shippers to send operational data to Elasticsearch directly or through Logstash". Elastic Agent with Fleet is the centrally managed option. Elastic also ships its own Distributions of OpenTelemetry (EDOT) — [docs-content: ingest tools](https://github.com/elastic/docs-content/blob/main/manage-data/ingest/tools.md).
10. **Elastic Agent now runs on OpenTelemetry.** According to Elastic's docs as summarised in search, "starting with version 9.2, Elastic Agent runs the Elastic Distribution of OpenTelemetry (EDOT) Collector", and Beat inputs run as receivers inside it. The search summary noted that sources disagree on whether some parts became GA in 9.2 or 9.3 — [Elastic: Elastic Agent as an OTel Collector (search result)](https://www.elastic.co/docs/reference/fleet/elastic-agent-as-otel-collector); [Elastic: Beats vs Agent comparison (search result)](https://elastic.co/guide/en/fleet/current/beats-agent-comparison.html). The `start-local` script can install the EDOT Collector with `--edot` — [elastic/start-local README](https://github.com/elastic/start-local/blob/main/README.md).
11. **Fluentd and Fluent Bit (the "F" in EFK).** Both are CNCF graduated projects. The comparison table:

    | | Fluentd | Fluent Bit |
    |---|---|---|
    | Language | C and Ruby | C |
    | Memory | "Greater than 60 MB" | "Approximately 450 KB" |
    | Plugins | "Over 1,000 external plugins" | "Over 100 built-in plugins" |
    | OpenTelemetry | through plugins | "Native OTLP ingestion and delivery" |

    Source: [fluent-bit-docs: Fluentd and Fluent Bit](https://github.com/fluent/fluent-bit-docs/blob/master/about/fluentd-and-fluent-bit.md).
12. **Kibana Discover and its query languages.** "Discover has two query modes. ES|QL mode doesn't require a data view. Classic mode uses data views with KQL or Lucene" — [docs-content: Discover](https://github.com/elastic/docs-content/blob/main/explore-analyze/discover.md). KQL is "a text-based language for filtering data". A condition is "a field name, an operator, and a value, such as `http.request.method: GET`". "By default, the query bar of dashboards and of Discover in classic mode uses KQL." Examples from the doc: `http.response.status_code: (400 OR 401 OR 404)`, `machine.os: win*`, `response: 200 OR extension: php` — [docs-content: KQL](https://github.com/elastic/docs-content/blob/main/explore-analyze/query-filter/languages/kql.md). ES|QL is piped. The doc's example is `FROM kibana_sample_data_logs | WHERE response.keyword == "200" | STATS total_bytes = SUM(bytes) BY geo.dest`, and ES|QL works in Discover, dashboards, alerting and the Dev Tools Console — [docs-content: ES|QL in Kibana](https://github.com/elastic/docs-content/blob/main/explore-analyze/query-filter/languages/esql-kibana.md). *Intuition:* KQL is a filter box. ES|QL is a Unix pipeline over your logs.
13. **Licence history.**
    - Elasticsearch and Kibana were Apache 2.0 until January 2021. Elastic then moved to a dual Elastic License / SSPL licence, neither of which is open source. Its stated aim was to stop cloud providers offering the products as a service. AWS responded with the Apache-2.0 OpenSearch fork — [ITmedia via search summary (search result)](https://atmarkit.itmedia.co.jp/ait/articles/2409/03/news049.html).
    - In August 2024 Elastic added AGPLv3 as a third option alongside SSPL 1.0 and ELv2. The change does not affect existing users and makes "no change to Elastic's binary distributions". Client libraries stay Apache 2.0 — [BusinessWire announcement (search result)](https://www.businesswire.com/news/home/20240829537786/en/Elastic-Announces-Open-Source-License-Elasticsearch-Kibana); [IT Brief (search result)](https://itbrief.co.uk/story/elastic-adds-agpl-option-to-elasticsearch-kibana-licences); [DevClass (search result)](https://devclass.com/2024/09/02/elasticsearch-will-be-open-source-again-as-cto-declares-changed-landscape/).
    - The current repo LICENSE.txt says source is "a triple license under the 'GNU Affero General Public License v3.0 only', 'the Server Side Public License, v 1', and the 'Elastic License 2.0'". Code "licensed solely under the 'Elastic License 2.0' is found only in the x-pack folder" — [elastic/elasticsearch LICENSE.txt](https://github.com/elastic/elasticsearch/blob/main/LICENSE.txt).
14. **OpenSearch.** It joined the Linux Foundation in September 2024 through the new OpenSearch Software Foundation. OpenSearch 3.0 went GA on 6 May 2025, with Lucene 10 and Java 21 as the minimum — [opensearch.org blog (search result)](https://opensearch.org/blog/unveiling-opensearch-3-0/); [DevClass (search result)](https://devclass.com/2025/05/07/opensearch-3-0-hits-first-major-release-under-linux-foundation-as-it-battles-elasticsearch-for-mindshare/). The repo licence is Apache 2.0 — [OpenSearch LICENSE.txt](https://github.com/opensearch-project/OpenSearch/blob/main/LICENSE.txt). The latest tag is 3.9.0, dated 2026-09-22 — [git ls-remote opensearch-project/OpenSearch](https://github.com/opensearch-project/OpenSearch). One secondary source contrasts OpenSearch with "Elasticsearch's shift to the AGPLv3". That is inaccurate: AGPL was *added* as an option, not substituted — [DevClass (search result)](https://devclass.com/2025/05/07/opensearch-3-0-hits-first-major-release-under-linux-foundation-as-it-battles-elasticsearch-for-mindshare/) vs [LICENSE.txt](https://github.com/elastic/elasticsearch/blob/main/LICENSE.txt).

**Misconceptions to address (L1)**
- "Shards are free, so make many." Too many shards "can degrade search performance and make the cluster unstable", which is called *oversharding*. Aim for shards of 10–50 GB with fewer than 200M documents each. Each search uses one CPU thread per shard, so many shards drain the search thread pool. Master-eligible nodes need about 1 GB of heap per 3,000 indices — [docs-content: size your shards](https://github.com/elastic/docs-content/blob/main/deploy-manage/production-guidance/optimize-performance/size-shards.md).
- "I can change the primary shard count later." No. It is fixed at creation. Only the replica count is dynamic — [clusters, nodes, shards](https://github.com/elastic/docs-content/blob/main/deploy-manage/distributed-architecture/clusters-nodes-shards.md).
- "Indexed means instantly searchable." Search is near real-time, within about 1 s after a refresh — [near real-time search](https://github.com/elastic/docs-content/blob/main/manage-data/data-store/near-real-time-search.md).
- "AGPL replaced the Elastic licence." No. It is a third option, and the binaries did not change — [LICENSE.txt](https://github.com/elastic/elasticsearch/blob/main/LICENSE.txt); [BusinessWire (search result)](https://www.businesswire.com/news/home/20240829537786/en/Elastic-Announces-Open-Source-License-Elasticsearch-Kibana).
- "Logstash is required." No. Beats and Agent can ship straight to Elasticsearch, and Fluent Bit has a native `es` output — [ingest tools](https://github.com/elastic/docs-content/blob/main/manage-data/ingest/tools.md); [fluent-bit-docs: Elasticsearch output](https://github.com/fluent/fluent-bit-docs/blob/master/pipeline/outputs/elasticsearch.md).

**Example commands and queries (L1)**, all [author example, untested]. They assume the lab stack from Lesson 2 with security disabled at `http://localhost:9200`.
```bash
# 1. Cluster and node
curl -s localhost:9200                         # JSON with cluster_name and version.number "9.5.5"
curl -s 'localhost:9200/_cat/health?v'         # expect status green (or yellow, see below)

# 2. Create an index with explicit shard/replica counts
curl -s -X PUT localhost:9200/demo-logs -H 'Content-Type: application/json' -d '{
  "settings": {"number_of_shards": 1, "number_of_replicas": 1},
  "mappings": {"properties": {
    "@timestamp": {"type": "date"}, "level": {"type": "keyword"},
    "service": {"type": "keyword"}, "message": {"type": "text"}}}}'
curl -s 'localhost:9200/_cat/health?v'   # on 1 node: status "yellow", because the replica cannot sit on the same node as its primary
curl -s -X PUT localhost:9200/demo-logs/_settings -H 'Content-Type: application/json' -d '{"number_of_replicas":0}'
# health goes back to green (teaches: replica count is dynamic, primary count is not)

# 3. Index a structured log event
curl -s -X POST localhost:9200/demo-logs/_doc -H 'Content-Type: application/json' -d '{
  "@timestamp":"2026-10-30T10:00:00Z","level":"ERROR","service":"checkout",
  "message":"Payment FAILED for order 42: card declined"}'
# response: "result":"created" plus an auto-generated _id

# 4. See the inverted index tokens (the "back-of-book index")
curl -s -X POST localhost:9200/_analyze -H 'Content-Type: application/json' -d '{
  "analyzer":"standard","text":"Payment FAILED for order 42"}'
# tokens: payment, failed, for, order, 42  (lowercased, split on word boundaries)

# 5. Dynamic mapping guesses: index a doc with a new field, then inspect
curl -s -X POST localhost:9200/demo-logs/_doc -H 'Content-Type: application/json' -d '{"@timestamp":"2026-10-30T10:01:00Z","duration_ms":"120"}'
curl -s 'localhost:9200/demo-logs/_mapping?pretty'   # duration_ms is mapped as text + keyword subfield, NOT a number
```
KQL in Discover (classic mode), using the Lesson 2 data:
- `level: ERROR and service: checkout` returns only error events from checkout.
- `not level: (DEBUG or INFO)`
- `message: "card declined"` is a phrase match on a `text` field.

ES|QL in Discover:
```
FROM app-logs-*
| WHERE level == "ERROR"
| STATS errors = COUNT(*) BY service
| SORT errors DESC
| LIMIT 10
```
Expected result: a two-column table (`errors`, `service`) with one row per service, highest count first.

**Hands-on exercise ideas (L1)**
1. "Grep vs index": run three containers that log to stdout. Find one error with `docker logs` across all three, then find it in Kibana. Talk about why the second is easier.
2. Run `_analyze` on the same sentence with the `standard` and `keyword` analyzers. Explain why `level` should be `keyword` and `message` should be `text`.
3. Watch dynamic mapping go wrong: send `"status":"200"` first and `"status":200` later, or the reverse, to a fresh index. Inspect `_mapping`, then fix it with an explicit mapping.
4. Make the cluster yellow, then green, by changing `number_of_replicas` on a single node.
5. Write the same question ("errors per service in the last 15 min") in KQL with a visualization, and again in ES|QL.

**Curated resources (L1)**
- Elastic docs, Index basics: [docs-content source](https://github.com/elastic/docs-content/blob/main/manage-data/data-store/index-basics.md). Published under www.elastic.co/docs/manage-data/data-store/index-basics (pattern-derived, not opened).
- Elastic docs, Clusters, nodes, and shards: [source](https://github.com/elastic/docs-content/blob/main/deploy-manage/distributed-architecture/clusters-nodes-shards.md); and Size your shards: [source](https://github.com/elastic/docs-content/blob/main/deploy-manage/production-guidance/optimize-performance/size-shards.md)
- Elastic docs, KQL: [source](https://github.com/elastic/docs-content/blob/main/explore-analyze/query-filter/languages/kql.md); ES|QL in Kibana: [source](https://github.com/elastic/docs-content/blob/main/explore-analyze/query-filter/languages/esql-kibana.md)
- Fluentd vs Fluent Bit comparison: [fluent-bit-docs](https://github.com/fluent/fluent-bit-docs/blob/master/about/fluentd-and-fluent-bit.md)
- Licence-change read: [DevClass, 2 Sep 2024 (search result)](https://devclass.com/2024/09/02/elasticsearch-will-be-open-source-again-as-cto-declares-changed-landscape/)
- Video (search result, channel unverified): "What is ELK Stack in 100 Seconds?" https://www.youtube.com/watch?v=u_GzDkrq5m4
- Video (search result, channel unverified): "Explore and query your Kibana data with Discover" https://www.youtube.com/watch?v=b4Edz_ybA_8
- Video (search result, channel unverified): "Kibana Query Language (KQL) Tutorial for Beginners" https://www.youtube.com/watch?v=tXTg48wxzt0

### Inferences
- The yellow-cluster demo is the most memorable way to teach replicas. A replica is never placed on the same node as its primary, so a one-node lab with `number_of_replicas: 1` stays yellow. This is standard Elasticsearch behaviour, but I did not open a doc page stating it this session.
- Log levels (DEBUG/INFO/WARN/ERROR/FATAL) and "log at INFO in production, DEBUG only when diagnosing" are general practice. I did not open an authoritative page on them in this session, so treat them as background knowledge. The OTel logs data model has a severity field that could serve as a citation.
- Teach ES|QL as the primary Discover language and KQL as the filter-bar language. In the 9.x docs ES|QL appears everywhere (Discover, dashboards, alerting, and the Observability logs and traces views), and Discover calls the KQL mode "classic".
- Present OpenSearch as "the Apache-2.0 fork, now under the Linux Foundation". Its Dashboards UI and query support are close enough that Lesson 1 concepts carry over. I did not verify OpenSearch's ES|QL equivalent (PPL/SQL).

### Gaps
- I could not open the official elastic.co blog post on AGPL ("Elasticsearch is open source, again"). The DNS lookup for www.elastic.co failed in the sandbox, so the licence history above rests on the repo LICENSE.txt plus press coverage.
- I did not confirm the default `index.mapping.total_fields.limit` value (commonly 1,000) against the docs this session. The mapping page only says to "use the mapping limit settings".
- No authoritative source checked for the exact Logstash resource footprint (JVM-based, so heavier than Fluent Bit). The comparison here is limited to Fluentd vs Fluent Bit.

---

## Lesson 2 blueprint: Running EFK and working with logs (lab, Kubernetes DaemonSet, templates, data streams, ILM, dashboards, alerts, cost, Loki)

### Takeaway
Build a local Docker Compose lab: Elasticsearch 9.5.5 + Kibana 9.5.5 + Fluent Bit 5.1.5, with an app container using Docker's `fluentd` logging driver. On a Mac, Docker Desktop keeps container log files inside its Linux VM, so the logging driver is easier than tailing files. Then explain the Kubernetes form: a Fluent Bit DaemonSet installed by Helm that tails `/var/log/containers/*.log` with the `docker,cri` multiline parsers and enriches records with the `kubernetes` filter. Finish with lifecycle and cost:
- index templates
- data streams (with logsdb on by default for new `logs-*-*` streams in 9.x)
- ILM or data-stream-lifecycle retention
- the Loki model: index labels only and keep chunks in object storage, which is cheaper but has no full-text index

### Cited Findings

**Fluent Bit pipeline and Kubernetes deployment**
- **Deployment.** Fluent Bit "should be deployed as a DaemonSet". The recommended install is the Helm chart: `helm repo add fluent https://fluent.github.io/helm-charts`, then `helm upgrade --install fluent-bit fluent/fluent-bit` — [fluent-bit-docs: Kubernetes](https://github.com/fluent/fluent-bit-docs/blob/master/installation/downloads/kubernetes.md).
- **What the default chart does** (same doc):
  - parses container logs with the `docker` or `cri` multiline parser
  - remembers how far it read each file, so a restarted pod "picks up from where it left off"
  - adds Kubernetes `labels` and `annotations`, using a cache and contacting the API server only on a cache miss
  - outputs to Elasticsearch "in Logstash format"
  - sets `Retry_Limit False`, so it "will retry indefinitely"
- **Where the metadata comes from.** The kubernetes filter gets `pod_id`, `labels` and `annotations` from the API server. `pod_name`, `container_id` and `container_name` come "locally from the log file names" — [same doc](https://github.com/fluent/fluent-bit-docs/blob/master/installation/downloads/kubernetes.md).
- **Kubernetes filter options** — [fluent-bit-docs: kubernetes filter](https://github.com/fluent/fluent-bit-docs/blob/master/pipeline/filters/kubernetes.md):
  - `merge_log` (default Off): "check if the `log` field content is a JSON string map. If it's, append the map fields as part of the log structure"
  - `merge_log_key` nests those fields under a key
  - `keep_log` (default On) controls whether the raw `log` string is kept
  - `labels` and `annotations` default On
  - `k8s-logging.exclude` lets pods opt out with the annotation `fluentbit.io/exclude`
  - `use_kubelet` fetches metadata from the kubelet to reduce API-server load in large clusters
- **Tail input.** `multiline.parser: docker, cri` "helps reassemble large messages originally split by Docker or CRI". It tries `docker` first and then `cri` — [fluent-bit-docs: tail](https://github.com/fluent/fluent-bit-docs/blob/master/pipeline/inputs/tail.md).
- **Fluent Bit 5.x changes:**
  - 5.0: a refactored shared HTTP listener stack, plus a "unified processing and delivery model" for logs, metrics and traces
  - 5.1: multi-worker TCP/UDP/Forward inputs, an input rate gate, FIPS mode, automatic TLS certificate reload, a GCS output, and `elasticsearch` added as an alias of the `es` output name

  Source: [fluent-bit-docs: What's new in v5](https://github.com/fluent/fluent-bit-docs/blob/master/installation/whats-new-in-fluent-bit-v5.md).
- **Upgrade notes.** 5.1.3 fixed `tls.verify_client_cert` being ignored when combined with `tls.verify off`. From 5.0.4, the forward output's `retain_metadata_in_forward_mode` defaults to `true` — [fluent-bit-docs: upgrade notes](https://github.com/fluent/fluent-bit-docs/blob/master/installation/upgrade-notes.md).

**Elasticsearch output gotchas** — [fluent-bit-docs: Elasticsearch output](https://github.com/fluent/fluent-bit-docs/blob/master/pipeline/outputs/elasticsearch.md)
- `suppress_type_name` defaults to Off, but "Elasticsearch 8.0.0 or higher no longer supports mapping types". Without it you get `"Action/metadata line [1] contains an unknown parameter [_type]"` (HTTP 400). **Set `suppress_type_name on` for ES 8/9.**
- `logstash_format on` writes to `<logstash_prefix>-YYYY.MM.DD` (default prefix `logstash`) and adds an `@timestamp` field (`time_key`). Without `logstash_format`, the `index` default is `fluent-bit`.
- `write_operation` defaults to `create`. `generate_id` or `id_key` prevents duplicates on retry. Partial bulk failures are retried with only the rejected documents. Since 5.1.3, `drop_unrecoverable_records on` drops 4xx rejections such as mapping conflicts instead of retrying them forever.
- `trace_error on` logs the request and response of failed bulk calls. This is the first thing to switch on when "nothing shows up in Kibana".
- `logstash_prefix_key $kubernetes['namespace_name']` creates per-namespace indices. This is useful but multiplies the index count (see the shard misconception below).
- In YAML, quote strftime values that begin with `%`, for example `logstash_dateformat: "%Y.%m.%d"`.

**Docker logging driver (Mac lab path)**
- The `fluentd` logging driver sends `container_id`, `container_name`, `source` (stdout/stderr) and `log` (the message). It connects to `localhost:24224` by default, or to `fluentd-address`. "If container cannot connect to the Fluentd daemon, the container stops immediately unless the `fluentd-async` option is used." `tag` supports Go templates such as `{{.Name}}` — [docker/docs: fluentd driver](https://github.com/docker/docs/blob/main/content/manuals/engine/logging/drivers/fluentd.md).
- The Fluent Bit `forward` input implements the Fluentd Forward protocol and listens on TCP 24224 by default — [fluent-bit-docs: forward input](https://github.com/fluent/fluent-bit-docs/blob/master/pipeline/inputs/forward.md).

**Index templates, data streams, logsdb, lifecycle**
- **Data streams.** A data stream is "a layer of abstraction over a set of indices that are optimized for storing append-only time series data". Its rules:
  - It "requires a matching index template".
  - "Every document indexed to a data stream must contain a `@timestamp` field".
  - Only the newest backing index (the write index) takes new documents.

  If you overwrite documents by the same `_id`, use an alias with a write index instead — [docs-content: data streams](https://github.com/elastic/docs-content/blob/main/manage-data/data-store/data-streams.md).
- **logsdb.** Logsdb index mode "reduced the storage footprint of log data by up to 60%, with a small impact (10-20%) to indexing performance" in benchmarks. "As of Elasticsearch version 9.0, logsdb mode is automatically set on **new** data streams with names matching the `logs-*-*` pattern". Existing 8.x streams are not converted. A `logsdb_columnar` mode also exists — [docs-content: logs data stream](https://github.com/elastic/docs-content/blob/main/manage-data/data-store/data-streams/logs-data-stream.md).
- **ILM.** ILM moves indices through `hot`, `warm`, `cold`, `frozen` and `delete` phases. Rollover "creates a new write index when the current one reaches a certain size, number of docs, or age". The doc's example ends with "Delete the index once the required 30 day retention period is reached". Data streams are "our recommended option" over managing plain indices — [docs-content: ILM](https://github.com/elastic/docs-content/blob/main/manage-data/lifecycle/index-lifecycle-management.md).
- **Data stream lifecycle.** A "simpler lifecycle management tool" that configures retention without data tiers. It ensures data is kept "at least for the retention time you defined" and deletes older data. In 9.5+ it can move old backing indices to low-cost searchable storage — [docs-content: data stream lifecycle](https://github.com/elastic/docs-content/blob/main/manage-data/lifecycle/data-stream.md); [ILM page](https://github.com/elastic/docs-content/blob/main/manage-data/lifecycle/index-lifecycle-management.md).
- **Rollover sizing.** With ILM, set rollover `max_primary_shard_size: 50gb` and `min_primary_shard_size: 10gb` — [size your shards](https://github.com/elastic/docs-content/blob/main/deploy-manage/production-guidance/optimize-performance/size-shards.md).

**Kibana alerts**
- The **Elasticsearch query** rule type "runs a user-configured query, compares the number of matches to a configured threshold, and schedules actions". It accepts Query DSL, ES|QL, KQL or Lucene. Aggregations are `count`, `average`, `sum`, `min` and `max`, with optional grouping on up to four fields — [docs-content: ES query rule](https://github.com/elastic/docs-content/blob/main/explore-analyze/alerting/alerts/rule-type-es-query.md).
- Rules run on a schedule, create alerts and trigger actions through *connectors* — [docs-content: alerts](https://github.com/elastic/docs-content/blob/main/explore-analyze/alerting/alerts.md). "Some connector types are paid commercial features, while others are free" — [docs-content: manage connectors](https://github.com/elastic/docs-content/blob/main/deploy-manage/manage-connectors.md).
- A newer "alerting v2" system with separate base, alert and recovery queries is marked `stack: ga 9.6+`, so it is not yet in the 9.5.5 release — [ES|QL in Kibana](https://github.com/elastic/docs-content/blob/main/explore-analyze/query-filter/languages/esql-kibana.md).

**Loki vs Elasticsearch**
- Loki "does not index the contents of the logs, but only indexes metadata about your logs as a set of labels for each log stream". Data is "compressed and stored in chunks in an object store such as Amazon S3 or GCS". "The compressed chunks, smaller index, and use of low-cost object storage, make Loki less expensive to operate". The query language is LogQL, which feels like PromQL — [grafana/loki docs: overview](https://github.com/grafana/loki/blob/main/docs/sources/get-started/overview.md).
- Fields such as `userId`, `shoppingCartId` and `orderId` are "high-cardinality" and are a problem as Loki labels — [grafana/loki docs: cardinality](https://github.com/grafana/loki/blob/main/docs/sources/get-started/labels/cardinality.md).
- Loki is AGPLv3 ([LICENSE](https://github.com/grafana/loki/blob/main/LICENSE)). The latest tag is v3.7.9, dated 2026-10-20 ([git ls-remote grafana/loki](https://github.com/grafana/loki)).

**Minimal lab files (L2)** [author example, untested; built from the docs cited above]

`compose.yaml` (LOCAL LAB ONLY, security off):
```yaml
services:
  elasticsearch:
    image: docker.elastic.co/elasticsearch/elasticsearch:9.5.5
    environment:
      - discovery.type=single-node
      - xpack.security.enabled=false        # lab only; start-local keeps security on
      - ES_JAVA_OPTS=-Xms1g -Xmx1g
    ports: ["9200:9200"]
    mem_limit: 2g
  kibana:
    image: docker.elastic.co/kibana/kibana:9.5.5
    environment:
      - ELASTICSEARCH_HOSTS=http://elasticsearch:9200
    ports: ["5601:5601"]
    depends_on: [elasticsearch]
  fluent-bit:
    image: cr.fluentbit.io/fluent/fluent-bit:5.1.5
    volumes: ["./fluent-bit.yaml:/fluent-bit/etc/fluent-bit.yaml:ro"]
    command: ["-c", "/fluent-bit/etc/fluent-bit.yaml"]
    ports: ["24224:24224"]          # the Docker daemon (not the compose network) dials this
    depends_on: [elasticsearch]
  app:
    image: busybox:1.36
    command: ["sh","-c","i=0; while true; do i=$$((i+1)); echo \"{\\\"level\\\":\\\"INFO\\\",\\\"service\\\":\\\"checkout\\\",\\\"msg\\\":\\\"order $$i ok\\\"}\"; [ $$((i%5)) -eq 0 ] && echo \"{\\\"level\\\":\\\"ERROR\\\",\\\"service\\\":\\\"checkout\\\",\\\"msg\\\":\\\"payment failed for order $$i\\\"}\"; sleep 1; done"]
    logging:
      driver: fluentd
      options:
        fluentd-address: localhost:24224
        fluentd-async: "true"
        tag: app.{{.Name}}
    depends_on: [fluent-bit]
```
`fluent-bit.yaml`:
```yaml
service:
  flush: 1
  log_level: info
parsers:
  - name: app_json
    format: json
pipeline:
  inputs:
    - name: forward
      listen: 0.0.0.0
      port: 24224
  filters:
    - name: parser            # turn the JSON string in "log" into fields
      match: 'app.*'
      key_name: log
      parser: app_json
      reserve_data: on        # keep container_name, source, etc.
  outputs:
    - name: es
      match: 'app.*'
      host: elasticsearch
      port: 9200
      logstash_format: on     # daily index app-logs-YYYY.MM.DD + @timestamp
      logstash_prefix: app-logs
      suppress_type_name: on  # REQUIRED for Elasticsearch 8/9
      trace_error: on
    - name: stdout            # debug: see what Fluent Bit emits
      match: '*'
```
Expected output:
- `docker compose logs fluent-bit` shows records like `[{"level":"ERROR","service":"checkout","msg":"payment failed for order 5","container_name":"/<project>-app-1","source":"stdout",...}]`.
- `curl 'localhost:9200/_cat/indices/app-logs-*?v'` shows `app-logs-2026.10.30`, with `docs.count` going up.
- In Kibana, create a data view `app-logs-*` with time field `@timestamp`. Discover then shows `level`, `service` and `msg` as separate fields.

Kubernetes variant of the pipeline (core from the [kubernetes filter doc](https://github.com/fluent/fluent-bit-docs/blob/master/pipeline/filters/kubernetes.md), output from the [ES output doc](https://github.com/fluent/fluent-bit-docs/blob/master/pipeline/outputs/elasticsearch.md)):
```yaml
pipeline:
  inputs:
    - name: tail
      tag: kube.*
      path: /var/log/containers/*.log
      multiline.parser: docker,cri
  filters:
    - name: kubernetes
      match: 'kube.*'
      kube_url: https://kubernetes.default.svc:443
      kube_ca_file: /var/run/secrets/kubernetes.io/serviceaccount/ca.crt
      kube_token_file: /var/run/secrets/kubernetes.io/serviceaccount/token
      kube_tag_prefix: kube.var.log.containers.
      merge_log: on
      merge_log_key: log_processed
      k8s-logging.exclude: on
  outputs:
    - name: es
      match: 'kube.*'
      host: <elasticsearch host>     # for a kind cluster + compose ES on a Mac, try host.docker.internal (untested)
      port: 9200
      logstash_format: on
      logstash_prefix: k8s-logs
      suppress_type_name: on
```

Retention [author example, untested; API shapes are from memory and need checking]:
```
PUT _ilm/policy/app-logs-7d
{"policy":{"phases":{"hot":{"actions":{}},"delete":{"min_age":"7d","actions":{"delete":{}}}}}}

PUT _index_template/app-logs
{"index_patterns":["app-logs-*"],
 "template":{"settings":{"number_of_shards":1,"number_of_replicas":0,"index.lifecycle.name":"app-logs-7d"},
  "mappings":{"properties":{"@timestamp":{"type":"date"},"level":{"type":"keyword"},
    "service":{"type":"keyword"},"msg":{"type":"text"}}}}}
```
Expected: new daily indices get 1 shard and 0 replicas (cluster green), and are deleted after 7 days. `GET app-logs-*/_ilm/explain` shows the phase.

**Misconceptions (L2)**
- **"Keep logs forever."** Use ILM delete phases or data-stream retention. The doc's own example deletes at 30 days — [ILM](https://github.com/elastic/docs-content/blob/main/manage-data/lifecycle/index-lifecycle-management.md).
- **"One index per app per namespace per day is tidy."** It multiplies small shards. Aim for 10–50 GB shards and keep under 3,000 indices per GB of master heap — [size your shards](https://github.com/elastic/docs-content/blob/main/deploy-manage/production-guidance/optimize-performance/size-shards.md). Compare with `logstash_prefix_key` per namespace in the [ES output doc](https://github.com/fluent/fluent-bit-docs/blob/master/pipeline/outputs/elasticsearch.md).
- **"Dynamic mapping is fine for everything."** Arbitrary JSON keys (user IDs as keys, request headers as keys) cause mapping explosions — [mapping](https://github.com/elastic/docs-content/blob/main/manage-data/data-store/mapping.md).
- **"`Retry_Limit False` is safe."** It retries forever, and before 5.1.3 a mapping-conflict 4xx was retried forever too — [K8s doc](https://github.com/fluent/fluent-bit-docs/blob/master/installation/downloads/kubernetes.md); [ES output doc](https://github.com/fluent/fluent-bit-docs/blob/master/pipeline/outputs/elasticsearch.md).
- **"Loki is just a cheaper Elasticsearch."** It indexes only labels, so a full-text search scans chunks. Putting high-cardinality values in labels breaks it — [Loki overview](https://github.com/grafana/loki/blob/main/docs/sources/get-started/overview.md); [cardinality](https://github.com/grafana/loki/blob/main/docs/sources/get-started/labels/cardinality.md).
- **"My app container failed to start, Docker is broken."** With the fluentd driver and no listener, the container stops unless `fluentd-async` is set — [docker/docs fluentd driver](https://github.com/docker/docs/blob/main/content/manuals/engine/logging/drivers/fluentd.md).

**Hands-on exercise ideas (L2)**
1. Bring up the compose lab. Break it on purpose by setting `suppress_type_name: off`, read the `_type` error with `trace_error: on`, then fix it.
2. Add an index template with explicit keyword mappings. Compare `_mapping` before and after.
3. Write an ILM policy with a 1-day delete, or for a live demo `min_age: 1m` with a short poll interval. Watch indices disappear.
4. Build a Kibana dashboard: errors over time (Lens bar chart split by `level`), a top-services table, and a saved Discover search.
5. Create an Elasticsearch query rule, "more than 3 ERROR docs in 1 minute", with a free connector such as Index or Server log. Confirm alerts fire.
6. Stretch: install `kind`, deploy Fluent Bit with Helm, add the annotation `fluentbit.io/exclude: "true"` to a chatty pod, and confirm its logs stop.
7. Stretch: run the same app against Grafana Loki and compare a LogQL label query with a full-text search.

**Curated resources (L2)**
- Fluent Bit, Kubernetes install: [source](https://github.com/fluent/fluent-bit-docs/blob/master/installation/downloads/kubernetes.md). docs.fluentbit.io has older versions of this page in search results, for example https://docs.fluentbit.io/manual/1.5/installation/kubernetes (outdated).
- Fluent Bit, Kubernetes filter: [source](https://github.com/fluent/fluent-bit-docs/blob/master/pipeline/filters/kubernetes.md); Elasticsearch output: [source](https://github.com/fluent/fluent-bit-docs/blob/master/pipeline/outputs/elasticsearch.md)
- Elastic, Data streams: [source](https://github.com/elastic/docs-content/blob/main/manage-data/data-store/data-streams.md); ILM: [source](https://github.com/elastic/docs-content/blob/main/manage-data/lifecycle/index-lifecycle-management.md); logsdb: [source](https://github.com/elastic/docs-content/blob/main/manage-data/data-store/data-streams/logs-data-stream.md)
- Grafana Loki overview (for the trade-off discussion): [source](https://github.com/grafana/loki/blob/main/docs/sources/get-started/overview.md)
- TechWorld with Nana, "Logging in K8s with Elasticsearch, Fluentd and Kibana | Complete Course" (Sept 2020; uses Fluentd, so dated): https://dev.to/techworld_with_nana/logging-in-k8s-with-elasticsearch-fluentd-and-kibana-complete-course-4gpa (search result; no YouTube URL surfaced)
- Video (search result, channel unverified, possibly older): "[Kube 34] Monitor Kubernetes Logs using EFK stack - Elasticsearch, FluentBit & Kibana" https://www.youtube.com/watch?v=8nWh1GLd7nY
- Video (search result): "Fluent Bit in 2022: Logs, Prometheus and OpenTelemetry - Eduardo Silva, Calyptia" (by Fluent Bit's creator; 2022) https://www.youtube.com/watch?v=qVjWu2WBinU

### Inferences
- On macOS, Docker Desktop runs containers in a Linux VM. Tailing `/var/lib/docker/containers` from a Fluent Bit container is fragile there. The `fluentd` logging driver with `forward` input on a published port 24224 is the more reliable lab path. The Docker daemon makes that connection, not the compose network, so the address should be `localhost:24224` rather than `fluent-bit:24224`. This follows from the driver doc's default of `localhost:24224`. Test it.
- Fluent Bit only adds `@timestamp` when `logstash_format` is on, and data streams require `@timestamp`. So the beginner lab should use `logstash_format` daily indices plus an ILM policy, and data streams should be taught conceptually. An untested trick to try: `logstash_format on`, `logstash_prefix logs-app`, `logstash_dateformat: default`. If strftime passes literals through, the index name becomes `logs-app-default`, which matches the built-in `logs-*-*` template and so creates a logsdb data stream. Verify before teaching.
- Simplest teaching story for cost: every GB is paid for at ingest (CPU), at storage (times 1 + replicas), and at retention (times days). Levers: drop DEBUG at the edge with a Fluent Bit filter, sample noisy health-check logs, shorten retention, logsdb (up to 60% less storage), fewer replicas for low-value logs, and Loki or object storage for "keep but rarely query" logs.
- For Kubernetes, a kind cluster plus the compose Elasticsearch outside it is lighter on a Mac than running Elasticsearch inside the cluster with ECK.

### Gaps
- I did not verify which Kibana connectors are free under the Basic licence. My belief is that Index and Server log are free and Slack, email and webhook need a paid tier, but the docs only say "some connector types are paid".
- I did not verify that ILM and data stream lifecycle are included in the free Basic licence. I believe they are, but did not confirm it.
- The Fluent Bit docs do not describe writing to Elasticsearch data streams. The default Helm chart's Elasticsearch host and index values (`values.yaml`) were not opened.
- No authoritative per-GB cost figures were found for log ingestion and storage. Treat cost as relative, not absolute.
- None of the lab files above were run in this session (no Docker in the sandbox).

---

## Lesson 3 blueprint: Distributed tracing with OpenTelemetry (concepts, misconceptions, examples, exercises, resources)

### Takeaway
Teach this order: why traces; trace, span and span context; context propagation with the W3C `traceparent` header; sampling (head vs tail, and the fact that the SDK default samples everything); the OpenTelemetry project (API vs SDK, zero-code vs manual instrumentation, OTLP on ports 4317 and 4318, the Collector's receivers, processors, exporters and pipelines); then backends. Jaeger v2 is itself built on the Collector, and v1 is end-of-life. Grafana Tempo 3.x needs only object storage. The lab: Flask app, `opentelemetry-instrument`, Jaeger all-in-one on `localhost:16686`.

### Cited Findings

**Concepts in teaching order**
1. **Span.** Spans have a span context, attributes, span events, span links, a status (`Unset`, `Error`, `Ok`; `Unset` means "completed without an error") and a kind (`Client`, `Server`, `Internal`, `Producer`, `Consumer`). "Internal spans represent operations which do not cross a process boundary" — [OTel docs: traces](https://github.com/open-telemetry/opentelemetry.io/blob/main/content/en/docs/concepts/signals/traces.md). *Intuition:* a labelled stopwatch with sticky notes (attributes and events) attached.
2. **Trace.** A tree of spans that share a `trace_id`. The root span has `parent_id: null`. In the getting-started console output, the Flask server span `/rolldice` has `"kind": "SpanKind.SERVER"` and `"parent_id": null`. The manual child span `roll` is `SpanKind.INTERNAL` with the same `trace_id` — [OTel Python getting started](https://github.com/open-telemetry/opentelemetry.io/blob/main/content/en/docs/languages/python/getting-started.md). *Intuition:* a parcel's tracking history. One tracking number (trace ID), with each depot scan (span) showing when it arrived, when it left, and anything that went wrong.
3. **Context propagation.** "The default propagator uses the headers specified by the W3C TraceContext specification". The trace ID and parent span ID travel in the `traceparent` header. The receiving service extracts it and injects it into its local context — [OTel docs: context propagation](https://github.com/open-telemetry/opentelemetry.io/blob/main/content/en/docs/concepts/context-propagation/index.md).
   - **Format:** `traceparent: 00-0af7651916cd43dd8448eb211c80319c-b7ad6b7169203331-01`, which is `version-traceid-parentid-traceflags`.
   - **Fields:** trace-id is 32 hex characters (16 bytes), parent-id is 16 hex characters (8 bytes), and neither may be all zeroes. trace-flags is 8 bits; `01` means sampled.

   Source: [W3C trace-context spec source](https://github.com/w3c/trace-context/blob/main/spec/20-http_request_header_format.md). *Intuition:* the tracking number printed on the parcel label. Every depot copies it onto the next label.
4. **Sampling.** "For high-volume systems, it is quite common for a sampling rate of 1% or lower to very accurately represent the other 99% of data." With head sampling, the decision is "made based on the trace ID and the desired percentage", so whole traces are kept. But "you cannot ensure that all traces with an error within them are sampled with head sampling alone". Tail sampling decides after seeing all or most spans, for example "always sampling traces that contain an error" or sampling by latency. The Tail Sampling Processor lives in collector-contrib — [OTel docs: sampling](https://github.com/open-telemetry/opentelemetry.io/blob/main/content/en/docs/concepts/sampling/index.md).
5. **SDK default sampler.** The default `OTEL_TRACES_SAMPLER` is `parentbased_always_on`, which means sample 100%. Options include `traceidratio` and `parentbased_traceidratio`, with `OTEL_TRACES_SAMPLER_ARG` setting the ratio — [OTel SDK config: general](https://github.com/open-telemetry/opentelemetry.io/blob/main/content/en/docs/languages/sdk-configuration/general.md).
6. **OTel in Python: API vs SDK, zero-code vs manual.** OpenTelemetry Python supports "Python 3.10 and higher" — [OTel Python index](https://github.com/open-telemetry/opentelemetry.io/blob/main/content/en/docs/languages/python/_index.md).
   - **Zero-code:** `pip install opentelemetry-distro`, then `opentelemetry-bootstrap -a install`, then `opentelemetry-instrument --traces_exporter console --metrics_exporter console --service_name dice-server flask run -p 8080`.
   - **Manual:** `tracer = trace.get_tracer("diceroller.tracer")`, then `with tracer.start_as_current_span("roll") as rollspan: rollspan.set_attribute("roll.value", res)`.

   Source: [OTel Python getting started](https://github.com/open-telemetry/opentelemetry.io/blob/main/content/en/docs/languages/python/getting-started.md). Every CLI flag has an `OTEL_` environment variable (`exporter_otlp_endpoint` becomes `OTEL_EXPORTER_OTLP_ENDPOINT`) — [zero-code Python configuration](https://github.com/open-telemetry/opentelemetry.io/blob/main/content/en/docs/zero-code/python/configuration.md). Example: `OTEL_SERVICE_NAME=... OTEL_TRACES_EXPORTER=console,otlp OTEL_EXPORTER_OTLP_TRACES_ENDPOINT=0.0.0.0:4317 opentelemetry-instrument python myapp.py` — [zero-code Python](https://github.com/open-telemetry/opentelemetry.io/blob/main/content/en/docs/zero-code/python/_index.md).
7. **SDK wiring in code.** `TracerProvider(resource=Resource.create({SERVICE_NAME: ...}))`, then `BatchSpanProcessor(OTLPSpanExporter(endpoint=...))`, then `trace.set_tracer_provider(...)`. Exporter packages are `opentelemetry-exporter-otlp-proto-grpc` and `-proto-http`. "Service name is required for most backends" — [OTel Python exporters](https://github.com/open-telemetry/opentelemetry.io/blob/main/content/en/docs/languages/python/exporters.md). The OTLP protocol default is "SDK-dependent, but will typically be either `http/protobuf` or `grpc`" — [OTel SDK config: OTLP exporter](https://github.com/open-telemetry/opentelemetry.io/blob/main/content/en/docs/languages/sdk-configuration/otlp-exporter.md).
8. **OTLP ports.** `4317` is OTLP over gRPC, "the default for most SDKs". `4318` is OTLP over HTTP. `55679` is ZPages, a debug UI. The core image is `otel/opentelemetry-collector` — [OTel Collector quick start](https://github.com/open-telemetry/opentelemetry.io/blob/main/content/en/docs/collector/quick-start.md).
9. **The Collector.** Config has `receivers` (e.g. `otlp` on 0.0.0.0:4317 and 4318), `processors` (e.g. `memory_limiter`, `attributes` with insert, delete and hash actions to scrub fields like `db.statement` and `email`, and `filter`), `exporters` (`otlp_grpc`, `otlp_http`, `debug`, `file`, `prometheus`, ...), `extensions` (`health_check`, `pprof`, `zpages`), and `service.pipelines` per signal (traces, metrics, logs). The current docs batch through the exporter's `sending_queue: batch:` setting — [OTel Collector configuration](https://github.com/open-telemetry/opentelemetry.io/blob/main/content/en/docs/collector/configuration.md). *Intuition:* a post-office sorting hub. Inbound docks are receivers, sorting and redacting are processors, outbound trucks are exporters.
10. **Exporter rename (recent).** In Collector v0.144.0 the `otlp` exporter was renamed `otlp_grpc` and `otlphttp` was renamed `otlp_http`. The old names remain as deprecated aliases — [opentelemetry-collector CHANGELOG](https://github.com/open-telemetry/opentelemetry-collector/blob/main/CHANGELOG.md). Most tutorials before 2026 use the old names.
11. **Jaeger v2.** Run it with `docker run --rm --name jaeger -p 16686:16686 -p 4317:4317 -p 4318:4318 -p 5778:5778 -p 9411:9411 cr.jaegertracing.io/jaegertracing/jaeger:<version>`. This is the all-in-one configuration with "transient in-memory storage", and the UI is at `http://localhost:16686`. The HotROD microservices demo runs with `docker compose` from `jaeger/examples/hotrod`. Storage backends include Cassandra, ClickHouse, Elasticsearch and OpenSearch — [Jaeger v2 getting started (docs source)](https://github.com/jaegertracing/documentation/blob/main/content/docs/v2/_dev/getting-started.md). The docs site's latest v2 version is 2.22, with binaries at 2.22.0; the v1 docs stop at 1.76 (docs repo `hugo.yaml`). The latest tag is v2.22.0 (2026-10-06); v2.0.0 was 2024-11-10 ([git ls-remote jaegertracing/jaeger](https://github.com/jaegertracing/jaeger)). Licence: Apache 2.0 ([LICENSE](https://github.com/jaegertracing/jaeger/blob/main/LICENSE)).
12. **Jaeger v1 end-of-life.** v1 reached end-of-life around 31 December 2025. v2 "is built on the OpenTelemetry Collector". Jaeger client libraries are retired in favour of OTel SDKs. The Collector dropped its Jaeger-format exporter, so send OTLP — [CNCF blog "Jaeger at 10" (search result)](https://cncf.io/blog/2025/09/01/jaeger-at-10-forged-in-community-reborn-in-opentelemetry); secondary summaries in the same search. The EOL date comes from secondary sources plus the CNCF post saying v1 would be fully deprecated in January 2026.
13. **Grafana Tempo.** "Tempo is cost-efficient and only requires an object storage to operate". It is queried with TraceQL, "inspired by PromQL and LogQL" — [Tempo docs index](https://github.com/grafana/tempo/blob/main/docs/sources/tempo/_index.md). Tempo 3.0 "replaces ingesters with a design that separates read and write paths". It uses Kafka in microservices mode but not in monolithic mode, moves from RF3 to RF1 (no 2–2.5x duplication), and makes TraceQL metrics GA — [Tempo v3.0 release notes](https://github.com/grafana/tempo/blob/main/docs/sources/tempo/release-notes/v3-0.md). v3.0.0 is dated 2026-05-28 and the latest is v3.1.1 (2026-10-21) ([git ls-remote grafana/tempo](https://github.com/grafana/tempo)). Licence: AGPLv3 ([LICENSE](https://github.com/grafana/tempo/blob/main/LICENSE)).
14. **Logs and traces together.** With Python logging auto-instrumentation (`OTEL_PYTHON_LOGGING_AUTO_INSTRUMENTATION_ENABLED=true`), log records carry `otelTraceID`, so a log line can be joined to its trace — [OTel zero-code Python logs example](https://github.com/open-telemetry/opentelemetry.io/blob/main/content/en/docs/zero-code/python/logs-example.md).

**Misconceptions (L3)**
- **"Leave sampling at the default in production."** The default is `parentbased_always_on`, which is 100% — [SDK config](https://github.com/open-telemetry/opentelemetry.io/blob/main/content/en/docs/languages/sdk-configuration/general.md). 1% often represents high-volume traffic well — [sampling](https://github.com/open-telemetry/opentelemetry.io/blob/main/content/en/docs/concepts/sampling/index.md).
- **"Head sampling at 1% will still catch my errors."** It will not reliably. Use tail sampling in a Collector to keep error and slow traces — [sampling](https://github.com/open-telemetry/opentelemetry.io/blob/main/content/en/docs/concepts/sampling/index.md).
- **"OpenTelemetry is a backend."** It is APIs, SDKs, instrumentation, the Collector and the OTLP protocol. Jaeger, Tempo and Elastic store and display the data — [Collector configuration](https://github.com/open-telemetry/opentelemetry.io/blob/main/content/en/docs/collector/configuration.md); [Jaeger getting started](https://github.com/jaegertracing/documentation/blob/main/content/docs/v2/_dev/getting-started.md).
- **"Install the Jaeger client library."** It is retired. Use the OTel SDK and send OTLP to Jaeger on 4317/4318 — [CNCF Jaeger at 10 (search result)](https://cncf.io/blog/2025/09/01/jaeger-at-10-forged-in-community-reborn-in-opentelemetry).
- **"My Flask debug server isn't producing spans."** The debug reloader can break instrumentation. Use `use_reloader=False` — [OTel zero-code Python example](https://github.com/open-telemetry/opentelemetry.io/blob/main/content/en/docs/zero-code/python/example.md).
- **"Traces vanished after restarting Jaeger."** All-in-one uses transient in-memory storage — [Jaeger getting started](https://github.com/jaegertracing/documentation/blob/main/content/docs/v2/_dev/getting-started.md).
- **"Copy-pasted Collector configs with `exporters: otlp:` are broken or correct."** Both are wrong. `otlp` is now a deprecated alias for `otlp_grpc` — [Collector CHANGELOG](https://github.com/open-telemetry/opentelemetry-collector/blob/main/CHANGELOG.md).
- **"Put PII in span attributes; it's only debug data."** Scrub it in the Collector with `attributes` processor actions (`delete`, `hash`) — [Collector configuration](https://github.com/open-telemetry/opentelemetry.io/blob/main/content/en/docs/collector/configuration.md). The OWASP list in the beginner-mistakes section applies to telemetry too.

**Lab (L3)** [author example, untested]
```bash
# Terminal 1: Jaeger v2 all-in-one (check that the tag format is 2.22.0 on cr.jaegertracing.io)
docker run --rm --name jaeger -p 16686:16686 -p 4317:4317 -p 4318:4318 \
  cr.jaegertracing.io/jaegertracing/jaeger:2.22.0

# Terminal 2: Flask app (app.py = the OTel getting-started dice app)
python3 -m venv venv && source venv/bin/activate
pip install flask opentelemetry-distro opentelemetry-exporter-otlp
opentelemetry-bootstrap -a install          # installs opentelemetry-instrumentation-flask etc.
export OTEL_SERVICE_NAME=dice-server
export OTEL_TRACES_EXPORTER=otlp
export OTEL_METRICS_EXPORTER=none
export OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4317
opentelemetry-instrument flask run -p 8080

# Terminal 3
for i in $(seq 20); do curl -s localhost:8080/rolldice; echo; done
```
Expected: in the Jaeger UI at http://localhost:16686, choose Service = `dice-server` and Find Traces. You should see 20 traces, each with a `GET /rolldice` server span, plus a child `roll` span if the manual span from the docs is added. Propagation demo: add a second Flask service that calls the first with `requests` (auto-instrumented). Then one trace spans two services, and `request.headers['traceparent']` printed in service B matches the trace ID shown in Jaeger.

Optional Collector hop (`otel/opentelemetry-collector-contrib` image, so tail sampling is available) [author example, untested]:
```yaml
receivers:
  otlp:
    protocols:
      grpc: {endpoint: 0.0.0.0:4317}
      http: {endpoint: 0.0.0.0:4318}
processors:
  memory_limiter: {check_interval: 5s, limit_mib: 400, spike_limit_mib: 100}
  attributes/scrub:
    actions:
      - {key: email, action: hash}
  tail_sampling:
    decision_wait: 5s
    policies:
      - {name: errors, type: status_code, status_code: {status_codes: [ERROR]}}
      - {name: one-in-ten, type: probabilistic, probabilistic: {sampling_percentage: 10}}
exporters:
  otlp_grpc/jaeger:
    endpoint: jaeger:4317
    tls: {insecure: true}
  debug: {verbosity: basic}
service:
  pipelines:
    traces:
      receivers: [otlp]
      processors: [memory_limiter, attributes/scrub, tail_sampling]
      exporters: [otlp_grpc/jaeger, debug]
```
(The `tail_sampling` policy field names come from memory of collector-contrib and were not opened this session. Verify them against the tailsamplingprocessor README.)

**Hands-on exercise ideas (L3)**
1. Run the getting-started app with `--traces_exporter console` and read one span's JSON: find `trace_id`, `span_id`, `parent_id`, `kind` and attributes.
2. Point it at Jaeger and find the slowest trace. Add `time.sleep(random.random())` and a manual span to see where time goes.
3. Two services: print the `traceparent` header in service B and decode it by hand (version, trace ID, parent span ID, flags).
4. Set `OTEL_TRACES_SAMPLER=parentbased_traceidratio` and `OTEL_TRACES_SAMPLER_ARG=0.1`, fire 100 requests, and count traces in Jaeger. You should see about 10.
5. Raise an exception in 5% of requests. Compare head sampling at 10% with Collector tail sampling that keeps all errors.
6. Turn on `OTEL_PYTHON_LOGGING_AUTO_INSTRUMENTATION_ENABLED=true`, ship the logs to the Lesson 2 Elasticsearch, and search Kibana for a trace ID copied from Jaeger. This ties the three lessons together.
7. Stretch: run the Jaeger HotROD demo (`jaeger/examples/hotrod`) and find the injected latency culprit.

**Curated resources (L3)**
- OpenTelemetry Python getting started: [source](https://github.com/open-telemetry/opentelemetry.io/blob/main/content/en/docs/languages/python/getting-started.md) (published at opentelemetry.io/docs/languages/python/getting-started/; path from repo, not opened)
- OpenTelemetry sampling concepts: [source](https://github.com/open-telemetry/opentelemetry.io/blob/main/content/en/docs/concepts/sampling/index.md); context propagation: [source](https://github.com/open-telemetry/opentelemetry.io/blob/main/content/en/docs/concepts/context-propagation/index.md)
- OTel Collector configuration: [source](https://github.com/open-telemetry/opentelemetry.io/blob/main/content/en/docs/collector/configuration.md)
- Jaeger v2 getting started: [source](https://github.com/jaegertracing/documentation/blob/main/content/docs/v2/_dev/getting-started.md)
- W3C Trace Context header format: [spec source](https://github.com/w3c/trace-context/blob/main/spec/20-http_request_header_format.md). The published spec is https://www.w3.org/TR/trace-context/, a link that appears inside the OTel docs.
- Book: *Distributed Tracing in Practice* by Austin Parker, Daniel Spoonhower, Jonathan Mace, Ben Sigelman and Rebecca Isaacs (O'Reilly, April 2020), https://www.oreilly.com/library/view/distributed-tracing-in/9781492056621 (search result). It predates OpenTelemetry's maturity, so use it for concepts only.
- Video (search result, channel unverified): "Practical introduction to OpenTelemetry tracing" by Nicolas Frankel, https://www.youtube.com/watch?v=_vVh1dGGqKY
- Video (search result, channel unverified): "OpenTelemetry and Distributed Tracing in Python" https://www.youtube.com/watch?v=tmoCZHUOUgc
- Video (search result; KubeCon NA 2022 per search summary): "OpenTelemetry: The Vision, Reality, and How to Get Started" by Dotan Horovits, https://www.youtube.com/watch?v=qE1ggEmvz2Y
- Other video candidates from search, unverified: "Distributed Tracing Explained" https://www.youtube.com/watch?v=PmrSvsEJBUc ; "The Anatomy of a Distributed Trace" https://www.youtube.com/watch?v=yM2BiSo45M0 ; "OpenTelemetry: OpenTelemetry in Five Minutes" https://www.youtube.com/watch?v=l8xiNOCIdLY ; "Deploying the OpenTelemetry Collector on Kubernetes" https://youtube.com/watch?pp=ygUMI290ZWxwcm9qZWN0&v=X60owauFkGA. The `pp` parameter decodes to "#otelproject", which hints that this video may come from the OTel project's channel, but I did not confirm it.

### Inferences
- The most useful single demo is propagation across two services, shown as one waterfall in Jaeger. It makes the `traceparent` header concrete and justifies the whole topic.
- For a beginner course, skip the Collector in the first run (SDK straight to Jaeger) and add it as step two. Jaeger v2 is a Collector distribution, so the config vocabulary carries over.
- Version drift is the main trap with OTel material: renamed Collector exporters, the Jaeger v1-to-v2 change, and a batch processor that the docs now replace with exporter-side `sending_queue` batching. The lesson should pin versions: Collector v0.164.0, Python SDK 1.45.2, Jaeger 2.22.0.

### Gaps
- I could not open the tail-sampling processor README, so the policy YAML above needs checking.
- I did not confirm whether the `batch` processor is formally deprecated. The current docs examples simply use `sending_queue.batch` on exporters instead.
- No authoritative source checked for Jaeger image tag format (`2.22.0` vs `v2.22.0`) or for arm64 manifests of the Jaeger and Collector images.
- No official OpenTelemetry-channel or CNCF beginner video was confirmed. freeCodeCamp and KodeKloud tracing videos did not appear in search results.

---

## What intuitions help (an index as a book's back-of-book index; a trace as a parcel's tracking history; logs as events, metrics as aggregates)?

### Takeaway
All three suggested intuitions match the official definitions and are worth using. Add a few more: encyclopedia volumes and photocopies (shards and replicas), the notebook series where you only write in the newest one (data stream write index), the mail sorter in every building (Fluent Bit DaemonSet), the post-office hub (Collector), and the tracking number on the label (`traceparent`).

### Cited Findings
- **Back-of-book index.** Lucene's segment "is similar to an inverted index", and documents become searchable within about 1 s — [near real-time search](https://github.com/elastic/docs-content/blob/main/manage-data/data-store/near-real-time-search.md). Each shard is "a self-contained Lucene index" — [clusters, nodes, shards](https://github.com/elastic/docs-content/blob/main/deploy-manage/distributed-architecture/clusters-nodes-shards.md).
- **Parcel tracking.** A trace is spans sharing one `trace_id`, with parent and child links and kinds such as SERVER, CLIENT and INTERNAL — [OTel traces](https://github.com/open-telemetry/opentelemetry.io/blob/main/content/en/docs/concepts/signals/traces.md). The tracking number travels in the `traceparent` header: `00-<32 hex trace-id>-<16 hex parent-id>-<flags>` — [W3C spec](https://github.com/w3c/trace-context/blob/main/spec/20-http_request_header_format.md).
- **Logs as events, metrics as aggregates.** Majors: "You can derive metrics, or logs, or traces, but it's all the same data", and "aggregate at read time" — [Honeycomb whitepaper (search result)](https://www.honeycomb.io/resources/whitepapers/bridge-from-observability1dot0-2dot0-logs-not-metrics). The OTel primer says logs gain value when correlated with traces and spans — [primer](https://github.com/open-telemetry/opentelemetry.io/blob/main/content/en/docs/concepts/observability-primer.md).
- **Encyclopedia volumes and photocopies.** Primaries hold disjoint subsets of documents. A replica is a copy that "protects against hardware failure and increases capacity to serve read requests" — [clusters, nodes, shards](https://github.com/elastic/docs-content/blob/main/deploy-manage/distributed-architecture/clusters-nodes-shards.md).
- **Notebook series.** "The most recently created backing index is the data stream's write index. The stream adds new documents to this index only" — [data streams](https://github.com/elastic/docs-content/blob/main/manage-data/data-store/data-streams.md). ILM plays the archivist who moves old notebooks to cheaper shelves and then shreds them, through hot, warm, cold, frozen and delete — [ILM](https://github.com/elastic/docs-content/blob/main/manage-data/lifecycle/index-lifecycle-management.md).
- **Mail sorter in every building.** Fluent Bit is a DaemonSet, "a pod that runs on every node", and it stamps each letter with pod metadata — [Fluent Bit Kubernetes](https://github.com/fluent/fluent-bit-docs/blob/master/installation/downloads/kubernetes.md).
- **Library catalogue by shelf vs full index.** Loki indexes only labels, the shelf labels, and scans compressed chunks, while Elasticsearch indexes every word — [Loki overview](https://github.com/grafana/loki/blob/main/docs/sources/get-started/overview.md).
- **Opinion poll.** "A sampling rate of 1% or lower" can "very accurately represent the other 99%" for high-volume systems — [OTel sampling](https://github.com/open-telemetry/opentelemetry.io/blob/main/content/en/docs/concepts/sampling/index.md). Head sampling decides before reading the story; tail sampling decides after reading the ending.

### Inferences
- **Mapping as the first-impression schema.** The first document decides a field's type, and you cannot easily change it later. That is why `"duration_ms":"120"` gets mapped as text.
- **Tags in Fluent Bit as postal codes.** `match: 'app.*'` routes letters by their postcode. This is an inference from the tag/match config examples.
- **Spans as stopwatches with sticky notes.** Attributes and events are the notes. Status `Error` is a red sticker.

### Gaps
- No source states these analogies directly. They are teaching devices built on the cited definitions.

---

## What do beginners get wrong (unstructured logs, logging secrets, keeping logs forever, mapping explosions, too many shards, 100% trace sampling in production)?

### Takeaway
All six listed mistakes are real and documented. Add these:
- forgetting `suppress_type_name` with ES 8/9
- infinite Fluent Bit retries
- the container-stops-if-the-log-collector-is-down behaviour of Docker's fluentd driver
- the Flask debug reloader breaking instrumentation
- copying pre-2026 Collector configs (`otlp` and `otlphttp` exporter names, the removed Jaeger exporter)
- treating Jaeger all-in-one's in-memory store as persistent

### Cited Findings
- **Unstructured logs.** Fluent Bit can only turn the `log` string into fields when it is JSON (`merge_log`). Otherwise you need regex parsers — [Fluent Bit kubernetes filter](https://github.com/fluent/fluent-bit-docs/blob/master/pipeline/filters/kubernetes.md); [parser filter](https://github.com/fluent/fluent-bit-docs/blob/master/pipeline/filters/parser.md). Majors' case for wide structured events — [Honeycomb (search result)](https://www.honeycomb.io/resources/whitepapers/bridge-from-observability1dot0-2dot0-logs-not-metrics).
- **Logging secrets.** OWASP says these should usually not be recorded directly but "removed, masked, sanitized, hashed, or encrypted":
  - application source code
  - session identification values
  - access tokens
  - sensitive personal data and PII
  - authentication passwords
  - database connection strings
  - encryption keys and other primary secrets
  - bank account or payment card holder data
  - data classified higher than the logging system may store
  - commercially sensitive information
  - data collected without consent

  Source: [OWASP Logging Cheat Sheet (GitHub source)](https://github.com/OWASP/CheatSheetSeries/blob/master/cheatsheets/Logging_Cheat_Sheet.md). The related weakness is CWE-532, insertion of sensitive information into a log file — [MITRE EMB3D MID-084 (search result)](https://emb3d.mitre.org/mitigations/MID-084.html). The Collector `attributes` processor can `delete` or `hash` keys such as `email` and `db.statement` — [Collector configuration](https://github.com/open-telemetry/opentelemetry.io/blob/main/content/en/docs/collector/configuration.md).
- **Keeping logs forever.** ILM delete phase and retention — [ILM](https://github.com/elastic/docs-content/blob/main/manage-data/lifecycle/index-lifecycle-management.md). Data stream lifecycle retention — [DSL](https://github.com/elastic/docs-content/blob/main/manage-data/lifecycle/data-stream.md).
- **Mapping explosions.** "Too many fields ... can cause out of memory errors" — [mapping](https://github.com/elastic/docs-content/blob/main/manage-data/data-store/mapping.md). Every segment needs heap per mapped field, so high field counts and long field names add overhead — [size your shards](https://github.com/elastic/docs-content/blob/main/deploy-manage/production-guidance/optimize-performance/size-shards.md). The Loki equivalent is high-cardinality labels such as `userId` and `orderId` — [Loki cardinality](https://github.com/grafana/loki/blob/main/docs/sources/get-started/labels/cardinality.md).
- **Too many shards.** "Oversharding": aim for 10–50 GB per shard and fewer than 200M documents. "Searching a thousand 50MB shards will be substantially more expensive than searching a single 50GB shard" — [size your shards](https://github.com/elastic/docs-content/blob/main/deploy-manage/production-guidance/optimize-performance/size-shards.md).
- **100% trace sampling.** The default sampler is `parentbased_always_on` — [SDK config](https://github.com/open-telemetry/opentelemetry.io/blob/main/content/en/docs/languages/sdk-configuration/general.md). The sampling doc lists when to sample and when not to, and three costs of sampling (compute, engineering, opportunity) — [OTel sampling](https://github.com/open-telemetry/opentelemetry.io/blob/main/content/en/docs/concepts/sampling/index.md).
- **Extra mistakes:**
  - `_type` error without `suppress_type_name on` on ES 8+ — [ES output](https://github.com/fluent/fluent-bit-docs/blob/master/pipeline/outputs/elasticsearch.md)
  - `Retry_Limit False` retries forever — [Fluent Bit Kubernetes](https://github.com/fluent/fluent-bit-docs/blob/master/installation/downloads/kubernetes.md)
  - the container stops without `fluentd-async` — [docker fluentd driver](https://github.com/docker/docs/blob/main/content/manuals/engine/logging/drivers/fluentd.md)
  - Flask reloader — [OTel zero-code example](https://github.com/open-telemetry/opentelemetry.io/blob/main/content/en/docs/zero-code/python/example.md)
  - exporter rename in v0.144.0 — [Collector CHANGELOG](https://github.com/open-telemetry/opentelemetry-collector/blob/main/CHANGELOG.md)
  - in-memory Jaeger — [Jaeger getting started](https://github.com/jaegertracing/documentation/blob/main/content/docs/v2/_dev/getting-started.md)
  - Docker Desktop given less than 4 GB of memory — [Elastic Docker install](https://github.com/elastic/docs-content/blob/main/deploy-manage/deploy/self-managed/install-elasticsearch-docker-basic.md)

### Inferences
- Rank these for a 40-minute lesson by blast radius: secrets in logs (a security incident), no retention (cost and compliance), 100% sampling (cost), oversharding and mapping explosion (cluster instability), unstructured logs (lost time). The config gotchas fit better as a "troubleshooting" box in the lab.
- A good mnemonic slide: **"Structure it, scrub it, sample it, expire it."**

### Gaps
- No incident data or statistics were found on how often these mistakes occur in practice.

---

## What are the current versions and licences, which images run locally for free on an Apple Silicon Mac, how much memory do they need, and which registry (docker.elastic.co or Docker Hub official images) is the right choice?

### Takeaway
As of 30 October 2026, versions are newer than the brief assumed: **Fluent Bit is 5.1.x, not 4.x**, Tempo is 3.x, and Jaeger is 2.22. Everything in the lab is free:
- Elasticsearch and Kibana under the free Basic licence. The start-local trial reverts to Basic after a month.
- Fluent Bit and Jaeger under Apache 2.0.
- Loki and Tempo under AGPLv3.
- OpenSearch under Apache 2.0.

Elastic's docs use `docker.elastic.co` images. Docker Hub's official `elasticsearch` and `kibana` images are now built from Elastic's own `elastic/dockerfiles` repo, with Elastic employees as maintainers, and ship arm64v8. Either works, but **teach `docker.elastic.co` to match the docs**. Give Docker Desktop at least 4 GB of memory, and 6 to 8 GB if Elasticsearch, Kibana, Fluent Bit, Jaeger and an app run together.

### Cited Findings

**Version and licence table**
All versions verified with `git ls-remote --tags`; dates are tag commit dates.

| Component | Latest (Oct 2026) | Date | Notable earlier releases | Licence |
|---|---|---|---|---|
| Elasticsearch | 9.5.5 | 2026-09-30 | 9.5.0 on 2026-07-29; 9.0.0 on 2025-04-08 | AGPLv3 / SSPL / ELv2 triple; x-pack ELv2 only ([LICENSE.txt](https://github.com/elastic/elasticsearch/blob/main/LICENSE.txt)) |
| Kibana | 9.5.5 | — | — | Same model as Elasticsearch (per the AGPL announcement) |
| Fluent Bit | 5.1.5 | 2026-10-20 | 5.0.0 on 2026-03-24; 4.0.0 on 2025-04-01 | Apache 2.0 ([LICENSE](https://github.com/fluent/fluent-bit/blob/master/LICENSE)) |
| Fluentd | 1.20.1 | — | — | — |
| OpenSearch | 3.9.0 | 2026-09-22 | 3.0.0 tag 2025-04-29, GA announced 2025-05-06 | Apache 2.0 ([LICENSE.txt](https://github.com/opensearch-project/OpenSearch/blob/main/LICENSE.txt)) |
| OTel Collector releases | v0.164.0 | 2026-10-26 | — | — |
| Jaeger | v2.22.0 | 2026-10-06 | last v1 tag v1.76.0 | Apache 2.0 ([LICENSE](https://github.com/jaegertracing/jaeger/blob/main/LICENSE)) |
| Grafana Tempo | v3.1.1 | 2026-10-21 | 3.0.0 on 2026-05-28 | AGPLv3 ([LICENSE](https://github.com/grafana/tempo/blob/main/LICENSE)) |
| Grafana Loki | v3.7.9 | 2026-10-20 | — | AGPLv3 ([LICENSE](https://github.com/grafana/loki/blob/main/LICENSE)) |
| OTel Python SDK | v1.45.2 | 2026-10-29 | contrib instrumentation latest beta tag v0.66b0 | — |
| OTel spec | v1.62.0 | — | — | — |

Repos for the version checks: [elastic/elasticsearch](https://github.com/elastic/elasticsearch), [elastic/kibana](https://github.com/elastic/kibana), [fluent/fluent-bit](https://github.com/fluent/fluent-bit), [fluent/fluentd](https://github.com/fluent/fluentd), [opensearch-project/OpenSearch](https://github.com/opensearch-project/OpenSearch), [open-telemetry/opentelemetry-collector-releases](https://github.com/open-telemetry/opentelemetry-collector-releases), [jaegertracing/jaeger](https://github.com/jaegertracing/jaeger), [grafana/tempo](https://github.com/grafana/tempo), [grafana/loki](https://github.com/grafana/loki), [open-telemetry/opentelemetry-python](https://github.com/open-telemetry/opentelemetry-python), [open-telemetry/opentelemetry-python-contrib](https://github.com/open-telemetry/opentelemetry-python-contrib), [open-telemetry/opentelemetry-specification](https://github.com/open-telemetry/opentelemetry-specification). The Collector core changelog heading is "v1.70.0/v0.164.0" — [CHANGELOG](https://github.com/open-telemetry/opentelemetry-collector/blob/main/CHANGELOG.md).

The Elastic docs already describe some unreleased 9.6 features (marked `stack: ga 9.6+`), but no 9.6.0 tag exists yet — [ES|QL in Kibana](https://github.com/elastic/docs-content/blob/main/explore-analyze/query-filter/languages/esql-kibana.md).

**Images and registries**
- **Elastic.** The docs pull `docker.elastic.co/elasticsearch/elasticsearch:<version>` and `docker.elastic.co/kibana/kibana:<version>` and verify them with cosign. Hardened Wolfi-based images also exist — [Elastic: Docker basic install](https://github.com/elastic/docs-content/blob/main/deploy-manage/deploy/self-managed/install-elasticsearch-docker-basic.md). The Kibana Docker page says "Docker images for Kibana (hub.docker.com/_/kibana) are available from the Elastic Docker registry", and the images are built from `github.com/elastic/dockerfiles` — [Elastic: Kibana with Docker](https://github.com/elastic/docs-content/blob/main/deploy-manage/deploy/self-managed/install-kibana-with-docker.md).
- **Docker Hub official images.** The `elasticsearch` and `kibana` library entries have `GitRepo: https://github.com/elastic/dockerfiles.git`, with maintainers Rene Groeschke (@breskeby) for Elasticsearch and Jon Budzenski (@jbudz) for Kibana. Tags are 8.19.23, 9.4.8 and 9.5.5, all on `amd64, arm64v8` — [docker-library elasticsearch](https://github.com/docker-library/official-images/blob/master/library/elasticsearch); [docker-library kibana](https://github.com/docker-library/official-images/blob/master/library/kibana).
- **Older forum posts.** These say the Docker Hub image was "not supported by Elastic" (2017) and lagged releases (7.15 in 2021). Since 6.4 the Hub images are "essentially copies" of Elastic's — [discuss.elastic.co (search result)](https://discuss.elastic.co/t/issue-with-elasticsearch-docker-image/156913); [discuss.elastic.co 7.15 (search result)](https://discuss.elastic.co/t/why-is-7-15-not-available-in-docker-hub-yet/286930). That history explains the "use docker.elastic.co" advice still found in tutorials.
- **Fluent Bit.** `cr.fluentbit.io/fluent/fluent-bit` (used in the docs' `docker run`) or Docker Hub `fluent/fluent-bit`. Tags 5.1.5 and 5.1.5-debug cover `amd64, arm64, arm/v7` — [fluent-bit-docs: Docker](https://github.com/fluent/fluent-bit-docs/blob/master/installation/downloads/docker.md).
- **OTel Collector.** Core image `otel/opentelemetry-collector:<version>` — [Collector quick start](https://github.com/open-telemetry/opentelemetry.io/blob/main/content/en/docs/collector/quick-start.md). The tail sampling processor is in collector-contrib — [sampling](https://github.com/open-telemetry/opentelemetry.io/blob/main/content/en/docs/concepts/sampling/index.md).
- **Jaeger.** `cr.jaegertracing.io/jaegertracing/jaeger:<version>`, with all-in-one on in-memory storage — [Jaeger getting started](https://github.com/jaegertracing/documentation/blob/main/content/docs/v2/_dev/getting-started.md).

**Memory and Mac specifics**
- **Elasticsearch.** "If using Docker Desktop, make sure to allocate at least 4GB of memory" in Settings > Resources. Running `docker run ... -m 1GB` sets the container limit and "removes the need to manually set the JVM size". ML features need about 6 GB — [Elastic Docker basic](https://github.com/elastic/docs-content/blob/main/deploy-manage/deploy/self-managed/install-elasticsearch-docker-basic.md); same 4 GB note in [compose](https://github.com/elastic/docs-content/blob/main/deploy-manage/deploy/self-managed/install-elasticsearch-docker-compose.md) and [Kibana](https://github.com/elastic/docs-content/blob/main/deploy-manage/deploy/self-managed/install-kibana-with-docker.md).
- **`vm.max_map_count`.** Production needs `1048576`. On macOS with Docker Desktop it has to be set inside the VM — [Elastic Docker prod](https://github.com/elastic/docs-content/blob/main/deploy-manage/deploy/self-managed/install-elasticsearch-docker-prod.md).
- **start-local.** `curl -fsSL https://elastic.co/start-local | sh` sets up Elasticsearch on :9200 and Kibana on :5601 "for local development only". It needs 5 GB of disk and works on Linux and macOS. It ships a one-month trial that "reverts to Free and open - Basic", and Basic includes ES|QL. `--esonly` skips Kibana and `--edot` adds the EDOT Collector. HTTPS is off, with Basic auth and an API key in `.env` — [docs-content: local quickstart](https://github.com/elastic/docs-content/blob/main/deploy-manage/deploy/self-managed/local-development-installation-quickstart.md); [start-local README](https://github.com/elastic/start-local/blob/main/README.md).
- **start-local internals.** The script sets `ES_LOCAL_JAVA_OPTS="-Xms128m -Xmx2g"`, or `-Xms2g -Xmx2g` with EDOT. It also sets `discovery.type=single-node`, `xpack.security.enabled=true`, `xpack.security.http.ssl.enabled=false`, `xpack.license.self_generated.type=trial` and a disk watermark of 1gb — [start-local.sh](https://github.com/elastic/start-local/blob/main/start-local.sh).
- **Fluent Bit** uses about 450 KB vs Fluentd's more than 60 MB — [fluent-bit-docs](https://github.com/fluent/fluent-bit-docs/blob/master/about/fluentd-and-fluent-bit.md).
- **OTel Python** needs Python 3.10 or later — [OTel Python](https://github.com/open-telemetry/opentelemetry.io/blob/main/content/en/docs/languages/python/_index.md).

### Inferences
- **Recommended Docker Desktop allocation** for the full logging lab: 6 GB, or 8 GB if the tracing lab runs at the same time. The sum is Elasticsearch at about 2 GB with a 1 GB heap, Kibana at about 1 GB (an estimate, not sourced), and Fluent Bit, Jaeger, the Collector and a Flask app at a few hundred MB together. Elastic's own floor is 4 GB.
- **Two lab paths.** Path A uses `start-local` for the fastest working Elasticsearch and Kibana, but adds auth and an API key that Fluent Bit then needs (`http_user`/`http_passwd` or `http_api_key`). Path B is a hand-written compose with security off, which is simpler for Fluent Bit and teaches more, but is insecure. For a beginner course, Path B is probably better for the EFK lab, with start-local mentioned as the official one-liner.
- **`vm.max_map_count` on a Mac.** In single-node dev mode, Elasticsearch usually only warns about it. If startup fails, the Elastic docs explain how to set it inside the Docker Desktop VM.
- **Docker Hub vs docker.elastic.co.** Both are Elastic-built and both have arm64. Use docker.elastic.co so commands match Elastic's docs and cosign verification. Pin exact versions (`9.5.5`) because Elastic images have no `latest` tag. I believe this from experience and did not verify it this session.
- **OpenSearch 3.9** with OpenSearch Dashboards is a fully Apache-2.0 alternative for learners who care about licensing. The Fluent Bit `opensearch` output exists (listed in the outputs directory of fluent-bit-docs), but I did not read it.

### Gaps
- I did not verify arm64 manifests for `otel/opentelemetry-collector(-contrib)` or `cr.jaegertracing.io/jaegertracing/jaeger`. Registry APIs were not queried. Both projects are widely used on Apple Silicon, but treat this as unverified.
- No sourced RAM figure was found for Kibana alone, or for Jaeger all-in-one and the Collector under light load.
- I did not check whether `latest` tags exist on docker.elastic.co.
- I could not query live Docker Hub pages; the docker-library manifests stand in for them.

---

## What is the minimal working Fluent Bit config (inputs, parsers, filters, outputs) for Docker or Kubernetes logs to Elasticsearch?

### Takeaway
**Docker on a Mac:** `forward` input on 24224, fed by Docker's `fluentd` logging driver; a `parser` filter with `key_name: log` and a JSON parser defined in the YAML `parsers:` section; and an `es` output with `logstash_format: on` and `suppress_type_name: on`.

**Kubernetes:** `tail` on `/var/log/containers/*.log` with `multiline.parser: docker,cri`; the `kubernetes` filter with `merge_log: on`; and the same `es` output. Install it as a DaemonSet with the official Helm chart.

Full files are in the Lesson 2 section above.

### Cited Findings
- **YAML layout.** Fluent Bit YAML config has top-level `parsers:` and `pipeline:` (`inputs`, `filters`, `outputs`), and `service:` holds settings such as `parsers_file` — [Fluent Bit Kubernetes (Windows example YAML)](https://github.com/fluent/fluent-bit-docs/blob/master/installation/downloads/kubernetes.md); [parser filter](https://github.com/fluent/fluent-bit-docs/blob/master/pipeline/filters/parser.md).
- **Parser filter.** It takes `key_name` (the field to parse), `reserve_data` ("Keep all other original fields", default false) and `preserve_key` (keep the original field, default false) — [parser filter](https://github.com/fluent/fluent-bit-docs/blob/master/pipeline/filters/parser.md).
- **Default parsers.** Default parsers (docker, apache, ...) live in `conf/parsers.conf` in the fluent-bit repo. Custom parsers can be defined in YAML — [fluent-bit-docs: parsers](https://github.com/fluent/fluent-bit-docs/blob/master/pipeline/parsers.md).
- **Running in Docker.** `docker run -ti -v ./fluent-bit.yaml:/fluent-bit/etc/fluent-bit.yaml cr.fluentbit.io/fluent/fluent-bit -c /fluent-bit/etc/fluent-bit.yaml` — [fluent-bit-docs: Docker](https://github.com/fluent/fluent-bit-docs/blob/master/installation/downloads/docker.md).
- **Forward input** listens on `0.0.0.0:24224` by default — [forward input](https://github.com/fluent/fluent-bit-docs/blob/master/pipeline/inputs/forward.md). The Docker `fluentd` driver puts the message in `log`, plus `container_id`, `container_name` and `source` — [docker fluentd driver](https://github.com/docker/docs/blob/main/content/manuals/engine/logging/drivers/fluentd.md).
- **Kubernetes core config.** `tail` with `tag: kube.*`, `path: /var/log/containers/*.log` and `multiline.parser: docker,cri`, followed by a `kubernetes` filter with `kube_url`, `kube_ca_file`, `kube_token_file`, `kube_tag_prefix: kube.var.log.containers.`, `merge_log: on` and `merge_log_key: log_processed` — [kubernetes filter](https://github.com/fluent/fluent-bit-docs/blob/master/pipeline/filters/kubernetes.md).
- **ES output essentials** for 9.x — [ES output](https://github.com/fluent/fluent-bit-docs/blob/master/pipeline/outputs/elasticsearch.md):
  - `host` and `port`
  - `suppress_type_name on`
  - `logstash_format on` with `logstash_prefix`, or a fixed `index`
  - credentials through `http_user`/`http_passwd` or `http_api_key` ("Must be base64 encoded"), or `cloud_id`/`cloud_auth` for Elastic Cloud
  - `tls on` when HTTPS is used
  - `trace_error on` while debugging
- **Name alias.** From v5.1, `name: elasticsearch` works as an alias of `name: es` — [What's new in v5](https://github.com/fluent/fluent-bit-docs/blob/master/installation/whats-new-in-fluent-bit-v5.md).

### Inferences
- **Define your own parser.** For a beginner lab, define the JSON parser inline (`parsers: - name: app_json, format: json`) rather than relying on whether the default `parsers.conf` is auto-loaded with a YAML config. The docs show `parsers_file` commented out in YAML examples, which suggests it is opt-in.
- **Keep a `stdout` output during the lab.** Seeing records leave Fluent Bit separates "Fluent Bit isn't receiving" from "Elasticsearch is rejecting".
- **Expected record in Elasticsearch** (Docker path): `{"@timestamp": "...", "container_id": "...", "container_name": "/lab-app-1", "source": "stdout", "level": "ERROR", "service": "checkout", "msg": "payment failed for order 5"}`.
  - Without `reserve_data: on`, only the parsed fields survive.
  - Without the parser filter, everything sits in one `log` string.

### Gaps
- None of the configs were executed in this session. I was not able to confirm whether a YAML config auto-loads the image's default `parsers.conf`. I also did not check how the official Helm chart's default values set the Elasticsearch host and index.
