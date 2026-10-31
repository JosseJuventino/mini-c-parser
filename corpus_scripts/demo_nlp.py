"""
demo_nlp.py  -  demo con spaCy

Uso:
    python demo_nlp.py                    # recorre las oraciones elegidas, con pausa
    python demo_nlp.py --rapido           # sin pausas
    python demo_nlp.py "El niño come."    # analiza una oración cualquiera
"""
import sys     # para leer lo que se escribe en la terminal (sys.argv)
import spacy   # librería de NLP

# Oraciones elegidas para la presentación.
# Cada elemento es una pareja (oración, nota sobre qué observar).
OPCIONES = [
    ("El niño come la manzana.",
     "Simple: spaCy la analiza sin problema."),
    ("El perro grande come rápidamente la comida en la casa.",
     "Con modificadores: adjetivo, adverbio y frase preposicional."),
    ("Vi al hombre con el telescopio.",
     "Ambigua: spaCy elige UNA lectura y no avisa de la otra."),
    ("La manzana que el niño comió estaba fresca.",
     "Relativa con hueco: una CFG simple no la maneja."),
    ("Los niño come la manzana.",
     "Agramatical: spaCy la analiza igual, no la rechaza."),
]


def arbol(token, nivel=0):
    """Árbol de dependencias como texto con sangría.

    Es una función RECURSIVA: se llama a sí misma para cada hijo del token.
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
    raiz = next(t for t in doc if t.dep_ == "ROOT")
    for linea in arbol(raiz):
        print("   " + linea)


def main():
    # sys.argv es la lista de lo escrito en la terminal. El elemento [0] es
    # el nombre del script, así que se toma desde el [1].
    # 'args' = textos normales; las opciones que empiezan con "--" se separan.
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    rapido = "--rapido" in sys.argv   # True si se pasó la opción --rapido

    print("Cargando spaCy...")
    nlp = spacy.load("es_core_news_sm")   # carga el modelo una sola vez

    # Modo 1: si se escribió una oración, se analiza solo esa y termina.
    if args:
        analizar(" ".join(args), "", nlp)
        return

    # Modo 2: recorre las oraciones elegidas.
    for oracion, nota in OPCIONES:
        analizar(oracion, nota, nlp)
        if not rapido:
            # input() detiene el programa hasta que se presiona Enter,
            # útil para ir explicando cada oración en vivo.
            input("\n[Enter para la siguiente oración]")


# Este bloque hace que main() se ejecute solo cuando el archivo se corre
# directamente (python demo_nlp.py), y no cuando otro archivo lo importa.
if __name__ == "__main__":
    main()