"""A2: clasificación visual de las imágenes con máscara vacía. Ejecutar desde la raíz."""
import argparse
import csv
from collections import Counter

import cv2
import matplotlib.pyplot as plt

from config import DATA_DIR, REPO_DIR, exigir_archivos

# Argumento para permitir un archivo CSV independiente por revisor
parser = argparse.ArgumentParser()
parser.add_argument("--revisor", default="", help="Nombre del revisor para sufijo del CSV")
args = parser.parse_args()
sufijo = f"_{args.revisor}" if args.revisor else ""
SALIDA = REPO_DIR / "docs" / f"clasificacion_vacias{sufijo}.csv"

OPCIONES = {
    "1": "sin_ulcera_visible",
    "2": "ulcera_sin_anotar",
    "3": "dudosa",
}

# 1) Calcular las imágenes con máscara vacía
casos = []
for conjunto in ("train", "validation"):
    for ruta in exigir_archivos(DATA_DIR / conjunto / "labels"):
        m = cv2.imread(str(ruta), cv2.IMREAD_GRAYSCALE)
        if m is None:
            raise SystemExit(f"ERROR: no se pudo leer {ruta}")
        if cv2.countNonZero(m) == 0:
            casos.append((conjunto, ruta.name))
print(f"Imágenes con máscara vacía: {len(casos)}")

# 2) Retomar lo ya clasificado
resp = {}
if SALIDA.exists():
    with open(SALIDA, newline="", encoding="utf-8") as f:
        for fila in csv.DictReader(f):
            resp[(fila["conjunto"], fila["archivo"])] = fila["categoria"]


def guardar():
    SALIDA.parent.mkdir(parents=True, exist_ok=True)
    with open(SALIDA, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["conjunto", "archivo", "categoria"])
        for caso in casos:
            if caso in resp:
                w.writerow([*caso, resp[caso]])


pos = next((i for i, c in enumerate(casos) if c not in resp), len(casos))
fig, ax = plt.subplots(figsize=(8, 8))


def mostrar():
    ax.clear()
    ax.axis("off")
    if pos >= len(casos):
        ax.text(0.5, 0.5, "Listo. Cierra la ventana.",
                ha="center", va="center", fontsize=16)
    else:
        conjunto, nombre = casos[pos]
        ruta = DATA_DIR / conjunto / "images" / nombre
        img = cv2.imread(str(ruta))
        if img is None:
            raise SystemExit(f"ERROR: no se pudo leer {ruta}")
        ax.imshow(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
        previa = resp.get(casos[pos], "sin clasificar")
        ax.set_title(
            f"{pos + 1}/{len(casos)}  {conjunto} {nombre}  [{previa}]\n"
            "1 = sin úlcera visible | 2 = úlcera sin anotar | 3 = dudosa | "
            "z = atrás | q = salir",
            fontsize=10,
        )
    fig.canvas.draw_idle()


def on_key(event):
    global pos
    if event.key in OPCIONES and pos < len(casos):
        resp[casos[pos]] = OPCIONES[event.key]
        guardar()
        pos += 1
    elif event.key == "z" and pos > 0:
        pos -= 1
    else:
        return
    mostrar()


fig.canvas.mpl_connect("key_press_event", on_key)
mostrar()
plt.show()
guardar()

print(Counter(resp.values()))
print(f"Guardado en: {SALIDA}")