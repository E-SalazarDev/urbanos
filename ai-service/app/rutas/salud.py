from fastapi import APIRouter, Request

from ..esquemas import InfoModelo, Salud

router = APIRouter(tags=["Salud"])


@router.get("/salud", response_model=Salud, summary="Dice si el servicio y el modelo están listos")
def salud(request: Request):
    detector = request.app.state.detector
    return Salud(
        estado="ok",
        servicio="urbanos-ai",
        listo=detector.listo,
        modo=request.app.state.config.modo,
        simulado=detector.simulado,
        modelo=InfoModelo(nombre=detector.nombre, version=detector.version),
    )
