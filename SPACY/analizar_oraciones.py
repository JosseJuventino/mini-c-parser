"""
analizar_oraciones.py

Procesa un corpus de oraciones en español con spaCy, aplica el criterio
de aceptación C1–C2–C3 y genera dos salidas:
  - Un archivo de texto con el análisis lingüístico completo (.txt).
  - Un CSV con la decisión por oración y el detalle de cada criterio (.csv).

Criterio de aceptación (C1–C2–C3):
  C1  Concordancia sujeto–verbo (persona y número).
  C2  Concordancia determinante–sustantivo–adjetivo (género y número).
  C3  La raíz sintáctica tiene categoría VERB o AUX.

Valores posibles por criterio: "si" | "no" | "no_evaluable"
Decisión final: "acepta" | "rechaza"

  - acepta  : ningún criterio produjo "no" (incluye casos con "no_evaluable")
  - rechaza : C3=no  O  C1=no  O  C2=no

Entrada:
  - CSV: requiere columna "oracion". Las columnas "id", "nivel",
    "fenomeno" y "gramatical" son opcionales.
  - TXT: una oración por línea.

Uso:
  python analizar_oraciones.py
  python analizar_oraciones.py mi_corpus.csv
  python analizar_oraciones.py mi_corpus.csv salida.txt salida.csv
"""

import csv
import sys
from datetime import datetime

import spacy


# ---------------------------------------------------------------------
# Configuración predeterminada
# ---------------------------------------------------------------------

CORPUS_POR_DEFECTO = "benchmark/corpus_fase2.csv"
SALIDA_TXT_POR_DEFECTO = "spacy/analisis_spacy.txt"
SALIDA_CSV_POR_DEFECTO = "spacy/logs/spacy.csv"
MODELO = "es_core_news_sm"


# ---------------------------------------------------------------------
# Lectura del corpus
# ---------------------------------------------------------------------

def leer_csv(ruta):
    """
    Lee un CSV y devuelve sus filas como lista de diccionarios.
    Intenta UTF-8 (con BOM) y Windows-1252. Detecta separador , o ;.
    """
    texto = None
    for codificacion in ("utf-8-sig", "cp1252"):
        try:
            with open(ruta, encoding=codificacion, newline="") as f:
                texto = f.read()
            break
        except UnicodeDecodeError:
            continue

    if texto is None:
        sys.exit(
            "Error: no se pudo interpretar la codificación del CSV. "
            "Utilice UTF-8 o Windows-1252."
        )

    primera = texto.splitlines()[0] if texto else ""
    separador = ";" if primera.count(";") > primera.count(",") else ","
    return list(csv.DictReader(texto.splitlines(), delimiter=separador))


def leer_oraciones(ruta):
    """
    Lee un corpus CSV o TXT y devuelve lista de diccionarios con clave "oracion".
    """
    if ruta.lower().endswith(".txt"):
        lineas = None
        for codificacion in ("utf-8-sig", "cp1252"):
            try:
                with open(ruta, encoding=codificacion) as f:
                    lineas = [l.strip() for l in f if l.strip()]
                break
            except UnicodeDecodeError:
                continue

        if lineas is None:
            sys.exit(
                "Error: no se pudo interpretar la codificación del TXT. "
                "Utilice UTF-8 o Windows-1252."
            )
        return [{"id": str(i), "oracion": linea} for i, linea in enumerate(lineas, start=1)]

    filas = leer_csv(ruta)
    if not filas or "oracion" not in filas[0]:
        columnas = list(filas[0].keys()) if filas else []
        sys.exit(
            "Error: el CSV necesita una columna llamada 'oracion'. "
            f"Columnas encontradas: {columnas}"
        )
    return filas


# ---------------------------------------------------------------------
# Árbol de dependencias (visualización)
# ---------------------------------------------------------------------

def arbol(token, nivel=0):
    """
    Construye las líneas de texto del subárbol de un token (recursivo).
    Excluye puntuación de la visualización.
    """
    lineas = [f"{'    ' * nivel}{token.text}  ({token.dep_}, {token.pos_})"]
    for hijo in token.children:
        if not hijo.is_punct:
            lineas.extend(arbol(hijo, nivel + 1))
    return lineas


# ---------------------------------------------------------------------
# Criterio C1: concordancia sujeto–verbo
# ---------------------------------------------------------------------

def evaluar_c1(doc):
    """
    Verifica la concordancia de persona y número entre el sujeto y la raíz.

    Busca el token con dep_='ROOT'. Si tiene un dependiente con dep_='nsubj',
    extrae Person y Number de ambos y los compara.

    Retorna (resultado, motivo):
      resultado: "si" | "no" | "no_evaluable"
      motivo   : descripción de la evaluación para el log
    """
    raiz = next((t for t in doc if t.dep_ == "ROOT"), None)
    if raiz is None:
        return "no_evaluable", "no se encontró raíz"

    # Buscar sujeto directo de la raíz
    sujeto = next(
        (t for t in raiz.children if t.dep_ in ("nsubj", "nsubj:pass")),
        None
    )
    if sujeto is None:
        return "no_evaluable", "sin sujeto explícito (nsubj)"

    # Extraer rasgos morfológicos del sujeto y del verbo raíz
    morph_suj = sujeto.morph
    morph_raiz = raiz.morph

    person_suj = morph_suj.get("Person")    # lista, p.ej. ['3']
    number_suj = morph_suj.get("Number")    # lista, p.ej. ['Sing']
    person_raiz = morph_raiz.get("Person")
    number_raiz = morph_raiz.get("Number")

    # Si alguno carece de rasgos, no se puede evaluar
    sin_rasgos = []
    if not person_suj or not number_suj:
        sin_rasgos.append(f"sujeto '{sujeto.text}' ({sujeto.pos_}) sin Person/Number")
    if not person_raiz or not number_raiz:
        sin_rasgos.append(f"raíz '{raiz.text}' ({raiz.pos_}) sin Person/Number")

    if sin_rasgos:
        return "no_evaluable", "; ".join(sin_rasgos)

    # Comparar
    person_ok = set(person_suj) & set(person_raiz)
    number_ok = set(number_suj) & set(number_raiz)

    if person_ok and number_ok:
        return "si", (
            f"sujeto '{sujeto.text}' Person={person_suj} Number={number_suj} "
            f"| raíz '{raiz.text}' Person={person_raiz} Number={number_raiz}"
        )
    else:
        discordancias = []
        if not person_ok:
            discordancias.append(
                f"persona: sujeto={person_suj} vs raíz={person_raiz}"
            )
        if not number_ok:
            discordancias.append(
                f"número: sujeto={number_suj} vs raíz={number_raiz}"
            )
        return "no", (
            f"discordancia sujeto '{sujeto.text}'–raíz '{raiz.text}': "
            + "; ".join(discordancias)
        )


# ---------------------------------------------------------------------
# Criterio C2: concordancia determinante–sustantivo–adjetivo
# ---------------------------------------------------------------------

def evaluar_c2(doc):
    """
    Verifica concordancia de género y número entre determinantes/adjetivos
    y el sustantivo cabeza al que modifican.

    Para cada sustantivo (NOUN/PROPN) busca sus dependientes det y amod.
    Compara Gender y Number entre el sustantivo y cada modificador.

    Prioridad del resultado global:
      1. Si algún par discorda              → "no"
      2. Si ninguno discorda pero hay NE    → "no_evaluable"
      3. Si todos concuerdan y todos se pudieron evaluar → "si"

    Retorna (resultado, motivo).
    """
    hay_no_evaluable = False
    motivos_no = []
    motivos_ne = []

    for token in doc:
        if token.pos_ not in ("NOUN", "PROPN"):
            continue

        morph_sust = token.morph
        gender_sust = morph_sust.get("Gender")
        number_sust = morph_sust.get("Number")

        # Modificadores: determinantes y adjetivos
        modificadores = [
            t for t in token.children
            if t.dep_ in ("det", "amod") and t.pos_ in ("DET", "ADJ", "PROPN", "NOUN")
        ]

        for mod in modificadores:
            morph_mod = mod.morph
            gender_mod = morph_mod.get("Gender")
            number_mod = morph_mod.get("Number")

            # Verificar si hay rasgos en ambos lados
            sin_rasgos_sust = not gender_sust or not number_sust
            sin_rasgos_mod = not gender_mod or not number_mod

            if sin_rasgos_sust or sin_rasgos_mod:
                faltantes = []
                if sin_rasgos_sust:
                    faltantes.append(f"sust '{token.text}' sin Gender/Number")
                if sin_rasgos_mod:
                    faltantes.append(f"mod '{mod.text}' sin Gender/Number")
                motivos_ne.append("; ".join(faltantes))
                hay_no_evaluable = True
                continue

            # Comparar género y número
            gender_ok = set(gender_sust) & set(gender_mod)
            number_ok = set(number_sust) & set(number_mod)

            if not gender_ok or not number_ok:
                discordancias = []
                if not gender_ok:
                    discordancias.append(
                        f"género: '{mod.text}'={gender_mod} vs '{token.text}'={gender_sust}"
                    )
                if not number_ok:
                    discordancias.append(
                        f"número: '{mod.text}'={number_mod} vs '{token.text}'={number_sust}"
                    )
                motivos_no.append("; ".join(discordancias))

    # Aplicar prioridad
    if motivos_no:
        return "no", "discordancia: " + " | ".join(motivos_no)
    if hay_no_evaluable:
        return "no_evaluable", "pares sin rasgos: " + " | ".join(motivos_ne)
    return "si", "todos los pares evaluados concuerdan"


# ---------------------------------------------------------------------
# Criterio C3: raíz verbal
# ---------------------------------------------------------------------

def evaluar_c3(doc):
    """
    Verifica que el token con dep_='ROOT' tenga pos_ VERB o AUX.

    Retorna (resultado, motivo).
    """
    raiz = next((t for t in doc if t.dep_ == "ROOT"), None)
    if raiz is None:
        return "no", "no se encontró ningún token con dep_=ROOT"

    if raiz.pos_ in ("VERB", "AUX"):
        return "si", f"raíz '{raiz.text}' es {raiz.pos_}"
    else:
        return "no", f"raíz '{raiz.text}' es {raiz.pos_} (esperado VERB o AUX)"


# ---------------------------------------------------------------------
# Decisión final
# ---------------------------------------------------------------------

def decidir(c1, c2, c3):
    """
    Aplica la lógica de combinación de C1–C2–C3. Decisión binaria: acepta/rechaza.

    C3 es condición necesaria: si es 'no', la decisión es siempre 'rechaza'.
    Si alguno de C1 o C2 es 'no', también 'rechaza'.
    En cualquier otro caso (incluyendo 'no_evaluable' por falta de rasgos
    morfológicos), la decisión es 'acepta': la ausencia de evidencia de fallo
    no se penaliza.
    """
    if c3 == "no" or c1 == "no" or c2 == "no":
        return "rechaza"
    return "acepta"


# ---------------------------------------------------------------------
# Función principal
# ---------------------------------------------------------------------

def main():
    """
    Coordina la lectura del corpus, el análisis spaCy, la aplicación del
    criterio C1–C2–C3 y la escritura del reporte .txt y el CSV de decisiones.
    """
    corpus   = sys.argv[1] if len(sys.argv) > 1 else CORPUS_POR_DEFECTO
    salida_txt = sys.argv[2] if len(sys.argv) > 2 else SALIDA_TXT_POR_DEFECTO
    salida_csv = sys.argv[3] if len(sys.argv) > 3 else SALIDA_CSV_POR_DEFECTO

    oraciones = leer_oraciones(corpus)
    nlp = spacy.load(MODELO)

    # Crear directorio de salida CSV si no existe
    import os
    os.makedirs(os.path.dirname(salida_csv), exist_ok=True)

    filas_csv = []

    with open(salida_txt, "w", encoding="utf-8") as out:

        # Encabezado del reporte
        out.write("ANÁLISIS DE spaCy\n")
        out.write(f"Corpus: {corpus}  ({len(oraciones)} oraciones)\n")
        out.write(f"spaCy {spacy.__version__}  |  modelo {MODELO} {nlp.meta['version']}\n")
        out.write(f"Fecha: {datetime.now():%Y-%m-%d %H:%M}\n")
        out.write("Criterio: C1=concordancia sujeto-verbo | C2=concordancia det/sust/adj | C3=raíz verbal\n")
        out.write("=" * 70 + "\n\n")

        for i, fila in enumerate(oraciones, start=1):
            doc = nlp(fila["oracion"])

            id_   = fila.get("id") or str(i)
            nivel = f" (nivel {fila['nivel']})" if fila.get("nivel") else ""

            # Aplicar criterios
            res_c1, mot_c1 = evaluar_c1(doc)
            res_c2, mot_c2 = evaluar_c2(doc)
            res_c3, mot_c3 = evaluar_c3(doc)
            decision = decidir(res_c1, res_c2, res_c3)

            # Motivo de rechazo (vacío si acepta)
            motivos = []
            if res_c3 == "no":
                motivos.append(f"C3: {mot_c3}")
            if res_c1 == "no":
                motivos.append(f"C1: {mot_c1}")
            if res_c2 == "no":
                motivos.append(f"C2: {mot_c2}")
            motivo_str = " | ".join(motivos) if motivos else ""

            # Acumular fila CSV
            filas_csv.append({
                "id": id_,
                "decision_spacy": decision,
                "c1": res_c1,
                "c2": res_c2,
                "c3": res_c3,
                "motivo_rechazo": motivo_str,
            })

            # --- Bloque de texto ---
            out.write(f"[{id_}]{nivel} {fila['oracion']}\n")
            if fila.get("gramatical"):
                out.write(f"    ¿gramatical?: {fila['gramatical']}\n")
            if fila.get("fenomeno"):
                out.write(f"    fenómeno: {fila['fenomeno']}\n")

            out.write(f"\n    DECISIÓN: {decision.upper()}")
            out.write(f"  |  C1={res_c1}  C2={res_c2}  C3={res_c3}\n")
            if motivo_str:
                out.write(f"    Motivo: {motivo_str}\n")

            out.write("\n    palabra        categoría  función     depende de    rasgos\n")
            for t in doc:
                out.write(
                    f"    {t.text:<14} {t.pos_:<10} {t.dep_:<11} "
                    f"{t.head.text:<13} {t.morph}\n"
                )

            out.write("\n    Árbol de dependencias:\n")
            raiz = next(t for t in doc if t.dep_ == "ROOT")
            for linea in arbol(raiz):
                out.write("        " + linea + "\n")
            out.write("\n" + "-" * 70 + "\n\n")

    # Escribir CSV
    with open(salida_csv, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["id", "decision_spacy", "c1", "c2", "c3", "motivo_rechazo"],
            delimiter=";"
        )
        writer.writeheader()
        writer.writerows(filas_csv)

    # Resumen en terminal
    conteo = {}
    for fila in filas_csv:
        conteo[fila["decision_spacy"]] = conteo.get(fila["decision_spacy"], 0) + 1

    print(f"Listo: {len(oraciones)} oraciones analizadas")
    print(f"  -> {salida_txt}")
    print(f"  -> {salida_csv}")
    print("Decisiones:")
    for k in ("acepta", "rechaza"):
        print(f"  {k:<10}: {conteo.get(k, 0)}")


if __name__ == "__main__":
    main()
