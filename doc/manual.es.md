# Manual de Larimar

Este manual explica cómo escribir programas en Larimar, de lo más simple a lo más avanzado.
Todos los ejemplos completos (los que tienen `function main`) se compilan y se ejecutan tal cual, y
su salida es la que se muestra.

**No hace falta saber Larimar, C ni ninguna herramienta para leerlo.** Ayuda haber escrito algo de
código en otro lenguaje (saber qué es una variable o una función), pero cada término de Larimar se
explica la primera vez que aparece. Léelo en orden: cada capítulo usa solo lo que explicaron los
anteriores, y los últimos (memoria, hilos, C, proyectos) se apoyan en los primeros.

Algunas palabras aparecen desde el principio:

| Palabra | Qué significa aquí |
|---|---|
| **programa** | un archivo que tu computadora puede ejecutar, como cualquier aplicación (en Windows, un `.exe`) |
| **compilador** | un programa que convierte el texto que escribes en un programa que se puede ejecutar |
| **C** | un lenguaje de programación antiguo y muy extendido; todos los sistemas tienen compiladores para él. Larimar escribe el C por ti: nunca tienes que escribirlo ni leerlo |
| **`larimar`** | la herramienta que escribes en una terminal: revisa tu código, lo convierte en C, lo compila y lo ejecuta |
| **terminal** | la ventana donde se escriben comandos (Terminal en macOS, PowerShell en Windows) |

Los nombres del lenguaje, de la herramienta y de los ejemplos están en inglés; las explicaciones, en español.
[Read in English](manual.md).

## Índice

1. [Primeros pasos](#1-primeros-pasos)
2. [Estructura de un programa](#2-estructura-de-un-programa)
3. [Variables y constantes](#3-variables-y-constantes)
4. [Tipos básicos](#4-tipos-básicos)
5. [Operadores](#5-operadores)
6. [Texto (`String`)](#6-texto-string)
7. [Control de flujo](#7-control-de-flujo)
8. [Funciones](#8-funciones)
9. [Structs](#9-structs)
10. [Clases y herencia](#10-clases-y-herencia)
11. [Interfaces](#11-interfaces)
12. [Enums](#12-enums)
13. [`switch` y patrones](#13-switch-y-patrones)
14. [Opcionales y `null`](#14-opcionales-y-null)
15. [Arreglos y listas](#15-arreglos-y-listas)
16. [Memoria](#16-memoria)
17. [La regla de vida y `clone()`](#17-la-regla-de-vida-y-clone)
18. [Lambdas y closures](#18-lambdas-y-closures)
19. [Errores: `throw`, `try` y `catch`](#19-errores-throw-try-y-catch)
20. [Fallos en tiempo de ejecución](#20-fallos-en-tiempo-de-ejecución)
21. [`Any`: datos de forma libre](#21-any-datos-de-forma-libre)
22. [Hilos](#22-hilos)
23. [Llamar a C](#23-llamar-a-c)
24. [Módulos](#24-módulos)
25. [Biblioteca estándar](#25-biblioteca-estándar)
26. [Proyectos: `larimar.toml` y `larimar build`](#26-proyectos-larimartoml-y-larimar-build)
27. [Bibliotecas escritas en Larimar](#27-bibliotecas-escritas-en-larimar)
28. [Qué genera el transpilador](#28-qué-genera-el-transpilador)
29. [Larimar escrito en Larimar](#29-larimar-escrito-en-larimar)
30. [Limitaciones actuales](#30-limitaciones-actuales)
31. [Referencia rápida](#31-referencia-rápida)

---

## 1. Primeros pasos

### Cómo nace un programa en Larimar

Escribes tu programa como texto, en archivos que terminan en `.lar`. Luego la herramienta `larimar`
hace tres cosas por ti, en un solo comando:

1. **Revisa tu código.** Si algo está mal (un nombre mal escrito, un número donde se esperaba un
   texto), lista cada error con su archivo y su línea, y se detiene ahí.
2. **Lo traduce a C.** Larimar escribe un archivo C equivalente a tu programa. No necesitas mirarlo.
3. **Compila ese C a un programa y lo ejecuta.** Un compilador de C convierte el C en un programa que
   tu computadora ejecuta directamente, tan rápido como los programas escritos en C.

### Instalarlo

En una terminal, en macOS o Linux:

```sh
curl -fsSL https://zerh.github.io/larimar/install.sh | sh
```

En Windows, en PowerShell:

```sh
powershell -c "irm https://zerh.github.io/larimar/install.ps1 | iex"
```

Se instala en la carpeta `.larimar` de tu usuario, sin permisos de administrador, y añade `larimar` a
los comandos de la terminal (abre una terminal nueva después). En Linux y Windows, Larimar trae su
propio compilador de C, así que no hace falta nada más. En macOS usa el de Apple: si falta, el
instalador te dice que ejecutes `xcode-select --install` una vez.

Para comprobarlo, `larimar --version` muestra la versión.

### Tu primer programa

Crea un archivo llamado `hola.lar` con este texto (sirve cualquier editor de texto; VS Code con la
extensión de Larimar además lo colorea y muestra los errores mientras escribes):

```ts
function main(): int32 {
    println("Hello, world");
    return 0;
}
```

Y ejecútalo desde la terminal, en la carpeta del archivo:

```sh
larimar hola.lar
```

Salida: `Hello, world`

Línea por línea:

- `function main(): int32 {` declara una **función** llamada `main`. Una función es un trozo de código
  con nombre; `main` es especial: es donde empieza todo programa. `(): int32` significa que no recibe
  nada y devuelve un número entero (`int32` es el tipo de los enteros, explicado en el
  [capítulo 4](#4-tipos-básicos)). Las llaves `{ }` encierran lo que hace la función.
- `println("Hello, world");` escribe el texto entre comillas y pasa a la línea siguiente. Cada
  instrucción termina con `;`.
- `return 0;` termina `main` y devuelve `0`. Ese número es el **código de salida** del programa: `0`
  significa que todo fue bien, y cualquier otro número que algo falló. Un `main` que no tiene nada que
  informar se puede declarar `function main(): void` (o solo `function main()`) y no llevar `return`.

### Cuando algo está mal

Si el programa tiene errores, Larimar los lista todos y no ejecuta nada. Por ejemplo, al darle un
texto a una variable declarada como número:

```
Semantic Error [hola.lar:2]: Initializer of 'x': expected int32 but got String.
```

El mensaje dice **dónde** (el archivo y la línea, `hola.lar:2`) y **qué** (esperaba un `int32` y
recibió un `String`). Los mensajes de error intentan decir también cómo arreglar el problema. Están
en inglés, como los nombres del lenguaje.

### Proyectos

Un solo archivo `.lar` basta para programas pequeños y scripts. Cuando un programa crece a varios
archivos, o necesita bibliotecas de C, pasa a ser un **proyecto**: una carpeta con un archivo llamado
`larimar.toml` que dice cómo se llama el programa y cómo construirlo.

```sh
larimar new hello        # crea la carpeta hello con un proyecto dentro
cd hello
larimar run              # construye el programa y lo ejecuta
```

`larimar new` crea tres archivos:

- `larimar.toml`, la descripción del proyecto. Está escrito en **TOML**, un formato de texto sencillo
  de líneas `clave = valor` agrupadas bajo títulos entre corchetes (`[project]`). El
  [capítulo 26](#26-proyectos-larimartoml-y-larimar-build) explica cada clave.
- `src/main.lar`, el archivo principal, con un `main` como el de arriba.
- `.gitignore`, para que git no guarde la carpeta `build/`, donde queda el programa construido.

`larimar build` construye el programa sin ejecutarlo: queda en `build/hello` (`build\hello.exe` en
Windows), y se puede copiar y ejecutar en otra computadora del mismo sistema sin instalar nada.

### Qué compilador de C lo construye

Puedes saltarte esto hasta que te importe. Larimar necesita un compilador de C para terminar el programa:

- En Linux y Windows trae uno, **tcc**, en `$LARIMAR_HOME/toolchain/tcc` (`LARIMAR_HOME` es la carpeta
  donde está instalado Larimar). En macOS usa el de Apple.
- `larimar archivo.lar` (un archivo, ejecutado al momento) usa primero el tcc incluido: compila en un instante.
- Un proyecto (`larimar run`, `build`, `test`) usa el compilador del sistema (cc, gcc o clang) cuando
  hay uno, porque hace programas más rápidos; el tcc incluido solo cuando no hay ninguno, con una nota que lo dice.
- `--cc <programa>`, la variable `CC` o `compiler = "..."` en el `larimar.toml` eligen otro (`tcc`: el incluido).
- Un programa que usa TLS (direcciones `https://`) necesita el compilador del sistema: el tcc incluido no
  puede compilarlo, y Larimar dice qué instalar. Las pruebas compiladas con tcc corren sin
  AddressSanitizer (un detector de errores de memoria en C).

`larimar archivo.lar` le pasa al programa los argumentos que van después del archivo (después de `--`
cuando parecen opciones de larimar), solo imprime lo que imprime el programa y termina con su código de
salida: sirve para scripts y tuberías.

---

## 2. Estructura de un programa

Dos palabras describen las partes de un programa:

- Una **declaración** le da nombre a algo: una función, una constante, un tipo de datos.
- Una **instrucción** es una orden que hace algo cuando el programa se ejecuta: `println(...)`,
  `return 0;`, darle un valor a una variable.

Las instrucciones van dentro de funciones. Fuera de toda función, en lo que se llama el **nivel
superior** del archivo, solo puede haber declaraciones:

| Declaración | Ejemplo |
|---|---|
| Importación | `import geo.shapes;` (al principio del archivo; ver [Módulos](#24-módulos)) |
| Función | `function add(a: int32, b: int32): int32 { ... }` |
| Constante | `const MAX: int32 = 64;` |
| Variable global | `let counter: int32 = 0;` |
| Struct | `struct Point { ... }` |
| Clase | `class Animal { ... }`, `synchronized class Counter { ... }` (ver [Hilos](#22-hilos)) |
| Interfaz | `interface Drawable { ... }` |
| Enum | `enum Color { Red, Green }` |
| Código C | `cinclude "<math.h>";`, `native function ...`, `native type ...` |

Un programa puede repartirse en varios archivos; cada uno es un **módulo** ([capítulo 24](#24-módulos)).
Cualquier declaración puede llevar `public` delante para que otros módulos la usen.

El orden de las declaraciones no importa: una función puede usar otra que esté más abajo.
Las variables globales se inicializan en el orden en que aparecen, antes de `main`. Por eso el valor
inicial de una global solo puede usar las de arriba, y las funciones que llama tampoco pueden usar una
de más abajo: la encontrarían sin su valor, y el compilador lo dice.

Los comentarios son como en C: `// hasta el final de la línea` y `/* en bloque */`.
Cada instrucción termina en `;`, y los bloques van entre `{ }`.

---

## 3. Variables y constantes

Una **variable** es un nombre que guarda un valor, que puede cambiar mientras el programa se ejecuta.
Se declara con `let`, su nombre, su **tipo** (qué clase de valor guarda: un número, un texto…) y su
primer valor:

```ts
let age: int32 = 30;
let name: String = "Ana";
age = 31;          // las variables se pueden reasignar
age += 1;          // también +=, -=, *=, /=, %=, &=, |=, ^=
```

`a op= b` es `a = a op b`, con el lugar calculado una vez: en `counts[next()] += 1`, `next()` se ejecuta una vez.

- El **tipo es obligatorio**, y también el **valor inicial**: no existen variables sin inicializar.
- Una variable declarada dentro de un bloque solo existe dentro de él.
- Se puede declarar una variable con el mismo nombre que otra de un bloque exterior; la interior la oculta.

Las **constantes** se declaran a nivel superior, y su valor se calcula al compilar. Pueden ser
números, `bool` o `String`, y se pueden usar como tamaño de un arreglo:

```ts
const SIZE: int32 = 16;
const KILO: int64 = 1024;
const MEGA: int64 = KILO * KILO;
const LABEL: String = "sensor";

function main(): int32 {
    let data: int32[SIZE] = [];
    println("${LABEL}: ${data.length} of ${SIZE}, ${MEGA} bytes");
    return 0;
}
```

Salida: `sensor: 0 of 16, 1048576 bytes`

---

## 4. Tipos básicos

| Tipo | Valores | En C |
|---|---|---|
| `int8`, `int16`, `int32`, `int64` | enteros con signo | `int8_t` … `int64_t` |
| `byte` (o `uint8`), `uint16`, `uint32`, `uint64` | enteros sin signo | `uint8_t` … `uint64_t` |
| `float32`, `float64` | decimales | `float`, `double` |
| `bool` | `true`, `false` | `bool` |
| `String` | texto | estructura del runtime |
| `void` | nada (solo como tipo de retorno) | `void` |

Los tipos **primitivos se escriben en minúscula**: son valores simples que nunca necesitan memoria,
no tienen campos y no se pueden redefinir. Todo lo demás empieza con mayúscula: `String` (que sí
necesita memoria), y los structs, clases, interfaces y enums que declares. Así, con mirar el nombre
se sabe si un tipo es del lenguaje o es tuyo. Es una convención: el compilador no la exige, pero la
biblioteca estándar y estas páginas la siguen.

### Literales numéricos

```ts
let a: int32 = 1_000_000;     // los _ separan dígitos
let b: byte = 0xFF;           // hexadecimal
let c: byte = 0b1010_0101;    // binario
let d: float64 = 2.5e3;       // exponente
```

Un literal entero toma el tipo que se espera en ese lugar. El compilador comprueba que quepa:
`let b: byte = 256;` es un error.

### Caracteres

`'a'` es el código del carácter (su número Unicode), y se usa como cualquier literal entero: toma
el tipo que se espera. Sirve sobre todo para comparar bytes de un texto:

```ts
function digits(s: String): int32 {
    let n: int32 = 0;
    for (b in s) {
        if (b >= '0' && b <= '9') { n += 1; }
    }
    return n;
}

function main(): int32 {
    let first: byte = "hola"[0];
    println("${first == 'h'} ${digits("a1b22")} ${'A'} ${'\n'} ${'€'}");
    return 0;
}
```

Salida: `true 3 65 10 8364`

Escapes: `'\n'`, `'\t'`, `'\r'`, `'\0'`, `'\\'`, `'\''` y `'\"'`. Un literal tiene exactamente un
carácter; si el código no cabe en el tipo (`let b: byte = '€';`), es un error.

### Desbordamiento

Los enteros **vuelven a empezar** cuando se pasan del máximo o del mínimo, con y sin signo.
Nunca hay comportamiento indefinido:

```ts
function main(): int32 {
    let max: int32 = 2147483647;
    let b: byte = 255;
    b += 1;
    println("${max + 1} ${b}");
    return 0;
}
```

Salida: `-2147483648 0`

### Conversiones con `as`

No hay conversiones automáticas entre tipos numéricos. Se hacen con `as`:

```ts
function main(): int32 {
    let n: int32 = 7;
    let wide: int64 = n as int64;
    let half: float64 = (n as float64) / 2.0;
    let huge: float64 = 1e20;
    println("${wide} ${half} ${huge as int32} ${-1.5 as byte}");
    return 0;
}
```

Salida: `7 3.5 2147483647 0`

De decimal a entero se trunca, y si el valor no cabe se usa el límite más cercano (en lugar del
comportamiento indefinido de C).

### Decimales como texto

Un decimal se escribe con **los dígitos justos para que, al leerlo, dé el mismo valor**, como en Go,
Java o JavaScript: `0.1 * 3.0` es `0.30000000000000004` (ese es su valor real), y un `float32` `0.1` es
`0.1`. Siempre lleva `.` o exponente, para que se lea como decimal: `2.0`, `1234567.0`, `1e+20`,
`1e-05`. Sin exponente desde `0.0001` hasta `1e15`. Y `nan`, `inf`, `-inf`. Lo que se imprime, leído
con `toFloat()`, da el mismo número.

---

## 5. Operadores

| Precedencia (de menor a mayor) | Operadores |
|---|---|
| condicional | `c ? a : b` (de derecha a izquierda) |
| valor por defecto de un opcional | `??` |
| o lógico | `\|\|` |
| y lógico | `&&` |
| comparación | `==` `!=` `<` `<=` `>` `>=` |
| bits | `\|`, luego `^`, luego `&` |
| desplazamiento | `<<` `>>` |
| suma | `+` `-` |
| producto | `*` `/` `%` |
| conversión | `as` |
| unarios | `-` `!` `~` |
| sufijos | llamada `f()`, campo `a.b`, índice `a[i]`, `x!` |

Reglas:
- Los dos lados de un operador deben ser **del mismo tipo** (`int32 + int64` es un error; usa `as`).
  Los literales se adaptan al otro lado.
- `as` se aplica antes que las comparaciones: `n > MAX as int64 ? a : b` es `(n > (MAX as int64)) ? a : b`,
  sin paréntesis. Después de `as T`, un `?` seguido del principio de una expresión es el del
  condicional; seguido de `)`, `;`, `,`, `??`, `==`... es parte del tipo (`T?`).
- `/` y `%` entre enteros comprueban la división por cero. `%` solo es para enteros.
- Los operadores de bits están **por encima** de las comparaciones, así que `x & 1 == 0`
  significa `(x & 1) == 0`, no la trampa de C.
- En `a << n`, solo se usan los bits bajos de `n` (para `uint32`, `n & 31`).
- `&&` y `||` no evalúan el lado derecho si no hace falta.
- `==` compara números, `bool`, `String` (por contenido), enums sin datos y objetos (por identidad).
  Un objeto opcional (`Node?`) se puede comparar con un `Node`.
- **Todo se evalúa de izquierda a derecha**, una vez: los operandos de un operador, los argumentos de
  una llamada (después del objeto de un método), los elementos de una lista y los campos de un literal
  **en el orden en que están escritos**, y en una asignación el lugar antes que el valor. C deja ese
  orden abierto; Larimar lo fija, así un programa hace lo mismo con cualquier compilador de C.

### El condicional `c ? a : b`

Da `a` si la condición es `true`, y `b` si no. Solo se evalúa el lado elegido:

```ts
class Animal { let name: String; }
class Dog extends Animal { }
class Cat extends Animal { }

function sign(n: int64): String { return n > 0 ? "+" : n < 0 ? "-" : "0"; }

function main(): int32 {
    let big: int64 = 10000000000;
    let small: bool = true;
    let n: int64 = small ? 1 : big;                    // el literal toma el tipo int64
    let dog: Dog = Dog { name: "Rex" };
    let cat: Cat = Cat { name: "Tom" };
    let pet: Animal = small ? dog : cat;              // la clase común más cercana
    let maybe: Dog? = small ? null : dog;             // con null, el tipo es opcional
    println("${n} ${pet.name} ${maybe == null} ${sign(-3)}");
    return 0;
}
```

Salida: `1 Rex true -`

- El tipo sale del lado que no es un literal suelto (un número o `null`); el otro se adapta. Si los
  dos lados tienen tipos distintos (`int64` y `String`), es un error: da un tipo a la variable.
- Cada lado sabe lo que dice la condición: en `x != null ? x.value : 0`, `x` no es `null` a la izquierda.
- También vale en constantes: `const SIZE: int32 = DEBUG ? 16 : 1024;`.

---

## 6. Texto (`String`)

Un `String` es **inmutable**: una vez creado, no cambia. Se compara por contenido y tiene `length`
(en bytes, porque el texto es UTF-8).

```ts
enum Color { Red, Green }

function main(): int32 {
    let name: String = "Ana";
    let n: int32 = 3;
    let color: Color = Color.Green;
    let message: String = "${name} has ${n} apples of color ${color}";
    println(message);
    println("${name == "Ana"} ${message.length}");
    return 0;
}
```

Salida:
```
Ana has 3 apples of color Green
true 31
```

- **Interpolación**: `"${expresión}"` admite números, `bool`, `String` y enums (se imprime el nombre de la variante).
- **Escapes**: `\n`, `\t`, `\r`, `\0`, `\\`, `\"`, `\'` y `\$` (para escribir `$` literal).
- **No hay `+` para texto**: se une con interpolación, `"${a}${b}"`.
- `print(text)` y `println(text)` escriben en la salida estándar.

Un texto con interpolación necesita memoria para existir. Dónde se crea se explica en la
[sección 16](#16-memoria); por ahora basta saber que, si no dices nada, el compilador lo pone donde
corresponde y lo libera cuando deja de usarse.

### Texto en varias líneas: `"""`

Como en Java, un bloque de texto empieza con `"""` y un salto de línea, y termina con `"""`. Se
quita la sangría común a todas las líneas (y a la línea del `"""` final, si está sola), y los espacios
al final de cada línea. Las comillas no necesitan escape, y los escapes y `${...}` funcionan igual:

```ts
function main(): int32 {
    let name: String = "Ana";
    let page: String = """
        <p class="greeting">
          Hola, ${name}.
        </p>
        """;
    print(page);
    return 0;
}
```

Salida:
```
<p class="greeting">
  Hola, Ana.
</p>
```

Con el `"""` final al terminar la última línea, el texto no acaba en salto de línea.

### Texto crudo: `raw"""`

Un `raw"""` es un bloque de texto que se toma **tal como está escrito**: sin escapes (una barra `\` es
una barra) y sin `${...}`. Sirve para texto que tiene sus propias comillas y barras, como código C, SQL,
expresiones regulares o plantillas:

```ts
let code: String = raw"""
    printf("hola\n");      /* \n son dos caracteres: \ y n */
    char* p = "${HOME}";   /* ${...} es texto, no se interpola */
    """;
```

- Como en `"""`, empieza con `raw"""` y un salto de línea, y se quita la sangría común.
- Si el texto tiene tres comillas seguidas, se abre con más comillas y se cierra con las mismas:
  `raw""""` ... `""""`.
- Es la forma de llevar SQL, HTML o C en un programa: el texto va tal cual, sin escapar nada.

### Métodos

Un `String` está hecho de **bytes** (UTF-8): `s[i]` es un `byte`, `for (b in s)` recorre sus bytes, y
`length` cuenta bytes. Una letra con tilde ocupa dos; para contar letras está `codePointCount()`.

```ts
function main(): int32 {
    let s: String = "  Hello, Larimar world!  ";
    let t: String = s.trim();                                  // una vista: no copia nada
    println("[${t}] ${t.indexOf("o") ?? -1} ${t.contains("Larimar")} ${t.count("l")}");
    println("${t.substring(7, 14)} ${t.toUpperCase()} ${t.replace("l", "L")}");
    let parts: String[*] = "a,b,,c".split(",");
    println("${parts.length}: ${parts.join(" | ")}");
    println("${"42".toInt() ?? 0} ${"0x1F".toInt() ?? 0} ${"x".toInt() ?? -1} ${"2.5".toFloat() ?? 0.0}");
    println("${"apple" < "banana"} ${"7".padStart(3, "0")} ${"ab".repeat(3)} ${t[0]}");
    return 0;
}
```

Salida:
```
[Hello, Larimar world!] 4 true 3
Larimar HELLO, LARIMAR WORLD! HeLLo, Larimar worLd!
4: a | b |  | c
42 31 -1 2.5
true 007 ababab 72
```

| Grupo | Métodos |
|---|---|
| Consultar | `length`, `isEmpty()`, `isBlank()`, `s[i]` (un `byte`), `for (b in s)`, `codePointCount()` |
| Buscar | `indexOf(t)`, `indexOf(t, from)`, `lastIndexOf(t)` (dan `int32?`), `contains(t)`, `startsWith(t)`, `endsWith(t)`, `count(t)` |
| Cortar: **vistas**, sin copiar | `substring(from)`, `substring(from, to)`, `trim()`, `trimStart()`, `trimEnd()`, `bytes()` (un `byte[]`) |
| Crear texto nuevo | `toUpperCase()`, `toLowerCase()`, `replace(a, b)`, `repeat(n)`, `padStart(n, s)`, `padEnd(n, s)` |
| Dividir y unir | `split(sep)`, `lines()`, `codePoints()` (listas nuevas); `list.join(sep)` |
| Comparar | `==`, `!=`, `<`, `<=`, `>`, `>=` (orden de bytes), `compareTo(t)`, `equalsIgnoreCase(t)` |
| Convertir | `toInt()` (`int64?`: decimal, `0x`, `0b`, con `_`), `toFloat()` (`float64?`), `toBool()` (`bool?`) |

- **Las vistas comparten los bytes del texto original**: cortar es instantáneo y no usa memoria. Viven
  tanto como el original, y la regla de vida lo comprueba.
- **Lo que crea texto nuevo** va, como la interpolación, donde corresponda o a la memoria que digas
  con `in`: `s.toUpperCase() in memory`. Las listas de `split`, `lines` y `codePoints` también.
- `toUpperCase`, `toLowerCase` y `equalsIgnoreCase` cambian solo letras ASCII.
- Un `String` no se modifica: `s[0] = 65` es un error. Para construir texto está `StringBuilder`.
- `length` se lee sin paréntesis, aquí y en todo (listas, arrays, `Any`, memorias, `StringBuilder`): lo
  que es un dato no lleva paréntesis, lo que hace algo sí. `s.length()` es un error que lo dice.

### `StringBuilder`

Para construir un texto grande por partes sin crear uno nuevo cada vez:

```ts
function main(): int32 {
    let out: StringBuilder = {};
    for (i in 0..3) { out.add("item ${i}, "); }   // la interpolación se escribe directo en el builder
    out.addLine("end");
    let text: String = out.toString();          // una vista de lo construido hasta ahora
    println("${text.length} ${out.length}");
    print(text);
    return 0;
}
```

Salida:
```
28 28
item 0, item 1, item 2, end
```

`add(text)`, `addLine(text)`, `length`, `toString()` y `clear()`. El texto crece en la memoria del
builder. Lo que devuelve `toString()` no cambia aunque después se añada más o se llame a `clear()`.

---

## 7. Control de flujo

### `if`

```ts
function classify(n: int32): String {
    if (n < 0) {
        return "negative";
    } else if (n == 0) {
        return "zero";
    } else {
        return "positive";
    }
}
```

Las llaves son obligatorias. La condición debe ser `bool`: `if (1)` es un error.

### `while`

```ts
let i: int32 = 0;
while (i < 10) {
    i += 1;
}
```

### `for`

```ts
for (i in 0..5) { }            // 0, 1, 2, 3, 4 (el final no se incluye)
for (x in items) { }           // cada elemento
for (i, x in items) { }        // índice y elemento
```

Las variables del `for` no se pueden reasignar dentro del cuerpo.

### Bloques

Unas llaves sueltas forman un bloque: lo que se declara dentro solo existe ahí, y las memorias creadas
dentro se liberan al cerrarlo. Sirve para acotar memorias e hilos ([sección 22](#22-hilos)).

```ts
{
    let scratch: byte[*] = [] in heap;
    let text: String = "temporary ${1}" in scratch;
    println(text);
}   // 'scratch' se libera aquí
```

### `break` y `continue`

Funcionan como en C o Java, dentro de `while` y `for`.

```ts
function main(): int32 {
    let sum: int32 = 0;
    for (i in 0..10) {
        if (i % 2 == 0) { continue; }
        if (i > 7) { break; }
        sum += i;
    }
    println("${sum}");     // 1 + 3 + 5 + 7
    return 0;
}
```

Salida: `16`

---

## 8. Funciones

Una función es un trozo de código con nombre, que se puede usar (**llamar**) desde otros sitios.
Recibe valores (sus **parámetros**, cada uno con su tipo), y puede devolver uno con `return` (el tipo
después de los `:` dice cuál; `void` significa que no devuelve nada):

```ts
function add(a: int32, b: int32): int32 {
    return a + b;
}

function greet(name: String): void {
    println("Hello, ${name}");
}

function bye() {               // ": void" se puede omitir
    println("Bye");
}
```

- Los parámetros llevan tipo siempre.
- Si la función no devuelve `void`, **todos los caminos** deben terminar en `return` (o `throw`).
  Un `while (true)` sin `break` cuenta como un camino que nunca termina.
- Las funciones se declaran a nivel superior o dentro de clases y structs. Dentro de un cuerpo se usan lambdas.
- Para pasar una función donde se espera una función, escribe `::add` (ver [Referencias a funciones](#referencias-a-funciones-))
  o una lambda ([capítulo 18](#18-lambdas-y-closures)): `(x) -> { return add(x, 1); }`.

### `main` y los argumentos del programa

`main` puede recibir los argumentos con los que se ejecutó el programa (sin su propio nombre):

```ts
function main(args: String[]): int32 {
    if (args.length == 0) {
        println("usage: greet <name>");
        return 2;
    }
    println("Hello, ${args[0]}");
    return 0;
}
```

Con `larimar run -- Ana` imprime `Hello, Ana`. Lo que devuelve `main` es el código de salida.

---

## 9. Structs

Un `struct` es un **valor**: un grupo de campos que se copia entero al asignarlo o pasarlo.
No necesita memoria especial; vive donde vive la variable.

```ts
struct Vector2 {
    let x: int32;
    let y: int32 = 0;                      // valor por defecto

    function length2(): int32 {            // un método
        return self.x * self.x + self.y * self.y;
    }

    function scale(k: int32): void {       // los métodos pueden modificar self
        self.x = self.x * k;
        self.y = self.y * k;
    }

    operator +(other: Vector2): Vector2 {
        return { x: self.x + other.x, y: self.y + other.y };
    }

    operator ==(other: Vector2): bool {
        return self.x == other.x && self.y == other.y;
    }
}

function main(): int32 {
    let a: Vector2 = { x: 1, y: 2 };       // literal: el tipo sale de la variable
    let b: Vector2 = Vector2 { x: 3 };     // con el tipo escrito; y = 0 por defecto
    let c: Vector2 = a + b;
    c.scale(2);
    let copy: Vector2 = c;                 // una copia independiente
    copy.x = 100;
    println("(${c.x}, ${c.y}) ${c.length2()} ${copy.x} ${a == b}");
    return 0;
}
```

Salida: `(8, 4) 80 100 false`

### Literales

- `{ field: value, ... }` cuando el tipo se sabe por el contexto (una variable, un parámetro, un `return`).
- `Type { field: value }` cuando no.
- `{ x, y }` es la abreviatura de `{ x: x, y: y }`.
- Los campos sin valor por defecto son **obligatorios**: si falta uno, es un error de compilación.
- Un struct nunca lleva `in`: es un valor y vive en su variable. (Los objetos de clase, en cambio, siempre lo llevan.)
- Los valores por defecto deben ser constantes (literales, `null`, `[]`, enums o structs hechos de constantes).

### Operadores

Un struct (o una clase) puede definir `+ - * / % == <` y el `-` unario (`operator -()`, sin parámetros).
A partir de `==` se obtiene `!=`, y a partir de `<` se obtienen `>`, `<=` y `>=`.
Sin `operator ==`, comparar dos structs con `==` es un error.

---

## 10. Clases y herencia

Una clase define **objetos**: tienen identidad, viven en una memoria y se usan por **referencia**.
Asignar un objeto a otra variable no lo copia; las dos variables apuntan al mismo objeto.

```ts
class Animal {
    let name: String;

    function sound(): String { return "..."; }

    function introduce(): void {
        println("${self.name} says ${self.sound()}");
    }
}

class Dog extends Animal {
    let breed: String = "mixed";

    override function sound(): String { return "woof"; }
}

class Puppy extends Dog {
    override function sound(): String { return "yip"; }

    override function introduce(): void {
        super.introduce();
        println("(and it is a ${self.breed} puppy)");
    }
}

function main(): int32 {
    let a: Animal = Animal { name: "Kitty" };
    let d: Dog = Dog { name: "Rex", breed: "shepherd" };
    let p: Animal = Puppy { name: "Bobby" };

    a.introduce();
    d.introduce();
    p.introduce();

    let same: Animal = d;       // la misma referencia
    same.name = "Rexy";
    println(d.name);
    return 0;
}
```

Salida:
```
Kitty says ...
Rex says woof
Bobby says yip
(and it is a mixed puppy)
Rexy
```

- Los objetos se crean con un literal, como los structs: `Dog { name: "Rex" }`, o `Dog {}` si todos los
  campos tienen valor por defecto. No existe `new`.
- Un objeto vive en una memoria: si no se dice nada, la de su variable (su bloque), la de la lista donde
  se añade, o la de quien llama si se devuelve. Con `in` se elige: `Dog { name: "Rex" } in memory`, o
  `in default` para que viva todo el programa (ver [sección 16](#16-memoria)).
- Un struct es un valor, no vive en ninguna memoria; escribir `in` después de él es un error.
- **Herencia simple**: `extends` una sola clase. Los campos y métodos se heredan.
- Todos los métodos son **virtuales**: se ejecuta el de la clase real del objeto.
- Redefinir un método exige **`override`**, y debe tener exactamente la misma firma.
  Escribir `override` en un método que no existe en el padre también es un error.
- `super.method(...)` llama a la versión del padre.
- Un campo no puede redefinir uno heredado.
- Un `Dog` se puede usar donde se espera un `Animal`. Al revés no: para pasar de `Animal` a `Dog`
  se usa un `switch` con un patrón de tipo ([sección 13](#13-switch-y-patrones)).
- `==` entre objetos compara identidad (si son el mismo objeto), salvo que la clase defina `operator ==`.

### Funciones estáticas

Una función estática pertenece al tipo, no a un objeto: no tiene `self` y se llama con el nombre del tipo.
Se puede escribir dentro del tipo con `static`, o fuera con `function Tipo.nombre`; las dos formas son lo mismo.

```ts
class Order {
    let id: int32;
    let owner: String;

    static function make(owner: String): Order {
        return Order { id: 1, owner: owner };
    }
}

function Order.empty(): Order {
    return Order { id: 0, owner: "" };
}

function main(): int32 {
    let o: Order = Order.make("Ana");
    println("${o.owner} ${Order.empty().id}");
    return 0;
}
```

- Valen en `struct`, `class`, `enum` y `native type`. Las interfaces no tienen funciones estáticas.
- En un `native type` también se puede escribir `static native function nombre(...) = funcion_c;`, que llama
  a esa función de C ([Tipos de C con miembros](#tipos-de-c-con-miembros)).
- `function Tipo.nombre` solo se puede escribir en el módulo que declara el tipo.
- Se llaman siempre como `Tipo.nombre(...)` (o `modulo.Tipo.nombre(...)`); no desde un objeto.
- No usan `self`, no entran en la tabla virtual y no se redefinen con `override`.
- Un tipo no puede tener un método y una función estática con el mismo nombre.
- Son visibles donde lo es su tipo: se marca `public` el tipo, no la función.

---

## 11. Interfaces

Una interfaz describe **qué se puede hacer** con algo: solo firmas de métodos, sin campos.

```ts
interface Drawable {
    function draw(): void;
}
```

Hay tres formas de cumplirla:

**1. Con una clase**, declarándolo con `implements` (una clase puede implementar varias):

```ts
class Circle implements Drawable {
    let radius: float64;
    function draw(): void { println("circle of radius ${self.radius}"); }
}
```

**2. Con un literal**, dando cada método como una lambda:

```ts
let mark: Drawable = { draw: () -> { println("X"); } };
```

**3. Con una lambda**, si la interfaz tiene un solo método:

```ts
let quick: Drawable = () -> { println("quick"); };
```

Un ejemplo completo:

```ts
interface Drawable {
    function draw(): void;
}

class Circle implements Drawable {
    let radius: float64;
    function draw(): void { println("circle of radius ${self.radius}"); }
}

function main(): int32 {
    let things: Drawable[*] = [];
    things.push(Circle { radius: 2.0 });
    things.push({ draw: () -> { println("a literal"); } });
    things.push(() -> { println("a lambda"); });
    for (t in things) { t.draw(); }
    return 0;
}
```

Salida:
```
circle of radius 2.0
a literal
a lambda
```

A quien recibe un `Drawable` le da igual cuál de las tres formas hay detrás.

Una interfaz puede **extender** otras: tiene también sus métodos, y una clase que la implementa es
también cada una de ellas.

```ts
interface Named {
    function name(): String;
}

interface Pet extends Named {
    function sound(): String;
}

class Dog implements Pet {
    function name(): String { return "Rex"; }
    function sound(): String { return "woof"; }
}

let n: Named = Dog {};          // un Dog es un Pet, y por eso un Named
```

Un valor cuyo tipo es `Pet` no se vuelve `Named` (solo los objetos de las clases).

---

## 12. Enums

Un enum es un valor que es **una de varias variantes**. Las variantes pueden llevar datos.

```ts
enum State { Off, On, Failed }

enum Shape {
    Circle(radius: float64),
    Rect(width: float64, height: float64),
    Empty
}
```

Crear valores:

```ts
let s: State = State.On;
let a: Shape = Shape.Circle { radius: 2.0 };            // por nombre
let b: Shape = Shape.Rect { height: 4.0, width: 3.0 };  // el orden no importa
let c: Shape = Shape.Rect(3.0, 4.0);                    // atajo por posición
let d: Shape = Shape.Empty;
```

- Los enums **sin datos** se pueden comparar con `==` y `!=`.
- Los enums con datos se examinan con un `switch` ([sección 13](#13-switch-y-patrones)).
- En una interpolación, un enum se escribe con el nombre de su variante: `"${s}"` da `On`.
- Los enums son valores: se copian, como los structs.

---

## 13. `switch` y patrones

El `switch` sigue el estilo moderno de Java: cada caso usa `->`, no hay "caída" de un caso al siguiente,
y no hace falta `break`.

### Como instrucción

```ts
switch (state) {
    case Off -> println("off");
    case On -> {
        println("on");
        println("all good");
    }
    case Failed -> println("failed");
}
```

Un caso sin llaves debe ser una llamada; para cualquier otra cosa usa `{ }`.

### Como expresión

```ts
let text: String = switch (n) {
    case 0 -> "zero";
    case 1, 2, 3 -> "a few";               // varios valores en un caso
    default -> {
        if (n < 0) { yield "negative"; }   // yield da el valor desde un bloque
        yield "many";
    }
};
```

Dentro de un `switch` usado como expresión, los bloques terminan con `yield value;`, y `return` no está permitido.
Si el resultado es opcional (`T?`), un caso puede dar `null`:

```ts
function digit(c: byte): int32? {
    return switch (c) {
        case '0' -> 0;
        case '1' -> 1;
        default -> null;
    };
}
```

### Patrones

| Patrón | Funciona con | Significado |
|---|---|---|
| `0`, `-1`, `2.5`, `"a"`, `true` | números, `String`, `bool` | igual a ese valor |
| `MAX` | lo mismo | igual a esa constante |
| `Circle` | enums | esa variante |
| `Circle { radius }` | enums | esa variante, sacando el campo `radius` |
| `Rect { width: w, height: h }` | enums | sacando campos con otro nombre |
| `Rect r` | enums | la variante, con el valor entero en `r` |
| `Rect { height } r` | enums | las dos cosas |
| `Dog d` | clases e interfaces | si el objeto es un `Dog` (o subclase), como `Dog` en `d` |
| `null` | opcionales | si no hay valor |
| `default` | todo | cualquier otro caso |

Los campos de un patrón se toman **por nombre**: el orden no importa y los que no nombres se ignoran.

`when` añade una condición a un caso:

```ts
enum Shape { Circle(radius: float64), Rect(width: float64, height: float64), Empty }

class Animal { let name: String; }
class Dog extends Animal { let breed: String = "mixed"; }

function area(s: Shape): float64 {
    return switch (s) {
        case Circle { radius } when radius > 10.0 -> 0.0;   // demasiado grande: no se cuenta
        case Circle { radius } -> 3.0 * radius * radius;
        case Rect { width: w, height: h } -> w * h;
        case Empty -> 0.0;
    };
}

function describe(a: Animal): String {
    return switch (a) {
        case Dog d -> "a ${d.breed} dog";
        default -> "an animal";
    };
}

function main(): int32 {
    println("${area(Shape.Circle { radius: 2.0 })} ${area(Shape.Rect(3.0, 4.0))} ${area(Shape.Empty)}");
    println(describe(Dog { name: "Rex", breed: "shepherd" }));
    println(describe(Animal { name: "Kitty" }));
    return 0;
}
```

Salida:
```
12.0 12.0 0.0
a shepherd dog
an animal
```

### Cubrir todos los casos

- Un `switch` sobre un **enum** debe cubrir todas las variantes (o tener `default`), sea instrucción
  o expresión. Si mañana añades una variante, el compilador te señala cada `switch` que hay que revisar.
- Los casos con `when` no cuentan como cubiertos.
- Un `switch` usado como **expresión** sobre cualquier otro tipo necesita `default`.
- Dentro de un `switch` en un bucle, `break` y `continue` se refieren al bucle.

### Un solo caso: `x is T nombre`

Para preguntar por una sola clase no hace falta un `switch`: `x is Dog` es `true` si `x` es un `Dog`
(o una subclase), y `x is Dog d` además le da el nombre `d`, ya como `Dog`, donde la prueba se sabe
cierta: dentro del `if`, a la derecha de `&&`, en un lado de `?:`, y después de un
`if (!(x is Dog d)) { return ...; }`.

```ts
class Animal { let name: String; }
class Dog extends Animal { let breed: String = "mixed"; }

function describe(a: Animal?): String {
    if (a is Dog d && d.breed != "mixed") { return "${d.name}, a ${d.breed}"; }
    if (!(a is Dog d)) { return "not a dog"; }
    return "${d.name}, a dog";
}

function main(): int32 {
    let rex: Dog = Dog { name: "Rex", breed: "beagle" };
    let tom: Animal = Animal { name: "Tom" };
    println("${describe(rex)} | ${describe(tom)} | ${describe(null)} | ${tom is Dog}");
    return 0;
}
```

Salida: `Rex, a beagle | not a dog | not a dog | false`

`x` puede ser un objeto, un objeto opcional o una interfaz, y `T` una clase con la que pueda coincidir.

---

## 14. Opcionales y `null`

Ningún valor es `null` salvo que su tipo lo permita con `?`.

```ts
let a: int32 = null;      // error
let b: int32? = null;     // bien
```

Para usar un opcional:

| Forma | Qué hace |
|---|---|
| `x ?? value` | `x` si tiene valor; si no, `value` |
| `x!` | el valor; si es `null`, el programa se detiene |
| `if (x != null) { ... }` | dentro del bloque, `x` se usa como si no fuera opcional |
| `switch (x) { case null -> ...; default -> ... }` | por casos |

```ts
class Node {
    let value: int32;
    let next: Node? = null;
}

function count(first: Node?): int32 {
    let total: int32 = 0;
    let current: Node? = first;
    while (current != null) {
        total += current.value;
        current = current.next;
    }
    return total;
}

function describe(n: Node?): String {
    if (n == null || n.value < 0) { return "none"; }
    return "value ${n.value}";
}

function main(): int32 {
    let c: Node = Node { value: 3 };
    let b: Node = Node { value: 2, next: c };
    let a: Node = Node { value: 1, next: b };
    println("${count(a)} ${count(null)} ${describe(a)} ${describe(null)}");

    let maybe: int32? = null;
    println("${maybe ?? 7}");
    maybe = 5;
    if (maybe != null) { println("has ${maybe + 1}"); }
    return 0;
}
```

Salida:
```
6 0 value 1 none
7
has 6
```

### Dónde se sabe que no es `null`

El compilador sigue las condiciones, y una variable local o un parámetro opcional se usa como si no lo
fuera donde ya se comprobó:

- dentro de `if (x != null) { ... }`, y en el `else` de `if (x == null) { ... } else { ... }`;
- después de `if (x == null) { return ...; }` (o `throw`, `break`, `continue`): en el resto del bloque;
- a la derecha de `x != null && ...`, y de `x == null || ...`; y con varias: `a != null && b != null`;
- dentro de `while (x != null) { ... }`;
- en cada lado de `c ? a : b`, según la condición.

Termina donde la variable se vuelve a asignar: en `current = current.next;` el lado derecho todavía
sabe que `current` no es `null`, pero lo que sigue ya no. Los campos (`n.next`) no se estrechan, porque
otra función o un hilo podría cambiarlos entre la comprobación y el uso: guárdalos antes en una
variable local. Un `!` que ya no hace falta está permitido y no hace nada.

---

## 15. Arreglos y listas

Hay tres formas de agrupar elementos del mismo tipo:

| Tipo | Qué es | Dónde vive |
|---|---|---|
| `T[N]` | hasta N elementos; capacidad fija, longitud variable | con la variable, como un struct |
| `T[]` | en un parámetro: cualquier arreglo, prestado | donde esté el original |
| `T[*]` | lista que crece | en una memoria |

### `T[N]`

```ts
function main(): int32 {
    let xs: int32[8] = [5, 3, 8];         // capacidad 8, longitud 3
    let ok: bool = xs.push(1);            // true: cabía
    println("${xs.length} ${xs[0]} ${ok}");
    xs[0] = 50;
    let inferred: int32[] = [1, 2, 3];    // capacidad tomada del literal: 3
    println("${inferred.push(4)}");       // false: está lleno
    return 0;
}
```

Salida:
```
4 5 true
false
```

- `[]` en una variable significa "la capacidad sale del valor".
- `push` devuelve `false` si no cabe; nunca escribe fuera del arreglo.
- Un `T[N]` se puede asignar a un `T[M]` si `N <= M` (se copian los elementos).
- Es un valor: asignarlo lo copia.

### `T[]` en parámetros

Un parámetro `T[]` acepta cualquier arreglo o lista de `T`, sin copiarlo. Se pueden leer y cambiar
sus elementos, pero no añadir:

```ts
function sum(xs: int32[]): int32 {
    let total: int32 = 0;
    for (x in xs) { total += x; }
    return total;
}
```

### `T[*]`

```ts
let numbers: int32[*] = [];
for (i in 0..1000) { numbers.push(i); }
```

Crece dentro de su memoria. Si la memoria es de tamaño fijo y se llena, `push` devuelve `false`.

### Operaciones

| Operación | `T[N]` | `T[]` | `T[*]` |
|---|---|---|---|
| `.length`, `x[i]`, `x[i] = v`, `for` | sí | sí | sí |
| `.push(v)` → `bool`, `.clear()` | sí | no | sí |
| `.pop()` → el último (y lo quita) | sí | no | sí |
| `.contains(v)` → `bool` (compara con `==`) | sí | sí | sí |
| `.filter(f)`, `.map(f)` | dan `T[N]` | dan `T[*]` | dan `T[*]` |
| `.sort()`, `.sort(compare)` (en su lugar) | sí | sí | sí |
| `.join(sep)` (listas de `String`) | sí | sí | sí |
| `.clone()` | sí | no | sí |

Un índice fuera de rango, o `pop()` en una lista vacía, detiene el programa con un mensaje
([sección 20](#20-fallos-en-tiempo-de-ejecución)).

`map` necesita saber el tipo del resultado, así que se usa donde haya un tipo declarado:

```ts
function main(): int32 {
    let numbers: int32[*] = [3, 8, 15, 4];
    let even: int32[*] = numbers.filter((n) -> { return n % 2 == 0; });
    let labels: String[*] = even.map((n) -> { return "#${n}"; });
    for (i, t in labels) { println("${i}: ${t}"); }
    return 0;
}
```

Salida:
```
0: #8
1: #4
```

El resultado de `filter` y `map` sobre una lista se crea en la misma memoria que la lista, salvo que
digas otra con `in`.

### Ordenar: `sort`

`sort()` ordena números y `String` en su orden natural (los textos byte a byte). Para otros elementos,
o para otro orden, `sort` recibe un comparador: una función `(a, b) -> int32` que da un número negativo
si `a` va antes, cero si son iguales y positivo si va después, como `Comparator` en Java. Ordena la lista
en su lugar y es estable: de dos elementos iguales, el que iba primero sigue primero.

```ts
class User {
    let name: String;
    let age: int32;
}

function main(): int32 {
    let words: String[*] = ["luis", "ana", "eva"];
    words.sort();                                     // ana eva luis

    let users: User[*] = [User { name: "Eva", age: 30 }, User { name: "Ana", age: 25 }];
    let byName: (User, User) -> int32 = (a: User, b: User) -> { return a.name.compareTo(b.name); };
    users.sort(byName);                               // guardado en una variable, se reutiliza
    users.sort((a: User, b: User) -> { return b.age - a.age; });          // de mayor a menor
    println("${words.join(" ")} | ${users[0].name}");
    return 0;
}
```

Salida: `ana eva luis | Eva`

Para varios criterios, el comparador los encadena:
`a.age != b.age ? a.age - b.age : a.name.compareTo(b.name)`. Sin comparador, una lista de objetos es un
error: `User has no natural order: give sort() a comparator ...`.

---

## 16. Memoria

Mientras se ejecuta, un programa guarda sus datos (textos, listas, objetos) en la memoria de la
computadora (la RAM). Cuando un dato ya no hace falta, hay que devolver su espacio, o el programa
crecería hasta llenar la memoria. Los lenguajes lo resuelven de tres formas:

- En **C**, el programador libera cada cosa a mano. Es rápido, pero un error (liberar antes de tiempo,
  o nunca) rompe el programa.
- En **Java, Go, Python o JavaScript**, un **recolector de basura** busca de vez en cuando los datos que
  ya no se usan y los libera. Es cómodo, pero gasta memoria y hace pequeñas pausas.
- **Larimar** no hace ninguna de las dos: agrupa los datos en **memorias**, y una memoria se libera
  entera, de golpe, en un momento que se ve en el código (normalmente, cuando termina el bloque `{ }`
  donde se crearon los datos). El compilador decide dónde va cada cosa, y comprueba que nada se use
  después de liberada su memoria ([capítulo 17](#17-la-regla-de-vida-y-clone)).

Larimar **no tiene recolector de basura**, y casi nunca hay que pensar en la memoria: el compilador la
organiza en **memorias** que se liberan enteras, en momentos que se ven en el código.

> Todo lo que necesita memoria vive en una memoria, y todo lo de una memoria se libera junto.

### Qué necesita memoria

Los números, `bool`, structs, enums y `T[N]` **no** la necesitan: viven con su variable.
Sí la necesitan los objetos de clase, las listas `T[*]`, los textos interpolados, las tablas `Any` y los
literales de interfaz.

### Memorias automáticas

Sin escribir nada, cada cosa vive donde le corresponde:

| Lo que se crea | Dónde vive | Se libera |
|---|---|---|
| lo que no se guarda en ningún sitio: argumentos, partes de una expresión, el texto de un `println` | la memoria temporal de la instrucción | al terminar la instrucción (en el `;`) |
| el valor de una variable local (`let`, o al asignarla) | la memoria de su bloque | al cerrar el bloque (`}`); en un bucle, en cada vuelta |
| lo que se añade a una lista, o se pone en un campo o en una tabla | la memoria de la lista, del objeto o de la tabla | con ella |
| lo que devuelve una función | la memoria que dice quien llama | depende de quien llama |
| el valor inicial de una variable global | la memoria por defecto | nunca |

```ts
class Order { let customer: String; let total: int32 = 0; }

function createOrder(customer: String, n: int32): Order {
    return Order { customer: "${customer} #${n}", total: n * 10 };   // donde diga quien llama
}

function main(): int32 {
    let orders: Order[*] = [];                     // en la memoria del bloque de main
    for (i in 0..3) {
        let o: Order = createOrder("Ana", i);      // en la memoria de la vuelta: se libera en cada vuelta
        println("${o.customer}: ${o.total}");      // el texto es un temporal de esta instrucción
        orders.push(createOrder("Luis", i));       // en la memoria de la lista
    }
    println("${orders.length} orders");
    return 0;
}
```

Salida:
```
Ana #0: 0
Ana #1: 10
Ana #2: 20
3 orders
```

Un programa que corre mucho tiempo (un servidor, un bucle que procesa archivos) no acumula nada: lo de
cada vuelta se libera en cada vuelta.

### Lo que devuelve una función

Una función que devuelve algo **creado por ella** lo crea directamente en la memoria de quien llama, sin
copiarlo. Quien llama decide dónde, casi siempre sin escribirlo: `let` lo pone en su bloque, `push` en
la lista, una asignación a un campo en el objeto, un `return` en la memoria de *su* llamada. Para decirlo
explícitamente, la llamada lleva `in`, como cualquier otro valor:

```ts
let report: String = summary(data);
```

- Las variables que la función devuelve también se crean en la memoria de quien llama:

```ts
function parts(text: String): String[*] {
    let out: String[*] = [];          // se devuelve: vive donde diga quien llama
    for (p in text.split(",")) { out.push(p.trim()); }
    return out;
}
```

- Si la función devuelve algo **que ya existía** (un elemento de una lista, un campo, un parámetro o
  una parte de él), no crea nada: el resultado sigue viviendo donde estaba. Un `find(name)` que busca
  en una lista global devuelve un objeto que vive todo el programa.
- Los argumentos que solo se usan durante la llamada son temporales de la instrucción. Los que pueden
  acabar en el resultado (como el texto que `trim()` recorta) se crean donde va el resultado.

### La memoria por defecto: `in default`

Hay una memoria que vive todo el programa: la **memoria por defecto**. Nada termina ahí sin que se vea
en el código: se usa solo cuando se pide con `in default`.

- Los valores iniciales de las variables globales se crean ahí solos.
- Darle a una global un valor **nuevo** lo pide: `config = load(path) in default;`. Si falta, el error
  lo dice: `This value lives in the memory of this block, but 'config' lives for the whole program: create it with 'in default'.`
- Un parámetro `p: T in default` (ver [sección 17](#17-la-regla-de-vida-y-clone)) recibe su argumento
  creado ahí, sin escribir nada más en la llamada.

### Memorias propias

Cuando conviene decidirlo uno mismo (soltar algo grande antes, agrupar lo de una tarea), se crean
memorias. Una memoria es un bloque de bytes, `byte[...]`:

```ts
let a: byte[4096] = [];             // 4 KB en el stack (o estática, si es global)
let b: byte[1024] = [] in heap;     // un bloque pedido al sistema
let c: byte[*] = [] in heap;        // crece pidiendo más bloques al sistema
```

- **`in heap`** pide la memoria al sistema operativo. Con `byte[N]`, el tamaño puede depender de una variable.
- Sin `in heap`, el bloque está en el stack (dentro de una función) o es memoria estática (si es global).
  Una memoria local sin heap está limitada a 64 KB.
- `byte[*]` (que crece) siempre necesita `in heap`.

Y se usan con `in`:

```ts
let text: String = "hello ${name}" in c;
let pet: Animal = Animal { name: "Kitty" } in c;
let numbers: int32[*] = [] in c;
let order: Order = createOrder("Ana", 3) in c;    // el resultado de una llamada, también
let short: String = "id ${n}" in byte[64];        // un búfer temporal del bloque actual
```

| Dónde | Cuánto vive |
|---|---|
| sin `in` | donde corresponde (ver [Memorias automáticas](#memorias-automáticas)) |
| `in m`, con `m` local | hasta el final del bloque donde se declaró `m` |
| `in m`, con `m` global | todo el programa |
| `in byte[N]` | hasta el final del bloque actual; un texto que no cabe se corta |
| `in default` | todo el programa |

Además:
- Un bloque `{ ... }` dentro de una función tiene su propia memoria: lo creado en él se libera al cerrarlo.
- Una memoria se libera **en todas las salidas** de su bloque: al terminar, con `return`,
  `break`, `continue` o cuando sale un error.
- Las memorias se consultan con `m.length` (bytes usados), `m.capacity` y `m.peak` (máximo usado).
- Una función también puede recibir una memoria como parámetro (`m: byte[*]`) y crear ahí. Rara vez
  hace falta: basta con que quien llama escriba `f(x) in m`.

### Memorias que viven mucho: `Memory.limit` y `Memory.compact`

Una memoria libera todo de golpe cuando termina su bloque. Una memoria que vive horas y cambia todo el
tiempo (el mundo de un juego, el caché de un algoritmo largo) también guarda los bytes de lo que descartó.
`std.memory` tiene dos funciones para eso:

```ts
import std.memory as Memory;

function jugar(): void {
    let mundo: byte[*] = [] in heap;
    Memory.limit(mundo, 256 * 1024 * 1024);      // más de 256 MB: un panic que nombra 'mundo'
    let mapa: Any = {} in mundo;
    let rutas: Ruta[*] = [] in mundo;
    let vivo: int64 = 0;
    while (corriendo) {
        actualizar(mapa, rutas);
        if (mundo.length > 2 * vivo + 1024 * 1024) {    // duplicó lo que estaba vivo la última vez
            Memory.compact(mundo);                       // se copia lo que alcanzan mapa y rutas; lo demás se libera
            vivo = mundo.length;                         // justo después de compact(): exactamente lo vivo
        }
    }
}
```

- `Memory.compact(m)` copia a bloques nuevos lo que las variables de `m` todavía alcanzan dentro de `m`,
  les da las copias a las variables (lo compartido sigue compartido, los ciclos siguen siendo ciclos) y
  libera los bloques viejos. Lo que vive en otras memorias se queda donde está.
- Una memoria no puede saber sola cuánto de `m.length` sigue vivo; justo después de un `compact()`, sí.
  Compactar cuando eso se duplica reparte el costo entre todo lo creado entre medio.
- El compilador revisa cada llamada: `m` crece (`byte[*] in heap`) y está declarada en una función
  (`main`, o la que hace el trabajo); toda variable de su bloque que pueda apuntar dentro vive en ella;
  nada de la memoria propia del bloque se guarda en ella; la llamada no está dentro de un `for` sobre
  datos; y lo que mueve no tiene lambdas, hilos ni objetos sincronizados. Cada error nombra la variable y
  cómo arreglarlo.
- Una memoria pertenece a un solo hilo, así que nadie más la usa mientras se mueve.

### Cuándo usar cada una

- **Casi siempre**: ninguna; las memorias automáticas ya liberan cada cosa cuando deja de usarse.
- **Datos de todo el programa** (configuración, cachés): `in default`, o una memoria global.
- **Controlar cuándo se libera algo grande**: una memoria propia `in heap`, o un bloque `{ }`.
- **Valores pequeños y de corta vida**: un búfer `in byte[N]`.

### Restricciones

- Una memoria no es un valor: no se asigna, no se devuelve y no se guarda en campos.
  Se usa después de `in`, se pasa a parámetros y se consulta.
- Un `byte[N]` que se usa como memoria no se puede usar a la vez como bytes de datos.
- Las lambdas solo pueden usar memorias globales o creadas dentro de ellas.

---

## 17. La regla de vida y `clone()`

Si un valor vivía en una memoria que se libera, y algo lo siguiera usando, el programa leería basura
o se caería: en C es uno de los errores más comunes y peligrosos. En Larimar no puede pasar, porque el
compilador lo comprueba antes de que el programa exista.

El compilador garantiza que **nada apunte a memoria ya liberada**, con una regla:

> Un valor no puede guardarse en un sitio que vive más que la memoria donde se creó.

Por ejemplo:

```ts
class Card { let name: String = ""; }

function rename(c: Card): void {
    let draft: byte[*] = [] in heap;
    let fresh: String = "temporary ${1}" in draft;
    c.name = fresh;          // ERROR: 'draft' se libera al salir y c.name quedaría apuntando ahí
}
```

El error dice:

```
'fresh' lives in memory 'draft', but field 'name' lives longer (in 'c' (owned by the caller)). Keep a copy there: fresh.clone()
```

Y la solución es la que sugiere: **`clone()`**, que copia el valor en el lugar del destino.

```ts
c.name = fresh.clone();      // bien: se copia a la memoria de c
```

### `clone()`

- Crea una **copia completa e independiente**: un objeto con todo lo que contiene, una lista con sus
  elementos, un texto. Si hay ciclos entre objetos, la copia los respeta.
- La copia va al lugar del destino (la memoria de un objeto, de una lista, del bloque) o a donde digas
  con `in`: `let p: Person = ana.clone() in otherMemory;`.
- Existe para todos los tipos. En los que no tienen memoria (números, structs simples) es igual que asignar.
- No está disponible para interfaces, lambdas ni parámetros `T[]`.

### Dónde aplica la regla

- Al asignar una variable, un campo o un elemento.
- Al crear un objeto o una lista: sus campos y elementos deben vivir al menos tanto como él.
- Al devolver: el valor no puede venir de una memoria de la función (un `in m` con `m` local, un búfer
  `byte[N]`). Lo que se crea en el `return`, o en una variable que se devuelve, vive donde diga quien
  llama, así que no hay nada que comprobar.
- Al guardar en una variable global: solo valores que viven todo el programa (créalos con `in default`).
- Un parámetro que recibe datos del que llama no se puede guardar en otro objeto que también viene
  del que llama sin `clone()`, porque el compilador no sabe cuál de los dos vive más. Es el caso típico:

```ts
class Contact {
    let name: String = "";
    function setName(n: String): void {
        self.name = n.clone();       // sin clone() es un error
    }
}
```

- Para las variables que se reasignan, el compilador considera todos los valores que reciben
  (también en bucles). Este patrón es válido:

```ts
let last: Animal? = null;
for (a in animals) { last = a; }
```

### Decir dónde vive un parámetro: `in`

Cuando una función **sí** debe guardar un parámetro en otro (construir un árbol, llenar una tabla),
el parámetro puede decir dónde viven sus datos, igual que `in` dice dónde se crea algo:

| Parámetro | Significa | Quien llama debe pasar |
|---|---|---|
| `k: Node in p` | vive tanto como el parámetro `p` | algo que viva al menos tanto como lo que pasa en `p` |
| `s: String in default` | vive todo el programa | lo que se crea en la llamada va ahí solo; si ya existía, algo global, literal o `in default` |
| `x: Item in self` | (en un método) vive tanto como el objeto | algo que viva tanto como el objeto |
| `t: String in m` | vive en la memoria `m` (un parámetro `byte[*]`) | algo que viva tanto como esa memoria |

Dentro de la función, ese parámetro se puede guardar ahí sin `clone()`. El compilador lo comprueba
en cada llamada:

```ts
class Node {
    let name: String;
    let kids: Node[*] = [];
}

let names: String[*] = [] in default;

function addKid(parent: Node, kid: Node in parent): void {
    parent.kids.push(kid);                 // bien: kid vive tanto como parent
}

function remember(name: String in default): void {
    names.push(name);                      // bien: name vive todo el programa
}

function main(): int32 {
    let memory: byte[*] = [] in heap;
    let root: Node = Node { name: "root" } in memory;
    addKid(root, Node { name: "a" } in memory);
    addKid(root, Node { name: "b" } in memory);
    remember("first");
    println("${root.kids.length} ${root.kids[1].name} ${names.length}");
    return 0;
}
```

Salida: `2 b 1`

Si en la llamada el valor vive menos (por ejemplo, un nodo creado en una memoria `scratch` de un
bucle, que se libera en cada vuelta), el error lo dice:
`Argument 2 of 'addKid' ('kid: Node in parent') must live as long as argument 1 (memory 'memory'), but it lives in memory 'scratch'.`
Y cuando falta el `in`, el mensaje de error lo sugiere: `... or declare the parameter as 'kid: Node in parent'`.

- `in` solo tiene sentido en parámetros que apuntan a memoria (objetos, listas, textos).
- Un método que redefine a otro (`override`) o implementa una interfaz debe repetir los mismos `in`.
- Las funciones `native` no lo usan, salvo `in default` en un callback que C guarda ([capítulo 23](#callbacks-con-contexto-context)).

---

## 18. Lambdas y closures

Una lambda es una función sin nombre que se guarda en una variable o se pasa como argumento.
Su tipo se escribe con los parámetros y el resultado:

```ts
let double: (int32) -> int32 = (x) -> { return x * 2; };
let add: (int32, int32) -> int32 = (a: int32, b: int32) -> { return a + b; };
let warn: () -> void = () -> { println("warning"); };
```

El tipo de los parámetros se puede omitir cuando se deduce del contexto.

### Capturas

Una lambda puede usar variables de alrededor. Las **copia** en el momento de crearse
(los objetos se copian como referencia: la lambda ve el mismo objeto).

```ts
function makeAdder(base: int32): (int32) -> int32 {
    return (x) -> { return x + base; };
}

class Counter {
    let value: int32 = 0;
    function incrementer(): () -> int32 {
        return () -> { self.value += 1; return self.value; };
    }
}

function main(): int32 {
    let plus10: (int32) -> int32 = makeAdder(10);
    println("${plus10(5)}");

    let c: Counter = Counter {};
    let inc: () -> int32 = c.incrementer();
    inc();
    inc();
    println("${inc()} ${c.value}");
    return 0;
}
```

Salida:
```
15
3 3
```

**Regla:** una variable capturada **no se puede reasignar ni modificar**, ni antes ni después de la
lambda, ni dentro de ella. Así la copia nunca queda desactualizada:

```ts
let x: int32 = 5;
let f: () -> int32 = () -> { return x; };
x = 10;     // error: 'x' está capturada
```

Lo mismo para cambiar un campo de un struct capturado o añadir a un `T[N]` capturado. Los objetos de
clase y las listas `T[*]` sí se pueden modificar, porque la lambda comparte la misma referencia.

### Otras reglas

- Una lambda puede devolverse o guardarse en campos sin problema: lleva consigo sus copias. Lo que
  captura debe vivir tanto como el sitio donde se guarda la lambda: para guardar una lambda en una lista
  global, clona lo que captura **antes** de crearla (`let kept: String = label.clone() in default;`, y
  captura `kept`). Un `label.clone()` dentro de la lambda solo se ejecuta cuando la llaman: para entonces
  puede que `label` ya no exista, y el compilador lo dice.
- En métodos de clase, una lambda puede usar `self`. En métodos de struct no, porque el struct podría copiarse o desaparecer.
- Las lambdas no pueden lanzar errores.
- Una lambda no puede capturar otra lambda **de su mismo tipo** (el compilador lo detecta).

### Referencias a funciones: `::`

`::` pasa una función donde se espera un tipo función, sin escribir la lambda:

```ts
app.get("/casas/{id}", Casas::ver);         // una función de un módulo importado
app.get("/", ::inicio);                     // una función de este módulo
let sumar: (int32) -> void = contador::add; // un método de un objeto (captura 'contador')
return self::refrescar;                     // un método de self
```

`Casas::ver` es la lambda `(ctx) -> { Casas.ver(ctx); }`, con los parámetros del tipo que se espera ahí.
Una referencia a un método captura su objeto como cualquier lambda, con las mismas reglas. Antes de `::`
va un módulo, una variable o `self`; una función con `throws` no se puede referenciar (las lambdas no
lanzan errores).

---

## 19. Errores: `throw`, `try` y `catch`

Algunas operaciones pueden fallar por razones que el programa no controla: un archivo que no existe,
una conexión que se corta. Una función que puede fallar lo dice en su declaración con `throws`, y quien
la llama tiene que atender el fallo (con `try` y `catch`) o pasarlo hacia arriba. El compilador
comprueba que ningún fallo se olvide.

Los errores esperables (un archivo que no existe, una lectura inválida) se representan con enums ([capítulo 12](#12-enums)):

```ts
enum FileError {
    NotFound,
    Denied(user: String),
    Full(bytes: int64)
}

function open(path: String): int32 throws FileError {
    if (path == "") { throw FileError.NotFound; }
    if (path == "secret") { throw FileError.Denied { user: "ana" }; }
    return path.length;
}

function readBoth(a: String, b: String): int32 throws FileError {
    return open(a) + open(b);        // si open falla, el error sigue subiendo
}

function main(): int32 {
    let attempts: String[] = ["hello", "", "secret"];
    for (p in attempts) {
        try {
            println("read ${readBoth("data", p)}");
        } catch (FileError e) {
            switch (e) {
                case NotFound -> println("not found");
                case Denied { user } -> println("denied for ${user}");
                case Full { bytes } -> println("full: ${bytes}");
            }
        }
    }
    return 0;
}
```

Salida:
```
read 9
not found
denied for ana
```

Las reglas:
- **`throws E`** declara el enum que la función puede lanzar (uno por función).
- Cada llamada a una función que puede fallar debe estar dentro de un `try` que capture ese tipo,
  o en una función que declare el mismo `throws` (entonces el error sube solo).
  Si no, es un error de compilación.
- Un `try` puede tener varios `catch`, uno por tipo de error. Lo que no se captura sigue subiendo.
- Los métodos de clases e interfaces también pueden declarar `throws`; un `override` debe declarar el mismo.
- Los datos que viajan en un error deben vivir todo el programa: usa literales o `.clone()`.
- Si `main` declara `throws` y un error llega hasta ella, el programa termina con código 1 y el mensaje
  `uncaught error: FileError.NotFound`.

Por dentro, un error es un valor que se devuelve: no hay saltos ocultos, y las memorias locales se liberan
mientras el error sube.

---

## 20. Fallos en tiempo de ejecución

Algunos fallos no se pueden prever al compilar. En lugar de corromper la memoria, el programa se
detiene con un mensaje que dice el archivo y la línea, y el código de salida **101**:

| Causa | Mensaje |
|---|---|
| índice fuera de rango | `panic [src/main.lar:4]: index 5 out of range (length 3)` |
| división por cero | `panic [src/main.lar:4]: division by zero` |
| `!` sobre `null` | `panic [src/main.lar:4]: '!' used on a null value` |
| una memoria de tamaño fijo se llena al crear algo | `panic [src/main.lar:4]: memory is full` |
| el sistema no da más memoria | `panic: out of memory: ...` |

Estos fallos no se capturan con `catch`: indican un error del programa, no una situación esperada.

El programa también puede detenerse así a propósito, con **`panic("mensaje")`**, cuando encuentra algo que
no debería pasar nunca:

```ts
function name(n: int32): String {
    if (n == 1) { return "uno"; }
    panic("no sé decir ${n}");
}
```

Salida, si se llama con 7: `panic [src/main.lar:3]: no sé decir 7`, con código de salida 101.

- `panic` recibe un `String` (puede ser un texto interpolado).
- Una función puede terminar con `panic(...)` en lugar de `return`: el compilador sabe que no sigue.
- Es para errores del programa. Lo que se espera que pueda fallar (un archivo que no existe, un dato mal
  escrito) se avisa con `throw`, que quien llama puede capturar.

---

## 21. `Any`: datos de forma libre

Los structs y las clases sirven para datos cuya forma conoces de antemano. Para datos cuya forma no
conoces (configuración, mensajes, JSON) está **`Any`**: un valor que puede ser un número, un `bool`, un
`String`, `null`, un objeto, un struct, un enum o una **tabla**. Una tabla tiene, como en Lua, dos partes: una **por posición**
(0, 1, 2…) y otra **por nombre**.

```ts
function main(): int32 {
    let config: Any = {
        "web", "api",                  // posiciones 0 y 1
        name: "server",                // por nombre
        port: 8080,
        limits: { max: 100, ratio: 0.75 },
    };

    println("${config[0]} ${config.name} ${config.limits.max}");
    config.port = 9090;                // cambiar una entrada
    config["debug"] = true;            // añadir una entrada (también con un String calculado)
    config.push("admin");              // añadir al final de la parte por posición
    println("${config}");
    return 0;
}
```

Salida:
```
web server 100
{"web", "api", "admin", name: "server", port: 9090, limits: {max: 100, ratio: 0.75}, debug: true}
```

- **Una tabla vive en una memoria**, como un objeto: la de su variable, o la que digas con `in`.
  Las tablas dentro de otra, y las que se asignan o añaden a una tabla, viven en la memoria de esa tabla.
- **Los valores llevan su tipo.** Un entero sin tipo se guarda como `int64` y un decimal como `float64`;
  para otro tipo, dilo: `0xFF as byte`, `1.5 as float32`.
- Una tabla guarda números, `bool`, `String`, `null`, otras tablas, objetos, structs y enums
  (ver más abajo). Listas `[*]`, lambdas e interfaces no: para eso están los campos con su tipo.
- **Leer nunca falla**: una entrada que no existe, o leer dentro de algo que no es una tabla, da `null`.
  Por eso `config.server.port` funciona aunque falte `server`. Escribir en algo que no es una tabla, en
  cambio, detiene el programa.
- Las entradas por nombre se recorren en el orden en que se añadieron.
- `a.length` es el tamaño de la parte por posición. Para una entrada llamada `length`, `push` o `fields`,
  usa corchetes: `a["length"]`.

### Leer un valor: `as`

Como el tipo de lo que hay dentro no se conoce al compilar, leer un valor con un tipo da un **opcional**:
el valor si lo hay y es de ese tipo, o `null`. Se combina con `??`:

```ts
function main(): int32 {
    let config: Any = { port: 8080, ratio: 0.75, name: "web" };
    let port: int32 = config.port as int32 ?? 80;         // 8080: un entero que cabe se convierte
    let small: byte = config.port as byte ?? 0;           // 0: 8080 no cabe en un byte
    let ratio: float64 = config.ratio as float64 ?? 1.0;
    let timeout: int32 = config.server.timeout as int32 ?? 30;   // no existe: 30
    let name: String = config.name as String ?? "?";
    println("${port} ${small} ${ratio} ${timeout} ${name} ${config.missing == null}");
    return 0;
}
```

Salida: `8080 0 0.75 30 web true`

Los enteros se convierten a cualquier tipo entero en el que quepan, y los números a decimal. `as`
también sirve con clases, structs y enums: `v as Dog` da un `Dog?`.

### Recorrer y distinguir

`for (i, v in table)` recorre la parte por posición y `for (name, v in table.fields)` la parte por nombre.
Para saber qué hay en cada valor se usa un `switch` con el tipo; `case Any t` es una tabla:

```ts
function describe(v: Any): String {
    return switch (v) {
        case int64 n when n > 1000 -> "big number ${n}";
        case int64 n -> "number ${n}";
        case float64 f -> "decimal ${f}";
        case String s -> "text '${s}'";
        case Any t -> "table of ${t.length}";
        case null -> "nothing";
        default -> "something else";
    };
}

function main(): int32 {
    let packet: Any = { 3, 2.5, "three", { 1, 2 }, name: "sensor", port: 8080 };
    for (i, v in packet) { println("${i}: ${describe(v)}"); }
    for (name, v in packet.fields) { println("${name}: ${describe(v)}"); }
    return 0;
}
```

Salida:
```
0: number 3
1: decimal 2.5
2: text 'three'
3: table of 2
name: text 'sensor'
port: big number 8080
```

- El `switch` sobre un `Any` compara el tipo exacto: `8080` está guardado como `int64`, así que
  `case int32` no lo cubre. Usado como expresión, necesita `default`.
- Mientras se recorre una tabla se pueden cambiar sus valores, pero no añadir ni quitar entradas: si
  pasa, el programa se detiene con un mensaje.
- `clone()` copia una tabla con todo lo que contiene, también si se contiene a sí misma.

### Objetos, structs y enums

Un `Any` también guarda objetos, structs y enums, y se recuperan con su tipo:

- **un objeto se guarda por referencia**: la tabla y la variable apuntan al mismo objeto;
- **un struct o un enum se guarda copiado** en la memoria de la tabla. Fuera de una tabla, se dice dónde
  va la copia a la memoria de la variable (o donde digas con `in`): `let v: Any = point;`.

```ts
struct Point { let x: int32; let y: int32; }
class Animal { let name: String; }
class Dog extends Animal { let breed: String = "mixed"; }

function main(): int32 {
    let rex: Dog = { name: "Rex", breed: "shepherd" };
    let p: Point = { x: 1, y: 2 };
    let things: Any = { 42, p, rex, null };

    for (v in things) {
        let text: String = switch (v) {
            case int64 n -> "number ${n}";
            case Point q -> "point ${q.x},${q.y}";
            case Animal a -> "animal ${a.name}";      // un Dog también es un Animal
            case null -> "null";
            default -> "other";
        };
        println(text);
    }
    let dog: Dog? = things[2] as Dog;
    println("${things} ${dog != null}");
    return 0;
}
```

Salida:
```
number 42
point 1,2
animal Rex
null
{42, <Point>, <Dog>, null} true
```

Al imprimir, un objeto o un struct se muestra con el nombre de su tipo. `clone()` de una tabla copia
también los objetos que contiene, salvo los de clases `synchronized` y los `Thread`, que se comparten.

### Buscar

| Método | Qué hace |
|---|---|
| `t.contains(x)` | `true` si `x` es el nombre de una entrada, o es igual a un elemento por posición |
| `t.containsKey("name")` | `true` si hay una entrada con ese nombre |

`contains` busca números (por valor: `5` es igual a `5.0`), `bool`, `String`, objetos (el mismo objeto) y
`null`. No mira los valores de las entradas con nombre: esos se recorren con `fields`. Usado con nombres,
un `Any` es un conjunto:

```ts
function main(): int32 {
    let seen: Any = {};
    let words: String[] = ["x", "y", "x"];
    for (w in words) {
        if (seen.contains(w)) { println("again: ${w}"); }
        seen[w] = true;
    }
    return 0;
}
```

Salida: `again: x`

### Quitar entradas

| Método | Qué hace |
|---|---|
| `t.remove("name")` | quita una entrada por nombre; da `true` si existía |
| `t.removeAt(i)` | quita una posición; las siguientes se corren hacia atrás |
| `t.clear()` | vacía la tabla |
| `t.removeIf((v) -> ...)` | quita, de las dos partes, los valores para los que la lambda da `true`; devuelve cuántos |
| `t.removeIf((name, v) -> ...)` | lo mismo con la parte por nombre, recibiendo también el nombre |

```ts
function main(): int32 {
    let config: Any = { 1, null, 3, name: "x", debug: null, port: 80 };
    config.remove("name");
    config.removeAt(0);
    let removed: int32 = config.removeIf((v) -> { return v == null; });
    println("${removed} ${config}");
    return 0;
}
```

Salida: `2 {3, port: 80}`

Quitar entradas mientras se recorre la misma tabla detiene el programa, igual que añadirlas: el recorrido
se saltaría entradas. Para quitar varias, `removeIf` lo hace de una vez. Quitar no libera memoria: lo que
vive en una memoria se libera junto, cuando se libera la memoria.

---

## 22. Hilos

Un hilo ejecuta código al mismo tiempo que el resto del programa. En Larimar, un **`Thread`** es un
objeto que vive en una memoria, y lo que ejecuta (su `run`) es una lambda escrita ahí mismo:

```ts
let worker: Thread = { run: () -> { println("working"); } };
worker.start();       // empieza a correr
worker.join();        // espera a que termine
```

- **Cuando se libera la memoria de un hilo, primero se espera a que termine.** Así un hilo nunca vive
  más que su memoria, y todo lo que usa sigue existiendo mientras corre. Los hilos en la memoria por
  defecto se esperan al terminar el programa.
- `start()` arranca el hilo (una sola vez) y `join()` espera a que termine.

### Compartir datos: `synchronized class`

Dos hilos que cambian lo mismo a la vez corrompen los datos. Por eso un hilo **solo puede usar** de
fuera dos clases de cosas, y el compilador lo comprueba:

1. **Valores**, que el hilo recibe copiados: números, `bool`, `String`, y structs, enums y `T[N]` hechos de eso.
2. **Objetos de una `synchronized class`**, y **objetos de una clase sin campos**: como no tienen nada
   que pueda cambiar, varios hilos pueden usarlos a la vez (un conjunto de rutas, una forma de hacer algo).

```ts
class Pages {                                     // sin campos: se puede compartir
    function routes(r: Router in self): void {
        r.get("/", self::index);                  // donde se espera una función 'thread safe': bien
    }
    function index(req: Request, res: Response): void { ... }
}
```

Si la clase, o una clase que la extiende, tiene un campo, no se puede compartir, y el error lo nombra:
`'self::index' is given where a 'thread safe' function is expected, but it keeps self (Pages), which has fields ('visits') that other threads could change at the same time.`

Una clase `synchronized` protege sus datos con un candado. Cada método lo toma al empezar y lo suelta al
salir, por cualquier camino, así que dos hilos nunca están dentro del mismo objeto a la vez:

```ts
synchronized class Counter {
    let total: int64 = 0;
    function add(n: int64): void { self.total += n; }
    function get(): int64 { return self.total; }
}

function main(): int32 {
    let shared: byte[*] = [] in heap;
    let counter: Counter = {} in shared;
    {
        let workers: byte[*] = [] in heap;     // los hilos viven aquí (en la memoria de la vuelta,
                                               // se esperaría a cada uno al terminar su vuelta)
        for (w in 0..4) {
            let t: Thread = {
                run: () -> {
                    for (k in 0..1000) { counter.add(k as int64); }
                }
            } in workers;
            t.start();
        }
    }   // al liberarse 'workers', se espera a los 4 hilos
    println("${counter.get()}");
    return 0;
}
```

Salida: `1998000`

Los cuatro hilos corren a la vez porque su memoria está fuera del bucle. El bloque `{ }` sirve para
decir hasta dónde llegan: al cerrarlo se libera `workers` y, con ella, se espera a los hilos.

Las reglas de una clase `synchronized`:
- Sus campos solo se usan dentro de sus métodos, a través de `self`.
- Sus métodos reciben y devuelven valores u objetos `synchronized`, nunca listas, objetos normales ni `Any`:
  así sus datos no salen sin el candado.
- Solo hereda de otra clase `synchronized`, y solo una clase `synchronized` hereda de ella. El objeto
  tiene un único candado, y todos los métodos lo toman, también los heredados.
- Dentro de una lambda de sus métodos, `self` solo se usa para llamar a sus métodos (`self.run()` o
  `self::run`), que toman el candado; sus campos no, porque la lambda podría ejecutarse más tarde, sin él.
- Un método puede llamar a otro del mismo objeto: el candado se puede tomar varias veces.

```ts
synchronized class Queue {
    let items: int32[*] = [];
    function put(x: int32): void { self.items.push(x); }
    function size(): int32 { return self.items.length; }
}

synchronized class LimitedQueue extends Queue {      // el mismo candado para put, size y later
    let limit: int32 = 100;
    override function put(x: int32): void {
        if (self.size() < self.limit) { super.put(x); }
    }
    function later(): () -> void thread safe {
        return () -> { self.put(0); };                // bien: put toma el candado
    }
}
```

### Esperar a que algo ocurra: `wait until`

Un método de una clase `synchronized` puede decir **cuándo** puede ejecutarse, con `wait until
(condición)` en su firma. Quien lo llama **espera ahí** (sin gastar procesador y soltando el candado
mientras tanto) hasta que la condición se cumpla, y entonces el método corre con el candado tomado:

```ts
synchronized class Queue {
    let items: int32[64] = [];
    let closed: bool = false;

    function put(v: int32): void { self.items.push(v); }
    function close(): void { self.closed = true; }

    function take(): int32 wait until (self.items.length > 0 || self.closed) {
        if (self.items.length == 0) { return -1; }        // cerrada y vacía
        let v: int32 = self.items[0];
        let rest: int32[64] = [];
        for (i in 1..self.items.length) { rest.push(self.items[i]); }
        self.items = rest;
        return v;
    }
}

synchronized class Total {
    let sum: int64 = 0;
    function add(n: int64): void { self.sum += n; }
    function get(): int64 { return self.sum; }
}

function main(): int32 {
    let queue: Queue = {};
    let total: Total = {};
    let consumer: Thread = {
        run: () -> {
            while (true) {
                let v: int32 = queue.take();             // espera hasta que haya algo
                if (v < 0) { break; }
                total.add(v as int64);
            }
        }
    };
    consumer.start();
    for (i in 1..11) { queue.put(i); }
    queue.close();
    consumer.join();
    println("sum ${total.get()}");
    return 0;
}
```

Salida: `sum 55`

- **Se lee en la firma:** "take espera hasta que haya algo o esté cerrada". Quien lee el método sabe que
  esa llamada puede quedarse esperando.
- **Nadie avisa a mano.** Cuando termina cualquier método del objeto (`put`, `close`...), quienes
  esperan vuelven a mirar su condición. No hay `notify` que olvidar.
- **El cuerpo empieza sabiendo que la condición se cumple**, con el candado tomado: nada la cambia antes
  de la primera línea.
- **La condición puede usar los parámetros**: `function serve(ticket: int32): int32 wait until (self.now >=
  ticket)` deja pasar a cada uno en su turno.
- **Solo en métodos de una clase `synchronized`**, porque son los únicos cambios que el objeto puede ver.
- **Se escribe en dos palabras**, como `released by`: las cláusulas que describen una declaración se leen
  como frase. Las palabras clave que empiezan algo van en una sola pieza (`cinclude`, `ccode`).
- **Varias condiciones a la vez:** una cola con capacidad limitada pone `wait until (self.items.length < 4)`
  en `put` y `wait until (self.items.length > 0)` en `take`, y cada lado espera lo suyo.

### Un objeto como trabajo: `Runnable`

En lugar de una lambda, `run` puede ser un objeto `synchronized` que implemente `Runnable`
(`interface Runnable { function run(): void; }`):

```ts
synchronized class Download implements Runnable {
    let done: bool = false;
    function run(): void { self.done = true; }
    function finished(): bool { return self.done; }
}

function main(): int32 {
    let job: Download = {};
    let t: Thread = { run: job, name: "download" };
    t.start();
    t.join();
    println("${job.finished()}");
    return 0;
}
```

Salida: `true`

### Funciones para varios hilos: `thread safe`

Una función que otros hilos van a llamar, a veces varios a la vez, se marca con **`thread safe`** al final
de su tipo. La escribe quien diseña la API (un servidor, un grupo de hilos); quien la usa escribe una
lambda normal:

```ts
class Pool {
    let threads: int32 = 4;
    let work: (int32) -> void thread safe;        // los hilos del Pool la llaman a la vez
    ...
}

let total: Total = {};                             // synchronized
let names: String[*] = [];

let pool: Pool = { work: (id: int32) -> { total.add(id as int64); } };     // bien
let bad: Pool = { work: (id: int32) -> { names.push("x"); } };              // error
```

```
Semantic Error [src/main.lar:9]: This 'thread safe' lambda uses 'names' (String[*]), which other threads could change at the same time. ...
```

- **Una lambda dada donde se espera una función `thread safe` se comprueba como el `run` de un `Thread`**:
  solo usa valores, objetos de clases `synchronized` o de clases sin campos y otras funciones `thread safe`, y las funciones que
  llama no cambian globales. Sus capturas no cambian (como en toda lambda), así que varios hilos pueden
  ejecutarla a la vez.
- **Un valor `thread safe` se puede compartir entre hilos**: un `Thread` lo puede usar y un método
  `synchronized` lo puede recibir. Así se escriben en Larimar normal los servidores de `std.net`.
- **Una función `thread safe` sirve donde se espera una normal**, pero no al revés: una variable con una
  lambda normal no se puede dar donde se pide `thread safe` (solo una lambda escrita ahí, que se comprueba).
- Son dos palabras, como `wait until`, y ninguna está reservada. Con un tipo función dentro de otro, va al
  más cercano a su izquierda: en `(A) -> (B) -> C thread safe` lo es `(B) -> C`; para el de fuera,
  paréntesis: `((A) -> (B) -> C) thread safe`.

`synchronized` y `thread safe` son cosas distintas: una clase `synchronized` es un objeto con candado; una
función `thread safe` no necesita candado porque solo toca cosas que ya son seguras.

### Muchas tareas, pocos hilos: `ThreadPool`

Para un lote de tareas (las imágenes de una carpeta, los archivos por descargar) un hilo por tarea son
demasiados. **`std.thread`** tiene un pool: ejecuta las tareas en unos pocos hilos, según llegan.

```ts
import std.thread { ThreadPool };

synchronized class Total {
    let n: int64 = 0;
    function add(k: int64): void { self.n += k; }
    function get(): int64 { return self.n; }
}

function main(): int32 {
    let total: Total = {};
    let pool: ThreadPool = { threads: 8 };
    for (i in 0..1000) {
        let k: int64 = i as int64;
        pool.submit(() -> { total.add(k); });       // se ejecuta en uno de los 8 hilos
    }
    pool.wait();                                    // hasta que todas hayan terminado
    println("${total.get()}");                      // 499500
    return 0;
}
```

- Una tarea es un `() -> void thread safe`: captura solo valores y objetos sincronizados (las reglas de
  [`thread safe`](#funciones-para-varios-hilos-thread-safe)).
- Los hilos arrancan según llegan tareas, como mucho `threads`, y terminan cuando no queda ninguna; cuando
  se va la memoria del pool, se esperan. `queue: 100` acota las tareas que esperan: `submit` espera
  mientras haya esas.
- Las tareas viven en la memoria del pool hasta que el pool se va, así que un pool es para un **lote**,
  creado donde está el lote (dentro de una función, en la vuelta de un bucle). Un servidor que corre
  días no guarda un pool: sus hilos toman valores, como hace `TcpServer`.

### Lo que el compilador rechaza

```ts
let hits: int32 = 0;
class Box { let n: int32 = 0; }

function main(): int32 {
    let box: Box = {};
    let t: Thread = { run: () -> { box.n = 1; hits += 1; } };
    t.start();
    return 0;
}
```

```
Semantic Error [src/main.lar:7]: This thread uses 'box' (Box), which could change while the thread runs. A thread can share only values ...
Semantic Error [src/main.lar:7]: This thread can reach global 'hits' (src/main.lar:7), which can change while threads use it. Keep shared state in an object of a synchronized class.
```

La comprobación sigue las funciones que llama el hilo: si alguna, por profunda que esté, cambia una
variable global o usa una memoria global, el error lo dice. Las globales que nunca cambian (una
configuración, un texto) sí se pueden leer.

Entre hilos se comparte solo **la memoria por defecto**, que tiene su propio candado: crear algo
`in default` desde varios hilos es seguro. Las demás memorias son de un solo hilo.

Lo que esto **no** evita son los bloqueos mutuos: dos objetos `synchronized` que se llaman entre sí en
orden contrario pueden quedarse esperando para siempre. Ningún lenguaje con candados lo impide del todo.

Por dentro, Larimar usa los hilos del sistema: POSIX (`pthread`) en Linux y macOS, y la API de
Windows en Windows. `larimar build` añade lo necesario para compilar.

---

## 23. Llamar a C

Hay miles de bibliotecas escritas en C, para casi cualquier cosa: gráficos, sonido, bases de datos,
compresión. Larimar puede usarlas directamente. Como Larimar se convierte en C, llamar a una función
de C no cuesta nada: solo la **declaras** con `native function` (su nombre, qué recibe y qué devuelve),
y luego la usas como cualquier otra función.

```ts
cinclude "<stdio.h>";
cinclude "<math.h>";

native function printf(format: String, ...): int32;
native function sqrt(x: float64): float64;

function main(): int32 {
    printf("square root of 2 = %f\n", sqrt(2.0));
    return 0;
}
```

Salida: `square root of 2 = 1.414214`

`cinclude` trae el archivo de C que declara esas funciones (un **header**), y `native function` le
dice a Larimar cómo se llama cada una. Con `<math.h>`, en algunos sistemas hay que **enlazar** (unir
al programa cuando se construye) la biblioteca matemática: `dynamic_libraries = ["m"]` en el `larimar.toml`
de un proyecto ([capítulo 26](#26-proyectos-larimartoml-y-larimar-build)).

El camino contrario, Larimar visto desde C, es [`export function`](#que-c-llame-a-larimar-export-function),
y en grande una biblioteca entera escrita en Larimar para programas de C ([capítulo 27](#27-bibliotecas-escritas-en-larimar)).

Todo lo que viene de C se declara con **`native`**, y todas las declaraciones siguen la misma regla:
**a la izquierda va el nombre en Larimar; después del `=`, el nombre en C**. Sin `=`, se llama igual.

| Declaración | Qué es |
|---|---|
| `native function f(...): T;` | una función de C ([abajo](#23-llamar-a-c)) |
| `native type X;`, `native type X = FILE*;` | un tipo de C ([Tipos de C](#tipos-de-c-native-type)) |
| `native type X = T* { ... }` | un tipo de C con campos y métodos ([Tipos de C con miembros](#tipos-de-c-con-miembros)) |
| `native type F = (int32) -> void;` | un puntero a una función de C ([Punteros a funciones de C](#punteros-a-funciones-de-c)) |
| `native struct P { ... }` | un struct de C, por valor ([Structs de C](#structs-de-c-native-struct)) |
| `native const N: int32;`, `native let errno: int32;` | una constante, una macro o una variable de C ([Constantes y variables](#constantes-y-variables-de-c-native-const-native-let)) |

Una biblioteca propia se declara igual. Por ejemplo, para una de ventanas:

```ts
cinclude "windows_lib.h";

native type Window;                                      // un puntero opaco de C
native function create_window(title: String): Window;
native function close_window(w: Window): void;
```

- `cinclude` añade un `#include` al C generado (dentro de `#when unix` ... `#end`, solo en ese sistema:
  ver [Cada sistema lo suyo: `#when`](#cada-sistema-lo-suyo-when)).
- Los parámetros de una `native function` solo pueden ser números, `bool`, `String` (llega como
  `const char*`), `String?` (`null` llega como `NULL`), tipos `native` (también opcionales, `T?`, que en C
  son un puntero que puede ser `NULL`), structs de C y punteros de C (`T*`, ver
  [Punteros de C](#punteros-de-c-t-y-)). `...` permite argumentos variables, como en `printf`.
- Una función de C puede devolver `String?`: `NULL` llega como `null` (`getenv`).
- **Si el nombre de C es otro**, se escribe después del `=`: `native function cExit(code: int32): void = exit;`.
  Si no es un nombre simple (un cast, una macro entre paréntesis), va como **texto de C, `c"..."`**, tal
  cual en C: `= c"(fio_start)"`, `= c"(const char*)sqlite3_column_text"`. La `c` delante dice que es C, no
  un `String` de Larimar.
- Un **`T[]` de números o `bool`** (`byte[]`, `int32[]`, `float64[]`...) llega a C como **dos argumentos**:
  un puntero a los elementos y cuántos son. C puede leerlos y escribir en ellos, así que es la forma de que
  C llene un búfer de Larimar (leer de un archivo o de un socket) sin copiar nada:

  ```ts
  ccode {
      static int32_t fill(uint8_t* items, int32_t length) { /* escribe en items[0..length) */ return length; }
  }
  native function fill(buffer: byte[]): int32;      // en C: fill(uint8_t* items, int32_t length)

  let buf: byte[*] = buffer(4096);
  let n: int32 = fill(buf);                          // una lista, un T[N] o un T[] valen
  ```
- Si el archivo no tiene ningún `cinclude` ni `ccode`, el transpilador escribe él mismo el prototipo de C
  de cada `native function`. Es lo que hace falta para funciones propias escritas en un `.c` aparte (ver
  `sources` en el [apartado 26](#26-proyectos-larimartoml-y-larimar-build)). Si la función viene de una
  cabecera, incluye la cabecera.
- Una función de C que devuelve `String` debe devolver un texto terminado en cero que siga existiendo:
  uno estático, o uno creado en una memoria que recibe (ver más abajo).
- Una `native function` no tiene cuerpo: es una función de C. Para escribir una en Larimar, se escribe una
  función normal.
- En un módulo, el nombre de C no cambia: `public native function Beep(...)` en el módulo `win` se usa
  como `win.Beep(...)` y llama a `Beep` de C.

**Una macro con argumentos con nombre.** Algunas bibliotecas simulan argumentos con nombre con una macro
que arma un struct (`fio_start(.threads = 1, .workers = 2)` en facil.io). La macro esconde una función de
verdad con el mismo nombre, que recibe el struct; entre paréntesis, C llama a la función y no a la macro:

```ts
ccode {
    #include <stdio.h>
    struct sum_args { int a; int b; };
    static int sum(struct sum_args s) { return s.a + s.b; }
    #define sum(...) sum((struct sum_args){__VA_ARGS__})     /* sum(.a = 1, .b = 2) en C */
}

native struct SumArgs = c"struct sum_args" { let a: int32; let b: int32; }
native function sum(args: SumArgs): int32 = c"(sum)";       // la función, no la macro

function main(): int32 {
    println("${sum({ a: 3, b: 4 })}");                      // los campos que no se dan valen cero
    return 0;
}
```

Salida: `7`

### C en el mismo archivo: `ccode`

Casi todo lo de C se usa directamente, con declaraciones: funciones, tipos, structs, constantes,
variables, punteros y recursos (secciones siguientes). Para lo que aun así conviene escribir en C (un
algoritmo, un bloque de Apple, código entre `fork` y `exec`), se escribe en C dentro del propio archivo y
se declara con `native function`:

```ts
ccode {
    #include <ctype.h>

    static int32_t sum_digits(int64_t v) {
        int32_t s = 0;
        if (v < 0) v = -v;
        while (v > 0) { s += (int32_t)(v % 10); v /= 10; }
        return s;
    }
}

native function sum_digits(v: int64): int32;

function main(): int32 {
    println("${sum_digits(98765)}");
    return 0;
}
```

Salida: `35`

Dentro de un `ccode`, **`lar"nombre"`** es el nombre en C de una función, un tipo o una variable global
de Larimar (`lar"modulo.nombre"` para la de otro módulo). Así el C no depende de cómo nombra las cosas el
compilador:

```ts
ccode {
    static int32_t both(int32_t a) { return lar"twice"(a) + lar"area"(a, 3); }
}

function twice(x: int32): int32 { return x * 2; }
function area(w: int32, h: int32): int32 { return w * h; }
native function both(a: int32): int32;

function main(): int32 {
    println("${both(5)}");
    return 0;
}
```

Salida: `25`

- Un nombre que no existe es un error del compilador: *lar"nope" in ccode: 'nope' is not a function, type
  or global of Larimar seen here*.
- Los prototipos de las funciones nombradas así se escriben antes del `ccode` cuando sus tipos son
  números, `bool`, `String` o `void`. Una función que devuelve datos recibe además la memoria de la
  llamada (como en C las ve el [capítulo 28](#28-qué-genera-el-transpilador)); para que C llame a Larimar
  con una firma de C limpia está [`export function`](#que-c-llame-a-larimar-export-function).

En la biblioteca estándar, `native type` también declara los métodos de los tipos que el compilador
conoce, y mezcla intrínsecos, métodos escritos en Larimar y llamadas a C:

```ts
public native type String {
    native let length: int32;
    native operator [](i: int32): byte;
    native function substring(from: int32, to: int32): String in self;
    function isEmpty(): bool { return self.length == 0; }
}
```

Una función nativa de una clase delega en una expresión Larimar, que puede llamar a una función de C:

```ts
public class StringBuilder {
    let buffer: TextBuf = text_buf_new();
    native function add(text: String): void = text_buf_add(self.buffer, text);
    native function toString(): String in self = text_buf_view(self.buffer);
}
```

De los bloques `ccode` de la biblioteca estándar solo llega al C lo que se usa: cada función, tipo o
variable de C se queda si algo que el programa usa la nombra. El `ccode` del propio programa, en cambio,
se copia entero.

Así está escrito `String`: el compilador solo conoce su núcleo (`length`, `[]`, `substring`, `bytes`,
`split` y `lines`, que son vistas del texto), y todo lo demás (`indexOf`, `replace`, `toUpperCase`,
`padStart`, `toInt`, `codePoints`...) está escrito en Larimar en `std/lang.lar`, con un `ccode` pequeño
solo para lo que necesita C (`strtod`, para `toFloat`).

- El contenido se copia tal cual al C generado, después de las cabeceras y antes del programa.
- **Las puertas entre los dos lenguajes son `native` (de C a Larimar), `export function` (de Larimar a C)
  y `lar"..."` (dentro de un `ccode`)**, con sus tipos comprobados. El C no debe usar de otra forma las
  variables ni los tipos que genera Larimar, porque sus nombres pueden cambiar.
- Dentro de `ccode` no hay garantías: el C puede hacer cualquier cosa. Conviene que sea poco y simple.

### C de cada sistema: clases con C en sus métodos

Lo que cambia entre sistemas se escribe como **una interfaz y una clase por sistema**, cuyos métodos
tienen **C como cuerpo** (`ccode { ... }` en lugar del bloque de Larimar). Cada clase dice la plataforma
para la que es implementándola (`UnixPlatform`, `WindowsPlatform`...), y cuál se usa se elige con un
`switch` sobre `os.platform()`. Así lo hace la biblioteca estándar (`std.time`, `std.os`, `std.net`...):
sus módulos son solo archivos `.lar`, y nadie escribe un `#if` a mano.

```ts
import std.os;
import std.os { OS, UnixPlatform, WindowsPlatform };

interface Clock {
    function monotonic(): int64;
    function sleep(ms: int64): void;
}

class PosixClock implements Clock, UnixPlatform {
    cinclude "<time.h>";

    ccode {                                   // C que comparten sus métodos
        static int64_t ms_of(clockid_t which) {
            struct timespec t;
            clock_gettime(which, &t);
            return (int64_t)t.tv_sec * 1000 + t.tv_nsec / 1000000;
        }
    }

    function monotonic(): int64 ccode { return ms_of(CLOCK_MONOTONIC); }

    function sleep(ms: int64): void ccode {
        struct timespec t = { (time_t)(ms / 1000), (long)(ms % 1000) * 1000000L };
        nanosleep(&t, NULL);
    }
}

class WindowsClock implements Clock, WindowsPlatform {
    cinclude "<windows.h>";

    function monotonic(): int64 ccode { return (int64_t)GetTickCount64(); }

    function sleep(ms: int64): void ccode { Sleep((DWORD)ms); }
}

let clock: Clock = switch (os.platform()) {
    case Linux, MacOS, Unix -> PosixClock {};
    case Windows -> WindowsClock {};
};
```

- **Un cuerpo de C** ve los parámetros por su nombre, con su tipo de C: un `int64` es un `int64_t`, un
  `String` un `const char*` (para leer), un `byte[]` son `items` e `items_length`, un tipo native su tipo
  de C. Devuelve lo que dice la firma (un `String` lo copia Larimar). Lo que está fuera del método (otra
  función, una global de Larimar) se nombra con `lar"nombre"`. `self` no está: lo que el C necesita va
  como parámetro. Una función fuera de una clase también puede tener cuerpo de C.
- **`cinclude` y `ccode` dentro de una clase** son sus headers y el C que comparten sus métodos.
- **Las plataformas** son interfaces de `std.os`, una dentro de otra:

  ```ts
  public interface Platform {}
  public interface UnixPlatform extends Platform {}       // Linux, macOS y los otros Unix
  public interface LinuxPlatform extends UnixPlatform {}
  public interface MacOSPlatform extends UnixPlatform {}
  public interface WindowsPlatform extends Platform {}
  ```

  Una clase de una plataforma pone todo su C (headers, `ccode`, cuerpos) en el C dentro del `#if` de ese
  sistema, que escribe el compilador. El mismo archivo C compila en todas partes, y un build de Linux
  nunca ve `<windows.h>`. Llamado en otro sistema, un método de esa clase da un panic: *'WindowsClock.sleep'
  is for windows, not for this system*. Una subclase puede ser de una plataforma más estrecha: `class
  MacOSSystem extends PosixSystem implements MacOSPlatform` reescribe solo lo que cambia en macOS.
- **`os.platform()`** da `OS.Linux`, `MacOS`, `Windows` o `Unix` (otro Unix). Un `switch` sobre él sin
  `default` tiene que nombrar cada sistema: un sistema que se añada después muestra cada sitio que portar.
  Es una constante del compilador de C, así que la rama de los otros sistemas desaparece del ejecutable.
- Las implementaciones guardadas en una global las comparten los hilos: una interfaz cuyas clases no
  tienen campos se puede compartir (no tiene estado que cambiar).

Qué usar, de menos C a más:

1. **Declaraciones `native`**, cuando C ya tiene la función, el tipo o la constante: casi siempre.
2. **`ccode { ... }`**, unas líneas que C escribe mejor: un cast, una macro, un bucle sobre `EINTR`.
3. **Una clase por plataforma con C en sus métodos**, cuando los sistemas lo hacen distinto.
4. **`native` + [`#when`](#cada-sistema-lo-suyo-when)**, una forma corta para una o dos declaraciones que
   cambian de nombre entre sistemas, en un binding propio.

### Pasar una memoria a C

Una función de C puede recibir una memoria de Larimar (`m: byte[*]` en la declaración) y crear cosas en
ella. Cuando **la memoria es su primer parámetro**, la llamada no la escribe: C recibe la memoria de la
llamada, la misma que recibiría una función de Larimar, así que lo que devuelve vive donde diga quien
llama (su bloque, la lista donde se añade, o la memoria que se escriba con `in`). Es la forma correcta de
que C devuelva texto:

```ts
ccode {
    #include <ctype.h>

    static const char* shout(RtMem* m, const char* text) {
        size_t n = strlen(text);
        char* out = (char*)rt_mem_alloc(m, n + 2, 0);     /* memoria a cero: el texto termina solo */
        for (size_t i = 0; i < n; i++) out[i] = (char)toupper((unsigned char)text[i]);
        out[n] = '!';
        return out;
    }
}

native function shout(m: byte[*], text: String): String;

function main(): int32 {
    println(shout("hello larimar"));                      // en la memoria temporal de la instrucción
    let memory: byte[*] = [] in heap;
    let kept: String = shout("kept") in memory;           // en una memoria propia
    println(kept);
    return 0;
}
```

Salida:
```
HELLO LARIMAR!
KEPT!
```

En C, una memoria llega como `RtMem*`, y `rt_mem_alloc(m, bytes, 0)` reserva espacio dentro de ella
(con los bytes a cero). Esa es toda la interfaz que el C necesita conocer. La regla es una: **el C usa la
memoria solo durante la llamada**. Si guardara el puntero para después, la memoria podría liberarse antes.
Una memoria en otro parámetro (no el primero) se pasa escrita, como cualquier argumento.

Así queda el ejemplo de Windows que antes necesitaba un archivo `.c` aparte:

```ts
ccode {
    #include <windows.h>

    static const char* computer_name(RtMem* m) {
        DWORD size = MAX_COMPUTERNAME_LENGTH + 1;
        char* name = (char*)rt_mem_alloc(m, size, 0);
        return GetComputerNameA(name, &size) ? name : "";
    }
}

native function computer_name(m: byte[*]): String;
```

### Tipos de C: `native type`

Un tipo que viene de C se declara con `native type`. Después del `=` va su tipo en C:

| Declaración | Qué es | En C |
|---|---|---|
| `native type Handle;` | un puntero opaco: se recibe, se guarda y se pasa, sin mirar dentro | `void*` |
| `native type File = FILE*;` | un tipo de C concreto | `FILE*` |
| `native type Tm = c"struct tm*";` | un tipo de C que no es un nombre simple, como texto de C `c"..."` | `struct tm*` |
| `native type Op = (int32, int32) -> int32;` | un puntero a una función de C | `int32_t (*)(int32_t, int32_t)` |

```ts
ccode {
    #include <stdio.h>

    typedef struct Point { float x, y; } Point;

    static Point point_mid(Point a, Point b) {
        Point m = { (a.x + b.x) / 2, (a.y + b.y) / 2 };
        return m;
    }
    static FILE* log_file(void) { return stderr; }
    static void log_line(FILE* f, const char* text) { fprintf(f, "%s\n", text); }
}

native type File = FILE*;                                    // un tipo de C concreto
native struct Point { let x: float32; let y: float32; }      // un struct de C, por valor

native function point_mid(a: Point, b: Point): Point;
native function log_file(): File;
native function log_line(f: File, text: String): void;

function main(): int32 {
    let a: Point = { x: 0, y: 0 };
    let b: Point = Point { x: 4, y: 2 };
    let m: Point = point_mid(a, b);
    println("(${m.x}, ${m.y})");
    log_line(log_file(), "listo");
    return 0;
}
```

Salida: `(2.0, 1.0)`, y `listo` en la salida de errores.

- **Cada `native type` es un tipo distinto en Larimar**, aunque en C sean lo mismo: no se puede pasar un
  `File` donde se espera un `Handle`.
- **El tipo exacto de C** (`= FILE*`) hace que el compilador de C también compruebe los tipos: con `void*`
  no notaría que se pasa un `FILE*` donde la biblioteca espera un `sqlite3*`.

### Tipos de C con miembros

Una biblioteca de C suele girar alrededor de un puntero (`sqlite3*`, `SDL_Window*`, `http_s*`) y de las
funciones que lo reciben primero. Un `native type` puede declarar todo eso entre llaves, y entonces se usa
como un objeto:

```ts
ccode {
    typedef struct Counter { int value; const char* name; } Counter;
    static Counter* counter_new(const char* name) { Counter* c = (Counter*)calloc(1, sizeof(Counter)); c->name = name; return c; }
    static void counter_free(Counter* c) { free(c); }
    static void counter_add(Counter* c, int n) { c->value += n; }
    static int counter_get(Counter* c) { return c->value; }
}

native type Counter = Counter* {
    let value: int32;                                  // un campo del struct al que apunta
    let label: String = name;                          // con otro nombre en C
    native function add(n: int32): void = counter_add; // counter_add(self, n)
    native let current: int32 = counter_get;           // se lee sin paréntesis: counter_get(self)
    function addTwice(n: int32): void {                // un método escrito en Larimar
        self.add(n);
        self.add(n);
    }
    static native function make(name: String): Counter = counter_new;
}
native function counter_free(c: Counter): void;

function main(): int32 {
    let c: Counter = Counter.make("clicks");
    c.add(3);
    c.addTwice(2);
    c.value += 10;
    println("${c.label}: ${c.value} ${c.current}");
    counter_free(c);
    return 0;
}
```

Salida: `clicks: 17 17`

- **`let`** es un campo del struct de C al que apunta el tipo, que se lee y se escribe con `x.campo` (en C,
  `x->campo`). Después del `=` va su nombre en C cuando es otro. Un tipo con campos tiene que ser un
  puntero: `= Counter*`.
- **`native function m(...) = c_m;`** llama a esa función de C con `self` primero y después los argumentos.
  Si su primer parámetro es una memoria (`m: byte[*]`), esa va antes de `self` y no se escribe en la
  llamada, como en [Pasar una memoria a C](#pasar-una-memoria-a-c).
- **`native let x: T = c_x;`** es lo mismo sin argumentos, y se lee sin paréntesis.
- Después del `= c_m` de cualquiera de los dos, **`released by f`** dice que C hace el texto que devuelve,
  que se copia y se libera ([Textos que hace C](#textos-que-hace-c-released-by-en-una-función)):
  `native let name: String = item_name released by free;`.
- Con cualquier otra expresión después del `=`, el método es esa expresión de Larimar, como en una clase:
  `native function ok(text: String): void = reply(self, 200, text);`.
- **`function`** es un método escrito en Larimar, y **`static native function`** llama a una función de C
  sin `self` (`Counter.make(...)`). También vale `static function`.
- Un tipo con miembros se declara fuera de `#when`; dentro de cada `#when` va, si cambia, su tipo de C.

### Structs de C: `native struct`

Un struct de C que se pasa **por valor** se declara con `native struct`, con los campos que se usan:

```ts
ccode {
    typedef struct span_t { int from_; int to_; } span_t;
    static span_t widen(span_t s) { s.from_ -= 1; s.to_ += 1; return s; }
}

native struct Span = span_t {
    let from: int32 = from_;                  // el nombre en C, cuando es otro
    let to: int32 = to_;
    function length(): int32 { return self.to - self.from; }
}
native function widen(s: Span): Span;

function main(): int32 {
    let s: Span = widen({ from: 3, to: 10 });
    println("${s.from} ${s.to} ${s.length()}");
    return 0;
}
```

Salida: `2 11 9`

- Se usa como cualquier struct de Larimar: literales (`{ x: 1, y: 2 }` o `Point { x: 1 }`), acceso a
  campos, copia por valor, listas (`Point[*]`) y métodos escritos en Larimar.
- La definición la pone C (el `.h` o el `ccode`); Larimar no la escribe. Así el orden y la alineación
  de los campos siempre son los de C.
- Basta con declarar los campos que se usan: si el struct de C tiene diez y te interesan tres, declaras tres.
- Sus campos solo pueden ser números, `bool`, tipos `native`, punteros (`T*`), otros structs de C y
  `String`. Un campo `String` es un texto de C (`char*` o `char[N]`) que **se lee, no se asigna**, y es
  una vista del texto de C: si C lo cambia o lo libera, la vista también. Para guardarlo, `.clone()`.
- Los campos que no se dan en un literal valen cero, como en C: `{ ai_socktype: 1 }`.
- Si el nombre en C es otro, va después del `=`: `native struct Rect = rect_t { ... }`, o como texto de C si
  no es un nombre simple: `native struct AddrInfo = c"struct addrinfo" { ... }`.

### Constantes y variables de C: `native const`, `native let`

Las constantes, las macros y las variables globales de C se usan por su nombre, declarándolas con su tipo:

```ts
cinclude "<errno.h>";
cinclude "<limits.h>";

native const INT_MAX: int32;                                       // una macro de C
native const ENOENT: int32;
native const POINTER_SIZE: int32 = c"(int)sizeof(void*)";           // una expresión de C
native let errno: int32;                                           // una variable de C

function main(): int32 {
    println("${INT_MAX} ${POINTER_SIZE} ${errno == ENOENT}");
    return 0;
}
```

- **`native const`** no cambia; **`native let`** se puede leer y asignar (`errno = 0;`).
- Larimar escribe en el C el nombre tal cual, así que valen macros, constantes de `enum` y variables, y
  también macros que se expanden en algo más complejo (`errno`, `stdout`).
- Después del `=` va su nombre en C cuando es otro (`native const MAX: int32 = INT_MAX;`), o, como
  texto de C `c"..."`, una expresión de C para lo que no tiene nombre: `sizeof`, un cast, una macro con argumentos.
- Una `native const` puede ser un `String` (una macro de texto); una `native let`, no.

### Punteros de C: `T*` y `&`

Muchas funciones de C piden o devuelven punteros: una lista enlazada (`getaddrinfo`), un resultado que se
escribe en una variable (`accept(fd, &addr, &len)`), un búfer. **`T*`** es un puntero de C a un número, a
`bool`, a un struct de C, a un tipo `native` o a otro puntero:

```ts
ccode {
    typedef struct Node { int value; struct Node* next; const char* name; } Node;
    static Node nodes[3] = { { 10, &nodes[1], "uno" }, { 20, &nodes[2], "dos" }, { 30, NULL, "tres" } };
    static Node* first_node(void) { return &nodes[0]; }
    static void two_results(int* a, int* b) { *a = 7; *b = 42; }
    static int sum_bytes(const unsigned char* p, int n) { int s = 0; for (int i = 0; i < n; i++) s += p[i]; return s; }
}

native struct Node {
    let value: int32;
    let next: Node*;
    let name: String;                       // un texto de C: se lee
}
native function first_node(): Node*;
native function two_results(a: int32*, b: int32*): void;
native function sum_bytes(p: byte*, n: int32): int32;

function main(): int32 {
    let sum: int32 = 0;
    let p: Node* = first_node();
    while (p != null) {                     // un puntero puede ser null, como en C
        sum += p.value;                     // p.value es p->value
        p = p.next;
    }
    let a: int32 = 0;
    let b: int32 = 0;
    two_results(&a, &b);                    // C escribe en a y en b
    let bytes: byte[4] = [1, 2, 3, 4];
    println("${sum} ${a} ${b} ${sum_bytes(bytes, bytes.length)}");
    return 0;
}
```

Salida: `60 7 42 10`

- **`p.campo`** lee o escribe el campo del struct al que apunta (`p->campo` en C). Si `p` es `null`, el
  programa se detiene con un error en esa línea, en vez de fallar en C.
- **`&x`** da la dirección de una variable para que C la lea o escriba. **Solo vale como argumento de una
  función de C** (`f(&x)`), así que el puntero nunca vive más que la llamada; `x` es una variable cuyo tipo
  admite punteros. `&x as Otro*` también vale ahí (C pide a veces otro tipo de puntero).
- **Un arreglo donde C pide `T*`** llega como el puntero a sus elementos: `fread(buffer, 1, buffer.length, f)`.
- **`as`** convierte entre punteros (un `sockaddr_in*` como `sockaddr*`), y entre un puntero y un tipo
  `native` opaco (`void*`).
- Un puntero no apunta a memoria de Larimar (`&x` solo existe durante la llamada), así que no entra en la
  regla de vida: lo que hay al otro lado es de C, y C dice cuánto dura.

### Recursos: `released by`

Algunas cosas de C hay que soltarlas: un archivo (`fclose`), un socket (`close`), una ventana
(`SDL_DestroyWindow`), una base de datos (`sqlite3_close`). Se declara una vez, en su `native type`, con
qué función se suelta:

```ts
cinclude "<stdio.h>";

native type CFile = FILE* released by fclose;
native function fopen(path: String, mode: String): CFile?;
native function fputs(text: String, f: CFile): int32;
native function fclose(f: CFile): int32;

function main(): int32 {
    for (i in 0..1000) {
        let f: CFile? = fopen("log.txt", "a");
        if (f == null) { return 1; }
        fputs("una línea\n", f!);
    }   // cada vuelta: su memoria se libera, y con ella el archivo (fclose)
    let g: CFile? = fopen("log.txt", "a");
    release(g);                            // antes de tiempo, si hace falta
    return 0;
}
```

- **Un recurso vive en una memoria, como cualquier dato**: donde se guarda lo que devuelve la función de C
  (el bloque de un `let`, el objeto de un campo, `in scratch`...). **Cuando esa memoria se libera, se suelta.**
  Lo que se ve en el código es dónde vive, igual que con un `String`.
- **`release(x)`** lo suelta ya. Soltarlo dos veces no hace nada; usarlo después detiene el programa con
  `a released CFile was used`.
- **La función de C que lo crea devuelve `T?`**, porque puede fallar: un puntero `NULL` (o `-1`, como
  `INVALID_HANDLE_VALUE`) o un número negativo (un descriptor `-1`) llega como `null`.
- **Una función de Larimar puede devolver lo que crea una así** (`function open(path: String): CFile? { return fopen(path, "r"); }`):
  el recurso se crea donde diga quien la llama, como cualquier resultado.
- **La función que lo suelta recibe exactamente un `T`**, y solo `release()` puede llamarla: llamarla a mano
  lo soltaría dos veces. Puede ser una función de C o una de Larimar (para soltar en varios pasos).
- Un objeto que guarda un recurso **no se puede clonar** (se soltaría dos veces).
- Si la función que lo suelta existe en un solo sistema (`closedir` en Unix), el recurso solo existe allí.
- Un recurso también puede tener [miembros](#tipos-de-c-con-miembros):
  `native type Db = sqlite3* released by sqlite3_close { native function errmsg(): String = sqlite3_errmsg; ... }`.

### Textos que hace C: `released by` en una función

Algunas funciones de C devuelven un texto que ya es de quien llama, hecho con `malloc` (o con el
asignador de la propia biblioteca): `strdup`, `realpath(path, NULL)`, `sqlite3_expanded_sql`. Después del
resultado (y de su `= C`, si lo tiene) va **`released by`** con la función que lo libera:

```ts
cinclude "<string.h>";
cinclude "<stdlib.h>";

native function strdup(text: String): String released by free;
native function free(text: String): void;

function main(): int32 {
    for (i in 0..1000) {
        let copy: String = strdup("texto ${i}");
        if (i == 999) { println(copy); }
    }
    return 0;
}
```

Salida: `texto 999`

- El texto se **copia** en la memoria donde va el resultado, como cualquier resultado (el bloque de un
  `let`, un objeto, `in scratch`, un buffer), y el de C se libera en seguida: Larimar no se queda con el
  puntero de C, así que nada se pierde y nada se libera dos veces.
- Con `String?`, un `NULL` llega como `null` (y no hay nada que liberar).
- La función después de `released by` es una `native function` que recibe un `String`, y solo el
  compilador la llama. En C se declara con `void*`, como lo están `free(void*)` o `sqlite3_free(void*)`.
- Un texto que C conserva (uno estático, o uno que pertenece a algo de C, como `sqlite3_errmsg`) no se
  libera: se declara sin `released by`.

### Cada sistema lo suyo: `#when`

Lo que cambia entre sistemas se escribe entre **`#when`** y **`#end`**, que eligen al compilar el C
(`#if`), no al ejecutar. Empiezan con `#` para que se vean distintos de la lógica del programa:

```ts
cinclude "<errno.h>";
#when unix
    cinclude "<unistd.h>";
#when windows
    cinclude "<winsock2.h>";
    cinclude "<ws2tcpip.h>";
#end

#when unix
    native type Socket = int released by close;
    native function close(s: Socket): int32;
    native let errno: int32;
#when windows
    native type Socket = SOCKET released by closesocket;
    native function closesocket(s: Socket): int32;
    native function WSAGetLastError(): int32;
#end

function lastError(): int32 {
    #when windows
        return WSAGetLastError();
    #else
        return errno;
    #end
}
```

- Los sistemas son **`windows`**, **`macos`**, **`linux`** y **`unix`** (todos menos Windows).
- **Cada directiva va sola en su línea**: `#when <sistema>`, `#else` y `#end` (detrás solo cabe un
  comentario). Un `#when` tras otro es la siguiente opción, como el `#elif` de C.
- **Sin llaves y sin bloque.** Lo de dentro pertenece al bloque de alrededor, como las líneas de un `#if`
  de C. La sangría no es obligatoria, pero ayuda a leerlo.
- **`#when`, `#else` y `#end` de una misma elección empiezan en la misma columna.** Un `#when` con más
  sangría está anidado dentro de una rama:

  ```ts
  #when windows
      return "windows";
  #else
      #when macos
          let what: String = "mac";
      #else
          let what: String = "otro unix";
      #end
      return what;
  #end
  ```

- **Lo que todas las ramas declaran, con el mismo tipo, sigue existiendo después de `#end`**:

  ```ts
  #when windows
      let sep: String = "\\";
  #else
      let sep: String = "/";
  #end
  println(sep);              // sep existe aquí
  ```

  Lo que declara una rama sola es solo de esa rama. Si las ramas no cubren todos los sistemas (sin
  `#else`), nada de lo que declaran queda después: algún sistema no lo tendría.
- **Fuera de las funciones**, dentro de `#when` solo van `cinclude` y declaraciones `native` (sin
  miembros), y `#else` solo sigue a `#when windows` o a `#when unix` (el resto es entonces el otro).
- **El compilador comprueba todas las ramas**, así que un error del código de Windows se ve también
  compilando en un Mac. Una rama que nunca se elegiría (`#when macos` tras `#when unix`) es un error.
- **Lo que solo existe en un sistema se usa dentro de su `#when`**: llamar a `closesocket` fuera de
  `#when windows` es un error del compilador (*'closesocket' exists only on windows*).
- **Un tipo puede declararse una vez por sistema** (`Socket` arriba), siempre que cubra todos.

Así está escrita la red de la biblioteca estándar (`std/net.lar`): sockets de Unix y de Windows, sin una
línea de `ccode`. También los archivos (`std.io.files`), la consola y `std.os`.

### Punteros a funciones de C

`native type Op = (A, B) -> R;` declara el tipo de un puntero a función de C. Un valor de ese tipo se
pasa a C, se guarda y **se llama como una función**:

```ts
ccode {
    typedef int32_t (*op_fn)(int32_t, int32_t);

    static int32_t sumar(int32_t a, int32_t b) { return a + b; }
    static int32_t apply(op_fn f, int32_t a, int32_t b) { return f(a, b); }
}

native type Operation = (int32, int32) -> int32;

native function sumar(a: int32, b: int32): int32;
native function apply(f: Operation, a: int32, b: int32): int32;

export function restar(a: int32, b: int32): int32 {
    return a - b;
}

function main(): int32 {
    println("${apply(sumar, 10, 3)}");      // una función de C
    println("${apply(restar, 10, 3)}");     // una función de Larimar, llamada desde C
    let op: Operation = restar;
    println("${op(20, 5)}");                // un puntero a función se llama como una función
    return 0;
}
```

Salida:
```
13
7
15
```

- Donde se espera un `Operation` vale **una función que exista en C con esa firma exacta**: una
  `native function` o una `export function`.
- **Una lambda no vale aquí**, porque no es una función de C: lleva capturas, y C no sabría qué hacer con
  ellas. Cuando la biblioteca da un `void*` de contexto, sí vale: ver la sección siguiente.
- Una función de Larimar normal tampoco vale: el compilador pide marcarla `export`.
- También pueden venir de C: una función de C que devuelve un `Operation`, o un campo de un struct de C.
- Los tipos permitidos son los de `native function`. Un `String` llega a C como `const char*`, y uno que
  devuelve C se lee igual que en una `native function`.

### Callbacks con contexto: `Context`

Casi todas las bibliotecas de C que reciben un callback reciben también un **`void*` de contexto**, que le
devuelven en cada llamada (`user_data`, `arg`, `udata`). Larimar lo llama **`Context`**. Si el tipo del
callback y la función que lo recibe declaran ese `Context`, **cualquier función de Larimar vale, también
una lambda con lo que captura**:

```ts
ccode {
    typedef void (*item_fn)(int32_t index, const char* name, void* data);
    static void for_each_name(item_fn f, void* data) {
        const char* names[] = { "uno", "dos", "tres" };
        for (int32_t i = 0; i < 3; i++) f(i, names[i], data);
    }
}

native type ItemFn = (int32, String, Context) -> void;
native function for_each_name(f: ItemFn, data: Context): void;

class Totals { let count: int32 = 0; }

function main(): int32 {
    let prefix: String = "->";
    let totals: Totals = {};
    for_each_name((i, name) -> {             // un (int32, String) -> void: el Context no se escribe
        totals.count += 1;
        println("${prefix} ${i} ${name.toUpperCase()}");
    });
    println("count ${totals.count}");
    return 0;
}
```

Salida:
```
-> 0 UNO
-> 1 DOS
-> 2 TRES
count 3
```

- **El `Context` no se escribe**, ni en la lambda ni en la llamada: C recibe una función de C que hace el
  compilador, y como contexto, la función de Larimar con sus capturas.
- **Una `export function` o una `native function` del tipo exacto también valen**, y van tal cual (con
  `NULL` como contexto).
- **Si C guarda el callback para después** (un manejador, un temporizador), el parámetro lo dice con
  **`in default`**, y entonces lo que captura debe vivir todo el programa:

  ```ts
  native type BusyFn = (Context, int32) -> int32;
  native function set_busy(f: BusyFn in default, data: Context): void;

  let limit: Limit = Limit { count: 5 } in default;
  set_busy((tries) -> { return tries < limit.count ? 1 : 0; });
  ```

  Si `limit` viviera en el bloque, el error lo dice: *C keeps the function given to 'set_busy' (in
  default), so what it uses must live as long as the whole program*.
- **Un miembro de un tipo de C también lo acepta**: `native function onBusy(handler: BusyFn in default, data: Context): int32 = sqlite3_busy_handler;`
  se llama como `db.onBusy((n) -> { return n < 5 ? 1 : 0; })`.
- La función de Larimar no puede devolver un `String` a C (C no sabría cuándo liberarlo), y el callback no
  puede recibir recursos.
- Si la biblioteca llama al callback desde otro hilo, las reglas de hilos de Larimar no la protegen, igual
  que con una `export function`.
- Si la biblioteca no da contexto (facil.io, por ejemplo, guarda su `udata` en otro lado), el callback es
  una `export function`, y lo que necesita lo busca en una variable global.

### Que C llame a Larimar: `export function`

`export function` es lo contrario de `native function`: **lleva una función de Larimar a C**. El
compilador la genera en C con ese mismo nombre y con tipos de C, así que C puede llamarla, guardarla en un
puntero o recibirla como callback:

```ts
ccode {
    typedef void (*item_fn)(int32_t index, const char* name, void* data);

    static void for_each_name(item_fn f, void* data) {
        const char* names[] = { "uno", "dos", "tres" };
        for (int32_t i = 0; i < 3; i++) f(i, names[i], data);
    }
}

native type ItemHandler = (int32, String, Context) -> void;

native function for_each_name(f: ItemHandler, data: Context): void;

export function show_item(index: int32, name: String, data: Context): void {
    println("${index}: ${name.toUpperCase()}");
}

function main(): int32 {
    for_each_name(show_item);
    return 0;
}
```

Salida:
```
0: UNO
1: DOS
2: TRES
```

Lo que garantiza `export function`:

- **Su nombre en C es el suyo**, también dentro de un módulo: `public export function lm_double(...)` en
  el módulo `gfx.shapes` sigue llamándose `lm_double` en C. **`= nombre_c`** después de la firma le da
  otro: `export function double(x: int32): int32 = lm_double { ... }`. En una biblioteca es
  `<prefijo>_<nombre>` salvo que diga `= nombre_c` (ver [Bibliotecas escritas en Larimar](#27-bibliotecas-escritas-en-larimar)).
- **Firma de C limpia**: sin parámetros ocultos. Números y `bool` tal cual, `String` llega como
  `const char*` (se convierte a texto de Larimar al entrar), un `String?` también (`NULL` es `null`), tipos
  `native` como su tipo de C y structs de C por valor.
- **Un texto que devuelve es de C.** Un resultado `String` llega a C como un `char*` hecho con `malloc`,
  una copia que C libera con `free` cuando termina con ella; un `String?` es eso, o `NULL` para `null`.
  Larimar no se queda con nada de él.
- **Cada llamada desde C tiene su propia memoria**, que nace al entrar y muere al volver, como cualquier
  función. Lo que la función crea no se queda colgando en C.
- **Un `ccode` puede usarla directamente**. Si su firma solo tiene números, `bool`, `String`, `String?` y
  tipos `native` opacos, el compilador escribe su prototipo antes de los `ccode`. Si usa structs de C o
  tipos de C concretos, que quizá define el propio `ccode`, el prototipo va después, y el `ccode` que la
  llame debe declararla él mismo.

```ts
export function greet(name: String?): String = lar_greet {
    return "hola ${name ?? "nadie"}";
}

ccode {
    #include <stdio.h>
    #include <stdlib.h>

    static void say_hi(void) {
        char* a = lar_greet("Ana");
        char* b = lar_greet(NULL);
        printf("%s, %s\n", a, b);
        free(a);
        free(b);
    }
}

native function say_hi(): void;

function main(): int32 {
    say_hi();
    return 0;
}
```

Salida: `hola Ana, hola nadie`

Y lo que no admite, porque C no podría manejarlo:

- `throws`: un error no puede atravesar código C, así que se captura dentro;
- `in` en los parámetros o en el resultado, memorias (`byte[*]`), listas o `Any`;
- clases, salvo en una biblioteca, donde C guarda sus objetos como handles
  ([Bibliotecas escritas en Larimar](#27-bibliotecas-escritas-en-larimar));
- `main`.

Si la biblioteca llama a la función desde otro hilo, el compilador no puede saberlo: las reglas de hilos
de Larimar no la protegen, igual que pasa dentro de un `ccode`.

---

## 24. Módulos

Un programa puede repartirse en varios archivos. **Cada archivo es un módulo**, y su nombre sale de
su ruta dentro de la carpeta del archivo principal:

```
src/
  main.lar            el archivo principal (tiene main)
  geo/shapes.lar      el módulo geo.shapes
  util/text.lar       el módulo util.text
```

### `public`

Lo que declara un módulo es **privado** salvo que lleve `public` delante. Se puede marcar cualquier
declaración con nombre: funciones, constantes, variables globales, structs, clases, interfaces, enums y
declaraciones `native`.

```ts
// src/geo/shapes.lar
public const PI: float64 = 3.14159;

public enum Shape { Circle(radius: float64), Rect(width: float64, height: float64), Empty }

function square(x: float64): float64 { return x * x; }     // privada

public function area(s: Shape): float64 {
    return switch (s) {
        case Circle { radius } -> PI * square(radius);
        case Rect { width, height } -> width * height;
        case Empty -> 0.0;
    };
}
```

`public` se aplica al nombre completo: en una clase pública, sus campos y métodos se ven desde fuera.
No hay `private`: escribirlo es un error (`'private' is not needed: ...`), porque sin `public` ya lo es.

Por convención, un campo o un método que no está pensado para usarse fuera de su clase empieza con `_`:
`let _cache: Any = {};`. El compilador no lo exige; se lo dice a quien lee. (Un solo `_`: los nombres
no pueden tener `__`.)

### `import`

Los `import` van al principio del archivo y tienen tres formas:

```ts
import geo.shapes;                   // los nombres se usan con el prefijo: shapes.area(s)
import geo.shapes as g;              // con otro prefijo: g.area(s)
import geo.shapes { Shape, area };   // esos nombres, sin prefijo: area(s)
```

Con el prefijo se accede a todo lo público: funciones (`shapes.area(s)`), constantes (`shapes.PI`),
tipos (`let s: shapes.Shape`, `shapes.Figure { ... }`, `class Wheel extends shapes.Figure`,
`catch (shapes.ShapeError e)`) y variantes (`shapes.Shape.Circle { radius: 1.0 }`).

```ts
import geo.shapes;
import geo.shapes { Shape };

function main(): int32 {
    let s: Shape = Shape.Circle { radius: 2.0 };
    println("area ${shapes.area(s)}, pi ${shapes.PI}");
    return 0;
}
```

Salida: `area 12.56636, pi 3.14159`

### Reglas

- Una variable local puede llamarse como un módulo o como uno de sus nombres; dentro de su bloque, gana la local.
- Dos módulos pueden tener nombres iguales sin conflicto: `geo.shapes.square` y `util.text.square` son distintos.
- Los módulos pueden importarse entre sí en círculo (`a` importa `b` y `b` importa `a`).
- Las variables globales se inicializan módulo por módulo: primero los importados, al final el archivo principal.
- **Los módulos no ven el archivo principal.** Nadie puede importarlo; lo compartido va en un módulo.
- Un mismo archivo se carga una sola vez, aunque lo importen varios módulos.
- Los nombres no pueden contener `__` (doble guion bajo): el C generado lo usa para separar el
  módulo del nombre (`geo__shapes__area`).

Los errores dicen en qué archivo están:

```
Module Error [src/main.lar:2]: 'square' is private to module 'geo.shapes'; mark it 'public' there to use it here.
Semantic Error [src/geo/shapes.lar:14]: Initializer of 'x': expected int32 but got String.
```

Y los fallos en tiempo de ejecución también: `panic [src/geo/shapes.lar:9]: index 5 out of range (length 3)`.

---

## 25. Biblioteca estándar

La biblioteca estándar son módulos que vienen con Larimar y se importan como cualquier otro:
`import std.os;`. Están escritos en Larimar, con un poco de C (`ccode`) para hablar con el sistema
operativo, y viven en la carpeta `std/` junto a la herramienta (o en `$LARIMAR_HOME/std`). Solo lo que se
importa entra en el programa, y el ejecutable no necesita la carpeta `std` para funcionar.

| Módulo | Para qué |
|---|---|
| `std.lang` | tipos y métodos disponibles en todo programa (`String`, `Any`, `Thread`, `StringBuilder`); se ve sin importarlo |
| `std.io` | lo que comparte toda entrada y salida: `IoError`, `InputStream`, `OutputStream`, `Closeable`, `Reader`, `copy`, `buffer`, streams en memoria |
| `std.io.files` | archivos y carpetas: archivos enteros de una vez, como `Files` de Java, y un `File` abierto para leer o escribir por partes |
| `std.io.path` | rutas: carpeta, nombre, extensión, unir, normalizar |
| `std.io.console` | la entrada, la salida y la salida de errores |
| `std.os` | el entorno: variables, carpeta actual, ejecutar comandos, terminar con Ctrl+C o SIGTERM |
| `std.os.process` | otros programas: `Process`, hablarles por su entrada y su salida |
| `std.time` | el reloj (`now`, `monotonic`), `sleep`, fechas como texto (HTTP, ISO 8601) |
| `std.thread` | `ThreadPool`: un lote de tareas en unos pocos hilos |
| `std.crypto` | SHA-256, SHA-1, HMAC-SHA256 y bytes aleatorios seguros |
| `std.text` | clasificar bytes (para lexers y parsers) |
| `std.text.regex` | expresiones regulares: `Regex`, `Match` (escritas en Larimar, sin bibliotecas de C) |
| `std.encoding.json` | JSON a `Any` y `Any` a JSON |
| `std.encoding.toml` | TOML a `Any` y `Any` a TOML |
| `std.encoding.base64`, `hex`, `url` | bytes como texto base64 y hex; codificación de URL y *query strings* |
| `std.net` | TCP y UDP: `TcpSocket`, `TcpListener`, `TcpServer` (normal o https), `UdpSocket`, `UdpServer`, `EventLoop`, `Connection`, `OpenSslProvider`, `StopSignal` |
| `std.net.http` | cliente HTTP/1.1 y `https://`: `Client`, `Request`; el cuerpo como texto, JSON o stream |
| `std.net.tls` | `TlsProvider` (la interfaz para conexiones cifradas de cliente) y `SystemTls` (el TLS del sistema) |

**`std.lang`** es especial: todo programa ve sus nombres sin escribir `import`, y al C solo llega lo que el
programa nombra (y lo que eso necesita). Un nombre propio del archivo principal tapa al de `std.lang`.

### `std.io.files`: archivos y carpetas

Se importa con el nombre de Java: `import std.io.files as Files;`. Ninguna función recibe memorias: lo
que devuelven (el texto de un archivo, los nombres de una carpeta) vive donde diga quien llama, como lo
de cualquier función (`Files.readString(path) in memory`, si se quiere elegir). Todo lo que puede fallar lanza
`IoError`, de `std.io` ([más abajo](#stdio-leer-y-escribir-sin-importar-de-dónde); `Files.message(e)` lo dice en texto).

| Función | Qué hace |
|---|---|
| `Files.readString(path): String` | el archivo entero, como texto |
| `Files.writeString(path, text)` | reemplaza el archivo (lo crea si no existe) |
| `Files.appendString(path, text)` | añade al final |
| `Files.exists(path)`, `isFile(path)`, `isDirectory(path)` | qué hay en esa ruta |
| `Files.list(path): String[*]` | los nombres de lo que hay en una carpeta |
| `Files.createDirectories(path)` | crea la carpeta y las que falten por encima |
| `Files.copy(from, to)`, `Files.delete(path)` | copiar un archivo; borrar un archivo o una carpeta vacía |
| `Files.modifiedTime(path)`, `Files.size(path)` | cuándo cambió por última vez (segundos desde 1970, 0 si no hay nada), su tamaño en bytes (-1) |

**Un archivo abierto.** `Files.open(path)`, `Files.create(path)` (lo vacía) y `Files.append(path)`
(escribe al final) dan un `File` (`import std.io.files { File };`). Como stream
binario implementa `read(buffer: byte[]): int32`, `write(bytes: byte[])`, `flush()` y `close()`. `read`
devuelve los bytes leídos y `0` al llegar al final. También ofrece `readLine(): String?`, `readAll()` y
`writeText(text)` como operaciones de texto. **Un `File` se cierra solo cuando se libera la memoria donde
vive** (normalmente, al cerrar el bloque de su variable); `close()` lo cierra antes.

### `std.io`: leer y escribir sin importar de dónde

**El error** de toda entrada y salida, de los archivos a los sockets:

```ts
public enum IoError {
    NotFound(path: String),      // a file or folder that is not there
    Denied(path: String),        // no permission
    Closed,                      // the other side closed it (a socket, a pipe)
    TimedOut,                    // a read or a write took longer than allowed
    Failed(what: String)         // anything else: what failed
}
```

`Io.message(e)` (con `import std.io as Io;`) lo da como texto: `not found: notes.txt`, `timed out`...

**Los streams**: lo mínimo, como en Go: bytes que se leen, bytes que se escriben, y algo que se puede cerrar.

| Interfaz | Métodos |
|---|---|
| `InputStream` | `read(buffer: byte[]): int32`: llena el búfer desde el inicio y dice cuántos bytes leyó; `0` al final |
| `OutputStream` | `write(bytes: byte[])` (todos, o lanza `IoError`) y `flush()` |
| `Closeable` | `close()`: suelta antes de tiempo lo que tiene del sistema (lo suelta igual al liberarse su memoria) |

Lo implementan `File`, `TcpSocket` y `TlsSocket` (y cualquier `Connection` con `input()` y `output()`), el
cuerpo de una respuesta de `std.net.http` y los streams de la consola
(`Console.input`, `Console.output`, `Console.error`). Además:

| Nombre | Qué es |
|---|---|
| `Reader { from: stream }` | texto sobre cualquier `InputStream`: `readLine(): String?` (corta en `\n`, quita un `\r` antes), `readAll()`, y bytes con `readInto(buffer, max)`; también es un `InputStream` |
| `copy(input, output)` | copia todo y hace `flush()`; no cierra ninguno |
| `buffer(n)` | `n` bytes a cero, para dárselos a `read()` |
| `MemoryInputStream { data: text }` | lee un `String` (texto o bytes) que ya está en memoria |
| `MemoryOutputStream {}` | junta lo que se escribe: `toString()`, `toByteArray()` |

Un `byte[4096] = []` no sirve como búfer de `read()`: empieza vacío (longitud 0) y `read()` llena solo hasta
la longitud de lo que recibe; para eso está `buffer(4096)`.

El `Reader` tiene un búfer para toda su vida, y una línea se crea una sola vez, a su tamaño, donde diga quien
llama. Con una memoria en la pila, leer un archivo (o un socket) de cualquier tamaño no pide memoria en el
bucle:

```ts
while (true) {
    let scratch: byte[4096] = [];
    let line: String? = lines.readLine() in scratch;   // la línea vive en scratch, hasta el final de la vuelta
    if (line == null) { break; }
    ...
}
```

`readLine()` y `readInto()` se pueden mezclar: lo que quedó en el búfer después de una línea sale primero en
`readInto()`. Así se leen protocolos con cabeceras de texto y un cuerpo binario, como HTTP.

### `std.io.console`: la consola

`import std.io.console as Console;` da `Console.readLine(): String?` (una línea de la entrada estándar),
`Console.printError(text)` (una línea en la salida de errores) y tres streams: `Console.input` (un
`InputStream`), `Console.output` y `Console.error` (`OutputStream`). Para
protocolos con longitud (como el de `larimar lsp`): `Console.read(n)` (exactamente `n` bytes, menos solo si
la entrada se acaba; `Console.lastCount()` dice cuántos), `Console.write(text)` (sin salto de línea),
`Console.flush()` y `Console.binaryMode()` (en Windows, que `\n` no se convierta en `\r\n`).

Un `wc` (contar líneas, palabras y bytes), que sirve para un archivo o para la entrada estándar:

```ts
import std.io { IoError };
import std.io.files { open };
import std.io { InputStream, Reader };
import std.io.console as Console;

function count(input: InputStream, name: String): void throws IoError {
    let lines: int32 = 0;
    let words: int32 = 0;
    let bytes: int32 = 0;
    let text: Reader = { from: input };
    while (true) {
        let scratch: byte[4096] = [];
        let line: String? = text.readLine() in scratch;   // una línea a la vez, sin pedir memoria
        if (line == null) { break; }
        lines += 1;
        bytes += line.length + 1;
        let inWord: bool = false;
        for (b in line) {
            let space: bool = b == ' ' || b == '\t';
            if (!space && !inWord) { words += 1; }
            inWord = !space;
        }
    }
    println("${lines} ${words} ${bytes} ${name}");
}

function main(args: String[]): int32 {
    try {
        if (args.length == 0) {
            count(Console.input, "-");
        } else {
            count(open(args[0]), args[0]);             // el archivo se cierra al terminar la instrucción
        }
        return 0;
    } catch (IoError e) {
        Console.printError("cannot read ${args[0]}");
        return 1;
    }
}
```

### `std.io.path`: rutas

`import std.io.path as Paths;`. Las rutas que crean estas funciones viven donde diga quien llama, como lo
de cualquier función; aceptan `/` y `\`.

| Función | Ejemplo |
|---|---|
| `Paths.parent(p)` | `"a/b/c.lar"` → `"a/b"` (`""` si no hay carpeta) |
| `Paths.fileName(p)`, `Paths.stem(p)`, `Paths.extension(p)` | `"c.lar"`, `"c"`, `"lar"` |
| `Paths.join(dir, file)` | `"a/b"` + `"c.lar"` → `"a/b/c.lar"` (si `file` es absoluta, queda igual) |
| `Paths.isAbsolute(p)` | `"/x"`, `"C:/x"` y `"\\x"` lo son |
| `Paths.normalize(p)` | `"/x/./y/../z"` → `"/x/z"` |
| `Paths.absolute(p)` | normalizada y desde la carpeta actual si era relativa |
| `Paths.relative(base, p)` | `p` relativa a `base` si está dentro; si no, absoluta |

### `std.os`: el entorno

| Función | Qué hace |
|---|---|
| `os.env(name): String?` | una variable de entorno, o `null` |
| `os.cwd(): String` | la carpeta actual |
| `os.run(command): int32` | ejecuta un comando con el shell del sistema y da su código de salida |
| `os.programDir(): String` | la carpeta del ejecutable (`""` si no se puede saber) |
| `os.programPath(): String` | la ruta completa del ejecutable (`""` si no se puede saber) |
| `os.platform(): OS` | `OS.Linux`, `MacOS`, `Windows` o `Unix` (otro Unix): para un `switch` |
| `os.platformName(): String` | `"linux"`, `"macos"`, `"windows"` o `"unix"` |
| `os.exit(code)` | termina el programa ya (sin liberar memorias ni esperar hilos) |
| `os.catchTermination()` | desde ahí, Ctrl+C y SIGTERM no terminan el programa: ponen `os.terminating()` en `true` |
| `os.terminating(): bool` | si llegó Ctrl+C o SIGTERM después de `catchTermination()`; los servidores de `std.net` se detienen con él |

### `std.os.process`: otros programas

Lanza un programa y le habla por su entrada y su salida. El literal dice qué ejecutar (no puede fallar);
`start()` lo ejecuta. Cada lectura dice cuánto puede esperar, así que un programa que no responde nunca
deja colgado al que lo llama.

```ts
import std.os.process { Process, ProcessError, message };

function main(): int32 {
    let cat: Process = { program: "cat" };
    try {
        cat.start();
        cat.write("hola\n");
        println(cat.readLine(5000) ?? "nothing in 5 s");
        cat.closeInput();
        println("exit ${cat.wait(5000) ?? -1}");
    } catch (ProcessError e) {
        println(message(e));            // cannot start cat: not found
    }
    return 0;
}
```

| Del literal | Qué es |
|---|---|
| `program` | el programa: una ruta, o un nombre que se busca en el PATH |
| `args` | sus argumentos (cada uno llega tal cual, sin pasar por un shell) |
| `env` | `"NOMBRE=valor"` que se añaden al entorno de este programa para él |
| `quiet` | `true`: su salida de errores se descarta (si no, va a donde va la de este programa) |
| `mergeErrors` | `true`: su salida de errores llega junto con su salida, y se lee con ella |
| `shareConsole` | `true`: usa la consola de este programa (entrada, salida, errores); no se lee ni se escribe por el `Process` |

| Método | Qué hace |
|---|---|
| `start()` | lo ejecuta; `throws ProcessError.CannotStart` si no puede (no existe, sin permiso) |
| `write(text)` | escribe en su entrada; `throws ProcessError.NotRunning` si ya no la lee |
| `closeInput()` | cierra su entrada: lee el final (un `cat` termina) |
| `readLine(ms): String?` | la siguiente línea de su salida, sin el fin de línea; `null` si no llegó en `ms` o terminó |
| `read(count, ms): String?` | exactamente `count` bytes de su salida (`null` si no llegaron todos en `ms`) |
| `readAll(ms): String` | toda su salida hasta que termine (lo que llegó, si no terminó en `ms`) |
| `wait(ms): int32?` | espera hasta `ms` (`-1`: lo que haga falta) a que termine: su código de salida, o `null` |
| `kill()` | lo termina ya |

`findProgram(name): String?` dice dónde está un programa en el PATH. Un `Process` que sigue ejecutándose
cuando se libera su memoria se termina. Con `std.os.process` están escritas las pruebas que hablan con
`larimar lsp`, `larimar dap` y los depuradores.

### `std.text`: leer texto byte a byte

Para lexers y parsers: `text.isDigit(b)`, `isHexDigit`, `isLetter`, `isLetterOrDigit`,
`isIdentifierPart` (letra, dígito o `_`), `isSpace`, `isUpper`, `isLower` (todas ASCII),
`text.digitValue(b): int32?`, `text.isAscii(s)` y `text.fromCode(code): String` (el texto de un carácter
Unicode: `fromCode(241)` es `"ñ"`).

### `std.text.regex`: expresiones regulares

Escritas en Larimar, sin ninguna biblioteca de C: funcionan igual en todos los sistemas.

```ts
import std.text.regex { Regex, Match, RegexError, message };

let email: Regex = Regex.compile("([a-z]+)@([a-z]+)\\.com");      // RegexError si el patrón está mal
let m: Match? = email.find("escribe a ana@correo.com");
if (m != null) {
    println("${m.value} es de ${m.group(1) ?? ""}");                // ana@correo.com es de ana
}
let date: Regex = Regex.compile("(\\d{4})-(\\d{2})-(\\d{2})");
println(date.replace("2026-10-26", "$3/$2/$1"));                    // 26/10/2026
```

- **Qué ofrece:** `matches(text)` (el texto entero), `contains(text)`, `find(text): Match?`,
  `findAll(text): Match[*]`, `replace(text, reemplazo)` (`$0` es lo encontrado, `$1`..`$9` los grupos,
  `$$` un `$`) y `split(text)`.
- **Un `Match`** tiene `start` y `end` (bytes), `value`, y `group(i): String?` (`null` si el grupo no
  participó; `group(0)` es todo).
- **Lo que entiende un patrón:**
  - caracteres (`\.` para un signo tal cual, `\n`, `\t`) y `.` (cualquiera menos `\n`);
  - clases (`[abc]`, `[a-z]`, `[^0-9]`) y atajos (`\d`, `\w`, `\s` y sus contrarios `\D`, `\W`, `\S`);
  - anclas: `^`, `$`, `\b` y `\B`;
  - repeticiones `*`, `+`, `?`, `{n}`, `{n,}` y `{n,m}`; con `?` detrás toman lo menos posible;
  - grupos `(x)`, sin captura `(?:x)`, y alternativas `x|y`.
- **Las clases son ASCII.** Una letra con tilde cuenta como un carácter para `.` y `[^...]`, pero no
  está en `\w` ni puede escribirse dentro de `[...]`.
- **No se cuelga.** Cada posición del texto se prueba como mucho una vez por instrucción del patrón, así
  que patrones como `(a*)*b`, que en otros motores tardan una eternidad, aquí responden al momento.

### `std.net`: TCP

`TcpSocket.connect(host, port)` abre una conexión (con un nombre o una IP, v4 o v6) y
`TcpListener.bind(host, port)` espera conexiones (`"0.0.0.0"` para todas las direcciones; con el puerto 0
el sistema elige uno, y `port()` dice cuál). Un `TcpSocket` se usa directamente, como en C (`read(buffer)`,
`write(bytes)`, `writeText(text)`, `close()`), y además es un `InputStream` y un `OutputStream`: el `Reader`
lee líneas de él igual que de un archivo, y `copy()` envía cualquier stream por la red.

```ts
import std.net { TcpSocket, TcpListener, NetError, message };
import std.io { Reader };
import std.io { IoError };
import std.io.console as Console;

function main(): int32 {
    try {
        let server: TcpListener = TcpListener.bind("127.0.0.1", 8080);
        while (true) {
            let client: TcpSocket = server.accept();     // se cierra solo al final de la vuelta
            client.setTimeout(5000);
            try {
                let request: Reader = { from: client };
                while (true) {
                    let scratch: byte[4096] = [];
                    let line: String? = request.readLine() in scratch;   // sin malloc por línea
                    if (line == null || line! == "") { break; }          // fin de las cabeceras
                }
                client.writeText("HTTP/1.0 200 OK\r\nContent-Type: text/plain\r\n\r\nhola\n");
            } catch (IoError e) {}
        }
    } catch (NetError e) {
        Console.printError(message(e));
        return 1;
    }
    return 0;
}
```

- Los errores de conectar y escuchar son un `NetError`: `HostNotFound(host)`, `Refused`, `Timeout`,
  `Closed`, `Reset`, `AddressInUse`, `Other(code)`; `message(e)` da el texto. Leer y escribir lanzan
  `IoError`, como cualquier stream.
- Los sockets esperan (bloquean): `read` espera a que llegue algo y devuelve 0 cuando el otro lado cerró.
  `setTimeout(ms)` limita la espera de `read` y `write`.
- `finishWriting()` le dice al otro lado que ya no se escribirá más (lee el fin), pero se sigue pudiendo
  leer su respuesta.
- Un socket se cierra solo cuando se libera la memoria donde vive, así que uno aceptado en un bucle no
  queda abierto aunque no se llame a `close()`.
- `read` llena el búfer que recibe, sin crear nada; con el `Reader` y `readLine() in scratch`, leer un
  millón de líneas de un socket pidió al sistema unas 4.400 asignaciones de memoria en total.
- Para atender varias conexiones a la vez, `TcpServer` (abajo). En Windows (Winsock) `larimar build`
  enlaza `ws2_32` automáticamente.
- `Connection` es la interfaz de una conexión en los dos sentidos (`read`, `write`, `flush`, `close`): la
  implementa `TcpSocket`, y también lo que da un `TlsProvider` (ver `std.net.tls`). Quien habla un
  protocolo sobre una `Connection` no sabe si va cifrada.
- `handle()` da el socket del sistema (un `Socket`, el tipo de `std.net`), para una biblioteca de C que
  trabaje sobre una conexión ya abierta, como una de TLS: una función de C que recibe un `Socket` recibe el
  descriptor (un `SOCKET` en Windows). El socket sigue siendo del `TcpSocket`, y se cierra con él.
- `std.net` está escrito en Larimar sobre las funciones de sockets del sistema, sin `ccode`: es un buen
  ejemplo de [`when`](#cada-sistema-lo-suyo-when), [punteros](#punteros-de-c-t-y-) y
  [recursos](#recursos-released-by).
- `NetError.Tls(reason)` es un fallo del cifrado (un certificado rechazado, un saludo TLS fallido) y
  `NetError.TlsUnavailable(what)` que no hay TLS que usar.

### `std.net`: servidores TCP y UDP

`TcpServer` y `UdpServer` son el bucle de un servidor ya escrito: se configuran con un literal (que no
puede fallar) y `run()` hace el trabajo (escuchar puede fallar, y lanza `NetError`). Lo que se hace con
cada conexión o datagrama es una función `thread safe`, así que el compilador comprueba que los hilos del
servidor no se pisen.

```ts
import std.net { TcpServer, Connection, StopSignal, NetError, message };
import std.io { Reader, IoError };
import std.os;

synchronized class Stats {
    let served: int32 = 0;
    function add(): int32 { self.served += 1; return self.served; }
}

function main(): int32 {
    os.catchTermination();          // Ctrl+C y SIGTERM terminan run() en orden (systemd, docker stop)
    let stats: Stats = {};
    let quit: StopSignal = {};
    let server: TcpServer = {
        port: 8080,                 // host: "127.0.0.1" salvo que se diga otro ("0.0.0.0": toda la red)
        threads: 8,                 // conexiones atendidas a la vez (1 si no se dice)
        stop: quit,
        onConnect: (client: Connection) -> {
            try {
                let lines: Reader = { from: client.input() };
                let line: String = lines.readLine() ?? "";
                if (line == "quit") { quit.stop(); }
                client.writeText("hola #${stats.add()}: ${line}\n");
            } catch (IoError e) {}
        }                           // al volver, client se cierra y su memoria se libera
    };
    try {
        server.run();               // espera aquí hasta quit.stop(), Ctrl+C o SIGTERM
    } catch (NetError e) {
        println("no puedo escuchar: ${message(e)}");
        return 1;
    }
    return 0;
}
```

- `run()` acepta en el hilo que lo llama y reparte las conexiones entre sus `threads` hilos; cada
  conexión se atiende con su propia memoria, que se libera al terminar `onConnect`.
- `onConnect` recibe una `Connection`: `read`, `write`, `writeText`, `close`, e `input()`/`output()` para
  usarla como stream (`Reader { from: client.input() }`, `copy`). Con TLS es el mismo tipo.
- Un `StopSignal` es un objeto `synchronized` con `stop()`: se da al literal (`stop: quit`) y se llama
  desde cualquier sitio, el manejador incluido. El servidor lo nota en menos de una quinta de segundo y
  `run()` vuelve tras las peticiones en curso. Después de `os.catchTermination()`, Ctrl+C y SIGTERM hacen
  lo mismo. Sin ninguno de los dos, sirve hasta que termina el programa.

**Los límites.** Un servidor viene con los valores de servidores como nginx y Tomcat, para que un
cliente lento o malicioso no retenga sus hilos; un límite de `0` es ninguno:

| Campo | Por defecto | Qué limita |
|---|---|---|
| `readTimeout`, `writeTimeout` | 30000 ms | una lectura, una escritura |
| `requestTimeout` | 60000 ms | una llamada de `onConnect`, todas sus lecturas y escrituras juntas: un cliente que manda un byte cada vez queda cortado |
| `idleTimeout` | 75000 ms | cuánto espera una conexión mantenida (`keepAlive`) su siguiente petición |
| `maxQueue` | 100 | conexiones esperando un hilo libre; las demás se cierran en el acto |
| `handshakeTimeout` | 10000 ms | el *handshake* TLS |

Cuando se pasa un límite, la lectura o la escritura lanza `IoError.TimedOut`.

**Conexiones mantenidas.** Con `keepAlive: true`, la conexión no se cierra al volver `onConnect`: cuando
el cliente envía otra vez, `onConnect` se llama de nuevo con ella, y se termina con `client.close()`. Una
conexión normal que espera su siguiente petición no ocupa un hilo: el hilo de `run()` las vigila todas
con un `EventLoop` y solo da una a un hilo cuando tiene algo que leer. Así se atiende el *keep-alive* de
HTTP con pocos hilos. Cuando un cliente mantenido cierra, `onConnect` se llama una vez más y su primera
lectura da 0 (el `readLine` de un `Reader`, `null`): ciérrala entonces.

**`EventLoop`.** El bucle de `run()` también es una clase de `std.net`, para un servidor propio: vigila
sockets por su número (`TcpSocket.number()`, `TcpListener.number()`) y dice cuáles se pueden leer.

```ts
let listener: TcpListener = TcpListener.bind("127.0.0.1", 9000);
let loop: EventLoop = {};
loop.watch(listener.number());                         // lugar 0
while (true) {
    loop.wait(200);                                    // hasta que uno esté listo, 200 ms como mucho
    if (loop.isReady(0)) { ... listener.accept() ... }
    let i: int32 = loop.count() - 1;
    while (i >= 1) {                                   // desde el final: unwatch mueve el último a i
        if (loop.isReady(i) || loop.waited(i) > 30000) { ... loop.unwatch(i); }
        i -= 1;
    }
}
```

- `watch(n)` añade uno (queda el último), `unwatch(i)` saca el del lugar `i` (el último ocupa su lugar),
  `socket(i)` es su número y `waited(i)` los ms desde que se vigila.
- `wait(ms)` da cuántos están listos (0 si pasó el tiempo). Listo también es cerrado por el otro lado: la
  lectura da entonces 0.
- Usa `poll` (`WSAPoll` en Windows), que basta para miles de conexiones; epoll (Linux) y kqueue (macOS)
  serían su siguiente paso, con los mismos métodos.

**HTTPS.** Con `tls`, el mismo servidor es https: las conexiones llegan a `onConnect` ya descifradas. El
certificado y su clave se cargan una vez con `OpenSslProvider.load(certificado, clave)`, que lanza
`NetError` si un archivo no se puede usar o la clave no es la del certificado:

```ts
let server: TcpServer = {
    host: "0.0.0.0", port: 443, threads: 16, keepAlive: true,
    tls: OpenSslProvider.load("/etc/letsencrypt/live/example.com/fullchain.pem",
                              "/etc/letsencrypt/live/example.com/privkey.pem"),
    onConnect: (client: Connection) -> { ... }       // el mismo manejador que en HTTP normal
};
```

- Con Let's Encrypt se usan `fullchain.pem` (el certificado con su cadena) y `privkey.pem`. Ese archivo
  solo lo lee root: el programa necesita permiso para leerlo. Cuando el certificado se renueva, hay que
  reiniciar el servidor.
- El *handshake* ocurre en el hilo que atiende, con `handshakeTimeout`: un cliente que no lo completa, o
  que no habla TLS, se descarta sin llegar a `onConnect`.
- Una conexión TLS mantenida conserva su hilo mientras espera su siguiente petición (hasta `idleTimeout`).
- Un `OpenSslProvider` es `synchronized`: lo comparten los hilos del servidor, y también varios servidores.
- Usa OpenSSL 1.1 o 3, cargado la primera vez que hace falta: en Linux viene con el sistema; en macOS,
  `brew install openssl@3`. En Windows aún no está: `load` lanza `NetError.TlsUnavailable`.

`UdpSocket` envía y recibe datagramas: cada uno llega entero o no llega, sin conexión.
`UdpSocket.bind(host, port)` recibe en un puerto y `UdpSocket.open()` da uno cualquiera para enviar;
`sendTo(bytes, Address { host, port })` envía y `receive(buffer)` espera uno y da un `Datagram`
(`length` y `from`, la `Address` de quien lo envió). `UdpServer` es su servidor:

```ts
let server: UdpServer = {
    port: 9000,
    threads: 4,
    stop: quit,
    onReceive: (socket: UdpSocket, data: byte[], from: Address) -> {
        try { socket.sendTo(data, from); } catch (NetError e) {}       // el eco
    }
};
server.run();
```

- Cada hilo tiene su propia copia del socket, en el mismo puerto: las respuestas salen del puerto al que
  escribió el cliente.
- `maxSize` (65507 si no se dice) es el datagrama más grande que se recibe entero.
- UDP no reenvía: un datagrama puede perderse, y quien envía decide si lo repite.

### `std.net.http`: cliente HTTP y HTTPS

Un `Client` dice **cómo conectarse** (TLS, tiempos de espera, redirecciones, cabeceras de todas las
peticiones) y una `Request` **qué pedir**. `send` lee la línea de estado y las cabeceras; el cuerpo se lee
cuando se pide: entero con `text()`, `bytes()` o `json()` (con `std.encoding.json`), o por partes desde `body`, que es
un `InputStream` (sirven `Reader` y `copy()`).

```ts
import std.net.http { Client, Response, Header, HttpError, message };
import std.io.files { create };
import std.io { copy };
import std.io { IoError };

function main(): int32 {
    let api: Client = {
        timeout: 10000,
        headers: [Header { name: "Authorization", value: "Bearer abc" }]     // van en todas las peticiones
    };
    try {
        let r: Response = api.get("https://api.example.com/users/7");
        if (!r.ok()) {
            println("status ${r.status} ${r.reason}");      // un 404 es una respuesta, no un error
            return 1;
        }
        let user: Any = r.json();
        println("${user.name} (${r.header("Content-Type") ?? "?"})");

        let saved: Response = api.send({                    // la Request, como literal
            method: "POST",
            url: "https://api.example.com/users",
            headers: [Header { name: "Content-Type", value: "application/json" }],
            body: "{\"name\": \"Ana\"}"
        });
        println("created: ${saved.status}");

        let big: Response = api.send({ url: "https://mirror.example.com/disk.iso", timeout: 0 });
        copy(big.body, create("disk.iso"));                 // 4 KB a la vez: nunca entero en memoria
    } catch (HttpError e) {
        println(message(e));
        return 1;
    } catch (IoError e) {
        println("disk.iso: io");
        return 1;
    }
    return 0;
}
```

- `Client`: todos sus campos tienen valor por defecto, así que `Client {}` ya habla `http://` y `https://`.
  `tls` (un `TlsProvider`; por defecto `SystemTls {}`), `timeout` en ms (30000; 0 sin límite),
  `maxRedirects` (5; 0 no las sigue) y `headers` (se envían en todas, antes de las de la petición). Métodos:
  `send(request)`, `get(url)` y `post(url, body, contentType)`.
- `Request`: solo `url` es obligatoria (`{ url: "..." }` es un GET). Además `method`, `headers` (un arreglo
  de `Header { name, value }`: conserva el orden y admite repetidas), `body` (texto, enviado con su
  `Content-Length`) y `timeout` (-1, el del cliente).
- `get(url)`, `post(url, body, contentType)` y `send(request)` sueltas usan un `Client {}`: sirven para
  scripts y pruebas.
- `Response`: `status`, `reason`, `headers`, `url` (la última, después de las redirecciones), `ok()`
  (200 a 299), `header(name)` (sin distinguir mayúsculas), `body`, `text()`, `bytes()`, `json()` y `close()`.
- **`HttpError` es que no hubo respuesta**: `Net(reason)` (no conectó, se cortó, tardó demasiado, o el TLS
  falló: `"network: tls: certificate rejected: ..."`), `BadResponse(reason)` (el servidor no habla HTTP, o
  `json()` de algo que no es JSON), `TooManyRedirects`, `BadUrl(url)` y `Unsupported(what)`: `https://`
  cuando no hay TLS que usar. Un 404 o un 500 son respuestas: se miran con `status` u `ok()`.
- El cuerpo termina donde termina, sea por `Content-Length`, por `chunked` o porque el servidor cierra; quien
  lee no ve la diferencia. Las redirecciones 301, 302 y 303 pasan a GET sin cuerpo; 307 y 308 repiten el
  método. Una redirección de `http://` a `https://` usa el `TlsProvider` del cliente.
- **Memoria**: la respuesta, sus cabeceras y su conexión viven donde diga quien llama, y la conexión se
  cierra sola cuando se libera esa memoria. Con `api.get(url) in scratch` dentro de un bucle, 3.000
  peticiones se mantuvieron en 2 MB de memoria, sin dejar conexiones abiertas. La respuesta puede apuntar al
  cliente (a su `TlsProvider`), así que el cliente debe vivir al menos tanto como ella.
- Cada petición abre su conexión (`Connection: close`). **Todo espera** (bloquea) y no hay hilos por
  dentro. Un `Client` no se comparte entre hilos: cada hilo crea el suyo.

#### Peticiones en paralelo

Si hacen falta varias a la vez, cada una va en un `Thread` (no hay `sendAsync`: así se ve dónde corre cada
una, dónde vive su respuesta y cuándo se espera):

```ts
import std.net.http { get, HttpError, message };

synchronized class Results {
    let lines: String[*] = [];
    function add(line: String): void { self.lines.push(line.clone()); }
    function all(): String { return self.lines.join("\n"); }
}

function main(): int32 {
    let paths: String[] = ["/a", "/b", "/c"];
    let shared: byte[*] = [] in heap;
    let results: Results = {} in shared;
    {
        let threads: byte[*] = [] in heap;
        for (path in paths) {
            let url: String = "http://127.0.0.1:8080${path}" in threads;   // vive tanto como los hilos
            let t: Thread = {
                run: () -> {
                    try { results.add("${url}: ${get(url).text().length} bytes"); }
                    catch (HttpError e) { results.add("${url}: ${message(e)}"); }
                }
            } in threads;
            t.start();
        }
    }   // aquí espera a los tres hilos
    println(results.all());
    return 0;
}
```

### `std.net.tls`: conexiones cifradas

`https://` no sabe nada de cifrado: le pide a un **`TlsProvider`** una conexión cifrada y habla HTTP sobre
ella. La interfaz es una sola función:

```ts
public interface TlsProvider {
    /** An encrypted connection to host:port, after the TLS handshake. timeout: for reads and writes, in ms. */
    function connect(host: String, port: int32, timeout: int32): Connection throws NetError;
}
```

**`SystemTls`** es la que trae Larimar, y la que usa un `Client` si no se le da otra. Usa lo que ya tiene el
sistema:

| Sistema | Usa | Certificados de confianza |
|---|---|---|
| macOS | Network.framework (viene con el sistema) | los del Llavero, como Safari |
| Windows | SChannel (viene con el sistema) | los del almacén de Windows |
| Linux y otros | OpenSSL (`libssl.so.3` o `libssl.so.1.1`), cargada la primera vez que se usa | los del sistema (`/etc/ssl/certs`) |

- Comprueba el certificado del servidor y que sea para ese nombre. `SystemTls { verify: false }` acepta
  cualquiera: solo para probar contra un servidor local con un certificado propio.
- Un programa que nunca abre `https://` no carga nada, y para compilar no hacen falta cabeceras ni
  bibliotecas de OpenSSL: `larimar build` enlaza lo necesario (`-framework Network -framework Security` en
  macOS, `secur32` en Windows, `-ldl` en Linux).
- Si en el sistema no hay TLS (un Linux sin OpenSSL), la petición da
  `HttpError.Unsupported("https: OpenSSL not found (tried libssl.so.3, libssl.so.1.1, libssl.so)")`: el
  mensaje dice qué falta.
- En Windows, SChannel negocia TLS 1.2 (TLS 1.3 con SChannel necesita otra API, aún no usada aquí).

#### Un TLS propio: mbedTLS

Para usar otra biblioteca (para llevar el TLS dentro del ejecutable, por ejemplo), se implementa
`TlsProvider` y se le da al cliente: `Client { tls: MbedTls {} }`. Un ejemplo completo con
[mbedTLS](https://github.com/Mbed-TLS/mbedtls) 3.6, que es C puro y se compila con `make`:

```
secure/
├── larimar.toml
├── mbedtls/          # el código de mbedTLS (de su página de versiones), compilado con: make lib
└── src/
    ├── main.lar
    └── mbed.lar      # el TlsProvider
```

```toml
[project]
name = "secure"

[c]
include_paths = ["mbedtls/include"]
static_library_paths = ["mbedtls/library"]
static_libraries = ["mbedtls", "mbedx509", "mbedcrypto"]     # en este orden
```

`src/mbed.lar` tiene dos partes: el C que llama a mbedTLS (en un `ccode`) y las dos clases que implementan
las interfaces. La sesión de mbedTLS es un **recurso**: C la crea con `malloc`, y Larimar la suelta con
`mbed_free` cuando se libera la memoria de la conexión (`released by`), así que el C no necesita saber nada
de las memorias de Larimar:

```ts
import std.net { Connection, TcpSocket, NetError, Socket };
import std.net.tls { TlsProvider };
import std.io { IoError, InputStream, OutputStream };

ccode {
    #include <stdlib.h>
    #include <mbedtls/ssl.h>
    #include <mbedtls/net_sockets.h>
    #include <mbedtls/entropy.h>
    #include <mbedtls/ctr_drbg.h>
    #include <mbedtls/error.h>
    #include <psa/crypto.h>

    typedef struct {
        int error;                      /* 0: fine */
        char text[200];
        int open;
        mbedtls_net_context net;        /* only its fd: the socket belongs to the TcpSocket */
        mbedtls_ssl_context ssl;
        mbedtls_ssl_config conf;
        mbedtls_x509_crt ca;
        mbedtls_entropy_context entropy;
        mbedtls_ctr_drbg_context drbg;
    } MbedConn;

    static void mbed_fail(MbedConn* c, const char* what, int code) {
        char why[150];
        mbedtls_strerror(code, why, sizeof why);
        snprintf(c->text, sizeof c->text, "%s: %s", what, why);
        c->error = 1;
    }

    /* Larimar releases it (released by mbed_free) when the memory of the connection is freed */
    static void mbed_free(MbedConn* c) {
        if (c->open) mbedtls_ssl_close_notify(&c->ssl);
        mbedtls_ssl_free(&c->ssl);
        mbedtls_ssl_config_free(&c->conf);
        mbedtls_x509_crt_free(&c->ca);
        mbedtls_ctr_drbg_free(&c->drbg);
        mbedtls_entropy_free(&c->entropy);
        free(c);
    }

    static MbedConn* mbed_open(int fd, const char* host, const char* caFile, bool verify) {
        MbedConn* c = (MbedConn*)calloc(1, sizeof(MbedConn));
        if (!c) return NULL;
        mbedtls_ssl_init(&c->ssl);
        mbedtls_ssl_config_init(&c->conf);
        mbedtls_x509_crt_init(&c->ca);
        mbedtls_entropy_init(&c->entropy);
        mbedtls_ctr_drbg_init(&c->drbg);
        psa_crypto_init();
        int r = mbedtls_ctr_drbg_seed(&c->drbg, mbedtls_entropy_func, &c->entropy, NULL, 0);
        if (r != 0) { mbed_fail(c, "random", r); return c; }
        if (verify && (r = mbedtls_x509_crt_parse_file(&c->ca, caFile)) < 0) { mbed_fail(c, caFile, r); return c; }
        r = mbedtls_ssl_config_defaults(&c->conf, MBEDTLS_SSL_IS_CLIENT, MBEDTLS_SSL_TRANSPORT_STREAM, MBEDTLS_SSL_PRESET_DEFAULT);
        if (r != 0) { mbed_fail(c, "config", r); return c; }
        mbedtls_ssl_conf_authmode(&c->conf, verify ? MBEDTLS_SSL_VERIFY_REQUIRED : MBEDTLS_SSL_VERIFY_NONE);
        mbedtls_ssl_conf_ca_chain(&c->conf, &c->ca, NULL);
        mbedtls_ssl_conf_rng(&c->conf, mbedtls_ctr_drbg_random, &c->drbg);
        if ((r = mbedtls_ssl_setup(&c->ssl, &c->conf)) != 0) { mbed_fail(c, "setup", r); return c; }
        if ((r = mbedtls_ssl_set_hostname(&c->ssl, host)) != 0) { mbed_fail(c, "host", r); return c; }
        c->net.fd = fd;
        mbedtls_ssl_set_bio(&c->ssl, &c->net, mbedtls_net_send, mbedtls_net_recv, NULL);
        while ((r = mbedtls_ssl_handshake(&c->ssl)) != 0) {
            if (r != MBEDTLS_ERR_SSL_WANT_READ && r != MBEDTLS_ERR_SSL_WANT_WRITE) { mbed_fail(c, "handshake", r); return c; }
        }
        c->open = 1;
        return c;
    }

    static int32_t mbed_read(MbedConn* c, uint8_t* items, int32_t len) {
        while (c->open) {
            int r = mbedtls_ssl_read(&c->ssl, items, (size_t)len);
            if (r > 0) return r;
            if (r == 0 || r == MBEDTLS_ERR_SSL_PEER_CLOSE_NOTIFY) break;           /* the end */
    #ifdef MBEDTLS_ERR_SSL_RECEIVED_NEW_SESSION_TICKET
            if (r == MBEDTLS_ERR_SSL_RECEIVED_NEW_SESSION_TICKET) continue;          /* TLS 1.3: not data */
    #endif
            mbed_fail(c, "read", r);
            return -1;
        }
        c->open = 0;
        return 0;
    }

    static int32_t mbed_write(MbedConn* c, const uint8_t* items, int32_t len) {
        int32_t done = 0;
        while (done < len) {
            int r = mbedtls_ssl_write(&c->ssl, items + done, (size_t)(len - done));
            if (r <= 0) { mbed_fail(c, "write", r); return -1; }
            done += r;
        }
        return 0;
    }

    static int32_t mbed_error(MbedConn* c) { return c->error; }
    static const char* mbed_error_text(MbedConn* c) { return c->text; }
}

native type MbedHandle released by mbed_free;
native function mbed_open(s: Socket, host: String, caFile: String, verify: bool): MbedHandle?;
native function mbed_free(c: MbedHandle): void;
native function mbed_read(c: MbedHandle, buffer: byte[]): int32;
native function mbed_write(c: MbedHandle, bytes: byte[]): int32;
native function mbed_error(c: MbedHandle): int32;
native function mbed_error_text(c: MbedHandle): String;

/** https:// with mbedTLS. caFile: the trusted certificates, in PEM. */
public class MbedTls implements TlsProvider {
    let caFile: String = "/etc/ssl/certs/ca-certificates.crt";     // Debian/Ubuntu; macOS: /etc/ssl/cert.pem
    let verify: bool = true;

    function connect(host: String, port: int32, timeout: int32): Connection throws NetError {
        let c: MbedConnection = {};                   // what is returned: created where the caller says
        c.tcp = TcpSocket.connect(host, port);        // ...and these, in c's memory
        c.tcp!.setTimeout(timeout);
        c.tls = mbed_open(c.tcp!.handle()!, host, self.caFile, self.verify);
        if (c.tls == null) { throw NetError.Tls("out of memory"); }
        if (mbed_error(c.tls!) != 0) { throw NetError.Tls(mbed_error_text(c.tls!).clone()); }
        return c;
    }
}

/** The TLS session over its TcpSocket. */
class MbedConnection implements Connection, InputStream, OutputStream {
    let tcp: TcpSocket? = null;
    let tls: MbedHandle? = null;

    function read(buffer: byte[]): int32 throws IoError {
        let n: int32 = mbed_read(self.tls!, buffer);
        if (n < 0) { throw IoError.Failed("mbedtls: ${mbed_error_text(self.tls!)}"); }
        return n;
    }

    function write(bytes: byte[]): void throws IoError {
        if (mbed_write(self.tls!, bytes) < 0) { throw IoError.Failed("mbedtls: ${mbed_error_text(self.tls!)}"); }
    }

    function writeText(text: String): void throws IoError { self.write(text.bytes()); }
    function input(): InputStream { return self; }
    function output(): OutputStream { return self; }
    function flush(): void throws IoError {}

    function close(): void throws IoError {
        release(self.tls);                            // the session first, then its socket
        self.tcp!.close();
    }
}
```

Y `src/main.lar` lo usa como cualquier otro:

```ts
import std.net.http { Client, Response, HttpError, message };
import mbed { MbedTls };

function main(args: String[]): int32 {
    let client: Client = { tls: MbedTls {} };
    try {
        let r: Response = client.get(args.length > 0 ? args[0] : "https://github.com/");
        println("${r.status} ${r.header("Content-Type") ?? ""}");
    } catch (HttpError e) {
        println(message(e));
        return 1;
    }
    return 0;
}
```

```
$ larimar run
200 text/html; charset=utf-8
```

- Las piezas son las mismas que en cualquier `TlsProvider`: abrir el `TcpSocket`, hacer el saludo TLS sobre
  su socket (`handle()`: C recibe el descriptor) y devolver un objeto que implementa `Connection`. Lo que
  devuelve `connect` se crea donde dice quien llama (la respuesta HTTP), y con él la sesión, que se suelta
  sola (`released by mbed_free`).
- Con `MbedTls { caFile: "mi-ca.pem" }` se confía en un certificado propio (un servidor de pruebas, una red
  interna) sin desactivar la verificación.
- mbedTLS va dentro del ejecutable (bibliotecas estáticas): el programa no depende de lo que tenga el
  sistema. A cambio, actualizar mbedTLS cuando salga un fallo de seguridad es trabajo de quien lo usa.

### `std.encoding.json`: JSON

`Json.parse(text): Any throws JsonError` convierte un texto JSON en un `Any`: un objeto es una tabla con
nombres, un arreglo una tabla por posiciones, los números enteros que caben son `int64` y los demás
`float64`. `Json.stringify(v)` hace lo contrario (una tabla vacía se escribe `{}`), y `Json.quote(s)` da
un `String` como cadena JSON, con sus comillas y escapes.

```ts
import std.encoding.json as Json;
import std.encoding.json { JsonError };

function main(): int32 {
    try {
        let config: Any = Json.parse("{\"port\": 8080, \"names\": [\"a\", \"b\"], \"debug\": true}");
        println("port ${config.port as int64 ?? 80}, ${config.names.length} names");
        println(Json.stringify({ ok: true, list: { 1, 2, 3 }, name: "x\ty" }));
        Json.parse("[1, 2");
    } catch (JsonError e) {
        switch (e) {
            case Invalid { at, why } -> println("invalid JSON at ${at}: ${why}");
        }
    }
    return 0;
}
```

Salida:

```
port 8080, 2 names
{"ok":true,"list":[1,2,3],"name":"x\ty"}
invalid JSON at 5: expected ',' or ']'
```

### `std.encoding.toml`: TOML

`Toml.parse(text): Any` (`throws TomlError`) y `Toml.stringify(table): String`, como `std.encoding.json`. Cubre lo
que usan los archivos de configuración: `[secciones]` (también `[a.b]`, una tabla dentro de otra),
`clave = valor` con textos, números enteros, `true`/`false` y listas (que pueden ocupar varias líneas), y
comentarios con `#`. Es el mismo lector que usa el compilador para `larimar.toml`.

```ts
import std.encoding.toml as Toml;
import std.encoding.toml { TomlError, message };

function main(): int32 {
    try {
        let config: Any = Toml.parse("[project]\nname = \"demo\"\n[c]\nflags = [\"-O2\", \"-Wall\"]\n");
        println("${config.project.name} ${config.c.flags.length}");
        println(Toml.stringify({ server: { port: 8080, hosts: { "a", "b" } } }));
        Toml.parse("[a]\nnada\n");
    } catch (TomlError e) {
        println(message(e));
    }
    return 0;
}
```

Salida:
```
demo 2
[server]
port = 8080
hosts = ["a", "b"]

line 2: Expected key = value
```

Una sección es una tabla con nombres y una lista, una tabla por posición; el orden del archivo se
conserva. Una clave que se llama como una palabra de Larimar se lee con corchetes, como `length` o `push`:
`config.options["default"]`. `stringify` escribe un archivo nuevo: no conserva los comentarios de uno que se leyó.

---

### `std.time`: el reloj y las fechas

```ts
import std.time as Time;

let started: int64 = Time.monotonic();
Time.sleep(250);
println("${Time.monotonic() - started} ms");          // unos 250
println(Time.httpDate(Time.now()));                    // Mon, 02 Nov 2026 23:04:00 GMT
println(Time.isoDate(Time.now()));                     // 2026-11-02T23:04:00Z
```

| Función | Qué hace |
|---|---|
| `Time.now(): int64` | milisegundos desde 1970 (UTC): el reloj de pared, que puede saltar si se cambia la hora del sistema |
| `Time.monotonic(): int64` | milisegundos que solo avanzan: para medir tiempo y para plazos |
| `Time.sleep(ms)` | espera, en este hilo |
| `Time.fromMillis(ms): DateTime` | las partes de un momento (`year`, `month`, `day`, `hour`, `minute`, `second`, `millisecond`, `weekday`), UTC |
| `Time.toMillis(t)` | de vuelta a milisegundos |
| `Time.httpDate(ms)` | la fecha de HTTP (`Date`, `Last-Modified`, el `Expires` de una cookie) |
| `Time.isoDate(ms)`, `Time.parseIsoDate(text): int64?` | ISO 8601 en UTC, y de vuelta |

### `std.crypto`: hashes y bytes aleatorios

Escrito en Larimar; solo los bytes aleatorios vienen del sistema (`/dev/urandom`, `arc4random`, `RtlGenRandom`).

| Función | Qué da |
|---|---|
| `Crypto.sha256(bytes): byte[*]` | el SHA-256 (32 bytes) |
| `Crypto.sha1(bytes): byte[*]` | el SHA-1 (20 bytes): roto para firmas, solo para protocolos que lo piden (WebSocket) |
| `Crypto.hmacSha256(key, bytes): byte[*]` | una firma con una clave: para cookies y tokens firmados |
| `Crypto.randomBytes(n): byte[*]` | bytes aleatorios seguros: para IDs de sesión, tokens CSRF, sales |
| `Crypto.sameBytes(a, b): bool` | compara en el mismo tiempo donde sea que difieran: para comprobar firmas |

```ts
import std.crypto as Crypto;
import std.encoding.hex as Hex;
import std.encoding.base64 as Base64;

println(Hex.encode(Crypto.sha256("hola".bytes())));            // b221d9db...
let session: String = Base64.encodeUrl(Crypto.randomBytes(32));
```

### `std.encoding.base64`, `hex` y `url`

| Función | Qué hace |
|---|---|
| `Base64.encode(bytes)`, `Base64.decode(text): byte[*]?` | base64 con `+` y `/`, rellenado con `=` (RFC 4648) |
| `Base64.encodeUrl(bytes)`, `Base64.decodeUrl(text)` | base64 para URLs, nombres de archivo y cookies: `-` y `_`, sin `=` |
| `Hex.encode(bytes)`, `Hex.decode(text): byte[*]?` | dos dígitos hex por byte |
| `Url.encode(text)`, `Url.decode(text): String?` | codificación de URL: todo salvo letras, dígitos y `- _ . ~` como `%XX` |
| `Url.parseQuery("a=1&b=dos+palabras"): Any` | una *query string* (o un formulario) como tabla de textos; `+` es un espacio |
| `Url.query(tabla): String` | una *query string* con las entradas con nombre de una tabla |

Un decodificador da `null` cuando el texto no es válido, en lugar de lanzar: qué hacer entonces lo decide quien llama.

## 26. Proyectos: `larimar.toml` y `larimar build`

Un proyecto es una carpeta con un archivo `larimar.toml`. **TOML** es un formato de texto para
configuraciones: cada línea es `clave = valor` (los textos entre comillas, las listas entre `[ ]`), las
líneas que siguen a un título entre corchetes como `[project]` pertenecen a esa **sección**, y `#`
empieza un comentario. El que crea `larimar new` basta para empezar:

```toml
[project]
name = "hello"
version = "0.1.0"
main = "src/main.lar"

[c]
flags = ["-O2"]
dynamic_libraries = []
```

`[project]` dice cómo se llama el programa y dónde empieza; `[c]` dice cómo se compila el C. Todas las claves:

```toml
[project]
name = "melody"              # obligatorio: nombre del ejecutable
version = "0.1.0"
kind = "program"             # por defecto; "library" construye una biblioteca (ver Bibliotecas escritas en Larimar)
main = "src/main.lar"        # por defecto; su carpeta es la raíz de los módulos
output = "dist/melody"       # por defecto build/<name> (build/<name>.exe en Windows; una biblioteca: la carpeta build/<name>)

[library]                    # solo con kind = "library"
type = "static"              # por defecto; o "dynamic"
prefix = "mel"               # con qué empiezan sus nombres de C: mel_play (por defecto, el nombre)

[c]
compiler = "gcc"             # por defecto el del sistema (cc, gcc, clang) o el tcc incluido
flags = ["-O2", "-Wall"]     # por defecto ["-O2"]
sources = ["csrc/helpers.c"] # archivos C propios que se compilan junto al programa
include_paths = ["include"]  # carpetas de cabeceras (-I)
static_libraries = ["tone"]          # lib<name>.a: dentro del ejecutable
static_library_paths = ["vendor/lib"]    # dónde están
dynamic_libraries = ["user32", "m"]  # -l<name>: user32.dll, libm.so; se cargan al arrancar
dynamic_library_paths = ["libs"]     # dónde están (-L), y dónde las busca el ejecutable
```

Las rutas son relativas a la carpeta del proyecto. Una clave o sección desconocida es un error, para
que una errata no pase desapercibida.

**Dependencias.** `[dependencies]` nombra las bibliotecas que usa el proyecto y sus versiones:

```toml
[dependencies]
sql = "github.com/zerh/sql@v1.2.0"
```

Un gestor de dependencias (Minero, con `larimar add` y `larimar fetch`) baja cada una a `deps/<nombre>/`.
El compilador solo lee los nombres, y hace tres cosas con ellos:

- **Un import busca también en las dependencias**: cuando `import sql.core;` no está en `src/`, se busca en
  `deps/*/src/` (`deps/sql/src/sql/core.lar`). Un módulo que está en dos dependencias es un error que nombra las dos.
- **El C de cada dependencia se suma al del proyecto**: las `static_libraries`, `dynamic_libraries`, sus
  rutas, `include_paths` y `sources` de `deps/<nombre>/larimar.toml` (su `[c]` y las secciones de su plataforma), con sus rutas
  relativas a la carpeta de la dependencia.
- **Una dependencia que no está en `deps/` es un error**: `'sql' is in [dependencies] but not in deps/: get it with 'larimar fetch' (Minero)`.

**Por plataforma.** `[c.linux]`, `[c.macos]`, `[c.windows]` y `[c.unix]` (Linux y macOS) llevan las mismas
claves que `[c]` y solo cuentan en esa plataforma: sus listas se suman a las de `[c]`, y un `compiler` ahí
reemplaza al de `[c]`. Los nombres son los mismos que en `#when`.

```toml
[c]
sources = ["c/common.c"]

[c.linux]
dynamic_libraries = ["SDL3", "m"]

[c.windows]
dynamic_libraries = ["SDL3", "ws2_32"]
```

| Comando | Qué hace |
|---|---|
| `larimar new <name>` | crea la carpeta con `larimar.toml`, `src/main.lar` y `.gitignore` |
| `larimar new <name> --library` | lo mismo para una biblioteca: `src/<name>.lar` con una export function, y su prueba |
| `larimar build [carpeta]` | escribe `build/<name>.c` y lo compila al ejecutable (una biblioteca: `build/<name>/`) |
| `larimar build --static`, `--dynamic` | una biblioteca de ese tipo, en lugar del de `[library]` |
| `larimar build --debug` | lo mismo, para un depurador (ver [Depurar](#depurar-larimar-build---debug-y-larimar-dap)) |
| `larimar run [carpeta] [-- args]` | compila y ejecuta, pasándole los argumentos |
| `larimar build --cc <programa>` | compila con ese compilador de C en lugar del del proyecto (`tcc`: el incluido) |
| `larimar test [archivo o carpeta]` | ejecuta las pruebas (ver [Pruebas](#pruebas-test-function-y-larimar-test)) |
| `larimar <comando de un plugin>` | ejecuta el programa de un plugin (ver [Plugins](#plugins-comandos-de-otros-programas)) |
| `larimar check [archivo o carpeta] [--json]` | busca los errores sin generar C (ver [El editor](#el-editor-larimar-check-y-larimar-lsp)) |
| `larimar lsp` | el servidor de lenguaje para editores |
| `larimar dap` | el depurador para editores (sobre `lldb-dap`) |
| `larimar <archivo.lar> [args]` | compila un archivo (primero con el tcc incluido) y lo ejecuta con los argumentos |
| `larimar <archivo.lar> -o <salida.c>` | escribe el C generado de un archivo |
| `larimar c <archivo.lar>` | muestra el C generado de un archivo (con sus módulos) |

### Bibliotecas de C: estáticas, dinámicas y código fuente

Un programa de Larimar puede usar cualquier biblioteca de C. Se declaran sus funciones con
`native function` (y sus tipos con `native type`) y el `larimar.toml` le dice al compilador de C dónde
está. Hay cinco formas de traer una biblioteca, según cómo venga:

| Cómo viene | En `[c]` | Resultado |
|---|---|---|
| **Código fuente** (`.c`), como SQLite o raygui | `sources = ["vendor/sqlite3.c"]` | se compila junto al programa: queda dentro del ejecutable |
| **Biblioteca estática** (`.a`) | `static_libraries = ["sqlite3"]` y `static_library_paths = ["vendor/lib"]` | queda dentro del ejecutable, aunque haya una dinámica al lado |
| **Biblioteca dinámica propia** (`.so`, `.dylib`, `.dll`) | `dynamic_libraries = ["tone"]` y `dynamic_library_paths = ["vendor/lib"]` | el ejecutable la carga al arrancar, desde esa carpeta |
| **Biblioteca del sistema** (`m`, `pthread`, `user32`, una instalada con el gestor de paquetes) | `dynamic_libraries = ["m"]` y, si hace falta, `include_paths` | el ejecutable la carga del sistema |
| **Biblioteca escrita en Larimar** (con su `.interface`) | una de las dos de arriba, con su carpeta | ver [Bibliotecas escritas en Larimar](#27-bibliotecas-escritas-en-larimar) |

Un ejemplo con cuatro a la vez:

```toml
[c]
include_paths = ["vendor/include"]           # los .h (-I)
sources = ["vendor/src/embedded.c"]          # código fuente: va dentro del ejecutable
static_libraries = ["mylib"]                 # vendor/lib/libmylib.a: dentro del ejecutable
static_library_paths = ["vendor/lib"]
dynamic_libraries = ["tone", "m"]            # vendor/lib/libtone.so, y la libm del sistema
dynamic_library_paths = ["vendor/lib"]
```

```ts
cinclude "vendor.h";
cinclude "<math.h>";

native function mylib_triple(x: int32): int32;     // de libmylib.a
native function tone_play(hz: int32): void;        // de libtone.so
native function embedded_add(a: int32, b: int32): int32;   // de embedded.c
native function sqrt(x: float64): float64;         // de libm
```

**La clave dice estática o dinámica.** Un nombre en `static_libraries` es el archivo `lib<name>.a` de una
de las `static_library_paths`: el compilador le da al enlazador ese archivo, así que va dentro del
ejecutable aunque haya una dinámica en la misma carpeta. Si no está en ninguna, en Linux se busca entre
las del sistema (`-Wl,-Bstatic -l<name>`); en los demás es un error que lo dice. Un nombre en
`dynamic_libraries` es `-l<name>`, que se busca en `dynamic_library_paths` (`-L`) y en las carpetas del
sistema. Un nombre no puede estar en las dos.

Antes de la 1.3 había una sola `libraries` (y `library_paths`), y elegía el enlazador: prefería la
dinámica cuando encontraba las dos, así que lo que quedaba en el ejecutable dependía de lo que tuviera
cada máquina. Ahora cada biblioteca es una cosa o la otra, y `libraries` o `library_paths` es un error que
dice qué clave usar.

Lo estático y el código fuente son lo más portátil: el ejecutable es un solo archivo, sin nada que copiar
ni instalar.

**Cuándo se busca cada una.** Una biblioteca dinámica se busca dos veces, en momentos distintos:

1. **Al compilar.** El compilador de C la busca en sus propias carpetas (MinGW trae las de Windows, como
   `user32`) y en `dynamic_library_paths` (`-L`).
2. **Al ejecutar.** El sistema operativo carga el archivo (`.dll`, `.so`, `.dylib`). Si no lo encuentra, el
   programa no arranca.

Por eso `larimar build` **no copia ninguna biblioteca dinámica**. Se quedan donde están:

- **Las del sistema** las busca el ejecutable en las rutas normales del sistema, y la máquina donde se
  ejecute debe tenerlas instaladas.
- **Las de `dynamic_library_paths`**: en Linux y macOS, el ejecutable se compila con la instrucción de
  buscarlas en esas mismas carpetas (`-Wl,-rpath,...`), así que `larimar run` funciona sin copiar nada. En
  Windows, una `.dll` se busca junto al `.exe` o en el `PATH`.

Llevar las dinámicas a otra máquina (un instalador, un paquete del sistema, una dependencia documentada)
es decisión de quien distribuye el programa, y de sus licencias. Si el ejecutable debe ser un solo
archivo, la biblioteca se enlaza de forma estática o se compila como código fuente.

Un proyecto también se puede construir como biblioteca para C y para Larimar: ver el
[capítulo 28](#28-bibliotecas-escritas-en-larimar).

### Un ejemplo con Windows

```ts
// src/win.lar: el módulo que habla con Windows
cinclude "<windows.h>";

public native type HWND;
public native function GetConsoleWindow(): HWND;
public native function MessageBoxA(owner: HWND, text: String, caption: String, kind: uint32): int32;

public const MB_YESNO: uint32 = 0x04;
public const IDYES: int32 = 6;
```

```ts
// src/main.lar
import win;

function main(): int32 {
    let window: win.HWND = win.GetConsoleWindow();
    if (win.MessageBoxA(window, "Continue?", "Larimar", win.MB_YESNO) == win.IDYES) {
        println("yes");
    }
    return 0;
}
```

con `dynamic_libraries = ["user32"]` en `[c]`. Declarar todo lo de Windows en un módulo `win` evita repetir
las declaraciones `native`: cada `native type` es un tipo distinto en cada módulo que lo declara, así
que el `HWND` debe venir de un solo sitio.

### El editor: `larimar check` y `larimar lsp`

**`larimar check`** enlaza y analiza un programa igual que `larimar build`, pero no genera C ni llama
al compilador de C: es la forma rápida de saber si hay errores.

```sh
larimar check                    # el proyecto de esta carpeta (su larimar.toml)
larimar check src/tools.lar      # un archivo suelto, como programa
larimar check . --json           # para herramientas: [{ "file", "line", "message", "kind" }]
```

Sin `--json` escribe los errores en la salida de error (o `no errors`); el código de salida es 1 si hay
errores.

**`larimar lsp`** es el servidor de lenguaje (Language Server Protocol): el editor lo arranca y le
habla por la entrada y la salida estándar. Responde:

| Qué | Cómo se ve en el editor |
|---|---|
| Errores en vivo | subrayados mientras escribes (cuando dejas de teclear un momento), en todos los archivos del programa |
| Hover | la declaración (firma, campos de un struct, variantes de un enum) y el comentario `/** ... */` o `//` que tiene encima |
| Ir a la definición | también a otro módulo o a `std` |
| Referencias | los usos de una variable, función, método, campo, variante o tipo |
| Símbolos del archivo | el esquema (Outline): funciones, tipos y sus miembros |
| Autocompletado | tras `.`: campos y métodos según el tipo, nombres públicos de un módulo (`shapes.`), variantes de un enum; sin `.`: variables locales, nombres visibles, módulos y palabras clave |
| Ayuda de firma | los parámetros de la función que estás llamando, con el actual resaltado |

Cómo trabaja:

- Guarda en memoria el texto de los archivos abiertos (lo que aún no has guardado incluido), en memoria
  de C que se libera cuando el texto cambia: el servidor puede estar horas abierto sin crecer.
- Cada pregunta la responde un proceso nuevo (`fork()`): enlaza y analiza el programa con esos textos,
  responde y termina. Así ningún análisis deja memoria atrás ni ve el estado del anterior, y si uno
  falla solo se pierde esa respuesta. En el compilador mismo (unas 16.000 líneas) cada respuesta tarda
  unos 0,2 s.
- El programa de un archivo es el `main` del `larimar.toml` que tiene encima; si ese programa no lo
  importa (o no hay `larimar.toml`), el archivo se analiza como programa por sí solo.
- Donde no hay `fork()` (Windows), o con `LARIMAR_LSP_NO_FORK=1`, cada pregunta va a un
  `larimarc lsp-worker` a través de dos archivos temporales.
- Los mensajes de diagnóstico del servidor van a la salida de error (el editor los muestra en su
  panel de salida); la salida estándar es solo del protocolo.

Límites: el análisis se hace del programa entero, así que un error de sintaxis (que impide enlazar)
deja sin respuestas hasta corregirlo; las columnas se buscan en el texto de la línea (el compilador
guarda la línea de cada nodo, no la columna), así que si un nombre aparece dos veces en la misma línea
con significados distintos, el primero gana.

#### VS Code

La extensión de Larimar para VS Code se instala desde su paquete:

```sh
code --install-extension larimar-<versión>.vsix
```

Busca Larimar en este orden: el ajuste `larimar.home`, la variable `LARIMAR_HOME`, `larimar` en el
`PATH` y, en macOS y Linux, el `LARIMAR_HOME` de tu shell de inicio (VS Code abierto desde el Dock no
ve lo que exporta `~/.zshrc`). Arranca `$LARIMAR_HOME/bin/larimarc lsp`. Añade los comandos
**Larimar: Run Project** y **Debug Project** (también en el botón ▷ del editor), **Build Project**,
**Check Project**, **Show Generated C** y **Restart Language Server**. Las pruebas del proyecto se
ven en la vista **Testing**, cada una en su línea, para ejecutar una, un archivo o todas (con
`larimar test --list --json` y `--json`, ver [Pruebas](#pruebas-test-function-y-larimar-test)).

Otros editores (Neovim, Helix, Zed, Sublime...) solo necesitan que se les diga que arranquen
`larimarc lsp` para los archivos `.lar`, con `LARIMAR_HOME` en el entorno.

### Depurar: `larimar build --debug` y `larimar dap`

`larimar build --debug` (también `larimar run --debug`, y `larimar archivo.lar -o archivo.c --debug`)
compila con `-g -O0` (sin las `-O` de `flags`) y pone en el C directivas `#line` que dicen de qué línea
del `.lar` viene cada parte. Dentro de una función, cada línea de C lleva la línea del `.lar` de la
sentencia de la que viene, y la cabecera de la función la línea donde se declara; las funciones del
runtime y los ayudantes generados se ven como el C que son. Además escribe junto al C el **mapa de
depuración** (`build/<name>.debug.json`): cada función de C con su nombre de Larimar y sus variables
(su nombre en Larimar, su nombre en C y su tipo), las globales y la forma de cada tipo.

**`larimar dap`** es el depurador para editores (Debug Adapter Protocol), escrito en Larimar. Va entre
el editor y `lldb-dap`, el adaptador de LLVM que ejecuta el programa bajo lldb:

```
VS Code  <-- DAP -->  larimar dap  <-- DAP -->  lldb-dap  -->  build/demo
```

Lo que pasa por él sin cambios: arrancar, puntos de interrupción, continuar, paso a paso, hilos. Lo que
responde él, con el mapa:

- **La pila** con los nombres de Larimar (`main`, `Dog.bark`, `geo.shapes.area`); los marcos del
  runtime y de C salen atenuados y con `[C]`, y el editor enfoca el primero de Larimar.
- **Las variables** con sus nombres de Larimar (`total`, no `total_12`), sin los temporales del
  compilador, solo las ya declaradas en esa línea, y cada valor leído y mostrado como Larimar:

  | Valor | Se ve como |
  |---|---|
  | `String` | `"Larimar ñ"` |
  | `T[*]`, `T[]` | `[3] ["a", "b", "c"]`, y al abrirlo `[0]`, `[1]`... |
  | `T?` | su valor, o `null` |
  | struct | `Point {x=1, y=2}`, y sus campos |
  | enum | `Circle(r=1.5)`, y sus campos |
  | objeto de clase | con su clase real (un `Animal` que es un `Dog` se ve como `Dog`) y los campos de todos los niveles |
  | interfaz | el objeto que hay detrás |
  | `Any` | lo que guarda: `42`, `"x"`, `{ 2 items, 2 entries }` con sus entradas al abrirlo, o el objeto |

  Los valores se leen con expresiones de C que lldb evalúa (`(long long)(x).len`, `memory read`...):
  no hay nada que instalar en lldb. Un ámbito **C** muestra además todo lo que ve lldb, tal cual.
- **La consola de depuración y el hover** entienden caminos de Larimar: `a.name`, `list[2]`,
  `pts[1].y`, `data.inner`, `list.length`. Lo demás (una expresión de C, un comando de lldb empezando
  con `` ` ``) va a lldb.
- **Puntos de interrupción de función** con nombres de Larimar (`main`, `Dog.bark`).
- **Entrar en una función** se salta el runtime (no acabas dentro de `rt_str` o `List_s_push`).
- **Panics**: con el filtro *Panics* (activo por defecto), el programa para donde ocurre un panic
  (índice fuera de rango, `!` sobre `null`, `panic(...)`) y el editor lo muestra como una excepción con
  su mensaje: *index 3 out of range (length 3)*.

Necesita `lldb-dap`: en macOS viene con las herramientas de Xcode recientes (`xcrun --find lldb-dap`)
o con el LLVM de Homebrew; en Linux, con el paquete de lldb (`lldb-dap` o `lldb-dap-18`, por ejemplo);
en Windows, con LLVM. `larimar dap --backend <ruta>` o `LARIMAR_LLDB_DAP` dicen cuál usar.

**En VS Code**, **Larimar: Debug Project** o F5 en un archivo `.lar` compila con `--debug` y arranca
`larimar dap`. Un `launch.json` puede fijar el proyecto, los argumentos, el entorno, si para al
empezar (en el `main` de Larimar) y si la salida va a la consola de depuración o a la terminal (para
programas que leen el teclado):

```json
{
    "type": "larimar",
    "request": "launch",
    "name": "Debug Larimar project",
    "project": "${workspaceFolder}",
    "args": ["--verbose"],
    "env": { "PORT": "8080" },
    "stopOnEntry": false,
    "console": "integratedTerminal"
}
```

**Desde la terminal**, o con otros depuradores, `debug/` trae formateadores que enseñan a lldb y gdb a
mostrar los mismos valores (no los nombres: ahí las variables se llaman como en el C, `total_12`, y se
ven los temporales):

```sh
larimar build --debug
lldb build/demo
(lldb) command script import $LARIMAR_HOME/debug/larimar_lldb.py
(lldb) breakpoint set --file main.lar --line 12
(lldb) run
(lldb) frame variable
```

Con gdb: `source $LARIMAR_HOME/debug/larimar_gdb.py` y `break main.lar:12`. En VS Code, el ajuste
`larimar.debugger` puede usar CodeLLDB o la extensión C/C++ con gdb en lugar de `larimar dap`, con
estos formateadores.

### Plugins: comandos de otros programas

Un programa de `$LARIMAR_HOME/bin` puede añadir comandos a `larimar`, declarados en un archivo de
`$LARIMAR_HOME/plugins/`, uno por plugin:

```toml
# $LARIMAR_HOME/plugins/minero.toml
[plugin]
name = "minero"
program = "minero"           # en $LARIMAR_HOME/bin, en ningún otro sitio
version = "1.0.0"

[commands]
add = ["add"]                # larimar add x  ->  bin/minero add x
fetch = ["fetch"]
```

- `larimar add github.com/zerh/sql@v1` ejecuta `bin/minero add github.com/zerh/sql@v1` en la misma
  consola, con `LARIMAR_HOME` puesto, y su código de salida es el de larimar.
- Un plugin no puede tomar un comando propio de larimar (`build`, `run`, `test`...), y dos plugins no
  pueden tomar el mismo: los dos casos se avisan, y el comando no se toma.
- `larimar help` lista los comandos de los plugins y quién los atiende.
- Si el programa no está, el error lo dice: `'larimar add' is answered by minero (plugins/minero.toml), but bin/minero does not exist`.
- Instalar un plugin es poner su programa en `bin/` y su archivo en `plugins/`; quitarlo, borrar los dos.

### Pruebas: `test function` y `larimar test`

Una prueba es una función marcada con `test`. No recibe nada (o un *setup*, abajo) y no devuelve nada;
dentro, las funciones de `std.test` comprueban lo que debe pasar:

```ts
// tests/shapes_test.lar
import std.test { check, checkText, checkInt, checkFloat };
import geo.shapes { Shape, area, name };

test function circleArea(): void {
    checkFloat(12.56636, area(Shape.Circle { radius: 2.0 }), 0.0001);
}

test function names(): void {
    checkText("circle", name(Shape.Circle { radius: 1.0 }));
    check(name(Shape.Empty) != "", "every shape has a name");
}
```

```
$ larimar test
  ok    tests/shapes_test.lar: circleArea
  FAIL  tests/shapes_test.lar: names
        check failed: expected "circle" but got "Circle"

1 passed, 1 failed
failed:
  tests/shapes_test.lar: names
```

| De `std.test` | Falla cuando... |
|---|---|
| `check(cond, mensaje)` | `cond` es `false` (dice el mensaje) |
| `checkText(esperado, real)` | los dos textos son distintos |
| `checkInt(esperado, real)`, `checkInt64` | los dos números son distintos |
| `checkFloat(esperado, real, tolerancia)` | están más lejos que la tolerancia |
| `fail(mensaje)` | siempre |
| `skip(motivo)` | nunca: la prueba se salta (falta un programa, otra plataforma); después, `return` |

Una comprobación que falla dice por qué y la prueba sigue (para cortarla ahí, `return`); la prueba falla si
falló alguna. Si la prueba llama a algo que puede lanzar un error, lo declara como cualquier función
(`test function x(): void throws ParseError`); si el error llega hasta arriba, la prueba falla con
`the test threw ParseError`.

**Un setup** prepara algo antes de cada prueba y lo limpia después. Es una clase que implementa
`TestSetup`, y la prueba la recibe como parámetro:

```ts
import std.test { checkText, fail, TestSetup };
import std.io.files as Files;
import std.io { IoError };

class TempFile implements TestSetup {
    let path: String = "build/test/tmp.txt";

    function beforeEach(): void {
        try { Files.writeString(self.path, "hola"); } catch (IoError e) { fail("cannot write ${self.path}"); }
    }

    function afterEach(): void {
        try { Files.delete(self.path); } catch (IoError e) { }
    }
}

test function readsBack(f: TempFile): void throws IoError {
    checkText("hola", Files.readString(f.path));
}
```

Para cada prueba se crea un `TempFile {}` nuevo (sus campos necesitan valores por defecto), se llama a
`beforeEach()`, a la prueba y a `afterEach()`, siempre, también si algo falló. Si falla una comprobación
en `beforeEach()`, la prueba no se ejecuta.

**Cómo funciona.** `larimar test` no tiene nada escondido:

- Busca los `.lar` de `tests/` (o los archivos y carpetas que se le den). Los que tienen `test function`
  son pruebas; los demás (módulos que las pruebas importan) no se ejecutan.
- Por cada archivo escribe una copia con un `main` añadido al final, que ejecuta la prueba cuyo nombre
  recibe. La copia queda en `build/test/<archivo>.lar` para leerla; el archivo original no se toca.
- Compila esa copia con AddressSanitizer y UBSan (salvo en Windows o con `--no-sanitize`) y ejecuta **cada
  prueba en su propio proceso**: un `panic` o un error de memoria marcan esa prueba y las demás siguen,
  y nada se comparte entre pruebas.
- Termina con código 0 si todo pasó y 1 si algo falló.

```sh
larimar test                      # todas las de tests/
larimar test tests/shapes_test.lar
larimar test --only circle        # las que tienen "circle" en el nombre o la ruta
larimar test tests/shapes_test.lar --test names   # solo esa prueba, por su nombre exacto
larimar test --list               # las pruebas, sin ejecutarlas
larimar test --no-sanitize
```

**Para los editores**, `--json` escribe un objeto JSON por línea en lugar del texto de arriba: con
`--list`, un `{"event": "found", "file": ..., "path": ..., "name": ..., "line": ...}` por prueba; al
ejecutarlas, un `{"event": "result", ..., "result": "passed" | "failed" | "skipped", "message": ...}`
por prueba y al final `{"event": "summary", "passed": ..., "failed": ..., "skipped": ...}`. Así la
extensión de VS Code muestra las pruebas en su vista Testing.

Las reglas:

- `larimar build` deja fuera las `test function`: no llegan al ejecutable. `larimar check` y el editor sí
  las revisan.
- Un archivo con pruebas no tiene `main` (lo escribe `larimar test`), y una `test function` no puede ser
  `public`.
- En un proyecto, las pruebas importan desde la carpeta del `main` del proyecto (`src/`), así que
  `import geo.shapes` encuentra `src/geo/shapes.lar`; se compilan con las bibliotecas de `[c]`.
  Sin `larimar.toml`, importan desde su propia carpeta.
- Las pruebas (y el editor) también encuentran módulos desde la carpeta del proyecto: lo que comparten
  varias pruebas va en un módulo como `tests/support/files.lar`, y se importa con
  `import tests.support.files { ... }`. `larimar build` no los ve.
- Las comprobaciones se usan desde el hilo de la prueba (guardan cuántas fallaron en una variable global,
  que los lambdas de un `Thread` no pueden tocar).

---

## 27. Bibliotecas escritas en Larimar

El [capítulo 23](#23-llamar-a-c) es C visto desde Larimar. Este capítulo es al revés, en grande:
código escrito en Larimar entregado como una **biblioteca de C**, que un programa de C usa con su `.h`
sin saber de Larimar, y que un programa de Larimar importa como un módulo. Quien la escribe tiene las
reglas de memoria de Larimar; quien la usa recibe una biblioteca de C normal.

Un proyecto con `kind = "library"` se construye como **biblioteca**: un programa de C la usa como
cualquier biblioteca de C, y un programa de Larimar la importa como un módulo. Por defecto es
**estática** (va dentro del ejecutable que la usa); `type = "dynamic"` en `[library]`, o
`larimar build --dynamic`, la hace dinámica (`--static` hace lo contrario).

```toml
[project]
name = "textkit"
version = "1.0.0"
kind = "library"             # "program" (por defecto) o "library"
main = "src/textkit.lar"

[library]
type = "static"              # "static" (por defecto) o "dynamic"
prefix = "tk"                # sus nombres de C empiezan con él: tk_wordCount (por defecto, el nombre)
```

### Crear una biblioteca

`larimar new textkit --library` crea una así, con una export function y una prueba de ella. El nombre de
una biblioteca es también su módulo y sus archivos, así que solo lleva letras, dígitos y `_`.

Lo que C (y Larimar) ve de una biblioteca son sus **export functions** ([Que C llame a Larimar](#que-c-llame-a-larimar-export-function))
y las clases que dan o reciben, con sus campos y métodos:

```ts
// src/textkit.lar

/** Counts the words of a text. */
public export function wordCount(text: String): int32 {
    let n: int32 = 0;
    for (w in text.split(" ")) {
        if (w != "") { n += 1; }
    }
    return n;
}

/** The text with its first letter in upper case. */
public export function title(text: String): String {
    if (text == "") { return ""; }
    return "${text.substring(0, 1).toUpperCase()}${text.substring(1)}";
}

/** Counts words as they come. */
public class Counter {
    /** The words counted so far. */
    let words: int32 = 0;
    let texts: String[*] = [];

    /** Counts the words of a text, and keeps it. */
    function add(text: String): void {
        self.words += wordCount(text);
        self.texts.push(text.clone());
    }

    /** The last text it counted (null when there is none). */
    function last(): String? {
        if (self.texts.length == 0) { return null; }
        return self.texts[self.texts.length - 1].clone();
    }
}

/** A new counter, at zero. */
public export function newCounter(): Counter { return Counter {}; }
```

`larimar build` deja cuatro archivos en `build/textkit/`, que van juntos:

| Archivo | Para | Qué tiene |
|---|---|---|
| `libtextkit.a` | los dos | la biblioteca (dinámica: `libtextkit.so`, `libtextkit.dylib` o `textkit.dll`) |
| `textkit.h` | C | los prototipos, con sus comentarios de documentación, y cómo liberar lo que dan |
| `textkit.lar` | Larimar | las mismas funciones como declaraciones `native` |
| `textkit.interface` | el compilador | su nombre, versión, tipo, lo que necesita enlazado y el **hash de la interfaz** |

### Usarla desde C

El `.h` lo dice todo (aquí sin su primer comentario; los textos de los comentarios son los
de la biblioteca y los que escribe el compilador, en inglés):

```c
typedef struct tk_Counter tk_Counter;

/* Counter: its fields (to read) and its methods; self is the handle. */

/** The words counted so far. */
int32_t tk_Counter_words(tk_Counter* self);

/** Counts the words of a text, and keeps it. */
void tk_Counter_add(tk_Counter* self, const char* text);

/**
 * The last text it counted (null when there is none).
 *
 * NULL, or a text that is yours: free it with tk_free.
 */
char* tk_Counter_last(tk_Counter* self);

/** Counts the words of a text. */
int32_t tk_wordCount(const char* text);

/**
 * The text with its first letter in upper case.
 *
 * The text is yours: free it with tk_free.
 */
char* tk_title(const char* text);

/**
 * A new counter, at zero.
 *
 * A new Counter that is yours: give it back with tk_Counter_release.
 */
tk_Counter* tk_newCounter(void);

/** Gives back a Counter (NULL does nothing). */
void tk_Counter_release(tk_Counter* handle);

/** Frees a text the library returned (NULL does nothing). */
void tk_free(void* text);

/** The interface hash of the library (as in textkit.interface): compare it with TEXTKIT_INTERFACE. */
const char* tk_interface(void);
```

```c
#include <stdio.h>
#include "textkit.h"

int main(void) {
    char* t = tk_title("larimar");
    tk_Counter* c = tk_newCounter();
    tk_Counter_add(c, "one two");
    tk_Counter_add(c, "three");
    char* last = tk_Counter_last(c);
    printf("%s %d %d %s\n", t, tk_wordCount("a b c"), tk_Counter_words(c), last);
    tk_free(t);
    tk_free(last);
    tk_Counter_release(c);
    return 0;
}
```

```sh
cc -std=c99 -Ibuild/textkit main.c build/textkit/libtextkit.a -lm
./a.out                                  # Larimar 3 3 three
```

Lo que una biblioteca estática necesita enlazado además está en `links` de su `.interface` (`-lm`,
`-pthread` si usa hilos, las de TLS...).

### Usarla desde Larimar

Los cuatro archivos se copian a una carpeta del programa (o se dejan donde están), y la
biblioteca se nombra en `[c]` como cualquier otra:

```toml
[c]
static_libraries = ["textkit"]
static_library_paths = ["libs/textkit"]
```

```ts
import textkit;
import textkit { Counter };

function main(): int32 {
    let c: Counter = textkit.newCounter();
    c.add("one two");
    c.add("three");
    println("${textkit.title("larimar")} ${c.words} ${c.last() ?? "-"}");
    return 0;
}
```

Salida: `Larimar 3 three`

Como `textkit.interface` está en esa carpeta, el compilador sabe que es una biblioteca escrita en
Larimar: `import textkit` encuentra ahí `textkit.lar` (también `larimar check` y el editor), se incluye su
`.h` y se enlaza lo que necesita. El `.lar` que lee son declaraciones `native` normales:

```ts
cinclude "textkit.h";

/** Counts words as they come. */
public native type Counter = tk_Counter* released by tk_Counter_release {
    // not given to C (they do not cross): texts (String[*])
    /** The words counted so far. */
    native let words: int32 = tk_Counter_words;
    /** Counts the words of a text, and keeps it. */
    native function add(text: String): void = tk_Counter_add;
    /** The last text it counted (null when there is none). */
    native function last(): String? = tk_Counter_last released by tk_free;
}

/** Counts the words of a text. */
public native function wordCount(text: String): int32 = tk_wordCount;

/** The text with its first letter in upper case. */
public native function title(text: String): String = tk_title released by tk_free;

/** A new counter, at zero. */
public function newCounter(): Counter { return newCounter_c()!; }
native function newCounter_c(): Counter? = tk_newCounter;

// what gives back the texts and objects of the library (only the compiler calls them)
native function tk_free(text: String): void = tk_free;
native function tk_Counter_release(handle: Counter): void = tk_Counter_release;
```

Un texto de la biblioteca se copia en la memoria del programa y se libera en seguida
([`released by` en una función](#textos-que-hace-c-released-by-en-una-función)); un `Counter` es un
[recurso](#recursos-released-by): cuando se libera la memoria donde vive, `tk_Counter_release` lo
devuelve. No se libera nada a mano, y la clase se usa como en la biblioteca: se llaman sus métodos
(`c.add("x")`), se leen sus campos (`c.words`), y las funciones tienen los mismos nombres y tipos.

### El hash de la interfaz

El `.interface` tiene ocho dígitos hexadecimales, el comienzo del SHA-256 del
`.lar`; la biblioteca tiene los mismos dentro (`tk_interface()` los devuelve, y el `.h` los tiene en
`TEXTKIT_INTERFACE`). Antes de construir un programa que la enlaza, `larimar build` comprueba que los tres
coinciden, y se detiene con lo que está mal:

- un `.lar` editado a mano: `textkit.lar does not match the library (its hash is ..., textkit.interface says ...)`;
- una biblioteca de otro build junto a un `.lar` viejo: `libtextkit.a is from another build than textkit.lar and textkit.interface`;
- una biblioteca estática en `dynamic_libraries` (o al revés): `textkit is a static library (...): put it in static_libraries`.

Así un programa nunca llama a una biblioteca con declaraciones que no son las suyas. El hash cubre todo
el `.lar`: las funciones, sus tipos y su documentación, la versión y el tipo. Una versión nueva son cuatro
archivos nuevos que van juntos. Un programa de C puede comprobar lo mismo al arrancar:
`strcmp(tk_interface(), TEXTKIT_INTERFACE) == 0`.

### Las export functions y las clases de una biblioteca

Qué va a C, y cómo:

- **Sus nombres de C** son `<prefijo>_<nombre>` (`tk_wordCount`). `= nombre_c` después de la firma le da
  uno propio (`export function answer(): int32 = tk_the_answer { ... }`), y `prefix = ""` deja los
  nombres como están. La biblioteca misma da `<prefijo>_free`, `<prefijo>_<Clase>_release` y
  `<prefijo>_interface`: una export function no puede tomar esos nombres (ni un método llamarse `release`).
- **Sus tipos**: números, `bool`, `String` y `String?` (`const char*`; `NULL` es `null`), y las **clases**
  de la biblioteca y sus opcionales. Los tipos native y los structs de C no van: son de cabeceras de C que
  el programa también necesitaría.
- **Un texto que devuelve** es una copia (`char*`) para quien llama: C la libera con `<prefijo>_free`.
- **Un objeto que devuelve** es un **handle**: C lo guarda (`tk_Counter*`), lo pasa a sus métodos y a
  otras export functions, y lo devuelve con `<prefijo>_<Clase>_release`. El handle tiene su propia memoria: lo que el
  objeto crea después (una lista que crece, sus textos) vive ahí y se libera con él. Un `NULL` donde se
  espera una clase detiene el programa con un pánico que nombra la función y el parámetro
  (`tk_Counter_add: 'self' is NULL`); donde se espera `Counter?`, es `null`.
- **También van los miembros de sus clases.** Por cada clase que C recibe: cada campo se lee con
  `<prefijo>_<Clase>_<campo>(handle)` (un texto: una copia que se libera) y cada método se llama con
  `<prefijo>_<Clase>_<método>(handle, ...)`, por su vtable, así que corre el método de una subclase.
  Van también los miembros de sus padres. En el `.lar` son un `native let` y una `native function` de
  la clase, así que un programa escribe `c.words` y `c.add("x")`. Un campo solo se lee: se cambia con un
  método. Lo que no cruza (un campo lista, un método que lanza o que recibe una lista, un operador) se
  queda dentro, y el `.lar` lo dice en un comentario. Un campo de tipo clase tampoco va: su objeto es
  del otro; un método que devuelve uno nuevo sí.
- **Cada llamada tiene su propia memoria**, que se libera al volver. Las globales de la biblioteca se
  crean al cargarla (o en su primera llamada) y viven lo que dura el programa.
- **`export` no hace `public` a una función**: con las dos, las pruebas de la biblioteca (y sus otros
  módulos) la pueden llamar desde Larimar.
- **Sin main**: el programa que la usa tiene el suyo. Una biblioteca con `main` es un error.

### Por dentro, todo es privado

Todo el C menos las export functions y esas tres es `static`: el runtime
de la biblioteca, sus clases, sus otras funciones. Así dos bibliotecas escritas en Larimar, y el programa
de Larimar que las enlaza, no chocan: cada una tiene su propio runtime (unos pocos KB) y sus propias
memorias, y de una a otra no pasa nada más que textos (copiados) y handles.

### Sus pruebas

`larimar test` en la carpeta de la biblioteca ejecuta sus pruebas como en cualquier
proyecto: importan sus módulos (el código de Larimar, no el `.a`). `larimar check` y el editor también
aplican a su código las reglas de una biblioteca.

### Aclaraciones

- **Por qué estática por defecto.** El ejecutable que la usa es un solo archivo, y no depende de que
  donde se ejecute esté instalado un `.so` del build correcto. Una dinámica la comparten varios programas
  y se puede reemplazar sin construirlos de nuevo.
- **Dónde se busca una dinámica.** Como cualquier biblioteca dinámica: en Linux y macOS, en las
  `dynamic_library_paths` del programa (rpath; en macOS la biblioteca es `@rpath/libtextkit.dylib`); en
  Windows, junto al `.exe` o en el `PATH` (el enlazador usa `libtextkit.dll.a`, que se hace con ella).
- **Lo que necesita una estática.** Las bibliotecas que necesita su C, y las que ella misma enlaza, están
  en `links`: un programa de Larimar las agrega solo; uno de C las agrega a su comando. Las bibliotecas
  estáticas que enlaza una biblioteca estática no se meten dentro de ella: el programa también las necesita.
- **Pánicos.** Un pánico dentro de la biblioteca (un error de programación: un índice fuera de rango, un
  handle `NULL`) lo imprime y termina el programa, como en un programa de Larimar.
- **Hilos.** La biblioteca puede crear hilos por dentro. Las llamadas desde varios hilos de C a la vez son
  cosa de quien llama, como con cualquier biblioteca de C (Larimar no las ve): un handle, o las globales,
  en un hilo a la vez, salvo que sea una `synchronized class`.
- **El hash no es una firma.** Descubre errores (archivos de builds distintos), no a alguien que cambia
  una biblioteca a propósito.
- **Los cuatro archivos se generan**: no se editan, no se guardan en el repositorio de la biblioteca
  (están en `build/`) y se publican juntos.
- **Todavía no**: las listas, los callbacks y los errores (`throws`) no cruzan una biblioteca; van como
  textos, handles y números (un código de error), o se quedan dentro. Un programa no crea objetos de la
  biblioteca con `Counter {}`, ni extiende sus clases: los hacen sus funciones y métodos.

---

## 28. Qué genera el transpilador

Un **transpilador** es un compilador que escribe código en otro lenguaje en lugar de un programa:
Larimar escribe C. Este capítulo es para los curiosos, y para quien quiera compilar el C a mano.

El resultado es **un único archivo C99** (`build/<name>.c`) que contiene el runtime y todo el programa,
con todos sus módulos, sin dependencias más allá de la biblioteca estándar de C. `larimar build` lo
compila, pero también se puede compilar a mano con cualquier compilador de C:

```sh
larimar c src/main.lar > program.c
gcc -std=c99 -O2 program.c -o program
```

El C generado compila sin avisos con `gcc -std=c99 -Wall -Wextra -pedantic`, y **solo lleva lo que el
programa usa**. Se decide en dos pasos, siguiendo los nombres:

1. **El programa.** Se parte de `main`, de las `export function` y del C que el programa escribió él mismo
   (`cinclude`, `ccode`), y se queda cada función, método, tipo, variable global o función auxiliar que
   algo de eso nombra, y así sucesivamente. Un método de `String` que el programa no llama, el `Opt_i64`
   que solo aparecía en su firma o la función de `std` que nadie usa no llegan al C.
2. **El runtime.** Del runtime se añaden las piezas que define algún nombre de lo que quedó (y las que
   esas usan), con sus `#include`. El runtime es el C de `std/runtime/` (`memory.lar`, `string.lar`,
   `any.lar`..., un `ccode` cada uno), leído del `std/` instalado como el resto de la biblioteca. Un programa que no usa memorias no lleva el código de memorias; uno que
   no divide no lleva las comprobaciones de división; un `println` de números y textos se escribe con
   `printf`.

Un "hola mundo" queda así:

```c
/* Generated by the transpiler. Runtime first, then the program. */
#include <stdint.h>
#include <stdio.h>

/* ---- Prototypes ------------------------------------------------------------ */
static int32_t user_main(void);

/* ---- Functions ------------------------------------------------------------- */
static int32_t user_main(void) {
    fputs("hola mundo\n", stdout);
    return 0;
}

/* ---- Entry point ----------------------------------------------------------- */
int main(void) {
    int32_t result = user_main();
    return (int)result;
}
```

Y es legible:

| En Larimar | En C |
|---|---|
| `struct` | `struct` normal; los métodos son funciones que reciben `S*` |
| `class` | `struct` con una cabecera (vtable y memoria); la subclase contiene a su padre como `_super` |
| métodos virtuales | una tabla de punteros a función por clase |
| `interface` | `{ void* obj; const Table* t; }` |
| `enum` | `{ int32_t tag; union { ... } as; }` |
| lambda | `{ puntero a función; entorno con las capturas }`, por valor |
| `T[N]` | `{ int32_t length; T items[N]; }` |
| `throws` | un parámetro extra `RtError*`, comprobado después de cada llamada |
| memorias automáticas | un `RtMem` por bloque (`mem_N`) y por instrucción (`tmp_N`), creado solo si algo vive ahí y liberado en todas las salidas |
| lo que devuelve una función | un primer parámetro `RtMem* rt_dest`: la memoria de la llamada (`NULL` si la función no crea su resultado) |
| `geo.shapes.area` | `geo__shapes__area` (el archivo principal conserva sus nombres) |
| `main` | `user_main`, llamada desde el `main` de C |
| `native type X;` / `= T;` | `typedef void* Ext_X;` / `typedef T Ext_X;` |
| `native type X = (A) -> R;` | `typedef R (*Ext_X)(A);` |
| `native struct X { ... }` | el struct de C, con su nombre; Larimar no lo define |
| `native type X = T* { native function m() = c_m; }` | `x.m()` es `c_m(x)`: una función `static` que la llama |
| un callback con `Context` | una función de C (`lm_ctx_...`) que llama a la de Larimar que lleva el contexto |
| `export function f` | la función de Larimar (`larimar_f`) y una función `f` con tipos de C que la llama |
| `Any` | `RtAny`: `{ kind; union de valores }`; una tabla es un `RtTable*` con índice hash; un struct va en una copia |
| `Thread`, `synchronized` | hilos del sistema (`pthread` o Windows); un candado recursivo por objeto |

### Comprobar la memoria

Para comprobar un programa durante el desarrollo, compila con los detectores de errores de gcc o clang:

```toml
[c]
flags = ["-g", "-fsanitize=address,undefined"]
```

Con AddressSanitizer activado, **el runtime le enseña a ver dentro de las memorias**. Una memoria pide al
sistema bloques grandes y reparte trozos de ellos, así que, sin ayuda, AddressSanitizer solo vería el
bloque entero y no notaría que algo se sale de su trozo. El runtime lo resuelve así:

- la parte de cada bloque que todavía no se ha repartido está envenenada;
- cada trozo desenvenena exactamente los bytes que se pidieron;
- en las memorias que crecen, entre un trozo y el siguiente queda un hueco envenenado.

Así, leer o escribir un solo byte de más se detiene en esa línea, con el error y la pila de llamadas.
Pasa sobre todo con código C (`ccode`) que escribe en una memoria:

```ts
ccode {
    static const char* bad(RtMem* m) {
        char* out = (char*)rt_mem_alloc(m, 4, 0);
        for (int i = 0; i <= 4; i++) out[i] = 'A';      /* un byte de más */
        out[3] = 0;
        return out;
    }
}
```

```
==441==ERROR: AddressSanitizer: use-after-poison on address 0x531000000815
WRITE of size 1 at 0x531000000815 thread T0
    #0 in bad program.c:274
```

Sin las comprobaciones, ese byte pisaría en silencio lo siguiente de la memoria. Lo que ya murió también
se detecta: una memoria liberada devuelve sus bloques al sistema, y AddressSanitizer avisa si algo los
lee después.

- Las comprobaciones solo existen al compilar con `-fsanitize=address`. Sin esa opción no cuestan nada:
  el C es el mismo, sin huecos ni comprobaciones.
- Con `-DRT_DEBUG_MEMORY` (sin AddressSanitizer) se dejan los mismos huecos, y los bloques liberados se
  rellenan con `0xDD`: un valor que sobrevivió a su memoria se lee como basura en vez de parecer correcto.
- Las memorias sobre un búfer de la pila o estático (`in byte[N]`) no se envenenan, porque ese búfer no es
  del runtime.

**Si el compilador se equivoca.** Si el generador encuentra algo que el análisis debería haber resuelto
(por ejemplo, una llamada que crea su resultado y se quedó sin memoria), no escribe C que fallaría al
ejecutar, sino que se detiene con un error:

```
Internal Error [main.lar:7]: 'buffer' creates its result, but this call was given no memory for it.
This is a bug of the compiler, not of your program: please report it.
```

Y si aun así algo intentara crear un valor sin memoria, el programa se detiene con un `panic` que lo dice,
en lugar de fallar con un error de segmentación.

---

## 29. Larimar escrito en Larimar

El compilador de Larimar, **larimarc**, y la herramienta `larimar` están escritos en Larimar. El
repositorio tiene:

```
larimar/
  src/                   el compilador (Larimar), una carpeta por etapa:
    main.lar               los comandos (new, build, run, test, check, lsp, dap)
    syntax/                del texto al árbol: lexer, parser, ast
    semantics/             entender el programa: módulos (linker), tipos, análisis, expresiones
    codegen/               del árbol a C: gen, expresiones, runtimeselect, prune, mapa de depuración
    editor/                larimar check, lsp y dap
    project/               el compilador de C, larimar test (larimar.toml se lee con std.encoding.toml)
  std/                   la biblioteca estándar (std/runtime: el runtime, el C bajo cada programa)
  tests/                 las pruebas (tests/lsp: check y el servidor de lenguaje)
  doc/                   el manual (manual.md en inglés; manual.es.md, este) y la especificación (spec.md)
  bootstrap/
    larimarc.c           el compilador ya traducido a C, para arrancar sin Larimar
    build.sh, build.ps1  construyen el compilador e instalan la carpeta ../out/larimar
  bin/larimar            el lanzador que se instala
  tools/
    debuggers/           formateadores de valores para lldb y gdb (se instalan como debug/)
    tcc/                 construyen el tcc que traen los releases (Linux, Windows)
```

Para construirlo solo hace falta un compilador de C:

```sh
cd larimar
./bootstrap/build.sh --verify
```

1. Compila `bootstrap/larimarc.c` y obtiene `larimarc`.
2. Con `--verify`, compila `src/` tres veces: con ese larimarc (`build/stage1.c`), con el compilador que
   sale de ahí (`build/stage2.c`) y con el que sale de este (`build/stage3.c`). `stage2.c` y `stage3.c`
   deben ser idénticos byte a byte: el compilador, compilado por sí mismo, se produce a sí mismo. Si
   `bootstrap/larimarc.c` es más antiguo que `src/`, lo avisa e instala el compilador hecho desde `src/`.
3. Instala en `../out/larimar` (o en `LARIMAR_PREFIX`) el resultado: `bin/larimarc`, `bin/larimar`, una
   copia de `std/`, de `doc/` y de los formateadores (`debug/`). Esa carpeta se puede borrar y regenerar cuando se quiera;
   todo se edita en el repositorio.

Después de cambiar el compilador, `./bootstrap/build.sh --verify` lo comprueba e instala, y el C de
arranque se actualiza con lo que indica:

```sh
cp build/stage2.c bootstrap/larimarc.c
```

`bin/larimar` fija `LARIMAR_HOME` en la carpeta de la instalación, y el compilador busca la biblioteca
estándar en `$LARIMAR_HOME/std`, y el runtime en `$LARIMAR_HOME/std/runtime`.

**El runtime es C, no Larimar.** Las memorias, los textos, `Any`, las clases y los hilos son el suelo
sobre el que se apoya el C generado, así que están escritos en C: el `ccode` de `std/runtime/*.lar` (un archivo por
parte, en el orden en que los lista `codegen/runtimeselect.lar`). El compilador los lee al generar un
programa y se queda solo con los párrafos que usa. Cambiar el runtime no cambia el compilador: no hace
falta regenerar `bootstrap/larimarc.c`, solo volver a pasar las pruebas.

**Una regla al cambiar el lenguaje.** El compilador se construye con su propia biblioteca estándar, así
que `std/` solo puede usar lo que ya entiende el compilador que lo compila. Si añades algo al lenguaje
(como `panic`) y quieres usarlo en `std/`, primero se añade al compilador, se regenera
`bootstrap/larimarc.c` con un compilador que ya lo entiende, y después se usa en `std/`.

### Las pruebas

`tests/run-tests.sh` ejecuta `larimarc test` sobre `tests/` y lo que necesita más de un programa (abajo).
Todas son `test function` ([sección 26](#pruebas-test-function-y-larimar-test)), agrupadas por tema en un
archivo por tema (`tests/c/callbacks_test.lar`, `tests/language/when_test.lar`...). Las que prueban al
compilador mismo usan `tests/support/compiler.lar`, que compila un programa con el compilador que se
prueba y dice qué debe pasar:

```ts
import tests.support.compiler { failsWith, runs };

test function aNativeFunctionHasNoBody(): void {
    failsWith(raw"""
        native function hack(): void { }
        function main(): int32 { return 0; }
        """, "A native function has no body");
}

test function callbacksWithAContext(): void {
    runs("tests/cases/c/native_callbacks_with_context.lar", ["-> 0 UNO", "-> 1 DOS", "-> 2 TRES", "count 3"]);
}
```

| De `tests.support.compiler` | La prueba pasa si... |
|---|---|
| `failsWith(fuente, texto)` | el compilador rechaza esa fuente con un error que contiene `texto` (con `larimar check --json`) |
| `runs(archivo, líneas)` | compila, se ejecuta sin errores de memoria, termina con 0 e imprime esas líneas |
| `panics(archivo, texto)` | compila, y se detiene al ejecutar (`panic`) con `texto` |
| `memoryError(archivo)` | compila, y los detectores encuentran un error de memoria al ejecutar |
| `generatedC(archivo)` | (da el C generado, para comprobar con `hasWord` qué contiene) |

Los programas con errores van dentro de la prueba, en un `raw"""`: son cortos y se leen junto al error
que deben dar. Los que se ejecutan son archivos normales en `tests/cases/<carpeta>/`, que el editor
entiende y que se pueden correr solos (`larimar tests/cases/c/ffi_pointers.lar`) para depurarlos. Lo que
el ayudante escribe y compila queda en `build/test/cases/`. Compila con `$CC` (o `cc`), con
AddressSanitizer y UBSan salvo en Windows, con tcc o con `LARIMAR_TEST_SANITIZE=0`.

```sh
./bootstrap/build.sh --verify --test  # construir, comprobar que se compila a sí mismo, probar e instalar
tests/run-tests.sh                    # todas, con el larimarc que hizo bootstrap/build.sh
tests/run-tests.sh memory             # solo las que tienen "memory" en la ruta o el nombre
larimarc test tests/memory            # solo larimarc test, sobre una carpeta
LARIMARC=build/larimarc_stage2 tests/run-tests.sh
```

`tests/memory/` cubre el modelo de memoria: lo que devuelve una función (creado, vista de un argumento,
uno de sus argumentos), llamadas anidadas, valores por defecto de campos, interpolación, bucles, `map` y
`filter`, lambdas guardadas, `in default`, memorias propias, `clone()`, excepciones con temporales
vivos, `switch` que crea, objetos, `Any`, hilos, `export function` llamada desde C, y lo que debe
rechazarse. **Cada fallo que se encuentre entra primero como prueba**, y después se arregla.

Tres archivos de pruebas lanzan otros programas con `std.os.process` y les hablan como lo haría un editor,
sin Python. `tests/lsp/lsp_test.lar` prueba `larimar check --json` y habla con `larimar lsp` sobre el
proyecto de `tests/lsp/project`: errores publicados, hover, definición, referencias, símbolos,
autocompletado y ayuda de firma, con `fork()` y con `LARIMAR_LSP_NO_FORK=1`.
`tests/debug/debug_test.lar` compila `tests/debug/values.lar` con `--debug`, para con lldb y con gdb (los
que haya) en una línea del `.lar` y comprueba cómo se ven los valores; con `lldb-dap`, habla con
`larimar dap` como un editor (pila, variables, hijos, caminos en evaluate, y un panic de
`tests/debug/panic.lar` como excepción con su mensaje). Lo que no está instalado se salta.
`tests/tls/tls_test.lar` sirve HTTPS (con el certificado propio de `tests/tls`) y HTTP, y compila y ejecuta
`tests/tls/client.lar`: el certificado rechazado por defecto, y con `SystemTls { verify: false }` un GET, un
cuerpo `chunked`, uno grande con `copy()`, un POST, una redirección de `http://` a `https://` y un
`TlsProvider` propio; en Linux, además, el mensaje cuando falta OpenSSL. Toman el compilador de
`$LARIMARC` (lo pone `run-tests.sh`) o del PATH.

---

## 30. Limitaciones actuales

### Por diseño

Lo que Larimar no tiene, ni va a tener, con lo que se usa en su lugar:

- **Sin genéricos.** Los arreglos (`T[N]`, `T[*]`) y `Any` ya guardan cualquier tipo, y las interfaces cubren el resto.
- **Sin recolector de basura.** La memoria se libera en el `;` y en la `}`: siempre se ve dónde ([sección 16](#16-memoria)).
- **Sin constructores.** Un literal crea el objeto; si hay que validar, una función normal lo hace.
- **Sin sobrecarga.** Cada nombre es una función, y el C generado se lee sin adivinar.
- **Sin saltos ocultos.** Un error es un valor que se devuelve, y `throws` lo anuncia en la firma ([sección 19](#19-errores-throw-try-y-catch)).
- **Sin hilos ocultos ni async.** Los hilos se crean a la vista, y el compilador revisa lo que comparten ([sección 22](#22-hilos)).
- **Sin `null` por sorpresa.** Solo puede ser `null` lo que lleva `?` ([sección 14](#14-opcionales-y-null)).
- **Sin conversiones implícitas.** Entre tipos numéricos se convierte con `as`, a la vista: `int32 + int64` no compila.
- **Sin comportamiento indefinido.** Los enteros dan la vuelta, los índices se comprueban y un fallo se detiene con su archivo y su línea ([sección 20](#20-fallos-en-tiempo-de-ejecución)).

### Todavía no

- No hay `defer`.
- Un `Any` no guarda listas `[*]`, lambdas ni interfaces.
- `wait until` no tiene tiempo límite (espera hasta que la condición se cumpla).
- La biblioteca estándar es pequeña: archivos, consola, rutas, entorno, otros programas, tiempo, hashes y
  bytes aleatorios, expresiones regulares, JSON, TOML, base64, hex y URLs, TCP y UDP con sus servidores
  (normales o https), y un cliente HTTP y HTTPS. La red aún no tiene servidor HTTP (eso es para un
  framework encima de `TcpServer`), WebSockets ni un bucle de eventos. Una conexión TLS mantenida ocupa su
  hilo mientras espera. El servidor TLS aún no está en Windows. El TLS de cliente de macOS y Windows está
  escrito y compila, pero sus pruebas solo se han ejecutado en Linux.
- Algunas operaciones de `String` y `Any` siguen siendo intrínsecas del compilador; las listas aún no se declaran en `std.lang`.
- Una lambda con capturas solo va a C cuando la biblioteca da un `void*` de contexto como parámetro
  (`Context`); si lo guarda en otro lado, el callback es una `export function`. Un struct de C no puede tener campos arreglo (salvo un texto,
  `char name[32]`, que se lee como `String`) ni uniones; se leen con una función en `ccode`.
- Un puntero de C (`T*`) no se indexa (`p[i]`) ni se le suma; para un arreglo de C, una función en `ccode`.
  `&x` solo vale como argumento de una función de C.
- La función que suelta un recurso (`released by`) recibe solo el recurso: si necesita más contexto (una
  tabla de funciones cargada con `dlopen`, como OpenSSL en `std.net`), va en `ccode`.
- Una biblioteca escrita en Larimar le da a C (y a los programas que la enlazan) números, `bool`, textos y
  handles de sus clases: las listas, los callbacks y los errores todavía no la cruzan.
- No se puede vaciar una memoria a mano (`clear()`); se libera al final de su bloque.
- El compilador decide sin ejecutar si una función crea su resultado. Si a veces devuelve algo nuevo y a
  veces algo que ya existía, se la trata como si siempre creara: lo que devuelve vive en la memoria de
  la llamada (para guardarlo más tiempo, `in default` o `clone()`).
- Las lambdas, y por tanto los literales de interfaz, no pueden lanzar errores.
- Una lambda no puede capturar otra del mismo tipo.
- Un enum no puede contener otro valor de su mismo tipo (usa una clase para estructuras recursivas).
- Los nombres de tipos, métodos y variantes deben ser ASCII; las variables y los campos pueden usar cualquier letra.
- Ningún nombre puede contener `__`.

---

## 31. Referencia rápida

```ts
// Módulos
import geo.shapes;                      // shapes.area(s)
import geo.shapes as g;                 // g.area(s)
import geo.shapes { Shape, area };      // area(s)
public function exported(): void { }

// Declaraciones
const MAX: int32 = 10;
let global: int32 = 0;
function f(a: int32, b: String): bool throws MyError { ... }
function add(p: Node, k: Node in p): void { p.kids.push(k); }   // k vive tanto como p (también: in default, in self)
struct S { let field: int32 = 0; function m(): void { } operator +(o: S): S { ... } }
class C extends Parent implements I { let field: String; override function m(): void { super.m(); } }
interface I { function m(): void; }
enum E { A, B(x: int32) }
test function adds(): void { checkInt(4, 2 + 2); }     // la ejecuta larimar test (std.test)

// Variables y valores
let x: int32 = 5;
let s: S = { field: 1 };
let o: C = C { field: "x" };                  // vive en la memoria de su bloque
let e: E = E.B { x: 3 };
let q: int32? = null;
let arr: int32[8] = [1, 2];
let items: int32[*] = [];
let last: int32 = items.pop();
let fn: (int32) -> int32 = (n) -> { return n + x; };

// Memoria (automática: temporales de la instrucción, memoria del bloque, la de quien llama)
let text: String = "hello ${x}";                // en la memoria del bloque
let kept: String = "for ever ${x}" in default;  // todo el programa
let memory: byte[*] = [] in heap;               // una memoria propia
let made: String = build(x) in memory;          // el resultado de una llamada, ahí
let copy: String = text.clone();

// Control
if (c) { } else if (d) { } else { }
while (c) { }
for (i in 0..10) { }
for (i, v in items) { }
let r: int32 = switch (e) { case A -> 0; case B { x } -> x; };
if (pet is Dog d) { println(d.breed); }
try { f(1, "a"); } catch (MyError err) { }
throw MyError.Something;

// Opcionales
let v: int32 = q ?? 0;
let w: int32 = q!;
if (q != null) { let z: int32 = q + 1; }
if (q == null) { return; }              // desde aquí, q no es null
let k: String = q > 0 ? "pos" : "neg";

// C
cinclude "<stdio.h>";
native function puts(text: String): int32;
native function cExit(code: int32): void = exit;           // otro nombre en C
native const EOF: int32;
native const SIZE: int32 = c"(int)sizeof(long)";
native let errno: int32;
native type CFile = FILE* released by fclose;               // un recurso: se suelta con su memoria
native function fopen(path: String, mode: String): CFile?;
native function fclose(f: CFile): int32;
native function strdup(text: String): String released by free;   // un texto de C: se copia y se libera
native struct Node = c"struct node" { let next: Node*; let name: String; }
native type Doc = Doc* released by doc_close {                  // un tipo de C con miembros
    let id: int32;                                              // un campo: d.id es d->id
    native function title(): String = doc_title;                // d.title() es doc_title(d)
}
native type ItemFn = (int32, Context) -> void;                  // un callback con contexto:
native function each(f: ItemFn, data: Context): void;           // each((i) -> { ... }) acepta lambdas
ccode { static int twice_all(int x) { return lar"twice"(x); } }   // lar"..." nombra a Larimar desde C
two_results(&a, &b);                                            // & solo como argumento de C
release(file);                                                  // soltarlo antes
#when windows                                                   // elegido al compilar el C; cada directiva
    let sep: String = "\\";                                     // sola en su línea; #when, #else y #end
#else                                                           // de una elección, en la misma columna
    let sep: String = "/";
#end                                                            // sep sigue: todas las ramas lo declaran

// Literales
let c: byte = 'a';
let page: String = """
    <p>${text}</p>
    """;
let sql: String = raw"""
    SELECT * FROM users WHERE name = "x\y";
    """;                                  // tal cual: sin escapes ni ${...}

// Texto
let w: String = text.trim().substring(0, 3);          // vistas
let up: String = text.toUpperCase();                 // texto nuevo
let n: int64 = "42".toInt() ?? 0;
let sb: StringBuilder = {};
sb.add("x = ${n}");

// Programa y biblioteca estándar
// main puede recibir los argumentos: main(args: String[])
import std.io.files as Files;
let content: String = Files.readString(args[0]);

// Any
let t: Any = { 1, "two", name: "x", inner: { 3 } };
let n: int32 = t.port as int32 ?? 80;
for (k, v in t.fields) { }

// Hilos
synchronized class Box { let n: int32 = 0; function inc(): void { self.n += 1; } }
function take(): int32 wait until (self.n > 0) { ... }           // en una clase synchronized: espera a que se cumpla
let onConnect: (TcpSocket) -> void thread safe;                 // la llaman otros hilos: su lambda se comprueba
let th: Thread = { run: () -> { box.inc(); } };   // al liberarse su memoria, se espera a que termine
th.start();
th.join();

// Fallos del programa
panic("no debería pasar: ${x}");                     // se detiene con el mensaje (código 101)

// C
cinclude "<math.h>";
native function sqrt(x: float64): float64;
native type Handle;                                   // void*
native type File = FILE*;                             // un tipo de C concreto
native struct Point { let x: float32; let y: float32; }    // un struct de C
native type Op = (int32, int32) -> int32;             // un puntero a función de C
export function restar(a: int32, b: int32): int32 { return a - b; }   // C puede llamarla
export function nombre(id: int32): String = lm_nombre { return "n${id}"; }  // su nombre en C; C libera el texto

// larimar.toml de una biblioteca: build/<name>/ con lib<name>.a, <name>.h, <name>.lar, <name>.interface
// [project] kind = "library"      [library] type = "static" (o "dynamic"), prefix = "tk"
// [c] static_libraries / static_library_paths, dynamic_libraries / dynamic_library_paths
```
