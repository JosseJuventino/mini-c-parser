from analizadorEsp import ACEPTA, ERROR_LEXICO, analizar
from parser import Nodo
from arbol_matplot import exportar_arbol
from ll1 import resumen, verificar_ll1
import re
import sys
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


# El árbol usa el símbolo "ε" para la producción vacía. Con UTF-8 se evita
# un error al imprimirlo cuando la salida se redirige a un archivo.
sys.stdout.reconfigure(encoding="utf-8")

#oracion = "Ana guardó las manzanas en la caja ayer"
#oracion = "La calabaza escribe el código"
oracion = "El niño come"

# Se muestra el resultado de la verificación LL(1) antes de analizar.
print(resumen(verificar_ll1()))

resultado = analizar(oracion)

if resultado["estado"] == ACEPTA:
    print("Oración sintácticamente válida")
    print("\nÁrbol de análisis sintáctico:")
    imprimir_arbol(resultado["arbol"])

    for verbo, tiempo in resultado["verbos"]:
        print(f"Tiempo verbal de '{verbo}': {tiempo}")

    nombre = oracion.strip().rstrip(".?!")
    nombre = re.sub(r'[<>:"/\\|?*\x00-\x1f]', "_", nombre)
    nombre = nombre.strip(" .") or "arbol"

    ruta = exportar_arbol(resultado["arbol"], Path("arboles") / f"{nombre}.png")
    print(f"Árbol guardado en {ruta}")

elif resultado["estado"] == ERROR_LEXICO:
    # Una palabra no está en el léxico o hay un carácter no admitido.
    print(f"Error léxico: {resultado['mensaje']}")

else:
    # Las palabras se conocen, pero la oración no cumple la gramática.
    print(f"Rechazo sintáctico: {resultado['mensaje']}")
