# Actividad 5 — Entrenamiento, ajuste y registro de modelos con MLflow

Parte de **UrbanOS**, una plataforma municipal que usa datos e inteligencia artificial para apoyar el cuidado de las calles. Esta actividad pertenece a la materia *Gestión de proyectos de inteligencia artificial* (Tecmilenio) y vive en `ml/actividad5` del repositorio.

## 1. Descripción

**Problema:** clasificación binaria de imágenes de calles.

* Clase positiva (`etiqueta = 1`): `bache`.
* Clase negativa (`etiqueta = 0`): `sin_dano`.
* Criterio principal: reducir los falsos negativos (baches reales que el modelo no detecta), sin dejar de reportar accuracy, precision, recall, F1 y ROC-AUC.

En la Actividad 4 se compararon modelos preentrenados de Hugging Face directamente sobre las imágenes. Aquí se parte de las mismas imágenes, pero se extraen **16 características tabulares** (color, brillo, contraste, bordes, nitidez y textura) y se comparan dos algoritmos clásicos con ajuste sistemático de hiperparámetros:

| Algoritmo | Candidatos en la búsqueda | Validación |
| --- | --- | --- |
| Regresión logística | 6 | `GridSearchCV`, validación cruzada estratificada de 5 folds |
| Random Forest | 48 | `GridSearchCV`, validación cruzada estratificada de 5 folds |

Todos los parámetros, métricas, modelos y artefactos se registran en **MLflow** (experimento `UrbanOS_Actividad5_Clasificacion`).

## 2. Estructura

```text
actividad5/
├── datos/
│   ├── datos_ini/
│   │   └── dataset_original.csv        # inventario de las 681 imágenes originales con sus características
│   └── datos_limp/
│       ├── dataset_limpio.csv          # 668 registros listos para entrenar
│       ├── diccionario_datos.csv       # descripción de cada campo
│       ├── filas_eliminadas.csv        # registros descartados y motivo
│       └── version.json                # versión del dataset, hash SHA-256 y reglas aplicadas
├── fuentes/
│   ├── datos_prep.py                   # funciones de limpieza, versionado y gráficas exploratorias
│   ├── train.py                        # entrenamiento, ajuste, evaluación y registro en MLflow
│   └── entrena.ipynb                   # notebook: exploración, evaluación y comparación (no reentrena por defecto)
├── evidencias/
│   ├── graficas/                       # análisis exploratorio (7 figuras)
│   ├── modelos/                        # matrices de confusión, curvas ROC, importancia y comparativo
│   └── mlflow/                         # capturas del panel de MLflow
├── resultados/                         # CSV y JSON generados por train.py
├── requirements.txt
├── README.md
└── CHANGELOG.md
```

`mlflow.db` y `mlartifacts/` se generan localmente y **no se versionan** (están en el `.gitignore` de la raíz del repositorio).

## 3. Dataset

| Campo | Valor |
| --- | --- |
| Nombre | Pothole Detection Dataset |
| Autor indicado en Kaggle | Atulya Kumar |
| Fuente | https://www.kaggle.com/datasets/atulyakumar98/pothole-detection-dataset |
| Licencia indicada por la fuente | CC0: Public Domain |
| Fecha de descarga | 10 de octubre de 2026 |
| Contenido | 681 imágenes: 352 `normal` (calles sin daño) y 329 `potholes` (baches) |

Según el autor, las imágenes se tomaron de internet para un proyecto universitario. Aunque el dataset se publica como dominio público, no se verificaron los derechos originales de cada fotografía.

**Las imágenes no se incluyen en el repositorio.** Se versiona el inventario con las características extraídas de cada imagen (`datos_ini/dataset_original.csv`). Quien quiera regenerarlo debe descargar el dataset desde Kaggle (ver sección 5.1).

### Limpieza y versionado (`fuentes/datos_prep.py`)

| Regla | Criterio | Registros afectados |
| --- | --- | --- |
| Duplicados exactos | mismo `md5` | 5 eliminados |
| Casi duplicados | huella perceptual dHash de 64 bits, distancia de Hamming ≤ 4 | 8 eliminados |
| Imágenes inválidas o muy pequeñas | lado mínimo de 64 px y relación de aspecto máxima de 4.0 | 0 (ninguna incumplió la regla) |
| Valores atípicos | 1.5 × rango intercuartil | se **marcan** en `n_variables_atipicas`, no se eliminan |

Resultado: **681 → 668 registros** (341 `sin_dano` y 327 `bache`). La versión del dataset limpio es `v1-71d200e2` (SHA-256 completo en `datos/datos_limp/version.json`). Cada registro descartado se conserva en `filas_eliminadas.csv` con su motivo.

El diccionario de datos completo está en `datos/datos_limp/diccionario_datos.csv`.

## 4. Requisitos e instalación

Probado con Python 3.11.9 en Windows. Desde la carpeta `ml/actividad5`:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

`requirements.txt` conserva las dependencias de la Actividad 4 (incluidas `torch` y `transformers`) y agrega al final, en una sección marcada, las de esta actividad (`mlflow`, `ipykernel`, `nbformat`). Esta actividad solo necesita numpy, pandas, scipy, scikit-learn, matplotlib, Pillow, mlflow, ipykernel y nbformat.

## 5. Ejecución

### 5.1 Preparación de datos (opcional)

Los datos limpios ya están en el repositorio. Para regenerarlos, descargar el dataset desde Kaggle y colocar `dataset.zip` (o las carpetas `normal/` y `potholes/`) en `ml/data/raw/`. Luego, desde `ml/actividad5`:

```powershell
python .\fuentes\datos_prep.py --imagenes ..\data\raw --salida datos --graficas evidencias\graficas
```

El script reescribe `datos/` y `evidencias/graficas/`.

### 5.2 Servidor de MLflow

El servidor corre en Docker (imagen `ghcr.io/mlflow/mlflow:v3.17.1`, contenedor `urbanos-mlflow`) como el servicio `mlflow` de `infra/docker-compose.yml`. El servicio monta `ml/actividad5` en `/mlflow`, por eso `mlflow.db` y `mlartifacts/` aparecen en esta carpeta. Desde la carpeta `infra` del repositorio:

```powershell
docker compose up -d mlflow
docker ps
```

(Sin indicar el servicio, `docker compose up -d` también levanta la base de datos PostGIS y requiere el archivo `.env`.) La interfaz queda en http://127.0.0.1:5000. `train.py` usa esa dirección por defecto; se puede cambiar con la variable de entorno `MLFLOW_TRACKING_URI`.

### 5.3 Entrenamiento y evaluación

Con el servidor activo:

```powershell
python .\fuentes\train.py
```

Tarda poco más de un minuto. Crea tres ejecuciones en MLflow (`regresion_logistica`, `random_forest` y `comparacion_final`) y genera los archivos de `resultados/` y `evidencias/modelos/`.

### 5.4 Notebook

Abrir `fuentes/entrena.ipynb` en VS Code o Jupyter, elegir el intérprete del entorno `.venv` y ejecutar las celdas en orden. El notebook lee los datos, los resultados y las ejecuciones de MLflow; **no reentrena** salvo que se cambie `REENTRENAR = True` en la primera celda.

## 6. Diseño experimental

* Partición entrenamiento/prueba estratificada: 534 / 134 registros (`TEST_SIZE = 0.20`), con semilla 42.
* Búsqueda de hiperparámetros solo con el conjunto de entrenamiento; el conjunto de prueba se evalúa una vez.
* Validación cruzada estratificada de 5 folds (con mezcla y semilla 42) dentro de `GridSearchCV`.
* Criterio de selección: F1 (`scoring = "f1"`), por ser un equilibrio entre precision y recall en clases casi balanceadas. Con `refit = True`, el mejor candidato se reentrena con todo el conjunto de entrenamiento.
* Preprocesamiento: la regresión logística va en un `Pipeline` con `StandardScaler`; Random Forest no necesita escalado.
* Espacios de búsqueda:
  * Regresión logística (6 candidatos): `C` ∈ {0.1, 1.0, 10.0} y `class_weight` ∈ {`None`, `"balanced"`}.
  * Random Forest (48 candidatos): `n_estimators` ∈ {200, 400}, `max_depth` ∈ {`None`, 10, 20}, `min_samples_split` ∈ {2, 5}, `min_samples_leaf` ∈ {1, 2} y `class_weight` ∈ {`None`, `"balanced"`}.
* `class_weight` forma parte de la búsqueda de hiperparámetros en ambos modelos.
* Mejores hiperparámetros:
  * Regresión logística: `C = 1.0`, `class_weight = "balanced"`.
  * Random Forest: `n_estimators = 400`, `max_depth = 10`, `min_samples_split = 5`, `min_samples_leaf = 1`, `class_weight = "balanced"`.

## 7. Resultados

Conjunto de prueba (134 imágenes: 68 `sin_dano` y 66 `bache`):

| Modelo | Accuracy | Precision | Recall | F1 | ROC-AUC |
| --- | --- | --- | --- | --- | --- |
| Regresión logística | 0.9328 | 0.9130 | 0.9545 | 0.9333 | 0.9615 |
| Random Forest | 0.9179 | 0.8986 | 0.9394 | 0.9185 | 0.9599 |

Matrices de confusión:

| Modelo | Verdaderos negativos | Falsas alarmas | Baches no detectados | Verdaderos positivos |
| --- | --- | --- | --- | --- |
| Regresión logística | 62 | 6 | 3 | 63 |
| Random Forest | 61 | 7 | 4 | 62 |

Validación cruzada (F1, 5 folds):

| Modelo | F1 validación (media ± desv.) | F1 entrenamiento (media) | Brecha |
| --- | --- | --- | --- |
| Regresión logística | 0.9206 ± 0.0175 | 0.9191 | −0.0014 |
| Random Forest | 0.8718 ± 0.0436 | 0.9962 | 0.1243 |

Comparación estadística (`resultados/comparacion_estadistica.json`): prueba de Wilcoxon pareada bilateral sobre el F1 por fold, **p = 0.0625**. La regresión logística superó al Random Forest en los cinco folds, pero con solo cinco observaciones el valor p más pequeño posible en esta prueba es 0.0625, por lo que nunca podría alcanzar 0.05. El resultado es exploratorio y no concluyente.

## 8. Interpretación

* La regresión logística obtuvo mejores métricas y una validación cruzada más estable (desviación de 0.0175 frente a 0.0436).
* Random Forest muestra una brecha de 0.12 entre el F1 de entrenamiento y el de validación, señal de **posible sobreajuste**: memoriza bien el entrenamiento, pero generaliza peor.
* La variable más importante en Random Forest es `saturacion_media` (0.37), seguida de `azul_desv` (0.14). Una dependencia tan marcada de una variable de color conviene validarla con fotos de otras fuentes, porque puede reflejar diferencias entre los orígenes de las imágenes y no solo la presencia de baches.
* Las características tabulares simples quedan por debajo de los modelos preentrenados de la Actividad 4, que sobre imágenes alcanzaron entre 96 % y 99 % de accuracy con otra partición de datos. Las cifras no son estrictamente comparables, pero sirven de referencia.

## 9. Registro en MLflow

Cada ejecución registra:

* **Parámetros:** mejores hiperparámetros y configuración del experimento.
* **Métricas:** accuracy, precision, recall, F1 y ROC-AUC de prueba, y F1 medio y desviación de la validación cruzada.
* **Modelo:** el modelo entrenado.
* **Artefactos:** `validacion_cruzada/` (resultados del grid), `reportes/`, `predicciones/`, `evaluacion/` (matriz de confusión), `graficas/` y `comparacion/`.

Capturas del panel en `evidencias/mlflow/`.

## 10. Limitaciones y deuda técnica

* Dataset pequeño (668 registros) y fotos de internet, sin validar con imágenes de calles de México.
* Posibles imágenes parecidas entre entrenamiento y prueba que los umbrales de duplicados no detecten.
* Solo cinco folds: la comparación estadística tiene poco poder.
* MLflow local con SQLite: no apto para trabajo en equipo ni para producción.
* Las imágenes no están versionadas (solo sus características); falta una herramienta de versionado de datos como DVC.
* Entorno compartido con otros proyectos: MLflow detectó `torch` instalado aunque esta actividad no lo usa. Se recomienda un entorno aislado; `requirements.txt` separa las dependencias heredadas de la Actividad 4 de las agregadas en esta actividad.
* No hay pruebas automáticas ni integración continua.
* Próximos pasos con enfoque MLOps: versionar datos, registrar el modelo elegido en el *Model Registry*, automatizar el entrenamiento y monitorear el desempeño con fotos reales.

## 11. Créditos

Dataset: Atulya Kumar (Kaggle, CC0). Proyecto: José Eduardo Salazar Tecuapacho. Profesora: Tania Judith Mendoza Torres.

