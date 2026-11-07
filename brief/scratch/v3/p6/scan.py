import json, re, sys
d = json.load(open(sys.argv[1]))
def fields(d):
    yield "intro", d["intro"]
    for i,r in enumerate(d["recap"]): yield f"recap{i}", r
    for i,f in enumerate(d["flashcards"]): yield f"fc{i}", f["back"]
    for i,r in enumerate(d["resources"]): yield f"res{i}", r["why"]
    for i,q in enumerate(d["quiz"]): yield f"quiz{i}", q["why"]
    for L in d["lessons"]:
        p = L["id"]
        yield p+".goal", L["goal"]; yield p+".guess", L["guess"]["why"]
        for i,t in enumerate(L["terms"]): yield f"{p}.term{i}", t["plain"]
        for i,s in enumerate(L["sections"]): yield f"{p}.sec{i}", s["body"]
        for k in ("analogy","mistake","real_world"): yield f"{p}.{k}", L[k]
        for i,s in enumerate(L["worked"]["steps"]): yield f"{p}.worked{i}", s["say"]
        for i,s in enumerate(L["task"]["steps"]): yield f"{p}.task{i}", s
        for i,s in enumerate(L["task"]["hints"]): yield f"{p}.hint{i}", s
        yield p+".done", L["task"]["done_when"]
        yield p+".ebp", L["explain_back"]["prompt"]; yield p+".eba", L["explain_back"]["answer"]
        for i,r in enumerate(L["recap"]): yield f"{p}.recap{i}", r
        for i,q in enumerate(L["check"]): yield f"{p}.check{i}", q["why"]
        for i,q in enumerate(L["interview"]): yield f"{p}.iv{i}", q["a"]
        yield p+".deeper", L["deeper"]["body"]
pats = {
 "ing-tail": r", (\w+ing)\b",
 "So-start": r"(^|\. |\n)So\b",
 "worth": r"\bworth\b",
 "simply/just/really": r"\b(simply|really|actually|exactly)\b",
 "count-intro": r"\b(Two|Three|Four|One more|A few) (things|ways|details|settings|more)\b",
 "finally": r"\b(Finally|First|Second|Third|Also),",
 "remember": r"\b(Remember|Note|Notice) that\b",
 "colon-fragment": r"\b(The short version|Free advice)\b",
 "think of": r"\b[Tt]hink of\b",
 "comparison": r"\b(comparison|picture misses|has a limit)\b",
 "not-x": r"\bnot [^.,]{1,30}, (but )?(the|a)\b",
 "matters": r"\bmatters?\b",
 "semicolon": r";",
}
for where, t in fields(d):
    for name, pat in pats.items():
        for m in re.finditer(pat, t):
            print(f"{where} [{name}] ...{t[max(0,m.start()-50):m.end()+40]!r}")
