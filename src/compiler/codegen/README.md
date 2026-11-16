# codegen: the C

What goes in: the analyzed program. What comes out: one C99 file with the program and the part of the
runtime it uses.

- `gen.lar` (the pass EmitC) writes every type, function and method; `gen/` has the types, the classes
  (tables of methods, interfaces, closures) and the statements; `expressions.lar` and `expressions/` the
  expressions. A function's C is written as text into `writing.out`; statements that need a memory for
  their temporaries get one only if something used it.
- `localnames.lar` (the pass NameC): the compiler's variables are asked for by what they are
  (`tmp("result")`) and named when their function is done: `result`, or `result_2` when the function's C
  already names `result`. They never meet a name of the program's code.
- `cprogram.lar`: the C as parts. EmitC writes a `CProgram`: text, and each function and lambda whole
  (`CFunction`, with the names it uses). The bodies are still text.
- `prune.lar` (the pass Prune): keeps only what `main` (and std's C) reaches, of the program and of the
  runtime (`runtime/`, one `ccode` per piece), with the `#include`s it needs. A function of the
  `CProgram` is one piece; only the text between functions is cut into declarations.
- `debugmap.lar`: with `--debug`, what the debugger needs to show Larimar's names and values.
- The names in the C read on their own: the runtime is `lar_` / `Lar` / `LAR_` in whole words
  (`LarMemory`, `lar_text_to_c`), a check says its line (`LINE(27)`), and a C name of the program that
  could meet them gets a `_`.

## Its API

<!-- api: written by tools/reference.py from the code; not edited by hand -->

- **`codegen.cprogram`**: the C of a program as parts, not one text
  - `class CFunction`: A function of the C: its name, its whole text (header and body), and the names it uses (Prune fills them)
  - `class CPart`: A part of the C, in order: text, or one function
  - `class CProgram`: The C of the program, in parts
  - `function cSection(program: CProgram, title: String): void`: A heading of a section of the C: Prune knows the sections by it
- **`codegen.debugmap`**: with larimar build --debug, what the debugger (larimar dap) needs to show the program as Larimar: for each C function, its Larimar name and the variables it has (their Larimar names, their names in C and their types), the globals, and the shape of every type (fields with their C paths, enum variants, classes)
  - `function debugMap(): String`: The debug map of the program just generated, as JSON
- **`codegen.expressions`**: C99 code generation (Gen.java), part 2: expressions
  - `function typeCName(n: String): String`
  - `function mangle(type: Type): String`
  - `function cType(type: Type): String`
  - `function structName(type: Type): String`
  - `function paren(s: String): String`
  - `function hoist(cTypeText: String, v: String): String`
  - `function hoistAs(cTypeText: String, v: String, role: String): String`: A value kept in a temporary that says what it is
  - `function hoistIfNeeded(cTypeText: String, v: String, e: Expr?): String`
  - `function inOrder(parts: Expr[*] in default): Expr[*]`: Computes, in order, the parts before the last one with effects; returns them, for forget()
  - `function forget(held: Expr[*]): void`: The C of these parts is written: they are computed again where they appear next
  - `function writtenValues(literal: ObjectLit in default): Expr[*]`: The values of a literal, in the order they are written
  - `function isPure(e: Expr): bool`
  - `function lazy(e: Expr in default): String`: Generates `e` (its value) into a separate buffer: its statements go to lazyPre
  - `function strip(s: String): String`: Removes the outer parentheses of a C expression when they enclose all of it
  - `function zero(type: Type): String`
  - `function discard(e: String): void`: A call whose result is not used
  - `function value(e: Expr in default): String`: An expression with its conversion applied: where a value is stored or passed
  - `function boxType(type: Type in default): String`: The descriptor of a struct or enum stored in an Any (its name and how to clone it)
  - `function boxDescriptors(): String`
  - `function anyKind(type: Type): String`: LAR_ANY_I32 and so on: the kind an Any uses for a value of type t
  - `function anyPayload(type: Type, v: String): String`: The value inside an Any already known to hold kind t
  - `function expr(e: Expr in default): String`
  - `function intLiteral(v: int64, big: bool, t: Type?): String`: An integer literal of type t (value v, as uint64 when big)
  - `function fieldC(field: FieldInfo): String`: A field's name in C: the exact one in a C struct, otherwise escaped
  - `function classFieldPath(cls: String, field: FieldInfo): String`
  - `function lvalue(target: Expr in default): String`: The C lvalue of an assignment target (no narrowing)
  - `function addrOf(e: Expr in default): String`: A pointer to the value of `e` (a temporary if `e` is not a variable or field)
  - `function memoryRef(mem: Symbol): String`
  - `function placeMem(e: Expr in default): String`: C expression of type LarMemory* for an allocation
  - `function callMem(c: Expr in default): String`: The memory a call gives for its result: none (NULL) when the callee only returns data that already exists
  - `function placeMemOf(p: Place? in default): String`
- **`codegen.expressions.calls`**: calls.
  - `function receiver(call: Call): Expr`: The object a method is called on: a in a.f(...)
  - `function call(c: Call in default): String`
  - `function args(asg: Expr[*] in default, memParams: bool[*]): String[*]`
  - `function lines(text: String in default): void`: Several lines of C, each written like line() does (a final newline adds no empty line)
- **`codegen.expressions.clone`**: clone: copying a value into another memory.
  - `function cloneTypeList(): Type[*]`
  - `function needsDeepClone(t: Type): bool`
  - `function requireClone(t: Type in default): void`
  - `function cloneHeader(type: Type): String`
  - `function cloneOf(type: Type in default, v: String): String`
  - `function cloneCall(call: Call in default, b: CallInfo in default): String`
  - `function compactCall(call: Call in default, b: CallInfo in default): String`: Memory.compact(m): m starts again with no blocks; what its variables reach in the old blocks is copied back (each thing once, cycles included), the variables are pointed at the copies, and the old blocks are freed
  - `function cloneFunctions(): String`
- **`codegen.expressions.lambdas`**: lambdas and literal objects.
  - `function lambdaValue(l: Lambda in default): String`
  - `function singleMethodObject(lambda: Lambda in default, conversion: Conversion in default): String`: A lambda used as a single-method interface: a small object holding the closure
  - `function objectLit(literal: ObjectLit in default, type: Type in default): String`
  - `function arrayLit(a: ArrayLit in default, type: Type): String`
- **`codegen.expressions.operators`**: operators.
  - `function wide(type: Type): String`
  - `function unary(u: Unary in default, type: Type): String`
  - `function binary(b: Binary in default, type: Type): String`
  - `function isTest(isExpr: IsExpr in default): String`: x is T [b]: lar_as_class gives the object when it is a T (NULL otherwise); the binding keeps it
  - `function ternary(te: Ternary in default, type: Type): String`: c ? a : b: a C conditional, or an if when a side needs statements of its own
  - `function cast(c: Cast in default, to: Type in default): String`
- **`codegen.expressions.patterns`**: the patterns of a switch.
  - `function patternTest(patternInfo: PatternInfo in default, st: Type, inner: Type, subj: String, val: String): String`: Joined only with || (several patterns in one case), so a comparison needs no parentheses of its own (clang warns about if ((a == b)))
  - `function bindPattern(patternInfo: PatternInfo, inner: Type, subj: String, val: String): void`
- **`codegen.expressions.strings`**: strings: literals, interpolation and their methods.
  - `function string(s: StringLit in default, memOverride: String): String`: memOverride != "": the text is built in that memory
  - `function printDirect(s: StringLit in default, newline: bool): String?`: print/println of a literal, or of a text whose parts are integers, bool, String or enums: straight to stdout (fputs or printf), with no text built in memory
  - `function appendPieces(s: StringLit in default, sbRef: String): void`: Writes the parts of an interpolated text into a builder (sbRef: a LarTextBuilder*)
  - `function stringLiteral(raw: String): String`
- **`codegen.gen`**: C99 code generation (Gen.java), part 1: the file, types, classes and interfaces, globals, bodies and statements
  - `class Block`
  - `class TryCtx`
  - `class ArmCtx`
  - `class FunctionCode`
  - `class Temp`: A statement's temporary memory, declared before the statement only if something used it
  - `function newFunctionCode(): FunctionCode`
  - `class Generation`: The state of the generator: the function being written, the pieces of C made on the way (lambdas, literals, helpers) and its errors
  - `function useGeneration(state: Generation in default): void`: Makes `state` the one the compiler works on
  - `function internalError(line: int32, msg: String): void`
  - `function lineMark(encoded: int32): String`
  - `function spreadLines(c: String, cFile: String): String`: After generating with debugLines: inside a function, every line of C after a #line gets that same .lar line (C would count on: N, N+1, N+2...); after the function, the lines are the C file's again, so the runtime and helpers are shown as the C they are
  - `function line(s: String): void`
  - `function tmp(role: String): String`: A temporary of the function being generated, by what it is: its name comes from codegen.localnames
  - `function indent4(text: String in default): String`: Adds four spaces to every line (like String.indent(4) in Java)
  - `function pushBlock(blockCode: Block in default): void`
  - `function popBlock(): void`
  - `function topBlock(): Block`
  - `function rootBlock(): Block`
  - `function generate(): String`: The C of the analyzed program: emitC, then nameC, then pruneC (the passes EmitC, NameC and Prune)
  - `function nameC(program: CProgram): void`: NameC: the names of the compiler's variables (codegen.localnames)
  - `function emitC(): CProgram`: EmitC: the whole program, every function and type, before anything is cut: text, and each function whole
  - `function pruneC(emitted: CProgram): String`: Prune: only what main and the ccode reach, after the runtime it needs
  - `function section(out: StringBuilder, title: String): void`
  - `function classesByDepth(): ClassInfo[*]`
- **`codegen.gen.classes`**: classes, interfaces and closures in C; globals and the entry point.
  - `function returnsData(ret: Type): bool`: Returning something that points to memory: the function creates it in the memory of the call
  - `function params(paramSymbols: Symbol[*], memParams: bool[*]): String`
  - `function functionHeader(functionInfo: FunctionInfo): String`
  - `function methodName(method: MethodInfo): String`
  - `function methodHeader(method: MethodInfo, isStructMethod: bool): String`
  - `function nativeMethodHeader(method: MethodInfo): String`
  - `function lambdaHeader(lambdaInfo: LambdaInfo): String`
  - `function paramCTypes(method: MethodInfo in default): String[*]`: The C parameters after self: the memory of the call first when it returns data
  - `function vtableStruct(out: StringBuilder, classInfo: ClassInfo in default): void`
  - `function vtableInit(concrete: ClassInfo in default, level: ClassInfo): String`
  - `function dispatchName(intro: String, method: MethodInfo): String`
  - `function dispatchHelper(out: StringBuilder, classInfo: ClassInfo, method: MethodInfo in default): void`
  - `function interfaceTableStruct(out: StringBuilder, interfaceInfo: InterfaceInfo in default): void`
  - `function ifaceCallName(interfaceInfo: InterfaceInfo, method: MethodInfo): String`
  - `function interfaceCallHelper(out: StringBuilder, interfaceInfo: InterfaceInfo, method: MethodInfo in default): void`
  - `function interfaceImplementations(out: StringBuilder): void`: For each class that declares `implements I`: thunks plus a table
  - `function samTable(out: StringBuilder, interfaceInfo: InterfaceInfo in default): void`
  - `function samThunk(out: StringBuilder, interfaceInfo: InterfaceInfo in default): void`
  - `function closureCallHelper(out: StringBuilder, functionType: Type): void`
  - `function collectionHelpers(out: StringBuilder, type: Type): void`
  - `function initGlobals(): String`
  - `function mainWrapper(): String`
  - `function clonePrototypes(): String`
  - `function classClone(out: StringBuilder, classInfo: ClassInfo in default): void`
- **`codegen.gen.statements`**: bodies and statements, switch included.
  - `function body(stmts: Stmt[*] in default, ret: Type in default, throwsOut: bool, lambda: LambdaInfo? in default,`: lock != "": a method of a synchronized class, locked for its whole run (unlocked on every exit)
  - `function endsWithJump(stmts: Stmt[*]): bool`
  - `function block(stmts: Stmt[*] in default): void`
  - `function cleanupsUntil(stop: Block): void`: Emits the cleanups of every block from the innermost up to `stop` (inclusive)
  - `function stmt(s: Stmt in default): void`: A statement; what it creates without a place lives in its temporary memory, freed when it ends
  - `function openMemory(stmts: Stmt[*] in default): void`: A block whose variables hold data gets its memory, freed when the block ends
  - `function tempMem(): String`: The current statement's temporary memory (declared before it the first time it is used)
  - `function ret(r: ReturnStmt in default): void`
  - `function throwStmt(t: ThrowStmt in default): void`
  - `function propagate(): void`: Sends the current error to the innermost try, or to the caller
  - `function switchCode(switchExpr: SwitchExpr in default, isExpr: bool): String`
- **`codegen.gen.types`**: the C of the types of a program.
  - `function externPrototype(functionInfo: FunctionInfo in default): String`: C functions receive String as a NUL-terminated const char*
  - `function externDefinition(functionInfo: FunctionInfo in default): String`: The header of the C function of a C body, with its parameters named as in Larimar (a T[] is name and name_length)
  - `function larInC(code: String): String`: ccode with lar"name" (the linker gave the linked name): the C name of that function, type or global
  - `function larPrototypes(code: String, out: StringBuilder): void`: The prototypes of the Larimar functions a ccode names (those with C types the runtime already has)
  - `function isCName(n: String): bool`: A plain C name (a function a prototype can declare), not C text
  - `function externCType(type: Type): String`
  - `function forward(out: StringBuilder, type: Type): void`
  - `function define(out: StringBuilder, t: Type): void`
  - `function envField(symbol: Symbol): String`
- **`codegen.localnames`**: the names of the C variables the compiler makes in a function (its temporaries, its memories, the result it returns)
  - `function localName(role: String): String`: The name of a temporary that is `role` (letters, digits and '_'): one of its own, decided by nameLocals
  - `function localNameFor(role: String, key: String): String`: The same temporary for a key that names it already (a memory of a block of the analysis: mem_3)
  - `function nameLocals(text: String): String`: The text with each mark replaced by its name: the role, or the role and a number when it is taken
- **`codegen.prune`**: only the C the program reaches, of what it generates and of the runtime
  - `function prune(program: CProgram, roots: String[*]): String`: The generated program without what it does not reach
  - `function selectRuntime(program: String, threads: bool, files: bool, allHeaders: bool): String`: The runtime the program needs, in the runtime's order
  - `function braceDelta(ln: String): int32`: The braces a line opens minus those it closes (strings and comments left out)
  - `function isName(t: String): bool`
  - `function tokens(c: String): String[*]`: C tokens: names, numbers and single punctuation characters; comments, strings and characters are skipped

<!-- /api -->
