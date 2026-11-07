#!/usr/bin/env python3
"""Build a temporary p7 copy with the five edited lessons swapped in, then prove
that only prose fields changed: same keys, same code, commands, URLs, answer
indexes, options, diagrams, ids, titles and terms. Also compares the inline
`code` spans and link targets inside each prose field and lists any change."""
import json
import pathlib
import re
import sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[3]
orig = json.loads((HERE / "p7.orig.json").read_text())
edited = json.loads((HERE / "lessons.json").read_text())
by_id = {L["id"]: L for L in edited}

# temporary merged copy for validate.py and tells.py
merged = json.loads(json.dumps(orig))
merged["lessons"] = [by_id.get(L["id"], L) for L in merged["lessons"]]
(HERE / "p7.merged.json").write_text(json.dumps(merged, ensure_ascii=False, indent=1) + "\n")

# prose paths that may change (lesson level only)
PROSE = re.compile(
    r"^(goal|guess\.why|terms\[\d+\]\.plain|sections\[\d+\]\.body|analogy|mistake|real_world|"
    r"worked\.steps\[\d+\]\.say|task\.(steps|hints)\[\d+\]|task\.done_when|explain_back\.(prompt|answer)|"
    r"recap\[\d+\]|check\[\d+\]\.why|interview\[\d+\]\.a|deeper\.body)$"
)


def flat(o, path=""):
    if isinstance(o, dict):
        yield path, ("dict", tuple(sorted(o)))
        for k, v in o.items():
            yield from flat(v, f"{path}.{k}" if path else k)
    elif isinstance(o, list):
        yield path, ("list", len(o))
        for i, v in enumerate(o):
            yield from flat(v, f"{path}[{i}]")
    else:
        yield path, o


def spans(t):
    return sorted(re.findall(r"`[^`]*`", t)), sorted(re.findall(r"\]\(([^)]+)\)", t))


problems, changed, span_notes = [], 0, []
O = {L["id"]: L for L in orig["lessons"]}
assert [L["id"] for L in edited] == ["d30", "d31", "d32", "d33", "d34"], "wrong lesson set"
for lid, E in by_id.items():
    a, b = dict(flat(O[lid])), dict(flat(E))
    if a.keys() != b.keys():
        problems.append(f"{lid}: key structure differs: {set(a) ^ set(b)}")
        continue
    for p in a:
        if a[p] == b[p]:
            continue
        if not PROSE.match(p):
            problems.append(f"{lid} {p}: non-prose field changed")
            continue
        changed += 1
        if spans(a[p]) != spans(b[p]):
            span_notes.append(f"{lid} {p}: inline code/link spans differ\n   before {spans(a[p])}\n   after  {spans(b[p])}")
# part level untouched in merged copy
for k in orig:
    if k != "lessons" and orig[k] != merged[k]:
        problems.append(f"part field {k} changed")
for L in merged["lessons"]:
    if L["id"] not in by_id and L != O[L["id"]]:
        problems.append(f"{L['id']} changed but is not mine")

print(f"{changed} prose fields changed in {len(by_id)} lessons")
for s in span_notes:
    print(s)
for p in problems:
    print("PROBLEM", p)
print("OK: only prose changed" if not problems else f"{len(problems)} problems")
sys.exit(1 if problems else 0)
