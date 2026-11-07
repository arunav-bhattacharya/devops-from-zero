import json, sys
f, lid = sys.argv[1], sys.argv[2]
d = json.load(open(f))
for l in d['lessons']:
    if l['id'] != lid: continue
    def wc(s): return len(s.split())
    print('ID', l['id'], l['title'], 'minutes', l['minutes'])
    print('GOAL:', l['goal'])
    g = l['guess']; print('GUESS:', g['q']); [print('  ', i, o) for i, o in enumerate(g['options'])]; print('  ans', g['answer'], 'WHY:', g['why'])
    print('TERMS:')
    for t in l['terms']: print('  -', t['term'], ':', t['plain'])
    tot = 0
    for i, s in enumerate(l['sections']):
        tot += wc(s['body'])
        print(f'\n=== S{i}: {s["h"]} ({wc(s["body"])} w)')
        print(s['body'])
        for r in s.get('refs', []): print('   ref:', r['title'], r['url'])
    print('\nTOTAL section words', tot)
    print('\nANALOGY:', l['analogy'])
    print('\nCAPTION:', l['diagram_caption'])
    print('\nWORKED:', l['worked']['title'])
    for s in l['worked']['steps']:
        print(' SAY:', s['say'])
        if s.get('code'): print('   CODE:\n' + '\n'.join('     ' + x for x in s['code'].split('\n')))
    print('\nCODE FILES:', [c['title'] for c in l['code']])
    for c in l['code']:
        print('---', c['title'], 'run:', c.get('run'))
        print(c['src'])
    print('\nCOMMANDS:')
    for c in l['commands']: print('  ', c['cmd'], '::', c['what'])
    print('\nMISTAKE:', l['mistake'])
    print('\nREAL_WORLD:', l['real_world'])
    t = l['task']; print('\nTASK:', t['title'])
    for s in t['steps']: print('  *', s)
    for h in t['hints']: print('  hint:', h)
    print('  done_when:', t['done_when'])
    print('\nEXPLAIN_BACK:', l['explain_back']['prompt']); print('  A:', l['explain_back']['answer'])
    print('\nRECAP:'); [print('  -', r) for r in l['recap']]
    print('\nCHECK:')
    for c in l['check']:
        print('  Q:', c['q']); [print('    ', i, o) for i, o in enumerate(c['options'])]; print('    ans', c['answer'], 'WHY:', c['why'])
    print('\nINTERVIEW:')
    for c in l['interview']: print('  Q:', c['q']); print('  A:', c['a'])
    print('\nDEEPER:', l['deeper']['body'])
    print('\nSOURCES:', l['sources'])
