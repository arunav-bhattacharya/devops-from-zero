import json, sys
d = json.load(open(sys.argv[1]))
lid = sys.argv[2]
def wc(s): return len(s.split())
if lid == 'part':
    print('INTRO:', d['intro']); print('RECAP:', d['recap'])
    for f in d['flashcards']: print('FC:', f)
    for q in d['quiz']: print('QZ:', q)
    for r in d['resources']: print('RES:', r)
    sys.exit()
for l in d['lessons']:
    if l['id'] != lid: continue
    print('#', l['id'], l['title'], l['minutes'])
    print('GOAL:', l['goal'])
    print('GUESS:', json.dumps(l['guess']))
    for t in l['terms']: print('TERM:', t['term'], '::', t['plain'])
    tot = 0
    for i, s in enumerate(l['sections']):
        tot += wc(s['body'])
        print(f'\n== S{i}: {s["h"]} ({wc(s["body"])} w)\n{s["body"]}')
    print('\nTOTAL section words', tot)
    print('\nANALOGY:', l['analogy'])
    print('CAPTION:', l['diagram_caption'])
    print('WORKED:', l['worked']['title'])
    for st in l['worked']['steps']:
        print('  SAY:', st['say']); 
        if st.get('code'): print('  CODE:\n' + st['code'])
    for c in l['code']: print('CODEFILE:', c['title'], c.get('run'))
    for c in l['commands']: print('CMD:', c['cmd'], '::', c['what'])
    print('MISTAKE:', l['mistake'])
    print('REAL:', l['real_world'])
    print('TASK:', l['task']['title'])
    for s in l['task']['steps']: print('  STEP:', s)
    for s in l['task']['hints']: print('  HINT:', s)
    print('  DONE:', l['task']['done_when'])
    print('EB PROMPT:', l['explain_back']['prompt'])
    print('EB ANSWER:', l['explain_back']['answer'])
    for r in l['recap']: print('RECAP:', r)
    for c in l['check']: print('CHECK:', json.dumps(c))
    for c in l['interview']: print('IV:', c['q'], '\n   A:', c['a'])
    print('DEEPER:', l['deeper']['body'])
