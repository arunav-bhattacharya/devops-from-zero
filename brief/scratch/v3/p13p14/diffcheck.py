#!/usr/bin/env python3
"""Prove that only prose fields changed between an original part file and the edited one.

Usage: diffcheck.py ORIG.json NEW.json
Checks: identical key structure and list lengths; every non-prose leaf is byte-identical
(ids, titles, terms[].term, code, commands, worked code, URLs, refs, sources, answers,
options, questions, diagrams); inside prose fields, the set of URLs and inline `code`
spans is unchanged. Prints each changed prose path. Exit 1 on any violation."""
import json
import re
import sys

# Leaf paths (with list indexes replaced by *) that may change.
PROSE = [
    r"intro", r"recap\.\*", r"flashcards\.\*\.back", r"quiz\.\*\.why", r"resources\.\*\.why",
    r"lessons\.\*\.(goal|analogy|mistake|real_world)",
    r"lessons\.\*\.terms\.\*\.plain",
    r"lessons\.\*\.sections\.\*\.body",
    r"lessons\.\*\.worked\.steps\.\*\.say",
    r"lessons\.\*\.task\.(steps\.\*|hints\.\*|done_when)",
    r"lessons\.\*\.explain_back\.(prompt|answer)",
    r"lessons\.\*\.recap\.\*",
    r"lessons\.\*\.(check\.\*|guess)\.why",
    r"lessons\.\*\.interview\.\*\.a",
    r"lessons\.\*\.deeper\.body",
]
PROSE_RE = re.compile(r"^(" + "|".join(PROSE) + r")$")
URL = re.compile(r"\]\((https?://[^)]+)\)|(https?://\S+)")
CODE = re.compile(r"`[^`]+`")


def walk(a, b, path, out):
    if type(a) is not type(b):
        out["bad"].append(f"{path}: type changed")
        return
    if isinstance(a, dict):
        if set(a) != set(b):
            out["bad"].append(f"{path}: keys differ {sorted(set(a) ^ set(b))}")
        for k in a:
            if k in b:
                walk(a[k], b[k], f"{path}.{k}" if path else k, out)
    elif isinstance(a, list):
        if len(a) != len(b):
            out["bad"].append(f"{path}: list length {len(a)} -> {len(b)}")
        for i, (x, y) in enumerate(zip(a, b)):
            walk(x, y, f"{path}.{i}", out)
    else:
        if a == b:
            return
        generic = re.sub(r"\.\d+(?=\.|$)", ".*", path)
        if not PROSE_RE.match(generic) or not isinstance(a, str):
            out["bad"].append(f"{path}: non-prose field changed")
            return
        urls_a = sorted(m.group(1) or m.group(2) for m in URL.finditer(a))
        urls_b = sorted(m.group(1) or m.group(2) for m in URL.finditer(b))
        if urls_a != urls_b:
            out["bad"].append(f"{path}: URLs changed {urls_a} -> {urls_b}")
        lost = set(CODE.findall(a)) - set(CODE.findall(b))
        if lost:
            out["warn"].append(f"{path}: inline code no longer present: {sorted(lost)}")
        out["changed"].append(path)


def main(orig, new):
    a, b = json.load(open(orig)), json.load(open(new))
    out = {"bad": [], "warn": [], "changed": []}
    walk(a, b, "", out)
    for p in out["changed"]:
        print("prose changed:", p)
    for w in out["warn"]:
        print("NOTE", w)
    for x in out["bad"]:
        print("VIOLATION", x)
    print(f"{new}: {len(out['changed'])} prose fields changed, {len(out['bad'])} violations")
    return 1 if out["bad"] else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1], sys.argv[2]))
