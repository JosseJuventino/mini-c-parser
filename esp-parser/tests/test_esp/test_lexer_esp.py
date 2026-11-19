"""
Pruebas del lexer del español (src/lexerEsp.py) y del léxico (src/lexico.py).

Ejecutar desde la carpeta esp-parser:
  python -m unittest discover -s tests/test_esp -v
"""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

import ll1  # noqa: E402
from gramatica import GRAMATICA  # noqa: E402
from lexerEsp import ErrorLexico, etiquetar, tiempo_verbal, tokenizarEsp  # noqa: E402
from lexico import LEXICO  # noqa: E402


def tipos(oracion):
    return [token.tipo for token in tokenizarEsp(oracion)]


def valores(oracion):
    return [token.valor for token in tokenizarEsp(oracion)]


class TestTokens(unittest.TestCase):
    def test_oracion_simple(self):
        self.assertEqual(
            tipos("Marcela come los dulces."),
            ["NP_fs", "V_s", "DET_mp", "N_mp", "EOF"],
        )

    def test_siempre_termina_en_eof(self):
        self.assertEqual(tipos(""), ["EOF"])
        self.assertEqual(tipos("Marcela")[-1], "EOF")

    def test_no_distingue_mayusculas(self):
        self.assertEqual(tipos("MARCELA COME"), tipos("marcela come"))

    def test_ignora_puntuacion_final(self):
        self.assertEqual(tipos("¿Marcela come?"), tipos("Marcela come"))

    def test_contracciones(self):
        # "al" = "a" + "el" y "del" = "de" + "el".
        self.assertEqual(valores("al")[:-1], ["a", "el"])
        self.assertEqual(tipos("al")[:-1], ["PREP", "DET_ms"])
        self.assertEqual(valores("del")[:-1], ["de", "el"])

    def test_columna_de_cada_token(self):
        columnas = [token.columna for token in tokenizarEsp("Ana come")]
        self.assertEqual(columnas, [1, 5, 9])


class TestErroresLexicos(unittest.TestCase):
    def test_palabra_desconocida(self):
        with self.assertRaises(ErrorLexico) as contexto:
            tokenizarEsp("Marcela corrió.")
        self.assertIn("corrió", str(contexto.exception))
        self.assertIn("columna 9", str(contexto.exception))

    def test_caracter_invalido(self):
        with self.assertRaises(ErrorLexico):
            tokenizarEsp("Marcela come 3 dulces.")

    def test_error_lexico_tambien_es_syntax_error(self):
        # El código que ya capturaba SyntaxError sigue funcionando.
        with self.assertRaises(SyntaxError):
            tokenizarEsp("Marcela corrió.")

    def test_la_coma_es_un_token_y_no_una_palabra_desconocida(self):
        self.assertEqual(tipos("Marcela come, hoy")[2], "COMA")


class TestLexico(unittest.TestCase):
    def test_nombres_y_pronombre_con_tilde(self):
        self.assertEqual(tipos("José")[0], "NP_ms")
        self.assertEqual(tipos("María")[0], "NP_fs")
        self.assertEqual(tipos("Tú")[0], "PRON_s")

    def test_tu_sin_tilde_no_es_pronombre(self):
        with self.assertRaises(ErrorLexico):
            tokenizarEsp("Tu come")

    def test_adjetivos_de_genero_comun(self):
        self.assertEqual(etiquetar("verde"), "Adj_cs")
        self.assertEqual(etiquetar("verdes"), "Adj_cp")

    def test_no_hay_claves_repetidas_en_el_archivo(self):
        # Un diccionario de Python conserva solo la última clave repetida,
        # así que una repetición borra una entrada sin avisar.
        import ast

        ruta = Path(__file__).resolve().parents[2] / "src" / "lexico.py"
        arbol = ast.parse(ruta.read_text(encoding="utf-8"))
        claves = [
            clave.value
            for nodo in ast.walk(arbol)
            if isinstance(nodo, ast.Dict)
            for clave in nodo.keys
        ]
        self.assertEqual(len(claves), len(set(claves)))

    def test_los_verbos_tienen_tiempo(self):
        tiempos = set()
        for palabra, entrada in LEXICO.items():
            if entrada[0] == "V":
                with self.subTest(palabra):
                    self.assertEqual(len(entrada), 4)
                    self.assertIn(
                        entrada[3],
                        {"presente", "pretérito", "presente o pretérito"},
                    )
                    tiempos.add(entrada[3])
        # El léxico cubre al menos dos tiempos verbales.
        self.assertIn("presente", tiempos)
        self.assertIn("pretérito", tiempos)

    def test_tiempo_verbal(self):
        self.assertEqual(tiempo_verbal("come"), "presente")
        self.assertEqual(tiempo_verbal("Comió"), "pretérito")
        self.assertEqual(tiempo_verbal("escribimos"), "presente o pretérito")
        self.assertIsNone(tiempo_verbal("mesa"))
        self.assertIsNone(tiempo_verbal("xyz"))


class TestLexicoCoincideConLaGramatica(unittest.TestCase):
    def setUp(self):
        self.terminales = ll1.analizar_gramatica(GRAMATICA)["terminales"]
        self.etiquetas = {etiquetar(palabra) for palabra in LEXICO}

    def test_toda_etiqueta_del_lexico_es_un_terminal(self):
        self.assertEqual(self.etiquetas - self.terminales, set())

    def test_todo_terminal_tiene_al_menos_una_palabra(self):
        # EOF lo agrega el lexer; no es una palabra.
        self.assertEqual(self.terminales - self.etiquetas, {"EOF"})


if __name__ == "__main__":
    unittest.main()
