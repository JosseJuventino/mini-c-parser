
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

def etiquetar(palabra: str) -> str:
    tipo, genero, numero = LEXICO[palabra]
    if genero or numero:
        return f"{tipo}_{genero or ''}{numero or ''}"
    return tipo

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
            raise SyntaxError(
                f"Carácter inválido '{valor}' "
                f"en columna {columna}"
            )

        #if tipo == "ID" and valor == "int":
        #    tipo = "INT"

        #if tipo == "SIMBOLO":
        #    tipo = valor

        # tokens.append(TokenEsp(tipo, valor, linea, columna))

        PALABRAS = valor.lower()
        for parte in CONTRACCIONES.get(PALABRAS, [PALABRAS]):
            if parte not in LEXICO:
                raise SyntaxError(
                    f"Palabra desconocida '{parte}' "
                    f"en columna {columna}"
                )
            tokens.append(Token(etiquetar(parte), parte, 1, columna))

    tokens.append(Token("EOF", "", 1, len(oracion) + 1))
    return tokens
