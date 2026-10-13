"""Configuración del servicio de IA, leída de variables de entorno."""
import os
from dataclasses import dataclass

MODOS_VALIDOS = ("simulado", "real")


def _texto(nombre, por_defecto):
    """Lee una variable de entorno e ignora comentarios al final de la línea."""
    return os.getenv(nombre, por_defecto).split("#")[0].strip()


@dataclass(frozen=True)
class Configuracion:
    modo: str
    confianza_minima: float
    max_mb: int
    ruta_modelo: str


def cargar():
    """Construye la configuración y valida los valores."""
    config = Configuracion(
        modo=_texto("AI_MODE", "simulado"),
        confianza_minima=float(_texto("AI_CONFIANZA_MIN", "0.25")),
        max_mb=int(_texto("AI_MAX_MB", "10")),
        ruta_modelo=_texto("AI_RUTA_MODELO", "modelos/detector_rdd2022.pt"),
    )
    if config.modo not in MODOS_VALIDOS:
        raise ValueError(f"AI_MODE debe ser uno de {MODOS_VALIDOS}, no '{config.modo}'.")
    if not 0 <= config.confianza_minima <= 1:
        raise ValueError("AI_CONFIANZA_MIN debe estar entre 0 y 1.")
    return config
