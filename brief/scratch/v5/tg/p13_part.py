"""Book-voice rewrite of Part 13's own fields. Writer: tg."""
import json, pathlib

P = pathlib.Path("/home/user/devops-from-zero/content/p13.json")
d = json.loads(P.read_text())

d["intro"] = (
    "Part 12 put the lab's numbers into Prometheus. This part puts them in front of people. The first lesson builds "
    "a Grafana dashboard that an engineer woken at night can read in seconds, and keeps it as a file in git. The "
    "second adds Grafana's own alerts, collects the app's log lines with Alloy and Loki, and tours the rest of the "
    "Grafana family of tools."
)

d["recap"] = [
    "Grafana stores dashboards, users and alert rules; the data stays in data sources such as Prometheus and Loki.",
    "Choose each panel's chart from its question, and set units and thresholds instead of rewriting PromQL.",
    "Use `$__rate_interval` for rate ranges, `=~` with multi-value variables, and `or vector(0)` where empty should mean zero.",
    "Design for on-call: RED stats on top, the same signals over time below, details collapsed or linked.",
    "Dashboards and alerts are code: provision them from files in git, with fixed uids, and change the file, not the UI.",
    "Grafana alerting runs rules on any data source; contact points and notification policies deliver the result.",
    "Loki indexes only labels, so keep labels few and bounded; LogQL filters and parses the text when you ask.",
    "Alloy collects logs (Promtail has reached end of life); Tempo, Mimir and Pyroscope cover traces, metrics and profiles.",
]

cards = [
    ("What does Grafana store, and what does it not store?", "It stores dashboards, users, settings and alert rules. Metrics and logs stay in the data sources."),
    ("What is `$__rate_interval`?", "A Grafana variable for the range in rate(): the larger of the step plus one scrape interval, and four scrape intervals."),
    ("Why add `or vector(0)` to an error ratio query?", "Before any error, the 5xx series does not exist, so the panel would show No data instead of 0%."),
    ("Which unit shows a ratio from 0 to 1 as a percentage?", "Percent (0.0-1.0), written `percentunit` in the dashboard JSON."),
    ("A variable allows several values. Which label matcher must the query use?", "`=~`, because Grafana inserts a text pattern such as a|b."),
    ("How should a RED dashboard for on-call be laid out?", "Stats on top, the same signals over time below, and details in collapsed rows or linked dashboards."),
    ("What does `allowUiUpdates: false` do for a provisioned dashboard?", "The UI cannot save over it. You change the JSON file in git instead."),
    ("Why set `updateIntervalSeconds` above 10 when Grafana runs in Docker on a Mac?", "At 10 or less Grafana waits for file events, which shared folders may not deliver. Above 10 it checks the folder itself."),
    ("Name the three main parts of Grafana alerting.", "Alert rules (queries, condition, pending period), contact points and notification policies."),
    ("What does `noDataState: OK` do on a Grafana alert rule?", "An empty query result counts as Normal instead of raising a DatasourceNoData alert."),
    ("What does Loki put in its index?", "Only the labels of each stream. The log text is compressed and not indexed."),
    ("What is the shape of a LogQL query?", "A stream selector in braces, then line filters, a parser and label filters, joined by |."),
    ("Why does a LogQL metric query over `| json` sometimes fail, and how do you fix it?", "Lines that are not JSON get an __error__ label; add `| __error__=\"\"` to drop them."),
    ("What replaced Promtail?", "Grafana Alloy. Promtail reached end of life on 2 March 2026."),
    ("What does LGTM stand for?", "Loki for logs, Grafana, Tempo for traces and Mimir for metrics."),
    ("Which Grafana tools from older tutorials should you not use any more?", "The grafana-oss image (frozen at 12.4), grafana-cli (now `grafana cli`), and Grizzly or grafanactl (replaced by gcx)."),
]
assert len(cards) == len(d["flashcards"])
for f, (front, back) in zip(d["flashcards"], cards):
    f["front"], f["back"] = front, back

whys = [
    "Grafana's own advice on what makes a dashboard useful, including RED and USE layouts and maturity levels.",
    "Every option for loading data sources, dashboards and alerts from files.",
    "A short hands-on walk-through of keeping dashboards as code with provisioning.",
    "How query variables and `$__rate_interval` work, with the common mistakes.",
    "The full list of transformations, each with a small before-and-after table.",
    "The alerting model on one page: rules, instances, contact points and policies.",
    "The reference for log queries and metric queries, with examples.",
    "Grafana's own small Loki stack, for practising LogQL on made-up logs.",
    "One container with Grafana, Loki, Tempo, Prometheus and Pyroscope, for trying every signal on a laptop.",
    "A beginner walk-through of building panels and choosing charts.",
    "Filters, parsers and formatting in LogQL, shown step by step.",
    "What dynamic dashboards, suggested dashboards and the other Grafana 13 features look like in use.",
]
assert len(whys) == len(d["resources"])
for r, w in zip(d["resources"], whys):
    r["why"] = w

quiz = [
    ("Prometheus CPU jumps every time the team's wall screen refreshes its 30-panel dashboard every 5 seconds. Which change helps most?",
     "Every refresh runs every panel's query. Fewer refreshes and ready-made recording rules cut the load."),
    ("A panel shows memory use as 1610612736. What is the best fix?",
     "Keep base units in the query and let the unit format them: 1610612736 bytes shows as 1.50 GiB."),
    ("You added `grafana/provisioning/datasources/loki.yaml`, but Grafana does not list Loki. What do you do?",
     "Data source files are read when Grafana starts; the dashboard folder checks do not cover them."),
    ("Which LogQL query returns lines from the web service that contain `timeout` but not `healthz`?",
     "The selector picks the stream by label; |= keeps lines containing a string and != drops lines containing one."),
    ("A Grafana rule has `for: 5m`. Its condition has been true for 2 minutes. What state is the instance in?",
     "The pending period works like Prometheus's for: the instance waits in Pending before it fires."),
    ("`docker compose logs web` shows new request lines, but Loki has had nothing from web for 10 minutes. Where do you look first?",
     "Alloy is the link between Docker and Loki, and its UI shows which component is failing."),
    ("Your company has 40 services that all expose the same RED metrics. How should their dashboards be built?",
     "A variable lets one dashboard serve every service; copies drift apart and pile up."),
    ("Why do the lab's panels use `sum(rate(...))` and never `rate(sum(...))`?",
     "Adding up first hides the moment one counter resets, so rate() would see a drop and get the speed wrong."),
    ("You run `docker compose -f compose.yaml -f compose.loki.yaml up -d`. compose.loki.yaml adds only an environment variable to `web`. What happens to `web`?",
     "Compose merges files in order: new settings are added to the existing service, and the changed container is created again."),
    ("A trace shows the checkout service is slow, and you want to know which function inside it burns the CPU. Which tool fits?",
     "Profiles show time per function; traces show time per service call."),
]
assert len(quiz) == len(d["quiz"])
for q, (qq, why) in zip(d["quiz"], quiz):
    q["q"], q["why"] = qq, why

P.write_text(json.dumps(d, indent=1, ensure_ascii=False) + "\n")
print("p13 part fields written")
