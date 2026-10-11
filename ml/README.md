# Comparativo de modelos preentrenados para detectar daño en calles

Parte de **UrbanOS**, una plataforma municipal que cuida las calles de una ciudad con datos e inteligencia artificial. Esta carpeta contiene la actividad de visión por computadora de la maestría en IA: comparo tres modelos preentrenados de Hugging Face en una tarea real del proyecto.

## Caso de uso

Antes de contar y ubicar cada bache en el mapa, UrbanOS necesita decidir si una foto muestra un bache o la calle está en buen estado.

- **Rama de IA:** visión por computadora.
- **Tarea:** clasificación binaria de imágenes. Clase positiva: `bache`. Clase negativa: `sin_dano`.
- **Criterio principal:** no dejar pasar un bache real (falso negativo). Una falsa alarma solo cuesta una revisión.

## Modelos comparados

| Modelo | Id en Hugging Face | Tamaño |
|---|---|---|
| MobileNetV2 | `google/mobilenet_v2_1.0_224` | Ligero |
| ResNet-50 | `microsoft/resnet-50` | Mediano |
| ViT-Base | `google/vit-base-patch16-224` | Grande |

La licencia y la tarea de cada uno se consultan al Hub dentro del cuaderno y quedan en `results/metricas_modelos.csv`.

**Ajuste mínimo:** los modelos no se reentrenan. Los uso congelados como extractores de características y entreno una regresión logística encima. El parámetro `C` se elige con la partición de validación.

## Estructura

```
ml/
├── notebooks/
│   └── 01_comparativo_modelos_baches.ipynb
├── src/
│   ├── datos.py
│   ├── metricas.py
│   └── preparar_dataset.py
├── data/
├── results/
└── requirements.txt
```

## Entorno de ejecución

- Google Colab con GPU T4.
- Token de lectura de Hugging Face guardado en los Secretos de Colab como `HF_TOKEN`.
- Las dependencias se instalan dentro del cuaderno. Las versiones exactas quedan en `results/requirements_colab.txt`.

## Pasos de ejecución

1. Descargo el dataset desde Kaggle y subo el ZIP a Colab con el nombre `dataset.zip`.
2. Abro `notebooks/01_comparativo_modelos_baches.ipynb` en Google Colab con GPU T4.
3. Guardo el token de Hugging Face en los Secretos de Colab como `HF_TOKEN`.
4. Ejecuto todas las celdas. Al final se descarga `entregables_urbanos.zip` con los datos y los resultados.
5. Copio las carpetas `data/` y `results/` de ese ZIP a esta carpeta.

Para generar solo el manifiesto del dataset, desde esta carpeta:

```bash
python -m src.preparar_dataset --raiz data/raw --salida data
```

## Dataset

| Campo | Valor |
|---|---|
| Nombre | Pothole Detection Dataset |
| Autor | Atulya Kumar |
| Fuente | https://www.kaggle.com/datasets/atulyakumar98/pothole-detection-dataset |
| Licencia | CC0: Public Domain |
| Fecha de descarga | 10 de octubre de 2026 |
| Contenido | 681 archivos en dos carpetas: `normal` (352 imágenes de calles lisas) y `potholes` (calles con baches) |

Según el autor, las imágenes se tomaron de internet para un proyecto universitario.

- **Manifiesto:** `data/dataset.csv`, una fila por imagen. También en `data/dataset_baches.xlsx`, con hojas de diccionario, origen y resumen.
- **Diccionario de datos:** `data/diccionario_datos.csv`, con la descripción de cada campo.
- **Limpieza:** se quitan imágenes dañadas, duplicados exactos y duplicados con etiquetas contradictorias. Las cantidades quedan en `data/resumen_dataset.json`.
- **División:** 70 % `train`, 15 % `val` y 15 % `test`, con semilla 42 y proporción de clases conservada.
- Las imágenes originales no se suben al repositorio; `data/raw/` está en el `.gitignore`.

## Resultados

Todo se genera en `results/`:

| Archivo | Contenido |
|---|---|
| `metricas_modelos.csv` | Accuracy, precision, recall, F1, AUC, latencia, memoria, tamaño y licencia de cada modelo |
| `umbrales_modelos.csv` | Precision y recall con distintos umbrales de decisión |
| `predicciones_test.csv` | Probabilidad de bache de cada modelo para cada imagen de prueba |
| `metricas_por_modelo.png`, `eficiencia_vs_precision.png`, `matrices_confusion.png`, `errores_mejor_modelo.png` | Gráficas |
| `requirements_colab.txt`, `entorno.json` | Versiones y GPU usadas |

## Limitaciones

- Las imágenes vienen de internet y algunas no son representativas (por ejemplo, anuncios junto a una carretera o un accidente etiquetados como `sin_dano`).
- Solo se eliminan duplicados exactos; puede haber imágenes muy parecidas entre `train` y `test`.
- El conjunto de prueba es pequeño: el 15 % del dataset.
- No está probado con calles de México.
- Clasifica la foto completa; no ubica ni cuenta baches.
- Las latencias dependen de la GPU y de la carga de Colab en el momento de la medición.