from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt
import tensorflow as tf


# ==========================================================
# CONFIGURACIÓN
# ==========================================================

BASE_DIR = Path(
    r"C:\Users\alejo\pie_diabetico_ia\wound-segmentation\data\Foot Ulcer Segmentation Challenge"
)

IMG_HEIGHT = 512
IMG_WIDTH = 512

# Empezamos conservador para no consumir demasiada memoria
BATCH_SIZE = 4

SEED = 42

AUTOTUNE = tf.data.AUTOTUNE


# ==========================================================
# CREAR PARES IMAGEN - MÁSCARA
# ==========================================================

def obtener_pares(conjunto):

    carpeta_imagenes = BASE_DIR / conjunto / "images"
    carpeta_mascaras = BASE_DIR / conjunto / "labels"

    imagenes = sorted(carpeta_imagenes.glob("*.png"))
    mascaras = sorted(carpeta_mascaras.glob("*.png"))

    imagenes_dict = {
        archivo.stem: archivo
        for archivo in imagenes
    }

    mascaras_dict = {
        archivo.stem: archivo
        for archivo in mascaras
    }

    nombres_comunes = sorted(
        set(imagenes_dict.keys())
        & set(mascaras_dict.keys())
    )

    rutas_imagenes = [
        str(imagenes_dict[nombre])
        for nombre in nombres_comunes
    ]

    rutas_mascaras = [
        str(mascaras_dict[nombre])
        for nombre in nombres_comunes
    ]

    return rutas_imagenes, rutas_mascaras


# ==========================================================
# CARGAR Y PREPROCESAR
# ==========================================================

def cargar_datos(ruta_imagen, ruta_mascara):

    # ------------------------------------------------------
    # IMAGEN RGB
    # ------------------------------------------------------

    imagen = tf.io.read_file(
        ruta_imagen
    )

    imagen = tf.image.decode_png(
        imagen,
        channels=3
    )

    imagen = tf.cast(
        imagen,
        tf.float32
    )

    # Normalización:
    # 0 - 255  --->  0 - 1

    imagen = imagen / 255.0

    imagen.set_shape(
        [IMG_HEIGHT, IMG_WIDTH, 3]
    )


    # ------------------------------------------------------
    # MÁSCARA
    # ------------------------------------------------------

    mascara = tf.io.read_file(
        ruta_mascara
    )

    mascara = tf.image.decode_png(
        mascara,
        channels=1
    )

    # Convierte:
    #
    # 0   -> 0
    # 32  -> 1
    # 255 -> 1

    mascara = tf.cast(
        mascara > 0,
        tf.float32
    )

    mascara.set_shape(
        [IMG_HEIGHT, IMG_WIDTH, 1]
    )

    return imagen, mascara


# ==========================================================
# OBTENER RUTAS
# ==========================================================

train_images, train_masks = obtener_pares(
    "train"
)

val_images, val_masks = obtener_pares(
    "validation"
)


print("\n" + "=" * 65)
print("DATOS ENCONTRADOS")
print("=" * 65)

print(
    f"Train: {len(train_images)} "
    f"imágenes + {len(train_masks)} máscaras"
)

print(
    f"Validation: {len(val_images)} "
    f"imágenes + {len(val_masks)} máscaras"
)


# ==========================================================
# DATASET DE ENTRENAMIENTO
# ==========================================================

train_dataset = tf.data.Dataset.from_tensor_slices(
    (
        train_images,
        train_masks
    )
)

train_dataset = train_dataset.map(
    cargar_datos,
    num_parallel_calls=AUTOTUNE
)

train_dataset = train_dataset.shuffle(
    buffer_size=len(train_images),
    seed=SEED,
    reshuffle_each_iteration=True
)

train_dataset = train_dataset.batch(
    BATCH_SIZE
)

train_dataset = train_dataset.prefetch(
    AUTOTUNE
)


# ==========================================================
# DATASET DE VALIDACIÓN
# ==========================================================

validation_dataset = tf.data.Dataset.from_tensor_slices(
    (
        val_images,
        val_masks
    )
)

validation_dataset = validation_dataset.map(
    cargar_datos,
    num_parallel_calls=AUTOTUNE
)

validation_dataset = validation_dataset.batch(
    BATCH_SIZE
)

validation_dataset = validation_dataset.prefetch(
    AUTOTUNE
)


# ==========================================================
# COMPROBAR UN BATCH
# ==========================================================

for imagenes_batch, mascaras_batch in train_dataset.take(1):

    print("\n" + "=" * 65)
    print("VERIFICACIÓN DEL PIPELINE")
    print("=" * 65)

    print(
        "Forma batch imágenes:",
        imagenes_batch.shape
    )

    print(
        "Forma batch máscaras:",
        mascaras_batch.shape
    )

    print(
        "Valor mínimo imagen:",
        float(
            tf.reduce_min(imagenes_batch)
        )
    )

    print(
        "Valor máximo imagen:",
        float(
            tf.reduce_max(imagenes_batch)
        )
    )

    print(
        "Valores máscara:",
        np.unique(
            mascaras_batch.numpy()
        )
    )


    # ======================================================
    # MOSTRAR EJEMPLO
    # ======================================================

    imagen = imagenes_batch[0].numpy()

    mascara = (
        mascaras_batch[0]
        .numpy()
        .squeeze()
    )

    plt.figure(
        figsize=(15, 5)
    )


    # ------------------------------------------------------
    # Imagen original
    # ------------------------------------------------------

    plt.subplot(
        1,
        3,
        1
    )

    plt.imshow(
        imagen
    )

    plt.title(
        "Imagen normalizada"
    )

    plt.axis(
        "off"
    )


    # ------------------------------------------------------
    # Máscara binaria
    # ------------------------------------------------------

    plt.subplot(
        1,
        3,
        2
    )

    plt.imshow(
        mascara,
        cmap="gray"
    )

    plt.title(
        "Máscara binaria 0 / 1"
    )

    plt.axis(
        "off"
    )


    # ------------------------------------------------------
    # Superposición
    # ------------------------------------------------------

    plt.subplot(
        1,
        3,
        3
    )

    plt.imshow(
        imagen
    )

    plt.imshow(
        mascara,
        alpha=0.40,
        cmap="Reds"
    )

    plt.title(
        "Imagen + máscara"
    )

    plt.axis(
        "off"
    )


    plt.tight_layout()

    plt.show()


# ==========================================================
# RESUMEN
# ==========================================================

print("\n" + "=" * 65)
print("PIPELINE PREPARADO CORRECTAMENTE")
print("=" * 65)

print(
    "Resolución:",
    IMG_WIDTH,
    "x",
    IMG_HEIGHT
)

print(
    "Batch size:",
    BATCH_SIZE
)

print(
    "Normalización imágenes: 0 - 1"
)

print(
    "Máscaras binarias: 0 - 1"
)

print(
    "\n✅ Datos listos para ser utilizados por TensorFlow."
)