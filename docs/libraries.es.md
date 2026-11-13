# Bibliotecas en Larimar: manual de desarrollo

Este manual recorre **todos los escenarios** de escribir, publicar y usar una biblioteca hecha en Larimar.
Cada escenario trae el código completo, la salida real que dio al ejecutarlo, y qué prueba lo cubre. Está
pensado para seguirlo paso a paso y, de paso, comprobar las reglas de memoria en cada frontera.

Versión descrita: Larimar 1.7.0. La referencia breve está en el [manual, capítulo 27](manual.es.md#27-bibliotecas-escritas-en-larimar).

**Cómo se comprobó.** Todos los ejemplos se ejecutaron en Linux con el detector de errores de memoria
(AddressSanitizer, que incluye la detección de fugas). La columna «Prueba» de cada escenario dice si
está en la suite (`tests/project/libraries_test.lar`, que corre con `./bootstrap/build.sh --verify --test`)
o si se ejecutó a mano para este manual. En Windows y macOS no se ha ejecutado nada de esto.

## Contenido

1. [El modelo en una página](#1-el-modelo-en-una-página)
2. [La regla de memoria: prestado y propio](#2-la-regla-de-memoria-prestado-y-propio)
3. [Escenario: una biblioteca solo en Larimar](#3-escenario-una-biblioteca-solo-en-larimar)
4. [Escenario: clases que cruzan como handles](#4-escenario-clases-que-cruzan-como-handles)
5. [Escenario: intentos de romper la memoria](#5-escenario-intentos-de-romper-la-memoria)
6. [Escenario: C de terceros en código fuente](#6-escenario-c-de-terceros-en-código-fuente)
7. [Escenario: una biblioteca del sistema](#7-escenario-una-biblioteca-del-sistema)
8. [Escenario: C ya compilado](#8-escenario-c-ya-compilado)
9. [Escenario: funciones del programa que la biblioteca llama](#9-escenario-funciones-del-programa-que-la-biblioteca-llama)
10. [Escenario: la biblioteca llama desde otro hilo](#10-escenario-la-biblioteca-llama-desde-otro-hilo)
11. [Escenario: un paquete que usa otro](#11-escenario-un-paquete-que-usa-otro)
12. [Escenario: publicar y usar el .lpk](#12-escenario-publicar-y-usar-el-lpk)
13. [Escenario: entregar la biblioteca a un programa en C](#13-escenario-entregar-la-biblioteca-a-un-programa-en-c)
14. [Escenario: las pruebas de la biblioteca](#14-escenario-las-pruebas-de-la-biblioteca)
15. [Errores y su arreglo](#15-errores-y-su-arreglo)
16. [Qué garantiza el binding generado, y qué no](#16-qué-garantiza-el-binding-generado-y-qué-no)
17. [Límites conocidos y trabajo pendiente](#17-límites-conocidos-y-trabajo-pendiente)

---

## 1. El modelo en una página

Una biblioteca hecha en Larimar es, hacia fuera, **una biblioteca de C con un archivo de bindings**.

```
  src/textkit.lar  ──larimar build──►  build/textkit.lpk          el paquete, en un archivo
                                        build/textkit/             lo mismo, como carpeta:
                                          textkit.c                  la biblioteca traducida a C
                                          textkit.h                  para C
                                          textkit.lar                para Larimar: el binding, generado
                                          textkit.interface          el manifiesto
                                          c/                         el C de terceros que trae
```

- **Quien la usa desde Larimar** nombra el `.lpk` en `[packages]` de su `larimar.toml` y escribe
  `import textkit;`. El C del paquete se compila junto con su programa, en cualquier sistema.
- **Quien la usa desde C** incluye `textkit.h` y compila `textkit.c`, o enlaza la biblioteca ya
  compilada (`larimar build --static` o `--dynamic`).
- **Cada biblioteca lleva su propio runtime**, privado. Dos bibliotecas y el programa no comparten
  memoria ni nombres: solo cruzan números, textos (copiados), objetos (como *handles*) y callbacks.

Lo que cruza la frontera:

| Cruza | En Larimar | En C |
|---|---|---|
| Números y `bool` | `int32`, `float64`, `bool`… | `int32_t`, `double`, `bool`… |
| Textos | `String`, `String?` | `const char*` al entrar, `char*` al salir (`NULL` es `null`) |
| Objetos de la biblioteca | una clase, o `Clase?` | un handle: `tk_Clase*` |
| Funciones del programa | un parámetro de tipo función | un puntero a función y un `void*` |

Lo que **no** cruza: listas, tablas, `Any`, structs, interfaces y errores (`throws`).
Lo que no cruza se queda dentro, y el binding lo dice en un comentario.

---

## 2. La regla de memoria: prestado y propio

Todo el contrato cabe en una frase:

> **La biblioteca nunca libera nada tuyo. Tú liberas solo lo que una función de la biblioteca te devuelve.**

| Qué cruza | De quién es | Quién libera |
|---|---|---|
| Un texto que le pasas a la biblioteca | tuyo (prestado durante la llamada) | tú; si ella lo guarda, guarda una copia |
| Un texto que la biblioteca te devuelve | tuyo | tú: `<prefijo>_free` |
| Un objeto que la biblioteca te devuelve | tuyo | tú: `<prefijo>_<Clase>_release` |
| Un objeto que le pasas a la biblioteca | tuyo (prestado) | tú |
| Lo que recibe una función tuya que la biblioteca llama | de la biblioteca | nadie de tu lado |
| El texto que da esa función | pasa a la biblioteca, que lo guarda en su memoria | nadie de tu lado |

En **C** esta regla la cumple el programador. En **Larimar** la cumple el compilador: el binding lleva
`released by` en cada texto y cada clase, y el programa no escribe ninguna liberación.

---
## 3. Escenario: una biblioteca solo en Larimar

**Prueba:** `aPackageIsCompiledWithTheProgram` (suite) y ejecución a mano con el detector de memoria.

El proyecto de la biblioteca:
```toml
[project]
name = "textkit"
version = "1.0.0"
kind = "library"
main = "src/textkit.lar"

[library]
prefix = "tk"
```
`src/textkit.lar`:
```ts
/** Cuenta las palabras de un texto. */
public export function wordCount(text: String): int32 {
    let n: int32 = 0;
    for (w in text.split(" ")) {
        if (w != "") { n += 1; }
    }
    return n;
}

/** El texto con su primera letra en mayúscula. */
public export function title(text: String): String {
    if (text == "") { return ""; }
    return "${text.substring(0, 1).toUpperCase()}${text.substring(1)}";
}

/** La primera palabra, o null si no hay ninguna. */
public export function firstWord(text: String?): String? {
    if (text == null) { return null; }
    for (w in text!.split(" ")) {
        if (w != "") { return w; }
    }
    return null;
}
```
```sh
larimar build
# built build/textkit.lpk, the package in one file, and build/textkit/: textkit.c, textkit.h, textkit.lar, textkit.interface
```

Puntos a notar:

- `export` marca lo que sale de la biblioteca. `public` además deja que sus pruebas y sus otros módulos la llamen desde Larimar.
- `prefix = "tk"` da los nombres de C: `tk_wordCount`. Sin `prefix`, se usa el nombre del proyecto.
- `String?` cruza como un puntero que puede ser `NULL`.

### Usarla desde Larimar

`larimar.toml` del programa:
```toml
[project]
name = "app"

[c]
flags = ["-g", "-fsanitize=address"]

[packages]
textkit = "../textkit/build/textkit.lpk"
```
`flags` con `-fsanitize=address` es solo para comprobar la memoria; un programa normal no lo lleva.

`src/main.lar`:
```ts
import textkit;

let kept: String[*] = [] in default;

function main(): int32 {
    println("${textkit.wordCount("uno dos  tres")}");
    for (i in 0..3) {
        let t: String = textkit.title("palabra ${i}");
        kept.push(t.clone() in default);            // para guardarlo más que el bloque: una copia
    }
    println(kept.join(", "));
    println(textkit.firstWord("  hola mundo") ?? "nada");
    println(textkit.firstWord(null) ?? "nada");
    return 0;
}
```
Salida:

```
3
Palabra 0, Palabra 1, Palabra 2
hola
nada
```

**Qué pasa con la memoria.** `textkit.title(...)` devuelve un texto que la biblioteca creó con su
asignador. El binding dice `released by tk_free`, así que el compilador lo copia a la memoria del programa
y libera el original en el acto. `t` vive en el bloque del `for`; para guardarlo en `kept`, que vive todo el
programa, hace falta la copia `t.clone() in default`. Sin ella el compilador lo rechaza (ver sección 5).

### Usarla desde C
```c
#include <stdio.h>
#include "textkit.h"

int main(void) {
    char* t = tk_title("larimar");
    char* w = tk_firstWord("  hola mundo");
    char* none = tk_firstWord(NULL);
    printf("%d %s %s %s\n", tk_wordCount("uno dos  tres"), t, w, none ? none : "nada");
    tk_free(t);
    tk_free(w);
    tk_free(none);                 /* NULL: no hace nada */
    return 0;
}
```
```sh
cc -std=c99 -Ibuild/textkit main.c build/textkit/textkit.c -lm -o demo
./demo
# 3 Larimar hola nada
```

En C, cada `char*` que devuelve la biblioteca se libera con `tk_free`. `tk_free(NULL)` no hace nada.

---
## 4. Escenario: clases que cruzan como handles

**Prueba:** `aStaticLibraryForCAndForLarimar` (suite) y ejecución a mano con el detector de memoria.

Una clase que aparece en una `export function` cruza como **handle**: el programa la tiene, la pasa y la devuelve, sin ver lo que hay dentro. Sus campos se leen y sus métodos se llaman.

`src/bank.lar`:
```ts
/** Una cuenta: su dueño, su saldo y sus movimientos. */
public class Account {
    /** El dueño de la cuenta. */
    let owner: String;
    /** El saldo. */
    let balance: int64 = 0;
    let moves: String[*] = [];

    /** Ingresa una cantidad y anota por qué. */
    function deposit(amount: int64, why: String): void {
        self.balance += amount;
        self.moves.push("${why}: ${amount}");
    }

    /** El último movimiento (null si no hay). */
    function last(): String? {
        if (self.moves.length == 0) { return null; }
        return self.moves[self.moves.length - 1].clone();
    }

    /** Una cuenta nueva con el mismo dueño y el mismo saldo. */
    function copy(): Account { return Account { owner: self.owner.clone(), balance: self.balance }; }
}

/** Abre una cuenta. */
public export function open(owner: String): Account { return Account { owner: owner.clone() }; }

/** Busca una cuenta: null si el nombre está vacío. */
public export function find(owner: String): Account? {
    if (owner == "") { return null; }
    return Account { owner: owner.clone() };
}

/** Pasa una cantidad de una cuenta a otra. */
public export function transfer(from: Account, to: Account, amount: int64): void {
    from.deposit(-amount, "a ${to.owner}");
    to.deposit(amount, "de ${from.owner}");
}
```
El binding que genera `larimar build` (`build/bank/bank.lar`, sin su cabecera):
```ts
public native type Account = bank_Account* released by bank_Account_release {
    // not given to C (they do not cross): moves (String[*])
    native let owner: String = bank_Account_owner released by bank_free;
    native let balance: int64 = bank_Account_balance;
    native function deposit(amount: int64, why: String): void = bank_Account_deposit;
    native function last(): String? = bank_Account_last released by bank_free;
    function copy(): Account { return self.copy_c()!; }
    native function copy_c(): Account? = bank_Account_copy;
}

public function open(owner: String): Account { return open_c(owner)!; }
native function open_c(owner: String): Account? = bank_open;
public native function find(owner: String): Account? = bank_find;
public native function transfer(from: Account, to: Account, amount: int64): void = bank_transfer;
```
Qué dice ese binding:

- `Account` es un **recurso**: cuando la memoria donde vive se cierra, se llama a `bank_Account_release`.
- `moves` es una lista y no cruza: se queda dentro, y el comentario lo avisa.
- Un campo solo se **lee** desde fuera; se cambia con un método.
- Un método que devuelve un objeto nuevo (`copy`) da un handle nuevo, con su propia memoria.

El programa en Larimar:
```ts
import bank;
import bank { Account };

function main(): int32 {
    let ana: Account = bank.open("Ana");
    let luis: Account = bank.open("Luis");
    ana.deposit(100, "nómina");
    bank.transfer(ana, luis, 30);
    println("${ana.owner} ${ana.balance} (${ana.last() ?? "-"})");
    println("${luis.owner} ${luis.balance} (${luis.last() ?? "-"})");
    let otra: Account = luis.copy();
    println("${otra.owner} ${otra.balance} (${otra.last() ?? "-"})");
    let nadie: Account? = bank.find("");
    println(nadie == null ? "no hay cuenta" : "hay cuenta");
    return 0;
}
```
Salida:

```
Ana 70 (a Luis: -30)
Luis 30 (de Ana: 30)
Luis 30 (-)
no hay cuenta
```

El mismo uso desde C:
```c
#include <stdio.h>
#include "bank.h"

int main(void) {
    bank_Account* ana = bank_open("Ana");
    bank_Account* luis = bank_open("Luis");
    bank_Account_deposit(ana, 100, "nomina");
    bank_transfer(ana, luis, 30);
    char* owner = bank_Account_owner(ana);
    char* last = bank_Account_last(ana);
    printf("%s %lld (%s)\n", owner, (long long)bank_Account_balance(ana), last);
    bank_free(owner);
    bank_free(last);
    bank_Account_release(ana);
    bank_Account_release(luis);
    return 0;
}
```
Reglas de los handles:

- Cada handle tiene **su propia memoria**: lo que el objeto crea después (una lista que crece, sus textos) vive ahí y se libera con él.
- `NULL` donde se espera una clase detiene el programa con un mensaje que nombra la función y el parámetro (`bank_Account_deposit: 'self' is NULL`). Donde se espera `Clase?`, es `null`.
- Un programa no crea objetos de la biblioteca con `Account { }` ni extiende sus clases: los hacen sus funciones.
- Un campo cuyo tipo es otra clase no cruza: ese objeto es del primero. Un método que devuelve uno nuevo, sí.

---
## 5. Escenario: intentos de romper la memoria

**Prueba:** ejecutados a mano para este manual, con el detector de memoria. Los marcados con (suite) están además en las pruebas.

Cada caso es un programa Larimar que usa `bank` (sección 4) e intenta algo indebido.

### 5.1 Guardar un handle más tiempo que su bloque

```ts
let all: Account[*] = [] in default;
function main(): int32 {
    for (i in 0..2) {
        let a: Account = bank.open("x${i}");
        all.push(a);
    }
    ...
```

**Rechazado al compilar:**

```
'a' lives in the memory of this block, but the array lives for the whole program.
```

El arreglo es crear el handle donde debe vivir: `let a: Account = bank.open("x${i}") in default;`. Con eso compila y funciona (salida `x0 x1`).

> Nota: el mensaje sugiere `a.clone()`, que para un handle no es el arreglo adecuado. Está anotado en la sección 17.

### 5.2 Usar un objeto después de liberarlo

```ts
let a: Account = bank.open("x");
release(a);
a.deposit(1, "tarde");
```

**Detenido al ejecutar, con un mensaje claro** (no hay acceso a memoria liberada):

```
panic [build/packages/bank/bank.lar:15]: a released Account was used
```

### 5.3 Guardar un texto de la biblioteca en algo que vive más

```ts
let kept: String[*] = [] in default;
...
let a: Account = bank.open("x");
for (i in 0..2) { kept.push(a.owner); }
```

**Aceptado, y es correcto.** El texto se copia directamente a la memoria de `kept` (la del programa entero), porque ahí es donde va el resultado. Salida `x,x`, sin errores del detector.

Lo que **no** se acepta es pasar por una variable del bloque: `let t: String = a.owner; kept.push(t);` se rechaza, porque `t` vive en el bloque. Ahí hace falta `t.clone() in default`.

### 5.4 Devolver un handle desde una función

```ts
function make(n: int32): Account {
    let a: Account = bank.open("cuenta ${n}");
    a.deposit(n as int64, "inicio");
    return a;
}
```

**Aceptado, y es correcto.** El handle se crea en la memoria que indica quien llama. Salida `cuenta 5 5`.

### 5.5 Compartir un handle con un hilo

```ts
let a: Account = bank.open("x") in default;
let t: Thread = { run: () -> { a.deposit(1, "hilo"); } };
```

**Rechazado al compilar:**

```
This thread uses 'a' (bank.Account), which could change while the thread runs.
```

### 5.6 Una función guardada que usa un dato local, y guardar el objeto que recibe (suite)

Ver sección 9.

### 5.7 Un método sobrescrito que devuelve su argumento (suite)

No es de bibliotecas, pero apareció en esta revisión: un método de una subclase que devolvía su argumento, llamado a través de la clase base, dejaba guardar un texto que moría antes. El detector lo confirmó como uso de memoria liberada. Corregido en 1.7.0; prueba `anOverrideMayReturnItsArgument`.

---
## 6. Escenario: C de terceros en código fuente

**Prueba:** `aPackageBringsItsC` (suite).

Es el caso más común: una biblioteca de C pequeña que se distribuye como `.c` y `.h` (un parser, SQLite, zlib). Va **dentro** del paquete y se compila con el programa.

```
tinykit/
  larimar.toml
  src/tinykit.lar
  vendor/tiny/tiny.h
  vendor/tiny/tiny.c
```

```toml
[project]
name = "tinykit"
kind = "library"
main = "src/tinykit.lar"

[c]
include_paths = ["vendor/tiny"]
sources = ["vendor/tiny/tiny.c"]
```

```ts
cinclude "tiny.h";
native function twiceC(n: int32): int32 = tiny_twice;

public export function twice(n: int32): int32 { return twiceC(n); }
public export function shout(text: String): String { return "${text.toUpperCase()}!"; }
```

`larimar build` copia ese C a `c/` dentro del paquete, con la misma ruta, y lo anota en el manifiesto:

```
build/tinykit/c/vendor/tiny/tiny.c
build/tinykit/c/vendor/tiny/tiny.h
```

```toml
sources = ["c/vendor/tiny/tiny.c"]
include_paths = ["c/vendor/tiny"]
```

Reglas:

- Las rutas de `sources` e `include_paths` tienen que estar **dentro** de la carpeta de la biblioteca. Una ruta que sale de ella es un error.
- `include_paths` se copia entero (la carpeta completa); de `sources`, cada archivo.
- Lo que hay en `[c.linux]`, `[c.macos]`, `[c.windows]` y `[c.unix]` se copia todo, y cada sistema compila lo común más lo suyo.
- Quien usa la biblioteca no ve ni instala nada: `tinykit = "libs/tinykit.lpk"` y listo.

La misma prueba comprueba además que **dos paquetes en un programa no chocan**.

---
## 7. Escenario: una biblioteca del sistema

**Prueba:** ejecutado a mano para este manual.

Cuando el C que usa la biblioteca viene con el sistema (o se instala aparte), no se mete en el paquete: se nombra, y el programa lo enlaza.
```toml
[project]
name = "mathkit"
kind = "library"
main = "src/mathkit.lar"

[c.unix]
dynamic_libraries = ["m"]       # la biblioteca matemática del sistema (en Windows va con el compilador)
```
```ts
cinclude "<math.h>";
native function cbrt(x: float64): float64;

/** La raíz cúbica. */
public export function cubeRoot(x: float64): float64 { return cbrt(x); }
```
El manifiesto lo anota por plataforma:

```toml
[library]
links = []

[library.unix]
links = ["-lm"]
```

El programa no escribe nada de eso:
```ts
import mathkit;
function main(): int32 {
    println("${mathkit.cubeRoot(27.0)}");
    return 0;
}
```
Salida: `3.0000000000000004`

A tener en cuenta: esa biblioteca del sistema tiene que estar instalada **donde se construye** el programa y, si es dinámica, **donde se ejecuta**. El paquete no la trae. Si falta al construir, hoy el error es el del enlazador de C (ver sección 17).

---

## 8. Escenario: C ya compilado

**Prueba:** `aPackageBringsCompiledCAndNamesItsPackages` (suite).

Para una biblioteca de C que solo existe como `lib<nombre>.a`. Si el archivo está en las `static_library_paths` de la biblioteca, va dentro del paquete y se enlaza en el programa.

```toml
[project]
name = "tinykit"
kind = "library"
main = "src/tinykit.lar"

[c]
include_paths = ["vendor"]
static_libraries = ["tiny"]
static_library_paths = ["vendor"]        # aquí está vendor/libtiny.a
```

El paquete queda con `c/vendor/libtiny.a`, y el manifiesto con `objects = ["c/vendor/libtiny.a"]`.

Un `.a` es para **un sistema y un procesador**. Para dar uno a cada sistema:

```toml
[c.linux]
static_libraries = ["tiny"]
static_library_paths = ["vendor/linux"]

[c.macos]
static_libraries = ["tiny"]
static_library_paths = ["vendor/macos"]
```

Límites: no hay separación por procesador (Intel y ARM del mismo sistema serían dos paquetes), y un `.a` puesto en `[c]` hace que el paquete sirva solo para la plataforma de ese archivo. Una biblioteca nombrada en `static_libraries` que **no** está en esas carpetas se trata como del sistema (`-l<nombre>`).

---
## 9. Escenario: funciones del programa que la biblioteca llama

**Prueba:** `aLibraryCallsTheProgramBack` y `aCallbackGetsAnObjectAndGivesAText` (suite), y ejecución a mano con el detector de memoria, desde Larimar y desde C.

Una biblioteca recibe una función del programa como **un parámetro de tipo función**, igual que en cualquier código Larimar, y la llama como cualquier función:

```ts
/** Una petición: su ruta y sus parámetros. */
public class Request {
    let path: String;
    let name: String = "";

    /** El valor de un parámetro ("" si no está). */
    function param(key: String): String { return key == "name" ? self.name.clone() : ""; }
}

/** Atiende una petición con `handler` y devuelve la respuesta, con su tamaño. */
public export function serve(path: String, name: String, handler: (Request) -> String): String {
    let req: Request = { path: path.clone(), name: name.clone() };
    let body: String = handler(req);              // vive en este bloque
    return "${body} (${body.length} bytes)";
}
```

No hay nada especial en ese código: ni `Context`, ni tipos de C.

### Desde Larimar

```ts
import webkit;
import webkit { Request };

function main(): int32 {
    let greeting: String = "hola";
    for (i in 0..3) {
        println(webkit.serve("/hi", "ana ${i}", (req: Request) -> { return "${greeting} ${req.param("name")} en ${req.path}"; }));
    }
    return 0;
}
```

Salida:

```
hola ana 0 en /hi (17 bytes)
hola ana 1 en /hi (17 bytes)
hola ana 2 en /hi (17 bytes)
```

Las reglas son las de siempre:

- **`req` es un parámetro.** La lambda lo usa durante la llamada y no puede guardarlo. Es de la biblioteca.
- **El resultado vive donde dice quien llama.** El texto que da la lambda queda en el bloque de `serve` y se limpia al salir de él. Nadie libera nada a mano.
- **La lambda captura lo que necesita** (`greeting`), como cualquier lambda.
- **Si puede fallar, lo maneja dentro:** una lambda no puede lanzar. `'risky' can throw Bad. Lambdas cannot throw: handle it with try/catch inside the lambda.`

Intentos de romperlo, todos ejecutados:

| Intento | Resultado |
|---|---|
| Guardar `req` en una lista global | rechazado: `This value lives in 'req' (owned by the caller), but the array lives longer` |
| Guardarlo en un campo de un objeto que vive más | rechazado, mismo mensaje |
| `release(req)` dentro de la lambda | no le quita el objeto a la biblioteca, que lo sigue usando bien |
| `release(req)` y luego usarlo | detenido: `a released Request was used` |
| Una función con `req: Request in default` | rechazado: `must live as long as the whole program` |

### Desde C

El `.h` da el tipo de la función. C entrega una función y un `void*`, que la función recibe de vuelta en cada llamada:

```c
typedef void (*wk_serve_handler)(wk_Request*, void* data, void* out);
char* wk_serve(const char* path, const char* name, wk_serve_handler handler, void* handler_data);
void wk_give(void* out, const char* text);
```

```c
static void hello(wk_Request* req, void* data, void* out) {
    char text[128];
    char* name = wk_Request_param(req, "name");       /* un texto que devuelve la biblioteca: mío, lo libero */
    snprintf(text, sizeof text, "%s %s", (const char*)data, name);
    wk_free(name);
    wk_give(out, text);                               /* la biblioteca lo copia en el acto */
}

int main(void) {
    char* answer = wk_serve("/hi", "ana", hello, "hola");
    printf("%s\n", answer);                           /* hola ana (8 bytes) */
    wk_free(answer);
    return 0;
}
```

- Una función que da un número lo devuelve con `return`. Una que da un texto lo deja con `<prefijo>_give(out, texto)`, donde `out` es su último argumento: así es la biblioteca la que guarda el texto en su memoria, y C no tiene que reservar nada.
- El `wk_Request*` que recibe es de la biblioteca: no se libera ni se guarda.

### Una función que la biblioteca guarda

Si la biblioteca conserva la función para llamarla después, lo dice con `in default` en el parámetro. Es la anotación normal de Larimar para «esto se queda»:

```ts
let saved: ((int32, String) -> int32)? = null;

public export function keep(visit: (int32, String) -> int32 in default): void {
    saved = visit;
}
```

Sin `in default`, la propia biblioteca no compila:

```
The function 'visit' lives in 'visit' (owned by the caller), but 'saved' lives for the whole program.
```

Y entonces la lambda del programa no puede usar nada que muera antes que el programa:

```ts
let seen: String[*] = [];
evkit.keep((n: int32, label: String) -> { seen.push(label.clone()); return n; });
```

```
C keeps the function given to 'evkit.keep' (in default), so what it uses must live as long as the
whole program, but it lives in the memory of this block. Create what it uses in default.
```

### Qué puede llevar una función que cruza

Parámetros: números, `bool`, `String` y clases de la biblioteca. Resultado: un número, `bool`, `String` o nada. Todavía no: listas, y funciones en **métodos** de una clase (sección 17).

---

## 10. Escenario: la biblioteca llama desde otro hilo

**Prueba:** `aLibraryCallsBackFromAnotherThread`, `aFunctionOfASynchronizedObjectIsThreadSafe` (suite), y ejecución a mano con el detector de hilos (ThreadSanitizer).

Para que varios hilos usen una función, la biblioteca tiene que guardarla en un objeto `synchronized`, y ahí el compilador exige que el tipo lo diga:

```ts
synchronized class Holder {
    let tick: (int32) -> int32 thread safe;
    let total: int32 = 0;
    function fire(i: int32): void { self.total += self.tick(i); }
    function sum(): int32 { return self.total; }
}

/** Llama a `tick` cuatro veces desde otro hilo, y espera a que termine. */
public export function inBackground(tick: (int32) -> int32 thread safe in default): int32 {
    let h: Holder = { tick } in default;
    let t: Thread = { run: () -> { for (i in 0..4) { h.fire(i); } } } in default;
    t.start();
    t.join();
    return h.sum();
}
```

Sin `thread safe`:

```
Field 'tick' of synchronized class 'Holder' is a function that other threads may call:
declare it '(int32) -> int32 thread safe'.
```

El binding lo lleva (`native type inBackground_tick = (int32, Context) -> int32 thread safe;`), y la función del programa se comprueba como el `run` de un hilo. Esto se rechaza:

```ts
let seen: int32[*] = [] in default;
...
bg.inBackground((n: int32) -> { seen.push(n); return n * 2; })
```

```
This 'thread safe' lambda can reach global 'seen', which can change while threads use it.
Keep shared state in an object of a synchronized class.
```

Y esto funciona (salida `12 4`):

```ts
synchronized class Seen {
    let count: int32 = 0;
    function add(): void { self.count += 1; }
    function get(): int32 { return self.count; }
}
...
let seen: Seen = { } in default;
println("${bg.inBackground((n: int32) -> { seen.add(); return n * 2; })} ${seen.get()}");
```

Una biblioteca que llama a la función en el mismo hilo no escribe `thread safe`, y la lambda del programa puede tocar sus datos con libertad.

**Esta sección cerró un fallo del lenguaje, no solo de las bibliotecas.** Antes, un objeto `synchronized` se podía crear alrededor de una función corriente o de una lista que su creador seguía usando, y dos hilos acababan tocando lo mismo sin el candado. El detector de hilos lo confirmó en un programa sin ninguna biblioteca. Ahora un objeto `synchronized` se crea con valores, o con lo que se escribe ahí mismo.

---

## 11. Escenario: un paquete que usa otro

**Prueba:** `aPackageBringsCompiledCAndNamesItsPackages` (suite).

Una biblioteca puede usar otro paquete, igual que un programa:

```toml
[project]
name = "fourkit"
kind = "library"
main = "src/fourkit.lar"

[packages]
tinykit = "../tinykit/build/tinykit.lpk"
```

```ts
import tinykit;
public export function fourTimes(n: int32): int32 { return tinykit.twice(tinykit.twice(n)); }
```

Su manifiesto anota lo que usa: `packages = ["tinykit"]`. **El paquete no lleva dentro al otro.** El programa nombra los dos:

```toml
[packages]
fourkit = "libs/fourkit.lpk"
tinykit = "libs/tinykit.lpk"
```

Si olvida uno, el error lo dice antes de llamar al compilador de C:

```
package 'fourkit' uses the package 'tinykit': name it in [packages] too (tinykit = "...")
```

---

## 12. Escenario: publicar y usar el .lpk

**Prueba:** `aPackageInOneFile` (suite).

`larimar build` deja `build/<nombre>.lpk`. Es **un zip sin comprimir**: lo abre cualquier herramienta.

```sh
unzip -l build/textkit.lpk
#        58  1980-01-01 00:00   c/vendor/tiny/tiny.c
#        23  1980-01-01 00:00   c/vendor/tiny/tiny.h
#     17697  1980-01-01 00:00   textkit.c
#      1552  1980-01-01 00:00   textkit.h
#       482  1980-01-01 00:00   textkit.interface
#       933  1980-01-01 00:00   textkit.lar
```

- No lleva fechas: la misma biblioteca da siempre el mismo archivo, byte a byte.
- Para publicarlo basta subir ese archivo (por ejemplo, a las *releases* de un repositorio).

Quien lo usa lo copia a su proyecto y lo nombra:

```toml
[packages]
textkit = "libs/textkit.lpk"
```

Al construir o comprobar el proyecto se desempaqueta en `build/packages/textkit/`. Solo se vuelve a desempaquetar cuando el archivo cambia, y entonces la carpeta se vacía antes, para que no quede nada del anterior. `larimar check` y el editor también lo encuentran.

Mientras se escribe la biblioteca es más cómodo nombrar la **carpeta**, sin copiar nada:

```toml
[packages]
textkit = "../textkit/build/textkit"
```

No hay una herramienta que descargue paquetes: se copian a mano.

---

## 13. Escenario: entregar la biblioteca a un programa en C

**Prueba:** `aStaticLibraryForCAndForLarimar` y `aDynamicLibrary` (suite).

Tres formas, según lo que quiera quien la recibe:

| Qué | Comando | Resultado | Sirve en |
|---|---|---|---|
| El código C | `larimar build` | `build/textkit/textkit.c` y `textkit.h` | cualquier sistema |
| Biblioteca estática | `larimar build --static` | `build/textkit/libtextkit.a` | el sistema donde se compiló |
| Biblioteca dinámica | `larimar build --dynamic` | `libtextkit.so`, `.dylib` o `.dll` | el sistema donde se compiló |

```sh
# el código C, compilado con el programa
cc -std=c99 -Ibuild/textkit main.c build/textkit/textkit.c -lm -o demo

# estática
larimar build --static
cc -std=c99 -Ibuild/textkit main.c build/textkit/libtextkit.a -lm -o demo

# dinámica (Linux)
larimar build --dynamic
cc -std=c99 -Ibuild/textkit main.c -Lbuild/textkit -ltextkit -Wl,-rpath,$PWD/build/textkit -o demo
```

Las tres dieron la misma salida con el `main.c` de la sección 3: `3 Larimar hola nada`.

- Cada build **reemplaza** al anterior en `build/textkit/`, para no mezclar archivos. El `.lpk` que ya existía no se toca.
- Lo que una estática necesita enlazado además está en `links` de su `.interface` (`-lm`, `-pthread` si usa hilos…).
- `[library] type = "static"` en el toml fija ese tipo sin escribir la opción cada vez.
- El `.h` trae la constante `TEXTKIT_INTERFACE` y la función `tk_interface()`: un programa en C puede comprobar al arrancar que el `.h` y la biblioteca son del mismo build con `strcmp(tk_interface(), TEXTKIT_INTERFACE) == 0`.
- Un pánico dentro de la biblioteca (un índice fuera de rango, un handle `NULL`) lo imprime y termina el programa.

---

## 14. Escenario: las pruebas de la biblioteca

**Prueba:** `theTestsOfALibraryUseItsRules` (suite) y ejecución a mano.

Las pruebas de una biblioteca importan **su código Larimar**, no el paquete: prueban la lógica sin pasar por la frontera.
```ts
import std.test { checkInt, checkText };
import textkit { wordCount, title };

test function countsWords(): void { checkInt(3, wordCount("uno dos  tres")); }
test function titles(): void { checkText("Hola", title("hola")); }
```
```sh
larimar test
#   ok    tests/textkit_test.lar: countsWords
#   ok    tests/textkit_test.lar: titles
# 2 passed, 0 failed
```

Para probar la frontera misma (que el paquete funciona al usarlo), hace falta un programa aparte que lo nombre en `[packages]`, como los de este manual. `larimar test` usa el detector de memoria por defecto donde está disponible.

---

## 15. Errores y su arreglo

| Mensaje | Causa | Arreglo |
|---|---|---|
| `package 'x': libs/x.lpk does not exist` | La ruta de `[packages]` no existe | Copiar el `.lpk` o corregir la ruta |
| `… is not a package (a .lpk is a zip)` | El archivo no es un paquete | Usar el que deja `larimar build` |
| `… is compressed, and a .lpk is a zip without compression` | Se rehizo el zip a mano con compresión | No recomprimir; o `zip -0` |
| `… has no x.interface` | La carpeta no es un paquete, o el nombre de `[packages]` no es el de la biblioteca | El nombre a la izquierda es el del proyecto de la biblioteca |
| `x.lar does not match the library (its hash is …)` | El binding se editó a mano o es de otro build | Copiar el paquete entero de un solo build |
| `x.c is from another build than x.lar and x.interface` | Archivos mezclados de dos builds | Igual |
| `package 'a' uses the package 'b': name it in [packages] too` | Falta un paquete que otro usa | Añadirlo a `[packages]` |
| `the library has no export functions` | Ninguna función lleva `export` | Marcar las que se usan desde fuera |
| `A library has no main` | La biblioteca tiene `main` | Quitarla; el `main` es de quien la usa |
| `two export functions are called 'x'` | Dos módulos exportan el mismo nombre | Renombrar una, o `= otro_nombre` |
| `'x' in [c] is outside the library's folder` | Un `sources` o `include_paths` apunta fuera | Mover ese C dentro de la biblioteca |
| `Parameter 'p' of export function 'f': C can only pass …` | Un tipo que no cruza (una lista, un struct) | Pasar números, textos o una clase; o varias llamadas |
| `Export function 'f' cannot throw` | Los errores no cruzan | Capturarlo dentro y devolver un código o `null` |
| `'in default' is not allowed on the parameters of an export function` | `in` en un parámetro que no es una función | Solo va en un parámetro de tipo función |
| `x is a static library, for C programs: a Larimar program uses the package` | Se nombró en `[packages]` una biblioteca compilada | Nombrar el `.lpk` |
| `Field 'f' of synchronized class 'C' is a function that other threads may call` | Una función en un objeto `synchronized` | Declarar su tipo `thread safe` |
| `C keeps the function given to 'f' (in default) …` | Una lambda guardada usa algo local | Crear eso `in default` |
| `a released X was used` (al ejecutar) | Se usó un handle tras `release` | No usarlo después de liberarlo |

---

## 16. Qué garantiza el binding generado, y qué no

**Garantiza**, para un programa Larimar que usa una biblioteca Larimar:

- El binding lo escribe el compilador a partir del código de la biblioteca; nadie lo escribe a mano.
- Lleva la propiedad de cada cosa: `released by` en textos y clases, `in default` en callbacks guardados.
- No se puede usar con una biblioteca que no es la suya: el hash de la interfaz lo impide.
- Lleva `thread safe` cuando la biblioteca llama a la función desde otro hilo, y entonces la función del programa se comprueba para eso.
- Con eso, las reglas normales de memoria del programa cubren la frontera. En esta revisión se intentó guardar de más un handle y un texto, usar un objeto liberado, compartir un handle con un hilo y capturar un local en un callback guardado: todo fue rechazado al compilar o detenido con un mensaje claro, sin acceso a memoria liberada.
- Nada del C de la biblioteca es visible fuera salvo sus funciones exportadas (comprobado listando los símbolos del C compilado).

**No garantiza:**

- **Un programa en C.** Tiene el `.h` y sus comentarios; C no comprueba nada. Liberar dos veces, usar un handle liberado o guardar un texto prestado son errores que solo evita quien escribe el C.
- **El C de terceros** que la biblioteca trae. Sus declaraciones `native` son afirmaciones de quien las escribe.
- **Windows y macOS.** No se ha ejecutado nada de este manual en ellos.

---

## 17. Límites conocidos y trabajo pendiente

Encontrados o confirmados al escribir este manual.

**Corregido durante esta revisión** (ya en 1.7.0):

- Una biblioteca que creaba algo `in default`, o usaba una lambda como interfaz (el `run` de un `Thread`), no enlazaba con un programa que hiciera lo mismo: dos nombres de su C no eran privados. Prueba: `aLibraryAndItsProgramShareNoNames`.
- El fallo de memoria con métodos sobrescritos (sección 5.7).

**Corregido después, al implementar el diseño de la frontera:**

- Un objeto `synchronized` creado alrededor de una función o de una lista compartida (sección 10): era un fallo del lenguaje, con o sin bibliotecas.

**Pendiente:**

1. **Funciones en métodos de una clase.** `app.get("/x", handler)` como método todavía no cruza; como función sí: `webkit.get(app, "/x", handler)`.
2. **`in self`**: que una función guardada viva lo que viva el objeto que la guarda. Hoy una función guardada vive todo el programa (`in default`).
3. **El mensaje al guardar un handle de más** sugiere `clone()`; debería sugerir `in default`.
4. **Una biblioteca del sistema que falta** da el error del enlazador de C, no uno de Larimar.
5. **Un puntero a función de C ajeno que devuelve `String`**: el compilador trata ese texto como si viviera todo el programa. Es una suposición sobre el C ajeno que no se comprueba.
6. **Sin separación por procesador** para el C ya compilado.
7. **El C del paquete se recompila** en cada `larimar build` del programa.
8. **Listas, tablas y errores no cruzan.** El API de una biblioteca es de números, textos, handles y callbacks.
