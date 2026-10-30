#!/usr/bin/env python3
"""Build content/p9.json (Part 9: Monitoring with Prometheus) from the lesson modules.

Run: python3 brief/scratch/v2/p9/build.py
Then: python3 brief/validate.py content/p9.json
"""

import importlib
import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from part import PART  # noqa: E402

lessons = []
for lid in ("d41", "d42", "d43", "d44"):
    try:
        mod = importlib.import_module(lid)
    except ModuleNotFoundError:
        print(f"skip {lid} (not written yet)")
        continue
    lessons.append(mod.LESSON)

out = dict(PART)
out["lessons"] = lessons
# Keep the key order of the brief's schema.
ordered = {k: out[k] for k in ("part", "title", "intro", "lessons", "recap", "flashcards", "resources", "quiz")}
path = pathlib.Path("/home/user/devops-from-zero/content/p9.json")
path.write_text(json.dumps(ordered, indent=1, ensure_ascii=False) + "\n")
print(f"wrote {path} with {len(lessons)} lessons")
