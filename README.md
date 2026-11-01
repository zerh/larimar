# Larimar Compiler

The Larimar compiler, written in Larimar. Self-hosting compiler that compiles to C99.

## Directory Structure

```
larimar-compiler/
├── src/                     # Compiler source code (Larimar)
│   ├── main.lar             # Entry point
│   ├── lexer.lar            # Lexical analysis
│   ├── parser.lar           # Syntax analysis
│   ├── analyzer.lar         # Semantic analysis
│   ├── gen.lar              # Code generation
│   ├── runtime.lar          # Runtime C code
│   ├── session.lar          # One analysis without C (larimar check)
│   ├── lsp.lar, ide.lar     # Language server (larimar lsp) and its answers
│   ├── testing.lar          # Test runner (larimar test)
│   └── ...
├── std/                     # Standard library source (edit it here); std/net.lar: TCP, UDP and their servers, TLS servers; std/net/http.lar: HTTP client; std/net/http/tls.lar: TLS
│                            # (net, io and os are written in Larimar over the system's C functions: extern, #when, T*, released by)
├── tests/                   # Tests (larimarc test, tests/run-tests.sh; tests/lsp for check and lsp)
├── debug/                   # lldb and gdb formatters for Larimar values (installed in larimar/debug)
├── bin/larimar              # Wrapper installed as larimar/bin/larimar
├── MANUAL.md                # Language manual (English)
├── MANUAL_ES.md             # Language manual (Spanish)
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
# Should output: larimar 0.3.0

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
the debuggers and a client as other programs (`std.process`) and talk to them like an editor would:
`larimar check --json` and `larimar lsp`, `larimar --debug` with lldb, gdb and `larimar dap`, and
`https://` against a local HTTPS server (the certificate in `tests/tls`). No Python is needed.

## Editor support

`larimar check [file|folder] [--json]` reports the errors without generating C. `larimar lsp` is the
language server (see "The editor" in section 26 of `MANUAL.md`): the server keeps the open documents
(`docstore.lar`) and answers each request in a forked process that links and analyzes the program
(`session.lar`) and answers from the analysis (`ide.lar`).

`larimar build --debug` compiles with `-g -O0`, `#line` directives to the `.lar` files and a debug map
(`build/<name>.debug.json`, from `debugmap.lar`). `larimar dap` (`dap.lar`) is the debugger for editors:
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
version = "0.3.0"
main = "src/main.lar"

[c]
flags = ["-O2"]
```

## Source Files Overview

| File | Purpose |
|------|---------|
| analyzer.lar | Semantic analysis, type checking, lifetime analysis |
| checkexpr.lar | Expression type checking, method resolution |
| genexpr.lar | C code generation for expressions |
| gen.lar | C code generation for statements |
| runtime.lar | Runtime C code (strings, memory, Any) |
| parser.lar | Syntax parsing, AST construction |
| sema.lar | Type system, symbol tables |
| linker.lar | Module linking, C compilation |
| lexer.lar | Tokenization |
| ast.lar | AST node definitions |
| main.lar | CLI, project management |
| rtselect.lar | Runtime selection |
| prune.lar | Keeps only the generated C the program reaches |
| ide.lar | Editor answers: hover, definition, references, symbols, completion |
| lsp.lar | Language server: JSON-RPC, documents, forked analyses |
| session.lar | One analysis without C; larimar check |
| docstore.lar | The editor's open documents (freeable C memory) |
| dap.lar | Debugger: DAP adapter over lldb-dap, values shown as Larimar |
| debugmap.lar | Debug map: C names and types of every variable, for the debugger |
| toml.lar | TOML parser |
| testing.lar | Test runner: larimar test, test functions and `// expect:` files |
| cc.lar | Calling the C compiler and other programs |

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
