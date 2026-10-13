from fastapi import APIRouter, File, Request, UploadFile
from starlette.concurrency import run_in_threadpool

from ..esquemas import InfoModelo, ResultadoDeteccion, TamanoImagen
from ..servicios.imagenes import leer_imagen

router = APIRouter(tags=["Detección"])


@router.post(
    "/detect",
    response_model=ResultadoDeteccion,
    summary="Detecta baches y grietas en una foto",
)
async def detectar(request: Request, archivo: UploadFile = File(description="Foto en JPEG, PNG o WEBP.")):
    config = request.app.state.config
    detector = request.app.state.detector

    imagen = await leer_imagen(archivo, config.max_mb)
    detecciones = await run_in_threadpool(detector.detectar, imagen)

    return ResultadoDeteccion(
        simulado=detector.simulado,
        modelo=InfoModelo(nombre=detector.nombre, version=detector.version),
        imagen=TamanoImagen(ancho=imagen.width, alto=imagen.height),
        detecciones=detecciones,
    )
