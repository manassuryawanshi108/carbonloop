"""
Pydantic Schemas for API requests, responses, and validation in CarbonLoop.
"""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Dict, Any

class UserRegister(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6)
    full_name: str
    organization_name: str
    is_individual: bool = False

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: str
    email: str
    full_name: str
    org_id: str
    org_name: str
    is_synthetic: bool

class ActivityCreate(BaseModel):
    activity_date: str  # YYYY-MM-DD or YYYY-MM
    activity_type: str  # Factor ID e.g. ELEC_IN_GRID
    activity_value: float = Field(ge=0.0)
    activity_unit: str
    data_quality: str = "USER_ENTERED"  # MEASURED, USER_ENTERED, ESTIMATE, SECONDARY, SYNTHETIC
    notes: Optional[str] = None

class ScenarioSimulateRequest(BaseModel):
    solar_share_pct: float = Field(default=0.0, ge=0.0, le=100.0)
    hvac_temp_offset_c: float = Field(default=0.0, ge=0.0, le=4.0)
    transit_shift_pct: float = Field(default=0.0, ge=0.0, le=100.0)
    flight_reduction_pct: float = Field(default=0.0, ge=0.0, le=100.0)
    waste_composting_pct: float = Field(default=0.0, ge=0.0, le=100.0)

class TargetCreate(BaseModel):
    target_name: str
    target_year: int
    target_reduction_pct: float = Field(gt=0.0, le=100.0)
