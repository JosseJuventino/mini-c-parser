# mini-c-parser

Este proyecto es un analizador léxico (lexer) y sintáctico (parser) hecho en Python para interpretar una parte básica del lenguaje C.

Por ahora permite reconocer declaraciones de variables, asignaciones y operaciones aritméticas, por ejemplo:

```c
int edad = 20;
edad = edad + 5 * 2;
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

Por ejemplo, este código es válido:

```c
int edad = 20;
int resultado = (edad + 5) * 2;
edad = resultado / 5;
```

También se respeta la prioridad de los operadores, es decir, las multiplicaciones y divisiones se agrupan antes que las sumas y restas.

### ¿Qué no admite?

Por ahora no se han implementado otras construcciones de C, como:

- Condicionales (`if`, `else`, `switch`).
- Ciclos (`for`, `while`, `do while`).
- Funciones.
- Otros tipos de datos como `float`, `double` o `char`.
- Declaraciones sin inicializar, como `int edad;`.
- Operadores de comparación y lógicos.
- Operadores unarios, como `-5`.

También hay que tener en cuenta que **el programa solamente realiza análisis léxico y sintáctico**. No ejecuta el código ni comprueba errores semánticos, como utilizar una variable que no ha sido declarada.

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

Se agregaron pruebas para comprobar que tanto el lexer como el parser funcionen correctamente.

Desde la carpeta principal ejecutamos:

```bash
python -m unittest tests.test_lexer tests.test_parser -v
```

Esto ejecuta las pruebas de ambos archivos y muestra cuáles pasaron o fallaron.

Si todo funciona correctamente, al final debería aparecer `OK`.