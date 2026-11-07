import json, sys
d = json.load(open(sys.argv[1]))
only = sys.argv[2] if len(sys.argv) > 2 else None
def out(path, text):
    print(f"=== {path}\n{text}\n")
if only in (None, 'part'):
    out("intro", d["intro"])
    for i, r in enumerate(d["recap"]): out(f"recap[{i}]", r)
    for i, f in enumerate(d["flashcards"]): out(f"flashcards[{i}].back  (front: {f['front']})", f["back"])
    for i, q in enumerate(d["quiz"]): out(f"quiz[{i}].why (q: {q['q']} | opts: {q['options']} | ans {q['answer']})", q["why"])
    for i, r in enumerate(d["resources"]): out(f"resources[{i}].why ({r['title']})", r["why"])
for L in d["lessons"]:
    if only not in (None, L["id"]): continue
    p = L["id"]
    out(f"{p}.goal", L["goal"])
    out(f"{p}.guess.why (q: {L['guess']['q']} | {L['guess']['options']} | ans {L['guess']['answer']})", L["guess"]["why"])
    for i, t in enumerate(L["terms"]): out(f"{p}.terms[{i}].plain ({t['term']})", t["plain"])
    for i, s in enumerate(L["sections"]): out(f"{p}.sections[{i}].body (h: {s['h']})", s["body"])
    out(f"{p}.analogy", L["analogy"])
    out(f"{p}.diagram_caption", L["diagram_caption"])
    for i, s in enumerate(L["worked"]["steps"]):
        out(f"{p}.worked.steps[{i}].say", s["say"] + ("\n[code:]\n" + s["code"] if s.get("code") else ""))
    out(f"{p}.mistake", L["mistake"])
    out(f"{p}.real_world", L["real_world"])
    for i, s in enumerate(L["task"]["steps"]): out(f"{p}.task.steps[{i}]", s)
    for i, s in enumerate(L["task"]["hints"]): out(f"{p}.task.hints[{i}]", s)
    out(f"{p}.task.done_when", L["task"]["done_when"])
    out(f"{p}.explain_back.prompt", L["explain_back"]["prompt"])
    out(f"{p}.explain_back.answer", L["explain_back"]["answer"])
    for i, r in enumerate(L["recap"]): out(f"{p}.recap[{i}]", r)
    for i, q in enumerate(L["check"]): out(f"{p}.check[{i}].why (q: {q['q']} | {q['options']} | ans {q['answer']})", q["why"])
    for i, q in enumerate(L["interview"]): out(f"{p}.interview[{i}].a (q: {q['q']})", q["a"])
    out(f"{p}.deeper.body", L["deeper"]["body"])
