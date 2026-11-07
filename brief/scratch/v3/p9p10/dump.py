import json, sys
path, which = sys.argv[1], sys.argv[2]
d = json.load(open(path))
def p(k, v):
    print(f"### {k}\n{v}\n")
if which == "part":
    p("intro", d["intro"])
    for i, r in enumerate(d["recap"]): p(f"recap[{i}]", r)
    for i, f in enumerate(d["flashcards"]): p(f"flash[{i}] FRONT: {f['front']}", f["back"])
    for i, q in enumerate(d["quiz"]): p(f"quiz[{i}] Q: {q['q']} | OPTS: {q['options']} | ans={q['answer']}", q["why"])
    for i, r in enumerate(d["resources"]): p(f"res[{i}] {r['title']}", r["why"])
else:
    L = [l for l in d["lessons"] if l["id"] == which][0]
    p("goal", L["goal"])
    g = L["guess"]; p(f"guess Q: {g['q']} | OPTS: {g['options']} | ans={g['answer']}", g["why"])
    for i, t in enumerate(L["terms"]): p(f"term[{i}] {t['term']}", t["plain"])
    for i, s in enumerate(L["sections"]): p(f"sec[{i}] {s['h']}", s["body"])
    p("analogy", L["analogy"])
    for i, s in enumerate(L["worked"]["steps"]):
        p(f"worked[{i}] say", s["say"])
        if s.get("code"): print("  [code]\n" + s["code"] + "\n")
    p("mistake", L["mistake"]); p("real_world", L["real_world"])
    t = L["task"]
    for i, s in enumerate(t["steps"]): p(f"task.step[{i}]", s)
    for i, s in enumerate(t["hints"]): p(f"task.hint[{i}]", s)
    p("task.done_when", t["done_when"])
    p("explain.prompt", L["explain_back"]["prompt"]); p("explain.answer", L["explain_back"]["answer"])
    for i, r in enumerate(L["recap"]): p(f"recap[{i}]", r)
    for i, c in enumerate(L["check"]): p(f"check[{i}] Q: {c['q']} | OPTS: {c['options']} | ans={c['answer']}", c["why"])
    for i, q in enumerate(L["interview"]): p(f"interview[{i}] Q: {q['q']}", q["a"])
    p("deeper", L["deeper"]["body"])
