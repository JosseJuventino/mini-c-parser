Esta parte del proyecto adapta el análisis descendente recursivo a un conjunto limitado de oraciones en español. Utiliza un léxico definido manualmente para reconocer las palabras, comprobar las concordancias programadas y construir un árbol sintáctico.

La entrada se escribe directamente en la variable `oracion` de `mainEsp.py`. Al ejecutar ese archivo, el programa muestra el árbol si acepta la oración o un mensaje con el primer error encontrado.

### Archivos necesarios

| Archivo | Función |
| --- | --- |
| `mainEsp.py` | Contiene la oración de entrada, llama al lexer y al parser e imprime el resultado. |
| `lexerEsp.py` | Separa la oración en tokens y consulta la categoría de cada palabra en el léxico. |
| `lexico.py` | Define el diccionario `LEXICO`, con la categoría gramatical, el género y el número de las palabras reconocidas. |
| `parserEsp.py` | Define la clase `ParserEsp`, reconoce la estructura de la oración y construye el árbol. |
| `lexer.py` | Proporciona la clase `Token`, utilizada también por el lexer español. |
| `parser.py` | Proporciona la clase `Nodo`, utilizada para construir e imprimir el árbol. |

Con los imports de los archivos españoles, estos módulos deben estar disponibles en la misma carpeta y ser compatibles entre sí. La extensión reutiliza `Token` y `Nodo`; al ejecutar `mainEsp.py`.

### Requisitos

- **Python 3.9 o superior.**
- Los archivos indicados en la tabla anterior.
- Para la ejecución desde el editor: VS Code con soporte de Python y un intérprete seleccionado.

Esta parte utiliza la biblioteca estándar de Python. No requiere instalar spaCy ni descargar un modelo de lenguaje.

### Ejecutar desde VS Code

1. Abre en VS Code la carpeta que contiene los archivos del parser español.
2. Abre `mainEsp.py`.
3. Comprueba que la variable `oracion` contiene el texto que deseas analizar:

   ```python
   oracion = "La calabaza escribe el código"
   ```

4. Guarda el archivo.
5. Pulsa **Run Python File**.
6. Revisa el resultado en la terminal de VS Code.

Para esta entrada se muestra `Oración sintácticamente válida` y el árbol de análisis. Si la entrada se rechaza, se muestra `Error:` seguido de la causa.

### Ejecutar desde la terminal

Abre una terminal en la carpeta que contiene `mainEsp.py` y ejecuta:

```bash
python mainEsp.py
```

Si tu instalación utiliza el comando `python3`, ejecuta:

```bash
python3 mainEsp.py
```

Si los archivos están dentro de una subcarpeta del repositorio, sitúate primero en esa carpeta. Esta entrada se ejecuta como archivo: el comando `python -m src.main` descrito anteriormente corresponde a la interfaz de Mini-C.

### Probar otra oración

Para cambiar la entrada, modifica únicamente el texto de la variable `oracion` en `mainEsp.py`, guarda y vuelve a ejecutar el archivo. Por ejemplo:

```python
oracion = "Marcela come los dulces."
```

También puedes probar una subordinada:

```python
oracion = "El examen vio que Jaime dijo que Marcela corrigió."
```

`mainEsp.py` analiza una oración por ejecución. La versión documentada toma la entrada de esa variable; no lee una oración desde argumentos de terminal, un CSV ni un menú interactivo.

**Todas las palabras deben estar registradas en `LEXICO`.** Una oración puede ser correcta en español y rechazarse porque contiene una palabra desconocida o una estructura que la gramática no incluye.

### Ejemplo de árbol sintáctico

Para la entrada predeterminada:

```python
oracion = "La calabaza escribe el código"
```

La versión reformulada produce una salida como esta:

```text
Oración sintácticamente válida

Árbol de análisis sintáctico:
Programa
  Oracion
    Sujeto
      SN_fs
        la
        calabaza
    Verbo
      escribe
      Complemento
        SN
          SN_ms
            el
            código
        Complemento2
```

La sangría representa la relación entre los nodos. `SN_fs` identifica un sintagma nominal femenino singular y `SN_ms`, uno masculino singular. `Complemento2` agrupa las preposiciones y el adverbio opcionales. En este ejemplo no hay ninguno; la función de impresión omite sus nodos vacíos.

Las palabras aparecen en minúsculas porque el lexer normaliza la entrada antes de consultar el léxico.

### Funcionamiento

1. `mainEsp.py` toma el contenido de `oracion`.
2. `tokenizarEsp(oracion)` identifica las palabras, las convierte a minúsculas y consulta `LEXICO`.
3. El lexer expande las contracciones `al` en `a el` y `del` en `de el`, y añade el token `EOF` al final.
4. `ParserEsp(tokens).programa()` analiza la oración según las producciones y comprueba que se consuma toda la entrada.
5. Si se acepta, `imprimir_arbol()` recorre los nodos y muestra la estructura mediante sangría.
6. Si el lexer o el parser lanza un `SyntaxError`, `mainEsp.py` muestra el mensaje y termina el análisis de esa oración.

### Léxico y concordancia

Cada entrada de `LEXICO` tiene la forma `(categoria, genero, numero)`. Se utiliza `None` cuando un rasgo no corresponde:

```python
"calabaza": ("N", "f", "s"),
"calabazas": ("N", "f", "p"),
"escribe": ("V", None, "s"),
"dijo": ("V", None, "s"),
"rápidamente": ("ADV", None, None),
```

| Etiqueta | Significado |
| --- | --- |
| `DET` | Determinante. |
| `N` | Sustantivo. |
| `NP` | Nombre propio. |
| `Adj` | Adjetivo. |
| `V` | Verbo. |
| `PREP` | Preposición. |
| `ADV` | Adverbio. |
| `que` | Palabra que introduce la subordinada completiva. |

Los valores de género son `m` y `f`; los de número, `s` y `p`. Al generar los tokens se combinan con la categoría: por ejemplo, `calabaza` se reconoce como `N_fs` y `escribe` como `V_s`.

Las reglas comprueban género y número entre determinantes, sustantivos y adjetivos, y número entre el sujeto y el verbo. La persona verbal no está representada en estas etiquetas.

Para ampliar el vocabulario, añade la palabra en minúsculas a `LEXICO` con los rasgos adecuados. Añadir una palabra no incorpora automáticamente una estructura sintáctica nueva: para eso también deben ampliarse las producciones del parser.

### Gramática de referencia de la versión reformulada

La gramática presentada en el informe es libre de contexto. `|` separa alternativas, `ε` indica la cadena vacía y `EOF` marca el final de la entrada:

```text
programa      → oracion EOF
oracion       → sujeto_s verbo_s | sujeto_p verbo_p

sujeto_s      → sn_ms | sn_fs
sujeto_p      → sn_mp | sn_fp

sn_ms         → DET_ms N_ms adjs_ms | NP_ms
sn_fs         → DET_fs N_fs adjs_fs | NP_fs
sn_mp         → DET_mp N_mp adjs_mp | N_mp adjs_mp
sn_fp         → DET_fp N_fp adjs_fp | N_fp adjs_fp

adjs_ms       → Adj_ms adjs_ms | ε
adjs_fs       → Adj_fs adjs_fs | ε
adjs_mp       → Adj_mp adjs_mp | ε
adjs_fp       → Adj_fp adjs_fp | ε

verbo_s       → V_s complemento
verbo_p       → V_p complemento

complemento   → sn complemento2 | "que" oracion | complemento2
complemento2  → preps adverbio
sn            → sn_ms | sn_fs | sn_mp | sn_fp

preps         → sp preps | ε
sp            → PREP sn
adverbio      → ADV | ε
```

En `complemento`, el token actual permite distinguir un sintagma nominal, la palabra `que` o el cierre con preposiciones y adverbio opcionales. La alternativa vacía de ese cierre permite terminar cuando se alcanza `EOF`. En esta reformulación, la subordinada introducida por `que` contiene su propio cierre.

### Casos para la demostración

Para recorrer estos ejemplos, copia cada oración en la variable `oracion`, guarda `mainEsp.py` y ejecútalo de nuevo. Son casos de prueba manuales; esta entrada no los recorre automáticamente.

| Oración | Resultado esperado con la versión reformulada | Qué muestra |
| --- | --- | --- |
| `La calabaza escribe el código` | Aceptada. | Sujeto, verbo y complemento nominal; ejemplo del árbol anterior. |
| `Las calabazas pequeñas duermen furiosamente.` | Aceptada. | Concordancia, adjetivo y adverbio final. |
| `El esqueleto pequeño escribe rápidamente el código nuevo en la clase.` | Rechazada. | La gramática no permite continuar con el objeto después del adverbio. |
| `Marcela vio al fantasma con el telescopio.` | Aceptada con una estructura. | Grupos preposicionales y una oración con dos lecturas posibles. |
| `El examen que Jaime corrigió asustó a Jose.` | Rechazada en `que`. | Falta una regla de relativas dentro del sintagma nominal. |
| `Los fantasma come los dulces.` | Rechazada en `fantasma`. | Discordancia entre el determinante plural y el sustantivo singular. |
| `El examen vio que Jaime dijo que Marcela corrigió.` | Aceptada. | Subordinación completiva recursiva y ausencia de comprobación semántica. |
| `Los esqueletos escribe el código.` | Rechazada en `escribe`. | Discordancia de número entre sujeto y verbo. |
| `Las calabazas pequeños duermen furiosamente.` | Rechazada en `pequeños`. | Discordancia de género entre sustantivo y adjetivo. |

En los cinco casos centrales comparados en el informe se estudian el adverbio antes del objeto, el telescopio, la relativa, `Los fantasma` y la subordinación recursiva. Los demás ejemplos permiten mostrar el funcionamiento correcto y otras comprobaciones de concordancia.

Que una entrada se rechace no significa siempre que esté mal escrita en español. Hay que distinguir las discordancias de las construcciones válidas que esta gramática todavía no reconoce.

### Errores

Un ejemplo de discordancia es:

```python
oracion = "Los fantasma come los dulces."
```

El análisis se detiene al encontrar el sustantivo singular después del determinante plural:

```text
Error: Columna 5: se esperaba 'N_mp', pero se encontró 'fantasma'
```

Si aparece una palabra ausente del léxico, el error se produce antes de comenzar el análisis sintáctico. Por ejemplo:

```python
oracion = "El gato come los dulces."
```

```text
Error: Palabra desconocida 'gato' en columna 4
```

Se conserva la escritura de las palabras del léxico, incluidas las tildes. Por ejemplo, `código` y `codigo` son cadenas diferentes. El lexer ignora puntos y signos de interrogación o exclamación, entre otros signos definidos en `PATRON`; esto no implica que admita cualquier signo de puntuación.

### Alcance y limitaciones

- **Vocabulario limitado:** solo se reconocen las palabras registradas en `LEXICO`.
- **Sujeto explícito y anterior al verbo:** no se admiten ejemplos como `Escribimos el parser.` o `Come Marcela los dulces.`.
- **Modificadores en posiciones definidas:** los adjetivos nominales aparecen después del sustantivo y se admite un adverbio al final del grupo verbal.
- **Subordinación limitada:** se incluyen completivas introducidas por `que`, pero no relativas que modifiquen al sustantivo.
- **Una estructura por entrada aceptada:** no se enumeran las distintas lecturas de una oración ambigua.
- **Sin comprobación semántica:** aceptar `El examen vio que Jaime dijo que Marcela corrigió.` no significa que el programa evalúe su sentido.
- **Primer error:** el proceso se detiene ante el primer error léxico o sintáctico detectado.

Estas limitaciones describen la implementación. Los rechazos por reglas ausentes no demuestran, por sí solos, que esas construcciones sean imposibles de representar mediante otras gramáticas libres de contexto.

### Si no se ejecuta

| Mensaje o situación | Qué revisar |
| --- | --- |
| Aparece una palabra desconocida | Consulta `LEXICO`, revisa las tildes o incorpora la palabra con su categoría y rasgos. |
| El IDE utilizada no permite correr el código | Revisar que cuenta con la extensión correspondiente de Python |
| El programa no encuentra Nodo o Token | Revisar que los archivos lexer.py y parser.py se encuentran en la misma carpeta |
