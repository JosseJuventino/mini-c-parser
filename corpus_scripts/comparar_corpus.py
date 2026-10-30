"""
comparar_corpus.py

Procesa cada oración de corpus_fase1.csv con spaCy (modelo es_core_news_sm)
y genera:
  - tabla_comparacion.csv : una fila por oración
  - log_spacy.txt         : análisis palabra por palabra

Uso (con el entorno virtual activo):
    python comparar_corpus.py
"""

# --- Librerías -------------------------------------------------------------
import csv      # para leer y escribir archivos .csv
import os       # para comprobar si un archivo existe
import spacy    # la librería de NLP que analiza las oraciones

# --- Nombres de archivos ---------------------------------------------------
CORPUS = "corpus_fase1.csv"                      # entrada 1: las oraciones
PARSER_PROPIO = "resultados_parser_propio.csv"   # entrada 2: resultados del parser propio
SALIDA_TABLA = "tabla_comparacion.csv"           # salida 1: tabla resumen
SALIDA_LOG = "log_spacy.txt"                     # salida 2: análisis detallado

# Carga el modelo de español. Se hace UNA sola vez porque tarda unos segundos.
# 'nlp' es el que recibe texto y devuelve el análisis.
nlp = spacy.load("es_core_news_sm")

# --- Leer el corpus --------------------------------------------------------
# encoding="utf-8-sig" evita problemas con el BOM (una marca invisible que
# Excel y Windows agregan al inicio de los CSV).
# csv.DictReader convierte cada fila en un diccionario: fila["oracion"], etc.
# list(...) las guarda todas en una lista.
with open(CORPUS, encoding="utf-8-sig") as f:
    oraciones = list(csv.DictReader(f))

# --- Leer los resultados del parser propio (si P3 ya los entregó) ----------
# 'propio' será un diccionario {id: resultado}, por ejemplo {"1": "acepta"}.
propio = {}
if os.path.exists(PARSER_PROPIO):
    with open(PARSER_PROPIO, encoding="utf-8-sig") as f:
        # Comprensión de diccionario: para cada fila r, guarda id -> resultado.
        # .strip() quita espacios y .lower() pasa a minúsculas, para que
        # "Acepta " y "acepta" cuenten igual.
        propio = {r["id"]: r["resultado"].strip().lower() for r in csv.DictReader(f)}
    print(f"Parser propio: {len(propio)} resultados cargados.")
else:
    print(f"Aviso: no existe {PARSER_PROPIO}; esas columnas quedarán PENDIENTE.")

# --- Procesar cada oración -------------------------------------------------
filas = []  # aquí se acumulan las filas de la tabla final

# Se abre el log para escribir; se irá llenando dentro del ciclo.
with open(SALIDA_LOG, "w", encoding="utf-8") as log:
    for fila in oraciones:

        # spaCy analiza la oración. 'doc' es una secuencia de tokens
        # (palabras y signos), cada uno con sus etiquetas.
        doc = nlp(fila["oracion"])

        # Palabras sin signos de puntuación (quitamos el "." final, etc.).
        palabras = [t for t in doc if not t.is_punct]

        # La raíz del árbol de dependencias: normalmente el verbo principal.
        # next(...) toma el primer token cuya función (dep_) es "ROOT".
        raiz = next(t.text for t in doc if t.dep_ == "ROOT")

        # Resultado del parser propio para esta oración.
        # .get devuelve "PENDIENTE", si propio no tiene un resultado para esta id.
        resultado = propio.get(fila["id"], "PENDIENTE")
        if resultado == "PENDIENTE":
            coincide = "PENDIENTE"
        else:
            # Compara lo que hizo el parser con lo que esperábamos.
            # .startswith permite que "falla o da una sola lectura" cuente
            # como coincidencia si el resultado empieza igual.
            # NOTA: el corpus usa "falla" en el nivel 3, pero el parser propio puede devolver "falla o da una sola lectura".
            coincide = "si" if fila["esperado_parser_propio"].lower().startswith(resultado) else "no"

        # Una fila de la tabla final: un diccionario con una clave por columna.
        filas.append({
            "id": fila["id"],
            "nivel": fila["nivel"],
            "oracion": fila["oracion"],
            "gramatical": fila["gramatical"],
            "fenomeno": fila["fenomeno"],
            "esperado_parser_propio": fila["esperado_parser_propio"],
            "parser_propio": resultado,
            "parser_propio_coincide_con_esperado": coincide,
            # spaCy nunca rechaza: siempre devuelve un análisis.
            "spacy_veredicto": "analiza",
            "spacy_raiz": raiz,
            # Cada palabra con su categoría gramatical (pos_): "niño/NOUN".
            "spacy_etiquetas": " ".join(f"{t.text}/{t.pos_}" for t in palabras),
            # Cada palabra con su función (dep_) y la palabra de la que
            # depende (head): "niño:nsubj->come" significa que "niño" es el
            # sujeto de "come".
            "spacy_dependencias": " ".join(
                f"{t.text}:{t.dep_}->{t.head.text}" for t in palabras
            ),
        })

        # --- Log detallado: una línea por palabra ---
        log.write(f"[{fila['id']}] (nivel {fila['nivel']}) {fila['oracion']}\n")
        log.write(f"    fenómeno: {fila['fenomeno']}\n")
        for t in doc:
            # {:<14} reserva 14 caracteres alineados a la izquierda, para que
            # las columnas queden ordenadas. t.morph son los rasgos
            # (género, número, persona, tiempo...).
            log.write(f"    {t.text:<14} {t.pos_:<6} {t.dep_:<10} "
                      f"-> {t.head.text:<12} {t.morph}\n")
        log.write("\n")

# --- Guardar la tabla ------------------------------------------------------
# newline="" evita líneas en blanco extra en Windows.
with open(SALIDA_TABLA, "w", newline="", encoding="utf-8-sig") as f:
    # Los nombres de las columnas salen de las claves de la primera fila.
    w = csv.DictWriter(f, fieldnames=list(filas[0].keys()))
    w.writeheader()      # escribe la fila de encabezados
    w.writerows(filas)   # escribe todas las filas de datos

# --- Resumen en pantalla ---------------------------------------------------
# Oraciones marcadas como no gramaticales (gramatical == "no").
agram = [x for x in filas if x["gramatical"] == "no"]
print(f"Listo: {len(filas)} oraciones -> {SALIDA_TABLA} y {SALIDA_LOG}")
# Como spaCy siempre analiza, el número de analizadas es igual al de agramaticales.
print(f"Oraciones agramaticales que spaCy analiza sin rechazar: {len(agram)}/{len(agram)}")