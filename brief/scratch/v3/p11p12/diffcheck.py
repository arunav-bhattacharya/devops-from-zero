#!/usr/bin/env python3
"""Prove that only prose fields changed between an original part file and the edited one.
Usage: diffcheck.py ORIG.json NEW.json
Checks: identical key structure and list lengths everywhere; every non-prose leaf identical
(ids, titles, terms[].term, code, commands, URLs, refs, sources, answers, options, diagrams, ...);
and inline code spans and link URLs inside prose unchanged, except for listed exceptions.
Prints every changed prose field."""
import json
import re
import sys

# Prose leaves, as path patterns ('*' = any list index). Everything else must be identical.
PROSE = [
    ("intro",), ("recap", "*"), ("flashcards", "*", "back"), ("quiz", "*", "why"), ("resources", "*", "why"),
    ("lessons", "*", "goal"), ("lessons", "*", "guess", "why"), ("lessons", "*", "terms", "*", "plain"),
    ("lessons", "*", "sections", "*", "body"), ("lessons", "*", "analogy"), ("lessons", "*", "mistake"),
    ("lessons", "*", "real_world"), ("lessons", "*", "worked", "steps", "*", "say"),
    ("lessons", "*", "task", "steps", "*"), ("lessons", "*", "task", "hints", "*"),
    ("lessons", "*", "task", "done_when"), ("lessons", "*", "explain_back", "prompt"),
    ("lessons", "*", "explain_back", "answer"), ("lessons", "*", "recap", "*"),
    ("lessons", "*", "check", "*", "why"), ("lessons", "*", "interview", "*", "a"),
    ("lessons", "*", "deeper", "body"),
]
# Inline-code changes in prose that are deliberate factual fixes (reported).
ALLOWED_CODE_CHANGES = {("`otlphttp`", "`otlp_http`")}


def is_prose(path):
    for pat in PROSE:
        if len(pat) == len(path) and all(p == "*" and isinstance(k, int) or p == k for p, k in zip(pat, path)):
            return True
    return False


def walk(a, b, path, problems, changed):
    if type(a) is not type(b):
        problems.append(f"type differs at {path}")
        return
    if isinstance(a, dict):
        if list(a.keys()) != list(b.keys()):
            problems.append(f"keys differ at {path}: {list(a)} vs {list(b)}")
        for k in a:
            if k in b:
                walk(a[k], b[k], path + (k,), problems, changed)
    elif isinstance(a, list):
        if len(a) != len(b):
            problems.append(f"list length differs at {path}")
        for i, (x, y) in enumerate(zip(a, b)):
            walk(x, y, path + (i,), problems, changed)
    elif a != b:
        if is_prose(path):
            changed.append((path, a, b))
        else:
            problems.append(f"NON-PROSE leaf changed at {path}")


def spans(s):
    code = re.findall(r"`[^`]*`", s)
    urls = re.findall(r"\]\((https?://[^)]+)\)", s)
    return code, urls


def main(orig, new):
    A, B = json.load(open(orig)), json.load(open(new))
    problems, changed = [], []
    walk(A, B, (), problems, changed)
    for path, a, b in changed:
        ca, ua = spans(a)
        cb, ub = spans(b)
        if ua != ub:
            problems.append(f"link URLs changed in {path}")
        if sorted(ca) != sorted(cb):  # same spans in a new order (reordered sentences) is fine
            sa, sb = sorted(ca), sorted(cb)
            removed = [x for x in ca if x not in cb]
            added = [x for x in cb if x not in ca]
            pairs = set(zip(removed, added))
            if len(removed) != len(added) or not pairs <= ALLOWED_CODE_CHANGES:
                if sa != sb:
                    problems.append(f"inline code changed in {path}: -{removed} +{added}")
            else:
                print(f"note: allowed inline-code fix in {path}: {sorted(pairs)}")
    lid = lambda p: (A["lessons"][p[1]]["id"] + "." + ".".join(map(str, p[2:]))) if p[0] == "lessons" else ".".join(map(str, p))
    print(f"{orig} -> {new}: {len(changed)} prose fields changed")
    for path, a, b in changed:
        print("  changed:", lid(path))
    for p in problems:
        print("PROBLEM:", p)
    print("OK: only prose changed" if not problems else f"{len(problems)} problems")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1], sys.argv[2]))
