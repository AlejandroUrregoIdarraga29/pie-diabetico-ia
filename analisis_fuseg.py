from pathlib import Path
from collections import Counter

import cv2
import numpy as np
import matplotlib.pyplot as plt


# ==========================================================
# RUTAS
# ==========================================================

BASE_DIR = Path(
    r"C:\Users\alejo\pie_diabetico_ia\wound-segmentation\data\Foot Ulcer Segmentation Challenge"
)

SALIDA = Path(r"C:\Users\alejo\pie_diabetico_ia")


# ==========================================================
# FUNCIÓN PARA LISTAR IMÁGENES
# ==========================================================

EXTENSIONES = {".png", ".jpg", ".jpeg", ".bmp"}


def obtener_archivos(carpeta):
    return sorted([
        archivo
        for archivo in carpeta.iterdir()
        if archivo.is_file()
        and archivo.suffix.lower() in EXTENSIONES
    ])


# ==========================================================
# ANALIZAR IMÁGENES
# ==========================================================

def analizar_imagenes(carpeta):
    archivos = obtener_archivos(carpeta)

    resoluciones = []
    errores = []

    for archivo in archivos:

        imagen = cv2.imread(str(archivo))

        if imagen is None:
            errores.append(archivo.name)
            continue

        alto, ancho = imagen.shape[:2]

        resoluciones.append(
            (ancho, alto)
        )

    return archivos, resoluciones, errores


# ==========================================================
# ANALIZAR MÁSCARAS
# ==========================================================

def analizar_mascaras(carpeta):
    archivos = obtener_archivos(carpeta)

    coberturas = []
    resoluciones = []
    valores_encontrados = set()
    errores = []

    for archivo in archivos:

        mascara = cv2.imread(
            str(archivo),
            cv2.IMREAD_GRAYSCALE
        )

        if mascara is None:
            errores.append(archivo.name)
            continue

        alto, ancho = mascara.shape

        resoluciones.append(
            (ancho, alto)
        )

        # Valores diferentes encontrados
        valores = np.unique(mascara)

        for valor in valores:
            valores_encontrados.add(
                int(valor)
            )

        # Cantidad de píxeles de úlcera
        pixeles_ulcera = np.count_nonzero(
            mascara
        )

        pixeles_totales = mascara.size

        porcentaje = (
            pixeles_ulcera
            / pixeles_totales
        ) * 100

        coberturas.append(
            porcentaje
        )

    return (
        archivos,
        resoluciones,
        coberturas,
        valores_encontrados,
        errores
    )


# ==========================================================
# MOSTRAR RESUMEN DE RESOLUCIONES
# ==========================================================

def mostrar_resoluciones(nombre, resoluciones):

    contador = Counter(resoluciones)

    print("\n" + "=" * 65)
    print(f"RESOLUCIONES - {nombre}")
    print("=" * 65)

    print(
        f"Cantidad total analizada: "
        f"{len(resoluciones)}"
    )

    print(
        f"Resoluciones diferentes: "
        f"{len(contador)}"
    )

    for resolucion, cantidad in contador.most_common():

        print(
            f"{resolucion[0]} x "
            f"{resolucion[1]} -> "
            f"{cantidad} imágenes"
        )


# ==========================================================
# TRAIN
# ==========================================================

train_images_dir = BASE_DIR / "train" / "images"
train_labels_dir = BASE_DIR / "train" / "labels"

(
    train_images,
    train_res,
    train_errors
) = analizar_imagenes(
    train_images_dir
)

(
    train_masks,
    train_mask_res,
    train_cobertura,
    train_valores,
    train_mask_errors
) = analizar_mascaras(
    train_labels_dir
)


# ==========================================================
# VALIDATION
# ==========================================================

validation_images_dir = (
    BASE_DIR
    / "validation"
    / "images"
)

validation_labels_dir = (
    BASE_DIR
    / "validation"
    / "labels"
)

(
    val_images,
    val_res,
    val_errors
) = analizar_imagenes(
    validation_images_dir
)

(
    val_masks,
    val_mask_res,
    val_cobertura,
    val_valores,
    val_mask_errors
) = analizar_mascaras(
    validation_labels_dir
)


# ==========================================================
# TEST
# ==========================================================

test_images_dir = BASE_DIR / "test" / "images"

(
    test_images,
    test_res,
    test_errors
) = analizar_imagenes(
    test_images_dir
)


# ==========================================================
# RESULTADOS DE RESOLUCIÓN
# ==========================================================

mostrar_resoluciones(
    "TRAIN - IMÁGENES",
    train_res
)

mostrar_resoluciones(
    "TRAIN - MÁSCARAS",
    train_mask_res
)

mostrar_resoluciones(
    "VALIDATION - IMÁGENES",
    val_res
)

mostrar_resoluciones(
    "VALIDATION - MÁSCARAS",
    val_mask_res
)

mostrar_resoluciones(
    "TEST - IMÁGENES",
    test_res
)


# ==========================================================
# RESULTADOS DE LAS MÁSCARAS
# ==========================================================

print("\n" + "=" * 65)
print("ANÁLISIS DEL TAMAÑO RELATIVO DE LAS ÚLCERAS")
print("=" * 65)

train_array = np.array(
    train_cobertura
)

val_array = np.array(
    val_cobertura
)

print("\nTRAIN")

print(
    f"Cobertura mínima: "
    f"{train_array.min():.2f} %"
)

print(
    f"Cobertura máxima: "
    f"{train_array.max():.2f} %"
)

print(
    f"Cobertura promedio: "
    f"{train_array.mean():.2f} %"
)

print(
    f"Mediana: "
    f"{np.median(train_array):.2f} %"
)

print(
    f"Valores de máscara encontrados: "
    f"{sorted(train_valores)}"
)


print("\nVALIDATION")

print(
    f"Cobertura mínima: "
    f"{val_array.min():.2f} %"
)

print(
    f"Cobertura máxima: "
    f"{val_array.max():.2f} %"
)

print(
    f"Cobertura promedio: "
    f"{val_array.mean():.2f} %"
)

print(
    f"Mediana: "
    f"{np.median(val_array):.2f} %"
)

print(
    f"Valores de máscara encontrados: "
    f"{sorted(val_valores)}"
)


# ==========================================================
# REVISAR ERRORES DE LECTURA
# ==========================================================

print("\n" + "=" * 65)
print("ERRORES DE LECTURA")
print("=" * 65)

todos_errores = (
    train_errors
    + train_mask_errors
    + val_errors
    + val_mask_errors
    + test_errors
)

if len(todos_errores) == 0:
    print("✅ No se encontraron archivos dañados o ilegibles.")
else:

    print(
        f"❌ Archivos con problemas: "
        f"{len(todos_errores)}"
    )

    for archivo in todos_errores:
        print(archivo)


# ==========================================================
# HISTOGRAMA DE COBERTURA
# ==========================================================

plt.figure(figsize=(9, 5))

plt.hist(
    train_cobertura,
    bins=30,
    alpha=0.7,
    label="Train"
)

plt.hist(
    val_cobertura,
    bins=30,
    alpha=0.7,
    label="Validation"
)

plt.xlabel(
    "Porcentaje de la imagen ocupado por la úlcera (%)"
)

plt.ylabel(
    "Número de imágenes"
)

plt.title(
    "Distribución del tamaño relativo de las úlceras - FUSeg"
)

plt.legend()

plt.tight_layout()


# ==========================================================
# GUARDAR GRÁFICA
# ==========================================================

ruta_grafica = (
    SALIDA
    / "distribucion_cobertura_ulceras.png"
)

plt.savefig(
    ruta_grafica,
    dpi=300
)

print("\n" + "=" * 65)

print(
    "✅ Gráfica guardada en:"
)

print(
    ruta_grafica
)


# ==========================================================
# MOSTRAR GRÁFICA
# ==========================================================

plt.show()