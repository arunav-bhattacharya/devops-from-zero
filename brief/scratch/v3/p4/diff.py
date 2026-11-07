#!/usr/bin/env python3
"""Prove that only prose fields changed between the original and the edited p4.json.
Usage: diff.py ORIGINAL EDITED
Fails if keys, list lengths, types or any non-prose leaf differ (ids, titles, terms[].term,
code, commands, worked code, URLs, refs, sources, options, answers, diagrams, minutes, ...)."""
import json
import sys

PROSE_LEAVES = {"intro", "why", "back", "goal", "plain", "body", "analogy", "mistake", "real_world",
                "say", "done_when", "prompt", "answer", "a"}
PROSE_LISTS = {"recap", "steps", "hints"}

problems, changed = [], []


def is_prose(path, value):
    last = path[-1]
    parent = path[-2] if len(path) >= 2 else None
    if isinstance(last, str):
        if last == "answer" and not isinstance(value, str):
            return False  # answer index of a multiple-choice item
        return last in PROSE_LEAVES
    return parent in PROSE_LISTS and isinstance(value, str)


def walk(a, b, path):
    if type(a) is not type(b):
        problems.append(f"type changed at {path}")
        return
    if isinstance(a, dict):
        if list(a) != list(b):
            problems.append(f"keys changed at {path}: {list(a)} vs {list(b)}")
            return
        for k in a:
            walk(a[k], b[k], path + (k,))
    elif isinstance(a, list):
        if len(a) != len(b):
            problems.append(f"list length changed at {path}")
            return
        for i, (x, y) in enumerate(zip(a, b)):
            walk(x, y, path + (i,))
    elif a != b:
        if is_prose(path, a):
            changed.append(path)
        else:
            problems.append(f"NON-PROSE leaf changed at {path}")


orig, new = (json.load(open(p)) for p in sys.argv[1:3])
walk(orig, new, ())


def label(path):
    out = []
    node = new
    for k in path:
        if isinstance(node, dict) and "id" in node and isinstance(k, str) and node is not new:
            pass
        node = node[k]
    # readable label with lesson id
    if path[0] == "lessons":
        return new["lessons"][path[1]]["id"] + "." + ".".join(str(x) for x in path[2:])
    return "part." + ".".join(str(x) for x in path)


print(f"{len(changed)} prose fields changed:")
for p in changed:
    print("  " + label(p))
for p in problems:
    print("PROBLEM " + p)
print("OK: only prose changed" if not problems else f"{len(problems)} problems")
sys.exit(1 if problems else 0)
