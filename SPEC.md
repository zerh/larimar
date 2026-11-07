# The Larimar Language Specification

**Version 1.0**

This document defines the Larimar programming language. It is normative: a program means what this
document says, and an implementation is correct when it does what this document says. The
[Manual](MANUAL.md) teaches the language with examples; when the two disagree, this document wins.

The compiler has its own version, independent of this one. `larimar --version` shows both:
`larimar 1.2.0 (language 1.0)`. A compiler release may add to the standard library and to the tools
without changing the language; a change to anything in this document is a new language version.

## Contents

1. [Introduction](#1-introduction)
2. [Notation](#2-notation)
3. [Source code](#3-source-code)
4. [Lexical elements](#4-lexical-elements)
5. [Types](#5-types)
6. [Declarations and scope](#6-declarations-and-scope)
7. [Constants and variables](#7-constants-and-variables)
8. [Functions](#8-functions)
9. [Structs, classes, interfaces and enums](#9-structs-classes-interfaces-and-enums)
10. [Expressions](#10-expressions)
11. [Statements](#11-statements)
12. [Optionals and narrowing](#12-optionals-and-narrowing)
13. [Patterns](#13-patterns)
14. [Memory](#14-memory)
15. [The lifetime rule](#15-the-lifetime-rule)
16. [Errors and panics](#16-errors-and-panics)
17. [Any](#17-any)
18. [Threads](#18-threads)
19. [C interoperability](#19-c-interoperability)
20. [Platform directives](#20-platform-directives)
21. [Modules](#21-modules)
22. [Tests](#22-tests)
23. [Predeclared names](#23-predeclared-names)
24. [Program execution](#24-program-execution)
- [Appendix A. Grammar](#appendix-a-grammar)
- [Appendix B. Implementation-defined behavior and limits](#appendix-b-implementation-defined-behavior-and-limits)
- [Appendix C. Outside this specification](#appendix-c-outside-this-specification)

---

## 1. Introduction

Larimar is a statically typed, compiled language. A program is translated to C99 and then compiled by
a C compiler. Its design principles are normative, in the sense that they decide the cases this document
might not foresee:

- **Nothing is hidden.** No garbage collector, no hidden threads, no hidden control flow, no implicit
  conversions, no constructors, no overloading. What a program does can be read in its text.
- **No undefined behavior.** Every operation of the language either has a defined result or stops the
  program with a message ([§16.3](#163-panics)). Only code written in C (`c_code`, native functions)
  is outside this guarantee.
- **Memory without a collector and without dangling references.** Every value that needs storage lives
  in a *memory* that is freed whole at a point that can be seen in the code ([§14](#14-memory)), and the
  compiler proves that nothing refers to freed storage ([§15](#15-the-lifetime-rule)).
- **Threads checked by the compiler.** A thread can share only values and objects that protect
  themselves ([§18](#18-threads)).

What the language deliberately does not have: generics, garbage collection, constructors, function
overloading, exceptions as hidden jumps, `async`, implicit `null`, implicit numeric conversions.

### 1.1 Terms

- **Error** (or *compile error*): the program is rejected by the compiler.
- **Panic**: the program stops at run time with a message and exit code 101 ([§16.3](#163-panics)).
- **Implementation-defined**: an implementation chooses, and documents its choice
  ([Appendix B](#appendix-b-implementation-defined-behavior-and-limits)).
- *Must* and *cannot* state rules; breaking one is an error unless the text says it is a panic.

---

## 2. Notation

The grammar is written in this notation, the same as the comments of the reference parser:

```
word        that word, written as is (a keyword or a symbol)
NAME        an identifier
"TEXT"      a string literal
x | y       x or y
[ x ]       x, optionally
x*          x, any number of times (also none)
x+          x, one or more times
( ... )     grouping
```

The complete grammar is collected in [Appendix A](#appendix-a-grammar). Examples use the language
itself; a line comment shows the output or the error.

---

## 3. Source code

A source file is UTF-8 text with the extension `.lar`. Line breaks are `\n` or `\r\n`. Lines are
numbered from 1, and every message of the compiler and every panic names a file and a line.

Each file is a module ([§21](#21-modules)).

---

## 4. Lexical elements

### 4.1 Comments

- `//` starts a comment that ends at the end of the line.
- `/*` starts a comment that ends at the next `*/`. Block comments do not nest.
- A comment that starts with `/**` is a documentation comment: it is a comment for the language, and
  tools may show it with the declaration that follows it.

### 4.2 Tokens

The tokens are identifiers, keywords, operators and punctuation, and literals. Spaces, tabs, line breaks
and comments separate tokens and are otherwise ignored, except where a rule names the line or the column
(platform directives, [§20](#20-platform-directives), and text blocks, [§4.8](#48-text-blocks)).

### 4.3 Identifiers

An identifier is a letter or `_` followed by letters, digits and `_`. Letters are the ASCII letters and
any non-ASCII Unicode letter.

- The names of types, methods, enum variants, functions, constants and modules must be ASCII.
  Variables, parameters and fields can use any letter (`let ñandú: int32 = 1;`).
- No identifier can contain `__` (two underscores in a row).
- By convention, primitive types are written in lowercase and every other type starts with an uppercase
  letter; and a member of a type that is not meant to be used from outside it starts with `_`
  (`_cache`). These conventions are not enforced.

### 4.4 Keywords

These words are reserved and cannot be identifiers:

```
as        break     case      catch     class     const     continue  default
else      enum      extends   false     for       function  heap      if
implements import   in        interface is        let       native
new       null      operator  override  private   public    return    self
static    struct    super     switch    synchronized          throw     throws
true      try       when      while     yield     c_include c_code
```

Also part of the language, but not reserved: `wait until`, `thread safe`, `released by`, `test`,
`export`, `type`, `lar` (only inside `c_code`) and `raw` (see the table below).

`new` and `private` are reserved but have no meaning: `new` is an error (objects are created with
literals), and `private` is an error that says it is not needed (what is not `public` is private).

These words have a meaning only in one place, and are identifiers everywhere else:

| Word | Where |
|---|---|
| `test` | before `function` at the top level ([§22](#22-tests)) |
| `export` | before `function` at the top level ([§19.9](#199-export-functions)) |
| `type` | after `native` |
| `c` | before a string in `= c "..."` ([§19](#19-c-interoperability)) |
| `raw` | immediately before `"""` ([§4.9](#49-raw-text-blocks)) |
| `released by` | in a `native type` ([§19.7](#197-resources)) |
| `wait until` | at the end of a method signature ([§18.3](#183-wait-until)) |
| `thread safe` | after a function type ([§18.4](#184-thread-safe-functions)) |

The two-word clauses (`released by`, `wait until`, `thread safe`) describe a declaration and read like
a phrase; keywords that start a declaration are a single token (`c_include`, `c_code`).

### 4.5 Operators and punctuation

```
+    -    *    /    %    &    |    ^    ~    !    <<   >>
==   !=   <    <=   >    >=   &&   ||   ??   ?    :    ::   ->
=    +=   -=   *=   /=   %=   &=   |=   ^=
(    )    [    ]    {    }    ,    ;    .    ..
```

`#when`, `#else` and `#end` are directives ([§20](#20-platform-directives)).

### 4.6 Numeric literals

```
decimal   = digit ( digit | _ )*
hex       = 0x hexdigit ( hexdigit | _ )*
binary    = 0b bindigit ( bindigit | _ )*
float     = decimal . decimal [ exponent ] | decimal exponent
exponent  = ( e | E ) [ + | - ] decimal
```

`_` separates digits and has no value: `1_000_000`. A literal has no sign; `-1` is the unary minus
applied to `1`.

An **integer literal** has no type of its own. It takes the type expected where it is written (the type
of the variable, of the parameter, of the other operand, of the field): any integer type, or a floating
type. The value must fit in that type, or it is an error (`let b: byte = 256;`). Where no type is
expected, it is `int32`; inside an `Any` ([§17](#17-any)) it is `int64`.

A **floating literal** takes the floating type expected (`float32` or `float64`), and is `float64`
where none is expected.

### 4.7 Character literals

`'x'` is the Unicode code point of exactly one character, as an integer literal: it takes the expected
type, and must fit in it (`let b: byte = '€';` is an error; `let c: int32 = '€';` is 8364).

Escapes: `\n`, `\t`, `\r`, `\0`, `\\`, `\'` and `\"`.

### 4.8 String literals

A string literal is written between `"` on one line. Escapes: `\n`, `\t`, `\r`, `\0`, `\\`, `\"`,
`\'` and `\$`.

`${expression}` inside a string literal is an **interpolation**: the value of the expression is written
there as text. Its type must be a number, `bool`, `String`, an enum (its variant's name is written) or
`Any` ([§17](#17-any)). Optionals cannot be interpolated. `\$` writes a literal `$`.

The text of a value:

| Type | Text |
|---|---|
| integers | decimal, with `-` if negative |
| `float32`, `float64` | the fewest significant digits that convert back to the same value of its type (`0.30000000000000004`; a `float32` `0.1` is `0.1`). Without an exponent when the decimal exponent is from −4 to 14, with one otherwise (`1e+20`, `1e-05`); `.0` is added when there would be no `.` or exponent (`2.0`). NaN is `nan`, the infinities `inf` and `-inf` |
| `bool` | `true` or `false` |
| `String` | itself |
| an enum | the name of the variant (`Circle`), without its data |
| `Any` | [§17.6](#176-text-of-an-any) |

A string literal without interpolation is a constant and needs no memory. One with interpolation
creates a new `String` ([§14](#14-memory)).

### 4.9 Text blocks

A text block starts with `"""` followed by a line break and ends with `"""`.

- Its content is the lines between them. The indentation common to all non-blank lines, and to the line
  of the closing `"""` when that line has nothing else, is removed from each line. Spaces at the end of
  each line are removed.
- If the closing `"""` is alone on its line, the text ends with a line break; if it ends the last line
  of text, it does not.
- `"` needs no escape. Escapes and interpolations work as in [§4.8](#48-string-literals).

### 4.10 Raw text blocks

`raw"""` followed by a line break starts a raw text block. It follows the indentation rules of
[§4.9](#49-text-blocks), but has no escapes and no interpolation: every character is itself.

If the content has three quotes in a row, the block is opened with more quotes and closed with the same
number: `raw""""` ... `""""`.

---

## 5. Types

```
Type  = ( qualifiedName | ( Type ) | ( [ Type ( , Type )* ] ) -> Type [ thread safe ] ) suffix*
suffix = [ ] | [ * ] | [ expression ] | ? | *
```

### 5.1 Primitive types

| Type | Values |
|---|---|
| `int8`, `int16`, `int32`, `int64` | signed integers of 8, 16, 32 and 64 bits, two's complement |
| `byte` (also `uint8`), `uint16`, `uint32`, `uint64` | unsigned integers of 8, 16, 32 and 64 bits |
| `float32`, `float64` | IEEE 754 binary32 and binary64 |
| `bool` | `true` and `false` |
| `void` | no value; only as the result of a function |

Primitive types need no memory, have no fields, and cannot be declared again.

### 5.2 `String`

A `String` is an immutable sequence of bytes, by convention UTF-8 text. Its `length` is its number of
bytes; `s[i]` is the `byte` at position `i`. Strings are compared by content. A string can be a
*view* of part of another one ([§14.8](#148-views)). Its methods are in [§23](#23-predeclared-names).

### 5.3 Arrays and lists

| Type | What it is |
|---|---|
| `T[N]` | an array of capacity `N` (a constant expression) and a length from 0 to `N`. It is a value: it lives with its variable and is copied whole on assignment |
| `T[]` | in a parameter: any array or list of `T`, borrowed without copying. Elements can be read and written, not added. In a variable declaration, `T[]` means `T[N]` with `N` taken from the initializer |
| `T[*]` | a list that grows. It lives in a memory ([§14](#14-memory)) |

Indexes are `int32` and start at 0. An index outside `0 .. length-1` is a panic.

### 5.4 Optional types

`T?` is `T` or `null`. A value of a type without `?` is never `null`. `T??` is not a type.

### 5.5 Structs, classes, interfaces, enums

Declared types: [§9](#9-structs-classes-interfaces-and-enums). Structs and enums are **values**: they
are copied on assignment and need no memory of their own. Class objects are **references**: assigning
one copies the reference, and the object lives in a memory. An interface value refers to a class object,
an interface literal or a lambda.

### 5.6 Function types

`(A, B) -> R` is the type of a lambda that takes an `A` and a `B` and returns an `R`.
`(A, B) -> R thread safe` is a function type that several threads may call at once
([§18.4](#184-thread-safe-functions)). `thread safe` applies to the nearest function type on its left;
parentheses choose another: in `(A) -> (B) -> C thread safe` it applies to `(B) -> C`, and in
`((A) -> (B) -> C) thread safe` to the outer type.

### 5.7 `Any`

A value of any of the types listed in [§17](#17-any), carrying its type at run time, or a table.

### 5.8 Memories

`byte[N]` and `byte[*]` are byte arrays and lists; a variable of one of these types becomes a **memory**
when it is used after `in` ([§14.5](#145-memories-of-your-own)).

### 5.9 C types

`native type` declares a type that comes from C ([§19.4](#194-native-types)); `T*` is a pointer to C
data ([§19.6](#196-pointers)). They exist only for C interoperability.

### 5.10 Type identity and assignability

Two types are identical when they are written with the same declaration and the same suffixes. Each
declared type is distinct, even when two declarations are equal; each `native type` is distinct, even
when the C types are the same.

A value of type `V` is **assignable** to a place of type `T` when:

1. `V` and `T` are identical;
2. `V` is a class and `T` is a class it extends, directly or not;
3. `V` is a class that implements the interface `T` (directly or through a parent class);
4. `T` is `V?`, or the value is `null` and `T` is optional or a pointer;
5. `V` is `S[N]`, `T` is `S[M]` and `N <= M` (the elements are copied);
6. `V` is any array or list of `S` and `T` is the parameter type `S[]`;
7. `V` is `F thread safe` and `T` is the plain function type `F`;
8. `T` is `Any` and `V` is a type an `Any` can hold ([§17](#17-any));
9. the value is a literal that adapts to `T` (§4.6, §4.7, object literals in §10.4, lambdas in §10.13).

There are no other conversions. Numeric conversions are written with `as` ([§10.10](#1010-conversions-as)).

---

## 6. Declarations and scope

### 6.1 The file

```
program = import* ( [ public ] declaration | #when block )*
```

A file is a list of imports followed by declarations. At the top level there are only declarations:
`const`, `let`, `function`, `test function`, `export function`, `struct`, `class`,
`synchronized class`, `interface`, `enum`, `c_include`, `c_code` and the `native` declarations
([§19](#19-c-interoperability)). Statements go only inside functions.

Statements end with `;`. Blocks are written between `{` and `}`.

### 6.2 Scope

- Top-level names are visible in the whole module, before and after their declaration, except as
  [§7.3](#73-initialization-of-global-variables) says for global initializers.
- A local variable is visible from its declaration to the end of its block.
- A local variable can have the name of a variable of an outer block, of a global, or of a module; the
  inner one hides the outer one until its block ends.
- Two declarations with the same name in the same scope are an error. There is no overloading: each name
  is one function.
- A type cannot have a method and a static function with the same name.
- `public` makes a top-level name visible to other modules ([§21](#21-modules)). Members of a type have
  the visibility of the type.

---

## 7. Constants and variables

### 7.1 Constants

```
const NAME : Type = expression ;
```

Constants are top-level declarations. Their type is a number, `bool` or `String`, and their value is
computed when compiling: the expression may use literals, other constants, operators, conversions and
`?:`. A constant integer can be the capacity of an array: `int32[SIZE]`.

### 7.2 Variables

```
let NAME : Type = expression ;
```

The type and the initial value are always written: there are no uninitialized variables. A variable can
be assigned again with `=` and the compound operators ([§11.2](#112-assignment)), except the variables of
a `for` and captured variables ([§10.13](#1013-lambdas)).

### 7.3 Initialization of global variables

Global variables are initialized before `main`, module by module: the modules a module imports first,
the main file last; within a module, in the order they are written. The initial values are created in
the default memory ([§14.4](#144-the-default-memory)).

The initializer of a global can use only the globals declared before it in its module and the globals of
other modules. It cannot call, directly or through other functions, a function that reads a global of
its module declared after it: that would read a variable not yet initialized, and it is an error.

When two modules import each other in a cycle, which of them is initialized first is
implementation-defined.

---

## 8. Functions

```
function [ TYPE . ] NAME ( [ parameter ( , parameter )* ] ) [ : Type ] [ in lives ]
    [ throws Type ] [ wait until ( expression ) ] ( block | ; )
parameter = NAME : Type [ in lives ]
lives     = default | self | NAME
```

- Every parameter has a type. A parameter is a local variable of the function: assigning it changes only
  the function's copy.
- Without `: Type`, the result is `void`.
- If the result is not `void`, every path through the body must end in `return expression`, `throw` or
  a call to `panic`. A `while (true)` without a `break` is a path that does not end.
- Functions are declared at the top level and inside types. Inside a body, functions are lambdas
  ([§10.13](#1013-lambdas)).
- A function is not a value. To pass one, it is wrapped in a lambda: `(x) -> { return add(x, 1); }`.
  The exception is a C function pointer ([§19.8](#198-c-function-pointers-and-callbacks)).
- `in` on a parameter says where its data lives ([§15.3](#157-saying-where-a-parameter-lives-in)). `in`
  after the result type is allowed only in `native function`s and says the result is a view tied to the
  receiver (`in self`).
- `throws`: [§16](#16-errors-and-panics). `wait until`: [§18.3](#183-wait-until).

### 8.1 Methods and `self`

A function declared inside a struct or a class is a method. Inside it, `self` is the receiver. A method
of a struct can modify `self`; the change is made on the variable it was called on.

### 8.2 Static functions

A static function belongs to a type: it has no `self` and is called as `Type.name(...)` (or
`module.Type.name(...)`), never through a value. It is declared inside the type with `static function`,
or outside it, in the same module, as `function Type.name(...)`; the two forms are the same. Static
functions exist in structs, classes, enums and native types; not in interfaces. They are not virtual and
cannot be overridden.

### 8.3 Operators

```
operator ( + | - | * | / | % | == | < ) parameters : Type block
```

A struct or a class can define the binary operators `+ - * / % == <` with one parameter, and the unary
`-` with none. From `==` the language derives `!=`; from `<` it derives `>`, `<=` and `>=`. `==` must
return `bool`, and so must `<`.

---

## 9. Structs, classes, interfaces and enums

### 9.1 Fields

```
let NAME : Type [ = expression ] ;
```

A field without a default value is required in every literal of its type. Default values of struct
fields must be constant (literals, constants, `null`, `[]`, enum values and struct literals made of
constants). Default values of class fields are evaluated for each object, inside the memory of that
object.

### 9.2 Structs

```
struct NAME { ( field | static ... | function ... | operator ... )* }
```

A struct is a value. Comparing two structs with `==` requires `operator ==`. A struct cannot be written
with `in` ([§14](#14-memory)): it lives in its variable.

### 9.3 Classes

```
[ synchronized ] class NAME [ extends NAME ] [ implements NAME ( , NAME )* ]
    { ( field | static ... | [ override ] function ... | native function ... | native let ... | operator ... )* }
```

- A class extends at most one class, and implements any number of interfaces.
- Fields and methods are inherited. A field cannot have the name of an inherited field.
- Every method is virtual: a call runs the method of the object's actual class.
- A method that redefines an inherited one is marked `override` and has exactly the same signature,
  the same `in` on its parameters and the same `throws`. `override` on a method that redefines nothing
  is an error, and so is redefining without `override`.
- `super.name(...)` calls the parent's version of a method.
- `==` between objects compares identity, unless the class defines `operator ==`.
- A value of a class is used where a parent class is expected. To go from a parent to a subclass, a type
  pattern is used ([§13](#13-patterns)).

`synchronized class`: [§18.2](#182-synchronized-classes).

### 9.4 Interfaces

```
interface NAME { ( function NAME parameters [ : Type ] [ throws Type ] ; )* }
```

An interface has only method signatures. A value of an interface type is one of:

1. an object of a class that declares `implements` it;
2. an **interface literal**, `{ method: lambda, ... }`, with a lambda for each method;
3. a **lambda**, when the interface has exactly one method.

A class that implements an interface defines each of its methods with the same signature, `in` and
`throws`.

### 9.5 Enums

```
enum NAME { [ variant ( , variant )* [ , ] ] }
variant = NAME [ ( parameter ( , parameter )* ) ]
```

An enum value is one of its variants; a variant can carry fields. Enums are values.

- A variant without data is written `E.V`. One with data is written `E.V { field: value, ... }`, in any
  order, or `E.V(value, ...)`, in the order of declaration.
- Enums whose variants have no data can be compared with `==` and `!=`. Enums with data are examined
  with patterns ([§13](#13-patterns)).
- An enum cannot contain a value of its own type, directly or through other values.

### 9.6 Native types

`native type NAME { ... }` (without `=`) declares the methods of a type that the compiler already knows
(`String`, `Any`). It is used by the standard library ([§23](#23-predeclared-names)); the native types
of C are in [§19.4](#194-native-types):

- `native function f(...);` without a body declares an operation the compiler implements;
- `native function f(...) = expression;` defines the method as that expression, usually a call to a
  native function;
- `native let name: T;` declares a value read without parentheses, which the compiler implements
  (`length`);
- `native operator [](i: int32): T;` declares indexing;
- ordinary `function`s and `static` functions can also appear.

`native function ... = expression;` can also be written in a class, and so can
`native let name: T = expression;`: a value read without parentheses (`sb.length`), computed by that
expression, of a number type or `bool`. A `native let` is never assigned, and calling it with
parentheses is an error.

---

## 10. Expressions

### 10.1 Evaluation order

Operands are evaluated **from left to right**, each one once:

- the left operand of a binary operator before the right one;
- the arguments of a call from the first to the last, after the receiver of a method call;
- the elements of a list literal, and the fields of an object literal **in the order they are
  written**;
- the parts of an interpolated string from left to right;
- in an assignment, the place (its object and its index) before the value.

`&&`, `||`, `??` and `?:` evaluate their right operands only when needed ([§10.7](#107-logical-operators),
[§10.9](#109-the-conditional-and-the-default-value)).

### 10.2 Precedence

From the lowest to the highest:

| Level | Operators | Associativity |
|---|---|---|
| placement | `e in m` ([§14.3](#143-placement-in)) | — |
| conditional | `c ? a : b` | right |
| default value | `??` | right |
| logical or | `\|\|` | left |
| logical and | `&&` | left |
| comparison | `==` `!=` `<` `<=` `>` `>=` `is` | left |
| bitwise or | `\|` | left |
| bitwise xor | `^` | left |
| bitwise and | `&` | left |
| shift | `<<` `>>` | left |
| additive | `+` `-` | left |
| multiplicative | `*` `/` `%` | left |
| conversion | `as` | left |
| unary | `-` `!` `~` `&` | right |
| postfix | call `f(...)`, field `a.b`, index `a[i]`, `x!`, reference `a::f` | left |

Bitwise operators bind more tightly than comparisons: `x & 1 == 0` is `(x & 1) == 0`.
`as` binds more tightly than comparisons: `n > MAX as int64` is `n > (MAX as int64)`. After `as T`, a
`?` followed by the start of an expression begins a conditional; followed by `)`, `;`, `,`, `??`, `==`
or another token that can follow a type, it makes `T` optional.

### 10.3 Operands and names

An operand is a literal, a name (a variable, a parameter, a constant, `self`), a qualified name
(`module.name`, `Type.name`, `Enum.Variant`), a parenthesized expression, an object or list literal, a
`switch` expression or a lambda.

### 10.4 Object literals

```
[ Type ] { [ field ( , field )* [ , ] ] }
field = NAME : expression | NAME | expression
```

`{ ... }` creates a value of the type expected where it is written; `Type { ... }` names the type. `NAME`
alone is short for `NAME: NAME`.

- For a struct or a class: every required field is given, each at most once, by name, in any order.
  Fields not given take their default value. `Dog {}` is a literal with no fields given.
- For an interface: an interface literal ([§9.4](#94-interfaces)).
- For an enum variant: `E.V { ... }` ([§9.5](#95-enums)).
- For `Any`: a table ([§17](#17-any)); entries without a name go by position.
- For a C struct: [§19.5](#195-native-structs-constants-and-variables).

There is no `new` and there are no constructors: a literal creates the value; when something must be
validated, a function does it and returns the literal.

### 10.5 List literals

`[a, b, c]` creates a `T[N]` or a `T[*]`, the type expected where it is written. `[]` is an empty one.
For a `T[N]`, the elements must fit in its capacity.

### 10.6 Arithmetic

The two operands of a binary operator have the same type; a literal adapts to the other operand
([§4.6](#46-numeric-literals)). `int32 + int64` is an error.

| Operator | Operands |
|---|---|
| `+ - * /` | numbers, or a type with that operator |
| `%` | integers, or a type with that operator |
| `& \| ^ << >>` | integers |
| unary `-` | numbers, or a type with `operator -()` |
| `~` | integers |

There is no `+` for strings: they are joined with interpolation.

**Integers.** The result of `+ - *`, unary `-` and `<<` is the exact result reduced modulo 2ⁿ, where n is
the width of the type: integers wrap around, signed and unsigned.

- `/` truncates toward zero; `%` has the sign of the left operand, and `(a / b) * b + a % b == a`.
- `/` or `%` by zero is a panic. For the minimum value of a signed type, `MIN / -1` is `MIN` and
  `MIN % -1` is `0`.
- In `a << n` and `a >> n`, only the low bits of `n` count: `n` modulo the width of `a`.
- `>>` on a signed integer keeps the sign (arithmetic shift); on an unsigned one it fills with zeros.

**Floating point** follows IEEE 754 with rounding to nearest. Division by zero gives an infinity or NaN;
it is not a panic.

### 10.7 Logical operators

`&&`, `||` and `!` take and give `bool`. `&&` and `||` do not evaluate their right operand when the left
one decides the result. Conditions of `if`, `while` and `?:` must be `bool`.

### 10.8 Comparison

- `==` and `!=` compare numbers, `bool`, `String` (by content), enums without data, objects (identity,
  or `operator ==`), structs that define `operator ==`, an optional with `null` or with a value of its
  type, and a pointer with `null`.
- `<`, `<=`, `>`, `>=` compare numbers, strings (byte by byte; a prefix goes first) and types that
  define `operator <`.
- `x is T` and `x is T name`: [§13.4](#134-is).

The result is `bool`.

### 10.9 The conditional and the default value

`c ? a : b` evaluates `c`, then only `a` if it is `true`, only `b` otherwise. The type of the result is
the type of the operand that is not a bare literal (a number or `null`); the other one adapts. With
`null` the result is optional. For two classes it is their nearest common class. Otherwise the two types
must be identical.

`x ?? y`, with `x` of type `T?`: the value of `x` if it is not `null`; otherwise `y` is evaluated and
is the result. `y` is a `T` (the result is `T`) or a `T?` (the result is `T?`).

`x!`, with `x` of type `T?`: the value of `x`; if it is `null`, a panic. On a value already known not to
be `null` ([§12](#12-optionals-and-narrowing)), `!` is allowed and does nothing.

### 10.10 Conversions: `as`

| From | To | Result |
|---|---|---|
| an integer | an integer | the value modulo 2ⁿ of the destination (`300 as byte` is `44`) |
| an integer | a floating type | the nearest value |
| a floating type | an integer | truncated toward zero; a value beyond the limits gives the nearest limit; NaN gives 0 |
| `float64` | `float32` and back | IEEE 754 conversion |
| `Any` | any type an `Any` holds | an optional: [§17.3](#173-reading-a-value-as) |
| a pointer | another pointer, or an opaque `native type` | the same address ([§19.6](#196-pointers)) |

`as` between other types is an error. There are no implicit conversions.

### 10.11 Calls, fields and indexes

- `f(a, b)` calls a function; `x.m(a)` calls a method; `x.f` reads a field. A field of an optional
  value cannot be read until it is known not to be `null` ([§12](#12-optionals-and-narrowing)).
- `x[i]` indexes an array, a list, a `String` (a `byte`, read only) or an `Any`.
- A call to a function that declares `throws` must be inside a `try` that catches its error type, or in a
  function that declares the same `throws` ([§16](#16-errors-and-panics)).
- `length` is read without parentheses on strings, arrays, lists, `Any` tables, memories and
  `StringBuilder`; `x.length()` is an error. What is a value is read without parentheses; what does
  something is called with them.

### 10.12 `switch` expressions

```
switch ( expression ) { case* }
case = ( case pattern ( , pattern )* | default ) [ when expression ] -> ( block | throw expression ; | expression ; )
```

The cases are tried in order; the first whose pattern matches and whose `when` condition holds is chosen.
A case gives its value with an expression, or with `yield expression;` from a block. `return` is not
allowed inside a `switch` expression. A case can `throw`.

All cases give values of one type, by the rules of `?:`; with a case that gives `null`, an optional.

Coverage: [§13.3](#133-coverage).

### 10.13 Lambdas

```
( [ parameter ( , parameter )* ] ) -> block
```

A lambda is an anonymous function value. Parameter types can be left out when the expected type gives
them. Its type is a function type, or an interface with one method.

- **Captures.** A lambda can use the local variables and parameters around it. It copies them when it is
  created; an object or a list is copied as a reference (the lambda sees the same object).
- A captured variable cannot be assigned or modified (not a field of a captured struct, not an element of
  a captured `T[N]`) before the lambda, after it, or inside it. Objects and `T[*]` lists reached through
  a captured reference can be modified.
- In a method of a class, a lambda can use `self`. In a method of a struct it cannot.
- A lambda cannot throw errors.
- A lambda cannot capture another lambda of its own type.
- A lambda can be returned and stored: it carries its copies.

### 10.14 Function references: `::`

```
:: NAME                 a function of this module
module :: NAME          a function of an imported module
variable :: NAME        a method of the object in a local variable or parameter
self :: NAME            a method of self
```

`a::f` is a lambda that calls `f` with its own parameters and returns what it returns: where the type
`(P1, ..., Pn) -> R` is expected, `Pages::show` is `(p1: P1, ..., pn: Pn) -> { return Pages.show(p1, ..., pn); }`
(without `return` when `R` is `void`).

- Its type comes from the place where it is used, like a lambda without parameter types: without an
  expected function type it is an error. The call it makes is checked like any call.
- `variable::f` and `self::f` capture the variable (or `self`) as a lambda does
  ([§10.13](#1013-lambdas)), with the same rules: what it captures must live as long as the place
  where the reference is kept ([§15](#15-the-lifetime-rule)).
- Only a module, a variable or `self` goes before `::` (or nothing, for this module): `a.b::f` is an error (keep `a.b` in a variable).
- A function that declares `throws` cannot be referenced: a lambda cannot throw.

---

## 11. Statements

```
statement = let ... | return [ expression ] ; | if ... | while ( expression ) block | for ... |
            break ; | continue ; | throw expression ; | yield expression ; | try ... | #when ... |
            block | switch ... | expression [ assign-op expression ] ;
```

### 11.1 Expression statements

An expression used as a statement must be a call (or a `switch` used as a statement).

### 11.2 Assignment

`place = value;` where the place is a variable, a field, an element (`x[i]`) or an entry of an `Any`.
The value must be assignable to the type of the place ([§5.10](#510-type-identity-and-assignability))
and must obey the lifetime rule ([§15](#15-the-lifetime-rule)).

`place op= value;`, for `op` among `+ - * / % & | ^`, is `place = place op value`, with the place (its
object and its index) evaluated **once**.

### 11.3 `if`

```
if ( expression ) block [ else ( if ... | block ) ]
```

Braces are required.

### 11.4 `while`

`while ( condition ) block` repeats the block while the condition is `true`.

### 11.5 `for`

```
for ( [ NAME , ] NAME in expression [ .. expression ] ) block
```

- `for (i in a..b)`: `i` takes the values from `a` to `b - 1`. `a` and `b` are integers of one type, are
  evaluated once before the first turn, and `i` has their type.
- `for (x in e)` and `for (i, x in e)`: each element of `e`, with its index (`int32`) when two names are
  given. `e` is an array, a list, a `String` (its bytes) or an `Any` (its positions).
  `for (name, v in t.fields)` goes over the named entries of an `Any` ([§17.4](#174-going-over-a-table)).
- Over a list, the length is read before each turn: elements pushed during the loop are visited.
- The variables of a `for` cannot be assigned in its body.

### 11.6 `break` and `continue`

They apply to the innermost `while` or `for`, also inside a `switch` within the loop.

### 11.7 `return`

`return;` in a `void` function; `return expression;` otherwise.

### 11.8 Blocks

`{ statement* }` is a block. What it declares exists only inside it, and it has its own memory, which is
freed when it closes ([§14.2](#142-automatic-memories)).

### 11.9 `switch` statements

A `switch` used as a statement has the same cases as the expression ([§10.12](#1012-switch-expressions)).
A case without braces must be a call; anything else goes in a block. There is no fall-through and no
`break` to end a case.

### 11.10 `throw`, `try`, `catch`

[§16](#16-errors-and-panics).

---

## 12. Optionals and narrowing

A local variable or a parameter of type `T?` is used as a `T` where it is known not to be `null`:

- inside `if (x != null) { ... }`, and in the `else` of `if (x == null) { ... } else { ... }`;
- after `if (x == null) { ... }` when that block always ends in `return`, `throw`, `break`, `continue`
  or `panic`: in the rest of the enclosing block;
- on the right of `x != null && ...` and of `x == null || ...`, also with several conditions joined
  (`a != null && b != null`);
- inside `while (x != null) { ... }`;
- in each operand of `c ? a : b`, according to `c`.

A `switch` on `x` with `case null` does not narrow `x` in its other cases. `is` gives a new name that is
already narrowed ([§13.4](#134-is)).

The knowledge ends where the variable is assigned again; the right side of that assignment still has
it. Fields are never narrowed: another function or thread could change them between the check and the
use.

---

## 13. Patterns

### 13.1 Forms

| Pattern | Applies to | Matches |
|---|---|---|
| a literal: `0`, `-1`, `2.5`, `'a'`, `"a"`, `true` | numbers, `String`, `bool` | an equal value |
| a constant: `MAX` | the same | an equal value |
| `V` | an enum | the variant `V` |
| `V { f, g: name }` | an enum | the variant `V`, binding its fields (`f` to `f`, `g` to `name`) |
| `V name`, `V { f } name` | an enum | the variant, with the whole value bound to `name` |
| `T name` | a class, an interface, `Any` | a value whose actual type is `T` or a subclass of `T`, bound as a `T` |
| `null` | an optional | `null` |
| `default` | anything | anything |

Fields of a pattern are named, not positional: order does not matter and fields not named are ignored.
A case can list several patterns: `case 1, 2, 3 ->`. `when expression` adds a condition to a case.

Over an `Any`, a type pattern matches the exact type of the value it holds: an integer kept as `int64`
does not match `int32`. `case Any t` matches a table.

### 13.2 Bindings

The names bound by a pattern exist only in its case, with the types of the fields or of `T`.

### 13.3 Coverage

- A `switch` on an enum, statement or expression, covers every variant, or has `default`. Cases with
  `when` do not count as covering.
- A `switch` expression on any other type has `default`.
- A `switch` on an optional covers `null` or has `default`.

### 13.4 `is`

`x is T` is `true` when `x` (an object, an optional object or an interface) is a `T` or a subclass of
`T`. `x is T name` also binds `name`, as a `T`, where the test is known to be true: inside the `if`, on
the right of `&&`, in the corresponding operand of `?:`, and after `if (!(x is T name)) { ... }` when
that block always leaves.

---

## 14. Memory

### 14.1 Values that need memory

Numbers, `bool`, structs, enums, `T[N]` arrays and string constants need no memory: they live in their
variable, field or element. Class objects, `T[*]` lists, strings created at run time (interpolation, the
methods that create text), `Any` tables, interface literals and threads need memory: each one is created
**in a memory**, and a memory is freed whole.

There is no garbage collector, and nothing is freed one by one.

### 14.2 Automatic memories

Where a value is created is decided by the place it goes to, unless the program says otherwise with `in`:

| What is created | Where it lives | When it is freed |
|---|---|---|
| a value not stored anywhere: an argument, part of an expression, the text of a `println` | the temporary memory of the statement | at the end of the statement |
| the value of a local variable (initialized or assigned) | the memory of the variable's block | when the block ends; in a loop, at the end of each turn |
| a value pushed to a list, stored in a field, an element or a table | the memory of that list, object or table | with it |
| a value returned by a function that creates it | the memory the caller gives ([§14.7](#147-results-of-functions)) | according to the caller |
| the initial value of a global variable | the default memory | never |

A memory is freed on **every** exit of its block: at its end, by `return`, `break`, `continue`, and when
an error leaves it.

### 14.3 Placement: `in`

```
expression in ( heap | default | byte [ expression ] | NAME )
```

`e in m` creates the value of `e` in the memory `m` instead of its automatic one:

| Placement | The value lives |
|---|---|
| `in m`, `m` a local memory | until the end of the block that declared `m` |
| `in m`, `m` a global memory | the whole program |
| `in default` | the whole program ([§14.4](#144-the-default-memory)) |
| `in byte[N]` | in a new buffer of `N` bytes of the current block, until it ends; text that does not fit is cut |
| `in heap` | only in the declaration of a memory ([§14.5](#145-memories-of-your-own)) |

`in` applies only to expressions that create a value that needs memory, including calls that return one.
On a struct or on a value that already exists it is an error.

### 14.4 The default memory

The default memory lives for the whole program and is never freed. Nothing goes there unless the program
says `in default`, except the initial values of globals. Assigning a new value to a global requires a
value that lives in it ([§15.2](#155-where-the-rule-is-checked)). The default memory is the only memory
shared between threads, and creating values in it is safe from any thread.

### 14.5 Memories of your own

```ts
let a: byte[4096] = [];             // in the function's frame (static storage, if global)
let b: byte[1024] = [] in heap;     // asked from the system
let c: byte[*] = [] in heap;        // grows by asking the system for more blocks
```

- A `byte[N]` without `in heap` is in the function's frame, or static if it is global. `in heap` asks
  the system; with `in heap`, `N` can be any `int32` expression.
- A `byte[*]` memory requires `in heap`.
- A memory is used after `in`, passed as a parameter of type `byte[*]`, and queried: `m.length` (bytes in
  use), `m.capacity`, `m.peak` (the most ever in use).
- A memory is not a value: it is not assigned, not returned, not stored in fields, not captured by
  lambdas (lambdas can use only global memories and memories they declare).
- A `byte[N]` used as a memory cannot also be used as data.
- A fixed memory that is full: creating a value there is a panic, and `push` to a list there returns
  `false`.

### 14.6 Limiting and compacting a memory

`std.memory` has two functions that act on a memory itself, so their first argument is the memory's
name (not a parameter that receives a memory):

- `Memory.limit(m, bytes)`: `m` (a `byte[*]` memory) may obtain at most `bytes` from the system; a
  creation that would need more is a panic that names `m`. `0` removes the limit. A fixed memory
  (`byte[N]`) is an error: its size is its limit.
- `Memory.compact(m)`: what the variables of `m` reach inside `m` is copied to new storage of `m`, each
  value once (shared values stay shared, cycles stay cycles); the variables are given the copies; the old
  storage is freed. Values that live in other memories are not copied. `m.length` then counts only what
  is alive; `m.peak` is kept.

`Memory.compact(m)` is an error when:

1. `m` is not a `byte[*]` memory declared in a function (a global memory, a parameter, a fixed memory,
   or `default`);
2. a local variable visible at the call, of a type with references ([§14.1](#141-values-that-need-memory)),
   lives in the memory of `m`'s block or of a block inside it, and not in `m`: it could point into `m`
   and would be left pointing to freed storage;
3. data that lives in the memory of `m`'s block (not in `m`) is stored in `m` anywhere in its block;
4. a variable of `m` holds, or may hold through a class, a struct, an enum or `Any`, a lambda, an
   interface value, a synchronized object or a thread;
5. the call is inside a `for` over a list, a table or a text, between the call and `m`'s block.

A memory that holds threads, synchronized objects or resources when it is compacted is a panic. A memory
other than `default` belongs to one thread ([§18.5](#185-what-a-thread-can-use)), so no other thread
uses it while it is compacted. C code must not keep a pointer it received after the call returns
([§19.6](#196-pointers)); compacting relies on it.

### 14.7 Results of functions

A function that returns a value it creates (in the `return` expression, or in a local variable that is
returned) creates it **directly in the memory of the caller**, without copying. The caller's memory is
the automatic one for the place the call goes to, or the one written with `in`: `let`, its block;
`push`, the list; a field, the object; a `return`, the memory of its own caller.

A function that returns a value that already existed (a parameter, a field, an element, part of one of
them) creates nothing, and the result lives where it already lived.

When a function sometimes creates its result and sometimes returns an existing one, the result is treated
as created: it lives in the caller's memory.

The arguments that can become part of the result (for example a string the function returns a view of)
are created where the result goes; the others are temporaries of the statement.

### 14.8 Views

Some operations return a **view**: a value that shares the storage of another one, without copying.
`substring`, `trim`, `trimStart`, `trimEnd`, `bytes` and `StringBuilder.toString` return views. A view
lives as long as the value it shares, and the lifetime rule treats it as that value.

### 14.9 What freeing a memory does

Before the storage of a memory is reclaimed, every thread created in it is joined
([§18.1](#181-thread)) and every resource stored in it is released ([§19.7](#197-resources)).

---

## 15. The lifetime rule

### 15.1 The rule

> A value cannot be stored in a place that lives longer than the memory the value was created in.

The compiler checks it when compiling; there is no check at run time. This section defines the check
exactly: every expression has a **region** (§15.2–§15.4), regions are ordered by how long they live
(§15.3), and at each place where a value is stored the region of the value must live at least as long as
the region of the place (§15.5). What a call returns is decided by two properties of the function that
is called, computed before any body is checked (§15.6).

A program that breaks the rule is an error, which says where each side lives and suggests `.clone()` or
an `in` on a parameter.

### 15.2 Regions

| Region | What it is |
|---|---|
| **static** | lives the whole program: literals, constants, values that need no memory, globals, the default memory |
| **local(B)** | the memory of the block `B`, or of a memory declared in `B`; the temporary memory of a statement is the local region of that statement |
| **caller(p)** | data that came to the function through its parameter `p` (also `self`, and a memory parameter) |
| **caller(result)** | the memory the caller gives for the result of the function ([§14.7](#147-results-of-functions)) |
| **caller-any** | data of the caller, through a parameter that is not known |
| **meet(r₁, …, rₙ)** | the shortest of those regions: what lives as long as each of them |

A **reassigned variable** has, as its region, the meet of the regions of every value it receives in the
function, in any order and in any turn of a loop. That region is known when the whole function has been
read; the checks that involve it (§15.5) are made then.

### 15.3 Which region lives longer

*r outlives s* ("what is in r lives at least as long as what is in s") is defined by these rules, and by
nothing else:

1. **static** outlives every region. No region other than static outlives static.
2. **local(A)** outlives **local(B)** when `A` is `B` or a block that encloses `B`.
3. **caller(p)**, **caller(result)** and **caller-any** outlive every **local** region of the function.
4. **caller(p)** outlives **caller(q)** only when `p` and `q` are the same parameter. Data that came
   through two different parameters has no known order: storing one in the other needs `clone()` or
   `in` ([§15.7](#157-saying-where-a-parameter-lives-in)).
5. **caller(p)** and **caller-any** outlive **caller-any**.
6. When the function may return data of its arguments (*flows*, §15.6), its parameters outlive
   **caller(result)**: the caller checks, at the call, that the arguments live as long as the place the
   result goes to.
7. A **meet** outlives a region when each of its parts does; a region outlives a meet when it outlives one
   of its parts.

The **meet of two regions** is the one of them that the other outlives. When neither outlives the
other, it is the local one, if one is local, and caller-any otherwise.

### 15.4 The region of an expression

| Expression | Region |
|---|---|
| a literal, a constant, a value whose type needs no memory (numbers, `bool`, enums and structs of them) | static |
| a global variable | static |
| a local variable | the region of its value (§15.2 for reassigned ones) |
| a parameter `p` | caller(p); with `in default`, static; with `in q`, the region of `q`; with `in self`, the region of `self` |
| `self` | caller(self) |
| `a.f`, `a[i]`, the read of an entry of an `Any` | the region of `a` |
| a view of `a` (`substring`, `trim`, `bytes`, `toString` of a `StringBuilder`, the elements of `split`) | the region of `a` |
| a value created here: an object, list or table literal, an interpolated string, `clone()`, a method of `String` or `Any` that creates text or lists | the region of the place it is created in ([§14.2](#142-automatic-memories)); with `in`, the region of that memory |
| a call to a function that **creates** its result (§15.6) | the meet of the region of the place the result goes to and, for each parameter the result **flows** from, the region of its argument |
| a call to a function that does not create its result | the meet of the regions of the arguments the result flows from, or static when there are none |
| a method call | as a call, with the object as one more argument (`self`) |
| `c ? a : b`, `x ?? y`, a `switch` | the meet of the regions of the values it can give |
| `x!`, `x as T` | the region of `x` |

The region of the place a value is created in follows [§14.2](#142-automatic-memories): the temporary
memory of the statement is local(statement); the value of a local variable, local(its block); a value
stored in an object, a list or a table, the region of that object, list or table; a value returned,
caller(result); the initial value of a global, static; `in m`, local(B) for a memory `m` declared in the
block `B`, or static for a global memory.

### 15.5 Where the rule is checked

At each of these points, the region of the value must outlive the region of the place:

| Point | The place |
|---|---|
| `x = v`, `let x: T = v` | the region of `x`'s block (local variables are checked against the block that declares them) |
| `a.f = v`, `a[i] = v`, `t.name = v` | the region of `a` (or `t`) |
| `list.push(v)`, the elements of a literal, the fields of an object literal | the region of the list or of the object |
| `return v` | caller(result); a value of a local memory or of a `byte[N]` buffer is an error |
| a global `g = v` | static |
| an argument for a parameter with `in` | the region the `in` names, as seen from the caller (§15.7) |
| the data carried by an error | static |
| the arguments the result flows from, at a call | the region of the place the result goes to (rule 6 of §15.3) |

Values whose type needs no memory are never checked.

### 15.6 What a call returns: *flows* and *creates*

Before any body is checked, the compiler computes two properties of every function and method. Both are
**conservative**: when unsure, the property is true, and every `return` inside the function is still
checked against its own regions, so a conservative answer can make the compiler reject a program but
never accept a wrong one.

**flows(p)**: the result may point to data of the parameter `p` (or of `self`, for a method). A name is
*in the flow* when:

1. it appears in the value of a `return`;
2. it appears in the initial or assigned value of a variable that is in the flow, in the collection of a
   `for` whose variable is in the flow, or in the subject of an `is` or a `switch` whose bindings are in
   the flow;
3. it is passed to a method of a value in the flow that can keep it (`push`, and methods not known to
   keep nothing).

These parts do not bring their names into the flow: an index or a key (`a[i]`, the `i`), the parts of an
interpolated string (they are copied into new text), numbers read from data (`s.length`, a numeric
field), and the arguments of a call for parameters the result of that call does not flow from. `flows(p)`
is true when `p` is in the flow of the function's body. Since a call can make its caller's result flow
from an argument, the property is computed again for every function until nothing changes.

**creates**: the result may be new data, created in the memory the caller gives. A function creates its
result when one of these values *creates*: the value of a `return`, or the value given to a variable that
is in the flow. A value creates when it is:

- an interpolated string, an object, list or table literal, a lambda, `clone()`;
- an arithmetic operator (it may be an `operator` method that creates its result), or a unary `-` on
  something other than a literal;
- a call to a function that creates, or to one whose result flows from an argument that creates;
- `c ? a : b`, `x ?? y` or a `switch` with a branch that creates;
- when the result is an `Any`: also a variable, a field or an element (a struct or an enum put in an `Any`
  is copied).

A value does not create when it is a literal without interpolation, `null`, a comparison, an `is`, a
variable, a parameter, `self`, a field or an element (outside an `Any`), or a value placed with `in`
(it says where it lives). The property is computed again until nothing changes.

Fixed answers:

- a method of an interface: flows from every argument and from `self`, and creates (any class may
  implement it);
- a native function: when its first parameter is a memory ([§19.3](#193-native-functions)), it
  creates and its result flows from nothing; otherwise it does not create, and its result may flow from
  every argument (C may return a pointer into one of them);
- a `native function` with `in self` in its result flows from `self`.

What they decide:

- A function that **creates** receives from each call the memory its result goes to: the result lives
  where the caller puts it ([§14.7](#147-results-of-functions)). A function that sometimes creates and
  sometimes returns existing data creates.
- A function whose result **flows** from a parameter makes the caller check, at each call, that the
  argument lives as long as the place the result goes to.
- A function that neither creates nor flows returns static data (or data that needs no memory).

### 15.7 Saying where a parameter lives: `in`

| Parameter | Its region inside the function | The caller passes |
|---|---|---|
| `k: T in p` | the region of parameter `p` | a value whose region outlives the region of its argument for `p` |
| `k: T in self` | (in a method) the region of `self` | a value whose region outlives the object's |
| `k: T in default` | static | a value whose region is static; a value created in the call is created in the default memory |
| `k: T in m` | the region of the memory parameter `m` | a value whose region outlives that memory |

`in q` follows `q`'s own `in`: in `a: T in b, b: T in default`, `a` is static. Parameters that live in each
other in a circle are an error. `in` applies only to parameters whose type needs memory; it is not allowed
on a memory parameter, on native functions (except `in default` on a callback, [§19.8](#198-c-function-pointers-and-callbacks)) or on export functions. A method that overrides another, or
implements an interface, repeats the same `in`.

### 15.8 `clone()`

`x.clone()` makes a complete, independent copy of `x` in the memory of its destination (or the one given
with `in`): an object with everything it refers to, a list with its elements, a table with its contents,
a string. Its region is the region of that place. Cycles between objects are preserved. Objects of
`synchronized` classes and threads inside a cloned table are shared, not copied.

`clone()` exists for every type; on values that need no memory it is a copy. It does not exist for
interfaces, lambdas and `T[]` parameters, nor for objects that hold a resource
([§19.7](#197-resources)).

---

## 16. Errors and panics

### 16.1 Errors: `throws`, `try`, `catch`

An expected failure is an **error**: a value of an enum, thrown with `throw` and announced in the
signature.

```
function NAME ( ... ) [ : Type ] throws EnumType ...
throw expression ;
try block ( catch ( qualifiedName NAME ) block )+
```

- A function declares at most one error type, an enum, with `throws`.
- `throw e;` ends the function with the error `e`, whose type must be the declared one.
- A call to a function that declares `throws E` must be in a `try` with a `catch (E name)`, or in a
  function that declares `throws E`, where the error continues to the caller. Otherwise it is an error.
- A `try` has one or more `catch`, one per error type. An error not caught continues outward.
- Methods of classes and interfaces can declare `throws`; an `override` and an implementation declare
  the same one.
- The data an error carries must live the whole program: literals, constants, or values created
  `in default` (for example `why.clone() in default`).
- An error is a value that is returned. There are no hidden jumps: memories are freed as the error goes
  up, as on any other exit.
- Lambdas cannot throw.

### 16.2 Errors in `main`

`main` can declare `throws`. If an error reaches the end of `main`, the program writes
`uncaught error: Type.Variant` and ends with exit code 1.

### 16.3 Panics

A panic is a failure of the program, not an expected situation. It cannot be caught. The program writes
a message to the error output and ends with exit code **101**:

```
panic [src/main.lar:4]: index 5 out of range (length 3)
```

The causes:

| Cause | Message |
|---|---|
| an index out of range | `index I out of range (length N)` |
| `/` or `%` by zero (integers) | `division by zero` |
| `!` on `null` | `'!' used on a null value` |
| `pop()` on an empty list | a message saying so |
| a fixed memory is full when creating a value | `memory is full` |
| the system gives no more memory | `out of memory: ...` |
| a field read through a null C pointer | a message saying so |
| using a released resource | `a released T was used` |
| adding or removing entries of a table while it is gone over | a message saying so |
| writing to an `Any` that is not a table | a message saying so |
| `panic(message)` | the message |

`panic(text)` stops the program on purpose. A function can end with `panic(...)` instead of `return`.

---

## 17. Any

An `Any` holds a value whose type is known at run time: a number, a `bool`, a `String`, `null`, an
object, a struct, an enum, or a **table**. It cannot hold `T[*]` lists, lambdas or interfaces.

### 17.1 Tables

A table has two parts: entries **by position** (0, 1, 2…) and entries **by name**, which keep the order
they were added in.

```ts
let config: Any = { "web", "api", name: "server", limits: { max: 100 } };
```

- A table lives in a memory, like an object. Tables inside it, and values assigned or pushed to it, live
  in its memory.
- Integer literals in an `Any` are `int64`, floating literals `float64`, unless converted:
  `0xFF as byte`.
- An object is held by reference. A struct or an enum is copied into the table's memory.

### 17.2 Reading and writing

- `t.name` and `t["name"]` read an entry by name; `t[i]` by position. Reading an entry that does not
  exist, or reading inside a value that is not a table, gives `null`. Reading never panics.
- `t.name = v`, `t["name"] = v` and `t[i] = v` write an entry; writing a new name adds it. Writing to a
  value that is not a table is a panic.
- `t.push(v)` adds at the end of the positions.
- `length`, `push` and `fields` are names of the language on an `Any`; entries with those names are
  reached with brackets: `t["length"]`.

### 17.3 Reading a value: `as`

`v as T` gives a `T?`: the value, if `v` holds a value of that type, or `null`. Integers convert to any
integer type in which they fit (otherwise `null`), and numbers to floating types. `as` with a class
gives the object if it is of that class or a subclass.

### 17.4 Going over a table

`for (i, v in t)` goes over the positions; `for (name, v in t.fields)` over the named entries, in
order. During the walk values can be changed, but adding or removing entries is a panic.

### 17.5 Methods

| Method | Result |
|---|---|
| `length` | the number of positions |
| `push(v)` | adds at the end |
| `contains(x)` | `true` if `x` is the name of an entry or equal to a value by position (numbers by value, `5 == 5.0`) |
| `containsKey(name)` | `true` if there is an entry with that name |
| `remove(name)` | removes an entry; `true` if it existed |
| `removeAt(i)` | removes a position; the following ones move back |
| `clear()` | removes everything |
| `removeIf(f)` | removes the values (by position and by name) for which `f` gives `true`; returns how many |
| `clone()` | [§15.4](#158-clone) |

Removing entries does not free memory: their storage is freed with the table's memory.

### 17.6 Text of an `Any`

Interpolating an `Any` writes its value; a table as `{a, b, name: value}`, with strings in quotes; an
object or a struct as `<TypeName>`.

---

## 18. Threads

### 18.1 `Thread`

`Thread` is a predeclared class ([§23](#23-predeclared-names)) with the fields `run` (a `Runnable`: a
lambda or a `synchronized` object that implements it) and `name`, and the methods `start()` (once) and
`join()`.

A thread lives in a memory like any object. **When its memory is freed, the thread is joined first**:
a thread never outlives its memory, and everything it uses exists while it runs. Threads in the default
memory are joined when the program ends. The language creates no thread that the program does not
create.

### 18.2 Synchronized classes

A `synchronized class` protects its data with a lock: each method takes the lock when it starts and
releases it on every exit. The lock is re-entrant: a method can call another method of the same object.

- Its fields are used only inside its methods, through `self`.
- Its methods take and return only values ([§18.5](#185-what-a-thread-can-use)), objects of synchronized
  classes and `thread safe` functions: never lists, ordinary objects or `Any`.
- It extends only another synchronized class, and only a synchronized class extends it. The object has a
  single lock, taken by every method, the inherited ones too.
- Inside a lambda of its methods, `self` is used only to call its methods (`self.m()`, `self::m`), which
  take the lock; its fields are not used there, since the lambda could run later, without the lock.

### 18.3 `wait until`

A method of a synchronized class can declare `wait until (condition)` after its signature. A call waits,
without the lock and without using the processor, until the condition holds; then the body runs with the
lock held and the condition true. Whenever a method of the object ends, the waiting calls check their
conditions again; there is no `notify`. The condition can use `self` and the parameters. `wait until`
appears only on methods of synchronized classes.

### 18.4 `thread safe` functions

A value of type `F thread safe` can be called by several threads at once.

- A lambda written where a `thread safe` type is expected is checked like the `run` of a thread
  ([§18.5](#185-what-a-thread-can-use)), and the functions it calls cannot modify globals.
- A `thread safe` value can be shared between threads and passed to synchronized methods.
- A `thread safe` function is assignable to the plain type; a plain function value is not assignable to
  the `thread safe` type (only a lambda written there, which is checked).

### 18.5 What a thread can use

The `run` lambda of a thread, and a `thread safe` lambda, can use from outside only:

1. values, which they receive copied: numbers, `bool`, `String`, and structs, enums and `T[N]` made of
   them;
2. objects of synchronized classes, and objects of classes without fields (neither the class nor a class
   that extends it has fields, and it is not a `Thread` or a `StringBuilder`): they have no state to change;
3. `thread safe` functions.

The check follows every function they call, at any depth: if one modifies a global variable or uses a
global memory, it is an error. Globals that are never modified can be read.

Memories other than the default one belong to one thread. The language does not prevent deadlocks
between synchronized objects.

---

## 19. C interoperability

### 19.1 `c_include`

`c_include "<header.h>";` or `c_include "file.h";` adds an `#include` to the generated C.

### 19.2 `c_code`

```
c_code { C text }
```

The C text is copied to the generated C, after the headers and before the program. Braces inside C
strings, characters and comments do not count toward the closing brace. Inside it, **`lar"NAME"`** (or
`lar"module.NAME"`) is replaced by the C name of that Larimar function, type or global variable; a name
that does not exist is a compile error. The prototypes of the functions named this way whose types are
numbers, `bool`, `String` or `void` are written before the `c_code`. Otherwise the C must use only the
doors of §19: `native` declarations (C seen from Larimar), `export function`s (Larimar seen from C) and
`lar"..."`; the names the compiler generates for everything else are not part of the language. Code in
`c_code` is outside every guarantee of this document.

### 19.3 Native functions

```
native function NAME ( [ parameter ( , parameter )* [ , ... ] ] ) [ : Type ] [ = C ] ;
C = NAME | "C TEXT"
```

A `native` declaration names something of C. The name on the left is the Larimar one; after `=` comes
the C one: a name, or C text in quotes when it is not a plain name (`"(fio_start)"`, a cast). Without
`=`, the C name is the same.

- Parameter and result types: numbers, `bool`, `String` (a `const char*`), `String?` parameters (`null`
  is `NULL`), native types and their optionals, C structs, pointers, `T[]` of numbers or `bool`, and
  `byte[*]` memories. `...` allows variable arguments.
- A `T[]` of numbers or `bool` is passed as two C arguments: a pointer to the elements and their count.
- A result of type `String` must be a zero-terminated text that keeps existing (static, or created in a
  memory the function receives). `String?` turns `NULL` into `null`.
- A `public native function` keeps its C name inside a module.
- A memory as the **first** parameter is not written in the call: the function receives the memory of
  the call, so its result lives where the caller says ([§14.7](#147-results-of-functions)). In C it is an
  `RtMem*`, and `rt_mem_alloc(m, bytes, 0)` reserves zeroed bytes in it. The C may use the memory only
  during the call. A memory in another position is passed explicitly.
- A parameter of type `Context` is not written in the call either: it carries the function given in the
  callback parameter ([§19.8](#198-c-function-pointers-and-callbacks)).
- When the module has no `c_include` and no `c_code`, the compiler writes the C prototype of each native
  function whose C is a plain name.
- A native function has no body. In the standard library, `std.memory` declares `limit` and `compact` as
  native functions that the compiler writes itself.

### 19.4 Native types

```
native type NAME [ released by NAME ] ;                                   an opaque pointer (void*)
native type NAME = CTYPE [ released by NAME ] ( ; | { member* } )         a C type
native type NAME = ( Type , ... ) -> Type ;                               a pointer to a C function (§19.8)
CTYPE  = NAME *...  |  "C TYPE"
member = let NAME : Type [ = NAME ] ;
       | native function NAME parameters [ : Type ] [ in lives ] [ throws Type ] = ( C | expression ) ;
       | native let NAME : Type = ( C | expression ) ;
       | function ...  |  static function ...  |  static native function ... = C ;
```

Each native type is distinct, even when two declarations are equal. The members of a C type:

- **`let`** declares a field of the C struct the type points to, read and written with `x.f` (C's `x->f`);
  after `=` comes its C name when it is another. A type with fields must be a pointer (`= c_struct*`).
- **`native function m(...) = C;`** calls that C function with `self` as its first argument, then the
  arguments; before `self` goes only the memory of the call, when the first parameter is one. A parameter
  of type `Context` is not part of the method. Any other expression after `=` is Larimar, as in a class.
- **`native let x: T = C;`** is the same with no arguments, read without parentheses.
- **`function`** is a method written in Larimar; `self` is the C value.
- **`static native function f(...) = C;`** calls that C function without `self`; `static function` is
  written in Larimar. Both are called as `NAME.f(...)`.

A native type with members is declared outside `#when`. The methods of a type the compiler knows
(`native type String { ... }`, without `=`) are declared only in the standard library ([§9.6](#96-native-types)).

### 19.5 Native structs, constants and variables

```
native struct NAME [ = C ] { ( let NAME : Type [ = NAME ] ; | function ... | static function ... )* }
native const NAME : Type [ = C ] ;
native let NAME : Type [ = NAME ] ;
```

A native struct is a C struct, by value. It declares only the fields the program uses; the C definition
(from a header or `c_code`) gives the layout. Its fields are numbers, `bool`, native types, pointers, C
structs and `String`; after `=` comes a field's C name when it is another. A `String` field is a C text,
read-only, and a view of the C storage. A native struct is used like a Larimar struct (literals, field
access, copies, lists, methods written in Larimar); fields not given in a literal are zero.

`native const` names a C constant, a macro or a C expression (`= "sizeof(struct stat)"`), read-only; it
can be a `String`. `native let` names a C variable that can be read and assigned; it cannot be a `String`.

### 19.6 Pointers

`T*` is a pointer to C data: a number, `bool`, a C struct, a native type or another pointer.

- `p.f` reads or writes a field of the struct `p` points to; on a `null` pointer it is a panic.
- `&x` is the address of a local variable and is allowed **only** as an argument of a native function
  (also as `&x as U*`). So the address never outlives the call.
- An array passed where C asks for a `T*` is passed as a pointer to its elements.
- Pointers can be compared with `null` and converted with `as` ([§10.10](#1010-conversions-as)). They
  cannot be indexed, and there is no pointer arithmetic.
- Pointers refer to C storage and are outside the lifetime rule.

### 19.7 Resources

`native type T ... released by f` declares a **resource**: a C value that `f` releases.

- A resource lives in a memory like any value; when the memory is freed, `f` is called on it.
- `release(x)` releases it now. Releasing twice does nothing; using a released resource is a panic.
- The functions that create it return `T?`: a `NULL` pointer, `-1` (also `INVALID_HANDLE_VALUE`) or a
  negative descriptor arrives as `null`. A Larimar function that returns what such a function makes
  creates it where its caller says.
- `f` takes exactly one `T`, and only `release` and the freeing of memories can call it.
- An object that holds a resource cannot be cloned.
- If `f` exists only on some platforms, so does the resource.

### 19.8 C function pointers and callbacks

A value of a `native type F = (A) -> R` is a C function: a `native function` or an `export function`
with exactly that signature, or a value that C returns. It can be passed, stored and called like a
function.

`Context` (declared by `std.lang`) is C's `void*` that a C function gives back to its callback. When `F`
has one parameter of type `Context`, a native function that takes an `F` and a `Context` also takes
**any Larimar function** of the same signature without the `Context`, lambdas included, with what they
capture:

- the C function receives a function of C made by the compiler, and the Larimar function as the Context;
- an `export function` or a `native function` of type `F` goes as it is, with `NULL` as the Context;
- without `in`, C may call it only during the call; with **`in default`** on the parameter, C may keep it,
  and what it captures must live as long as the whole program;
- the Larimar function cannot return `String`, and `F` cannot carry resources.

A member of a native type that calls a C function taking such a callback takes the Larimar function.

### 19.9 Export functions

`export function NAME(...)` makes a Larimar function callable from C, with exactly its own name (also
inside a module) and a plain C signature.

- Parameters and results: numbers, `bool`, `String` parameters (a `const char*`), native types and C
  structs. It cannot return `String`, declare `throws`, use `in`, take memories, classes, lists or `Any`,
  or be `main`.
- Each call from C has its own temporary memory, freed when it returns.
- If C calls it from another thread, the thread rules of [§18](#18-threads) do not apply to that call.

---

## 20. Platform directives

```
#when PLATFORM  body  ( #when PLATFORM  body )*  [ #else  body ]  #end
PLATFORM = windows | macos | linux | unix
```

A directive chooses code when the C is compiled (C's `#if`), not when the program runs.

- `unix` is every platform but `windows`.
- Each directive is alone on its line; only a comment can follow it. The `#when`, `#else` and `#end` of
  one choice start in the same column; a directive further to the right belongs to a nested choice.
- A later `#when` is the next alternative (C's `#elif`). A branch that an earlier one already covers is
  an error (`#when macos` after `#when unix`).
- The body is a list of statements of the surrounding block, without braces. At the top level, the body
  contains only `c_include` and `native` declarations (without members), and `#else` follows only `#when windows` or
  `#when unix`.
- The compiler checks every branch, whatever the platform it runs on.
- A name declared in every branch, with the same type, exists after `#end`. A name declared in only some
  branches exists only inside them; without `#else`, no name survives `#end`.
- A declaration that exists only on some platforms can be used only inside a `#when` of those platforms.
- A type can be declared once per platform, when the declarations cover every platform.

---

## 21. Modules

### 21.1 Files and names

Each file is a module. Its name is its path, from the folder of the main file, without `.lar`, with `.`
between folders: `src/geo/shapes.lar` is `geo.shapes`. A module `a` and the modules in the folder `a/`
are separate modules. Modules of the standard library start with `std.`. Nobody can import the main
file.

### 21.2 `public`

What a module declares is private to it unless marked `public`. A public type makes all its fields and
methods visible.

### 21.3 `import`

```
import NAME ( . NAME )* [ as NAME | { NAME ( , NAME )* } ] ;
```

Imports go at the start of the file.

| Form | Names are used as |
|---|---|
| `import geo.shapes;` | `shapes.area(s)`: the last part of the module name is the prefix |
| `import geo.shapes as g;` | `g.area(s)` |
| `import geo.shapes { Shape, area };` | `Shape`, `area`, without prefix |

Through a prefix every public name is reached: functions, constants, variables, types
(`shapes.Shape`, `extends shapes.Figure`, `catch (shapes.ShapeError e)`) and variants
(`shapes.Shape.Circle { radius: 1.0 }`).

### 21.4 Rules

- Modules can import each other in cycles.
- A module is loaded once, however many modules import it.
- Names of different modules do not conflict: `geo.shapes.square` and `util.text.square` are different.
- A local name hides an imported one in its block.

---

## 22. Tests

```
test function NAME ( [ NAME : Type ] ) : void [ throws Type ] block
```

A test function is a top-level function marked `test`.

- It takes nothing, or one parameter whose type is a class that implements `std.test.TestSetup`, returns
  `void`, has no `in`, and is not `public`.
- A program built for running (`larimar build`) leaves test functions out. The checks of this document
  apply to them as to any function.
- The runner, its checks and its output belong to the tools and to `std.test`, not to the language
  ([Appendix C](#appendix-c-outside-this-specification)).

---

## 23. Predeclared names

Every module sees these names without an import. They are declared in `std/lang.lar` (or implemented by
the compiler); their meaning is part of the language.

### 23.1 Functions

| Function | Meaning |
|---|---|
| `print(text: String)` | writes the text to the standard output |
| `println(text: String)` | writes the text and a line break |
| `panic(text: String)` | stops the program ([§16.3](#163-panics)) |
| `release(x)` | releases a resource now ([§19.7](#197-resources)) |
| `stringOf(bytes: byte[]): String` | a new string with those bytes |
| `stringOfRange(bytes: byte[], from: int32, to: int32): String` | a new string with the bytes `from` to `to - 1` |

### 23.2 Types

`String`, `StringBuilder`, `Any`, `Thread`, `Runnable` (`interface Runnable { function run(): void; }`) and
`Context` (C's `void*` given back to a callback, [§19.8](#198-c-function-pointers-and-callbacks)).

### 23.3 Methods of `String`

| Group | Methods |
|---|---|
| Query | `length`, `isEmpty()`, `isBlank()`, `s[i]`, `codePointCount()` |
| Search | `indexOf(t)`, `indexOf(t, from)`, `lastIndexOf(t)` (they give `int32?`), `contains(t)`, `startsWith(t)`, `endsWith(t)`, `count(t)` |
| Views | `substring(from)`, `substring(from, to)`, `trim()`, `trimStart()`, `trimEnd()`, `bytes()` |
| New text | `toUpperCase()`, `toLowerCase()`, `replace(a, b)`, `repeat(n)`, `padStart(n, s)`, `padEnd(n, s)` |
| Split | `split(sep)`, `lines()`, `codePoints()` (new lists) |
| Compare | `compareTo(t)` (negative, zero or positive), `equalsIgnoreCase(t)` |
| Convert | `toInt()` (`int64?`; decimal, `0x`, `0b`, with `_`), `toFloat()` (`float64?`), `toBool()` (`bool?`) |
| Copy | `clone()` |

`toUpperCase`, `toLowerCase` and `equalsIgnoreCase` change only ASCII letters. Indexes are byte
positions.

### 23.4 `StringBuilder`

`add(text)`, `addLine(text)`, `length`, `toString()` (a view of what has been built; it does not change
when more is added or after `clear()`) and `clear()`. Created with `{}`; it grows in its own memory.

### 23.5 Methods of arrays and lists

| Operation | `T[N]` | `T[]` | `T[*]` |
|---|---|---|---|
| `length`, `x[i]`, `x[i] = v`, `for` | yes | yes | yes |
| `push(v): bool` (`false` if it does not fit), `clear()`, `pop(): T` | yes | no | yes |
| `contains(v): bool` (with `==`) | yes | yes | yes |
| `filter(f)`, `map(f)` | give `T[N]` | give `T[*]` | give `T[*]` |
| `sort()`, `sort(compare)` | yes | yes | yes |
| `join(sep)` (of `String`) | yes | yes | yes |
| `clone()` | yes | no | yes |

- `map` needs the result type from the context. The results of `filter` and `map` on a list are created
  in the list's memory, unless `in` says otherwise.
- `sort()` sorts numbers and strings in their natural order (strings byte by byte). `sort(compare)`
  takes a `(T, T) -> int32` that is negative when the first goes before, zero when they are equal and
  positive when it goes after. Sorting is in place and **stable**. `sort()` on other element types is an
  error.

### 23.6 Methods of `Any`

[§17.5](#175-methods).

---

## 24. Program execution

1. The globals are initialized ([§7.3](#73-initialization-of-global-variables)).
2. `main` runs. It is declared in the main file as `function main()`, `function main(): int32`,
   `function main(args: String[])` or `function main(args: String[]): int32`, optionally with
   `throws`. `args` holds the arguments of the program, without its name.
3. The program ends when `main` returns. Its exit code is the value `main` returns, or 0 for a `void`
   `main`. Before it ends, the threads in the default memory are joined.

Other exit codes: 1 for an error that leaves `main` ([§16.2](#162-errors-in-main)), 101 for a panic
([§16.3](#163-panics)).

---

## Appendix A. Grammar

```
program              = import* ( [ public ] topLevel | platformDeclarations )*
import               = import NAME ( . NAME )* [ as NAME | { NAME ( , NAME )* } ] ;

topLevel             = const NAME : Type = expression ;
                     | let NAME : Type = expression ;
                     | function
                     | test function
                     | export function
                     | struct NAME { ( field | static staticMember | function | operator )* }
                     | [ synchronized ] class NAME [ extends qualifiedName ] [ implements qualifiedName ( , qualifiedName )* ]
                           { ( field | static staticMember | [ override ] function | native ( nativeFunction | nativeLet ) | operator )* }
                     | interface NAME { ( function NAME parameters [ : Type ] [ throws Type ] ; )* }
                     | enum NAME { [ variant ( , variant )* [ , ] ] }
                     | native type NAME { ( static staticMember | native ( nativeFunction | nativeLet | nativeOperator ) | function )* }
                     | c_include "TEXT" ;
                     | c_code { C TEXT }
                     | native cDeclaration

function             = function [ NAME . ] NAME parameters [ : Type ] [ in lives ] [ throws Type ]
                           [ wait until ( expression ) ] ( block | ; )
parameters           = ( [ parameter ( , parameter )* ] )
parameter            = NAME : Type [ in lives ]
lives                = default | self | NAME
operator             = operator ( + | - | * | / | % | == | < ) parameters : Type block
field                = let NAME : Type [ = expression ] ;
variant              = NAME [ parameters ]
staticMember         = function | native nativeFunction
nativeFunction       = function NAME parameters [ : Type ] [ in lives ] [ throws Type ] [ = expression ] ;
nativeOperator       = operator ( [ ] | SYMBOL ) parameters : Type ;
nativeLet            = let NAME : Type [ = expression ] ;

cDeclaration         = function NAME ( [ parameter ( , parameter )* [ , ... ] ] ) [ : Type ] [ = C ] ;
                     | type NAME [ released by NAME ] ;
                     | type NAME = CTYPE [ released by NAME ] ( ; | { cMember* } )
                     | type NAME = ( [ Type ( , Type )* ] ) -> Type ;
                     | struct NAME [ = C ] { ( cField | function | static staticMember )* }
                     | const NAME : Type [ = C ] ;
                     | let NAME : Type [ = NAME ] ;
cMember              = cField
                     | native function NAME parameters [ : Type ] [ in lives ] [ throws Type ] = ( C | expression ) ;
                     | native let NAME : Type = ( C | expression ) ;
                     | function
                     | static ( function | native function NAME parameters [ : Type ] = C ; )
cField               = let NAME : Type [ = NAME ] ;
C                    = NAME | "TEXT"
CTYPE                = NAME *... | "TEXT"

platformDeclarations = #when PLATFORM topLevel* ( #when PLATFORM topLevel* )* [ #else topLevel* ] #end

Type                 = ( qualifiedName | ( Type ) | ( [ Type ( , Type )* ] ) -> Type ) suffix* [ thread safe ]
suffix               = [ ] | [ * ] | [ expression ] | ? | *
qualifiedName        = NAME ( . NAME )*

block                = { statement* }
statement            = let NAME : Type = expression ;
                     | return [ expression ] ;
                     | if ( expression ) block [ else ( if ... | block ) ]
                     | while ( expression ) block
                     | for ( [ NAME , ] NAME in expression [ .. expression ] ) block
                     | break ; | continue ;
                     | throw expression ;
                     | yield expression ;
                     | try block ( catch ( qualifiedName NAME ) block )+
                     | #when PLATFORM statement* ( #when PLATFORM statement* )* [ #else statement* ] #end
                     | block
                     | switch ( expression ) { case* }
                     | expression [ assignOp expression ] ;
assignOp             = = | += | -= | *= | /= | %= | &= | |= | ^=

expression           = ternary [ in ( heap | default | byte [ expression ] | expression ) ]
ternary              = coalesce [ ? ternary : ternary ]
coalesce             = or [ ?? coalesce ]
or                   = and ( || and )*
and                  = comparison ( && comparison )*
comparison           = bitOr ( ( == | != | < | <= | > | >= ) bitOr | is qualifiedName [ NAME ] )*
bitOr                = bitXor ( | bitXor )*
bitXor               = bitAnd ( ^ bitAnd )*
bitAnd               = shift ( & shift )*
shift                = additive ( ( << | >> ) additive )*
additive             = multiplicative ( ( + | - ) multiplicative )*
multiplicative       = cast ( ( * | / | % ) cast )*
cast                 = unary ( as Type )*
unary                = ( - | ! | ~ | & ) unary | postfix
postfix              = primary ( arguments | . NAME | . NAME objectLiteral | [ expression ] | ! | :: NAME )*
arguments            = ( [ expression ( , expression )* ] )
primary              = NUMBER | CHAR | STRING | TEXTBLOCK | true | false | null | self | super . NAME | :: NAME
                     | objectLiteral | [ [ expression ( , expression )* ] ] | switch ( expression ) { case* }
                     | NAME [ objectLiteral ] | lambda | ( expression )
objectLiteral        = { [ entry ( , entry )* [ , ] ] }
entry                = NAME : expression | NAME | expression
lambda               = ( [ NAME [ : Type ] ( , NAME [ : Type ] )* ] ) -> block

case                 = ( case pattern ( , pattern )* | default ) [ when expression ]
                           -> ( block | throw expression ; | expression ; )
pattern              = null | literal | qualifiedName [ NAME ]
                     | qualifiedName { [ NAME [ : NAME ] ( , NAME [ : NAME ] )* ] } [ NAME ]
```

## Appendix B. Implementation-defined behavior and limits

| Item | The reference implementation |
|---|---|
| Which module of an import cycle is initialized first | the order in which the modules are loaded |
| The order in which, when a memory is freed, its threads are joined and its resources released | the reverse of the order in which they were created |
| The stack size of the program and its threads | the system's default |
| The largest memory without `in heap` inside a function | 64 KB |
| The text of a panic caused by the system (out of memory) | `panic: out of memory: ...` |
| The C compiler and its flags | any C99 compiler; [Appendix C](#appendix-c-outside-this-specification) |

A conforming implementation documents each of these.

## Appendix C. Outside this specification

These belong to the tools and the library, which have their own versions and documentation (the
[Manual](MANUAL.md)):

- the modules of the standard library other than `std.lang` (`std.io`, `std.io.files`, `std.os`,
  `std.os.process`, `std.time`, `std.crypto`, `std.encoding.json`, `std.net`, `std.test`, ...);
- the commands `larimar build`, `run`, `check`, `test`, `lsp`, `dap`, the plugins, and the file
  `larimar.toml` (with `[dependencies]` and `deps/`);
- the names and the shape of the generated C, other than what [§19](#19-c-interoperability) defines
  (`RtMem*`, `rt_mem_alloc`, `lar"..."`, the names of native and export functions);
- the text of compile errors.
