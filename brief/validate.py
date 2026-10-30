#!/usr/bin/env python3
"""Validate one part file against the course brief.
Usage: validate.py content/pN.json   (prints ERROR/WARN lines; exit 1 on any ERROR)"""
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
INDEX = json.loads((ROOT / "brief/index.json").read_text())

BANNED = ["delve", "tapestry", "intricate", "interplay", "underscore", "showcase", "testament", "pivotal",
          "crucial", "foster", "leverage", "landscape", "seamless", "transformative", "game-changer",
          "game changer", "unlock", "realm", "embark", "journey", "let's dive", "here's the thing",
          "let's break it down", "in conclusion", "in today's fast-paced",
          # more chatbot tells from the human-writing skill
          "serves as", "stands as", "it's worth noting", "it is worth noting", "moreover", "furthermore", "additionally",
          "crucially", "valuable", "enhance", "boasts", "key takeaway", "let that sink in", "honestly?", "real talk",
          "at its core", "the real question", "what really matters", "plays a key role", "plays a crucial role",
          "garner", "bolster", "vibrant", "meticulous", "align with", "evolving", "that's the real", "here's what"]
LANGS = {"bash", "console", "dockerfile", "yaml", "hcl", "python", "json", "text", "ini"}
KINDS = {"read", "watch", "listen", "docs"}
SVG_CLASSES = {"bx", "bxo", "bxt", "bxg", "bxp", "ln", "lnd", "t", "ts", "tk"}

errors, warns = [], []
err = lambda where, msg: errors.append(f"ERROR {where}: {msg}")
warn = lambda where, msg: warns.append(f"WARN  {where}: {msg}")


def words(s):
    return len(re.findall(r"[A-Za-z0-9'`]+", s or ""))


def strip_markup(s):
    s = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", s or "")
    return re.sub(r"`[^`]*`", "code", s)


def sentences(s):
    s = strip_markup(s)
    out = []
    for line in s.split("\n"):
        line = re.sub(r"^\s*(- |\d+\. )", "", line).strip()
        if line:
            out += [x for x in re.split(r"(?<=[.!?])\s+(?=[A-Z0-9])", line) if x.strip()]
    return out


def text_checks(where, s, prose=True):
    if not isinstance(s, str):
        return
    if "—" in s or "–" in s:
        err(where, "em/en dash found")
    low = s.lower()
    for b in BANNED:
        if re.search(r"\b" + re.escape(b) + r"\b", low):
            warn(where, f"banned word/phrase: {b!r}")
    if re.search(r"\bnot (just|only) [^.]{1,40}, but\b", low) or re.search(r"it's not just", low):
        warn(where, "'not X, but Y' framing")
    if "```" in s:
        err(where, "code fence inside markup text")
    if prose:
        for sent in sentences(s):
            n = words(sent)
            if n > 30:
                warn(where, f"sentence over 30 words ({n}): {sent[:70]}...")


def mcq(where, q, need_from=False):
    if not isinstance(q, dict):
        return err(where, "not an object")
    for k in ("q", "options", "answer", "why"):
        if k not in q:
            err(where, f"missing {k}")
    if len(q.get("options", [])) != 4:
        err(where, "needs exactly 4 options")
    if not isinstance(q.get("answer"), int) or not 0 <= q.get("answer", -1) <= 3:
        err(where, "answer must be 0..3")
    for k in ("q", "why"):
        text_checks(where + "." + k, q.get(k, ""))
    for o in q.get("options", []):
        text_checks(where + ".option", o, prose=False)
    opts = q.get("options", [])
    if len(opts) == 4 and isinstance(q.get("answer"), int) and 0 <= q["answer"] <= 3:
        lens = [len(o) for o in opts]
        if lens[q["answer"]] == max(lens) and max(lens) > 1.6 * sorted(lens)[1]:
            warn(where, "right option is much longer than the others")


def svg_checks(where, svg):
    if not svg:
        return err(where, "diagram missing")
    m = re.match(r'<svg viewBox="0 0 560 (\d+)" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="[^"]+">', svg)
    if not m:
        err(where, 'must start with <svg viewBox="0 0 560 H" xmlns=... role="img" aria-label="...">')
    elif not 140 <= int(m.group(1)) <= 380:
        err(where, "viewBox height must be 140..380")
    for bad in ("<defs", "<style", "style=", "<image", "foreignObject", "filter"):
        if bad in svg:
            err(where, f"forbidden in svg: {bad}")
    if re.search(r"<svg[^>]*\s(width|height)=", svg):
        err(where, "no width/height on the svg element")
    if re.search(r'(fill|stroke)="#', svg):
        err(where, "hard-coded color in svg")
    for cls in re.findall(r'class="([^"]+)"', svg):
        for c in cls.split():
            if c not in SVG_CLASSES:
                err(where, f"unknown svg class {c}")
    for t in re.findall(r"<text[^>]*>", svg):
        if "font-size" not in t:
            warn(where, "text without font-size")
    if not svg.rstrip().endswith("</svg>"):
        err(where, "svg not closed")


def refs_checks(where, refs, lo=1, hi=3):
    if not isinstance(refs, list) or not lo <= len(refs) <= hi:
        err(where, f"needs {lo}..{hi} refs")
        return
    for r in refs:
        if not str(r.get("url", "")).startswith("https://"):
            err(where, f"bad url {r.get('url')}")
        if "kind" in r and r["kind"] not in KINDS:
            err(where, f"bad kind {r.get('kind')}")
        if not r.get("title"):
            err(where, "ref without title")


def lesson(L, ref, part):
    lid = L.get("id", "?")
    w = lid
    if L.get("id") != ref["id"]:
        err(w, f"id should be {ref['id']}")
    if L.get("title") != ref["title"]:
        err(w, f"title should be {ref['title']!r}")
    need = ["minutes", "goal", "guess", "terms", "sections", "analogy", "diagram", "diagram_caption", "worked", "code",
            "commands", "mistake", "real_world", "task", "explain_back", "recap", "check", "interview", "deeper", "sources"]
    for k in need:
        if k not in L:
            err(w, f"missing {k}")
    mx = 60 if lid == "d02" else 50
    if not isinstance(L.get("minutes"), int) or not 30 <= L.get("minutes", 0) <= mx:
        err(w, f"minutes must be 30..{mx}")
    if not str(L.get("goal", "")).startswith("By the end you can"):
        warn(w, "goal should start with 'By the end you can'")
    if "guess" in L:
        mcq(w + ".guess", L["guess"])
    terms = L.get("terms", [])
    if not 5 <= len(terms) <= 8:
        err(w, "terms must be 5..8")
    for t in terms:
        if not t.get("term") or not t.get("plain"):
            err(w, "term needs term and plain")
        text_checks(w + ".term", t.get("plain", ""))
    secs = L.get("sections", [])
    if not 5 <= len(secs) <= 7:
        (warn if lid in ("d01", "d02") and 4 <= len(secs) <= 8 else err)(w, "sections must be 5..7")
    total = 0
    for i, s in enumerate(secs):
        sw = f"{w}.sec{i + 1}"
        if not s.get("h") or not s.get("body"):
            err(sw, "section needs h and body")
        if s.get("h") and s["h"][0].islower():
            warn(sw, "heading should start with a capital")
        text_checks(sw, s.get("body", ""))
        refs_checks(sw + ".refs", s.get("refs"))
        total += words(s.get("body", ""))
    lo, hi = 1400, 2200
    if lid == "d02":
        lo = 600
    if not lo <= total <= hi:
        warn(w, f"section text is {total} words (want {lo}..{hi})")
    for k in ("analogy", "mistake", "real_world"):
        text_checks(f"{w}.{k}", L.get(k, ""))
        if not L.get(k):
            err(w, f"{k} empty")
    svg_checks(w + ".diagram", L.get("diagram", ""))
    wk = L.get("worked") or {}
    if not 4 <= len(wk.get("steps", [])) <= 8:
        err(w, "worked needs 4..8 steps")
    for st in wk.get("steps", []):
        text_checks(w + ".worked", st.get("say", ""))
        if st.get("code") and st.get("lang") not in LANGS:
            err(w, f"worked step lang {st.get('lang')!r} not allowed")
    code = L.get("code", [])
    if not code and lid != "d01":
        err(w, "code is empty")
    for c in code:
        if c.get("lang") not in LANGS:
            err(w, f"code lang {c.get('lang')!r} not allowed")
        if not c.get("src") or not c.get("title"):
            err(w, "code needs title and src")
        if re.search(r"^\s*\.\.\.\s*$", c.get("src", ""), re.M):
            err(w, f"placeholder ... in {c.get('title')}")
    cmds = L.get("commands", [])
    if not (6 <= len(cmds) <= 16 or (lid == "d01" and len(cmds) <= 16)):
        err(w, "commands must be 6..16")
    for c in cmds:
        if not c.get("cmd") or not c.get("what"):
            err(w, "command needs cmd and what")
        if c.get("cmd", "").startswith("$ "):
            err(w, "no $ prompt in commands")
    t = L.get("task", {})
    if not 4 <= len(t.get("steps", [])) <= 10:
        err(w, "task needs 4..10 steps")
    if not 1 <= len(t.get("hints", [])) <= 3:
        err(w, "task needs 1..3 hints")
    if not t.get("done_when") or not t.get("title"):
        err(w, "task needs title and done_when")
    for s in t.get("steps", []) + t.get("hints", []):
        text_checks(w + ".task", s)
    eb = L.get("explain_back") or {}
    if not eb.get("prompt") or not eb.get("answer"):
        err(w, "explain_back needs prompt and answer")
    text_checks(w + ".explain_back", eb.get("answer", ""))
    if not 4 <= len(L.get("recap", [])) <= 6:
        err(w, "recap must be 4..6")
    for r in L.get("recap", []):
        text_checks(w + ".recap", r)
    chk = L.get("check", [])
    if len(chk) != 3:
        err(w, "check must have exactly 3 questions")
    for i, q in enumerate(chk):
        mcq(f"{w}.check{i + 1}", q)
    iv = L.get("interview", [])
    if not 2 <= len(iv) <= 3:
        err(w, "interview must have 2 or 3 items")
    for q in iv:
        if not q.get("q") or not q.get("a"):
            err(w, "interview item needs q and a")
        text_checks(w + ".interview", q.get("a", ""))
    d = L.get("deeper") or {}
    dw = words(d.get("body", ""))
    if not 250 <= dw <= 650:
        warn(w, f"deeper is {dw} words (want 250..600)")
    text_checks(w + ".deeper", d.get("body", ""))
    refs_checks(w + ".sources", L.get("sources"), 1, 4)
    kinds = {r.get("kind") for s_ in secs for r in s_.get("refs", [])}
    if "watch" not in kinds:
        warn(w, "no video ('watch') in any section refs")
    if "docs" not in kinds:
        warn(w, "no official docs ('docs') in any section refs")
    blob = json.dumps(L, ensure_ascii=False)
    if blob.count("**") // 2 > 2:
        warn(w, f"bold used {blob.count('**') // 2} times (max 2)")
    answers = [q.get("answer") for q in chk] + [L.get("guess", {}).get("answer")]
    if len(set(answers)) == 1:
        warn(w, "all answers in this lesson use the same index")
    allsent = [x for s in secs for x in sentences(s.get("body", ""))]
    if allsent:
        avg = sum(words(x) for x in allsent) / len(allsent)
        if avg > 16:
            warn(w, f"average sentence length {avg:.1f} words (aim under 15)")
    return total


def main(path):
    P = json.loads(pathlib.Path(path).read_text())
    part = P.get("part")
    ref = next((x for x in INDEX if x["part"] == part), None)
    if ref is None:
        err("part", f"unknown part {part}")
        return
    if P.get("title") != ref["title"]:
        err("part", f"title should be {ref['title']!r}")
    for k in ("intro", "lessons", "recap", "flashcards", "quiz"):
        if k not in P:
            err("part", f"missing {k}")
    text_checks("part.intro", P.get("intro", ""))
    ids = [L.get("id") for L in P.get("lessons", [])]
    if ids != [x["id"] for x in ref["lessons"]]:
        err("part", f"lesson ids {ids} should be {[x['id'] for x in ref['lessons']]}")
    total = 0
    for L, R in zip(P.get("lessons", []), ref["lessons"]):
        total += lesson(L, R, part) or 0
    if not 6 <= len(P.get("recap", [])) <= 10:
        err("part", "recap must be 6..10")
    res = P.get("resources", [])
    if not 6 <= len(res) <= 12:
        err("part", "resources must be 6..12")
    for r in res:
        if not str(r.get("url", "")).startswith("https://") or not r.get("title") or not r.get("why") or r.get("kind") not in KINDS:
            err("part", f"bad resource {r.get('title')!r}: needs title, https url, kind and why")
        text_checks("part.resource", r.get("why", ""))
    lo, hi = (8, 12) if part == 0 else (10, 20)
    if not lo <= len(P.get("flashcards", [])) <= hi:
        err("part", f"flashcards must be {lo}..{hi}")
    for f in P.get("flashcards", []):
        if not f.get("front") or not f.get("back"):
            err("part", "flashcard needs front and back")
        text_checks("part.flashcard", f.get("back", ""))
    quiz = P.get("quiz", [])
    if not ((part == 0 and len(quiz) == 6) or (part > 0 and 8 <= len(quiz) <= 10)):
        err("part", "quiz must have 8..10 questions (Part 0: 6)")
    for i, q in enumerate(quiz):
        mcq(f"part.quiz{i + 1}", q)
    froms = [q for q in quiz if q.get("from")]
    if part >= 2 and len(froms) != 2:
        err("part", "2 quiz questions must revisit earlier parts with 'from'")
    for q in froms:
        m = re.match(r"Part (\d+)$", q["from"])
        if not m or int(m.group(1)) >= part:
            err("part", f"bad from {q['from']!r}")
    dist = [q.get("answer") for q in quiz]
    if dist and max(dist.count(i) for i in range(4)) > len(dist) // 2:
        warn("part", f"quiz answer indexes are lopsided: {dist}")
    print(f"{path}: {len(ids)} lessons, ~{total} words of section text")


if __name__ == "__main__":
    main(sys.argv[1])
    for x in errors + warns:
        print(x)
    print(f"{len(errors)} errors, {len(warns)} warnings")
    sys.exit(1 if errors else 0)
