"""Pruebas del clasificador: medidas de la imagen, paridad con el entrenamiento y casos límite."""
import json
from io import BytesIO
from pathlib import Path

import numpy as np
import pytest
from fastapi.testclient import TestClient
from PIL import Image

from app.main import app
from app.servicios.caracteristicas import calcular_caracteristicas
from app.servicios.clasificador import ClasificadorBaches

# Medidas de un patrón de 320 x 200 calculadas con ml/actividad5/fuentes/datos_prep.py (el código del entrenamiento).
MEDIDAS_ENTRENAMIENTO = {'rojo_media': 0.460022, 'verde_media': 0.472028, 'azul_media': 0.364712, 'rojo_desv': 0.296484, 'verde_desv': 0.309893, 'azul_desv': 0.277291, 'brillo_media': 0.456211, 'brillo_desv': 0.22015, 'contraste': 0.682353, 'proporcion_oscura': 0.223145, 'proporcion_clara': 0.093994, 'saturacion_media': 0.646494, 'densidad_bordes': 0.02301, 'nitidez': 0.006015, 'entropia': 4.641976, 'textura_bloques': 0.042649}

# Filas reales del conjunto de prueba: medidas del dataset limpio y la probabilidad que dio el modelo en MLflow.
REFERENCIA = [
    (3.913271054501774e-07, {'rojo_media': 0.3577632308006286, 'verde_media': 0.4966354370117187, 'azul_media': 0.3512322008609772, 'rojo_desv': 0.1727684140205383, 'verde_desv': 0.141330674290657, 'azul_desv': 0.3193937242031097, 'brillo_media': 0.4384878277778625, 'brillo_desv': 0.1628353893756866, 'contraste': 0.529411792755127, 'proporcion_oscura': 0.13739013671875, 'proporcion_clara': 0.0084228515625, 'saturacion_media': 0.583747923374176, 'densidad_bordes': 0.07635498046875, 'nitidez': 0.011018737219274, 'entropia': 4.331681569766704, 'textura_bloques': 0.0621118806302547}),
    (0.0069387245483095, {'rojo_media': 0.77174973487854, 'verde_media': 0.7752792835235596, 'azul_media': 0.7747175693511963, 'rojo_desv': 0.2063146084547042, 'verde_desv': 0.1989748030900955, 'azul_desv': 0.1988944560289383, 'brillo_media': 0.7741270065307617, 'brillo_desv': 0.2001934498548507, 'contraste': 0.4352940917015075, 'proporcion_oscura': 0.0, 'proporcion_clara': 0.55255126953125, 'saturacion_media': 0.0335056707262992, 'densidad_bordes': 0.03900146484375, 'nitidez': 0.0047499346546828, 'entropia': 2.13843617344021, 'textura_bloques': 0.0223073773086071}),
    (0.0415098399987111, {'rojo_media': 0.5689103603363037, 'verde_media': 0.5131669044494629, 'azul_media': 0.4918035864830017, 'rojo_desv': 0.2854881584644317, 'verde_desv': 0.2565974295139313, 'azul_desv': 0.2651721835136413, 'brillo_media': 0.5273837447166443, 'brillo_desv': 0.2578316628932953, 'contraste': 0.843137264251709, 'proporcion_oscura': 0.15179443359375, 'proporcion_clara': 0.2281494140625, 'saturacion_media': 0.283013105392456, 'densidad_bordes': 0.15081787109375, 'nitidez': 0.0195915792137384, 'entropia': 4.857959905208508, 'textura_bloques': 0.0863522663712501}),
    (0.6575239263640202, {'rojo_media': 0.4382092356681824, 'verde_media': 0.4413006901741028, 'azul_media': 0.4456672072410583, 'rojo_desv': 0.1887183785438537, 'verde_desv': 0.185617133975029, 'azul_desv': 0.1912689805030822, 'brillo_media': 0.4408641159534454, 'brillo_desv': 0.1849431842565536, 'contraste': 0.6235294342041016, 'proporcion_oscura': 0.1002197265625, 'proporcion_clara': 0.09185791015625, 'saturacion_media': 0.1753537654876709, 'densidad_bordes': 0.1646728515625, 'nitidez': 0.0255466699600219, 'entropia': 4.355697895836653, 'textura_bloques': 0.0925641655921936}),
    (0.913806108940083, {'rojo_media': 0.4110141098499298, 'verde_media': 0.401513934135437, 'azul_media': 0.4032913446426391, 'rojo_desv': 0.1449981033802032, 'verde_desv': 0.1490439623594284, 'azul_desv': 0.162917748093605, 'brillo_media': 0.4045211672782898, 'brillo_desv': 0.1480012089014053, 'contraste': 0.4705882668495178, 'proporcion_oscura': 0.140625, 'proporcion_clara': 0.0137939453125, 'saturacion_media': 0.1077356785535812, 'densidad_bordes': 0.1097412109375, 'nitidez': 0.0167647488415241, 'entropia': 4.255619364042248, 'textura_bloques': 0.0669577494263649}),
    (0.9816557168222446, {'rojo_media': 0.5684270858764648, 'verde_media': 0.552187442779541, 'azul_media': 0.5750718116760254, 'rojo_desv': 0.1407922059297561, 'verde_desv': 0.1436021029949188, 'azul_desv': 0.1497479528188705, 'brillo_media': 0.5595684051513672, 'brillo_desv': 0.1431119292974472, 'contraste': 0.4823529720306396, 'proporcion_oscura': 0.0556640625, 'proporcion_clara': 0.01422119140625, 'saturacion_media': 0.0586140975356102, 'densidad_bordes': 0.08416748046875, 'nitidez': 0.0155962202697992, 'entropia': 3.9132300847129895, 'textura_bloques': 0.0568022727966308}),
    (0.9944459749697224, {'rojo_media': 0.638542652130127, 'verde_media': 0.6121953129768372, 'azul_media': 0.6514105796813965, 'rojo_desv': 0.1005331575870513, 'verde_desv': 0.1033629029989242, 'azul_desv': 0.1081563606858253, 'brillo_media': 0.6243236064910889, 'brillo_desv': 0.1026320159435272, 'contraste': 0.3137255012989044, 'proporcion_oscura': 0.006103515625, 'proporcion_clara': 0.062255859375, 'saturacion_media': 0.0704393610358238, 'densidad_bordes': 0.09442138671875, 'nitidez': 0.0246644280850887, 'entropia': 3.635476081185607, 'textura_bloques': 0.0572815611958503}),
]

CAMPOS = {
    "simulado", "modelo", "imagen", "es_bache", "probabilidad_bache",
    "umbral", "caracteristicas", "fuera_de_rango", "advertencia",
}


def patron(ancho=320, alto=200):
    y, x = np.mgrid[0:alto, 0:ancho]
    rojo = x * 255 // max(ancho - 1, 1)
    verde = y * 255 // max(alto - 1, 1)
    azul = ((x // 7 + y // 5) % 2) * 200
    matriz = np.stack([rojo, verde, azul], axis=-1).astype(np.uint8)
    matriz[alto // 3 : alto // 3 + max(alto // 10, 1), :, :] = 30
    return Image.fromarray(matriz)


def en_bytes(imagen, formato="PNG", **opciones):
    buffer = BytesIO()
    imagen.save(buffer, format=formato, **opciones)
    return buffer.getvalue()


def enviar(cliente, contenido, nombre="foto.png", tipo="image/png"):
    return cliente.post("/clasificar", files={"archivo": (nombre, contenido, tipo)})


def test_las_medidas_son_iguales_a_las_del_entrenamiento():
    obtenidas = calcular_caracteristicas(patron())
    assert set(obtenidas) == set(MEDIDAS_ENTRENAMIENTO)
    for nombre, esperado in MEDIDAS_ENTRENAMIENTO.items():
        assert obtenidas[nombre] == pytest.approx(esperado, abs=1e-5), nombre


@pytest.mark.filterwarnings("ignore:X does not have valid feature names")
def test_el_modelo_exportado_da_las_mismas_probabilidades_que_mlflow():
    clasificador = ClasificadorBaches.cargar("modelos/clasificador_baches.joblib")
    for esperada, medidas in REFERENCIA:
        valores = np.array([[medidas[c] for c in clasificador.columnas]])
        assert clasificador.modelo.predict_proba(valores)[0, 1] == pytest.approx(esperada, abs=1e-9)


def test_la_ficha_declara_16_columnas_y_umbral():
    ficha = json.loads(Path("modelos/clasificador_baches.json").read_text(encoding="utf-8"))
    assert len(ficha["columnas_entrada"]) == 16
    assert set(ficha["columnas_entrada"]) == set(MEDIDAS_ENTRENAMIENTO)
    assert ficha["umbral"] == 0.5


def test_clasificar_devuelve_el_formato_acordado(cliente):
    respuesta = enviar(cliente, en_bytes(patron()))
    assert respuesta.status_code == 200
    datos = respuesta.json()
    assert set(datos) == CAMPOS
    assert datos["simulado"] is False
    assert datos["imagen"] == {"ancho": 320, "alto": 200}
    assert 0 <= datos["probabilidad_bache"] <= 1
    assert datos["es_bache"] == (datos["probabilidad_bache"] >= datos["umbral"])
    assert len(datos["caracteristicas"]) == 16


def test_la_misma_foto_da_el_mismo_resultado(cliente):
    foto = en_bytes(patron())
    assert enviar(cliente, foto).json() == enviar(cliente, foto).json()


def test_el_formato_del_archivo_no_cambia_la_respuesta_con_png_y_webp_sin_perdida(cliente):
    imagen = patron()
    png = enviar(cliente, en_bytes(imagen)).json()["probabilidad_bache"]
    webp = enviar(cliente, en_bytes(imagen, "WEBP", lossless=True), "foto.webp", "image/webp").json()
    assert webp["probabilidad_bache"] == pytest.approx(png, abs=1e-9)


def test_jpeg_da_una_probabilidad_parecida_a_la_del_png(cliente):
    imagen = patron()
    png = enviar(cliente, en_bytes(imagen)).json()["probabilidad_bache"]
    jpeg = enviar(cliente, en_bytes(imagen, "JPEG", quality=92), "foto.jpg", "image/jpeg").json()
    assert abs(jpeg["probabilidad_bache"] - png) < 0.15


@pytest.mark.parametrize("modo", ["L", "RGBA", "P", "LA"])
def test_acepta_otros_modos_de_color(cliente, modo):
    imagen = patron().convert(modo)
    respuesta = enviar(cliente, en_bytes(imagen))
    assert respuesta.status_code == 200
    assert 0 <= respuesta.json()["probabilidad_bache"] <= 1


def test_una_foto_de_un_solo_pixel_no_rompe_el_servicio(cliente):
    respuesta = enviar(cliente, en_bytes(Image.new("RGB", (1, 1), (120, 120, 120))))
    assert respuesta.status_code == 200
    datos = respuesta.json()
    assert datos["imagen"] == {"ancho": 1, "alto": 1}
    assert 0 <= datos["probabilidad_bache"] <= 1


def test_una_imagen_de_un_solo_color_es_valida_y_se_marca_fuera_de_rango(cliente):
    respuesta = enviar(cliente, en_bytes(Image.new("RGB", (400, 300), (0, 0, 0))))
    assert respuesta.status_code == 200
    datos = respuesta.json()
    assert datos["caracteristicas"]["entropia"] == 0
    assert len(datos["fuera_de_rango"]) >= 3
    assert datos["advertencia"]


def test_la_orientacion_exif_se_respeta(cliente):
    imagen = patron(300, 100)
    exif = Image.Exif()
    exif[274] = 6
    girada = enviar(cliente, en_bytes(imagen, "JPEG", quality=95, exif=exif), "foto.jpg", "image/jpeg").json()
    assert girada["imagen"] == {"ancho": 100, "alto": 300}


def test_una_foto_muy_alta_se_procesa(cliente):
    respuesta = enviar(cliente, en_bytes(patron(40, 4000)))
    assert respuesta.status_code == 200


def test_rechaza_archivo_vacio(cliente):
    assert enviar(cliente, b"", "vacio.png").status_code == 400


def test_rechaza_archivo_que_no_es_imagen(cliente):
    assert enviar(cliente, b"esto no es una imagen", "nota.png").status_code == 415


def test_rechaza_imagen_cortada_a_la_mitad(cliente):
    foto = en_bytes(patron(), "JPEG")
    assert enviar(cliente, foto[: len(foto) // 2], "rota.jpg", "image/jpeg").status_code == 415


def test_rechaza_formato_no_permitido(cliente):
    assert enviar(cliente, en_bytes(patron(), "GIF"), "foto.gif", "image/gif").status_code == 415


def test_rechaza_imagen_demasiado_grande(monkeypatch):
    monkeypatch.setenv("AI_MAX_MB", "1")
    with TestClient(app) as cliente:
        assert enviar(cliente, b"0" * (2 * 1024 * 1024)).status_code == 413


def test_sin_archivo_responde_422(cliente):
    assert cliente.post("/clasificar").status_code == 422


def test_ficha_del_modelo(cliente):
    respuesta = cliente.get("/clasificar/modelo")
    assert respuesta.status_code == 200
    datos = respuesta.json()
    assert datos["nombre"] == "clasificador_baches"
    assert datos["dataset"].startswith("v1-")
    assert len(datos["columnas_entrada"]) == 16
    assert datos["metricas_prueba"]["f1"] > 0.9


def test_sin_modelo_el_servicio_arranca_pero_clasificar_responde_503(monkeypatch):
    monkeypatch.setenv("AI_RUTA_CLASIFICADOR", "modelos/no_existe.joblib")
    with TestClient(app) as cliente:
        assert cliente.get("/salud").status_code == 200
        assert enviar(cliente, en_bytes(patron())).status_code == 503
        assert cliente.get("/clasificar/modelo").status_code == 503


def test_detect_sigue_simulado(cliente):
    respuesta = cliente.post("/detect", files={"archivo": ("f.png", en_bytes(patron()), "image/png")})
    assert respuesta.status_code == 200
    assert respuesta.json()["simulado"] is True