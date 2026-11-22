# C in the standard library

Larimar becomes C, and the standard library talks to the operating system through it: files, sockets,
threads, TLS, the clock. That C is written in std, with the declarations of this chapter.

**A program and a library written in Larimar have no C of their own.** `cinclude`, `ccode`, the
`native` declarations and the functions with a body of C are only for the standard library; anywhere else
they are an error (a project with `[project] unsafe_c = true` may declare
[native interfaces](#what-a-header-gives-native-interface), and nothing else, and every build says so):

```
Module Error [src/main.lar:1]: ccode is only for the standard library: C is written there, and a program uses what std gives.
```

So all the C a program runs is part of Larimar, written and tested with it, and a library someone else
wrote cannot bring C that the compiler does not check. For what std does not have, a program uses another
process instead of loading its C: another program, a call of `std.os.rpc`, a stream of `std.os.sharedmemory`
([chapter 23 of the manual](manual.md#23-other-programs-calls-shared-memory-and-processes)). If that
process fails, it does not corrupt the memory of yours.

This document is for whoever writes or reads the standard library; the [manual](manual.md) of the
language does not have it, because a program cannot use any of it. `larimarc --unsafe-c` lets a file
outside std use these declarations: the compiler is built with it (its editor tools still have C of their
own) and so are its tests of std's C. A program built with it has none of the language's guarantees.
The rules, exactly, are in [Appendix D of the specification](spec.md#appendix-d-the-c-of-the-standard-library).

**`native` always means C.** What the compiler writes itself (the core of `String` and `Any`,
`Thread.start`) has no body in `std.lang` and no `native`: `type String { let length: int32; ... }`.

## What a header gives: `native interface`

Since Larimar becomes C, calling a C function costs nothing. **std talks to C's library (libc) and to the
system through native interfaces**: what a header gives, under one name.

```ts
native interface Stdio "<stdio.h>" {
    type FILE released by fclose;                 // C's FILE*: the memory it is in calls fclose
    const stdout: FILE;
    function fputs(text: String, f: FILE): int32;
    function fclose(f: FILE): int32;
}

native interface LibM "<math.h>" {
    function sqrt(x: float64): float64;
    function fabs(x: float64): float64;
}

function main(): int32 {
    Stdio.fputs("square root of 2 = ${LibM.sqrt(2.0)}\n", Stdio.stdout);
    return 0;
}
```

- **`Name.f(...)` calls the C function `f`**, and `Name.N` reads a constant or a variable. The members
  are declared as below (`function`, `type`, `const`, `let`), without `native` in front: the interface
  already is.
- **A `type` keeps its name** in the module (`FILE`); without `=` it is a pointer to the C type of its
  name (`FILE*`). `released by` names a function of the same interface.
- **A `type` with fields is a struct or a union of C, by value**, and lists only the fields used:
  `type Stat = struct stat { let st_mode: uint32; let st_size: int64; }`. The header gives the layout,
  so a struct and a union are written the same, and a wrong field stops the C compiler. It goes by value,
  by pointer with `&x` (C's changes stay in `x`), and in a `T[]` as a C array. The three forms, opaque,
  with an owner and with fields, are in [§D.0 of the spec](spec.md#d0-native-interfaces).
- **Several headers** go in one interface: `native interface LibC "<stdio.h>", "<errno.h>" { ... }`; one
  can extend others: `native interface Posix "<unistd.h>" extends LibC { ... }` has their members too.
- **The header reaches the C only when something of it is used**: an interface of fifty functions costs
  nothing for the ones a program does not call.
- **Inside a class for one system** ([below](#c-for-each-system-classes-with-c-in-their-methods)) the
  interface is the class's: its C is only for that system.
- This is how `std.math`, `std.os`, `std.io.console` and `std.io.files` reach libc. Outside std, a project
  with `[project] unsafe_c = true` may declare them too ([chapter 27 of the manual](manual.md#c-of-its-own-unsafe_c--true)).

The rest of this document is the older, finer tool: one declaration at a time, with `cinclude`.

```ts
cinclude "<stdio.h>";
cinclude "<math.h>";

native function printf(format: String, ...): int32;
native function sqrt(x: float64): float64;

function main(): int32 {
    printf("square root of 2 = %f\n", sqrt(2.0));
    return 0;
}
```

Output: `square root of 2 = 1.414214`

`cinclude` brings in the C file that declares those functions (a **header**), and `native function`
says to Larimar how each one is called. What the C of std needs linked (the math library, threads,
OpenSSL) the compiler finds in the C it generates, and links.

Everything that comes from C is declared with **`native`**, and every declaration follows the same rule:
**the Larimar name goes on the left; after `=`, the C name**. Without `=`, the name is the same.

| Declaration | What it is |
|---|---|
| `native function f(...): T;` | a C function, in the standard library ([below](#c-in-the-standard-library)) |
| `native type X;`, `native type X = FILE*;` | a C type ([C types](#c-types-native-type)) |
| `native type X = T* { ... }` | a C type with fields and methods ([C types with members](#c-types-with-members)) |
| `native struct P { ... }` | a C struct, by value ([C structs](#c-structs-native-struct)) |
| `native const N: int32;`, `native let errno: int32;` | a C constant, macro or variable ([Constants and variables](#c-constants-and-variables-native-const-native-let)) |

A library of your own is declared the same way. For example, for one of windows:

```ts
cinclude "windows_lib.h";

native type Window;                                      // an opaque C pointer
native function create_window(title: String): Window;
native function close_window(w: Window): void;
```

- `cinclude` adds an `#include` to the generated C (inside a class for a platform, only on that
  system: see [C for each system](#c-for-each-system-classes-with-c-in-their-methods)).
- The parameters of a `native function` can only be numbers, `bool`, `String` (it arrives as
  `const char*`), `String?` (`null` arrives as `NULL`), `native` types (optional ones too, `T?`, which in C
  are a pointer that can be `NULL`), C structs and C pointers (`T*`, see [C pointers](#c-pointers-t-and-)).
  `...` allows variable arguments, as in `printf`.
- A C function can return `String?`: `NULL` arrives as `null` (`getenv`).
- **When the C name is another one**, it goes after `=`: `native function cExit(code: int32): void = exit;`.
  When it is not a plain name (a cast, a macro in parentheses), it goes as **C text, `c"..."`**, exactly as
  in C: `= c"(fio_start)"`, `= c"(const char*)sqlite3_column_text"`. The `c` in front says it is C, not a
  Larimar `String`.
- A **`T[]` of numbers or `bool`** (`byte[]`, `int32[]`, `float64[]`...) arrives in C as **two
  arguments**: a pointer to the elements and how many there are. C can read them and write to them, so
  it is the way for C to fill a Larimar buffer (reading from a file or a socket) without copying anything:

  ```ts
  ccode {
      static int32_t fill(uint8_t* items, int32_t length) { /* writes to items[0..length) */ return length; }
  }
  native function fill(buffer: byte[]): int32;      // in C: fill(uint8_t* items, int32_t length)

  let buf: byte[*] = buffer(4096);
  let n: int32 = fill(buf);                          // a list, a T[N] or a T[] work
  ```
- If the module has no `cinclude` and no `ccode` (neither it nor the modules of its folder: `net/posix.lar`
  for `net.lar`), the transpiler writes the C prototype of each
  `native function` itself. If the function comes from a header, include the header.
- A C function that returns `String` must return a zero-terminated text that keeps existing: a static
  one, or one created in a memory it receives (see below).
- A `native function` is C: either it names a C function (`= c_name;`), or its body is C
  (`native function twice(x: int32): int32 { return 2 * x; }`), which the compiler writes as a C function.
  To write one in Larimar, write a plain function.
- In a module, the C name does not change: `public native function Beep(...)` in the module `win` is
  used as `win.Beep(...)` and calls C's `Beep`.

**A macro with named arguments.** Some libraries imitate named arguments with a macro that builds a
struct (`fio_start(.threads = 1, .workers = 2)` in facil.io). The macro hides a real function with the
same name, which takes the struct; in parentheses, C calls the function and not the macro:

```ts
ccode {
    #include <stdio.h>
    struct sum_args { int a; int b; };
    static int sum(struct sum_args s) { return s.a + s.b; }
    #define sum(...) sum((struct sum_args){__VA_ARGS__})     /* sum(.a = 1, .b = 2) in C */
}

native struct SumArgs = struct sum_args { let a: int32; let b: int32; }
native function sum(args: SumArgs): int32 = c"(sum)";       // the function, not the macro

function main(): int32 {
    println("${sum({ a: 3, b: 4 })}");                      // the fields not given are zero
    return 0;
}
```

Output: `7`

## C in the same file: `ccode`

Almost everything from C is used directly, with declarations: functions, types, structs, constants,
variables, pointers and resources (next sections). For what is still better written in C (an algorithm,
an Apple block, code between `fork` and `exec`), you write it in C inside the file itself and declare it
with `native function`:

```ts
ccode {
    #include <ctype.h>

    static int32_t sum_digits(int64_t v) {
        int32_t s = 0;
        if (v < 0) v = -v;
        while (v > 0) { s += (int32_t)(v % 10); v /= 10; }
        return s;
    }
}

native function sum_digits(v: int64): int32;

function main(): int32 {
    println("${sum_digits(98765)}");
    return 0;
}
```

Output: `35`

Inside a `ccode`, **`lar"name"`** is the C name of a Larimar function, type or global variable
(`lar"module.name"` for one of another module). That way the C does not depend on how the compiler
names things:

```ts
ccode {
    static int32_t both(int32_t a) { return lar"twice"(a) + lar"area"(a, 3); }
}

function twice(x: int32): int32 { return x * 2; }
function area(w: int32, h: int32): int32 { return w * h; }
native function both(a: int32): int32;

function main(): int32 {
    println("${both(5)}");
    return 0;
}
```

Output: `25`

- A name that does not exist is a compile error: *lar"nope" in ccode: 'nope' is not a function, type or
  global of Larimar seen here*.
- The prototypes of the functions named this way are written before the `ccode` when their types are
  numbers, `bool`, `String` or `void`. A function that returns data also receives the memory of the call
  (as [chapter 28 of the manual](manual.md#28-what-the-transpiler-generates) shows).

In `std.lang`, `type` declares the methods of the types the compiler knows: what has no body the
compiler writes, and the rest is Larimar (which may call C):

```ts
public type String {
    let length: int32;
    operator [](i: int32): byte;
    function substring(from: int32, to: int32): String in self;
    function isEmpty(): bool { return self.length == 0; }
}
```

A native function of a class delegates to a Larimar expression, which can call a C function:

```ts
public class StringBuilder {
    let buffer: TextBuf = text_buf_new();
    native function add(text: String): void = text_buf_add(self.buffer, text);
    native function toString(): String in self = text_buf_view(self.buffer);
}
```

Of the `ccode` blocks of the standard library only what is used reaches the C: each C function, type
or variable stays if something the program uses names it. The `ccode` of the program itself, instead,
is copied whole.

That is how `String` is written: the compiler only knows its core (`length`, `[]`, `substring`, `bytes`,
`split` and `lines`, which are views of the text), and everything else (`indexOf`, `replace`,
`toUpperCase`, `padStart`, `toInt`, `codePoints`...) is written in Larimar in `src/std/lang.lar`, with a
small `ccode` only for what needs C (`strtod`, for `toFloat`).

- The content is copied as it is into the generated C, after the headers and before the program.
- **The doors between the two languages are `native` (from C to Larimar) and `lar"..."` (inside a
  `ccode`, from C to Larimar's functions)**, with their types checked. The C must not use the
  variables and types that Larimar generates in any other way, because their names may change.
- Inside `ccode` there are no guarantees: the C can do anything. It is better to keep it small and simple.

## C for each system: classes with C in their methods

What changes between systems is written as **a class for each system**, whose static functions are
**native functions with a body of C** (`static native function f(): T { C }`). Each class says the
platform it is for by implementing it (`UnixPlatform`, `WindowsPlatform`...), and which one runs is
chosen with a `switch` on `Platform.current()`. It is how the standard library does it (`std.time`,
`std.os`, `std.net`...): its modules are only `.lar` files, and no `#if` is written by hand.

```ts
// src/std/time/posix.lar
import std.platform { UnixPlatform };

public class PosixClock implements UnixPlatform {
    cinclude "<time.h>";

    ccode {                                   // C its functions share
        static int64_t ms_of(clockid_t which) {
            struct timespec t;
            clock_gettime(which, &t);
            return (int64_t)t.tv_sec * 1000 + t.tv_nsec / 1000000;
        }
    }

    static native function monotonic(): int64 { return ms_of(CLOCK_MONOTONIC); }

    static native function sleep(ms: int64): void {
        struct timespec t = { (time_t)(ms / 1000), (long)(ms % 1000) * 1000000L };
        nanosleep(&t, NULL);
    }
}

// src/std/time/windows.lar: the same, with GetTickCount64 and Sleep, implements WindowsPlatform

// src/std/time.lar
import std.platform { Platform, OS };
import std.time.posix { PosixClock };
import std.time.windows { WindowsClock };

public function monotonic(): int64 {
    return switch (Platform.current()) {
        case Linux, MacOS, Unix -> PosixClock.monotonic();
        case Windows -> WindowsClock.monotonic();
    };
}
```

- **A body of C** sees the parameters by their names, with their C types: an `int64` is an `int64_t`, a
  `String` a `const char*` (to read), a `byte[]` is `items` and `items_length`, a native type its C
  type. It returns what the signature says (a `String` is copied by Larimar). What is outside the method
  (another function, a global of Larimar) is named with `lar"name"`. `self` is not there: what the C needs
  goes as parameters. A function outside a class can have a C body too.
- **`cinclude` and `ccode` inside a class** are its headers and the C its methods share.
- **The platforms** are interfaces of `std.platform` (a module that imports nothing), one inside the other:

  ```ts
  public interface Platform {}
  public interface UnixPlatform extends Platform {}       // Linux, macOS and the other Unix
  public interface LinuxPlatform extends UnixPlatform {}
  public interface MacOSPlatform extends UnixPlatform {}
  public interface WindowsPlatform extends Platform {}
  ```

  A class for a platform puts all its C (headers, `ccode`, bodies) into the C inside the `#if` of that
  system, which the compiler writes. The same C file builds everywhere, and a build for Linux never sees
  `<windows.h>`. Called on another system, a function of that class with a C body panics:
  *'WindowsClock.sleep' is for windows, not for this system*. A class can be for a narrower platform:
  `class MacOSSystem implements MacOSPlatform` has only what changes on macOS, and `std.os` calls it there.
- **`Platform.current()`** (a static function of the interface `Platform`) gives `OS.Linux`, `MacOS`,
  `Windows` or `Unix` (another Unix); `Platform.name()`, the same as text (`"linux"`...). A `switch` on it
  without `default` has to name every system: a system added later shows every place to port. It is a
  constant of the C compiler, so the branch of the other systems disappears from the executable.
- **Where they go:** the module (`time.lar`) keeps its API and chooses; each platform's class goes in a
  module of its folder (`time/posix.lar`, `time/windows.lar`), which the module imports. **A part never
  imports the module that uses it**: std has no cycles of imports (`tests/std/cycles_test.lar` checks
  it). What several parts share goes in a part of its own that they import (`process/common.lar`,
  `net/internal.lar`: the `Socket` type).
- **The parts are std's own**: a module whose path has `posix`, `windows`, `macos`, `common` or
  `internal` is imported only from std; a program gets an error that names what to use instead.
- An interface is for a real choice (`TlsProvider`: the system's TLS or OpenSSL), not to reach a
  platform: the static functions of each class are enough for that.

Which to use, from less C to more:

1. **A native interface**, when a header already has the function, type or constant: almost always.
2. **`ccode { ... }`**, a few lines that C writes better: a cast, a macro, a loop on `EINTR`.
3. **`native function f(...): T { C }`**, a function whose body is C: when the C is only for it.
4. **A class for each platform with static native functions**, when the systems do it differently.

## The C of one platform only: `--target`

By default the generated C is **one file for every system**: each platform's classes go inside the `#if`
the compiler writes, and the C compiler of each system takes its own. It is what lets the same C be
built anywhere (Larimar's own bootstrap is that).

With **`--target linux`** (or `macos`, `windows`, `unix`) the choice is made by Larimar, when it
generates:

```sh
larimar main.lar -o main.c --target windows      # the C of Windows, from any system
larimar build --target linux
```

- `switch (Platform.current())` becomes its arm: the other platforms' classes are not even created.
- The C of the target's classes is written plain, with no `#if`; that of the other platforms is not
  written at all.
- Everything is still checked: a class for Windows with an error is an error with `--target linux` too.

The result is shorter C, of that system only: to read it, to debug it, or to take it to a machine
where it will be compiled (a program for Windows generated on a Mac). The program does the same either
way.

## Passing a memory to C

A C function can receive a Larimar memory (`m: byte[*]` in the declaration) and create things in it.
When **the memory is its first parameter**, the call does not write it: C receives the memory of the
call, the same one a Larimar function would receive, so what it returns lives where the caller says (its
block, the list it is added to, or the memory written with `in`). It is the right way for C to return
text:

```ts
ccode {
    #include <ctype.h>

    static const char* shout(LarMemory* m, const char* text) {
        size_t n = strlen(text);
        char* out = (char*)lar_memory_alloc(m, n + 2, 0);     /* zeroed memory: the text ends by itself */
        for (size_t i = 0; i < n; i++) out[i] = (char)toupper((unsigned char)text[i]);
        out[n] = '!';
        return out;
    }
}

native function shout(m: byte[*], text: String): String;

function main(): int32 {
    println(shout("hello larimar"));                      // in the temporary memory of the statement
    let memory: byte[*] = [] in heap;
    let kept: String = shout("kept") in memory;           // in a memory of its own
    println(kept);
    return 0;
}
```

Output:
```
HELLO LARIMAR!
KEPT!
```

In C, a memory arrives as `LarMemory*`, and `lar_memory_alloc(m, bytes, 0)` reserves space inside it (with the
bytes zeroed). That is the whole interface the C needs to know. The rule is one: **the C uses the memory
only during the call**. If it kept the pointer for later, the memory could be freed before. A memory in
another parameter (not the first) is passed written, like any argument.

This is the Windows example that used to need a separate `.c` file:

```ts
ccode {
    #include <windows.h>

    static const char* computer_name(LarMemory* m) {
        DWORD size = MAX_COMPUTERNAME_LENGTH + 1;
        char* name = (char*)lar_memory_alloc(m, size, 0);
        return GetComputerNameA(name, &size) ? name : "";
    }
}

native function computer_name(m: byte[*]): String;
```

## C types: `native type`

A type that comes from C is declared with `native type`. After `=` goes its type in C:

| Declaration | What it is | In C |
|---|---|---|
| `native type Handle;` | an opaque pointer: received, kept and passed, without looking inside | `void*` |
| `native type File = FILE*;` | a concrete C type | `FILE*` |
| `native type Tm = struct tm*;` | a C struct known by its tag, by pointer | `struct tm*` |
| `native type Count = c"unsigned long";` | any other C type, as C text `c"..."` | `unsigned long` |

```ts
ccode {
    #include <stdio.h>

    typedef struct Point { float x, y; } Point;

    static Point point_mid(Point a, Point b) {
        Point m = { (a.x + b.x) / 2, (a.y + b.y) / 2 };
        return m;
    }
    static FILE* log_file(void) { return stderr; }
    static void log_line(FILE* f, const char* text) { fprintf(f, "%s\n", text); }
}

native type File = FILE*;                                    // a concrete C type
native struct Point { let x: float32; let y: float32; }      // a C struct, by value

native function point_mid(a: Point, b: Point): Point;
native function log_file(): File;
native function log_line(f: File, text: String): void;

function main(): int32 {
    let a: Point = { x: 0, y: 0 };
    let b: Point = Point { x: 4, y: 2 };
    let m: Point = point_mid(a, b);
    println("(${m.x}, ${m.y})");
    log_line(log_file(), "done");
    return 0;
}
```

Output: `(2.0, 1.0)`, and `done` on the error output.

- **Each `native type` is a distinct type in Larimar**, even when they are the same in C: a `File`
  cannot be passed where a `Handle` is expected.
- **The exact C type** (`= FILE*`) makes the C compiler check the types too: with `void*` it would not
  notice that a `FILE*` is passed where the library expects a `sqlite3*`.

## C types with members

A C library usually turns around a pointer (`sqlite3*`, `SDL_Window*`, `http_s*`) and the functions that
take it first. A `native type` can declare all that between braces, and then it is used like an object:

```ts
ccode {
    typedef struct Counter { int value; const char* name; } Counter;
    static Counter* counter_new(const char* name) { Counter* c = (Counter*)calloc(1, sizeof(Counter)); c->name = name; return c; }
    static void counter_free(Counter* c) { free(c); }
    static void counter_add(Counter* c, int n) { c->value += n; }
    static int counter_get(Counter* c) { return c->value; }
}

native type Counter = Counter* {
    let value: int32;                                  // a field of the struct it points to
    let label: String = name;                          // with another name in C
    native function add(n: int32): void = counter_add; // counter_add(self, n)
    native let current: int32 = counter_get;           // read without parentheses: counter_get(self)
    function addTwice(n: int32): void {                // a method written in Larimar
        self.add(n);
        self.add(n);
    }
    static native function make(name: String): Counter = counter_new;
}
native function counter_free(c: Counter): void;

function main(): int32 {
    let c: Counter = Counter.make("clicks");
    c.add(3);
    c.addTwice(2);
    c.value += 10;
    println("${c.label}: ${c.value} ${c.current}");
    counter_free(c);
    return 0;
}
```

Output: `clicks: 17 17`

- **`let`** is a field of the C struct the type points to, read and written with `x.field` (in C,
  `x->field`). After `=` goes its C name when it is another. A type with fields must be a pointer:
  `= Counter*`.
- **`native function m(...) = c_m;`** calls that C function with `self` first and then the arguments.
  If its first parameter is a memory (`m: byte[*]`), it goes before `self` and is not written in the
  call, as in [Passing a memory to C](#passing-a-memory-to-c).
- **`native let x: T = c_x;`** is the same with no arguments, and it is read without parentheses.
- After `= c_m` of either, **`released by f`** says that C makes the text it returns, which is copied and
  freed ([Texts that C makes](#texts-that-c-makes-released-by-on-a-function)):
  `native let name: String = item_name released by free;`.
- With any other expression after `=`, the method is that Larimar expression, as in a class:
  `native function ok(text: String): void = reply(self, 200, text);`.
- **`function`** is a method written in Larimar, and **`static native function`** calls a C function
  without `self` (`Counter.make(...)`). `static function` works too.

## C structs: `native struct`

A C struct passed **by value** is declared with `native struct`, with the fields that are used:

```ts
ccode {
    typedef struct span_t { int from_; int to_; } span_t;
    static span_t widen(span_t s) { s.from_ -= 1; s.to_ += 1; return s; }
}

native struct Span = span_t {
    let from: int32 = from_;                  // the C name, when it is another
    let to: int32 = to_;
    function length(): int32 { return self.to - self.from; }
}
native function widen(s: Span): Span;

function main(): int32 {
    let s: Span = widen({ from: 3, to: 10 });
    println("${s.from} ${s.to} ${s.length()}");
    return 0;
}
```

Output: `2 11 9`

- It is used like any Larimar struct: literals (`{ x: 1, y: 2 }` or `Point { x: 1 }`), field access,
  copies by value, lists (`Point[*]`) and methods written in Larimar.
- C gives the definition (the `.h` or the `ccode`); Larimar does not write it. So the order and the
  alignment of the fields are always C's.
- It is enough to declare the fields that are used: if the C struct has ten and you care about three,
  you declare three.
- Its fields can only be numbers, `bool`, `native` types, pointers (`T*`), other C structs and `String`. A
  `String` field is a C text (`char*` or `char[N]`) that **is read, not assigned**, and it is a view of
  the C text: if C changes or frees it, so does the view. To keep it, `.clone()`.
- The fields not given in a literal are zero, as in C: `{ ai_socktype: 1 }`.

**Why declare it, if C already has it.** Larimar does not read C headers: `native struct` is what tells
it which fields there are and of which type, the same way `native function` tells it the signature of a
function C already has. Nothing is defined twice: the struct is C's, and the declaration only names
what the program uses of it. The methods (`length()` above) are the part that is new: Larimar code
over C's data.

**Its name in C** goes after `=` when it is not the same:

| In Larimar | For a C struct declared as |
|---|---|
| `native struct Span { ... }` | `Span` (the same name) |
| `native struct Span = span_t { ... }` | `span_t`, a name of its own (a `typedef`) |
| `native struct AddrInfo = struct addrinfo { ... }` | `struct addrinfo`, known by its tag |

The way to know is how the header declares a variable of it: `span_t s;` or `struct addrinfo hints;`.

**`native struct` or `native type`.** Both name something of C; what changes is whether Larimar looks
inside:

| | `native type` | `native struct` |
|---|---|---|
| What Larimar does with it | receives it, keeps it and passes it back to C | reads and writes its fields, builds it with a literal |
| What it is | a handle (usually a pointer): `FILE*`, a socket | a value, copied like any struct: `struct timeval` |
| Who frees it | C, when its memory goes (`released by`) | nobody: it is a value |

If the program never needs the fields, `native type` is simpler and does not depend on how the struct
is made.

**In a body of C** a `native struct` parameter is the C struct (`s: Span` is a `span_t`, a copy; `s:
Span*` a pointer to it), and its fields have their C names:

```ts
native function widen(s: Span): Span {
    s.from_ -= 1;
    s.to_ += 1;
    return s;
}

native function grow(s: Span*, by: int32): void { s->to_ += by; }

let s: Span = widen({ from: 3, to: 10 });
grow(&s, 5);                                  // s lives in this function; C has it only during the call
```

**Where `c"..."` is needed.** A name (`span_t`, `sqrt`, `FILE*`, `INT_MAX`) and a struct by its tag
(`struct stat`) are written as they are. `c"..."` is for the rest, what is C text and not a name: a type
of several words (`c"unsigned long"`), an expression (`c"(int)sizeof(void*)"`), a cast or a macro with
arguments. In functions it is rarely needed: that C is written in the body
(`native function start(x: int32): int32 { return (fio_start)(x); }`).

## C constants and variables: `native const`, `native let`

The constants, macros and global variables of C are used by their name, declaring them with their type:

```ts
cinclude "<errno.h>";
cinclude "<limits.h>";

native const INT_MAX: int32;                                       // a C macro
native const ENOENT: int32;
native const POINTER_SIZE: int32 = c"(int)sizeof(void*)";           // a C expression
native let errno: int32;                                           // a C variable

function main(): int32 {
    println("${INT_MAX} ${POINTER_SIZE} ${errno == ENOENT}");
    return 0;
}
```

- **`native const`** does not change; **`native let`** can be read and assigned (`errno = 0;`).
- Larimar writes the name as it is in the C, so macros, `enum` constants and variables all work, and
  also macros that expand into something more complex (`errno`, `stdout`).
- After `=` goes its C name when it is another (`native const MAX: int32 = INT_MAX;`), or, as C text `c"..."`, a C
  expression for what has no name: `sizeof`, a cast, a macro with arguments.
- A `native const` can be a `String` (a text macro); a `native let` cannot.

## C pointers: `T*` and `&`

Many C functions ask for or return pointers: a linked list (`getaddrinfo`), a result written into a
variable (`accept(fd, &addr, &len)`), a buffer. **`T*`** is a C pointer to a number, a `bool`, a C
struct, a `native` type or another pointer:

```ts
ccode {
    typedef struct Node { int value; struct Node* next; const char* name; } Node;
    static Node nodes[3] = { { 10, &nodes[1], "one" }, { 20, &nodes[2], "two" }, { 30, NULL, "three" } };
    static Node* first_node(void) { return &nodes[0]; }
    static void two_results(int* a, int* b) { *a = 7; *b = 42; }
    static int sum_bytes(const unsigned char* p, int n) { int s = 0; for (int i = 0; i < n; i++) s += p[i]; return s; }
}

native struct Node {
    let value: int32;
    let next: Node*;
    let name: String;                       // a C text: it is read
}
native function first_node(): Node*;
native function two_results(a: int32*, b: int32*): void;
native function sum_bytes(p: byte*, n: int32): int32;

function main(): int32 {
    let sum: int32 = 0;
    let p: Node* = first_node();
    while (p != null) {                     // a pointer can be null, as in C
        sum += p.value;                     // p.value is p->value
        p = p.next;
    }
    let a: int32 = 0;
    let b: int32 = 0;
    two_results(&a, &b);                    // C writes into a and b
    let bytes: byte[4] = [1, 2, 3, 4];
    println("${sum} ${a} ${b} ${sum_bytes(bytes, bytes.length)}");
    return 0;
}
```

Output: `60 7 42 10`

- **`p.field`** reads or writes the field of the struct it points to (`p->field` in C). If `p` is
  `null`, the program stops with an error on that line, instead of failing in C.
- **`&x`** gives the address of a variable so that C reads or writes it. **It is only allowed as an
  argument of a C function** (`f(&x)`), so the pointer never lives longer than the call; `x` is a variable
  whose type allows pointers. `&x as Other*` is also allowed there (C sometimes asks for another pointer type).
- **An array where C asks for `T*`** arrives as the pointer to its elements: `fread(buffer, 1, buffer.length, f)`.
- **`as`** converts between pointers (a `sockaddr_in*` as a `sockaddr*`), and between a pointer and an
  opaque `native` type (`void*`).
- A pointer does not point to Larimar memory (`&x` only exists during the call), so it is not part of the
  lifetime rule: what is on the other side belongs to C, and C says how long it lasts.

## Resources: `released by`

Some things from C have to be released: a file (`fclose`), a socket (`close`), a window
(`SDL_DestroyWindow`), a database (`sqlite3_close`). It is declared once, in its `native type`, with the
function that releases it:

```ts
cinclude "<stdio.h>";

native type CFile = FILE* released by fclose;
native function fopen(path: String, mode: String): CFile?;
native function fputs(text: String, f: CFile): int32;
native function fclose(f: CFile): int32;

function main(): int32 {
    for (i in 0..1000) {
        let f: CFile? = fopen("log.txt", "a");
        if (f == null) { return 1; }
        fputs("a line\n", f!);
    }   // each turn: its memory is freed, and with it the file (fclose)
    let g: CFile? = fopen("log.txt", "a");
    release(g);                            // earlier, when needed
    return 0;
}
```

- **A resource lives in a memory, like any data**: where what the C function returns is stored (the
  block of a `let`, the object of a field, `in scratch`...). **When that memory is freed, it is
  released.** What the code shows is where it lives, just like with a `String`.
- **`release(x)`** releases it now. Releasing it twice does nothing; using it afterwards stops the
  program with `a released CFile was used`.
- **The C function that creates it returns `T?`**, because it can fail: a `NULL` pointer (or `-1`, like
  `INVALID_HANDLE_VALUE`) or a negative number (a `-1` descriptor) arrives as `null`.
- **A Larimar function can return what such a function creates** (`function open(path: String): CFile? { return fopen(path, "r"); }`):
  the resource is created where its caller says, like any result.
- **The function that releases it takes exactly one `T`**, and only `release()` can call it: calling it
  by hand would release it twice. It can be a C function or a Larimar one (to release in several steps).
- An object that holds a resource **cannot be cloned** (it would be released twice).
- If the function that releases it exists on one system only (`closedir` on Unix), the resource only
  exists there.
- A resource can also have [members](#c-types-with-members):
  `native type Db = sqlite3* released by sqlite3_close { native function errmsg(): String = sqlite3_errmsg; ... }`.

## Texts that C makes: `released by` on a function

Some C functions return a text that is now the caller's, made with `malloc` (or with the library's own
allocator): `strdup`, `realpath(path, NULL)`, `sqlite3_expanded_sql`. After the result (and its `= C`, if
there is one) comes **`released by`** with the function that frees it:

```ts
cinclude "<string.h>";
cinclude "<stdlib.h>";

native function strdup(text: String): String released by free;
native function free(text: String): void;

function main(): int32 {
    for (i in 0..1000) {
        let copy: String = strdup("text ${i}");
        if (i == 999) { println(copy); }
    }
    return 0;
}
```

Output: `text 999`

- The text is **copied** into the memory where the result goes, like any result (the block of a `let`,
  an object, `in scratch`, a buffer), and C's is freed right away: Larimar does not keep C's pointer, so
  nothing leaks and nothing is freed twice.
- With `String?`, a `NULL` arrives as `null` (and there is nothing to free).
- The function after `released by` is a `native function` that takes one `String`, and only the compiler
  calls it. In C it is declared with `void*`, as `free(void*)` or `sqlite3_free(void*)` are.
- A text that C keeps (a static one, or one that belongs to something of C, like `sqlite3_errmsg`) is not
  freed: it is declared without `released by`.

---
