from lexerEsp import tokenizarEsp
from parserEsp import ParserEsp
from parser import Nodo
from arbol_matplot import exportar_arbol
import re
from pathlib import Path


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



#oracion = "Ana guardó las manzanas en la caja ayer"
#oracion = "La calabaza escribe el código"
oracion = "El niño come"

try:
    tokens = tokenizarEsp(oracion)

    parser = ParserEsp(tokens)
    arbol = parser.programa()

    print("Oración sintácticamente válida")
    print("\nÁrbol de análisis sintáctico:")
    imprimir_arbol(arbol)

    nombre = oracion.strip().rstrip(".?!")
    nombre = re.sub(r'[<>:"/\\|?*\x00-\x1f]', "_", nombre)
    nombre = nombre.strip(" .") or "arbol"

    ruta = exportar_arbol(arbol, Path("arboles") / f"{nombre}.png")
    print(f"Árbol guardado en {ruta}")


except SyntaxError as error:
    print(f"Error: {error}")