# Comparación con NLP moderno (spaCy) — Fase 1

Este módulo procesa un conjunto de oraciones en español con **spaCy** para mostrar cómo una herramienta moderna de NLP las analiza. Es la contraparte del parser propio, basado en una gramática libre de contexto (CFG).

Las oraciones son las mismas que intenta analizar la gramática extendida al español, como pide el enunciado de la Fase 1.

## Contenido

| Archivo | Qué es |
|---|---|
| `corpus_fase1.csv` | Corpus de entrada: 35 oraciones en español (elaboración propia). |
| `analizar_oraciones.py` | Lee el corpus y guarda en un `.txt` el análisis de spaCy de cada oración. |
| `demo_nlp.py` | Demo en vivo con oraciones elegidas del corpus (o una oración cualquiera). |

Los resultados que genera el código (por ejemplo, `analisis_spacy.txt`) **no se incluyen en el repositorio**: se producen al ejecutar los scripts y están en `.gitignore`.

## Requisitos

- Python 3.9 o superior.
- Conexión a internet solo para instalar (spaCy y el modelo de español).

## Instalación

Desde la carpeta de este módulo:

```bash
python -m venv venv

# Windows
venv\Scripts\activate
# Mac / Linux
source venv/bin/activate

pip install spacy
python -m spacy download es_core_news_sm
```

El entorno virtual (`venv/`) no se sube al repositorio.

## Cómo ejecutar

Con el entorno virtual activo (debe verse `(venv)` al inicio de la línea de la terminal):

```bash
python analizar_oraciones.py                      # usa corpus_fase1.csv
python analizar_oraciones.py otro_corpus.csv      # usa otro corpus
python analizar_oraciones.py otro_corpus.csv salida.txt   # y otro nombre de salida
```

Genera `analisis_spacy.txt`. Al inicio deja constancia del corpus usado, la versión de spaCy, el modelo y la fecha. Después, para cada oración, incluye una tabla palabra por palabra (categoría gramatical, función, palabra de la que depende y rasgos de género y número) y el árbol de dependencias.

```bash
python demo_nlp.py                       # recorre las oraciones elegidas; Enter para avanzar
python demo_nlp.py --rapido              # sin pausas
python demo_nlp.py "El niño come."       # analiza una oración cualquiera
```

## Formato del corpus

Archivo `.csv` con estas columnas:

| Columna | Descripción |
|---|---|
| `oracion` | Texto de la oración. **Obligatoria.** |
| `id` | Identificador de la oración. |
| `nivel` | `1` simples, `2` intermedias, `3` complejas, `A` agramaticales a propósito. |
| `gramatical` | `si` o `no`. |
| `fenomeno` | Fenómeno lingüístico que la oración pone a prueba. |
| `esperado_parser_propio` | Resultado esperado del parser propio (`acepta`, `rechaza`, `falla`...). No la usa `analizar_oraciones.py`; se conserva para comparar con la gramática extendida. |

El script acepta archivos separados por coma, punto y coma o tabulación, y guardados en UTF-8 o en Windows-1252. También acepta un `.txt` con una oración por línea.

Las oraciones son de elaboración propia, pensadas para probar un fenómeno concreto cada una. No provienen de un corpus público.

## Qué esperar de los resultados

- spaCy **no valida si una oración es gramatical**: siempre devuelve un análisis, incluso con oraciones mal formadas. Una CFG sí acepta o rechaza.
- spaCy puede cometer errores de etiquetado (por ejemplo, marcar una forma verbal en indicativo como subjuntivo, o un sustantivo como adjetivo).
- El modelo usado es `es_core_news_sm` (el más pequeño). Otros modelos de spaCy en español pueden dar resultados distintos.

## Limitaciones

- El corpus tiene 35 oraciones: suficiente para ilustrar fenómenos en la Fase 1, pero pequeño para sacar conclusiones estadísticas.
- Al ser oraciones de elaboración propia, no representan el español real.
- La revisión de qué análisis es correcto se hizo a mano, sin una anotación de referencia (*gold standard*).
