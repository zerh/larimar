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
  other programs, libraries and services, the editor and the tests.
- [Specification](docs/spec.md) (language 1.3): when it and the manual disagree, it wins.
- [Bibliotecas en Larimar](docs/libraries.es.md) (in Spanish): every scenario of writing, publishing and
  using a library, each with its code and the output it gave.
- [Changelog](CHANGELOG.md) and [how to contribute](CONTRIBUTING.md): how the compiler is organized, with
  [every function of it](docs/compiler-reference.md), [every public name of std](docs/std-reference.md),
  [how libraries and services are made inside](docs/compiler-libraries.es.md) (in Spanish) and
  [the C of the standard library](docs/std-c.md).

## No C of its own: other programs instead

Larimar becomes C, and the standard library talks to the operating system through it (files, sockets,
threads, TLS). That C is std's: **a program, a library and a service written in Larimar have no C of their
own**, so all the C a program runs is part of Larimar, written and tested with it, and nobody's library
can bring C that the compiler does not check. What Larimar does not have runs in another process:

- **`std.os.rpc`**: calls to another program (JSON-RPC). `Rpc.startShared` talks to a Larimar program
  through shared memory, in a few microseconds per call; `Rpc.start` to any program, through its pipes.
- **`std.os.shared`**: streams of bytes between two programs through shared memory, with no system call
  while there is something to read.
- **`Process { run: task }` and `ProcessPool`**: a `Task` of the program runs in a copy of it, used as a
  thread is (`start`, `join`; `submit`, `wait`); a panic there is a `ProcessError` here.

If the other process fails, it does not corrupt the memory of yours: the call gets an error. See
[chapter 23 of the manual](docs/manual.md#23-other-programs-calls-shared-memory-and-processes).

For one C header, a project can say `[project] unsafe_c = true` and declare a **native interface**
(`native interface LibM "<math.h>" { function cbrt(x: float64): float64; }`, then `LibM.cbrt(x)`): std
reaches libc the same way. Every build of a program with that C says where it comes from
([chapter 27](docs/manual.md#c-of-its-own-unsafe_c--true)).

## Libraries and services

A project with `kind = "library"` is a library. A program names its folder in `[dependencies]` and writes
`import <name>`: the library's source is compiled with the program, with one runtime and the whole
language on both sides (interfaces the program implements, lists, enums, `throws`). Its modules are
`<name>` and `<name>.<part>`, so they never meet the program's, and the libraries it uses come with it.

A project with `kind = "service"` is a service: its public functions run in its own process. A program
names it in `[dependencies]` too, and imports a class with the same functions, each one a call to the
service's executable (`let c: Calc = Calc.start(); c.add(2, 40)`). `larimar build` of the program builds
its services first. See [chapter 27 of the manual](docs/manual.md#27-libraries-and-services-written-in-larimar)
and the [manual of libraries](docs/libraries.es.md) (in Spanish).

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
already translated to C. After changing `src/`, `--verify` says whether it is older than `src/`; then:

```sh
cp build/stage2.c bootstrap/larimarc.c
```

`std/` can only use what the compiler that compiles it already understands: something new in the
language goes into the compiler first, the bootstrap is regenerated, and then `std/` may use it.

## Repository layout

```
larimar/
├── src/                 the compiler (Larimar), one folder per stage
│   ├── main.lar         the commands
│   ├── syntax/          lexer, parser, ast
│   ├── semantics/       linker (modules), types, analyzer, expressions
│   ├── codegen/         gen, expressions, prune, debugmap
│   ├── editor/          session (larimar check), lsp, ide, docstore, dap
│   └── project/         cc (the C compiler), testing (larimar test), libraries, services
├── std/                 the standard library (io, os, net, thread, encoding, text, time...)
├── runtime/             the runtime: the C under every program
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
(a tool can add `larimar hello` that way). The libraries and services written in Larimar that a project
uses are named in `[dependencies]`, each with the folder of its project. ([manual, chapter 26](docs/manual.md#26-projects-larimartoml-and-larimar-build).)

## Editor support

`larimar check [file|folder] [--json]` reports the errors without generating C. `larimar lsp` is the
language server (see "The editor" in chapter 26 of the [manual](docs/manual.md)): the server keeps the open documents
(`editor/docstore.lar`) and answers each request in a forked process that links and analyzes the program
(`editor/session.lar`) and answers from the analysis (`editor/ide.lar`).

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

| File | Purpose |
|------|---------|
| main.lar | CLI, project management |
| syntax/lexer.lar | Tokenization |
| syntax/parser.lar | The class Parser (tokens, where it reads) and `parseProgram` |
| syntax/parser/ | The grammar, above each function: declarations, natives, types, statements, expressions |
| syntax/ast.lar | AST node definitions |
| semantics/linker.lar | Modules and imports, native interfaces (and what tasks need) |
| semantics/types.lar | Type system, symbol tables |
| semantics/analyzer.lar | Semantic analysis: its state, its entry, scopes and symbols |
| semantics/analyzer/ | declarations, classes, statements, flow (what a result points to), compact, narrowing, threads, order |
| semantics/expressions.lar | Expression type checking: types as written, names, members, indexes |
| semantics/expressions/ | constants, conversions, literals, operators, calls, switches |
| codegen/gen.lar | C code generation: the context of a function, the assembly of the output |
| codegen/gen/ | types, classes, statements |
| codegen/expressions.lar | C code generation for expressions: names, C types, values |
| codegen/expressions/ | strings, operators, calls, clone, lambdas, patterns |
| codegen/prune.lar | Only the C the program reaches: of what it generates, and of the runtime (runtime/) |
| codegen/debugmap.lar | Debug map: C names and types of every variable, for the debugger |
| editor/session.lar | One analysis without C; larimar check |
| editor/lsp.lar | Language server: JSON-RPC, documents, forked analyses |
| editor/ide.lar | Editor answers: hover, definition, references, symbols, completion |
| editor/docstore.lar | The editor's open documents (freeable C memory) |
| editor/dap.lar | Debugger: DAP adapter over lldb-dap, values shown as Larimar |
| project/cc.lar | Calling the C compiler and other programs |
| project/testing.lar | Test runner: larimar test and test functions |
| project/libraries.lar | Libraries and services of [dependencies]: their folders and their checks |
| project/services.lar | Services: what they give, the module a program imports, the main of their executable |

## License

[MIT](LICENSE).
