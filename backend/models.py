from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

# --- Pydantic Schemas for API Requests & Responses ---

class ProductVariant(BaseModel):
    product_id: str
    product_variant: str
    product_family: str
    target_temperature: float
    min_temperature: float
    max_temperature: float
    target_pressure: float
    min_pressure: float
    max_pressure: float

class ValidationRequest(BaseModel):
    product_variant: str
    temperature: float
    pressure: float

class ValidationResponse(BaseModel):
    product_variant: str
    temperature: float
    pressure: float
    temp_valid: bool
    pressure_valid: bool
    interaction_valid: bool
    interaction_score: float
    status: str  # VALID, WARNING, BLOCKED
    reason: str
    temp_deviation: float
    pressure_deviation: float

class SetupStepItem(BaseModel):
    step_id: int
    step_name: str
    step_completed: bool
    timestamp: str
    duration_seconds: int
    notes: Optional[str] = ""

class SetupCreateRequest(BaseModel):
    setup_id: Optional[str] = None
    batch_id: str
    product_variant: str
    operator_id: str
    operator_experience_level: str
    machine_id: str
    shift: str
    is_prototype: bool = True
    temperature: float
    pressure: float
    heating_time: float
    stabilization_time: float
    steps: List[SetupStepItem]

class FirstPieceInspectionRequest(BaseModel):
    setup_id: str
    dimensional_quality: float  # mm deviation or score
    surface_quality: float      # score 1-10
    weight: float               # grams
    color_appearance: str       # Normal, Discolored, Scratched
    defect_detected: bool
    defect_type: Optional[str] = "None" # dimensional_variation, surface_defect, weight_variation, incomplete_formation, discoloration, interaction_stress_defect, none
    inspector_comment: Optional[str] = ""

class SetupRecordResponse(BaseModel):
    setup_id: str
    batch_id: str
    product_variant: str
    operator_id: str
    machine_id: str
    start_time: str
    end_time: str
    setup_time_minutes: float
    temperature: float
    pressure: float
    validation_status: str
    is_prototype: bool
    first_piece_pass: Optional[bool] = None
    defect_type: Optional[str] = None
    rework_required: Optional[bool] = False
    material_waste_kg: Optional[float] = 0.0
    maintenance_flag: Optional[bool] = False

class RecommendationResponse(BaseModel):
    product_variant: str
    recommended_temperature: float
    recommended_pressure: float
    sample_size: int
    historical_pass_rate: float
    min_safe_temp: float
    max_safe_temp: float
    min_safe_pressure: float
    max_safe_pressure: float
    confidence_level: str
    disclaimer: str

class SyncPayload(BaseModel):
    setups: List[SetupCreateRequest]
    inspections: List[FirstPieceInspectionRequest]
