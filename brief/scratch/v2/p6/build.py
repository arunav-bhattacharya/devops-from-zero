#!/usr/bin/env python3
"""Build content/p6.json (Part 6: Terraform) for the second edition.

Run:  python3 brief/scratch/v2/p6/build.py
Code blocks are read from the tested lab files (labs/hello-devops/infra,
labs/hello-devops/.github/workflows/terraform.yml, labs/terraform-practice)
and from files/dNN/ for day-specific versions of infra/local.
"""
import json
import sys

sys.path.insert(0, __import__("os").path.dirname(__file__))

from common import ROOT  # noqa: E402
import d25, d26, d27, d28, d29  # noqa: E402,E401
import part  # noqa: E402

DOC = {
    "part": 6,
    "title": "Infrastructure as Code with Terraform",
    "intro": part.INTRO,
    "lessons": [d25.LESSON, d26.LESSON, d27.LESSON, d28.LESSON, d29.LESSON],
    "recap": part.RECAP,
    "flashcards": part.FLASHCARDS,
    "resources": part.RESOURCES,
    "quiz": part.QUIZ,
}

out = ROOT / "content" / "p6.json"
out.write_text(json.dumps(DOC, indent=1, ensure_ascii=False) + "\n")
print(f"wrote {out}")
