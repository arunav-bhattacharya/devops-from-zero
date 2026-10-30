"""Turn CRD YAML files into JSON schemas that kubeconform can read.
Usage: python3 -I crd2schema.py OUT_DIR crd1.yaml [crd2.yaml ...]
Writes OUT_DIR/<group>/<kind>_<version>.json (kind lowercased)."""
import json
import pathlib
import sys

import yaml


def strict(node):
    # kubeconform -strict expects additionalProperties: false on objects with fixed properties.
    if isinstance(node, dict):
        if "properties" in node and "additionalProperties" not in node and not node.get("x-kubernetes-preserve-unknown-fields"):
            node["additionalProperties"] = False
        for v in node.values():
            strict(v)
    elif isinstance(node, list):
        for v in node:
            strict(v)


out = pathlib.Path(sys.argv[1])
for f in sys.argv[2:]:
    for doc in yaml.safe_load_all(pathlib.Path(f).read_text()):
        if not doc or doc.get("kind") != "CustomResourceDefinition":
            continue
        spec = doc["spec"]
        group, kind = spec["group"], spec["names"]["kind"].lower()
        for ver in spec["versions"]:
            schema = ver.get("schema", {}).get("openAPIV3Schema")
            if not schema:
                continue
            strict(schema)
            p = out / group / f"{kind}_{ver['name']}.json"
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(json.dumps(schema))
            print(p)
