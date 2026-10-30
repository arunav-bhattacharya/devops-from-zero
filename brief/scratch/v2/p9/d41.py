from common import lab, ref, src

DIAGRAM = (
    '<svg viewBox="0 0 560 340" xmlns="http://www.w3.org/2000/svg" role="img" '
    'aria-label="From requests to an SLI, compared with the SLO target, giving an error budget, a burn rate, '
    'and finally a page or a ticket">'
    '<rect class="bx" x="40" y="12" width="200" height="36" rx="10"/>'
    '<text class="t" x="140" y="35" font-size="13" text-anchor="middle">Requests</text>'
    '<text class="ts" x="260" y="35" font-size="11" text-anchor="start">every response to /</text>'
    '<line class="ln" x1="140" y1="49" x2="140" y2="64" marker-end="url(#ar)"/>'
    '<rect class="bxt" x="40" y="68" width="200" height="36" rx="10"/>'
    '<text class="tk" x="140" y="91" font-size="13" text-anchor="middle">SLI</text>'
    '<text class="ts" x="260" y="91" font-size="11" text-anchor="start">good / valid = 99.95%</text>'
    '<line class="ln" x1="140" y1="105" x2="140" y2="120" marker-end="url(#ar)"/>'
    '<rect class="bxt" x="40" y="124" width="200" height="36" rx="10"/>'
    '<text class="tk" x="140" y="147" font-size="13" text-anchor="middle">SLO target</text>'
    '<text class="ts" x="260" y="147" font-size="11" text-anchor="start">99.9% over 30 days</text>'
    '<line class="ln" x1="140" y1="161" x2="140" y2="176" marker-end="url(#ar)"/>'
    '<rect class="bxo" x="40" y="180" width="200" height="36" rx="10"/>'
    '<text class="tk" x="140" y="203" font-size="13" text-anchor="middle">Error budget</text>'
    '<text class="ts" x="260" y="203" font-size="11" text-anchor="start">100% - 99.9% = 0.1% may fail</text>'
    '<line class="ln" x1="140" y1="217" x2="140" y2="232" marker-end="url(#ar)"/>'
    '<rect class="bxo" x="40" y="236" width="200" height="36" rx="10"/>'
    '<text class="tk" x="140" y="259" font-size="13" text-anchor="middle">Burn rate</text>'
    '<text class="ts" x="260" y="259" font-size="11" text-anchor="start">error ratio / budget</text>'
    '<line class="ln" x1="140" y1="273" x2="140" y2="288" marker-end="url(#ar)"/>'
    '<rect class="bxp" x="40" y="292" width="200" height="36" rx="10"/>'
    '<text class="tk" x="140" y="315" font-size="13" text-anchor="middle">Page or ticket</text>'
    '<text class="ts" x="260" y="315" font-size="11" text-anchor="start">fast burn: page; slow burn: ticket</text>'
    "</svg>"
)

LESSON = {
    "id": "d41",
    "title": "Observability foundations: signals, SLOs and alerts",
    "minutes": 45,
    "goal": "By the end you can explain the four signals, describe a service with RED and a machine with USE, turn an SLO into an error budget and burn rates, and say which alerts deserve a page.",
    "guess": {
        "q": "Which of these should wake an engineer at 3 a.m.?",
        "options": [
            "CPU on the web servers has been above 90% for 10 minutes",
            "The database disk is 70% full and growing slowly",
            "5% of checkout requests have failed for the last 10 minutes",
            "One pod restarted once and is healthy again",
        ],
        "answer": 2,
        "why": "Failed checkouts are a symptom that users feel right now. The others are possible causes that may never hurt anyone, so they belong on a dashboard or in a ticket.",
    },
    "terms": [
        {"term": "Telemetry", "plain": "The data a running system gives off about itself: metrics, logs, traces and profiles."},
        {"term": "Metric", "plain": "A number measured again and again over time, such as requests per second."},
        {"term": "Trace", "plain": "The path of one request through every service it touched, with the time spent in each step."},
        {"term": "SLI", "plain": "Service level indicator: a measure of service quality, usually good events divided by all valid events."},
        {"term": "SLO", "plain": "Service level objective: a target for an SLI over a time window, such as 99.9% over 30 days."},
        {"term": "Error budget", "plain": "The failure an SLO still allows: 100% minus the SLO, such as 0.1% of requests."},
        {"term": "Burn rate", "plain": "How fast you spend the error budget. At burn rate 1 it lasts exactly until the end of the window."},
        {"term": "Symptom alert", "plain": "An alert on something users feel, such as errors or slow pages, not on a possible cause like high CPU."},
    ],
    "sections": [
        {
            "h": "Monitoring and observability",
            "body": (
                "Monitoring means you decide in advance what can go wrong, measure it, and get told when it happens. "
                "Is hello-devops answering? Is the disk filling up? Each of those is a check someone wrote on purpose.\n\n"
                "**Observability** is how well you can answer a question you did not plan for, using the data the system already gives off. "
                "Here is one: why did requests from the mobile app get slow at 14:00, but only for users with items in their basket? "
                "No alert you wrote last month answers that. If your data has enough detail, you can still find the answer without shipping new code.\n\n"
                "You need both. Monitoring catches the problems you know about and wakes someone up. "
                "Observability helps that person find out why. "
                "Google's [SRE book chapter on monitoring](https://sre.google/sre-book/monitoring-distributed-systems/) adds one more split worth knowing:\n"
                "- White-box monitoring looks inside: numbers and logs the app reports about itself.\n"
                "- Black-box monitoring looks from outside, like a user would: does the page load at all?\n\n"
                "White-box data explains a problem. Black-box checks catch the problems your app cannot see, such as a broken DNS record in front of it."
            ),
            "refs": [ref("sre_monitoring"), ref("otel_primer")],
        },
        {
            "h": "Four signals, four questions",
            "body": (
                "The data a system gives off about itself is called telemetry. It comes in four kinds, usually called signals:\n"
                "- Metrics: numbers over time, like requests per second. They tell you that something is wrong.\n"
                "- Logs: one line of text per event, with a timestamp. They tell you what happened to one request.\n"
                "- Traces: one request followed through every service, split into timed steps called spans. They tell you where the time or the error came from.\n"
                "- Profiles: which functions use the CPU and memory. They tell you which code is expensive.\n\n"
                "Metrics are cheap because they are already summed up. A thousand requests a second become one counter that Prometheus reads every 15 seconds. "
                "Logs and traces grow with traffic, so teams keep less of them, or only a sample.\n\n"
                "A real incident often uses them in that order. A metric alert fires: 3% of checkouts fail. "
                "A trace of one failed checkout shows a 5-second wait on the payment service. "
                "That service's logs for the same trace ID say its database connection pool was full.\n\n"
                "The next parts of the course follow the same split:\n"
                "- Part 9 (Days 41 to 44): metrics and alerts with Prometheus.\n"
                "- Part 10 (Days 45 and 46): dashboards with Grafana, and logs with Loki.\n"
                "- Part 11 (Days 47 to 49): logs with the Elastic stack, traces with OpenTelemetry.\n"
                "- Part 12 (Days 50 and 51): Dynatrace, one commercial product that collects every signal."
            ),
            "refs": [ref("otel_signals"), ref("v_how_prom")],
        },
        {
            "h": "Golden signals, RED and USE",
            "body": (
                "Which few numbers should you watch first? Three well-known checklists answer that, and they overlap a lot.\n\n"
                "The four golden signals come from the SRE book: latency, traffic, errors and saturation. "
                "Its advice is blunt: if you can only measure four metrics of a user-facing system, measure these.\n\n"
                "The [RED method](https://grafana.com/blog/the-red-method-how-to-instrument-your-services/), from Tom Wilkie, keeps three of them for anything that serves requests:\n"
                "- Rate: requests per second.\n"
                "- Errors: failed requests per second, or the share that fail.\n"
                "- Duration: how long requests take, usually as percentiles.\n\n"
                "A percentile reads like this: a p95 of 200 ms means 95% of requests took 200 ms or less. "
                "Averages hide the slow ones, so teams watch p95 or p99.\n\n"
                "The [USE method](https://www.brendangregg.com/usemethod.html), from Brendan Gregg, is for resources such as CPU, memory, disks and network cards:\n"
                "- Utilization: how busy the resource was, such as CPU busy 70% of the time.\n"
                "- Saturation: extra work waiting because the resource is full, such as a queue of runnable processes.\n"
                "- Errors: error events, such as failed disk reads.\n\n"
                "Grafana's dashboard guide says it well: USE tells you how happy your machines are, RED tells you how happy your users are. "
                "For hello-devops, RED is requests per second to `/`, the share of 5xx answers, and the p95 response time. "
                "You will write all three in PromQL on Day 43."
            ),
            "refs": [ref("red_blog"), ref("use"), ref("v_red")],
        },
        {
            "h": "SLIs, SLOs and SLAs",
            "body": (
                "An SLI (service level indicator) says how good the service is, seen from the user's side. "
                "The most useful shape is a ratio of good events to valid events:\n"
                "- Availability SLI: responses that are not 5xx, divided by all responses.\n"
                "- Latency SLI: responses faster than 300 ms, divided by all responses.\n\n"
                "An SLO (service level objective) is a target for an SLI over a time window. "
                "For example: 99.9% of requests to `/` succeed, measured over the last 30 days. "
                "An SLA (service level agreement) is a contract with a customer that says what happens when you miss, often money back. "
                "Teams set the SLA looser than the SLO, so they notice trouble before it costs money.\n\n"
                "Do not aim for 100%. The SRE book's chapter on [embracing risk](https://sre.google/sre-book/embracing-risk/) gives the reason: "
                "a user on a phone that works 99% of the time cannot tell 99.99% from 99.999%. "
                "Each extra nine costs far more work, and users never notice it. "
                "So pick a target that keeps users happy and treat it as a floor and a ceiling. "
                "If you are far more reliable than your SLO, you are probably shipping slower than you could."
            ),
            "refs": [ref("sre_slo"), ref("v_slo_ohmy")],
        },
        {
            "h": "Error budgets and burn rate",
            "body": (
                "The error budget is the failure the SLO allows: 100% minus the SLO. For 99.9% that is 0.1%. "
                "With 200,000 requests a day, 30 days hold 6,000,000 requests, and 6,000 of them may fail. "
                "If everything fails at once, 0.1% of 43,200 minutes is 43.2 minutes of full outage.\n\n"
                "The budget turns an argument into arithmetic. Developers want to ship, operators want quiet nights, and both can look at the same number. "
                "While budget is left, you ship at normal speed and take some risks. "
                "When it is spent, the SRE book's answer is to pause risky releases until reliability is back.\n\n"
                "The burn rate says how fast you are spending it: the current error ratio divided by the budget. With a 0.1% budget:\n"
                "- 0.1% of requests failing is burn rate 1. The budget lasts exactly 30 days.\n"
                "- 0.6% failing is burn rate 6. The budget is gone in 5 days.\n"
                "- 1.44% failing is burn rate 14.4. The budget is gone in about 2 days, and one hour of this spends 2% of it.\n\n"
                "Those numbers come from Google's [SRE Workbook](https://sre.google/workbook/alerting-on-slos/): page at 14.4 over one hour or 6 over six hours, and open a ticket at 1 over three days. "
                "Day 44 turns them into Prometheus alerts. "
                "Burn rate works better than a raw error count because it already knows your traffic and your target."
            ),
            "refs": [ref("sre_risk"), ref("sre_wb_alerting"), ref("v_burn")],
        },
        {
            "h": "Alert on symptoms, and keep pages rare",
            "body": (
                "A page is an alert that interrupts a person, maybe at 3 a.m. "
                "Each one costs sleep and focus, so every page must be urgent, real and something a human can act on. "
                "The [Prometheus alerting guide](https://prometheus.io/docs/practices/alerting/) puts it in one line: keep alerting simple, alert on symptoms, and avoid pages where there is nothing to do.\n\n"
                "A symptom is something users feel: errors, slow answers, the site down. "
                "A cause is a reason that might lead to a symptom: high CPU, a busy disk, a pod restart. "
                "Causes are useful on dashboards, where you look during an investigation. "
                "They make poor pages, because many of them never hurt anyone. "
                "A server at 90% CPU that answers every request in 50 ms is simply doing its job.\n\n"
                "Sort every alert into one of three groups:\n"
                "- Page: users hurt now and a human must act now. A fast error budget burn, or the service down.\n"
                "- Ticket: needs a human in working hours. A slow burn, or a certificate that expires in 10 days.\n"
                "- Dashboard only: everything else, such as CPU, memory and single restarts.\n\n"
                "Too many alerts cause alert fatigue: people learn that pages are usually noise and start to ignore them, including the real one. "
                "If an alert fires and nobody needs to do anything, delete it or make it a ticket."
            ),
            "refs": [ref("prom_alerting_practice"), ref("grafana_bp")],
        },
        {
            "h": "On-call and blameless postmortems",
            "body": (
                "On-call means one person carries the pager for a shift, often a week, and answers pages within minutes. "
                "Teams keep it bearable with three habits:\n"
                "- Few pages, each one tied to a symptom.\n"
                "- A runbook for every alert: a short page with what the alert means and the first things to check.\n"
                "- A second person to call when the first one is stuck.\n\n"
                "After an incident, the team writes a postmortem: what happened, the timeline, the impact on users, and what will stop it from happening again. "
                "Blameless means the document looks for gaps in systems and processes, not for a person to punish. "
                "If one command could take production down, the fix is a safer command; blaming the engineer only teaches everyone to hide mistakes. "
                "Google's [postmortem chapter](https://sre.google/sre-book/postmortem-culture/) describes the practice in detail.\n\n"
                "The SLO links all of this. It defines what working means, the burn rate decides when someone gets paged, "
                "and the postmortem decides what to change so next month's budget lasts longer."
            ),
            "refs": [ref("sre_postmortem"), ref("sre_wb_oncall")],
        },
    ],
    "analogy": (
        "Think of a train company that promises 99% of its trains arrive within five minutes of the timetable each month. "
        "That promise is the SLO, and the 1% of trains allowed to be late is the error budget. "
        "If the company has used little of it by mid-month, it can close a track for repairs; if a storm has used it all, repairs wait. "
        "Where it breaks: trains run on a fixed timetable, while software failures come in sudden bursts, which is why you watch the burn rate and not only the monthly total."
    ),
    "diagram": DIAGRAM,
    "diagram_caption": "An SLO turns raw requests into a budget, and the burn rate decides who gets woken up.",
    "worked": {
        "title": "An SLO for hello-devops, from numbers to an alert plan",
        "steps": [
            {
                "say": (
                    "Start with what users do. hello-devops has one real job: the JSON at `/`. "
                    "A good event is a response that is not 5xx. A valid event is any response to `/`. "
                    "A 404 for a mistyped URL is the user's mistake, so it does not count against you."
                ),
            },
            {
                "say": "Pick a target and a window, then let the Day 41 script do the arithmetic. I guessed 200,000 requests a day.",
                "code": "$ python3 observability/error_budget.py 99.9 30 200000\n"
                + "SLO 99.90% over 30 days\nError budget: 0.10% of requests\nFull outage allowed: 43.2 minutes\n"
                + "Failed requests allowed: 6,000 of 6,000,000\n"
                + "Burn rate 14.4: error ratio 1.44%, budget gone in 2.1 days; 1 h of this uses 2% (page)\n"
                + "Burn rate    6: error ratio 0.60%, budget gone in 5.0 days; 6 h of this uses 5% (page)\n"
                + "Burn rate    1: error ratio 0.10%, budget gone in 30.0 days; 72 h of this uses 10% (ticket)",
                "lang": "console",
            },
            {
                "say": (
                    "Read it like a budget. One bad deploy that breaks everything for 20 minutes spends almost half the month. "
                    "That tells you something concrete: a rollback must take minutes, not an hour."
                ),
                "code": "$ python3 -c \"print(20 / 43.2)\"\n0.4629629629629629",
                "lang": "console",
            },
            {
                "say": (
                    "Now a bad hour: 2% of requests fail for 60 minutes. The burn rate is 0.02 / 0.001 = 20, above 14.4, so this should page. "
                    "One hour at burn rate 20 spends 20/720 of the budget, because 30 days have 720 hours."
                ),
                "code": "$ python3 -c \"print(0.02 / 0.001, 20 * 1 / 720)\"\n20.0 0.027777777777777776",
                "lang": "console",
            },
            {
                "say": (
                    "Compare a slow leak: 0.3% of requests fail all week. That is burn rate 3, and the budget lasts 10 days. "
                    "Nobody needs to wake up, but someone must fix it this week, so it is a ticket."
                ),
                "code": "$ python3 -c \"print(round(0.003 / 0.001, 2), 30 / 3)\"\n3.0 10.0",
                "lang": "console",
            },
            {
                "say": (
                    "Write the plan down in plain words before any PromQL. Day 44 turns exactly these lines into `alerts.yml`. "
                    "Each long window has a short partner, so the alert stops soon after the errors stop."
                ),
                "code": "SLI:    responses to / that are not 5xx, divided by all responses to /\n"
                "SLO:    99.9% over 30 days  (error budget 0.1%)\n"
                "Page:   error ratio > 1.44% over 1 h AND over 5 m\n"
                "        or > 0.6% over 6 h AND over 30 m\n"
                "Ticket: error ratio > 0.1% over 3 days AND over 6 h\n"
                "Never page on: CPU, memory, single pod restarts (dashboard only)",
                "lang": "text",
            },
        ],
    },
    "code": [
        {
            "lang": "python",
            "title": "observability/error_budget.py",
            "src": lab("observability/error_budget.py"),
            "run": "python3 observability/error_budget.py 99.9 30 200000",
        }
    ],
    "commands": [
        {"cmd": "python3 observability/error_budget.py 99.9 30 200000", "what": "Print the error budget and burn-rate thresholds for a 99.9% SLO, 30 days, 200,000 requests a day."},
        {"cmd": "python3 observability/error_budget.py 99.99", "what": "See how small the budget gets with one more nine: 4.3 minutes a month."},
        {"cmd": "python3 -c \"print(0.02 / 0.001)\"", "what": "Burn rate = error ratio divided by budget. Here 2% errors against a 0.1% budget gives 20."},
        {"cmd": "docker compose up -d", "what": "In the repo root: start hello-devops and Redis from the Day 15 Compose file."},
        {"cmd": "curl -s -o /dev/null -w '%{http_code} %{time_total}\\n' localhost:8000/", "what": "Measure one request by hand: its status code and how many seconds it took."},
        {"cmd": "for i in $(seq 1 200); do curl -s -o /dev/null -w '%{http_code} %{time_total}\\n' localhost:8000/; done > sli.txt", "what": "Measure 200 requests and save one line per request."},
        {"cmd": "awk '$1 < 500' sli.txt | wc -l", "what": "Count the good responses: every status below 500."},
        {"cmd": "awk '$1 < 500 {good++} END {printf \"%.2f%%\\n\", 100 * good / NR}' sli.txt", "what": "Print the availability SLI as a percentage."},
        {"cmd": "awk '$2 <= 0.1' sli.txt | wc -l", "what": "Count responses that took 0.1 seconds or less, for a latency SLI."},
        {"cmd": "docker compose stop redis", "what": "Break the app's dependency on purpose so the SLI drops."},
        {"cmd": "docker compose start redis", "what": "Bring Redis back."},
    ],
    "mistake": (
        "Paging on causes such as CPU above 80%, memory above 90% or any pod restart. These fire all the time without users noticing, "
        "so people stop trusting the pager. Page on symptoms (error budget burn, the service not answering) and put causes on a dashboard you open once a page fires."
    ),
    "real_world": (
        "At a payments company with a product called PayFlow, the card team might set an SLO of 99.95% of authorisations answered without error within 2 seconds, over 28 days. "
        "The on-call engineer is paged only on a fast burn of that budget. "
        "When the budget runs out, the team's written policy freezes feature releases until two weeks of clean numbers come back."
    ),
    "task": {
        "title": "Measure an SLI by hand, then sort the alerts",
        "steps": [
            "In your repo root, start the Day 15 stack with `docker compose up -d` and check that `curl localhost:8000/` answers.",
            "Send 200 requests to `/` and save the status code and time of each one to `sli.txt`, using curl's `-w` option from Day 9.",
            "Stop Redis with `docker compose stop redis`, then append 20 more requests to the same file. Each one takes a few seconds, because the app retries Redis before it gives up.",
            "With awk (Day 5), count the good responses (status below 500) and print the availability SLI as a percentage. Then compute a latency SLI: the share that took 0.1 seconds or less.",
            "Start Redis again. Run `error_budget.py` for a 99.5% SLO over 30 days with your own guess of daily traffic.",
            "Work out the burn rate your measured error ratio means against that 99.5% SLO, and how many days the budget would last at that rate.",
            "Sort these eight alerts into page, ticket or dashboard, with one line of why for each: CPU above 80% for 10 minutes; 5% of requests to `/` fail for 10 minutes; p95 latency above 2 seconds for 15 minutes; disk 70% full; a pod restarted once; a TLS certificate expires in 10 days; burn rate 1.5 over 3 days; no successful request at all for 2 minutes.",
        ],
        "hints": [
            "`awk '$1 < 500' sli.txt | wc -l` counts the good lines, and `wc -l < sli.txt` counts all of them.",
            "Burn rate is the error ratio divided by the budget. For 99.5% the budget is 0.5%, so 5% errors is burn rate 10.",
            "For each alert, ask two questions: do users feel it now, and can a person fix it now?",
        ],
        "done_when": "You have an availability SLI from your own requests (mine was 200 good of 220, 90.91%), its burn rate against a 99.5% SLO, and all eight alerts sorted with a reason.",
    },
    "explain_back": {
        "prompt": "Explain to a product manager, in 3 to 4 sentences, what an error budget is and why it can let the team ship more, not less. Mention the SLO, the burn rate and what happens when the budget runs out.",
        "answer": (
            "Our SLO says 99.9% of requests must succeed over 30 days, so 0.1% may fail, and that 0.1% is our error budget. "
            "While budget is left we can ship features and take some risk, because a few failures are already priced in. "
            "The burn rate tells us how fast we are spending it: a fast burn pages someone, a slow burn becomes a ticket. "
            "If the budget runs out, we pause risky releases and fix reliability first, so we argue about a number instead of about feelings."
        ),
    },
    "recap": [
        "Monitoring checks for known problems; observability lets you ask new questions of your telemetry.",
        "Metrics say that something is wrong, traces say where, logs say what happened, profiles say which code is expensive.",
        "RED (rate, errors, duration) describes a service from the user's side; USE (utilization, saturation, errors) describes a machine.",
        "An SLI is good events over valid events, an SLO is its target over a window, and the error budget is 100% minus the SLO.",
        "Burn rate is the error ratio divided by the budget: page on fast burns (14.4 over 1 hour, 6 over 6 hours), open a ticket on slow ones.",
        "Page only on symptoms with a clear action, and learn from incidents with blameless postmortems.",
    ],
    "check": [
        {
            "q": "An image-resize service gets 1,000,000 requests a month and has an SLO of 99.95%. How many failed requests does its monthly error budget allow?",
            "options": ["50", "500", "5,000", "9,995"],
            "answer": 1,
            "why": "The budget is 100% minus 99.95%, which is 0.05%, and 0.05% of 1,000,000 is 500.",
        },
        {
            "q": "Which of these is a saturation signal for a Postgres database server?",
            "options": [
                "Queries per second",
                "The share of queries that return an error",
                "Queries waiting for a free connection",
                "The median query time",
            ],
            "answer": 2,
            "why": "Saturation is work that waits because a resource is full, and a queue of waiting queries is exactly that.",
        },
        {
            "q": "Your SLO is 99.9%. For the last 6 hours 0.7% of requests failed, and the last 30 minutes look the same. What should happen?",
            "options": [
                "Page someone: burn rate 7 over 6 hours passes the 6x line",
                "Nothing: 99.3% success still sounds high",
                "Add it to next quarter's planning notes",
                "Restart every pod to clear the errors",
            ],
            "answer": 0,
            "why": "0.7% divided by the 0.1% budget is burn rate 7, above the 6x paging line, and the short window shows it is still happening.",
        },
    ],
    "interview": [
        {
            "q": "What is the difference between an SLI, an SLO and an SLA?",
            "a": (
                "An SLI measures service quality from the user's point of view, usually good events divided by valid events, such as the share of requests that succeed. "
                "An SLO is the target for that SLI over a window, such as 99.9% over 30 days. "
                "An SLA is a contract with customers that says what happens, often credits, if a promised level is missed. "
                "Teams set the SLO tighter than the SLA so they react before they owe anyone money."
            ),
        },
        {
            "q": "Why should alerts fire on symptoms rather than causes?",
            "a": (
                "Users feel symptoms such as errors and slow responses, so a symptom alert always means real pain. "
                "A cause such as high CPU may or may not hurt anyone, and there are far too many possible causes to alert on each one. "
                "Paging on causes produces false alarms, which trains people to ignore the pager. "
                "Causes still matter: they belong on dashboards, where the on-call engineer looks once a symptom alert fires."
            ),
        },
        {
            "q": "How would you choose an SLO for a new service?",
            "a": (
                "I would start with a simple SLI, such as successful requests over all requests, and measure what the service achieves today. "
                "Then I would pick a target a little below that, so the team is not paged from day one, and agree with the product owner what happens when the budget runs out. "
                "I would review it every quarter: if users complain while the SLO is met, the SLI or the target is wrong. "
                "I would never pick 100%, because it leaves no room for deploys and costs far more than users can notice."
            ),
        },
    ],
    "deeper": {
        "minutes": 12,
        "body": (
            "Why do the SLO alerts in this course compare two windows? Try the simple version first and see where it fails.\n\n"
            "Alert 1 is a plain threshold: page when the error ratio over the last 5 minutes is above 0.1%. "
            "It fires on every small blip, such as ten bad requests during a deploy, and spends your nights on errors that barely touch the budget. "
            "Alert 2 uses a long window instead: page when the ratio over 30 days is above 0.1%. "
            "Now it fires far too late, and once it fires it stays on for days after the problem is fixed.\n\n"
            "Burn rate fixes the size question. Paging at burn rate 14.4 over one hour means you only page when one hour has already spent 2% of the month's budget. "
            "A ten-request blip never gets there. A real outage gets there within minutes, because a total outage is a burn rate of 1,000 for a 99.9% SLO.\n\n"
            "The short window fixes the reset question. A one-hour window remembers a bad spike for an hour, so the alert would keep firing long after you fixed it. "
            "The [SRE Workbook](https://sre.google/workbook/alerting-on-slos/) adds a second condition with a window one twelfth as long, 5 minutes for the 1-hour alert. "
            "Both windows must be over the line. The 5-minute window drops back within minutes of the fix, so the page clears quickly too.\n\n"
            "The Workbook then layers three pairs:\n"
            "- Page: burn rate 14.4 over 1 hour and 5 minutes (2% of the budget).\n"
            "- Page: burn rate 6 over 6 hours and 30 minutes (5% of the budget).\n"
            "- Ticket: burn rate 1 over 3 days and 6 hours (10% of the budget).\n\n"
            "These are starting numbers, and the Workbook says to tune them for your service. "
            "Day 44 turns them into Prometheus rules for hello-devops, with a `promtool` test that proves a slow leak opens a ticket but does not page.\n\n"
            "One more thing to try on paper: a latency SLO. Write it as a ratio too, for example requests answered within 300 ms divided by all requests. "
            "Then the same budget and burn-rate maths works unchanged. "
            "This is why many teams prefer ratio SLIs over a rule like p99 below 300 ms: ratios add up across time and across servers, and percentiles do not."
        ),
    },
    "sources": [src("sre_slo"), src("sre_wb_alerting"), src("red_blog"), src("prom_alerting_practice")],
}
