"""Detectores de daños en la calle.

Todos tienen la misma forma: reciben una imagen y devuelven una lista de detecciones.
Así, cuando llegue el modelo YOLO real (ajustado con RDD2022), el resto del servicio no cambia.
"""
import hashlib
import random

TIPOS_DANO = {
    "D00": "Grieta longitudinal",
    "D10": "Grieta transversal",
    "D20": "Grieta piel de cocodrilo",
    "D40": "Bache",
}


class DetectorSimulado:
    """Detecciones de ejemplo, repetibles: la misma imagen siempre da el mismo resultado."""

    nombre = "simulado"
    version = "0.1.0"
    simulado = True
    listo = True

    def __init__(self, confianza_minima):
        self.confianza_minima = confianza_minima

    def detectar(self, imagen):
        miniatura = imagen.convert("RGB").resize((16, 16)).tobytes()
        semilla = int(hashlib.sha256(miniatura).hexdigest()[:16], 16)
        azar = random.Random(semilla)

        detecciones = []
        for _ in range(azar.randint(0, 3)):
            ancho = min(azar.randint(max(imagen.width // 10, 1), max(imagen.width // 3, 2)), imagen.width)
            alto = min(azar.randint(max(imagen.height // 10, 1), max(imagen.height // 3, 2)), imagen.height)
            x = azar.randint(0, imagen.width - ancho)
            y = azar.randint(0, imagen.height - alto)
            tipo = azar.choice(list(TIPOS_DANO))
            confianza = round(azar.uniform(0.30, 0.99), 2)
            if confianza >= self.confianza_minima:
                detecciones.append({
                    "tipo_dano": tipo,
                    "nombre": TIPOS_DANO[tipo],
                    "confianza": confianza,
                    "caja": {"x": x, "y": y, "ancho": ancho, "alto": alto},
                })
        return detecciones


def obtener_detector(config):
    """Elige el detector según AI_MODE."""
    if config.modo == "simulado":
        return DetectorSimulado(config.confianza_minima)
    raise RuntimeError(
        "AI_MODE=real todavía no está disponible: falta entrenar y conectar el modelo "
        f"({config.ruta_modelo}). Usa AI_MODE=simulado por ahora."
    )
