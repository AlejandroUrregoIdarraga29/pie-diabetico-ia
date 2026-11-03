# Baseline U-Net (A3)

## Entorno
Python 3.12.5, TensorFlow 2.21.0, Keras 3.15.1, NumPy 2.5.4, OpenCV 5.0.0.93.
Resolución 256×256, batch 4, hasta 20 épocas, Adam 1e-4, pérdida BCE + Dice, sin data augmentation.

## Comandos
- Corrida 1 (semilla 42): `python entrenar_unet.py`
- Corrida 2: `python entrenar_unet.py --seed 43 --nombre run2`
- Evaluación: `python evaluar_modelo.py modelos\unet_fuseg_baseline.keras` y `python evaluar_modelo.py modelos\unet_fuseg_run2.keras`

## Métricas originales (Keras, validation de 200 imágenes)
Dice 0,655 · IoU 0,681 · precisión 0,890 · recall 0,749

No son comparables entre sí: el Dice usa probabilidades sin umbral, el IoU usa umbral 0,5, ambos se promedian por lote de 4, y precisión y recall se acumulan sobre todo el conjunto.

## Métricas recalculadas (una sola función, umbral 0,5)
| Corrida | Conjunto | Dice global | IoU global | Dice por imagen | IoU por imagen | Precisión | Recall |
|---|---|---|---|---|---|---|---|
| 1 | completa (200) | 0,7966 | 0,6619 | 0,6743 | 0,5781 | 0,8205 | 0,7740 |
| 1 | limpia (187) | 0,7946 | 0,6592 | 0,6775 | 0,5779 | 0,8248 | 0,7666 |
| 2 | completa (200) | 0,8325 | 0,7131 | 0,7375 | 0,6384 | 0,8351 | 0,8300 |
| 2 | limpia (187) | 0,8295 | 0,7087 | 0,7348 | 0,6322 | 0,8341 | 0,8250 |

## Variabilidad
Diferencia entre corridas en la validation limpia (corrida 2 menos corrida 1): Dice por imagen +0,057, IoU por imagen +0,054, Dice global +0,035, IoU global +0,050. Con solo dos corridas es una idea de la variabilidad, no una medida estadística. Una mejora menor a ~0,05 de Dice no puede atribuirse a un cambio de método sin repetir con varias semillas. Para comparar experimentos futuros se usará el Dice por imagen sobre la validation limpia.

## Limitaciones
- La mejor época se elige con la misma validation en que se reporta (optimista).
- La corrida 1 no usó semilla completa en Keras 3; no es exactamente reproducible.
- La corrida 2 se relanzó tras un error de memoria (oneDNN) usando `set TF_ENABLE_ONEDNN_OPTS=0`; difiere de la corrida 1 en la semilla (43) y en esa configuración.
- La precisión recalculada (0,82) no coincide con la de la tarjeta (0,890); esta última probablemente viene de otra corrida.
- Ninguna corrida convergió: la corrida 2 usó las 20 épocas completas, y la validación es inestable.