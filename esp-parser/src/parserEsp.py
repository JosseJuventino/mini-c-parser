"""
parserEsp.py

Parser descendente recursivo predictivo para la gramática de gramatica.py.

Cada no terminal de la gramática tiene un método con su nombre en minúsculas
(Oracion -> oracion(), SN_ms -> sn_ms(), ...). Cada método mira solo el token
actual para decidir qué producción aplicar, sin retroceder. Eso es posible
porque la gramática es LL(1), y se comprueba con ll1.verificar_ll1() antes
de analizar.

El resultado es el árbol de derivación de la oración:
  - Un no terminal es un Nodo cuyo nombre es el no terminal y cuyos hijos
    son, en orden, los símbolos de la producción que se aplicó.
  - Un terminal es un Nodo cuyo nombre es el tipo de token (DET_ms, V_s...)
    y cuyo único hijo es la palabra de la oración.
  - La producción vacía se representa con el hijo EPSILON.
  - El token EOF se consume para comprobar que no sobran palabras, pero no
    se agrega al árbol porque no es una palabra de la oración.
"""

from dataclasses import dataclass
from lexer import Token
from parser import Nodo
from gramatica import EPSILON
from ll1 import verificar_ll1

class ParserEsp:
    def __init__(self, tokens: list[Token]):
        # Antes de analizar se comprueba que la gramática de gramatica.py
        # (la misma que implementan los métodos de esta clase) es LL(1).
        # Si no lo fuera, se lanza GramaticaNoLL1 y el parser no llega a
        # ejecutarse. El cálculo se hace una sola vez por ejecución; las
        # siguientes llamadas lo reutilizan.
        verificar_ll1()

        self.tokens = tokens
        self.posicion = 0

    def actual(self) -> Token:
        return self.tokens[self.posicion]

    def texto_actual(self) -> str:
        # Texto del token actual para los mensajes de error. El token EOF
        # no tiene palabra, así que se describe como "fin de la oración".
        token = self.actual()
        if token.tipo == "EOF":
            return "fin de la oración"
        return token.valor

    def consumir(self, tipo: str) -> Token:
        token = self.actual()

        if token.tipo != tipo:
            raise SyntaxError(
                f"Columna {token.columna}: "
                f"se esperaba '{tipo}', "
                f"pero se encontró '{self.texto_actual()}'"
            )

        self.posicion += 1
        return token

    def terminal(self, tipo: str) -> Nodo:
        # Consume un token del tipo indicado y devuelve su hoja del árbol:
        # el tipo de token como nombre y la palabra como único hijo.
        token = self.consumir(tipo)
        return Nodo(tipo, [token.valor])

    def programa(self) -> Nodo:
        # Programa -> Oracion EOF
        arbol = self.oracion()
        self.consumir("EOF")
        return Nodo("Programa", [arbol])

    def oracion(self) -> Nodo:
        # Oracion -> Sujeto_s SV_s | Sujeto_p SV_p
        tipo = self.actual().tipo
        if tipo in ("DET_ms", "NP_ms", "DET_fs", "NP_fs", "PRON_s"):
            sujeto = self.sujeto_s()
            verbo = self.sv_s()
            return Nodo("Oracion", [sujeto, verbo])
        if tipo in ("DET_mp", "N_mp", "DET_fp", "N_fp", "PRON_p"):
            sujeto = self.sujeto_p()
            verbo = self.sv_p()
            return Nodo("Oracion", [sujeto, verbo])
        raise SyntaxError(
            f"Columna {self.actual().columna}: se esperaba un sujeto, "
            f"pero se encontró '{self.texto_actual()}'"
        )

    def sujeto_s(self) -> Nodo:
        # Sujeto_s -> SN_ms | SN_fs | PRON_s
        tipo = self.actual().tipo
        if tipo in ("DET_ms", "NP_ms"):
            return Nodo("Sujeto_s", [self.sn_ms()])
        if tipo in ("DET_fs", "NP_fs"):
            return Nodo("Sujeto_s", [self.sn_fs()])
        if tipo == "PRON_s":
            return Nodo("Sujeto_s", [self.terminal("PRON_s")])
        raise SyntaxError(
            f"Columna {self.actual().columna}: se esperaba un sujeto singular, "
            f"pero se encontró '{self.texto_actual()}'"
        )

    def sujeto_p(self) -> Nodo:
        # Sujeto_p -> SN_mp | SN_fp | PRON_p
        tipo = self.actual().tipo
        if tipo in ("DET_mp", "N_mp"):
            return Nodo("Sujeto_p", [self.sn_mp()])
        if tipo in ("DET_fp", "N_fp"):
            return Nodo("Sujeto_p", [self.sn_fp()])
        if tipo == "PRON_p":
            return Nodo("Sujeto_p", [self.terminal("PRON_p")])
        raise SyntaxError(
            f"Columna {self.actual().columna}: se esperaba un sujeto plural, "
            f"pero se encontró '{self.texto_actual()}'"
        )

    def sn_ms(self) -> Nodo:
        # SN_ms -> DET_ms N_ms Adjs_ms | NP_ms

        # Alternativa 1: DET_ms N_ms Adjs_ms
        if self.actual().tipo == "DET_ms":
            det = self.terminal("DET_ms")
            sust = self.terminal("N_ms")
            adjs = self.adjs_ms()
            return Nodo("SN_ms", [det, sust, adjs])

        # Alternativa 2: NP_ms
        if self.actual().tipo == "NP_ms":
            return Nodo("SN_ms", [self.terminal("NP_ms")])

        token = self.actual()
        raise SyntaxError(
            f"Columna {token.columna}: se esperaba un sintagma nominal "
            f"masculino singular, pero se encontró '{self.texto_actual()}'"
        )

    def sn_fs(self) -> Nodo:
        # SN_fs -> DET_fs N_fs Adjs_fs | NP_fs

        # Alternativa 1: DET_fs N_fs Adjs_fs
        if self.actual().tipo == "DET_fs":
            det = self.terminal("DET_fs")
            sust = self.terminal("N_fs")
            adjs = self.adjs_fs()
            return Nodo("SN_fs", [det, sust, adjs])

        # Alternativa 2: NP_fs
        if self.actual().tipo == "NP_fs":
            return Nodo("SN_fs", [self.terminal("NP_fs")])

        token = self.actual()
        raise SyntaxError(
            f"Columna {token.columna}: se esperaba un sintagma nominal "
            f"femenino singular, pero se encontró '{self.texto_actual()}'"
        )

    def sn_mp(self) -> Nodo:
        # SN_mp -> DET_mp N_mp Adjs_mp | N_mp Adjs_mp

        # Alternativa 1: DET_mp N_mp Adjs_mp
        if self.actual().tipo == "DET_mp":
            det = self.terminal("DET_mp")
            sust = self.terminal("N_mp")
            adjs = self.adjs_mp()
            return Nodo("SN_mp", [det, sust, adjs])

        # Alternativa 2: N_mp Adjs_mp
        if self.actual().tipo == "N_mp":
            sust = self.terminal("N_mp")
            adjs = self.adjs_mp()
            return Nodo("SN_mp", [sust, adjs])

        token = self.actual()
        raise SyntaxError(
            f"Columna {token.columna}: se esperaba un sintagma nominal "
            f"masculino plural, pero se encontró '{self.texto_actual()}'"
        )

    def sn_fp(self) -> Nodo:
        # SN_fp -> DET_fp N_fp Adjs_fp | N_fp Adjs_fp

        # Alternativa 1: DET_fp N_fp Adjs_fp
        if self.actual().tipo == "DET_fp":
            det = self.terminal("DET_fp")
            sust = self.terminal("N_fp")
            adjs = self.adjs_fp()
            return Nodo("SN_fp", [det, sust, adjs])

        # Alternativa 2: N_fp Adjs_fp
        if self.actual().tipo == "N_fp":
            sust = self.terminal("N_fp")
            adjs = self.adjs_fp()
            return Nodo("SN_fp", [sust, adjs])

        token = self.actual()
        raise SyntaxError(
            f"Columna {token.columna}: se esperaba un sintagma nominal "
            f"femenino plural, pero se encontró '{self.texto_actual()}'"
        )

    # Adjetivos. En los cuatro métodos, si el token actual no es un adjetivo
    # que concuerde se aplica la producción vacía. Si ese token tampoco
    # pertenece a FOLLOW, el error lo reporta el método que continúa (por
    # ejemplo, "se esperaba un verbo plural, pero se encontró 'pequeños'").

    def adjs_ms(self) -> Nodo:
        # Adjs_ms -> Adj_ms Adjs_ms | Adj_cs Adjs_ms | ε
        tipo = self.actual().tipo
        if tipo in ("Adj_ms", "Adj_cs"):
            adjetivo = self.terminal(tipo)
            resto = self.adjs_ms()
            return Nodo("Adjs_ms", [adjetivo, resto])
        return Nodo("Adjs_ms", [EPSILON])

    def adjs_fs(self) -> Nodo:
        # Adjs_fs -> Adj_fs Adjs_fs | Adj_cs Adjs_fs | ε
        tipo = self.actual().tipo
        if tipo in ("Adj_fs", "Adj_cs"):
            adjetivo = self.terminal(tipo)
            resto = self.adjs_fs()
            return Nodo("Adjs_fs", [adjetivo, resto])
        return Nodo("Adjs_fs", [EPSILON])

    def adjs_mp(self) -> Nodo:
        # Adjs_mp -> Adj_mp Adjs_mp | Adj_cp Adjs_mp | ε
        tipo = self.actual().tipo
        if tipo in ("Adj_mp", "Adj_cp"):
            adjetivo = self.terminal(tipo)
            resto = self.adjs_mp()
            return Nodo("Adjs_mp", [adjetivo, resto])
        return Nodo("Adjs_mp", [EPSILON])

    def adjs_fp(self) -> Nodo:
        # Adjs_fp -> Adj_fp Adjs_fp | Adj_cp Adjs_fp | ε
        tipo = self.actual().tipo
        if tipo in ("Adj_fp", "Adj_cp"):
            adjetivo = self.terminal(tipo)
            resto = self.adjs_fp()
            return Nodo("Adjs_fp", [adjetivo, resto])
        return Nodo("Adjs_fp", [EPSILON])

    def sv_s(self) -> Nodo:
        # SV_s -> V_s Complemento
        if self.actual().tipo == "V_s":
            verbo = self.terminal("V_s")
            complemento = self.complemento()
            return Nodo("SV_s", [verbo, complemento])

        token = self.actual()
        raise SyntaxError(
            f"Columna {token.columna}: se esperaba un verbo "
            f"singular, pero se encontró '{self.texto_actual()}'"
        )

    def sv_p(self) -> Nodo:
        # SV_p -> V_p Complemento
        if self.actual().tipo == "V_p":
            verbo = self.terminal("V_p")
            complemento = self.complemento()
            return Nodo("SV_p", [verbo, complemento])

        token = self.actual()
        raise SyntaxError(
            f"Columna {token.columna}: se esperaba un verbo "
            f"plural, pero se encontró '{self.texto_actual()}'"
        )

    def sn(self) -> Nodo:
        # SN -> SN_ms | SN_fs | SN_mp | SN_fp
        tipo = self.actual().tipo
        if tipo in ("DET_ms", "NP_ms"):
            return Nodo("SN", [self.sn_ms()])
        if tipo in ("DET_fs", "NP_fs"):
            return Nodo("SN", [self.sn_fs()])
        if tipo in ("DET_mp", "N_mp"):
            return Nodo("SN", [self.sn_mp()])
        if tipo in ("DET_fp", "N_fp"):
            return Nodo("SN", [self.sn_fp()])
        raise SyntaxError(
            f"Columna {self.actual().columna}: se esperaba un sintagma nominal, "
            f"pero se encontró '{self.texto_actual()}'"
        )

    def complemento(self) -> Nodo:
        # Complemento -> SN Complemento2 | que Oracion | Complemento2
        tipo = self.actual().tipo

        # Alternativa 1: SN Complemento2 (el token está en FIRST(SN))
        if tipo in ("DET_ms", "NP_ms", "DET_fs", "NP_fs", "DET_mp", "N_mp", "DET_fp", "N_fp"):
            sn = self.sn()
            complemento2 = self.complemento2()
            return Nodo("Complemento", [sn, complemento2])

        # Alternativa 2: que Oracion
        if tipo == "que":
            que = self.terminal("que")
            oracion = self.oracion()
            return Nodo("Complemento", [que, oracion])

        # Alternativa 3: Complemento2, que puede ser vacío. Se elige con
        # FIRST(Complemento2) = {PREP, ADV} y FOLLOW(Complemento) = {EOF}.
        if tipo in ("PREP", "ADV", "EOF"):
            return Nodo("Complemento", [self.complemento2()])

        raise SyntaxError(
            f"Columna {self.actual().columna}: se esperaba un sintagma nominal, "
            f"'que', una preposición, un adverbio o fin de la oración, "
            f"pero se encontró '{self.texto_actual()}'"
        )

    def complemento2(self) -> Nodo:
        # Complemento2 -> Preps Adverbio
        preps = self.preps()
        adverbio = self.adverbio()
        return Nodo("Complemento2", [preps, adverbio])

    def preps(self) -> Nodo:
        # Preps -> PREP SN Preps | ε
        if self.actual().tipo == "PREP":
            prep = self.terminal("PREP")
            sn = self.sn()
            preps = self.preps()
            return Nodo("Preps", [prep, sn, preps])

        # Producción vacía: FOLLOW(Preps) = {ADV, EOF}
        if self.actual().tipo in ("ADV", "EOF"):
            return Nodo("Preps", [EPSILON])

        token = self.actual()
        raise SyntaxError(
            f"Columna {token.columna}: se esperaba una preposición, "
            f"un adverbio o fin de la oración, "
            f"pero se encontró '{self.texto_actual()}'"
        )

    def adverbio(self) -> Nodo:
        # Adverbio -> ADV | ε
        if self.actual().tipo == "ADV":
            return Nodo("Adverbio", [self.terminal("ADV")])

        # Producción vacía: FOLLOW(Adverbio) = {EOF}
        if self.actual().tipo == "EOF":
            return Nodo("Adverbio", [EPSILON])

        token = self.actual()
        raise SyntaxError(
            f"Columna {token.columna}: se esperaba un adverbio "
            f"o fin de la oración, pero se encontró '{self.texto_actual()}'"
        )
