"""
Pruebas de la verificación LL(1) (src/ll1.py).

Ejecutar desde la carpeta esp-parser:
  python -m unittest discover -s tests/test_esp -v
"""

import itertools
import sys
import unittest
from pathlib import Path

# Los módulos de src se importan por su nombre (lexer, parserEsp, ...),
# igual que cuando se ejecuta mainEsp.py desde esa carpeta.
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

import ll1  # noqa: E402
from gramatica import GRAMATICA  # noqa: E402
from lexer import Token  # noqa: E402
from lexerEsp import tokenizarEsp  # noqa: E402
from parserEsp import ParserEsp  # noqa: E402


def parser_acepta(tipos):
    """Ejecuta ParserEsp sobre una lista de tipos de token."""
    tokens = [Token(tipo, tipo, 1, i + 1) for i, tipo in enumerate(tipos)]
    try:
        ParserEsp(tokens).programa()
        return True
    except SyntaxError:
        return False


class TestGramaticaDelProyecto(unittest.TestCase):
    def setUp(self):
        self.reporte = ll1.analizar_gramatica(GRAMATICA)

    def test_la_gramatica_es_ll1(self):
        self.assertEqual(self.reporte["incumplimientos"], [])
        self.assertEqual(self.reporte["conflictos"], [])
        self.assertTrue(self.reporte["es_ll1"])

    def test_tamano_de_la_gramatica(self):
        self.assertEqual(len(GRAMATICA), 19)
        self.assertEqual(len(self.reporte["terminales"]), 24)
        self.assertEqual(sum(len(p) for p in GRAMATICA.values()), 43)
        self.assertEqual(len(self.reporte["tabla"]), 92)

    def test_first_y_follow_de_casos_conocidos(self):
        first = self.reporte["first"]
        follow = self.reporte["follow"]
        self.assertEqual(first["Sujeto_s"], {"DET_ms", "NP_ms", "DET_fs", "NP_fs", "PRON_s"})
        self.assertEqual(first["Complemento2"], {"PREP", "ADV", "ε"})
        self.assertEqual(follow["Sujeto_s"], {"V_s"})
        self.assertEqual(follow["Oracion"], {"EOF"})
        # parserEsp.py usa estos dos FOLLOW en preps() y adverbio().
        self.assertEqual(follow["Preps"], {"ADV", "EOF"})
        self.assertEqual(follow["Adverbio"], {"EOF"})

    def test_no_hay_recursion_por_la_izquierda(self):
        # Ninguna producción empieza con su propio no terminal.
        for no_terminal, producciones in GRAMATICA.items():
            for produccion in producciones:
                with self.subTest(no_terminal):
                    self.assertNotEqual(produccion[:1], [no_terminal])


class TestDeteccionDeGramaticasNoLL1(unittest.TestCase):
    """El verificador debe rechazar gramáticas que no son LL(1)."""

    def test_prefijo_comun_incumple_la_condicion_i(self):
        # s -> a b | a c : las dos producciones empiezan con "a".
        reporte = ll1.analizar_gramatica({"s": [["a", "b"], ["a", "c"]]})
        self.assertFalse(reporte["es_ll1"])
        self.assertEqual(reporte["incumplimientos"][0][:2], ("i", "s"))
        self.assertEqual(reporte["conflictos"][0][:2], ("s", "a"))

    def test_recursion_por_la_izquierda(self):
        # e -> e + n | n
        reporte = ll1.analizar_gramatica({"e": [["e", "+", "n"], ["n"]]})
        self.assertFalse(reporte["es_ll1"])

    def test_choque_con_follow_incumple_la_condicion_ii(self):
        # s -> x a ; x -> a | epsilon : con "a" no se sabe si x desaparece.
        reporte = ll1.analizar_gramatica({"s": [["x", "a"]], "x": [["a"], []]})
        self.assertFalse(reporte["es_ll1"])
        self.assertEqual(reporte["incumplimientos"][0][:2], ("ii", "x"))
        self.assertEqual(reporte["conflictos"][0][:2], ("x", "a"))

    def test_frase_preposicional_dentro_del_sintagma_nominal(self):
        # Si además se permitiera una frase preposicional dentro del SN
        # ("la niña de la mochila"), después del objeto una preposición
        # podría pertenecer al SN o al verbo: la gramática es ambigua y
        # deja de ser LL(1). Por eso la gramática del proyecto solo admite
        # frases preposicionales junto al verbo.
        gramatica = {
            "o": [["sn", "V", "sn", "preps", "EOF"]],
            "sn": [["DET", "N", "preps"]],
            "preps": [["PREP", "sn", "preps"], []],
        }
        reporte = ll1.analizar_gramatica(gramatica)
        self.assertFalse(reporte["es_ll1"])
        self.assertIn(("preps", "PREP"), [c[:2] for c in reporte["conflictos"]])

    def test_adverbio_antes_del_objeto(self):
        # Si además del adverbio final se permitiera uno justo después del
        # verbo ("escribe rápidamente el código"), en "duermen furiosamente"
        # no se sabría cuál de los dos es: la gramática deja de ser LL(1).
        # Por eso la gramática del proyecto solo admite el adverbio final.
        gramatica = {
            "sv": [["V", "adv_inicial", "complemento", "EOF"]],
            "adv_inicial": [["ADV"], []],
            "complemento": [["SN", "adv_final"], ["adv_final"]],
            "adv_final": [["ADV"], []],
        }
        reporte = ll1.analizar_gramatica(gramatica)
        self.assertFalse(reporte["es_ll1"])
        self.assertIn(("adv_inicial", "ADV"), [c[:2] for c in reporte["conflictos"]])

    def test_condiciones_y_tabla_dan_el_mismo_veredicto(self):
        gramaticas = [
            GRAMATICA,
            {"s": [["a", "b"], ["a", "c"]]},
            {"e": [["e", "+", "n"], ["n"]]},
            {"s": [["x", "a"]], "x": [["a"], []]},
            {"s": [["a", "s"], []]},
        ]
        for gramatica in gramaticas:
            reporte = ll1.analizar_gramatica(gramatica)
            self.assertEqual(
                bool(reporte["incumplimientos"]), bool(reporte["conflictos"])
            )


class TestParserUsaLaVerificacion(unittest.TestCase):
    def test_el_parser_se_detiene_si_la_gramatica_no_es_ll1(self):
        original = ll1.GRAMATICA
        ll1.GRAMATICA = {"s": [["a", "b"], ["a", "c"]]}
        ll1._REPORTE = None
        try:
            with self.assertRaises(ll1.GramaticaNoLL1):
                ParserEsp(tokenizarEsp("Marcela come los dulces."))
        finally:
            ll1.GRAMATICA = original
            ll1._REPORTE = None


class TestGramaticaCoincideConElParser(unittest.TestCase):
    """
    La verificación LL(1) se hace sobre gramatica.py. Estas pruebas comprueban
    que ParserEsp acepta y rechaza exactamente lo mismo que esa gramática.
    """

    def setUp(self):
        self.reporte = ll1.verificar_ll1()

    def test_cada_no_terminal_tiene_su_metodo_en_el_parser(self):
        for no_terminal in GRAMATICA:
            with self.subTest(no_terminal):
                self.assertTrue(callable(getattr(ParserEsp, no_terminal.lower(), None)))

    def test_todas_las_secuencias_de_hasta_tres_tokens(self):
        # Se agrega COMA: el lexer la produce y la gramática no la admite.
        terminales = sorted(self.reporte["terminales"] - {"EOF"}) + ["COMA"]
        diferencias = []
        for largo in range(4):
            for combinacion in itertools.product(terminales, repeat=largo):
                tipos = list(combinacion) + ["EOF"]
                if ll1.reconocer(tipos, self.reporte["tabla"]) != parser_acepta(tipos):
                    diferencias.append(tipos)
        self.assertEqual(diferencias, [])


if __name__ == "__main__":
    unittest.main()
