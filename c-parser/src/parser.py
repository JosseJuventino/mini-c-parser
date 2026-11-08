from dataclasses import dataclass
from .lexer import Token

OPERADORES_COMPARACION = ("==", "!=", "<", ">", "<=", ">=")

@dataclass
class Nodo:
    nombre: str
    hijos: list
class Parser:
    def __init__(self, tokens: list[Token]):
        self.tokens = tokens
        self.posicion = 0

    def actual(self) -> Token:
        return self.tokens[self.posicion]

    def consumir(self, tipo: str) -> Token:
        token = self.actual()

        if token.tipo != tipo:
            encontrado = (
                token.valor
                if token.tipo != "EOF"
                else "fin del código"
            )

            raise SyntaxError(
                f"Línea {token.linea}, columna {token.columna}: "
                f"se esperaba '{tipo}', "
                f"pero se encontró '{encontrado}'"
            )

        self.posicion += 1
        return token

    def parsear(self) -> Nodo:
        hijos = []

        while self.actual().tipo != "EOF":
            hijos.append(self.sentencia())

        self.consumir("EOF")
        return Nodo("Programa", hijos)

    def sentencia(self) -> Nodo:
        tipo = self.actual().tipo

        if tipo == "INT":
            return Nodo("Sentencia", [self.declaracion()])

        if tipo == "ID":
            return Nodo("Sentencia", [self.asignacion()])

        if tipo == "IF":
            return Nodo("Sentencia", [self.condicional()])

        token = self.actual()

        if tipo == "ELSE":
            raise SyntaxError(
                f"Línea {token.linea}, columna {token.columna}: "
                f"se encontró 'else' sin un 'if' antes"
            )

        encontrado = (
            token.valor
            if token.tipo != "EOF"
            else "fin del código"
        )

        raise SyntaxError(
            f"Línea {token.linea}, columna {token.columna}: "
            f"se esperaba una declaración, asignación o 'if', "
            f"pero se encontró '{encontrado}'"
        )

    def condicional(self) -> Nodo:
        self.consumir("IF")
        self.consumir("(")
        condicion = self.condicion()
        self.consumir(")")
        bloque_if = self.bloque()

        hijos = ["if", "(", condicion, ")", bloque_if]

        if self.actual().tipo == "ELSE":
            self.consumir("ELSE")
            hijos.extend(["else", self.bloque()])

        return Nodo("Condicional", hijos)

    def bloque(self) -> Nodo:
        apertura = self.consumir("{")
        hijos = ["{"]

        while self.actual().tipo not in ("}", "EOF"):
            hijos.append(self.sentencia())

        if self.actual().tipo == "EOF":
            token = self.actual()
            raise SyntaxError(
                f"Línea {token.linea}, columna {token.columna}: "
                f"se esperaba '}}' para cerrar el bloque abierto en la "
                f"línea {apertura.linea}, columna {apertura.columna}, "
                f"pero se encontró 'fin del código'"
            )

        self.consumir("}")
        hijos.append("}")

        return Nodo("Bloque", hijos)

    def condicion(self) -> Nodo:
        izquierda = self.expresion()

        token = self.actual()

        if token.tipo not in OPERADORES_COMPARACION:
            encontrado = (
                token.valor
                if token.tipo != "EOF"
                else "fin del código"
            )

            raise SyntaxError(
                f"Línea {token.linea}, columna {token.columna}: "
                f"se esperaba un operador de comparación "
                f"(==, !=, <, >, <=, >=), "
                f"pero se encontró '{encontrado}'"
            )

        operador = self.consumir(token.tipo)
        derecha = self.expresion()

        return Nodo("Condicion", [izquierda, operador.valor, derecha])

    def declaracion(self) -> Nodo:
        self.consumir("INT")
        nombre = self.consumir("ID")
        self.consumir("=")
        expresion = self.expresion()
        self.consumir(";")

        return Nodo("Declaracion", [
            "int", nombre.valor, "=", expresion, ";"
        ])

    def asignacion(self) -> Nodo:
        nombre = self.consumir("ID")
        self.consumir("=")
        expresion = self.expresion()
        self.consumir(";")

        return Nodo("Asignacion", [
            nombre.valor, "=", expresion, ";"
        ])

    def expresion(self) -> Nodo:
        hijos = [self.termino()]

        while self.actual().tipo in ("+", "-"):
            operador = self.consumir(self.actual().tipo)
            hijos.extend([operador.valor, self.termino()])

        return Nodo("Expresion", hijos)

    def termino(self) -> Nodo:
        hijos = [self.factor()]

        while self.actual().tipo in ("*", "/"):
            operador = self.consumir(self.actual().tipo)
            hijos.extend([operador.valor, self.factor()])

        return Nodo("Termino", hijos)

    def factor(self) -> Nodo:
        tipo = self.actual().tipo

        if tipo == "NUMERO":
            numero = self.consumir("NUMERO")
            return Nodo("Factor", [numero.valor])

        if tipo == "ID":
            nombre = self.consumir("ID")
            return Nodo("Factor", [nombre.valor])

        if tipo == "(":
            self.consumir("(")
            expresion = self.expresion()
            self.consumir(")")
            return Nodo("Factor", ["(", expresion, ")"])

        token = self.actual()
        encontrado = (
            token.valor
            if token.tipo != "EOF"
            else "fin del código"
        )

        raise SyntaxError(
            f"Línea {token.linea}, columna {token.columna}: "
            f"se esperaba un número, identificador o '(', "
            f"pero se encontró '{encontrado}'"
        )
