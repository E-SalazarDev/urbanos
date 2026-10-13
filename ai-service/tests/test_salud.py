def test_salud_responde_ok(cliente):
    respuesta = cliente.get("/salud")
    assert respuesta.status_code == 200
    datos = respuesta.json()
    assert datos["estado"] == "ok"
    assert datos["servicio"] == "urbanos-ai"
    assert datos["listo"] is True
    assert datos["modo"] == "simulado"
    assert datos["simulado"] is True
    assert datos["modelo"]["version"]
