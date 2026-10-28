#!/usr/bin/env python3
"""larimar check and larimar lsp, end to end: python3 tests/lsp/lsp_test.py <larimarc>"""
import json, os, subprocess, sys, time

EXE = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else "larimarc")
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "project")
MAIN = os.path.join(ROOT, "src", "main.lar")
SHAPES = os.path.join(ROOT, "src", "geo", "shapes.lar")
EXTRA = os.path.join(ROOT, "src", "extra.lar")
failures = []

def check(name, ok, got=None):
    if ok:
        print("  ok    lsp: " + name)
    else:
        failures.append(name)
        print("  FAIL  lsp: " + name + ("\n        got: " + json.dumps(got, ensure_ascii=False)[:500] if got is not None else ""))

# ---- larimar check --json ----
out = subprocess.run([EXE, "check", ROOT, "--json"], capture_output=True, text=True)
errs = json.loads(out.stdout or "[]")
check("check --json finds the error", out.returncode == 1 and len(errs) == 1 and errs[0]["line"] == 14 and errs[0]["file"].endswith("main.lar"), errs)
out = subprocess.run([EXE, "check", SHAPES], capture_output=True, text=True)
check("check of a file without errors", out.returncode == 0, out.stderr)

# ---- the server ----
def run(env_extra):
    env = dict(os.environ, **env_extra)
    p = subprocess.Popen([EXE, "lsp"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, env=env)
    notes = []
    def send(o):
        b = json.dumps(o).encode()
        p.stdin.write(b"Content-Length: %d\r\n\r\n" % len(b) + b)
        p.stdin.flush()
    def recv():
        n = None
        while True:
            l = p.stdout.readline()
            if not l:
                return None
            l = l.strip()
            if not l:
                break
            if l.lower().startswith(b"content-length"):
                n = int(l.split(b":")[1])
        return json.loads(p.stdout.read(n))
    ids = [0]
    def req(method, params):
        ids[0] += 1
        send({"jsonrpc": "2.0", "id": ids[0], "method": method, "params": params})
        while True:
            m = recv()
            if m is None:
                return None
            if m.get("id") == ids[0]:
                return m.get("result")
            notes.append(m)
    def uri(path): return "file://" + path
    def at(path, line, ch): return {"textDocument": {"uri": uri(path)}, "position": {"line": line, "character": ch}}
    def change(path, text, v):
        send({"jsonrpc": "2.0", "method": "textDocument/didChange", "params": {"textDocument": {"uri": uri(path), "version": v}, "contentChanges": [{"text": text}]}})

    caps = req("initialize", {"processId": None, "capabilities": {}})
    check("initialize", caps and caps["capabilities"].get("hoverProvider") is True, caps)
    send({"jsonrpc": "2.0", "method": "initialized", "params": {}})
    text = open(MAIN).read()
    send({"jsonrpc": "2.0", "method": "textDocument/didOpen", "params": {"textDocument": {"uri": uri(MAIN), "languageId": "larimar", "version": 1, "text": text}}})
    time.sleep(1.0)
    req("textDocument/hover", at(MAIN, 0, 0))          # the errors arrive before this answer
    diag = {n["params"]["uri"]: n["params"]["diagnostics"] for n in notes if n.get("method") == "textDocument/publishDiagnostics"}
    d = diag.get(uri(MAIN), [])
    check("errors published", len(d) == 1 and d[0]["range"]["start"]["line"] == 13 and "expected int32" in d[0]["message"], diag)
    check("other files cleared", diag.get(uri(SHAPES)) == [], diag)

    h = req("textDocument/hover", at(MAIN, 12, 14))
    check("hover function + comment", h and "function greet(name: String, times: int32): String" in h["contents"]["value"] and "Greets someone." in h["contents"]["value"], h)
    h = req("textDocument/hover", at(MAIN, 11, 18))
    check("hover method of another module", h and "norm(): float64" in h["contents"]["value"] and "Distance to the origin." in h["contents"]["value"], h)
    h = req("textDocument/hover", at(MAIN, 11, 35))
    check("hover module.function", h and "area(side: float64)" in h["contents"]["value"], h)
    h = req("textDocument/hover", at(MAIN, 10, 12))
    check("hover struct", h and "let x: float64;" in h["contents"]["value"], h)
    h = req("textDocument/hover", at(MAIN, 6, 17))
    check("hover String method", h and "repeat(n: int32): String" in h["contents"]["value"], h)

    r = req("textDocument/definition", at(MAIN, 11, 18))
    check("definition in another file", r and r["uri"] == uri(SHAPES) and r["range"]["start"]["line"] == 5, r)
    r = req("textDocument/definition", at(MAIN, 6, 12))
    check("definition of a local", r and r["range"]["start"] == {"line": 5, "character": 8}, r)
    r = req("textDocument/references", dict(at(SHAPES, 1, 15), context={"includeDeclaration": True}))
    check("references of a type", r is not None and len(r) == 4, r)
    r = req("textDocument/documentSymbol", {"textDocument": {"uri": uri(SHAPES)}})
    check("symbols with members", r and r[0]["name"] == "Point" and [c["name"] for c in r[0]["children"]] == ["x", "y", "norm"], r)

    lines = text.split("\n")
    def complete(line, label):
        lines[13] = line
        change(MAIN, "\n".join(lines), 10 + len(label))
        return req("textDocument/completion", at(MAIN, 13, len(line)))
    r = complete("    p.", "p.")
    check("completion of fields and methods", r and [i["label"] for i in r["items"]] == ["x", "y", "norm"], r)
    r = complete("    shapes.", "shapes.")
    check("completion of a module", r and sorted(i["label"] for i in r["items"]) == ["Point", "area"], r)
    r = complete("    gre", "gre")
    check("completion of names", r and [i["label"] for i in r["items"]] == ["greet"], r)
    lines[13] = "    greet(\"a\", "
    change(MAIN, "\n".join(lines), 50)
    r = req("textDocument/signatureHelp", at(MAIN, 13, len(lines[13])))
    check("signature help", r and r["activeParameter"] == 1 and r["signatures"][0]["label"].startswith("greet("), r)

    send({"jsonrpc": "2.0", "method": "textDocument/didOpen", "params": {"textDocument": {"uri": uri(EXTRA), "languageId": "larimar", "version": 1, "text": open(EXTRA).read()}}})
    h = req("textDocument/hover", at(EXTRA, 2, 31))
    check("a file the project does not import; UTF-16 columns", h and "let ñandú: int32" in h["contents"]["value"] and h["range"]["start"]["character"] == 29, h)

    check("shutdown", req("shutdown", None) is None)
    send({"jsonrpc": "2.0", "method": "exit"})
    check("exit code 0", p.wait(10) == 0)

run({})
if os.name != "nt":
    print("  (without fork: lsp-worker)")
    if os.path.basename(EXE) == "larimarc":
        run({"LARIMAR_LSP_NO_FORK": "1"})

print("")
print("lsp: %d failed" % len(failures))
sys.exit(1 if failures else 0)
