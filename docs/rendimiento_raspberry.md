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

## 7. Comparación de resultados entre Windows y Raspberry Pi

Se realizó una comparación inicial utilizando la imagen `0001.png`.

### 7.1. Comparación de máscaras binarias

| Parámetro | Resultado |
|---|---|
| Dimensiones en Windows | 256 × 256 |
| Dimensiones en Raspberry | 256 × 256 |
| Coincidencia de píxeles | 100 % |
| Píxeles diferentes | 0 |
| Píxeles positivos en Windows | 12 |
| Píxeles positivos en Raspberry | 12 |

Las máscaras binarias generadas en ambos sistemas coincidieron exactamente para esta imagen, utilizando un umbral de 0.5.

Este resultado no demuestra por sí mismo que la segmentación sea correcta respecto a la anotación real, ni que todas las imágenes generen máscaras idénticas.

### 7.2. Comparación de probabilidades

| Parámetro | Resultado |
|---|---:|
| Dimensiones de salida | (1, 256, 256, 1) |
| Diferencia máxima absoluta | 0.11777973 |
| Diferencia media absoluta | 0.00006487444 |
| Píxeles con diferencia superior a 0.01 | 50 |
| Coincidencia numérica exacta | No |

La mayor diferencia se identificó en la fila 120 y columna 98:

- Probabilidad en Windows: 0.53387576.
- Probabilidad en Raspberry: 0.65165550.

Aunque la máscara binaria coincidió, las probabilidades presentaron diferencias numéricas.

Una posible causa es que el script utiliza TensorFlow para redimensionar las imágenes cuando dicha biblioteca está disponible en Windows, mientras que en Raspberry utiliza OpenCV.

También pueden influir diferencias entre las implementaciones de los intérpretes y las operaciones ejecutadas por los procesadores.

Estas hipótesis no se consideran verificadas. La comparación con preprocesamiento idéntico y la evaluación del resto de las imágenes quedan pendientes.

## 8. Limitaciones identificadas

1. La Raspberry Pi 3 presenta una latencia cercana a dos segundos por inferencia. Esta característica podría afectar la experiencia de uso de una aplicación web.
2. El benchmark registra principalmente el tiempo de inferencia y no la latencia total de la aplicación.
3. No se ha medido el rendimiento de Flask o FastAPI sobre esta Raspberry.
4. La comparación de máscaras binarias se realizó inicialmente sobre una única imagen.
5. Las diferencias de probabilidades entre plataformas requieren evaluación adicional.
6. No se ha evaluado aún la adquisición de imágenes desde la ESP32-S3-CAM ni desde un dispositivo móvil.
7. La segmentación y la estimación del área no constituyen una validación clínica del sistema.

## 9. Evidencias disponibles

El script utilizado en esta actividad es:

`inferencia_raspberry.py`

El archivo CSV del benchmark completo se conservó localmente en Windows con el nombre:

`resultados/raspberry/rendimiento_raspberry_pi3.csv`

En la Raspberry se encuentra en:

`/home/alejandro/pie_diabetico_ia/resultados/raspberry/rendimiento.csv`

También se generaron máscaras binarias PNG y matrices de probabilidades NumPy para las imágenes procesadas.

Se dispone de salidas de terminal que muestran la instalación de las dependencias, la ejecución del modelo y los resultados del benchmark.

Los pesos del modelo, las imágenes y los resultados generados no forman parte de los archivos que se pretenden añadir específicamente en el commit de A6.

## 10. Conclusiones

1. Se confirmó la compatibilidad de `ai-edge-litert` 2.3.0 con Raspberry Pi 3, Debian 13, ARM64 y Python 3.13.5.
2. La U-Net exportada a TFLite pudo ejecutar correctamente las diez imágenes de prueba.
3. Las 500 inferencias medidas presentaron un tiempo promedio de 1963.32 ms por imagen.
4. La memoria RSS registrada al finalizar fue de 142.39 MiB.
5. Para la imagen `0001.png`, las máscaras binarias obtenidas en Windows y Raspberry coincidieron al 100 %, aunque las probabilidades no fueron idénticas.
6. Se comprobó que el modelo es ejecutable en esta plataforma; queda pendiente determinar si su latencia es aceptable para los requisitos finales de la aplicación web.
7. La actividad A6 aporta evidencia experimental para decidir si se mantiene la Raspberry Pi 3, se optimiza el modelo o se evalúa otra plataforma de procesamiento.

## 11. Trabajo posterior

Se propone continuar con:

- La evaluación detallada de las diferencias numéricas entre Windows y Raspberry.
- La validación de las predicciones sobre más imágenes.
- La implementación de la interfaz web para visualizar máscaras.
- La evaluación de alternativas de optimización del modelo, si la latencia requerida lo justifica.
- La integración futura de adquisición de imágenes mediante ESP32-S3-CAM.
- La comunicación supervisada con el ESP32-S3 encargado del hardware experimental.

Estas actividades son posteriores al benchmark A6 y no se consideran resultados ya realizados.

---

**Proyecto:** Segmentación de úlceras del pie diabético mediante inteligencia artificial e integración de sistemas embebidos.

**Actividad:** A6 — Inferencia del modelo U-Net en Raspberry Pi.

**Plataforma evaluada:** Raspberry Pi 3 Model B Rev 1.2.

**Estado:** Pruebas de inferencia y rendimiento completadas; documentación y entrega mediante Git pendientes.
