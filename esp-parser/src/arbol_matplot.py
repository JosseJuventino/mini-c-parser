
from pathlib import Path

from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.figure import Figure

from parser import Nodo


def exportar_arbol(
    arbol: Nodo, archivo: str | Path = "arbol.svg"
) -> Path:
    destino = Path(archivo)
    if destino.suffix.lower() not in {".svg", ".png"}:
        raise ValueError("Usa la extensión .svg o .png para el árbol.")

    etiquetas: list[tuple[float, int, str, bool]] = []
    ramas: list[tuple[float, int, float, int]] = []
    siguiente_hoja = 0

    def ubicar(nodo: Nodo | str, nivel: int) -> float:
        nonlocal siguiente_hoja

        es_nodo = isinstance(nodo, Nodo)
        hijos = (
            [hijo for hijo in nodo.hijos if not isinstance(hijo, Nodo) or hijo.hijos]
            if es_nodo else []
        )
        if hijos:
            posiciones = [ubicar(hijo, nivel + 1) for hijo in hijos]
            x = (posiciones[0] + posiciones[-1]) / 2
            ramas.extend((x, nivel, hijo_x, nivel + 1) for hijo_x in posiciones)
        else:
            x = siguiente_hoja
            siguiente_hoja += 1

        texto = nodo.nombre if es_nodo else str(nodo)
        etiquetas.append((x, nivel, texto, es_nodo))
        return x

    ubicar(arbol, 0)
    profundidad = max(nivel for _, nivel, _, _ in etiquetas)
    etiqueta_mas_larga = max(len(texto) for _, _, texto, _ in etiquetas)
    espacio_horizontal = max(1.0, 0.15 * etiqueta_mas_larga + 0.25)
    figura = Figure(
        figsize=(max(4, siguiente_hoja * espacio_horizontal), max(2, (profundidad + 1) * 0.62)),
        facecolor="white",
    )
    FigureCanvasAgg(figura)
    eje = figura.add_axes([0.02, 0.03, 0.96, 0.94])
    eje.set_xlim(-0.6, siguiente_hoja - 0.4)
    eje.set_ylim(profundidad + 0.5, -0.5)
    eje.set_axis_off()

    for padre_x, padre_y, hijo_x, hijo_y in ramas:
        eje.plot([padre_x, hijo_x], [padre_y, hijo_y], color="#63758A", linewidth=1.2)

    for x, nivel, texto, es_nodo in etiquetas:
        eje.text(
            x, nivel, texto,
            ha="center", va="center", color="#142C42", fontsize=10,
            fontweight="bold" if es_nodo else "normal",
            parse_math=False,
            bbox={
                "boxstyle": "round,pad=0.3",
                "facecolor": "#E1EFFA" if es_nodo else "#F5F7FA",
                "edgecolor": "#8AA6BD" if es_nodo else "#BAC5D0",
            },
        )

    destino.parent.mkdir(parents=True, exist_ok=True)
    figura.savefig(destino, dpi=180)
    return destino
