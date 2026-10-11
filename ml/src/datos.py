"""Preparación del dataset de baches."""
import hashlib
from pathlib import Path

import pandas as pd
from PIL import Image
from sklearn.model_selection import train_test_split

EXTENSIONES = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}
CLASES = ["sin_dano", "bache"]
PALABRAS_SIN_DANO = ("normal", "plain", "good", "no_pothole", "nopothole", "sin_dano", "sano")
PALABRAS_BACHE = ("pothole", "bache")

DICCIONARIO = [
    ("id", "texto", "Identificador de la imagen dentro del dataset (img_00001, img_00002, ...)."),
    ("ruta_relativa", "texto", "Ruta de la imagen dentro de la carpeta data/raw."),
    ("clase", "texto", "Clase de la imagen: 'bache' o 'sin_dano', deducida del nombre de la carpeta original."),
    ("etiqueta", "entero", "Clase en número: 1 = bache, 0 = sin_dano."),
    ("particion", "texto", "Parte del dataset: 'train', 'val' o 'test'."),
    ("ancho_px", "entero", "Ancho de la imagen en píxeles."),
    ("alto_px", "entero", "Alto de la imagen en píxeles."),
    ("tamano_kb", "decimal", "Tamaño del archivo en kilobytes."),
    ("md5", "texto", "Huella del archivo, usada para detectar imágenes repetidas."),
]
COLUMNAS = [campo for campo, _, _ in DICCIONARIO]


def clase_desde_ruta(ruta_relativa):
    """Deduce la clase a partir de los nombres de las carpetas."""
    partes = [p.lower() for p in Path(ruta_relativa).parts[:-1]]
    for parte in partes:
        if any(palabra in parte for palabra in PALABRAS_SIN_DANO):
            return "sin_dano"
    for parte in partes:
        if any(palabra in parte for palabra in PALABRAS_BACHE):
            return "bache"
    return None


def escanear_imagenes(raiz):
    """Lista las imágenes de la carpeta con su clase."""
    raiz = Path(raiz)
    filas = []
    for ruta in sorted(raiz.rglob("*")):
        if not ruta.is_file() or ruta.suffix.lower() not in EXTENSIONES:
            continue
        relativa = ruta.relative_to(raiz)
        clase = clase_desde_ruta(relativa)
        if clase is not None:
            filas.append({"ruta_relativa": relativa.as_posix(), "clase": clase})
    return pd.DataFrame(filas, columns=["ruta_relativa", "clase"])


def agregar_metadatos(df, raiz):
    """Agrega tamaño, dimensiones y huella md5 de cada imagen."""
    raiz = Path(raiz)
    filas = []
    for relativa in df["ruta_relativa"]:
        ruta = raiz / relativa
        contenido = ruta.read_bytes()
        ancho = alto = None
        valida = True
        try:
            with Image.open(ruta) as imagen:
                imagen.load()
                ancho, alto = imagen.size
        except Exception:
            valida = False
        filas.append({
            "md5": hashlib.md5(contenido).hexdigest(),
            "tamano_kb": round(len(contenido) / 1024, 1),
            "ancho_px": ancho,
            "alto_px": alto,
            "valida": valida,
        })
    return pd.concat([df.reset_index(drop=True), pd.DataFrame(filas)], axis=1)


def depurar(df):
    """Quita imágenes dañadas, duplicados exactos y duplicados con clases contradictorias."""
    resumen = {"imagenes_encontradas": int(len(df))}

    df = df[df["valida"]].copy()
    resumen["invalidas_eliminadas"] = resumen["imagenes_encontradas"] - int(len(df))

    clases_por_huella = df.groupby("md5")["clase"].nunique()
    contradictorias = clases_por_huella[clases_por_huella > 1].index
    antes = len(df)
    df = df[~df["md5"].isin(contradictorias)].copy()
    resumen["contradictorias_eliminadas"] = int(antes - len(df))

    antes = len(df)
    df = df.drop_duplicates(subset="md5", keep="first").copy()
    resumen["duplicadas_eliminadas"] = int(antes - len(df))

    df = df.drop(columns="valida").reset_index(drop=True)
    df["ancho_px"] = df["ancho_px"].astype(int)
    df["alto_px"] = df["alto_px"].astype(int)
    resumen["imagenes_finales"] = int(len(df))
    return df, resumen


def dividir(df, semilla=42, prop_val=0.15, prop_test=0.15):
    """Divide en train, val y test conservando la proporción de clases."""
    df = df.copy()
    resto, test = train_test_split(df, test_size=prop_test, stratify=df["clase"], random_state=semilla)
    train, val = train_test_split(
        resto, test_size=prop_val / (1 - prop_test), stratify=resto["clase"], random_state=semilla
    )
    df.loc[train.index, "particion"] = "train"
    df.loc[val.index, "particion"] = "val"
    df.loc[test.index, "particion"] = "test"
    return df


def construir_manifiesto(raiz, semilla=42, max_por_clase=None):
    """Escanea, depura y divide el dataset; devuelve el manifiesto y un resumen."""
    df = escanear_imagenes(raiz)
    if df.empty:
        raise ValueError(f"No se encontraron imágenes clasificables en {raiz}.")
    conteo = df["clase"].value_counts()
    if len(conteo) < 2:
        raise ValueError(f"Solo se encontró una clase ({conteo.index[0]}).")

    if max_por_clase:
        df = pd.concat(
            [g.sample(min(len(g), max_por_clase), random_state=semilla) for _, g in df.groupby("clase")]
        )

    df = agregar_metadatos(df, raiz)
    df, resumen = depurar(df)
    if df["clase"].value_counts().min() < 10:
        raise ValueError("Hay menos de 10 imágenes en alguna clase.")

    df = dividir(df, semilla=semilla).sort_values("ruta_relativa").reset_index(drop=True)
    df["id"] = [f"img_{i + 1:05d}" for i in range(len(df))]
    df["etiqueta"] = df["clase"].map({"sin_dano": 0, "bache": 1}).astype(int)
    resumen["semilla"] = semilla
    resumen["max_por_clase"] = max_por_clase
    return df[COLUMNAS], resumen
