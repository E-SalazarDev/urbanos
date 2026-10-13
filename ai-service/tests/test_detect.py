import pytest
from fastapi.testclient import TestClient

from app.main import app

TIPOS = {"D00", "D10", "D20", "D40"}


def enviar(cliente, contenido, nombre="foto.png", tipo="image/png"):
    return cliente.post("/detect", files={"archivo": (nombre, contenido, tipo)})


def test_devuelve_el_formato_acordado(cliente, crear_foto):
    respuesta = enviar(cliente, crear_foto(1))
    assert respuesta.status_code == 200
    datos = respuesta.json()
    assert datos["simulado"] is True
    assert datos["modelo"]["nombre"] == "simulado"
    assert datos["imagen"] == {"ancho": 200, "alto": 100}
    assert isinstance(datos["detecciones"], list)


def test_las_detecciones_son_validas_y_caen_dentro_de_la_imagen(cliente, crear_foto):
    total = 0
    for numero in range(30):
        datos = enviar(cliente, crear_foto(numero)).json()
        for d in datos["detecciones"]:
            total += 1
            assert d["tipo_dano"] in TIPOS
            assert 0 <= d["confianza"] <= 1
            caja = d["caja"]
            assert caja["x"] >= 0 and caja["y"] >= 0
            assert caja["ancho"] > 0 and caja["alto"] > 0
            assert caja["x"] + caja["ancho"] <= 200
            assert caja["y"] + caja["alto"] <= 100
    assert total > 0


def test_la_misma_foto_da_el_mismo_resultado(cliente, crear_foto):
    foto = crear_foto(7)
    assert enviar(cliente, foto).json() == enviar(cliente, foto).json()


def test_la_confianza_minima_filtra_detecciones(monkeypatch, crear_foto):
    monkeypatch.setenv("AI_CONFIANZA_MIN", "1")
    with TestClient(app) as cliente:
        for numero in range(10):
            assert enviar(cliente, crear_foto(numero)).json()["detecciones"] == []


def test_rechaza_archivo_vacio(cliente):
    assert enviar(cliente, b"", "vacio.png").status_code == 400


def test_rechaza_archivo_que_no_es_imagen(cliente):
    assert enviar(cliente, b"esto no es una imagen", "nota.png").status_code == 415


def test_rechaza_imagen_demasiado_grande(monkeypatch):
    monkeypatch.setenv("AI_MAX_MB", "1")
    with TestClient(app) as cliente:
        respuesta = enviar(cliente, b"0" * (2 * 1024 * 1024))
    assert respuesta.status_code == 413


def test_no_arranca_en_modo_real_todavia(monkeypatch):
    monkeypatch.setenv("AI_MODE", "real")
    with pytest.raises(RuntimeError):
        with TestClient(app):
            pass


def test_modo_invalido_no_arranca(monkeypatch):
    monkeypatch.setenv("AI_MODE", "inventado")
    with pytest.raises(ValueError):
        with TestClient(app):
            pass
