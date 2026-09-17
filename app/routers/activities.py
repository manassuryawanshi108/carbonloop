"""
Activities and Traceability router for CarbonLoop.
Every activity entry triggers deterministic calculation and records full audit metadata.
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
import uuid
from app.database import get_db_connection
from app.models import ActivityCreate
from app.security import get_current_user_token
from app.carbon_engine.engine import DeterministicCarbonEngine
from app.carbon_engine.factors import get_factor

router = APIRouter(prefix="/api/activities", tags=["activities"])

@router.post("")
def create_activity(req: ActivityCreate, token_data: dict = Depends(get_current_user_token)):
    org_id = token_data["org_id"]
    user_id = token_data["sub"]

    act_id = f"act-{uuid.uuid4().hex[:10]}"
    calc_id = f"calc-{act_id}"

    # 1. Deterministic Calculation
    try:
        calc_result = DeterministicCarbonEngine.calculate_single(
            activity_type=req.activity_type,
            raw_value=req.activity_value,
            raw_unit=req.activity_unit,
            data_quality=req.data_quality,
            activity_id=act_id
        )
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except KeyError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # 2. Database Insert
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO activities (id, org_id, user_id, activity_date, scope, category, activity_type, activity_value, activity_unit, data_quality, notes)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        act_id,
        org_id,
        user_id,
        req.activity_date,
        calc_result["scope"],
        calc_result["category"],
        req.activity_type,
        req.activity_value,
        req.activity_unit,
        req.data_quality,
        req.notes
    ))

    cursor.execute("""
    INSERT INTO calculations (id, activity_id, org_id, factor_id, factor_value, co2e_kg, co2e_tonnes, formula, status)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        calc_id,
        act_id,
        org_id,
        calc_result["factor_id"],
        calc_result["factor_value"],
        calc_result["co2e_kg"],
        calc_result["co2e_tonnes"],
        calc_result["formula"],
        calc_result["status"]
    ))

    # Audit log
    cursor.execute("""
    INSERT INTO audit_logs (id, org_id, user_id, action, entity_type, entity_id, details)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        f"audit-{uuid.uuid4().hex[:8]}",
        org_id,
        user_id,
        "CREATE_ACTIVITY",
        "activity",
        act_id,
        f"Created {req.activity_type} ({req.activity_value} {req.activity_unit}) => {calc_result['co2e_kg']} kg CO2e"
    ))

    conn.commit()
    conn.close()

    return {
        "success": True,
        "activity_id": act_id,
        "calculation": calc_result
    }

@router.get("")
def list_activities(
    scope: Optional[str] = None,
    month: Optional[str] = None,
    search: Optional[str] = None,
    limit: int = 500,
    token_data: dict = Depends(get_current_user_token)
):
    org_id = token_data["org_id"]
    conn = get_db_connection()
    cursor = conn.cursor()

    query = """
    SELECT a.id, a.activity_date, a.scope, a.category, a.activity_type, a.activity_value, a.activity_unit,
           a.data_quality, a.notes, a.created_at,
           c.factor_id, c.factor_value, c.co2e_kg, c.co2e_tonnes, c.formula, c.status
    FROM activities a
    JOIN calculations c ON a.id = c.activity_id
    WHERE a.org_id = ?
    """
    params = [org_id]

    if scope:
        query += " AND a.scope = ?"
        params.append(scope)
    if month:
        query += " AND a.activity_date LIKE ?"
        params.append(f"{month}%")
    if search:
        query += " AND (a.activity_type LIKE ? OR a.category LIKE ? OR a.notes LIKE ? OR a.activity_date LIKE ?)"
        term = f"%{search.strip()}%"
        params.extend([term, term, term, term])

    query += " ORDER BY a.activity_date DESC, a.created_at DESC LIMIT ?"
    params.append(limit)

    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()

    return [dict(r) for r in rows]

@router.get("/{activity_id}/trace")
def trace_calculation(activity_id: str, token_data: dict = Depends(get_current_user_token)):
    """
    Click-to-Trace Audit Modal Endpoint.
    Returns complete scientific provenance: Input -> Normalized -> Factor -> Authority -> Formula -> Output.
    """
    org_id = token_data["org_id"]
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT a.id, a.activity_date, a.scope, a.category, a.activity_type, a.activity_value, a.activity_unit,
           a.data_quality, a.notes, a.created_at,
           c.factor_id, c.factor_value, c.co2e_kg, c.co2e_tonnes, c.formula, c.status, c.calculated_at
    FROM activities a
    JOIN calculations c ON a.id = c.activity_id
    WHERE a.id = ? AND a.org_id = ?
    """, (activity_id, org_id))
    row = cursor.fetchone()
    conn.close()

    if not row:
        raise HTTPException(status_code=404, detail="Activity record not found")

    item = dict(row)
    factor_meta = get_factor(item["activity_type"])

    return {
        "activity_id": item["id"],
        "activity_date": item["activity_date"],
        "scope": item["scope"],
        "category": item["category"],
        "raw_input": {
            "value": item["activity_value"],
            "unit": item["activity_unit"],
            "data_quality": item["data_quality"],
            "notes": item["notes"]
        },
        "emission_factor": {
            "factor_id": factor_meta["factor_id"],
            "name": factor_meta["name"],
            "value": factor_meta["value"],
            "unit": factor_meta["unit"],
            "geography": factor_meta["geography"],
            "year": factor_meta["year"],
            "source": factor_meta["source"],
            "source_url": factor_meta["source_url"],
            "methodology": factor_meta["methodology"],
            "confidence": factor_meta["confidence"],
            "version": factor_meta.get("version", "2024")
        },
        "calculation_result": {
            "co2e_kg": item["co2e_kg"],
            "co2e_tonnes": item["co2e_tonnes"],
            "formula": item["formula"],
            "status": item["status"],
            "calculated_at": item["calculated_at"]
        },
        "audit_trail": {
            "iso_14064_aligned": True,
            "ghg_protocol_aligned": True,
            "sebi_brsr_ready": True
        }
    }
