#!/usr/bin/env python3
"""Prove that only prose fields changed between the backup and the edited p6.json.
Checks: identical key structure and list lengths everywhere; every changed leaf is an allowed prose field;
code, commands, URLs, answer indexes, options, ids, titles, terms and diagrams are byte-identical;
every link URL inside a changed prose field is kept."""
import json
import re
import sys

ORIG = "/home/user/devops-from-zero/brief/scratch/v3/p6/p6.orig.json"
NEW = "/home/user/devops-from-zero/content/p6.json"

# Allowed prose leaves, as path patterns (ints shown as #).
ALLOWED = [
    r"intro", r"recap/#", r"flashcards/#/back", r"quiz/#/why", r"resources/#/why",
    r"lessons/#/goal", r"lessons/#/guess/why", r"lessons/#/terms/#/plain", r"lessons/#/sections/#/body",
    r"lessons/#/analogy", r"lessons/#/diagram_caption", r"lessons/#/mistake", r"lessons/#/real_world",
    r"lessons/#/worked/steps/#/say", r"lessons/#/task/steps/#", r"lessons/#/task/hints/#", r"lessons/#/task/done_when",
    r"lessons/#/explain_back/prompt", r"lessons/#/explain_back/answer", r"lessons/#/recap/#",
    r"lessons/#/check/#/why", r"lessons/#/interview/#/a", r"lessons/#/deeper/body",
]
ALLOWED_RE = [re.compile("^" + a.replace("#", r"\d+") + "$") for a in ALLOWED]
LINK = re.compile(r"\]\((https?://[^)]+)\)")

problems, changed = [], []


def walk(a, b, path):
    p = "/".join(map(str, path))
    if type(a) is not type(b):
        problems.append(f"type changed at {p}")
        return
    if isinstance(a, dict):
        if list(a.keys()) != list(b.keys()):
            problems.append(f"keys changed at {p}: {list(a)} vs {list(b)}")
            return
        for k in a:
            walk(a[k], b[k], path + [k])
    elif isinstance(a, list):
        if len(a) != len(b):
            problems.append(f"list length changed at {p}: {len(a)} vs {len(b)}")
            return
        for i, (x, y) in enumerate(zip(a, b)):
            walk(x, y, path + [i])
    else:
        if a != b:
            if not any(r.match(p) for r in ALLOWED_RE):
                problems.append(f"NON-PROSE leaf changed at {p}")
            else:
                changed.append(p)
                if sorted(LINK.findall(a)) != sorted(LINK.findall(b)):
                    problems.append(f"link URLs changed at {p}")


A = json.load(open(ORIG))
B = json.load(open(NEW))
walk(A, B, [])

# Explicit spot checks of protected content.
for la, lb in zip(A["lessons"], B["lessons"]):
    for k in ("id", "title", "minutes", "diagram", "code", "commands", "sources"):
        if la[k] != lb[k]:
            problems.append(f"{la['id']}: {k} changed")
    if [t["term"] for t in la["terms"]] != [t["term"] for t in lb["terms"]]:
        problems.append(f"{la['id']}: term names changed")
    for x, y in zip(la["worked"]["steps"], lb["worked"]["steps"]):
        if x.get("code") != y.get("code") or x.get("lang") != y.get("lang"):
            problems.append(f"{la['id']}: worked code changed")
    for qa, qb in zip([la["guess"]] + la["check"], [lb["guess"]] + lb["check"]):
        if (qa["q"], qa["options"], qa["answer"]) != (qb["q"], qb["options"], qb["answer"]):
            problems.append(f"{la['id']}: question/options/answer changed")
    for sa, sb in zip(la["sections"], lb["sections"]):
        if sa["h"] != sb["h"] or sa["refs"] != sb["refs"]:
            problems.append(f"{la['id']}: section heading or refs changed")
for qa, qb in zip(A["quiz"], B["quiz"]):
    if (qa["q"], qa["options"], qa["answer"], qa.get("from")) != (qb["q"], qb["options"], qb["answer"], qb.get("from")):
        problems.append("part quiz question/options/answer changed")
for ra, rb in zip(A["resources"], B["resources"]):
    if (ra["title"], ra["url"], ra["kind"]) != (rb["title"], rb["url"], rb["kind"]):
        problems.append("resource title/url/kind changed")
for fa, fb in zip(A["flashcards"], B["flashcards"]):
    if fa["front"] != fb["front"]:
        problems.append("flashcard front changed")

print(f"{len(changed)} prose fields changed")
for c in changed:
    print("  changed:", c)
for p in problems:
    print("PROBLEM:", p)
print("OK: only prose fields changed" if not problems else f"{len(problems)} problems")
sys.exit(1 if problems else 0)
