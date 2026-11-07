import json,sys
d=json.load(open(sys.argv[1]))
which=sys.argv[2]
def p(k,v): print(f"### {k}\n{v}\n")
if which=='part':
    p('intro',d['intro'])
    for i,r in enumerate(d['recap']): p(f'recap{i}',r)
    for i,f in enumerate(d['flashcards']): p(f'fc{i} FRONT: {f["front"]}', f['back'])
    for i,q in enumerate(d['quiz']): p(f'quiz{i} Q: {q["q"]} OPTS:{q["options"]} ANS:{q["answer"]}', q['why'])
    for i,r in enumerate(d['resources']): p(f'res{i} {r["title"]}', r['why'])
else:
    L=[l for l in d['lessons'] if l['id']==which][0]
    p('goal',L['goal'])
    p('guess Q: '+L['guess']['q']+' OPTS:'+str(L['guess']['options'])+' ANS:'+str(L['guess']['answer']), L['guess']['why'])
    for t in L['terms']: p('term '+t['term'], t['plain'])
    for i,s in enumerate(L['sections']): p(f'sec{i} H: {s["h"]}', s['body'])
    p('analogy',L['analogy'])
    p('diagram_caption',L['diagram_caption'])
    for i,s in enumerate(L['worked']['steps']): p(f'worked{i}', s['say'] + ("\n[CODE]\n"+s['code'] if s.get('code') else ''))
    p('mistake',L['mistake']); p('real_world',L['real_world'])
    for i,s in enumerate(L['task']['steps']): p(f'task.step{i}', s)
    for i,s in enumerate(L['task']['hints']): p(f'task.hint{i}', s)
    p('task.done_when', L['task']['done_when'])
    p('explain.prompt', L['explain_back']['prompt']); p('explain.answer', L['explain_back']['answer'])
    for i,r in enumerate(L['recap']): p(f'recap{i}',r)
    for i,q in enumerate(L['check']): p(f'check{i} Q: {q["q"]} OPTS:{q["options"]} ANS:{q["answer"]}', q['why'])
    for i,q in enumerate(L['interview']): p(f'interview{i} Q: {q["q"]}', q['a'])
    p('deeper', L['deeper']['body'])
