"""Patch one lesson's prose fields in content/p10.json from brief/scratch/v5/tf/<id>.py.
Usage: python3 brief/scratch/v5/tf/apply.py d38"""
import importlib.util
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[4]
PART = ROOT / "content/p10.json"
lid = sys.argv[1]
spec = importlib.util.spec_from_file_location(lid, pathlib.Path(__file__).parent / f"{lid}.py")
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
N = m.NEW

d = json.loads(PART.read_text())
L = next(x for x in d["lessons"] if x["id"] == lid)


def same_len(a, b, what):
    if len(a) != len(b):
        sys.exit(f"{what}: {len(b)} given, lesson has {len(a)}")


for k in ("opening", "closing", "goal", "diagram_caption", "mistake", "real_world", "analogy"):
    if k in N:
        L[k] = N[k]
for k in N.get("drop", []):
    L.pop(k, None)
if "aside" in N:
    L["aside"] = N["aside"]
L["guess"]["q"], L["guess"]["why"] = N["guess"]
same_len(L["terms"], N["terms"], "terms")
for t, p in zip(L["terms"], N["terms"]):
    t["plain"] = p
same_len(L["sections"], N["sections"], "sections")
for s, (h, body) in zip(L["sections"], N["sections"]):
    s["h"], s["body"] = h, body.strip()
same_len(L["worked"]["steps"], N["worked"], "worked")
for s, say in zip(L["worked"]["steps"], N["worked"]):
    s["say"] = say
L["task"]["steps"], L["task"]["hints"], L["task"]["done_when"] = N["task"]
L["explain_back"]["prompt"], L["explain_back"]["answer"] = N["explain_back"]
L["recap"] = N["recap"]
same_len(L["check"], N["check"], "check")
for q, (qq, why) in zip(L["check"], N["check"]):
    q["q"], q["why"] = qq, why
same_len(L["interview"], N["interview"], "interview")
for q, (qq, a) in zip(L["interview"], N["interview"]):
    q["q"], q["a"] = qq, a
L["deeper"]["body"] = N["deeper"].strip()

# keep a stable key order: opening after goal, closing after recap
order = list(L.keys())
for k in ("opening", "closing", "aside"):
    if k in order:
        order.remove(k)
out = {}
for k in order:
    out[k] = L[k]
    if k == "goal":
        out["opening"] = L["opening"]
    if k == "recap":
        out["closing"] = L["closing"]
        if "aside" in L:
            out["aside"] = L["aside"]
d["lessons"][d["lessons"].index(L)] = out
PART.write_text(json.dumps(d, indent=1, ensure_ascii=False) + "\n")
print("patched", lid)
