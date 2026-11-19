"""
Pruebas del parser del español (src/parserEsp.py y src/analizadorEsp.py).

Ejecutar desde la carpeta esp-parser:
  python -m unittest discover -s tests/test_esp -v
"""

import csv
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

import ll1  # noqa: E402
from analizadorEsp import (  # noqa: E402
    ACEPTA,
    ERROR_LEXICO,
    RECHAZO_SINTACTICO,
    analizar,
)
from gramatica import EPSILON, GRAMATICA, INICIAL  # noqa: E402
from lexerEsp import tokenizarEsp  # noqa: E402
from parser import Nodo  # noqa: E402

# Corpus de la Fase 2: id, oración y salida esperada de la gramática.
RUTA_CORPUS = Path(__file__).resolve().parents[3] / "benchmark" / "corpus_fase2.csv"


def leer_corpus():
    with open(RUTA_CORPUS, encoding="utf-8-sig", newline="") as archivo:
        return list(csv.DictReader(archivo, delimiter=";"))


def palabras_del_arbol(nodo):
    """Hojas del árbol de izquierda a derecha, sin las producciones vacías."""
    if not isinstance(nodo, Nodo):
        return [] if nodo == EPSILON else [nodo]
    palabras = []
    for hijo in nodo.hijos:
        palabras += palabras_del_arbol(hijo)
    return palabras


class TestCorpus(unittest.TestCase):
    def setUp(self):
        self.corpus = leer_corpus()
        self.tabla = ll1.verificar_ll1()["tabla"]

    def test_tamano_y_niveles_del_corpus(self):
        self.assertEqual(len(self.corpus), 76)
        por_nivel = [fila["nivel"] for fila in self.corpus]
        self.assertEqual(por_nivel.count("1"), 20)
        self.assertEqual(por_nivel.count("2"), 28)
        self.assertEqual(por_nivel.count("3"), 28)
        # Los identificadores no se repiten.
        self.assertEqual(len({fila["id"] for fila in self.corpus}), 76)

    def test_etiquetas_del_corpus(self):
        # Cada oración tiene las dos etiquetas con valores válidos.
        for fila in self.corpus:
            with self.subTest(fila["id"]):
                self.assertIn(fila["salida_cfg"], {"acepta", "rechaza"})
                self.assertIn(fila["gramatical"], {"si", "no"})
        incorrectas = [fila for fila in self.corpus if fila["gramatical"] == "no"]
        self.assertEqual(len(incorrectas), 23)

    def test_salida_esperada_de_cada_oracion(self):
        for fila in self.corpus:
            resultado = analizar(fila["oracion"])
            with self.subTest(fila["id"]):
                # Todas las palabras del corpus están en el léxico, así que
                # ningún rechazo del corpus es un error léxico.
                self.assertNotEqual(resultado["estado"], ERROR_LEXICO)
                esperado = ACEPTA if fila["salida_cfg"] == "acepta" else RECHAZO_SINTACTICO
                self.assertEqual(resultado["estado"], esperado)

    def test_la_tabla_ll1_da_la_misma_salida(self):
        for fila in self.corpus:
            tipos = [token.tipo for token in tokenizarEsp(fila["oracion"])]
            with self.subTest(fila["id"]):
                self.assertEqual(
                    ll1.reconocer(tipos, self.tabla),
                    fila["salida_cfg"] == "acepta",
                )


class TestArbolDeDerivacion(unittest.TestCase):
    def setUp(self):
        self.terminales = ll1.verificar_ll1()["terminales"]

    def comprobar_nodo(self, nodo):
        """Cada nodo con sus hijos debe ser una producción de la gramática."""
        if nodo.nombre in GRAMATICA:
            if nodo.hijos == [EPSILON]:
                derecha = []
            else:
                derecha = [hijo.nombre for hijo in nodo.hijos]
            if nodo.nombre == INICIAL:
                # El token EOF se consume pero no se agrega al árbol.
                derecha = derecha + ["EOF"]
            self.assertIn(derecha, GRAMATICA[nodo.nombre])
            for hijo in nodo.hijos:
                if isinstance(hijo, Nodo):
                    self.comprobar_nodo(hijo)
        else:
            # Hoja: el nombre es un terminal y el único hijo es la palabra.
            self.assertIn(nodo.nombre, self.terminales)
            self.assertEqual(len(nodo.hijos), 1)
            self.assertIsInstance(nodo.hijos[0], str)

    def test_los_arboles_del_corpus_siguen_la_gramatica(self):
        aceptadas = 0
        for fila in leer_corpus():
            resultado = analizar(fila["oracion"])
            if resultado["estado"] != ACEPTA:
                continue
            aceptadas += 1
            with self.subTest(fila["id"]):
                self.comprobar_nodo(resultado["arbol"])
                # Las hojas, en orden, son las palabras de la oración.
                tokens = tokenizarEsp(fila["oracion"])
                self.assertEqual(
                    palabras_del_arbol(resultado["arbol"]),
                    [token.valor for token in tokens[:-1]],
                )
        self.assertEqual(aceptadas, 45)

    def test_arbol_de_una_oracion_simple(self):
        arbol = analizar("El niño come.")["arbol"]
        self.assertEqual(
            arbol,
            Nodo("Programa", [
                Nodo("Oracion", [
                    Nodo("Sujeto_s", [
                        Nodo("SN_ms", [
                            Nodo("DET_ms", ["el"]),
                            Nodo("N_ms", ["niño"]),
                            Nodo("Adjs_ms", [EPSILON]),
                        ]),
                    ]),
                    Nodo("SV_s", [
                        Nodo("V_s", ["come"]),
                        Nodo("Complemento", [
                            Nodo("Complemento2", [
                                Nodo("Preps", [EPSILON]),
                                Nodo("Adverbio", [EPSILON]),
                            ]),
                        ]),
                    ]),
                ]),
            ]),
        )

    def test_los_adjetivos_se_anidan_por_la_derecha(self):
        arbol = analizar("El niño pequeño nuevo come.")["arbol"]
        sn = arbol.hijos[0].hijos[0].hijos[0]
        self.assertEqual(
            sn.hijos[2],
            Nodo("Adjs_ms", [
                Nodo("Adj_ms", ["pequeño"]),
                Nodo("Adjs_ms", [
                    Nodo("Adj_ms", ["nuevo"]),
                    Nodo("Adjs_ms", [EPSILON]),
                ]),
            ]),
        )


class TestTresResultados(unittest.TestCase):
    def test_acepta(self):
        resultado = analizar("Marcela come los dulces.")
        self.assertEqual(resultado["estado"], ACEPTA)
        self.assertEqual(resultado["mensaje"], "")
        self.assertIsInstance(resultado["arbol"], Nodo)

    def test_rechazo_sintactico(self):
        resultado = analizar("Los esqueletos escribe el código.")
        self.assertEqual(resultado["estado"], RECHAZO_SINTACTICO)
        self.assertIn("se esperaba un verbo plural", resultado["mensaje"])
        self.assertIn("escribe", resultado["mensaje"])
        self.assertIsNone(resultado["arbol"])

    def test_error_lexico(self):
        resultado = analizar("Marcela corrió.")
        self.assertEqual(resultado["estado"], ERROR_LEXICO)
        self.assertIn("corrió", resultado["mensaje"])
        self.assertIsNone(resultado["arbol"])

    def test_la_coma_es_un_rechazo_sintactico(self):
        resultado = analizar("Marcela come, los dulces.")
        self.assertEqual(resultado["estado"], RECHAZO_SINTACTICO)
        self.assertIn("','", resultado["mensaje"])

    def test_oracion_incompleta_menciona_el_fin_de_la_oracion(self):
        for oracion in ["", "Marcela.", "Ana dijo que.", "El niño come la."]:
            resultado = analizar(oracion)
            with self.subTest(oracion):
                self.assertEqual(resultado["estado"], RECHAZO_SINTACTICO)
                self.assertIn("fin de la oración", resultado["mensaje"])

    def test_tiempo_de_los_verbos(self):
        self.assertEqual(
            analizar("Marcela comió los dulces.")["verbos"],
            [("comió", "pretérito")],
        )
        self.assertEqual(
            analizar("Ana dijo que Diego escribe el código.")["verbos"],
            [("dijo", "pretérito"), ("escribe", "presente")],
        )


class TestConcordancia(unittest.TestCase):
    def acepta(self, oracion):
        return analizar(oracion)["estado"] == ACEPTA

    def test_genero_y_numero_en_el_sintagma_nominal(self):
        self.assertTrue(self.acepta("La niña pequeña come."))
        self.assertFalse(self.acepta("La niña pequeño come."))
        self.assertFalse(self.acepta("La niña pequeñas come."))
        self.assertFalse(self.acepta("El niña come."))
        self.assertFalse(self.acepta("Los niño comen."))

    def test_numero_entre_sujeto_y_verbo(self):
        self.assertTrue(self.acepta("Los niños comen."))
        self.assertFalse(self.acepta("Los niños come."))
        self.assertFalse(self.acepta("El niño comen."))
        self.assertFalse(self.acepta("Ellos come."))

    def test_adjetivo_de_genero_comun(self):
        # "verde" sirve para masculino y femenino, pero no cambia de número.
        self.assertTrue(self.acepta("La mesa verde duerme."))
        self.assertTrue(self.acepta("El libro verde duerme."))
        self.assertTrue(self.acepta("Las mesas verdes duermen."))
        self.assertTrue(self.acepta("Los libros verdes duermen."))
        self.assertFalse(self.acepta("Las mesas verde duermen."))
        self.assertFalse(self.acepta("El libro verdes duerme."))

    def test_plural_sin_determinante(self):
        self.assertTrue(self.acepta("Niños comen dulces."))
        self.assertFalse(self.acepta("Niño come."))


class TestLimitesDocumentados(unittest.TestCase):
    """
    Comportamientos que son límites conocidos de la gramática (ver README).
    Están aquí para que un cambio en la gramática que los altere no pase
    inadvertido, porque cambiaría las etiquetas del corpus.
    """

    def acepta(self, oracion):
        return analizar(oracion)["estado"] == ACEPTA

    def test_no_se_comprueba_la_persona(self):
        # Solo se comprueba el número. Es el caso C20 del corpus.
        self.assertTrue(self.acepta("Yo come el libro."))
        self.assertTrue(self.acepta("Jaime dijo que nosotros corrigen los exámenes en la clase."))

    def test_cualquier_verbo_admite_una_subordinada_con_que(self):
        self.assertTrue(self.acepta("Ana come que Diego duerme."))

    def test_no_hay_frase_preposicional_dentro_del_sintagma_nominal(self):
        self.assertFalse(self.acepta("La niña de la mochila blanca compró unas cartas."))

    def test_un_solo_adverbio_y_al_final(self):
        self.assertTrue(self.acepta("Ana guardó las manzanas en la caja ayer."))
        self.assertFalse(self.acepta("Ana guardó las manzanas en la caja cuidadosamente ayer."))
        self.assertFalse(self.acepta("El esqueleto escribe rápidamente el código."))

    def test_el_sujeto_es_obligatorio_y_va_antes_del_verbo(self):
        self.assertFalse(self.acepta("Escribimos el parser."))
        self.assertFalse(self.acepta("Come Marcela los dulces."))

    def test_no_hay_oraciones_de_relativo(self):
        self.assertFalse(self.acepta("El profesor que explica la gramática corrige los exámenes."))

    def test_la_ambiguedad_estructural_produce_un_solo_arbol(self):
        # "con el telescopio" puede modificar a "vio" o a "fantasma". La
        # gramática solo permite la primera lectura: la frase cuelga del verbo.
        arbol = analizar("Marcela vio al fantasma con el telescopio.")["arbol"]
        # Programa -> Oracion -> SV_s -> Complemento -> Complemento2
        complemento = arbol.hijos[0].hijos[1].hijos[1]
        self.assertEqual(complemento.nombre, "Complemento")
        complemento2 = complemento.hijos[0]
        self.assertEqual(complemento2.nombre, "Complemento2")
        preps = complemento2.hijos[0]
        self.assertEqual(
            [preps.hijos[0], preps.hijos[2].hijos[0]],
            [Nodo("PREP", ["a"]), Nodo("PREP", ["con"])],
        )


if __name__ == "__main__":
    unittest.main()
