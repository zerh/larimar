# Bibliotecas en Larimar: manual de desarrollo

Este manual recorre **todos los escenarios** de escribir, publicar y usar una biblioteca hecha en Larimar,
y **todos los intentos de usarla mal** que se probaron. Cada apartado trae el código completo y la salida
real que dio al ejecutarlo.

Versión descrita: Larimar 1.7.0. La referencia breve está en el
[manual, capítulo 27](manual.es.md#27-bibliotecas-escritas-en-larimar).

**Cómo se hizo.** Un banco de pruebas escribió cada proyecto de este manual en disco, lo construyó, lo
ejecutó y guardó lo que imprimió: 129 ejecuciones. Los bloques de salida son esa salida, sin retocar. Los
programas en Larimar y en C se compilaron con el detector de errores de memoria (AddressSanitizer, que
incluye la detección de fugas); los de hilos, además con el detector de carreras (ThreadSanitizer).
Todo se ejecutó en **Linux**. En Windows y macOS no se ha ejecutado nada de este manual.

---

## Contenido

**Parte I. Conceptos**

1. [El modelo](#1-el-modelo)
2. [Las reglas de memoria en la frontera](#2-las-reglas-de-memoria-en-la-frontera)
3. [Anatomía de un paquete](#3-anatomía-de-un-paquete)

**Parte II. Escribir una biblioteca**

4. [La primera biblioteca](#4-la-primera-biblioteca)
5. [Textos](#5-textos)
6. [Estado de la biblioteca](#6-estado-de-la-biblioteca)
7. [Clases: objetos que cruzan](#7-clases-objetos-que-cruzan)
8. [Funciones del programa que la biblioteca llama](#8-funciones-del-programa-que-la-biblioteca-llama)
9. [Hilos](#9-hilos)

**Parte III. Bibliotecas que usan C**

10. [C de terceros en código fuente](#10-c-de-terceros-en-código-fuente)
11. [Una biblioteca del sistema](#11-una-biblioteca-del-sistema)
12. [C ya compilado](#12-c-ya-compilado)

**Parte IV. Distribuir**

13. [El paquete .lpk](#13-el-paquete-lpk)
14. [Un paquete que usa otro](#14-un-paquete-que-usa-otro)
15. [Entregar la biblioteca a un programa en C](#15-entregar-la-biblioteca-a-un-programa-en-c)

**Parte V. Probar y diagnosticar**

16. [Las pruebas de la biblioteca](#16-las-pruebas-de-la-biblioteca)
17. [Errores al construir una biblioteca](#17-errores-al-construir-una-biblioteca)
18. [Errores al usar un paquete](#18-errores-al-usar-un-paquete)

**Parte VI. Seguridad**

19. [Catálogo de intentos de romper la memoria](#19-catálogo-de-intentos-de-romper-la-memoria)
20. [Qué garantiza el binding generado, y qué no](#20-qué-garantiza-el-binding-generado-y-qué-no)
21. [Fallos encontrados al escribir este manual](#21-fallos-encontrados-al-escribir-este-manual)
22. [Límites conocidos](#22-límites-conocidos)

**Apéndices**

- [A. Qué prueba de la suite cubre cada cosa](#a-qué-prueba-de-la-suite-cubre-cada-cosa)
- [B. Chuleta](#b-chuleta)

---

# Parte I. Conceptos

## 1. El modelo

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

### 1.1 Los dos públicos

| Quién la usa | Qué recibe | Cómo |
|---|---|---|
| Un programa en **Larimar** | el paquete `.lpk` | lo nombra en `[packages]` y escribe `import textkit;` |
| Un programa en **C** | `textkit.h` y `textkit.c`, o la biblioteca compilada | `#include "textkit.h"` |

El C del paquete se compila **junto con el programa** que lo usa, en cualquier sistema: un solo paquete
sirve para Linux, macOS y Windows.

### 1.2 Cada biblioteca, su runtime

Cada biblioteca lleva dentro su propia copia del runtime de Larimar (memorias, textos, hilos), y todo lo
suyo es privado. El programa y cada biblioteca son mundos separados que solo se tocan por las funciones
exportadas.

Se comprobó listando los nombres que el C de una biblioteca deja visibles. Esto es todo lo que se ve de
`bank` (sección 7):

```
bank_Account_balance
bank_Account_copy
bank_Account_deposit
bank_Account_last
bank_Account_owner
bank_Account_release
bank_find
bank_free
bank_interface
bank_larimar_interface
bank_open
bank_transfer
```

Consecuencias:

- Dos bibliotecas y el programa no chocan, aunque todos usen hilos, memorias y las mismas clases de `std`.
- Nada cruza por referencia a la memoria del otro: los textos se copian y los objetos van como *handles*.
- Una biblioteca que usan el programa y otra biblioteca a la vez es **una sola** en el ejecutable
  (sección 14).

### 1.3 Qué cruza

| Cruza | En Larimar | En C |
|---|---|---|
| Números y `bool` | `int32`, `float64`, `bool`… | `int32_t`, `double`, `bool`… |
| Textos | `String`, `String?` | `const char*` al entrar, `char*` al salir (`NULL` es `null`) |
| Objetos de la biblioteca | una clase, o `Clase?` | un handle: `tk_Clase*` |
| Funciones del programa | un parámetro de tipo función | un puntero a función y un `void*` |

**No cruzan:** listas, tablas, `Any`, structs, interfaces y errores (`throws`). Lo que no cruza se queda
dentro de la biblioteca, y el binding lo avisa en un comentario.

---

## 2. Las reglas de memoria en la frontera

En la frontera valen las dos reglas que Larimar aplica a cualquier función:

1. **Un parámetro se usa durante la llamada.** Quien lo recibe no puede guardarlo, salvo que lo declare
   con `in`.
2. **Un resultado vive donde dice quien llama.**

De ellas sale todo lo demás.

### 2.1 Textos

| Situación | Qué pasa |
|---|---|
| Le pasas un texto a la biblioteca | Lo usa durante la llamada. Si lo guarda, guarda una copia. |
| La biblioteca te devuelve un texto | Es tuyo: vive en la memoria donde lo recibes. |
| Una función tuya recibe un texto de la biblioteca | Lo usa durante la llamada; para guardarlo, `clone()`. |
| Una función tuya le da un texto a la biblioteca | Vive en el bloque de la biblioteca que la llamó. |

### 2.2 Objetos

| Situación | Qué pasa |
|---|---|
| La biblioteca te devuelve un objeto | Es tuyo: vive en la memoria donde lo creas, y se libera con ella. |
| Le pasas un objeto a la biblioteca | Lo usa durante la llamada. |
| Una función tuya recibe un objeto de la biblioteca | Lo usa durante la llamada; no puede guardarlo ni se lo quita a la biblioteca. |

### 2.3 Funciones

| Situación | Qué pasa |
|---|---|
| La biblioteca llama a tu función y no la conserva | Tu función puede usar datos locales. |
| La biblioteca la guarda en un objeto (`in self`) | Lo que tu función usa vive al menos lo que viva el objeto. |
| La biblioteca la guarda en una variable de módulo (`in default`) | Lo que tu función usa tiene que vivir todo el programa. |
| La biblioteca la llama desde otro hilo (`thread safe`) | Tu función se comprueba como el `run` de un hilo. |
| Tu función puede fallar | Lo maneja dentro, con `try`/`catch`. |

### 2.4 Quién las cumple

- En **Larimar**, el compilador. El binding lleva la información (`released by`, `in default`,
  `thread safe`) y el programa no escribe ninguna liberación.
- En **C**, el programador, leyendo los comentarios del `.h`. La regla para C cabe en una frase:

> **La biblioteca nunca libera nada tuyo. Tú liberas solo lo que una función de la biblioteca te devuelve.**

---

## 3. Anatomía de un paquete

### 3.1 Los archivos

Después de `larimar build` de la biblioteca de la sección 4:

```
./textkit-objects/0.o
./textkit.lpk
./textkit/textkit.c
./textkit/textkit.h
./textkit/textkit.interface
./textkit/textkit.lar
```

- `textkit.lpk` es lo que se publica.
- `textkit/` tiene lo mismo, como carpeta. Sirve para mirar qué se generó y para usar la biblioteca
  mientras se escribe, sin copiar nada.
- `textkit-objects/` es de trabajo: `larimar build` compila el C una vez para encontrar sus errores ya, y
  deja ahí el resultado. No forma parte del paquete.

### 3.2 El manifiesto: `textkit.interface`

```
# textkit: a library written in Larimar. Written by larimar build; read by larimar build of the
# programs that link it. The interface hash is that of textkit.lar, and textkit.c has it inside:
# a program builds only when they agree.

[library]
name = "textkit"
version = "1.0.0"
type = "package"
prefix = "tk"
interface = "e86f9946"
larimar = "1.7.0"
files = ["textkit.c", "textkit.h", "textkit.lar"]
links = []
sources = []
include_paths = []
objects = []
packages = []
```

| Campo | Significa |
|---|---|
| `name`, `version` | Los del `[project]` de la biblioteca |
| `type` | `package` (el C se compila con el programa), `static` o `dynamic` (ya compilada, para C) |
| `prefix` | El prefijo de sus nombres en C |
| `interface` | El **hash de la interfaz**: 8 dígitos del SHA-256 del `.lar` |
| `larimar` | La versión del compilador que la hizo |
| `links` | Lo que el programa enlaza además (`-lm`, bibliotecas del sistema) |
| `sources`, `include_paths` | El C de terceros que trae, dentro de `c/` |
| `objects` | El C ya compilado que trae (`lib<nombre>.a`) |
| `packages` | Los otros paquetes que usa |

Cuando la biblioteca tiene C distinto por sistema, aparecen además secciones `[library.unix]`,
`[library.linux]`, `[library.macos]` y `[library.windows]` con los mismos campos (sección 11).

### 3.3 El hash de la interfaz

El hash sale del `.lar`: las funciones, sus tipos y sus comentarios, la versión y el tipo. El C de la
biblioteca lo lleva dentro. Un programa solo se construye cuando el `.lar`, el manifiesto y el C
coinciden. Así se detecta, antes de llamar al compilador de C, un binding editado a mano o archivos
mezclados de dos builds (sección 18).

### 3.4 El `.h`, para C

```
/*
 * textkit.h: textkit 1.0.0, a package library written in Larimar (larimar 1.7.0).
 * Written by larimar build from the export functions: do not edit it.
 *
 * - A text it returns (char*) is yours: free it with tk_free.
 * - The texts it receives are copied when it keeps them; NULL is an error, except for a String? (may be NULL).
 * - A panic inside the library (a bug: an index out of range, a NULL handle) prints it and ends the program.
 */
#ifndef TEXTKIT_H
#define TEXTKIT_H

#include <stdint.h>
#include <stdbool.h>

/* The interface it was built with: tk_interface() gives the one of the library linked. */
#define TEXTKIT_INTERFACE "e86f9946"

#ifdef __cplusplus
extern "C" {
#endif

/** Cuenta las palabras de un texto. */
int32_t tk_wordCount(const char* text);

/**
 * El texto con su primera letra en mayúscula.
 *
 * The text is yours: free it with tk_free.
 */
char* tk_title(const char* text);

/**
 * La primera palabra, o null si no hay ninguna.
 *
 * NULL, or a text that is yours: free it with tk_free.
 */
char* tk_firstWord(const char* text);

/** Cuántas veces se ha llamado a esta función: la biblioteca recuerda entre llamadas. */
int32_t tk_count(void);

/** Frees a text the library returned (NULL does nothing). */
void tk_free(void* text);

/** The interface hash of the library (as in textkit.interface): compare it with TEXTKIT_INTERFACE. */
const char* tk_interface(void);

#ifdef __cplusplus
}
#endif

#endif
```

Cada comentario de la biblioteca pasa al `.h`, y el compilador añade debajo lo que C necesita saber sobre
la memoria (*The text is yours: free it with tk_free*).

### 3.5 El `.lar`, para Larimar

```
// textkit 1.0.0: a package library written in Larimar (larimar 1.7.0).
// Written by larimar build from the export functions: do not edit it. textkit.interface has the hash
// of this file, and so does the library inside: a program builds only when they agree.

cinclude "textkit.h";

/** Cuenta las palabras de un texto. */
public native function wordCount(text: String): int32 = tk_wordCount;

/** El texto con su primera letra en mayúscula. */
public native function title(text: String): String = tk_title released by tk_free;

/** La primera palabra, o null si no hay ninguna. */
public native function firstWord(text: String?): String? = tk_firstWord released by tk_free;

/** Cuántas veces se ha llamado a esta función: la biblioteca recuerda entre llamadas. */
public native function count(): int32 = tk_count;

// what gives back the texts and objects of the library (only the compiler calls them)
native function tk_free(text: String): void = tk_free;
```

Es el binding: las mismas funciones como declaraciones `native`, con `released by` donde hay algo que
liberar. **Lo escribe el compilador; no se edita.**

---

# Parte II. Escribir una biblioteca

## 4. La primera biblioteca

**Prueba de la suite:** `aPackageIsCompiledWithTheProgram`.

### 4.1 El proyecto

`larimar.toml`:

```toml
[project]
name = "textkit"
version = "1.0.0"
kind = "library"
main = "src/textkit.lar"

[library]
prefix = "tk"
```

`kind = "library"` hace que `larimar build` construya una biblioteca en vez de un ejecutable. Una
biblioteca no tiene `main`.

### 4.2 El código

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

let calls: int32 = 0;

/** Cuántas veces se ha llamado a esta función: la biblioteca recuerda entre llamadas. */
public export function count(): int32 {
    calls += 1;
    return calls;
}
```

- **`export`** marca lo que sale de la biblioteca.
- **`public`** además deja que sus pruebas y sus otros módulos la llamen desde Larimar.
- El comentario `/** ... */` de cada función pasa al `.h` y al `.lar`.

### 4.3 Los nombres en C

`prefix = "tk"` da `tk_wordCount`, `tk_title`… Sin `prefix` se usa el nombre del proyecto
(`textkit_wordCount`). Una función puede elegir su nombre: `export function f(): int32 = otro_nombre`.

### 4.4 Construirla

```sh
larimar build
```

```
built build/textkit.lpk, the package in one file, and build/textkit/: textkit.c, textkit.h, textkit.lar, textkit.interface (interface e86f9946)
```

### 4.5 Usarla desde Larimar

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

function main(): int32 {
    println("${textkit.wordCount("uno dos  tres")}");
    println(textkit.title("larimar"));
    println(textkit.firstWord("  hola mundo") ?? "nada");
    println(textkit.firstWord(null) ?? "nada");
    println("${textkit.count()} ${textkit.count()} ${textkit.count()}");
    return 0;
}
```

```sh
larimar run
```

```
3
Larimar
hola
nada
1 2 3
```

`larimar check` y el editor también encuentran la biblioteca:

```sh
larimar check src/main.lar      # no errors
```

### 4.6 Usarla desde C

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
```

```
3 Larimar hola nada
```

---

## 5. Textos

### 5.1 Un texto que entra

Un `String` llega a la biblioteca como un texto de Larimar normal. Vale durante la llamada; si la
biblioteca lo guarda, tiene que copiarlo (`text.clone()`), y el compilador se lo exige.

Desde C es un `const char*` terminado en cero. La biblioteca nunca lo libera ni lo conserva.

### 5.2 Un texto que sale

`textkit.title(...)` devuelve un texto que la biblioteca creó. Al programa le llega como un texto suyo:
el binding dice `released by tk_free`, así que el compilador lo copia a la memoria del programa y libera
el original en el acto.

Se puede devolver desde una función propia sin hacer nada especial:

```ts
function shout(text: String): String { return "${textkit.title(text)}!"; }
function main(): int32 {
    println(shout("hola"));
    return 0;
}
```

```
Hola!
```

Desde C es un `char*` que hay que liberar con `tk_free`. `tk_free(NULL)` no hace nada.

### 5.3 Textos que pueden faltar

`String?` cruza como un puntero que puede ser `NULL`. En el ejemplo de la sección 4, `firstWord(null)`
devuelve `null`, y en C `tk_firstWord(NULL)` devuelve `NULL`.

Un `NULL` donde la biblioteca espera un `String` (sin `?`) se toma como texto vacío:

```c
#include <stdio.h>
#include "textkit.h"
int main(void) { printf("%d\n", tk_wordCount(NULL)); return 0; }
```

```
0
salida: 0
```

### 5.4 Guardar un texto de la biblioteca

Tres formas, con tres resultados distintos.

**Por una variable del bloque: rechazado.**

```ts
let kept: String[*] = [] in default;
function main(): int32 {
    for (i in 0..3) {
        let t: String = textkit.title("palabra ${i}");
        kept.push(t);
    }
    println(kept.join(", "));
    return 0;
}
```

```
Semantic Error [src/main.lar:6]: 't' lives in the memory of this block, but the array lives for the whole program. Keep a copy there: t.clone()
```

`t` vive en el bloque del `for`, y `kept` vive todo el programa.

**Con una copia: correcto.**

```ts
let kept: String[*] = [] in default;
function main(): int32 {
    for (i in 0..3) {
        let t: String = textkit.title("palabra ${i}");
        kept.push(t.clone() in default);
    }
    println(kept.join(", "));
    return 0;
}
```

```
Palabra 0, Palabra 1, Palabra 2
```

**Directamente: correcto.**

```ts
let kept: String[*] = [] in default;
function main(): int32 {
    for (i in 0..3) { kept.push(textkit.title("palabra ${i}")); }
    println(kept.join(", "));
    return 0;
}
```

```
Palabra 0, Palabra 1, Palabra 2
```

Aquí el texto se crea ya en la memoria de `kept`, porque ahí es donde va el resultado. Los tres se
ejecutaron bajo el detector de memoria sin ningún aviso.

---

## 6. Estado de la biblioteca

Una variable de módulo de la biblioteca vive todo el programa y se conserva entre llamadas. En
`textkit`:

```ts
let calls: int32 = 0;

public export function count(): int32 {
    calls += 1;
    return calls;
}
```

El programa de la sección 4 imprime `1 2 3` al llamarla tres veces.

- Ese estado es **de la biblioteca**: el programa no lo ve ni puede tocarlo.
- Si dos partes del programa usan la misma biblioteca, comparten ese estado (sección 14).
- Lo que la biblioteca crea `in default` vive en *su* memoria por defecto, que es distinta de la del
  programa.

Para estado que no deba ser global, lo natural es un objeto (sección 7): cada objeto tiene su memoria y
vive lo que el programa decida.

---

## 7. Clases: objetos que cruzan

**Prueba de la suite:** `aStaticLibraryForC` (desde C), `aPackageIsCompiledWithTheProgram`.

Una clase que aparece en una `export function` cruza como **handle**: el programa la tiene, la pasa y la
devuelve sin ver lo que hay dentro. Sus campos se leen y sus métodos se llaman.

### 7.1 La biblioteca

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

### 7.2 El binding que se genera

```
/** Una cuenta: su dueño, su saldo y sus movimientos. */
public native type Account = bank_Account* released by bank_Account_release {
    // not given to C (they do not cross): moves (String[*])
    /** El dueño de la cuenta. */
    native let owner: String = bank_Account_owner released by bank_free;
    /** El saldo. */
    native let balance: int64 = bank_Account_balance;
    /** Ingresa una cantidad y anota por qué. */
    native function deposit(amount: int64, why: String): void = bank_Account_deposit;
    /** El último movimiento (null si no hay). */
    native function last(): String? = bank_Account_last released by bank_free;
    /** Una cuenta nueva con el mismo dueño y el mismo saldo. */
    function copy(): Account { return self.copy_c()!; }
    native function copy_c(): Account? = bank_Account_copy;
}

/** Abre una cuenta. */
public function open(owner: String): Account { return open_c(owner)!; }
native function open_c(owner: String): Account? = bank_open;

/** Busca una cuenta: null si el nombre está vacío. */
public native function find(owner: String): Account? = bank_find;

/** Pasa una cantidad de una cuenta a otra. */
public native function transfer(from: Account, to: Account, amount: int64): void = bank_transfer;

// what gives back the texts and objects of the library (only the compiler calls them)
native function bank_free(text: String): void = bank_free;
native function bank_Account_release(handle: Account): void = bank_Account_release;
```

- `Account` es un **recurso**: cuando la memoria donde vive se cierra, se llama a
  `bank_Account_release`.
- `moves` es una lista y no cruza: se queda dentro, y el comentario lo avisa.
- Un método que devuelve un objeto nuevo (`copy`) da un handle nuevo.

### 7.3 Usarla desde Larimar

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

```
Ana 70 (a Luis: -30)
Luis 30 (de Ana: 30)
Luis 30 (-)
no hay cuenta
```

### 7.4 Dónde vive un objeto

Un objeto de la biblioteca vive en la memoria donde el programa lo crea.

**En un bloque:** se libera al salir del bloque. Es el caso del ejemplo anterior.

**En todo el programa:** `in default`.

```ts
let all: Account[*] = [] in default;
function main(): int32 {
    for (i in 0..2) {
        let a: Account = bank.open("x${i}") in default;
        all.push(a);
    }
    println("${all[0].owner} ${all[1].owner}");
    return 0;
}
```

```
x0 x1
```

**Dentro de otro objeto:** vive lo que viva ese objeto.

```ts
class Client {
    let name: String;
    let account: Account;
}
function main(): int32 {
    let c: Client = { name: "Ana", account: bank.open("Ana") };
    c.account.deposit(7, "regalo");
    println("${c.name} ${c.account.balance}");
    return 0;
}
```

```
Ana 7
```

**Devuelto por una función:** se crea donde diga quien llama.

```ts
function make(n: int32): Account {
    let a: Account = bank.open("cuenta ${n}");
    a.deposit(n as int64, "inicio");
    return a;
}
function main(): int32 {
    let a: Account = make(5);
    println("${a.owner} ${a.balance}");
    return 0;
}
```

```
cuenta 5 5
```

### 7.5 Campos

Un campo solo se **lee** desde fuera. Intentar escribirlo:

```ts
function main(): int32 {
    let a: Account = bank.open("x");
    a.balance = 1000000;
    return 0;
}
```

```
Semantic Error [src/main.lar:6]: Only variables, fields and array elements can be assigned.
```

Un campo que no cruza no existe para el programa:

```ts
function main(): int32 {
    let a: Account = bank.open("x");
    println("${a.moves.length}");
    return 0;
}
```

```
Semantic Error [src/main.lar:6]: 'bank.Account' has no field 'moves'.
```

Un campo cuyo tipo es otra clase tampoco cruza: ese objeto es del primero. Un método que devuelve uno
nuevo, sí.

### 7.6 Lo que un programa no puede hacer con una clase de la biblioteca

Crearla por su cuenta:

```ts
function main(): int32 {
    let a: Account = Account { owner: "x" };
    return 0;
}
```

```
Semantic Error [src/main.lar:5]: Unknown type 'bank.Account' in object literal.
```

Extenderla:

```ts
class Savings extends Account { }
function main(): int32 { return 0; }
```

```
Semantic Error [src/main.lar:4]: Class 'Savings' extends 'bank.Account', but that class was not found.
```

Los objetos los hacen las funciones de la biblioteca.

### 7.7 El mismo objeto dos veces

Pasar el mismo objeto en dos parámetros funciona como se espera:

```ts
function main(): int32 {
    let a: Account = bank.open("x");
    a.deposit(10, "inicio");
    bank.transfer(a, a, 4);
    println("${a.balance} (${a.last() ?? "-"})");
    return 0;
}
```

```
10 (de x: 4)
```

### 7.8 Usarla desde C

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

```
Ana 70 (a Luis: -30)
```

Reglas para C:

- Cada handle se libera con `bank_Account_release` cuando ya no se usa.
- Cada `char*` que devuelve la biblioteca se libera con `bank_free`.
- `NULL` donde se espera un objeto detiene el programa con un mensaje que nombra la función y el
  parámetro:

```c
#include <stdio.h>
#include "bank.h"
int main(void) { bank_Account_deposit(NULL, 1, "x"); return 0; }
```

```
salida: 101
panic: bank_Account_deposit: 'self' is NULL
```

  Donde se espera `Clase?`, `NULL` es `null`.

---

## 8. Funciones del programa que la biblioteca llama

**Pruebas de la suite:** `aLibraryCallsTheProgramBack`, `aCallbackGetsAnObjectAndGivesAText`.

Una biblioteca recibe una función del programa como **un parámetro de tipo función**, igual que en
cualquier código Larimar, y la llama como cualquier función. No hay tipos de C ni `Context` en el código
de la biblioteca.

### 8.1 Llamada durante la función

```ts
let saved: ((int32, String) -> int32)? = null;

/** Llama a `visit` por cada número menor que `n`, y suma lo que devuelve. */
public export function each(n: int32, visit: (int32, String) -> int32): int32 {
    let total: int32 = 0;
    for (i in 0..n) { total += visit(i, "item ${i}"); }
    return total;
}

/** Guarda `visit` para llamarla después, con fire. */
public export function keep(visit: (int32, String) -> int32 in default): void {
    saved = visit;
}

/** Llama a la función guardada (-1 si no hay). */
public export function fire(n: int32): int32 {
    if (saved == null) { return -1; }
    return saved!(n, "fired");
}
```

`each` llama a `visit` y no la conserva. El programa le da una lambda, que puede usar lo que tenga a
mano:

```ts
import evkit;
let factor: int32 = 10;
function main(): int32 {
    let seen: String[*] = [];
    println("${evkit.each(4, (n: int32, label: String) -> { seen.push(label.clone()); return n * factor; })}");
    println(seen.join(","));
    evkit.keep((n: int32, label: String) -> { return n + label.length; });
    println("${evkit.fire(5)}");
    return 0;
}
```

```
60
item 0,item 1,item 2,item 3
10
```

- En `each`, la lambda captura `seen`, que es local. Está permitido porque la biblioteca no guarda la
  función.
- `label` es un texto de la biblioteca: vale durante la llamada. Para guardarlo, `label.clone()`.

Sin la copia:

```ts
let labels: String[*] = [] in default;
function main(): int32 {
    evkit.each(2, (n: int32, label: String) -> { labels.push(label); return n; });
    return 0;
}
```

```
Semantic Error [src/main.lar:4]: This value lives in 'label' (owned by the caller), but the array lives longer (in the whole program). Use .clone() to copy it there, or declare the parameter as 'label: String in default'.
```

### 8.2 Una función con nombre

No tiene que ser una lambda:

```ts
function double(n: int32, label: String): int32 { return n * 2; }
function main(): int32 {
    println("${evkit.each(4, ::double)}");
    return 0;
}
```

```
12
```

### 8.3 Llamadas anidadas

Una función del programa puede volver a llamar a la biblioteca, que vuelve a llamar a otra función del
programa:

```ts
function main(): int32 {
    println("${evkit.each(3, (n: int32, label: String) -> { return evkit.each(2, (m: int32, inner: String) -> { return n + m; }); })}");
    return 0;
}
```

```
9
```

### 8.4 Una función que la biblioteca guarda

`keep` conserva la función para llamarla después. Lo dice con `in default` en el parámetro, que es la
anotación normal de Larimar para «esto se queda»:

```ts
public export function keep(visit: (int32, String) -> int32 in default): void {
    saved = visit;
}
```

Sin `in default`, la propia biblioteca no compila:

```
Semantic Error [src/evkit.lar:12]: The function 'visit' lives in 'visit' (owned by the caller), but 'saved' lives for the whole program. A function cannot be copied with clone(): make 'visit' live there (declare the parameter as 'visit: (int32, String) -> int32 in default').
```

Y entonces la función del programa no puede usar nada que muera antes que el programa:

```ts
function main(): int32 {
    let seen: String[*] = [];
    evkit.keep((n: int32, label: String) -> { seen.push(label.clone()); return n; });
    return 0;
}
```

```
Semantic Error [src/main.lar:4]: C keeps the function given to 'evkit.keep' (in default), so what it uses must live as long as the whole program, but it lives in the memory of this block. Create what it uses in default.
```

Con el dato creado `in default`, funciona:

```ts
function main(): int32 {
    let seen: String[*] = [] in default;
    evkit.keep((n: int32, label: String) -> { seen.push(label.clone()); return n; });
    println("${evkit.fire(1)} ${evkit.fire(2)} ${seen.join(",")}");
    return 0;
}
```

```
1 2 fired,fired
```

### 8.5 La función recibe un objeto de la biblioteca y da un texto

Es la forma de un manejador web.

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

```
hola ana 0 en /hi (17 bytes)
hola ana 1 en /hi (17 bytes)
hola ana 2 en /hi (17 bytes)
```

- **`req` es un parámetro.** La lambda lo usa durante la llamada; es de la biblioteca.
- **El texto que da la lambda vive en el bloque de `serve`**, la función de la biblioteca que la llamó, y
  se limpia al salir de él. Nadie libera nada a mano.
- **La lambda captura lo que necesita** (`greeting`).

Para comprobar que no se acumula memoria, se llamó 2,000 veces con un texto de varios cientos de bytes
cada vez, bajo el detector de fugas:

```ts
function main(): int32 {
    let total: int32 = 0;
    for (i in 0..2000) {
        let answer: String = webkit.serve("/p${i}", "n", (req: Request) -> { return "${req.path} ".repeat(50); });
        total += answer.length;
    }
    println("${total}");
    return 0;
}
```

```
668500
```

Sin ningún aviso del detector.

### 8.6 Una función que puede fallar

Una lambda no puede lanzar. Si llama a algo que falla, lo maneja dentro:

```ts
enum Bad { Thing }
function risky(n: int32): String throws Bad { if (n > 0) { throw Bad.Thing; } return "ok"; }
function main(): int32 {
    println(webkit.serve("/hi", "ana", (req: Request) -> { return risky(1); }));
    return 0;
}
```

```
Semantic Error [src/main.lar:7]: 'risky' can throw Bad. Lambdas cannot throw: handle it with try/catch inside the lambda.
```

```ts
enum Bad { Thing }
function risky(n: int32): String throws Bad { if (n > 0) { throw Bad.Thing; } return "ok"; }
function main(): int32 {
    println(webkit.serve("/hi", "ana", (req: Request) -> {
        try { return risky(1); } catch (Bad e) { return "no se pudo"; }
    }));
    return 0;
}
```

```
no se pudo (10 bytes)
```

### 8.7 Qué puede llevar una función que cruza

| | Admite |
|---|---|
| Parámetros | números, `bool`, `String`, clases de la biblioteca |
| Resultado | un número, `bool`, `String`, o nada |

Todavía no: listas, y que la función devuelva un objeto (sección 22).

### 8.8 Lo que se genera

En el `.h` de `evkit`:

```
typedef int32_t (*ev_each_visit)(int32_t, const char*, void* data);
/**
 * A function of yours that ev_keep calls: `data` is the void* you give with it, and both are kept:
 * they must stay valid for as long as the program runs.
 */
typedef int32_t (*ev_keep_visit)(int32_t, const char*, void* data);
/** Llama a `visit` por cada número menor que `n`, y suma lo que devuelve. */
int32_t ev_each(int32_t n, ev_each_visit visit, void* visit_data);
/** Guarda `visit` para llamarla después, con fire. */
void ev_keep(ev_keep_visit visit, void* visit_data);
/** Llama a la función guardada (-1 si no hay). */
int32_t ev_fire(int32_t n);
/** Frees a text the library returned (NULL does nothing). */
void ev_free(void* text);
/** The interface hash of the library (as in evkit.interface): compare it with EVKIT_INTERFACE. */
const char* ev_interface(void);
#ifdef __cplusplus
}
#endif
#endif
```

En su `.lar`:

```
native type each_visit = (int32, String, Context) -> int32;

native type keep_visit = (int32, String, Context) -> int32;

/** Llama a `visit` por cada número menor que `n`, y suma lo que devuelve. */
public native function each(n: int32, visit: each_visit, visit_data: Context): int32 = ev_each;

/** Guarda `visit` para llamarla después, con fire. */
public native function keep(visit: keep_visit in default, visit_data: Context): void = ev_keep;

/** Llama a la función guardada (-1 si no hay). */
public native function fire(n: int32): int32 = ev_fire;

// what gives back the texts and objects of the library (only the compiler calls them)
native function ev_free(text: String): void = ev_free;
```

Ahí sí aparece `Context`: es el `void*` de C, y en el binding lo rellena el compilador con lo que la
lambda captura. Quien escribe la biblioteca y quien la usa no lo ven.

### 8.9 Desde C

C entrega una función y un `void*`, que la función recibe de vuelta en cada llamada.

```c
#include <stdio.h>
#include <string.h>
#include "evkit.h"

static int32_t twice(int32_t n, const char* label, void* data) { (void)label; return n * *(int*)data; }
static int32_t length(int32_t n, const char* label, void* data) { (void)data; return n + (int32_t)strlen(label); }

int main(void) {
    int k = 2;
    printf("%d\n", ev_each(4, twice, &k));
    ev_keep(length, NULL);
    printf("%d\n", ev_fire(5));
    return 0;
}
```

```
12
10
```

Con una función que recibe un objeto y da un texto, el `.h` de `webkit` dice:

```
 * A function of yours that wk_serve calls: `data` is the void* you give with it.
 * A wk_Request* it gets is the library's: use it during the call, do not release it nor keep it.
 * It gives its text with wk_give(out, text): the library copies it at once.
 */
typedef void (*wk_serve_handler)(wk_Request*, void* data, void* out);

/* Request: its fields (to read) and its methods; self is the handle. */

/** The text is yours: free it with wk_free. */
char* wk_Request_path(wk_Request* self);

/** The text is yours: free it with wk_free. */
char* wk_Request_name(wk_Request* self);

/**
 * El valor de un parámetro ("" si no está).
 *
 * The text is yours: free it with wk_free.
 */
char* wk_Request_param(wk_Request* self, const char* key);

/**
 * Atiende una petición con `handler` y devuelve la respuesta, con su tamaño.
 *
```

```c
#include <stdio.h>
#include "webkit.h"

static void hello(wk_Request* req, void* data, void* out) {
    char text[128];
    char* name = wk_Request_param(req, "name");       /* un texto que devuelve la biblioteca: mío, lo libero */
    snprintf(text, sizeof text, "%s %s", (const char*)data, name);
    wk_free(name);
    wk_give(out, text);                               /* la biblioteca lo copia en el acto */
}

int main(void) {
    char* answer = wk_serve("/hi", "ana", hello, "hola");
    printf("%s\n", answer);
    wk_free(answer);
    return 0;
}
```

```
hola ana (8 bytes)
```

- Una función que da un número lo devuelve con `return`.
- Una que da un texto lo deja con `<prefijo>_give(out, texto)`, donde `out` es su último argumento. La
  biblioteca lo copia a su memoria en el acto: C no reserva nada ni tiene que mantener vivo el texto.
- El `wk_Request*` que recibe es de la biblioteca: no se libera ni se guarda.

Si la función de C no da ningún texto, la biblioteca recibe el texto vacío:

```c
#include <stdio.h>
#include "webkit.h"
static void silent(wk_Request* req, void* data, void* out) { (void)req; (void)data; (void)out; }
int main(void) {
    char* answer = wk_serve("/hi", "ana", silent, NULL);
    printf("[%s]\n", answer);
    wk_free(answer);
    return 0;
}
```

```
[ (0 bytes)]
```

### 8.10 Funciones en los métodos de una clase

**Prueba de la suite:** `aMethodKeepsAFunctionInItsObject`.

Un método de una clase de la biblioteca recibe una función igual que una función exportada. Es la forma
natural de una aplicación con rutas:

```ts
/** Una petición: su ruta y sus parámetros. */
public class Request {
    let path: String;
    let name: String = "";

    /** El valor de un parámetro ("" si no está). */
    function param(key: String): String { return key == "name" ? self.name.clone() : ""; }
}

/** Una aplicación: sus rutas, y quién las atiende. */
public class App {
    let paths: String[*] = [];
    let handlers: ((Request) -> String)[*] = [];

    /** Atiende `path` con `handler`. */
    function get(path: String, handler: (Request) -> String in self): void {
        self.paths.push(path.clone());
        self.handlers.push(handler);
    }

    /** La respuesta a una petición ("404" si nadie atiende esa ruta). */
    function handle(path: String, name: String): String {
        for (i, p in self.paths) {
            if (p == path) {
                let req: Request = { path: path.clone(), name: name.clone() };
                return self.handlers[i](req);
            }
        }
        return "404";
    }
}

/** Una aplicación nueva. */
public export function newApp(): App { return App { }; }
```

```ts
import webkit;
import webkit { App, Request };

function serveOnce(greeting: String): void {
    let app: App = webkit.newApp();                 // vive en este bloque
    let prefix: String = "${greeting}, ";           // y esto también
    app.get("/hi", (req: Request) -> { return "${prefix}${req.param("name")}"; });
    app.get("/bye", (req: Request) -> { return "adiós ${req.param("name")}"; });
    println("${app.handle("/hi", "ana")} | ${app.handle("/bye", "luis")} | ${app.handle("/nada", "x")}");
}                                                   // aquí mueren app, sus funciones y prefix

function main(): int32 {
    for (i in 0..3) { serveOnce("hola ${i}"); }
    return 0;
}
```

```
hola 0, ana | adiós luis | 404
hola 1, ana | adiós luis | 404
hola 2, ana | adiós luis | 404
```

### 8.11 Una función guardada en el objeto: `in self`

En `get`, el parámetro dice `in self`: la función se queda **en el objeto**. Es la anotación normal de
Larimar para un método que guarda lo que recibe, y su consecuencia es la de siempre: lo que la función
usa tiene que vivir al menos tanto como el objeto. Ni más.

En el ejemplo anterior, `app` vive en el bloque de `serveOnce`, y la lambda usa `prefix`, que vive en el
mismo bloque. Al salir, mueren los tres juntos. Con `in default` eso no compilaría, porque `prefix`
tendría que vivir todo el programa.

**El objeto vive más que lo que usa la función: rechazado.**

```ts
function main(): int32 {
    let app: App = webkit.newApp() in default;
    for (i in 0..2) {
        let prefix: String = "hola ${i}, ";
        app.get("/hi", (req: Request) -> { return "${prefix}${req.param("name")}"; });
    }
    return 0;
}
```

```
Semantic Error [src/main.lar:8]: Argument 2 of 'get()' ('handler: (webkit.Request) -> String in self') must live as long as the object (the whole program), but it lives in the memory of this block. A function cannot be copied with clone(): create what it captures there.
```

**Lo que usa la función está en un bloque interior: rechazado.**

```ts
function main(): int32 {
    let app: App = webkit.newApp();
    if (true) {
        let prefix: String = "hola ${1}, ";
        app.get("/hi", (req: Request) -> { return "${prefix}${req.param("name")}"; });
    }
    println(app.handle("/hi", "ana"));
    return 0;
}
```

```
Semantic Error [src/main.lar:8]: Argument 2 of 'get()' ('handler: (webkit.Request) -> String in self') must live as long as the object (the memory of an outer block), but it lives in the memory of this block (freed at its '}'). A function cannot be copied with clone(): create what it captures there.
```

**El objeto llega como parámetro y la función usa un dato local: rechazado.**

```ts
function register(app: App): void {
    let prefix: String = "hola ${1}, ";
    app.get("/hi", (req: Request) -> { return "${prefix}${req.param("name")}"; });
}
function main(): int32 {
    let app: App = webkit.newApp();
    register(app);
    return 0;
}
```

```
Semantic Error [src/main.lar:6]: Argument 2 of 'get()' ('handler: (webkit.Request) -> String in self') must live as long as the object ('app' (owned by the caller)), but it lives in the memory of this block. A function cannot be copied with clone(): create what it captures there.
```

**El objeto llega como parámetro y la función no usa nada de fuera: correcto.**

```ts
function register(app: App): void {
    app.get("/hi", (req: Request) -> { return "hola ${req.param("name")}"; });
}
function main(): int32 {
    let app: App = webkit.newApp();
    register(app);
    println(app.handle("/hi", "ana"));
    return 0;
}
```

```
hola ana
```

**El objeto y lo que usa la función viven todo el programa: correcto.**

```ts
let prefix: String = "hola, ";
function main(): int32 {
    let app: App = webkit.newApp() in default;
    app.get("/hi", (req: Request) -> { return "${prefix}${req.param("name")}"; });
    println(app.handle("/hi", "ana"));
    return 0;
}
```

```
hola, ana
```

**Sin fugas.** 500 aplicaciones, cada una con cuatro funciones que usan un dato de su bloque, bajo el
detector de fugas:

```ts
function main(): int32 {
    let total: int32 = 0;
    for (i in 0..500) {
        let app: App = webkit.newApp();
        let tag: String = "r${i}";
        for (k in 0..4) { app.get("/p${k}", (req: Request) -> { return "${tag}:${req.path}"; }); }
        total += app.handle("/p3", "x").length;
    }
    println("${total}");
    return 0;
}
```

```
3890
```

Lo que se genera. En el `.lar`:

```
native type App_get_handler = (Request, Context) -> String;
    native function get(path: String, handler: App_get_handler in self, handler_data: Context): void = wk_App_get;
```

En el `.h`:

```
 * A function of yours that wk_App_get calls: `data` is the void* you give with it, and both are kept in
 * the object: they must stay valid for as long as it is not released.
typedef void (*wk_App_get_handler)(wk_Request*, void* data, void* out);
void wk_App_get(wk_App* self, const char* path, wk_App_get_handler handler, void* handler_data);
```

Desde C, la función y su `void*` tienen que valer mientras el objeto no se libere:

```c
#include <stdio.h>
#include "webkit.h"

static void hello(wk_Request* req, void* data, void* out) {
    char text[64];
    char* name = wk_Request_param(req, "name");
    snprintf(text, sizeof text, "%s %s", (const char*)data, name);
    wk_free(name);
    wk_give(out, text);
}

int main(void) {
    wk_App* app = wk_newApp();
    wk_App_get(app, "/hi", hello, "hola");      /* la función y "hola" valen mientras viva app */
    char* answer = wk_App_handle(app, "/hi", "ana");
    printf("%s\n", answer);
    wk_free(answer);
    wk_App_release(app);
    return 0;
}
```

```
hola ana
```

**Cuándo usar cada una:**

| La biblioteca guarda la función en… | Anotación | Lo que usa la función vive… |
|---|---|---|
| ningún sitio: la llama y termina | ninguna | lo que dure la llamada |
| un objeto suyo | `in self` | al menos lo que viva el objeto |
| una variable de módulo | `in default` | todo el programa |

Una limitación: cada función guardada ocupa sitio en la memoria del objeto hasta que el objeto muere.
Registrar rutas al arrancar no importa; volver a registrar sin parar sobre un objeto que no muere iría
acumulando.

---

## 9. Hilos

**Pruebas de la suite:** `aLibraryCallsBackFromAnotherThread`, `aFunctionOfASynchronizedObjectIsThreadSafe`,
`aSynchronizedObjectIsNotCreatedAroundSharedData`, `aLibraryAndItsProgramShareNoNames`.

### 9.1 Una biblioteca puede usar hilos por dentro

Sin ninguna condición: sus hilos son suyos y el programa no se entera. La sección 14 tiene un programa y
una biblioteca que usan hilos a la vez.

### 9.2 Llamar a una función del programa desde otro hilo

El compilador de la biblioteca lo impide por las vías directas. Capturándola en el `run` del hilo:

```ts
public export function inBackground(tick: (int32) -> int32 in default): int32 {
    let total: int32[*] = [0] in default;
    let t: Thread = { run: () -> { total[0] += tick(1); } } in default;
    ...
```

```
Semantic Error [src/bg.lar:4]: This thread uses 'total' (int32[*]), which could change while the thread runs. A thread can share only values (numbers, bool, String, and structs, enums and T[N] made of them), objects of synchronized classes or of classes without fields, and 'thread safe' functions.
```

A través de una global:

```ts
let saved: ((int32) -> int32)? = null;
function work(): void { saved!(1); }
...
    let t: Thread = { run: () -> { work(); } } in default;
```

```
Semantic Error [src/bg.lar:6]: This thread can reach global 'saved' (src/bg.lar:2), which can change while threads use it. Keep shared state in an object of a synchronized class.
```

La forma permitida es la que Larimar tiene para compartir estado entre hilos: un objeto `synchronized`.
Y ahí el compilador exige que el tipo de la función lo diga:

```
Semantic Error [src/bg.lar:10]: Field 'tick' of synchronized class 'Holder' is a function that other threads may call: declare it '(int32) -> int32 thread safe'.
```

Con `thread safe`:

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

### 9.3 El binding lo lleva

```
native type inBackground_tick = (int32, Context) -> int32 thread safe;
/** Llama a `tick` cuatro veces desde otro hilo, y espera a que termine. */
public native function inBackground(tick: inBackground_tick in default, tick_data: Context): int32 = bg_inBackground;
```

Y el `.h` lo avisa a quien use la biblioteca desde C:

```
 * A function of yours that bg_inBackground calls, maybe from another thread and several at once: `data` is the void* you give with it, and both are kept:
 * they must stay valid for as long as the program runs.
 */
typedef int32_t (*bg_inBackground_tick)(int32_t, void* data);
```

### 9.4 La función del programa se comprueba

Una lambda que toca una lista global:

```ts
import bg;
let seen: int32[*] = [] in default;
function main(): int32 {
    println("${bg.inBackground((n: int32) -> { seen.push(n); return n * 2; })}");
    return 0;
}
```

```
Semantic Error [src/main.lar:4]: This 'thread safe' lambda can reach global 'seen' (src/main.lar:4), which can change while threads use it. Keep shared state in an object of a synchronized class.
```

Con el estado en un objeto `synchronized`, funciona:

```ts
synchronized class Seen {
    let count: int32 = 0;
    function add(): void { self.count += 1; }
    function get(): int32 { return self.count; }
}
function main(): int32 {
    let seen: Seen = { } in default;
    println("${bg.inBackground((n: int32) -> { seen.add(); return n * 2; })} ${seen.get()}");
    return 0;
}
```

```
12 4
```

Ese programa se ejecutó además bajo el detector de carreras, sin ningún aviso:

```
12 4
```

### 9.5 Cuando no hace falta

Una biblioteca que llama a la función en el mismo hilo no escribe `thread safe`, y la lambda del programa
puede tocar sus datos con libertad, como en la sección 8.1.

### 9.6 Un objeto `synchronized` se crea con valores

Esta regla es del lenguaje, no solo de las bibliotecas, y apareció al escribir este manual (sección 21).
Un objeto `synchronized` no se puede crear alrededor de datos que su creador sigue usando:

```ts
synchronized class Bag {
    let items: int32[*];
    function add(n: int32): void { self.items.push(n); }
}
function main(): int32 {
    let shared: int32[*] = [] in default;
    let b: Bag = { items: shared } in default;
    let t: Thread = { run: () -> { for (i in 0..1000) { b.add(i); } } } in default;
    t.start();
    for (i in 0..1000) { shared.push(i); }
    t.join();
    return 0;
}
```

```
Semantic Error [race1.lar:7]: Field 'items' of synchronized class 'Bag' is given int32[*] that others may still use, without its lock: give it a value written here ([...] or { ... }), or fill it with its methods.
```

La forma correcta es que el objeto cree lo suyo y se llene con sus métodos:

```ts
synchronized class Bag {
    let items: int32[*] = [];
    function add(n: int32): void { self.items.push(n); }
    function size(): int32 { return self.items.length; }
}
function main(): int32 {
    let b: Bag = { } in default;
    let t: Thread = { run: () -> { for (i in 0..1000) { b.add(i); } } } in default;
    t.start();
    for (i in 0..1000) { b.add(i); }
    t.join();
    println("${b.size()}");
    return 0;
}
```

Ejecutado bajo el detector de carreras:

```
2000
```

---

# Parte III. Bibliotecas que usan C

## 10. C de terceros en código fuente

**Prueba de la suite:** `aPackageBringsItsC`.

Es el caso más común: una biblioteca de C que se distribuye como `.c` y `.h` (un parser, SQLite, zlib).
Va **dentro** del paquete y se compila con el programa.

### 10.1 El proyecto

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
version = "1.0.0"
kind = "library"
main = "src/tinykit.lar"

[c]
include_paths = ["vendor/tiny"]
sources = ["vendor/tiny/tiny.c"]
```

```ts
cinclude "tiny.h";
native function twiceC(n: int32): int32 = tiny_twice;

/** El doble de n, calculado por la biblioteca de C. */
public export function twice(n: int32): int32 { return twiceC(n); }
```

`vendor/tiny/tiny.h` y `tiny.c`:

```c
int tiny_twice(int n);
```

```c
#include "tiny.h"
int tiny_twice(int n) { return n * 2; }
```

### 10.2 Lo que queda en el paquete

```
./c/vendor/tiny/tiny.c
./c/vendor/tiny/tiny.h
./tinykit.c
./tinykit.h
./tinykit.interface
./tinykit.lar
```

El C se copia a `c/` con la misma ruta, y el manifiesto lo anota:

```toml
sources = ["c/vendor/tiny/tiny.c"]
include_paths = ["c/vendor/tiny"]
```

### 10.3 Quien la usa no ve nada de esto

```ts
import tinykit;
function main(): int32 {
    println("${tinykit.twice(21)}");
    return 0;
}
```

```
42
```

### 10.4 Reglas

- Las rutas de `sources` e `include_paths` tienen que estar **dentro** de la carpeta de la biblioteca:

```
larimar: '../elsewhere/tiny.c' in [c] is outside the library's folder: what goes in its package is inside it
```

- `include_paths` se copia entero; de `sources`, cada archivo.
- **Un error en ese C se ve al construir la biblioteca**, no cuando alguien la usa:

```
tinykit/build/tinykit/c/vendor/tiny/tiny.c: In function ‘broken’:
tinykit/build/tinykit/c/vendor/tiny/tiny.c:3:27: error: ‘undeclared’ undeclared (first use in this function)
    3 | int broken(void) { return undeclared; }
      |                           ^~~~~~~~~~
```

---

## 11. Una biblioteca del sistema

Cuando el C que usa la biblioteca viene con el sistema o se instala aparte, no se mete en el paquete: se
nombra, y el programa lo enlaza.

### 11.1 Por plataforma

```toml
[project]
name = "mathkit"
version = "1.0.0"
kind = "library"
main = "src/mathkit.lar"

[c.unix]
dynamic_libraries = ["m"]       # la biblioteca matemática del sistema
```

```ts
cinclude "<math.h>";
native function cbrt(x: float64): float64;

/** La raíz cúbica. */
public export function cubeRoot(x: float64): float64 { return cbrt(x); }
```

`[c.unix]` vale para Linux y macOS; también hay `[c.linux]`, `[c.macos]` y `[c.windows]`. El manifiesto
lo anota en la sección de cada plataforma:

```
# mathkit: a library written in Larimar. Written by larimar build; read by larimar build of the
# programs that link it. The interface hash is that of mathkit.lar, and mathkit.c has it inside:
# a program builds only when they agree.

[library]
name = "mathkit"
version = "1.0.0"
type = "package"
prefix = "mathkit"
interface = "bd6d5cd1"
larimar = "1.7.0"
files = ["mathkit.c", "mathkit.h", "mathkit.lar"]
links = []
sources = []
include_paths = []
objects = []
packages = []

[library.unix]
links = ["-lm"]
sources = []
include_paths = []
objects = []
```

### 11.2 El programa

```ts
import nokit;
function main(): int32 { return nokit.f(); }
```

```
3.0000000000000004
```

### 11.3 Si la biblioteca del sistema no está

El paquete no la trae. Tiene que estar instalada **donde se construye** el programa y, si es dinámica,
**donde se ejecuta**. Cuando falta al construir, hoy el error es el del enlazador de C:

```
/usr/bin/ld: cannot find -ldoesnotexist: No such file or directory
collect2: error: ld returned 1 exit status
larimar: the C compiler failed (exit 1). Command: cc -std=c99 -O2 -o app/build/app app/build/app.c -Iapp/build/packages/nokit app/build/packages/nokit/nokit.c -lm -ldoesnotexist
The generated C is in build/app.c
```

La construcción de la biblioteca misma no lo detecta, porque ahí solo se compila, no se enlaza.

---

## 12. C ya compilado

**Prueba de la suite:** `aPackageBringsCompiledCAndNamesItsPackages`.

Para una biblioteca de C que solo existe como `lib<nombre>.a`. Si el archivo está en las
`static_library_paths` de la biblioteca, va dentro del paquete y se enlaza en el programa.

### 12.1 El proyecto

```toml
[project]
name = "tinykit"
version = "1.0.0"
kind = "library"
main = "src/tinykit.lar"

[c]
include_paths = ["vendor"]
static_libraries = ["tiny"]
static_library_paths = ["vendor"]
```

Con `vendor/libtiny.a` y `vendor/tiny.h` en su sitio:

```
libtiny.a
tiny.h
```

### 12.2 Lo que queda en el paquete

```
./c/vendor/libtiny.a
./c/vendor/tiny.h
./tinykit.c
./tinykit.h
./tinykit.interface
./tinykit.lar
```

```
sources = []
include_paths = ["c/vendor"]
objects = ["c/vendor/libtiny.a"]
```

```
42
```

### 12.3 Un `.a` es para un sistema

Para dar uno a cada sistema, cada uno en su sección:

```toml
[c.linux]
static_libraries = ["tiny"]
static_library_paths = ["vendor/linux"]

[c.macos]
static_libraries = ["tiny"]
static_library_paths = ["vendor/macos"]
```

- Un `.a` puesto en `[c]` hace que el paquete sirva solo para la plataforma de ese archivo.
- No hay separación por procesador: Intel y ARM del mismo sistema serían dos paquetes.
- Una biblioteca nombrada en `static_libraries` que **no** está en esas carpetas se trata como del
  sistema (`-l<nombre>`).

---

# Parte IV. Distribuir

## 13. El paquete .lpk

**Prueba de la suite:** `aPackageInOneFile`.

### 13.1 Qué es

`larimar build` deja `build/<nombre>.lpk`: **un zip sin comprimir**, que abre cualquier herramienta.

```
Archive:  textkit/build/textkit.lpk
  Length      Date    Time    Name
---------  ---------- -----   ----
    19590  1980-01-01 00:00   textkit.c
     1449  1980-01-01 00:00   textkit.h
      472  1980-01-01 00:00   textkit.interface
      965  1980-01-01 00:00   textkit.lar
---------                     -------
    22476                     4 files
```

- No lleva fechas: la misma biblioteca da siempre el mismo archivo, byte a byte.
- Para publicarlo basta subir ese archivo.

### 13.2 Usarlo

Se copia al proyecto y se nombra:

```toml
[packages]
textkit = "libs/textkit.lpk"
```

Al construir o comprobar el proyecto se desempaqueta en `build/packages/textkit/`. Solo se vuelve a
desempaquetar cuando el archivo cambia, y entonces la carpeta se vacía antes.

### 13.3 Mientras se escribe la biblioteca

Es más cómodo nombrar la **carpeta**, sin copiar nada:

```toml
[packages]
textkit = "../textkit/build/textkit"
```

### 13.4 Sin gestor

No hay una herramienta que descargue paquetes ni que fije versiones: se copian a mano.

---

## 14. Un paquete que usa otro

**Prueba de la suite:** `aPackageBringsCompiledCAndNamesItsPackages`, `aPackageBringsItsC`.

### 14.1 Las dos bibliotecas

`tinykit`, con estado propio:

```ts
let hits: int32[*] = [0] in default;

/** El doble de n. */
public export function twice(n: int32): int32 {
    hits[0] += 1;
    return n * 2;
}
/** Cuántas veces se ha llamado a twice. */
public export function uses(): int32 { return hits[0]; }
```

`fourkit`, que la usa:

```toml
[project]
name = "fourkit"
version = "1.0.0"
kind = "library"
main = "src/fourkit.lar"

[packages]
tinykit = "../tinykit/build/tinykit.lpk"
```

```ts
import tinykit;

/** Cuatro veces n. */
public export function fourTimes(n: int32): int32 { return tinykit.twice(tinykit.twice(n)); }
```

Su manifiesto anota lo que usa:

```
packages = ["tinykit"]
```

### 14.2 El programa nombra los dos

Un paquete **no lleva dentro** a los que usa. Si el programa olvida uno, el error lo dice antes de llamar
al compilador de C:

```
Project Error [larimar.toml]: package 'fourkit' uses the package 'tinykit': name it in [packages] too (tinykit = "...")
```

Con los dos:

```toml
[packages]
fourkit = "../fourkit/build/fourkit.lpk"
tinykit = "../tinykit/build/tinykit.lpk"
```

```ts
import fourkit;
import tinykit;
let mine: int32[*] = [0] in default;

function main(): int32 {
    mine[0] += 1;
    let t: Thread = { run: () -> { println("en un hilo"); } } in default;
    t.start();
    t.join();
    println("${fourkit.fourTimes(3)} ${tinykit.twice(5)} ${tinykit.uses()}");
    return 0;
}
```

```
en un hilo
12 10 3
```

### 14.3 Qué demuestra ese programa

- **`tinykit` es una sola en el ejecutable.** `uses()` da `3`: dos llamadas desde `fourkit` y una desde
  el programa, contadas en el mismo sitio.
- **Tres mundos sin choques.** El programa, `fourkit` y `tinykit` crean cosas `in default`; el programa
  además usa un hilo. Cada uno tiene su memoria por defecto.
- Los nombres que cada biblioteca deja ver son solo los suyos:

```
tinykit_free tinykit_interface tinykit_larimar_interface tinykit_twice tinykit_uses 
fourkit_fourTimes fourkit_free fourkit_interface fourkit_larimar_interface 
```

---

## 15. Entregar la biblioteca a un programa en C

**Pruebas de la suite:** `aStaticLibraryForC`, `aDynamicLibrary`.

### 15.1 Tres formas

| Qué | Comando | Resultado | Sirve en |
|---|---|---|---|
| El código C | `larimar build` | `build/textkit/textkit.c` y `textkit.h` | cualquier sistema |
| Biblioteca estática | `larimar build --static` | `build/textkit/libtextkit.a` | el sistema donde se compiló |
| Biblioteca dinámica | `larimar build --dynamic` | `libtextkit.so`, `.dylib` o `.dll` | el sistema donde se compiló |

Las tres dieron la misma salida con el `main.c` de la sección 4.6: `3 Larimar hola nada`.

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

### 15.2 El manifiesto de una estática

```
# textkit: a library written in Larimar. Written by larimar build; read by larimar build of the
# programs that link it. The interface hash is that of textkit.lar, and libtextkit.a has it inside:
# a program builds only when they agree.

[library]
name = "textkit"
version = "1.0.0"
type = "static"
prefix = "tk"
interface = "8bb3a487"
larimar = "1.7.0"
files = ["libtextkit.a", "textkit.h", "textkit.lar"]
links = ["-lm"]
sources = []
include_paths = []
objects = []
packages = []
```

`links` dice lo que hay que enlazar además (`-lm`, `-pthread` si usa hilos…).

### 15.3 Detalles

- Cada build **reemplaza** al anterior en `build/textkit/`, para no mezclar archivos. El `.lpk` que ya
  existía no se toca.
- `[library] type = "static"` en el toml fija ese tipo sin escribir la opción cada vez.
- El `.h` trae la constante `TEXTKIT_INTERFACE` y la función `tk_interface()`: un programa en C puede
  comprobar al arrancar que el `.h` y la biblioteca son del mismo build con
  `strcmp(tk_interface(), TEXTKIT_INTERFACE) == 0`.
- Un pánico dentro de la biblioteca (un índice fuera de rango, un handle `NULL`) lo imprime y termina
  el programa con salida 101.

### 15.4 Una compilada no es para un programa Larimar

Un programa Larimar usa el paquete. Nombrar una estática en `[packages]`:

```
Project Error [larimar.toml]: textkit (textkit/build/textkit/textkit.interface) is a static library, for C programs: a Larimar program uses the package (larimar build, without --static)
```

---

# Parte V. Probar y diagnosticar

## 16. Las pruebas de la biblioteca

**Prueba de la suite:** `theTestsOfALibraryUseItsRules`.

### 16.1 Probar la lógica

Las pruebas de una biblioteca importan **su código Larimar**, no el paquete: prueban la lógica sin pasar
por la frontera.

`tests/textkit_test.lar`:

```ts
import std.test { checkInt, checkText };
import textkit { wordCount, title };

test function countsWords(): void { checkInt(3, wordCount("uno dos  tres")); }
test function titles(): void { checkText("Hola", title("hola")); }
```

```sh
larimar test
```

```
  ok    tests/textkit_test.lar: countsWords
  ok    tests/textkit_test.lar: titles

2 passed, 0 failed
```

`larimar test` usa el detector de memoria por defecto donde está disponible.

### 16.2 Probar la frontera

Para comprobar que el paquete funciona al usarlo hace falta un programa aparte que lo nombre en
`[packages]`. Con el detector de memoria en sus `flags`, cubre también el C de la biblioteca, porque se
compila con el programa:

```toml
[c]
flags = ["-g", "-fsanitize=address"]

[packages]
textkit = "../textkit/build/textkit"
```

Para hilos, `-fsanitize=thread` en lugar de `address`. Así se hicieron los ejemplos de este manual.

### 16.3 Probar desde C

Un `main.c` que incluya el `.h` y se compile con el `.c` del paquete, con las mismas opciones del
detector:

```sh
cc -std=c99 -g -fsanitize=address -Ibuild/textkit main.c build/textkit/textkit.c -lm -o demo && ./demo
```

---

## 17. Errores al construir una biblioteca

Cada uno es la salida real de `larimar build` con una biblioteca de una o dos líneas.

### 17.1 Tiene `main`

```ts
public export function f(): int32 { return 1; }
function main(): int32 { return 0; }
```

```
Semantic Error [src/k.lar:2]: A library has no main: C (or the program that uses it) calls its export functions. Remove main, or build a program ([project] kind = "program").
```

### 17.2 No exporta nada

```ts
public function f(): int32 { return 1; }
```

```
Library Error [k]: the library has no export functions: mark the functions C calls with 'export function'
```

### 17.3 Una función exportada lanza

```ts
enum E { Bad }
public export function f(n: int32): int32 throws E { ... }
```

```
Semantic Error [src/k.lar:2]: Export function 'k_f' cannot throw: an error cannot cross into C. Catch it inside.
```

El arreglo es capturar el error dentro y devolver un código, un `bool` o `null`.

### 17.4 Recibe una lista

```ts
public export function f(items: int32[*]): int32 { return items.length; }
```

```
Semantic Error [src/k.lar:1]: Parameter 'items' of export function 'k_f': C can only pass numbers, bool, String, String? and the library's classes, and functions of the program (of numbers, bool, String and the library's classes).
```

### 17.5 Devuelve una lista

```ts
public export function f(): String[*] { return ["a"]; }
```

```
Semantic Error [src/k.lar:1]: Export function 'k_f' can only return void or numbers, bool, String, String? and the library's classes.
```

### 17.6 Recibe un struct o un `Any`

```
Semantic Error [src/k.lar:2]: Parameter 'p' of export function 'k_f': C can only pass numbers, bool, String, String? and the library's classes, and functions of the program (of numbers, bool, String and the library's classes).
```

### 17.7 Devuelve una función

```ts
public export function f(): (int32) -> int32 { ... }
```

```
Semantic Error [src/k.lar:1]: Export function 'k_f' can only return void or numbers, bool, String, String? and the library's classes.
```

### 17.8 `in default` en un parámetro que no es una función

```ts
public export function f(text: String in default): int32 { return text.length; }
```

```
Semantic Error [src/k.lar:1]: 'in default' is not allowed on the parameters of an export function: C gives plain values.
```

### 17.9 Una función del programa con tipos que no cruzan

```ts
public export function f(visit: (int32[*]) -> int32): int32 { return 1; }
```

```
Semantic Error [src/k.lar:1]: Parameter 'visit' of export function 'k_f': C can only pass numbers, bool, String, String? and the library's classes, and functions of the program (of numbers, bool, String and the library's classes).
```

### 17.10 Un tipo de biblioteca que no existe

```toml
[library]
type = "shared"
```

```
Project Error [larimar.toml]: type = "shared" in [library]: it is "package" (the default), "static" or "dynamic"
```

### 17.11 C fuera de la carpeta, o C con errores

Ver sección 10.4.

---

## 18. Errores al usar un paquete

Cada uno es la salida real de `larimar build` en el programa.

### 18.1 El archivo no existe

```
Project Error [larimar.toml]: package 'textkit': libs/none.lpk does not exist
```

### 18.2 El nombre no es el de la biblioteca

El nombre a la izquierda en `[packages]` tiene que ser el del proyecto de la biblioteca.

```toml
[packages]
other = "../textkit/build/textkit"
```

```
Project Error [larimar.toml]: package 'other': ../textkit/build/textkit has no other.interface (a package is the folder that larimar build makes of a library, or its .lpk)
```

### 18.3 No es un zip

```
Project Error [larimar.toml]: package 'textkit': app/libs/textkit.lpk is not a package (a .lpk is a zip)
```

### 18.4 Es un zip comprimido

Pasa al rehacer el `.lpk` a mano con una herramienta que comprime.

```
Project Error [larimar.toml]: package 'textkit': app/libs/textkit.lpk: 'textkit.interface' is compressed, and a .lpk is a zip without compression (larimar build makes it)
```

### 18.5 El binding se editó a mano

Se añadió una línea al `textkit.lar` del paquete:

```
Project Error [larimar.toml]: textkit/build/textkit/textkit.lar does not match the library (its hash is 391ae5bb, textkit.interface says e86f9946): it was edited, or comes from another build. Copy the whole folder of one build.
```

### 18.6 Archivos de dos builds mezclados

Se copió el `textkit.c` de un build anterior junto al `.lar` de uno nuevo:

```
Project Error [larimar.toml]: textkit/build/textkit/textkit.c is from another build than textkit.lar and textkit.interface (interface 1cbaee3b): copy the whole folder of one build.
```

### 18.7 Falta un paquete que otro usa

```
Project Error [larimar.toml]: package 'fourkit' uses the package 'tinykit': name it in [packages] too (tinykit = "...")
```

### 18.8 Es una biblioteca compilada

```
Project Error [larimar.toml]: textkit (textkit/build/textkit/textkit.interface) is a static library, for C programs: a Larimar program uses the package (larimar build, without --static)
```

---

# Parte VI. Seguridad

## 19. Catálogo de intentos de romper la memoria

Todo lo que sigue se ejecutó. «Rechazado» quiere decir que el compilador no deja construir el programa;
«detenido», que el programa se para con un mensaje claro, sin tocar memoria liberada.

### 19.1 Con textos

| Intento | Resultado | Dónde |
|---|---|---|
| Guardar un texto de la biblioteca pasando por una variable del bloque | rechazado | 5.4 |
| Guardarlo directamente en algo que vive más | correcto: se crea ahí | 5.4 |
| Guardar el texto que recibe una función llamada por la biblioteca | rechazado; con `clone()` es correcto | 8.1 |
| 2,000 llamadas que devuelven textos largos, bajo el detector de fugas | sin fugas | 8.5 |

### 19.2 Con objetos

**Guardar un objeto más tiempo que su bloque: rechazado.**

```ts
let all: Account[*] = [] in default;
function main(): int32 {
    for (i in 0..2) {
        let a: Account = bank.open("x${i}");
        all.push(a);
    }
    println(all[0].owner);
    return 0;
}
```

```
Semantic Error [src/main.lar:8]: 'a' lives in the memory of this block, but the array lives for the whole program. Keep a copy there: a.clone()
```

El arreglo es crearlo donde debe vivir, con `in default` (sección 7.4).

**Usar un objeto después de liberarlo: detenido.**

```ts
function main(): int32 {
    let a: Account = bank.open("x");
    release(a);
    a.deposit(1, "tarde");
    println("${a.balance}");
    return 0;
}
```

```
panic [build/packages/bank/bank.lar:15]: a released Account was used
```

**Pasarle a la biblioteca un objeto liberado: detenido.**

```ts
function main(): int32 {
    let a: Account = bank.open("a");
    let b: Account = bank.open("b");
    release(a);
    bank.transfer(a, b, 5);
    return 0;
}
```

```
panic [src/main.lar:8]: a released Account was used
```

**Liberarlo dos veces: no pasa nada.**

```ts
function main(): int32 {
    let a: Account = bank.open("x");
    release(a);
    release(a);
    println("liberada dos veces: no pasa nada");
    return 0;
}
```

```
liberada dos veces: no pasa nada
```

**Guardar un texto de un campo pasando por una variable: rechazado.**

```ts
let kept: String[*] = [] in default;
function main(): int32 {
    let a: Account = bank.open("x");
    let owner: String = a.owner;
    kept.push(owner);
    return 0;
}
```

```
Semantic Error [src/main.lar:8]: 'owner' lives in the memory of this block, but the array lives for the whole program. Keep a copy there: owner.clone()
```

**Compartir un objeto con un hilo: rechazado.**

```ts
function main(): int32 {
    let a: Account = bank.open("x") in default;
    let t: Thread = { run: () -> { a.deposit(1, "hilo"); } };
    t.start();
    t.join();
    return 0;
}
```

```
Semantic Error [src/main.lar:6]: This thread uses 'a' (bank.Account), which could change while the thread runs. A thread can share only values (numbers, bool, String, and structs, enums and T[N] made of them), objects of synchronized classes or of classes without fields, and 'thread safe' functions.
```

### 19.3 Con el objeto que recibe una función

Sobre `webkit` (sección 8.5).

**Guardarlo en una lista global: rechazado.**

```ts
let kept: Request[*] = [] in default;
function main(): int32 {
    println(webkit.serve("/hi", "ana", (req: Request) -> { kept.push(req); return "x"; }));
    return 0;
}
```

```
Semantic Error [src/main.lar:6]: This value lives in 'req' (owned by the caller), but the array lives longer (in the whole program). Use .clone() to copy it there, or declare the parameter as 'req: webkit.Request in default'.
```

**Guardarlo en un objeto que vive más: rechazado.**

```ts
class Box { let last: Request? = null; }
function main(): int32 {
    let box: Box = { } in default;
    println(webkit.serve("/hi", "ana", (req: Request) -> { box.last = req; return "x"; }));
    return 0;
}
```

```
Semantic Error [src/main.lar:7]: This value lives in 'req' (owned by the caller), but field 'last' lives longer (in the whole program). Use .clone() to copy it there, or declare the parameter as 'req: webkit.Request in default'.
```

**Liberarlo dentro de la función: no se lo quita a la biblioteca.**

```ts
function main(): int32 {
    println(webkit.serve("/hi", "ana", (req: Request) -> { let p: String = req.path; release(req); return p; }));
    return 0;
}
```

```
/hi (3 bytes)
```

La biblioteca sigue usando su objeto sin problema.

**Liberarlo y seguir usándolo: detenido.**

```ts
function main(): int32 {
    println(webkit.serve("/hi", "ana", (req: Request) -> { release(req); return req.path; }));
    return 0;
}
```

```
panic [build/packages/webkit/webkit.lar:9]: a released Request was used
```

**Declarar que vive todo el programa: rechazado.**

```ts
let kept: Request[*] = [] in default;
function h(req: Request in default): String { kept.push(req); return "x"; }
function main(): int32 {
    println(webkit.serve("/hi", "ana", ::h));
    return 0;
}
```

```
Semantic Error [src/main.lar:7]: Argument 1 of 'h' ('req: webkit.Request in default') must live as long as the whole program, but it lives in '.ref0' (owned by the caller). Use .clone() to copy it there.
```

### 19.4 Con funciones guardadas

| Intento | Resultado | Dónde |
|---|---|---|
| La biblioteca guarda una función sin decirlo | rechazado al construir la biblioteca | 8.4 |
| Una función guardada usa un dato local | rechazado | 8.4 |
| Una función guardada en un objeto usa algo que vive menos que el objeto | rechazado | 8.11 |
| 500 objetos con cuatro funciones guardadas cada uno, bajo el detector de fugas | sin fugas | 8.11 |
| Una función deja escapar un error | rechazado | 8.6 |

### 19.5 Con hilos

| Intento | Resultado | Dónde |
|---|---|---|
| La biblioteca captura la función en el `run` de un hilo | rechazado | 9.2 |
| La alcanza desde un hilo a través de una global | rechazado | 9.2 |
| La mete en un objeto `synchronized` sin `thread safe` | rechazado | 9.2 |
| El programa da una función que toca una global a una biblioteca que la llama desde otro hilo | rechazado | 9.4 |
| Crear un objeto `synchronized` alrededor de una lista compartida | rechazado | 9.6 |

### 19.6 Lo que el compilador no puede impedir

Desde C nada de esto se comprueba. Son errores del programa en C, no de la biblioteca:

- liberar dos veces un handle o un texto;
- usar un handle después de liberarlo;
- guardar el `const char*` o el handle que recibe una función llamada por la biblioteca;
- dar a una biblioteca que guarda la función un `void*` que deja de valer;
- llamar a la biblioteca desde dos hilos a la vez sobre el mismo objeto.

---

## 20. Qué garantiza el binding generado, y qué no

**Garantiza**, para un programa Larimar que usa una biblioteca Larimar:

- El binding lo escribe el compilador a partir del código de la biblioteca; nadie lo escribe a mano.
- Lleva la propiedad de cada cosa: `released by` en textos y clases, `in default` o `in self` en
  funciones guardadas, `thread safe` en las que se llaman desde otro hilo.
- No se puede usar con una biblioteca que no es la suya: el hash de la interfaz lo impide.
- Con eso, las reglas normales de memoria y de hilos del programa cubren la frontera. Todos los intentos
  de la sección 19 acabaron rechazados o detenidos con un mensaje claro.
- Nada del C de la biblioteca es visible fuera salvo sus funciones exportadas.
- Las reglas que permiten a una función recibir objetos y dar textos valen **solo** en el binding de un
  paquete. En un binding escrito a mano para C ajeno siguen prohibidas, porque ese C no sigue la
  convención.

**No garantiza:**

- **Un programa en C** (sección 19.6).
- **El C de terceros** que la biblioteca trae. Sus declaraciones `native` son afirmaciones de quien las
  escribe.
- **Windows y macOS.** No se ha ejecutado nada de este manual en ellos.
- **Que no queden huecos.** Las pruebas cubren lo que se nos ocurrió probar. Al escribir este manual
  aparecieron cuatro fallos (sección 21), dos de ellos del lenguaje y anteriores a las bibliotecas.

---

## 21. Fallos encontrados al escribir este manual

Todos están corregidos en 1.7.0 y tienen prueba.

### 21.1 Un método sobrescrito podía devolver su argumento sin que se notara

Un método de una subclase que devolvía su argumento, llamado a través de la clase base, dejaba guardar
para todo el programa un texto que moría antes. El detector de memoria lo confirmó como uso de memoria
liberada. Ahora un método tiene también lo que devuelven los que lo sobrescriben.

Prueba: `anOverrideMayReturnItsArgument`.

### 21.2 Una biblioteca y su programa chocaban al enlazar

Una biblioteca que creaba algo `in default`, o usaba una lambda como interfaz (el `run` de un `Thread`),
no enlazaba con un programa que hiciera lo mismo: dos nombres de su C no eran privados.

Prueba: `aLibraryAndItsProgramShareNoNames`.

### 21.3 Un objeto `synchronized` creado alrededor de datos compartidos

Un objeto `synchronized` se podía crear con una lista que su creador seguía usando, o con una función
corriente que tocaba una global. Dos hilos acababan modificando lo mismo sin el candado. El detector de
carreras lo confirmó en un programa sin ninguna biblioteca.

Pruebas: `aSynchronizedObjectIsNotCreatedAroundSharedData`, `aFunctionOfASynchronizedObjectIsThreadSafe`.

### 21.4 Una función exportada podía devolver una función

Al admitir funciones como parámetro, la comprobación aceptaba también devolverlas, que no cruza. Se
detectó al escribir la sección 17.

---

## 22. Límites conocidos

1. **Listas.** No cruzan, ni como parámetro ni como resultado.
2. **Una función del programa no devuelve un objeto.**
3. **Errores.** No cruzan en ninguna dirección: se capturan dentro.
4. **El mensaje al guardar un objeto de más** sugiere `clone()`; debería sugerir `in default`.
5. **Una biblioteca del sistema que falta** da el error del enlazador de C (sección 11.3).
6. **Un puntero a función de C ajeno que devuelve `String`**: el compilador trata ese texto como si
   viviera todo el programa. Es una suposición sobre el C ajeno que no se comprueba.
7. **Sin separación por procesador** para el C ya compilado.
8. **El C del paquete se recompila** en cada `larimar build` del programa.
9. **Sin gestor de paquetes.** Se copian a mano.

---

# Apéndices

## A. Qué prueba de la suite cubre cada cosa

Están en `tests/project/libraries_test.lar`, salvo las indicadas. Corren con
`./bootstrap/build.sh --verify --test`.

| Prueba | Cubre | Secciones |
|---|---|---|
| `aPackageIsCompiledWithTheProgram` | Paquete usado desde Larimar, `larimar check` | 4 |
| `aPackageBringsItsC` | C de terceros en fuente; dos paquetes en un programa | 10, 14 |
| `aLibraryCallsTheProgramBack` | Funciones del programa: llamada, guardada, desde C, rechazos | 8.1 a 8.4, 8.9 |
| `aCallbackGetsAnObjectAndGivesAText` | La función recibe un objeto y da un texto; rechazos; desde C | 8.5, 19.3 |
| `aMethodKeepsAFunctionInItsObject` | Funciones en métodos; `in self`; rechazo; desde C | 8.10, 8.11 |
| `aLibraryCallsBackFromAnotherThread` | `thread safe` en la biblioteca, en el binding y en el programa | 9 |
| `aLibraryAndItsProgramShareNoNames` | Cada uno con su runtime | 1.2, 14 |
| `aPackageInOneFile` | El `.lpk`; un archivo que no es un zip | 13, 18.3 |
| `aPackageBringsCompiledCAndNamesItsPackages` | C ya compilado; un paquete que usa otro | 12, 14 |
| `aPackageIsNamedByItsFolder` | Una carpeta que no es un paquete | 18.2 |
| `aStaticLibraryForC` | Estática desde C; rechazo en `[packages]` | 15 |
| `aDynamicLibrary` | Dinámica desde C | 15 |
| `anotherBuildIsFoundOut` | El hash de la interfaz | 18.5, 18.6 |
| `theTestsOfALibraryUseItsRules` | `larimar test` en una biblioteca | 16 |
| `anOverrideMayReturnItsArgument` (`tests/memory/results_test.lar`) | El fallo 21.1 | 21.1 |
| `aSynchronizedObjectIsNotCreatedAroundSharedData`, `aFunctionOfASynchronizedObjectIsThreadSafe` (`tests/language/threads_test.lar`) | El fallo 21.3 | 9.6, 21.3 |

Los ejemplos de las secciones 5, 6, 7.4 a 7.7, 11, 17 y buena parte de la 19 se ejecutaron con el banco
de este manual y **no están todavía en la suite**.

## B. Chuleta

```toml
# la biblioteca
[project]
name = "textkit"
kind = "library"
main = "src/textkit.lar"

[library]
prefix = "tk"                 # nombres en C: tk_...
type = "package"              # por defecto; "static" o "dynamic" para C

[c]                           # el C que trae
include_paths = ["vendor/x"]
sources = ["vendor/x/x.c"]

[c.unix]                      # por plataforma: unix, linux, macos, windows
dynamic_libraries = ["m"]

[packages]                    # los paquetes que usa
otra = "libs/otra.lpk"
```

```toml
# el programa
[packages]
textkit = "libs/textkit.lpk"
```

```ts
public export function f(n: int32, text: String): String { ... }          // números y textos
public export function open(name: String): Account { ... }                // un objeto: un handle
public export function each(n: int32, visit: (int32) -> int32): int32     // una función del programa
public export function keep(visit: (int32) -> int32 in default): void     // que la biblioteca guarda
function get(path: String, handler: (Request) -> String in self): void    // en un método: guardada en el objeto
public export function bg(tick: (int32) -> int32 thread safe in default)  // y llama desde otro hilo
```

```sh
larimar build              # build/textkit.lpk y build/textkit/
larimar build --static     # build/textkit/libtextkit.a, para C
larimar build --dynamic    # build/textkit/libtextkit.so, para C
larimar test               # las pruebas de la biblioteca
```
