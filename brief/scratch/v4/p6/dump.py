import json,sys
d=json.load(open(sys.argv[1]))
want=sys.argv[2:]
for L in d['lessons']:
    if want and L['id'] not in want: continue
    print('='*30,L['id'],L['title'],L['minutes'])
    print('GOAL:',L['goal'])
    g=L['guess'];print('GUESS:',g['q'],g['options'],g['answer'],'\n  why:',g['why'])
    for t in L['terms']: print('TERM',t['term'],':',t['plain'])
    for i,s in enumerate(L['sections']):
        print(f'--- S{i}: {s["h"]}'); print(s['body'])
    print('--- ANALOGY:',L['analogy'])
    print('--- CAPTION:',L['diagram_caption'])
    print('--- WORKED:',L['worked']['title'])
    for st in L['worked']['steps']:
        print(' SAY:',st['say'])
        if st.get('code'): print('   CODE:',st['code'].replace('\n','\n        '))
    print('--- CODE files:',[c['title'] for c in L['code']])
    print('--- MISTAKE:',L['mistake'])
    print('--- REAL:',L['real_world'])
    t=L['task'];print('--- TASK:',t['title'])
    for s in t['steps']: print('  *',s)
    for h in t['hints']: print('  hint:',h)
    print('  done:',t['done_when'])
    print('--- EB:',L['explain_back']['prompt'],'\n  ANS:',L['explain_back']['answer'])
    print('--- RECAP:'); [print('  -',r) for r in L['recap']]
    for c in L['check']: print('CHECK:',c['q'],c['options'],c['answer'],'\n  why:',c['why'])
    for c in L['interview']: print('INT:',c['q'],'\n  A:',c['a'])
    print('--- DEEPER:',L['deeper']['body'])
