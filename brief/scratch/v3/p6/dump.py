import json, sys
d = json.load(open(sys.argv[1]))
which = sys.argv[2]
def show(path, val):
    print(f"=== {path}\n{val}\n")
if which == "part":
    show("intro", d["intro"])
    for i, r in enumerate(d["recap"]): show(f"recap[{i}]", r)
    for i, f in enumerate(d["flashcards"]): show(f"flashcards[{i}] FRONT: {f['front']}", f["back"])
    for i, r in enumerate(d["resources"]): show(f"resources[{i}] {r['title']}", r["why"])
    for i, q in enumerate(d["quiz"]): show(f"quiz[{i}] Q: {q['q']} | OPTS: {q['options']} | ANS {q['answer']}", q["why"])
else:
    L = next(x for x in d["lessons"] if x["id"] == which)
    show("goal", L["goal"])
    g = L["guess"]; show(f"guess Q: {g['q']} | {g['options']} | ans {g['answer']}", g["why"])
    for i, t in enumerate(L["terms"]): show(f"terms[{i}] {t['term']}", t["plain"])
    for i, s in enumerate(L["sections"]): show(f"sections[{i}] H: {s['h']}", s["body"])
    show("analogy", L["analogy"])
    show("diagram_caption", L["diagram_caption"])
    for i, s in enumerate(L["worked"]["steps"]): show(f"worked.steps[{i}] (code: {bool(s.get('code'))})", s["say"] + ("\n--code--\n" + s["code"] if s.get("code") else ""))
    for i, c in enumerate(L["commands"]): show(f"commands[{i}] {c['cmd']}", c["what"])
    show("mistake", L["mistake"])
    show("real_world", L["real_world"])
    t = L["task"]
    show("task.title", t["title"])
    for i, s in enumerate(t["steps"]): show(f"task.steps[{i}]", s)
    for i, s in enumerate(t["hints"]): show(f"task.hints[{i}]", s)
    show("task.done_when", t["done_when"])
    show("explain_back.prompt", L["explain_back"]["prompt"])
    show("explain_back.answer", L["explain_back"]["answer"])
    for i, r in enumerate(L["recap"]): show(f"recap[{i}]", r)
    for i, q in enumerate(L["check"]): show(f"check[{i}] Q: {q['q']} | {q['options']} | ans {q['answer']}", q["why"])
    for i, q in enumerate(L["interview"]): show(f"interview[{i}] Q: {q['q']}", q["a"])
    show("deeper", L["deeper"]["body"])
