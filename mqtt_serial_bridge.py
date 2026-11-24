import os
import time
import hmac
import threading

import paho.mqtt.client as mqtt
import serial
from serial.tools import list_ports

MQTT_HOST = os.getenv("MQTT_HOST", "192.168.1.53")
MQTT_PORT = int(os.getenv("MQTT_PORT", "1883"))

MQTT_SIM_TOPIC = "nova_luz/simulation/event"
MQTT_LAB_TOPIC = "nova_luz/lab/command"
MQTT_STATUS_TOPIC = "nova_luz/lab/status"

ESP_SERIAL = os.getenv("ESP_SERIAL", "5C4C189255")

LAB_ENABLED = os.getenv("LAB_ENABLED", "false").lower() == "true"
LAB_TOKEN = os.getenv("LAB_TOKEN", "")

LAB_MAX_DURATION_S = float(os.getenv("LAB_MAX_DURATION_S", "3.0"))
LAB_HEARTBEAT_INTERVAL_S = 0.5


def encontrar_esp():
    for puerto in list_ports.comports():
        if puerto.serial_number == ESP_SERIAL:
            return puerto.device
    raise RuntimeError("ESP32-S3 no encontrado")


def main():
    puerto = encontrar_esp()
    bloqueo = threading.RLock()

    estado = {
        "activo": False,
        "inicio": 0.0,
        "ultimo_h": 0.0,
        "usado": False,
        "conexion_previa": False,
        "bloqueado": False,
    }

    with serial.Serial(puerto, 115200, timeout=0.5) as esp:
        time.sleep(2)

        def enviar(comando):
            with bloqueo:
                esp.write(comando.encode("ascii"))
                esp.flush()

        def publicar(estado_mqtt):
            if cliente.is_connected():
                cliente.publish(
                    MQTT_STATUS_TOPIC,
                    estado_mqtt,
                    qos=1,
                    retain=False,
                )
            print("ESTADO:", estado_mqtt)

        def detener(motivo):
            with bloqueo:
                estado["activo"] = False
                respuesta = ""
                try:
                    enviar("p")
                    respuesta = ""
                    limite = time.monotonic() + 1.5

                    while time.monotonic() < limite:
                        linea = esp.readline().decode(
                            "utf-8", errors="replace"
                        ).strip()

                        if linea == "GENERACION DETENIDA":
                            respuesta = linea
                            break

                    if respuesta:
                        publicar("STOP_CONFIRMED_SERIAL")
                    else:
                        publicar("STOP_UNCONFIRMED")

                except serial.SerialException as error:
                    print("ERROR SERIAL:", error)
                    publicar("SERIAL_ERROR")

                print("PARADA:", motivo)

                if respuesta == "GENERACION DETENIDA" and not estado["bloqueado"]:
                    estado["usado"] = False
                    publicar("LAB_READY")
                    print("LISTO PARA OTRO ENSAYO")

        def on_connect(client, userdata, flags, reason_code, properties):
            if reason_code != 0:
                print("Error MQTT:", reason_code)
                return

            with bloqueo:
                if estado["conexion_previa"]:
                    estado["bloqueado"] = True
                    detener("RECONEXION MQTT")
                estado["conexion_previa"] = True

            client.subscribe(MQTT_SIM_TOPIC, qos=1)
            client.subscribe(MQTT_LAB_TOPIC, qos=1)
            print("MQTT conectado")
            publicar("LAB_READY" if LAB_ENABLED and not estado["bloqueado"]
                     else "LAB_BLOCKED")

        def on_disconnect(client, userdata, flags, reason_code, properties):
            with bloqueo:
                estado["bloqueado"] = True
                detener("DESCONEXION MQTT")

        def on_message(client, userdata, msg):
            if msg.retain:
                print("Mensaje retenido rechazado")
                return

            accion = msg.payload.decode(
                "utf-8", errors="replace"
            ).strip()

            print("MQTT:", msg.topic, accion.split(":")[0])

            with bloqueo:
                if msg.topic == MQTT_SIM_TOPIC:
                    if accion == "STOP_SIMULATION":
                        detener("PARADA DESDE WEB")
                    elif accion == "START_SIMULATION":
                        publicar("SIMULATION_ONLY")
                    return

                if msg.topic != MQTT_LAB_TOPIC:
                    return

                if accion == "GET_STATUS":
                    if estado["bloqueado"] or not LAB_ENABLED:
                        publicar("LAB_BLOCKED")
                    elif estado["activo"]:
                        publicar("LAB_START_SENT")
                    else:
                        publicar("LAB_READY")
                    return

                if accion == "STOP_LAB":
                    detener("STOP_LAB")
                    return

                if not accion.startswith("START_LAB:"):
                    publicar("LAB_INVALID_COMMAND")
                    return

                token_recibido = accion.partition(":")[2]

                autorizado = (
                    LAB_ENABLED
                    and bool(LAB_TOKEN)
                    and hmac.compare_digest(token_recibido, LAB_TOKEN)
                    and not estado["bloqueado"]
                    and not estado["activo"]
                    and not estado["usado"]
                )

                if not autorizado:
                    publicar("LAB_START_REJECTED")
                    return

                estado["usado"] = True

                try:
                    esp.reset_input_buffer()
                    enviar("s")

                    estado["activo"] = True
                    ahora = time.monotonic()
                    estado["inicio"] = ahora
                    estado["ultimo_h"] = ahora

                    publicar("LAB_START_SENT")
                    print("ENSAYO INICIADO: MAXIMO 3 SEGUNDOS")

                except serial.SerialException:
                    estado["bloqueado"] = True
                    detener("ERROR AL INICIAR")

        cliente = mqtt.Client(
            mqtt.CallbackAPIVersion.VERSION2,
            client_id="nova_luz_bridge_lab",
        )

        cliente.on_connect = on_connect
        cliente.on_disconnect = on_disconnect
        cliente.on_message = on_message

        # Estado seguro inicial.
        enviar("p")
        print("ESP32 conectado:", puerto)
        print("Laboratorio habilitado:", LAB_ENABLED)

        try:
            cliente.connect(MQTT_HOST, MQTT_PORT, 30)
            cliente.loop_start()

            while True:
                time.sleep(0.05)

                with bloqueo:
                    if not estado["activo"]:
                        continue

                    ahora = time.monotonic()

                    if ahora - estado["inicio"] >= LAB_MAX_DURATION_S:
                        detener("LIMITE DE 3 SEGUNDOS")
                        publicar("LAB_TIME_LIMIT_REACHED")
                        continue

                    if not cliente.is_connected():
                        estado["bloqueado"] = True
                        detener("MQTT NO DISPONIBLE")
                        continue

                    if ahora - estado["ultimo_h"] >= LAB_HEARTBEAT_INTERVAL_S:
                        try:
                            enviar("h")
                            estado["ultimo_h"] = ahora
                        except serial.SerialException:
                            estado["bloqueado"] = True
                            detener("ERROR HEARTBEAT")

        except KeyboardInterrupt:
            print("Cerrando puente...")

        finally:
            with bloqueo:
                estado["bloqueado"] = True
                detener("CIERRE DEL PUENTE")

            cliente.disconnect()
            cliente.loop_stop()
            print("Puerto serial cerrado")


if __name__ == "__main__":
    main()
