import json, sys
d = json.load(open(sys.argv[1]))
which = sys.argv[2] if len(sys.argv) > 2 else None
def out(*a): print(*a)
if which == 'part':
    out('INTRO', d['intro']); out('RECAP', json.dumps(d['recap'], indent=1))
    for f in d['flashcards']: out('FC', f['front'], '||', f['back'])
    for q in d['quiz']: out('QZ', q['q'], q['options'], q['answer'], '||', q['why'], q.get('from'))
    for r in d['resources']: out('RS', r['title'], '||', r['why'])
    sys.exit()
for l in d['lessons']:
    if which and l['id'] != which: continue
    out('=====', l['id'], l['title'], l['minutes'])
    out('GOAL:', l['goal'])
    g = l['guess']; out('GUESS:', g['q'], g['options'], g['answer'], '|| WHY:', g['why'])
    for t in l['terms']: out('TERM:', t['term'], '::', t['plain'])
    for i, s in enumerate(l['sections']):
        out(f'\n--- S{i}: {s["h"]}'); out(s['body'])
    out('\nANALOGY:', l['analogy'])
    out('CAPTION:', l['diagram_caption'])
    out('\nWORKED:', l['worked']['title'])
    for st in l['worked']['steps']:
        out('  SAY:', st['say'])
        if st.get('code'): out('  CODE:\n' + st['code'])
    out('\nCODE FILES:', [c['title'] for c in l['code']])
    for c in l['commands']: out('CMD:', c['cmd'], '::', c['what'])
    out('\nMISTAKE:', l['mistake']); out('REAL:', l['real_world'])
    t = l['task']; out('\nTASK:', t['title'])
    for s in t['steps']: out('  STEP:', s)
    for h in t['hints']: out('  HINT:', h)
    out('  DONE:', t['done_when'])
    e = l['explain_back']; out('\nEB PROMPT:', e['prompt']); out('EB ANSWER:', e['answer'])
    out('\nRECAP:'); [out('  -', r) for r in l['recap']]
    for c in l['check']: out('CHECK:', c['q'], c['options'], c['answer'], '|| WHY:', c['why'])
    for q in l['interview']: out('IV:', q['q'], '\n  A:', q['a'])
    out('\nDEEPER:', l['deeper']['body'])
