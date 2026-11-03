"""A3: evalúa un modelo guardado con metricas.py.
Uso (desde la raíz): python evaluar_modelo.py [ruta_modelo]"""
import csv
import json
import sys
from pathlib import Path

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
PARTICION = REPO_DIR / "docs" / "particion_evaluacion.csv"

with open(PARTICION, newline="", encoding="utf-8") as f:
    filas = list(csv.DictReader(f))
nombres = [r["archivo"] for r in filas]
limpia = np.array([r["incluido"] == "1" for r in filas])


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
P = modelo.predict(X, batch_size=8, verbose=0)[..., 0] > UMBRAL


def evaluar(idx):
    tp = fp = fn = 0
    dices, ious = [], []
    for i in np.where(idx)[0]:
        a, b, c = conteos(Y[i], P[i])
        tp, fp, fn = tp + a, fp + b, fn + c
        m = desde_conteos(a, b, c)
        dices.append(m["dice"])
        ious.append(m["iou"])
    return {
        "imagenes": int(idx.sum()),
        "global": desde_conteos(tp, fp, fn),
        "por_imagen": {"dice": float(np.mean(dices)), "iou": float(np.mean(ious))},
    }


res = {
    "modelo": ruta_modelo.name,
    "umbral": UMBRAL,
    "validation_completa": evaluar(np.ones(len(nombres), dtype=bool)),
    "validation_limpia": evaluar(limpia),
}

for clave in ("validation_completa", "validation_limpia"):
    r = res[clave]
    g, p = r["global"], r["por_imagen"]
    print(f"\n{clave} ({r['imagenes']} imágenes)")
    print(f"  global      Dice {g['dice']:.4f}  IoU {g['iou']:.4f}  "
          f"precisión {g['precision']:.4f}  recall {g['recall']:.4f}")
    print(f"  por imagen  Dice {p['dice']:.4f}  IoU {p['iou']:.4f}")
    print(f"  chequeo: Dice/(2-Dice) = {g['dice'] / (2 - g['dice']):.4f} (debe igualar el IoU global)")

salida = RESULTADOS_DIR / f"evaluacion_{ruta_modelo.stem}.json"
with open(salida, "w", encoding="utf-8") as f:
    json.dump(res, f, indent=4)
print(f"\nGuardado en: {salida}")