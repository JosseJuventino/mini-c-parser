# Importar re para trabajar con expresiones regulares
import re
from dataclasses import dataclass


@dataclass
class Token:
    tipo: str
    valor: str
    linea: int
    columna: int


# Palabras que tienen forma de identificador pero un significado especial.
# Solo se reconocen si coinciden exactamente (ifVariable sigue siendo un ID).
PALABRAS_RESERVADAS = {
    "int": "INT",
    "if": "IF",
    "else": "ELSE",
}


PATTERN = re.compile(
    r"(?P<ESPACIO>[ \t\r\n]+)|"
    r"(?P<NUMERO>\d+)|"
    r"(?P<ID>[a-zA-Z_][a-zA-Z0-9_]*)|"
    # Los operadores de dos caracteres van antes que los de uno, así
    # "==" no se separa en dos "=" ni "<=" en "<" y "=".
    r"(?P<COMPARACION>==|!=|<=|>=|<|>)|"
    r"(?P<SIMBOLO>[=+\-*/(){};])|"
    r"(?P<ERROR>.)"  # Ninguno de los anteriores
)


def tokenizar(codigo: str) -> list[Token]:
    tokens = []

    for match in PATTERN.finditer(codigo):
        tipo = match.lastgroup
        valor = match.group()
        inicio = match.start()

        linea = codigo.count("\n", 0, inicio) + 1
        columna = inicio - codigo.rfind("\n", 0, inicio)

        if tipo == "ESPACIO":
            continue

        if tipo == "ERROR":
            raise SyntaxError(
                f"Carácter inválido '{valor}' "
                f"en línea {linea}, columna {columna}"
            )

        if tipo == "ID" and valor in PALABRAS_RESERVADAS:
            tipo = PALABRAS_RESERVADAS[valor]

        # Igual que con los símbolos, el tipo de un operador de
        # comparación es el mismo operador (por ejemplo ">=").
        if tipo in ("SIMBOLO", "COMPARACION"):
            tipo = valor

        tokens.append(Token(tipo, valor, linea, columna))

    # EOF se agrega después de procesar todos los tokens
    tokens.append(
        Token("EOF", "", linea_final(codigo), columna_final(codigo))
    )

    return tokens


# Estas son funciones auxiliares
def linea_final(codigo: str) -> int:
    return codigo.count("\n") + 1


def columna_final(codigo: str) -> int:
    return len(codigo) - codigo.rfind("\n")