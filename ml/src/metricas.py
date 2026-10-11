"""Métricas de clasificación binaria (clase positiva: bache)."""
import numpy as np
import pandas as pd
from sklearn.metrics import accuracy_score, confusion_matrix, f1_score, precision_score, recall_score


def calcular_metricas(y_real, prob_bache, umbral=0.5):
    """Accuracy, precision, recall, F1 y matriz de confusión para un umbral."""
    y_real = np.asarray(y_real)
    y_pred = (np.asarray(prob_bache) >= umbral).astype(int)
    tn, fp, fn, tp = confusion_matrix(y_real, y_pred, labels=[0, 1]).ravel()
    return {
        "accuracy": accuracy_score(y_real, y_pred),
        "precision": precision_score(y_real, y_pred, zero_division=0),
        "recall": recall_score(y_real, y_pred, zero_division=0),
        "f1": f1_score(y_real, y_pred, zero_division=0),
        "tn": int(tn), "fp": int(fp), "fn": int(fn), "tp": int(tp),
    }


def tabla_umbrales(y_real, prob_bache, umbrales=(0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8)):
    """Métricas para varios umbrales de decisión."""
    filas = []
    for umbral in umbrales:
        fila = calcular_metricas(y_real, prob_bache, umbral)
        fila["umbral"] = umbral
        filas.append(fila)
    return pd.DataFrame(filas)[["umbral", "accuracy", "precision", "recall", "f1", "fp", "fn"]]
