"""A2: auditoría de máscaras de FUSeg. Ejecutar desde la raíz del repo."""
import csv

import cv2
import numpy as np

from config import DATA_DIR, REPO_DIR, exigir_archivos

ESPERADAS_VACIAS = {"train": 19, "validation": 5}
KERNEL = np.ones((3, 3), np.uint8)
filas = []

for conjunto in ("train", "validation"):
    mascaras = exigir_archivos(DATA_DIR / conjunto / "labels")
    imagenes = exigir_archivos(DATA_DIR / conjunto / "images")
    sin_par = sorted({a.stem for a in mascaras} ^ {a.stem for a in imagenes})

    formas, vacias, raras = set(), [], []
    for ruta in mascaras:
        m = cv2.imread(str(ruta), cv2.IMREAD_GRAYSCALE)
        if m is None:
            raise SystemExit(f"ERROR: no se pudo leer {ruta}")
        formas.add(m.shape)
        px_ulcera = int(np.count_nonzero(m))
        px_255 = int(np.count_nonzero(m == 255))
        otros = (m != 0) & (m != 255)
        px_otros = int(np.count_nonzero(otros))

        if px_ulcera == 0:
            vacias.append(ruta.stem)
            filas.append([conjunto, ruta.name, "vacia", 0, 0, 0, 0, ""])
        if px_otros:
            cerca = cv2.dilate((m == 255).astype(np.uint8), KERNEL) > 0
            junto = int(np.count_nonzero(otros & cerca))
            ys, xs = np.where(otros)
            bbox = f"x{xs.min()}-{xs.max()} y{ys.min()}-{ys.max()}"
            raras.append((ruta.stem, px_otros, junto))
            filas.append(
                [conjunto, ruta.name, "valores_raros", px_ulcera, px_255, px_otros, junto, bbox]
            )

    esperado = ESPERADAS_VACIAS[conjunto]
    estado = "OK" if len(vacias) == esperado else "NO COINCIDE"
    print(f"\n=== {conjunto.upper()} ===")
    print(f"Máscaras: {len(mascaras)} | imágenes: {len(imagenes)} | tamaños: {sorted(formas)}")
    print(f"Sin par imagen/máscara: {sin_par or 'ninguno'}")
    print(f"Máscaras vacías: {len(vacias)} (esperadas {esperado}: {estado})")
    print(vacias)
    for nombre, px, junto in raras:
        print(f"Valores distintos de 0 y 255 en {nombre}: {px} px, {junto} pegados a un píxel 255")

test_dir = DATA_DIR / "test"
n_test = len(list((test_dir / "images").glob("*.png")))
print(f"\nTEST: {n_test} imágenes | ¿existe carpeta labels? {(test_dir / 'labels').exists()}")

salida = REPO_DIR / "docs" / "auditoria_mascaras.csv"
salida.parent.mkdir(parents=True, exist_ok=True)
with open(salida, "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["conjunto", "archivo", "motivo", "px_ulcera", "px_255",
                "px_otros", "px_otros_junto_a_255", "bbox_otros"])
    w.writerows(filas)
print(f"\nTabla guardada en: {salida}")