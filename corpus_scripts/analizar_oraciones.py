"""
analizar_oraciones.py

Lee las oraciones de un corpus y guarda en un archivo de texto el análisis que
hace spaCy (modelo es_core_news_sm) de cada una.

El corpus puede ser:
  - un .csv con una columna llamada "oracion" (las columnas "id", "nivel",
    "fenomeno" y "gramatical" son opcionales y, si existen, se muestran), o
  - un .txt con una oración por línea.

Uso (con el entorno virtual activo):
    python analizar_oraciones.py                      # usa corpus_fase1.csv
    python analizar_oraciones.py mi_corpus.csv        # usa otro corpus
    python analizar_oraciones.py mi_corpus.csv salida.txt   # y otro nombre de salida
"""

import csv
import sys
from datetime import datetime
import spacy

# --- Archivos por defecto ----------------------------
CORPUS_POR_DEFECTO = "corpus_fase1.csv"
SALIDA_POR_DEFECTO = "analisis_spacy.txt"
MODELO = "es_core_news_sm"


def leer_csv(ruta):
    """Lee un CSV y devuelve una lista de diccionarios (una fila = un diccionario).

    Es tolerante con los archivos guardados desde Excel:
      - Codificación: prueba UTF-8 y, si falla, Windows-1252 (ANSI).
      - Separador: detecta coma o punto y coma.
    """
    for codificacion in ("utf-8-sig", "cp1252"):
        try:
            with open(ruta, encoding=codificacion, newline="") as f:
                texto = f.read()
            break
        except UnicodeDecodeError:
            continue
    primera = texto.splitlines()[0] if texto else ""
    separador = ";" if primera.count(";") > primera.count(",") else ","
    return list(csv.DictReader(texto.splitlines(), delimiter=separador))


def leer_oraciones(ruta):
    """Devuelve una lista de diccionarios con al menos la clave 'oracion'."""
    if ruta.lower().endswith(".txt"):
        # Un .txt: una oración por línea; se ignoran las líneas vacías.
        for codificacion in ("utf-8-sig", "cp1252"):
            try:
                with open(ruta, encoding=codificacion) as f:
                    lineas = [l.strip() for l in f if l.strip()]
                break
            except UnicodeDecodeError:
                continue
        return [{"id": str(i), "oracion": l} for i, l in enumerate(lineas, start=1)]

    filas = leer_csv(ruta)
    if not filas or "oracion" not in filas[0]:
        columnas = list(filas[0].keys()) if filas else []
        sys.exit(f"Error: el CSV necesita una columna llamada 'oracion'. "
                 f"Columnas encontradas: {columnas}")
    return filas


def arbol(token, nivel=0):
    """Árbol de dependencias como texto con sangría (función recursiva)."""
    lineas = [f"{'    ' * nivel}{token.text}  ({token.dep_}, {token.pos_})"]
    for hijo in token.children:        # palabras que dependen de este token
        if not hijo.is_punct:          # se omiten los signos de puntuación
            lineas.extend(arbol(hijo, nivel + 1))
    return lineas


def main():
    # Argumentos opcionales: corpus y archivo de salida
    corpus = sys.argv[1] if len(sys.argv) > 1 else CORPUS_POR_DEFECTO
    salida = sys.argv[2] if len(sys.argv) > 2 else SALIDA_POR_DEFECTO

    oraciones = leer_oraciones(corpus)
    nlp = spacy.load(MODELO)

    with open(salida, "w", encoding="utf-8") as out:
        # Encabezado: deja constancia de qué se usó y cuándo
        out.write("ANÁLISIS DE spaCy\n")
        out.write(f"Corpus: {corpus}  ({len(oraciones)} oraciones)\n")
        out.write(f"spaCy {spacy.__version__}  |  modelo {MODELO} {nlp.meta['version']}\n")
        out.write(f"Fecha: {datetime.now():%Y-%m-%d %H:%M}\n")
        out.write("=" * 70 + "\n\n")

        for i, fila in enumerate(oraciones, start=1):
            doc = nlp(fila["oracion"])

            # Título de la oración, con los datos opcionales si existen
            id_ = fila.get("id") or str(i)
            nivel = f" (nivel {fila['nivel']})" if fila.get("nivel") else ""
            out.write(f"[{id_}]{nivel} {fila['oracion']}\n")
            if fila.get("gramatical"):
                out.write(f"    ¿gramatical?: {fila['gramatical']}\n")
            if fila.get("fenomeno"):
                out.write(f"    fenómeno: {fila['fenomeno']}\n")

            # Tabla palabra por palabra:
            #   pos_ = categoría, dep_ = función, head = de qué palabra depende,
            #   morph = rasgos (género, número, persona, tiempo...)
            out.write("\n    palabra        categoría  función     depende de    rasgos\n")
            for t in doc:
                out.write(f"    {t.text:<14} {t.pos_:<10} {t.dep_:<11} "
                          f"{t.head.text:<13} {t.morph}\n")

            # Árbol de dependencias, desde la raíz (el verbo principal)
            out.write("\n    Árbol de dependencias:\n")
            raiz = next(t for t in doc if t.dep_ == "ROOT")
            for linea in arbol(raiz):
                out.write("        " + linea + "\n")
            out.write("\n" + "-" * 70 + "\n\n")

    print(f"Listo: {len(oraciones)} oraciones analizadas -> {salida}")


if __name__ == "__main__":
    main()
