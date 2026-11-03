import argparse
import json

import tensorflow as tf
import matplotlib.pyplot as plt

from config import DATA_DIR as BASE_DIR, MODELOS_DIR, RESULTADOS_DIR, asegurar_carpetas

# ==========================================================
# ARGUMENTOS (A3: permiten repetir el entrenamiento sin pisar el baseline)
# ==========================================================
parser = argparse.ArgumentParser()
parser.add_argument("--seed", type=int, default=42)
parser.add_argument("--nombre", default="baseline")
args = parser.parse_args()

asegurar_carpetas()

IMG_HEIGHT = 256
IMG_WIDTH = 256
BATCH_SIZE = 4
EPOCHS = 20
SEED = args.seed

AUTOTUNE = tf.data.AUTOTUNE

# Fija semilla de Python, NumPy y TensorFlow/Keras (incluye pesos iniciales)
tf.keras.utils.set_random_seed(SEED)


# ==========================================================
# OBTENER PARES IMAGEN - MÁSCARA
# ==========================================================

def obtener_pares(conjunto):
    carpeta_imagenes = BASE_DIR / conjunto / "images"
    carpeta_mascaras = BASE_DIR / conjunto / "labels"

    imagenes = {a.stem: a for a in carpeta_imagenes.glob("*.png")}
    mascaras = {a.stem: a for a in carpeta_mascaras.glob("*.png")}

    nombres = sorted(set(imagenes) & set(mascaras))

    return (
        [str(imagenes[n]) for n in nombres],
        [str(mascaras[n]) for n in nombres],
    )


# ==========================================================
# CARGAR Y PREPROCESAR
# ==========================================================

def cargar_datos(ruta_imagen, ruta_mascara):
    imagen = tf.io.read_file(ruta_imagen)
    imagen = tf.image.decode_png(imagen, channels=3)
    imagen = tf.cast(imagen, tf.float32)
    imagen = tf.image.resize(imagen, [IMG_HEIGHT, IMG_WIDTH], method="bilinear")
    imagen = imagen / 255.0

    mascara = tf.io.read_file(ruta_mascara)
    mascara = tf.image.decode_png(mascara, channels=1)
    # Criterio único del proyecto: cualquier valor > 0 es úlcera
    mascara = tf.cast(mascara > 0, tf.float32)
    # nearest evita crear valores nuevos en la máscara
    mascara = tf.image.resize(mascara, [IMG_HEIGHT, IMG_WIDTH], method="nearest")

    return imagen, mascara


# ==========================================================
# CREAR DATASETS
# ==========================================================

train_images, train_masks = obtener_pares("train")
val_images, val_masks = obtener_pares("validation")

print("\n" + "=" * 70)
print("DATASET")
print("=" * 70)
print(f"Entrenamiento: {len(train_images)} pares")
print(f"Validación: {len(val_images)} pares")

train_dataset = tf.data.Dataset.from_tensor_slices((train_images, train_masks))
train_dataset = train_dataset.map(cargar_datos, num_parallel_calls=AUTOTUNE)
train_dataset = train_dataset.shuffle(
    len(train_images), seed=SEED, reshuffle_each_iteration=True
)
train_dataset = train_dataset.batch(BATCH_SIZE).prefetch(AUTOTUNE)

validation_dataset = tf.data.Dataset.from_tensor_slices((val_images, val_masks))
validation_dataset = validation_dataset.map(cargar_datos, num_parallel_calls=AUTOTUNE)
validation_dataset = validation_dataset.batch(BATCH_SIZE).prefetch(AUTOTUNE)


# ==========================================================
# MÉTRICAS Y PÉRDIDAS
# ==========================================================

def dice_coefficient(y_true, y_pred):
    smooth = 1e-6
    y_true = tf.reshape(tf.cast(y_true, tf.float32), [-1])
    y_pred = tf.reshape(tf.cast(y_pred, tf.float32), [-1])
    intersection = tf.reduce_sum(y_true * y_pred)
    return (2.0 * intersection + smooth) / (
        tf.reduce_sum(y_true) + tf.reduce_sum(y_pred) + smooth
    )


def dice_loss(y_true, y_pred):
    return 1.0 - dice_coefficient(y_true, y_pred)


def bce_dice_loss(y_true, y_pred):
    bce = tf.reduce_mean(tf.keras.losses.binary_crossentropy(y_true, y_pred))
    return bce + dice_loss(y_true, y_pred)


def iou_metric(y_true, y_pred):
    smooth = 1e-6
    y_true = tf.reshape(tf.cast(y_true > 0.5, tf.float32), [-1])
    y_pred = tf.reshape(tf.cast(y_pred > 0.5, tf.float32), [-1])
    intersection = tf.reduce_sum(y_true * y_pred)
    union = tf.reduce_sum(y_true) + tf.reduce_sum(y_pred) - intersection
    return (intersection + smooth) / (union + smooth)


# ==========================================================
# U-NET
# ==========================================================

def bloque_conv(entrada, filtros):
    x = tf.keras.layers.Conv2D(filtros, 3, padding="same", activation="relu")(entrada)
    x = tf.keras.layers.BatchNormalization()(x)
    x = tf.keras.layers.Conv2D(filtros, 3, padding="same", activation="relu")(x)
    x = tf.keras.layers.BatchNormalization()(x)
    return x


def construir_unet():
    inputs = tf.keras.layers.Input(shape=(IMG_HEIGHT, IMG_WIDTH, 3))

    # Encoder
    c1 = bloque_conv(inputs, 16)
    p1 = tf.keras.layers.MaxPooling2D((2, 2))(c1)
    c2 = bloque_conv(p1, 32)
    p2 = tf.keras.layers.MaxPooling2D((2, 2))(c2)
    c3 = bloque_conv(p2, 64)
    p3 = tf.keras.layers.MaxPooling2D((2, 2))(c3)
    c4 = bloque_conv(p3, 128)
    p4 = tf.keras.layers.MaxPooling2D((2, 2))(c4)

    # Bottleneck
    c5 = bloque_conv(p4, 256)

    # Decoder
    u6 = tf.keras.layers.Conv2DTranspose(128, 2, strides=2, padding="same")(c5)
    c6 = bloque_conv(tf.keras.layers.Concatenate()([u6, c4]), 128)

    u7 = tf.keras.layers.Conv2DTranspose(64, 2, strides=2, padding="same")(c6)
    c7 = bloque_conv(tf.keras.layers.Concatenate()([u7, c3]), 64)

    u8 = tf.keras.layers.Conv2DTranspose(32, 2, strides=2, padding="same")(c7)
    c8 = bloque_conv(tf.keras.layers.Concatenate()([u8, c2]), 32)

    u9 = tf.keras.layers.Conv2DTranspose(16, 2, strides=2, padding="same")(c8)
    c9 = bloque_conv(tf.keras.layers.Concatenate()([u9, c1]), 16)

    outputs = tf.keras.layers.Conv2D(1, 1, activation="sigmoid")(c9)

    return tf.keras.Model(inputs=inputs, outputs=outputs, name="UNet_FUSeg")


modelo = construir_unet()

modelo.compile(
    optimizer=tf.keras.optimizers.Adam(learning_rate=1e-4),
    loss=bce_dice_loss,
    metrics=[
        dice_coefficient,
        iou_metric,
        tf.keras.metrics.Precision(name="precision"),
        tf.keras.metrics.Recall(name="recall"),
    ],
)

print("\n" + "=" * 70)
print("MODELO U-NET")
print("=" * 70)
modelo.summary()


# ==========================================================
# CALLBACKS
# ==========================================================

ruta_modelo = MODELOS_DIR / f"unet_fuseg_{args.nombre}.keras"

checkpoint = tf.keras.callbacks.ModelCheckpoint(
    filepath=str(ruta_modelo),
    monitor="val_dice_coefficient",
    mode="max",
    save_best_only=True,
    verbose=1,
)

early_stopping = tf.keras.callbacks.EarlyStopping(
    monitor="val_dice_coefficient",
    mode="max",
    patience=5,
    restore_best_weights=True,
    verbose=1,
)

reduce_lr = tf.keras.callbacks.ReduceLROnPlateau(
    monitor="val_loss",
    factor=0.5,
    patience=3,
    min_lr=1e-7,
    verbose=1,
)


# ==========================================================
# ENTRENAMIENTO
# ==========================================================

print("\n" + "=" * 70)
print("INICIANDO ENTRENAMIENTO")
print("=" * 70)
print(f"Corrida: {args.nombre} | semilla: {SEED}")
print(f"Resolución usada: {IMG_WIDTH} x {IMG_HEIGHT}")
print(f"Batch size: {BATCH_SIZE}")
print(f"Máximo de épocas: {EPOCHS}")
print("\nEste es el BASELINE. No se usa Data Augmentation todavía.")

history = modelo.fit(
    train_dataset,
    validation_data=validation_dataset,
    epochs=EPOCHS,
    callbacks=[checkpoint, early_stopping, reduce_lr],
)


# ==========================================================
# GUARDAR HISTORIAL
# ==========================================================

historial = {
    clave: [float(v) for v in valores]
    for clave, valores in history.history.items()
}

ruta_historial = RESULTADOS_DIR / f"historial_unet_{args.nombre}.json"
with open(ruta_historial, "w", encoding="utf-8") as archivo:
    json.dump(historial, archivo, indent=4)


# ==========================================================
# GRÁFICAS
# ==========================================================

def guardar_grafica(clave, etiqueta, titulo):
    plt.figure(figsize=(8, 5))
    plt.plot(history.history[clave], label="Train")
    plt.plot(history.history[f"val_{clave}"], label="Validation")
    plt.xlabel("Época")
    plt.ylabel(etiqueta)
    plt.title(f"U-Net FUSeg ({args.nombre}) - {titulo}")
    plt.legend()
    plt.tight_layout()
    ruta = RESULTADOS_DIR / f"unet_{args.nombre}_{etiqueta.lower()}.png"
    plt.savefig(ruta, dpi=300)
    plt.close()
    return ruta


ruta_loss = guardar_grafica("loss", "Loss", "Loss")
ruta_dice = guardar_grafica("dice_coefficient", "Dice", "Dice")
ruta_iou = guardar_grafica("iou_metric", "IoU", "IoU")


# ==========================================================
# EVALUACIÓN FINAL EN VALIDATION (métricas de Keras, no comparables entre sí)
# Las métricas oficiales se recalculan con evaluar_modelo.py
# ==========================================================

print("\n" + "=" * 70)
print("EVALUACIÓN FINAL (métricas de Keras)")
print("=" * 70)

resultados = modelo.evaluate(validation_dataset, verbose=1)
for nombre, valor in zip(modelo.metrics_names, resultados):
    print(f"{nombre}: {valor:.4f}")

print("\n" + "=" * 70)
print("ENTRENAMIENTO FINALIZADO")
print("=" * 70)
print(f"\nMejor modelo guardado en:\n{ruta_modelo}")
print(f"\nHistorial guardado en:\n{ruta_historial}")
print(f"\nGráficas guardadas en:\n{ruta_loss}\n{ruta_dice}\n{ruta_iou}")