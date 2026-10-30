import unittest

from src.lexer import tokenizar
from src.parser import Parser


## assertEqual() comprueba que dos valores sean iguales.
## assertTrue() comprueba que un valor sea verdadero.
## assertRaises() comprueba que se produzca una excepción.

def analizar(codigo):
    tokens = tokenizar(codigo)
    parser = Parser(tokens)
    return parser.parsear()


def primera_instruccion(arbol):
    return arbol.hijos[0].hijos[0]


class TestEntradasValidas(unittest.TestCase):
    def test_declaracion_construye_arbol(self):
        arbol = analizar("int edad = 20;")

        self.assertEqual(arbol.nombre, "Programa")
        self.assertEqual(len(arbol.hijos), 1)

        declaracion = primera_instruccion(arbol)
        self.assertEqual(declaracion.nombre, "Declaracion")
        self.assertEqual(declaracion.hijos[:3], ["int", "edad", "="])
        self.assertEqual(declaracion.hijos[4], ";")

        expresion = declaracion.hijos[3]
        factor = expresion.hijos[0].hijos[0]
        self.assertEqual(factor.nombre, "Factor")
        self.assertEqual(factor.hijos, ["20"])

    def test_asignacion_construye_arbol(self):
        arbol = analizar("edad = 25;")

        asignacion = primera_instruccion(arbol)
        self.assertEqual(asignacion.nombre, "Asignacion")
        self.assertEqual(asignacion.hijos[0], "edad")
        self.assertEqual(asignacion.hijos[1], "=")
        self.assertEqual(asignacion.hijos[3], ";")

        expresion = asignacion.hijos[2]
        factor = expresion.hijos[0].hijos[0]
        self.assertEqual(factor.hijos, ["25"])

    def test_varias_sentencias(self):
        arbol = analizar("int x = 1; x = x + 1;")

        self.assertEqual(len(arbol.hijos), 2)
        self.assertEqual(arbol.hijos[0].hijos[0].nombre, "Declaracion")
        self.assertEqual(arbol.hijos[1].hijos[0].nombre, "Asignacion")

    def test_multiplicacion_tiene_prioridad(self):
        arbol = analizar("resultado = edad + 5 * 2;")
        expresion = primera_instruccion(arbol).hijos[2]

        self.assertEqual(expresion.hijos[1], "+")

        termino_derecho = expresion.hijos[2]
        self.assertEqual(termino_derecho.hijos[1], "*")
        self.assertEqual(termino_derecho.hijos[0].hijos, ["5"])
        self.assertEqual(termino_derecho.hijos[2].hijos, ["2"])

    def test_resta_y_division(self):
        arbol = analizar("resultado = 10 - 8 / 2;")
        expresion = primera_instruccion(arbol).hijos[2]

        self.assertEqual(expresion.hijos[1], "-")

        termino_derecho = expresion.hijos[2]
        self.assertEqual(termino_derecho.hijos[1], "/")

    def test_parentesis_cambian_agrupacion(self):
        arbol = analizar("resultado = (10 + 5) * 2;")
        expresion = primera_instruccion(arbol).hijos[2]
        termino = expresion.hijos[0]

        self.assertEqual(termino.hijos[1], "*")

        factor_parentesis = termino.hijos[0]
        self.assertEqual(factor_parentesis.hijos[0], "(")
        self.assertEqual(factor_parentesis.hijos[2], ")")

        expresion_interna = factor_parentesis.hijos[1]
        self.assertEqual(expresion_interna.hijos[1], "+")

    def test_espacios_y_saltos_de_linea(self):
        codigo = """
        int edad = 20;

        edad = edad + 1;
        """

        arbol = analizar(codigo)
        self.assertEqual(len(arbol.hijos), 2)


class TestEntradasInvalidas(unittest.TestCase):
    def test_sin_expresion(self):
        with self.assertRaises(SyntaxError):
            analizar("int edad = ;")

    def test_sin_punto_y_coma(self):
        with self.assertRaises(SyntaxError):
            analizar("int edad = 20")

    def test_sin_identificador(self):
        with self.assertRaises(SyntaxError):
            analizar("int = 20;")

    def test_parentesis_sin_cerrar(self):
        with self.assertRaises(SyntaxError):
            analizar("resultado = (10 + 5;")

    def test_operadores_consecutivos(self):
        with self.assertRaises(SyntaxError):
            analizar("resultado = 10 + * 2;")

    def test_sentencia_no_admitida(self):
        with self.assertRaises(SyntaxError):
            analizar("float resultado = 10;")

    def test_error_informa_linea_y_columna(self):
        codigo = "int x = 10;\nint y = ;"

        with self.assertRaises(SyntaxError) as contexto:
            analizar(codigo)

        mensaje = str(contexto.exception)
        self.assertIn("nea 2, columna 9", mensaje)


if __name__ == "__main__":
    unittest.main()
