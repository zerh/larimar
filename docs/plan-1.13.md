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

### Callbacks: `Callback`, `registerCallback`, `CallbackData`

A library keeps a pointer to a function and calls it later, after the call that gave it has returned. A
lambda is code and what it captures, and what it captures lives in some memory: if that memory goes and
the library calls, the pointer points to nothing.

**A callback lives as long as the memory where it is made**:

- **A lambda given straight to a function** lives as long as its block. It is enough for the callbacks
  that are called during the call itself (`qsort`, `sqlite3_exec`) or until the end of `run()`.
- **`loader.registerCallback(lambda)`**, in `setup()`, is for a callback the library keeps: it lives as
  long as the process, because the loader does. It gives a `Callback`.
- **When the library calls a callback whose memory is gone**, there is no garbage: its C function sees
  that it is dead and panics with a clear message. The task's process ends, and the program gets a
  `ProcessError`.

```ts
/** A callback that the library keeps: it lives as long as the process. */
public class Callback {
    /** Whether the library may still call it (false after release). */
    function alive(): bool;
    /** When the library says it dropped it: from then on a call is a panic, and its place is free. */
    function release(): void;
}
```

A `Callback` remembers the signature of its lambda, as a `T[*]` remembers its `T`: giving a `Callback`
of `(String) -> void` where the library takes `(int32) -> int32` is a compile error.

How the compiler writes it:

- **With a `void* user_data`** (GTK, sqlite, libcurl): one C function for each signature, which takes
  the `user_data` as the callback and calls its lambda. In the interface, the parameter that carries it
  is a **`CallbackData`**:
  ```ts
  function g_signal_connect(o: Widget, name: String, f: (Widget, CallbackData) -> void, data: CallbackData): int64;
  ```
- **Without one** (`qsort`, signals, older libraries): a fixed number of C functions for each signature
  (16), each of which reads its own place; when they run out, a `LoadError` says so.

In C:

```c
typedef struct LarCallback {
    LarLambda lambda;     /* its code and captures, copied to the loader's memory */
    int32_t slot;         /* -1 with user_data; otherwise its place */
    bool alive;
    LarThread thread;     /* the only thread that may call it */
} LarCallback;
```

Three more rules:

- **A callback does not throw**: the stack of C cannot be unwound. A lambda given to C has no `throws`;
  when something goes wrong, it panics.
- **A call from a thread of the library is a panic**: Larimar does not know which memory that thread is
  in. Later, not now: the call can go to a queue of the task's thread (audio, GStreamer and libuv call
  from threads of their own).
- **A callback of `setup()` does not capture the channel**: the channel is of each task, and it does not
  exist in `setup()` yet. A callback that tells the program something is given in `run()`, and the
  library drops it when `run()` ends.

### After that

- **Messages with a type**: a struct whose fields cross (the rule of the fields of a `Task`) goes
  through a channel as it is, and is made again on the other side (`value as Progress`).
- **Interfaces written from the headers**, as `jextract` does for Java: a tool that reads a `.h` and
  writes its `native interface` with its `type`s.
- **`EventLoop`**: callbacks instead of times, for many channels, timers and later a window, on top of
  `receive(ms)`, which stays.
