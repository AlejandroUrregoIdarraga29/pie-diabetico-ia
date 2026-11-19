import paho.mqtt.publish as publish
from app.config import settings


def publicar_prueba(accion: str) -> dict:
    """Publica eventos de simulación, nunca órdenes al hardware."""

    if accion not in ("START_SIMULATION", "STOP_SIMULATION"):
        raise ValueError("Acción de simulación no permitida")

    if not settings.MQTT_ENABLED or settings.USE_MOCKS:
        print(f"[NOVA LUZ MOCK] {accion}")
        return {
            "mode": "SIMULATION",
            "action": accion,
            "published": False
        }

    publish.single(
        topic="nova_luz/simulation/event",
        payload=accion,
        hostname=settings.MQTT_HOST,
        port=settings.MQTT_PORT,
        qos=1,
        retain=False
    )

    return {
        "mode": "MQTT_SIMULATION",
        "action": accion,
        "published": True
    }
