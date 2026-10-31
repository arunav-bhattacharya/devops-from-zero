# DevOps, from zero

A hands-on DevOps course for an engineer who has never done cloud or DevOps work.
55 lessons in 15 parts, about 45 focused minutes each, at your own pace. You ship a real app,
`hello-devops`, from your laptop to a Kubernetes cluster, and build a Kotlin service with Gradle on the way.

| Part | Days | Topic |
|---|---|---|
| 0 | 1–2 | Start here: the DevOps map, set up your laptop |
| 1 | 3–7 | The Linux command line (shell, files, grep and regex, pipes, permissions, processes, systemd, SSH, scripts) |
| 2 | 8–10 | Networking and the cloud (IP, ports, DNS, HTTP, TLS, proxies, load balancers, regions, IAM, cost) |
| 3 | 11–16 | Docker (containers, images and layers, Dockerfiles, volumes and networks, Compose, production images) |
| 4 | 17–21 | CI/CD with GitHub Actions |
| 5 | 22–24 | Builds with Gradle |
| 6 | 25–29 | Infrastructure as Code with Terraform |
| 7 | 30–38 | Kubernetes (nine lessons, ending with a break-and-fix troubleshooting lab) |
| 8 | 39–40 | GitOps with Argo CD |
| 9 | 41–44 | Monitoring with Prometheus |
| 10 | 45–46 | Dashboards with Grafana |
| 11 | 47–49 | Logs and traces: ELK, EFK and OpenTelemetry |
| 12 | 50–51 | Dynatrace |
| 13 | 52–53 | DevSecOps |
| 14 | 54–55 | Platform engineering, AI in DevOps, and your capstone |

Every lesson has a warm-up guess, key words, sections with a diagram and an analogy, a worked example
with real output, the files and commands it uses, a hands-on task with hints, "explain it back",
a 3-question check, interview questions, an optional "go deeper", and links and videos for further learning.
The site adds spaced-repetition review of every term, a command cheat sheet, a glossary, a library of
every link and video, the finished lab files, and a plan that moves with your pace.

## What is in this repo

| Folder | What it holds |
|---|---|
| `content/` | The lessons, one JSON file per part (`p0.json` to `p14.json`); `content/v1/` is the first edition |
| `labs/` | The finished, checked lab projects: `hello-devops`, `hello-jvm`, `linux`, `terraform-practice` |
| `brief/` | The course plan (`index.json`), the writer brief and the validator |
| `research_notes/`, `reports/` | The research behind the second edition |
| `design/` | The "Freight Notation" design philosophy and the generator for the part plates |
| `site/` | The site source: `template.html`, `app.css`, `art.css`, `app.js`, `art/` and `build.py` |
| `public/index.html` | The built site as a complete web page (what Cloudflare serves) |
| `dist/index.html` | The same page as a fragment, for publishing as a claude.ai artifact |

## Build

```bash
pip install pygments
python3 site/build.py                          # writes public/index.html and dist/index.html
python3 brief/validate.py content/p3.json      # checks one part against the brief
python3 design/covers.py                       # regenerates the part plates (only after design changes)
```

## Deploy to Cloudflare

The site is one static file, so Cloudflare serves it from `public/` with no server code (`wrangler.jsonc`).

The simplest way: connect the repo once, and every push to `main` redeploys.

1. In the Cloudflare dashboard, open **Workers & Pages**, then **Create**, then **Import a repository**.
2. Pick `devops-from-zero` and keep the defaults: no build command, deploy command `npx wrangler deploy`.
3. Deploy. The site appears at `https://devops-from-zero.<your-subdomain>.workers.dev`.

Or deploy from your laptop:

```bash
npx wrangler login
npx wrangler deploy
```

Progress is saved in the browser. When the page is opened as a claude.ai artifact, progress also
syncs across devices and the "Ask the tutor" box appears.
