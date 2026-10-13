from io import BytesIO

import pytest
from fastapi.testclient import TestClient
from PIL import Image

from app.main import app


@pytest.fixture
def cliente(monkeypatch):
    monkeypatch.setenv("AI_MODE", "simulado")
    monkeypatch.setenv("AI_CONFIANZA_MIN", "0.25")
    monkeypatch.setenv("AI_MAX_MB", "10")
    with TestClient(app) as cliente:
        yield cliente


@pytest.fixture
def crear_foto():
    """Devuelve una función que genera fotos PNG distintas según el número que se le dé."""

    def _crear(numero=0, tamano=(200, 100)):
        imagen = Image.new("RGB", tamano, color=((numero * 37) % 256, (numero * 91) % 256, (numero * 53) % 256))
        for x in range(tamano[0]):
            imagen.putpixel((x, (x * (numero + 1)) % tamano[1]), (255, 255, 255))
        buffer = BytesIO()
        imagen.save(buffer, format="PNG")
        return buffer.getvalue()

    return _crear
