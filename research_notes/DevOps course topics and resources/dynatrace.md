# Dynatrace for a beginner DevOps course (state as of 30 October 2026)

Verification legend used on every URL below:
- **[opened]** = I read the content myself (GitHub repos cloned with git, or raw.githubusercontent.com read with curl, on 2026-10-30).
- **[search]** = the URL appeared in a WebSearch result and the claim comes from the search snippet or summary. I could not open the page: WebFetch and curl to dynatrace.com, docs.dynatrace.com, community.dynatrace.com, developer.dynatrace.com, nasdaq.com and youtube.com all failed from this sandbox.
- **[linked]** = the URL appears inside a file I opened (for example a README), but I did not open the URL itself.

Audience reminder: an experienced software engineer who is new to observability and works on an Apple Silicon Mac. Every item says whether it is free or paid.

---

## Key question 1: What is the current state of the Dynatrace platform in 2026 ("latest Dynatrace" vs "Dynatrace Classic", new apps, generative and agentic AI), and which names are current vs renamed?

### Takeaway
In 2026 Dynatrace is a SaaS-first platform built on Grail, its data lakehouse. You query it with DQL and work in "apps" (Notebooks, Dashboards, Problems, Workflows, Site Reliability Guardian and others) at `https://<env-id>.apps.dynatrace.com`. The older "Dynatrace Classic" pages still exist as "classic apps". At Perform 2026 (28 January 2026), Dynatrace grouped all of its AI under the name **Dynatrace Intelligence**: "Davis" is now the root-cause component inside it, and **Dynatrace Assist** succeeds **Davis CoPilot**. Agentic features (domain "Intelligence Agents", agentic workflows with approvals, and an MCP server) are the 2026 focus. Docs and APIs still use the old names in many places (Davis CoPilot docs, `davis-copilot:*` token scopes, `dt.davis.problems`), so learners will see both sets of names.

### Cited Findings

**AI naming (the biggest change in 2026)**
- At Perform 2026 in Las Vegas (28 Jan 2026), Dynatrace launched "Dynatrace Intelligence", described as an agentic operations system that fuses deterministic AI (grounded in real-time causal context) with agentic AI that acts within defined guardrails — [Dynatrace press release](https://www.dynatrace.com/news/press-release/dynatrace-intelligence-redefines-observability/) [search]; [Perform 2026 press release](https://www.dynatrace.com/news/press-release/perform-2026-ignites-new-era/) [search].
- Perform 2026 also announced "Dynatrace Intelligence Agents" (specialised domain agents that work together), "agentic workflows" with policy-driven controls and approvals, and an updated Dynatrace MCP Server with support for Claude, AWS Bedrock AgentCore and Azure AI Foundry — [Perform 2026 press release](https://www.dynatrace.com/news/press-release/perform-2026-ignites-new-era/) [search]; [Domain-specific agents PDF](https://d1io3yog0oux5.cloudfront.net/_3bf04250e68f1ac6669adfbd634f07ac/dynatrace/news/2026-01-28_Dynatrace_Introduces_Domain_Specific_Agents_to_412.pdf) [search]; [IT Brief UK](https://itbrief.co.uk/story/dynatrace-unveils-agentic-ai-push-with-new-platform-tools) [search].
- A third-party pricing-page tracker logged that in Q1 2026 "Davis AI" was renamed "Dynatrace Intelligence" across the platform section of dynatrace.com — [PricingSaaS diff Q1 2026](https://pricingsaas.com/companies/dynatrace/diffs/2026Q1) [search]. Techzine says Dynatrace consolidated its AI capabilities under the single name Dynatrace Intelligence, and that Davis remains the root-cause capability inside that umbrella — [Techzine](https://www.techzine.eu/blogs/infrastructure/144561/dynatrace-intelligence-aims-for-autonomous-operations/) [search].
- The docs URL structure supports the rename: the Problems app upgrade guide now lives under `/docs/dynatrace-intelligence/problems-app/` — [Upgrade Problems Classic to Problems on Grail](https://docs.dynatrace.com/docs/dynatrace-intelligence/problems-app/upgrade-guide-problems) [search].
- Davis CoPilot (the generative AI assistant) went GA with SaaS version 1.301 for Dynatrace Platform Subscription customers and 1.304 for classic-licence customers. Davis CoPilot Chat arrived with 1.307 — [Davis CoPilot GA blog](https://www.dynatrace.com/news/blog/announcing-general-availability-of-davis-copilot-your-new-ai-assistant/) [search].
- Dynatrace's blog calls **Dynatrace Assist** "the evolution of Davis CoPilot" and its "next-generation AI chat" — [Dynatrace Assist blog](https://www.dynatrace.com/news/blog/dynatrace-assist-ask-analyze-and-act-with-dynatrace-intelligence/) [search]. The Hub listing still carries Davis CoPilot naming and lists release notes into 2026 (for example 1.332.0 in Feb 2026) — [Hub: Ask Davis CoPilot](https://www.dynatrace.com/hub/detail/ask-davis-copilot/) [search]. The Davis CoPilot docs page still exists — [Davis CoPilot overview](https://docs.dynatrace.com/docs/discover-dynatrace/platform/davis-ai/copilot/copilot-overview) [search].
- Old names survive in APIs. The (now deprecated) local MCP server needs token scopes `davis-copilot:conversations:execute`, `davis-copilot:nl2dql:execute`, `davis-copilot:dql2nl:execute`, `davis:analyzers:read/execute`. It also lists tools `chat_with_davis_copilot` and `execute_davis_analyzer` under the heading "Dynatrace Intelligence" — [dynatrace-oss/dynatrace-mcp README](https://github.com/dynatrace-oss/dynatrace-mcp) [opened].

**AI developer tooling (changed during 2026)**
- The local open-source Dynatrace MCP server is **deprecated**: "Version 2.1.2 was the final release". It recommends **Dynatrace-for-AI + `dtctl`** for local development (VS Code, Claude Code, Cursor and similar) and the **Dynatrace Remote MCP Server** (no local setup) for agent-to-agent use — [dynatrace-mcp README](https://github.com/dynatrace-oss/dynatrace-mcp) [opened].
- The same README warns that MCP-triggered DQL queries "may incur costs" based on GB scanned, and offers a `DT_GRAIL_QUERY_BUDGET_GB` guard (default 1000 GB) — [dynatrace-mcp README](https://github.com/dynatrace-oss/dynatrace-mcp) [opened].
- `dtctl` is "a CLI for Dynatrace SaaS" with kubectl-style verb-noun syntax, for example `dtctl query "fetch logs | limit 10"` and `dtctl get workflows`. Install: `brew install dynatrace-oss/tap/dtctl` (macOS/Linux). Dynatrace Managed has a separate tool, `dtmgd` — [dtctl README](https://github.com/dynatrace-oss/dtctl) [opened].
- "Dynatrace for AI" is an official repo of Agent Skills (DQL essentials, problems, Kubernetes, logs, platform costs, OneAgent setup and more). It is installable with `npx skills add dynatrace/dynatrace-for-ai` or `claude plugin install dynatrace@claude-plugins-official`. The last commit was 29 Oct 2026 — [Dynatrace/dynatrace-for-ai](https://github.com/Dynatrace/dynatrace-for-ai) [opened].

**"Latest Dynatrace" vs "Dynatrace Classic"**
- The docs call the new platform "Latest Dynatrace" and provide an upgrade guide covering new concepts that replace classic configuration, for example management zones → segments — [Latest Dynatrace foundations](https://docs.dynatrace.com/docs/platform/upgrade/foundations) [search].
- Capability mapping: management zones → Segments, IAM policies and clusters; Service Flow → service topology in the unified Services view. Some classic features (Profiling & Optimization, Backtrace) have no direct replacement yet — [Capability mapping Classic → Latest](https://docs.dynatrace.com/docs/platform/upgrade/foundations/capability-mapping-classic-to-latest) [search].
- "Classic apps" (formerly "wrapper apps") are Classic capabilities packaged as apps and opened from the Launcher in latest Dynatrace. Examples are Dashboards Classic and Web Monitoring — [Dynatrace style guide: terminology](https://styleguide.dynatrace.com/docs/dynatrace-terminology) [search].
- "Problems" (on Grail) and "Problems Classic" run side by side and users can switch without data loss. In June 2024 Dynatrace committed to support Problems Classic for at least one year — [Problems upgrade guide](https://docs.dynatrace.com/docs/platform/upgrade/keep-problems-and-alerting-working/upgrade-guide-problems) [search].
- URLs differ by generation. Latest Dynatrace (platform) is `https://<EnvironmentID>.apps.dynatrace.com`. Classic and API endpoints use `https://<EnvironmentID>.live.dynatrace.com` — [obslab tenant-details snippet](https://github.com/Dynatrace/obslab-release-validation) [opened]. One tool says "do not use Dynatrace classic URLs like abc12345.live.dynatrace.com" for platform access — [dynatrace-mcp README](https://github.com/dynatrace-oss/dynatrace-mcp) [opened]. The DynaKube `apiUrl` still uses `https://ENVIRONMENTID.live.dynatrace.com/api` — [operator sample](https://github.com/Dynatrace/dynatrace-operator/blob/main/assets/samples/dynakube/v1beta6/cloudNativeFullStack.yaml) [opened].
- In DQL, classic entity fields `dt.entity.*` are **deprecated**. New queries should use `dt.smartscape.*` fields and the `smartscapeNodes` command ("Smartscape on Grail") — [dt-dql-essentials skill](https://github.com/Dynatrace/dynatrace-for-ai) [opened].

**SaaS vs Managed**
- Grail, AppEngine and AutomationEngine are listed as unavailable on Dynatrace Managed and available on SaaS (selected AWS/Azure regions) — [Unavailable in Dynatrace Managed](https://docs.dynatrace.com/managed/upgrade/unavailable-in-managed) [search]. A Dynatrace community answer says the Managed roadmap does not include Grail, because Grail was built for SaaS and massively parallel processing — [Community: Grail on Dynatrace Managed](https://community.dynatrace.com/t5/Upgrade-to-SaaS/Grail-on-Dynatrace-Managed/td-p/204501) [search]. Managed is still positioned for customers with mandatory on-premises requirements and still gets monthly updates — same thread [search].

**Kubernetes Operator status (verified from GitHub)**
- Latest Dynatrace Operator release tags: **v1.11.1 (21 Oct 2026)**, v1.11.0 (1 Oct 2026), v1.10.0 (15 Jul 2026). The main branch was last committed 29 Oct 2026 — [Dynatrace/dynatrace-operator](https://github.com/Dynatrace/dynatrace-operator) [opened; dates from `git ls-remote` plus tag commit dates].
- Current DynaKube samples use `apiVersion: dynatrace.com/v1beta6`, with v1beta5 samples kept alongside. New v1beta6 samples cover `telemetryIngest` (OTLP, Zipkin, StatsD and Jaeger receivers via the Dynatrace OTel Collector), `otlpExporterConfiguration` (auto-configure apps' OTLP exporters), `logMonitoring`, `kubernetesSecurityPostureManagement` and `resourceAttributes` — [operator samples dir](https://github.com/Dynatrace/dynatrace-operator/tree/main/assets/samples/dynakube) [opened].

**Market positioning (for the comparison segment)**
- In the 2025 Gartner Magic Quadrant for Observability Platforms (published July 2025), Gartner evaluated 20 vendors. Dynatrace says it was positioned highest for Ability to Execute and named a Leader for the 15th consecutive time — [BusinessWire press release](https://www.businesswire.com/news/home/20250710820419/en/Dynatrace-Positioned-Highest-in-Execution-in-the-2025-Gartner-Magic-Quadrant-for-Observability-Platforms) [search].
- Other vendors that say they were Leaders in that 2025 MQ: Datadog (5th consecutive year), New Relic (13th consecutive time), Splunk, IBM, Grafana Labs and Elastic — [Datadog MQ page](https://www.datadoghq.com/resources/gartner-magic-quadrant-observability-platforms-2025/) [search]; [New Relic MQ page](https://newrelic.com/es/resources/gartner-magic-quadrant-observability) [search]; [Grafana Labs blog](https://grafana.com/blog/2025/07/10/grafana-labs-named-a-leader-again-in-the-2025-gartner-magic-quadrant-for-observability-platforms/?pg=contact) [search].

### Inferences
- For a beginner, the clean mental model is: **Dynatrace Intelligence** (umbrella) contains **Davis** (deterministic, causal root-cause analysis and anomaly detection), **Assist** (chat, the successor to Davis CoPilot) and **agents** (actions with guardrails). Expect the UI, docs and APIs to mix these names for the rest of 2026.
- Lessons should teach the **latest Dynatrace** apps (Notebooks, Dashboards, Problems, Workflows, SRG, Kubernetes, Services) and mention Classic only as "what you'll see in older screenshots, blog posts and certification material".
- Because Grail is SaaS-only, everything in Lesson 2 (DQL, Notebooks, Workflows, SRG) assumes SaaS. A learner on a Managed cluster at work would not have it.

### Gaps
- I could not open the Perform 2026 press releases, so I have no GA vs preview status per feature and no confirmation of the exact Intelligence Agent names. Secondary coverage also mentions a DevCycle acquisition and 13-month RUM retention; neither is verified.
- I found no official statement of when, or whether, the "Davis" brand will disappear from APIs and docs.
- I found no end-of-life date for Dynatrace Classic as a whole.

---

## Key question 2: What intuitions help a beginner?

### Takeaway
Three intuitions carry most of Lesson 1. OneAgent is an agent that instruments everything on a host automatically. Smartscape is a live dependency graph built from what OneAgent observes. Davis follows that graph and the traces to a root cause, instead of looking for graphs that spike together. The docs explicitly support the "follows dependencies, not just time correlation" framing.

### Cited Findings
- PurePath distributed traces combine tracing with code-level visibility, topology and metadata. OneAgent collects them automatically across the transaction, and they feed Davis baselining and root-cause analysis — [PurePath distributed traces docs](https://docs.dynatrace.com/docs/observe-and-explore/purepath-distributed-traces) [search].
- Root cause analysis: once Davis detects a problem in a component, it does not rely only on time correlation. It examines monitored transactions (distributed traces) to find dependencies between that problem and other components, then runs a fault-tree analysis to reach the most probable root cause — [Root cause analysis docs](https://docs.dynatrace.com/docs/shortlink/next-gen-ai-analytics) [search].
- Dynatrace markets its AI as deterministic and causation-based rather than correlation-based — [Dynatrace (legacy) AI page](https://www.dynatrace.com/legacy/platform/artificial-intelligence/) [search]. This is vendor positioning.
- Distributed tracing now combines OpenTelemetry signals with OneAgent-captured traces (or Trace Ingest API data) and requires "Traces powered by Grail" — [dt-url.net/vc23u9n (Dynatrace docs short link)](https://dt-url.net/vc23u9n) [search].
- The Smartscape node types used in DQL include `HOST`, `SERVICE`, `PROCESS` and `K8S_CLUSTER`. Each has its own ID field (`dt.smartscape.host`, `dt.smartscape.service` and so on) and is queried with `smartscapeNodes "HOST"` — [dt-dql-essentials skill](https://github.com/Dynatrace/dynatrace-for-ai) [opened].
- Problems are grouped and denoised by root-cause analysis, and alerting uses static-threshold, adaptive-baseline or seasonal-baseline anomaly detectors — [dt-alerting skill](https://github.com/Dynatrace/dynatrace-for-ai) [opened].
- The predictive side uses analyzers: `timeseries-forecast`, `adaptive-anomaly-detector`, `seasonal-baseline-anomaly-detector`, `static-threshold-analyzer` and `timeseries-novelty-detection`. The forecast analyzer is univariate only, and "DQL has no native forecast function" — [dt-obs-predictive-analytics skill](https://github.com/Dynatrace/dynatrace-for-ai) [opened].

### Inferences (teaching intuitions; my framing, not Dynatrace's words)
- **OneAgent = a resident doctor who examines every process on the host.** You install it once per host, or once per node via the Operator. It finds the processes, instruments supported runtimes (Java, .NET, Node.js, Go and others) and starts sending traces, metrics and logs without code changes. Contrast: in the open-source world you add an SDK or exporter per service and wire up each signal.
- **ActiveGate = the hospital's front desk / switchboard.** It is a proxy and routing component that can also talk to things OneAgent can't run inside, such as the Kubernetes API and cloud APIs. In the Operator it appears as `routing`, `kubernetes-monitoring`, `metrics-ingest` and `dynatrace-api` capabilities.
- **Smartscape = a live, self-drawing architecture diagram.** Hosts run processes, processes provide services, services call other services. Nobody draws it; OneAgent observes it.
- **PurePath = one request's itinerary.** It records every service hop for a single request, down to the method or database call.
- **Davis = a detective who walks the dependency map.** It does not say "these 12 graphs spiked at 10:02". It says "the checkout service is slow because it calls the payment service, which is failing on this method". The fault-tree wording in the docs supports this.
- **Predictive vs causal:** causal = "why is it broken now?" (walks the graph). Predictive = "when will this disk fill?" (forecasts one metric from its own history).
- **Problem vs alert:** a problem is a bundle of related events that share a root cause, so one incident produces one ticket instead of 40 alerts.
- **Grail = one big append-only data lake you query with pipes.** It holds logs, spans, events and metrics together, so there are no separate Loki, Tempo and Prometheus stores to join by hand.

### Gaps
- I found no official Dynatrace "explain like I'm five" analogy pages; the analogies above are mine.
- I could not open the Smartscape docs page, so its classic UI behaviour (vertical stack and horizontal call graph) is not cited here.

---

## Key question 3: What do beginners get wrong?

### Takeaway
The common traps are: thinking automatic instrumentation replaces deciding what "good" means (SLOs); ingesting and querying everything without noticing that ingest **and** queries cost money under the Dynatrace Platform Subscription (DPS); following Classic screenshots or `live.` URLs in the latest platform; and writing DQL as if it were SQL. DQL is a left-to-right pipeline with its own syntax rules.

### Cited Findings
**DQL is not SQL.** Dynatrace's own "DQL essentials" skill lists these pitfalls — [dt-dql-essentials skill](https://github.com/Dynatrace/dynatrace-for-ai) [opened]:
- DQL is "a pipeline-based query language … differs from SQL". Queries start with `fetch <data_object>` or `timeseries` and chain commands with `|`.
- Equality is `==`, not `=` (single `=` is assignment in `fieldsAdd` or `summarize` aliases).
- Static lists use `in(field, {"a","b"})`. Square brackets `[...]` wrap **sub-queries**, not array literals.
- Group-by lists need braces: `by: {severity, status}`.
- The log severity field is `loglevel`. `log.level` does not exist. The log message body is `content`.
- There is no `fetch dt.metric`. Metrics use `timeseries avg(metric.key)`. The `metrics` command returns metadata, not values.
- `sort count() desc` fails. Alias the aggregate first (`summarize n = count() | sort n desc`).
- There is no `length()`; use `stringLength()`. Spans have `start_time` and `end_time`, not `timestamp`.
- Do not wrap a filtered field in `lower()` or `upper()`. "It defeats the Grail index and can scan far more data"; use `contains(field, "err", caseSensitive:false)` or `matchesValue`.
- `==` against an array-typed field (for example `k8s.namespace.name` on `dt.davis.problems`) silently matches nothing; use `in()`.
- `dt.entity.*` is deprecated; use `dt.smartscape.*`.
- `percentile`, `median` and `percentRank` in `timeseries` need `rollup:` or they silently return empty results.
- Discover what data exists with `fetch dt.system.data_objects | fields name, display_name, type`.

**Cost awareness**
- DPS is an annual commitment drawn down against a rate card. Usage beyond the commitment continues on demand, billed monthly at the same rates — [Last9: Dynatrace pricing explained (2026)](https://last9.io/blog/dynatrace-pricing/) [search]; [Dynatrace pricing FAQ](https://www.dynatrace.com/pricing/frequently-asked-questions/) [search].
- Querying Grail costs money by data scanned: "using certain capabilities to access data in Dynatrace Grail may incur additional costs … costs depend on the volume (GB scanned)". Advice: start with 12h–24h timeframes and use buckets — [dynatrace-mcp README](https://github.com/dynatrace-oss/dynatrace-mcp) [opened].
- DQL cost levers: filter early, use bucket filters, short time ranges, field selection, `samplingRatio`, and `scanLimitGBytes` — [dt-dql-essentials skill](https://github.com/Dynatrace/dynatrace-for-ai) [opened]. The obslab uses `fetch logs, scanLimitGBytes: 1` — [obslab-release-validation docs](https://github.com/Dynatrace/obslab-release-validation) [opened].
- Billing usage itself is queryable: all DPS consumption lives in `dt.system.events` with `event.kind == "BILLING_USAGE_EVENT"` — [dt-platform-costs skill](https://github.com/Dynatrace/dynatrace-for-ai) [opened]. The same skill warns that the absence of billing events does **not** mean a capability is unlicensed.

**Classic vs latest confusion**
- Classic and latest apps run side by side (for example "Problems" and "Problems Classic"), and classic capabilities appear as "classic apps" in the Launcher — [Problems upgrade guide](https://docs.dynatrace.com/docs/platform/upgrade/keep-problems-and-alerting-working/upgrade-guide-problems) [search]; [style guide terminology](https://styleguide.dynatrace.com/docs/dynatrace-terminology) [search].
- A Dynatrace community thread asks whether the Associate exam covers Classic or new apps; the search result showed no answer — [Community: Associate exam Classic vs new apps](https://community.dynatrace.com/t5/Start-with-Dynatrace/Associate-Exam-Classic-App-vs-New-Apps/m-p/279191) [search].
- The OTLP docs warn that `live.apps.dynatrace.com` is an incorrect base URL; the right one is `{env-id}.live.dynatrace.com/api/v2/otlp` — [Dynatrace OTLP API endpoints](https://docs.dynatrace.com/docs/ingest-from/opentelemetry/otlp-api) [search].

**SLOs are still a human decision**
- Site Reliability Guardian lets "SREs apply Service-Level Objectives (SLOs) for their critical services" to make release decisions. The objectives and thresholds are configured by people, though SRG can suggest auto-baselined thresholds — [Automations docs](https://docs.dynatrace.com/docs/platform-modules/automations) [search]; [obslab "enable auto baselines" step](https://github.com/Dynatrace/obslab-release-validation) [opened].

### Inferences
- Misconception list for the lesson writer:
  1. "Dynatrace will tell me what's important, so I don't need SLOs." Davis detects anomalies against baselines; it does not know your business promise. SLOs and SRG objectives are still yours to write.
  2. "Ingest everything; it's all-in-one." Under DPS every GiB ingested, retained and **scanned** is metered. Treat log ingest like cloud egress.
  3. "The screenshot doesn't match my screen." It is probably Classic. Look for the latest app with the same name, or the "Classic" suffix.
  4. "DQL is SQL with pipes." Wrong operators, braces and field names mostly fail **silently** (zero rows), which is worse than an error.
  5. "Davis = correlation engine." It walks dependencies and traces. If OneAgent can't see the dependency (an uninstrumented service), Davis can't follow it either.
  6. "One agent means no OpenTelemetry." Dynatrace ingests OTLP natively, and the Operator can even auto-configure OTLP exporters.
  7. "Full-stack is always best." On GKE Autopilot, EKS Fargate or Bottlerocket, only application observability is possible.

### Gaps
- I found no Dynatrace-published "top beginner mistakes" list; the list above combines the official pitfall tables with my inferences.

---

## Key question 4: What exact steps let a learner try it (free trial, playground, Operator on kind / Apple Silicon, DQL on demo data)?

### Takeaway
There are two free routes. (1) The **Dynatrace Playground**: a public sandbox with sample data and nothing to install. (2) A **15-day free SaaS trial** for your own data. The lowest-friction hands-on lab is Dynatrace's own **obslab** "Release Validation" lab, which runs the OpenTelemetry demo in **GitHub Codespaces** and sends data to your trial. That avoids Apple Silicon issues entirely. Running the Operator on a local **kind** cluster is plausible, because the images are multi-arch (amd64 and arm64) and Dynatrace itself uses kind for Operator end-to-end tests. However, I found **no official statement** that kind or arm64 Macs are a supported target, so present it as an advanced, best-effort exercise.

### Cited Findings
**Free options**
- Dynatrace offers a 15-day free trial and, separately, a no-cost **Playground**: a public sandbox with sample data, no installation and no data ingestion. Playground is reachable from the environment switcher, and also by people without an account — [Try it free (docs)](https://docs.dynatrace.com/docs/discover-dynatrace/get-started) [search]; [Two ways to get started](https://www.dynatrace.com/try-free) [search].
- One search source said no credit card is required for the trial — [Try it free](https://www.dynatrace.com/try-free) [search]. I could not open the page to confirm.
- The obslab labs link the trial via the short link `https://dt-url.net/trial` and require a Dynatrace environment plus an API token with `metrics.ingest`, `logs.ingest`, `events.ingest` and `openTelemetryTrace.ingest`. The token is created via `Ctrl+K` → "access tokens" — [obslab-release-validation getting-started](https://github.com/Dynatrace/obslab-release-validation) [opened]. The lab opens with "Open in GitHub Codespaces" and asks you to delete the codespace and the API token afterwards — same repo [opened].

**Dynatrace Operator on Kubernetes (exact commands)**
- Operator modes (from the README): `classicFullStack` (one OneAgent pod per node monitors the node and its pods); `applicationMonitoring` (webhook-based app-only injection; the CSI driver can optionally cache OneAgent downloads); `hostMonitoring` (nodes only); `cloudNativeFullStack` = `applicationMonitoring` + `hostMonitoring` (uses the CSI driver). ActiveGate capabilities: `routing`, `kubernetes-monitoring`, `metrics-ingest`. The Operator lives in namespace `dynatrace` — [dynatrace-operator README](https://github.com/Dynatrace/dynatrace-operator) [opened].
- Docs: cloud-native full-stack is the **recommended** deployment, classic full-stack is "supported but no longer recommended for most environments", and the manual OneAgent DaemonSet is deprecated. A CSI driver is mandatory for cloud-native full-stack. On GKE Autopilot or EKS Bottlerocket, full-stack is unavailable and application observability is the default — [Set up Dynatrace on Kubernetes: deployment](https://docs.dynatrace.com/docs/ingest-from/setup-on-k8s/deployment) [search]; [Classic full-stack page](https://docs.dynatrace.com/docs/shortlink/installation-k8s-classic-fs) [search]; [K8s quickstart](https://docs.dynatrace.com/docs/ingest-from/setup-on-k8s/quickstart) [search]. The docs group the options as "Kubernetes platform monitoring", "Application observability" and "Full-Stack observability" — same pages [search].
- Install with Helm (OCI chart; chart tags carry no `v` prefix, GitHub tags do) — [dt-setup-oneagent kubernetes reference](https://github.com/Dynatrace/dynatrace-for-ai) [opened]. That reference pins 1.9.0; the latest tag is v1.11.1, so the version below is updated (the 1.11.1 chart itself was not checked):
  ```bash
  helm upgrade --install dynatrace-operator oci://public.ecr.aws/dynatrace/dynatrace-operator \
    --version 1.11.1 --create-namespace --namespace dynatrace --atomic
  ```
  Manifest fallback: `kubectl apply -f https://github.com/Dynatrace/dynatrace-operator/releases/download/v1.11.1/kubernetes-csi.yaml`. I confirmed this asset returns HTTP 200; a `kubernetes.yaml` (non-CSI) asset also exists, HTTP 200 [opened].
- Secret named `dynakube` with keys `apiToken` and `dataIngestToken`. The reference recommends piping a manifest rather than `--from-literal`, so the token never appears in the process list — [dt-setup-oneagent kubernetes reference](https://github.com/Dynatrace/dynatrace-for-ai) [opened].
- Official `cloudNativeFullStack` sample, current main branch, comments removed — [cloudNativeFullStack.yaml](https://github.com/Dynatrace/dynatrace-operator/blob/main/assets/samples/dynakube/v1beta6/cloudNativeFullStack.yaml) [opened]:
  ```yaml
  apiVersion: dynatrace.com/v1beta6
  kind: DynaKube
  metadata:
    name: dynakube
    namespace: dynatrace
  spec:
    apiUrl: https://ENVIRONMENTID.live.dynatrace.com/api
    selfMonitoring: {}
    metadataEnrichment:
      enabled: true
    oneAgent:
      cloudNativeFullStack:
        tolerations:
          - effect: NoSchedule
            key: node-role.kubernetes.io/master
            operator: Exists
          - effect: NoSchedule
            key: node-role.kubernetes.io/control-plane
            operator: Exists
    activeGate:
      capabilities: [routing, kubernetes-monitoring, dynatrace-api]
      resources:
        requests: { cpu: 200m, memory: 6Gi }
        limits:   { cpu: 1000m, memory: 6Gi }
  ```
  The `applicationMonitoring` sample is identical except `oneAgent: { applicationMonitoring: {} }` — [applicationMonitoring.yaml](https://github.com/Dynatrace/dynatrace-operator/blob/main/assets/samples/dynakube/v1beta6/applicationMonitoring.yaml) [opened]. The samples also include a commented-out `namespaceSelector` (matchLabels or matchExpressions) to limit injection to chosen namespaces, and point to sizing guidance at `https://dt-url.net/26agsizes` and the parameter reference `https://docs.dynatrace.com/docs/ingest-from/setup-on-k8s/reference/dynakube-parameters` [linked].
- **Conflicting ActiveGate sizing:** the official sample asks for **6Gi** memory (request and limit), while the official AI-skill example uses `requests: {cpu: 500m, memory: 512Mi}` and `limits: {cpu: 1000m, memory: 1.5Gi}` — [operator sample](https://github.com/Dynatrace/dynatrace-operator/blob/main/assets/samples/dynakube/v1beta6/cloudNativeFullStack.yaml) [opened] vs [dt-setup-oneagent kubernetes reference](https://github.com/Dynatrace/dynatrace-for-ai) [opened].
- Run `kubectl apply --dry-run=server -f dynakube.yaml` first, because the Operator webhook returns useful validation errors. Uninstall in order: delete the DynaKube, wait for its finalizers, uninstall Helm, delete the CRDs, then the namespace. Otherwise the namespace can stay stuck in `Terminating` — [dt-setup-oneagent kubernetes reference](https://github.com/Dynatrace/dynatrace-for-ai) [opened].
- EKS Fargate: `applicationMonitoring` only, without CSI. Bottlerocket: `applicationMonitoring` only — same reference [opened].

**kind and Apple Silicon (arm64) evidence**
- Operator images are built for `linux/amd64,linux/arm64,linux/ppc64le,linux/s390x` — [operator .github/workflows/ci.yaml](https://github.com/Dynatrace/dynatrace-operator) [opened].
- The Operator repo ships a kind setup (`hack/kind/setup.sh`, `hack/kind/cluster.yaml`; kind node images for Kubernetes 1.29 to 1.37) and an "E2E tests on kind" GitHub workflow. It runs suites `deploy`, `edgeconnect` and `smoke` on `ubuntu-24.04` runners with kind v0.33.0 and Helm v4.3.1 — [dynatrace-operator repo](https://github.com/Dynatrace/dynatrace-operator) [opened].
- The OneAgent support matrix lists ARM64 (AArch64) for several Linux distributions (for example Debian 11–13, RHEL 7–10, Rocky 8–10) — [Technology support](https://docs.dynatrace.com/docs/ingest-from/technology-support) [search].
- A 2024 community thread reports a DynaKube failing on arm64 Kubernetes nodes that worked on amd64, with no confirmed resolution — [Community: OneAgent DynaKube fails on arm64 nodes](https://community.dynatrace.com/t5/Container-platforms/Oneagent-Dynakube-deployment-fails-for-K8s-arm64-nodes/m-p/244414) [search].

**DQL on demo data**
- The obslab's first DQL check, run in a Notebook (Notebook → `+` → DQL section): `fetch logs, scanLimitGBytes: 1 | filter contains(content, "conversion")`. Expected result: log lines from the OpenTelemetry demo — [obslab validate-telemetry step](https://github.com/Dynatrace/obslab-release-validation) [opened].

### Inferences
- **Recommended learner path on an Apple Silicon Mac (cheapest to hardest):**
  1. **Playground** (free, no install). Practise DQL in Notebooks, explore Problems, Services and Smartscape on sample data.
  2. **15-day trial + obslab in GitHub Codespaces** (Dynatrace is free for 15 days; Codespaces runs on GitHub's amd64 VMs, so the Mac's arm64 doesn't matter). You get a real Operator or OTel setup, real traces and an SRG exercise. Check your own GitHub Codespaces free quota first; I did not research it.
  3. **Local kind on the Mac** (advanced). Start with `applicationMonitoring`, and lower the ActiveGate memory or omit the ActiveGate. Reasons: kind nodes are Docker containers, so a host-level agent (`cloudNativeFullStack`, `classicFullStack`) is less likely to work than app-only injection, and a 6Gi ActiveGate request will likely sit `Pending` on a default Docker Desktop VM. Arm64 images exist, but treat this path as "may work, unsupported".
- Teach that the trial clock (15 days) starts at sign-up. Learners should finish the reading first, then start the trial when ready to do Lesson 2's labs back to back.

### Gaps
- I could not open the trial page, so these are unconfirmed: what is included in the trial (all apps? Grail? any ingest caps?), what happens on day 16, and whether Playground needs a sign-up form. The URL `https://prod-website.dynatrace.com/signup/playground` appeared in search results, but its odd host suggests a staging mirror, so I do not recommend citing it.
- I found no official doc stating that kind, Docker Desktop or Apple Silicon is supported or unsupported for the Operator. Dynatrace's own kind tests run on amd64.
- I don't know which sample datasets the Playground contains, so I cannot promise that a given query returns rows there. Tell learners to start with `fetch dt.system.data_objects`.

---

## Key question 5 (Lesson 1 build sheet): Dynatrace as an all-in-one observability platform

### Takeaway
Teach Dynatrace as "agent-first, auto-discovered, causal". One agent (OneAgent) instruments hosts and processes automatically. The platform builds a live topology (Smartscape) and per-request traces (PurePath). Davis walks that graph to produce a **problem** with a **root cause**, instead of a flood of alerts. Then contrast it with assembling Prometheus + Grafana + Loki + Tempo/Jaeger yourself, and with Datadog, New Relic and Elastic.

### Cited Findings
**Concepts in teaching order (one line each, with source)**
1. **The problem it solves.** Logs, metrics and traces live in different tools, and correlating them during an incident is manual. Dynatrace's pitch is unified data plus causal AI — [Dynatrace (legacy) AI page](https://www.dynatrace.com/legacy/platform/artificial-intelligence/) [search]; [Gartner MQ 2025 press release](https://www.businesswire.com/news/home/20250710820419/en/Dynatrace-Positioned-Highest-in-Execution-in-the-2025-Gartner-Magic-Quadrant-for-Observability-Platforms) [search].
2. **SaaS vs Managed.** SaaS is hosted by Dynatrace and includes Grail, AppEngine and AutomationEngine. Managed is self-hosted for on-prem requirements and has none of those three — [Unavailable in Managed](https://docs.dynatrace.com/managed/upgrade/unavailable-in-managed) [search].
3. **OneAgent and automatic instrumentation.** A single agent per host (or per node or pod via the Operator) auto-captures PurePath traces end to end — [PurePath docs](https://docs.dynatrace.com/docs/observe-and-explore/purepath-distributed-traces) [search]; [operator README](https://github.com/Dynatrace/dynatrace-operator) [opened].
4. **ActiveGate.** A routing and proxy component with capabilities such as `routing`, `kubernetes-monitoring`, `metrics-ingest` and `dynatrace-api` — [operator README and samples](https://github.com/Dynatrace/dynatrace-operator) [opened]. Environment ActiveGates also expose the OTLP endpoint (default port 9999) — [OTLP API docs](https://docs.dynatrace.com/docs/ingest-from/opentelemetry/otlp-api) [search].
5. **Entities: hosts → processes → services (and K8s clusters).** These are typed topology nodes (`HOST`, `PROCESS`, `SERVICE`, `K8S_CLUSTER`) with `dt.smartscape.*` IDs — [dt-dql-essentials](https://github.com/Dynatrace/dynatrace-for-ai) [opened].
6. **Smartscape topology map.** The live relationship graph between those entities, now also queryable in DQL with `smartscapeNodes` and `smartscapeEdges` — [dt-dql-essentials](https://github.com/Dynatrace/dynatrace-for-ai) [opened]; video [How to query Smartscape on Grail](https://www.youtube.com/watch?v=ujSWwuyvCVE) [search].
7. **PurePath distributed traces.** Per-request, code-level traces that merge with OpenTelemetry spans in Grail — [PurePath docs](https://docs.dynatrace.com/docs/observe-and-explore/purepath-distributed-traces) [search]; [dt-url.net/vc23u9n](https://dt-url.net/vc23u9n) [search].
8. **Davis (causal) and problems with root cause.** It detects an anomaly, follows trace dependencies, then runs a fault-tree analysis to find the most probable root cause — [Root cause analysis docs](https://docs.dynatrace.com/docs/shortlink/next-gen-ai-analytics) [search]. Problems are stored in Grail as `dt.davis.problems` (status `ACTIVE` or `CLOSED`) — [dt-obs-problems skill](https://github.com/Dynatrace/dynatrace-for-ai) [opened].
9. **Davis (predictive).** Univariate forecasting and anomaly analyzers (adaptive baseline, seasonal baseline, static threshold) — [dt-obs-predictive-analytics](https://github.com/Dynatrace/dynatrace-for-ai) [opened]; [dt-alerting](https://github.com/Dynatrace/dynatrace-for-ai) [opened].
10. **Dynatrace Intelligence and Assist (generative and agentic AI).** See Key question 1. Assist answers questions and can write DQL (the scopes include `nl2dql` and `dql2nl`) — [dynatrace-mcp README](https://github.com/dynatrace-oss/dynatrace-mcp) [opened]; video [How to use Dynatrace Assist](https://m.youtube.com/watch?v=_XgzpUBZK08) [search].
11. **Dashboards and Notebooks.** Notebooks are where you write DQL step by step; Dashboards are for sharing. "Dashboards Classic" is the old version — [obslab notebook step](https://github.com/Dynatrace/obslab-release-validation) [opened]; [style guide](https://styleguide.dynatrace.com/docs/dynatrace-terminology) [search]. Official AI skills exist for both apps (`dt-app-notebooks`, `dt-app-dashboards`) — [dynatrace-for-ai](https://github.com/Dynatrace/dynatrace-for-ai) [opened].
12. **Positioning vs others.** All of these were 2025 Gartner MQ Leaders: Dynatrace (highest Ability to Execute), Datadog, New Relic, Splunk, IBM, Grafana Labs and Elastic — sources in Key question 1 [search].

**Example DQL for Lesson 1 (show, don't drill)** — patterns from [dt-dql-essentials](https://github.com/Dynatrace/dynatrace-for-ai) and [dt-obs-problems](https://github.com/Dynatrace/dynatrace-for-ai) [opened]:
```dql
// Topology: list hosts known to Smartscape
smartscapeNodes "HOST"
```
```dql
// Active problems Davis has opened in the last 2 hours
fetch dt.davis.problems, from:now() - 2h
| filter not(dt.davis.is_duplicate) and event.status == "ACTIVE"
| fields event.start, display_id, event.name, event.category
| sort event.start desc
| limit 20
```
Expected result: a table with one row per active problem (display IDs look like `P-XXXXX`), or zero rows on a quiet environment.

### Inferences
**Comparison talking points** (my synthesis; check before stating as fact):
- **Open-source stack (Prometheus + Grafana + Loki or Elasticsearch + Jaeger or Tempo):** free software, but you run and scale four or five backends. You instrument each service (OTel SDKs or exporters), and you build the correlation yourself (exemplars, trace IDs in logs, dashboards and alert rules). Dynatrace: one agent, auto-discovered topology, causal problem grouping and one query language over one store, in exchange for licence cost and vendor lock-in.
- **Datadog and New Relic:** also SaaS, all-in-one and agent-based, and also Gartner Leaders. Dynatrace's distinguishing claims are the deterministic topology-driven causal AI (Davis), the auto-discovered Smartscape, and Grail plus DQL as a single store and language.
- **Elastic Observability:** grew from search and logs (ELK). It can be self-managed or cloud, and Elastic was also a 2025 MQ Leader.
- **Exercise ideas (Lesson 1, about 40 minutes, Playground only, free):**
  1. *Topology tour (10 min):* in Playground, open a service, find its host and process, and sketch the three-tier relationship on paper. Then run `smartscapeNodes "SERVICE"`.
  2. *Problem post-mortem (10 min):* open any problem and write down the root-cause entity, the affected entities and the evidence Davis cites. Discussion question: "How would you have found this with Grafana dashboards?"
  3. *Trace reading (10 min):* open one distributed trace and identify the slowest span and which service owns it.
  4. *Ask Assist (5 min):* ask it to "show error logs from the last hour", then read and critique the DQL it generates.
- Keep Dynatrace Intelligence and agentic AI to about 3 minutes in Lesson 1: name it, say what Assist does, and say "agents act within guardrails and approvals".

**Curated resources (Lesson 1)**
1. [Distributed tracing by PurePath technology (docs)](https://docs.dynatrace.com/docs/observe-and-explore/purepath-distributed-traces) — [search]
2. [Root cause analysis (docs)](https://docs.dynatrace.com/docs/shortlink/next-gen-ai-analytics) — [search]
3. [Latest Dynatrace foundations / capability mapping Classic → Latest](https://docs.dynatrace.com/docs/platform/upgrade/foundations/capability-mapping-classic-to-latest) — [search]
4. [Dynatrace Assist blog (successor to Davis CoPilot)](https://www.dynatrace.com/news/blog/dynatrace-assist-ask-analyze-and-act-with-dynatrace-intelligence/) — [search]
5. [Techzine: Dynatrace Intelligence aims for autonomous operations (independent read on Perform 2026)](https://www.techzine.eu/blogs/infrastructure/144561/dynatrace-intelligence-aims-for-autonomous-operations/) — [search]
6. Video: [How to query Smartscape on Grail (Dynatrace DQL)](https://www.youtube.com/watch?v=ujSWwuyvCVE) — [search; channel not verified]
7. Video: [How to use Dynatrace Assist](https://m.youtube.com/watch?v=_XgzpUBZK08) — [search; channel not verified]
8. [Gartner MQ 2025 (Dynatrace press release, for positioning only)](https://www.businesswire.com/news/home/20250710820419/en/Dynatrace-Positioned-Highest-in-Execution-in-the-2025-Gartner-Magic-Quadrant-for-Observability-Platforms) — [search]

### Gaps
- No independent, primary source compares Dynatrace feature by feature with Datadog, New Relic or Elastic; the comparison above is inference.
- I couldn't verify which YouTube uploads come from Dynatrace's official channel or from "Observability Clinic". Observability Clinic sessions found in search are on-demand registration pages, not YouTube links: [Kubernetes managed by Davis](https://info.dynatrace.com/global-all-wc-observability-clinic-kubernetes-managed-by-davis-18556-registration.html) and [OpenObservability](https://info.dynatrace.com/global-all-wc-observability-clinic-openobservability-21799-registration.html) [search]. I found no KodeKloud Dynatrace content.
- I have no cited list of the languages and runtimes OneAgent auto-instruments; check the technology-support page before listing them.

---

## Key question 6 (Lesson 2 build sheet): Dynatrace in practice — Operator, Grail and DQL, SLOs, workflows, OpenTelemetry, SRG, trial, pricing, certification

### Takeaway
Lesson 2 should be hands-on in this order:
1. Get a tenant (Playground or the 15-day trial).
2. Get data in: the Operator on Kubernetes, or OTLP from an OpenTelemetry app.
3. Query it in a Notebook with DQL (fetch → filter → summarize → makeTimeseries or timeseries).
4. Turn the queries into SLOs and a Site Reliability Guardian release check triggered from CI/CD via a Workflow.
5. Close with cost (DPS: ingest, retention and query scanning are all metered) and with the learning path (Dynatrace University and the Associate certification).

### Cited Findings
**A. Dynatrace Operator on Kubernetes** — see Key question 4 for commands and manifests. Key facts:
- Latest release: v1.11.1 (21 Oct 2026). DynaKube `dynatrace.com/v1beta6` — [dynatrace-operator](https://github.com/Dynatrace/dynatrace-operator) [opened].
- Modes: `cloudNativeFullStack` (recommended; needs CSI), `applicationMonitoring` (app-only injection; the only option on Fargate, Bottlerocket and GKE Autopilot), `hostMonitoring`, `classicFullStack` (supported, not recommended) — [operator README](https://github.com/Dynatrace/dynatrace-operator) [opened]; [K8s deployment docs](https://docs.dynatrace.com/docs/ingest-from/setup-on-k8s/deployment) [search].
- Teams onboard namespaces by labelling them, using a standard selector — [Dynatrace blog: Kubernetes-native observability](https://www.dynatrace.com/news/blog/flexible-scalable-self-service-kubernetes-native-observability/) [search]. The DynaKube sample shows `namespaceSelector` with matchLabels or matchExpressions — [cloudNativeFullStack.yaml](https://github.com/Dynatrace/dynatrace-operator/blob/main/assets/samples/dynakube/v1beta6/cloudNativeFullStack.yaml) [opened].
- Expected result after a successful apply (inference from the README, not verified on a cluster): the Operator, webhook and CSI-driver pods in namespace `dynatrace`, an ActiveGate StatefulSet pod, OneAgent pods per node (full-stack modes), and the Kubernetes app in Dynatrace showing the cluster.

**B. Grail and DQL basics** — all patterns from [dt-dql-essentials](https://github.com/Dynatrace/dynatrace-for-ai) [opened] unless noted.
- Grail stores logs, spans, events, bizevents, security events, RUM sessions and metrics. Data objects include `logs`, `spans`, `events`, `bizevents`, `dt.davis.problems`, `dt.davis.events`, `user.sessions` and `dt.system.events`. Metrics use `timeseries`, and topology uses `smartscapeNodes`.
- Grail is GA for SaaS on AWS and Azure — [Unavailable in Managed / upgrade info](https://docs.dynatrace.com/managed/upgrade/unavailable-in-managed) [search].
- Teaching sequence of queries:
  ```dql
  // 0. What data exists?
  fetch dt.system.data_objects | fields name, display_name, type
  ```
  ```dql
  // 1. fetch + limit (cheap first look)
  fetch logs, from: -1h | limit 10
  ```
  ```dql
  // 2. filter (note ==, loglevel, content)
  fetch logs, from: -1h, scanLimitGBytes: 1
  | filter loglevel == "ERROR"
  | filter contains(content, "timeout", caseSensitive:false)
  ```
  ```dql
  // 3. summarize (alias, then sort)
  fetch logs, from: -2h
  | filter loglevel == "ERROR"
  | summarize errors = count(), by: {k8s.namespace.name}
  | sort errors desc
  ```
  Query 3 is my composition from the documented rules (`loglevel`, `by: {…}`, aliasing before `sort`). Expected result: one row per namespace with an error count.
  ```dql
  // 4. makeTimeseries: chart non-metric data over time
  fetch logs
  | makeTimeseries {total = count(), errors = countIf(loglevel == "ERROR")},
      interval: 5m, by: {k8s.cluster.name}
  | fieldsAdd error_rate = errors[] * 100.0 / total[]
  ```
  Expected result: one row per cluster with array columns (one value per 5-minute bucket) that a Notebook renders as a line chart.
  ```dql
  // 5. timeseries: real metrics (not fetch!)
  timeseries cpu = avg(dt.host.cpu.usage), by:{dt.smartscape.host}
  | fieldsAdd avg_cpu = arrayAvg(cpu), max_cpu = arrayMax(cpu)
  ```
  ```dql
  // 6. RED metrics per service (response time is in microseconds, hence /1000)
  timeseries {
    p95 = percentile(dt.service.request.response_time, 95),
    total_requests = sum(dt.service.request.count),
    failures = sum(dt.service.request.failure_count)
  }, by: {dt.service.name}
  | fieldsAdd p95_ms = p95[] / 1000, error_rate_pct = (failures[] * 100.0) / total_requests[]
  ```
  Source for query 6: [dt-obs-services skill](https://github.com/Dynatrace/dynatrace-for-ai) [opened].
  ```dql
  // 7. SLO-style compliance from spans
  fetch spans, from: now() - 1h | filter request.is_root_span == true
  | fieldsAdd meets_sla = if(request.is_failed == false AND duration < 3s, 1, else: 0)
  | summarize total = count(), sla_compliant = sum(meets_sla), by: {dt.service.name}
  | fieldsAdd sla_compliance_pct = (sla_compliant * 100.0) / total
  ```
  Source for query 7: [dt-obs-services skill](https://github.com/Dynatrace/dynatrace-for-ai) [opened].
  ```dql
  // 8. Cost awareness: what is consuming my subscription?
  fetch dt.system.events, from: -7d
  | filter event.kind == "BILLING_USAGE_EVENT"
  | summarize event_count = count(), by: {event.type}
  | sort event_count desc
  ```
  Source for query 8: [dt-platform-costs skill](https://github.com/Dynatrace/dynatrace-for-ai) [opened].
- Community-documented gotcha: you cannot compute a ratio inside `makeTimeseries`. Build both series, then compute the ratio in `fieldsAdd` with `[]` array arithmetic — [Community: convert DQL log query to timeseries](https://community.dynatrace.com/t5/DQL/convert-DQL-log-query-to-timeseries/td-p/242310) [search]. For sparse data, `makeTimeseries` returns empty unless you use `nonempty: true` with `default: 0` — [DQL aggregation commands docs](https://docs.dynatrace.com/docs/discover-dynatrace/platform/grail/dynatrace-query-language/commands/aggregation-commands) [search].

**C. SLOs**
- There is a platform SLO API to list templates and SLOs, create, update and delete them, and start or poll evaluations; it is pitched for automating SLO lifecycle and integrating SLO checks into workflows — [Platform SLO API v1](https://docs.dynatrace.com/docs/dynatrace-api/platform-api/platform-slo-v1) [search]. There is an SLO app in the Hub — [Hub: Service-Level Objectives](https://www.dynatrace.com/hub/detail/service-level-objectives) [search]. Classic SLO docs are separate — [SLO Classic](https://docs.dynatrace.com/docs/deliver/service-level-objectives-classic/configure-and-monitor-slo) [search].

**D. Workflows and automation**
- AutomationEngine is the backend of the Workflows app; it manages workflows and runs executions, and is not meant for mass data ingest or export — [AutomationEngine (developer docs)](https://developer.dynatrace.com/develop/platform-services/services/automation-engine/) [search]; [AutomationEngine docs](https://docs.dynatrace.com/docs/discover-dynatrace/platform/automationengine) [search].
- Problem-triggered notification routing goes through workflows to email, Slack, ServiceNow or webhooks — [dt-alerting skill](https://github.com/Dynatrace/dynatrace-for-ai) [opened]. Official sample workflows are in [Dynatrace/dynatrace-workflow-samples](https://github.com/Dynatrace/dynatrace-workflow-samples) [opened: README returns HTTP 200].

**E. OpenTelemetry ingestion**
- SaaS OTLP base: `https://{env-id}.live.dynatrace.com/api/v2/otlp`; append signal paths such as `/v1/traces`. Header: `Authorization: Api-Token <token>`. Scopes: `openTelemetryTrace.ingest`, `metrics.ingest`, `logs.ingest` (combinable in one token). **HTTP only, gRPC not supported** on this endpoint, and protobuf must be binary (no JSON). Environment ActiveGates use port 9999 by default. Standard env vars: `OTEL_EXPORTER_OTLP_ENDPOINT` and `OTEL_EXPORTER_OTLP_HEADERS` — [Dynatrace OTLP API endpoints](https://docs.dynatrace.com/docs/ingest-from/opentelemetry/otlp-api) [search]; [OTLP export getting started](https://docs.dynatrace.com/docs/ingest-from/opentelemetry/getting-started/otlp-export) [search].
- On Kubernetes, the Operator can deploy the Dynatrace OTel Collector (`public.ecr.aws/dynatrace/dynatrace-otel-collector`) to receive OTLP, Zipkin, StatsD and Jaeger (`spec.telemetryIngest`). It can also auto-configure app OTLP exporters for metrics, traces and logs (`spec.otlpExporterConfiguration`) — [telemetryIngest.yaml and otlpExporterAutoConfiguration.yaml samples](https://github.com/Dynatrace/dynatrace-operator/tree/main/assets/samples/dynakube/v1beta6) [opened].

**F. Release validation with Site Reliability Guardian (SRG) in CI/CD**
- SRG is an app that validates a new release against objectives for availability, performance, capacity and security. The CI/CD tool sends an event, and a Workflow runs the guardian. Dynatrace recommends **SDLC events** (business events are also supported). There are native integrations for GitHub Actions, GitLab, Azure DevOps, Argo CD and others. The result is stored as an SDLC event you can query with DQL to promote or block a release — [Release validation docs](https://docs.dynatrace.com/docs/deliver/quality-gates) [search]; [Release validation use case](https://docs.dynatrace.com/docs/platform-modules/automations/use-cases/release-validation) [search].
- Cloud Automation's (Keptn-based) quality gates moved to SRG. Instead of `slo.yaml` and `sli.yaml` files you define a guardian whose objectives set pass and warning thresholds — [Upgrade from Cloud Automation to SRG](https://docs.dynatrace.com/docs/deliver/site-reliability-guardian/evolve-to-srg) [search].
- Harness CD has a documented SRG integration (Harness deploys and decides; Dynatrace evaluates) — [Harness: Dynatrace SRG](https://developer.harness.io/docs/continuous-delivery/verify/configure-cv/health-sources/dynatrace/dynatrace-srg) [search].
- Concrete lab flow from obslab-release-validation, last updated 25 Aug 2026 — [Dynatrace/obslab-release-validation](https://github.com/Dynatrace/obslab-release-validation) [opened]:
  1. Run the OpenTelemetry demo in Codespaces.
  2. Create a guardian for `checkoutservice` ("Three golden signals") with auto-baselined thresholds.
  3. Have a k6 load test send a `CUSTOM_INFO` event to `/api/v2/events/ingest` at teardown.
  4. Click "Automate" to create a Workflow whose filter is `event.type == "CUSTOM_INFO" and dt.entity.service.name == "checkoutservice" and tool == "k6" and action == "test" …`.
  5. Enable the `paymentServiceFailure` feature flag. **Expected result:** the guardian **fails** because the checkoutservice error rate is too high, and the span events show `exception.message: PaymentService Fail Feature Flag Enabled`.
  6. Roll back the flag.
  The README links a [YouTube overview video](https://www.youtube.com/watch?v=91t_NWnTFWA) [linked] and the [hands-on guide](https://dynatrace.github.io/obslab-release-validation/) [linked].

**G. Pricing model (high level)**
- **Dynatrace Platform Subscription (DPS):** an annual commitment drawn down by usage against a rate card. Overage continues on demand at the same rates. Your individual rate card is part of your purchase order and visible in Account Management — [Dynatrace pricing FAQ](https://www.dynatrace.com/pricing/frequently-asked-questions/) [search]; [How pricing works (docs)](https://docs.dynatrace.com/docs/license/how-pricing-works) [search]; [Rate card](https://dynatrace.com/pricing/rate-card) [search, not opened].
- Indicative public list rates, **from third-party sites only (not verified against the official rate card)**: Full-Stack Monitoring $0.01 per memory-GiB-hour (4 GiB per-host minimum); Infrastructure Monitoring $0.04 per host-hour; Log ingest $0.20 per GiB; log retention $0.0007 per GiB-day; Kubernetes $0.002 per pod-hour — [Last9](https://last9.io/blog/dynatrace-pricing/) [search]; [SigNoz](https://signoz.io/guides/dynatrace-pricing/) [search]; [CubeAPM](https://cubeapm.com/blog/dynatrace-pricing-and-review/) [search].
- Older non-DPS environments use classic licence units (host units, DDUs, DEM units and so on) — [dt-platform-costs skill](https://github.com/Dynatrace/dynatrace-for-ai) [opened].

**H. Dynatrace University and certification**
- Dynatrace University is the official training hub — [Dynatrace University](https://www.dynatrace.com/dynatrace-university/) [search]. Community threads point to a 2025 Associate certification learning-path PDF there — [Community: Associate exam preparation](https://community.dynatrace.com/t5/Open-Q-A/Dynatrace-Associate-Exam-Preparation/m-p/277212) [search].
- Exam cost and format are **unverified**: one third-party prep site says about $200 for public candidates (often free for partners), 70 questions in 105 minutes, online and proctored — [open-exam-prep](https://open-exam-prep.com/practice/dynatrace-associate) [search]. An older blog says the Associate exam used to be free but no longer is — [qainsights](https://qainsights.com/?p=4834) [search].

### Inferences
**Concepts in teaching order (Lesson 2) with intuitions:**
1. *Tenant and tokens.* Your environment ID is in the URL. The API token is a scoped key; give it only the `*.ingest` scopes you need. Intuition: a house key cut for one door.
2. *Operator and DynaKube.* The Operator is a robot that installs and upgrades the agents; the DynaKube is the order form. Intuition: a Kubernetes-native installer.
3. *Deployment modes.* `applicationMonitoring` = monitor my apps only. `cloudNativeFullStack` = monitor my apps and my nodes. Intuition: "tenant vs landlord view".
4. *Grail.* One lake for every signal; you pay to put data in, keep it, and scan it. Intuition: a pay-per-scan data warehouse.
5. *DQL.* Data flows left to right through pipes, like a shell pipeline (`cat | grep | sort | uniq -c`), not SQL's declarative `SELECT … FROM … WHERE`.
6. *Notebooks → Dashboards.* Explore in a Notebook, then pin tiles to a Dashboard.
7. *SLOs.* You decide what "good" is (for example 99.5% of checkout requests succeed under 3 s); Dynatrace measures it.
8. *Workflows.* "If this event, then run these steps": notify, run a guardian, call a webhook.
9. *SRG.* An automated go/no-go gate: the SLOs evaluated over the window of a test or deploy.
10. *OpenTelemetry.* The vendor-neutral path. Dynatrace accepts OTLP over HTTP, so code instrumented with OTel can ship to Dynatrace or to an open-source backend.
11. *Cost and next steps.* DPS metering, the billing query, Dynatrace University.

**Hands-on exercises (Lesson 2, about 40 minutes):**
- **Ex 1 — DQL ladder (Playground, free, 15 min):** run queries 0 → 1 → 2 → 3 → 4 above, saving each in a Notebook. Then deliberately run the "wrong" SQL-style versions (`filter loglevel = "ERROR"`, `by: k8s.namespace.name` without braces, `fetch dt.metric`) and read the errors.
- **Ex 2 — Release gate (trial + Codespaces, free during trial, 20 min):** follow obslab-release-validation through the guardian failure and rollback. Then write the DQL that lists SRG results.
- **Ex 3 — OTLP (stretch, trial):** point an OTel-instrumented app's `OTEL_EXPORTER_OTLP_ENDPOINT` at `https://<env>.live.dynatrace.com/api/v2/otlp` with the `Api-Token` header and `http/protobuf`, then find the spans with `fetch spans`.
- **Ex 4 — Operator on kind (stretch, Apple Silicon, best effort):** install the Operator with Helm, apply an `applicationMonitoring` DynaKube with reduced ActiveGate memory, run `kubectl apply --dry-run=server` first, and observe the pods in `dynatrace`. Uninstall in the documented order.
- **Ex 5 — Cost check (trial):** run the billing query (query 8) at the end of the trial and discuss which categories dominated.

**Free vs paid summary for the lesson writer:**
- **Free:** the Playground; the 15-day trial (no card required per one search result); the obslab repos and the Dynatrace-for-AI skills and `dtctl` (open source); Dynatrace Operator (Apache-2.0); Dynatrace University content (the exact free scope is unverified).
- **Paid:** anything after the trial (DPS); the Associate exam fee (unverified); GitHub Codespaces beyond your free quota.

**Curated resources (Lesson 2)**
1. [Dynatrace/dynatrace-operator (README, DynaKube samples, releases)](https://github.com/Dynatrace/dynatrace-operator) — [opened]
2. [Set up Dynatrace on Kubernetes: deployment options](https://docs.dynatrace.com/docs/ingest-from/setup-on-k8s/deployment) — [search]
3. [Dynatrace/obslab-release-validation (SRG lab in Codespaces)](https://github.com/Dynatrace/obslab-release-validation) plus its [overview video](https://www.youtube.com/watch?v=91t_NWnTFWA) — [opened / linked]
4. [Release validation docs (SRG)](https://docs.dynatrace.com/docs/deliver/quality-gates) — [search]
5. [Dynatrace OTLP API endpoints](https://docs.dynatrace.com/docs/ingest-from/opentelemetry/otlp-api) — [search]
6. [Dynatrace/dynatrace-for-ai: dt-dql-essentials skill (best concise DQL pitfalls table)](https://github.com/Dynatrace/dynatrace-for-ai) — [opened]
7. Video: [A Practical Guide to DQL (Dynatrace Query Language)](https://www.youtube.com/watch?v=F2VbVqNlswk) — [search; channel not verified]. Alternatives: [Search data in DQL](https://www.youtube.com/watch?v=T_Ejvcqzk6s), [Dynatrace Can Do THAT with OpenTelemetry](https://www.youtube.com/watch?v=wfikpvSV1vY), [Dynatrace Office Hours: Configuring Grail and managing data access](https://www.youtube.com/watch?v=Pwh0hmqqjIk) — [search]
8. [Dynatrace University](https://www.dynatrace.com/dynatrace-university/) and [How pricing works](https://docs.dynatrace.com/docs/license/how-pricing-works) — [search]

### Gaps
- None of the DQL or Operator steps were executed against a live tenant from this sandbox, so the "expected results" are from documentation (obslab) or inferred.
- Official DPS rate-card numbers were not opened; treat all prices as indicative third-party figures.
- Trial specifics are unconfirmed: included capabilities, ingest limits, and whether a trial can be extended.
- The Associate certification's current price, format and whether it tests Classic or latest apps are unconfirmed from official sources.
- The new (non-classic) SLO app docs URL was not confirmed in search results; only the platform SLO API, the Hub page and the SLO Classic docs were.
- No well-known third-party educator (KodeKloud and similar) Dynatrace course turned up in search.
- Helm chart version 1.11.1 on `oci://public.ecr.aws/dynatrace/dynatrace-operator` was inferred from the GitHub tag (the skill's documented example pins 1.9.0). Confirm with `helm show chart oci://public.ecr.aws/dynatrace/dynatrace-operator --version 1.11.1`.
