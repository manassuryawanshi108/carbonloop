"""
Decarbonization Targets router for CarbonLoop.
"""

from fastapi import APIRouter, HTTPException, Depends
import uuid
from app.database import get_db_connection
from app.models import TargetCreate
from app.security import get_current_user_token

router = APIRouter(prefix="/api/targets", tags=["targets"])

@router.get("")
def list_targets(token_data: dict = Depends(get_current_user_token)):
    org_id = token_data["org_id"]
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT t.id, t.target_name, t.baseline_year, t.target_year, t.target_reduction_pct, t.target_co2e_kg, t.status, t.created_at,
           o.baseline_year as org_base_year
    FROM targets t
    JOIN organizations o ON t.org_id = o.id
    WHERE t.org_id = ?
    ORDER BY t.created_at DESC
    """, (org_id,))
    rows = cursor.fetchall()

    # Get current total footprint
    cursor.execute("""
    SELECT SUM(c.co2e_kg) as current_kg
    FROM calculations c
    WHERE c.org_id = ?
    """, (org_id,))
    cur_row = cursor.fetchone()
    current_kg = cur_row["current_kg"] or 0.0
    conn.close()

    targets = []
    for r in rows:
        target_dict = dict(r)
        # Progress calculation
        base_kg = target_dict["target_co2e_kg"] / (1.0 - (target_dict["target_reduction_pct"] / 100.0))
        actual_reduction_kg = max(0.0, base_kg - current_kg)
        target_reduction_kg = base_kg - target_dict["target_co2e_kg"]
        progress = (actual_reduction_kg / target_reduction_kg * 100.0) if target_reduction_kg > 0 else 0.0

        target_dict["current_footprint_kg"] = round(current_kg, 2)
        target_dict["progress_pct"] = round(min(progress, 100.0), 1)
        targets.append(target_dict)

    return targets

@router.post("")
def create_target(req: TargetCreate, token_data: dict = Depends(get_current_user_token)):
    org_id = token_data["org_id"]
    conn = get_db_connection()
    cursor = conn.cursor()

    # Get current total footprint
    cursor.execute("SELECT SUM(co2e_kg) as total_kg FROM calculations WHERE org_id = ?", (org_id,))
    row = cursor.fetchone()
    current_kg = (row["total_kg"] if row and row["total_kg"] is not None else 176534.49)

    target_co2e_kg = current_kg * (1.0 - (req.target_reduction_pct / 100.0))
    target_id = f"target-{uuid.uuid4().hex[:8]}"

    cursor.execute("""
    INSERT INTO targets (id, org_id, target_name, baseline_year, target_year, target_reduction_pct, target_co2e_kg, status)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        target_id,
        org_id,
        req.target_name,
        2023,
        req.target_year,
        req.target_reduction_pct,
        target_co2e_kg,
        "ACTIVE"
    ))

    conn.commit()
    conn.close()

    return {
        "success": True,
        "target_id": target_id,
        "target_co2e_kg": round(target_co2e_kg, 2),
        "target_reduction_pct": req.target_reduction_pct
    }
