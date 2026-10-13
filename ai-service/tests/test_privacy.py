import pytest
from PIL import Image

from app.privacy import detectar_rostros_y_placas, difuminar_cajas


def imagen_de_rayas():
    imagen = Image.new("RGB", (100, 80), (255, 255, 255))
    for x in range(0, 100, 4):
        for y in range(80):
            imagen.putpixel((x, y), (0, 0, 0))
    return imagen


def test_difumina_solo_la_zona_indicada():
    original = imagen_de_rayas()
    resultado = difuminar_cajas(original, [{"x": 20, "y": 20, "ancho": 40, "alto": 30}])
    assert resultado.getpixel((40, 35)) != original.getpixel((40, 35))
    assert resultado.getpixel((5, 5)) == original.getpixel((5, 5))
    assert resultado.getpixel((90, 70)) == original.getpixel((90, 70))


def test_no_modifica_la_imagen_original():
    original = imagen_de_rayas()
    copia = original.copy()
    difuminar_cajas(original, [{"x": 0, "y": 0, "ancho": 100, "alto": 80}])
    assert original.tobytes() == copia.tobytes()


def test_ignora_cajas_fuera_de_la_imagen():
    original = imagen_de_rayas()
    resultado = difuminar_cajas(original, [{"x": 500, "y": 500, "ancho": 40, "alto": 30}])
    assert resultado.tobytes() == original.tobytes()


def test_el_detector_de_rostros_y_placas_aun_no_existe():
    with pytest.raises(NotImplementedError):
        detectar_rostros_y_placas(imagen_de_rayas())
