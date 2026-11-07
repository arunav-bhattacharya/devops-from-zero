#!/usr/bin/env python3
"""Human-writing pass (v3, blog mode) for Parts 9 and 10 (d41 to d46).
Loads the current content JSON, replaces prose only, writes it back.
Each edit is either a full replacement (old=None) or an exact substring swap that must match once."""
import json
import pathlib

ROOT = pathlib.Path("/home/user/devops-from-zero")


def get(d, path):
    cur = d
    for k in path[:-1]:
        cur = lesson(d, k) if isinstance(k, str) and k.startswith("d") and cur is d else cur[k]
    return cur, path[-1]


def lesson(d, lid):
    return next(L for L in d["lessons"] if L["id"] == lid)


def apply(d, edits, name):
    for path, old, new in edits:
        parent, key = get(d, path)
        cur = parent[key]
        if old is None:
            parent[key] = new
        else:
            n = cur.count(old)
            assert n == 1, f"{name} {path}: expected 1 match, got {n}: {old[:60]!r}"
            parent[key] = cur.replace(old, new)


# ---------------------------------------------------------------- Part 9
P9 = [
    # part level
    (("intro",), None,
     "Part 8 left hello-devops running on kind, deployed by Argo CD. This part shows you how it is doing. "
     "Day 41 covers the ideas every monitoring tool shares: signals, SLOs, error budgets and alerts on what users feel. "
     "Days 42 to 44 put them to work with Prometheus in a Compose lab on your laptop. "
     "You learn PromQL up to a full RED view, send alerts to a receiver, and then monitor the app on Kubernetes the same way."),
    (("resources", 0, "why"), None,
     "Start here: the official map of the server, exporters, Pushgateway and Alertmanager, with the architecture picture."),
    (("resources", 9, "why"), None,
     "More from Julius Volz: short videos on histograms, rates and the finer points of PromQL."),
    (("resources", 10, "why"), None,
     "Read this when increase() returns a fraction or a young series reads low; it shows the exact maths."),

    # d41
    (("d41", "sections", 0, "body"),
     "adds one more split worth knowing:",
     "also splits monitoring by where you look from:"),
    (("d41", "sections", 2, "body"),
     "Which few numbers should you watch first? Three well-known checklists answer that, and they overlap a lot.",
     "Three well-known checklists tell you which few numbers to watch first, and they overlap a lot."),
    (("d41", "sections", 2, "body"),
     "Grafana's dashboard guide says it well: USE",
     "Grafana's dashboard guide sums up the split: USE"),
    (("d41", "sections", 3, "body"),
     "gives the reason: users rarely notice the difference between high and extreme reliability. Their own phone and mobile network fail far more often. Each extra nine costs far more work, and users barely notice it.",
     "explains why. Users rarely notice the difference between high and extreme reliability, because their own phone and mobile network fail far more often. Each extra nine still costs far more work."),
    (("d41", "sections", 4, "body"),
     "The budget turns an argument into arithmetic. Developers want to ship, operators want quiet nights, and both can look at the same number.",
     "Developers want to ship and operators want quiet nights. The budget gives both sides the same number to argue over."),
    (("d41", "sections", 4, "body"),
     "Burn rate works better than a raw error count because it already knows your traffic and your target.",
     "Burn rate beats a raw error count because it is already scaled to your traffic and your target."),
    (("d41", "sections", 5, "body"),
     "so every page must be urgent, real and something a human can act on. The [Prometheus alerting guide](https://prometheus.io/docs/practices/alerting/) puts it in one line:",
     "so a page has to be urgent and real, and a human must be able to do something about it. The [Prometheus alerting guide](https://prometheus.io/docs/practices/alerting/) gives the same advice:"),
    (("d41", "sections", 6, "body"),
     "The SLO links all of this. It defines what working means, the burn rate decides when someone gets paged, and the postmortem decides what to change so next month's budget lasts longer.",
     "The SLO ties these habits together. It says what working means, and the burn rate against it decides when someone gets paged. The postmortem then decides what to change so next month's budget lasts longer."),
    (("d41", "analogy"), None,
     "A train company promises that 99% of its trains arrive within five minutes of the timetable each month. "
     "That promise is the SLO, and the 1% of trains allowed to be late is the error budget. "
     "If little of it is used by mid-month, the company can close a track for repairs; if a storm has used it all, the repairs wait. "
     "The comparison stops at timing. "
     "Trains run on a fixed timetable, but software fails in sudden bursts, so you also watch how fast the budget burns."),
    (("d41", "worked", "steps", 2, "say"),
     "spends almost half the month. That tells you something concrete: a rollback must take minutes, not an hour.",
     "spends almost half the month, so a rollback has to take minutes, not an hour."),
    (("d41", "mistake"), None,
     "A page on CPU above 80%, memory above 90% or any pod restart looks responsible. "
     "These fire all the time without users noticing, so people stop trusting the pager. "
     "Page on symptoms (error budget burn, the service not answering) and put causes on a dashboard you open once a page fires."),
    (("d41", "real_world"), None,
     "For card payments, an SLO might read: 99.95% of authorizations answered without error within 2 seconds, over 28 days. "
     "The on-call engineer is paged only on a fast burn of that budget. "
     "When the budget runs out, the team's written policy freezes feature releases until two weeks of clean numbers come back."),
    (("d41", "interview", 2, "a"), None,
     "Start with a simple SLI, such as successful requests over all requests, and measure what the service achieves today. "
     "Then pick a target a little below that, so the team is not paged from day one. "
     "Agree with the product owner on what happens when the budget runs out. "
     "Review the SLO every quarter: if users complain while it is met, the SLI or the target is wrong. "
     "I would never pick 100%, because it leaves no room for deploys and costs far more than users can notice."),

    # d42
    (("d42", "sections", 2, "body"),
     "Two details surprise most people.",
     "Two details look odd at first."),
    (("d42", "sections", 3, "body"),
     "This is the most important idea in Prometheus. A **time series** is identified",
     "Everything Prometheus stores and queries is a time series. Each **time series** is identified"),
    (("d42", "sections", 5, "body"),
     "Labels look free, and this trips most people up. Each new label value creates new series,",
     "A label is one extra word in your code, so it looks free. In Prometheus, each new label value creates new series,"),
    (("d42", "analogy"), None,
     "Prometheus is a meter reader on a fixed round, passing every house every 15 seconds. "
     "Each house shows its meters through the window (the /metrics page), and the reader writes down every number with the time and the house address (the labels). "
     "If a house does not answer, the reader notes that too, which is up = 0. "
     "A real house has a fixed number of meters, though. "
     "An app that invents a new label value per user keeps adding meters, thousands of them, and Prometheus has to read and store every one."),
    (("d42", "real_world"), None,
     "Cardinality is easiest to catch before the code merges. "
     "Picture a payments company where every service exposes /metrics, and Prometheus finds the pods through Kubernetes service discovery. "
     "Its code review checklist asks one question about every new label: how many values can it have? "
     "A `merchant_id` label would mean one series per merchant per route per bucket, so merchant-level detail goes into logs instead."),

    (("d42", "check", 1, "why"), None,
     "Queue length goes up and down, which is what a gauge measures."),
    (("d42", "sections", 5, "body"),
     "Now imagine someone adds",
     "Suppose someone adds"),

    # d43
    (("d43", "sections", 2, "body"),
     "Two relatives:",
     "`rate()` has two relatives:"),
    (("d43", "sections", 5, "body"),
     "Two real examples:",
     "Both of these happened in the lab:"),
    (("d43", "worked", "steps", 3, "say"),
     "Now break the app's dependency and wait about 90 seconds.",
     "Break the app's dependency next, and wait about 90 seconds."),
    (("d43", "sections", 1, "body"),
     "An empty result is not zero. It means no series matched, and this trips most people up.",
     "An empty result is not zero, and the two are easy to confuse. Empty means no series matched."),
    (("d43", "sections", 3, "body"),
     "The `/healthz` line is the Docker health check from Day 16: one request every 30 seconds is about 0.03 a second. Aggregation shows you traffic you did not know about.",
     "The `/healthz` line is traffic you may not have known about: the Docker health check from Day 16, one request every 30 seconds, about 0.03 a second."),
    (("d43", "analogy"), None,
     "Picture a huge spreadsheet: one column per series, one row per scrape. "
     "A selector picks columns, and a range like [5m] picks the last rows. "
     "Then rate() is the slope of each column, and sum by (path) is a pivot table that adds columns together. "
     "Real data is messier than that. The rows never line up perfectly, because each target is scraped at a slightly different moment, "
     "so Prometheus has to estimate values at the edges of every window."),
    (("d43", "mistake"), None,
     "A range that is too short for rate(), such as [10s] or [15s] with a 15-second scrape, fails quietly. "
     "The query returns no error; series just disappear from the result now and then, and a graph shows gaps or nothing at all. "
     "Use at least 4 times the scrape interval, and in Grafana use its $__rate_interval variable (Day 45)."),
    (("d43", "real_world"), None,
     "In an incident review, a strange graph often gets one question first: was that a real change, or an empty result, a NaN or a too-short range? "
     "A payments company with many services might also give every service the same three RED recording rules from a shared template. "
     "Then dashboards and alerts read cheap precomputed series, and every team gets the same number for its error ratio."),
    (("d43", "interview", 0, "a"), None,
     "The rate() function gives the average per-second increase of a counter over the whole range, and it handles counter resets. "
     "That makes it the default for graphs and alerts. "
     "With irate(), only the last two samples in the range count, so it reacts fast but is noisy: fine for a zoomed-in graph, wrong for an alert. "
     "As for increase(), it is rate() multiplied by the range in seconds, so it reads as a count but can return fractions. "
     "All three need at least two samples in the range."),

    # d44
    (("d44", "sections", 4, "body"),
     "Two defaults surprise people.",
     "Two defaults look like bugs until you know them."),
    (("d44", "sections", 5, "body"),
     "This is the gotcha. The chart's Prometheus",
     "Labels also decide whether Prometheus reads your objects at all. The chart's Prometheus"),
    (("d44", "sections", 6, "body"),
     "Then there is time. One Prometheus",
     "History is the other limit. One Prometheus"),
    (("d44", "analogy"), None,
     "In a building's fire system, Prometheus is the smoke detector and Alertmanager is the alarm desk. "
     "A detector only decides that there is smoke, and only after it lasts a few seconds (for:). "
     "The desk turns ten detectors on one floor into one call (grouping). "
     "It sends a fire to the fire brigade and a faulty sensor to the caretaker (routing). "
     "It ignores floor alarms while the whole building is already evacuating (inhibition), and stays quiet during a planned fire drill (a silence). "
     "A person at a real desk would notice a call going to the wrong place. "
     "Alertmanager follows its rules exactly as written, so a wrong route sends the page nowhere."),
    (("d44", "mistake"), None,
     "If a ServiceMonitor or PrometheusRule lacks the release label of the Helm release, kubectl still accepts it, nothing logs an error, and Prometheus never sees it. "
     "Check Status, Target health and Rule health in the Prometheus UI after every apply, and compare labels before you debug anything else."),
    (("d44", "real_world"), None,
     "Monitoring config at PayFlow, a made-up payments company, ships in the same Helm chart as the code: every team puts a ServiceMonitor and a PrometheusRule next to its Deployment. "
     "So monitoring changes go through code review like any other change, and CI runs promtool test rules on every pull request. "
     "Alertmanager routes severity=page to PagerDuty and everything else to a Slack channel per team. "
     "Planned maintenance always starts with a silence that has a comment and an author."),
    (("d44", "deeper", "body"),
     "Finally, the Kubernetes pods still run two gunicorn workers.",
     "One gap remains: the Kubernetes pods still run two gunicorn workers."),
]

# ---------------------------------------------------------------- Part 10
P10 = [
    # d45
    (("d45", "sections", 1, "body"),
     "A stat panel squeezes a whole series into one number. A setting called Calculation decides how: Last, Mean, Max and others. This trips people up. A stat",
     "A stat panel squeezes a whole series into one number, and a setting called Calculation decides how: Last, Mean, Max and others. Choose it on purpose. A stat"),
    (("d45", "sections", 2, "body"),
     "Two more settings matter:",
     "Check two more things on each query:"),
    (("d45", "sections", 3, "body"),
     "Two related tools:",
     "Mappings and overrides change the display further:"),
    (("d45", "sections", 5, "body"),
     "Now the layout. Picture the engineer",
     "For the layout, picture the engineer"),
    (("d45", "sections", 5, "body"),
     "put it simply: \"A dashboard",
     "say: \"A dashboard"),
    (("d45", "sections", 6, "body"),
     "Two provider settings are worth knowing. With `allowUiUpdates: false`, the Save button refuses,",
     "In the provider file, `allowUiUpdates: false` makes the Save button refuse,"),
    (("d45", "analogy"), None,
     "A Grafana dashboard is like a spreadsheet whose cells hold formulas that pull live numbers from a database. "
     "The file saves the formulas, the chart types and the colors, and the numbers arrive fresh each time you open it. "
     "A dashboard variable is the cell at the top that every formula reads, so changing it changes every chart. "
     "A spreadsheet can also keep its own copy of the data, and a panel can't. "
     "When Prometheus deletes old samples (after 7 days in the lab), that part of every graph goes empty."),
    (("d45", "mistake"), None,
     "You edit a provisioned dashboard in the browser and expect the change to stick. "
     "With `allowUiUpdates: false` Grafana refuses to save it, and if you set it to true, the next change to the file quietly overwrites your edit. "
     "Make the change in the UI, export the JSON, paste it into the file in git, and let provisioning load it."),
    (("d45", "real_world"), None,
     "Dashboard uids end up in runbooks. "
     "In a payments company with many services, each team might own one RED dashboard in its repo, built from a shared template. "
     "CI checks the JSON on every pull request. "
     "The on-call runbook links straight to `/d/<uid>` URLs, which is why nobody changes a uid. "
     "Dashboards made by hand in the UI are fine for exploring, and they get cleaned up after 30 days."),
    (("d45", "deeper", "body"),
     "Next, link each row to the service dashboard.",
     "Each row should then link to the service dashboard."),
    (("d45", "deeper", "body"),
     "Then cover the machines. RED describes",
     "The machines need their own view. RED describes"),
    (("d45", "deeper", "body"),
     "Finally, watch the cost. Every panel is at least one query, every refresh runs them all, and every viewer multiplies that.",
     "Watch the cost too. Each panel is at least one query, and every refresh runs all of them again for every viewer."),

    (("d45", "worked", "steps", 3, "say"),
     "Now the error ratio. Nothing has failed yet,",
     "The error ratio needs one extra step. Nothing has failed yet,"),

    # d46
    (("d46", "sections", 5, "body"),
     "The signals are worth most when you can jump between them. If the app",
     "If the app"),
    (("d46", "sections", 1, "body"),
     "Think of a log count from Loki",
     "A rule can put a log count from Loki"),
    (("d46", "sections", 4, "body"),
     "One more change makes the logs worth having. Gunicorn",
     "There is one more gap: Gunicorn"),
    (("d46", "analogy"), None,
     "Loki works like a library that catalogs books only by shelf: subject, author and year, never the words inside. "
     "To find a quote, you walk to the right shelf and flip through the few books there. "
     "The catalog stays tiny, and flipping is fast when the shelf is small. "
     "That only holds while the shelves stay few. "
     "Make a shelf for every reader's name and the catalog grows larger than the books, which is what a user ID label does to Loki."),
    (("d46", "worked", "steps", 4, "say"),
     "The same thing works for any data source, which is the point of the next sections: the query could just as well count error lines in Loki.",
     "Nothing in this rule is specific to Prometheus: the query could just as well count error lines in Loki, which you do in the task."),
    (("d46", "mistake"), None,
     "A request ID, user ID or full URL in a Loki label looks like an easy way to search. "
     "Each new value makes a new stream, and Loki slows down and fills its index with tiny chunks. "
     "Keep labels to a few values such as service and environment, leave the IDs in the line, and find them with a filter such as `|= \"req-42\"` or `| json | user_id=\"42\"`."),
    (("d46", "real_world"), None,
     "Splitting alerting between two systems works when each alert has exactly one home. "
     "A payments company might let Prometheus and Alertmanager page on-call for the checkout SLO. "
     "Grafana alerting gets the rest, such as a rule that counts `card declined` lines in Loki per merchant. "
     "Every Grafana rule and contact point lives in Terraform next to the dashboards, so a new team gets its alerts by pull request, not by clicking."),
    (("d46", "deeper", "body"),
     "It is worth knowing what belongs there and what doesn't.",
     "Some jobs belong there and some don't."),
    (("d46", "deeper", "body"),
     "Finally, retention. The lab keeps",
     "Retention is the last thing to plan. The lab keeps"),
]


def run(name, edits):
    path = ROOT / "content" / name
    d = json.loads(path.read_text())
    apply(d, edits, name)
    with open(path, "w") as f:
        json.dump(d, f, ensure_ascii=False, indent=1)
    print(f"{name}: {len(edits)} edits applied")


if __name__ == "__main__":
    run("p9.json", P9)
    run("p10.json", P10)
