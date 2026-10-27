from pathlib import Path
import cv2
import numpy as np
import matplotlib.pyplot as plt
from config import DATA_DIR as BASE_DIR

# ==========================================================
# CASOS CON MÁSCARA VACÍA
# ==========================================================

casos_train = [
    "0092.png",
    "0131.png",
    "0223.png",
    "0281.png",
    "0335.png",
]

casos_val = [
    "0128.png",
    "0417.png",
    "0483.png",
    "0533.png",
    "0869.png",
]


def mostrar_casos(conjunto, archivos):

    for nombre in archivos:

        ruta_img = BASE_DIR / conjunto / "images" / nombre
        ruta_mask = BASE_DIR / conjunto / "labels" / nombre

        imagen = cv2.imread(str(ruta_img))
        mascara = cv2.imread(
            str(ruta_mask),
            cv2.IMREAD_GRAYSCALE
        )

        imagen = cv2.cvtColor(
            imagen,
            cv2.COLOR_BGR2RGB
        )

        print("\n" + "=" * 60)
        print(f"{conjunto.upper()} - {nombre}")
        print("=" * 60)

        print(
            "Valores máscara:",
            np.unique(mascara)
        )

        print(
            "Píxeles distintos de cero:",
            np.count_nonzero(mascara)
        )

        plt.figure(figsize=(10, 5))

        plt.subplot(1, 2, 1)
        plt.imshow(imagen)
        plt.title(f"Imagen original - {nombre}")
        plt.axis("off")

        plt.subplot(1, 2, 2)
        plt.imshow(mascara, cmap="gray")
        plt.title("Máscara")
        plt.axis("off")

        plt.tight_layout()
        plt.show()


# ==========================================================
# REVISAR ALGUNOS CASOS VACÍOS
# ==========================================================

mostrar_casos(
    "train",
    casos_train
)

mostrar_casos(
    "validation",
    casos_val
)


# ==========================================================
# REVISAR MÁSCARA 0233
# ==========================================================

ruta_0233 = (
    BASE_DIR
    / "validation"
    / "labels"
    / "0233.png"
)

mascara_0233 = cv2.imread(
    str(ruta_0233),
    cv2.IMREAD_GRAYSCALE
)

valores, cantidades = np.unique(
    mascara_0233,
    return_counts=True
)

print("\n" + "=" * 60)
print("ANÁLISIS DETALLADO DE 0233.png")
print("=" * 60)

for valor, cantidad in zip(
    valores,
    cantidades
):

    print(
        f"Valor {valor}: "
        f"{cantidad} píxeles"
    )