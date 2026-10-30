import unittest

from src.lexer import tokenizar


class TestLexer(unittest.TestCase):
    def test_reconoce_declaracion(self):
        tokens = tokenizar("int edad = 20;")

        tipos = [token.tipo for token in tokens]
        valores = [token.valor for token in tokens]

        self.assertEqual(tipos, ["INT", "ID", "=", "NUMERO", ";", "EOF"])
        self.assertEqual(valores, ["int", "edad", "=", "20", ";", ""])

    def test_distingue_int_de_un_identificador(self):
        tokens = tokenizar("int entero = 1;")

        self.assertEqual(tokens[0].tipo, "INT")
        self.assertEqual(tokens[1].tipo, "ID")
        self.assertEqual(tokens[1].valor, "entero")

    def test_registra_linea_y_columna(self):
        tokens = tokenizar("int x = 1;\nx = 2;")
        segundo_x = tokens[5]

        self.assertEqual(segundo_x.valor, "x")
        self.assertEqual(segundo_x.linea, 2)
        self.assertEqual(segundo_x.columna, 1)

    def test_rechaza_caracter_invalido(self):
        with self.assertRaises(SyntaxError):
            tokenizar("int edad = @;")


if __name__ == "__main__":
    unittest.main()
