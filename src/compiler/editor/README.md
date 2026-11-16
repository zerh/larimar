# editor: larimar check, lsp and dap

What goes in: the editor's messages (JSON-RPC on the standard input) and the texts it has open. What comes
out: errors, hovers, definitions, completions; and, for the debugger, the program's stack and values with
Larimar's names. No line of C: what it starts, it starts with `std.os.process`.

- `session.lar`: one analysis of a program without generating C (the passes up to Analyze), for
  `larimar check` (`--json` for tools) and for the language server.
- `lsp.lar`: the language server. It keeps the editor's texts (in a memory it compacts) and nothing
  else; each question is answered by a new `larimarc lsp-worker`, so an analysis never leaves memory
  behind and a crash only loses one answer.
- `opendocuments.lar`: the texts of the open files, which the linker reads before the disk.
- `ide.lar`: the answers, from an analyzed program.
- `dap.lar`: the debugger: between the editor and lldb-dap, it shows the call stack and the variables as
  Larimar names them, with the debug map the compiler writes (`codegen.debugmap`).

## Its API

<!-- api: written by tools/reference.py from the code; not edited by hand -->

- **`editor.dap`**: larimar dap, the debugger for editors (Debug Adapter Protocol on stdin and stdout)
  - `function serveDebugger(args: String[*]): int32`
- **`editor.ide`**: answers the editor's questions (larimar lsp) from an analyzed program: errors, hover, go to definition, references, the symbols of a file, completion and the signature being written
  - `function lineText(index: int32, line: int32): String`: The text of a line (from 1) of a file, without its end
  - `function fileIndex(path: String): int32`: The file index of a path in the analysis, or -1
  - `function utf16Col(line: String, byteCol: int32): int32`: UTF-16 units of the first `byteCol` bytes of a line (what the editor counts)
  - `function byteCol(line: String, units: int32): int32`: The byte of a line where the editor's UTF-16 column falls
  - `function uriOfPath(path: String): String`: file:///a/b%20c.lar
  - `function pathOfUri(uri: String): String`: The path of a file:// URI
  - `function hoverJson(path: String, line0: int32, char16: int32): String`: Hover: the declaration, as code, and its comment
  - `function definitionJson(path: String, line0: int32, char16: int32): String`: Go to definition
  - `function referencesJson(path: String, line0: int32, char16: int32, withDecl: bool): String`: Every place that names the same thing (with its declaration when `withDecl`)
  - `function symbolsJson(path: String): String`: The symbols of a file: its declarations, with the members of its types inside
  - `function prepareCompletion(path: String, line0: int32, char16: int32, signatureHelp: bool): void`: Before analyzing for completion or signature help: the line being written does not compile yet, so in this process the document gets a line that does (the rest of the program stays as it is)
  - `function completionJson(path: String, line0: int32, char16: int32): String`: Completion, after prepareCompletion and the analysis
  - `function signatureJson(path: String): String`: The signature of the call being written, after prepareCompletion(..., true) and the analysis
  - `function diagnosticsJson(requested: String): String`: The errors of the analysis, per file: one { uri, diagnostics } per line, for every file of the program that is not part of std (so a file whose errors are fixed gets an empty list), and for any file with errors
- **`editor.lsp`**: larimar lsp, the language server editors start (Language Server Protocol, JSON-RPC on stdin and stdout, each message after a "Content-Length: N" header)
  - `function serve(): int32`: larimar lsp
  - `function worker(reqPath: String, respPath: String): int32`: larimarc lsp-worker: answers one question written to a file by the server
- **`editor.opendocuments`**: the texts of the documents open in the editor, by file path, for the analysis of one question (larimar lsp-worker)
  - `function setOpenDocument(path: String, text: String): void`: Keeps (a copy of) the editor's text of a file
  - `function openDocument(path: String): String?`: The editor's text of a file, or null when it is not open
- **`editor.session`**: one analysis of a program, without generating C (larimar check, larimar lsp)
  - `function analyzeFile(main: String, shownFrom: String): bool`: Links and analyzes a main file (pipeline.analysisPasses)
  - `function compilationOf(main: String, shownFrom: String): Compilation`: A compilation of a main file, with this session's std and source root
  - `function stdDir(): String`: Where std/ is: $LARIMAR_HOME/std, or next to the tool (bin/larimar -> std/)
  - `class Diagnostic`: An error of the analysis, with its file and line
  - `function diagnostics(): Diagnostic[*]`: The errors of the last analysis
  - `function projectMain(file: String): String`: The main file of the project a file belongs to (larimar.toml above it), or the file itself
  - `function checkCommand(rest: String[*]): int32`: larimar check [file.lar | folder] [--json]: the errors of a program, without generating C

<!-- /api -->
