import json, sys
f, lid = sys.argv[1], sys.argv[2]
d = json.load(open(f))
for L in d['lessons']:
    if L['id'] != lid: continue
    print('ID', L['id'], L['title'], 'min', L['minutes'])
    print('GOAL:', L['goal'])
    g = L['guess']; print('GUESS:', g['q'], g['options'], g['answer'], '\n  WHY:', g['why'])
    print('TERMS:')
    for t in L['terms']: print('  -', t['term'], '::', t['plain'])
    for i, s in enumerate(L['sections']):
        print(f'\n=== S{i}: {s["h"]}'); print(s['body'])
    print('\nANALOGY:', L['analogy'])
    print('CAPTION:', L['diagram_caption'])
    print('DIAGRAM:', L['diagram'][:3000])
    print('\nWORKED:', L['worked']['title'])
    for st in L['worked']['steps']:
        print(' SAY:', st['say']); 
        if st.get('code'): print('  CODE:\n' + st['code'])
    print('\nCODE FILES:')
    for c in L['code']: print(' --', c['title'], c.get('run')); print(c['src'][:2500])
    print('\nCOMMANDS:')
    for c in L['commands']: print(' ', c['cmd'], '::', c['what'])
    print('\nMISTAKE:', L['mistake']); print('REAL:', L['real_world'])
    t = L['task']; print('\nTASK:', t['title'])
    for s in t['steps']: print('  *', s)
    print(' HINTS:', t['hints']); print(' DONE:', t['done_when'])
    print('\nEXPLAIN:', L['explain_back']['prompt'], '\n  A:', L['explain_back']['answer'])
    print('\nRECAP:'); [print('  -', r) for r in L['recap']]
    print('\nCHECK:')
    for c in L['check']: print('  Q:', c['q'], c['options'], c['answer'], '\n   WHY:', c['why'])
    print('\nINTERVIEW:')
    for c in L['interview']: print('  Q:', c['q'], '\n   A:', c['a'])
    print('\nDEEPER:', L['deeper']['body'])
