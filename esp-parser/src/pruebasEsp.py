
import csv
import re
from pathlib import Path

from lexerEsp import tokenizarEsp
from parserEsp import ParserEsp
from arbol_matplot import exportar_arbol
from ll1 import resumen, verificar_ll1

# El corpus se lee del mismo archivo que usa el resto del benchmark, para que
# exista una sola copia de las oraciones y de sus etiquetas.
RUTA_CORPUS = Path(__file__).resolve().parents[2] / "benchmark" / "corpus_fase2.csv"


def leer_corpus():
    """
    Devuelve dos valores:
      - un diccionario id -> oración, en el orden del archivo;
      - el conjunto de ids cuya salida esperada de la CFG es "rechaza".
    """
    corpus = {}
    rechazos = set()
    with open(RUTA_CORPUS, encoding="utf-8", newline="") as archivo:
        for fila in csv.DictReader(archivo, delimiter=";"):
            corpus[fila["id"]] = fila["oracion"]
            if fila["salida_cfg"] == "rechaza":
                rechazos.add(fila["id"])
    return corpus, rechazos


CORPUS, RECHAZOS_ESPERADOS = leer_corpus()

CARPETA_ARBOLES = Path(__file__).resolve().parent / "arboles"


def main():
    # Se muestra el resultado de la verificación LL(1) antes de analizar.
    print(resumen(verificar_ll1()))

    aceptadas = 0
    rechazos_sintacticos = 0
    errores_lexicos = 0
    imagenes = 0
    coincidencias = 0

    for identificador, oracion in CORPUS.items():
        espera_rechazo = identificador in RECHAZOS_ESPERADOS
        esperado = "RECHAZO SINTÁCTICO" if espera_rechazo else "ACEPTA"
        print(f"\n{identificador} | {oracion}")

        try:
            tokens = tokenizarEsp(oracion)
        except SyntaxError as error:
            errores_lexicos += 1
            print(f"  ERROR LÉXICO | Esperado: {esperado}")
            print(f"  {error}")
            continue

        try:
            arbol = ParserEsp(tokens).programa()
        except SyntaxError as error:
            rechazos_sintacticos += 1
            coincidencias += int(espera_rechazo)
            print(f"  RECHAZO SINTÁCTICO | Esperado: {esperado}")
            print(f"  {error}")
            continue

        aceptadas += 1
        coincidencias += int(not espera_rechazo)
        print(f"  ACEPTA | Esperado: {esperado}")

        nombre = oracion.strip().rstrip(".?!")
        nombre = re.sub(r'[<>:"/\\|?*\x00-\x1f]', "_", nombre)
        nombre = nombre.strip(" .") or identificador
        destino = CARPETA_ARBOLES / f"{nombre}.png"

        try:
            ruta = exportar_arbol(arbol, destino)
        except (OSError, ValueError, RuntimeError) as error:
            print(f"  No se pudo guardar la imagen: {error}")
        else:
            imagenes += 1
            print(f"  Árbol: {ruta}")

    print("\nRESUMEN")
    print(f"Oraciones procesadas: {len(CORPUS)}")
    print(f"Aceptadas: {aceptadas}")
    print(f"Rechazos sintácticos: {rechazos_sintacticos}")
    print(f"Errores léxicos: {errores_lexicos}")
    print(f"Coincidencias con el corpus: {coincidencias}/{len(CORPUS)}")
    print(f"Imágenes guardadas: {imagenes}")


if __name__ == "__main__":
    main()