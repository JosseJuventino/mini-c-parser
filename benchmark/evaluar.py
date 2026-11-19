
import csv
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]

RUTA_CORPUS = RAIZ / "benchmark" / "corpus_fase2.csv"

RUTAS_LOGS = {
    "NLTK": RAIZ / "NLTK" / "logs" / "nltk.csv",

    "Parser propio": (
        RAIZ / "benchmark" / "logs" / "log_parser_propio.csv"
    ),

    "Gemini zero-shot": (
        RAIZ / "LLM" / "gemini_zero_shot.csv"
    ),

    "Gemini few-shot": (
        RAIZ / "LLM" / "gemini_few_shot.csv"
    ),
}



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
    ruta = RAIZ / "benchmark" / "resultados" / "metricas_comparativas.csv"

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


def normalizar_spacy(corpus, resultados_spacy):
    ids_corpus = {fila["id"] for fila in corpus}
    ids_encontrados = set()
    decisiones_definitivas = []

    for fila in resultados_spacy:
        identificador = fila["id"]
        decision = fila["decision_spacy"]

        if identificador in ids_encontrados:
            raise ValueError(f"ID duplicado en spaCy: {identificador}")

        if identificador not in ids_corpus:
            raise ValueError(f"ID desconocido en spaCy: {identificador}")

        ids_encontrados.add(identificador)

        if decision not in ("acepta", "rechaza", "acepta_parcial"):
            raise ValueError(
                f"Decisión inválida en spaCy: {identificador}"
            )

        if decision == "acepta_parcial":
            continue

        decisiones_definitivas.append({
            "id": identificador,
            "decision": decision,
        })

    if ids_encontrados != ids_corpus:
        faltantes = ids_corpus - ids_encontrados
        raise ValueError(f"Faltan oraciones de spaCy: {faltantes}")

    return decisiones_definitivas


def imprimir_filas(filas):
    for fila in filas:
        print(
            f"{fila['criterio']} | "
            f"Nivel {fila['nivel']} | "
            f"Precisión: {mostrar_porcentaje(fila['precision'])} | "
            f"Recall: {mostrar_porcentaje(fila['recall'])} | "
            f"Rechazo: {mostrar_porcentaje(fila['rechazo_correcto'])}"
        )


def main():
    corpus = leer_csv(RUTA_CORPUS)

    print(f"Oraciones del corpus: {len(corpus)}")

    filas_exportar = []

    for nombre, ruta in RUTAS_LOGS.items():
        if not ruta.is_file():
            raise FileNotFoundError(
                f"No se encontró el log de {nombre}: {ruta}"
            )

        resultados = leer_csv(ruta)

        filas_enfoque = evaluar_enfoque(
            nombre,
            corpus,
            resultados
        )

        filas_exportar.extend(filas_enfoque)

        print(f"\nResultados de {nombre}:")
        imprimir_filas(filas_enfoque)

    ruta_spacy = RAIZ / "SPACY" / "logs" / "spacy.csv"
    resultados_spacy = leer_csv(ruta_spacy)

    decisiones_spacy = normalizar_spacy(
        corpus,
        resultados_spacy
    )

    ids_definitivos = {
        fila["id"] for fila in decisiones_spacy
    }

    corpus_evaluable = [
        fila for fila in corpus
        if fila["id"] in ids_definitivos
    ]

    filas_spacy = evaluar_enfoque(
        "spaCy",
        corpus_evaluable,
        decisiones_spacy
    )

    filas_exportar.extend(filas_spacy)

    print("\nResultados de spaCy:")
    print(f"Decisiones definitivas: {len(decisiones_spacy)}")
    print(f"Indeterminadas: {len(corpus) - len(decisiones_spacy)}")
    imprimir_filas(filas_spacy)

    totales_por_nivel = {
        "general": len(corpus),
        "1": sum(1 for fila in corpus if fila["nivel"] == "1"),
        "2": sum(1 for fila in corpus if fila["nivel"] == "2"),
        "3": sum(1 for fila in corpus if fila["nivel"] == "3"),
    }

    for fila in filas_exportar:
        total = totales_por_nivel[fila["nivel"]]
        evaluadas = fila["oraciones"]

        fila["total_corpus"] = total
        fila["indeterminadas"] = total - evaluadas
        fila["cobertura"] = round(evaluadas / total * 100, 2)

    guardar_resultados(filas_exportar)


if __name__ == "__main__":
    main()
