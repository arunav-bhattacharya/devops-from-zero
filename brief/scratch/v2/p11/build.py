#!/usr/bin/env python3
"""Build content/p11.json (Part 11: Logs and traces) from the lesson modules.

Run: python3 brief/scratch/v2/p11/build.py
Then: python3 brief/validate.py content/p11.json
Lab files are read from labs/hello-devops/ at build time, so the lesson code always matches the lab.
"""

import importlib
import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from part import PART  # noqa: E402

lessons = [importlib.import_module(lid).L for lid in ("d47", "d48", "d49")]

out = dict(PART)
out["lessons"] = lessons
# Keep the key order of the brief's schema.
ordered = {k: out[k] for k in ("part", "title", "intro", "lessons", "recap", "flashcards", "resources", "quiz")}
path = pathlib.Path("/home/user/devops-from-zero/content/p11.json")
path.write_text(json.dumps(ordered, indent=1, ensure_ascii=False) + "\n")
print(f"wrote {path} with {len(lessons)} lessons")
