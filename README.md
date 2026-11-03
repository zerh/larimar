# Larimar Compiler

The Larimar compiler, written in Larimar. Self-hosting compiler that compiles to C99.

## Directory Structure

```
larimar-compiler/
├── src/                     # Compiler source code (Larimar), one folder per stage
│   ├── main.lar             # Entry point: the commands
│   ├── syntax/              # lexer, parser, ast
│   ├── semantics/           # linker (modules), types, analyzer, expressions
│   ├── codegen/             # gen, expressions, runtime, runtimeselect, prune, debugmap
│   ├── editor/              # session (larimar check), lsp, ide, docstore, dap
│   └── project/             # cc (the C compiler), testing (larimar test)
├── std/                     # Standard library source (edit it here): io.lar and io/ (files, path, console), os.lar and os/process.lar,
│                            # time.lar, crypto.lar, encoding/ (json, toml, base64, hex, url), net.lar (TCP, UDP, servers with TLS),
│                            # net/tls.lar (client TLS), net/http.lar (HTTP client), text.lar and text/regex.lar, test.lar
│                            # (net, io and os are written in Larimar over the system's C functions: extern, #when, T*, released by)
├── tests/                   # Tests (larimarc test, tests/run-tests.sh; tests/lsp for check and lsp)
├── debug/                   # lldb and gdb formatters for Larimar values (installed in larimar/debug)
├── bin/larimar              # Wrapper installed as larimar/bin/larimar
├── MANUAL.md                # Language manual (English)
├── MANUAL_ES.md             # Language manual (Spanish)
├── SPEC.md                  # Language specification (version 1.0)
├── larimarc_bootstrap.c     # C bootstrap
├── build-bootstrap.sh       # Build from the C bootstrap and install
├── larimar.toml             # Project configuration
└── README.md                # This file
```

Everything is edited here. `../larimar/` is the **installation**: a build result that
`build-bootstrap.sh` fills and that can be deleted and regenerated at any time:

```
larimar/
├── bin/larimarc             # the compiler
├── bin/larimar              # wrapper that sets LARIMAR_HOME
├── debug/                   # copy of debug/ (lldb and gdb formatters)
├── std/                     # copy of std/
└── MANUAL.md                # copy of MANUAL.md
```

## Calling C

C functions, constants, macros, globals, structs, pointers and resources are declared, not wrapped:
`extern function`, `extern const` / `extern let`, `T*` and `&x` (in calls), `extern type X = c "FILE*"
released by fclose` (released when the memory it lives in is freed, or with `release(x)`), and `#when windows`
... `#else` ... `#end` for what changes between platforms (compiled as `#if`, every branch checked). See chapter 23
of `MANUAL.md`.

## Building from C Bootstrap

If you have a C compiler but no Larimar compiler:

```bash
./build-bootstrap.sh            # builds ./larimarc and installs it into ../larimar
./build-bootstrap.sh --verify   # also checks that the compiler compiles itself
./build-bootstrap.sh --no-install
LARIMAR_PREFIX=/opt/larimar ./build-bootstrap.sh   # install somewhere else
```

This compiles `larimarc_bootstrap.c` (pre-generated C code) into a working Larimar compiler.
The only requirement is a C99 compiler (gcc, clang, tcc...).

## Building with Larimar

If you already have a working Larimar compiler:

```bash
export LARIMAR_HOME=$(pwd)      # use std/ from this folder while developing
larimar build
# Creates: build/larimarc
```

This compiles the Larimar source code in `src/` into a new compiler.

## Regenerating Bootstrap C

To update `larimarc_bootstrap.c` after changes:

```bash
# Build compiler with Larimar
larimar build

# Check that the new compiler compiles itself, and install it
./build-bootstrap.sh --verify

# Then update the bootstrap C with the compiler built from src/
cp build/stage2.c larimarc_bootstrap.c
```

## Verification

Test the compiler:

```bash
./larimarc --version
# Should output: larimar 0.5.0 (language 1.0)

# Compile a test program
echo 'function main(): void { println("Hello!"); }' > test.lar
LARIMAR_HOME=$(pwd) ./larimarc test.lar -o test.c
cc -std=c99 -O2 test.c -o test
./test
```

## Tests

```bash
tests/run-tests.sh            # everything: larimarc test on tests/, plus the runner check and std-check
tests/run-tests.sh memory     # only the tests whose path or name contains "memory"
bin/larimarc test tests/std   # only larimarc test, on one folder
```

Tests are of two kinds, and `larimarc test` runs both (with AddressSanitizer and UBSan): `test function`s
with `std.test` checks, like `tests/std/regex_test.lar` (MANUAL.md, section 26), and files that say what
they expect in their first lines (`// expect: run` with `// output:` lines, `// expect: error <text>`,
`// expect: panic <text>` or `// expect: memory-error`), which test the compiler itself (section 28).
Every bug found goes in as a test first.

`tests/lsp/lsp_test.lar`, `tests/debug/debug_test.lar` and `tests/tls/tls_test.lar` start the compiler,
the debuggers and a client as other programs (`std.os.process`) and talk to them like an editor would:
`larimar check --json` and `larimar lsp`, `larimar --debug` with lldb, gdb and `larimar dap`, and
`https://` against a local HTTPS server (the certificate in `tests/tls`). No Python is needed.

## Plugins and dependencies

Other programs of `$LARIMAR_HOME/bin` answer commands of `larimar`, declared in `$LARIMAR_HOME/plugins/<name>.toml`
(that is how Minero gives `larimar add` and `larimar fetch`). A project's `[dependencies]` live in
`deps/<name>/`: their modules are imported from `deps/<name>/src` and their `[c]` is added to the
project's. (MANUAL.md, section 26.)

## Editor support

`larimar check [file|folder] [--json]` reports the errors without generating C. `larimar lsp` is the
language server (see "The editor" in section 26 of `MANUAL.md`): the server keeps the open documents
(`editor/docstore.lar`) and answers each request in a forked process that links and analyzes the program
(`editor/session.lar`) and answers from the analysis (`editor/ide.lar`).

`larimar test --list --json` lists the tests and `larimar test --json [file] [--test <name>]` runs them,
one JSON object per line: that is how the VS Code extension shows them in its Testing view.

`larimar build --debug` compiles with `-g -O0`, `#line` directives to the `.lar` files and a debug map
(`build/<name>.debug.json`, from `codegen/debugmap.lar`). `larimar dap` (`editor/dap.lar`) is the debugger for editors:
a DAP adapter written in Larimar over LLVM's `lldb-dap`, which shows the stack, variables and values
as Larimar (names, real classes, Any, enums), understands Larimar paths in evaluate and stops on
panics as exceptions. `debug/larimar_lldb.py` and
`debug/larimar_gdb.py` show the same values in lldb and gdb from a terminal. `tests/debug/debug_test.lar`
checks all of it.

## Project Configuration

`larimar.toml`:
```toml
[project]
name = "larimarc"
version = "0.5.0"
main = "src/main.lar"

[c]
flags = ["-O2"]
```

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
| codegen/runtime.lar | Runtime C code (strings, memory, Any) |
| codegen/runtimeselect.lar | Runtime selection |
| codegen/prune.lar | Keeps only the generated C the program reaches |
| codegen/debugmap.lar | Debug map: C names and types of every variable, for the debugger |
| editor/session.lar | One analysis without C; larimar check |
| editor/lsp.lar | Language server: JSON-RPC, documents, forked analyses |
| editor/ide.lar | Editor answers: hover, definition, references, symbols, completion |
| editor/docstore.lar | The editor's open documents (freeable C memory) |
| editor/dap.lar | Debugger: DAP adapter over lldb-dap, values shown as Larimar |
| project/cc.lar | Calling the C compiler and other programs |
| project/testing.lar | Test runner: larimar test, test functions and `// expect:` files |

## Self-Hosting

The compiler is **self-hosting**: it's written in Larimar and can compile itself.

```
Larimar source → [larimarc] → C code → [gcc/clang] → larimarc executable
```

The bootstrap C file (`larimarc_bootstrap.c`) allows cold-start compilation on any system with just a C compiler.

## Development

Modify `src/` or `std/`, then rebuild:

```bash
larimar build
./build/larimarc --version
```

Install it (copies the compiler, `std/` and `MANUAL.md` into `../out/larimar`):

```bash
./build-bootstrap.sh --verify
cp build/stage2.c larimarc_bootstrap.c     # when it says the bootstrap C is older than src/
```

## License

See individual files for license information.
