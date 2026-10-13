from pathlib import Path
import cv2
import numpy as np
import matplotlib.pyplot as plt

BASE_DIR = Path(
    r"C:\Users\alejo\pie_diabetico_ia\wound-segmentation\data\Foot Ulcer Segmentation Challenge"
)

ruta_imagen = BASE_DIR / "validation" / "images" / "0233.png"
ruta_mascara = BASE_DIR / "validation" / "labels" / "0233.png"

imagen = cv2.imread(str(ruta_imagen))
mascara = cv2.imread(str(ruta_mascara), cv2.IMREAD_GRAYSCALE)

imagen = cv2.cvtColor(imagen, cv2.COLOR_BGR2RGB)

# Separar los dos valores encontrados
pixeles_32 = (mascara == 32)
pixeles_255 = (mascara == 255)

print("Píxeles valor 32:", np.sum(pixeles_32))
print("Píxeles valor 255:", np.sum(pixeles_255))

plt.figure(figsize=(15, 5))

plt.subplot(1, 3, 1)
plt.imshow(imagen)
plt.title("Imagen original - 0233.png")
plt.axis("off")

plt.subplot(1, 3, 2)
plt.imshow(pixeles_32, cmap="gray")
plt.title("Píxeles con valor 32")
plt.axis("off")

plt.subplot(1, 3, 3)
plt.imshow(pixeles_255, cmap="gray")
plt.title("Píxeles con valor 255")
plt.axis("off")

plt.tight_layout()
plt.show()