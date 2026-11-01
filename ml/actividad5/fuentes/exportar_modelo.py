"""Exporta el modelo ganador registrado en MLflow a un archivo .joblib para el servicio de IA.

Guarda junto al modelo un archivo JSON con su ficha técnica: columnas de entrada en orden,
métricas, versiones de las librerías, versión del dataset y rangos de entrenamiento.

Uso, desde la carpeta ml/actividad5:
    python fuentes/exportar_modelo.py --carpeta-modelo mlartifacts/models/<m-...>/artifacts \
        --reporte <ruta>/regresion_logistica_reporte.json --salida ../../ai-service/modelos
"""
import argparse
import hashlib
import json
import platform
from datetime import datetime, timezone
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import sklearn
from skops.io import get_untrusted_types, load

NOMBRE = "clasificador_baches"
UMBRAL = 0.5


def cargar_modelo_mlflow(carpeta):
    """Carga el modelo guardado por MLflow en formato skops (archivo propio, por eso se confía en sus tipos)."""
    archivo = Path(carpeta) / "model.skops"
    if not archivo.exists():
        raise FileNotFoundError(f"No se encontró {archivo}. Revisa la ruta de --carpeta-modelo.")
    tipos = get_untrusted_types(file=archivo)
    if tipos:
        print("Tipos que skops no confía por defecto (se aceptan porque el archivo es propio):", tipos)
    return load(archivo, trusted=tipos)


def sha256(ruta):
    return hashlib.sha256(Path(ruta).read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description="Exporta el modelo ganador a joblib.")
    parser.add_argument("--carpeta-modelo", required=True, help="Carpeta artifacts del modelo en mlartifacts.")
    parser.add_argument("--datos", default="datos/datos_limp/dataset_limpio.csv")
    parser.add_argument("--reporte", default=None, help="JSON de reporte de la corrida (para copiar las métricas).")
    parser.add_argument("--salida", default="../../ai-service/modelos")
    args = parser.parse_args()

    modelo = cargar_modelo_mlflow(args.carpeta_modelo)
    columnas = [str(c) for c in modelo.feature_names_in_]

    datos = Path(args.datos)
    df = pd.read_csv(datos)
    version = json.loads((datos.parent / "version.json").read_text(encoding="utf-8"))
    X = df[columnas]
    rangos = {
        c: {
            "min": float(X[c].min()), "p01": float(X[c].quantile(0.01)),
            "p99": float(X[c].quantile(0.99)), "max": float(X[c].max()),
        }
        for c in columnas
    }

    salida = Path(args.salida)
    salida.mkdir(parents=True, exist_ok=True)
    archivo_modelo = salida / f"{NOMBRE}.joblib"
    joblib.dump(modelo, archivo_modelo, compress=3)

    metricas = None
    if args.reporte:
        reporte = json.loads(Path(args.reporte).read_text(encoding="utf-8"))
        metricas = reporte.get("metricas_test")

    ficha = {
        "nombre": NOMBRE,
        "version": version["version"],
        "algoritmo": "regresion_logistica",
        "tarea": "clasificacion binaria: ¿la foto muestra un bache?",
        "umbral": UMBRAL,
        "columnas_entrada": columnas,
        "metricas_prueba": metricas,
        "dataset": {"version": version["version"], "sha256": version["sha256"], "filas": int(len(df))},
        "rangos_entrenamiento": rangos,
        "entorno_exportacion": {
            "python": platform.python_version(),
            "scikit_learn": sklearn.__version__,
            "numpy": np.__version__,
        },
        "exportado_en": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "sha256_modelo": sha256(archivo_modelo),
    }
    (salida / f"{NOMBRE}.json").write_text(json.dumps(ficha, indent=2, ensure_ascii=False), encoding="utf-8")

    print(f"Modelo exportado: {archivo_modelo} ({archivo_modelo.stat().st_size / 1024:.1f} KB)")
    print(f"Columnas de entrada ({len(columnas)}): {columnas}")
    print(f"Versión del dataset: {version['version']}")


if __name__ == "__main__":
    main()