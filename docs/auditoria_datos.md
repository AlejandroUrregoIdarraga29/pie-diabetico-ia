# Auditoría de datos (A2)

Dataset: Foot Ulcer Segmentation Challenge (submódulo `wound-segmentation`).
Aviso: las clasificaciones visuales fueron hechas por un integrante del equipo, sin criterio clínico.

## 1. Inventario
| Conjunto | Imágenes | Máscaras | Tamaño |
|---|---|---|---|
| train | 810 | 810 | 512×512 |
| validation | 200 | 200 | 512×512 |
| test | 200 | no tiene | 512×512 |

- Sin archivos dañados ni sin pareja.
- Todas las fotos llevan una banda negra a la derecha (relleno hasta 512×512).

## 2. Máscaras vacías
- 24 máscaras vacías: 19 en train y 5 en validation.
- Clasificación visual (`docs/clasificacion_vacias.csv`): 21 "úlcera sin anotar" y 3 "dudosa" (train: 0092, 0600, 0725).
- Ninguna quedó como "sin úlcera visible". Son posibles errores de anotación, no fotos de control.
- Nota: 0092 y 0335 son la misma foto (distancia 0) y se clasificaron distinto (dudosa / sin anotar).
- No se corrigieron máscaras: eso corresponde a un clínico.

## 3. Máscara 0233 (validation)
- 369 px de úlcera: 285 con valor 255 y 84 con valor 32.
- Los 84 forman un anillo fino alrededor de la zona de 255 (borde suavizado).
- Decisión: binarizar con `mascara > 0` (función `binarizar` en `config.py`).
- Es la única máscara con valores distintos de 0 y 255 entre las 1.010.

## 4. Duplicados (`docs/duplicados.csv`)
Hash perceptual de 256 bits sobre la imagen recortada, umbral de distancia 25: 73 pares.

| Tipo | Pares |
|---|---|
| train-train | 18 |
| train-validation | 7 |
| validation-validation | 1 |
| test-train | 33 |
| test-validation | 3 |
| test-test | 11 |

- Los 7 pares train-validation son fuga de datos: inflan el Dice de validation.
- `test` comparte 33 imágenes con train, y no tiene máscaras; por eso no sirve para evaluar.

## 5. Partición de evaluación (`docs/particion_evaluacion.csv`)
Validation limpia: **187 de 200**. Se excluyen:
- 7 duplicadas de train.
- 1 duplicada dentro de validation.
- 5 con máscara vacía y úlcera visible (0128, 0417, 0483, 0533, 0869).

Train no se modifica por ahora.

## 6. Limitaciones
- El hash perceptual detecta fotos casi idénticas, no fotos distintas del mismo paciente (no hay ID de paciente).
- Pares con distancia entre 10 y 25 no se revisaron a mano.
- Clasificación hecha por una sola persona, no clínica.

## 7. Pendiente
- A3: reentrenar y comparar con y sin las máscaras vacías, y medir el Dice con la validation limpia.
- Decidir si se excluyen de train las máscaras vacías y los duplicados.
- A8: definir el preprocesamiento (relleno o redimensionado) para fotos de la cámara.