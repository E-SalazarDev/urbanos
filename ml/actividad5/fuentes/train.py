"""
Actividad 5 - UrbanOS ML
Entrenamiento, ajuste de hiperparámetros, evaluación y registro en MLflow.

Ejecutar desde ml/actividad5:
    python .\fuentes\train.py
"""

from __future__ import annotations

import json
import logging
import os
import platform
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import mlflow
import mlflow.sklearn
import numpy as np
import pandas as pd
import sklearn
from mlflow.models import infer_signature
from scipy.stats import wilcoxon
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    ConfusionMatrixDisplay,
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
    RocCurveDisplay,
)
from sklearn.model_selection import GridSearchCV, StratifiedKFold, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

# ---------------------------------------------------------------------
# Configuración
# ---------------------------------------------------------------------

SEMILLA = 42
TEST_SIZE = 0.20
N_SPLITS = 5
SCORING = "f1"

RUTA_DATASET = Path("datos/datos_limp/dataset_limpio.csv")
RUTA_RESULTADOS = Path("resultados")
RUTA_EVIDENCIAS = Path("evidencias") / "modelos"

MLFLOW_TRACKING_URI = os.getenv("MLFLOW_TRACKING_URI", "http://127.0.0.1:5000")
EXPERIMENTO = "UrbanOS_Actividad5_Clasificacion"

CARACTERISTICAS = [
    "rojo_media",
    "verde_media",
    "azul_media",
    "rojo_desv",
    "verde_desv",
    "azul_desv",
    "brillo_media",
    "brillo_desv",
    "contraste",
    "proporcion_oscura",
    "proporcion_clara",
    "saturacion_media",
    "densidad_bordes",
    "nitidez",
    "entropia",
    "textura_bloques",
]
OBJETIVO = "etiqueta"
ETIQUETAS = [0, 1]
NOMBRES_CLASES = ["sin_dano", "bache"]

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)
logger = logging.getLogger("urbanos_actividad5")


# ---------------------------------------------------------------------
# Utilidades
# ---------------------------------------------------------------------

def crear_directorios() -> None:
    RUTA_RESULTADOS.mkdir(parents=True, exist_ok=True)
    RUTA_EVIDENCIAS.mkdir(parents=True, exist_ok=True)


def convertir_valor_json(valor: Any) -> Any:
    """Convierte tipos NumPy/Pandas a valores serializables en JSON."""
    if isinstance(valor, dict):
        return {str(k): convertir_valor_json(v) for k, v in valor.items()}
    if isinstance(valor, (list, tuple)):
        return [convertir_valor_json(v) for v in valor]
    if isinstance(valor, np.integer):
        return int(valor)
    if isinstance(valor, np.floating):
        return float(valor)
    if isinstance(valor, np.bool_):
        return bool(valor)
    if isinstance(valor, np.ndarray):
        return valor.tolist()
    if valor is pd.NA:
        return None
    if isinstance(valor, float) and not np.isfinite(valor):
        return None
    return valor


def guardar_json(datos: dict[str, Any], ruta: Path) -> None:
    with ruta.open("w", encoding="utf-8") as archivo:
        json.dump(
            convertir_valor_json(datos),
            archivo,
            ensure_ascii=False,
            indent=2,
            allow_nan=False,
        )


def cargar_dataset() -> tuple[pd.DataFrame, pd.DataFrame, pd.Series]:
    if not RUTA_DATASET.exists():
        raise FileNotFoundError(
            f"No se encontró el dataset: {RUTA_DATASET.resolve()}\n"
            "Confirma que dataset_limpio.csv esté en datos/datos_limp/."
        )

    df = pd.read_csv(RUTA_DATASET)
    requeridas = CARACTERISTICAS + [OBJETIVO]
    faltantes = [col for col in requeridas if col not in df.columns]
    if faltantes:
        raise ValueError(
            "Faltan columnas requeridas en el dataset: " + ", ".join(faltantes)
        )

    df = df[requeridas].copy()
    if df.empty:
        raise ValueError("El dataset está vacío.")

    for columna in requeridas:
        df[columna] = pd.to_numeric(df[columna], errors="coerce")

    if df.isna().any().any():
        columnas = df.columns[df.isna().any()].tolist()
        raise ValueError(f"Hay valores nulos o no numéricos en: {columnas}")

    if not np.isfinite(df[CARACTERISTICAS].to_numpy(dtype=float)).all():
        raise ValueError("Hay valores infinitos en las características.")

    valores_objetivo = set(df[OBJETIVO].unique().tolist())
    if valores_objetivo != {0, 1}:
        raise ValueError(f"Se esperaban etiquetas 0 y 1; se encontraron: {valores_objetivo}")

    df[OBJETIVO] = df[OBJETIVO].astype(int)
    X = df[CARACTERISTICAS].astype(float)
    y = df[OBJETIVO]

    if y.value_counts().min() < N_SPLITS:
        raise ValueError(f"Cada clase necesita al menos {N_SPLITS} registros para CV.")

    logger.info("Dataset cargado: %s", RUTA_DATASET.resolve())
    logger.info("Registros: %s | Características: %s", len(df), len(CARACTERISTICAS))
    logger.info("Distribución de clases: %s", y.value_counts().sort_index().to_dict())
    return df, X, y


def configuraciones_modelos() -> dict[str, tuple[Any, dict[str, list[Any]]]]:
    regresion = Pipeline(
        steps=[
            ("escalador", StandardScaler()),
            (
                "clasificador",
                LogisticRegression(max_iter=3000, random_state=SEMILLA),
            ),
        ]
    )
    grid_regresion = {
        "clasificador__C": [0.1, 1.0, 10.0],
        "clasificador__class_weight": [None, "balanced"],
    }

    bosque = RandomForestClassifier(random_state=SEMILLA, n_jobs=1)
    grid_bosque = {
        "n_estimators": [200, 400],
        "max_depth": [None, 10, 20],
        "min_samples_split": [2, 5],
        "min_samples_leaf": [1, 2],
        "class_weight": [None, "balanced"],
    }

    return {
        "regresion_logistica": (regresion, grid_regresion),
        "random_forest": (bosque, grid_bosque),
    }


def guardar_graficas(
    nombre: str,
    y_test: pd.Series,
    predicciones: np.ndarray,
    probabilidades: np.ndarray,
    modelo: Any,
) -> dict[str, str]:
    rutas: dict[str, str] = {}

    fig, ax = plt.subplots(figsize=(6, 5))
    ConfusionMatrixDisplay(
        confusion_matrix(y_test, predicciones, labels=ETIQUETAS),
        display_labels=NOMBRES_CLASES,
    ).plot(ax=ax, cmap="Blues", colorbar=False)
    ax.set_title(f"Matriz de confusión - {nombre}")
    fig.tight_layout()
    ruta_cm = RUTA_EVIDENCIAS / f"{nombre}_matriz_confusion.png"
    fig.savefig(ruta_cm, dpi=160, bbox_inches="tight")
    plt.close(fig)
    rutas["matriz_confusion"] = str(ruta_cm)

    fig, ax = plt.subplots(figsize=(6, 5))
    RocCurveDisplay.from_predictions(
        y_test, probabilidades, name=nombre, ax=ax
    )
    ax.plot([0, 1], [0, 1], linestyle="--", label="Azar")
    ax.set_title(f"Curva ROC - {nombre}")
    ax.legend(loc="lower right")
    fig.tight_layout()
    ruta_roc = RUTA_EVIDENCIAS / f"{nombre}_curva_roc.png"
    fig.savefig(ruta_roc, dpi=160, bbox_inches="tight")
    plt.close(fig)
    rutas["curva_roc"] = str(ruta_roc)

    estimador = modelo
    if hasattr(modelo, "named_steps"):
        estimador = modelo.named_steps.get("clasificador", modelo)

    if hasattr(estimador, "feature_importances_"):
        importancia = pd.DataFrame({
            "caracteristica": CARACTERISTICAS,
            "importancia": estimador.feature_importances_,
        }).sort_values("importancia", ascending=False)
        ruta_csv = RUTA_RESULTADOS / f"{nombre}_importancia_variables.csv"
        importancia.to_csv(ruta_csv, index=False, encoding="utf-8-sig")

        fig, ax = plt.subplots(figsize=(9, 7))
        importancia.sort_values("importancia").plot(
            kind="barh", x="caracteristica", y="importancia", legend=False, ax=ax
        )
        ax.set_title(f"Importancia de características - {nombre}")
        ax.set_xlabel("Importancia")
        fig.tight_layout()
        ruta_png = RUTA_EVIDENCIAS / f"{nombre}_importancia_variables.png"
        fig.savefig(ruta_png, dpi=160, bbox_inches="tight")
        plt.close(fig)
        rutas["importancia_variables"] = str(ruta_png)
        rutas["importancia_variables_csv"] = str(ruta_csv)

    return rutas


def comparar_folds(resultados_cv: dict[str, list[float]]) -> dict[str, Any]:
    """Comparación exploratoria de F1 pareado entre los folds de ambos modelos."""
    nombres = list(resultados_cv)
    if len(nombres) != 2:
        return {
            "metodo": "No calculado: se requieren exactamente dos modelos.",
            "p_value": None,
            "interpretacion": "No se realizó una prueba estadística.",
        }

    a = np.asarray(resultados_cv[nombres[0]], dtype=float)
    b = np.asarray(resultados_cv[nombres[1]], dtype=float)
    resultado: dict[str, Any] = {
        "metrica": "F1",
        "modelos": nombres,
        "f1_por_fold": {nombres[0]: a.tolist(), nombres[1]: b.tolist()},
        "diferencias_f1_fold_1_menos_fold_2": (a - b).tolist(),
        "metodo": "Wilcoxon pareado bilateral sobre F1 por fold",
        "advertencia": (
            "Solo hay cinco folds y los mejores hiperparámetros se seleccionaron "
            "con esos folds; el resultado es exploratorio, no concluyente."
        ),
        "p_value": None,
        "interpretacion": None,
    }

    try:
        p_value = 1.0 if np.allclose(a, b) else float(wilcoxon(a, b).pvalue)
        resultado["p_value"] = p_value
        if p_value < 0.05:
            resultado["interpretacion"] = (
                "La prueba exploratoria detecta una diferencia al nivel 0.05; "
                "debe interpretarse con cautela por el tamaño pequeño de la muestra."
            )
        else:
            resultado["interpretacion"] = (
                "No se detectó una diferencia estadísticamente significativa al "
                "nivel 0.05. Esto no demuestra que los modelos sean iguales."
            )
    except (ValueError, ZeroDivisionError) as exc:
        resultado["interpretacion"] = f"No fue posible calcular Wilcoxon: {exc}"

    return resultado


# ---------------------------------------------------------------------
# Entrenamiento y evaluación
# ---------------------------------------------------------------------

def entrenar_evaluar(
    nombre: str,
    estimador: Any,
    parametros: dict[str, list[Any]],
    X_train: pd.DataFrame,
    X_test: pd.DataFrame,
    y_train: pd.Series,
    y_test: pd.Series,
) -> dict[str, Any]:
    cv = StratifiedKFold(
        n_splits=N_SPLITS, shuffle=True, random_state=SEMILLA
    )
    busqueda = GridSearchCV(
        estimator=estimador,
        param_grid=parametros,
        scoring=SCORING,
        cv=cv,
        n_jobs=-1,
        refit=True,
        return_train_score=True,
        error_score="raise",
        verbose=1,
    )

    logger.info("Iniciando búsqueda para %s", nombre)
    with mlflow.start_run(run_name=nombre) as run:
        mlflow.set_tags({
            "proyecto": "UrbanOS",
            "actividad": "Actividad 5",
            "algoritmo": nombre,
            "tipo_problema": "clasificacion_binaria",
            "semilla": str(SEMILLA),
            "version_sklearn": sklearn.__version__,
            "version_python": platform.python_version(),
        })
        mlflow.log_params({
            "semilla": SEMILLA,
            "test_size": TEST_SIZE,
            "cv_folds": N_SPLITS,
            "scoring": SCORING,
            "dataset": RUTA_DATASET.as_posix(),
            "n_registros_total": len(X_train) + len(X_test),
            "n_registros_train": len(X_train),
            "n_registros_test": len(X_test),
            "n_caracteristicas": X_train.shape[1],
            "version_python": platform.python_version(),
            "version_sklearn": sklearn.__version__,
            "version_pandas": pd.__version__,
            "version_numpy": np.__version__,
        })

        busqueda.fit(X_train, y_train)
        mejor_modelo = busqueda.best_estimator_
        predicciones = mejor_modelo.predict(X_test)
        probabilidades = mejor_modelo.predict_proba(X_test)[:, 1]

        mejor_indice = busqueda.best_index_
        metricas = {
            "accuracy": float(accuracy_score(y_test, predicciones)),
            "precision": float(precision_score(y_test, predicciones, zero_division=0)),
            "recall": float(recall_score(y_test, predicciones, zero_division=0)),
            "f1": float(f1_score(y_test, predicciones, zero_division=0)),
            "roc_auc": float(roc_auc_score(y_test, probabilidades)),
            "cv_f1_media": float(busqueda.best_score_),
            "cv_f1_std": float(busqueda.cv_results_["std_test_score"][mejor_indice]),
            "cv_f1_train_media": float(
                busqueda.cv_results_["mean_train_score"][mejor_indice]
            ),
        }
        mlflow.log_metrics(metricas)

        parametros_ganadores = {
            str(k): convertir_valor_json(v)
            for k, v in busqueda.best_params_.items()
        }
        mlflow.log_params({f"mejor_{k}": str(v) for k, v in parametros_ganadores.items()})

        resultados_grid = pd.DataFrame(busqueda.cv_results_)
        columnas_grid = [
            col for col in resultados_grid.columns
            if col.startswith("param_") or col in {
                "mean_test_score", "std_test_score", "rank_test_score",
                "mean_train_score", "std_train_score", "mean_fit_time", "std_fit_time",
            }
        ]
        ruta_grid = RUTA_RESULTADOS / f"{nombre}_resultados_cv.csv"
        resultados_grid[columnas_grid].to_csv(
            ruta_grid, index=False, encoding="utf-8-sig"
        )
        mlflow.log_artifact(str(ruta_grid), artifact_path="validacion_cruzada")

        reporte_clasificacion = classification_report(
            y_test, predicciones, labels=ETIQUETAS,
            target_names=NOMBRES_CLASES, output_dict=True, zero_division=0,
        )
        ruta_reporte_clases = RUTA_RESULTADOS / f"{nombre}_classification_report.csv"
        pd.DataFrame(reporte_clasificacion).transpose().to_csv(
            ruta_reporte_clases, encoding="utf-8-sig"
        )
        mlflow.log_artifact(str(ruta_reporte_clases), artifact_path="reportes")

        predicciones_df = pd.DataFrame({
            "indice_original": y_test.index,
            "etiqueta_real": y_test.to_numpy(),
            "etiqueta_predicha": predicciones,
            "probabilidad_bache": probabilidades,
            "acierto": y_test.to_numpy() == predicciones,
        })
        ruta_predicciones = RUTA_RESULTADOS / f"{nombre}_predicciones_test.csv"
        predicciones_df.to_csv(ruta_predicciones, index=False, encoding="utf-8-sig")
        mlflow.log_artifact(str(ruta_predicciones), artifact_path="predicciones")

        matriz = confusion_matrix(y_test, predicciones, labels=ETIQUETAS)
        matriz_df = pd.DataFrame(
            matriz,
            index=[f"real_{x}" for x in NOMBRES_CLASES],
            columns=[f"predicho_{x}" for x in NOMBRES_CLASES],
        )
        ruta_matriz_csv = RUTA_RESULTADOS / f"{nombre}_matriz_confusion.csv"
        matriz_df.to_csv(ruta_matriz_csv, encoding="utf-8-sig")
        mlflow.log_artifact(str(ruta_matriz_csv), artifact_path="evaluacion")

        rutas_graficas = guardar_graficas(
            nombre, y_test, predicciones, probabilidades, mejor_modelo
        )
        for ruta in rutas_graficas.values():
            mlflow.log_artifact(ruta, artifact_path="graficas")

        firma = infer_signature(
            X_train.head(5), mejor_modelo.predict(X_train.head(5))
        )

        # Random Forest usa internamente sklearn.tree._tree.Tree.
        # Se autoriza únicamente ese tipo concreto para el modelo entrenado aquí.
        tipos_confiables = (
            ["sklearn.tree._tree.Tree"]
            if nombre == "random_forest"
            else []
        )
        mlflow.sklearn.log_model(
            sk_model=mejor_modelo,
            name="modelo",
            signature=firma,
            input_example=X_train.head(3),
            skops_trusted_types=tipos_confiables,
        )

        reporte = {
            "modelo": nombre,
            "run_id": run.info.run_id,
            "fecha_utc": datetime.now(timezone.utc).isoformat(),
            "dataset": RUTA_DATASET.as_posix(),
            "n_registros_total": int(len(X_train) + len(X_test)),
            "n_train": int(len(X_train)),
            "n_test": int(len(X_test)),
            "n_caracteristicas": int(X_train.shape[1]),
            "semilla": SEMILLA,
            "test_size": TEST_SIZE,
            "validacion_cruzada": {
                "tipo": "StratifiedKFold",
                "n_splits": N_SPLITS,
                "criterio_busqueda": SCORING,
                "f1_media_mejor_configuracion": metricas["cv_f1_media"],
                "f1_desviacion_estandar": metricas["cv_f1_std"],
                "f1_media_train_mejor_configuracion": metricas["cv_f1_train_media"],
            },
            "mejores_hiperparametros": parametros_ganadores,
            "metricas_test": metricas,
            "matriz_confusion": matriz.tolist(),
            "classification_report": reporte_clasificacion,
            "artefactos": {
                "resultados_cv": str(ruta_grid),
                "reporte_clasificacion": str(ruta_reporte_clases),
                "predicciones_test": str(ruta_predicciones),
                "matriz_confusion_csv": str(ruta_matriz_csv),
                **rutas_graficas,
            },
        }
        ruta_reporte_json = RUTA_RESULTADOS / f"{nombre}_reporte.json"
        guardar_json(reporte, ruta_reporte_json)
        mlflow.log_artifact(str(ruta_reporte_json), artifact_path="reportes")

        logger.info(
            "%s | F1 test=%.4f | ROC-AUC=%.4f | CV F1=%.4f ± %.4f",
            nombre, metricas["f1"], metricas["roc_auc"],
            metricas["cv_f1_media"], metricas["cv_f1_std"],
        )

        return {
            "modelo": nombre,
            "run_id": run.info.run_id,
            "mejor_modelo": mejor_modelo,
            "mejores_hiperparametros": parametros_ganadores,
            "metricas": metricas,
            "f1_por_fold": [
                float(busqueda.cv_results_[f"split{i}_test_score"][mejor_indice])
                for i in range(N_SPLITS)
            ],
        }


def main() -> None:
    crear_directorios()
    mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
    mlflow.set_experiment(EXPERIMENTO)

    logger.info("Tracking URI MLflow: %s", mlflow.get_tracking_uri())
    logger.info("Experimento: %s", EXPERIMENTO)

    _, X, y = cargar_dataset()
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=TEST_SIZE, random_state=SEMILLA, stratify=y
    )

    resultados = []
    for nombre, (estimador, parametros) in configuraciones_modelos().items():
        resultados.append(
            entrenar_evaluar(
                nombre, estimador, parametros, X_train, X_test, y_train, y_test
            )
        )

    filas_comparativas = []
    folds: dict[str, list[float]] = {}
    for resultado in resultados:
        filas_comparativas.append({
            "modelo": resultado["modelo"],
            "run_id": resultado["run_id"],
            **resultado["metricas"],
            "mejores_hiperparametros": json.dumps(
                resultado["mejores_hiperparametros"], ensure_ascii=False
            ),
        })
        folds[resultado["modelo"]] = resultado["f1_por_fold"]

    comparativo = pd.DataFrame(filas_comparativas).sort_values(
        by="f1", ascending=False
    )
    ruta_comparativo = RUTA_RESULTADOS / "comparativo_modelos.csv"
    comparativo.to_csv(ruta_comparativo, index=False, encoding="utf-8-sig")

    comparacion_estadistica = comparar_folds(folds)
    ruta_estadistica = RUTA_RESULTADOS / "comparacion_estadistica.json"
    guardar_json(comparacion_estadistica, ruta_estadistica)

    with mlflow.start_run(run_name="comparacion_final"):
        mlflow.set_tags({
            "proyecto": "UrbanOS",
            "actividad": "Actividad 5",
            "tipo_registro": "comparacion_modelos",
        })
        mlflow.log_artifact(str(ruta_comparativo), artifact_path="comparacion")
        mlflow.log_artifact(str(ruta_estadistica), artifact_path="comparacion")
        if comparacion_estadistica.get("p_value") is not None:
            mlflow.log_metric(
                "wilcoxon_p_value", float(comparacion_estadistica["p_value"])
            )

        metricas_grafica = [
            "accuracy", "precision", "recall", "f1", "roc_auc", "cv_f1_media"
        ]
        ax = comparativo.set_index("modelo")[metricas_grafica].plot(
            kind="bar", figsize=(11, 6), ylim=(0, 1.05)
        )
        ax.set_title("Comparación de modelos UrbanOS")
        ax.set_ylabel("Puntuación")
        ax.set_xlabel("Modelo")
        ax.tick_params(axis="x", rotation=0)
        ax.legend(loc="lower right")
        plt.tight_layout()
        ruta_grafica = RUTA_EVIDENCIAS / "comparativo_metricas.png"
        plt.savefig(ruta_grafica, dpi=160, bbox_inches="tight")
        plt.close()
        mlflow.log_artifact(str(ruta_grafica), artifact_path="comparacion")

    logger.info("Comparativo guardado en: %s", ruta_comparativo.resolve())
    logger.info("Comparación estadística guardada en: %s", ruta_estadistica.resolve())
    logger.info("Resultados finales:\n%s", comparativo.to_string(index=False))
    logger.info("Entrenamiento terminado correctamente.")


if __name__ == "__main__":
    try:
        main()
    except Exception:
        logger.exception("El entrenamiento terminó con un error.")
        sys.exit(1)
