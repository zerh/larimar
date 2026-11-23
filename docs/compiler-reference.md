# El compilador de Larimar: referencia de funciones

Cada módulo de `src/`, con su descripción y **todas** sus funciones, clases y métodos: la firma tal como está en el código y el comentario que la acompaña.

> Este archivo se **genera** a partir del código (`/** ... */` y `//` encima de cada declaración) con `tools/reference.py`. No se edita a mano: si una descripción falta o está mal, se corrige el comentario en el código. Las descripciones están en inglés, como en el código. Una entrada sin texto es una función sin comentario.

Para la visión de conjunto (fases, datos que pasan de una a otra, recetas), ver la guía de mantenimiento. Aquí está el detalle.

**54 módulos, 1137 funciones y métodos** (589 con comentario, 548 sin él).

## Módulos

- [`src/compiler/main.lar`](#main) — 38 funciones
- [`src/compiler/pipeline.lar`](#pipeline) — 25 funciones
- [`src/compiler/syntax/ast.lar`](#syntax-ast) — 6 funciones
- [`src/compiler/syntax/lexer.lar`](#syntax-lexer) — 26 funciones
- [`src/compiler/syntax/parser.lar`](#syntax-parser) — 22 funciones
- [`src/compiler/syntax/parser/declarations.lar`](#syntax-parser-declarations) — 15 funciones
- [`src/compiler/syntax/parser/expressions.lar`](#syntax-parser-expressions) — 22 funciones
- [`src/compiler/syntax/parser/natives.lar`](#syntax-parser-natives) — 19 funciones
- [`src/compiler/syntax/parser/statements.lar`](#syntax-parser-statements) — 8 funciones
- [`src/compiler/syntax/parser/types.lar`](#syntax-parser-types) — 2 funciones
- [`src/compiler/semantics/analyzer.lar`](#semantics-analyzer) — 19 funciones
- [`src/compiler/semantics/analyzer/classes.lar`](#semantics-analyzer-classes) — 11 funciones
- [`src/compiler/semantics/analyzer/compact.lar`](#semantics-analyzer-compact) — 15 funciones
- [`src/compiler/semantics/analyzer/declarations.lar`](#semantics-analyzer-declarations) — 29 funciones
- [`src/compiler/semantics/analyzer/flow.lar`](#semantics-analyzer-flow) — 42 funciones
- [`src/compiler/semantics/analyzer/narrowing.lar`](#semantics-analyzer-narrowing) — 15 funciones
- [`src/compiler/semantics/analyzer/order.lar`](#semantics-analyzer-order) — 8 funciones
- [`src/compiler/semantics/analyzer/statements.lar`](#semantics-analyzer-statements) — 20 funciones
- [`src/compiler/semantics/analyzer/threads.lar`](#semantics-analyzer-threads) — 13 funciones
- [`src/compiler/semantics/expressions.lar`](#semantics-expressions) — 28 funciones
- [`src/compiler/semantics/expressions/callbacks.lar`](#semantics-expressions-callbacks) — 5 funciones
- [`src/compiler/semantics/expressions/calls.lar`](#semantics-expressions-calls) — 32 funciones
- [`src/compiler/semantics/expressions/constants.lar`](#semantics-expressions-constants) — 9 funciones
- [`src/compiler/semantics/expressions/conversions.lar`](#semantics-expressions-conversions) — 13 funciones
- [`src/compiler/semantics/expressions/literals.lar`](#semantics-expressions-literals) — 15 funciones
- [`src/compiler/semantics/expressions/operators.lar`](#semantics-expressions-operators) — 16 funciones
- [`src/compiler/semantics/expressions/switches.lar`](#semantics-expressions-switches) — 10 funciones
- [`src/compiler/semantics/linker.lar`](#semantics-linker) — 73 funciones
- [`src/compiler/semantics/rules.lar`](#semantics-rules) — 26 funciones
- [`src/compiler/semantics/types.lar`](#semantics-types) — 90 funciones
- [`src/compiler/codegen/cprogram.lar`](#codegen-cprogram) — 4 funciones
- [`src/compiler/codegen/debugmap.lar`](#codegen-debugmap) — 10 funciones
- [`src/compiler/codegen/expressions.lar`](#codegen-expressions) — 52 funciones
- [`src/compiler/codegen/expressions/callbacks.lar`](#codegen-expressions-callbacks) — 6 funciones
- [`src/compiler/codegen/expressions/calls.lar`](#codegen-expressions-calls) — 17 funciones
- [`src/compiler/codegen/expressions/clone.lar`](#codegen-expressions-clone) — 10 funciones
- [`src/compiler/codegen/expressions/lambdas.lar`](#codegen-expressions-lambdas) — 10 funciones
- [`src/compiler/codegen/expressions/operators.lar`](#codegen-expressions-operators) — 12 funciones
- [`src/compiler/codegen/expressions/patterns.lar`](#codegen-expressions-patterns) — 2 funciones
- [`src/compiler/codegen/expressions/strings.lar`](#codegen-expressions-strings) — 8 funciones
- [`src/compiler/codegen/gen.lar`](#codegen-gen) — 25 funciones
- [`src/compiler/codegen/gen/classes.lar`](#codegen-gen-classes) — 28 funciones
- [`src/compiler/codegen/gen/statements.lar`](#codegen-gen-statements) — 31 funciones
- [`src/compiler/codegen/gen/types.lar`](#codegen-gen-types) — 12 funciones
- [`src/compiler/codegen/localnames.lar`](#codegen-localnames) — 6 funciones
- [`src/compiler/codegen/prune.lar`](#codegen-prune) — 22 funciones
- [`src/compiler/project/cc.lar`](#project-cc) — 11 funciones
- [`src/compiler/project/libraries.lar`](#project-libraries) — 4 funciones
- [`src/compiler/project/testing.lar`](#project-testing) — 27 funciones
- [`src/compiler/editor/dap.lar`](#editor-dap) — 62 funciones
- [`src/compiler/editor/ide.lar`](#editor-ide) — 74 funciones
- [`src/compiler/editor/lsp.lar`](#editor-lsp) — 21 funciones
- [`src/compiler/editor/opendocuments.lar`](#editor-opendocuments) — 2 funciones
- [`src/compiler/editor/session.lar`](#editor-session) — 9 funciones

---

## main

`src/compiler/main.lar` · 853 líneas · 38 funciones
larimar: the Larimar tool and compiler, written in Larimar (Larimar.java + Transpiler.java).

larimar new <name>              creates a project
larimar build [folder]          larimar.toml -> build/<name>.c -> executable (a library: checked)
larimar run [folder] [-- args]  builds, then runs the program
larimar build --debug           -g -O0 and #line to the .lar files (debuggers; also run, and file.lar -o)
larimar check [file|folder]     the errors, without generating C (--json for tools)
larimar test [file|folder]...   runs the tests (testing.lar)
larimar lsp                     the language server for editors (LSP on stdin/stdout)
larimar dap                     the debugger for editors (DAP on stdin/stdout, over lldb-dap)
larimar c <file.lar>            prints the C of a file (imports are looked up next to it)
larimar <file.lar> [-o out.c]   the same, written to a file (how the compiler is used by scripts)

`function main(args: String[]): int32`
<sub>línea 49</sub>

`function debugMapPath(cFile: String): String`  
build/demo.c -> build/demo.debug.json: what larimar dap needs to show the program as Larimar.  
<sub>línea 67</sub>

`function fail(msg: String in default): int32`
<sub>línea 78</sub>

`function command(args: String[]): int32`  
The options of larimar itself, taken out of the arguments; what follows `--` is the program's.  
<sub>línea 84</sub>

`function newProject(rest: String[*]): int32`  
larimar new <name> [--library]  
<sub>línea 132</sub>

`function buildProject(run: bool, rest: String[*], programArgs: String[*]): int32`  
larimar build [folder], larimar run [folder] [-- args]  
<sub>línea 142</sub>

`function test(rest: String[*]): int32`  
larimar test [file|folder]...  
<sub>línea 156</sub>

`function file(main: String, rest: String[*], programArgs: String[*]): int32`  
larimar file.lar -o out.c: its C; larimar file.lar [args]: build it and run it  
<sub>línea 162</sub>

`function writeC(main: String, output: String): int32`  
The C of a file, into `output` ("": printed).  
<sub>línea 175</sub>

`function plugin(cmd: String, args: String[]): int32`  
A command that is not larimar's: a plugin's, or an error.  
<sub>línea 193</sub>

`function version(): int32`
<sub>línea 203</sub>

`function usage(): int32`
<sub>línea 208</sub>

### class `Plugin`
A command of a plugin: `larimar <command> x` runs `bin/<program> <args> x`.

`function larimarHome(): String`  
$LARIMAR_HOME, or the installation the tool is in (the folder of std/).  
<sub>línea 260</sub>

`function plugins(problems: String[*]): Plugin[*]`  
The commands that plugins declare, one file each in $LARIMAR_HOME/plugins: [plugin] name = "mytool" program = "mytool" # a program of $LARIMAR_HOME/bin, nowhere else version = "1.0.0" [commands] hello = ["hello"] # larimar hello x -> bin/mytool hello x A plugin cannot take a command of larimar itself, and two plugins cannot take the same one: both are problems (and that command is not taken).  
<sub>línea 279</sub>

`function runPlugin(plugin: Plugin, args: String[]): int32`  
Runs the program of a plugin with its arguments and the user's, on this console; its exit code is larimar's.  
<sub>línea 326</sub>

`function compileFile(main: String, shownFrom: String): String`  
The C of a main file (pipeline.compilerPasses), or "" with the problems in compileErrors.  
<sub>línea 354</sub>

`function testCompiler(wanted: String): CCompiler?`  
The C compiler for the tests (a test file that uses TLS needs the system's: compileC says so).  
<sub>línea 369</sub>

`function testSettings(): TestSettings?`  
The project's [c] settings for the tests, or the defaults when there is no larimar.toml here.  
<sub>línea 377</sub>

`function testMain(rest: String[*]): int32`  
larimarc test-main <file.lar> -o <out.c> [--root <folder>]: the C of a file of test functions with a main added (testing.lar). Next to out.c it writes the file with its main (.lar) and the tests' names (.tests, one per line).  
<sub>línea 402</sub>

### class `Project`

`function load(dir: String): Project?`
<sub>línea 466</sub>

`function keysOf(section: String): String`
<sub>línea 487</sub>

`function allowedKey(section: String, key: String): bool`
<sub>línea 491</sub>

`function project(dir: String, config: Any): Project?`
<sub>línea 495</sub>

`function moduleName(name: String): bool`  
A name of a module: letters, digits and '_', not starting with a digit.  
<sub>línea 568</sub>

`function isPlatform(name: String): bool`  
The platforms: of [c.<platform>] and of --target.  
<sub>línea 577</sub>

`function hasNames(value: Any): bool`  
Whether a table has entries with a name (a section does; a list does not).  
<sub>línea 583</sub>

`function isSection(value: Any): bool`
<sub>línea 588</sub>

`function text(section: Any, key: String, def: String): String`
<sub>línea 595</sub>

`function list(section: Any, key: String, def: String[*]): String[*]`
<sub>línea 604</sub>

`function validName(name: String): bool`
<sub>línea 627</sub>

`function resolve(dir: String, p: String): String`  
A path of the project: relative to its folder, or absolute.  
<sub>línea 640</sub>

`function build(p: Project, debug: bool): String`  
Builds the project; returns the executable, or "" on failure.  
<sub>línea 643</sub>

`function buildFrom(p: Project, main: String, debug: bool): String`  
Compiles `main` (and what it imports) to the project's executable.  
<sub>línea 653</sub>

`function checkLibrary(p: Project): bool`  
larimar build of a library: its code is checked (its main file and every part it imports). A program uses it from its [dependencies], compiling its source with its own; nothing is built for the library alone.  
<sub>línea 711</sub>

`function runScript(file: String, args: String[*]): int32`  
larimar file.lar [args]: the file is built in a folder of the system's temporary files (the bundled tcc first: it starts fast) and run with the arguments; its exit code is larimar's. Nothing is printed but what the program prints, so scripts can be piped.  
<sub>línea 732</sub>

`function execute(exe: String, args: String[*]): int32`
<sub>línea 774</sub>

`function create(path: String, library: bool): int32`
<sub>línea 784</sub>

`function createLibrary(path: String, name: String): int32`  
larimar new <name> --library: a library with one function and a test of it.  
<sub>línea 816</sub>

---

## pipeline

`src/compiler/pipeline.lar` · 216 líneas · 25 funciones
pipeline: one compilation, as passes over it. A Compilation says what goes in (the main file, where std
is) and keeps what the passes leave (the program, its problems, the C); a Pass does one thing to it and
reports what went wrong instead of throwing. The compiler runs them in order and stops after the first
that leaves problems:

Link -> CheckRules -> Assemble -> Analyze -> EmitC -> NameC -> Prune

Link        reads and parses the main file and every module it imports (semantics.linker)
CheckRules  the rules of the language about modules (semantics.rules: each error says its rule)
Assemble    every module's declarations, with their C names, in one Program
Analyze     types, lifetimes, threads (semantics.analyzer)
EmitC       the C of every function and type (codegen.gen)
NameC       the names of the compiler's variables (codegen.localnames)
Prune       only what main reaches, after the runtime it needs (codegen.prune)

larimar check and the editor run the passes up to Analyze (analysisPasses); a build runs them all.
The state of each stage is one object the Compilation holds (Linking, Declarations, Analysis,
Generation); each module reaches the one in use through a variable (linking, declared, analysis,
generation), and install(unit) makes a compilation's the ones in use.

### class `Compilation`
One compilation: what goes in, and what each pass leaves.

- `function failed(): bool`
  <sub>línea 57</sub>

### interface `Pass`
A step of the compilation. It reports problems in the Compilation instead of throwing.

- `function name(): String`
  <sub>línea 62</sub>

- `function run(unit: Compilation): void`
  <sub>línea 63</sub>

`public function analysisPasses(): Pass[*]`  
The passes of larimar check and of the editor: up to Analyze.  
<sub>línea 67</sub>

`public function compilerPasses(): Pass[*]`  
The passes of a build: all of them.  
<sub>línea 72</sub>

`public function assembledProgram(): Program`
<sub>línea 79</sub>

`public function compilationWith(main: String, shownFrom: String, std: String, sourceRoot: String): Compilation`  
A compilation of a main file with the state the compiler has now (and the settings given to it).  
<sub>línea 82</sub>

`public function install(unit: Compilation in default): void`  
Makes the state of a compilation the one the stages work on (useLinking, useAnalysis...): for a second compilation in the same process, with states of its own. compilationWith takes the ones in use.  
<sub>línea 93</sub>

`public function run(unit: Compilation, passes: Pass[*]): bool`  
Runs the passes in order, until one leaves problems. true: none did.  
<sub>línea 101</sub>

`function gather(unit: Compilation, from: String[*], start: int32): void`  
The problems a list got since it had `from`, into the compilation.  
<sub>línea 110</sub>

### class `LinkPass implements Pass`

- `override function name(): String`
  <sub>línea 115</sub>

- `override function run(unit: Compilation): void`
  <sub>línea 116</sub>

### class `CheckRulesPass implements Pass`

- `override function name(): String`
  <sub>línea 134</sub>

- `override function run(unit: Compilation): void`
  <sub>línea 135</sub>

### class `AssemblePass implements Pass`

- `override function name(): String`
  <sub>línea 146</sub>

- `override function run(unit: Compilation): void`
  <sub>línea 147</sub>

### class `AnalyzePass implements Pass`

- `override function name(): String`
  <sub>línea 156</sub>

- `override function run(unit: Compilation): void`
  <sub>línea 157</sub>

### class `EmitCPass implements Pass`

- `override function name(): String`
  <sub>línea 168</sub>

- `override function run(unit: Compilation): void`
  <sub>línea 169</sub>

### class `NameCPass implements Pass`

- `override function name(): String`
  <sub>línea 177</sub>

- `override function run(unit: Compilation): void`
  <sub>línea 178</sub>

### class `PrunePass implements Pass`

- `override function name(): String`
  <sub>línea 182</sub>

- `override function run(unit: Compilation): void`
  <sub>línea 183</sub>

`function findLibraryRoots(main: String): void`  
The libraries the project of a file uses ([dependencies] of its larimar.toml, and theirs): `import textkit` finds textkit.lar in the folder of its modules. A problem with them is larimar build's to say.  
<sub>línea 192</sub>

---

## syntax.ast

`src/compiler/syntax/ast.lar` · 569 líneas · 6 funciones
syntax.ast: the syntax tree (Ast.java). One class per kind of node; the analyzer writes what it
finds into the fields of Node, and the generator reads them from there.

### class `Node`

### class `Expr extends Node`

### class `Stmt extends Node`

### enum `TypeRefKind`

### class `TypeRef extends Node`

`public function typeNamed(name: String in default, line: int32): TypeRef`
<sub>línea 72</sub>

### class `Program extends Node`

### class `ImportDecl extends Node`
import a.b; import a.b as x; import a.b { n1, n2 };

### class `CIncludeDecl extends Node`
platform: "" (every one), "windows", "macos", "linux" or "unix": that of the class it is in (the analyzer sets it).

### class `CCodeDecl extends Node`

### class `NativeInterfaceDecl extends Node`
native interface Name "<h>" [extends A, B] { function...; type...; const...; let... }: what a C header gives, under one name. Its functions and values become Name__f (called Name.f); its types keep their names (a type with fields is a struct or a union of C, by value). The header reaches the C only when something of it is used.

### class `ExternTypeDecl extends Node`
native type X; = T*; = c"C TYPE"; ... released by f;

### class `ExternFunctionDecl extends Node`
cName: the C function called (it stays when a module renames the declaration); prototype: no cinclude. A method of a native type (`native function m() = c_m;`) becomes one of these, with self first.

### class `ExternValueDecl extends Node`
native const NAME: T [= c_name | = "C"]; native let NAME: T [= c_name]; a C constant (or macro) or a C global variable.

### class `ConstDecl extends Node`

### class `Param extends Node`
lives: "", "default", "self" or another parameter (`k: Node in p`).

### class `FunctionDecl extends Node`
Functions, methods, operators and interface signatures (hasBody false).

### class `FieldDecl extends Node`

### class `StructDecl extends Node`

### class `ClassDecl extends Node`

### class `InterfaceDecl extends Node`

### class `NativeTypeDecl extends Node`

### class `EnumVariant extends Node`

### class `EnumDecl extends Node`

`public function declName(d: Node): String`  
The name a declaration introduces, or "".  
<sub>línea 236</sub>

`public function isTypeDecl(d: Node): bool`
<sub>línea 254</sub>

### class `VarDecl extends Stmt`

### class `AssignStmt extends Stmt`

### class `ReturnStmt extends Stmt`

### class `ExprStmt extends Stmt`

### class `IfStmt extends Stmt`
platform != "": chosen when the C is compiled (#if ... #else ... #endif), not when it runs. It is how a native method of a class for one platform calls its C only there (the analyzer writes it; no syntax gives it). A further platform is an IfStmt in elseBody with `chained`.

### class `WhileStmt extends Stmt`

### class `ForStmt extends Stmt`
for (x in e), for (i, x in e), for (i in a..b)

### class `BreakStmt extends Stmt`

### class `ContinueStmt extends Stmt`

### class `ThrowStmt extends Stmt`

### class `YieldStmt extends Stmt`

### class `CatchClause extends Node`

### class `TryStmt extends Stmt`

### class `SwitchStmt extends Stmt`

### class `BlockStmt extends Stmt`
{ ... } as a statement: a scope (memories declared inside are freed at its end).

### class `IntLit extends Expr`
big: the value is num as uint64 (above int64); huge: it does not fit in 64 bits (text has it).

### class `FloatLit extends Expr`

### class `StringLit extends Expr`
texts.length == exprs.length + 1; the texts keep their escapes.

### class `BoolLit extends Expr`

### class `NullLit extends Expr`

### class `Ident extends Expr`

### class `SelfExpr extends Expr`

### class `SuperMember extends Expr`

### class `Member extends Expr`

### class `Index extends Expr`

### class `Call extends Expr`

### class `Unary extends Expr`

### class `Binary extends Expr`

### class `Ternary extends Expr`

### class `IsExpr extends Expr`
expr is Type [binding]

### class `Cast extends Expr`

### class `Unwrap extends Expr`

### class `Lambda extends Expr`

### class `FieldInit extends Node`
name "": a positional entry ({ 1, 2 } in an Any). shorthand: written { x } for { x: x }.

### class `ObjectLit extends Expr`

### class `ArrayLit extends Expr`

### class `Placed extends Expr`
e in m, in heap, in byte[N], in default

### class `Pattern extends Node`
fields[i] is bound to bindings[i]; binding is the name for the whole value.

### class `SwitchCase extends Node`
One of expr, block (hasBlock) or throwStmt is the arm.

### class `SwitchExpr extends Expr`

`public function allStmts(body: Stmt[*] in out, out: Stmt[*]): void`  
Every statement of a body, nested ones included (not inside lambdas).  
<sub>línea 454</sub>

`public function allExprs(body: Stmt[*] in out, lambdas: bool, out: Expr[*]): void`  
Every expression of a body (into lambda bodies when `lambdas`).  
<sub>línea 478</sub>

`public function exprAll(e: Expr? in out, lambdas: bool, out: Expr[*]): void`
<sub>línea 515</sub>

---

## syntax.lexer

`src/compiler/syntax/lexer.lar` · 630 líneas · 26 funciones
syntax.lexer: source text -> tokens (Lexer.java).

String literals keep their raw text (escapes and ${...} included); the parser splits
them and lexes each ${...} again with a Lexer of its own.

### enum `TokenType`

### class `Token`

### class `Lexer`
Reads a source text into tokens: Lexer { src, line }, run(), then its toks. `line` is the encoded line of its first byte (file 1000000 + line). An error stops it: `error` says why ("" when there is none).

- `function run(): void`  
  Reads src into toks, ending in Eof (or stops at the first error).  
  <sub>línea 41</sub>

- `function inNativeHeader(): bool`  
  After the header of a native function (native function f(...): T): its body is C, not Larimar.  
  <sub>línea 75</sub>

- `function fail(at: int32, msg: String): void`  
  Records the first error and stops.  
  <sub>línea 93</sub>

- `function peek(k: int32): byte`
  <sub>línea 98</sub>

- `function add(kind: TokenType, text: String in self, length: int32): void`
  <sub>línea 102</sub>

- `function blockComment(): void`
  <sub>línea 107</sub>

- `function identifier(): void`
  <sub>línea 121</sub>

- `function cText(): void`  
  c"...": C text in a native declaration (= c"(http_listen)", = c"struct sqlite3*"). It is taken as it is written up to the closing quote: no escapes of Larimar and no ${...}; a \" is a quote of C.  
  <sub>línea 140</sub>

- `function cCode(): void`  
  ccode { ... }: the C text up to the matching brace (braces in C strings and comments do not count).  
  <sub>línea 159</sub>

- `function intToken(digits: String, radix: int32, whole: String): void`  
  A literal whose digits are `digits` (without '_') in base `radix`.  
  <sub>línea 210</sub>

- `function cleanDigits(digits: String, whole: String): String`  
  Digits without '_', or "" after reporting an error.  
  <sub>línea 235</sub>

- `function number(): void`
  <sub>línea 243</sub>

- `function stringLiteral(): void`  
  Keeps the raw text; ${...} pieces are lexed again by the parser.  
  <sub>línea 284</sub>

- `function interpolation(start: int32): bool`  
  Skips ${...} (with the strings nested in it); false after reporting an error.  
  <sub>línea 308</sub>

- `function textBlock(): void`  
  A text block (\"\"\" then a new line ... \"\"\"): the common indentation and the spaces at line ends go.  
  <sub>línea 332</sub>

- `function rawTextBlock(): void`  
  raw\"\"\" then a new line ... \"\"\": a text block taken as it is written. No escapes (a backslash is a backslash) and no ${...}. The common indentation goes, as in a text block. If the text has three quotes in a row, open with more (raw\"\"\"\") and close with as many.  
  <sub>línea 371</sub>

- `function closes(quotes: int32): bool`  
  `quotes` quotes in a row at pos.  
  <sub>línea 404</sub>

- `function charLiteral(): void`  
  'a', '\n': the character's code (Unicode), as an integer literal.  
  <sub>línea 412</sub>

- `function punctuation(c: byte): void`
  <sub>línea 471</sub>

`function isLetter(b: byte): bool`  
ASCII letters, and the bytes of any non-ASCII character (names can use any letter).  
<sub>línea 541</sub>

`function isNameByte(b: byte): bool`  
A byte of a name: letters (any), digits and _.  
<sub>línea 543</sub>

`function keyword(w: String): TokenType`
<sub>línea 545</sub>

`function digitValue(b: byte): int32`
<sub>línea 595</sub>

`public function stripIndent(raw: String): String`
<sub>línea 601</sub>

`function blank(l: String): bool`
<sub>línea 623</sub>

`function indent(l: String): int32`
<sub>línea 625</sub>

---

## syntax.parser

`src/compiler/syntax/parser.lar` · 208 líneas · 22 funciones
syntax.parser: tokens -> syntax tree.

A recursive descent parser. Parser holds what is being read (the tokens, where it is, the first
error) and reads them one by one; the constructions of the language are functions over it, in the
modules of syntax/parser/: declarations, natives (what comes from C), types, statements, expressions.
Each reads one construction, and the comment above it shows its form, in this notation:

word        that word (a keyword or a symbol)          [ x ]     x, optionally
NAME        an identifier                              x*        x, any number of times
x | y       x or y                                     ( ... )   grouping

The first syntax error is kept; after it every token reads as the end of the file, so the parser
unwinds quickly and its result is thrown away.

`public function parseProgram(source: String in default, startLine: int32): Program`  
The tree of one source file; its `error` is the first lexical or syntax error. `startLine`: the number of its first line (it also says the file).  
<sub>línea 20</sub>

`public function parseModule(source: String in default, startLine: int32, openInterfaces: bool): Program`  
The same, for a module of a program or a library (`openInterfaces`): its native interfaces are opened, their functions found in a library when an UnsafeTask runs, as those declared in its class.  
<sub>línea 26</sub>

### class `Parser`
The tokens of a source text, read one by one.

- `function error(line: int32, message: String): void`
  <sub>línea 50</sub>

- `function hasFailed(): bool`
  <sub>línea 54</sub>

- `function current(): Token`  
  The token to read next.  
  <sub>línea 57</sub>

- `function next(): Token`  
  The token after the current one.  
  <sub>línea 62</sub>

- `function previous(): Token`  
  The token just read.  
  <sub>línea 68</sub>

- `function atEnd(): bool`
  <sub>línea 70</sub>

- `function at(kind: TokenType): bool`  
  Is the current token of this kind?  
  <sub>línea 73</sub>

- `function atWord(word: String): bool`  
  Is the current token the identifier `word` (a word with a meaning only there: test, type...)?  
  <sub>línea 76</sub>

- `function atWords(first: String, second: String): bool`  
  Are the next two tokens the identifiers `first` and `second` (wait until, thread safe)?  
  <sub>línea 79</sub>

- `function advance(): Token`  
  Reads the current token and gives it.  
  <sub>línea 84</sub>

- `function optional(kind: TokenType): bool`  
  [ kind ]: reads the token when it is of this kind, and says whether it was.  
  <sub>línea 90</sub>

- `function optionalWords(first: String, second: String): bool`  
  [ first second ]: reads the two words when they come, and says whether they did.  
  <sub>línea 97</sub>

- `function expect(kind: TokenType, message: String): Token`  
  kind: reads the token, which must be of this kind (else the error says what came instead).  
  <sub>línea 105</sub>

`public function endedBySemicolon(parser: Parser in default, node: Node, what: String): Node`  
The node, after its ';'.  
<sub>línea 115</sub>

`public function qualifiedName(parser: Parser in default, message: String): String`  
NAME ( . NAME )*  
<sub>línea 121</sub>

`public function strictList(parser: Parser in default, close: TokenType, readItem: () -> void): void`  
[ item ( , item )* ] before `close` (which is not read).  
<sub>línea 131</sub>

`public function looseList(parser: Parser in default, close: TokenType, readItem: () -> void): void`  
Like strictList, but a comma may also end the list.  
<sub>línea 140</sub>

`public function lives(parser: Parser in default): String`  
in ( default | self | NAME ): where a parameter or a result lives.  
<sub>línea 148</sub>

`function program(parser: Parser in default, startLine: int32): Program`  
import* ( [public] declaration )*  
<sub>línea 155</sub>

`function importDeclaration(parser: Parser in default): ImportDecl`  
import NAME ( . NAME )* [ as NAME | { NAME ( , NAME )* } ] ;  
<sub>línea 188</sub>

---

## syntax.parser.declarations

`src/compiler/syntax/parser/declarations.lar` · 367 líneas · 15 funciones
syntax.parser.declarations: what a file declares (functions, structs, classes, interfaces, enums, constants).
Each function reads one construction; the comment above it shows its form (the notation is in syntax.parser).

`public function topLevelDeclaration(parser: Parser in default): Node`  
ccode { C } | ccode "FILE" ; | cinclude "HEADER" ; | native ... | test function ... | const ... | let ... | function ... | struct ... | [synchronized] class ... | interface ... | enum ... | native type ...  
<sub>línea 20</sub>

`function testFunction(parser: Parser in default): FunctionDecl`  
(after `test`) function NAME ( [ NAME : Type ] ) : void block  
<sub>línea 65</sub>

`function constant(parser: Parser in default): Node`  
(after `const`) NAME : Type = expression ;  
<sub>línea 81</sub>

`public function parameter(parser: Parser in default, typeRequired: bool): Param`  
NAME : Type [ in lives ] (in a lambda: NAME [ : Type ])  
<sub>línea 90</sub>

`public function parameters(parser: Parser in default): Param[*]`  
( [ parameter ( , parameter )* ] )  
<sub>línea 104</sub>

`public function functionDeclaration(parser: Parser in default, isOverride: bool, withBody: bool): FunctionDecl`
<sub>línea 112</sub>

`function operatorDeclaration(parser: Parser in default): FunctionDecl`  
operator ( + | - | | / | % | == | < ) parameters : Type block  
<sub>línea 156</sub>

`function structDeclaration(parser: Parser in default): StructDecl`  
(after `struct`) NAME { ( field | static ... | function ... | operator ... )* }  
<sub>línea 170</sub>

`function classDeclaration(parser: Parser in default, isSynchronized: bool): ClassDecl`  
(after `class`) NAME [ extends NAME ] [ implements NAME ( , NAME )* ] { ( field | static ... | [override] function ... | native function ... | native let ... | operator ... )* }  
<sub>línea 198</sub>

`public function cBodied(p: Parser in default, declaration: FunctionDecl in default): void`  
native function f(params): T { C } (a method, a static function): the body is C. It becomes a C function the compiler writes (its parameters with their C types and names), and f calls it. In a class for one system (it implements UnixPlatform...), f calls it only there (elsewhere it panics; the C of that system reaches no other).  
<sub>línea 267</sub>

`function method(parser: Parser in default, ofSynchronizedClass: bool, isOverride: bool): FunctionDecl`  
A method of a class: in a synchronized class it may say `wait until`.  
<sub>línea 286</sub>

`function interfaceDeclaration(parser: Parser in default): InterfaceDecl`  
(after `interface`) NAME [ extends NAME ( , NAME )* ] { ( function NAME parameters [ : Type ] ... ; | static function ... )* }  
<sub>línea 294</sub>

`public function staticFunction(parser: Parser in default, owner: String in default): void`  
(after `static`, inside the type `owner`) function ... | native function ... = C ;  
<sub>línea 319</sub>

`function enumDeclaration(parser: Parser in default): EnumDecl`  
(after `enum`) NAME { [ variant ( , variant )* [ , ] ] } variant: NAME [ parameters ]  
<sub>línea 339</sub>

`public function field(parser: Parser in default): FieldDecl`  
let NAME : Type [ = expression ] ;  
<sub>línea 358</sub>

---

## syntax.parser.expressions

`src/compiler/syntax/parser/expressions.lar` · 443 líneas · 22 funciones
syntax.parser.expressions: expressions, from the lowest precedence to the highest.
Each function reads one construction; the comment above it shows its form (the notation is in syntax.parser).

`public function expression(parser: Parser in default): Expr`  
ternary [ in ( heap | default | byte[N] | expression ) ]: where a created value lives  
<sub>línea 17</sub>

`function ternary(parser: Parser in default): Expr`  
coalesce [ ? ternary : ternary ] (right to left)  
<sub>línea 30</sub>

`public function coalesce(parser: Parser in default): Expr`  
binary operators [ ?? coalesce ]  
<sub>línea 40</sub>

`public function level(kind: TokenType): int32`  
The level of a binary operator, from the loosest (1) to the tightest; 0: not one. || && == != < <= > >= (and `is`) | ^ & << >> + - / %  
<sub>línea 51</sub>

`function binaryFrom(parser: Parser in default, minimum: int32): Expr`  
cast ( OPERATOR cast ... | is qualified NAME [ NAME ] )*: the operators of level `minimum` or tighter, each one left-associative (precedence climbing: the right side takes only tighter operators).  
<sub>línea 70</sub>

`function cast(parser: Parser in default): Expr`  
unary ( as Type )*  
<sub>línea 89</sub>

`function unary(parser: Parser in default): Expr`  
( - | ! | ~ | & ) unary | postfix  
<sub>línea 103</sub>

`function postfix(parser: Parser in default): Expr`  
primary ( ( arguments ) | . NAME | . NAME { fields } | [ expression ] | ! )*  
<sub>línea 110</sub>

`function methodReference(parser: Parser in default, target: Expr in default): Expr`  
Module::function, variable::method, self::method: a lambda that calls it with its own parameters. The parameters come from the function type expected there (the analyzer adds them).  
<sub>línea 145</sub>

`function referenceLambda(callee: Expr in default): Lambda`  
The lambda of a reference: its body calls `callee` (the analyzer adds the parameters).  
<sub>línea 154</sub>

`function primary(parser: Parser in default): Expr`  
NUMBER | "TEXT" | true | false | null | self | super . NAME | { fields } | [ expressions ] | switch ... | NAME [ { fields } ] | lambda | ( expression )  
<sub>línea 163</sub>

`function objectLiteral(parser: Parser in default, typeName: String in default, line: int32): ObjectLit`  
{ [ field ( , field )* [ , ] ] } field: NAME : expression | NAME | expression  
<sub>línea 210</sub>

`function lambdaAhead(parser: Parser in default): bool`  
Is a lambda next: ( ... ) followed by -> ?  
<sub>línea 231</sub>

`function lambda(parser: Parser in default): Lambda`  
( [ parameter ( , parameter )* ] ) -> block  
<sub>línea 250</sub>

`public function switchExpression(parser: Parser in default, line: int32): SwitchExpr`  
(after `switch`) ( expression ) { case* } case: ( case pattern ( , pattern )* | default ) [ when expression ] -> ( block | throw expression ; | expression ; )  
<sub>línea 263</sub>

`function pattern(parser: Parser in default): Pattern`  
null | constant | qualified NAME [ NAME ] | qualified NAME { [ NAME [ : NAME ] ( , ... )* ] } [ NAME ] (a value, a type with its binding, or an enum variant with its fields)  
<sub>línea 306</sub>

`function string(parser: Parser in default, token: Token in default): StringLit`  
"Hello ${name}": the texts, and the parsed expressions between them.  
<sub>línea 334</sub>

`function interpolation(parser: Parser in default, inner: String in default, line: int32): Expr`  
The expression inside ${...}: its own tokens, read with this parser, then back to the string's.  
<sub>línea 370</sub>

`function binary(operatorText: String in default, left: Expr in default, right: Expr in default, line: int32): Expr`
<sub>línea 383</sub>

`public function waitFirst(line: int32, condition: Expr in default, body: Stmt[*] in default): Stmt[*]`  
wait until (cond): the body starts with `while (!(cond)) { self.__wait(); }`. The lock is held when the body starts; __wait (a name no program can write) lets it go while waiting, and every method of the object that ends wakes the waiters to look at their condition again.  
<sub>línea 392</sub>

`public function optionalFollows(next: TokenType): bool`  
After `as T`, a '?' makes T optional only when what follows can come after a type (x as int64? ?? 0, (x as T?), x as T?;). Followed by the start of an expression it is a ternary: x as int64 ? a : b.  
<sub>línea 404</sub>

`function dottedPath(value: Expr): String`  
a, a.b, a.b.c (only names), or "".  
<sub>línea 412</sub>

---

## syntax.parser.natives

`src/compiler/syntax/parser/natives.lar` · 574 líneas · 19 funciones
syntax.parser.natives: what comes from C (native functions, types, structs and values; cinclude and ccode).
Each function reads one construction; the comment above it shows its form (the notation is in syntax.parser).

`public function nativeDeclaration(parser: Parser in default, line: int32): Node`  
(after `native`) function NAME ( [ parameter ( , parameter )* [ , ... ] ] ) [ : Type ] [ = C ] [ released by NAME ] ; a C function const NAME : Type [ = C ] ; let NAME : Type [ = NAME ] ; a C constant, macro or global struct NAME [ = C ] { ( let NAME : Type [ = NAME ] ; | function ... | static ... )* } a C struct, by value (in a native interface: type NAME [ = C ] { ... }, a struct or a union of C, by value) type NAME [ = CTYPE | = ( Type, ... ) -> Type ] [ released by NAME ] ( ; | { member* } ) a C type type NAME { ... } (std) a type the compiler knows  
<sub>línea 23</sub>

`public function nativeInterface(parser: Parser in default, owner: String in default, opened: bool): NativeInterfaceDecl`  
(after `native interface`) NAME STRING ( , STRING )* [ extends NAME ( , NAME )* ] { ( function ... ; | type NAME ... ( ; | { fields } ) | const ... ; | let ... )* } What C headers give, under one name: Name.f(...) calls the C function f. In a class (`owner`) it is its own, static: only on the class's system. In a class that implements UnsafeTask (`opened`) its functions are found when the task runs, in the library that loader.bind(Name, "library") opens.  
<sub>línea 45</sub>

`function openedFunctions(parser: Parser in default, declaration: NativeInterfaceDecl in default, functions: ExternFunctionDecl[*] in default): void`  
The functions of an interface of an UnsafeTask are found when the task runs: each call goes through a pointer of the header's own type (so the C compiler still checks it), and a C function binds them all to an opened library. The interface's name, as a value, is that function (loader.bind(Name, "...")).  
<sub>línea 127</sub>

`function typeWithFields(parser: Parser in default): bool`  
Whether the type that starts here has fields: a '{' comes before its ';'. Then it is a struct or a union of C, by value; without fields it is a pointer (type FILE: a FILE*).  
<sub>línea 181</sub>

`function cNames(text: String, into: String[*] in default): void`  
The C names in C text (struct tm*: struct, tm), added to `into`.  
<sub>línea 193</sub>

`function atCText(parser: Parser in default): bool`  
At C text: c"...".  
<sub>línea 207</sub>

`function cTarget(parser: Parser in default, what: String): String`  
[ = NAME | = struct NAME | = c"C" ]: what a native declaration is in C; "" without '='.  
<sub>línea 210</sub>

`function nativeFunctionOfC(parser: Parser in default): ExternFunctionDecl`  
(after `native function`) NAME ( [ parameter ( , parameter )* [ , ... ] ] ) [ : Type ] [ = C ] [ released by NAME ] ;  
<sub>línea 224</sub>

`function nativeValue(parser: Parser in default): Node`  
(after `native`) ( const NAME : Type [ = C ] | let NAME : Type [ = NAME ] ) ;  
<sub>línea 262</sub>

`function nativeStruct(parser: Parser in default, what: String): StructDecl`  
(after `native struct`) NAME [ = C ] { ( let NAME : Type [ = NAME ] ; | function ... | static ... )* }  
<sub>línea 281</sub>

`function cField(parser: Parser in default): FieldDecl`  
let NAME : Type [ = NAME ] ; a field of a C struct (after '=': its name in C)  
<sub>línea 304</sub>

`function nativeCType(parser: Parser in default, name: Token in default): Node`  
(after `native type NAME`) [ = CTYPE ] [ released by NAME ] ( ; | { member* } ) CTYPE: [ struct ] NAME *... or c"C TYPE"; without '=' it is opaque (void*)  
<sub>línea 320</sub>

`function nativeMembers(parser: Parser in default, declaration: ExternTypeDecl in default): void`  
{ ( let NAME : Type [ = NAME ] ; | native function ... | native let ... | function ... | static ... )* } The members of a C type: its fields (when it is a pointer to a C struct), functions of C that take it first (self), and functions written in Larimar.  
<sub>línea 354</sub>

`function nativeMember(p: Parser in default, owner: String in default, line: int32, property: bool, isStatic: bool): FunctionDecl`  
(after `native function` or `native let`, in a native type) NAME parameters [ : Type ] [ in lives ] [ throws Type ] = ( C | expression ) ; (let: NAME : Type = ...) With `= C` (a name, or "C text"), the method calls that C function with self first: before it only the memory of the call, when the first parameter is one (m: byte[*]). Any other expression is Larimar.  
<sub>línea 406</sub>

`public function languageType(parser: Parser in default, line: int32): NativeTypeDecl`  
(after `type`) NAME { ( static ... | let NAME : Type [ = expression ] ; | operator ... ; | function ... ( ; | block ) )* } A type of the language (String, Any), in std.lang: what has no body the compiler writes.  
<sub>línea 473</sub>

`function nativeType(parser: Parser in default, line: int32, name: Token in default): NativeTypeDecl`  
(after `native type NAME`) { ( static ... | native function ... | native let ... | native operator ... | function ... )* } The methods of a type the compiler knows (String, Any): only in the standard library.  
<sub>línea 484</sub>

`public function nativeFunction(parser: Parser in default, line: int32): FunctionDecl`  
(after `native function`) NAME parameters [ : Type ] [ in lives ] [ throws Type ] [ = expression ] ;  
<sub>línea 517</sub>

`public function nativeProperty(parser: Parser in default, line: int32): FunctionDecl`  
(after `native let`) NAME : Type [ = expression ] ; A value read without parentheses and never assigned (s.length). Without `= expression` the compiler gives it; with it, it is that expression.  
<sub>línea 547</sub>

`function nativeOperator(parser: Parser in default, line: int32): FunctionDecl`  
(after `native operator`) ( [ ] | SYMBOL ) parameters : Type ;  
<sub>línea 560</sub>

---

## syntax.parser.statements

`src/compiler/syntax/parser/statements.lar` · 172 líneas · 8 funciones
syntax.parser.statements: statements and blocks.
Each function reads one construction; the comment above it shows its form (the notation is in syntax.parser).

`public function variable(parser: Parser in default): VarDecl`  
let NAME : Type [ = expression ] ;  
<sub>línea 14</sub>

`public function block(parser: Parser in default, what: String): Stmt[*]`  
{ statement* }  
<sub>línea 25</sub>

`function statement(parser: Parser in default): Stmt`  
let ... | return [ expression ] ; | if ... | while ( expression ) block | for ... | break ; | continue ; | throw expression ; | yield expression ; | try ... | block | switch ... | assignment or call  
<sub>línea 37</sub>

`function assignmentOrCall(parser: Parser in default, line: int32): Stmt`  
expression [ ( = | += | -= | ... ) expression ] ; (a += b is a = a + b)  
<sub>línea 99</sub>

`function misplaced(parser: Parser in default, token: Token, message: String): Stmt`  
Something that does not go here: the error, and an empty statement.  
<sub>línea 117</sub>

`function ifStatement(parser: Parser in default, line: int32): IfStmt`  
(after `if`) ( expression ) block [ else ( if ... | block ) ]  
<sub>línea 123</sub>

`function forStatement(parser: Parser in default, line: int32): ForStmt`  
(after `for`) ( [ NAME , ] NAME in expression [ .. expression ] ) block  
<sub>línea 140</sub>

`function tryStatement(parser: Parser in default, line: int32): TryStmt`  
(after `try`) block ( catch ( qualified NAME NAME ) block )+  
<sub>línea 159</sub>

---

## syntax.parser.types

`src/compiler/syntax/parser/types.lar` · 73 líneas · 2 funciones
syntax.parser.types: types as they are written (int32, String?, T[*], (A) -> R thread safe).
Each function reads one construction; the comment above it shows its form (the notation is in syntax.parser).

`public function type(parser: Parser in default): TypeRef`  
( qualified NAME | ( Type ) | ( [ Type ( , Type )* ] ) -> Type ) suffix* suffix: [ ] | [ ] | [ expression ] | ? | and after a function type: [ thread safe ]  
<sub>línea 13</sub>

`function threadSafe(parser: Parser in default, functionType: TypeRef in default): TypeRef`  
[ thread safe ] after a function type: other threads may call it at the same time. Two words, like `wait until`; neither is reserved. With function types inside function types it goes to the nearest one on its left; parentheses choose another: ((A) -> (B) -> C) thread safe.  
<sub>línea 63</sub>

---

## semantics.analyzer

`src/compiler/semantics/analyzer.lar` · 343 líneas · 19 funciones
semantics.analyzer: semantic analysis (Analyzer.java), part 1: declarations, statements, regions
and the final passes. Expressions are in checkexpr.lar.

- Types: declarations, expressions with expected types, implicit conversions.
- Regions: every value that references memory carries the region of that memory;
storing it somewhere that outlives the region is an error (fix: .clone()).
- Captures: a lambda captures by value; captured variables cannot change.
- Errors: throws/try/catch are checked; every throwing call is handled.
- Switch: patterns resolved, enums covered completely.

### class `Diag`

### class `Analysis`
The state of the analysis: its scopes and frames, every symbol, what it checks once the bodies are read (lifetimes, mutations, threads), and its errors.

`public function newAnalysis(): Analysis`  
An analysis that has read nothing: its global frame and scope.  
<sub>línea 60</sub>

`public function useAnalysis(state: Analysis in default): void`  
Makes `state` the one the compiler works on.  
<sub>línea 70</sub>

`public function error(line: int32, msg: String): void`
<sub>línea 73</sub>

`public function wrong(line: int32, msg: String): Type`  
Reports an error where a type is expected: the result is the error type.  
<sub>línea 78</sub>

`public function bindingSymbol(name: String in default, type: Type in default, line: int32, region: Region in default): Symbol`  
A symbol for the name after `is`, declared later where the test is true (see narrow).  
<sub>línea 84</sub>

### class `HandledSet`

### class `FrameState`

### enum `MutK`

### class `Mutation`

### enum `DefK`

### class `Deferred`

### class `ThreadRun`

`public function frame(): Frame`
<sub>línea 142</sub>

`public function state(): FrameState`
<sub>línea 143</sub>

`public function analyze(program: Program in default): void`
<sub>línea 150</sub>

`public function pushFrame(kind: FrameKind, ret: Type? in default, throwsType: Type? in default, lambda: LambdaInfo? in default,`
<sub>línea 226</sub>

`public function popFrame(restore: Scope in default): void`
<sub>línea 240</sub>

`public function pushScope(): void`
<sub>línea 246</sub>

`public function popScope(): void`
<sub>línea 248</sub>

`public function block(): Scope`  
The block the current statement is in (names are declared there, not in the statement).  
<sub>línea 251</sub>

`public function declare(name: String in default, kind: SymbolKind, type: Type in default, line: int32): Symbol`
<sub>línea 253</sub>

`public function lookup(name: String): Symbol?`
<sub>línea 274</sub>

`public function narrowedType(symbol: Symbol): Type?`
<sub>línea 284</sub>

`public function noteCapture(symbol: Symbol in default, line: int32): void`  
Records that the current lambda (and every lambda in between) captures `s`.  
<sub>línea 297</sub>

`function checkMutations(): void`
<sub>línea 325</sub>

`function checkMemoryUses(): void`
<sub>línea 338</sub>

---

## semantics.analyzer.classes

`src/compiler/semantics/analyzer/classes.lar` · 252 líneas · 11 funciones
semantics.analyzer.classes: classes and interfaces: fields, methods, what a class inherits and what it implements.

`public function validateClasses(): void`
<sub>línea 14</sub>

`function processClass(classInfo: ClassInfo in default, done: Any): void`
<sub>línea 65</sub>

`function implementedOf(classInfo: ClassInfo, name: String): String`  
The interface, of those a class implements, that has a method of this name ("" when none does).  
<sub>línea 132</sub>

`function sameLives(a: Param[*], b: Param[*]): bool`
<sub>línea 140</sub>

`function sameThrows(a: Type?, b: Type?): bool`
<sub>línea 148</sub>

`function throwsText(t: Type?): String`
<sub>línea 150</sub>

`function checkSameSig(classInfo: ClassInfo, method: MethodInfo, parentMethod: MethodInfo, line: int32): void`
<sub>línea 152</sub>

`public function validateInterfaces(): void`
<sub>línea 164</sub>

`public function checkFieldDefaults(): void`
<sub>línea 192</sub>

`function isConstantExpr(e: Expr): bool`
<sub>línea 211</sub>

`public function checkMain(): void`
<sub>línea 238</sub>

---

## semantics.analyzer.compact

`src/compiler/semantics/analyzer/compact.lar` · 351 líneas · 15 funciones
semantics.analyzer.compact: Memory.compact: where a memory may be compacted.

### class `CompactCall`
A call to Memory.compact(m): its memory, and the variables that could be seen where it is.

### class `Mixing`
Where data of another memory of the same block was stored in a memory with a name.

`public function noteCompact(c: Call in default, m: Symbol in default): void`  
Memory.compact(m) here: m must belong to this function, and the call cannot be inside a for over data.  
<sub>línea 36</sub>

`function checkCompacts(): void`  
Once every variable's memory is known: the variables of the compacted memory move with it; any other variable of its block (or of a block inside it) that may point into it would be left pointing to freed memory, so it is an error. So is data of another memory of the block stored in it.  
<sub>línea 60</sub>

`function notMovable(t: Type in default, seen: Any in default): String`  
What a value of this type may hold that compact() cannot move ("" when nothing): "a lambda", "a thread"...  
<sub>línea 100</sub>

`public function resolveRegions(): void`
<sub>línea 143</sub>

`public function objectOf(e: Expr): Expr?`  
The object of a field or element access: a.b and a[i] give a.  
<sub>línea 164</sub>

`public function throughReference(target: Expr): bool`  
Is the target reached through a class object or list (shared, not a captured copy)?  
<sub>línea 171</sub>

`public function isReference(type: Type): bool`
<sub>línea 180</sub>

`public function storageRegion(obj: Expr in default): Region`  
Where the fields or elements of `obj` are stored.  
<sub>línea 185</sub>

`public function placeFor(obj: Expr in default): Place`  
The memory new data should go to when stored inside `obj`.  
<sub>línea 197</sub>

`public function rootSymbol(e: Expr in default): Symbol?`
<sub>línea 205</sub>

`public function isLValue(e: Expr): bool`
<sub>línea 214</sub>

`public function analyzeReturn(r: ReturnStmt in default): void`
<sub>línea 221</sub>

`function analyzeWhen(ifStmt: IfStmt in default): void`  
An if for platforms (IfStmt.platform): a ... b ... else. Every branch is checked, each for its platform, in the block around (there is no block of its own). A name every branch declares, with the same type, stays for the code after it (one C name for all of them); what only some declare belongs to its branch.  
<sub>línea 253</sub>

`function whenBranch(body: Stmt[*] in default, platform: String in default, branch: int32, syms: int32[*] in default, branchOf: int32[*] in default, blockScope: Scope in default): void`  
One branch of an if for platforms, checked for `platform`; what it declares is hidden until every branch is seen.  
<sub>línea 312</sub>

`public function analyzeIf(ifStmt: IfStmt in default): void`
<sub>línea 332</sub>

---

## semantics.analyzer.declarations

`src/compiler/semantics/analyzer/declarations.lar` · 721 líneas · 29 funciones
semantics.analyzer.declarations: what a program declares: the system of each class, C declarations, constants and signatures.

`function requireAscii(name: String, line: int32, what: String): void`
<sub>línea 22</sub>

`function interfaceDecl(name: String): InterfaceDecl?`
<sub>línea 32</sub>

`function classDecl(name: String): ClassDecl?`
<sub>línea 37</sub>

`function withAncestors(names: String[] in default, line: int32): String[*]`  
The interfaces given, with every one they extend, each once (in the order found).  
<sub>línea 43</sub>

`function platformOfClass(name: String, line: int32): String`  
"linux", "macos", "windows", "unix" or "" (every system), from the interfaces of the class and its superclasses.  
<sub>línea 62</sub>

`function narrower(a: String, b: String, owner: String, line: int32): String`  
Of two systems, the narrower one (linux within unix); two that do not overlap are an error.  
<sub>línea 84</sub>

`function assignPlatforms(program: Program in default): void`  
The C of a class for one platform goes only there: its cinclude, its ccode and the C functions of its methods get that platform, and each method with a C body calls its function only there (elsewhere it panics). With --target nothing is left to the C compiler: the C of the target's classes is plain C, and that of the others is not generated.  
<sub>línea 99</sub>

`function platformNumber(platform: String): int32`  
The number std.os gives each platform (its platformNumber).  
<sub>línea 137</sub>

`function onlyOn(c: ClassDecl in default, system: String in default): void`  
The methods with a C body of a class for one platform: they call their C only there; elsewhere they panic.  
<sub>línea 147</sub>

`function onlyOnFunction(m: FunctionDecl in default, owner: String, system: String in default): void`  
A method or static function with a C body, of a class (`owner`) for one platform: its C only there.  
<sub>línea 154</sub>

`public function collect(program: Program in default): void`
<sub>línea 170</sub>

`function typeNameTaken(name: String, line: int32): bool`
<sub>línea 283</sub>

`function collectStatic(f: FunctionDecl in default): void`  
Type.name: a function that belongs to a type, without self.  
<sub>línea 296</sub>

`function instanceMethodNamed(t: String in default, name: String): bool`  
An instance method `name` of the type `t` (to reject a static function with the same name).  
<sub>línea 312</sub>

`function functionNameTaken(name: String, line: int32): bool`
<sub>línea 322</sub>

`public function constants(program: Program in default): void`
<sub>línea 337</sub>

`public function constIntText(v: ConstVal): String`
<sub>línea 369</sub>

`public function signatures(program: Program in default): void`
<sub>línea 376</sub>

`public function externValue(v: ExternValueDecl in default): void`  
extern const NAME: T; extern let NAME: T; a name C has (a constant, a macro, a global).  
<sub>línea 552</sub>

`function externResource(e: ExternTypeInfo in default): void`  
released by f: f takes exactly one X and returns nothing useful; only release() calls it.  
<sub>línea 570</sub>

`function textReleaser(functionInfo: FunctionInfo in default): void`  
...: String = c_f released by r: r is a native function that takes the text (one String); only the compiler calls it.  
<sub>línea 589</sub>

`function externResourceRules(functionInfo: FunctionInfo in default): void`  
A C function that makes a resource returns X? (C fails: null). A resource goes to C as X, not X?.  
<sub>línea 611</sub>

`function resolveMethodSig(method: MethodInfo in default, m: FunctionDecl in default): void`
<sub>línea 623</sub>

`function resolveSig(params: Param[*] in default, ret: TypeRef in default): Type`
<sub>línea 636</sub>

`function callbackProblem(type: Type): String`  
What a function type given to C may have ("" when it is fine): numbers, bool, String (a char*), String?, pointers (void*, the "this"), native types that are not resources and C structs; a T[] of numbers, bool or String takes its count from the integer before it (sqlite3_exec: int argc, char** argv). It returns void, a number, bool, a pointer or a native type: a text would have no memory to live in.  
<sub>línea 659</sub>

`function isPlainNumber(type: Type): bool`
<sub>línea 686</sub>

`function resolveThrows(t: TypeRef? in default): Type?`
<sub>línea 690</sub>

`public function isByteArrayRef(typeRef: TypeRef): bool`  
byte[N], byte[], byte[*] as written.  
<sub>línea 703</sub>

`function memoryParams(params: Param[*] in default, body: Stmt[*] in default): bool[*]`  
byte-array parameters used after `in` inside the body are memory parameters.  
<sub>línea 710</sub>

---

## semantics.analyzer.flow

`src/compiler/semantics/analyzer/flow.lar` · 740 líneas · 42 funciones
semantics.analyzer.flow: what a function's result may point to, and whether the function creates it.

`public function flowSummaries(): void`
<sub>línea 29</sub>

`function overridden(method: MethodInfo): MethodInfo[*]`  
The methods that `m` writes again: those of its name in the classes above its own.  
<sub>línea 148</sub>

`public function builtinFresh(name: String): bool`  
Built-in methods whose result is new data, or a plain value: their receiver can be a temporary.  
<sub>línea 162</sub>

`public function viewMethod(name: String): bool`  
May a method call's result point to its receiver?  
<sub>línea 173</sub>

`public function creatingMethod(name: String): bool`  
Some method of that name may create its result.  
<sub>línea 178</sub>

`function linked(e: Expr): Expr`  
module.name, after linking, is the name itself.  
<sub>línea 181</sub>

`public function callMemory(functionInfo: FunctionInfo): bool`  
An extern whose first parameter is a memory: it creates in the memory of the call, which is not written.  
<sub>línea 184</sub>

`function makesResource(functionInfo: FunctionInfo): bool`  
A C function that makes a resource (returns X?, X released by f): the resource lives where its result goes.  
<sub>línea 187</sub>

`function steadyParams(params: Param[*] in default, body: Stmt[*]): Param[*]`  
The parameters that keep their written type in the whole body: no variable of the body takes their name.  
<sub>línea 200</sub>

`function lengthIsNumber(name: String): bool`  
name.length, with name a parameter written as String or a list: a number.  
<sub>línea 222</sub>

`function mentioned(e: Expr, out: Any, viaPlaced: bool): void`
<sub>línea 232</sub>

`function rootName(start: Expr): String`
<sub>línea 284</sub>

`function flowOf(params: Param[*] in default, body: Stmt[*]): Any`  
The names whose data may be in what the body returns (flowNames), reading its parameters with their written types.  
<sub>línea 298</sub>

`public function returnsArgs(params: Param[*] in default, body: Stmt[*], method: bool): bool`  
May the result point to data of a parameter (or of self)? On the safe side: the regions still check every return.  
<sub>línea 306</sub>

`function flowNames(body: Stmt[*], viaPlaced: bool): Any`  
The names whose data may flow into what the body returns: used in a return, or in the value of a variable that is, and what is passed to a method of one of them (it may keep it). `viaPlaced`: also what is used inside `... in m` (it is pointed to, but not created where the result goes).  
<sub>línea 319</sub>

`function entries(t: Any): int32`  
How many named entries a table has.  
<sub>línea 366</sub>

`function bindsFlow(switchExpr: SwitchExpr, flow: Any): bool`
<sub>línea 372</sub>

### class `Declared`
The types written for the parameters and the variables of a body (by name; the last one wins).

`function declaredType(d: Declared, name: String): TypeRef?`
<sub>línea 390</sub>

`function isDeclared(d: Declared, name: String): bool`
<sub>línea 399</sub>

`function createsResult(body: Stmt[*], ret: Type in default, params: Param[*]): bool`  
May the body create its result (in the memory the caller gives)? On the safe side: when not, the result only points to existing data (arguments, self, globals) and the call gives no memory.  
<sub>línea 405</sub>

`function refsOf(t: TypeRef?): bool`  
Has a written type references to memory? (unknown: yes)  
<sub>línea 436</sub>

`function creates(start: Expr?, any: bool, declared: Declared): bool`  
May this expression create data where it is placed? `any`: the result is an Any (a struct put in it is copied).  
<sub>línea 452</sub>

`function switchCreates(switchExpr: SwitchExpr, any: bool, declared: Declared): bool`
<sub>línea 485</sub>

`function yieldsCreate(block: Stmt[*], any: bool, declared: Declared): bool`  
Does a block arm of a switch yield a value it creates? (a local it yields lives in the block: an error, not a result)  
<sub>línea 494</sub>

`function staticCallee(call: Call): FunctionInfo?`  
Type.name(...) when it calls a static function.  
<sub>línea 504</sub>

`function callCreates(call: Call, any: bool, declared: Declared): bool`
<sub>línea 509</sub>

`function methodCreates(member: Member, call: Call, coarse: bool, any: bool, declared: Declared): bool`
<sub>línea 536</sub>

`public function valuePlace(name: String, global: bool): Place`  
Where a variable's value is created: the caller's memory if it is returned, else its block's (globals: forever).  
<sub>línea 561</sub>

`public function blockRegion(b: Scope in default): Region`  
The memory of a block (created the first time something lives in it).  
<sub>línea 567</sub>

`public function returnedNames(body: Stmt[*]): Any`  
The locals whose data may end up in the result: they are created where the caller says.  
<sub>línea 570</sub>

`public function requireOutlives(value: Expr in default, storage: Region in default, line: int32, target: String): void`
<sub>línea 574</sub>

`public function lifetime(value: Region in default, storage: Region in default, line: int32, msg: String in default): void`  
value must live at least as long as storage; checked now, or at the end if a variable is involved.  
<sub>línea 585</sub>

`public function lifetimeOf(value: Expr in default, storage: Region in default, line: int32, msg: String in default, role: String): void`  
The same, knowing the expression and what it is for (a field of a literal, a thrown error), to name the culprit.  
<sub>línea 591</sub>

`public function mustLiveForever(value: Region in default, line: int32, msg: String in default): void`
<sub>línea 596</sub>

`function fill(msg: String, v: Region, storage: Region): String`
<sub>línea 600</sub>

`public function runCheck(deferred: Deferred in default, resolve: bool): void`
<sub>línea 617</sub>

`function placementFor(region: Region): String`  
The `in` that puts a copy where a region lives, when the code can say it: " in default", " in m", or "".  
<sub>línea 643</sub>

`function culprit(deferred: Deferred in default, v: Region, storage: Region, resolve: bool): String`  
A message that names what lives too little, and the code that fixes it, when the value is something the programmer wrote: a lambda (its capture), a view (its text), a variable. "" when there is none.  
<sub>línea 652</sub>

`function isFunctionValue(e: Expr): bool`  
A lambda or a function value (it has no clone()).  
<sub>línea 714</sub>

`function parameterHint(name: String, storage: Region): String`  
For a parameter that must live where it is kept: its declaration with `in`.  
<sub>línea 717</sub>

`function viewCulprit(e: Expr, v: Region, target: String, lives: String, keep: String): String`  
x.trim(), x.substring(...)...: the result shares the bytes of x.  
<sub>línea 724</sub>

`function clonesInside(lambda: Lambda, name: String): bool`  
Does the body of the lambda call name.clone()? (It runs when the lambda is called, not when it is made.)  
<sub>línea 732</sub>

---

## semantics.analyzer.narrowing

`src/compiler/semantics/analyzer/narrowing.lar` · 273 líneas · 15 funciones
semantics.analyzer.narrowing: where a T? variable is known not to be null.

`public function nonNull(c: Expr in default, onTrue: bool): Symbol[*]`  
The optional locals that are not null when `c` evaluates to `onTrue` (and the names after `is`).  
<sub>línea 20</sub>

`function facts(c: Expr in default, onTrue: bool, out: Symbol[*] in default): void`
<sub>línea 26</sub>

`public function hasSymbol(list: Symbol[*], symbol: Symbol): bool`
<sub>línea 52</sub>

`public function narrow(syms: Symbol[*] in default): void`  
Narrows in the current scope; an assignment to the variable ends it (see analyzeStmts).  
<sub>línea 60</sub>

`public function unnarrow(syms: Symbol[*]): void`
<sub>línea 77</sub>

`public function leaves(body: Stmt[*]): bool`  
Does the block always leave (return, throw, break, continue)?  
<sub>línea 92</sub>

`public function reassignedNames(body: Stmt[*] in default): Any`  
The variables a body assigns somewhere (not inside lambdas).  
<sub>línea 103</sub>

`public function assigns(body: Stmt[*] in default, name: String): bool`
<sub>línea 113</sub>

`public function analyzeFor(f: ForStmt in default): void`
<sub>línea 122</sub>

`function loopBody(body: Stmt[*] in default): void`
<sub>línea 187</sub>

`public function analyzeThrow(t: ThrowStmt in default): void`
<sub>línea 196</sub>

`public function requireHandled(enumInfo: EnumInfo, line: int32, what: String): void`
<sub>línea 209</sub>

`public function analyzeYield(yieldStmt: YieldStmt in default): void`
<sub>línea 225</sub>

`public function analyzeTry(t: TryStmt in default): void`
<sub>línea 237</sub>

`function hasEnum(list: EnumInfo[*], enumInfo: EnumInfo): bool`
<sub>línea 267</sub>

---

## semantics.analyzer.order

`src/compiler/semantics/analyzer/order.lar` · 145 líneas · 8 funciones
semantics.analyzer.order: orders that must exist: globals get their values in order, C structs are defined before they are embedded.

`public function checkGlobalOrder(initializers: Owner[*] in default): void`  
The initial value of a global, and every function it calls however deep, cannot use a global that is initialized after it (or itself): it would find it without its value.  
<sub>línea 14</sub>

`function initializedFrom(g: Symbol in default, k: int32): bool`  
Whether global `g` is the k-th one or one initialized after it.  
<sub>línea 39</sub>

`public function computeTypeOrder(): void`
<sub>línea 53</sub>

`function visitType(type: Type in default, path: Type[*] in default): void`
<sub>línea 68</sub>

`function display(type: Type): String`
<sub>línea 93</sub>

`function typeLine(t: Type): int32`
<sub>línea 95</sub>

`function valueDeps(t: Type in default): Type[*]`  
Types that t's C definition embeds by value.  
<sub>línea 110</sub>

`function addValueDep(out: Type[*] in default, type: Type in default): void`
<sub>línea 138</sub>

---

## semantics.analyzer.statements

`src/compiler/semantics/analyzer/statements.lar` · 484 líneas · 20 funciones
semantics.analyzer.statements: the bodies of functions and methods, statement by statement.

`public function analyzeFunction(functionInfo: FunctionInfo in default): void`
<sub>línea 39</sub>

`public function analyzeMethod(method: MethodInfo in default, selfType: Type in default): void`
<sub>línea 57</sub>

`public function declareParam(p: Param in default, type: Type in default, memory: bool): Symbol`
<sub>línea 74</sub>

`function applyLives(params: Param[*] in default, syms: Symbol[*] in default, mem: bool[*] in default, selfSym: Symbol? in default): void`  
`k: Node in p`, `s: String in default`, `x: T in self`, `x: T in m` (a memory parameter): the parameter's data lives as long as that, so it can be stored there.  
<sub>línea 89</sub>

`function livesRegion(params: Param[*] in default, syms: Symbol[*] in default, mem: bool[*], selfSym: Symbol? in default, start: int32, line: int32): Region?`
<sub>línea 106</sub>

`public function livesHint(value: Region, storage: Region): String`  
When a parameter is stored somewhere longer-lived, the parameter can say so: `k: Node in p`.  
<sub>línea 145</sub>

`public function checkReturns(body: Stmt[*] in default, ret: Type, line: int32, what: String): void`
<sub>línea 164</sub>

`function isPanic(e: Expr): bool`  
panic(...): the program stops there.  
<sub>línea 170</sub>

`public function alwaysExits(body: Stmt[*]): bool`
<sub>línea 176</sub>

`function containsBreak(body: Stmt[*]): bool`
<sub>línea 203</sub>

`public function analyzeStmts(body: Stmt[*] in default): void`
<sub>línea 233</sub>

`public function analyzeBlock(body: Stmt[*] in default): void`
<sub>línea 260</sub>

`function analyzeStmt(s: Stmt in default): void`
<sub>línea 266</sub>

`public function requireBool(cond: Expr in default, what: String): void`
<sub>línea 300</sub>

`public function analyzeVarDecl(v: VarDecl in default): void`
<sub>línea 305</sub>

`function declareHeapMemory(v: VarDecl in default, p: Placed in default, kind: SymbolKind, global: bool): void`
<sub>línea 352</sub>

`function analyzeAssign(asg: AssignStmt in default): void`
<sub>línea 377</sub>

`public function cStructField(field: FieldInfo): bool`  
A field of a C struct (extern type X = struct { ... }).  
<sub>línea 468</sub>

`function memberIsAnyKey(m: Member in default): bool`
<sub>línea 473</sub>

`function describeTarget(t: Expr): String`
<sub>línea 479</sub>

---

## semantics.analyzer.threads

`src/compiler/semantics/analyzer/threads.lar` · 214 líneas · 13 funciones
semantics.analyzer.threads: what a thread can share.

`public function currentOwner(): Owner?`
<sub>línea 13</sub>

`public function edge(from: Owner? in default, to: Owner? in default): void`
<sub>línea 23</sub>

`public function useGlobal(symbol: Symbol in default, line: int32): void`
<sub>línea 27</sub>

`public function callTargets(receiver: Type, method: MethodInfo in default): MethodInfo[*]`  
Every method a call can reach: overrides in subclasses, or the implementations of an interface method.  
<sub>línea 36</sub>

`public function sendable(type: Type in default): bool`  
Can a value of this type be used by two threads at once without a lock?  
<sub>línea 50</sub>

`function sendableIn(t: Type in default, visiting: Any): bool`
<sub>línea 55</sub>

`function implementsInterface(classInfo: ClassInfo in default, i: String): bool`  
Class c implements interface i (itself, or a class it extends).  
<sub>línea 89</sub>

`public function stateFields(name: String in default): String`  
The fields that make objects of class `name` changeable, as text ('a', 'b'), or "" when they have none: an object with no fields, in its class or in any class that extends it, has no state that two threads could change, so it is shared like a value (a set of routes, a strategy). A Thread or a StringBuilder keeps state of its own.  
<sub>línea 104</sub>

`function changeable(type: Type in default): String`  
For the message of a value that cannot be shared: what an ordinary object has that could change.  
<sub>línea 118</sub>

`public function checkSynchronizedClasses(): void`
<sub>línea 124</sub>

`public function checkThreadSafeLambda(lambdaInfo: LambdaInfo in default, line: int32): void`  
A lambda given where a `thread safe` function is expected: checked like the run of a Thread.  
<sub>línea 153</sub>

`public function checkThreadRun(literal: ObjectLit in default): void`  
Thread { run: ... }: a lambda written here, or a synchronized object.  
<sub>línea 158</sub>

`public function checkThreads(): void`
<sub>línea 176</sub>

---

## semantics.expressions

`src/compiler/semantics/expressions.lar` · 553 líneas · 28 funciones
semantics.expressions: semantic analysis (Analyzer.java), part 2: types as written, constants,
expressions, conversions, calls, switch and patterns.

`public function resolveTop(typeRef: TypeRef in default, ctx: int32, what: String): Type`
<sub>línea 39</sub>

`public function resolveValue(typeRef: TypeRef in default, what: String): Type`
<sub>línea 50</sub>

`public function resolveType(typeRef: TypeRef in default): Type`
<sub>línea 55</sub>

`function resolveNamed(typeRef: TypeRef in default): Type`
<sub>línea 101</sub>

`public function note(type: Type in default): void`  
Registers a type (and its parts) so the generator emits it.  
<sub>línea 122</sub>

`public function noted(type: Type in default): Type`  
Notes that the generated C needs the type, and returns it.  
<sub>línea 152</sub>

`public function check(e: Expr in default, expected: Type? in default, place: Place in default): Type`
<sub>línea 161</sub>

`function checkInner(e: Expr in default, expected: Type? in default, place: Place in default): Type`
<sub>línea 169</sub>

`function checkUnwrap(unwrap: Unwrap in default, expected: Type? in default, place: Place in default): Type`
<sub>línea 197</sub>

`public function checkIntValue(v: ConstVal, line: int32, expected: Type? in default): Type`  
An integer literal where `expected` is wanted.  
<sub>línea 207</sub>

`function checkString(s: StringLit in default, place: Place in default): Type`
<sub>línea 223</sub>

`function checkIdent(id: Ident in default, expected: Type? in default): Type`
<sub>línea 236</sub>

`function checkSelf(se: Expr in default): Type`
<sub>línea 272</sub>

`public function lookupIn(sc: Scope in default, name: String): Symbol?`
<sub>línea 292</sub>

`public function variantFieldNames(variant: VariantInfo in default): String`
<sub>línea 300</sub>

`public function typeNamed(e: Expr): String`  
The type an expression names (Order, String, a type of another module), or "".  
<sub>línea 308</sub>

`public function enumNamed(e: Expr): EnumInfo?`
<sub>línea 314</sub>

`public function memoryNamed(e: Expr): Symbol?`  
The memory a name refers to, if it is one.  
<sub>línea 319</sub>

`function checkMember(m: Member in default, place: Place in default): Type`
<sub>línea 325</sub>

`public function isProperty(type: Type in default, name: String): bool`  
A value read without parentheses: the length of a String, an array, a list or an Any, or a native let.  
<sub>línea 420</sub>

`public function fieldOf(type: Type in default, name: String): FieldInfo?`
<sub>línea 426</sub>

`public function methodOf(type: Type in default, name: String): MethodInfo?`  
A method of a struct, class or interface (not an operator).  
<sub>línea 432</sub>

`function nativeMethodOf(owner: String, name: String): MethodInfo?`  
A method that a native type declares for a C type.  
<sub>línea 443</sub>

`public function describeExpr(e: Expr): String`
<sub>línea 450</sub>

`function checkIndex(indexExpr: Index in default): Type`
<sub>línea 459</sub>

`public function resolvePlacement(p: Placed in default): Place?`  
The Place written after `in`, or null after reporting an error.  
<sub>línea 480</sub>

`function checkPlaced(p: Placed in default, expected: Type? in default): Type`
<sub>línea 501</sub>

`public function resolveMemory(e: Expr in default): Symbol?`  
`in m`: m must be a memory (a heap memory, or an empty byte[N] that becomes one).  
<sub>línea 521</sub>

---

## semantics.expressions.callbacks

`src/compiler/semantics/expressions/callbacks.lar` · 174 líneas · 5 funciones
semantics.expressions.callbacks: callbacks given to C (spec §D.10). C has no methods: a library that calls
back takes a function and its "this", a void*, which it gives back to the function. A program passes the
same pair, written where it goes:

Sqlite.sqlite3_exec(db!, sql, self::onRow, self, null);     // a method and its object
Sqlite.sqlite3_exec(db!, sql, row, row, null);               // a lambda and itself (its captures)
LibC.qsort(items, count, size, ::compare);                   // a function without state, no this

Here: what may go as the function, what as the void*, and that the two make a pair when both are in the
same call. The C of it (the trampolines) is in codegen.expressions.callbacks.

`public function checkCallbackArg(a: Expr in default, type: Type in default, place: Place in default, what: String in default): void`  
An argument given where C takes a function (`type`, the parameter's function type).  
<sub>línea 23</sub>

`function isObject(e: Expr): bool`  
Before ::, a value (self, a variable): its method, with the object as its this. A module or a type is not one.  
<sub>línea 60</sub>

`function methodCallback(a: Expr in default, m: Member in default, type: Type in default, what: String): void`  
object::method given to C: the same parameters, but the this may be written with the type of its class.  
<sub>línea 68</sub>

`public function checkThisArg(a: Expr in default, type: Type in default, what: String in default): void`  
An argument given where C takes a void*: an object, a function given as a callback, a pointer or null.  
<sub>línea 130</sub>

`public function checkPairs(call: Call in default, params: Type[*] in default, name: String): void`  
When C takes one void* and a callback in the same call, the void* is the callback's "this": the object of a method, the function itself, and nothing for a function without state. Given in two calls (libcurl's CURLOPT_WRITEFUNCTION and CURLOPT_WRITEDATA), the compiler cannot see the pair.  
<sub>línea 156</sub>

---

## semantics.expressions.calls

`src/compiler/semantics/expressions/calls.lar` · 826 líneas · 32 funciones
semantics.expressions.calls: calls: functions, methods, constructors and what the language has built in.

`public function checkAllArgs(call: Call in default): Type`
<sub>línea 31</sub>

`function builtinCall(c: Call in default, kind: BuiltinKind, receiver: Type? in default): void`
<sub>línea 36</sub>

`function throwing(call: Call in default, tt: Type?, what: String): void`  
A call to something that can throw: it must be handled.  
<sub>línea 41</sub>

`public function checkCall(call: Call in default, expected: Type? in default, place: Place in default): Type`
<sub>línea 47</sub>

`function checkMemoryCall(c: Call in default, compact: bool): Type`  
Memory.limit(m, bytes) and Memory.compact(m): they work on the memory itself, so m must be its name. compact() is checked again at the end (checkCompacts), once the memory of every variable is known.  
<sub>línea 96</sub>

`function checkFunctionCall(c: Call in default, functionInfo: FunctionInfo in default, place: Place in default): Type`
<sub>línea 125</sub>

`function inUnsafeTask(): bool`  
Inside a method of a class that implements UnsafeTask (or inside a lambda written in one): there its C runs.  
<sub>línea 174</sub>

`function flowsOf(call: Call, method: MethodInfo): bool[*]`  
The arguments the result of a method call may point to.  
<sub>línea 190</sub>

`public function all(n: int32, b: bool): bool[*]`  
n times b.  
<sub>línea 195</sub>

`public function madeBy(e: Expr in default, method: MethodInfo in default, place: Place in default): Region`  
What a method call creates (only if some method of that name may create its result).  
<sub>línea 202</sub>

`public function placedResult(e: Expr in default, ret: Type in default, place: Place in default): Region`  
A result with data, created where the expression says (like a call's).  
<sub>línea 207</sub>

`function checkSuperCall(c: Call in default, sm: SuperMember in default, place: Place in default): Type`
<sub>línea 213</sub>

`function checkMethodCall(c: Call in default, callee: Member in default, expected: Type? in default, place: Place in default): Type`
<sub>línea 237</sub>

`function checkNativeMethodCall(c: Call in default, callee: Member in default, mi: MethodInfo in default, place: Place in default): Type`
<sub>línea 337</sub>

`function closureCall(c: Call in default, t: Type in default, calleeRegion: Region in default, place: Place in default): Type`
<sub>línea 348</sub>

`public function same(call: Call in default, place: Place in default): Place[*]`  
The same place for every argument.  
<sub>línea 362</sub>

`function checkArgsLives(call: Call in default, params: Type[*] in default, varargs: bool, memParams: bool[*], name: String,`  
Checks arguments, and the `in` of the parameters; returns the meet of the regions of the arguments that reference memory. argPlace: where arguments with data are created (the call's place when the result may point to them). A parameter that says where it lives gets its argument created there: `in default`, `in self`.  
<sub>línea 373</sub>

`function checkArgs(call: Call in default, params: Type[*] in default, varargs: bool, memParams: bool[*], name: String, places: Place[*] in default,`
<sub>línea 433</sub>

`function checkClone(call: Call in default, objectType: Type in default, place: Place in default): Type`
<sub>línea 489</sub>

`function heldResource(t: Type, visiting: Any): String`  
The resource type a value holds (directly or in a field, an element...), or "".  
<sub>línea 508</sub>

`function changesArray(call: Call in default, obj: Expr in default, at: Type in default, kind: BuiltinKind): void`  
push, pop and clear change a fixed array in place: it must be a variable or a field.  
<sub>línea 533</sub>

`function checkArrayMethod(call: Call in default, member: Member in default, at: Type in default, expected: Type? in default, place: Place in default): Type`
<sub>línea 539</sub>

`function checkSort(call: Call in default, obj: Expr in default, at: Type in default): Type`  
list.sort(): numbers and Strings in their natural order. list.sort(compare): any elements, in the order that compare(a, b) says (negative: a goes first; zero: equal; positive: b goes first). Stable, in place.  
<sub>línea 603</sub>

`function checkMapFilter(call: Call in default, obj: Expr in default, isMap: bool, at: Type in default, expected: Type? in default, place: Place in default): Type`
<sub>línea 620</sub>

`function stringForms(name: String): String`  
The String methods the compiler writes itself (the rest are written in Larimar in std/lang.lar).  
<sub>línea 654</sub>

`function checkStringMethod(call: Call in default, member: Member in default, place: Place in default): Type`  
The core methods of String: its length, views of it (substring, bytes) and lists of views (split, lines).  
<sub>línea 664</sub>

`function checkAnyMethod(call: Call in default, member: Member in default): Type`  
remove(name), removeAt(i), clear(), removeIf((value) -> ...) or removeIf((name, value) -> ...).  
<sub>línea 724</sub>

`function comparableInAny(type: Type): bool`  
Values contains() can find in an Any: compared by value (numbers, bool, String) or identity (objects).  
<sub>línea 796</sub>

`function comparable(type: Type): bool`  
Elements contains() can compare with ==.  
<sub>línea 802</sub>

`function markGlobalMutation(obj: Expr in default): void`
<sub>línea 806</sub>

`function recordValueMutation(obj: Expr in default, line: int32): void`
<sub>línea 811</sub>

`function throughRef(target: Expr): bool`
<sub>línea 818</sub>

---

## semantics.expressions.constants

`src/compiler/semantics/expressions/constants.lar` · 153 líneas · 9 funciones
semantics.expressions.constants: the values known when compiling.

### class `ConstVal`

`function cInt(i: int64): ConstVal`
<sub>línea 18</sub>

`function cFloat(f: float64): ConstVal`
<sub>línea 19</sub>

`function cBool(b: bool): ConstVal`
<sub>línea 20</sub>

`function asDouble(v: ConstVal): float64`
<sub>línea 22</sub>

`public function literalValue(n: IntLit in default, negate: bool): ConstVal`  
The value of an integer literal, negated or not.  
<sub>línea 28</sub>

`public function intFits(i: int64, big: bool, huge: bool, type: Type): bool`  
Integer values: does it fit in t?  
<sub>línea 51</sub>

`public function evalConst(e: Expr in default): ConstVal?`  
int64, float64, bool or String (raw text), or null after reporting an error.  
<sub>línea 58</sub>

`function evalBinary(e: Binary in default): ConstVal?`
<sub>línea 99</sub>

`public function evalSize(e: Expr in default): int64`
<sub>línea 140</sub>

---

## semantics.expressions.conversions

`src/compiler/semantics/expressions/conversions.lar` · 228 líneas · 13 funciones
semantics.expressions.conversions: when a value of one type can be used as another: coercion and conversions.

`public function typeOf(e: Node): Type`
<sub>línea 16</sub>

`public function regionOf(e: Node): Region`
<sub>línea 17</sub>

`public function setRegion(e: Node in default, r: Region in default): void`
<sub>línea 18</sub>

`public function placeRegion(p: Place in default): Region`
<sub>línea 22</sub>

`function tempRegion(label: String in default): Region`  
The current statement's temporaries (none at the top level: there it is the whole program).  
<sub>línea 50</sub>

`public function hasRefs(type: Type): bool`
<sub>línea 59</sub>

`public function namedHasRefs(name: String, namedKind: NamedKind): bool`  
Has a struct or an enum (by name) references to memory?  
<sub>línea 65</sub>

`function hasRefsIn(type: Type, visiting: Any): bool`
<sub>línea 70</sub>

`function namedRefsIn(name: String, namedKind: NamedKind, visiting: Any): bool`
<sub>línea 85</sub>

`public function conversionOf(kind: ConversionKind, from: Type in default, to: Type in default): Conversion`
<sub>línea 108</sub>

`public function coerce(e: Expr in default, target: Type in default, place: Place in default, ctx: String in default): Type`  
Checks `e` where a value of type `target` is needed, applying implicit conversions. Returns the target type, or ERROR.  
<sub>línea 117</sub>

`function box(e: Expr in default, type: Type, place: Place in default): void`  
A struct or enum put in an Any is copied into a memory: the one written with `in`, or the table's.  
<sub>línea 181</sub>

`public function conversion(from: Type in default, to: Type in default): Conversion?`
<sub>línea 191</sub>

---

## semantics.expressions.literals

`src/compiler/semantics/expressions/literals.lar` · 367 líneas · 15 funciones
semantics.expressions.literals: lambdas, objects, lists, tables and casts.

`public function checkLambda(l: Lambda in default, expected: Type? in default, place: Place in default): Type`
<sub>línea 20</sub>

`public function calledReference(c: Call in default, ref: Call in default): Type`  
pepito::run(): the parentheses call it; the reference is written without them.  
<sub>línea 73</sub>

`public function refText(call: Call): String`  
How a method reference was written: Pages::show.  
<sub>línea 82</sub>

`function referenceTarget(call: Call in default): bool`  
Module::function, variable::method or self::method; not a field (it would be read on every call).  
<sub>línea 93</sub>

`function checkValues(literal: ObjectLit in default): Type`
<sub>línea 101</sub>

`function valuesRegion(literal: ObjectLit in default): Region`
<sub>línea 106</sub>

`function writtenHere(e: Expr in default): bool`  
A value nobody else has: a list or an object written there, of values or of what is written there too.  
<sub>línea 113</sub>

`function checkSynchronizedInits(literal: ObjectLit in default, typeName: String in default): void`  
What a synchronized object is created with: values, or what is written right there. A list or an object that whoever creates it still has would be used by two threads without the lock, and a function could be called by two at once: that one is `thread safe`.  
<sub>línea 135</sub>

`public function checkObjectLit(literal: ObjectLit in default, expected: Type? in default, place: Place in default): Type`
<sub>línea 148</sub>

`function checkAnyLit(literal: ObjectLit in default, place: Place in default): Type`  
{ 1, "two", name: v, inner: { ... } }: positions and named entries.  
<sub>línea 238</sub>

`function checkFieldInits(literal: ObjectLit in default, fields: FieldInfo[*] in default, typeName: String, place: Place in default, objRegion: Region? in default): void`  
objRegion != null: a class object, whose fields must not reference shorter-lived data.  
<sub>línea 258</sub>

`public function checkArrayLit(a: ArrayLit in default, expected: Type? in default, place: Place in default): Type`
<sub>línea 289</sub>

`public function checkCast(c: Cast in default): Type`
<sub>línea 330</sub>

`public function checkWith(facts: Symbol[*] in default, e: Expr in default, expected: Type? in default, place: Place in default): Type`  
Checks e where the facts hold (the right side of && and ||, a side of ?:).  
<sub>línea 350</sub>

`public function coerceWith(facts: Symbol[*] in default, e: Expr in default, target: Type in default, place: Place in default, ctx: String in default): Type`
<sub>línea 359</sub>

---

## semantics.expressions.operators

`src/compiler/semantics/expressions/operators.lar` · 339 líneas · 16 funciones
semantics.expressions.operators: ? :, is, and the unary and binary operators.

`public function checkTernary(t: Ternary in default, expected: Type? in default, place: Place in default): Type`  
c ? a : b. The side that is not a bare literal (a number or null) gives the type, and the other side takes it. Two classes meet in their nearest common ancestor.  
<sub>línea 24</sub>

`public function checkIs(isExpr: IsExpr in default): Type`  
x is Dog [d]: the binding is declared where the test is known to be true (see facts).  
<sub>línea 62</sub>

`public function related(classInfo: ClassInfo in default, type: Type in default): bool`  
Can a value of class or interface type `t` be a `cls`?  
<sub>línea 93</sub>

`function loose(e: Expr): bool`  
A number or null literal: it takes the type of the other side of ?:.  
<sub>línea 98</sub>

`public function withoutThreadSafe(type: Type in default): Type`  
A type without `thread safe` (also inside an optional), or the type itself.  
<sub>línea 101</sub>

`public function optional(type: Type in default): Type`
<sub>línea 107</sub>

`function unify(a: Type in default, b: Type in default): Type?`
<sub>línea 111</sub>

`function convertTo(e: Expr in default, from: Type in default, to: Type in default): void`
<sub>línea 128</sub>

`public function checkUnary(unary: Unary in default, expected: Type? in default, place: Place in default): Type`
<sub>línea 137</sub>

`function checkAddress(unary: Unary in default): Type`  
&x: a pointer to the variable x, for C to read or write (getaddrinfo(..., &list), accept(fd, &addr, &len)). Only as an argument of an extern function, so it never outlives the call; x is a variable whose type a C pointer can point to.  
<sub>línea 169</sub>

`function operatorOf(type: Type in default, op: String, arity: int32): MethodInfo?`
<sub>línea 198</sub>

`function isIntLiteral(e: Expr): bool`
<sub>línea 203</sub>

`public function checkBinary(binary: Binary in default, expected: Type? in default, place: Place in default): Type`
<sub>línea 211</sub>

`function checkEquality(binary: Binary in default): void`
<sub>línea 280</sub>

`function operands(binary: Binary in default, hint: Type? in default): bool`  
Checks both sides (into lt and rt); integer literals adapt to the other side. Returns false when one is an error.  
<sub>línea 309</sub>

`function overloaded(binary: Binary in default, firstType: Type in default, op: String in default): bool`
<sub>línea 328</sub>

---

## semantics.expressions.switches

`src/compiler/semantics/expressions/switches.lar` · 336 líneas · 10 funciones
semantics.expressions.switches: switch: its patterns and what they cover.

`public function analyzeSwitch(switchExpr: SwitchExpr in default, isExpr: bool, expected: Type? in default, place: Place in default): Type`
<sub>línea 20</sub>

`function namedTypeByName(name: String in default): Type?`
<sub>línea 118</sub>

`function bind(name: String in default, type: Type in default, line: int32): Symbol`  
An immutable name bound by a pattern.  
<sub>línea 127</sub>

`function bindPatternsForInference(c: SwitchCase in default, inner: Type in default): void`  
Declares pattern bindings before inferring the switch type from the first arm.  
<sub>línea 134</sub>

`function bindPart(name: String in default, type: Type in default, line: int32, subject: Expr in default): Symbol`  
A name bound to (part of) the subject: it shares the subject's memory when it references any.  
<sub>línea 160</sub>

`function resolvePattern(p: Pattern in default, st: Type in default, inner: Type in default, subject: Expr in default): PatternInfo?`
<sub>línea 166</sub>

`function anyPattern(p: Pattern in default, subject: Expr in default, patternInfo: PatternInfo in default): PatternInfo?`  
case int64 n, case String s, case Any t (a table), case null.  
<sub>línea 252</sub>

`function classPattern(p: Pattern in default, inner: Type in default, patternInfo: PatternInfo in default, binding: String in default, subject: Expr in default): PatternInfo?`
<sub>línea 268</sub>

`function analyzeArm(c: SwitchCase in default, switchInfo: SwitchInfo in default, isExpr: bool, place: Place in default): void`
<sub>línea 284</sub>

`function alwaysYields(body: Stmt[*]): bool`
<sub>línea 320</sub>

---

## semantics.linker

`src/compiler/semantics/linker.lar` · 1444 líneas · 73 funciones
semantics.linker: modules (Linker.java). Each file is a module; `import a.b` loads a/b.lar.

Every module is parsed, its top-level declarations are renamed with its path
(geo.shapes.Circle becomes geo__shapes__Circle; the main file keeps its names), every
reference is resolved through the module's imports, and everything is joined into one
program. The analyzer and the generator then see a single program with distinct names.

Lines are file index * 1000000 + line; decode() turns them back into "file:line".

### class `Module`

`function newModule(path: String in default, index: int32): Module`
<sub>línea 41</sub>

### class `Linking`
The state of linking: the settings it was given (target, std, libraries, --unsafe-c), every module read and its order, the files of the program, and the errors.

`public function useLinking(state: Linking in default): void`  
Makes `state` the one the compiler works on.  
<sub>línea 87</sub>

`public function inTarget(platform: String): bool`  
Whether what is for `platform` ("": every one) is for the target.  
<sub>línea 95</sub>

`function ownStd(mainPath: String in default): String?`  
The standard library a file belongs to, when it is one of its files (std/crypto.lar open in the editor, of a copy that is not the installed one): its modules are then the ones of that copy, so that `import std.crypto` in its parts is the file being read, not another.  
<sub>línea 106</sub>

`public function link(mainShown: String in default, mainSource: String in default, sourceDir: String in default, std: String in default, mainPath: String in default): void`  
Link: reads the main file and every module it imports (parsing each), in an order where a module comes after the ones it uses, and gives each the names it sees. The rules (semantics.rules) look at the modules next; assemble puts them together.  
<sub>línea 124</sub>

`public function flushRuleErrors(): void`  
The errors said so far, into linkErrors (each once).  
<sub>línea 144</sub>

`public function linkedModules(): Module[*]`  
The modules linked, each after the ones it imports.  
<sub>línea 150</sub>

`public function declarationsOf(module: Module in default): Node[*]`  
The declarations of a module, as written (before assemble gives them their C names).  
<sub>línea 153</sub>

`public function linkedMainFile(): String`  
The main file linked.  
<sub>línea 156</sub>

`public function importsOf(module: Module in default): ImportDecl[*]`  
The imports of a module.  
<sub>línea 159</sub>

`public function ruleError(line: int32, rule: String, msg: String): void`  
A broken rule of the language: its message, with the rule's id (semantics.rules).  
<sub>línea 162</sub>

`public function assemble(): Program`  
Assemble: every module's declarations, with their C names, in one Program; the errors go to linkErrors.  
<sub>línea 167</sub>

`function dictFromSet(into: Any, names: Any in default, prefix: String): void`
<sub>línea 195</sub>

`function error(line: int32, msg: String): void`
<sub>línea 199</sub>

`function loadLang(): void`  
std.lang, cut down to the declarations the program mentions, and the ones those mention (comments after // do not count). A name the main file declares itself is its own.  
<sub>línea 207</sub>

`function taskInterface(c: ClassDecl in default, p: Program in default): String`  
The name of `implements` that is std.os.process.Task, as the class wrote it ("" when it does not implement it): Task imported by name, or through the alias of std.os.process.  
<sub>línea 291</sub>

`function taskScalar(typeRef: TypeRef in default): bool`
<sub>línea 309</sub>

`function fromTable(typeRef: TypeRef in default, x: String): String`  
What a value of a scalar type is when it comes back from a table (`x`: the Any).  
<sub>línea 312</sub>

`function modulePathOf(file: String): String`  
The module path a file is imported by: from the project's folder (tests, and the editor, also from the folder above it, as moduleFile does). "" when it is under neither.  
<sub>línea 323</sub>

`function pathUnder(dir: String, file: String): String`
<sub>línea 338</sub>

### class `LinkedClass`
A class as the linker sees it, before the analysis: its declaration and its module.

`function classChain(c: ClassDecl in default, m: Module in default): LinkedClass[*]`  
The class and the classes it extends, from it up; a parent may be in another module (imported).  
<sub>línea 357</sub>

`function classNamed(name: String in default, m: Module in default): LinkedClass?`  
The class a module names: its own, one it imports by name, or alias.Name.  
<sub>línea 372</sub>

`function writeTasks(mainPath: String): void`  
For each module with classes that implement Task, two functions of its own: one gives the class and fields of a task as a table, the other makes it again from them. std.os.process.tasks is then written to ask each of those modules.  
<sub>línea 400</sub>

`function addWords(text: String in default): void`  
Adds the words of a text (not those of its comments) to `words`.  
<sub>línea 581</sub>

`function cWords(code: String in default, names: Any in default): void`  
Every name in a piece of C, into names.  
<sub>línea 597</sub>

`function cCodeUses(code: String in default, cSymbols: Any in default): bool`
<sub>línea 610</sub>

`function parse(module: Module in default, source: String in default): void`
<sub>línea 629</sub>

`public function readSource(path: String): String?`  
The text of a file, or null if it cannot be read.  
<sub>línea 663</sub>

`public function isStd(path: String): bool`
<sub>línea 673</sub>

`public function trusted(module: Module in default, mainPath: String): bool`  
Whether a module may have C: the standard library's (the installed one, or the copy being edited), and the language's.  
<sub>línea 681</sub>

`function moduleFile(path: String): String`  
Where a module's file is: std/, else a library of [dependencies] (its name, or <name>.<part>), else the project's folder (the main file's).  
<sub>línea 691</sub>

`public function libraryOf(path: String): int32`  
The library a module belongs to (its name, or <name>.<part>): its index, or -1.  
<sub>línea 714</sub>

`function shownName(path: String): String`  
How a module's file is shown in messages.  
<sub>línea 722</sub>

`function visit(module: Module in default): void`  
Loads the imports first, so each module comes after the ones it uses (and globals start in that order).  
<sub>línea 729</sub>

`function tables(module: Module in default): void`
<sub>línea 760</sub>

`function bring(module: Module, into: Any, n: String in into, from: Module, mangled: String in into, line: int32): void`
<sub>línea 823</sub>

`function push(): void`
<sub>línea 841</sub>

`function pop(): void`
<sub>línea 846</sub>

`function declare(n: String in default): void`
<sub>línea 848</sub>

`function local(n: String): bool`
<sub>línea 852</sub>

`public function stdFileOpened(module: Module in default): bool`  
A file of std opened alone (the editor, larimar check std/x.lar): it is std, whatever its module path.  
<sub>línea 863</sub>

`public function isLanguage(module: Module in default): bool`  
std.lang (or std/lang.lar opened alone): what has no body there the compiler writes.  
<sub>línea 870</sub>

`function nativeKnown(module: Module in default, name: String): bool`
<sub>línea 875</sub>

`function larNames(module: Module in default, code: String, line: int32): String`  
lar"name" in ccode: a function, type or global of Larimar, by its Larimar name (module.name for another module); it becomes lar"its linked name", and the generator writes its C name there.  
<sub>línea 884</sub>

`function larName(module: Module in default, name: String): String`  
The linked name of a Larimar name seen from module m ("a.b.name": the module a.b), or "".  
<sub>línea 909</sub>

`function rewriteDecl(module: Module in default, d: Node in default): void`
<sub>línea 923</sub>

`function hasHeaders(module: Module in default): bool`  
Whether a module brings its own C headers (cinclude or ccode), itself or in its parts (the modules of its folder, net/posix.lar for net.lar): then its natives are declared by them, not by us.  
<sub>línea 1021</sub>

`function function_(f: FunctionDecl in default, name: String in default): void`
<sub>línea 1033</sub>

`function fields(fs: FieldDecl[*] in default): void`
<sub>línea 1044</sub>

`function params(ps: Param[*] in default): void`
<sub>línea 1051</sub>

`function typeRef(t: TypeRef? in default): void`
<sub>línea 1055</sub>

`function typeName(name: String in default, line: int32): String`  
Shape, geo.Shape, Shape.Circle (enum variant), geo.Shape.Circle.  
<sub>línea 1068</sub>

`function exported(from: Module, n: String, values: bool, line: int32): String`  
A public name of another module: values first, then types ("" after an error).  
<sub>línea 1085</sub>

`function hidden(n: String, line: int32): void`  
Modules do not see the main file's declarations (nobody imports the main file).  
<sub>línea 1099</sub>

`function block(body: Stmt[*] in default, newScope: bool): void`
<sub>línea 1107</sub>

`function stmt(s: Stmt in default): void`
<sub>línea 1113</sub>

`function exprOpt(e: Expr? in default): Expr?`
<sub>línea 1164</sub>

`function expr(e: Expr in default): Expr`  
The expression renamed; module.name comes back as the name itself.  
<sub>línea 1167</sub>

`function asksPlatform(e: Expr in default): bool`  
Platform.current(), as the linker leaves it.  
<sub>línea 1254</sub>

`function chosen(switchExpr: SwitchExpr in default): bool`  
A switch on the platform that --target reduced to its arm.  
<sub>línea 1260</sub>

`function choosePlatform(switchExpr: SwitchExpr in default): void`  
With --target, a switch on Platform.current() keeps only the arm of that platform, as its default.  
<sub>línea 1265</sub>

`function switchExpr(sw: SwitchExpr in default): void`
<sub>línea 1284</sub>

`function isAlias(n: String): bool`
<sub>línea 1298</sub>

`function identName(id: Ident in default): void`
<sub>línea 1302</sub>

`function pattern(p: Pattern in default): void`  
A variant keeps its name; a type or a constant is renamed (variant lookup ignores a module prefix).  
<sub>línea 1322</sub>

`public function decode(msg: String): String`  
"[Line 2000005]" -> "[src/geo.lar:5]", "line 7" -> "main.lar:7", and geo__Shape -> geo.Shape.  
<sub>línea 1344</sub>

`function replaceLines(msg: String, key: String, bracket: bool): String`
<sub>línea 1350</sub>

`function moduleOfFile(index: int32): Module?`
<sub>línea 1390</sub>

`public function namesOfFile(index: int32): Any`  
What a file can name: name -> its name after linking (its own, imported and the language's).  
<sub>línea 1399</sub>

`public function isLangHelper(name: String): bool`  
A name std.lang keeps to itself (its helpers): every file sees it, but the editor does not offer it.  
<sub>línea 1409</sub>

`public function aliasesOfFile(index: int32): Any`  
The modules a file imports with a name: alias -> module path ("geo.shapes").  
<sub>línea 1416</sub>

`public function publicsOfModule(path: String): Any`  
The public names of a module, each with its name after linking.  
<sub>línea 1428</sub>

`public function fileOfModule(path: String): String`  
The file of a module, from its path ("geo.shapes"), or "".  
<sub>línea 1438</sub>

---

## semantics.rules

`src/compiler/semantics/rules.lar` · 204 líneas · 26 funciones
semantics.rules: the rules of the language that are checked on the linked modules, one object each,
listed by languageRules(). Each has an id, which its errors say (error[std-own-import]), and the part of
the spec that says it. The pass CheckRules (pipeline) asks each rule about each module, after Link and
before the modules are put together; tests/language/rules_test.lar has a case that breaks each one.

The rules that need types (lifetimes, threads, what crosses to a process) are the analyzer's; these are
the ones about modules and what they declare: where C may be, which modules a module may import, and
what must have a body.

### interface `Rule`
A rule of the language.

- `function id(): String`  
  Its id, as its errors say it: error[<id>].  
  <sub>línea 20</sub>

- `function spec(): String`  
  Where the spec says it (docs/spec.md).  
  <sub>línea 22</sub>

- `function check(module: Module in default): void`  
  Says each place where the module breaks it (ruleError).  
  <sub>línea 24</sub>

`public function languageRules(): Rule[*]`  
Every rule CheckRules asks, in this order.  
<sub>línea 28</sub>

`public function ruleIds(): String[*]`  
The ids of every rule (for the test that each one has a case that breaks it).  
<sub>línea 33</sub>

`function stdOwnPart(part: String): bool`  
A part of a module's path that makes a module of std std's own: the C of one system, what its parts share.  
<sub>línea 42</sub>

`public function stdOwn(path: String): bool`  
A module of std that only std imports (std.net.posix, std.os.process.internal).  
<sub>línea 47</sub>

`public function stdPublicOf(path: String): String`  
std.net.posix -> std.net: where what it does is given.  
<sub>línea 56</sub>

### class `StdOwnImport implements Rule`
A part of std for std itself is imported only from std.

- `override function id(): String`
  <sub>línea 67</sub>

- `override function spec(): String`
  <sub>línea 68</sub>

- `override function check(module: Module in default): void`
  <sub>línea 69</sub>

`public function internalOwner(path: String): String?`  
What is inside an `internal` folder (a.b.internal.c) is imported only by the modules of its folder (a.b...).  
<sub>línea 80</sub>

### class `InternalImport implements Rule`

- `override function id(): String`
  <sub>línea 93</sub>

- `override function spec(): String`
  <sub>línea 94</sub>

- `override function check(module: Module in default): void`
  <sub>línea 95</sub>

`function importsUnsafeTask(module: Module in default): bool`  
Whether the module takes UnsafeTask from std.os.process (by name, or through an alias).  
<sub>línea 113</sub>

### class `NoCOutsideStd implements Rule`
C is the standard library's, and an UnsafeTask's: a program, and a library written in Larimar, use what std gives; a C library of their own is a native interface (in a module, or in the class of a task), opened: only the methods of an UnsafeTask call it, in the task's own process (checkFunctionCall).

- `override function id(): String`
  <sub>línea 131</sub>

- `override function spec(): String`
  <sub>línea 132</sub>

- `override function check(module: Module in default): void`
  <sub>línea 133</sub>

`function cKind(d: Node): String`  
What of C a declaration is ("" when it is not C).  
<sub>línea 160</sub>

### class `BodyNeeded implements Rule`
A function has its body: only what the compiler writes, in std.lang (and std.memory), has none.

- `override function id(): String`
  <sub>línea 180</sub>

- `override function spec(): String`
  <sub>línea 181</sub>

- `override function check(module: Module in default): void`
  <sub>línea 182</sub>

### class `LanguageTypeOnlyInLang implements Rule`
`type X { }` (a type of the language, String and Any) is only in std.lang.

- `override function id(): String`
  <sub>línea 193</sub>

- `override function spec(): String`
  <sub>línea 194</sub>

- `override function check(module: Module in default): void`
  <sub>línea 195</sub>

---

## semantics.types

`src/compiler/semantics/types.lar` · 1044 líneas · 90 funciones
semantics.types: what the analyzer knows. Types, regions (where data lives), scopes, symbols,
the information about declarations, and the per-node facts the generator reads.
It follows Types.java and Analysis.java of the Java version.

### enum `TypeKind`

### enum `NamedKind`

### enum `ArrayKind`

### class `Type`

### class `Declarations`
What a program declares, gathered by the analysis: its types, functions, globals and lambdas, and what its C needs (includes, ccode, files).

`public function useDeclarations(state: Declarations in default): void`  
Makes `state` the one the compiler works on.  
<sub>línea 71</sub>

`function intern(type: Type in default): Type`
<sub>línea 75</sub>

`function primitive(name: String in default): Type`
<sub>línea 83</sub>

`public function primByName(name: String): Type?`  
A built-in type by name (uint8 is byte), or null.  
<sub>línea 105</sub>

`public function isPrimName(name: String): bool`
<sub>línea 116</sub>

`public function named(name: String in default, namedKind: NamedKind): Type`
<sub>línea 118</sub>

`public function functionTypeOf(params: Type[*] in default, ret: Type in default, safe: bool): Type`
<sub>línea 122</sub>

`public function hasThreadSafe(type: Type in default): bool`  
Is there a `thread safe` function type in t (itself, or the element of an optional or an array)?  
<sub>línea 139</sub>

`public function cTypeOf(type: Type in default): Type`  
The type C sees: t without `thread safe` (the same closure type), also inside optionals and arrays.  
<sub>línea 146</sub>

`public function arrayTypeOf(elem: Type in default, arrayKind: ArrayKind, size: int64): Type`
<sub>línea 153</sub>

`public function optionalOf(inner: Type in default): Type`
<sub>línea 164</sub>

`public function pointerTo(inner: Type in default): Type`  
T*: a C pointer (only to numbers, C structs, extern types and other pointers).  
<sub>línea 171</sub>

`public function isPtr(type: Type): bool`
<sub>línea 175</sub>

`public function bits(type: Type): int32`
<sub>línea 177</sub>

`public function isFloat(type: Type): bool`
<sub>línea 188</sub>

`public function isInteger(type: Type): bool`
<sub>línea 189</sub>

`public function isNumeric(type: Type): bool`
<sub>línea 190</sub>

`public function isSigned(type: Type): bool`
<sub>línea 191</sub>

`public function isError(type: Type): bool`
<sub>línea 192</sub>

`public function isClass(type: Type): bool`
<sub>línea 193</sub>

`public function isStruct(type: Type): bool`
<sub>línea 194</sub>

`public function isInterface(type: Type): bool`
<sub>línea 195</sub>

`public function isEnumT(type: Type): bool`
<sub>línea 196</sub>

`public function isExternT(type: Type): bool`
<sub>línea 197</sub>

`public function isByteArray(type: Type): bool`
<sub>línea 198</sub>

`public function isOpt(type: Type): bool`
<sub>línea 199</sub>

`public function isArray(type: Type, arrayKind: ArrayKind): bool`
<sub>línea 200</sub>

`public function optIsPointer(o: Type): bool`  
An optional that is a pointer in C (null is NULL): classes, extern types, T[*].  
<sub>línea 203</sub>

`public function minOf(type: Type): int64`  
The smallest and largest value of an integer type; for uint64 the largest is kept apart.  
<sub>línea 209</sub>

`public function maxOf(type: Type): int64`
<sub>línea 219</sub>

`public function maxText(type: Type): String`  
"the largest value" as text, for messages.  
<sub>línea 237</sub>

### enum `RegionKind`

### class `Region`

`public function rStaticMemory(symbol: Symbol in default): Region`  
The region of a global memory: static like R_STATIC, but it keeps the memory's name for messages.  
<sub>línea 258</sub>

`public function rMemory(symbol: Symbol in default): Region`  
The region of a local memory with a name.  
<sub>línea 260</sub>

`public function rCaller(p: Symbol in default): Region`
<sub>línea 263</sub>

`public function rResult(r: Symbol in default): Region`  
The memory a caller gives for the result of a function (or method, or lambda).  
<sub>línea 265</sub>

`public function rLocal(s: Scope in default, label: String in default): Region`
<sub>línea 268</sub>

`public function variableRegion(v: Symbol in default): Region`
<sub>línea 269</sub>

`public function symbolic(region: Region): bool`
<sub>línea 271</sub>

`public function resolveRegion(region: Region in default): Region`  
Replaces Var parts with the regions computed for those variables (Symbol.resolved).  
<sub>línea 282</sub>

`public function outlives(a: Region, b: Region): bool`  
Does data in `a` live at least as long as data in `b`? (both concrete)  
<sub>línea 296</sub>

`public function meet(a: Region in default, b: Region in default): Region`  
The shorter-lived of two regions.  
<sub>línea 310</sub>

`public function sameRegion(a: Region, b: Region): bool`
<sub>línea 332</sub>

`public function describe(region: Region): String`
<sub>línea 344</sub>

### class `Scope`

`public function newScope(parent: Scope? in default, frame: Frame in default): Scope`
<sub>línea 376</sub>

`public function isAncestorOrSelf(a: Scope, s: Scope): bool`
<sub>línea 381</sub>

### enum `FrameKind`

### class `Owner`
What a body can reach, for the thread checks: the globals it uses and what it calls.

`public function newOwner(): Owner`
<sub>línea 400</sub>

### class `Frame`

### enum `SymbolKind`

### enum `MemoryKind`

### enum `ConstantKind`

### class `Symbol`

`public function isMemory(symbol: Symbol): bool`
<sub>línea 456</sub>

`public function isCReserved(name: String): bool`
<sub>línea 470</sub>

`public function ascii(name: String): String`  
C99 identifiers are ASCII: año -> a_u00f1o.  
<sub>línea 481</sub>

`function asciiChar(c: int32): String`
<sub>línea 492</sub>

`function hex4Digits(c: int32): String`  
Lowercase hexadecimal, at least 4 digits (like %04x).  
<sub>línea 497</sub>

`function startsLar(n: String): bool`  
Lar and a capital (LarMemory): the names of the runtime's types.  
<sub>línea 511</sub>

`public function escapeName(name: String): String`
<sub>línea 513</sub>

### class `FieldInfo`

### class `FunctionInfo`

### class `ExternTypeInfo`
A type that comes from C: opaque (void*), a C type (c "T") or a pointer to a C function (sig). With `released by`, a resource: it lives in a memory, and the releaser runs when that memory is freed.

### class `MethodInfo`

`public function isMemParam(flags: bool[*], i: int32): bool`
<sub>línea 588</sub>

`public function cSuffix(method: MethodInfo): String`
<sub>línea 590</sub>

### class `StructInfo`

### class `ClassInfo`

### class `InterfaceInfo`

### class `VariantInfo`

### class `EnumInfo`

### class `LambdaInfo`

`public function bytesOf(t: Type): int64`  
How many bytes a value of the type takes in C, roughly (enough to tell a small value from a big one).  
<sub>línea 665</sub>

`public function hasBigCaptures(lambdaInfo: LambdaInfo): bool`  
A lambda whose captures are too big to carry in every closure of its type.  
<sub>línea 688</sub>

`public function hasCapture(lambdaInfo: LambdaInfo, symbol: Symbol): bool`
<sub>línea 694</sub>

### enum `PlaceKind`
Where an allocating expression puts its data. Temp: nothing said, a temporary of the statement; Global: `in default`; Block: a variable's value, the memory of its block; Result: a returned value, the memory the caller gives; Memory, Stack: `in m`, `in byte[N]`; OfObject, OfList, OfAny: stored inside an object, a list or a table.

### class `Place`

`public function placeOf(kind: PlaceKind, expr: Expr? in default): Place`
<sub>línea 721</sub>

### enum `ConversionKind`

### class `Conversion`

### enum `CallK`

### enum `BuiltinKind`

### class `CallInfo`

### enum `CallbackKind`
A callback given to C (spec §D.10): a function and its "this", the void* C gives back. Closure: a value of function type, whose this is a pointer to it; Method: object::method, whose this is the object; Plain: a function without state (a lambda that captures nothing, or a reference to a function), with no this.

### class `CallbackInfo`

`public function isVoidPointer(type: Type): bool`  
void*: what C gives back to a callback, its "this".  
<sub>línea 772</sub>

`public function voidPointers(type: Type): int32[*]`  
The parameters of a callback type that are void*.  
<sub>línea 775</sub>

### enum `MemberKind`

### class `MemberInfo`

### enum `PatK`

### class `PatternInfo`

### class `SwitchInfo`

### class `ForInfo`

### class `CatchInfo`

`public function structOf(name: String): StructInfo?`
<sub>línea 839</sub>

`public function classOf(name: String): ClassInfo?`
<sub>línea 844</sub>

`public function interfaceOf(name: String): InterfaceInfo?`
<sub>línea 849</sub>

`public function enumOf(name: String): EnumInfo?`
<sub>línea 854</sub>

`public function functionOf(name: String): FunctionInfo?`
<sub>línea 859</sub>

`public function isExternTypeName(name: String): bool`
<sub>línea 864</sub>

`public function isResource(type: Type): bool`  
An extern type declared `released by`: a resource that lives in a memory.  
<sub>línea 867</sub>

`public function platformCondition(p: String): String`  
The C condition of a platform, for #if.  
<sub>línea 874</sub>

`public function platformWithin(inner: String, outer: String): bool`  
Code that runs only on `inner` also runs where `outer` holds? (macos and linux are unix)  
<sub>línea 884</sub>

`public function nativeOwner(owner: String): Type`  
The type whose methods a native type declares: one the compiler knows (String), or one of C.  
<sub>línea 890</sub>

`public function externInfoOf(name: String): ExternTypeInfo?`
<sub>línea 897</sub>

`public function externStructC(type: Type): String`  
The C struct a `native struct X { ... }` describes ("" for other types).  
<sub>línea 903</sub>

`public function isExternStruct(type: Type): bool`
<sub>línea 909</sub>

`public function isCValue(type: Type): bool`  
What can cross to C and back: numbers, bool, String (const char*), extern types, C structs and C pointers.  
<sub>línea 912</sub>

`public function pointable(type: Type): bool`  
What a C pointer can point to: numbers, bool, C structs, extern types that are not resources, pointers.  
<sub>línea 918</sub>

`public function structMethod(structInfo: StructInfo, n: String, op: bool, arity: int32): MethodInfo?`
<sub>línea 923</sub>

`public function structField(structInfo: StructInfo, n: String): FieldInfo?`
<sub>línea 930</sub>

`public function interfaceMethod(interfaceInfo: InterfaceInfo, n: String): MethodInfo?`
<sub>línea 937</sub>

`public function variantOf(enumInfo: EnumInfo, name: String): VariantInfo?`  
A variant by name; a module prefix never names a variant.  
<sub>línea 945</sub>

`public function enumSimple(enumInfo: EnumInfo): bool`
<sub>línea 955</sub>

`public function parentOf(classInfo: ClassInfo): ClassInfo?`
<sub>línea 962</sub>

`public function syncField(classInfo: ClassInfo in default): String`  
Where the lock of a synchronized class is in its C struct: the first synchronized class of the chain has it.  
<sub>línea 967</sub>

`public function chain(name: String in default): ClassInfo[*]`  
Root first; safe on broken hierarchies.  
<sub>línea 973</sub>

`public function findField(cls: String in default, field: String): FieldInfo?`
<sub>línea 993</sub>

`public function findMethod(cls: String in default, name: String, op: bool, arity: int32): MethodInfo?`  
The most derived definition (operators match by arity).  
<sub>línea 1003</sub>

`public function allFields(cls: String in default): FieldInfo[*]`
<sub>línea 1015</sub>

`public function isSubclass(sub: String in default, sup: String): bool`
<sub>línea 1023</sub>

`public function implementor(cls: String in default, iface: String): String`  
The ancestor (or the class itself) that declares `implements iface`, or "".  
<sub>línea 1031</sub>

`public function classDepth(name: String in default): int32`
<sub>línea 1043</sub>

---

## codegen.cprogram

`src/compiler/codegen/cprogram.lar` · 57 líneas · 4 funciones
codegen.cprogram: the C of a program as parts, not one text. EmitC makes a CProgram: text where the C is
written in pieces (headings, types, prototypes), and a CFunction for each function and lambda, whole.
NameC names the variables of each part; Prune keeps the parts main reaches, and needs to cut only the
text: a function is one part already, with what it uses.

The bodies are text still; making them structure (CBlock, CStatement) is what comes next.

### class `CFunction`
A function of the C: its name, its whole text (header and body), and the names it uses (Prune fills them).

### class `CPart`
A part of the C, in order: text, or one function.

### class `CProgram`
The C of the program, in parts.

- `function add(text: String): void`  
  Text at the end (a heading, a type, a prototype...): it joins the text part before it.  
  <sub>línea 26</sub>

- `function addFunction(name: String, text: String): void`  
  A whole function.  
  <sub>línea 37</sub>

- `function text(): String`  
  The C as one text.  
  <sub>línea 42</sub>

`public function cSection(program: CProgram, title: String): void`  
A heading of a section of the C: Prune knows the sections by it.  
<sub>línea 52</sub>

---

## codegen.debugmap

`src/compiler/codegen/debugmap.lar` · 223 líneas · 10 funciones
codegen.debugmap: with larimar build --debug, what the debugger (larimar dap) needs to show the program as
Larimar: for each C function, its Larimar name and the variables it has (their Larimar names, their
names in C and their types), the globals, and the shape of every type (fields with their C paths,
enum variants, classes). Written next to the C as <name>.debug.json.

A type is described as JSON: {"k": "int"|"float"|"bool"|"String"|"any"|"list"|"slice"|"array"|"opt"|
"struct"|"class"|"interface"|"enum"|"raw", ...}; structs, classes, interfaces and enums by name, in
"types", so a type that contains itself is no problem.

`public function debugMap(): String`  
The debug map of the program just generated, as JSON.  
<sub>línea 24</sub>

`function methodJson(method: MethodInfo in default, isStruct: bool): String`
<sub>línea 60</sub>

`function fnJson(cName: String, display: String, line: int32, params: Symbol[*], selfVar: String?, body: Stmt[*] in default,`
<sub>línea 70</sub>

`function varJson(name: String, c: String, type: Type, line: int32): String`  
line: where it is declared (0 for parameters: from the start), so the debugger hides it before.  
<sub>línea 85</sub>

`function localsOf(body: Stmt[*] in default): Symbol[*]`  
The variables a body declares (not those of lambdas inside it: they are their own functions).  
<sub>línea 90</sub>

`function switchBindings(switchExpr: SwitchExpr in out, out: Symbol[*]): void`
<sub>línea 129</sub>

`function typeJson(type: Type): String`
<sub>línea 142</sub>

`function raw(type: Type): String`
<sub>línea 171</sub>

`function describe(name: String, namedKind: NamedKind): void`  
Adds a named type to "types" (once).  
<sub>línea 174</sub>

`function fieldJson(field: FieldInfo, path: String): String`
<sub>línea 220</sub>

---

## codegen.expressions

`src/compiler/codegen/expressions.lar` · 687 líneas · 52 funciones
codegen.expressions: C99 code generation (Gen.java), part 2: expressions.
An expression becomes a C expression; what needs statements first writes them with line().

`public function typeCName(n: String): String`
<sub>línea 31</sub>

`public function mangle(type: Type): String`
<sub>línea 36</sub>

`public function cType(type: Type): String`
<sub>línea 65</sub>

`public function structName(type: Type): String`
<sub>línea 103</sub>

`public function paren(s: String): String`
<sub>línea 112</sub>

`public function hoist(cTypeText: String, v: String): String`
<sub>línea 114</sub>

`public function hoistAs(cTypeText: String, v: String, role: String): String`  
A value kept in a temporary that says what it is.  
<sub>línea 117</sub>

`function hoistAddr(cTypeText: String, v: String): String`
<sub>línea 123</sub>

`public function hoistIfNeeded(cTypeText: String, v: String, e: Expr?): String`
<sub>línea 125</sub>

`public function inOrder(parts: Expr[*] in default): Expr[*]`  
Computes, in order, the parts before the last one with effects; returns them, for forget().  
<sub>línea 137</sub>

`public function forget(held: Expr[*]): void`  
The C of these parts is written: they are computed again where they appear next.  
<sub>línea 154</sub>

`function hasEffects(e: Expr): bool`  
Whether evaluating it can do something another part could see: a call, an index (a panic)...  
<sub>línea 159</sub>

`function anyEffects(es: Expr[*]): bool`
<sub>línea 171</sub>

`function unchangeable(e: Expr): bool`  
Whether nothing evaluated after it can change its value: literals, locals, parameters, constants.  
<sub>línea 179</sub>

`function callParts(c: Call in default): Expr[*]`  
The parts of a call, in the order they are written: the object (not a struct, which is passed by address), then the arguments.  
<sub>línea 192</sub>

`function orderedCall(c: Call in default): String`
<sub>línea 205</sub>

`function orderedIndex(x: Index in default): String`
<sub>línea 212</sub>

`function orderedBinary(b: Binary in default, type: Type): String`
<sub>línea 219</sub>

`public function writtenValues(literal: ObjectLit in default): Expr[*]`  
The values of a literal, in the order they are written.  
<sub>línea 228</sub>

`public function isPure(e: Expr): bool`
<sub>línea 234</sub>

`public function lazy(e: Expr in default): String`  
Generates `e` (its value) into a separate buffer: its statements go to lazyPre.  
<sub>línea 246</sub>

`public function strip(s: String): String`  
Removes the outer parentheses of a C expression when they enclose all of it.  
<sub>línea 257</sub>

`public function zero(type: Type): String`
<sub>línea 283</sub>

`public function discard(e: String): void`  
A call whose result is not used.  
<sub>línea 294</sub>

`function isIdentifier(s: String): bool`
<sub>línea 300</sub>

`public function value(e: Expr in default): String`  
An expression with its conversion applied: where a value is stored or passed.  
<sub>línea 312</sub>

`function convert(v: String, conversion: Conversion in default, e: Expr? in default): String`
<sub>línea 319</sub>

`function innerConversion(from: Type in default, to: Type in default, outer: Conversion in default): Conversion?`  
The inner conversion of WRAP_OPTIONAL (upcast or interface), if any.  
<sub>línea 364</sub>

`public function boxType(type: Type in default): String`  
The descriptor of a struct or enum stored in an Any (its name and how to clone it).  
<sub>línea 376</sub>

`public function boxDescriptors(): String`
<sub>línea 384</sub>

`public function anyKind(type: Type): String`  
LAR_ANY_I32 and so on: the kind an Any uses for a value of type t.  
<sub>línea 399</sub>

`public function anyPayload(type: Type, v: String): String`  
The value inside an Any already known to hold kind t.  
<sub>línea 418</sub>

`function toAny(v: String, from: Type in default, e: Expr in default): String`
<sub>línea 428</sub>

`public function expr(e: Expr in default): String`
<sub>línea 453</sub>

`function unwrap(u: Unwrap in default): String`
<sub>línea 482</sub>

`function placed(inner: Expr in default): String`  
`x in memory`: the value; a lambda that becomes an interface object is created there.  
<sub>línea 490</sub>

`public function intLiteral(v: int64, big: bool, t: Type?): String`  
An integer literal of type t (value v, as uint64 when big).  
<sub>línea 496</sub>

`function identExpr(id: Ident in default): String`
<sub>línea 513</sub>

`function constValue(symbol: Symbol): String`
<sub>línea 526</sub>

`function selfExpr(se: Expr in default): String`
<sub>línea 537</sub>

`function member(m: Member in default): String`
<sub>línea 544</sub>

`function fieldAccess(obj: Expr in default, f: MemberInfo): String`
<sub>línea 585</sub>

`public function fieldC(field: FieldInfo): String`  
A field's name in C: the exact one in a C struct, otherwise escaped.  
<sub>línea 596</sub>

`public function classFieldPath(cls: String, field: FieldInfo): String`
<sub>línea 602</sub>

`function index(indexExpr: Index in default): String`
<sub>línea 613</sub>

`function isLvalueExpr(e: Expr): bool`
<sub>línea 631</sub>

`public function lvalue(target: Expr in default): String`  
The C lvalue of an assignment target (no narrowing).  
<sub>línea 645</sub>

`public function addrOf(e: Expr in default): String`  
A pointer to the value of `e` (a temporary if `e` is not a variable or field).  
<sub>línea 650</sub>

`public function memoryRef(mem: Symbol): String`
<sub>línea 655</sub>

`public function placeMem(e: Expr in default): String`  
C expression of type LarMemory* for an allocation.  
<sub>línea 660</sub>

`public function callMem(c: Expr in default): String`  
The memory a call gives for its result: none (NULL) when the callee only returns data that already exists.  
<sub>línea 663</sub>

`public function placeMemOf(p: Place? in default): String`
<sub>línea 665</sub>

---

## codegen.expressions.callbacks

`src/compiler/codegen/expressions/callbacks.lar` · 123 líneas · 6 funciones
codegen.expressions.callbacks: callbacks given to C (spec §D.10). C calls a C function, the trampoline,
with the void* it was given; the trampoline turns it back into what it is (the object of a method, or
the closure of a function), converts the arguments (a char* to a String, a char** and its count to a
String[]) and calls it. One trampoline per pair of a C signature and a method, a closure type or a
function without state:

static int32_t callback_3_Users_onRow(void* a0, int32_t a1, char** a2, char** a3) {
...
int32_t result = Users_onRow__dispatch((Users*)a0, a0, a1, values, columns);
...
}

`public function callbackArg(a: Expr in default, callback: CallbackInfo in default): String`  
The C of an argument given where C takes a function: its trampoline.  
<sub>línea 25</sub>

`public function thisArg(a: Expr in default): String`  
The C of an argument given where C takes a void*: a function goes as a pointer to it, the rest as it is.  
<sub>línea 43</sub>

`function callbackCType(type: Type): String`  
What C gives a callback, as C: a String is a char*, a String[] a char**.  
<sub>línea 50</sub>

`function isText(type: Type): bool`  
String or String?: a char* in C.  
<sub>línea 57</sub>

`function trampolineHead(name: String, type: Type): String`
<sub>línea 59</sub>

`function trampoline(head: String, callback: CallbackInfo in default): String`
<sub>línea 65</sub>

---

## codegen.expressions.calls

`src/compiler/codegen/expressions/calls.lar` · 452 líneas · 17 funciones
codegen.expressions.calls: calls.

`public function receiver(call: Call): Expr`  
The object a method is called on: a in a.f(...).  
<sub>línea 21</sub>

`function calleeName(call: Call): String`  
The name of the method called: f in a.f(...).  
<sub>línea 26</sub>

`public function call(c: Call in default): String`
<sub>línea 30</sub>

`function first(x: String, xs: String[*]): String[*]`  
x, then the items of xs.  
<sub>línea 132</sub>

`function isBuilderAdd(call: Call, callInfo: CallInfo): bool`
<sub>línea 138</sub>

`public function args(asg: Expr[*] in default, memParams: bool[*]): String[*]`
<sub>línea 145</sub>

`function writtenParams(functionInfo: FunctionInfo): Type[*]`  
The parameters of a C function that a call writes (not the memory of the call, when C takes it first).  
<sub>línea 155</sub>

`function externArgsAs(asg: Expr[*] in default, varargs: bool, params: Type[*]?): String[*]`  
The arguments as C takes them, for C parameters of these types (a T[] is two: its elements and their count).  
<sub>línea 164</sub>

`function itemsOf(at: Type, obj: Expr in default): String[*]`  
The elements of an array as C: items and length.  
<sub>línea 210</sub>

`function builtin(call: Call in default, b: CallInfo in default): String`
<sub>línea 220</sub>

`function printCall(call: Call in default, newline: bool): String`
<sub>línea 273</sub>

`function stringMethod(call: Call in default): String`
<sub>línea 287</sub>

`function splitText(call: Call in default, s: String, sep: String, isLines: bool): String`  
split, lines: views of the text in a new list.  
<sub>línea 302</sub>

`public function lines(text: String in default): void`  
Several lines of C, each written like line() does (a final newline adds no empty line).  
<sub>línea 333</sub>

`function anyRemoveIf(call: Call in default): String`  
Keeps the entries for which the lambda says false; returns how many were removed.  
<sub>línea 341</sub>

`function sortList(call: Call in default, at: Type in default): String`  
list.sort(...): a merge sort, bottom up, in place (stable: of two equal elements the first stays first), with a buffer for one copy of the elements while it runs.  
<sub>línea 385</sub>

`function mapFilter(call: Call in default, b: CallInfo): String`
<sub>línea 424</sub>

---

## codegen.expressions.clone

`src/compiler/codegen/expressions/clone.lar` · 206 líneas · 10 funciones
codegen.expressions.clone: clone: copying a value into another memory.

`public function cloneTypeList(): Type[*]`
<sub>línea 16</sub>

`public function needsDeepClone(t: Type): bool`
<sub>línea 18</sub>

`public function requireClone(t: Type in default): void`
<sub>línea 42</sub>

`public function cloneHeader(type: Type): String`
<sub>línea 64</sub>

`public function cloneOf(type: Type in default, v: String): String`
<sub>línea 68</sub>

`function requireClassClones(): void`  
A class object is copied by its own class (a subclass, maybe): every class's fields may need copying.  
<sub>línea 75</sub>

`public function cloneCall(call: Call in default, b: CallInfo in default): String`
<sub>línea 83</sub>

`public function compactCall(call: Call in default, b: CallInfo in default): String`  
Memory.compact(m): m starts again with no blocks; what its variables reach in the old blocks is copied back (each thing once, cycles included), the variables are pointed at the copies, and the old blocks are freed. What lives in other memories is left where it is.  
<sub>línea 103</sub>

`public function cloneFunctions(): String`
<sub>línea 125</sub>

`function cloneBody(out: StringBuilder, t: Type in default): void`
<sub>línea 139</sub>

---

## codegen.expressions.lambdas

`src/compiler/codegen/expressions/lambdas.lar` · 209 líneas · 10 funciones
codegen.expressions.lambdas: lambdas and literal objects.

`public function lambdaValue(l: Lambda in default): String`
<sub>línea 17</sub>

`function captureValue(symbol: Symbol): String`
<sub>línea 33</sub>

`function genLambda(lambdaInfo: LambdaInfo in default): void`
<sub>línea 39</sub>

`public function singleMethodObject(lambda: Lambda in default, conversion: Conversion in default): String`  
A lambda used as a single-method interface: a small object holding the closure.  
<sub>línea 61</sub>

`function givenValue(literal: ObjectLit, name: String): Expr?`
<sub>línea 75</sub>

`public function objectLit(literal: ObjectLit in default, type: Type in default): String`
<sub>línea 83</sub>

`function fieldInits(fields: FieldInfo[*] in default, literal: ObjectLit in default, mem: String in default): String`
<sub>línea 134</sub>

`function classInit(level: ClassInfo in default, concrete: String, literal: ObjectLit in default, mem: String in default): String`
<sub>línea 154</sub>

`function interfaceLit(literal: ObjectLit in default, interfaceInfo: InterfaceInfo in default): String`
<sub>línea 165</sub>

`public function arrayLit(a: ArrayLit in default, type: Type): String`
<sub>línea 194</sub>

---

## codegen.expressions.operators

`src/compiler/codegen/expressions/operators.lar` · 218 líneas · 12 funciones
codegen.expressions.operators: operators.

`public function wide(type: Type): String`
<sub>línea 15</sub>

`public function unary(u: Unary in default, type: Type): String`
<sub>línea 19</sub>

`public function binary(b: Binary in default, type: Type): String`
<sub>línea 30</sub>

`public function isTest(isExpr: IsExpr in default): String`  
x is T [b]: lar_as_class gives the object when it is a T (NULL otherwise); the binding keeps it.  
<sub>línea 90</sub>

`public function ternary(te: Ternary in default, type: Type): String`  
c ? a : b: a C conditional, or an if when a side needs statements of its own.  
<sub>línea 107</sub>

`function coalesce(binary: Binary in default, type: Type): String`
<sub>línea 126</sub>

`function operatorCall(method: MethodInfo, op: Expr in default, left: Expr in default, right: Expr? in default): String`  
a OP b, where the operator is a method of a's type; `op` is the expression (data it returns is created where it says).  
<sub>línea 153</sub>

`function operatorCallSwapped(method: MethodInfo, binary: Binary in default): String`  
b < a, keeping the evaluation order a then b.  
<sub>línea 162</sub>

`function minMacro(p: Type): String`
<sub>línea 168</sub>

`function maxMacro(p: Type): String`
<sub>línea 170</sub>

`public function cast(c: Cast in default, to: Type in default): String`
<sub>línea 174</sub>

`function anyAs(v: String, type: Type in default, objectType: Type): String`  
`a as T`: T? holding the value if the Any has one of that kind (numbers convert when they fit).  
<sub>línea 186</sub>

---

## codegen.expressions.patterns

`src/compiler/codegen/expressions/patterns.lar` · 66 líneas · 2 funciones
codegen.expressions.patterns: the patterns of a switch.

`public function patternTest(patternInfo: PatternInfo in default, st: Type, inner: Type, subj: String, val: String): String`  
Joined only with || (several patterns in one case), so a comparison needs no parentheses of its own (clang warns about if ((a == b))).  
<sub>línea 11</sub>

`public function bindPattern(patternInfo: PatternInfo, inner: Type, subj: String, val: String): void`
<sub>línea 42</sub>

---

## codegen.expressions.strings

`src/compiler/codegen/expressions/strings.lar` · 220 líneas · 8 funciones
codegen.expressions.strings: strings: literals, interpolation and their methods.

`public function string(s: StringLit in default, memOverride: String): String`  
memOverride != "": the text is built in that memory.  
<sub>línea 13</sub>

`public function printDirect(s: StringLit in default, newline: bool): String?`  
print/println of a literal, or of a text whose parts are integers, bool, String or enums: straight to stdout (fputs or printf), with no text built in memory. null when it does not apply.  
<sub>línea 34</sub>

`function decodeRaw(raw: String in default): String`  
The bytes of a raw literal text (escapes interpreted; an unknown escape keeps its backslash).  
<sub>línea 86</sub>

`function cLiteral(text: String): String`  
The C literal of some bytes.  
<sub>línea 116</sub>

`public function appendPieces(s: StringLit in default, sbRef: String): void`  
Writes the parts of an interpolated text into a builder (sbRef: a LarTextBuilder*).  
<sub>línea 125</sub>

`public function stringLiteral(raw: String): String`
<sub>línea 153</sub>

`function cBytes(raw: String): String`
<sub>línea 163</sub>

`function cByte(builder: StringBuilder, v: byte, text: String): void`
<sub>línea 200</sub>

---

## codegen.gen

`src/compiler/codegen/gen.lar` · 714 líneas · 25 funciones
codegen.gen: C99 code generation (Gen.java), part 1: the file, types, classes and interfaces,
globals, bodies and statements. Expressions are in genexpr.lar.

- struct     -> C struct, copied by value; methods are plain functions on S*.
- class      -> C struct in a memory, used through pointers. The root struct starts with
LarObjectHeader (vtable + memory); a subclass embeds its parent as `_super`.
- interface  -> { void* obj; const I_Table* t; }
- enum       -> { int32_t tag; union { ...payloads } as; }
- closure    -> { fn; union of every environment of that type }, copied by value.
- T[N]       -> { length; items[N] } by value; T[] -> { items*, length };
T[*] -> pointer to { items*, length, capacity, mem }.
- errors     -> a function that throws takes LarError* err_out; every call checks it.
- memories   -> LarMemory; heap memories are freed on every exit of their block.

### class `Block`

### class `TryCtx`

### class `ArmCtx`

### class `FunctionCode`

### class `Temp`
A statement's temporary memory, declared before the statement only if something used it.

`public function newFunctionCode(): FunctionCode`
<sub>línea 76</sub>

### class `Generation`
The state of the generator: the function being written, the pieces of C made on the way (lambdas, literals, helpers) and its errors.

`public function useGeneration(state: Generation in default): void`  
Makes `state` the one the compiler works on.  
<sub>línea 110</sub>

`public function internalError(line: int32, msg: String): void`
<sub>línea 114</sub>

`public function lineMark(encoded: int32): String`
<sub>línea 124</sub>

`function cPathLiteral(path: String): String`
<sub>línea 131</sub>

`public function spreadLines(c: String, cFile: String): String`  
After generating with debugLines: inside a function, every line of C after a #line gets that same .lar line (C would count on: N, N+1, N+2...); after the function, the lines are the C file's again, so the runtime and helpers are shown as the C they are.  
<sub>línea 138</sub>

`function firstMark(all: String[*], k: int32): String`  
The first #line of the function whose header is all[k] (before the function ends), or "".  
<sub>línea 185</sub>

`public function line(s: String): void`
<sub>línea 198</sub>

`public function tmp(role: String): String`  
A temporary of the function being generated, by what it is: its name comes from codegen.localnames.  
<sub>línea 208</sub>

`public function indent4(text: String in default): String`  
Adds four spaces to every line (like String.indent(4) in Java).  
<sub>línea 211</sub>

`public function pushBlock(blockCode: Block in default): void`
<sub>línea 223</sub>

`public function popBlock(): void`
<sub>línea 225</sub>

`public function topBlock(): Block`
<sub>línea 235</sub>

`public function rootBlock(): Block`
<sub>línea 236</sub>

`public function generate(): String`  
The C of the analyzed program: emitC, then nameC, then pruneC (the passes EmitC, NameC and Prune).  
<sub>línea 244</sub>

`public function nameC(program: CProgram): void`  
NameC: the names of the compiler's variables (codegen.localnames). A function's are named when it is written; here, those left in the text between them.  
<sub>línea 254</sub>

`public function emitC(): CProgram`  
EmitC: the whole program, every function and type, before anything is cut: text, and each function whole.  
<sub>línea 261</sub>

`public function pruneC(emitted: CProgram): String`  
Prune: only what main and the ccode reach, after the runtime it needs.  
<sub>línea 576</sub>

`function resources(out: StringBuilder): void`  
Resources (extern type X released by f): a value lives in a cell of the memory it was made in, with its state; the memory releases it when it is freed, unless release(x) already did.  
<sub>línea 606</sub>

`function shortName(n: String): String`  
A name without its module prefix: std__net__Socket -> Socket.  
<sub>línea 651</sub>

`function sectionOf(out: StringBuilder, title: String, content: StringBuilder): void`
<sub>línea 656</sub>

`public function section(out: StringBuilder, title: String): void`
<sub>línea 662</sub>

`function bodyText(body: String in default): String`  
A C body as it was written, indented once (its closing line's indentation does not count).  
<sub>línea 669</sub>

`function stripIndent(code: String in default): String`  
Like Java's stripIndent().strip(): removes the common indentation and the blank lines around.  
<sub>línea 677</sub>

`public function classesByDepth(): ClassInfo[*]`
<sub>línea 700</sub>

---

## codegen.gen.classes

`src/compiler/codegen/gen/classes.lar` · 351 líneas · 28 funciones
codegen.gen.classes: classes, interfaces and closures in C; globals and the entry point.

`function errParam(throwsOut: bool): String`
<sub>línea 15</sub>

`public function returnsData(ret: Type): bool`  
Returning something that points to memory: the function creates it in the memory of the call.  
<sub>línea 20</sub>

`public function params(paramSymbols: Symbol[*], memParams: bool[*]): String`
<sub>línea 22</sub>

`public function functionHeader(functionInfo: FunctionInfo): String`
<sub>línea 30</sub>

`public function methodName(method: MethodInfo): String`
<sub>línea 41</sub>

`public function methodHeader(method: MethodInfo, isStructMethod: bool): String`
<sub>línea 52</sub>

`public function nativeMethodHeader(method: MethodInfo): String`
<sub>línea 65</sub>

`public function lambdaHeader(lambdaInfo: LambdaInfo): String`
<sub>línea 72</sub>

`public function paramCTypes(method: MethodInfo in default): String[*]`  
The C parameters after self: the memory of the call first when it returns data.  
<sub>línea 81</sub>

`public function vtableStruct(out: StringBuilder, classInfo: ClassInfo in default): void`
<sub>línea 90</sub>

`public function vtableInit(concrete: ClassInfo in default, level: ClassInfo): String`
<sub>línea 107</sub>

`public function dispatchName(intro: String, method: MethodInfo): String`
<sub>línea 122</sub>

`function argsDecl(paramTypes: String[*], throwsOut: bool): String`
<sub>línea 124</sub>

`function argsPass(n: int32, throwsOut: bool): String`
<sub>línea 131</sub>

`function retWord(type: Type): String`
<sub>línea 142</sub>

`public function dispatchHelper(out: StringBuilder, classInfo: ClassInfo, method: MethodInfo in default): void`
<sub>línea 146</sub>

`public function interfaceTableStruct(out: StringBuilder, interfaceInfo: InterfaceInfo in default): void`
<sub>línea 153</sub>

`public function ifaceCallName(interfaceInfo: InterfaceInfo, method: MethodInfo): String`
<sub>línea 165</sub>

`public function interfaceCallHelper(out: StringBuilder, interfaceInfo: InterfaceInfo, method: MethodInfo in default): void`
<sub>línea 167</sub>

`public function interfaceImplementations(out: StringBuilder): void`  
For each class that declares `implements I`: thunks plus a table.  
<sub>línea 175</sub>

`public function samTable(out: StringBuilder, interfaceInfo: InterfaceInfo in default): void`
<sub>línea 193</sub>

`public function samThunk(out: StringBuilder, interfaceInfo: InterfaceInfo in default): void`
<sub>línea 201</sub>

`public function closureCallHelper(out: StringBuilder, functionType: Type): void`
<sub>línea 208</sub>

`public function collectionHelpers(out: StringBuilder, type: Type): void`
<sub>línea 224</sub>

`public function initGlobals(): String`
<sub>línea 258</sub>

`public function mainWrapper(): String`
<sub>línea 280</sub>

`public function clonePrototypes(): String`
<sub>línea 328</sub>

`public function classClone(out: StringBuilder, classInfo: ClassInfo in default): void`
<sub>línea 334</sub>

---

## codegen.gen.statements

`src/compiler/codegen/gen/statements.lar` · 651 líneas · 31 funciones
codegen.gen.statements: bodies and statements, switch included.

`function usesErrors(body: Stmt[*] in default): bool`
<sub>línea 24</sub>

`public function body(stmts: Stmt[*] in default, ret: Type in default, throwsOut: bool, lambda: LambdaInfo? in default,`  
lock != "": a method of a synchronized class, locked for its whole run (unlocked on every exit).  
<sub>línea 45</sub>

`public function endsWithJump(stmts: Stmt[*]): bool`
<sub>línea 94</sub>

`function emitCleanups(blockCode: Block): void`
<sub>línea 100</sub>

`public function block(stmts: Stmt[*] in default): void`
<sub>línea 108</sub>

`function bracedBlock(stmts: Stmt[*] in default): void`  
A block between braces, one level in.  
<sub>línea 118</sub>

`public function cleanupsUntil(stop: Block): void`  
Emits the cleanups of every block from the innermost up to `stop` (inclusive).  
<sub>línea 125</sub>

`function anyCleanups(stop: Block): bool`
<sub>línea 135</sub>

`public function stmt(s: Stmt in default): void`  
A statement; what it creates without a place lives in its temporary memory, freed when it ends.  
<sub>línea 147</sub>

`public function openMemory(stmts: Stmt[*] in default): void`  
A block whose variables hold data gets its memory, freed when the block ends.  
<sub>línea 179</sub>

`public function tempMem(): String`  
The current statement's temporary memory (declared before it the first time it is used).  
<sub>línea 187</sub>

`function stmtInner(s: Stmt in default): void`
<sub>línea 197</sub>

`function assign(s: AssignStmt in default): void`
<sub>línea 229</sub>

`function placeParts(target: Expr in default, parts: Expr[*] in default): void`  
The parts of a place that are computed, in order: the object and the index of a[i], the object of a.f. An object that is a value (a struct, a T[N]) is not copied: its own place is looked into.  
<sub>línea 253</sub>

`function placeObject(o: Expr in default, parts: Expr[*] in default): void`
<sub>línea 264</sub>

`function assignTo(s: AssignStmt in default, target: Expr in default): void`
<sub>línea 273</sub>

`function varDecl(v: VarDecl in default): void`
<sub>línea 295</sub>

`public function ret(r: ReturnStmt in default): void`
<sub>línea 320</sub>

`function ifStmt(i: IfStmt in default): void`
<sub>línea 338</sub>

`function whenStmt(ifStmt: IfStmt in default): void`  
An if for platforms (IfStmt.platform): C's #if / #elif / #else / #endif, with no braces, so what a branch declares stays for the code after it. Every branch is written (the C compiler keeps one); what a branch leaves to free at the end of the block is freed only where that branch is kept.  
<sub>línea 358</sub>

`function keptWhen(c: String, above: String[*]): String`  
When the C compiler keeps a branch: its condition, and none of the ones above.  
<sub>línea 379</sub>

`function whenBranch(stmts: Stmt[*] in default, kept: String): void`
<sub>línea 384</sub>

`function loopBlockOpen(): Block`  
Opens the block of a loop body.  
<sub>línea 394</sub>

`function loopBody(body: Stmt[*] in default, blockCode: Block in default): void`
<sub>línea 401</sub>

`function whileStmt(w: WhileStmt in default): void`
<sub>línea 408</sub>

`function indexVar(ix: Symbol? in default, value: String): void`  
`int32_t i = idx;` for the index variable of a for, if it has one.  
<sub>línea 426</sub>

`function forStmt(f: ForStmt in default): void`
<sub>línea 432</sub>

`public function throwStmt(t: ThrowStmt in default): void`
<sub>línea 509</sub>

`public function propagate(): void`  
Sends the current error to the innermost try, or to the caller.  
<sub>línea 518</sub>

`function tryStmt(t: TryStmt in default): void`
<sub>línea 534</sub>

`public function switchCode(switchExpr: SwitchExpr in default, isExpr: bool): String`
<sub>línea 574</sub>

---

## codegen.gen.types

`src/compiler/codegen/gen/types.lar` · 232 líneas · 12 funciones
codegen.gen.types: the C of the types of a program.

`public function externPrototype(functionInfo: FunctionInfo in default): String`  
C functions receive String as a NUL-terminated const char*.  
<sub>línea 14</sub>

`public function externDefinition(functionInfo: FunctionInfo in default): String`  
The header of the C function of a C body, with its parameters named as in Larimar (a T[] is name and name_length).  
<sub>línea 35</sub>

`public function larInC(code: String): String`  
ccode with lar"name" (the linker gave the linked name): the C name of that function, type or global.  
<sub>línea 54</sub>

`public function larPrototypes(code: String, out: StringBuilder): void`  
The prototypes of the Larimar functions a ccode names (those with C types the runtime already has).  
<sub>línea 72</sub>

`function plainSig(signature: Type): bool`  
Only numbers, bool, String and void: C types the runtime declares before any ccode.  
<sub>línea 87</sub>

`function cNameOf(name: String): String`
<sub>línea 96</sub>

`public function isCName(n: String): bool`  
A plain C name (a function a prototype can declare), not C text.  
<sub>línea 109</sub>

`public function externCType(type: Type): String`
<sub>línea 117</sub>

`function cStruct(type: Type): bool`  
A C struct (extern type X = struct { ... }): C defines it, Larimar does not.  
<sub>línea 126</sub>

`public function forward(out: StringBuilder, type: Type): void`
<sub>línea 132</sub>

`public function define(out: StringBuilder, t: Type): void`
<sub>línea 148</sub>

`public function envField(symbol: Symbol): String`
<sub>línea 231</sub>

---

## codegen.localnames

`src/compiler/codegen/localnames.lar` · 89 líneas · 6 funciones
codegen.localnames: the names of the C variables the compiler makes in a function (its temporaries,
its memories, the result it returns). Each is asked for by what it is (`localName("result")`), and gets
that name, or `result_2`, `result_3`... when the name is taken in the function: by another temporary,
or by anything the function's C already names (a variable of the Larimar code, a global, a function).

While a function is generated, a temporary is a mark in its text (its role and a number of its own);
when the function is done, nameLocals gives each mark its name. So a name never meets a name of the
code, whichever comes first in the text.

`function markByte(): String`  
The byte that starts and ends the parts of a mark (it never appears in the C: texts escape it).  
<sub>línea 11</sub>

`public function localName(role: String): String`  
The name of a temporary that is `role` (letters, digits and '_'): one of its own, decided by nameLocals.  
<sub>línea 20</sub>

`public function localNameFor(role: String, key: String): String`  
The same temporary for a key that names it already (a memory of a block of the analysis: mem_3).  
<sub>línea 26</sub>

`function isNameStart(c: byte): bool`
<sub>línea 28</sub>

`function isNamePart(c: byte): bool`
<sub>línea 30</sub>

`public function nameLocals(text: String): String`  
The text with each mark replaced by its name: the role, or the role and a number when it is taken.  
<sub>línea 33</sub>

---

## codegen.prune

`src/compiler/codegen/prune.lar` · 500 líneas · 22 funciones
codegen.prune: only the C the program reaches, of what it generates and of the runtime.

The C is cut into pieces: the generated program into declarations (a function, a type, a helper, a
prototype, a global), the runtime into paragraphs (blank lines outside braces and #if blocks; each
#include is one). A piece is kept when it defines a name that a kept piece uses. For the program, the
roots are main, the export functions, and what the program wrote in C itself (cinclude, ccode), which
stays whole; the ccode of the standard library ("ccode (std)") is cut like the rest. For the runtime,
the roots are the names the pruned program uses; #ifdef LAR_THREADS and #ifdef LAR_FILES are decided here.

The runtime itself is C, in the ccode of runtime/*.lar, beside std/ (read in the order of runtimeFiles):
editing it does not change the compiler, nor the bootstrap.

### class `Piece`
A piece of C: a declaration of the program, a paragraph of the runtime, or a heading over them.

`function rootSection(title: String): bool`  
Sections written by the program itself: they stay whole, and what they use is kept.  
<sub>línea 37</sub>

`public function prune(program: CProgram, roots: String[*]): String`  
The generated program without what it does not reach. roots: main and the export functions. A function of the CProgram is a piece as it is; its text between them is cut into declarations.  
<sub>línea 45</sub>

`function flush(pieces: Piece[*], lines: String[*], root: bool): void`  
The lines gathered so far become a piece.  
<sub>línea 99</sub>

`function flushHeader(pieces: Piece[*], lines: String[*]): void`  
The lines of a header of a native interface become a piece: it defines what its comment says it gives.  
<sub>línea 107</sub>

`function runtimeC(file: String): String`  
The C of a runtime file: between "ccode {" and the last "}" (each file is that one ccode).  
<sub>línea 127</sub>

`function runtimeSource(): String`
<sub>línea 135</sub>

`function headerNames(i: int32): String`
<sub>línea 159</sub>

`public function selectRuntime(program: String, threads: bool, files: bool, allHeaders: bool): String`  
The runtime the program needs, in the runtime's order. allHeaders: the program has its own C (ccode, native), which may count on the standard headers.  
<sub>línea 174</sub>

`function paragraph(pieces: Piece[*], lines: String[*]): void`  
The lines gathered so far become a paragraph: a heading when it is only a comment.  
<sub>línea 211</sub>

`function includePiece(line: String): Piece`  
#include <stdio.h>: it defines what that header gives.  
<sub>línea 221</sub>

`function resolve(text: String, threads: bool, files: bool): String[*]`  
Keeps the lines that apply: #ifdef LAR_THREADS / LAR_FILES (and their #else) are decided; other #if stay.  
<sub>línea 233</sub>

`function reach(pieces: Piece[*], wanted: String[*]): bool[*]`  
For each piece, whether it is kept: a root, or one that defines a name wanted or used by a kept one.  
<sub>línea 287</sub>

`function kept(pieces: Piece[*], keep: bool[*], i: int32): bool`  
A piece that is kept; a heading goes with what is kept under it.  
<sub>línea 330</sub>

`function describe(p: Piece): void`  
What a piece defines (at its top level) and every name it uses.  
<sub>línea 341</sub>

`function statementEnd(toks: String[*], from: int32): int32`  
Where the statement that starts at `from` ends: its `;` outside braces (toks.length if none).  
<sub>línea 395</sub>

`function define(p: Piece, defined: Any, name: String): void`
<sub>línea 405</sub>

`function unique(toks: String[*]): String[*]`  
The names of some tokens, each once.  
<sub>línea 412</sub>

`function names(c: String): String[*]`  
The names a C text mentions, each once (comments, strings and character literals left out).  
<sub>línea 424</sub>

`public function braceDelta(ln: String): int32`  
The braces a line opens minus those it closes (strings and comments left out).  
<sub>línea 432</sub>

`public function isName(t: String): bool`
<sub>línea 466</sub>

`function letter(c: byte): bool`
<sub>línea 468</sub>

`public function tokens(c: String): String[*]`  
C tokens: names, numbers and single punctuation characters; comments, strings and characters are skipped.  
<sub>línea 471</sub>

---

## project.cc

`src/compiler/project/cc.lar` · 149 líneas · 11 funciones
project.cc: calling the C compiler and other programs (larimar build, larimar test).

`public function windows(): bool`
<sub>línea 9</sub>

`public function mac(): bool`
<sub>línea 10</sub>

`public function quote(a: String): String`  
Quotes an argument for the shell.  
<sub>línea 13</sub>

`public function commandLine(args: String[*]): String`  
The arguments joined, each quoted: a command for os.run.  
<sub>línea 18</sub>

`public function systemLibraries(c: String): String[*]`  
What the generated C needs from the system when linking: threads, sockets, TLS.  
<sub>línea 25</sub>

`public function selfPath(): String`  
The compiler itself (bin/larimarc), to run it as another process.  
<sub>línea 49</sub>

### class `CCompiler`
The C compiler of a build: the program and the arguments that go right after it.

`public function bundledTcc(home: String): String`  
The tcc that comes with Larimar on Linux and Windows ($LARIMAR_HOME/toolchain/tcc), or "".  
<sub>línea 68</sub>

`function tccCompiler(exe: String): CCompiler`  
The bundled tcc with what it needs: on Linux it links statically with the musl next to it.  
<sub>línea 74</sub>

`public function systemCompiler(): String`  
The system's C compiler: cc, gcc or clang (on Windows gcc, clang or cc), or "" when there is none.  
<sub>línea 86</sub>

`public function chooseCompiler(home: String, wanted: String, script: bool, tls: bool, problem: String[*]): CCompiler?`  
The C compiler for a build. `wanted` is what was asked for (--cc, [c] compiler, CC; "" for none, and "tcc" is the bundled one when the system has no tcc). A script (larimar file.lar) prefers the bundled tcc, which starts fast; a project the system's, which optimizes. A program with TLS needs the system's: the bundled tcc cannot build it. null when there is none, and `problem` says what to install.  
<sub>línea 101</sub>

`public function installHint(): String`  
The command that installs a C compiler here.  
<sub>línea 133</sub>

---

## project.libraries

`src/compiler/project/libraries.lar` · 96 líneas · 4 funciones
project.libraries: the libraries written in Larimar that a project uses, as source.

[dependencies] of larimar.toml names each one with its folder: the folder of a library project
([project] kind = "library"), whose main file (src/<name>.lar) is `import <name>`. Its other modules are
<name>.<part> (src/<name>/<part>.lar): a library's modules all start with its name, so they never meet the
program's. It is compiled with the program, in the same C and with the same runtime, and the language
is the same on both sides: classes, interfaces, lists, throws.

A library's own [dependencies] are read too (their folders are relative to the library's): a program names
only the libraries it imports. Two libraries with the same name in different folders are an error.

### class `LarimarLibrary`
A library of [dependencies]: its name (its module) and the folder of its modules.

`public function larimarLibraries(dir: String, config: Any, problems: String[*]): LarimarLibrary[*]`  
The libraries of a project's [dependencies], and theirs. Problems go to `problems`.  
<sub>línea 26</sub>

`function collect(dir: String, config: Any, of: String, out: LarimarLibrary[*], problems: String[*]): void`  
The [dependencies] of one larimar.toml (of the program, or of a library: `of` is its name).  
<sub>línea 33</sub>

`function libraryConfig(name: String, folder: String, from: String, problems: String[*]): Any`  
The larimar.toml of a library's folder, checked to be that library's (null: a problem was given).  
<sub>línea 62</sub>

`function named(libraries: LarimarLibrary[*], name: String): LarimarLibrary?`
<sub>línea 90</sub>

---

## project.testing

`src/compiler/project/testing.lar` · 485 líneas · 27 funciones
project.testing: larimar test, the test runner.

larimar test [file|folder]... [--only <text>] [--test <name>]... [--list] [--json] [--no-sanitize]

--list shows the tests without running them. --json writes one JSON object per line, for editors:

{"event": "found", "file": "tests/a_test.lar", "path": "/.../tests/a_test.lar", "name": "adds", "line": 4}
{"event": "result", "file": ..., "path": ..., "name": "adds", "line": 4, "result": "passed", "message": ""}
{"event": "summary", "passed": 3, "failed": 1, "skipped": 0}

"result" is passed, failed or skipped.

A test passes (exit 0), fails (1: a check failed; 101: a panic; a memory error...) or is skipped (3:
std.test's skip(), when it cannot run here).

It runs the test functions (`test function name(): void { ... }`) of the .lar files under tests/ (or the
ones given). For each file, `larimarc test-main` writes the file again with a main of its own
(build/test/<file>.lar, to read), and compiles it. Each test then runs alone, in its own process:
`program <test name>`.

Other .lar files (modules that the tests import) are not run. With AddressSanitizer and UBSan, except
on Windows or with --no-sanitize.

### class `TestSettings`
How the tests are compiled: the project's [c] settings, or the defaults when there is no project.

### class `TestFunction`
A test function of a file.

`public function testFunctions(source: String in default): TestFunction[*]`  
The test functions of a file, in order (none when it has syntax errors: the compiler shows them).  
<sub>línea 60</sub>

`public function hasMain(source: String in default): bool`  
Whether the file declares a main of its own.  
<sub>línea 76</sub>

`public function withMain(source: String, tests: TestFunction[*]): String`  
The file with a main added: `program <name>` runs that test and ends with 0 (it passed), 1 (a check failed), 3 (it was skipped) or 2 (no test has that name). std.test is imported on the first line, so the lines of the file do not move and its errors keep their line numbers.  
<sub>línea 89</sub>

`public function runTests(args: String[*], s: TestSettings in default): int32`
<sub>línea 143</sub>

`function collect(dir: String, into: String[*]): void`  
The .lar files of a folder and its folders.  
<sub>línea 228</sub>

`function sortTexts(xs: String[*]): void`  
Sorts texts by their bytes (the order of the files every time).  
<sub>línea 242</sub>

`function before(a: String, b: String): bool`
<sub>línea 256</sub>

`function hasTestFunctions(source: String): bool`
<sub>línea 266</sub>

`function base(shown: String): String`  
build/test/<the file's path, with '_' for the folders>: where the files of one test go.  
<sub>línea 274</sub>

`function selected(shown: String, name: String): bool`  
Whether a test runs: the names given with --test, else the ones --only matches ("": the file itself).  
<sub>línea 281</sub>

`function list(shown: String, tests: TestFunction[*]): void`  
--list: the tests of a file.  
<sub>línea 287</sub>

`function found(shown: String, name: String, line: int32): void`
<sub>línea 293</sub>

`function lineOf(name: String): int32`  
The line of a test of the file that runs (1 for the file itself).  
<sub>línea 302</sub>

`function report(shown: String, name: String, result: String, message: String): void`  
A result: a line for a person (ok, FAIL, skip), or a JSON object with --json.  
<sub>línea 307</sub>

`function pass(shown: String, name: String): void`
<sub>línea 327</sub>

`function failed(shown: String, name: String, problem: String): void`
<sub>línea 332</sub>

`function skip(shown: String, name: String, why: String): void`
<sub>línea 337</sub>

`function fileFailed(shown: String, problem: String): void`  
A file of tests that did not get to run (it did not compile): for a person, one failure; with --json, each of its tests fails with that message, so an editor marks them.  
<sub>línea 346</sub>

`function read(path: String): String`
<sub>línea 356</sub>

`function head(text: String, count: int32): String`  
The first lines of a text (what a failure shows).  
<sub>línea 361</sub>

`function compileC(cFile: String, exe: String): String`  
Compiles the C of a test into an executable; "" when it worked, else what the C compiler said.  
<sub>línea 375</sub>

`function runProgram(exe: String, args: String[*], outFile: String, errFile: String): int32`  
Runs a program, its output to <base>.out and <base>.err; gives its exit code.  
<sub>línea 407</sub>

`function memoryError(err: String): bool`
<sub>línea 415</sub>

`function memoryReport(err: String): String`  
The lines of a sanitizer's report that say what happened.  
<sub>línea 420</sub>

`function skipText(out: String): String`  
What a skipped test said: the text after "skipped: ".  
<sub>línea 433</sub>

`function exeName(b: String): String`
<sub>línea 440</sub>

`function runTestFile(file: String, shown: String, source: String): void`  
A file of test functions: compiled once with a main, then each test runs alone.  
<sub>línea 443</sub>

---

## editor.dap

`src/compiler/editor/dap.lar` · 1269 líneas · 62 funciones
editor.dap: larimar dap, the debugger for editors (Debug Adapter Protocol on stdin and stdout).

It sits between the editor and lldb-dap (LLVM's debug adapter, which runs the program under lldb):

VS Code  <-- DAP -->  larimar dap  <-- DAP -->  lldb-dap  -->  the program (built with --debug)

Most messages pass through as they are (launch, breakpoints, continue, step...). What makes it Larimar
is answered here, with the debug map the compiler writes next to the C (debugmap.lar):

- the call stack shows Larimar names (main, Dog.bark, geo.shapes.area), and the runtime's frames
are de-emphasized;
- the variables are those of the Larimar code, with their Larimar names (total, not total_12),
without the compiler's temporaries, and each value is read and shown as Larimar shows it: String
as text, lists with their elements, optionals, enums as Variant(fields), objects with their real
class, Any with what it holds. The values are read with C expressions lldb evaluates
((long long)(x).len, memory read ...): nothing to install in lldb;
- the debug console and hovers understand Larimar paths (a.name, list[2], data.inner);
- function breakpoints take Larimar names, "step into" skips the runtime, and "Panics" stops where
a panic happens.

`function contentLength(line: String): int32`  
The value of a "Content-Length: N" header line, or -1.  
<sub>línea 66</sub>

`function editorMessage(ms: int32): String?`  
The body of the editor's next message, waiting up to ms for it (-1: until one comes); null when none came or it ended.  
<sub>línea 73</sub>

`function backendMessage(ms: int32): String?`  
The body of the backend's next message, waiting up to ms for it to begin; null when none came or it ended.  
<sub>línea 99</sub>

`function toBackendRaw(body: String): void`  
Writes one message to the backend (nothing when it has ended).  
<sub>línea 127</sub>

### struct `Handle`

`function keep(text: String): void`
<sub>línea 151</sub>

`function newHandle(kind: int32, frame: int32, ref: int32, expr: String, type: String): int32`
<sub>línea 158</sub>

`function handleAt(id: int32): Handle?`
<sub>línea 167</sub>

`function log(text: String): void`
<sub>línea 172</sub>

`function withNumber(json: String, key: String, value: int32): String`  
A JSON text with the top-level numeric field `key` set to `value` (added when missing).  
<sub>línea 179</sub>

`function toEditorRaw(body: String): void`
<sub>línea 210</sub>

`function emit(body: String): void`  
A message to the editor with our sequence number.  
<sub>línea 217</sub>

`function respond(req: Any, body: String): void`
<sub>línea 223</sub>

`function respondError(req: Any, message: String): void`
<sub>línea 229</sub>

`function output(text: String): void`
<sub>línea 235</sub>

`function parse(text: String): Any`
<sub>línea 239</sub>

`function sendBackend(command: String, args: String): int32`  
Sends a request of ours to the backend; returns its seq.  
<sub>línea 248</sub>

`function call(command: String, args: String): String`  
A request of ours to the backend, and its response (as JSON text). What arrives meanwhile from the backend (events, answers to forwarded requests) goes on to the editor; the editor's messages wait.  
<sub>línea 260</sub>

`function eval(frame: int32, expr: String): String?`  
A C expression's value in a frame, or null when lldb cannot evaluate it.  
<sub>línea 279</sub>

`function evalInt(frame: int32, expr: String): int64?`
<sub>línea 285</sub>

`function evalAddress(frame: int32, expr: String): int64?`
<sub>línea 291</sub>

`function command(frame: int32, text: String): String`  
An lldb command in a frame; its output.  
<sub>línea 303</sub>

`function tableOf(v: Any): Any`  
A table of the debug map (or an empty one when it is missing).  
<sub>línea 309</sub>

`function atMost(n: int64, limit: int32): int32`
<sub>línea 316</sub>

`function hexValue(s: String): int64`
<sub>línea 318</sub>

`function readBytes(frame: int32, address: int64, count: int32): String?`  
`count` bytes at an address, as text (UTF-8).  
<sub>línea 329</sub>

`function readCString(frame: int32, expr: String): String?`  
A C string (a class's name) at the address an expression gives.  
<sub>línea 346</sub>

### class `Shown`
What the editor shows for one value: its text, and its children (a handle) when it has them.

`function typeEntry(name: String): Any`
<sub>línea 367</sub>

`function typeText(t: Any): String`
<sub>línea 369</sub>

`function quoteText(s: String): String`
<sub>línea 386</sub>

`function stringValue(frame: int32, expr: String): String?`  
The text of a String value at expr (a LarString).  
<sub>línea 389</sub>

`function classOfObject(frame: int32, pointer: String): String`  
The class (C name) of the object at a pointer expression, or "".  
<sub>línea 402</sub>

`function show(frame: int32, expr: String, t: Any, preview: bool): Shown?`  
How the editor shows the value of `expr` (a C expression) of type `t`. preview: a short text only.  
<sub>línea 407</sub>

`function showAny(frame: int32, expr: String, preview: bool, s: Shown): Shown?`
<sub>línea 563</sub>

`function fieldsPreview(frame: int32, entry: Any, access: String, preview: bool, display: String): String`  
Point {x=1, y=2}: the first scalar fields, read with `access` + their C path.  
<sub>línea 592</sub>

`function variableJson(name: String, s: Shown, evaluateName: String): String`  
The JSON of one variable for the editor.  
<sub>línea 615</sub>

`function children(id: int32, start: int32, count: int32): String[*]`  
The children of a value handle.  
<sub>línea 622</sub>

`function fieldVariables(frame: int32, fields: Any, access: String, out: String[*]): void`
<sub>línea 677</sub>

`function hasFunction(cName: String): bool`
<sub>línea 692</sub>

`function functionEntry(cName: String): Any`
<sub>línea 693</sub>

`function localVariables(frame: int32): String[*]`  
The Larimar variables of a frame.  
<sub>línea 696</sub>

`function globalVariables(frame: int32): String[*]`
<sub>línea 731</sub>

### class `Resolved`

`function resolvePath(frame: int32, text: String): Resolved`
<sub>línea 751</sub>

`function splitPath(text: String): String[*]`  
"a.b[2].c" -> ["a", ".b", "[2]", ".c"]; [] when it is not a path.  
<sub>línea 793</sub>

`function isNameByte(c: byte): bool`
<sub>línea 819</sub>

`function step(frame: int32, r: Resolved, part: String): bool`  
One step of a path: .field or [index].  
<sub>línea 824</sub>

`function fromEditor(body: String): bool`
<sub>línea 872</sub>

`function forward(body: String, msg: Any, args: String): void`  
Passes a request on to the backend (with new arguments when `args` is not "").  
<sub>línea 909</sub>

`function capabilities(r: Any): String`
<sub>línea 918</sub>

`function launchArguments(msg: Any): String`  
launch for lldb-dap: the program, and lldb set up for Larimar.  
<sub>línea 932</sub>

`function loadMap(path: String): void`
<sub>línea 951</sub>

`function functionBreakpoints(msg: Any): String`  
Function breakpoints by Larimar name: main -> user_main, Dog.bark -> Dog_bark.  
<sub>línea 966</sub>

`function exceptionBreakpoints(msg: Any): void`
<sub>línea 978</sub>

`function stackTrace(msg: Any): void`  
The call stack with Larimar names; the runtime's frames de-emphasized.  
<sub>línea 1002</sub>

`function scopes(msg: Any): void`
<sub>línea 1031</sub>

`function variables(msg: Any): void`
<sub>línea 1047</sub>

`function backendVariables(frame: int32, ref: int32): String[*]`  
lldb-dap's own variables (the C view), with our handles for their children.  
<sub>línea 1074</sub>

`function evaluate(body: String, msg: Any): void`  
The debug console, hovers and watches: Larimar paths here; the rest (C, lldb commands) to lldb.  
<sub>línea 1088</sub>

`function isPanicStop(msg: Any): bool`
<sub>línea 1121</sub>

`function exceptionInfo(msg: Any): void`  
The panic's message: the msg argument of lar_panic, at the top of the thread's stack.  
<sub>línea 1132</sub>

`function fromBackend(body: String, msg: Any): void`
<sub>línea 1145</sub>

`function findBackend(given: String): String`  
lldb-dap: the one given, $LARIMAR_LLDB_DAP, on the PATH, or Xcode's (xcrun).  
<sub>línea 1184</sub>

`public function serveDebugger(args: String[*]): int32`
<sub>línea 1209</sub>

---

## editor.ide

`src/compiler/editor/ide.lar` · 1502 líneas · 74 funciones
editor.ide: answers the editor's questions (larimar lsp) from an analyzed program: errors, hover, go to
definition, references, the symbols of a file, completion and the signature being written.

It runs in a process made only for one question (see lsp.lar): it may keep what it builds for the
whole process, which ends when it answers. Positions come from the editor as (line, character) from 0,
with characters counted in UTF-16; the compiler counts lines from 1 (with the file in the number, see
FILE_LINES) and knows the line of each node, not its column, so the column of a name is found in the
text of its line.

### class `Lines`
The start of each line of a file (by file index), computed when first needed.

`function linesOf(index: int32): Lines`
<sub>línea 41</sub>

`public function lineText(index: int32, line: int32): String`  
The text of a line (from 1) of a file, without its end.  
<sub>línea 56</sub>

`function lineCount(index: int32): int32`
<sub>línea 65</sub>

`public function fileIndex(path: String): int32`  
The file index of a path in the analysis, or -1.  
<sub>línea 68</sub>

`function fileOf(encoded: int32): int32`
<sub>línea 76</sub>

`function lineOf(encoded: int32): int32`
<sub>línea 77</sub>

`public function utf16Col(line: String, byteCol: int32): int32`  
UTF-16 units of the first `byteCol` bytes of a line (what the editor counts).  
<sub>línea 80</sub>

`public function byteCol(line: String, units: int32): int32`  
The byte of a line where the editor's UTF-16 column falls.  
<sub>línea 92</sub>

`function nameByte(c: byte): bool`
<sub>línea 104</sub>

`function wordColumns(text: String, word: String, dotted: int32): int32[*]`  
The byte columns where `word` is written as a whole name; dotted: 1 after a '.', 0 not after one, -1 any.  
<sub>línea 107</sub>

### class `Word`
The name the cursor is on (bytes from..to of the line), and whether a '.' comes before it.

`function wordAt(line: String, col: int32): Word`
<sub>línea 133</sub>

`function rangeJson(index: int32, line: int32, from: int32, to: int32): String`  
A range of the editor, as JSON, for bytes from..to of a line (from 1) of a file.  
<sub>línea 147</sub>

`function lineRangeJson(index: int32, line: int32): String`  
The range of a whole line, without its indentation.  
<sub>línea 155</sub>

`public function uriOfPath(path: String): String`  
file:///a/b%20c.lar  
<sub>línea 164</sub>

`public function pathOfUri(uri: String): String`  
The path of a file:// URI.  
<sub>línea 180</sub>

`function hexValue(c: byte): int32`
<sub>línea 206</sub>

`function isStdFile(path: String): bool`
<sub>línea 213</sub>

`function shortName(name: String): String`  
The name as written: geo__shapes__Shape -> Shape, Order.make -> make.  
<sub>línea 223</sub>

`function shown(name: String): String`  
The name to show: geo__shapes__Shape -> geo.shapes.Shape.  
<sub>línea 233</sub>

`function typeText(t: Type?): String`
<sub>línea 235</sub>

`function collect(): void`
<sub>línea 246</sub>

`function method(m: MethodInfo in default): void`
<sub>línea 285</sub>

`function body(b: Stmt[*] in default): void`
<sub>línea 293</sub>

`function statements(b: Stmt[*] in default): void`
<sub>línea 298</sub>

### class `Target`

`function none(): Target`
<sub>línea 345</sub>

`function ofSymbol(s: Symbol in default): Target`
<sub>línea 347</sub>

`function ofFunc(functionInfo: FunctionInfo in default): Target`
<sub>línea 361</sub>

`function ofMethod(m: MethodInfo in default): Target`
<sub>línea 365</sub>

`function ofField(f: FieldInfo in default): Target`
<sub>línea 369</sub>

`function ofVariant(enumInfo: EnumInfo in default, v: VariantInfo in default): Target`
<sub>línea 373</sub>

`function ofType(linked: String): Target`  
A type by its name after linking, or K_NONE.  
<sub>línea 378</sub>

`function ofLinked(linked: String): Target`  
A declaration by its name after linking (geo__shapes__area).  
<sub>línea 400</sub>

`function targetAt(index: int32, line: int32, w: Word): Target`  
What the name under the cursor refers to.  
<sub>línea 415</sub>

`function signature(name: String, params: String[*], ret: String, throwsText: String): String`
<sub>línea 524</sub>

`function funcParams(functionInfo: FunctionInfo): String[*]`
<sub>línea 530</sub>

`function methodParams(method: MethodInfo): String[*]`
<sub>línea 541</sub>

`function funcLabel(functionInfo: FunctionInfo): String`
<sub>línea 551</sub>

`function methodLabel(method: MethodInfo): String`
<sub>línea 557</sub>

`function detail(target: Target): String`  
The code shown on hover.  
<sub>línea 563</sub>

`function typeOfConst(c: ConstDecl): String`
<sub>línea 617</sub>

`function typeDetail(linked: String): String`
<sub>línea 619</sub>

`function cText(c: String): String`  
C's name or type as a native declaration writes it: a plain name (FILE*) as it is, anything else as c"...".  
<sub>línea 674</sub>

`function docAbove(index: int32, line: int32): String`  
The comment written right above a declaration (// lines or a doc block), as text.  
<sub>línea 688</sub>

### class `Place`
Where a target is declared: file index, line and the byte columns of its name.

`function placeOf(target: Target): Place`
<sub>línea 724</sub>

`function locationJson(p: Place): String`
<sub>línea 743</sub>

### class `Cursor`
The cursor: a file index, a line from 1 and a byte column.

`function cursorOf(path: String, line0: int32, char16: int32): Cursor`
<sub>línea 759</sub>

`public function hoverJson(path: String, line0: int32, char16: int32): String`  
Hover: the declaration, as code, and its comment.  
<sub>línea 768</sub>

`function ownerNote(target: Target): String`
<sub>línea 785</sub>

`public function definitionJson(path: String, line0: int32, char16: int32): String`  
Go to definition.  
<sub>línea 799</sub>

`public function referencesJson(path: String, line0: int32, char16: int32, withDecl: bool): String`  
Every place that names the same thing (with its declaration when `withDecl`).  
<sub>línea 808</sub>

`function refersTo(e: Expr, target: Target): int32`  
Whether an expression names the target: -1 no; else how its name is written (1 after a '.', 0 not, -1 any).  
<sub>línea 863</sub>

`public function symbolsJson(path: String): String`  
The symbols of a file: its declarations, with the members of its types inside.  
<sub>línea 908</sub>

`function symbolJson(name: String, kind: int32, encoded: int32, word: String, kids: String[*]): String`
<sub>línea 965</sub>

`function blockEnd(index: int32, line: int32): int32`  
The line where the block a declaration opens on `line` closes (the same line when it has none).  
<sub>línea 978</sub>

`public function prepareCompletion(path: String, line0: int32, char16: int32, signatureHelp: bool): void`  
Before analyzing for completion or signature help: the line being written does not compile yet, so in this process the document gets a line that does (the rest of the program stays as it is).  
<sub>línea 1027</sub>

`function probeStatement(text: String, before: String, chainStart: int32, indent: String): String`  
A line that compiles and has `chain.probe()`, so the analysis gives the type of what comes before the '.'; "" when the names alone answer (a module or a type before the '.': the program must still link).  
<sub>línea 1074</sub>

`function needsNoProbe(text: String, chain: String): bool`  
A module alias (import ... as chain) or a type name: completed from the names, without a probe.  
<sub>línea 1085</sub>

`function openParen(before: String): int32`  
The '(' still open before the cursor, or -1.  
<sub>línea 1094</sub>

`function commasAfter(before: String, open: int32): int32`
<sub>línea 1109</sub>

`function chainBefore(line: String, dot: int32): String`  
The expression that ends right before byte `dot` (a '.'): names, dots, calls and indexes.  
<sub>línea 1128</sub>

### class `Items`

`function add(items: Items, label: String, kind: int32, detailText: String, doc: String): void`
<sub>línea 1179</sub>

`public function completionJson(path: String, line0: int32, char16: int32): String`  
Completion, after prepareCompletion and the analysis.  
<sub>línea 1189</sub>

`function probeObject(index: int32): Expr?`  
The probe left by prepareCompletion: the object before the '.'.  
<sub>línea 1203</sub>

`function memberItems(items: Items, index: int32): void`
<sub>línea 1212</sub>

`function memberItem(items: Items, method: MethodInfo): void`  
A method, or a native let (read without parentheses).  
<sub>línea 1241</sub>

`function typeMembers(items: Items, t: Type): void`
<sub>línea 1249</sub>

`function docOf(encoded: int32): String`
<sub>línea 1309</sub>

`function nameItem(items: Items, name: String, linked: String): void`  
A name a file can see, by its name after linking.  
<sub>línea 1315</sub>

`function nameItems(items: Items, index: int32): void`
<sub>línea 1339</sub>

`function enclosingStart(index: int32, line: int32): int32`  
The line where the function or method around a line starts, or 0.  
<sub>línea 1363</sub>

`function closer(best: int32, index: int32, start: int32, line: int32): int32`
<sub>línea 1378</sub>

`public function signatureJson(path: String): String`  
The signature of the call being written, after prepareCompletion(..., true) and the analysis.  
<sub>línea 1386</sub>

`function methodOf(firstType: Type, name: String): MethodInfo?`
<sub>línea 1441</sub>

`public function diagnosticsJson(requested: String): String`  
The errors of the analysis, per file: one { uri, diagnostics } per line, for every file of the program that is not part of std (so a file whose errors are fixed gets an empty list), and for any file with errors.  
<sub>línea 1473</sub>

---

## editor.lsp

`src/compiler/editor/lsp.lar` · 351 líneas · 21 funciones
editor.lsp: larimar lsp, the language server editors start (Language Server Protocol, JSON-RPC on stdin and
stdout, each message after a "Content-Length: N" header).

The server keeps the texts of the open documents (in a memory it compacts, as they change on every key)
and nothing else. Each question (the errors of a file, hover, go to definition, ...) is answered by a
new process, `larimarc lsp-worker`, which gets the question and the editor's texts in a file, links and
analyzes the program, writes its answer to another file and ends. So an analysis never leaves memory
behind, never sees the state of the one before, and a crash only loses one answer. The same on every
system, without a line of C.

The errors are computed when the editor stops typing (no message for a moment) for the file that
changed last, and published for every file of its program.

`function readMessage(): String?`  
The next message's body, or null when the editor closed the input.  
<sub>línea 40</sub>

`function send(body: String): void`
<sub>línea 59</sub>

`function respond(id: String, result: String): void`
<sub>línea 65</sub>

`function respondError(id: String, code: int32, message: String): void`
<sub>línea 69</sub>

`function notify(method: String, params: String): void`
<sub>línea 73</sub>

`function log(text: String): void`
<sub>línea 77</sub>

`function capabilities(): String`
<sub>línea 79</sub>

`function docPath(msg: Any): String`  
The normalized path of a message's text document.  
<sub>línea 88</sub>

### class `Documents`
The texts of the open documents (paths[i]: texts[i]), and the file whose errors are still to be published.

- `function size(): int64`  
  The bytes of the texts kept now (what a compaction keeps of them).  
  <sub>línea 104</sub>

- `function find(path: String): int32`  
  Where a path is ("" finds a free slot), or -1.  
  <sub>línea 111</sub>

`public function serve(): int32`  
larimar lsp  
<sub>línea 120</sub>

`function handle(body: String, kept: byte[*], docs: Documents in kept): int32`  
A message of the editor: -1 to go on, or the exit code of the server.  
<sub>línea 143</sub>

`function keep(kept: byte[*], docs: Documents in kept, path: String, text: String): void`  
The editor's new text of a file; its errors are published once the editor stops typing.  
<sub>línea 188</sub>

`function publish(path: String, docs: Documents): void`  
Publishes the errors of the program a file belongs to.  
<sub>línea 202</sub>

`function parsed(body: String): Any`
<sub>línea 210</sub>

`function pathOf(msg: Any): String`
<sub>línea 218</sub>

`function answer(msg: Any, path: String, main: String): String?`  
The answer after analyzing `main`, or null when that program does not reach the file.  
<sub>línea 225</sub>

`function readFile(path: String): String?`
<sub>línea 253</sub>

`function ask(body: String, docs: Documents): String`  
The answer (JSON) to a message, from a new process: a worker gets it and the editor's texts.  
<sub>línea 268</sub>

`function runWorker(req: String, resp: String): int32`  
Runs `larimarc lsp-worker req resp` and waits for it (at most WORKER_MS: then it is ended). What it writes is read and dropped: the standard output is the editor's, and a worker says nothing there.  
<sub>línea 303</sub>

`public function worker(reqPath: String, respPath: String): int32`  
larimarc lsp-worker: answers one question written to a file by the server.  
<sub>línea 323</sub>

---

## editor.opendocuments

`src/compiler/editor/opendocuments.lar` · 16 líneas · 2 funciones
editor.opendocuments: the texts of the documents open in the editor, by file path, for the analysis of one
question (larimar lsp-worker). The linker reads a file from here when it is open in the editor (with its
changes not saved yet), and from the disk otherwise.

A worker answers one question and ends, so the texts live in the default memory: nothing is ever freed
here. The server, which runs for hours while the texts change on every key, keeps its own copies in a
memory it compacts (editor.lsp, Documents).

`public function setOpenDocument(path: String, text: String): void`  
Keeps (a copy of) the editor's text of a file.  
<sub>línea 12</sub>

`public function openDocument(path: String): String?`  
The editor's text of a file, or null when it is not open.  
<sub>línea 15</sub>

---

## editor.session

`src/compiler/editor/session.lar` · 159 líneas · 9 funciones
editor.session: one analysis of a program, without generating C (larimar check, larimar lsp).
It links and analyzes like a compilation; the errors stay in linkErrors and analysisErrors (with the
line numbers that also say the file), and the analyzed program stays in `program` for the questions
of the editor (ide.lar).

`public function analyzeFile(main: String, shownFrom: String): bool`  
Links and analyzes a main file (pipeline.analysisPasses). true: no errors. Messages name files relative to `shownFrom`.  
<sub>línea 29</sub>

`public function compilationOf(main: String, shownFrom: String): Compilation`  
A compilation of a main file, with this session's std and source root.  
<sub>línea 39</sub>

`public function stdDir(): String`  
Where std/ is: $LARIMAR_HOME/std, or next to the tool (bin/larimar -> std/).  
<sub>línea 44</sub>

`function stdIn(home: String): String?`  
The std of a folder: std/ of an installation, or src/std of the repository.  
<sub>línea 58</sub>

### class `Diagnostic`
An error of the analysis, with its file and line.

`public function diagnostics(): Diagnostic[*]`  
The errors of the last analysis.  
<sub>línea 75</sub>

`function diagnostic(raw: String): Diagnostic`  
"Semantic Error [Line 1000012]: message" -> file 1, line 12.  
<sub>línea 84</sub>

`public function projectMain(file: String): String`  
The main file of the project a file belongs to (larimar.toml above it), or the file itself.  
<sub>línea 100</sub>

`function tomlMain(path: String): String`  
[project] main of a larimar.toml ("src/main.lar" when it does not say).  
<sub>línea 116</sub>

`public function checkCommand(rest: String[*]): int32`  
larimar check [file.lar | folder] [--json]: the errors of a program, without generating C. A folder means its larimar.toml. With --json, a list of { file, line, message, kind }. Exit code 1 when there are errors.  
<sub>línea 132</sub>
