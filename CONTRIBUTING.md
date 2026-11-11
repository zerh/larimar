# Contributing to Larimar

How the code is organized, so that it stays easy to read and to change.

## Modules and their parts

- A file is a module: `std/net.lar` is `std.net`.
- A module that grows is split by creating **a folder with its name, next to the file**. The file stays
  as the entry: its public API (or its main class), what the others import. The folder holds its parts:
  `std/net.lar` and `std/net/posix.lar`, `std/net/windows.lar`; `src/syntax/parser.lar` and
  `src/syntax/parser/statements.lar`.
- Import modules with a name: `import std.io.files as Files;` and write `Files.readString(...)`.

## Platforms

- What changes between systems is a class for each platform, marked with the platform it is for
  (`implements UnixPlatform`, `LinuxPlatform`, `MacOSPlatform`, `WindowsPlatform`), and chosen with a
  `switch (os.platform())`. There is no `#if` written by hand.
- Each platform's class goes in a part of the module (`time/posix.lar`, `time/windows.lar`). The parts
  reach the C before the module that imports them: C shared by several parts goes in a part of its own
  that they import (`process/common.lar`).
- C is written where it is used: `native function f(...): T { C }` for a function whose C is only for it;
  `ccode { }` only for what several share (a struct, a helper).
- Names of C helpers: `lm_<module>_<thing>` (`lm_proc_start`).

## Inside a file

1. The comment of the module (what it is, an example) and the imports.
2. The public API.
3. The private details, in Larimar.
4. At the end, the C: `ccode`, native functions with a body of C.

- `self.` is always written: it shows what is state.
- `switch` with patterns instead of chains of `if (x is ...)`.
- Files of a few hundred lines: past ~800, split the module in parts.
- No mutable globals in the compiler: each phase is a class (`Lexer`, `Parser`, ...).

## Changes

- `./bootstrap/build.sh --verify --test` must pass: the compiler builds itself (stage 2 == stage 3) and
  every test passes. A change to the compiler regenerates `bootstrap/larimarc.c`.
- The language is described in `doc/spec.md` and taught in `doc/manual.md` and `doc/manual.es.md`: a
  change to the language changes the three.
