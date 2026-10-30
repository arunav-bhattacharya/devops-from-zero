import json, sys, re
sys.path.insert(0, '/home/user/devops-from-zero/brief')
import validate as V
P = json.load(open(sys.argv[1]))
for L in P['lessons']:
    secs = L['sections']
    tot = sum(V.words(s['body']) for s in secs)
    sents = [x for s in secs for x in V.sentences(s['body'])]
    avg = sum(V.words(x) for x in sents) / len(sents)
    print(L['id'], 'sections', len(secs), 'words', tot, 'avg', round(avg, 1), 'deeper', V.words(L['deeper']['body']),
          'bold', json.dumps(L).count('**') // 2, [V.words(s['body']) for s in secs])
