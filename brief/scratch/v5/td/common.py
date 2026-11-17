"""Shared helpers for td's fifth-pass rewrites: start each lesson from the original, then save."""
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[4]


def load(part, lid):
    path = ROOT / f"content/p{part}.json"
    P = json.loads(path.read_text())
    orig = json.loads((ROOT / f"brief/scratch/v5/orig/p{part}.json").read_text())
    i = next(i for i, x in enumerate(P["lessons"]) if x["id"] == lid)
    P["lessons"][i] = next(x for x in orig["lessons"] if x["id"] == lid)  # start from the original each run
    return path, P, P["lessons"][i]


def save(path, P):
    path.write_text(json.dumps(P, indent=1, ensure_ascii=False) + "\n")


def set_list(items, key, values):
    assert len(items) == len(values), (key, len(items), len(values))
    for it, v in zip(items, values):
        it[key] = v


def drop_extras(L):
    for k in ("analogy", "mistake", "real_world"):
        L.pop(k, None)
