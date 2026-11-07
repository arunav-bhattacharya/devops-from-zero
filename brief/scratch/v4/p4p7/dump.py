import json, sys
f, lid = sys.argv[1], sys.argv[2]
d = json.load(open(f))
for l in d['lessons']:
    if l['id'] != lid: continue
    print('#', l['id'], l['title'], l.get('minutes'))
    print('GOAL:', l['goal'])
    g = l['guess']; print('GUESS:', g['q']); [print('  ', i, o) for i, o in enumerate(g['options'])]; print('  ans', g['answer'], 'WHY:', g['why'])
    print('TERMS:')
    for t in l['terms']: print('  -', t['term'], '::', t['plain'])
    for i, s in enumerate(l['sections']):
        print(f'\n## S{i} {s["h"]}  ({len(s["body"].split())}w)')
        print(s['body'])
    print('\nANALOGY:', l['analogy'])
    print('CAPTION:', l['diagram_caption'])
    print('\nWORKED:', l['worked']['title'])
    for st in l['worked']['steps']:
        print('  SAY:', st['say'])
        if st.get('code'): print('  CODE:\n' + '\n'.join('     ' + x for x in st['code'].split('\n')))
    print('\nCODE FILES:')
    for c in l['code']: print('  ', c['title'], '| run:', c.get('run'))
    print('COMMANDS:')
    for c in l['commands']: print('  ', c['cmd'], '::', c['what'])
    print('\nMISTAKE:', l['mistake'])
    print('REAL_WORLD:', l['real_world'])
    t = l['task']; print('\nTASK:', t['title'])
    for s in t['steps']: print('  *', s)
    for h in t['hints']: print('  HINT:', h)
    print('  DONE:', t['done_when'])
    print('\nEXPLAIN PROMPT:', l['explain_back']['prompt']); print('EXPLAIN ANSWER:', l['explain_back']['answer'])
    print('RECAP:'); [print('  -', r) for r in l['recap']]
    print('CHECK:')
    for c in l['check']:
        print('  Q:', c['q']); [print('    ', i, o) for i, o in enumerate(c['options'])]; print('    ans', c['answer'], 'WHY:', c['why'])
    print('INTERVIEW:')
    for c in l['interview']: print('  Q:', c['q']); print('  A:', c['a'])
    print('\nDEEPER:', l['deeper']['body'])
    words = sum(len(s['body'].split()) for s in l['sections'])
    print('\nSECTION WORDS:', words)
