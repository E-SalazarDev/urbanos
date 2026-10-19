import argparse
import hashlib
import json
import zipfile
from datetime import date
from io import BytesIO
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from PIL import Image, ImageOps
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

EXTENSIONES = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}
PALABRAS_SIN_DANO = ("normal", "plain", "good", "no_pothole", "nopothole", "sin_dano", "sano")
PALABRAS_BACHE = ("pothole", "bache")

TAMANO_REDUCIDO = 128
LADO_BLOQUE = 8
MIN_LADO_PX = 64
MAX_RELACION_ASPECTO = 4.0
UMBRAL_HAMMING = 4
FACTOR_IQR = 1.5

COLUMNAS_ARCHIVO = ["ancho_px", "alto_px", "relacion_aspecto", "tamano_kb"]
COLUMNAS_IMAGEN = [
    "rojo_media", "verde_media", "azul_media", "rojo_desv", "verde_desv", "azul_desv",
    "brillo_media", "brillo_desv", "contraste", "proporcion_oscura", "proporcion_clara",
    "saturacion_media", "densidad_bordes", "nitidez", "entropia", "textura_bloques",
]

DICCIONARIO = [
    ("ruta_relativa", "texto", "Ruta de la imagen dentro de la carpeta de imágenes."),
    ("clase", "texto", "Clase original, deducida de la carpeta: 'bache' o 'sin_dano'."),
    ("etiqueta", "entero", "Clase codificada: 1 = bache, 0 = sin_dano."),
    ("md5", "texto", "Huella exacta del archivo; detecta duplicados idénticos."),
    ("huella", "texto", "Huella perceptual (dHash de 64 bits); detecta imágenes casi idénticas."),
    ("ancho_px", "entero", "Ancho original en píxeles."),
    ("alto_px", "entero", "Alto original en píxeles."),
    ("relacion_aspecto", "decimal", "Ancho dividido entre alto."),
    ("tamano_kb", "decimal", "Peso del archivo en kilobytes."),
    ("rojo_media", "decimal", "Promedio del canal rojo (0 a 1)."),
    ("verde_media", "decimal", "Promedio del canal verde (0 a 1)."),
    ("azul_media", "decimal", "Promedio del canal azul (0 a 1)."),
    ("rojo_desv", "decimal", "Desviación estándar del canal rojo."),
    ("verde_desv", "decimal", "Desviación estándar del canal verde."),
    ("azul_desv", "decimal", "Desviación estándar del canal azul."),
    ("brillo_media", "decimal", "Brillo promedio en escala de grises (0 a 1)."),
    ("brillo_desv", "decimal", "Variación del brillo."),
    ("contraste", "decimal", "Diferencia entre los percentiles 95 y 5 del brillo."),
    ("proporcion_oscura", "decimal", "Fracción de píxeles con brillo menor a 0.25."),
    ("proporcion_clara", "decimal", "Fracción de píxeles con brillo mayor a 0.75."),
    ("saturacion_media", "decimal", "Saturación promedio del color (0 a 1)."),
    ("densidad_bordes", "decimal", "Fracción de píxeles donde el brillo cambia bruscamente."),
    ("nitidez", "decimal", "Varianza del laplaciano; mide el detalle fino."),
    ("entropia", "decimal", "Entropía del histograma de brillo, en bits."),
    ("textura_bloques", "decimal", "Promedio de la variación del brillo dentro de bloques de 8x8."),
    ("n_variables_atipicas", "entero", "Cuántas variables de la fila quedan fuera de 1.5 veces el rango intercuartil."),
]


def clase_desde_ruta(ruta_relativa):
   
    partes = [p.lower() for p in Path(ruta_relativa).parts[:-1]]
    for parte in partes:
        if any(palabra in parte for palabra in PALABRAS_SIN_DANO):
            return "sin_dano"
    for parte in partes:
        if any(palabra in parte for palabra in PALABRAS_BACHE):
            return "bache"
    return None


def huella_perceptual(imagen):
    
    miniatura = np.asarray(imagen.convert("L").resize((9, 8), Image.BILINEAR), dtype=np.int16)
    bits = (miniatura[:, 1:] > miniatura[:, :-1]).flatten()
    return int("".join("1" if b else "0" for b in bits), 2)


def calcular_caracteristicas(imagen):
  
    reducida = imagen.convert("RGB").resize((TAMANO_REDUCIDO, TAMANO_REDUCIDO), Image.BILINEAR)
    rgb = np.asarray(reducida, dtype=np.float32) / 255.0
    gris = np.asarray(reducida.convert("L"), dtype=np.float32) / 255.0
    saturacion = np.asarray(reducida.convert("HSV"), dtype=np.float32)[..., 1] / 255.0

    gy, gx = np.gradient(gris)
    magnitud = np.hypot(gx, gy)
    laplaciano = (
        -4 * gris[1:-1, 1:-1] + gris[:-2, 1:-1] + gris[2:, 1:-1] + gris[1:-1, :-2] + gris[1:-1, 2:]
    )
    histograma, _ = np.histogram(gris, bins=32, range=(0, 1))
    probabilidades = histograma / histograma.sum()
    probabilidades = probabilidades[probabilidades > 0]
    n = TAMANO_REDUCIDO // LADO_BLOQUE
    bloques = gris.reshape(n, LADO_BLOQUE, n, LADO_BLOQUE).std(axis=(1, 3))

    return {
        "rojo_media": float(rgb[..., 0].mean()),
        "verde_media": float(rgb[..., 1].mean()),
        "azul_media": float(rgb[..., 2].mean()),
        "rojo_desv": float(rgb[..., 0].std()),
        "verde_desv": float(rgb[..., 1].std()),
        "azul_desv": float(rgb[..., 2].std()),
        "brillo_media": float(gris.mean()),
        "brillo_desv": float(gris.std()),
        "contraste": float(np.percentile(gris, 95) - np.percentile(gris, 5)),
        "proporcion_oscura": float((gris < 0.25).mean()),
        "proporcion_clara": float((gris > 0.75).mean()),
        "saturacion_media": float(saturacion.mean()),
        "densidad_bordes": float((magnitud > 0.1).mean()),
        "nitidez": float(laplaciano.var()),
        "entropia": float(-(probabilidades * np.log2(probabilidades)).sum()),
        "textura_bloques": float(bloques.mean()),
    }


def medir_imagen(ruta):
    
    contenido = ruta.read_bytes()
    fila = {
        "md5": hashlib.md5(contenido).hexdigest(),
        "tamano_kb": round(len(contenido) / 1024, 1),
        "valida": True,
    }
    try:
        with Image.open(BytesIO(contenido)) as original:
            ancho, alto = original.size
            original.draft("RGB", (TAMANO_REDUCIDO * 2, TAMANO_REDUCIDO * 2))
            imagen = ImageOps.exif_transpose(original)
            imagen.load()
            fila["ancho_px"] = ancho
            fila["alto_px"] = alto
            fila["relacion_aspecto"] = round(ancho / alto, 4)
            fila["huella"] = f"{huella_perceptual(imagen):016x}"
            fila.update(calcular_caracteristicas(imagen))
    except Exception:
        fila["valida"] = False
    return fila


def _extraer_zip_si_hace_falta(raiz):
    hay_imagenes = any(p.suffix.lower() in EXTENSIONES for p in raiz.rglob("*") if p.is_file())
    zip_dataset = raiz / "dataset.zip"
    if not hay_imagenes and zip_dataset.exists():
        with zipfile.ZipFile(zip_dataset) as z:
            z.extractall(raiz)


def construir_inventario(raiz):
    
    raiz = Path(raiz)
    _extraer_zip_si_hace_falta(raiz)
    filas = []
    for ruta in sorted(raiz.rglob("*")):
        if not ruta.is_file() or ruta.suffix.lower() not in EXTENSIONES:
            continue
        relativa = ruta.relative_to(raiz)
        clase = clase_desde_ruta(relativa)
        if clase is None:
            continue
        fila = {"ruta_relativa": relativa.as_posix(), "clase": clase}
        fila.update(medir_imagen(ruta))
        filas.append(fila)
    if not filas:
        raise ValueError(f"No se encontraron imágenes clasificables en {raiz}.")
    df = pd.DataFrame(filas)
    df["etiqueta"] = (df["clase"] == "bache").astype(int)
    return df


def _agrupar_casi_duplicados(huellas, umbral):
  
    padre = list(range(len(huellas)))

    def buscar(i):
        while padre[i] != i:
            padre[i] = padre[padre[i]]
            i = padre[i]
        return i

    for i in range(len(huellas)):
        for j in range(i + 1, len(huellas)):
            if bin(huellas[i] ^ huellas[j]).count("1") <= umbral:
                padre[buscar(j)] = buscar(i)
    return [buscar(i) for i in range(len(huellas))]


def limpiar(df):

    df = df.sort_values("ruta_relativa").reset_index(drop=True)
    eliminadas = []

    def quitar(actual, mascara, motivo):
        if mascara.any():
            eliminadas.append(actual[mascara].assign(motivo=motivo))
        return actual[~mascara]

    actual = quitar(df, ~df["valida"], "imagen_invalida")
    actual = quitar(actual, actual[["ancho_px", "alto_px"]].min(axis=1) < MIN_LADO_PX, "lado_menor_al_minimo")

    razon = actual["relacion_aspecto"]
    actual = quitar(actual, (razon > MAX_RELACION_ASPECTO) | (razon < 1 / MAX_RELACION_ASPECTO), "relacion_de_aspecto_extrema")

    finitas = np.isfinite(actual[COLUMNAS_IMAGEN].to_numpy(dtype=float)).all(axis=1)
    actual = quitar(actual, pd.Series(~finitas, index=actual.index), "caracteristicas_no_validas")

    clases_por_md5 = actual.groupby("md5")["clase"].nunique()
    actual = quitar(actual, actual["md5"].map(clases_por_md5) > 1, "duplicada_exacta_con_etiquetas_contradictorias")
    actual = quitar(actual, actual.duplicated("md5", keep="first"), "duplicada_exacta")

    grupo = pd.Series(_agrupar_casi_duplicados([int(h, 16) for h in actual["huella"]], UMBRAL_HAMMING), index=actual.index)
    clases_por_grupo = actual.groupby(grupo)["clase"].nunique()
    actual = quitar(actual, grupo.map(clases_por_grupo) > 1, "casi_duplicada_con_etiquetas_contradictorias")
    grupo = grupo[actual.index]
    actual = quitar(actual, grupo.duplicated(keep="first"), "casi_duplicada")

    limpio = actual.drop(columns="valida").reset_index(drop=True)
    for columna in ("ancho_px", "alto_px", "etiqueta"):
        limpio[columna] = limpio[columna].astype(int)
    for columna in ["relacion_aspecto", "tamano_kb"] + COLUMNAS_IMAGEN:
        limpio[columna] = limpio[columna].astype(float)

    eliminadas = pd.concat(eliminadas, ignore_index=True) if eliminadas else df.iloc[0:0].assign(motivo="")
    reporte = {
        "filas_iniciales": int(len(df)),
        "filas_finales": int(len(limpio)),
        "eliminadas_por_regla": {k: int(v) for k, v in eliminadas["motivo"].value_counts().items()},
        "balance_inicial": {k: int(v) for k, v in df["clase"].value_counts().items()},
        "balance_final": {k: int(v) for k, v in limpio["clase"].value_counts().items()},
        "umbrales": {
            "lado_minimo_px": MIN_LADO_PX,
            "relacion_aspecto_maxima": MAX_RELACION_ASPECTO,
            "distancia_hamming_casi_duplicadas": UMBRAL_HAMMING,
            "factor_iqr_atipicos": FACTOR_IQR,
        },
    }
    return limpio, eliminadas, reporte


def marcar_atipicos(df):
 
    conteo = np.zeros(len(df), dtype=int)
    for columna in COLUMNAS_ARCHIVO + COLUMNAS_IMAGEN:
        q1, q3 = df[columna].quantile([0.25, 0.75])
        rango = q3 - q1
        fuera = (df[columna] < q1 - FACTOR_IQR * rango) | (df[columna] > q3 + FACTOR_IQR * rango)
        conteo += fuera.to_numpy().astype(int)
    return df.assign(n_variables_atipicas=conteo)


def hash_archivo(ruta):
    
    contenido = Path(ruta).read_bytes().replace(b"\r\n", b"\n")
    return hashlib.sha256(contenido).hexdigest()


def guardar(original, limpio, eliminadas, reporte, carpeta):
    
    carpeta = Path(carpeta)
    ini, limp = carpeta / "datos_ini", carpeta / "datos_limp"
    ini.mkdir(parents=True, exist_ok=True)
    limp.mkdir(parents=True, exist_ok=True)

    original.to_csv(ini / "dataset_original.csv", index=False, lineterminator="\n")
    limpio.to_csv(limp / "dataset_limpio.csv", index=False, lineterminator="\n")
    eliminadas.to_csv(limp / "filas_eliminadas.csv", index=False, lineterminator="\n")
    pd.DataFrame(DICCIONARIO, columns=["campo", "tipo", "descripcion"]).to_csv(
        limp / "diccionario_datos.csv", index=False, lineterminator="\n"
    )

    sha = hash_archivo(limp / "dataset_limpio.csv")
    version = {"version": f"v1-{sha[:8]}", "sha256": sha, "fecha": date.today().isoformat(), "reporte": reporte}
    (limp / "version.json").write_text(json.dumps(version, indent=2, ensure_ascii=False), encoding="utf-8")
    return version


def generar_graficas(original, limpio, eliminadas, carpeta):
   
    carpeta = Path(carpeta)
    carpeta.mkdir(parents=True, exist_ok=True)
    colores = {"sin_dano": "#16A34A", "bache": "#DC2626"}
    nombres = {"sin_dano": "Sin daño", "bache": "Bache"}

    fig, eje = plt.subplots(figsize=(8, 3.5))
    if len(eliminadas):
        conteo = eliminadas["motivo"].value_counts().sort_values()
        eje.barh(conteo.index, conteo.values, color="#2563EB")
        for i, valor in enumerate(conteo.values):
            eje.text(valor, i, f" {valor}", va="center")
    else:
        eje.text(0.5, 0.5, "No se eliminó ninguna fila", ha="center", va="center")
        eje.axis("off")
    eje.set_title("Filas eliminadas por regla de limpieza")
    fig.tight_layout()
    fig.savefig(carpeta / "01_motivos_eliminacion.png", dpi=150)
    plt.close(fig)

    fig, eje = plt.subplots(figsize=(6, 4))
    posiciones = np.arange(2)
    for desplazamiento, (titulo, datos) in zip((-0.2, 0.2), (("Antes", original), ("Después", limpio))):
        valores = [int((datos["clase"] == c).sum()) for c in ("sin_dano", "bache")]
        barras = eje.bar(posiciones + desplazamiento, valores, width=0.4, label=titulo)
        eje.bar_label(barras)
    eje.set_xticks(posiciones)
    eje.set_xticklabels([nombres["sin_dano"], nombres["bache"]])
    eje.set_title("Balance de clases antes y después de limpiar")
    eje.legend()
    fig.tight_layout()
    fig.savefig(carpeta / "02_balance_clases.png", dpi=150)
    plt.close(fig)

    fig, ejes = plt.subplots(2, 2, figsize=(9, 6))
    for eje, (columna, titulo, logaritmo) in zip(
        ejes.flat,
        [("ancho_px", "Ancho (px)", True), ("alto_px", "Alto (px)", True),
         ("tamano_kb", "Tamaño del archivo (KB)", True), ("relacion_aspecto", "Relación de aspecto", False)],
    ):
        for clase in ("sin_dano", "bache"):
            valores = limpio.loc[limpio["clase"] == clase, columna]
            valores = np.log10(valores) if logaritmo else valores
            eje.hist(valores, bins=25, alpha=0.6, color=colores[clase], label=nombres[clase])
        eje.set_title(titulo + (" · escala log10" if logaritmo else ""))
        eje.legend()
    fig.tight_layout()
    fig.savefig(carpeta / "03_distribucion_archivo.png", dpi=150)
    plt.close(fig)

    fig, ejes = plt.subplots(2, 3, figsize=(11, 6))
    for eje, columna in zip(ejes.flat, ["brillo_media", "contraste", "densidad_bordes", "nitidez", "entropia", "proporcion_oscura"]):
        datos = [limpio.loc[limpio["clase"] == c, columna] for c in ("sin_dano", "bache")]
        caja = eje.boxplot(datos, patch_artist=True)
        for parche, clase in zip(caja["boxes"], ("sin_dano", "bache")):
            parche.set_facecolor(colores[clase])
            parche.set_alpha(0.6)
        eje.set_xticks([1, 2])
        eje.set_xticklabels([nombres["sin_dano"], nombres["bache"]])
        eje.set_title(columna)
    fig.suptitle("Características por clase (los puntos son valores atípicos)")
    fig.tight_layout()
    fig.savefig(carpeta / "04_caracteristicas_por_clase.png", dpi=150)
    plt.close(fig)

    with np.errstate(invalid="ignore", divide="ignore"):
        correlacion = np.nan_to_num(np.corrcoef(limpio[COLUMNAS_IMAGEN].to_numpy(dtype=float), rowvar=False))
    fig, eje = plt.subplots(figsize=(8, 7))
    imagen = eje.imshow(correlacion, cmap="coolwarm", vmin=-1, vmax=1)
    eje.set_xticks(range(len(COLUMNAS_IMAGEN)))
    eje.set_xticklabels(COLUMNAS_IMAGEN, rotation=90)
    eje.set_yticks(range(len(COLUMNAS_IMAGEN)))
    eje.set_yticklabels(COLUMNAS_IMAGEN)
    fig.colorbar(imagen, ax=eje, label="Correlación")
    eje.set_title("Correlación entre características de la imagen")
    fig.tight_layout()
    fig.savefig(carpeta / "05_correlaciones.png", dpi=150)
    plt.close(fig)

    estandarizado = StandardScaler().fit_transform(limpio[COLUMNAS_IMAGEN].to_numpy(dtype=float))
    pca = PCA(n_components=2, random_state=42)
    componentes = pca.fit_transform(estandarizado)
    fig, eje = plt.subplots(figsize=(6.5, 5))
    for clase in ("sin_dano", "bache"):
        mascara = (limpio["clase"] == clase).to_numpy()
        eje.scatter(componentes[mascara, 0], componentes[mascara, 1], s=14, alpha=0.6, color=colores[clase], label=nombres[clase])
    eje.set_xlabel(f"Componente 1 ({pca.explained_variance_ratio_[0] * 100:.0f} % de la varianza)")
    eje.set_ylabel(f"Componente 2 ({pca.explained_variance_ratio_[1] * 100:.0f} % de la varianza)")
    eje.set_title("PCA de las características de imagen")
    eje.legend()
    fig.tight_layout()
    fig.savefig(carpeta / "06_pca_clases.png", dpi=150)
    plt.close(fig)

    fig, eje = plt.subplots(figsize=(6.5, 4))
    conteo = limpio["n_variables_atipicas"].value_counts().sort_index()
    eje.bar(conteo.index, conteo.values, color="#7C3AED")
    eje.set_xlabel("Variables atípicas por imagen")
    eje.set_ylabel("Imágenes")
    eje.set_title("Anomalías: cuántas variables se salen del rango normal")
    fig.tight_layout()
    fig.savefig(carpeta / "07_atipicos.png", dpi=150)
    plt.close(fig)


def main():
    parser = argparse.ArgumentParser(description="Prepara el dataset de la Actividad 5.")
    parser.add_argument("--imagenes", default="../data/raw", help="Carpeta con las imágenes (o con dataset.zip).")
    parser.add_argument("--salida", default="datos", help="Carpeta que contendrá datos_ini y datos_limp.")
    parser.add_argument("--graficas", default="evidencias/graficas", help="Carpeta de las gráficas.")
    args = parser.parse_args()

    original = construir_inventario(args.imagenes)
    limpio, eliminadas, reporte = limpiar(original)
    limpio = marcar_atipicos(limpio)
    version = guardar(original, limpio, eliminadas, reporte, args.salida)
    generar_graficas(original, limpio, eliminadas, args.graficas)

    print(f"Versión del dataset: {version['version']}")
    print(f"Filas: {reporte['filas_iniciales']} -> {reporte['filas_finales']}")
    print("Eliminadas por regla:", reporte["eliminadas_por_regla"] or "ninguna")
    print("Balance final:", reporte["balance_final"])


if __name__ == "__main__":
    main()