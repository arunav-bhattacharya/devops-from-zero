import json, sys
path, lid = sys.argv[1], sys.argv[2]
d = json.load(open(path))
if lid == 'part':
    for k in ('intro','recap'):
        print('==',k); print(json.dumps(d[k],indent=1,ensure_ascii=False))
    print('== flashcards')
    for f in d['flashcards']: print('F:',f['front'],'\n B:',f['back'])
    print('== quiz')
    for q in d['quiz']: print('Q:',q['q'],'\n  opts:',q['options'],q['answer'],'\n  why:',q['why'],q.get('from',''))
    print('== resources')
    for r in d['resources']: print('R:',r['title'],'|',r['why'])
    sys.exit()
L = [l for l in d['lessons'] if l['id']==lid][0]
print('#', L['id'], L['title'], L['minutes'])
print('GOAL:', L['goal'])
g=L['guess']; print('GUESS:', g['q'], g['options'], g['answer'], '\n WHY:', g['why'])
print('TERMS:')
for t in L['terms']: print(' -', t['term'], '::', t['plain'])
for i,s in enumerate(L['sections'],1):
    print(f'\n## S{i}: {s["h"]}\n{s["body"]}')
print('\nANALOGY:', L['analogy'])
print('CAPTION:', L['diagram_caption'])
print('\nWORKED:', L['worked']['title'])
for i,s in enumerate(L['worked']['steps'],1):
    print(f' W{i} SAY: {s["say"]}')
    if s.get('code'): print('   CODE:\n' + '\n'.join('     '+x for x in s['code'].split('\n')))
print('\nCODE FILES:')
for c in L['code']: print(' --', c['title'], '| run:', c.get('run'), '\n' + c['src'][:3000])
print('\nCOMMANDS:')
for c in L['commands']: print(' -', c['cmd'], '::', c['what'])
print('\nMISTAKE:', L['mistake'])
print('REAL_WORLD:', L['real_world'])
t=L['task']; print('\nTASK:', t['title'])
for s in t['steps']: print(' *', s)
for h in t['hints']: print(' H:', h)
print(' DONE:', t['done_when'])
e=L['explain_back']; print('\nEXPLAIN PROMPT:', e['prompt'], '\n ANSWER:', e['answer'])
print('\nRECAP:'); [print(' -', r) for r in L['recap']]
print('\nCHECK:')
for q in L['check']: print(' Q:', q['q'], q['options'], q['answer'], '\n  WHY:', q['why'])
print('\nINTERVIEW:')
for q in L['interview']: print(' Q:', q['q'], '\n  A:', q['a'])
print('\nDEEPER:', L['deeper']['body'])
