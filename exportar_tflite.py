"""A5: exporta el modelo a TFLite (float32) y lo compara con el original.
Uso (desde la raíz): python exportar_tflite.py [ruta_modelo] [N]"""
import csv
import sys
from pathlib import Path

import numpy as np
import tensorflow as tf

from config import DATA_DIR, MODELOS_DIR, REPO_DIR, asegurar_carpetas
from metricas import conteos, desde_conteos

asegurar_carpetas()
TAM = 256
UMBRAL = 0.5
ruta_modelo = (
    Path(sys.argv[1]) if len(sys.argv) > 1
    else MODELOS_DIR / "unet_fuseg_baseline.keras"
)
N = int(sys.argv[2]) if len(sys.argv) > 2 else 10
ruta_tflite = ruta_modelo.with_suffix(".tflite")
PARTICION = REPO_DIR / "docs" / "particion_evaluacion.csv"

if not ruta_modelo.exists():
    raise SystemExit(f"ERROR: no existe {ruta_modelo}")

# 1) Convertir
modelo = tf.keras.models.load_model(ruta_modelo, compile=False)
convertidor = tf.lite.TFLiteConverter.from_keras_model(modelo)
ruta_tflite.write_bytes(convertidor.convert())
print(f"TFLite guardado: {ruta_tflite} ({ruta_tflite.stat().st_size / 1e6:.2f} MB)")

# 2) Elegir N imágenes repartidas de la validation limpia
with open(PARTICION, newline="", encoding="utf-8") as f:
    nombres = [r["archivo"] for r in csv.DictReader(f) if r["incluido"] == "1"]
idx = np.linspace(0, len(nombres) - 1, N).astype(int)
nombres = [nombres[i] for i in idx]


def cargar(nombre):
    """Mismo preprocesamiento que entrenar_unet.py."""
    ri = DATA_DIR / "validation" / "images" / nombre
    img = tf.image.decode_png(tf.io.read_file(str(ri)), channels=3)
    img = tf.image.resize(tf.cast(img, tf.float32), [TAM, TAM], method="bilinear") / 255.0
    return img.numpy()


X = np.stack([cargar(n) for n in nombres])

# 3) Predecir con ambos
PROB_KERAS = modelo.predict(X, batch_size=4, verbose=0)[..., 0]

interp = tf.lite.Interpreter(model_path=str(ruta_tflite))
interp.allocate_tensors()
ent = interp.get_input_details()[0]
sal = interp.get_output_details()[0]
print(f"Entrada TFLite: {ent['shape']} {ent['dtype'].__name__} | salida: {sal['shape']}")


def predecir_tflite(x):
    interp.set_tensor(ent["index"], x[None].astype(np.float32))
    interp.invoke()
    return interp.get_tensor(sal["index"])[0, ..., 0]


# 4) Comparar
peor_dif = 0.0
dif_mascara = 0
print(f"\n{'imagen':10s} {'dif máx prob':>13s} {'px distintos':>13s} {'Dice entre máscaras':>20s}")
for i, nombre in enumerate(nombres):
    pk = PROB_KERAS[i]
    pt = predecir_tflite(X[i])
    dif = float(np.abs(pk - pt).max())
    mk, mt = pk > UMBRAL, pt > UMBRAL
    distintos = int(np.sum(mk != mt))
    dice = desde_conteos(*conteos(mk, mt))["dice"]
    peor_dif = max(peor_dif, dif)
    dif_mascara += distintos
    print(f"{nombre:10s} {dif:13.2e} {distintos:13d} {dice:20.4f}")

print(f"\nMayor diferencia de probabilidad: {peor_dif:.2e}")
print(f"Píxeles de máscara distintos en total: {dif_mascara}")
print("RESULTADO:", "equivalente" if peor_dif < 1e-3 and dif_mascara == 0 else "REVISAR diferencias")