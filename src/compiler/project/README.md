# project: larimar.toml, the C compiler and the tests

What goes in: a project's folder (its `larimar.toml`) or a file. What comes out: an executable, or the
results of its tests.

- `cc.lar`: finds the C compiler (the system's, or the bundled tcc), and the libraries the C needs from
  what it includes (`<math.h>`: `-lm`; threads; OpenSSL).
- `libraries.lar`: the libraries of `[dependencies]` (and theirs), each a folder with its `larimar.toml`
  (`kind = "library"`), checked; their modules are compiled with the program.
- `testing.lar`: `larimar test`: a file of `test function`s becomes a program that runs each one in a
  process of its own, so that a panic or a crash is one failed test.
- The commands themselves (`larimar build`, `run`, `new`, `test`) are in `main.lar`.

## Its API

<!-- api: written by tools/reference.py from the code; not edited by hand -->

- **`project.cc`**: calling the C compiler and other programs (larimar build, larimar test).
  - `function windows(): bool`
  - `function mac(): bool`
  - `function quote(a: String): String`: Quotes an argument for the shell
  - `function commandLine(args: String[*]): String`: The arguments joined, each quoted: a command for os.run
  - `function systemLibraries(c: String): String[*]`: What the generated C needs from the system when linking: threads, sockets, TLS
  - `function selfPath(): String`: The compiler itself (bin/larimarc), to run it as another process
  - `class CCompiler`: The C compiler of a build: the program and the arguments that go right after it
  - `function bundledTcc(home: String): String`: The tcc that comes with Larimar on Linux and Windows ($LARIMAR_HOME/toolchain/tcc), or ""
  - `function systemCompiler(): String`: The system's C compiler: cc, gcc or clang (on Windows gcc, clang or cc), or "" when there is none
  - `function chooseCompiler(home: String, wanted: String, script: bool, tls: bool, problem: String[*]): CCompiler?`: The C compiler for a build
  - `function installHint(): String`: The command that installs a C compiler here
- **`project.libraries`**: the libraries written in Larimar that a project uses, as source
  - `class LarimarLibrary`: A library of [dependencies]: its name (its module) and the folder of its modules
  - `function larimarLibraries(dir: String, config: Any, problems: String[*]): LarimarLibrary[*]`: The libraries of a project's [dependencies], and theirs
- **`project.testing`**: larimar test, the test runner
  - `class TestSettings`: How the tests are compiled: the project's [c] settings, or the defaults when there is no project
  - `class TestFunction`: A test function of a file
  - `function testFunctions(source: String in default): TestFunction[*]`: The test functions of a file, in order (none when it has syntax errors: the compiler shows them)
  - `function hasMain(source: String in default): bool`: Whether the file declares a main of its own
  - `function withMain(source: String, tests: TestFunction[*]): String`: The file with a main added: `program <name>` runs that test and ends with 0 (it passed), 1 (a check failed), 3 (it was skipped) or 2 (no test has that name)
  - `function runTests(args: String[*], s: TestSettings in default): int32`

<!-- /api -->
