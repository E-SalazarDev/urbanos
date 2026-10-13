"""Lectura y validación de la imagen que llega al servicio."""
from io import BytesIO

from fastapi import HTTPException, UploadFile
from PIL import Image, ImageOps, UnidentifiedImageError

FORMATOS_PERMITIDOS = {"JPEG", "PNG", "WEBP"}


async def leer_imagen(archivo: UploadFile, max_mb: int):
    """Devuelve la imagen en RGB, o responde con un error claro si no es válida."""
    limite = max_mb * 1024 * 1024
    contenido = await archivo.read(limite + 1)

    if not contenido:
        raise HTTPException(status_code=400, detail="El archivo está vacío.")
    if len(contenido) > limite:
        raise HTTPException(status_code=413, detail=f"La imagen supera el máximo de {max_mb} MB.")

    try:
        imagen = Image.open(BytesIO(contenido))
        formato = imagen.format
        imagen.load()
    except Image.DecompressionBombError:
        raise HTTPException(status_code=413, detail="La imagen tiene demasiados píxeles.")
    except (UnidentifiedImageError, OSError):
        raise HTTPException(status_code=415, detail="El archivo no es una imagen válida.")

    if formato not in FORMATOS_PERMITIDOS:
        raise HTTPException(status_code=415, detail="Formato no permitido. Usa JPEG, PNG o WEBP.")

    return ImageOps.exif_transpose(imagen).convert("RGB")
