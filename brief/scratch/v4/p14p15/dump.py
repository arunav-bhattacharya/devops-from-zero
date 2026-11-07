import json, sys
p = json.load(open(sys.argv[1]))
ids = sys.argv[2:] if len(sys.argv) > 2 else None
def wc(s): return len(s.split())
if not ids:
    print("PART", p['part'], p['title']); print("INTRO:", p['intro'])
for L in p['lessons']:
    if ids and L['id'] not in ids: continue
    print("="*80); print(L['id'], L['title'], L['minutes'])
    print("GOAL:", L['goal'])
    g = L['guess']; print("GUESS:", g['q'], g['options'], g['answer'], "WHY:", g['why'])
    print("TERMS:")
    for t in L['terms']: print("  -", t['term'], ":", t['plain'])
    tot = 0
    for i, s in enumerate(L['sections']):
        tot += wc(s['body'])
        print(f"\n--- S{i}: {s['h']} ({wc(s['body'])}w)"); print(s['body'])
    print("\nSECTION WORDS:", tot)
    print("\nANALOGY:", L['analogy'])
    print("CAPTION:", L['diagram_caption'])
    print("WORKED:", L['worked']['title'])
    for st in L['worked']['steps']:
        print("  SAY:", st['say'])
        if st.get('code'): print("  CODE:\n" + "\n".join("     "+x for x in st['code'].split("\n")))
    print("FILES:", [c['title'] for c in L['code']])
    print("COMMANDS:")
    for c in L['commands']: print("  ", c['cmd'], "::", c['what'])
    print("MISTAKE:", L['mistake'])
    print("REAL_WORLD:", L['real_world'])
    print("TASK:", L['task']['title'])
    for s in L['task']['steps']: print("  -", s)
    print("  HINTS:", L['task']['hints'])
    print("  DONE:", L['task']['done_when'])
    print("EXPLAIN_BACK:", L['explain_back']['prompt']); print("  ANSWER:", L['explain_back']['answer'])
    print("RECAP:"); [print("  -", r) for r in L['recap']]
    print("CHECK:")
    for c in L['check']: print("  Q:", c['q'], c['options'], c['answer'], "WHY:", c['why'])
    print("INTERVIEW:")
    for c in L['interview']: print("  Q:", c['q']); print("  A:", c['a'])
    print("DEEPER:", L['deeper']['body'])
if not ids:
    print("PART RECAP:", p['recap'])
    for f in p['flashcards']: print("FC:", f['front'], "->", f['back'])
    for q in p['quiz']: print("QZ:", q['q'], q['options'], q['answer'], q['why'], q.get('from'))
    for r in p['resources']: print("RES:", r['title'], r['why'])
