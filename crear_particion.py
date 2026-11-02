"""A2: partición de evaluación sin fuga. Ejecutar desde la raíz."""
import csv
from collections import Counter

from config import DATA_DIR, REPO_DIR, exigir_archivos

DUP = REPO_DIR / "docs" / "duplicados.csv"
VACIAS = REPO_DIR / "docs" / "clasificacion_vacias.csv"
SALIDA = REPO_DIR / "docs" / "particion_evaluacion.csv"
DIST_MAX = 10  # más estricto que el 25 del detector, para evitar falsos positivos

excluir = {}  # archivo de validation -> motivo

with open(DUP, newline="", encoding="utf-8") as f:
    for r in csv.DictReader(f):
        if int(r["distancia"]) > DIST_MAX:
            continue
        if r["tipo"] == "train-validation":
            excluir.setdefault(r["archivo_b"], "duplicado_en_train")
            print("train-validation:", r["archivo_a"], r["archivo_b"], r["distancia"])
        elif r["tipo"] == "validation-validation":
            excluir.setdefault(r["archivo_b"], "duplicado_en_validation")
            print("validation-validation:", r["archivo_a"], r["archivo_b"], r["distancia"])

with open(VACIAS, newline="", encoding="utf-8") as f:
    for r in csv.DictReader(f):
        if r["conjunto"] == "validation" and r["categoria"] == "ulcera_sin_anotar":
            excluir.setdefault(r["archivo"], "mascara_vacia_con_ulcera")

archivos = [p.name for p in exigir_archivos(DATA_DIR / "validation" / "images")]
with open(SALIDA, "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["archivo", "incluido", "motivo"])
    for a in archivos:
        w.writerow([a, 0 if a in excluir else 1, excluir.get(a, "")])

print(Counter(excluir.values()))
print(f"Validation limpia: {len(archivos) - len(excluir)} de {len(archivos)}")
print(f"Guardado en: {SALIDA}")