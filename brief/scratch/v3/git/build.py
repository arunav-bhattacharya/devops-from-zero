#!/usr/bin/env python3
"""Build content/p2.json (Part 2, Git: Days 8 and 9) and rework Day 23 in content/p6.json.

Run from anywhere:  python3 brief/scratch/v3/git/build.py
Day 23 is rebuilt from p6.orig.json (a copy of p6.json taken before the rework), so running
this script again gives the same result. Only the Day 23 lesson in p6.json is replaced.
"""
import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import d08  # noqa: E402
import d09  # noqa: E402
import d23  # noqa: E402
import part  # noqa: E402
from common import ROOT  # noqa: E402


def write(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=1) + "\n")
    print("wrote", path.relative_to(ROOT))


def main():
    p2 = {
        "part": 2,
        "title": "Version control with Git",
        "intro": part.INTRO,
        "lessons": [d08.LESSON, d09.LESSON],
        "recap": part.RECAP,
        "flashcards": part.FLASHCARDS,
        "resources": part.RESOURCES,
        "quiz": part.QUIZ,
    }
    write(ROOT / "content" / "p2.json", p2)

    # Day 23: replace only that lesson in the current p6.json. d23.build() takes the
    # parts it keeps from p6.orig.json, so a re-run gives the same Day 23.
    p6 = json.loads((ROOT / "content" / "p6.json").read_text())
    idx = next(i for i, x in enumerate(p6["lessons"]) if x["id"] == "d23")
    p6["lessons"][idx] = d23.build()
    p6["lessons"][idx]["minutes"] = 50
    write(ROOT / "content" / "p6.json", p6)


if __name__ == "__main__":
    main()
