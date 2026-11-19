import threading
import time

import paho.mqtt.client as mqtt

from app.config import settings

_lock = threading.Lock()
_client = None
_state = {
    "mqtt_connected": False,
    "status": "WAITING",
    "updated_at": None,
    "last_request_at": 0.0,
}


def _on_connect(client, userdata, flags, reason_code, properties):
    with _lock:
        _state["mqtt_connected"] = reason_code == 0

    if reason_code == 0:
        client.subscribe("nova_luz/lab/status", qos=1)
        client.publish(
            "nova_luz/lab/command",
            "GET_STATUS",
            qos=1,
            retain=False
        )


def _on_disconnect(client, userdata, flags, reason_code, properties):
    with _lock:
        _state["mqtt_connected"] = False
        _state["status"] = "DISCONNECTED"


def _on_message(client, userdata, msg):
    if msg.topic != "nova_luz/lab/status" or msg.retain:
        return

    with _lock:
        _state["status"] = msg.payload.decode(
            "utf-8", errors="replace"
        ).strip()
        _state["updated_at"] = time.time()
        _state["last_request_at"] = 0.0


def iniciar_monitor():
    global _client

    if _client is not None or not settings.MQTT_ENABLED:
        return

    client = mqtt.Client(
        mqtt.CallbackAPIVersion.VERSION2,
        client_id="nova_luz_web_status"
    )
    client.on_connect = _on_connect
    client.on_disconnect = _on_disconnect
    client.on_message = _on_message

    try:
        client.connect(settings.MQTT_HOST, settings.MQTT_PORT, 30)
        client.loop_start()
        _client = client
    except Exception as error:
        print("Monitor MQTT no disponible:", error)


def obtener_estado():
    with _lock:
        estado = dict(_state)

    if _client is not None and _client.is_connected():
        ahora = time.time()

        with _lock:
            ultimo = _state["updated_at"]
            solicitud = _state["last_request_at"]

            consultar = (
                (ultimo is None or ahora - ultimo > 5)
                and ahora - solicitud > 5
            )

            if consultar:
                _state["last_request_at"] = ahora

        if consultar:
            _client.publish(
                "nova_luz/lab/command",
                "GET_STATUS",
                qos=1,
                retain=False
            )

    return estado
