# Análisis de oraciones en español con spaCy

## Descripción del módulo

Este módulo procesa un conjunto de oraciones en español mediante **spaCy**, una biblioteca de Python para el procesamiento del lenguaje natural (*Natural Language Processing*, NLP).

A partir de un corpus de oraciones elaborado para el proyecto, el programa utiliza el modelo de español `es_core_news_sm` para obtener información lingüística de cada oración. Entre los resultados se encuentran la categoría gramatical de cada palabra, su relación sintáctica con otras palabras y distintos rasgos morfológicos.

El programa también genera una representación textual del árbol de dependencias de cada oración. De esta manera, permite observar cómo el modelo analiza la estructura sintáctica de las oraciones proporcionadas.

## Contenido

| Archivo | Descripción |
|---|---|
| `corpus_fase1.csv` | Corpus de entrada con 16 oraciones en español, elaboradas para observar distintos fenómenos lingüísticos. |
| `analizar_oraciones.py` | Lee el corpus, procesa cada oración con spaCy y guarda los resultados en un archivo de texto. |
| `demo_nlp.py` | Demostración en vivo: muestra en pantalla el análisis de spaCy de oraciones seleccionadas del corpus o de una oración escrita por el usuario. |

Los resultados generados por el programa, como `analisis_spacy.txt`, no se incluyen en el repositorio: se producen al ejecutar el script y están contemplados en `.gitignore`.

## Requisitos

- Python 3.9 o superior.
- Conexión a internet para instalar spaCy y descargar el modelo de español.
- Biblioteca spaCy.
- Modelo de lenguaje `es_core_news_sm`.

## Instalación

Desde la carpeta de este módulo, crea y activa un entorno virtual:

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Mac / Linux
source venv/bin/activate
```

Instala spaCy y descarga el modelo de español:

```bash
pip install spacy
python -m spacy download es_core_news_sm
```

El entorno virtual (`venv/`) no se sube al repositorio.

## Cómo ejecutar

Con el entorno virtual activo, ejecuta:

```bash
python analizar_oraciones.py
```

Por defecto, el programa utiliza `corpus_fase1.csv` como archivo de entrada y genera `analisis_spacy.txt` como archivo de salida.

También es posible indicar otro corpus y, opcionalmente, otro nombre para el archivo de resultados:

```bash
python analizar_oraciones.py mi_corpus.csv
python analizar_oraciones.py mi_corpus.csv salida.txt
```

El programa acepta como entrada:

- Un archivo `.csv` con una columna obligatoria llamada `oracion`.
- Un archivo `.txt` que contenga una oración por línea. Las líneas vacías se ignoran.

Al inicio del archivo de resultados se registra el nombre del corpus, la cantidad de oraciones procesadas, las versiones de spaCy y del modelo, y la fecha de ejecución.

Para cada oración, el programa presenta los datos disponibles del corpus y una tabla con el análisis de cada palabra. Finalmente, incluye el árbol de dependencias correspondiente.

### Demostración en vivo (`demo_nlp.py`)

Con el entorno virtual activo, ejecuta:

```bash
python demo_nlp.py                    # recorre las oraciones elegidas, con pausa
python demo_nlp.py --rapido           # sin pausas
python demo_nlp.py "El niño come."    # analiza una oración cualquiera
```

Sin argumentos, la demostración recorre cinco oraciones seleccionadas del corpus. Después de cada una espera que se presione Enter, lo que permite explicar cada resultado antes de continuar; no se hace pausa tras la última oración. Con la opción `--rapido` se muestran todas seguidas. Si se escribe una oración entre comillas, se analiza únicamente esa.

Para cada oración, la demostración muestra:

1. **La oración y una nota** sobre lo que se busca observar.
2. **Una tabla palabra por palabra**, con el texto, la categoría gramatical (`pos_`), la relación sintáctica (`dep_`) y el token del que depende (`head`). Los signos de puntuación se omiten.
3. **El árbol de dependencias**, construido con la misma función recursiva `arbol()` y a partir de la raíz (`ROOT`).

A diferencia de `analizar_oraciones.py`, la demostración no muestra rasgos morfológicos y no genera archivos.

## Formato del corpus

El corpus puede proporcionarse como un archivo `.csv` o `.txt`.

### Archivo CSV

El archivo CSV debe contener una columna llamada `oracion`. Las siguientes columnas son opcionales:

| Columna | Descripción |
|---|---|
| `oracion` | Texto de la oración que será procesada. Es obligatoria. |
| `id` | Identificador de la oración. Si no se proporciona, el programa asigna uno según su posición en el archivo. |
| `nivel` | Clasificación de las oraciones según su complejidad: `1` simples, `2` intermedias, `3` complejas y `A` agramaticales a propósito. |
| `gramatical` | Indica si la oración está clasificada como gramatical (`si`) o no (`no`). Este valor se muestra como información del corpus; no es una validación realizada por spaCy. |
| `fenomeno` | Fenómeno lingüístico que se busca observar en la oración. |

El programa reconoce archivos CSV separados por **comas (`,`) o punto y coma (`;`)**. También contempla archivos guardados con codificación UTF-8 o Windows-1252.

### Archivo TXT

En los archivos `.txt`, cada oración debe escribirse en una línea independiente. Las líneas vacías se omiten durante la lectura.

## Fundamento del análisis con spaCy

### ¿Qué es spaCy?

spaCy es una biblioteca de Python especializada en el procesamiento del lenguaje natural. Proporciona herramientas para procesar textos y obtener información lingüística mediante modelos entrenados previamente.

En este proyecto se utiliza para analizar oraciones en español y obtener una representación estructurada de sus elementos. La biblioteca y el modelo cumplen funciones distintas: spaCy proporciona la infraestructura para ejecutar el procesamiento, mientras que `es_core_news_sm` aporta el modelo entrenado para trabajar con el idioma español.

### Modelo `es_core_news_sm`

El programa utiliza el modelo `es_core_news_sm`, un modelo de lenguaje de spaCy entrenado para procesar textos en español. La terminación `sm` corresponde a la versión *small* (pequeña) del modelo.

El modelo aplica métodos estadísticos y representaciones aprendidas durante su entrenamiento para identificar características lingüísticas y predecir relaciones entre las palabras de una oración. Por ello, los resultados son predicciones del modelo y no reglas gramaticales definidas manualmente para cada oración.

Al procesar un texto, spaCy lo convierte en un objeto `Doc`, que contiene los tokens y la información lingüística asignada durante el procesamiento. En este proyecto, el programa consulta esa información para construir el reporte de cada oración.

### Información lingüística obtenida

El script utiliza los siguientes atributos de los tokens:

| Atributo | Información que proporciona | Uso en el programa |
|---|---|---|
| `token.text` | Texto original del token. | Muestra la palabra o elemento de la oración. |
| `token.pos_` | Categoría gramatical general (*Part of Speech*). | Indica si el token es sustantivo, verbo, adjetivo, pronombre, entre otras categorías. |
| `token.dep_` | Etiqueta de la relación sintáctica de dependencia. | Identifica la función o relación del token dentro de la estructura de la oración. |
| `token.head` | Token del que depende sintácticamente el token actual. | Muestra la palabra que actúa como núcleo o elemento rector de la relación. |
| `token.morph` | Características morfológicas identificadas por el modelo. | Muestra rasgos como género, número, persona, tiempo, modo y otros, cuando corresponda. |
| `token.children` | Tokens que dependen directamente del token actual. | Permite recorrer las relaciones de dependencia para construir el árbol. |

Las etiquetas de categoría gramatical y de dependencia son etiquetas asignadas por el modelo. Por tanto, deben interpretarse como el análisis que propone spaCy y no como una clasificación necesariamente libre de errores.

### Análisis sintáctico por dependencias

El análisis sintáctico que se presenta en el reporte está basado en dependencias. En este enfoque, las palabras de una oración se relacionan entre sí mediante vínculos que indican qué elemento depende de otro.

En el árbol generado por el programa:

- Cada palabra o token se representa como un nodo.
- La etiqueta de dependencia (`dep_`) indica la relación sintáctica que el modelo asigna al token.
- El atributo `head` permite identificar el token del que depende cada palabra.
- El token cuya etiqueta de dependencia es `ROOT` se toma como raíz del árbol.
- Los tokens hijos (`children`) permiten recorrer los elementos que dependen de cada nodo.

Los scripts `analizar_oraciones.py` y `demo_nlp.py` construyen el árbol mediante la función recursiva `arbol()`. Esta función recibe un token, muestra su texto y sus etiquetas de dependencia y categoría gramatical, y luego recorre sus hijos. La sangría aumenta en cada llamada recursiva para representar visualmente los distintos niveles de dependencia. Los signos de puntuación se omiten en esta representación.

## Qué esperar de los resultados

- spaCy realiza un análisis lingüístico de las oraciones proporcionadas, pero **no determina por sí mismo si una oración es gramatical o agramatical**.
- El modelo intenta asignar categorías y relaciones sintácticas a los elementos del texto, incluso cuando la oración contiene construcciones inusuales o agramaticales.
- Las etiquetas y relaciones obtenidas pueden no coincidir con el análisis esperado. Por ejemplo, el modelo puede asignar una categoría gramatical o una característica morfológica incorrecta.
- El árbol de dependencias representa la estructura que predice el modelo para la oración procesada.
- Los resultados dependen del modelo y de su versión. Por ello, distintas versiones o modelos pueden producir análisis diferentes.
- En las pruebas de la demostración, la oración con ambigüedad estructural recibe una única interpretación: el modelo no señala que existe otra lectura posible.
- Al analizar oraciones escritas libremente, el modelo también puede cometer errores de etiquetado. Por ejemplo, en una prueba realizada con «Los niños comen.», etiquetó «comen» como adjetivo.

## Limitaciones

- El corpus contiene 16 oraciones. Su tamaño permite observar el comportamiento del modelo ante los ejemplos seleccionados, pero no permite generalizar los resultados a todo el español ni obtener conclusiones estadísticas amplias.
- Las oraciones fueron elaboradas para el proyecto y representan un conjunto limitado de construcciones lingüísticas.
- `es_core_news_sm` es la versión pequeña del modelo de español; sus predicciones pueden presentar errores de etiquetado morfológico o de análisis sintáctico.
- El análisis generado depende de las predicciones del modelo y no constituye una verificación definitiva de la estructura sintáctica o de la gramaticalidad de las oraciones.