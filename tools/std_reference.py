#!/usr/bin/env python3
"""Writes docs/std-reference.md from src/std/ (run from the repository: tools/std_reference.py).

Every module a program can import, with what it makes public: its types (and their members, which are
as visible as their type), functions, constants and variables, each with the comment above it. The parts
of std for std itself (posix, windows, macos, common, internal; and tasks, which the compiler writes) are
left out: a program does not import them.
"""
import os, re, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from reference import strip_strings, doc_above, signature  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STD = 'src/std' if os.path.isdir(os.path.join(ROOT, 'src/std')) else 'std'
OWN = {'posix', 'windows', 'macos', 'common', 'internal'}

TYPE_RE = re.compile(r'^public\s+(synchronized\s+)?(class|interface|struct|enum|type|native\s+type|native\s+interface)\s+(\w+)([^{;]*)')
FUNC_RE = re.compile(r'^((?:public|override|static|native|synchronized)\s+)*(function|operator)\b')
MEMBER_LET_RE = re.compile(r'^(?:native\s+)?let\s+(\w+)\s*:\s*([^=;]+)')
TOP_VALUE_RE = re.compile(r'^public\s+(const|let)\s+(\w+)\s*:\s*([^=;]+)')


def modules():
    out = []
    for dirpath, _, names in os.walk(os.path.join(ROOT, STD)):
        for n in names:
            if not n.endswith('.lar'):
                continue
            rel = os.path.relpath(os.path.join(dirpath, n), ROOT)
            path = 'std.' + rel[len(STD) + 1:-len('.lar')].replace('/', '.')
            parts = path.split('.')
            if OWN & set(parts) or path == 'std.os.process.tasks':
                continue
            out.append((path, rel))
    return sorted(out)


def read(rel):
    lines = open(os.path.join(ROOT, rel)).read().split('\n')
    head = []
    for l in lines:
        if l.startswith('//'):
            head.append(l[3:].rstrip() if l.startswith('// ') else l[2:].rstrip())
        else:
            break
    entries = []          # (kind, text, doc, inside)
    depth = 0
    in_text = False
    in_type = False        # inside a public type: its members are listed
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
        if stripped.startswith(('ccode', 'native function', 'native type', 'native struct', 'native const', 'native let')) and depth == 0 and not stripped.startswith('public'):
            pass
        if depth == 0:
            t = TYPE_RE.match(stripped)
            f = FUNC_RE.match(stripped)
            v = TOP_VALUE_RE.match(stripped)
            if t:
                kind = ' '.join((t.group(1) or '').split() + t.group(2).split())
                rest = ' '.join(t.group(4).split())
                parent = re.match(r'extends\s+(\w+)', rest)
                if parent and parent.group(1) in INHERITED:
                    rest = re.sub(r'extends\s+\w+\s*', '', rest).strip()      # a part of std's own: its members are listed here
                entries.append(('type', f"{kind} `{t.group(3)}{(' ' + rest) if rest else ''}`", doc_above(lines, i), False))
                in_type = '{' in bare and '}' not in bare[bare.index('{'):]
                if parent and parent.group(1) in INHERITED:
                    entries.extend(INHERITED[parent.group(1)])
            elif f and stripped.startswith('public'):
                entries.append(('func', signature(stripped)[len('public '):], doc_above(lines, i), False))
            elif v:
                entries.append(('value', f"{v.group(1)} {v.group(2)}: {v.group(3).strip()}", doc_above(lines, i), False))
        elif in_type and depth == 1:
            f = FUNC_RE.match(stripped)
            m = MEMBER_LET_RE.match(stripped)
            if f and not stripped.startswith('native function lar_'):
                entries.append(('func', signature(stripped), doc_above(lines, i), True))
            elif m and not m.group(1).startswith('_'):
                entries.append(('value', f"{m.group(1)}: {m.group(2).strip()}", doc_above(lines, i), True))
        depth += bare.count('{') - bare.count('}')
        if depth <= 0:
            depth = 0
            in_type = False
    return head, entries


def anchor(path):
    return path.replace('.', '')


# The public classes of std's own parts that a public class extends (std.os.process.internal's Child): their
# members are listed in the class that extends them, as a program sees them.
INHERITED = {}


def own_classes():
    for dirpath, _, names in os.walk(os.path.join(ROOT, STD)):
        for n in names:
            rel = os.path.relpath(os.path.join(dirpath, n), ROOT)
            parts = set(rel[len(STD) + 1:-len('.lar')].split('/'))
            if not n.endswith('.lar') or not (OWN & parts):
                continue
            head, entries = read(rel)
            current = None
            for kind, text, doc, inside in entries:
                if kind == 'type':
                    m = re.match(r'class `(\w+)', text)
                    current = m.group(1) if m else None
                    if current:
                        INHERITED[current] = []
                elif inside and current:
                    INHERITED[current].append((kind, text, doc, inside))


def main():
    own_classes()
    mods = [(path, rel) + read(rel) for path, rel in modules()]
    names = sum(1 for m in mods for e in m[3] if not e[3])
    out = ['# The standard library: reference\n']
    out.append('Every module of `std` a program can import, and everything it makes public: types (with their '
               'members, as visible as their type), functions, constants and variables, as they are in the code, '
               'with the comment above each one.\n')
    out.append('> This file is **generated** from `src/std/` with `tools/std_reference.py`; it is not edited by hand. '
               'The [manual](manual.md#25-standard-library) explains the library with examples. The parts of std for '
               'std itself (`*.posix`, `*.windows`, `*.macos`, `*.common`, `*.internal`) are not here: a program '
               'cannot import them.\n')
    out.append(f'**{len(mods)} modules, {names} public names.**\n')
    out.append('## Modules\n')
    for path, rel, head, entries in mods:
        first = next((h for h in head if h.strip()), '')
        first = re.sub(r'^std\.[\w.]+:\s*', '', first)
        out.append(f'- [`{path}`](#{anchor(path)}): {first}')
    out.append('\n---\n')
    for path, rel, head, entries in mods:
        out.append(f'## {path}\n')
        if head:
            text = '\n'.join(head).strip('\n')
            text = re.sub(r'^std\.[\w.]+:\s*', '', text)
            out.append('```\n' + text + '\n```' if '\n  ' in text or 'import ' in text else text)
        out.append(f'\n`{rel}`\n')
        for kind, text, doc, inside in entries:
            if kind == 'type':
                out.append(f'### {text}')
                if doc:
                    out.append(doc)
                out.append('')
                continue
            bullet = '- ' if inside else ''
            out.append(f'{bullet}`{text}`' + ('  ' if doc else ''))
            if doc:
                out.append(('  ' if inside else '') + doc)
            out.append('')
        out.append('---\n')
    open(os.path.join(ROOT, 'docs/std-reference.md'), 'w').write('\n'.join(out).rstrip('-\n') + '\n')
    print(f'{len(mods)} modules, {names} public names')


if __name__ == '__main__':
    main()
