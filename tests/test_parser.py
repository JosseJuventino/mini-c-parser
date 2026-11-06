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


def sentencias_del_bloque(bloque):
    # Un Bloque tiene la forma ["{", Sentencia, ..., Sentencia, "}"]
    return [sentencia.hijos[0] for sentencia in bloque.hijos[1:-1]]


class TestCondicionalesValidos(unittest.TestCase):
    def test_if_sin_else(self):
        codigo = """
        if (edad >= 18) {
            edad = edad + 1;
        }
        """
        arbol = analizar(codigo)

        self.assertEqual(len(arbol.hijos), 1)
        self.assertEqual(arbol.hijos[0].nombre, "Sentencia")

        condicional = primera_instruccion(arbol)
        self.assertEqual(condicional.nombre, "Condicional")
        self.assertEqual(len(condicional.hijos), 5)
        self.assertEqual(condicional.hijos[0], "if")
        self.assertEqual(condicional.hijos[1], "(")
        self.assertEqual(condicional.hijos[3], ")")

        condicion = condicional.hijos[2]
        self.assertEqual(condicion.nombre, "Condicion")
        self.assertEqual(len(condicion.hijos), 3)
        self.assertEqual(condicion.hijos[0].nombre, "Expresion")
        self.assertEqual(condicion.hijos[0].hijos[0].hijos[0].hijos, ["edad"])
        self.assertEqual(condicion.hijos[1], ">=")
        self.assertEqual(condicion.hijos[2].nombre, "Expresion")
        self.assertEqual(condicion.hijos[2].hijos[0].hijos[0].hijos, ["18"])

        bloque = condicional.hijos[4]
        self.assertEqual(bloque.nombre, "Bloque")
        self.assertEqual(bloque.hijos[0], "{")
        self.assertEqual(bloque.hijos[-1], "}")

        instrucciones = sentencias_del_bloque(bloque)
        self.assertEqual(len(instrucciones), 1)
        self.assertEqual(instrucciones[0].nombre, "Asignacion")
        self.assertEqual(instrucciones[0].hijos[0], "edad")
        self.assertEqual(instrucciones[0].hijos[2].hijos[1], "+")

    def test_if_else_con_declaracion_previa(self):
        codigo = """
        int edad = 20;

        if (edad >= 18) {
            int resultado = edad * 2;
        } else {
            resultado = 0;
        }
        """
        arbol = analizar(codigo)

        self.assertEqual(len(arbol.hijos), 2)
        self.assertEqual(arbol.hijos[0].hijos[0].nombre, "Declaracion")

        condicional = arbol.hijos[1].hijos[0]
        self.assertEqual(condicional.nombre, "Condicional")
        self.assertEqual(len(condicional.hijos), 7)
        self.assertEqual(condicional.hijos[5], "else")

        bloque_if = condicional.hijos[4]
        bloque_else = condicional.hijos[6]
        self.assertEqual(bloque_if.nombre, "Bloque")
        self.assertEqual(bloque_else.nombre, "Bloque")

        instrucciones_if = sentencias_del_bloque(bloque_if)
        self.assertEqual(len(instrucciones_if), 1)
        declaracion = instrucciones_if[0]
        self.assertEqual(declaracion.nombre, "Declaracion")
        self.assertEqual(declaracion.hijos[1], "resultado")
        self.assertEqual(declaracion.hijos[3].hijos[0].hijos[1], "*")

        instrucciones_else = sentencias_del_bloque(bloque_else)
        self.assertEqual(len(instrucciones_else), 1)
        asignacion = instrucciones_else[0]
        self.assertEqual(asignacion.nombre, "Asignacion")
        self.assertEqual(asignacion.hijos[0], "resultado")
        self.assertEqual(asignacion.hijos[2].hijos[0].hijos[0].hijos, ["0"])

    def test_condicionales_anidados_con_expresion_en_condicion(self):
        codigo = """
        if ((edad + 2) >= 18) {
            if (edad == 20) {
                edad = 21;
            }
        }
        """
        arbol = analizar(codigo)

        externo = primera_instruccion(arbol)
        self.assertEqual(externo.nombre, "Condicional")

        # La parte izquierda es una expresión entre paréntesis: (edad + 2)
        condicion_externa = externo.hijos[2]
        self.assertEqual(condicion_externa.hijos[1], ">=")
        factor_parentesis = condicion_externa.hijos[0].hijos[0].hijos[0]
        self.assertEqual(factor_parentesis.hijos[0], "(")
        self.assertEqual(factor_parentesis.hijos[1].hijos[1], "+")
        self.assertEqual(factor_parentesis.hijos[2], ")")

        instrucciones = sentencias_del_bloque(externo.hijos[4])
        self.assertEqual(len(instrucciones), 1)

        interno = instrucciones[0]
        self.assertEqual(interno.nombre, "Condicional")
        self.assertEqual(len(interno.hijos), 5)
        self.assertEqual(interno.hijos[2].hijos[1], "==")

        instrucciones_internas = sentencias_del_bloque(interno.hijos[4])
        self.assertEqual(instrucciones_internas[0].nombre, "Asignacion")
        self.assertEqual(
            instrucciones_internas[0].hijos[2].hijos[0].hijos[0].hijos,
            ["21"],
        )

    def test_bloque_vacio(self):
        arbol = analizar("if (x != 0) {\n}")

        condicional = primera_instruccion(arbol)
        self.assertEqual(condicional.hijos[2].hijos[1], "!=")

        bloque = condicional.hijos[4]
        self.assertEqual(bloque.nombre, "Bloque")
        self.assertEqual(bloque.hijos, ["{", "}"])

    def test_bloque_con_varias_instrucciones(self):
        codigo = """
        if (a < b) {
            int c = 1;
            c = c + a;
            b = c * 2;
        }
        """
        bloque = primera_instruccion(analizar(codigo)).hijos[4]
        instrucciones = sentencias_del_bloque(bloque)

        self.assertEqual(
            [instruccion.nombre for instruccion in instrucciones],
            ["Declaracion", "Asignacion", "Asignacion"],
        )

    def test_todos_los_operadores_de_comparacion(self):
        for operador in ("==", "!=", "<", ">", "<=", ">="):
            with self.subTest(operador=operador):
                arbol = analizar(f"if (a {operador} b) {{ }}")
                condicion = primera_instruccion(arbol).hijos[2]
                self.assertEqual(condicion.hijos[1], operador)

    def test_expresiones_aritmeticas_a_ambos_lados(self):
        arbol = analizar("if (a + b * 2 <= c - 1) { }")
        condicion = primera_instruccion(arbol).hijos[2]

        izquierda = condicion.hijos[0]
        derecha = condicion.hijos[2]

        # La comparación queda arriba; la aritmética mantiene su precedencia
        self.assertEqual(condicion.hijos[1], "<=")
        self.assertEqual(izquierda.hijos[1], "+")
        self.assertEqual(izquierda.hijos[2].hijos[1], "*")
        self.assertEqual(derecha.hijos[1], "-")

    def test_identificador_que_empieza_con_if(self):
        arbol = analizar("ifVariable = 1;")

        asignacion = primera_instruccion(arbol)
        self.assertEqual(asignacion.nombre, "Asignacion")
        self.assertEqual(asignacion.hijos[0], "ifVariable")

    def test_sentencias_despues_del_condicional(self):
        arbol = analizar("if (x > 0) { x = 1; } x = 2;")

        self.assertEqual(len(arbol.hijos), 2)
        self.assertEqual(arbol.hijos[0].hijos[0].nombre, "Condicional")
        self.assertEqual(arbol.hijos[1].hijos[0].nombre, "Asignacion")


class TestCondicionalesInvalidos(unittest.TestCase):
    def mensaje_de_error(self, codigo):
        with self.assertRaises(SyntaxError) as contexto:
            analizar(codigo)

        return str(contexto.exception)

    def test_falta_expresion_derecha_en_condicion(self):
        mensaje = self.mensaje_de_error(
            "if (edad >=) {\n"
            "    edad = 20;\n"
            "}"
        )

        self.assertIn("nea 1, columna 12", mensaje)
        self.assertIn("se esperaba un número, identificador o '('", mensaje)

    def test_falta_llave_de_cierre(self):
        mensaje = self.mensaje_de_error(
            "if (edad >= 18) {\n"
            "    edad = 20;"
        )

        self.assertIn("se esperaba '}'", mensaje)
        self.assertIn("línea 1, columna 17", mensaje)
        self.assertIn("fin del código", mensaje)

    def test_falta_parentesis_en_condicion(self):
        mensaje = self.mensaje_de_error(
            "if edad >= 18 {\n"
            "    edad = 20;\n"
            "}"
        )

        self.assertIn("nea 1, columna 4", mensaje)
        self.assertIn("se esperaba '('", mensaje)

    def test_else_sin_if(self):
        mensaje = self.mensaje_de_error(
            "else {\n"
            "    edad = 20;\n"
            "}"
        )

        self.assertIn("nea 1, columna 1", mensaje)
        self.assertIn("'else' sin un 'if'", mensaje)

    def test_asignacion_incompleta_dentro_del_bloque(self):
        mensaje = self.mensaje_de_error(
            "if (edad >= 18) {\n"
            "    edad = ;\n"
            "}"
        )

        self.assertIn("nea 2, columna 12", mensaje)

    def test_falta_operador_de_comparacion(self):
        mensaje = self.mensaje_de_error("if (edad) {\n}")

        self.assertIn("operador de comparación", mensaje)
        self.assertIn("se encontró ')'", mensaje)

    def test_falta_parentesis_de_cierre(self):
        mensaje = self.mensaje_de_error("if (edad > 1 {\n}")

        self.assertIn("se esperaba ')'", mensaje)
        self.assertIn("se encontró '{'", mensaje)

    def test_falta_punto_y_coma_dentro_del_bloque(self):
        mensaje = self.mensaje_de_error(
            "if (edad > 1) {\n"
            "    edad = 2\n"
            "}"
        )

        self.assertIn("nea 3, columna 1", mensaje)
        self.assertIn("se esperaba ';'", mensaje)

    def test_if_sin_llaves(self):
        mensaje = self.mensaje_de_error("if (edad > 1) edad = 2;")

        self.assertIn("se esperaba '{'", mensaje)

    def test_else_sin_llaves(self):
        mensaje = self.mensaje_de_error("if (x > 1) { } else x = 2;")

        self.assertIn("se esperaba '{'", mensaje)

    def test_else_if_no_admitido(self):
        with self.assertRaises(SyntaxError):
            analizar("if (x > 1) { } else if (x > 0) { }")

    def test_condicion_vacia(self):
        with self.assertRaises(SyntaxError):
            analizar("if () { }")


if __name__ == "__main__":
    unittest.main()
