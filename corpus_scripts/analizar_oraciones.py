"""
analizar_oraciones.py

Procesa un corpus de oraciones en español con spaCy y guarda en un archivo
de texto el análisis lingüístico obtenido mediante el modelo es_core_news_sm.

Entrada:
  - CSV: requiere una columna "oracion". Las columnas "id", "nivel",
    "fenomeno" y "gramatical" son opcionales.
  - TXT: una oración por línea.

Uso:
  python analizar_oraciones.py
  python analizar_oraciones.py mi_corpus.csv
  python analizar_oraciones.py mi_corpus.csv salida.txt
"""

import csv
import sys
from datetime import datetime

import spacy


# ---------------------------------------------------------------------
# Configuración predeterminada
# ---------------------------------------------------------------------

# Corpus utilizado cuando no se proporciona una ruta como argumento.
CORPUS_POR_DEFECTO = "corpus_fase1.csv"

# Archivo en el que se guardará el reporte generado.
SALIDA_POR_DEFECTO = "analisis_spacy.txt"

# Modelo de spaCy entrenado para procesar textos en español.
MODELO = "es_core_news_sm"


# ---------------------------------------------------------------------
# Lectura del corpus
# ---------------------------------------------------------------------

def leer_csv(ruta):
    """
    Lee un CSV y devuelve sus filas como una lista de diccionarios.

    Intenta las codificaciones UTF-8 (incluido el posible BOM) y
    Windows-1252. Detecta como separador la coma o el punto y coma,
    examinando cuál aparece más veces en la primera línea.

    Parámetro:
        ruta (str): ruta del archivo CSV.

    Retorna:
        list[dict]: registros del CSV, usando los encabezados como claves.
    """

    # Se intenta primero UTF-8; si la lectura falla por la codificación,
    # se prueba Windows-1252.
    texto = None
    for codificacion in ("utf-8-sig", "cp1252"):
        try:
            with open(ruta, encoding=codificacion, newline="") as f:
                texto = f.read()
            break
        except UnicodeDecodeError:
            continue

    # Evita continuar si el archivo no pudo decodificarse.
    if texto is None:
        sys.exit(
            "Error: no se pudo interpretar la codificación del CSV. "
            "Utilice UTF-8 o Windows-1252."
        )

    # Se compara la frecuencia de coma y punto y coma en el encabezado.
    primera = texto.splitlines()[0] if texto else ""
    separador = ";" if primera.count(";") > primera.count(",") else ","

    # DictReader toma la primera fila como encabezado y convierte cada
    # registro en un diccionario: nombre_de_columna -> valor.
    return list(csv.DictReader(texto.splitlines(), delimiter=separador))


def leer_oraciones(ruta):
    """
    Lee un corpus CSV o TXT y devuelve una lista de diccionarios.
    Cada diccionario contiene al menos la clave "oracion".

    En un TXT, cada línea no vacía se considera una oración y recibe
    un identificador consecutivo. En un CSV, se requiere la columna
    "oracion"; las demás columnas se conservan como metadatos.
    """

    # La extensión permite decidir si el archivo se interpreta como TXT.
    if ruta.lower().endswith(".txt"):
        # Un .txt: una oración por línea; se ignoran las líneas vacías.
        for codificacion in ("utf-8-sig", "cp1252"):
            try:
                with open(ruta, encoding=codificacion) as f:
                    # strip() elimina espacios y saltos de línea externos.
                    # El filtro descarta las líneas vacías.
                    lineas = [l.strip() for l in f if l.strip()]
                break
            except UnicodeDecodeError:
                continue

        if lineas is None:
            sys.exit(
                "Error: no se pudo interpretar la codificación del TXT. "
                "Utilice UTF-8 o Windows-1252."
            )

        # Cada línea se convierte en un diccionario con un ID consecutivo.
        return [
            {"id": str(i), "oracion": linea}
            for i, linea in enumerate(lineas, start=1)
        ]

    # Si no es TXT, se procesa como CSV mediante la función anterior.
    filas = leer_csv(ruta)

    # Se verifica que haya registros y que exista la columna obligatoria.
    if not filas or "oracion" not in filas[0]:
        columnas = list(filas[0].keys()) if filas else []
        sys.exit(
            "Error: el CSV necesita una columna llamada 'oracion'. "
            f"Columnas encontradas: {columnas}"
        )

    return filas


# ---------------------------------------------------------------------
# Construcción recursiva del árbol de dependencias
# ---------------------------------------------------------------------

def arbol(token, nivel=0):
    """
    Construye las líneas de texto que representan el subárbol de un token.

    Parámetros:
        token: token de spaCy desde el que comienza el recorrido.
        nivel (int): profundidad actual; determina la sangría del nodo.

    Retorna:
        list[str]: representación textual del token y sus descendientes.

    La recursividad permite visitar cada hijo y, a su vez, los hijos de
    ese hijo. Cuando un token no tiene hijos, el ciclo termina y se
    devuelve únicamente la línea correspondiente a ese token.
    """

    # Se representa el token actual. Cada nivel agrega cuatro espacios
    # para mostrar visualmente la profundidad dentro del árbol.
    lineas = [f"{'    ' * nivel}{token.text}  ({token.dep_}, {token.pos_})"]

    # children contiene los tokens que dependen directamente del actual.
    for hijo in token.children:

        # La puntuación se excluye del árbol, aunque puede aparecer
        # en la tabla general de tokens.
        if not hijo.is_punct:

            # Se llama de nuevo a la función para recorrer el subárbol
            # del hijo. nivel + 1 aumenta la profundidad de la sangría.
            lineas.extend(arbol(hijo, nivel + 1))

    return lineas


# ---------------------------------------------------------------------
# Función principal
# ---------------------------------------------------------------------

def main():
    """
    Coordina la lectura del corpus, la carga del modelo, el análisis
    de cada oración y la escritura del reporte de resultados.
    """

    # sys.argv contiene los argumentos recibidos desde la terminal.
    # El primer argumento opcional es el corpus y el segundo es la salida.
    corpus = sys.argv[1] if len(sys.argv) > 1 else CORPUS_POR_DEFECTO
    salida = sys.argv[2] if len(sys.argv) > 2 else SALIDA_POR_DEFECTO

    # Se leen las oraciones y los metadatos del corpus.
    oraciones = leer_oraciones(corpus)
    nlp = spacy.load(MODELO)

    # Se abre el archivo de salida en modo escritura. UTF-8 conserva
    # correctamente los caracteres y tildes del español.
    with open(salida, "w", encoding="utf-8") as out:

        # Encabezado del reporte: identifica el corpus, las versiones
        # de spaCy y del modelo, y la fecha en que se realizó el análisis.
        out.write("ANÁLISIS DE spaCy\n")
        out.write(f"Corpus: {corpus}  ({len(oraciones)} oraciones)\n")
        out.write(f"spaCy {spacy.__version__}  |  modelo {MODELO} {nlp.meta['version']}\n")
        out.write(f"Fecha: {datetime.now():%Y-%m-%d %H:%M}\n")
        out.write("=" * 70 + "\n\n")

        # Se procesa cada fila del corpus. enumerate() proporciona un
        # contador desde 1 para identificar la posición de la oración.
        for i, fila in enumerate(oraciones, start=1):

            # nlp() procesa el texto con el modelo y devuelve un objeto Doc.
            # Doc contiene los tokens y las anotaciones lingüísticas
            # que se consultan para generar el reporte.
            doc = nlp(fila["oracion"])

            # Se utiliza el ID del corpus o, si no existe, la posición
            # de la oración dentro del archivo.
            id_ = fila.get("id") or str(i)

            # El nivel se muestra únicamente cuando está disponible.
            nivel = f" (nivel {fila['nivel']})" if fila.get("nivel") else ""

            # Se escribe el texto de la oración y los metadatos opcionales.
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

    # Mensaje en la terminal para indicar que el reporte se generó.
    print(f"Listo: {len(oraciones)} oraciones analizadas -> {salida}")


# Esta condición ejecuta main() solo cuando el archivo se ejecuta
# directamente, y no cuando se importa desde otro módulo.
if __name__ == "__main__":
    main()
