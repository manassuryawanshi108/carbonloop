"""
Emission Factors public registry router for CarbonLoop.
Provides complete transparency and auditability for all factors.
"""

from fastapi import APIRouter
from app.carbon_engine.factors import list_all_factors, get_factor

router = APIRouter(prefix="/api/factors", tags=["factors"])

@router.get("")
def get_all_factors():
    """Returns the full catalog of verified emission factors with official citations."""
    return list_all_factors()

@router.get("/{factor_id}")
def get_factor_detail(factor_id: str):
    """Returns details for a specific factor."""
    return get_factor(factor_id)
