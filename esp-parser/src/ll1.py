"""
ll1.py

Comprueba que la gramática declarada en gramatica.py es LL(1).

Una gramática es LL(1) cuando, al mirar solo el siguiente token, siempre hay
una única producción posible. La comprobación sigue lo visto en clase:

  1. FIRST(A): terminales con los que puede empezar lo que deriva A.
  2. FOLLOW(A): terminales que pueden aparecer justo después de A.
  3. Definición de gramática LL(1). Para cada par de producciones del mismo
     no terminal, A -> alfa y A -> beta:
       (i)  FIRST(alfa) y FIRST(beta) no tienen elementos en común.
       (ii) Si epsilon está en FIRST(alfa), ni FIRST(alfa) ni FIRST(beta)
            tienen terminales en común con FOLLOW(A).
  4. Tabla LL(1). Para cada producción A -> alfa:
       - por cada terminal a de FIRST(alfa) se agrega A -> alfa a M[A, a];
       - si epsilon está en FIRST(alfa), se agrega A -> alfa a M[A, b] por
         cada terminal b de FOLLOW(A).
     Una celda con dos producciones distintas es un CONFLICTO. Las celdas
     vacías son errores sintácticos.

La gramática es LL(1) si se cumplen las condiciones del paso 3 y la tabla
del paso 4 no tiene conflictos (las dos comprobaciones son equivalentes y
se hacen ambas).

Esta verificación se activa sola: ParserEsp llama a verificar_ll1() antes de
analizar una oración, y si la gramática no fuera LL(1) el parser se detiene
con el error GramaticaNoLL1.

Uso directo, para ver el detalle completo (desde la carpeta esp-parser/src):
  python ll1.py
      imprime gramática, FIRST, FOLLOW, condiciones y tabla
  python ll1.py ../docs/ll1_reporte.txt ../docs/ll1_tabla.csv
      además guarda el reporte en texto y la tabla de doble entrada en CSV
"""

import csv
import sys

from gramatica import EPSILON, GRAMATICA, INICIAL


class GramaticaNoLL1(Exception):
    """La gramática no cumple la definición de LL(1)."""


# ---------------------------------------------------------------------
# Paso 1: FIRST
# ---------------------------------------------------------------------

def first_de_secuencia(secuencia, first, gramatica):
    """
    Calcula FIRST de una secuencia de símbolos (el lado derecho de una
    producción, o una parte de él).

    Se recorre la secuencia de izquierda a derecha. Cada símbolo aporta su
    FIRST, y solo se sigue con el siguiente si el actual puede desaparecer
    (derivar la cadena vacía). Si todos pueden desaparecer, o la secuencia
    está vacía, el resultado incluye EPSILON.
    """
    resultado = set()

    for simbolo in secuencia:
        if simbolo not in gramatica:
            # Un terminal empieza consigo mismo y nunca desaparece.
            resultado.add(simbolo)
            return resultado

        resultado |= first[simbolo] - {EPSILON}
        if EPSILON not in first[simbolo]:
            return resultado

    resultado.add(EPSILON)
    return resultado


def calcular_first(gramatica):
    """
    Devuelve un diccionario no_terminal -> conjunto FIRST.

    Los conjuntos empiezan vacíos y se repasan todas las producciones hasta
    que una pasada completa ya no agrega nada nuevo (punto fijo).
    """
    first = {no_terminal: set() for no_terminal in gramatica}

    cambio = True
    while cambio:
        cambio = False
        for no_terminal, producciones in gramatica.items():
            for produccion in producciones:
                nuevos = first_de_secuencia(produccion, first, gramatica)
                if not nuevos <= first[no_terminal]:
                    first[no_terminal] |= nuevos
                    cambio = True

    return first


# ---------------------------------------------------------------------
# Paso 2: FOLLOW
# ---------------------------------------------------------------------

def calcular_follow(gramatica, first):
    """
    Devuelve un diccionario no_terminal -> conjunto FOLLOW.

    Para cada aparición de un no terminal B en una producción A -> ... B beta:
      - todo lo que hay en FIRST(beta), menos EPSILON, entra en FOLLOW(B);
      - si beta puede desaparecer (o no hay nada después de B), todo
        FOLLOW(A) también entra en FOLLOW(B).

    No se agrega el marcador "$" al símbolo inicial porque la gramática ya
    termina con el token EOF (Programa -> Oracion EOF), que cumple ese papel.
    Por eso FOLLOW(Programa) queda vacío.
    """
    follow = {no_terminal: set() for no_terminal in gramatica}

    cambio = True
    while cambio:
        cambio = False
        for no_terminal, producciones in gramatica.items():
            for produccion in producciones:
                for posicion, simbolo in enumerate(produccion):
                    if simbolo not in gramatica:
                        continue

                    resto = produccion[posicion + 1:]
                    first_resto = first_de_secuencia(resto, first, gramatica)

                    nuevos = first_resto - {EPSILON}
                    if EPSILON in first_resto:
                        nuevos |= follow[no_terminal]

                    if not nuevos <= follow[simbolo]:
                        follow[simbolo] |= nuevos
                        cambio = True

    return follow


# ---------------------------------------------------------------------
# Paso 3: condiciones de la definición de gramática LL(1)
# ---------------------------------------------------------------------

def comprobar_condiciones(gramatica, first, follow):
    """
    Comprueba las condiciones (i) y (ii) para cada par de producciones del
    mismo no terminal.

    Devuelve la lista de incumplimientos. Cada uno es una tupla
    (condición, no_terminal, alfa, beta, elementos_en_común).
    """
    incumplimientos = []

    for no_terminal, producciones in gramatica.items():
        for posicion, alfa in enumerate(producciones):
            first_alfa = first_de_secuencia(alfa, first, gramatica)

            for beta in producciones[posicion + 1:]:
                first_beta = first_de_secuencia(beta, first, gramatica)

                # (i) FIRST(alfa) y FIRST(beta) deben ser disjuntos.
                comunes = first_alfa & first_beta
                if comunes:
                    incumplimientos.append(
                        ("i", no_terminal, alfa, beta, comunes)
                    )

                # (ii) Si una de las dos puede desaparecer, ninguna puede
                # empezar con un terminal de FOLLOW(A). Se revisa en los
                # dos sentidos porque cualquiera de las dos puede ser la
                # que deriva la cadena vacía.
                for vacia, otra in ((alfa, beta), (beta, alfa)):
                    first_vacia = first_de_secuencia(vacia, first, gramatica)
                    if EPSILON not in first_vacia:
                        continue

                    first_otra = first_de_secuencia(otra, first, gramatica)
                    comunes = (
                        (first_vacia | first_otra) - {EPSILON}
                    ) & follow[no_terminal]
                    if comunes:
                        incumplimientos.append(
                            ("ii", no_terminal, vacia, otra, comunes)
                        )

    return incumplimientos


# ---------------------------------------------------------------------
# Paso 4: tabla LL(1) y conflictos
# ---------------------------------------------------------------------

def construir_tabla(gramatica, first, follow):
    """
    Construye la tabla LL(1) y la lista de conflictos.

    tabla[(no_terminal, terminal)] = producción que se debe aplicar.
    Cada conflicto es una tupla (no_terminal, terminal, producción_1,
    producción_2): dos producciones distintas que compiten por la misma celda.
    """
    tabla = {}
    conflictos = []

    for no_terminal, producciones in gramatica.items():
        for produccion in producciones:
            first_produccion = first_de_secuencia(produccion, first, gramatica)

            # Terminales que hacen elegir esta producción.
            terminales = first_produccion - {EPSILON}
            if EPSILON in first_produccion:
                terminales |= follow[no_terminal]

            for terminal in terminales:
                celda = (no_terminal, terminal)
                if celda in tabla and tabla[celda] != produccion:
                    conflictos.append(
                        (no_terminal, terminal, tabla[celda], produccion)
                    )
                else:
                    tabla[celda] = produccion

    return tabla, conflictos


def analizar_gramatica(gramatica):
    """
    Ejecuta los cuatro pasos sobre una gramática y devuelve un diccionario
    con todo lo calculado. No lanza errores: solo informa.
    """
    first = calcular_first(gramatica)
    follow = calcular_follow(gramatica, first)
    incumplimientos = comprobar_condiciones(gramatica, first, follow)
    tabla, conflictos = construir_tabla(gramatica, first, follow)

    terminales = {
        simbolo
        for producciones in gramatica.values()
        for produccion in producciones
        for simbolo in produccion
        if simbolo not in gramatica
    }

    return {
        "gramatica": gramatica,
        "terminales": terminales,
        "first": first,
        "follow": follow,
        "incumplimientos": incumplimientos,
        "tabla": tabla,
        "conflictos": conflictos,
        "es_ll1": not incumplimientos and not conflictos,
    }


# ---------------------------------------------------------------------
# Verificación que se activa al ejecutar el parser
# ---------------------------------------------------------------------

# El resultado se guarda aquí para calcularlo una sola vez por ejecución,
# aunque se analicen muchas oraciones.
_REPORTE = None


def verificar_ll1():
    """
    Comprueba que GRAMATICA (gramatica.py) es LL(1) y devuelve el reporte.

    ParserEsp la llama antes de analizar. Si la gramática no es LL(1) lanza
    GramaticaNoLL1 con las condiciones incumplidas y las celdas en conflicto.
    """
    global _REPORTE

    if _REPORTE is None:
        _REPORTE = analizar_gramatica(GRAMATICA)

    if not _REPORTE["es_ll1"]:
        detalle = [
            "  " + texto_incumplimiento(incumplimiento)
            for incumplimiento in _REPORTE["incumplimientos"]
        ] + [
            "  " + texto_conflicto(conflicto)
            for conflicto in _REPORTE["conflictos"]
        ]
        raise GramaticaNoLL1(
            "La gramática de gramatica.py no es LL(1):\n" + "\n".join(detalle)
        )

    return _REPORTE


def reconocer(tipos, tabla, inicial=INICIAL):
    """
    Analizador LL(1) dirigido por la tabla, con una pila de símbolos: dice si
    una lista de tipos de token (terminada en "EOF") pertenece al lenguaje
    de la gramática.

    No construye el árbol. Se usa en las pruebas para comprobar que
    ParserEsp acepta y rechaza exactamente lo mismo que la gramática de
    gramatica.py, es decir, que la gramática verificada es la implementada.
    """
    no_terminales = {no_terminal for no_terminal, _ in tabla}
    pila = [inicial]
    posicion = 0

    while pila:
        cima = pila.pop()
        actual = tipos[posicion] if posicion < len(tipos) else None

        if cima in no_terminales:
            produccion = tabla.get((cima, actual))
            if produccion is None:
                return False  # celda vacía: error sintáctico
            # Se apila al revés para que el primer símbolo quede arriba.
            pila.extend(reversed(produccion))
        else:
            if cima != actual:
                return False
            posicion += 1

    return posicion == len(tipos)


# ---------------------------------------------------------------------
# Textos para mostrar el resultado
# ---------------------------------------------------------------------

def texto_produccion(no_terminal, produccion):
    derecha = " ".join(produccion) if produccion else EPSILON
    return f"{no_terminal} -> {derecha}"


def texto_conjunto(conjunto):
    return "{ " + ", ".join(sorted(conjunto)) + " }"


def texto_incumplimiento(incumplimiento):
    condicion, no_terminal, alfa, beta, comunes = incumplimiento
    return (
        f"Condición ({condicion}) en {no_terminal}: "
        f"{texto_produccion(no_terminal, alfa)}  /  "
        f"{texto_produccion(no_terminal, beta)}  "
        f"comparten {texto_conjunto(comunes)}"
    )


def texto_conflicto(conflicto):
    no_terminal, terminal, primera, segunda = conflicto
    return (
        f"Conflicto en M[{no_terminal}, {terminal}]: "
        f"{texto_produccion(no_terminal, primera)}  /  "
        f"{texto_produccion(no_terminal, segunda)}"
    )


def resumen(reporte):
    """Una línea con el resultado; es lo que imprimen mainEsp y pruebasEsp."""
    gramatica = reporte["gramatica"]
    producciones = sum(len(lista) for lista in gramatica.values())
    veredicto = "es LL(1)" if reporte["es_ll1"] else "NO es LL(1)"
    terminales = len(reporte["terminales"])
    celdas = len(reporte["tabla"])
    conflictos = len(reporte["conflictos"])

    return (
        f"Verificación LL(1): la gramática {veredicto} | "
        f"{len(gramatica)} no terminales, "
        f"{terminales} terminales, "
        f"{producciones} producciones, "
        f"{celdas} celdas en la tabla, "
        f"{conflictos} conflictos"
    )


def columnas_de_la_tabla(reporte):
    """Terminales en orden alfabético, con EOF al final (como el "$")."""
    terminales = sorted(reporte["terminales"] - {"EOF"})
    if "EOF" in reporte["terminales"]:
        terminales.append("EOF")
    return terminales


def reporte_completo(reporte):
    """Devuelve las líneas del reporte detallado."""
    gramatica = reporte["gramatica"]
    first = reporte["first"]
    follow = reporte["follow"]
    lineas = [resumen(reporte), ""]

    lineas.append("GRAMÁTICA")
    for no_terminal, producciones in gramatica.items():
        for produccion in producciones:
            lineas.append("  " + texto_produccion(no_terminal, produccion))

    lineas += ["", "FIRST"]
    for no_terminal in gramatica:
        lineas.append(
            f"  FIRST({no_terminal}) = {texto_conjunto(first[no_terminal])}"
        )

    lineas += ["", "FOLLOW"]
    for no_terminal in gramatica:
        lineas.append(
            f"  FOLLOW({no_terminal}) = {texto_conjunto(follow[no_terminal])}"
        )

    lineas += [
        "",
        "CONDICIONES LL(1)",
        "  Para cada no terminal con más de una producción se muestra el FIRST",
        "  de cada alternativa. Deben ser disjuntos (condición i) y, si una",
        "  alternativa puede derivar " + EPSILON + ", ninguna puede empezar con un",
        "  terminal de FOLLOW (condición ii).",
    ]
    for no_terminal, producciones in gramatica.items():
        if len(producciones) < 2:
            continue
        lineas.append(f"  {no_terminal}")
        hay_vacia = False
        for produccion in producciones:
            first_produccion = first_de_secuencia(produccion, first, gramatica)
            hay_vacia = hay_vacia or EPSILON in first_produccion
            lineas.append(
                f"    FIRST({' '.join(produccion) if produccion else EPSILON})"
                f" = {texto_conjunto(first_produccion)}"
            )
        if hay_vacia:
            lineas.append(
                f"    FOLLOW({no_terminal}) = {texto_conjunto(follow[no_terminal])}"
            )
    lineas.append("")
    if reporte["incumplimientos"]:
        for incumplimiento in reporte["incumplimientos"]:
            lineas.append("  " + texto_incumplimiento(incumplimiento))
    else:
        lineas.append("  Resultado: se cumplen las condiciones (i) y (ii) en todos los casos.")

    lineas += ["", "TABLA LL(1)  (las celdas que no aparecen son errores sintácticos)"]
    for no_terminal in gramatica:
        for terminal in columnas_de_la_tabla(reporte):
            produccion = reporte["tabla"].get((no_terminal, terminal))
            if produccion is not None:
                lineas.append(
                    f"  M[{no_terminal}, {terminal}] = "
                    f"{texto_produccion(no_terminal, produccion)}"
                )

    lineas += ["", "CONFLICTOS"]
    if reporte["conflictos"]:
        for conflicto in reporte["conflictos"]:
            lineas.append("  " + texto_conflicto(conflicto))
    else:
        lineas.append(
            "  Ninguno: ninguna celda tiene más de una producción, "
            "por lo tanto la gramática es LL(1)."
        )

    return lineas


def guardar_tabla_csv(reporte, ruta):
    """
    Guarda la tabla LL(1) como tabla de doble entrada: una fila por no
    terminal y una columna por terminal. Las celdas vacías son errores.
    """
    columnas = columnas_de_la_tabla(reporte)

    with open(ruta, "w", encoding="utf-8-sig", newline="") as archivo:
        escritor = csv.writer(archivo, delimiter=";")
        escritor.writerow(["No terminal"] + columnas)
        for no_terminal in reporte["gramatica"]:
            fila = [no_terminal]
            for terminal in columnas:
                produccion = reporte["tabla"].get((no_terminal, terminal))
                if produccion is None:
                    fila.append("")
                else:
                    fila.append(texto_produccion(no_terminal, produccion))
            escritor.writerow(fila)


def main():
    # La consola de Windows no siempre puede mostrar "ε" con su codificación
    # por defecto; con UTF-8 se evita un error al imprimir.
    sys.stdout.reconfigure(encoding="utf-8")

    reporte = analizar_gramatica(GRAMATICA)
    lineas = reporte_completo(reporte)
    print("\n".join(lineas))

    if len(sys.argv) > 1:
        with open(sys.argv[1], "w", encoding="utf-8", newline="\n") as salida:
            salida.write("\n".join(lineas) + "\n")
        print(f"\nReporte guardado en {sys.argv[1]}")

    if len(sys.argv) > 2:
        guardar_tabla_csv(reporte, sys.argv[2])
        print(f"Tabla guardada en {sys.argv[2]}")

    # Código de salida distinto de cero si la gramática no es LL(1).
    sys.exit(0 if reporte["es_ll1"] else 1)


if __name__ == "__main__":
    main()
