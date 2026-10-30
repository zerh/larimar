#!/usr/bin/env python3
"""https:// with SystemTls: python3 tests/tls/tls_test.py <larimarc> [cc]

Starts an HTTPS server (cert.pem: a certificate of its own, for 127.0.0.1) and an HTTP server that redirects
to it, builds client.lar and checks what it prints: the certificate rejected by default, then with
SystemTls { verify: false } a GET, a chunked body, a big body through copy(), a POST, a redirection from
http:// to https:// and a TlsProvider of its own. On Linux, also the message when OpenSSL is missing."""
import http.server, os, socketserver, ssl, subprocess, sys, tempfile, threading, shutil

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
CFLAGS = ["-std=c99", "-g", "-O1", "-fno-omit-frame-pointer", "-fsanitize=address,undefined", "-fno-sanitize-recover=undefined"]
LIBS = ["-pthread", "-lm"] + (["-ldl"] if sys.platform.startswith("linux") else []) + \
       (["-framework", "Network", "-framework", "Security"] if sys.platform == "darwin" else [])

failures = []


def check(name, ok, got=""):
    print("  %s  tls: %s" % ("ok  " if ok else "FAIL", name))
    if not ok:
        failures.append(name)
        if got:
            print("        " + str(got).replace("\n", "\n        ")[:3000])


class Secure(http.server.BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def send(self, body, extra=()):
        self.send_response(200)
        for k, v in extra:
            self.send_header(k, v)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path == "/chunked":
            self.send_response(200)
            self.send_header("Transfer-Encoding", "chunked")
            self.end_headers()
            self.wfile.write(b"5\r\nhola \r\n7\r\nmundo!!\r\n0\r\n\r\n")
        elif self.path == "/big":
            self.send(b"0123456789" * 20000)
        else:
            self.send(("secreto " + self.path).encode())

    def do_POST(self):
        n = int(self.headers.get("Content-Length", "0"))
        self.send(self.rfile.read(n))

    def log_message(self, *a):
        pass


def redirect_handler(port):
    class Plain(http.server.BaseHTTPRequestHandler):
        protocol_version = "HTTP/1.1"

        def do_GET(self):
            self.send_response(302)
            self.send_header("Location", "https://127.0.0.1:%d/b" % port)
            self.send_header("Content-Length", "0")
            self.end_headers()

        def log_message(self, *a):
            pass
    return Plain


def serve(server):
    t = threading.Thread(target=server.serve_forever, daemon=True)
    t.start()
    return server


def build(src, out, env, edit=None):
    c = out + ".c"
    r = subprocess.run([EXE, src, "-o", c], env=env, capture_output=True, text=True)
    if r.returncode != 0:
        return r.stderr
    if edit:
        text = open(c, encoding="utf-8").read()
        open(c, "w", encoding="utf-8").write(edit(text))
    r = subprocess.run([CC] + CFLAGS + [c, "-o", out] + LIBS, capture_output=True, text=True)
    return None if r.returncode == 0 else r.stderr


socketserver.TCPServer.allow_reuse_address = True
secure = socketserver.ThreadingTCPServer(("127.0.0.1", 0), Secure)
context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
context.load_cert_chain(os.path.join(HERE, "cert.pem"), os.path.join(HERE, "key.pem"))
secure.socket = context.wrap_socket(secure.socket, server_side=True)
serve(secure)
tls_port = secure.server_address[1]
plain = serve(socketserver.ThreadingTCPServer(("127.0.0.1", 0), redirect_handler(tls_port)))
http_port = plain.server_address[1]

tmp = tempfile.mkdtemp()
try:
    env = dict(os.environ, LARIMAR_HOME=ROOT, ASAN_OPTIONS="detect_leaks=0")
    prog = os.path.join(tmp, "client")
    problem = build(os.path.join(HERE, "client.lar"), prog, env)
    check("client builds", problem is None, problem)
    if problem is None:
        r = subprocess.run([prog, str(tls_port), str(http_port)], env=env, capture_output=True, text=True, timeout=60)
        lines = r.stdout.splitlines()
        out = r.stdout + r.stderr

        def line(prefix):
            return next((l for l in lines if l.startswith(prefix)), "")
        check("exits cleanly", r.returncode == 0, out)
        check("certificate rejected by default", line("default: ").startswith("default: network: tls: "), out)
        check("GET with verify: false", "200 secreto /a" in lines, out)
        check("chunked over TLS", "chunked: hola mundo!!" in lines, out)
        check("big body with copy()", "big: 200000" in lines, out)
        check("POST over TLS", "post: ñandú por tls" in lines, out)
        check("redirect http -> https", "redirect: 200 secreto /b true" in lines, out)
        check("a TlsProvider of its own", "custom: secreto /c (1 connection)" in lines, out)
    if sys.platform.startswith("linux"):
        # no OpenSSL: the names it looks for do not exist
        prog2 = os.path.join(tmp, "missing")
        problem = build(os.path.join(HERE, "client.lar"), prog2, env,
                        lambda c: c.replace('"libssl.so.3", "libssl.so.1.1", "libssl.so"', '"libnossl.so.3"'))
        check("missing build", problem is None, problem)
        if problem is None:
            r = subprocess.run([prog2, str(tls_port), str(http_port)], env=env, capture_output=True, text=True, timeout=60)
            check("OpenSSL missing: Unsupported, in English",
                  "default: unsupported: https: OpenSSL not found (tried libssl.so.3, libssl.so.1.1, libssl.so)" in r.stdout.splitlines(),
                  r.stdout + r.stderr)
finally:
    secure.shutdown()
    plain.shutdown()
    shutil.rmtree(tmp, ignore_errors=True)

print("")
print("tls: %d failed" % len(failures))
sys.exit(1 if failures else 0)
