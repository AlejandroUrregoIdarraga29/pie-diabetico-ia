
from pathlib import Path
import argparse
import csv
import platform
import statistics
import time

import numpy as np
import psutil


BASE_DIR = Path(__file__).resolve().parent
MODELO = BASE_DIR / "modelos" / "unet_fuseg_baseline.tflite"
IMAGENES = BASE_DIR / "muestras"
RESULTADOS = BASE_DIR / "resultados" / "raspberry"


def cargar_interprete(ruta_modelo):
    inicio = time.perf_counter()

    try:
        from ai_edge_litert.interpreter import Interpreter
        runtime = "ai-edge-litert"
    except ImportError:
        try:
            from tflite_runtime.interpreter import Interpreter
            runtime = "tflite-runtime"
        except ImportError:
            import tensorflow as tf
            Interpreter = tf.lite.Interpreter
            runtime = "TensorFlow Lite"

    interprete = Interpreter(model_path=str(ruta_modelo))
    interprete.allocate_tensors()

    tiempo_carga = (time.perf_counter() - inicio) * 1000
    return interprete, runtime, tiempo_carga


def preparar_imagen(ruta, alto, ancho):
    # Se utiliza TensorFlow si esta disponible para reproducir
    # el preprocesamiento de visualizar_predicciones.py.
    try:
        import tensorflow as tf

        imagen = tf.io.read_file(str(ruta))
        imagen = tf.image.decode_png(imagen, channels=3)
        imagen = tf.image.resize(
            tf.cast(imagen, tf.float32),
            [alto, ancho],
            method="bilinear"
        ) / 255.0

        imagen = imagen.numpy()

    except ImportError:
        # Alternativa ligera para Raspberry Pi.
        import cv2

        imagen = cv2.imread(str(ruta), cv2.IMREAD_COLOR)
        if imagen is None:
            raise ValueError(f"No se pudo abrir: {ruta}")

        imagen = cv2.cvtColor(imagen, cv2.COLOR_BGR2RGB)
        imagen = cv2.resize(
            imagen,
            (ancho, alto),
            interpolation=cv2.INTER_LINEAR
        )
        imagen = imagen.astype(np.float32) / 255.0

    return np.expand_dims(imagen, axis=0).astype(np.float32)


def ejecutar_inferencia(interprete, entrada, indice_entrada, indice_salida):
    interprete.set_tensor(indice_entrada, entrada)

    inicio = time.perf_counter()
    interprete.invoke()
    tiempo_ms = (time.perf_counter() - inicio) * 1000

    salida = interprete.get_tensor(indice_salida)
    return salida, tiempo_ms


def main():
    parser = argparse.ArgumentParser(
        description="Benchmark de inferencia U-Net TFLite para Raspberry Pi"
    )
    parser.add_argument("--repeticiones", type=int, default=50)
    parser.add_argument("--calentamiento", type=int, default=3)
    args = parser.parse_args()

    if args.repeticiones < 1 or args.calentamiento < 0:
        parser.error("Las repeticiones deben ser >= 1 y el calentamiento >= 0")

    if not MODELO.is_file():
        raise FileNotFoundError(f"No se encontro el modelo: {MODELO}")

    rutas = sorted(IMAGENES.glob("*.png"))

    if not rutas:
        raise FileNotFoundError(f"No hay imagenes PNG en {IMAGENES}")

    RESULTADOS.mkdir(parents=True, exist_ok=True)

    proceso = psutil.Process()
    memoria_inicial = proceso.memory_info().rss / (1024 ** 2)

    interprete, runtime, tiempo_carga = cargar_interprete(MODELO)

    entrada_info = interprete.get_input_details()[0]
    salida_info = interprete.get_output_details()[0]

    forma = entrada_info["shape"]

    if len(forma) != 4 or forma[0] != 1 or forma[3] != 3:
        raise ValueError(f"Entrada no compatible: {forma}")

    if entrada_info["dtype"] != np.float32:
        raise ValueError("Este script requiere entrada float32")

    alto, ancho = int(forma[1]), int(forma[2])

    print("\n=== INFORMACION DEL SISTEMA ===")
    print("Sistema:", platform.platform())
    print("Arquitectura:", platform.machine())
    print("Runtime:", runtime)
    print("Modelo:", MODELO.name)
    print("Entrada:", entrada_info["shape"])
    print("Salida:", salida_info["shape"])
    print(f"Carga del modelo: {tiempo_carga:.3f} ms")
    print(f"Memoria inicial: {memoria_inicial:.2f} MiB")

    registros = []

    for ruta in rutas:
        imagen = preparar_imagen(ruta, alto, ancho)

        for _ in range(args.calentamiento):
            ejecutar_inferencia(
                interprete,
                imagen,
                entrada_info["index"],
                salida_info["index"]
            )

        tiempos = []
        mascara = None

        for _ in range(args.repeticiones):
            mascara, tiempo = ejecutar_inferencia(
                interprete,
                imagen,
                entrada_info["index"],
                salida_info["index"]
            )
            tiempos.append(tiempo)

        memoria = proceso.memory_info().rss / (1024 ** 2)

        if mascara.shape != (1, alto, ancho, 1):
            raise ValueError(f"Salida inesperada: {mascara.shape}")

        # Guardar probabilidades para comparar PC y Raspberry.
        np.save(RESULTADOS / f"{ruta.stem}_probabilidades.npy", mascara)

        # Mascara binaria con umbral 0.5.
        mascara_binaria = (mascara[0, :, :, 0] >= 0.5).astype(np.uint8) * 255

        # Guardamos PNG sin depender de OpenCV.
        from PIL import Image
        Image.fromarray(mascara_binaria).save(
            RESULTADOS / f"{ruta.stem}_mascara.png"
        )

        media = statistics.mean(tiempos)
        mediana = statistics.median(tiempos)
        maximo = max(tiempos)

        registros.append({
            "imagen": ruta.name,
            "media_ms": round(media, 3),
            "mediana_ms": round(mediana, 3),
            "maximo_ms": round(maximo, 3),
            "memoria_rss_mib": round(memoria, 2)
        })

        print(
            f"{ruta.name}: media={media:.2f} ms | "
            f"mediana={mediana:.2f} ms | "
            f"max={maximo:.2f} ms | "
            f"RSS={memoria:.2f} MiB"
        )

    archivo_csv = RESULTADOS / "rendimiento.csv"

    with open(archivo_csv, "w", newline="", encoding="utf-8") as archivo:
        escritor = csv.DictWriter(archivo, fieldnames=registros[0].keys())
        escritor.writeheader()
        escritor.writerows(registros)

    print("\n=== FINALIZADO ===")
    print("Imagenes procesadas:", len(registros))
    print("CSV:", archivo_csv)
    print("Resultados:", RESULTADOS)


if __name__ == "__main__":
    main()
