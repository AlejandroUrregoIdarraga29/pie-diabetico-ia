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
    overlay_image: Optional[str] = None

class ClinicalAssessment(BaseModel):
    # Historia del paciente
    age: Optional[int] = None
    comorbidities: Optional[str] = None
    nutritional_status: Optional[str] = None
    immunosuppressive_treatment: Optional[bool] = None
    stress_level: Optional[str] = None
    treatment_adherence: Optional[str] = None

    # Evaluación vascular y neurológica
    sensitivity: Optional[str] = None
    circulation: Optional[str] = None
    local_temperature_c: Optional[float] = None
    pain_level: Optional[int] = None

    # Características de la herida
    wound_location: Optional[str] = None
    wound_length_mm: Optional[float] = None
    wound_width_mm: Optional[float] = None
    wound_depth_mm: Optional[float] = None
    wound_bed: Optional[str] = None
    wound_edges: Optional[str] = None
    necrosis: Optional[bool] = None
    surrounding_redness: Optional[bool] = None
    maceration: Optional[bool] = None

    # Exudación
    exudate_amount: Optional[str] = None
    exudate_type: Optional[str] = None
    exudate_color: Optional[str] = None
    exudate_consistency: Optional[str] = None
    odor: Optional[str] = None

    # Valoración y seguimiento
    infection_signs: Optional[str] = None
    wound_classification: Optional[str] = None
    treatment_duration_days: Optional[int] = None
    treatment_cost: Optional[float] = None
    clinical_notes: Optional[str] = None
