# Comparación con NLP moderno (spaCy) — Fase 1

Este módulo procesa un conjunto de oraciones en español con **spaCy** y guarda el resultado, para compararlo con lo que hace el parser propio basado en una gramática libre de contexto (CFG).

Las oraciones que se procesan son las mismas que intenta analizar la gramática extendida al español, como pide el enunciado de la Fase 1.

## Contenido

| Archivo | Qué es |
|---|---|
| `corpus_fase1.csv` | Corpus de entrada: 35 oraciones en español (elaboración propia). |
| `comparar_corpus.py` | Procesa el corpus con spaCy y genera la tabla y el log. |
| `demo_nlp.py` | Demo en vivo con 5 oraciones elegidas (o una oración cualquiera). |
| `tabla_comparacion.csv` | Salida: una fila por oración, con el resultado de spaCy y del parser propio. |
| `log_spacy.txt` | Salida: análisis palabra por palabra de cada oración. |

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

## Cómo ejecutar

Con el entorno virtual activo (debe verse `(venv)` al inicio de la línea de la terminal):

```bash
python comparar_corpus.py
```

Genera `tabla_comparacion.csv` y `log_spacy.txt`.

```bash
python demo_nlp.py                       # recorre 5 oraciones; Enter para avanzar
python demo_nlp.py --rapido              # sin pausas
python demo_nlp.py "El niño come."       # analiza una oración cualquiera
```

La demo muestra, por cada oración, la categoría gramatical de cada palabra, su función en la oración y el árbol de dependencias.

## Formato del corpus

`corpus_fase1.csv` tiene estas columnas:

| Columna | Descripción |
|---|---|
| `id` | Identificador de la oración. |
| `nivel` | `1` simples, `2` intermedias, `3` complejas, `A` agramaticales a propósito. |
| `oracion` | Texto de la oración. |
| `gramatical` | `si` o `no`. |
| `fenomeno` | Fenómeno lingüístico que la oración pone a prueba. |
| `esperado_parser_propio` | Resultado que se espera del parser propio (`acepta`, `rechaza`, `falla`...). |

Las oraciones son de elaboración propia, pensadas para probar un fenómeno concreto cada una. No provienen de un corpus público.

## Integrar los resultados del parser propio

Si en esta carpeta existe `resultados_parser_propio.csv`, `comparar_corpus.py` lo agrega a la tabla y calcula si el parser coincidió con lo esperado. Formato:

```
id,resultado
1,acepta
21,rechaza
```

Los valores permitidos son `acepta` o `rechaza`. Si el archivo no existe, las columnas del parser propio quedan en `PENDIENTE`.

## Qué esperar de los resultados

- spaCy **no valida si una oración es gramatical**: siempre devuelve un análisis, incluso con oraciones mal formadas. Una CFG sí acepta o rechaza.
- spaCy puede cometer errores de etiquetado (por ejemplo, tratar "perro" como nombre propio).
- El modelo usado es `es_core_news_sm` (el más pequeño). Otros modelos de spaCy en español pueden dar resultados distintos.

## Limitaciones

- El corpus tiene 35 oraciones, suficiente para la Fase 1 pero pequeño para sacar conclusiones estadísticas.
- Al ser oraciones de elaboración propia, no representan el español real.
- La revisión de qué análisis es correcto se hizo a mano, sin una anotación de referencia (*gold standard*).
