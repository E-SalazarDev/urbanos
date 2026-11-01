"""Servicio de IA de UrbanOS. Solo analiza imágenes: no guarda datos ni conoce el GPS."""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from .config import cargar
from .rutas import clasificar, detectar, salud
from .servicios.clasificador import ClasificadorBaches
from .servicios.detector import obtener_detector

registro = logging.getLogger("uvicorn.error")


@asynccontextmanager
async def ciclo_de_vida(app: FastAPI):
    """Carga la configuración, el detector y el clasificador una sola vez, al arrancar."""
    app.state.config = cargar()
    app.state.detector = obtener_detector(app.state.config)
    try:
        app.state.clasificador = ClasificadorBaches.cargar(app.state.config.ruta_clasificador)
    except FileNotFoundError as error:
        app.state.clasificador = None
        registro.warning("Clasificador no cargado: %s", error)
    yield


app = FastAPI(
    title="UrbanOS · Servicio de IA",
    version="0.2.0",
    description=(
        "Recibe una foto y devuelve lo que encuentra en la calle. "
        "`/detect` es de ejemplo mientras `simulado` sea true; "
        "`/clasificar` usa el modelo entrenado y dice si la foto muestra un bache."
    ),
    lifespan=ciclo_de_vida,
)
app.include_router(salud.router)
app.include_router(detectar.router)
app.include_router(clasificar.router)