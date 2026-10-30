"""
demo_nlp.py  -  demo con spaCy

Uso:
    python demo_nlp.py                    # recorre las oraciones elegidas, con pausa
    python demo_nlp.py --rapido           # sin pausas
    python demo_nlp.py "El niño come."    # analiza una oración cualquiera
"""
import sys
import spacy

# Oraciones elegidas para la presentación
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
    """Árbol de dependencias como texto con sangría."""
    lineas = [f"{'    ' * nivel}{token.text}  ({token.dep_}, {token.pos_})"]
    for hijo in token.children:
        if not hijo.is_punct:
            lineas.extend(arbol(hijo, nivel + 1))
    return lineas


def analizar(oracion, nota, nlp):
    print("\n" + "=" * 70)
    print(f"ORACIÓN: {oracion}")
    if nota:
        print(f"Qué observar: {nota}")
    print("=" * 70)

    doc = nlp(oracion)
    print("\n[spaCy] palabra / categoría / función -> depende de")
    for t in doc:
        if not t.is_punct:
            print(f"   {t.text:<12} {t.pos_:<6} {t.dep_:<8} -> {t.head.text}")

    print("\n[spaCy] árbol de dependencias:")
    raiz = next(t for t in doc if t.dep_ == "ROOT")
    for linea in arbol(raiz):
        print("   " + linea)


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    rapido = "--rapido" in sys.argv

    print("Cargando spaCy...")
    nlp = spacy.load("es_core_news_sm")

    if args:
        analizar(" ".join(args), "", nlp)
        return

    for oracion, nota in OPCIONES:
        analizar(oracion, nota, nlp)
        if not rapido:
            input("\n[Enter para la siguiente oración]")


if __name__ == "__main__":
    main()