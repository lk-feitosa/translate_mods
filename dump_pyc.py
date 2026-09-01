import marshal, types, sys, struct

def strings(co, seen, out):
    if co in seen:
        return out
    seen.add(co)
    for c in co.co_consts:
        if isinstance(c, str):
            out.append(c)
        elif isinstance(c, types.CodeType):
            strings(c, seen, out)
    return out

for name in sys.argv[1:]:
    with open(f'recovered/{name}.cpython-314.pyc', 'rb') as f:
        data = f.read()
    # pyc: 4 magic + 4 flags + 4 mtime + 4 size = 16-byte header (py3.7+, and py3.14)
    co = marshal.loads(data[16:])
    print(f"\n########## {name} ##########")
    ss = strings(co, set(), [])
    print("TOTAL STRINGS:", len(ss))
    for s in ss:
        print(repr(s))