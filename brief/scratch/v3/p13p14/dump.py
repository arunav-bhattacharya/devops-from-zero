import json, sys
d = json.load(open(sys.argv[1]))
def p(path, t):
    print(f"### {path}\n{t}\n")
print("PART", d.get("part"), d.get("title"))
p("intro", d["intro"])
for i, r in enumerate(d["recap"]): p(f"recap[{i}]", r)
for i, f in enumerate(d["flashcards"]): p(f"flashcards[{i}] FRONT {f['front']}", f["back"])
for i, q in enumerate(d["quiz"]): p(f"quiz[{i}] Q {q['q']} | OPTS {q['options']} | ANS {q['answer']}", q["why"])
for i, r in enumerate(d["resources"]): p(f"resources[{i}] {r['title']}", r["why"])
for L in d["lessons"]:
    if len(sys.argv) > 2 and L["id"] != sys.argv[2]: continue
    print("=" * 30, L["id"], L["title"])
    p("goal", L["goal"])
    g = L["guess"]; p(f"guess Q {g['q']} | OPTS {g['options']} | ANS {g['answer']}", g["why"])
    for i, t in enumerate(L["terms"]): p(f"terms[{i}] {t['term']}", t["plain"])
    for i, s in enumerate(L["sections"]): p(f"sections[{i}] H {s['h']}", s["body"])
    p("analogy", L["analogy"])
    for i, s in enumerate(L["worked"]["steps"]): p(f"worked[{i}] (code: {bool(s.get('code'))})", s["say"])
    p("mistake", L["mistake"]); p("real_world", L["real_world"])
    t = L["task"]
    for i, s in enumerate(t["steps"]): p(f"task.steps[{i}]", s)
    for i, s in enumerate(t["hints"]): p(f"task.hints[{i}]", s)
    p("task.done_when", t["done_when"])
    p("explain_back.prompt", L["explain_back"]["prompt"]); p("explain_back.answer", L["explain_back"]["answer"])
    for i, r in enumerate(L["recap"]): p(f"recap[{i}]", r)
    for i, c in enumerate(L["check"]): p(f"check[{i}] Q {c['q']} | OPTS {c['options']} | ANS {c['answer']}", c["why"])
    for i, c in enumerate(L["interview"]): p(f"interview[{i}] Q {c['q']}", c["a"])
    p("deeper", L["deeper"]["body"])
