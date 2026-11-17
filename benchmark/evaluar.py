
import csv
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]

RUTA_CORPUS = RAIZ / "benchmark" / "corpus_fase2.csv"
RUTA_NLTK = RAIZ / "NLTK" / "logs" / "nltk.csv"


def leer_csv(ruta):
    with open(ruta, encoding="utf-8-sig", newline="") as archivo:
        lector = csv.DictReader(archivo, delimiter=";")
        return list(lector)

# Relaciona los archivos mediante el ID, Comprueba que no falten oraciones, Cuenta los aciertos y errores
def construir_matriz(corpus, resultados, criterio="CFG"):
    esperados = {fila["id"]: fila for fila in corpus}

    obtenidos = {}

    for fila in resultados:
        identificador = fila["id"]

        if identificador in obtenidos:
            raise ValueError(f"ID duplicado: {identificador}")

        obtenidos[identificador] = fila
    if esperados.keys() != obtenidos.keys():
        raise ValueError(
            "Los IDs del corpus y del log no coinciden."
        )

    matriz = {
        "TP": 0,
        "FP": 0,
        "TN": 0,
        "FN": 0,
    }

    for identificador, fila in esperados.items():
        if criterio == "CFG":
            esperado = fila["salida_cfg"]
        elif criterio == "ESPAÑOL":
            gramatical = fila["gramatical"]

            if gramatical not in ("si", "no"):
                raise ValueError(
                    f"Gramaticalidad inválida en {identificador}"
                )

            esperado = "acepta" if gramatical == "si" else "rechaza"
        else:
            raise ValueError(f"Criterio desconocido: {criterio}")

        obtenido = obtenidos[identificador]["decision"]

        if esperado not in ("acepta", "rechaza"):
            raise ValueError(f"Etiqueta esperada inválida: {identificador}")

        if obtenido not in ("acepta", "rechaza"):
            raise ValueError(f"Decisión inválida: {identificador}")

        if esperado == "acepta" and obtenido == "acepta":
            matriz["TP"] += 1

        elif esperado == "rechaza" and obtenido == "acepta":
            matriz["FP"] += 1

        elif esperado == "rechaza" and obtenido == "rechaza":
            matriz["TN"] += 1

        elif esperado == "acepta" and obtenido == "rechaza":
            matriz["FN"] += 1

    return matriz


def dividir_seguro(numerador, denominador):
    if denominador == 0:
        return None

    return numerador / denominador


def calcular_metricas(matriz):
    tp = matriz["TP"]
    fp = matriz["FP"]
    tn = matriz["TN"]
    fn = matriz["FN"]

    return {
        "precision": dividir_seguro(tp, tp + fp),
        "recall": dividir_seguro(tp, tp + fn),
        "rechazo_correcto": dividir_seguro(tn, tn + fp),
    }


def crear_fila_resultado(enfoque, criterio, nivel, matriz):
    metricas = calcular_metricas(matriz)

    def porcentaje(valor):
        if valor is None:
            return ""
        return round(valor * 100, 2)

    return {
        "enfoque": enfoque,
        "criterio": criterio,
        "nivel": nivel,
        "oraciones": sum(matriz.values()),
        "TP": matriz["TP"],
        "FP": matriz["FP"],
        "TN": matriz["TN"],
        "FN": matriz["FN"],
        "precision": porcentaje(metricas["precision"]),
        "recall": porcentaje(metricas["recall"]),
        "rechazo_correcto": porcentaje(
            metricas["rechazo_correcto"]
        ),
    }


def guardar_resultados(filas):
    ruta = RAIZ / "benchmark" / "resultados" / "metricas_nltk.csv"

    # Crear la carpeta si todavía no existe.
    ruta.parent.mkdir(parents=True, exist_ok=True)

    with open(ruta, "w", encoding="utf-8-sig", newline="") as archivo:
        escritor = csv.DictWriter(
            archivo,
            fieldnames=list(filas[0].keys()),
            delimiter=";"
        )

        escritor.writeheader()
        escritor.writerows(filas)

    print(f"\nResultados guardados en: {ruta}")


def evaluar_enfoque(nombre, corpus, resultados):
    filas_exportar = []

    for nivel in ("general", "1", "2", "3"):
        if nivel == "general":
            corpus_filtrado = corpus
            resultados_filtrados = resultados
        else:
            corpus_filtrado = [
                fila for fila in corpus
                if fila["nivel"] == nivel
            ]

            ids = {
                fila["id"] for fila in corpus_filtrado
            }

            resultados_filtrados = [
                fila for fila in resultados
                if fila["id"] in ids
            ]

        for criterio in ("CFG", "ESPAÑOL"):
            matriz = construir_matriz(
                corpus_filtrado,
                resultados_filtrados,
                criterio=criterio
            )

            fila = crear_fila_resultado(
                nombre,
                criterio,
                nivel,
                matriz
            )

            filas_exportar.append(fila)

    return filas_exportar


def mostrar_porcentaje(valor):
    if valor == "":
        return "N/D"

    return f"{valor:.2f}%"


def main():
    corpus = leer_csv(RUTA_CORPUS)
    resultados_nltk = leer_csv(RUTA_NLTK)

    print(f"Oraciones del corpus: {len(corpus)}")
    print(f"Resultados de NLTK: {len(resultados_nltk)}")

    filas_exportar = evaluar_enfoque(
        "NLTK",
        corpus,
        resultados_nltk
    )

    for fila in filas_exportar:
        print(
            f"{fila['criterio']} | "
            f"Nivel {fila['nivel']} | "
            f"Precisión: {mostrar_porcentaje(fila['precision'])} | "
            f"Recall: {mostrar_porcentaje(fila['recall'])} | "
            f"Rechazo: {mostrar_porcentaje(fila['rechazo_correcto'])}"
        )

    guardar_resultados(filas_exportar)


if __name__ == "__main__":
    main()
