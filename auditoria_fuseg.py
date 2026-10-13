from pathlib import Path
import cv2
import numpy as np
import matplotlib.pyplot as plt

# ==========================================================
# RUTA DEL DATASET FUSEG
# ==========================================================

BASE_DIR = Path(
    r"C:\Users\alejo\pie_diabetico_ia\wound-segmentation\data\Foot Ulcer Segmentation Challenge"
)

# Extensiones de imagen que vamos a reconocer
EXTENSIONES = {".jpg", ".jpeg", ".png", ".bmp"}


# ==========================================================
# FUNCIÓN PARA OBTENER ARCHIVOS
# ==========================================================

def obtener_imagenes(carpeta):
    return sorted([
        archivo for archivo in carpeta.iterdir()
        if archivo.is_file() and archivo.suffix.lower() in EXTENSIONES
    ])


# ==========================================================
# AUDITORÍA DE TRAIN Y VALIDATION
# ==========================================================

def auditar_conjunto(nombre):
    carpeta_images = BASE_DIR / nombre / "images"
    carpeta_labels = BASE_DIR / nombre / "labels"

    imagenes = obtener_imagenes(carpeta_images)
    mascaras = obtener_imagenes(carpeta_labels)

    print("\n" + "=" * 60)
    print(f"CONJUNTO: {nombre.upper()}")
    print("=" * 60)

    print(f"Imágenes encontradas: {len(imagenes)}")
    print(f"Máscaras encontradas: {len(mascaras)}")

    # Comparar por nombre sin extensión
    nombres_imagenes = {archivo.stem: archivo for archivo in imagenes}
    nombres_mascaras = {archivo.stem: archivo for archivo in mascaras}

    faltan_mascaras = set(nombres_imagenes) - set(nombres_mascaras)
    faltan_imagenes = set(nombres_mascaras) - set(nombres_imagenes)

    coincidencias = set(nombres_imagenes) & set(nombres_mascaras)

    print(f"Pares imagen-máscara encontrados: {len(coincidencias)}")

    if not faltan_mascaras:
        print("✅ Todas las imágenes tienen máscara.")
    else:
        print(f"❌ Imágenes sin máscara: {len(faltan_mascaras)}")
        print(sorted(faltan_mascaras)[:10])

    if not faltan_imagenes:
        print("✅ Todas las máscaras tienen imagen.")
    else:
        print(f"❌ Máscaras sin imagen: {len(faltan_imagenes)}")
        print(sorted(faltan_imagenes)[:10])

    return imagenes, mascaras, nombres_imagenes, nombres_mascaras, coincidencias


# ==========================================================
# EJECUTAR AUDITORÍA
# ==========================================================

train = auditar_conjunto("train")
validation = auditar_conjunto("validation")


# ==========================================================
# AUDITORÍA DEL CONJUNTO TEST
# ==========================================================

test_images = obtener_imagenes(BASE_DIR / "test" / "images")

print("\n" + "=" * 60)
print("CONJUNTO: TEST")
print("=" * 60)

print(f"Imágenes encontradas: {len(test_images)}")
print("ℹ️ El conjunto test no contiene máscaras públicas.")


# ==========================================================
# REVISAR UN EJEMPLO REAL DE TRAIN
# ==========================================================

_, _, train_images_dict, train_masks_dict, coincidencias = train

if coincidencias:

    nombre = sorted(coincidencias)[0]

    ruta_imagen = train_images_dict[nombre]
    ruta_mascara = train_masks_dict[nombre]

    imagen = cv2.imread(str(ruta_imagen))
    mascara = cv2.imread(str(ruta_mascara), cv2.IMREAD_GRAYSCALE)

    if imagen is None:
        print("\n❌ No se pudo leer la imagen.")

    elif mascara is None:
        print("\n❌ No se pudo leer la máscara.")

    else:
        print("\n" + "=" * 60)
        print("EJEMPLO DE IMAGEN Y MÁSCARA")
        print("=" * 60)

        print(f"Archivo imagen: {ruta_imagen.name}")
        print(f"Archivo máscara: {ruta_mascara.name}")

        print(f"Tamaño imagen: {imagen.shape}")
        print(f"Tamaño máscara: {mascara.shape}")

        print(
            "Valores presentes en la máscara:",
            np.unique(mascara)
        )

        # Convertir BGR a RGB para mostrar correctamente
        imagen_rgb = cv2.cvtColor(imagen, cv2.COLOR_BGR2RGB)

        plt.figure(figsize=(10, 5))

        plt.subplot(1, 2, 1)
        plt.imshow(imagen_rgb)
        plt.title("Imagen original")
        plt.axis("off")

        plt.subplot(1, 2, 2)
        plt.imshow(mascara, cmap="gray")
        plt.title("Máscara de la úlcera")
        plt.axis("off")

        plt.tight_layout()
        plt.show()