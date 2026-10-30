"""Validate the Day 35 to 38 lessons and the proposed extras.
1. Builds a temporary full Part 7 file (my lessons only) in the scratchpad and runs brief/validate.py on it.
2. Runs validate.py's lesson checks on each of my lessons against its own index entry, plus extras checks."""
import importlib.util
import json
import pathlib
import subprocess
import sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[3]
spec = importlib.util.spec_from_file_location("v", ROOT / "brief/validate.py")
v = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v)

lessons = json.loads((ROOT / "content/parts/p7b.json").read_text())
extras = json.loads((ROOT / "content/parts/p7b-extras.json").read_text())

tmp = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else HERE / "tmp"
tmp.mkdir(parents=True, exist_ok=True)
full = {"part": 7, "title": "Kubernetes", "intro": "Temporary file for validation only.", "lessons": lessons, **extras}
(tmp / "p7-full.json").write_text(json.dumps(full, indent=1, ensure_ascii=False))
print("== official validator on the temporary full part (lesson-id and part-count errors are expected)")
r = subprocess.run([sys.executable, "-I", str(ROOT / "brief/validate.py"), str(tmp / "p7-full.json")], capture_output=True, text=True)
print(r.stdout)

print("== per-lesson checks against the right index entries")
ref = next(p for p in v.INDEX if p["part"] == 7)
refs = {x["id"]: x for x in ref["lessons"]}
v.errors.clear(); v.warns.clear()
for L in lessons:
    total = v.lesson(L, refs[L["id"]], 7)
    print(L["id"], "section words:", total)
for k in ("recap",):
    for b in extras[k]:
        v.text_checks("extras.recap", b)
for f in extras["flashcards"]:
    v.text_checks("extras.flashcard", f["back"])
for i, q in enumerate(extras["quiz"]):
    v.mcq(f"extras.quiz{i+1}", q)
for r_ in extras["resources"]:
    v.text_checks("extras.resource", r_["why"])
assert 3 <= len(extras["recap"]) <= 5 and 6 <= len(extras["flashcards"]) <= 10
assert 4 <= len(extras["quiz"]) <= 5 and 4 <= len(extras["resources"]) <= 6
froms = [q for q in extras["quiz"] if q.get("from")]
assert len(froms) == 1 and froms[0]["from"] in ("Part 3", "Part 6"), froms
for x in v.errors + v.warns:
    print(x)
print(f"{len(v.errors)} errors, {len(v.warns)} warnings")
