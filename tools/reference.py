#!/usr/bin/env python3
"""Writes docs/compiler-reference.md from the comments of the compiler's sources, and the generated part of
the README.md of each folder of the compiler and of std (its micro API: the public names of each module).

    tools/reference.py            writes them
    tools/reference.py --check    says which README.md does not match the code (exit 1), and writes nothing
"""
import os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = 'src/compiler' if os.path.isdir(os.path.join(ROOT, 'src/compiler')) else 'src'
STD = 'src/std' if os.path.isdir(os.path.join(ROOT, 'src/std')) else 'std'
GROUPS = ['main', 'pipeline', 'syntax', 'semantics', 'codegen', 'project', 'editor']
FOLDERS = ['syntax', 'semantics', 'codegen', 'project', 'editor']
BEGIN = '<!-- api: written by tools/reference.py from the code; not edited by hand -->'
END = '<!-- /api -->'


def files(base=None):
    base = base or SRC
    out = []
    for dirpath, _, names in os.walk(os.path.join(ROOT, base)):
        for n in names:
            if n.endswith('.lar'):
                rel = os.path.relpath(os.path.join(dirpath, n), ROOT)
                out.append(rel)
    def key(rel):
        parts = rel[len(base) + 1:-len('.lar')].split('/')
        return (GROUPS.index(parts[0]) if parts[0] in GROUPS else 99, parts)
    return sorted(out, key=key)


def strip_strings(line):
    """The line without its string and character literals (their braces do not count)."""
    out, i = [], 0
    while i < len(line):
        c = line[i]
        if line.startswith('//', i):
            break
        if c == '"' or c == "'":
            q = c
            i += 1
            while i < len(line) and line[i] != q:
                if line[i] == '\\':
                    i += 1
                i += 1
            i += 1
            continue
        out.append(c)
        i += 1
    return ''.join(out)


def doc_above(lines, i):
    """The comment right above line i: a /** */ block, or // lines."""
    j = i - 1
    if j >= 0 and lines[j].strip().endswith('*/'):
        block = []
        while j >= 0:
            block.insert(0, lines[j].strip())
            if lines[j].strip().startswith('/**') or lines[j].strip().startswith('/*'):
                break
            j -= 1
        text = ' '.join(block)
        text = re.sub(r'^/\*\*?', '', text)
        text = re.sub(r'\*/$', '', text)
        text = ' '.join(t.lstrip('*').strip() for t in text.split(' * '))
        return ' '.join(text.split())
    block = []
    while j >= 0 and lines[j].strip().startswith('//'):
        block.insert(0, lines[j].strip()[2:].strip())
        j -= 1
    return ' '.join(' '.join(block).split())


TYPE_RE = re.compile(r'^(public\s+)?(synchronized\s+)?(class|interface|struct|enum)\s+(\w+)([^{]*)')
FUNC_RE = re.compile(r'^((?:public|override|static|native|test|synchronized)\s+)*(function|operator)\b')


def signature(text):
    text = text.strip()
    depth = 0
    for k, c in enumerate(text):
        if c == '(':
            depth += 1
        elif c == ')':
            depth -= 1
        elif depth == 0 and (c == '{' or c == ';'):
            return text[:k].strip()
        elif depth == 0 and text.startswith('= ', k):
            return text[:k].strip()
    return text.rstrip('{; ').strip()


def module(rel):
    src = open(os.path.join(ROOT, rel)).read()
    lines = src.split('\n')
    head = []
    for l in lines:
        if l.startswith('//'):
            head.append(l[2:].strip())
        else:
            break
    entries = []        # (kind, text, doc, line, inType)
    depth = 0
    in_text = False
    in_type = None
    type_depth = 0
    count = 0
    for i, line in enumerate(lines):
        stripped = line.strip()
        if '"""' in line:
            if line.count('"""') % 2 == 1:
                in_text = not in_text
            if in_text:
                continue
        if in_text:
            continue
        bare = strip_strings(line)
        if depth == 0 or (in_type is not None and depth == type_depth + 1):
            t = TYPE_RE.match(stripped)
            f = FUNC_RE.match(stripped)
            nt = re.match(r'^(public\s+)?native\s+type\s+(\w+)(.*)', stripped)
            if depth == 0 and t:
                kind = ('synchronized class' if t.group(2) else t.group(3))
                rest = ' '.join(t.group(5).split())
                entries.append(('type', f"{kind} `{t.group(4)}{(' ' + rest) if rest else ''}`", doc_above(lines, i), i + 1, False))
                if '{' in bare and '}' not in bare[bare.index('{'):]:
                    in_type = t.group(4)
                    type_depth = 0
            elif depth == 0 and nt and '{' in bare:
                entries.append(('type', f"native type `{nt.group(2)}`", doc_above(lines, i), i + 1, False))
                in_type = nt.group(2)
                type_depth = 0
            elif f:
                sig = signature(stripped)
                inside = depth > 0
                entries.append(('func', sig, doc_above(lines, i), i + 1, inside))
                count += 1
            elif depth == 0 and stripped.startswith(('let ', 'public let ', 'const ', 'public const ')):
                pass
        depth += bare.count('{') - bare.count('}')
        if depth <= 0:
            depth = 0
            if in_type is not None and '}' in bare:
                in_type = None
    return head, entries, count, len(lines)


def anchor(rel):
    return rel[len(SRC) + 1:-len('.lar')].replace('/', '-')


def title(rel):
    return rel[len(SRC) + 1:-len('.lar')].replace('/', '.')


def module_name(rel, base):
    name = rel[len(base) + 1:-len('.lar')].replace('/', '.')
    return ('std.' + name) if base == STD else name


def public_api(rel, base):
    """The public names of a module: its first line of comment, and each public type and function (its signature, its doc's first sentence)."""
    src = open(os.path.join(ROOT, rel)).read()
    head, entries, count, n = module(rel)
    lines = src.split('\n')
    out = []
    first = ''
    if head:
        first = ' '.join(head).split('. ')[0].strip()
        first = re.sub(r'^[\w.]+:\s*', '', first)
    out.append(f'- **`{module_name(rel, base)}`**' + (f': {first}' if first else ''))
    for kind, text, doc, line, inside in entries:
        decl = lines[line - 1].strip()
        if inside or not decl.startswith('public'):
            continue
        short = doc.split('. ')[0].rstrip('.') if doc else ''
        sig = text if kind == 'func' else text.replace('`', '')
        sig = sig.replace('public ', '')
        out.append(f'  - `{sig}`' + (f': {short}' if short else ''))
    return out


def readme_api(folder, base):
    path = os.path.join(base, folder) if folder else base
    mods = [rel for rel in files(base) if rel.startswith(path + '/') or rel == path + '.lar']
    if folder:
        own = os.path.join(base, folder + '.lar')
        if os.path.isfile(os.path.join(ROOT, own)):
            mods = [own] + [m for m in mods if m != own]
    out = []
    for rel in mods:
        if '/internal/' in rel or rel.endswith('/internal.lar'):
            continue
        out.extend(public_api(rel, base))
    return '\n'.join(out)


def readmes():
    """(README path, its generated part) for each folder of the compiler, and for std."""
    done = []
    for folder in FOLDERS:
        done.append((os.path.join(SRC, folder, 'README.md'), readme_api(folder, SRC)))
    std_mods = [rel for rel in files(STD) if not re.search(r'/(posix|windows|macos|common|internal)(/|\.lar$)', rel)]
    lines = []
    for rel in std_mods:
        lines.extend(public_api(rel, STD))
    done.append((os.path.join(STD, 'README.md'), '\n'.join(lines)))
    return done


def with_api(text, api):
    if BEGIN in text and END in text:
        a = text.index(BEGIN)
        b = text.index(END) + len(END)
        return text[:a] + BEGIN + '\n\n' + api + '\n\n' + END + text[b:]
    return text.rstrip('\n') + '\n\n## Its API\n\n' + BEGIN + '\n\n' + api + '\n\n' + END + '\n'


def write_readmes(check):
    wrong = []
    for path, api in readmes():
        full = os.path.join(ROOT, path)
        old = open(full).read() if os.path.isfile(full) else ''
        new = with_api(old, api)
        if new != old:
            if check:
                wrong.append(path)
            else:
                open(full, 'w').write(new)
    return wrong


def main():
    if '--check' in sys.argv:
        wrong = write_readmes(True)
        for w in wrong:
            print(f'{w}: its API part does not match the code (tools/reference.py writes it)')
        sys.exit(1 if wrong else 0)
    write_readmes(False)
    mods = [(rel,) + module(rel) for rel in files()]
    total = sum(m[3] for m in mods)
    documented = sum(1 for m in mods for e in m[2] if e[0] == 'func' and e[2])
    out = []
    out.append('# El compilador de Larimar: referencia de funciones\n')
    out.append('Cada módulo de `src/`, con su descripción y **todas** sus funciones, clases y métodos: la firma tal como está en el código y el comentario que la acompaña.\n')
    out.append('> Este archivo se **genera** a partir del código (`/** ... */` y `//` encima de cada declaración) con `tools/reference.py`. No se edita a mano: si una descripción falta o está mal, se corrige el comentario en el código. Las descripciones están en inglés, como en el código. Una entrada sin texto es una función sin comentario.\n')
    out.append('Para la visión de conjunto (fases, datos que pasan de una a otra, recetas), ver la guía de mantenimiento. Aquí está el detalle.\n')
    out.append(f'**{len(mods)} módulos, {total} funciones y métodos** ({documented} con comentario, {total - documented} sin él).\n')
    out.append('## Módulos\n')
    for rel, head, entries, count, n in mods:
        out.append(f'- [`{rel}`](#{anchor(rel)}) — {count} funciones')
    out.append('\n---\n')
    for rel, head, entries, count, n in mods:
        out.append(f'## {title(rel)}\n')
        out.append(f'`{rel}` · {n} líneas · {count} funciones')
        if head:
            out.append('\n'.join(head).strip('\n'))
        out.append('')
        for kind, text, doc, line, inside in entries:
            if kind == 'type':
                out.append(f'### {text}')
                if doc:
                    out.append(doc)
                out.append('')
                continue
            if inside:
                out.append(f'- `{text}`  ' if doc else f'- `{text}`')
                if doc:
                    out.append(f'  {doc}  ')
                out.append(f'  <sub>línea {line}</sub>\n')
            else:
                out.append(f'`{text}`  ' if doc else f'`{text}`')
                if doc:
                    out.append(f'{doc}  ')
                out.append(f'<sub>línea {line}</sub>\n')
        out.append('---\n')
    open(os.path.join(ROOT, 'docs/compiler-reference.md'), 'w').write('\n'.join(out).rstrip('-\n') + '\n')
    print(f'{len(mods)} modules, {total} functions ({documented} documented)')


if __name__ == '__main__':
    main()
