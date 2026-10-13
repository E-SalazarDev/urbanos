"""Formato de los datos que entran y salen del servicio (el contrato de la API)."""
from typing import Literal

from pydantic import BaseModel, Field


class InfoModelo(BaseModel):
    nombre: str = Field(description="Nombre del modelo que dio la respuesta.")
    version: str = Field(description="Versión del modelo.")


class Salud(BaseModel):
    estado: str
    servicio: str
    listo: bool = Field(description="True si el modelo ya está cargado y puede responder.")
    modo: str = Field(description="'simulado' o 'real'.")
    simulado: bool
    modelo: InfoModelo


class Caja(BaseModel):
    """Rectángulo en píxeles de la imagen original. (x, y) es la esquina superior izquierda."""

    x: int
    y: int
    ancho: int
    alto: int


class Deteccion(BaseModel):
    tipo_dano: Literal["D00", "D10", "D20", "D40"] = Field(
        description="D00 grieta longitudinal, D10 grieta transversal, D20 piel de cocodrilo, D40 bache."
    )
    nombre: str = Field(description="Nombre del daño en español.")
    confianza: float = Field(ge=0, le=1, description="Confianza de la IA, de 0 a 1.")
    caja: Caja


class TamanoImagen(BaseModel):
    ancho: int
    alto: int


class ResultadoDeteccion(BaseModel):
    simulado: bool = Field(description="True si la respuesta es de ejemplo y no de un modelo real.")
    modelo: InfoModelo
    imagen: TamanoImagen
    detecciones: list[Deteccion]
