

\# Informe técnico — U-Net Baseline FUSeg



\## 1. Objetivo



Implementar y evaluar una arquitectura U-Net como modelo de referencia para la segmentación automática de úlceras de pie diabético utilizando el conjunto de datos FUSeg.



Este experimento constituye la línea base para posteriores mejoras y comparaciones de modelos.



\## 2. Conjunto de datos



Dataset: Foot Ulcer Segmentation Challenge (FUSeg).



\- Entrenamiento: 810 imágenes y 810 máscaras.

\- Validación: 200 imágenes y 200 máscaras.

\- Prueba: 200 imágenes sin máscaras públicas.

\- Resolución original: 512 × 512 píxeles.

\- Resolución del entrenamiento: 256 × 256 píxeles.



Se conservaron los archivos originales del dataset.



Durante la auditoría inicial se identificaron 24 máscaras vacías: 19 en entrenamiento y 5 en validación.



También se identificó la máscara 0233.png, que contiene valores 0, 32 y 255. Para la segmentación binaria se utiliza la condición máscara > 0 durante el preprocesamiento.



\## 3. Arquitectura implementada



Modelo: U-Net con encoder, bottleneck, decoder y conexiones de salto.



\- Parámetros totales: 1.946.993.

\- Parámetros entrenables: 1.944.049.

\- Parámetros no entrenables: 2.944.

\- Entrada: 256 × 256 × 3.

\- Salida: 256 × 256 × 1.

\- Activación de salida: sigmoid.



La arquitectura fue comprobada mediante model.summary().



\## 4. Configuración del entrenamiento



\- Framework: TensorFlow / Keras.

\- Procesamiento: CPU.

\- Batch size: 4.

\- Épocas ejecutadas: 20.

\- Optimizador: Adam.

\- Learning rate inicial: 0.0001.

\- Función de pérdida: Binary Crossentropy + Dice Loss.

\- Semilla configurada: 42.

\- Data Augmentation: no aplicado en esta primera corrida.



El entrenamiento se realizó sobre el dataset original, incluyendo las máscaras vacías.



\## 5. Resultados experimentales



| Indicador | Resultado |

|---|---:|

| Épocas completadas | 20 |

| Mejor Dice de validación | 0.6273 |

| Época del mejor Dice | 19 |

| Mejor IoU de validación | 0.6923 |

| Época del mejor IoU | 16 |

| Loss inicial de entrenamiento | 1.6242 |

| Loss final de entrenamiento | 0.2955 |

| Loss inicial de validación | 1.4788 |

| Loss final de validación | 0.4319 |



Evaluación final del modelo con los mejores pesos restaurados:



| Métrica | Valor |

|---|---:|

| Loss | 0.4360 |

| Dice continuo | 0.6273 |

| IoU binario | 0.6527 |

| Precision | 0.8205 |

| Recall | 0.7740 |



Nota: Dice se calcula sobre probabilidades continuas, mientras que IoU utiliza predicciones binarizadas con umbral 0.5. Por tanto, estas métricas todavía no deben compararse directamente.



Los resultados corresponden al conjunto de validación y no constituyen una evaluación independiente sobre el conjunto de prueba.



\## 6. Análisis de los resultados



Las curvas de entrenamiento muestran una reducción progresiva de la función de pérdida tanto en entrenamiento como en validación.



El Dice de validación alcanzó su mejor resultado en la época 19, mientras que el IoU de validación alcanzó su mejor valor en la época 16.



Se observa una separación entre las curvas de entrenamiento y validación en las últimas épocas. Es necesario realizar análisis adicionales antes de concluir si existe sobreajuste.



El modelo demuestra aprendizaje durante el entrenamiento, pero todavía falta evaluar visualmente la calidad de las máscaras predichas y cuantificar los errores de segmentación.



\## 7. Archivos generados



Los siguientes archivos están guardados localmente:



Modelo entrenado:

\- modelos/unet\_fuseg\_baseline.keras



Historial:

\- resultados/historial\_unet\_baseline.json



Gráficas:

\- resultados/unet\_baseline\_loss.png

\- resultados/unet\_baseline\_dice.png

\- resultados/unet\_baseline\_iou.png



Las carpetas modelos/ y resultados/ están excluidas actualmente del control de versiones mediante .gitignore.



Por tanto, estos archivos no se incluyen automáticamente en GitHub.



\## 8. Actividades pendientes



1\. Visualizar imágenes originales, máscaras reales y máscaras predichas.

2\. Unificar el cálculo de Dice e IoU utilizando criterios consistentes.

3\. Analizar falsos positivos, falsos negativos y lesiones pequeñas.

4\. Investigar el efecto de las 24 máscaras vacías.

5\. Comparar el rendimiento con y sin las máscaras vacías, manteniendo intacto FUSeg.

6\. Evaluar posteriormente Data Augmentation y diferentes resoluciones.

7\. Repetir los experimentos con un protocolo de evaluación reproducible.

8\. Documentar las mejoras y comparar resultados.



\## 9. Relación con Trello



A1 — Repositorio reproducible:

Actualización descargada y auditoría ejecutada satisfactoriamente en el computador de desarrollo.



A2 — Máscaras vacías y anomalías:

Auditoría inicial realizada. Pendientes los experimentos comparativos.



A3 — Baseline y métricas:

Primer entrenamiento ejecutado. Pendientes la unificación de métricas y la repetición experimental.



A4 — Visualización de predicciones:

Pendiente de desarrollo y validación.



\## 10. Conclusión preliminar



Se implementó y entrenó satisfactoriamente una primera arquitectura U-Net para la segmentación de úlceras de pie diabético utilizando FUSeg.



Se verificaron 1.946.993 parámetros y se completaron 20 épocas de entrenamiento.



Los resultados permiten establecer una línea base experimental inicial para continuar con la evaluación cuantitativa, la visualización de predicciones y la optimización del modelo.



Este resultado no constituye una validación clínica ni demuestra todavía capacidad de generalización sobre datos externos.



