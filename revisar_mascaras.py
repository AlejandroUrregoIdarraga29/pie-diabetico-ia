from pathlib import Path
import cv2
import numpy as np
from config import DATA_DIR as BASE_DIR

def revisar(carpeta, nombre):

    print("\n" + "=" * 60)
    print(nombre)
    print("=" * 60)

    mascaras = sorted(carpeta.glob("*"))

    mascaras_vacias = []
    mascaras_valores_raros = []
    coberturas = []

    for ruta in mascaras:

        if not ruta.is_file():
            continue

        mascara = cv2.imread(
            str(ruta),
            cv2.IMREAD_GRAYSCALE
        )

        if mascara is None:
            continue

        valores = np.unique(mascara)

        pixeles_ulcera = np.count_nonzero(mascara)

        cobertura = (
            pixeles_ulcera / mascara.size
        ) * 100

        coberturas.append(
            (ruta.name, cobertura)
        )

        # Máscara completamente vacía
        if pixeles_ulcera == 0:
            mascaras_vacias.append(
                ruta.name
            )

        # Buscar valores diferentes de 0 y 255
        valores_raros = [
            int(v)
            for v in valores
            if v not in [0, 255]
        ]

        if valores_raros:

            mascaras_valores_raros.append(
                (
                    ruta.name,
                    valores_raros
                )
            )

    print(
        f"Máscaras vacías: "
        f"{len(mascaras_vacias)}"
    )

    if mascaras_vacias:
        print(mascaras_vacias)

    print(
        f"\nMáscaras con valores distintos "
        f"de 0 y 255: "
        f"{len(mascaras_valores_raros)}"
    )

    for archivo, valores in mascaras_valores_raros:

        print(
            f"{archivo} -> {valores}"
        )

    coberturas.sort(
        key=lambda x: x[1]
    )

    print("\n5 máscaras con menor cobertura:")

    for archivo, cobertura in coberturas[:5]:

        print(
            f"{archivo}: "
            f"{cobertura:.6f} %"
        )


revisar(
    BASE_DIR / "train" / "labels",
    "TRAIN"
)

revisar(
    BASE_DIR / "validation" / "labels",
    "VALIDATION"
)