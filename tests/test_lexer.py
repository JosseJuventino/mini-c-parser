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


class TestLexerCondicionales(unittest.TestCase):
    def test_reconoce_if_y_else(self):
        tokens = tokenizar("if else")

        tipos = [token.tipo for token in tokens]
        self.assertEqual(tipos, ["IF", "ELSE", "EOF"])

    def test_palabras_que_empiezan_con_if_o_else_son_identificadores(self):
        tokens = tokenizar("ifVariable elsewhere iff")

        tipos = [token.tipo for token in tokens]
        valores = [token.valor for token in tokens]

        self.assertEqual(tipos, ["ID", "ID", "ID", "EOF"])
        self.assertEqual(valores, ["ifVariable", "elsewhere", "iff", ""])

    def test_reconoce_llaves(self):
        tokens = tokenizar("{ }")

        tipos = [token.tipo for token in tokens]
        self.assertEqual(tipos, ["{", "}", "EOF"])

    def test_operadores_de_dos_caracteres_son_un_solo_token(self):
        for operador in ("==", "!=", "<=", ">="):
            with self.subTest(operador=operador):
                tokens = tokenizar(f"a {operador} b")

                tipos = [token.tipo for token in tokens]
                valores = [token.valor for token in tokens]

                self.assertEqual(tipos, ["ID", operador, "ID", "EOF"])
                self.assertEqual(valores, ["a", operador, "b", ""])

    def test_operadores_de_dos_caracteres_sin_espacios(self):
        tokens = tokenizar("a==b")

        tipos = [token.tipo for token in tokens]
        self.assertEqual(tipos, ["ID", "==", "ID", "EOF"])

    def test_menor_y_mayor_simples(self):
        tokens = tokenizar("a < b > c")

        tipos = [token.tipo for token in tokens]
        self.assertEqual(tipos, ["ID", "<", "ID", ">", "ID", "EOF"])

    def test_asignacion_sigue_siendo_un_igual(self):
        tokens = tokenizar("x = 1;")

        self.assertEqual(tokens[1].tipo, "=")

    def test_condicional_completo(self):
        tokens = tokenizar("if (edad >= 18) { edad = 0; } else { }")

        tipos = [token.tipo for token in tokens]
        self.assertEqual(tipos, [
            "IF", "(", "ID", ">=", "NUMERO", ")",
            "{", "ID", "=", "NUMERO", ";", "}",
            "ELSE", "{", "}", "EOF",
        ])

    def test_linea_y_columna_en_condicional(self):
        tokens = tokenizar("if (x)\n{\n  x = 1;\n}")
        llave = tokens[4]
        operador = tokens[6]

        self.assertEqual(llave.tipo, "{")
        self.assertEqual((llave.linea, llave.columna), (2, 1))
        self.assertEqual(operador.tipo, "=")
        self.assertEqual((operador.linea, operador.columna), (3, 5))

    def test_exclamacion_sola_es_invalida(self):
        with self.assertRaises(SyntaxError):
            tokenizar("if (!x) { }")


if __name__ == "__main__":
    unittest.main()
