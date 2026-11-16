# The standard library: reference

Every module of `std` a program can import, and everything it makes public: types (with their members, as visible as their type), functions, constants and variables, as they are in the code, with the comment above each one.

> This file is **generated** from `src/std/` with `tools/std_reference.py`; it is not edited by hand. The [manual](manual.md#25-standard-library) explains the library with examples. The parts of std for std itself (`*.posix`, `*.windows`, `*.macos`, `*.common`, `*.internal`) are not here: a program cannot import them.

**29 modules, 198 public names.**

## Modules

- [`std.crypto`](#stdcrypto): hashes, HMAC and secure random bytes, written in Larimar (only the random bytes come from
- [`std.encoding.base64`](#stdencodingbase64): bytes as base64 text (RFC 4648), and back.
- [`std.encoding.hex`](#stdencodinghex): bytes as hexadecimal text, and back.
- [`std.encoding.json`](#stdencodingjson): JSON text to Any, and Any to JSON text.
- [`std.encoding.toml`](#stdencodingtoml): TOML text to Any, and Any to TOML text.
- [`std.encoding.url`](#stdencodingurl): percent-encoding (RFC 3986) and query strings.
- [`std.io`](#stdio): what every input and output shares: the error (IoError), the streams (bytes from anywhere and
- [`std.io.bytes`](#stdiobytes): binary messages. A ByteWriter puts numbers, texts and bytes one after another; a ByteReader
- [`std.io.console`](#stdioconsole): the standard input, output and error.
- [`std.io.files`](#stdiofiles): files and folders: whole files in one call, like Java's Files, and an open File to read
- [`std.io.path`](#stdiopath): paths as text, with / or \ between folders.
- [`std.lang`](#stdlang): the part of the language written in Larimar. Every program sees its public names
- [`std.math`](#stdmath): the numbers every program ends up needing.
- [`std.memory`](#stdmemory): a limit for a memory that grows, and compacting one that has been used for a long time.
- [`std.net`](#stdnet): TCP and UDP. A TcpSocket is read and written directly (read, write), like a socket in C,
- [`std.net.http`](#stdnethttp): an HTTP/1.1 client over std.net, with https:// through a TlsProvider (std.net.tls).
- [`std.net.openssl`](#stdnetopenssl): the TLS servers on Unix, over OpenSSL loaded at run time (std.net.tls's client on
- [`std.net.tls`](#stdnettls): encrypted connections, for https:// (and whatever else needs TLS).
- [`std.net.tls.openssl`](#stdnettlsopenssl): the TLS client on Linux, over the OpenSSL of std.net's servers.
- [`std.os`](#stdos): the environment the program runs in.
- [`std.os.process`](#stdosprocess): processes. A Process runs another program, or a task of this one in a copy of it; a
- [`std.os.rpc`](#stdosrpc): calls to another program, and a program that answers them (JSON-RPC 2.0).
- [`std.os.sharedmemory`](#stdossharedmemory): memory that several programs see. A stream is a queue (each message once, in
- [`std.platform`](#stdplatform): the system the program is built for, and the marks of the classes that are for one.
- [`std.test`](#stdtest): the checks that test functions use (larimar test runs them).
- [`std.text`](#stdtext): helpers for reading text byte by byte (lexers, parsers).
- [`std.text.regex`](#stdtextregex): regular expressions, written in Larimar (no C library: the same on every system).
- [`std.thread`](#stdthread): a pool of threads for a batch of tasks.
- [`std.time`](#stdtime): the clock, waiting, and dates as text.

---

## std.crypto

```
hashes, HMAC and secure random bytes, written in Larimar (only the random bytes come from
the system).

  import std.crypto as Crypto;
  import std.encoding.hex as Hex;
  println(Hex.encode(Crypto.sha256("hola".bytes())));       // b221d9db...
  let mac: byte[*] = Crypto.hmacSha256(key.bytes(), body.bytes());
  let session: byte[*] = Crypto.randomBytes(32);            // for session ids, CSRF tokens, salts

SHA-1 is broken for signatures: it is here for protocols that need it (the WebSocket handshake). For
anything new, SHA-256. The results are new lists, created where the caller puts them.
```

`src/std/crypto.lar`

`function randomBytes(n: int32): byte[*]`  
n bytes from the system's secure random source (it panics if there is none: it never gives weak bytes).

`function sha256(data: byte[]): byte[*]`  
The SHA-256 of some bytes: 32 bytes.

`function sha1(data: byte[]): byte[*]`  
The SHA-1 of some bytes: 20 bytes. Only for protocols that ask for it (WebSocket).

`function hmacSha256(key: byte[], data: byte[]): byte[*]`  
HMAC-SHA256 (RFC 2104): a signature of `data` with `key`, 32 bytes. For signed cookies and tokens.

`function sameBytes(a: byte[], b: byte[]): bool`  
Whether two byte lists are equal, taking the same time wherever they differ (to compare signatures).

---

## std.encoding.base64

```
bytes as base64 text (RFC 4648), and back.

  import std.encoding.base64 as Base64;
  println(Base64.encode("hola".bytes()));                // aG9sYQ==
  println(Base64.encodeUrl(token));                      // for URLs and cookies: - and _, no '='
  let bytes: byte[*]? = Base64.decode("aG9sYQ==");
```

`src/std/encoding/base64.lar`

`function encode(bytes: byte[]): String`  
Base64 with + and /, padded with '='.

`function encodeUrl(bytes: byte[]): String`  
Base64 for URLs, file names and cookies: - and _ instead of + and /, without '='.

`function decode(text: String): byte[*]?`  
The bytes of base64 text (with + and /, the '=' optional), or null when it is not base64.

`function decodeUrl(text: String): byte[*]?`  
The bytes of URL base64 text (with - and _, the '=' optional), or null when it is not base64.

---

## std.encoding.hex

```
bytes as hexadecimal text, and back.

  import std.encoding.hex as Hex;
  println(Hex.encode("hola".bytes()));                   // 686f6c61
  let bytes: byte[*]? = Hex.decode("686F6C61");          // upper or lower case
```

`src/std/encoding/hex.lar`

`function encode(bytes: byte[]): String`  
Two lowercase hex digits per byte.

`function decode(text: String): byte[*]?`  
The bytes of hex text (upper or lower case), or null when it is not hex or has an odd length.

---

## std.encoding.json

```
JSON text to Any, and Any to JSON text.

  import std.encoding.json as Json;
  let config: Any = Json.parse("{\"port\": 8080, \"names\": [\"a\", \"b\"]}");
  println("${config.port as int32 ?? 80}");
  println(Json.stringify({ ok: true, list: { 1, 2, 3 } }));

An object becomes a table with named entries, an array a table with positions. Whole numbers that
fit are int64, the rest float64. A table with named entries is written as an object; one with only
positions, as an array; an empty table, as {}.
```

`src/std/encoding/json.lar`

### enum `JsonError`
The text is not valid JSON: where (byte position) and why.

`function parse(text: String): Any throws JsonError`  
The value of a JSON text.

`function stringify(v: Any): String`  
The JSON text of a value.

`function quote(s: String): String`  
A String as a JSON string, with its quotes.

---

## std.encoding.toml

```
TOML text to Any, and Any to TOML text.

  import std.encoding.toml as Toml;
  let config: Any = Toml.parse(Files.readString("larimar.toml"));
  println(config.project.name as String ?? "?");
  println(Toml.stringify({ project: { name: "demo", version: "1.0.0" } }));

The part of TOML that configuration files use: [sections] (also [a.b], a table inside a table),
key = value, where a value is a "string", a whole number, true or false, or a list of those
([...], which may span several lines). Comments start with #. Keys are letters, digits, '_' and '-'.

A section becomes a table with named entries; a list, a table with positions. The entries keep the
order of the file.
```

`src/std/encoding/toml.lar`

### enum `TomlError`
The text is not valid TOML: the line (from 1) and why.

`function message(e: TomlError): String`  
A message for the error: "line 3: Expected key = value".

`function parse(text: String): Any throws TomlError`  
The tables of a TOML text: keys before any [section] go in the top table.

`function stringify(root: Any): String`  
The TOML text of a table: its plain entries first, then one [section] for each table inside it.

---

## std.encoding.url

```
percent-encoding (RFC 3986) and query strings.

  import std.encoding.url as Url;
  println(Url.encode("casa en Punta Cana"));                         // casa%20en%20Punta%20Cana
  println(Url.decode("casa%20en%20Punta%20Cana") ?? "?");            // casa en Punta Cana
  let q: Any = Url.parseQuery("city=Santo+Domingo&rooms=3");         // { city: "Santo Domingo", rooms: "3" }
  println(Url.query({ city: "La Romana", page: 2 }));                 // city=La%20Romana&page=2
```

`src/std/encoding/url.lar`

`function encode(text: String): String`  
Everything but letters, digits and - _ . ~ as %XX (UTF-8 bytes): for a part of a path or a query value.

`function decode(text: String): String?`  
%XX back to bytes (a '+' stays a '+'), or null when a % is not followed by two hex digits.

`function parseQuery(query: String): Any`  
The entries of a query string (what follows '?', or a form sent as application/x-www-form-urlencoded): a table of names and texts, '+' read as a space. When a name repeats, the last value stays. An entry that cannot be decoded is left out.

`function query(entries: Any): String`  
A query string from the named entries of a table: "a=1&b=two%20words" (numbers and bool as text).

---

## std.io

```
what every input and output shares: the error (IoError), the streams (bytes from anywhere and
to anywhere), text on top of them (Reader), and streams in memory.

  import std.io { IoError, InputStream, OutputStream, Reader, copy };
  import std.io.files { open };

  let lines: Reader = { from: open("notes.txt") };          // a File is an InputStream
  let line: String? = lines.readLine();

  let out: BytesOutputStream = {};
  copy(BytesInputStream { data: "hello" }, out);
  println(out.toString());

Files (std.io.files), sockets (std.net), the body of an HTTP response (std.net.http) and the console
(std.io.console) are streams, and their reads and writes throw IoError. Only what holds something of
the system (a File, a socket) is Closeable; it also closes itself when its memory is freed.

Memory: reading and copying ask the system for memory only where they must. A Reader has one buffer
for its whole life, and a line is created once, at its exact size, wherever the caller puts the
result. So reading a file of any size line by line can use a fixed buffer on the stack:

  while (true) {
      let scratch: byte[4096] = [];                     // on the stack: no malloc in the loop
      let line: String? = lines.readLine() in scratch;  // the line is created in scratch
      if (line == null) { break; }
      ...
  }
```

`src/std/io.lar`

### enum `IoError`
What went wrong reading or writing: a file, a folder, a socket, the console.

`function message(e: IoError): String`  
"not found: notes.txt", "denied: ...", "closed", "timed out" or "failed: ...".

`function raise(code: int32, path: String): void throws IoError`  
Throws the IoError of a result code: 1 not found, 2 denied, 3 failed, 4 closed, 5 timed out (0 is fine).

### interface `InputStream`
Where bytes are read from.

- `function read(buffer: byte[]): int32 throws IoError`  
  Fills buffer from its start; returns how many bytes it read, 0 when nothing is left.

### interface `OutputStream`
Where bytes are written.

- `function write(bytes: byte[]): void throws IoError`  
  Writes all of them, or throws.

- `function flush(): void throws IoError`  
  Makes sure what was written has arrived (nothing to do for what has no buffer).

### interface `Closeable`
Something that holds a resource of the system and can let it go before its memory is freed.

- `function close(): void throws IoError`

### class `BytesInputStream implements InputStream`
Reads bytes (or UTF-8 text) already in memory. A String is bytes, so it serves for both.

- `data: String`

- `position: int32`

- `override function read(buffer: byte[]): int32 throws IoError`

### class `BytesOutputStream implements OutputStream`
BytesOutputStream: collects what is written, in its own memory (it must grow: collecting is its job).

- `data: byte[*]`

- `override function write(bytes: byte[]): void throws IoError`

- `override function flush(): void throws IoError`

- `function toString(): String`  
  What was written, as text (a copy).

- `function toByteArray(): byte[*]`  
  What was written, as bytes (a copy).

### class `Reader implements InputStream`
Text from any InputStream. Lines are cut only at \n (and a \r before it is dropped), so a UTF-8 character is never split, even when its bytes arrive in two reads. It does not close what it reads: whoever opened it does (or its memory does). Its buffer lives with it (one allocation for its whole life). A line that is all in the buffer (almost every line) becomes a String with one copy, created where the caller puts the result; only a line that crosses the end of the buffer is gathered first.

- `from: InputStream`

- `chunk: byte[*]`

- `count: int32`

- `position: int32`

- `finished: bool`

- `function more(): bool throws IoError`  
  Makes sure there is a byte to read; false at the end.

- `function readLine(): String? throws IoError`  
  The next line, without its end; null when nothing is left.

- `function readInto(buffer: byte[], max: int32): int32 throws IoError`  
  Up to max bytes (and no more than buffer.length) into buffer, from its start: first what the Reader already has, then from its stream. 0 at the end. Lines and bytes can be mixed: what readLine() left in the buffer comes out here first (an HTTP body after its header lines, say).

- `override function read(buffer: byte[]): int32 throws IoError`  
  As an InputStream: readInto(buffer, buffer.length).

- `function readAll(): String throws IoError`  
  Everything that is left.

`function buffer(n: int32): byte[*]`  
n zero bytes, to give to read(). (A `byte[4096] = []` would not do: a T[N] starts empty, and read() fills only up to the length of what it receives.)

`function copy(input: InputStream, output: OutputStream): void throws IoError`  
Copies everything from input to output, then flushes output. Closes neither. One buffer for the whole copy; a full read is written as it is, and the last, shorter piece goes through a buffer on the stack: copying a file of any size asks the system for memory once.

---

## std.io.bytes

```
binary messages. A ByteWriter puts numbers, texts and bytes one after another; a ByteReader
takes them back in the same order. For what goes over a stream or a segment of shared memory when JSON
would cost too much (frames, samples, commands of drawing).

  import std.io.bytes { ByteWriter, ByteReader };

  let out: ByteWriter = {};
  out.putInt32(7);
  out.putFloat64(2.5);
  out.putString("hola");
  stream.write(out.bytes);                  // or segment.putBytes(0, out.bytes)

  let input: ByteReader = { data: received };
  let n: int32 = input.getInt32();          // 7, then 2.5, then "hola"

Numbers are little-endian, the order of the processors Larimar runs on; a String is its length (an
int32) and its bytes. A ByteReader that runs out of bytes throws IoError.Failed: the message came cut,
or it is not what the reader thought.
```

`src/std/io/bytes.lar`

### class `ByteWriter`
Writes values one after another into `bytes`, which grows.

- `bytes: byte[*]`

- `function putByte(value: byte): void`

- `function putBool(value: bool): void`

- `function putInt32(value: int32): void`

- `function putInt64(value: int64): void`

- `function putFloat64(value: float64): void`

- `function putString(value: String): void`  
  Its length (an int32), then its bytes.

- `function putBytes(value: byte[]): void`  
  The bytes as they are (the reader must know how many: write the count first).

- `function length(): int32`  
  How many bytes were written.

- `function clear(): void`  
  Empties it, to write the next message in the same memory.

- `function putInteger(value: int64, count: int32): void`

### class `ByteReader`
Reads values from `data` in the order a ByteWriter wrote them.

- `data: byte[*]`

- `position: int32`

- `function getByte(): byte throws IoError`

- `function getBool(): bool throws IoError`

- `function getInt32(): int32 throws IoError`

- `function getInt64(): int64 throws IoError`

- `function getFloat64(): float64 throws IoError`

- `function getString(): String throws IoError`  
  A String that putString wrote.

- `function getBytes(into: byte[]): void throws IoError`  
  Fills `into` with the next bytes (as many as it has).

- `function remaining(): int32`  
  How many bytes are left to read.

- `function getInteger(count: int32): int64 throws IoError`

- `function need(count: int32): void throws IoError`

---

## std.io.console

```
the standard input, output and error.

  import std.io.console as Console;
  let name: String = Console.readLine() ?? "";
  Console.printError("something went wrong");

input, output and error are also streams, for code that takes any InputStream or OutputStream.
```

`src/std/io/console.lar`

`function readLine(): String?`  
The next line of the standard input, without its end, or null at its end.

`function read(count: int32): String`  
Exactly `count` bytes of the standard input (fewer only if it ends; see lastCount()).

`function lastCount(): int32`  
How many bytes the last read() got (also the length of what it gave).

`function write(text: String): void`  
Writes to the standard output, without a new line.

`function flush(): void`  
Sends what was written to the standard output now.

`function binaryMode(): void`  
Input and output byte by byte, as they are (on Windows, without turning \n into \r\n).

`function unbufferInput(): void`  
The standard input without a buffer of this program: call it before reading anything, when the program waits for input with waitForInput (so that what was read ahead is never hidden from it).

`function waitForInput(ms: int32): bool`  
Whether something arrives on the standard input within ms milliseconds (-1: as long as it takes).

`function printError(text: String): void`  
Writes a line to the standard error.

`let input: InputStream`  
The standard input as a byte stream.

`let output: OutputStream`  
The standard output as a byte stream.

`let error: OutputStream`  
The standard error as a byte stream.

---

## std.io.files

```
files and folders: whole files in one call, like Java's Files, and an open File to read
or write in parts.

  import std.io.files as Files;
  import std.io.files { File };
  let text: String = Files.readString("notes.txt");
  Files.writeString("copy.txt", text);
  let f: File = Files.open("notes.txt");
  while (true) { let line: String? = f.readLine(); if (line == null) { break; } ... }

A File closes itself when the memory it lives in is freed (the end of the block that keeps it), so it
is never left open; close() closes it earlier.

What these functions give lives where the call says (Files.readString(path) in memory), or in
the memory of the block that keeps it. Everything that can fail throws IoError. Written in Larimar
over C's stdio; folders over each system's own functions (opendir, mkdir; FindFirstFile, _mkdir).
```

`src/std/io/files.lar`

`function message(e: IoError): String`  
A message for the error (the same as std.io's): "not found: notes.txt"...

`function readString(path: String): String throws IoError`  
The whole file as text.

`function writeString(path: String, text: String): void throws IoError`  
Replaces the file with `text`, creating it if needed.

`function appendString(path: String, text: String): void throws IoError`  
Adds `text` at the end of the file, creating it if needed.

`function exists(path: String): bool`  
Is there a file or a folder with that path?

`function isFile(path: String): bool`

`function isDirectory(path: String): bool`

`function modifiedTime(path: String): int64`  
When the file was last changed: seconds since 1970 (UTC), or 0 when there is nothing at that path.

`function size(path: String): int64`  
The size of a file in bytes, or -1 when there is nothing at that path.

`function list(path: String): String[*] throws IoError`  
The names of what a folder holds (files and folders, in no particular order).

`function createDirectories(path: String): void throws IoError`  
Creates the folder, and the folders above it that are missing.

`function copy(from: String, to: String): void throws IoError`  
Copies a file (replacing `to` if it exists, even a read-only one, like cp -f); on Unix an executable stays executable.

`function delete(path: String): void throws IoError`  
Deletes a file, or an empty folder.

### class `File implements InputStream, OutputStream`
An open file.

- `file: FileHandle?`

- `path: String`

- `lineBuffer: byte[*]`

- `function live(): FileHandle throws IoError`  
  The C file, or an IoError if it was closed.

- `override function read(buffer: byte[]): int32 throws IoError`  
  Fills buffer from its start (one fread); how many bytes, 0 at the end.

- `function readLine(): String? throws IoError`  
  The next line, without its end (\n, or \r\n); null at the end of the file.

- `function readAll(): String throws IoError`  
  What is left of the file, as text.

- `override function write(bytes: byte[]): void throws IoError`

- `function writeText(text: String): void throws IoError`

- `override function flush(): void throws IoError`  
  Writes what is waiting in C's buffer: an error here is an error writing the file.

- `function close(): void throws IoError`  
  Closes the file now (what is in the buffer is written first); otherwise it is closed when its memory is freed.

`function open(path: String): File throws IoError`  
Opens a file to read it.

`function create(path: String): File throws IoError`  
Creates a file to write it (replacing it if it exists).

`function append(path: String): File throws IoError`  
Opens a file to write at its end (creating it if needed).

---

## std.io.path

```
paths as text, with / or \ between folders.

  import std.io.path as Paths;
  let config: String = Paths.join(Paths.parent(file), "larimar.toml");

The paths these functions create are short and go to the default memory.
```

`src/std/io/path.lar`

`function parent(path: String): String`  
"a/b/c.lar" -> "a/b"; "" when there is no folder.

`function fileName(path: String): String`  
"a/b/c.lar" -> "c.lar".

`function stem(path: String): String`  
"a/b/c.lar" -> "c" (a name that starts with a dot keeps it: ".config").

`function extension(path: String): String`  
"a/b/c.lar" -> "lar"; "" when there is none.

`function join(dir: String, file: String): String`  
`file` inside the folder `dir`; an absolute `file` stays as it is.

`function isAbsolute(path: String): bool`  
"/x", "\x" and "C:/x" are absolute.

`function absolute(path: String): String`  
The absolute, normalized form (a relative path is taken from the current folder).

`function normalize(path: String): String`  
Without "." and "folder/.." parts, with / between folders; "." when nothing is left.

`function relative(base: String, file: String): String`  
`file` relative to the folder `base` when it is inside it; absolute otherwise.

---

## std.lang

the part of the language written in Larimar. Every program sees its public names
without an import, and only what a program mentions (and what that needs) reaches the C.

`src/std/lang.lar`

### interface `Runnable`
What a Thread runs.

### class `Thread`
A thread of the operating system: Thread { run: ... } in memory, then start() and join(). What has no body here (start, join; the core of Any and String) the compiler writes.

- `run: Runnable`

- `name: String`

- `function start(): void`

- `function join(): void`

### type `Any`

- `length: int32`

- `function push(x: Any in self): void`

- `function containsKey(name: String): bool`

- `function contains(x: Any): bool`

- `function remove(name: String): bool`

- `function removeAt(i: int64): void`

- `function clear(): void`

- `function removeIf(f: (Any) -> bool): int32`

### type `String`

- `length: int32`  
  The core: the compiler writes these. Cuts are views (they share the bytes of the text).

- `operator [](i: int32): byte`

- `function substring(from: int32, to: int32): String in self`

- `function bytes(): byte[0]`

- `function split(sep: String): String[*]`  
  split and lines give views of the text in a new list: the caller checks that the text lives as long as the list, a rule a Larimar signature cannot say yet, so the compiler writes them.

- `function lines(): String[*]`

- `function isEmpty(): bool`

- `function isBlank(): bool`

- `function substring(from: int32): String in self`

- `function indexOf(s: String, from: int32): int32?`  
  Where s starts, looking from `from` on (a negative `from` is 0); null if it is not there.

- `function indexOf(s: String): int32?`

- `function contains(s: String): bool`

- `function startsWith(prefix: String): bool`

- `function endsWith(suffix: String): bool`

- `function trim(): String in self`

- `function trimStart(): String in self`

- `function trimEnd(): String in self`

- `function lastIndexOf(needle: String): int32?`

- `function count(needle: String): int32`

- `function compareTo(s: String): int32`  
  -1, 0 or 1, comparing the bytes.

- `function equalsIgnoreCase(other: String): bool`

- `function toUpperCase(): String`  
  A copy with a-z as A-Z (other bytes stay).

- `function toLowerCase(): String`  
  A copy with A-Z as a-z (other bytes stay).

- `function repeat(n: int32): String`

- `function replace(from: String, to: String): String`  
  A copy with every `from` changed to `to` (an empty `from` changes nothing).

- `function padStart(width: int32, fill: String): String`  
  Filled on the left with `fill` (repeated, and cut) up to `width` bytes.

- `function padEnd(width: int32, fill: String): String`  
  Filled on the right with `fill` (repeated, and cut) up to `width` bytes.

- `function toInt(): int64?`  
  "123", "-7", "+5", "0xFF", "0b1010", "1_000"; null if it is not a whole int64.

- `function toFloat(): float64?`  
  A number as C's strtod reads it (the whole text, no spaces around); null if it is not one.

- `function toBool(): bool?`

- `function codePointCount(): int32`  
  How many characters (UTF-8 code points).

- `function codePoints(): int32[*]`  
  The characters as numbers (UTF-8 decoded; a broken sequence gives 0xFFFD and moves one byte).

### class `StringBuilder`

- `buf: TextBuf`

- `function add(text: String): void`

- `function addLine(text: String): void`

- `length: int32`

- `function toString(): String in self`

- `function clear(): void`

`function stringOf(bytes: byte[]): String`  
A String with a copy of these bytes (UTF-8 expected, not checked). A byte 0 ends the text.

`function stringOfRange(bytes: byte[], from: int32, to: int32): String`  
A String with a copy of bytes[from..to) (UTF-8 expected, not checked): one allocation of the exact size, where the caller's result goes (`reader.readLine() in scratch` puts it in scratch).

---

## std.math

```
the numbers every program ends up needing.

  import std.math as Math;
  import std.math { Random };
  let side: float64 = Math.sqrt(2.0);
  let dice: Random = { seed: 42 };
  let roll: int32 = dice.below(6) + 1;                // 1..6, the same sequence for the same seed

The functions are C's (<math.h>, through its native interface LibM), by their names. Random is for
games and simulations: for secrets, std.crypto.randomBytes.
```

`src/std/math.lar`

`const PI: float64`

`const E: float64`

`function sqrt(x: float64): float64`

`function pow(base: float64, exponent: float64): float64`

`function exp(x: float64): float64`

`function log(x: float64): float64`

`function log10(x: float64): float64`

`function floor(x: float64): float64`

`function ceil(x: float64): float64`

`function round(x: float64): float64`

`function abs(x: float64): float64`

`function sin(x: float64): float64`

`function cos(x: float64): float64`

`function tan(x: float64): float64`

`function atan2(y: float64, x: float64): float64`

`function min(a: float64, b: float64): float64`

`function max(a: float64, b: float64): float64`

### class `Random`
A fast sequence of random numbers: the same for the same seed (xorshift64).

- `seed: uint64`

- `function next(): uint64`

- `function below(n: int32): int32`  
  0 <= it < n

- `function fraction(): float64`  
  0.0 <= it < 1.0

---

## std.memory

```
a limit for a memory that grows, and compacting one that has been used for a long time.

  import std.memory as Memory;

  function play(): void {
      let world: byte[*] = [] in heap;
      Memory.limit(world, 256 * 1024 * 1024);       // past 256 MB the program stops, naming 'world'
      let map: Any = {} in world;
      let paths: Path[*] = [] in world;
      while (running) {
          update(map, paths);                          // adds things, and drops others, for hours
          if (world.length > 64 * 1024 * 1024) {
              Memory.compact(world);                   // what map and paths still reach is copied; the rest is freed
          }
      }
  }

A memory frees everything at once, when its block ends; a memory that lives long and keeps changing
keeps the bytes of what was dropped too. compact() copies what its variables still reach to new blocks,
points the variables at the copies, and frees the old blocks. world.length, .capacity and .peak say how
much it uses.

The compiler checks every compact() call:
  - the memory is declared in a function (main, or the one that runs the work) and grows (byte[*] in heap);
  - every variable of its block that may point into it lives in it (it moves with it); any other is an
    error, and so is data of another memory of the block stored in it;
  - the call is not inside a 'for' over data, and what it moves holds no lambdas, interface values,
    threads or synchronized objects.
A memory with threads, synchronized objects or C resources in it stops the program when compacted. C must
not keep pointers it was given after a call returns (the rule of every extern function).
```

`src/std/memory.lar`

`function limit(memory: byte[*], bytes: int64): void`  
The most bytes `memory` may obtain from the system; past it the program stops with a message that names it. 0: no limit. Only for memories that grow (byte[*] in heap): a fixed one already has its size.

`function compact(memory: byte[*]): void`  
Copies what the variables of `memory` still reach to new blocks, points them at the copies, and frees the old blocks: the memory then holds only what is alive. Data of other memories is left where it is.

---

## std.net

```
TCP and UDP. A TcpSocket is read and written directly (read, write), like a socket in C,
and it is also an InputStream and an OutputStream, so Reader and copy() work on it as on a file.
TcpServer and UdpServer are the loop of a server, written for you: you give what to do with each
connection (or datagram), as a `thread safe` function, and run() serves them with the threads you say.

TCP connections. A TcpSocket is read and written directly (read, write), like a socket in C,
and it is also an InputStream and an OutputStream, so Reader and copy() work on it as on a file.

  import std.net { TcpSocket, TcpListener, NetError };
  import std.io { Reader };

  let socket: TcpSocket = TcpSocket.connect("example.com", 80);
  socket.writeText("GET / HTTP/1.0\r\nHost: example.com\r\n\r\n");
  let lines: Reader = { from: socket };
  println(lines.readLine() ?? "");                  // HTTP/1.0 200 OK

  let server: TcpListener = TcpListener.bind("127.0.0.1", 8080);
  while (true) {
      let client: TcpSocket = server.accept();      // closed when the turn's memory is freed
      ...
  }

Sockets block (read waits for data; setTimeout limits the wait). A socket closes itself when the memory
it lives in is freed, so one accepted in a loop is never left open. On Windows (Winsock) the program
is linked with ws2_32 by larimar build.

An EventLoop waits on many sockets at once (poll): TcpServer's own thread is one, watching the listener
and the kept connections; it is there for a server of your own too.

Written in Larimar over the C functions of the system (BSD sockets, Winsock on Windows): the C here is
declarations and a few small functions, and the TLS servers (OpenSSL, loaded at run time).
```

`src/std/net.lar`

### interface `Connection`
A connection both ways: a TcpSocket and a TlsSocket are one, and so is what a TlsProvider (std.net.tls) gives. Whoever speaks a protocol (std.net.http, a server's onConnect) works on a Connection, so it does not care whether it is encrypted.

- `function read(buffer: byte[]): int32 throws IoError`  
  Reads what has arrived, up to the length of buffer; 0 when the other side closed.

- `function write(bytes: byte[]): void throws IoError`  
  Writes all the bytes, or throws.

- `function writeText(text: String): void throws IoError`  
  Writes a text (its UTF-8 bytes).

- `function flush(): void throws IoError`

- `function close(): void throws IoError`

- `function input(): InputStream`  
  The connection as an InputStream: for a Reader, or copy().

- `function output(): OutputStream`  
  The connection as an OutputStream.

### enum `NetError`
Why something of the network failed.

`function message(e: NetError): String`  
"connection refused", "host not found: example.org"...

### class `TcpSocket implements InputStream, OutputStream, Closeable, Connection`
A TCP connection.

- `socket: Socket?`

- `readLimit: int32`

- `writeLimit: int32`

- `deadline: int64`

- `static function connect(host: String, port: int32): TcpSocket throws NetError`  
  Connects to host:port (a name or an IP, v4 or v6).

- `function live(): Socket throws IoError`  
  The socket, or an IoError when it is closed.

- `function prepare(writing: bool): void throws IoError`  
  Before a read or a write: with a deadline, the wait is what is left of it (or the limit, when shorter), and past it the call fails with IoError.TimedOut. A client that sends one byte at a time cannot keep the connection longer than its deadline.

- `override function read(buffer: byte[]): int32 throws IoError`  
  Reads what has arrived, up to the length of buffer; 0 when the other side closed.

- `override function write(bytes: byte[]): void throws IoError`  
  Writes all the bytes, or throws.

- `override function writeText(text: String): void throws IoError`  
  Writes a text (its UTF-8 bytes).

- `override function input(): InputStream`

- `override function output(): OutputStream`

- `override function flush(): void throws IoError`  
  Nothing to do: what is written goes to the system at once (TCP_NODELAY).

- `function setTimeout(ms: int32): void`  
  How long read and write wait before failing with a timeout (0: no limit).

- `function finishWriting(): void`  
  Says that nothing more will be written: the other side reads the end, and can still answer.

- `function isOpen(): bool`

- `function handle(): Socket?`  
  The socket of the system, for a C library that works on an open connection (a TLS library): an extern function that takes a Socket receives the descriptor (a SOCKET on Windows). It stays this object's: it is closed with it.

- `function number(): int64`  
  Its number for the system (the descriptor): what an EventLoop watches; -1 once closed.

- `function localPort(): int32`  
  The local port of the connection.

- `override function close(): void throws IoError`  
  Closes it now; otherwise it closes when its memory is freed.

### class `TcpListener implements Closeable`
Waits for connections on a port.

- `socket: Socket?`

- `static function bind(host: String, port: int32): TcpListener throws NetError`  
  Listens on host:port ("0.0.0.0" or "::" for every address; port 0: one the system chooses).

- `function accept(): TcpSocket throws NetError`  
  Waits for the next connection.

- `function port(): int32`  
  The port it listens on (the one the system chose, after bind with port 0).

- `function number(): int64`  
  Its number for the system (the descriptor): what an EventLoop watches; -1 once closed.

- `override function close(): void throws IoError`

### synchronized class `StopSignal`
Tells a server to stop: give one to its literal (stop: quit) and call quit.stop() from anywhere, the handler included. The server notices within a fifth of a second and run() returns after the requests being served.

- `stopped: bool`

- `function stop(): void`

- `function isStopped(): bool`

### class `TcpServer`
A TCP server, plain or with TLS (https): it listens on host:port and gives each connection to onConnect, in one of its threads. let server: TcpServer = { port: 8080, // host: "127.0.0.1" unless you say "0.0.0.0" threads: 16, // connections served at the same time stop: quit, // a StopSignal (also Ctrl+C and SIGTERM, after os.catchTermination()) onConnect: (client: Connection) -> { ... } // thread safe: checked like the run of a Thread }; server.run(); With `tls: OpenSslProvider.load("fullchain.pem", "privkey.pem")` it is https: onConnect gets the connection already decrypted (a TlsSocket). Without keepAlive, the connection closes when onConnect returns. With keepAlive, it stays open, and when the client sends again onConnect is called again with it; onConnect ends it with close(). When a kept client closes, onConnect is called once more and its first read gives 0 (a Reader's readLine, null): close it then. A plain connection that waits for its next request does not hold a thread: one thread (the one of run) watches all of them with poll. (A TLS one keeps its thread while it waits, for now.) The limits, with the values of servers like nginx and Tomcat: - readTimeout, writeTimeout (30 s): how long one read or one write may wait; - requestTimeout (60 s): how long one call of onConnect may read and write in all: a client that sends one byte at a time cannot keep a thread longer; - idleTimeout (75 s): how long a kept connection may wait for its next request; - maxQueue (100): connections waiting for a free thread; more are closed at once. A limit of 0 means none. When one is passed, reads and writes fail with IoError.TimedOut.

- `host: String`

- `port: int32`

- `threads: int32`

- `stop: StopSignal?`

- `tls: OpenSslProvider?`

- `handshakeTimeout: int32`  
  How long a client has to finish the TLS handshake (ms).

- `readTimeout: int32`

- `writeTimeout: int32`

- `requestTimeout: int32`

- `idleTimeout: int32`

- `maxQueue: int32`

- `keepAlive: bool`

- `onConnect: (Connection) -> void thread safe`

- `function run(): void throws NetError`  
  Listens and serves until its StopSignal says stop (or os.catchTermination() saw Ctrl+C or SIGTERM). Throws when it cannot listen.

### class `EventLoop`
Waits on many sockets at once, by their numbers (TcpSocket.number()): watch them, wait, and see which are ready to read (or were closed). It is the loop of TcpServer's own thread: the listener and the kept connections that wait for their next request. let loop: EventLoop = {}; loop.watch(listener.number()); while (true) { loop.wait(200); // ms at most for (i in 0..loop.count()) { if (loop.isReady(i)) { ... loop.socket(i) ... } } } unwatch(i) puts the last one in place i: walk the sockets from the end when taking some out. It uses poll (WSAPoll on Windows): enough for thousands of connections; epoll and kqueue would be its next step.

- `fds: int64[*]`

- `since: int64[*]`

- `ready: int32[*]`

- `function watch(number: int64): void`  
  Watches one more socket (its number); it is the last one, count() - 1.

- `function unwatch(i: int32): void`  
  Stops watching the one in place i (the last one takes its place).

- `function count(): int32`

- `function socket(i: int32): int64`

- `function waited(i: int32): int64`  
  ms since the one in place i was watched.

- `function isReady(i: int32): bool`  
  After wait: the one in place i can be read without waiting (or was closed).

- `function wait(ms: int32): int32`  
  Waits until one of them is ready, or ms pass; how many are ready (0: none, -1: error).

### struct `Address`
Where a datagram comes from or goes to: an IP (or a name, to send) and a port.

- `host: String`

- `port: int32`

### struct `Datagram`
What receive() got: how many bytes of the buffer, and from where.

- `length: int32`

- `from: Address`

### class `UdpSocket implements Closeable`
A UDP socket: datagrams, each one whole, with no connection. Bound to a port to receive (a server), or to any port the system chooses (open(), a client); both send with sendTo. let socket: UdpSocket = UdpSocket.open(); socket.sendTo("ping".bytes(), Address { host: "127.0.0.1", port: 9000 }); let data: byte[*] = buffer(1500); let got: Datagram = socket.receive(data); // waits for one

- `socket: Socket?`

- `family: int32`

- `static function bind(host: String, port: int32): UdpSocket throws NetError`  
  Receives on host:port ("0.0.0.0" or "::" for every address; port 0: one the system chooses).

- `static function open(): UdpSocket throws NetError`  
  A socket to send from (IPv4), on a port the system chooses; the answers come back to it.

- `function sendTo(bytes: byte[], to: Address): void throws NetError`  
  Sends bytes as one datagram (it may be lost: UDP does not resend).

- `function receive(buffer: byte[]): Datagram throws NetError`  
  Waits for one datagram, into buffer (what does not fit is lost), and says its length and sender.

- `function setTimeout(ms: int32): void`  
  How long receive and sendTo wait before failing with NetError.Timeout (0: no limit).

- `function isOpen(): bool`

- `function port(): int32`  
  The local port (the one the system chose, after open() or bind with port 0).

- `override function close(): void throws IoError`  
  Closes it now; otherwise it closes when its memory is freed.

### class `UdpServer`
A UDP server: it receives on host:port and gives each datagram to onReceive (the socket to answer with, the bytes, who sent them), in one of its threads. Each thread has its own copy of the socket, on the same port, so the answers come from the port the client wrote to. let quit: StopSignal = {}; let server: UdpServer = { port: 9000, threads: 4, stop: quit, onReceive: (socket: UdpSocket, data: byte[], from: Address) -> { socket.sendTo(data, from); } }; server.run(); // until quit.stop()

- `host: String`

- `port: int32`

- `threads: int32`

- `stop: StopSignal?`

- `maxSize: int32`  
  The largest datagram it takes whole (bytes); the rest of a bigger one is lost.

- `onReceive: (UdpSocket, byte[], Address) -> void thread safe`

- `function run(): void throws NetError`  
  Receives and serves until its StopSignal says stop. Throws when it cannot bind.

### synchronized class `OpenSslProvider`
The certificate and the key of a TLS server, loaded with OpenSSL. Load it once and give it to as many servers as you want: their threads share it. let tls: OpenSslProvider = OpenSslProvider.load("/etc/letsencrypt/live/example.com/fullchain.pem", "/etc/letsencrypt/live/example.com/privkey.pem");

- `context: TlsContextHandle?`

- `number: int64`

- `static function load(certificate: String, key: String): OpenSslProvider throws NetError`  
  Loads the certificate (with its chain: Let's Encrypt's fullchain.pem) and its private key (PEM files). Throws NetError.Tls when a file cannot be used or the key is not the certificate's, and NetError.TlsUnavailable when there is no OpenSSL.

- `function open(certificate: String, key: String): void throws NetError`

- `function contextNumber(): int64`  
  What a worker gives OpenSSL for each connection (the context, shared by every thread).

### class `TlsSocket implements InputStream, OutputStream, Closeable, Connection`
A connection of a TcpServer with tls, already decrypted: used like a TcpSocket (read, write, writeText, Reader, copy). It closes when its memory is freed.

- `tcp: TcpSocket?`

- `session: TlsSessionHandle?`

- `override function read(buffer: byte[]): int32 throws IoError`  
  Reads what has arrived, up to the length of buffer; 0 when the other side closed.

- `override function write(bytes: byte[]): void throws IoError`  
  Writes all the bytes, or throws.

- `override function writeText(text: String): void throws IoError`  
  Writes a text (its UTF-8 bytes).

- `override function input(): InputStream`

- `override function output(): OutputStream`

- `override function flush(): void throws IoError`

- `function setTimeout(ms: int32): void`  
  How long read and write wait before failing with a timeout (0: no limit).

- `function isOpen(): bool`

- `override function close(): void throws IoError`  
  Closes it now (it tells the client); otherwise it closes when its memory is freed.

---

## std.net.http

```
an HTTP/1.1 client over std.net, with https:// through a TlsProvider (std.net.tls).

  import std.net.http { Client, Request, Response, Header, HttpError, message, get };

  let r: Response = get("https://example.com/");            // a Client {} with the system's TLS
  println("${r.status} ${r.text()}");

  let api: Client = { timeout: 10000, headers: [Header { name: "Authorization", value: "Bearer x" }] };
  let big: Response = api.send({ url: "https://mirror.local/disk.iso" });
  copy(big.body, create("disk.iso"));        // the body is a stream: 4 KB at a time, never all of it

A Client says how to connect (TLS, timeouts, redirections, headers for every request); a Request says
what to ask. send() reads the status line and the headers; the body is read when it is asked for: all
of it with text(), bytes() or json(), or piece by piece from body (an InputStream, so Reader and copy()
work on it). A status like 404 is a response, not an error: HttpError means there was no response.

Everything blocks; there are no threads inside (a request in another thread goes in a Thread of yours).
Memory: a Response, its headers and its connection live where the caller puts the result
(`api.send(req) in scratch` frees all of it, closing the connection, at the end of scratch's block).
Each request has its own connection (Connection: close). A Client is not shared between threads.
```

`src/std/net/http.lar`

### enum `HttpError`
Why there was no response.

`function message(e: HttpError): String`  
"network: connection refused", "bad response: ...", ...

### class `Header`
One header line: "Name: value".

- `name: String`

- `value: String`

### class `Request`
What to ask. Only url is needed: { url: "http://..." } is a GET.

- `method: String`

- `url: String`

- `headers: Header[*]`  
  Sent after the Client's headers.

- `body: String`  
  Sent as it is, with its Content-Length (empty: no body).

- `timeout: int32`  
  How long this request may wait for the server, in ms (0: no limit; -1: the Client's timeout).

### class `Client`
How to connect. Every field has a default: Client {} speaks http:// and https:// (with the system's TLS), waits up to 30 s and follows up to 5 redirections.

- `tls: TlsProvider`  
  What makes https:// connections. Give it your own TlsProvider to use another TLS library.

- `timeout: int32`  
  How long the connection may wait for the server, in ms (0: no limit).

- `maxRedirects: int32`  
  301, 302, 303, 307 and 308 are followed up to this many times (0: not followed).

- `headers: Header[*]`  
  Sent with every request (before the request's own).

- `function send(req: Request): Response throws HttpError`  
  Sends the request and reads the answer up to the end of its headers (following redirections).

- `function get(url: String): Response throws HttpError`  
  A GET.

- `function post(url: String, body: String, contentType: String): Response throws HttpError`  
  A POST with that body and Content-Type.

### class `Body implements InputStream, Closeable`
The body of a response, as an InputStream: it ends where the body ends (Content-Length, the last chunk, or the server closing), whatever the server sends after.

- `tcp: TcpSocket?`

- `connection: Connection?`

- `host: String`

- `from: Reader?`

- `mode: int32`

- `left: int64`

- `done: bool`

- `override function read(buffer: byte[]): int32 throws IoError`

- `function nextChunk(from: Reader): bool throws IoError`  
  Reads the size line of the next chunk; false at the last one (size 0, then trailers).

- `function useTcp(): void`  
  http://: the connection is the TcpSocket.

- `override function close(): void throws IoError`  
  Closes the connection (what was not read is lost).

### class `Response implements Closeable`
What the server answered.

- `status: int32`

- `reason: String`  
  The text after the status: "OK", "Not Found"...

- `headers: Header[*]`

- `url: String`  
  Where the answer came from (after redirections, the last URL).

- `body: Body`

- `function ok(): bool`  
  200 to 299.

- `function header(name: String): String?`  
  The value of the first header with that name (names are compared ignoring case), or null.

- `function bytes(): byte[*] throws HttpError`  
  The whole body (what is left of it) as bytes.

- `function text(): String throws HttpError`  
  The whole body (what is left of it) as text.

- `function json(): Any throws HttpError`  
  The body parsed as JSON (std.encoding.json); not JSON is a BadResponse.

- `override function close(): void throws IoError`  
  Closes the connection now; otherwise it closes when the Response's memory is freed.

`function get(url: String): Response throws HttpError`  
A GET with a Client {} (the system's TLS for https://).

`function post(url: String, body: String, contentType: String): Response throws HttpError`  
A POST with a Client {}.

`function send(req: Request): Response throws HttpError`  
A request with a Client {}.

---

## std.net.openssl

the TLS servers on Unix, over OpenSSL loaded at run time (std.net.tls's client on
Linux uses it too).

`src/std/net/openssl.lar`

### class `LinuxOpenSslNames implements LinuxPlatform`
Where OpenSSL is on Linux, and what to say when it is not there.

### class `MacOSOpenSslNames implements MacOSPlatform`
Where OpenSSL is on macOS (Homebrew), and what to say when it is not there.

### class `OpenSslServers implements UnixPlatform`
The TLS servers on Unix: OpenSSL, loaded at run time (std.net.tls's client on Linux uses it too).

---

## std.net.tls

```
encrypted connections, for https:// (and whatever else needs TLS).

  public interface TlsProvider {
      function connect(host: String, port: int32, timeout: int32): Connection throws NetError;
  }

A Client (std.net.http) has one: SystemTls unless it is given another. Implement TlsProvider to use a
TLS library of your own (mbedTLS, wolfSSL...): it gives back a Connection (read, write, flush, close)
and std.net.http speaks HTTP over it without knowing what is underneath.

SystemTls uses what the system has: Network.framework on macOS, SChannel on Windows, OpenSSL on Linux
(libssl, loaded the first time it is needed, so a program that never uses https:// needs nothing).
When there is none, connect throws NetError.TlsUnavailable saying what is missing.

Everything blocks, like a TcpSocket: there are no threads inside. A connection closes itself when the
memory it lives in is freed.
```

`src/std/net/tls.lar`

### interface `TlsProvider`
What gives encrypted connections.

- `function connect(host: String, port: int32, timeout: int32): Connection throws NetError`  
  An encrypted connection to host:port, after the TLS handshake. It checks the server's certificate as the implementation decides (SystemTls: against the system's trusted certificates, for host). timeout: how long reads and writes may wait, in ms (0: no limit). A failure is a NetError: HostNotFound, Refused, Timeout..., Tls(reason) when the handshake or the certificate fails, TlsUnavailable(what) when there is no TLS to use.

### class `SystemTls implements TlsProvider`
The TLS of the system: Network.framework (macOS), SChannel (Windows), OpenSSL (Linux and others). verify: false accepts any certificate, for tests against a local server with one of its own.

- `verify: bool`

- `override function connect(host: String, port: int32, timeout: int32): Connection throws NetError`

---

## std.net.tls.openssl

the TLS client on Linux, over the OpenSSL of std.net's servers.

`src/std/net/tls/openssl.lar`

### class `OpenSslTls implements LinuxPlatform`
Linux: OpenSSL, loaded at run time (std.net's, shared with its TLS servers).

---

## std.os

```
the environment the program runs in.

  import std.os;
  let home: String = os.env("HOME") ?? "/";

The system is std.platform's Platform.current(); what differs between systems is a class for each, in
std/os/posix.lar, macos.lar and windows.lar.
```

`src/std/os.lar`

`function processId(): int64`  
The number the system gives this running program (its process id).

`function env(name: String): String?`  
The value of an environment variable, or null if it is not set.

`function cwd(): String`  
The folder the program runs in.

`function runCommand(command: String): int32`  
Runs a command line with the system's shell (sh, or cmd.exe on Windows), waits for it, and gives its exit code. To run a program and talk to it, std.os.process.Process.

`function programPath(): String`  
This program's executable (its full path), or "" if it cannot be known.

`function programDir(): String`  
The folder this program's executable is in, or "" if it cannot be known.

`function exit(code: int32): void`  
Ends the program now with this exit code (memories are not freed first).

`function catchTermination(): void`  
From now on, Ctrl+C and SIGTERM (what systemd, docker stop and kill send) do not end the program at once: they only make terminating() true, so the program can finish what it is doing and end on its own. The servers of std.net look at it: they stop accepting, finish the connections they serve, and run() returns. Nothing changes until this is called.

`function terminating(): bool`  
Whether Ctrl+C or SIGTERM arrived after catchTermination().

---

## std.os.process

```
processes. A Process runs another program, or a task of this one in a copy of it; a
ProcessPool runs many tasks in a few copies. They are used as threads are: start() and join(), submit()
and wait().

  import std.os.process { Process, ProcessError };

  let lsp: Process = { program: "larimarc", args: ["lsp"] };
  lsp.start();                              // throws ProcessError when it cannot start
  lsp.write("Content-Length: 2\r\n\r\n{}");
  let line: String? = lsp.readLine(5000);   // waits up to 5 s; null when nothing came (or it ended)
  lsp.kill();

The literal says what to run (it cannot fail); start() runs it. Its output is read through a pipe,
and every read says how long it may wait, so a program that does not answer never hangs the caller.
Its error output goes where this program's goes, nowhere with `quiet: true`, or into its output (read
with the rest) with `mergeErrors: true`. A Process that is still running when its memory is freed is
killed.

Work of the program itself runs in other processes too: a class that implements Task is work that goes
to a copy of this program with its fields, and what run() gives comes back; a panic there is a
ProcessError here.

  class Resize implements Task {
      let file: String;
      let width: int32;
      override function run(): Any { return Images.resize(self.file, self.width); }
  }

  let p: Process = { run: Resize { file: "casa.jpg", width: 800 } };
  p.start();
  let r: Any = p.join();                    // what run() gave there

  let pool: ProcessPool = { processes: 4 };
  pool.submit(Resize { file: "1.jpg", width: 800 });
  pool.submit(Resize { file: "2.jpg", width: 800 });
  let all: Any = pool.wait();               // what each run() gave, in the order they were submitted
```

`src/std/os/process.lar`

### enum `ProcessError`
Why a process could not be used.

`function message(e: ProcessError): String`  
A message for the error, in English.

### interface `Task`
Work that runs in another process: a copy of this program, so that a panic or a crash there is only an error here. The object goes there with its fields (numbers, bool, String, optionals and lists of them); what run() gives comes back the same way (a table, a number, a String...). A class that implements it says so itself (implements Task) and extends no other class.

- `function run(): Any`

### class `Process`
A process: another program (`program`, with `args`), or a task of this program (`run`) in a copy of it; one or the other. The literal says what to run; start() runs it, and join() waits for it to end.

- `program: String`  
  The program: a path, or a name looked for in the PATH.

- `args: String[*]`

- `env: String[*]`  
  "NAME=value": added to this program's environment for it.

- `quiet: bool`  
  true: its error output is thrown away (else it goes where this program's goes).

- `mergeErrors: bool`  
  true: its error output comes with its output, read together (it wins over quiet).

- `shareConsole: bool`  
  true: it uses this program's console (input, output, error output); nothing is read or written through it.

- `handle: ProcessHandle?`

- `pending: byte[*]`  
  What was read and not given yet: from `taken` on.

- `taken: int32`

- `chunk: byte[*]`

- `ended: bool`

- `function launch(): String?`  
  Starts it: null when it runs, else why it could not (not found, not allowed).

- `function send(text: String): bool`  
  Writes text to its input: false when it does not read it any more (or never started).

- `function closeInput(): void`  
  Closes its input: it reads the end (a program that reads until the end, like `cat`, then finishes).

- `function readLine(ms: int32): String?`  
  The next line of its output, without the line end (\n or \r\n). Waits up to `ms` milliseconds for it; null when it did not come in time, or the output ended (what is left without a line end is the last line).

- `function read(count: int32, ms: int32): String?`  
  Exactly `count` bytes of its output, as text; waits up to `ms` for them (null if they did not all come).

- `function readAll(ms: int32): String`  
  All of its output until it ends, waiting up to `ms` in total (what came, if it did not end in time).

- `function fill(until: int64): bool`  
  Reads more of its output into `pending`, waiting until `until`: false when nothing came in time.

- `function compact(): void`  
  Drops what was already given.

- `function wait(ms: int32): int32?`  
  Waits up to `ms` (-1: as long as it takes) for it to end: its exit code, or null if it did not end yet.

- `function kill(): void`  
  Ends it now (if it still runs).

- `function started(): bool`  
  Whether it was started (and not given up when it could not start).

- `function hasTask(): bool`  
  True when what it runs is a task of this program, not a program (a Process with `run`).

- `run: Task?`  
  The task to run in a copy of this program (instead of a program).

- `copy: Rpc?`

- `call: int64`

- `joined: bool`

- `override function hasTask(): bool`

- `function start(): void throws ProcessError`  
  Starts it. Throws ProcessError.CannotStart when it cannot (not found, not allowed, nothing to run).

- `function join(): Any throws ProcessError`  
  Waits for it to end: what the task's run() gave, or the exit code of the program. Throws ProcessError.NotRunning when it was not started (or was joined already), Failed when the task did not finish.

- `function write(text: String): void throws ProcessError`  
  Writes text to its input. Throws ProcessError.NotRunning when it does not read it any more.

- `override function kill(): void`  
  Ends it now (if it still runs).

`function findProgram(name: String): String?`  
Where a program is found in the PATH (with .exe on Windows), or null. A path with a folder is checked as it is.

### class `ProcessPool`
Runs tasks in up to `processes` copies of this program, each one a task at a time: let pool: ProcessPool = { processes: 8 }; pool.submit(task); ... let all: Any = pool.wait(); The copies start as tasks arrive and stay for the next ones until the pool's memory goes.

- `processes: int32`  
  How many processes at most (they start when there is work for them).

- `workers: Rpc[*]`

- `busy: int32[*]`  
  For each worker, the task it runs (its place among the submitted ones), or -1.

- `ids: int64[*]`

- `queued: Any`  
  What goes for each task submitted and not sent yet.

- `sent: int32`

- `results: Any`

- `done: int32`

- `function submit(task: Task): void throws ProcessError`  
  Runs the task in one of the processes, as soon as one is free (it does not wait for it).

- `function wait(): Any throws ProcessError`  
  Waits until every task submitted so far has finished: what each run() gave, in the order they were submitted. Throws ProcessError.Failed when one did not finish (the others are dropped too).

- `function dispatch(): void throws ProcessError`  
  Sends queued tasks to free workers, starting workers up to `processes`.

- `function reset(): void`  
  Drops the workers and the tasks: a new start for whatever comes next.

`function serveTasks(): int32`  
What a copy of this program started for tasks does instead of its main (the compiler calls it when LARIMAR_PROCESS is set): it runs the tasks it is sent until it is closed.

---

## std.os.rpc

```
calls to another program, and a program that answers them (JSON-RPC 2.0).

  import std.os.rpc { Rpc, RpcCall, RpcError, serve };
  import std.os.process { Process };

  // the program that calls
  let calc: Rpc = Rpc.startShared(Process { program: "./calc" });   // a Larimar program that serves
  let sum: Any = calc.call("add", { a: 2, b: 3 });                   // 5
  calc.close();                                                      // it ends when it sees the end

  // the program that answers (./calc)
  function main(): int32 {
      serve((call) -> {
          if (call.method == "add") { return (call.params.a as int64 ?? 0) + (call.params.b as int64 ?? 0); }
          call.fail(-32601, "no method ${call.method}");
          return null;
      });
      return 0;
  }

The Process says what runs (program, args, env, quiet...), and Rpc starts it and talks to it. Each
message is JSON with a Content-Length header before it, as in LSP. Rpc.start talks to any program
through its standard input and output (the program writes nothing else there); Rpc.startShared talks to
a Larimar program through two streams of shared memory (std.os.sharedmemory), so its own output stays its
own and the bytes do not go through the system. serve() answers on the shared streams it was started with,
or else on its standard input and output; it returns when the caller closes. Rpc.over and serveOver do
the same on any pair of streams (a socket, for example).

A call waits for its answer (timeout: how long, 0 for as long as it takes). If the other program ends,
the call throws RpcError.Ended with its exit code instead of waiting.
```

`src/std/os/rpc.lar`

### enum `RpcError`
What went wrong with a call.

`function message(e: RpcError): String`  
A message for the error, in English.

### class `RpcCall`
One call that came: what it asks for. The handler answers with what it returns, or with fail().

- `method: String`

- `params: Any`

- `code: int64`

- `text: String`

- `function fail(code: int64, message: String): void`  
  Answers with an error instead of a result (JSON-RPC: -32601 no such method, -32602 bad params...).

- `function failed(): bool`

### class `Rpc`
A connection to a program that answers calls. It closes when its memory is freed.

- `wire: Wire`

- `process: Child?`

- `nextId: int64`

- `timeout: int32`  
  How long a call may wait for its answer, in ms (0: as long as it takes).

- `static function start(process: Child): Rpc throws RpcError`  
  Starts the program of a Process (std.os.process), which answers JSON-RPC on its standard input and output (any program): Rpc reads and writes them.

- `static function startShared(process: Child): Rpc throws RpcError`  
  Starts the program of a Process, a Larimar program that answers with serve(): the calls go through shared memory (it adds LARIMAR_RPC to the Process's env), and its standard output stays this console's.

- `static function over(input: InputStream, output: OutputStream): Rpc`  
  Calls over two streams that already exist (a socket, for example).

- `function call(method: String, params: Any): Any throws RpcError`  
  Calls `method` and waits for its answer: the result, or RpcError.

- `function begin(method: String, params: Any): int64 throws RpcError`  
  Sends a call and does not wait: its id, for finish (calls to several programs at once).

- `function finish(id: int64): Any throws RpcError`  
  Waits for the answer of the call `id` (what begin gave): the result, or RpcError.

- `function notify(method: String, params: Any): void throws RpcError`  
  Sends `method` without waiting for an answer (a notification: the other program answers nothing).

- `function close(): void`  
  Closes the connection: the other program sees the end (serve returns), and this one waits for it.

- `function stop(): void`  
  Ends the other program now, if this one started it.

`function serve(handler: (RpcCall) -> Any): void`  
Answers the calls that come, one after another, with `handler`, until the caller closes: on the shared streams this program was started with (Rpc.startShared), or else on its standard input and output.

`function serveOver(input: InputStream, output: OutputStream, handler: (RpcCall) -> Any): void`  
Answers the calls that come on two streams that already exist, until the input ends.

---

## std.os.sharedmemory

```
memory that several programs see. A stream is a queue (each message once, in
order, from one writer to one reader); a segment is a board (bytes at offsets, the latest value written
there, which any program that opens it reads).

  import std.os.sharedmemory { SharedMemoryOutputStream, SharedMemoryInputStream, SharedMemorySegment };

  // one program
  let out: SharedMemoryOutputStream = SharedMemoryOutputStream.create("frames", 1 << 20);   // 1 MB of shared memory
  out.write(frame);                       // waits while it is full: the other one reads at its pace
  out.close();                            // the reader sees the end after what was written

  // another program
  let input: SharedMemoryInputStream = SharedMemoryInputStream.open("frames", 5000);        // waits up to 5 s for it
  let n: int32 = input.read(buffer);      // 0: the writer closed it and everything was read

A name is the meeting point: one program creates it (as writer or as reader), the other opens it; each
stream has one writer and one reader. The bytes go through a ring in shared memory, with no copy through
the system and no system call while there is something to read or room to write; a side that has to
wait spins for a moment and then sleeps in short steps. If the other program ends without closing, the
waiting side gets IoError.Closed instead of waiting forever. The name is freed as soon as the other side
opens it (or when the creator closes it). A stream closes itself when its memory is freed.

  // a segment: one program creates it, others open it
  let board: SharedMemorySegment = SharedMemorySegment.create("scores", 4096);
  board.putInt64(0, 42);
  let seen: SharedMemorySegment = SharedMemorySegment.open("scores", 5000);    // in another program
  let n: int64 = seen.getInt64(0);                                             // 42

Every get and put is checked against the segment's size (outside it: a panic, as an index of a list).
An int64 at an offset that is a multiple of 8 is read and written whole: whoever reads a value with
getInt64 also sees what was written before it was put (a number of frame, a flag of "ready"). The name
stays while its creator has it open.

The streams are streams like a file or a socket: a Reader, copy(), and anything that takes an InputStream or an
OutputStream works with them. Names: letters, digits, '.', '_' and '-', at most 26 of them;
uniqueName("rpc") gives one that no other program uses.
```

`src/std/os/sharedmemory.lar`

`function uniqueName(prefix: String): String`  
A name for a new stream that no other program uses: the prefix (at most 8 bytes), this program's id, a count.

### class `SharedMemoryOutputStream implements OutputStream, Closeable`
The writing side of a stream between two programs.

- `name: String`

- `handle: SharedHandle?`

- `timeout: int32`  
  How long a write may wait for room, in ms (0: as long as it takes).

- `static function create(name: String, capacity: int32): SharedMemoryOutputStream throws IoError`  
  Creates the stream `name` with room for `capacity` bytes (at least 4096); the other program opens it as a reader.

- `static function open(name: String, ms: int32): SharedMemoryOutputStream throws IoError`  
  Opens the stream `name` that a reader created, waiting up to `ms` for it to exist (0: only now).

- `override function write(bytes: byte[]): void throws IoError`  
  Writes all the bytes, waiting while the ring is full. IoError.Closed: the reader closed it, or ended.

- `override function flush(): void throws IoError`  
  Nothing to do: what is written is already there for the reader.

- `override function close(): void throws IoError`  
  The end: the reader reads what was written, then 0.

- `function capacity(): int64`  
  How many bytes the ring holds.

### class `SharedMemoryInputStream implements InputStream, Closeable`
The reading side of a stream between two programs.

- `name: String`

- `handle: SharedHandle?`

- `timeout: int32`  
  How long a read may wait for bytes, in ms (0: as long as it takes); then IoError.TimedOut.

- `static function create(name: String, capacity: int32): SharedMemoryInputStream throws IoError`  
  Creates the stream `name` with room for `capacity` bytes (at least 4096); the other program opens it as a writer.

- `static function open(name: String, ms: int32): SharedMemoryInputStream throws IoError`  
  Opens the stream `name` that a writer created, waiting up to `ms` for it to exist (0: only now).

- `override function read(buffer: byte[]): int32 throws IoError`  
  Fills buffer with what has arrived (waiting until something does): how many bytes; 0 when the writer closed the stream and everything was read. IoError.Closed: the writer ended without closing it.

- `function available(): int64`  
  How many bytes can be read now, without waiting.

- `override function close(): void throws IoError`  
  Stops reading: the writer's next write gets IoError.Closed.

### class `SharedMemorySegment implements Closeable`
Memory that several programs see, by name: bytes at offsets, read and written with get and put. One program creates it; the others open it. It closes itself when its memory is freed.

- `name: String`

- `handle: SharedHandle?`

- `bytes: int64`

- `static function create(name: String, size: int32): SharedMemorySegment throws IoError`  
  Creates the segment `name` with `size` bytes (all 0); other programs open it by its name.

- `static function open(name: String, ms: int32): SharedMemorySegment throws IoError`  
  Opens the segment `name` that another program created, waiting up to `ms` for it to exist (0: only now).

- `function size(): int64`  
  How many bytes it has.

- `function getInt64(offset: int64): int64`

- `function putInt64(offset: int64, value: int64): void`

- `function getInt32(offset: int64): int32`

- `function putInt32(offset: int64, value: int32): void`

- `function getFloat64(offset: int64): float64`

- `function putFloat64(offset: int64, value: float64): void`

- `function getByte(offset: int64): byte`

- `function putByte(offset: int64, value: byte): void`

- `function getBytes(offset: int64, into: byte[]): void`  
  Copies into `into` the bytes from `offset` on (as many as `into` has).

- `function putBytes(offset: int64, bytes: byte[]): void`  
  Writes `bytes` from `offset` on.

- `override function close(): void throws IoError`  
  Lets it go: the name is freed when its creator closes it; what other programs mapped stays theirs.

- `function at(offset: int64, count: int64): SharedHandle`  
  The handle, when `count` bytes from `offset` are inside the segment; a panic when they are not.

---

## std.platform

```
the system the program is built for, and the marks of the classes that are for one.

  import std.platform { Platform, OS };
  if (Platform.current() == OS.Windows) { ... }

What differs between systems is a class for each, marked with the platform it is for (implements
UnixPlatform, LinuxPlatform, MacOSPlatform or WindowsPlatform), with the C of that system in it: its C
reaches only that system's build. A switch on Platform.current() chooses the one that runs (with
--target, the compiler chooses it). This module imports nothing: every part of std can mark its classes.
```

`src/std/platform.lar`

### enum `OS`
The systems Larimar runs on (Unix: another Unix, a BSD).

### interface `Platform`
What a class is for: a class that implements one of these is for that platform. Its C (cinclude, ccode, the C bodies of its methods) reaches only that system's build; elsewhere its methods with C panic.

- `static function current(): OS`  
  The system this program was compiled for.

- `static function name(): String`  
  Its name: "linux", "macos", "windows" or "unix".

### interface `UnixPlatform extends Platform`

### interface `LinuxPlatform extends UnixPlatform`

### interface `MacOSPlatform extends UnixPlatform`

### interface `WindowsPlatform extends Platform`

---

## std.test

```
the checks that test functions use (larimar test runs them).

  import std.test { check, checkText, checkInt };

  test function addsUp(): void {
      checkInt(4, 2 + 2);
      checkText("hola 3", "hola ${1 + 2}");
  }

A check that fails prints why, and the test goes on (to stop there, `return`). The test fails when
any of its checks failed. Each test runs alone, in its own process, so nothing is shared between tests.
```

`src/std/test.lar`

`function check(condition: bool, message: String): void`  
Fails when the condition is false, with this message.

`function checkText(expected: String, actual: String): void`  
Fails when the two texts differ.

`function checkInt(expected: int32, actual: int32): void`  
Fails when the two numbers differ.

`function checkInt64(expected: int64, actual: int64): void`  
Fails when the two numbers differ (int64).

`function checkFloat(expected: float64, actual: float64, tolerance: float64): void`  
Fails when the two numbers are further apart than `tolerance`.

`function fail(message: String): void`  
Fails, with this message.

`function skip(reason: String): void`  
Skips the test: it cannot run here (a program it needs is not installed, another platform). Say why; larimar test shows it as skipped, not passed. Then `return`.

`function skipReason(): String`  
Why the running test was skipped, or "" (larimar test asks it when the test ends).

`function failedChecks(): int32`  
How many checks of the running test failed (larimar test asks it when the test ends).

### interface `TestSetup`
What a test needs ready before it runs, and cleaned after: `test function name(s: MySetup)`. For each test, larimar test makes a new MySetup {} (so its fields need default values), calls beforeEach(), the test, and afterEach() (always, also when a check failed). When a check fails in beforeEach(), the test does not run.

- `function beforeEach(): void`

- `function afterEach(): void`

---

## std.text

```
helpers for reading text byte by byte (lexers, parsers).

  import std.text;
  if (text.isDigit(source[i])) { ... }

Bytes are ASCII-aware: letters with accents are several bytes in UTF-8 and are not
letters here; use String.codePoints() for those.
```

`src/std/text.lar`

`function isDigit(b: byte): bool`

`function isHexDigit(b: byte): bool`

`function isLetter(b: byte): bool`

`function isLetterOrDigit(b: byte): bool`

`function isIdentifierPart(b: byte): bool`  
A letter, a digit or _: a byte of a name in most languages.

`function isSpace(b: byte): bool`  
Space, tab, newline, carriage return.

`function isUpper(b: byte): bool`

`function isLower(b: byte): bool`

`function digitValue(b: byte): int32?`  
The value of a digit (0-9, a-f, A-F), or null.

`function isAscii(s: String): bool`  
Is every byte ASCII (below 128)?

`function fromCode(code: int32): String`  
The text of one Unicode character (its UTF-8 bytes); a code that is not a character gives U+FFFD.

---

## std.text.regex

```
regular expressions, written in Larimar (no C library: the same on every system).

  import std.text.regex { Regex, Match };
  let email: Regex = Regex.compile("([a-z]+)@([a-z]+)\\.com");
  let m: Match? = email.find("write to ana@mail.com");
  if (m != null) { println(m.group(1) ?? ""); }          // ana

What a pattern can say:
  a  \.  \n \t \r       a character (\ before a sign takes it as it is)
  .                      any character but \n
  [abc] [a-z] [^0-9]     one of them, a range, none of them
  \d \w \s  \D \W \S     a digit, a letter/digit/_, a space; and their opposites
  ^ $  \b \B             start, end, a word boundary, not a boundary
  * + ? {n} {n,} {n,m}   repeated (as many as possible); with a ? after, as few as possible
  (x) (?:x)  x|y         a group (captured, or not), one or the other

The classes (\d, \w, [a-z]...) are ASCII; a letter with an accent is one character for '.' and [^...].
It checks each place of the text once per instruction at most: no pattern makes it take forever.
```

`src/std/text/regex.lar`

### enum `RegexError`
A pattern that cannot be compiled: why, and where (the byte of the pattern).

`function message(e: RegexError): String`  
"missing ')' at 7".

### class `Match`
A place where the pattern matched.

- `start: int32`  
  Where it starts and ends in the text (bytes, the end not included).

- `end: int32`

- `value: String`  
  What it matched.

- `groups: String[*]`  
  groups[i]: what group i matched ("" if it took no part); groups[0] is the whole match.

- `spans: int32[*]`  
  spans[2i], spans[2i+1]: where group i starts and ends (-1 if it took no part).

- `function group(i: int32): String?`  
  What group i matched, or null if it took no part (0 is the whole match).

### class `Regex`
A compiled pattern.

- `pattern: String`

- `op: int32[*]`

- `x: int32[*]`

- `y: int32[*]`

- `lo: byte[*]`  
  Classes: ranges lo..hi from clsFirst[k], clsCount[k] of them; clsNeg[k] 1 for [^...].

- `hi: byte[*]`

- `clsFirst: int32[*]`

- `clsCount: int32[*]`

- `clsNeg: byte[*]`

- `groupCount: int32`  
  Groups, the whole match counted.

- `pos: int32`  
  while compiling

- `groups: int32`

- `static function compile(pattern: String): Regex throws RegexError`  
  Compiles a pattern; a pattern with an error throws RegexError.

- `function fail(reason: String): void throws RegexError`

- `function emit(o: int32, a: int32, b: int32): int32`

- `function here(): int32`

- `function more(): bool`

- `function peek(): byte`

- `function cut(n: int32): void`  
  Forgets the code from `n` on (to write it again, wrapped).

- `function alternation(): void throws RegexError`  
  x|y|z: each branch is compiled, then again after a SPLIT once a '|' says it was one.

- `function concat(): void throws RegexError`

- `function piece(): void throws RegexError`  
  An atom and its repetition: the atom is compiled, and again as often as the repetition says.

- `function choose(split: int32, more: int32, done: int32, lazy: bool): void`  
  SPLIT to `more` first (as many as possible), or to `done` first when lazy.

- `function again(atomPos: int32, atomGroups: int32): void throws RegexError`  
  Compiles the atom at `atomPos` once more (its groups keep their numbers).

- `lastMin: int32`

- `lastMax: int32`

- `function counted(): bool throws RegexError`  
  {n}, {n,}, {n,m} into lastMin/lastMax; false if what follows '{' is not one.

- `function number(): int32`  
  The digits at pos as a number, or -1 if there are none.

- `function atom(): void throws RegexError`

- `function escape(): void throws RegexError`

- `function escaped(e: byte): byte`  
  \n, \t, \r, \f, \v, \0; any other byte after '\' is itself (\. \* \\ ...).

- `function newClass(negated: bool): int32`

- `function range(k: int32, a: byte, b: byte): void`

- `function shorthand(k: int32, e: byte): void`  
  The ranges of \d, \w or \s (in either case: the class says if it is negated).

- `function charClass(): void throws RegexError`  
  [abc], [a-z0-9_], [^"], []a] (a ']' first is a ']').

- `function inClass(k: int32, b: byte): bool`

- `function run(text: String, start: int32, caps: int32[*], seen: byte[], whole: bool): bool`  
  Runs the program from `start`: true if it reaches MATCH (caps then has the groups). Backtracking with its own stack; `seen` remembers each (instruction, place) already tried: trying it again would fail again, so nothing is tried twice. whole: only a match that ends at the end counts.

- `function findFrom(text: String, from: int32, whole: bool): Match?`  
  The first match at `from` or after, or null.

- `function matches(text: String): bool`  
  Does the pattern match the whole text?

- `function contains(text: String): bool`  
  Does it match somewhere in the text?

- `function find(text: String): Match?`  
  The first match, or null.

- `function findAll(text: String): Match[*]`  
  Every match, one after the other (an empty match moves one character on).

- `function replace(text: String, replacement: String): String`  
  The text with every match replaced: $0 is the match, $1..$9 its groups, $$ a '$'.

- `function split(text: String): String[*]`  
  The pieces of the text between the matches.

---

## std.thread

```
a pool of threads for a batch of tasks.

  import std.thread { ThreadPool };
  let pool: ThreadPool = { threads: 8 };
  for (file in files) {
      let name: String = file;
      pool.submit(() -> { resize(name); });          // runs on one of the 8 threads
  }
  pool.wait();                                       // until every task submitted has finished

A task is a function () -> void thread safe: what it captures has to be safe to share (values, and
synchronized objects). The threads start as tasks arrive (at most `threads`) and end when there is none
left; when the pool's memory goes, they are joined. queue > 0 bounds the tasks waiting: submit waits
while that many have not started.

The tasks live in the pool's memory until the pool goes: a pool is for a batch (a folder of images, the
requests of a test), made where the batch is. For a server that runs forever, std.net.TcpServer has its
own workers, which take values and keep nothing.
```

`src/std/thread.lar`

### class `ThreadPool`
Runs tasks on up to `threads` threads: let pool: ThreadPool = { threads: 8 }; pool.submit(() -> { ... }); queue > 0: submit waits while that many tasks have not started.

- `threads: int32`

- `queue: int32`

- `tasks: TaskQueue`

- `workers: Thread[*]`

- `bounded: bool`

- `function submit(task: () -> void thread safe in self): void`  
  Runs the task on one of the pool's threads (it waits first if the queue is full).

- `function wait(): void`  
  Waits until every task submitted so far has finished.

---

## std.time

```
the clock, waiting, and dates as text.

  import std.time as Time;
  let started: int64 = Time.monotonic();
  Time.sleep(250);
  println("${Time.monotonic() - started} ms");               // about 250
  println(Time.httpDate(Time.now()));                         // Mon, 02 Nov 2026 23:04:00 GMT
  println(Time.isoDate(Time.now()));                          // 2026-11-02T23:04:00Z

now() is the wall clock (it can jump when the system's clock is set); monotonic() only moves forward,
so it is the one for measuring time and for deadlines. Dates are UTC.
```

`src/std/time.lar`

`function now(): int64`  
Milliseconds since 1970-01-01 00:00 UTC (the wall clock).

`function monotonic(): int64`  
Milliseconds from some fixed moment, only ever forward: for measuring time and for deadlines.

`function sleep(ms: int64): void`  
Waits that many milliseconds (this thread only).

### struct `DateTime`
A moment split into its parts, in UTC.

- `year: int32`

- `month: int32`

- `day: int32`

- `hour: int32`

- `minute: int32`

- `second: int32`

- `millisecond: int32`

- `weekday: int32`

`function fromMillis(ms: int64): DateTime`  
The parts of a moment (milliseconds since 1970, as now() gives).

`function toMillis(t: DateTime): int64`  
Milliseconds since 1970 of these parts (UTC); weekday is not used.

`function httpDate(ms: int64): String`  
The date of HTTP (Date, Last-Modified, the Expires of a cookie): "Mon, 02 Nov 2026 23:04:00 GMT".

`function isoDate(ms: int64): String`  
ISO 8601 in UTC: "2026-11-02T23:04:00Z".

`function parseIsoDate(text: String): int64?`  
An ISO 8601 date in UTC ("2026-11-02", "2026-11-02T23:04:00Z", "2026-11-02T23:04:00.250Z") in milliseconds, or null.
