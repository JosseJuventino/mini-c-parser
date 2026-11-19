
import csv
from pathlib import Path

from evaluar import (
    RAIZ,
    RUTA_CORPUS,
    RUTAS_LOGS,
    leer_csv,
    normalizar_spacy,
)


RUTA_SALIDA = (
    RAIZ / "benchmark" / "resultados" / "errores_detallados.csv"
)


def cargar_enfoques(corpus):
    enfoques = {
        nombre: leer_csv(ruta)
        for nombre, ruta in RUTAS_LOGS.items()
    }

    ruta_spacy = RAIZ / "SPACY" / "logs" / "spacy.csv"

    enfoques["spaCy"] = normalizar_spacy(
        corpus,
        leer_csv(ruta_spacy)
    )

    return enfoques


def analizar_errores(corpus, enfoques):
    errores = []

    for enfoque, resultados in enfoques.items():
        decisiones = {
            fila["id"]: fila["decision"]
            for fila in resultados
        }

        if len(decisiones) != len(corpus):
            raise ValueError(
                f"{enfoque}: no hay 76 decisiones únicas"
            )

        for fila in corpus:
            for criterio in ("CFG", "ESPAÑOL"):

                if criterio == "CFG":
                    esperado = fila["salida_cfg"]
                else:
                    esperado = (
                        "acepta"
                        if fila["gramatical"] == "si"
                        else "rechaza"
                    )

                obtenido = decisiones[fila["id"]]

                if esperado == obtenido:
                    continue

                tipo_error = (
                    "FP"
                    if obtenido == "acepta"
                    else "FN"
                )

                errores.append({
                    "enfoque": enfoque,
                    "criterio": criterio,
                    "id": fila["id"],
                    "nivel": fila["nivel"],
                    "oracion": fila["oracion"],
                    "esperado": esperado,
                    "obtenido": obtenido,
                    "tipo_error": tipo_error,
                    "fenomeno": fila["fenomeno"],
                })

    return errores


def guardar_errores(errores):
    RUTA_SALIDA.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    columnas = [
        "enfoque",
        "criterio",
        "id",
        "nivel",
        "oracion",
        "esperado",
        "obtenido",
        "tipo_error",
        "fenomeno",
    ]

    with RUTA_SALIDA.open(
        "w",
        encoding="utf-8-sig",
        newline=""
    ) as archivo:
        escritor = csv.DictWriter(
            archivo,
            fieldnames=columnas,
            delimiter=";",
        )

        escritor.writeheader()
        escritor.writerows(errores)


def main():
    corpus = leer_csv(RUTA_CORPUS)
    enfoques = cargar_enfoques(corpus)

    errores = analizar_errores(corpus, enfoques)

    guardar_errores(errores)

    print(f"Errores registrados: {len(errores)}")
    print(f"Archivo generado: {RUTA_SALIDA}")


if __name__ == "__main__":
    main()
