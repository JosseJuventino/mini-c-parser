
import csv
from pathlib import Path
from analizadorEsp import analizar 

carpeta_benchmark = Path(__file__).resolve().parents[2] / "benchmark"
archivo_corpus = carpeta_benchmark / "corpus_fase2.csv"
archivo_log = carpeta_benchmark / "logs" / "log_parser_propio.csv"


with open(archivo_corpus, encoding="utf-8-sig", newline="") as f:
    filas = list(csv.DictReader(f, delimiter=";"))


archivo_log.parent.mkdir(parents=True, exist_ok=True)

coincidencias = 0   # contador de aciertos

with open(archivo_log, "w", encoding="utf-8-sig", newline="") as f:
    escritor = csv.writer(f, delimiter=";")


    escritor.writerow([
        "id", "nivel", "oracion", "esperado_cfg", "gramatical",
        "decision", "coincide_cfg", "mensaje",
    ])

    for fila in filas:
        resultado = analizar(fila["oracion"])

        if resultado["estado"] == "acepta":
            decision = "acepta"
        else:
            decision = "rechaza"

        if decision == fila["salida_cfg"]:
            coincide = "si"
            coincidencias = coincidencias + 1
        else:
            coincide = "no"

        escritor.writerow([
            fila["id"],
            fila["nivel"],
            fila["oracion"],
            fila["salida_cfg"],
            fila["gramatical"],
            decision,
            coincide,
            resultado["mensaje"],
        ])

# rEsumen
print("Oraciones procesadas:", len(filas))
print("Coincidencias con salida_cfg:", coincidencias, "de", len(filas))
print("Log guardado en:", archivo_log)