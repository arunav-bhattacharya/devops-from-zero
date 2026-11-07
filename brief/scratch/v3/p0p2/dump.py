import json, sys
d = json.load(open(sys.argv[1]))
which = sys.argv[2] if len(sys.argv) > 2 else None
def p(label, t):
    print(f"### {label}\n{t}\n")
if which in (None, 'part'):
    p('intro', d['intro'])
    for i, r in enumerate(d['recap']): p(f'recap[{i}]', r)
    for i, f in enumerate(d['flashcards']): p(f'flash[{i}] FRONT: {f["front"]}', f['back'])
    for i, q in enumerate(d['quiz']): p(f'quiz[{i}] Q: {q["q"]} OPTS: {q["options"]} ANS {q["answer"]} FROM {q.get("from")}', q['why'])
    for i, r in enumerate(d['resources']): p(f'res[{i}] {r["title"]}', r['why'])
for L in d['lessons']:
    if which not in (None, L['id']): continue
    print("="*30, L['id'], L['title'])
    p('goal', L['goal'])
    g = L['guess']; p(f'guess Q: {g["q"]} OPTS {g["options"]} ANS {g["answer"]}', g['why'])
    for i, t in enumerate(L['terms']): p(f'term[{i}] {t["term"]}', t['plain'])
    for i, s in enumerate(L['sections']): p(f'sec[{i}] {s["h"]}', s['body'])
    p('analogy', L['analogy'])
    p('diagram_caption', L.get('diagram_caption'))
    print('### worked title', L['worked']['title'])
    for i, s in enumerate(L['worked']['steps']):
        p(f'worked[{i}] say', s['say'])
        if s.get('code'): print('   [code]', s['code'][:400].replace('\n','\n   '), '\n')
    p('mistake', L['mistake'])
    p('real_world', L['real_world'])
    t = L['task']; print('### task', t['title'])
    for i, s in enumerate(t['steps']): p(f'task.step[{i}]', s)
    for i, s in enumerate(t['hints']): p(f'task.hint[{i}]', s)
    p('done_when', t['done_when'])
    p('explain prompt', L['explain_back']['prompt']); p('explain answer', L['explain_back']['answer'])
    for i, r in enumerate(L['recap']): p(f'recap[{i}]', r)
    for i, q in enumerate(L['check']): p(f'check[{i}] Q: {q["q"]} OPTS {q["options"]} ANS {q["answer"]}', q['why'])
    for i, q in enumerate(L['interview']): p(f'interview[{i}] Q: {q["q"]}', q['a'])
    p('deeper', L['deeper']['body'])
