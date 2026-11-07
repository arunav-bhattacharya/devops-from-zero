#!/usr/bin/env python3
"""Prove that only prose fields changed between the original and the edited part file.

Usage: diffcheck.py ORIG NEW
Fails (exit 1) when keys, list lengths or any non-prose value differ.
Also reports, per changed prose field, inline code spans, URLs and numbers that were lost or added,
so dropped commands or invented numbers are visible."""
import json
import re
import sys

PART_PROSE = {("intro",), ("recap", "*"), ("flashcards", "*", "back"), ("quiz", "*", "why"), ("resources", "*", "why")}
LESSON_PROSE = {("goal",), ("terms", "*", "plain"), ("sections", "*", "body"), ("analogy",), ("mistake",),
                ("real_world",), ("worked", "steps", "*", "say"), ("task", "steps", "*"), ("task", "hints", "*"),
                ("task", "done_when"), ("explain_back", "prompt"), ("explain_back", "answer"), ("recap", "*"),
                ("check", "*", "why"), ("guess", "why"), ("interview", "*", "a"), ("deeper", "body")}


def norm(path):
    return tuple("*" if isinstance(p, int) else p for p in path)


def is_prose(path):
    if path[:1] == ("lessons",):
        return norm(path[2:]) in LESSON_PROSE
    return norm(path) in PART_PROSE


problems, changed = [], []


def walk(a, b, path=()):
    if type(a) is not type(b):
        problems.append(f"type differs at {path}")
        return
    if isinstance(a, dict):
        if list(a.keys()) != list(b.keys()):
            problems.append(f"keys differ at {path}: {list(a)} vs {list(b)}")
        for k in a:
            if k in b:
                walk(a[k], b[k], path + (k,))
    elif isinstance(a, list):
        if len(a) != len(b):
            problems.append(f"list length differs at {path}")
        for i, (x, y) in enumerate(zip(a, b)):
            walk(x, y, path + (i,))
    elif a != b:
        if is_prose(path) and isinstance(a, str):
            changed.append((path, a, b))
        else:
            problems.append(f"NON-PROSE value changed at {path}")


def spans(s):
    return re.findall(r"`[^`]+`", s)


def urls(s):
    return re.findall(r"https?://[^\s)\]]+", s)


def nums(s):
    s = re.sub(r"`[^`]+`", "", s)
    return re.findall(r"\b\d[\d.,]*\b", s)


def multiset_diff(x, y):
    from collections import Counter
    cx, cy = Counter(x), Counter(y)
    return sorted((cx - cy).elements()), sorted((cy - cx).elements())


def main(orig, new):
    a, b = json.load(open(orig)), json.load(open(new))
    walk(a, b)
    for path, old, new_ in changed:
        notes = []
        for name, fn in (("code", spans), ("url", urls), ("number", nums)):
            lost, added = multiset_diff(fn(old), fn(new_))
            if lost:
                notes.append(f"{name} lost {lost}")
            if added:
                notes.append(f"{name} added {added}")
        if notes:
            print(f"  note {path}: " + "; ".join(notes))
    print(f"{len(changed)} prose fields changed, {len(problems)} problems")
    for p in problems:
        print("PROBLEM", p)
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1], sys.argv[2]))
