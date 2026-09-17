"""
Automated Test Suite for CarbonLoop Deterministic Engine.
Executes the 10 Hand-Computed Benchmark Cases specified in Phase 1 Research Gate.
"""

import pytest
import math
from app.carbon_engine.engine import DeterministicCarbonEngine
from app.carbon_engine.scenarios import ScenarioEngine

TOLERANCE = 0.01  # Tolerance within 0.01 kg CO2e

def test_case_01_electricity_cea():
    """
    Test Case 1: Electricity Consumption (Scope 2 Location-based, CEA v20.0)
    12,500 kWh in Mumbai, India.
    Expected: 9,093.658 kg CO2e
    """
    result = DeterministicCarbonEngine.calculate_single(
        activity_type="ELEC_IN_GRID",
        raw_value=12500.0,
        raw_unit="kWh"
    )
    assert result["status"] == "CALCULATED"
    assert result["scope"] == "Scope 2"
    expected = 9093.658225
    assert math.isclose(result["co2e_kg"], expected, abs_tol=TOLERANCE)
    assert math.isclose(result["co2e_tonnes"], expected / 1000.0, abs_tol=1e-4)
    assert "0.727493" in result["formula"] or "0.72749" in result["formula"]

def test_case_02_diesel_generator():
    """
    Test Case 2: Stationary Diesel Generator (Scope 1, DESNZ 2024)
    450 Litres of diesel fuel.
    Expected: 1,130.535 kg CO2e
    """
    result = DeterministicCarbonEngine.calculate_single(
        activity_type="FUEL_DIESEL_L",
        raw_value=450.0,
        raw_unit="L"
    )
    assert result["status"] == "CALCULATED"
    assert result["scope"] == "Scope 1"
    expected = 1130.535000
    assert math.isclose(result["co2e_kg"], expected, abs_tol=TOLERANCE)

def test_case_03_petrol_vehicle():
    """
    Test Case 3: Company Petrol Fleet Vehicle (Scope 1, DESNZ 2024)
    320 Litres of petrol fuel.
    Expected: 667.046 kg CO2e
    """
    result = DeterministicCarbonEngine.calculate_single(
        activity_type="FUEL_PETROL_L",
        raw_value=320.0,
        raw_unit="L"
    )
    assert result["status"] == "CALCULATED"
    assert result["scope"] == "Scope 1"
    expected = 667.046400
    assert math.isclose(result["co2e_kg"], expected, abs_tol=TOLERANCE)

def test_case_04_lpg_canteen():
    """
    Test Case 4: Canteen Commercial LPG (Scope 1, DESNZ 2024)
    190 kg LPG fuel.
    Expected: 558.479 kg CO2e
    """
    result = DeterministicCarbonEngine.calculate_single(
        activity_type="FUEL_LPG_KG",
        raw_value=190.0,
        raw_unit="kg"
    )
    assert result["status"] == "CALCULATED"
    assert result["scope"] == "Scope 1"
    expected = 558.478581
    assert math.isclose(result["co2e_kg"], expected, abs_tol=TOLERANCE)

def test_case_05_bus_commute():
    """
    Test Case 5: Employee Commuting by Local Transit Bus (Scope 3, Cat 7, DESNZ 2024)
    8,400 passenger-km on local municipal bus.
    Expected: 911.064 kg CO2e
    """
    result = DeterministicCarbonEngine.calculate_single(
        activity_type="TRANSIT_BUS_PKM",
        raw_value=8400.0,
        raw_unit="pkm"
    )
    assert result["status"] == "CALCULATED"
    assert result["scope"] == "Scope 3"
    assert "Category 7" in result["category"]
    expected = 911.064000
    assert math.isclose(result["co2e_kg"], expected, abs_tol=TOLERANCE)

def test_case_06_domestic_flight():
    """
    Test Case 6: Business Travel Domestic Air Flight (Scope 3, Cat 6, DESNZ 2024 with RF)
    9,200 passenger-km.
    Expected: 2,507.644 kg CO2e
    """
    result = DeterministicCarbonEngine.calculate_single(
        activity_type="FLIGHT_DOMESTIC_PKM",
        raw_value=9200.0,
        raw_unit="pkm"
    )
    assert result["status"] == "CALCULATED"
    assert result["scope"] == "Scope 3"
    assert "Category 6" in result["category"]
    expected = 2507.644000
    assert math.isclose(result["co2e_kg"], expected, abs_tol=TOLERANCE)

def test_case_07_waste_landfill():
    """
    Test Case 7: Operational Waste to Landfill (Scope 3, Cat 5, DESNZ 2024)
    1,500 kg (1.5 tonnes) commercial waste to municipal landfill.
    Expected: 780.501 kg CO2e
    """
    result = DeterministicCarbonEngine.calculate_single(
        activity_type="WASTE_LANDFILL_KG",
        raw_value=1500.0,
        raw_unit="kg"
    )
    assert result["status"] == "CALCULATED"
    assert result["scope"] == "Scope 3"
    assert "Category 5" in result["category"]
    expected = 780.501300
    assert math.isclose(result["co2e_kg"], expected, abs_tol=TOLERANCE)

def test_case_08_water_mains():
    """
    Test Case 8: Municipal Water Supply & Wastewater Treatment (Scope 3, DESNZ 2024)
    250 m3 water supply and wastewater discharge.
    Expected: 84.713 kg CO2e
    """
    result = DeterministicCarbonEngine.calculate_single(
        activity_type="WATER_MAINS_M3",
        raw_value=250.0,
        raw_unit="m3"
    )
    assert result["status"] == "CALCULATED"
    assert result["scope"] == "Scope 3"
    expected = 84.712500
    assert math.isclose(result["co2e_kg"], expected, abs_tol=TOLERANCE)

def test_case_09_reduction_scenario_solar():
    """
    Test Case 9: Decarbonization Scenario Projection (Solar PV Displacement)
    Baseline: 10,000 kWh/month grid electricity = 7,274.927 kg CO2e
    40% solar PV substitution (4,000 kWh displaced).
    Expected Monthly Reduction: 2,909.971 kg CO2e (40.00%)
    """
    base_calc = DeterministicCarbonEngine.calculate_single(
        activity_type="ELEC_IN_GRID",
        raw_value=10000.0,
        raw_unit="kWh"
    )
    baseline_elec_kg = base_calc["co2e_kg"]
    assert math.isclose(baseline_elec_kg, 7274.92658, abs_tol=TOLERANCE)

    # 40% displacement
    sim_res = ScenarioEngine.simulate_reduction(
        baseline_annual={"grid_electricity_kwh": 10000.0, "total_baseline_kg": baseline_elec_kg},
        solar_share_pct=40.0
    )
    assert sim_res["classification"] == "SIMULATION/PROJECTION"
    assert math.isclose(sim_res["total_projected_reduction_kg"], 2909.970632, abs_tol=TOLERANCE)
    assert math.isclose(sim_res["projected_residual_kg"], 4364.955948, abs_tol=TOLERANCE)
    assert sim_res["projected_reduction_pct"] == 40.0

def test_case_10_missing_and_invalid_inputs():
    """
    Test Case 10: Missing Data, Boundary & Invalid Input Handling
    10a: Zero activity value -> 0.000 kg CO2e (valid)
    10b: None/missing input -> DATA_GAP flag
    10c: Negative activity input -> ValueError
    10d: Unregistered factor ID -> KeyError
    """
    # 10a: Zero value
    zero_res = DeterministicCarbonEngine.calculate_single(
        activity_type="FUEL_DIESEL_L",
        raw_value=0.0,
        raw_unit="L"
    )
    assert zero_res["status"] == "CALCULATED"
    assert zero_res["co2e_kg"] == 0.0

    # 10b: Missing value
    missing_res = DeterministicCarbonEngine.calculate_single(
        activity_type="FUEL_DIESEL_L",
        raw_value=None,
        raw_unit="L"
    )
    assert missing_res["status"] == "DATA_GAP"
    assert missing_res["data_quality"] == "DATA_GAP"
    assert missing_res["co2e_kg"] == 0.0

    # 10c: Negative value
    with pytest.raises(ValueError, match="Activity value cannot be negative"):
        DeterministicCarbonEngine.calculate_single(
            activity_type="ELEC_IN_GRID",
            raw_value=-50.0,
            raw_unit="kWh"
        )

    # 10d: Unregistered factor ID
    with pytest.raises(KeyError, match="not found in registry"):
        DeterministicCarbonEngine.calculate_single(
            activity_type="UNKNOWN_FACTOR_999",
            raw_value=100.0,
            raw_unit="kg"
        )
