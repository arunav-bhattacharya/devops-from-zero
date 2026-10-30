def sub(path, pairs):
    s = open(path).read()
    for a, b in pairs:
        if a not in s:
            raise SystemExit(f"{path}: not found: {a[:70]}")
        s = s.replace(a, b, 1)
    open(path, 'w').write(s)

sub('d31.py', [
    ('''            "options": [
                "`kubectl get pods -n payments`",
                "`kubectl describe nodes`",
                "`kubectl logs payments`",
                "`kind load docker-image payments`",
            ],
            "answer": 0,''',
     '''            "options": [
                "`kubectl describe nodes`",
                "`kubectl logs payments`",
                "`kind load docker-image payments`",
                "`kubectl get pods -n payments`",
            ],
            "answer": 3,'''),
])
sub('d32.py', [
    ('''            "options": [
                "A new revision with the CHANGE-CAUSE `scale`",
                "Ten new revisions, one per Pod",
                "The same revisions as before",
                "Only revision 1, because history resets on scale",
            ],
            "answer": 2,''',
     '''            "options": [
                "The same revisions as before",
                "A new revision with the CHANGE-CAUSE `scale`",
                "Ten new revisions, one per Pod",
                "Only revision 1, because history resets on scale",
            ],
            "answer": 0,'''),
    ('''            "options": [
                "The rollout finishes and every Pod runs the broken version",
                "The rollout stalls after the first Pod, so users are safe",
                "Kubernetes notices the errors and rolls back by itself",
                "The Service skips the new Pods because they return errors",
            ],
            "answer": 0,''',
     '''            "options": [
                "The rollout stalls after the first Pod, so users are safe",
                "Kubernetes notices the errors and rolls back by itself",
                "The rollout finishes and every Pod runs the broken version",
                "The Service skips the new Pods because they return errors",
            ],
            "answer": 2,'''),
])
sub('d33.py', [
    ('''            "options": [
                "kube-proxy runs in iptables mode",
                "The selector does not match the Pod labels",
                "The nodePort is outside 30000 to 32767",
                "CoreDNS is down in kube-system",
            ],
            "answer": 1,''',
     '''            "options": [
                "kube-proxy runs in iptables mode",
                "The nodePort is outside 30000 to 32767",
                "CoreDNS is down in kube-system",
                "The selector does not match the Pod labels",
            ],
            "answer": 3,'''),
])
sub('d34.py', [
    ('''            "options": [
                "Old image with the new ConfigMap data",
                "Old image with the old ConfigMap data",
                "New image with the old ConfigMap data",
                "Nothing, because undo refuses to run",
            ],
            "answer": 0,''',
     '''            "options": [
                "Old image with the old ConfigMap data",
                "New image with the old ConfigMap data",
                "Old image with the new ConfigMap data",
                "Nothing, because undo refuses to run",
            ],
            "answer": 2,'''),
])
print('ok')
