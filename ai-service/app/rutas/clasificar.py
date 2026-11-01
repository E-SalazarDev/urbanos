from fastapi import APIRouter, File, HTTPException, Request, UploadFile
from starlette.concurrency import run_in_threadpool

from ..esquemas import InfoClasificador, InfoModelo, ResultadoClasificacion, TamanoImagen
from ..servicios.imagenes import leer_imagen

router = APIRouter(tags=["Clasificación"])


def _clasificador(request: Request):
    clasificador = request.app.state.clasificador
    if clasificador is None:
        raise HTTPException(status_code=503, detail="El clasificador no está disponible: no se cargó el modelo.")
    return clasificador


@router.post(
    "/clasificar",
    response_model=ResultadoClasificacion,
    summary="Dice si una foto muestra un bache (modelo real, sin cajas)",
)
async def clasificar(request: Request, archivo: UploadFile = File(description="Foto en JPEG, PNG o WEBP.")):
    clasificador = _clasificador(request)
    imagen = await leer_imagen(archivo, request.app.state.config.max_mb)
    resultado = await run_in_threadpool(clasificador.clasificar, imagen)
    return ResultadoClasificacion(
        simulado=False,
        modelo=InfoModelo(nombre=clasificador.nombre, version=clasificador.version),
        imagen=TamanoImagen(ancho=imagen.width, alto=imagen.height),
        **resultado,
    )


@router.get(
    "/clasificar/modelo",
    response_model=InfoClasificador,
    summary="Ficha del modelo: versión, métricas y columnas de entrada",
)
def ficha_del_modelo(request: Request):
    return _clasificador(request).informacion()