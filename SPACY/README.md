# Análisis de oraciones en español con spaCy

## Descripción del módulo

Este módulo procesa un conjunto de oraciones en español mediante **spaCy**, una biblioteca de Python para el procesamiento del lenguaje natural (*Natural Language Processing*, NLP).

A partir de un corpus de oraciones elaborado para el proyecto, el programa utiliza el modelo de español `es_core_news_sm` para obtener información lingüística de cada oración. Entre los resultados se encuentran la categoría gramatical de cada palabra, su relación sintáctica con otras palabras y distintos rasgos morfológicos.

El programa aplica un criterio de aceptación y rechazo definido por el equipo (ver sección **Criterio de evaluación**) y genera dos archivos de salida: un reporte textual con el análisis detallado de cada oración y un CSV con la decisión por oración.

## Contenido

| Archivo | Descripción |
|---|---|
| `../benchmark/corpus_fase2.csv` | Corpus de entrada utilizado por defecto, con 76 oraciones en español elaboradas para observar distintos fenómenos lingüísticos. |
| `analizar_oraciones.py` | Lee el corpus, procesa cada oración con spaCy, aplica el criterio C1–C2–C3 y guarda los resultados en un archivo de texto y en un CSV. |
| `logs/spacy.csv` | CSV con la decisión por oración (`acepta`, `acepta_parcial` o `rechaza`) y el detalle de cada criterio. |
| `demo_nlp.py` | Demostración en vivo: muestra en pantalla el análisis de spaCy de oraciones seleccionadas del corpus o de una oración escrita por el usuario. |

El archivo `analisis_spacy.txt` no se incluye en el repositorio: se produce al ejecutar el script y está contemplado en `.gitignore`.

## Requisitos

- Python 3.9 o superior.
- Conexión a internet para instalar spaCy y descargar el modelo de español.
- Biblioteca spaCy.
- Modelo de lenguaje `es_core_news_sm`.

## Instalación

Desde la carpeta raíz del repositorio, activa el entorno virtual:

```bash
# Windows
venv\Scripts\activate

# Mac / Linux
source venv/bin/activate
```

Instala las dependencias del proyecto:

```bash
pip install -r requirements.txt
```

El entorno virtual (`venv/`) no se sube al repositorio.

## Cómo ejecutar

Con el entorno virtual activo, ejecuta desde la **carpeta raíz del repositorio**:

```bash
python SPACY/analizar_oraciones.py
```

Por defecto, el programa utiliza `benchmark/corpus_fase2.csv` como archivo de entrada y genera `SPACY/analisis_spacy.txt` y `SPACY/logs/spacy.csv` como archivos de salida.

También es posible indicar rutas distintas:

```bash
python SPACY/analizar_oraciones.py mi_corpus.csv
python SPACY/analizar_oraciones.py mi_corpus.csv salida.txt salida.csv
```

El programa acepta como entrada:

- Un archivo `.csv` con una columna obligatoria llamada `oracion`.
- Un archivo `.txt` que contenga una oración por línea. Las líneas vacías se ignoran.

Al inicio del archivo de resultados se registra el nombre del corpus, la cantidad de oraciones procesadas, las versiones de spaCy y del modelo, la fecha de ejecución y el criterio aplicado.

Para cada oración, el programa presenta los datos disponibles del corpus, la decisión de los criterios C1–C2–C3, una tabla con el análisis de cada palabra y el árbol de dependencias correspondiente.

### Demostración en vivo (`demo_nlp.py`)

Con el entorno virtual activo, ejecuta desde la **carpeta raíz del repositorio**:

```bash
python SPACY/demo_nlp.py                    # recorre las oraciones elegidas, con pausa
python SPACY/demo_nlp.py --rapido           # sin pausas
python SPACY/demo_nlp.py "El niño come."    # analiza una oración cualquiera
```

Sin argumentos, la demostración recorre cinco oraciones seleccionadas del corpus. Después de cada una espera que se presione Enter; no se hace pausa tras la última oración. Con `--rapido` se muestran todas seguidas. Si se escribe una oración entre comillas, se analiza únicamente esa.

A diferencia de `analizar_oraciones.py`, la demostración no aplica el criterio C1–C2–C3, no muestra rasgos morfológicos y no genera archivos.

## Criterio de evaluación

spaCy no acepta ni rechaza oraciones por sí mismo. El equipo definió un criterio explícito basado en tres condiciones que el modelo puede verificar automáticamente a partir de los rasgos morfosintácticos que asigna.

### Condiciones

| Condición | Definición | Valores posibles |
|---|---|---|
| **C1** | Concordancia de persona y número entre el sujeto explícito (`nsubj`) y el verbo raíz. | `si` / `no` / `no_evaluable` |
| **C2** | Concordancia de género y número entre determinantes/adjetivos y el sustantivo al que modifican. | `si` / `no` / `no_evaluable` |
| **C3** | El token raíz tiene categoría gramatical verbal (`VERB` o `AUX`). Es condición necesaria. | `si` / `no` |

Un criterio produce `no_evaluable` cuando el modelo no asigna los rasgos morfológicos necesarios para realizar la comparación (por ejemplo, cuando un sustantivo carece de `Person` o `Number`). Esto no es un fallo del criterio sino una limitación de la cobertura morfológica del modelo.

### Lógica de decisión

**C3 es condición necesaria**: si C3 = `no`, la decisión es siempre `rechaza`, sin importar C1 ni C2.

| C1 | C2 | C3 | Decisión |
|---|---|---|---|
| `si` | `si` | `si` | **acepta** |
| `no` | `*` | `*` | **rechaza** |
| `*` | `no` | `*` | **rechaza** |
| `*` | `*` | `no` | **rechaza** |
| `no_evaluable` | `si` | `si` | **acepta_parcial** |
| `si` | `no_evaluable` | `si` | **acepta_parcial** |
| `no_evaluable` | `no_evaluable` | `si` | **acepta_parcial** |

Los tres valores de decisión son distintos:
- **acepta**: spaCy cumplió y pudo verificar todos los criterios.
- **acepta_parcial**: no se detectaron incumplimientos, pero no fue posible evaluar todos los criterios por falta de información morfológica.
- **rechaza**: al menos un criterio presentó un incumplimiento.

### Resultados sobre el corpus

El script se ejecutó sobre las 76 oraciones del corpus con spaCy 3.8.18 y `es_core_news_sm` 3.8.0:

| Decisión | gramatical = si (53) | gramatical = no (23) | Total |
|---|---|---|---|
| acepta | 5 | 0 | **5** |
| acepta_parcial | 46 | 14 | **60** |
| rechaza | 2 | 9 | **11** |

El alto número de `acepta_parcial` refleja que `es_core_news_sm` no asigna rasgos de persona y número a la mayoría de sustantivos y nombres propios, lo que impide evaluar C1 en esos casos. Esto es en sí mismo un hallazgo sobre la cobertura morfológica del modelo.

## Formato del corpus

### Archivo CSV

El archivo CSV debe contener una columna llamada `oracion`. Las siguientes columnas son opcionales:

| Columna | Descripción |
|---|---|
| `oracion` | Texto de la oración que será procesada. Es obligatoria. |
| `id` | Identificador de la oración. Si no se proporciona, el programa asigna uno según su posición en el archivo. |
| `nivel` | Clasificación de las oraciones según su complejidad: `1` simples, `2` intermedias, `3` complejas. |
| `gramatical` | Indica si la oración está clasificada como gramatical (`si`) o no (`no`). Este valor se muestra como información del corpus; no es una validación realizada por spaCy. |
| `fenomeno` | Fenómeno lingüístico que se busca observar en la oración. |

El programa reconoce archivos CSV separados por **comas (`,`) o punto y coma (`;`)** y contempla archivos guardados con codificación UTF-8 o Windows-1252.

### Archivo TXT

En los archivos `.txt`, cada oración debe escribirse en una línea independiente. Las líneas vacías se omiten durante la lectura.

## Fundamento del análisis con spaCy

### ¿Qué es spaCy?

spaCy es una biblioteca de Python especializada en el procesamiento del lenguaje natural. Proporciona herramientas para procesar textos y obtener información lingüística mediante modelos entrenados previamente.

En este proyecto se utiliza para analizar oraciones en español y obtener una representación estructurada de sus elementos. La biblioteca y el modelo cumplen funciones distintas: spaCy proporciona la infraestructura para ejecutar el procesamiento, mientras que `es_core_news_sm` aporta el modelo entrenado para trabajar con el idioma español.

### Modelo `es_core_news_sm`

El programa utiliza el modelo `es_core_news_sm` (versión 3.8.0), un modelo de lenguaje de spaCy entrenado para procesar textos en español. La terminación `sm` corresponde a la versión *small* (pequeña) del modelo.

El modelo aplica métodos estadísticos y representaciones aprendidas durante su entrenamiento para identificar características lingüísticas y predecir relaciones entre las palabras de una oración. Por ello, los resultados son predicciones del modelo y no reglas gramaticales definidas manualmente para cada oración.

Al procesar un texto, spaCy lo convierte en un objeto `Doc`, que contiene los tokens y la información lingüística asignada durante el procesamiento.

### Información lingüística obtenida

El script utiliza los siguientes atributos de los tokens:

| Atributo | Información que proporciona | Uso en el programa |
|---|---|---|
| `token.text` | Texto original del token. | Muestra la palabra o elemento de la oración. |
| `token.pos_` | Categoría gramatical general (*Part of Speech*). | Indica si el token es sustantivo, verbo, adjetivo, pronombre, entre otras categorías. |
| `token.dep_` | Etiqueta de la relación sintáctica de dependencia. | Identifica la función o relación del token dentro de la estructura de la oración. |
| `token.head` | Token del que depende sintácticamente el token actual. | Muestra la palabra que actúa como núcleo o elemento rector de la relación. |
| `token.morph` | Características morfológicas identificadas por el modelo. | Muestra rasgos como género, número, persona, tiempo y modo. Se usa en la verificación de C1 y C2. |
| `token.children` | Tokens que dependen directamente del token actual. | Permite recorrer las relaciones de dependencia para construir el árbol y verificar C2. |

Las etiquetas de categoría gramatical y de dependencia son etiquetas asignadas por el modelo. Por tanto, deben interpretarse como el análisis que propone spaCy y no como una clasificación necesariamente libre de errores.

### Análisis sintáctico por dependencias

El análisis sintáctico que se presenta en el reporte está basado en dependencias. En este enfoque, las palabras de una oración se relacionan entre sí mediante vínculos que indican qué elemento depende de otro.

En el árbol generado por el programa:

- Cada palabra o token se representa como un nodo.
- La etiqueta de dependencia (`dep_`) indica la relación sintáctica que el modelo asigna al token.
- El atributo `head` permite identificar el token del que depende cada palabra.
- El token cuya etiqueta de dependencia es `ROOT` se toma como raíz del árbol y es el que verifica C3.
- Los tokens hijos (`children`) permiten recorrer los elementos que dependen de cada nodo y verificar C2.

Los scripts construyen el árbol mediante la función recursiva `arbol()`. La sangría aumenta en cada llamada recursiva para representar visualmente los distintos niveles de dependencia. Los signos de puntuación se omiten en esta representación.

## Qué esperar de los resultados

- spaCy realiza un análisis lingüístico de las oraciones proporcionadas, pero **no determina por sí mismo si una oración es gramatical o agramatical**.
- El modelo intenta asignar categorías y relaciones sintácticas a los elementos del texto, incluso cuando la oración contiene construcciones inusuales o agramaticales.
- Las etiquetas y relaciones obtenidas pueden no coincidir con el análisis esperado. Por ejemplo, el modelo puede asignar una categoría gramatical o una característica morfológica incorrecta.
- El árbol de dependencias representa la estructura que predice el modelo para la oración procesada.
- Los resultados dependen del modelo y de su versión. Por ello, distintas versiones o modelos pueden producir análisis diferentes.
- En las pruebas de la demostración, la oración con ambigüedad estructural recibe una única interpretación: el modelo no señala que existe otra lectura posible.

## Limitaciones

- `es_core_news_sm` no asigna rasgos de persona y número a la mayoría de sustantivos comunes ni a nombres propios en este corpus. Esto impide evaluar C1 en la mayor parte de las oraciones y produce un alto número de decisiones `acepta_parcial`.
- C3 produce falsos negativos por errores del etiquetador POS: dos oraciones correctas (C06) e incorrectas (I22) fueron rechazadas porque el modelo etiquetó el verbo como nombre propio (`PROPN`). Estos casos se documentan como limitaciones del modelo y no se corrigen manualmente.
- `es_core_news_sm` es la versión pequeña del modelo de español; sus predicciones pueden presentar errores de etiquetado morfológico o de análisis sintáctico.
- El análisis generado depende de las predicciones del modelo y no constituye una verificación definitiva de la estructura sintáctica o de la gramaticalidad de las oraciones.