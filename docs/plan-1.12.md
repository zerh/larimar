# Plan for 1.12

What was agreed after 1.11.0. Each step ends with the compiler compiling itself to the same C, and every
test passing.

## Done

- **The state of each stage is one object**, which the `Compilation` holds: `Linking`, `Declarations`,
  `Analysis` and `Generation` (`linking`, `declared`, `analysis`, `generation` in their modules).
- **The C as parts**: `CProgram`, with each function and lambda whole (`CFunction`, with the names it
  uses); Prune cuts only the text between functions.

## To do

### From here on: std only

The work goes to the standard library, not to the compiler. The aim is a std as much in Larimar as it
can be, with the compiler as it is.

- What can be Larimar today: what calls C that is the same on every system (`stdio.h`, `stdlib.h`,
  `string.h`, `math.h`, `time.h`), through a native interface at module level, as `std.io.files` and
  `std.os` already do; and every piece of logic around a call to the system.
- What stays C: the classes of one system (`posix.lar`, `windows.lar`, `macos.lar`). The compiler checks
  and writes a function of such a class for its system only when its body is C, so their calls to the
  system stay in C bodies. Moving them to native interfaces would need the compiler to do the same for
  bodies in Larimar: not now.

### Later, not now

- The editor as a program apart (`bin/larimar-editor`, a plugin): it stays in the compiler.
- The C of the classes of one system through native interfaces (it needs the compiler, above).
- The bodies of the C as structure (`CBlock`, `CStatement`).
- The context left in variables of a module (`flowParams`, `selfInLambda`...), as parameters.
