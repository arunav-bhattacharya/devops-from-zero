# DevOps, from zero

A hands-on DevOps course for an engineer who has never done cloud or DevOps work.
68 lessons in 20 parts, about 45 focused minutes each, at your own pace. You ship a real app,
`hello-devops`, from your laptop to a Kubernetes cluster, and build a Kotlin service with Gradle on the way.

| Section | Part | Days | Topic |
|---|---|---|---|
| Foundations | 0 | 1–2 | Start here: the DevOps map, set up your laptop |
|  | 1 | 3–7 | The Linux command line (shell, files, grep and regex, pipes, permissions, processes, systemd, SSH, scripts) |
|  | 2 | 8–9 | Version control with Git (snapshots, undo, branches, merge, rebase, remotes) |
|  | 3 | 10–14 | Networking and the cloud (IP, ports, DNS, HTTP, TLS, load balancers, cloud basics), then hands-on AWS (IAM, CLI, S3, EC2, VPC, CloudWatch) |
|  | 4 | 15–16 | Python scripts for automation (files, JSON, CLI tools, APIs, boto3, tests) |
| Build and ship | 5 | 17–22 | Docker (containers, images and layers, Dockerfiles, volumes and networks, Compose, production images) |
|  | 6 | 23–27 | CI/CD with GitHub Actions |
|  | 7 | 28–30 | Builds with Gradle |
| Infrastructure as code | 8 | 31–35 | Infrastructure as Code with Terraform |
|  | 9 | 36–37 | Configuration management with Ansible |
| Run on Kubernetes | 10 | 38–46 | Kubernetes (nine lessons, ending with a break-and-fix troubleshooting lab) |
|  | 11 | 47–48 | GitOps with Argo CD |
| Observability | 12 | 49–52 | Monitoring with Prometheus |
|  | 13 | 53–54 | Dashboards with Grafana |
|  | 14 | 55–57 | Logs and traces: ELK, EFK and OpenTelemetry |
| Operate at scale | 15 | 58–60 | Service mesh: Envoy, Istio, Linkerd and Cilium |
|  | 16 | 61–62 | Dynatrace |
| Security, AI and the capstone | 17 | 63–64 | DevSecOps |
|  | 18 | 65–66 | AI in DevOps (assistants, agents, MCP, guardrails) |
|  | 19 | 67–68 | Platform engineering and your capstone |

Every lesson has a warm-up guess, key words, sections with a diagram and an analogy, a worked example
with real output, the files and commands it uses, a hands-on task with hints, "explain it back",
a 3-question check, interview questions, an optional "go deeper", and links and videos for further learning.
The site adds spaced-repetition review of every term, a command cheat sheet, a glossary, a library of
every link and video, the finished lab files, and a plan that moves with your pace.

## What is in this repo

| Folder | What it holds |
|---|---|
| `content/` | The lessons, one JSON file per part (`p0.json` to `p19.json`); `content/v1/` is the first edition |
| `labs/` | The finished, checked lab projects: `hello-devops`, `hello-jvm`, `linux`, `git`, `aws`, `python-ops`, `ansible`, `terraform-practice` |
| `brief/` | The course plan (`index.json`), the writer brief and the validator |
| `research_notes/`, `reports/` | The research behind the second edition (the third edition's new parts were researched by their writers) |
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
Anyone with the link can read every lesson, and progress is saved in each visitor's browser.
Steps are in [DEPLOY.md](DEPLOY.md).

The same page also works as a claude.ai artifact (`dist/index.html`), where progress syncs across devices
and the "Ask the tutor" box appears.
