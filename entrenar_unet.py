from pathlib import Path
import json

import tensorflow as tf
import matplotlib.pyplot as plt

# ==========================================================
# CONFIGURACIÓN GENERAL (Importada desde config.py)
# ==========================================================
from config import DATA_DIR as BASE_DIR, MODELOS_DIR, RESULTADOS_DIR, asegurar_carpetas

asegurar_carpetas()

IMG_HEIGHT = 256
IMG_WIDTH = 256

BATCH_SIZE = 4
EPOCHS = 20
SEED = 42

AUTOTUNE = tf.data.AUTOTUNE

tf.random.set_seed(SEED)


# ==========================================================
# OBTENER PARES IMAGEN - MÁSCARA
# ==========================================================

def obtener_pares(conjunto):

    carpeta_imagenes = BASE_DIR / conjunto / "images"
    carpeta_mascaras = BASE_DIR / conjunto / "labels"

    imagenes = {
        archivo.stem: archivo
        for archivo in carpeta_imagenes.glob("*.png")
    }

    mascaras = {
        archivo.stem: archivo
        for archivo in carpeta_mascaras.glob("*.png")
    }

    nombres = sorted(
        set(imagenes.keys())
        & set(mascaras.keys())
    )

    rutas_imagenes = [
        str(imagenes[nombre])
        for nombre in nombres
    ]

    rutas_mascaras = [
        str(mascaras[nombre])
        for nombre in nombres
    ]

    return rutas_imagenes, rutas_mascaras


# ==========================================================
# CARGAR Y PREPROCESAR
# ==========================================================

def cargar_datos(ruta_imagen, ruta_mascara):

    # ------------------------------------------------------
    # IMAGEN
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

    # Redimensionar de 512x512 a 256x256
    imagen = tf.image.resize(
        imagen,
        [IMG_HEIGHT, IMG_WIDTH],
        method="bilinear"
    )

    # Normalizar a 0 - 1
    imagen = imagen / 255.0


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

    # Convertimos cualquier valor > 0 en úlcera
    mascara = tf.cast(
        mascara > 0,
        tf.float32
    )

    # IMPORTANTE:
    # nearest evita crear nuevos valores en la máscara
    mascara = tf.image.resize(
        mascara,
        [IMG_HEIGHT, IMG_WIDTH],
        method="nearest"
    )

    return imagen, mascara


# ==========================================================
# CREAR DATASETS
# ==========================================================

train_images, train_masks = obtener_pares(
    "train"
)

val_images, val_masks = obtener_pares(
    "validation"
)

print("\n" + "=" * 70)
print("DATASET")
print("=" * 70)

print(
    f"Entrenamiento: {len(train_images)} pares"
)

print(
    f"Validación: {len(val_images)} pares"
)


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
    len(train_images),
    seed=SEED,
    reshuffle_each_iteration=True
)

train_dataset = train_dataset.batch(
    BATCH_SIZE
)

train_dataset = train_dataset.prefetch(
    AUTOTUNE
)


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
# MÉTRICA DICE
# ==========================================================

def dice_coefficient(y_true, y_pred):

    smooth = 1e-6

    y_true = tf.cast(
        y_true,
        tf.float32
    )

    y_pred = tf.cast(
        y_pred,
        tf.float32
    )

    y_true = tf.reshape(
        y_true,
        [-1]
    )

    y_pred = tf.reshape(
        y_pred,
        [-1]
    )

    intersection = tf.reduce_sum(
        y_true * y_pred
    )

    return (
        (2.0 * intersection + smooth)
        /
        (
            tf.reduce_sum(y_true)
            + tf.reduce_sum(y_pred)
            + smooth
        )
    )


# ==========================================================
# DICE LOSS
# ==========================================================

def dice_loss(y_true, y_pred):

    return 1.0 - dice_coefficient(
        y_true,
        y_pred
    )


# ==========================================================
# BCE + DICE LOSS
# ==========================================================

def bce_dice_loss(y_true, y_pred):

    bce = tf.keras.losses.binary_crossentropy(
        y_true,
        y_pred
    )

    bce = tf.reduce_mean(
        bce
    )

    return bce + dice_loss(
        y_true,
        y_pred
    )


# ==========================================================
# MÉTRICA IoU
# ==========================================================

def iou_metric(y_true, y_pred):

    smooth = 1e-6

    y_true = tf.cast(
        y_true > 0.5,
        tf.float32
    )

    y_pred = tf.cast(
        y_pred > 0.5,
        tf.float32
    )

    y_true = tf.reshape(
        y_true,
        [-1]
    )

    y_pred = tf.reshape(
        y_pred,
        [-1]
    )

    intersection = tf.reduce_sum(
        y_true * y_pred
    )

    union = (
        tf.reduce_sum(y_true)
        + tf.reduce_sum(y_pred)
        - intersection
    )

    return (
        intersection + smooth
    ) / (
        union + smooth
    )


# ==========================================================
# BLOQUE CONVOLUCIONAL
# ==========================================================

def bloque_conv(
    entrada,
    filtros
):

    x = tf.keras.layers.Conv2D(
        filtros,
        3,
        padding="same",
        activation="relu"
    )(entrada)

    x = tf.keras.layers.BatchNormalization()(x)

    x = tf.keras.layers.Conv2D(
        filtros,
        3,
        padding="same",
        activation="relu"
    )(x)

    x = tf.keras.layers.BatchNormalization()(x)

    return x


# ==========================================================
# CONSTRUIR U-NET
# ==========================================================

def construir_unet():

    inputs = tf.keras.layers.Input(
        shape=(
            IMG_HEIGHT,
            IMG_WIDTH,
            3
        )
    )


    # ------------------------------------------------------
    # ENCODER
    # ------------------------------------------------------

    c1 = bloque_conv(
        inputs,
        16
    )

    p1 = tf.keras.layers.MaxPooling2D(
        (2, 2)
    )(c1)


    c2 = bloque_conv(
        p1,
        32
    )

    p2 = tf.keras.layers.MaxPooling2D(
        (2, 2)
    )(c2)


    c3 = bloque_conv(
        p2,
        64
    )

    p3 = tf.keras.layers.MaxPooling2D(
        (2, 2)
    )(c3)


    c4 = bloque_conv(
        p3,
        128
    )

    p4 = tf.keras.layers.MaxPooling2D(
        (2, 2)
    )(c4)


    # ------------------------------------------------------
    # BOTTLENECK
    # ------------------------------------------------------

    c5 = bloque_conv(
        p4,
        256
    )


    # ------------------------------------------------------
    # DECODER
    # ------------------------------------------------------

    u6 = tf.keras.layers.Conv2DTranspose(
        128,
        2,
        strides=2,
        padding="same"
    )(c5)

    u6 = tf.keras.layers.Concatenate()(
        [u6, c4]
    )

    c6 = bloque_conv(
        u6,
        128
    )


    u7 = tf.keras.layers.Conv2DTranspose(
        64,
        2,
        strides=2,
        padding="same"
    )(c6)

    u7 = tf.keras.layers.Concatenate()(
        [u7, c3]
    )

    c7 = bloque_conv(
        u7,
        64
    )


    u8 = tf.keras.layers.Conv2DTranspose(
        32,
        2,
        strides=2,
        padding="same"
    )(c7)

    u8 = tf.keras.layers.Concatenate()(
        [u8, c2]
    )

    c8 = bloque_conv(
        u8,
        32
    )


    u9 = tf.keras.layers.Conv2DTranspose(
        16,
        2,
        strides=2,
        padding="same"
    )(c8)

    u9 = tf.keras.layers.Concatenate()(
        [u9, c1]
    )

    c9 = bloque_conv(
        u9,
        16
    )


    # ------------------------------------------------------
    # SALIDA
    # ------------------------------------------------------

    outputs = tf.keras.layers.Conv2D(
        1,
        1,
        activation="sigmoid"
    )(c9)


    modelo = tf.keras.Model(
        inputs=inputs,
        outputs=outputs,
        name="UNet_FUSeg"
    )

    return modelo


# ==========================================================
# CREAR MODELO
# ==========================================================

modelo = construir_unet()


# ==========================================================
# COMPILAR
# ==========================================================

modelo.compile(

    optimizer=tf.keras.optimizers.Adam(
        learning_rate=1e-4
    ),

    loss=bce_dice_loss,

    metrics=[
        dice_coefficient,
        iou_metric,
        tf.keras.metrics.Precision(
            name="precision"
        ),
        tf.keras.metrics.Recall(
            name="recall"
        )
    ]
)


# ==========================================================
# MOSTRAR RESUMEN
# ==========================================================

print("\n" + "=" * 70)
print("MODELO U-NET")
print("=" * 70)

modelo.summary()


# ==========================================================
# CALLBACKS
# ==========================================================

ruta_modelo = (
    MODELOS_DIR
    / "unet_fuseg_baseline.keras"
)


checkpoint = tf.keras.callbacks.ModelCheckpoint(

    filepath=str(ruta_modelo),

    monitor="val_dice_coefficient",

    mode="max",

    save_best_only=True,

    verbose=1
)


early_stopping = tf.keras.callbacks.EarlyStopping(

    monitor="val_dice_coefficient",

    mode="max",

    patience=5,

    restore_best_weights=True,

    verbose=1
)


reduce_lr = tf.keras.callbacks.ReduceLROnPlateau(

    monitor="val_loss",

    factor=0.5,

    patience=3,

    min_lr=1e-7,

    verbose=1
)


# ==========================================================
# ENTRENAMIENTO
# ==========================================================

print("\n" + "=" * 70)
print("INICIANDO ENTRENAMIENTO")
print("=" * 70)

print(
    f"Resolución usada: "
    f"{IMG_WIDTH} x {IMG_HEIGHT}"
)

print(
    f"Batch size: {BATCH_SIZE}"
)

print(
    f"Máximo de épocas: {EPOCHS}"
)

print(
    "\nEste es el BASELINE."
)

print(
    "No se está utilizando Data Augmentation todavía."
)


history = modelo.fit(

    train_dataset,

    validation_data=validation_dataset,

    epochs=EPOCHS,

    callbacks=[
        checkpoint,
        early_stopping,
        reduce_lr
    ]
)


# ==========================================================
# GUARDAR HISTORIAL
# ==========================================================

historial = {}

for clave, valores in history.history.items():

    historial[clave] = [
        float(valor)
        for valor in valores
    ]


ruta_historial = (
    RESULTADOS_DIR
    / "historial_unet_baseline.json"
)

with open(
    ruta_historial,
    "w",
    encoding="utf-8"
) as archivo:

    json.dump(
        historial,
        archivo,
        indent=4
    )


# ==========================================================
# GRÁFICA LOSS
# ==========================================================

plt.figure(
    figsize=(8, 5)
)

plt.plot(
    history.history["loss"],
    label="Train"
)

plt.plot(
    history.history["val_loss"],
    label="Validation"
)

plt.xlabel(
    "Época"
)

plt.ylabel(
    "Loss"
)

plt.title(
    "U-Net FUSeg - Loss"
)

plt.legend()

plt.tight_layout()

ruta_loss = (
    RESULTADOS_DIR
    / "unet_baseline_loss.png"
)

plt.savefig(
    ruta_loss,
    dpi=300
)

plt.close()


# ==========================================================
# GRÁFICA DICE
# ==========================================================

plt.figure(
    figsize=(8, 5)
)

plt.plot(
    history.history[
        "dice_coefficient"
    ],
    label="Train"
)

plt.plot(
    history.history[
        "val_dice_coefficient"
    ],
    label="Validation"
)

plt.xlabel(
    "Época"
)

plt.ylabel(
    "Dice"
)

plt.title(
    "U-Net FUSeg - Dice"
)

plt.legend()

plt.tight_layout()

ruta_dice = (
    RESULTADOS_DIR
    / "unet_baseline_dice.png"
)

plt.savefig(
    ruta_dice,
    dpi=300
)

plt.close()


# ==========================================================
# GRÁFICA IoU
# ==========================================================

plt.figure(
    figsize=(8, 5)
)

plt.plot(
    history.history[
        "iou_metric"
    ],
    label="Train"
)

plt.plot(
    history.history[
        "val_iou_metric"
    ],
    label="Validation"
)

plt.xlabel(
    "Época"
)

plt.ylabel(
    "IoU"
)

plt.title(
    "U-Net FUSeg - IoU"
)

plt.legend()

plt.tight_layout()

ruta_iou = (
    RESULTADOS_DIR
    / "unet_baseline_iou.png"
)

plt.savefig(
    ruta_iou,
    dpi=300
)

plt.close()


# ==========================================================
# EVALUACIÓN FINAL EN VALIDATION
# ==========================================================

print("\n" + "=" * 70)
print("EVALUACIÓN FINAL")
print("=" * 70)

resultados = modelo.evaluate(
    validation_dataset,
    verbose=1
)

for nombre, valor in zip(
    modelo.metrics_names,
    resultados
):

    print(
        f"{nombre}: {valor:.4f}"
    )


# ==========================================================
# RESULTADOS GUARDADOS
# ==========================================================

print("\n" + "=" * 70)
print("ENTRENAMIENTO FINALIZADO")
print("=" * 70)

print(
    "\nMejor modelo guardado en:"
)

print(
    ruta_modelo
)

print(
    "\nHistorial guardado en:"
)

print(
    ruta_historial
)

print(
    "\nGráficas guardadas en:"
)

print(
    ruta_loss
)

print(
    ruta_dice
)

print(
    ruta_iou
)