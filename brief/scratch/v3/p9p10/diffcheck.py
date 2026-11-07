#!/usr/bin/env python3
"""Prove that only prose fields changed between the backup and the current file.
Usage: diffcheck.py ORIG.json NEW.json"""
import json
import re
import sys

LESSON_PROSE = {
    ("goal",), ("terms", "*", "plain"), ("sections", "*", "body"), ("analogy",), ("mistake",), ("real_world",),
    ("worked", "steps", "*", "say"), ("task", "steps", "*"), ("task", "hints", "*"), ("task", "done_when"),
    ("explain_back", "prompt"), ("explain_back", "answer"), ("recap", "*"), ("check", "*", "why"),
    ("guess", "why"), ("interview", "*", "a"), ("deeper", "body"),
}
PART_PROSE = {("intro",), ("recap", "*"), ("flashcards", "*", "back"), ("quiz", "*", "why"), ("resources", "*", "why")}
URL = re.compile(r"\]\((https?://[^)]+)\)")
CODE = re.compile(r"`[^`]*`")


def norm(path):
    return tuple("*" if isinstance(p, int) else p for p in path)


def walk(a, b, path, out):
    if type(a) is not type(b):
        out.append(("TYPE", path))
    elif isinstance(a, dict):
        if a.keys() != b.keys():
            out.append(("KEYS", path))
        for k in a:
            if k in b:
                walk(a[k], b[k], path + (k,), out)
    elif isinstance(a, list):
        if len(a) != len(b):
            out.append(("LEN", path))
        for i, (x, y) in enumerate(zip(a, b)):
            walk(x, y, path + (i,), out)
    elif a != b:
        out.append(("VALUE", path))


def main(orig, new):
    A, B = json.load(open(orig)), json.load(open(new))
    diffs = []
    walk(A, B, (), diffs)
    bad, changed = [], 0
    for kind, path in diffs:
        if kind != "VALUE":
            bad.append(f"{kind} at {path}")
            continue
        n = norm(path)
        ok = n in PART_PROSE or (n[0] == "lessons" and n[2:] in LESSON_PROSE)
        if not ok:
            bad.append(f"non-prose change at {path}")
            continue
        changed += 1
        old, cur = A, B
        for p in path:
            old, cur = old[p], cur[p]
        if URL.findall(old) != URL.findall(cur):
            bad.append(f"link URLs changed at {path}")
        lost = set(CODE.findall(old)) - set(CODE.findall(cur))
        if lost:
            bad.append(f"inline code dropped at {path}: {sorted(lost)}")
    print(f"{new}: {changed} prose fields changed")
    for line in bad:
        print("PROBLEM", line)
    if not bad:
        print("OK: same keys and list lengths; ids, titles, terms, code, commands, URLs, answers, options, diagrams unchanged")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(*sys.argv[1:3]))
