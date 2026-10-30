#!/usr/bin/env python3
"""Build content/p4.json: Part 4, CI/CD with GitHub Actions (d17 to d21), second edition.

Run:   python3 brief/scratch/v2/p4/build.py [--docs /path/to/github-docs-clone]
Then:  python3 brief/validate.py content/p4.json

Lab files (ci.yml, release.yml, dependabot.yml, the PR template and the
setup-app composite action) are read from labs/hello-devops, and the earlier
versions of ci.yml plus the Day 20 practice files from files/, so the lesson
code always matches what was tested. files/out-*.txt hold the real act output
written by run_act.sh.

With --docs, every docs.github.com link is checked against a local clone of
github/docs (content/<path>.md or content/<path>/index.md must exist).
"""
import json
import pathlib
import re
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import d17  # noqa: E402
import d18  # noqa: E402
import d19  # noqa: E402
import d20  # noqa: E402
import d21  # noqa: E402
import part  # noqa: E402
from common import ROOT  # noqa: E402

OUT = ROOT / "content/p4.json"


def check_docs(data, docs):
    urls = sorted(set(re.findall(r"https://docs\.github\.com/en/[^\s\)\"\]]+", json.dumps(data))))
    bad = []
    for u in urls:
        p = u[len("https://docs.github.com/en/"):].split("#")[0].rstrip("/")
        if not ((docs / "content" / (p + ".md")).exists() or (docs / "content" / p / "index.md").exists()):
            bad.append(u)
    print(f"checked {len(urls)} docs.github.com links, {len(bad)} missing")
    for u in bad:
        print("  MISSING", u)
    return not bad


def main():
    data = {
        "part": 4,
        "title": "CI/CD with GitHub Actions",
        "intro": part.INTRO,
        "lessons": [d17.LESSON, d18.LESSON, d19.LESSON, d20.LESSON, d21.LESSON],
        "recap": part.RECAP,
        "flashcards": part.FLASHCARDS,
        "resources": part.RESOURCES,
        "quiz": part.QUIZ,
    }
    ok = True
    if "--docs" in sys.argv:
        ok = check_docs(data, pathlib.Path(sys.argv[sys.argv.index("--docs") + 1]))
    OUT.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")
    print(f"wrote {OUT}")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
