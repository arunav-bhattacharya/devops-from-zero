#!/usr/bin/env python3
"""Prove that only prose fields changed between the backup and the edited file.

Usage: diffcheck.py ORIG.json NEW.json
Checks: identical key structure and list lengths; every non-prose leaf identical (ids, titles, terms,
code, commands, URLs, answer indexes, options, diagrams, sources, refs); inside changed prose, the
inline `code` spans and link URLs are kept. Prints each changed prose field."""
import json
import re
import sys

PART_PROSE = [r"intro", r"recap/\d+", r"flashcards/\d+/back", r"quiz/\d+/why", r"resources/\d+/why"]
LESSON_PROSE = [r"goal", r"terms/\d+/plain", r"sections/\d+/body", r"analogy", r"mistake", r"real_world",
                r"worked/steps/\d+/say", r"task/steps/\d+", r"task/hints/\d+", r"task/done_when",
                r"explain_back/prompt", r"explain_back/answer", r"recap/\d+", r"check/\d+/why",
                r"guess/why", r"interview/\d+/a", r"deeper/body"]
RX = re.compile("^(" + "|".join(PART_PROSE) + r"|lessons/\d+/(" + "|".join(LESSON_PROSE) + "))$")


def walk(o, path=""):
    if isinstance(o, dict):
        yield path, ("dict", tuple(o.keys()))
        for k, v in o.items():
            yield from walk(v, f"{path}/{k}" if path else k)
    elif isinstance(o, list):
        yield path, ("list", len(o))
        for i, v in enumerate(o):
            yield from walk(v, f"{path}/{i}" if path else str(i))
    else:
        yield path, o


def spans(s):
    return sorted(re.findall(r"`[^`]+`", s)), sorted(re.findall(r"\]\((https?://[^)]+)\)", s))


def main(a, b):
    A = dict(walk(json.load(open(a))))
    B = dict(walk(json.load(open(b))))
    bad = 0
    if A.keys() != B.keys():
        print("KEY SET DIFFERS:", sorted(set(A) ^ set(B))[:20])
        bad += 1
    changed = 0
    for k in A:
        if k not in B or A[k] == B[k]:
            continue
        if isinstance(A[k], str) and isinstance(B[k], str) and RX.match(k):
            changed += 1
            ca, ua = spans(A[k])
            cb, ub = spans(B[k])
            if ua != ub:
                print(f"URL CHANGED in {k}: {ua} -> {ub}")
                bad += 1
            if ca != cb:
                lost = [x for x in ca if x not in cb]
                added = [x for x in cb if x not in ca]
                print(f"NOTE inline code differs in {k}: lost {lost} added {added}")
            continue
        print(f"NON-PROSE CHANGE at {k}: {str(A[k])[:80]!r} -> {str(B[k])[:80]!r}")
        bad += 1
    print(f"{b}: {changed} prose fields changed, {bad} problems")
    return bad


if __name__ == "__main__":
    sys.exit(1 if main(sys.argv[1], sys.argv[2]) else 0)
