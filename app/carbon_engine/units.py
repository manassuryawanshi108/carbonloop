"""
Unit normalization and validation utility for CarbonLoop.
Ensures strict unit conversion into base units required by the deterministic factor engine.
"""

from typing import Tuple

UNIT_CONVERSIONS = {
    # Energy -> kWh
    "kwh": ("kWh", 1.0),
    "mwh": ("kWh", 1000.0),
    "gwh": ("kWh", 1_000_000.0),
    
    # Volume -> L
    "l": ("L", 1.0),
    "litre": ("L", 1.0),
    "litres": ("L", 1.0),
    "liter": ("L", 1.0),
    "liters": ("L", 1.0),
    "ml": ("L", 0.001),
    "gallon": ("L", 3.785411784),
    "gal": ("L", 3.785411784),

    # Mass -> kg
    "kg": ("kg", 1.0),
    "tonne": ("kg", 1000.0),
    "tonnes": ("kg", 1000.0),
    "t": ("kg", 1000.0),
    "g": ("kg", 0.001),

    # Distance -> km / pkm
    "km": ("km", 1.0),
    "mile": ("km", 1.609344),
    "miles": ("km", 1.609344),
    "pkm": ("pkm", 1.0),
    "passenger-km": ("pkm", 1.0),

    # Water Volume -> m3
    "m3": ("m3", 1.0),
    "cu_m": ("m3", 1.0),
    "cum": ("m3", 1.0),

    # Counts
    "meal": ("meal", 1.0),
    "meals": ("meal", 1.0)
}

def normalize_unit(raw_value: float, raw_unit: str) -> Tuple[float, str]:
    """
    Normalizes user-supplied activity quantity and unit to the standard base unit.
    Throws ValueError for unrecognized units.
    """
    cleaned_unit = raw_unit.strip().lower()
    if cleaned_unit not in UNIT_CONVERSIONS:
        raise ValueError(f"Unsupported unit: '{raw_unit}'. Supported units: {list(UNIT_CONVERSIONS.keys())}")
    
    base_unit, multiplier = UNIT_CONVERSIONS[cleaned_unit]
    normalized_value = raw_value * multiplier
    return normalized_value, base_unit
