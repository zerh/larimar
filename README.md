# Larimar

Larimar is a programming language that compiles to C99: classes, interfaces, lambdas, threads and
modules, with **memory without a garbage collector and without `free`**. Every value lives in a memory
(the block that created it, an object, a memory of your own), and the compiler checks that nothing
outlives what it points to. C libraries are declared, not wrapped, and a Larimar project can itself be
built into a static or dynamic C library. The compiler is written in Larimar.

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

- [Manual](doc/manual.md) ([en español](doc/manual.es.md)): the language with examples, projects,
  C, libraries, the editor and the tests.
- [Specification](doc/spec.md) (language 1.0): when it and the manual disagree, it wins.
- [Changelog](CHANGELOG.md) and [how to contribute](CONTRIBUTING.md).

## Calling C

C functions, constants, macros, globals, structs, pointers and resources are declared, not wrapped, with
`native`: the Larimar name on the left, the C name after `=`. `native function`, `native const` / `native let`,
`native struct`, `T*` and `&x` (in calls), `native type X = FILE* released by fclose` (released when the memory
it lives in is freed, or with `release(x)`), C types with fields and methods
(`native type Db = sqlite3* { native function errmsg(): String = sqlite3_errmsg; }`), callbacks that take
lambdas when C passes a `Context`, C text as `c"..."` when it is not a plain name, C written in the file
(`ccode { ... }`), methods whose body is C, `lar"name"` inside that C, and a class for each system
(`implements OnUnix` / `OnWindows`, chosen with `switch (os.platform())`) for what changes between them:
its C reaches only that system's build, and no `#if` is written by hand. A text that C makes with `malloc`
is copied and freed (`native function strdup(s: String): String released by free`). See [chapter 23 of the manual](doc/manual.md#23-calling-c).

## Libraries for C and for Larimar

A project with `kind = "library"` builds a library instead of an executable, static by default
(`[library] type = "dynamic"` or `larimar build --dynamic` for a `.so`/`.dylib`/`.dll`). `build/<name>/`
gets four files: `lib<name>.a`, `<name>.h` for C, `<name>.lar` for Larimar (its `export function`s as
`native` declarations) and `<name>.interface` with an 8-digit hash of the `.lar` that the library also has
inside, so a program that links it (`static_libraries` or `dynamic_libraries` in `[c]`, then
`import <name>`) builds only with files of one build. The library's classes go to C as handles, with
their fields and methods (`tk_Counter_add(c, "x")` in C, `c.add("x")` in Larimar), its texts as copies to
free; everything else of its C is static, so libraries and programs do not clash. See
[chapter 27 of the manual](doc/manual.md#27-libraries-written-in-larimar).

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
│   ├── codegen/         gen, expressions, runtimeselect, prune, debugmap
│   ├── editor/          session (larimar check), lsp, ide, docstore, dap
│   └── project/         cc (the C compiler), testing (larimar test), libraries
├── std/                 the standard library (io, os, net, thread, encoding, text, time...); std/runtime: the runtime
├── tests/               the tests (tests/run-tests.sh)
├── doc/                 manual.md, manual.es.md, spec.md
├── bootstrap/           larimarc.c (the compiler in C), build.sh, build.ps1
├── bin/                 the launchers installed as larimar/bin/larimar(.cmd)
├── tools/
│   ├── debuggers/       lldb and gdb formatters (installed as larimar/debug)
│   └── tcc/             build the tcc that the releases bring (Linux, Windows)
├── docs/                the website (GitHub Pages)
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

Tests are `test function`s with `std.test` checks ([manual, chapter 26](doc/manual.md#tests-test-function-and-larimar-test)), grouped one file per topic
(`tests/c/callbacks_test.lar`, `tests/language/when_test.lar`...), run with AddressSanitizer and UBSan. The
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
(that is how Minero gives `larimar add` and `larimar fetch`). A project's `[dependencies]` live in
`deps/<name>/`: their modules are imported from `deps/<name>/src` and their `[c]` is added to the
project's. ([manual, chapter 26](doc/manual.md#26-projects-larimartoml-and-larimar-build).)

## Editor support

`larimar check [file|folder] [--json]` reports the errors without generating C. `larimar lsp` is the
language server (see "The editor" in chapter 26 of the [manual](doc/manual.md)): the server keeps the open documents
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
| syntax/parser.lar | Syntax parsing, AST construction (its grammar above each function) |
| syntax/ast.lar | AST node definitions |
| semantics/linker.lar | Modules and imports |
| semantics/types.lar | Type system, symbol tables |
| semantics/analyzer.lar | Semantic analysis, type checking, lifetime analysis |
| semantics/expressions.lar | Expression type checking, method resolution |
| codegen/gen.lar | C code generation for statements |
| codegen/expressions.lar | C code generation for expressions |
| codegen/runtimeselect.lar | Runtime selection: only the pieces of the runtime (std/runtime) the program uses |
| codegen/prune.lar | Keeps only the generated C the program reaches |
| codegen/debugmap.lar | Debug map: C names and types of every variable, for the debugger |
| editor/session.lar | One analysis without C; larimar check |
| editor/lsp.lar | Language server: JSON-RPC, documents, forked analyses |
| editor/ide.lar | Editor answers: hover, definition, references, symbols, completion |
| editor/docstore.lar | The editor's open documents (freeable C memory) |
| editor/dap.lar | Debugger: DAP adapter over lldb-dap, values shown as Larimar |
| project/cc.lar | Calling the C compiler and other programs |
| project/testing.lar | Test runner: larimar test and test functions |
| project/libraries.lar | Libraries written in Larimar: their files, the interface hash and its checks |

## License

[MIT](LICENSE).
