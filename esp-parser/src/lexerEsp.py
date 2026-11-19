
# Importar re para trabajar con expresiones regulares
import re
from dataclasses import dataclass
from lexer import Token
from lexico import LEXICO


'''
@dataclass
class TokenEsp:
    # tipo: str # No se ocupa 
    valor: str
    # linea: int
    columna: int
'''

PATRON = re.compile(
    r"(?P<ESPACIO>\s+)|"
    r"(?P<PALABRA>[^\W\d_]+)|"  # Acepta letras usadaas en el español (á, ñ, ü) 
    r"(?P<COMA>,)|"
    r"(?P<IGNORAR>[.?¿!¡;:])|" # Ignora simbolos
    r"(?P<ERROR>.)"
)

CONTRACCIONES = {"al": ["a", "el"], "del": ["de", "el"]}


class ErrorLexico(SyntaxError):
    """
    La oración contiene algo que el lexer no puede clasificar: una palabra
    que no está en el léxico o un carácter que no se admite.

    Hereda de SyntaxError para que el código que ya capturaba SyntaxError
    siga funcionando, pero permite distinguir este caso (la palabra no
    pertenece al vocabulario) de un rechazo sintáctico (las palabras se
    conocen, pero su orden no cumple la gramática).
    """


def etiquetar(palabra: str) -> str:
    # Los verbos tienen un cuarto dato (el tiempo) que no forma parte del
    # tipo de token; por eso solo se toman los tres primeros.
    tipo, genero, numero = LEXICO[palabra][:3]
    if genero or numero:
        return f"{tipo}_{genero or ''}{numero or ''}"
    return tipo


def tiempo_verbal(palabra: str) -> str | None:
    """
    Devuelve el tiempo de un verbo del léxico ("presente", "pretérito" o
    "presente o pretérito") y None si la palabra no es un verbo.

    El tiempo es un dato del léxico y no una categoría de la gramática:
    ninguna regla sintáctica del fragmento depende de él.
    """
    entrada = LEXICO.get(palabra.lower())
    if entrada is None or entrada[0] != "V":
        return None
    return entrada[3]

def tokenizarEsp(oracion: str) -> list[Token]:
    tokens = []

    for match in PATRON.finditer(oracion):
        tipo = match.lastgroup
        valor = match.group()
        columna = match.start() + 1

        # linea = codigo.count("\n", 0, inicio) + 1
        # columna = inicio - codigo.rfind("\n", 0, inicio)

        if tipo == "ESPACIO":
            continue

        if tipo == "IGNORAR":
             continue
    
        if tipo == "ERROR":
            raise ErrorLexico(
                f"Carácter inválido '{valor}' "
                f"en columna {columna}"
            )

        # La coma es un signo válido del español, pero la gramática no tiene
        # ninguna regla que la use. Se entrega como token COMA para que el
        # parser la rechace con un error sintáctico claro, en lugar de
        # tratarla como una palabra desconocida.
        if tipo == "COMA":
            tokens.append(Token("COMA", valor, 1, columna))
            continue

        #if tipo == "ID" and valor == "int":
        #    tipo = "INT"

        #if tipo == "SIMBOLO":
        #    tipo = valor

        # tokens.append(TokenEsp(tipo, valor, linea, columna))

        PALABRAS = valor.lower()
        for parte in CONTRACCIONES.get(PALABRAS, [PALABRAS]):
            if parte not in LEXICO:
                raise ErrorLexico(
                    f"Palabra desconocida '{parte}' "
                    f"en columna {columna}"
                )
            tokens.append(Token(etiquetar(parte), parte, 1, columna))

    tokens.append(Token("EOF", "", 1, len(oracion) + 1))
    return tokens
