"""Replace NAME = \"\"\"...\"\"\" blocks in a lesson script. Usage: patch.py SCRIPT NEWBLOCKS.py"""
import re, sys
src = open(sys.argv[1]).read()
new = open(sys.argv[2]).read()
for m in re.finditer(r'^([A-Z0-9_]+) = """(.*?)"""', new, re.S | re.M):
    name = m.group(1)
    pat = re.compile(r'^' + name + r' = """.*?"""', re.S | re.M)
    assert pat.search(src), name
    src = pat.sub(lambda _: m.group(0), src, count=1)
open(sys.argv[1], "w").write(src)
print("patched")
