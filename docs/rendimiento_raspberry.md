# A6 — Evaluación de inferencia U-Net en Raspberry Pi 3

## 1. Objetivo

Implementar y evaluar la ejecución del modelo de segmentación de úlceras del pie diabético `unet_fuseg_baseline.tflite` en una Raspberry Pi 3, utilizando LiteRT como motor de inferencia.

Se busca verificar la compatibilidad del modelo con la plataforma embebida y medir el tiempo de carga, la latencia de inferencia y el consumo de memoria RAM, comparando posteriormente las predicciones con las obtenidas en Windows.

## 2. Características del hardware y software

| Característica | Especificación |
|---|---|
| Dispositivo | Raspberry Pi 3 Model B Rev 1.2 |
| Memoria RAM física | Aproximadamente 1 GB |
| Memoria reportada por Linux | 905 MiB |
| Sistema operativo | Debian GNU/Linux 13 (Trixie) |
| Arquitectura | ARM64 (aarch64) |
| Kernel | Linux 6.18.39+rpt-rpi-v8 |
| Python | 3.13.5 |
| Motor de inferencia | ai-edge-litert 2.3.0 |
| NumPy | 2.5.4 |
| OpenCV Headless | 5.0.0.93 |
| psutil | 7.2.2 |
| Pillow | 13.0.0 |
| Aceleración | CPU mediante delegado XNNPACK |
| Acceso remoto | SSH desde Windows, verificado |

La Raspberry Pi utiliza el usuario local `alejandro`. La conexión SSH fue comprobada satisfactoriamente desde Windows mediante la red doméstica.

La dirección IP utilizada durante las pruebas fue `192.168.1.62`. Esta dirección es local y puede cambiar según la red o la asignación DHCP.

No se almacenan contraseñas ni credenciales de acceso en este documento.

## 3. Modelo evaluado

Se utilizó el modelo U-Net exportado a TensorFlow Lite y disponible en:

`modelos/unet_fuseg_baseline.tflite`

| Parámetro | Valor |
|---|---|
| Arquitectura | U-Net |
| Formato | TensorFlow Lite (.tflite) |
| Tamaño del archivo | 7.806.148 bytes |
| Entrada | (1, 256, 256, 3) |
| Tipo de entrada | float32 |
| Salida | (1, 256, 256, 1) |
| Tipo de salida | float32 |
| Tarea | Segmentación binaria de úlceras |

El modelo fue cargado correctamente mediante `ai-edge-litert`, sin requerir la instalación completa de TensorFlow en la Raspberry Pi.

## 4. Preparación del entorno

Se creó un entorno virtual independiente para evitar modificaciones sobre las bibliotecas del sistema operativo.

Comandos utilizados en la Raspberry:

```bash
python3 -m venv ~/venv_a6
source ~/venv_a6/bin/activate
```

Posteriormente se instalaron las dependencias:

```bash
python -m pip install ai-edge-litert
python -m pip install opencv-python-headless psutil
python -m pip install Pillow
```

La instalación de LiteRT fue exitosa y se verificó mediante:

```bash
python -c "from ai_edge_litert.interpreter import Interpreter; print('LiteRT OK')"
```

Resultado:

```text
LiteRT OK
```

Los registros de instalación se almacenaron localmente en:

- `~/instalacion_litert_a6.log`
- `~/instalacion_dependencias_a6.log`

Pillow se instaló posteriormente al identificar que era necesario para guardar las máscaras generadas.

## 5. Procedimiento experimental

El script `inferencia_raspberry.py` se transfirió desde Windows mediante SCP, junto con el modelo TFLite y diez imágenes de prueba.

Las imágenes utilizadas fueron:

`0001.png`, `0079.png`, `0211.png`, `0349.png`, `0451.png`, `0566.png`, `0674.png`, `0809.png`, `0905.png` y `1009.png`.

### 5.1. Preprocesamiento

El procesamiento en Raspberry Pi consistió en:

1. Leer la imagen PNG utilizando OpenCV.
2. Convertir el orden de canales BGR a RGB.
3. Redimensionar a 256 × 256 píxeles mediante interpolación lineal.
4. Convertir los valores a `float32`.
5. Normalizar los valores dividiendo entre 255.
6. Agregar la dimensión de lote para obtener `(1, 256, 256, 3)`.

### 5.2. Ejecución de inferencias

Inicialmente se verificó la ejecución del modelo mediante una prueba con una inferencia por imagen.

Comando:

```bash
python ~/pie_diabetico_ia/inferencia_raspberry.py --repeticiones 1 --calentamiento 0
```

La prueba fue completada correctamente para las diez imágenes después de instalar Pillow.

Posteriormente se ejecutó el benchmark principal:

```bash
python ~/pie_diabetico_ia/inferencia_raspberry.py --repeticiones 50 --calentamiento 3
```

Se realizaron:

- 10 imágenes diferentes.
- 3 inferencias de calentamiento por imagen.
- 50 inferencias medidas por imagen.
- 500 inferencias medidas en total.

El cronometraje se realizó alrededor de la ejecución del intérprete (`invoke()`), sin incluir en cada medición el tiempo de lectura y redimensionamiento de la imagen.

Se registraron la media, mediana y latencia máxima de cada conjunto de 50 ejecuciones, además de la memoria RSS del proceso.

## 6. Resultados experimentales

### 6.1. Latencia por imagen

| Imagen | Media (ms) | Mediana (ms) | Máximo (ms) | Memoria RSS (MiB) |
|---|---:|---:|---:|---:|
| 0001.png | 1954.39 | 2020.65 | 2440.50 | 139.56 |
| 0079.png | 1971.73 | 2024.76 | 2394.21 | 142.39 |
| 0211.png | 1925.24 | 1936.40 | 2456.18 | 142.39 |
| 0349.png | 1865.69 | 1903.63 | 2452.61 | 142.39 |
| 0451.png | 1986.97 | 2052.40 | 2441.12 | 142.39 |
| 0566.png | 1935.14 | 1965.59 | 2393.53 | 142.39 |
| 0674.png | 1922.69 | 1989.01 | 2424.27 | 142.39 |
| 0809.png | 2003.31 | 2070.07 | 2435.76 | 142.39 |
| 0905.png | 2058.05 | 2070.94 | 2392.37 | 142.39 |
| 1009.png | 2009.95 | 2061.03 | 2428.75 | 142.39 |

### 6.2. Resumen de rendimiento

| Indicador | Resultado |
|---|---:|
| Inferencias medidas | 500 |
| Tiempo medio global, calculado desde las medias por imagen | 1963.32 ms |
| Tiempo medio expresado en segundos | 1.963 s |
| Mayor tiempo individual registrado | 2456.18 ms |
| Tiempo de carga del modelo | 198.017 ms |
| Memoria RSS inicial | 29.13 MiB |
| Memoria RSS final registrada | 142.39 MiB |
| Imágenes procesadas correctamente | 10/10 |

El tiempo medio global se calculó como el promedio de las diez medias registradas. Debido a que cada imagen tuvo 50 ejecuciones, equivale al promedio de las 500 inferencias medidas, dentro de la precisión de los datos presentados.

La memoria RSS representa la memoria residente del proceso Python; no equivale al consumo total de RAM de todo el sistema.

### 6.3. Interpretación

El modelo U-Net pudo ejecutarse correctamente en la Raspberry Pi 3 mediante LiteRT.

La latencia media fue aproximadamente de 1.96 segundos por imagen, lo cual indica que la plataforma puede utilizarse para realizar pruebas de inferencia individuales, aunque todavía debe evaluarse su adecuación a los requisitos de respuesta de la aplicación web.

Durante las mediciones, la memoria RSS se mantuvo aproximadamente en 142.39 MiB después de las primeras imágenes. No se observó un crecimiento sostenido en los valores registrados.

Los resultados muestran viabilidad de ejecución, pero no representan una evaluación de toda la cadena de adquisición, transmisión, procesamiento, presentación web y comunicación con el microcontrolador.
## 7. Comparación y Validación de Equivalencia Multi-Imagen (PC vs. Raspberry Pi)

Inicialmente se identificó una leve variación de probabilidades al comparar usando bibliotecas de preprocesamiento distintas (TensorFlow vs. OpenCV). Al estandarizar el script de evaluación (`validar_equivalencia.py`) para utilizar la misma conversión de imagen y umbralización, se evaluaron las 10 imágenes del dataset de prueba.

### 7.1. Resultados del Benchmark Multi-Imagen

| Imagen | Máx. Dif. Probabilidad | Coincidencia Binaria (%) | IoU Binario | Estado |
|---|:---:|:---:|:---:|:---:|
| 0001.png | 0.000000 | 100.00% | 1.0000 | Coincidencia exacta |
| 0079.png | 0.000000 | 100.00% | 1.0000 | Coincidencia exacta |
| 0211.png | 0.000000 | 100.00% | 1.0000 | Coincidencia exacta |
| 0349.png | 0.000000 | 100.00% | 1.0000 | Coincidencia exacta |
| 0451.png | 0.000000 | 100.00% | 1.0000 | Coincidencia exacta |
| 0566.png | 0.000000 | 100.00% | 1.0000 | Coincidencia exacta |
| 0674.png | 0.000000 | 100.00% | 1.0000 | Coincidencia exacta |
| 0809.png | 0.000000 | 100.00% | 1.0000 | Coincidencia exacta |
| 0905.png | 0.000000 | 100.00% | 1.0000 | Coincidencia exacta |
| 1009.png | 0.000000 | 100.00% | 1.0000 | Coincidencia exacta |

### 7.2. Conclusión de Equivalencia

- **Coincidencia binaria promedio:** 100.00%
- **IoU binario promedio:** 1.0000
- **Diferencia en segmentación:** 0 píxeles divergentes en el lote completo.

Se confirma que el modelo `unet_fuseg_baseline.tflite` produce salidas numéricamente y clínicamente equivalentes entre la arquitectura x86_64 (Windows) y ARM64 (Raspberry Pi 3).

---

## 8. Limitaciones identificadas

1. La Raspberry Pi 3 presenta una latencia de inferencia de aproximadamente ~1.96 segundos por imagen, tiempo que se considera aceptable para una aplicación médica punto a punto (point-of-care), aunque deberá ser tomado en cuenta al diseñar la experiencia de usuario (UX) en la interfaz web.
2. El benchmark mide el tiempo directo de `invoke()`; la latencia total del sistema incluirá la transmisión HTTP desde el ESP32-S3 y la visualización en frontend.
3. Pendiente de medir el rendimiento del servidor web (FastAPI/Flask) sobre la Raspberry Pi 3 bajo carga de peticiones HTTP POST.

---

## 10. Conclusiones

1. Se confirmó la compatibilidad y excelente estabilidad de `ai-edge-litert` 2.3.0 en Raspberry Pi 3 (Debian 13 ARM64, Python 3.13.5).
2. El modelo U-Net cuantizado/exportado a TFLite procesó satisfactoriamente 500 inferencias de prueba.
3. El tiempo medio de inferencia se estableció en **1.96 segundos por imagen**, con una huella de memoria RAM contenida en **142.39 MiB RSS**.
4. **Criterio de Aceptación Cumplido:** Se verificó la equivalencia del 100% de coincidencia binaria e IoU = 1.0 en un lote de 10 imágenes entre PC y Raspberry Pi.
5. Se aprueba la integración del modelo TFLite en la arquitectura embebida del proyecto.

---