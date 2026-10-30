#!/usr/bin/env python3
"""larimar --debug with a real debugger: python3 tests/debug/debug_test.py <larimarc> [cc]

Builds values.lar with #line to the .lar file, stops on the line marked "// break here" and checks
that Larimar's formatters (debug/larimar_lldb.py, debug/larimar_gdb.py) show the values as Larimar
values, with lldb and gdb (whichever are installed). Then, with lldb-dap, talks to larimar dap (the
debugger written in Larimar) like an editor: Larimar names in the stack and the variables, values,
children, Larimar paths in evaluate, and a panic shown as an exception with its message."""
import json, os, shutil, subprocess, sys, tempfile, threading

HERE = os.path.dirname(os.path.abspath(__file__))
def default_compiler(root):
    """larimarc where build-bootstrap.sh leaves it: ../out/larimar/bin, bin/, or the repository's root."""
    for p in (os.path.join(root, "..", "out", "larimar", "bin", "larimarc"), os.path.join(root, "bin", "larimarc"),
              os.path.join(root, "larimarc")):
        if os.path.exists(p) or os.path.exists(p + ".exe"):
            return p
    return os.path.join(root, "larimarc")

ROOT = os.path.dirname(os.path.dirname(HERE))
EXE = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else default_compiler(ROOT))
CC = sys.argv[2] if len(sys.argv) > 2 else os.environ.get("CC", "cc")
SRC = os.path.join(HERE, "values.lar")
LINE = next(i + 1 for i, l in enumerate(open(SRC, encoding="utf-8")) if "// break here" in l)

EXPECT = [                       # (variable, text its value must contain)
    ("name", '"Larimar '),
    ("maybe", "7"),
    ("nothing", "null"),
    ("a", 'Dog {name="Rex", age=3, breed="mutt"}'),
    ("list", '[3] ["a", "b", "c"]'),
    ("nums", "[3] [1, 2, 3]"),
    ("shape", "Circle(r=1.5)"),
    ("data", "{ 2 items, 2 entries }"),
    ("pet", 'Cat {n="tom"}'),
    ("total", "3"),
]

failures = []


def check(name, ok, got=""):
    print("  %s  debug: %s" % ("ok  " if ok else "FAIL", name))
    if not ok:
        failures.append(name)
        if got:
            print("        " + got.replace("\n", "\n        ")[:3000])


def find_lldb_dap():
    for name in ("lldb-dap", "lldb-dap-20", "lldb-dap-19", "lldb-dap-18", "lldb-vscode"):
        if shutil.which(name):
            return name
    try:
        found = subprocess.run(["xcrun", "--find", "lldb-dap"], capture_output=True, text=True).stdout.strip()
        return found if found and os.path.exists(found) else None
    except OSError:
        return None


class Dap:
    def __init__(self, env, backend):
        self.p = subprocess.Popen([EXE, "dap", "--backend", backend], stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                  stderr=subprocess.DEVNULL, env=env)
        self.seq = 0

    def send(self, cmd, args=None):
        self.seq += 1
        b = json.dumps({"seq": self.seq, "type": "request", "command": cmd, "arguments": args or {}}).encode()
        self.p.stdin.write(b"Content-Length: %d\r\n\r\n" % len(b) + b)
        self.p.stdin.flush()
        return self.seq

    def recv(self):
        n = None
        while True:
            line = self.p.stdout.readline()
            if not line:
                raise RuntimeError("larimar dap ended")
            line = line.strip()
            if not line:
                break
            if line.lower().startswith(b"content-length"):
                n = int(line.split(b":")[1])
        return json.loads(self.p.stdout.read(n))

    def wait(self, pred, seconds=30):
        """The next message that pred accepts; a test fails (it does not hang) after seconds without it."""
        timer = threading.Timer(seconds, self.p.kill)
        timer.start()
        try:
            while True:
                m = self.recv()
                if pred(m):
                    return m
        except RuntimeError:
            if not timer.is_alive():
                raise RuntimeError("no answer from larimar dap in %d seconds" % seconds)
            raise
        finally:
            timer.cancel()

    def req(self, cmd, args=None):
        s = self.send(cmd, args)
        return self.wait(lambda m: m.get("type") == "response" and m.get("request_seq") == s)

    def stopped(self):
        m = self.wait(lambda m: m.get("event") in ("stopped", "terminated", "exited"))
        if m.get("event") != "stopped":
            raise RuntimeError("the program ended without stopping at the breakpoint")
        return m

    def frames(self, tid):
        return self.req("stackTrace", {"threadId": tid})["body"]["stackFrames"]

    def locals(self, frame):
        sc = self.req("scopes", {"frameId": frame})["body"]["scopes"]
        return self.req("variables", {"variablesReference": sc[0]["variablesReference"]})["body"]["variables"]

    def close(self):
        try:
            self.req("disconnect", {"terminateDebuggee": True})
            return self.p.wait(15)
        except Exception:
            self.p.kill()
            return -1


def dap_tests(env, prog, c_file):
    backend = find_lldb_dap()
    if not backend:
        print("  skip  debug: larimar dap (no lldb-dap)")
        return
    debug_map = c_file[:-2] + ".debug.json"
    check("debug map written", os.path.exists(debug_map))
    d = Dap(env, backend)
    try:
        caps = d.req("initialize", {"adapterID": "larimar", "linesStartAt1": True, "columnsStartAt1": True})["body"]
        check("dap: panic filter", any(f["filter"] == "panic" for f in caps.get("exceptionBreakpointFilters", [])))
        d.send("launch", {"program": prog, "debugMap": debug_map})
        d.wait(lambda m: m.get("event") == "initialized")
        bp = d.req("setBreakpoints", {"source": {"path": SRC}, "breakpoints": [{"line": LINE}]})["body"]["breakpoints"]
        check("dap: breakpoint in the .lar", bp and bp[0].get("verified"))
        fb = d.req("setFunctionBreakpoints", {"breakpoints": [{"name": "describe"}]})["body"]["breakpoints"]
        check("dap: function breakpoint by Larimar name", fb and fb[0].get("verified"))
        d.req("configurationDone")
        tid = d.stopped()["body"]["threadId"]
        frames = d.frames(tid)
        check("dap: stack with Larimar names", frames[0]["name"] == "main" and frames[0]["line"] == LINE, frames[:2])
        vs = {v["name"]: v for v in d.locals(frames[0]["id"])}
        for name, want in EXPECT:
            got = vs.get(name, {}).get("value", "")
            check("dap shows %s" % name, want in got, "%s = %s" % (name, got))
        check("dap: no temporaries", not any(n.startswith("t_") or n.startswith("tmp_") for n in vs), list(vs))
        kids = d.req("variables", {"variablesReference": vs["a"]["variablesReference"]})["body"]["variables"]
        check("dap: fields of the real class", [k["name"] for k in kids] == ["name", "age", "breed"], kids)
        for expr, want in (("a.name", '"Rex"'), ("list[1]", '"b"'), ("pts[1].y", "4"), ("nums.length", "3")):
            r = d.req("evaluate", {"expression": expr, "frameId": frames[0]["id"], "context": "watch"})
            check("dap: evaluate %s" % expr, r.get("body", {}).get("result") == want, r)
        d.req("continue", {"threadId": tid})
        d.stopped()
        frames = d.frames(tid)
        check("dap: stops in describe", frames[0]["name"] == "describe", frames[:2])
        vs = {v["name"]: v["value"] for v in d.locals(frames[0]["id"])}
        check("dap: parameter s", vs.get("s") == "Circle(r=1.5)", vs)
    finally:
        check("dap: ends", d.close() == 0)

    # a panic: an exception with its message, focused on the Larimar frame
    tmp2 = tempfile.mkdtemp()
    try:
        c2 = os.path.join(tmp2, "panic.c")
        p2 = os.path.join(tmp2, "panic")
        subprocess.run([EXE, os.path.join(HERE, "panic.lar"), "-o", c2, "--debug"], env=env, check=True)
        subprocess.run([CC, "-std=c99", "-g", "-O0", "-w", c2, "-o", p2, "-lm"], check=True)
        d = Dap(env, backend)
        try:
            d.req("initialize", {"adapterID": "larimar", "linesStartAt1": True})
            d.send("launch", {"program": p2})
            d.wait(lambda m: m.get("event") == "initialized")
            d.req("setExceptionBreakpoints", {"filters": ["panic"]})
            d.req("configurationDone")
            st = d.stopped()
            tid = st["body"]["threadId"]
            check("dap: panic is an exception", st["body"].get("reason") == "exception", st)
            info = d.req("exceptionInfo", {"threadId": tid}).get("body", {})
            check("dap: panic message", "index 3 out of range" in info.get("description", ""), info)
            frames = d.frames(tid)
            pick = [f for f in frames if f["name"] == "pick"]
            check("dap: Larimar frame under the runtime", bool(pick) and frames[0].get("presentationHint") == "subtle", frames[:4])
            if pick:
                vs = {v["name"]: v["value"] for v in d.locals(pick[0]["id"])}
                check("dap: values where it panicked", vs.get("i") == "3" and vs.get("xs", "").startswith("[3]"), vs)
        finally:
            d.close()
    finally:
        shutil.rmtree(tmp2, ignore_errors=True)


tmp = tempfile.mkdtemp()
try:
    env = dict(os.environ, LARIMAR_HOME=ROOT, LANG="C.UTF-8", LC_ALL="C.UTF-8")
    c_file = os.path.join(tmp, "values.c")
    prog = os.path.join(tmp, "values")
    r = subprocess.run([EXE, SRC, "-o", c_file, "--debug"], env=env, capture_output=True, text=True)
    check("larimar --debug", r.returncode == 0, r.stderr)
    c = open(c_file, encoding="utf-8").read() if r.returncode == 0 else ""
    check("#line to the .lar file", ('#line %d "' % LINE) in c and "values.lar" in c)
    r = subprocess.run([CC, "-std=c99", "-g", "-O0", "-w", c_file, "-o", prog, "-lm"], capture_output=True, text=True)
    check("compiles with -g", r.returncode == 0, r.stderr)

    ran = False
    if r.returncode == 0 and shutil.which("lldb"):
        ran = True
        cmds = os.path.join(tmp, "lldb.txt")
        with open(cmds, "w") as f:
            f.write("command script import \"%s\"\n" % os.path.join(ROOT, "debug", "larimar_lldb.py"))     # a path with spaces
            f.write("breakpoint set --file values.lar --line %d\nrun\n" % LINE)
            f.write("frame variable %s\n" % " ".join(v for v, _ in EXPECT))
            f.write("bt 1\nkill\nquit\n")
        out = subprocess.run(["lldb", "-b", "-s", cmds, prog], env=env, capture_output=True, text=True, timeout=120).stdout
        check("lldb stops on values.lar:%d" % LINE, ("values.lar:%d" % LINE) in out, out)
        for v, want in EXPECT:
            line = next((l for l in out.splitlines() if (") %s = " % v) in l), "")
            check("lldb shows %s" % v, want in line, line or out)
    if r.returncode == 0 and shutil.which("gdb"):
        ran = True
        args = ["gdb", "-batch", "-ex", "source " + os.path.join(ROOT, "debug", "larimar_gdb.py"),
                "-ex", "break values.lar:%d" % LINE, "-ex", "run"]
        for v, _ in EXPECT:
            args += ["-ex", "output %s" % v, "-ex", 'echo \\n']
        out = subprocess.run(args + [prog], env=env, capture_output=True, text=True, timeout=120).stdout
        check("gdb stops on values.lar:%d" % LINE, ("values.lar:%d" % LINE) in out, out)
        lines = out.splitlines()
        tail = lines[-len(EXPECT):] if len(lines) >= len(EXPECT) else lines
        for (v, want), got in zip(EXPECT, tail):
            check("gdb shows %s" % v, want in got, got)
    if not ran:
        print("  skip  debug: no lldb or gdb")
    if r.returncode == 0:
        dap_tests(env, prog, c_file)
finally:
    shutil.rmtree(tmp, ignore_errors=True)

print("")
print("debug: %d failed" % len(failures))
sys.exit(1 if failures else 0)
