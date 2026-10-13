# Servicio de IA (ai-service)

Servicio aparte que **solo analiza imágenes**: recibe una foto y devuelve los daños que encuentra (baches y grietas). No guarda datos y no conoce el GPS ni la base de datos; eso lo hace el backend.

## Tecnologías
Python, FastAPI, Uvicorn, Pillow y `python-multipart`. Pruebas con pytest y httpx.
Más adelante: el modelo YOLO ajustado con RDD2022 (Ultralytics, PyTorch) y OpenCV.

## Estado
- `POST /detect` responde en modo **simulado** (`"simulado": true`): las detecciones son de ejemplo, pero siempre iguales para la misma foto.
- El módulo `privacy` ya difumina las zonas que se le indiquen. Falta el detector de rostros y placas, que necesita un modelo aparte.
- Falta entrenar y conectar el modelo real.

## Cómo correrlo
Desde la carpeta `ai-service`, con el entorno virtual activado:

```powershell
python -m uvicorn app.main:app --reload --port 8001
```

- Documentación interactiva: http://127.0.0.1:8001/docs
- Estado del servicio: http://127.0.0.1:8001/salud

Probar con una foto:

```powershell
curl.exe -F "archivo=@foto.jpg" http://127.0.0.1:8001/detect
```

## Pruebas

```powershell
python -m pytest
```

## Variables de entorno

| Variable | Qué hace | Valor por defecto |
|---|---|---|
| `AI_MODE` | `simulado` o `real` | `simulado` |
| `AI_CONFIANZA_MIN` | Confianza mínima para devolver una detección (0 a 1) | `0.25` |
| `AI_MAX_MB` | Tamaño máximo de la foto | `10` |
| `AI_RUTA_MODELO` | Archivo del modelo entrenado (modo real) | `modelos/detector_rdd2022.pt` |

## Contrato de la API

### `GET /salud`
```json
{
  "estado": "ok",
  "servicio": "urbanos-ai",
  "listo": true,
  "modo": "simulado",
  "simulado": true,
  "modelo": { "nombre": "simulado", "version": "0.1.0" }
}
```

### `POST /detect`
Recibe un formulario con el campo `archivo` (JPEG, PNG o WEBP).

```json
{
  "simulado": true,
  "modelo": { "nombre": "simulado", "version": "0.1.0" },
  "imagen": { "ancho": 640, "alto": 480 },
  "detecciones": [
    {
      "tipo_dano": "D40",
      "nombre": "Bache",
      "confianza": 0.91,
      "caja": { "x": 120, "y": 200, "ancho": 80, "alto": 60 }
    }
  ]
}
```

- `tipo_dano`: `D00` grieta longitudinal, `D10` grieta transversal, `D20` piel de cocodrilo, `D40` bache.
- `confianza`: de 0 a 1.
- `caja`: en píxeles de la imagen original; `(x, y)` es la esquina superior izquierda.
- Una foto sin daños devuelve `"detecciones": []`.

| Código | Cuándo |
|---|---|
| 200 | Foto analizada |
| 400 | Archivo vacío |
| 413 | Foto demasiado grande |
| 415 | No es una imagen válida o el formato no se permite |

## Estructura

```
ai-service/
├── app/
│   ├── main.py            # crea la app y carga el detector al arrancar
│   ├── config.py          # variables de entorno
│   ├── esquemas.py        # formato de entrada y salida
│   ├── privacy.py         # difuminado de rostros y placas
│   ├── rutas/             # salud y detectar
│   └── servicios/         # detector y lectura de imágenes
├── tests/
└── pytest.ini
```
