# DevOps, from zero

A 23-lesson, hands-on DevOps course for an engineer who has never done cloud or DevOps work.
About 35 focused minutes a day for about 3 weeks. You ship one small app, `hello-devops`,
from your laptop to a Kubernetes cluster.

| Part | Days | Topic |
|---|---|---|
| 0 | 1–2 | Start here: the DevOps map, set up your laptop |
| 1 | 3–4 | Linux and networking basics |
| 2 | 5–8 | Docker |
| 3 | 9–12 | CI/CD with GitHub Actions |
| 4 | 13–15 | Infrastructure as Code with Terraform |
| 5 | 16–19 | Kubernetes |
| 6 | 20–23 | Modern DevOps: GitOps, observability, DevSecOps, platform engineering, AI in DevOps |

Every lesson has: a warm-up guess, key words, short sections with a diagram, an analogy,
a worked example with real output, the files and commands it uses, a hands-on task with hints,
"explain it back", a 3-question check, interview questions and an optional "go deeper".
The site adds spaced-repetition review of every term, a command cheat sheet, a glossary,
the finished lab files, and a plan that moves with your pace.

## What is in this repo

| Folder | What it holds |
|---|---|
| `content/` | The lessons, one JSON file per part (`p0.json` to `p6.json`) |
| `brief/` | The course plan (`index.json`), the writer brief and the validator |
| `labs/hello-devops/` | The finished, tested lab repo the lessons build |
| `site/` | The site source: `template.html`, `app.css`, `app.js` and `build.py` |
| `dist/index.html` | The built site: one HTML file, no server needed |

## Build

```bash
pip install pygments
python3 site/build.py                         # writes dist/index.html
python3 brief/validate.py content/p2.json     # checks one part against the brief
```

Open `dist/index.html` in a browser, or deploy it.

## Deploy to Cloudflare (like ai-engineer-from-zero)

```bash
npx wrangler deploy
```

`wrangler.jsonc` serves `dist/` as static assets. Progress is saved in the browser. When the page
is opened as a claude.ai artifact, progress also syncs across devices and the "Ask the tutor" box appears.
