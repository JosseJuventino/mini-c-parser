# Cómo ejecutar todas las pruebas

Esta guía reúne las pruebas unitarias de ambas fases y los scripts del benchmark. Todos los comandos son para PowerShell en Windows. Cada bloque indica desde qué carpeta se ejecuta.

## 1. Preparar el entorno

Desde la raíz del repositorio:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Las pruebas unitarias usan `unittest`, que viene con Python, así que no hace falta instalar pytest. Las dependencias solo se necesitan para las gráficas y para volver a correr spaCy, NLTK y Gemini.

## 2. Pruebas unitarias

| Suite | Carpeta | Pruebas |
|---|---|---|
| Parser de C (Fase 1) | `Fase 1/c-parser` | 76 |
| Parser de C dentro de `esp-parser` | `esp-parser` | 18 |
| Parser del español | `esp-parser` | 63 |

### Parser de C, Fase 1

```powershell
cd "Fase 1/c-parser"
python -m unittest discover -s tests -v
cd ../..
```

### Parser de C en `esp-parser`

`src/parser.py` importa `lexer` sin el prefijo `src.`, por eso la carpeta `src` debe estar en `PYTHONPATH`:

```powershell
cd esp-parser
$env:PYTHONPATH = "src"
python -m unittest discover -s tests/test_c -v
Remove-Item Env:PYTHONPATH
cd ..
```

### Parser del español

```powershell
cd esp-parser
python -m unittest discover -s tests/test_esp -v
cd ..
```

Cada suite termina con `OK` cuando todas las pruebas pasan.

## 3. Benchmark de la Fase 2

Desde la raíz, en este orden:

```powershell
python benchmark/normalizar_llm.py
python benchmark/evaluar.py
python benchmark/analizar_errores.py
python benchmark/graficar.py
```

| Script | Qué genera |
|---|---|
| `normalizar_llm.py` | `LLM/gemini_zero_shot.csv` y `LLM/gemini_few_shot.csv` a partir de los TXT de Gemini |
| `evaluar.py` | `benchmark/resultados/metricas_comparativas.csv` |
| `analizar_errores.py` | `benchmark/resultados/errores_detallados.csv`, con cada falso positivo y falso negativo por enfoque y criterio |
| `graficar.py` | Las gráficas en `benchmark/resultados/graficas/` |

Los tres primeros solo usan la biblioteca estándar. `graficar.py` necesita matplotlib.

`normalizar_llm.py` puede mostrar el aviso `índice 38 repetido con la misma decisión`. Es esperado: Gemini repitió esa línea en su respuesta y el script la descarta.

## 4. Regenerar los registros de cada enfoque

Estos comandos sobrescriben los archivos de salida que se usan en el benchmark. Conviene correrlos en una copia del repositorio y después repetir la sección 3.

```powershell
python esp-parser/src/logEsp.py
python SPACY/analizar_oraciones.py
python NLTK/correr_nltk.py
```

NLTK descarga el corpus `cess_esp` la primera vez.

Para Gemini se necesita la variable `GEMINI_API_KEY`:

```powershell
$env:GEMINI_API_KEY = "<tu-clave>"
python LLM/llm.py
```

Los TXT nuevos quedan en `LLM/` con la fecha y hora en el nombre. Para evaluarlos, páselos al normalizador:

```powershell
python benchmark/normalizar_llm.py --zero-shot LLM/<archivo_zero_shot>.txt --few-shot LLM/<archivo_few_shot>.txt
```
