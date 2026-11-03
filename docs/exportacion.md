# Exportación a TFLite (A5)

## Comando
`python exportar_tflite.py` (modelo `modelos\unet_fuseg_baseline.keras`, 10 imágenes de la validation limpia)

## Resultado
- Formato: TFLite float32, 7,81 MB (modelo original: 7,43 MB, 1.946.993 parámetros).
- Entrada [1, 256, 256, 3] float32 (valores 0-1); salida [1, 256, 256, 1] float32 (probabilidad).
- Mayor diferencia de probabilidad frente al original: 3,53e-05.
- Píxeles de máscara distintos (umbral 0,5): 0 de 10 imágenes. Dice entre máscaras: 1,0000.

## Pendiente
- Confirmar modelo de Raspberry, sistema operativo y versión de Python.
- Probar la inferencia con `ai_edge_litert` (reemplazo de `tf.lite.Interpreter`, en desuso) y medir el tiempo por imagen.
- Evaluar cuantización solo si el tiempo en la Raspberry lo exige.
- El preprocesamiento (redimensionar a 256×256 y dividir entre 255) debe ser idéntico en la Raspberry.