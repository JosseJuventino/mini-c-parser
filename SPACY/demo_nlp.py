"""
demo_nlp.py  -  demo en vivo con spaCy

Analiza oraciones en español con spaCy (modelo es_core_news_sm) y muestra, para
cada una, la categoría de cada palabra, su función en la oración y el árbol de
dependencias. Las oraciones elegidas pertenecen al corpus de la Fase 1, las
mismas que intenta analizar la gramática extendida al español.

Uso (con el entorno virtual activo):
    python demo_nlp.py                    # recorre las oraciones elegidas, con pausa
    python demo_nlp.py --rapido           # sin pausas
    python demo_nlp.py "El niño come."    # analiza una oración cualquiera
"""
import sys     # para leer lo que se escribe en la terminal
import spacy   # librería de NLP

MODELO = "es_core_news_sm"

# Oraciones elegidas para la presentación, tomadas del corpus.
# Cada elemento es una pareja: (oración, nota sobre qué observar).
OPCIONES = [
    ("Marcela come los dulces.",
     "Simple: spaCy la analiza sin problema."),
    ("El esqueleto pequeño escribe rápidamente el código nuevo en la clase.",
     "Con modificadores: adjetivos, adverbio y frase preposicional."),
    ("Marcela vio al fantasma con el telescopio.",
     "Ambigua: spaCy une 'con el telescopio' al verbo y no avisa de la otra lectura."),
    ("El examen que Jaime corrigió asustó a Jose.",
     "Relativa con hueco: spaCy la resuelve; una CFG simple no."),
    ("Los fantasma come los dulces.",
     "Agramatical: spaCy la analiza igual, no la rechaza."),
]


def arbol(token, nivel=0):
    """Árbol de dependencias como texto con sangría.

    Es una función recursiva: se llama a sí misma para cada hijo del token.
    'nivel' indica la profundidad y define cuántos espacios de sangría lleva
    cada línea.
    """
    # Línea del token actual: sangría + palabra + (función, categoría).
    lineas = [f"{'    ' * nivel}{token.text}  ({token.dep_}, {token.pos_})"]
    # token.children son las palabras que dependen de este token.
    for hijo in token.children:
        if not hijo.is_punct:                        # se omiten los signos
            lineas.extend(arbol(hijo, nivel + 1))    # llamada recursiva, un nivel más adentro
    return lineas


def analizar(oracion, nota, nlp):
    """Muestra el análisis completo de una oración."""
    # Encabezado con la oración y, si hay, la nota de qué observar.
    print("\n" + "=" * 70)
    print(f"ORACIÓN: {oracion}")
    if nota:
        print(f"Qué observar: {nota}")
    print("=" * 70)

    doc = nlp(oracion)   # spaCy analiza la oración

    # Tabla palabra por palabra:
    #   t.pos_  = categoría gramatical (NOUN, VERB, DET...)
    #   t.dep_  = función en la oración (nsubj = sujeto, obj = objeto...)
    #   t.head  = palabra de la que depende
    print("\n[spaCy] palabra / categoría / función -> depende de")
    for t in doc:
        if not t.is_punct:   # se omiten los signos de puntuación
            print(f"   {t.text:<12} {t.pos_:<6} {t.dep_:<8} -> {t.head.text}")

    # El árbol parte de la raíz (el verbo principal, dep_ == "ROOT") y baja
    # por sus dependientes.
    print("\n[spaCy] árbol de dependencias:")
    raiz = next((t for t in doc if t.dep_ == "ROOT"), None)
    if raiz is not None:
        for linea in arbol(raiz):
            print("   " + linea)


def main():
    # sys.argv es la lista de lo escrito en la terminal. El elemento [0] es
    # el nombre del script, así que se toma desde el [1].
    # 'args' = textos normales; las opciones que empiezan con "--" se separan.
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    rapido = "--rapido" in sys.argv   # True si se pasó la opción --rapido

    print("Cargando spaCy...")
    nlp = spacy.load(MODELO)          # carga el modelo una sola vez

    # Modo 1: si se escribió una oración, se analiza solo esa y termina.
    if args:
        analizar(" ".join(args), "", nlp)
        return

    # Modo 2: recorre las oraciones elegidas.
    for i, (oracion, nota) in enumerate(OPCIONES, start=1):
        analizar(oracion, nota, nlp)
        # input() detiene el programa hasta que se presiona Enter, útil para ir
        # explicando cada oración en vivo. No se pausa después de la última.
        if not rapido and i < len(OPCIONES):
            input("\n[Enter para la siguiente oración]")


# Este bloque hace que main() se ejecute solo cuando el archivo se corre
# directamente (python demo_nlp.py), y no cuando otro archivo lo importa.
if __name__ == "__main__":
    main()
