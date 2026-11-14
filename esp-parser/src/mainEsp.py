from lexerEsp import tokenizarEsp
from parserEsp import ParserEsp
from parser import Nodo


def imprimir_arbol(nodo, nivel=0):
    espacio = "  " * nivel

    if isinstance(nodo, Nodo):
        if not nodo.hijos:
            return

        print(f"{espacio}{nodo.nombre}")

        for hijo in nodo.hijos:
            imprimir_arbol(hijo, nivel + 1)
    else:
        print(f"{espacio}{nodo}")




oracion = "La calabaza escribe el código"

try:
    tokens = tokenizarEsp(oracion)

    parser = ParserEsp(tokens)
    arbol = parser.programa()

    print("Oración sintácticamente válida")
    print("\nÁrbol de análisis sintáctico:")
    imprimir_arbol(arbol)

except SyntaxError as error:
    print(f"Error: {error}")