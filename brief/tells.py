#!/usr/bin/env python3
"""Find templated, chatbot-like patterns in lesson prose (the human-writing skill's tells).
Usage: tells.py FILE [FILE ...]   (a part file content/pN.json, or a JSON list of lesson objects)
Prints each finding with its lesson id and field. Exit code 1 if anything is found."""
import collections
import json
import re
import sys

PATTERNS = {
    # formula endings and openers that repeat across lessons
    "analogy limit as a formula": r"\b(where (the |this )?(analogy|picture|comparison|metaphor) (breaks|fails|stops working)|where it breaks|the analogy breaks|the picture (breaks|fails)|the comparison (breaks|fails))\b",
    "'this trips people up'": r"\bthis trips (most |a lot of )?(people|learners|beginners) up\b",
    "run-up 'here is/here's the ...'": r"\bhere(?: i|')s (the|what|how|where|why) (part|thing|catch|trick|point|deal|key)\b",
    "'the key idea/point/insight'": r"\bthe key (idea|point|insight|takeaway|thing)\b",
    "'in other words'": r"\bin other words\b",
    "'think of it as/like'": r"\bthink of (it|this|them) (as|like)\b",
    "'it turns out'": r"\bit turns out\b",
    "'that's (it|all|the whole trick)'": r"\bthat(?:'s| is) (it|all there is|the whole (trick|idea|point))\.",
    "'not just X, but/it's Y'": r"\bnot (just|only|merely) [^.]{1,50}?(, but|; it|\. it)",
    "'the good news / the bad news'": r"\bthe (good|bad) news\b",
    "'simply put / in short / in a nutshell'": r"\b(simply put|in short|in a nutshell|put simply)\b",
    "'let's' run-up": r"\blet's (look|see|start|walk|dive|break|take a look)\b",
}
PROSE = ("goal", "analogy", "mistake", "real_world")


def lessons_of(path):
    d = json.load(open(path))
    return d if isinstance(d, list) else d.get("lessons", [])


def texts(L):
    for k in PROSE:
        yield k, L.get(k, "")
    for i, s in enumerate(L.get("sections", []), 1):
        yield f"sec{i}", s.get("body", "")
    for i, s in enumerate((L.get("worked") or {}).get("steps", []), 1):
        yield f"worked{i}", s.get("say", "")
    yield "explain", (L.get("explain_back") or {}).get("answer", "")
    for i, q in enumerate(L.get("interview", []), 1):
        yield f"interview{i}", q.get("a", "")
    yield "deeper", (L.get("deeper") or {}).get("body", "")


def opener(t, n):
    return " ".join(re.findall(r"[A-Za-z']+", t or "")[:n]).lower()


def main(paths):
    found = 0
    allL = [L for p in paths for L in lessons_of(p)]
    for L in allL:
        for field, t in texts(L):
            for name, pat in PATTERNS.items():
                for m in re.finditer(pat, t or "", re.I):
                    print(f"{L['id']} {field}: {name}: ...{t[max(0, m.start() - 40):m.end() + 30]}...")
                    found += 1
    # the same opening words in the same field across lessons
    for field, n in (("analogy", 3), ("real_world", 2), ("mistake", 3), ("goal", 6)):
        c = collections.Counter(opener(L.get(field, ""), n) for L in allL)
        for k, v in c.items():
            if k and v >= 3 and not (field == "goal" and k.startswith("by the end you can")):
                print(f"[{field}] {v} lessons open with '{k} ...': " + ", ".join(L["id"] for L in allL if opener(L.get(field, ""), n) == k))
                found += 1
    # fake company names used as a stock opener
    starts = [L["id"] for L in allL if re.match(r"^\s*At (PayLite|PayFlow|PayLoop|a (fake|made-up|fictional))", L.get("real_world", ""))]
    if len(starts) >= 2:
        print(f"[real_world] {len(starts)} lessons open with 'At <fake company>': {', '.join(starts)}")
        found += 1
    # section openers repeated inside one lesson
    for L in allL:
        c = collections.Counter(opener(s.get("body", ""), 2) for s in L.get("sections", []))
        for k, v in c.items():
            if k and v >= 3:
                print(f"{L['id']}: {v} sections open with '{k} ...'")
                found += 1
    print(f"{found} findings in {len(allL)} lessons")
    return found


if __name__ == "__main__":
    sys.exit(1 if main(sys.argv[1:]) else 0)
