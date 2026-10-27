from pathlib import Path
import cv2
import matplotlib.pyplot as plt
from config import DATA_DIR as BASE_DIR, REPORTS_DIR

train_vacias = [
    "0092.png", "0131.png", "0223.png", "0281.png", "0335.png",
    "0361.png", "0457.png", "0502.png", "0564.png", "0600.png",
    "0701.png", "0725.png", "0736.png", "0778.png", "0832.png",
    "0899.png", "0912.png", "0931.png", "0950.png"
]

val_vacias = [
    "0128.png", "0417.png", "0483.png", "0533.png", "0869.png"
]

casos = (
    [("train", nombre) for nombre in train_vacias] +
    [("validation", nombre) for nombre in val_vacias]
)

fig, axes = plt.subplots(4, 6, figsize=(16, 11))

for ax, (conjunto, nombre) in zip(axes.flat, casos):

    ruta = BASE_DIR / conjunto / "images" / nombre

    imagen = cv2.imread(str(ruta))
    imagen = cv2.cvtColor(imagen, cv2.COLOR_BGR2RGB)

    ax.imshow(imagen)
    ax.set_title(f"{conjunto}\n{nombre}", fontsize=9)
    ax.axis("off")

plt.suptitle(
    "Imágenes con máscara vacía en FUSeg",
    fontsize=16
)

plt.tight_layout()

salida = REPORTS_DIR / "mascaras_vacias_revision.png"

plt.savefig(
    salida,
    dpi=250
)

print("Gráfica guardada en:")
print(salida)

plt.show()