"""Build content/parts/p7b.json (Days 35 to 38) and p7b-extras.json for Part 7, second half.
Run from anywhere: python3 -I brief/scratch/v2/p7b/build_p7b.py
Code blocks are read from the lab files, so the lesson always shows the tested files."""
import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
ROOT = HERE.parents[3]
LAB = ROOT / "labs/hello-devops"
OUT = ROOT / "content/parts"

import d35, d36, d37, d38  # noqa: E402
from extras import EXTRAS  # noqa: E402

ORDER = ["id", "title", "minutes", "goal", "guess", "terms", "sections", "analogy", "diagram", "diagram_caption",
         "worked", "code", "commands", "mistake", "real_world", "task", "explain_back", "recap", "check", "interview",
         "deeper", "sources"]


def build(mod):
    L = dict(mod.LESSON)
    code = []
    for lang, path, run in L.pop("code_files"):
        src = (LAB / path).read_text().rstrip("\n")
        code.append({"lang": lang, "title": path, "src": src, "run": run})
    L["code"] = code
    missing = [k for k in ORDER if k not in L]
    assert not missing, (L["id"], missing)
    return {k: L[k] for k in ORDER}


lessons = [build(m) for m in (d35, d36, d37, d38)]
OUT.mkdir(parents=True, exist_ok=True)
(OUT / "p7b.json").write_text(json.dumps(lessons, indent=1, ensure_ascii=False) + "\n")
(OUT / "p7b-extras.json").write_text(json.dumps(EXTRAS, indent=1, ensure_ascii=False) + "\n")
print("wrote", OUT / "p7b.json", "and", OUT / "p7b-extras.json")
