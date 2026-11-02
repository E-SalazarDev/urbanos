# Changelog — Actividad 5 (UrbanOS ML)

Formato basado en [Keep a Changelog](https://keepachangelog.com/es-ES/1.1.0/). Este archivo funciona también como reporte final de la actividad.

## [1.0.0] - 2026-10-18

### Agregado
- `README.md` con descripción, estructura, instalación, ejecución, resultados y limitaciones.
- `fuentes/entrena.ipynb`: notebook de exploración, evaluación y comparación que lee los resultados existentes y las ejecuciones de MLflow sin reentrenar.
- `requirements.txt`: conserva las dependencias de la Actividad 4 y agrega, en una sección separada, las de esta actividad (`mlflow`, `ipykernel`, `nbformat`).
- Capturas del panel de MLflow en `evidencias/mlflow/`.

### Cambiado
- `infra/docker-compose.yml`: el servicio `mlflow` (imagen `ghcr.io/mlflow/mlflow:v3.17.1`) monta `ml/actividad5` en `/mlflow`, de donde salen `mlflow.db` y `mlartifacts/`.
- El `.gitignore` de la raíz excluye `ml/actividad5/mlflow.db`, `ml/actividad5/mlartifacts/` y `ml/actividad5/mlruns/`.

## [0.2.0] - 2026-10-18

### Agregado
- `fuentes/train.py`: entrenamiento de regresión logística y Random Forest con `GridSearchCV` (validación cruzada estratificada de 5 folds, criterio F1, semilla 42, 20 % de prueba; 6 y 48 candidatos).
- Evaluación en prueba con accuracy, precision, recall, F1 y ROC-AUC.
- Registro en MLflow (experimento `UrbanOS_Actividad5_Clasificacion`): parámetros, métricas, modelos y artefactos de cada algoritmo, más una ejecución `comparacion_final`.
- Comparación estadística por fold (Wilcoxon pareada): p = 0.0625, resultado exploratorio.
- Salidas en `resultados/` (reportes, matrices de confusión, predicciones, resultados de la validación cruzada, comparativo) y en `evidencias/modelos/` (matrices, curvas ROC, importancia de variables y comparativo de métricas).

### Resultados
- Regresión logística: F1 de prueba 0.9333, ROC-AUC 0.9615, F1 de validación cruzada 0.9206 ± 0.0175.
- Random Forest: F1 de prueba 0.9185, ROC-AUC 0.9599, F1 de validación cruzada 0.8718 ± 0.0436, con F1 de entrenamiento de 0.9962 (posible sobreajuste).

## [0.1.0] - 2026-10-17

### Agregado
- `fuentes/datos_prep.py`: inventario de imágenes, extracción de 16 características, limpieza, marcado de atípicos, versionado y gráficas exploratorias.
- Dataset original (`datos/datos_ini/dataset_original.csv`, 681 registros) y limpio (`datos/datos_limp/dataset_limpio.csv`, 668 registros), con diccionario de datos, `filas_eliminadas.csv` y `version.json`.
- Siete gráficas de exploración en `evidencias/graficas/`.

### Cambiado
- Limpieza: se eliminaron 5 duplicados exactos (`md5`) y 8 casi duplicados (dHash, distancia de Hamming ≤ 4). En la Actividad 4 solo se habían eliminado los duplicados exactos.
- Versión del dataset limpio: `v1-71d200e2`.

## Resumen final

| Aspecto | Resultado |
| --- | --- |
| Dataset | Pothole Detection Dataset (Kaggle, CC0), 681 → 668 registros, 16 características |
| Mejor modelo | Regresión logística (`C = 1.0`, `class_weight = "balanced"`) |
| Comparación | Mejor en los 5 folds; Wilcoxon p = 0.0625, no concluyente con 5 folds |
| Riesgo principal | Sobreajuste de Random Forest (brecha de 0.12 en F1) |

### Deuda técnica y acciones MLOps pendientes
- Versionar datos con DVC o similar (las imágenes no están en el repositorio).
- Pasar MLflow de SQLite local a un servidor compartido y registrar el modelo elegido en el *Model Registry*.
- Aislar el entorno: MLflow detectó `torch` sin que la actividad lo use.
- Añadir pruebas automáticas e integración continua.
- Ampliar el conjunto de datos con fotos propias de calles y validar la dependencia del modelo en `saturacion_media`.
