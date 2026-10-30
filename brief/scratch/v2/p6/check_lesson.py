"""Run the course validator's lesson checks on single lessons while drafting.
Usage: python3 check_lesson.py d25 [d26 ...]"""
import importlib
import json
import sys

sys.path.insert(0, "/home/user/devops-from-zero/brief")
import validate as V  # noqa: E402

for lid in sys.argv[1:]:
    mod = importlib.import_module(lid)
    L = mod.LESSON
    ref = next(x for p in V.INDEX for x in p["lessons"] if x["id"] == lid)
    V.errors.clear()
    V.warns.clear()
    total = V.lesson(L, ref, 6)
    secs = L["sections"]
    sent = [x for s in secs for x in V.sentences(s["body"])]
    avg = sum(V.words(x) for x in sent) / len(sent)
    per = [V.words(s["body"]) for s in secs]
    print(f"{lid}: section words {total} {per}, avg sentence {avg:.1f}, deeper {V.words(L['deeper']['body'])}")
    for x in V.errors + V.warns:
        print("  ", x)
    json.dumps(L)
