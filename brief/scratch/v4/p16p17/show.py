import json, sys, re
f, lid = sys.argv[1], sys.argv[2]
d = json.load(open(f))
if lid == 'part':
    for k in ['intro','recap','flashcards','resources','quiz']:
        print('==', k); print(json.dumps(d[k], indent=1, ensure_ascii=False))
    sys.exit()
L = [l for l in d['lessons'] if l['id'] == lid][0]
def p(k, v): print(f"\n### {k}\n{v}")
p('title', L['title']); p('goal', L['goal'])
p('guess', json.dumps(L['guess'], indent=1, ensure_ascii=False))
for t in L['terms']: print(f"- {t['term']}: {t['plain']}")
wc = 0
for i, s in enumerate(L['sections']):
    wc += len(s['body'].split())
    p(f"S{i} {s['h']}", s['body'])
print("\nSECTION WORDS", wc)
p('analogy', L['analogy']); p('diagram_caption', L['diagram_caption'])
p('worked', L['worked']['title'])
for s in L['worked']['steps']:
    print('SAY:', s['say']); 
    if s.get('code'): print('CODE:\n' + s['code'])
p('code', '\n'.join(c['title'] + ' | ' + c.get('run','') for c in L['code']))
for c in L['code']: print('----', c['title']); print(c['src'])
p('commands', '\n'.join(c['cmd'] + ' :: ' + c['what'] for c in L['commands']))
p('mistake', L['mistake']); p('real_world', L['real_world'])
p('task', json.dumps(L['task'], indent=1, ensure_ascii=False))
p('explain_back', json.dumps(L['explain_back'], indent=1, ensure_ascii=False))
p('recap', '\n'.join(L['recap']))
p('check', json.dumps(L['check'], indent=1, ensure_ascii=False))
p('interview', json.dumps(L['interview'], indent=1, ensure_ascii=False))
p('deeper', L['deeper']['body'])
