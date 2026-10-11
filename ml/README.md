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
│   └── 01_comparativo_modelos_baches.ipynb
├── src/
│   ├── datos.py
│   ├── metricas.py
│   └── preparar_dataset.py
├── data/
├── results/
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
| Imágenes originales reportadas  | 681                                                                     |

El dataset contiene imágenes de calles sin baches y calles con baches. El manifiesto preparado se encuentra en `data/dataset.csv`; también se incluyen archivos auxiliares para documentar los campos, el origen y el resumen del conjunto de datos.

* **Manifiesto:** `data/dataset.csv`, con una fila por imagen.
* **Libro de datos:** `data/dataset_baches.xlsx`.
* **Diccionario:** `data/diccionario_datos.csv`.
* **Origen:** `data/origen_dataset.json`.
* **Resumen:** `data/resumen_dataset.json`.
* **Particiones:** entrenamiento, validación y prueba, con semilla 42 y proporción de clases conservada.

Las imágenes originales no se incluyen en el repositorio. Cada persona que reproduzca el experimento debe obtener el dataset desde Kaggle y colocarlo localmente en `data/raw/dataset.zip`.

## Entorno de ejecución

El experimento se desarrolló localmente en Windows con Python 3.11, una GPU NVIDIA RTX 4050 Laptop y PyTorch con CUDA 12.8.

### Requisitos

* Python 3.11.
* Git.
* Conexión a internet para descargar el dataset y los modelos preentrenados.
* GPU NVIDIA compatible con CUDA, recomendada para acelerar el procesamiento. También es posible ejecutar en CPU, aunque puede tardar considerablemente más.

### Instalación

Desde la carpeta `ml`, crear y activar un entorno virtual:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
```

Instalar las dependencias del proyecto:

```powershell
pip install -r requirements.txt
```

Instalar PyTorch y Torchvision de acuerdo con la plataforma y la GPU. Para reproducir la configuración CUDA 12.8 utilizada durante el desarrollo, consultar el selector oficial de instalación de PyTorch: https://pytorch.org/get-started/locally/

Las versiones utilizadas durante el experimento se documentan en `results/requirements_local.txt` y `results/entorno.json`.

Si Hugging Face solicita autenticación para descargar algún modelo, configurar el token mediante el mecanismo oficial de autenticación o una variable de entorno. No incluir tokens ni credenciales en el repositorio.

## Pasos de ejecución

### 1. Obtener el repositorio

Clonar el repositorio y entrar en la carpeta `ml`:

```powershell
git clone <URL_DEL_REPOSITORIO>
cd <REPOSITORIO>\ml
```

Sustituir los marcadores por la URL y el nombre reales del repositorio.

### 2. Descargar el dataset

Descargar el dataset desde Kaggle:

https://www.kaggle.com/datasets/atulyakumar98/pothole-detection-dataset

Crear la carpeta `data/raw/` si no existe y colocar allí el archivo original con el nombre `dataset.zip`.

### 3. Preparar los datos

Con el entorno virtual activado y desde la carpeta `ml`, ejecutar:

```powershell
python -m src.preparar_dataset --raiz data/raw --salida data --semilla 42
```

Este comando prepara el manifiesto y los archivos auxiliares del dataset. Si los archivos preparados ya existen, revisar antes de ejecutar si se desea regenerarlos.

### 4. Ejecutar el experimento

Abrir `notebooks/01_comparativo_modelos_baches.ipynb` en VS Code o Jupyter, seleccionar el intérprete del entorno `.venv` y ejecutar las celdas en orden.

El notebook carga los modelos preentrenados, extrae características, ajusta la regresión logística y evalúa el rendimiento. La primera ejecución puede tardar más por las descargas de modelos y el procesamiento de imágenes.

### 5. Consultar los resultados

Los resultados se guardan en `results/`. Incluyen métricas, gráficas, predicciones, umbrales de decisión e información del entorno.

El archivo `results/entregables_urbanos.zip` reúne el código, los datos preparados y los resultados, pero no las imágenes originales. Para reproducir el experimento desde cero, es necesario descargar el dataset por separado.

## Resultados generados

| Archivo                       | Contenido                                               |
| ----------------------------- | ------------------------------------------------------- |
| `metricas_modelos.csv`        | Métricas comparativas de los modelos                    |
| `umbrales_modelos.csv`        | Métricas con distintos umbrales de decisión             |
| `predicciones_test.csv`       | Predicciones sobre el conjunto de prueba                |
| `metricas_por_modelo.png`     | Comparación de métricas                                 |
| `eficiencia_vs_precision.png` | Comparación de eficiencia y rendimiento                 |
| `matrices_confusion.png`      | Matrices de confusión                                   |
| `errores_mejor_modelo.png`    | Ejemplos de errores del modelo seleccionado             |
| `requirements_local.txt`      | Versiones de dependencias registradas del entorno local |
| `entorno.json`                | Información del entorno de ejecución                    |

## Limitaciones

* Las imágenes proceden de internet y pueden contener ejemplos poco representativos o etiquetas incorrectas.
* La eliminación de duplicados exactos no garantiza que no existan imágenes muy similares entre las particiones.
* El conjunto de prueba es relativamente pequeño, por lo que las métricas tienen incertidumbre.
* El rendimiento no está validado específicamente para calles de México.
* El sistema clasifica la imagen completa; no localiza ni cuenta individualmente los baches.
* La latencia depende del hardware, el modelo y las condiciones de ejecución.
* Los resultados de este experimento no garantizan el mismo rendimiento en condiciones reales de operación.
