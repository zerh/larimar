# Changelog

Each version of the compiler (`larimar --version`) and the version of the language it implements.

## 1.3.1 — 2026-11-08

- The repository is reorganized: the manuals and the specification are in `doc/` (`manual.md`,
  `manual.es.md`, `spec.md`), the bootstrap in `bootstrap/` (`larimarc.c`, `build.sh`, `build.ps1`), the
  debugger formatters in `tools/debuggers/` and the tcc scripts in `tools/tcc/`. To build:
  `./bootstrap/build.sh --verify`.
- The installation has `doc/` (the manuals and the specification) instead of `MANUAL.md`.
- License: MIT.
- `CHANGELOG.md`, `CONTRIBUTING.md` and issue templates.

## 1.3.0 — 2026-11-07

- Libraries written in Larimar: `kind = "library"` builds `build/<name>/` with `lib<name>.a` (or the
  `.so`/`.dylib`/`.dll` with `type = "dynamic"` or `larimar build --dynamic`), `<name>.h` for C,
  `<name>.lar` for Larimar and `<name>.interface` with the interface hash. The classes of a library go to
  C as handles, with their fields and methods.
- `export function f(...) = c_name`; export functions return `String` and `String?` (copies that C frees).
- `native function f(): String released by free`: a text that C makes is copied, then released.
- `[c]` has `static_libraries`, `static_library_paths`, `dynamic_libraries` and `dynamic_library_paths`
  instead of `libraries` and `library_paths`.
- `larimar new <name> --library`.

## 1.2.0 — 2026-11-07

- `native` replaces `extern`: native functions, types with members, structs, constants and variables,
  with `= c_name`. Callbacks with lambdas through `Context`. `lar"name"` inside `c_code`.
- The tests are test functions grouped by topic, with `tests.support.compiler`.

## 1.1.0 — 2026-11-05

- The releases for Linux and Windows bring tcc: `larimar file.lar` runs a file at once.

## 1.0.0 — 2026-11-03

- The manuals with their examples as `ts` blocks. Language specification 1.0.

## 0.5.2 — 2026-11-03

- The hints for lambda captures name the memory to copy into.

## 0.5.1 — 2026-11-02

- Clearer messages for lambda captures; lifetime errors name what lives too little and give the code
  that fixes it.

## 0.5.0 — 2026-11-02

- Plugins, `deps/`, the standard library reorganized (io, os, encoding, time, crypto), `TcpServer` with
  TLS, limits, keep-alive and poll.

## 0.4.1 — 2026-11-01

- Language specification 1.0, left-to-right evaluation, `length` as a property, shortest decimals, a
  check of global initialization, `larimar test --list/--json/--test`.

## 0.4.0 — 2026-11-01

- Test functions and `larimar test`, `std.test`, `std.process`, `std.toml`, `[c.<platform>]`, sorting
  lists; the compiler in one folder per stage.

## 0.3.0 — 2026-10-31

- `std.process`; the tests of the editor, the debugger and TLS written in Larimar; `skip()` in `std.test`.

## 0.2.1 — 2026-10-30

- The debugger on macOS, and the manual in English and Spanish.

## 0.2.0 — 2026-10-30

- Thread-safe functions, TCP, UDP and TLS servers in `std.net`.

## 0.1.0 — 2026-10-28

- The first version.
