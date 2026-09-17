"""
Decarbonization Scenario Simulation Engine for CarbonLoop.
Produces projected/potential results strictly labeled SIMULATION/PROJECTION.
Never modifies historical measured actuals.
"""

from typing import Dict, Any
from app.carbon_engine.factors import get_factor

class ScenarioEngine:

    @staticmethod
    def simulate_reduction(
        baseline_annual: Dict[str, Any],
        solar_share_pct: float = 0.0,          # 0 - 100%
        hvac_temp_offset_c: float = 0.0,       # 0 - 4 °C (approx 4% cooling saving per deg C)
        transit_shift_pct: float = 0.0,        # 0 - 100% solo commute to metro/bus
        flight_reduction_pct: float = 0.0,     # 0 - 100% virtual meeting substitution
        waste_composting_pct: float = 0.0      # 0 - 100% landfill waste diverted to composting
    ) -> Dict[str, Any]:
        """
        Calculates projected reduction scenarios against an annual baseline.
        """
        # Baseline annual activity values
        grid_kwh = baseline_annual.get("grid_electricity_kwh", 168200.0)
        flight_pkm = baseline_annual.get("flight_domestic_pkm", 34500.0)
        commute_car_km = baseline_annual.get("commute_car_km", 37500.0)
        commute_moto_km = baseline_annual.get("commute_moto_km", 74800.0)
        waste_kg = baseline_annual.get("waste_landfill_kg", 8090.0)

        # Baseline Emissions
        ef_elec = get_factor("ELEC_IN_GRID")["value"]
        ef_flight = get_factor("FLIGHT_DOMESTIC_PKM")["value"]
        ef_car = get_factor("VEHICLE_CAR_KM")["value"]
        ef_moto = get_factor("VEHICLE_MOTO_KM")["value"]
        ef_rail = get_factor("TRANSIT_RAIL_PKM")["value"]
        ef_waste = get_factor("WASTE_LANDFILL_KG")["value"]

        base_elec_co2 = grid_kwh * ef_elec
        base_flight_co2 = flight_pkm * ef_flight
        base_commute_co2 = (commute_car_km * ef_car) + (commute_moto_km * ef_moto)
        base_waste_co2 = waste_kg * ef_waste

        total_baseline_kg = baseline_annual.get("total_baseline_kg", 176534.49)

        # 1. Solar Rooftop Generation (Displaces Grid Electricity)
        clamped_solar = min(max(solar_share_pct, 0.0), 100.0)
        solar_displaced_kwh = grid_kwh * (clamped_solar / 100.0)
        solar_reduction_kg = solar_displaced_kwh * ef_elec

        # 2. HVAC Optimization (4% cooling load reduction per °C; summer cooling ~ 45% of electricity)
        clamped_temp = min(max(hvac_temp_offset_c, 0.0), 4.0)
        cooling_portion_kwh = grid_kwh * 0.45
        hvac_saved_kwh = cooling_portion_kwh * (clamped_temp * 0.04)
        hvac_reduction_kg = hvac_saved_kwh * ef_elec

        # 3. Transit Shift (Shift personal car/bike to electric metro/rail)
        clamped_transit = min(max(transit_shift_pct, 0.0), 100.0)
        shifted_car_km = commute_car_km * (clamped_transit / 100.0)
        shifted_moto_km = commute_moto_km * (clamped_transit / 100.0)
        # Previous emissions from shifted distance:
        prev_shift_emissions = (shifted_car_km * ef_car) + (shifted_moto_km * ef_moto)
        # New emissions via electric rail/metro:
        new_rail_emissions = (shifted_car_km + shifted_moto_km) * ef_rail
        transit_reduction_kg = max(0.0, prev_shift_emissions - new_rail_emissions)

        # 4. Virtual Meeting Flight Reduction
        clamped_flights = min(max(flight_reduction_pct, 0.0), 100.0)
        flight_displaced_pkm = flight_pkm * (clamped_flights / 100.0)
        flight_reduction_kg = flight_displaced_pkm * ef_flight

        # 5. Waste Composting Diversion
        clamped_waste = min(max(waste_composting_pct, 0.0), 100.0)
        waste_diverted_kg = waste_kg * (clamped_waste / 100.0)
        waste_reduction_kg = waste_diverted_kg * ef_waste

        # Total Potential Reduction
        total_reduction_kg = (
            solar_reduction_kg +
            hvac_reduction_kg +
            transit_reduction_kg +
            flight_reduction_kg +
            waste_reduction_kg
        )
        projected_residual_kg = max(0.0, total_baseline_kg - total_reduction_kg)
        reduction_percentage = (total_reduction_kg / total_baseline_kg * 100.0) if total_baseline_kg > 0 else 0.0

        return {
            "classification": "SIMULATION/PROJECTION",
            "warning": "All figures in this projection are potential estimates for decarbonization modeling and do not represent verified historical emissions.",
            "baseline_total_kg": round(total_baseline_kg, 2),
            "baseline_total_tonnes": round(total_baseline_kg / 1000.0, 3),
            "projected_residual_kg": round(projected_residual_kg, 2),
            "projected_residual_tonnes": round(projected_residual_kg / 1000.0, 3),
            "total_projected_reduction_kg": round(total_reduction_kg, 2),
            "total_projected_reduction_tonnes": round(total_reduction_kg / 1000.0, 3),
            "projected_reduction_pct": round(reduction_percentage, 1),
            "interventions": {
                "solar_pv": {
                    "share_pct": clamped_solar,
                    "displaced_kwh": round(solar_displaced_kwh, 1),
                    "reduction_kg": round(solar_reduction_kg, 2),
                    "reduction_tonnes": round(solar_reduction_kg / 1000.0, 3)
                },
                "hvac_efficiency": {
                    "temp_offset_c": clamped_temp,
                    "saved_kwh": round(hvac_saved_kwh, 1),
                    "reduction_kg": round(hvac_reduction_kg, 2),
                    "reduction_tonnes": round(hvac_reduction_kg / 1000.0, 3)
                },
                "transit_shift": {
                    "shift_pct": clamped_transit,
                    "reduction_kg": round(transit_reduction_kg, 2),
                    "reduction_tonnes": round(transit_reduction_kg / 1000.0, 3)
                },
                "virtual_travel": {
                    "reduction_pct": clamped_flights,
                    "displaced_pkm": round(flight_displaced_pkm, 1),
                    "reduction_kg": round(flight_reduction_kg, 2),
                    "reduction_tonnes": round(flight_reduction_kg / 1000.0, 3)
                },
                "waste_diversion": {
                    "composting_pct": clamped_waste,
                    "diverted_kg": round(waste_diverted_kg, 1),
                    "reduction_kg": round(waste_reduction_kg, 2),
                    "reduction_tonnes": round(waste_reduction_kg / 1000.0, 3)
                }
            }
        }
