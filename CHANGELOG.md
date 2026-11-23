# Changelog

Each version of the compiler (`larimar --version`) and the version of the language it implements.

## Unreleased (1.13)

- **A task talks through a `Channel`** (`std.os.process`): `Task` is `run(channel: Channel): void throws
  ProcessError`, and run() gives nothing back. What one side sends (`send(value)`), the other receives
  (`receive(ms)`), both ways and while it runs. `receive(ms)` waits up to `ms` and gives a `Received`:
  `Message(value)`, `Nothing` or `Finished` (the task ended and everything it sent was received).
  `Process.onMessage(handler)` gives each message to `handler` while `join()` waits.
  `Process.channel()` is the channel of its task and `join()` gives an `int32` (the exit code of a
  program, 0 for a task); `ProcessPool.submit` gives the channel of each task and `wait()` gives nothing.
  A panic there is `Failed: "the program ended (exit 101)"`.
- **`UnsafeTask`: C of its own, in its own process** (`std.os.process`, `std.os.library`). A task
  that implements it declares native interfaces in its class and binds them in `setup(loader)`, once in
  each process: `loader.bind(Sdl, "SDL2")` opens `libSDL2.so`, `libSDL2.dylib` or `SDL2.dll` and finds
  each function there, through a pointer of the header's own type. It needs no `unsafe_c`: a crash in
  that C is a `ProcessError` for the program. A missing library or function is a `LoadError` that ends
  the task saying which. `bootstrap/build.sh` links `-ldl` (`LIBS`), for older Linux.
  A relative library file (`"libs/libSDL2.so"`) is next to the program, not where it was started from.
- **A `type` with fields in a native interface is a struct or a union of C**, by value: `type Point { let
  x: int32; let y: int32; }`, with only the fields used (the header gives the layout, so a union is
  written as a struct). There is no `struct` member in an interface any more (`std.io.files` now says
  `type Stat = struct stat { ... }`). A `T[]` of C structs goes to C as an array, with its count.
- **`[project] unsafe_c` is gone**: a program or a library has no C of its own in its process. A C
  library goes in the native interface of an `UnsafeTask`, whose C runs in the task's own process (a
  crash there is a `ProcessError`); a native interface outside one is an error that says so, and so is
  `unsafe_c` in `larimar.toml`. `larimarc --unsafe-c` stays, for the compiler's tests of std's C.
- **Native interfaces in a module, called only in an `UnsafeTask`**: a program or a library declares a
  native interface in a module (or in a class), opened like those of a task; its functions are called
  only in the methods of a class that implements `UnsafeTask` and in the lambdas written in them, and a
  call anywhere else is a compile error. A library gives the interface and a task with methods that call
  C; a program's task extends it.
- **A task may extend another class**, in any module: the fields of the classes it extends go with it
  (with the same rule: types that cross), and it runs in the other process as its own class. Before, a
  class that extended a task was taken as its parent there, without a word.
- **Callbacks to C: a function and its "this"** (spec §D.10). A parameter of a native function may have
  a function type, and `void*` is a type. A call passes the same pair C asks for: a method and its object
  (`Sqlite.sqlite3_exec(db!, sql, self::onRow, self, null)`), a lambda and itself (`row, row`), or a
  function without state (a lambda that captures nothing, `::compare`) and `null`. The compiler writes a
  trampoline for each pair, which turns the `void*` back into the object or the lambda and converts the
  arguments (`char*` to `String`, `char**` and the count before it to `String[]` or `String?[]`), and
  checks the pair when both are in the same call. A method given to C has no `throws`, and may write its
  "this" with the type of its class (when the callback has more than one `void*`, it must). Also in an
  `UnsafeTask`.
- **Tasks no longer go through `std.os.rpc`**: they have their own messages over shared memory.
  `std.os.rpc` stays, to talk JSON-RPC with other programs; the framing both use is
  `std.os.internal.frames`.

## 1.12.0 — 2026-11-16 (language 1.4)

- **The state of each stage is one object**, which the `Compilation` holds: `Linking` (what linking was
  told and what it found: modules, files, libraries, errors), `Declarations` (what the program declares:
  types, functions, globals, lambdas, what its C needs), `Analysis` (scopes, frames, symbols, what is
  checked at the end, errors) and `Generation` (the function being written, the pieces made on the way,
  errors). Their modules reach them through one variable each (`linking`, `declared`, `analysis`,
  `generation`); `useLinking`... and `pipeline.install` change them, for a compilation with states of its
  own. A pass reads its errors from the compilation (`unit.analysis.analysisErrors`).
- **The C as parts** (`codegen.cprogram`): EmitC makes a `CProgram`, text between its functions and each
  function and lambda whole (`CFunction`, with the names it uses). Prune keeps or drops a function as one
  piece, and cuts only the text between them; NameC names that text part by part. The bodies are text
  still; the C of a program is the same.

## 1.11.0 — 2026-11-16 (language 1.4)

The compiler has no C of its own, names that read, readable C, a pipeline of passes, and everything
under `src/`. Services leave the project: a program that answers is any program, started with a `Process`.

- **The repository**: `src/compiler` (the compiler: `main.lar`, `pipeline.lar` and a folder per stage),
  `src/std` and `src/runtime` (installed, as before, as `std/` and `runtime/`). The compiler finds
  `$LARIMAR_HOME/src/std` when there is no `$LARIMAR_HOME/std`, so `LARIMAR_HOME=src` and the root of the
  repository both work; `larimar test` finds `tests.support` in the folders above the main file's, up to
  the project's.

- **The compiler has no C of its own** and builds without `--unsafe-c`. `larimar lsp` keeps the editor's
  texts in a memory it compacts and answers each question with a `larimarc lsp-worker` started with
  `Process`, the same on every system (no `fork()`; `LARIMAR_LSP_NO_FORK` is gone). `larimar dap` talks
  to lldb-dap through a `Process` and keeps its variable handles in Larimar.
- **`std.io.console`**: `unbufferInput()` and `waitForInput(ms)` (true when there is something to read).
- **Every program starts through `Process`**: `Rpc.start(process)` and `Rpc.startShared(process)` take a
  `Process` (its `program`, `args`, `env`, `quiet`...) and start it; `startShared` adds `LARIMAR_RPC` to
  its `env`. `Rpc.start(program, args)` and `startSharedWith` are gone. Rpc refuses, with
  `RpcError.Ended`, a Process with a task (*the Process has a task, not a program: start it with start()
  and wait for it with join()*), one without a program, and one started already.
- **`os.run` is `os.runCommand`**: a command line of the shell, waited for; its exit code.
- **No services in the project**: `kind = "service"`, services in `[dependencies]`, the generated client
  class and server, and `larimar new --service` are gone. A program that answers with `serve()` is any
  program: another one starts it with `Rpc.startShared(Process { program: "..." })`. The kinds of a
  project are a program and a library.
- **Shared memory, by its name**: `std.os.shared` is `std.os.sharedmemory`, and its streams are
  `SharedMemoryOutputStream` and `SharedMemoryInputStream`. New **`SharedMemorySegment`**:
  `create(name, size)` / `open(name, ms)`, and `get`/`put` of `byte`, `int32`, `int64`, `float64` and bytes
  at an offset, each checked against its size; an `int64` at a multiple of 8 is read and written whole, in
  order. A stream is a queue; a segment is a board.
- **`std.io.bytes`**: `ByteWriter` and `ByteReader`, binary messages (numbers little-endian, a `String` as
  its length and its bytes).
- **`MemoryInputStream` / `MemoryOutputStream` are `BytesInputStream` / `BytesOutputStream`.**
- **The compilation is a pipeline**: a `Compilation` and its passes (`pipeline.lar`: Link, CheckRules,
  Assemble, Analyze, EmitC, NameC, Prune), each of which reports problems instead of throwing; `larimar
  check` and the editor run them up to Analyze.
- **The rules in one place**: `src/semantics/rules.lar`, one object each (`Rule { id(); spec(); check() }`,
  listed by `languageRules()`); each error says its rule: `error[std-own-import]`, `error[no-c-outside-std]`,
  `error[body-needed]`, `error[language-type]`, and the new **`error[internal-import]`**: a module of a
  folder `internal` (`tools.internal.cache`) is imported only by the modules of the folder above it. A test
  breaks each rule.
- **A README.md in each folder of the compiler and in std**: what it does, written by hand, and its API,
  written by `tools/reference.py` from the code (a test fails when they differ).
- **Names that read on their own** in the compiler (`TypeKind`, `optionalOf`, `constantKind`, `method`,
  `classInfo`, `builder`...); the rule is in CONTRIBUTING. `editor.docstore` is `editor.opendocuments`.
- **Readable C.** The runtime and std's C are `lar_` / `Lar` / `LAR_`, in whole words (`LarMemory`,
  `LarMemoryBlock`, `LarResource`, `LarTextBuilder`, `lar_text_to_c`, `LarMethodTable`, `lar_process_*`,
  `lar_shared_*`); a C name of a program that starts so gets a `_`. The compiler's variables are named by
  what they are (`memory`, `line27_temps`, `result`, `new_Shout`, `range_start`), with a number only when
  the name repeats in the function (`codegen.localnames`); the line a check reports is `LINE(27)`. An
  object's header is `.header`, a class's table of methods `methods_Shout`, a type of C
  `LarNative_FILE` and its cell `LarResource_FILE`.
- **Lambdas with big captures** (more than 64 bytes) keep them in the memory where the lambda lives:
  before, every closure of a function type was as big as the biggest (one that captured an
  `int64[25000]` made every `() -> void` 200 KB, and a `ThreadPool` of empty tasks 700 times slower).
- The hint of a value that outlives its memory names the right parameter (`docs: Documents in kept`).

## 1.10.0 — 2026-11-15 (language 1.3)

Processes are used like threads, `native` always means C, and the C of std goes through native
interfaces.

- **Processes like threads** (`std.os.process`): `SystemProcess` is now **`Task`**, and a `Process` runs
  one as a `Thread` runs a `Runnable`: `let p: Process = { run: Resize { ... } }; p.start(); let r: Any =
  p.join();`. A `Process` is `{ program, args }` (another program) or `{ run: task }` (a copy of this
  one), not both; `join()` of a program gives its exit code. `ProcessPool` has the verbs of `ThreadPool`:
  `submit(task)` gives it to a free process, `wait()` gives every result in the order submitted
  (`run` and `runAll` are gone). Only the `Task` of `std.os.process` is a task: an interface of a program
  called `Task` is its own.
- **`native interface`**: `native interface LibM "<math.h>" { function cbrt(x: float64): float64; }`, then
  `LibM.cbrt(x)`. What one or more headers give under one name: functions and values (`Name.f`,
  `Name.N`), types (`type FILE released by fclose;` is a `FILE*`) and structs, which keep their names; an
  interface can `extend` others and be declared in a class (then its C is only for the class's system).
  A header reaches the C only when something it declares is used. `std.math`, `std.os`, `std.io.console`
  and `std.io.files` reach libc this way.
- **`[project] unsafe_c = true`**: a program, a library or a service may declare native interfaces (and
  nothing else of C). A program that uses such a library is built with that C, and every build says it:
  `note: unsafe C (native interface) from: NAME`, and names the pointer types that nothing releases.
- **`native` always means C.** The types of the language are `type String { ... }` and `type Any { ... }`
  in `std.lang`, and what the compiler writes has no body and no `native` (`let length: int32;`,
  `function substring(...)...;`, `Thread.start`, `std.memory.limit`). Only `std.lang` (and `std.memory`)
  has functions without a body; anywhere else it is an error (*Function 'f' needs its body*).
- **`std.platform`**: `Platform`, `OS`, `UnixPlatform`, `LinuxPlatform`, `MacOSPlatform` and
  `WindowsPlatform` moved from `std.os`: `import std.platform { Platform, OS };`. It imports nothing.
- **No interfaces to reach a platform**: `Clock`, `System`, `RandomSource`, `NetSystem`, `FolderSystem`
  and `Executables` are gone; each platform's class has static functions (`PosixClock.now()`), and the
  module chooses with a `switch` on `Platform.current()`. A static function with a body of C of a class
  for one system panics on another, as its methods do.
- **No cycles in std**: a part never imports the module that uses it (`tests/std/cycles_test.lar`).
  `Socket` is in `std.net.internal`; the program's tasks reach `std.os.process` through
  `std.os.process.tasks`, which the compiler writes and std does not import.
- **The parts of std are its own**: a module whose path has `posix`, `windows`, `macos`, `common` or
  `internal` is imported only from std (`std.os.process.internal`: what `Process` and `std.os.rpc` start
  programs with).
- **`[dependencies]`** instead of `[packages]` in `larimar.toml`.
- **The runtime is in `runtime/`**, beside `std/` (it was `std/runtime/`); the install copies both.
- A program whose C includes `<math.h>` is linked with `-lm` on Linux.
- `larimar --version` says `1.10.0 (language 1.3)` (1.9.0 still said 1.8.0).

## 1.9.0 — 2026-11-14 (language 1.2)

No contact with C for the programmer: what Larimar does not have runs in another process, and Larimar
makes those processes and talks to them.

- **Libraries for C programs are gone**: `export function`, `larimar build` of a library into
  `lib<name>.a` or a dynamic one with its `.h`, `[library]` (`type`, `prefix`), `--static` and
  `--dynamic`, and what went with them (handles, `<prefix>_give`, `<prefix>_interface`, the functions of
  a C program). `larimar build` of a library now checks it; a program uses it from `[packages]`.
- **`std.os.shared`**: `SharedOutputStream` and `SharedInputStream`, a stream of bytes from one program to
  another through a ring in shared memory (POSIX `shm_open`, a file mapping on Windows). No system call
  while there is something to read or room to write; a side that waits spins, then naps. If the other
  program ends without closing, the waiting side gets `IoError.Closed`; the name is freed as soon as both
  sides have it, and one left by a program that ended is taken back. `uniqueName(prefix)`.
- **`std.os.rpc`**: JSON-RPC 2.0 with `Content-Length` frames. `Rpc.startShared` (a Larimar program, through
  two shared streams), `Rpc.start` (any program, through its pipes), `Rpc.over` (any streams); `call`,
  `notify`, `begin`/`finish`, `timeout`, `close`, `stop`; `RpcError` (`Failed`, `Ended` with the exit code,
  `TimedOut`). `serve((call) -> ...)` answers on the shared streams it was started with, or on its standard
  input and output; `serveOver` on any streams.
- **`SystemProcess` and `ProcessPool`** (`std.os.process`): a class that implements `SystemProcess` is a
  task; `pool.run(task)` and `pool.runAll(tasks)` run it in copies of the program, which get its fields
  and give back what `run()` returns. The compiler writes, for each module with such classes, how their
  objects go to the other process (`std.os.process.tasks`), and checks their fields (numbers, `bool`,
  `String`, optionals and lists of them) and that they extend no class. A copy runs its globals and then
  tasks, not `main`. A panic in a task is `ProcessError.Failed`, and the pool starts new processes.
- **Services** (`[project] kind = "service"`, `larimar new <name> --service`): the public functions of its
  main module run in its own process. `larimar build` makes its executable, whose main
  (`build/<name>-service.lar`) answers with those functions. A program that names it in `[packages]`
  imports a module written for it: a class (`calc` → `Calc`) with `start()`, `startAt(path)`, the same
  functions as calls (`throws RpcError`), `setTimeout` and `close`. `larimar build` of the program builds
  its services first. What crosses: numbers, `bool`, `String`, optionals and lists of them, `Any`; a
  public function that throws is an error.
- `larimar build --target` is in chapter 26 of the manual. The manual's chapter 23 is now "Other programs:
  calls, shared memory and processes", and chapter 27 "Libraries and services written in Larimar". The C of
  the standard library is described in [docs/std-c.md](docs/std-c.md) for whoever maintains std, and in
  Appendix D of the specification (language 1.2, chapter 19 "Libraries, services and tasks").
- The compiler is 21,423 lines (about 440 fewer, with the services and tasks added), and the suite has
  248 tests (`tests/std/shared_test.lar`, `rpc_test.lar`, `pool_test.lar`, `tests/project/services_test.lar`
  are new). `docs/compiler-reference.md` is written by `tools/reference.py`.

## 1.8.0 — 2026-11-13 (language 1.1)

Larimar has no C of its own outside the standard library, and a library written in Larimar is shared as
source.

- **C is only the standard library's.** `cinclude`, `ccode`, the `native` declarations and the functions
  with a body of C (in classes too) are an error in a program and in a library: *ccode is only for the
  standard library: C is written there, and a program uses what std gives.* All the C a program runs is
  part of Larimar, and a library written by someone else cannot bring C the compiler does not check. For
  what std does not have, a program talks to another program (`std.os.process`). `larimarc --unsafe-c`
  lifts the rule for the compiler's own sources (its editor tools still have C) and its tests of std's C.
- **C function pointer types and `Context` are gone** (`native type F = (A) -> R`, callbacks with a
  context), with what made them work: trampolines, the `ctx` information of native functions,
  `rt_res_lent`.
- **A library written in Larimar is used as source.** `[packages]` names the folder of the library's
  project (`textkit = "../textkit"`), and the program compiles its modules with its own: one C, one
  runtime, and the whole language on both sides (interfaces the program implements, lists, enums,
  `throws`), checked as one program. Its modules are `<name>` and `<name>.<part>`; a program module with
  one of those names is an error. A library's own `[packages]` come with it; two libraries with the same
  name in different folders are an error. `export` has no effect there.
- **Packages are gone**: no `.lpk`, no `.interface`, no generated `.lar` binding, no interface hash
  between a program and a library (`project/lpk.lar` is deleted).
- **For C programs**, `larimar build` of a library makes `lib<name>.a` (the default; `type = "static"`) or
  a dynamic one (`--dynamic`), and `<name>.h`, which ends with what to link it with. `<prefix>_interface()`
  gives the hash of that `.h`. Everything else of the library for C stays: handles, texts to free,
  functions of the C program with their `void*`, `in default` and `in self`, `<prefix>_give`, `thread safe`.
- **`export function` is only for a library.** In a program it is an error.
- **`[c]` has only `compiler` and `flags`** (and its platform sections): `sources`, `include_paths`,
  `static_libraries`, `static_library_paths`, `dynamic_libraries` and `dynamic_library_paths` are gone.
- The compiler is 21,861 lines, about a thousand fewer. The manual of libraries (`docs/libraries.es.md`)
  is rewritten, with every case built and run (54 runs, with the sanitizers), and
  `docs/compiler-libraries.es.md` describes how it is made inside.

## 1.7.0 — 2026-11-11

The standard library, organized: each module keeps its API, and the class of each platform goes in a
part of it, in the folder of its name.

- `std.time`, `std.os`, `std.io.files`, `std.io.console`, `std.crypto`, `std.os.process`, `std.net` and
  `std.net.tls`: their platform classes moved to `time/posix.lar`, `os/windows.lar`, `net/openssl.lar`,
  `net/tls/macos.lar`... The interfaces they implement are public (`Clock`, `System`, `NetSystem`...),
  so a platform of one's own can be added.
- C that the parts of a module share goes in a part of its own (`process/common.lar`,
  `net/tls/common.lar`): the parts reach the C before the module.
- A module whose parts bring the C headers (cinclude, ccode) gets no prototypes of ours for its natives.
- `std.os.process`: the check of what can be run is `Executables` (`Runnable` is std.lang's).
- A module opened alone (`larimar check std/time.lar`) is the same module its parts import back.
- `CONTRIBUTING.md`: how the code is organized (modules and parts, platforms, the order inside a file).
- Interfaces can have static functions (`static function unit(): Shape { ... }`, called `Shape.unit()`):
  with a body and no `self`. Their other methods are signatures, as before.
- `Platform.current()` and `Platform.name()`, static functions of the interface `Platform`, replace
  `os.platform()` and `os.platformName()`.
- `--target <platform>` (`linux`, `macos`, `windows`, `unix`): the C of one platform only. A `switch` on
  `Platform.current()` becomes its arm, the C of that platform's classes has no `#if`, and that of the
  others is not written. Without it, as before, the same C builds on every system.
- A C struct known by its tag is named without `c"..."`: `native struct AddrInfo = struct addrinfo { ... }`,
  `native type Tm = struct tm*;`.
- `std.math`: C's math by its names (`sqrt`, `pow`, `floor`, `sin`...), `PI`, `E`, `min`, `max`, and
  `Random`, a fast sequence that repeats with its seed.
- `larimar`: its commands are a `switch`, and its help a text block.
- The compiler: `codegen/runtimeselect.lar` and `codegen/prune.lar` are one module (one way to cut C into
  pieces and to follow what is reached, for the program and for the runtime); the generated C is the same.
  A resource type has one releaser; fixed C is written as text blocks; what `#when` left behind is gone.
- A file of a copy of the standard library (a repository's `std/crypto.lar`, open in an editor whose
  installed Larimar is another) is checked against that copy: it showed *Switch value: expected
  RandomSource but got std.crypto.posix.UrandomSource*.
- A library takes **functions of the program**: a parameter of a function type in an export function
  (`handler: (Request) -> String`), called inside like any function. A Larimar program gives it a lambda,
  with what it captures; a C program, a function and a `void*`. The function gets objects of the library
  (it uses them, and cannot keep them) and gives a number, a `bool`, nothing or a text, which lives in the
  block of the library that called it (C gives it with `<prefix>_give`). `in default` on the parameter
  says the library keeps the function: what it uses then lives as long as the program.
- A **method** of a class of a library takes functions too, and may keep one in its object with **`in self`**
  (`function get(path: String, handler: (Request) -> String in self): void`): what the program's function
  uses then lives at least as long as the object, and dies with it.
- A Larimar program uses the package of a library; a library compiled with `--static` or `--dynamic` is
  for C programs, and is no longer named in `[packages]`.
- **Fixed**: an object of a synchronized class could be created around a list that its creator kept using,
  or with a plain function that touched a global: two threads then used the same data without the lock (a
  data race, found by review and confirmed with the thread sanitizer). Now it is created with values or
  with what is written right there, and a field that is a function is `thread safe`. A library that calls
  the program's function from another thread has that in its `.lar`, and the function is checked for it.
- **Fixed**: an export function of a library could be declared to return a function, which does not cross.
- **Fixed**: a library that created something `in default`, or gave a lambda where an interface is
  expected (a `Thread`'s `run`), did not link with a program that did the same (*multiple definition of
  rt_default_mem*): those two names of its C were not its own. Now only its export functions are seen.
- **Fixed**: a method that a subclass overrides now has what the override returns. A call through the
  base class could keep, for the whole program, a text that the override returned from an argument that
  lived only in a block (a use after free). Found by review, with its test.
- The parser is a class, `Parser` (the tokens and where it reads), with no state outside it: two can read
  at once (the one of a `${...}` inside the one of its file). Its grammar is in `syntax/parser/`:
  `declarations`, `natives`, `types`, `statements`, `expressions`.
- The compiler's longest files are split by theme, each with the folder of its name:
  `semantics/analyzer/` (declarations, classes, statements, flow, compact, narrowing, threads, order),
  `semantics/expressions/` (constants, conversions, literals, operators, calls, switches), `codegen/gen/`
  (types, classes, statements, library) and `codegen/expressions/` (strings, operators, calls, clone,
  lambdas, patterns). No file of them passes 900 lines; the generated C is the same.
- The result of a method of a struct, or of a class without subclasses or superclass, is read as that of
  a function: it points only to the arguments its body can return. `p.expect(kind, "... ${name} ...")`
  gives a token that lives where `p` lives, whatever the message.
- A library written in Larimar is built into a **package**: `build/<name>/` with the library in C
  (`<name>.c`), the C it brings (`c/`: the `sources` and `include_paths` of its `[c]`, of every platform),
  its `.h`, its `.lar` and its `.interface`. A program names the folder in **`[packages]`**
  (`textkit = "libs/textkit"`) and the package is compiled with it: one folder for every platform, nothing
  compiled per system. `--static` and `--dynamic` (or `[library] type`) still compile the library, for C;
  such a folder is named in `[packages]` too.
- `larimar build` also writes the package in one file, **`build/<name>.lpk`**: a zip without compression,
  which a program names in `[packages]` (`textkit = "libs/textkit.lpk"`) and gets unpacked in
  `build/packages/`. A package brings the C libraries already compiled that its library names
  (`lib<name>.a` in its `static_library_paths`, per platform in `[c.linux]`...), and its `.interface` says
  which packages the library uses: the program names those too, or the error names the one that is missing.
- `[packages]` is the one way to use a library written in Larimar. `[dependencies]` with `deps/` (Larimar
  code used as source) is gone, and a library is no longer found among `static_libraries` by its
  `.interface`. The plugin example in the manuals is a generic `mytool`.
- `docs/libraries.es.md`: the manual of libraries. Every scenario of writing, publishing and using one, and
  every attempt to misuse one that was tried, each with its code and the output it gave when it was run. `docs/compiler-reference.md`: every function of the compiler, with
  its signature and its comment, generated from the source.
- **A method of an interface is marked `override`** (a change to the language that existing programs must
  follow): `class Circle implements Drawable { override function draw(): void { … } }`. The rule is now
  one: `override` marks a method the class did not introduce, of its superclass or of an interface it
  implements; a method that is both has one. Without it: *Method 'draw' in class 'Circle' implements
  'Drawable' and REQUIRES the 'override' keyword*. An `override` on a method that is in neither is an
  error that says so (*has 'override' but redefines nothing: the class has no superclass, and no interface
  it implements has it*), so a method left behind when an interface changes is found. The standard
  library, the tests and the manuals follow it.
- The page said v1.1: it says v1.7.
- The compiler: what a library does with a function of the program is one module, `codegen/gen/callbacks.lar`,
  whose header tells the whole path and where each piece is; unused imports and an unused function are
  gone. The generated C is the same.
- `docs/compiler-libraries.es.md`: how libraries are made inside the compiler, for who changes it (the
  files, the path of a call, of an object and of a function of the program, and what to touch to change
  each thing). `CONTRIBUTING.md` shows the compiler from a file to a program, the folders, and the
  bootstrap. These two and the manual of libraries have diagrams (Mermaid, which GitHub draws).
- The manuals and the specification are in `docs/`, next to the page that shows them (`manual.html`
  reads the ones published with it). The manual explains `native struct` and `native type`, and where
  `c"..."` is needed; the page no longer speaks of `#when`.

## 1.6.1 — 2026-11-11

- The standard library and the compiler use `native function f(...): T { C }` where a C function in a
  `ccode` was declared again as a native to be called once: one place for each (`StringBuilder`'s text,
  `ByteText`, the TLS errors, the editor's documents, numbers as text).
- The handles of `std.net` and `std.net.tls` name their C types (`native type TlsHandle = LmTls*;`), so a
  body of C reads their fields.
- `std.lang`: the C of a kept type or body stays with it (a `ccode` that only defines a struct).
- The lexer: a `native function` right after a class or another body of C is read correctly.

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
