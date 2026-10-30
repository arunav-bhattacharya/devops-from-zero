#!/usr/bin/env python3
"""Build content/p10.json (Part 10: Dashboards with Grafana) from d45.py and d46.py.

Every console output below was captured from the lab on 2026-10-30 (Grafana 13.3.0,
Prometheus 3.15.1, Loki 3.7.9, Alloy 1.21.3), run with the real observability/compose.yaml
plus compose.loki.yaml, on test ports (Grafana 13000) that are shown here as 3000.
"""
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from d45 import D45, Q_FUNC, DOC_BEST, DOC_PROV, DOC_PROMVARS, TUT_PROV, VID_VIZ, DOC_TRANSFORM  # noqa: E402
from d46 import D46, DOC_ALERT, DOC_LOGQL, LOKI_QS, LGTM_REPO, VID_LOGQL, VID_G13, VID_GITSYNC  # noqa: E402

OUT = pathlib.Path("/home/user/devops-from-zero/content/p10.json")

RATIO = 'sum(rate(hello_responses_total{job="hello-devops", status=~"5.."}[1m])) / sum(rate(hello_responses_total{job="hello-devops"}[1m]))'
RATIO0 = '(sum(rate(hello_responses_total{job="hello-devops", status=~"5.."}[1m])) or vector(0)) / sum(rate(hello_responses_total{job="hello-devops"}[1m]))'

D45["worked"] = {
    "title": "From a raw counter to a number on-call can read",
    "steps": [
        {
            "say": "Start from the running lab: `docker compose up -d` in `observability/`, and the curl loop from the Commands list in a second terminal. First check that Grafana answers. The health endpoint needs no login.",
            "code": "$ curl -s localhost:3000/api/health\n{\n  \"database\": \"ok\",\n  \"version\": \"13.3.0\",\n  \"commit\": \"6f8ce3c693b493043ebcd4787566d2b6b118b0f0\"\n}",
            "lang": "console",
        },
        {
            "say": "Every panel sends its query to Grafana's `/api/ds/query` endpoint, the same one your browser uses. The shell function `q` sends one instant query there and prints each series' labels and value. Start with the raw counter: totals since the app started.",
            "code": Q_FUNC + "\n$ q 'hello_responses_total{job=\"hello-devops\"}'\n{\"labels\":{\"path\":\"/\",\"status\":\"200\"},\"value\":563}\n{\"labels\":{\"path\":\"/healthz\",\"status\":\"200\"},\"value\":4}",
            "lang": "console",
        },
        {
            "say": "On a graph those totals only climb, so you can't spot a spike. The `rate()` function turns each total into requests per second over the last minute. Wrapping it in `sum by (status)` adds the paths together, and that is the query behind the Rate panel. (The `/healthz` requests come from Docker's health check every 30 seconds.)",
            "code": "$ q 'rate(hello_responses_total{job=\"hello-devops\"}[1m])'\n{\"labels\":{\"path\":\"/\",\"status\":\"200\"},\"value\":4.377777777777777}\n{\"labels\":{\"path\":\"/healthz\",\"status\":\"200\"},\"value\":0.04444444444444444}\n$ q 'sum by (status) (rate(hello_responses_total{job=\"hello-devops\"}[1m]))'\n{\"labels\":{\"status\":\"200\"},\"value\":4.422222222222222}",
            "lang": "console",
        },
        {
            "say": "Now the error ratio. Nothing has failed yet, so no 5xx series exists. The plain division returns an empty frame, which a stat panel shows as No data. With `or vector(0)` the same question returns a real 0.",
            "code": "$ q '" + RATIO + "'\n{\"labels\":null,\"value\":null}\n$ q '" + RATIO0 + "'\n{\"labels\":{},\"value\":0}",
            "lang": "console",
        },
        {
            "say": "Break the app: stop Redis. The `/` page needs it, so it returns 500, and each failing request now hangs for seconds while the app tries to reach Redis. After a minute, ask again. A ratio of 0.917 shows as 91.7% with the unit Percent (0.0-1.0), on red, because it is above the 0.05 threshold. Notice the traffic too: it fell from 4.4 to 0.27 requests per second, because the curl loop waits for every slow error.",
            "code": "$ docker compose stop redis\n$ q '" + RATIO0 + "'\n{\"labels\":{},\"value\":0.9166666666666667}\n$ q 'sum by (status) (rate(hello_responses_total{job=\"hello-devops\"}[1m]))'\n{\"labels\":{\"status\":\"200\"},\"value\":0.02222222222222222}\n{\"labels\":{\"status\":\"500\"},\"value\":0.2444444444444444}",
            "lang": "console",
        },
        {
            "say": "Start Redis again. Then look at what `$__rate_interval` turns into. Send the Rate panel's query as a range query over the last 30 minutes, and Grafana reports the query it really ran. With a 15-second scrape interval the range became one minute: four scrapes.",
            "code": "$ docker compose start redis\n$ jq -n '{queries:[{refId:\"A\",datasource:{uid:\"prometheus\"},expr:\"sum(rate(hello_responses_total[$__rate_interval]))\",range:true,intervalMs:15000,maxDataPoints:800}],from:\"now-30m\",to:\"now\"}' \\\n    | curl -s -u admin:admin -H 'Content-Type: application/json' localhost:3000/api/ds/query -d @- \\\n    | jq -r '.results.A.frames[0].schema.meta.executedQueryString'\nExpr: sum(rate(hello_responses_total[1m0s]))\nStep: 15s",
            "lang": "console",
        },
    ],
}

RULES = "curl -s -u admin:admin localhost:3000/api/prometheus/grafana/api/v1/rules | jq -c '.data.groups[].rules[] | {name, state}'"

D46["worked"] = {
    "title": "Watch a Grafana alert go from Normal to Firing and back",
    "steps": [
        {
            "say": "Save `hello-alerts.yaml` from the Files section in `grafana/provisioning/alerting/` and restart Grafana. Then ask Grafana what it loaded. The field `provenance: file` means the rule came from a file, so the UI won't let anyone edit it.",
            "code": "$ docker compose restart grafana\n$ curl -s -u admin:admin localhost:3000/api/v1/provisioning/alert-rules | jq '.[] | {title, ruleGroup, for, condition, provenance}'\n{\n  \"title\": \"HelloErrorRatioHigh\",\n  \"ruleGroup\": \"hello-devops\",\n  \"for\": \"1m\",\n  \"condition\": \"C\",\n  \"provenance\": \"file\"\n}\n$ curl -s -u admin:admin localhost:3000/api/v1/provisioning/contact-points | jq -c '.[] | {name, type, url: .settings.url}'\n{\"name\":\"lab-webhook\",\"type\":\"webhook\",\"url\":\"http://webhook:5001/grafana\"}",
            "lang": "console",
        },
        {
            "say": "With the traffic loop running and Redis up, the rule is inactive: almost nothing fails, so condition C is false. Break the app the same way as on Day 45.",
            "code": "$ " + RULES + "\n{\"name\":\"HelloErrorRatioHigh\",\"state\":\"inactive\"}\n$ docker compose stop redis",
            "lang": "console",
        },
        {
            "say": "Watch the state with a small loop that prints a line only when it changes (times are UTC). Redis stopped at 05:22:30. The rule looks at a 2-minute window and runs every 30 seconds, so the ratio crossed 5% at 05:24:04 and the rule turned Pending. It stayed true for the whole pending period of one minute, and at 05:25:05 it fired.",
            "code": "$ prev=; while true; do\n    s=$(" + RULES + ")\n    [ \"$s\" != \"$prev\" ] && echo \"$(date -u +%T) $s\" && prev=$s\n    sleep 5\n  done\n05:23:49 {\"name\":\"HelloErrorRatioHigh\",\"state\":\"inactive\"}\n05:24:04 {\"name\":\"HelloErrorRatioHigh\",\"state\":\"pending\"}\n05:25:05 {\"name\":\"HelloErrorRatioHigh\",\"state\":\"firing\"}",
            "lang": "console",
        },
        {
            "say": "Stop the loop with Ctrl+C and read the webhook's last few minutes. The `[lab-webhook]` prefix is Grafana's contact point. The summary comes from the rule's annotation template, which turned the value of query A into a percentage. The `[pager]` line is the Day 44 fast-burn alert, sent by Alertmanager to the same webhook. Its 4.5% is the 1-hour error ratio, which moves much slower than Grafana's 2-minute window.",
            "code": "$ docker compose logs --since 5m webhook\nwebhook-1  | [lab-webhook] FIRING HelloErrorRatioHigh job=hello-devops severity=ticket: 89.66% of hello-devops requests fail\nwebhook-1  | [pager] FIRING HelloErrorBudgetFastBurn job=hello-devops severity=page: 4.463% of hello-devops requests fail (fast burn)",
            "lang": "console",
        },
        {
            "say": "Start Redis. Once the 2-minute ratio drops back under 5%, the instance returns to Normal and Grafana sends a resolved message. The same thing works for any data source, which is the point of the next sections: the query could just as well count error lines in Loki.",
            "code": "$ docker compose start redis\n$ docker compose logs --since 5m webhook | grep lab-webhook\nwebhook-1  | [lab-webhook] FIRING HelloErrorRatioHigh job=hello-devops severity=ticket: 89.66% of hello-devops requests fail\nwebhook-1  | [lab-webhook] RESOLVED HelloErrorRatioHigh job=hello-devops severity=ticket: 0% of hello-devops requests fail",
            "lang": "console",
        },
    ],
}


def ordered(d):
    keys = ["id", "title", "minutes", "goal", "guess", "terms", "sections", "analogy", "diagram", "diagram_caption",
            "worked", "code", "commands", "mistake", "real_world", "task", "explain_back", "recap", "check",
            "interview", "deeper", "sources"]
    return {k: d[k] for k in keys}


PART = {
    "part": 10,
    "title": "Dashboards with Grafana",
    "intro": (
        "Part 9 put the lab's metrics into Prometheus. This part puts them in front of people. "
        "Day 45 builds a Grafana dashboard that an on-call engineer can read in seconds, and keeps it as code in git. "
        "Day 46 adds Grafana alerting, collects logs with Alloy and Loki, and tours the rest of the Grafana stack."
    ),
    "lessons": [ordered(D45), ordered(D46)],
    "recap": [
        "Grafana stores dashboards, users and alert rules; the data stays in data sources such as Prometheus and Loki.",
        "Choose each panel's visualization from its question, and set units and thresholds instead of rewriting PromQL.",
        "Use `$__rate_interval` for rate ranges, `=~` with multi-value variables, and `or vector(0)` where empty should mean zero.",
        "Design for on-call: RED stats on top, the same signals over time below, details collapsed or linked.",
        "Dashboards and alerts are code: provision them from files in git, with fixed uids, and change the file, not the UI.",
        "Grafana alerting runs rules on any data source; contact points and notification policies deliver the result.",
        "Loki indexes only labels, so keep labels few and bounded; LogQL filters and parses the text at query time.",
        "Alloy collects logs (Promtail has reached end of life); Tempo, Mimir and Pyroscope cover traces, metrics and profiles.",
    ],
    "flashcards": [
        {"front": "What does Grafana store, and what does it not store?", "back": "It stores dashboards, users, settings and alert rules. Metrics and logs stay in the data sources."},
        {"front": "What is `$__rate_interval`?", "back": "A Grafana variable for the range in rate(): the larger of the step plus one scrape interval, and four scrape intervals."},
        {"front": "Why add `or vector(0)` to an error ratio query?", "back": "Before any error, the 5xx series doesn't exist, so the panel would show No data instead of 0%."},
        {"front": "Which unit shows a ratio from 0 to 1 as a percentage?", "back": "Percent (0.0-1.0), written `percentunit` in the dashboard JSON."},
        {"front": "A variable allows several values. Which label matcher must the query use?", "back": "`=~`, because Grafana inserts a regular expression such as a|b."},
        {"front": "How should a RED dashboard for on-call be laid out?", "back": "Stats on top, the same signals over time below, and details in collapsed rows or linked dashboards."},
        {"front": "What does `allowUiUpdates: false` do for a provisioned dashboard?", "back": "The UI can't save over it. You change the JSON file in git instead."},
        {"front": "Why set `updateIntervalSeconds` above 10 when Grafana runs in Docker on a Mac?", "back": "At 10 or less Grafana waits for file events, which bind mounts may not deliver. Above 10 it polls."},
        {"front": "Name the three main parts of Grafana alerting.", "back": "Alert rules (queries, condition, pending period), contact points and notification policies."},
        {"front": "What does `noDataState: OK` do on a Grafana alert rule?", "back": "An empty query result counts as Normal instead of raising a DatasourceNoData alert."},
        {"front": "What does Loki put in its index?", "back": "Only the labels of each stream. The log text is compressed and not indexed."},
        {"front": "What is the shape of a LogQL query?", "back": "A stream selector in braces, then line filters, a parser and label filters, joined by |."},
        {"front": "Why does a LogQL metric query over `| json` sometimes fail, and how do you fix it?", "back": "Lines that are not JSON get an __error__ label; add `| __error__=\"\"` to drop them."},
        {"front": "What replaced Promtail?", "back": "Grafana Alloy. Promtail reached end of life on 2 March 2026."},
        {"front": "What does LGTM stand for?", "back": "Loki for logs, Grafana, Tempo for traces and Mimir for metrics."},
        {"front": "Which Grafana tools from older tutorials should you not use any more?", "back": "The grafana-oss image (frozen at 12.4), grafana-cli (now `grafana cli`), and Grizzly or grafanactl (replaced by gcx)."},
    ],
    "resources": [
        {"title": "Grafana docs: dashboard best practices", "url": DOC_BEST, "kind": "docs",
         "why": "Grafana's own advice on what makes a dashboard useful, including RED and USE layouts and maturity levels."},
        {"title": "Grafana docs: provision Grafana", "url": DOC_PROV, "kind": "docs",
         "why": "Every option for loading data sources, dashboards and alerts from files."},
        {"title": "Grafana tutorial: provision dashboards and data sources", "url": TUT_PROV, "kind": "read",
         "why": "A short hands-on walk-through of dashboards as code with provisioning."},
        {"title": "Grafana docs: Prometheus template variables", "url": DOC_PROMVARS, "kind": "docs",
         "why": "How query variables and `$__rate_interval` work, with the common mistakes."},
        {"title": "Grafana docs: transform data", "url": DOC_TRANSFORM, "kind": "docs",
         "why": "The full list of transformations, each with a small before-and-after table."},
        {"title": "Grafana docs: introduction to Grafana Alerting", "url": DOC_ALERT, "kind": "docs",
         "why": "The alerting model in one page: rules, instances, contact points and policies."},
        {"title": "Loki docs: query Loki with LogQL", "url": DOC_LOGQL, "kind": "docs",
         "why": "The reference for log queries and metric queries, with examples."},
        {"title": "Loki quickstart with Docker Compose and Alloy", "url": LOKI_QS, "kind": "read",
         "why": "Grafana's own small Loki stack to practise LogQL on generated logs."},
        {"title": "docker-otel-lgtm on GitHub", "url": LGTM_REPO, "kind": "docs",
         "why": "One container with Grafana, Loki, Tempo, Prometheus and Pyroscope for trying every signal on a laptop."},
        {"title": "Creating visualizations with Grafana (video)", "url": VID_VIZ, "kind": "watch",
         "why": "A beginner walk-through of building panels and choosing visualizations."},
        {"title": "How to query Grafana Loki with LogQL (video)", "url": VID_LOGQL, "kind": "watch",
         "why": "Filters, parsers and formatting in LogQL, shown step by step."},
        {"title": "Grafana 13 deep dive from GrafanaCON 2026 (video)", "url": VID_G13, "kind": "watch",
         "why": "What dynamic dashboards, suggested dashboards and the other Grafana 13 features look like in use."},
    ],
    "quiz": [
        {
            "q": "Prometheus CPU jumps every time the team's wall screen refreshes its 30-panel dashboard every 5 seconds. Which change helps most?",
            "options": [
                "Use recording rules and refresh every 30 seconds",
                "Turn every time series panel into a stat panel",
                "Set `allowUiUpdates: true` in the dashboard provider",
                "Add a dashboard variable with an All option",
            ],
            "answer": 0,
            "why": "Every refresh runs every panel's query; fewer refreshes and precomputed recording rules cut the load.",
        },
        {
            "q": "A panel shows memory use as 1610612736. What is the best fix?",
            "options": [
                "Divide by 1024 three times in the PromQL query",
                "Add a transformation that renames the field to GiB",
                "Set the panel unit to bytes (IEC)",
                "Switch the panel to a gauge from 0 to 100",
            ],
            "answer": 2,
            "why": "Keep base units in the query and let the unit format them: 1610612736 bytes shows as 1.50 GiB.",
        },
        {
            "q": "You added `grafana/provisioning/datasources/loki.yaml`, but Grafana doesn't list Loki. What do you do?",
            "options": [
                "Add the Loki data source to the dashboard JSON file",
                "Wait 30 seconds for the dashboard provider to poll",
                "Rename the file to end in .json instead of .yaml",
                "Restart Grafana or call the data source reload API",
            ],
            "answer": 3,
            "why": "Data source files are read at start; the dashboard provider's polling doesn't cover them.",
        },
        {
            "q": "Which LogQL query returns lines from the web service that contain `timeout` but not `healthz`?",
            "options": [
                "`{service_name=\"web\", text=\"timeout\"} != \"healthz\"`",
                "`{service_name=\"web\"} |= \"timeout\" != \"healthz\"`",
                "`{service_name=\"web\"} | json | timeout != healthz`",
                "`{service_name=~\"timeout\"} |= \"web\" != \"healthz\"`",
            ],
            "answer": 1,
            "why": "The selector picks the stream by label; |= keeps lines containing a string and != drops lines containing one.",
        },
        {
            "q": "A Grafana rule has `for: 5m`. Its condition has been true for 2 minutes. What state is the instance in?",
            "options": [
                "Normal, because no notification has been sent yet",
                "Firing, because the condition is true",
                "Pending, until the condition has held for 5 minutes",
                "NoData, because the pending period is not over",
            ],
            "answer": 2,
            "why": "The pending period works like Prometheus's for: the instance waits in Pending before it fires.",
        },
        {
            "q": "`docker compose logs web` shows new request lines, but Loki has had nothing from web for 10 minutes. Where do you look first?",
            "options": [
                "The Alloy UI, to see which component is unhealthy",
                "The Grafana dashboard provider settings file",
                "The Prometheus scrape config for the web job",
                "The routing tree in the Alertmanager config",
            ],
            "answer": 0,
            "why": "Alloy is the link between Docker and Loki; its UI shows which component is failing.",
        },
        {
            "q": "Your company has 40 services that all expose the same RED metrics. How should their dashboards be built?",
            "options": [
                "Copy the dashboard 40 times and change the job in each copy",
                "Build one panel per service on one very large dashboard",
                "Keep one dashboard in the UI and edit the queries for each service",
                "Build one dashboard with a job variable, kept as code",
            ],
            "answer": 3,
            "why": "A variable lets one dashboard serve every service; copies drift and become sprawl.",
        },
        {
            "q": "Why do the lab's panels use `sum(rate(...))` and never `rate(sum(...))`?",
            "options": [
                "Because rate() only accepts a single series as input",
                "Because rate() must see each raw counter to handle restarts correctly",
                "Because sum() is slower when it runs before rate()",
                "Because Grafana can't draw the result of rate(sum())",
            ],
            "answer": 1,
            "why": "Summing first hides the moment one counter resets, so rate() would see a drop and get the speed wrong.",
            "from": "Part 9",
        },
        {
            "q": "You run `docker compose -f compose.yaml -f compose.loki.yaml up -d`. compose.loki.yaml adds only an environment variable to `web`. What happens to `web`?",
            "options": [
                "It loses its build, command and ports, because the second file replaces it",
                "Nothing, because a service defined twice is ignored",
                "It keeps its settings from compose.yaml, gains the variable and is recreated",
                "Compose stops with an error about a duplicate service",
            ],
            "answer": 2,
            "why": "Compose merges files in order: new keys are added to the existing service, and the changed container is recreated.",
            "from": "Part 3",
        },
        {
            "q": "A trace shows the checkout service is slow, and you want to know which function inside it burns the CPU. Which tool fits?",
            "options": [
                "Loki, with a LogQL metric query",
                "Mimir, with long-term PromQL",
                "Alloy, with a relabel rule",
                "Pyroscope, with a flame graph",
            ],
            "answer": 3,
            "why": "Profiles show time per function; traces show time per service call.",
        },
    ],
}

OUT.write_text(json.dumps(PART, indent=1, ensure_ascii=False) + "\n")
print("wrote", OUT)
