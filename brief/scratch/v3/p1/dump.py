import json, sys
d = json.load(open(sys.argv[1]))
want = sys.argv[2]
for L in d['lessons']:
    if L['id'] != want: continue
    print('ID', L['id'], L['title'])
    print('GOAL:', L['goal'])
    g = L['guess']; print('GUESS:', g['q'], g['options'], g['answer'], '\n  WHY:', g['why'])
    for t in L['terms']: print('TERM:', t['term'], '::', t['plain'])
    for i, s in enumerate(L['sections'], 1):
        print(f'\n=== SEC{i}: {s["h"]}\n{s["body"]}')
    print('\nANALOGY:', L['analogy'])
    print('\nCAPTION:', L['diagram_caption'])
    print('\nWORKED:', L['worked']['title'])
    for i, s in enumerate(L['worked']['steps'], 1):
        print(f'  W{i} SAY: {s["say"]}')
        if s.get('code'): print('     CODE:', s['code'].replace('\n', '\n           '))
    for c in L['code']: print('\nCODEFILE:', c['title'], '| run:', c.get('run'))
    for c in L['commands']: print('CMD:', c['cmd'], '::', c['what'])
    print('\nMISTAKE:', L['mistake'])
    print('\nREAL:', L['real_world'])
    t = L['task']; print('\nTASK:', t['title'])
    for s in t['steps']: print('  STEP:', s)
    for s in t['hints']: print('  HINT:', s)
    print('  DONE:', t['done_when'])
    print('\nEXPLAIN PROMPT:', L['explain_back']['prompt'])
    print('EXPLAIN ANS:', L['explain_back']['answer'])
    for r in L['recap']: print('RECAP:', r)
    for q in L['check']: print('CHECK:', q['q'], q['options'], q['answer'], '\n  WHY:', q['why'])
    for q in L['interview']: print('IV Q:', q['q'], '\n  A:', q['a'])
    print('\nDEEPER:', L['deeper']['minutes'], '\n' + L['deeper']['body'])
