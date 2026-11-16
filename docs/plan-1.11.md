# Plan for 1.11

What was agreed after 1.10.0, in the order it will be done. Each step ends with the compiler compiling
itself to the same C, and every test passing.

## Where it stands (1.11.0)

Done: 1 (no C in the compiler), 2 (names), 3 (readable C), 4 (rules.lar, the READMEs and their test,
`internal` folders), 6 (everything under `src/`), 7 (Process and Rpc, `os.runCommand`), 8 (no services),
9 (shared memory: `std.os.sharedmemory`, `SharedMemorySegment`, `std.io.bytes`, `Bytes*Stream`) and
10 (big captures behind a pointer).

Of 5, the first part: a `Compilation` and its passes (`src/compiler/pipeline.lar`: Link, CheckRules,
Assemble, Analyze, EmitC, NameC, Prune), the rules as objects with their ids in the errors, and the names
of the C from one place (`codegen/localnames.lar`). What is left of 5, for the next versions: the globals
of the linker, the analyzer and the generator into `Compilation`, one by one; a pass Lower; and the C as
structure (`CProgram`, `CFunction`, `CBlock`), with Prune on its pieces instead of on text.

## 1. No C of its own in the compiler

- `src/editor/docstore.lar`: in plain Larimar (a table of the open documents).
- `src/editor/lsp.lar` and `src/editor/dap.lar`: start programs and read from them with `std.os.process`
  (and std.os.shared where it fits), without `ccode` or functions with a body of C.
- Then the compiler builds without `--unsafe-c`, and the editor shows no errors in its own sources.

## 2. Names in Larimar that say what they are

- Rule: a name reads on its own, without going to its definition. Allowed short: `id`, `url`, `json`,
  `cType`, `cName`, and `i`, `j`, `k` in a loop.
- Fields: `ck` -> `constantKind`, `cf` -> `constantFloat`, ...
- Functions: `tname`, `sam`, `prim`, `optT`, `ptrT`, `funcT`, `arrayT`, `newFn`, `rVar`, `hex4`, `noC`,
  `conv`, `m`, `f`, ...
- Locals: `sb`, `ps`, `mi`, `st`, `so`, `ci`, `pt`, `ot`, `co`, `pr`, `ft`, `rm`, `im`, `pw`, `ni`, ...
  (about 150 names in all).
- One folder at a time, one commit each. The rule goes into CONTRIBUTING.

## 3. Readable C, generated and of the runtime

- The runtime: `rt_` -> `lar_`, `Rt` -> `Lar`, whole words: `RtMem` -> `LarMemory`, `RtChunk` ->
  `LarMemoryBlock`, `RtRes` -> `LarResource`, `RtSb` -> `LarTextBuilder`, `rt_str_cz` -> `lar_text_to_c`,
  `RtVTableHead` -> `LarMethodTable`.
- Temporaries named by what they are: `mem_0` -> `main_memory`, `tmp_2` -> `line27_temps`, `t_5` ->
  `toupper_result`, `obj_8` -> `new_Shout`, `ret_10` -> `result` (a number at the end only when one repeats).
- The line of a panic as `LINE(27)`, not a bare number.
- Inner fields: `._h` -> `.header`, `vtable_` -> `methods_`, `Ext_FILE` / `Res_FILE` -> `LarResource_FILE`.
- std's own C: `lm_proc_*` -> `lar_process_*`, `lm_sh_*` -> `lar_shared_*`, ...
- The debugger (`dap.lar`) and the tests that look for names in the C change with it.

## 4. Rules in one place, and a map of each folder

- `src/semantics/rules.lar`: the tables of the language's rules, each a short function with its comment
  (modules only std imports, what the compiler writes, the platforms, what crosses to another process,
  what `unsafe_c` allows). The spec links to it.
- A `README.md` in `src/syntax`, `semantics`, `codegen`, `project`, `editor` and `std`: a short part by
  hand (what the folder does, what goes in and out, the ideas the code does not show) and a generated part
  (its public functions: its micro API), written by `tools/reference.py`.
- A test that fails when a generated part does not match the code.
- `*/internal` folders of the compiler, imported only by their folder (as std's).

## 5. The generation as a pipeline (in 1.11)

- One compilation is an object (`Compilation`: modules, facts, problems, the C, by parts), with no
  globals; the stages are passes over it (`Pass { name(); run(unit) }`, which reports problems instead of
  throwing): Parse, Link, CheckRules, Analyze, Lower, EmitC, Prune, NameC.
- Rules are objects (`Rule { id(); spec(); check(unit, module) }`) listed in `languageRules()` of
  `rules.lar`; each error says its rule (`error[std-own-import]`), and a test checks that every rule has a
  case that fires it.
- The C is built as structure (`CFunction`, `CBlock`), and `Prune` works on its pieces, not on text.
- The names of the variables of each C function come from one `LocalNames`: `locals.unique("toupper_result")`
  gives that name, or `toupper_result_2` when it is taken.
- Getting there: first each current stage wrapped as a Pass (the same C), then the globals into
  Compilation one by one, then the rules into rules.lar, and at the end EmitC and Prune on CProgram.

## 6. The organization of the repository (in 1.11, decided)

- Everything under src/: `src/compiler/` (main.lar, syntax/, semantics/, codegen/, project/, editor/),
  `src/std/` and `src/runtime/` (what an install copies as $LARIMAR_HOME/std and /runtime). The compiler
  builds itself with LARIMAR_HOME = src/; its main is src/compiler/main.lar, so `std.io` is always std.
- build.sh, build.ps1, the CI, the paths of the tests and the docs change with it.
- The folders of the compiler by stage of the pipeline, each with its README and its micro API.

## 7. Every program starts through Process

- `Process` says what runs (program, args, env, quiet...); `Rpc.start(process)` (its input and output)
  and `Rpc.startShared(process)` (shared memory: it adds LARIMAR_RPC to its env before starting it) talk
  to it; `Rpc.over(input, output)` stays. `startSharedWith` goes; Rpc keeps its static form and its name.
- `Process { run: task }`, `ProcessPool` and the generated clients of services use `Rpc.startShared(process)`.
- Rpc refuses, with RpcError.Ended: a Process with a task (*the Process has a task, not a program: start
  it with start() and wait for it with join()*), one without a program (*the Process has no program*), and
  one started already (*the Process was started already: Rpc starts it*). A Process with `run` is used as a
  thread is; one with `program`, directly or through Rpc.
- `os.runCommand(command)` stays in std.os, named `os.runCommand(command): int32` (the shell's command, waited
  for, its exit code).

## 8. No services in the project (decided)

- `kind = "service"` goes, and with it: services in [dependencies], their build at each build of the
  program, the generated client class and server, `larimar new --service`, src/project/services.lar
  (contract, clientSource, serverSource), buildServices / buildService in main.lar, the linker's
  libraryServices, tests/project/services_test.lar, and their parts of the manuals (chapter 27), the spec
  (chapter 19) and docs/compiler-libraries.es.md.
- A service is any program that answers with serve(); another program starts it from a path of the
  system (`Process { program: "/usr/local/bin/images" }`, `Rpc.startShared(process)`) and orchestrates
  it as it wants. The kinds of a project are a program and a library.

## 9. Shared memory, by its name (in 1.11)

- `std.os.shared` becomes `std.os.sharedmemory`; `SharedOutputStream` / `SharedInputStream` become
  `SharedMemoryOutputStream` / `SharedMemoryInputStream`.
- New `SharedMemorySegment`: `create(name, size)` / `open(name)`, `get` / `put` of numbers at an offset,
  each one checked against the size. A stream is a queue (each message once, in order); a segment is a
  board (the latest value, overwritten).
- `ByteWriter` / `ByteReader` in std, for binary messages over the streams.
- `MemoryInputStream` / `MemoryOutputStream` (std.io) become `BytesInputStream` / `BytesOutputStream`.

## 10. Lambdas that carry big captures (a bug, in 1.11)

- Every lambda of a type is as big as the biggest one in the program (a union of their captures): one
  that captured an int64[25000] made every `() -> void` 200 KB (a ThreadPool of empty tasks went from 1 µs
  to 700 µs a task; bench/concurrency). Captures past a small size go behind a pointer, in the lambda's
  memory.

## Graphics: Lienzo and Pincel (decided; after 1.11)

- **Lienzo comes with Larimar** (`bin/lienzo`): the program that opens a window and paints anything it
  is told. It is general: a game framework, a UI library or a chart use it the same way.
- **`std.lienzo`**, its client in std (versioned with Lienzo, since they share the protocol):
  `class Lienzo extends Process` with title, width, height, fullScreen, resizable; `program` empty means
  `$LARIMAR_HOME/bin/lienzo`, and another path is another Lienzo (a version, a build of one's own, a fake
  for tests). `start()` starts it and opens the window (ProcessError when it cannot: one throws type);
  `join()` waits until the window is closed; a Lienzo with a `run` task is refused. Then textures by path,
  `nextFrame()` / `showFrame(frame)` with the frame's drawing commands (textures, rectangles, lines,
  text, clip, transform) sent as one batch, and the events that come back. Low level: no game loop, no
  widgets.
- The first thing both say is their protocol version: a Lienzo that speaks another one makes `start()`
  fail with both versions in the message (*/opt/lienzo speaks protocol 3; this program, 2*).
- **Pincel** is a framework in the manner of LibGDX on top of std.lienzo (Game, SpriteBatch, Texture,
  Pixmap, cameras): a library of its own, not std. A UI library would be another one on the same base.
- What else std gives, general and useful to anything: Process, Rpc, SharedMemorySegment, the
  SharedMemory streams, ByteWriter / ByteReader.

- Lienzo (it was larimar-window) is written in Larimar (a project with
  `unsafe_c = true`), has the window and all the drawing: SDL3 of the system, then SDL2 (both with
  SDL_Renderer on the GPU), then its own fenster with a software rasterizer. Nothing of SDL is shipped.
  `LARIMAR_WINDOW=fenster` forces one.
- The program has an API in the manner of LibGDX (no C, no window): `Texture` (loaded by path, once:
  Lienzo reads the file and gives an id), `SpriteBatch` (begin, draw, end), `ShapeRenderer`,
  `BitmapFont`, `OrthographicCamera`, and `Pixmap` for pixels computed by the program (Mode 7), sent as a
  texture's new content.
- Each frame is a batch of instructions in binary (one byte of kind and fixed fields: draw texture 7 at
  x, y with rotation, scale, color...), written into a SharedMemorySegment with three slots: the program
  writes the free one and sets `ready` (only it writes it); Lienzo sets `showing` and the number of
  the last frame shown (only it writes them), and the program waits when it is two frames ahead.
- Events (keys, mouse, closed) come back through a SharedMemory stream, as small binary messages, read
  with ByteReader. Opening the window and loading textures may go through Rpc.
- `Game { create; render(seconds); dispose }` and `Window.run(game)`, as LibGDX's ApplicationListener.
- What fenster cannot do (GPU speed, gamepads, resize) is asked with `window.supports(...)`; what a
  program needs and is not there is a WindowError that says how to install SDL.
- If Lienzo ends (a driver crashes), Pincel starts it again and gives it back what it had:
  the window (title, size, full screen), every texture by its path and with its same id, the last
  content of each Pixmap. The game's state is the program's and is not touched. Held keys get a release
  event (none stays stuck). At most 3 restarts a minute, then a WindowError (a driver that always fails).
  `Game.windowRestarted()` (empty by default) tells the program, if it cares.
- 3D later in the same Lienzo (OpenGL 3.3 through SDL): the program describes the scene (models
  by path, transforms, camera, lights), as Xoppa's tutorials.
- A UI (in the manner of microui) is a program apart, which receives messages and draws.

## Also noted

- BytesInputStream / BytesOutputStream copy byte by byte: how to copy in blocks is to be seen later.

- No server made of processes yet (several processes accepting on one port): std.net has no
  SO_REUSEPORT nor a way to give a socket to another process. Needed to compare a server of threads with
  one of processes (bench/concurrency).

- Later, not now: a client whose methods the user configures, each one making its call when it is
  called (perhaps giving the text of the command to send, or writing it to a stream).

- `className()` of an object and of an `Any` (a method without a body in std.lang; `RtClass` stays the
  runtime's).
- Functions with a body of C of std grouped in named wrappers (`native type TextBuf` with methods): the
  parser has to accept C bodies in the methods of a `native type`.
- `std.net`'s sockets through native interfaces (their headers change with the system).
- Pincel and Lienzo: see "Graphics" above.
