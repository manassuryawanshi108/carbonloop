"""
KPI calculation service for CarbonLoop.
Computes strictly scientific, non-vanity indicators aligned with GHG Protocol and SEBI BRSR Core.
"""

from typing import Dict, Any

class KPIService:

    @staticmethod
    def compute_organization_kpis(
        aggregate_footprint: Dict[str, Any],
        employee_count: int = 50,
        facility_sqft: float = 15000.0,
        target_pct: float = 30.0,
        baseline_year_kg: float = 176534.49
    ) -> Dict[str, Any]:
        """
        Computes standard disclosure KPIs.
        """
        total_kg = aggregate_footprint.get("total_co2e_kg", 0.0)
        total_tonnes = total_kg / 1000.0

        # Intensities
        per_employee_kg = (total_kg / employee_count) if employee_count > 0 else 0.0
        per_employee_tonnes = per_employee_kg / 1000.0

        per_sqft_kg = (total_kg / facility_sqft) if facility_sqft > 0 else 0.0

        # Data Quality Score
        quality_dist = aggregate_footprint.get("data_quality_distribution", {})
        total_records = sum(quality_dist.values())
        measured_count = quality_dist.get("MEASURED", 0)
        confidence_pct = (measured_count / total_records * 100.0) if total_records > 0 else 85.0

        # Target math
        target_co2e_kg = baseline_year_kg * (1.0 - (target_pct / 100.0))
        actual_reduction_kg = max(0.0, baseline_year_kg - total_kg)
        required_reduction_kg = max(0.0, baseline_year_kg - target_co2e_kg)
        progress_pct = (actual_reduction_kg / required_reduction_kg * 100.0) if required_reduction_kg > 0 else 0.0

        return {
            "total_co2e_tonnes": round(total_tonnes, 3),
            "total_co2e_kg": round(total_kg, 2),
            "scope1_tonnes": aggregate_footprint.get("scopes", {}).get("Scope 1", {}).get("co2e_tonnes", 0.0),
            "scope2_tonnes": aggregate_footprint.get("scopes", {}).get("Scope 2", {}).get("co2e_tonnes", 0.0),
            "scope3_tonnes": aggregate_footprint.get("scopes", {}).get("Scope 3", {}).get("co2e_tonnes", 0.0),
            "intensity_per_employee_t": round(per_employee_tonnes, 3),
            "intensity_per_employee_kg": round(per_employee_kg, 2),
            "intensity_per_sqft_kg": round(per_sqft_kg, 3),
            "dominant_hotspot": aggregate_footprint.get("dominant_hotspot"),
            "data_confidence_pct": round(confidence_pct, 1),
            "target": {
                "target_pct": target_pct,
                "baseline_kg": round(baseline_year_kg, 2),
                "target_co2e_kg": round(target_co2e_kg, 2),
                "actual_reduction_kg": round(actual_reduction_kg, 2),
                "progress_pct": round(progress_pct, 1)
            }
        }
