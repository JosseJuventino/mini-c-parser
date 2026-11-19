"""
gramatica.py

Gramática libre de contexto del subconjunto del español, escrita como datos.

G = (N, T, P, S) donde:
  - N (no terminales) son las claves del diccionario GRAMATICA.
  - T (terminales) son todos los demás símbolos: los tipos de token que
    produce lexerEsp.py (DET_ms, N_fp, V_s, PREP, ...).
  - P (producciones) son las listas de cada clave. Cada producción es una
    lista de símbolos y la lista vacía [] es la producción vacía (epsilon).
  - S (símbolo inicial) es INICIAL.

Es la misma gramática que parserEsp.py implementa con funciones: cada no
terminal tiene en ParserEsp un método con su nombre en minúsculas
(Oracion -> oracion(), SN_ms -> sn_ms(), ...).

Sufijos de los símbolos:
  m / f / c   género masculino, femenino o común (sirve para los dos)
  s / p       número singular o plural

EOF es el token que el lexer agrega al final de la oración. Cumple el papel
del marcador de fin de cadena "$" de la teoría.

ll1.py lee este archivo para calcular FIRST, FOLLOW y la tabla LL(1).
"""

# Símbolo inicial de la gramática.
INICIAL = "Programa"

# Texto con el que se muestra la producción vacía en los reportes y en el
# árbol de derivación.
EPSILON = "ε"

GRAMATICA = {
    "Programa": [
        ["Oracion", "EOF"],
    ],

    # Concordancia sujeto-verbo: el número del sujeto decide el número del
    # sintagma verbal. En una CFG la concordancia se expresa duplicando
    # las reglas, una por cada valor del rasgo.
    "Oracion": [
        ["Sujeto_s", "SV_s"],
        ["Sujeto_p", "SV_p"],
    ],

    "Sujeto_s": [
        ["SN_ms"],
        ["SN_fs"],
        ["PRON_s"],
    ],
    "Sujeto_p": [
        ["SN_mp"],
        ["SN_fp"],
        ["PRON_p"],
    ],

    # Sintagmas nominales. Hay uno por cada combinación de género y número
    # para que determinante, sustantivo y adjetivos concuerden.
    "SN_ms": [
        ["DET_ms", "N_ms", "Adjs_ms"],
        ["NP_ms"],
    ],
    "SN_fs": [
        ["DET_fs", "N_fs", "Adjs_fs"],
        ["NP_fs"],
    ],
    # En plural el sustantivo puede ir sin determinante ("niños comen").
    "SN_mp": [
        ["DET_mp", "N_mp", "Adjs_mp"],
        ["N_mp", "Adjs_mp"],
    ],
    "SN_fp": [
        ["DET_fp", "N_fp", "Adjs_fp"],
        ["N_fp", "Adjs_fp"],
    ],

    # Cero o más adjetivos. La repetición se escribe con recursión por la
    # derecha; la recursión por la izquierda no es compatible con LL(1).
    # Adj_cs y Adj_cp son adjetivos de género común ("verde", "verdes").
    "Adjs_ms": [
        ["Adj_ms", "Adjs_ms"],
        ["Adj_cs", "Adjs_ms"],
        [],
    ],
    "Adjs_fs": [
        ["Adj_fs", "Adjs_fs"],
        ["Adj_cs", "Adjs_fs"],
        [],
    ],
    "Adjs_mp": [
        ["Adj_mp", "Adjs_mp"],
        ["Adj_cp", "Adjs_mp"],
        [],
    ],
    "Adjs_fp": [
        ["Adj_fp", "Adjs_fp"],
        ["Adj_cp", "Adjs_fp"],
        [],
    ],

    # Sintagma verbal: el verbo y todo lo que lo acompaña.
    "SV_s": [
        ["V_s", "Complemento"],
    ],
    "SV_p": [
        ["V_p", "Complemento"],
    ],

    # Sintagma nominal en posición de objeto o dentro de una frase
    # preposicional: aquí puede ir cualquier género y número.
    "SN": [
        ["SN_ms"],
        ["SN_fs"],
        ["SN_mp"],
        ["SN_fp"],
    ],

    # Objeto directo, oración subordinada con "que", o nada.
    "Complemento": [
        ["SN", "Complemento2"],
        ["que", "Oracion"],
        ["Complemento2"],
    ],
    "Complemento2": [
        ["Preps", "Adverbio"],
    ],

    # Cero o más frases preposicionales.
    "Preps": [
        ["PREP", "SN", "Preps"],
        [],
    ],

    # Un adverbio opcional al final.
    "Adverbio": [
        ["ADV"],
        [],
    ],
}
