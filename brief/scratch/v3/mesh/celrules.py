"""Print the CEL rules (x-kubernetes-validations) and string patterns that apply to each
field used in a manifest, so they can be checked by hand (kubeconform skips CEL).
Usage: python3 -I celrules.py CRDS.yaml MANIFEST.yaml [...]"""
import sys
import yaml

crds = {}
for d in yaml.safe_load_all(open(sys.argv[1])):
    if d and d.get("kind") == "CustomResourceDefinition":
        for v in d["spec"]["versions"]:
            crds[(d["spec"]["group"], v["name"], d["spec"]["names"]["kind"])] = v["schema"]["openAPIV3Schema"]


def walk(node, schema, path):
    if not isinstance(schema, dict):
        return
    for r in schema.get("x-kubernetes-validations", []):
        print(f"  {path or '/'}: CEL {r.get('rule')!r}  ({r.get('message', '')})")
    if "pattern" in schema:
        print(f"  {path}: pattern {schema['pattern']!r} value={node!r}")
    if isinstance(node, dict):
        props = schema.get("properties", {})
        for k, v in node.items():
            if k in props:
                walk(v, props[k], f"{path}/{k}")
    elif isinstance(node, list) and "items" in schema:
        for i, v in enumerate(node):
            walk(v, schema["items"], f"{path}[{i}]")


for f in sys.argv[2:]:
    for doc in yaml.safe_load_all(open(f)):
        if not doc:
            continue
        g, _, v = doc["apiVersion"].rpartition("/")
        key = (g, v, doc["kind"])
        if key not in crds:
            continue
        print(f"== {f}: {doc['kind']} {doc['metadata']['name']}")
        walk(doc, crds[key], "")
