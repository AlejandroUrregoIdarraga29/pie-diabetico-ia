



Nova Luz: Sistema Embebido Inteligente para Heridas Crónicas
Proyecto del curso Sistemas Embebidos 2026-2 (Universidad Central). Equipo Nova Luz: Alejandro Urrego, Johan González y Jhonny Jiménez.

Sistema que segmenta úlceras de pie diabético mediante una red U-Net, permite visualizar y validar los resultados desde una aplicación web e integra un módulo experimental de generación de pulsos eléctricos bifásicos mediante ESP32-S3 y MCP4822.

La web constituye el centro de control del sistema: permite cargar imágenes, visualizar la segmentación, registrar decisiones y supervisar el módulo electrónico. La integración entre la decisión clínica y la generación de pulsos continúa en desarrollo.

El módulo electrónico se ha implementado y evaluado exclusivamente en condiciones de laboratorio mediante una carga resistiva de 2,2 kΩ, sin aplicación sobre pacientes.

Capa	Dónde se aplica
Visión e inferencia	U-Net exportada a LiteRT/TFLite, ejecutada en Raspberry Pi
Control embebido	ESP32-S3 programado con Arduino y PlatformIO
Generación de señales	MCP4822, con dos perfiles bifásicos de 0,5 Hz y 50 Hz
Comunicación	MQTT, USB serial y red local
Aplicación web	FastAPI + frontend HTML/CSS/JS
Interfaz física	Pantalla TFT táctil conectada a Raspberry Pi
Validación experimental	Osciloscopio y carga resistiva de 2,2 kΩ
Contenido
Arquitectura utilizada
Diagrama de componentes
Diagrama de secuencia
Modelo de IA (U-Net)
Aplicación web
Modelo de datos
Instrucciones para ejecutar el proyecto
Metodología de trabajo
Historial de tareas oficial de Trello
Tecnologías
Estado actual y limitaciones
Trabajo futuro
1. Arquitectura utilizada
El backend sigue el patrón Repository con interfaces, de modo que la IA, la base de datos y el hardware se pueden cambiar sin tocar la API ni el frontend.

api: rutas FastAPI y esquemas Pydantic.
services: interfaces (interfaces.py) e implementaciones simuladas o reales.
frontend: plantilla HTML, estilos y lógica en JavaScript.
hardware: ESP32-S3 y convertidor digital-analógico MCP4822.
comunicación: intermediación entre FastAPI, MQTT y comunicación serial.
interfaz TFT: visualización local de variables, estados y perfiles del generador.
Estructura principal del repositorio:

.
├── app/
│   ├── main.py
│   ├── models/
│   │   └── schemas.py
│   ├── services/
│   │   └── interfaces.py
│   ├── templates/
│   │   └── index.html
│   └── static/
│       ├── css/
│       ├── js/
│       │   ├── app.js
│       │   └── nova_pulse_profiles.js
│       └── img/
├── data/
├── docs/
│   └── adr/
├── firmware/
│   ├── ESP32S3_MCP4822_Pulsos/
│   └── respaldos/
│       ├── main_0_5Hz_original.cpp
│       └── main_50Hz_original.cpp
├── reports/
├── tests/
│   └── test_api.py
├── mqtt_serial_bridge.py
├── requirements.txt
└── README.md
El firmware integrado de dos perfiles también se conserva en el proyecto local de PlatformIO utilizado para programar el ESP32-S3. Su incorporación definitiva al repositorio debe verificarse antes de cerrar la integración.

La aplicación de la pantalla TFT se encuentra en la Raspberry Pi, en el directorio ~/nova_luz_tft/.

Reglas de diseño que se respetan:

La web nunca habla directamente con el hardware: las órdenes pasan por la API.
Los servicios dependen de interfaces, no de implementaciones concretas.
Los pacientes se identifican con un código anónimo (ADR-002).
El umbral de binarización tiene límites establecidos entre 0.30 y 0.70.
Los comandos de control del laboratorio se transmiten mediante MQTT y comunicación serial.
La selección de perfiles se realiza con la generación detenida.
El módulo de estimulación es experimental y no constituye un dispositivo médico validado.
1.1. Arquitectura de comunicación del módulo NOVA LUZ
La integración de laboratorio utiliza la siguiente cadena:

APLICACIÓN WEB / PANTALLA TFT
             |
             v
       FastAPI :8001
             |
             v
       MQTT Mosquitto
             |
             v
   Raspberry Pi 3 B+
  mqtt_serial_bridge.py
             |
             v
      USB SERIAL
             |
             v
         ESP32-S3
             |
          SPI
             |
             v
          MCP4822
             |
             v
      Circuito de ensayo
             |
             v
    Carga resistiva 2,2 kΩ
             |
             v
        Osciloscopio
El backend recibe las solicitudes provenientes de la web y la pantalla TFT, mientras que el puente MQTT–serial permite transmitir los comandos al microcontrolador.

La separación entre interfaces, API y firmware facilita el mantenimiento del sistema y permite conservar la implementación existente de segmentación de imágenes.

2. Diagrama de componentes
La generación de pulsos y la aplicación web forman parte de una arquitectura integrada, mientras que la habilitación automática de estimulación a partir de decisiones clínicas sigue siendo una funcionalidad futura.

3. Diagrama de secuencia
3.1. Flujo de segmentación y decisión
3.2. Flujo de generación de pulsos de laboratorio
Este segundo diagrama representa la arquitectura de integración del laboratorio. La comunicación completa debe distinguirse de la confirmación física de la señal, que requiere medición experimental.

4. Modelo de IA (U-Net)
Dataset: Foot Ulcer Segmentation Challenge (810 pares de entrenamiento, 200 de validación y 200 imágenes de prueba sin máscaras), procesado a 512×512.
Se aislaron las máscaras vacías, se binarizaron las máscaras con valor > 0 y se definió una partición de validación limpia de 187 imágenes.
Métricas unificadas: Dice e IoU, calculadas con la misma función sobre la misma partición.
Dice por imagen en validación limpia: 0.6775 (corrida 1) y 0.7348 (corrida 2).
Exportación a LiteRT/TFLite (float32) y verificación numérica frente a Keras.
Validación en Raspberry Pi: 100 % de equivalencia en 10 imágenes de prueba respecto a Windows.
La arquitectura U-Net permite realizar segmentación semántica de la lesión y producir una máscara que diferencia los píxeles asociados con la úlcera del resto de la imagen.

La validación experimental del modelo se realizó de manera independiente de las pruebas del generador electrónico.

Las actividades A7 y A8 registran en Trello la captura de imagen y el flujo captura → segmentación → máscara en pantalla. La disponibilidad de estos módulos en el código debe distinguirse de su ejecución efectiva con la cámara y el servicio de IA reales el día de la demostración. El tablero usa la expresión «ESP32-S3-CAM» en A7; el equipo también desarrolló integración con cámara IMX219 en Raspberry. Debe confirmarse el dispositivo utilizado antes de declarar un único hardware de captura.

5. Aplicación web
Panel de decisión clínica en tres pasos:

Captura: código de paciente e imagen de la lesión.
Validación: overlay de la segmentación, área estimada y estado de la sesión.
Decisión: umbral de binarización, notas clínicas, aprobar o rechazar.
Características de la interfaz:

Pantalla de carga con el logo y logo fijo en el encabezado.
Encabezado fijo con el botón DETENER SISTEMA siempre visible, incluso con scroll y en celular.
Diseño responsivo y paleta tomada del logo (azul marino, azul cielo y naranja).
Indicadores de estado del sistema y del ESP32.
5.1. Integración del módulo de pulsos NOVA LUZ
Se incorporó a la aplicación web un módulo para visualizar y controlar los ensayos eléctricos de laboratorio.

Este módulo permite:

Seleccionar el perfil original de 0,5 Hz.
Seleccionar el perfil experimental de 50 Hz.
Consultar los tiempos programados de cada señal.
Visualizar los parámetros de generación.
Enviar la solicitud de selección mediante FastAPI y MQTT.
Utilizar los botones GENERAR y DETENER.
Consultar indicadores de estado del laboratorio.
El tercer perfil, PERSONALIZADO, dispone de campos editables en la interfaz, pero sus parámetros todavía no se aplican al firmware del ESP32-S3.

5.2. Firmware ESP32-S3 y MCP4822
El sistema electrónico utiliza un ESP32-S3 para controlar el convertidor digital-analógico MCP4822, mediante el protocolo SPI.

La programación se desarrolló en C++ utilizando Arduino y PlatformIO.

Asignación de pines:

Señal	ESP32-S3
CS del MCP4822	GPIO10
MOSI	GPIO11
SCK	GPIO12
Comunicación con Raspberry	Puerto serial USB
Se conservaron los códigos y niveles DAC utilizados durante el desarrollo de las versiones originales.

La señal bifásica se genera mediante la alternancia de los canales A y B del MCP4822:

Fase A: el canal A presenta un nivel superior al canal B.
Intervalo: ambos canales se establecen en cero.
Fase B: el canal B presenta un nivel superior al canal A.
Reposo: ambas salidas permanecen en cero hasta el siguiente ciclo.
Perfiles de generación
Parámetro	Perfil 0,5 Hz	Perfil 50 Hz
Frecuencia nominal	0,5 Hz	50 Hz
Período nominal	2000 ms	20 ms
Duración fase A	200 ms	100 µs
Intervalo entre fases	100 ms	100 µs
Duración fase B	400 ms	100 µs
Reposo nominal	1300 ms	19,7 ms
Selección serial	0	5
Los tiempos corresponden a los parámetros nominales del firmware. La duración efectiva de cada fase puede incluir retardos de ejecución y comunicación SPI, por lo que su exactitud debe establecerse mediante mediciones.

Comandos seriales
Comando	Función
0	Seleccionar perfil de 0,5 Hz
5	Seleccionar perfil de 50 Hz
s	GENERAR: iniciar la señal
p	DETENER: finalizar la generación
h	Heartbeat de comunicación
El firmware conserva una supervisión temporal de comunicación de 5000 ms. El puente de laboratorio también incorpora un límite de duración configurable, utilizado durante las pruebas.

La selección del perfil se realiza únicamente cuando la generación está detenida.

5.3. Comunicación Raspberry Pi, MQTT y ESP32-S3
La Raspberry Pi se utiliza como nodo de integración entre la aplicación web, el broker MQTT, la pantalla TFT y el microcontrolador.

Componentes principales:

FastAPI: recepción de solicitudes HTTP.
Mosquitto: transporte de mensajes MQTT.
mqtt_serial_bridge.py: traducción de las órdenes MQTT a comandos seriales.
ESP32-S3: ejecución del firmware de generación de señales.
MCP4822: conversión digital-analógica.
Configuración utilizada durante el desarrollo:

Servicio	Dirección o recurso
Aplicación web	http://192.168.1.62:8001
FastAPI	Puerto 8001
Broker MQTT	192.168.1.53:1883
Comunicación ESP32	/dev/ttyACM0 durante las pruebas
Canal de órdenes	nova_luz/lab/command
La API emplea el endpoint:

POST /api/v1/pulse/lab

Acciones incorporadas:

START_LAB: solicitar inicio de generación.
STOP_LAB: solicitar parada.
SET_PROFILE: solicitar selección del perfil de frecuencia.
El puente procesa las órdenes y envía los caracteres correspondientes al ESP32-S3.

La selección utiliza los mismos mecanismos de autorización de laboratorio implementados para el control de generación.

Los mensajes MQTT confirman la recepción o transmisión de solicitudes, mientras que la comprobación de la forma de onda corresponde a la medición con osciloscopio.

La dirección del broker y la IP de la Raspberry pueden cambiar entre la red doméstica y la red compartida de la universidad. La integración agregó opciones de configuración de MQTT_HOST y MQTT_PORT; las direcciones de la tabla son referencias históricas de una red de pruebas, no una IP permanente. Verificar IP, USB serial y estado del broker en la red activa antes de ejecutar los servicios.

5.4. Pantalla TFT táctil
Se desarrolló una interfaz TFT local para la Raspberry Pi, utilizando Python.

La pantalla ofrece navegación entre:

INICIO.
PULSOS.
CONTROL.
WEB.
RED / IP.
ÓRDENES.
SISTEMA.
En el menú de pulsos se incorporó un selector de perfiles:

0,5 Hz → 50 Hz → CUSTOM

Las representaciones gráficas muestran los tiempos y la estructura de las señales.

La interfaz utiliza FastAPI para solicitar las acciones de control. Los comandos de selección de perfiles también fueron incorporados al código de la TFT.

El perfil CUSTOM permanece como opción visual, pendiente de implementación y validación.

La pantalla incluye controles para GENERAR y DETENER, conservando la lógica de comunicación existente.

En el tablero esta integración corresponde a B7 · Integración de perfiles WEB/TFT, marcada como «Hecho». La descripción de B7 aclara que la sincronización del estado real entre interfaces todavía requiere validación; tener botones o selectores visibles no la demuestra.

5.5. Validación experimental de las señales
Se realizó una comprobación funcional de ambos perfiles con el osciloscopio, utilizando el montaje experimental y una carga resistiva de 2,2 kΩ.

Para el perfil de 0,5 Hz, se utilizó una configuración de visualización aproximada de:

Base de tiempo: 500 ms/div.
Escala vertical: 500 mV/div.
Para el perfil de 50 Hz, se utilizó una configuración aproximada de:

Base de tiempo: 1 ms/div.
Escala vertical: 200 mV/div.
En ambos casos se observó la respuesta correspondiente al perfil seleccionado.

La prueba permitió comprobar funcionalmente el cambio entre las dos configuraciones de generación.

Las escalas del osciloscopio corresponden a ajustes de visualización y no deben confundirse con valores medidos de amplitud, período, corriente o precisión temporal.

No se dispone en este documento de una caracterización metrológica completa de amplitud, ancho de pulso, error de frecuencia y respuesta de la etapa analógica.

Las pruebas se limitaron al montaje experimental, sin conexión a personas.

6. Modelo de datos
La API persiste las sesiones clínicas con SQLAlchemy. Cada sesión guarda el paciente (código anónimo), el resultado de la segmentación y la decisión del médico.

Campo	Descripción
session_id	Identificador único de la sesión
patient_code	Código anónimo del paciente (ADR-002), sin nombres
area_pixels	Área segmentada en píxeles
status	Estado de la sesión (por ejemplo PENDING)
overlay_image	Ruta de la imagen con la segmentación superpuesta
decision	APPROVED o REJECTED (nulo hasta que el médico decide)
threshold	Umbral de binarización usado, entre 0.30 y 0.70
notes	Notas clínicas del médico
Esquemas de la API (app/models/schemas.py): SessionCreate (entrada de la captura), DecisionCreate (decisión, umbral y notas) y SessionResponse (respuesta con área, estado y overlay).

7. Instrucciones para ejecutar el proyecto
Requisitos generales: Python 3.12 y Git.

7.1. Entorno de desarrollo
git clone https://github.com/AlejandroUrregoIdarraga29/pie-diabetico-ia.git
cd pie-diabetico-ia
python -m venv pie_diabetico_env
Activación del entorno en Windows:

pie_diabetico_env\Scripts\activate
pip install -r requirements.txt
Ejecución de la aplicación web de desarrollo:

uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
Componente	URL
Panel de control local	http://localhost:8000
Documentación API	http://localhost:8000/docs
Para acceder desde otro dispositivo conectado a la misma red:

http://IP-DE-TU-PC:8000

Pruebas automatizadas:

pytest tests/
7.2. Ejecución en Raspberry Pi
El entorno experimental de NOVA LUZ se ejecuta desde el directorio:

cd ~/pie_diabetico_web
La aplicación web utiliza FastAPI en el puerto 8001.

El puente de comunicación utiliza:

python mqtt_serial_bridge.py
La configuración del laboratorio requiere variables de entorno para habilitación y autorización, incluyendo:

LAB_ENABLED.
LAB_TOKEN.
LAB_WEB_ENABLED.
LAB_WEB_PIN.
MQTT_ENABLED.
Estas variables deben suministrarse mediante la configuración local autorizada. No deben publicarse PIN, tokens ni credenciales en GitHub.

Durante el desarrollo se recuperaron los comandos locales de arranque de los servicios de la Raspberry Pi.

Cuando dichos archivos de configuración estén disponibles, pueden ejecutarse en terminales independientes:

cd ~/pie_diabetico_web
bash ~/.nova_luz_mqtt_start
Y para FastAPI:

cd ~/pie_diabetico_web
bash ~/.nova_luz_web_start
Los archivos anteriores son configuraciones locales del equipo, no componentes portables del repositorio.

Nota de reproducción: estos scripts pueden depender de rutas de Python, entornos virtuales y direcciones de red específicas del equipo. Antes de usarlos hay que verificar el intérprete de ~/venv_a6, el acceso a la red/broker y el dispositivo serial real; no deben copiarse credenciales ni asumir que un proceso web iniciado significa MQTT o salida física operativa. La activación de laboratorio requiere autorización explícita.

La pantalla TFT se ejecuta desde el directorio:

/home/alejandro/nova_luz_tft/
Archivo principal:

nova_luz_panel.py
Se deben conservar las configuraciones locales de acceso a pantalla, puertos y periféricos.

7.3. Firmware ESP32-S3
El desarrollo del firmware se realizó mediante Visual Studio Code y PlatformIO.

Configuración principal:

[env:esp32-s3-devkitc-1]
platform = espressif32
board = esp32-s3-devkitc-1
framework = arduino
monitor_speed = 115200

build_flags =
    -D ARDUINO_USB_CDC_ON_BOOT=1
    -D ARDUINO_USB_MODE=1
El archivo principal de programación es:

src/main.cpp

Se conservaron en Git los códigos originales de 0,5 Hz y 50 Hz antes de realizar su integración.

La versión integrada contiene ambos perfiles en un único firmware, evitando la necesidad de cargar programas diferentes para cambiar la frecuencia.

8. Metodología de trabajo
Flujo por tarea, una rama por cada una:

Tarea en Trello (flujo simple y lineal).
Rama Git por tarea (feature/...).
Desarrollo y pruebas locales.
Commit y push de la rama.
Pull Request y merge a main.
Actualizar Trello y pasar a la siguiente tarea.
Para la integración electrónica se aplicó adicionalmente el siguiente procedimiento:

Conservación de los códigos originales del firmware.
Implementación individual de los perfiles.
Integración de ambos perfiles en el ESP32-S3.
Compilación y carga desde PlatformIO.
Observación de las señales con osciloscopio.
Integración progresiva con MQTT, FastAPI y TFT.
Registro de modificaciones y respaldos.
Actualización de la documentación técnica.
Se priorizó conservar las funcionalidades existentes de segmentación, comunicación y control.

9. Historial de tareas oficial de Trello
Fuente: Tablero Nova Luz, exportación del 24 de noviembre de 2026. Se conservaron los 22 identificadores oficiales de los carriles A (A1–A8), B (B1–B7), C (C1–C3) y W (W0, W1, W2a, W3). No existe un «carril E» en esta documentación.

Cómo interpretar el estado: todas las tarjetas codificadas aparecen en la columna Hecho de Trello. Esto refleja el estado registrado en el tablero, no una certificación de que cada ensayo técnico se haya completado. En particular, las descripciones de B6, B7 y C1–C3 conservan verificaciones pendientes. Se indican expresamente para no confundir implementación, prueba reportada y validación demostrada.

Carril A: software, visión e inteligencia artificial
Tarjeta oficial de Trello	Estado en tablero	Avance documentado y límites de verificación	Rama indicada en README previo
A1 · Repo reproducible: rutas relativas, README y versiones fijadas	Hecho	Repositorio reproducible, rutas relativas, dependencias y documentación base. El criterio de reproducción en clon limpio está definido en la tarjeta.	feature/a1-repo-reproducible
A2 · Máscaras vacías, máscara 0233 y partición de evaluación	Hecho	Revisión de 24 máscaras vacías, anomalía 0233, datos de prueba y partición de evaluación; decisiones del dataset documentadas.	feature/a2-datos
A3 · Documentar el baseline, unificar métricas y repetir una corrida	Hecho	Baseline U-Net, métricas Dice/IoU bajo evaluación homogénea y repetición de entrenamiento. Los resultados numéricos se documentan en la sección 4.	feature/a3-baseline
A4 · Script de visualización: imagen, máscara real y máscara predicha	Hecho	Visualización comparativa de imagen original, máscara real y predicción, incluidos casos favorables y desfavorables.	feature/a4-visualizacion
A5 · Exportar el modelo para la Raspberry	Hecho	Exportación del modelo para inferencia en Raspberry mediante LiteRT/TFLite y comparación con Keras.	feature/a5-exportar-tflite
A6 · Modelo corriendo en la Raspberry sobre imágenes de validación	Hecho	Inferencia del modelo en Raspberry sobre imágenes de validación; revisar los registros de latencia y memoria para citar cifras.	feature/a6-raspberry
A7 · ESP32-S3-CAM capture y envíe la imagen a la Raspberry	Hecho	Tarjeta de captura y transferencia de imagen a Raspberry. La integración de cámara aparece en el trabajo fusionado; confirmar en la demo la cámara efectivamente conectada.	No especificada en Trello
A8 · Captura → segmentación → máscara en pantalla	Hecho	Flujo captura → inferencia U-Net → máscara/overlay en pantalla. La integración LiteRT se incorporó en el trabajo de software; verificar el modo real frente al simulado al ejecutarla.	No especificada en Trello
Carril B: hardware, firmware y FreeRTOS
Tarjeta oficial de Trello	Estado en tablero	Avance documentado y límites de verificación	Rama indicada en README previo
B1 · Inventario de hardware y esquema de conexiones (borrador)	Hecho	Inventario y borrador de conexiones: Raspberry, ESP32-S3, cámara, MCP4822, alimentación, instrumentos y carga de ensayo.	No especificada en Trello
B2 · FreeRTOS verificado en la ESP32-S3: dos tareas y una cola	Hecho	Tareas FreeRTOS de distinta prioridad y comunicación mediante cola; la tarjeta exige registro serial, uso de pila y ensayo reproducible.	No especificada en Trello
B3 · Diseño de tareas (diagrama) y tarea de seguridad que apaga la salida	Hecho	Diseño de tareas y prioridades, recursos compartidos y lógica de seguridad para apagar la salida. Confirmar la prueba documental de parada.	No especificada en Trello
B4 · Pulsos con temporización, medidos	Hecho	Firmware integrado con perfiles de 0,5 Hz y 50 Hz; el equipo reportó comprobación con osciloscopio. Falta anexar las capturas instrumentales.	No especificada en Trello
B5 · Circuito y electrodos con carga de prueba	Hecho	Prueba reportada exclusivamente con carga resistiva de 2,2 kΩ. No se ha acreditado validación de electrodos ni ensayos en personas.	No especificada en Trello
B6 · Comunicación Raspberry–ESP32 (iniciar y detener)	Hecho	Comunicación Raspberry–ESP32 mediante MQTT y USB serial, con comandos para iniciar/detener. Pendiente evidencia de intercambios completos y parada por pérdida de enlace.	No especificada en Trello
B7 · Integración de perfiles WEB/TFT	Hecho	Selectores de 0,5 Hz y 50 Hz en WEB/TFT; comunicación vía FastAPI y MQTT reportada. Sincronización real de estados entre WEB y TFT pendiente de validación.	No especificada en Trello
Carril C: pruebas, seguridad y cierre
Tarjeta oficial de Trello	Estado en tablero	Avance documentado y límites de verificación	Rama indicada en README previo
C1 · Pruebas de estrés y parada de emergencia	Hecho	La tarjeta figura en «Hecho», pero su descripción solicita pruebas de estrés, parada de emergencia y fallos de comunicación aún sin evidencia documentada.	No especificada en Trello
C2 · Diagramas finales y documentación	Hecho	README, arquitectura, comandos y diagramas documentados. Pendiente adjuntar capturas/registros y cerrar la guía de reproducción para terceros.	No especificada en Trello
C3 · Ensayo de la demo	Hecho	La tarjeta figura en «Hecho», aunque su descripción dice ensayo integral, guion y plan alternativo pendientes.	No especificada en Trello
Carril W: aplicación web e integración de interfaz
Tarjeta oficial de Trello	Estado en tablero	Avance documentado y límites de verificación	Rama indicada en README previo
W0 · Decisión de alcance de la web	Hecho	Alcance funcional, usuario objetivo, anonimización y criterios de operación de la web establecidos mediante ADR.	feature/w0-adr-web
W1 · Servicio en la Raspberry (API)	Hecho	Servicio FastAPI, sesiones, decisiones, estado y control desacoplados mediante interfaces; entorno configurable y pruebas de API.	feature/w1-fastapi-backend
W2a · Interfaz: sesión y decisión	Hecho	Interfaz de sesión y decisión, superposición de máscara, notas, umbral y controles visibles. Conservar la denominación oficial W2a, no W2.	feature/w2-frontend-ui
W3 – Mejoramiento del frontend	Hecho	Mejoras del frontend: identidad visual, pantalla de carga, cabecera fija, parada visible y adaptación a móvil.	feature/w3-frontend
Otras actividades que también aparecen en el tablero
Además de los 22 códigos anteriores, la exportación contiene dos tarjetas transversales en «Hecho»: Añadir roles y tareas y Mirar diferente bases de datos para realcion con el tema.... No se les asignan códigos nuevos.

La distribución de responsabilidades registrada en las etiquetas del tablero es: Johan (software, visión e integración), Alejandro (firmware y FreeRTOS) y Jhonny (hardware y seguridad eléctrica).

Entregables técnicos e integración entre carriles
Segmentación (A/W): modelo U-Net, exportación LiteRT/TFLite, captura de imagen, visualización de máscara y aplicación FastAPI para gestionar sesiones y decisiones. La ejecución en modo real depende de la configuración desplegada; un resultado en modo simulado no acredita inferencia real.
Electrónica (B): ESP32-S3, MCP4822 por SPI, perfiles nominales 0,5/50 Hz, comandos seriales 0, 5, s, p, h, supervisión temporal y ensayos limitados a carga resistiva.
Comunicación (B/W): API → MQTT Mosquitto → mqtt_serial_bridge.py en Raspberry → USB serial → ESP32-S3; topic de órdenes nova_luz/lab/command. Una conexión de red o un mensaje MQTT por sí solos no prueban la generación de una señal eléctrica.
Interfaces (B7/W): página web y pantalla TFT para seleccionar perfil y consultar controles/estados. El cierre de sincronización WEB/TFT/ESP32 debe comprobarse con los tres componentes ejecutándose.
Cierre (C): el README documenta arquitectura, funcionamiento y límites; faltan evidencias finales de seguridad, estrés, confirmación de estados, capturas instrumentales y ensayo integral según las propias descripciones de Trello.
Criterio de seguridad del proyecto: ninguna salida de este prototipo se considera validada para uso sobre personas. Las pruebas del generador se limitan al banco con carga resistiva y autorización de laboratorio.

Registro de versiones e integración de GitHub
Se conservaron los códigos originales de ambas frecuencias en el registro histórico:

40d8687 — backup: conservar firmware original de 0.5 Hz y 50 Hz

Rama de integración electrónica: feature/nova-luz-mqtt-pulsos.

El Pull Request #12 — Integración NOVA LUZ: ESP32-S3, pulsos bifásicos y comunicación MQTT se fusionó con main; incluye avances de software, cámara, segmentación y comunicación. La existencia del merge no reemplaza la verificación final sobre la Raspberry y los instrumentos de laboratorio.

10. Tecnologías
Área	Herramientas
Entorno y control de versiones	Python, Git, pip, GitHub, PlatformIO
Datos	Pandas, OpenCV, NumPy
Modelo	TensorFlow / Keras, Scikit-learn, Matplotlib, PIL
Exportación y borde	TensorFlow Lite Converter, FlatBuffers, LiteRT Runtime, XNNPACK, Raspberry Pi OS
Backend	FastAPI, Uvicorn, SQLAlchemy, Pydantic, Pytest
Frontend	HTML5, CSS3, JavaScript (Fetch API), Canvas API
Comunicación	MQTT, Mosquitto, PySerial, USB Serial, SPI
Hardware	Raspberry Pi 3 B+, ESP32-S3, MCP4822, pantalla TFT táctil
Programación embebida	C++, Arduino Framework, PlatformIO
Validación	Osciloscopio, multímetro, carga resistiva de 2,2 kΩ
Documentación	Markdown, Mermaid, ADR
11. Estado actual y limitaciones
11.1. Segmentación e inteligencia artificial
La U-Net real fue exportada a LiteRT/TFLite y se incorporó trabajo de integración con la API y el flujo A8. Antes de la demostración se debe comprobar si la instancia ejecutada usa el servicio real o MockSegmentationService, porque la selección depende de la configuración efectiva (USE_MOCKS) y del despliegue de Raspberry; un recuadro simulado no se debe presentar como inferencia real.
El slider de umbral se envía junto con la decisión; todavía no vuelve a segmentar la imagen.
La integración automática entre aprobación clínica y generación de pulsos permanece pendiente.
El área se mide en píxeles de la imagen redimensionada, sin escala real (cm/píxel).
11.2. Generación electrónica
Se implementaron dos perfiles nominales: 0,5 Hz y 50 Hz.
Ambos perfiles fueron integrados en un único firmware ESP32-S3.
Se conservaron los niveles DAC utilizados en los desarrollos originales.
Se observaron las respuestas de los dos perfiles mediante osciloscopio.
La prueba experimental se realizó con una carga resistiva de 2,2 kΩ.
Los tiempos, amplitudes y formas de onda deben caracterizarse cuantitativamente para determinar su error respecto a los valores programados.
La amplitud en la etapa analógica de potencia y la corriente entregada requieren validación adicional.
El perfil personalizado continúa sin aplicarse al hardware.
11.3. Integración WEB, MQTT y TFT
La aplicación web incorpora selección de perfiles y control de generación.
FastAPI dispone de acciones para seleccionar perfil, generar y detener.
El puente MQTT permite traducir las solicitudes autorizadas a comandos seriales.
La pantalla TFT incorpora visualización de perfiles y funciones de control.
La sincronización integral y confirmación de estados entre WEB, TFT y ESP32-S3 requiere cierre de verificación. Este pendiente también consta en la descripción oficial de la tarjeta B7, aunque la columna de Trello sea «Hecho».
Los estados de comunicación publicados por MQTT no sustituyen la medición física de la señal.
Las variables de autorización deben conservarse correctamente durante el inicio de los servicios.
Los botones GENERAR y DETENER corresponden al módulo experimental de laboratorio; la integración de la parada de emergencia global de la aplicación debe verificarse por separado.
11.4. Alcance del prototipo
NOVA LUZ constituye un prototipo académico de investigación y laboratorio.

Los resultados de segmentación y las señales eléctricas generadas no constituyen por sí mismos una validación de eficacia terapéutica o seguridad clínica.

El sistema no se encuentra habilitado para aplicación de estimulación eléctrica en personas.

12. Trabajo futuro
Inyectar LiteRTSegmentationService en lugar del servicio simulado.
Implementar el endpoint para resegmentar con el umbral elegido.
Integrar formalmente la decisión clínica con los servicios de hardware.
Verificar el funcionamiento integral de la parada de emergencia.
Incorporar un indicador explícito de modo simulado cuando se utilicen servicios mock.
Implementar una escala de medición real para el área de la lesión.
Consolidar la sincronización del perfil activo entre WEB, TFT y ESP32-S3.
Implementar el perfil personalizado con parámetros definidos y validados.
Registrar medidas cuantitativas de amplitud, frecuencia, ancho de pulso, corriente y error temporal.
Evaluar la respuesta del circuito de acondicionamiento y de la etapa analógica.
Incorporar el firmware integrado definitivo al repositorio.
Completar la documentación de interfaces, firmware y comunicación.
Mantener la trazabilidad entre las 22 tarjetas oficiales A/B/C/W de Trello y la evidencia de GitHub, sin crear identificadores ajenos al tablero.
Adjuntar capturas instrumentales, registros de pruebas de estrés/parada, evidencia de sincronización WEB/TFT y video del ensayo de demostración (tarjetas C1–C3).
Verificar en Raspberry y banco de pruebas los cambios del PR #12 ya fusionado en main, sin sobrescribir las configuraciones locales ni las modificaciones no confirmadas.
Conclusión
El proyecto NOVA LUZ ha avanzado desde el desarrollo independiente de un modelo de segmentación de úlceras y una aplicación web hacia la integración de un sistema embebido que combina inteligencia artificial, comunicación MQTT, control mediante Raspberry Pi y generación experimental de señales bifásicas.

Durante la fase de integración electrónica se consolidaron dos configuraciones de generación, 0,5 Hz y 50 Hz, utilizando un único ESP32-S3 y el convertidor MCP4822.

También se incorporaron mecanismos de selección de perfiles desde las interfaces WEB y TFT, junto con el transporte de órdenes mediante FastAPI, MQTT y comunicación serial.

Las señales fueron observadas experimentalmente mediante osciloscopio sobre una carga resistiva, permitiendo comprobar funcionalmente la operación de los perfiles desarrollados.

Como siguiente etapa se requiere consolidar la sincronización entre interfaces, completar la documentación de las mediciones y fortalecer la integración del modelo de inteligencia artificial con el sistema embebido.

El resultado constituye una base experimental para continuar el desarrollo de una plataforma interdisciplinaria que integra ingeniería electrónica, sistemas embebidos e inteligencia artificial aplicada al análisis de heridas crónicas.





