"""
correr_nltk.py

Segunda herramienta de NLP del benchmark: NLTK.

Pasa las oraciones de benchmark/corpus_fase2.csv por NLTK y guarda el
resultado de cada una en NLTK/logs/nltk.csv. El script solo lee las columnas
"id" y "oracion" del corpus; no mira las etiquetas esperadas.

NLTK no trae un analizador de español que diga si una oración es correcta.
Lo que se hace es:

  1. ETIQUETAR. Se entrena un etiquetador con cess_esp, un corpus de español
     anotado a mano que viene con NLTK. A cada palabra le asigna una etiqueta
     EAGLES, que incluye categoría, género, número y persona. Por ejemplo:
       da0mp0   determinante, masculino, plural
       ncfs000  nombre común, femenino, singular
       vmip3s0  verbo, indicativo, presente, 3.ª persona, singular

  2. AGRUPAR. Con nltk.RegexpParser se juntan en un sintagma nominal (SN) el
     determinante, el nombre y los adjetivos que van seguidos.

  3. DECIDIR. La oración se RECHAZA si incumple alguna de estas reglas y se
     ACEPTA si las cumple todas:
       R1  Dentro de un SN, el determinante y los adjetivos concuerdan en
           género y número con el nombre.
       R2  Cada verbo conjugado concuerda en persona y número con su sujeto.
           El sujeto es el SN o pronombre personal más cercano a la izquierda
           del verbo que no vaya detrás de una preposición, sin pasar de un
           "que". Si no hay ninguno, el sujeto es tácito y no se comprueba.
       R3  La oración tiene al menos un verbo conjugado.

Las reglas se fijaron antes de correr el corpus y no se ajustaron después.

Uso, desde la carpeta raíz del repositorio:
  python NLTK/correr_nltk.py

La primera vez descarga el corpus cess_esp de NLTK (necesita internet).
"""

import csv
import platform
from datetime import datetime
from pathlib import Path

import nltk
from nltk.corpus import cess_esp
from nltk.tokenize import RegexpTokenizer

# Esta carpeta (NLTK) guarda el script y sus logs. El corpus es el mismo para
# todos los enfoques y está en la carpeta benchmark del repositorio.
CARPETA = Path(__file__).resolve().parent
RUTA_CORPUS = CARPETA.parent / "benchmark" / "corpus_fase2.csv"
RUTA_LOG = CARPETA / "logs" / "nltk.csv"
RUTA_INFO = CARPETA / "logs" / "nltk_ejecucion.txt"

# Separa palabras y signos de puntuación.
TOKENIZADOR = RegexpTokenizer(r"\w+|[^\w\s]")

# Sintagma nominal: determinante opcional, adjetivos, un nombre y adjetivos.
# En las etiquetas EAGLES, "d" es determinante, "a" adjetivo y "n" nombre.
AGRUPADOR = nltk.RegexpParser("SN: {<d.*>?<a.*>*<n.*><a.*>*}")

# Valores de género o número que concuerdan con cualquier otro:
# "c" común, "n" invariable o neutro, "0" sin dato.
COMODINES = "cn0"

NOMBRES_DE_RASGOS = {
    "m": "masculino", "f": "femenino", "c": "común", "n": "invariable",
    "s": "singular", "p": "plural", "0": "sin dato",
}


# ---------------------------------------------------------------------
# Paso 1: etiquetador
# ---------------------------------------------------------------------

def cargar_entrenamiento():
    """
    Devuelve las oraciones anotadas de cess_esp como listas de pares
    (palabra, etiqueta).

    Se quitan los elementos vacíos del corpus (por ejemplo "*0*", que marca
    un sujeto omitido): no son palabras y su etiqueta empieza con "sn".
    """
    try:
        cess_esp.ensure_loaded()
    except LookupError:
        nltk.download("cess_esp")

    oraciones = []
    for oracion in cess_esp.tagged_sents():
        limpia = [
            (palabra, etiqueta)
            for palabra, etiqueta in oracion
            if not etiqueta.startswith("sn")
        ]
        if limpia:
            oraciones.append(limpia)
    return oraciones


def entrenar_etiquetador(oraciones):
    """
    Entrena una cadena de etiquetadores. Cada uno se usa solo cuando el
    anterior no sabe qué responder:

      1. Bigrama: la etiqueta más frecuente de la palabra según la etiqueta
         de la palabra anterior.
      2. Unigrama: la etiqueta más frecuente de la palabra.
      3. Mayúscula inicial: una palabra desconocida que empieza con mayúscula
         se toma como nombre propio.
      4. Sufijo: una palabra desconocida recibe la etiqueta más frecuente
         entre las palabras que terminan con sus mismas tres letras.
      5. Por defecto: nombre común masculino singular, la etiqueta más
         frecuente entre los nombres.
    """
    por_defecto = nltk.DefaultTagger("ncms000")
    sufijo = nltk.AffixTagger(oraciones, affix_length=-3, backoff=por_defecto)
    mayuscula = nltk.RegexpTagger([(r"^[A-ZÁÉÍÓÚÑ]", "np00000")], backoff=sufijo)
    unigrama = nltk.UnigramTagger(oraciones, backoff=mayuscula)
    bigrama = nltk.BigramTagger(oraciones, backoff=unigrama)
    return bigrama


def medir_exactitud(oraciones):
    """
    Mide qué tan bien etiqueta la cadena: se entrena con el primer 90 % de
    cess_esp y se cuenta la proporción de etiquetas acertadas en el 10 %
    restante, que el etiquetador no vio.
    """
    corte = len(oraciones) * 9 // 10
    etiquetador = entrenar_etiquetador(oraciones[:corte])
    return etiquetador.accuracy(oraciones[corte:])


def etiquetar(oracion, etiquetador, vocabulario):
    """
    Devuelve la oración como lista de pares (palabra, etiqueta).

    La primera palabra lleva mayúscula solo por ir al inicio. Si el
    etiquetador no la conoce así, se le consulta en minúscula.
    """
    palabras = TOKENIZADOR.tokenize(oracion)
    consulta = list(palabras)
    if consulta and consulta[0] not in vocabulario:
        consulta[0] = consulta[0].lower()

    etiquetas = [etiqueta for _, etiqueta in etiquetador.tag(consulta)]
    return list(zip(palabras, etiquetas))


# ---------------------------------------------------------------------
# Paso 2: agrupar en sintagmas nominales
# ---------------------------------------------------------------------

def agrupar(etiquetadas):
    """
    Aplica el agrupador y devuelve una lista de elementos en orden. Cada
    elemento es ("SN", [(palabra, etiqueta), ...]) o ("palabra", (palabra,
    etiqueta)).
    """
    elementos = []
    for nodo in AGRUPADOR.parse(etiquetadas):
        if isinstance(nodo, nltk.Tree):
            elementos.append(("SN", list(nodo.leaves())))
        else:
            elementos.append(("palabra", nodo))
    return elementos


# ---------------------------------------------------------------------
# Paso 3: reglas de decisión
# ---------------------------------------------------------------------

def genero_y_numero(etiqueta):
    """Género y número de un nombre, un determinante o un adjetivo."""
    if etiqueta.startswith("n"):
        return etiqueta[2], etiqueta[3]
    return etiqueta[3], etiqueta[4]


def concuerdan(valor_1, valor_2):
    return valor_1 == valor_2 or valor_1 in COMODINES or valor_2 in COMODINES


def describir(genero, numero):
    return f"{NOMBRES_DE_RASGOS[genero]} {NOMBRES_DE_RASGOS[numero]}"


def es_verbo_conjugado(etiqueta):
    # Modo indicativo (i), subjuntivo (s) o imperativo (m).
    return etiqueta.startswith("v") and etiqueta[2] in "ism"


def es_pronombre_sujeto(etiqueta):
    # Pronombre personal en caso nominativo (n) o sin caso marcado (0).
    # Quedan fuera los de objeto, como "las" en "las comieron".
    return etiqueta.startswith("pp") and etiqueta[5] in "n0"


def nombre_del_sn(sintagma):
    """El nombre de un SN: la única palabra cuya etiqueta empieza con "n"."""
    for palabra, etiqueta in sintagma:
        if etiqueta.startswith("n"):
            return palabra, etiqueta


def regla_1(elementos):
    """R1: concordancia de género y número dentro de cada SN."""
    fallos = []
    for tipo, contenido in elementos:
        if tipo != "SN":
            continue
        nombre, etiqueta_nombre = nombre_del_sn(contenido)
        genero_nombre, numero_nombre = genero_y_numero(etiqueta_nombre)

        for palabra, etiqueta in contenido:
            if etiqueta.startswith("n"):
                continue
            genero, numero = genero_y_numero(etiqueta)
            if not (concuerdan(genero, genero_nombre) and concuerdan(numero, numero_nombre)):
                fallos.append(
                    f"R1: «{palabra}» ({describir(genero, numero)}) no concuerda "
                    f"con «{nombre}» ({describir(genero_nombre, numero_nombre)})"
                )
    return fallos


def buscar_sujeto(elementos, posicion_verbo):
    """
    Busca el sujeto de un verbo hacia la izquierda. Devuelve (texto, persona,
    número) o None si el sujeto es tácito.
    """
    posicion = posicion_verbo - 1
    while posicion >= 0:
        tipo, contenido = elementos[posicion]

        if tipo == "palabra":
            etiqueta = contenido[1]
            # "que" (conjunción o relativo) marca el inicio de la subordinada:
            # el sujeto no puede estar antes.
            if etiqueta == "cs" or etiqueta.startswith("pr"):
                return None

        es_candidato = tipo == "SN" or es_pronombre_sujeto(contenido[1])
        if es_candidato:
            anterior = elementos[posicion - 1] if posicion > 0 else None
            tras_preposicion = (
                anterior is not None
                and anterior[0] == "palabra"
                and anterior[1][1].startswith("sp")
            )
            if not tras_preposicion:
                if tipo == "SN":
                    nombre, etiqueta = nombre_del_sn(contenido)
                    numero = genero_y_numero(etiqueta)[1]
                    if etiqueta.startswith("np"):
                        numero = "s"  # un nombre propio es singular
                    return nombre, "3", numero

                palabra, etiqueta = contenido
                persona = etiqueta[2]
                if etiqueta[7] == "p":
                    persona = "3"  # "usted" y "ustedes" llevan verbo en 3.ª persona
                return palabra, persona, etiqueta[4]

        posicion -= 1
    return None


def regla_2(elementos):
    """R2: concordancia de persona y número entre el sujeto y el verbo."""
    fallos = []
    for posicion, (tipo, contenido) in enumerate(elementos):
        if tipo != "palabra":
            continue
        verbo, etiqueta = contenido
        # Solo indicativo y subjuntivo: el imperativo no lleva sujeto expreso.
        if not (etiqueta.startswith("v") and etiqueta[2] in "is"):
            continue

        sujeto = buscar_sujeto(elementos, posicion)
        if sujeto is None:
            continue
        texto, persona, numero = sujeto
        persona_verbo, numero_verbo = etiqueta[4], etiqueta[5]

        if persona != persona_verbo or not concuerdan(numero, numero_verbo):
            fallos.append(
                f"R2: el sujeto «{texto}» ({persona}.ª persona "
                f"{NOMBRES_DE_RASGOS[numero]}) no concuerda con el verbo «{verbo}» "
                f"({persona_verbo}.ª persona {NOMBRES_DE_RASGOS[numero_verbo]})"
            )
    return fallos


def regla_3(etiquetadas):
    """R3: la oración tiene al menos un verbo conjugado."""
    if any(es_verbo_conjugado(etiqueta) for _, etiqueta in etiquetadas):
        return []
    return ["R3: la oración no tiene verbo conjugado"]


def decidir(etiquetadas):
    """
    Devuelve la decisión ("acepta" o "rechaza"), la lista de fallos y los
    elementos agrupados.
    """
    elementos = agrupar(etiquetadas)
    fallos = regla_1(elementos) + regla_2(elementos) + regla_3(etiquetadas)
    decision = "rechaza" if fallos else "acepta"
    return decision, fallos, elementos


# ---------------------------------------------------------------------
# Textos del log
# ---------------------------------------------------------------------

def texto_analisis(elementos):
    """Palabra/etiqueta de toda la oración, con cada SN entre corchetes."""
    partes = []
    for tipo, contenido in elementos:
        if tipo == "SN":
            dentro = " ".join(f"{palabra}/{etiqueta}" for palabra, etiqueta in contenido)
            partes.append(f"[SN {dentro}]")
        else:
            palabra, etiqueta = contenido
            partes.append(f"{palabra}/{etiqueta}")
    return " ".join(partes)


def categoria(palabra, etiqueta):
    """
    Traduce la etiqueta EAGLES a las categorías de la gramática del proyecto,
    para poder comparar el etiquetado. Devuelve None para la puntuación.
    """
    if etiqueta.startswith("F"):
        return None
    if palabra.lower() == "que":
        return "que"
    if etiqueta.startswith("spc"):
        return "PREP+DET"  # contracciones "al" y "del"
    inicios = [
        ("d", "DET"), ("nc", "N"), ("np", "NP"), ("a", "Adj"), ("v", "V"),
        ("r", "ADV"), ("sp", "PREP"), ("p", "PRON"),
    ]
    for inicio, nombre in inicios:
        if etiqueta.startswith(inicio):
            return nombre
    return "OTRO"


def texto_categorias(etiquetadas):
    categorias = [categoria(palabra, etiqueta) for palabra, etiqueta in etiquetadas]
    return " ".join(c for c in categorias if c is not None)


# ---------------------------------------------------------------------
# Programa principal
# ---------------------------------------------------------------------

def main():
    entrenamiento = cargar_entrenamiento()
    exactitud = medir_exactitud(entrenamiento)
    etiquetador = entrenar_etiquetador(entrenamiento)
    vocabulario = {palabra for oracion in entrenamiento for palabra, _ in oracion}

    with open(RUTA_CORPUS, encoding="utf-8-sig", newline="") as archivo:
        corpus = list(csv.DictReader(archivo, delimiter=";"))

    filas = []
    for fila in corpus:
        etiquetadas = etiquetar(fila["oracion"], etiquetador, vocabulario)
        decision, fallos, elementos = decidir(etiquetadas)
        filas.append({
            "id": fila["id"],
            "oracion": fila["oracion"],
            "decision": decision,
            "reglas": " ".join(sorted({fallo[:2] for fallo in fallos})),
            "analisis": texto_analisis(elementos),
            "categorias": texto_categorias(etiquetadas),
            "detalle": " | ".join(fallos),
        })

    RUTA_LOG.parent.mkdir(parents=True, exist_ok=True)
    with open(RUTA_LOG, "w", encoding="utf-8", newline="") as archivo:
        escritor = csv.DictWriter(archivo, fieldnames=list(filas[0]), delimiter=";")
        escritor.writeheader()
        escritor.writerows(filas)

    aceptadas = sum(1 for fila in filas if fila["decision"] == "acepta")
    por_regla = {
        regla: sum(1 for fila in filas if regla in fila["reglas"].split())
        for regla in ("R1", "R2", "R3")
    }
    palabras = sum(len(oracion) for oracion in entrenamiento)
    informacion = [
        f"Fecha de la corrida: {datetime.now():%Y-%m-%d %H:%M:%S}",
        f"Python: {platform.python_version()}",
        f"NLTK: {nltk.__version__}",
        f"Corpus de entrenamiento: cess_esp ({len(entrenamiento)} oraciones, {palabras} palabras)",
        "Etiquetador: bigrama -> unigrama -> mayúscula inicial -> sufijo de 3 letras -> por defecto",
        f"Exactitud del etiquetador (90 % para entrenar, 10 % para medir): {exactitud:.4f}",
        f"Corpus de prueba: {RUTA_CORPUS.name} ({len(filas)} oraciones)",
        f"Aceptadas: {aceptadas}",
        f"Rechazadas: {len(filas) - aceptadas}",
        f"Rechazos por regla: R1 = {por_regla['R1']}, R2 = {por_regla['R2']}, R3 = {por_regla['R3']}",
        f"Log: {RUTA_LOG.name}",
    ]
    RUTA_INFO.write_text("\n".join(informacion) + "\n", encoding="utf-8")
    print("\n".join(informacion))


if __name__ == "__main__":
    main()
