# Plan 1.13: the standard library

## Done

- **A task talks through a `Channel`**: `run(channel: Channel): void throws ProcessError`; tasks have
  their own messages over shared memory, not `std.os.rpc`.
- **What a receive brings is a `Received`**: `Message(value)`, `Nothing` or `Finished`. `receive(ms)`
  waits *up to* `ms` and comes back as soon as something comes; there is no negative time and no
  `finished()`. `Process.onMessage(handler)` gives each message to `handler` while `join()` waits, for a
  program that only waits. `kill()` stays on the `Process`: it knows whether its child still runs, and a
  pid can be given to another program once it ends.

## To do

### C only in processes apart: `UnsafeTask`

The C of a library is used only from a task, in a copy of the program: when it fails, the task fails,
not the program. The process is the region of that C: what the library took and did not free goes when
the process ends.

```ts
class Thumbnail implements UnsafeTask {
    let file: String;
    let width: int32;

    native interface Vips "<vips/vips.h>" {
        type VipsImage released by g_object_unref;
        function vips_init(name: String): int32;
        function vips_thumbnail(input: String, out: VipsImage, width: int32): int32;
        function vips_set_log(f: (String) -> void): void;
    }

    override function setup(loader: LibraryLoader): void throws LoadError {
        loader.bind(Vips, "vips");                      // libvips.so, libvips.dylib or vips.dll
        let log: Callback = loader.registerCallback((text) -> { eprintln(text); });
        Vips.vips_set_log(log);
    }

    override function run(channel: Channel): void throws ProcessError {
        ...
        channel.send({ done: true });
    }
}
```

- `interface UnsafeTask extends Task` has one more method, `setup(loader: LibraryLoader): void throws
  LoadError`. It is called once in each process, before its first task: a `ProcessPool` keeps the
  library loaded for the next tasks.
- `LibraryLoader.bind(Interface, name)` opens the library (`dlopen`, `LoadLibrary`) and looks up each
  function of the interface (`dlsym`, `GetProcAddress`), keeping a pointer of its exact C type: the
  calls are typed C, with no libffi. The name is written once, without `lib` or the extension, and is
  made the name of each system. A missing library or function is a `LoadError` that names it, before
  `run()`.
- **The rule** (`rules.lar`): a `native interface` outside std is declared only in a class that
  implements `UnsafeTask`.
- C pointers never leave the process: what crosses is what crosses through a channel.

### The types of a header: `type`

Inside a `native interface` everything from C is a **`type`**. There is no `struct` and no `union`
there: the C that Larimar writes includes the header itself, so the C compiler knows the true layout of
every struct and union. Larimar only needs to know which fields the program uses, and of what type.

```ts
native interface Sdl "<SDL2/SDL.h>" {
    type SDL_Window released by SDL_DestroyWindow;      // opaque, with an owner
    type SDL_Surface;                                   // opaque, without an owner
    type SDL_Rect { x: int32; y: int32; w: int32; h: int32; }
    type SDL_Keysym { sym: int32; mod: uint16; }
    type SDL_KeyboardEvent { keysym: SDL_Keysym; }
    type SDL_Event { type: uint32; key: SDL_KeyboardEvent; }    // a union in C: it does not matter

    function SDL_FillRect(s: SDL_Surface, r: SDL_Rect, color: uint32): int32;
    function SDL_PollEvent(event: SDL_Event): int32;
    function SDL_RenderFillRects(r: SDL_Renderer, rects: SDL_Rect[], count: int32): int32;
}
```

The three forms:

| Form | What it is | What a program does with it |
|---|---|---|
| `type X;` | opaque: a pointer the library gives and takes | passes it from one function to another |
| `type X released by f;` | opaque, with an owner | the same; `f` frees it when its memory goes |
| `type X { fields }` | a struct or a union of C, whose fields it uses | makes it with a literal, reads and writes its fields |

The rules of `type X { fields }`:

1. **Only the fields used.** A `type` lists the fields the program reads or writes, not all of them:
   `SDL_Event` has dozens, the interface names two. Their order does not matter, because C finds each
   one by its name.
2. **A struct and a union are written the same.** `e.key.keysym.sym` is written to C as it is, and the C
   compiler knows that `key` is a member of a union. Reading a member that is not the one C wrote gives
   numbers without meaning, not a crash: they are plain data, and the task's process holds the worst
   case.
3. **A wrong field is a compile error of C**: a field that does not exist, or has another type, stops
   the build; it never runs.
4. **It goes by pointer, and what C changes comes back.** A parameter of such a type is passed as a
   pointer to a copy, and after the call the copy goes back to the program's variable. One rule covers a
   `const SDL_Rect*` that C only reads and an `SDL_Event*` that C fills:
   ```ts
   let e: Sdl.SDL_Event = {};
   while (Sdl.SDL_PollEvent(e) != 0) {
       if (e.type == SDL_KEYDOWN) { println("${e.key.keysym.sym}"); }
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
