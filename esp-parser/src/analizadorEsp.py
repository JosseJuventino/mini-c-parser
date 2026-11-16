"""
analizadorEsp.py

Punto de entrada único para analizar una oración. Ejecuta el lexer y el
parser y clasifica el resultado en uno de tres estados:

  ACEPTA              la oración pertenece al lenguaje de la gramática
  RECHAZO_SINTACTICO  todas las palabras se conocen, pero su orden o su
                      concordancia no cumplen ninguna producción
  ERROR_LEXICO        hay una palabra que no está en el léxico o un carácter
                      que no se admite; la oración no llega al parser

Los dos últimos son rechazos. Se distinguen porque su causa es distinta: el
error léxico es un límite del vocabulario y el rechazo sintáctico es un
límite de las reglas.
"""

from lexerEsp import ErrorLexico, tiempo_verbal, tokenizarEsp
from parserEsp import ParserEsp

ACEPTA = "acepta"
RECHAZO_SINTACTICO = "rechazo_sintactico"
ERROR_LEXICO = "error_lexico"


def analizar(oracion: str) -> dict:
    """
    Analiza una oración y devuelve un diccionario con:

      estado   ACEPTA, RECHAZO_SINTACTICO o ERROR_LEXICO
      mensaje  el error reportado (cadena vacía si la oración se acepta)
      arbol    el árbol de derivación (None si la oración no se acepta)
      verbos   lista de pares (verbo, tiempo) en el orden de la oración
    """
    try:
        tokens = tokenizarEsp(oracion)
    except ErrorLexico as error:
        return {
            "estado": ERROR_LEXICO,
            "mensaje": str(error),
            "arbol": None,
            "verbos": [],
        }

    verbos = [
        (token.valor, tiempo_verbal(token.valor))
        for token in tokens
        if token.tipo in ("V_s", "V_p")
    ]

    try:
        arbol = ParserEsp(tokens).programa()
    except SyntaxError as error:
        return {
            "estado": RECHAZO_SINTACTICO,
            "mensaje": str(error),
            "arbol": None,
            "verbos": verbos,
        }

    return {
        "estado": ACEPTA,
        "mensaje": "",
        "arbol": arbol,
        "verbos": verbos,
    }
