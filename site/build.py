#!/usr/bin/env python3
"""Build the course site into one HTML file.

Reads brief/index.json, content/pN.json (parts not written yet show as "being written")
and the reference lab files, turns the light markup into HTML, highlights code,
and inlines everything into dist/index.html.

Usage: python3 site/build.py            (needs: pip install pygments)
"""
import datetime
import hashlib
import html
import json
import pathlib
import re

from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import get_lexer_by_name

ROOT = pathlib.Path(__file__).resolve().parent.parent
SITE = ROOT / "site"
OUT = ROOT / "dist/index.html"
WEB = ROOT / "public"

FMT = HtmlFormatter(nowrap=True)
ALIAS = {"sh": "bash", "shell": "bash", "zsh": "bash", "console": "console", "yml": "yaml", "tf": "hcl", "kts": "kotlin",
         "hcl": "terraform", "dockerfile": "docker", "text": "text", "ini": "ini"}


def esc(s):
    return html.escape(s or "", quote=False)


def inline(s):
    """Inline markup: `code`, **bold**, [text](url)."""
    parts = re.split(r"(`[^`]+`)", s or "")
    out = []
    for p in parts:
        if len(p) > 2 and p.startswith("`") and p.endswith("`"):
            out.append(f"<code>{esc(p[1:-1])}</code>")
            continue
        p = esc(p)
        p = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", p)
        p = re.sub(r"\[([^\]]+)\]\((https?://[^)\s]+)\)",
                   lambda m: f'<a href="{html.escape(m.group(2))}" target="_blank" rel="noopener">{m.group(1)}</a>', p)
        out.append(p)
    return "".join(out)


def md(s):
    """Block markup: paragraphs, '- ' bullets, '1. ' numbered lists."""
    blocks, cur = [], []
    for line in (s or "").replace("\r", "").split("\n"):
        if not line.strip():
            if cur:
                blocks.append(cur)
                cur = []
        else:
            cur.append(line.rstrip())
    if cur:
        blocks.append(cur)
    out = []
    for b in blocks:
        # a block may start with a lead-in line followed by list items
        i, lead = 0, []
        while i < len(b) and not re.match(r"^\s*(- |\d+\. )", b[i]):
            lead.append(b[i])
            i += 1
        if lead:
            out.append("<p>" + inline(" ".join(x.strip() for x in lead)) + "</p>")
        items, kind = [], None
        for line in b[i:]:
            m = re.match(r"^\s*(- |(\d+)\. )(.*)$", line)
            if m:
                k = "ol" if m.group(2) else "ul"
                if kind and k != kind:
                    out.append(f"<{kind}>" + "".join(items) + f"</{kind}>")
                    items = []
                kind = k
                items.append("<li>" + inline(m.group(3)) + "</li>")
            elif items:  # continuation line of the last item
                items[-1] = items[-1][:-5] + " " + inline(line.strip()) + "</li>"
        if items:
            out.append(f"<{kind}>" + "".join(items) + f"</{kind}>")
    return "".join(out)


def plain(s):
    s = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", s or "")
    return re.sub(r"[`*]", "", s)


def hl(lang, src):
    name = ALIAS.get(lang or "text", lang or "text")
    try:
        lexer = get_lexer_by_name(name)
    except Exception:
        lexer = get_lexer_by_name("text")
    return highlight((src or "").rstrip("\n"), lexer, FMT)


def mcq(q):
    return {"q": inline(q["q"]), "options": [inline(o) for o in q["options"]], "answer": q["answer"],
            "why": inline(q.get("why", "")), "from": q.get("from", "")}


def slug(s):
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")[:40]


def hid(s):
    return hashlib.sha1(s.encode()).hexdigest()[:8]


def lesson(L, R, part, k):
    lid = R["id"]
    text = [L.get("goal", "")] + [s["h"] + ". " + plain(s["body"]) for s in L["sections"]]
    return {
        "id": lid, "k": k, "part": part, "day": int(lid[1:]), "title": R["title"], "minutes": L.get("minutes", 35),
        "goal": inline(L.get("goal", "")),
        "guess": mcq(L["guess"]) if L.get("guess") else None,
        "terms": [{"term": t["term"], "plain": inline(t["plain"]), "id": f"t:{lid}:{slug(t['term'])}"} for t in L.get("terms", [])],
        "sections": [{"h": s["h"], "html": md(s["body"]),
                      "refs": [{"title": inline(r["title"]), "url": r["url"], "kind": r.get("kind", "read")} for r in s.get("refs", [])]}
                     for s in L["sections"]],
        "analogy": md(L.get("analogy", "")), "diagram": L.get("diagram", ""), "caption": inline(L.get("diagram_caption", "")),
        "worked": {"title": inline(L["worked"].get("title", "")),
                   "steps": [{"say": md(s.get("say", "")), "code": hl(s.get("lang"), s["code"]) if s.get("code") else "",
                              "lang": s.get("lang", "")} for s in L["worked"].get("steps", [])]} if L.get("worked") else None,
        "code": [{"title": c.get("title", ""), "lang": c.get("lang", "text"), "html": hl(c.get("lang"), c["src"]),
                  "run": c.get("run", "")} for c in L.get("code", [])],
        "commands": [{"cmd": c["cmd"], "html": hl("bash", c["cmd"]), "what": inline(c["what"])} for c in L.get("commands", [])],
        "mistake": md(L.get("mistake", "")), "realWorld": md(L.get("real_world", "")),
        "task": {"title": inline(L["task"]["title"]), "steps": [inline(x) for x in L["task"]["steps"]],
                 "hints": [inline(x) for x in L["task"].get("hints", [])], "doneWhen": inline(L["task"].get("done_when", ""))},
        "explain": {"prompt": inline(L["explain_back"]["prompt"]), "answer": md(L["explain_back"]["answer"]),
                    "raw": plain(L["explain_back"]["prompt"]) + " || " + plain(L["explain_back"]["answer"])} if L.get("explain_back") else None,
        "recap": [inline(x) for x in L.get("recap", [])],
        "check": [mcq(q) for q in L.get("check", [])],
        "interview": [{"q": inline(x["q"]), "a": md(x["a"])} for x in L.get("interview", [])],
        "deeper": {"minutes": L["deeper"].get("minutes", 12), "html": md(L["deeper"]["body"])} if L.get("deeper") else None,
        "sources": [{"title": inline(s["title"]), "url": s["url"]} for s in L.get("sources", [])],
        "text": "\n".join(text)[:9000],
    }


FIRST = ["app.py", "test_app.py", "requirements.txt", "requirements-dev.txt", ".gitignore", "Dockerfile", ".dockerignore", "compose.yaml"]
# (project, path prefix, day the file is built or finished), first match wins
DAYS = [
    ("hello-devops", "app.py", 2), ("hello-devops", "test_app.py", 2), ("hello-devops", "requirements", 2), ("hello-devops", ".gitignore", 2),
    ("hello-devops", "Dockerfile", 16), ("hello-devops", ".dockerignore", 13), ("hello-devops", "docker/", 13), ("hello-devops", "compose.yaml", 15),
    ("hello-devops", ".github/pull_request_template", 17), ("hello-devops", ".github/workflows/ci", 19), ("hello-devops", ".github/actions", 20),
    ("hello-devops", ".github/dependabot", 21), ("hello-devops", ".github/workflows/release", 21), ("hello-devops", ".github/workflows/terraform", 29),
    ("hello-devops", "infra/aws", 29), ("hello-devops", "infra/modules", 28), ("hello-devops", "infra/", 27),
    ("hello-devops", "kind-config", 30), ("hello-devops", "k8s/examples", 31), ("hello-devops", "k8s/hpa", 35), ("hello-devops", "k8s/gateway", 36),
    ("hello-devops", "k8s/", 30), ("hello-devops", "chart/", 37), ("hello-devops", "overlays/", 37), ("hello-devops", "k8s-broken/", 38),
    ("hello-devops", "argocd/", 39), ("hello-devops", "gitops/", 40),
    ("hello-devops", "observability/grafana", 45), ("hello-devops", "observability/loki", 46), ("hello-devops", "observability/compose.loki", 46),
    ("hello-devops", "observability/", 42), ("hello-devops", "logging/", 47), ("hello-devops", "tracing/", 49), ("hello-devops", "dynatrace/", 51),
    ("hello-devops", "policy/ai-agent", 54), ("hello-devops", "policy/", 53), ("hello-devops", "security/capstone", 55), ("hello-devops", "security/agent", 54), ("hello-devops", "security/", 53),
    ("linux", "", 3), ("hello-jvm", "Dockerfile", 24), ("hello-jvm", ".dockerignore", 24), ("hello-jvm", ".github/", 24),
    ("hello-jvm", "gradle/libs", 23), ("hello-jvm", "build-logic", 23), ("hello-jvm", "greeting", 23), ("hello-jvm", "", 22),
    ("terraform-practice", "", 26),
]
LANGS = {".py": "python", ".yaml": "yaml", ".yml": "yaml", ".tf": "hcl", ".tpl": "text", ".txt": "text", ".json": "json", ".md": "text",
         ".kts": "kotlin", ".kt": "kotlin", ".toml": "ini", ".properties": "ini", ".sh": "bash", ".conf": "ini", ".alloy": "text",
         ".dql": "text", ".log": "text", ".jsonl": "json"}
SKIP_DIRS = {".terraform", "__pycache__", ".pytest_cache", ".ruff_cache", ".venv", "charts", ".gradle", "build", ".kotlin", "node_modules"}
PROJECT_ORDER = ["hello-devops", "linux", "hello-jvm", "terraform-practice"]


def labs():
    out = []
    projects = sorted((d for d in (ROOT / "labs").iterdir() if d.is_dir()), key=lambda d: (PROJECT_ORDER.index(d.name) if d.name in PROJECT_ORDER else 9, d.name))
    for proj in projects:
        for x in sorted(proj.rglob("*")):
            if not x.is_file() or SKIP_DIRS & set(x.relative_to(proj).parts) or x.name.endswith((".tfstate", ".lock.hcl", ".pyc", ".tgz", ".zip", ".backup", ".jar")) \
                    or x.name in ("gradlew.bat",) or x.stat().st_size > 200_000:
                continue
            rel = str(x.relative_to(proj))
            if proj.name == "hello-devops" and rel == "README.md":
                continue
            try:
                raw = x.read_text()
            except UnicodeDecodeError:
                continue
            day = next((d for pr, pre, d in DAYS if pr == proj.name and rel.startswith(pre)), 55)
            lang = "dockerfile" if x.name.startswith("Dockerfile") else ("bash" if x.name == "gradlew" else LANGS.get(x.suffix, "text"))
            out.append({"path": f"{proj.name}/{rel}", "lang": lang, "day": day, "html": hl(lang, raw), "lines": raw.count("\n") + 1,
                        "proj": proj.name, "rank": FIRST.index(rel) if rel in FIRST else 99})
    return sorted(out, key=lambda f: (f["day"], PROJECT_ORDER.index(f["proj"]) if f["proj"] in PROJECT_ORDER else 9, f["rank"], f["path"]))


def main():
    index = json.loads((ROOT / "brief/index.json").read_text())
    course = {"parts": [], "order": [], "lessons": {}, "labs": labs(), "built": datetime.date.today().isoformat()}
    k = 0
    for P in index:
        path = ROOT / f"content/p{P['part']}.json"
        data = json.loads(path.read_text()) if path.exists() else None
        byid = {L["id"]: L for L in (data or {}).get("lessons", [])}
        ids = []
        for R in P["lessons"]:
            ids.append(R["id"])
            course["order"].append(R["id"])
            if R["id"] in byid:
                course["lessons"][R["id"]] = lesson(byid[R["id"]], R, P["part"], k)
            else:
                course["lessons"][R["id"]] = {"id": R["id"], "k": k, "part": P["part"], "day": int(R["id"][1:]), "title": R["title"],
                                              "minutes": 35, "pending": True, "scope": R["scope"]}
            k += 1
        d = data or {}
        course["parts"].append({
            "part": P["part"], "slug": P["slug"], "title": P["title"], "tool": P["tool"], "ready": bool(data),
            "intro": inline(d.get("intro", "")), "recap": [inline(x) for x in d.get("recap", [])],
            "flashcards": [{"front": inline(f["front"]), "back": inline(f["back"]), "id": f"f:p{P['part']}:{hid(f['front'])}"}
                           for f in d.get("flashcards", [])],
            "quiz": [mcq(q) for q in d.get("quiz", [])], "lessons": ids,
            "resources": [{"title": inline(r["title"]), "url": r["url"], "kind": r.get("kind", "read"), "why": inline(r.get("why", ""))}
                          for r in d.get("resources", [])],
            "art": (SITE / f"art/p{P['part']}.svg").read_text() if (SITE / f"art/p{P['part']}.svg").exists() else "",
        })
    data = json.dumps(course, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    page = (SITE / "template.html").read_text()
    page = page.replace("/*CSS*/", (SITE / "app.css").read_text() + (SITE / "art.css").read_text())
    page = page.replace("/*JS*/", (SITE / "app.js").read_text())
    page = page.replace("{{DATA}}", data)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(page)  # fragment: claude.ai wraps it in its own document
    # full document for Cloudflare (or any static host)
    WEB.mkdir(parents=True, exist_ok=True)
    (WEB / "index.html").write_text('<!doctype html>\n<html lang="en"><head><meta charset="utf-8">'
                                    '<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">'
                                    '<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 24 24%22%3E%3Crect x=%223%22 y=%2214%22 width=%225%22 height=%227%22 fill=%22%230a6a7e%22/%3E%3Crect x=%2210%22 y=%228%22 width=%225%22 height=%2213%22 fill=%22%23c84410%22/%3E%3Crect x=%2217%22 y=%222%22 width=%225%22 height=%2219%22 fill=%22%23e8ad00%22/%3E%3C/svg%3E">'
                                    '</head><body>\n' + page + '\n</body></html>\n')
    ready = sum(1 for L in course["lessons"].values() if not L.get("pending"))
    print(f"{OUT}  {OUT.stat().st_size // 1024} KB  {ready}/{len(course['order'])} lessons ready  {len(course['labs'])} lab files")


if __name__ == "__main__":
    main()
