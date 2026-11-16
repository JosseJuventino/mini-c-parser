"""
Comprueba que la documentación coincide con la gramática de gramatica.py:
el README y los archivos generados en docs/.

Si la gramática cambia, hay que volver a generar docs/ desde esp-parser/src:
  python ll1.py ../docs/ll1_reporte.txt ../docs/ll1_tabla.csv

Ejecutar desde la carpeta esp-parser:
  python -m unittest discover -s tests/test_esp -v
"""

import csv
import sys
import tempfile
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ / "src"))

import ll1  # noqa: E402
from gramatica import GRAMATICA  # noqa: E402
from lexico import LEXICO  # noqa: E402


def leer_csv(ruta):
    with open(ruta, encoding="utf-8-sig", newline="") as archivo:
        return list(csv.reader(archivo, delimiter=";"))


class TestArchivosGenerados(unittest.TestCase):
    def setUp(self):
        self.reporte = ll1.analizar_gramatica(GRAMATICA)

    def test_reporte_ll1_esta_actualizado(self):
        guardado = (RAIZ / "docs" / "ll1_reporte.txt").read_text(encoding="utf-8")
        self.assertEqual(
            guardado.splitlines(),
            ll1.reporte_completo(self.reporte),
        )

    def test_tabla_ll1_esta_actualizada(self):
        with tempfile.TemporaryDirectory() as carpeta:
            nueva = Path(carpeta) / "tabla.csv"
            ll1.guardar_tabla_csv(self.reporte, nueva)
            self.assertEqual(
                leer_csv(RAIZ / "docs" / "ll1_tabla.csv"),
                leer_csv(nueva),
            )

    def test_la_tabla_tiene_una_fila_por_no_terminal(self):
        filas = leer_csv(RAIZ / "docs" / "ll1_tabla.csv")
        self.assertEqual([fila[0] for fila in filas[1:]], list(GRAMATICA))
        # Una columna por terminal, más la columna del no terminal.
        self.assertEqual(len(filas[0]), len(self.reporte["terminales"]) + 1)
        ocupadas = sum(1 for fila in filas[1:] for celda in fila[1:] if celda)
        self.assertEqual(ocupadas, len(self.reporte["tabla"]))


class TestReadme(unittest.TestCase):
    def setUp(self):
        self.reporte = ll1.analizar_gramatica(GRAMATICA)
        self.lineas = (RAIZ / "README.md").read_text(encoding="utf-8").splitlines()
        # El mismo texto en una sola línea, para buscar frases aunque el
        # archivo las parta en dos renglones.
        self.texto = " ".join(" ".join(self.lineas).split())

    def test_contiene_todas_las_producciones(self):
        for no_terminal, producciones in GRAMATICA.items():
            for produccion in producciones:
                linea = ll1.texto_produccion(no_terminal, produccion)
                with self.subTest(linea):
                    self.assertIn(linea, self.lineas)

    def test_no_contiene_producciones_que_no_existen(self):
        esperadas = {
            ll1.texto_produccion(no_terminal, produccion)
            for no_terminal, producciones in GRAMATICA.items()
            for produccion in producciones
        }
        escritas = {
            linea
            for linea in self.lineas
            if " -> " in linea and linea.split(" -> ")[0] in GRAMATICA
        }
        self.assertEqual(escritas, esperadas)

    def test_las_cifras_coinciden(self):
        producciones = sum(len(lista) for lista in GRAMATICA.values())
        terminales = len(self.reporte["terminales"])
        celdas = len(self.reporte["tabla"])

        self.assertIn(f"No terminales ({len(GRAMATICA)})", self.texto)
        self.assertIn(f"Terminales ({terminales})", self.texto)
        self.assertIn(f"Producciones ({producciones})", self.texto)
        self.assertIn(
            f"{len(GRAMATICA)} no terminales, {terminales} terminales, "
            f"{producciones} producciones, {celdas} celdas ocupadas",
            self.texto,
        )
        self.assertIn(f"{len(LEXICO)} palabras", self.texto)

    def test_nombra_todos_los_simbolos(self):
        simbolos = set(GRAMATICA) | self.reporte["terminales"]
        for simbolo in simbolos:
            with self.subTest(simbolo):
                self.assertIn(f"`{simbolo}`", self.texto)


if __name__ == "__main__":
    unittest.main()
