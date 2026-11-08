
from dataclasses import dataclass
from lexer import Token
from parser import Nodo  

class ParserEsp:
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
                else "fin de la oración"
            )
            raise SyntaxError(
                f"Columna {token.columna}: "
                f"se esperaba '{tipo}', "
                f"pero se encontró '{encontrado}'"
            )
    
        self.posicion += 1
        return token

    def programa(self) -> Nodo:
        arbol = self.oracion()
        self.consumir("EOF")
        return Nodo("Programa", [arbol])

    def oracion(self) -> Nodo:
        # oracion -> Sujeto_s V_s | Sujeto_p V_p
        tipo = self.actual().tipo
        if tipo in ("DET_ms", "NP_ms", "DET_fs", "NP_fs"):
            sn = self.sujeto_s()
            verbo = self.verbo_s()
            return Nodo("Oracion", [sn, verbo])
        if tipo in ("DET_mp", "NP_mp", "DET_fp", "NP_fp", "N_mp", "N_fp"):
            sn = self.sujeto_p()
            verbo = self.verbo_p()
            return Nodo("Oracion", [sn, verbo])
        raise SyntaxError(
            f"Columna {self.actual().columna}: se esperaba un sujeto, "
            f"pero se encontró '{self.actual().valor}'"
        )

    def sujeto_ms(self) -> Nodo:
        # Alternativa 1: DET_ms N_ms adjs_ms
        if self.actual().tipo == "DET_ms":
            det = self.consumir("DET_ms")
            sust = self.consumir("N_ms")
            hijos = [det.valor, sust.valor]

            # adjs_ms -> Adj_ms*
            while self.actual().tipo == "Adj_ms":
                hijos.append(self.consumir("Adj_ms").valor)

            return Nodo("SN_ms", hijos)

        # Alternativa 2: NP_ms
        if self.actual().tipo == "NP_ms":
            nombre = self.consumir("NP_ms")
            return Nodo("SN_ms", [nombre.valor])

        token = self.actual()
        raise SyntaxError(
            f"Columna {token.columna}: se esperaba un sujeto "
            f"masculino singular, pero se encontró '{token.valor}'"
        )

    def sujeto_fs(self) -> Nodo:

        # Alternativa 1: DET_fs N_fs adjs_fs
        if self.actual().tipo == "DET_fs":
            det = self.consumir("DET_fs")
            sust = self.consumir("N_fs")
            hijos = [det.valor, sust.valor]
        
            # adjs_fs -> Adj_fs adj_fs | e
            while self.actual().tipo == "Adj_fs":
                hijos.append(self.consumir("Adj_fs").valor)
        
            return Nodo("SN_fs", hijos)

        # Alternativa 2: NP_fs
        if self.actual().tipo == "NP_fs":
            nombre = self.consumir("NP_fs")
            return Nodo("SN_fs", [nombre.valor])
            
        token = self.actual()
        raise SyntaxError(
            f"Columna {token.columna}: se esperaba un sujeto "
            f"femenino singular, pero se encontró '{token.valor}'"
        )

    def sujeto_mp(self) -> Nodo:
        # Alternativa 1: DET_mp N_mp adjs_mp
        if self.actual().tipo == "DET_mp":
            det = self.consumir("DET_mp")
            sust = self.consumir("N_mp")
            hijos = [det.valor, sust.valor]

            # adjs_mp -> Adj_mp adj_mp | e
            while self.actual().tipo == "Adj_mp":
                hijos.append(self.consumir("Adj_mp").valor)

            return Nodo("SN_mp", hijos)

        # Alternativa 2: NP_mp
        if self.actual().tipo == "NP_mp":
            nombre = self.consumir("NP_mp")
            return Nodo("SN_mp", [nombre.valor])

        # Alternativa 3: N_mp adjs_mp
        if self.actual().tipo == "N_mp":
            sust = self.consumir("N_mp")
            hijos = [sust.valor]

            # adjs_mp -> Adj_mp adj_mp | e
            while self.actual().tipo == "Adj_mp":
                hijos.append(self.consumir("Adj_mp").valor)

            return Nodo("SN_mp", hijos)

        token = self.actual()
        raise SyntaxError(
            f"Columna {token.columna}: se esperaba un sujeto "
            f"masculino plural, pero se encontró '{token.valor}'"
        )

    def sujeto_fp(self) -> Nodo:
        # Alternativa 1: DET_fp N_fp adjs_fp
        if self.actual().tipo == "DET_fp":
            det = self.consumir("DET_fp")
            sust = self.consumir("N_fp")
            hijos = [det.valor, sust.valor]

            # adjs_fp -> Adj_fp adj_fp | e
            while self.actual().tipo == "Adj_fp":
                hijos.append(self.consumir("Adj_fp").valor)

            return Nodo("SN_fp", hijos)

        # Alternativa 2: NP_fp
        if self.actual().tipo == "NP_fp":
            nombre = self.consumir("NP_fp")
            return Nodo("SN_fp", [nombre.valor])

        # Alternativa 3: N_fp adjs_fp
        if self.actual().tipo == "N_fp":
            sust = self.consumir("N_fp")
            hijos = [sust.valor]

            # adjs_fp -> Adj_fp adj_fp | e
            while self.actual().tipo == "Adj_fp":
                hijos.append(self.consumir("Adj_fp").valor)

            return Nodo("SN_fp", hijos)

        token = self.actual()
        raise SyntaxError(
            f"Columna {token.columna}: se esperaba un sujeto "
            f"femenino plural, pero se encontró '{token.valor}'"
        )

    def sujeto_s(self) -> Nodo:
        tipo = self.actual().tipo
        if tipo in ("DET_ms", "NP_ms"):
            return Nodo("Sujeto", [self.sujeto_ms()])
        if tipo in ("DET_fs", "NP_fs"):
            return Nodo("Sujeto", [self.sujeto_fs()])
        raise SyntaxError(
            f"Columna {self.actual().columna}: se esperaba un sujeto singular, "
            f"pero se encontró '{self.actual().valor}'"
        )

    def sujeto_p(self) -> Nodo:
        tipo = self.actual().tipo
        if tipo in ("DET_mp", "NP_mp", "N_mp"):
            return Nodo("Sujeto", [self.sujeto_mp()])
        if tipo in ("DET_fp", "NP_fp", "N_fp"):
            return Nodo("Sujeto", [self.sujeto_fp()])
        raise SyntaxError(
            f"Columna {self.actual().columna}: se esperaba un sujeto plural, "
            f"pero se encontró '{self.actual().valor}'"
        )
    
    def verbo_s(self) -> Nodo:
        #verbo_s -> V_s complemento 
        if self.actual().tipo == "V_s":
            verbo = self.consumir("V_s")
            hijos = [verbo.valor]
            hijos.append(self.complemento())
            #hijos.append(self.preps())
            #hijos.append(self.adverbio())
            return Nodo("Verbo", hijos)

        token = self.actual()
        raise SyntaxError(
            f"Columna {token.columna}: se esperaba un verbo "
            f"singular, pero se encontró '{token.valor}'"
        )

    def verbo_p(self) -> Nodo:
            #verbo_p -> V_p complemento
            if self.actual().tipo == "V_p":
                verbo = self.consumir("V_p")
                hijos = [verbo.valor]
                hijos.append(self.complemento())
                #hijos.append(self.preps())
                #hijos.append(self.adverbio())
                return Nodo("Verbo", hijos)
    
            token = self.actual()
            raise SyntaxError(
                f"Columna {token.columna}: se esperaba un verbo "
                f"plural, pero se encontró '{token.valor}'"
            )

    def sn(self) -> Nodo:
        tipo = self.actual().tipo
        if tipo in ("DET_ms", "NP_ms"):
            return Nodo("SN", [self.sujeto_ms()])
        if tipo in ("DET_fs", "NP_fs"):
            return Nodo("SN", [self.sujeto_fs()])
        if tipo in ("DET_mp", "NP_mp", "N_mp"):
            return Nodo("SN", [self.sujeto_mp()])
        if tipo in ("DET_fp", "NP_fp", "N_fp"):
            return Nodo("SN", [self.sujeto_fp()])
        raise SyntaxError(
            f"Columna {self.actual().columna}: se esperaba un sintagma nominal, "
            f"pero se encontró '{self.actual().valor}'"
        )

    def complemento(self) -> Nodo:
        # complemento -> SN complemento2 | que oracion | complemento2
        if self.actual().tipo in ("DET_ms", "NP_ms", "DET_fs", "NP_fs", "DET_mp", "NP_mp", "DET_fp", "NP_fp", "N_mp", "N_fp"):
            sn = self.sn()
            complemento2 = self.complemento2()
            return Nodo("Complemento", [sn, complemento2])
        if self.actual().tipo == "que":
            que = self.consumir("que")
            oracion = self.oracion()
            return Nodo("Complemento", [que.valor, oracion])
        if self.actual().tipo in ("PREP", "ADV", "EOF"):
            return Nodo("Complemento", [self.complemento2()])

        raise SyntaxError(
            f"Columna {self.actual().columna}: se esperaba un sintagma nominal, "
            f"'que', una preposición, un adverbio o fin de la oración, "
            f"pero se encontró '{self.actual().valor}'"
        )

    def complemento2(self) -> Nodo:
        hijos = []
        hijos.append(self.preps())
        hijos.append(self.adverbio())
        return Nodo("Complemento2", hijos)

    def preps(self) -> Nodo:
        # preps -> PREP SN preps | e
        if self.actual().tipo == "PREP":
            prep = self.consumir("PREP")
            sn = self.sn()
            preps = self.preps()
            return Nodo("Preposiciones", [prep.valor, sn, preps])

        # FOLLOW(preps) = {ADV, EOF}
        if self.actual().tipo in ("ADV", "EOF"):
            return Nodo("Preposiciones", [])

        token = self.actual()
        raise SyntaxError(
            f"Columna {token.columna}: se esperaba una preposición, "
            f"un adverbio o fin de la oración, "
            f"pero se encontró '{token.valor}'"
        )

    def adverbio(self) -> Nodo:
        # adverbio -> ADV | e
        if self.actual().tipo == "ADV":
            adv = self.consumir("ADV")
            return Nodo("Adverbio", [adv.valor])

        # FOLLOW(adverbio) = {EOF}
        if self.actual().tipo == "EOF":
            return Nodo("Adverbio", [])

        token = self.actual()
        raise SyntaxError(
            f"Columna {token.columna}: se esperaba un adverbio "
            f"o fin de la oración, pero se encontró '{token.valor}'"
        )
    