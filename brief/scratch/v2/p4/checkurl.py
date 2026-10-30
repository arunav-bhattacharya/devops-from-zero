#!/usr/bin/env python3
"""Check that docs.github.com/en/<path> URLs map to a source file in a local
github/docs clone (content/<path>.md or content/<path>/index.md).
Usage: checkurl.py DOCS_CLONE URL [URL...]"""
import pathlib
import sys

docs = pathlib.Path(sys.argv[1])
bad = 0
for url in sys.argv[2:]:
    pre = "https://docs.github.com/en/"
    if not url.startswith(pre):
        print("SKIP", url)
        continue
    p = url[len(pre):].split("#")[0].rstrip("/")
    cands = [docs / "content" / (p + ".md"), docs / "content" / p / "index.md"]
    hit = next((c for c in cands if c.exists()), None)
    if hit:
        print("OK  ", url)
    else:
        bad += 1
        print("MISS", url)
sys.exit(1 if bad else 0)
