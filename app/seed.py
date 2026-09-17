"""
Database Seeder for CarbonLoop.
Loads GreenTech Demo Pvt. Ltd. (Mumbai, 50 employees, 12 months full dataset)
Labeled SYNTHETIC DEMONSTRATION DATASET everywhere.
"""

import uuid
from app.database import get_db_connection, init_db
from app.security import hash_password
from app.carbon_engine.engine import DeterministicCarbonEngine

DEMO_ORG_ID = "org-greentech-demo"
DEMO_USER_ID = "user-greentech-demo"

def seed_demo_data():
    init_db()
    conn = get_db_connection()
    cursor = conn.cursor()

    # Check if already seeded
    cursor.execute("SELECT id FROM organizations WHERE id = ?", (DEMO_ORG_ID,))
    if cursor.fetchone():
        conn.close()
        return

    print("Seeding GreenTech Demo Pvt. Ltd. (SYNTHETIC DEMONSTRATION DATASET)...")

    # 1. Organization
    cursor.execute("""
    INSERT INTO organizations (id, name, industry, country, state, employee_count, facility_sqft, baseline_year, is_synthetic)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        DEMO_ORG_ID,
        "GreenTech Demo Pvt. Ltd. (SYNTHETIC DEMO DATASET)",
        "Technology & Light Manufacturing",
        "India",
        "Maharashtra (Mumbai)",
        50,
        15000.0,
        2023,
        1
    ))

    # 2. Demo User
    cursor.execute("""
    INSERT INTO users (id, email, hashed_password, full_name, role, org_id)
    VALUES (?, ?, ?, ?, ?, ?)
    """, (
        DEMO_USER_ID,
        "demo@greentech.in",
        hash_password("demo1234"),
        "Aarav Sharma (Sustainability Lead)",
        "admin",
        DEMO_ORG_ID
    ))

    # 3. 12 Months Activities and Calculations
    months = ["2023-01", "2023-02", "2023-03", "2023-04", "2023-05", "2023-06",
              "2023-07", "2023-08", "2023-09", "2023-10", "2023-11", "2023-12"]

    elec_kwh = [11500, 11800, 13200, 16500, 18200, 17100, 14000, 13500, 13800, 14200, 12600, 11800]
    diesel_l = [120, 110, 140, 260, 310, 240, 180, 160, 150, 140, 130, 120]
    petrol_l = [220, 210, 230, 250, 260, 240, 230, 220, 240, 250, 230, 220]
    lpg_kg = [85, 80, 85, 90, 95, 90, 85, 85, 90, 95, 90, 85]
    commute_bus_pkm = [4500, 4400, 4600, 4500, 4300, 4400, 4500, 4600, 4500, 4600, 4400, 4200]
    commute_rail_pkm = [12500, 12000, 12800, 12400, 11900, 12200, 12500, 12700, 12500, 12800, 12200, 11500]
    commute_moto_km = [6200, 6000, 6400, 6300, 6100, 6200, 6300, 6400, 6300, 6500, 6200, 5900]
    commute_car_km = [3100, 3000, 3200, 3100, 3000, 3100, 3200, 3300, 3200, 3300, 3100, 2900]
    air_dom_pkm = [2300, 0, 4600, 2300, 6900, 2300, 0, 2300, 4600, 2300, 4600, 2300]
    waste_kg = [650, 620, 680, 720, 750, 710, 660, 640, 670, 700, 660, 630]
    water_m3 = [110, 105, 120, 145, 160, 150, 130, 125, 130, 135, 120, 110]

    for i, m in enumerate(months):
        items = [
            ("ELEC_IN_GRID", elec_kwh[i], "kWh", "Main Office Grid Meter (SYNTHETIC DEMO DATA)"),
            ("FUEL_DIESEL_L", diesel_l[i], "L", "Backup DG Set (SYNTHETIC DEMO DATA)"),
            ("FUEL_PETROL_L", petrol_l[i], "L", "Company Service Fleet (SYNTHETIC DEMO DATA)"),
            ("FUEL_LPG_KG", lpg_kg[i], "kg", "Employee Canteen Cylinders (SYNTHETIC DEMO DATA)"),
            ("TRANSIT_BUS_PKM", commute_bus_pkm[i], "pkm", "Employee Commute Transit Bus (SYNTHETIC DEMO DATA)"),
            ("TRANSIT_RAIL_PKM", commute_rail_pkm[i], "pkm", "Employee Commute Mumbai Suburban Rail / Metro (SYNTHETIC DEMO DATA)"),
            ("VEHICLE_MOTO_KM", commute_moto_km[i], "km", "Employee Commute Two-Wheelers (SYNTHETIC DEMO DATA)"),
            ("VEHICLE_CAR_KM", commute_car_km[i], "km", "Employee Commute Solo Cars (SYNTHETIC DEMO DATA)"),
            ("FLIGHT_DOMESTIC_PKM", air_dom_pkm[i], "pkm", "Client On-site Business Travel Flights (SYNTHETIC DEMO DATA)"),
            ("WASTE_LANDFILL_KG", waste_kg[i], "kg", "Commercial Solid Waste to Landfill (SYNTHETIC DEMO DATA)"),
            ("WATER_MAINS_M3", water_m3[i], "m3", "Municipal Mains Water Utility (SYNTHETIC DEMO DATA)")
        ]

        for factor_id, val, unit, note in items:
            if val == 0:
                continue
            act_id = f"act-{m}-{factor_id}"
            # 1. Deterministic Calculation
            calc_res = DeterministicCarbonEngine.calculate_single(
                activity_type=factor_id,
                raw_value=float(val),
                raw_unit=unit,
                data_quality="SYNTHETIC",
                activity_id=act_id
            )

            # 2. Store Activity
            cursor.execute("""
            INSERT INTO activities (id, org_id, user_id, activity_date, scope, category, activity_type, activity_value, activity_unit, data_quality, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                act_id,
                DEMO_ORG_ID,
                DEMO_USER_ID,
                m,
                calc_res["scope"],
                calc_res["category"],
                factor_id,
                val,
                unit,
                "SYNTHETIC",
                note
            ))

            # 3. Store Calculation
            calc_id = f"calc-{act_id}"
            cursor.execute("""
            INSERT INTO calculations (id, activity_id, org_id, factor_id, factor_value, co2e_kg, co2e_tonnes, formula, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                calc_id,
                act_id,
                DEMO_ORG_ID,
                calc_res["factor_id"],
                calc_res["factor_value"],
                calc_res["co2e_kg"],
                calc_res["co2e_tonnes"],
                calc_res["formula"],
                calc_res["status"]
            ))

    # 4. Target Setting
    cursor.execute("""
    INSERT INTO targets (id, org_id, target_name, baseline_year, target_year, target_reduction_pct, target_co2e_kg, status)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        "target-greentech-2030",
        DEMO_ORG_ID,
        "Net-Zero Pathway: 30% Absolute Reduction by 2030 (SYNTHETIC TARGET)",
        2023,
        2030,
        30.0,
        176534.49 * 0.70,
        "ACTIVE"
    ))

    # 5. Pre-configured Decarbonization Scenario
    cursor.execute("""
    INSERT INTO scenarios (id, org_id, name, solar_share_pct, hvac_temp_offset_c, transit_shift_pct, flight_reduction_pct, waste_composting_pct, projected_annual_reduction_kg, projected_residual_co2e_kg, classification)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        "scenario-greentech-primary",
        DEMO_ORG_ID,
        "Composite Decarbonization Plan 2026 (Rooftop Solar + HVAC + Metro Commute)",
        40.0,  # 40% Solar
        2.0,   # +2 deg C HVAC
        30.0,  # 30% Transit shift
        25.0,  # 25% Flight reduction
        50.0,  # 50% Composting
        58450.0,
        118084.49,
        "SIMULATION/PROJECTION"
    ))

    conn.commit()
    conn.close()
    print("GreenTech Demo Pvt. Ltd. successfully loaded.")

if __name__ == "__main__":
    seed_demo_data()
