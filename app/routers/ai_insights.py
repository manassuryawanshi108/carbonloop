"""
Downstream AI Insights Router for CarbonLoop.
Strictly downstream of verified calculations: Verified Results -> AI.
"""

from fastapi import APIRouter, Depends
from app.database import get_db_connection
from app.security import get_current_user_token
from app.carbon_engine.engine import DeterministicCarbonEngine
from app.ai_service import CarbonLoopAIService

router = APIRouter(prefix="/api/ai", tags=["ai"])

@router.post("/narrative")
def get_ai_narrative(token_data: dict = Depends(get_current_user_token)):
    org_id = token_data["org_id"]
    conn = get_db_connection()
    cursor = conn.cursor()

    # Get org profile
    cursor.execute("SELECT name, employee_count, facility_sqft FROM organizations WHERE id = ?", (org_id,))
    org_row = cursor.fetchone()
    org_context = dict(org_row) if org_row else {"name": "Organization", "employee_count": 50}

    # Get calculations
    cursor.execute("""
    SELECT a.id, a.scope, a.category, a.data_quality, c.co2e_kg, c.co2e_tonnes, c.status
    FROM activities a
    JOIN calculations c ON a.id = c.activity_id
    WHERE a.org_id = ?
    """, (org_id,))
    rows = cursor.fetchall()
    conn.close()

    calcs = [dict(r) for r in rows]
    verified_footprint = DeterministicCarbonEngine.aggregate_footprint(calcs)

    # Call AI narrative service
    narrative_result = CarbonLoopAIService.generate_narrative_insights(
        verified_footprint=verified_footprint,
        org_context=org_context
    )

    return narrative_result
