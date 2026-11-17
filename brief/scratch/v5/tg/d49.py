"""Book-voice rewrite of d49 (Observability foundations). Writer: tg."""
import json, pathlib

P = pathlib.Path("/home/user/devops-from-zero/content/p12.json")
d = json.loads(P.read_text())
L = next(x for x in d["lessons"] if x["id"] == "d49")

L["opening"] = (
    "Picture driving home late on a quiet highway. Three lights come on at once on the dashboard. One says the "
    "oil pressure is low. One says the washer fluid is low. One says a service is due in 500 km. Only one of them "
    "means \"pull over now\", and you have about two seconds to know which.\n\n"
    "Software teams face the same moment every night, with far more lights. It is easy to treat every light as "
    "urgent, and just as easy, after the tenth false alarm, to ignore them all. Both habits feel reasonable at "
    "the time.\n\n"
    "Last time, Argo CD made sure the cluster runs exactly what git says. It could not tell us whether the app "
    "works well for the people using it. In this lesson, we'll decide what \"working\" means for hello-devops, "
    "write it down as a number, and use that number to decide which problems wake someone up.\n\n"
    "Before we start, make a guess, and keep it in mind."
)

L["guess"]["q"] = "Which of these should wake an engineer at 3 a.m.?"
L["guess"]["why"] = (
    "Failed checkouts are something users feel right now. The others are possible causes that may never hurt "
    "anyone, so they belong on a screen you look at, or on a to-do list."
)

plains = {
    "Telemetry": "The data a running system gives off about itself: metrics, logs, traces and profiles.",
    "Metric": "A number measured again and again over time, such as requests per second.",
    "Trace": "The path of one request through every service it touched, with the time spent in each step.",
    "SLI": "A measure of how good the service is for users, usually good events divided by all valid events.",
    "SLO": "A target for an SLI over a stretch of time, such as 99.9% over 30 days.",
    "Error budget": "The failure an SLO still allows: 100% minus the SLO, such as 0.1% of requests.",
    "Burn rate": "How fast you spend the error budget. At burn rate 1 it lasts exactly until the end of the window.",
    "Symptom alert": "An alert on something users feel, such as errors or slow pages, rather than a possible cause like a busy chip.",
}
for t in L["terms"]:
    t["plain"] = plains[t["term"]]

S = L["sections"]

S[0]["h"] = "Warning lights and open questions: monitoring and observability"
S[0]["body"] = (
    "Your car's dashboard is monitoring. Years before you bought the car, an engineer decided that low fuel and "
    "low oil matter. They put a sensor on each, picked a line, and wired a light to it. Software monitoring "
    "works the same way. You decide in advance what can go wrong, measure it, and get told when it happens.\n\n"
    "Is hello-devops answering? Is the disk filling up? Each of those is a check someone wrote on purpose. "
    "Our lab app, hello-devops, is a tiny web app that answers every visit with a greeting and a count of visits "
    "so far.\n\n"
    "Now picture a stranger question. Why does the car shake, but only on cold mornings, and only above 80 km/h? "
    "Nobody built a light for that. A mechanic can still answer it, if the car recorded enough detail about each "
    "trip. That is observability: how well you can answer a question you did not plan for, using the data the "
    "system already gives off.\n\n"
    "The software version of the shaking car sounds like this. Why did requests from the mobile app get slow at "
    "14:00, but only for users with items in their basket? A request is one message that asks the app for "
    "something, such as a page. No alert you wrote last month answers that question. If your data has enough "
    "detail, you can still find the answer without shipping new code.\n\n"
    "You need both. Monitoring catches the problems you know about and wakes someone up. Observability helps "
    "that person find out why. Google's [SRE book chapter on monitoring]"
    "(https://sre.google/sre-book/monitoring-distributed-systems/) also splits monitoring by where you look from:\n"
    "- White-box monitoring looks inside: numbers and logs the app reports about itself.\n"
    "- Black-box monitoring looks from outside, like a user would: does the page load at all?\n\n"
    "White-box data explains a problem. Black-box checks catch the problems your app cannot see from inside. One "
    "example is a broken DNS record in front of it. DNS is the internet's address book, so a wrong entry sends "
    "users somewhere else before they ever reach your app.\n\n"
    "Both kinds of looking need data. Next, we'll sort that data into four kinds."
)

S[1]["h"] = "Four signals, four questions"
S[1]["body"] = (
    "A car records more than its lights show. There are gauges for speed and fuel, a trip log, and, for anything "
    "you ship, a tracking number that follows a parcel through every depot. Software gives off a similar mix of "
    "data about itself, called telemetry.\n\n"
    "Two words help before the list. A service is one program that answers requests; a big app is made of many "
    "of them. The CPU is the chip that does the computing, and memory is its fast working space.\n\n"
    "Telemetry comes in four kinds, usually called signals:\n"
    "- Metrics: numbers over time, like requests per second. They tell you that something is wrong.\n"
    "- Logs: one line of text per event, with a timestamp. They tell you what happened to one request.\n"
    "- Traces: one request followed through every service, split into timed steps called spans. They tell you where the time or the error came from.\n"
    "- Profiles: which functions use the CPU and memory. They tell you which code is expensive.\n\n"
    "A trace works like the parcel's tracking number: every service it passes through stamps it with a time. A "
    "function, in the last line, is a named piece of code.\n\n"
    "Metrics are cheap because they are already summed up. The app keeps a counter, one number in memory, and "
    "adds 1 to it for every request. A thousand requests a second still make one number. Prometheus, the tool we "
    "meet next time, reads it every 15 seconds. Logs and traces grow with traffic, so teams keep less of them, or "
    "only a sample.\n\n"
    "A real incident, a time when the service is broken for users, often uses them in that order. A metric alert "
    "fires: 3% of checkouts fail. A trace of one failed checkout shows a 5-second wait on the payment service. "
    "That service's logs for the same trace ID say its database connection pool was full. In plain words, the "
    "service had used up all its open lines to the database.\n\n"
    "The next parts of the course follow the same split:\n"
    "- Part 12 (Days 49 to 52): metrics and alerts with Prometheus.\n"
    "- Part 13 (Days 53 and 54): dashboards with Grafana, and logs with Loki.\n"
    "- Part 14 (Days 55 to 57): logs with the Elastic stack, traces with OpenTelemetry.\n"
    "- Part 16 (Days 61 and 62): Dynatrace, one commercial product that collects every signal.\n\n"
    "Metrics come first in that story. But one machine can report hundreds of them. Next, we'll pick the few "
    "worth watching."
)

S[2]["h"] = "Which numbers to watch first: golden signals, RED and USE"
S[2]["body"] = (
    "A car could show you hundreds of numbers, but the dashboard shows four or five. One Linux server can also "
    "report hundreds of numbers, and nobody can watch them all. A server is a computer that runs programs for "
    "others, and Linux is the system most servers run. Three well-known checklists tell you which few to watch "
    "first, and they overlap a lot.\n\n"
    "The four golden signals come from the SRE book:\n"
    "- Latency: how long requests take.\n"
    "- Traffic: how many requests arrive.\n"
    "- Errors: how many of them fail.\n"
    "- Saturation: how full the service is, such as a queue of waiting work that keeps growing.\n\n"
    "Its advice is blunt: if you can only measure four metrics of a user-facing system, measure these.\n\n"
    "The [RED method](https://grafana.com/blog/the-red-method-how-to-instrument-your-services/), from Tom Wilkie, "
    "keeps three of them for anything that serves requests:\n"
    "- Rate: requests per second.\n"
    "- Errors: failed requests per second, or the share that fail.\n"
    "- Duration: how long requests take, usually as percentiles.\n\n"
    "A percentile reads like this: a p95 of 200 ms means 95% of requests took 200 milliseconds or less. Averages "
    "hide the slow ones, so teams watch p95 or p99.\n\n"
    "The [USE method](https://www.brendangregg.com/usemethod.html), from Brendan Gregg, is for resources such as "
    "CPU, memory, disks and network cards:\n"
    "- Utilization: how busy the resource was, such as CPU busy 70% of the time.\n"
    "- Saturation: extra work waiting because the resource is full, such as a queue of runnable processes.\n"
    "- Errors: error events, such as failed disk reads.\n\n"
    "A process is a running program, and a runnable one is ready to work but waiting for the CPU. Grafana, the "
    "dashboard tool of Part 13, sums up the split in its guide. USE tells you how happy your machines are, and "
    "RED tells you how happy your users are.\n\n"
    "For hello-devops, RED is requests per second to `/`, the share of 5xx answers, and the p95 response time. "
    "Every answer carries a three-digit status code, and codes from 500 to 599 (5xx) mean the server failed. You "
    "will write all three in PromQL, Prometheus's query language, on Day 51.\n\n"
    "Gauges tell us how things are. They do not say how good is good enough. Next, we'll write that down as a "
    "promise."
)

S[3]["h"] = "Writing down \"good enough\": SLIs, SLOs and SLAs"
S[3]["body"] = (
    "A parcel company says your parcel will arrive within two days, 99 times in 100. Three different things hide "
    "in that sentence. There is what they measure, there is the target, and there may be a contract that pays "
    "you back when they miss. Software teams use the same three, with short names.\n\n"
    "An SLI (service level indicator) says how good the service is, seen from the user's side. The most useful "
    "shape is a ratio of good events to valid events:\n"
    "- Availability SLI: responses that are not 5xx, divided by all responses.\n"
    "- Latency SLI: responses faster than 300 ms, divided by all responses.\n\n"
    "An SLO (service level objective) is a target for an SLI over a time window. For example: 99.9% of requests to "
    "`/` succeed, measured over the last 30 days.\n\n"
    "An SLA (service level agreement) is a contract with a customer that says what happens when you miss, often "
    "money back. Teams set the SLA looser than the SLO, so they notice trouble before it costs money.\n\n"
    "Do not aim for 100%. The SRE book's chapter on [embracing risk](https://sre.google/sre-book/embracing-risk/) "
    "explains why. Users rarely notice the difference between high and extreme reliability, because their own "
    "phone and mobile network fail far more often. Each extra nine, such as going from 99.9% to 99.99%, still "
    "costs far more work.\n\n"
    "**Perfect is a target nobody can afford. Pick the level users would actually miss.**\n\n"
    "So pick a target that keeps users happy and treat it as a floor and a ceiling. If you are far more reliable "
    "than your SLO, you are probably shipping slower than you could.\n\n"
    "That last sentence sounds odd: why would being too reliable be a problem? Next, the error budget answers it."
)

S[4]["h"] = "Spending failure on purpose: error budgets and burn rate"
S[4]["body"] = (
    "Think of a phone plan with 10 GB of data a month. You do not panic about every video. You panic when half "
    "the data is gone on day three. An SLO works the same way, and the data is your allowed failure.\n\n"
    "The error budget is the failure the SLO allows: 100% minus the SLO. For 99.9% that is 0.1%. With 200,000 "
    "requests a day, 30 days hold 6,000,000 requests, and 6,000 of them may fail. If everything fails at once, "
    "0.1% of 43,200 minutes is 43.2 minutes of full outage.\n\n"
    "Developers want to ship and operators want quiet nights. The budget gives both sides the same number to "
    "argue over. While budget is left, you ship at normal speed and take some risks. When it is spent, the SRE "
    "book's answer is to pause risky releases until reliability is back. That answers the odd sentence from "
    "before: a budget you never touch is speed you never used.\n\n"
    "The burn rate says how fast you are spending it: the current error ratio divided by the budget. With a 0.1% "
    "budget:\n"
    "- 0.1% of requests failing is burn rate 1. The budget lasts exactly 30 days.\n"
    "- 0.6% failing is burn rate 6. The budget is gone in 5 days.\n"
    "- 1.44% failing is burn rate 14.4. The budget is gone in about 2 days, and one hour of this spends 2% of it.\n\n"
    "Those numbers come from Google's [SRE Workbook](https://sre.google/workbook/alerting-on-slos/). It says to "
    "page someone at 14.4 over one hour or 6 over six hours, and to open a ticket at 1 over three days.\n\n"
    "The odd 14.4 comes from working backwards. You want a page once a single hour has spent 2% of the budget. "
    "2% of the 720 hours in 30 days is 14.4 hours of budget, and burning that in one hour is burn rate 14.4. Day "
    "52 turns these numbers into Prometheus alerts.\n\n"
    "Burn rate beats a raw error count because it is already scaled to your traffic and your target. Ten "
    "failures mean nothing on a busy shop and a lot on a quiet one.\n\n"
    "Now we know when the budget is in danger. Next, we'll decide who gets told, and how loudly."
)

S[5]["h"] = "Alert on what users feel, and keep pages rare"
S[5]["body"] = (
    "Back on the highway, the oil light means stop now, the washer light means fill up this week, and the "
    "service reminder means book a garage. Alerts need the same sorting.\n\n"
    "A page is an alert that interrupts a person, maybe at 3 a.m. Each one costs sleep and focus. So a page has "
    "to be urgent and real, and a human must be able to do something about it. The [Prometheus alerting "
    "guide](https://prometheus.io/docs/practices/alerting/) gives the same advice: keep alerting simple, alert on "
    "symptoms, and avoid pages where there is nothing to do.\n\n"
    "A symptom is something users feel: errors, slow answers, the site down. A cause is a reason that might lead "
    "to a symptom: high CPU, a busy disk, a restart of a pod (one running copy of the app in Kubernetes). Causes "
    "are useful on dashboards, where you look during an investigation. They make poor pages, because many of "
    "them never hurt anyone. A server at 90% CPU that answers every request in 50 ms is simply doing its job.\n\n"
    "**Wake people for what users feel. Put the causes on a dashboard.**\n\n"
    "Sort every alert into one of three groups:\n"
    "- Page: users hurt now and a human must act now. A fast error budget burn, or the service down.\n"
    "- Ticket: needs a human in working hours. A slow burn, or a certificate that expires in 10 days.\n"
    "- Dashboard only: everything else, such as CPU, memory and single restarts.\n\n"
    "A ticket is a task in the team's to-do list. A certificate is the proof a website shows that it is who it "
    "says it is, and it stops working on a fixed date.\n\n"
    "Too many alerts cause alert fatigue. People learn that pages are usually noise and start to ignore them, "
    "including the real one. Picture a car whose warning lights flash so often that the driver "
    "puts tape over them. If an alert fires and nobody needs to do anything, delete it or make it a ticket.\n\n"
    "A page still lands on a real person. Next, we'll look at how teams make that bearable, and what they do "
    "after things break."
)

S[6]["h"] = "On-call, and learning from incidents without blame"
S[6]["body"] = (
    "On-call means one person carries the pager for a shift, often a week, and answers pages within minutes. "
    "Teams keep it bearable with three habits:\n"
    "- Few pages, each one tied to a symptom.\n"
    "- A runbook for every alert: a short page with what the alert means and the first things to check.\n"
    "- A second person to call when the first one is stuck.\n\n"
    "After an incident, the team writes a postmortem: what happened, the timeline, the impact on users, and what "
    "will stop it from happening again. Blameless means the document looks for gaps in systems and processes, "
    "and never for a person to punish. If one command could take production down, the fix is a safer command. "
    "Blaming the engineer only teaches everyone to hide mistakes. Google's [postmortem "
    "chapter](https://sre.google/sre-book/postmortem-culture/) describes the practice in detail.\n\n"
    "The SLO ties these habits together. It says what working means, and the burn rate against it decides when "
    "someone gets paged. The postmortem then decides what to change so next month's budget lasts longer.\n\n"
    "All of this is still on paper. An SLO is only as good as the numbers behind it, and so far we have none "
    "from hello-devops. Something has to collect a count of requests and errors from the running app, every few "
    "seconds, and keep it. That is the job of Prometheus, and it is where the next lesson starts."
)

# The highway scene and the parcel promise carry the analogy; section 6 carries the CPU-page mistake.
L.pop("analogy", None)
L.pop("mistake", None)
L["real_world"] = (
    "Picture a team that runs card payments for online shops. Their SLO might read: 99.95% of payment approvals "
    "answered without error within 2 seconds, over 28 days. The engineer on call is paged only on a fast burn of "
    "that budget. When the budget runs out, the team's written policy freezes new features until two weeks of "
    "clean numbers come back."
)

W = L["worked"]["steps"]
W[0]["say"] = (
    "Start with what users do. hello-devops has one real job: the JSON (structured text) it returns at `/`. A good "
    "event is a response that is not 5xx. A valid event is any response to `/`. A 404 for a mistyped address is "
    "the user's mistake, so it does not count against you."
)
W[1]["say"] = (
    "Pick a target and a window, then let this lesson's `error_budget.py` do the arithmetic. I guessed 200,000 "
    "requests a day."
)
W[2]["say"] = (
    "Read it like a budget. One bad deploy that breaks everything for 20 minutes spends almost half the month. So "
    "a rollback has to take minutes, not an hour."
)
W[3]["say"] = (
    "Now a bad hour: 2% of requests fail for 60 minutes. The burn rate is 0.02 / 0.001 = 20, above 14.4, so this "
    "should page. One hour at burn rate 20 spends 20/720 of the budget, because 30 days have 720 hours."
)
W[4]["say"] = (
    "Compare a slow leak: 0.3% of requests fail all week. That is burn rate 3, and the budget lasts 10 days. "
    "Nobody needs to wake up, but someone must fix it this week, so it is a ticket."
)
W[5]["say"] = (
    "Write the plan down in plain words before any PromQL. Day 52 turns exactly these lines into `alerts.yml`. "
    "Each long window has a short partner, so the alert stops soon after the errors stop."
)

T = L["task"]
T["steps"] = [
    "In your repo root, start the Day 21 stack with `docker compose up -d` and check that `curl localhost:8000/` answers.",
    "Send 200 requests to `/` and save the status code and time of each one to `sli.txt`, using curl's `-w` option from Day 11.",
    "Stop Redis with `docker compose stop redis`, then append 20 more requests to the same file. Each one takes a few seconds, because the app retries Redis before it gives up.",
    "With awk (Day 5), count the good responses (status below 500) and print the availability SLI as a percentage. Then compute a latency SLI: the share that took 0.1 seconds or less.",
    "Start Redis again. Run `error_budget.py` for a 99.5% SLO over 30 days with your own guess of daily traffic.",
    "Work out the burn rate your measured error ratio means against that 99.5% SLO, and how many days the budget would last at that rate.",
    "Sort these eight alerts into page, ticket or dashboard, with one line of why for each. CPU above 80% for 10 minutes. 5% of requests to `/` fail for 10 minutes. P95 latency above 2 seconds for 15 minutes. Disk 70% full. A pod restarted once. A TLS certificate expires in 10 days. Burn rate 1.5 over 3 days. No successful request at all for 2 minutes.",
]
T["hints"] = [
    "`awk '$1 < 500' sli.txt | wc -l` counts the good lines, and `wc -l < sli.txt` counts all of them.",
    "Burn rate is the error ratio divided by the budget. For 99.5% the budget is 0.5%, so 5% errors is burn rate 10.",
    "For each alert, ask two questions: do users feel it now, and can a person fix it now?",
]
T["done_when"] = (
    "You have an availability SLI from your own requests (mine was 200 good of 220, 90.91%), its burn rate "
    "against a 99.5% SLO, and all eight alerts sorted with a reason."
)

L["explain_back"]["prompt"] = (
    "Explain to a product manager, in 3 to 4 sentences, what an error budget is and why it can let the team ship "
    "more, not less. Mention the SLO, the burn rate and what happens when the budget runs out."
)
L["explain_back"]["answer"] = (
    "Our SLO says 99.9% of requests must succeed over 30 days, so 0.1% may fail, and that 0.1% is our error "
    "budget. While budget is left, we can ship features and take some risk, because a few failures are already "
    "planned for. The burn rate tells us how fast we are spending it: a fast burn pages someone, a slow burn "
    "becomes a ticket. If the budget runs out, we pause risky releases and fix reliability first, so we argue "
    "about a number instead of about feelings."
)

L["recap"] = [
    "Monitoring checks for known problems; observability lets you ask new questions of the data a system gives off.",
    "Metrics say that something is wrong, traces say where, logs say what happened, profiles say which code is expensive.",
    "RED (rate, errors, duration) describes a service from the user's side; USE (utilization, saturation, errors) describes a machine.",
    "An SLI is good events over valid events, an SLO is its target over a window, and the error budget is 100% minus the SLO.",
    "Burn rate is the error ratio divided by the budget: page on fast burns (14.4 over 1 hour, 6 over 6 hours), open a ticket on slow ones.",
    "Page only on symptoms with a clear action. All of this stays on paper until a tool collects real numbers from the app.",
]

C = L["check"]
C[0]["q"] = (
    "An image-resize service gets 1,000,000 requests a month and has an SLO of 99.95%. How many failed requests "
    "does its monthly error budget allow?"
)
C[0]["why"] = "The budget is 100% minus 99.95%, which is 0.05%, and 0.05% of 1,000,000 is 500."
C[1]["q"] = "Which of these is a saturation signal for a Postgres database server?"
C[1]["why"] = "Saturation is work that waits because a resource is full, and a queue of waiting queries is exactly that."
C[2]["q"] = (
    "Your SLO is 99.9%. For the last 6 hours 0.7% of requests failed, and the last 30 minutes look the same. What "
    "should happen?"
)
C[2]["why"] = (
    "0.7% divided by the 0.1% budget is burn rate 7, above the 6x paging line, and the short window shows it is "
    "still happening."
)

I = L["interview"]
I[0]["a"] = (
    "An SLI measures service quality from the user's point of view, usually good events divided by valid events, "
    "such as the share of requests that succeed. An SLO is the target for that SLI over a window, such as 99.9% "
    "over 30 days. An SLA is a contract with customers that says what happens, often credits, if a promised level "
    "is missed. Teams set the SLO tighter than the SLA so they react before they owe anyone money."
)
I[1]["a"] = (
    "Users feel symptoms such as errors and slow responses, so a symptom alert always means real pain. A cause such "
    "as high CPU may or may not hurt anyone, and there are far too many possible causes to alert on each one. "
    "Paging on causes produces false alarms, which trains people to ignore the pager. Causes still matter: they "
    "belong on dashboards, where the on-call engineer looks once a symptom alert fires."
)
I[2]["a"] = (
    "Start with a simple SLI, such as successful requests over all requests, and measure what the service achieves "
    "today. Then pick a target a little below that, so the team is not paged from day one. Agree with the product "
    "owner on what happens when the budget runs out. Review the SLO every quarter: if users complain while it is "
    "met, the SLI or the target is wrong. I would never pick 100%, because it leaves no room for deploys and costs "
    "far more than users can notice."
)

L["deeper"]["body"] = (
    "Why do the SLO alerts in this course compare two windows? Try the simple version first and see where it "
    "fails.\n\n"
    "Alert 1 is a plain threshold: page when the error ratio over the last 5 minutes is above 0.1%. It fires on "
    "every small blip, such as ten bad requests during a deploy. It spends your nights on errors that barely touch "
    "the budget. Alert 2 uses a long window instead: page when the ratio over 30 days is above 0.1%. Now it fires "
    "far too late, and once it fires it stays on for days after the problem is fixed.\n\n"
    "Burn rate fixes the size question. Paging at burn rate 14.4 over one hour means you only page when one hour "
    "has already spent 2% of the month's budget. A ten-request blip never gets there. A real outage gets there "
    "within minutes, because a total outage is a burn rate of 1,000 for a 99.9% SLO.\n\n"
    "The short window fixes the reset question. A one-hour window remembers a bad spike for an hour, so the alert "
    "would keep firing long after you fixed it. The [SRE Workbook](https://sre.google/workbook/alerting-on-slos/) "
    "adds a second condition with a window one twelfth as long, 5 minutes for the 1-hour alert. Both windows must "
    "be over the line. The 5-minute window drops back within minutes of the fix, so the page clears quickly too.\n\n"
    "The Workbook then layers three pairs:\n"
    "- Page: burn rate 14.4 over 1 hour and 5 minutes (2% of the budget).\n"
    "- Page: burn rate 6 over 6 hours and 30 minutes (5% of the budget).\n"
    "- Ticket: burn rate 1 over 3 days and 6 hours (10% of the budget).\n\n"
    "These are starting numbers, and the Workbook says to tune them for your service. Day 52 turns them into "
    "Prometheus rules for hello-devops, with a `promtool` test that proves a slow leak opens a ticket but does not "
    "page.\n\n"
    "One more thing to try on paper: a latency SLO. Write it as a ratio too, for example requests answered within "
    "300 ms divided by all requests. Then the same budget and burn-rate maths works unchanged. This is why many "
    "teams prefer ratio SLIs over a rule like p99 below 300 ms. Ratios add up across time and across servers, and "
    "percentiles do not."
)

L["closing"] = (
    "We started on a dark highway with three lights, and only one that mattered. Now our lab app has the same "
    "sorting on paper. An SLI counts good answers, and the SLO asks for 99.9%. That leaves a budget of 43 minutes "
    "a month, and burn rates say when to page and when to open a ticket. Look at one alert you receive today, from any system, "
    "and ask: page, ticket or dashboard?\n\n"
    "Next, we'll meet Prometheus and answer the question this lesson left open: how does a tool get a fresh count "
    "of requests out of a running app every 15 seconds?"
)

P.write_text(json.dumps(d, indent=1, ensure_ascii=False) + "\n")
print("d49 written")
