#!/usr/bin/env python3
"""Prove that only prose fields changed between two versions of a part file.
Usage: diffcheck.py ORIG.json NEW.json
Fails if keys, list lengths or any non-prose value differ, if a lesson outside d35..d38 changed,
or if a changed field lost or gained a URL. Lists inline-code differences per field for review."""
import json
import re
import sys

MINE = {"d35", "d36", "d37", "d38"}
LESSON_PROSE = [r"goal", r"guess\.why", r"terms\.\d+\.plain", r"sections\.\d+\.body", r"analogy", r"mistake",
                r"real_world", r"worked\.steps\.\d+\.say", r"task\.steps\.\d+", r"task\.hints\.\d+", r"task\.done_when",
                r"explain_back\.prompt", r"explain_back\.answer", r"recap\.\d+", r"check\.\d+\.why", r"interview\.\d+\.a",
                r"deeper\.body"]
PART_PROSE = [r"intro", r"recap\.\d+", r"flashcards\.\d+\.back", r"quiz\.\d+\.why", r"resources\.\d+\.why"]
URL = re.compile(r"https?://[^\s)\]]+")
CODE = re.compile(r"`[^`]+`")

problems, notes, changed = [], [], []


def walk(a, b, path):
    if type(a) is not type(b):
        problems.append(f"type differs at {path}")
        return
    if isinstance(a, dict):
        if list(a.keys()) != list(b.keys()):
            problems.append(f"keys differ at {path}: {list(a.keys())} vs {list(b.keys())}")
        for k in a:
            if k in b:
                walk(a[k], b[k], f"{path}.{k}" if path else k)
    elif isinstance(a, list):
        if len(a) != len(b):
            problems.append(f"list length differs at {path}: {len(a)} vs {len(b)}")
        for i, (x, y) in enumerate(zip(a, b)):
            walk(x, y, f"{path}.{i}")
    elif a != b:
        check_leaf(path, a, b)


def check_leaf(path, a, b):
    m = re.match(r"lessons\.(\d+)\.(.*)$", path)
    if m:
        lid = ORIG["lessons"][int(m.group(1))]["id"]
        rest = m.group(2)
        if lid not in MINE:
            problems.append(f"{lid} is not mine but changed at {rest}")
            return
        allowed = any(re.fullmatch(p, rest) for p in LESSON_PROSE)
        where = f"{lid}.{rest}"
    else:
        allowed = any(re.fullmatch(p, path) for p in PART_PROSE)
        where = f"part.{path}"
    if not allowed:
        problems.append(f"non-prose field changed: {where}")
        return
    changed.append(where)
    if sorted(URL.findall(a)) != sorted(URL.findall(b)):
        problems.append(f"URLs differ in {where}: {URL.findall(a)} vs {URL.findall(b)}")
    ca, cb = sorted(CODE.findall(a)), sorted(CODE.findall(b))
    if ca != cb:
        lost = [c for c in set(ca) if ca.count(c) > cb.count(c)]
        gained = [c for c in set(cb) if cb.count(c) > ca.count(c)]
        notes.append(f"inline code in {where}: lost {lost} gained {gained}")
    if a.count("**") != b.count("**"):
        notes.append(f"bold count changed in {where}")


ORIG = json.load(open(sys.argv[1]))
NEW = json.load(open(sys.argv[2]))
walk(ORIG, NEW, "")
print(f"{len(changed)} prose fields changed")
for c in changed:
    print("  changed:", c)
for n in notes:
    print("NOTE", n)
for p in problems:
    print("PROBLEM", p)
print("OK: only prose fields changed" if not problems else f"{len(problems)} problems")
sys.exit(1 if problems else 0)
