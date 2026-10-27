# Nova Luz

Sistema embebido para apoyo al seguimiento de heridas crónicas (úlceras de pie).
Proyecto del curso de Sistemas Embebidos 2026-2.

## Estado actual

| Parte | Estado |
|---|---|
| Segmentación de úlceras con U-Net (TensorFlow/Keras) | Baseline entrenado en PC |
| Captura con cámara (ESP32-S3 CAM) | Planeado |
| Inferencia en Raspberry Pi 5 | Planeado |
| Control con ESP32-S3 y FreeRTOS | Planeado |
| Estimulación eléctrica | Planeado. Solo se probará sobre una carga de prueba, nunca en personas |

## Arquitectura

Las líneas continuas existen hoy. Las punteadas son la propuesta de trabajo, por validar.

```mermaid
flowchart LR
 subgraph PC["PC: desarrollo y entrenamiento"]
    DS[("Dataset FUSeg")]
    TRAIN["Entrenamiento U-Net<br>TensorFlow / Keras"]
    MODEL[("Modelo .keras<br>1.946.993 parámetros")]
 end
 subgraph SIS["Sistema embebido (propuesta)"]
    CAM["ESP32-S3 CAM<br>captura"]
    PI["Raspberry Pi 5<br>segmentación"]
    ESP["ESP32-S3 con FreeRTOS<br>pulsos y seguridad"]
    HW["Circuito con límites<br>de corriente en hardware"]
    LOAD["Carga de prueba"]
 end
 DS --> TRAIN
 TRAIN --> MODEL
 MODEL -. "exportar" .-> PI
 CAM -. "Wi-Fi + HTTP: imagen" .-> PI
 PI -. "UART o USB serie: comandos y latido" .-> ESP
 ESP -.-> HW
 HW -.-> LOAD
```

## Requisitos

Python 3.12 y Git.

## Instalación

```
git clone --recurse-submodules https://github.com/AlejandroUrregoIdarraga29/pie-diabetico-ia.git
cd pie-diabetico-ia
py -m venv pie_diabetico_env
pie_diabetico_env\Scripts\activate.bat
pip install -r requirements.txt
```

## Uso

Desde la raíz del repositorio:

```
python auditoria_fuseg.py
python entrenar_unet.py
```

`entrenar_unet.py` entrena 20 épocas y en CPU tarda mucho.

## Estructura

- `config.py`: rutas del proyecto, calculadas desde la ubicación del repositorio
- `*.py`: scripts de auditoría de datos y entrenamiento
- `wound-segmentation/`: submódulo con el dataset FUSeg
- `modelos/` y `resultados/`: salidas locales, no se versionan

## Notas

- TensorFlow en Windows nativo solo usa CPU.
- El modelo entrenado no se versiona; pídelo al equipo.