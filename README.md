# mini-c-parser

Este proyecto es un analizador léxico (lexer) y sintáctico (parser) hecho en Python para interpretar una parte básica del lenguaje C.

Por ahora permite reconocer declaraciones de variables, asignaciones, operaciones aritméticas y condicionales `if` / `if-else`, por ejemplo:

```c
int edad = 20;
edad = edad + 5 * 2;

if (edad >= 18) {
    int resultado = edad * 2;
} else {
    edad = 0;
}
```

Si el código es válido, el programa genera un árbol sintáctico donde se puede ver cómo interpreta cada instrucción. Si hay algún error, muestra la línea y columna donde está el problema.

No se necesita instalar ninguna librería adicional, ya que solamente se utilizan las que vienen incluidas con Python.

## ¿Qué permite analizar?

El parser solamente reconoce un subconjunto pequeño de C, no todo el lenguaje.

Actualmente admite:

- **Declaraciones de variables:** solamente de tipo `int` y con un valor inicial, por ejemplo `int edad = 20;`.
- **Asignaciones:** permite asignar valores o expresiones a variables, por ejemplo `edad = edad + 5;`.
- **Operaciones aritméticas:** suma (`+`), resta (`-`), multiplicación (`*`) y división (`/`).
- **Paréntesis:** se pueden utilizar para agrupar operaciones y cambiar su orden.
- **Números enteros e identificadores:** reconoce números y nombres de variables dentro de las expresiones.
- **Varias instrucciones:** permite analizar varias declaraciones o asignaciones, siempre que terminen con punto y coma (`;`).
- **Condicionales `if` e `if-else`:** la condición va entre paréntesis y cada rama va entre llaves, por ejemplo `if (edad >= 18) { edad = 0; }`. El `else` es opcional.
- **Operadores de comparación:** `==`, `!=`, `<`, `>`, `<=` y `>=`, con expresiones aritméticas a ambos lados, por ejemplo `if ((edad + 2) * 3 > limite - 1) { }`.
- **Bloques:** dentro de las llaves se pueden poner declaraciones, asignaciones y otros `if` (anidados). También se permiten bloques vacíos (`{ }`).

Por ejemplo, este código es válido:

```c
int edad = 20;
int resultado = (edad + 5) * 2;
edad = resultado / 5;

if ((edad + 2) >= 18) {
    if (edad == 20) {
        edad = 21;
    }
} else {
}
```

También se respeta la prioridad de los operadores, es decir, las multiplicaciones y divisiones se agrupan antes que las sumas y restas. La comparación siempre se hace al final, entre las dos expresiones ya agrupadas.

### Ejemplos inválidos

Estos son algunos códigos que el parser rechaza y el error que muestra:

| Código | Error |
| --- | --- |
| `if (edad >=) { edad = 20; }` | Falta la expresión del lado derecho de `>=`. |
| `if (edad >= 18) { edad = 20;` | Falta la llave `}` que cierra el bloque. |
| `if edad >= 18 { edad = 20; }` | Faltan los paréntesis de la condición. |
| `else { edad = 20; }` | Hay un `else` sin un `if` antes. |
| `if (edad >= 18) { edad = ; }` | La asignación del bloque no tiene expresión. |
| `if (edad) { }` | Falta el operador de comparación. |
| `if (edad > 1) edad = 2;` | Las ramas del `if` siempre necesitan llaves. |

Por ejemplo, para el segundo caso el mensaje es:

```text
Línea 2, columna 15: se esperaba '}' para cerrar el bloque abierto en la línea 1, columna 17, pero se encontró 'fin del código'
```

### ¿Qué no admite?

Por ahora no se han implementado otras construcciones de C, como:

- `else if` (aunque se puede escribir un `if` dentro del bloque del `else`).
- `switch`.
- Ciclos (`for`, `while`, `do while`).
- Funciones.
- Otros tipos de datos como `float`, `double` o `char`.
- Declaraciones sin inicializar, como `int edad;`.
- Operadores lógicos (`&&`, `||`, `!`).
- `if` sin llaves, como `if (x > 0) x = 1;`.
- Operadores unarios, como `-5`.

También hay que tener en cuenta que **el programa solamente realiza análisis léxico y sintáctico**. No ejecuta el código ni comprueba errores semánticos, como utilizar una variable que no ha sido declarada. Tampoco evalúa si una condición es verdadera o falsa: solo revisa que esté bien escrita.

## Gramática

Esta es la gramática que sigue el parser. Cada regla corresponde a un método de la clase `Parser` en `src/parser.py`.

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

Como la comparación está en su propia regla (`condicion`) y no dentro de `expresion`, la precedencia de `+`, `-`, `*` y `/` no cambia. Por eso tampoco se puede escribir una comparación en una asignación, como `x = a > b;`.

## ¿Cómo se procesa un condicional?

Tomemos este código:

```c
if (edad >= 18) {
    edad = edad + 1;
}
```

1. El lexer lo convierte en tokens: `IF`, `(`, `ID`, `>=`, `NUMERO`, `)`, `{`, `ID`, `=`, `ID`, `+`, `NUMERO`, `;`, `}`. Las palabras `if` y `else` solo se toman como reservadas si están escritas exactamente así; por ejemplo, `ifVariable` sigue siendo un identificador normal.
2. En `sentencia`, el parser ve que el token actual es `IF` y llama a `condicional`.
3. `condicional` consume `if` y `(`, y llama a `condicion`.
4. `condicion` lee una expresión (`edad`), revisa que siga un operador de comparación (`>=`) y lee la otra expresión (`18`).
5. De vuelta en `condicional`, se consume `)` y se llama a `bloque`.
6. `bloque` consume `{` y llama a `sentencia` una y otra vez hasta encontrar `}`. Como `bloque` vuelve a llamar a `sentencia`, dentro de un bloque puede ir cualquier instrucción, incluso otro `if`.
7. Al final, si el siguiente token es `ELSE`, se consume y se analiza un segundo bloque. Si no, el condicional termina ahí.

El árbol que se genera se ve así:

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

## Estructura del proyecto

```text
src/
  lexer.py     # Convierte el código en tokens
  parser.py    # Analiza los tokens y genera el árbol sintáctico
  main.py      # Archivo principal para ejecutar el programa
tests/
  test_lexer.py
  test_parser.py
```

## 1. Clonar el proyecto

Primero clonamos el repositorio y entramos a la carpeta del proyecto:

```bash
git clone <url-del-repositorio>
cd mini-c-parser
```

Para ejecutarlo se necesita tener instalado **Python 3.9 o superior**. El proyecto se desarrolló utilizando Python 3.13.

## 2. Ejecutar el programa

Desde la carpeta principal del proyecto ejecutamos:

```bash
python -m src.main
```

Es importante ejecutarlo de esta forma y no con `python src/main.py`, porque se utilizan imports relativos entre los archivos.

Si todo está correcto, debería aparecer algo parecido a esto:

```text
Código sintácticamente válido

Árbol de análisis sintáctico:
Programa
  Sentencia
    Declaracion
      int
      edad
      =
      Expresion
        Termino
          Factor
            20
      ;
  ...
```

Básicamente, el lexer se encarga de separar el código en tokens y después el parser analiza esos tokens para construir el árbol sintáctico.

Si quieren probar otro código, solamente tienen que modificar la variable `codigo` que está en `src/main.py`.

### Ejecutarlo desde VS Code

También se puede ejecutar directamente desde VS Code.

El proyecto ya tiene una configuración llamada **Debug mini-c-parser** en `.vscode/launch.json`.

Solo hay que abrir la carpeta del proyecto, tener instalada la extensión de Python y presionar **F5**.

## 3. Ejecutar las pruebas

Se agregaron pruebas para comprobar que tanto el lexer como el parser funcionen correctamente, incluyendo los condicionales (casos válidos, inválidos y la estructura de los nodos `Condicional`, `Condicion` y `Bloque`).

Desde la carpeta principal ejecutamos:

```bash
python -m unittest discover -s tests -v
```

Esto busca y ejecuta todas las pruebas de la carpeta `tests` y muestra cuáles pasaron o fallaron. También se puede seguir usando la forma anterior:

```bash
python -m unittest tests.test_lexer tests.test_parser -v
```

Si todo funciona correctamente, al final debería aparecer `OK`.