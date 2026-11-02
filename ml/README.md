# Comparativo de modelos preentrenados para detectar daño en calles

Parte de **UrbanOS**, una plataforma municipal que utiliza datos e inteligencia artificial para apoyar el cuidado de las calles. Este proyecto compara tres modelos preentrenados de Hugging Face en una tarea de visión por computadora aplicada a la detección de baches.

## Caso de uso

Antes de contar y ubicar cada bache en un mapa, UrbanOS necesita determinar si una imagen muestra un bache o una calle sin daño visible.

* **Rama de IA:** visión por computadora.
* **Tarea:** clasificación binaria de imágenes.
* **Clase positiva:** `bache`.
* **Clase negativa:** `sin_dano`.
* **Criterio principal:** reducir los falsos negativos, es decir, los baches reales que el modelo no detecta.

## Modelos comparados

| Modelo      | Identificador en Hugging Face | Tamaño relativo |
| ----------- | ----------------------------- | --------------- |
| MobileNetV2 | `google/mobilenet_v2_1.0_224` | Ligero          |
| ResNet-50   | `microsoft/resnet-50`         | Mediano         |
| ViT-Base    | `google/vit-base-patch16-224` | Grande          |

Los modelos se utilizan como extractores de características congelados. Sobre las características extraídas se entrena una regresión logística; el parámetro `C` se selecciona con la partición de validación.

## Estructura del proyecto

```text
ml/
├── notebooks/
│   ├── 01_comparativo_modelos_baches.ipynb          # versión para ejecución local
│   └── colab/
│       └── 01_comparativo_modelos_baches_colab.ipynb  # versión para Google Colab
├── src/
│   ├── datos.py
│   ├── metricas.py
│   └── preparar_dataset.py
├── data/
├── results/            # ejecución local
├── results_colab/      # ejecución en Google Colab
├── requirements.txt
└── README.md
```

## Dataset

| Campo                           | Valor                                                                   |
| ------------------------------- | ----------------------------------------------------------------------- |
| Nombre                          | Pothole Detection Dataset                                               |
| Autor indicado en Kaggle        | Atulya Kumar                                                            |
| Fuente                          | https://www.kaggle.com/datasets/atulyakumar98/pothole-detection-dataset |
| Licencia indicada por la fuente | CC0: Public Domain                                                      |
| Fecha de descarga registrada    | 10 de octubre de 2026                                                   |
| Imágenes originales reportadas  | 681 (352 en `normal` y 329 en `potholes`)                               |
| Imágenes tras la limpieza       | 676 (se eliminaron 5 duplicados exactos)                                |

| Partición     | Bache | Sin daño | Total |
| ------------- | ----- | -------- | ----- |
| Entrenamiento | 229   | 243      | 472   |
| Validación    | 49    | 53       | 102   |
| Prueba        | 49    | 53       | 102   |

El manifiesto preparado se encuentra en `data/dataset.csv`; también se incluyen archivos auxiliares para documentar los campos, el origen y el resumen del conjunto de datos.

* **Manifiesto:** `data/dataset.csv`, con una fila por imagen.
* **Libro de datos:** `data/dataset_baches.xlsx`.
* **Diccionario:** `data/diccionario_datos.csv`.
* **Origen:** `data/origen_dataset.json`.
* **Resumen:** `data/resumen_dataset.json`.
* **Particiones:** entrenamiento, validación y prueba (70 / 15 / 15), con semilla 42 y proporción de clases conservada.

Las imágenes originales no se incluyen en el repositorio. Cada persona que reproduzca el experimento debe obtener el dataset desde Kaggle y colocarlo localmente en `data/raw/dataset.zip`.

## Entorno de ejecución

El experimento se ejecutó dos veces: en Google Colab y en un equipo local con Windows. Los dos entornos se documentan por separado.

| Elemento                         | Google Colab (gratuito) | Equipo local                     |
| -------------------------------- | ----------------------- | -------------------------------- |
| GPU                              | Tesla T4                | NVIDIA GeForce RTX 4050 Laptop   |
| Python                           | 3.13.15                 | 3.11.9                           |
| PyTorch                          | 2.11.0+cu130            | 2.11.0+cu128                     |
| transformers                     | 5.18.0                  | 5.19.0                           |
| datasets                         | 4.8.5                   | 5.1.0                            |
| huggingface_hub                  | 1.33.0                  | 2.2.0                            |
| scikit-learn                     | 1.6.1                   | 1.9.1                            |
| pandas                           | 2.2.3                   | 3.0.6                            |
| numpy                            | 2.1.3                   | 2.4.6                            |
| Tamaño de lote en la medición de velocidad | 32            | 8                                |

Las versiones exactas de cada ejecución están en `results_colab/requirements_colab.txt` y `results/requirements_local.txt`.

### Ejecución en Google Colab

Notebook en Colab: https://colab.research.google.com/drive/1eBDj48CTk_DGeFUtUMpB0lI9jhPoZQic?usp=sharing

1. Descargar el dataset desde Kaggle y subir el archivo a Colab con el nombre `dataset.zip`.
2. Seleccionar una GPU en *Entorno de ejecución → Cambiar tipo de entorno de ejecución*.
3. Guardar un token de lectura de Hugging Face en los *Secretos* de Colab con el nombre `HF_TOKEN` y habilitar el acceso para el notebook.
4. Ejecutar todas las celdas. Al finalizar se descarga `entregables_urbanos.zip` con los datos y los resultados.

### Ejecución local

Requisitos: Python 3.11, Git, conexión a internet para descargar el dataset y los modelos, y una GPU NVIDIA compatible con CUDA (recomendada; también es posible ejecutar en CPU, con tiempos mayores).

Desde la carpeta `ml`, crear y activar un entorno virtual:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
```

Instalar las dependencias:

```powershell
pip install -r requirements.txt
```

El archivo instala las versiones de PyTorch y Torchvision que se publican en PyPI para la plataforma. Para usar la GPU, instalar las mismas versiones con el soporte CUDA correspondiente desde el selector oficial: https://pytorch.org/get-started/locally/

Si Hugging Face solicita autenticación para descargar algún modelo, configurar el token mediante el mecanismo oficial de autenticación o una variable de entorno. No incluir tokens ni credenciales en el repositorio.

## Pasos de ejecución local

### 1. Obtener el repositorio

```powershell
git clone https://github.com/E-SalazarDev/urbanos.git
cd urbanos\ml
```

### 2. Descargar el dataset

Descargar el dataset desde Kaggle:

https://www.kaggle.com/datasets/atulyakumar98/pothole-detection-dataset

Crear la carpeta `data/raw/` si no existe y colocar allí el archivo original con el nombre `dataset.zip`.

### 3. Ejecutar el experimento

Abrir `notebooks/01_comparativo_modelos_baches.ipynb` en VS Code o Jupyter, seleccionar el intérprete del entorno `.venv` y ejecutar las celdas en orden. El notebook descomprime el ZIP, prepara el manifiesto, carga los modelos preentrenados, extrae características, ajusta la regresión logística y evalúa el rendimiento. La primera ejecución puede tardar más por las descargas de modelos y el procesamiento de imágenes.

### 4. Preparar solo el manifiesto (opcional)

Con las imágenes ya extraídas en `data/raw/normal/` y `data/raw/potholes/`, desde la carpeta `ml`:

```powershell
python -m src.preparar_dataset --raiz data/raw --salida data --semilla 42
```

Si los archivos preparados ya existen, revisar antes de ejecutar si se desea regenerarlos.

### 5. Consultar los resultados

Los resultados se guardan en `results/` (ejecución local) y `results_colab/` (ejecución en Colab). Incluyen métricas, gráficas, predicciones, umbrales de decisión e información del entorno. El archivo `entregables_urbanos.zip` reúne el código, los datos preparados y los resultados, pero no las imágenes originales.

## Resultados

Las métricas de clasificación son idénticas en las dos ejecuciones (misma semilla y mismas particiones). Cambian las mediciones de tiempo y memoria, que dependen del hardware.

| Modelo      | Accuracy | Precision | Recall | F1    | AUC   | Falsas alarmas | Baches no detectados |
| ----------- | -------- | --------- | ------ | ----- | ----- | -------------- | -------------------- |
| MobileNetV2 | 0.961    | 0.959     | 0.959  | 0.959 | 0.995 | 2              | 2                    |
| ResNet-50   | 0.990    | 0.980     | 1.000  | 0.990 | 0.997 | 1              | 0                    |
| ViT-Base    | 0.990    | 1.000     | 0.980  | 0.990 | 0.998 | 0              | 1                    |

Latencia mediana por imagen, de punta a punta (preprocesado, modelo y clasificador):

| Modelo      | GPU Colab T4 | GPU local RTX 4050 | CPU en Colab | CPU local |
| ----------- | ------------ | ------------------ | ------------ | --------- |
| MobileNetV2 | 17.1 ms      | 18.7 ms            | 34.1 ms      | 27.8 ms   |
| ResNet-50   | 9.8 ms       | 16.1 ms            | 158.1 ms     | 60.0 ms   |
| ViT-Base    | 16.7 ms      | 14.7 ms            | 370.5 ms     | 152.8 ms  |

La velocidad por lote y la memoria de GPU no son comparables entre ejecuciones porque se midieron con lotes de distinto tamaño (32 en Colab y 8 en local).

Archivos generados en cada carpeta de resultados:

| Archivo                       | Contenido                                               |
| ----------------------------- | ------------------------------------------------------- |
| `metricas_modelos.csv`        | Métricas comparativas de los modelos                    |
| `umbrales_modelos.csv`        | Métricas con distintos umbrales de decisión             |
| `predicciones_test.csv`       | Predicciones sobre el conjunto de prueba                |
| `metricas_por_modelo.png`     | Comparación de métricas                                 |
| `eficiencia_vs_precision.png` | Comparación de eficiencia y rendimiento                 |
| `matrices_confusion.png`      | Matrices de confusión                                   |
| `errores_mejor_modelo.png`    | Ejemplos de errores del modelo seleccionado             |
| `requirements_local.txt` / `requirements_colab.txt` | Versiones de dependencias registradas en cada entorno |
| `entorno.json`                | Información del entorno de ejecución                    |

## Conclusiones

* Los tres modelos preentrenados distinguen un bache de una calle sin daño sin necesidad de reentrenarse: obtuvieron entre 96.1 % y 99.0 % de accuracy en las 102 imágenes de prueba.
* Un ajuste mínimo, que consiste en congelar el modelo y entrenar una regresión logística sobre sus características, fue suficiente para este experimento y es rápido y reproducible.
* **ResNet-50 es el modelo recomendado.** Fue el único que no dejó pasar ningún bache (recall 1.00), tiene F1 de 0.990 y licencia Apache-2.0, y es considerablemente más ligero y rápido en CPU que ViT-Base.
* ViT-Base empata con ResNet-50 en aciertos (101 de 102) con 3.7 veces más parámetros y una latencia en CPU mayor en ambos entornos.
* MobileNetV2 es el más ligero (8.9 MB) y el más rápido en CPU en ambos entornos, a cambio de 3 aciertos menos en la prueba.
* Con 102 imágenes de prueba, las diferencias entre ResNet-50 y ViT-Base son de una sola imagen y no son concluyentes. Los resultados deben tomarse como una primera referencia y validarse con fotos propias antes de usarse en UrbanOS.

## Limitaciones

* Las imágenes proceden de internet y pueden contener ejemplos poco representativos o etiquetas incorrectas; por ejemplo, la única falsa alarma de ResNet-50 es una fotografía de un accidente etiquetada como `sin_dano`.
* La eliminación de duplicados exactos no garantiza que no existan imágenes muy similares entre las particiones.
* El conjunto de prueba es relativamente pequeño, por lo que las métricas tienen incertidumbre.
* El rendimiento no está validado específicamente para calles de México.
* El sistema clasifica la imagen completa; no localiza ni cuenta individualmente los baches.
* La latencia depende del hardware, el modelo y las condiciones de ejecución.
* Los resultados de este experimento no garantizan el mismo rendimiento en condiciones reales de operación.