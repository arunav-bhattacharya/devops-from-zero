"""Book-voice rewrite of d53 (Grafana dashboards). Writer: tg."""
import json, pathlib

P = pathlib.Path("/home/user/devops-from-zero/content/p13.json")
d = json.loads(P.read_text())
L = next(x for x in d["lessons"] if x["id"] == "d53")

L["opening"] = (
    "Picture a doctor called to the ward at 3 a.m. On the wall by the nurses' station hangs a board with forty "
    "numbers in small handwriting. Some temperatures are in Celsius and some in Fahrenheit. Nothing is circled. She "
    "has one minute to decide which patient to see first, and the board, full as it is, does not help.\n\n"
    "Every team builds that board by accident. Each number was added for a good reason, by someone who knew what it "
    "meant. Nobody planned the whole.\n\n"
    "Last time, our alerts learned to wake the right person, once. When that person opens a laptop, they need to "
    "see what is wrong in seconds. In this lesson, we'll use Grafana to draw hello-devops's numbers as a dashboard. "
    "It will have big, clear dials with the right units and red where it matters, laid out for a tired reader. Then we'll keep "
    "it in git, so nobody's late-night edit quietly changes it.\n\n"
    "Before we start, make a guess, and keep it in mind."
)

L["guess"]["q"] = (
    "A Grafana dashboard, a web page of graphs, shows the last 7 days of request rates for hello-devops. Where do "
    "those numbers live?"
)
L["guess"]["why"] = (
    "Grafana stores dashboards, users and settings, but not your numbers. Each panel asks a data source, here "
    "Prometheus, every time the page loads or refreshes."
)

plains = {
    "Data source": "A connection from Grafana to a system that stores data, such as Prometheus for metrics or Loki for logs.",
    "Panel": "One box on a Grafana dashboard: one or more queries plus a chart that draws the result.",
    "Visualization": "How a panel draws its data, for example as a line graph, a single big number, a dial, a table or a heatmap.",
    "Unit": "A panel setting that says what a number means, so a ratio of 0.034 can show as 3.4% and 0.2 seconds as 200 ms.",
    "Threshold": "A value at which a panel changes color, for example red once the error ratio reaches 5%.",
    "Transformation": "A step inside Grafana that reshapes query results (rename, sort, join, filter) before the panel draws them.",
    "Dashboard variable": "A dropdown at the top of a dashboard; its value is put into every query that uses $name.",
    "Provisioning": "Grafana loading data sources, dashboards and alerts from files when it starts, so they can live in git.",
}
for t in L["terms"]:
    t["plain"] = plains[t["term"]]

S = L["sections"]

S[0]["h"] = "Grafana draws, Prometheus remembers"
S[0]["body"] = (
    "During an incident you want a dozen graphs ready on one page, with names, units and colors the whole team "
    "agrees on. Prometheus's Query page answers one query at a time. That is the blank board, not the finished one.\n\n"
    "Grafana is a web app for looking at data that lives somewhere else. In the lab, Prometheus scrapes and stores "
    "the metrics of hello-devops, our tiny app that greets visitors and counts the visits. Grafana asks Prometheus "
    "questions in PromQL, Prometheus's query language, and draws the answers. It has a small database of its own for "
    "dashboards, users and alert rules, but the numbers stay in Prometheus.\n\n"
    "Each system Grafana can ask is a data source. One Grafana can talk to many at once:\n"
    "- Prometheus and Mimir, for metrics.\n"
    "- Loki (next lesson) and Elasticsearch (Part 14), for logs.\n"
    "- Tempo and Jaeger, for traces.\n"
    "- PostgreSQL, MySQL and many hosted services, for everything else.\n\n"
    "Here is what happens when you open a dashboard:\n"
    "1. Your browser loads the dashboard's JSON (a structured text file) from the Grafana server.\n"
    "2. For each panel, the browser sends the panel's query to Grafana.\n"
    "3. Grafana passes it on to Prometheus. That is what `access: proxy` means in the data source file.\n"
    "4. Prometheus answers, and the browser draws the result.\n\n"
    "Two things follow from this. Grafana cannot show anything Prometheus never scraped, so an empty graph is usually "
    "a scrape or query problem. And Grafana keeps no copy: when Prometheus deletes old samples (after 7 days in the "
    "lab), that part of every graph goes empty.\n\n"
    "Every open dashboard also runs all its queries again on each refresh. A wall screen with 30 heavy panels that "
    "refreshes every 10 seconds is real load on Prometheus.\n\n"
    "The lab's Grafana is already in `observability/compose.yaml`: the `grafana/grafana:13.3.0` image on "
    "http://localhost:3000, user `admin`, password `admin`. Many older tutorials use the `grafana/grafana-oss` image. "
    "It stopped getting updates at version 12.4, so skip it.\n\n"
    "Grafana is the board, and Prometheus is the patient chart behind it. Next, we'll pick what to draw in each box."
)

S[1]["h"] = "Panels: pick the chart from the question"
S[1]["body"] = (
    "A car dashboard does not draw your speed as a table. It uses a dial, because the question is \"how fast, right "
    "now, and is that too fast?\" Grafana works the same way. A panel is one box on a dashboard: a query and a "
    "visualization, the kind of picture it draws. Start from the question the panel answers, then pick how to draw "
    "it:\n"
    "- How does it change over time? Time series, the line chart. Right most of the time.\n"
    "- What is the number right now? Stat: one big number with a small trend line behind it.\n"
    "- How close are we to a limit? Gauge: a dial from a minimum to a maximum, like disk use from 0 to 100%.\n"
    "- How do these things compare? Bar chart or bar gauge: one bar per path, pod or region.\n"
    "- What are the exact values? Table: rows and columns you can sort.\n"
    "- How are the values spread out? Heatmap: time across, buckets up the side, color for how many.\n\n"
    "A panel can hold several queries, named A, B, C and so on (the refId). The lab's latency panel has three: p50 "
    "in A, p95 in B and p99 in C. Each query can return many series, and the legend, the list of names under the "
    "chart, names them. Write `{{status}}` in the legend field and each line is named `200` or `500` from its labels.\n\n"
    "A stat panel squeezes a whole series into one number, and a setting called Calculation decides how: Last, Mean, "
    "Max and others. Choose it on purpose. A stat that shows the mean of the last 7 days hides a 10-minute outage. "
    "For \"right now\", use Last *, which means the last value that is not empty.\n\n"
    "Grafana 13 also suggests visualizations. It looks at the shape of your query result and offers a few charts "
    "that fit. Treat that as a first draft, and check it against your question.\n\n"
    "The picture is only as good as the question behind it. Next, the queries, and the helpers Grafana adds to them."
)

S[2]["h"] = "Queries: PromQL plus Grafana's helpers"
S[2]["body"] = (
    "The query editor has two modes. Builder lets you click a metric, labels and functions together. Code is a text "
    "box for PromQL. Both produce the same query, so use Builder to explore and Code once you know what you want.\n\n"
    "Grafana adds a few variables of its own to PromQL. The one you will use most is `$__rate_interval`. It goes "
    "where you would write the range in `rate()`:\n\n"
    "`sum(rate(hello_responses_total[$__rate_interval]))`\n\n"
    "Why not write `[1m]`? A graph panel sends a range query: Prometheus runs the same PromQL once for each point, at "
    "evenly spaced times. The gap between points is the step, and Grafana picks it from the time range and the "
    "panel's width.\n\n"
    "On the lab's 30-minute graph the step is 15 seconds, and `[1m]` is fine. On a 7-day graph the points are many "
    "minutes apart. A one-minute window then looks at one minute out of every ten and misses the spikes in between. "
    "It is like checking the speedometer for one second every ten minutes of a drive. The `$__rate_interval` "
    "variable grows with the step. Grafana takes the larger of two values:\n"
    "- the step plus one scrape interval;\n"
    "- four scrape intervals, the Prometheus advice from two lessons ago.\n\n"
    "It only works if Grafana knows the scrape interval. That is the `timeInterval: 15s` line in the lab's data "
    "source file, and it must match `scrape_interval` in `prometheus.yml`.\n\n"
    "**A fixed range that looks fine zoomed in goes blind zoomed out. Use $__rate_interval in every rate().**\n\n"
    "Check two more things on each query:\n"
    "- Range or instant. A range query returns many points, for graphs. An instant query returns one value per series, which is all a stat or a table needs.\n"
    "- Empty results. Before any request has failed, the 5xx series does not exist. An error ratio built on it shows \"No data\" instead of 0%. Adding `or vector(0)` gives you a real zero. The worked example shows both.\n\n"
    "The query now returns the right number. Next, we'll make that number readable by a human."
)

S[3]["h"] = "Units, thresholds and overrides: making a number readable"
S[3]["body"] = (
    "A car's dashboard says 120 km/h, not 33.3 metres per second, though both are true. And its rev counter has a "
    "red zone, so you never need to remember the number where the engine suffers. Grafana gives every panel the same "
    "two tools.\n\n"
    "Prometheus stores base units: seconds, bytes, and ratios between 0 and 1. That is right for storage and hard "
    "on a tired human. The unit setting fixes the display without touching the data:\n"
    "- 0.0347 with unit \"Percent (0.0-1.0)\" shows as 3.47%.\n"
    "- 0.231 with unit \"seconds\" shows as 231 ms.\n"
    "- 3.76 with unit \"requests/sec\" shows as 3.76 req/s.\n"
    "- 1610612736 with unit \"bytes (IEC)\" shows as 1.50 GiB.\n\n"
    "So do not multiply by 100 in PromQL to get a percentage. Keep the ratio and set the unit. In the JSON these are "
    "short codes: `percentunit`, `s`, `reqps`, `bytes`.\n\n"
    "A threshold is the red zone: a value where the color changes. The list starts with a base color, then adds "
    "steps upward. The lab's error ratio stat is green below 1%, orange from 1% and red from 5%. On a time series, "
    "thresholds can also draw a line or a shaded area, so you see the moment a line crossed into red.\n\n"
    "Mappings and overrides change the display further:\n"
    "- Value mappings turn numbers into words. The lab shows `up` = 1 as UP and 0 as DOWN.\n"
    "- Overrides change settings for some series only. The lab's rate graph paints the `500` line red, whatever color the palette would give it.\n\n"
    "Use color for what someone should act on, and leave the rest neutral. If every panel is red or green all day, "
    "people stop looking at the colors, the same way they stop hearing a car alarm in the street.\n\n"
    "Sometimes the numbers are right and readable, but in the wrong shape. Next, we'll reshape them."
)

S[4]["h"] = "Transformations: reshape the result inside Grafana"
S[4]["body"] = (
    "Sometimes the query returns the right numbers in the wrong shape. A transformation reshapes the result inside "
    "Grafana, after the query and before the drawing. You can chain several, and each one works on the output of the "
    "one before.\n\n"
    "The lab's table \"Requests by path and status\" is an example. Its query is an instant query with Format set to "
    "Table:\n\n"
    "`sum by (path, status) (increase(hello_responses_total{job=~\"$job\"}[5m]))`\n\n"
    "Prometheus returns one row per path and status, with the columns Time, path, status and Value. Two "
    "transformations make it readable:\n"
    "1. Organize fields by name: hide Time, rename Value to Requests and put the columns in order.\n"
    "2. Sort by: Requests, largest first.\n\n"
    "Other transformations you will meet:\n"
    "- Reduce: turn each series into one row (last, mean, max). Good for top-10 tables.\n"
    "- Labels to fields: turn series labels into table columns.\n"
    "- Join by field: line up two queries on a shared column, such as time or path.\n"
    "- Filter data by values: drop rows, for example everything under 1 request.\n"
    "- Add field from calculation: a new column computed from the others.\n\n"
    "My rule: if PromQL can do the maths, do it in PromQL. A query runs on the Prometheus server and also works in "
    "recording rules and alerts. A transformation exists only in this one panel.\n\n"
    "Use transformations for layout, and for joining data that PromQL cannot see together. One example is a metric "
    "next to a table from a SQL database, the kind of database that stores rows and columns.\n\n"
    "We have good panels. Next, we'll put them on one page that a tired person can read, and make that page serve "
    "more than one service."
)

S[5]["h"] = "Variables, annotations and a layout for on-call"
S[5]["body"] = (
    "A dashboard variable is a dropdown at the top of the dashboard. Its value goes into every query that mentions "
    "it, like the knob on a car radio that changes every speaker at once. The lab's dashboard has two:\n"
    "- `job` is a Query variable. Grafana asks Prometheus for every value of the `job` label on `hello_responses_total`. Today that is only `hello-devops`; with 40 services, the same dashboard would serve all 40.\n"
    "- `path` depends on `job`. It lists the paths of the chosen job, allows several at once and has an All option.\n\n"
    "With several values selected, Grafana inserts a regular expression, a text pattern, such as `/|/healthz`. So "
    "queries must use `=~`, not `=`: `{job=~\"$job\", path=~\"$path\"}`. Forgetting this is the most common variable "
    "bug.\n\n"
    "Annotations mark events on every time series panel, as a vertical line or a shaded band with a note. You can "
    "add one by hand (Ctrl or Cmd and click on a graph) or let a query find the events. The lab's dashboard marks "
    "when Prometheus alerts fire, using the `ALERTS` series. Real teams add a mark for every deploy. Then \"errors "
    "went up at 14:02\" becomes \"errors went up right after version 1.4 shipped\".\n\n"
    "For the layout, picture the doctor from the opening, or the engineer who opens this at 3 a.m. after a page. "
    "They need three answers fast: is it broken, since when, and where. So the lab's dashboard has three bands:\n"
    "1. Top: four stats. Requests per second, error ratio, p95 latency and whether Prometheus can reach the app.\n"
    "2. Middle: the same signals over time. Rate on the left, errors in the middle, duration on the right.\n"
    "3. Bottom: a collapsed Details row with a table per path and a latency heatmap, for when the top says something is wrong.\n\n"
    "Grafana's own [dashboard best "
    "practices](https://grafana.com/docs/grafana/latest/dashboards/build-dashboards/best-practices/) say: \"A "
    "dashboard should tell a story or answer a question.\" A 40-panel dashboard answers none. If you need more, build "
    "a second dashboard and link to it.\n\n"
    "The page is designed. Next, we'll make sure it cannot be lost or quietly changed."
)

S[6]["h"] = "Dashboards are JSON, so keep them in git"
S[6]["body"] = (
    "A dashboard built only by clicking lives in Grafana's own database. Nobody reviews its changes, and if that "
    "database is lost, so is the dashboard. Underneath, every dashboard is a JSON document. Open the dashboard "
    "settings, find JSON Model, and you see something like the lab's `hello-red.json`:\n"
    "- `uid` and `title`. The uid is part of the URL, `/d/hello-red/...`, so keep it fixed and links never break.\n"
    "- `templating.list`: the variables.\n"
    "- `panels`: one object per panel, with `type`, `title`, `gridPos` (its place on a grid 24 columns wide), `targets` (the queries) and `fieldConfig` (units, thresholds, overrides).\n\n"
    "If the JSON is the dashboard, you can keep it in git and review changes like code. Provisioning loads such "
    "files when Grafana starts. Grafana reads `/etc/grafana/provisioning/`, and the lab mounts its own folder there, "
    "which means the container sees a folder from your laptop at that path:\n"
    "- `datasources/`: YAML files that create data sources.\n"
    "- `dashboards/`: a provider file that says \"load every JSON file in this folder\".\n"
    "- `alerting/`: alert rules and contact points (next lesson).\n\n"
    "In the provider file, `allowUiUpdates: false` makes the Save button refuse, because the file is the truth. "
    "With `updateIntervalSeconds: 30`, Grafana checks the folder for changed files every 30 seconds. Keep that above "
    "10 on a Mac. At 10 or less, Grafana waits for file change events, and Docker bind mounts (the folder sharing "
    "just described) may never pass them on.\n\n"
    "**An edit made in the browser is a change nobody reviewed. Change the file, and let provisioning load it.**\n\n"
    "The everyday loop:\n"
    "1. Change the dashboard in the UI until you like it.\n"
    "2. Use Export to copy its JSON, and paste it over the file.\n"
    "3. Commit and open a pull request.\n"
    "4. Grafana picks up the file within 30 seconds.\n\n"
    "One trap: in provisioning YAML files, Grafana replaces `$NAME` with environment variables, settings passed in "
    "from outside the program. So a real dollar sign must be written `$$`. Dashboard JSON files are left alone, so "
    "`$job` in a query is safe there.\n\n"
    "A dashboard still only shows numbers, and only to someone who is looking. Say the graph shows errors since "
    "14:02. The next question is what the app said at 14:02, and that needs logs. The next lesson brings "
    "them into the same Grafana."
)

# The board and the car dashboard carry the analogy; the provisioning mistake is in section 7.
L.pop("analogy", None)
L.pop("mistake", None)
L["real_world"] = (
    "Dashboard uids end up in runbooks, the short how-to pages for each alert. In a payments company with many "
    "services, each team might own one RED dashboard in its repo, built from a shared template. CI checks the JSON "
    "on every pull request. The on-call runbook links straight to `/d/<uid>` URLs, which is why nobody changes a "
    "uid. Dashboards made by hand in the UI are fine for exploring, and they get cleaned up after 30 days."
)

W = L["worked"]["steps"]
W[0]["say"] = (
    "Start from the running lab: `docker compose up -d` in `observability/`, and the curl loop from the Commands "
    "list in a second terminal. First check that Grafana answers. The health address needs no login."
)
W[1]["say"] = (
    "Every panel sends its query to Grafana's `/api/ds/query` address, the same one your browser uses. The shell "
    "function `q` sends one instant query there and prints each series' labels and value. Start with the raw "
    "counter: totals since the app started."
)
W[2]["say"] = (
    "On a graph those totals only climb, so you cannot spot a spike. The `rate()` function turns each total into "
    "requests per second over the last minute. Wrapping it in `sum by (status)` adds the paths together, and that "
    "is the query behind the Rate panel. (The `/healthz` requests come from Docker's health check every 30 seconds.)"
)
W[3]["say"] = (
    "The error ratio needs one extra step. Nothing has failed yet, so no 5xx series exists. The plain division "
    "returns an empty frame, which a stat panel shows as No data. With `or vector(0)` the same question returns a "
    "real 0."
)
W[4]["say"] = (
    "Break the app: stop Redis. The `/` page needs it, so it returns 500, and each failing request now hangs for "
    "seconds while the app tries to reach Redis. After a minute, ask again. A ratio of 0.917 shows as 91.7% with the "
    "unit Percent (0.0-1.0), on red, because it is above the 0.05 threshold. Notice the traffic too: it fell from "
    "4.4 to 0.27 requests per second, because the curl loop waits for every slow error."
)
W[5]["say"] = (
    "Start Redis again. Then look at what `$__rate_interval` turns into. Send the Rate panel's query as a range "
    "query over the last 30 minutes, and Grafana reports the query it really ran. With a 15-second scrape interval "
    "the range became one minute: four scrapes."
)

T = L["task"]
T["steps"] = [
    "In `observability/`, create the two provisioning files and `grafana/dashboards/hello-red.json` from this lesson's Files section.",
    "Start the lab with `docker compose up -d` (or `docker compose restart grafana` if it already runs). Check the Grafana logs for provisioning errors.",
    "Start the traffic loop in a second terminal, open http://localhost:3000 and find the RED dashboard in the hello-devops folder. Try the Path dropdown with one path, then All.",
    "Change a panel title and try to save. Read Grafana's message and say in one sentence why it refuses.",
    "Create a new, empty dashboard and build a bar gauge panel: requests per second for each path, with unit requests/sec and one threshold of your choice.",
    "Copy that panel's JSON (panel menu, Inspect, Panel JSON) and add it to the `panels` list in `hello-red.json`, with a new `id` and a free `gridPos`.",
    "Check the file with `jq`, call the dashboards reload API (or wait 30 seconds) and refresh the browser.",
    "Stop Redis for two minutes and note which panels change first. Then start it again and delete the scratch dashboard.",
]
T["hints"] = [
    "A bar gauge wants one value per path: an instant query such as `sum by (path) (rate(hello_responses_total{job=~\"$job\"}[$__rate_interval]))` with the legend `{{path}}`.",
    "Put the new panel in the list just before the Details row and give it `\"gridPos\": {\"h\": 6, \"w\": 24, \"x\": 0, \"y\": 12}`. Grafana pushes the row down.",
    "Nothing changed? Run `docker compose logs grafana | grep -i dashboard` and look for a JSON error or a duplicate panel id.",
]
T["done_when"] = (
    "`curl -s -u admin:admin localhost:3000/api/dashboards/uid/hello-red | jq '.meta.provisioned, [.dashboard.panels[].title]'` "
    "prints `true` and a list that includes your new panel's title."
)

L["explain_back"]["prompt"] = (
    "Explain to a teammate, in 3 to 4 sentences, how a number gets from hello-devops onto your RED dashboard, and why "
    "the dashboard lives in a file in git. Mention data source, panel and provisioning."
)
L["explain_back"]["answer"] = (
    "Prometheus scrapes the app's /metrics page every 15 seconds and stores the samples. Grafana stores no metrics. "
    "Each panel holds a PromQL query; when the page loads, Grafana sends it to the Prometheus data source and draws "
    "the answer with the panel's units and thresholds. The dashboard itself is a JSON document, so we keep it in "
    "git, review changes in pull requests and let provisioning load it when Grafana starts. That way a new Grafana "
    "gets the same dashboards, and nobody's quick edit in the browser is lost or slips in unreviewed."
)

L["recap"] = [
    "Grafana stores dashboards, not data: every panel asks a data source such as Prometheus each time it loads.",
    "Pick the chart from the question: time series for change over time, stat for now, table for exact values, heatmap for spread.",
    "Use `$__rate_interval` in `rate()`, set the data source scrape interval, and add `or vector(0)` where an empty result should read as 0.",
    "Keep base units in PromQL and set the panel unit; color only what someone must act on.",
    "Lay out for on-call: RED numbers on top, the same signals over time below, details collapsed at the bottom.",
    "Keep dashboards as JSON in git with a fixed uid. A dashboard still shows only numbers, not what the app said.",
]

C = L["check"]
C[0]["q"] = "A stat panel shows the error ratio as 0.021. The team wants it to read 2.1% and turn red from 2%. What do you change?"
C[0]["why"] = (
    "Keep the base ratio from Prometheus. The percentunit unit shows 0.021 as 2.1%, and thresholds compare against "
    "the raw value, 0.02."
)
C[1]["q"] = (
    "Your `$instance` variable allows several values. With two instances picked, every panel shows No data. The "
    "query has `{instance=\"$instance\"}`. What is wrong?"
)
C[1]["why"] = "Grafana inserts something like a|b for several values, which only matches with the pattern matcher =~."
C[2]["q"] = (
    "You change `hello-red.json` on your Mac. Five minutes later Grafana in Docker still shows the old version, and "
    "`updateIntervalSeconds` is 5. What is the likely cause?"
)
C[2]["why"] = (
    "With 10 seconds or less, Grafana waits for file system events. Set it above 10 so Grafana checks the folder "
    "itself instead."
)

I = L["interview"]
I[0]["a"] = (
    "I start from the questions on-call has during a page: is it broken, since when, and where. The top row shows the "
    "RED numbers as stats: request rate, error ratio and a latency percentile, plus whether the target is up. Below "
    "them are the same signals as time series, with deploy annotations, so you can see when things changed. Details "
    "such as per-endpoint tables, heatmaps and machine metrics go in collapsed rows or linked dashboards. I use one "
    "variable for the service so the same dashboard works for every service, and I keep it in git."
)
I[1]["a"] = (
    "Dashboards made by hand drift, get copied and are lost when an instance is rebuilt. As code, each dashboard is "
    "JSON in git with a fixed uid, reviewed in pull requests and loaded by Grafana's file provisioning, the Terraform "
    "provider or Git Sync. I set the provider so the UI cannot save over provisioned dashboards, which makes the file "
    "the single source of truth. The workflow is to edit in the UI, export the JSON, commit it and let CI check that "
    "it parses."
)
I[2]["a"] = (
    "It is a Grafana variable for the range in rate() and increase(). Grafana sets it to the larger of two values: "
    "the step between graph points plus one scrape interval, or four scrape intervals. A fixed range like [1m] is "
    "fine zoomed in, but skips data when each graph point is many minutes apart, and a range under four scrapes can "
    "return nothing. It only works if the data source's scrape interval setting matches Prometheus."
)

L["deeper"]["body"] = (
    "One dashboard per service is a good start. With 30 services, people want a single page that says which one is "
    "unhappy. That is a different dashboard with a different job, and Grafana's best practices call it a "
    "drill-down.\n\n"
    "Build an overview first. Make one table panel with three instant queries, all grouped `by (job)`: request rate, "
    "error ratio and p95 latency. Then add these transformations:\n"
    "1. Join by field on `job`, so each service becomes one row with three columns.\n"
    "2. Organize fields, to rename the columns and hide the Time columns.\n"
    "3. Sort by error ratio, worst first.\n\n"
    "Add thresholds to the error column, and the unhappy service turns red at the top of the table.\n\n"
    "Each row should then link to the service dashboard. A data link on the table can point to "
    "`/d/hello-red?var-job=${__data.fields.job}`. Grafana fills in the job from the row you click, and `var-job` sets "
    "the dashboard variable from the URL. So one click takes on-call from \"something is red\" to the RED dashboard "
    "for exactly that service.\n\n"
    "The machines need their own view. RED describes how users experience a service. The USE method describes "
    "resources: utilization, saturation and errors for each CPU, disk and network card. node_exporter already gives "
    "you the numbers:\n"
    "- Utilization: the share of CPU time not idle, from `node_cpu_seconds_total`.\n"
    "- Saturation: load average compared with the number of CPUs (`node_load1`).\n"
    "- Errors: network errors from `node_network_receive_errs_total`.\n\n"
    "Keep RED and USE on separate dashboards and link them. They answer different questions, and mixing them makes "
    "both harder to read.\n\n"
    "Grafana's best practices page describes three maturity levels. Low means copied dashboards and one-offs that "
    "never go away. Medium means template variables instead of copies, drill-downs, and dashboard JSON in version "
    "control. High means no editing in the browser at all: scripts generate the dashboards, and viewers change what "
    "they see with variables. The next lesson shows the tools for that last step: Terraform, the Foundation SDK and "
    "Git Sync.\n\n"
    "Watch the cost too. Each panel is at least one query, and every refresh runs all of them again for every "
    "viewer. Set a sensible refresh (30 seconds, not 5), avoid huge time ranges by default, and move heavy "
    "expressions into recording rules that the panels read.\n\n"
    "Last, a newer format. Grafana 12 and 13 added a second dashboard format (v2) for dynamic dashboards with tabs "
    "and automatic layout. To provision a v2 dashboard from a file, it must use a Kubernetes-style wrapper. Classic "
    "JSON still works everywhere, and this course uses it."
)

L["closing"] = (
    "We started with a doctor in front of forty numbers in small handwriting. Now hello-devops has a board worth "
    "reading. Four stats sit on top, with the same signals over time below. The units make sense to a human, red "
    "appears only where someone must act, and the whole thing is a file in git. In the lab, open each stat panel and check its Calculation: "
    "is it Last *, or a mean that could hide an outage?\n\n"
    "Next, we'll put the app's own words next to its numbers. How do you search a day of log lines as easily as a "
    "graph, without paying to index every word?"
)

P.write_text(json.dumps(d, indent=1, ensure_ascii=False) + "\n")
print("d53 written")
