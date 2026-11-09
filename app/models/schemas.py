from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class SessionCreate(BaseModel):
    patient_code: str

class DecisionCreate(BaseModel):
    decision: str  # "APPROVED" o "REJECTED"
    threshold: Optional[float] = 0.5
    notes: Optional[str] = None

class SessionResponse(BaseModel):
    session_id: str
    patient_code: str
    created_at: datetime
    area_pixels: int
    status: str
    decision: Optional[str] = None