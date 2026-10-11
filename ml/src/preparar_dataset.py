"""
Genera el manifiesto del dataset a partir de una carpeta de imágenes.

Uso, desde la carpeta ml/:
    python -m src.preparar_dataset --raiz data/raw --salida data
"""
import argparse
import json
from pathlib import Path

import pandas as pd

from .datos import DICCIONARIO, construir_manifiesto


def main():
    parser = argparse.ArgumentParser(description="Prepara el dataset de baches y crea su manifiesto.")
    parser.add_argument("--raiz", default="data/raw")
    parser.add_argument("--salida", default="data")
    parser.add_argument("--semilla", type=int, default=42)
    parser.add_argument("--max-por-clase", type=int, default=None)
    args = parser.parse_args()

    salida = Path(args.salida)
    salida.mkdir(parents=True, exist_ok=True)

    manifiesto, resumen = construir_manifiesto(args.raiz, args.semilla, args.max_por_clase)
    manifiesto.to_csv(salida / "dataset.csv", index=False)
    pd.DataFrame(DICCIONARIO, columns=["campo", "tipo", "descripcion"]).to_csv(
        salida / "diccionario_datos.csv", index=False
    )
    (salida / "resumen_dataset.json").write_text(json.dumps(resumen, indent=2, ensure_ascii=False), encoding="utf-8")

    print(json.dumps(resumen, indent=2, ensure_ascii=False))
    print(pd.crosstab(manifiesto["particion"], manifiesto["clase"]))


if __name__ == "__main__":
    main()
