"""A2: detección de imágenes duplicadas o casi duplicadas. Ejecutar desde la raíz."""
import csv
from collections import Counter

import cv2
import numpy as np

from config import DATA_DIR, REPO_DIR, exigir_archivos

SALIDA = REPO_DIR / "docs" / "duplicados.csv"
LADO = 16      # hash de 16x16 = 256 bits
UMBRAL = 25    # bits distintos para marcar un par como casi duplicado


def hash_imagen(ruta):
    img = cv2.imread(str(ruta), cv2.IMREAD_GRAYSCALE)
    if img is None:
        raise SystemExit(f"ERROR: no se pudo leer {ruta}")
    ys, xs = np.where(img > 8)  # quita la banda negra de relleno
    if len(xs):
        img = img[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    peq = cv2.resize(img, (LADO + 1, LADO), interpolation=cv2.INTER_AREA)
    return (peq[:, 1:] > peq[:, :-1]).flatten()


items, hashes = [], []
for conjunto in ("train", "validation", "test"):
    for ruta in exigir_archivos(DATA_DIR / conjunto / "images"):
        items.append((conjunto, ruta.name))
        hashes.append(hash_imagen(ruta))

H = np.array(hashes, dtype=np.int32)
s = H.sum(axis=1)
dist = s[:, None] + s[None, :] - 2 * (H @ H.T)  # distancia de Hamming

i_idx, j_idx = np.triu_indices(len(items), 1)
mask = dist[i_idx, j_idx] <= UMBRAL
pares = []
for i, j in zip(i_idx[mask], j_idx[mask]):
    (ca, na), (cb, nb) = items[i], items[j]
    tipo = "-".join(sorted((ca, cb)))
    pares.append([ca, na, cb, nb, int(dist[i, j]), tipo])
pares.sort(key=lambda p: p[4])

SALIDA.parent.mkdir(parents=True, exist_ok=True)
with open(SALIDA, "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["conjunto_a", "archivo_a", "conjunto_b", "archivo_b", "distancia", "tipo"])
    w.writerows(pares)

print(f"Pares casi duplicados (distancia <= {UMBRAL}): {len(pares)}")
print(Counter(p[5] for p in pares))
print(f"Guardado en: {SALIDA}")