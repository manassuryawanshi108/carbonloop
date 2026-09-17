"""
Verified Emission Factor Registry for CarbonLoop.
Every entry here is extracted from official primary sources verified in Phase 1:
- CEA India CO2 Baseline Database Version 20.0 (December 2024, FY 2023-24)
- UK DESNZ / DEFRA GHG Conversion Factors for Company Reporting 2024 v1.1
- Poore & Nemecek (Science 2018) for Dietary Baseline LCA
"""

from typing import Dict, Any, List

# Emission Factor Schema
# factor_id: unique identifier
# name: human readable descriptor
# scope: "Scope 1" | "Scope 2" | "Scope 3"
# category: GHG category or subcategory
# value: numeric kg CO2e per unit
# unit: standard input unit
# geography: geographical jurisdiction
# year: publication / baseline year
# source: official publishing authority
# source_url: verified direct URL
# methodology: calculation derivation
# confidence: "HIGH (Official Primary)" | "MEDIUM (Estimate)"

EMISSION_FACTORS: Dict[str, Dict[str, Any]] = {
    "ELEC_IN_GRID": {
        "factor_id": "ELEC_IN_GRID",
        "name": "India National Grid Electricity (Location-based)",
        "scope": "Scope 2",
        "category": "Purchased Electricity",
        "value": 0.727492658,
        "unit": "kWh",
        "geography": "India (National Grid)",
        "year": "2023-24",
        "source": "Central Electricity Authority (CEA), Ministry of Power, GoI",
        "source_url": "https://cea.nic.in/cdm-co2-baseline-database/?lang=en",
        "methodology": "Weighted average net generation effective injection including renewables & captive generation (CEA CO2 Baseline Database Version 20.0, Results sheet row 29).",
        "confidence": "HIGH (Official Primary)",
        "version": "20.0"
    },
    "FUEL_DIESEL_L": {
        "factor_id": "FUEL_DIESEL_L",
        "name": "Diesel Fuel (Stationary / Mobile / DG Set)",
        "scope": "Scope 1",
        "category": "Direct Stationary / Mobile Combustion",
        "value": 2.5123000,
        "unit": "L",
        "geography": "Global / UK / India standard",
        "year": "2024",
        "source": "UK DESNZ / DEFRA 2024 v1.1",
        "source_url": "https://www.gov.uk/government/collections/government-conversion-factors-for-company-reporting",
        "methodology": "3014.09462 kg CO2e/tonne / 1199.733 L/tonne density (average forecourt blend)",
        "confidence": "HIGH (Official Primary)",
        "version": "2024 v1.1"
    },
    "FUEL_PETROL_L": {
        "factor_id": "FUEL_PETROL_L",
        "name": "Petrol / Gasoline (Company Fleet / Mobile)",
        "scope": "Scope 1",
        "category": "Direct Mobile Combustion",
        "value": 2.0845200,
        "unit": "L",
        "geography": "Global / UK / India standard",
        "year": "2024",
        "source": "UK DESNZ / DEFRA 2024 v1.1",
        "source_url": "https://www.gov.uk/government/collections/government-conversion-factors-for-company-reporting",
        "methodology": "2778.52935 kg CO2e/tonne / 1332.932 L/tonne density (average biofuel blend)",
        "confidence": "HIGH (Official Primary)",
        "version": "2024 v1.1"
    },
    "FUEL_LPG_KG": {
        "factor_id": "FUEL_LPG_KG",
        "name": "Commercial LPG (Canteen / Kitchen / Heating)",
        "scope": "Scope 1",
        "category": "Direct Stationary Combustion",
        "value": 2.93936095,
        "unit": "kg",
        "geography": "Global standard",
        "year": "2024",
        "source": "UK DESNZ / DEFRA 2024 v1.1",
        "source_url": "https://www.gov.uk/government/collections/government-conversion-factors-for-company-reporting",
        "methodology": "2939.36095 kg CO2e / tonne / 1000 kg/tonne",
        "confidence": "HIGH (Official Primary)",
        "version": "2024 v1.1"
    },
    "FUEL_CNG_KG": {
        "factor_id": "FUEL_CNG_KG",
        "name": "Compressed Natural Gas (CNG)",
        "scope": "Scope 1",
        "category": "Direct Mobile / Stationary Combustion",
        "value": 2.56816441,
        "unit": "kg",
        "geography": "Global standard",
        "year": "2024",
        "source": "UK DESNZ / DEFRA 2024 v1.1",
        "source_url": "https://www.gov.uk/government/collections/government-conversion-factors-for-company-reporting",
        "methodology": "2568.16441 kg CO2e / tonne / 1000 kg/tonne",
        "confidence": "HIGH (Official Primary)",
        "version": "2024 v1.1"
    },
    "TRANSIT_BUS_PKM": {
        "factor_id": "TRANSIT_BUS_PKM",
        "name": "Municipal Transit / Local Bus",
        "scope": "Scope 3",
        "category": "Category 7: Employee Commuting",
        "value": 0.1084600,
        "unit": "pkm",
        "geography": "Urban transit",
        "year": "2024",
        "source": "UK DESNZ / DEFRA 2024 v1.1",
        "source_url": "https://www.gov.uk/government/collections/government-conversion-factors-for-company-reporting",
        "methodology": "Average local bus passenger.km weighted factor",
        "confidence": "HIGH (Official Primary)",
        "version": "2024 v1.1"
    },
    "TRANSIT_RAIL_PKM": {
        "factor_id": "TRANSIT_RAIL_PKM",
        "name": "Suburban / National Rail / Metro",
        "scope": "Scope 3",
        "category": "Category 7: Employee Commuting",
        "value": 0.0354600,
        "unit": "pkm",
        "geography": "Rail network",
        "year": "2024",
        "source": "UK DESNZ / DEFRA 2024 v1.1",
        "source_url": "https://www.gov.uk/government/collections/government-conversion-factors-for-company-reporting",
        "methodology": "National rail passenger.km average factor",
        "confidence": "HIGH (Official Primary)",
        "version": "2024 v1.1"
    },
    "VEHICLE_MOTO_KM": {
        "factor_id": "VEHICLE_MOTO_KM",
        "name": "Two-Wheeler / Motorcycle Commute",
        "scope": "Scope 3",
        "category": "Category 7: Employee Commuting",
        "value": 0.1136700,
        "unit": "km",
        "geography": "Fleet average",
        "year": "2024",
        "source": "UK DESNZ / DEFRA 2024 v1.1",
        "source_url": "https://www.gov.uk/government/collections/government-conversion-factors-for-company-reporting",
        "methodology": "Average motorcycle per km mix factor",
        "confidence": "HIGH (Official Primary)",
        "version": "2024 v1.1"
    },
    "VEHICLE_CAR_KM": {
        "factor_id": "VEHICLE_CAR_KM",
        "name": "Passenger Car (Average / Unknown Fuel)",
        "scope": "Scope 3",
        "category": "Category 7: Employee Commuting",
        "value": 0.1698400,
        "unit": "km",
        "geography": "Fleet average",
        "year": "2024",
        "source": "UK DESNZ / DEFRA 2024 v1.1",
        "source_url": "https://www.gov.uk/government/collections/government-conversion-factors-for-company-reporting",
        "methodology": "Average car per km unknown fuel factor with real-world uplift",
        "confidence": "HIGH (Official Primary)",
        "version": "2024 v1.1"
    },
    "FLIGHT_DOMESTIC_PKM": {
        "factor_id": "FLIGHT_DOMESTIC_PKM",
        "name": "Business Travel: Domestic Flight (with RF)",
        "scope": "Scope 3",
        "category": "Category 6: Business Travel",
        "value": 0.2725700,
        "unit": "pkm",
        "geography": "Domestic flights (<1,000 km average leg)",
        "year": "2024",
        "source": "UK DESNZ / DEFRA 2024 v1.1",
        "source_url": "https://www.gov.uk/government/collections/government-conversion-factors-for-company-reporting",
        "methodology": "Domestic flight passenger.km including 8% distance uplift and Radiative Forcing (RF)",
        "confidence": "HIGH (Official Primary)",
        "version": "2024 v1.1"
    },
    "FLIGHT_SHORTHAUL_PKM": {
        "factor_id": "FLIGHT_SHORTHAUL_PKM",
        "name": "Business Travel: Short-Haul Flight (with RF)",
        "scope": "Scope 3",
        "category": "Category 6: Business Travel",
        "value": 0.1859200,
        "unit": "pkm",
        "geography": "International (<3,700 km)",
        "year": "2024",
        "source": "UK DESNZ / DEFRA 2024 v1.1",
        "source_url": "https://www.gov.uk/government/collections/government-conversion-factors-for-company-reporting",
        "methodology": "Short-haul flight with Radiative Forcing",
        "confidence": "HIGH (Official Primary)",
        "version": "2024 v1.1"
    },
    "WASTE_LANDFILL_KG": {
        "factor_id": "WASTE_LANDFILL_KG",
        "name": "Commercial Waste to Landfill",
        "scope": "Scope 3",
        "category": "Category 5: Waste Generated in Operations",
        "value": 0.5203342,
        "unit": "kg",
        "geography": "Commercial waste",
        "year": "2024",
        "source": "UK DESNZ / DEFRA 2024 v1.1",
        "source_url": "https://www.gov.uk/government/collections/government-conversion-factors-for-company-reporting",
        "methodology": "520.3342 kg CO2e / tonne commercial waste to landfill / 1000 kg/tonne",
        "confidence": "HIGH (Official Primary)",
        "version": "2024 v1.1"
    },
    "WATER_MAINS_M3": {
        "factor_id": "WATER_MAINS_M3",
        "name": "Mains Water Supply & Sewage Treatment",
        "scope": "Scope 3",
        "category": "Category 1/5: Purchased Goods / Waste",
        "value": 0.3388500,
        "unit": "m3",
        "geography": "Mains utility",
        "year": "2024",
        "source": "UK DESNZ / DEFRA 2024 v1.1",
        "source_url": "https://www.gov.uk/government/collections/government-conversion-factors-for-company-reporting",
        "methodology": "Water supply (0.15311) + Water treatment (0.18574) per cubic metre",
        "confidence": "HIGH (Official Primary)",
        "version": "2024 v1.1"
    },
    "MEAL_VEG": {
        "factor_id": "MEAL_VEG",
        "name": "Vegetarian Diet Meal",
        "scope": "Scope 3",
        "category": "Individual / Dietary",
        "value": 1.2000000,
        "unit": "meal",
        "geography": "Global / India",
        "year": "2018",
        "source": "Poore & Nemecek (Science 2018)",
        "source_url": "https://doi.org/10.1126/science.aaq0216",
        "methodology": "Average cradle-to-plate LCA for vegetarian diet portions",
        "confidence": "MEDIUM (Estimate)",
        "version": "2018"
    },
    "MEAL_NONVEG": {
        "factor_id": "MEAL_NONVEG",
        "name": "Meat-inclusive Meal (Poultry/Fish/Mutton)",
        "scope": "Scope 3",
        "category": "Individual / Dietary",
        "value": 3.8000000,
        "unit": "meal",
        "geography": "Global / India",
        "year": "2018",
        "source": "Poore & Nemecek (Science 2018)",
        "source_url": "https://doi.org/10.1126/science.aaq0216",
        "methodology": "Average cradle-to-plate LCA for mixed meat diet portions",
        "confidence": "MEDIUM (Estimate)",
        "version": "2018"
    }
}

def get_factor(factor_id: str) -> Dict[str, Any]:
    if factor_id not in EMISSION_FACTORS:
        raise KeyError(f"Emission factor '{factor_id}' not found in registry.")
    return EMISSION_FACTORS[factor_id]

def list_all_factors() -> List[Dict[str, Any]]:
    return list(EMISSION_FACTORS.values())
