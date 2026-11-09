from fastapi import FastAPI, UploadFile, File, Form, HTTPException
import uuid
from datetime import datetime
from app.config import settings
from app.models.schemas import SessionResponse, DecisionCreate
from app.services.interfaces import MockSegmenter, MockCommandEmitter

app = FastAPI(title="Pie Diabético IA - API Web", version="1.0.0")

segmenter = MockSegmenter()
emitter = MockCommandEmitter()
sessions_db = {}

@app.post("/api/v1/sessions/", response_model=SessionResponse)
async def create_session(
    patient_code: str = Form(...),
    file: UploadFile = File(...)
):
    contents = await file.read()
    mask, area_px = segmenter.predict(contents)
    session_id = f"SES-{uuid.uuid4().hex[:8].upper()}"
    
    session_data = {
        "session_id": session_id,
        "patient_code": patient_code,
        "created_at": datetime.now(),
        "area_pixels": area_px,
        "status": "PENDING",
        "decision": None
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