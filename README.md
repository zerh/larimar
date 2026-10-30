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
│   └── ...
├── std/                     # Standard library source (edit it here); std/net.lar: TCP; std/net/http.lar: HTTP client; std/net/http/tls.lar: TLS
│                            # (net, io and os are written in Larimar over the system's C functions: extern, #when, T*, released by)
├── tests/                   # Tests (tests/run-tests.sh; tests/lsp for check and lsp)
├── editors/vscode/          # VS Code extension (language server and debugger)
├── debug/                   # lldb and gdb formatters for Larimar values (installed in larimar/debug)
├── bin/larimar              # Wrapper installed as larimar/bin/larimar
├── MANUAL.md                # Language manual (Spanish)
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
# Should output: larimar 0.2.0

# Compile a test program
echo 'function main(): void { println("Hello!"); }' > test.lar
LARIMAR_HOME=$(pwd) ./larimarc test.lar -o test.c
cc -std=c99 -O2 test.c -o test
./test
```

## Tests

```bash
tests/run-tests.sh            # every test in tests/, compiled and run with AddressSanitizer and UBSan
tests/run-tests.sh memory     # only tests/memory
```

Each test file says what it expects in its first lines (`// expect: run` with `// output:` lines,
`// expect: error <text>`, `// expect: panic <text>` or `// expect: memory-error`). See section 28 of
`MANUAL.md`. Every bug found goes in as a test first.

`tests/lsp/lsp_test.py` (run by `run-tests.sh` when `python3` exists) checks `larimar check --json` and
talks LSP to `larimar lsp`: errors, hover, definition, references, symbols, completion, signature help,
with `fork()` and with `LARIMAR_LSP_NO_FORK=1`.
`tests/tls/tls_test.py` runs `https://` against a local HTTPS server (the certificate in `tests/tls`).

## Editors

`larimar check [file|folder] [--json]` reports the errors without generating C. `larimar lsp` is the
language server (see "El editor" in section 26 of `MANUAL.md`): the server keeps the open documents
(`docstore.lar`) and answers each request in a forked process that links and analyzes the program
(`session.lar`) and answers from the analysis (`ide.lar`). `editors/vscode` is the VS Code extension:

```bash
cd editors/vscode && npm install && npm run compile && npx vsce package
code --install-extension larimar-0.4.0.vsix
```

`larimar build --debug` compiles with `-g -O0`, `#line` directives to the `.lar` files and a debug map
(`build/<name>.debug.json`, from `debugmap.lar`). `larimar dap` (`dap.lar`) is the debugger for editors:
a DAP adapter written in Larimar over LLVM's `lldb-dap`, which shows the stack, variables and values
as Larimar (names, real classes, Any, enums), understands Larimar paths in evaluate and stops on
panics as exceptions. In VS Code, F5 on a `.lar` file builds and starts it. `debug/larimar_lldb.py` and
`debug/larimar_gdb.py` show the same values in lldb and gdb from a terminal. `tests/debug/debug_test.py`
checks all of it.

## Project Configuration

`larimar.toml`:
```toml
[project]
name = "larimarc"
version = "0.1.0"
main = "src/main.lar"

[c]
flags = ["-O2"]
```

## Source Files Overview

| File | Lines | Purpose |
|------|-------|---------|
| analyzer.lar | ~2,377 | Semantic analysis, type checking, lifetime analysis |
| checkexpr.lar | ~2,280 | Expression type checking, method resolution |
| genexpr.lar | ~1,711 | C code generation for expressions |
| gen.lar | ~1,439 | C code generation for statements |
| runtime.lar | ~1,167 | Runtime C code (strings, memory, Any) |
| parser.lar | ~1,025 | Syntax parsing, AST construction |
| sema.lar | ~818 | Type system, symbol tables |
| linker.lar | ~694 | Module linking, C compilation |
| lexer.lar | ~538 | Tokenization |
| ast.lar | ~489 | AST node definitions |
| main.lar | ~432 | CLI, project management |
| rtselect.lar | ~356 | Runtime selection |
| prune.lar | ~250 | Keeps only the generated C the program reaches |
| ide.lar | ~1,460 | Editor answers: hover, definition, references, symbols, completion |
| lsp.lar | ~460 | Language server: JSON-RPC, documents, forked analyses |
| session.lar | ~145 | One analysis without C; larimar check |
| docstore.lar | ~70 | The editor's open documents (freeable C memory) |
| dap.lar | ~1,350 | Debugger: DAP adapter over lldb-dap, values shown as Larimar |
| debugmap.lar | ~230 | Debug map: C names and types of every variable, for the debugger |
| toml.lar | ~229 | TOML parser |

**Total:** ~16,350 lines (91% Larimar, 9% embedded C in runtime.lar)

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

Install it (copies the compiler, `std/` and `MANUAL.md` into `../larimar`):

```bash
./build-bootstrap.sh --verify
cp build/stage2.c larimarc_bootstrap.c     # when it says the bootstrap C is older than src/
```

## License

See individual files for license information.
