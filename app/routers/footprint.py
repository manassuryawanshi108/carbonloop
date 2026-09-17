"""
Footprint analytics and KPI router for CarbonLoop.
Delivers verified aggregations, monthly trends, and disclosure KPIs.
"""

from fastapi import APIRouter, Depends
from typing import Dict, Any, List
from collections import defaultdict
from app.database import get_db_connection
from app.security import get_current_user_token
from app.carbon_engine.engine import DeterministicCarbonEngine
from app.carbon_engine.kpis import KPIService

router = APIRouter(prefix="/api/footprint", tags=["footprint"])

@router.get("/summary")
def get_footprint_summary(token_data: dict = Depends(get_current_user_token)):
    org_id = token_data["org_id"]
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT a.id, a.scope, a.category, a.data_quality, c.co2e_kg, c.co2e_tonnes, c.status
    FROM activities a
    JOIN calculations c ON a.id = c.activity_id
    WHERE a.org_id = ?
    """, (org_id,))
    rows = cursor.fetchall()
    conn.close()

    calcs = [dict(r) for r in rows]
    aggregation = DeterministicCarbonEngine.aggregate_footprint(calcs)
    return aggregation

@router.get("/monthly")
def get_monthly_footprint(token_data: dict = Depends(get_current_user_token)):
    org_id = token_data["org_id"]
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT a.activity_date, a.scope, c.co2e_kg
    FROM activities a
    JOIN calculations c ON a.id = c.activity_id
    WHERE a.org_id = ?
    ORDER BY a.activity_date ASC
    """, (org_id,))
    rows = cursor.fetchall()
    conn.close()

    # Aggregate by YYYY-MM
    months_data = defaultdict(lambda: {"Scope 1": 0.0, "Scope 2": 0.0, "Scope 3": 0.0, "total_kg": 0.0})

    for r in rows:
        m = r["activity_date"][:7]  # YYYY-MM
        sc = r["scope"]
        kg = r["co2e_kg"]
        months_data[m][sc] += kg
        months_data[m]["total_kg"] += kg

    result = []
    for m in sorted(months_data.keys()):
        data = months_data[m]
        tot_kg = data["total_kg"]
        result.append({
            "month": m,
            "scope1_kg": round(data["Scope 1"], 2),
            "scope2_kg": round(data["Scope 2"], 2),
            "scope3_kg": round(data["Scope 3"], 2),
            "total_kg": round(tot_kg, 2),
            "total_tonnes": round(tot_kg / 1000.0, 3)
        })

    return result

@router.get("/kpis")
def get_footprint_kpis(token_data: dict = Depends(get_current_user_token)):
    org_id = token_data["org_id"]
    conn = get_db_connection()
    cursor = conn.cursor()

    # Get org metadata
    cursor.execute("SELECT employee_count, facility_sqft, baseline_year FROM organizations WHERE id = ?", (org_id,))
    org = cursor.fetchone()
    emp_count = org["employee_count"] if org else 50
    facility_sqft = org["facility_sqft"] if org else 15000.0
    base_year = org["baseline_year"] if org and "baseline_year" in org.keys() else 2023

    # Get active target
    cursor.execute("SELECT target_reduction_pct, baseline_year FROM targets WHERE org_id = ? AND status = 'ACTIVE' LIMIT 1", (org_id,))
    tgt = cursor.fetchone()
    target_pct = tgt["target_reduction_pct"] if tgt else 30.0

    # Get calculations for all activities
    cursor.execute("""
    SELECT a.id, a.scope, a.category, a.data_quality, c.co2e_kg, c.co2e_tonnes, c.status
    FROM activities a
    JOIN calculations c ON a.id = c.activity_id
    WHERE a.org_id = ?
    """, (org_id,))
    rows = cursor.fetchall()

    # Get baseline year specific total
    cursor.execute("""
    SELECT SUM(c.co2e_kg) as base_kg
    FROM activities a
    JOIN calculations c ON a.id = c.activity_id
    WHERE a.org_id = ? AND a.activity_date LIKE ?
    """, (org_id, f"{base_year}%"))
    base_row = cursor.fetchone()
    base_year_kg = base_row["base_kg"] if base_row and base_row["base_kg"] else None

    conn.close()

    calcs = [dict(r) for r in rows]
    aggregation = DeterministicCarbonEngine.aggregate_footprint(calcs)
    actual_baseline_kg = base_year_kg if base_year_kg is not None else aggregation["total_co2e_kg"]

    kpi_report = KPIService.compute_organization_kpis(
        aggregate_footprint=aggregation,
        employee_count=emp_count,
        facility_sqft=facility_sqft,
        target_pct=target_pct,
        baseline_year_kg=actual_baseline_kg
    )

    return kpi_report
