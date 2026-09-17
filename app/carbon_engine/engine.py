"""
Deterministic Carbon Engine for CarbonLoop.
Guarantees 100% mathematical fidelity. Never touched or modified by AI.
Formula: Emissions (kg CO2e) = Activity Value (Normalized) * Factor Value
"""

from typing import Dict, Any, List, Optional
from app.carbon_engine.factors import get_factor, EMISSION_FACTORS
from app.carbon_engine.units import normalize_unit

class DeterministicCarbonEngine:

    @staticmethod
    def calculate_single(
        activity_type: str,
        raw_value: Optional[float],
        raw_unit: str,
        data_quality: str = "USER_ENTERED",
        activity_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Executes deterministic calculation for a single activity.
        Rejects negative values.
        Emits immutable traceability metadata.
        """
        if raw_value is None:
            return {
                "status": "DATA_GAP",
                "activity_id": activity_id,
                "activity_type": activity_type,
                "raw_value": None,
                "raw_unit": raw_unit,
                "co2e_kg": 0.0,
                "co2e_tonnes": 0.0,
                "formula": "MISSING_DATA",
                "message": "Activity value is missing or unrecorded.",
                "data_quality": "DATA_GAP"
            }

        if raw_value < 0:
            raise ValueError(f"Activity value cannot be negative: {raw_value}")

        factor_meta = get_factor(activity_type)
        factor_val = factor_meta["value"]
        target_unit = factor_meta["unit"]

        # Unit normalization
        normalized_val, norm_unit = normalize_unit(raw_value, raw_unit)
        if norm_unit != target_unit:
            raise ValueError(
                f"Normalized unit '{norm_unit}' does not match factor target unit '{target_unit}' for {activity_type}"
            )

        co2e_kg = normalized_val * factor_val
        co2e_tonnes = co2e_kg / 1000.0

        formula = f"{normalized_val:.4f} {target_unit} × {factor_val:.6f} kg CO2e/{target_unit} = {co2e_kg:.4f} kg CO2e"

        return {
            "status": "CALCULATED",
            "activity_id": activity_id,
            "activity_type": activity_type,
            "activity_name": factor_meta["name"],
            "scope": factor_meta["scope"],
            "category": factor_meta["category"],
            "raw_value": raw_value,
            "raw_unit": raw_unit,
            "normalized_value": normalized_val,
            "unit": target_unit,
            "factor_id": factor_meta["factor_id"],
            "factor_value": factor_val,
            "factor_source": factor_meta["source"],
            "factor_source_url": factor_meta["source_url"],
            "factor_methodology": factor_meta["methodology"],
            "confidence": factor_meta["confidence"],
            "data_quality": data_quality,
            "co2e_kg": round(co2e_kg, 6),
            "co2e_tonnes": round(co2e_tonnes, 6),
            "formula": formula
        }

    @staticmethod
    def aggregate_footprint(calculations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Aggregates a collection of calculated activities into scopes, categories, and totals.
        """
        total_kg = 0.0
        scope_totals = {
            "Scope 1": 0.0,
            "Scope 2": 0.0,
            "Scope 3": 0.0
        }
        category_breakdown: Dict[str, float] = {}
        quality_counts: Dict[str, int] = {}
        hotspots: List[Dict[str, Any]] = []

        for calc in calculations:
            if calc.get("status") != "CALCULATED":
                continue
            kg = calc["co2e_kg"]
            scope = calc["scope"]
            cat = calc["category"]
            quality = calc.get("data_quality", "USER_ENTERED")

            total_kg += kg
            scope_totals[scope] = scope_totals.get(scope, 0.0) + kg
            category_breakdown[cat] = category_breakdown.get(cat, 0.0) + kg
            quality_counts[quality] = quality_counts.get(quality, 0) + 1

        total_tonnes = total_kg / 1000.0

        # Scope shares
        scope_pcts = {}
        for sc, val in scope_totals.items():
            pct = (val / total_kg * 100.0) if total_kg > 0 else 0.0
            scope_pcts[sc] = {
                "co2e_kg": round(val, 3),
                "co2e_tonnes": round(val / 1000.0, 3),
                "percentage": round(pct, 1)
            }

        # Hotspot detection (sorted descending)
        sorted_categories = sorted(category_breakdown.items(), key=lambda x: x[1], reverse=True)
        for cat, kg in sorted_categories:
            pct = (kg / total_kg * 100.0) if total_kg > 0 else 0.0
            hotspots.append({
                "category": cat,
                "co2e_kg": round(kg, 3),
                "co2e_tonnes": round(kg / 1000.0, 3),
                "percentage": round(pct, 1)
            })

        dominant_hotspot = hotspots[0] if hotspots else None

        return {
            "total_co2e_kg": round(total_kg, 3),
            "total_co2e_tonnes": round(total_tonnes, 3),
            "scopes": scope_pcts,
            "hotspots": hotspots,
            "dominant_hotspot": dominant_hotspot,
            "data_quality_distribution": quality_counts,
            "record_count": len(calculations)
        }
