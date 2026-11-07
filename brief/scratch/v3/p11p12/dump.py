import json, sys
d = json.load(open(sys.argv[1]))
which = sys.argv[2] if len(sys.argv) > 2 else None
def p(path, v):
    print(f"=== {path}\n{v}\n")
if which in (None, "part"):
    p("intro", d["intro"])
    for i, r in enumerate(d["recap"]): p(f"recap[{i}]", r)
    for i, f in enumerate(d["flashcards"]): p(f"flashcards[{i}] FRONT: {f['front']}", f["back"])
    for i, q in enumerate(d["quiz"]): p(f"quiz[{i}] Q: {q['q']} | {q['options']} ans={q['answer']}", q["why"])
    for i, r in enumerate(d["resources"]): p(f"resources[{i}] {r['title']}", r["why"])
for L in d["lessons"]:
    if which not in (None, L["id"]): continue
    i0 = L["id"]
    p(f"{i0}.goal", L["goal"])
    g = L["guess"]; p(f"{i0}.guess Q: {g['q']} | {g['options']} ans={g['answer']}", g["why"])
    for i, t in enumerate(L["terms"]): p(f"{i0}.terms[{i}] {t['term']}", t["plain"])
    for i, s in enumerate(L["sections"]): p(f"{i0}.sections[{i}] H: {s['h']}", s["body"])
    p(f"{i0}.analogy", L["analogy"])
    for i, s in enumerate(L["worked"]["steps"]):
        p(f"{i0}.worked[{i}].say", s["say"])
    p(f"{i0}.mistake", L["mistake"])
    p(f"{i0}.real_world", L["real_world"])
    t = L["task"]
    for i, s in enumerate(t["steps"]): p(f"{i0}.task.steps[{i}]", s)
    for i, s in enumerate(t["hints"]): p(f"{i0}.task.hints[{i}]", s)
    p(f"{i0}.task.done_when", t["done_when"])
    p(f"{i0}.explain_back.prompt", L["explain_back"]["prompt"])
    p(f"{i0}.explain_back.answer", L["explain_back"]["answer"])
    for i, r in enumerate(L["recap"]): p(f"{i0}.recap[{i}]", r)
    for i, q in enumerate(L["check"]): p(f"{i0}.check[{i}] Q: {q['q']} | {q['options']} ans={q['answer']}", q["why"])
    for i, q in enumerate(L["interview"]): p(f"{i0}.interview[{i}] Q: {q['q']}", q["a"])
    p(f"{i0}.deeper", L["deeper"]["body"])
