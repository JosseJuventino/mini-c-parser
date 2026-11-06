
# Se determina qué es cada palabra
# Para género m masculino, f femenino
# Numero es s singural y p plural
# Sustantivo es N
# Nombre propio es NP
# Adjetivo es Adj
# Verb es V (puede ser singular o plural)
# Adverbio es ADV
# Preposicion PREP
# que es que

# ( <TIPO>, <GENERO>, <NUMERO> )
LEXICO = {
    # Determinantes
    "el": ("DET", "m", "s"),
    "la":("DET", "f", "s"),
    "los": ("DET", "m", "p"),
    "las": ("DET", "f", "p"),

    # Nombres propios
    "marcela": ("NP", "f", "s"),
    "jaime": ("NP", "m", "s"),
    "jose":("NP", "m", "s"),

    # Sustantivos 
    "calabaza":("N", "f", "s"),
    "calabazas":("N", "f", "p"),
    "clase":("N", "f", "s"),
    "código": ("N", "m", "s"),
    "dulces":("N", "m", "p"),   
    "esqueleto": ("N", "m", "s"),
    "esqueletos":("N", "m", "p"),
    "examen":("N", "m", "s"),
    "exámenes":("N", "m", "p"),
    "fantasma":("N", "m", "s"),   
    "fantasmas":("N", "m", "p"),
    "gramática":("N", "f", "s"),
    "parser":("N", "m", "s"),
    "profesor":("N", "m", "s"),
    "telescopio": ("N", "m", "s"),

    # Adjetivos
    "nuevo": ("Adj", "m", "s"),
    "nuevos": ("Adj", "m", "p"),
    "pequeño":("Adj", "m", "s"),
    "pequeños":("Adj", "m", "p"),
    "pequeñas": ("Adj", "f", "p"),
    "pequeña": ("Adj", "f", "s"),

    # Verbos, género no importa 
    "asustó": ("V", None, "s"),  
    "come":("V", None, "s"),  
    "comen": ("V", None, "p"),  
    "corrige": ("V", None, "s"), 
    "corrigió":("V", None, "s"),  
    "duermen":("V", None, "p"),  
    "duerme":("V", None, "s"),
    "escribe":("V", None, "s"),  
    "escribimos":("V", None, "p"),  
    "explica":("V", None, "s"), 
    "ven":("V", None, "p"),  
    "vio": ("V", None, "s"),  

    # Adverbios, no importa ni género ni número
    "furiosamente":("ADV", None, None),
    "rápidamente": ("ADV", None, None),

    # Preposiciones 
    "a": ("PREP", None, None),    
    #"al":  ("PREP", "m", "s"),      
    "con":("PREP", None, None),
    "en": ("PREP", None, None),
    "de":("PREP", None, None),

    # que es que
    "que":("que", None, None),    
}