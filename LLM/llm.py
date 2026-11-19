from google import genai
from oraciones import oraciones
from datetime import datetime

import sys
import os

sys.path.append(os.path.abspath("esp-parser/src"))

import gramatica

#Se manda a llamar al cliente de la API de Gemini con la API key
client = genai.Client(api_key="")

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

    #Aquí se manda el prompt a la api de gemini y se recibe su respuesta
    try:
        interaction = client.interactions.create(
            model='gemini-4-hydrogen',
            input=tipoPrompt,
        )
    
        response = interaction.output_text.strip()
    
    except Exception as e:
        print(f"Error: {e}")

    #Se obtiene el directorio actual del archivo llm.py para guardar los logs en la misma carpeta
    directorio_actual = os.path.dirname(os.path.abspath(__file__))

    #Se obtiene la fecha y hora actual
    timestamp = datetime.now().strftime("%d-%m-%Y_%H-%M")

    #Se crea un archivo de logs con el nombre del tipo de prompt y se guarda la respuesta generada por la API (un archivo por cada tipo de prompt Zero-Shot y Few-Shot)
    archivoLogs = os.path.join(directorio_actual, f"logs_{tipo.lower().replace('-', '_')}_{timestamp}.txt")
    with open(archivoLogs, "w", encoding="utf-8") as f_out:
        f_out.write(f"--- ANALISIS {tipo} (76 oraciones) ---\n\n")
        f_out.write("Prompt utilizado:\n")
        f_out.write(tipoPrompt)
        f_out.write("\n\n")
        f_out.write("Respuesta generada:\n")
        f_out.write(response)
                
    print(f"Analisis {tipo} finalizado. Logs guardados en '{archivoLogs}'.")
        
#Se ejecuta la función de analisis de oraciones para ambos tipos de prompt (Zero-Shot y Few-Shot)
analisisOraciones(promptZeroShot, "Zero-Shot")
analisisOraciones(promptFewShot, "Few-Shot")