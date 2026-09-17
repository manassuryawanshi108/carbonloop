"""
Automated Live End-to-End Verification of Demo Flow.
Executes every step of Step 14 over HTTP against the running CarbonLoop server:
Create/Login -> Enter Activity -> Calculate Footprint -> Scope Breakdown -> Hotspot -> AI Insight -> Reduction Scenario -> Target -> Progress -> Traceability.
"""

import requests
import sys

BASE_URL = "http://127.0.0.1:8000"

def test_full_demo_flow():
    print("=== STARTING LIVE END-TO-END DEMO FLOW VERIFICATION ===")

    # 1. Login
    print("\n--- STEP 1: Login with Demo User ---")
    login_res = requests.post(f"{BASE_URL}/api/auth/login", json={
        "email": "demo@greentech.in",
        "password": "demo1234"
    })
    assert login_res.status_code == 200, f"Login failed: {login_res.text}"
    token_data = login_res.json()
    token = token_data["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print(f"Logged in as: {token_data['full_name']} ({token_data['org_name']})")
    assert token_data["is_synthetic"] is True, "GreenTech Demo must be marked synthetic"

    # 2. Enter Activity Data
    print("\n--- STEP 2: Enter Activity Data (New Grid Electricity Meter Reading) ---")
    act_res = requests.post(f"{BASE_URL}/api/activities", headers=headers, json={
        "activity_date": "2024-01",
        "activity_type": "ELEC_IN_GRID",
        "activity_value": 15000.0,
        "activity_unit": "kWh",
        "data_quality": "MEASURED",
        "notes": "Adani Electricity Bill Mumbai #INV-2024-001"
    })
    assert act_res.status_code == 200, f"Activity entry failed: {act_res.text}"
    act_data = act_res.json()
    new_act_id = act_data["activity_id"]
    calc = act_data["calculation"]
    print(f"Created Activity ID: {new_act_id}")
    print(f"Deterministic Result: {calc['co2e_kg']} kg CO2e ({calc['co2e_tonnes']} t CO2e)")
    print(f"Formula: {calc['formula']}")
    assert abs(calc["co2e_kg"] - (15000 * 0.727492658)) < 0.01

    # 3. Calculate Footprint
    print("\n--- STEP 3: Calculate Total Footprint ---")
    summary_res = requests.get(f"{BASE_URL}/api/footprint/summary", headers=headers)
    assert summary_res.status_code == 200
    summary = summary_res.json()
    print(f"Total Gross Footprint: {summary['total_co2e_tonnes']} t CO2e ({summary['total_co2e_kg']} kg CO2e)")

    # 4. View Scope Breakdown
    print("\n--- STEP 4: View Scope Breakdown ---")
    scopes = summary["scopes"]
    for sc, d in scopes.items():
        print(f"  {sc}: {d['co2e_tonnes']} t CO2e ({d['percentage']}%)")
    assert "Scope 1" in scopes and "Scope 2" in scopes and "Scope 3" in scopes

    # 5. Identify Hotspot
    print("\n--- STEP 5: Identify Dominant Hotspot ---")
    dominant = summary["dominant_hotspot"]
    assert dominant is not None
    print(f"Primary Hotspot Identified: '{dominant['category']}' ({dominant['percentage']}% of emissions, {dominant['co2e_tonnes']} t CO2e)")
    assert dominant["percentage"] > 50.0, "Electricity should dominate in GreenTech"

    # 6. Generate AI Insight
    print("\n--- STEP 6: Generate AI Narrative & Action Roadmap ---")
    ai_res = requests.post(f"{BASE_URL}/api/ai/narrative", headers=headers)
    assert ai_res.status_code == 200
    ai_data = ai_res.json()
    print(f"AI Narrative Source: {ai_data['source']}")
    print(f"Executive Summary:\n  {ai_data['executive_summary'][:150]}...")
    print(f"Hotspot Analysis:\n  {ai_data['hotspot_analysis'][:150]}...")
    print(f"Recommended Actions: {len(ai_data['recommended_actions'])} concrete steps generated.")
    for idx, act in enumerate(ai_data["recommended_actions"][:2]):
        print(f"  [{idx+1}] {act['title']} ({act['impact_scope']}, {act['timeframe']})")

    # 7. Run Reduction Scenario
    print("\n--- STEP 7: Run Reduction Scenario Simulation ---")
    scenario_res = requests.post(f"{BASE_URL}/api/scenarios/simulate", headers=headers, json={
        "solar_share_pct": 40.0,
        "hvac_temp_offset_c": 2.0,
        "transit_shift_pct": 30.0,
        "flight_reduction_pct": 25.0,
        "waste_composting_pct": 50.0
    })
    assert scenario_res.status_code == 200
    sim = scenario_res.json()
    assert sim["classification"] == "SIMULATION/PROJECTION"
    print(f"Classification: {sim['classification']}")
    print(f"Baseline: {sim['baseline_total_tonnes']} t CO2e")
    print(f"Projected Avoided: -{sim['total_projected_reduction_tonnes']} t CO2e (-{sim['projected_reduction_pct']}%)")
    print(f"Projected Residual: {sim['projected_residual_tonnes']} t CO2e")

    # 8. Set Target
    print("\n--- STEP 8: Set Decarbonization Target ---")
    target_res = requests.post(f"{BASE_URL}/api/targets", headers=headers, json={
        "target_name": "SBTi Net-Zero 2030 Commitment",
        "target_year": 2030,
        "target_reduction_pct": 30.0
    })
    assert target_res.status_code == 200
    tgt_info = target_res.json()
    print(f"Target Created: {tgt_info['target_id']} (30% reduction by 2030, ceiling: {tgt_info['target_co2e_kg']} kg)")

    # 9. View Progress
    print("\n--- STEP 9: View Target Distance & Progress ---")
    targets_list_res = requests.get(f"{BASE_URL}/api/targets", headers=headers)
    assert targets_list_res.status_code == 200
    targets = targets_list_res.json()
    print(f"Active Targets: {len(targets)}")
    for t in targets:
        print(f"  Target: {t['target_name']} | Progress: {t['progress_pct']}% | Target Year: {t['target_year']}")

    # 10. Click-to-Trace Provenance
    print("\n--- STEP 10: Click-to-Trace Audit Provenance ---")
    trace_res = requests.get(f"{BASE_URL}/api/activities/{new_act_id}/trace", headers=headers)
    assert trace_res.status_code == 200
    trace = trace_res.json()
    print(f"Activity Input: {trace['raw_input']['value']} {trace['raw_input']['unit']}")
    print(f"Factor ID: {trace['emission_factor']['factor_id']} = {trace['emission_factor']['value']} kg CO2e/{trace['emission_factor']['unit']}")
    print(f"Authority Source: {trace['emission_factor']['source']}")
    print(f"Official URL: {trace['emission_factor']['source_url']}")
    print(f"Formula: {trace['calculation_result']['formula']}")
    print(f"Audit Status: {trace['audit_trail']}")

    print("\n=== ALL 10 STEPS OF LIVE DEMO FLOW COMPLETED SUCCESSFULLY ===")

if __name__ == "__main__":
    test_full_demo_flow()
