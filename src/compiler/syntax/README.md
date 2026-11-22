# syntax: from text to a tree

What goes in: the text of one file. What comes out: its `Program` (`syntax.ast`), a tree with one class
per kind of node, and the errors of syntax. Nothing here knows about other files or about types.

- `lexer.lar` cuts the text into tokens (`TokenType`). A token keeps its line; the linker adds the file
  to it later (a line number above a million says which file).
- `parser.lar` and its parts (`declarations`, `statements`, `expressions`, `types`, `natives`) build the
  tree by recursive descent, one function per rule of the grammar of the spec. A parser is an object
  (`Parser`): two files are parsed without sharing anything.
- The tree only says what was written. What the analysis learns (the type of an expression, where its
  value lives, which symbol a name is) is written later into fields of the same nodes (`ty`, `place`,
  `symbol`), which start empty.
- A syntax error stops at the first one of a file: the rest of the file is not parsed.

## Its API

<!-- api: written by tools/reference.py from the code; not edited by hand -->

- **`syntax.ast`**: the syntax tree (Ast.java)
  - `class Node`
  - `class Expr extends Node`
  - `class Stmt extends Node`
  - `enum TypeRefKind`
  - `class TypeRef extends Node`
  - `function typeNamed(name: String in default, line: int32): TypeRef`
  - `class Program extends Node`
  - `class ImportDecl extends Node`: import a.b; import a.b as x; import a.b { n1, n2 };
  - `class CIncludeDecl extends Node`: platform: "" (every one), "windows", "macos", "linux" or "unix": that of the class it is in (the analyzer sets it)
  - `class CCodeDecl extends Node`
  - `class NativeInterfaceDecl extends Node`: native interface Name "<h>" [extends A, B] { function...; type...; const...; let
  - `class ExternTypeDecl extends Node`: native type X; = T*; = c"C TYPE"; 
  - `class ExternFunctionDecl extends Node`: cName: the C function called (it stays when a module renames the declaration); prototype: no cinclude
  - `class ExternValueDecl extends Node`: native const NAME: T [= c_name | = "C"]; native let NAME: T [= c_name]; a C constant (or macro) or a C global variable
  - `class ConstDecl extends Node`
  - `class Param extends Node`: lives: "", "default", "self" or another parameter (`k: Node in p`)
  - `class FunctionDecl extends Node`: Functions, methods, operators and interface signatures (hasBody false)
  - `class FieldDecl extends Node`
  - `class StructDecl extends Node`
  - `class ClassDecl extends Node`
  - `class InterfaceDecl extends Node`
  - `class NativeTypeDecl extends Node`
  - `class EnumVariant extends Node`
  - `class EnumDecl extends Node`
  - `function declName(d: Node): String`: The name a declaration introduces, or ""
  - `function isTypeDecl(d: Node): bool`
  - `class VarDecl extends Stmt`
  - `class AssignStmt extends Stmt`
  - `class ReturnStmt extends Stmt`
  - `class ExprStmt extends Stmt`
  - `class IfStmt extends Stmt`: platform != "": chosen when the C is compiled (#if 
  - `class WhileStmt extends Stmt`
  - `class ForStmt extends Stmt`: for (x in e), for (i, x in e), for (i in a..b)
  - `class BreakStmt extends Stmt`
  - `class ContinueStmt extends Stmt`
  - `class ThrowStmt extends Stmt`
  - `class YieldStmt extends Stmt`
  - `class CatchClause extends Node`
  - `class TryStmt extends Stmt`
  - `class SwitchStmt extends Stmt`
  - `class BlockStmt extends Stmt`: { 
  - `class IntLit extends Expr`: big: the value is num as uint64 (above int64); huge: it does not fit in 64 bits (text has it)
  - `class FloatLit extends Expr`
  - `class StringLit extends Expr`: texts.length == exprs.length + 1; the texts keep their escapes
  - `class BoolLit extends Expr`
  - `class NullLit extends Expr`
  - `class Ident extends Expr`
  - `class SelfExpr extends Expr`
  - `class SuperMember extends Expr`
  - `class Member extends Expr`
  - `class Index extends Expr`
  - `class Call extends Expr`
  - `class Unary extends Expr`
  - `class Binary extends Expr`
  - `class Ternary extends Expr`
  - `class IsExpr extends Expr`: expr is Type [binding]
  - `class Cast extends Expr`
  - `class Unwrap extends Expr`
  - `class Lambda extends Expr`
  - `class FieldInit extends Node`: name "": a positional entry ({ 1, 2 } in an Any)
  - `class ObjectLit extends Expr`
  - `class ArrayLit extends Expr`
  - `class Placed extends Expr`: e in m, in heap, in byte[N], in default
  - `class Pattern extends Node`: fields[i] is bound to bindings[i]; binding is the name for the whole value
  - `class SwitchCase extends Node`: One of expr, block (hasBlock) or throwStmt is the arm
  - `class SwitchExpr extends Expr`
  - `function allStmts(body: Stmt[*] in out, out: Stmt[*]): void`: Every statement of a body, nested ones included (not inside lambdas)
  - `function allExprs(body: Stmt[*] in out, lambdas: bool, out: Expr[*]): void`: Every expression of a body (into lambda bodies when `lambdas`)
  - `function exprAll(e: Expr? in out, lambdas: bool, out: Expr[*]): void`
- **`syntax.lexer`**: source text -> tokens (Lexer.java)
  - `enum TokenType`
  - `class Token`
  - `class Lexer`: Reads a source text into tokens: Lexer { src, line }, run(), then its toks
  - `function stripIndent(raw: String): String`
- **`syntax.parser`**: tokens -> syntax tree
  - `function parseProgram(source: String in default, startLine: int32): Program`: The tree of one source file; its `error` is the first lexical or syntax error
  - `class Parser`: The tokens of a source text, read one by one
  - `function endedBySemicolon(parser: Parser in default, node: Node, what: String): Node`: The node, after its ';'
  - `function qualifiedName(parser: Parser in default, message: String): String`: NAME ( 
  - `function strictList(parser: Parser in default, close: TokenType, readItem: () -> void): void`: [ item ( , item )* ] before `close` (which is not read)
  - `function looseList(parser: Parser in default, close: TokenType, readItem: () -> void): void`: Like strictList, but a comma may also end the list
  - `function lives(parser: Parser in default): String`: in ( default | self | NAME ): where a parameter or a result lives
- **`syntax.parser.declarations`**: what a file declares (functions, structs, classes, interfaces, enums, constants)
  - `function topLevelDeclaration(parser: Parser in default): Node`: ccode { C } | ccode "FILE" ; | cinclude "HEADER" ; | native 
  - `function parameter(parser: Parser in default, typeRequired: bool): Param`: NAME : Type [ in lives ] (in a lambda: NAME [ : Type ])
  - `function parameters(parser: Parser in default): Param[*]`: ( [ parameter ( , parameter )* ] )
  - `function functionDeclaration(parser: Parser in default, isOverride: bool, withBody: bool): FunctionDecl`
  - `function cBodied(p: Parser in default, declaration: FunctionDecl in default): void`: native function f(params): T { C } (a method, a static function): the body is C
  - `function staticFunction(parser: Parser in default, owner: String in default): void`: (after `static`, inside the type `owner`) function 
  - `function field(parser: Parser in default): FieldDecl`: let NAME : Type [ = expression ] ;
- **`syntax.parser.expressions`**: expressions, from the lowest precedence to the highest
  - `function expression(parser: Parser in default): Expr`: ternary [ in ( heap | default | byte[N] | expression ) ]: where a created value lives
  - `function coalesce(parser: Parser in default): Expr`: binary operators [ ?? coalesce ]
  - `function level(kind: TokenType): int32`: The level of a binary operator, from the loosest (1) to the tightest; 0: not one
  - `function switchExpression(parser: Parser in default, line: int32): SwitchExpr`: (after `switch`) ( expression ) { case* } case: ( case pattern ( , pattern )* | default ) [ when expression ] -> ( block | throw expression ; | expression ; )
  - `function waitFirst(line: int32, condition: Expr in default, body: Stmt[*] in default): Stmt[*]`: wait until (cond): the body starts with `while (!(cond)) { self.__wait(); }`
  - `function optionalFollows(next: TokenType): bool`: After `as T`, a '?' makes T optional only when what follows can come after a type (x as int64? ?? 0, (x as T?), x as T?;)
- **`syntax.parser.natives`**: what comes from C (native functions, types, structs and values; cinclude and ccode)
  - `function nativeDeclaration(parser: Parser in default, line: int32): Node`: (after `native`) function NAME ( [ parameter ( , parameter )* [ , 
  - `function nativeInterface(parser: Parser in default, owner: String in default, opened: bool): NativeInterfaceDecl`: (after `native interface`) NAME STRING ( , STRING )* [ extends NAME ( , NAME )* ] { ( function 
  - `function languageType(parser: Parser in default, line: int32): NativeTypeDecl`: (after `type`) NAME { ( static 
  - `function nativeFunction(parser: Parser in default, line: int32): FunctionDecl`: (after `native function`) NAME parameters [ : Type ] [ in lives ] [ throws Type ] [ = expression ] ;
  - `function nativeProperty(parser: Parser in default, line: int32): FunctionDecl`: (after `native let`) NAME : Type [ = expression ] ; A value read without parentheses and never assigned (s.length)
- **`syntax.parser.statements`**: statements and blocks
  - `function variable(parser: Parser in default): VarDecl`: let NAME : Type [ = expression ] ;
  - `function block(parser: Parser in default, what: String): Stmt[*]`: { statement* }
- **`syntax.parser.types`**: types as they are written (int32, String?, T[*], (A) -> R thread safe)
  - `function type(parser: Parser in default): TypeRef`: ( qualified NAME | ( Type ) | ( [ Type ( , Type )* ] ) -> Type ) suffix* suffix: [ ] | [ ] | [ expression ] | ? | and after a function type: [ thread safe ]

<!-- /api -->
