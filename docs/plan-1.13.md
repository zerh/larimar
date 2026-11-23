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
