import argparse
import csv
import re
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]

RUTA_CORPUS = RAIZ / "benchmark" / "corpus_fase2.csv"

ARCHIVOS = {
    "zero_shot": (
        RAIZ / "LLM" / "logs_zero_shot_18-11-2026_1-00.txt",
        RAIZ / "LLM" / "gemini_zero_shot.csv",
    ),
    "few_shot": (
        RAIZ / "LLM" / "logs_few_shot_18-11-2026_1-00.txt",
        RAIZ / "LLM" / "gemini_few_shot.csv",
    ),
}


def leer_corpus():
    with RUTA_CORPUS.open(
        encoding="utf-8-sig",
        newline=""
    ) as archivo:
        return list(csv.DictReader(archivo, delimiter=";"))


def extraer_decisiones(texto, modo, corpus):
    if "Respuesta generada:" not in texto:
        raise ValueError("No se encontró la respuesta del LLM")

    respuesta = texto.split("Respuesta generada:", 1)[1]

    if modo == "zero_shot":
        patron = re.compile(
            r"(?m)^(?:\*\*)?(\d+)\.(?:\*\*[ \t]*\n\*[ \t]+|[ \t]+)"
            r"\*\*Índice:\*\*[ \t]*(\d+)[ \t]*$"
        )
    else:
        patron = re.compile(
            r'(?m)^\*\*(\d+)\.(?:\*\*)?[ \t]*["“]([^\n"”]+)["”]'
        )

    coincidencias = list(patron.finditer(respuesta))
    decisiones = {}

    for i, coincidencia in enumerate(coincidencias):
        indice = int(coincidencia.group(1))

        if not 1 <= indice <= len(corpus):
            raise ValueError(f"Índice fuera del corpus: {indice}")

        if modo == "zero_shot":
            indice_interno = int(coincidencia.group(2))

            if indice != indice_interno:
                raise ValueError(
                    f"Índices distintos: {indice} y {indice_interno}"
                )

        inicio = coincidencia.start()

        fin = (
            coincidencias[i + 1].start()
            if i + 1 < len(coincidencias)
            else len(respuesta)
        )

        bloque = respuesta[inicio:fin]

        resultado = re.search(
            r"\*\*(?:Resultado|Estado):\*\*[ \t]*"
            r"(?:Se[ \t]+)?"
            r"(acepta|rechaza|aceptada|rechazada)\b",
            bloque,
            flags=re.IGNORECASE,
        )

        if resultado is None:
            raise ValueError(
                f"No se encontró una decisión en oración {indice}"
            )

        palabra = resultado.group(1).lower()

        decision = (
            "rechaza"
            if palabra.startswith("rechaz")
            else "acepta"
        )

        if modo == "zero_shot":
            oracion = re.search(
                r"\*\*Oraci[oó]n:\*\*[ \t]*([^\r\n]+)",
                bloque,
                flags=re.IGNORECASE,
            )

            if oracion is None:
                raise ValueError(
                    f"No se encontró la oración {indice}"
                )

            texto_oracion = oracion.group(1).strip()

        else:
            texto_oracion = coincidencia.group(2).strip()

        esperado = corpus[indice - 1]

        if texto_oracion != esperado["oracion"]:
            raise ValueError(
                f"La oración {indice} no coincide con el corpus"
            )

        # El log few-shot repite la oración 38
        # dentro de una corrección de formato.
        if indice in decisiones:
            if decisiones[indice]["decision"] != decision:
                raise ValueError(
                    f"Decisiones contradictorias en {indice}"
                )

            print(
                f"Aviso: índice {indice} repetido "
                f"con la misma decisión; se ignora la repetición"
            )
            continue

        decisiones[indice] = {
            "id": esperado["id"],
            "indice": indice,
            "oracion": texto_oracion,
            "decision": decision,
        }

    if len(decisiones) != len(corpus):
        faltantes = sorted(
            set(range(1, len(corpus) + 1))
            - set(decisiones)
        )
        raise ValueError(
            f"Faltan decisiones del LLM: {faltantes}"
        )

    return [
        decisiones[indice]
        for indice in sorted(decisiones)
    ]


def guardar_csv(ruta, filas):
    with ruta.open(
        "w",
        encoding="utf-8-sig",
        newline=""
    ) as archivo:
        escritor = csv.DictWriter(
            archivo,
            fieldnames=[
                "id",
                "indice",
                "oracion",
                "decision",
            ],
            delimiter=";",
        )

        escritor.writeheader()
        escritor.writerows(filas)


def main():
    parser = argparse.ArgumentParser(description="Extrae las decisiones de Gemini para el evaluador.")
    parser.add_argument("--zero-shot", type=Path, help="Registro zero-shot de la corrida")
    parser.add_argument("--few-shot", type=Path, help="Registro few-shot de la misma corrida")
    args = parser.parse_args()
    if (args.zero_shot is None) != (args.few_shot is None):
        parser.error("Indique los dos registros de la corrida.")

    entradas = {"zero_shot": args.zero_shot, "few_shot": args.few_shot}
    corpus = leer_corpus()
    resultados = {}
    for modo, (predeterminada, _) in ARCHIVOS.items():
        entrada = entradas[modo] or predeterminada
        texto = entrada.read_text(encoding="utf-8-sig")
        resultados[modo] = extraer_decisiones(texto, modo, corpus)

    for modo, filas in resultados.items():
        salida = ARCHIVOS[modo][1]
        guardar_csv(salida, filas)

        print(
            f"{modo}: {len(filas)} decisiones "
            f"guardadas en {salida}"
        )


if __name__ == "__main__":
    main()
