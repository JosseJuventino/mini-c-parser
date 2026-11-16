# Extensión del parser al español

Parser descendente recursivo predictivo para un subconjunto controlado del
español. Valida oraciones, construye su árbol de derivación y comprueba, cada
vez que se ejecuta, que la gramática sobre la que opera es LL(1).

## Contenido

| Archivo | Qué contiene |
|---|---|
| `src/gramatica.py` | La gramática libre de contexto, escrita como datos |
| `src/ll1.py` | Cálculo de FIRST, FOLLOW y tabla LL(1); verificación de que la gramática es LL(1) |
| `src/lexico.py` | Vocabulario: 171 palabras con su categoría, género y número |
| `src/lexerEsp.py` | Lexer: convierte la oración en tokens usando el léxico |
| `src/parserEsp.py` | Parser: un método por cada no terminal de la gramática |
| `src/analizadorEsp.py` | Función `analizar(oracion)`: ejecuta lexer y parser y clasifica el resultado |
| `src/arbol_matplot.py` | Dibuja el árbol en una imagen PNG o SVG |
| `src/mainEsp.py` | Demostración con una oración |
| `src/pruebasEsp.py` | Recorre las 60 oraciones del corpus y guarda los árboles |
| `docs/ll1_reporte.txt` | FIRST, FOLLOW, condiciones y tabla LL(1) generados por `ll1.py` |
| `docs/ll1_tabla.csv` | La tabla LL(1) como tabla de doble entrada (se abre en Excel) |
| `tests/test_esp/` | Pruebas del lexer, del parser y de la verificación LL(1) |

`src/lexer.py` y `src/parser.py` son el lexer y el parser de C de la Fase 1.
El parser del español reutiliza de ellos las clases `Token` y `Nodo`.

## Cómo ejecutar

Requisitos: Python 3.10 o superior. Para generar las imágenes de los árboles
también se necesita matplotlib (`pip install matplotlib`).

Desde la carpeta `esp-parser/src`:

```
python mainEsp.py        analiza la oración escrita en el archivo
python pruebasEsp.py     analiza las 60 oraciones del corpus
python ll1.py            muestra FIRST, FOLLOW, condiciones y tabla LL(1)
python ll1.py ../docs/ll1_reporte.txt ../docs/ll1_tabla.csv
                         además vuelve a generar los dos archivos de docs
```

Desde la carpeta `esp-parser`:

```
python -m unittest discover -s tests/test_esp -v
```

Las pruebas no necesitan matplotlib.

## La gramática

G = (N, T, P, S), con S = `Programa`.

- **No terminales (19):** `Programa`, `Oracion`, `Sujeto_s`, `Sujeto_p`,
  `SN_ms`, `SN_fs`, `SN_mp`, `SN_fp`, `Adjs_ms`, `Adjs_fs`, `Adjs_mp`,
  `Adjs_fp`, `SV_s`, `SV_p`, `SN`, `Complemento`, `Complemento2`, `Preps`,
  `Adverbio`.
- **Terminales (24):** los tipos de token que produce el lexer: `DET_ms`,
  `DET_fs`, `DET_mp`, `DET_fp`, `N_ms`, `N_fs`, `N_mp`, `N_fp`, `NP_ms`,
  `NP_fs`, `Adj_ms`, `Adj_fs`, `Adj_mp`, `Adj_fp`, `Adj_cs`, `Adj_cp`,
  `PRON_s`, `PRON_p`, `V_s`, `V_p`, `PREP`, `ADV`, `que` y `EOF`.
- **Sufijos:** `m`, `f` y `c` son género masculino, femenino y común (la
  misma forma sirve para los dos, como "verde"); `s` y `p` son singular y
  plural.
- **EOF** es el token que el lexer agrega al final de la oración. Cumple el
  papel del marcador de fin de cadena `$`.

**Producciones (43):**

```
Programa -> Oracion EOF
Oracion -> Sujeto_s SV_s
Oracion -> Sujeto_p SV_p
Sujeto_s -> SN_ms
Sujeto_s -> SN_fs
Sujeto_s -> PRON_s
Sujeto_p -> SN_mp
Sujeto_p -> SN_fp
Sujeto_p -> PRON_p
SN_ms -> DET_ms N_ms Adjs_ms
SN_ms -> NP_ms
SN_fs -> DET_fs N_fs Adjs_fs
SN_fs -> NP_fs
SN_mp -> DET_mp N_mp Adjs_mp
SN_mp -> N_mp Adjs_mp
SN_fp -> DET_fp N_fp Adjs_fp
SN_fp -> N_fp Adjs_fp
Adjs_ms -> Adj_ms Adjs_ms
Adjs_ms -> Adj_cs Adjs_ms
Adjs_ms -> ε
Adjs_fs -> Adj_fs Adjs_fs
Adjs_fs -> Adj_cs Adjs_fs
Adjs_fs -> ε
Adjs_mp -> Adj_mp Adjs_mp
Adjs_mp -> Adj_cp Adjs_mp
Adjs_mp -> ε
Adjs_fp -> Adj_fp Adjs_fp
Adjs_fp -> Adj_cp Adjs_fp
Adjs_fp -> ε
SV_s -> V_s Complemento
SV_p -> V_p Complemento
SN -> SN_ms
SN -> SN_fs
SN -> SN_mp
SN -> SN_fp
Complemento -> SN Complemento2
Complemento -> que Oracion
Complemento -> Complemento2
Complemento2 -> Preps Adverbio
Preps -> PREP SN Preps
Preps -> ε
Adverbio -> ADV
Adverbio -> ε
```

Qué cubre:

- Oraciones Sujeto-Verbo-Objeto, con objeto opcional.
- Concordancia de género y número entre determinante, sustantivo y
  adjetivos, y de número entre sujeto y verbo.
- Modificadores: adjetivos después del sustantivo, frases preposicionales
  después del objeto y un adverbio al final.
- Una oración subordinada introducida por "que", que puede anidarse.
- Dos tiempos verbales, presente y pretérito, registrados en el léxico.

## Por qué la gramática es LL(1)

Definición usada (la vista en clase). Para cada par de producciones de un
mismo no terminal, A -> α y A -> β:

1. **Condición (i):** FIRST(α) y FIRST(β) no tienen elementos en común.
2. **Condición (ii):** si ε está en FIRST(α), ni FIRST(α) ni FIRST(β) tienen
   terminales en común con FOLLOW(A).

`ll1.py` calcula FIRST y FOLLOW, comprueba las dos condiciones y construye
la tabla con las reglas de clase: A -> α va en M[A, a] por cada terminal a de
FIRST(α) y, si ε está en FIRST(α), también en M[A, b] por cada b de FOLLOW(A).
Una celda con dos producciones es un conflicto.

Resultado para esta gramática: 19 no terminales, 24 terminales, 43
producciones, 92 celdas ocupadas y **0 conflictos**. Las condiciones (i) y
(ii) se cumplen en todos los no terminales. El detalle completo está en
`docs/ll1_reporte.txt` y la tabla en `docs/ll1_tabla.csv`.

No hizo falta transformar la gramática:

- **No hay recursión por la izquierda.** Las repeticiones (`Adjs_*` y
  `Preps`) están escritas con recursión por la derecha.
- **No hay prefijos comunes**, así que no se aplicó factorización. Las
  alternativas de cada no terminal empiezan con terminales distintos porque
  el género y el número forman parte del tipo de token: `DET_ms` y `DET_fp`
  son terminales diferentes.

La verificación se activa sola. El constructor de `ParserEsp` llama a
`verificar_ll1()` antes de analizar; si la gramática no fuera LL(1), el
parser se detiene con el error `GramaticaNoLL1` y muestra la condición
incumplida y la celda en conflicto. `mainEsp.py` y `pruebasEsp.py` imprimen
el resultado al empezar.

## El parser

Es un **parser descendente recursivo predictivo**: cada no terminal tiene un
método con su nombre en minúsculas (`Oracion` es `oracion()`, `SN_ms` es
`sn_ms()`), y cada método elige la producción mirando solo el token actual,
sin retroceder. Eso es posible precisamente porque la gramática es LL(1).

La gramática está escrita dos veces: como datos en `gramatica.py` y como
métodos en `parserEsp.py`. Las pruebas comprueban que ambas coinciden:
`ll1.reconocer()` es un analizador dirigido por la tabla, con pila, y debe
dar la misma respuesta que `ParserEsp` en las 60 oraciones del corpus y en
todas las secuencias de hasta tres tokens.

### Árbol de derivación

- Un no terminal es un nodo cuyos hijos son, en orden, los símbolos de la
  producción que se aplicó.
- Un terminal es un nodo con el tipo de token, y su único hijo es la palabra.
- La producción vacía se muestra con la hoja `ε`.
- `EOF` se consume para comprobar que no sobran palabras, pero no se dibuja.

Por lo tanto cada nodo con sus hijos es exactamente una producción de la
gramática. Ejemplo, "El niño come.":

```
Programa
  Oracion
    Sujeto_s
      SN_ms
        DET_ms
          el
        N_ms
          niño
        Adjs_ms
          ε
    SV_s
      V_s
        come
      Complemento
        Complemento2
          Preps
            ε
          Adverbio
            ε
```

### Resultado del análisis

`analizar(oracion)` devuelve uno de tres estados:

| Estado | Significado |
|---|---|
| `acepta` | La oración pertenece al lenguaje de la gramática |
| `rechazo_sintactico` | Las palabras se conocen, pero la oración no cumple ninguna producción |
| `error_lexico` | Hay una palabra fuera del léxico o un carácter no admitido |

Los dos últimos son rechazos. Se separan porque su causa es distinta: uno es
un límite de las reglas y el otro del vocabulario. El resultado incluye
además el mensaje de error, el árbol y el tiempo de cada verbo.

## Decisiones de diseño y límites conocidos

| Tema | Comportamiento | Motivo |
|---|---|---|
| Concordancia | Se expresa con un no terminal por cada combinación de género y número | Una CFG no tiene rasgos; cada valor del rasgo necesita sus propias reglas |
| Género común | "verde" y "verdes" son `Adj_cs` y `Adj_cp` y valen para masculino y femenino | Cada palabra del léxico tiene una sola categoría; así no hay ambigüedad léxica |
| Tiempo verbal | Es un dato del léxico; presente y pretérito comparten los terminales `V_s` y `V_p` | Ninguna regla sintáctica del fragmento depende del tiempo. "escribimos" tiene la misma forma en los dos tiempos y se registra como "presente o pretérito" |
| Persona | No se comprueba: se acepta "Yo come el libro" | Solo se codificó el número. Agregar la persona multiplicaría las reglas de sujeto y verbo |
| Subordinada con "que" | Cualquier verbo la admite: se acepta "Ana come que Diego duerme" | La gramática no distingue clases de verbos |
| Frases preposicionales | Solo acompañan al verbo; se rechaza "La niña de la mochila blanca compró unas cartas" | Si también pudieran ir dentro del sintagma nominal, una preposición después del objeto tendría dos lecturas. La gramática sería ambigua y dejaría de ser LL(1) |
| Ambigüedad | "Marcela vio al fantasma con el telescopio" produce un solo árbol | Consecuencia de lo anterior: un parser LL(1) da un único árbol |
| Adverbios | Uno solo y al final de la oración | Un adverbio antes del objeto chocaría con el adverbio final |
| Orden | El sujeto es obligatorio y va antes del verbo | No se cubren el sujeto tácito ni el sujeto después del verbo |
| Relativas | No se cubren: se rechaza "El profesor que explica la gramática corrige los exámenes" | "que" solo introduce una subordinada después del verbo |
| Coma | Es un token que la gramática no admite; produce un rechazo sintáctico | No hay reglas para enumeraciones ni incisos |
| Vocabulario | Cerrado: 171 palabras, cada una con una sola categoría | Una palabra desconocida es un error léxico, no un rechazo sintáctico |

Cada fila tiene una prueba en `tests/test_esp/`, de modo que un cambio en la
gramática que altere uno de estos comportamientos no pasa inadvertido.

## Pruebas

`tests/test_esp/` contiene cuatro archivos:

- `test_ll1.py`: la gramática es LL(1); el verificador detecta gramáticas que
  no lo son (prefijo común, recursión por la izquierda, choque con FOLLOW,
  frase preposicional dentro del sintagma nominal); el parser se detiene si
  la gramática no es LL(1); el parser y la tabla coinciden.
- `test_lexer_esp.py`: tokens, contracciones "al" y "del", errores léxicos,
  y que el léxico y los terminales de la gramática coinciden.
- `test_parser_esp.py`: la salida esperada de las 60 oraciones del corpus
  (`benchmark/corpus_fase2.csv`), que cada árbol sigue la gramática, los tres
  estados del análisis, la concordancia y los límites conocidos.
- `test_documentos.py`: que este README y los archivos de `docs/` coinciden
  con la gramática de `gramatica.py`.
