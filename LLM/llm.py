from google import genai
from oraciones import oraciones
from datetime import datetime

import sys
import os

sys.path.append(os.path.abspath("esp-parser/src"))

import gramatica

#Se manda a llamar al cliente de la API de Gemini con la API key
api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    sys.exit("Defina GEMINI_API_KEY para ejecutar una nueva corrida de Gemini.")
client = genai.Client(api_key=api_key)

#Se pasan las reglas a texto para poder mandarlas en el prompt
reglas = "Símbolo Inicial: " + gramatica.INICIAL + "\nReglas:\n"
for noTerminal, producciones in gramatica.GRAMATICA.items():
    derecha = [" ".join(p) if p else "ε" for p in producciones]
    reglas += f"  {noTerminal} -> {' | '.join(derecha)}\n"

#Se crea el prompt Zero-Shorts para el analisis de las oraciones (incluye las reglas y todas las oraciones) 
promptZeroShot = f"""
Necesito que analices estas oraciones basándote exclusivamente en las reglas que te proporcionaré a continuación. No uses tu conocimiento general del español ni modifiques las reglas ya creadas. Haz el analisis de cada oración indicando el indice, la oración, si se acepta o se rechaza, el fenomeno que se observa y la estructura generada.

Reglas de nuestra gramática:
{reglas}

Oraciones a analizar:
{oraciones}
"""

#Se crea el prompt Few-Shots para el analisis de las oraciones (incluye las reglas, todas las oraciones y ejemplos de oraciones aceptadas y rechazadas)
promptFewShot = promptZeroShot + """

Toma estos ejemplos como referencia:
Oración1: "Los esqueletos dibujaron las calabazas."
Salida esperada: Aceptada.
Fenomeno: SVO en pretérito con sujeto plural.
Estructura generada: (Programa -> {Oracion -> [Sujeto_p -> (SN_mp -> {DET_mp -> los} {N_mp -> esqueletos} {Adjs_mp -> ε})] [SV_p -> (V_p -> dibujaron) (Complemento -> {SN -> [SN_fp -> (DET_fp -> las) (N_fp -> calabazas) (Adjs_fp -> ε)]} {Complemento2 -> [Preps -> ε] [Adverbio -> ε]})]})

Oración2: "Marcela vio al fantasma con el telescopio."
Salida esperada: Aceptada.
Fenomeno: «Con el telescopio» admite dos lecturas. La CFG agrupa ambas frases en la secuencia de SP.
Estructura generada: (Programa -> {Oracion -> [Sujeto_s -> (SN_fs -> {NP_fs -> marcela})] [SV_s -> (V_s -> vio) (Complemento -> {Complemento2 -> [Preps -> (PREP -> a) (SN -> {SN_ms -> [DET_ms -> el] [N_ms -> fantasma] [Adjs_ms -> ε]}) (Preps -> {PREP -> con} {SN -> [SN_ms -> (DET_ms -> el) (N_ms -> telescopio) (Adjs_ms -> ε)]} {Preps -> ε})] [Adverbio -> ε]})]})

Oración3: "Los fantasma come los dulces."
Salida esperada: Rechazada.
Fenomeno: Primer fallo en «fantasma». Se espera N_mp.
Estructura generada: Sin árbol generado.

Oración4: "El examen que Jaime corrigió asustó a Jose."
Salida esperada: Rechazada.
Fenomeno: Relativa en el sujeto con objeto omitido dentro de la relativa.
Estructura generada: Sin árbol generado.
"""

#Función donde se envia el tipo de prompt y se indica el tipo de prompt para el analisis de oraciones y guardarlas en un archivo de logs
def analisisOraciones(tipoPrompt, tipo):
    print(f"\n--- INICIANDO ANALISIS: {tipo} (76 oraciones) ---")

    inicio = datetime.now().astimezone()
    interaction = client.interactions.create(
        model="gemini-4-hydrogen",
        input=tipoPrompt,
    )
    response = interaction.output_text
    if not response or not response.strip():
        raise RuntimeError(f"Gemini devolvió una respuesta vacía para {tipo}.")

    directorio_actual = os.path.dirname(os.path.abspath(__file__))
    timestamp = inicio.strftime("%d-%m-%Y_%H-%M-%S-%f")
    archivoLogs = os.path.join(directorio_actual, f"logs_{tipo.lower().replace('-', '_')}_{timestamp}.txt")
    with open(archivoLogs, "x", encoding="utf-8") as f_out:
        f_out.write(f"--- ANALISIS {tipo} (76 oraciones) ---\n")
        f_out.write(f"Inicio de la llamada: {inicio.isoformat()}\n\n")
        f_out.write("Prompt utilizado:\n")
        f_out.write(tipoPrompt)
        f_out.write("\n\nRespuesta generada:\n")
        f_out.write(response)

    print(f"Analisis {tipo} finalizado. Logs guardados en '{archivoLogs}'.")
        
#Se ejecuta la función de analisis de oraciones para ambos tipos de prompt (Zero-Shot y Few-Shot)
analisisOraciones(promptZeroShot, "Zero-Shot")
analisisOraciones(promptFewShot, "Few-Shot")