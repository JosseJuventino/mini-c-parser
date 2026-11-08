# mini-c-parser

Analizador léxico (lexer) y sintáctico (parser) hecho en Python para una parte pequeña del lenguaje C, a la que llamamos **Mini-C**.

No se necesita instalar ninguna librería: todo usa lo que ya viene con Python.

## Descripción del proyecto

Mini-C recibe un fragmento de código, revisa si está bien escrito según una gramática y, si lo está, muestra el árbol sintáctico que construyó. Si encuentra un error, dice en qué línea y columna está.

El trabajo se divide en dos partes:

- **Lexer** (`src/lexer.py`): lee el texto carácter por carácter y lo separa en **tokens**, que son las "palabras" del lenguaje: `int`, `edad`, `=`, `20`, `;`, etc. Cada token guarda su tipo, su valor y la línea y columna donde aparece. Para reconocerlos se usa una expresión regular con un grupo por cada tipo de token. Si aparece un carácter que no pertenece al lenguaje (por ejemplo `@`), aquí se detecta el error léxico.
- **Parser** (`src/parser.py`): recibe la lista de tokens y revisa que vengan en un orden permitido por la gramática. Es un **parser descendente recursivo**: cada regla de la gramática es un método de la clase `Parser`, y los métodos se llaman entre sí igual que las reglas se usan unas a otras. Por ejemplo, `expresion()` llama a `termino()`, que llama a `factor()`. Mientras avanza, cada método crea un nodo del árbol.

Un ejemplo de código que Mini-C acepta:

```c
int edad = 20;
edad = edad + 5 * 2;

if (edad >= 18) {
    int resultado = edad * 2;
} else {
    edad = 0;
}
```

## Subconjunto de C seleccionado

El parser solamente reconoce un subconjunto pequeño de C, no todo el lenguaje.

### Lo que sí admite

- **Declaraciones de variables:** solamente de tipo `int` y con un valor inicial, por ejemplo `int edad = 20;`.
- **Asignaciones:** `edad = edad + 5;`.
- **Operaciones aritméticas:** suma (`+`), resta (`-`), multiplicación (`*`) y división (`/`), respetando que `*` y `/` se agrupan antes que `+` y `-`.
- **Paréntesis:** para agrupar operaciones y cambiar el orden, por ejemplo `(edad + 5) * 2`.
- **Números enteros e identificadores** dentro de las expresiones.
- **Varias instrucciones** seguidas, cada una terminada en punto y coma (`;`).
- **Condicionales `if` e `if-else`:** la condición va entre paréntesis y cada rama va entre llaves. El `else` es opcional.
- **Operadores de comparación:** `==`, `!=`, `<`, `>`, `<=` y `>=`, con expresiones aritméticas a ambos lados, por ejemplo `if ((edad + 2) * 3 > limite - 1) { }`.
- **Bloques:** dentro de las llaves puede ir cualquier instrucción, incluso otro `if` (anidado). También se permiten bloques vacíos (`{ }`).

### Lo que todavía no admite

- `else if` (aunque se puede escribir un `if` dentro del bloque del `else`).
- `switch`.
- Ciclos (`for`, `while`, `do while`).
- Funciones, incluida `main()`.
- `#include`, `std::cout` y cualquier otra cosa propia de C++.
- Otros tipos de datos como `float`, `double` o `char`.
- Declaraciones sin inicializar, como `int edad;`.
- Operadores lógicos (`&&`, `||`, `!`).
- `if` sin llaves, como `if (x > 0) x = 1;`.
- Operadores unarios, como `-5`.
- Comentarios (`//` o `/* */`).

## Gramática formal

Cada regla corresponde a un método de la clase `Parser` en `src/parser.py`. Está escrita en EBNF:

- `*` significa "cero o más veces".
- `?` significa "opcional" (cero o una vez).
- `|` separa alternativas.
- Lo que está entre comillas es un símbolo literal y lo que está en mayúsculas es un token que viene del lexer.

```text
programa       → sentencia*

sentencia      → declaracion
               | asignacion
               | condicional

declaracion    → INT ID "=" expresion ";"
asignacion     → ID "=" expresion ";"

condicional    → IF "(" condicion ")" bloque
                 (ELSE bloque)?

bloque         → "{" sentencia* "}"

condicion      → expresion op_comparacion expresion

op_comparacion → "==" | "!=" | "<" | ">"
               | "<=" | ">="

expresion      → termino (("+" | "-") termino)*
termino        → factor (("*" | "/") factor)*
factor         → NUMERO | ID | "(" expresion ")"
```

Como la comparación está en su propia regla (`condicion`) y no dentro de `expresion`, la precedencia de `+`, `-`, `*` y `/` no cambia, y la comparación siempre se hace al final, entre dos expresiones ya agrupadas. Por eso tampoco se puede escribir una comparación en una asignación, como `x = a > b;`.

En el código, cada `*` es un ciclo `while` y cada `?` es un `if`. Por ejemplo, `(ELSE bloque)?` es el `if self.actual().tipo == "ELSE"` de `condicional()`.

### La misma gramática en BNF

Esta es la misma gramática en BNF estricta, donde las repeticiones y las partes opcionales se escriben con reglas recursivas y la cadena vacía (`ε`):

```text
<programa>         ::= <lista_sentencias>

<lista_sentencias> ::= <sentencia> <lista_sentencias>
                     | ε

<sentencia>        ::= <declaracion>
                     | <asignacion>
                     | <condicional>

<declaracion>      ::= "int" <id> "=" <expresion> ";"
<asignacion>       ::= <id> "=" <expresion> ";"

<condicional>      ::= "if" "(" <condicion> ")" <bloque> <parte_else>
<parte_else>       ::= "else" <bloque>
                     | ε

<bloque>           ::= "{" <lista_sentencias> "}"

<condicion>        ::= <expresion> <op_comparacion> <expresion>
<op_comparacion>   ::= "==" | "!=" | "<" | ">" | "<=" | ">="

<expresion>        ::= <termino> <resto_expresion>
<resto_expresion>  ::= "+" <termino> <resto_expresion>
                     | "-" <termino> <resto_expresion>
                     | ε

<termino>          ::= <factor> <resto_termino>
<resto_termino>    ::= "*" <factor> <resto_termino>
                     | "/" <factor> <resto_termino>
                     | ε

<factor>           ::= <numero>
                     | <id>
                     | "(" <expresion> ")"
```

Los terminales `<id>` y `<numero>` los reconoce el lexer: `<id>` es una letra o `_` seguida de letras, dígitos o `_` (sin contar las palabras reservadas `int`, `if` y `else`), y `<numero>` es una secuencia de uno o más dígitos.

Algunas notas sobre la gramática:

- **No hay ambigüedad del "else colgante".** En C normal, `if (a) if (b) x; else y;` es ambiguo porque no se sabe a cuál `if` pertenece el `else`. Aquí no pasa porque las llaves son obligatorias: el `else` siempre va justo después de la `}` de su `if`, así que solo hay un árbol posible.
- **La gramática es LL(1).** Con solo mirar el token actual se sabe qué regla aplicar, así que se puede implementar con descenso recursivo sin retroceder.

## Funcionamiento

El recorrido completo es:

```text
Código fuente → Lexer → Tokens → Parser → Árbol sintáctico
```

1. `src/main.py` lee el archivo `.cpp` (o usa el ejemplo predeterminado).
2. `tokenizar()` convierte el texto en una lista de tokens y agrega un token `EOF` al final para marcar dónde termina el código.
3. `Parser(tokens).parsear()` llama a `sentencia()` una y otra vez hasta llegar a `EOF`.
4. Si todo cuadra, se imprime el árbol. Si no, se muestra el error con su línea y columna.

### ¿Cómo decide `sentencia()` qué analizar?

Mira solamente el tipo del token actual:

| Token actual | Qué se analiza |
| --- | --- |
| `INT` | `declaracion()` |
| `ID` | `asignacion()` |
| `IF` | `condicional()` |
| `ELSE` | Error: un `else` sin un `if` antes |
| Cualquier otro | Error: se esperaba una declaración, asignación o `if` |

Un `else` correcto nunca llega a `sentencia()`, porque `condicional()` lo consume justo después del bloque del `if`. Por eso, si `sentencia()` ve un `else`, es que está suelto.

### ¿Por qué se pueden anidar condicionales?

Porque las reglas se llaman en círculo:

```text
sentencia() → condicional() → bloque() → sentencia() → ...
```

`condicional()` usa `bloque()` para cada rama, y `bloque()` llama a `sentencia()` hasta encontrar la `}`. Como `sentencia()` puede volver a llamar a `condicional()`, dentro de un bloque puede ir otro `if`, y dentro de ese otro más. No hace falta escribir nada especial para los anidados: sale solo de la recursión.

### Ejemplo paso a paso

Para este código:

```c
if (edad >= 18) {
    edad = edad + 1;
}
```

1. El lexer genera: `IF`, `(`, `ID`, `>=`, `NUMERO`, `)`, `{`, `ID`, `=`, `ID`, `+`, `NUMERO`, `;`, `}`. Las palabras `if` y `else` solo se toman como reservadas si están escritas exactamente así; `ifVariable` sigue siendo un identificador normal.
2. `sentencia()` ve `IF` y llama a `condicional()`.
3. `condicional()` consume `if` y `(`, y llama a `condicion()`.
4. `condicion()` lee una expresión (`edad`), revisa que siga un operador de comparación (`>=`) y lee la otra expresión (`18`).
5. `condicional()` consume `)` y llama a `bloque()`.
6. `bloque()` consume `{`, llama a `sentencia()` hasta encontrar `}` y la consume. Si el código se acaba antes, avisa dónde se abrió la llave que quedó sin cerrar.
7. Si el siguiente token es `ELSE`, se consume y se analiza un segundo bloque. Si no, el condicional termina ahí.

El árbol que se genera:

```text
Programa
  Sentencia
    Condicional
      if
      (
      Condicion
        Expresion
          Termino
            Factor
              edad
        >=
        Expresion
          Termino
            Factor
              18
      )
      Bloque
        {
        Sentencia
          Asignacion
            edad
            =
            Expresion
              ...
            ;
        }
```

Si hubiera un `else`, después del primer `Bloque` aparecerían `else` y un segundo `Bloque`.

## Ejecución

Se necesita **Python 3.9 o superior** (se desarrolló con Python 3.13). Todos los comandos se ejecutan desde la carpeta principal del proyecto.

```bash
git clone https://github.com/JosseJuventino/mini-c-parser.git
cd mini-c-parser
```

Es importante usar `python -m src.main` y no `python src/main.py`, porque los archivos se importan entre sí con imports relativos.

### Analizar un archivo `.cpp`

```bash
python -m src.main ejemplos/validos/condicional_else.cpp
python -m src.main ejemplos/invalidos/condicion_incompleta.cpp
```

Para probar otro código, basta con guardarlo en un archivo `.cpp` (en UTF-8) y pasar su ruta. Ya no hace falta modificar `src/main.py`.

Sin argumentos, se analiza un ejemplo predeterminado:

```bash
python -m src.main
```

### Ver los tokens

Con `--tokens` (o `-t`) se muestra primero la lista de tokens con su posición, y después el árbol:

```bash
python -m src.main --tokens ejemplos/validos/condicional.cpp
```

```text
Tokens reconocidos:
  LÍNEA:COL  TIPO      VALOR
  1:1        INT       int
  1:5        ID        edad
  1:10       =         =
  1:12       NUMERO    20
  1:14       ;         ;
  ...
  4:1        IF        if
  4:4        (         (
  4:5        ID        edad
  4:10       >=        >=
  ...
```

### Modo demostración

```bash
python -m src.main --demo
```

Recorre todos los archivos de `ejemplos/validos` y `ejemplos/invalidos`. Para cada uno muestra el resultado esperado, el obtenido, si coinciden, y el árbol (si es válido) o el error (si es inválido). Un ejemplo inválido cuenta como correcto cuando el analizador lo **rechaza**. Al final aparece un resumen:

```text
RESUMEN DE LA DEMOSTRACIÓN

Ejemplos procesados: 14
Comportamientos correctos: 14
Comportamientos incorrectos: 0
```

`--demo` también funciona con `--tokens`, y encuentra la carpeta `ejemplos` aunque el comando se ejecute desde otra carpeta.

### Ayuda y códigos de salida

```bash
python -m src.main --help
```

| Código | Significado |
| --- | --- |
| `0` | El código es válido (o, en `--demo`, todos los ejemplos se comportaron como se esperaba). |
| `1` | El código tiene un error léxico o sintáctico (o, en `--demo`, hubo alguna diferencia). |
| `2` | No se pudo leer el archivo (no existe, es una carpeta o no está en UTF-8), o los argumentos son incorrectos. |

### Desde VS Code

En `.vscode/launch.json` hay dos configuraciones: **Debug mini-c-parser** (ejemplo predeterminado) y **Demo mini-c-parser** (`--demo`). Se elige una en la pestaña de ejecución y se presiona **F5**.

### Pruebas

```bash
python -m unittest discover -s tests -v
```

Hay tres archivos de pruebas:

- `tests/test_lexer.py`: tokens, palabras reservadas, operadores de comparación, línea y columna.
- `tests/test_parser.py`: árboles de entradas válidas, errores en entradas inválidas y condicionales.
- `tests/test_main.py`: lectura de archivos, todos los ejemplos de la carpeta `ejemplos`, mensajes de error, `--tokens`, `--demo` y códigos de salida (algunas pruebas ejecutan el programa con `subprocess`, igual que desde la terminal).

Si todo funciona, al final aparece `OK`.

## Ejemplos válidos e inválidos

Los ejemplos están en la carpeta `ejemplos`. Usan la extensión `.cpp` solo para organizarlos y que el editor los coloree, pero **no son programas C++ completos**: son fragmentos que usan únicamente el subconjunto de Mini-C. No tienen `#include`, `main()` ni `std::cout`, y probablemente no compilarían con un compilador de C++. Mini-C no analiza todo C ni todo C++.

### Válidos

| Archivo | Qué muestra |
| --- | --- |
| `declaraciones.cpp` | Varias declaraciones `int`. |
| `operaciones.cpp` | Suma, resta, multiplicación y división con su precedencia. |
| `parentesis.cpp` | Paréntesis anidados que cambian el orden de las operaciones. |
| `condicional.cpp` | Dos `if` sin `else`, uno con expresiones a ambos lados de `!=`. |
| `condicional_else.cpp` | Un `if-else`. |
| `condicional_anidado.cpp` | Un `if-else` dentro de otro `if-else`. |

Por ejemplo, `condicional_anidado.cpp`:

```c
int edad = 20;
int resultado = 0;

if (edad >= 18) {
    if (edad == 20) {
        resultado = 100;
    } else {
        resultado = 50;
    }
} else {
    resultado = 0;
}
```

Resultado: `Código sintácticamente válido` y su árbol, con un nodo `Condicional` dentro del primer `Bloque` del otro.

### Inválidos

| Archivo | Código con el error | Mensaje |
| --- | --- | --- |
| `sin_expresion.cpp` | `int edad = ;` | `Línea 1, columna 12: se esperaba un número, identificador o '(', pero se encontró ';'` |
| `sin_punto_coma.cpp` | `int edad = 20` (y en la línea 2 sigue otra instrucción) | `Línea 2, columna 1: se esperaba ';', pero se encontró 'edad'` |
| `sin_identificador.cpp` | `int = 20;` | `Línea 1, columna 5: se esperaba 'ID', pero se encontró '='` |
| `parentesis_sin_cerrar.cpp` | `int resultado = (edad + 5 * 2;` | `Línea 2, columna 30: se esperaba ')', pero se encontró ';'` |
| `condicion_incompleta.cpp` | `if (edad >=) {` | `Línea 3, columna 12: se esperaba un número, identificador o '(', pero se encontró ')'` |
| `bloque_sin_cerrar.cpp` | Un `if` cuyo bloque nunca se cierra | `Línea 5, columna 1: se esperaba '}' para cerrar el bloque abierto en la línea 3, columna 17, pero se encontró 'fin del código'` |
| `else_sin_if.cpp` | Una asignación entre la `}` del `if` y el `else` | `Línea 7, columna 1: se encontró 'else' sin un 'if' antes` |
| `caracter_invalido.cpp` | `int total = edad @ 2;` | `Carácter inválido '@' en línea 2, columna 18` (error léxico) |

Todos los errores salen como un mensaje del analizador (`Error léxico: ...` o `Error sintáctico: ...`), nunca como un fallo interno de Python.

Otros casos que también se rechazan (están en las pruebas):

| Código | Por qué falla |
| --- | --- |
| `if edad >= 18 { edad = 20; }` | Faltan los paréntesis de la condición. |
| `if (edad) { }` | Falta el operador de comparación. |
| `if (edad > 1) edad = 2;` | Las ramas del `if` siempre necesitan llaves. |

## Limitaciones

- **Solo se valida la sintaxis.** El programa no ejecuta las instrucciones, no evalúa si una condición es verdadera o falsa y no calcula ningún resultado.
- **No hay análisis semántico.** No se revisa si una variable fue declarada antes de usarla ni si se declara dos veces.
- **Las llaves son obligatorias en los condicionales.** Por eso el problema clásico del *dangling else* (un `else` que podría pertenecer a dos `if` distintos cuando no hay llaves) queda fuera de este subconjunto.
- **Se detiene en el primer error.** Si un archivo tiene varios errores, solo se informa el primero.
- Todo lo que aparece en [Lo que todavía no admite](#lo-que-todavía-no-admite) produce un error, aunque sea C válido.

## Estructura del proyecto

```text
src/
  lexer.py       # Convierte el código en tokens
  parser.py      # Analiza los tokens y genera el árbol sintáctico
  main.py        # Interfaz de terminal: archivos, --tokens y --demo
ejemplos/
  validos/       # Fragmentos que el parser debe aceptar
  invalidos/     # Fragmentos que el parser debe rechazar
tests/
  test_lexer.py
  test_parser.py
  test_main.py
DEMO.md          # Guion para la exposición
```
