# ADR-002: Arquitectura de la Interfaz Web y Control por el Profesional de Salud

* **Estado:** Propuesto / En revisión
* **Fecha:** 2026-11-09
* **Autores:** Equipo del Proyecto (Sistemas Embebidos - Pie Diabético IA)

## 1. Contexto y Problema

Se requiere una interfaz de usuario accesible y centralizada en la Raspberry Pi 3 para visualizar la captura de la úlcera del pie diabético, la máscara binaria generada por el modelo U-Net TFLite y la estimación del área.

El sistema embebido debe permitir al profesional de la salud validar la segmentación realizada por la IA antes de desencadenar acciones en el control electrónico, además de garantizar la trazabilidad de los datos respetando la privacidad del paciente.

## 2. Decisiones de Arquitectura

### 2.1. Usuario y Capacidad de Decisión
* **Usuario principal:** Profesional de la salud (médico/enfermero).
* **Control:** El sistema no actúa de forma autónoma. El profesional puede:
  - Visualizar la fotografía original, la máscara U-Net en overlay y el cálculo de área.
  - **Validar o rechazar** la segmentación binaria obtenida.
  - Ajustar parámetros en tiempo de ejecución dentro de límites seguros (ej. umbral de probabilidad $0.3 - 0.7$).
  - **Iniciar y detener** el ciclo de evaluación o transmisión hacia el módulo electrónico (ESP32 / FreeRTOS).

### 2.2. Adquisición Dual de Imágenes
La API web soportará dos fuentes de adquisición independientes mediante endpoints HTTP POST:
1. **Dispositivo Principal (ESP32-S3-CAM):** Envío automático por Wi-Fi mediante HTTP POST directo al backend.
2. **Dispositivo Secundario (Celular / Navegador):** Carga manual de fotografías desde la interfaz web utilizando la cámara del dispositivo móvil o archivos locales, sirviendo como entorno de prueba y respaldo operativo.

### 2.3. Almacenamiento, Historial y Privacidad (Privacy by Design)
* **Anonimización:** Siguiendo normativas de salud (HIPAA / GDPR), el sistema aplica minimización de datos. La identificación del paciente se maneja exclusivamente mediante un **código único de paciente/sesión** (ej. `PAC-84920` o UUID), omitiendo nombres o datos personales directos en el almacenamiento del dispositivo embebido.
* **Trazabilidad e Historial:** El sistema conservará el historial evolutivo de las lesiones asociadas a cada código de paciente para permitir el seguimiento clínico longitudinal (comparativa de área entre sesiones).
* **Persistencia (SQLite):** Se guardarán las sesiones registrando:
  - Código anónimo del paciente (`PAC-XXXX`) y timestamp.
  - Fotografía original, máscara generada y matriz de probabilidades.
  - Área calculada de la lesión (píxeles / $cm^2$).
  - Decisiones tomadas por el usuario (aprobado/rechazado, ajustes de parámetros) y registro de eventos del sistema.

### 2.4. Despliegue y Acceso
* **Servidor:** La aplicación web será servida directamente por la Raspberry Pi 3 utilizando **FastAPI / Uvicorn**.
* **Acceso:** Disponible para cualquier navegador web conectado a la misma red local Wi-Fi (`http://<IP_RASPBERRY>:8000`) o acceso remoto seguro vía VPN (Tailscale).

## 3. Criterios de Aceptación (Definición de Listo - W0)

- [x] Especificación formal del rol de usuario y flujo de decisión clínica.
- [x] Definición del esquema anonimizado y seguimiento de historial por código de paciente.
- [x] Definición del despliegue en red local servido por la Raspberry Pi.
- [ ] Aprobación explícita del documento ADR-002 por los tres integrantes del equipo.
- [ ] Presentación y revisión por parte del profesor.