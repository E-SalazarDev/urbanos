import numpy as np
from PIL import Image

TAMANO_REDUCIDO = 128
LADO_BLOQUE = 8


def calcular_caracteristicas(imagen):
    reducida = imagen.convert("RGB").resize((TAMANO_REDUCIDO, TAMANO_REDUCIDO), Image.BILINEAR)
    rgb = np.asarray(reducida, dtype=np.float32) / 255.0
    gris = np.asarray(reducida.convert("L"), dtype=np.float32) / 255.0
    saturacion = np.asarray(reducida.convert("HSV"), dtype=np.float32)[..., 1] / 255.0

    gy, gx = np.gradient(gris)
    magnitud = np.hypot(gx, gy)
    laplaciano = (
        -4 * gris[1:-1, 1:-1] + gris[:-2, 1:-1] + gris[2:, 1:-1] + gris[1:-1, :-2] + gris[1:-1, 2:]
    )
    histograma, _ = np.histogram(gris, bins=32, range=(0, 1))
    probabilidades = histograma / histograma.sum()
    probabilidades = probabilidades[probabilidades > 0]
    n = TAMANO_REDUCIDO // LADO_BLOQUE
    bloques = gris.reshape(n, LADO_BLOQUE, n, LADO_BLOQUE).std(axis=(1, 3))

    return {
        "rojo_media": float(rgb[..., 0].mean()),
        "verde_media": float(rgb[..., 1].mean()),
        "azul_media": float(rgb[..., 2].mean()),
        "rojo_desv": float(rgb[..., 0].std()),
        "verde_desv": float(rgb[..., 1].std()),
        "azul_desv": float(rgb[..., 2].std()),
        "brillo_media": float(gris.mean()),
        "brillo_desv": float(gris.std()),
        "contraste": float(np.percentile(gris, 95) - np.percentile(gris, 5)),
        "proporcion_oscura": float((gris < 0.25).mean()),
        "proporcion_clara": float((gris > 0.75).mean()),
        "saturacion_media": float(saturacion.mean()),
        "densidad_bordes": float((magnitud > 0.1).mean()),
        "nitidez": float(laplaciano.var()),
        "entropia": float(abs(-(probabilidades * np.log2(probabilidades)).sum())),
        "textura_bloques": float(bloques.mean()),
    }