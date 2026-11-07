#!/usr/bin/env python3
"""Prove that only prose fields changed between the saved originals and content/.

Checks: same keys and list lengths everywhere; every changed string sits on an
allowed prose path; inside changed prose, inline `code` spans, link URLs and
**bold** terms are the same as before. Prints each changed field and any change
in the digits it contains (for a manual fact check)."""
import collections
import json
import re
import sys

ROOT = "/home/user/devops-from-zero"
HERE = ROOT + "/brief/scratch/v3/p0p2"

PROSE = [
    r"intro", r"recap\[\d+\]", r"flashcards\[\d+\]\.back", r"quiz\[\d+\]\.why", r"resources\[\d+\]\.why",
    r"lessons\[\d+\]\.(goal|analogy|mistake|real_world|recap\[\d+\])",
    r"lessons\[\d+\]\.terms\[\d+\]\.plain",
    r"lessons\[\d+\]\.sections\[\d+\]\.body",
    r"lessons\[\d+\]\.worked\.steps\[\d+\]\.say",
    r"lessons\[\d+\]\.task\.(steps\[\d+\]|hints\[\d+\]|done_when)",
    r"lessons\[\d+\]\.explain_back\.(prompt|answer)",
    r"lessons\[\d+\]\.(check\[\d+\]|guess)\.why",
    r"lessons\[\d+\]\.interview\[\d+\]\.a",
    r"lessons\[\d+\]\.deeper\.body",
]
PROSE_RE = re.compile(r"^(" + "|".join(PROSE) + r")$")


def walk(a, b, path, out, problems):
    if type(a) is not type(b):
        problems.append(f"{path}: type changed")
    elif isinstance(a, dict):
        if list(a) != list(b):
            problems.append(f"{path}: keys changed {list(a)} -> {list(b)}")
        for k in a:
            if k in b:
                walk(a[k], b[k], f"{path}.{k}" if path else k, out, problems)
    elif isinstance(a, list):
        if len(a) != len(b):
            problems.append(f"{path}: list length {len(a)} -> {len(b)}")
        for i, (x, y) in enumerate(zip(a, b)):
            walk(x, y, f"{path}[{i}]", out, problems)
    elif a != b:
        if not isinstance(a, str) or not PROSE_RE.match(path):
            problems.append(f"{path}: non-prose value changed")
        else:
            out.append((path, a, b))


def spans(s):
    return {
        "code": collections.Counter(re.findall(r"`[^`]*`", s)),
        "urls": collections.Counter(re.findall(r"\]\((https?://[^)]+)\)", s)),
        "bold": collections.Counter(re.findall(r"\*\*[^*]+\*\*", s)),
    }


def main():
    bad = 0
    for name in ("p0", "p2"):
        a = json.load(open(f"{HERE}/{name}.orig.json"))
        b = json.load(open(f"{ROOT}/content/{name}.json"))
        changed, problems = [], []
        walk(a, b, "", changed, problems)
        for path, old, new in changed:
            so, sn = spans(old), spans(new)
            for kind in so:
                if so[kind] != sn[kind]:
                    problems.append(f"{path}: {kind} differ: {dict(so[kind] - sn[kind])} -> {dict(sn[kind] - so[kind])}")
            do, dn = collections.Counter(re.findall(r"\d+", old)), collections.Counter(re.findall(r"\d+", new))
            note = "" if do == dn else f"   digits: -{dict(do - dn)} +{dict(dn - do)}"
            print(f"{name} changed {path}{note}")
        for p in problems:
            print(f"{name} PROBLEM {p}")
        bad += len(problems)
        print(f"{name}: {len(changed)} prose fields changed, {len(problems)} problems")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
