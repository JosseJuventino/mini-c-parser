# TLP02-2026 – Evaluación de parsers para el español

La Fase 2 compara el parser del equipo, spaCy, NLTK y Gemini sobre [76 oraciones](benchmark/corpus_fase2.csv). Cada oración tiene dos referencias. La columna `salida_cfg` indica si la gramática del equipo la acepta. La columna `gramatical` indica si es correcta en español.

## Reproducir la tabla del informe

Desde la raíz del repositorio, ejecute los siguientes comandos con Python. Usan la biblioteca estándar y las respuestas de Gemini que se entregan con el informe.

```powershell
python benchmark/normalizar_llm.py
python benchmark/evaluar.py
```

Abra el [CSV de resultados](benchmark/resultados/metricas_comparativas.csv) y filtre por `criterio = ESPAÑOL` y `nivel = general` para obtener la tabla 6.1. Hay cinco filas porque Gemini se evaluó con dos variantes del prompt. El 82.61 % de rechazo correcto de NLTK, por ejemplo, corresponde a 19 rechazos entre las 23 oraciones agramaticales. La columna `recall` contiene la cobertura que se reporta en el informe. La columna `cobertura` indica el porcentaje de oraciones que recibieron una decisión.

## Revisar una oración

Busque el identificador de la oración en el [registro del parser](benchmark/logs/log_parser_propio.csv), las [decisiones de spaCy](SPACY/logs/spacy.csv) y el [registro de NLTK](NLTK/logs/nltk.csv). El [análisis detallado de spaCy](SPACY/analisis_spacy.txt) permite consultar cada palabra. En los CSV de Gemini, la columna `indice` corresponde al número que lleva la oración en el prompt.

Por ejemplo, C21 («Yo come los dulces.») es la oración 69 del prompt. El parser y ambas variantes de Gemini la aceptaron de acuerdo con la CFG, que comprueba el número. spaCy y NLTK la rechazaron por la diferencia de persona entre «yo» y «come».

## Contrastar las dos corridas de Gemini

Cada TXT incluye el prompt exacto y la respuesta completa. Los horarios que siguen son los que figuran en los nombres de los archivos del 18 de noviembre de 2026.

- **Corrida del informe.** Los registros [zero-shot](LLM/logs_zero_shot_18-11-2026_1-00.txt) y [few-shot](LLM/logs_few_shot_18-11-2026_1-00.txt) llevan la hora 01:00. Esa hora se incorporó al renombrar los archivos originales. El normalizador usa este par por defecto.
- **Segunda corrida.** Los registros [zero-shot de las 23:58](LLM/logs_zero_shot_18-11-2026_23-58.txt) y [few-shot de las 23:59](LLM/logs_few_shot_18-11-2026_23-59.txt) usaron los mismos prompts. Para comprobar sus resultados, ejecute:

```powershell
python benchmark/normalizar_llm.py --zero-shot LLM/logs_zero_shot_18-11-2026_23-58.txt --few-shot LLM/logs_few_shot_18-11-2026_23-59.txt
python benchmark/evaluar.py
```

Ambas corridas dieron las mismas 76 decisiones por variante. Frente a la CFG, zero-shot acertó 75 de 76 y few-shot acertó las 76. La única diferencia fue C02, una de las cuatro oraciones incluidas como ejemplo. Al excluir esos ejemplos, ambas variantes acertaron las 72 restantes.

## Generar las gráficas y repetir los experimentos

El equipo utilizó Python 3.14.3. En PowerShell, desde la raíz:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python benchmark/graficar.py
```

Las tres gráficas quedan en [benchmark/resultados/graficas](benchmark/resultados/graficas/). Para generar registros nuevos, trabaje en una copia del repositorio. El parser, spaCy y NLTK actualizan sus archivos de salida.

- **Parser propio.** Ejecute `python esp-parser/src/logEsp.py`.
- **spaCy.** Ejecute `python SPACY/analizar_oraciones.py`. Genera el TXT con el análisis por palabra y el CSV con la decisión de cada oración.
- **NLTK.** Ejecute `python NLTK/correr_nltk.py`. La primera corrida descarga el corpus de entrenamiento `cess_esp` si hace falta.
- **Gemini.** Con una clave de la API en la variable de entorno `GEMINI_API_KEY` y acceso al modelo `gemini-4-hydrogen`, ejecute `python LLM/llm.py`. Hace una llamada por variante y guarda en `LLM/` un TXT por respuesta con la hora de inicio y la zona horaria. Para evaluar esos TXT, pase sus rutas al normalizador con `--zero-shot` y `--few-shot` y vuelva a ejecutar `python benchmark/evaluar.py`.
