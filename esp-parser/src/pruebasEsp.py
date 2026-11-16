
import re
from pathlib import Path

from lexerEsp import tokenizarEsp
from parserEsp import ParserEsp
from arbol_matplot import exportar_arbol
from ll1 import resumen, verificar_ll1

CORPUS = {
    # Nivel 1: oraciones simples
    "S01": "Marcela come los dulces.",
    "S02": "El profesor corrige los exámenes.",
    "S03": "Los fantasmas ven las calabazas.",
    "S04": "El profesor corrigió los exámenes.",
    "S05": "Marcela comió los dulces.",
    "S06": "Los esqueletos dibujaron las calabazas.",
    "S07": "La niña vio los fantasmas.",
    "S08": "Los niños compraron unas calabazas.",
    "S09": "El esqueleto pinta la calabaza.",
    "S10": "Los fantasmas comen las manzanas.",
    "S11": "Jaime escribe el código.",
    "S12": "Jaime escribió el código.",
    "S13": "La profesora explica la gramática.",
    "S14": "Las profesoras corrigen los exámenes.",
    "S15": "Él leyó el libro.",
    "S16": "Nosotras escribimos el parser.",
    "S17": "Ana compra una mochila.",
    "S18": "Diego guarda los cuadernos.",
    "S19": "Ellos buscaron las cajas.",
    "S20": "Ella pintó la mesa.",

    # Nivel 2: modificadores y variaciones
    "I01": "Los fantasmas pequeños comen los dulces nuevos.",
    "I02": "Las calabazas pequeñas duermen furiosamente.",
    "I03": "Los fantasma come los dulces.",
    "I04": "El calabaza escribe el código.",
    "I05": "Los esqueletos escribe el código.",
    "I06": "Jaime corrige los examen.",
    "I07": "Las calabazas pequeños duermen furiosamente.",
    "I08": "El esqueleto pequeño guardó los dulces en la caja.",
    "I09": "Las niñas dibujaron unos fantasmas blancos ayer.",
    "I10": "El fantasma duerme bajo la mesa hoy.",
    "I11": "Ellas pintaron las calabazas rojas con los niños.",
    "I12": "Jaime corrigió los exámenes en la clase ayer.",
    "I13": "La profesora nueva explica la gramática en la clase.",
    "I14": "Nosotros escribimos el código nuevo en la clase.",
    "I15": "Usted lee el libro cuidadosamente.",
    "I16": "Ella guardó el cuaderno en la mochila con una carta.",
    "I17": "Ana compró una mochila bonita para Mateo.",
    "I18": "Mateo guardó las manzanas rojas en una caja.",
    "I19": "Los gatos blancos duermen afuera.",
    "I20": "Ellos guardó las cartas en la caja.",

    # Nivel 3: oraciones complejas
    "C01": "El esqueleto pequeño escribe rápidamente el código nuevo en la clase.",
    "C02": "Marcela vio al fantasma con el telescopio.",
    "C03": "El profesor que explica la gramática corrige los exámenes.",
    "C04": "El examen que Jaime corrigió asustó a Jose.",
    "C05": "Escribimos el parser.",
    "C06": "Come Marcela los dulces.",
    "C07": "La profesora dijo que Jaime corrigió los exámenes.",
    "C08": "Ana dijo que Diego dijo que ella escribe el código.",
    "C09": "Marcela dijo que ellos dibujaron los fantasmas.",
    "C10": "Mateo dijo que nosotros escribimos las cartas.",
    "C11": "Los fantasmas que vio Marcela comen los dulces.",
    "C12": "Los libros que leyó la profesora los guardó Diego.",
    "C13": "Anoche los esqueletos comieron los dulces.",
    "C14": "En la clase Jaime explica la gramática.",
    "C15": "Las manzanas las comieron los niños.",
    "C16": "Ana guardó las manzanas en la caja cuidadosamente ayer.",
    "C17": "Jaime dijo que corrigió los exámenes.",
    "C18": "Marcela vio rápidamente al fantasma con el telescopio.",
    "C19": "La niña de la mochila blanca compró unas cartas.",
    "C20": "Jaime dijo que nosotros corrigen los exámenes en la clase.",
}

RECHAZOS_ESPERADOS = {
    "I03", "I04", "I05", "I06", "I07", "I20",
    "C01", "C03", "C04", "C05", "C06",
    "C11", "C12", "C13", "C14", "C15", "C16",
    "C17", "C18", "C19",
}

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