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

### Callbacks: the "this" of C (Thursday, in a new conversation)

C has no methods: a library that calls back asks for **a function and its "this"**, a `void*` (`ctx`,
`user_data`, `arg`). Larimar passes the same pair, written where it goes: what is passed as the `void*`
is the "this" of what is passed as the function. There is no special type: `void*` is `void*`.

```ts
native interface Sqlite "<sqlite3.h>" {
    type sqlite3 released by sqlite3_close;
    function sqlite3_exec(db: sqlite3, sql: String,
                          row: (void*, int32, String[], String[]) -> int32,
                          data: void*, error: String?*): int32;
}

function onRow(data: void*, count: int32, values: String[], columns: String[]): int32 { ... }

Sqlite.sqlite3_exec(db!, "select name from users", self::onRow, self, null);   // a method and its object
```

**The three forms**, and the rule that joins them: the signature is what is written, at the call and
in the callback (no parameter the compiler fills in by itself).

| Passed as the function | Passed as the `void*` | Its "this" |
|---|---|---|
| `self::onRow`, a method reference | `self` | the object |
| `row`, a lambda | `row`, the same one | its captures |
| `Calc.compare`, a function without state | `null` | none |

```ts
let names: String[*] = [];
let row: (void*, int32, String[], String[]) -> int32 = (data, count, values, columns) -> {
    names.push(values[0].clone());
    return 0;
};
Sqlite.sqlite3_exec(db!, sql, row, row, null);
```

- **The compiler checks the pair** when both are in the same call (`self::onRow` with `self`, `row` with
  `row`); in two calls (libcurl: `CURLOPT_WRITEFUNCTION` and `CURLOPT_WRITEDATA`) it cannot, and a wrong
  pair is a crash, in the task's process.

**Where the "this" comes back**: each library puts it in another place (SQLite first, libcurl and GTK
last, pthreads alone), and the compiler finds it without guessing:

- **The callback has one `void*`**: it comes back there. The method may write it as `void*` or as its
  own class.
- **It has more than one** (an allocator's `free(void* ctx, void* ptr)`): the method says which, writing
  it with the type of its class (`function free(ctx: Arena, ptr: void*)`); if it does not, a compile
  error says so.
- **It has none** (`qsort`'s `compare(const void* a, const void* b)`): a method reference or a lambda
  with captures cannot go there; a function without state can. Later: a fixed number of C functions for
  each signature (16), each reading its own place.
- **Open**: a "this" that comes back inside a struct, not as a parameter (llhttp's callbacks get the
  `llhttp_t*`, whose field `data` holds it). It needs a way to say "it is that field".

**The C the compiler writes**: one trampoline for each pair of a C signature and a method (or a lambda's
type), which turns the `void*` back into the object or the lambda and calls it, converting the
arguments (`char*` to `String`, `char**` with its count to `String[]`). The same as C++ and Rust
programmers write by hand (`static_cast<Users*>(self)->onRow(...)`), but checked.

**What it lives**: as long as what it is. A method reference lives as long as its object, a lambda as
long as its block: enough for the callbacks called during the call (`sqlite3_exec`, `qsort`, llhttp).
For a callback the library keeps, the object lives longer (a field of something that lasts, or `in
heap`); `registerCallback` is not needed unless that turns out short.

**Three more rules**

- A callback does not throw: the stack of C cannot be unwound. A method or lambda given to C has no
  `throws`; when something goes wrong, it panics, and the task fails.
- A call from a thread of the library is a panic (Larimar does not know which memory that thread is
  in). Later: the call goes to a queue of the task's thread (audio, GStreamer, libuv).
- Lambdas as fields of a `type` (llhttp's `settings.on_url = ...`) take the same conversion as a
  parameter: the field gets the trampoline.

**Also open**: text a library makes and the caller frees (`sqlite3_exec`'s `errmsg`, freed with
`sqlite3_free`): a way to say it in the interface, as `released by` says it for types.

**How to do it cheaply**: the trampolines and the context of the lambda were already written once, as
callbacks with a `Context`, in commit `4292b16` (`contextArgs` in the codegen of calls, `ctxParam` and
`ctxKeep` in the analysis, tests `tests/c/callbacks_test.lar` and `tests/cases/c/native_callbacks_with_context.lar`),
and removed in `a532535` (1.10.0) with the `native function`s they were for. Bring them back and adapt
them: the runtime's names (`rt_` to `lar_`, `Lar`), the folders (`src/compiler/...`), native
interfaces (also opened ones, in an `UnsafeTask`), method references and `self`, and `void*` in place
of `Context`. Run only `tests/c` and the tests of tasks.

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
