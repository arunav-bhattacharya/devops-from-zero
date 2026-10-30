# Course brief: "DevOps, from zero" second edition (writer instructions)

You are writing part of the SECOND EDITION of a DevOps course for one learner: 55 lessons in 15 parts. The learner read the first edition and found it rushed. This edition takes its time: every lesson builds real intuition for its topic, defines every idea before using it, and shows enough examples that someone who has never seen a tool can start from here alone.

Read this whole file first. Then read:
- `/home/user/devops-from-zero/brief/index.json`: every part and lesson with the exact scope of each. Stay inside your lessons' scope; other writers cover the rest (a one-line pointer like "Day 37 covers Helm" is fine). Day numbers changed from the first edition: always use the NEW numbers from index.json.
- `/home/user/devops-from-zero/research_notes/DevOps course topics and resources/`: research notes per topic (verified facts, concepts in teaching order, misconceptions, exercises, curated links and videos), and `reports/DevOps course topics and resources.md` when it exists. Use them.
- The first edition: `/home/user/devops-from-zero/content/v1/pN.json` with its index `/home/user/devops-from-zero/brief/index-v1.json`. A lesson's `from` field in index.json lists FIRST-EDITION ids (old numbering) to build on. Keep what was good and tested there (worked examples with real output, diagrams, questions, lab steps), fix anything the research shows is wrong, and expand.
- The lab repos: `/home/user/devops-from-zero/labs/hello-devops/` (tested) and the lab folders you own (see your task).

Write your part as JSON to `/home/user/devops-from-zero/content/pN.json` (N = part number, no padding) with a Python script in `/home/user/devops-from-zero/brief/scratch/v2/pN/`. Then run `python3 /home/user/devops-from-zero/brief/validate.py /home/user/devops-from-zero/content/pN.json` and fix every ERROR and every WARN you reasonably can.

## The learner

- An experienced software engineer (backend, Kotlin and JVM, some Python). Knows programming and basic git. Has NEVER done cloud, Linux administration, networking, containers, CI/CD, infrastructure as code or Kubernetes. Treat all of those as brand new and define every term.
- Uses a Mac with Apple Silicon. Give Mac commands first. Add a short Windows (WSL2) or Linux note only where it differs.
- Has 30 to 45 focused minutes a day and is happy for the course to take as long as it needs. Wants to be hands-on, to build intuition, and to remember what he learned. Uses Kotlin, Gradle and the JVM at work.
- Asked for very simple English: "easily digestible", "explain from scratch".

## Facts verified on 2026-10-30 (use these; verify anything else)

- Latest versions: Kubernetes v1.37.2; kubectl 1.37; kind v0.33.0; Helm v4.3.1 (Helm 4 is current); Terraform 1.17.1; OpenTofu 1.13.5; Docker Engine 29.9, Docker Compose v5.6; Argo CD v3.5.6; Gateway API v1.7.0; Envoy Gateway v1.9.3; Traefik v3.7; Prometheus 3.15; Grafana 13.3; OpenTelemetry Collector 0.164; cosign v3.1.4; syft 1.55; trivy 0.76; Kyverno 1.19; Flux 2.10; Backstage 1.56; gh CLI 2.103; k9s 0.51; terraform-provider-aws 6.71; kreuzwerker/docker provider 4.6.0.
- GitHub Actions major versions: actions/checkout@v7, actions/setup-python@v7, actions/upload-artifact@v7, docker/setup-buildx-action@v4, docker/login-action@v4, docker/metadata-action@v6, docker/build-push-action@v7, hashicorp/setup-terraform@v4, aws-actions/configure-aws-credentials@v6, aquasecurity/trivy-action@v0.36.0.
- Python packages: flask 3.1, gunicorn 26, redis 8, prometheus-client 0.26, pytest 9, ruff 0.17. Base image: python:3.14-slim. Redis image: redis:8-alpine.
- Do not write exact versions in prose unless they matter. Where a learner installs something, prefer "latest" install commands from official docs, and say "check the current docs" once.
- Anything that can go stale (prices, free tier rules, install commands, deprecations, CRD fields) must be checked against official docs with WebFetch or WebSearch in this task. Never from memory. If you cannot verify, say less.

## The lab (one project, all course long)

- The learner's repo: `hello-devops` on their GitHub account, cloned at `~/code/hello-devops`. Created on Day 2.
- The app: `app.py` (Flask). Endpoints: `/` returns JSON `{message, version, host, visits}`; `/healthz` (liveness); `/readyz` (readiness, 503 if Redis is set but down); `/metrics` (Prometheus, counter `hello_requests_total`). Settings from env vars: `APP_VERSION` (default "dev"), `GREETING` (default "Hello, DevOps!"), `REDIS_HOST` (empty means count in memory), `PORT` (default 8000 for `python app.py`). In containers it runs with gunicorn on port 8000.
- Port convention: the app listens on 8000 in its container. Compose maps 8000:8000. Terraform local maps 8080. kind maps NodePort 30080 to localhost:8081.
- Image names: local `hello-devops:1.0.0`; registry `ghcr.io/<your-github-user>/hello-devops`.
- Files (read them): `app.py`, `test_app.py`, `requirements.txt`, `requirements-dev.txt`, `Dockerfile`, `.dockerignore`, `compose.yaml`, `.github/workflows/ci.yml`, `.github/workflows/release.yml`, `infra/local/*.tf`, `k8s/*.yaml` (namespace `hello`), `kind-config.yaml`.
- New lab folders in the second edition (each owned by one writer, named in its task): `labs/linux/` (sample app.log, access.log and a JSON log for Part 1 exercises), `labs/hello-jvm/` (a small Kotlin multi-project Gradle build, Part 5), `labs/hello-devops/observability/` (Compose stack: Prometheus, node_exporter, Alertmanager, Grafana with provisioning; Parts 9 and 10), `labs/hello-devops/logging/` (Elasticsearch, Kibana, Fluent Bit; Part 11), `labs/hello-devops/tracing/` (OpenTelemetry Collector and Jaeger; Part 11), `labs/hello-devops/dynatrace/` (Part 12), `labs/hello-devops/k8s-broken/` (Day 38 break-and-fix). Extra host ports: Prometheus 9090, Grafana 3000, Alertmanager 9093, Elasticsearch 9200, Kibana 5601, Jaeger UI 16686, OTLP 4317/4318.
- Never edit lab files owned by another writer; if you find a bug there, report it.
- Tools in this sandbox for testing: docker (daemon running; for builds that pip install, add `--network host`), terraform (providers kreuzwerker/docker 4.6.0 and hashicorp/aws 6.71.0 are mirrored locally; the registry is blocked, so pin to those), kubectl, kubeconform (`kubeconform -strict -summary`), helm 4, kind (cannot start clusters here because of a kernel limit, so validate manifests with kubeconform and `helm lint`/`helm template`). The network blocks some hosts; Docker Hub and GitHub release downloads work. Test every runnable code block you can. Use unique container names and free ports when you test (other writers share this machine), and clean up after yourself.

## How a lesson teaches (learning science, applied)

Every lesson follows this shape, in this order on the page:

1. Guess first (`guess`): one multiple-choice question asked BEFORE reading. It targets a common misconception so the reveal teaches. Its `why` explains the answer in 1 to 2 sentences.
2. Words you'll meet (`terms`): 5 to 8 terms, one plain line each (no jargon inside the definition). These also become spaced-repetition cards, so make each one a clean, self-contained fact.
3. The explanation (`sections`): 5 to 7 sections. Intuition first, then mechanics. One idea per section. Define each term in the text the first time too. Say plainly when something is hard ("this trips most people up").
4. Analogy (`analogy`): one everyday analogy for the core idea, and one sentence on where it breaks.
5. Diagram (`diagram`): one simple inline SVG that shows the mechanism (rules below).
6. Worked example (`worked`): 4 to 8 steps; solve one concrete example step by step, narrating WHY each step happens, with commands and their real output where it helps. It must differ from the hands-on task.
7. Files (`code`): the complete files this lesson creates or changes (Dockerfile, YAML, HCL, scripts). Each with a `run` command.
8. Commands (`commands`): 6 to 16 commands this lesson uses, each with a short plain explanation. These feed the cheat sheet page.
9. Common mistake (`mistake`) and In real teams (`real_world`: how this shows up at work, 2 to 3 sentences; you may use a FAKE payments product as the example, never a real employer).
10. Hands-on (`task`): the learner does a similar but different thing on their own laptop. Steps say WHAT to do, not the full answer. `hints` (1 to 3) narrow the space without giving it away. `done_when` is one checkable line ("you are done when `curl localhost:8000` shows visits counting up").
11. Explain it back (`explain_back`): a prompt asking the learner to explain the idea in their own words (3 to 4 sentences), plus a model answer.
12. Recap (`recap`, 4 to 6 bullets) and Check (`check`, exactly 3 questions that apply the idea to a NEW case, not recall of wording).
13. Interview corner (`interview`): 2 or 3 common interview questions on this lesson's topic with short, strong answers (3 to 5 sentences each).
14. Go deeper (`deeper`): an optional 10 to 15 minute extra (more depth, an edge case, how it works at scale). Plus `sources`: 1 to 4 links from official docs or the original source.

The core (1 to 12) fits 40 to 50 minutes. Set `minutes` to an honest estimate (40 to 50; Day 2 may be 60). A learner may split a lesson over two sittings; that is fine.

Part extras: `intro` (2 to 4 sentences), `recap` (6 to 10 bullets), `resources` (6 to 12, see below), `flashcards` (10 to 20, active recall: a question on the front, a short answer on the back; Part 0 may have 8 to 10), and `quiz` (8 to 10 questions; Part 0 has 6). From Part 2 on, 2 of the quiz questions revisit EARLIER parts (interleaving); mark those with `"from": "Part N"` (N = the earlier part's number).

## Links, further reading and videos (the learner asked for this)

- Every lesson includes at least one credible video (`"kind": "watch"`) in a section's refs when the research notes list one for the topic, and at least one official docs link (`"kind": "docs"`).
- Every part has `resources`: 6 to 12 hand-picked items for going deeper on that part's topic (official docs, a book, a free course, the best videos, a talk), each `{"title", "url", "kind", "why"}` where `why` is one plain sentence on what the learner gets from it. Mix kinds.
- Links come from the research notes or from your own WebSearch results in this task. Many docs sites are blocked for WebFetch here; github.com and raw.githubusercontent.com work through curl and git, so you can confirm a doc page exists by finding its source file in the project's GitHub docs repo.

- Every section gets `refs`: 1 to 3 credible picks for further learning on that section's topic, each `{"title", "url", "kind": "read" | "watch" | "listen" | "docs"}`. Prefer official docs (docs.docker.com, kubernetes.io, developer.hashicorp.com, docs.github.com, argo-cd.readthedocs.io, prometheus.io, opentelemetry.io), the original post or paper, CNCF material, well-known educators (for example TechWorld with Nana, KodeKloud, Julia Evans' zines, Kelsey Hightower's talks, Google's SRE book). Mix kinds where good options exist.
- Only use URLs you have opened yourself with WebFetch in this task (or that are in this brief). Never invent or guess a URL. One confirmed link beats three guessed ones. Video links: only YouTube URLs you confirmed exist (WebSearch result pages count).
- When the text names a specific source, link it inline: [Google's SRE book](https://sre.google/sre-book/table-of-contents/).

## Simple English (checked)

- Short sentences: aim for an average under 15 words. Never more than 30 words in one sentence.
- Everyday words. Use a technical word only after explaining it, then use it consistently.
- No idioms or slang a non-native reader might miss.
- Second person ("you"). Conversational, like a kind senior engineer at a whiteboard: intuition first.
- Each section body: 1 to 3 short paragraphs and/or 3 to 7 bullets. Bullets are one line each (max about 20 words).
- LISTS: whenever text names three or more things, write a bulleted list; whenever it describes steps or an order, write a numbered list ("1. ", "2. "). A short lead-in sentence, then the list.
- Section text per lesson: 1,400 to 2,200 words. Day 2 (setup) may be shorter in prose and longer in steps. Depth means more examples, more 'why', and small runnable commands with their output, never padding.

## Voice: human, blog mode (the learner asked for this)

All prose must read as if a person wrote it. Apply the human-writing skill (`/root/.claude/skills/synced/5c806f8d-0769-4e35-ac24-a3ea18081c67_433d709e-8728-4258-b10c-98909f71fe68/human-writing/SKILL.md`) in blog mode: an experienced engineer writing a blog-style lesson for one friend. Direct, concrete, uneven rhythm that follows the thought, plain opinions where there is a real basis ("for one app on your laptop, port-forward is enough"). Cut staging lines, forced triads, one-line closers, "-ing" tails, "serves as", filler transitions and fake-deep sayings. Never invent anecdotes, numbers or sources to sound human.

## Human writing rules (checked by the validator)

- No em dashes or en dashes anywhere. Use a period, comma, colon or parentheses.
- No "not X, but Y" or "it's not just X, it's Y" framing.
- No run-ups: "let's dive in", "here's the thing", "let's break it down".
- No filler words: delve, tapestry, intricate, interplay, underscore, showcase, testament, pivotal, crucial, robust (non-technical), foster, leverage, landscape, seamless, transformative, game-changer, unlock, navigate (figurative), realm, embark, journey.
- No forced optimism, no "In conclusion", no dramatic one-line closers. No emojis. Sentence case headings.
- Bold (**x**) at most twice per lesson, only for a term being defined. No bold labels at the start of bullets.
- Accuracy first. Do not invent statistics, studies, quotes, prices or incidents.

## Commands and code rules

- Shell commands are for zsh/bash on a Mac. Prefix nothing (no `$ ` prompts) in `code` and `commands`. In `worked` steps you may show a command and then its output, in a "console" block with `$ ` before commands so the reader can tell input from output.
- Files are complete and runnable (no "..." placeholders). Comments in simple English. YAML and HCL formatted (terraform fmt style).
- Put code in `code`, `worked` or `commands`, never as fenced blocks in section bodies. Inline `code` in prose is fine.
- `lang` values: bash, console, dockerfile, yaml, hcl, python, json, text, ini.
- Safety: everything runs locally and free by default. Anything that can cost money (Day 15 cloud part) is clearly optional, says what it may cost, and ends with a destroy step.

## Diagrams (inline SVG)

Each lesson gets one simple diagram that shows the mechanism (flow, boxes, arrows, layers). Rules:

- `<svg viewBox="0 0 560 H" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="short description">` with H between 140 and 380. No width/height attributes. No `<defs>`, no `<style>`, no `style=""`, no colors written as attributes (no fill="#..." or stroke="#..."), no images, no foreignObject, no filters.
- Use ONLY these classes; the page supplies colors (and dark/light themes):
  - Shapes: `bx` (neutral card), `bxo` (orange), `bxt` (teal), `bxg` (gold), `bxp` (purple). Use `rx="10"` on rects.
  - Lines: `ln` (solid), `lnd` (dashed). Add `marker-end="url(#ar)"` for an arrow head.
  - Text: `t` (main label, font-size="13"), `ts` (small caption, font-size="11"), `tk` (label inside a colored box, font-size="13"). Text in a `bx` box uses `t`. Always set `font-size` and `text-anchor="middle"` for centered labels.
- Labels are short (1 to 3 words). Box width >= 8 x (characters in longest label) + 24. Keep 12px between elements and 8px from the edge. Nothing overlaps or leaves the viewBox.
- Prefer left-to-right or top-to-bottom flows with 3 to 7 boxes. Simple beats clever.

## JSON schema (exact)

```json
{
  "part": 2,
  "title": "Docker",
  "intro": "2 to 3 plain sentences: what this part gives you and why it comes now.",
  "lessons": [
    {
      "id": "d05",
      "title": "Containers: your first docker run",
      "minutes": 35,
      "goal": "One sentence starting 'By the end you can ...'",
      "guess": {"q": "...", "options": ["A", "B", "C", "D"], "answer": 1, "why": "1 to 2 sentences."},
      "terms": [{"term": "Container", "plain": "A running, isolated process made from an image."}],
      "sections": [{"h": "Sentence case heading", "body": "Markup text (see below).", "refs": [{"title": "...", "url": "https://...", "kind": "docs"}]}],
      "analogy": "2 to 4 sentences, plus one on where it breaks.",
      "diagram": "<svg ...>...</svg>",
      "diagram_caption": "One short line.",
      "worked": {"title": "Short name", "steps": [{"say": "What happens and why, 1 to 3 sentences.", "code": "optional, max ~14 lines", "lang": "console"}]},
      "code": [{"lang": "dockerfile", "title": "Dockerfile", "src": "...", "run": "docker build -t hello-devops:1.0.0 ."}],
      "commands": [{"cmd": "docker ps -a", "what": "List all containers, including stopped ones."}],
      "mistake": "The most common mistake and what to do instead. 2 to 3 sentences.",
      "real_world": "2 to 3 sentences on how teams use this at work.",
      "task": {"title": "...", "steps": ["step"], "hints": ["hint"], "done_when": "One line."},
      "explain_back": {"prompt": "Explain ... in 3 to 4 sentences. Mention ...", "answer": "3 to 5 plain sentences."},
      "recap": ["4 to 6 one-line bullets"],
      "check": [{"q": "...", "options": ["A", "B", "C", "D"], "answer": 2, "why": "One sentence."}],
      "interview": [{"q": "...", "a": "3 to 5 sentences."}],  // 2 or 3 items
      "deeper": {"minutes": 12, "body": "Markup text, 250 to 600 words."},
      "sources": [{"title": "...", "url": "https://..."}]
    }
  ],
  "recap": ["6 to 8 one-line bullets"],
  "flashcards": [{"front": "Question", "back": "Short answer"}],
  "resources": [{"title": "...", "url": "https://...", "kind": "watch", "why": "One plain sentence."}],
  "quiz": [{"q": "...", "options": ["A", "B", "C", "D"], "answer": 0, "why": "...", "from": "Part 1"}]
}
```

Field rules:
- `worked.steps`: 3 to 7 steps. `task.steps`: 4 to 10. `task.hints`: 1 to 3.
- `code` may be [] only when a lesson truly creates no files (Day 1). `commands` may be [] only on Day 1.
- Every multiple-choice item has exactly 4 options, and the right `answer` index varies (0 to 3) across the lesson and the part. Wrong options are plausible. Options are similar in length (the right one must not be the longest every time).
- `sources`: 1 to 4 real URLs. Never invent a URL.

### Markup inside body, analogy, mistake, real_world, deeper, explain_back answer, interview answers, task steps

Plain text with: a blank line between paragraphs; bullet lines start with "- "; numbered lines start with "1. "; `inline code`; **bold** (max twice per lesson); links as [text](https://url). No headings, tables or code fences.

## Before you finish

1. Run the validator and fix all errors.
2. Read one full lesson as a beginner would. Is every sentence simple, true and useful? Is every term defined before use? Cut anything that only restates.
3. Check every Day reference uses the new numbering and every link came from the research notes or your own search results.
4. Report back in under 150 words: file path, lessons, approximate words, lab files you added or changed, and anything you were unsure about.
