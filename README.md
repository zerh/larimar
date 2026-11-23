# Larimar

Larimar is a programming language that compiles to C99: classes, interfaces, lambdas, threads and
modules, with **memory without a garbage collector and without `free`**. Every value lives in a memory
(the block that created it, an object, a memory of your own), and the compiler checks that nothing
outlives what it points to. A program has no C of its own: **what Larimar does not have runs in another
process**, with calls through shared memory or pipes, so a failure there is an error here. The compiler is
written in Larimar.

```ts
function main(): int32 {
    let names: String[*] = ["Ana", "Luis"];
    for (n in names) { println("Hello, ${n}!"); }
    return 0;
}
```

## Install

```sh
curl -fsSL https://zerh.github.io/larimar/install.sh | sh                    # macOS and Linux
powershell -c "irm https://zerh.github.io/larimar/install.ps1 | iex"         # Windows
```

Or download a release from [Releases](https://github.com/zerh/larimar/releases): Linux and Windows bring
their own C compiler (tcc), so `larimar hello.lar` runs a file at once.

## Documentation

- [Manual](docs/manual.md) ([en español](docs/manual.es.md)): the language with examples, projects,
  other programs, libraries, the editor and the tests.
- [Specification](docs/spec.md) (language 1.4): when it and the manual disagree, it wins.
- [Bibliotecas en Larimar](docs/libraries.es.md) (in Spanish): every scenario of writing, publishing and
  using a library, each with its code and the output it gave.
- [Changelog](CHANGELOG.md) and [how to contribute](CONTRIBUTING.md): how the compiler is organized, with
  [every function of it](docs/compiler-reference.md), [every public name of std](docs/std-reference.md),
  [how libraries and tasks are made inside](docs/compiler-libraries.es.md) (in Spanish) and
  [the C of the standard library](docs/std-c.md).

## No C of its own: other programs instead

Larimar becomes C, and the standard library talks to the operating system through it (files, sockets,
threads, TLS). That C is std's: **a program and a library written in Larimar have no C of their own**, so all the C a program runs is part of Larimar, written and tested with it, and nobody's library
can bring C that the compiler does not check. What Larimar does not have runs in another process:

- **`std.os.rpc`**: calls to another program (JSON-RPC). A `Process` says what runs;
  `Rpc.startShared(process)` talks to a Larimar program through shared memory, in a few microseconds per
  call; `Rpc.start(process)` to any program, through its pipes. Any program that answers with `serve()` is
  a service.
- **`std.os.sharedmemory`**: streams of bytes between two programs through shared memory (a queue), with no
  system call while there is something to read, and segments (a board: numbers at offsets, the latest
  value); `std.io.bytes` writes and reads binary messages.
- **`Process { run: task }` and `ProcessPool`**: a `Task` of the program runs in a copy of it, used as a
  thread is (`start`, `join`; `submit`, `wait`); a panic there is a `ProcessError` here.

If the other process fails, it does not corrupt the memory of yours: the call gets an error. See
[chapter 23 of the manual](docs/manual.md#23-other-programs-calls-shared-memory-and-processes).

A C library goes in an `UnsafeTask`: its class declares the library's **native interface**
(`native interface Sdl "<SDL2/SDL.h>" { ... }`, then `Sdl.SDL_Init(...)`), and that C runs in the task's
own process, where a crash is an error of the task ([chapter 27](docs/manual.md#c-of-its-own-in-an-unsafetask)).

## Libraries

A project with `kind = "library"` is a library (the other kind is a program, the default). A program names
its folder in `[dependencies]` and writes `import <name>`: the library's source is compiled with the
program, with one runtime and the whole language on both sides (interfaces the program implements, lists,
enums, `throws`). Its modules are `<name>` and `<name>.<part>`, so they never meet the program's, and the
libraries it uses come with it. What should not share the program's memory is another program, started
with a `Process` ([chapter 27 of the manual](docs/manual.md#27-libraries-written-in-larimar), and the
[manual of libraries](docs/libraries.es.md), in Spanish).

## Building from source

Only a C99 compiler is needed (cc, gcc, clang, tcc...):

```sh
./bootstrap/build.sh                     # builds bin/larimarc from bootstrap/larimarc.c and installs ../out/larimar
./bootstrap/build.sh --verify            # also checks that the compiler compiles itself (stage 2 = stage 3)
./bootstrap/build.sh --verify --test     # and runs all the tests
./bootstrap/build.sh --no-install
LARIMAR_PREFIX=/opt/larimar ./bootstrap/build.sh   # install somewhere else
```

On Windows, `.\bootstrap\build.ps1 -verify` (with MinGW's gcc). `bootstrap/larimarc.c` is the compiler
already translated to C. After changing `src/compiler`, `--verify` says whether it is older than it; then:

```sh
cp build/stage2.c bootstrap/larimarc.c
```

`src/std/` can only use what the compiler that compiles it already understands: something new in the
language goes into the compiler first, the bootstrap is regenerated, and then `src/std/` may use it. To
run the compiler of the repository by hand: `LARIMAR_HOME=src bin/larimarc file.lar` (or
`LARIMAR_HOME=$PWD`: the compiler finds `src/std` there too).

## Repository layout

```
larimar/
├── src/
│   ├── compiler/        the compiler (Larimar), one folder per stage, each with a README.md (its API)
│   │   ├── main.lar     the commands
│   │   ├── pipeline.lar a compilation as passes: Link, CheckRules, Assemble, Analyze, EmitC, NameC, Prune
│   │   ├── syntax/      lexer, parser, ast
│   │   ├── semantics/   linker (modules), rules, types, analyzer, expressions
│   │   ├── codegen/     gen, expressions, localnames, cprogram, prune, debugmap
│   │   ├── editor/      session (larimar check), lsp, ide, opendocuments, dap
│   │   └── project/     cc (the C compiler), testing (larimar test), libraries
│   ├── std/             the standard library (io, os, net, thread, encoding, text, time...)
│   └── runtime/         the runtime: the C under every program
├── tests/               the tests (tests/run-tests.sh)
├── bootstrap/           larimarc.c (the compiler in C), build.sh, build.ps1
├── bin/                 the launchers installed as larimar/bin/larimar(.cmd)
├── tools/
│   ├── debuggers/       lldb and gdb formatters (installed as larimar/debug)
│   └── tcc/             build the tcc that the releases bring (Linux, Windows)
├── docs/                the website (GitHub Pages), with manual.md, manual.es.md and spec.md
└── larimar.toml
```

Everything is edited here. `../out/larimar/` is the **installation**, which `bootstrap/build.sh` fills
and can be deleted and regenerated at any time: `bin/larimarc`, `bin/larimar` (sets `LARIMAR_HOME`),
`std/`, `doc/`, `debug/` and, in the releases for Linux and Windows, `toolchain/tcc/`.

## Tests

```bash
tests/run-tests.sh            # everything: larimarc test on tests/, plus the runner check and std-check
tests/run-tests.sh memory     # only the tests whose path or name contains "memory"
bin/larimarc test tests/std   # only larimarc test, on one folder
```

Tests are `test function`s with `std.test` checks ([manual, chapter 26](docs/manual.md#tests-test-function-and-larimar-test)), grouped one file per topic
(`tests/std/rpc_test.lar`, `tests/language/threads_test.lar`...), run with AddressSanitizer and UBSan. The
ones that test the compiler itself use `tests/support/compiler.lar`: `failsWith(raw"""...""", "error")` for a
program the compiler must reject, and `runs("tests/cases/...", [lines])`, `panics(...)`, `memoryError(...)`
for the programs in `tests/cases/` (chapter 29).
Every bug found goes in as a test first.

`tests/lsp/lsp_test.lar`, `tests/debug/debug_test.lar` and `tests/tls/tls_test.lar` start the compiler,
the debuggers and a client as other programs (`std.os.process`) and talk to them like an editor would:
`larimar check --json` and `larimar lsp`, `larimar --debug` with lldb, gdb and `larimar dap`, and
`https://` against a local HTTPS server (the certificate in `tests/tls`). No Python is needed.

## Plugins and dependencies

Other programs of `$LARIMAR_HOME/bin` answer commands of `larimar`, declared in `$LARIMAR_HOME/plugins/<name>.toml`
(a tool can add `larimar hello` that way). The libraries written in Larimar that a project
uses are named in `[dependencies]`, each with the folder of its project. ([manual, chapter 26](docs/manual.md#26-projects-larimartoml-and-larimar-build).)

## Editor support

`larimar check [file|folder] [--json]` reports the errors without generating C. `larimar lsp` is the
language server (see "The editor" in chapter 26 of the [manual](docs/manual.md)): the server keeps the open documents
(in a memory it compacts; `editor/opendocuments.lar` for the worker) and answers each request with a
`larimarc lsp-worker`, a process that links and analyzes the program (`editor/session.lar`) and answers
from the analysis (`editor/ide.lar`).

`larimar test --list --json` lists the tests and `larimar test --json [file] [--test <name>]` runs them,
one JSON object per line: that is how the VS Code extension shows them in its Testing view.

`larimar build --debug` compiles with `-g -O0`, `#line` directives to the `.lar` files and a debug map
(`build/<name>.debug.json`, from `codegen/debugmap.lar`). `larimar dap` (`editor/dap.lar`) is the debugger for editors:
a DAP adapter written in Larimar over LLVM's `lldb-dap`, which shows the stack, variables and values
as Larimar (names, real classes, Any, enums), understands Larimar paths in evaluate and stops on
panics as exceptions. `tools/debuggers/larimar_lldb.py` and
`tools/debuggers/larimar_gdb.py` show the same values in lldb and gdb from a terminal. `tests/debug/debug_test.lar`
checks all of it.

## Source Files Overview

Each folder of `src/compiler` has a README.md: what it does, and its API (written by
`tools/reference.py` from the code). Every function: [docs/compiler-reference.md](docs/compiler-reference.md).

| File | Purpose |
|------|---------|
| main.lar | CLI, project management |
| pipeline.lar | One compilation (`Compilation`) and its passes |
| syntax/ | Lexer, parser (its grammar, by theme), the tree (`ast.lar`) |
| semantics/linker.lar | Modules and imports, native interfaces (and what tasks need) |
| semantics/rules.lar | The rules about modules, one object each (`languageRules()`; `error[rule-id]`) |
| semantics/types.lar | Type system, symbol tables |
| semantics/analyzer.lar, analyzer/ | Semantic analysis: declarations, classes, statements, flow, compact, narrowing, threads, order |
| semantics/expressions.lar, expressions/ | Expressions: constants, conversions, literals, operators, calls, callbacks to C, switches |
| codegen/gen.lar, gen/ | C generation: the file, types, classes, statements |
| codegen/expressions.lar, expressions/ | C of expressions: strings, operators, calls, callbacks to C, clone, lambdas, patterns |
| codegen/localnames.lar | The names of the compiler's variables in the C |
| codegen/cprogram.lar | The C as parts: text, and each function whole (CProgram, CFunction) |
| codegen/prune.lar | Only the C the program reaches: of what it generates, and of the runtime (src/runtime/) |
| codegen/debugmap.lar | Debug map: C names and types of every variable, for the debugger |
| editor/session.lar | One analysis without C; larimar check |
| editor/lsp.lar | Language server: JSON-RPC, documents, workers |
| editor/ide.lar | Editor answers: hover, definition, references, symbols, completion |
| editor/opendocuments.lar | The editor's open documents, which the linker reads before the disk |
| editor/dap.lar | Debugger: DAP adapter over lldb-dap, values shown as Larimar |
| project/cc.lar | Calling the C compiler and other programs |
| project/testing.lar | Test runner: larimar test and test functions |
| project/libraries.lar | Libraries of [dependencies]: their folders and their checks |

## License

[MIT](LICENSE).
