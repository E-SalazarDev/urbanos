"""Privacidad: difuminado de zonas sensibles (rostros y placas) antes de guardar una imagen.

Hoy solo existe la parte que difumina las zonas que se le indiquen.
Falta el detector de rostros y placas, que necesita un modelo aparte.
"""
from PIL import ImageFilter


def difuminar_cajas(imagen, cajas, radio=12):
    """Devuelve una copia de la imagen con las cajas difuminadas.

    Cada caja es un diccionario con x, y, ancho y alto, en píxeles.
    """
    resultado = imagen.copy()
    for caja in cajas:
        x0 = max(int(caja["x"]), 0)
        y0 = max(int(caja["y"]), 0)
        x1 = min(x0 + int(caja["ancho"]), imagen.width)
        y1 = min(y0 + int(caja["alto"]), imagen.height)
        if x1 <= x0 or y1 <= y0:
            continue
        zona = resultado.crop((x0, y0, x1, y1)).filter(ImageFilter.GaussianBlur(radio))
        resultado.paste(zona, (x0, y0))
    return resultado


def detectar_rostros_y_placas(imagen):
    """Pendiente: encontrar rostros y placas. Se define qué modelo usar y su licencia antes de implementarlo."""
    raise NotImplementedError("El detector de rostros y placas todavía no está implementado.")
