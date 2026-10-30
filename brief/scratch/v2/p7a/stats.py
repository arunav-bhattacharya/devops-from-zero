import json, sys, importlib.util
spec = importlib.util.spec_from_file_location('v', '/home/user/devops-from-zero/brief/validate.py')
v = importlib.util.module_from_spec(spec); spec.loader.exec_module(v)
P = json.load(open('/home/user/devops-from-zero/brief/scratch/v2/p7a/p7-full.json'))
lim = int(sys.argv[1]) if len(sys.argv) > 1 else 24
for L in P['lessons']:
    secs = L['sections']
    tot = sum(v.words(s['body']) for s in secs)
    sents = [x for s in secs for x in v.sentences(s['body'])]
    avg = sum(v.words(x) for x in sents)/len(sents)
    print(L['id'], 'sections', tot, [v.words(s['body']) for s in secs], 'avg', round(avg,1), 'deeper', v.words(L['deeper']['body']))
    blob = json.dumps(L, ensure_ascii=False)
    print('  bold', blob.count('**')//2, 'answers', L['guess']['answer'], [q['answer'] for q in L['check']])
    for x in sents:
        if v.words(x) > lim: print('   long', v.words(x), x[:120])
