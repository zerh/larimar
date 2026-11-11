# Changelog

Each version of the compiler (`larimar --version`) and the version of the language it implements.

## 1.6.0 — 2026-11-11

One way to reach C less: what each system does differently is only a class for its platform.

- `#when`, `#else` and `#end` are gone from the language (and the types declared once per platform with
  them). The standard library no longer used them; a class for each platform does the same, checked by
  the compiler, and `switch (os.platform())` chooses it.
- A body of C is a native function: `native function f(...): T { C }`, at the top level, in a class (a
  method of its platform) or static. `function f(): T ccode { C }` is no longer the way.
- `StringBuilder`'s methods are plain Larimar over its C (no `native ... = expression` left in `std.lang`).

## 1.5.0 — 2026-11-10

- The platforms are interfaces of `std.os`, one inside the other: `Platform`, `UnixPlatform`,
  `LinuxPlatform`, `MacOSPlatform` (both extend `UnixPlatform`) and `WindowsPlatform`. A class is for a
  platform by implementing it (`class PosixClock implements Clock, UnixPlatform`), and the compiler finds
  it through the types, aliases and superclasses included, not by its name. They replace `OnUnix`,
  `OnLinux`, `OnMacOS` and `OnWindows`.
- `os.platform()` gives `enum OS { Linux, MacOS, Windows, Unix }` (it was `Platform`).
- Interfaces can extend others: `interface Pet extends Named` has the methods of `Named`, and a class that
  implements `Pet` is also a `Named`.
- The compiler: the lexer is a class, `Lexer { src, line }`, with no global state; its main loop is a
  `switch`.
- `.gitattributes`: `.lar` files keep `\n` on Windows too (the runtime's C is read from them).

## 1.4.0 — 2026-11-10

The language is still 1.0. Its C reads as C, and what each system does differently is Larimar: the
repository has no `.c` file but the bootstrap, and the modules of the standard library choose their
system with a `switch`, not with `#if` (only the runtime, the C under every program, keeps its own).

- `c_code` is `ccode`, `c_include` is `cinclude`, and the C text of a native declaration is written
  `c"..."` (`native function root(x: float64): float64 = c"sqrt";`).
- A function or method can have a body of C: `function now(): int64 ccode { ... }`. It sees its
  parameters by name with their C types, and Larimar with `lar"name"`.
- A class can have its own `cinclude` and `ccode`. A class that implements `OnUnix`, `OnLinux`, `OnMacOS`
  or `OnWindows` (std.os) is for that system: its C goes only into that system's build, inside the `#if`
  the compiler writes, so the same generated C still builds on all three.
- `os.platform()` gives `enum Platform { Linux, MacOS, Windows, Unix }`, for a `switch` that chooses the
  class of each system (`os.platformName()` is the text it was before).
- An interface whose classes have no fields (or are synchronized) is shared by threads like a value.
- The standard library is written that way: `std.os`, `std.time`, `std.io.files`, `std.io.console`,
  `std.crypto`, `std.net`, `std.net.tls` and `std.os.process`, an interface and a class for each system.
- The runtime is the `ccode` of `std/runtime/*.lar`, read when a program is generated, instead of text
  inside the compiler (`src/codegen/runtime.lar` is gone): changing it no longer needs a new bootstrap.
- `std.thread`: `ThreadPool` (`{ threads: 8, queue: 100 }`, `submit`, `wait`) for a batch of tasks.
- `std.net`: `EventLoop` (`watch`, `unwatch`, `wait`, `isReady`), the loop that `TcpServer` uses for
  its listener and its kept connections, with no limit of 1024 sockets; `TcpSocket.number()` and
  `TcpListener.number()`.

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
