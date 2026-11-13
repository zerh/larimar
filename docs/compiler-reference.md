# El compilador de Larimar: referencia de funciones

Cada módulo de `src/`, con su descripción y **todas** sus funciones, clases y métodos: la firma tal como está en el código y el comentario que la acompaña.

> Este archivo se **genera** a partir del código (`/** ... */` y `//` encima de cada declaración). No se edita a mano: si una descripción falta o está mal, se corrige el comentario en el código. Las descripciones están en inglés, como en el código. Una entrada sin texto es una función sin comentario.

Para la visión de conjunto (fases, datos que pasan de una a otra, recetas), ver la guía de mantenimiento. Aquí está el detalle.

**51 módulos, 1127 funciones y métodos** (578 con comentario, 549 sin él).

## Módulos

- [`src/main.lar`](#main) — 45 funciones
- [`src/syntax/ast.lar`](#syntax-ast) — 6 funciones
- [`src/syntax/lexer.lar`](#syntax-lexer) — 26 funciones
- [`src/syntax/parser.lar`](#syntax-parser) — 21 funciones
- [`src/syntax/parser/declarations.lar`](#syntax-parser-declarations) — 15 funciones
- [`src/syntax/parser/expressions.lar`](#syntax-parser-expressions) — 23 funciones
- [`src/syntax/parser/natives.lar`](#syntax-parser-natives) — 14 funciones
- [`src/syntax/parser/statements.lar`](#syntax-parser-statements) — 8 funciones
- [`src/syntax/parser/types.lar`](#syntax-parser-types) — 2 funciones
- [`src/semantics/analyzer.lar`](#semantics-analyzer) — 17 funciones
- [`src/semantics/analyzer/classes.lar`](#semantics-analyzer-classes) — 10 funciones
- [`src/semantics/analyzer/compact.lar`](#semantics-analyzer-compact) — 15 funciones
- [`src/semantics/analyzer/declarations.lar`](#semantics-analyzer-declarations) — 32 funciones
- [`src/semantics/analyzer/flow.lar`](#semantics-analyzer-flow) — 42 funciones
- [`src/semantics/analyzer/narrowing.lar`](#semantics-analyzer-narrowing) — 15 funciones
- [`src/semantics/analyzer/order.lar`](#semantics-analyzer-order) — 8 funciones
- [`src/semantics/analyzer/statements.lar`](#semantics-analyzer-statements) — 20 funciones
- [`src/semantics/analyzer/threads.lar`](#semantics-analyzer-threads) — 13 funciones
- [`src/semantics/expressions.lar`](#semantics-expressions) — 29 funciones
- [`src/semantics/expressions/calls.lar`](#semantics-expressions-calls) — 32 funciones
- [`src/semantics/expressions/constants.lar`](#semantics-expressions-constants) — 9 funciones
- [`src/semantics/expressions/conversions.lar`](#semantics-expressions-conversions) — 13 funciones
- [`src/semantics/expressions/literals.lar`](#semantics-expressions-literals) — 15 funciones
- [`src/semantics/expressions/operators.lar`](#semantics-expressions-operators) — 16 funciones
- [`src/semantics/expressions/switches.lar`](#semantics-expressions-switches) — 10 funciones
- [`src/semantics/linker.lar`](#semantics-linker) — 53 funciones
- [`src/semantics/types.lar`](#semantics-types) — 87 funciones
- [`src/codegen/debugmap.lar`](#codegen-debugmap) — 10 funciones
- [`src/codegen/expressions.lar`](#codegen-expressions) — 52 funciones
- [`src/codegen/expressions/calls.lar`](#codegen-expressions-calls) — 19 funciones
- [`src/codegen/expressions/clone.lar`](#codegen-expressions-clone) — 10 funciones
- [`src/codegen/expressions/lambdas.lar`](#codegen-expressions-lambdas) — 10 funciones
- [`src/codegen/expressions/operators.lar`](#codegen-expressions-operators) — 12 funciones
- [`src/codegen/expressions/patterns.lar`](#codegen-expressions-patterns) — 2 funciones
- [`src/codegen/expressions/strings.lar`](#codegen-expressions-strings) — 8 funciones
- [`src/codegen/gen.lar`](#codegen-gen) — 32 funciones
- [`src/codegen/gen/callbacks.lar`](#codegen-gen-callbacks) — 6 funciones
- [`src/codegen/gen/classes.lar`](#codegen-gen-classes) — 28 funciones
- [`src/codegen/gen/library.lar`](#codegen-gen-library) — 17 funciones
- [`src/codegen/gen/statements.lar`](#codegen-gen-statements) — 31 funciones
- [`src/codegen/gen/types.lar`](#codegen-gen-types) — 23 funciones
- [`src/codegen/prune.lar`](#codegen-prune) — 21 funciones
- [`src/project/cc.lar`](#project-cc) — 11 funciones
- [`src/project/libraries.lar`](#project-libraries) — 8 funciones
- [`src/project/lpk.lar`](#project-lpk) — 13 funciones
- [`src/project/testing.lar`](#project-testing) — 27 funciones
- [`src/editor/dap.lar`](#editor-dap) — 69 funciones
- [`src/editor/docstore.lar`](#editor-docstore) — 11 funciones
- [`src/editor/ide.lar`](#editor-ide) — 74 funciones
- [`src/editor/lsp.lar`](#editor-lsp) — 29 funciones
- [`src/editor/session.lar`](#editor-session) — 8 funciones

---

## main

`src/main.lar` · 1243 líneas · 45 funciones
larimar: the Larimar tool and compiler, written in Larimar (Larimar.java + Transpiler.java).

larimar new <name>              creates a project
larimar build [folder]          larimar.toml -> build/<name>.c -> executable (a library: build/<name>/)
larimar run [folder] [-- args]  builds, then runs the program
larimar build --debug           -g -O0 and #line to the .lar files (debuggers; also run, and file.lar -o)
larimar check [file|folder]     the errors, without generating C (--json for tools)
larimar test [file|folder]...   runs the tests (testing.lar)
larimar lsp                     the language server for editors (LSP on stdin/stdout)
larimar dap                     the debugger for editors (DAP on stdin/stdout, over lldb-dap)
larimar c <file.lar>            prints the C of a file (imports are looked up next to it)
larimar <file.lar> [-o out.c]   the same, written to a file (how the compiler is used by scripts)

`function main(args: String[]): int32`
<sub>línea 50</sub>

`function debugMapPath(cFile: String): String`  
build/demo.c -> build/demo.debug.json: what larimar dap needs to show the program as Larimar.  
<sub>línea 68</sub>

`function fail(msg: String in default): int32`
<sub>línea 82</sub>

`function command(args: String[]): int32`  
The options of larimar itself, taken out of the arguments; what follows `--` is the program's.  
<sub>línea 88</sub>

`function newProject(rest: String[*]): int32`  
larimar new <name> [--library]  
<sub>línea 136</sub>

`function buildProject(run: bool, rest: String[*], programArgs: String[*]): int32`  
larimar build [folder], larimar run [folder] [-- args]  
<sub>línea 145</sub>

`function test(rest: String[*]): int32`  
larimar test [file|folder]...  
<sub>línea 160</sub>

`function file(main: String, rest: String[*], programArgs: String[*]): int32`  
larimar file.lar -o out.c: its C; larimar file.lar [args]: build it and run it  
<sub>línea 166</sub>

`function writeC(main: String, output: String): int32`  
The C of a file, into `output` ("": printed).  
<sub>línea 179</sub>

`function plugin(cmd: String, args: String[]): int32`  
A command that is not larimar's: a plugin's, or an error.  
<sub>línea 197</sub>

`function version(): int32`
<sub>línea 207</sub>

`function usage(): int32`
<sub>línea 212</sub>

### class `Plugin`
A command of a plugin: `larimar <command> x` runs `bin/<program> <args> x`.

`function larimarHome(): String`  
$LARIMAR_HOME: the folder of bin/, std/ and plugins/.  
<sub>línea 265</sub>

`function plugins(problems: String[*]): Plugin[*]`  
The commands that plugins declare, one file each in $LARIMAR_HOME/plugins: [plugin] name = "mytool" program = "mytool"             # a program of $LARIMAR_HOME/bin, nowhere else version = "1.0.0" [commands] hello = ["hello"]              # larimar hello x  ->  bin/mytool hello x A plugin cannot take a command of larimar itself, and two plugins cannot take the same one: both are problems (and that command is not taken).  
<sub>línea 281</sub>

`function runPlugin(pl: Plugin, args: String[]): int32`  
Runs the program of a plugin with its arguments and the user's, on this console; its exit code is larimar's.  
<sub>línea 328</sub>

`function compileFile(main: String, shownFrom: String): String`  
The C of a main file; `import a.b` reads a/b.lar next to it. Messages name files relative to `shownFrom`.  
<sub>línea 355</sub>

`function testCompiler(wanted: String): CCompiler?`  
The C compiler for the tests (a test file that uses TLS needs the system's: compileC says so).  
<sub>línea 374</sub>

`function testSettings(): TestSettings?`  
The project's [c] settings for the tests, or the defaults when there is no larimar.toml here.  
<sub>línea 382</sub>

`function testMain(rest: String[*]): int32`  
larimarc test-main <file.lar> -o <out.c> [--root <folder>]: the C of a file of test functions with a main added (testing.lar). Next to out.c it writes the file with its main (.lar) and the tests' names (.tests, one per line).  
<sub>línea 418</sub>

### class `Project`

`function load(dir: String): Project?`
<sub>línea 490</sub>

`function keysOf(section: String): String`
<sub>línea 512</sub>

`function allowedKey(section: String, key: String): bool`
<sub>línea 516</sub>

`function oldKey(key: String, where: String): String`  
libraries and library_paths of before 1.3: a library is now static or dynamic by the key that names it.  
<sub>línea 521</sub>

`function project(dir: String, config: Any): Project?`
<sub>línea 528</sub>

`function cIdentifier(name: String): bool`  
A name of C (and of a module): letters, digits and '_', not starting with a digit.  
<sub>línea 626</sub>

`function isPlatform(name: String): bool`  
The platforms: of [c.<platform>] and of --target.  
<sub>línea 635</sub>

`function hasNames(value: Any): bool`  
Whether a table has entries with a name (a section does; a list does not).  
<sub>línea 641</sub>

`function isSection(value: Any): bool`
<sub>línea 646</sub>

`function text(section: Any, key: String, def: String): String`
<sub>línea 653</sub>

`function list(section: Any, key: String, def: String[*]): String[*]`
<sub>línea 662</sub>

`function validName(name: String): bool`
<sub>línea 685</sub>

`function resolve(dir: String, p: String): String`  
A path of the project: relative to its folder, or absolute.  
<sub>línea 698</sub>

`function build(p: Project, debug: bool): String`  
Builds the project; returns the executable, or "" on failure.  
<sub>línea 701</sub>

`function linkArgs(p: Project, bundled: bool): String[*]`  
How a program links its libraries. A static one (static_libraries) is the file lib<name>.a of static_library_paths, given to the linker by its path, so it goes inside the executable even when a dynamic one is next to it (on Linux, one of the system's: -Wl,-Bstatic). A dynamic one (dynamic_libraries) is -l<name> with -L for each of dynamic_library_paths, and the executable looks for it in those folders when it runs (Linux and macOS: rpath; on Windows, next to the .exe or in the PATH). A package of [packages] adds what its C needs.  
<sub>línea 774</sub>

`function packageArgs(p: Project): String[*]`  
What the libraries of [packages] add to a C command: their folder (the .h their .lar includes), and of a package its C.  
<sub>línea 812</sub>

`function buildLibrary(p: Project, debug: bool): bool`  
larimar build of a library: build/<name>/ gets lib<name>.a (or the dynamic one), <name>.h for C, <name>.lar for Larimar and <name>.interface with the hash of the .lar, which the library also has inside. Everything of the C but the export functions (and what the library gives with them) is static, so two libraries and the program that links them do not clash; each one has its own runtime.  
<sub>línea 828</sub>

`function buildPackage(p: Project, c: String, header: String, module: String, hash: String, cc: CCompiler): bool`  
larimar build of a library as a package (the default): build/<name>/ gets <name>.c, the library in C, with its .h, .lar and .interface, and in c/ the C the library brings (the sources and include_paths of its [c], those of every platform). Nothing is compiled into it: the program that names the folder in [packages] compiles it with its own C, so one folder serves every platform. Its C is compiled once here, to find its errors now.  
<sub>línea 961</sub>

`function quotedList(items: String[*]): String`
<sub>línea 1060</sub>

`function packaged(dir: String, path: String, outDir: String, folder: bool): bool`  
Copies a file (or a folder, whole) of the library's project into c/ of its package, at the same path.  
<sub>línea 1067</sub>

`function copyFolder(from: String, to: String): void throws IoError`
<sub>línea 1088</sub>

`function runC(cmd: String[*], program: String, dir: String, cFile: String): bool`  
Runs the C compiler; false (and toolError) when it fails.  
<sub>línea 1101</sub>

`function runScript(file: String, args: String[*]): int32`  
larimar file.lar [args]: the file is built in a folder of the system's temporary files (the bundled tcc first: it starts fast) and run with the arguments; its exit code is larimar's. Nothing is printed but what the program prints, so scripts can be piped.  
<sub>línea 1119</sub>

`function execute(exe: String, args: String[*]): int32`
<sub>línea 1161</sub>

`function create(path: String, library: bool): int32`
<sub>línea 1171</sub>

`function createLibrary(path: String, name: String): int32`  
larimar new <name> --library: a library with one export function and a test of it.  
<sub>línea 1204</sub>

---

## syntax.ast

`src/syntax/ast.lar` · 553 líneas · 6 funciones
syntax.ast: the syntax tree (Ast.java). One class per kind of node; the analyzer writes what it
finds into the fields of Node, and the generator reads them from there.

### class `Node`

### class `Expr extends Node`

### class `Stmt extends Node`

### enum `TK`

### class `TypeRef extends Node`

`public function typeNamed(name: String in default, line: int32): TypeRef`
<sub>línea 71</sub>

### class `Program extends Node`

### class `ImportDecl extends Node`
import a.b;  import a.b as x;  import a.b { n1, n2 };

### class `CIncludeDecl extends Node`
platform: "" (every one), "windows", "macos", "linux" or "unix": that of the class it is in (the analyzer sets it).

### class `CCodeDecl extends Node`

### class `ExternTypeDecl extends Node`
native type X;  = T*;  = c"C TYPE";  = (A, B) -> R  (a C function pointer);  ... released by f;

### class `ExternFunctionDecl extends Node`
cName: the C function called (it stays when a module renames the declaration); prototype: no cinclude. A method of a native type (`native function m() = c_m;`) becomes one of these, with self first.

### class `ExternValueDecl extends Node`
native const NAME: T [= c_name | = "C"];  native let NAME: T [= c_name];  a C constant (or macro) or a C global variable.

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
<sub>línea 221</sub>

`public function isTypeDecl(d: Node): bool`
<sub>línea 238</sub>

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
<sub>línea 438</sub>

`public function allExprs(body: Stmt[*] in out, lambdas: bool, out: Expr[*]): void`  
Every expression of a body (into lambda bodies when `lambdas`).  
<sub>línea 462</sub>

`public function exprAll(e: Expr? in out, lambdas: bool, out: Expr[*]): void`
<sub>línea 499</sub>

---

## syntax.lexer

`src/syntax/lexer.lar` · 630 líneas · 26 funciones
syntax.lexer: source text -> tokens (Lexer.java).

String literals keep their raw text (escapes and ${...} included); the parser splits
them and lexes each ${...} again with a Lexer of its own.

### enum `TT`

### class `Token`

### class `Lexer`
Reads a source text into tokens: Lexer { src, line }, run(), then its toks. `line` is the encoded line of its first byte (file * 1000000 + line). An error stops it: `error` says why ("" when there is none).

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

- `function add(kind: TT, text: String in self, length: int32): void`
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

`function keyword(w: String): TT`
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

`src/syntax/parser.lar` · 202 líneas · 21 funciones
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

### class `Parser`
The tokens of a source text, read one by one.

- `function error(line: int32, message: String): void`
  <sub>línea 44</sub>

- `function hasFailed(): bool`
  <sub>línea 48</sub>

- `function current(): Token`  
  The token to read next.  
  <sub>línea 51</sub>

- `function next(): Token`  
  The token after the current one.  
  <sub>línea 56</sub>

- `function previous(): Token`  
  The token just read.  
  <sub>línea 62</sub>

- `function atEnd(): bool`
  <sub>línea 64</sub>

- `function at(kind: TT): bool`  
  Is the current token of this kind?  
  <sub>línea 67</sub>

- `function atWord(word: String): bool`  
  Is the current token the identifier `word` (a word with a meaning only there: test, export, type...)?  
  <sub>línea 70</sub>

- `function atWords(first: String, second: String): bool`  
  Are the next two tokens the identifiers `first` and `second` (wait until, thread safe)?  
  <sub>línea 73</sub>

- `function advance(): Token`  
  Reads the current token and gives it.  
  <sub>línea 78</sub>

- `function optional(kind: TT): bool`  
  [ kind ]: reads the token when it is of this kind, and says whether it was.  
  <sub>línea 84</sub>

- `function optionalWords(first: String, second: String): bool`  
  [ first second ]: reads the two words when they come, and says whether they did.  
  <sub>línea 91</sub>

- `function expect(kind: TT, message: String): Token`  
  kind: reads the token, which must be of this kind (else the error says what came instead).  
  <sub>línea 99</sub>

`public function endedBySemicolon(p: Parser in default, node: Node, what: String): Node`  
The node, after its ';'.  
<sub>línea 109</sub>

`public function qualifiedName(p: Parser in default, message: String): String`  
NAME ( . NAME )*  
<sub>línea 115</sub>

`public function strictList(p: Parser in default, close: TT, readItem: () -> void): void`  
[ item ( , item )* ] before `close` (which is not read).  
<sub>línea 125</sub>

`public function looseList(p: Parser in default, close: TT, readItem: () -> void): void`  
Like strictList, but a comma may also end the list.  
<sub>línea 134</sub>

`public function lives(p: Parser in default): String`  
in ( default | self | NAME ): where a parameter or a result lives.  
<sub>línea 142</sub>

`function program(p: Parser in default, startLine: int32): Program`  
import* ( [public] declaration )*  
<sub>línea 149</sub>

`function importDeclaration(p: Parser in default): ImportDecl`  
import NAME ( . NAME )* [ as NAME | { NAME ( , NAME )* } ] ;  
<sub>línea 182</sub>

---

## syntax.parser.declarations

`src/syntax/parser/declarations.lar` · 367 líneas · 15 funciones
syntax.parser.declarations: what a file declares (functions, structs, classes, interfaces, enums, constants).
Each function reads one construction; the comment above it shows its form (the notation is in syntax.parser).

`public function topLevelDeclaration(p: Parser in default): Node`  
ccode { C } | ccode "FILE" ; | cinclude "HEADER" ; | native ... | test function ... | export function ... | const ... | let ... | function ... | struct ... | [synchronized] class ... | interface ... | enum ... | native type ...  
<sub>línea 20</sub>

`function testFunction(p: Parser in default): FunctionDecl`  
(after `test`) function NAME ( [ NAME : Type ] ) : void block  
<sub>línea 70</sub>

`function constant(p: Parser in default): Node`  
(after `const`) NAME : Type = expression ;  
<sub>línea 86</sub>

`public function parameter(p: Parser in default, typeRequired: bool): Param`  
NAME : Type [ in lives ]      (in a lambda: NAME [ : Type ])  
<sub>línea 95</sub>

`public function parameters(p: Parser in default): Param[*]`  
( [ parameter ( , parameter )* ] )  
<sub>línea 109</sub>

`public function functionDeclaration(p: Parser in default, isOverride: bool, withBody: bool): FunctionDecl`
<sub>línea 117</sub>

`function operatorDeclaration(p: Parser in default): FunctionDecl`  
operator ( + | - | * | / | % | == | < ) parameters : Type block  
<sub>línea 162</sub>

`function structDeclaration(p: Parser in default): StructDecl`  
(after `struct`) NAME { ( field | static ... | function ... | operator ... )* }  
<sub>línea 176</sub>

`function classDeclaration(p: Parser in default, isSynchronized: bool): ClassDecl`  
(after `class`) NAME [ extends NAME ] [ implements NAME ( , NAME )* ] { ( field | static ... | [override] function ... | native function ... | native let ... | operator ... )* }  
<sub>línea 204</sub>

`public function cBodied(p: Parser in default, declaration: FunctionDecl in default): void`  
native function f(params): T { C } (a method, a static function): the body is C. It becomes a C function the compiler writes (its parameters with their C types and names), and f calls it. In a class for one system (it implements UnixPlatform...), f calls it only there (elsewhere it panics; the C of that system reaches no other).  
<sub>línea 267</sub>

`function method(p: Parser in default, ofSynchronizedClass: bool, isOverride: bool): FunctionDecl`  
A method of a class: in a synchronized class it may say `wait until`.  
<sub>línea 286</sub>

`function interfaceDeclaration(p: Parser in default): InterfaceDecl`  
(after `interface`) NAME [ extends NAME ( , NAME )* ] { ( function NAME parameters [ : Type ] ... ; | static function ... )* }  
<sub>línea 294</sub>

`public function staticFunction(p: Parser in default, owner: String in default): void`  
(after `static`, inside the type `owner`) function ... | native function ... = C ;  
<sub>línea 319</sub>

`function enumDeclaration(p: Parser in default): EnumDecl`  
(after `enum`) NAME { [ variant ( , variant )* [ , ] ] }      variant: NAME [ parameters ]  
<sub>línea 339</sub>

`public function field(p: Parser in default): FieldDecl`  
let NAME : Type [ = expression ] ;  
<sub>línea 358</sub>

---

## syntax.parser.expressions

`src/syntax/parser/expressions.lar` · 443 líneas · 23 funciones
syntax.parser.expressions: expressions, from the lowest precedence to the highest.
Each function reads one construction; the comment above it shows its form (the notation is in syntax.parser).

`public function expression(p: Parser in default): Expr`  
ternary [ in ( heap | default | byte[N] | expression ) ]: where a created value lives  
<sub>línea 17</sub>

`function ternary(p: Parser in default): Expr`  
coalesce [ ? ternary : ternary ]      (right to left)  
<sub>línea 30</sub>

`public function coalesce(p: Parser in default): Expr`  
binary operators [ ?? coalesce ]  
<sub>línea 40</sub>

`public function level(kind: TT): int32`  
The level of a binary operator, from the loosest (1) to the tightest; 0: not one. ||   &&   == != < <= > >= (and `is`)   |   ^   &   << >>   + -   * / %  
<sub>línea 51</sub>

`function binaryFrom(p: Parser in default, minimum: int32): Expr`  
cast ( OPERATOR cast ... | is qualified NAME [ NAME ] )*: the operators of level `minimum` or tighter, each one left-associative (precedence climbing: the right side takes only tighter operators).  
<sub>línea 70</sub>

`function cast(p: Parser in default): Expr`  
unary ( as Type )*  
<sub>línea 89</sub>

`function unary(p: Parser in default): Expr`  
( - | ! | ~ | & ) unary | postfix  
<sub>línea 103</sub>

`function postfix(p: Parser in default): Expr`  
primary ( ( arguments ) | . NAME | . NAME { fields } | [ expression ] | ! )*  
<sub>línea 110</sub>

`function methodReference(p: Parser in default, target: Expr in default): Expr`  
Module::function, variable::method, self::method: a lambda that calls it with its own parameters. The parameters come from the function type expected there (the analyzer adds them).  
<sub>línea 145</sub>

`function referenceLambda(callee: Expr in default): Lambda`  
The lambda of a reference: its body calls `callee` (the analyzer adds the parameters).  
<sub>línea 154</sub>

`function primary(p: Parser in default): Expr`  
NUMBER | "TEXT" | true | false | null | self | super . NAME | { fields } | [ expressions ] | switch ... | NAME [ { fields } ] | lambda | ( expression )  
<sub>línea 163</sub>

`function objectLiteral(p: Parser in default, typeName: String in default, line: int32): ObjectLit`  
{ [ field ( , field )* [ , ] ] }      field: NAME : expression | NAME | expression  
<sub>línea 210</sub>

`function lambdaAhead(p: Parser in default): bool`  
Is a lambda next: ( ... ) followed by -> ?  
<sub>línea 231</sub>

`function lambda(p: Parser in default): Lambda`  
( [ parameter ( , parameter )* ] ) -> block  
<sub>línea 250</sub>

`public function switchExpression(p: Parser in default, line: int32): SwitchExpr`  
(after `switch`) ( expression ) { case* } case: ( case pattern ( , pattern )* | default ) [ when expression ] -> ( block | throw expression ; | expression ; )  
<sub>línea 263</sub>

`function pattern(p: Parser in default): Pattern`  
null | constant | qualified NAME [ NAME ] | qualified NAME { [ NAME [ : NAME ] ( , ... )* ] } [ NAME ] (a value, a type with its binding, or an enum variant with its fields)  
<sub>línea 306</sub>

`function string(p: Parser in default, token: Token in default): StringLit`  
"Hello ${name}": the texts, and the parsed expressions between them.  
<sub>línea 334</sub>

`function interpolation(p: Parser in default, inner: String in default, line: int32): Expr`  
The expression inside ${...}: its own tokens, read with this parser, then back to the string's.  
<sub>línea 370</sub>

`function binary(operatorText: String in default, left: Expr in default, right: Expr in default, line: int32): Expr`
<sub>línea 383</sub>

`public function waitFirst(line: int32, condition: Expr in default, body: Stmt[*] in default): Stmt[*]`  
wait until (cond): the body starts with `while (!(cond)) { self.__wait(); }`. The lock is held when the body starts; __wait (a name no program can write) lets it go while waiting, and every method of the object that ends wakes the waiters to look at their condition again.  
<sub>línea 392</sub>

`public function optionalFollows(next: TT): bool`  
After `as T`, a '?' makes T optional only when what follows can come after a type (x as int64? ?? 0, (x as T?), x as T?;). Followed by the start of an expression it is a ternary: x as int64 ? a : b.  
<sub>línea 404</sub>

`function dottedPath(value: Expr): String`  
a, a.b, a.b.c (only names), or "".  
<sub>línea 412</sub>

`function interpolationEnd(raw: String, open: int32): int32`  
Where the ${ that starts at `open` (the '{') closes: its '}' (strings inside are skipped).  
<sub>línea 422</sub>

---

## syntax.parser.natives

`src/syntax/parser/natives.lar` · 401 líneas · 14 funciones
syntax.parser.natives: what comes from C (native functions, types, structs and values; cinclude and ccode).
Each function reads one construction; the comment above it shows its form (the notation is in syntax.parser).

`public function nativeDeclaration(p: Parser in default, line: int32): Node`  
(after `native`) function NAME ( [ parameter ( , parameter )* [ , ... ] ] ) [ : Type ] [ = C ] [ released by NAME ] ;  a C function const NAME : Type [ = C ] ;      let NAME : Type [ = NAME ] ;                        a C constant, macro or global struct NAME [ = C ] { ( let NAME : Type [ = NAME ] ; | function ... | static ... )* }  a C struct, by value type NAME [ = CTYPE | = ( Type, ... ) -> Type ] [ released by NAME ] ( ; | { member* } )   a C type type NAME { ... }                                                                   (std) a type the compiler knows  
<sub>línea 22</sub>

`function atCText(p: Parser in default): bool`  
At C text: c"...".  
<sub>línea 37</sub>

`function cTarget(p: Parser in default, what: String): String`  
[ = NAME | = struct NAME | = c"C" ]: what a native declaration is in C; "" without '='.  
<sub>línea 40</sub>

`function nativeFunctionOfC(p: Parser in default): ExternFunctionDecl`  
(after `native function`) NAME ( [ parameter ( , parameter )* [ , ... ] ] ) [ : Type ] [ = C ] [ released by NAME ] ;  
<sub>línea 54</sub>

`function nativeValue(p: Parser in default): Node`  
(after `native`) ( const NAME : Type [ = C ] | let NAME : Type [ = NAME ] ) ;  
<sub>línea 92</sub>

`function nativeStruct(p: Parser in default): StructDecl`  
(after `native struct`) NAME [ = C ] { ( let NAME : Type [ = NAME ] ; | function ... | static ... )* }  
<sub>línea 111</sub>

`function cField(p: Parser in default): FieldDecl`  
let NAME : Type [ = NAME ] ;      a field of a C struct (after '=': its name in C)  
<sub>línea 134</sub>

`function nativeCType(p: Parser in default, name: Token in default): Node`  
(after `native type NAME`) [ = CTYPE | = ( Type, ... ) -> Type ] [ released by NAME ] ( ; | { member* } ) CTYPE: [ struct ] NAME *...  or c"C TYPE";  without '=' it is opaque (void*)  
<sub>línea 150</sub>

`function nativeMembers(p: Parser in default, declaration: ExternTypeDecl in default): void`  
{ ( let NAME : Type [ = NAME ] ; | native function ... | native let ... | function ... | static ... )* } The members of a C type: its fields (when it is a pointer to a C struct), functions of C that take it first (self), and functions written in Larimar.  
<sub>línea 187</sub>

`function nativeMember(p: Parser in default, owner: String in default, line: int32, property: bool, isStatic: bool): FunctionDecl`  
(after `native function` or `native let`, in a native type) NAME parameters [ : Type ] [ in lives ] [ throws Type ] = ( C | expression ) ;      (let: NAME : Type = ...) With `= C` (a name, or "C text"), the method calls that C function with self first: before it only the memory of the call, when the first parameter is one (m: byte[*]). Any other expression is Larimar.  
<sub>línea 240</sub>

`function nativeType(p: Parser in default, line: int32, name: Token in default): NativeTypeDecl`  
(after `native type NAME`) { ( static ... | native function ... | native let ... | native operator ... | function ... )* } The methods of a type the compiler knows (String, Any): only in the standard library.  
<sub>línea 316</sub>

`public function nativeFunction(p: Parser in default, line: int32): FunctionDecl`  
(after `native function`) NAME parameters [ : Type ] [ in lives ] [ throws Type ] [ = expression ] ;  
<sub>línea 344</sub>

`public function nativeProperty(p: Parser in default, line: int32): FunctionDecl`  
(after `native let`) NAME : Type [ = expression ] ; A value read without parentheses and never assigned (s.length). Without `= expression` the compiler gives it; with it, it is that expression.  
<sub>línea 374</sub>

`function nativeOperator(p: Parser in default, line: int32): FunctionDecl`  
(after `native operator`) ( [ ] | SYMBOL ) parameters : Type ;  
<sub>línea 387</sub>

---

## syntax.parser.statements

`src/syntax/parser/statements.lar` · 172 líneas · 8 funciones
syntax.parser.statements: statements and blocks.
Each function reads one construction; the comment above it shows its form (the notation is in syntax.parser).

`public function variable(p: Parser in default): VarDecl`  
let NAME : Type [ = expression ] ;  
<sub>línea 14</sub>

`public function block(p: Parser in default, what: String): Stmt[*]`  
{ statement* }  
<sub>línea 25</sub>

`function statement(p: Parser in default): Stmt`  
let ... | return [ expression ] ; | if ... | while ( expression ) block | for ... | break ; | continue ; | throw expression ; | yield expression ; | try ... | block | switch ... | assignment or call  
<sub>línea 37</sub>

`function assignmentOrCall(p: Parser in default, line: int32): Stmt`  
expression [ ( = | += | -= | ... ) expression ] ;      (a += b is a = a + b)  
<sub>línea 99</sub>

`function misplaced(p: Parser in default, token: Token, message: String): Stmt`  
Something that does not go here: the error, and an empty statement.  
<sub>línea 117</sub>

`function ifStatement(p: Parser in default, line: int32): IfStmt`  
(after `if`) ( expression ) block [ else ( if ... | block ) ]  
<sub>línea 123</sub>

`function forStatement(p: Parser in default, line: int32): ForStmt`  
(after `for`) ( [ NAME , ] NAME in expression [ .. expression ] ) block  
<sub>línea 140</sub>

`function tryStatement(p: Parser in default, line: int32): TryStmt`  
(after `try`) block ( catch ( qualified NAME NAME ) block )+  
<sub>línea 159</sub>

---

## syntax.parser.types

`src/syntax/parser/types.lar` · 73 líneas · 2 funciones
syntax.parser.types: types as they are written (int32, String?, T[*], (A) -> R thread safe).
Each function reads one construction; the comment above it shows its form (the notation is in syntax.parser).

`public function type(p: Parser in default): TypeRef`  
( qualified NAME | ( Type ) | ( [ Type ( , Type )* ] ) -> Type ) suffix* suffix: [ ] | [ * ] | [ expression ] | ? | *          and after a function type: [ thread safe ]  
<sub>línea 13</sub>

`function threadSafe(p: Parser in default, functionType: TypeRef in default): TypeRef`  
[ thread safe ] after a function type: other threads may call it at the same time. Two words, like `wait until`; neither is reserved. With function types inside function types it goes to the nearest one on its left; parentheses choose another: ((A) -> (B) -> C) thread safe.  
<sub>línea 63</sub>

---

## semantics.analyzer

`src/semantics/analyzer.lar` · 325 líneas · 17 funciones
semantics.analyzer: semantic analysis (Analyzer.java), part 1: declarations, statements, regions
and the final passes. Expressions are in checkexpr.lar.

- Types: declarations, expressions with expected types, implicit conversions.
- Regions: every value that references memory carries the region of that memory;
storing it somewhere that outlives the region is an error (fix: .clone()).
- Captures: a lambda captures by value; captured variables cannot change.
- Errors: throws/try/catch are checked; every throwing call is handled.
- Switch: patterns resolved, enums covered completely.

### class `Diag`

`public function error(line: int32, msg: String): void`
<sub>línea 38</sub>

`public function wrong(line: int32, msg: String): Type`  
Reports an error where a type is expected: the result is the error type.  
<sub>línea 43</sub>

`public function bindingSymbol(name: String in default, type: Type in default, line: int32, region: Region in default): Symbol`  
A symbol for the name after `is`, declared later where the test is true (see narrow).  
<sub>línea 49</sub>

### class `HandledSet`

### class `FrameState`

### enum `MutK`

### class `Mutation`

### enum `DefK`

### class `Deferred`

### class `ThreadRun`

`public function frame(): Frame`
<sub>línea 122</sub>

`public function state(): FrameState`
<sub>línea 123</sub>

`public function analyze(program: Program in default): void`
<sub>línea 132</sub>

`public function pushFrame(kind: FrameK, ret: Type? in default, throwsType: Type? in default, lambda: LambdaInfo? in default, selfType: Type? in default, parent: Scope in default, owner: Owner? in default): Frame`
<sub>línea 208</sub>

`public function popFrame(restore: Scope in default): void`
<sub>línea 222</sub>

`public function pushScope(): void`
<sub>línea 228</sub>

`public function popScope(): void`
<sub>línea 230</sub>

`public function block(): Scope`  
The block the current statement is in (names are declared there, not in the statement).  
<sub>línea 233</sub>

`public function declare(name: String in default, kind: SymK, type: Type in default, line: int32): Symbol`
<sub>línea 235</sub>

`public function lookup(name: String): Symbol?`
<sub>línea 256</sub>

`public function narrowedType(s: Symbol): Type?`
<sub>línea 266</sub>

`public function noteCapture(s: Symbol in default, line: int32): void`  
Records that the current lambda (and every lambda in between) captures `s`.  
<sub>línea 279</sub>

`function checkMutations(): void`
<sub>línea 307</sub>

`function checkMemoryUses(): void`
<sub>línea 320</sub>

---

## semantics.analyzer.classes

`src/semantics/analyzer/classes.lar` · 241 líneas · 10 funciones
semantics.analyzer.classes: classes and interfaces: fields, methods, what a class inherits and what it implements.

`public function validateClasses(): void`
<sub>línea 14</sub>

`function processClass(c: ClassInfo in default, done: Any): void`
<sub>línea 65</sub>

`function sameLives(a: Param[*], b: Param[*]): bool`
<sub>línea 129</sub>

`function sameThrows(a: Type?, b: Type?): bool`
<sub>línea 137</sub>

`function throwsText(t: Type?): String`
<sub>línea 139</sub>

`function checkSameSig(c: ClassInfo, m: MethodInfo, pm: MethodInfo, line: int32): void`
<sub>línea 141</sub>

`public function validateInterfaces(): void`
<sub>línea 153</sub>

`public function checkFieldDefaults(): void`
<sub>línea 181</sub>

`function isConstantExpr(e: Expr): bool`
<sub>línea 200</sub>

`public function checkMain(): void`
<sub>línea 227</sub>

---

## semantics.analyzer.compact

`src/semantics/analyzer/compact.lar` · 352 líneas · 15 funciones
semantics.analyzer.compact: Memory.compact: where a memory may be compacted.

### class `CompactCall`
A call to Memory.compact(m): its memory, and the variables that could be seen where it is.

### class `Mixing`
Where data of another memory of the same block was stored in a memory with a name.

`public function noteCompact(c: Call in default, m: Symbol in default): void`  
Memory.compact(m) here: m must belong to this function, and the call cannot be inside a for over data.  
<sub>línea 37</sub>

`function checkCompacts(): void`  
Once every variable's memory is known: the variables of the compacted memory move with it; any other variable of its block (or of a block inside it) that may point into it would be left pointing to freed memory, so it is an error. So is data of another memory of the block stored in it.  
<sub>línea 61</sub>

`function notMovable(t: Type in default, seen: Any in default): String`  
What a value of this type may hold that compact() cannot move ("" when nothing): "a lambda", "a thread"...  
<sub>línea 101</sub>

`public function resolveRegions(): void`
<sub>línea 144</sub>

`public function objectOf(e: Expr): Expr?`  
The object of a field or element access: a.b and a[i] give a.  
<sub>línea 165</sub>

`public function throughReference(target: Expr): bool`  
Is the target reached through a class object or list (shared, not a captured copy)?  
<sub>línea 172</sub>

`public function isReference(t: Type): bool`
<sub>línea 181</sub>

`public function storageRegion(obj: Expr in default): Region`  
Where the fields or elements of `obj` are stored.  
<sub>línea 186</sub>

`public function placeFor(obj: Expr in default): Place`  
The memory new data should go to when stored inside `obj`.  
<sub>línea 198</sub>

`public function rootSymbol(e: Expr in default): Symbol?`
<sub>línea 206</sub>

`public function isLValue(e: Expr): bool`
<sub>línea 215</sub>

`public function analyzeReturn(r: ReturnStmt in default): void`
<sub>línea 222</sub>

`function analyzeWhen(i: IfStmt in default): void`  
An if for platforms (IfStmt.platform): a ... b ... else. Every branch is checked, each for its platform, in the block around (there is no block of its own). A name every branch declares, with the same type, stays for the code after it (one C name for all of them); what only some declare belongs to its branch.  
<sub>línea 254</sub>

`function whenBranch(body: Stmt[*] in default, platform: String in default, branch: int32, syms: int32[*] in default, branchOf: int32[*] in default, blk: Scope in default): void`  
One branch of an if for platforms, checked for `platform`; what it declares is hidden until every branch is seen.  
<sub>línea 313</sub>

`public function analyzeIf(i: IfStmt in default): void`
<sub>línea 333</sub>

---

## semantics.analyzer.declarations

`src/semantics/analyzer/declarations.lar` · 816 líneas · 32 funciones
semantics.analyzer.declarations: what a program declares: the system of each class, C declarations, constants and signatures.

`function requireAscii(name: String, line: int32, what: String): void`
<sub>línea 24</sub>

`function interfaceDecl(name: String): InterfaceDecl?`
<sub>línea 34</sub>

`function classDecl(name: String): ClassDecl?`
<sub>línea 39</sub>

`function withAncestors(names: String[] in default, line: int32): String[*]`  
The interfaces given, with every one they extend, each once (in the order found).  
<sub>línea 45</sub>

`function platformOfClass(name: String, line: int32): String`  
"linux", "macos", "windows", "unix" or "" (every system), from the interfaces of the class and its superclasses.  
<sub>línea 64</sub>

`function narrower(a: String, b: String, owner: String, line: int32): String`  
Of two systems, the narrower one (linux within unix); two that do not overlap are an error.  
<sub>línea 86</sub>

`function assignPlatforms(program: Program in default): void`  
The C of a class for one platform goes only there: its cinclude, its ccode and the C functions of its methods get that platform, and each method with a C body calls its function only there (elsewhere it panics). With --target nothing is left to the C compiler: the C of the target's classes is plain C, and that of the others is not generated.  
<sub>línea 101</sub>

`function platformNumber(platform: String): int32`  
The number std.os gives each platform (its platformNumber).  
<sub>línea 136</sub>

`function onlyOn(c: ClassDecl in default, system: String in default): void`  
The methods with a C body of a class for one platform: they call their C only there; elsewhere they panic.  
<sub>línea 146</sub>

`public function collect(program: Program in default): void`
<sub>línea 165</sub>

`function typeNameTaken(name: String, line: int32): bool`
<sub>línea 278</sub>

`function collectStatic(f: FunctionDecl in default): void`  
Type.name: a function that belongs to a type, without self.  
<sub>línea 291</sub>

`function externSignature(e: ExternTypeInfo in default): void`  
extern type X = (A, B) -> R: the signature C functions of that type have.  
<sub>línea 307</sub>

`function exportCName(f: FunctionDecl in default): String`  
The C name of an export function: = c_name, else its name (in a library, <prefix>_<name>).  
<sub>línea 351</sub>

`function exportable(t: Type): bool`  
What an export function can take: what C can pass, a String? (NULL is null), and in a library its classes.  
<sub>línea 358</sub>

`public function libraryCallback(t: Type): bool`  
A function of the program that a library takes: a function type of numbers, bool, String and the library's classes, that gives a number, a bool, a String or nothing. C gives it as a function and a void* (the program's own data, given back to the function on each call).  
<sub>línea 370</sub>

`function checkExport(f: FunctionInfo in default, fd: FunctionDecl in default): void`  
export function: C calls it by its name, with C types.  
<sub>línea 379</sub>

`function instanceMethodNamed(t: String in default, name: String): bool`  
An instance method `name` of the type `t` (to reject a static function with the same name).  
<sub>línea 412</sub>

`function functionNameTaken(name: String, line: int32): bool`
<sub>línea 422</sub>

`public function constants(program: Program in default): void`
<sub>línea 437</sub>

`public function constIntText(v: ConstVal): String`
<sub>línea 469</sub>

`public function signatures(program: Program in default): void`
<sub>línea 476</sub>

`public function externValue(v: ExternValueDecl in default): void`  
extern const NAME: T;  extern let NAME: T;  a name C has (a constant, a macro, a global).  
<sub>línea 668</sub>

`function externResource(e: ExternTypeInfo in default): void`  
released by f: f takes exactly one X and returns nothing useful; only release() calls it.  
<sub>línea 686</sub>

`function textReleaser(f: FunctionInfo in default): void`  
...: String = c_f released by r: r is a native function that takes the text (one String); only the compiler calls it.  
<sub>línea 709</sub>

`function externResourceRules(f: FunctionInfo in default): void`  
A C function that makes a resource returns X? (C fails: null). A resource goes to C as X, not X?.  
<sub>línea 731</sub>

`function resolveMethodSig(mi: MethodInfo in default, m: FunctionDecl in default): void`
<sub>línea 743</sub>

`function resolveSig(params: Param[*] in default, ret: TypeRef in default): Type`
<sub>línea 764</sub>

`function isPlainNumber(t: Type): bool`  
A number or bool: what a T[] given to C may hold (C sees an array of them).  
<sub>línea 781</sub>

`function resolveThrows(t: TypeRef? in default): Type?`
<sub>línea 785</sub>

`public function isByteArrayRef(t: TypeRef): bool`  
byte[N], byte[], byte[*] as written.  
<sub>línea 798</sub>

`function memoryParams(params: Param[*] in default, body: Stmt[*] in default): bool[*]`  
byte-array parameters used after `in` inside the body are memory parameters.  
<sub>línea 805</sub>

---

## semantics.analyzer.flow

`src/semantics/analyzer/flow.lar` · 740 líneas · 42 funciones
semantics.analyzer.flow: what a function's result may point to, and whether the function creates it.

`public function flowSummaries(): void`
<sub>línea 29</sub>

`function overridden(m: MethodInfo): MethodInfo[*]`  
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

`public function callMemory(f: FunctionInfo): bool`  
An extern whose first parameter is a memory: it creates in the memory of the call, which is not written.  
<sub>línea 184</sub>

`function makesResource(f: FunctionInfo): bool`  
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

`function bindsFlow(sw: SwitchExpr, flow: Any): bool`
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

`function switchCreates(sw: SwitchExpr, any: bool, declared: Declared): bool`
<sub>línea 485</sub>

`function yieldsCreate(block: Stmt[*], any: bool, declared: Declared): bool`  
Does a block arm of a switch yield a value it creates? (a local it yields lives in the block: an error, not a result)  
<sub>línea 494</sub>

`function staticCallee(c: Call): FunctionInfo?`  
Type.name(...) when it calls a static function.  
<sub>línea 504</sub>

`function callCreates(c: Call, any: bool, declared: Declared): bool`
<sub>línea 509</sub>

`function methodCreates(m: Member, c: Call, coarse: bool, any: bool, declared: Declared): bool`
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

`function fill(msg: String, v: Region, st: Region): String`
<sub>línea 600</sub>

`public function runCheck(d: Deferred in default, resolve: bool): void`
<sub>línea 617</sub>

`function placementFor(r: Region): String`  
The `in` that puts a copy where a region lives, when the code can say it: " in default", " in m", or "".  
<sub>línea 643</sub>

`function culprit(d: Deferred in default, v: Region, st: Region, resolve: bool): String`  
A message that names what lives too little, and the code that fixes it, when the value is something the programmer wrote: a lambda (its capture), a view (its text), a variable. "" when there is none.  
<sub>línea 652</sub>

`function isFunctionValue(e: Expr): bool`  
A lambda or a function value (it has no clone()).  
<sub>línea 714</sub>

`function parameterHint(name: String, st: Region): String`  
For a parameter that must live where it is kept: its declaration with `in`.  
<sub>línea 717</sub>

`function viewCulprit(e: Expr, v: Region, target: String, lives: String, keep: String): String`  
x.trim(), x.substring(...)...: the result shares the bytes of x.  
<sub>línea 724</sub>

`function clonesInside(l: Lambda, name: String): bool`  
Does the body of the lambda call name.clone()? (It runs when the lambda is called, not when it is made.)  
<sub>línea 732</sub>

---

## semantics.analyzer.narrowing

`src/semantics/analyzer/narrowing.lar` · 275 líneas · 15 funciones
semantics.analyzer.narrowing: where a T? variable is known not to be null.

`public function nonNull(c: Expr in default, onTrue: bool): Symbol[*]`  
The optional locals that are not null when `c` evaluates to `onTrue` (and the names after `is`).  
<sub>línea 22</sub>

`function facts(c: Expr in default, onTrue: bool, out: Symbol[*] in default): void`
<sub>línea 28</sub>

`public function hasSymbol(list: Symbol[*], s: Symbol): bool`
<sub>línea 54</sub>

`public function narrow(syms: Symbol[*] in default): void`  
Narrows in the current scope; an assignment to the variable ends it (see analyzeStmts).  
<sub>línea 62</sub>

`public function unnarrow(syms: Symbol[*]): void`
<sub>línea 79</sub>

`public function leaves(body: Stmt[*]): bool`  
Does the block always leave (return, throw, break, continue)?  
<sub>línea 94</sub>

`public function reassignedNames(body: Stmt[*] in default): Any`  
The variables a body assigns somewhere (not inside lambdas).  
<sub>línea 105</sub>

`public function assigns(body: Stmt[*] in default, name: String): bool`
<sub>línea 115</sub>

`public function analyzeFor(f: ForStmt in default): void`
<sub>línea 124</sub>

`function loopBody(body: Stmt[*] in default): void`
<sub>línea 189</sub>

`public function analyzeThrow(t: ThrowStmt in default): void`
<sub>línea 198</sub>

`public function requireHandled(e: EnumInfo, line: int32, what: String): void`
<sub>línea 211</sub>

`public function analyzeYield(y: YieldStmt in default): void`
<sub>línea 227</sub>

`public function analyzeTry(t: TryStmt in default): void`
<sub>línea 239</sub>

`function hasEnum(list: EnumInfo[*], e: EnumInfo): bool`
<sub>línea 269</sub>

---

## semantics.analyzer.order

`src/semantics/analyzer/order.lar` · 145 líneas · 8 funciones
semantics.analyzer.order: orders that must exist: globals get their values in order, C structs are defined before they are embedded.

`public function checkGlobalOrder(initializers: Owner[*] in default): void`  
The initial value of a global, and every function it calls however deep, cannot use a global that is initialized after it (or itself): it would find it without its value.  
<sub>línea 14</sub>

`function initializedFrom(g: Symbol in default, k: int32): bool`  
Whether global `g` is the k-th one or one initialized after it.  
<sub>línea 39</sub>

`public function computeTypeOrder(): void`
<sub>línea 53</sub>

`function visitType(t: Type in default, path: Type[*] in default): void`
<sub>línea 68</sub>

`function display(t: Type): String`
<sub>línea 93</sub>

`function typeLine(t: Type): int32`
<sub>línea 95</sub>

`function valueDeps(t: Type in default): Type[*]`  
Types that t's C definition embeds by value.  
<sub>línea 110</sub>

`function addValueDep(out: Type[*] in default, t: Type in default): void`
<sub>línea 138</sub>

---

## semantics.analyzer.statements

`src/semantics/analyzer/statements.lar` · 477 líneas · 20 funciones
semantics.analyzer.statements: the bodies of functions and methods, statement by statement.

`public function analyzeFunction(f: FunctionInfo in default): void`
<sub>línea 38</sub>

`public function analyzeMethod(m: MethodInfo in default, selfType: Type in default): void`
<sub>línea 56</sub>

`public function declareParam(p: Param in default, t: Type in default, memory: bool): Symbol`
<sub>línea 73</sub>

`function applyLives(ps: Param[*] in default, syms: Symbol[*] in default, mem: bool[*] in default, selfSym: Symbol? in default): void`  
`k: Node in p`, `s: String in default`, `x: T in self`, `x: T in m` (a memory parameter): the parameter's data lives as long as that, so it can be stored there.  
<sub>línea 88</sub>

`function livesRegion(ps: Param[*] in default, syms: Symbol[*] in default, mem: bool[*], selfSym: Symbol? in default, start: int32, line: int32): Region?`
<sub>línea 105</sub>

`public function livesHint(value: Region, storage: Region): String`  
When a parameter is stored somewhere longer-lived, the parameter can say so: `k: Node in p`.  
<sub>línea 144</sub>

`public function checkReturns(body: Stmt[*] in default, ret: Type, line: int32, what: String): void`
<sub>línea 157</sub>

`function isPanic(e: Expr): bool`  
panic(...): the program stops there.  
<sub>línea 163</sub>

`public function alwaysExits(body: Stmt[*]): bool`
<sub>línea 169</sub>

`function containsBreak(body: Stmt[*]): bool`
<sub>línea 196</sub>

`public function analyzeStmts(body: Stmt[*] in default): void`
<sub>línea 226</sub>

`public function analyzeBlock(body: Stmt[*] in default): void`
<sub>línea 253</sub>

`function analyzeStmt(s: Stmt in default): void`
<sub>línea 259</sub>

`public function requireBool(cond: Expr in default, what: String): void`
<sub>línea 293</sub>

`public function analyzeVarDecl(v: VarDecl in default): void`
<sub>línea 298</sub>

`function declareHeapMemory(v: VarDecl in default, p: Placed in default, kind: SymK, global: bool): void`
<sub>línea 345</sub>

`function analyzeAssign(asg: AssignStmt in default): void`
<sub>línea 370</sub>

`public function cStructField(f: FieldInfo): bool`  
A field of a C struct (extern type X = struct { ... }).  
<sub>línea 461</sub>

`function memberIsAnyKey(m: Member in default): bool`
<sub>línea 466</sub>

`function describeTarget(t: Expr): String`
<sub>línea 472</sub>

---

## semantics.analyzer.threads

`src/semantics/analyzer/threads.lar` · 214 líneas · 13 funciones
semantics.analyzer.threads: what a thread can share.

`public function currentOwner(): Owner?`
<sub>línea 13</sub>

`public function edge(from: Owner? in default, to: Owner? in default): void`
<sub>línea 23</sub>

`public function useGlobal(s: Symbol in default, line: int32): void`
<sub>línea 27</sub>

`public function callTargets(receiver: Type, m: MethodInfo in default): MethodInfo[*]`  
Every method a call can reach: overrides in subclasses, or the implementations of an interface method.  
<sub>línea 36</sub>

`public function sendable(t: Type in default): bool`  
Can a value of this type be used by two threads at once without a lock?  
<sub>línea 50</sub>

`function sendableIn(t: Type in default, visiting: Any): bool`
<sub>línea 55</sub>

`function implementsInterface(c: ClassInfo in default, i: String): bool`  
Class c implements interface i (itself, or a class it extends).  
<sub>línea 89</sub>

`public function stateFields(name: String in default): String`  
The fields that make objects of class `name` changeable, as text ('a', 'b'), or "" when they have none: an object with no fields, in its class or in any class that extends it, has no state that two threads could change, so it is shared like a value (a set of routes, a strategy). A Thread or a StringBuilder keeps state of its own.  
<sub>línea 104</sub>

`function changeable(t: Type in default): String`  
For the message of a value that cannot be shared: what an ordinary object has that could change.  
<sub>línea 118</sub>

`public function checkSynchronizedClasses(): void`
<sub>línea 124</sub>

`public function checkThreadSafeLambda(l: LambdaInfo in default, line: int32): void`  
A lambda given where a `thread safe` function is expected: checked like the run of a Thread.  
<sub>línea 153</sub>

`public function checkThreadRun(o: ObjectLit in default): void`  
Thread { run: ... }: a lambda written here, or a synchronized object.  
<sub>línea 158</sub>

`public function checkThreads(): void`
<sub>línea 176</sub>

---

## semantics.expressions

`src/semantics/expressions.lar` · 571 líneas · 29 funciones
semantics.expressions: semantic analysis (Analyzer.java), part 2: types as written, constants,
expressions, conversions, calls, switch and patterns.

`public function resolveTop(t: TypeRef in default, ctx: int32, what: String): Type`
<sub>línea 40</sub>

`public function resolveValue(t: TypeRef in default, what: String): Type`
<sub>línea 51</sub>

`public function resolveType(t: TypeRef in default): Type`
<sub>línea 56</sub>

`function resolveNamed(t: TypeRef in default): Type`
<sub>línea 101</sub>

`public function note(t: Type in default): void`  
Registers a type (and its parts) so the generator emits it.  
<sub>línea 122</sub>

`public function noted(t: Type in default): Type`  
Notes that the generated C needs the type, and returns it.  
<sub>línea 152</sub>

`public function check(e: Expr in default, expected: Type? in default, place: Place in default): Type`
<sub>línea 161</sub>

`function checkInner(e: Expr in default, expected: Type? in default, place: Place in default): Type`
<sub>línea 169</sub>

`function checkUnwrap(u: Unwrap in default, expected: Type? in default, place: Place in default): Type`
<sub>línea 197</sub>

`public function checkIntValue(v: ConstVal, line: int32, expected: Type? in default): Type`  
An integer literal where `expected` is wanted.  
<sub>línea 207</sub>

`function checkString(s: StringLit in default, place: Place in default): Type`
<sub>línea 223</sub>

`function checkIdent(id: Ident in default, expected: Type? in default): Type`
<sub>línea 236</sub>

`function cFunctionValue(id: Ident in default, f: FunctionInfo in default, ft: Type in default, sig: Type in default): Type`  
A function given where a pointer to a C function is expected: it must exist in C with that signature.  
<sub>línea 274</sub>

`function checkSelf(se: Expr in default): Type`
<sub>línea 290</sub>

`public function lookupIn(sc: Scope in default, name: String): Symbol?`
<sub>línea 310</sub>

`public function variantFieldNames(v: VariantInfo in default): String`
<sub>línea 318</sub>

`public function typeNamed(e: Expr): String`  
The type an expression names (Order, String, a type of another module), or "".  
<sub>línea 326</sub>

`public function enumNamed(e: Expr): EnumInfo?`
<sub>línea 332</sub>

`public function memoryNamed(e: Expr): Symbol?`  
The memory a name refers to, if it is one.  
<sub>línea 337</sub>

`function checkMember(m: Member in default, place: Place in default): Type`
<sub>línea 343</sub>

`public function isProperty(t: Type in default, name: String): bool`  
A value read without parentheses: the length of a String, an array, a list or an Any, or a native let.  
<sub>línea 438</sub>

`public function fieldOf(t: Type in default, name: String): FieldInfo?`
<sub>línea 444</sub>

`public function methodOf(t: Type in default, name: String): MethodInfo?`  
A method of a struct, class or interface (not an operator).  
<sub>línea 450</sub>

`function nativeMethodOf(owner: String, name: String): MethodInfo?`  
A method that a native type declares for a C type.  
<sub>línea 461</sub>

`public function describeExpr(e: Expr): String`
<sub>línea 468</sub>

`function checkIndex(ix: Index in default): Type`
<sub>línea 477</sub>

`public function resolvePlacement(p: Placed in default): Place?`  
The Place written after `in`, or null after reporting an error.  
<sub>línea 498</sub>

`function checkPlaced(p: Placed in default, expected: Type? in default): Type`
<sub>línea 519</sub>

`public function resolveMemory(e: Expr in default): Symbol?`  
`in m`: m must be a memory (a heap memory, or an empty byte[N] that becomes one).  
<sub>línea 539</sub>

---

## semantics.expressions.calls

`src/semantics/expressions/calls.lar` · 837 líneas · 32 funciones
semantics.expressions.calls: calls: functions, methods, constructors and what the language has built in.

`public function checkAllArgs(c: Call in default): Type`
<sub>línea 29</sub>

`function builtinCall(c: Call in default, kind: BK, receiver: Type? in default): void`
<sub>línea 34</sub>

`function throwing(c: Call in default, tt: Type?, what: String): void`  
A call to something that can throw: it must be handled.  
<sub>línea 39</sub>

`public function checkCall(c: Call in default, expected: Type? in default, place: Place in default): Type`
<sub>línea 45</sub>

`function checkMemoryCall(c: Call in default, compact: bool): Type`  
Memory.limit(m, bytes) and Memory.compact(m): they work on the memory itself, so m must be its name. compact() is checked again at the end (checkCompacts), once the memory of every variable is known.  
<sub>línea 94</sub>

`function checkFunctionCall(c: Call in default, f: FunctionInfo in default, place: Place in default): Type`
<sub>línea 123</sub>

`function namesCFunction(a: Expr): bool`  
Does the argument name a function of C, a native or an export function (it goes to C as it is)?  
<sub>línea 193</sub>

`function flowsOf(c: Call, m: MethodInfo): bool[*]`  
The arguments the result of a method call may point to.  
<sub>línea 200</sub>

`public function all(n: int32, b: bool): bool[*]`  
n times b.  
<sub>línea 205</sub>

`public function madeBy(e: Expr in default, m: MethodInfo in default, place: Place in default): Region`  
What a method call creates (only if some method of that name may create its result).  
<sub>línea 212</sub>

`public function placedResult(e: Expr in default, ret: Type in default, place: Place in default): Region`  
A result with data, created where the expression says (like a call's).  
<sub>línea 217</sub>

`function checkSuperCall(c: Call in default, sm: SuperMember in default, place: Place in default): Type`
<sub>línea 223</sub>

`function checkMethodCall(c: Call in default, callee: Member in default, expected: Type? in default, place: Place in default): Type`
<sub>línea 247</sub>

`function checkNativeMethodCall(c: Call in default, callee: Member in default, mi: MethodInfo in default, place: Place in default): Type`
<sub>línea 347</sub>

`function closureCall(c: Call in default, t: Type in default, calleeRegion: Region in default, place: Place in default): Type`
<sub>línea 358</sub>

`public function same(c: Call in default, place: Place in default): Place[*]`  
The same place for every argument.  
<sub>línea 383</sub>

`function checkArgsLives(c: Call in default, params: Type[*] in default, varargs: bool, memParams: bool[*], name: String, decls: Param[*]? in default, selfRegion: Region? in default, argPlace: Place in default, receiver: Expr? in default, flows: bool[*]?): Region`  
Checks arguments, and the `in` of the parameters; returns the meet of the regions of the arguments that reference memory. argPlace: where arguments with data are created (the call's place when the result may point to them). A parameter that says where it lives gets its argument created there: `in default`, `in self`.  
<sub>línea 394</sub>

`function checkArgs(c: Call in default, params: Type[*] in default, varargs: bool, memParams: bool[*], name: String, places: Place[*] in default, flows: bool[*]): Region`
<sub>línea 454</sub>

`function checkClone(c: Call in default, ot: Type in default, place: Place in default): Type`
<sub>línea 500</sub>

`function heldResource(t: Type, visiting: Any): String`  
The resource type a value holds (directly or in a field, an element...), or "".  
<sub>línea 519</sub>

`function changesArray(c: Call in default, obj: Expr in default, at: Type in default, kind: BK): void`  
push, pop and clear change a fixed array in place: it must be a variable or a field.  
<sub>línea 544</sub>

`function checkArrayMethod(c: Call in default, m: Member in default, at: Type in default, expected: Type? in default, place: Place in default): Type`
<sub>línea 550</sub>

`function checkSort(c: Call in default, obj: Expr in default, at: Type in default): Type`  
list.sort(): numbers and Strings in their natural order. list.sort(compare): any elements, in the order that compare(a, b) says (negative: a goes first; zero: equal; positive: b goes first). Stable, in place.  
<sub>línea 614</sub>

`function checkMapFilter(c: Call in default, obj: Expr in default, isMap: bool, at: Type in default, expected: Type? in default, place: Place in default): Type`
<sub>línea 631</sub>

`function stringForms(name: String): String`  
The String methods the compiler writes itself (the rest are written in Larimar in std/lang.lar).  
<sub>línea 665</sub>

`function checkStringMethod(c: Call in default, m: Member in default, place: Place in default): Type`  
The core methods of String: its length, views of it (substring, bytes) and lists of views (split, lines).  
<sub>línea 675</sub>

`function checkAnyMethod(c: Call in default, m: Member in default): Type`  
remove(name), removeAt(i), clear(), removeIf((value) -> ...) or removeIf((name, value) -> ...).  
<sub>línea 735</sub>

`function comparableInAny(t: Type): bool`  
Values contains() can find in an Any: compared by value (numbers, bool, String) or identity (objects).  
<sub>línea 807</sub>

`function comparable(t: Type): bool`  
Elements contains() can compare with ==.  
<sub>línea 813</sub>

`function markGlobalMutation(obj: Expr in default): void`
<sub>línea 817</sub>

`function recordValueMutation(obj: Expr in default, line: int32): void`
<sub>línea 822</sub>

`function throughRef(target: Expr): bool`
<sub>línea 829</sub>

---

## semantics.expressions.constants

`src/semantics/expressions/constants.lar` · 153 líneas · 9 funciones
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

`public function intFits(i: int64, big: bool, huge: bool, t: Type): bool`  
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

`src/semantics/expressions/conversions.lar` · 228 líneas · 13 funciones
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

`public function hasRefs(t: Type): bool`
<sub>línea 59</sub>

`public function namedHasRefs(name: String, nk: NamedK): bool`  
Has a struct or an enum (by name) references to memory?  
<sub>línea 65</sub>

`function hasRefsIn(t: Type, visiting: Any): bool`
<sub>línea 70</sub>

`function namedRefsIn(name: String, nk: NamedK, visiting: Any): bool`
<sub>línea 85</sub>

`public function conv(kind: ConvK, from: Type in default, to: Type in default): Conversion`
<sub>línea 108</sub>

`public function coerce(e: Expr in default, target: Type in default, place: Place in default, ctx: String in default): Type`  
Checks `e` where a value of type `target` is needed, applying implicit conversions. Returns the target type, or ERROR.  
<sub>línea 117</sub>

`function box(e: Expr in default, t: Type, place: Place in default): void`  
A struct or enum put in an Any is copied into a memory: the one written with `in`, or the table's.  
<sub>línea 181</sub>

`public function conversion(from: Type in default, to: Type in default): Conversion?`
<sub>línea 191</sub>

---

## semantics.expressions.literals

`src/semantics/expressions/literals.lar` · 369 líneas · 15 funciones
semantics.expressions.literals: lambdas, objects, lists, tables and casts.

`public function checkLambda(l: Lambda in default, expected: Type? in default): Type`
<sub>línea 20</sub>

`public function calledReference(c: Call in default, ref: Call in default): Type`  
pepito::run(): the parentheses call it; the reference is written without them.  
<sub>línea 71</sub>

`public function refText(c: Call): String`  
How a method reference was written: Pages::show.  
<sub>línea 80</sub>

`function referenceTarget(c: Call in default): bool`  
Module::function, variable::method or self::method; not a field (it would be read on every call).  
<sub>línea 91</sub>

`function checkValues(o: ObjectLit in default): Type`
<sub>línea 99</sub>

`function valuesRegion(o: ObjectLit in default): Region`
<sub>línea 104</sub>

`function writtenHere(e: Expr in default): bool`  
A value nobody else has: a list or an object written there, of values or of what is written there too.  
<sub>línea 111</sub>

`function checkSynchronizedInits(o: ObjectLit in default, typeName: String in default): void`  
What a synchronized object is created with: values, or what is written right there. A list or an object that whoever creates it still has would be used by two threads without the lock, and a function could be called by two at once: that one is `thread safe`.  
<sub>línea 133</sub>

`public function checkObjectLit(o: ObjectLit in default, expected: Type? in default, place: Place in default): Type`
<sub>línea 146</sub>

`function checkAnyLit(o: ObjectLit in default, place: Place in default): Type`  
{ 1, "two", name: v, inner: { ... } }: positions and named entries.  
<sub>línea 236</sub>

`function checkFieldInits(o: ObjectLit in default, fields: FieldInfo[*] in default, typeName: String, place: Place in default, objRegion: Region? in default): void`  
objRegion != null: a class object, whose fields must not reference shorter-lived data.  
<sub>línea 256</sub>

`public function checkArrayLit(a: ArrayLit in default, expected: Type? in default, place: Place in default): Type`
<sub>línea 287</sub>

`public function checkCast(c: Cast in default): Type`
<sub>línea 328</sub>

`public function checkWith(facts: Symbol[*] in default, e: Expr in default, expected: Type? in default, place: Place in default): Type`  
Checks e where the facts hold (the right side of && and ||, a side of ?:).  
<sub>línea 352</sub>

`public function coerceWith(facts: Symbol[*] in default, e: Expr in default, target: Type in default, place: Place in default, ctx: String in default): Type`
<sub>línea 361</sub>

---

## semantics.expressions.operators

`src/semantics/expressions/operators.lar` · 341 líneas · 16 funciones
semantics.expressions.operators: ? :, is, and the unary and binary operators.

`public function checkTernary(t: Ternary in default, expected: Type? in default, place: Place in default): Type`  
c ? a : b. The side that is not a bare literal (a number or null) gives the type, and the other side takes it. Two classes meet in their nearest common ancestor.  
<sub>línea 26</sub>

`public function checkIs(x: IsExpr in default): Type`  
x is Dog [d]: the binding is declared where the test is known to be true (see facts).  
<sub>línea 64</sub>

`public function related(cls: ClassInfo in default, t: Type in default): bool`  
Can a value of class or interface type `t` be a `cls`?  
<sub>línea 95</sub>

`function loose(e: Expr): bool`  
A number or null literal: it takes the type of the other side of ?:.  
<sub>línea 100</sub>

`public function withoutThreadSafe(t: Type in default): Type`  
A type without `thread safe` (also inside an optional), or the type itself.  
<sub>línea 103</sub>

`public function optional(t: Type in default): Type`
<sub>línea 109</sub>

`function unify(a: Type in default, b: Type in default): Type?`
<sub>línea 113</sub>

`function convertTo(e: Expr in default, from: Type in default, to: Type in default): void`
<sub>línea 130</sub>

`public function checkUnary(u: Unary in default, expected: Type? in default, place: Place in default): Type`
<sub>línea 139</sub>

`function checkAddress(u: Unary in default): Type`  
&x: a pointer to the variable x, for C to read or write (getaddrinfo(..., &list), accept(fd, &addr, &len)). Only as an argument of an extern function, so it never outlives the call; x is a variable whose type a C pointer can point to.  
<sub>línea 171</sub>

`function operatorOf(t: Type in default, op: String, arity: int32): MethodInfo?`
<sub>línea 200</sub>

`function isIntLiteral(e: Expr): bool`
<sub>línea 205</sub>

`public function checkBinary(b: Binary in default, expected: Type? in default, place: Place in default): Type`
<sub>línea 213</sub>

`function checkEquality(b: Binary in default): void`
<sub>línea 282</sub>

`function operands(b: Binary in default, hint: Type? in default): bool`  
Checks both sides (into lt and rt); integer literals adapt to the other side. Returns false when one is an error.  
<sub>línea 311</sub>

`function overloaded(b: Binary in default, t0: Type in default, op: String in default): bool`
<sub>línea 330</sub>

---

## semantics.expressions.switches

`src/semantics/expressions/switches.lar` · 336 líneas · 10 funciones
semantics.expressions.switches: switch: its patterns and what they cover.

`public function analyzeSwitch(sw: SwitchExpr in default, isExpr: bool, expected: Type? in default, place: Place in default): Type`
<sub>línea 20</sub>

`function namedTypeByName(name: String in default): Type?`
<sub>línea 118</sub>

`function bind(name: String in default, t: Type in default, line: int32): Symbol`  
An immutable name bound by a pattern.  
<sub>línea 127</sub>

`function bindPatternsForInference(c: SwitchCase in default, inner: Type in default): void`  
Declares pattern bindings before inferring the switch type from the first arm.  
<sub>línea 134</sub>

`function bindPart(name: String in default, t: Type in default, line: int32, subject: Expr in default): Symbol`  
A name bound to (part of) the subject: it shares the subject's memory when it references any.  
<sub>línea 160</sub>

`function resolvePattern(p: Pattern in default, st: Type in default, inner: Type in default, subject: Expr in default): PatternInfo?`
<sub>línea 166</sub>

`function anyPattern(p: Pattern in default, subject: Expr in default, pi: PatternInfo in default): PatternInfo?`  
case int64 n, case String s, case Any t (a table), case null.  
<sub>línea 252</sub>

`function classPattern(p: Pattern in default, inner: Type in default, pi: PatternInfo in default, binding: String in default, subject: Expr in default): PatternInfo?`
<sub>línea 268</sub>

`function analyzeArm(c: SwitchCase in default, si: SwitchInfo in default, isExpr: bool, place: Place in default): void`
<sub>línea 284</sub>

`function alwaysYields(body: Stmt[*]): bool`
<sub>línea 320</sub>

---

## semantics.linker

`src/semantics/linker.lar` · 1020 líneas · 53 funciones
semantics.linker: modules (Linker.java). Each file is a module; `import a.b` loads a/b.lar.

Every module is parsed, its top-level declarations are renamed with its path
(geo.shapes.Circle becomes geo__shapes__Circle; the main file keeps its names), every
reference is resolved through the module's imports, and everything is joined into one
program. The analyzer and the generator then see a single program with distinct names.

Lines are file index * 1000000 + line; decode() turns them back into "file:line".

### class `Module`

`function newModule(path: String in default, index: int32): Module`
<sub>línea 39</sub>

`public function inTarget(platform: String): bool`  
Whether what is for `platform` ("": every one) is for the target.  
<sub>línea 63</sub>

`function ownStd(mainPath: String in default): String?`  
The standard library a file belongs to, when it is one of its files (std/crypto.lar open in the editor, of a copy that is not the installed one): its modules are then the ones of that copy, so that `import std.crypto` in its parts is the file being read, not another.  
<sub>línea 81</sub>

`public function link(mainShown: String in default, mainSource: String in default, sourceDir: String in default, std: String in default, mainPath: String in default): Program`
<sub>línea 95</sub>

`function dictFromSet(into: Any, names: Any in default, prefix: String): void`
<sub>línea 134</sub>

`function error(line: int32, msg: String): void`
<sub>línea 138</sub>

`function loadLang(): void`  
std.lang, cut down to the declarations the program mentions, and the ones those mention (comments after // do not count). A name the main file declares itself is its own.  
<sub>línea 146</sub>

`function addWords(text: String in default): void`  
Adds the words of a text (not those of its comments) to `words`.  
<sub>línea 217</sub>

`function cWords(code: String in default, names: Any in default): void`  
Every name in a piece of C, into names.  
<sub>línea 233</sub>

`function cCodeUses(code: String in default, cSymbols: Any in default): bool`
<sub>línea 246</sub>

`function parse(m: Module in default, source: String in default): void`
<sub>línea 266</sub>

`public function readSource(path: String): String?`  
The text of a file, or null if it cannot be read.  
<sub>línea 298</sub>

`public function isStd(path: String): bool`
<sub>línea 308</sub>

`function moduleFile(path: String): String`  
Where a module's file is: std/, else the project's folder (the main file's), else a library of [packages] (its .lar, in its folder).  
<sub>línea 314</sub>

`function shownName(path: String): String`  
How a module's file is shown in messages.  
<sub>línea 334</sub>

`function visit(m: Module in default): void`  
Loads the imports first, so each module comes after the ones it uses (and globals start in that order).  
<sub>línea 343</sub>

`function tables(m: Module in default): void`
<sub>línea 378</sub>

`function bring(m: Module, into: Any, n: String in into, from: Module, mangled: String in into, line: int32): void`
<sub>línea 422</sub>

`function push(): void`
<sub>línea 440</sub>

`function pop(): void`
<sub>línea 445</sub>

`function declare(n: String in default): void`
<sub>línea 447</sub>

`function local(n: String): bool`
<sub>línea 451</sub>

`function nativeKnown(m: Module in default, name: String): bool`  
The native functions of modules: Memory.limit and Memory.compact, in std/memory.lar (imported, or opened alone).  
<sub>línea 461</sub>

`function larNames(m: Module in default, code: String, line: int32): String`  
lar"name" in ccode: a function, type or global of Larimar, by its Larimar name (module.name for another module); it becomes lar"its linked name", and the generator writes its C name there.  
<sub>línea 470</sub>

`function larName(m: Module in default, name: String): String`  
The linked name of a Larimar name seen from module m ("a.b.name": the module a.b), or "".  
<sub>línea 495</sub>

`function rewriteDecl(m: Module in default, d: Node in default): void`
<sub>línea 509</sub>

`function hasHeaders(m: Module in default): bool`  
Whether a module brings its own C headers (cinclude or ccode), itself or in its parts (the modules of its folder, net/posix.lar for net.lar): then its natives are declared by them, not by us.  
<sub>línea 608</sub>

`function function_(f: FunctionDecl in default, name: String in default): void`
<sub>línea 620</sub>

`function fields(fs: FieldDecl[*] in default): void`
<sub>línea 631</sub>

`function params(ps: Param[*] in default): void`
<sub>línea 638</sub>

`function typeRef(t: TypeRef? in default): void`
<sub>línea 642</sub>

`function typeName(name: String in default, line: int32): String`  
Shape, geo.Shape, Shape.Circle (enum variant), geo.Shape.Circle.  
<sub>línea 655</sub>

`function exported(from: Module, n: String, values: bool, line: int32): String`  
A public name of another module: values first, then types ("" after an error).  
<sub>línea 672</sub>

`function hidden(n: String, line: int32): void`  
Modules do not see the main file's declarations (nobody imports the main file).  
<sub>línea 686</sub>

`function block(body: Stmt[*] in default, newScope: bool): void`
<sub>línea 694</sub>

`function stmt(s: Stmt in default): void`
<sub>línea 700</sub>

`function exprOpt(e: Expr? in default): Expr?`
<sub>línea 751</sub>

`function expr(e: Expr in default): Expr`  
The expression renamed; module.name comes back as the name itself.  
<sub>línea 754</sub>

`function asksPlatform(e: Expr in default): bool`  
Platform.current(), as the linker leaves it.  
<sub>línea 834</sub>

`function chosen(sw: SwitchExpr in default): bool`  
A switch on the platform that --target reduced to its arm.  
<sub>línea 840</sub>

`function choosePlatform(sw: SwitchExpr in default): void`  
With --target, a switch on Platform.current() keeps only the arm of that platform, as its default.  
<sub>línea 845</sub>

`function switchExpr(sw: SwitchExpr in default): void`
<sub>línea 864</sub>

`function isAlias(n: String): bool`
<sub>línea 878</sub>

`function identName(id: Ident in default): void`
<sub>línea 882</sub>

`function pattern(p: Pattern in default): void`  
A variant keeps its name; a type or a constant is renamed (variant lookup ignores a module prefix).  
<sub>línea 898</sub>

`public function decode(msg: String): String`  
"[Line 2000005]" -> "[src/geo.lar:5]", "line 7" -> "main.lar:7", and geo__Shape -> geo.Shape.  
<sub>línea 920</sub>

`function replaceLines(msg: String, key: String, bracket: bool): String`
<sub>línea 926</sub>

`function moduleOfFile(index: int32): Module?`
<sub>línea 966</sub>

`public function namesOfFile(index: int32): Any`  
What a file can name: name -> its name after linking (its own, imported and the language's).  
<sub>línea 975</sub>

`public function isLangHelper(name: String): bool`  
A name std.lang keeps to itself (its helpers): every file sees it, but the editor does not offer it.  
<sub>línea 985</sub>

`public function aliasesOfFile(index: int32): Any`  
The modules a file imports with a name: alias -> module path ("geo.shapes").  
<sub>línea 992</sub>

`public function publicsOfModule(path: String): Any`  
The public names of a module, each with its name after linking.  
<sub>línea 1004</sub>

`public function fileOfModule(path: String): String`  
The file of a module, from its path ("geo.shapes"), or "".  
<sub>línea 1014</sub>

---

## semantics.types

`src/semantics/types.lar` · 1006 líneas · 87 funciones
semantics.types: what the analyzer knows. Types, regions (where data lives), scopes, symbols,
the information about declarations, and the per-node facts the generator reads.
It follows Types.java and Analysis.java of the Java version.

### enum `TyK`

### enum `NamedK`

### enum `ArrK`

### class `Type`

`function intern(t: Type in default): Type`
<sub>línea 45</sub>

`function prim(name: String in default): Type`
<sub>línea 53</sub>

`public function primByName(name: String): Type?`  
A built-in type by name (uint8 is byte), or null.  
<sub>línea 75</sub>

`public function isPrimName(name: String): bool`
<sub>línea 86</sub>

`public function named(name: String in default, nk: NamedK): Type`
<sub>línea 88</sub>

`public function funcT(params: Type[*] in default, ret: Type in default, safe: bool): Type`
<sub>línea 92</sub>

`public function hasThreadSafe(t: Type in default): bool`  
Is there a `thread safe` function type in t (itself, or the element of an optional or an array)?  
<sub>línea 109</sub>

`public function cTypeOf(t: Type in default): Type`  
The type C sees: t without `thread safe` (the same closure type), also inside optionals and arrays.  
<sub>línea 116</sub>

`public function arrayT(elem: Type in default, ak: ArrK, size: int64): Type`
<sub>línea 123</sub>

`public function optT(inner: Type in default): Type`
<sub>línea 134</sub>

`public function ptrT(inner: Type in default): Type`  
T*: a C pointer (only to numbers, C structs, extern types and other pointers).  
<sub>línea 141</sub>

`public function isPtr(t: Type): bool`
<sub>línea 145</sub>

`public function bits(t: Type): int32`
<sub>línea 147</sub>

`public function isFloat(t: Type): bool`
<sub>línea 158</sub>

`public function isInteger(t: Type): bool`
<sub>línea 159</sub>

`public function isNumeric(t: Type): bool`
<sub>línea 160</sub>

`public function isSigned(t: Type): bool`
<sub>línea 161</sub>

`public function isError(t: Type): bool`
<sub>línea 162</sub>

`public function isClass(t: Type): bool`
<sub>línea 163</sub>

`public function isStruct(t: Type): bool`
<sub>línea 164</sub>

`public function isInterface(t: Type): bool`
<sub>línea 165</sub>

`public function isEnumT(t: Type): bool`
<sub>línea 166</sub>

`public function isExternT(t: Type): bool`
<sub>línea 167</sub>

`public function isByteArray(t: Type): bool`
<sub>línea 168</sub>

`public function isOpt(t: Type): bool`
<sub>línea 169</sub>

`public function isArray(t: Type, ak: ArrK): bool`
<sub>línea 170</sub>

`public function optIsPointer(o: Type): bool`  
An optional that is a pointer in C (null is NULL): classes, extern types, T[*].  
<sub>línea 173</sub>

`public function minOf(t: Type): int64`  
The smallest and largest value of an integer type; for uint64 the largest is kept apart.  
<sub>línea 179</sub>

`public function maxOf(t: Type): int64`
<sub>línea 189</sub>

`public function maxText(t: Type): String`  
"the largest value" as text, for messages.  
<sub>línea 207</sub>

### enum `RK`

### class `Region`

`public function rStaticMemory(s: Symbol in default): Region`  
The region of a global memory: static like R_STATIC, but it keeps the memory's name for messages.  
<sub>línea 228</sub>

`public function rMemory(s: Symbol in default): Region`  
The region of a local memory with a name.  
<sub>línea 230</sub>

`public function rCaller(p: Symbol in default): Region`
<sub>línea 233</sub>

`public function rResult(r: Symbol in default): Region`  
The memory a caller gives for the result of a function (or method, or lambda).  
<sub>línea 235</sub>

`public function rLocal(s: Scope in default, label: String in default): Region`
<sub>línea 238</sub>

`public function rVar(v: Symbol in default): Region`
<sub>línea 239</sub>

`public function symbolic(r: Region): bool`
<sub>línea 241</sub>

`public function resolveRegion(r: Region in default): Region`  
Replaces Var parts with the regions computed for those variables (Symbol.resolved).  
<sub>línea 252</sub>

`public function outlives(a: Region, b: Region): bool`  
Does data in `a` live at least as long as data in `b`? (both concrete)  
<sub>línea 266</sub>

`public function meet(a: Region in default, b: Region in default): Region`  
The shorter-lived of two regions.  
<sub>línea 280</sub>

`public function sameRegion(a: Region, b: Region): bool`
<sub>línea 302</sub>

`public function describe(r: Region): String`
<sub>línea 314</sub>

### class `Scope`

`public function newScope(parent: Scope? in default, frame: Frame in default): Scope`
<sub>línea 346</sub>

`public function isAncestorOrSelf(a: Scope, s: Scope): bool`
<sub>línea 351</sub>

### enum `FrameK`

### class `Owner`
What a body can reach, for the thread checks: the globals it uses and what it calls.

`public function newOwner(): Owner`
<sub>línea 370</sub>

### class `Frame`

### enum `SymK`

### enum `MemK`

### enum `ConstK`

### class `Symbol`

`public function isMemory(s: Symbol): bool`
<sub>línea 426</sub>

`public function isCReserved(name: String): bool`
<sub>línea 440</sub>

`public function ascii(name: String): String`  
C99 identifiers are ASCII: año -> a_u00f1o.  
<sub>línea 451</sub>

`function asciiChar(c: int32): String`
<sub>línea 462</sub>

`function hex4(c: int32): String`  
Lowercase hexadecimal, at least 4 digits (like %04x).  
<sub>línea 467</sub>

`public function escapeName(name: String): String`
<sub>línea 480</sub>

### class `FieldInfo`

### class `FunctionInfo`

### class `ExternTypeInfo`
A type that comes from C: opaque (void*), a C type (c "T") or a pointer to a C function (sig). With `released by`, a resource: it lives in a memory, and the releaser runs when that memory is freed.

### class `MethodInfo`

`public function isMemParam(flags: bool[*], i: int32): bool`
<sub>línea 566</sub>

`public function cSuffix(m: MethodInfo): String`
<sub>línea 568</sub>

### class `StructInfo`

### class `ClassInfo`

### class `InterfaceInfo`

### class `VariantInfo`

### class `EnumInfo`

### class `LambdaInfo`

`public function hasCapture(l: LambdaInfo, s: Symbol): bool`
<sub>línea 639</sub>

### enum `PlaceK`
Where an allocating expression puts its data. Temp: nothing said, a temporary of the statement; Global: `in default`; Block: a variable's value, the memory of its block; Result: a returned value, the memory the caller gives; Memory, Stack: `in m`, `in byte[N]`; OfObject, OfList, OfAny: stored inside an object, a list or a table.

### class `Place`

`public function placeOf(kind: PlaceK, expr: Expr? in default): Place`
<sub>línea 666</sub>

### enum `ConvK`

### class `Conversion`

### enum `CallK`

### enum `BK`

### class `CallInfo`

### enum `MbK`

### class `MemberInfo`

### enum `PatK`

### class `PatternInfo`

### class `SwitchInfo`

### class `ForInfo`

### class `CatchInfo`

`public function structOf(name: String): StructInfo?`
<sub>línea 784</sub>

`public function classOf(name: String): ClassInfo?`
<sub>línea 789</sub>

`public function interfaceOf(name: String): InterfaceInfo?`
<sub>línea 794</sub>

`public function enumOf(name: String): EnumInfo?`
<sub>línea 799</sub>

`public function functionOf(name: String): FunctionInfo?`
<sub>línea 804</sub>

`public function isExternTypeName(name: String): bool`
<sub>línea 809</sub>

`public function isResource(t: Type): bool`  
An extern type declared `released by`: a resource that lives in a memory.  
<sub>línea 812</sub>

`public function platformCondition(p: String): String`  
The C condition of a platform, for #if.  
<sub>línea 819</sub>

`public function platformWithin(inner: String, outer: String): bool`  
Code that runs only on `inner` also runs where `outer` holds? (macos and linux are unix)  
<sub>línea 829</sub>

`public function nativeOwner(owner: String): Type`  
The type whose methods a native type declares: one the compiler knows (String), or one of C.  
<sub>línea 835</sub>

`public function externInfoOf(name: String): ExternTypeInfo?`
<sub>línea 842</sub>

`public function isContextT(t: Type): bool`  
Context: the void* of C that a callback gets back (std.lang declares it).  
<sub>línea 849</sub>

`public function contextView(t: Type): Type?`  
The Larimar function a pointer to a C function with a Context stands for, or null.  
<sub>línea 852</sub>

`public function externSig(t: Type): Type?`
<sub>línea 858</sub>

`public function externStructC(t: Type): String`  
The C struct a `native struct X { ... }` describes ("" for other types).  
<sub>línea 865</sub>

`public function isExternStruct(t: Type): bool`
<sub>línea 871</sub>

`public function isCValue(t: Type): bool`  
What can cross to C and back: numbers, bool, String (const char*), extern types, C structs and C pointers.  
<sub>línea 874</sub>

`public function pointable(t: Type): bool`  
What a C pointer can point to: numbers, bool, C structs, extern types that are not resources, pointers.  
<sub>línea 880</sub>

`public function structMethod(s: StructInfo, n: String, op: bool, arity: int32): MethodInfo?`
<sub>línea 885</sub>

`public function structField(s: StructInfo, n: String): FieldInfo?`
<sub>línea 892</sub>

`public function interfaceMethod(i: InterfaceInfo, n: String): MethodInfo?`
<sub>línea 899</sub>

`public function variantOf(e: EnumInfo, name: String): VariantInfo?`  
A variant by name; a module prefix never names a variant.  
<sub>línea 907</sub>

`public function enumSimple(e: EnumInfo): bool`
<sub>línea 917</sub>

`public function parentOf(c: ClassInfo): ClassInfo?`
<sub>línea 924</sub>

`public function syncField(c: ClassInfo in default): String`  
Where the lock of a synchronized class is in its C struct: the first synchronized class of the chain has it.  
<sub>línea 929</sub>

`public function chain(name: String in default): ClassInfo[*]`  
Root first; safe on broken hierarchies.  
<sub>línea 935</sub>

`public function findField(cls: String in default, field: String): FieldInfo?`
<sub>línea 955</sub>

`public function findMethod(cls: String in default, name: String, op: bool, arity: int32): MethodInfo?`  
The most derived definition (operators match by arity).  
<sub>línea 965</sub>

`public function allFields(cls: String in default): FieldInfo[*]`
<sub>línea 977</sub>

`public function isSubclass(sub: String in default, sup: String): bool`
<sub>línea 985</sub>

`public function implementor(cls: String in default, iface: String): String`  
The ancestor (or the class itself) that declares `implements iface`, or "".  
<sub>línea 993</sub>

`public function classDepth(name: String in default): int32`
<sub>línea 1005</sub>

---

## codegen.debugmap

`src/codegen/debugmap.lar` · 224 líneas · 10 funciones
codegen.debugmap: with larimar build --debug, what the debugger (larimar dap) needs to show the program as
Larimar: for each C function, its Larimar name and the variables it has (their Larimar names, their
names in C and their types), the globals, and the shape of every type (fields with their C paths,
enum variants, classes). Written next to the C as <name>.debug.json.

A type is described as JSON: {"k": "int"|"float"|"bool"|"String"|"any"|"list"|"slice"|"array"|"opt"|
"struct"|"class"|"interface"|"enum"|"raw", ...}; structs, classes, interfaces and enums by name, in
"types", so a type that contains itself is no problem.

`public function debugMap(): String`  
The debug map of the program just generated, as JSON.  
<sub>línea 25</sub>

`function methodJson(m: MethodInfo in default, isStruct: bool): String`
<sub>línea 61</sub>

`function fnJson(cName: String, display: String, line: int32, params: Symbol[*], selfVar: String?, body: Stmt[*] in default, lambda: LambdaInfo?): String`
<sub>línea 71</sub>

`function varJson(name: String, c: String, t: Type, line: int32): String`  
line: where it is declared (0 for parameters: from the start), so the debugger hides it before.  
<sub>línea 86</sub>

`function localsOf(body: Stmt[*] in default): Symbol[*]`  
The variables a body declares (not those of lambdas inside it: they are their own functions).  
<sub>línea 91</sub>

`function switchBindings(sw: SwitchExpr in out, out: Symbol[*]): void`
<sub>línea 130</sub>

`function typeJson(t: Type): String`
<sub>línea 143</sub>

`function raw(t: Type): String`
<sub>línea 172</sub>

`function describe(name: String, nk: NamedK): void`  
Adds a named type to "types" (once).  
<sub>línea 175</sub>

`function fieldJson(f: FieldInfo, path: String): String`
<sub>línea 221</sub>

---

## codegen.expressions

`src/codegen/expressions.lar` · 694 líneas · 52 funciones
codegen.expressions: C99 code generation (Gen.java), part 2: expressions.
An expression becomes a C expression; what needs statements first writes them with line().

`native function gen_double_text(d: float64): String`  
The shortest decimal text that gives the same double back.  
<sub>línea 27</sub>

`public function tname(n: String): String`
<sub>línea 41</sub>

`public function mangle(t: Type): String`
<sub>línea 46</sub>

`public function cType(t: Type): String`
<sub>línea 75</sub>

`public function structName(t: Type): String`
<sub>línea 113</sub>

`public function paren(s: String): String`
<sub>línea 122</sub>

`public function hoist(ct: String, v: String): String`
<sub>línea 124</sub>

`function hoistAddr(ct: String, v: String): String`
<sub>línea 130</sub>

`public function hoistIfNeeded(ct: String, v: String, e: Expr?): String`
<sub>línea 132</sub>

`public function inOrder(parts: Expr[*] in default): Expr[*]`  
Computes, in order, the parts before the last one with effects; returns them, for forget().  
<sub>línea 144</sub>

`public function forget(held: Expr[*]): void`  
The C of these parts is written: they are computed again where they appear next.  
<sub>línea 161</sub>

`function hasEffects(e: Expr): bool`  
Whether evaluating it can do something another part could see: a call, an index (a panic)...  
<sub>línea 166</sub>

`function anyEffects(es: Expr[*]): bool`
<sub>línea 178</sub>

`function unchangeable(e: Expr): bool`  
Whether nothing evaluated after it can change its value: literals, locals, parameters, constants.  
<sub>línea 186</sub>

`function callParts(c: Call in default): Expr[*]`  
The parts of a call, in the order they are written: the object (not a struct, which is passed by address), then the arguments.  
<sub>línea 199</sub>

`function orderedCall(c: Call in default): String`
<sub>línea 212</sub>

`function orderedIndex(x: Index in default): String`
<sub>línea 219</sub>

`function orderedBinary(b: Binary in default, t: Type): String`
<sub>línea 226</sub>

`public function writtenValues(o: ObjectLit in default): Expr[*]`  
The values of a literal, in the order they are written.  
<sub>línea 235</sub>

`public function isPure(e: Expr): bool`
<sub>línea 241</sub>

`public function lazy(e: Expr in default): String`  
Generates `e` (its value) into a separate buffer: its statements go to lazyPre.  
<sub>línea 253</sub>

`public function strip(s: String): String`  
Removes the outer parentheses of a C expression when they enclose all of it.  
<sub>línea 264</sub>

`public function zero(t: Type): String`
<sub>línea 290</sub>

`public function discard(e: String): void`  
A call whose result is not used.  
<sub>línea 301</sub>

`function isIdentifier(s: String): bool`
<sub>línea 307</sub>

`public function value(e: Expr in default): String`  
An expression with its conversion applied: where a value is stored or passed.  
<sub>línea 319</sub>

`function convert(v: String, c: Conversion in default, e: Expr? in default): String`
<sub>línea 326</sub>

`function innerConversion(from: Type in default, to: Type in default, outer: Conversion in default): Conversion?`  
The inner conversion of WRAP_OPTIONAL (upcast or interface), if any.  
<sub>línea 371</sub>

`public function boxType(t: Type in default): String`  
The descriptor of a struct or enum stored in an Any (its name and how to clone it).  
<sub>línea 383</sub>

`public function boxDescriptors(): String`
<sub>línea 391</sub>

`public function anyKind(t: Type): String`  
RT_ANY_I32 and so on: the kind an Any uses for a value of type t.  
<sub>línea 406</sub>

`public function anyPayload(t: Type, v: String): String`  
The value inside an Any already known to hold kind t.  
<sub>línea 425</sub>

`function toAny(v: String, from: Type in default, e: Expr in default): String`
<sub>línea 435</sub>

`public function expr(e: Expr in default): String`
<sub>línea 460</sub>

`function unwrap(u: Unwrap in default): String`
<sub>línea 489</sub>

`function placed(inner: Expr in default): String`  
`x in memory`: the value; a lambda that becomes an interface object is created there.  
<sub>línea 497</sub>

`public function intLiteral(v: int64, big: bool, t: Type?): String`  
An integer literal of type t (value v, as uint64 when big).  
<sub>línea 503</sub>

`function identExpr(id: Ident in default): String`
<sub>línea 520</sub>

`function constValue(s: Symbol): String`
<sub>línea 533</sub>

`function selfExpr(se: Expr in default): String`
<sub>línea 544</sub>

`function member(m: Member in default): String`
<sub>línea 551</sub>

`function fieldAccess(obj: Expr in default, f: MemberInfo): String`
<sub>línea 592</sub>

`public function fieldC(f: FieldInfo): String`  
A field's name in C: the exact one in a C struct, otherwise escaped.  
<sub>línea 603</sub>

`public function classFieldPath(cls: String, f: FieldInfo): String`
<sub>línea 609</sub>

`function index(ix: Index in default): String`
<sub>línea 620</sub>

`function isLvalueExpr(e: Expr): bool`
<sub>línea 638</sub>

`public function lvalue(target: Expr in default): String`  
The C lvalue of an assignment target (no narrowing).  
<sub>línea 652</sub>

`public function addrOf(e: Expr in default): String`  
A pointer to the value of `e` (a temporary if `e` is not a variable or field).  
<sub>línea 657</sub>

`public function memoryRef(mem: Symbol): String`
<sub>línea 662</sub>

`public function placeMem(e: Expr in default): String`  
C expression of type RtMem* for an allocation.  
<sub>línea 667</sub>

`public function callMem(c: Expr in default): String`  
The memory a call gives for its result: none (NULL) when the callee only returns data that already exists.  
<sub>línea 670</sub>

`public function placeMemOf(p: Place? in default): String`
<sub>línea 672</sub>

---

## codegen.expressions.calls

`src/codegen/expressions/calls.lar` · 534 líneas · 19 funciones
codegen.expressions.calls: calls.

`public function receiver(c: Call): Expr`  
The object a method is called on: a in a.f(...).  
<sub>línea 20</sub>

`function calleeName(c: Call): String`  
The name of the method called: f in a.f(...).  
<sub>línea 25</sub>

`public function call(c: Call in default): String`
<sub>línea 29</sub>

`function first(x: String, xs: String[*]): String[*]`  
x, then the items of xs.  
<sub>línea 136</sub>

`function isBuilderAdd(c: Call, ci: CallInfo): bool`
<sub>línea 142</sub>

`public function args(asg: Expr[*] in default, memParams: bool[*]): String[*]`
<sub>línea 149</sub>

`function writtenParams(f: FunctionInfo): Type[*]`  
The parameters of a C function that a call writes (not the memory of the call, when C takes it first).  
<sub>línea 159</sub>

`function externArgsAs(asg: Expr[*] in default, varargs: bool, params: Type[*]?): String[*]`  
The arguments as C takes them, for C parameters of these types (a T[] is two: its elements and their count).  
<sub>línea 168</sub>

`function contextArgs(c: Call in default, f: FunctionInfo, ci: CallInfo): String[*]`  
The arguments of a C function that takes a callback and its Context, in C's order: the callback goes as a trampoline (a C function), and the Context as the Larimar function itself, which the trampoline calls.  
<sub>línea 208</sub>

`function trampoline(ext: Type, view: Type): String`  
The C function of type `ext` that calls the Larimar function its Context carries (made once per pair).  
<sub>línea 248</sub>

`function itemsOf(at: Type, obj: Expr in default): String[*]`  
The elements of an array as C: items and length.  
<sub>línea 291</sub>

`function builtin(c: Call in default, b: CallInfo in default): String`
<sub>línea 301</sub>

`function printCall(c: Call in default, newline: bool): String`
<sub>línea 354</sub>

`function stringMethod(c: Call in default): String`
<sub>línea 368</sub>

`function splitText(c: Call in default, s: String, sep: String, isLines: bool): String`  
split, lines: views of the text in a new list.  
<sub>línea 383</sub>

`public function lines(text: String in default): void`  
Several lines of C, each written like line() does (a final newline adds no empty line).  
<sub>línea 414</sub>

`function anyRemoveIf(c: Call in default): String`  
Keeps the entries for which the lambda says false; returns how many were removed.  
<sub>línea 422</sub>

`function sortList(c: Call in default, at: Type in default): String`  
list.sort(...): a merge sort, bottom up, in place (stable: of two equal elements the first stays first), with a buffer for one copy of the elements while it runs.  
<sub>línea 466</sub>

`function mapFilter(c: Call in default, b: CallInfo): String`
<sub>línea 505</sub>

---

## codegen.expressions.clone

`src/codegen/expressions/clone.lar` · 205 líneas · 10 funciones
codegen.expressions.clone: clone: copying a value into another memory.

`public function cloneTypeList(): Type[*]`
<sub>línea 15</sub>

`public function needsDeepClone(t: Type): bool`
<sub>línea 17</sub>

`public function requireClone(t: Type in default): void`
<sub>línea 41</sub>

`public function cloneHeader(t: Type): String`
<sub>línea 63</sub>

`public function cloneOf(t: Type in default, v: String): String`
<sub>línea 67</sub>

`function requireClassClones(): void`  
A class object is copied by its own class (a subclass, maybe): every class's fields may need copying.  
<sub>línea 74</sub>

`public function cloneCall(c: Call in default, b: CallInfo in default): String`
<sub>línea 82</sub>

`public function compactCall(c: Call in default, b: CallInfo in default): String`  
Memory.compact(m): m starts again with no blocks; what its variables reach in the old blocks is copied back (each thing once, cycles included), the variables are pointed at the copies, and the old blocks are freed. What lives in other memories is left where it is.  
<sub>línea 102</sub>

`public function cloneFunctions(): String`
<sub>línea 124</sub>

`function cloneBody(out: StringBuilder, t: Type in default): void`
<sub>línea 138</sub>

---

## codegen.expressions.lambdas

`src/codegen/expressions/lambdas.lar` · 200 líneas · 10 funciones
codegen.expressions.lambdas: lambdas and literal objects.

`public function lambdaValue(l: Lambda in default): String`
<sub>línea 20</sub>

`function captureValue(s: Symbol): String`
<sub>línea 30</sub>

`function genLambda(li: LambdaInfo in default): void`
<sub>línea 36</sub>

`public function sam(l: Lambda in default, c: Conversion in default): String`  
A lambda used as a single-method interface: a small object holding the closure.  
<sub>línea 52</sub>

`function givenValue(o: ObjectLit, name: String): Expr?`
<sub>línea 66</sub>

`public function objectLit(o: ObjectLit in default, t: Type in default): String`
<sub>línea 74</sub>

`function fieldInits(fields: FieldInfo[*] in default, o: ObjectLit in default, mem: String in default): String`
<sub>línea 125</sub>

`function classInit(level: ClassInfo in default, concrete: String, o: ObjectLit in default, mem: String in default): String`
<sub>línea 145</sub>

`function interfaceLit(o: ObjectLit in default, i: InterfaceInfo in default): String`
<sub>línea 156</sub>

`public function arrayLit(a: ArrayLit in default, t: Type): String`
<sub>línea 185</sub>

---

## codegen.expressions.operators

`src/codegen/expressions/operators.lar` · 218 líneas · 12 funciones
codegen.expressions.operators: operators.

`public function wide(t: Type): String`
<sub>línea 15</sub>

`public function unary(u: Unary in default, t: Type): String`
<sub>línea 19</sub>

`public function binary(b: Binary in default, t: Type): String`
<sub>línea 30</sub>

`public function isTest(x: IsExpr in default): String`  
x is T [b]: rt_as_class gives the object when it is a T (NULL otherwise); the binding keeps it.  
<sub>línea 90</sub>

`public function ternary(te: Ternary in default, t: Type): String`  
c ? a : b: a C conditional, or an if when a side needs statements of its own.  
<sub>línea 107</sub>

`function coalesce(b: Binary in default, t: Type): String`
<sub>línea 126</sub>

`function operatorCall(m: MethodInfo, op: Expr in default, left: Expr in default, right: Expr? in default): String`  
a OP b, where the operator is a method of a's type; `op` is the expression (data it returns is created where it says).  
<sub>línea 153</sub>

`function operatorCallSwapped(m: MethodInfo, b: Binary in default): String`  
b < a, keeping the evaluation order a then b.  
<sub>línea 162</sub>

`function minMacro(p: Type): String`
<sub>línea 168</sub>

`function maxMacro(p: Type): String`
<sub>línea 170</sub>

`public function cast(c: Cast in default, to: Type in default): String`
<sub>línea 174</sub>

`function anyAs(v: String, t: Type in default, ot: Type): String`  
`a as T`: T? holding the value if the Any has one of that kind (numbers convert when they fit).  
<sub>línea 186</sub>

---

## codegen.expressions.patterns

`src/codegen/expressions/patterns.lar` · 66 líneas · 2 funciones
codegen.expressions.patterns: the patterns of a switch.

`public function patternTest(pi: PatternInfo in default, st: Type, inner: Type, subj: String, val: String): String`  
Joined only with || (several patterns in one case), so a comparison needs no parentheses of its own (clang warns about if ((a == b))).  
<sub>línea 11</sub>

`public function bindPattern(pi: PatternInfo, inner: Type, subj: String, val: String): void`
<sub>línea 42</sub>

---

## codegen.expressions.strings

`src/codegen/expressions/strings.lar` · 220 líneas · 8 funciones
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
Writes the parts of an interpolated text into a builder (sbRef: an RtSb*).  
<sub>línea 125</sub>

`public function stringLiteral(raw: String): String`
<sub>línea 153</sub>

`function cBytes(raw: String): String`
<sub>línea 163</sub>

`function cByte(sb: StringBuilder, v: byte, text: String): void`
<sub>línea 200</sub>

---

## codegen.gen

`src/codegen/gen.lar` · 898 líneas · 32 funciones
codegen.gen: C99 code generation (Gen.java), part 1: the file, types, classes and interfaces,
globals, bodies and statements. Expressions are in genexpr.lar.

- struct     -> C struct, copied by value; methods are plain functions on S*.
- class      -> C struct in a memory, used through pointers. The root struct starts with
RtObjHead (vtable + memory); a subclass embeds its parent as `_super`.
- interface  -> { void* obj; const I_Table* t; }
- enum       -> { int32_t tag; union { ...payloads } as; }
- closure    -> { fn; union of every environment of that type }, copied by value.
- T[N]       -> { length; items[N] } by value; T[] -> { items*, length };
T[*] -> pointer to { items*, length, capacity, mem }.
- errors     -> a function that throws takes RtError* err_out; every call checks it.
- memories   -> RtMem; heap memories are freed on every exit of their block.

### class `Block`

### class `TryCtx`

### class `ArmCtx`

### class `Fn`

### class `Temp`
A statement's temporary memory, declared before the statement only if something used it.

`public function newFn(): Fn`
<sub>línea 79</sub>

`public function internalError(line: int32, msg: String): void`
<sub>línea 88</sub>

`public function lineMark(encoded: int32): String`
<sub>línea 115</sub>

`function cPathLiteral(path: String): String`
<sub>línea 122</sub>

`public function spreadLines(c: String, cFile: String): String`  
After generating with debugLines: inside a function, every line of C after a #line gets that same .lar line (C would count on: N, N+1, N+2...); after the function, the lines are the C file's again, so the runtime and helpers are shown as the C they are.  
<sub>línea 129</sub>

`function firstMark(all: String[*], k: int32): String`  
The first #line of the function whose header is all[k] (before the function ends), or "".  
<sub>línea 176</sub>

`public function line(s: String): void`
<sub>línea 189</sub>

`public function tmp(prefix: String): String`
<sub>línea 198</sub>

`public function indent4(text: String in default): String`  
Adds four spaces to every line (like String.indent(4) in Java).  
<sub>línea 205</sub>

`public function pushBlock(b: Block in default): void`
<sub>línea 217</sub>

`public function popBlock(): void`
<sub>línea 219</sub>

`public function topBlock(): Block`
<sub>línea 229</sub>

`public function rootBlock(): Block`
<sub>línea 230</sub>

`public function generate(): String`
<sub>línea 238</sub>

`public function internal(): String`  
In a library everything but its export functions stays inside it: two libraries (and the program) do not clash.  
<sub>línea 592</sub>

`function exportHelpers(out: StringBuilder): void`  
What export functions use to give C its texts and the handles of a library's objects (cut when unused).  
<sub>línea 595</sub>

`function libraryGlue(out: StringBuilder): void`  
What a library gives C besides its export functions: <prefix>_free for its texts, <prefix>_<Class>_release for its handles, <prefix>_interface, and the start: the globals are made before the first call (when the library is loaded, where the C compiler allows it).  
<sub>línea 641</sub>

`public function handleClassNames(): String[*]`  
The classes C knows as handles, in order (their names in the C of the library): those that the export functions take or return, and those that the members of these give C in turn.  
<sub>línea 666</sub>

`function addHandles(t: Type, out: String[*] in default): void`
<sub>línea 695</sub>

`public function handleClasses(): String[*]`  
The classes C knows as handles, by the names C and Larimar see (without their module).  
<sub>línea 702</sub>

### class `LibraryMember`
A method or a field of a class that a library gives C: <prefix>_<Class>_<name>(handle, ...).

`function crosses(t: Type, field: bool): bool`  
What can go to C from a member: what an export function takes (a field: not a class, which it keeps).  
<sub>línea 718</sub>

`function memberProblem(m: MethodInfo): String`  
Why a member of a class does not go to C ("" when it goes).  
<sub>línea 724</sub>

`public function libraryMembers(cls: String in default): LibraryMember[*]`  
The members of a class that go to C: its fields and methods (and its parents'), the most derived ones.  
<sub>línea 744</sub>

`public function memberSkips(cls: String in default): String[*]`  
The members of a class that do not go to C, with why: the .lar says it.  
<sub>línea 758</sub>

`function methodsOf(cls: String in default): MethodInfo[*]`  
The instance methods of a class and its parents, each one by its most derived definition.  
<sub>línea 771</sub>

`function resources(out: StringBuilder): void`  
Resources (extern type X released by f): a value lives in a cell of the memory it was made in, with its state; the memory releases it when it is freed, unless release(x) already did.  
<sub>línea 789</sub>

`function shortName(n: String): String`  
A name without its module prefix: std__net__Socket -> Socket.  
<sub>línea 835</sub>

`function sectionOf(out: StringBuilder, title: String, content: StringBuilder): void`
<sub>línea 840</sub>

`public function section(out: StringBuilder, title: String): void`
<sub>línea 846</sub>

`function bodyText(body: String in default): String`  
A C body as it was written, indented once (its closing line's indentation does not count).  
<sub>línea 853</sub>

`function stripIndent(code: String in default): String`  
Like Java's stripIndent().strip(): removes the common indentation and the blank lines around.  
<sub>línea 861</sub>

`public function classesByDepth(): ClassInfo[*]`
<sub>línea 884</sub>

---

## codegen.gen.callbacks

`src/codegen/gen/callbacks.lar` · 123 líneas · 6 funciones
codegen.gen.callbacks: a function of the program that a library takes, on the library's side.

The library writes a parameter of a function type (handler: (Request) -> String) and calls it like any
function. C gives two things for it: a function and a void*, its own data, that the function gets back on
each call. This module turns those two into a function of Larimar's:

callbackC       the C type of the function C gives:   R (*name)(A..., void* data)
a text is not returned: it is left in one more argument, where the library says
->  void (*name)(A..., void* data, void* out)
callbackValue   the closure made of the two: its env holds them (RtCCallback), and its function is
callbackThunk   lm_callback_<id>: the arguments as C takes them, C's function called, its result back
- a text goes as a char* ended by zero, for the time of the call
- an object of the library goes as a handle on the stack: C uses it, and cannot keep it
- a text C gives is made, by <prefix>_give, in the memory the library's caller chose

The other pieces:
semantics/analyzer/declarations.lar   libraryCallback: which function types cross; 'in' on that parameter
codegen/gen/types.lar                 exportBody, memberBody: the C function, with the two parameters
codegen/gen/library.lar               the .h (its typedef) and the .lar (a native type with a Context)
std/runtime/memory.lar, string.lar    RtCCallback; RtTextOut, where a text is left
and on the side of the program that uses the library (any native function that takes a callback):
codegen/expressions/calls.lar         trampoline: the C function that calls the program's lambda
semantics/expressions/calls.lar       what the lambda uses lives as long as who keeps it

`public function callbackC(t: Type, name: String): String`  
A function of C's as a parameter: R (*name)(A..., void*), the void* being the one given with it.  
<sub>línea 31</sub>

`function callbackThunk(t: Type): String`  
What makes a function of C's a function of Larimar's: the function a closure of that type runs, which calls C's with the arguments as C takes them (a text, ended by a zero, for the time of the call) and with its void*.  
<sub>línea 47</sub>

`public function callbackValue(t: Type, x: String): String`  
The closure a function of C's and its void* make: `x` is the function, `x_data` the void*.  
<sub>línea 85</sub>

`function callbackTypes(): Type[*]`  
The function types that the export functions and the methods of the library's classes take, each once.  
<sub>línea 90</sub>

`public function callbackThunks(): String`  
The thunks of all of them.  
<sub>línea 110</sub>

`public function takesTextFunctions(): bool`  
Does a function or a method of the library take a function that gives a text? (<prefix>_give is for those.)  
<sub>línea 117</sub>

---

## codegen.gen.classes

`src/codegen/gen/classes.lar` · 345 líneas · 28 funciones
codegen.gen.classes: classes, interfaces and closures in C; globals and the entry point.

`function errParam(throwsOut: bool): String`
<sub>línea 14</sub>

`public function returnsData(ret: Type): bool`  
Returning something that points to memory: the function creates it in the memory of the call.  
<sub>línea 19</sub>

`public function params(ps: Symbol[*], memParams: bool[*]): String`
<sub>línea 21</sub>

`public function functionHeader(f: FunctionInfo): String`
<sub>línea 29</sub>

`public function methodName(m: MethodInfo): String`
<sub>línea 40</sub>

`public function methodHeader(m: MethodInfo, isStructMethod: bool): String`
<sub>línea 51</sub>

`public function nativeMethodHeader(m: MethodInfo): String`
<sub>línea 64</sub>

`public function lambdaHeader(l: LambdaInfo): String`
<sub>línea 71</sub>

`public function paramCTypes(m: MethodInfo in default): String[*]`  
The C parameters after self: the memory of the call first when it returns data.  
<sub>línea 80</sub>

`public function vtableStruct(out: StringBuilder, c: ClassInfo in default): void`
<sub>línea 89</sub>

`public function vtableInit(concrete: ClassInfo in default, level: ClassInfo): String`
<sub>línea 106</sub>

`public function dispatchName(intro: String, m: MethodInfo): String`
<sub>línea 121</sub>

`function argsDecl(pt: String[*], throwsOut: bool): String`
<sub>línea 123</sub>

`function argsPass(n: int32, throwsOut: bool): String`
<sub>línea 130</sub>

`function retWord(t: Type): String`
<sub>línea 141</sub>

`public function dispatchHelper(out: StringBuilder, c: ClassInfo, m: MethodInfo in default): void`
<sub>línea 145</sub>

`public function interfaceTableStruct(out: StringBuilder, i: InterfaceInfo in default): void`
<sub>línea 152</sub>

`public function ifaceCallName(i: InterfaceInfo, m: MethodInfo): String`
<sub>línea 164</sub>

`public function interfaceCallHelper(out: StringBuilder, i: InterfaceInfo, m: MethodInfo in default): void`
<sub>línea 166</sub>

`public function interfaceImplementations(out: StringBuilder): void`  
For each class that declares `implements I`: thunks plus a table.  
<sub>línea 174</sub>

`public function samTable(out: StringBuilder, i: InterfaceInfo in default): void`
<sub>línea 192</sub>

`public function samThunk(out: StringBuilder, i: InterfaceInfo in default): void`
<sub>línea 200</sub>

`public function closureCallHelper(out: StringBuilder, ft: Type): void`
<sub>línea 207</sub>

`public function collectionHelpers(out: StringBuilder, t: Type): void`
<sub>línea 223</sub>

`public function initGlobals(): String`
<sub>línea 257</sub>

`public function mainWrapper(): String`
<sub>línea 279</sub>

`public function clonePrototypes(): String`
<sub>línea 322</sub>

`public function classClone(out: StringBuilder, c: ClassInfo in default): void`
<sub>línea 328</sub>

---

## codegen.gen.library

`src/codegen/gen/library.lar` · 364 líneas · 17 funciones
codegen.gen.library: a library's interface: its .h (C) and its .lar (Larimar), from its export functions.

`public function plainName(n: String): String`  
The name a class or function has in Larimar's own code, without its module (the linker's a__b).  
<sub>línea 16</sub>

`public function exports(): FunctionInfo[*]`  
The export functions of the library, in the order they are declared.  
<sub>línea 22</sub>

`public function libraryProblems(): String[*]`  
What is wrong with the library's interface (two exports or classes with the same name): one message each.  
<sub>línea 31</sub>

`function callbackTypedef(owner: String, param: String, t: Type, lives: String, p: String): String`  
In the .h: the type of a function of yours that `owner` (a function or a method of the library) takes.  
<sub>línea 56</sub>

`function bindingCallbackType(name: String, t: Type): String`  
In the .lar: the same type, which only the compiler names. A thread safe one is checked for other threads.  
<sub>línea 79</sub>

`function callbackName(f: FunctionInfo, i: int32): String`  
The C type of a function a library takes, in its .h: <export name>_<parameter>.  
<sub>línea 87</sub>

`function bindingCallback(f: FunctionInfo, i: int32): String`  
The same in the .lar, where only the compiler names it.  
<sub>línea 90</sub>

`function docAbove(encoded: int32): String[*]`  
The doc comment (a doc block or // lines) right above a declaration, one line each.  
<sub>línea 93</sub>

`function docBlock(lines: String[*], indent: String): String`  
A doc comment for the .h or the .lar ("" when there is none).  
<sub>línea 123</sub>

`function headerType(t: Type, result: bool): String`  
A type of an export function in the library's .h.  
<sub>línea 134</sub>

`function headerPrototype(f: FunctionInfo): String`  
The C prototype of an export function in the .h.  
<sub>línea 141</sub>

`function resultNote(f: FunctionInfo): String`  
What the .h says a result is, after its doc comment.  
<sub>línea 157</sub>

`function typeNote(r: Type): String`
<sub>línea 159</sub>

`public function libraryHeader(name: String, version: String, kind: String, hash: String, made: String): String`  
The library's header for C: its handles, its export functions, how to free what they give.  
<sub>línea 171</sub>

`function bindingClass(cls: String in default, p: String): String`  
A class of the library in its .lar: a resource (the handle) with its fields as `native let` and its methods as `native function`, so a program uses it as in the library: c.add("x"), c.words.  
<sub>línea 253</sub>

`function bindingType(t: Type): String`  
A type of an export function in the library's .lar.  
<sub>línea 309</sub>

`public function libraryModule(name: String, version: String, kind: String, made: String): String`  
The library's module for Larimar: native declarations of its export functions, with the C names of the .h. A text is copied into the caller's memory and freed; a class is a resource that gives the handle back.  
<sub>línea 318</sub>

---

## codegen.gen.statements

`src/codegen/gen/statements.lar` · 650 líneas · 31 funciones
codegen.gen.statements: bodies and statements, switch included.

`function usesErrors(body: Stmt[*] in default): bool`
<sub>línea 23</sub>

`public function body(stmts: Stmt[*] in default, ret: Type in default, throwsOut: bool, lambda: LambdaInfo? in default, ps: Symbol[*], lock: String, declLine: int32): String`  
lock != "": a method of a synchronized class, locked for its whole run (unlocked on every exit).  
<sub>línea 44</sub>

`public function endsWithJump(stmts: Stmt[*]): bool`
<sub>línea 93</sub>

`function emitCleanups(b: Block): void`
<sub>línea 99</sub>

`public function block(stmts: Stmt[*] in default): void`
<sub>línea 107</sub>

`function bracedBlock(stmts: Stmt[*] in default): void`  
A block between braces, one level in.  
<sub>línea 117</sub>

`public function cleanupsUntil(stop: Block): void`  
Emits the cleanups of every block from the innermost up to `stop` (inclusive).  
<sub>línea 124</sub>

`function anyCleanups(stop: Block): bool`
<sub>línea 134</sub>

`public function stmt(s: Stmt in default): void`  
A statement; what it creates without a place lives in its temporary memory, freed when it ends.  
<sub>línea 146</sub>

`public function openMemory(stmts: Stmt[*] in default): void`  
A block whose variables hold data gets its memory, freed when the block ends.  
<sub>línea 178</sub>

`public function tempMem(): String`  
The current statement's temporary memory (declared before it the first time it is used).  
<sub>línea 186</sub>

`function stmtInner(s: Stmt in default): void`
<sub>línea 196</sub>

`function assign(s: AssignStmt in default): void`
<sub>línea 228</sub>

`function placeParts(target: Expr in default, parts: Expr[*] in default): void`  
The parts of a place that are computed, in order: the object and the index of a[i], the object of a.f. An object that is a value (a struct, a T[N]) is not copied: its own place is looked into.  
<sub>línea 252</sub>

`function placeObject(o: Expr in default, parts: Expr[*] in default): void`
<sub>línea 263</sub>

`function assignTo(s: AssignStmt in default, target: Expr in default): void`
<sub>línea 272</sub>

`function varDecl(v: VarDecl in default): void`
<sub>línea 294</sub>

`public function ret(r: ReturnStmt in default): void`
<sub>línea 319</sub>

`function ifStmt(i: IfStmt in default): void`
<sub>línea 337</sub>

`function whenStmt(i: IfStmt in default): void`  
An if for platforms (IfStmt.platform): C's #if / #elif / #else / #endif, with no braces, so what a branch declares stays for the code after it. Every branch is written (the C compiler keeps one); what a branch leaves to free at the end of the block is freed only where that branch is kept.  
<sub>línea 357</sub>

`function keptWhen(c: String, above: String[*]): String`  
When the C compiler keeps a branch: its condition, and none of the ones above.  
<sub>línea 378</sub>

`function whenBranch(stmts: Stmt[*] in default, kept: String): void`
<sub>línea 383</sub>

`function loopBlockOpen(): Block`  
Opens the block of a loop body.  
<sub>línea 393</sub>

`function loopBody(body: Stmt[*] in default, b: Block in default): void`
<sub>línea 400</sub>

`function whileStmt(w: WhileStmt in default): void`
<sub>línea 407</sub>

`function indexVar(ix: Symbol? in default, value: String): void`  
`int32_t i = idx;` for the index variable of a for, if it has one.  
<sub>línea 425</sub>

`function forStmt(f: ForStmt in default): void`
<sub>línea 431</sub>

`public function throwStmt(t: ThrowStmt in default): void`
<sub>línea 508</sub>

`public function propagate(): void`  
Sends the current error to the innermost try, or to the caller.  
<sub>línea 517</sub>

`function tryStmt(t: TryStmt in default): void`
<sub>línea 533</sub>

`public function switchCode(sw: SwitchExpr in default, isExpr: bool): String`
<sub>línea 573</sub>

---

## codegen.gen.types

`src/codegen/gen/types.lar` · 375 líneas · 23 funciones
codegen.gen.types: the C of the types of a program.

`public function externPrototype(f: FunctionInfo in default): String`  
C functions receive String as a NUL-terminated const char*.  
<sub>línea 17</sub>

`public function externDefinition(f: FunctionInfo in default): String`  
The header of the C function of a C body, with its parameters named as in Larimar (a T[] is name and name_length).  
<sub>línea 38</sub>

`public function larInC(code: String): String`  
ccode with lar"name" (the linker gave the linked name): the C name of that function, type or global.  
<sub>línea 57</sub>

`public function larPrototypes(code: String, out: StringBuilder): void`  
The prototypes of the Larimar functions a ccode names (those with C types the runtime already has).  
<sub>línea 75</sub>

`function plainSig(sig: Type): bool`  
Only numbers, bool, String and void: C types the runtime declares before any ccode.  
<sub>línea 90</sub>

`function cNameOf(name: String): String`
<sub>línea 99</sub>

`public function isCName(n: String): bool`  
A plain C name (a function a prototype can declare), not C text.  
<sub>línea 112</sub>

`public function externCType(t: Type): String`
<sub>línea 120</sub>

`public function exportHeader(f: FunctionInfo, early: bool): String`  
export function: the C function C code calls (C types), which calls the Larimar one.  
<sub>línea 128</sub>

`public function isHandle(t: Type): bool`  
A class of a library, as C sees it: a handle (its object, and the memory a result of C's lives in).  
<sub>línea 145</sub>

`public function exportBody(f: FunctionInfo): String`  
The body of an export function: C's values become Larimar's, the Larimar function runs, and its result goes to C: a text as a copy that C frees (malloc), an object of a library as a new handle.  
<sub>línea 151</sub>

`function fromC(t: Type, x: String, fn: String, param: String): String`  
A value of C as Larimar's: a text, a text or null, the object of a handle.  
<sub>línea 165</sub>

`function callToC(callee: String, recv: String, xs: String[*], r: Type): String`  
The statements that call `callee` (with `recv` first, when it is a method) and give C its result: a result with data is made in a memory of the call (a text, copied for C) or of a new handle (an object).  
<sub>línea 182</sub>

`function toC(t: Type, x: String): String`  
A Larimar value as C receives it: a text as a copy it frees (NULL for null).  
<sub>línea 207</sub>

`public function memberBody(m: LibraryMember): String`  
A member of a class, for C: a method through its vtable (a subclass's runs), or a field read.  
<sub>línea 214</sub>

`function exportParam(f: FunctionInfo, i: int32): String`
<sub>línea 242</sub>

`function abiType(t: Type, early: bool): String`  
A type as C code sees it. Early (before the ccode): an opaque extern type is still void*.  
<sub>línea 245</sub>

`public function earlyExport(f: FunctionInfo): bool`  
Its prototype can go before the ccode: numbers, bool, const char* and opaque extern types only.  
<sub>línea 252</sub>

`function plainC(t: Type): bool`
<sub>línea 260</sub>

`function cStruct(t: Type): bool`  
A C struct (extern type X = struct { ... }): C defines it, Larimar does not.  
<sub>línea 268</sub>

`public function forward(out: StringBuilder, t: Type): void`
<sub>línea 274</sub>

`public function define(out: StringBuilder, t: Type): void`
<sub>línea 290</sub>

`public function envField(s: Symbol): String`
<sub>línea 374</sub>

---

## codegen.prune

`src/codegen/prune.lar` · 463 líneas · 21 funciones
codegen.prune: only the C the program reaches, of what it generates and of the runtime.

The C is cut into pieces: the generated program into declarations (a function, a type, a helper, a
prototype, a global), the runtime into paragraphs (blank lines outside braces and #if blocks; each
#include is one). A piece is kept when it defines a name that a kept piece uses. For the program, the
roots are main, the export functions, and what the program wrote in C itself (cinclude, ccode), which
stays whole; the ccode of the standard library ("ccode (std)") is cut like the rest. For the runtime,
the roots are the names the pruned program uses; #ifdef RT_THREADS and #ifdef RT_FILES are decided here.

The runtime itself is C, in the ccode of std/runtime/*.lar (read in the order of runtimeFiles): editing
it does not change the compiler, nor the bootstrap.

### class `Piece`
A piece of C: a declaration of the program, a paragraph of the runtime, or a heading over them.

`function rootSection(title: String): bool`  
Sections written by the program itself: they stay whole, and what they use is kept.  
<sub>línea 33</sub>

`public function prune(program: String, roots: String[*]): String`  
The generated program without what it does not reach. roots: main and the export functions.  
<sub>línea 38</sub>

`function flush(pieces: Piece[*], lines: String[*], root: bool): void`  
The lines gathered so far become a piece.  
<sub>línea 77</sub>

`function runtimeC(file: String): String`  
The C of a runtime file: between "ccode {" and the last "}" (each file is that one ccode).  
<sub>línea 90</sub>

`function runtimeSource(): String`
<sub>línea 98</sub>

`function headerNames(i: int32): String`
<sub>línea 122</sub>

`public function selectRuntime(program: String, threads: bool, files: bool, allHeaders: bool): String`  
The runtime the program needs, in the runtime's order. allHeaders: the program has its own C (ccode, native), which may count on the standard headers.  
<sub>línea 137</sub>

`function paragraph(pieces: Piece[*], lines: String[*]): void`  
The lines gathered so far become a paragraph: a heading when it is only a comment.  
<sub>línea 174</sub>

`function includePiece(line: String): Piece`  
#include <stdio.h>: it defines what that header gives.  
<sub>línea 184</sub>

`function resolve(text: String, threads: bool, files: bool): String[*]`  
Keeps the lines that apply: #ifdef RT_THREADS / RT_FILES (and their #else) are decided; other #if stay.  
<sub>línea 196</sub>

`function reach(pieces: Piece[*], wanted: String[*]): bool[*]`  
For each piece, whether it is kept: a root, or one that defines a name wanted or used by a kept one.  
<sub>línea 250</sub>

`function kept(pieces: Piece[*], keep: bool[*], i: int32): bool`  
A piece that is kept; a heading goes with what is kept under it.  
<sub>línea 293</sub>

`function describe(p: Piece): void`  
What a piece defines (at its top level) and every name it uses.  
<sub>línea 304</sub>

`function statementEnd(toks: String[*], from: int32): int32`  
Where the statement that starts at `from` ends: its `;` outside braces (toks.length if none).  
<sub>línea 358</sub>

`function define(p: Piece, defined: Any, name: String): void`
<sub>línea 368</sub>

`function unique(toks: String[*]): String[*]`  
The names of some tokens, each once.  
<sub>línea 375</sub>

`function names(c: String): String[*]`  
The names a C text mentions, each once (comments, strings and character literals left out).  
<sub>línea 387</sub>

`public function braceDelta(ln: String): int32`  
The braces a line opens minus those it closes (strings and comments left out).  
<sub>línea 395</sub>

`public function isName(t: String): bool`
<sub>línea 429</sub>

`function letter(c: byte): bool`
<sub>línea 431</sub>

`public function tokens(c: String): String[*]`  
C tokens: names, numbers and single punctuation characters; comments, strings and characters are skipped.  
<sub>línea 434</sub>

---

## project.cc

`src/project/cc.lar` · 146 líneas · 11 funciones
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
<sub>línea 46</sub>

### class `CCompiler`
The C compiler of a build: the program and the arguments that go right after it.

`public function bundledTcc(home: String): String`  
The tcc that comes with Larimar on Linux and Windows ($LARIMAR_HOME/toolchain/tcc), or "".  
<sub>línea 65</sub>

`function tccCompiler(exe: String): CCompiler`  
The bundled tcc with what it needs: on Linux it links statically with the musl next to it.  
<sub>línea 71</sub>

`public function systemCompiler(): String`  
The system's C compiler: cc, gcc or clang (on Windows gcc, clang or cc), or "" when there is none.  
<sub>línea 83</sub>

`public function chooseCompiler(home: String, wanted: String, script: bool, tls: bool, problem: String[*]): CCompiler?`  
The C compiler for a build. `wanted` is what was asked for (--cc, [c] compiler, CC; "" for none, and "tcc" is the bundled one when the system has no tcc). A script (larimar file.lar) prefers the bundled tcc, which starts fast; a project the system's, which optimizes. A program with TLS needs the system's: the bundled tcc cannot build it. null when there is none, and `problem` says what to install.  
<sub>línea 98</sub>

`public function installHint(): String`  
The command that installs a C compiler here.  
<sub>línea 130</sub>

---

## project.libraries

`src/project/libraries.lar` · 246 líneas · 8 funciones
project.libraries: the libraries written in Larimar, as larimar build makes them and as the programs
that use them find them. A library is a folder, a package, that larimar build fills:

textkit.interface       its name, version, type, the interface hash, and what goes with it
textkit.lar             for Larimar: its export functions as native declarations (import textkit)
textkit.h               for C: the same functions, its handles, how to free what they give
textkit.c               the library, translated to C: it is compiled with the program that uses it
c/...                   the C the library brings (the sources and include_paths of its [c])

That is type "package", the default: the same folder serves every platform. With --static or --dynamic the
library is compiled here instead (libtextkit.a; libtextkit.so, libtextkit.dylib, textkit.dll), for a C program.
A Larimar program names the package in [packages] of its larimar.toml: its .lpk, the same folder in one
file (project.lpk), or the folder.

The interface hash is the first 8 hex digits of the SHA-256 of the .lar, and the library has it inside
("larimar-interface:<hash>"). A program builds only when the three agree: a .lar edited by hand, or
copied from another build, is found out before the C compiler runs.

### class `LarimarLibrary`
A package the project names in [packages]: what it adds to the program's build.

`public function interfaceHash(module: String): String`  
The interface hash of a library: the first 8 hex digits of the SHA-256 of its .lar.  
<sub>línea 42</sub>

`public function libraryFile(name: String, kind: String): String`  
The file of a library: <name>.c in a package, lib<name>.a, or the dynamic one of this platform.  
<sub>línea 48</sub>

`public function interfaceMarker(hash: String): String`  
The marker the library has inside, with its hash.  
<sub>línea 56</sub>

`public function larimarLibraries(dir: String, config: Any, verify: bool, problems: String[*]): LarimarLibrary[*]`  
The libraries of [packages] (name = "folder"): each folder has the <name>.interface that larimar build wrote. With `verify`, the interface is checked against the .lar and the library (larimar build); without it, only found (the editor).  
<sub>línea 63</sub>

`function strings(section: Any, key: String, into: String[*]): void`  
The strings of a list of a section, added to `into` (nothing when there is no such list).  
<sub>línea 104</sub>

`function read(name: String, folder: String, verify: bool, problems: String[*]): LarimarLibrary?`  
A library's folder, read through its .interface (and checked, with `verify`).  
<sub>línea 114</sub>

`function fileHas(path: String, marker: String): bool throws IoError`  
Whether a file has the marker of an interface in its bytes (read in pieces: a library has zeros, which a String of std cannot hold). The marker's first byte is not in the rest of it, so one pass finds it.  
<sub>línea 188</sub>

`public function interfaceText(name: String, version: String, kind: String, prefix: String, hash: String, made: String, links: String[*], sources: String[*], includePaths: String[*], objects: String[*], packages: String[*]): String`  
The .interface of a library that larimar build writes.  
<sub>línea 214</sub>

---

## project.lpk

`src/project/lpk.lar` · 197 líneas · 13 funciones
project.lpk: a package in one file. <name>.lpk is the folder of a package (project.libraries) as a zip
without compression: any zip tool opens it, and reading it needs no decompressor. larimar build of a
library writes it next to the folder; a program that names it in [packages] gets it unpacked in its
build folder, once for each .lpk (its size and time are kept in a file next to what was unpacked).

### class `Bytes`
Bytes, written and read as zip does: numbers with their lowest byte first.

- `function length(): int32`
  <sub>línea 19</sub>

- `function number(value: uint32, width: int32): void`  
  A number in `width` bytes.  
  <sub>línea 22</sub>

- `function text(s: String): void`
  <sub>línea 30</sub>

- `function add(other: Bytes): void`
  <sub>línea 34</sub>

- `function read(at: int32, width: int32): int32`  
  The number in `width` bytes at `at`.  
  <sub>línea 39</sub>

- `function part(at: int32, count: int32): Bytes`  
  `count` bytes from `at`.  
  <sub>línea 46</sub>

- `function crc(): uint32`  
  The CRC-32 of zip.  
  <sub>línea 53</sub>

- `function header(signature: uint32, name: String, crc: uint32, size: int32): void`  
  The header of a file: the one before its bytes (LOCAL), or the start of its entry in the directory (CENTRAL).  
  <sub>línea 63</sub>

`public function pack(folder: String, lpk: String): void throws IoError`  
Writes the files of a folder (all of them, with those of its folders) into a .lpk.  
<sub>línea 81</sub>

`public function unpack(lpk: String, folder: String): String`  
Unpacks a .lpk into a folder, unless that was already done for this very file: "" when it is there, or what is wrong with the file.  
<sub>línea 120</sub>

`function clear(folder: String): void throws IoError`  
Deletes what a folder has.  
<sub>línea 163</sub>

`function filesOf(folder: String, prefix: String, into: String[*]): void throws IoError`  
The files under a folder, as paths from it with '/'.  
<sub>línea 172</sub>

`function contents(path: String): Bytes throws IoError`  
The bytes of a file.  
<sub>línea 184</sub>

---

## project.testing

`src/project/testing.lar` · 483 líneas · 27 funciones
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
<sub>línea 59</sub>

`public function hasMain(source: String in default): bool`  
Whether the file declares a main of its own.  
<sub>línea 75</sub>

`public function withMain(source: String, tests: TestFunction[*]): String`  
The file with a main added: `program <name>` runs that test and ends with 0 (it passed), 1 (a check failed), 3 (it was skipped) or 2 (no test has that name). std.test is imported on the first line, so the lines of the file do not move and its errors keep their line numbers.  
<sub>línea 88</sub>

`public function runTests(args: String[*], s: TestSettings in default): int32`
<sub>línea 142</sub>

`function collect(dir: String, into: String[*]): void`  
The .lar files of a folder and its folders.  
<sub>línea 227</sub>

`function sortTexts(xs: String[*]): void`  
Sorts texts by their bytes (the order of the files every time).  
<sub>línea 241</sub>

`function before(a: String, b: String): bool`
<sub>línea 255</sub>

`function hasTestFunctions(source: String): bool`
<sub>línea 265</sub>

`function base(shown: String): String`  
build/test/<the file's path, with '_' for the folders>: where the files of one test go.  
<sub>línea 273</sub>

`function selected(shown: String, name: String): bool`  
Whether a test runs: the names given with --test, else the ones --only matches ("": the file itself).  
<sub>línea 280</sub>

`function list(shown: String, tests: TestFunction[*]): void`  
--list: the tests of a file.  
<sub>línea 286</sub>

`function found(shown: String, name: String, line: int32): void`
<sub>línea 292</sub>

`function lineOf(name: String): int32`  
The line of a test of the file that runs (1 for the file itself).  
<sub>línea 301</sub>

`function report(shown: String, name: String, result: String, message: String): void`  
A result: a line for a person (ok, FAIL, skip), or a JSON object with --json.  
<sub>línea 306</sub>

`function pass(shown: String, name: String): void`
<sub>línea 326</sub>

`function failed(shown: String, name: String, problem: String): void`
<sub>línea 331</sub>

`function skip(shown: String, name: String, why: String): void`
<sub>línea 336</sub>

`function fileFailed(shown: String, problem: String): void`  
A file of tests that did not get to run (it did not compile): for a person, one failure; with --json, each of its tests fails with that message, so an editor marks them.  
<sub>línea 345</sub>

`function read(path: String): String`
<sub>línea 355</sub>

`function head(text: String, count: int32): String`  
The first lines of a text (what a failure shows).  
<sub>línea 360</sub>

`function compileC(cFile: String, exe: String): String`  
Compiles the C of a test into an executable; "" when it worked, else what the C compiler said.  
<sub>línea 374</sub>

`function runProgram(exe: String, args: String[*], outFile: String, errFile: String): int32`  
Runs a program, its output to <base>.out and <base>.err; gives its exit code.  
<sub>línea 406</sub>

`function memoryError(err: String): bool`
<sub>línea 414</sub>

`function memoryReport(err: String): String`  
The lines of a sanitizer's report that say what happened.  
<sub>línea 419</sub>

`function skipText(out: String): String`  
What a skipped test said: the text after "skipped: ".  
<sub>línea 432</sub>

`function exeName(b: String): String`
<sub>línea 439</sub>

`function runTestFile(file: String, shown: String, source: String): void`  
A file of test functions: compiled once with a main, then each test runs alone.  
<sub>línea 442</sub>

---

## editor.dap

`src/editor/dap.lar` · 1456 líneas · 69 funciones
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

### class `DapUnix implements UnixPlatform`
Dap's C on Unix.

### class `DapWindows implements WindowsPlatform`
Dap's C on Windows.

`native function lm_dap_spawn(path: String): bool`
<sub>línea 327</sub>

`native function lm_dap_kill(): void`
<sub>línea 328</sub>

`native function lm_dap_fill(ms: int32): void`
<sub>línea 329</sub>

`native function lm_dap_eof(which: int32): bool`
<sub>línea 330</sub>

`native function lm_dap_take(m: byte[*], which: int32): String`
<sub>línea 331</sub>

`native function lm_dap_took(): bool`
<sub>línea 332</sub>

`native function lm_dap_write(which: int32, body: String, length: int32): void`
<sub>línea 333</sub>

`native function lm_dap_handle(kind: int32, frame: int32, ref: int32, expr: String, type: String): int32`
<sub>línea 334</sub>

`native function lm_dap_clear(): void`
<sub>línea 335</sub>

`native function lm_dap_h_kind(id: int32): int32`
<sub>línea 336</sub>

`native function lm_dap_h_frame(id: int32): int32`
<sub>línea 337</sub>

`native function lm_dap_h_ref(id: int32): int32`
<sub>línea 338</sub>

`native function lm_dap_h_expr(id: int32): String`
<sub>línea 339</sub>

`native function lm_dap_h_type(id: int32): String`
<sub>línea 340</sub>

`function log(text: String): void`
<sub>línea 371</sub>

`function withNumber(json: String, key: String, value: int32): String`  
A JSON text with the top-level numeric field `key` set to `value` (added when missing).  
<sub>línea 378</sub>

`function toEditorRaw(body: String): void`
<sub>línea 409</sub>

`function emit(body: String): void`  
A message to the editor with our sequence number.  
<sub>línea 412</sub>

`function respond(req: Any, body: String): void`
<sub>línea 418</sub>

`function respondError(req: Any, message: String): void`
<sub>línea 424</sub>

`function output(text: String): void`
<sub>línea 430</sub>

`function parse(text: String): Any`
<sub>línea 434</sub>

`function sendBackend(command: String, args: String): int32`  
Sends a request of ours to the backend; returns its seq.  
<sub>línea 443</sub>

`function call(command: String, args: String): String`  
A request of ours to the backend, and its response (as JSON text). What arrives meanwhile from the backend (events, answers to forwarded requests) goes on to the editor; the editor's messages wait.  
<sub>línea 455</sub>

`function eval(frame: int32, expr: String): String?`  
A C expression's value in a frame, or null when lldb cannot evaluate it.  
<sub>línea 474</sub>

`function evalInt(frame: int32, expr: String): int64?`
<sub>línea 480</sub>

`function evalAddress(frame: int32, expr: String): int64?`
<sub>línea 486</sub>

`function command(frame: int32, text: String): String`  
An lldb command in a frame; its output.  
<sub>línea 498</sub>

`function tableOf(v: Any): Any`  
A table of the debug map (or an empty one when it is missing).  
<sub>línea 504</sub>

`function atMost(n: int64, limit: int32): int32`
<sub>línea 511</sub>

`function hexValue(s: String): int64`
<sub>línea 513</sub>

`function readBytes(frame: int32, address: int64, count: int32): String?`  
`count` bytes at an address, as text (UTF-8).  
<sub>línea 524</sub>

`function readCString(frame: int32, expr: String): String?`  
A C string (a class's name) at the address an expression gives.  
<sub>línea 541</sub>

### class `Shown`
What the editor shows for one value: its text, and its children (a handle) when it has them.

`function typeEntry(name: String): Any`
<sub>línea 562</sub>

`function typeText(t: Any): String`
<sub>línea 564</sub>

`function quoteText(s: String): String`
<sub>línea 581</sub>

`function stringValue(frame: int32, expr: String): String?`  
The text of a String value at expr (an RtString).  
<sub>línea 584</sub>

`function classOfObject(frame: int32, pointer: String): String`  
The class (C name) of the object at a pointer expression, or "".  
<sub>línea 597</sub>

`function show(frame: int32, expr: String, t: Any, preview: bool): Shown?`  
How the editor shows the value of `expr` (a C expression) of type `t`. preview: a short text only.  
<sub>línea 602</sub>

`function showAny(frame: int32, expr: String, preview: bool, s: Shown): Shown?`
<sub>línea 758</sub>

`function fieldsPreview(frame: int32, entry: Any, access: String, preview: bool, display: String): String`  
Point {x=1, y=2}: the first scalar fields, read with `access` + their C path.  
<sub>línea 787</sub>

`function variableJson(name: String, s: Shown, evaluateName: String): String`  
The JSON of one variable for the editor.  
<sub>línea 810</sub>

`function children(id: int32, start: int32, count: int32): String[*]`  
The children of a value handle.  
<sub>línea 817</sub>

`function fieldVariables(frame: int32, fields: Any, access: String, out: String[*]): void`
<sub>línea 870</sub>

`function hasFunction(cName: String): bool`
<sub>línea 885</sub>

`function functionEntry(cName: String): Any`
<sub>línea 886</sub>

`function localVariables(frame: int32): String[*]`  
The Larimar variables of a frame.  
<sub>línea 889</sub>

`function globalVariables(frame: int32): String[*]`
<sub>línea 924</sub>

### class `Resolved`

`function resolvePath(frame: int32, text: String): Resolved`
<sub>línea 944</sub>

`function splitPath(text: String): String[*]`  
"a.b[2].c" -> ["a", ".b", "[2]", ".c"]; [] when it is not a path.  
<sub>línea 986</sub>

`function isNameByte(c: byte): bool`
<sub>línea 1012</sub>

`function step(frame: int32, r: Resolved, part: String): bool`  
One step of a path: .field or [index].  
<sub>línea 1017</sub>

`function fromEditor(body: String): bool`
<sub>línea 1065</sub>

`function forward(body: String, msg: Any, args: String): void`  
Passes a request on to the backend (with new arguments when `args` is not "").  
<sub>línea 1102</sub>

`function capabilities(r: Any): String`
<sub>línea 1111</sub>

`function launchArguments(msg: Any): String`  
launch for lldb-dap: the program, and lldb set up for Larimar.  
<sub>línea 1125</sub>

`function loadMap(path: String): void`
<sub>línea 1144</sub>

`function functionBreakpoints(msg: Any): String`  
Function breakpoints by Larimar name: main -> user_main, Dog.bark -> Dog_bark.  
<sub>línea 1159</sub>

`function exceptionBreakpoints(msg: Any): void`
<sub>línea 1171</sub>

`function stackTrace(msg: Any): void`  
The call stack with Larimar names; the runtime's frames de-emphasized.  
<sub>línea 1195</sub>

`function scopes(msg: Any): void`
<sub>línea 1224</sub>

`function variables(msg: Any): void`
<sub>línea 1240</sub>

`function backendVariables(frame: int32, ref: int32): String[*]`  
lldb-dap's own variables (the C view), with our handles for their children.  
<sub>línea 1266</sub>

`function evaluate(body: String, msg: Any): void`  
The debug console, hovers and watches: Larimar paths here; the rest (C, lldb commands) to lldb.  
<sub>línea 1280</sub>

`function isPanicStop(msg: Any): bool`
<sub>línea 1313</sub>

`function exceptionInfo(msg: Any): void`  
The panic's message: the msg argument of rt_panic, at the top of the thread's stack.  
<sub>línea 1324</sub>

`function fromBackend(body: String, msg: Any): void`
<sub>línea 1337</sub>

`function findBackend(given: String): String`  
lldb-dap: the one given, $LARIMAR_LLDB_DAP, on the PATH, or Xcode's (xcrun).  
<sub>línea 1376</sub>

`public function serveDebugger(args: String[*]): int32`
<sub>línea 1401</sub>

---

## editor.docstore

`src/editor/docstore.lar` · 67 líneas · 11 funciones
editor.docstore: the texts of the documents open in the editor, by file path (larimar lsp).
They live in C memory (malloc), so a text can be freed when the editor sends a new one: the server
runs for hours and its documents change on every key. The linker reads a file from here when it is
open in the editor (with its changes not saved yet), and from the disk otherwise.

`native function lm_doc_set(path: String, text: String): void`
<sub>línea 25</sub>

`native function lm_doc_remove(path: String): void`
<sub>línea 41</sub>

`native function lm_doc_has(path: String): bool`
<sub>línea 48</sub>

`native function lm_doc_text(path: String): String`
<sub>línea 49</sub>

`native function lm_doc_count(): int32`
<sub>línea 50</sub>

`native function lm_doc_path(i: int32): String`
<sub>línea 51</sub>

`public function setDocument(path: String, text: String): void`  
Keeps (a copy of) the editor's text of a file.  
<sub>línea 54</sub>

`public function removeDocument(path: String): void`  
The editor closed the file: from now on it is read from the disk.  
<sub>línea 57</sub>

`public function document(path: String): String?`  
The editor's text of a file, or null when it is not open.  
<sub>línea 60</sub>

`public function documentCount(): int32`
<sub>línea 65</sub>

`public function documentPath(i: int32): String`
<sub>línea 66</sub>

---

## editor.ide

`src/editor/ide.lar` · 1503 líneas · 74 funciones
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

`function ofFunc(f: FunctionInfo in default): Target`
<sub>línea 361</sub>

`function ofMethod(m: MethodInfo in default): Target`
<sub>línea 365</sub>

`function ofField(f: FieldInfo in default): Target`
<sub>línea 369</sub>

`function ofVariant(e: EnumInfo in default, v: VariantInfo in default): Target`
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

`function funcParams(f: FunctionInfo): String[*]`
<sub>línea 530</sub>

`function methodParams(m: MethodInfo): String[*]`
<sub>línea 541</sub>

`function funcLabel(f: FunctionInfo): String`
<sub>línea 551</sub>

`function methodLabel(m: MethodInfo): String`
<sub>línea 557</sub>

`function detail(t: Target): String`  
The code shown on hover.  
<sub>línea 563</sub>

`function typeOfConst(c: ConstDecl): String`
<sub>línea 617</sub>

`function typeDetail(linked: String): String`
<sub>línea 619</sub>

`function cText(c: String): String`  
C's name or type as a native declaration writes it: a plain name (FILE*) as it is, anything else as c"...".  
<sub>línea 675</sub>

`function docAbove(index: int32, line: int32): String`  
The comment written right above a declaration (// lines or a doc block), as text.  
<sub>línea 689</sub>

### class `Place`
Where a target is declared: file index, line and the byte columns of its name.

`function placeOf(t: Target): Place`
<sub>línea 725</sub>

`function locationJson(p: Place): String`
<sub>línea 744</sub>

### class `Cursor`
The cursor: a file index, a line from 1 and a byte column.

`function cursorOf(path: String, line0: int32, char16: int32): Cursor`
<sub>línea 760</sub>

`public function hoverJson(path: String, line0: int32, char16: int32): String`  
Hover: the declaration, as code, and its comment.  
<sub>línea 769</sub>

`function ownerNote(t: Target): String`
<sub>línea 786</sub>

`public function definitionJson(path: String, line0: int32, char16: int32): String`  
Go to definition.  
<sub>línea 800</sub>

`public function referencesJson(path: String, line0: int32, char16: int32, withDecl: bool): String`  
Every place that names the same thing (with its declaration when `withDecl`).  
<sub>línea 809</sub>

`function refersTo(e: Expr, t: Target): int32`  
Whether an expression names the target: -1 no; else how its name is written (1 after a '.', 0 not, -1 any).  
<sub>línea 864</sub>

`public function symbolsJson(path: String): String`  
The symbols of a file: its declarations, with the members of its types inside.  
<sub>línea 909</sub>

`function symbolJson(name: String, kind: int32, encoded: int32, word: String, kids: String[*]): String`
<sub>línea 966</sub>

`function blockEnd(index: int32, line: int32): int32`  
The line where the block a declaration opens on `line` closes (the same line when it has none).  
<sub>línea 979</sub>

`public function prepareCompletion(path: String, line0: int32, char16: int32, signatureHelp: bool): void`  
Before analyzing for completion or signature help: the line being written does not compile yet, so in this process the document gets a line that does (the rest of the program stays as it is).  
<sub>línea 1028</sub>

`function probeStatement(text: String, before: String, chainStart: int32, indent: String): String`  
A line that compiles and has `chain.probe()`, so the analysis gives the type of what comes before the '.'; "" when the names alone answer (a module or a type before the '.': the program must still link).  
<sub>línea 1075</sub>

`function needsNoProbe(text: String, chain: String): bool`  
A module alias (import ... as chain) or a type name: completed from the names, without a probe.  
<sub>línea 1086</sub>

`function openParen(before: String): int32`  
The '(' still open before the cursor, or -1.  
<sub>línea 1095</sub>

`function commasAfter(before: String, open: int32): int32`
<sub>línea 1110</sub>

`function chainBefore(line: String, dot: int32): String`  
The expression that ends right before byte `dot` (a '.'): names, dots, calls and indexes.  
<sub>línea 1129</sub>

### class `Items`

`function add(items: Items, label: String, kind: int32, detailText: String, doc: String): void`
<sub>línea 1180</sub>

`public function completionJson(path: String, line0: int32, char16: int32): String`  
Completion, after prepareCompletion and the analysis.  
<sub>línea 1190</sub>

`function probeObject(index: int32): Expr?`  
The probe left by prepareCompletion: the object before the '.'.  
<sub>línea 1204</sub>

`function memberItems(items: Items, index: int32): void`
<sub>línea 1213</sub>

`function memberItem(items: Items, m: MethodInfo): void`  
A method, or a native let (read without parentheses).  
<sub>línea 1242</sub>

`function typeMembers(items: Items, t: Type): void`
<sub>línea 1250</sub>

`function docOf(encoded: int32): String`
<sub>línea 1310</sub>

`function nameItem(items: Items, name: String, linked: String): void`  
A name a file can see, by its name after linking.  
<sub>línea 1316</sub>

`function nameItems(items: Items, index: int32): void`
<sub>línea 1340</sub>

`function enclosingStart(index: int32, line: int32): int32`  
The line where the function or method around a line starts, or 0.  
<sub>línea 1364</sub>

`function closer(best: int32, index: int32, start: int32, line: int32): int32`
<sub>línea 1379</sub>

`public function signatureJson(path: String): String`  
The signature of the call being written, after prepareCompletion(..., true) and the analysis.  
<sub>línea 1387</sub>

`function methodOf(t0: Type, name: String): MethodInfo?`
<sub>línea 1442</sub>

`public function diagnosticsJson(requested: String): String`  
The errors of the analysis, per file: one { uri, diagnostics } per line, for every file of the program that is not part of std (so a file whose errors are fixed gets an empty list), and for any file with errors.  
<sub>línea 1474</sub>

---

## editor.lsp

`src/editor/lsp.lar` · 499 líneas · 29 funciones
editor.lsp: larimar lsp, the language server editors start (Language Server Protocol, JSON-RPC on stdin and
stdout, each message after a "Content-Length: N" header).

The server keeps the texts of the open documents (docstore.lar, freed when they change) and nothing
else. Each question (the errors of a file, hover, go to definition, ...) is answered by a new process:
a fork() of the server that links and analyzes the program with the editor's texts, writes its answer
to a pipe and ends. So an analysis never leaves memory behind, never sees the state of the one before,
and a crash only loses one answer. Where fork() does not exist (Windows), or with
LARIMAR_LSP_NO_FORK=1, the question goes to a new `larimarc lsp-worker` through two files.

The errors are computed when the editor stops typing (no message for a moment) for the file that
changed last, and published for every file of its program.

### class `LspUnix implements UnixPlatform`
Lsp's C on Unix.

### class `LspWindows implements WindowsPlatform`
Lsp's C on Windows.

`native function lm_lsp_fork(): int32`
<sub>línea 199</sub>

`native function lm_lsp_send(text: String, length: int32): void`
<sub>línea 200</sub>

`native function lm_lsp_quit(code: int32): void`
<sub>línea 201</sub>

`native function lm_lsp_receive(m: byte[*], pid: int32): String`
<sub>línea 202</sub>

`native function lm_lsp_attempt(): int32`
<sub>línea 203</sub>

`native function lm_lsp_waiting(ms: int32): bool`
<sub>línea 204</sub>

`native function lm_lsp_unbuffered(): void`
<sub>línea 205</sub>

`native function lm_lsp_set_pending(path: String): void`
<sub>línea 206</sub>

`native function lm_lsp_get_pending(): String`
<sub>línea 207</sub>

`native function lm_lsp_pid(): int32`
<sub>línea 208</sub>

`function readMessage(): String?`  
The next message's body, or null when the editor closed the input.  
<sub>línea 218</sub>

`function send(body: String): void`
<sub>línea 237</sub>

`function respond(id: String, result: String): void`
<sub>línea 243</sub>

`function respondError(id: String, code: int32, message: String): void`
<sub>línea 247</sub>

`function notify(method: String, params: String): void`
<sub>línea 251</sub>

`function log(text: String): void`
<sub>línea 255</sub>

`function capabilities(): String`
<sub>línea 257</sub>

`function docPath(msg: Any): String`  
The normalized path of a message's text document.  
<sub>línea 266</sub>

`public function serve(): int32`  
larimar lsp  
<sub>línea 278</sub>

`function publish(path: String): void`  
Publishes the errors of the program a file belongs to.  
<sub>línea 338</sub>

`function ask(body: String): String`  
The answer (JSON) to a message, from a new process.  
<sub>línea 347</sub>

`function answerInChild(body: String): String`  
In the forked process: analyze and answer.  
<sub>línea 365</sub>

`function parsed(body: String): Any`
<sub>línea 381</sub>

`function pathOf(msg: Any): String`
<sub>línea 389</sub>

`function answer(msg: Any, path: String, main: String): String?`  
The answer after analyzing `main`, or null when that program does not reach the file.  
<sub>línea 396</sub>

`function readFile(path: String): String?`
<sub>línea 424</sub>

`function askWorker(body: String): String`
<sub>línea 438</sub>

`function quiet(): String`  
The worker's standard output goes to the standard error: the standard output is the editor's.  
<sub>línea 468</sub>

`public function worker(reqPath: String, respPath: String): int32`  
larimarc lsp-worker: answers one question written to a file by the server.  
<sub>línea 471</sub>

---

## editor.session

`src/editor/session.lar` · 182 líneas · 8 funciones
editor.session: one analysis of a program, without generating C (larimar check, larimar lsp).
It links and analyzes like a compilation; the errors stay in linkErrors and analysisErrors (with the
line numbers that also say the file), and the analyzed program stays in `program` for the questions
of the editor (ide.lar).

`public function analyzeFile(main: String, shownFrom: String): bool`  
Links and analyzes a main file. true: no errors. Messages name files relative to `shownFrom`.  
<sub>línea 29</sub>

`function findLibraryRoots(main: String): void`  
The folders of the libraries the project of a file uses ([packages] of its larimar.toml): `import textkit` finds textkit.lar there. larimar build checks them.  
<sub>línea 51</sub>

`public function stdDir(): String`  
Where std/ is: $LARIMAR_HOME/std, or next to the tool (bin/larimar -> std/).  
<sub>línea 77</sub>

### class `Diagnostic`
An error of the analysis, with its file and line.

`public function diagnostics(): Diagnostic[*]`  
The errors of the last analysis.  
<sub>línea 98</sub>

`function diagnostic(raw: String): Diagnostic`  
"Semantic Error [Line 1000012]: message" -> file 1, line 12.  
<sub>línea 107</sub>

`public function projectMain(file: String): String`  
The main file of the project a file belongs to (larimar.toml above it), or the file itself.  
<sub>línea 123</sub>

`function tomlMain(path: String): String`  
[project] main of a larimar.toml ("src/main.lar" when it does not say).  
<sub>línea 139</sub>

`public function checkCommand(rest: String[*]): int32`  
larimar check [file.lar | folder] [--json]: the errors of a program, without generating C. A folder means its larimar.toml. With --json, a list of { file, line, message, kind }. Exit code 1 when there are errors.  
<sub>línea 155</sub>
