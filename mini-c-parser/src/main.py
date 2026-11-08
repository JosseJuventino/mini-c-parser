
from .lexer import tokenizar
from .parser import Parser, Nodo


def imprimir_arbol(nodo, nivel=0):
    espacio = "  " * nivel

    if isinstance(nodo, Nodo):
        print(f"{espacio}{nodo.nombre}")

        for hijo in nodo.hijos:
            imprimir_arbol(hijo, nivel + 1)
    else:
        print(f"{espacio}{nodo}")


codigo = """
int edad = 20;
edad = edad + 5 * 2;
"""

try:
    tokens = tokenizar(codigo)

    parser = Parser(tokens)
    arbol = parser.parsear()

    print("Código sintácticamente válido")
    print("\nÁrbol de análisis sintáctico:")
    imprimir_arbol(arbol)

except SyntaxError as error:
    print(f"Error: {error}")
