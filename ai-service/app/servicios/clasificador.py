import json
import warnings
from pathlib import Path

import joblib
import numpy as np

from .caracteristicas import calcular_caracteristicas

ADVERTENCIA_RANGO = (
    "La foto es muy distinta a las usadas para entrenar el modelo; el resultado puede no ser confiable."
)
MINIMO_FUERA_DE_RANGO = 3


class ClasificadorBaches:
    simulado = False
    listo = True

    def __init__(self, modelo, ficha):
        self.modelo = modelo
        self.ficha = ficha
        self.nombre = ficha["nombre"]
        self.version = ficha["version"]
        self.umbral = float(ficha["umbral"])
        self.columnas = list(ficha["columnas_entrada"])
        self.rangos = ficha["rangos_entrenamiento"]

    @classmethod
    def cargar(cls, ruta_modelo):
        """Carga el modelo (.joblib) y su ficha (.json, junto al modelo con el mismo nombre)."""
        ruta = Path(ruta_modelo)
        ruta_ficha = ruta.with_suffix(".json")
        for archivo in (ruta, ruta_ficha):
            if not archivo.exists():
                raise FileNotFoundError(f"No se encontró {archivo}.")
        ficha = json.loads(ruta_ficha.read_text(encoding="utf-8"))
        return cls(joblib.load(ruta), ficha)

    def clasificar(self, imagen):
        caracteristicas = calcular_caracteristicas(imagen)
        valores = np.array([[caracteristicas[c] for c in self.columnas]], dtype=np.float64)
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", message="X does not have valid feature names")
            probabilidad = float(self.modelo.predict_proba(valores)[0, 1])

        fuera = [
            c for c in self.columnas
            if not self.rangos[c]["min"] <= caracteristicas[c] <= self.rangos[c]["max"]
        ]
        return {
            "es_bache": probabilidad >= self.umbral,
            "probabilidad_bache": probabilidad,
            "umbral": self.umbral,
            "caracteristicas": {c: caracteristicas[c] for c in self.columnas},
            "fuera_de_rango": fuera,
            "advertencia": ADVERTENCIA_RANGO if len(fuera) >= MINIMO_FUERA_DE_RANGO else None,
        }

    def informacion(self):
        return {
            "nombre": self.nombre,
            "version": self.version,
            "algoritmo": self.ficha["algoritmo"],
            "umbral": self.umbral,
            "dataset": self.ficha["dataset"]["version"],
            "metricas_prueba": self.ficha.get("metricas_prueba"),
            "columnas_entrada": self.columnas,
        }