#!/usr/bin/env python3
"""Prove that the human-writing pass changed only prose fields of content/p3.json.

Walks the original (p3.orig.json) and the edited file side by side. Every key must match.
Any changed string must sit at a prose path; everything else (ids, titles, terms[].term,
code, commands, worked code, URLs, refs, sources, answer indexes, options, questions,
diagrams) must be identical. Also checks that inline `code` spans and link URLs inside
changed prose did not appear or vanish unexpectedly. Prints every changed path.
"""
import json
import pathlib
import re
import sys

HERE = pathlib.Path(__file__).resolve().parent
A = json.loads((HERE / "p3.orig.json").read_text())
B = json.loads((HERE.parents[3] / "content/p3.json").read_text())

PROSE = [
    r"intro", r"recap\[\d+\]", r"flashcards\[\d+\]\.back", r"quiz\[\d+\]\.why", r"resources\[\d+\]\.why",
    r"lessons\[\d+\]\.(goal|analogy|mistake|real_world|diagram_caption)",
    r"lessons\[\d+\]\.terms\[\d+\]\.plain",
    r"lessons\[\d+\]\.sections\[\d+\]\.body",
    r"lessons\[\d+\]\.worked\.steps\[\d+\]\.say",
    r"lessons\[\d+\]\.task\.(steps|hints)\[\d+\]", r"lessons\[\d+\]\.task\.done_when",
    r"lessons\[\d+\]\.explain_back\.(prompt|answer)",
    r"lessons\[\d+\]\.recap\[\d+\]",
    r"lessons\[\d+\]\.(check\[\d+\]|guess)\.why",
    r"lessons\[\d+\]\.interview\[\d+\]\.a",
    r"lessons\[\d+\]\.deeper\.body",
]
PROSE = [re.compile("^" + p + "$") for p in PROSE]
problems, changed = [], []


def links(s):
    return sorted(re.findall(r"\]\((https?://[^)]+)\)", s))


def walk(a, b, path):
    if type(a) is not type(b):
        problems.append(f"type differs at {path}")
    elif isinstance(a, dict):
        if list(a) != list(b):
            problems.append(f"keys differ at {path}: {list(a)} vs {list(b)}")
        for k in a:
            if k in b:
                walk(a[k], b[k], f"{path}.{k}" if path else k)
    elif isinstance(a, list):
        if len(a) != len(b):
            problems.append(f"list length differs at {path}")
        for i, (x, y) in enumerate(zip(a, b)):
            walk(x, y, f"{path}[{i}]")
    elif a != b:
        if isinstance(a, str) and any(p.match(path) for p in PROSE):
            changed.append(path)
            if links(a) != links(b):
                problems.append(f"link URLs changed in {path}")
            gone = sorted(set(re.findall(r"`[^`]+`", a)) - set(re.findall(r"`[^`]+`", b)))
            new = sorted(set(re.findall(r"`[^`]+`", b)) - set(re.findall(r"`[^`]+`", a)))
            if gone or new:
                print(f"note {path}: inline code removed {gone} added {new}")
        else:
            problems.append(f"non-prose value changed at {path}: {str(a)[:60]!r} -> {str(b)[:60]!r}")


walk(A, B, "")
for p in changed:
    print("changed", p)
print(f"{len(changed)} prose fields changed")
for p in problems:
    print("PROBLEM", p)
print(f"{len(problems)} problems")
sys.exit(1 if problems else 0)
