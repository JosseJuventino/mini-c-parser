import argparse
import sys
from pathlib import Path

from .lexer import tokenizar
from .parser import Parser, Nodo


RAIZ_PROYECTO = Path(__file__).resolve().parent.parent
CARPETA_EJEMPLOS = RAIZ_PROYECTO / "ejemplos"

CODIGO_PREDETERMINADO = """
int edad = 20;
edad = edad + 5 * 2;

if (edad >= 18) {
    int resultado = (edad - 18) * 2;
} else {
    edad = 0;
}
"""


def imprimir_arbol(nodo, nivel=0):
    espacio = "  " * nivel

    if isinstance(nodo, Nodo):
        print(f"{espacio}{nodo.nombre}")

        for hijo in nodo.hijos:
            imprimir_arbol(hijo, nivel + 1)
    else:
        print(f"{espacio}{nodo}")


def imprimir_tokens(tokens):
    print("Tokens reconocidos:")
    print(f"  {'LÍNEA:COL':<11}{'TIPO':<10}VALOR")

    for token in tokens:
        posicion = f"{token.linea}:{token.columna}"
        print(f"  {posicion:<11}{token.tipo:<10}{token.valor}")

    print()


def leer_archivo(ruta: Path) -> str:
    if not ruta.exists():
        raise OSError(f"No existe el archivo '{ruta}'")

    if not ruta.is_file():
        raise OSError(f"'{ruta}' no es un archivo")

    try:
        return ruta.read_text(encoding="utf-8-sig")
    except UnicodeDecodeError:
        raise OSError(
            f"El archivo '{ruta}' no está guardado en UTF-8"
        ) from None


def analizar(codigo: str):
    try:
        tokens = tokenizar(codigo)
    except SyntaxError as error:
        return None, None, f"Error léxico: {error}"

    try:
        arbol = Parser(tokens).parsear()
    except SyntaxError as error:
        return tokens, None, f"Error sintáctico: {error}"

    return tokens, arbol, None


def mostrar_resultado(tokens, arbol, error, ver_tokens):
    if ver_tokens and tokens is not None:
        imprimir_tokens(tokens)

    if error is not None:
        print("Código inválido")
        print(error)
        return

    print("Código sintácticamente válido")
    print("\nÁrbol de análisis sintáctico:")
    imprimir_arbol(arbol)


def analizar_codigo(codigo: str, ver_tokens: bool) -> int:
    tokens, arbol, error = analizar(codigo)
    mostrar_resultado(tokens, arbol, error, ver_tokens)

    return 0 if error is None else 1


def analizar_archivo(ruta: Path, ver_tokens: bool) -> int:
    try:
        codigo = leer_archivo(ruta)
    except OSError as error:
        print(f"Error: {error}", file=sys.stderr)
        return 2

    print(f"Archivo: {ruta}\n")
    return analizar_codigo(codigo, ver_tokens)


def nombre_para_mostrar(ruta: Path) -> str:
    try:
        return ruta.relative_to(RAIZ_PROYECTO).as_posix()
    except ValueError:
        return str(ruta)


def ejecutar_demo(ver_tokens: bool, carpeta: Path = CARPETA_EJEMPLOS) -> int:
    casos = [
        (ruta, True) for ruta in sorted((carpeta / "validos").glob("*.cpp"))
    ] + [
        (ruta, False) for ruta in sorted((carpeta / "invalidos").glob("*.cpp"))
    ]

    if not casos:
        print(
            f"Error: no se encontraron archivos .cpp en '{carpeta}'",
            file=sys.stderr,
        )
        return 2

    correctos = 0

    for ruta, se_espera_valido in casos:
        print("=" * 70)
        print(f"Archivo: {nombre_para_mostrar(ruta)}")
        print(f"Resultado esperado: {'válido' if se_espera_valido else 'inválido'}")

        try:
            tokens, arbol, error = analizar(leer_archivo(ruta))
        except OSError as error_lectura:
            tokens, arbol, error = None, None, f"Error: {error_lectura}"

        es_valido = error is None
        coincide = es_valido == se_espera_valido

        if coincide:
            correctos += 1

        print(f"Resultado obtenido: {'válido' if es_valido else 'inválido'}")
        print(f"¿Coincide con lo esperado?: {'sí' if coincide else 'NO'}")
        print()
        mostrar_resultado(tokens, arbol, error, ver_tokens)
        print()

    incorrectos = len(casos) - correctos

    print("=" * 70)
    print("RESUMEN DE LA DEMOSTRACIÓN")
    print()
    print(f"Ejemplos procesados: {len(casos)}")
    print(f"Comportamientos correctos: {correctos}")
    print(f"Comportamientos incorrectos: {incorrectos}")

    return 0 if incorrectos == 0 else 1


def crear_argumentos() -> argparse.ArgumentParser:
    argumentos = argparse.ArgumentParser(
        prog="python -m src.main",
        description=(
            "Analizador léxico y sintáctico de Mini-C. Revisa si un "
            "fragmento de código cumple la gramática y muestra su árbol "
            "sintáctico. No ejecuta ni compila el código."
        ),
    )
    argumentos.add_argument(
        "archivo",
        nargs="?",
        type=Path,
        help=(
            "archivo .cpp con el código a analizar; si no se indica, "
            "se analiza un ejemplo predeterminado"
        ),
    )
    argumentos.add_argument(
        "-t",
        "--tokens",
        action="store_true",
        help="mostrar los tokens (tipo, valor, línea y columna) antes del árbol",
    )
    argumentos.add_argument(
        "--demo",
        action="store_true",
        help="analizar todos los ejemplos de ejemplos/validos y ejemplos/invalidos",
    )
    return argumentos


def main(argv=None) -> int:
    argumentos = crear_argumentos()
    opciones = argumentos.parse_args(argv)

    if opciones.demo and opciones.archivo is not None:
        argumentos.error("no se puede indicar un archivo junto con --demo")

    if opciones.demo:
        return ejecutar_demo(opciones.tokens)

    if opciones.archivo is not None:
        return analizar_archivo(opciones.archivo, opciones.tokens)

    print("Analizando el ejemplo predeterminado.")
    print("Para analizar un archivo: python -m src.main ruta/al/archivo.cpp\n")
    return analizar_codigo(CODIGO_PREDETERMINADO, opciones.tokens)


if __name__ == "__main__":
    sys.exit(main())
