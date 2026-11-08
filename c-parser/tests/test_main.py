import io
import os
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

from src.main import (
    CARPETA_EJEMPLOS,
    RAIZ_PROYECTO,
    analizar,
    ejecutar_demo,
    leer_archivo,
    main,
)
from src.parser import Nodo


VALIDOS = sorted((CARPETA_EJEMPLOS / "validos").glob("*.cpp"))
INVALIDOS = sorted((CARPETA_EJEMPLOS / "invalidos").glob("*.cpp"))

ERRORES_ESPERADOS = {
    "sin_expresion.cpp": (
        "Error sintáctico: Línea 1, columna 12",
        "se esperaba un número, identificador o '('",
    ),
    "sin_punto_coma.cpp": (
        "Error sintáctico: Línea 2, columna 1",
        "se esperaba ';'",
    ),
    "sin_identificador.cpp": (
        "Error sintáctico: Línea 1, columna 5",
        "se esperaba 'ID'",
    ),
    "parentesis_sin_cerrar.cpp": (
        "Error sintáctico: Línea 2, columna 30",
        "se esperaba ')'",
    ),
    "condicion_incompleta.cpp": (
        "Error sintáctico: Línea 3, columna 12",
        "pero se encontró ')'",
    ),
    "bloque_sin_cerrar.cpp": (
        "Error sintáctico: Línea 5, columna 1",
        "bloque abierto en la línea 3, columna 17",
    ),
    "else_sin_if.cpp": (
        "Error sintáctico: Línea 7, columna 1",
        "'else' sin un 'if' antes",
    ),
    "caracter_invalido.cpp": (
        "Error léxico: Carácter inválido '@'",
        "línea 2, columna 18",
    ),
}


def ejecutar_cli(*argumentos, cwd=RAIZ_PROYECTO):
    entorno = dict(os.environ)
    entorno["PYTHONIOENCODING"] = "utf-8"
    entorno["PYTHONPATH"] = str(RAIZ_PROYECTO)

    return subprocess.run(
        [sys.executable, "-m", "src.main", *argumentos],
        cwd=cwd,
        env=entorno,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )


def buscar_nodos(nodo, nombre):
    encontrados = []

    if isinstance(nodo, Nodo):
        if nodo.nombre == nombre:
            encontrados.append(nodo)

        for hijo in nodo.hijos:
            encontrados.extend(buscar_nodos(hijo, nombre))

    return encontrados


class TestLecturaDeArchivos(unittest.TestCase):
    def test_lee_archivo_cpp_en_utf8(self):
        with tempfile.TemporaryDirectory() as carpeta:
            ruta = Path(carpeta) / "prueba.cpp"
            ruta.write_text("int año = 2026;\n", encoding="utf-8")

            self.assertEqual(leer_archivo(ruta), "int año = 2026;\n")

    def test_ignora_marca_bom_de_utf8(self):
        with tempfile.TemporaryDirectory() as carpeta:
            ruta = Path(carpeta) / "con_bom.cpp"
            ruta.write_text("int edad = 20;", encoding="utf-8-sig")

            codigo = leer_archivo(ruta)
            _, arbol, error = analizar(codigo)

            self.assertEqual(codigo, "int edad = 20;")
            self.assertIsNone(error)
            self.assertIsNotNone(arbol)

    def test_archivo_inexistente(self):
        with self.assertRaises(OSError) as contexto:
            leer_archivo(Path("no_existe.cpp"))

        self.assertIn("No existe el archivo", str(contexto.exception))

    def test_ruta_que_es_una_carpeta(self):
        with self.assertRaises(OSError) as contexto:
            leer_archivo(CARPETA_EJEMPLOS)

        self.assertIn("no es un archivo", str(contexto.exception))

    def test_archivo_que_no_esta_en_utf8(self):
        with tempfile.TemporaryDirectory() as carpeta:
            ruta = Path(carpeta) / "latin1.cpp"
            ruta.write_bytes("int año = 1;".encode("latin-1"))

            with self.assertRaises(OSError) as contexto:
                leer_archivo(ruta)

        self.assertIn("UTF-8", str(contexto.exception))


class TestEjemplos(unittest.TestCase):
    def test_existen_los_ejemplos(self):
        self.assertEqual(len(VALIDOS), 6)
        self.assertEqual(len(INVALIDOS), 8)

    def test_ejemplos_validos_se_aceptan(self):
        for ruta in VALIDOS:
            with self.subTest(archivo=ruta.name):
                tokens, arbol, error = analizar(leer_archivo(ruta))

                self.assertIsNone(error)
                self.assertEqual(arbol.nombre, "Programa")
                self.assertEqual(tokens[-1].tipo, "EOF")

    def test_ejemplos_invalidos_se_rechazan_con_el_error_esperado(self):
        self.assertEqual(
            sorted(ruta.name for ruta in INVALIDOS),
            sorted(ERRORES_ESPERADOS),
        )

        for ruta in INVALIDOS:
            with self.subTest(archivo=ruta.name):
                _, arbol, error = analizar(leer_archivo(ruta))

                self.assertIsNone(arbol)
                for fragmento in ERRORES_ESPERADOS[ruta.name]:
                    self.assertIn(fragmento, error)

    def test_operadores_de_comparacion_en_un_archivo(self):
        codigo = """
        if (a == b) { }
        if (a != b) { }
        if (a < b) { }
        if (a > b) { }
        if (a <= b) { }
        if (a >= b) { }
        """

        with tempfile.TemporaryDirectory() as carpeta:
            ruta = Path(carpeta) / "comparaciones.cpp"
            ruta.write_text(codigo, encoding="utf-8")

            _, arbol, error = analizar(leer_archivo(ruta))

        self.assertIsNone(error)
        operadores = [nodo.hijos[1] for nodo in buscar_nodos(arbol, "Condicion")]
        self.assertEqual(operadores, ["==", "!=", "<", ">", "<=", ">="])

    def test_arbol_del_condicional_anidado(self):
        ruta = CARPETA_EJEMPLOS / "validos" / "condicional_anidado.cpp"
        _, arbol, _ = analizar(leer_archivo(ruta))

        externo = arbol.hijos[2].hijos[0]
        self.assertEqual(externo.nombre, "Condicional")
        self.assertEqual(externo.hijos[0], "if")
        self.assertEqual(externo.hijos[2].nombre, "Condicion")
        self.assertEqual(externo.hijos[2].hijos[1], ">=")
        self.assertEqual(externo.hijos[4].nombre, "Bloque")
        self.assertEqual(externo.hijos[5], "else")
        self.assertEqual(externo.hijos[6].nombre, "Bloque")

        interno = externo.hijos[4].hijos[1].hijos[0]
        self.assertEqual(interno.nombre, "Condicional")
        self.assertEqual(interno.hijos[2].hijos[1], "==")
        self.assertEqual(len(interno.hijos), 7)

        self.assertEqual(len(buscar_nodos(arbol, "Condicional")), 2)


class TestFuncionMain(unittest.TestCase):
    def ejecutar(self, *argumentos):
        salida = io.StringIO()
        errores = io.StringIO()

        with redirect_stdout(salida), redirect_stderr(errores):
            codigo = main(list(argumentos))

        return codigo, salida.getvalue(), errores.getvalue()

    def test_sin_argumentos_usa_el_ejemplo_predeterminado(self):
        codigo, salida, _ = self.ejecutar()

        self.assertEqual(codigo, 0)
        self.assertIn("ejemplo predeterminado", salida)
        self.assertIn("Código sintácticamente válido", salida)

    def test_archivo_valido_devuelve_cero(self):
        ruta = CARPETA_EJEMPLOS / "validos" / "condicional_else.cpp"
        codigo, salida, _ = self.ejecutar(str(ruta))

        self.assertEqual(codigo, 0)
        self.assertIn("Código sintácticamente válido", salida)
        self.assertIn("Condicional", salida)

    def test_archivo_invalido_devuelve_uno(self):
        ruta = CARPETA_EJEMPLOS / "invalidos" / "condicion_incompleta.cpp"
        codigo, salida, _ = self.ejecutar(str(ruta))

        self.assertEqual(codigo, 1)
        self.assertIn("Código inválido", salida)
        self.assertIn("Línea 3, columna 12", salida)
        self.assertNotIn("Árbol", salida)

    def test_archivo_inexistente_devuelve_dos(self):
        codigo, salida, errores = self.ejecutar("no_existe.cpp")

        self.assertEqual(codigo, 2)
        self.assertEqual(salida, "")
        self.assertIn("Error: No existe el archivo 'no_existe.cpp'", errores)

    def test_tokens_se_muestran_antes_del_arbol(self):
        ruta = CARPETA_EJEMPLOS / "validos" / "condicional.cpp"
        codigo, salida, _ = self.ejecutar("--tokens", str(ruta))

        self.assertEqual(codigo, 0)
        self.assertIn("Tokens reconocidos:", salida)
        self.assertIn("4:1        IF        if", salida)
        self.assertIn("4:10       >=        >=", salida)
        self.assertLess(
            salida.index("Tokens reconocidos:"),
            salida.index("Árbol de análisis sintáctico:"),
        )

    def test_tokens_en_archivo_con_error_sintactico(self):
        ruta = CARPETA_EJEMPLOS / "invalidos" / "sin_expresion.cpp"
        codigo, salida, _ = self.ejecutar("--tokens", str(ruta))

        self.assertEqual(codigo, 1)
        self.assertIn("Tokens reconocidos:", salida)
        self.assertIn("Error sintáctico", salida)

    def test_demo_con_los_ejemplos_del_proyecto(self):
        codigo, salida, _ = self.ejecutar("--demo")

        self.assertEqual(codigo, 0)
        self.assertIn("RESUMEN DE LA DEMOSTRACIÓN", salida)
        self.assertIn("Ejemplos procesados: 14", salida)
        self.assertIn("Comportamientos correctos: 14", salida)
        self.assertIn("Comportamientos incorrectos: 0", salida)
        self.assertNotIn("¿Coincide con lo esperado?: NO", salida)


class TestDemoConOtrasCarpetas(unittest.TestCase):
    def crear_ejemplos(self, carpeta, validos, invalidos):
        for subcarpeta, archivos in (("validos", validos), ("invalidos", invalidos)):
            (carpeta / subcarpeta).mkdir()

            for nombre, contenido in archivos.items():
                (carpeta / subcarpeta / nombre).write_text(contenido, encoding="utf-8")

    def ejecutar_demo(self, carpeta):
        salida = io.StringIO()
        errores = io.StringIO()

        with redirect_stdout(salida), redirect_stderr(errores):
            codigo = ejecutar_demo(False, carpeta)

        return codigo, salida.getvalue(), errores.getvalue()

    def test_discrepancia_devuelve_codigo_distinto_de_cero(self):
        with tempfile.TemporaryDirectory() as temporal:
            carpeta = Path(temporal)
            self.crear_ejemplos(
                carpeta,
                validos={"mal_clasificado.cpp": "int = 5;"},
                invalidos={"bien.cpp": "int x = ;"},
            )

            codigo, salida, _ = self.ejecutar_demo(carpeta)

        self.assertEqual(codigo, 1)
        self.assertIn("¿Coincide con lo esperado?: NO", salida)
        self.assertIn("Ejemplos procesados: 2", salida)
        self.assertIn("Comportamientos correctos: 1", salida)
        self.assertIn("Comportamientos incorrectos: 1", salida)

    def test_invalido_rechazado_cuenta_como_correcto(self):
        with tempfile.TemporaryDirectory() as temporal:
            carpeta = Path(temporal)
            self.crear_ejemplos(
                carpeta,
                validos={"ok.cpp": "int x = 1;"},
                invalidos={"error.cpp": "if (x) { }"},
            )

            codigo, salida, _ = self.ejecutar_demo(carpeta)

        self.assertEqual(codigo, 0)
        self.assertIn("Comportamientos correctos: 2", salida)
        self.assertIn("se esperaba un operador de comparación", salida)

    def test_carpeta_sin_ejemplos(self):
        with tempfile.TemporaryDirectory() as temporal:
            codigo, salida, errores = self.ejecutar_demo(Path(temporal))

        self.assertEqual(codigo, 2)
        self.assertIn("no se encontraron archivos .cpp", errores)


class TestInterfazDeTerminal(unittest.TestCase):
    def test_help(self):
        resultado = ejecutar_cli("--help")

        self.assertEqual(resultado.returncode, 0)
        self.assertIn("--tokens", resultado.stdout)
        self.assertIn("--demo", resultado.stdout)

    def test_sin_argumentos(self):
        resultado = ejecutar_cli()

        self.assertEqual(resultado.returncode, 0)
        self.assertIn("Código sintácticamente válido", resultado.stdout)

    def test_archivo_valido(self):
        resultado = ejecutar_cli("ejemplos/validos/condicional_else.cpp")

        self.assertEqual(resultado.returncode, 0)
        self.assertIn("Árbol de análisis sintáctico:", resultado.stdout)

    def test_archivo_invalido_no_produce_traceback(self):
        resultado = ejecutar_cli("ejemplos/invalidos/condicion_incompleta.cpp")

        self.assertEqual(resultado.returncode, 1)
        self.assertIn("Error sintáctico: Línea 3, columna 12", resultado.stdout)
        self.assertNotIn("Traceback", resultado.stdout + resultado.stderr)

    def test_archivo_inexistente(self):
        resultado = ejecutar_cli("ejemplos/no_existe.cpp")

        self.assertEqual(resultado.returncode, 2)
        self.assertIn("No existe el archivo", resultado.stderr)
        self.assertNotIn("Traceback", resultado.stderr)

    def test_archivo_y_demo_a_la_vez_es_un_error(self):
        resultado = ejecutar_cli("--demo", "ejemplos/validos/condicional.cpp")

        self.assertEqual(resultado.returncode, 2)
        self.assertIn("no se puede indicar un archivo junto con --demo", resultado.stderr)

    def test_demo_desde_otra_carpeta(self):
        with tempfile.TemporaryDirectory() as otra_carpeta:
            resultado = ejecutar_cli("--demo", cwd=otra_carpeta)

        self.assertEqual(resultado.returncode, 0)
        self.assertIn("Ejemplos procesados: 14", resultado.stdout)
        self.assertIn("Comportamientos incorrectos: 0", resultado.stdout)


if __name__ == "__main__":
    unittest.main()
