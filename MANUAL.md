# Larimar Manual

This manual explains how to write programs in Larimar, from the simplest to the most advanced.
All the complete examples (the ones with `function main`) compile and run as they are, and their
output is the one shown.

The names of the language, the tool and the examples are in English, like the explanations.
[Leer en español](MANUAL_ES.md).

## Contents

1. [Getting started](#1-getting-started)
2. [Structure of a program](#2-structure-of-a-program)
3. [Variables and constants](#3-variables-and-constants)
4. [Basic types](#4-basic-types)
5. [Operators](#5-operators)
6. [Text (`String`)](#6-text-string)
7. [Control flow](#7-control-flow)
8. [Functions](#8-functions)
9. [Structs](#9-structs)
10. [Classes and inheritance](#10-classes-and-inheritance)
11. [Interfaces](#11-interfaces)
12. [Enums](#12-enums)
13. [`switch` and patterns](#13-switch-and-patterns)
14. [Optionals and `null`](#14-optionals-and-null)
15. [Arrays and lists](#15-arrays-and-lists)
16. [Memory](#16-memory)
17. [The lifetime rule and `clone()`](#17-the-lifetime-rule-and-clone)
18. [Lambdas and closures](#18-lambdas-and-closures)
19. [Errors: `throw`, `try` and `catch`](#19-errors-throw-try-and-catch)
20. [Failures at run time](#20-failures-at-run-time)
21. [`Any`: free-form data](#21-any-free-form-data)
22. [Threads](#22-threads)
23. [Calling C](#23-calling-c)
24. [Modules](#24-modules)
25. [Standard library](#25-standard-library)
26. [Projects: `larimar.toml` and `larimar build`](#26-projects-larimartoml-and-larimar-build)
27. [What the transpiler generates](#27-what-the-transpiler-generates)
28. [Larimar written in Larimar](#28-larimar-written-in-larimar)
29. [Current limitations](#29-current-limitations)
30. [Quick reference](#30-quick-reference)

---

## 1. Getting started

Larimar is translated into a single C99 file, which is then compiled with any C compiler to get an
executable. The `larimar` tool does both steps:

```sh
./build-bootstrap.sh             # once: builds larimarc and installs it in ../out/larimar (bin/, std/, MANUAL.md)
export LARIMAR_HOME="$PWD/../out/larimar"
export PATH="$LARIMAR_HOME/bin:$PATH"   # on Windows, add the bin folder to the PATH

larimar new hello                # creates hello/larimar.toml and hello/src/main.lar
cd hello
larimar run                      # translates to C, compiles with gcc or clang and runs
```

`larimar run` needs a C compiler installed (gcc or clang; on Windows, MinGW).
[Section 26](#26-projects-larimartoml-and-larimar-build) explains the project file.

The first program (`src/main.lar`):

```actionscript
function main(): int32 {
    println("Hello, world");
    return 0;
}
```

Output: `Hello, world`

`main` is the entry point. It returns `int32` (the exit code of the program) or `void`.

If the program has errors, Larimar lists them all, with the file and the line, and generates no C:

```
Semantic Error [src/main.lar:2]: Initializer of 'x': expected int32 but got String.
```

---

## 2. Structure of a program

A file is a list of **declarations**. At the top level there can only be declarations, not loose
statements:

| Declaration | Example |
|---|---|
| Import | `import geo.shapes;` (at the start of the file; see [Modules](#24-modules)) |
| Function | `function add(a: int32, b: int32): int32 { ... }` |
| Constant | `const MAX: int32 = 64;` |
| Global variable | `let counter: int32 = 0;` |
| Struct | `struct Point { ... }` |
| Class | `class Animal { ... }`, `synchronized class Counter { ... }` (see [Threads](#22-threads)) |
| Interface | `interface Drawable { ... }` |
| Enum | `enum Color { Red, Green }` |
| C code | `c_include "<math.h>";`, `extern function ...`, `extern type ...` |

Any declaration can have `public` in front so that other modules can use it.

The order of the declarations does not matter: a function can use another one that is further down.
Global variables are initialized in the order in which they appear, before `main`.

Comments are as in C: `// to the end of the line` and `/* in a block */`.
Each statement ends in `;`, and blocks go between `{ }`.

---

## 3. Variables and constants

```actionscript
let age: int32 = 30;
let name: String = "Ana";
age = 31;          // variables can be reassigned
age += 1;          // also +=, -=, *=, /=, %=, &=, |=, ^=
```

- The **type is required**, and so is the **initial value**: there are no uninitialized variables.
- A variable declared inside a block only exists inside it.
- A variable can be declared with the same name as one of an outer block; the inner one hides it.

**Constants** are declared at the top level, and their value is computed when compiling. They can
be numbers, `bool` or `String`, and they can be used as the size of an array:

```actionscript
const SIZE: int32 = 16;
const KILO: int64 = 1024;
const MEGA: int64 = KILO * KILO;
const LABEL: String = "sensor";

function main(): int32 {
    let data: int32[SIZE] = [];
    println("${LABEL}: ${data.length} of ${SIZE}, ${MEGA} bytes");
    return 0;
}
```

Output: `sensor: 0 of 16, 1048576 bytes`

---

## 4. Basic types

| Type | Values | In C |
|---|---|---|
| `int8`, `int16`, `int32`, `int64` | signed integers | `int8_t` … `int64_t` |
| `byte` (or `uint8`), `uint16`, `uint32`, `uint64` | unsigned integers | `uint8_t` … `uint64_t` |
| `float32`, `float64` | decimals | `float`, `double` |
| `bool` | `true`, `false` | `bool` |
| `String` | text | a structure of the runtime |
| `void` | nothing (only as a return type) | `void` |

**Primitive types are written in lowercase**: they are simple values that never need memory, have
no fields and cannot be redefined. Everything else starts with an uppercase letter: `String` (which
does need memory), and the structs, classes, interfaces and enums you declare. So by looking at the
name you know whether a type is the language's or yours.

### Numeric literals

```actionscript
let a: int32 = 1_000_000;     // _ separates digits
let b: byte = 0xFF;           // hexadecimal
let c: byte = 0b1010_0101;    // binary
let d: float64 = 2.5e3;       // exponent
```

An integer literal takes the type that is expected in that place. The compiler checks that it fits:
`let b: byte = 256;` is an error.

### Characters

`'a'` is the code of the character (its Unicode number), and it is used like any integer literal:
it takes the type that is expected. It is useful above all to compare the bytes of a text:

```actionscript
function digits(s: String): int32 {
    let n: int32 = 0;
    for (b in s) {
        if (b >= '0' && b <= '9') { n += 1; }
    }
    return n;
}

function main(): int32 {
    let first: byte = "hola"[0];
    println("${first == 'h'} ${digits("a1b22")} ${'A'} ${'\n'} ${'€'}");
    return 0;
}
```

Output: `true 3 65 10 8364`

Escapes: `'\n'`, `'\t'`, `'\r'`, `'\0'`, `'\\'`, `'\''` and `'\"'`. A literal has exactly one
character; if the code does not fit in the type (`let b: byte = '€';`), it is an error.

### Overflow

Integers **wrap around** when they go past the maximum or the minimum, signed and unsigned.
There is never undefined behavior:

```actionscript
function main(): int32 {
    let max: int32 = 2147483647;
    let b: byte = 255;
    b += 1;
    println("${max + 1} ${b}");
    return 0;
}
```

Output: `-2147483648 0`

### Conversions with `as`

There are no automatic conversions between numeric types. They are done with `as`:

```actionscript
function main(): int32 {
    let n: int32 = 7;
    let wide: int64 = n as int64;
    let half: float64 = (n as float64) / 2.0;
    let huge: float64 = 1e20;
    println("${wide} ${half} ${huge as int32} ${-1.5 as byte}");
    return 0;
}
```

Output: `7 3.5 2147483647 0`

From decimal to integer the value is truncated, and if it does not fit the nearest limit is used
(instead of the undefined behavior of C).

---

## 5. Operators

| Precedence (lowest to highest) | Operators |
|---|---|
| conditional | `c ? a : b` (right to left) |
| default value of an optional | `??` |
| logical or | `\|\|` |
| logical and | `&&` |
| comparison | `==` `!=` `<` `<=` `>` `>=` |
| bits | `\|`, then `^`, then `&` |
| shift | `<<` `>>` |
| sum | `+` `-` |
| product | `*` `/` `%` |
| conversion | `as` |
| unary | `-` `!` `~` |
| suffixes | call `f()`, field `a.b`, index `a[i]`, `x!` |

Rules:
- The two sides of an operator must be **of the same type** (`int32 + int64` is an error; use `as`).
  Literals adapt to the other side.
- `as` applies before comparisons: `n > MAX as int64 ? a : b` is `(n > (MAX as int64)) ? a : b`,
  without parentheses. After `as T`, a `?` followed by the start of an expression is the one of the
  conditional; followed by `)`, `;`, `,`, `??`, `==`... it is part of the type (`T?`).
- `/` and `%` between integers check division by zero. `%` is only for integers.
- Bit operators are **above** comparisons, so `x & 1 == 0` means `(x & 1) == 0`, not C's trap.
- In `a << n`, only the low bits of `n` are used (for `uint32`, `n & 31`).
- `&&` and `||` do not evaluate the right side if it is not needed.
- `==` compares numbers, `bool`, `String` (by content), enums without data and objects (by identity).
  An optional object (`Node?`) can be compared with a `Node`.

### The conditional `c ? a : b`

It gives `a` if the condition is `true`, and `b` otherwise. Only the chosen side is evaluated:

```actionscript
class Animal { let name: String; }
class Dog extends Animal { }
class Cat extends Animal { }

function sign(n: int64): String { return n > 0 ? "+" : n < 0 ? "-" : "0"; }

function main(): int32 {
    let big: int64 = 10000000000;
    let small: bool = true;
    let n: int64 = small ? 1 : big;                    // the literal takes the type int64
    let dog: Dog = Dog { name: "Rex" };
    let cat: Cat = Cat { name: "Tom" };
    let pet: Animal = small ? dog : cat;              // the nearest common class
    let maybe: Dog? = small ? null : dog;             // with null, the type is optional
    println("${n} ${pet.name} ${maybe == null} ${sign(-3)}");
    return 0;
}
```

Output: `1 Rex true -`

- The type comes from the side that is not a loose literal (a number or `null`); the other adapts.
  If the two sides have different types (`int64` and `String`), it is an error: give the variable a type.
- Each side knows what the condition says: in `x != null ? x.value : 0`, `x` is not `null` on the left.
- It also works in constants: `const SIZE: int32 = DEBUG ? 16 : 1024;`.

---

## 6. Text (`String`)

A `String` is **immutable**: once created, it does not change. It is compared by content and has
`length` (in bytes, because the text is UTF-8).

```actionscript
enum Color { Red, Green }

function main(): int32 {
    let name: String = "Ana";
    let n: int32 = 3;
    let color: Color = Color.Green;
    let message: String = "${name} has ${n} apples of color ${color}";
    println(message);
    println("${name == "Ana"} ${message.length}");
    return 0;
}
```

Output:
```
Ana has 3 apples of color Green
true 31
```

- **Interpolation**: `"${expression}"` accepts numbers, `bool`, `String` and enums (the name of the variant is printed).
- **Escapes**: `\n`, `\t`, `\r`, `\0`, `\\`, `\"`, `\'` and `\$` (to write a literal `$`).
- **There is no `+` for text**: it is joined with interpolation, `"${a}${b}"`.
- `print(text)` and `println(text)` write to the standard output.

An interpolated text needs memory to exist. Where it is created is explained in
[section 16](#16-memory); for now it is enough to know that, if you say nothing, the compiler puts
it where it belongs and frees it when it is no longer used.

### Text on several lines: `"""`

As in Java, a text block starts with `"""` and a line break, and ends with `"""`. The indentation
common to all the lines (and to the line of the closing `"""`, if it is alone) is removed, and so are
the spaces at the end of each line. Quotes need no escape, and escapes and `${...}` work the same:

```actionscript
function main(): int32 {
    let name: String = "Ana";
    let page: String = """
        <p class="greeting">
          Hola, ${name}.
        </p>
        """;
    print(page);
    return 0;
}
```

Output:
```
<p class="greeting">
  Hola, Ana.
</p>
```

With the closing `"""` at the end of the last line, the text does not end in a line break.

### Raw text: `raw"""`

A `raw"""` is a text block taken **exactly as written**: without escapes (a backslash `\` is a
backslash) and without `${...}`. It is useful for text that has its own quotes and backslashes, like
C code, SQL, regular expressions or templates:

```actionscript
let code: String = raw"""
    printf("hola\n");      /* \n is two characters: \ and n */
    char* p = "${HOME}";   /* ${...} is text, it is not interpolated */
    """;
```

- As with `"""`, it starts with `raw"""` and a line break, and the common indentation is removed.
- If the text has three quotes in a row, it is opened with more quotes and closed with the same:
  `raw""""` ... `""""`.
- The compiler writes its runtime this way (`src/runtime.lar`): the C goes as it is, escaping nothing.

### Methods

A `String` is made of **bytes** (UTF-8): `s[i]` is a `byte`, `for (b in s)` goes over its bytes,
and `length` counts bytes. An accented letter takes two; to count letters there is `codePointCount()`.

```actionscript
function main(): int32 {
    let s: String = "  Hello, Larimar world!  ";
    let t: String = s.trim();                                  // a view: it copies nothing
    println("[${t}] ${t.indexOf("o") ?? -1} ${t.contains("Larimar")} ${t.count("l")}");
    println("${t.substring(7, 14)} ${t.toUpperCase()} ${t.replace("l", "L")}");
    let parts: String[*] = "a,b,,c".split(",");
    println("${parts.length}: ${parts.join(" | ")}");
    println("${"42".toInt() ?? 0} ${"0x1F".toInt() ?? 0} ${"x".toInt() ?? -1} ${"2.5".toFloat() ?? 0.0}");
    println("${"apple" < "banana"} ${"7".padStart(3, "0")} ${"ab".repeat(3)} ${t[0]}");
    return 0;
}
```

Output:
```
[Hello, Larimar world!] 4 true 3
Larimar HELLO, LARIMAR WORLD! HeLLo, Larimar worLd!
4: a | b |  | c
42 31 -1 2.5
true 007 ababab 72
```

| Group | Methods |
|---|---|
| Query | `length`, `isEmpty()`, `isBlank()`, `s[i]` (a `byte`), `for (b in s)`, `codePointCount()` |
| Search | `indexOf(t)`, `indexOf(t, from)`, `lastIndexOf(t)` (they give `int32?`), `contains(t)`, `startsWith(t)`, `endsWith(t)`, `count(t)` |
| Cut: **views**, without copying | `substring(from)`, `substring(from, to)`, `trim()`, `trimStart()`, `trimEnd()`, `bytes()` (a `byte[]`) |
| Create new text | `toUpperCase()`, `toLowerCase()`, `replace(a, b)`, `repeat(n)`, `padStart(n, s)`, `padEnd(n, s)` |
| Split and join | `split(sep)`, `lines()`, `codePoints()` (new lists); `list.join(sep)` |
| Compare | `==`, `!=`, `<`, `<=`, `>`, `>=` (byte order), `compareTo(t)`, `equalsIgnoreCase(t)` |
| Convert | `toInt()` (`int64?`: decimal, `0x`, `0b`, with `_`), `toFloat()` (`float64?`), `toBool()` (`bool?`) |

- **Views share the bytes of the original text**: cutting is instant and uses no memory. They live as
  long as the original, and the lifetime rule checks it.
- **What creates new text** goes, like interpolation, where it belongs or to the memory you say with
  `in`: `s.toUpperCase() in memory`. The lists of `split`, `lines` and `codePoints` too.
- `toUpperCase`, `toLowerCase` and `equalsIgnoreCase` change only ASCII letters.
- A `String` is not modified: `s[0] = 65` is an error. To build text there is `StringBuilder`.

### `StringBuilder`

To build a big text in parts without creating a new one each time:

```actionscript
function main(): int32 {
    let out: StringBuilder = {};
    for (i in 0..3) { out.add("item ${i}, "); }   // the interpolation is written straight into the builder
    out.addLine("end");
    let text: String = out.toString();          // a view of what has been built so far
    println("${text.length} ${out.length()}");
    print(text);
    return 0;
}
```

Output:
```
28 28
item 0, item 1, item 2, end
```

`add(text)`, `addLine(text)`, `length()`, `toString()` and `clear()`. The text grows in the memory of
the builder. What `toString()` returns does not change even if more is added afterwards or `clear()`
is called.

---

## 7. Control flow

### `if`

```actionscript
function classify(n: int32): String {
    if (n < 0) {
        return "negative";
    } else if (n == 0) {
        return "zero";
    } else {
        return "positive";
    }
}
```

Braces are required. The condition must be `bool`: `if (1)` is an error.

### `while`

```actionscript
let i: int32 = 0;
while (i < 10) {
    i += 1;
}
```

### `for`

```actionscript
for (i in 0..5) { }            // 0, 1, 2, 3, 4 (the end is not included)
for (x in items) { }           // each element
for (i, x in items) { }        // index and element
```

The variables of the `for` cannot be reassigned inside the body.

### Blocks

Loose braces form a block: what is declared inside only exists there, and the memories created inside
are freed when it closes. It is useful to bound memories and threads ([section 22](#22-threads)).

```actionscript
{
    let scratch: byte[*] = [] in heap;
    let text: String = "temporary ${1}" in scratch;
    println(text);
}   // 'scratch' is freed here
```

### `break` and `continue`

They work as in C or Java, inside `while` and `for`.

```actionscript
function main(): int32 {
    let sum: int32 = 0;
    for (i in 0..10) {
        if (i % 2 == 0) { continue; }
        if (i > 7) { break; }
        sum += i;
    }
    println("${sum}");     // 1 + 3 + 5 + 7
    return 0;
}
```

Output: `16`

---

## 8. Functions

```actionscript
function add(a: int32, b: int32): int32 {
    return a + b;
}

function greet(name: String): void {
    println("Hello, ${name}");
}

function bye() {               // ": void" can be left out
    println("Bye");
}
```

- Parameters always have a type.
- If the function does not return `void`, **every path** must end in `return` (or `throw`).
  A `while (true)` without `break` counts as a path that never ends.
- Functions are declared at the top level or inside classes and structs. Inside a body, lambdas are used.
- Functions are not values; to pass one, wrap it in a lambda: `(x) -> { return add(x, 1); }`.

### `main` and the arguments of the program

`main` can receive the arguments the program was run with (without its own name):

```actionscript
function main(args: String[]): int32 {
    if (args.length == 0) {
        println("usage: greet <name>");
        return 2;
    }
    println("Hello, ${args[0]}");
    return 0;
}
```

With `larimar run -- Ana` it prints `Hello, Ana`. What `main` returns is the exit code.

---

## 9. Structs

A `struct` is a **value**: a group of fields that is copied whole when it is assigned or passed.
It needs no special memory; it lives where the variable lives.

```actionscript
struct Vector2 {
    let x: int32;
    let y: int32 = 0;                      // default value

    function length2(): int32 {            // a method
        return self.x * self.x + self.y * self.y;
    }

    function scale(k: int32): void {       // methods can modify self
        self.x = self.x * k;
        self.y = self.y * k;
    }

    operator +(other: Vector2): Vector2 {
        return { x: self.x + other.x, y: self.y + other.y };
    }

    operator ==(other: Vector2): bool {
        return self.x == other.x && self.y == other.y;
    }
}

function main(): int32 {
    let a: Vector2 = { x: 1, y: 2 };       // literal: the type comes from the variable
    let b: Vector2 = Vector2 { x: 3 };     // with the type written; y = 0 by default
    let c: Vector2 = a + b;
    c.scale(2);
    let copy: Vector2 = c;                 // an independent copy
    copy.x = 100;
    println("(${c.x}, ${c.y}) ${c.length2()} ${copy.x} ${a == b}");
    return 0;
}
```

Output: `(8, 4) 80 100 false`

### Literals

- `{ field: value, ... }` when the type is known from the context (a variable, a parameter, a `return`).
- `Type { field: value }` when it is not.
- `{ x, y }` is short for `{ x: x, y: y }`.
- Fields without a default value are **required**: if one is missing, it is a compile error.
- A struct never has `in`: it is a value and lives in its variable. (Class objects, on the other hand, always have it.)
- Default values must be constants (literals, `null`, `[]`, enums or structs made of constants).

### Operators

A struct (or a class) can define `+ - * / % == <` and the unary `-` (`operator -()`, without parameters).
From `==` you get `!=`, and from `<` you get `>`, `<=` and `>=`.
Without `operator ==`, comparing two structs with `==` is an error.

---

## 10. Classes and inheritance

A class defines **objects**: they have identity, live in a memory and are used by **reference**.
Assigning an object to another variable does not copy it; both variables point to the same object.

```actionscript
class Animal {
    let name: String;

    function sound(): String { return "..."; }

    function introduce(): void {
        println("${self.name} says ${self.sound()}");
    }
}

class Dog extends Animal {
    let breed: String = "mixed";

    override function sound(): String { return "woof"; }
}

class Puppy extends Dog {
    override function sound(): String { return "yip"; }

    override function introduce(): void {
        super.introduce();
        println("(and it is a ${self.breed} puppy)");
    }
}

function main(): int32 {
    let a: Animal = Animal { name: "Kitty" };
    let d: Dog = Dog { name: "Rex", breed: "shepherd" };
    let p: Animal = Puppy { name: "Bobby" };

    a.introduce();
    d.introduce();
    p.introduce();

    let same: Animal = d;       // the same reference
    same.name = "Rexy";
    println(d.name);
    return 0;
}
```

Output:
```
Kitty says ...
Rex says woof
Bobby says yip
(and it is a mixed puppy)
Rexy
```

- Objects are created with a literal, like structs: `Dog { name: "Rex" }`, or `Dog {}` if every field
  has a default value. There is no `new`.
- An object lives in a memory: if nothing is said, the one of its variable (its block), the one of the
  list it is added to, or the caller's if it is returned. With `in` you choose: `Dog { name: "Rex" } in memory`,
  or `in default` so that it lives the whole program (see [section 16](#16-memory)).
- A struct is a value, it does not live in any memory; writing `in` after it is an error.
- **Single inheritance**: `extends` one class only. Fields and methods are inherited.
- Every method is **virtual**: the one of the real class of the object runs.
- Redefining a method requires **`override`**, and it must have exactly the same signature.
  Writing `override` on a method that does not exist in the parent is an error too.
- `super.method(...)` calls the parent's version.
- A field cannot redefine an inherited one.
- A `Dog` can be used where an `Animal` is expected. Not the other way around: to go from `Animal` to `Dog`
  a `switch` with a type pattern is used ([section 13](#13-switch-and-patterns)).
- `==` between objects compares identity (whether they are the same object), unless the class defines `operator ==`.

### Static functions

A static function belongs to the type, not to an object: it has no `self` and is called with the name
of the type. It can be written inside the type with `static`, or outside with `function Type.name`;
both forms are the same.

```actionscript
class Order {
    let id: int32;
    let owner: String;

    static function make(owner: String): Order {
        return Order { id: 1, owner: owner };
    }
}

function Order.empty(): Order {
    return Order { id: 0, owner: "" };
}

function main(): int32 {
    let o: Order = Order.make("Ana");
    println("${o.owner} ${Order.empty().id}");
    return 0;
}
```

- They work in `struct`, `class`, `enum` and `native type`. Interfaces have no static functions.
- In a `native type` you can also write `static native function name(...) = c_function(...);`.
- `function Type.name` can only be written in the module that declares the type.
- They are always called as `Type.name(...)` (or `module.Type.name(...)`); not from an object.
- They do not use `self`, do not go in the virtual table and are not redefined with `override`.
- A type cannot have a method and a static function with the same name.
- They are visible where their type is: the type is marked `public`, not the function.

---

## 11. Interfaces

An interface describes **what can be done** with something: only method signatures, without fields.

```actionscript
interface Drawable {
    function draw(): void;
}
```

There are three ways to fulfill it:

**1. With a class**, declaring it with `implements` (a class can implement several):

```actionscript
class Circle implements Drawable {
    let radius: float64;
    function draw(): void { println("circle of radius ${self.radius}"); }
}
```

**2. With a literal**, giving each method as a lambda:

```actionscript
let mark: Drawable = { draw: () -> { println("X"); } };
```

**3. With a lambda**, if the interface has a single method:

```actionscript
let quick: Drawable = () -> { println("quick"); };
```

A complete example:

```actionscript
interface Drawable {
    function draw(): void;
}

class Circle implements Drawable {
    let radius: float64;
    function draw(): void { println("circle of radius ${self.radius}"); }
}

function main(): int32 {
    let things: Drawable[*] = [];
    things.push(Circle { radius: 2.0 });
    things.push({ draw: () -> { println("a literal"); } });
    things.push(() -> { println("a lambda"); });
    for (t in things) { t.draw(); }
    return 0;
}
```

Output:
```
circle of radius 2.0
a literal
a lambda
```

Whoever receives a `Drawable` does not care which of the three forms is behind it.

---

## 12. Enums

An enum is a value that is **one of several variants**. Variants can carry data.

```actionscript
enum State { Off, On, Failed }

enum Shape {
    Circle(radius: float64),
    Rect(width: float64, height: float64),
    Empty
}
```

Creating values:

```actionscript
let s: State = State.On;
let a: Shape = Shape.Circle { radius: 2.0 };            // by name
let b: Shape = Shape.Rect { height: 4.0, width: 3.0 };  // the order does not matter
let c: Shape = Shape.Rect(3.0, 4.0);                    // shortcut by position
let d: Shape = Shape.Empty;
```

- Enums **without data** can be compared with `==` and `!=`.
- Enums with data are examined with a `switch` ([section 13](#13-switch-and-patterns)).
- In an interpolation, an enum is written with the name of its variant: `"${s}"` gives `On`.
- Enums are values: they are copied, like structs.

---

## 13. `switch` and patterns

The `switch` follows the modern Java style: each case uses `->`, there is no "fall through" from one
case to the next, and `break` is not needed.

### As a statement

```actionscript
switch (state) {
    case Off -> println("off");
    case On -> {
        println("on");
        println("all good");
    }
    case Failed -> println("failed");
}
```

A case without braces must be a call; for anything else use `{ }`.

### As an expression

```actionscript
let text: String = switch (n) {
    case 0 -> "zero";
    case 1, 2, 3 -> "a few";               // several values in a case
    default -> {
        if (n < 0) { yield "negative"; }   // yield gives the value from a block
        yield "many";
    }
};
```

Inside a `switch` used as an expression, blocks end with `yield value;`, and `return` is not allowed.
If the result is optional (`T?`), a case can give `null`:

```actionscript
function digit(c: byte): int32? {
    return switch (c) {
        case '0' -> 0;
        case '1' -> 1;
        default -> null;
    };
}
```

### Patterns

| Pattern | Works with | Meaning |
|---|---|---|
| `0`, `-1`, `2.5`, `"a"`, `true` | numbers, `String`, `bool` | equal to that value |
| `MAX` | the same | equal to that constant |
| `Circle` | enums | that variant |
| `Circle { radius }` | enums | that variant, taking out the field `radius` |
| `Rect { width: w, height: h }` | enums | taking out fields with another name |
| `Rect r` | enums | the variant, with the whole value in `r` |
| `Rect { height } r` | enums | both things |
| `Dog d` | classes and interfaces | if the object is a `Dog` (or a subclass), as `Dog` in `d` |
| `null` | optionals | if there is no value |
| `default` | everything | any other case |

The fields of a pattern are taken **by name**: the order does not matter and the ones you do not name are ignored.

`when` adds a condition to a case:

```actionscript
enum Shape { Circle(radius: float64), Rect(width: float64, height: float64), Empty }

class Animal { let name: String; }
class Dog extends Animal { let breed: String = "mixed"; }

function area(s: Shape): float64 {
    return switch (s) {
        case Circle { radius } when radius > 10.0 -> 0.0;   // too big: not counted
        case Circle { radius } -> 3.0 * radius * radius;
        case Rect { width: w, height: h } -> w * h;
        case Empty -> 0.0;
    };
}

function describe(a: Animal): String {
    return switch (a) {
        case Dog d -> "a ${d.breed} dog";
        default -> "an animal";
    };
}

function main(): int32 {
    println("${area(Shape.Circle { radius: 2.0 })} ${area(Shape.Rect(3.0, 4.0))} ${area(Shape.Empty)}");
    println(describe(Dog { name: "Rex", breed: "shepherd" }));
    println(describe(Animal { name: "Kitty" }));
    return 0;
}
```

Output:
```
12.0 12.0 0.0
a shepherd dog
an animal
```

### Covering every case

- A `switch` on an **enum** must cover every variant (or have `default`), whether it is a statement
  or an expression. If you add a variant tomorrow, the compiler points at each `switch` to review.
- Cases with `when` do not count as covered.
- A `switch` used as an **expression** on any other type needs `default`.
- Inside a `switch` in a loop, `break` and `continue` refer to the loop.

### A single case: `x is T name`

To ask about a single class a `switch` is not needed: `x is Dog` is `true` if `x` is a `Dog`
(or a subclass), and `x is Dog d` also gives it the name `d`, already as `Dog`, where the test is known
to be true: inside the `if`, on the right of `&&`, on one side of `?:`, and after an
`if (!(x is Dog d)) { return ...; }`.

```actionscript
class Animal { let name: String; }
class Dog extends Animal { let breed: String = "mixed"; }

function describe(a: Animal?): String {
    if (a is Dog d && d.breed != "mixed") { return "${d.name}, a ${d.breed}"; }
    if (!(a is Dog d)) { return "not a dog"; }
    return "${d.name}, a dog";
}

function main(): int32 {
    let rex: Dog = Dog { name: "Rex", breed: "beagle" };
    let tom: Animal = Animal { name: "Tom" };
    println("${describe(rex)} | ${describe(tom)} | ${describe(null)} | ${tom is Dog}");
    return 0;
}
```

Output: `Rex, a beagle | not a dog | not a dog | false`

`x` can be an object, an optional object or an interface, and `T` a class it can match.

---

## 14. Optionals and `null`

No value is `null` unless its type allows it with `?`.

```actionscript
let a: int32 = null;      // error
let b: int32? = null;     // fine
```

To use an optional:

| Form | What it does |
|---|---|
| `x ?? value` | `x` if it has a value; otherwise, `value` |
| `x!` | the value; if it is `null`, the program stops |
| `if (x != null) { ... }` | inside the block, `x` is used as if it were not optional |
| `switch (x) { case null -> ...; default -> ... }` | by cases |

```actionscript
class Node {
    let value: int32;
    let next: Node? = null;
}

function count(first: Node?): int32 {
    let total: int32 = 0;
    let current: Node? = first;
    while (current != null) {
        total += current.value;
        current = current.next;
    }
    return total;
}

function describe(n: Node?): String {
    if (n == null || n.value < 0) { return "none"; }
    return "value ${n.value}";
}

function main(): int32 {
    let c: Node = Node { value: 3 };
    let b: Node = Node { value: 2, next: c };
    let a: Node = Node { value: 1, next: b };
    println("${count(a)} ${count(null)} ${describe(a)} ${describe(null)}");

    let maybe: int32? = null;
    println("${maybe ?? 7}");
    maybe = 5;
    if (maybe != null) { println("has ${maybe + 1}"); }
    return 0;
}
```

Output:
```
6 0 value 1 none
7
has 6
```

### Where it is known not to be `null`

The compiler follows the conditions, and an optional local variable or parameter is used as if it
were not optional where it was already checked:

- inside `if (x != null) { ... }`, and in the `else` of `if (x == null) { ... } else { ... }`;
- after `if (x == null) { return ...; }` (or `throw`, `break`, `continue`): in the rest of the block;
- on the right of `x != null && ...`, and of `x == null || ...`; and with several: `a != null && b != null`;
- inside `while (x != null) { ... }`;
- on each side of `c ? a : b`, according to the condition.

It ends where the variable is assigned again: in `current = current.next;` the right side still
knows that `current` is not `null`, but what follows no longer does. Fields (`n.next`) are not
narrowed, because another function or a thread could change them between the check and the use:
keep them in a local variable first. A `!` that is no longer needed is allowed and does nothing.

---

## 15. Arrays and lists

There are three ways to group elements of the same type:

| Type | What it is | Where it lives |
|---|---|---|
| `T[N]` | up to N elements; fixed capacity, variable length | with the variable, like a struct |
| `T[]` | in a parameter: any array, borrowed | where the original is |
| `T[*]` | a list that grows | in a memory |

### `T[N]`

```actionscript
function main(): int32 {
    let xs: int32[8] = [5, 3, 8];         // capacity 8, length 3
    let ok: bool = xs.push(1);            // true: it fit
    println("${xs.length} ${xs[0]} ${ok}");
    xs[0] = 50;
    let inferred: int32[] = [1, 2, 3];    // capacity taken from the literal: 3
    println("${inferred.push(4)}");       // false: it is full
    return 0;
}
```

Output:
```
4 5 true
false
```

- `[]` in a variable means "the capacity comes from the value".
- `push` returns `false` if it does not fit; it never writes outside the array.
- A `T[N]` can be assigned to a `T[M]` if `N <= M` (the elements are copied).
- It is a value: assigning it copies it.

### `T[]` in parameters

A `T[]` parameter accepts any array or list of `T`, without copying it. Its elements can be read and
changed, but not added:

```actionscript
function sum(xs: int32[]): int32 {
    let total: int32 = 0;
    for (x in xs) { total += x; }
    return total;
}
```

### `T[*]`

```actionscript
let numbers: int32[*] = [];
for (i in 0..1000) { numbers.push(i); }
```

It grows inside its memory. If the memory has a fixed size and fills up, `push` returns `false`.

### Operations

| Operation | `T[N]` | `T[]` | `T[*]` |
|---|---|---|---|
| `.length`, `x[i]`, `x[i] = v`, `for` | yes | yes | yes |
| `.push(v)` → `bool`, `.clear()` | yes | no | yes |
| `.pop()` → the last one (and removes it) | yes | no | yes |
| `.contains(v)` → `bool` (compares with `==`) | yes | yes | yes |
| `.filter(f)`, `.map(f)` | give `T[N]` | give `T[*]` | give `T[*]` |
| `.join(sep)` (lists of `String`) | yes | yes | yes |
| `.clone()` | yes | no | yes |

An index out of range, or `pop()` on an empty list, stops the program with a message
([section 20](#20-failures-at-run-time)).

`map` needs to know the type of the result, so it is used where there is a declared type:

```actionscript
function main(): int32 {
    let numbers: int32[*] = [3, 8, 15, 4];
    let even: int32[*] = numbers.filter((n) -> { return n % 2 == 0; });
    let labels: String[*] = even.map((n) -> { return "#${n}"; });
    for (i, t in labels) { println("${i}: ${t}"); }
    return 0;
}
```

Output:
```
0: #8
1: #4
```

The result of `filter` and `map` on a list is created in the same memory as the list, unless you say
another one with `in`.

---

## 16. Memory

Larimar **has no garbage collector**, and you almost never have to think about memory: the compiler
organizes it in **memories** that are freed whole, at moments that can be seen in the code.

> Everything that needs memory lives in a memory, and everything in a memory is freed together.

### What needs memory

Numbers, `bool`, structs, enums and `T[N]` do **not** need it: they live with their variable.
Class objects, `T[*]` lists, interpolated texts, `Any` tables and interface literals do need it.

### Automatic memories

Without writing anything, each thing lives where it belongs:

| What is created | Where it lives | It is freed |
|---|---|---|
| what is not kept anywhere: arguments, parts of an expression, the text of a `println` | the temporary memory of the statement | when the statement ends (at the `;`) |
| the value of a local variable (`let`, or when assigning it) | the memory of its block | when the block closes (`}`); in a loop, on each turn |
| what is added to a list, or put in a field or in a table | the memory of the list, of the object or of the table | with it |
| what a function returns | the memory the caller says | it depends on the caller |
| the initial value of a global variable | the default memory | never |

```actionscript
class Order { let customer: String; let total: int32 = 0; }

function createOrder(customer: String, n: int32): Order {
    return Order { customer: "${customer} #${n}", total: n * 10 };   // where the caller says
}

function main(): int32 {
    let orders: Order[*] = [];                     // in the memory of main's block
    for (i in 0..3) {
        let o: Order = createOrder("Ana", i);      // in the memory of the turn: freed on each turn
        println("${o.customer}: ${o.total}");      // the text is a temporary of this statement
        orders.push(createOrder("Luis", i));       // in the memory of the list
    }
    println("${orders.length} orders");
    return 0;
}
```

Output:
```
Ana #0: 0
Ana #1: 10
Ana #2: 20
3 orders
```

A program that runs for a long time (a server, a loop that processes files) accumulates nothing:
what belongs to each turn is freed on each turn.

### What a function returns

A function that returns something **it created** creates it directly in the caller's memory, without
copying it. The caller decides where, almost always without writing it: `let` puts it in its block,
`push` in the list, an assignment to a field in the object, a `return` in the memory of *its* call.
To say it explicitly, the call has `in`, like any other value:

```actionscript
let report: String = summary(data);
```

- The variables that the function returns are also created in the caller's memory:

```actionscript
function parts(text: String): String[*] {
    let out: String[*] = [];          // it is returned: it lives where the caller says
    for (p in text.split(",")) { out.push(p.trim()); }
    return out;
}
```

- If the function returns something **that already existed** (an element of a list, a field, a
  parameter or a part of one), it creates nothing: the result keeps living where it was. A
  `find(name)` that searches a global list returns an object that lives the whole program.
- The arguments that are only used during the call are temporaries of the statement. The ones that
  can end up in the result (like the text that `trim()` cuts) are created where the result goes.

### The default memory: `in default`

There is a memory that lives the whole program: the **default memory**. Nothing ends up there
without it being seen in the code: it is used only when asked for with `in default`.

- The initial values of global variables are created there on their own.
- Giving a global a **new** value asks for it: `config = load(path) in default;`. If it is missing,
  the error says so: `This value lives in the memory of this block, but 'config' lives for the whole program: create it with 'in default'.`
- A parameter `p: T in default` (see [section 17](#17-the-lifetime-rule-and-clone)) receives its
  argument created there, without writing anything else in the call.

### Memories of your own

When it is better to decide it yourself (to let go of something big earlier, to group what belongs
to a task), memories are created. A memory is a block of bytes, `byte[...]`:

```actionscript
let a: byte[4096] = [];             // 4 KB on the stack (or static, if it is global)
let b: byte[1024] = [] in heap;     // a block asked from the system
let c: byte[*] = [] in heap;        // it grows by asking the system for more blocks
```

- **`in heap`** asks the operating system for the memory. With `byte[N]`, the size can depend on a variable.
- Without `in heap`, the block is on the stack (inside a function) or is static memory (if it is global).
  A local memory without heap is limited to 64 KB.
- `byte[*]` (which grows) always needs `in heap`.

And they are used with `in`:

```actionscript
let text: String = "hello ${name}" in c;
let pet: Animal = Animal { name: "Kitty" } in c;
let numbers: int32[*] = [] in c;
let order: Order = createOrder("Ana", 3) in c;    // the result of a call, too
let short: String = "id ${n}" in byte[64];        // a temporary buffer of the current block
```

| Where | How long it lives |
|---|---|
| without `in` | where it belongs (see [Automatic memories](#automatic-memories)) |
| `in m`, with `m` local | until the end of the block where `m` was declared |
| `in m`, with `m` global | the whole program |
| `in byte[N]` | until the end of the current block; a text that does not fit is cut |
| `in default` | the whole program |

Also:
- A block `{ ... }` inside a function has its own memory: what is created in it is freed when it closes.
- A memory is freed **on every exit** of its block: when it ends, with `return`, `break`,
  `continue` or when an error leaves it.
- Memories are queried with `m.length` (bytes used), `m.capacity` and `m.peak` (maximum used).
- A function can also receive a memory as a parameter (`m: byte[*]`) and create things there. It is
  rarely needed: it is enough for the caller to write `f(x) in m`.

### When to use each one

- **Almost always**: none; the automatic memories already free each thing when it is no longer used.
- **Data for the whole program** (configuration, caches): `in default`, or a global memory.
- **Controlling when something big is freed**: a memory of your own `in heap`, or a block `{ }`.
- **Small, short-lived values**: a buffer `in byte[N]`.

### Restrictions

- A memory is not a value: it is not assigned, not returned and not kept in fields.
  It is used after `in`, passed to parameters and queried.
- A `byte[N]` used as a memory cannot be used at the same time as bytes of data.
- Lambdas can only use global memories or memories created inside them.

---

## 17. The lifetime rule and `clone()`

The compiler guarantees that **nothing points to memory that was already freed**, with one rule:

> A value cannot be kept in a place that lives longer than the memory where it was created.

For example:

```actionscript
class Card { let name: String = ""; }

function rename(c: Card): void {
    let draft: byte[*] = [] in heap;
    let fresh: String = "temporary ${1}" in draft;
    c.name = fresh;          // ERROR: 'draft' is freed on the way out and c.name would point there
}
```

The error says:

```
This value lives in memory 'draft', but field 'name' lives longer (in 'c' (owned by the caller)). Use .clone() to copy it there.
```

And the solution is the one it suggests: **`clone()`**, which copies the value to the place of the destination.

```actionscript
c.name = fresh.clone();      // fine: it is copied to c's memory
```

### `clone()`

- It creates a **complete, independent copy**: an object with everything it contains, a list with its
  elements, a text. If there are cycles between objects, the copy respects them.
- The copy goes to the place of the destination (the memory of an object, of a list, of the block) or
  to where you say with `in`: `let p: Person = ana.clone() in otherMemory;`.
- It exists for every type. In the ones that have no memory (numbers, simple structs) it is the same as assigning.
- It is not available for interfaces, lambdas or `T[]` parameters.

### Where the rule applies

- When assigning a variable, a field or an element.
- When creating an object or a list: its fields and elements must live at least as long as it does.
- When returning: the value cannot come from a memory of the function (an `in m` with `m` local, a
  `byte[N]` buffer). What is created in the `return`, or in a variable that is returned, lives where
  the caller says, so there is nothing to check.
- When keeping it in a global variable: only values that live the whole program (create them with `in default`).
- A parameter that receives data from the caller cannot be kept in another object that also comes
  from the caller without `clone()`, because the compiler does not know which of the two lives longer.
  It is the typical case:

```actionscript
class Contact {
    let name: String = "";
    function setName(n: String): void {
        self.name = n.clone();       // without clone() it is an error
    }
}
```

- For variables that are reassigned, the compiler considers every value they receive (in loops too).
  This pattern is valid:

```actionscript
let last: Animal? = null;
for (a in animals) { last = a; }
```

### Saying where a parameter lives: `in`

When a function **does** have to keep a parameter in another one (building a tree, filling a table),
the parameter can say where its data lives, just as `in` says where something is created:

| Parameter | Means | The caller must pass |
|---|---|---|
| `k: Node in p` | lives as long as the parameter `p` | something that lives at least as long as what it passes in `p` |
| `s: String in default` | lives the whole program | what is created in the call goes there on its own; if it already existed, something global, a literal or `in default` |
| `x: Item in self` | (in a method) lives as long as the object | something that lives as long as the object |
| `t: String in m` | lives in the memory `m` (a `byte[*]` parameter) | something that lives as long as that memory |

Inside the function, that parameter can be kept there without `clone()`. The compiler checks it in
each call:

```actionscript
class Node {
    let name: String;
    let kids: Node[*] = [];
}

let names: String[*] = [] in default;

function addKid(parent: Node, kid: Node in parent): void {
    parent.kids.push(kid);                 // fine: kid lives as long as parent
}

function remember(name: String in default): void {
    names.push(name);                      // fine: name lives the whole program
}

function main(): int32 {
    let memory: byte[*] = [] in heap;
    let root: Node = Node { name: "root" } in memory;
    addKid(root, Node { name: "a" } in memory);
    addKid(root, Node { name: "b" } in memory);
    remember("first");
    println("${root.kids.length} ${root.kids[1].name} ${names.length}");
    return 0;
}
```

Output: `2 b 1`

If in the call the value lives less (for example, a node created in a `scratch` memory of a loop,
which is freed on each turn), the error says so:
`Argument 2 of 'addKid' ('kid: Node in parent') must live as long as argument 1 (memory 'memory'), but it lives in memory 'scratch'.`
And when the `in` is missing, the error message suggests it: `... or declare the parameter as 'kid: Node in parent'`.

- `in` only makes sense in parameters that point to memory (objects, lists, texts).
- A method that redefines another (`override`) or implements an interface must repeat the same `in`.
- `extern` functions do not use it.

---

## 18. Lambdas and closures

A lambda is a function without a name that is kept in a variable or passed as an argument.
Its type is written with the parameters and the result:

```actionscript
let double: (int32) -> int32 = (x) -> { return x * 2; };
let add: (int32, int32) -> int32 = (a: int32, b: int32) -> { return a + b; };
let warn: () -> void = () -> { println("warning"); };
```

The type of the parameters can be left out when it is deduced from the context.

### Captures

A lambda can use variables from around it. It **copies** them at the moment it is created
(objects are copied as a reference: the lambda sees the same object).

```actionscript
function makeAdder(base: int32): (int32) -> int32 {
    return (x) -> { return x + base; };
}

class Counter {
    let value: int32 = 0;
    function incrementer(): () -> int32 {
        return () -> { self.value += 1; return self.value; };
    }
}

function main(): int32 {
    let plus10: (int32) -> int32 = makeAdder(10);
    println("${plus10(5)}");

    let c: Counter = Counter {};
    let inc: () -> int32 = c.incrementer();
    inc();
    inc();
    println("${inc()} ${c.value}");
    return 0;
}
```

Output:
```
15
3 3
```

**Rule:** a captured variable **cannot be reassigned or modified**, neither before nor after the
lambda, nor inside it. That way the copy never gets out of date:

```actionscript
let x: int32 = 5;
let f: () -> int32 = () -> { return x; };
x = 10;     // error: 'x' is captured
```

The same goes for changing a field of a captured struct or adding to a captured `T[N]`. Class objects
and `T[*]` lists can be modified, because the lambda shares the same reference.

### Other rules

- A lambda can be returned or kept in fields without a problem: it carries its copies with it.
- In class methods, a lambda can use `self`. In struct methods it cannot, because the struct could be copied or disappear.
- Lambdas cannot throw errors.
- A lambda cannot capture another lambda **of its own type** (the compiler detects it).

---

## 19. Errors: `throw`, `try` and `catch`

Expected errors (a file that does not exist, an invalid read) are represented with enums:

```actionscript
enum FileError {
    NotFound,
    Denied(user: String),
    Full(bytes: int64)
}

function open(path: String): int32 throws FileError {
    if (path == "") { throw FileError.NotFound; }
    if (path == "secret") { throw FileError.Denied { user: "ana" }; }
    return path.length;
}

function readBoth(a: String, b: String): int32 throws FileError {
    return open(a) + open(b);        // if open fails, the error keeps going up
}

function main(): int32 {
    let attempts: String[] = ["hello", "", "secret"];
    for (p in attempts) {
        try {
            println("read ${readBoth("data", p)}");
        } catch (FileError e) {
            switch (e) {
                case NotFound -> println("not found");
                case Denied { user } -> println("denied for ${user}");
                case Full { bytes } -> println("full: ${bytes}");
            }
        }
    }
    return 0;
}
```

Output:
```
read 9
not found
denied for ana
```

The rules:
- **`throws E`** declares the enum that the function can throw (one per function).
- Each call to a function that can fail must be inside a `try` that catches that type, or in a
  function that declares the same `throws` (then the error goes up on its own). Otherwise, it is a
  compile error.
- A `try` can have several `catch`, one per error type. What is not caught keeps going up.
- Methods of classes and interfaces can also declare `throws`; an `override` must declare the same.
- The data that travels in an error must live the whole program: use literals or `.clone()`.
- If `main` declares `throws` and an error reaches it, the program ends with code 1 and the message
  `uncaught error: FileError.NotFound`.

Inside, an error is a value that is returned: there are no hidden jumps, and local memories are freed
while the error goes up.

---

## 20. Failures at run time

Some failures cannot be foreseen when compiling. Instead of corrupting memory, the program stops with
a message that says the file and the line, and the exit code **101**:

| Cause | Message |
|---|---|
| index out of range | `panic [src/main.lar:4]: index 5 out of range (length 3)` |
| division by zero | `panic [src/main.lar:4]: division by zero` |
| `!` on `null` | `panic [src/main.lar:4]: '!' used on a null value` |
| a fixed-size memory fills up when creating something | `panic [src/main.lar:4]: memory is full` |
| the system gives no more memory | `panic: out of memory: ...` |

These failures are not caught with `catch`: they mean an error in the program, not an expected situation.

The program can also stop like this on purpose, with **`panic("message")`**, when it finds something
that should never happen:

```actionscript
function name(n: int32): String {
    if (n == 1) { return "one"; }
    panic("I cannot say ${n}");
}
```

Output, if it is called with 7: `panic [src/main.lar:3]: I cannot say 7`, with exit code 101.

- `panic` receives a `String` (it can be an interpolated text).
- A function can end with `panic(...)` instead of `return`: the compiler knows it does not go on.
- It is for errors in the program. What is expected to possibly fail (a file that does not exist,
  badly written data) is reported with `throw`, which the caller can catch.

---

## 21. `Any`: free-form data

Structs and classes are for data whose shape you know in advance. For data whose shape you do not
know (configuration, messages, JSON) there is **`Any`**: a value that can be a number, a `bool`, a
`String`, `null`, an object, a struct, an enum or a **table**. A table has, as in Lua, two parts: one
**by position** (0, 1, 2…) and another **by name**.

```actionscript
function main(): int32 {
    let config: Any = {
        "web", "api",                  // positions 0 and 1
        name: "server",                // by name
        port: 8080,
        limits: { max: 100, ratio: 0.75 },
    };

    println("${config[0]} ${config.name} ${config.limits.max}");
    config.port = 9090;                // change an entry
    config["debug"] = true;            // add an entry (also with a computed String)
    config.push("admin");              // add at the end of the part by position
    println("${config}");
    return 0;
}
```

Output:
```
web server 100
{"web", "api", "admin", name: "server", port: 9090, limits: {max: 100, ratio: 0.75}, debug: true}
```

- **A table lives in a memory**, like an object: the one of its variable, or the one you say with `in`.
  The tables inside another one, and the ones assigned or added to a table, live in the memory of that table.
- **Values carry their type.** An integer without a type is kept as `int64` and a decimal as `float64`;
  for another type, say it: `0xFF as byte`, `1.5 as float32`.
- A table keeps numbers, `bool`, `String`, `null`, other tables, objects, structs and enums
  (see below). `[*]` lists, lambdas and interfaces do not: that is what typed fields are for.
- **Reading never fails**: an entry that does not exist, or reading inside something that is not a
  table, gives `null`. That is why `config.server.port` works even if `server` is missing. Writing to
  something that is not a table, on the other hand, stops the program.
- The entries by name are gone over in the order in which they were added.
- `a.length` is the size of the part by position. For an entry called `length`, `push` or `fields`,
  use brackets: `a["length"]`.

### Reading a value: `as`

Since the type of what is inside is not known when compiling, reading a value with a type gives an
**optional**: the value if there is one and it is of that type, or `null`. It is combined with `??`:

```actionscript
function main(): int32 {
    let config: Any = { port: 8080, ratio: 0.75, name: "web" };
    let port: int32 = config.port as int32 ?? 80;         // 8080: an integer that fits is converted
    let small: byte = config.port as byte ?? 0;           // 0: 8080 does not fit in a byte
    let ratio: float64 = config.ratio as float64 ?? 1.0;
    let timeout: int32 = config.server.timeout as int32 ?? 30;   // it does not exist: 30
    let name: String = config.name as String ?? "?";
    println("${port} ${small} ${ratio} ${timeout} ${name} ${config.missing == null}");
    return 0;
}
```

Output: `8080 0 0.75 30 web true`

Integers are converted to any integer type they fit in, and numbers to decimal. `as` also works with
classes, structs and enums: `v as Dog` gives a `Dog?`.

### Going over and telling apart

`for (i, v in table)` goes over the part by position and `for (name, v in table.fields)` the part by
name. To know what each value holds, a `switch` with the type is used; `case Any t` is a table:

```actionscript
function describe(v: Any): String {
    return switch (v) {
        case int64 n when n > 1000 -> "big number ${n}";
        case int64 n -> "number ${n}";
        case float64 f -> "decimal ${f}";
        case String s -> "text '${s}'";
        case Any t -> "table of ${t.length}";
        case null -> "nothing";
        default -> "something else";
    };
}

function main(): int32 {
    let packet: Any = { 3, 2.5, "three", { 1, 2 }, name: "sensor", port: 8080 };
    for (i, v in packet) { println("${i}: ${describe(v)}"); }
    for (name, v in packet.fields) { println("${name}: ${describe(v)}"); }
    return 0;
}
```

Output:
```
0: number 3
1: decimal 2.5
2: text 'three'
3: table of 2
name: text 'sensor'
port: big number 8080
```

- The `switch` on an `Any` compares the exact type: `8080` is kept as `int64`, so `case int32` does
  not cover it. Used as an expression, it needs `default`.
- While a table is gone over its values can be changed, but entries cannot be added or removed: if
  it happens, the program stops with a message.
- `clone()` copies a table with everything it contains, also if it contains itself.

### Objects, structs and enums

An `Any` also keeps objects, structs and enums, and they are recovered with their type:

- **an object is kept by reference**: the table and the variable point to the same object;
- **a struct or an enum is kept copied** in the memory of the table. Outside a table, the copy goes
  to the memory of the variable (or where you say with `in`): `let v: Any = point;`.

```actionscript
struct Point { let x: int32; let y: int32; }
class Animal { let name: String; }
class Dog extends Animal { let breed: String = "mixed"; }

function main(): int32 {
    let rex: Dog = { name: "Rex", breed: "shepherd" };
    let p: Point = { x: 1, y: 2 };
    let things: Any = { 42, p, rex, null };

    for (v in things) {
        let text: String = switch (v) {
            case int64 n -> "number ${n}";
            case Point q -> "point ${q.x},${q.y}";
            case Animal a -> "animal ${a.name}";      // a Dog is also an Animal
            case null -> "null";
            default -> "other";
        };
        println(text);
    }
    let dog: Dog? = things[2] as Dog;
    println("${things} ${dog != null}");
    return 0;
}
```

Output:
```
number 42
point 1,2
animal Rex
null
{42, <Point>, <Dog>, null} true
```

When printed, an object or a struct is shown with the name of its type. `clone()` of a table also
copies the objects it contains, except the ones of `synchronized` classes and the `Thread`s, which
are shared.

### Searching

| Method | What it does |
|---|---|
| `t.contains(x)` | `true` if `x` is the name of an entry, or is equal to an element by position |
| `t.containsKey("name")` | `true` if there is an entry with that name |

`contains` searches numbers (by value: `5` is equal to `5.0`), `bool`, `String`, objects (the same
object) and `null`. It does not look at the values of the entries with a name: those are gone over
with `fields`. Used with names, an `Any` is a set:

```actionscript
function main(): int32 {
    let seen: Any = {};
    let words: String[] = ["x", "y", "x"];
    for (w in words) {
        if (seen.contains(w)) { println("again: ${w}"); }
        seen[w] = true;
    }
    return 0;
}
```

Output: `again: x`

### Removing entries

| Method | What it does |
|---|---|
| `t.remove("name")` | removes an entry by name; gives `true` if it existed |
| `t.removeAt(i)` | removes a position; the following ones move back |
| `t.clear()` | empties the table |
| `t.removeIf((v) -> ...)` | removes, from both parts, the values for which the lambda gives `true`; returns how many |
| `t.removeIf((name, v) -> ...)` | the same with the part by name, also receiving the name |

```actionscript
function main(): int32 {
    let config: Any = { 1, null, 3, name: "x", debug: null, port: 80 };
    config.remove("name");
    config.removeAt(0);
    let removed: int32 = config.removeIf((v) -> { return v == null; });
    println("${removed} ${config}");
    return 0;
}
```

Output: `2 {3, port: 80}`

Removing entries while going over the same table stops the program, just like adding them: the walk
would skip entries. To remove several, `removeIf` does it at once. Removing does not free memory:
what lives in a memory is freed together, when the memory is freed.

---

## 22. Threads

A thread runs code at the same time as the rest of the program. In Larimar, a **`Thread`** is an
object that lives in a memory, and what it runs (its `run`) is a lambda written right there:

```actionscript
let worker: Thread = { run: () -> { println("working"); } };
worker.start();       // it starts running
worker.join();        // it waits for it to end
```

- **When the memory of a thread is freed, it first waits for it to end.** So a thread never lives
  longer than its memory, and everything it uses keeps existing while it runs. Threads in the default
  memory are waited for when the program ends.
- `start()` starts the thread (only once) and `join()` waits for it to end.

### Sharing data: `synchronized class`

Two threads that change the same thing at the same time corrupt the data. That is why a thread **can
only use** two kinds of things from outside, and the compiler checks it:

1. **Values**, which the thread receives copied: numbers, `bool`, `String`, and structs, enums and `T[N]` made of them.
2. **Objects of a `synchronized class`.**

A `synchronized` class protects its data with a lock. Each method takes it when it starts and lets it
go when it leaves, by any path, so two threads are never inside the same object at the same time:

```actionscript
synchronized class Counter {
    let total: int64 = 0;
    function add(n: int64): void { self.total += n; }
    function get(): int64 { return self.total; }
}

function main(): int32 {
    let shared: byte[*] = [] in heap;
    let counter: Counter = {} in shared;
    {
        let workers: byte[*] = [] in heap;     // the threads live here (in the memory of the turn,
                                               // each one would be waited for at the end of its turn)
        for (w in 0..4) {
            let t: Thread = {
                run: () -> {
                    for (k in 0..1000) { counter.add(k as int64); }
                }
            } in workers;
            t.start();
        }
    }   // when 'workers' is freed, the 4 threads are waited for
    println("${counter.get()}");
    return 0;
}
```

Output: `1998000`

The four threads run at the same time because their memory is outside the loop. The block `{ }` says
how far they go: when it closes, `workers` is freed and, with it, the threads are waited for.

The rules of a `synchronized` class:
- Its fields are only used inside its methods, through `self`.
- Its methods receive and return values or `synchronized` objects, never lists, plain objects or `Any`:
  so its data does not leave without the lock.
- It does not inherit and is not inherited, and inside its methods `self` is not used in lambdas
  (they could run without the lock).
- A method can call another one of the same object: the lock can be taken several times.

### Waiting for something to happen: `wait until`

A method of a `synchronized` class can say **when** it can run, with `wait until (condition)` in its
signature. Whoever calls it **waits there** (without using the processor and letting go of the lock
in the meantime) until the condition holds, and then the method runs with the lock taken:

```actionscript
synchronized class Queue {
    let items: int32[64] = [];
    let closed: bool = false;

    function put(v: int32): void { self.items.push(v); }
    function close(): void { self.closed = true; }

    function take(): int32 wait until (self.items.length > 0 || self.closed) {
        if (self.items.length == 0) { return -1; }        // closed and empty
        let v: int32 = self.items[0];
        let rest: int32[64] = [];
        for (i in 1..self.items.length) { rest.push(self.items[i]); }
        self.items = rest;
        return v;
    }
}

synchronized class Total {
    let sum: int64 = 0;
    function add(n: int64): void { self.sum += n; }
    function get(): int64 { return self.sum; }
}

function main(): int32 {
    let queue: Queue = {};
    let total: Total = {};
    let consumer: Thread = {
        run: () -> {
            while (true) {
                let v: int32 = queue.take();             // it waits until there is something
                if (v < 0) { break; }
                total.add(v as int64);
            }
        }
    };
    consumer.start();
    for (i in 1..11) { queue.put(i); }
    queue.close();
    consumer.join();
    println("sum ${total.get()}");
    return 0;
}
```

Output: `sum 55`

- **It is read in the signature:** "take waits until there is something or it is closed". Whoever
  reads the method knows that the call can stay waiting.
- **Nobody notifies by hand.** When any method of the object ends (`put`, `close`...), the ones
  waiting look at their condition again. There is no `notify` to forget.
- **The body starts knowing that the condition holds**, with the lock taken: nothing changes it before
  the first line.
- **The condition can use the parameters**: `function serve(ticket: int32): int32 wait until (self.now >=
  ticket)` lets each one through on its turn.
- **Only in methods of a `synchronized` class**, because they are the only changes the object can see.
- **It is written in two words**, like `released by`: the clauses that describe a declaration read
  like a phrase. The keywords that start something go in a single piece (`c_include`, `c_code`).
- **Several conditions at once:** a queue with a limited capacity puts `wait until (self.items.length < 4)`
  on `put` and `wait until (self.items.length > 0)` on `take`, and each side waits for its own.

### An object as the work: `Runnable`

Instead of a lambda, `run` can be a `synchronized` object that implements `Runnable`
(`interface Runnable { function run(): void; }`):

```actionscript
synchronized class Download implements Runnable {
    let done: bool = false;
    function run(): void { self.done = true; }
    function finished(): bool { return self.done; }
}

function main(): int32 {
    let job: Download = {};
    let t: Thread = { run: job, name: "download" };
    t.start();
    t.join();
    println("${job.finished()}");
    return 0;
}
```

Output: `true`

### Functions for several threads: `thread safe`

A function that other threads will call, sometimes several at the same time, is marked with
**`thread safe`** at the end of its type. Whoever designs the API (a server, a pool of threads)
writes it; whoever uses it writes a normal lambda:

```actionscript
class Pool {
    let threads: int32 = 4;
    let work: (int32) -> void thread safe;        // the Pool's threads call it at the same time
    ...
}

let total: Total = {};                             // synchronized
let names: String[*] = [];

let pool: Pool = { work: (id: int32) -> { total.add(id as int64); } };     // fine
let bad: Pool = { work: (id: int32) -> { names.push("x"); } };              // error
```

```
Semantic Error [src/main.lar:9]: This 'thread safe' lambda uses 'names' (String[*]), which other threads could change at the same time. ...
```

- **A lambda given where a `thread safe` function is expected is checked like the `run` of a `Thread`**:
  it only uses values, objects of `synchronized` classes and other `thread safe` functions, and the
  functions it calls do not change globals. Its captures do not change (as in every lambda), so
  several threads can run it at the same time.
- **A `thread safe` value can be shared between threads**: a `Thread` can use it and a `synchronized`
  method can receive it. That is how the servers of `std.net` are written in plain Larimar.
- **A `thread safe` function works where a plain one is expected**, but not the other way around: a
  variable with a plain lambda cannot be given where `thread safe` is asked for (only a lambda written
  there, which is checked).
- It is two words, like `wait until`, and neither is reserved. With a function type inside another,
  it goes to the nearest one on its left: in `(A) -> (B) -> C thread safe` it is `(B) -> C`; for the
  outer one, parentheses: `((A) -> (B) -> C) thread safe`.

`synchronized` and `thread safe` are different things: a `synchronized` class is an object with a
lock; a `thread safe` function needs no lock because it only touches things that are already safe.

### What the compiler rejects

```actionscript
let hits: int32 = 0;
class Box { let n: int32 = 0; }

function main(): int32 {
    let box: Box = {};
    let t: Thread = { run: () -> { box.n = 1; hits += 1; } };
    t.start();
    return 0;
}
```

```
Semantic Error [src/main.lar:7]: This thread uses 'box' (Box), which could change while the thread runs. A thread can share only values ...
Semantic Error [src/main.lar:7]: This thread can reach global 'hits' (src/main.lar:7), which can change while threads use it. Keep shared state in an object of a synchronized class.
```

The check follows the functions the thread calls: if any of them, however deep, changes a global
variable or uses a global memory, the error says so. Globals that never change (a configuration, a
text) can be read.

Between threads only **the default memory** is shared, and it has its own lock: creating something
`in default` from several threads is safe. The other memories belong to a single thread.

What this does **not** prevent are deadlocks: two `synchronized` objects that call each other in
opposite order can stay waiting forever. No language with locks prevents it completely.

Inside, Larimar uses the threads of the system: POSIX (`pthread`) on Linux and macOS, and the Windows
API on Windows. `larimar build` adds what is needed to compile.

---

## 23. Calling C

```actionscript
c_include "<stdio.h>";
c_include "<math.h>";

extern function printf(format: String, ...): int32;
extern function sqrt(x: float64): float64;

function main(): int32 {
    printf("square root of 2 = %f\n", sqrt(2.0));
    return 0;
}
```

Output: `square root of 2 = 1.414214`

With `<math.h>`, on some systems the math library has to be linked: `libraries = ["m"]` in the
`larimar.toml`.

A library of your own is declared the same way. For example, for one of windows:

```actionscript
c_include "windows_lib.h";

extern type Window;                                      // an opaque C pointer
extern function create_window(title: String): Window;
extern function close_window(w: Window): void;
```

- `c_include` adds an `#include` to the generated C (inside `#when unix` ... `#end`, only on that
  system: see [Each system its own: `#when`](#each-system-its-own-when)).
- `extern function` declares a C function. Its parameters can only be numbers, `bool`, `String`
  (it arrives as `const char*`), `extern` types (optional ones too, `T?`, which in C are a pointer that
  can be `NULL`), C structs and C pointers (`T*`, see [C pointers](#c-pointers-t-and-)). `...` allows
  variable arguments, as in `printf`.
- A C function can return `String?`: `NULL` arrives as `null` (`getenv`).
- If the C name clashes with a Larimar one, the function is declared with another name and the C one
  is given: `extern function cExit(code: int32): void = c "exit";`.
- A **`T[]` of numbers or `bool`** (`byte[]`, `int32[]`, `float64[]`...) arrives in C as **two
  arguments**: a pointer to the elements and how many there are. C can read them and write to them, so
  it is the way for C to fill a Larimar buffer (reading from a file or a socket) without copying anything:

  ```actionscript
  c_code {
      static int32_t fill(uint8_t* items, int32_t length) { /* writes to items[0..length) */ return length; }
  }
  extern function fill(buffer: byte[]): int32;      // in C: fill(uint8_t* items, int32_t length)

  let buf: byte[*] = buffer(4096);
  let n: int32 = fill(buf);                          // a list, a T[N] or a T[] work
  ```
- If the file has no `c_include`, the transpiler writes the C prototype of each `extern function`
  itself. That is what is needed for functions of your own written in a separate `.c` (see `sources`
  in [section 26](#26-projects-larimartoml-and-larimar-build)). If the function comes from a header,
  include the header.
- An external function that returns `String` must return a zero-terminated text that keeps existing:
  a static one, or one created in a memory it receives (see below).
- `extern type` declares a type that comes from C: opaque, a concrete C type, a C struct or a pointer
  to a function (see [C types](#c-types-extern-type) below).
- In `std.lang`, `native type` declares methods of a primitive type of the language. A `native function`
  without a body declares an intrinsic operation; with `= expression;` it defines the method using a
  Larimar expression, often an `extern` call. In a class you can also write `native function ... = expression;`.
- `native operator []` declares the intrinsic indexing. `in self` in the return says that the returned
  value is a view tied to the life of the receiver. The initializers of class fields are evaluated for
  each object, inside the memory of that object.
- In a module, the C name does not change: `public extern function Beep(...)` in the module `win` is
  used as `win.Beep(...)` and calls C's `Beep`.

### C in the same file: `c_code`

Almost everything from C is used directly, with declarations: functions, constants, variables,
structs, pointers and resources (the following sections). For what is still better written in C (an
algorithm, a library with callbacks, an Apple block), a C function is written inside the file itself
and declared with `extern function`:

```actionscript
c_code {
    #include <ctype.h>

    static int32_t sum_digits(int64_t v) {
        int32_t s = 0;
        if (v < 0) v = -v;
        while (v > 0) { s += (int32_t)(v % 10); v /= 10; }
        return s;
    }
}

extern function sum_digits(v: int64): int32;

function main(): int32 {
    println("${sum_digits(98765)}");
    return 0;
}
```

Output: `35`

For example, the API of a primitive type can mix intrinsics, methods implemented in Larimar and C calls:

```actionscript
public native type String {
    native function length(): int32;
    native operator [](i: int32): byte;
    native function substring(from: int32, to: int32): String in self;
    function isEmpty(): bool { return self.length() == 0; }
}
```

A native function with an implementation delegates to a Larimar expression; that expression can call a C function:

```actionscript
public class StringBuilder {
    let buffer: TextBuf = text_buf_new();
    native function add(text: String): void = text_buf_add(self.buffer, text);
    native function toString(): String in self = text_buf_view(self.buffer);
}
```

`native type` can only name primitive types the compiler already knows. From the `c_code` blocks of the
standard library only what is used reaches the C: each C function, type or variable stays if something
the program uses names it. The program's own `c_code`, on the other hand, is copied whole.

That is how `String` is written: the compiler only knows its core (`length`, `[]`, `substring`,
`bytes`, `split` and `lines`, which are views of the text), and everything else (`indexOf`, `replace`,
`toUpperCase`, `padStart`, `toInt`, `codePoints`...) is written in Larimar in `std/lang.lar`, with a
small `c_code` only for what needs C (`strtod`, for `toFloat`).

- The content is copied as it is to the generated C, after the headers and before the program.
- **The doors between the two languages are `extern function` (from C to Larimar) and `export function`
  (from Larimar to C)**, with their types checked. The C must not use the variables or the types that
  Larimar generates, because their names can change.
- Inside `c_code` there are no guarantees: the C can do anything. It is best kept small and simple.
- If the file has `c_code`, Larimar writes no prototypes for its `extern function`s: the block is
  assumed to define or include them.

### Passing a memory to C

A C function can receive a Larimar memory (`m: byte[*]` in the declaration) and create things in it.
When **the memory is its first parameter**, the call does not write it: C receives the memory of the
call, the same one a Larimar function would receive, so what it returns lives where the caller says
(its block, the list it is added to, or the memory written with `in`). It is the right way for C to
return text:

```actionscript
c_code {
    #include <ctype.h>

    static const char* shout(RtMem* m, const char* text) {
        size_t n = strlen(text);
        char* out = (char*)rt_mem_alloc(m, n + 2, 0);     /* zeroed memory: the text ends by itself */
        for (size_t i = 0; i < n; i++) out[i] = (char)toupper((unsigned char)text[i]);
        out[n] = '!';
        return out;
    }
}

extern function shout(m: byte[*], text: String): String;

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

In C, a memory arrives as `RtMem*`, and `rt_mem_alloc(m, bytes, 0)` reserves space inside it (with the
bytes set to zero). That is the whole interface the C needs to know. The rule is one: **the C uses the
memory only during the call**. If it kept the pointer for later, the memory could be freed before.
A memory in another parameter (not the first) is passed written, like any argument.

This is how the Windows example that used to need a separate `.c` file looks:

```actionscript
c_code {
    #include <windows.h>

    static const char* computer_name(RtMem* m) {
        DWORD size = MAX_COMPUTERNAME_LENGTH + 1;
        char* name = (char*)rt_mem_alloc(m, size, 0);
        return GetComputerNameA(name, &size) ? name : "";
    }
}

extern function computer_name(m: byte[*]): String;
```

### C types: `extern type`

Everything that comes from C is declared with `extern type`. After the `=` goes its form:

| Declaration | What it is | In C |
|---|---|---|
| `extern type Handle;` | an opaque pointer: it is received, kept and passed, without looking inside | `void*` |
| `extern type File = c "FILE*";` | a concrete C type, written as it is | `FILE*` |
| `extern type Point = struct { ... };` | a C struct, by value, with the fields that are used | the C struct |
| `extern type Op = (int32, int32) -> int32;` | a pointer to a C function | `int32_t (*)(int32_t, int32_t)` |

```actionscript
c_code {
    #include <stdio.h>

    typedef struct Point { float x, y; } Point;

    static Point point_mid(Point a, Point b) {
        Point m = { (a.x + b.x) / 2, (a.y + b.y) / 2 };
        return m;
    }
    static FILE* log_file(void) { return stderr; }
    static void log_line(FILE* f, const char* text) { fprintf(f, "%s\n", text); }
}

extern type File = c "FILE*";                                      // a concrete C type
extern type Point = struct { let x: float32; let y: float32; };    // a C struct, by value

extern function point_mid(a: Point, b: Point): Point;
extern function log_file(): File;
extern function log_line(f: File, text: String): void;

function main(): int32 {
    let a: Point = { x: 0, y: 0 };
    let b: Point = Point { x: 4, y: 2 };
    let m: Point = point_mid(a, b);
    println("(${m.x}, ${m.y})");
    log_line(log_file(), "listo");
    return 0;
}
```

Output: `(2.0, 1.0)`, and `listo` on the error output.

- **Each `extern type` is a different type in Larimar**, even if in C they are the same: a `File`
  cannot be passed where a `Handle` is expected.
- **`c "..."`** is the exact C type. That way the C compiler also checks the types: with `void*` it
  would not notice that a `FILE*` is passed where the library expects a `sqlite3*`.
- **A C struct** is used like any Larimar struct: literals (`{ x: 1, y: 2 }` or `Point { x: 1 }`),
  fields with a default value, field access, copy by value, lists (`Point[*]`).
  - C provides the definition (the `.h` or the `c_code`); Larimar does not write it. That way the order
    and the alignment of the fields are always C's.
  - It is enough to declare the fields that are used: if the C struct has ten and you care about three,
    you declare three.
  - Its fields can only be numbers, `bool`, `extern` types, pointers (`T*`), other C structs and
    `String`. A `String` field is a C text (`char*` or `char[N]`) that **is read, not assigned**, and it
    is a view of the C text: if C changes it or frees it, the view does too. To keep it, `.clone()`.
  - The fields not given in a literal are zero, as in C: `{ ai_socktype: 1 }`.
  - It has no methods or operators.
  - If the name in C is different, it is written after `struct`: `extern type Rect = struct "struct rect_t" { ... };`.

### C constants and variables: `extern const`, `extern let`

C constants, macros and global variables are used by their name, declaring them with their type:

```actionscript
c_include "<errno.h>";
c_include "<limits.h>";

extern const INT_MAX: int32;                                       // a C macro
extern const ENOENT: int32;
extern const POINTER_SIZE: int32 = c "(int)sizeof(void*)";         // a C expression
extern let errno: int32;                                           // a C variable

function main(): int32 {
    println("${INT_MAX} ${POINTER_SIZE} ${errno == ENOENT}");
    return 0;
}
```

- **`extern const`** does not change; **`extern let`** can be read and assigned (`errno = 0;`).
- Larimar writes the name as it is in the C, so macros, `enum` constants and variables work, and also
  macros that expand into something more complex (`errno`, `stdout`).
- **`= c "..."`** gives a C expression for what has no name: `sizeof`, a cast, a macro with arguments.
- An `extern const` can be a `String` (a text macro); an `extern let` cannot.

### C pointers: `T*` and `&`

Many C functions ask for or return pointers: a linked list (`getaddrinfo`), a result written into a
variable (`accept(fd, &addr, &len)`), a buffer. **`T*`** is a C pointer to a number, to `bool`, to a C
struct, to an `extern` type or to another pointer:

```actionscript
c_code {
    typedef struct Node { int value; struct Node* next; const char* name; } Node;
    static Node nodes[3] = { { 10, &nodes[1], "one" }, { 20, &nodes[2], "two" }, { 30, NULL, "three" } };
    static Node* first_node(void) { return &nodes[0]; }
    static void two_results(int* a, int* b) { *a = 7; *b = 42; }
    static int sum_bytes(const unsigned char* p, int n) { int s = 0; for (int i = 0; i < n; i++) s += p[i]; return s; }
}

extern type Node = struct "Node" {
    let value: int32;
    let next: Node*;
    let name: String;                       // a C text: it is read
};
extern function first_node(): Node*;
extern function two_results(a: int32*, b: int32*): void;
extern function sum_bytes(p: byte*, n: int32): int32;

function main(): int32 {
    let sum: int32 = 0;
    let p: Node* = first_node();
    while (p != null) {                     // a pointer can be null, as in C
        sum += p.value;                     // p.value is p->value
        p = p.next;
    }
    let a: int32 = 0;
    let b: int32 = 0;
    two_results(&a, &b);                    // C writes to a and to b
    let bytes: byte[4] = [1, 2, 3, 4];
    println("${sum} ${a} ${b} ${sum_bytes(bytes, bytes.length)}");
    return 0;
}
```

Output: `60 7 42 10`

- **`p.field`** reads or writes the field of the struct it points to (`p->field` in C). If `p` is
  `null`, the program stops with an error on that line, instead of failing in C.
- **`&x`** gives the address of a variable for C to read or write. **It is only allowed as an argument
  of a C function** (`f(&x)`), so the pointer never lives longer than the call; `x` is a variable whose
  type allows pointers. `&x as Other*` also works there (C sometimes asks for another pointer type).
- **An array where C asks for `T*`** arrives as the pointer to its elements: `fread(buffer, 1, buffer.length, f)`.
- **`as`** converts between pointers (a `sockaddr_in*` as a `sockaddr*`), and between a pointer and an
  opaque `extern` type (`void*`).
- A pointer does not point to Larimar memory (`&x` only exists during the call), so it is not part of
  the lifetime rule: what is on the other side belongs to C, and C says how long it lasts.

### Resources: `released by`

Some things from C have to be let go: a file (`fclose`), a socket (`close`), a window
(`SDL_DestroyWindow`), a database (`sqlite3_close`). It is declared once, in its `extern type`, with
the function that lets it go:

```actionscript
c_include "<stdio.h>";

extern type CFile = c "FILE*" released by fclose;
extern function fopen(path: String, mode: String): CFile?;
extern function fputs(text: String, f: CFile): int32;
extern function fclose(f: CFile): int32;

function main(): int32 {
    for (i in 0..1000) {
        let f: CFile? = fopen("log.txt", "a");
        if (f == null) { return 1; }
        fputs("a line\n", f!);
    }   // each turn: its memory is freed, and with it the file (fclose)
    let g: CFile? = fopen("log.txt", "a");
    release(g);                            // ahead of time, if needed
    return 0;
}
```

- **A resource lives in a memory, like any data**: where what the C function returns is kept (the block
  of a `let`, the object of a field, `in scratch`...). **When that memory is freed, it is let go.** What
  is seen in the code is where it lives, just like with a `String`.
- **`release(x)`** lets it go now. Letting it go twice does nothing; using it afterwards stops the
  program with `a released CFile was used`.
- **The C function that creates it returns `T?`**, because it can fail: a `NULL` pointer (or `-1`, like
  `INVALID_HANDLE_VALUE`) or a negative number (a `-1` descriptor) arrives as `null`.
- **The function that lets it go receives exactly one `T`**, and only `release()` can call it: calling
  it by hand would let it go twice. It can be a C function or a Larimar one (to let go in several steps).
- An object that keeps a resource **cannot be cloned** (it would be let go twice).
- If the function that lets it go exists on a single system (`closedir` on Unix), the resource only exists there.

### Each system its own: `#when`

What changes between systems is written between **`#when`** and **`#end`**, which choose when the C is
compiled (`#if`), not when it runs. They start with `#` so that they look different from the logic of
the program:

```actionscript
c_include "<errno.h>";
#when unix
    c_include "<unistd.h>";
#when windows
    c_include "<winsock2.h>";
    c_include "<ws2tcpip.h>";
#end

#when unix
    extern type Socket = c "int" released by close;
    extern function close(s: Socket): int32;
    extern let errno: int32;
#when windows
    extern type Socket = c "SOCKET" released by closesocket;
    extern function closesocket(s: Socket): int32;
    extern function WSAGetLastError(): int32;
#end

function lastError(): int32 {
    #when windows
        return WSAGetLastError();
    #else
        return errno;
    #end
}
```

- The systems are **`windows`**, **`macos`**, **`linux`** and **`unix`** (all but Windows).
- **Each directive goes alone on its line**: `#when <system>`, `#else` and `#end` (only a comment fits
  after them). One `#when` after another is the next option, like C's `#elif`.
- **No braces and no block.** What is inside belongs to the surrounding block, like the lines of a C
  `#if`. Indentation is not required, but it helps to read it.
- **The `#when`, `#else` and `#end` of the same choice start in the same column.** A `#when` with more
  indentation is nested inside a branch:

  ```actionscript
  #when windows
      return "windows";
  #else
      #when macos
          let what: String = "mac";
      #else
          let what: String = "other unix";
      #end
      return what;
  #end
  ```

- **What every branch declares, with the same type, keeps existing after `#end`**:

  ```actionscript
  #when windows
      let sep: String = "\\";
  #else
      let sep: String = "/";
  #end
  println(sep);              // sep exists here
  ```

  What a single branch declares belongs only to that branch. If the branches do not cover every system
  (without `#else`), nothing they declare remains afterwards: some system would not have it.
- **Outside functions**, inside `#when` only `c_include` and `extern` declarations go, and `#else`
  only follows `#when windows` or `#when unix` (the rest is then the other one).
- **The compiler checks every branch**, so an error in the Windows code is also seen when compiling on
  a Mac. A branch that would never be chosen (`#when macos` after `#when unix`) is an error.
- **What only exists on one system is used inside its `#when`**: calling `closesocket` outside
  `#when windows` is a compiler error (*'closesocket' exists only on windows*).
- **A type can be declared once per system** (`Socket` above), as long as it covers all of them.

That is how the network of the standard library (`std/net.lar`) is written: Unix and Windows sockets,
in plain Larimar. So are the files (`std.io.file`, `std.io.files`), the console and `std.os`.

### Pointers to C functions

`extern type Op = (A, B) -> R;` declares the type of a pointer to a C function. A value of that type is
passed to C, kept and **called like a function**:

```actionscript
c_code {
    typedef int32_t (*op_fn)(int32_t, int32_t);

    static int32_t add(int32_t a, int32_t b) { return a + b; }
    static int32_t apply(op_fn f, int32_t a, int32_t b) { return f(a, b); }
}

extern type Operation = (int32, int32) -> int32;

extern function add(a: int32, b: int32): int32;
extern function apply(f: Operation, a: int32, b: int32): int32;

export function subtract(a: int32, b: int32): int32 {
    return a - b;
}

function main(): int32 {
    println("${apply(add, 10, 3)}");        // a C function
    println("${apply(subtract, 10, 3)}");   // a Larimar function, called from C
    let op: Operation = subtract;
    println("${op(20, 5)}");                // a function pointer is called like a function
    return 0;
}
```

Output:
```
13
7
15
```

- Where an `Operation` is expected, **a function that exists in C with that exact signature** works:
  an `extern function` or an `export function`.
- **A lambda does not work**, because it is not a C function: it carries captures, and C would not know
  what to do with them. If C needs context, almost every library also receives a `void* data`, which is
  declared as an optional extern type (see the next example).
- A plain Larimar function does not work either: the compiler asks to mark it `export`.
- They can also come from C: a C function that returns an `Operation`, or a field of a C struct.
- The allowed types are the ones of `extern function`. A `String` arrives in C as `const char*`, and one
  that C returns is read just like in an `extern function`.

### C calling Larimar: `export function`

`export function` is the opposite of `extern function`: **it brings a Larimar function to C**. The
compiler generates it in C with that same name and with C types, so C can call it, keep it in a pointer
or receive it as a callback:

```actionscript
c_code {
    typedef void (*item_fn)(int32_t index, const char* name, void* data);

    static void for_each_name(item_fn f, void* data) {
        const char* names[] = { "one", "two", "three" };
        for (int32_t i = 0; i < 3; i++) f(i, names[i], data);
    }
}

extern type Data;
extern type ItemHandler = (int32, String, Data?) -> void;

extern function for_each_name(f: ItemHandler, data: Data?): void;

export function show_item(index: int32, name: String, data: Data?): void {
    println("${index}: ${name.toUpperCase()}");
}

function main(): int32 {
    for_each_name(show_item, null);
    return 0;
}
```

Output:
```
0: ONE
1: TWO
2: THREE
```

What `export function` guarantees:

- **The name in C is exactly its own**, also inside a module: `public export function lm_double(...)`
  in the module `gfx.shapes` is still called `lm_double` in C.
- **A clean C signature**: without hidden parameters. Numbers and `bool` as they are, `String` arrives
  as `const char*` (it is converted to Larimar text on the way in), extern types as their C type and C
  structs by value.
- **Each call from C has its own memory**, which is born on the way in and dies on the way back, like
  any function. What the function creates is not left hanging in C.
- **A `c_code` can use it directly**. If its signature only has numbers, `bool`, `String` and opaque
  extern types, the compiler writes its prototype before the `c_code`s. If it uses C structs or
  `c "..."` types, which the `c_code` itself might define, the prototype goes after, and the `c_code`
  that calls it must declare it itself.

And what it does not allow, because C could not handle it:

- returning `String` (C would not know when to free it); return a number, an extern type or a C struct;
- `throws`: an error cannot cross C code, so it is caught inside;
- `in` in the parameters, memories (`byte[*]`), classes, lists or `Any`;
- `main`.

If the library calls the function from another thread, the compiler cannot know it: Larimar's thread
rules do not protect it, just as happens inside a `c_code`.

---

## 24. Modules

A program can be split into several files. **Each file is a module**, and its name comes from its path
inside the folder of the main file:

```
src/
  main.lar            the main file (it has main)
  geo/shapes.lar      the module geo.shapes
  util/text.lar       the module util.text
```

### `public`

What a module declares is **private** unless it has `public` in front. Any declaration with a name can
be marked: functions, constants, global variables, structs, classes, interfaces, enums and `extern`
declarations.

```actionscript
// src/geo/shapes.lar
public const PI: float64 = 3.14159;

public enum Shape { Circle(radius: float64), Rect(width: float64, height: float64), Empty }

function square(x: float64): float64 { return x * x; }     // private

public function area(s: Shape): float64 {
    return switch (s) {
        case Circle { radius } -> PI * square(radius);
        case Rect { width, height } -> width * height;
        case Empty -> 0.0;
    };
}
```

`public` applies to the whole name: in a public class, its fields and methods are seen from outside.
`private` also exists, but it is the same as writing nothing.

### `import`

The `import`s go at the start of the file and have three forms:

```actionscript
import geo.shapes;                   // the names are used with the prefix: shapes.area(s)
import geo.shapes as g;              // with another prefix: g.area(s)
import geo.shapes { Shape, area };   // those names, without a prefix: area(s)
```

With the prefix everything public is reached: functions (`shapes.area(s)`), constants (`shapes.PI`),
types (`let s: shapes.Shape`, `shapes.Figure { ... }`, `class Wheel extends shapes.Figure`,
`catch (shapes.ShapeError e)`) and variants (`shapes.Shape.Circle { radius: 1.0 }`).

```actionscript
import geo.shapes;
import geo.shapes { Shape };

function main(): int32 {
    let s: Shape = Shape.Circle { radius: 2.0 };
    println("area ${shapes.area(s)}, pi ${shapes.PI}");
    return 0;
}
```

Output: `area 12.56636, pi 3.14159`

### Rules

- A local variable can be named like a module or like one of its names; inside its block, the local wins.
- Two modules can have equal names without conflict: `geo.shapes.square` and `util.text.square` are different.
- Modules can import each other in a circle (`a` imports `b` and `b` imports `a`).
- Global variables are initialized module by module: first the imported ones, the main file last.
- **Modules do not see the main file.** Nobody can import it; what is shared goes in a module.
- The same file is loaded only once, even if several modules import it.
- Names cannot contain `__` (a double underscore): the generated C uses it to separate the module from
  the name (`geo__shapes__area`).

The errors say which file they are in:

```
Module Error [src/main.lar:2]: 'square' is private to module 'geo.shapes'; mark it 'public' there to use it here.
Semantic Error [src/geo/shapes.lar:14]: Initializer of 'x': expected int32 but got String.
```

And so do the failures at run time: `panic [src/geo/shapes.lar:9]: index 5 out of range (length 3)`.

---

## 25. Standard library

The standard library is a set of modules that come with Larimar and are imported like any other:
`import std.os;`. They are written in Larimar, with a little C (`c_code`) to talk to the operating
system, and they live in the `std/` folder next to the tool (or in `$LARIMAR_HOME/std`). Only what is
imported goes into the program, and the executable does not need the `std` folder to work.

| Module | What for |
|---|---|
| `std.lang` | types and methods available in every program (`String`, `Any`, `Thread`, `StringBuilder`); seen without importing it |
| `std.io.files` | files and folders all at once, like Java's `Files` |
| `std.io.file` | an open file (`File`), to read it line by line or write it in parts |
| `std.io.streams` | `InputStream` and `OutputStream`: reading and writing no matter from where |
| `std.io.console` | the input, the output and the error output |
| `std.path` | paths: folder, name, extension, join, normalize |
| `std.os` | the environment: variables, current folder, running commands |
| `std.text` | classifying bytes (for lexers and parsers) |
| `std.text.regex` | regular expressions: `Regex`, `Match` (written in Larimar, without C libraries) |
| `std.json` | JSON to `Any` and `Any` to JSON |
| `std.net` | TCP, UDP and server TLS: `TcpSocket`, `TcpListener`, `TcpServer`, `UdpSocket`, `UdpServer`, `TlsServer`, `OpenSslProvider`, `StopSignal` |
| `std.net.http` | HTTP/1.1 and `https://` client: `Client`, `Request`; the body as text, JSON or a stream |
| `std.net.http.tls` | `TlsProvider` (the interface for encrypted connections) and `SystemTls` (the system's TLS) |

**`std.lang`** is special: every program sees its names without writing `import`, and only what the
program names (and what that needs) reaches the C. A name of the main file itself hides the one of `std.lang`.

### `std.io.files`: files and folders

It is imported with Java's name: `import std.io.files as Files;`. No function receives memories: what
they return (the text of a file, the names in a folder) lives where the caller says, like what any
function returns (`Files.readString(path) in memory`, if you want to choose). Everything that can fail
throws `IoError` (`NotFound(path)`, `Denied(path)` or `Failed(path)`; `Files.message(e)` says it in text).

| Function | What it does |
|---|---|
| `Files.readString(path): String` | the whole file, as text |
| `Files.writeString(path, text)` | replaces the file (creates it if it does not exist) |
| `Files.appendString(path, text)` | adds at the end |
| `Files.exists(path)`, `isFile(path)`, `isDirectory(path)` | what there is at that path |
| `Files.list(path): String[*]` | the names of what is in a folder |
| `Files.createDirectories(path)` | creates the folder and the missing ones above it |
| `Files.copy(from, to)`, `Files.delete(path)` | copy a file; delete a file or an empty folder |

### `std.io.file`: an open file

`open(path)`, `create(path)` (empties it) and `append(path)` (writes at the end) give a `File`. As a
binary stream it implements `read(buffer: byte[]): int32`, `write(bytes: byte[])`, `flush()` and
`close()`. `read` returns the bytes read and `0` at the end. It also offers `readLine(): String?`,
`readAll()` and `writeText(text)` as text operations. **A `File` closes on its own when the memory
where it lives is freed** (usually, when the block of its variable closes); `close()` closes it earlier.

### `std.io.streams`: reading and writing no matter from where

The minimum, as in Go: bytes that are read, bytes that are written, and something that can be closed.

| Interface | Methods |
|---|---|
| `InputStream` | `read(buffer: byte[]): int32`: fills the buffer from the start and says how many bytes it read; `0` at the end |
| `OutputStream` | `write(bytes: byte[])` (all of them, or it throws `IoError`) and `flush()` |
| `Closeable` | `close()`: lets go ahead of time of what it holds from the system (it lets go anyway when its memory is freed) |

They are implemented by `File`, `TcpSocket`, the body of a `std.net.http` response and the streams of
the console (`Console.input`, `Console.output`, `Console.error`). Also:

| Name | What it is |
|---|---|
| `Reader { from: stream }` | text over any `InputStream`: `readLine(): String?` (cuts at `\n`, removes a `\r` before it), `readAll()`, and bytes with `readInto(buffer, max)`; it is also an `InputStream` |
| `copy(input, output)` | copies everything and does `flush()`; it closes neither |
| `buffer(n)` | `n` zeroed bytes, to give to `read()` |
| `MemoryInputStream { data: text }` | reads a `String` (text or bytes) that is already in memory |
| `MemoryOutputStream {}` | gathers what is written: `toString()`, `toByteArray()` |

A `byte[4096] = []` does not work as a buffer for `read()`: it starts empty (length 0) and `read()`
only fills up to the length of what it receives; that is what `buffer(4096)` is for.

The `Reader` has one buffer for its whole life, and a line is created only once, at its size, where
the caller says. With a memory on the stack, reading a file (or a socket) of any size asks for no
memory in the loop:

```actionscript
while (true) {
    let scratch: byte[4096] = [];
    let line: String? = lines.readLine() in scratch;   // the line lives in scratch, until the end of the turn
    if (line == null) { break; }
    ...
}
```

`readLine()` and `readInto()` can be mixed: what was left in the buffer after a line comes out first
in `readInto()`. That is how protocols with text headers and a binary body, like HTTP, are read.

### `std.io.console`: the console

`import std.io.console as Console;` gives `Console.readLine(): String?` (a line of the standard input),
`Console.printError(text)` (a line on the error output) and three streams: `Console.input` (an
`InputStream`), `Console.output` and `Console.error` (`OutputStream`). For protocols with lengths (like
the one of `larimar lsp`): `Console.read(n)` (exactly `n` bytes, fewer only if the input runs out;
`Console.lastCount()` says how many), `Console.write(text)` (without a line break), `Console.flush()`
and `Console.binaryMode()` (on Windows, so that `\n` is not turned into `\r\n`).

A `wc` (counting lines, words and bytes), which works for a file or for the standard input:

```actionscript
import std.io.files { IoError };
import std.io.file { open };
import std.io.streams { InputStream, Reader };
import std.io.console as Console;

function count(input: InputStream, name: String): void throws IoError {
    let lines: int32 = 0;
    let words: int32 = 0;
    let bytes: int32 = 0;
    let text: Reader = { from: input };
    while (true) {
        let scratch: byte[4096] = [];
        let line: String? = text.readLine() in scratch;   // one line at a time, asking for no memory
        if (line == null) { break; }
        lines += 1;
        bytes += line.length + 1;
        let inWord: bool = false;
        for (b in line) {
            let space: bool = b == ' ' || b == '\t';
            if (!space && !inWord) { words += 1; }
            inWord = !space;
        }
    }
    println("${lines} ${words} ${bytes} ${name}");
}

function main(args: String[]): int32 {
    try {
        if (args.length == 0) {
            count(Console.input, "-");
        } else {
            count(open(args[0]), args[0]);             // the file closes when the statement ends
        }
        return 0;
    } catch (IoError e) {
        Console.printError("cannot read ${args[0]}");
        return 1;
    }
}
```

### `std.path`: paths

`import std.path as Paths;`. The paths these functions create live where the caller says, like what
any function returns; they accept `/` and `\`.

| Function | Example |
|---|---|
| `Paths.parent(p)` | `"a/b/c.lar"` → `"a/b"` (`""` if there is no folder) |
| `Paths.fileName(p)`, `Paths.stem(p)`, `Paths.extension(p)` | `"c.lar"`, `"c"`, `"lar"` |
| `Paths.join(dir, file)` | `"a/b"` + `"c.lar"` → `"a/b/c.lar"` (if `file` is absolute, it stays the same) |
| `Paths.isAbsolute(p)` | `"/x"`, `"C:/x"` and `"\\x"` are |
| `Paths.normalize(p)` | `"/x/./y/../z"` → `"/x/z"` |
| `Paths.absolute(p)` | normalized and from the current folder if it was relative |
| `Paths.relative(base, p)` | `p` relative to `base` if it is inside; otherwise, absolute |

### `std.os`: the environment

| Function | What it does |
|---|---|
| `os.env(name): String?` | an environment variable, or `null` |
| `os.cwd(): String` | the current folder |
| `os.run(command): int32` | runs a command with the system's shell and gives its exit code |
| `os.programDir(): String` | the folder of the executable (`""` if it cannot be known) |
| `os.platform(): String` | `"windows"`, `"linux"`, `"macos"` or `"other"` |
| `os.exit(code)` | ends the program right away (without freeing memories or waiting for threads) |

### `std.text`: reading text byte by byte

For lexers and parsers: `text.isDigit(b)`, `isHexDigit`, `isLetter`, `isLetterOrDigit`,
`isIdentifierPart` (letter, digit or `_`), `isSpace`, `isUpper`, `isLower` (all ASCII),
`text.digitValue(b): int32?`, `text.isAscii(s)` and `text.fromCode(code): String` (the text of a
Unicode character: `fromCode(241)` is `"ñ"`).

### `std.text.regex`: regular expressions

Written in Larimar, without any C library: they work the same on every system.

```actionscript
import std.text.regex { Regex, Match, RegexError, message };

let email: Regex = Regex.compile("([a-z]+)@([a-z]+)\\.com");      // RegexError if the pattern is wrong
let m: Match? = email.find("write to ana@mail.com");
if (m != null) {
    println("${m.value} belongs to ${m.group(1) ?? ""}");           // ana@mail.com belongs to ana
}
let date: Regex = Regex.compile("(\\d{4})-(\\d{2})-(\\d{2})");
println(date.replace("2026-10-26", "$3/$2/$1"));                    // 26/10/2026
```

- **What it offers:** `matches(text)` (the whole text), `contains(text)`, `find(text): Match?`,
  `findAll(text): Match[*]`, `replace(text, replacement)` (`$0` is what was found, `$1`..`$9` the
  groups, `$$` a `$`) and `split(text)`.
- **A `Match`** has `start` and `end` (bytes), `value`, and `group(i): String?` (`null` if the group
  did not take part; `group(0)` is everything).
- **What a pattern understands:**
  - characters (`\.` for a sign as it is, `\n`, `\t`) and `.` (any except `\n`);
  - classes (`[abc]`, `[a-z]`, `[^0-9]`) and shortcuts (`\d`, `\w`, `\s` and their opposites `\D`, `\W`, `\S`);
  - anchors: `^`, `$`, `\b` and `\B`;
  - repetitions `*`, `+`, `?`, `{n}`, `{n,}` and `{n,m}`; with `?` after them they take as little as possible;
  - groups `(x)`, non-capturing `(?:x)`, and alternatives `x|y`.
- **Classes are ASCII.** An accented letter counts as one character for `.` and `[^...]`, but it is
  not in `\w` and cannot be written inside `[...]`.
- **It does not hang.** Each position of the text is tried at most once per instruction of the
  pattern, so patterns like `(a*)*b`, which take forever in other engines, answer right away here.

### `std.net`: TCP

`TcpSocket.connect(host, port)` opens a connection (with a name or an IP, v4 or v6) and
`TcpListener.bind(host, port)` waits for connections (`"0.0.0.0"` for every address; with port 0 the
system chooses one, and `port()` says which). A `TcpSocket` is used directly, as in C (`read(buffer)`,
`write(bytes)`, `writeText(text)`, `close()`), and it is also an `InputStream` and an `OutputStream`:
the `Reader` reads lines from it just like from a file, and `copy()` sends any stream over the network.

```actionscript
import std.net { TcpSocket, TcpListener, NetError, message };
import std.io.streams { Reader };
import std.io.files { IoError };
import std.io.console as Console;

function main(): int32 {
    try {
        let server: TcpListener = TcpListener.bind("127.0.0.1", 8080);
        while (true) {
            let client: TcpSocket = server.accept();     // it closes on its own at the end of the turn
            client.setTimeout(5000);
            try {
                let request: Reader = { from: client };
                while (true) {
                    let scratch: byte[4096] = [];
                    let line: String? = request.readLine() in scratch;   // no malloc per line
                    if (line == null || line! == "") { break; }          // end of the headers
                }
                client.writeText("HTTP/1.0 200 OK\r\nContent-Type: text/plain\r\n\r\nhola\n");
            } catch (IoError e) {}
        }
    } catch (NetError e) {
        Console.printError(message(e));
        return 1;
    }
    return 0;
}
```

- Errors when connecting and listening are a `NetError`: `HostNotFound(host)`, `Refused`, `Timeout`,
  `Closed`, `Reset`, `AddressInUse`, `Other(code)`; `message(e)` gives the text. Reading and writing
  throw `IoError`, like any stream.
- Sockets wait (they block): `read` waits for something to arrive and returns 0 when the other side
  closed. `setTimeout(ms)` limits the wait of `read` and `write`.
- `finishWriting()` tells the other side that nothing more will be written (it reads the end), but
  its answer can still be read.
- A socket closes on its own when the memory where it lives is freed, so one accepted in a loop is
  not left open even if `close()` is not called.
- `read` fills the buffer it receives, creating nothing; with the `Reader` and `readLine() in scratch`,
  reading a million lines from a socket asked the system for about 4,400 memory allocations in total.
- To serve several connections at the same time, `TcpServer` (below). On Windows (Winsock) `larimar build`
  links `ws2_32` automatically.
- `Connection` is the interface of a connection in both directions (`read`, `write`, `flush`, `close`):
  `TcpSocket` implements it, and so does what a `TlsProvider` gives (see `std.net.http.tls`). Whoever
  speaks a protocol over a `Connection` does not know whether it is encrypted.
- `handle()` gives the system's socket (a `Socket`, the type of `std.net`), for a C library that works
  on a connection that is already open, like a TLS one: a C function that receives a `Socket` receives
  the descriptor (a `SOCKET` on Windows). The socket still belongs to the `TcpSocket`, and closes with it.
- `std.net` is written in Larimar over the system's socket functions: it is a good example of
  [`#when`](#each-system-its-own-when), [pointers](#c-pointers-t-and-) and
  [resources](#resources-released-by).
- `NetError.Tls(reason)` is a failure of the encryption (a rejected certificate, a failed TLS handshake)
  and `NetError.TlsUnavailable(what)` that there is no TLS to use.

### `std.net`: TCP and UDP servers

`TcpServer` and `UdpServer` are the loop of a server, already written: they are configured with a
literal (which cannot fail) and `run()` does the work (listening can fail, and it throws `NetError`).
What is done with each connection or datagram is a `thread safe` function, so the compiler checks that
the threads of the server do not step on each other.

```actionscript
import std.net { TcpServer, TcpSocket, StopSignal, NetError, message };
import std.io.streams { Reader };
import std.io.files { IoError };

synchronized class Stats {
    let served: int32 = 0;
    function add(): int32 { self.served += 1; return self.served; }
}

function main(): int32 {
    let stats: Stats = {};
    let quit: StopSignal = {};
    let server: TcpServer = {
        port: 8080,                 // host: "127.0.0.1" unless another is given ("0.0.0.0": the whole network)
        threads: 8,                 // connections served at the same time (1 if not given)
        stop: quit,
        onConnect: (client: TcpSocket) -> {
            client.setTimeout(5000);
            try {
                let lines: Reader = { from: client };
                let line: String = lines.readLine() ?? "";
                if (line == "quit") { quit.stop(); }
                client.writeText("hello #${stats.add()}: ${line}\n");
            } catch (IoError e) {}
        }                           // on return, client is closed and its memory is freed
    };
    try {
        server.run();               // it waits here until quit.stop()
    } catch (NetError e) {
        println("cannot listen: ${message(e)}");
        return 1;
    }
    return 0;
}
```

- `run()` accepts in the thread that calls it and shares the connections among its `threads` threads;
  each connection is served with its own memory, which is freed when `onConnect` ends.
- A `StopSignal` is a `synchronized` object with `stop()`: it is given to the literal (`stop: quit`) and
  called from anywhere, the handler included. The server notices it in less than a fifth of a second and
  `run()` returns after the requests in progress. Without `stop`, it serves until the program ends.
- It is a good idea to call `client.setTimeout(...)` at the start: a client that sends nothing takes up
  a thread while it waits.

`UdpSocket` sends and receives datagrams: each one arrives whole or does not arrive, without a
connection. `UdpSocket.bind(host, port)` receives on a port and `UdpSocket.open()` gives any port to
send from; `sendTo(bytes, Address { host, port })` sends and `receive(buffer)` waits for one and gives a
`Datagram` (`length` and `from`, the `Address` of whoever sent it). `UdpServer` is its server:

```actionscript
let server: UdpServer = {
    port: 9000,
    threads: 4,
    stop: quit,
    onReceive: (socket: UdpSocket, data: byte[], from: Address) -> {
        try { socket.sendTo(data, from); } catch (NetError e) {}       // the echo
    }
};
server.run();
```

- Each thread has its own copy of the socket, on the same port: the answers leave from the port the
  client wrote to.
- `maxSize` (65507 if not given) is the biggest datagram received whole.
- UDP does not resend: a datagram can be lost, and whoever sends decides whether to repeat it.

### `std.net`: TLS servers (https)

`TlsServer` is a `TcpServer` whose connections arrive already decrypted. The certificate and its key
are loaded once with `OpenSslProvider.load(certificate, key)`, which throws `NetError` if a file cannot
be used or the key is not the certificate's:

```actionscript
import std.net { TlsServer, TlsSocket, OpenSslProvider, NetError, message };
import std.io.streams { Reader };
import std.io.files { IoError };

function main(): int32 {
    try {
        let tls: OpenSslProvider = OpenSslProvider.load(
            "/etc/letsencrypt/live/example.com/fullchain.pem",
            "/etc/letsencrypt/live/example.com/privkey.pem");
        let server: TlsServer = {
            host: "0.0.0.0",
            port: 443,
            threads: 8,
            tls: tls,
            onConnect: (client: TlsSocket) -> {
                client.setTimeout(5000);
                try {
                    let request: Reader = { from: client };
                    while ((request.readLine() ?? "") != "") {}                 // the headers
                    client.writeText("HTTP/1.1 200 OK\r\nContent-Length: 5\r\n\r\nhola\n");
                } catch (IoError e) {}
            }
        };
        server.run();
    } catch (NetError e) {
        println(message(e));
        return 1;
    }
    return 0;
}
```

- With Let's Encrypt, `fullchain.pem` (the certificate with its chain; `cert.pem` alone is not enough
  for every client) and `privkey.pem` are used. Only root reads that file: the program needs permission
  to read it. When the certificate is renewed, the server has to be restarted.
- A `TlsSocket` is used like a `TcpSocket`: `read`, `write`, `writeText`, `setTimeout`, `Reader`,
  `copy()`. It closes on its own when its memory is freed.
- The TLS handshake happens in the thread that serves, with `handshakeTimeout` (10 seconds if not
  given): a client that does not complete it, or does not speak TLS, is dropped without reaching `onConnect`.
- An `OpenSslProvider` is `synchronized`: the threads of the server share it, and so do several servers.
- It uses OpenSSL 1.1 or 3, loaded the first time it is needed: on Linux it comes with the system; on
  macOS, `brew install openssl@3`. On Windows it is not available yet: `load` throws `NetError.TlsUnavailable`.

### `std.net.http`: HTTP and HTTPS client

A `Client` says **how to connect** (TLS, timeouts, redirects, headers of every request) and a `Request`
**what to ask for**. `send` reads the status line and the headers; the body is read when it is asked
for: whole with `text()`, `bytes()` or `json()` (with `std.json`), or in parts from `body`, which is an
`InputStream` (`Reader` and `copy()` work).

```actionscript
import std.net.http { Client, Response, Header, HttpError, message };
import std.io.file { create };
import std.io.streams { copy };
import std.io.files { IoError };

function main(): int32 {
    let api: Client = {
        timeout: 10000,
        headers: [Header { name: "Authorization", value: "Bearer abc" }]     // they go in every request
    };
    try {
        let r: Response = api.get("https://api.example.com/users/7");
        if (!r.ok()) {
            println("status ${r.status} ${r.reason}");      // a 404 is a response, not an error
            return 1;
        }
        let user: Any = r.json();
        println("${user.name} (${r.header("Content-Type") ?? "?"})");

        let saved: Response = api.send({                    // the Request, as a literal
            method: "POST",
            url: "https://api.example.com/users",
            headers: [Header { name: "Content-Type", value: "application/json" }],
            body: "{\"name\": \"Ana\"}"
        });
        println("created: ${saved.status}");

        let big: Response = api.send({ url: "https://mirror.example.com/disk.iso", timeout: 0 });
        copy(big.body, create("disk.iso"));                 // 4 KB at a time: never whole in memory
    } catch (HttpError e) {
        println(message(e));
        return 1;
    } catch (IoError e) {
        println("disk.iso: io");
        return 1;
    }
    return 0;
}
```

- `Client`: every field has a default value, so `Client {}` already speaks `http://` and `https://`.
  `tls` (a `TlsProvider`; by default `SystemTls {}`), `timeout` in ms (30000; 0 without a limit),
  `maxRedirects` (5; 0 does not follow them) and `headers` (sent in every request, before the ones of
  the request). Methods: `send(request)`, `get(url)` and `post(url, body, contentType)`.
- `Request`: only `url` is required (`{ url: "..." }` is a GET). Also `method`, `headers` (an array of
  `Header { name, value }`: it keeps the order and allows repeated ones), `body` (text, sent with its
  `Content-Length`) and `timeout` (-1, the client's).
- The standalone `get(url)`, `post(url, body, contentType)` and `send(request)` use a `Client {}`: they
  are useful for scripts and tests.
- `Response`: `status`, `reason`, `headers`, `url` (the last one, after the redirects), `ok()`
  (200 to 299), `header(name)` (case-insensitive), `body`, `text()`, `bytes()`, `json()` and `close()`.
- **`HttpError` means there was no response**: `Net(reason)` (it did not connect, it was cut, it took
  too long, or the TLS failed: `"network: tls: certificate rejected: ..."`), `BadResponse(reason)` (the
  server does not speak HTTP, or `json()` of something that is not JSON), `TooManyRedirects`,
  `BadUrl(url)` and `Unsupported(what)`: `https://` when there is no TLS to use. A 404 or a 500 are
  responses: they are checked with `status` or `ok()`.
- The body ends where it ends, whether by `Content-Length`, by `chunked` or because the server closes;
  whoever reads sees no difference. Redirects 301, 302 and 303 switch to GET without a body; 307 and 308
  repeat the method. A redirect from `http://` to `https://` uses the client's `TlsProvider`.
- **Memory**: the response, its headers and its connection live where the caller says, and the
  connection closes on its own when that memory is freed. With `api.get(url) in scratch` inside a loop,
  3,000 requests stayed within 2 MB of memory, leaving no connections open. The response can point to
  the client (to its `TlsProvider`), so the client must live at least as long as it does.
- Each request opens its own connection (`Connection: close`). **Everything waits** (blocks) and there
  are no threads inside. A `Client` is not shared between threads: each thread creates its own.

#### Requests in parallel

If several are needed at the same time, each one goes in a `Thread` (there is no `sendAsync`: that way
you see where each one runs, where its response lives and when it is waited for):

```actionscript
import std.net.http { get, HttpError, message };

synchronized class Results {
    let lines: String[*] = [];
    function add(line: String): void { self.lines.push(line.clone()); }
    function all(): String { return self.lines.join("\n"); }
}

function main(): int32 {
    let paths: String[] = ["/a", "/b", "/c"];
    let shared: byte[*] = [] in heap;
    let results: Results = {} in shared;
    {
        let threads: byte[*] = [] in heap;
        for (path in paths) {
            let url: String = "http://127.0.0.1:8080${path}" in threads;   // it lives as long as the threads
            let t: Thread = {
                run: () -> {
                    try { results.add("${url}: ${get(url).text().length} bytes"); }
                    catch (HttpError e) { results.add("${url}: ${message(e)}"); }
                }
            } in threads;
            t.start();
        }
    }   // here it waits for the three threads
    println(results.all());
    return 0;
}
```

### `std.net.http.tls`: encrypted connections

`https://` knows nothing about encryption: it asks a **`TlsProvider`** for an encrypted connection and
speaks HTTP over it. The interface is a single function:

```actionscript
public interface TlsProvider {
    /** An encrypted connection to host:port, after the TLS handshake. timeout: for reads and writes, in ms. */
    function connect(host: String, port: int32, timeout: int32): Connection throws NetError;
}
```

**`SystemTls`** is the one that comes with Larimar, and the one a `Client` uses if it is not given
another. It uses what the system already has:

| System | Uses | Trusted certificates |
|---|---|---|
| macOS | Network.framework (it comes with the system) | the Keychain's, like Safari |
| Windows | SChannel (it comes with the system) | the Windows store's |
| Linux and others | OpenSSL (`libssl.so.3` or `libssl.so.1.1`), loaded the first time it is used | the system's (`/etc/ssl/certs`) |

- It checks the server's certificate and that it is for that name. `SystemTls { verify: false }`
  accepts any: only for testing against a local server with a certificate of its own.
- A program that never opens `https://` loads nothing, and no OpenSSL headers or libraries are needed
  to compile: `larimar build` links what is needed (`-framework Network -framework Security` on macOS,
  `secur32` on Windows, `-ldl` on Linux).
- If there is no TLS on the system (a Linux without OpenSSL), the request gives
  `HttpError.Unsupported("https: OpenSSL not found (tried libssl.so.3, libssl.so.1.1, libssl.so)")`:
  the message says what is missing.
- On Windows, SChannel negotiates TLS 1.2 (TLS 1.3 with SChannel needs another API, not used here yet).

#### A TLS of your own: mbedTLS

To use another library (to carry the TLS inside the executable, for example), `TlsProvider` is
implemented and given to the client: `Client { tls: MbedTls {} }`. A complete example with
[mbedTLS](https://github.com/Mbed-TLS/mbedtls) 3.6, which is plain C and builds with `make`:

```
secure/
├── larimar.toml
├── mbedtls/          # the mbedTLS code (from its releases page), built with: make lib
└── src/
    ├── main.lar
    └── mbed.lar      # the TlsProvider
```

```toml
[project]
name = "secure"

[c]
include_paths = ["mbedtls/include"]
library_paths = ["mbedtls/library"]
libraries = ["mbedtls", "mbedx509", "mbedcrypto"]     # in this order
```

`src/mbed.lar` has two parts: the C that calls mbedTLS (in a `c_code`) and the two classes that
implement the interfaces. The mbedTLS session is a **resource**: C creates it with `malloc`, and Larimar
lets it go with `mbed_free` when the memory of the connection is freed (`released by`), so the C needs
to know nothing about Larimar's memories:

```actionscript
import std.net { Connection, TcpSocket, NetError, Socket };
import std.net.http.tls { TlsProvider };
import std.io.files { IoError };

c_code {
    #include <stdlib.h>
    #include <mbedtls/ssl.h>
    #include <mbedtls/net_sockets.h>
    #include <mbedtls/entropy.h>
    #include <mbedtls/ctr_drbg.h>
    #include <mbedtls/error.h>
    #include <psa/crypto.h>

    typedef struct {
        int error;                      /* 0: fine */
        char text[200];
        int open;
        mbedtls_net_context net;        /* only its fd: the socket belongs to the TcpSocket */
        mbedtls_ssl_context ssl;
        mbedtls_ssl_config conf;
        mbedtls_x509_crt ca;
        mbedtls_entropy_context entropy;
        mbedtls_ctr_drbg_context drbg;
    } MbedConn;

    static void mbed_fail(MbedConn* c, const char* what, int code) {
        char why[150];
        mbedtls_strerror(code, why, sizeof why);
        snprintf(c->text, sizeof c->text, "%s: %s", what, why);
        c->error = 1;
    }

    /* Larimar releases it (released by mbed_free) when the memory of the connection is freed */
    static void mbed_free(MbedConn* c) {
        if (c->open) mbedtls_ssl_close_notify(&c->ssl);
        mbedtls_ssl_free(&c->ssl);
        mbedtls_ssl_config_free(&c->conf);
        mbedtls_x509_crt_free(&c->ca);
        mbedtls_ctr_drbg_free(&c->drbg);
        mbedtls_entropy_free(&c->entropy);
        free(c);
    }

    static MbedConn* mbed_open(int fd, const char* host, const char* caFile, bool verify) {
        MbedConn* c = (MbedConn*)calloc(1, sizeof(MbedConn));
        if (!c) return NULL;
        mbedtls_ssl_init(&c->ssl);
        mbedtls_ssl_config_init(&c->conf);
        mbedtls_x509_crt_init(&c->ca);
        mbedtls_entropy_init(&c->entropy);
        mbedtls_ctr_drbg_init(&c->drbg);
        psa_crypto_init();
        int r = mbedtls_ctr_drbg_seed(&c->drbg, mbedtls_entropy_func, &c->entropy, NULL, 0);
        if (r != 0) { mbed_fail(c, "random", r); return c; }
        if (verify && (r = mbedtls_x509_crt_parse_file(&c->ca, caFile)) < 0) { mbed_fail(c, caFile, r); return c; }
        r = mbedtls_ssl_config_defaults(&c->conf, MBEDTLS_SSL_IS_CLIENT, MBEDTLS_SSL_TRANSPORT_STREAM, MBEDTLS_SSL_PRESET_DEFAULT);
        if (r != 0) { mbed_fail(c, "config", r); return c; }
        mbedtls_ssl_conf_authmode(&c->conf, verify ? MBEDTLS_SSL_VERIFY_REQUIRED : MBEDTLS_SSL_VERIFY_NONE);
        mbedtls_ssl_conf_ca_chain(&c->conf, &c->ca, NULL);
        mbedtls_ssl_conf_rng(&c->conf, mbedtls_ctr_drbg_random, &c->drbg);
        if ((r = mbedtls_ssl_setup(&c->ssl, &c->conf)) != 0) { mbed_fail(c, "setup", r); return c; }
        if ((r = mbedtls_ssl_set_hostname(&c->ssl, host)) != 0) { mbed_fail(c, "host", r); return c; }
        c->net.fd = fd;
        mbedtls_ssl_set_bio(&c->ssl, &c->net, mbedtls_net_send, mbedtls_net_recv, NULL);
        while ((r = mbedtls_ssl_handshake(&c->ssl)) != 0) {
            if (r != MBEDTLS_ERR_SSL_WANT_READ && r != MBEDTLS_ERR_SSL_WANT_WRITE) { mbed_fail(c, "handshake", r); return c; }
        }
        c->open = 1;
        return c;
    }

    static int32_t mbed_read(MbedConn* c, uint8_t* items, int32_t len) {
        while (c->open) {
            int r = mbedtls_ssl_read(&c->ssl, items, (size_t)len);
            if (r > 0) return r;
            if (r == 0 || r == MBEDTLS_ERR_SSL_PEER_CLOSE_NOTIFY) break;           /* the end */
    #ifdef MBEDTLS_ERR_SSL_RECEIVED_NEW_SESSION_TICKET
            if (r == MBEDTLS_ERR_SSL_RECEIVED_NEW_SESSION_TICKET) continue;          /* TLS 1.3: not data */
    #endif
            mbed_fail(c, "read", r);
            return -1;
        }
        c->open = 0;
        return 0;
    }

    static int32_t mbed_write(MbedConn* c, const uint8_t* items, int32_t len) {
        int32_t done = 0;
        while (done < len) {
            int r = mbedtls_ssl_write(&c->ssl, items + done, (size_t)(len - done));
            if (r <= 0) { mbed_fail(c, "write", r); return -1; }
            done += r;
        }
        return 0;
    }

    static int32_t mbed_error(MbedConn* c) { return c->error; }
    static const char* mbed_error_text(MbedConn* c) { return c->text; }
}

extern type MbedHandle released by mbed_free;
extern function mbed_open(s: Socket, host: String, caFile: String, verify: bool): MbedHandle?;
extern function mbed_free(c: MbedHandle): void;
extern function mbed_read(c: MbedHandle, buffer: byte[]): int32;
extern function mbed_write(c: MbedHandle, bytes: byte[]): int32;
extern function mbed_error(c: MbedHandle): int32;
extern function mbed_error_text(c: MbedHandle): String;

/** https:// with mbedTLS. caFile: the trusted certificates, in PEM. */
public class MbedTls implements TlsProvider {
    let caFile: String = "/etc/ssl/certs/ca-certificates.crt";     // Debian/Ubuntu; macOS: /etc/ssl/cert.pem
    let verify: bool = true;

    function connect(host: String, port: int32, timeout: int32): Connection throws NetError {
        let c: MbedConnection = {};                   // what is returned: created where the caller says
        c.tcp = TcpSocket.connect(host, port);        // ...and these, in c's memory
        c.tcp!.setTimeout(timeout);
        c.tls = mbed_open(c.tcp!.handle()!, host, self.caFile, self.verify);
        if (c.tls == null) { throw NetError.Tls("out of memory"); }
        if (mbed_error(c.tls!) != 0) { throw NetError.Tls(mbed_error_text(c.tls!).clone()); }
        return c;
    }
}

/** The TLS session over its TcpSocket. */
class MbedConnection implements Connection {
    let tcp: TcpSocket? = null;
    let tls: MbedHandle? = null;

    function read(buffer: byte[]): int32 throws IoError {
        let n: int32 = mbed_read(self.tls!, buffer);
        if (n < 0) { throw IoError.Failed("mbedtls: ${mbed_error_text(self.tls!)}"); }
        return n;
    }

    function write(bytes: byte[]): void throws IoError {
        if (mbed_write(self.tls!, bytes) < 0) { throw IoError.Failed("mbedtls: ${mbed_error_text(self.tls!)}"); }
    }

    function flush(): void throws IoError {}

    function close(): void throws IoError {
        release(self.tls);                            // the session first, then its socket
        self.tcp!.close();
    }
}
```

And `src/main.lar` uses it like any other:

```actionscript
import std.net.http { Client, Response, HttpError, message };
import mbed { MbedTls };

function main(args: String[]): int32 {
    let client: Client = { tls: MbedTls {} };
    try {
        let r: Response = client.get(args.length > 0 ? args[0] : "https://github.com/");
        println("${r.status} ${r.header("Content-Type") ?? ""}");
    } catch (HttpError e) {
        println(message(e));
        return 1;
    }
    return 0;
}
```

```
$ larimar run
200 text/html; charset=utf-8
```

- The pieces are the same as in any `TlsProvider`: open the `TcpSocket`, do the TLS handshake over its
  socket (`handle()`: C receives the descriptor) and return an object that implements `Connection`. What
  `connect` returns is created where the caller says (the HTTP response), and with it the session,
  which is let go on its own (`released by mbed_free`).
- With `MbedTls { caFile: "my-ca.pem" }` a certificate of your own is trusted (a test server, an
  internal network) without turning off the verification.
- mbedTLS goes inside the executable (static libraries): the program does not depend on what the
  system has. In exchange, updating mbedTLS when a security flaw comes out is the job of whoever uses it.

### `std.json`: JSON

`Json.parse(text): Any throws JsonError` turns a JSON text into an `Any`: an object is a table with
names, an array a table by positions, the integers that fit are `int64` and the rest `float64`.
`Json.stringify(v)` does the opposite (an empty table is written `{}`), and `Json.quote(s)` gives a
`String` as a JSON string, with its quotes and escapes.

```actionscript
import std.json as Json;
import std.json { JsonError };

function main(): int32 {
    try {
        let config: Any = Json.parse("{\"port\": 8080, \"names\": [\"a\", \"b\"], \"debug\": true}");
        println("port ${config.port as int64 ?? 80}, ${config.names.length} names");
        println(Json.stringify({ ok: true, list: { 1, 2, 3 }, name: "x\ty" }));
        Json.parse("[1, 2");
    } catch (JsonError e) {
        switch (e) {
            case Invalid { at, why } -> println("invalid JSON at ${at}: ${why}");
        }
    }
    return 0;
}
```

Output:

```
port 8080, 2 names
{"ok":true,"list":[1,2,3],"name":"x\ty"}
invalid JSON at 5: expected ',' or ']'
```

---

## 26. Projects: `larimar.toml` and `larimar build`

A project is a folder with a `larimar.toml` file:

```toml
[project]
name = "melody"              # required: name of the executable
version = "0.1.0"
main = "src/main.lar"        # the default; its folder is the root of the modules
output = "dist/melody"       # by default build/<name> (build/<name>.exe on Windows)

[c]
compiler = "gcc"             # by default the CC variable, or cc (gcc on Windows)
flags = ["-O2", "-Wall"]     # by default ["-O2"]
sources = ["csrc/helpers.c"] # your own C files, compiled together with the program
include_paths = ["include"]  # header folders (-I)
libraries = ["user32"]       # libraries (-l): user32 -> user32.dll, tone -> libtone.so
library_paths = ["libs"]     # where they are (-L)
```

Paths are relative to the project folder. An unknown key or section is an error, so that a typo does
not go unnoticed.

| Command | What it does |
|---|---|
| `larimar new <name>` | creates the folder with `larimar.toml`, `src/main.lar` and `.gitignore` |
| `larimar build [folder]` | writes `build/<name>.c` and compiles it to the executable |
| `larimar build --debug` | the same, for a debugger (see [Debugging](#debugging-larimar-build---debug-and-larimar-dap)) |
| `larimar run [folder] [-- args]` | compiles and runs, passing it the arguments |
| `larimar check [file or folder] [--json]` | looks for the errors without generating C (see [The editor](#the-editor-larimar-check-and-larimar-lsp)) |
| `larimar lsp` | the language server for editors |
| `larimar dap` | the debugger for editors (over `lldb-dap`) |
| `larimar c <file.lar>` | shows the generated C of a file (with its modules) |

### C libraries: static, dynamic and source code

A Larimar program can use any C library. Its functions are declared with `extern function` (and its
types with `extern type`) and the `larimar.toml` tells the C compiler where it is. There are four ways
to bring in a library, depending on how it comes:

| How it comes | In `[c]` | Result |
|---|---|---|
| **Source code** (`.c`), like SQLite or raygui | `sources = ["vendor/sqlite3.c"]` | it is compiled together with the program: it ends up inside the executable |
| **Static library** (`.a`, `.lib`) | `library_paths = ["vendor/lib"]` and `libraries = ["sqlite3"]`, or the path of the `.a` in `sources` | it ends up inside the executable |
| **Dynamic library of your own** (`.so`, `.dylib`, `.dll`) | `library_paths = ["vendor/lib"]` and `libraries = ["tone"]` | the executable loads it when it starts, from that folder |
| **System library** (`m`, `pthread`, `user32`, one installed with the package manager) | `libraries = ["m"]` and, if needed, `include_paths` / `library_paths` | the executable loads it from the system |

An example with all four at once:

```toml
[c]
include_paths = ["vendor/include"]           # the .h files (-I)
sources = ["vendor/src/embedded.c"]          # source code: it goes inside the executable
library_paths = ["vendor/lib"]               # where to look for the libraries (-L)
libraries = ["mylib", "tone", "m"]           # libmylib.a (static), libtone.so (dynamic), libm (system)
```

```actionscript
c_include "vendor.h";
c_include "<math.h>";

extern function mylib_triple(x: int32): int32;     // from libmylib.a
extern function tone_play(hz: int32): void;        // from libtone.so
extern function embedded_add(a: int32, b: int32): int32;   // from embedded.c
extern function sqrt(x: float64): float64;         // from libm
```

**How static or dynamic is chosen.** `libraries = ["x"]` becomes `-lx`, and the linker looks for
`libx` in `library_paths` and in the system folders. If it only finds the static one (`libx.a`), it
puts it inside the executable; if it finds the dynamic one (`libx.so`, `.dylib`, `.dll`), it prefers
it. To **force the static one** even if the dynamic one exists, put the path of the `.a` in `sources`:

```toml
sources = ["vendor/lib/libmylib.a"]
```

Static libraries and source code are the most portable: the executable is a single file, with nothing
to copy or install.

**When each one is looked for.** A dynamic library is looked for twice, at different moments:

1. **When compiling.** The C compiler looks for it in its own folders (MinGW brings the Windows ones,
   like `user32`) and in `library_paths` (`-L`).
2. **When running.** The operating system loads the file (`.dll`, `.so`, `.dylib`). If it does not find
   it, the program does not start.

That is why `larimar build` **copies no dynamic library**. They stay where they are:

- **System libraries** are looked for by the executable in the usual system paths, and the machine
  where it runs must have them installed.
- **The ones in `library_paths`**: on Linux and macOS, the executable is compiled with the instruction
  to look for them in those same folders (`-Wl,-rpath,...`), so `larimar run` works without copying
  anything. On Windows, a `.dll` is looked for next to the `.exe` or in the `PATH`.

Taking the dynamic libraries to another machine (an installer, a system package, a documented
dependency) is up to whoever distributes the program, and to their licenses. If the executable must be
a single file, the library is linked statically or compiled as source code.

### An example with Windows

```actionscript
// src/win.lar: the module that talks to Windows
c_include "<windows.h>";

public extern type HWND;
public extern function GetConsoleWindow(): HWND;
public extern function MessageBoxA(owner: HWND, text: String, caption: String, kind: uint32): int32;

public const MB_YESNO: uint32 = 0x04;
public const IDYES: int32 = 6;
```

```actionscript
// src/main.lar
import win;

function main(): int32 {
    let window: win.HWND = win.GetConsoleWindow();
    if (win.MessageBoxA(window, "Continue?", "Larimar", win.MB_YESNO) == win.IDYES) {
        println("yes");
    }
    return 0;
}
```

with `libraries = ["user32"]` in `[c]`. Declaring everything about Windows in a `win` module avoids
repeating the `extern` declarations: each `extern type` is a different type in each module that
declares it, so the `HWND` must come from a single place.

### The editor: `larimar check` and `larimar lsp`

**`larimar check`** links and analyzes a program just like `larimar build`, but generates no C and
does not call the C compiler: it is the quick way to know whether there are errors.

```sh
larimar check                    # the project in this folder (its larimar.toml)
larimar check src/tools.lar      # a loose file, as a program
larimar check . --json           # for tools: [{ "file", "line", "message", "kind" }]
```

Without `--json` it writes the errors to the error output (or `no errors`); the exit code is 1 if
there are errors.

**`larimar lsp`** is the language server (Language Server Protocol): the editor starts it and talks to
it through the standard input and output. It answers:

| What | How it looks in the editor |
|---|---|
| Live errors | underlined while you type (when you stop typing for a moment), in every file of the program |
| Hover | the declaration (signature, fields of a struct, variants of an enum) and the `/** ... */` or `//` comment above it |
| Go to definition | also into another module or into `std` |
| References | the uses of a variable, function, method, field, variant or type |
| File symbols | the Outline: functions, types and their members |
| Completion | after `.`: fields and methods according to the type, public names of a module (`shapes.`), variants of an enum; without `.`: local variables, visible names, modules and keywords |
| Signature help | the parameters of the function you are calling, with the current one highlighted |

How it works:

- It keeps in memory the text of the open files (including what you have not saved yet), in C memory
  that is freed when the text changes: the server can stay open for hours without growing.
- Each question is answered by a new process (`fork()`): it links and analyzes the program with those
  texts, answers and ends. That way no analysis leaves memory behind or sees the state of the previous
  one, and if one fails only that answer is lost. On the compiler itself (some 16,000 lines) each answer
  takes about 0.2 s.
- The program of a file is the `main` of the `larimar.toml` above it; if that program does not import
  it (or there is no `larimar.toml`), the file is analyzed as a program on its own.
- Where there is no `fork()` (Windows), or with `LARIMAR_LSP_NO_FORK=1`, each question goes to a
  `larimarc lsp-worker` through two temporary files.
- The server's diagnostic messages go to the error output (the editor shows them in its output panel);
  the standard output is only for the protocol.

Limits: the analysis is done on the whole program, so a syntax error (which prevents linking) leaves
no answers until it is fixed; columns are looked for in the text of the line (the compiler keeps the
line of each node, not the column), so if a name appears twice on the same line with different
meanings, the first one wins.

#### VS Code

The Larimar extension for VS Code is installed from its package:

```sh
code --install-extension larimar-<version>.vsix
```

It looks for Larimar in this order: the `larimar.home` setting, the `LARIMAR_HOME` variable, `larimar`
on the `PATH` and, on macOS and Linux, the `LARIMAR_HOME` of your login shell (VS Code opened from the
Dock does not see what `~/.zshrc` exports). It starts `$LARIMAR_HOME/bin/larimarc lsp`. It adds the
commands **Larimar: Run Project** and **Debug Project** (also on the ▷ button of the editor), **Build
Project**, **Check Project**, **Show Generated C** and **Restart Language Server**.

Other editors (Neovim, Helix, Zed, Sublime...) only need to be told to start `larimarc lsp` for `.lar`
files, with `LARIMAR_HOME` in the environment.

### Debugging: `larimar build --debug` and `larimar dap`

`larimar build --debug` (also `larimar run --debug`, and `larimar file.lar -o file.c --debug`) compiles
with `-g -O0` (without the `-O` of `flags`) and puts `#line` directives in the C that say which line of
the `.lar` each part comes from. Inside a function, each C line carries the `.lar` line of the statement
it comes from, and the header of the function the line where it is declared; the functions of the
runtime and the generated helpers are seen as the C they are. It also writes the **debug map** next to
the C (`build/<name>.debug.json`): each C function with its Larimar name and its variables (their name
in Larimar, their name in C and their type), the globals and the shape of each type.

**`larimar dap`** is the debugger for editors (Debug Adapter Protocol), written in Larimar. It sits
between the editor and `lldb-dap`, LLVM's adapter that runs the program under lldb:

```
VS Code  <-- DAP -->  larimar dap  <-- DAP -->  lldb-dap  -->  build/demo
```

What goes through it unchanged: starting, breakpoints, continuing, stepping, threads. What it answers
itself, with the map:

- **The stack** with the Larimar names (`main`, `Dog.bark`, `geo.shapes.area`); the frames of the
  runtime and of C come out dimmed and with `[C]`, and the editor focuses the first Larimar one.
- **The variables** with their Larimar names (`total`, not `total_12`), without the compiler's
  temporaries, only the ones already declared on that line, and each value read and shown as Larimar:

  | Value | It looks like |
  |---|---|
  | `String` | `"Larimar ñ"` |
  | `T[*]`, `T[]` | `[3] ["a", "b", "c"]`, and when opened `[0]`, `[1]`... |
  | `T?` | its value, or `null` |
  | struct | `Point {x=1, y=2}`, and its fields |
  | enum | `Circle(r=1.5)`, and its fields |
  | class object | with its real class (an `Animal` that is a `Dog` looks like `Dog`) and the fields of every level |
  | interface | the object behind it |
  | `Any` | what it holds: `42`, `"x"`, `{ 2 items, 2 entries }` with its entries when opened, or the object |

  The values are read with C expressions that lldb evaluates (`(long long)(x).len`, `memory read`...):
  there is nothing to install in lldb. A **C** scope also shows everything lldb sees, as it is.
- **The debug console and the hover** understand Larimar paths: `a.name`, `list[2]`, `pts[1].y`,
  `data.inner`, `list.length`. The rest (a C expression, an lldb command starting with `` ` ``) goes to lldb.
- **Function breakpoints** with Larimar names (`main`, `Dog.bark`).
- **Stepping into a function** skips the runtime (you do not end up inside `rt_str` or `List_s_push`).
- **Panics**: with the *Panics* filter (on by default), the program stops where a panic happens (index
  out of range, `!` on `null`, `panic(...)`) and the editor shows it as an exception with its message:
  *index 3 out of range (length 3)*.

It needs `lldb-dap`: on macOS it comes with recent Xcode tools (`xcrun --find lldb-dap`) or with
Homebrew's LLVM; on Linux, with the lldb package (`lldb-dap` or `lldb-dap-18`, for example); on
Windows, with LLVM. `larimar dap --backend <path>` or `LARIMAR_LLDB_DAP` say which one to use.

**In VS Code**, **Larimar: Debug Project** or F5 on a `.lar` file compiles with `--debug` and starts
`larimar dap`. A `launch.json` can set the project, the arguments, the environment, whether it stops at
the start (in Larimar's `main`) and whether the output goes to the debug console or to the terminal
(for programs that read the keyboard):

```json
{
    "type": "larimar",
    "request": "launch",
    "name": "Debug Larimar project",
    "project": "${workspaceFolder}",
    "args": ["--verbose"],
    "env": { "PORT": "8080" },
    "stopOnEntry": false,
    "console": "integratedTerminal"
}
```

**From the terminal**, or with other debuggers, `debug/` brings formatters that teach lldb and gdb to
show the same values (not the names: there the variables are called as in the C, `total_12`, and the
temporaries are seen):

```sh
larimar build --debug
lldb build/demo
(lldb) command script import $LARIMAR_HOME/debug/larimar_lldb.py
(lldb) breakpoint set --file main.lar --line 12
(lldb) run
(lldb) frame variable
```

With gdb: `source $LARIMAR_HOME/debug/larimar_gdb.py` and `break main.lar:12`. In VS Code, the
`larimar.debugger` setting can use CodeLLDB or the C/C++ extension with gdb instead of `larimar dap`,
with these formatters.

---

## 27. What the transpiler generates

The result is **a single C99 file** (`build/<name>.c`) that contains the runtime and the whole program,
with all its modules, with no dependencies beyond the C standard library. `larimar build` compiles it,
but it can also be compiled by hand with any C compiler:

```sh
larimar c src/main.lar > program.c
gcc -std=c99 -O2 program.c -o program
```

The generated C compiles without warnings with `gcc -std=c99 -Wall -Wextra -pedantic`, and **only
carries what the program uses**. It is decided in two steps, following the names:

1. **The program.** It starts from `main`, the `export function`s and the C the program wrote itself
   (`c_include`, `c_code`), and keeps each function, method, type, global variable or helper function
   that any of that names, and so on. A `String` method the program does not call, the `Opt_i64` that
   only appeared in its signature or the `std` function nobody uses do not reach the C.
2. **The runtime.** The pieces of the runtime that define some name of what was kept (and the ones
   those use) are added, with their `#include`s. A program that uses no memories does not carry the
   memory code; one that does not divide does not carry the division checks; a `println` of numbers
   and texts is written with `printf`.

A "hello world" looks like this:

```c
/* Generated by the transpiler. Runtime first, then the program. */
#include <stdint.h>
#include <stdio.h>

/* ---- Prototypes ------------------------------------------------------------ */
static int32_t user_main(void);

/* ---- Functions ------------------------------------------------------------- */
static int32_t user_main(void) {
    fputs("hola mundo\n", stdout);
    return 0;
}

/* ---- Entry point ----------------------------------------------------------- */
int main(void) {
    int32_t result = user_main();
    return (int)result;
}
```

And it is readable:

| In Larimar | In C |
|---|---|
| `struct` | a plain `struct`; methods are functions that receive `S*` |
| `class` | a `struct` with a header (vtable and memory); the subclass contains its parent as `_super` |
| virtual methods | a table of function pointers per class |
| `interface` | `{ void* obj; const Table* t; }` |
| `enum` | `{ int32_t tag; union { ... } as; }` |
| lambda | `{ function pointer; environment with the captures }`, by value |
| `T[N]` | `{ int32_t length; T items[N]; }` |
| `throws` | an extra `RtError*` parameter, checked after each call |
| automatic memories | an `RtMem` per block (`mem_N`) and per statement (`tmp_N`), created only if something lives there and freed on every exit |
| what a function returns | a first parameter `RtMem* rt_dest`: the memory of the call (`NULL` if the function does not create its result) |
| `geo.shapes.area` | `geo__shapes__area` (the main file keeps its names) |
| `main` | `user_main`, called from C's `main` |
| `extern type X;` / `= c "T";` | `typedef void* Ext_X;` / `typedef T Ext_X;` |
| `extern type X = (A) -> R;` | `typedef R (*Ext_X)(A);` |
| `extern type X = struct { ... };` | the C struct, with its name; Larimar does not define it |
| `export function f` | the Larimar function (`larimar_f`) and a function `f` with C types that calls it |
| `Any` | `RtAny`: `{ kind; union of values }`; a table is an `RtTable*` with a hash index; a struct goes in a copy |
| `Thread`, `synchronized` | system threads (`pthread` or Windows); a recursive lock per object |

### Checking the memory

To check a program during development, compile it with the error detectors of gcc or clang:

```toml
[c]
flags = ["-g", "-fsanitize=address,undefined"]
```

With AddressSanitizer on, **the runtime teaches it to see inside the memories**. A memory asks the
system for big blocks and hands out pieces of them, so, without help, AddressSanitizer would only see
the whole block and would not notice that something goes outside its piece. The runtime solves it
like this:

- the part of each block that has not been handed out yet is poisoned;
- each piece unpoisons exactly the bytes that were asked for;
- in the memories that grow, there is a poisoned gap between one piece and the next.

That way, reading or writing a single byte too many stops at that line, with the error and the call
stack. It happens above all with C code (`c_code`) that writes into a memory:

```actionscript
c_code {
    static const char* bad(RtMem* m) {
        char* out = (char*)rt_mem_alloc(m, 4, 0);
        for (int i = 0; i <= 4; i++) out[i] = 'A';      /* one byte too many */
        out[3] = 0;
        return out;
    }
}
```

```
==441==ERROR: AddressSanitizer: use-after-poison on address 0x531000000815
WRITE of size 1 at 0x531000000815 thread T0
    #0 in bad program.c:274
```

Without the checks, that byte would silently step on what comes next in the memory. What has already
died is detected too: a freed memory gives its blocks back to the system, and AddressSanitizer warns if
something reads them afterwards.

- The checks only exist when compiling with `-fsanitize=address`. Without that option they cost
  nothing: the C is the same, without gaps or checks.
- With `-DRT_DEBUG_MEMORY` (without AddressSanitizer) the same gaps are left, and the freed blocks are
  filled with `0xDD`: a value that outlived its memory reads as garbage instead of looking right.
- Memories over a stack or static buffer (`in byte[N]`) are not poisoned, because that buffer does not
  belong to the runtime.

**If the compiler gets it wrong.** If the generator finds something the analysis should have resolved
(for example, a call that creates its result and was left without a memory), it does not write C that
would fail when running, but stops with an error:

```
Internal Error [main.lar:7]: 'buffer' creates its result, but this call was given no memory for it.
This is a bug of the compiler, not of your program: please report it.
```

And if even so something tried to create a value without a memory, the program stops with a `panic`
that says so, instead of failing with a segmentation fault.

---

## 28. Larimar written in Larimar

The Larimar compiler, **larimarc**, and the `larimar` tool are written in Larimar. The repository has:

```
larimar/
  src/                   the compiler (Larimar), with larimar check, larimar lsp and larimar dap
  std/                   the standard library
  tests/                 the tests (tests/lsp: check and the language server)
  debug/                 value formatters for lldb and gdb
  bin/larimar            the launcher that is installed
  MANUAL.md              this manual (MANUAL_ES.md: in Spanish)
  larimarc_bootstrap.c   the compiler already translated to C, to start without Larimar
  build-bootstrap.sh     builds the compiler and installs the ../out/larimar folder
```

To build it only a C compiler is needed:

```sh
cd larimar
./build-bootstrap.sh --verify
```

1. It compiles `larimarc_bootstrap.c` and gets `larimarc`.
2. With `--verify`, it compiles `src/` three times: with that larimarc (`build/stage1.c`), with the
   compiler that comes out of it (`build/stage2.c`) and with the one that comes out of that one
   (`build/stage3.c`). `stage2.c` and `stage3.c` must be identical byte by byte: the compiler, compiled
   by itself, produces itself. If `larimarc_bootstrap.c` is older than `src/`, it says so and installs
   the compiler made from `src/`.
3. It installs the result in `../out/larimar` (or in `LARIMAR_PREFIX`): `bin/larimarc`, `bin/larimar`,
   a copy of `std/`, of `debug/` and of this manual. That folder can be deleted and regenerated whenever
   you want; everything is edited in the repository.

After changing the compiler, `./build-bootstrap.sh --verify` checks and installs it, and the bootstrap C
is updated with what it says:

```sh
cp build/stage2.c larimarc_bootstrap.c
```

`bin/larimar` sets `LARIMAR_HOME` to the folder of the installation, and the compiler looks for the
standard library in `$LARIMAR_HOME/std`.

**A rule when changing the language.** The compiler is built with its own standard library, so `std/`
can only use what the compiler that compiles it already understands. If you add something to the
language (like `panic`) and want to use it in `std/`, it is first added to the compiler,
`larimarc_bootstrap.c` is regenerated with a compiler that already understands it, and then it is used
in `std/`.

### The tests

`tests/run-tests.sh` compiles and runs every program in `tests/`, each one with AddressSanitizer and
UBSan. Each file says in its first lines what it expects:

```actionscript
// expect: run
// output: hola 3
function make(n: int32): String { return "hola ${n}"; }
function main(): int32 { println(make(3)); return 0; }
```

| First line | The test passes if... |
|---|---|
| `// expect: run` | it compiles, runs without memory errors, ends with 0 and prints the `// output:` lines |
| `// expect: error text` | the compiler rejects it with a message that contains `text` |
| `// expect: panic text` | it compiles, and stops when running (`panic`) with `text` |
| `// expect: memory-error` | it compiles, and the detectors find a memory error when running |

```sh
./build-bootstrap.sh --verify --test  # build, check that it compiles itself, test and install
tests/run-tests.sh                    # all of them, with the larimarc that build-bootstrap.sh made
tests/run-tests.sh memory             # only the ones with "memory" in the path
LARIMARC=build/larimarc_stage2 tests/run-tests.sh
```

`tests/memory/` covers the memory model: what a function returns (created, a view of an argument, one
of its arguments), nested calls, default values of fields, interpolation, loops, `map` and `filter`,
kept lambdas, `in default`, memories of your own, `clone()`, exceptions with live temporaries, a
`switch` that creates, objects, `Any`, threads, `export function` called from C, and what must be
rejected. **Each failure that is found first goes in as a test**, and then it is fixed.

`tests/lsp/lsp_test.py` (`run-tests.sh` runs it if there is `python3`) tests `larimar check --json` and
talks to `larimar lsp` over the project in `tests/lsp/project`: published errors, hover, definition,
references, symbols, completion and signature help, with `fork()` and with `LARIMAR_LSP_NO_FORK=1`.
`tests/debug/debug_test.py` compiles `tests/debug/values.lar` with `--debug`, stops with lldb and with
gdb (whichever there are) on a line of the `.lar` and checks how the values look; with `lldb-dap`, it
talks to `larimar dap` like an editor (stack, variables, children, paths in evaluate, and a panic of
`tests/debug/panic.lar` as an exception with its message).
`tests/tls/tls_test.py` starts a local HTTPS server with the certificate of `tests/tls` and compiles
`tests/tls/client.lar`: the certificate rejected by default, and with `SystemTls { verify: false }` a
GET, a `chunked` body, a big one with `copy()`, a POST, a redirect from `http://` to `https://` and a
`TlsProvider` of its own; on Linux, also the message when OpenSSL is missing.

---

## 29. Current limitations

- There is no `defer` and there are no generics.
- An `Any` does not keep `[*]` lists, lambdas or interfaces.
- A `synchronized` class cannot inherit, and `wait until` has no time limit (it waits until the condition holds).
- The standard library is small: files, console, paths, environment, bytes, regular expressions, JSON,
  TCP and UDP with their servers, a TLS server, and an HTTP and HTTPS client (`std.io.*`, `std.path`,
  `std.os`, `std.text`, `std.text.regex`, `std.json`, `std.net`, `std.net.http`). The network does not
  have an HTTP server, WebSockets, an event loop or reused HTTP connections (keep-alive) yet. The TLS
  server is not available on Windows yet. The client TLS of macOS and Windows is written and compiles,
  but its tests have only run on Linux.
- Some operations of `String` and `Any` are still intrinsics of the compiler; lists are not declared in `std.lang` yet.
- Only C functions (`extern` or `export`) can be passed to C, not lambdas with captures; the context
  travels in the library's `void* data`. A C struct cannot have array fields (except a text,
  `char name[32]`, which is read as a `String`) or unions; they are read with a function in `c_code`.
- A C pointer (`T*`) is not indexed (`p[i]`) or added to; for a C array, a function in `c_code`.
  `&x` only works as an argument of a C function.
- The function that lets a resource go (`released by`) receives only the resource: if it needs more
  context (a table of functions loaded with `dlopen`, like OpenSSL in `std.net`), it goes in `c_code`.
- A memory cannot be emptied by hand (`clear()`); it is freed at the end of its block.
- The compiler decides without running whether a function creates its result. If it sometimes returns
  something new and sometimes something that already existed, it is treated as if it always created:
  what it returns lives in the memory of the call (to keep it longer, `in default` or `clone()`).
- Lambdas, and therefore interface literals, cannot throw errors.
- A lambda cannot capture another one of the same type.
- An enum cannot contain another value of its own type (use a class for recursive structures).
- The names of types, methods and variants must be ASCII; variables and fields can use any letter.
- No name can contain `__`.

---

## 30. Quick reference

```actionscript
// Modules
import geo.shapes;                      // shapes.area(s)
import geo.shapes as g;                 // g.area(s)
import geo.shapes { Shape, area };      // area(s)
public function exported(): void { }

// Declarations
const MAX: int32 = 10;
let global: int32 = 0;
function f(a: int32, b: String): bool throws MyError { ... }
function add(p: Node, k: Node in p): void { p.kids.push(k); }   // k lives as long as p (also: in default, in self)
struct S { let field: int32 = 0; function m(): void { } operator +(o: S): S { ... } }
class C extends Parent implements I { let field: String; override function m(): void { super.m(); } }
interface I { function m(): void; }
enum E { A, B(x: int32) }

// Variables and values
let x: int32 = 5;
let s: S = { field: 1 };
let o: C = C { field: "x" };                  // it lives in the memory of its block
let e: E = E.B { x: 3 };
let q: int32? = null;
let arr: int32[8] = [1, 2];
let items: int32[*] = [];
let last: int32 = items.pop();
let fn: (int32) -> int32 = (n) -> { return n + x; };

// Memory (automatic: temporaries of the statement, memory of the block, the caller's)
let text: String = "hello ${x}";                // in the memory of the block
let kept: String = "for ever ${x}" in default;  // the whole program
let memory: byte[*] = [] in heap;               // a memory of your own
let made: String = build(x) in memory;          // the result of a call, there
let copy: String = text.clone();

// Control
if (c) { } else if (d) { } else { }
while (c) { }
for (i in 0..10) { }
for (i, v in items) { }
let r: int32 = switch (e) { case A -> 0; case B { x } -> x; };
if (pet is Dog d) { println(d.breed); }
try { f(1, "a"); } catch (MyError err) { }
throw MyError.Something;

// Optionals
let v: int32 = q ?? 0;
let w: int32 = q!;
if (q != null) { let z: int32 = q + 1; }
if (q == null) { return; }              // from here on, q is not null
let k: String = q > 0 ? "pos" : "neg";

// C
c_include "<stdio.h>";
extern function puts(text: String): int32;
extern function cExit(code: int32): void = c "exit";           // another name in C
extern const EOF: int32;
extern const SIZE: int32 = c "(int)sizeof(long)";
extern let errno: int32;
extern type CFile = c "FILE*" released by fclose;               // a resource: let go with its memory
extern function fopen(path: String, mode: String): CFile?;
extern function fclose(f: CFile): int32;
extern type Node = struct "struct node" { let next: Node*; let name: String; };
two_results(&a, &b);                                            // & only as an argument of C
release(file);                                                  // let it go earlier
#when windows                                                   // chosen when compiling the C; each directive
    let sep: String = "\\";                                     // alone on its line; #when, #else and #end
#else                                                           // of one choice, in the same column
    let sep: String = "/";
#end                                                            // sep goes on: every branch declares it

// Literals
let c: byte = 'a';
let page: String = """
    <p>${text}</p>
    """;
let sql: String = raw"""
    SELECT * FROM users WHERE name = "x\y";
    """;                                  // as it is: no escapes or ${...}

// Text
let w: String = text.trim().substring(0, 3);          // views
let up: String = text.toUpperCase();                 // new text
let n: int64 = "42".toInt() ?? 0;
let sb: StringBuilder = {};
sb.add("x = ${n}");

// Program and standard library
// main can receive the arguments: main(args: String[])
import std.io.files as Files;
let content: String = Files.readString(args[0]);

// Any
let t: Any = { 1, "two", name: "x", inner: { 3 } };
let n: int32 = t.port as int32 ?? 80;
for (k, v in t.fields) { }

// Threads
synchronized class Box { let n: int32 = 0; function inc(): void { self.n += 1; } }
function take(): int32 wait until (self.n > 0) { ... }           // in a synchronized class: it waits until it holds
let onConnect: (TcpSocket) -> void thread safe;                 // other threads call it: its lambda is checked
let th: Thread = { run: () -> { box.inc(); } };   // when its memory is freed, it waits for it to end
th.start();
th.join();

// Failures of the program
panic("should not happen: ${x}");                    // it stops with the message (code 101)

// C
c_include "<math.h>";
extern function sqrt(x: float64): float64;
extern type Handle;                                   // void*
extern type File = c "FILE*";                         // a concrete C type
extern type Point = struct { let x: float32; let y: float32; };   // a C struct
extern type Op = (int32, int32) -> int32;             // a pointer to a C function
export function subtract(a: int32, b: int32): int32 { return a - b; }   // C can call it
```
