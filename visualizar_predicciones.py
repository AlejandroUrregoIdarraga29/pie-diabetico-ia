"""A4: compara foto, máscara real y predicción (mejores y peores casos).
Uso (desde la raíz): python visualizar_predicciones.py [ruta_modelo] [N]"""
import csv
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")  # sin ventanas: solo guarda archivos
import matplotlib.pyplot as plt
import numpy as np
import tensorflow as tf

from config import DATA_DIR, MODELOS_DIR, REPO_DIR, RESULTADOS_DIR, asegurar_carpetas
from metricas import conteos, desde_conteos

asegurar_carpetas()
TAM = 256
UMBRAL = 0.5
ruta_modelo = (
    Path(sys.argv[1]) if len(sys.argv) > 1
    else MODELOS_DIR / "unet_fuseg_baseline.keras"
)
N = int(sys.argv[2]) if len(sys.argv) > 2 else 4  # N buenos y N malos
PARTICION = REPO_DIR / "docs" / "particion_evaluacion.csv"
SALIDA = RESULTADOS_DIR / "visualizaciones"

if not ruta_modelo.exists():
    raise SystemExit(f"ERROR: no existe {ruta_modelo}. Entrena primero con entrenar_unet.py")
if not PARTICION.exists():
    raise SystemExit(f"ERROR: no existe {PARTICION}. ¿Estás en la rama con A2 integrada?")

with open(PARTICION, newline="", encoding="utf-8") as f:
    nombres = [r["archivo"] for r in csv.DictReader(f) if r["incluido"] == "1"]


def cargar(nombre):
    """Mismo preprocesamiento que entrenar_unet.py."""
    ri = DATA_DIR / "validation" / "images" / nombre
    rm = DATA_DIR / "validation" / "labels" / nombre
    img = tf.image.decode_png(tf.io.read_file(str(ri)), channels=3)
    img = tf.image.resize(tf.cast(img, tf.float32), [TAM, TAM], method="bilinear") / 255.0
    m = tf.image.decode_png(tf.io.read_file(str(rm)), channels=1)
    m = tf.image.resize(tf.cast(m > 0, tf.float32), [TAM, TAM], method="nearest")
    return img.numpy(), m.numpy()[..., 0] > 0.5


datos = [cargar(n) for n in nombres]
X = np.stack([d[0] for d in datos])
Y = np.stack([d[1] for d in datos])

modelo = tf.keras.models.load_model(ruta_modelo, compile=False)
PROB = modelo.predict(X, batch_size=8, verbose=0)[..., 0]
P = PROB > UMBRAL

dices = np.array([desde_conteos(*conteos(Y[i], P[i]))["dice"] for i in range(len(nombres))])
orden = np.argsort(dices)
peores = list(orden[:N])
mejores = list(orden[::-1][:N])

SALIDA.mkdir(parents=True, exist_ok=True)


def dibujar(i, etiqueta):
    fig, ejes = plt.subplots(1, 4, figsize=(16, 4.5))   
    ejes[0].imshow(X[i])
    ejes[0].set_title(f"Foto {nombres[i]}")
    ejes[1].imshow(Y[i], cmap="gray")
    ejes[1].set_title("Máscara real")
    ejes[2].imshow(P[i], cmap="gray")
    ejes[2].set_title("Predicción")
    im = ejes[3].imshow(PROB[i], cmap="magma", vmin=0, vmax=1)
    ejes[3].set_title(f"Probabilidad (máx {PROB[i].max():.2f})")
    fig.colorbar(im, ax=ejes[3], fraction=0.046)
    for ax in ejes:
        ax.axis("off")
    fig.suptitle(f"{etiqueta}: Dice de la imagen = {dices[i]:.3f}", fontsize=12)
    fig.tight_layout()
    ruta = SALIDA / f"{etiqueta}_{nombres[i].replace('.png', '')}.png"
    fig.savefig(ruta, dpi=150)
    plt.close(fig)
    return ruta


print(f"Imágenes evaluadas: {len(nombres)} | Dice mediano por imagen: {np.median(dices):.3f}")
for etiqueta, grupo in (("bueno", mejores), ("malo", peores)):
    for i in grupo:
        print(f"{etiqueta:5s} {nombres[i]}  Dice {dices[i]:.3f}  -> {dibujar(i, etiqueta)}")
print(f"\nGuardado en: {SALIDA}")