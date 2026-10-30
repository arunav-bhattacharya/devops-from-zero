import json, re, sys
sys.path.insert(0, '/home/user/devops-from-zero/brief')
import importlib.util
spec = importlib.util.spec_from_file_location('v', '/home/user/devops-from-zero/brief/validate.py')
v = importlib.util.module_from_spec(spec); spec.loader.exec_module(v)
P = json.load(open('/home/user/devops-from-zero/content/p4.json'))
for L in P['lessons']:
    secs = L['sections']
    tot = sum(v.words(s['body']) for s in secs)
    sents = [x for s in secs for x in v.sentences(s['body'])]
    avg = sum(v.words(x) for x in sents)/len(sents)
    long = [x for x in sents if v.words(x) > 22]
    print(L['id'], 'section words', tot, [v.words(s['body']) for s in secs], 'avg', round(avg,1), 'deeper', v.words(L['deeper']['body']))
    blob = json.dumps(L, ensure_ascii=False)
    print('  bold', blob.count('**')//2, 'answers', [q['answer'] for q in L['check']], L['guess']['answer'])
    for x in long: print('   long', v.words(x), x[:110])
