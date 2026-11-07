"""Build content/p15.json (Part 15: service mesh) for "DevOps, from zero".
Run from anywhere: python3 brief/scratch/v3/mesh/build.py
Code files are read from labs/hello-devops/mesh/ so the lesson and the lab never drift apart.
Lesson texts live in d58.py, d59.py, d60.py and part.py next to this file."""
import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[3]
sys.path.insert(0, str(HERE))

import d58  # noqa: E402
import d59  # noqa: E402
import d60  # noqa: E402
import part  # noqa: E402

doc = {
    "part": 15,
    "title": "Service mesh: Envoy, Istio, Linkerd and Cilium",
    "intro": part.INTRO,
    "lessons": [d58.LESSON, d59.LESSON, d60.LESSON],
    "recap": part.RECAP,
    "flashcards": part.FLASHCARDS,
    "resources": part.RESOURCES,
    "quiz": part.QUIZ,
}

out = ROOT / "content" / "p15.json"
out.write_text(json.dumps(doc, ensure_ascii=False, indent=1) + "\n")
print(f"wrote {out}")
