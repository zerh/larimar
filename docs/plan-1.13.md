# Plan 1.13: the standard library

## Done

- **A task talks through a `Channel`**: `run(channel: Channel): void throws ProcessError`; tasks have
  their own messages over shared memory, not `std.os.rpc`.
- **What a receive brings is a `Received`**: `Message(value)`, `Nothing` or `Finished`. `receive(ms)`
  waits *up to* `ms` and comes back as soon as something comes; there is no negative time and no
  `finished()`. `Process.onMessage(handler)` gives each message to `handler` while `join()` waits, for a
  program that only waits. `kill()` stays on the `Process`: it knows whether its child still runs, and a
  pid can be given to another program once it ends.
- **A `type` with fields is a struct or a union of C**, by value (spec §D.0): only the fields used, a
  union written as a struct, no `struct` member in an interface, and a `T[]` of them to C as an array.
  What was planned as "by pointer, with what C changes coming back" is what `T*` and `&x` already do
  (§D.6), written where it happens; and by value is simply a parameter of the type, so nothing is left
  open there. Tested in `tests/cases/c/interface_types.lar` (a list to C, `&x` filled by C, a struct
  returned, a union by value, `struct tm` through `mktime`).

- **`UnsafeTask` and `LibraryLoader`** (spec §19.2, §D.0): the interfaces of its class are opened,
  their functions found in the library that `loader.bind(Name, "library")` opens, through pointers of
  the header's own type (`__typeof__`), with no libffi. The compiler writes `setupTask`, as it writes
  `encodeTask`, so that `setup` runs once in each process. Tested in `tests/std/unsafe_task_test.lar`.
  Unlike what was planned, `unsafe_c = true` stays: it is C in the program's own process, for one header;
  an `UnsafeTask` is the safe way, and needs no `unsafe_c`.

- **Callbacks: a function and its "this"** (spec §D.10): a parameter of a function type in a native
  interface, `void*` as a type, and the three pairs: `self::onRow` with `self`, `row` with `row`, a
  function without state (a lambda that captures nothing, `::compare`) with `null`. One trampoline per
  pair (`codegen.expressions.callbacks`), which converts `char*` to `String` and `char**` with the
  count before it to `String[]` or `String?[]`; the pair is checked when both are in the same call
  (`semantics.expressions.callbacks`). Done again from scratch, not from `4292b16`: what that commit had
  (a `Context` parameter the compiler filled in) is not what was planned (the signature is what is
  written). Tested in `tests/c/callbacks_test.lar`, `tests/cases/c/native_callbacks.lar` and, in an
  `UnsafeTask`, `qsort` with a lambda (`tests/std/unsafe_task_test.lar`).

## To do

### C only in processes apart: `UnsafeTask` (done)

See the Done list and spec §19.2. What is left of it is below: callbacks.

### The types of a header: `type` (done)

Everything of C in an interface is a `type`, opaque (`type X;`), with an owner (`type X released by
f;`) or with fields (`type X { let ...; }`). The whole of it, with its table, is in spec §D.0; how it
looks for SDL:

```ts
native interface Sdl "<SDL2/SDL.h>" {
    type SDL_Window released by SDL_DestroyWindow;
    type SDL_Surface;
    type SDL_Rect { let x: int32; let y: int32; let w: int32; let h: int32; }
    type SDL_Keysym { let sym: int32; let mod: uint16; }
    type SDL_KeyboardEvent { let keysym: SDL_Keysym; }
    type SDL_Event { let type: uint32; let key: SDL_KeyboardEvent; }   // a union in C

    function SDL_FillRect(s: SDL_Surface, r: SDL_Rect*, color: uint32): int32;
    function SDL_PollEvent(event: SDL_Event*): int32;
    function SDL_RenderFillRects(r: SDL_Renderer, rects: SDL_Rect[]): int32;   // the pointer and the count
}

let e: SDL_Event = {};
while (Sdl.SDL_PollEvent(&e) != 0) {
    if (e.type == SDL_KEYDOWN) { println("${e.key.keysym.sym}"); }
}
```

DL_KEYDOWN) { println("${e.key.keysym.sym}"); }
   }
   ```
5. **A list of them is laid out as C lays out an array**, one after another, and goes as a pointer to
   the first: `Sdl.SDL_RenderFillRects(renderer, rects, rects.length)`.
6. **A pointer inside a struct** (a `char*`, a pointer to another struct) is declared as an opaque
   `type`, or as a `String`, copied when it is read.

Open: the few C functions that take a struct **by value**, not by pointer (`SDL_Color` in some of them).
They need a mark; to add no keyword, it can be C text (`c"..."`), only there.

### Callbacks: the "this" of C (done)

See the Done list and spec §D.10. What is left of it:

- **A callback with no `void*`** (`qsort`'s `compare`) takes only a function without state. Later: a
  fixed number of C functions for each signature (16), each reading its own place, so that a method or
  a lambda with captures can go there too.
- **A "this" that comes back inside a struct**, not as a parameter (llhttp's callbacks get the
  `llhttp_t*`, whose field `data` holds it): a way to say "it is that field". With it, **lambdas as
  fields of a `type`** (`settings.on_url = ...`), which take the same conversion as a parameter.
- **A call from a thread of the library** is not detected (Larimar does not know which memory that
  thread is in): it should be a panic. Later: the call goes to a queue of the task's thread (audio,
  GStreamer, libuv).
- **Text a library makes and the caller frees** (`sqlite3_exec`'s `errmsg`, freed with `sqlite3_free`):
  a way to say it in the interface, as `released by` says it for types.
- **The C type of the trampoline** is the one written in the interface (`String` is `const char*`, a
  `String[]` is `char**`), passed as `void*`: a header that says `char*` where Larimar writes
  `const char*` is the same function in practice, but clang's `-fsanitize=function` can see the
  difference.

### C only in an `UnsafeTask` (step 1 done)

The C of a program, or of a library written in Larimar, runs in a process apart: Larimar takes the idea
of regions to failures. A value lives in a region and cannot escape it; C the compiler does not check
lives in the process of a task, and a crash there does not cross into the program (it is a
`ProcessError`). The cost is smaller than it looks: the Larimar that uses the library runs inside the
task too, at the speed of C (a loop that draws, a `qsort` with its callback); only messages cross. When
a case of speed truly needs C in the program's process, the answer is std, which is C reviewed and
tested, as libc already is.

1. **Done: `[project] unsafe_c` is gone.** A native interface outside a class that implements
   `UnsafeTask` is an error that says where it goes; `unsafe_c` in `larimar.toml` too.
2. **Native interfaces at module level, used only "inside the task".** Declared in a module, so two tasks
   or a library (`sdlkit`: the interface, a `Window` class, helpers) share them. A function or method that
   calls `Sdl.*` is of the task, and so is everything that calls it, upwards; reaching it from outside an
   `UnsafeTask` (from `main`, from a thread of the program) is a compile error that shows the path:
   `main → draw → Sdl.SDL_FillRect: Sdl's C runs only in an UnsafeTask`. It is the analysis the compiler
   already does for threads (owners and edges), with another question. Constants and structs by value of
   the interface (`SDL_KEYDOWN`, `SDL_Rect`) are data and go anywhere; a type `released by` is of the task
   (releasing it calls C).
3. **`from`: the library of an interface** (below). With it the task opens, when its process starts, the
   libraries of every interface its code reaches.

**`setup` becomes optional, by composition.** An interface has no methods with a default body, so:

```ts
public interface UnsafeTask extends Task { }                         // the mark: this task brings C
public interface PreparedUnsafeTask extends UnsafeTask {             // and it prepares itself in each process
    function setup(loader: LibraryLoader): void throws LoadError;
}
```

`UnsafeTask` keeps no method of its own: it is the mark that the task brings C (for the compiler, what
opens its interfaces; for whoever reads, it is in the type). `PreparedUnsafeTask` has `setup(loader)`,
implemented only to choose the library when the task runs (`loader.bind(Sdl, path)`) or to prepare it
once in each process (`SDL_Init`, a connection). Because it extends `UnsafeTask`, nothing implements it
without being a task with C, and a class names only one: `class Game implements PreparedUnsafeTask`.
(A type declared inside another, `UnsafeTask.Setup`, would say it too, but Larimar has no nested types;
`extends` is enough.) Until `from` exists, `setup` is the only way to load a library, so this comes with it.

### The library of an interface: `from` (next)

The interface says the header and the library, all the C it uses, as `released by` says who frees a type:

```ts
native interface Sdl "<SDL2/SDL.h>" from "SDL2" { ... }
```

- **A name** (`"SDL2"`): the dynamic library, found where the system keeps them, and on macOS also in
  `/opt/homebrew/lib` and `/usr/local/lib` (where brew installs, on ARM and on Intel): the search
  `std.os.library.fileNames` already does. The task opens it when its process starts.
- **A path** (it has `/`, or ends in `.a`, `.so`, `.dylib`, `.dll`, `.lib`): a library that comes with the
  project, relative to its folder. A dynamic one is opened from next to the program. A **static** one
  (`.a`, `.lib`) cannot be opened when the task runs, but a task runs in a copy of the program: the
  compiler can link it into the executable and the task finds its functions in the program itself
  (`dlopen(NULL)`, `GetModuleHandle(NULL)`). To try; until then a static library is made shared.
- **What belongs to a machine goes in `larimar.toml`**, never an absolute path in the code: folders to
  look in, per system, next to those of the headers:

  ```toml
  [c.macos]
  libraries = ["/opt/local/lib"]        # besides the usual ones
  headers = ["/opt/local/include"]
  ```
- **`loader.bind` stays** (in `PreparedUnsafeTask`) for what is decided when the task runs: plugins, a path
  from the configuration.
- Later: `from pkg "sdl2"`, which asks `pkg-config` for paths and flags (GTK, GStreamer: libraries with
  many of their own).
- **Where the `.h` comes from**: a library (`.dll`, `.so`, `.dylib`) has its compiled code and the names
  of its functions, not their types nor the layout of its structs; the header says them, and comes with
  the library's development package (brew: both; Linux: `libsdl2-dev` beside `libsdl2`; Windows: a zip
  with `include/`, `lib/` and the `.dll`). The string of a native interface is written as an `#include`
  in the C Larimar makes, so the C compiler checks types, fields and macros; the task needs the header to
  compile and the library to run.

### After that

- **Messages with a type**: a struct whose fields cross (the rule of the fields of a `Task`) goes
  through a channel as it is, and is made again on the other side (`value as Progress`).
- **Interfaces written from the headers**, as `jextract` does for Java: a tool that reads a `.h` and
  writes its `native interface` with its `type`s.
- **Quick fixes in `larimar lsp`**: where a message says what to write (`.clone()`, `in self`), the
  editor offers to write it; nothing is done without the developer seeing it.
- **Annotations written in Larimar** (code that runs when compiling and writes declarations, as Rust's
  macros or Java's annotation processors): for what is written by hand today (to and from JSON, typed
  messages). They would need a public syntax tree and a way to see what they wrote (`larimar expand`).
  Not before the syntax is still.
- **`EventLoop`**: callbacks instead of times, for many channels, timers and later a window, on top of
  `receive(ms)`, which stays.
