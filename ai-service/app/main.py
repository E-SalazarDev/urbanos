"""Servicio de IA de UrbanOS. Solo analiza imágenes: no guarda datos ni conoce el GPS."""
from contextlib import asynccontextmanager

from fastapi import FastAPI

from .config import cargar
from .rutas import detectar, salud
from .servicios.detector import obtener_detector


@asynccontextmanager
async def ciclo_de_vida(app: FastAPI):
    """Carga la configuración y el detector una sola vez, al arrancar."""
    app.state.config = cargar()
    app.state.detector = obtener_detector(app.state.config)
    yield


app = FastAPI(
    title="UrbanOS · Servicio de IA",
    version="0.1.0",
    description=(
        "Recibe una foto y devuelve los daños que encuentra en la calle. "
        "Mientras `simulado` sea true, la respuesta es de ejemplo."
    ),
    lifespan=ciclo_de_vida,
)
app.include_router(salud.router)
app.include_router(detectar.router)
