# Contributing to Larimar

Thank you for helping. Bugs, ideas and pull requests are welcome, in English or Spanish.

## Build and test

Only a C99 compiler is needed (gcc or clang; on Windows, MinGW's gcc):

```sh
./bootstrap/build.sh --verify --test     # build, check that it compiles itself, run the tests, install ../out/larimar
tests/run-tests.sh memory                # only the tests whose path or name has "memory"
bin/larimarc test tests/std              # only larimarc test, on one folder
```

`--verify` compiles `src/` three times; stage 2 and stage 3 must be identical. If it says that
`bootstrap/larimarc.c` is older than `src/`, update it in the same commit:

```sh
cp build/stage2.c bootstrap/larimarc.c
```

## Changes

- **A bug is a test first**: a `test function` in the file of its topic (`tests/c/`, `tests/memory/`,
  `tests/language/`...). `tests/support/compiler.lar` has what the compiler's tests need:
  `failsWith(source, error)`, `runs(file, lines)`, `panics(file, text)`, `memoryError(file)`.
- **A change of the language** goes in `doc/spec.md` and in both manuals (`doc/manual.md`,
  `doc/manual.es.md`), with an example that runs. Something new in the language goes into the compiler
  first; `std/` may use it once the bootstrap is regenerated.
- **Messages and comments** say what happened and what to do, in plain words.
- One topic per pull request, with the tests passing (`./bootstrap/build.sh --verify --test`).

## Layout

`src/` is the compiler, `std/` the standard library, `tests/` the tests, `doc/` the manuals and the
specification, `bootstrap/` the compiler in C and the scripts that build it, `tools/` the debugger
formatters and the tcc of the releases, `docs/` the website. See the README.

## License

By contributing you agree that your contribution is under the [MIT license](LICENSE).
