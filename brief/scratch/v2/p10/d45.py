"""Day 45: Grafana dashboards. Content for content/p10.json (built by build.py)."""
import pathlib

LAB = pathlib.Path("/home/user/devops-from-zero/labs/hello-devops/observability")


def lab(rel):
    return (LAB / rel).read_text().rstrip("\n")


DOC_DS = "https://grafana.com/docs/grafana/latest/datasources/"
DOC_VIZ = "https://grafana.com/docs/grafana/latest/visualizations/panels-visualizations/visualizations/"
DOC_PANEL = "https://grafana.com/docs/grafana/latest/visualizations/panels-visualizations/panel-overview/"
DOC_PROMVARS = "https://grafana.com/docs/grafana/latest/datasources/prometheus/template-variables/"
DOC_UNITS = "https://grafana.com/docs/grafana/latest/visualizations/panels-visualizations/configure-standard-options/"
DOC_THRESH = "https://grafana.com/docs/grafana/latest/visualizations/panels-visualizations/configure-thresholds/"
DOC_OVERRIDES = "https://grafana.com/docs/grafana/latest/visualizations/panels-visualizations/configure-overrides/"
DOC_TRANSFORM = "https://grafana.com/docs/grafana/latest/panels-visualizations/query-transform-data/transform-data/"
DOC_BEST = "https://grafana.com/docs/grafana/latest/dashboards/build-dashboards/best-practices/"
DOC_ADVVARS = "https://grafana.com/docs/grafana/latest/visualizations/dashboards/variables/advanced-variables/"
DOC_ANNOT = "https://grafana.com/docs/grafana/latest/visualizations/dashboards/build-dashboards/annotate-visualizations/"
DOC_JSON = "https://grafana.com/docs/grafana/latest/visualizations/dashboards/build-dashboards/view-dashboard-json-model/"
DOC_PROV = "https://grafana.com/docs/grafana/latest/administration/provisioning/"
TUT_PROV = "https://grafana.com/tutorials/provision-dashboards-and-data-sources/"
BLOG_RATE = "https://grafana.com/blog/new-in-grafana-7-2-rate-interval-for-prometheus-rate-queries-that-just-work/"
VID_VIZ = "https://www.youtube.com/watch?v=yNRnLyVntUw"
VID_RED = "https://www.youtube.com/watch?v=zk77VS98Em8"
VID_DYN = "https://www.youtube.com/watch?v=nVlSpN3HULU"
VID_BEGIN = "https://www.youtube.com/watch?v=vf5MJLoXUG0"
DOCKER_DOC = "https://github.com/grafana/grafana/blob/main/docs/sources/setup-grafana/installation/docker/index.md"

Q_FUNC = (
    "$ q() { jq -n --arg e \"$1\" '{queries:[{refId:\"A\",datasource:{uid:\"prometheus\"},expr:$e,instant:true}],from:\"now-5m\",to:\"now\"}' \\\n"
    "    | curl -s -u admin:admin -H 'Content-Type: application/json' localhost:3000/api/ds/query -d @- \\\n"
    "    | jq -c '.results.A.frames[] | {labels: (.schema.fields[1].labels | del(.__name__, .job, .instance)), value: .data.values[1][0]}'; }"
)

D45 = {
    "id": "d45",
    "title": "Grafana dashboards",
    "minutes": 50,
    "goal": "By the end you can build Grafana panels from PromQL with the right units, thresholds and variables, lay out a RED dashboard an on-call engineer can read in seconds, and provision it from files in git.",
    "guess": {
        "q": "A Grafana dashboard shows the last 7 days of request rates for hello-devops. Where do those numbers live?",
        "options": [
            "In Grafana's own database, copied over from Prometheus every 15 seconds",
            "In Prometheus; each panel sends its query there when the page loads",
            "In the dashboard's JSON file, which saves the values of every panel",
            "In your browser's cache, filled the first time you open the page",
        ],
        "answer": 1,
        "why": "Grafana stores dashboards, users and settings, but not your metrics. Each panel asks a data source, here Prometheus, every time it loads or refreshes.",
    },
    "terms": [
        {"term": "Data source", "plain": "A connection from Grafana to a system that stores data, such as Prometheus for metrics or Loki for logs."},
        {"term": "Panel", "plain": "One box on a Grafana dashboard: one or more queries plus a visualization that draws the result."},
        {"term": "Visualization", "plain": "How a panel draws its data, for example as a time series graph, a single stat, a gauge, a table or a heatmap."},
        {"term": "Unit", "plain": "A panel setting that says what a number means, so a ratio of 0.034 can show as 3.4% and 0.2 seconds as 200 ms."},
        {"term": "Threshold", "plain": "A value at which a panel changes color, for example red once the error ratio reaches 5%."},
        {"term": "Transformation", "plain": "A step inside Grafana that reshapes query results (rename, sort, join, filter) before the panel draws them."},
        {"term": "Dashboard variable", "plain": "A dropdown at the top of a dashboard; its value is put into every query that uses $name."},
        {"term": "Provisioning", "plain": "Grafana loading data sources, dashboards and alerts from files at start, so they can live in git."},
    ],
    "sections": [
        {
            "h": "Grafana draws, Prometheus remembers",
            "body": (
                "Grafana is a web app for looking at data that lives somewhere else. In the lab, Prometheus scrapes and stores the metrics (Days 42 to 44). "
                "Grafana asks Prometheus questions in PromQL and draws the answers. "
                "It has a small database of its own for dashboards, users and alert rules, but the numbers stay in Prometheus.\n\n"
                "Each system Grafana can ask is a **data source**. One Grafana can talk to many at once:\n"
                "- Prometheus and Mimir, for metrics.\n"
                "- Loki (Day 46) and Elasticsearch (Part 11), for logs.\n"
                "- Tempo and Jaeger, for traces.\n"
                "- PostgreSQL, MySQL and many hosted services, for everything else.\n\n"
                "Here is what happens when you open a dashboard:\n"
                "1. Your browser loads the dashboard's JSON from the Grafana server.\n"
                "2. For each panel, the browser sends the panel's query to Grafana.\n"
                "3. Grafana passes it on to Prometheus. That is what `access: proxy` means in the data source file.\n"
                "4. Prometheus answers, and the browser draws the result.\n\n"
                "Two things follow from this. Grafana can't show anything Prometheus never scraped, so an empty graph is usually a scrape or query problem. "
                "And every open dashboard runs all its queries again on each refresh. A wall screen with 30 heavy panels that refreshes every 10 seconds is real load on Prometheus.\n\n"
                "The lab's Grafana is already in `observability/compose.yaml`: the `grafana/grafana:13.3.0` image on http://localhost:3000, user `admin`, password `admin`. "
                "Many older tutorials use the `grafana/grafana-oss` image. It stopped getting updates at version 12.4, so skip it."
            ),
            "refs": [
                {"title": "Grafana docs: data sources", "url": DOC_DS, "kind": "docs"},
                {"title": "Grafana docs: run Grafana in Docker (source on GitHub)", "url": DOCKER_DOC, "kind": "docs"},
                {"title": "Grafana tutorial for beginners (video)", "url": VID_BEGIN, "kind": "watch"},
            ],
        },
        {
            "h": "Panels: pick the chart from the question",
            "body": (
                "A panel is one box on a dashboard: a query and a visualization. Start from the question the panel answers, then pick how to draw it:\n"
                "- How does it change over time? Time series, the line chart. Right most of the time.\n"
                "- What is the number right now? Stat: one big number with a small trend line behind it.\n"
                "- How close are we to a limit? Gauge: a dial from a minimum to a maximum, like disk use from 0 to 100%.\n"
                "- How do these things compare? Bar chart or bar gauge: one bar per path, pod or region.\n"
                "- What are the exact values? Table: rows and columns you can sort.\n"
                "- How are the values spread out? Heatmap: time across, buckets up the side, color for how many.\n\n"
                "A panel can hold several queries, named A, B, C and so on (the refId). The lab's latency panel has three: p50 in A, p95 in B and p99 in C. "
                "Each query can return many series, and the legend names them. Write `{{status}}` in the legend field and each line is named `200` or `500` from its labels.\n\n"
                "A stat panel squeezes a whole series into one number. A setting called Calculation decides how: Last, Mean, Max and others. "
                "This trips people up. A stat that shows the mean of the last 7 days hides a 10-minute outage. "
                "For \"right now\", use Last *, which means the last value that is not empty.\n\n"
                "Grafana 13 also suggests visualizations. It looks at the shape of your query result and offers a few charts that fit. Treat that as a first draft, and check it against your question."
            ),
            "refs": [
                {"title": "Grafana docs: panel overview", "url": DOC_PANEL, "kind": "docs"},
                {"title": "Grafana docs: all visualizations", "url": DOC_VIZ, "kind": "docs"},
                {"title": "Creating visualizations with Grafana (Grafana for Beginners series)", "url": VID_VIZ, "kind": "watch"},
            ],
        },
        {
            "h": "Queries: PromQL plus Grafana's helpers",
            "body": (
                "The query editor has two modes. Builder lets you click a metric, labels and functions together. Code is a text box for PromQL. "
                "Both produce the same query, so use Builder to explore and Code once you know what you want.\n\n"
                "Grafana adds a few variables of its own to PromQL. The one you will use most is `$__rate_interval`. It goes where you would write the range in `rate()`:\n\n"
                "`sum(rate(hello_responses_total[$__rate_interval]))`\n\n"
                "Why not write `[1m]`? Because the right range depends on how far you zoom out. "
                "On a 30-minute graph, Grafana asks Prometheus for a point every 15 seconds, and `[1m]` is fine. "
                "On a 7-day graph the points are many minutes apart. A one-minute window then looks at one minute out of every ten and misses the spikes in between. "
                "The `$__rate_interval` variable grows with the gap between points. Grafana takes the larger of two values:\n"
                "- the gap between points plus one scrape interval;\n"
                "- four scrape intervals, the Prometheus advice from Day 43.\n\n"
                "It only works if Grafana knows the scrape interval. That is the `timeInterval: 15s` line in the lab's data source file, and it must match `scrape_interval` in `prometheus.yml`.\n\n"
                "Two more settings matter:\n"
                "- Range or instant. A range query returns many points, for graphs. An instant query returns one value per series, which is all a stat or a table needs.\n"
                "- Empty results. Before any request has failed, the 5xx series doesn't exist. An error ratio built on it shows \"No data\" instead of 0%. Adding `or vector(0)` gives you a real zero. The worked example shows both."
            ),
            "refs": [
                {"title": "Grafana docs: Prometheus template variables and $__rate_interval", "url": DOC_PROMVARS, "kind": "docs"},
                {"title": "Grafana blog: $__rate_interval for rate queries that just work", "url": BLOG_RATE, "kind": "read"},
            ],
        },
        {
            "h": "Units, thresholds and overrides",
            "body": (
                "Prometheus stores base units: seconds, bytes, and ratios between 0 and 1 (Day 42). "
                "That is right for storage and hard on a tired human. The unit setting fixes the display without touching the data:\n"
                "- 0.0347 with unit \"Percent (0.0-1.0)\" shows as 3.47%.\n"
                "- 0.231 with unit \"seconds\" shows as 231 ms.\n"
                "- 3.76 with unit \"requests/sec\" shows as 3.76 req/s.\n"
                "- 1610612736 with unit \"bytes (IEC)\" shows as 1.50 GiB.\n\n"
                "So don't multiply by 100 in PromQL to get a percentage. Keep the ratio and set the unit. In the JSON these are short codes: `percentunit`, `s`, `reqps`, `bytes`.\n\n"
                "A threshold is a value where the color changes. The list starts with a base color, then adds steps upward. "
                "The lab's error ratio stat is green below 1%, orange from 1% and red from 5%. "
                "On a time series, thresholds can also draw a line or a shaded area, so you see the moment a line crossed into red.\n\n"
                "Two related tools:\n"
                "- Value mappings turn numbers into words. The lab shows `up` = 1 as UP and 0 as DOWN.\n"
                "- Overrides change settings for some series only. The lab's rate graph paints the `500` line red, whatever color the palette would give it.\n\n"
                "Use color for what someone should act on, and leave the rest neutral. If every panel is red or green all day, people stop looking at the colors."
            ),
            "refs": [
                {"title": "Grafana docs: standard options and units", "url": DOC_UNITS, "kind": "docs"},
                {"title": "Grafana docs: configure thresholds", "url": DOC_THRESH, "kind": "docs"},
                {"title": "Grafana docs: field overrides", "url": DOC_OVERRIDES, "kind": "docs"},
            ],
        },
        {
            "h": "Transformations: reshape the result inside Grafana",
            "body": (
                "Sometimes the query returns the right numbers in the wrong shape. A transformation reshapes the result inside Grafana, after the query and before the drawing. "
                "You can chain several, and each one works on the output of the one before.\n\n"
                "The lab's table \"Requests by path and status\" is an example. Its query is an instant query with Format set to Table:\n\n"
                "`sum by (path, status) (increase(hello_responses_total{job=~\"$job\"}[5m]))`\n\n"
                "Prometheus returns one row per path and status, with the columns Time, path, status and Value. Two transformations make it readable:\n"
                "1. Organize fields by name: hide Time, rename Value to Requests and put the columns in order.\n"
                "2. Sort by: Requests, largest first.\n\n"
                "Other transformations you will meet:\n"
                "- Reduce: turn each series into one row (last, mean, max). Good for top-10 tables.\n"
                "- Labels to fields: turn series labels into table columns.\n"
                "- Join by field: line up two queries on a shared column, such as time or path.\n"
                "- Filter data by values: drop rows, for example everything under 1 request.\n"
                "- Add field from calculation: a new column computed from the others.\n\n"
                "My rule: if PromQL can do the math, do it in PromQL. A query runs on the Prometheus server and also works in recording rules and alerts. "
                "A transformation exists only in this one panel. Use transformations for layout, and for joining data that PromQL can't see together, such as a metric and a SQL table."
            ),
            "refs": [
                {"title": "Grafana docs: transform data", "url": DOC_TRANSFORM, "kind": "docs"},
            ],
        },
        {
            "h": "Variables, annotations and a layout for on-call",
            "body": (
                "A **dashboard variable** is a dropdown at the top of the dashboard. Its value goes into every query that mentions it. The lab's dashboard has two:\n"
                "- `job` is a Query variable. Grafana asks Prometheus for every value of the `job` label on `hello_responses_total`. Today that is only `hello-devops`; with 40 services, the same dashboard would serve all 40.\n"
                "- `path` depends on `job`. It lists the paths of the chosen job, allows several at once and has an All option.\n\n"
                "With several values selected, Grafana inserts a regular expression such as `/|/healthz`. So queries must use `=~`, not `=`: `{job=~\"$job\", path=~\"$path\"}`. Forgetting this is the most common variable bug.\n\n"
                "Annotations mark events on every time series panel, as a vertical line or a shaded band with a note. "
                "You can add one by hand (Ctrl or Cmd and click on a graph) or let a query find the events. "
                "The lab's dashboard marks when Prometheus alerts fire, using the `ALERTS` series. Real teams add a mark for every deploy, so \"errors went up at 14:02\" becomes \"errors went up right after version 1.4 shipped\".\n\n"
                "Now the layout. Picture the engineer who opens this at 3 a.m. after a page. They need three answers fast: is it broken, since when, and where. So the lab's dashboard has three bands:\n"
                "1. Top: four stats. Requests per second, error ratio, p95 latency and whether Prometheus can reach the app.\n"
                "2. Middle: the same signals over time. Rate on the left, errors in the middle, duration on the right.\n"
                "3. Bottom: a collapsed Details row with a table per path and a latency heatmap, for when the top says something is wrong.\n\n"
                "Grafana's own [dashboard best practices](" + DOC_BEST + ") put it simply: \"A dashboard should tell a story or answer a question.\" "
                "A 40-panel dashboard answers none. If you need more, build a second dashboard and link to it."
            ),
            "refs": [
                {"title": "Grafana docs: dashboard best practices", "url": DOC_BEST, "kind": "docs"},
                {"title": "Grafana docs: annotate visualizations", "url": DOC_ANNOT, "kind": "docs"},
                {"title": "The RED Method: how to instrument your services (talk by Tom Wilkie)", "url": VID_RED, "kind": "watch"},
            ],
        },
        {
            "h": "Dashboards are JSON, so keep them in git",
            "body": (
                "Every dashboard is a JSON document. Open the dashboard settings, find JSON Model, and you see something like the lab's `hello-red.json`:\n"
                "- `uid` and `title`. The uid is part of the URL, `/d/hello-red/...`, so keep it fixed and links never break.\n"
                "- `templating.list`: the variables.\n"
                "- `panels`: one object per panel, with `type`, `title`, `gridPos` (its place on a grid 24 columns wide), `targets` (the queries) and `fieldConfig` (units, thresholds, overrides).\n\n"
                "If the JSON is the dashboard, you can keep it in git and review changes like code. Provisioning loads such files when Grafana starts. "
                "Grafana reads `/etc/grafana/provisioning/`, and the lab mounts its own folder there:\n"
                "- `datasources/`: YAML files that create data sources.\n"
                "- `dashboards/`: a provider file that says \"load every JSON file in this folder\".\n"
                "- `alerting/`: alert rules and contact points (Day 46).\n\n"
                "Two provider settings are worth knowing. With `allowUiUpdates: false`, the Save button refuses, because the file is the truth. "
                "With `updateIntervalSeconds: 30`, Grafana checks the folder for changed files every 30 seconds. "
                "Keep that above 10 on a Mac: at 10 or less, Grafana waits for file change events, and Docker bind mounts may never pass them on.\n\n"
                "The everyday loop:\n"
                "1. Change the dashboard in the UI until you like it.\n"
                "2. Use Export to copy its JSON, and paste it over the file.\n"
                "3. Commit and open a pull request.\n"
                "4. Grafana picks up the file within 30 seconds.\n\n"
                "One trap: in provisioning YAML files, Grafana replaces `$NAME` with environment variables, so a real dollar sign must be written `$$`. "
                "Dashboard JSON files are left alone, so `$job` in a query is safe there.\n\n"
                "Grafana 12 and 13 added a second dashboard format (v2) for dynamic dashboards with tabs and automatic layout. To provision a v2 dashboard from a file, it must use a Kubernetes-style wrapper. "
                "Classic JSON still works everywhere, and this course uses it."
            ),
            "refs": [
                {"title": "Grafana docs: provision Grafana", "url": DOC_PROV, "kind": "docs"},
                {"title": "Grafana docs: dashboard JSON model", "url": DOC_JSON, "kind": "docs"},
                {"title": "Grafana tutorial: provision dashboards and data sources", "url": TUT_PROV, "kind": "read"},
            ],
        },
    ],
    "analogy": (
        "A Grafana dashboard is like a spreadsheet whose cells hold formulas that pull live numbers from a database. "
        "The file saves the formulas, the chart types and the colors, and the numbers arrive fresh each time you open it. "
        "A dashboard variable is the cell at the top that every formula reads, so changing it changes every chart. "
        "Where it breaks: a spreadsheet can keep a copy of the data, but a panel keeps nothing. When Prometheus deletes old samples (after 7 days in the lab), that part of every graph goes empty."
    ),
    "diagram": (
        '<svg viewBox="0 0 560 232" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="The browser asks Grafana for each panel; Grafana sends PromQL to Prometheus, which scrapes hello-devops; provisioning files in git load dashboards into Grafana">'
        '<rect class="bx" x="16" y="24" width="124" height="44" rx="10"/>'
        '<text class="t" x="78" y="51" font-size="13" text-anchor="middle">Browser</text>'
        '<rect class="bxg" x="16" y="164" width="140" height="44" rx="10"/>'
        '<text class="tk" x="86" y="191" font-size="13" text-anchor="middle">Files in git</text>'
        '<rect class="bxo" x="214" y="94" width="120" height="48" rx="10"/>'
        '<text class="tk" x="274" y="123" font-size="13" text-anchor="middle">Grafana</text>'
        '<rect class="bxt" x="404" y="94" width="132" height="48" rx="10"/>'
        '<text class="tk" x="470" y="123" font-size="13" text-anchor="middle">Prometheus</text>'
        '<rect class="bx" x="398" y="176" width="144" height="40" rx="10"/>'
        '<text class="t" x="470" y="201" font-size="13" text-anchor="middle">hello-devops</text>'
        '<line class="ln" x1="140" y1="56" x2="212" y2="102" marker-end="url(#ar)"/>'
        '<text class="ts" x="192" y="68" font-size="11" text-anchor="middle">panel query</text>'
        '<line class="ln" x1="156" y1="176" x2="212" y2="136" marker-end="url(#ar)"/>'
        '<text class="ts" x="196" y="174" font-size="11" text-anchor="middle">provisioning</text>'
        '<line class="ln" x1="334" y1="118" x2="400" y2="118" marker-end="url(#ar)"/>'
        '<text class="ts" x="367" y="110" font-size="11" text-anchor="middle">PromQL</text>'
        '<line class="lnd" x1="470" y1="142" x2="470" y2="172" marker-end="url(#ar)"/>'
        '<text class="ts" x="420" y="162" font-size="11" text-anchor="middle">scrape</text>'
        '</svg>'
    ),
    "diagram_caption": "Grafana stores dashboards, not metrics: every panel asks Prometheus again.",
    # worked steps are filled in by build.py from real output (see WORKED_45)
    "code": [
        {"lang": "yaml", "title": "observability/grafana/provisioning/datasources/prometheus.yaml",
         "src": lab("grafana/provisioning/datasources/prometheus.yaml"), "run": "docker compose restart grafana"},
        {"lang": "yaml", "title": "observability/grafana/provisioning/dashboards/provider.yaml",
         "src": lab("grafana/provisioning/dashboards/provider.yaml"), "run": "docker compose restart grafana"},
        {"lang": "json", "title": "observability/grafana/dashboards/hello-red.json",
         "src": lab("grafana/dashboards/hello-red.json"),
         "run": "curl -X POST -u admin:admin localhost:3000/api/admin/provisioning/dashboards/reload"},
    ],
    "commands": [
        {"cmd": "docker compose up -d", "what": "Start the monitoring lab from the observability folder: the app, Prometheus, Alertmanager and Grafana."},
        {"cmd": "open http://localhost:3000", "what": "Open Grafana in your browser (user admin, password admin)."},
        {"cmd": "curl -s localhost:3000/api/health", "what": "Check that Grafana is up and see its version. No login needed."},
        {"cmd": "curl -s -u admin:admin localhost:3000/api/datasources | jq '.[].name'", "what": "List the data sources Grafana knows about."},
        {"cmd": "curl -s -u admin:admin 'localhost:3000/api/search?query=hello' | jq '.[].title'", "what": "Find dashboards and folders by name."},
        {"cmd": "curl -s -u admin:admin localhost:3000/api/dashboards/uid/hello-red | jq '.meta.provisioned'", "what": "Prints true when the dashboard was loaded from a file."},
        {"cmd": "docker compose restart grafana", "what": "Restart Grafana so it reads changed provisioning files, such as a data source."},
        {"cmd": "curl -X POST -u admin:admin localhost:3000/api/admin/provisioning/dashboards/reload", "what": "Read the dashboard files again now, without waiting 30 seconds."},
        {"cmd": "docker compose logs grafana | grep -i provision", "what": "See what Grafana provisioned at start, and any errors in your files."},
        {"cmd": "jq empty grafana/dashboards/hello-red.json", "what": "Check that the dashboard file is valid JSON. Silence means it is."},
        {"cmd": "while true; do curl -s -o /dev/null localhost:8000/; sleep 0.2; done", "what": "Send steady traffic so the panels have something to show. Stop it with Ctrl+C."},
        {"cmd": "docker compose stop redis", "what": "Break the app on purpose: its / page returns 500 while Redis is gone. Bring it back with docker compose start redis."},
    ],
    "mistake": (
        "Editing a provisioned dashboard in the browser and expecting the change to stick. With `allowUiUpdates: false` Grafana refuses to save it. "
        "If you set it to true, the next change to the file quietly overwrites your edit. "
        "Make the change in the UI, export the JSON, paste it into the file in git, and let provisioning load it."
    ),
    "real_world": (
        "At a fake payments company, PayFlow, each service team owns one RED dashboard in its repo, built from a shared template, and CI checks the JSON on every pull request. "
        "The on-call runbook links straight to `/d/<uid>` URLs, which is why nobody changes a uid. "
        "Dashboards made by hand in the UI are allowed for exploring, and they get cleaned up after 30 days."
    ),
    "task": {
        "title": "Provision the RED dashboard, then add a panel the git way",
        "steps": [
            "In `observability/`, create the two provisioning files and `grafana/dashboards/hello-red.json` from this lesson's Files section.",
            "Start the lab with `docker compose up -d` (or `docker compose restart grafana` if it already runs). Check the Grafana logs for provisioning errors.",
            "Start the traffic loop in a second terminal, open http://localhost:3000 and find the RED dashboard in the hello-devops folder. Try the Path dropdown with one path, then All.",
            "Change a panel title and try to save. Read Grafana's message and say in one sentence why it refuses.",
            "Create a new, empty dashboard and build a bar gauge panel: requests per second for each path, with unit requests/sec and one threshold of your choice.",
            "Copy that panel's JSON (panel menu, Inspect, Panel JSON) and add it to the `panels` list in `hello-red.json`, with a new `id` and a free `gridPos`.",
            "Check the file with `jq`, call the dashboards reload API (or wait 30 seconds) and refresh the browser.",
            "Stop Redis for two minutes and note which panels change first. Then start it again and delete the scratch dashboard.",
        ],
        "hints": [
            "A bar gauge wants one value per path: an instant query such as `sum by (path) (rate(hello_responses_total{job=~\"$job\"}[$__rate_interval]))` with the legend `{{path}}`.",
            "Put the new panel in the list just before the Details row and give it `\"gridPos\": {\"h\": 6, \"w\": 24, \"x\": 0, \"y\": 12}`. Grafana pushes the row down.",
            "Nothing changed? Run `docker compose logs grafana | grep -i dashboard` and look for a JSON error or a duplicate panel id.",
        ],
        "done_when": "`curl -s -u admin:admin localhost:3000/api/dashboards/uid/hello-red | jq '.meta.provisioned, [.dashboard.panels[].title]'` prints `true` and a list that includes your new panel's title.",
    },
    "explain_back": {
        "prompt": "Explain to a teammate, in 3 to 4 sentences, how a number gets from hello-devops onto your RED dashboard, and why the dashboard lives in a file in git. Mention data source, panel and provisioning.",
        "answer": (
            "Prometheus scrapes the app's /metrics page every 15 seconds and stores the samples. "
            "Grafana stores no metrics. Each panel holds a PromQL query; when the page loads, Grafana sends it to the Prometheus data source and draws the answer with the panel's units and thresholds. "
            "The dashboard itself is a JSON document, so we keep it in git, review changes in pull requests and let provisioning load it when Grafana starts. "
            "That way a new Grafana gets the same dashboards and nobody's quick edit in the browser is lost or slips in unreviewed."
        ),
    },
    "recap": [
        "Grafana stores dashboards, not data: every panel asks a data source such as Prometheus each time it loads.",
        "Pick the visualization from the question: time series for change over time, stat for now, table for exact values, heatmap for spread.",
        "Use `$__rate_interval` in `rate()`, set the data source scrape interval, and add `or vector(0)` where an empty result should read as 0.",
        "Keep base units in PromQL and set the panel unit; color only what someone must act on.",
        "Lay out for on-call: RED numbers on top, the same signals over time below, details collapsed at the bottom.",
        "A dashboard is JSON: provision it from files in git with a fixed uid, and change the file, not the UI.",
    ],
    "check": [
        {
            "q": "A stat panel shows the error ratio as 0.021. The team wants it to read 2.1% and turn red from 2%. What do you change?",
            "options": [
                "Multiply the PromQL by 100 and add a threshold at 2",
                "Set the unit to Percent (0.0-1.0) and add a red threshold at 0.02",
                "Add a transformation that multiplies the value field by 100",
                "Set the unit to Percent (0-100) and add a red threshold at 2",
            ],
            "answer": 1,
            "why": "Keep the base ratio from Prometheus; the percentunit unit displays 0.021 as 2.1%, and thresholds compare against the raw value, 0.02.",
        },
        {
            "q": "Your `$instance` variable allows several values. With two instances picked, every panel shows No data. The query has `{instance=\"$instance\"}`. What is wrong?",
            "options": [
                "Variables can't be used inside label matchers",
                "The variable needs the Include All option turned on",
                "Several values become a regex, so the matcher must use =~",
                "The data source needs a shorter scrape interval setting",
            ],
            "answer": 2,
            "why": "Grafana inserts something like a|b for several values, which only matches with the regex matcher =~.",
        },
        {
            "q": "You change `hello-red.json` on your Mac. Five minutes later Grafana in Docker still shows the old version, and `updateIntervalSeconds` is 5. What is the likely cause?",
            "options": [
                "Below 10 seconds Grafana relies on file change events, which Docker bind mounts may not deliver",
                "Grafana only reads dashboard files once, so it always needs a full restart",
                "The uid in the file must change whenever the dashboard content changes",
                "Provisioned dashboards are cached by the browser for ten minutes",
            ],
            "answer": 0,
            "why": "With 10 seconds or less Grafana waits for file system events; set it above 10 so Grafana polls the folder instead.",
        },
    ],
    "interview": [
        {
            "q": "How would you design a dashboard for a service you are on call for?",
            "a": (
                "I start from the questions on-call has during a page: is it broken, since when, and where. "
                "The top row shows the RED numbers as stats: request rate, error ratio and a latency percentile, plus whether the target is up. "
                "Below them are the same signals as time series, with deploy annotations, so you can see when things changed. "
                "Details such as per-endpoint tables, heatmaps and machine metrics go in collapsed rows or linked dashboards. "
                "I use one variable for the service so the same dashboard works for every service, and I keep it in git."
            ),
        },
        {
            "q": "Why manage Grafana dashboards as code, and how do you do it?",
            "a": (
                "Dashboards made by hand drift, get copied and are lost when an instance is rebuilt. "
                "As code, each dashboard is JSON in git with a fixed uid, reviewed in pull requests and loaded by Grafana's file provisioning, the Terraform provider or Git Sync. "
                "I set the provider so the UI can't save over provisioned dashboards, which makes the file the single source of truth. "
                "The workflow is to edit in the UI, export the JSON, commit it and let CI check that it parses."
            ),
        },
        {
            "q": "What is $__rate_interval and why use it instead of a fixed range?",
            "a": (
                "It is a Grafana variable for the range in rate() and increase(). "
                "Grafana sets it to the larger of the step between graph points plus one scrape interval, and four scrape intervals. "
                "A fixed range like [1m] is fine zoomed in but skips data when each graph point is many minutes apart, and a range under four scrapes can return nothing. "
                "It only works if the data source's scrape interval setting matches Prometheus."
            ),
        },
    ],
    "deeper": {
        "minutes": 12,
        "body": (
            "One dashboard per service is a good start. With 30 services, people want a single page that says which one is unhappy. "
            "That is a different dashboard with a different job, and Grafana's best practices call it a drill-down.\n\n"
            "Build an overview first. Make one table panel with three instant queries, all grouped `by (job)`: request rate, error ratio and p95 latency. "
            "Then add these transformations:\n"
            "1. Join by field on `job`, so each service becomes one row with three columns.\n"
            "2. Organize fields, to rename the columns and hide the Time columns.\n"
            "3. Sort by error ratio, worst first.\n\n"
            "Add thresholds to the error column, and the unhappy service turns red at the top of the table.\n\n"
            "Next, link each row to the service dashboard. A data link on the table can point to `/d/hello-red?var-job=${__data.fields.job}`. "
            "Grafana fills in the job from the row you click, and `var-job` sets the dashboard variable from the URL. "
            "So one click takes on-call from \"something is red\" to the RED dashboard for exactly that service.\n\n"
            "Then cover the machines. RED describes how users experience a service. The USE method describes resources: utilization, saturation and errors for each CPU, disk and network card. "
            "node_exporter from Day 42 already gives you the numbers:\n"
            "- Utilization: the share of CPU time not idle, from `node_cpu_seconds_total`.\n"
            "- Saturation: load average compared with the number of CPUs (`node_load1`).\n"
            "- Errors: network errors from `node_network_receive_errs_total`.\n\n"
            "Keep RED and USE on separate dashboards and link them. They answer different questions, and mixing them makes both harder to read.\n\n"
            "Grafana's best practices page describes three maturity levels. Low means copied dashboards and one-offs that never go away. "
            "Medium means template variables instead of copies, drill-downs, and dashboard JSON in version control. "
            "High means no editing in the browser at all: scripts generate the dashboards, and viewers change what they see with variables. "
            "Day 46 shows the tools for that last step: Terraform, the Foundation SDK and Git Sync.\n\n"
            "Finally, watch the cost. Every panel is at least one query, every refresh runs them all, and every viewer multiplies that. "
            "Set a sensible refresh (30 seconds, not 5), avoid huge time ranges by default, and move heavy expressions into recording rules (Day 43) that the panels read."
        ),
    },
    "sources": [
        {"title": "Grafana docs: provision Grafana", "url": DOC_PROV},
        {"title": "Grafana docs: dashboard best practices", "url": DOC_BEST},
        {"title": "Grafana docs: Prometheus template variables", "url": DOC_PROMVARS},
        {"title": "Grafana docs: transform data", "url": DOC_TRANSFORM},
    ],
}
