import json, sys
f, lid = sys.argv[1], sys.argv[2]
d = json.load(open(f))
for l in d['lessons']:
    if l['id'] != lid: continue
    print('ID', l['id'], l['title'], 'min', l['minutes'])
    print('GOAL:', l['goal'])
    g = l['guess']; print('\nGUESS:', g['q']); [print('  ', i, o) for i, o in enumerate(g['options'])]; print('  ans', g['answer'], 'WHY:', g['why'])
    print('\nTERMS:')
    for t in l['terms']: print(' -', t['term'], '::', t['plain'])
    for i, s in enumerate(l['sections']):
        print(f'\n=== S{i}: {s["h"]}\n{s["body"]}')
        print('  refs:', [r['title'] for r in s.get('refs', [])])
    print('\nANALOGY:', l['analogy'])
    print('\nCAPTION:', l['diagram_caption'])
    print('\nWORKED:', l['worked']['title'])
    for st in l['worked']['steps']:
        print(' SAY:', st['say'])
        if st.get('code'): print('   CODE:\n' + st['code'])
    print('\nCODE files:', [(c['title'], c.get('run')) for c in l['code']])
    print('\nCOMMANDS:'); [print(' ', c['cmd'], '::', c['what']) for c in l['commands']]
    print('\nMISTAKE:', l['mistake'])
    print('\nREAL_WORLD:', l['real_world'])
    t = l['task']; print('\nTASK:', t['title']); [print('  step:', s) for s in t['steps']]; [print('  hint:', s) for s in t['hints']]; print('  done:', t['done_when'])
    print('\nEXPLAIN BACK:', l['explain_back']['prompt'], '\n  ANS:', l['explain_back']['answer'])
    print('\nRECAP:'); [print(' -', r) for r in l['recap']]
    print('\nCHECK:')
    for c in l['check']:
        print(' Q:', c['q']); [print('   ', i, o) for i, o in enumerate(c['options'])]; print('   ans', c['answer'], 'WHY:', c['why'])
    print('\nINTERVIEW:')
    for c in l['interview']: print(' Q:', c['q'], '\n A:', c['a'])
    print('\nDEEPER:', l['deeper']['minutes'], '\n' + l['deeper']['body'])
    print('\nSOURCES:', [s['url'] for s in l['sources']])
