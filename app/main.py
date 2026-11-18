from fastapi import FastAPI, UploadFile, File, Form, HTTPException
import uuid
from datetime import datetime
from app.config import settings
from app.models.schemas import SessionResponse, DecisionCreate, ClinicalAssessment
from app.services.interfaces import MockSegmenter, MockCommandEmitter
from app.services.litert_segmentation import LiteRTSegmentationService
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os
import subprocess
import shutil
from fastapi.responses import Response


app = FastAPI(title="Pie Diabético IA - API Web", version="1.0.0")

segmenter = (
    MockSegmenter()
    if settings.USE_MOCKS
    else LiteRTSegmentationService(settings.MODEL_PATH)
)

# El hardware permanece simulado por seguridad.
emitter = MockCommandEmitter()
sessions_db = {}

@app.get("/api/v1/camera/capture")
def capture_camera():
    camera_program = shutil.which("rpicam-still")

    if camera_program is None:
        raise HTTPException(
            status_code=503,
            detail="Cámara no disponible en este equipo."
        )

    try:
        result = subprocess.run(
            [
                camera_program,
                "--nopreview",
                "--timeout", "1000",
                "--width", "1640",
                "--height", "1232",
                "--output", "-"
            ],
            capture_output=True,
            timeout=15,
            check=True
        )

        if not result.stdout.startswith(b"\xff\xd8"):
            raise RuntimeError("La captura no devolvió una imagen JPEG.")

        return Response(
            content=result.stdout,
            media_type="image/jpeg",
            headers={"Cache-Control": "no-store"}
        )

    except (subprocess.SubprocessError, RuntimeError) as exc:
        raise HTTPException(
            status_code=503,
            detail=f"No se pudo capturar la fotografía: {exc}"
        )

@app.post("/api/v1/sessions/", response_model=SessionResponse)
async def create_session(
    patient_code: str = Form(...),
    file: UploadFile = File(...)
):
    contents = await file.read()
    mask, area_px, overlay_b64 = segmenter.predict(contents)
    session_id = f"SES-{uuid.uuid4().hex[:8].upper()}"
    
    session_data = {
        "session_id": session_id,
        "patient_code": patient_code,
        "created_at": datetime.now(),
        "area_pixels": area_px,
        "status": "PENDING",
        "decision": None,
        "overlay_image": overlay_b64
    }
    sessions_db[session_id] = session_data
    return session_data

@app.get("/api/v1/sessions/{session_id}", response_model=SessionResponse)
def get_session(session_id: str):
    if session_id not in sessions_db:
        raise HTTPException(status_code=404, detail="Sesión no encontrada")
    return sessions_db[session_id]

@app.post("/api/v1/sessions/{session_id}/decision")
def record_decision(session_id: str, decision: DecisionCreate):
    if session_id not in sessions_db:
        raise HTTPException(status_code=404, detail="Sesión no encontrada")
    
    sessions_db[session_id]["status"] = "COMPLETED"
    sessions_db[session_id]["decision"] = decision.decision
    
    if decision.decision == "APPROVED":
        emitter.send_command("START_TREATMENT")
    else:
        emitter.send_command("CANCEL_TREATMENT")
        
    return {"message": "Decisión registrada correctamente", "session_id": session_id}

@app.get("/api/v1/system/status")
def system_status():
    return {
        "env_mode": settings.ENV_MODE,
        "use_mocks": settings.USE_MOCKS,
        "system": "ONLINE"
    }
    
# Montar archivos estáticos
app.mount("/static", StaticFiles(directory="app/static"), name="static")

@app.get("/")
def serve_index():
    return FileResponse("app/templates/index.html")


@app.put("/api/v1/sessions/{session_id}/assessment")
def save_clinical_assessment(
    session_id: str,
    assessment: ClinicalAssessment
):
    if session_id not in sessions_db:
        raise HTTPException(
            status_code=404,
            detail="Sesión no encontrada"
        )

    sessions_db[session_id]["clinical_assessment"] = assessment.model_dump()

    return {
        "message": "Valoración clínica registrada correctamente",
        "session_id": session_id,
        "clinical_assessment": sessions_db[session_id]["clinical_assessment"]
    }


@app.get("/api/v1/sessions/{session_id}/assessment")
def get_clinical_assessment(session_id: str):
    if session_id not in sessions_db:
        raise HTTPException(
            status_code=404,
            detail="Sesión no encontrada"
        )

    assessment = sessions_db[session_id].get("clinical_assessment")

    if assessment is None:
        raise HTTPException(
            status_code=404,
            detail="La sesión todavía no tiene valoración clínica"
        )

    return {
        "session_id": session_id,
        "clinical_assessment": assessment
    }


# NOVA LUZ - API DE SIMULACION DE PULSOS
# Exclusivamente simulación; no permite activar hardware.
from typing import Literal
from pydantic import BaseModel
from app.services.mqtt_service import publicar_prueba

class PulseSimulationRequest(BaseModel):
    action: Literal["START_SIMULATION", "STOP_SIMULATION"]

@app.post("/api/v1/pulse/simulation")
def pulse_simulation(request: PulseSimulationRequest):
    resultado = publicar_prueba(request.action)
    return {
        "message": "Acción de simulación procesada",
        **resultado
    }


# NOVA_LUZ_LAB_WEB_INTEGRATION
import os
import hmac
import paho.mqtt.publish as lab_publish
from fastapi import HTTPException
from pydantic import BaseModel as LabBaseModel

class LabWebCommand(LabBaseModel):
    action: str
    pin: str = ""

@app.post("/api/v1/pulse/lab")
def controlar_laboratorio(request: LabWebCommand):
    if request.action not in ("START_LAB", "STOP_LAB"):
        raise HTTPException(status_code=400, detail="Acción inválida")

    if request.action == "START_LAB":
        habilitado = os.getenv("LAB_WEB_ENABLED") == "true"
        pin = os.getenv("LAB_WEB_PIN", "")
        token = os.getenv("LAB_TOKEN", "")

        if not habilitado or not pin or not token:
            raise HTTPException(
                status_code=403,
                detail="Laboratorio web deshabilitado"
            )

        if not hmac.compare_digest(request.pin, pin):
            raise HTTPException(
                status_code=403,
                detail="PIN incorrecto"
            )

        mensaje = "START_LAB:" + token
    else:
        mensaje = "STOP_LAB"

    try:
        lab_publish.single(
            topic="nova_luz/lab/command",
            payload=mensaje,
            hostname="192.168.1.53",
            port=1883,
            qos=1,
            retain=False
        )
    except Exception as error:
        raise HTTPException(
            status_code=503,
            detail="No se pudo enviar la orden MQTT"
        ) from error

    return {
        "ok": True,
        "action": request.action,
        "message": "Orden MQTT enviada; confirmar en el puente"
    }
