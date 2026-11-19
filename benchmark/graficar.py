import csv
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


BASE = Path(__file__).resolve().parent
CSV = BASE / "resultados" / "metricas_comparativas.csv"
SALIDA = BASE / "resultados" / "graficas"

METRICAS = [
    ("precision", "Precisión"),
    ("recall", "Recall"),
    ("rechazo_correcto", "Rechazo correcto"),
]

ORDEN = [
    "Parser propio",
    "NLTK",
    "spaCy",
    "Gemini zero-shot",
    "Gemini few-shot",
]
NIVELES = ["1", "2", "3"]


def cargar_datos():
    with CSV.open(encoding="utf-8-sig", newline="") as f:
        filas = list(csv.DictReader(f, delimiter=";"))

    if not filas:
        raise ValueError("No hay métricas para graficar.")

    datos = {}

    for fila in filas:
        clave = (
            fila["enfoque"],
            fila["criterio"],
            fila["nivel"],
        )
        datos[clave] = fila

    enfoques = [
        nombre for nombre in ORDEN
        if (nombre, "CFG", "general") in datos
    ]

    enfoques.extend(
        sorted({
            fila["enfoque"] for fila in filas
        } - set(enfoques))
    )

    return datos, enfoques


def valor(fila, columna):
    dato = fila[columna].strip()
    return float(dato) if dato else None


def anotar(ax, barra, numero, sufijo="%"):
    if numero is None:
        return

    ax.annotate(
        f"{numero:.1f}{sufijo}",
        (
            barra.get_x() + barra.get_width() / 2,
            barra.get_height()
        ),
        xytext=(0, 4),
        textcoords="offset points",
        ha="center",
        fontsize=8,
    )


def configurar(ax):
    ax.set_ylim(0, 115)
    ax.set_ylabel("Porcentaje (%)")
    ax.grid(axis="y", alpha=0.2)
    ax.set_axisbelow(True)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)


def guardar(fig, nombre):
    SALIDA.mkdir(parents=True, exist_ok=True)
    ruta = SALIDA / nombre

    fig.savefig(ruta, dpi=200, bbox_inches="tight")
    plt.close(fig)

    print(f"Generada: {ruta}")


# 1. Comparación global de ambos criterios
def grafica_general(datos, enfoques):
    fig, ejes = plt.subplots(
        1, 2, figsize=(17, 6.5), sharey=True
    )

    ancho = 0.8 / len(enfoques)

    for ax, criterio in zip(
        ejes, ["CFG", "ESPAÑOL"]
    ):
        for i, enfoque in enumerate(enfoques):
            fila = datos[
                (enfoque, criterio, "general")
            ]

            for j, (clave, _) in enumerate(METRICAS):
                x = j + (
                    i - (len(enfoques) - 1) / 2
                ) * ancho

                numero = valor(fila, clave)

                if numero is None:
                    continue

                barra = ax.bar(
                    x,
                    numero,
                    width=ancho * 0.9,
                    label=enfoque if j == 0 else None,
                    color=f"C{i}",
                )[0]

                anotar(ax, barra, numero)

        ax.set_xticks(
            range(len(METRICAS)),
            [nombre for _, nombre in METRICAS]
        )
        ax.set_title(f"Referencia: {criterio}")
        configurar(ax)

    fig.suptitle(
        "Rendimiento general de los analizadores",
        fontsize=15,
        fontweight="bold",
    )

    handles, labels = ejes[0].get_legend_handles_labels()

    fig.legend(
        handles,
        labels,
        loc="upper center",
        bbox_to_anchor=(0.5, 0.91),
        ncol=len(enfoques),
        frameon=False,
    )

    fig.text(
    0.5, 0.02,
        "Todos los enfoques evaluaron 76 oraciones. "
        "Las métricas utilizan dos referencias distintas: CFG y español.",
        ha="center",
        fontsize=9,
    )

    fig.tight_layout(rect=[0, 0.07, 1, 0.83])
    guardar(fig, "01_rendimiento_general.png")


# 2. Recall frente al español por nivel
def grafica_complejidad(datos, enfoques):
    fig, ax = plt.subplots(figsize=(10, 5.8))
    ancho = 0.8 / len(enfoques)

    for i, enfoque in enumerate(enfoques):
        fila_ejemplo = None

        for j, nivel in enumerate(NIVELES):
            fila = datos[
                (enfoque, "ESPAÑOL", nivel)
            ]

            numero = valor(fila, "recall")
            if numero is None:
                continue

            x = j + (
                i - (len(enfoques) - 1) / 2
            ) * ancho

            barra = ax.bar(
                x,
                numero,
                width=ancho * 0.9,
                label=enfoque if fila_ejemplo is None else None,
                color=f"C{i}",
            )[0]

            fila_ejemplo = fila
            anotar(ax, barra, numero)

    ax.set_xticks(
        range(3),
        ["Nivel 1 · Simple",
         "Nivel 2 · Intermedio",
         "Nivel 3 · Complejo"],
    )

    ax.set_title(
        "Recall según la complejidad del español",
        fontsize=14,
        fontweight="bold",
    )

    configurar(ax)
    ax.legend(frameon=False)

    fig.text(
        0.5, 0.02,
        "Recall = TP / (TP + FN). "
        "Todos los enfoques evaluaron las 76 oraciones.",
        ha="center",
        fontsize=9,
    )

    fig.tight_layout(rect=[0, 0.07, 1, 1])
    guardar(fig, "02_recall_complejidad.png")



def grafica_errores(datos, enfoques):
    fig, ax = plt.subplots(figsize=(12, 6))

    errores = [
        ("FP", "Falsos positivos"),
        ("FN", "Falsos negativos"),
    ]

    ancho = 0.8 / len(enfoques)
    maximo = 0

    for i, enfoque in enumerate(enfoques):
        fila = datos[
            (enfoque, "ESPAÑOL", "general")
        ]

        for j, (clave, _) in enumerate(errores):
            cantidad = int(fila[clave])
            maximo = max(maximo, cantidad)

            x = j + (
                i - (len(enfoques) - 1) / 2
            ) * ancho

            barra = ax.bar(
                x,
                cantidad,
                width=ancho * 0.9,
                label=enfoque if j == 0 else None,
                color=f"C{i}",
            )[0]

            ax.annotate(
                str(cantidad),
                (
                    barra.get_x() + barra.get_width() / 2,
                    barra.get_height()
                ),
                xytext=(0, 4),
                textcoords="offset points",
                ha="center",
                fontsize=9,
            )

    ax.set_xticks(
        range(len(errores)),
        [nombre for _, nombre in errores]
    )

    ax.set_ylim(0, maximo + 5)
    ax.set_ylabel("Número de oraciones")

    ax.set_title(
        "Errores de clasificación frente al español",
        fontsize=14,
        fontweight="bold",
    )

    ax.grid(axis="y", alpha=0.2)
    ax.set_axisbelow(True)

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    ax.legend(
        ncol=3,
        loc="upper center",
        bbox_to_anchor=(0.5, 1.02),
        frameon=False,
    )

    fig.text(
        0.5,
        0.02,
        "FP: acepta una oración incorrecta. "
        "FN: rechaza una oración correcta. "
        "Base: 76 oraciones.",
        ha="center",
        fontsize=9,
    )

    fig.tight_layout(rect=[0, 0.07, 1, 0.95])

    guardar(fig, "03_errores_espanol.png")


def main():
    datos, enfoques = cargar_datos()

    print(f"Enfoques encontrados: {len(enfoques)}")

    grafica_general(datos, enfoques)
    grafica_complejidad(datos, enfoques)
    grafica_errores(datos, enfoques)

    print("\nGráficas generadas correctamente.")



if __name__ == "__main__":
    main()
