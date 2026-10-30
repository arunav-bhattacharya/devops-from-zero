"""Quick per-lesson check with the real validator's functions: python3 lcheck.py l03"""
import importlib, sys, json
sys.path.insert(0, "/home/user/devops-from-zero/brief")
import validate as V
mod = importlib.import_module(sys.argv[1])
L = mod.LESSON
ref = next(l for p in V.INDEX for l in p["lessons"] if l["id"] == L["id"])
total = V.lesson(L, ref, 1)
print(L["id"], "section words:", total)
for i, s in enumerate(L["sections"]):
    print(f"  sec{i+1} {V.words(s['body'])} words  {s['h']}")
allsent = [x for s in L["sections"] for x in V.sentences(s["body"])]
print("  avg sentence", sum(V.words(x) for x in allsent) / len(allsent))
print("  deeper words", V.words(L["deeper"]["body"]))
for x in V.errors + V.warns: print(x)
