"""
Reduction Scenarios router for CarbonLoop.
Delivers real-time interactive simulation of decarbonization pathways.
All outputs are strictly tagged SIMULATION/PROJECTION.
"""

from fastapi import APIRouter, HTTPException, Depends
import uuid
from app.database import get_db_connection
from app.models import ScenarioSimulateRequest
from app.security import get_current_user_token
from app.carbon_engine.scenarios import ScenarioEngine

router = APIRouter(prefix="/api/scenarios", tags=["scenarios"])

@router.post("/simulate")
def simulate_scenario(req: ScenarioSimulateRequest, token_data: dict = Depends(get_current_user_token)):
    org_id = token_data["org_id"]
    conn = get_db_connection()
    cursor = conn.cursor()

    # Get annual baseline activities for this org
    cursor.execute("""
    SELECT a.activity_type, SUM(a.activity_value) as total_val, SUM(c.co2e_kg) as total_kg
    FROM activities a
    JOIN calculations c ON a.id = c.activity_id
    WHERE a.org_id = ?
    GROUP BY a.activity_type
    """, (org_id,))
    rows = cursor.fetchall()
    conn.close()

    activity_map = {r["activity_type"]: r["total_val"] for r in rows}
    total_baseline_kg = sum(r["total_kg"] for r in rows) if rows else 176534.49

    baseline_annual = {
        "grid_electricity_kwh": activity_map.get("ELEC_IN_GRID", 168200.0),
        "flight_domestic_pkm": activity_map.get("FLIGHT_DOMESTIC_PKM", 34500.0),
        "commute_car_km": activity_map.get("VEHICLE_CAR_KM", 37500.0),
        "commute_moto_km": activity_map.get("VEHICLE_MOTO_KM", 74800.0),
        "waste_landfill_kg": activity_map.get("WASTE_LANDFILL_KG", 8090.0),
        "total_baseline_kg": total_baseline_kg
    }

    simulation_result = ScenarioEngine.simulate_reduction(
        baseline_annual=baseline_annual,
        solar_share_pct=req.solar_share_pct,
        hvac_temp_offset_c=req.hvac_temp_offset_c,
        transit_shift_pct=req.transit_shift_pct,
        flight_reduction_pct=req.flight_reduction_pct,
        waste_composting_pct=req.waste_composting_pct
    )

    return simulation_result

@router.get("")
def list_scenarios(token_data: dict = Depends(get_current_user_token)):
    org_id = token_data["org_id"]
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT id, name, solar_share_pct, hvac_temp_offset_c, transit_shift_pct, flight_reduction_pct,
           waste_composting_pct, projected_annual_reduction_kg, projected_residual_co2e_kg, classification, created_at
    FROM scenarios
    WHERE org_id = ?
    ORDER BY created_at DESC
    """, (org_id,))
    rows = cursor.fetchall()
    conn.close()

    return [dict(r) for r in rows]
